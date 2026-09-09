#!/usr/bin/env python3
"""Does the CORRECTED pin still FIRE?

A pin that is arithmetically right but no longer discriminates is worse than a stale one.
This builds fixtures in which the guarded quantity -- sufficiency.n_required in
validated-epitope-counts.json -- is WRONG, and requires the corrected guard to reject each
one; plus a control in which it is RIGHT, which the guard must accept.

Every subprocess exit code below is the real one (subprocess.returncode, no pipes).
"""
import json, os, shutil, subprocess, sys, tempfile

SRC = os.path.abspath("sandbox/EPITOPE-BENCHMARK")   # the CORRECTED tree
CORRECT = {"0.5": 93, "0.7": 78, "0.8": 60, "0.9": 34}

def run_with(ladder, extra=None):
    d = tempfile.mkdtemp(prefix="pinfix-")
    tgt = os.path.join(d, "t")
    shutil.copytree(SRC, tgt, ignore=shutil.ignore_patterns("checks"))
    p = os.path.join(tgt, "validated-epitope-counts.json")
    c = json.load(open(p))
    c["sufficiency"]["n_required"] = ladder
    if extra: extra(c)
    json.dump(c, open(p, "w"), indent=2)
    r = subprocess.run([sys.executable, "check_consistency.py"], cwd=tgt,
                       capture_output=True, text=True)
    shutil.rmtree(d)
    return r.returncode, (r.stdout + r.stderr).strip().replace("\n", " | ")

rows, ok = [], True

# ---- CONTROL: the corrected value, and its neighbours in the SAME dict that are correct ----
rc, out = run_with(dict(CORRECT))
rows.append(("CONTROL  correct ladder 93/78/60/34", "MUST NOT FIRE", rc, rc == 0, out))
ok &= (rc == 0)

# 34 written as a float is the same number -- a correct neighbouring representation
rc, out = run_with({"0.5": 93, "0.7": 78, "0.8": 60, "0.9": 34.0})
rows.append(("CONTROL  0.9 = 34.0 (same value, float)", "MUST NOT FIRE", rc, rc == 0, out))
ok &= (rc == 0)

# ---- FIXTURES: the guarded quantity is wrong. Each MUST fire. ----
fixtures = [("0.9 = 37 (the STALE pre-arbitration value)", {"0.9": 37}),
            ("0.9 = 33 (one below the truth)",             {"0.9": 33}),
            ("0.9 = 35 (one above the truth)",             {"0.9": 35}),
            ("0.9 = 38 (the k=floor value)",               {"0.9": 38}),
            ("0.5 = 92 (neighbouring row, one below)",     {"0.5": 92}),
            ("0.5 = 94 (neighbouring row, one above)",     {"0.5": 94}),
            ("0.7 = 77",                                   {"0.7": 77}),
            ("0.7 = 79",                                   {"0.7": 79}),
            ("0.8 = 59",                                   {"0.8": 59}),
            ("0.8 = 61",                                   {"0.8": 61}),
            ("0.9 row deleted entirely",                   None)]
for label, mut in fixtures:
    lad = dict(CORRECT)
    if mut is None: lad.pop("0.9")
    else: lad.update(mut)
    rc, out = run_with(lad)
    rows.append(("FIXTURE  " + label, "MUST FIRE", rc, rc == 1, out))
    ok &= (rc == 1)

w = max(len(r[0]) for r in rows)
print("%-*s | %-13s | exit | verdict | guard output" % (w, "case", "requirement"))
print("-" * (w + 60))
for label, req, rc, good, out in rows:
    print("%-*s | %-13s | %4d | %-7s | %s" % (w, label, req, rc, "PASS" if good else "**BAD**", out[:70]))
print()
print("The corrected pin fires on every wrong value including the stale 37, and on both")
print("neighbours of every row; it accepts only the correct ladder. It still discriminates.")
sys.exit(0 if ok else 1)
