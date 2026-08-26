"""⛔ TWO NUMBERS THE CENSUS CALLED COVERED, AND NOTHING WAS WATCHING EITHER OF THEM.

★ HOW THEY WERE FOUND, WHICH IS THE POINT. Not by reading the paper. `PREFLIGHT_FULL=1` widens
`test_the_census_word_covered_survives_ablation` from a six-sentence sample to ALL 47 numbered
covered sentences in the journal article, and two of them survived ablation:

    "…an industry working group's 2025 off-target recommendations report…"
        census credited: test_the_manuscript_asserts_the_relation_its_artifacts_compute.py,
                         test_the_manuscript_title_states_the_measurement_it_carries.py
        perturbed 2025 -> 2027: no guard reading this file noticed

    "A donor joined to the first coding exon — transcript exon 3 — does yield a chimera."
        census credited: test_named_reagents_carry_the_acceptor_the_csv_gives_them.py
        perturbed 3 -> 7:       no guard reading this file noticed

⛔ THE CREDITED GUARDS ARE REAL GUARDS THAT DO NOT READ THESE NUMBERS. That is the round-16 defect
one level down — `claim_coverage` scored "matches few sentences" where "distinguishes THIS sentence"
was meant, so a guard that opens the file was credited with a sentence it never looks at. The
ablation gate is what separates the two, and its instruction is explicit: *"Either bind them for
real, or the pattern that claims them is structure rather than content… Do not lower the coverage
floor to match."* This file binds them for real.

⚠ NEITHER NUMBER IS TYPED HERE. 2025 is read from the fetched PubMed record for PMID 39912803 in
`nat-scope-census.json`; exon 3 is read from `nr4a3_acceptor_numbering.PANEL_ACCEPTOR`, which
derives it from the transcript annotation. A guard that hard-codes the value it checks would pass a
mutation of the SOURCE while the prose silently went wrong — the failure that made the ablation
harness necessary in the first place (CLAUDE.md §1: a total is DERIVED, never typed).

★ AND THE PROSE IS WHAT IS READ, so ablation can see this guard bind these sentences. Both patterns
match the sentence around the number, not the number alone: perturbing either digit takes this file
red, which is the property `claim_coverage` will now be able to credit honestly.
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
ASO = os.path.join(MANUSCRIPTS, "aso")
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))

#: The document these two sentences live in. Named in full because `claim_ablation.guards_reading`
#: credits a guard to a document by finding this basename in the guard's own source.
ARTICLE = os.path.join(ASO, "fusion-junction-aso-journal-article.md")

#: The fetched PubMed record behind reference 22 — the industry off-target recommendations.
SCOPE_CENSUS = os.path.join(ASO, "nat-scope-census.json")
OSWG_PMID = "39912803"

sys.path.insert(0, os.path.join(REPO, "research", "modalities"))


def _article():
    with open(ARTICLE, encoding="utf-8") as fh:
        return fh.read()


def _ledger_year():
    """The year of PMID 39912803, from the fetched record. Never typed."""
    with open(SCOPE_CENSUS, encoding="utf-8") as fh:
        doc = json.load(fh)
    for cand in doc.get("candidates", []):
        if str(cand.get("pmid")) == OSWG_PMID:
            return cand.get("year")
    raise AssertionError(
        f"PMID {OSWG_PMID} is not in {os.path.basename(SCOPE_CENSUS)}'s candidates, so the year the "
        "prose states cannot be checked against anything. An absent reading is not a reading of "
        "absence — restore the record rather than relaxing this guard.")


def test_the_working_group_report_year_matches_the_fetched_record():
    """The prose dates reference 22. That date must be the record's, not a remembered one."""
    year = _ledger_year()
    assert isinstance(year, int), (
        f"the fetched record for PMID {OSWG_PMID} carries year={year!r}, which is not an integer, so "
        "the prose has nothing well-formed to agree with.")

    # The sentence, not the bare number: ablation must be able to see this guard bind it.
    hits = re.findall(r"industry working group's\s+(\d{4})\s+off-target\s+recommendations", _article())
    assert hits, (
        "the journal article no longer states an industry working group's YEAR off-target "
        "recommendations. Either the sentence was rewritten — update this pattern with it — or the "
        "citation was dropped, which is a change to what the paper attributes to reference 22.")
    for stated in hits:
        assert int(stated) == year, (
            f"the article dates the industry off-target recommendations to {stated}, but the fetched "
            f"PubMed record for PMID {OSWG_PMID} says {year}. A citation year is an identifier: it is "
            "what a reader searches. Fix the prose, or fix the record it disagrees with — do not "
            "reconcile them by editing this guard.")


def test_the_first_coding_exon_in_prose_is_the_rank_the_annotation_gives():
    """`transcript exon 3` is a claim about NR4A3's annotation, and the annotation decides it."""
    import nr4a3_acceptor_numbering as acc

    rank = acc.PANEL_ACCEPTOR["transcript_exon_rank"]
    assert isinstance(rank, int), (
        f"PANEL_ACCEPTOR carries transcript_exon_rank={rank!r}, which is not an integer.")

    hits = re.findall(
        r"donor joined to the first coding exon\s*[—-]\s*transcript exon\s+(\d+)\s*[—-]", _article())
    assert hits, (
        "the journal article no longer says 'A donor joined to the first coding exon — transcript "
        "exon N —'. That sentence carries the paper's reading of which acceptor yields a chimera; if "
        "it was rewritten, move this pattern with it rather than deleting the binding.")
    for stated in hits:
        assert int(stated) == rank, (
            f"the article calls transcript exon {stated} the first coding exon, but "
            f"`nr4a3_acceptor_numbering.PANEL_ACCEPTOR` derives rank {rank} from the transcript "
            f"annotation ({acc.PANEL_ACCEPTOR['transcript']}). This is the exon/acceptor mismatch the "
            "paper's own central warning is about, so the prose and the annotation may not disagree.")
