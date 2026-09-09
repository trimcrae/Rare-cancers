#!/usr/bin/env python3
"""ASSESS-EPITOPE-BENCHMARK-3: independent Wilson re-derivation.

Written from the closed form of the Wilson score interval, NOT imported from
EPITOPE-BENCHMARK or EPITOPE-BENCHMARK-3.  Exact rational/Decimal arithmetic is
used so that boundary comparisons against 0.20 cannot turn on float noise.
"""
from decimal import Decimal, getcontext
from fractions import Fraction
import math

getcontext().prec = 50

# z for a two-sided 95% interval.  Computed here, not copied: solve Phi(z)=0.975
# by bisection on the erf-based normal CDF.
def Phi(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
lo, hi = 1.0, 3.0
for _ in range(200):
    mid = (lo + hi) / 2.0
    if Phi(mid) < 0.975: lo = mid
    else: hi = mid
Z = (lo + hi) / 2.0
print("z(0.975) derived by bisection on erf : %.15f" % Z)
print("scipy-free cross-check, lane's constant: 1.959963984540054")
print()

ZD = Decimal(repr(Z))

def wilson_width_dec(phat, n):
    """Exact-ish Wilson width in Decimal.  phat may be Fraction or Decimal."""
    p = Decimal(phat.numerator) / Decimal(phat.denominator) if isinstance(phat, Fraction) else Decimal(str(phat))
    N = Decimal(n)
    z2 = ZD * ZD
    d = 1 + z2 / N
    inner = p * (1 - p) / N + z2 / (4 * N * N)
    half = (ZD / d) * inner.sqrt()
    return 2 * half

TARGET = Decimal("0.20")
SENS = ["0.5", "0.7", "0.8", "0.9"]

CONVENTIONS = {
    "p-exact":  lambda p, n: Decimal(p),                       # continuous p straight in
    "k=round":  lambda p, n: Fraction(int(round(float(p) * n)), n),
    "k=ceil":   lambda p, n: Fraction(math.ceil(float(p) * n), n),
    "k=floor":  lambda p, n: Fraction(math.floor(float(p) * n), n),
    # a fifth, not in the subject's list: banker's rounding is what Python's
    # round() does on .5 ties; check it separately from round-half-up.
    "k=halfup": lambda p, n: Fraction(math.floor(float(p) * n + 0.5), n),
}

def first_n(conv, p, nmax=100000):
    for n in range(1, nmax):
        if wilson_width_dec(CONVENTIONS[conv](p, n), n) <= TARGET:
            return n
    return None

ladders = {}
for conv in CONVENTIONS:
    ladder = [first_n(conv, s) for s in SENS]
    ladders[conv] = ladder
    print("%-9s -> %s" % (conv, " / ".join(str(x) for x in ladder)))
print()

pinned_old = [93, 78, 60, 37]
pinned_new = [93, 78, 60, 34]
print("ladders matching 93/78/60/37 :", [c for c, l in ladders.items() if l == pinned_old])
print("ladders matching 93/78/60/34 :", [c for c, l in ladders.items() if l == pinned_new])
print()

# ---- attainability argument at n = 37, checked explicitly -------------------
for n in (33, 34, 35, 36, 37, 38, 39, 40):
    k = int(round(0.9 * n))
    w_round = wilson_width_dec(Fraction(k, n), n)
    w_pexact = wilson_width_dec(Decimal("0.9"), n)
    print("n=%2d  k=round(0.9n)=%2d  k/n=%.6f  width(k/n)=%.6f %s   width(p=0.9)=%.6f %s"
          % (n, k, k / n, w_round, "<=0.20" if w_round <= TARGET else " >0.20",
             w_pexact, "<=0.20" if w_pexact <= TARGET else " >0.20"))
print()

# ---- monotonicity: is 34 a floor, or just the FIRST n that passes? ----------
for conv in ("k=round", "p-exact"):
    bad = [n for n in range(34, 400)
           if wilson_width_dec(CONVENTIONS[conv]("0.9", n), n) > TARGET]
    print("%-9s at p=0.9: n in [34,400) that FAIL width<=0.20 -> %s" % (conv, bad if bad else "none"))
for conv in ("k=round",):
    for s in ("0.5", "0.7", "0.8"):
        base = first_n(conv, s)
        bad = [n for n in range(base, base + 300)
               if wilson_width_dec(CONVENTIONS[conv](s, n), n) > TARGET]
        print("%-9s at p=%s: first=%d, later failures in [%d,%d) -> %s"
              % (conv, s, base, base, base + 300, bad if bad else "none"))
