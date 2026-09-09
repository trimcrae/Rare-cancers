#!/usr/bin/env python3
"""Size-weighted calibration of the class-A genes' cross-program membership counts.

A gene in a large program is counted more often, so a raw 'in k of 32 programs' count is confounded
by program size. Here the common-platform universe is reconstructed from the same two sources the
frozen packet used (TPM symbol universe x GPL6244 gene-to-probes map), and each gene's expected
membership count under random program membership is sum_p (|program_p| / |universe|). The
Poisson-binomial tail P(K >= k) is computed exactly by convolution. Membership only.
"""
import csv, json, sys, collections
PKT = sys.argv[1]; W = 2000
tpm = {l.strip() for l in open(f"{PKT}/sources/tpm-symbol-universe.txt") if l.strip()}
arr = set(json.load(open(f"{PKT}/sources/GPL6244-gene-to-probes.json")))
uni = tpm & arr
P = collections.defaultdict(set)
with open(f"{PKT}/outputs/common-platform-membership.tsv") as fh:
    for r in csv.DictReader(fh, delimiter="\t"):
        if int(r["window_bp"]) == W:
            P[r["program"]].add(r["symbol"])
progs = sorted(P)
probs = [len(P[p]) / len(uni) for p in progs]
dist = [1.0]
for q in probs:
    nd = [0.0] * (len(dist) + 1)
    for i, v in enumerate(dist):
        nd[i] += v * (1 - q); nd[i + 1] += v * q
    dist = nd
def tail(k): return sum(dist[k:])
cnt = collections.Counter()
for p in progs:
    for s in P[p]: cnt[s] += 1
out = {"window_bp": W, "universe_size": len(uni), "universe_sources": [
        f"{PKT}/sources/tpm-symbol-universe.txt", f"{PKT}/sources/GPL6244-gene-to-probes.json"],
       "expected_programs_per_gene": round(sum(probs), 4),
       "class_A": {g: {"observed_k": cnt.get(g, 0), "poisson_binomial_P_ge_k": round(tail(cnt.get(g, 0)), 6),
                       "in_EWSR1-NR4A3": g in P["EWSR1-NR4A3"]} for g in ("ENO3","PPARG","SEMA3C")},
       "observed_genes_with_k_ge_6": sum(1 for v in cnt.values() if v >= 6),
       "expected_genes_with_k_ge_6": round(tail(6) * len(uni), 2)}
json.dump(out, sys.stdout, indent=1); print()
