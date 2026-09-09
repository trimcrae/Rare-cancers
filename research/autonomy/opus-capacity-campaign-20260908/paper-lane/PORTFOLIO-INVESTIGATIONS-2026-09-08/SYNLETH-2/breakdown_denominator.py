#!/usr/bin/env python3
"""
SYNLETH-2 sensitivity: how much denominator ignorance can the pan-essential-trap screen absorb?

Section D of denominator_envelope.py evaluates the screen at n_min = 943, the smallest denominator
my stated admissibility rule permits. That rule is an assumption. This check removes the dependence
on it: it scans n DOWNWARD from 2105 and reports the largest n at which the screen stops being
fully decided (some record's 95% interval straddles the cut). Read-only, same artifact.
"""
import json, math, os, sys
from scipy.stats import beta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
ART = os.path.join(ROOT, "research/modalities/depmap-sarcoma-dependency.json")
Z = 1.959963984540054
HALF = 5e-4

def wilson(p, n, z=Z):
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)

def cp(k, n, a=0.05):
    lo = 0.0 if k == 0 else float(beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 1, n - k))
    return lo, hi

def recs(d):
    out = []
    def w(o):
        if isinstance(o, dict):
            if "rest_frac_dependent" in o and "n_sarcoma" in o: out.append(o)
            else: [w(v) for v in o.values()]
        elif isinstance(o, list): [w(v) for v in o]
    w(d); return out

def main():
    d = json.load(open(ART)); rs = recs(d)
    res = {"input": ART, "n_records": len(rs), "method": "scan n downward; a cut is FULLY DECIDED at n "
           "iff no record's 95% interval straddles it, under BOTH Wilson (widened by the +/-5e-4 "
           "rounding on the point value) and Clopper-Pearson"}
    for cut in (0.80, 0.20):
        first_bad, bad_genes = None, []
        for n in range(2105, 9, -1):
            bad = []
            for r in rs:
                p = r["rest_frac_dependent"]
                wlo = wilson(max(0.0, p - HALF), n)[0]; whi = wilson(min(1.0, p + HALF), n)[1]
                k = max(0, min(n, round(p * n))); clo, chi = cp(k, n)
                lo, hi = min(wlo, clo), max(whi, chi)
                if lo < cut <= hi or (lo <= cut and hi >= cut and not (hi < cut or lo >= cut)):
                    bad.append((r["gene"], p))
            if bad:
                first_bad, bad_genes = n, sorted({g for g, _ in bad}); break
        res["cut_%.2f" % cut] = {
            "largest_n_at_which_screen_is_NOT_fully_decided": first_bad,
            "first_genes_to_go_fragile": bad_genes,
            "screen_fully_decided_for_all_n_greater_than": first_bad,
        }
        print("cut %.2f: fully decided for every n > %s ; first fragile gene(s) at n=%s: %s"
              % (cut, first_bad, first_bad, bad_genes))
    out = os.path.join(os.path.dirname(__file__), "breakdown-denominator.json")
    json.dump(res, open(out, "w"), indent=2)
    print("wrote %s" % out)
    return 0

if __name__ == "__main__":
    sys.exit(main())
