#!/usr/bin/env python3
"""(a) the 0.4515 vs 0.4507 question, (b) the convention-sensitivity probe that
would falsify '34', both computed here from the closed form."""
from decimal import Decimal, getcontext
from fractions import Fraction
import math
getcontext().prec = 50
Z = Decimal("1.959963984540054")
def W(phat, n):
    p = Decimal(phat.numerator)/Decimal(phat.denominator) if isinstance(phat, Fraction) else Decimal(str(phat))
    N = Decimal(n); z2 = Z*Z; d = 1 + z2/N
    return 2*(Z/d)*(p*(1-p)/N + z2/(4*N*N)).sqrt()
T = Decimal("0.20")

print("== achieved width at n = 15, sensitivity 0.5 ==")
print("p-exact  phat=0.5      width = %.6f  -> round4 = %.4f" % (W("0.5",15), W("0.5",15)))
for k in (7, 8):
    print("k=%d      phat=%d/15    width = %.6f  -> round4 = %.4f" % (k, k, W(Fraction(k,15),15), W(Fraction(k,15),15)))
print("python round(0.5*15) =", round(0.5*15), " (banker's)   math.floor(7.5+0.5) =", math.floor(7.5+0.5))
print("=> 0.4515 is the p-exact route; 0.4507 is the integer-k route.")
print("   SAME convention question as 37 vs 34, at a different call site.")
print()
print("== is the 0.9 requirement sensitive to HOW the attainable k is chosen? ==")
print("smallest n such that SOME integer k in [0,n] gives width <= 0.20 (no proximity to 0.9 required):")
for n in range(1, 60):
    best = min((W(Fraction(k,n),n), k) for k in range(0, n+1))
    if best[0] <= T:
        print("   n = %d (k = %d, phat = %.4f, width = %.6f)  <- a laxer 'attainable' rule" % (n, best[1], best[1]/n, best[0]))
        break
print("smallest n such that the k NEAREST 0.9n gives width <= 0.20:")
for n in range(1, 200):
    k = int(round(0.9*n))
    if W(Fraction(k,n),n) <= T:
        print("   n = %d (k = %d, width = %.6f)" % (n, k, W(Fraction(k,n),n))); break
print("smallest n such that ALL m >= n with k=round(0.9m) meet width <= 0.20 (a true threshold):")
first = None
for n in range(1, 200):
    if all(W(Fraction(int(round(0.9*m)),m),m) <= T for m in range(n, 400)):
        first = n; break
print("   n =", first, " <- note: NOT 34; 36 and 37 fail under k=round")
