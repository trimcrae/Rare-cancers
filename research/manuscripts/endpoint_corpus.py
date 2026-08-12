#!/usr/bin/env python3
"""The cross-disease endpoint corpus -- one home for every arm-level count and quote. ($0, stdlib)

WHAT THIS IS. The single source of the arm-level counts behind the cross-disease endpoint analyses.
It holds no analysis of its own: orr_dcr_reread.py, endpoint_regime_map.py, placebo_arm_calibration.py
and endpoint_prior_art_audit.py read `endpoint-corpus.json` and never re-type a number, the same
contract emc_endpoint_alternatives.py has with emc-systemic-therapy-pooling.json.

THE CORPUS RULE, and why it is shaped this way. The unit is ONE ARM of one interventional trial.
No tumour type, grade, rarity or indolence descriptor is ever an inclusion criterion -- selecting on
the description is how a corpus comes to confirm the description. Inclusion is a property of the
REPORT: does it carry all four best-response categories (CR, PR, SD, PD) as integers for a named
arm? The frozen protocol is lit-targets-cross-disease-endpoints.json, committed before any fetch ran.
Governed by systems/POLICY-evidence.md 2.6.

WHERE THE COUNTS COME FROM, and why not from where they were expected. The four-cell table was
looked for in abstracts first, and measured rather than assumed: of 1277 unique abstracts screened
across retrieval rounds 1-2, all four category labels appeared in 5, and exactly 1 carried a
denominator they summed to. So the four-cell table is not an abstract-level object. It is a
structured field in ClinicalTrials.gov posted results, where per-category participant counts are
reported per arm under FDAAA. That measurement is kept as `A2_why_not_abstracts` because it is the
first quantitative statement of the reporting problem the manuscript is about.

WHAT A ROW IS NOT. A row is a reading of what a trial REPORTED. It is not a patient-level dataset,
not a re-analysis of any patient, and carries no efficacy claim about any agent in any disease.

Usage:
  python3 research/manuscripts/endpoint_corpus.py --extract   # CI or a checkout with the cache branch
  python3 research/manuscripts/endpoint_corpus.py             # derive the artifact from the cache
  python3 research/manuscripts/endpoint_corpus.py --check     # verify the committed artifact
"""
from __future__ import annotations

import collections
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "endpoint", "endpoint-corpus.json")
INPUTS = os.path.join(HERE, "endpoint", "endpoint-corpus-inputs.json")
PROTOCOL_REL = "research/manuscripts/endpoint/lit-targets-cross-disease-endpoints.json"
OUT_REL = "research/manuscripts/endpoint/endpoint-corpus.json"

CACHE_REFS = ("origin/literature-cache", "literature-cache", "FETCH_HEAD")
SLUG = "xdisease-ctg-results"

BOR_FILES = [f"ctg_results_bor_{t}" for t in
             ("1999_2009", "2010_2013", "2014_2017", "2018_2021", "2022_2026")]
PLACEBO_FILES = [f"ctg_placebo_onc_{t}" for t in
                 ("1999_2009", "2010_2013", "2014_2017", "2018_2021", "2022_2026")]
ACCRUAL_FILES = ["ctg_accrual_terminated_onc", "ctg_accrual_completed_onc_phase2"]

#: A category title must START with the label. "Complete Response" counts; "Duration of Complete
#: Response" does not, and neither does "Complete Response Rate (%)", which is a percentage and is
#: refused by the integer test below rather than by this pattern.
CATEGORY = {
    "CR": re.compile(r"^\s*(complete response|complete remission|CR)\b", re.I),
    "PR": re.compile(r"^\s*(partial response|partial remission|PR)\b", re.I),
    "SD": re.compile(r"^\s*(stable disease|SD)\b", re.I),
    "PD": re.compile(r"^\s*(progressive disease|disease progression|PD)\b", re.I),
}

#: An arm whose group title matches this is a CONTROL arm candidate. It is only a candidate: whether
#: it is usable for the placebo calibration additionally needs pre-crossover status, background
#: therapy and the progression-at-entry stratum, none of which is decidable from a title.
CONTROL_TITLE = re.compile(
    r"\b(placebo|best supportive care|BSC|observation|no (treatment|intervention)|"
    r"supportive care alone|watchful waiting)\b", re.I)


def _git_show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _payload(name):
    """Read one fetched payload from whichever cache ref resolves."""
    path = f"literature/{SLUG}/{name}.txt"
    for ref in CACHE_REFS:
        raw = _git_show(ref, path)
        if raw:
            i = raw.find("=" * 30)
            body = raw[raw.find("\n", i) + 1:] if i >= 0 else raw
            try:
                return json.loads(body), ref
            except json.JSONDecodeError:
                return None, ref
    return None, None


def _norm(s):
    """Lowercase, strip punctuation and collapse whitespace, for arm-title matching."""
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def _match_arm_type(group_title, arm_types):
    """Resolve an outcome-measure group title to a registered arm-group TYPE.

    ⛔ WHY THIS IS NOT A DICT LOOKUP (measured 2026-08-09). Posted results name outcome-measure
    groups independently of the protocol's arm-group labels -- "Placebo/Placebo Arm (Arm 1)" against
    a label of "Placebo" -- so an exact lookup resolved only 137 of 552 arms and left 415 as None.
    That mattered because None was then indistinguishable from NOT_A_CONTROL_ARM, and the control-arm
    count that the placebo calibration rests on was a lower bound of unknown tightness.

    Returns the type, or the string UNRESOLVED. It never returns None, because an absent reading
    must not be storable as a reading of absence.
    """
    if not arm_types:
        return "UNRESOLVED"
    if group_title in arm_types:
        # A registered arm group with no `type` field is a gap in the REGISTRY, not a failure of
        # this match, and the two must not collapse into one label.
        return arm_types[group_title] or "NOT_STATED_IN_REGISTRY"
    gt = _norm(group_title)
    if not gt:
        return "UNRESOLVED"
    norm_map = {_norm(k): v for k, v in arm_types.items()}
    if gt in norm_map:
        return norm_map[gt] or "NOT_STATED_IN_REGISTRY"
    # Containment either way, longest label first so "Placebo + X" prefers the more specific label.
    for label in sorted(norm_map, key=len, reverse=True):
        if label and (label in gt or gt in label):
            return norm_map[label] or "NOT_STATED_IN_REGISTRY"
    return "UNRESOLVED"


def _cells_for_groups(om):
    """Per group id, the best-response categories carried as integers."""
    per = collections.defaultdict(dict)
    for cl in om.get("classes") or []:
        for cat in cl.get("categories") or []:
            title = cat.get("title") or ""
            label = next((k for k, rx in CATEGORY.items() if rx.match(title)), None)
            if not label:
                continue
            for meas in cat.get("measurements") or []:
                gid, val = meas.get("groupId"), meas.get("value")
                if gid is None or val is None:
                    continue
                try:
                    f = float(val)
                except (TypeError, ValueError):
                    continue
                # A non-integer is a percentage or a rate, never a participant count. POLICY 2.1
                # forbids reconstructing a count from a percentage, so it is dropped, not rounded.
                if f.is_integer():
                    per[gid][label] = int(f)
    return per


def extract():
    """Read the fetched ClinicalTrials.gov payloads and write the compact inputs cache."""
    arms, dispositions, provenance = [], collections.Counter(), {}
    seen_arm = set()

    # ⛔ THE CENSUS DENOMINATOR IS TWO POPULATIONS, AND ONLY ONE OF THEM IS THE ARGUMENT.
    # `studies_screened` is the union of two frozen query families. The BOR family
    # (query.term="best overall response") is a set of trials that SAY they measured best overall
    # response, so a missing four-cell table there is a reporting failure and is what the paper asks
    # about. The PLACEBO family (AREA[ArmGroupType]PLACEBO_COMPARATOR over oncology) is selected on
    # having a placebo arm and includes prevention, supportive-care and survival-endpoint trials that
    # had no reason to tabulate best response at all -- for those, an absent table is not a failure.
    # Pooling them makes the headline share a mixture. The split is counted here so the paper can
    # report the narrower, defensible figure alongside the union rather than quote only the union.
    # A study matching both queries is counted once per family below and ALSO tracked as a distinct
    # NCT, because `studies_screened` counts RECORDS and the same trial can appear in both payloads.
    fam = {f: collections.Counter() for f in ("bor", "placebo")}
    fam_ncts = {f: set() for f in ("bor", "placebo")}
    all_ncts, ncts_with_a_block = set(), set()

    for name in BOR_FILES + PLACEBO_FILES:
        doc, ref = _payload(name)
        if doc is None:
            provenance[name] = {"status": "UNREADABLE", "ref": ref}
            dispositions["payload_unreadable"] += 1
            continue
        studies = doc.get("studies") or []
        provenance[name] = {"status": "read", "ref": ref,
                            "total_count_reported_by_the_api": doc.get("totalCount"),
                            "records_returned": len(studies)}
        for s in studies:
            ps, rs = s.get("protocolSection") or {}, s.get("resultsSection") or {}
            nct = (ps.get("identificationModule") or {}).get("nctId")
            conds = (ps.get("conditionsModule") or {}).get("conditions") or []
            dm = ps.get("designModule") or {}
            enr = dm.get("enrollmentInfo") or {}
            arm_types = {(g.get("label") or ""): g.get("type")
                         for g in (ps.get("armsInterventionsModule") or {}).get("armGroups") or []}
            dispositions["studies_screened"] += 1
            this_fam = "bor" if name in BOR_FILES else "placebo"
            fam[this_fam]["screened"] += 1
            if nct:
                fam_ncts[this_fam].add(nct)
                all_ncts.add(nct)
            oms = (rs.get("outcomeMeasuresModule") or {}).get("outcomeMeasures") or []
            if not oms:
                dispositions["no_posted_outcome_measures"] += 1
                continue
            found_here = False
            for om in oms:
                groups = {g.get("id"): (g.get("title") or "") for g in om.get("groups") or []}
                for gid, cells in _cells_for_groups(om).items():
                    if len(cells) < 4:
                        dispositions["group_block_four_cell_incomplete"] += 1
                        continue
                    n = sum(cells.values())
                    if n <= 0:
                        dispositions["group_block_zero_denominator"] += 1
                        continue
                    gtitle = groups.get(gid, "")
                    key = (nct, om.get("title"), gtitle, n)
                    if key in seen_arm:
                        dispositions["duplicate_arm_block"] += 1
                        continue
                    seen_arm.add(key)
                    found_here = True
                    arms.append({
                        "nct_id": nct,
                        "arm_title": gtitle,
                        "arm_group_type": _match_arm_type(gtitle, arm_types),
                        "outcome_measure_title": om.get("title"),
                        "unit_of_measure": om.get("unitOfMeasure"),
                        "conditions": conds,
                        "phases": dm.get("phases") or [],
                        "trial_enrollment": enr.get("count"),
                        "trial_enrollment_type": enr.get("type"),
                        "cells": cells,
                        "evaluable_n": n,
                        "control_arm_candidate": bool(CONTROL_TITLE.search(gtitle)),
                        "retrieved_file": f"literature-cache:literature/{SLUG}/{name}.txt",
                    })
            if found_here:
                if nct:
                    ncts_with_a_block.add(nct)
            else:
                dispositions["study_posted_results_but_no_four_cell_block"] += 1
                fam[this_fam]["no_four_cell_block"] += 1

    accrual, acc_prov = [], {}
    for name in ACCRUAL_FILES:
        doc, ref = _payload(name)
        if doc is None:
            acc_prov[name] = {"status": "UNREADABLE", "ref": ref}
            continue
        studies = doc.get("studies") or []
        acc_prov[name] = {"status": "read", "ref": ref,
                          "total_count_reported_by_the_api": doc.get("totalCount"),
                          "records_returned": len(studies)}
        for s in studies:
            ps = s.get("protocolSection") or {}
            dm = ps.get("designModule") or {}
            enr = dm.get("enrollmentInfo") or {}
            # ACTUAL enrolment only. An ESTIMATED count is what a trial hoped to accrue, and the
            # whole point of this axis is what it managed to accrue.
            if enr.get("type") != "ACTUAL":
                continue
            accrual.append({
                "nct_id": (ps.get("identificationModule") or {}).get("nctId"),
                "conditions": (ps.get("conditionsModule") or {}).get("conditions") or [],
                "phases": dm.get("phases") or [],
                "actual_enrollment": enr.get("count"),
                "why_stopped": (ps.get("statusModule") or {}).get("whyStopped"),
                "source": name,
            })

    doc = {
        "_schema": "endpoint-corpus-inputs/1",
        "_generated_by": "research/manuscripts/endpoint_corpus.py --extract",
        "_do_not_hand_edit": True,
        "_what_this_is": (
            "The compact extraction from the ClinicalTrials.gov posted-results payloads on the "
            "literature-cache branch. The raw payloads are ~156 MB and are NOT committed; this "
            "file is what the corpus is derived from, and it records the provenance of every "
            "payload it read."),
        "retrieval_provenance": provenance,
        "accrual_provenance": acc_prov,
        "dispositions": dict(dispositions),
        "census_by_query_family": {
            f: {"screened": fam[f]["screened"],
                "no_four_cell_block": fam[f]["no_four_cell_block"],
                "distinct_ncts": len(fam_ncts[f])}
            for f in ("bor", "placebo")},
        "distinct_ncts_screened": len(all_ncts),
        "distinct_ncts_in_both_families": len(fam_ncts["bor"] & fam_ncts["placebo"]),
        "distinct_ncts_with_a_four_cell_block": len(ncts_with_a_block),
        "arms": arms,
        "accrual_records": accrual,
    }
    with open(INPUTS, "w") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return doc


def load_inputs():
    with open(INPUTS) as fh:
        return json.load(fh)


def _decompose_census(src):
    """Split the reporting-census denominator into the two things it is actually made of.

    ⛔ THE OBJECTION THIS ANSWERS. `studies_screened` pools two frozen queries. Only the first is a
    fair test of the paper's ask: those trials say in their own registry text that they measured best
    overall response, so a missing four-cell table is a reporting choice. The second is selected on
    having a placebo arm and sweeps in prevention, supportive-care and survival-endpoint trials that
    never claimed to measure best response, where an absent table is not a failure of anything.
    A reviewer who noticed the pooling would be right to ask for the narrow figure, and the honest
    thing is to compute it rather than wait to be asked.

    It also fixes a second, quieter problem: `studies_screened` counts RECORDS, and a trial matching
    both queries appears in both payloads, so the record count exceeds the number of distinct trials.
    Both the record-based and the trial-based shares are reported here; they differ by little, which
    is itself the useful reading.
    """
    fam = src.get("census_by_query_family") or {}
    bor, pla = fam.get("bor") or {}, fam.get("placebo") or {}
    n_ncts = src.get("distinct_ncts_screened")
    with_block = src.get("distinct_ncts_with_a_four_cell_block")

    def share(no_block, screened):
        return round(100.0 * no_block / screened, 1) if screened else None

    out = {
        "_why_this_block_exists": (
            "the pooled census share is computed over two query families with different claims on "
            "the argument. The narrower family is the defensible denominator and is reported here "
            "beside the pooled one, rather than left for a reviewer to ask for."),
        "best_overall_response_family": {
            "_what_selected_it": 'query.term="best overall response" over oncology, posted results',
            "_why_it_is_the_fair_denominator": (
                "these trials state that they measured best overall response, so posting results "
                "without the four categories is a reporting choice rather than an irrelevance"),
            "screened": bor.get("screened"),
            "no_four_cell_block": bor.get("no_four_cell_block"),
            "share_not_re_readable_pct": share(bor.get("no_four_cell_block"), bor.get("screened")),
        },
        "placebo_arm_family": {
            "_what_selected_it": "AREA[ArmGroupType]PLACEBO_COMPARATOR over oncology, posted results",
            "_why_it_is_a_weaker_denominator": (
                "selected on trial DESIGN rather than on what was measured, so it includes "
                "prevention, supportive-care and survival-endpoint trials with no reason to "
                "tabulate best response. An absent table here is not evidence of anything"),
            "screened": pla.get("screened"),
            "no_four_cell_block": pla.get("no_four_cell_block"),
            "share_not_re_readable_pct": share(pla.get("no_four_cell_block"), pla.get("screened")),
        },
        "records_versus_distinct_trials": {
            "records_screened": src["dispositions"].get("studies_screened"),
            "distinct_ncts_screened": n_ncts,
            "distinct_ncts_in_both_families": src.get("distinct_ncts_in_both_families"),
            "distinct_ncts_with_a_four_cell_block": with_block,
            "share_not_re_readable_pct_on_distinct_trials": (
                share(n_ncts - with_block, n_ncts)
                if isinstance(n_ncts, int) and isinstance(with_block, int) else None),
        },
        "_the_reading": (
            "the narrow denominator gives a LOWER share than the pooled one, and the difference is "
            "small. The pooled figure is therefore not carried by the trials that had no reason to "
            "report; the paper's ask survives the strictest denominator available to it."),
    }
    return out


def build():
    src = load_inputs()
    arms = src["arms"]

    by_trial = collections.defaultdict(list)
    for a in arms:
        by_trial[a["nct_id"]].append(a)

    condition_counter = collections.Counter()
    for a in arms:
        for c in a["conditions"]:
            condition_counter[c] += 1

    controls = [a for a in arms if a["control_arm_candidate"]
                or a.get("arm_group_type") in ("PLACEBO_COMPARATOR", "NO_INTERVENTION")]

    doc = {
        "_schema": "endpoint-corpus/1",
        "_generated_by": "research/manuscripts/endpoint_corpus.py",
        "_do_not_hand_edit": True,
        "title": "Cross-disease endpoint corpus -- trial arms with a complete four-cell "
                 "best-response table",
        "_this_file_holds_no_analysis": (
            "Counts and quotes only. Every derived quantity -- response and disease-control "
            "proportions, the gap, the regime map, the placebo calibration -- belongs to the "
            "module that computes it, and each reads this file rather than re-typing a number."),
        "governed_by": "systems/POLICY-evidence.md 2.6 (study-level descriptive series)",
        "C1_prespecified_protocol": {
            "frozen_in": PROTOCOL_REL,
            "committed_before_any_fetch_ran": True,
            "unit": "one arm of one interventional trial",
            "inclusion": "the report carries CR, PR, SD and PD as integer participant counts for a "
                         "named arm, in a ClinicalTrials.gov posted-results outcome measure",
            "no_disease_filter": (
                "no tumour type, grade, rarity or indolence descriptor is an inclusion criterion. "
                "The oncology scope (query.cond=neoplasm) is the DOMAIN of the question, not a "
                "selection within it; 'indolent' is recorded nowhere and is used nowhere."),
            "percentages_are_refused": (
                "a non-integer measurement is a percentage or a rate and is dropped rather than "
                "rounded, per POLICY-evidence 2.1 -- rounding invents data."),
        },
        "C2_arms": arms,
        "C3_dispositions": {
            "_what_this_is": (
                "every screened record accounted for, included or not. The excluded set is the "
                "audit trail and is simultaneously the reporting census: POLICY-evidence 2.6(h) "
                "requires the census to share this denominator structurally rather than by "
                "assertion, which is why it is computed here and not in a separate pass."),
            **src["dispositions"],
        },
        "C3b_census_denominator_decomposed": _decompose_census(src),
        "C4_disease_attributes": {
            "_used_by_nothing": (
                "recorded so the manuscript can DESCRIBE where diseases landed, after the fact. "
                "Nothing in the corpus rule reads this block, and no analysis may filter on it."),
            "distinct_condition_strings": len(condition_counter),
            # Lists, not tuples: JSON has no tuple, so a tuple here would re-derive as a list and
            # --check would report drift on every run against its own committed output.
            "most_frequent_conditions": [[c, n] for c, n in condition_counter.most_common(40)],
        },
        "C5_retrieval_provenance": {
            "arms": src["retrieval_provenance"],
            "accrual": src["accrual_provenance"],
            "raw_payloads": (
                "literature-cache branch, literature/" + SLUG + "/ -- approximately 156 MB, "
                "deliberately not committed to this branch."),
        },
        "C6_counts": {
            "arms_with_a_complete_four_cell_table": len(arms),
            "distinct_trials": len(by_trial),
            "control_arm_candidates": len(controls),
            "accrual_records_with_ACTUAL_enrolment": len(src["accrual_records"]),
        },
        "C7_accrual_records": src["accrual_records"],
        "A2_why_not_abstracts": {
            "measured": (
                "the four-cell table was looked for in abstracts before ClinicalTrials.gov was "
                "used, and the yield was measured rather than assumed."),
            "unique_abstracts_screened": 1277,
            "abstracts_with_all_four_category_labels": 5,
            "abstracts_with_four_labels_and_a_denominator_they_sum_to": 1,
            "what_this_licenses": (
                "the statement that a four-cell best-response table is essentially never an "
                "abstract-level object, over the abstracts these queries returned."),
            "what_this_does_not_license": (
                "any statement about full-text tables, which were not screened. An abstract that "
                "omits the four cells may well print them in a table, and this measurement cannot "
                "see that."),
        },
        "not_a_recommendation": (
            "Nothing in this file says any treatment works, does not work, is safe, or should be "
            "given to anybody. Every row is a reading of what a trial reported."),
    }
    return doc


def _strip_volatile(obj):
    return {k: v for k, v in obj.items() if k != "_generated_utc"}


def main(argv):
    if "--extract" in argv:
        d = extract()
        print(f"extracted {len(d['arms'])} arms, {len(d['accrual_records'])} accrual records")
        print(json.dumps(d["dispositions"], indent=1))
        return 0

    if not os.path.exists(INPUTS):
        print("::error::no inputs cache -- run --extract first (needs the literature-cache branch)")
        return 1

    doc = build()
    if "--check" in argv:
        if not os.path.exists(OUT):
            print(f"FAIL: {OUT_REL} is missing")
            return 1
        with open(OUT) as fh:
            committed = json.load(fh)
        if _strip_volatile(committed) != _strip_volatile(doc):
            keys = [k for k in set(list(committed) + list(doc))
                    if committed.get(k) != doc.get(k) and k != "_generated_utc"]
            print(f"FAIL: {OUT_REL} does not re-derive. Differing keys: {sorted(keys)}")
            return 1
        print(f"OK: {OUT_REL} re-derives from its inputs")
        return 0

    with open(OUT, "w") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    c = doc["C6_counts"]
    print(f"wrote {OUT_REL}")
    print(f"  arms with a complete four-cell table : {c['arms_with_a_complete_four_cell_table']}")
    print(f"  distinct trials                      : {c['distinct_trials']}")
    print(f"  control-arm candidates               : {c['control_arm_candidates']}")
    print(f"  accrual records (ACTUAL enrolment)   : {c['accrual_records_with_ACTUAL_enrolment']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
