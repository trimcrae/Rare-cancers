#!/usr/bin/env python3
"""Calibrate the class-A genes' membership across the 32 GSE243553 accessibility programs.

For each gene present in >=1 program at the frozen 2 kb window, count how many of the 32 programs
contain it. Report the empirical distribution and where ENO3 / PPARG / SEMA3C sit in it, plus the
per-program size context. Membership only; no expression value is read.
"""
import csv, sys, json, collections
SRC = sys.argv[1]; W = 2000
P = collections.defaultdict(set)
with open(SRC) as fh:
    for r in csv.DictReader(fh, delimiter="\t"):
        if int(r["window_bp"]) == W:
            P[r["program"]].add(r["symbol"])
cnt = collections.Counter()
for p, g in P.items():
    for s in g:
        cnt[s] += 1
dist = collections.Counter(cnt.values())
n_genes = len(cnt)
def pct_at_least(k):
    return round(sum(v for kk, v in dist.items() if kk >= k) / n_genes, 4)
res = {"window_bp": W, "n_programs": len(P), "n_genes_in_any_program": n_genes,
       "programs_per_gene_distribution": {str(k): dist[k] for k in sorted(dist)},
       "program_sizes": {p: len(g) for p, g in sorted(P.items())},
       "class_A": {}}
for g in ("ENO3", "PPARG", "SEMA3C"):
    k = cnt.get(g, 0)
    res["class_A"][g] = {"n_programs_containing": k,
                         "programs": sorted(p for p in P if g in P[p]),
                         "fraction_of_program_genes_in_>=k_programs": pct_at_least(k) if k else None,
                         "in_EWSR1-NR4A3_program": g in P.get("EWSR1-NR4A3", set())}
json.dump(res, sys.stdout, indent=1)
print()
