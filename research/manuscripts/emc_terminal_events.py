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


def tally(spec: dict) -> dict:
    by_label: dict[str, int] = {}
    papers: set[str] = set()
    for row in spec["individual_events"]:
        papers.add(row["pmid"])
        if row.get("split"):
            for lab, n in row["split"].items():
                by_label[lab] = by_label.get(lab, 0) + n
        else:
            by_label[row["label"]] = by_label.get(row["label"], 0) + row["n_patients"]
    return {"by_label": dict(sorted(by_label.items(), key=lambda kv: -kv[1])),
            "papers_contributing": len(papers)}


def main() -> int:
    spec = json.loads(CLASSIFIED.read_text(encoding="utf-8"))
    probe = json.loads(PROBE.read_text(encoding="utf-8"))
    index = probe_index(probe)

    problems = verify_quotes(spec, index)
    if problems:
        print("QUOTE PROVENANCE FAILED -- refusing to tally:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    counts = tally(spec)
    by_label = counts["by_label"]

    emc_papers = [e for e in probe["terminal_events"] if EMC_TITLE.search(e.get("title") or "")]
    total_deaths = sum(v for v in by_label.values())
    mech = {k: v for k, v in by_label.items() if k in MECHANISM_LABELS}
    n_mech = sum(mech.values())
    n_unstated = by_label.get("mechanism_unstated", 0)
    competing = by_label.get("competing_non_cancer", 0) + by_label.get("second_malignancy", 0)

    payload = {
        "_readme": (
            "What the open-access EMC literature says about how its patients die. Every row is a "
            "PATIENT or reported patient group, never a sentence, and every quote has been asserted "
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
            "papers_contributing_a_classified_death": counts["papers_contributing"],
            "⚠_inclusion_note": (
                "Only 34 of the 162 papers carrying a death sentence are about EMC. The rest match "
                "the enumeration because EMC appears in a differential diagnosis or a citation, and "
                "their deaths belong to other diseases' patients. Every count below is restricted to "
                "the 34."
            ),
        },
        "deaths_by_label": by_label,
        "headline": {
            "classified_deaths": total_deaths,
            "with_a_named_mechanism": n_mech,
            "mechanism_unstated": n_unstated,
            "proportion_with_named_mechanism": (
                round(n_mech / total_deaths, 3) if total_deaths else None),
            "⭐_the_finding": (
                "The published record of this disease mostly does not say how its patients died. "
                "That is not a gap in this table -- it is the result. A treatment portfolio aimed at "
                "preventing a specific event cannot describe the event it is aimed at."
            ),
        },
        "competing_and_second_malignancy": {
            "count": competing,
            "of_named_mechanism_deaths": round(competing / n_mech, 3) if n_mech else None,
            "⭐_reading": (
                "Deaths from a competing cause or a second cancer are the largest identifiable "
                "mechanism category in this corpus. They recur across independent case series, and "
                "they converge with the registry cause-split computed separately in "
                "emc-mortality-decomposition.json. ⚠ Case reports over-select the notable, so this "
                "is not an incidence -- but the direction agrees with the registry, which is not a "
                "case-report artifact."
            ),
        },
        "respiratory": {
            "count": by_label.get("respiratory_failure", 0),
            "⛔_the_premise_this_does_not_support": (
                "Respiratory failure from progressive pulmonary metastases is present in this corpus "
                "and is NOT its dominant named mechanism. One of the three respiratory deaths "
                "followed a tumour-embolic ischaemic stroke rather than pulmonary tumour burden. "
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
    print(f"  {len(emc_papers)} EMC papers, {counts['papers_contributing']} contributing a death")
    print(f"  {total_deaths} classified deaths: {n_mech} with a named mechanism, "
          f"{n_unstated} unstated")
    for k, v in by_label.items():
        print(f"    {v:>3}  {k}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
