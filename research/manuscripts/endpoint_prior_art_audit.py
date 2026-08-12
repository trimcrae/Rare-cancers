#!/usr/bin/env python3
"""Has oncology already fixed this, and where. The necessity check. ($0, stdlib)

WHY THIS FILE EXISTS, AND WHY IT COULD SINK THE PAPER. The argument that a response-rate summary
fails in a low-rate, low-accrual regime is only worth publishing if the field has not already
solved it. Several disciplines demonstrably have. This module establishes WHICH, HOW, and -- the
part that decides whether there is a paper -- which diseases in the regime still have nothing.

If the answer had come back "almost everyone has fixed this", the honest paper would be a map with
an unfixed set on it rather than a general complaint, and that outcome was planned for before the
data was read.

THE FOUR FIX FAMILIES. Every solution retrieved falls into one of four, and naming them is what
turns a list of criteria documents into a transferable argument:

  A  SWITCH THE ENDPOINT to time-to-event (progression-free rate at a fixed timepoint, PFS)
  B  REDEFINE RESPONSE so it catches non-shrinkage biology (density, necrosis, viable tumour)
  C  ADD CATEGORIES between response and progression (minor response, non-CR/non-PD)
  D  MAKE THE PATIENT THEIR OWN CONTROL (growth modulation index, randomised discontinuation)

EVIDENCE DISCIPLINE. Every row points at a retrieved record in endpoint-prior-art-inputs.json --
title, journal, year and abstract as returned by Europe PMC. The fix-family assignment and the
endorsement grade are JUDGEMENTS made from those retrieved fields and are labelled as judgements.
No identifier and no title is typed from recollection.

Usage:
  python3 research/manuscripts/endpoint_prior_art_audit.py           # regenerate
  python3 research/manuscripts/endpoint_prior_art_audit.py --check   # verify the committed artifact
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, "endpoint", "endpoint-prior-art-inputs.json")
REGIME = os.path.join(HERE, "endpoint", "endpoint-regime-map.json")
OUT = os.path.join(HERE, "endpoint", "endpoint-prior-art-audit.json")
OUT_REL = "research/manuscripts/endpoint/endpoint-prior-art-audit.json"

FAMILIES = {
    "A_switch_to_time_to_event": "replace the response summary with a time-to-event or "
                                 "fixed-timepoint progression-free endpoint",
    "B_redefine_response": "keep a response endpoint but redefine it so it detects the biology the "
                           "agent actually produces",
    "C_add_categories": "keep the endpoint and add categories between response and progression",
    "D_patient_as_own_control": "remove the historical comparator by making each patient their own "
                                "control",
}

#: pmid -> (domain, fix family, endorsement grade, what it changed). The pmid keys are the ones
#: returned by the fetches; every one resolves in endpoint-prior-art-inputs.json, asserted at build.
#: Grades: `consensus_guideline` (a named working group issuing criteria), `methodology_paper`
#: (a design or statistical method), `single_trial_precedent` (one trial using it).
ASSIGNMENTS = {
    "17470865": ("gastrointestinal stromal tumour", "B_redefine_response", "single_trial_precedent",
                 "the observation that imatinib-treated GIST changes density rather than size, "
                 "which is the measurement that motivated the Choi criteria"),
    "17470866": ("gastrointestinal stromal tumour", "B_redefine_response", "methodology_paper",
                 "the explicit argument that size-based response criteria should not be used in "
                 "this disease"),
    "20231676": ("high-grade glioma", "B_redefine_response", "consensus_guideline",
                 "response assessment criteria issued by a named neuro-oncology working group"),
    "21474379": ("diffuse low-grade glioma", "A_switch_to_time_to_event", "consensus_guideline",
                 "outcome assessment for trials in a slow-growing tumour, from the same group"),
    "20175033": ("hepatocellular carcinoma", "B_redefine_response", "consensus_guideline",
                 "a modified response assessment counting viable rather than total tumour"),
    "25113753": ("Hodgkin and non-Hodgkin lymphoma", "C_add_categories", "consensus_guideline",
                 "a staging and response classification for a family of diseases with indolent "
                 "members"),
    "28379322": ("lymphoma", "C_add_categories", "consensus_guideline",
                 "an international working group response classification issued alongside the "
                 "incumbent one"),
    "29540348": ("chronic lymphocytic leukaemia", "C_add_categories", "consensus_guideline",
                 "guidelines that specify indications for treatment as well as response "
                 "assessment, which is what makes deferred treatment measurable"),
    "26903579": ("castration-resistant prostate cancer", "A_switch_to_time_to_event",
                 "consensus_guideline",
                 "trial design and objectives from a named working group, in a disease where much "
                 "of the burden is not measurable by size at all"),
    "9607564": ("oncology-wide", "D_patient_as_own_control", "methodology_paper",
                "the argument that trial design rather than agent is often what produces a "
                "negative result"),
    "20920605": ("oncology-wide", "D_patient_as_own_control", "methodology_paper",
                 "statistical methods for a phase 2 trial using a growth modulation index"),
    "30458583": ("oncology-wide", "D_patient_as_own_control", "methodology_paper",
                 "a phase 2 design with the growth modulation index as the PRIMARY endpoint, so "
                 "the approach is powered rather than descriptive"),
    "33672857": ("soft-tissue sarcoma", "D_patient_as_own_control", "single_trial_precedent",
                 "a growth-modulation-index-based score applied in a sarcoma cohort"),
    "40156702": ("oncology-wide", "D_patient_as_own_control", "methodology_paper",
                 "a review of the growth modulation index as an efficacy outcome"),
    "30528315": ("oncology-wide", "D_patient_as_own_control", "single_trial_precedent",
                 "a placebo-controlled randomised discontinuation trial, the design that removes "
                 "the historical comparator entirely"),
    "27714541": ("breast carcinoma", "D_patient_as_own_control", "single_trial_precedent",
                 "a second randomised discontinuation trial, establishing the design is runnable "
                 "rather than theoretical"),
    "26731483": ("neuroendocrine tumour", "A_switch_to_time_to_event", "single_trial_precedent",
                 "a placebo-controlled trial in an indolent tumour reading out on tumour growth "
                 "control rather than on response"),
    "25317882": ("enteropancreatic neuroendocrine tumour", "A_switch_to_time_to_event",
                 "single_trial_precedent",
                 "a placebo-controlled trial in an indolent tumour with a progression-based "
                 "primary endpoint"),
}


#: Weakest-to-strongest. A consensus guideline from a named working group is an ENDORSEMENT; a
#: single trial that used the design is a PRECEDENT, which is weaker and must not be summarised as
#: the same thing.
GRADE_RANK = {"consensus_guideline": 0, "single_trial_precedent": 1, "methodology_paper": 2}


def _strength_by_domain(rows):
    """How strong the evidence is PER DOMAIN, not pooled across the audit.

    ⛔ WHY THIS IS NOT OPTIONAL. `count: 12` invites the sentence "four families endorsed across 12
    disease domains", which the abstract carried. Seven of those domains have a consensus guideline.
    The other five rest on a single trial that used the design -- a precedent, not an endorsement --
    and pooling the two under one word makes the weaker half borrow the stronger half's authority.
    Section 7 already split the grades in prose; the summary count did not, and the summary is what
    gets quoted.

    It also records how THIN the coverage is: a domain resting on one retrieved document is one
    query away from not being covered at all.
    """
    by = {}
    for r in rows:
        if r["domain"] == "oncology-wide":
            continue
        by.setdefault(r["domain"], []).append(r)
    def best(rs):
        return min(rs, key=lambda r: GRADE_RANK[r["endorsement_grade"]])["endorsement_grade"]
    strongest = {d: best(rs) for d, rs in by.items()}
    counts = {}
    for g in strongest.values():
        counts[g] = counts.get(g, 0) + 1
    return {
        "_what_this_measures": (
            "for each disease domain, the STRONGEST grade of document retrieved for it, and how "
            "many documents that domain rests on"),
        "strongest_grade_per_domain": strongest,
        "domains_by_strongest_grade": counts,
        "domains_with_a_consensus_guideline":
            sum(1 for g in strongest.values() if g == "consensus_guideline"),
        "domains_resting_only_on_a_trial_precedent":
            sum(1 for g in strongest.values() if g == "single_trial_precedent"),
        "documents_per_domain": {d: len(rs) for d, rs in sorted(by.items())},
        "domains_resting_on_a_single_document": sum(1 for rs in by.values() if len(rs) == 1),
        "_the_honest_summary": (
            "consensus guidelines in some domains and trial precedent in the rest. 'Endorsed across "
            "N domains' is true only of the first group, and the count of the second is reported "
            "beside it rather than folded into it."),
    }


def build():
    with open(INPUTS) as fh:
        inputs = json.load(fh)
    recs = inputs["records"]
    with open(REGIME) as fh:
        regime = json.load(fh)

    missing = sorted(set(ASSIGNMENTS) - set(recs))
    if missing:
        raise SystemExit(f"FAIL: assignments reference identifiers absent from the retrieved "
                         f"records: {missing}. Every row must trace to a fetch.")

    rows = []
    for pmid, (domain, fam, grade, changed) in sorted(
            ASSIGNMENTS.items(), key=lambda kv: recs[kv[0]]["year"] or ""):
        r = recs[pmid]
        rows.append({
            "pmid": pmid,
            "year": r["year"],
            "title": r["title"],
            "journal": r["journal"],
            "doi": r.get("doi"),
            "domain": domain,
            "fix_family": fam,
            "endorsement_grade": grade,
            "what_it_changed": changed,
            "_assignment_is_a_judgement": (
                "domain, fix family and endorsement grade are judgements made from the retrieved "
                "title, journal and abstract. The record itself is retrieved; the classification "
                "is not, and a reader may disagree with it without disturbing the citation."),
            "retrieved_via": r["retrieved_via"],
        })

    by_family, by_grade, domains = {}, {}, {}
    for row in rows:
        by_family.setdefault(row["fix_family"], []).append(row["pmid"])
        by_grade[row["endorsement_grade"]] = by_grade.get(row["endorsement_grade"], 0) + 1
        domains.setdefault(row["domain"], []).append(row["fix_family"])

    disease_specific = {d: sorted(set(f)) for d, f in domains.items() if d != "oncology-wide"}
    coords = regime["G3_disease_coordinates"]["coordinates"]
    low = [c for c in coords if c["median_objective_response_pct"] <= 15.0]

    doc = {
        "_schema": "endpoint-prior-art-audit/1",
        "_generated_by": "research/manuscripts/endpoint_prior_art_audit.py",
        "_do_not_hand_edit": True,
        "title": "Which diseases already replaced the response-rate summary, and how",
        "reads": ["research/manuscripts/endpoint/endpoint-prior-art-inputs.json",
                  "research/manuscripts/endpoint/endpoint-regime-map.json"],

        "A0_the_necessity_question": {
            "asked": "has oncology already solved this, making the argument unnecessary?",
            "answer": (
                "partly, repeatedly, and separately. At least four distinct solution families are "
                "in use, several carried by named working groups issuing formal criteria. What has "
                "NOT happened is generalisation: each fix was made for one disease or one drug "
                "class and stayed there."),
            "consequence_for_the_paper": (
                "the defensible claim is not that oncology has failed to notice. It is that the "
                "problem is a property of a coordinate, that the solutions already exist, and that "
                "they have not reached the diseases whose coordinates need them most. That is a "
                "narrower and more useful paper than the one that would have been written without "
                "asking."),
            "what_would_have_falsified_the_paper": (
                "finding a general, cross-disease treatment of the low-rate/low-accrual regime "
                "with an endorsed remedy. None was retrieved. That is an absence in what these "
                "queries returned, not a proof that none exists."),
        },

        "A1_endorsed_alternatives": rows,

        "A2_fix_families": {
            "definitions": FAMILIES,
            "documents_per_family": {k: len(v) for k, v in sorted(by_family.items())},
            "identifiers_per_family": {k: sorted(v) for k, v in sorted(by_family.items())},
            "_all_four_families_are_occupied": len(by_family) == len(FAMILIES),
        },

        "A3_endorsement_grades": {
            "definitions": {
                "consensus_guideline": "a named working group issuing response or trial-design "
                                       "criteria",
                "methodology_paper": "a design or statistical method, not disease-specific",
                "single_trial_precedent": "one trial or cohort using the approach",
            },
            "counts": by_grade,
            "reading": (
                "the disease-specific fixes are mostly consensus guidelines, and the "
                "patient-as-own-control family is mostly methodology and single-trial precedent. "
                "The family that best addresses the natural-history confound is the one with the "
                "least formal endorsement."),
        },

        "A4_diseases_with_an_endorsed_alternative": {
            "disease_domains_covered": disease_specific,
            "count": len(disease_specific),
            "_scope": (
                "covered means a document was retrieved for that domain by these queries. It is "
                "not a systematic review of guidelines and cannot show that a disease has NO "
                "alternative -- only that none was retrieved here."),
            "⚠_covered_is_not_uniformly_endorsed": _strength_by_domain(rows),
        },

        "A5_the_gap": {
            "conditions_in_the_low_response_regime": len(low),
            "_definition": "conditions placed on the regime map with a median objective response "
                           "of 15% or less",
            "_why_this_is_the_paper": (
                "the fixes exist and are old -- the earliest retrieved document is from 1998. The "
                "gap is not invention, it is diffusion: a remedy endorsed in glioma or GIST or "
                "lymphoma does not reach a rare tumour whose coordinate is worse than any of "
                "them."),
            "transferability": {
                "A_switch_to_time_to_event": "transfers immediately and costs no patients, but "
                                             "inherits the natural-history confound whole -- it "
                                             "only moves which number is uncalibrated",
                "B_redefine_response": "transfers only where the agent produces a specific "
                                       "non-shrinkage change that imaging can see",
                "C_add_categories": "transfers cheaply and improves reporting, but does not fix "
                                    "the small-sample problem",
                "D_patient_as_own_control": "the only family that attacks the confound rather than "
                                            "relocating it, and the least formally endorsed",
            },
        },

        "A6_what_this_audit_is_not": {
            "not_a_systematic_review": (
                "the corpus is what a frozen set of queries returned. A disease absent here may "
                "have an endorsed alternative that these queries did not reach."),
            "assignments_are_judgements": (
                "fix family, domain and endorsement grade are read off retrieved titles, journals "
                "and abstracts by the author of this file. The records are retrieved; the "
                "classification is an opinion that can be disputed without disturbing a citation."),
            "no_efficacy_claim": (
                "nothing here says any endpoint produced a better treatment decision, or that any "
                "agent works. It records what criteria exist and who issued them."),
        },
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
    print(f"wrote {OUT_REL}")
    print(f"  documents audited      : {len(doc['A1_endorsed_alternatives'])}")
    print(f"  per fix family         : {doc['A2_fix_families']['documents_per_family']}")
    print(f"  endorsement grades     : {doc['A3_endorsement_grades']['counts']}")
    print(f"  disease domains covered: {doc['A4_diseases_with_an_endorsed_alternative']['count']}")
    print(f"  low-response regime    : "
          f"{doc['A5_the_gap']['conditions_in_the_low_response_regime']} conditions")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
