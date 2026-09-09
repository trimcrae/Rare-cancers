#!/usr/bin/env python3
"""Line-level proof that the regenerated artifact is a strict superset of the committed one.

Every difference must be either (a) a new `"y0":`/`"y1":` line, or (b) an existing line that gained
a trailing comma because a key was appended after it. Any other insertion, deletion or value change
fails. (An earlier run of this check mishandled difflib `replace` opcodes whose two sides have
different lengths and reported 161 spurious failures; that run is preserved under
checks/12b-comma-only-FAILED-opcode-handling.)
"""
import difflib, json, sys

a = open(sys.argv[1]).read().splitlines()
b = open(sys.argv[2]).read().splitlines()
bad, commas, added = [], 0, 0
for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
    if tag == "equal":
        continue
    old, new = a[i1:i2], b[j1:j2]
    if tag == "delete":
        bad += [("deleted_line", l) for l in old]
        continue
    # pair each old line with a new line in order; anything left over must be a y0/y1 insertion
    k = 0
    for x in old:
        while k < len(new) and ('"y0":' in new[k] or '"y1":' in new[k]):
            added += 1
            k += 1
        if k >= len(new):
            bad.append(("deleted_line", x)); continue
        y = new[k]; k += 1
        if y == x:
            pass
        elif y == x + ",":
            commas += 1
        else:
            bad.append(("value_changed", x, y))
    for y in new[k:]:
        if '"y0":' in y or '"y1":' in y:
            added += 1
        else:
            bad.append(("unexpected_insertion", y))

n = 0
def walk(o):
    global n
    if isinstance(o, dict):
        if {"cx", "cy", "w"} <= set(o):
            n += 1
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)
walk(json.load(open(sys.argv[2])))

print("mark records in the whole document (figures + synthetic control):", n)
print("y0/y1 lines inserted:", added, "(expected 2 x n =", 2 * n, ")")
print("existing lines that only gained a trailing comma:", commas)
print("deletions / value changes / unexpected insertions:", len(bad))
for x in bad[:10]:
    print("  ", x)
print("STRICTLY_ADDITIVE", not bad and added == 2 * n)
sys.exit(0 if (not bad and added == 2 * n) else 1)
