#!/usr/bin/env python3
"""EPITOPE-BENCHMARK-3 - independent re-derivation of the Wilson sufficiency ladder.

Criterion (PUB-VACCINE-PATH, as reproduced by EPITOPE-BENCHMARK):
    smallest n such that the 95% Wilson score-interval width for an observed
    sensitivity p is <= 0.20.

The only free choice is how the observed proportion is formed at a given n:
  A. p-exact   : phat = p                 (continuous; no integer successes)
  B. k=round   : phat = round(p*n)/n
  C. k=ceil    : phat = ceil (p*n)/n
  D. k=floor   : phat = floor(p*n)/n
Nothing else in the closed form varies.
"""
import math

Z = 1.959963984540054  # two-sided 95%

def wilson_width(phat, n, z=Z):
    d = 1 + z*z/n
    half = (z/d)*math.sqrt(phat*(1-phat)/n + z*z/(4*n*n))
    return 2*half

def phat_of(conv, p, n):
    if conv == "p-exact": return p, None
    k = {"k=round": lambda: int(round(p*n)),
         "k=ceil":  lambda: math.ceil(p*n),
         "k=floor": lambda: math.floor(p*n)}[conv]()
    return k/n, k

def n_for_width(conv, p, target=0.20, nmax=100000):
    n = 1
    while n < nmax:
        phat, k = phat_of(conv, p, n)
        w = wilson_width(phat, n)
        if w <= target:
            return n, k, phat, w
        n += 1
    return None, None, None, None

CONVS = ["p-exact", "k=round", "k=ceil", "k=floor"]
SENS  = [0.5, 0.7, 0.8, 0.9]

print("=== 1. sensitivity 0.9, all conventions (the arbitrated row) ===")
for c in CONVS:
    n, k, ph, w = n_for_width(c, 0.9)
    print("  %-8s -> minimum n = %3d   (k=%s, phat=%.6f, width=%.6f)"
          % (c, n, ("%d" % k) if k is not None else "n/a", ph, w))

print()
print("=== 2. the full ladder under every convention ===")
print("  %-8s | %s" % ("conv", " | ".join("p=%.1f" % p for p in SENS)))
lad = {}
for c in CONVS:
    row = [n_for_width(c, p)[0] for p in SENS]
    lad[c] = row
    print("  %-8s | %s" % (c, " | ".join("%5d" % v for v in row)))

PINNED = [93, 78, 60, 37]
SETTLED_09 = 34
print()
print("=== 3. which convention reproduces the PINNED ladder 93/78/60/37 ? ===")
for c in CONVS:
    print("  %-8s : %s  %s" % (c, lad[c], "MATCHES PINNED LADDER" if lad[c] == PINNED else "no"))
print()
print("=== 4. which convention reproduces 93/78/60/34 (pinned ladder with the arbitrated 0.9) ===")
TARGET = [93, 78, 60, SETTLED_09]
for c in CONVS:
    print("  %-8s : %s  %s" % (c, lad[c], "MATCHES" if lad[c] == TARGET else "no"))
print()
print("=== 5. width table at and just below each candidate n, p=0.9 ===")
for c in CONVS:
    n, _, _, _ = n_for_width(c, 0.9)
    for nn in (n-1, n):
        ph, k = phat_of(c, 0.9, nn)
        print("  %-8s n=%3d k=%-4s phat=%.6f width=%.6f  %s"
              % (c, nn, ("%d" % k) if k is not None else "-", ph,
                 wilson_width(ph, nn), "<= 0.20" if wilson_width(ph, nn) <= 0.20 else "> 0.20"))
print()
print("=== 6. candidate values 34 and 37 evaluated under every convention, p=0.9 ===")
for c in CONVS:
    for nn in (34, 37, 38):
        ph, k = phat_of(c, 0.9, nn)
        print("  %-8s n=%d k=%-4s phat=%.6f width=%.6f %s"
              % (c, nn, ("%d" % k) if k is not None else "-", ph, wilson_width(ph, nn),
                 "MEETS <=0.20" if wilson_width(ph, nn) <= 0.20 else "fails"))
