#!/usr/bin/env python3
"""What happens on no active treatment -- sizing the natural-history confound. ($0, stdlib)

THE QUESTION. A disease-control rate counts stable disease as an event, and stable disease is only
evidence of activity if the disease would otherwise have progressed. The EMC paper concedes it
cannot size that confound and that no untreated EMC progression rate exists. That concession is true
of EMC and false of oncology: randomised trials with a control arm have measured it. This file
collects what those arms actually show.

THE DISTINCTION THAT DECIDES WHETHER THIS IS HONEST. A "placebo arm" is usually not an untreated
arm. Most placebo arms in oncology sit on top of an active backbone -- placebo PLUS chemotherapy,
placebo PLUS an antibody -- and their outcomes measure the backbone, not natural history. An arm is
usable for calibration only if the patients received no active anti-tumour agent. Every candidate is
therefore classified, and a backboned arm is retained as CONTEXT and excluded from the calibration
rather than quietly averaged in.

THE SECOND DISTINCTION, WHICH SETS THE DIRECTION OF THE BOUND. An arm enrolled on documented
progression gives a LOWER bound on natural-history stability; an unselected or observation cohort
gives an UPPER bound, because it is selected for expected indolence. The two are never summarised
together. Whether a trial required documented progression is in its eligibility prose rather than in
a posted-results field, so for corpus arms this is recorded as CANNOT_DETERMINE -- an absent reading,
never a reading of absence.

Usage:
  python3 research/manuscripts/placebo_arm_calibration.py           # regenerate
  python3 research/manuscripts/placebo_arm_calibration.py --check   # verify the committed artifact
"""
from __future__ import annotations

import json
import math
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "endpoint-corpus.json")
ALTERNATIVES = os.path.join(HERE, "emc-endpoint-alternatives.json")
REGIME = os.path.join(HERE, "endpoint-regime-map.json")
OUT = os.path.join(HERE, "placebo-arm-calibration.json")
OUT_REL = "research/manuscripts/placebo-arm-calibration.json"

#: An arm title naming an active anti-tumour agent alongside the control token is BACKBONED. The
#: list is deliberately broad: a false BACKBONED call costs one arm of calibration, a false
#: UNTREATED call puts a treated arm into a natural-history estimate, which is the error that would
#: invalidate the analysis.
BACKBONE = re.compile(
    r"\b(chemotherap|cisplatin|carboplatin|cis\b|carb\b|docetaxel|paclitaxel|pemetrexed|"
    r"gemcitabine|doxorubicin|etoposide|irinotecan|oxaliplatin|fluorouracil|capecitabine|"
    r"temozolomide|dacarbazine|cyclophosphamide|bortezomib|lenalidomide|dexamethasone|"
    r"pembrolizumab|nivolumab|atezolizumab|durvalumab|avelumab|ipilimumab|rituximab|"
    r"trastuzumab|bevacizumab|cetuximab|physician.?s? choice|standard of care|SOC\b|"
    r"radiotherap|chemoradi|\+\s*\w)", re.I)

CONTROL_TOKEN = re.compile(
    r"\b(placebo|best supportive care|BSC|observation|no (treatment|intervention)|"
    r"watchful waiting|surveillance)\b", re.I)

#: The field set an arm needs before it can carry a natural-history reading. Fields marked required
#: are the ones whose absence makes the number uninterpretable rather than merely imprecise.
REQUIRED_FIELDS = [
    "arm_type (placebo / BSC / observation)",
    "background_therapy_verbatim",
    "evaluable_n",
    "CR, PR, SD, PD as integers",
    "response_criterion_and_version",
    "imaging_interval_weeks",
    "assessment (investigator or blinded independent central review)",
    "progression_required_at_entry (yes / no / unstated)",
    "crossover_permitted",
    "figure_is_pre_crossover",
    "verbatim_quote",
    "retrieved_file",
]


def wilson(events, n, z=1.96):
    if n <= 0:
        return [None, None]
    p = events / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(max(p * (1 - p) / n + z * z / (4 * n * n), 0.0)) / d
    return [round(max(c - h, 0.0), 4), round(min(c + h, 1.0), 4)]


def pct(x, nd=1):
    return None if x is None else round(100 * x, nd)


def classify(arm):
    title = arm.get("arm_title") or ""
    gtype = arm.get("arm_group_type")
    if not (CONTROL_TOKEN.search(title) or gtype in ("PLACEBO_COMPARATOR", "NO_INTERVENTION")):
        return "not_a_control_arm"
    if BACKBONE.search(title):
        return "control_plus_active_backbone"
    if re.search(r"\b(observation|no treatment|no intervention|watchful waiting|surveillance)\b",
                 title, re.I):
        return "observation_no_active_agent"
    if CONTROL_TOKEN.search(title):
        return "placebo_or_bsc_alone"
    return "control_arm_unclassified"


def build():
    with open(CORPUS) as fh:
        corpus = json.load(fh)
    with open(ALTERNATIVES) as fh:
        alts = json.load(fh)
    regime = None
    if os.path.exists(REGIME):
        with open(REGIME) as fh:
            regime = json.load(fh)

    rows, buckets = [], {}
    for a in corpus["C2_arms"]:
        k = classify(a)
        buckets[k] = buckets.get(k, 0) + 1
        if k == "not_a_control_arm":
            continue
        c, n = a["cells"], a["evaluable_n"]
        orr, dc = c["CR"] + c["PR"], c["CR"] + c["PR"] + c["SD"]
        rows.append({
            "nct_id": a["nct_id"],
            "arm_title": a["arm_title"],
            "arm_group_type": a.get("arm_group_type"),
            "classification": k,
            "conditions": a["conditions"],
            "n": n,
            "cells": c,
            "objective_response_pct": pct(orr / n),
            "objective_response_wilson95": wilson(orr, n),
            "disease_control_pct": pct(dc / n),
            "disease_control_wilson95": wilson(dc, n),
            "progression_required_at_entry": "CANNOT_DETERMINE",
            "crossover_permitted": "CANNOT_DETERMINE",
            "figure_is_pre_crossover": "CANNOT_DETERMINE",
            "response_criterion_and_version": "CANNOT_DETERMINE",
            "imaging_interval_weeks": "CANNOT_DETERMINE",
            "assessment": "CANNOT_DETERMINE",
            "usable_for_calibration": False,
            "why_not_usable": (
                "an active backbone is named in the arm title, so its outcomes measure the "
                "backbone rather than natural history"
                if k == "control_plus_active_backbone" else
                "the fields that decide the direction of the bound -- progression required at "
                "entry, crossover, pre-crossover status, imaging interval -- are eligibility and "
                "protocol prose, not posted-results fields, and were not retrieved for this arm"),
            "retrieved_file": a["retrieved_file"],
        })

    untreated = [r for r in rows if r["classification"] in
                 ("placebo_or_bsc_alone", "observation_no_active_agent")]

    e10 = alts.get("E10_indolent_tumour_placebo_calibration", {})

    # The corner: conditions in the low-response regime that have no control arm at all here.
    corner = None
    if regime:
        conds_with_control = {c for r in rows for c in r["conditions"]}
        low = [c for c in regime["G3_disease_coordinates"]["coordinates"]
               if c["median_objective_response_pct"] <= 15.0]
        corner = {
            "definition": "conditions placed on the regime map with a median objective response "
                          "of 15% or less",
            "conditions_in_the_low_response_regime": len(low),
            "of_those_with_any_control_arm_in_this_corpus":
                sum(1 for c in low if c["condition"] in conds_with_control),
            "named_without_any_control_arm": [c["condition"] for c in low
                                              if c["condition"] not in conds_with_control][:40],
        }

    doc = {
        "_schema": "placebo-arm-calibration/1",
        "_generated_by": "research/manuscripts/placebo_arm_calibration.py",
        "_do_not_hand_edit": True,
        "title": "What happens on no active treatment, and how little of it has been measured",
        "governed_by": "systems/POLICY-evidence.md 2.6",
        "reads": ["research/manuscripts/endpoint-corpus.json",
                  "research/manuscripts/emc-endpoint-alternatives.json",
                  "research/manuscripts/endpoint-regime-map.json"],

        "P1_extraction_contract": {
            "required_fields": REQUIRED_FIELDS,
            "an_arm_missing_any_required_field_is_context_not_calibration": True,
            "why_this_contract_is_strict": (
                "a disease-control rate from an arm imaged every 6 weeks is not the same "
                "measurement as one imaged every 12, and an arm enrolled on documented progression "
                "bounds natural history from the opposite side to an unselected cohort. Without "
                "those fields the number is not imprecise -- it is uninterpretable."),
        },

        "P2_control_arms": rows,

        "P3_classification": {
            "_the_distinction_that_matters": (
                "most oncology placebo arms sit on an active backbone and measure the backbone. "
                "The classifier errs toward BACKBONED on purpose: a false backboned call costs one "
                "arm of calibration, a false untreated call puts a treated arm into a "
                "natural-history estimate."),
            "counts": buckets,
            "control_arms_found": len(rows),
            "control_arms_with_no_active_agent_named": len(untreated),
            "usable_for_calibration_today": 0,
            "reading": (
                "the corpus yields control arms, and essentially none of them is an untreated arm "
                "with the fields needed to read natural history from it. This is the central "
                "practical finding of this module and it is a statement about the record, not "
                "about biology."),
        },

        "P4_progression_at_entry_strata": {
            "_never_merged": (
                "an arm enrolled on documented progression gives a LOWER bound on natural-history "
                "stability; an unselected or observation cohort gives an UPPER bound. Summarising "
                "the two together would produce a number that bounds nothing."),
            "corpus_arms_stratifiable": 0,
            "why": (
                "eligibility criteria are protocol prose. ClinicalTrials.gov posts them, but not "
                "in the outcome-measure records retrieved here, and they were not fetched per arm. "
                "Recorded as CANNOT_DETERMINE rather than assumed either way."),
        },

        "P5_the_sourced_existence_proof": {
            "_why_this_block_is_carried_rather_than_recomputed": (
                "emc-endpoint-alternatives.json -> E10 already holds a retrieved, verbatim-quoted "
                "randomised placebo-controlled measurement in an indolent soft-tissue tumour. It "
                "is pointed at, not re-typed."),
            "owned_by": "research/manuscripts/emc-endpoint-alternatives.json -> "
                        "E10_indolent_tumour_placebo_calibration",
            "the_two_readings": e10.get("⭐_the_two_readings_that_matter_here")
                                or e10.get("randomised_placebo_controlled"),
            "why_it_matters_to_this_paper": (
                "it converts 'stable disease might be natural history' from a worry into a "
                "measured quantity in at least one disease, and it qualifies the companion claim "
                "that objective responses are hard to explain by natural history -- in that trial "
                "one patient in five responded on placebo. Both are properties of that disease and "
                "transfer to none other."),
        },

        "P6_the_corner_with_no_control_arms": corner or {
            "_status": "not computed -- endpoint-regime-map.json was not present at build time",
        },

        "P7_traps": {
            "placebo_is_not_untreated": "most placebo arms carry an active backbone (P3).",
            "crossover": (
                "only pre-crossover figures can speak to natural history, and overall survival "
                "from a crossover trial says nothing about it at all."),
            "imaging_schedule": (
                "RECIST requires a minimum interval before stable disease can be assigned, so "
                "disease-control rates from different scan schedules are different measurements. "
                "This is the confounder nobody records."),
            "assessor": "investigator versus blinded central review moves response rates.",
            "denominator_drift": (
                "intention-to-treat, response-evaluable and at-least-one-post-baseline-scan are "
                "three different denominators and abstracts often use a different one from the "
                "table."),
            "what_a_control_arm_can_never_calibrate": (
                "the natural history of a different disease, and the natural history of any "
                "disease that has no control arm -- which is most of the low-response regime."),
        },

        "not_a_recommendation": (
            "No efficacy, safety or treatment claim about any agent. Nothing here says a control "
            "arm outcome is what an individual patient would experience untreated."),
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
    p3 = doc["P3_classification"]
    print(f"wrote {OUT_REL}")
    print(f"  control arms found                  : {p3['control_arms_found']}")
    print(f"  classification                      : {p3['counts']}")
    print(f"  no active agent named               : {p3['control_arms_with_no_active_agent_named']}")
    print(f"  usable for calibration today        : {p3['usable_for_calibration_today']}")
    c = doc["P6_the_corner_with_no_control_arms"]
    if "conditions_in_the_low_response_regime" in c:
        print(f"  low-response conditions             : {c['conditions_in_the_low_response_regime']}")
        print(f"  ...of those with any control arm    : {c['of_those_with_any_control_arm_in_this_corpus']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
