"""Finite deletion sensitivity of therapeutic-address transcript reads; local CPU only.

The CLI checks that all three provenance inputs match HEAD before writing outputs.
Only the parent's gene_reads per_sample z_vs_array/class/gsm supply observations.
No parent expression pipeline is imported or executed. Synthetic inputs in tests
exercise missingness and deletion behavior; they are never written to the result.
"""
from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PARENT = "research/modalities/emc-expression-panels.json"
INPUTS = (PARENT, "research/modalities/emc-expression-panels-inputs.json",
          "research/modalities/emc_expression_panels.py")
OUTPUT = "research/modalities/surface-address-sensitivity.json"
NOTE = "research/modalities/surface-address-sensitivity.md"
MEMBERSHIP = "panels.surface_antigen.groups.route_named_addresses.genes_requested"
EXPECTED = {"CD276", "SSTR2", "PRAME", "FAP", "CD248", "CSPG4", "MSLN",
            "L1CAM", "GPC3", "ALPP", "CDH17"}
# Parent _gene_read rounds z to 4 places; its imported _welch rounds delta to 4.
# Trailing zeros are not preserved by JSON, so e.g. -0.249 still has 4-place precision.
PARENT_PLACES = 4


class InputError(ValueError):
    """A precise parent-input defect prevents the requested computation."""


def number(value):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise InputError(f"z_vs_array must be a finite number or null: {value!r}")
    return Fraction(str(value))


def sign(value):
    return None if value is None else (value > 0) - (value < 0)


def sample_map(record):
    result = {}
    rows = record.get("per_sample", [])
    if not isinstance(rows, list):
        raise InputError("per_sample must be a list")
    for row in rows:
        gsm, cls = row.get("gsm"), row.get("class")
        if not isinstance(gsm, str) or not gsm or not isinstance(cls, str) or not cls:
            raise InputError("per_sample row lacks a nonempty gsm or class")
        if gsm in result:
            raise InputError(f"duplicate per_sample gsm: {gsm}")
        number(row.get("z_vs_array"))
        result[gsm] = {"gsm": gsm, "class": cls, "z_vs_array": row.get("z_vs_array")}
    return result


def counts(rows):
    def arm(items):
        available = sum(r["z_vs_array"] is not None for r in items)
        return {"recorded_n": len(items), "available_n": available,
                "missing_n": len(items) - available}
    classes = sorted({r["class"] for r in rows if r["class"] != "EMC"})
    return {"EMC": arm([r for r in rows if r["class"] == "EMC"]),
            "comparator": arm([r for r in rows if r["class"] != "EMC"]),
            "comparator_classes": {c: arm([r for r in rows if r["class"] == c])
                                   for c in classes}}


def contrast(rows):
    a = [number(r["z_vs_array"]) for r in rows
         if r["class"] == "EMC" and r["z_vs_array"] is not None]
    b = [number(r["z_vs_array"]) for r in rows
         if r["class"] != "EMC" and r["z_vs_array"] is not None]
    ma = sum(a, Fraction()) / len(a) if a else None
    mb = sum(b, Fraction()) / len(b) if b else None
    delta = ma - mb if ma is not None and mb is not None else None
    return {"counts": counts(rows), "mean_EMC": None if ma is None else float(ma),
            "mean_comparator": None if mb is None else float(mb),
            "delta": None if delta is None else float(delta), "sign": sign(delta)}, delta


def deletion_summary(rows, baseline_sign):
    eligible = [r for r in rows if r["eligible"]]
    values = [r["delta"] for r in eligible]
    all_eligible = bool(rows) and len(eligible) == len(rows)
    preserved = (all_eligible and baseline_sign in (-1, 1)
                 and all(r["sign"] == baseline_sign for r in eligible))
    return {"n_deletions": len(rows), "n_eligible": len(eligible),
            "n_ineligible": len(rows) - len(eligible),
            "min_delta": min(values) if values else None,
            "max_delta": max(values) if values else None,
            "sign_flip_ids": [r["deleted_id"] for r in eligible if r["sign_flip"]],
            "sign_change_ids": [r["deleted_id"] for r in eligible if r["sign_change"]],
            "zero_delta_ids": [r["deleted_id"] for r in eligible if r["sign"] == 0],
            "strict_direction_survives_all": preserved if all_eligible else None}


def analyze_address(record, roster):
    """Delete each recorded EMC GSM or non-EMC class, including missing-value rows."""
    observed = sample_map(record or {})
    readable = record is not None and record.get("readable") is True
    if record is None:
        reason = "missing_gene_platform_record"
    elif not readable:
        reason = record.get("why_not_readable", "parent_readable_is_not_true")
    else:
        reason = None
    rows = []
    for gsm, cls in sorted(roster.items()):
        source = observed.get(gsm)
        if source and source["class"] != cls:
            raise InputError(f"conflicting class for {gsm}")
        missing_reason = None
        if not readable:
            missing_reason = "platform_address_unreadable"
        elif source is None:
            missing_reason = "absent_per_sample_row"
        elif source["z_vs_array"] is None:
            missing_reason = "missing_z_vs_array"
        rows.append({"gsm": gsm, "class": cls,
                     "z_vs_array": source["z_vs_array"] if not missing_reason else None,
                     "missing_reason": missing_reason})
    if set(observed) - set(roster):
        raise InputError("per_sample GSM outside platform roster")
    baseline, exact = contrast(rows)
    parent_delta = ((record or {}).get("welch_EMC_vs_comparator") or {}).get("delta_a_minus_b")
    if parent_delta is not None:
        number(parent_delta)
    rounded = float(round(exact, PARENT_PLACES)) if exact is not None else None
    comparison = {"parent_delta": parent_delta, "decimal_places": PARENT_PLACES,
                  "recomputed_at_parent_precision": rounded,
                  "status": ("not_comparable" if rounded is None or parent_delta is None else
                             "match" if rounded == parent_delta else "disagreement")}
    deletion_groups = {}
    for mode, ids in (
        ("leave_one_EMC_out", [r["gsm"] for r in rows if r["class"] == "EMC"]),
        ("leave_one_comparator_histology_out", sorted({r["class"] for r in rows
                                                       if r["class"] != "EMC"})),
    ):
        deleted_rows = []
        for item in ids:
            field = "gsm" if mode == "leave_one_EMC_out" else "class"
            removed = [r for r in rows if r[field] == item]
            retained = [r for r in rows if r[field] != item]
            entry, value = contrast(retained)
            eligible = readable and value is not None
            entry.update({"deleted_id": item, "deleted_gsms": [r["gsm"] for r in removed],
                          "deleted_available_n": sum(r["z_vs_array"] is not None for r in removed),
                          "eligible": eligible,
                          "ineligible_reason": (None if eligible else "unreadable_address" if not readable
                                                else "empty_available_arm_after_deletion"),
                          "sign_flip": (sign(value) * sign(exact) == -1
                                        if eligible and exact is not None else None),
                          "sign_change": (sign(value) != sign(exact)
                                          if eligible and exact is not None else None)})
            deleted_rows.append(entry)
        deletion_groups[mode] = {"summary": deletion_summary(deleted_rows, sign(exact)),
                                 "rows": deleted_rows}
    summaries = [v["summary"] for v in deletion_groups.values()]
    if not readable:
        state = "unreadable"
    elif exact is None:
        state = "unestimable_baseline"
    elif any(s["sign_change_ids"] for s in summaries):
        state = "unstable"
    elif exact == 0:
        state = "zero_baseline"
    elif any(s["strict_direction_survives_all"] is None for s in summaries):
        state = "incomplete_deletions"
    else:
        state = "stable_positive" if exact > 0 else "stable_negative"
    return {"readable": readable, "unreadable_reason": reason,
            "status": state, "source_samples": rows, "baseline": baseline,
            "parent_baseline_comparison": comparison, **deletion_groups}


def analyze(parent):
    try:
        members = parent["panels"]["surface_antigen"]["groups"]["route_named_addresses"]["genes_requested"]
        platforms = parent["platforms"]
        reads = parent["gene_reads"]
    except KeyError as exc:
        raise InputError(f"missing required parent field: {exc}") from exc
    if len(members) != len(EXPECTED) or set(members) != EXPECTED:
        raise InputError("route_named_addresses membership differs from the eleven assigned addresses")
    if not platforms:
        raise InputError("parent records no platforms")
    result = {"schema_version": 1, "membership_source": MEMBERSHIP,
              "addresses": members, "platforms": {}}
    for matrix, metadata in sorted(platforms.items()):
        roster = {}
        for gene in members:
            for gsm, row in sample_map(reads.get(gene, {}).get(matrix, {})).items():
                if gsm in roster and roster[gsm] != row["class"]:
                    raise InputError(f"{matrix}: conflicting class for {gsm}")
                roster[gsm] = row["class"]
        if not roster or "EMC" not in roster.values() or set(roster.values()) == {"EMC"}:
            raise InputError(f"{matrix}: gene_reads cannot establish an EMC/comparator roster")
        result["platforms"][matrix] = {
            "series": metadata["series"], "platform": metadata["platform"],
            "source_url": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={metadata['series']}",
            "roster_source": "union of the eleven named gene_reads per_sample gsm/class rows",
            "addresses": {g: analyze_address(reads.get(g, {}).get(matrix), roster) for g in members}}
    return result


def committed_inputs(root=ROOT):
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    sources, parent = [], None
    for path in INPUTS:
        try:
            raw = (root / path).read_bytes()
            committed = subprocess.check_output(["git", "show", f"{revision}:{path}"], cwd=root)
        except (OSError, subprocess.CalledProcessError) as exc:
            raise InputError(f"missing or uncommitted required input: {path}") from exc
        if raw != committed:
            raise InputError(f"working input differs from committed input: {path}")
        sources.append({"path": path, "sha256": hashlib.sha256(raw).hexdigest(),
                        "role": "observations_and_membership" if path == PARENT else "provenance_only"})
        if path == PARENT:
            parent = json.loads(raw)
    return parent, {"base_revision": revision, "parent_source_path": PARENT,
                    "parent_sha256": sources[0]["sha256"], "inputs": sources}


def render_note(result):
    lines = ["---", "id: DOC-SURFACE-ADDRESS-SENSITIVITY",
             "title: EMC therapeutic-address expression deletion sensitivity", "level: L4",
             "kind: memo", "status: live", "canonical_for: []",
             "purpose: Report finite deletion sensitivity of eleven existing EMC therapeutic-address reads.",
             "scope: Exploratory secondary reanalysis of rounded committed parent values on two platforms.",
             "audience: [maintainers, autonomous research agents]", "date: 2026-09-04",
             "last_verified: 2026-09-04", "---", "",
             "# EMC therapeutic-address expression deletion sensitivity", "",
             "Question: which EMC-versus-recorded-comparator expression directions survive deleting "
             "any one EMC sample or any one comparator histology? This is an exploratory secondary "
             "reanalysis, not a preregistered analysis. The stop condition is the deterministic result, "
             "this note, behavioral tests and independent arithmetic verification; no manuscript review.", "",
             "Generated by [surface_address_sensitivity.py](surface_address_sensitivity.py); "
             "[JSON result](surface-address-sensitivity.json) includes every deletion row, counts, "
             "missing sample IDs and the three parent fields used as observations. "
             "[Behavioral tests](tests/test_surface_address_sensitivity.py) also independently "
             "recompute the recorded arithmetic.", "",
             f"Parent: [{PARENT}](emc-expression-panels.json). SHA256: "
             f"`{result['provenance']['parent_sha256']}`. Base revision: "
             f"`{result['provenance']['base_revision']}`. The JSON records exact paths and SHA256 "
             "for all three committed provenance inputs; the cached inputs and parent script supply "
             "no additional observations.", "",
             "Within each platform, delta = mean(EMC) minus mean(all recorded non-EMC samples "
             "with a value), weighting samples equally, not histologies equally. Units are the "
             "parent's within-array z units. Only gene_reads per_sample z_vs_array, class and gsm "
             "enter arithmetic. The platform roster is their union across the eleven addresses; "
             "no samples outside those parent rows are added. Null or absent values are excluded "
             "without imputation. An absent row is distinguished from a null value and from an "
             "unreadable address. Each recorded EMC GSM is deleted in turn (a missing value's "
             "deletion has no numerical effect), then each recorded non-EMC class is removed in "
             "full. These are separate deletions, never simultaneous. A delta requires both "
             "available arms to remain nonempty; ineligible rows remain in the JSON.", "",
             "Arithmetic uses exact rational representations of the rounded decimal parent values "
             "before JSON numeric serialization. Strict signs use that arithmetic without a "
             "tolerance. A flip means opposite nonzero signs; sign changes additionally include "
             "reaching or leaving zero. Stable requires a nonzero baseline and retention of its "
             "strict sign for every deletion in both families; incomplete deletion coverage is "
             "not called stable. Baselines are compared at the parent's four decimal places "
             "(round to nearest, ties to even, including omitted trailing zeros); disagreements "
             "are retained, never substituted with the parent contrast. Ranges below span only "
             "the listed deletions and are displayed to four places. They are finite sensitivity "
             "ranges on rounded values, not sampling uncertainty. No p-values, confidence "
             "intervals, probabilities or cross-platform pooling are calculated.", ""]
    for matrix, platform in result["platforms"].items():
        addresses = platform["addresses"]
        first = next(iter(addresses.values()))["baseline"]["counts"]
        lines += [f"## {platform['series']} / {platform['platform']}", "",
                  f"Source: [{platform['series']}]({platform['source_url']}). Exact parent platform "
                  f"key: `{matrix}`. Recorded roster: {first['EMC']['recorded_n']} EMC and "
                  f"{first['comparator']['recorded_n']} comparator samples. Comparator classes: "
                  + "; ".join(f"{c} (n={v['recorded_n']})" for c, v in first['comparator_classes'].items()) + ".", "",
                  "| Address | Available EMC / comparator | Baseline | Delete EMC range | Delete histology range | Flips EMC / histology | Result | Parent delta |",
                  "|---|---:|---:|---|---|---:|---|---|"]
        def fmt(v):
            return "NA" if v is None else f"{v:.4f}"
        def span(s):
            return "NA" if s['min_delta'] is None else f"{fmt(s['min_delta'])} to {fmt(s['max_delta'])}"
        for gene, row in addresses.items():
            b = row["baseline"]
            e = row["leave_one_EMC_out"]["summary"]
            h = row["leave_one_comparator_histology_out"]["summary"]
            flips = f"{len(e['sign_flip_ids'])} / {len(h['sign_flip_ids'])}" if row['readable'] else "NA"
            lines.append(f"| {gene} | {b['counts']['EMC']['available_n']} / "
                         f"{b['counts']['comparator']['available_n']} | {fmt(b['delta'])} | "
                         f"{span(e)} | {span(h)} | {flips} | {row['status'].replace('_', ' ')} | "
                         f"{row['parent_baseline_comparison']['status']} |")
        lines.append("")
        for state in ("stable_positive", "stable_negative", "unstable", "unreadable"):
            genes = [g for g, r in addresses.items() if r["status"] == state]
            lines.append(f"{state.replace('_', ' ').capitalize()}: {', '.join(genes) or 'none'}.")
        lines.append("")
        for gene, row in addresses.items():
            if row["readable"]:
                missing = [f"{r['gsm']} ({r['class']}; {r['missing_reason']})"
                           for r in row["source_samples"] if r["missing_reason"]]
                if missing:
                    lines.append(f"Missing {gene}: {'; '.join(missing)}.")
                for mode in ("leave_one_EMC_out", "leave_one_comparator_histology_out"):
                    changed = row[mode]["summary"]["sign_change_ids"]
                    if changed:
                        lines.append(f"{gene} sign changes, {mode}: {', '.join(changed)}.")
            comparison = row['parent_baseline_comparison']
            if comparison['status'] == 'disagreement':
                lines.append(f"{gene} baseline disagreement: recomputed "
                             f"{fmt(comparison['recomputed_at_parent_precision'])}; "
                             f"parent {fmt(comparison['parent_delta'])}.")
        lines.append("")
    rows = [r for p in result['platforms'].values() for r in p['addresses'].values()]
    matches = sum(r['parent_baseline_comparison']['status'] == 'match' for r in rows)
    disagreements = sum(r['parent_baseline_comparison']['status'] == 'disagreement' for r in rows)
    lines += [f"Baseline checks: {matches} matches, {disagreements} disagreements, "
              f"{len(rows) - matches - disagreements} not comparable.", "",
              "The cohorts contain different comparator mixtures, including the parent's "
              "desmoid_fibromatosis class; these results concern the recorded comparison arms. "
              "The values already aggregate probes: this does not validate raw data or probe "
              "choice. Missing probe mapping does not mean absent expression. Transcript "
              "directions cannot establish tumour restriction, surface protein localisation, "
              "safety or efficacy. PRAME is an intracellular HLA-presented therapeutic address, "
              "not a surface protein; these transcript data do not demonstrate its presentation. "
              "The supplied GEO links are for coordinator verification; no network access or "
              "live source verification was performed in this run.", "",
              "Run context supplied by the runner: model `gpt-6-astra`, reasoning effort `high`, "
              "saved ChatGPT authentication, total timeout 1800 seconds, 1781.015 seconds "
              "remaining at dispatch (not a live reading), dispatch 1, maximum rounds/dispatches "
              "1/1. Token usage and remaining subscription capacity are unknown. No network, "
              "install or paid compute is required.", "",
              "Reproduce from the repository root in PowerShell (the temporary-directory "
              "settings also cover the existing test-suite fixtures):", "", "```powershell",
              "$surfacePython = 'C:\\Users\\mcrae\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe'",
              "& $surfacePython research/modalities/surface_address_sensitivity.py",
              "New-Item -ItemType Directory -Force .cache | Out-Null",
              "$env:TEMP = (Resolve-Path .cache).Path",
              "$env:TMP = $env:TEMP",
              "& $surfacePython -m pytest research/modalities/tests/test_surface_address_sensitivity.py "
              "--basetemp=.cache/surface-sensitivity-tests --tb=short -p no:cacheprovider",
              "```", "", "Run the generator twice and compare JSON bytes.", ""]
    return "\n".join(lines)


def main():
    parent, provenance = committed_inputs()
    result = analyze(parent)
    result["provenance"] = provenance
    result["method"] = {
        "contrast": "mean(EMC) - mean(all recorded non-EMC), available values, sample weighted",
        "units": "parent within-array z_vs_array units",
        "arithmetic": "exact rational decimal inputs; JSON numbers serialized as floats",
        "range": "finite min/max deletion deltas; not sampling uncertainty",
        "sign_flip": "opposite nonzero signs relative to recomputed baseline",
        "sign_change": "any sign change, including to/from zero",
        "missingness": "no imputation; unreadable is not absent expression",
        "scope": "exploratory secondary reanalysis; no pooling, raw-data or probe-choice validation",
    }
    (ROOT / OUTPUT).write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
                              encoding="utf-8", newline="\n")
    (ROOT / NOTE).write_text(render_note(result), encoding="utf-8", newline="\n")
    states = {}
    for platform in result["platforms"].values():
        for row in platform["addresses"].values():
            states[row["status"]] = states.get(row["status"], 0) + 1
    print(json.dumps({"outputs": [OUTPUT, NOTE], "states": states}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except InputError as exc:
        raise SystemExit(f"Missing/invalid committed input: {exc}") from exc
