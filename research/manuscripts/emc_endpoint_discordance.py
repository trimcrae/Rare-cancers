#!/usr/bin/env python3
"""How far apart do OBJECTIVE RESPONSE and DISEASE CONTROL sit when they are read off the SAME
extraskeletal myxoid chondrosarcoma (EMC) patients?

WHY THIS EXISTS
---------------
`emc-systemic-therapy-pooling.json` already pools both endpoints, and it owns those two numbers.
What it does not do is put them on the same denominator and ask what the difference costs, which is
the question a person designing or reading a 20-patient trial in this disease actually has. That
question needs four things nothing in this repository derives:

  D1  the two endpoints computed over the IDENTICAL patient set, with the discordant count named;
  D2  the share of the observed disease-control signal that an objective-response reading cannot see;
  D3  a completeness census -- for how many published EMC cohorts is each endpoint even extractable
      as an integer count, which is a property of the LITERATURE rather than of the disease;
  D4  the small-trial arithmetic that follows from each endpoint's event rate.

⛔ THIS FILE ASSERTS NOTHING ABOUT ANY DRUG. Every quantity below is arithmetic over integer counts
that `emc-systemic-therapy-pooling.json` already carries with their quotes and citations. It adds no
patient, no study and no clinical judgement, and a difference between two endpoints is a fact about
MEASUREMENT, never evidence that a treatment worked. The confound that stops it being the latter --
stable disease in an indolent tumour may be natural history -- is carried in the output as a
first-class field (`the_objection_that_this_cannot_answer`) rather than as a closing caveat, because
it is the strongest argument against the reading and it must travel with the number.

METHOD IS NOT NEGOTIABLE: systems/POLICY-evidence.md 2.1-2.4, same as the source file --
  * crude denominator-weighted proportions,
  * Wilson score 95% intervals (the SAME implementation as the source; parity is asserted, not hoped),
  * explicit integer {events, denom} only,
  * non-overlapping populations only,
  * time-to-event endpoints are never merged.

ONE HOME. The pooled objective-response and disease-control proportions belong to
`emc-systemic-therapy-pooling.json` -> `analyses.A1_*` / `analyses.A4_*`. This file RE-DERIVES them
from the same cohort rows purely as a parity check (`parity_with_source`) and fails if they differ,
so the discordance figures below are provably about the same object. It does not become a second
home for them.

Regenerate:  python3 research/manuscripts/emc_endpoint_discordance.py
Verify:      python3 research/manuscripts/emc_endpoint_discordance.py --check
Output:      research/manuscripts/emc-endpoint-discordance.json
Read by:     research/manuscripts/emc-response-endpoint-paper.md
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "emc-systemic-therapy-pooling.json")
OUT = os.path.join(HERE, "emc-endpoint-discordance.json")

SOURCE_REL = "research/manuscripts/emc-systemic-therapy-pooling.json"

# The three prospective EMC cohorts. Named rather than filtered, because "which cohorts may be
# pooled" is an evidence-contract judgement that the source file made and recorded with its reasons
# (`analyses.A1_*.why_these_three_may_be_pooled`); re-deriving the membership here by predicate would
# quietly create a second, unreviewed answer to that question. The assertion below checks that this
# list still equals what the source pools, so the two cannot drift apart in silence.
PROSPECTIVE = ["pazopanib_phase2", "sunitinib_nivolumab_immunosarc2", "trabectedin_emc_subset"]

# Trial sizes the arithmetic in D4 is reported at. Chosen to bracket what this disease has actually
# accrued: the two modern prospective EMC cohorts enrolled 22 and 23 response-evaluable patients, so
# 10-30 is the real design space and anything larger is hypothetical for a tumour whose incidence is
# well under one per million.
TRIAL_SIZES = [10, 15, 20, 22, 23, 25, 30]


# ------------------------------------------------------------------------------------------------
# Statistics. Byte-identical in behaviour to `emc_systemic_therapy_pooling.wilson` / `.pct` --
# duplicated rather than imported because that module executes a full build at import time; the
# `parity_with_source` block is what proves the two agree, and it would still catch a divergence if
# either implementation were edited.
# ------------------------------------------------------------------------------------------------
def wilson(events: int, n: int, z: float = 1.96):
    """Wilson score 95% interval for a binomial proportion (events out of n)."""
    if n <= 0:
        return (None, None)
    p = events / n
    z2 = z * z
    denom = 1 + z2 / n
    centre = p + z2 / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))
    return (round((centre - half) / denom, 4), round((centre + half) / denom, 4))


def pct(x):
    return None if x is None else round(100.0 * x, 1)


def load_source():
    with open(SOURCE, encoding="utf-8") as fh:
        return json.load(fh)


def cohort_map(src):
    return {c["key"]: c for c in src["cohorts"]}


# ------------------------------------------------------------------------------------------------
# The one arithmetic inconsistency in the underlying data, propagated rather than smoothed over.
# IMMUNOSARC II's EMC cohort states 23 response-evaluable patients, and its own best-response
# categories sum to 22 (2 responses + 18 stable + 2 progressive). One patient is unaccounted for and
# the abstract does not reconcile it. The source file carries the same sensitivity on A1. Reporting
# only the 23-denominator version would hide a defect in the newest datapoint this disease has.
# ------------------------------------------------------------------------------------------------
IMMUNOSARC2 = "sunitinib_nivolumab_immunosarc2"


def _sensitivity_22(rows, gap_as_reported):
    orr_ev = sum(r["orr_events"] for r in rows)
    dc_ev = sum(r["dc_events"] for r in rows)
    dn = sum(22 if r["key"] == IMMUNOSARC2 else r["orr_denom"] for r in rows)
    sd_ev = dc_ev - orr_ev
    o_lo, o_hi = wilson(orr_ev, dn)
    d_lo, d_hi = wilson(dc_ev, dn)
    s_lo, s_hi = wilson(sd_ev, dn)
    row = next(r for r in rows if r["key"] == IMMUNOSARC2)
    gap = round(pct(dc_ev / dn) - pct(orr_ev / dn), 1)
    return {
        "why": (
            "IMMUNOSARC II's EMC cohort reports %d response-evaluable patients, and its best-response "
            "categories sum to %d (%d objective response + %d stable + %d progressive). The abstract "
            "does not reconcile the difference and no full paper exists. Every headline figure is "
            "therefore recomputed with that cohort's denominator set to the sum of its own "
            "categories." % (row["orr_denom"], row["orr_events"] + row["sd_events"] + row["pd_events"],
                             row["orr_events"], row["sd_events"], row["pd_events"])),
        "n_patients": dn,
        "objective_response_pct": pct(orr_ev / dn),
        "objective_response_wilson95_pct": [pct(o_lo), pct(o_hi)],
        "disease_control_pct": pct(dc_ev / dn),
        "disease_control_wilson95_pct": [pct(d_lo), pct(d_hi)],
        "discordant_stable_disease_pct": pct(sd_ev / dn),
        "discordant_stable_disease_wilson95_pct": [pct(s_lo), pct(s_hi)],
        "gap_pct_points": gap,
        "gap_moves_by_pct_points": round(gap - gap_as_reported, 1),
        "conclusion": (
            "Dropping the unaccounted-for patient moves the gap between the two endpoints from %s "
            "to %s percentage points, a change of %s. The direction is AGAINST the smaller reading, "
            "so the version reported as headline is the conservative one. The inconsistency is real, "
            "it is the newest datapoint this disease has, and it is reported rather than smoothed "
            "over -- but it does not carry the finding."
            % (gap_as_reported, gap, round(gap - gap_as_reported, 1))),
    }


# ------------------------------------------------------------------------------------------------
# D1 -- the same patients, read twice
# ------------------------------------------------------------------------------------------------
def d1_same_patients(by_key):
    rows = [by_key[k] for k in PROSPECTIVE]

    orr_ev = sum(r["orr_events"] for r in rows)
    orr_dn = sum(r["orr_denom"] for r in rows)
    dc_ev = sum(r["dc_events"] for r in rows)
    dc_dn = sum(r["orr_denom"] for r in rows)

    # The load-bearing precondition. If the two endpoints were evaluated on different numbers of
    # patients the comparison below would be between populations, not between endpoints, and the
    # whole point would be lost. Every one of these three cohorts reports both categories over the
    # same response-evaluable denominator; assert it rather than assume it.
    assert orr_dn == dc_dn, "objective response and disease control are not on the same denominator"

    # The discordant patients -- best response stable disease: counted as a failure by objective
    # response and as an event by disease control. Derived two independent ways from the source rows
    # and required to agree, because `sd_events` and `dc_events - orr_events` are separately
    # extracted fields and a transcription error in either would otherwise pass unseen.
    sd_direct = sum(r["sd_events"] for r in rows)
    sd_by_subtraction = dc_ev - orr_ev
    assert sd_direct == sd_by_subtraction, (
        f"stable-disease count disagrees: reported {sd_direct}, "
        f"disease control minus response {sd_by_subtraction}"
    )

    orr_lo, orr_hi = wilson(orr_ev, orr_dn)
    dc_lo, dc_hi = wilson(dc_ev, dc_dn)
    sd_lo, sd_hi = wilson(sd_direct, orr_dn)

    per = {}
    for r in rows:
        n = r["orr_denom"]
        per[r["key"]] = {
            "regimen": r["regimen"],
            "design_tier": r["design_tier"],
            "sourceId": r["sourceId"],
            "n_response_evaluable": n,
            "objective_response": r["orr_events"],
            "objective_response_pct": pct(r["orr_events"] / n),
            "stable_disease": r["sd_events"],
            "progressive_disease": r["pd_events"],
            "disease_control": r["dc_events"],
            "disease_control_pct": pct(r["dc_events"] / n),
            "gap_pct_points": round(100.0 * (r["dc_events"] - r["orr_events"]) / n, 1),
        }

    gap = round(pct(dc_ev / dc_dn) - pct(orr_ev / orr_dn), 1)

    return {
        "question": (
            "Read over the IDENTICAL patients, how far apart are objective response and disease "
            "control in advanced EMC?"),
        "patient_set": (
            "every advanced-EMC patient ever evaluated for response inside a prospective trial with "
            "protocol-defined assessment -- the three cohorts the source file pools, no more"),
        "n_patients": orr_dn,
        "n_cohorts": len(rows),
        "objective_response": {
            "events": orr_ev, "denom": orr_dn,
            "proportion_pct": pct(orr_ev / orr_dn),
            "wilson95_pct": [pct(orr_lo), pct(orr_hi)],
        },
        "disease_control": {
            "events": dc_ev, "denom": dc_dn,
            "proportion_pct": pct(dc_ev / dc_dn),
            "wilson95_pct": [pct(dc_lo), pct(dc_hi)],
        },
        "discordant_patients_stable_disease_only": {
            "events": sd_direct, "denom": orr_dn,
            "proportion_pct": pct(sd_direct / orr_dn),
            "wilson95_pct": [pct(sd_lo), pct(sd_hi)],
            "what_they_are": (
                "patients whose best response was stable disease. The objective-response endpoint "
                "counts every one of them as a non-responder; the disease-control endpoint counts "
                "every one of them as an event. They are the entire difference between the two "
                "readings and they are the majority of the evidence base."),
            "derived_two_ways_and_agree": {
                "sum_of_reported_stable_disease": sd_direct,
                "disease_control_minus_objective_response": sd_by_subtraction,
            },
        },
        "gap_pct_points": gap,
        "ratio_disease_control_to_objective_response": round((dc_ev / dc_dn) / (orr_ev / orr_dn), 1),
        "per_cohort": per,
        "sensitivity_immunosarc2_denominator_22": _sensitivity_22(rows, gap),
        "the_objection_that_this_cannot_answer": (
            "A gap this size is a fact about the two ENDPOINTS on one dataset. It is not evidence "
            "that any drug held any tumour still. EMC is indolent -- 5-year overall survival 66-88 "
            "per cent, 10-year disease-specific survival about 85 per cent -- so an unknown share of "
            "these 36 stable diseases would have been stable without treatment, and NONE of the "
            "three cohorts was randomised against no treatment. All three required documented "
            "progression before entry, which bounds the objection without settling it. The source "
            "file states the same limit in its own words at `where_the_evidence_is_too_thin` and "
            "`analyses.A4_disease_control.interpretation_limit`."),
    }


# ------------------------------------------------------------------------------------------------
# D2 -- how much of the observed signal is invisible to an objective-response reading
# ------------------------------------------------------------------------------------------------
def d2_invisible_share(d1):
    sd = d1["discordant_patients_stable_disease_only"]["events"]
    dc = d1["disease_control"]["events"]
    return {
        "question": (
            "Of everything these three trials recorded as disease control, what fraction is "
            "invisible to an objective-response readout?"),
        "disease_control_events": dc,
        "of_which_stable_disease_only": sd,
        "share_invisible_to_objective_response_pct": round(100.0 * sd / dc, 1),
        "reading": (
            "An objective-response endpoint sees %d of the %d recorded disease-control events. The "
            "other %d are discarded by construction, not by judgement -- the endpoint has no "
            "category for them." % (dc - sd, dc, sd)),
        "what_this_is_not": (
            "It is NOT a claim that the discarded fraction is drug effect. It is a measurement of "
            "how much of the recorded observation one endpoint cannot represent; whether that "
            "observation means anything is the separate, unresolved question in D1."),
    }


# ------------------------------------------------------------------------------------------------
# D3 -- a completeness census of the literature, not of the disease
# ------------------------------------------------------------------------------------------------
def d3_reporting_completeness(src, by_key):
    rows = src["cohorts"]
    ctx = src.get("context_only_no_extractable_counts", [])

    def has_orr(r):
        return r.get("orr_events") is not None and bool(r.get("orr_denom"))

    def has_dc(r):
        return r.get("dc_events") is not None and bool(r.get("orr_denom"))

    def has_emc_pfs(r):
        return r.get("median_pfs_months") is not None and bool(r.get("median_pfs_is_emc_specific"))

    orr_rows = [r["key"] for r in rows if has_orr(r)]
    dc_rows = [r["key"] for r in rows if has_dc(r)]
    pfs_rows = [r["key"] for r in rows if has_emc_pfs(r)]

    # The 6-month progression-free rate -- the primary endpoint BOTH modern EMC trials chose. The
    # source file's A6 establishes that exactly one cohort reports it as an integer count; that row
    # is read from A6 rather than re-decided here, and the count is checked against it.
    a6 = src["analyses"]["A6_six_month_progression_free"]
    six_month_rows = [a6["the_single_extractable_row"]["cohort"]]

    n_rows = len(rows) + len(ctx)

    def frac(keys):
        return {"n": len(keys), "of": n_rows, "pct": pct(len(keys) / n_rows), "cohorts": keys}

    return {
        "question": (
            "For how many published EMC systemic-therapy cohorts is each endpoint extractable as an "
            "integer count, under the repository's evidence contract?"),
        "why_this_is_the_interesting_census": (
            "Choosing a better endpoint is worth nothing if the literature does not report it. This "
            "counts REPORTING, not biology: a cohort is credited only where the source prints "
            "explicit integers, because POLICY-evidence 2.1 forbids reconstructing counts from a "
            "published percentage."),
        "denominator": {
            "cohort_rows_in_the_source_table": len(rows),
            "context_only_rows_with_no_extractable_counts": len(ctx),
            "total_rows_considered": n_rows,
            "what_the_denominator_is": (
                "every row of the source's systemic-therapy table, which is every published report "
                "this repository has found bearing on systemic therapy in advanced EMC. ONE of the "
                "cohort rows (immunosarc1_sts_cohort) is a mixed soft-tissue-sarcoma cohort with no "
                "EMC subgroup reported, so it contributes to no endpoint here -- it is counted in "
                "the denominator because 'reports nothing extractable for EMC' is precisely what "
                "this census measures, and dropping it would flatter every row above."),
        },
        "extractable": {
            "objective_response_counts": frac(orr_rows),
            "disease_control_counts": frac(dc_rows),
            "emc_specific_median_pfs": frac(pfs_rows),
            "six_month_progression_free_as_a_count": dict(
                frac(six_month_rows),
                source_of_this_row=SOURCE_REL + " -> analyses.A6_six_month_progression_free"),
        },
        "rows_that_cannot_enter_a_pool": {
            "no_objective_response_count": frac([r["key"] for r in rows if not has_orr(r)]
                                                + [c["key"] for c in ctx]),
            "no_disease_control_count": frac([r["key"] for r in rows if not has_dc(r)]
                                             + [c["key"] for c in ctx]),
            "neither": frac([r["key"] for r in rows if not has_orr(r) and not has_dc(r)]
                            + [c["key"] for c in ctx]),
            "reading": (
                "The disease-control pool is the one the reporting gap bites hardest, which is the "
                "wrong way round for a disease whose trials have moved toward progression-based "
                "endpoints."),
        },
        "the_finding": (
            "The endpoint the field's own trials have already migrated to is the one it reports "
            "least completely. Objective-response counts are extractable for %d of %d cohorts; "
            "6-month progression-free status for %d. An endpoint argument in this disease is "
            "therefore also a reporting-standard argument, and the second half is the one that "
            "costs nothing to fix." % (len(orr_rows), n_rows, len(six_month_rows))),
        "what_the_missing_rows_are_missing": {
            "drilon_chemotherapy": "best-response categories given only as percentages",
            "apatinib_emc_subset": "per-subtype breakdown gives responses but not stable disease",
            "chiusole_metastatic_chemo": (
                "disease-control RATES only, several of which do not convert to integers on their "
                "own stated denominators"),
            "immunosarc1_sts_cohort": "mixed-histology cohort; no EMC subgroup reported separately",
        },
    }


# ------------------------------------------------------------------------------------------------
# D4 -- what each event rate does to a trial this disease can actually accrue
# ------------------------------------------------------------------------------------------------
def _p_zero_events(p, n):
    return (1.0 - p) ** n


def _n_for_90pct_chance_of_one_event(p, cap=100000):
    if p <= 0:
        return None
    n = 1
    while _p_zero_events(p, n) > 0.10 and n < cap:
        n += 1
    return n


def d4_small_trial_arithmetic(d1):
    orr = d1["objective_response"]
    dc = d1["disease_control"]
    p_orr = orr["events"] / orr["denom"]
    p_dc = dc["events"] / dc["denom"]
    orr_lo = orr["wilson95_pct"][0] / 100.0
    orr_hi = orr["wilson95_pct"][1] / 100.0

    zero_table = []
    for n in TRIAL_SIZES:
        zero_table.append({
            "n": n,
            "p_zero_objective_responses_at_point_estimate": round(_p_zero_events(p_orr, n), 3),
            "p_zero_objective_responses_at_wilson_lower": round(_p_zero_events(orr_lo, n), 3),
            "p_zero_objective_responses_at_wilson_upper": round(_p_zero_events(orr_hi, n), 3),
            "expected_objective_responses": round(n * p_orr, 1),
            "expected_disease_control_events": round(n * p_dc, 1),
        })

    return {
        "question": (
            "What does each endpoint's event rate do to a single-arm trial of the size this disease "
            "can actually accrue?"),
        "assumptions_stated_because_they_are_the_whole_content": [
            "The only inputs are the two pooled proportions from D1 and the binomial distribution.",
            ("It assumes the pooled proportion is the true event rate, which is the assumption a "
             "trial designer makes when they power on a historical rate. It is stated, not hidden, "
             "and the Wilson bounds are carried through every row for exactly that reason."),
            ("It is NOT a power calculation for any specific design and it names no alternative "
             "hypothesis. It says what the arithmetic of a rare event does to a small denominator."),
        ],
        "point_estimates_used": {
            "objective_response": orr["proportion_pct"],
            "objective_response_wilson95_pct": orr["wilson95_pct"],
            "disease_control": dc["proportion_pct"],
            "disease_control_wilson95_pct": dc["wilson95_pct"],
        },
        "patients_per_single_event": {
            "objective_response": round(1.0 / p_orr, 1),
            "disease_control": round(1.0 / p_dc, 1),
        },
        "probability_a_trial_sees_no_objective_response_at_all": zero_table,
        "n_for_a_90pct_chance_of_at_least_one_objective_response": {
            "at_point_estimate": _n_for_90pct_chance_of_one_event(p_orr),
            "at_wilson_lower_bound": _n_for_90pct_chance_of_one_event(orr_lo),
            "at_wilson_upper_bound": _n_for_90pct_chance_of_one_event(orr_hi),
            "for_scale": (
                "the two modern prospective EMC cohorts enrolled 22 and 23 response-evaluable "
                "patients, which took a European multi-network trial 2014-2017 and 2020-2024 "
                "respectively"),
        },
        "the_asymmetry_that_matters": (
            "A rare-event endpoint and a common-event endpoint fail in OPPOSITE directions at this "
            "sample size, and both failures are real. Objective response is so rare that a trial of "
            "20 has a material chance of observing none at all, which is uninterpretable rather "
            "than negative. Disease control is so common that nearly every patient is an event, "
            "which leaves it with almost no room to distinguish a drug from an indolent natural "
            "history unless it is read against a comparator or a time anchor. Neither observation "
            "recommends a drug or a design; together they say the endpoint question in this disease "
            "is not 'which is better' but 'what does each one buy at n around 20'."),
    }


# ------------------------------------------------------------------------------------------------
# D5 -- a correction to the source file's own summary sentence, carried as a DETECTOR
# ------------------------------------------------------------------------------------------------
# `emc-systemic-therapy-pooling.json` -> findings_no_source_states asserts that "both modern trials
# chose 6-month PFS rather than response rate as their primary endpoint". Its OWN verbatim quote for
# the 2019 pazopanib trial says the opposite: that trial's primary endpoint WAS objective response.
# Both strings are already committed in that file, so this is a discrepancy between two committed
# fields rather than an outside claim, and it is detected here rather than retyped -- if the source
# is corrected the detector reports that instead, which is the only way a correction of this shape
# cannot rot. Retyping the finding would have made this file a second home for the error.
CLAIM_MARKER = "both modern trials chose 6-month PFS"
QUOTE_MARKERS = ("primary endpoint", "objective response")


def d5_primary_endpoint_correction(src):
    findings = src.get("findings_no_source_states", [])
    claim = next((f for f in findings if CLAIM_MARKER in f), None)
    pazo = next((c for c in src["cohorts"] if c["key"] == "pazopanib_phase2"), None)
    quote = (pazo or {}).get("quote", "")
    quote_supports_orr_primary = all(m in quote.lower() for m in QUOTE_MARKERS)

    if claim is None:
        return {
            "status": "source_appears_corrected",
            "detector": (
                "the sentence this record was written against is no longer present in "
                + SOURCE_REL + " -> findings_no_source_states"),
            "what_to_do": (
                "re-read that file's summary and confirm the correction landed, then this block "
                "can be retired"),
        }

    return {
        "status": "discrepancy_detected_in_the_source_file",
        "what_the_source_summary_says": claim,
        "what_the_source_own_quote_says": quote,
        "the_discrepancy": (
            "The 2019 pazopanib trial's primary endpoint was the RECIST objective-response rate, "
            "not 6-month progression-free survival -- the source file's own verbatim quote of that "
            "trial reads '22 patients ... were evaluable for the primary endpoint: four (18% "
            "[95% CI 1-36]) had a RECIST objective response'. So the two modern prospective EMC "
            "trials did NOT both choose a progression-free endpoint; they chose DIFFERENT ones, "
            "six years apart."),
        "quote_contains_both_markers": quote_supports_orr_primary,
        "why_it_strengthens_rather_than_weakens_the_endpoint_argument": (
            "A field that had already settled on a progression-free endpoint would need no endpoint "
            "argument. What the record actually shows is a MIGRATION between 2019 and 2025 that "
            "nobody wrote down: the 2019 trial's primary endpoint was objective response and the "
            "2025 cohort's was the 6-month progression-free rate (registration NCT03277924, whose "
            "record the source file retrieved at HTTP 200 and which states that primary endpoint). "
            "An undocumented migration is exactly the situation in which the older endpoint keeps "
            "being quoted as though it were the disease's verdict."),
        "correction_owed_to": SOURCE_REL + " -> findings_no_source_states",
        "this_file_does_not_fix_it": (
            "The correction belongs in the file that owns the sentence. This record exists so the "
            "discrepancy is visible and dated rather than silently inherited, per CLAUDE.md rule "
            "1.2 -- a correction goes in an appendix and the superseded wording stays quotable."),
    }


# ------------------------------------------------------------------------------------------------
# Parity with the source -- this file must not become a second home for A1/A4
# ------------------------------------------------------------------------------------------------
def parity(src, d1):
    a1 = src["analyses"]["A1_objective_response_prospective"]["pool"]
    a4 = src["analyses"]["A4_disease_control"]["pool"]
    checks = {
        "A1_cohort_membership": (sorted(a1["cohorts"]) == sorted(PROSPECTIVE)),
        "A4_cohort_membership": (sorted(a4["cohorts"]) == sorted(PROSPECTIVE)),
        "A1_events": a1["events"] == d1["objective_response"]["events"],
        "A1_denom": a1["denom"] == d1["objective_response"]["denom"],
        "A1_proportion": a1["proportion_pct"] == d1["objective_response"]["proportion_pct"],
        "A1_wilson": a1["wilson95_pct"] == d1["objective_response"]["wilson95_pct"],
        "A4_events": a4["events"] == d1["disease_control"]["events"],
        "A4_denom": a4["denom"] == d1["disease_control"]["denom"],
        "A4_proportion": a4["proportion_pct"] == d1["disease_control"]["proportion_pct"],
        "A4_wilson": a4["wilson95_pct"] == d1["disease_control"]["wilson95_pct"],
    }
    failed = [k for k, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "PARITY FAILED against %s: %s. This file re-derives A1/A4 only to prove it is talking "
            "about the same object; a disagreement means the source moved and the discordance "
            "figures must be regenerated, not reconciled by hand." % (SOURCE_REL, ", ".join(failed)))
    return {
        "checked_against": SOURCE_REL,
        "what_is_checked": (
            "the pooled objective-response and disease-control proportions and their Wilson "
            "intervals, re-derived here from the same cohort rows"),
        "why": (
            "One fact, one home. A1 and A4 belong to the source file. Re-deriving them here is a "
            "CHECK, not a second home -- if the two ever disagree this script refuses to write."),
        "all_checks": checks,
        "result": "agree",
    }


def build():
    src = load_source()
    by_key = cohort_map(src)
    d1 = d1_same_patients(by_key)
    return {
        "_schema": "emc-endpoint-discordance/1",
        "_generated_by": "research/manuscripts/emc_endpoint_discordance.py",
        "_generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_do_not_hand_edit": (
            "Regenerate with `python3 research/manuscripts/emc_endpoint_discordance.py`. Every "
            "number here is arithmetic over integer counts owned by " + SOURCE_REL + "; that file "
            "carries the quote and citation behind each one. Editing this file by hand would break "
            "the only link between the two."),
        "title": (
            "Objective response and disease control read over the same advanced-EMC patients: the "
            "size of the gap, what it cannot mean, and what each endpoint costs a small trial"),
        "method": {
            "policy": "systems/POLICY-evidence.md sections 2.1-2.4",
            "pooling": "crude denominator-weighted proportions",
            "interval": "Wilson score 95%",
            "counts": "explicit integers only; never back-derived from a published percentage",
            "populations": "non-overlapping only",
            "time_to_event": "never merged",
            "source_of_every_count": SOURCE_REL,
        },
        "parity_with_source": parity(src, d1),
        "D1_same_patients_two_endpoints": d1,
        "D2_share_invisible_to_objective_response": d2_invisible_share(d1),
        "D3_reporting_completeness": d3_reporting_completeness(src, by_key),
        "D4_small_trial_arithmetic": d4_small_trial_arithmetic(d1),
        "D5_primary_endpoint_correction": d5_primary_endpoint_correction(src),
        "not_a_recommendation": (
            "Nothing here endorses or discourages any therapy, ranks any agent, or asserts that any "
            "treatment is effective in EMC. It compares two ways of MEASURING, over observations "
            "that have already been published, and its central limitation is that the endpoint it "
            "finds larger is also the one with no comparator. EMC care belongs with a specialist "
            "sarcoma centre."),
    }


def _strip_volatile(obj):
    return {k: v for k, v in obj.items() if k != "_generated_utc"}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="re-derive and compare against the committed JSON; exit 1 on any drift")
    args = ap.parse_args()

    built = build()

    if args.check:
        if not os.path.exists(OUT):
            print("FAIL: %s does not exist" % OUT, file=sys.stderr)
            return 1
        with open(OUT, encoding="utf-8") as fh:
            committed = json.load(fh)
        if _strip_volatile(committed) != _strip_volatile(built):
            print("FAIL: %s differs from a fresh derivation. Regenerate it." % OUT, file=sys.stderr)
            return 1
        print("emc_endpoint_discordance --check: OK (committed artifact reproduces exactly)")
        return 0

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(built, fh, indent=1, ensure_ascii=True)
        fh.write("\n")
    d1 = built["D1_same_patients_two_endpoints"]
    print("wrote %s" % OUT)
    print("  n = %d patients, %d cohorts" % (d1["n_patients"], d1["n_cohorts"]))
    print("  objective response  %s%% (95%% CI %s-%s)" % (
        d1["objective_response"]["proportion_pct"], *d1["objective_response"]["wilson95_pct"]))
    print("  disease control     %s%% (95%% CI %s-%s)" % (
        d1["disease_control"]["proportion_pct"], *d1["disease_control"]["wilson95_pct"]))
    print("  discordant (SD)     %d of %d = %s%%" % (
        d1["discordant_patients_stable_disease_only"]["events"], d1["n_patients"],
        d1["discordant_patients_stable_disease_only"]["proportion_pct"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
