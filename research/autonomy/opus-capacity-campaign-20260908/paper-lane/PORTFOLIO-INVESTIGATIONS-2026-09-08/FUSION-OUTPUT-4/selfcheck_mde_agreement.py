#!/usr/bin/env python3
"""Self-check: the single-platform MDEs must equal FUSION-OUTPUT-2's own, digit for digit.

Dropping a cohort must not silently change the surviving cohort's arithmetic. This
compares every GSE24369 MDE recomputed in FUSION-OUTPUT-4 against the corresponding
value already published in FUSION-OUTPUT-2/design-power.json. Any difference is a
finding, printed digit for digit, and exits non-zero. No expression value is read.
"""
import json, sys
new = json.load(open(sys.argv[1]))
old = json.load(open(sys.argv[2]))
bad = []
for w in ("1000", "2000", "5000"):
    for c in ("A", "B"):
        if new["step_1_rederived_set_sizes"][w][c] != old["gene_counts"][w][c]:
            bad.append(("set size", w, c, old["gene_counts"][w][c],
                        new["step_1_rederived_set_sizes"][w][c]))
        for r, v in new["step_2_single_platform_mde"][w][c]["mde_GSE24369_only"].items():
            o = old["mde_per_gene_sd_units"][w][c]["GSE24369"][r]
            if v != o:
                bad.append(("MDE GSE24369", "%s/%s rho=%s" % (w, c, r), "", o, v))
        for r, v in new["step_2_single_platform_mde"][w][c]["mde_GSE4303_if_it_had_been_kept"].items():
            o = old["mde_per_gene_sd_units"][w][c]["GSE4303"][r]
            if v != o:
                bad.append(("MDE GSE4303", "%s/%s rho=%s" % (w, c, r), "", o, v))
        for r, v in new["step_2_single_platform_mde"][w][c]["effective_independent_genes"].items():
            o = old["effective_independent_genes"][w][c][r]
            if v != o:
                bad.append(("m_eff", "%s/%s rho=%s" % (w, c, r), "", o, v))
for b in bad:
    print("MISMATCH", b)
print("checked FUSION-OUTPUT-4 against FUSION-OUTPUT-2/design-power.json")
print("mismatches:", len(bad))
print("crosscheck.all_reproduce:", new["step_1_crosscheck"]["all_reproduce"])
sys.exit(1 if bad or not new["step_1_crosscheck"]["all_reproduce"] else 0)
