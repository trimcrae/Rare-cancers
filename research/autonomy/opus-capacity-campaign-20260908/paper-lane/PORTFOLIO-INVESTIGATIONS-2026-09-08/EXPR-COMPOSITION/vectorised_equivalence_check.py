#!/usr/bin/env python3
"""Prove the vectorised permutation core equals the plain per-gene rank-partial-correlation
implementation it replaced. The first (aborted) attempt, checks/03, used the plain loop; it was
too slow for the checkpoint, not wrong. This check makes the substitution auditable.

Compares, gene by gene on BOTH frames and BOTH platforms, with the real labels:
  adjusted_r(...)  (vectorised)   vs   partial_rank(...)  (plain, one gene at a time)
  unadjusted_r(...) (vectorised)  vs   spearman(...)      (plain)
Exit 0 only if the maximum absolute difference is below 1e-9 everywhere.
"""
import json, sys
import numpy as np
import composition_adjusted_contrast as M

def main():
    d = json.load(open(M.SRC))
    cs = {}
    for pkey in (M.P1, M.P2):
        plat = d["platforms"][pkey]
        cols = list(plat["EMC_gsms"]) + list(plat["comparator_gsms"])
        cs[pkey] = M.composition_scores(d, pkey, cols)
    worst_a = worst_u = 0.0
    n_cmp = 0
    for fname, (syms, src) in M.frames(d).items():
        p1, p2 = M._frame_setup(d, fname, syms, src, cs)
        for tag, pk in (("GPL6244", p1), ("GPL3290", p2)):
            va = M.adjusted_r(pk["groups"], pk["G"], pk["lab"], pk["lookup"])
            vu = M.unadjusted_r(pk["groups"], pk["G"], pk["lab"])
            for i, sym in enumerate(syms):
                if not np.isfinite(va[i]):
                    continue
                ck = ("LOO:" + sym) if sym in M.MARKERS else "C"
                cov = pk["lookup"][ck]
                ok = np.isfinite(pk["Z"][i]) & np.isfinite(cov)
                pa = M.partial_rank(pk["Z"][i][ok], pk["lab"][ok], [cov[ok]])
                pu = M.spearman(pk["Z"][i][ok], pk["lab"][ok])
                worst_a = max(worst_a, abs(pa - va[i]))
                worst_u = max(worst_u, abs(pu - vu[i]))
                n_cmp += 1
            print("%-10s %-8s cumulative max |delta| adjusted %.3e  unadjusted %.3e  (n=%d)"
                  % (fname, tag, worst_a, worst_u, n_cmp))
    ok = worst_a < 1e-9 and worst_u < 1e-9
    print("\nEQUIVALENCE %s  max|delta| adjusted %.3e unadjusted %.3e over %d gene x platform x frame"
          % ("PASS" if ok else "FAIL", worst_a, worst_u, n_cmp))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
