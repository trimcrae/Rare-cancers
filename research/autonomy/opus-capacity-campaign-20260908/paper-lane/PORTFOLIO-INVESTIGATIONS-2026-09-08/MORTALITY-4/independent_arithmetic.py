#!/usr/bin/env python3
"""Independent re-derivation, from first principles and from the STRATUM COUNTS ONLY, of the
five load-bearing quantities MORTALITY-2 reports. This does not import or call any MORTALITY-2
code: it reads only the per-stratum flagged/sentence counts out of this lane's regenerated
genre-stratified-rates.json and recomputes Fisher, the exact stratified conditional test, the
Mantel-Haenszel odds ratio and both direct standardisations with its own arithmetic
(Fraction/exact integer where possible). Read-only; prints, writes nothing.
"""
import json, pathlib
from fractions import Fraction
from math import comb

S = json.loads(pathlib.Path(__file__).with_name("genre-stratified-rates.json").read_text())
strict = S["results"]["strict_terminal_event"]
strata = strict["by_five_strata"]
ORDER = ["case_report_or_series", "review_or_synthesis", "clinical_study",
         "laboratory_or_methods", "unclassified"]
tbl = []
for k in ORDER:
    e, o = strata[k]["emc"], strata[k]["other"]
    tbl.append((k, e["flagged"], e["sentences"], o["flagged"], o["sentences"]))
for r in tbl:
    print("stratum %-24s EMC %d/%-4d OTH %d/%-4d" % r)

# --- crude 2x2, exact Fisher two-sided (sum of tables no more probable than observed) ---
a = sum(r[1] for r in tbl); n1 = sum(r[2] for r in tbl)
c = sum(r[3] for r in tbl); n2 = sum(r[4] for r in tbl)
print(f"\ncrude EMC {a}/{n1} = {a/n1:.6f}   OTH {c}/{n2} = {c/n2:.6f}")
m = a + c; N = n1 + n2
def hyp(x): return Fraction(comb(n1, x) * comb(n2, m - x), comb(N, m))
p_obs = hyp(a)
p_f = sum(hyp(x) for x in range(max(0, m - n2), min(m, n1) + 1) if hyp(x) <= p_obs * Fraction(1000000001, 1000000000))
print(f"Fisher two-sided (exact rational) = {float(p_f):.10f}  -> rounded 5dp {round(float(p_f),5)}")

# --- Mantel-Haenszel OR over informative strata ---
num = den = 0.0
for k, af, an, cf, cn in tbl:
    A, B, C, D = af, an - af, cf, cn - cf
    n = an + cn
    if an == 0 or cn == 0 or (af + cf) == 0:
        print(f"  dropped as non-informative: {k}"); continue
    num += A * D / n; den += B * C / n
print(f"Mantel-Haenszel OR = {num/den:.10f}  -> rounded 4dp {round(num/den,4)}")

# --- exact stratified conditional test on informative strata (convolution of hypergeometrics) ---
dist = {0: Fraction(1)}
T = 0
for k, af, an, cf, cn in tbl:
    mi = af + cf
    if an == 0 or cn == 0 or mi == 0: continue
    T += af
    Ni = an + cn
    d2 = {}
    for x in range(max(0, mi - cn), min(mi, an) + 1):
        px = Fraction(comb(an, x) * comb(cn, mi - x), comb(Ni, mi))
        for t, pt in dist.items(): d2[t + x] = d2.get(t + x, Fraction(0)) + pt * px
    dist = d2
ET = sum(float(t) * float(p) for t, p in dist.items())
p_one = sum(p for t, p in dist.items() if t >= T)
p_obs_t = dist[T]
p_two = sum(p for t, p in dist.items() if p <= p_obs_t * Fraction(1000000001, 1000000000))
print(f"T_observed = {T}  E[T] = {ET:.6f}")
print(f"exact stratified one-sided (EMC higher) = {float(p_one):.10f} -> {round(float(p_one),6)}")
print(f"exact stratified two-sided (point prob) = {float(p_two):.10f} -> {round(float(p_two),6)}")

# --- direct standardisation ---
def std(rate_side, weight_side):
    num = wsum = 0.0
    for k, af, an, cf, cn in tbl:
        rn, rd = (af, an) if rate_side == "emc" else (cf, cn)
        w = an if weight_side == "emc" else cn
        if rd == 0: continue
        num += w * rn / rd; wsum += w
    return num / wsum
print(f"EMC rate standardised to comparator mix = {std('emc','other'):.10f} -> {round(std('emc','other'),5)}")
print(f"comparator rate standardised to EMC mix = {std('other','emc'):.10f} -> {round(std('other','emc'),5)}")
