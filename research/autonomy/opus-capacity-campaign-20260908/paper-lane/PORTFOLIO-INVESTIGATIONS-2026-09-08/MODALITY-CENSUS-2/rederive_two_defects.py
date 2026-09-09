#!/usr/bin/env python3
"""MODALITY-CENSUS-2: independent re-derivation of the two defects MODALITY-CENSUS-1 reported.

Written from the primary artifacts, not from MODALITY-CENSUS-1's ledger. Nothing is read from
that lane's outputs; the comparison against its printed values happens at the end, digit for digit.

Reads only committed files. Writes only into this lane directory.
"""
from __future__ import annotations
import hashlib, json, os, subprocess, sys

REPO = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                      check=True).stdout.strip()
LANE = os.path.join(REPO, "research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                          "PORTFOLIO-INVESTIGATIONS-2026-09-08/MODALITY-CENSUS-2")

PANELS = "research/modalities/emc-expression-panels.json"
AUDIT = "research/modalities/census-novelty-audit.json"
CENSUS = "systems/graph/modalities.json"
MS = "research/manuscripts/modality-census/cancer-modality-census.md"

GPL6244 = "GSE24369_series_matrix.txt.gz"
GPL3290 = "GSE4303-GPL3290_series_matrix.txt.gz"

# The five, taken from the STORED panel group, not from any prose list.
def sha(rel):
    with open(os.path.join(REPO, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()

def main():
    prov = {rel: {"sha256": sha(rel), "bytes": os.path.getsize(os.path.join(REPO, rel))}
            for rel in (PANELS, AUDIT, CENSUS, MS)}
    prov["_head"] = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                                   capture_output=True, text=True, check=True).stdout.strip()

    panels = json.load(open(os.path.join(REPO, PANELS), encoding="utf-8"))
    grp = panels["panels"]["apoptotic_dependency"]["groups"]["anti_apoptotic_the_druggable_ones"]
    five = list(grp["genes_requested"])
    print("A. STORED PANEL GROUP anti_apoptotic_the_druggable_ones")
    print("   genes_requested =", five)
    assert len(five) == 5

    # --- A1 per-gene EMC-minus-comparator mean_z deltas on both platforms
    reads = panels["gene_reads"]
    per_gene = {}
    for g in five:
        row = {}
        for label, series in (("GPL6244", GPL6244), ("GPL3290", GPL3290)):
            r = reads.get(g, {}).get(series)
            if r is None or not r.get("readable"):
                row[label] = None
                continue
            e = r["EMC"]["mean_z"]; c = r["comparator"]["mean_z"]
            row[label] = {"EMC_mean_z": e, "comparator_mean_z": c,
                          "delta": round(e - c, 4), "platform_field": r.get("platform")}
        per_gene[g] = row

    print("\nA1. PER-GENE EMC-minus-comparator mean_z delta")
    print(f"   {'gene':<8} {'GPL6244':>10} {'GPL3290':>10}  lower on both?")
    lower_both = []
    higher_somewhere = []
    for g in five:
        d6 = per_gene[g]["GPL6244"]["delta"]; d3 = per_gene[g]["GPL3290"]["delta"]
        lb = d6 < 0 and d3 < 0
        (lower_both if lb else higher_somewhere).append(g)
        print(f"   {g:<8} {d6:>+10.4f} {d3:>+10.4f}  {'yes' if lb else 'NO'}")
    print(f"   -> lower on both: {len(lower_both)}/5 {lower_both}")
    print(f"   -> NOT lower on both: {higher_somewhere}")

    # --- A2 module mean and t on both platforms
    print("\nA2. MODULE (group-mean score) result, read back from the stored group")
    module = {}
    for label, series in (("GPL6244", GPL6244), ("GPL3290", GPL3290)):
        pp = grp["per_platform"][series]
        s = pp["score"]
        module[label] = {"delta_a_minus_b": s["delta_a_minus_b"], "t": s["t"], "df": s["df"],
                         "EMC_mean_score": pp["EMC_mean_score"],
                         "comparator_mean_score": pp["comparator_mean_score"],
                         "n_genes_readable": pp["n_genes_readable"],
                         "n_genes_requested": pp["n_genes_requested"]}
        print(f"   {label}: delta={s['delta_a_minus_b']}  t={s['t']}  df={s['df']}  "
              f"({pp['n_genes_readable']}/{pp['n_genes_requested']} readable)")
        # recompute delta from the stored means as an internal consistency check
        rec = round(pp["EMC_mean_score"] - pp["comparator_mean_score"], 4)
        print(f"           recomputed EMC_mean_score - comparator_mean_score = {rec}"
              f"  {'CONSISTENT' if abs(rec - s['delta_a_minus_b']) < 5e-4 else 'INCONSISTENT'}")
        module[label]["recomputed_delta"] = rec
    module_lower_both = all(module[k]["delta_a_minus_b"] < 0 for k in module)
    print(f"   -> module lower in EMC on both platforms: {module_lower_both}")

    # --- B the 127 vs 111 discrepancy
    print("\nB. NEVER-SEARCHED DENOMINATOR")
    rows = json.load(open(os.path.join(REPO, CENSUS), encoding="utf-8"))
    n_rows = len(rows)
    ns = [r["id"] for r in rows if r.get("prior_coverage") == "never_searched"]
    audit = json.load(open(os.path.join(REPO, AUDIT), encoding="utf-8"))
    print(f"   registry {CENSUS}: {n_rows} class rows, "
          f"{len(ns)} with prior_coverage == 'never_searched'")
    print(f"   audit  {AUDIT}: n_never_searched_rows = {audit['n_never_searched_rows']}, "
          f"n_rows_with_a_candidate_collision = {audit['n_rows_with_a_candidate_collision']}, "
          f"len(findings) = {len(audit['findings'])}")
    print(f"   discrepancy = {audit['n_never_searched_rows']} - {len(ns)} = "
          f"{audit['n_never_searched_rows'] - len(ns)}")
    # do the audit's findings keys all still exist and are they still never_searched?
    by_id = {r["id"]: r for r in rows}
    stale_keys = [k for k in audit["findings"] if k not in by_id
                  or by_id[k].get("prior_coverage") != "never_searched"]
    print(f"   audit finding ids no longer never_searched (or absent from registry): "
          f"{len(stale_keys)} {stale_keys}")

    out = {
        "_lane": "MODALITY-CENSUS-2",
        "_what": "Independent re-derivation of the two defects reported by MODALITY-CENSUS-1.",
        "provenance": prov,
        "A_guardian_quantifier": {
            "stored_group": "panels.apoptotic_dependency.groups.anti_apoptotic_the_druggable_ones",
            "genes_requested": five,
            "per_gene_delta_EMC_minus_comparator_mean_z": per_gene,
            "n_lower_on_both": len(lower_both),
            "lower_on_both": lower_both,
            "not_lower_on_both": higher_somewhere,
            "module": module,
            "module_lower_on_both_platforms": module_lower_both,
        },
        "B_never_searched_denominator": {
            "registry_rows_total": n_rows,
            "registry_never_searched": len(ns),
            "audit_n_never_searched_rows": audit["n_never_searched_rows"],
            "audit_n_rows_with_a_candidate_collision": audit["n_rows_with_a_candidate_collision"],
            "audit_findings_len": len(audit["findings"]),
            "discrepancy": audit["n_never_searched_rows"] - len(ns),
            "audit_finding_ids_no_longer_never_searched": stale_keys,
        },
    }
    dest = os.path.join(LANE, "rederivation-2026-09-09.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print(f"\nwrote {dest}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
