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


def parse_skempi(csv_text):
    """Parse the SKEMPI CSV into (rows, columns, errors). Pure.

    SKEMPI's header names have drifted between releases, so the column a caller wants is resolved by
    exact-then-prefix match rather than hardcoded. That resolution is knowledge about the database
    and has exactly ONE home: this function. `records_for` and `scan_wedge_band` both read it here,
    so a header rename cannot fix one consumer and silently break the other.

    `columns` is a dict with keys pdb / mutation / kd_mut / kd_wt / temperature / reference. The four
    load-bearing ones are reported in `errors` if absent, rather than yielding an empty result that
    reads like "this mutation is not in SKEMPI".
    """
    import csv as _csv
    import io

    rows = list(_csv.DictReader(io.StringIO(csv_text), delimiter=";"))
    if not rows:
        return [], {}, []
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

    columns = {
        "pdb": col("#Pdb", "Pdb"),
        "mutation": col("Mutation(s)_PDB", "Mutation(s)_cleaned", "Mutation(s)"),
        "kd_mut": col("Affinity_mut (M)", "Affinity_mut_parsed", "Affinity_mut"),
        "kd_wt": col("Affinity_wt (M)", "Affinity_wt_parsed", "Affinity_wt"),
        "temperature": col("Temperature"),
        "reference": col("Reference", "Protein 1", "Method"),
    }
    missing = [n for n in ("pdb", "mutation", "kd_mut", "kd_wt") if columns[n] is None]
    errors = ([f"SKEMPI columns not found: {missing}; header was {cols[:10]}"] if missing else [])
    return rows, columns, errors


def records_for(csv_text, pdb, chain, resid, wt_letter, mut_letter):
    """Every SKEMPI record for one single-point mutation of one complex. Pure.

    Returns a list of {ddg_kcal, kd_mut, kd_wt, temperature_k, reference, ...}. Records whose
    affinities are missing or unparseable are reported as skipped rather than dropped silently.
    """
    rows, columns, errors = parse_skempi(csv_text)
    if not rows:
        return [], [], []
    if errors:
        return [], [], errors
    c_pdb, c_mut = columns["pdb"], columns["mutation"]
    c_kdm, c_kdw = columns["kd_mut"], columns["kd_wt"]
    c_t, c_ref = columns["temperature"], columns["reference"]

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


# ------------------------------------------------------------------------------------------------
# The WEDGE-SIZED benchmark gap
# ------------------------------------------------------------------------------------------------
# nr4a3-program-map.md (RUNG 5a-KS, "THE MOST DECISION-RELEVANT RESULT IS THE NOISE STRUCTURE") records that
# the qualified benchmark set brackets the wedge without covering it: a +3.4 kcal/mol hot-spot
# knockout and a ~0 near-null control, with NOTHING at the size the wedge actually measures. Its
# conclusion is quoted there and is the single home for it: *"the right validation for 5a-KS is a
# benchmark sized like the wedge, not a hot-spot knockout. That benchmark does not exist yet, and
# until it does the confirmatory line may not claim to resolve a paralogue-scale difference."*
#
# This scanner is the $0 half of closing that gap: it finds the CANDIDATES from primary data. The
# band's endpoints are NOT invented here — they are the wedge's own expected effect size, stated
# once in nr4a3-program-map.md's "Honest expectation, recorded BEFORE the run" for the matched pair. Anything
# smaller is the near-null control we already have; anything larger is the hot spot we already have.
WEDGE_BAND_KCAL = (0.5, 1.5)

# A reference is only as good as its own reproducibility. If independent SKEMPI records for the same
# mutation disagree by more than the band is wide, the "measured answer" is not resolved to
# wedge scale and scoring an engine against its median would be scoring it against noise. This is
# the same discipline as `check()`'s sign guard: a benchmark that cannot discriminate must not be
# allowed to look like one.
MAX_RECORD_SPREAD_KCAL = WEDGE_BAND_KCAL[1] - WEDGE_BAND_KCAL[0]


def _median(values):
    """Median of a non-empty sequence. Pure."""
    v = sorted(values)
    mid = len(v) // 2
    return v[mid] if len(v) % 2 else (v[mid - 1] + v[mid]) / 2.0


def scan_wedge_band(csv_text, pdb, chains=None, band=WEDGE_BAND_KCAL,
                    max_spread_kcal=MAX_RECORD_SPREAD_KCAL):
    """Find wedge-SIZED, charge-conserving, buildable single mutations of one complex. Pure.

    Scans every SKEMPI record for `pdb`, recomputes ddG from the deposited Kd pair (never from a
    remembered table cell — the same route `check()` uses, and the route that caught a wrong-SIGNED
    stored reference), groups independent records per mutation, and returns candidates ranked
    best-first.

    A candidate must clear FOUR filters, each of which exists because failing it would produce a
    benchmark that looks valid and is not:
      1. **charge-conserving** — a charge-changing mutation under PME carries a system-size-dependent
         finite-size artifact that does not cancel between the two differently-sized boxes, so engine
         error would be confounded with the artifact (`nr4a3_protein_fep` blocker 2).
      2. **buildable** — PRO/GLY alter the backbone, so the hybrid is not a side-chain swap.
      3. **|median ddG| inside `band`** — the whole point; see WEDGE_BAND_KCAL.
      4. **record spread <= `max_spread_kcal`** — the reference must itself be resolved at wedge scale.

    `chains` optionally restricts to chains we can actually stage (for 1BRS: barstar 'D' carries the
    mutation and barnase 'A' is the partner). A mutation on a chain the staging layer cannot cut is
    not a candidate however good its number is.

    Returns a report dict. It NEVER edits `protfep_bench.BENCHMARKS` — promoting a candidate to a
    benchmark is a deliberate edit, exactly as `check()` refuses to rewrite a reference, so a
    database quirk cannot quietly install a new pass criterion.
    """
    import nr4a3_protein_fep as pf

    lo, hi = float(band[0]), float(band[1])
    rows, columns, errors = parse_skempi(csv_text)
    out = {
        "source": SKEMPI_URL, "pdb": pdb, "chains": sorted(chains) if chains else None,
        "band_kcal": [lo, hi], "max_record_spread_kcal": float(max_spread_kcal),
        "n_rows_scanned": len(rows), "errors": list(errors),
        "candidates": [], "rejected": [], "n_candidates": 0, "n_rejected": 0,
        "note": ("Candidates only. This script never edits protfep_bench.BENCHMARKS — promoting one "
                 "is a deliberate edit, so a database quirk cannot silently move the pass criterion."),
    }
    # An empty table is NOT the finding "no wedge-sized mutation exists" — that is a scientific
    # claim, and a failed download or a renamed header must never be able to make it. Report the
    # load failure instead, with the counts present so a caller cannot read a bare 0 as a result.
    if not rows:
        out["errors"].append("SKEMPI parsed to ZERO rows — the database did not load; this is a "
                             "load failure, not the finding that no wedge-sized mutation exists")
    if out["errors"]:
        return out

    c_pdb, c_mut = columns["pdb"], columns["mutation"]
    c_kdm, c_kdw = columns["kd_mut"], columns["kd_wt"]
    c_t, c_ref = columns["temperature"], columns["reference"]

    # Group every parseable single-mutation record by its mutation cell.
    grouped = {}
    for row in rows:
        if not str(row.get(c_pdb, "")).upper().startswith(pdb.upper()):
            continue
        cell = str(row.get(c_mut) or "").strip().upper()
        if not cell or "," in cell or len(cell) < 4:
            continue                                    # multi-mutants are a different quantity
        temp, assumed = parse_temperature(row.get(c_t) if c_t else None)
        try:
            ddg = ddg_from_kd(row.get(c_kdm), row.get(c_kdw), temp)
        except (TypeError, ValueError):
            continue
        grouped.setdefault(cell, []).append({
            "ddg_kcal": round(ddg, 3), "kd_mut_M": row.get(c_kdm), "kd_wt_M": row.get(c_kdw),
            "temperature_k": temp, "temperature_assumed": assumed,
            "pdb_entry": row.get(c_pdb), "reference": (row.get(c_ref) if c_ref else None),
        })

    for cell, recs in sorted(grouped.items()):
        # SKEMPI writes <WT><CHAIN><RESI><MUT>; our engine wants 'CHAIN:WT<resi>MUT'.
        wt_letter, chain, mut_letter, resid = cell[0], cell[1], cell[-1], cell[2:-1]
        if not resid.isdigit():
            continue
        spec = f"{chain}:{wt_letter}{resid}{mut_letter}"
        try:
            m = pf.classify_mutation(spec)
        except pf.MutationError as e:
            out["rejected"].append({"mutation": spec, "reason": f"unparseable: {e}"})
            continue

        vals = [r["ddg_kcal"] for r in recs]
        median = round(_median(vals), 3)
        spread = round(max(vals) - min(vals), 3)
        entry = {
            "mutation": spec, "skempi_cell": cell, "chain": chain,
            "skempi_median_ddg_kcal": median, "skempi_range_kcal": [min(vals), max(vals)],
            "record_spread_kcal": spread, "n_records": len(recs),
            "charge_change": m["charge_change"], "buildable": m["buildable"],
            "records": recs,
        }

        reason = None
        if chains and chain not in chains:
            reason = f"chain {chain} is not stageable for this complex (stageable: {sorted(chains)})"
        elif not m["buildable"]:
            reason = m["risk"]
        elif m["charge_changing"]:
            reason = m["risk"]
        elif not (lo <= abs(median) <= hi):
            reason = (f"|{median:+.3f}| is outside the wedge band [{lo}, {hi}] — "
                      f"{'a near-null, already covered by the Y29F control' if abs(median) < lo else 'a hot spot, already covered by Y29A'}")
        elif spread > max_spread_kcal:
            reason = (f"independent records span {spread:.3f} kcal/mol (> {max_spread_kcal}), so the "
                      f"reference is not itself resolved at wedge scale — scoring against its median "
                      f"would be scoring against noise")
        if reason:
            entry["reason"] = reason
            out["rejected"].append(entry)
        else:
            out["candidates"].append(entry)

    # Best first: most independent records, then tightest spread, then closest to the band's middle
    # (a candidate at an endpoint is one revision away from falling out of the band).
    mid = (lo + hi) / 2.0
    out["candidates"].sort(key=lambda e: (-e["n_records"], e["record_spread_kcal"],
                                          abs(abs(e["skempi_median_ddg_kcal"]) - mid)))
    out["n_candidates"] = len(out["candidates"])
    out["n_rejected"] = len(out["rejected"])
    return out


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
    ap.add_argument("--wedge-scan", action="store_true",
                    help="scan SKEMPI for WEDGE-SIZED charge-conserving candidates instead of "
                         "verifying the stored references (see scan_wedge_band)")
    ap.add_argument("--wedge-pdb", default="1BRS",
                    help="complex to scan; defaults to the one whose staging is already proven")
    ap.add_argument("--wedge-chains", default="",
                    help="comma-separated stageable chains, e.g. 'A,D'; empty = no chain filter")
    args = ap.parse_args(argv)

    if args.wedge_scan:
        chains = {c.strip().upper() for c in args.wedge_chains.split(",") if c.strip()} or None
        text = fetch_skempi(cache_path=os.environ.get("SKEMPI_CACHE"))
        rep = scan_wedge_band(text, args.wedge_pdb, chains=chains)
        txt = json.dumps(rep, indent=2)
        print(txt)
        if args.out:
            with open(args.out, "w") as fh:
                fh.write(txt + "\n")
        print(f"\n{args.wedge_pdb}: {rep.get('n_candidates', 0)} wedge-sized candidates from "
              f"{rep['n_rows_scanned']} scanned rows ({rep.get('n_rejected', 0)} rejected)",
              file=sys.stderr)
        for e in rep["candidates"][:10]:
            print(f"  {e['mutation']:<10} {e['skempi_median_ddg_kcal']:+.3f} kcal/mol  "
                  f"n={e['n_records']} spread={e['record_spread_kcal']:.3f}", file=sys.stderr)
        if not rep["candidates"]:
            print("  NONE — the gap is not closable on this complex; scan another or say so plainly.",
                  file=sys.stderr)
        return 0

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
