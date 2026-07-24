#!/usr/bin/env python3
"""Verify the 5a-KS benchmark's reference ddG values against a primary-source database (SKEMPI 2.0).

WHY THIS EXISTS
---------------
`protfep_bench.BENCHMARKS` carries measured binding ddG values that the engine's PASS/FAIL verdict is
computed against. Those numbers were entered from the literature and flagged `ref_verified: False`,
because a verdict scored against an unchecked number is an unchecked verdict — and this gate's whole
job is to decide whether an unvalidated engine may put a number in the manuscript.

The dev sandbox's egress proxy blocks the publishers, and the primary paper (Schreiber & Fersht, J
Mol Biol 1995) is not open access, so a full-text read is not the practical verification route.
SKEMPI 2.0 is: a curated database of experimentally measured binding affinities for mutants of
structurally-resolved protein-protein complexes, with each record carrying its own literature
citation, the wild-type and mutant Kd, and the temperature. It is freely downloadable, so a CI
runner (unrestricted internet) can fetch it and recompute ddG from the deposited affinities.

That is a STRONGER check than reading one number off one table: it recomputes ddG from the reported
Kd values, shows every independent record for the mutation, and exposes the spread between them. If
the literature disagrees with itself, we see that rather than inheriting one value's confidence.

    ddG_bind = RT * ln(Kd_mut / Kd_wt)     (positive = the mutation WEAKENS binding)

This script does NOT silently rewrite the benchmark constants. It writes a report; reconciling the
constants to it is a deliberate edit, so a database quirk cannot quietly move the pass criterion.
"""

from __future__ import annotations

import json
import math
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import protfep_bench as pb  # noqa: E402

SKEMPI_URL = os.environ.get(
    "SKEMPI_URL", "https://life.bsc.es/pid/skempi2/database/download/skempi_v2.csv")
R_KCAL = 0.0019872041  # gas constant, kcal/(mol*K)


def ddg_from_kd(kd_mut, kd_wt, temperature_k=298.15):
    """ddG_bind from a mutant/wild-type Kd pair. Pure.

    Positive => the mutant binds WORSE, which is the sign convention protfep_bench uses and the sign
    the complex-minus-apo alchemical cycle produces.
    """
    kd_mut, kd_wt = float(kd_mut), float(kd_wt)
    if kd_mut <= 0 or kd_wt <= 0:
        raise ValueError(f"non-positive Kd (mut={kd_mut}, wt={kd_wt})")
    return R_KCAL * float(temperature_k) * math.log(kd_mut / kd_wt)


def parse_temperature(raw, default=298.15):
    """SKEMPI temperature cells carry annotations like '298(assumed)'. Pure.

    Falls back to 298.15 K when unparseable, and the caller records that it did — an assumed
    temperature shifts ddG by only a few percent, but an unrecorded assumption is how a number stops
    being traceable.
    """
    digits = "".join(c for c in str(raw or "") if c.isdigit())
    if not digits:
        return default, True
    try:
        t = float(digits[:3])
    except ValueError:
        return default, True
    return (t, False) if 250.0 <= t <= 350.0 else (default, True)


def mutation_matches(cell, chain, resid, wt_letter, mut_letter):
    """Does a SKEMPI mutation cell describe exactly this single mutation? Pure.

    SKEMPI writes a mutation as <WT><CHAIN><RESI><MUT>, e.g. 'YD29A'. Multi-mutant records are
    comma-separated and are REJECTED here: a double-mutant ddG is not the single-mutation quantity
    the alchemical leg computes, and quietly averaging one in would corrupt the reference.
    """
    cell = str(cell or "").strip()
    if not cell or "," in cell:
        return False
    want = f"{wt_letter}{chain}{resid}{mut_letter}".upper()
    return cell.upper() == want


def fetch_skempi(url=None, cache_path=None):
    """Download the SKEMPI CSV (or read a cached copy). Returns the raw text."""
    if cache_path and os.path.exists(cache_path) and os.path.getsize(cache_path) > 10000:
        with open(cache_path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    req = urllib.request.Request(url or SKEMPI_URL,
                                 headers={"User-Agent": "rare-cancers-protfep-refcheck"})
    with urllib.request.urlopen(req, timeout=180) as r:
        text = r.read().decode("utf-8", "replace")
    if cache_path:
        with open(cache_path, "w", encoding="utf-8") as fh:
            fh.write(text)
    return text


def records_for(csv_text, pdb, chain, resid, wt_letter, mut_letter):
    """Every SKEMPI record for one single-point mutation of one complex. Pure.

    Returns a list of {ddg_kcal, kd_mut, kd_wt, temperature_k, reference, ...}. Records whose
    affinities are missing or unparseable are reported as skipped rather than dropped silently.
    """
    import csv as _csv
    import io

    rows = list(_csv.DictReader(io.StringIO(csv_text), delimiter=";"))
    if not rows:
        return [], [], []
    cols = list(rows[0].keys())

    def col(*candidates):
        for c in candidates:
            for actual in cols:
                if actual.strip().lower() == c.lower():
                    return actual
        for c in candidates:                       # fall back to a prefix match
            for actual in cols:
                if actual.strip().lower().startswith(c.lower()[:12]):
                    return actual
        return None

    c_pdb = col("#Pdb", "Pdb")
    c_mut = col("Mutation(s)_PDB", "Mutation(s)_cleaned", "Mutation(s)")
    c_kdm = col("Affinity_mut (M)", "Affinity_mut_parsed", "Affinity_mut")
    c_kdw = col("Affinity_wt (M)", "Affinity_wt_parsed", "Affinity_wt")
    c_t = col("Temperature")
    c_ref = col("Reference", "Protein 1", "Method")
    missing = [n for n, v in [("pdb", c_pdb), ("mutation", c_mut),
                              ("affinity_mut", c_kdm), ("affinity_wt", c_kdw)] if v is None]
    if missing:
        return [], [], [f"SKEMPI columns not found: {missing}; header was {cols[:10]}"]

    hits, skipped = [], []
    for row in rows:
        if not str(row.get(c_pdb, "")).upper().startswith(pdb.upper()):
            continue
        if not mutation_matches(row.get(c_mut), chain, resid, wt_letter, mut_letter):
            continue
        temp, assumed = parse_temperature(row.get(c_t) if c_t else None)
        try:
            ddg = ddg_from_kd(row.get(c_kdm), row.get(c_kdw), temp)
        except (TypeError, ValueError) as e:
            skipped.append({"reason": str(e), "kd_mut": row.get(c_kdm), "kd_wt": row.get(c_kdw)})
            continue
        hits.append({
            "ddg_kcal": round(ddg, 3),
            "kd_mut_M": row.get(c_kdm), "kd_wt_M": row.get(c_kdw),
            "temperature_k": temp, "temperature_assumed": assumed,
            "pdb_entry": row.get(c_pdb),
            "reference": (row.get(c_ref) if c_ref else None),
        })
    return hits, skipped, []


def check(csv_text=None, tolerance_kcal=0.75):
    """Check every benchmark's stored reference against SKEMPI. Returns the report dict."""
    import nr4a3_protein_fep as pf
    text = csv_text if csv_text is not None else fetch_skempi(
        cache_path=os.environ.get("SKEMPI_CACHE"))
    out = {"source": SKEMPI_URL, "tolerance_kcal": tolerance_kcal, "benchmarks": {}}
    for name, b in pb.BENCHMARKS.items():
        m = pf.classify_mutation(b["mutation"])
        hits, skipped, errors = records_for(text, b["pdb"], m["chain"], m["resid"],
                                            m["wt_letter"], m["mutant_letter"])
        entry = {"mutation": b["mutation"], "pdb": b["pdb"],
                 "stored_ref_ddg_kcal": b["ref_ddg_bind_kcal"],
                 "n_records": len(hits), "records": hits,
                 "skipped": skipped, "errors": errors}
        if hits:
            vals = sorted(r["ddg_kcal"] for r in hits)
            mid = vals[len(vals) // 2] if len(vals) % 2 else (vals[len(vals) // 2 - 1]
                                                              + vals[len(vals) // 2]) / 2
            entry["skempi_median_ddg_kcal"] = round(mid, 3)
            entry["skempi_range_kcal"] = [vals[0], vals[-1]]
            stored = float(b["ref_ddg_bind_kcal"])
            entry["delta_vs_stored"] = round(mid - stored, 3)
            # A SIGN disagreement is never agreement, however small the gap. This is not pedantry:
            # the stored Y29F value was +0.5 while SKEMPI gives -0.13 — the mutation slightly
            # STRENGTHENS binding rather than weakening it — and a magnitude-only check waved that
            # through on a 0.63 gap inside a 0.75 window. A benchmark whose reference points the
            # wrong way would score an engine's correct answer as wrong (and vice versa).
            # `near_zero` exempts references indistinguishable from zero, where sign is not meaningful.
            near_zero = abs(mid) < 0.25 and abs(stored) < 0.25
            sign_ok = near_zero or (mid >= 0) == (stored >= 0)
            entry["sign_agrees"] = sign_ok
            entry["agrees"] = bool(abs(entry["delta_vs_stored"]) <= tolerance_kcal and sign_ok)
            if entry["agrees"]:
                entry["verdict"] = "stored reference CONFIRMED by SKEMPI"
            elif not sign_ok:
                entry["verdict"] = (f"SIGN DISAGREEMENT — stored {stored:+.2f} vs SKEMPI {mid:+.2f} "
                                    f"kcal/mol. The stored reference has the mutation pointing the WRONG "
                                    f"WAY, so it would score a correct engine answer as wrong. Reconcile "
                                    f"the constant before any verdict is trusted.")
            else:
                entry["verdict"] = ("stored reference DISAGREES with SKEMPI — reconcile before the "
                                    "benchmark verdict is trusted; the pass criterion is computed "
                                    "against this number")
        else:
            entry["agrees"] = None
            entry["verdict"] = ("NOT FOUND in SKEMPI for this pdb/chain/mutation — the stored value "
                                "remains unverified; do not upgrade ref_verified on a null result")
        out["benchmarks"][name] = entry
    out["all_confirmed"] = all(v.get("agrees") is True for v in out["benchmarks"].values())
    out["note"] = ("This script never rewrites protfep_bench.BENCHMARKS. Reconciling the constants to "
                   "this report is a deliberate edit, so a database quirk cannot silently move the "
                   "engine's pass criterion.")
    return out


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Verify benchmark reference ddG values against SKEMPI 2.0")
    ap.add_argument("--out", default=None)
    ap.add_argument("--tolerance", type=float, default=0.75)
    args = ap.parse_args(argv)
    rep = check(tolerance_kcal=args.tolerance)
    txt = json.dumps(rep, indent=2)
    print(txt)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(txt + "\n")
    for name, e in rep["benchmarks"].items():
        print(f"\n{name}: stored {e['stored_ref_ddg_kcal']} kcal/mol | "
              f"SKEMPI {e.get('skempi_median_ddg_kcal')} (n={e['n_records']}) -> {e['verdict']}",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
