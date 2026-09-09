#!/usr/bin/env python3
"""ENDPOINT-2 independent re-derivation of the corpus median objective-response rate.

Reads ONLY research/manuscripts/endpoint/endpoint-corpus.json (raw four-cell arm tables).
Does not import, execute or read back orr_dcr_reread.py or orr-dcr-reread.json for the
quantity under test; the committed artifact is opened only to quote what it states.
Python 3 stdlib only. No network.
"""
import json, math, os, hashlib, statistics, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", "..", "..", ".."))
CORPUS = os.path.join(ROOT, "research/manuscripts/endpoint/endpoint-corpus.json")
ARTIFACT = os.path.join(ROOT, "research/manuscripts/endpoint/orr-dcr-reread.json")

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

corpus = json.load(open(CORPUS))
arms = corpus["C2_arms"]

# ---- rebuild the analysis set exactly as the four-cell identity defines it -------------
rows = []
for a in arms:
    c = a["cells"]
    if any(c.get(k) is None for k in ("CR", "PR", "SD", "PD")):
        continue
    n = a["evaluable_n"]
    assert c["CR"] + c["PR"] + c["SD"] + c["PD"] == n, (a["nct_id"], a["arm_title"])
    rows.append({"nct": a["nct_id"], "arm": a["arm_title"], "n": n,
                 "orr_events": c["CR"] + c["PR"],
                 "orr_exact": 100.0 * (c["CR"] + c["PR"]) / n,
                 "orr_pct1": round(100.0 * (c["CR"] + c["PR"]) / n, 1)})

N = len(rows)
print(f"arms with a complete four-cell table and a satisfied identity: {N}")

def order_stats(vals):
    v = sorted(vals)
    k = len(v)
    lower = v[k // 2 - 1]
    upper = v[k // 2]
    return v, lower, upper, (lower + upper) / 2.0

# (a) on the producer's own 1-dp-rounded per-arm percentages (what orr_dcr_reread.py sorts)
v1, lo1, up1, med1 = order_stats([r["orr_pct1"] for r in rows])
# (b) on unrounded exact percentages
v2, lo2, up2, med2 = order_stats([r["orr_exact"] for r in rows])

print()
print("=== rounded-to-1dp per-arm ORR percentages (producer's input list) ===")
print(f"  count                       : {len(v1)}  (even: {len(v1)%2==0})")
print(f"  lower middle order stat  v[{len(v1)//2-1}] : {lo1!r}")
print(f"  upper middle order stat  v[{len(v1)//2}] : {up1!r}")
print(f"  true median (mean of the two)          : {med1!r}   -> rounded 1dp {round(med1,1)!r}")
print(f"  statistics.median cross-check          : {statistics.median(v1)!r}")
print(f"  producer's selector v[len//2]          : {v1[len(v1)//2]!r}   <- what is printed")

print()
print("=== unrounded exact per-arm ORR percentages ===")
print(f"  lower middle : {lo2!r}")
print(f"  upper middle : {up2!r}")
print(f"  true median  : {med2!r}  -> rounded 1dp {round(med2,1)!r}")
print(f"  producer-style selector v[len//2] : {v2[len(v2)//2]!r} -> 1dp {round(v2[len(v2)//2],1)!r}")

# name the two arms that sit at the middle, so the order statistics are checkable by hand
idx = sorted(range(N), key=lambda i: rows[i]["orr_pct1"])
for label, i in (("276th (lower middle)", idx[N//2 - 1]), ("277th (upper middle)", idx[N//2])):
    r = rows[i]
    print(f"  {label}: {r['nct']} | {r['arm'][:40]!r} | {r['orr_events']}/{r['n']} = {r['orr_pct1']}%")

# ---- blast radius: Figure 3 band expectations at each candidate p ----------------------
BINS = [(1, 4), (5, 9), (10, 19), (20, 39), (40, None)]
def quantile(sv, q):
    i = q * (len(sv) - 1); lo, hi = math.floor(i), math.ceil(i)
    return round(sv[int(i)], 1) if lo == hi else round(sv[lo] + (sv[hi]-sv[lo])*(i-lo), 1)

print()
print("=== Figure 3 bands: observed vs expected at p=7.7 (printed) and p=7.2 (true median) ===")
print(f"{'band':>7} {'arms':>5} {'med_n':>7} {'zero':>5} {'obs%':>6} {'exp@7.7':>8} {'exp@7.2':>8}")
band_tbl = []
for lo, hi in BINS:
    sub = [r for r in rows if r["n"] >= lo and (hi is None or r["n"] <= hi)]
    if not sub: continue
    ns = sorted(float(r["n"]) for r in sub)
    zero = [r for r in sub if r["orr_events"] == 0]
    obs = round(100*len(zero)/len(sub), 1)
    e77 = round(100*sum((1-0.077)**r["n"] for r in sub)/len(sub), 1)
    e72 = round(100*sum((1-0.072)**r["n"] for r in sub)/len(sub), 1)
    name = f"{lo}-{hi}" if hi else f"{lo}+"
    band_tbl.append((name, len(sub), quantile(ns,0.5), len(zero), obs, e77, e72))
    print(f"{name:>7} {len(sub):>5} {quantile(ns,0.5):>7} {len(zero):>5} {obs:>6} {e77:>8} {e72:>8}")

print()
print("qualitative reading at p=7.2 -- observed below expected in every band? "
      f"{all(b[4] < b[6] for b in band_tbl)}")
print("qualitative reading at p=7.7 -- observed below expected in every band? "
      f"{all(b[4] < b[5] for b in band_tbl)}")
print("gap (expected-observed) per band at 7.7:", [round(b[5]-b[4],1) for b in band_tbl])
print("gap (expected-observed) per band at 7.2:", [round(b[6]-b[4],1) for b in band_tbl])

# ---- what the committed artifact states -------------------------------------------------
art = json.load(open(ARTIFACT))
z = art["R8_zero_response_readouts"]["disjoint_bins_observed_against_binomial"]
print()
print("committed artifact states _corpus_median_objective_response_pct =",
      z["_corpus_median_objective_response_pct"])
for b in z["bands"]:
    print("  ", b["band"], b["arms"], b["median_n"], b["zero_response_arms"],
          b["observed_zero_response_pct"], b["expected_zero_response_pct"])

print()
print("input sha256:")
print(" ", sha(CORPUS), "endpoint-corpus.json")
print(" ", sha(ARTIFACT), "orr-dcr-reread.json")

# ---- known-answer controls --------------------------------------------------------------
print()
ok = True
def ctl(name, got, want):
    global ok
    p = (got == want)
    ok = ok and p
    print(("PASS " if p else "FAIL ") + name, got, "vs", want)
# even-length median definition on a hand-checkable vector
ctl("median_even_vector_[1,2,3,4]", statistics.median([1,2,3,4]), 2.5)
# the producer's selector on the same vector returns the upper middle, not the median
ctl("upper_middle_selector_[1,2,3,4]", [1,2,3,4][4//2], 3)
# odd-length: selector and median agree, so the bug is invisible at odd n
ctl("odd_vector_selector_equals_median_[1,2,3]", ([1,2,3][3//2], statistics.median([1,2,3])), (2,2))
# binomial zero-response probability, hand-checkable
ctl("zero_response_prob_p0.5_n2", round((1-0.5)**2, 4), 0.25)
# the analysis set is the whole corpus
ctl("all_552_arms_have_complete_cells", N, 552)
# my rounded per-arm percentages agree with the committed R2 rows (cross-artifact).
# NOTE: (nct_id, arm_title) is NOT unique in this corpus, so this control compares the two
# sets as MULTISETS keyed on the full four-cell content -- keying on the pair alone silently
# matched the wrong duplicate row and made this control fail spuriously in checks/01.
from collections import Counter
mine = Counter()
for a in arms:
    c = a["cells"]; n = a["evaluable_n"]
    mine[(a["nct_id"], a["arm_title"], n, c["CR"], c["PR"], c["SD"], c["PD"],
          round(100.0*(c["CR"]+c["PR"])/n, 1))] += 1
theirs = Counter()
for r in art["R2_per_arm_rows"]:
    c = r["cells"]
    theirs[(r["nct_id"], r["arm_title"], r["n"], c["CR"], c["PR"], c["SD"], c["PD"],
            r["objective_response"]["pct"])] += 1
mismatch = sum((mine - theirs).values()) + sum((theirs - mine).values())
ctl("R2_orr_pct_agrees_with_recompute_from_cells_multiset", mismatch, 0)
# mutation control: this comparison must be able to fail
bad = Counter(mine); k = next(iter(bad)); bad[k] -= 1
bad[k[:-1] + (k[-1] + 1.0,)] += 1
ctl("mutation_control_multiset_comparison_can_fail",
    sum((bad - theirs).values()) + sum((theirs - bad).values()) > 0, True)
print()
print("ALL CONTROLS PASS" if ok else "CONTROL FAILURE")
sys.exit(0 if ok else 2)
