#!/usr/bin/env python3
"""SYNLETH-3 -- method-independence cross-check on the critical n.

The critical n in undecidability_anatomy.py is computed under Wilson. Wilson is anti-conservative
near a boundary, so the honest number is the one under exact Clopper-Pearson too. This recomputes
the smallest n at which each gene's verdict at the 0.20 cut is decided under CP, with the implied
count k = round(p*n), and reports both so the Wilson figure is not quoted as if method-free.
"""
import math, json, os, sys
from scipy.stats import beta

HERE = os.path.dirname(os.path.abspath(__file__))
Z = 1.959963984540054
CUT = 0.20
TARGETS = {"BAK1": 0.187, "EGFR": 0.205}


def wilson(p, n, z=Z):
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def cp(k, n, alpha=0.05):
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return (lo, hi)


def decided(lo, hi):
    return lo >= CUT or hi < CUT


out = {"cut": CUT, "note": "critical n is the smallest n from which the verdict stays decided; "
                           "reported under both interval methods, exact stored fraction (no "
                           "rounding widening), k = round(p*n)"}
for g, p in sorted(TARGETS.items()):
    rows = {}
    for name, f in (("wilson95", lambda n: wilson(p, n)),
                    ("clopper_pearson95", lambda n: cp(int(round(p * n)), n))):
        n_first = None
        n_stable = None
        run = 0
        for n in range(100, 200001):
            if decided(*f(n)):
                if n_first is None:
                    n_first = n
                run += 1
                if run >= 500 and n_stable is None:
                    n_stable = n - run + 1
                    break
            else:
                run = 0
                n_stable = None
        rows[name] = {"first_decided_n": n_first, "stably_decided_from_n": n_stable}
    out[g] = {"stored_rest_frac_dependent": p, "distance_to_cut": round(abs(p - CUT), 6),
              "methods": rows,
              "ratio_cp_to_wilson": (round(rows["clopper_pearson95"]["stably_decided_from_n"] /
                                           rows["wilson95"]["stably_decided_from_n"], 3)
                                     if rows["wilson95"]["stably_decided_from_n"] else None)}
    print("%-5s p=%.3f dist=%.3f  wilson: first=%s stable_from=%s | CP: first=%s stable_from=%s"
          % (g, p, abs(p - CUT),
             rows["wilson95"]["first_decided_n"], rows["wilson95"]["stably_decided_from_n"],
             rows["clopper_pearson95"]["first_decided_n"], rows["clopper_pearson95"]["stably_decided_from_n"]))

path = os.path.join(HERE, "cp-cross-check.json")
json.dump(out, open(path, "w"), indent=2)
print("wrote %s" % path)
