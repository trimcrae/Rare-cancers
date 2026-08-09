#!/usr/bin/env python3
"""The two-axis regime map -- where a response-rate readout stops carrying information. ($0, stdlib)

THE INSTRUMENT. A response-rate endpoint fails in a regime fixed by two numbers: the plausible
objective-response rate, and the sample size a disease can actually accrue. Neither is a property of
any particular tumour. This file computes the regime from those two axes and then places diseases on
it, so that "which diseases are in trouble" is a READING rather than an assumption.

WHY THE BOUNDARY IS COMPUTED AND NOT DRAWN. Both contours are level sets of the binomial:

  ZERO-EVENT CONTOUR   the smallest n at which a true rate p gives at least a 90% chance of one
                       response. Below it, a trial that sees nothing has learned nothing -- a null
                       result there is uninterpretable rather than negative.
  DESIGN CONTOUR       the n an exact single-stage single-arm design needs to distinguish p from a
                       null of 0.05 at alpha 0.05, power 0.80. The 0.05 null is not invented here:
                       it is the null the 2019 pazopanib EMC stratum registered, recorded in
                       emc-endpoint-alternatives.json -> E1_design_ledger.

Because the boundary is a level set of a distribution over the two axes, no box was drawn around any
disease, and a reviewer can re-derive it without trusting a judgement.

WHAT PLACES A DISEASE. Its own measured numbers and nothing else: response rate from the arms in
endpoint-corpus.json, accrual from ClinicalTrials.gov ACTUAL enrolment. Never anticipated enrolment
-- a trial's hoped-for size is exactly what this axis is testing.

WHAT THIS FILE MAY NOT BE USED FOR. It says nothing about whether any treatment works. A disease
inside the uninformative regime is one whose trials cannot be summarised by a response rate; that is
a statement about measurement.

Usage:
  python3 research/manuscripts/endpoint_regime_map.py           # regenerate
  python3 research/manuscripts/endpoint_regime_map.py --check   # verify the committed artifact
"""
from __future__ import annotations

import collections
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from emc_endpoint_alternatives import binom_sf, single_stage_design  # noqa: E402

CORPUS = os.path.join(HERE, "endpoint-corpus.json")
DISCORDANCE = os.path.join(HERE, "emc-endpoint-discordance.json")
OUT = os.path.join(HERE, "endpoint-regime-map.json")
OUT_REL = "research/manuscripts/endpoint-regime-map.json"

#: The null a single-arm oncology phase 2 conventionally tests against, and the one the 2019
#: pazopanib EMC stratum registered. Sourced rather than chosen here.
DESIGN_NULL = 0.05
DESIGN_ALPHA = 0.05
DESIGN_POWER = 0.80
#: Bound on the design search. A rate close to the null needs an enormous single-arm trial, and the
#: honest report of that is "no single-stage design exists at n <= this bound" -- a finding about
#: the disease, not a limit of the solver. It also keeps the search cheap: an unbounded scan spends
#: minutes on big-integer binomials to reach the same conclusion.
DESIGN_N_MAX = 200
ZERO_EVENT_TOLERANCE = 0.10

GRID_P = [0.02, 0.03, 0.05, 0.075, 0.10, 0.125, 0.15, 0.20, 0.25, 0.30, 0.40]
GRID_N = [10, 15, 20, 25, 30, 40, 50, 75, 100]

#: A disease coordinate needs enough of both axes to mean anything. Stated before the data was
#: grouped, so the threshold is not a filter chosen to produce a tidy map.
MIN_ARMS = 3
MIN_ACCRUAL_RECORDS = 3


def p_zero_events(p, n):
    return round((1.0 - p) ** n, 4)


def n_for_90pct_chance_of_one_event(p, cap=100000):
    """Smallest n with P(0 events) <= 0.10. Closed form, guarded for p at the boundaries."""
    if p <= 0:
        return None
    if p >= 1:
        return 1
    n = math.ceil(math.log(ZERO_EVENT_TOLERANCE) / math.log(1.0 - p))
    return int(min(max(n, 1), cap))


NO_DESIGN = "NO_DESIGN_WITHIN_BOUND"
_DESIGN_CACHE = {}


def required_n_against_null(p):
    """n an exact single-stage design needs to tell p from DESIGN_NULL.

    None when p is at or below the null (nothing to detect). NO_DESIGN when none exists at
    n <= DESIGN_N_MAX, which is the interesting case rather than an error: the response rate is
    too close to "not worth pursuing" for any single-arm trial of realistic size to separate them."""
    if p <= DESIGN_NULL:
        return None
    key = round(p, 4)
    if key not in _DESIGN_CACHE:
        d = single_stage_design(DESIGN_NULL, p, DESIGN_ALPHA, 1 - DESIGN_POWER, n_max=DESIGN_N_MAX)
        _DESIGN_CACHE[key] = d.get("n") if d else NO_DESIGN
    return _DESIGN_CACHE[key]


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


def _median_int(vals):
    return int(statistics.median(vals)) if vals else None


def build():
    with open(CORPUS) as fh:
        corpus = json.load(fh)
    with open(DISCORDANCE) as fh:
        emc = json.load(fh)

    # ---- axis 1: response rate, per condition, from the corpus's own arms ------------------
    orr_by_cond = collections.defaultdict(list)
    orr_by_cond_p23 = collections.defaultdict(list)
    phase_by_cond = collections.defaultdict(collections.Counter)
    for a in corpus["C2_arms"]:
        n = a["evaluable_n"]
        orr = (a["cells"]["CR"] + a["cells"]["PR"]) / n
        phases = set(a["phases"] or [])
        for c in a["conditions"]:
            orr_by_cond[c].append(orr)
            for ph in (a["phases"] or ["NONE"]):
                phase_by_cond[c][ph] += 1
            if phases & {"PHASE2", "PHASE3"}:
                orr_by_cond_p23[c].append(orr)

    # ---- axis 2: accrual, per condition, ACTUAL enrolment only ----------------------------
    acc_by_cond = collections.defaultdict(list)
    stopped_by_cond = collections.Counter()
    for r in corpus["C7_accrual_records"]:
        e = r.get("actual_enrollment")
        if e is None:
            continue
        for c in r["conditions"]:
            acc_by_cond[c].append(e)
            if r.get("why_stopped"):
                stopped_by_cond[c] += 1

    coords, insufficient = [], []
    for cond in sorted(set(orr_by_cond) | set(acc_by_cond)):
        orrs, accs = orr_by_cond.get(cond, []), acc_by_cond.get(cond, [])
        if len(orrs) < MIN_ARMS or len(accs) < MIN_ACCRUAL_RECORDS:
            insufficient.append({"condition": cond, "arms": len(orrs),
                                 "accrual_records": len(accs)})
            continue
        p = statistics.median(orrs)
        n_med = _median_int(accs)
        need_zero = n_for_90pct_chance_of_one_event(p)
        need_design = required_n_against_null(p)
        coords.append({
            "condition": cond,
            "arms": len(orrs),
            "median_objective_response_pct": round(100 * p, 1),
            "accrual_records": len(accs),
            "median_actual_enrolment": n_med,
            "max_actual_enrolment": max(accs),
            "trials_stopped_with_a_reason_recorded": stopped_by_cond.get(cond, 0),
            "n_needed_for_90pct_chance_of_one_response": need_zero,
            "n_needed_for_a_single_stage_design_vs_null_5pct": need_design,
            "median_trial_is_below_the_zero_event_contour": (
                None if need_zero is None or n_med is None else n_med < need_zero),
            "median_trial_is_below_the_design_contour": (
                None if need_design is None or n_med is None
                else True if need_design == NO_DESIGN
                else n_med < need_design),
            "p_zero_responses_at_the_median_trial_size": (
                None if n_med is None else p_zero_events(p, n_med)),
            "phase_mix_of_the_contributing_arms": dict(phase_by_cond.get(cond, {})),
            "median_objective_response_pct_phase_2_3_arms_only": (
                round(100 * statistics.median(orr_by_cond_p23[cond]), 1)
                if orr_by_cond_p23.get(cond) else None),
            "phase_2_3_arms": len(orr_by_cond_p23.get(cond, [])),
        })

    # ⛔ THREE CATEGORIES, NOT TWO, AND THE THIRD IS THE EXTREME ONE (corrected 2026-08-09).
    # required_n_against_null() returns None when the median response rate is at or below the 5%
    # null -- "nothing to detect". Those conditions were then counted in the DENOMINATOR of
    # "share below the design contour" while never being able to appear in its numerator, so 16 of
    # 44 conditions diluted the headline. Every one of them has a median objective response of 0.0%
    # or 4.2%: a condition where the typical trial observes no responses at all is the STRONGEST
    # instance of this paper's thesis, and it was being reported as though it were unaffected.
    # The share is now taken over conditions where the comparison is defined, and the undefined
    # group is reported separately rather than hidden in a denominator.
    below_zero = [c for c in coords if c["median_trial_is_below_the_zero_event_contour"] is True]
    below_design = [c for c in coords if c["median_trial_is_below_the_design_contour"] is True]
    design_defined = [c for c in coords
                      if c["median_trial_is_below_the_design_contour"] is not None]
    zero_defined = [c for c in coords
                    if c["median_trial_is_below_the_zero_event_contour"] is not None]
    at_or_below_the_null = [c for c in coords
                            if c["median_objective_response_pct"] <= 100 * DESIGN_NULL]
    coords_sorted = sorted(coords, key=lambda c: c["median_objective_response_pct"])

    emc_d1 = emc["D1_same_patients_two_endpoints"]
    emc_p = _require(_require(emc_d1, "objective_response", "D1"),
                     "proportion_pct", "D1.objective_response")
    emc_pf = emc_p / 100.0 if emc_p is not None else None

    doc = {
        "_schema": "endpoint-regime-map/1",
        "_generated_by": "research/manuscripts/endpoint_regime_map.py",
        "_do_not_hand_edit": True,
        "title": "The regime in which a response-rate readout stops carrying information",
        "governed_by": "systems/POLICY-evidence.md 2.6",
        "reads": ["research/manuscripts/endpoint-corpus.json",
                  "research/manuscripts/emc-endpoint-discordance.json"],

        "G1_axis_definitions": {
            "axis_1_response_rate": (
                "the median objective-response proportion across the arms this corpus holds for a "
                "condition. Order statistic, not a pooled estimate -- POLICY-evidence 2.6(c)."),
            "axis_2_accruable_n": (
                "the median ACTUAL enrolment of ClinicalTrials.gov interventional trials in that "
                "condition. Anticipated enrolment is never used: what a trial hoped to accrue is "
                "the very thing this axis tests."),
            "why_two_axes_and_not_a_disease_list": (
                "the failure is a property of a coordinate, not of a tumour. Diseases are placed "
                "on the map by their own measured numbers, so which of them land in trouble is a "
                "reading rather than a premise."),
        },

        "G2_contours": {
            "zero_event_contour": {
                "definition": "smallest n at which a true rate p gives at least a 90% chance of "
                              "at least one response",
                "tolerance": ZERO_EVENT_TOLERANCE,
                "why_it_matters": (
                    "below this line a trial that observes no responses has not shown the agent "
                    "inactive. It has produced an uninterpretable result that is nonetheless read "
                    "as negative, and a futility rule keyed to it would stop an active agent."),
            },
            "design_contour": {
                "definition": f"n an exact single-stage single-arm design needs to distinguish p "
                              f"from a null of {DESIGN_NULL} at alpha {DESIGN_ALPHA} and power "
                              f"{DESIGN_POWER}",
                "null_is_sourced_not_chosen": (
                    "0.05 is the null the 2019 pazopanib EMC stratum registered, recorded in "
                    "emc-endpoint-alternatives.json -> E1_design_ledger. It is the conventional "
                    "'not worth pursuing' null for a single-arm oncology phase 2."),
            },
            "grid": [
                {"objective_response_pct": round(100 * p, 1),
                 "n_for_90pct_chance_of_one_response": n_for_90pct_chance_of_one_event(p),
                 "n_for_a_single_stage_design": required_n_against_null(p),
                 "p_zero_responses_by_n": {str(n): p_zero_events(p, n) for n in GRID_N}}
                for p in GRID_P],
            "_the_boundary_is_a_level_set": (
                "both contours are level sets of the binomial over the two axes. Nothing here is "
                "drawn around a disease, and the whole map re-derives from first principles."),
        },

        "G3_disease_coordinates": {
            "_inclusion": f"a condition is placed only if it has at least {MIN_ARMS} arms and "
                          f"{MIN_ACCRUAL_RECORDS} accrual records. Stated before grouping.",
            "conditions_placed": len(coords),
            "conditions_with_insufficient_data": len(insufficient),
            "coordinates": coords_sorted,
        },

        "G4_what_the_map_reads": {
            "conditions_placed": len(coords),
            "conditions_at_or_below_the_null_so_no_design_is_defined": len(at_or_below_the_null),
            "_what_that_group_is": (
                "a condition whose median objective response is at or below the 5% null the design "
                "contour tests against. No single-stage design can separate that rate from 'not "
                "worth pursuing', so the contour is undefined -- not because the condition is "
                "unaffected, but because it is past the point the contour was built to measure. "
                "Every one of these has a median objective response of 0.0% except one at 4.2%."),
            "conditions_where_the_design_comparison_is_defined": len(design_defined),
            "conditions_whose_median_trial_is_below_the_design_contour": len(below_design),
            "share_below_the_design_contour_pct": (
                round(100 * len(below_design) / len(design_defined), 1) if design_defined else None),
            "_share_denominator": (
                "conditions where the comparison is defined, NOT all conditions placed. Using all "
                "conditions placed puts 16 undefined rows in a denominator they can never enter the "
                "numerator of, which understates the finding."),
            "conditions_where_the_zero_event_comparison_is_defined": len(zero_defined),
            "conditions_whose_median_trial_is_below_the_zero_event_contour": len(below_zero),
            "share_below_the_zero_event_contour_pct": (
                round(100 * len(below_zero) / len(zero_defined), 1) if zero_defined else None),
            "conditions_that_cannot_support_a_response_endpoint_at_all": (
                len(below_design) + len(at_or_below_the_null)),
            "_that_last_figure": (
                "conditions below the design contour PLUS conditions past the null entirely. It is "
                "the count of conditions in which a response-rate summary cannot do the job asked "
                "of it, by either route."),
            "named_below_the_zero_event_contour": [c["condition"] for c in below_zero],
            "reading": (
                "a condition below the design contour cannot accrue, at its median trial size, "
                "the trial its own response rate would require. A condition below the zero-event "
                "contour is one where a typical trial has better than a one-in-ten chance of "
                "seeing no responses at all even when the agent works at the rate observed."),
        },

        "G5_emc_as_the_worked_extreme": {
            "objective_response_pct": emc_p,
            "n_needed_for_90pct_chance_of_one_response": (
                n_for_90pct_chance_of_one_event(emc_pf) if emc_pf else None),
            "n_needed_for_a_single_stage_design_vs_null_5pct": (
                required_n_against_null(emc_pf) if emc_pf else None),
            "what_emc_actually_accrued": (
                "22 and 23 response-evaluable patients, in the two modern prospective cohorts, "
                "across 2014-2017 and 2020-2024 respectively -- owned by "
                "emc-endpoint-discordance.json, not re-derived here."),
            "_why_it_is_the_worked_case_and_not_the_subject": (
                "EMC is placed by the same two measurements as every other condition. It is an "
                "extreme coordinate, not a separate argument."),
        },

        "G6_the_phase_composition_sensitivity": {
            "_the_objection": (
                "conditions at the bottom of the response axis include broad registry strings -- "
                "Advanced Solid Tumors, Metastatic Cancer, Solid Tumor -- that collect "
                "dose-escalation arms, where a response rate of zero is expected from the trial "
                "phase rather than from the disease. If that were the whole story the low corner "
                "would be an artefact of how ClinicalTrials.gov names conditions."),
            "_the_composition_difference_is_real": (
                "arms contributing to conditions at or below the null are phase-1 heavy (197 "
                "phase 1 against 147 phase 2 and 9 phase 3), where the remaining placed conditions "
                "are phase-2 heavy (133 phase 2, 96 phase 1, 37 phase 3). So the corpus IS "
                "composed differently at the bottom of the axis, and any claim that condition "
                "strings coarsen the map without biasing it is false."),
            "_but_the_finding_survives_the_restriction": (
                "recomputing the response axis on phase 2 and phase 3 arms only leaves the median "
                "at 0.0% for twelve of the fourteen conditions that have any phase 2/3 arm. Two "
                "have none at all. One, Solid Tumors, rises to 21.4%. The low corner is therefore "
                "not an artefact of dose escalation, and the sensitivity is reported because the "
                "objection is a good one rather than because it succeeds."),
            "per_condition": [
                {"condition": c["condition"],
                 "median_all_arms_pct": c["median_objective_response_pct"],
                 "median_phase_2_3_only_pct": c["median_objective_response_pct_phase_2_3_arms_only"],
                 "phase_2_3_arms": c["phase_2_3_arms"]}
                for c in coords_sorted],
        },

        "G7_what_this_map_does_not_say": {
            "not_about_efficacy": (
                "no statement that any treatment works, does not work, or is safe, in any disease "
                "on the map."),
            "median_hides_spread": (
                "a condition is placed by two medians. Trials within a condition vary widely, and "
                "a median coordinate is a summary of a heterogeneous set, not a description of any "
                "particular trial."),
            "condition_strings_are_the_registry_s_and_they_DO_bias": (
                "conditions are ClinicalTrials.gov strings, so one disease can appear under "
                "several spellings and a broad string can absorb several diseases. ⚠ SUPERSEDED, "
                "RETAINED: this field previously read 'This coarsens the map; it does not bias it "
                "toward any coordinate.' That was false and was corrected on 2026-08-09. The broad "
                "strings collect dose-escalation arms and sit disproportionately at the bottom of "
                "the response axis, so the coarsening is directional and points toward this "
                "paper's own conclusion. G6 measures the difference and tests whether the finding "
                "survives it."),
            "the_corpus_is_not_a_random_sample": (
                "only arms that posted a complete four-cell table are here -- 552 of the arms "
                "belonging to 4414 screened studies. orr-dcr-reread.json -> R6 states the bias "
                "argument in both directions and settles neither."),
            "accrual_is_a_ceiling_not_a_target": (
                "actual enrolment records what trials achieved under their own eligibility and "
                "funding, not what a disease could in principle accrue under a better design."),
        },

        "not_a_recommendation": (
            "Nothing here recommends an endpoint, a design, or a treatment for any disease. It "
            "computes where a response-rate summary carries information and where it does not."),
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
        print(f"OK: {OUT_REL} re-derives")
        return 0

    with open(OUT, "w") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    g = doc["G4_what_the_map_reads"]
    e = doc["G5_emc_as_the_worked_extreme"]
    print(f"wrote {OUT_REL}")
    print(f"  conditions placed                    : {g['conditions_placed']}")
    print(f"  below the design contour             : "
          f"{g['conditions_whose_median_trial_is_below_the_design_contour']} "
          f"({g['share_below_the_design_contour_pct']}%)")
    print(f"  below the zero-event contour         : "
          f"{g['conditions_whose_median_trial_is_below_the_zero_event_contour']}")
    print(f"  EMC: ORR {e['objective_response_pct']}% needs n="
          f"{e['n_needed_for_90pct_chance_of_one_response']} for one response, "
          f"n={e['n_needed_for_a_single_stage_design_vs_null_5pct']} to design against a 5% null")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
