#!/usr/bin/env python3
"""
PUB-LOCOREGIONAL / portfolio investigation 2026-09-08.

QUESTION
  Restricted to COUNTED local-recurrence events with a stated treatment-arm assignment,
  what is the ENTIRE admissible evidence base in this repository for the
  surgery+radiotherapy vs surgery-alone contrast in EMC -- once cohort overlap,
  endpoint definition and arm-level event availability are made explicit?

This script asserts NO efficacy, safety or therapeutic claim. It counts what is countable
and states what is not. Read-only over committed inputs; writes one JSON artifact next to it.
"""
import json, math, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(ROOT, *a)

REGISTRY = "research/data/emc-clinical-registry.json"
RTCONTRA = "research/modalities/emc-radiotherapy-contradiction.json"
PROGCOEF = "research/modalities/emc-prognostic-coefficients.json"
SITECUR  = "research/modalities/emc-site-curation.json"
LOCOELIG = "research/modalities/emc-locoregional-eligibility.json"

Z = 1.959963984540054

def wilson(events, denom):
    if denom == 0:
        return None
    p = events / denom
    d = 1 + Z * Z / denom
    c = p + Z * Z / (2 * denom)
    h = Z * math.sqrt(p * (1 - p) / denom + Z * Z / (4 * denom * denom))
    return [round(100 * (c - h) / d, 1), round(100 * (c + h) / d, 1)]

def fisher_two_sided(a, b, c, d):
    """2x2 [[a,b],[c,d]]; two-sided Fisher exact by summing tables no more probable."""
    n = a + b + c + d
    r1, c1 = a + b, a + c
    def prob(x):
        return (math.comb(r1, x) * math.comb(n - r1, c1 - x)) / math.comb(n, c1)
    lo = max(0, c1 - (n - r1)); hi = min(r1, c1)
    p0 = prob(a)
    return sum(prob(x) for x in range(lo, hi + 1) if prob(x) <= p0 * (1 + 1e-9))

def load(rel):
    with open(P(rel)) as f:
        return json.load(f)

reg = load(REGISTRY)["registry"]
rtc = load(RTCONTRA)
prog = load(PROGCOEF)
site = load(SITECUR)
elig = load(LOCOELIG)

est = {e["source_id"]: e for e in rtc["estimates"]}

# ---------------------------------------------------------------- 1. arm-level event ledger
arm_ledger = []

b = est["bishop2019"]
b_cmt_n = b["arms"]["preoperative_RT"] + b["arms"]["postoperative_RT"]
b_sa_n = b["arms"]["surgery_alone"]
b_events_total = b["events"]
b_sa_events = 4      # "4 of the 5 had surgery alone" -- printed integer, RTCONTRA.estimates[0].events_note
b_cmt_events = b_events_total - b_sa_events
arm_ledger.append({
    "source_id": "bishop2019",
    "arm_sizes_printed": {"surgery_plus_RT": b_cmt_n, "surgery_alone": b_sa_n},
    "arm_size_sum_equals_cohort_n": b_cmt_n + b_sa_n == 41,
    "local_events_total_printed": b_events_total,
    "arm_level_events_available": True,
    "arm_level_events": {"surgery_plus_RT": b_cmt_events, "surgery_alone": b_sa_events},
    "how_the_arm_split_is_known": ("printed as an integer sentence, not derived from a percentage: "
        "'5 patients (12%) with local relapse ... 4 of the 5 had surgery alone' "
        f"({RTCONTRA} -> estimates[0].events_note / .printed_in)"),
    "endpoint_as_printed": b["endpoint"],
    "endpoint_class": "actuarial_local_control_at_10y (headline) + crude during-follow-up relapse count (events)",
    "median_followup_months": b["median_followup_months"],
    "pooled_in_registry_headline": False,
    "why_not_pooled": "population-overlap (US single institution; likely within SEER / US Sarcoma Collaborative)",
})

m = est["masunaga2025"]
m_rt = [v for mdl in prog["models"] if mdl.get("model_id") == "masunaga2025_lrfs_univariate"
        for v in mdl["rows"] if v["variable"] == "neoadjuvant_or_adjuvant_radiotherapy"]
arm_ledger.append({
    "source_id": "masunaga2025",
    "arm_sizes_printed": {"radiotherapy": m["arms"]["neoadjuvant_RT"] + m["arms"]["adjuvant_RT"],
                          "no_perioperative_RT": m["arms"]["no_perioperative_RT"]},
    "arm_size_sum_equals_cohort_n": (m["arms"]["neoadjuvant_RT"] + m["arms"]["adjuvant_RT"]
                                     + m["arms"]["no_perioperative_RT"]) == 134,
    "local_events_total_printed": m["events"],
    "arm_level_events_available": False,
    "arm_level_events": None,
    "how_the_arm_split_is_known": ("NOT PRINTED. Table 2 publishes arm sizes (24 / 110) and a hazard ratio "
        "0.50 (0.11-2.25), p=0.365, but no per-arm local-recurrence event count. "
        "Reconstructing one from the HR would be deriving counts from a modelled quantity, "
        "which POLICY-evidence 2.1(2) forbids for pooling."),
    "endpoint_as_printed": m["endpoint"],
    "endpoint_class": "time-to-event (local recurrence-free survival), univariate HR only",
    "median_followup_months": m["median_followup_months"],
    "pooled_in_registry_headline": True,
    "why_not_pooled": None,
    "coefficient_row": m_rt,
})

countable = [a for a in arm_ledger if a["arm_level_events_available"]]
events_carrying_contrast = sum(a["local_events_total_printed"] for a in countable)

# ---------------------------------------------------------------- 2. the one countable 2x2
a_, b_ = b_sa_events, b_sa_n - b_sa_events        # surgery alone: event, no event
c_, d_ = b_cmt_events, b_cmt_n - b_cmt_events     # surgery + RT
two_by_two = {
    "series": "bishop2019",
    "table": {"surgery_alone": {"local_relapse": a_, "no_local_relapse": b_, "n": b_sa_n},
              "surgery_plus_RT": {"local_relapse": c_, "no_local_relapse": d_, "n": b_cmt_n}},
    "crude_risk_percent": {"surgery_alone": round(100 * a_ / b_sa_n, 1),
                           "surgery_plus_RT": round(100 * c_ / b_cmt_n, 1)},
    "wilson_95ci_percent": {"surgery_alone": wilson(a_, b_sa_n),
                            "surgery_plus_RT": wilson(c_, b_cmt_n)},
    "fisher_exact_two_sided_p": round(fisher_two_sided(a_, b_, c_, d_), 5),
    "total_events_in_the_table": a_ + c_,
    "⛔_this_is_not_an_effect_estimate": (
        "A crude 2x2 over 41 retrospectively treated patients with 5 events, no adjustment, "
        "no randomisation and treatment assigned by indication. It is reported here to show HOW LITTLE "
        "counted evidence sits under the published 'combined modality improves local control' headline, "
        "not to estimate an effect. No efficacy claim is made or supported."),
}

# fragility: how many surgery-alone events must be reassigned to make Fisher p cross 0.05
frag = None
for k in range(1, a_ + 1):
    if fisher_two_sided(a_ - k, b_ + k, c_, d_) > 0.05:
        frag = k
        break
two_by_two["events_that_must_move_for_p_to_cross_0.05"] = frag

# ------------------------------------------------- 3. actuarial-vs-crude internal consistency
consistency = {
    "check": ("Bishop's headline is 10-year local control 100% (surgery+RT) vs 63% (surgery alone). "
              "The crude event data in the same paper are 1 relapse among 33 surgery+RT patients."),
    "arithmetic": ("A 10-year actuarial local control of 100% cannot coexist with a relapse inside "
                   "10 years in that arm. So the single surgery+RT relapse must have occurred after "
                   "120 months, or that patient was censored before it."),
    "printed_relapse_times": b["events_note"],
    "relapse_time_range_months": [13, 176],
    "verdict": ("CONSISTENT ONLY IF the surgery+RT relapse is at or beyond 120 months -- the printed "
                "range reaches 176 months, so consistency is possible and is NOT contradicted. "
                "But it means the '100%' is a statement about a censored time horizon, not a statement "
                "that the arm had no local relapses. The paper's own event count says it had one."),
    "⛔_what_this_does_NOT_show": ("It does not show the paper is wrong, and it does not show radiotherapy "
                                  "fails. It shows that quoting '100% local control' without the event count "
                                  "and the horizon overstates what was observed."),
    "decidable_from": f"{RTCONTRA} -> estimates[0] (.ten_year_local_control_percent, .events, .events_note)",
}

# ---------------------------------------------------------------- 4. overlap ledger
overlap = []
for c in reg["cohorts"]:
    sid = c.get("sourceId")
    cit = reg["citations"].get(sid, {})
    overlap.append({
        "label": c.get("label"), "source_id": sid, "n": c.get("n"),
        "study_period": c.get("studyPeriod") or ("unknown" if c.get("studyPeriodUnknown") else None),
        "population": cit.get("population") or cit.get("design"),
        "pooled": c.get("pool"), "context_reason": c.get("contextReason"),
        "provenance": c.get("provenance"),
        "has_local_endpoint": bool(c.get("recurrence") or c.get("recurrencePct") or c.get("recurrenceText")),
        "local_endpoint_definition_recorded_in_registry": (
            "locoregional recurrence (stated in note)" if sid == "ussc2022"
            else "local relapse (stated in note)" if sid == "bishop2019"
            else "by surgical margin, percentage-only" if sid == "remiszewski2025" and c.get("recurrenceText")
            else "NOT STATED IN THE REGISTRY -- it records 'recurrence' without saying local, distant or any"
            if c.get("recurrence") or c.get("recurrencePct") else None),
        "endpoint_definition_resolvable_elsewhere": (
            ("emc-radiotherapy-contradiction.json -> estimates[1] establishes that masunaga2025's 16 events "
             "are LOCAL recurrence ('16 patients (11.9%) with local recurrence'), endpoint "
             "'local recurrence-free survival'") if sid == "masunaga2025"
            else "NOT RESOLVED in any committed artifact read here" if (c.get("recurrence") and sid in
                 {"meisKindblom1999", "chiusole2020"}) else None),
    })

us_overlap_family = sorted({o["source_id"] for o in overlap
                            if o["source_id"] in {"bishop2019", "ussc2022", "seer270_2022",
                                                  "remiszewski2025", "uMich2023"}})

# ------------------------------------------- 5. endpoint heterogeneity of the existing pool
pool_rows = [o for o in overlap if o["pooled"] and o["has_local_endpoint"]]
headline = elig.get("who_recurs_locally")

result = {
    "_id": "PUB-LOCOREGIONAL-RT-CONTRAST-LEDGER-2026-09-08",
    "_question": __doc__.split("QUESTION")[1].split("This script")[0].strip(),
    "_not_medical_advice": ("Nothing here asserts efficacy, safety, tolerability, a therapeutic window or "
                            "clinical readiness for radiotherapy or any other local treatment. "
                            "Retrospective series with treatment assigned by indication cannot establish that."),
    "_inputs": {"registry": REGISTRY, "rt_contradiction": RTCONTRA, "prognostic_coefficients": PROGCOEF,
                "site_curation": SITECUR, "locoregional_eligibility": LOCOELIG},
    "_method": ("Wilson score intervals per POLICY-evidence 2.2; two-sided Fisher exact from stdlib "
                "math.comb; no pooling performed across series (see admissibility_verdict)."),
    "arm_level_event_ledger": arm_ledger,
    "series_with_arm_level_local_events": [a["source_id"] for a in countable],
    "total_counted_local_events_carrying_the_RT_contrast": events_carrying_contrast,
    "the_one_countable_2x2": two_by_two,
    "actuarial_vs_crude_consistency": consistency,
    "population_overlap_ledger": overlap,
    "us_population_overlap_family": us_overlap_family,
    "existing_headline_local_recurrence_pool": {
        "value_from_committed_artifact": headline,
        "⚠_endpoint_mixture": ("The pooled 'local recurrence' headline mixes endpoint definitions: ussc2022 "
                               "contributes an explicitly LOCOREGIONAL recurrence count while masunaga2025, "
                               "meisKindblom1999 and chiusole2020 contribute a count the registry records only "
                               "as 'recurrence'. For 3 of the 4 pooled cohorts the registry does not state "
                               "whether the endpoint is local, distant or any recurrence."),
        "pooled_rows_and_their_recorded_endpoint_definition": [
            {"source_id": r["source_id"], "definition": r["local_endpoint_definition_recorded_in_registry"]}
            for r in pool_rows],
    },
    "admissibility_verdict": {
        "can_an_RT_vs_no_RT_contrast_be_POOLED_across_series": False,
        "why": [
            "k=1. Only bishop2019 publishes per-arm local-event counts; masunaga2025 publishes arm sizes and a "
            "hazard ratio but no per-arm event count, and POLICY-evidence 2.1(2) forbids reconstructing counts.",
            "The two series' local endpoints are not the same estimand: 10-year actuarial local control vs "
            "local recurrence-free survival. POLICY-evidence 2.4 forbids merging time-anchored figures.",
            "bishop2019 is pool:false for population overlap with the US Sarcoma Collaborative / SEER family, "
            "so it cannot be summed with any other US series either.",
            "No other cohort in the registry records a local-treatment exposure at all.",
        ],
        "what_the_evidence_base_actually_amounts_to": (
            f"{events_carrying_contrast} counted local-recurrence events, in one non-poolable "
            "single-institution retrospective series, split 4 / 1 between arms of 8 and 33 patients."),
        "⛔_no_go": ("No claim about the effectiveness of adjuvant radiotherapy on local control in EMC "
                    "can be supported at the level of counted events by this repository's evidence base. "
                    "A manuscript may state the size of the population, the arm sizes, the event counts and "
                    "the two published hazard ratios with their intervals -- and must not synthesise them."),
    },
}

OUT = os.path.join(HERE, "rt-local-control-contrast-ledger.json")
if "--check" in sys.argv:
    prev = json.load(open(OUT)) if os.path.exists(OUT) else None
    same = prev == result
    print("CHECK", "MATCH" if same else "DIFFERS")
    sys.exit(0 if same else 1)
with open(OUT, "w") as f:
    json.dump(result, f, indent=1, ensure_ascii=False)
    f.write("\n")
print("wrote", OUT)
print("counted events carrying the contrast:", events_carrying_contrast)
print("2x2:", two_by_two["table"])
print("crude %:", two_by_two["crude_risk_percent"], "Wilson:", two_by_two["wilson_95ci_percent"])
print("fisher p:", two_by_two["fisher_exact_two_sided_p"], "fragility:", frag)
print("pool possible:", result["admissibility_verdict"]["can_an_RT_vs_no_RT_contrast_be_POOLED_across_series"])
