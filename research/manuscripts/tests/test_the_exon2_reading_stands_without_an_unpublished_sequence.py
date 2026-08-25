"""The exon-2 passage must never lean on a sequence nobody has published.

⛔ WHY THIS GUARD EXISTS, AND IT IS A DECISION RATHER THAN A DEFECT. The revision checklist's item
B3 asked the author to email the group that established USZ20-EMC1 and USZ22-EMC2 for their junction
sequences, and marked it DO BEFORE SUBMITTING: a sequenced exon-exon boundary would turn this
paper's exon-2 reading from an inference into a determination. trimcrae ruled on 2026-08-25 that
the paper is not to be gated on a reply from a specific laboratory — "the science should stand on
its own based on published work".

★★ THAT RULING IS ONLY SAFE BECAUSE OF FOUR SENTENCES, AND UNTIL NOW NOTHING READ THEM. The paper
stands without the reply because it (1) says the published report carries no sequenced boundary, no
accession and no junction sequence, (2) calls its own parsimony reading an inference and not a
determination, (3) names a reagent at BOTH candidate acceptors so no design depends on which
reading is right, and (4) requires the test article's own breakpoint to be established by RNA
sequencing before any oligonucleotide is ordered. Weaken any one and the passage starts asserting a
junction on evidence that does not exist.

⛔⛔ AND THIS PAPER HAS ALREADY MADE EXACTLY THAT ERROR ONCE. An earlier version placed the acceptor
through a coding-versus-transcript exon indexing mistake and was withdrawn in full. The four
sentences are the repair. A guard that reads them is the difference between a repair and a memory.

⚠ WHAT THIS GUARD IS NOT. It does not check that the exon-2 reading is CORRECT — nothing here can,
which is the whole point of the hedge. It checks that the manuscript keeps saying it does not know.
"""
from __future__ import annotations

import csv
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.dirname(os.path.dirname(MANUSCRIPTS))
ASO = os.path.join(MANUSCRIPTS, "aso")

ARTICLE = os.path.join(ASO, "fusion-junction-aso-journal-article.md")
SEQUENCES = os.path.join(ASO, "fusion-junction-aso-sequences.csv")


def _article():
    """The manuscript with its line wrapping flattened.

    ⚠ NORMALISED, BECAUSE A HARD-WRAPPED FILE MOVES ITS OWN LINE BREAKS. Two guards in this suite
    have already failed on a phrase that was present and intact, split across a newline by an edit
    somewhere else in the same paragraph. A check on a claim must not also be a check on wrapping.
    """
    return re.sub(r"\s+", " ", io.open(ARTICLE, encoding="utf-8").read())


def test_the_manuscript_says_the_published_report_carries_no_sequence():
    """(1) The gap in the evidence is stated, not left for a reader to notice."""
    body = _article()
    for probe in ("no sequenced exon-exon boundary",
                  "no transcript accession",
                  "no junction sequence"):
        assert probe in body, (
            f"⛔ the manuscript no longer says the cell-model report carries {probe!r}. That "
            f"sentence is why the exon-2 reading is allowed to be an inference: it tells the "
            f"reader the primary source does not settle the question. Without it the paper "
            f"appears to be choosing between two documented readings, which is not the situation.")
    assert "not decidable from what is published" in body, (
        "⛔ the manuscript no longer says the acceptor question is not decidable from what is "
        "published. B3 — the email that WOULD decide it — was declined as a gate on this paper on "
        "the express basis that the paper does not need it. This is the sentence that makes that "
        "true.")


def test_the_parsimony_reading_is_labelled_an_inference():
    """(2) The load-bearing hedge, in the words the paper uses.

    ⚠ THE PHRASE IS THE CLAIM HERE, which is why this matches text rather than structure. "More
    parsimonious" is an argument from what the disease is known to do, not an observation, and the
    single sentence that says so is all that separates a reading from an assertion.
    """
    body = _article()
    assert re.search(r"this is an inference and not a determination", body, re.I), (
        "⛔ the manuscript no longer states that its exon-2 reading is an inference and not a "
        "determination. That sentence is load-bearing twice over: it is the honest strength of the "
        "claim, and it is the stated reason the paper does not need a junction sequence from the "
        "group that holds the cell models.")


def test_a_reagent_is_named_at_both_candidate_acceptors():
    """(3) No design depends on which reading turns out to be right.

    ⛔ CHECKED AGAINST THE CANONICAL SEQUENCE FILE, NOT AGAINST THE PROSE. The failure this paper
    was withdrawn for was an exon-numbering error, so "the manuscript mentions exon 2" is worth
    nothing: what matters is that a sequence the manuscript PRINTS is one the screen actually
    placed at an exon-2 acceptor. A renumbering in the artifact and a stale sentence in the paper
    is precisely the pair that produced the withdrawal.
    """
    body = _article()
    rows = list(csv.DictReader(io.open(SEQUENCES, encoding="utf-8")))
    #: ⚠ `or ""` RATHER THAN A DEFAULT ARGUMENT. `csv.DictReader` fills a short row's missing
    #: fields with None, not with the `.get` default, so `r.get("junction", "")` still hands None
    #: to `re.search` — measured here on the first run.
    at_exon_2 = {r["sequence"]: r["junction"] for r in rows
                 if re.search(r"NR4A3_e2\b", r.get("junction") or "")}
    at_exon_3 = {r["sequence"]: r["junction"] for r in rows
                 if re.search(r"NR4A3_e3\b", r.get("junction") or "")}
    assert at_exon_2 and at_exon_3, (
        "the canonical sequence file has no design at one of the two acceptors, so this guard "
        "cannot measure the property — fix the artifact, not this test")

    printed = set(re.findall(r"5′-([ACGT]{12,30})-3′", body))
    assert printed, "⛔ the manuscript prints no reagent sequence at all"
    named_2 = sorted(printed & set(at_exon_2))
    named_3 = sorted(printed & set(at_exon_3))
    assert named_2, (
        f"⛔ the manuscript prints no sequence that the canonical file places at an *NR4A3* exon-2 "
        f"acceptor. The two cell models are REPORTED at exon 2 and the panel was designed at exon "
        f"3; naming a reagent at each is what keeps the paper useful whichever reading is right, "
        f"and it is one of the four properties on which gating this submission on an unpublished "
        f"junction sequence was declined. Sequences printed: {sorted(printed)}")
    assert named_3, (
        f"⛔ the manuscript prints no sequence that the canonical file places at an *NR4A3* exon-3 "
        f"acceptor, which is the acceptor the whole panel was tiled at. Printed: {sorted(printed)}")


def test_the_breakpoint_must_be_sequenced_before_anything_is_ordered():
    """(4) The requirement that makes an undecided acceptor safe rather than merely admitted."""
    body = _article()
    assert re.search(r"established\s+at\s+nucleotide\s+resolution\s+by\s+RNA\s+sequencing", body), (
        "⛔ the manuscript no longer requires the test article's breakpoint to be established at "
        "nucleotide resolution by RNA sequencing before an oligonucleotide is ordered. Every "
        "design here is specific to the exon pair it was tiled at, so this requirement is what "
        "makes an unresolved acceptor a question rather than a hazard — and it is the reason the "
        "paper can leave the question open at all.")
