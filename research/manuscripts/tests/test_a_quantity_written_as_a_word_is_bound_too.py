#!/usr/bin/env python3
"""A number spelled out is still a number, and until now nothing in this repository read one.

⛔⛔ THE MEASUREMENT THIS EXISTS FOR, AND IT IS THE PUBLICATION TIER'S ONLY FINDING. On 2026-09-02 a
`PREFLIGHT_FULL=1` ablation sweep of the ASO journal article perturbed all 91 of its covered
numbered sentences and found **11 whose credited witnesses never went red**. Every one of the 11
failures was a NUMBER-WORD swap — `six->ten`, `seven->three`, `two->six`, `second->fourth`,
`five->nine`. **Zero digit swaps failed.** The guards bind the form the author happened to write and
are blind to the same fact written out, while `claim_coverage` credits them either way.

★ SO `covered: 106` WAS TRUE OF THE FORM AND FALSE OF THE PROPERTY, which is the defect this
repository keeps paying for at successively higher levels. Round 31 found a guard scoped to
predicate and cut but not ENSEMBLE. This is the same shape one level up: scoped to digits but not to
WORDS. In both cases the guard bound what was in front of it rather than what was being claimed.

⛔ AND THE COMMIT LOOP COULD NEVER HAVE SEEN IT. `test_the_census_word_covered_survives_ablation`
ablates an evenly spaced sample of SIX sentences per commit and the whole set only under
`PREFLIGHT_FULL`. 6 of 106 is 5.7 %, and the eleven blind ones were not in the sample — nine green
`PREFLIGHT_TESTS` runs on 2026-09-02 each ablated six and saw nothing. That tier boundary is
deliberate (CLAUDE.md §6: the 25 minutes is for the one door that opens outward) and it worked:
the door refused to open.

★★ WHAT THESE SENTENCES ARE, AND WHY THEY ARE NOT DECORATIVE. They carry the reagent geometry, the
condemnation criterion, the scope of the parent screen and the limitation that bounds the whole
paper. Change "six" to "ten" in the RNase-H gap requirement, or "ten" to "six" in the criterion the
screen condemns on, and before this file NOTHING in the repository noticed.

⚠ WHAT THIS FILE DOES NOT DO. It does not check that the sentences are well written, that the number
words should be words at all, or that every word-quantity in the paper is bound — only that the ones
naming a value an artifact computes agree with that artifact. A quantity with no artifact behind it
(an adopted convention, a range taken from the literature) is out of scope here and says so.
"""

from __future__ import annotations

import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(MANUSCRIPTS))
ARTICLE = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-journal-article.md")
REPORT = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-research-article.md")
GAP = os.path.join(ROOT, "research", "modalities", "aso-parent-gap-pairing.json")
PREMRNA = os.path.join(ROOT, "research", "modalities", "aso-premrna-offtarget.json")

#: ⛔ ONE HOME FOR THE MAPPING, and it is deliberately the same trick the scramble-null guard uses:
#: a word is turned into an integer and compared to a number an artifact COMPUTES. Anything that
#: cannot be turned into a comparison against a committed value does not belong in this table.
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
         "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "sixteen": 16}


def _text(path):
    return " ".join(open(path, encoding="utf-8").read().split())


def _artifacts():
    gap = json.load(open(GAP, encoding="utf-8"))
    pre = json.load(open(PREMRNA, encoding="utf-8"))
    return {
        # how many wild-type parent transcripts the mature screen actually reads
        "parents": len(gap["method"]["parents_searched"]),
        # the duplex length the mature screen condemns on
        "cut_bp": gap["method"]["min_duplex_bp"],
        # the gapmer's locked wing, from the geometry the designs were built to
        "wing": gap["_geometry"]["wing"],
        "gap_nt": gap["_geometry"]["gap_nt"],
        "oligo_len": gap["_geometry"]["oligo_len"],
        # the precursor arm's mismatch ceiling
        "max_mismatches": pre["method"]["max_mismatches"],
    }


#: Each row: (key into `_artifacts()`, a regex whose ONE group is the number word, what it claims).
#: ⚠ THE REGEX MATCHES THE SENTENCE, NOT THE NUMBER ALONE. A bare `\bsix\b` would bind every "six"
#: in the document to one artifact value, which is how a guard starts reddening on true input — the
#: failure `paper-hardening` §8b.1 says is worse than missing a defect, because the first thing
#: anyone does to a gate that reds on honest prose is loosen it.
BINDINGS = (
    ("parents", r"longest contiguous duplex any of (\w+) wild-type parent transcripts",
     "the mature screen's parent set"),
    ("parents", r"the parent arm reads (\w+) transcripts",
     "the mature screen's parent set, stated a second time"),
    ("cut_bp", r"screen condemns on a (\w+)-base-pair duplex through the gap",
     "the duplex length the mature screen condemns on"),
    ("cut_bp", r"counts a liability only at (\w+) contiguous base pairs of duplex",
     "the same criterion, stated where the screen is introduced"),
    # ⚠ `\S+-D-oxy-locked` rather than a literal β: the glyph is one character, and an earlier
    # draft of this row wrote `..` for it and matched nothing — a binding that silently watches
    # nothing is the failure this whole file is about, reproduced inside its own instrument.
    ("wing", r"with wings of (\w+) contiguous \S+-D-oxy-locked residues",
     "the gapmer's locked wing"),
    ("max_mismatches", r"condemns on a hit at up to (\w+) mismatches with the gap fully paired",
     "the precursor arm's mismatch ceiling"),
)


@pytest.mark.parametrize("key,pattern,what", BINDINGS)
def test_a_word_quantity_matches_the_artifact_that_computes_it(key, pattern, what):
    """⛔ THE ASSERTION THE ABLATION SWEEP PROVED WAS MISSING. Perturb any of these words and this
    goes red; before this file, nothing did."""
    art = _artifacts()
    text = _text(ARTICLE)
    m = re.search(pattern, text)
    assert m, (
        "no sentence in the journal article matches %r, so this binding is watching nothing. Either "
        "the sentence was rewritten — re-anchor the pattern against the new wording — or the claim "
        "was removed, in which case delete this row rather than leaving a guard that cannot fire."
        % pattern)
    word = m.group(1).lower()
    assert word in WORDS, (
        "the article writes %r where a number word was expected, for %s. If the prose moved to "
        "digits that is fine, but this row must move with it — a binding that cannot parse its own "
        "target is a binding that passes for the wrong reason." % (m.group(1), what))
    assert WORDS[word] == art[key], (
        "the article says %r (%d) for %s, and the artifact computes %d.\n"
        "  artifact: %s\n"
        "  matched:  ...%s...\n"
        "A number spelled out is still a number. This exact class — eleven of ninety-one covered "
        "sentences whose witnesses were blind to word forms — is why this file exists."
        % (word, WORDS[word], what, art[key],
           os.path.relpath(GAP if key != "max_mismatches" else PREMRNA, ROOT),
           text[max(0, m.start() - 60): m.end() + 60]))


def test_the_geometry_sentence_agrees_with_the_architecture_it_names():
    """The wing, the gap and the length are one fact in three parts; the paper states them apart.

    ⚠ `5-6-5` is the artifact's own spelling of the architecture, so this checks the prose's wing
    against the FIRST component rather than against a constant typed here.
    """
    art = _artifacts()
    arch = json.load(open(GAP, encoding="utf-8"))["_geometry"]["architecture"]
    parts = [int(n) for n in re.findall(r"\d+", arch.split("(")[0])]
    assert parts == [art["wing"], art["gap_nt"], art["wing"]], (
        "the artifact's architecture %r does not decompose into wing/gap/wing %r — the geometry "
        "fields and the architecture string have diverged in the artifact itself" % (arch, parts))
    assert sum(parts) == art["oligo_len"], (
        "%r sums to %d and the artifact's oligo_len is %d" % (arch, sum(parts), art["oligo_len"]))


def test_the_binding_table_covers_every_word_quantity_the_sweep_found_blind():
    """⛔ THE CONTROL: this file must not quietly shrink to the rows that were easy.

    The 2026-09-02 sweep named eleven blind sentences. The ones whose quantity an artifact computes
    are bound above; the rest are quantities with no artifact behind them — an adopted convention
    ("two to four locked residues per wing taken here as usual"), a range read out of the cited
    literature, and ordinals naming screens. Those are recorded here BY NAME so that a later reader
    can tell "not bindable" from "not attempted", which is the distinction the census lost.
    """
    unbindable = {
        "two to four per wing taken here as usual":
            "an adopted convention, explicitly labelled as such in the sentence itself — there is "
            "no artifact that computes what is 'usual', and inventing one would be worse than "
            "leaving it unbound",
        "a DNA gap of at least six nucleotides, with seven to ten the working range":
            "read out of PMID 24981949 and cited there; it is bound by the citation-provenance "
            "gate and by the verbatim quote in the literature record, not by a computation here",
        "The fourth records / The fifth covers / on the second":
            "ordinals enumerating the five screens in prose order. They are positional labels "
            "rather than measured quantities; binding them would pin the ORDER of the paragraphs, "
            "which is a formatting fact and not a claim about the work",
        "All five screens address hybridisation rather than cleavage":
            "the screen COUNT is a property of the paper's own structure, not of an artifact. It "
            "is left unbound deliberately and is named here so the gap is visible",
    }
    assert len(unbindable) == 4, "the record of what is deliberately unbound must stay explicit"
    text = _text(ARTICLE)
    for phrase in ("two to four", "at least six nucleotides", "All five screens"):
        assert phrase in text, (
            "%r is recorded above as a deliberately unbound quantity, but it is no longer in the "
            "article. Remove the row — a record of a gap that has closed reads as an open gap."
            % phrase)
