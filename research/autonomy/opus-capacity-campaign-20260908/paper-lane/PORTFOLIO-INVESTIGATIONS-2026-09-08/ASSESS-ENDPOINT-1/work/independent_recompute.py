#!/usr/bin/env python3
"""ASSESS-ENDPOINT-1: independent recomputation of a sample of ENDPOINT-1 ledger rows.
Written from the artifacts only; does not import rederive_claims.py."""
import json, math, statistics, collections, sys

BASE = "/home/user/Rare-cancers/research/manuscripts/endpoint/"
C = json.load(open(BASE + "endpoint-corpus.json"))
R = json.load(open(BASE + "orr-dcr-reread.json"))
G = json.load(open(BASE + "endpoint-regime-map.json"))
P = json.load(open(BASE + "placebo-arm-calibration.json"))
A = json.load(open(BASE + "endpoint-prior-art-audit.json"))
D = json.load(open(BASE + "emc-endpoint-discordance.json"))

arms = C["C2_arms"]
out = []
def rec(name, mine, theirs):
    ok = mine == theirs
    out.append((name, ok, mine, theirs))
    print(("OK  " if ok else "DIFF"), name, "| mine=", mine, "| ledger/paper=", theirs)

# ---- helpers, independent implementations
def q7(xs, p):
    s = sorted(xs); n = len(s)
    if n == 1: return float(s[0])
    h = (n - 1) * p
    lo = math.floor(h); hi = math.ceil(h)
    return s[lo] + (h - lo) * (s[hi] - s[lo])

def orr(a):
    c = a["cells"]; return 100.0 * (c["CR"] + c["PR"]) / a["evaluable_n"]
def dcr(a):
    c = a["cells"]; return 100.0 * (c["CR"] + c["PR"] + c["SD"]) / a["evaluable_n"]
def gap(a):
    c = a["cells"]; return 100.0 * c["SD"] / a["evaluable_n"]

# ---- M-ARMS
rec("M-ARMS arms/trials", [len(arms), len({a["nct_id"] for a in arms})], [552, 138])

# ---- M-IDENTITY: cells sum to evaluable_n for all arms
bad = sum(1 for a in arms if sum(a["cells"].values()) != a["evaluable_n"])
rec("M-IDENTITY violations", bad, 0)
# gap identity: dcr - orr == sd share
bad2 = sum(1 for a in arms if abs((dcr(a)-orr(a)) - gap(a)) > 1e-9)
rec("M-GAPID violations", bad2, 0)

gaps = [gap(a) for a in arms]
rec("M-MEDGAP", round(statistics.median(gaps), 1), 39.4)
rec("M-IQR", [round(q7(gaps, .25), 1), round(q7(gaps, .75), 1)], [20.0, 54.3])
rec("M-RANGE", [round(min(gaps),1), round(max(gaps),1)], [0.0, 100.0])
rec("M-GE50", sum(1 for g in gaps if g >= 50), 194)
rec("M-GE25", sum(1 for g in gaps if g >= 25), 396)
rec("M-GE75", sum(1 for g in gaps if g >= 75), 72)
rec("M-CORNER orr<=10 & dcr>=70", sum(1 for a in arms if orr(a) <= 10 and dcr(a) >= 70), 71)

# ---- M-WEIGHTED
tot_n = sum(a["evaluable_n"] for a in arms)
tot_sd = sum(a["cells"]["SD"] for a in arms)
rec("M-WEIGHTED", [tot_n, tot_sd, round(100.0*tot_sd/tot_n, 1)], [18318, 7213, 39.4])

# ---- Z-MEDORR: the disputed median
orrs = sorted(orr(a) for a in arms)
n = len(orrs)
true_median = statistics.median(orrs)
upper_mid = orrs[n // 2]
lower_mid = orrs[n // 2 - 1]
rec("Z-MEDORR true median (round1)", round(true_median, 1), 7.2)
rec("Z-MEDORR two middle order stats", [round(lower_mid,1), round(upper_mid,1)], [6.7, 7.7])
rec("Z-MEDORR selector orrs[n//2]", round(upper_mid, 1), 7.7)
print("   raw middles:", lower_mid, upper_mid, "mean", (lower_mid+upper_mid)/2)

# ---- Figure 3 bands, recomputed from raw cells, at BOTH p values
def binom_zero(nn, p):
    return (1 - p) ** nn
bands = [("1-4",1,4),("5-9",5,9),("10-19",10,19),("20-39",20,39),("40+",40,10**9)]
printed_expected = {"1-4":81.0,"5-9":61.0,"10-19":32.8,"20-39":11.5,"40+":0.5}
claimed_at_72   = {"1-4":82.1,"5-9":63.1,"10-19":35.3,"20-39":13.3,"40+":0.7}
printed_arms = {"1-4":(174,3.0,134,77.0),"5-9":(147,6.0,85,57.8),"10-19":(93,15.0,28,30.1),
                "20-39":(48,27.5,4,8.3),"40+":(90,128.5,0,0.0)}
for label, lo, hi in bands:
    sel = [a for a in arms if lo <= a["evaluable_n"] <= hi]
    ns = [a["evaluable_n"] for a in sel]
    zero = [a for a in sel if a["cells"]["CR"] + a["cells"]["PR"] == 0]
    obs = round(100.0*len(zero)/len(sel), 1)
    mine = (len(sel), round(statistics.median(ns),1), len(zero), obs)
    rec(f"Z-BAND-{label} arms/medn/zero/obs", list(mine), list(printed_arms[label]))
    e77 = round(100.0*sum(binom_zero(a["evaluable_n"], 0.077) for a in sel)/len(sel), 1)
    e72 = round(100.0*sum(binom_zero(a["evaluable_n"], 0.072) for a in sel)/len(sel), 1)
    rec(f"Z-BAND-{label} expected @p=7.7%", e77, printed_expected[label])
    rec(f"Z-BAND-{label} expected @p=7.2%", e72, claimed_at_72[label])
    print(f"   band {label}: observed {obs} vs expected(7.7)={e77} expected(7.2)={e72} -> obs<exp@7.2? {obs < e72}")

# ---- A-MEDIANS (accrual)
acc = C["C7_accrual_records"]
rec("A-RECORDS total", len(acc), 1837)
byst = collections.Counter(r.get("overall_status") or r.get("status") for r in acc)
print("   accrual statuses:", byst)

# ---- E-ORR / Wilson, independent closed form
def wilson(k, nn, z=1.959963984540054):
    p = k/nn
    d = 1 + z*z/nn
    c = (p + z*z/(2*nn))/d
    h = z*math.sqrt(p*(1-p)/nn + z*z/(4*nn*nn))/d
    return (round(100*(c-h),1), round(100*(c+h),1))
rec("E-ORR 6/47", [6,47,round(100*6/47,1)]+list(wilson(6,47)), [6,47,12.8,6.0,25.2])
rec("E-DCR 42/47", [round(100*42/47,1)]+list(wilson(42,47)), [89.4,77.4,95.4])
rec("E-GAP", [round(100*36/47,1),36], [76.6,36])
rec("E-FIXED 46", [round(100*6/46,1)]+list(wilson(6,46))+[round(100*42/46,1)]+list(wilson(42,46)),
    [13.0,6.1,25.7,91.3,79.7,96.6])

# ---- E-PCTILE
smaller = sum(1 for g in gaps if g < 76.6)
rec("E-PCTILE arms below 76.6", [smaller, len(gaps), round(100.0*smaller/len(gaps),1)], [491,552,88.9])

# ---- K-EMC-DESIGN: exact single-stage, p0=0.05, p1=0.128, alpha .05, power .80
def binom_upper(k, nn, p):  # P(X >= k)
    return sum(math.comb(nn,i)*p**i*(1-p)**(nn-i) for i in range(k, nn+1))
found = None
for N in range(1, 300):
    for r_ in range(0, N+1):
        if binom_upper(r_+1, N, 0.05) <= 0.05 and binom_upper(r_+1, N, 0.128) >= 0.80:
            found = (N, r_+1); break
    if found: break
rec("K-EMC-DESIGN N", found[0] if found else None, 79)
# K-EMC-ZERO: n for 90% chance of >=1 response at 12.8%
nn = 1
while 1-(1-0.128)**nn < 0.90: nn += 1
rec("K-EMC-ZERO n", nn, 17)

# ---- V-484 no-intervention arm
ni = [a for a in arms if a.get("arm_group_type") == "NO_INTERVENTION"]
print("   NO_INTERVENTION arms:", len(ni), [(a["nct_id"], round(orr(a),1)) for a in ni])
rec("V-484", round(orr(ni[0]),1) if len(ni)==1 else None, 48.4)
rec("V-19C control_arm_candidate", sum(1 for a in arms if a.get("control_arm_candidate")), 19)

# ---- R-1998 earliest prior-art document
years = []
for e in A.get("A1_endorsed_alternatives", []):
    y = e.get("year")
    if y: years.append(int(y))
rec("R-1998 earliest year", min(years) if years else None, 1998)

print()
print("SUMMARY: %d checks, %d agree, %d differ" % (len(out), sum(1 for o in out if o[1]), sum(1 for o in out if not o[1])))
sys.exit(0 if all(o[1] for o in out) else 3)
