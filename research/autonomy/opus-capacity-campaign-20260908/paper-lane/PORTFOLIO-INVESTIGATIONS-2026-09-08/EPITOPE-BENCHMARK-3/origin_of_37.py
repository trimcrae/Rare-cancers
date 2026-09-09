#!/usr/bin/env python3
"""Establish, by execution, where the pinned 37 came from.

Hypothesis: 37 is not a typo and not k=floor. It is what EPITOPE-BENCHMARK's OWN
producer, tabulate_epitopes.py, computes -- because its n_for_width() feeds the
CONTINUOUS sensitivity p straight into the Wilson width, never forming an integer
success count. This script lifts that producer code VERBATIM out of the file
(no retyping, no reimplementation) and runs it.
"""
import math, re, hashlib, sys

SRC = "../EPITOPE-BENCHMARK/tabulate_epitopes.py"
text = open(SRC, "rb").read()
print("source            :", SRC)
print("sha256            :", hashlib.sha256(text).hexdigest())
src = text.decode()

m = re.search(r"def wilson_width\(.*?\n\nREQ = \{[^\n]*\n", src, re.S)
assert m, "could not locate the producer's sufficiency block"
block = m.group(0)
print("--- verbatim block lifted from the producer ---")
print(block.rstrip())
print("--- end verbatim block ---")

ns = {"math": math}
exec(block, ns)
REQ = ns["REQ"]
print()
print("executed producer REQ =", REQ)
print("producer value at sensitivity 0.9 =", REQ[0.9])

# Is any integer success count formed anywhere in that block?
forms_k = bool(re.search(r"round\(|ceil\(|floor\(|int\(", block))
print("block forms an integer success count k? ", forms_k)

print()
print("VERDICT ON ORIGIN:")
if REQ[0.9] == 37 and not forms_k:
    print("  37 is EXACTLY what the producer computes, under the continuous-p ('p-exact')")
    print("  convention: phat := p, no integer success count is ever formed.")
    print("  => NOT a typo. NOT k=floor (k=floor gives 38). It is a real, reproducible")
    print("     convention that also produces 93 / 78 / 60 for the other three rows.")
    sys.exit(0)
print("  UNEXPECTED: producer did not reproduce 37 under the stated hypothesis.")
sys.exit(1)
