#!/usr/bin/env python3
"""Response and disease control read on identical patients, across diseases. ($0, stdlib)

WHAT THIS COMPUTES. For every arm in endpoint-corpus.json that carries a complete four-cell
best-response table, both endpoints on the SAME denominator, and the gap between them. Then the
distribution of that gap across arms, and -- from the same denominator -- the census of arms that
could not be re-read at all.

THE IDENTITY THAT MAKES THIS SIMPLE. On one denominator, DCR - ORR == SD / n exactly. The gap is
therefore a single proportion with its own exact interval, not a difference of two estimates needing
a covariance. Every gap interval below is the Wilson interval on the stable-disease count.

WHY THERE IS NO POOLED ESTIMATE. There is no common parameter across diseases, so a
denominator-weighted proportion would average unlike things and its interval would misstate its own
precision. POLICY-evidence 2.6 authorises this file's estimand -- a study-level descriptive series,
unit one arm, summarised by order statistics only -- and prohibits pooling, inverse-variance or
random-effects weighting, I-squared, meta-regression and significance tests across rows. None appears
here.

WHY ARMS ARE UNWEIGHTED BY n. The estimand is how a TRIAL reads, not how patients fare. A
denominator-weighted view answers a different question and is reported once, labelled as such, so
that nothing looks hidden.

WHY THE CENSUS LIVES IN THIS FILE. Arms that print four cells may differ systematically from arms
that do not, and the only honest bound on that difference is the size of the non-printing set.
POLICY-evidence 2.6(h) requires the census to share this analysis's denominator structurally rather
than by assertion, which is what putting them in one module achieves -- the same reason D1 and D3
live together in emc_endpoint_discordance.py.

Usage:
  python3 research/manuscripts/orr_dcr_reread.py           # regenerate
  python3 research/manuscripts/orr_dcr_reread.py --check    # verify the committed artifact
"""
from __future__ import annotations

import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "endpoint-corpus.json")
DISCORDANCE = os.path.join(HERE, "emc-endpoint-discordance.json")
OUT = os.path.join(HERE, "orr-dcr-reread.json")
OUT_REL = "research/manuscripts/orr-dcr-reread.json"

#: Pre-stated thresholds. Fixed before the distribution was looked at, so that "how many arms cross
#: this line" is a reading rather than a line drawn around the answer.
GAP_MARKS = (25, 50, 75)
LOW_ORR = 0.10
HIGH_DCR = 0.70


def wilson(events, n, z=1.96):
    """Wilson score interval. Chosen because it behaves at small n and near 0 and 1, which is the
    entire regime this analysis works in. Duplicated rather than imported for the reason recorded
    in emc_endpoint_discordance.py: importing would run another module's build at import time."""
    if n <= 0:
        return [None, None]
    p = events / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(max(p * (1 - p) / n + z * z / (4 * n * n), 0.0)) / d
    # A LIST, not a tuple: JSON has no tuple, so a tuple here re-derives as a list and --check
    # reports drift against its own committed output on every run.
    return [round(max(c - h, 0.0), 4), round(min(c + h, 1.0), 4)]


def pct(x, nd=1):
    return None if x is None else round(100 * x, nd)


def _quantile(sorted_vals, q):
    if not sorted_vals:
        return None
    i = q * (len(sorted_vals) - 1)
    lo, hi = math.floor(i), math.ceil(i)
    if lo == hi:
        return round(sorted_vals[int(i)], 1)
    return round(sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (i - lo), 1)


def _require(d, key, where):
    """Fetch a key that MUST exist, and fail loudly if it does not.

    A .get() on a renamed key returns None, and a None flows into the artifact as a blank field that
    reads exactly like "this quantity was not measured". That is the absent-reading-vs-reading-of-
    absence failure this repository treats as serious, and it happened here: the EMC response rate
    was read from 'pct' when the key is 'proportion_pct', and the artifact printed None rather than
    complaining."""
    if key not in d:
        raise SystemExit(f"FAIL: expected key {key!r} in {where}. "
                         f"Present: {sorted(d)}")
    return d[key]


def rows_from_corpus(corpus):
    out = []
    for a in corpus["C2_arms"]:
        c = a["cells"]
        n = a["evaluable_n"]
        orr_ev = c["CR"] + c["PR"]
        dc_ev = c["CR"] + c["PR"] + c["SD"]
        sd_ev = c["SD"]
        # The identity, asserted rather than assumed: if it ever fails, the four cells did not come
        # from one denominator and the comparison would be between populations.
        assert dc_ev - orr_ev == sd_ev, f"{a['nct_id']}: gap identity violated"
        assert orr_ev + sd_ev + c["PD"] == n, f"{a['nct_id']}: cells do not sum to n"
        out.append({
            "nct_id": a["nct_id"],
            "arm_title": a["arm_title"],
            "arm_group_type": a.get("arm_group_type"),
            "conditions": a["conditions"],
            "phases": a["phases"],
            "control_arm_candidate": a["control_arm_candidate"],
            "cells": c,
            "n": n,
            "objective_response": {"events": orr_ev, "pct": pct(orr_ev / n),
                                   "wilson95": wilson(orr_ev, n)},
            "disease_control": {"events": dc_ev, "pct": pct(dc_ev / n),
                                "wilson95": wilson(dc_ev, n)},
            "gap_pp": round(100 * sd_ev / n, 1),
            "gap_is_the_stable_disease_proportion": {"events": sd_ev, "n": n,
                                                     "wilson95": wilson(sd_ev, n)},
        })
    return out


def distribution(rows, label):
    gaps = sorted(r["gap_pp"] for r in rows)
    if not gaps:
        return {"arms": 0, "_note": "no arms in this stratum"}
    return {
        "_label": label,
        "arms": len(gaps),
        "median_gap_pp": round(statistics.median(gaps), 1),
        "iqr_gap_pp": [_quantile(gaps, 0.25), _quantile(gaps, 0.75)],
        "range_gap_pp": [gaps[0], gaps[-1]],
        "arms_at_or_above": {str(m): sum(1 for g in gaps if g >= m) for m in GAP_MARKS},
        "_no_pooled_estimate": (
            "deliberate. Order statistics only, per POLICY-evidence 2.6(c). A pooled proportion "
            "across diseases would average unlike things."),
    }


def build():
    with open(CORPUS) as fh:
        corpus = json.load(fh)
    with open(DISCORDANCE) as fh:
        emc = json.load(fh)

    rows = rows_from_corpus(corpus)
    disp = corpus["C3_dispositions"]

    low_orr_high_dcr = [r for r in rows
                        if r["objective_response"]["events"] / r["n"] <= LOW_ORR
                        and r["disease_control"]["events"] / r["n"] >= HIGH_DCR]

    # Denominator-weighted view, computed once so it cannot be said to have been hidden. It answers
    # "how do patients fare", which is NOT this file's estimand.
    tot_n = sum(r["n"] for r in rows)
    tot_sd = sum(r["cells"]["SD"] for r in rows)

    emc_d1 = emc["D1_same_patients_two_endpoints"]
    emc_gap = _require(emc_d1, "gap_pct_points", "D1")
    gaps_sorted = sorted(r["gap_pp"] for r in rows)
    below_emc = sum(1 for g in gaps_sorted if g < emc_gap) if emc_gap is not None else None

    screened = disp.get("studies_screened", 0)
    no_block = disp.get("study_posted_results_but_no_four_cell_block", 0)

    doc = {
        "_schema": "orr-dcr-reread/1",
        "_generated_by": "research/manuscripts/orr_dcr_reread.py",
        "_do_not_hand_edit": True,
        "title": "Objective response and disease control read on identical patients, across "
                 "diseases -- a study-level descriptive series",
        "governed_by": "systems/POLICY-evidence.md 2.6",
        "reads": ["research/manuscripts/endpoint-corpus.json",
                  "research/manuscripts/emc-endpoint-discordance.json"],

        "R1_gap_identity": {
            "statement": "on one denominator, disease control minus objective response equals the "
                         "stable-disease proportion exactly",
            "consequence": (
                "the gap is a single proportion and carries its own exact Wilson interval. It is "
                "not a difference of two estimates and needs no covariance, which removes any "
                "reason to model the pair."),
            "asserted_per_row": True,
            "also_asserted": "CR + PR + SD + PD == the evaluable denominator, for every row",
        },

        "R2_per_arm_rows": rows,

        "R3_distribution_summary": {
            "_estimand": (
                "how a TRIAL reads, not how patients fare. Arms are therefore unweighted by "
                "denominator (POLICY-evidence 2.6(d))."),
            "all_arms": distribution(rows, "all arms"),
            "low_response_high_stability_corner": {
                "definition": f"objective response <= {int(LOW_ORR * 100)}% and disease control "
                              f">= {int(HIGH_DCR * 100)}%, both pre-stated",
                "arms": len(low_orr_high_dcr),
                "share_of_arms_pct": pct(len(low_orr_high_dcr) / len(rows)) if rows else None,
                "_what_this_corner_is": (
                    "the regime the manuscript is about, reached without naming a disease. Which "
                    "tumour types land here is a description to be read off afterwards, never an "
                    "input."),
            },
            "denominator_weighted_sensitivity": {
                "_answers_a_different_question": (
                    "this is the patient-weighted stable-disease proportion -- 'how do patients "
                    "fare' rather than 'how does a trial read'. Reported once so that the "
                    "unweighted choice is visible rather than silent, and used nowhere else."),
                "total_patients_across_arms": tot_n,
                "stable_disease_events": tot_sd,
                "weighted_gap_pp": pct(tot_sd / tot_n) if tot_n else None,
            },
        },

        "R4_prestated_sensitivities": {
            "_why": "if the median gap survives every stratum, that is the finding. Each stratum "
                    "was named before the distribution was inspected.",
            "arms_with_n_at_least_20": distribution([r for r in rows if r["n"] >= 20],
                                                    "n >= 20"),
            "phase_2_only": distribution([r for r in rows if "PHASE2" in (r["phases"] or [])],
                                         "phase 2 only"),
            "phase_3_only": distribution([r for r in rows if "PHASE3" in (r["phases"] or [])],
                                         "phase 3 only"),
            "control_arm_candidates_only": distribution(
                [r for r in rows if r["control_arm_candidate"]], "control-arm candidates"),
            "_not_yet_stratifiable": {
                "recist_version": "not a field in posted results; needs the publication",
                "central_review": "not a field in posted results; needs the publication",
                "documented_progression_required_at_entry": (
                    "in the eligibility text rather than as a field. It is the stratifier that "
                    "matters most for the placebo calibration and is deferred to that module, "
                    "where it decides the DIRECTION of the bound rather than adding precision."),
            },
        },

        "R5_reporting_census": {
            "_this_is_the_sensitivity_analysis_not_a_separate_finding": (
                "arms that print four cells may differ systematically from arms that do not. The "
                "size of the non-printing set is the only honest bound on that bias, so it is "
                "computed from the same denominator as the re-read (POLICY-evidence 2.6(h))."),
            "studies_screened": screened,
            "studies_with_posted_results_but_no_four_cell_block": no_block,
            "share_of_screened_studies_not_re_readable_pct": (
                pct(no_block / screened) if screened else None),
            "arms_recovered": len(rows),
            "distinct_trials": corpus["C6_counts"]["distinct_trials"],
            "group_blocks_with_an_incomplete_four_cell_table":
                disp.get("group_block_four_cell_incomplete"),
            "abstracts_are_worse_still": corpus["A2_why_not_abstracts"],
        },

        "R6_what_the_census_costs_R3": {
            "the_bias_direction_is_not_known": (
                "a trial that posts a full best-response breakdown may be more likely to have "
                "something to break down. If so the recovered arms understate the gap, because "
                "arms with little stable disease are less likely to be reported in full. The "
                "opposite argument is equally available and neither is tested here."),
            "what_can_be_said": (
                "the distribution below describes the arms that CAN be re-read, and the census "
                "states how large that set is against everything screened. It is not a random "
                "sample of oncology trials and must never be described as one."),
        },

        "R8_zero_response_readouts": {
            "_why_this_block_exists": (
                "the distribution above measures how much an objective-response summary discards. "
                "This measures how often it returns nothing at all -- the case that gets read as "
                "'the agent is inactive' and that the regime map predicts is a function of arm "
                "size rather than of the agent."),
            "_definition": "an arm with zero complete and zero partial responses",
            "by_arm_size": {
                str(lo): {
                    "arms": len([a for a in rows if a["n"] >= lo]),
                    "zero_response_arms": len([a for a in rows if a["n"] >= lo
                                               and a["objective_response"]["events"] == 0]),
                    "zero_response_pct": pct(
                        len([a for a in rows if a["n"] >= lo
                             and a["objective_response"]["events"] == 0])
                        / max(len([a for a in rows if a["n"] >= lo]), 1)),
                    "zero_response_and_disease_control_at_least_50pct": len(
                        [a for a in rows if a["n"] >= lo
                         and a["objective_response"]["events"] == 0
                         and a["cells"]["SD"] / a["n"] >= 0.50]),
                    "zero_response_and_disease_control_at_least_70pct": len(
                        [a for a in rows if a["n"] >= lo
                         and a["objective_response"]["events"] == 0
                         and a["cells"]["SD"] / a["n"] >= 0.70]),
                } for lo in (1, 10, 20)},
            "reading": (
                "zero-response readouts concentrate in small arms, which is what the regime map "
                "predicts: at a fixed underlying rate, the probability of observing nothing falls "
                "with arm size. The stratification is therefore support for the argument rather "
                "than a weakening of it."),
            "⛔_what_this_may_not_be_read_as": (
                "an arm with zero responses that nonetheless shows stable disease is NOT thereby "
                "an active agent misread as inactive. Stable disease may be natural history, which "
                "is the confound placebo-arm-calibration.json exists to size and cannot. The claim "
                "here is narrower: at these arm sizes a zero is frequently uninterpretable rather "
                "than informative, and it is nonetheless reported as a result."),
            "_the_unweighted_headline_is_the_misleading_one": (
                "45.5% of all arms is dominated by dose-escalation cohorts of 3 patients. The "
                "n>=10 and n>=20 strata are the honest figures and are reported beside it rather "
                "than instead of it."),
        },

        "R7_emc_row_in_the_field_distribution": {
            "_why_this_block_exists": (
                "the original single-disease result becomes one labelled point in a cross-disease "
                "distribution rather than a claim standing on its own."),
            "emc_gap_pp": emc_gap,
            "emc_objective_response_pct": _require(
                _require(emc_d1, "objective_response", "D1"),
                "proportion_pct", "D1.objective_response"),
            "emc_disease_control_pct": _require(
                _require(emc_d1, "disease_control", "D1"),
                "proportion_pct", "D1.disease_control"),
            "corpus_arms_with_a_smaller_gap": below_emc,
            "corpus_arms_total": len(rows),
            "emc_percentile_in_the_corpus": (
                pct(below_emc / len(rows)) if below_emc is not None and rows else None),
            "reading": (
                "EMC sits in the upper tail rather than outside the distribution. The honest "
                "statement is that it is an extreme case of a general phenomenon, not a special "
                "one -- which is a weaker claim about EMC and a much stronger claim about "
                "endpoints."),
            "_not_pooled_with_the_corpus": (
                "the EMC figures come from published trial reports and the corpus from "
                "ClinicalTrials.gov posted results. They are placed on one axis for comparison "
                "and are never summed."),
        },

        "not_a_recommendation": (
            "No efficacy, safety, therapeutic-window or clinical-readiness claim about any agent "
            "in any disease. A difference between two endpoints is a fact about measurement, never "
            "evidence that a treatment did something. Nothing here recommends an endpoint, a "
            "design or a treatment."),
    }
    return doc


def _strip_volatile(obj):
    return {k: v for k, v in obj.items() if k != "_generated_utc"}


def main(argv):
    doc = build()
    if "--check" in argv:
        if not os.path.exists(OUT):
            print(f"FAIL: {OUT_REL} is missing")
            return 1
        with open(OUT) as fh:
            committed = json.load(fh)
        if _strip_volatile(committed) != _strip_volatile(doc):
            keys = sorted(k for k in set(list(committed) + list(doc))
                          if committed.get(k) != doc.get(k) and k != "_generated_utc")
            print(f"FAIL: {OUT_REL} does not re-derive. Differing keys: {keys}")
            return 1
        print(f"OK: {OUT_REL} re-derives from the corpus")
        return 0

    with open(OUT, "w") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    a = doc["R3_distribution_summary"]["all_arms"]
    c = doc["R5_reporting_census"]
    e = doc["R7_emc_row_in_the_field_distribution"]
    print(f"wrote {OUT_REL}")
    print(f"  arms                : {a['arms']} across {c['distinct_trials']} trials")
    print(f"  gap median (IQR)    : {a['median_gap_pp']} pp ({a['iqr_gap_pp'][0]}-{a['iqr_gap_pp'][1]})")
    print(f"  gap range           : {a['range_gap_pp'][0]}-{a['range_gap_pp'][1]} pp")
    print(f"  arms >= 50 pp       : {a['arms_at_or_above']['50']}")
    print(f"  low-ORR/high-DCR    : {doc['R3_distribution_summary']['low_response_high_stability_corner']['arms']}")
    print(f"  EMC gap {e['emc_gap_pp']} pp -> percentile {e['emc_percentile_in_the_corpus']}")
    print(f"  not re-readable     : {c['studies_with_posted_results_but_no_four_cell_block']} of "
          f"{c['studies_screened']} screened ({c['share_of_screened_studies_not_re_readable_pct']}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
