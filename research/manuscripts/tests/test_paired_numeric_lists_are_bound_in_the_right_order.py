"""A sentence pairing two enumerated numeric lists must bind them in an order the arithmetic allows.

⛔ WHY. On 2026-08-19, while FIXING an audit finding, this sentence was written into §2.7:

    "an eleven- or twelve-base-pair contiguous run inside a 16-mer carries four or five"

Read in parallel — which is how English binds paired lists — that asserts 11 + 4 = 15 and
12 + 5 = 17. A contiguous run of eleven inside a 16-mer leaves five positions unpaired and a run of
twelve leaves four. Both numbers were right; their ORDER was not.

★★ THE MECHANISM, BECAUSE IT WILL RECUR. The source diagnosis said "an 11- or 12-of-16 contiguous run
carries 4–5 mismatches", which is TRUE as a range over the class {11, 12}. Transcribing it into a
sentence that already enumerated "eleven- or twelve-" turned a range into a MAPPING, and because the
two quantities are anti-correlated — a longer paired run leaves fewer unpaired positions — writing
both lists in their natural ascending order made the mapping wrong by construction. Inverse
relationship plus parallel enumeration equals silent inversion.

⚠ AND IT WAS INTRODUCED BY A FIX, WHICH IS THE DANGEROUS PART. The passage had just been reviewed,
diagnosed and repaired, so it was the passage least likely to be read again — a defect landing
exactly in the blind spot the fix created. Nothing caught it: the numbers are not pinned figures, the
universal-claim guard checks scope rather than arithmetic, and the finding list's success criterion
was "every finding addressed", not "every new sentence true".

★ SO THE INVARIANT IS CHECKED, NOT THE WORDING. Inside an N-mer, a contiguous paired run of length L
leaves exactly N − L positions unpaired. Any sentence stating both, in any phrasing, has to satisfy
it — and when both appear as lists of equal length, element i must pair with element i.
"""
from __future__ import annotations

import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
ARTICLE = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-research-article.md")
#: ⚠ THE SI IS SCANNED TOO. The invariant is arithmetic, not editorial, and the supplement restates
#: the screen-5 scoping in its own words — a sentence that inverts the mapping there is the same
#: defect in a document a reader reaches from the same deposit.
SUPPLEMENT = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-supplementary-information.md")

WORD2NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
}
_NUMWORD = "|".join(WORD2NUM)
_NUM = rf"(?:{_NUMWORD}|\d+)"
_LIST = rf"{_NUM}(?:\s*(?:-\s*)?(?:or|to|and)\s+{_NUM})*"


def _to_int(token):
    token = token.strip().lower()
    return WORD2NUM.get(token, int(token) if token.isdigit() else None)


def _sentences(path):
    if not os.path.exists(path):
        pytest.fail(f"a scanned document is missing: {path}")
    text = re.sub(r"^---\n.*?\n---\n", "", open(path, encoding="utf-8").read(), flags=re.S)
    text = re.sub(r"^```.*?^```", "", text, flags=re.S | re.M)
    text = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("|"))
    #: ⛔⛔ WHITESPACE IS FLATTENED, NOT JUST DE-NEWLINED (2026-08-19, lane C2). This read
    #: `text.replace("\n", " ")`, and the manuscript hard-wraps at ~100 columns with a THREE-SPACE
    #: continuation indent — so a phrase broken across a wrap came back as "carries four    or
    #: five", with four spaces. Every regex here tolerates that (`\s+` throughout); the literal
    #: blacklist below did not, and the inverted mapping it exists to forbid was sitting in §6's
    #: screen-5 bullet, unmatched, while this file reported green. A prose needle must flatten.
    text = re.sub(r"[ \t]*\n[ \t]*", " ", text)
    return [" ".join(s.split()) for s in re.split(r"(?<=[.;])\s+", text) if s.strip()]


def _body_sentences():
    return _sentences(ARTICLE) + _sentences(SUPPLEMENT)


#: ⛔ THE VERB SET IS THE COVERAGE (widened 2026-08-19). Before this, the whole file matched ONE
#: sentence in the manuscript — the sentence the defect was found in — because the gap clause had
#: to open with `leaves|carries|leaving|carrying`. Any of "gives four", "has four", "with four
#: unpaired", "yielding four" would have carried the identical inversion straight past it, and a
#: guard that only recognises the phrasing of the bug it was written for is a record of that bug,
#: not a check on the class.
#:
#: ⚠ WHAT IS DELIBERATELY *NOT* IN THE SET: a bare "and"/"with" in front of "mismatches". "A 16-mer
#: with two mismatches and a contiguous run of eleven" states a SEARCH PARAMETER, not the
#: complement of the run, and 11 + 2 = 13 would be reported as an arithmetic error in a true
#: sentence. `with` is admitted only in front of an explicitly UNPAIRED count, where the reading is
#: unambiguous. The corpus was re-scanned after each addition; see the coverage assertion below.
_BINDING_VERB = (r"leaves?|leaving|left|carries|carry|carrying|carried|has|have|having"
                 r"|retains?|retaining|spares?|sparing|admits?|admitting|means?|meaning"
                 r"|implies|implying|allows?|allowing|permits?|permitting|gives?|giving"
                 r"|yields?|yielding")
_UNPAIRED_NOUN = (r"positions?\s+unpaired|unpaired\s+positions?|mismatch(?:es)?"
                  r"|bases?\s+unpaired|unpaired\s+bases?"
                  r"|nucleotides?\s+unpaired|unpaired\s+nucleotides?"
                  r"|base\s+pairs?\s+unpaired|unpaired\s+base\s+pairs?")

#: "a contiguous run of eleven or twelve base pairs" / "an eleven- or twelve-base-pair ... run"
_RUN_LIST = re.compile(
    rf"(?:(?:contiguous|paired|uninterrupted|perfect)\s+)*"
    rf"(?:runs?|stretch(?:es)?|tracts?|duplex(?:es)?|matches?|blocks?)\s+of\s+({_LIST})"
    rf"\s+(?:contiguous\s+)?(?:base\s+pairs?|bp|nucleotides?|bases?)"
    rf"|({_LIST})[-\s]*(?:contiguous[-\s]*)?(?:base[-\s]?pair|bp|nucleotide|base)[-\s]*"
    rf"(?:long\s+)?(?:runs?|stretch(?:es)?|tracts?|duplex(?:es)?|matches?|blocks?)"
    rf"|({_LIST})\s+contiguous\s+(?:base\s+pairs?|nucleotides?|bases?)",
    re.I)
#: "leaves five or four positions unpaired" / "carries four or five mismatches" / "with four
#: positions unpaired"
_GAP_LIST = re.compile(
    rf"(?:{_BINDING_VERB})\s+({_LIST})\s+(?:{_UNPAIRED_NOUN})"
    rf"|with\s+({_LIST})\s+(?:positions?|bases?|nucleotides?|base\s+pairs?)\s+unpaired"
    #: ⛔ AND THE NOUN MAY BE ELIDED (2026-08-19, lane C2). §6's screen-5 bullet reads "...inside a
    #: 16-mer carries four or five, so..." — the run list, the N-mer and the binding verb are all
    #: there and only the noun is gone, so every pattern above missed it and the inversion went
    #: unchecked in the one section a methods reader reconciles the screen from. A bare count list
    #: closing a clause, in a sentence that has ALREADY stated an N-mer and a paired-run list, can
    #: only be the complement — `_paired_sentences` requires both of those before this is read.
    rf"|(?:{_BINDING_VERB})\s+({_LIST})\s*(?=[,;.]|$)",
    re.I)
_NMER = re.compile(rf"\b({_NUM})[-\s]?mer\b", re.I)


def _split_list(blob):
    return [_to_int(p) for p in re.split(r"\s*(?:-\s*)?(?:or|to|and)\s+", blob)
            if _to_int(p) is not None]


def _first_group(match):
    return next((g for g in match.groups() if g), "")


def _paired_sentences():
    """Every sentence stating an N-mer, a paired-run list and an unpaired/mismatch list."""
    out = []
    for s in _body_sentences():
        nmer, run, gap = _NMER.search(s), _RUN_LIST.search(s), _GAP_LIST.search(s)
        if not (nmer and run and gap):
            continue
        runs, gaps = _split_list(_first_group(run)), _split_list(_first_group(gap))
        n = _to_int(nmer.group(1))
        if n is None or not runs or not gaps:
            continue
        out.append((n, runs, gaps, s))
    return out


def test_run_length_and_unpaired_count_always_sum_to_the_oligonucleotide_length():
    """Inside an N-mer, a paired run of L leaves N - L unpaired. Checked wherever both are stated."""
    checked = _paired_sentences()
    offenders = []
    for n, runs, gaps, s in checked:
        if len(runs) != len(gaps):
            offenders.append(f"list lengths differ ({runs} vs {gaps}) in: {s[:170]}")
            continue
        bad = [(a, b) for a, b in zip(runs, gaps) if a + b != n]
        if bad:
            offenders.append(
                f"in a {n}-mer, {' and '.join(f'{a}+{b}={a+b}' for a, b in bad)} "
                f"(each pair must total {n}) in: {s[:170]}")

    assert checked, (
        "no sentence stating both a paired-run length and an unpaired/mismatch count was found. "
        "If §2.7's screen-5 scoping sentence was reworded, update this test's patterns — a guard "
        "that silently matches nothing is worse than no guard, which is why this asserts coverage.")
    assert not offenders, (
        "a paired numeric list is bound in an order the arithmetic forbids:\n  "
        + "\n  ".join(offenders)
        + "\n\nInside an N-mer a contiguous paired run of L leaves exactly N - L positions unpaired, "
          "so the two lists run in OPPOSITE directions. Writing both ascending inverts the mapping. "
          "State the second list in the order the first demands and mark it 'respectively'.")


def test_every_paired_list_says_which_element_binds_to_which():
    """Two lists of equal length side by side are ambiguous until the sentence says they are not.

    ⛔ THE ANCHOR IS STRUCTURAL, NOT A QUOTED CLAUSE. This used to locate the sentence with
    `body.find("mismatches, and a contiguous run of eleven or twelve base pairs")` — a 61-character
    literal from one draft of one sentence, in a paper under active rewrite, and it asserted
    `!= -1`, so a reworded §2.7 failed here for having been reworded. The sentence is now found by
    the same patterns the arithmetic test uses, and what is required of it is the binding marker.
    """
    ambiguous = [(runs, gaps, s) for n, runs, gaps, s in _paired_sentences()
                 if len(runs) > 1 and len(gaps) > 1 and "respectively" not in s.lower()]
    assert not ambiguous, (
        "a sentence pairs two enumerated numeric lists without saying they bind element by "
        "element:\n  " + "\n  ".join(f"{r} vs {g}: {s[:150]}" for r, g, s in ambiguous)
        + "\n\nAdd 'respectively', or state the second list as a range rather than a mapping.")


def test_the_inverted_pairing_that_shipped_does_not_come_back():
    """⚠ THE NEEDLE LOST ITS TAIL (2026-08-19). It read `"carries four or five, so the"` — the
    inversion PLUS the four words that happened to follow it in the draft it was found in, so
    rewording anything after the comma retired the guard silently. What is forbidden is the
    mapping: an ascending run list bound to an ascending unpaired list."""
    body = " ".join(_body_sentences())
    assert "carries four or five" not in body, (
        "§2.7 has reverted to the inverted pairing: an eleven-base-pair run leaves FIVE positions "
        "unpaired and a twelve-base-pair run leaves FOUR, not the other way round.")
