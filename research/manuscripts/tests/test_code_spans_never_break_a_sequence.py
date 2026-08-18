"""A code span may wrap at a filename separator; it may never wrap inside an oligonucleotide.

⛔ WHY THE RULE WAS RELAXED AT ALL. Long identifiers were held atomic by a length threshold alone
(44 characters), so `emc-atr-vulnerability.json` at 26 and `aso_parent_gap_pairing.py` at 25 stayed
unbreakable, and the justified line BEFORE each carried about ten word-spaces of stretch. A blind
screen of the built manuscript PDF drew the distinction this code had missed: the paper's refusal to
break an unbreakable token is a SEQUENCE-safety rule — a newline a reader copies out of a base
string is invisible in a synthesis order form and produces the wrong molecule — and a filename or a
module name carries no such hazard.

⛔⛔ AND RELAXING IT IMMEDIATELY EXPOSED THE SEQUENCE CASE. `5′-GGGCATATCATCAAAC-3′` contains two
hyphens, so a separator-only rule hands it break opportunities after `5′-` and before `3′`, leaving
the delimiter stranded on the line above its bases. That is the exact defect this deposit was
rebuilt around. Delimited sequences normally reach the page as `.seq` spans rather than code spans,
so the refusal below is a belt on top of a brace — recorded because "it does not currently take that
path" is not a property a later edit is obliged to preserve.

★ WHAT THIS ASSERTS: the two behaviours together. Break filenames, never break bases.
"""
from __future__ import annotations

import importlib.util
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
BUILDER = os.path.join(os.path.abspath(os.path.join(HERE, "..")), "build_submission_pdf.py")


def _builder():
    spec = importlib.util.spec_from_file_location("build_submission_pdf", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B = _builder()

#: Tokens that MUST stay atomic, and why each one is dangerous.
UNBREAKABLE = [
    ("GGGCATATCATCAAAC", "a bare 16-mer"),
    ("CAGGGCATATCATCAAACCA", "a bare 20-mer"),
    ("5′-GGGCATATCATCAAAC-3′", "a delimited 16-mer: its hyphens are separators"),
    ("5′-AGGGCATATCATCAAACC-3′", "a delimited 18-mer"),
    ("ATGAGGGCCTTGTGTG", "the cryptic-exon reagent"),
    ("CAGTGGGCTCTCCACG", "a design the paper condemns"),
]

#: Tokens that SHOULD take a break, because a newline in them is harmless.
BREAKABLE = [
    "emc-atr-vulnerability.json",
    "aso_parent_gap_pairing.py",
    "fusion-junction-aso-sequences.csv",
    "research/manuscripts/aso_sequence_manifest.py",
]


@pytest.mark.parametrize("token,why", UNBREAKABLE, ids=[t for t, _ in UNBREAKABLE])
def test_a_token_carrying_bases_is_never_given_a_break_opportunity(token, why):
    html = B.code_span(token)
    assert "<wbr/>" not in html, (
        f"{token} ({why}) was given a break opportunity. A line break inside — or between a "
        "delimiter and its bases — is invisible to a reader who copies the string into a synthesis "
        "order, and the molecule they receive is not the one this paper measured.")
    assert 'class="brk"' not in html, (
        f"{token} ({why}) was marked breakable; it must stay one atomic token")


@pytest.mark.parametrize("token", BREAKABLE)
def test_a_filename_or_module_name_takes_breaks_at_its_separators(token):
    html = B.code_span(token)
    assert "<wbr/>" in html, (
        f"{token} takes no break opportunity, so the justified line before it stretches to hold it "
        "whole. It contains a separator and no base string, so breaking it is harmless.")
    assert 'class="brk"' in html


@pytest.mark.parametrize("token,_why", UNBREAKABLE, ids=[t for t, _ in UNBREAKABLE])
def test_the_token_survives_the_round_trip_intact(token, _why):
    """Whatever the markup, the characters a reader copies must be exactly the token."""
    stripped = re.sub(r"<[^>]+>", "", B.code_span(token))
    import html as _h
    assert _h.unescape(stripped) == token, (
        f"{token} came back as {_h.unescape(stripped)!r} after markup — the span altered the "
        "characters themselves, which is worse than any line break")


def test_the_sequence_detector_is_not_so_loose_it_blocks_every_filename():
    """A guard that refuses everything would silently reinstate the defect it replaced."""
    assert B._LOOKS_LIKE_A_SEQUENCE.search("GGGCATATCATCAAAC")
    for token in BREAKABLE:
        assert not B._LOOKS_LIKE_A_SEQUENCE.search(token), (
            f"{token} is being read as a sequence, so it will never break and the stretched-line "
            "defect returns for every path-like token")
