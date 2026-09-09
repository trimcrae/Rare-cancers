#!/usr/bin/env python3
"""Verify every gene table printed in PRE-REGISTRATION.md against the frozen JSON artifact,
and confirm the input digest quoted in the prose matches the one the generator computed.
Exits non-zero on any mismatch. No expression value is read."""
import json, re, sys
s = json.load(open('fusion-program-testsets.json'))
md = open('PRE-REGISTRATION.md').read()
rows = [l for l in md.splitlines() if l.startswith('| 1 kb |')
        or l.startswith('| **2 kb (primary)** |') or l.startswith('| 5 kb |')]
order = [('1000', 'A'), ('2000', 'A'), ('5000', 'A'), ('1000', 'B'), ('2000', 'B'), ('5000', 'B')]
bad = 0
if len(rows) != 6:
    print('FAIL: expected 6 gene-table rows, found', len(rows)); sys.exit(2)
for row, (w, c) in zip(rows, order):
    got = set(re.findall(r'\*([A-Z0-9]+)\*', row.split('|')[3]))
    exp = set(s['windows'][w][f'contrast_{c}_set']['genes'])
    ok = got == exp
    bad += not ok
    print(f'{w} {c} n={len(got)} {"OK" if ok else "MISMATCH missing=%s extra=%s" % (sorted(exp-got), sorted(got-exp))}')
sha = s['input']['sha256']
print('digest in prose:', 'OK' if sha in md else 'MISSING')
bad += sha not in md
sys.exit(1 if bad else 0)
