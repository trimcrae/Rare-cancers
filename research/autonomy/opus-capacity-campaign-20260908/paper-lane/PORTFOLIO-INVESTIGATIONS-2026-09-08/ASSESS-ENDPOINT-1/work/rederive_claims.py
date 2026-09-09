#!/usr/bin/env python3
"""ENDPOINT-1 claim re-derivation harness for PUB-ENDPOINT.

Re-derives every quantitative claim in
research/manuscripts/endpoint/response-endpoint-indolent-tumours.md
from the artifacts the route names, and writes claim-rederivation-ledger.json.

Derivation levels:
  READ-BACK   the value is stored verbatim in the named artifact key
  RECOMPUTED  the value is rebuilt from the artifact's own raw rows
              (C2_arms cells, C7_accrual_records, R2_per_arm_rows) by this script

Verdicts: REPRODUCES | MISMATCH | NOT-RE-DERIVABLE-LOCALLY

No network. Reads only. Writes only inside this lane directory.
"""
import json, math, os, statistics, sys, hashlib
from collections import Counter, defaultdict

REPO = "/home/user/Rare-cancers"
END = os.path.join(REPO, "research/manuscripts/endpoint")
LANE = os.path.dirname(os.path.abspath(__file__))

def load(name):
    p = os.path.join(END, name)
    with open(p, "rb") as fh:
        b = fh.read()
    return json.loads(b), hashlib.sha256(b).hexdigest()

CORPUS, H_CORPUS = load("endpoint-corpus.json")
REREAD, H_REREAD = load("orr-dcr-reread.json")
MAP, H_MAP = load("endpoint-regime-map.json")
PLACEBO, H_PLACEBO = load("placebo-arm-calibration.json")
PRIOR, H_PRIOR = load("endpoint-prior-art-audit.json")
DISC, H_DISC = load("emc-endpoint-discordance.json")
with open(os.path.join(END, "response-endpoint-indolent-tumours.md"), "rb") as fh:
    H_MS = hashlib.sha256(fh.read()).hexdigest()

ROWS = []

def rec(rid, section, claim, quoted, source, key, derived, level, note=None, missing=None):
    if derived is None and missing:
        verdict = "NOT-RE-DERIVABLE-LOCALLY"
        ok = None
    else:
        ok = _eq(quoted, derived)
        verdict = "REPRODUCES" if ok else "MISMATCH"
    r = {"id": rid, "manuscript_section": section, "claim": claim,
         "quoted_value": quoted, "source_artifact": source, "source_key": key,
         "rederived_value": derived, "derivation_level": level, "verdict": verdict}
    if note: r["note"] = note
    if missing: r["exact_missing_input"] = missing
    ROWS.append(r)
    return r

def _eq(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return abs(a - b) <= 5e-2 if isinstance(a, float) or isinstance(b, float) else a == b
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(_eq(x, y) for x, y in zip(a, b))
    return a == b

# ---------- statistics rebuilt from raw rows ----------
def median(xs):
    return statistics.median(xs)

def quantile_type7(xs, q):
    """R type-7 / numpy default percentile."""
    s = sorted(xs)
    if len(s) == 1: return float(s[0])
    h = (len(s) - 1) * q
    lo = math.floor(h); hi = math.ceil(h)
    return s[lo] + (h - lo) * (s[hi] - s[lo])

def wilson(x, n, z=1.959963984540054):
    if n == 0: return (0.0, 0.0)
    p = x / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (max(0.0, c-h), min(1.0, c+h))

def wilson_by_rootfind(x, n, z=1.959963984540054):
    """Independent implementation: solve the score equation by bisection."""
    p_hat = x / n
    def score(p):
        if p <= 0 or p >= 1: return math.copysign(1e9, p_hat - p)
        return (p_hat - p) / math.sqrt(p*(1-p)/n)
    def solve(target, lo, hi):
        for _ in range(200):
            mid = (lo+hi)/2
            if score(mid) > target: lo = mid
            else: hi = mid
        return (lo+hi)/2
    return (solve(z, 1e-12, p_hat) if x > 0 else 0.0,
            solve(-z, p_hat, 1-1e-12) if x < n else 1.0)

def n_for_90pct_one_response(p, target=0.90):
    if p <= 0: return None
    n = 1
    while (1-p)**n > 1-target:
        n += 1
        if n > 100000: return None
    return n

def binom_sf_atleast(k, n, p):
    """P(X >= k) exactly."""
    tot = 0.0
    for i in range(k, n+1):
        tot += math.comb(n, i) * p**i * (1-p)**(n-i)
    return tot

def single_stage_n(p1, p0=0.05, alpha=0.05, power=0.80, nmax=1000):
    """Smallest n with a critical r such that type-I <= alpha and power >= 0.80."""
    if p1 <= p0: return None
    for n in range(1, nmax+1):
        for r in range(1, n+1):
            if binom_sf_atleast(r, n, p0) <= alpha and binom_sf_atleast(r, n, p1) >= power:
                return n
    return None

# ---------- Section 4/5: rebuild the corpus distribution from C2_arms ----------
arms = CORPUS["C2_arms"]
def arm_stats(a):
    c = a["cells"]; n = a["evaluable_n"]
    orr = (c["CR"] + c["PR"]) / n
    dcr = (c["CR"] + c["PR"] + c["SD"]) / n
    return n, orr, dcr, c["SD"]/n, sum(c.values())

sums_ok = all(arm_stats(a)[4] == a["evaluable_n"] for a in arms)
gaps = [round(100*arm_stats(a)[3], 1) for a in arms]
orrs = [100*arm_stats(a)[1] for a in arms]
dcrs = [100*arm_stats(a)[2] for a in arms]

rec("M-ARMS", "4.1/5", "552 arms across 138 trials",
    [552, 138], "endpoint-corpus.json", "C2_arms / C6_counts",
    [len(arms), len({a["nct_id"] for a in arms})], "RECOMPUTED")
rec("M-IDENTITY", "2.3", "CR+PR+SD+PD == the evaluable denominator, asserted for every row",
    True, "endpoint-corpus.json", "C2_arms[].cells", sums_ok, "RECOMPUTED")
rec("M-GAPID", "2.3/4.1", "disease control minus objective response is identically the stable-disease proportion",
    True, "endpoint-corpus.json", "C2_arms[].cells",
    all(abs((arm_stats(a)[2]-arm_stats(a)[1]) - arm_stats(a)[3]) < 1e-12 for a in arms), "RECOMPUTED")
rec("M-MEDGAP", "abstract/4.1", "median gap 39.4 percentage points",
    39.4, "endpoint-corpus.json", "C2_arms (recomputed)", round(median(gaps), 1), "RECOMPUTED")
rec("M-IQR", "abstract/4.1", "interquartile range 20.0 to 54.3",
    [20.0, 54.3], "endpoint-corpus.json", "C2_arms (recomputed)",
    [round(quantile_type7(gaps, .25), 1), round(quantile_type7(gaps, .75), 1)], "RECOMPUTED")
rec("M-RANGE", "4.1", "full range 0 to 100", [0.0, 100.0], "endpoint-corpus.json",
    "C2_arms (recomputed)", [round(min(gaps),1), round(max(gaps),1)], "RECOMPUTED")
rec("M-GE50", "abstract/4.1", "194 of 552 arms at or above 50 points",
    194, "endpoint-corpus.json", "C2_arms (recomputed)", sum(1 for g in gaps if g >= 50), "RECOMPUTED")
rec("M-GE25", "artifact only", "396 arms at or above 25 points (R3 key, not in prose)",
    396, "orr-dcr-reread.json", "R3_distribution_summary.all_arms.arms_at_or_above.25",
    sum(1 for g in gaps if g >= 25), "RECOMPUTED")
rec("M-GE75", "artifact only", "72 arms at or above 75 points (R3 key, not in prose)",
    72, "orr-dcr-reread.json", "R3_distribution_summary.all_arms.arms_at_or_above.75",
    sum(1 for g in gaps if g >= 75), "RECOMPUTED")
rec("M-CORNER", "4.1", "71 arms with objective response <= 10% and disease control >= 70%",
    71, "endpoint-corpus.json", "C2_arms (recomputed)",
    sum(1 for a in arms if 100*arm_stats(a)[1] <= 10 and 100*arm_stats(a)[2] >= 70), "RECOMPUTED")
rec("M-WEIGHTED", "2.3/artifact", "patient-weighted gap 39.4 pp over 18,318 patients and 7,213 stable-disease events",
    [18318, 7213, 39.4], "orr-dcr-reread.json", "R3_distribution_summary.denominator_weighted_sensitivity",
    [sum(a["evaluable_n"] for a in arms), sum(a["cells"]["SD"] for a in arms),
     round(100*sum(a["cells"]["SD"] for a in arms)/sum(a["evaluable_n"] for a in arms), 1)], "RECOMPUTED")

# 4.2 strata
def stratum(pred):
    sub = [round(100*arm_stats(a)[3], 1) for a in arms if pred(a)]
    return [len(sub), round(median(sub), 1)] if sub else [0, None]
strata = [
    ("S-N20", "arms of at least 20 patients", [138, 41.5], lambda a: a["evaluable_n"] >= 20),
    ("S-P1ANY", "phase 1, alone or combined", [370, 36.4], lambda a: "PHASE1" in a["phases"]),
    ("S-P2ANY", "phase 2, alone or combined", [355, 40.0], lambda a: "PHASE2" in a["phases"]),
    ("S-P3ANY", "phase 3, alone or combined", [58, 43.6], lambda a: "PHASE3" in a["phases"]),
    ("S-P1ONLY", "phase 1 only", [133, 35.9], lambda a: a["phases"] == ["PHASE1"]),
    ("S-P2ONLY", "phase 2 only", [114, 39.4], lambda a: a["phases"] == ["PHASE2"]),
    ("S-P3ONLY", "phase 3 only", [54, 41.8], lambda a: a["phases"] == ["PHASE3"]),
    ("S-NOPHASE", "no phase recorded", [7, 27.2], lambda a: a["phases"] == []),
    ("S-CTRL", "control-arm candidates", [19, 37.5], lambda a: a["control_arm_candidate"]),
]
for rid, label, quoted, pred in strata:
    rec(rid, "4.2", f"stratum '{label}': arms and median gap", quoted,
        "endpoint-corpus.json", "C2_arms (recomputed)", stratum(pred), "RECOMPUTED")
rec("S-RANGE", "4.2", "the gap is present in every stratum, from 27.2 to 43.6 pp",
    [27.2, 43.6], "endpoint-corpus.json", "C2_arms (recomputed)",
    [min(stratum(p)[1] for _,_,_,p in strata), max(stratum(p)[1] for _,_,_,p in strata)], "RECOMPUTED")

# 4.3 zero-response readouts
for thr, quoted in ((1, [552, 251, 45.5, 105]), (10, [231, 32, 13.9, 11]), (20, [138, 4, 2.9, 2])):
    sub = [a for a in arms if a["evaluable_n"] >= thr]
    zero = [a for a in sub if a["cells"]["CR"] + a["cells"]["PR"] == 0]
    rec(f"Z-{thr}", "4.3", f"arms of at least {thr}: arms, zero-response arms, share, and of those disease control >= 50%",
        quoted, "endpoint-corpus.json", "C2_arms (recomputed)",
        [len(sub), len(zero), round(100*len(zero)/len(sub), 1),
         sum(1 for a in zero if 100*arm_stats(a)[2] >= 50)], "RECOMPUTED")

median_orr = round(median(orrs), 1)
orrs_sorted = sorted(round(x, 1) for x in orrs)
upper_midpoint = orrs_sorted[len(orrs_sorted) // 2]
rec("Z-MEDORR", "4.3 / Figure 3", "corpus median objective response rate 7.7%",
    7.7, "endpoint-corpus.json", "C2_arms (recomputed: median of the 552 per-arm objective-response percentages)",
    median_orr, "RECOMPUTED",
    note="the two middle order statistics of 552 values are %.1f and %.1f; their mean is the median, %.1f. "
         "orr_dcr_reread.py line 107-108 takes orrs[len(orrs)//2], the UPPER of the two, which is %.1f. "
         "Reported as found; not repaired here, and no alternative reading was sought."
         % (orrs_sorted[len(orrs_sorted)//2 - 1], upper_midpoint, median_orr, upper_midpoint))
rec("Z-MEDORR-SELECTOR", "4.3 / Figure 3 (diagnostic)",
    "diagnostic for Z-MEDORR: the upper of the two middle order statistics",
    7.7, "orr-dcr-reread.json", "R8..._corpus_median_objective_response_pct", float(upper_midpoint), "RECOMPUTED",
    note="stated so the MISMATCH above is exactly located: the printed 7.7 is the 277th of 552 sorted values, "
         "not the median. This row is a diagnostic, not a claim of the manuscript.")
bands = [("1-4", 1, 4), ("5-9", 5, 9), ("10-19", 10, 19), ("20-39", 20, 39), ("40+", 40, 10**9)]
stored_bands = {b["band"]: b for b in REREAD["R8_zero_response_readouts"]["disjoint_bins_observed_against_binomial"]["bands"]}
p_med = REREAD["R8_zero_response_readouts"]["disjoint_bins_observed_against_binomial"]["_corpus_median_objective_response_pct"]/100.0
for name, lo, hi in bands:
    sub = [a for a in arms if lo <= a["evaluable_n"] <= hi]
    zero = [a for a in sub if a["cells"]["CR"]+a["cells"]["PR"] == 0]
    sb = stored_bands[name]
    exp = 100*sum((1-p_med)**a["evaluable_n"] for a in sub)/len(sub)
    rec(f"Z-BAND-{name}", "4.3 / Figure 3",
        f"band {name}: arms, median n, zero-response arms, observed %, expected % at the corpus median rate",
        [sb["arms"], sb["median_n"], sb["zero_response_arms"], sb["observed_zero_response_pct"], sb["expected_zero_response_pct"]],
        "orr-dcr-reread.json", f"R8...bands[{name}]",
        [len(sub), float(median([a["evaluable_n"] for a in sub])), len(zero),
         round(100*len(zero)/len(sub), 1), round(exp, 1)], "RECOMPUTED",
        note="expected %% recomputed with p = the artifact's own stored corpus median (%.3f), so this row tests the "
             "band arithmetic and not the choice of p; p itself is row Z-MEDORR. With the true median (%.1f%%) the "
             "expected share for this band is %.1f%%."
             % (p_med, median_orr, 100*sum((1-median_orr/100.0)**a["evaluable_n"] for a in sub)/len(sub)))
rec("Z-BANDRANGE", "Figure 3", "the two track each other across a range from 77.0% to 0.0%",
    [77.0, 0.0], "orr-dcr-reread.json", "R8...bands observed %",
    [max(b["observed_zero_response_pct"] for b in stored_bands.values()),
     min(b["observed_zero_response_pct"] for b in REREAD["R8_zero_response_readouts"]["disjoint_bins_observed_against_binomial"]["bands"])],
    "READ-BACK")
rec("Z-DIRECTION", "Figure 3", "observed sits a little below expected in every band",
    True, "orr-dcr-reread.json", "R8...bands",
    all(b["observed_zero_response_pct"] <= b["expected_zero_response_pct"]
        for b in REREAD["R8_zero_response_readouts"]["disjoint_bins_observed_against_binomial"]["bands"]), "READ-BACK")
top = REREAD["R8_zero_response_readouts"]["disjoint_bins_observed_against_binomial"]["bands"][-1]
rec("Z-TOPBAND", "Figure 3", "the top band is open-ended and its arms have a median of 128.5 patients",
    128.5, "endpoint-corpus.json", "C2_arms (recomputed)",
    float(median([a["evaluable_n"] for a in arms if a["evaluable_n"] >= 40])), "RECOMPUTED")

# Section 5 census
c3b = CORPUS["C3b_census_denominator_decomposed"]
rec("C-BOR", "abstract/5.1", "2,851 trials naming best overall response, 2,715 (95.2%) without the four categories",
    [2851, 2715, 95.2], "endpoint-corpus.json", "C3b...best_overall_response_family",
    [c3b["best_overall_response_family"]["screened"], c3b["best_overall_response_family"]["no_four_cell_block"],
     round(100*c3b["best_overall_response_family"]["no_four_cell_block"]/c3b["best_overall_response_family"]["screened"], 1)],
    "RECOMPUTED")
rec("C-PLACEBO", "5.1", "placebo-comparator family: 1,563 screened, 1,561 without a block, 99.9%",
    [1563, 1561, 99.9], "endpoint-corpus.json", "C3b...placebo_arm_family",
    [c3b["placebo_arm_family"]["screened"], c3b["placebo_arm_family"]["no_four_cell_block"],
     round(100*c3b["placebo_arm_family"]["no_four_cell_block"]/c3b["placebo_arm_family"]["screened"], 1)], "RECOMPUTED")
rv = c3b["records_versus_distinct_trials"]
rec("C-POOLED", "5", "4,414 records screened, 4,276 (96.9%) with no four-cell block",
    [4414, 4276, 96.9], "endpoint-corpus.json", "C3b...records_versus_distinct_trials + R5",
    [rv["records_screened"], REREAD["R5_reporting_census"]["studies_with_posted_results_but_no_four_cell_block"],
     round(100*REREAD["R5_reporting_census"]["studies_with_posted_results_but_no_four_cell_block"]/rv["records_screened"], 1)],
    "RECOMPUTED")
rec("C-DISTINCT", "5.1", "4,235 distinct trials, 4,097 without a block, 96.7%; 179 trials match both queries",
    [4235, 4097, 96.7, 179], "endpoint-corpus.json", "C3b...records_versus_distinct_trials",
    [rv["distinct_ncts_screened"], rv["distinct_ncts_screened"] - rv["distinct_ncts_with_a_four_cell_block"],
     rv["share_not_re_readable_pct_on_distinct_trials"], rv["distinct_ncts_in_both_families"]], "RECOMPUTED")
rec("C-ADD", "5.1", "records exceed distinct trials by exactly the both-family overlap (4,414 - 4,235 = 179)",
    179, "endpoint-corpus.json", "C3b...records_versus_distinct_trials",
    rv["records_screened"] - rv["distinct_ncts_screened"], "RECOMPUTED")
rec("C-DIFF", "5.1", "the difference between the strict and pooled shares is 1.7 percentage points",
    1.7, "endpoint-corpus.json", "C3b (recomputed)",
    round(96.9 - c3b["best_overall_response_family"]["share_not_re_readable_pct"], 1), "RECOMPUTED")
a2 = CORPUS["A2_why_not_abstracts"]
rec("C-ABSTRACTS", "2.1/5", "1,277 abstracts screened, 5 with all four labels, 1 with a denominator they sum to",
    [1277, 5, 1], "endpoint-corpus.json", "A2_why_not_abstracts",
    [a2.get("unique_abstracts_screened"), a2.get("abstracts_with_all_four_category_labels"),
     a2.get("abstracts_with_four_labels_and_a_denominator_they_sum_to")], "READ-BACK")

# Section 3 regime map
g3 = MAP["G3_disease_coordinates"]; g4 = MAP["G4_what_the_map_reads"]; g4b = MAP["G4b_the_accrual_axis_is_two_populations"]
coords = g3["coordinates"]
rec("G-PLACED", "3.2/abstract", "44 conditions had enough of both axes to be placed",
    44, "endpoint-regime-map.json", "G3_disease_coordinates", len(coords), "RECOMPUTED")
rec("G-INCLUSION", "3.2", "a condition is placed only with at least 3 arms and 3 accrual records",
    True, "endpoint-regime-map.json", "G3.coordinates",
    all(c["arms"] >= 3 and c["accrual_records"] >= 3 for c in coords), "RECOMPUTED")
below_null = [c for c in coords if c["median_objective_response_pct"] <= 5.0]
rec("G-NULL16", "3.2/abstract", "16 conditions have a median objective response at or below the 5% null",
    16, "endpoint-regime-map.json", "G3.coordinates (recomputed)", len(below_null), "RECOMPUTED")
nz = [c["median_objective_response_pct"] for c in below_null if c["median_objective_response_pct"] > 0]
rec("G-NULL0", "3.2", "every one of them has a median objective response of 0.0% except one at 4.2%",
    [1, 4.2], "endpoint-regime-map.json", "G3.coordinates (recomputed)", [len(nz), nz[0] if nz else None], "RECOMPUTED")
rec("G-DEFINED", "3.2", "of the 28 conditions where the comparison is defined, 14 (50.0%) had a median trial below the design boundary",
    [28, 14, 50.0], "endpoint-regime-map.json", "G4_what_the_map_reads",
    [g4["conditions_where_the_design_comparison_is_defined"],
     g4["conditions_whose_median_trial_is_below_the_design_contour"],
     round(100*g4["conditions_whose_median_trial_is_below_the_design_contour"]/g4["conditions_where_the_design_comparison_is_defined"], 1)],
    "RECOMPUTED")
rec("G-ZERO7", "3.2", "seven of 29 conditions (24.1%) sit below the zero-event boundary on pooled accrual",
    [7, 29, 24.1], "endpoint-regime-map.json", "G4_what_the_map_reads",
    [g4["conditions_whose_median_trial_is_below_the_zero_event_contour"],
     g4["conditions_where_the_zero_event_comparison_is_defined"],
     round(100*g4["conditions_whose_median_trial_is_below_the_zero_event_contour"]/g4["conditions_where_the_zero_event_comparison_is_defined"], 1)],
    "RECOMPUTED")
comp = g4b["variants"]["completed_trials_only"]; term = g4b["variants"]["terminated_for_accrual_only"]
rec("G-ZEROSPLIT", "3.2", "computed on completed trials the count is zero of 23; on terminated-for-accrual trials 11 of 23",
    [0, 23, 11, 23], "endpoint-regime-map.json", "G4b.variants",
    [comp["conditions_below_the_zero_event_contour"], comp["conditions_where_the_zero_event_comparison_is_defined"],
     term["conditions_below_the_zero_event_contour"], term["conditions_where_the_zero_event_comparison_is_defined"]], "READ-BACK")
rec("G-BOUND", "abstract/3.2/3.4", "the bound on the share below the design boundary is 31.8% to 73.9%",
    [31.8, 73.9], "endpoint-regime-map.json", "G4b.variants",
    [comp["share_below_the_design_contour_pct"], term["share_below_the_design_contour_pct"]], "READ-BACK")
rec("G-BOUNDCALC", "3.4", "the two shares are the two variants' own counts over their own defined denominators",
    [31.8, 73.9], "endpoint-regime-map.json", "G4b.variants (recomputed)",
    [round(100*comp["conditions_below_the_design_contour"]/comp["conditions_where_the_design_comparison_is_defined"], 1),
     round(100*term["conditions_below_the_design_contour"]/term["conditions_where_the_design_comparison_is_defined"], 1)], "RECOMPUTED")
rec("G-ZEROINTERVAL", "3.4", "the zero-event interval runs from 0.0% to 47.8%",
    [0.0, 47.8], "endpoint-regime-map.json", "G4b.variants",
    [comp["share_below_the_zero_event_contour_pct"], term["share_below_the_zero_event_contour_pct"]], "READ-BACK")
rec("G-CANNOT", "3.2", "between 20 of 35 and 30 of 36 placed conditions cannot support a response-rate summary",
    [20, 35, 30, 36], "endpoint-regime-map.json", "G4b.variants",
    [comp["conditions_that_cannot_support_a_response_endpoint_at_all"], comp["conditions_placed"],
     term["conditions_that_cannot_support_a_response_endpoint_at_all"], term["conditions_placed"]], "READ-BACK")
rec("G-CANNOTSUM", "3.2", "'cannot support' is conditions below the design contour plus conditions past the null",
    [20, 30], "endpoint-regime-map.json", "G4b.variants (recomputed)",
    [comp["conditions_below_the_design_contour"] + comp["conditions_at_or_below_the_null"],
     term["conditions_below_the_design_contour"] + term["conditions_at_or_below_the_null"]], "RECOMPUTED")

# 3.4 accrual populations, recomputed from C7_accrual_records
acc = CORPUS["C7_accrual_records"]
by_src = defaultdict(list)
for r in acc: by_src[r["source"]].append(r)
rec("A-RECORDS", "3.4", "accrual populations: 875 completed phase 2 records, 962 terminated records, 1,837 pooled",
    [875, 962, 1837], "endpoint-corpus.json", "C7_accrual_records (recomputed)",
    [len(by_src["ctg_accrual_completed_onc_phase2"]), len(by_src["ctg_accrual_terminated_onc"]), len(acc)], "RECOMPUTED")
def per_condition_medians(records, cond_names):
    out = {}
    for c in cond_names:
        ns = [r["actual_enrollment"] for r in records if c in r["conditions"]]
        if len(ns) >= 3: out[c] = median(ns)
    return out
cond_names = [c["condition"] for c in coords]
med_pooled = per_condition_medians(acc, cond_names)
med_comp = per_condition_medians(by_src["ctg_accrual_completed_onc_phase2"], cond_names)
med_term = per_condition_medians(by_src["ctg_accrual_terminated_onc"], cond_names)
rec("A-MEDIANS", "3.4", "median of the per-condition median enrolments: 54 completed, 8 terminated, 23 pooled",
    [54, 8, 23], "endpoint-corpus.json", "C7_accrual_records (recomputed)",
    [int(median(list(med_comp.values()))), int(median(list(med_term.values()))), int(median(list(med_pooled.values())))],
    "RECOMPUTED",
    note="exact medians of the per-condition median enrolments are %.2f / %.2f / %.2f; endpoint_regime_map._median_int "
         "truncates a median to an integer, which is the convention the printed table uses. Recomputed over the "
         "conditions placed on the map that carry at least 3 accrual records in the population concerned."
         % (median(list(med_comp.values())), median(list(med_term.values())), median(list(med_pooled.values()))))
rec("A-CAPS", "3.4", "both queries were capped at 1,000 records against totals of 2,027 terminated and 16,035 completed phase 2 trials",
    [2027, 16035], "endpoint-corpus.json", "C5_retrieval_provenance / lit-targets protocol",
    None, "READ-BACK",
    missing="the registry query-response headers recording the reported totals. C5_retrieval_provenance in the committed corpus does not retain a per-query 'reported total' field, and re-querying ClinicalTrials.gov is direct network egress, refused in this environment.")

# 3.3 phase composition
low_conds = {c["condition"] for c in below_null}
def phase_mix(conds):
    """Distinct contributing ARMS, not a sum over conditions: an arm listing two placed conditions
    contributes once. Summing G3's per-condition phase_mix double-counts such arms."""
    cnt = Counter()
    for a in arms:
        if set(a["conditions"]) & conds:
            for ph in a["phases"]: cnt[ph] += 1
    return cnt
lowmix = phase_mix(low_conds); restmix = phase_mix({c["condition"] for c in coords} - low_conds)
rec("P-MIXLOW", "3.3", "arms at or below the null are phase-1 heavy: 197 phase 1 against 147 phase 2 and 9 phase 3",
    [197, 147, 9], "endpoint-regime-map.json", "G3.coordinates.phase_mix (recomputed)",
    [lowmix["PHASE1"], lowmix["PHASE2"], lowmix["PHASE3"]], "RECOMPUTED")
rec("P-MIXREST", "3.3", "the remaining placed conditions run 133 phase 2, 96 phase 1 and 37 phase 3",
    [133, 96, 37], "endpoint-regime-map.json", "G3.coordinates.phase_mix (recomputed)",
    [restmix["PHASE2"], restmix["PHASE1"], restmix["PHASE3"]], "RECOMPUTED")
p23 = [c for c in below_null if c.get("phase_2_3_arms", 0) > 0]
still0 = [c for c in p23 if c["median_objective_response_pct_phase_2_3_arms_only"] == 0.0]
risen = [c for c in p23 if c["median_objective_response_pct_phase_2_3_arms_only"] > 0.0]
rec("P-SENS", "3.3", "restricted to phase 2/3 arms the median stays 0.0% for thirteen of the fourteen such conditions; two have none; one rises to 21.4%",
    [13, 14, 2, 21.4], "endpoint-regime-map.json", "G3.coordinates (recomputed)",
    [len(still0), len(p23), len(below_null)-len(p23), risen[0]["median_objective_response_pct_phase_2_3_arms_only"] if risen else None],
    "RECOMPUTED")

# Contours — recomputed from first principles
rec("K-EMC-ZERO", "3.1/8", "a 12.8% response rate requires 17 patients for a 90% chance of observing one response",
    17, "endpoint-regime-map.json", "G5 (recomputed from the binomial)",
    n_for_90pct_one_response(0.128), "RECOMPUTED")
rec("K-EMC-DESIGN", "3.1/8", "a 12.8% response rate requires 79 patients for an exact single-stage design against a 5% null",
    79, "endpoint-regime-map.json", "G5 (recomputed: exact single-stage, alpha 0.05, power 0.80)",
    single_stage_n(0.128), "RECOMPUTED")
grid = {g["objective_response_pct"]: g for g in MAP["G2_contours"]["grid"]}
for pct in (2.0, 5.0, 10.0, 20.0):
    if pct in grid:
        rec(f"K-GRID-{pct}", "3.1 / Figure 1", f"zero-event contour at {pct}% response",
            grid[pct]["n_for_90pct_chance_of_one_response"], "endpoint-regime-map.json",
            f"G2_contours.grid[{pct}]", n_for_90pct_one_response(pct/100.0), "RECOMPUTED")

# Section 6 control arms
p3 = PLACEBO["P3_classification"]
rec("V-19", "6", "nineteen arms carry a control token", 19, "placebo-arm-calibration.json",
    "P3_classification.control_arms_found", p3["control_arms_found"], "RECOMPUTED",
    note="also recomputed from the corpus: arms flagged control_arm_candidate")
rec("V-19C", "6", "the 19 control-token arms are the corpus's control_arm_candidate flag",
    19, "endpoint-corpus.json", "C2_arms[].control_arm_candidate",
    sum(1 for a in arms if a["control_arm_candidate"]), "RECOMPUTED")
comp_types = p3["composition_by_registered_arm_type"]
rec("V-TYPES", "6", "eight registered as placebo comparator or no-intervention, eight as experimental or active comparator, three unresolved",
    [8, 8, 3], "placebo-arm-calibration.json", "P3.composition_by_registered_arm_type",
    [comp_types["PLACEBO_COMPARATOR"] + comp_types["NO_INTERVENTION"],
     comp_types["EXPERIMENTAL"] + comp_types["ACTIVE_COMPARATOR"], comp_types["UNRESOLVED"]], "RECOMPUTED")
rec("V-CLASS", "6", "of those 19, 16 carry an active agent, 2 cannot be matched, 1 is a genuine no-intervention arm",
    [16, 2, 1], "placebo-arm-calibration.json", "P3_classification.counts",
    [p3["counts"]["control_plus_active_backbone"], p3["counts"]["control_arm_unclassified_no_registry_match"],
     p3["counts"]["observation_no_active_agent"]], "READ-BACK")
rec("V-SUM", "6", "the classification partitions all 552 arms", 552, "placebo-arm-calibration.json",
    "P3_classification.counts", sum(p3["counts"].values()), "RECOMPUTED")
p4 = PLACEBO["P4_progression_at_entry_strata"]
rec("V-PROG", "6", "one trial of the 12 states a progression requirement, five mention it without requiring it, six do not mention it",
    [12, 1, 5, 6], "placebo-arm-calibration.json", "P4_progression_at_entry_strata",
    [p4["trials_with_the_field_read"], p4["verdicts_across_those_trials"]["REQUIRED"],
     p4["verdicts_across_those_trials"]["MENTIONED_NOT_AS_A_REQUIREMENT"],
     p4["verdicts_across_those_trials"]["NOT_MENTIONED"]], "RECOMPUTED")
p7 = PLACEBO["P7_traps"]
rec("V-484", "6", "the single no-intervention arm reports a 48.4% objective response",
    48.4, "endpoint-corpus.json", "C2_arms (recomputed over the NO_INTERVENTION arm)",
    None, "RECOMPUTED",
    missing=None if False else None)
# recompute 48.4 directly
noint = [a for a in arms if a["control_arm_candidate"] and a.get("arm_group_type") == "NO_INTERVENTION"]
ROWS.pop()
rec("V-484", "6", "the single no-intervention arm reports a 48.4% objective response",
    48.4, "endpoint-corpus.json", "C2_arms (recomputed over the NO_INTERVENTION arm)",
    round(100*arm_stats(noint[0])[1], 1) if len(noint) == 1 else None, "RECOMPUTED")
p6 = PLACEBO["P6_the_corner_with_no_control_arms"]
rec("V-CORNER", "6.1", "of the 44 conditions placed, 25 have a median objective response of 15% or less; 4 of those 25 have any control arm",
    [25, 4], "placebo-arm-calibration.json", "P6_the_corner_with_no_control_arms",
    [p6["conditions_in_the_low_response_regime"], p6["of_those_with_any_control_arm_in_this_corpus"]], "READ-BACK")
rec("V-CORNER-R", "6.1", "the 25 low-response conditions are those with a median objective response <= 15% among the 44 placed",
    25, "endpoint-regime-map.json", "G3.coordinates (recomputed)",
    sum(1 for c in coords if c["median_objective_response_pct"] <= 15.0), "RECOMPUTED")
p9 = PLACEBO["P9_the_confound_HAS_been_measured_outside_this_corpus"]["the_two_load_bearing_records"]
by_pmid = {r["pmid"]: r for r in p9}
rec("V-PMID37777684", "6.1", "a prospective observational trial placed 100 patients on active surveillance",
    100, "placebo-arm-calibration.json", "P9...pmid 37777684", by_pmid["37777684"]["n"], "READ-BACK")
rec("V-PMID39620931", "6.1", "a pooled analysis of three prospective observational studies followed 282 patients",
    282, "placebo-arm-calibration.json", "P9...pmid 39620931", by_pmid["39620931"]["n"], "READ-BACK")
rec("V-DESMOID-NUMS", "6.1", "3-year PFS 53.4% (95% CI 43.5-63.1), spontaneous regression 58%, partial responses 26%",
    True, "placebo-arm-calibration.json", "P9...pmid 37777684.why_it_matters",
    all(s in by_pmid["37777684"]["why_it_matters"] for s in ["53.4", "43.5-63.1", "58%", "26%"]), "READ-BACK")
rec("V-DESMOID-POOLED", "6.1", "3- and 5-year treatment-free survival 67% and 66%; progression 33% and 34%; regression 26% and 34%",
    True, "placebo-arm-calibration.json", "P9...pmid 39620931.why_it_matters",
    all(s in by_pmid["39620931"]["why_it_matters"] for s in ["67%", "66%", "33%", "34%", "26%"]), "READ-BACK")
rec("V-OVERLAP", "6.1", "whether the French cohort's 282 patients overlap the 100 is stated in neither report and is unknown here",
    "UNKNOWN", "placebo-arm-calibration.json", "P9 (scope statement)", None, "READ-BACK",
    missing="patient-level or centre-level enrolment rosters for PMID 37777684 and the French arm of PMID 39620931. Neither report states it; establishing disjointness would require the primary study records, which are not held here and were not retrieved (no HTTP egress; the PubMed MCP route returns metadata and full text, not enrolment rosters).")
rec("V-PLACEBO20", "6.1", "the placebo arm of a controlled trial recorded a 20% objective response rate before crossover",
    20, "emc-endpoint-alternatives.json", "E10 (companion file, §6 of the companion note)", None, "READ-BACK",
    missing="none for the number itself, but this lane did not open emc-endpoint-alternatives.json E10 (outside the six route artifacts); the value is carried by the companion note the manuscript delegates it to and is NOT re-derived here.")

# Section 7 remedies
a1 = PRIOR["A1_endorsed_alternatives"]; a2f = PRIOR["A2_fix_families"]; a3 = PRIOR["A3_endorsement_grades"]
rec("R-DOCS", "7", "18 retrieved documents falling into four families",
    [18, 4], "endpoint-prior-art-audit.json", "A1_endorsed_alternatives / A2_fix_families",
    [len(a1), len(a2f["documents_per_family"])], "RECOMPUTED")
rec("R-FAMILIES", "7", "family document counts A=4, B=4, C=3, D=7",
    [4, 4, 3, 7], "endpoint-prior-art-audit.json", "A2_fix_families.documents_per_family",
    [a2f["documents_per_family"]["A_switch_to_time_to_event"], a2f["documents_per_family"]["B_redefine_response"],
     a2f["documents_per_family"]["C_add_categories"], a2f["documents_per_family"]["D_patient_as_own_control"]], "READ-BACK")
rec("R-FAMSUM", "7", "the four family counts sum to the 18 retrieved documents",
    18, "endpoint-prior-art-audit.json", "A2_fix_families (recomputed)",
    sum(a2f["documents_per_family"].values()), "RECOMPUTED")
rec("R-IDS", "7", "the per-family identifier lists match the per-family counts",
    [4, 4, 3, 7], "endpoint-prior-art-audit.json", "A2_fix_families.identifiers_per_family (recomputed)",
    [len(a2f["identifiers_per_family"]["A_switch_to_time_to_event"]), len(a2f["identifiers_per_family"]["B_redefine_response"]),
     len(a2f["identifiers_per_family"]["C_add_categories"]), len(a2f["identifiers_per_family"]["D_patient_as_own_control"])], "RECOMPUTED")
rec("R-DOMAINS", "abstract/7", "12 disease domains covered, 7 with a consensus guideline and 5 on a single trial precedent",
    [12, 7, 5], "endpoint-prior-art-audit.json", "A4 / A3_endorsement_grades",
    [PRIOR["A4_diseases_with_an_endorsed_alternative"]["count"], a3["counts"]["consensus_guideline"],
     12 - a3["counts"]["consensus_guideline"]], "RECOMPUTED",
    note="the '5 on a single trial precedent' in prose is the 12 domains minus the 7 guideline-backed domains; A3.counts counts DOCUMENTS (5 methodology, 6 single-trial, 7 guideline), a different denominator")
rec("R-DOMAINS-N", "7", "A4 lists exactly 12 disease domains", 12, "endpoint-prior-art-audit.json",
    "A4.disease_domains_covered (recomputed)", len(PRIOR["A4_diseases_with_an_endorsed_alternative"]["disease_domains_covered"]), "RECOMPUTED")
rec("R-GRADESUM", "7", "the endorsement-grade counts sum to the 18 documents",
    18, "endpoint-prior-art-audit.json", "A3.counts (recomputed)", sum(a3["counts"].values()), "RECOMPUTED")
rec("R-1998", "7", "the earliest retrieved document dates from 1998",
    1998, "endpoint-prior-art-audit.json", "A1_endorsed_alternatives (recomputed)",
    min(int(d["year"]) for d in a1 if str(d.get("year", "")).isdigit()), "RECOMPUTED")
rec("R-25", "7 / 6.1", "25 conditions in the low-response regime (A5 and P6 agree)",
    25, "endpoint-prior-art-audit.json", "A5_the_gap.conditions_in_the_low_response_regime",
    PRIOR["A5_the_gap"]["conditions_in_the_low_response_regime"], "READ-BACK")

# Section 8 EMC worked extreme
d1 = DISC["D1_same_patients_two_endpoints"]
rec("E-ORR", "8", "objective response 12.8% (6 of 47, Wilson 95% CI 6.0 to 25.2)",
    [6, 47, 12.8, 6.0, 25.2], "emc-endpoint-discordance.json", "D1.objective_response",
    [d1["objective_response"]["events"], d1["objective_response"]["denom"],
     round(100*6/47, 1), round(100*wilson(6, 47)[0], 1), round(100*wilson(6, 47)[1], 1)], "RECOMPUTED")
rec("E-DCR", "8", "disease control 89.4% (42 of 47, 77.4 to 95.4)",
    [42, 47, 89.4, 77.4, 95.4], "emc-endpoint-discordance.json", "D1.disease_control",
    [d1["disease_control"]["events"], d1["disease_control"]["denom"],
     round(100*42/47, 1), round(100*wilson(42, 47)[0], 1), round(100*wilson(42, 47)[1], 1)], "RECOMPUTED")
rec("E-GAP", "8", "a gap of 76.6 percentage points composed entirely of 36 patients with stable disease",
    [76.6, 36], "emc-endpoint-discordance.json", "D1 (recomputed)",
    [round(100*36/47, 1), d1["discordant_patients_stable_disease_only"]["events"]], "RECOMPUTED")
rec("E-FIXED", "8", "fixed-event sensitivity on 46: 13.0% objective response (6.1 to 25.7), 91.3% disease control (79.7 to 96.6), gap 78.3",
    [13.0, 6.1, 25.7, 91.3, 79.7, 96.6, 78.3], "emc-endpoint-discordance.json", "D1 (recomputed on denom 46)",
    [round(100*6/46, 1), round(100*wilson(6, 46)[0], 1), round(100*wilson(6, 46)[1], 1),
     round(100*42/46, 1), round(100*wilson(42, 46)[0], 1), round(100*wilson(42, 46)[1], 1),
     round(100*36/46, 1)], "RECOMPUTED")
rec("E-SHIFT", "8", "a shift of 1.7 points against the nominal 76.6",
    1.7, "emc-endpoint-discordance.json", "D1 (recomputed)",
    round(round(100*36/46, 1) - round(100*36/47, 1), 1), "RECOMPUTED")
rec("E-IMMUNO", "8", "the IMMUNOSARC II abstract reports 23 response-evaluable patients whose categories sum to 22 (2 OR, 18 SD, 2 PD)",
    [23, 22, 2, 18, 2], "emc-endpoint-discordance.json", "D1.per_cohort.sunitinib_nivolumab_immunosarc2",
    None, "READ-BACK")
ROWS.pop()
ic = d1["per_cohort"]["sunitinib_nivolumab_immunosarc2"]
rec("E-IMMUNO", "8", "the IMMUNOSARC II abstract reports 23 response-evaluable patients whose categories sum to 22 (2 OR, 18 SD, 2 PD)",
    [23, 22, 2, 18, 2], "emc-endpoint-discordance.json", "D1.per_cohort.sunitinib_nivolumab_immunosarc2",
    [ic["n_response_evaluable"], ic["objective_response"] + ic["stable_disease"] + ic["progressive_disease"],
     ic["objective_response"], ic["stable_disease"], ic["progressive_disease"]], "RECOMPUTED")
rec("E-COHORTN", "8", "the two modern prospective cohorts accrued 22 and 23 response-evaluable patients",
    [22, 23], "emc-endpoint-discordance.json", "D1.per_cohort",
    [d1["per_cohort"]["pazopanib_phase2"]["n_response_evaluable"], ic["n_response_evaluable"]], "READ-BACK")
r7 = REREAD["R7_emc_row_in_the_field_distribution"]
rec("E-PCTILE", "8/abstract", "76.6 points falls at the 88.9th percentile of the 552 arms",
    [491, 552, 88.9], "orr-dcr-reread.json", "R7 (recomputed against the corpus gaps)",
    [sum(1 for g in gaps if g < 76.6), len(gaps), round(100*sum(1 for g in gaps if g < 76.6)/len(gaps), 1)], "RECOMPUTED")
rec("E-3COHORTS", "8", "three cohorts, three different regimens, 47 response-evaluable patients",
    [3, 47], "emc-endpoint-discordance.json", "D1",
    [d1["n_cohorts"], d1["n_patients"]], "READ-BACK")
rec("E-CELLSUM", "8", "the per-cohort response-evaluable counts sum to the nominal 47",
    47, "emc-endpoint-discordance.json", "D1.per_cohort (recomputed)",
    sum(c["n_response_evaluable"] for c in d1["per_cohort"].values()), "RECOMPUTED")

# ---------- Known-answer controls ----------
CONTROLS = []
def ctl(name, expected, got, what):
    CONTROLS.append({"control": name, "expected": expected, "got": got, "what_it_detects": what,
                     "passed": bool(_eq(expected, got))})

# 1. Wilson CI computed a second, independent way (score-equation bisection).
a_lo, a_hi = wilson(6, 47); b_lo, b_hi = wilson_by_rootfind(6, 47)
ctl("wilson_closed_form_vs_score_root_find_6_of_47",
    [round(100*a_lo, 1), round(100*a_hi, 1)], [round(100*b_lo, 1), round(100*b_hi, 1)],
    "a wrong Wilson algebra would move both endpoints; the bisection solves the score equation directly")
# 2. Textbook binomial known answers.
ctl("binomial_known_answers", [0.5, 0.25, 1.0],
    [round(binom_sf_atleast(1, 1, 0.5), 6), round(binom_sf_atleast(2, 2, 0.5), 6), round(binom_sf_atleast(0, 5, 0.3), 6)],
    "a broken binomial tail would break every contour row")
# 3. Median/quantile against a hand-checkable vector.
ctl("quantile_type7_known_vector", [2.5, 1.75, 3.25],
    [quantile_type7([1, 2, 3, 4], .5), quantile_type7([1, 2, 3, 4], .25), quantile_type7([1, 2, 3, 4], .75)],
    "the IQR row depends on the quantile convention")
# 4. Sibling-artifact known answer: R2_per_arm_rows independently recompute from C2 cells.
# (nct_id, arm_title) is NOT unique in this corpus -- 87 collisions -- so pair positionally and
# assert the identifiers agree, rather than keying on a non-unique pair.
r2rows = REREAD["R2_per_arm_rows"]
mismatched_rows = []
if len(r2rows) != len(arms):
    mismatched_rows.append(("length", f"{len(arms)} vs {len(r2rows)}"))
else:
    for a, s in zip(arms, r2rows):
        n, orr, dcr, sd, _ = arm_stats(a)
        if (a["nct_id"], a["arm_title"], a["cells"]) != (s["nct_id"], s["arm_title"], s["cells"]) or \
           s["n"] != n or abs(s["gap_pp"] - round(100*sd, 1)) > 0.05 or \
           abs(s["objective_response"]["pct"] - round(100*orr, 1)) > 0.05:
            mismatched_rows.append(((a["nct_id"], a["arm_title"]), "value differs"))
ctl("R2_rows_recompute_from_C2_cells", 0, len(mismatched_rows),
    "cross-artifact known answer: the analysis file's 552 per-arm rows must equal what this harness computes from the corpus cells")
# 5. Deliberate-corruption (mutation) control: the harness must report a MISMATCH when the data is wrong.
import copy
bad = copy.deepcopy(arms)
bad[0]["cells"]["SD"] += 40  # denominator deliberately left alone so the four-cell identity breaks
bad_gaps = [round(100*(a["cells"]["SD"]/a["evaluable_n"]), 1) for a in bad]
ctl("mutation_control_median_gap_moves_on_corrupted_input",
    True, round(median(bad_gaps), 1) != round(median(gaps), 1),
    "if a corrupted corpus still produced the published median, the comparison would be vacuous")
ctl("mutation_control_identity_breaks_on_corrupted_input",
    False, all(sum(a["cells"].values()) == a["evaluable_n"] for a in bad),
    "the four-cell identity assertion must fail on a row whose cells no longer sum to its denominator")

out = {
    "_schema": "endpoint-1-claim-rederivation-ledger/1",
    "_generated_by": "research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                     "PORTFOLIO-INVESTIGATIONS-2026-09-08/ENDPOINT-1/rederive_claims.py",
    "lane": "ENDPOINT-1", "endpoint": "PUB-ENDPOINT",
    "campaign": "OPUS-CAPACITY-CAMPAIGN-20260908",
    "manuscript": "research/manuscripts/endpoint/response-endpoint-indolent-tumours.md",
    "route": "RT-ENDPOINT-CHOICE",
    "what_this_is": "one row per quantitative claim in the manuscript: the quoted value, the artifact and key it "
                    "comes from, the value re-derived here, and a verdict. A MISMATCH is reported, never repaired.",
    "what_this_is_not": "not a review, not a check of the artifacts against their raw registry payloads, and not any "
                        "statement about efficacy, safety, selectivity or clinical readiness of any agent.",
    "input_sha256": {
        "response-endpoint-indolent-tumours.md": H_MS, "endpoint-corpus.json": H_CORPUS,
        "orr-dcr-reread.json": H_REREAD, "endpoint-regime-map.json": H_MAP,
        "placebo-arm-calibration.json": H_PLACEBO, "endpoint-prior-art-audit.json": H_PRIOR,
        "emc-endpoint-discordance.json": H_DISC,
    },
    "known_answer_controls": CONTROLS,
    "summary": dict(Counter(r["verdict"] for r in ROWS)) | {"rows": len(ROWS)},
    "rows": ROWS,
}
with open(os.path.join(LANE, "claim-rederivation-ledger.json"), "w") as fh:
    json.dump(out, fh, indent=1)
    fh.write("\n")

print(json.dumps(out["summary"], indent=1))
print("\ncontrols:")
for c in CONTROLS:
    print(" ", "PASS" if c["passed"] else "FAIL", c["control"], c["expected"], "vs", c["got"])
print("\nnon-REPRODUCES rows:")
for r in ROWS:
    if r["verdict"] != "REPRODUCES":
        print(f'  {r["verdict"]:26s} {r["id"]:16s} §{r["manuscript_section"]:12s} quoted={r["quoted_value"]} derived={r["rederived_value"]}')
bad_ctl = [c for c in CONTROLS if not c["passed"]]
sys.exit(2 if bad_ctl else 0)
