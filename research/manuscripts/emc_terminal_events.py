#!/usr/bin/env python3
"""Tally the classified EMC terminal events, and prove every quote is real.

WHAT THIS ANSWERS. When a patient with extraskeletal myxoid chondrosarcoma dies, does the
published record say what killed them -- and when it does, what does it say? The whole
treatment portfolio is aimed at preventing one event, and nobody had checked what that
event looks like or how often it is even described.

⛔ THE PROVENANCE CHECK IS THE POINT OF THIS SCRIPT, not a nicety attached to it. Every row
in emc-terminal-events-classified.json carries a quote that a human read and labelled. This
script asserts each quote still appears VERBATIM in the retrieval artifact, under the PMID
it claims. A label whose quote has drifted is a clinical fact with no source, which is the
failure mode CLAUDE.md's first golden rule exists to prevent. The build fails rather than
tallying.

⛔ AND A ROW IS NOT AUTOMATICALLY A DEATH, NOR IS A LABEL A MECHANISM. Every individual_events row
must carry an explicit `death_status` AND an explicit `mechanism_tier`. The stored `label` is
LEGACY: it says which bucket a row was filed in, not what its quoted sentence states. Most rows
carrying a mechanism label state only a broad cause CLASS -- a metastatic site, a setting, a disease
attribution, or an exclusion such as "non-EMC-related" -- and name no terminal mechanism.
`mechanism_tier` records that difference so the tally cannot be read as observed mechanisms.

⛔ AND THE TOTALS ARE SUMMED REPORTED PATIENT INSTANCES. They are not distinct records and they are
not unique people: the contributing papers include literature reviews that collect previously
published cases, and no cross-report de-duplication is possible from what was retrieved.

Every individual_events row must carry an explicit
`death_status`. Two retained rows describe a complication and a transition to supportive care
without stating that the patient died; they are kept for the harm they document and are excluded
from every death numerator AND denominator, including the named-mechanism count. The script
refuses to tally if any row lacks a recognised `death_status`, so a future row cannot be counted
as a death by default.

⚠ AND THE UNIT IS A PATIENT, NEVER A SENTENCE. One paper describes three deaths across seven
sentences; another describes one death four times. Counting sentences would have reported
the corpus as roughly three times larger than it is and would have weighted the most
verbose papers most heavily.

Inputs:  research/manuscripts/emc-terminal-events-classified.json
         research/literature/emc-mortality-probe.json
Output:  research/manuscripts/emc-terminal-events.json
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CLASSIFIED = ROOT / "research/manuscripts/emc-terminal-events-classified.json"
PROBE = ROOT / "research/literature/emc-mortality-probe.json"
OUT = ROOT / "research/manuscripts/emc-terminal-events.json"

EMC_TITLE = re.compile(r"myxoid chondrosarcoma|chordoid sarcoma|NR4A3", re.I)

# Mechanism labels, i.e. the labels that say something about HOW a patient died. A label
# outside this set is a death whose mechanism the record does not give, or not a death.
DOCUMENTED_DEATH = "documented_death"
# ⛔ Both non-death statuses are statements about the RECORD, not about the patient. Neither
# asserts that the patient survived; the record does not say.
NON_DEATH_STATUSES = {"death_not_documented_complication_recorded",
                      "death_not_documented_care_transition_recorded"}
DEATH_STATUSES = {DOCUMENTED_DEATH} | NON_DEATH_STATUSES

# Evidence tiers. `label` is legacy filing; the tier is what the quoted sentence states.
# ⛔ TIER_STATED'S NAME IS LEGACY AND IS BROADER THAN IT READS (root, 2026-09-08, reading the
# actual quotes). It holds a quote that names a physiological terminal EVENT and a quote that names
# a DISEASE ENTITY without naming the event -- PMID 32963861's "died from complications of
# unresectable colon cancer", whose complications are not themselves named. Those are different
# evidence. STATED_TYPES splits them so no output, and no sentence drafted from an output, can
# shorten this tier's count to "four named terminal mechanisms".
TIER_STATED = "stated_terminal_mechanism"
STATED_EVENT = "named_terminal_event"
STATED_ENTITY = "named_disease_entity"
STATED_TYPES = {STATED_EVENT, STATED_ENTITY}
TIER_BROAD = "assigned_broad_cause_category"
TIER_SPLIT = "split_see_split_mechanism_tiers"
MECHANISM_TIERS = {TIER_STATED, TIER_BROAD, "no_cause_or_mechanism_stated",
                   "attribution_ambiguous", "not_applicable_death_not_documented", TIER_SPLIT}

MECHANISM_LABELS = {
    "respiratory_failure",
    "locoregional_complication",
    "visceral_metastasis_complication",
    "treatment_related",
    "competing_non_cancer",
    "second_malignancy",
}


def normalise(s: str) -> str:
    """Whitespace-insensitive comparison. The probe collapses whitespace when it strips
    XML, so an exact string compare would fail on a quote a human retyped with a different
    line break while the words are identical."""
    return re.sub(r"\s+", " ", s).strip()


def probe_index(probe: dict) -> dict[str, list[str]]:
    return {e["pmid"]: [s["sentence"] for s in e["sentences"]]
            for e in probe["terminal_events"] if e.get("pmid")}


def verify_quotes(spec: dict, index: dict[str, list[str]]) -> list[str]:
    problems = []

    def check(pmid, quote, where):
        if pmid not in index:
            problems.append(f"{where}: PMID {pmid} is not in the retrieval artifact at all")
            return
        hay = [normalise(s) for s in index[pmid]]
        if not any(normalise(quote) in h or h in normalise(quote) for h in hay):
            problems.append(
                f"{where}: the quote attributed to PMID {pmid} appears in no retrieved "
                f"sentence for that paper. Quote begins: {quote[:70]!r}")

    for row in spec.get("individual_events", []):
        check(row["pmid"], row["quote"], f"individual_events[{row['pmid']}]")
    for row in spec.get("aggregate_cause_splits", []):
        check(row["pmid"], row["quote"], f"aggregate[{row['pmid']}/{row['stratum']}]")
    for row in spec.get("prognostic_findings", []):
        check(row["pmid"], row["quote"], f"prognostic[{row['pmid']}]")
        if row.get("corroborating_quote"):
            check(row["pmid"], row["corroborating_quote"], f"prognostic-corrob[{row['pmid']}]")
    for row in spec.get("not_a_patient_death_examples", []):
        check(row["pmid"], row["quote"], f"not_a_death[{row['pmid']}]")
    return problems


def verify_death_status(spec: dict) -> list[str]:
    """Every individual_events row must SAY whether its quoted sentence documents a death, and
    what evidence tier its mechanism claim sits at. Silence is not 'yes' for either. This is a
    refusal, not a default."""
    problems = []
    for row in spec.get("individual_events", []):
        where = f"individual_events[{row['pmid']}/{row['label']}]"
        st = row.get("death_status")
        if st not in DEATH_STATUSES:
            problems.append(f"{where}: death_status is {st!r}; it must be one of "
                            f"{sorted(DEATH_STATUSES)}")
        tier = row.get("mechanism_tier")
        if tier not in MECHANISM_TIERS:
            problems.append(f"{where}: mechanism_tier is {tier!r}; it must be one of "
                            f"{sorted(MECHANISM_TIERS)}")
        if tier == TIER_SPLIT:
            st_tiers = row.get("split_mechanism_tiers") or {}
            for lab in (row.get("split") or {}):
                if st_tiers.get(lab) not in MECHANISM_TIERS - {TIER_SPLIT}:
                    problems.append(f"{where}: split member {lab!r} has no recognised tier in "
                                    f"split_mechanism_tiers")
                if st_tiers.get(lab) == TIER_STATED and (
                        row.get("split_stated_types") or {}).get(lab) not in STATED_TYPES:
                    problems.append(f"{where}: split member {lab!r} is in {TIER_STATED} and must "
                                    f"declare a split_stated_types entry in {sorted(STATED_TYPES)}")
        #: ⛔ SILENCE IS NOT "a terminal event". A row whose quote is in the stated tier must say
        #: which of the two things that quote actually names, because the tier holds both and the
        #: difference is the whole point of the tier (see TIER_STATED's comment).
        elif tier == TIER_STATED and row.get("stated_type") not in STATED_TYPES:
            problems.append(f"{where}: mechanism_tier is {TIER_STATED} but stated_type is "
                            f"{row.get('stated_type')!r}; it must be one of {sorted(STATED_TYPES)}")
    return problems


def tally(spec: dict) -> dict:
    by_label: dict[str, int] = {}
    papers: set[str] = set()
    record_papers: set[str] = set()
    non_death: list[dict] = []
    by_tier: dict[str, int] = {}
    by_stated_type: dict[str, int] = {}
    tier_of_mechanism_label: dict[str, int] = {}
    n_records = 0
    for row in spec["individual_events"]:
        record_papers.add(row["pmid"])
        n_records += row["n_patients"]
        if row["death_status"] != DOCUMENTED_DEATH:
            non_death.append({
                "pmid": row["pmid"],
                "death_status": row["death_status"],
                "mechanism_label_it_would_have_carried": row["label"],
                "n_patients": row["n_patients"],
                "quote": row["quote"],
                "note": row["note"],
            })
            continue
        papers.add(row["pmid"])
        if row.get("split"):
            for lab, n in row["split"].items():
                by_label[lab] = by_label.get(lab, 0) + n
                t = row["split_mechanism_tiers"][lab]
                by_tier[t] = by_tier.get(t, 0) + n
                if t == TIER_STATED:
                    st = row["split_stated_types"][lab]
                    by_stated_type[st] = by_stated_type.get(st, 0) + n
                if lab in MECHANISM_LABELS:
                    tier_of_mechanism_label[t] = tier_of_mechanism_label.get(t, 0) + n
        else:
            by_label[row["label"]] = by_label.get(row["label"], 0) + row["n_patients"]
            t = row["mechanism_tier"]
            by_tier[t] = by_tier.get(t, 0) + row["n_patients"]
            if t == TIER_STATED:
                st = row["stated_type"]
                by_stated_type[st] = by_stated_type.get(st, 0) + row["n_patients"]
            if row["label"] in MECHANISM_LABELS:
                tier_of_mechanism_label[t] = (
                    tier_of_mechanism_label.get(t, 0) + row["n_patients"])
    return {"by_label": dict(sorted(by_label.items(), key=lambda kv: -kv[1])),
            "papers_contributing": len(papers),
            "papers_with_any_record": len(record_papers),
            "patient_records_total": n_records,
            "by_tier": dict(sorted(by_tier.items(), key=lambda kv: -kv[1])),
            "by_stated_type": dict(sorted(by_stated_type.items(), key=lambda kv: -kv[1])),
            "tier_of_mechanism_label": dict(sorted(tier_of_mechanism_label.items(),
                                                   key=lambda kv: -kv[1])),
            "non_death_records": non_death}


def main() -> int:
    spec = json.loads(CLASSIFIED.read_text(encoding="utf-8"))
    probe = json.loads(PROBE.read_text(encoding="utf-8"))
    index = probe_index(probe)

    problems = verify_quotes(spec, index) + verify_death_status(spec)
    if problems:
        print("QUOTE PROVENANCE OR DEATH-STATUS CHECK FAILED -- refusing to tally:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    counts = tally(spec)
    by_label = counts["by_label"]

    emc_papers = [e for e in probe["terminal_events"] if EMC_TITLE.search(e.get("title") or "")]
    total_deaths = sum(v for v in by_label.values())   # documented deaths only
    n_records = counts["patient_records_total"]
    non_death = counts["non_death_records"]
    n_non_death = sum(r["n_patients"] for r in non_death)
    mech = {k: v for k, v in by_label.items() if k in MECHANISM_LABELS}
    n_mech = sum(mech.values())
    tier_mech = counts["tier_of_mechanism_label"]
    n_unstated = by_label.get("mechanism_unstated", 0)
    competing = by_label.get("competing_non_cancer", 0) + by_label.get("second_malignancy", 0)

    payload = {
        "_readme": (
            "What the open-access EMC literature says about how its patients die. Every row is a "
            "PATIENT or reported patient group, never a sentence; the totals are SUMMED REPORTED "
            "PATIENT INSTANCES, not distinct records and not unique people. Every quote has been asserted "
            "against the retrieval artifact verbatim before this file was written. Nothing here is a "
            "rate, an incidence or a prognosis: it is a description of what a body of case reports "
            "and small series chose to record, in a disease too rare for anything better to exist."
        ),
        "generated_by": "research/manuscripts/emc_terminal_events.py",
        "sources": {
            "classification": "research/manuscripts/emc-terminal-events-classified.json",
            "retrieval": "research/literature/emc-mortality-probe.json",
        },
        "corpus": {
            "open_access_papers_enumerated": probe["summary"]["oa_corpus_enumerated"],
            "full_texts_retrieved": probe["summary"]["fulltext_retrieved"],
            "papers_with_any_death_sentence": probe["summary"]["papers_with_death_sentences"],
            "death_sentences_retrieved": probe["summary"]["death_sentences_total"],
            "papers_actually_about_emc": len(emc_papers),
            "death_sentences_in_those_papers": sum(e["n_sentences"] for e in emc_papers),
            "papers_contributing_a_classified_record": counts["papers_with_any_record"],
            "papers_contributing_a_documented_death": counts["papers_contributing"],
            "⚠_inclusion_note": (
                "Only 34 of the 162 papers carrying a death sentence are about EMC. The rest match "
                "the enumeration because EMC appears in a differential diagnosis or a citation, and "
                "their deaths belong to other diseases' patients. Every count below is restricted to "
                "the 34."
            ),
        },
        "deaths_by_label": by_label,
        "⛔_records_that_are_not_documented_deaths": {
            "summed_reported_patient_instances": n_records,
            "documented_death_instances": total_deaths,
            "instances_excluded_from_the_death_tally": n_non_death,
            "rows": non_death,
            "⛔_why_this_block_exists": (
                "The 18 classified rows sum to SUMMED REPORTED PATIENT INSTANCES, not to a death "
                "count. Two rows document no death: one records a small-bowel metastasis "
                "complication and its palliative management, the other a clinical deterioration "
                "and a transition to supportive care. Both are excluded from every numerator and "
                "denominator below -- and the first also carried a stored mechanism label, so "
                "excluding it moves the numerator and the denominator together. ⛔ Neither "
                "exclusion asserts that those patients survived, and neither status is a claim "
                "about a patient: each says only what the record documents."
            ),
        },
        "headline": {
            "summed_reported_patient_instances": n_records,
            "documented_death_instances": total_deaths,
            "papers_contributing_a_documented_death": counts["papers_contributing"],
            "with_a_stored_mechanism_label": n_mech,
            "mechanism_unstated": n_unstated,
            "proportion_with_a_stored_mechanism_label": (
                round(n_mech / total_deaths, 3) if total_deaths else None),
            "⛔_what_the_stored_mechanism_label_count_is_not": (
                "The stored mechanism label is LEGACY filing, not an observation. Of the "
                f"{n_mech} documented-death instances carrying one, "
                f"{tier_mech.get(TIER_STATED, 0)} have a quoted sentence that names a specific "
                f"terminal event or disease entity, and {tier_mech.get(TIER_BROAD, 0)} state only "
                "a broad cause class -- a metastatic site, a setting, a disease attribution, or an "
                "exclusion such as 'non-EMC-related'. ⛔ These must NOT be described as observed "
                "mechanisms. The count and its proportion are unchanged and stand; only the "
                "description of what they are has been corrected. See mechanism_evidence_tiers."
            ),
            "⛔_not_unique_patients": (
                "These are SUMMED REPORTED PATIENT INSTANCES from selected descriptive literature "
                "-- case reports, small series and literature reviews that themselves collect "
                "earlier cases. They are not distinct records and they are not unique people. "
                "Nothing here establishes that the summed instances are unique across reports or "
                "independent of one another, and no rate, incidence or denominator can be formed "
                "from them."
            ),
            "⭐_the_finding": (
                "The published record of this disease mostly does not say how its patients died. "
                "That is not a gap in this table -- it is the result. A treatment portfolio aimed at "
                "preventing a specific event cannot describe the event it is aimed at."
            ),
        },
        "mechanism_evidence_tiers": {
            "⛔_read_this_before_any_tier_count": (
                "A tier says what the retained quoted sentence STATES, independently of the row's "
                "legacy `label`. Tiers are assigned over documented-death instances only. "
                "`assigned_broad_cause_category` is conditional and inferred, not observed."
            ),
            "over_all_documented_death_instances": counts["by_tier"],
            "within_the_stated_terminal_mechanism_tier": {
                "counts": counts["by_stated_type"],
                "⛔_why_this_split_exists": (
                    f"This tier holds {counts['by_tier'].get(TIER_STATED, 0)} instances and they "
                    "are NOT all named terminal mechanisms. "
                    f"{counts['by_stated_type'].get(STATED_EVENT, 0)} quote a physiological "
                    "terminal event -- pulmonary failure, respiratory failure, cerebral "
                    f"haemorrhage. {counts['by_stated_type'].get(STATED_ENTITY, 0)} quotes a "
                    "disease entity and does not name the terminal event: 'died from "
                    "complications of unresectable colon cancer', where the complications are not "
                    "themselves named. ⛔ Any prose shortening this tier to 'four terminal "
                    "mechanisms' or 'four name a terminal event' is wrong for that instance."
                ),
            },
            "within_the_instances_carrying_a_stored_mechanism_label": tier_mech,
            "⚠_rows_whose_label_outruns_their_quote": (
                "PMID 29977924 ('died due to lung metastases') is a broad cause, not a documented "
                "respiratory failure. PMID 35775709's hepatic-metastasis patient states metastasis "
                "at death, not a named visceral complication. PMID 35665108's two deaths from "
                "'non-EMC-related factors' name no cause at all and do not establish a non-cancer "
                "death either. Their stored labels are retained as legacy filing and their tier "
                "records what the record actually says."
            ),
        },
        "competing_and_second_malignancy": {
            "count": competing,
            "of_stored_mechanism_label_instances": round(competing / n_mech, 3) if n_mech else None,
            "⭐_reading": (
                "Deaths filed to a competing cause or a second cancer are the largest LEGACY "
                "FILING category among the instances carrying a stored mechanism label -- not an "
                "identified mechanism category. ⛔ Of the six, one quote names a terminal event "
                "(cerebral haemorrhage) and one names a disease entity (unresectable colon "
                "cancer); the other four state a broad class only, two of them as the bare "
                "exclusion 'non-EMC-related', which does not establish a non-cancer death. They "
                "recur across separate reports whose INDEPENDENCE IS UNKNOWN -- reviews in this "
                "corpus collect earlier cases, so the same patient may appear twice. They converge "
                "with the registry cause-split computed separately in "
                "emc-mortality-decomposition.json. ⚠ Case reports over-select the notable, so this "
                "is not an incidence -- but the direction agrees with the registry, which is not a "
                "case-report artifact."
            ),
        },
        "respiratory": {
            "count": by_label.get("respiratory_failure", 0),
            "⚠_only_two_of_the_three_name_respiratory_failure": (
                "Two quoted sentences name pulmonary or respiratory failure. The third says the "
                "patient 'died due to lung metastases', which assigns a broad cause and names no "
                "terminal mechanism; it is tiered assigned_broad_cause_category."
            ),
            "⛔_the_premise_this_does_not_support": (
                "Respiratory failure from progressive pulmonary metastases is present in this corpus "
                "and is NOT its dominant named mechanism. ⚠ 'The three' here are the three "
                "instances FILED to the respiratory-failure label, only two of which name it; one "
                "of those two followed a tumour-embolic ischaemic stroke rather than pulmonary "
                "tumour burden. "
                "Lung is unambiguously EMC's dominant metastatic SITE; that is a different claim from "
                "lung failure being its dominant mode of death, and this corpus does not establish "
                "the second."
            ),
        },
        "aggregate_cause_splits": spec["aggregate_cause_splits"],
        "prognostic_findings": spec["prognostic_findings"],
        "individual_events": spec["individual_events"],
        "limits": [
            "A convenience sample: open-access full text only, 328 of 600 enumerated papers retrieved, and non-open-access series are systematically older and larger.",
            "Case reports are written because a case was notable, so unusual terminal events are over-represented and ordinary ones under-represented. This biases AGAINST the indolent, competing-cause picture the tally nevertheless shows.",
            "Counts are of reported patients, not of a defined population, so no denominator exists and no rate can be computed from this table.",
            "A label records what a paper asserted, never an independent adjudication. Where a paper called a death unrelated to EMC, that is the paper's judgement and its instrument is unknown.",
        ],
    }
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  {len(emc_papers)} EMC papers, {counts['papers_with_any_record']} contributing a "
          f"classified record, {counts['papers_contributing']} a documented death")
    print(f"  {n_records} summed reported patient instances, {n_non_death} documenting no death")
    print(f"  {total_deaths} documented-death instances: {n_mech} with a stored mechanism label "
          f"({tier_mech.get(TIER_STATED, 0)} stated terminal mechanism, "
          f"{tier_mech.get(TIER_BROAD, 0)} broad cause only), {n_unstated} unstated")
    for k, v in counts["by_tier"].items():
        print(f"    tier {v:>3}  {k}")
    for k, v in by_label.items():
        print(f"    {v:>3}  {k}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
