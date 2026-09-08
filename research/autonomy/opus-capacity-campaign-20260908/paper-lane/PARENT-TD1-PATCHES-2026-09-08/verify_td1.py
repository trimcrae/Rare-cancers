"""Numeric-leaf and membership invariance over the three TD1-patched JSON artifacts, plus the
publications-graph scope. Exit 1 on any numeric or membership change."""
import json, os, sys, collections
A = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(A, *[os.pardir]*5))
PAIRS = [("research/literature/fet-fusion-chaperone-clientship-2026-08-27.json", "C clientship"),
         ("research/modalities/census-route-expression-grading.json", "G census grading"),
         ("research/modalities/emc-expression-panels.json", "E expression panels"),
         ("systems/graph/publications.json", "PUB graph")]
fail = []
def leaves(o, p="$"):
    if isinstance(o, dict):
        for k, v in o.items(): yield from leaves(v, p + "." + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from leaves(v, p + "[%d]" % i)
    else: yield p, o
for rel, what in PAIRS:
    b = json.load(open(os.path.join(A, "BEFORE", os.path.basename(rel)), encoding="utf-8"))
    a = json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))
    bl, al = dict(leaves(b)), dict(leaves(a))
    add, rem = sorted(set(al) - set(bl)), sorted(set(bl) - set(al))
    ch = sorted(k for k in set(bl) & set(al) if bl[k] != al[k])
    nonstr = [k for k in ch if not (isinstance(bl[k], str) and isinstance(al[k], str))]
    ok = not add and not rem and not nonstr
    print("%s  %-22s leaves %d->%d  added=%d removed=%d changed=%d  NON-STRING CHANGED=%d"
          % ("PASS " if ok else "FAIL ", what, len(bl), len(al), len(add), len(rem), len(ch), len(nonstr)))
    for k in nonstr[:5]: print("        !! %s: %r -> %r" % (k, bl[k], al[k]))
    for k in (add + rem)[:5]: print("        !! membership: %s" % k)
    if not ok: fail.append(what)
print("\nfailed=%d" % len(fail))
sys.exit(1 if fail else 0)
