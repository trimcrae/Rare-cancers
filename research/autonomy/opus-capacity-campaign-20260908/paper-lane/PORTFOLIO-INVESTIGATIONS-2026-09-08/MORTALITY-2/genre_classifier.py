#!/usr/bin/env python3
"""PRE-SPECIFIED STUDY-TYPE (GENRE) CLASSIFIER for the 162-paper death-cue corpus.

WHY THIS FILE EXISTS AND WHY IT IS SEPARATE FROM THE RATE SCRIPT
----------------------------------------------------------------
The completed lane PUB-MORTALITY-MECHANISM measured a higher terminal-event cue rate in
EMC-titled papers (4/116 = 3.45%) than in the 128 same-retrieval papers that are not about
this disease (3/461 = 0.65%), Fisher p = 0.033. It named its own decisive limitation: the
comparator is UNMATCHED ON STUDY TYPE. Case reports narrate a death; cohort studies and
reviews tabulate deaths. A genre effect is as consistent with those counts as any difference
in reporting practice.

This file is the instrument that tests that. It is written and frozen BEFORE any cue rate is
computed within any stratum. It therefore:

  * reads ONLY title, journal and year -- the fields dumped by dump_corpus_metadata.py;
  * NEVER reads `sentences`, `has_mechanism_cue`, or any cue lexicon;
  * imports nothing from the rate script, and the rate script imports FROM here.

The ordering is evidenced by checks/: check 02 runs THIS file alone and prints the genre
distribution and this file's sha256 with no rate anywhere in its output; check 03 is the
hand-check; check 04 is the first execution in this lane that computes a cue rate, and it
re-prints the same sha256 to show the rule was not touched afterwards.

A rule tuned after seeing the answer would be worthless, so the rule is deliberately coarse,
keyword-based, and accepts known error, which check 03 quantifies rather than repairs.

THE RULE (first matching stratum wins; precedence is part of the pre-specification)
----------------------------------------------------------------------------------
 S1 case_report_or_series  Narrative report of one or a few identified patients. Trigger:
                           the JOURNAL name contains "case rep" (or is Cureus, a
                           case-report-dominated journal), OR the TITLE contains a
                           case-report phrase.
 S2 review_or_synthesis    Narrative review, systematic review, meta-analysis, guideline,
                           editorial, bibliometric or "state of the art" survey of a
                           literature. Checked BEFORE S3 so that "systematic review and
                           meta-analysis" is a synthesis, not a cohort.
 S3 clinical_study         Primary patient-level clinical data reported in aggregate:
                           trial, cohort, retrospective/prospective series, registry,
                           population-based or nationwide analysis, outcome/survival/
                           prognostic/efficacy/safety study.
 S4 laboratory_or_methods  Bench, model-system, molecular-pathology, imaging or
                           computational-methods work with no patient outcome table.
 S5 unclassified           No trigger fired. Kept as its own stratum and reported; it is
                           NOT silently folded into another.

Known and accepted failure modes of the rule, stated in advance: a case report whose title
neither says "case" nor sits in a case journal is missed to S3/S4/S5 (e.g. a title of the
form "An 11-year-old boy with ..."); a cohort paper published in a case-report journal is
pulled to S1 by the journal trigger; "review of the literature" appended to a case report is
handled by S1 winning, but a review that reports its own new case is a genuine hybrid the
rule cannot split. Check 03 measures how often this happens.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[6]
META = pathlib.Path(__file__).with_name("corpus-metadata.json")
OUT = pathlib.Path(__file__).with_name("genre-classification.json")

STRATA = ["case_report_or_series", "review_or_synthesis", "clinical_study",
          "laboratory_or_methods", "unclassified"]

RX_CASE_JOURNAL = re.compile(r"case rep|^cureus$|clin case|case stud", re.I)
RX_CASE_TITLE = re.compile(
    r"\bcase (?:report|reports|series|study|studies)\b|"
    r"\breport of (?:a|an|one|two|three|four|five|\d+)\b|"
    r"\breport and literature review\b|"
    r"\ba report of\b|\bcases? with review\b|"
    r"\b(?:report|reports) of \d+ cases\b|"
    r"\b\d+ cases? (?:with|of) review\b|"
    r"\bcase of\b|\ba rare case\b|\bcases with review of literature\b",
    re.I)
RX_REVIEW = re.compile(
    r"\breview\b|\breviews\b|meta-?analys|\bguidelines?\b|\beditorial\b|"
    r"state of the art|\bupdates? on\b|\(review\)|bibliometric|"
    r"\boverview\b|\bperspectives?\b|current landscape|"
    r"\bemerging trends\b|\bcurrent challenges\b|\bpractical guide\b|"
    r"\ba practical approach\b|\bwhat we can learn\b",
    re.I)
RX_CLINICAL = re.compile(
    r"\bphase (?:i{1,3}b?|1|2|3|ib|iii)\b|\btrial\b|\bcohort\b|"
    r"\bretrospective\b|\bprospective\b|population-?based|nationwide|"
    r"\bregistry\b|\bSEER\b|multicent(?:er|re)|\breal-?world\b|"
    r"\bsurvival\b|\boutcomes?\b|\bprognos(?:tic|is)\b|\befficacy\b|"
    r"\bsafety\b|\btolerability\b|\bpatients\b|\bsingle-arm\b|"
    r"\bexperience\b|\bfollow-?up\b|\bepidemiology\b|\bpooled\b|"
    r"\bpost hoc\b|\bpost-hoc\b|\bclinical activity\b|\bdose-escalation\b|"
    r"\bquality of life\b|\brisk (?:factors|prediction)\b|\bvalidation of\b",
    re.I)
RX_LAB = re.compile(
    r"\bin vitro\b|\bin vivo\b|\bcell (?:line|lines|model|models)\b|\bex vivo\b|"
    r"\bmurine\b|\bmice\b|\bmouse\b|\bzebrafish\b|\bchick\b|\bxenograft\w*\b|"
    r"\borganoids?\b|\bnanoparticles?\b|\bstructural insights\b|\bpurification\b|"
    r"\bimmunohistochemistry\b|\bsequencing\b|\bmolecular (?:testing|classification|"
    r"profiling|diagnostics|pathology|genetics)\b|\bgenomic profiling\b|"
    r"\bfusion(?:s)? (?:protein|proteins|partners)\b|\bdeep learning\b|"
    r"\bneural network\b|\bimaging findings\b|\bradiologic features\b|"
    r"\bcytology\b|\bpathogenesis\b|\bbiology\b|\bmicroenvironment\b|"
    r"\btherapeutic targets?\b|\bproof of (?:concept|principle)\b|"
    r"\bdistinguishes between\b|\brearrangement\b|\btranslocat\w+\b|"
    r"\bbiomarkers?\b|\bexpression\b|\bepigenetic\b|\bpreclinical\b",
    re.I)


def classify(title, journal):
    """Return (stratum, trigger). Title and journal only. No sentence, no cue, ever."""
    t = title or ""
    j = journal or ""
    if RX_CASE_JOURNAL.search(j):
        return "case_report_or_series", f"journal~{RX_CASE_JOURNAL.search(j).group(0)}"
    m = RX_CASE_TITLE.search(t)
    if m:
        return "case_report_or_series", f"title~{m.group(0)}"
    m = RX_REVIEW.search(t)
    if m:
        return "review_or_synthesis", f"title~{m.group(0)}"
    m = RX_CLINICAL.search(t)
    if m:
        return "clinical_study", f"title~{m.group(0)}"
    m = RX_LAB.search(t)
    if m:
        return "laboratory_or_methods", f"title~{m.group(0)}"
    return "unclassified", "no_trigger"


def load_rows():
    return json.loads(META.read_text())["papers"]


def classified_rows():
    rows = []
    for r in load_rows():
        s, trig = classify(r["title"], r["journal"])
        rows.append({**r, "stratum": s, "trigger": trig})
    return rows


def main():
    import hashlib
    rows = classified_rows()
    src = pathlib.Path(__file__).read_bytes()
    dist = {s: {"all": 0, "emc_titled": 0, "not_emc_titled": 0} for s in STRATA}
    for r in rows:
        dist[r["stratum"]]["all"] += 1
        dist[r["stratum"]]["emc_titled" if r["emc_titled"] else "not_emc_titled"] += 1
    out = {
        "_what_this_is": __doc__.strip(),
        "_no_outcome_was_read": ("This classification used title, journal and year only. "
                                 "No sentence text and no cue flag was read to produce it."),
        "classifier_sha256": hashlib.sha256(src).hexdigest(),
        "strata": STRATA,
        "distribution": dist,
        "papers": rows,
    }
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    print("classifier_sha256:", out["classifier_sha256"])
    print("\nGENRE DISTRIBUTION (papers) -- no cue rate is computed anywhere in this script")
    print(f'{"stratum":26s} {"all":>5s} {"EMC-titled":>11s} {"other":>7s}')
    for s in STRATA:
        d = dist[s]
        print(f'{s:26s} {d["all"]:5d} {d["emc_titled"]:11d} {d["not_emc_titled"]:7d}')
    print("\nassignments:")
    for r in rows:
        print(f'{r["pmid"]}\t{"EMC" if r["emc_titled"] else "OTH"}\t{r["stratum"]}\t{r["trigger"]}\t{r["title"][:90]}')
    return 0


if __name__ == "__main__":
    sys.exit(main())
