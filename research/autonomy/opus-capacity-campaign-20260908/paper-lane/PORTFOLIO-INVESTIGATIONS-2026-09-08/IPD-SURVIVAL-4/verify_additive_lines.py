#!/usr/bin/env python3
"""Line-level strict-superset test: the regenerated census may only INSERT lines whose key is one of
the permitted new keys, and may only change existing lines by gaining a trailing comma. Any
deletion, any value change, any other insertion fails."""
import difflib, json, re, sys

old = open(sys.argv[1], encoding="utf-8").read().splitlines()
new = open(sys.argv[2], encoding="utf-8").read().splitlines()
allowed = set(sys.argv[3:])
key = re.compile(r'^\s*"([^"]+)":')
ins, comma, bad = {}, 0, []
sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        continue
    if tag == "delete":
        bad += [("delete", l) for l in old[i1:i2]]
        continue
    if tag == "insert":
        for l in new[j1:j2]:
            m = key.match(l)
            if m and m.group(1) in allowed:
                ins[m.group(1)] = ins.get(m.group(1), 0) + 1
            else:
                bad.append(("insert", l))
        continue
    # replace: pair up what we can, treat the rest as insert/delete
    o, n = old[i1:i2], new[j1:j2]
    for a, b in zip(o, n):
        if b == a + ",":
            comma += 1
        else:
            bad.append(("replace", a, b))
    for l in o[len(n):]:
        bad.append(("delete", l))
    for l in n[len(o):]:
        m = key.match(l)
        if m and m.group(1) in allowed:
            ins[m.group(1)] = ins.get(m.group(1), 0) + 1
        else:
            bad.append(("insert", l))
print("inserted lines by key :", json.dumps(ins))
print("existing lines gaining only a trailing comma :", comma)
print("violations :", len(bad))
for b in bad[:20]:
    print("  !!", b)
print("STRICTLY_ADDITIVE", not bad)
sys.exit(0 if not bad else 1)
