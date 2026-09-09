#!/usr/bin/env python3
"""Independent re-derivation of the FET-class transfer falsification (MTAP-PRMT5-2).

Written without reusing PUB-MTAP-PRMT5/fet_class_transfer_test.py. Sole input is the
committed panel artifact. Recomputes, for PRMT5 on GSE24369/GPL6244:
  (a) the FET comparator (LGFMS, FUS::CREB3L2) vs the non-FET comparators
      (desmoid_fibromatosis + fibrosarcoma) Welch t and permutation p  -- the falsification;
  (b) the manuscript's headline EMC vs all-comparators Welch t (published +6.24) as a baseline;
  (c) EMC vs FET comparator, and EMC vs non-FET.
No network, no new data, no manuscript edit.
"""
import json, math, itertools, sys
import numpy as np

PANEL = "research/modalities/emc-expression-panels.json"
SERIES = "GSE24369_series_matrix.txt.gz"
FET = {"LGFMS"}
NONFET = {"desmoid_fibromatosis", "fibrosarcoma"}

def welch_t(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    na, nb = len(a), len(b)
    va, vb = a.var(ddof=1), b.var(ddof=1)
    se = math.sqrt(va/na + vb/nb)
    return (a.mean() - b.mean()) / se

def welch_t_vec(A, B):
    # A: (k, na), B: (k, nb) -> (k,)
    na, nb = A.shape[1], B.shape[1]
    va, vb = A.var(axis=1, ddof=1), B.var(axis=1, ddof=1)
    return (A.mean(axis=1) - B.mean(axis=1)) / np.sqrt(va/na + vb/nb)

def perm_p(a, b, seed, draws, enum_cap=400000):
    obs = abs(welch_t(a, b))
    pool = np.concatenate([np.asarray(a, float), np.asarray(b, float)])
    n, na = len(pool), len(a)
    n_lab = math.comb(n, na)
    if n_lab <= enum_cap:
        hits = 0
        idx = np.arange(n)
        for combo in itertools.combinations(range(n), na):
            m = np.zeros(n, bool); m[list(combo)] = True
            t = welch_t(pool[m], pool[~m])
            if abs(t) >= obs - 1e-12: hits += 1
        return dict(mode="exact", p=hits/n_lab, at_least_as_extreme=hits,
                    labelings=n_lab, draws=None, se=None, seed=None)
    rng = np.random.default_rng(seed)
    hits = 0
    block = 20000
    done = 0
    while done < draws:
        k = min(block, draws - done)
        perm = np.argsort(rng.random((k, n)), axis=1)
        P = pool[perm]
        t = np.abs(welch_t_vec(P[:, :na], P[:, na:]))
        hits += int((t >= obs - 1e-12).sum())
        done += k
    p = hits/draws
    se = math.sqrt(max(p*(1-p), 1e-12)/draws)
    return dict(mode="monte_carlo", p=p, at_least_as_extreme=hits,
                labelings=n_lab, draws=draws, se=round(se, 6), seed=seed)

def main():
    panel = json.load(open(PANEL))
    out = {"_what": "MTAP-PRMT5-2 independent re-derivation of the FET-class null",
           "input": PANEL, "series": SERIES, "platform": "GPL6244", "genes": {}}
    for gene in ["PRMT5", "MTAP", "CDKN2A", "NR4A3"]:
        blk = panel["gene_reads"][gene][SERIES]
        by = {}
        for s in blk["per_sample"]:
            by.setdefault(s["class"], []).append(s["z_vs_array"])
        emc = by["EMC"]
        fet = [v for c, vs in by.items() if c in FET for v in vs]
        non = [v for c, vs in by.items() if c in NONFET for v in vs]
        allc = fet + non
        g = {"n_by_class": {c: len(v) for c, v in sorted(by.items())},
             "mean_z_by_class": {c: round(float(np.mean(v)), 4) for c, v in sorted(by.items())}}
        for name, (a, b, seed, draws) in {
            "emc_vs_all_comparators": (emc, allc, 424242, 200000),
            "emc_vs_fet": (emc, fet, 424243, 200000),
            "emc_vs_nonfet": (emc, non, 424244, 200000),
            "fet_vs_nonfet": (fet, non, 424245, 1000000),
        }.items():
            t = welch_t(a, b)
            g[name] = {"t": round(float(t), 4), "n_a": len(a), "n_b": len(b),
                       "delta_mean_z": round(float(np.mean(a) - np.mean(b)), 4),
                       "permutation": perm_p(a, b, seed, draws)}
        out["genes"][gene] = g
    json.dump(out, sys.stdout, indent=2)
    print()

if __name__ == "__main__":
    main()
