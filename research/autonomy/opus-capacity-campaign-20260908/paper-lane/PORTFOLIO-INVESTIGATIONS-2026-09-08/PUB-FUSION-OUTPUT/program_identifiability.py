#!/usr/bin/env python3
"""Outcome-blind identifiability check for the proposed EMC program-specificity test.

Question: if one scored the EWSR1::NR4A3 accessibility program (GSE243553, Frenkel et al.,
doi:10.1038/s41587-024-02347-4) as a gene set in EMC tumour expression, could the result be
attributed to THIS fusion rather than to a generic oncofusion accessibility program?

Inputs are membership only. NO expression value is read; no outcome is computed.
Input: outputs/common-platform-membership.tsv from the frozen source packet
       research/autonomy/nr4a3-program-source-2026-09-07 (coordinator-frozen, outcome-independent).
"""
import csv, json, sys, collections

SRC = sys.argv[1]
NR4A3 = ["EWSR1-NR4A3", "TAF15-NR4A3", "TCF12-NR4A3", "TFG-NR4A3"]
INDEX = "EWSR1-NR4A3"
FLOOR = 4  # manuscript's own set-score floor (>=4 genes), PUB-FUSION-OUTPUT Sec 2.3

mem = collections.defaultdict(lambda: collections.defaultdict(set))
with open(SRC) as fh:
    for r in csv.DictReader(fh, delimiter="\t"):
        mem[int(r["window_bp"])][r["program"]].add(r["symbol"])

out = {"input": SRC, "floor_genes": FLOOR, "windows": {}}
for w in sorted(mem):
    P = mem[w]
    progs = sorted(P)
    alt = [p for p in progs if p not in NR4A3]
    union_alt = set().union(*(P[p] for p in alt)) if alt else set()
    union_other_nr4a3 = set().union(*(P[p] for p in NR4A3 if p != INDEX and p in P))
    idx = P.get(INDEX, set())
    # uniqueness of every program against the union of all other 31 (baseline distribution)
    uniq_frac = {}
    for p in progs:
        others = set().union(*(P[q] for q in progs if q != p))
        uniq_frac[p] = (len(P[p] - others), len(P[p]),
                        round(len(P[p] - others) / len(P[p]), 4) if P[p] else None)
    best_container = max(((p, len(idx & P[p]) / len(idx) if idx else 0) for p in alt),
                         key=lambda t: t[1], default=(None, 0))
    out["windows"][w] = {
        "n_programs": len(progs),
        "index_program": INDEX,
        "index_size": len(idx),
        "index_minus_all_alternative_fusion_programs": sorted(idx - union_alt),
        "n_index_minus_alternatives": len(idx - union_alt),
        "n_index_minus_alternatives_and_other_NR4A3": len(idx - union_alt - union_other_nr4a3),
        "clears_set_floor_after_subtracting_alternatives": len(idx - union_alt) >= FLOOR,
        "max_single_alternative_containment": {"program": best_container[0],
                                               "fraction_of_index_covered": round(best_container[1], 4)},
        "jaccard_index_vs_other_NR4A3": {
            p: round(len(idx & P[p]) / len(idx | P[p]), 4) for p in NR4A3 if p != INDEX and p in P},
        "uniqueness_fraction_all_programs": uniq_frac,
        "classA_gene_membership": {g: sorted(p for p in progs if g in P[p])
                                   for g in ("ENO3", "PPARG", "SEMA3C")},
    }
json.dump(out, sys.stdout, indent=1, sort_keys=True)
print()
