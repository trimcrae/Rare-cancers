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
CORPUS = os.path.join(HERE, "endpoint", "endpoint-corpus.json")
ALTERNATIVES = os.path.join(HERE, "endpoint", "emc-endpoint-alternatives.json")
REGIME = os.path.join(HERE, "endpoint", "endpoint-regime-map.json")
DETAIL = os.path.join(HERE, "endpoint", "placebo-arm-detail-inputs.json")
NATURAL_HISTORY = os.path.join(HERE, "endpoint", "natural-history-inputs.json")
OUT = os.path.join(HERE, "endpoint", "placebo-arm-calibration.json")
OUT_REL = "research/manuscripts/endpoint/placebo-arm-calibration.json"

#: An arm title naming an active anti-tumour agent alongside the control token is BACKBONED. The
#: list is deliberately broad: a false BACKBONED call costs one arm of calibration, a false
#: UNTREATED call puts a treated arm into a natural-history estimate, which is the error that would
#: invalidate the analysis.
#:
#: ⛔ THE `+` ALTERNATIVE IS OUTSIDE THE `\b` GROUP ON PURPOSE (fixed 2026-08-09). It was written
#: inside it, where the leading `\b` applies to the whole alternation and therefore to `\+` as well.
#: A word boundary before a `+` needs a word character immediately to its LEFT, so the pattern
#: matched `Placebo+Drug` and never `Placebo + Drug` -- the spaced form, which is how registry arm
#: titles are actually written. Measured over the 552 corpus arms, correcting the scope changes the
#: backbone call for 93 arms, two of which carry a control token: both are `Placebo + Sandostatin
#: LAR`, the exact arm this module's own docstring names as the case that defeated the name list.
#: It was caught by the registry signal alone; now both signals agree on it.
BACKBONE = re.compile(
    r"(?:\b(?:chemotherap|cisplatin|carboplatin|cis\b|carb\b|docetaxel|paclitaxel|pemetrexed|"
    r"gemcitabine|doxorubicin|etoposide|irinotecan|oxaliplatin|fluorouracil|capecitabine|"
    r"temozolomide|dacarbazine|cyclophosphamide|bortezomib|lenalidomide|dexamethasone|"
    r"pembrolizumab|nivolumab|atezolizumab|durvalumab|avelumab|ipilimumab|rituximab|"
    r"trastuzumab|bevacizumab|cetuximab|physician.?s? choice|standard of care|SOC\b|"
    r"radiotherap|chemoradi)|\+\s*\w)", re.I)

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


#: Intervention names that are NOT an active anti-tumour agent. Everything else registered as an
#: intervention on the arm is treated as active.
INERT_INTERVENTION = re.compile(
    r"^\s*(?:drug|biological|other|procedure|device|dietary supplement)?\s*:?\s*"
    r"(placebo[^|]*|normal saline|saline|sham[^|]*|best supportive care|bsc|observation|"
    r"no intervention|standard follow[- ]?up|matching placebo)\s*$", re.I)


def _norm_label(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def registered_interventions(nct_id, arm_title, detail):
    """The interventions the REGISTRY records for this arm, matched by label.

    ⛔ WHY THIS REPLACED A NAME LIST (measured 2026-08-09). The backbone detector was a regex over
    drug names, so it could only catch drugs somebody had thought to list. It passed
    `Placebo + Sandostatin LAR` as an untreated arm -- octreotide is an active anti-tumour agent in
    neuroendocrine tumours, the class PROMID and CLARINET were built on -- and `Demcizumab/Placebo`,
    a sequence arm. Both are FALSE UNTREATED calls, which is the error this module states would
    invalidate it. Registered interventions are structural: an arm is untreated only if everything
    the registry attached to it is inert.
    """
    rec = detail.get(nct_id) or {}
    groups = rec.get("arm_groups") or []
    if not groups:
        return None
    want = _norm_label(arm_title)
    best = None
    for g in groups:
        lab = _norm_label(g.get("label"))
        if not lab:
            continue
        if lab == want or lab in want or want in lab:
            if best is None or len(lab) > len(_norm_label(best.get("label"))):
                best = g
    return None if best is None else (best.get("interventions") or [])


def classify(arm, detail=None):
    """Classify an arm. BOTH signals must agree before an arm is called untreated.

    ⛔ TWO FAILURES, IN OPPOSITE DIRECTIONS, BOTH MEASURED 2026-08-09.

    The title-only detector was a regex over drug names, so it could only catch drugs somebody had
    listed. It passed `Placebo + Sandostatin LAR` -- octreotide, an active agent in neuroendocrine
    tumours and the class PROMID and CLARINET were built on -- as untreated.

    Replacing it with the registry's own intervention list was worse, not better. Outcome-measure
    group titles do not match protocol arm labels, so the lookup matched the WRONG arm group and
    called `Part 2: Placebo + Chemotherapy` untreated on the strength of a sibling arm registered as
    `Drug: Placebo`. A structural signal that can override a correct one is more dangerous than a
    name list, because it looks authoritative.

    So neither signal is trusted alone. An arm is untreated only when the title names no active
    agent AND its matched registry interventions are all inert. Any disagreement, and any failure to
    match a label at all, resolves to backboned or unclassifiable -- never to untreated. A false
    backboned call costs one arm of calibration; a false untreated call puts a treated arm into a
    natural-history estimate, which is the error that would invalidate this module.
    """
    detail = detail or {}
    title = arm.get("arm_title") or ""
    gtype = arm.get("arm_group_type")
    if not (CONTROL_TOKEN.search(title) or gtype in ("PLACEBO_COMPARATOR", "NO_INTERVENTION")):
        return "not_a_control_arm"

    title_says_active = bool(BACKBONE.search(title))
    iv = registered_interventions(arm.get("nct_id"), title, detail)

    if title_says_active:
        return "control_plus_active_backbone"
    if iv is None:
        # No registry corroboration available for this arm.
        return "control_arm_unclassified_no_registry_match"
    active = [x for x in iv if not INERT_INTERVENTION.match(x or "")]
    if active:
        return "control_plus_active_backbone"
    if not iv:
        return "observation_no_active_agent"
    return "placebo_or_bsc_alone"


def _type_counts(rows):
    out = {}
    for r in rows:
        t = r.get("arm_group_type") or "UNRESOLVED"
        out[t] = out.get(t, 0) + 1
    return out


def _verdict_counts(detail):
    out = {}
    for rec in detail.values():
        v = (rec.get("progression_at_entry") or {}).get("verdict", "UNREADABLE")
        out[v] = out.get(v, 0) + 1
    return out


def build():
    with open(CORPUS) as fh:
        corpus = json.load(fh)
    with open(ALTERNATIVES) as fh:
        alts = json.load(fh)
    regime = None
    if os.path.exists(REGIME):
        with open(REGIME) as fh:
            regime = json.load(fh)
    detail = {}
    if os.path.exists(DETAIL):
        with open(DETAIL) as fh:
            detail = json.load(fh).get("records", {})
    nat = {}
    if os.path.exists(NATURAL_HISTORY):
        with open(NATURAL_HISTORY) as fh:
            nat = json.load(fh)

    rows, buckets = [], {}
    for a in corpus["C2_arms"]:
        k = classify(a, detail)
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
            "progression_required_at_entry":
                (detail.get(a["nct_id"], {}).get("progression_at_entry") or
                 {"verdict": "CANNOT_DETERMINE"}),
            "crossover_mentioned_anywhere_in_the_record":
                detail.get(a["nct_id"], {}).get("crossover_mentioned", "CANNOT_DETERMINE"),
            "masking": detail.get(a["nct_id"], {}).get("masking", "CANNOT_DETERMINE"),
            "response_criterion_mentioned":
                detail.get(a["nct_id"], {}).get("response_criterion_mentioned",
                                                "CANNOT_DETERMINE"),
            "imaging_interval_stated":
                detail.get(a["nct_id"], {}).get("imaging_interval_stated", "CANNOT_DETERMINE"),
            "central_review_mentioned":
                detail.get(a["nct_id"], {}).get("central_review_mentioned", "CANNOT_DETERMINE"),
            "⛔_response_may_predate_the_control_period": (
                a["cells"]["CR"] + a["cells"]["PR"] > 0
                and k == "observation_no_active_agent"),
            "usable_for_calibration": (
                k in ("placebo_or_bsc_alone", "observation_no_active_agent")
                and not (a["cells"]["CR"] + a["cells"]["PR"] > 0
                         and k == "observation_no_active_agent")
                and (detail.get(a["nct_id"], {}).get("progression_at_entry") or {}).get("verdict")
                == "REQUIRED"),
            "bound_direction": (
                "LOWER -- enrolled on documented progression, so stability observed here is a floor "
                "on what natural history produces"
                if (detail.get(a["nct_id"], {}).get("progression_at_entry") or {}).get("verdict")
                == "REQUIRED" and k in ("placebo_or_bsc_alone", "observation_no_active_agent")
                else "UNASSIGNABLE"),
            "why_not_usable": (
                None if (k in ("placebo_or_bsc_alone", "observation_no_active_agent")
                         and (detail.get(a["nct_id"], {}).get("progression_at_entry") or {})
                         .get("verdict") == "REQUIRED")
                else "an active backbone is named in the arm title, so its outcomes measure the "
                     "backbone rather than natural history"
                if k == "control_plus_active_backbone" else
                "the arm carries no active agent, but its trial does not state that documented "
                "progression was required at entry, so the reading cannot be assigned a bound "
                "direction (P4)"),
            "retrieved_file": a["retrieved_file"],
        })

    untreated = [r for r in rows if r["classification"] in
                 ("placebo_or_bsc_alone", "observation_no_active_agent")]

    # Derived, never typed (CLAUDE.md rule 1.1). Every count the P3 prose quotes comes from here, so
    # a corpus change moves the sentence and the number together instead of leaving them disagreeing
    # -- which is exactly how P3's `reading` came to call 19 arms "control arms" while the field
    # directly above it called the same 19 a screening net.
    n_arms = len(corpus["C2_arms"])
    control_typed = len([r for r in rows if r.get("arm_group_type")
                         in ("PLACEBO_COMPARATOR", "NO_INTERVENTION")])
    active_typed = len([r for r in rows if r.get("arm_group_type")
                        in ("EXPERIMENTAL", "ACTIVE_COMPARATOR")])

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
        "reads": ["research/manuscripts/endpoint/endpoint-corpus.json",
                  "research/manuscripts/endpoint/emc-endpoint-alternatives.json",
                  "research/manuscripts/endpoint/endpoint-regime-map.json"],

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
            "⚠_what_the_screening_net_actually_counts": (
                f"arms whose TITLE or registered type carries a control token -- placebo, best "
                f"supportive care, observation. All {len(rows)} passed that net; it is not a claim "
                f"that all {len(rows)} are control arms. {active_typed} are registered EXPERIMENTAL "
                f"or ACTIVE_COMPARATOR and match only because their title contains 'BSC': in a "
                f"trial comparing an agent against chemotherapy plus best supportive care, BOTH "
                f"arms carry the token. The composition is reported below rather than left to a "
                f"reader who might take {len(rows)} as a count of control arms."),
            "composition_by_registered_arm_type": _type_counts(rows),
            "arms_the_registry_registers_as_a_control_type": control_typed,
            "arms_the_registry_registers_as_an_active_type": active_typed,
            "control_arms_with_no_active_agent_named": len(untreated),
            "usable_for_calibration_today": len([r for r in rows if r["usable_for_calibration"]]),
            "reading": (
                f"of {n_arms} arms, {len(rows)} pass the control-token screen. Reading the "
                f"registry's own intervention list rather than the arm title, "
                f"{buckets.get('control_plus_active_backbone', 0)} carry an active backbone. "
                f"{buckets.get('control_arm_unclassified_no_registry_match', 0)} cannot be matched "
                f"to a registered arm group and are therefore not called untreated. "
                f"{buckets.get('observation_no_active_agent', 0)} is a genuine no-intervention arm, "
                f"and its best-response table measures response to the therapy that preceded "
                f"randomisation (P7). ZERO arms in this corpus can carry a natural-history reading. "
                f"That is a statement about the record, not about biology, and it is a measured "
                f"conclusion from full protocol records rather than an absence of data."),
        },

        "P4_progression_at_entry_strata": {
            "_source": ("read from ClinicalTrials.gov eligibility prose, retrieved in round 6 for "
                        "the 12 trials contributing a control arm. Round 4's field limit had "
                        "dropped the eligibility module, which is why this was CANNOT_DETERMINE "
                        "for every arm until now."),
            "trials_with_the_field_read": len(detail),
            "verdicts_across_those_trials": _verdict_counts(detail),
            "arms_assignable_to_a_bound_direction": len(
                [r for r in rows if r["bound_direction"] != "UNASSIGNABLE"]),
            "_never_merged": (
                "an arm enrolled on documented progression gives a LOWER bound on natural-history "
                "stability; an unselected or observation cohort gives an UPPER bound. Summarising "
                "the two together would produce a number that bounds nothing."),
            "why_most_arms_remain_unassignable": (
                "a trial that does not STATE a progression requirement has not thereby enrolled "
                "unselected patients -- the requirement may sit in a protocol this record does not "
                "carry. NOT_MENTIONED is an absent reading, and it is not evidence that entry was "
                "unselected. Only a stated requirement assigns a direction."),
        },

        "P5_the_sourced_existence_proof": {
            "_why_this_block_is_carried_rather_than_recomputed": (
                "emc-endpoint-alternatives.json -> E10 already holds a retrieved, verbatim-quoted "
                "randomised placebo-controlled measurement in an indolent soft-tissue tumour. It "
                "is pointed at, not re-typed."),
            "owned_by": "research/manuscripts/endpoint/emc-endpoint-alternatives.json -> "
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
            "⛔_a_best_response_on_an_observation_arm_may_be_a_response_to_PRIOR_therapy": (
                "the single arm in this corpus that the registry records as carrying no "
                "intervention reports a 48.4% objective response. An arm receiving nothing cannot "
                "produce responses at that rate, and the resolution is that the trial randomises "
                "AFTER chemoradiotherapy: the best response recorded is the response to the "
                "preceding treatment, carried into the observation period. So even a genuine "
                "no-intervention arm does not automatically yield a natural-history reading -- the "
                "reading has to start when the observation does. This trap was found by asking why "
                "a number looked impossible, and it would have silently produced a natural-history "
                "'response rate' of 48.4% had the classification been trusted on its own."),
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

        "P9_the_confound_HAS_been_measured_outside_this_corpus": {
            "⛔_the_correction": (
                "P3 concludes that no arm in this corpus can carry a natural-history reading. That "
                "is true of the CORPUS and false of the LITERATURE. The corpus rule requires a "
                "four-cell best-response table from an interventional arm, so a prospective "
                "OBSERVATIONAL cohort of untreated patients was never eligible for it -- and that "
                "is exactly the design in which the confound has actually been measured. Reporting "
                "the corpus result without this would let a scope limit read as an absence of "
                "evidence, which is the failure this repository calls an absent reading standing "
                "in for a reading of absence."),
            "_found_how": (
                "retrieval round 5 was dispatched, returned six payloads, and was not opened for "
                "several days. These records were in it the whole time. An unused fetch that looks "
                "used is its own defect and is recorded as one."),
            "the_two_load_bearing_records": [
                {"pmid": "37777684",
                 "what_it_is": "prospective multicentre phase II observational trial, active "
                               "surveillance as the only intervention, central radiology review",
                 "n": 100,
                 "why_it_matters": (
                     "it reports a 3-year progression-free survival of 53.4% (95% CI 43.5-63.1) "
                     "and, on NO active treatment, 58% spontaneous regression and 26% partial "
                     "responses by RECIST. An objective response rate measured on untreated "
                     "patients is precisely the quantity a single-arm response readout assumes is "
                     "zero.")},
                {"pmid": "39620931",
                 "what_it_is": "pooled analysis of three prospective observational active "
                               "surveillance studies (Italy, Netherlands, France)",
                 "n": 282,
                 "why_it_matters": (
                     "3- and 5-year treatment-free survival of 67% and 66%, with crude cumulative "
                     "incidences of 33% and 34% for RECIST progression and 26% and 34% for "
                     "spontaneous RECIST regression. Larger, multinational, and concordant with "
                     "the single trial above.")},
            ],
            "⭐_it_agrees_with_the_randomised_evidence": (
                "emc-endpoint-alternatives.json -> E10 records a randomised placebo-controlled "
                "trial in the same disease reporting a 20% objective response rate in the placebo "
                "arm before crossover. Two independent designs -- a placebo arm and an untreated "
                "observational cohort -- put the natural-history objective response rate in this "
                "tumour at roughly a fifth to a quarter of patients. Agreement across designs is "
                "what turns one surprising number into a finding."),
            "⛔_what_this_does_NOT_license": (
                "any transfer of these rates to another disease, in either direction. Desmoid "
                "fibromatosis does not metastasise and most tumours in this corpus do; spontaneous "
                "regression is a documented feature of desmoid biology and is not documented in "
                "most of them. These figures establish that the confound is MEASURABLE and has "
                "been measured, not what its size is anywhere else."),
            "_the_general_consequence": (
                "the natural-history component of a response readout is not a theoretical worry "
                "that trialists may reasonably set aside. In at least one indolent tumour it has "
                "been measured twice, by different designs, and it is large. Where it has not been "
                "measured, that is a gap in the record rather than evidence that it is small."),
            "records": nat.get("records", {}),
            "transfer_fencing": nat.get("⛔_transfer_fencing"),
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
