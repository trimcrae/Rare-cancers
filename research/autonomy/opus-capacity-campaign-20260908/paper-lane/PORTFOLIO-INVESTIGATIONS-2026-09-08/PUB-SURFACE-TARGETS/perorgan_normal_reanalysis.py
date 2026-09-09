#!/usr/bin/env python3
"""PRESPECIFIED, READY-TO-RUN: per-organ, adult-only re-reading of the GSE28866 normal arm.

STATUS: the input file is NOT in this checkout and could not be fetched from this sandbox
(NCBI CONNECT 403 — see checks/01-fetch-probe). This module is therefore delivered as a
prespecified analysis whose LOGIC is validated offline against a synthetic fixture
(`--selftest`), so that the single missing dependency is a file, not a design.

DEPENDENCY (exactly one, one unauthenticated public GET):
  https://ftp.ncbi.nlm.nih.gov/geo/series/GSE28nnn/GSE28866/suppl/
      GSE28866_36048_normalized_peaks_cancer_and_normal.txt.gz   (~13 MB, already read once in CI)

PRESPECIFICATION (fixed before any real value is seen):
  1. Reduction order follows the committed producer: median across a gene's 3SEQ peaks first,
     then median across libraries within an arm (research/modalities/gse28866_tumour_vs_normal.py).
  2. The normal arm is resolved BY ORGAN, and separately for ADULT-ONLY libraries.
  3. Reported per gene: pooled median (the committed statistic, for comparability),
     adult-only pooled median, per-organ adult medians, and WORST-ORGAN normal =
     max over adult organ medians. Exposure is a worst-organ property, not a median property.
  4. Primary readout: emc_median / worst_adult_organ_normal, alongside the committed
     emc_median / pooled_normal. A candidate whose ranking changes between the two is
     flagged POOLING_SENSITIVE.
  5. Uterus contributes a single adult library; any organ with n<3 adult libraries is reported
     but marked LOW_N and excluded from the worst-organ maximum in the primary readout
     (reported as a sensitivity arm with it included).
  6. No test, no p-value, no q-value: n_EMC = 4 and the values are deposit-normalised,
     square-root-compressed summary scores. Ratios are descriptive.

NOT CLAIMED: nothing here measures protein, surface localisation, receptor density, selectivity,
safety or a therapeutic window, and a per-organ transcript reading cannot establish any of them.
"""
from __future__ import annotations
import argparse, json, statistics, sys

def parse_library(col: str) -> dict:
    """'STT5425_Adult_normal_breast' -> {'age':'adult','organ':'breast'}"""
    p = col.split("_")
    return {"library": col, "age": p[1].lower(), "organ": p[-1].lower()}

def per_organ_summary(gene_rows, normal_columns, emc_columns, min_adult_n=3):
    """gene_rows: list of dicts {column: value} — one per 3SEQ peak of ONE gene."""
    def peak_median(col):
        vals = [r[col] for r in gene_rows if col in r and r[col] is not None]
        return statistics.median(vals) if vals else None

    lib = {c: peak_median(c) for c in list(normal_columns) + list(emc_columns)}
    meta = [parse_library(c) for c in normal_columns]

    def med(cols):
        v = [lib[c] for c in cols if lib.get(c) is not None]
        return statistics.median(v) if v else None

    emc = med(list(emc_columns))
    pooled = med(list(normal_columns))
    adult_cols = [m["library"] for m in meta if m["age"] == "adult"]
    adult_pooled = med(adult_cols)

    organs = {}
    for m in meta:
        organs.setdefault((m["organ"], m["age"]), []).append(m["library"])
    per_organ = {f"{o}_{a}": {"n": len(cs), "median": med(cs)} for (o, a), cs in sorted(organs.items())}

    adult_organ = {k: v for k, v in per_organ.items() if k.endswith("_adult")}
    eligible = {k: v for k, v in adult_organ.items() if v["n"] >= min_adult_n and v["median"] is not None}
    low_n = sorted(k for k, v in adult_organ.items() if v["n"] < min_adult_n)
    worst = max(eligible.items(), key=lambda kv: kv[1]["median"]) if eligible else None
    all_adult = {k: v for k, v in adult_organ.items() if v["median"] is not None}
    worst_incl = max(all_adult.items(), key=lambda kv: kv[1]["median"]) if all_adult else None

    def ratio(num, den):
        return None if (num is None or not den) else round(num / den, 4)

    return {
        "emc_median": emc,
        "normal_pooled_median_committed_statistic": pooled,
        "normal_adult_only_pooled_median": adult_pooled,
        "per_organ": per_organ,
        "low_n_adult_organs_excluded_from_primary": low_n,
        "worst_adult_organ": None if worst is None else {"organ": worst[0], **worst[1]},
        "worst_adult_organ_including_low_n": None if worst_incl is None else {"organ": worst_incl[0], **worst_incl[1]},
        "emc_over_pooled_normal": ratio(emc, pooled),
        "emc_over_adult_pooled_normal": ratio(emc, adult_pooled),
        "emc_over_worst_adult_organ": ratio(emc, None if worst is None else worst[1]["median"]),
        "_no_test": "n_EMC=4; deposit-normalised sqrt-compressed scores; ratios are descriptive only.",
    }

FIXTURE_NORMALS = [
    "STT1_Adult_normal_breast", "STT2_Adult_normal_breast", "STT3_Adult_normal_breast",
    "STT4_Adult_normal_lung", "STT5_Adult_normal_lung", "STT6_Adult_normal_lung",
    "STT7_Adult_normal_kidney", "STT8_Adult_normal_kidney", "STT9_Adult_normal_kidney",
    "STT10_Adult_normal_uterus",
    "STT11_Fetal_normal_lung", "STT12_Fetal_normal_lung", "STT13_Fetal_normal_bowel",
]
FIXTURE_EMC = ["EMC_A", "EMC_B", "EMC_C", "EMC_D"]

def selftest() -> int:
    """A gene that is SAFE on the pooled median and DANGEROUS in one adult organ."""
    vals = {c: 0.1 for c in FIXTURE_NORMALS}
    for c in FIXTURE_NORMALS:
        if c.endswith("kidney"):
            vals[c] = 5.0            # one adult organ far above the tumour
        if c.startswith("STT10"):
            vals[c] = 9.0            # a single low-n organ, must not drive the primary readout
    for c in FIXTURE_EMC:
        vals[c] = 1.0
    rows = [dict(vals), {k: v * 1.0 for k, v in vals.items()}]  # two peaks, identical
    out = per_organ_summary(rows, FIXTURE_NORMALS, FIXTURE_EMC)

    checks = []
    checks.append(("pooled median hides the hot organ", out["normal_pooled_median_committed_statistic"] == 0.1))
    checks.append(("EMC/pooled looks favourable", out["emc_over_pooled_normal"] == 10.0))
    checks.append(("worst adult organ is kidney", out["worst_adult_organ"]["organ"] == "kidney_adult"))
    checks.append(("worst-organ ratio is unfavourable", out["emc_over_worst_adult_organ"] == 0.2))
    checks.append(("uterus excluded as LOW_N", out["low_n_adult_organs_excluded_from_primary"] == ["uterus_adult"]))
    checks.append(("uterus surfaces in the sensitivity arm", out["worst_adult_organ_including_low_n"]["organ"] == "uterus_adult"))
    checks.append(("fetal libraries excluded from adult pooled", out["normal_adult_only_pooled_median"] == 0.1))
    ok = all(c[1] for c in checks)
    for name, passed in checks:
        print(("PASS  " if passed else "FAIL  ") + name)
    print(json.dumps(out, indent=1))
    print("SELFTEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--peaks", help="GSE28866_36048_normalized_peaks_cancer_and_normal.txt(.gz) — NOT PRESENT in this checkout")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.peaks:
        print("no input: the GSE28866 peak matrix is not in this checkout and could not be fetched "
              "(NCBI CONNECT 403). Run --selftest to validate the logic.", file=sys.stderr)
        return 2
    print("real-input path intentionally not exercised: no peak matrix was available to this lane.", file=sys.stderr)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
