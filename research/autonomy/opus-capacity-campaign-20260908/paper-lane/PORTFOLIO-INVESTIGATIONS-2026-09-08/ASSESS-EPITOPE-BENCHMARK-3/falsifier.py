#!/usr/bin/env python3
"""The falsifier for the 37 -> 34 correction: four independent conditions, each of
which, if it failed, would sink the correction.  Run from this lane's directory
after `patch -p1` into sandbox/patched (checks/03).  Exit 0 = correction survives.
"""
from decimal import Decimal, getcontext
from fractions import Fraction
import hashlib, json, os, subprocess, sys
getcontext().prec = 50
Z = Decimal("1.959963984540054")
def W(k, n):
    p = Decimal(k)/Decimal(n); N = Decimal(n); z2 = Z*Z; d = 1+z2/N
    return 2*(Z/d)*(p*(1-p)/N + z2/(4*N*N)).sqrt()
T = Decimal("0.20")
REL = "research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/EPITOPE-BENCHMARK"
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "sandbox", "patched", REL)
B = os.path.join(HERE, "sandbox", "base", REL)
fails = []

# F1  34 is the smallest n whose attainable k = round(0.9n) meets width <= 0.20
n34 = next(n for n in range(1, 500) if W(int(round(0.9*n)), n) <= T)
print("F1 smallest n with k=round(0.9n) meeting width<=0.20 :", n34)
if n34 != 34: fails.append("F1: attainable-k minimum is %d, not 34" % n34)

# F2  37 is not attainable: k=round(0.9*37)=33 -> width > 0.20
w37 = W(33, 37)
print("F2 width at n=37, k=33                                : %.6f" % w37)
if not (w37 > T): fails.append("F2: n=37 IS attainable; the case against 37 collapses")

# F3  the patched producer regenerates the artifact byte-identically
before = hashlib.sha256(open(os.path.join(P, "validated-epitope-counts.json"), "rb").read()).hexdigest()
r = subprocess.run([sys.executable, "tabulate_epitopes.py"], cwd=P, capture_output=True, text=True)
after = hashlib.sha256(open(os.path.join(P, "validated-epitope-counts.json"), "rb").read()).hexdigest()
print("F3 producer rerun rc=%d; artifact sha stable: %s" % (r.returncode, before == after))
if r.returncode != 0 or before != after: fails.append("F3: producer does not reproduce the artifact")

# F4  the artifact differs from the committed one at exactly one leaf
def flat(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items(): yield from flat(v, p+"/"+str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from flat(v, p+"/%d" % i)
    else: yield p, o
a = dict(flat(json.load(open(os.path.join(B, "validated-epitope-counts.json")))))
b = dict(flat(json.load(open(os.path.join(P, "validated-epitope-counts.json")))))
d = sorted(k for k in set(a) | set(b) if a.get(k, "<m>") != b.get(k, "<m>"))
print("F4 differing leaf paths                               :", d)
if d != ["/sufficiency/n_required/0.9"]: fails.append("F4: the change is not confined to one leaf")

# F5  the corrected guard accepts the correct ladder and rejects the stale one
def guard(lad):
    import shutil, tempfile
    t = tempfile.mkdtemp(); tt = os.path.join(t, "t"); shutil.copytree(P, tt)
    pth = os.path.join(tt, "validated-epitope-counts.json"); c = json.load(open(pth))
    c["sufficiency"]["n_required"] = lad; json.dump(c, open(pth, "w"), indent=2)
    rc = subprocess.run([sys.executable, "check_consistency.py"], cwd=tt, capture_output=True).returncode
    shutil.rmtree(t); return rc
ok = guard({"0.5":93,"0.7":78,"0.8":60,"0.9":34}); bad = guard({"0.5":93,"0.7":78,"0.8":60,"0.9":37})
print("F5 guard on correct ladder rc=%d ; on stale 37 rc=%d" % (ok, bad))
if ok != 0 or bad != 1: fails.append("F5: the corrected guard does not discriminate")

print()
print("FALSIFIED:" if fails else "NOT FALSIFIED: all five conditions hold.")
for f in fails: print("  -", f)
sys.exit(1 if fails else 0)
