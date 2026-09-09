#!/usr/bin/env python3
"""STRONG backward-compatibility proof: strip the newly added key(s) from a regenerated census,
re-serialise with the detector's own writer settings, and require the result BYTE-IDENTICAL to the
unpatched run. Anything weaker (a field walk, a verdict comparison) is not proof.

usage: strip_and_hash.py <regenerated.json> <unpatched-baseline.json> <key> [<key> ...]
"""
import hashlib, io, json, sys

regen, base = sys.argv[1], sys.argv[2]
keys = sys.argv[3:]
doc = json.load(open(regen, encoding="utf-8"))
removed = {k: 0 for k in keys}


def walk(o):
    if isinstance(o, dict):
        for k in keys:
            if k in o:
                del o[k]
                removed[k] += 1
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(doc)
buf = io.StringIO()
json.dump(doc, buf, indent=2, ensure_ascii=False)   # km_risk_row_detect.py:879
buf.write("\n")                                     # ...and line 880, which DOES write a newline
stripped = buf.getvalue().encode("utf-8")
original = open(base, "rb").read()
h1, h2 = hashlib.sha256(stripped).hexdigest(), hashlib.sha256(original).hexdigest()
print("keys stripped:", json.dumps(removed))
print(f"stripped-and-reserialised : sha256 {h1}  {len(stripped)} B")
print(f"unpatched baseline run    : sha256 {h2}  {len(original)} B")
identical = stripped == original
print("BYTE_IDENTICAL", identical)
sys.exit(0 if identical and all(removed.values()) else 1)
