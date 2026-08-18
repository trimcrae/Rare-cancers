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

WORD2NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
}
_NUMWORD = "|".join(WORD2NUM)


def _to_int(token):
    token = token.strip().lower()
    return WORD2NUM.get(token, int(token) if token.isdigit() else None)


def _body_sentences():
    if not os.path.exists(ARTICLE):
        pytest.fail(f"the manuscript is missing: {ARTICLE}")
    text = re.sub(r"^---\n.*?\n---\n", "", open(ARTICLE, encoding="utf-8").read(), flags=re.S)
    text = re.sub(r"^```.*?^```", "", text, flags=re.S | re.M)
    text = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("|"))
    return [s.strip() for s in re.split(r"(?<=[.;])\s+", text.replace("\n", " ")) if s.strip()]


#: "a contiguous run of eleven or twelve base pairs" / "an eleven- or twelve-base-pair ... run"
_RUN_LIST = re.compile(
    rf"(?:run of|runs of)\s+((?:{_NUMWORD}|\d+)(?:\s+or\s+(?:{_NUMWORD}|\d+))*)\s+base pairs?"
    rf"|((?:{_NUMWORD}|\d+)(?:-\s*or\s+|\s+or\s+)(?:{_NUMWORD}|\d+))-?\s*base-pair",
    re.I)
#: "leaves five or four positions unpaired" / "carries four or five mismatches"
_GAP_LIST = re.compile(
    rf"(?:leaves|carries|leaving|carrying)\s+((?:{_NUMWORD}|\d+)(?:\s+or\s+(?:{_NUMWORD}|\d+))*)"
    rf"\s+(?:positions? unpaired|mismatch(?:es)?|unpaired positions?)", re.I)
_NMER = re.compile(r"\b(\d+)-mer\b")


def _split_list(blob):
    return [_to_int(p) for p in re.split(r"\s*(?:-\s*)?or\s+", blob) if _to_int(p) is not None]


def test_run_length_and_unpaired_count_always_sum_to_the_oligonucleotide_length():
    """Inside an N-mer, a paired run of L leaves N - L unpaired. Checked wherever both are stated."""
    offenders, checked = [], 0
    for s in _body_sentences():
        nmer = _NMER.search(s)
        run = _RUN_LIST.search(s)
        gap = _GAP_LIST.search(s)
        if not (nmer and run and gap):
            continue
        n = int(nmer.group(1))
        runs = _split_list(run.group(1) or run.group(2) or "")
        gaps = _split_list(gap.group(1) or "")
        if not runs or not gaps:
            continue
        checked += 1
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


def test_the_screen_five_scoping_sentence_states_the_pairing_explicitly():
    """The sentence that carried the defect must keep the binding unambiguous."""
    body = " ".join(_body_sentences())
    assert "carries four or five, so the" not in body, (
        "§2.7 has reverted to the inverted pairing: an eleven-base-pair run leaves FIVE positions "
        "unpaired and a twelve-base-pair run leaves FOUR, not the other way round.")
    where = body.find("mismatches, and a contiguous run of eleven or twelve base pairs")
    assert where != -1, "§2.7's screen-5 scoping sentence has moved or been reworded away."
    passage = body[where:where + 260]
    assert "five or four" in passage and "respectively" in passage, (
        "§2.7 must give the unpaired counts in the order the run lengths demand — 'five or four' — "
        "and say 'respectively', so the binding cannot be read the other way.")
