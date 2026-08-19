"""The canonical file has THREE verdict states, and its header must be true of all three.

⛔ WHY. `fusion-junction-aso-sequences.csv` is the file a laboratory orders from. Its header tells a
reader how to read a verdict, and the sentence it tells them with is:

    "READ do_not_order FIRST. A non-empty value means the paper names that design as one NOT to be
    carried forward. It is set at a ten-base-pair parent duplex: an EMPTY value is a reading at that
    one cut and NOT a clearance …"

That sentence describes TWO states. The file holds three. Nine rows at the two intron-2 cryptic-exon
seams carry an empty `do_not_order`, an empty duplex cell and an empty parent-pairing flag because
the mature-parent screen was NEVER RUN over them — §2.6's words are that "their counts are absent
rather than low and must not be read beside the panel's". For those nine the header's sentence is
false: an empty value there is not a reading at one cut, it is no reading at all. ⚠ AND AN ABSENT
READING IS NOT A READING OF ABSENCE — the most dangerous cell in an order sheet is one that looks
like a measured clearance and is not.

⚠ A FOURTH COMBINATION EXISTS AND IS NOT A FOURTH STATE. One row at the same seams
(`TGATGAGGGCCTTGTG`) has a blank duplex cell AND a condemnation, because it is condemned for the
un-rearranged-allele reason rather than by the duplex criterion. So the duplex cell alone never
determines the verdict, in either direction — which is precisely what the header must say.

★ WHAT THIS ASSERTS, AND WHAT IT DELIBERATELY DOES NOT. It asserts the PROPERTY — a third state
exists, it is distinguishable from both a clearance and a condemnation, and the header gives all
three a meaning — and NOT any particular sentinel token. `aso_sequence_manifest.py` is introducing a
visible sentinel for the third state concurrently; whatever token it picks, the contract is that the
token appears in the header, or (if the cells stay blank) that the header says a blank in that
column can mean "not measured". A guard written around one token would have to be rewritten by the
same commit it is supposed to check.
"""
from __future__ import annotations

import csv
import io
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
CSV = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-sequences.csv")
NULL = os.path.join(REPO, "research", "modalities", "aso-parent-null.json")

#: The columns a reader takes a verdict from. `do_not_order` is the verdict; the other two are what
#: the verdict is set from, and all three are blank on the unmeasured rows.
_DUPLEX = "mature_parent_duplex_through_gap_bp"
_FLAG = "pairs_a_wild_type_parent_through_the_gap"
_VERDICT = "do_not_order"
_VERDICT_COLUMNS = (_DUPLEX, _FLAG, _VERDICT)

#: Any phrasing that admits a cell may carry no measurement at all. This is the class of statement
#: the header owes the third state; the words are open because the wording is not the property.
_NOT_MEASURED = re.compile(
    r"\bno reading\b|\bnot a reading\b|\bnot computed\b|\bdoes not compute\b|\bnot screened\b"
    r"|\bnot (?:been )?measured\b|\bno measurement\b|\bnever (?:run|measured|screened)\b"
    r"|\bwas not run\b|\bdid not run\b|\babsent rather than\b|\bnot applicable\b|\bunmeasured\b",
    re.I)

#: A claim that an absent cell IS a reading — true of a cleared row and false of an unmeasured one.
_BLANK_IS_A_READING = re.compile(
    r"\b(?:empty|blank|absent|missing)\b[^.]{0,80}?\bis a reading\b"
    r"|\bis a reading\b[^.]{0,60}?\b(?:empty|blank)\b", re.I)


def _require(path):
    if not os.path.exists(path):
        pytest.fail(f"{os.path.basename(path)} is missing; the third state is unguarded")
    return path


def _raw():
    return open(_require(CSV), encoding="utf-8").read().splitlines()


def _header():
    """The comment block above the column line — the only place a reader is told how to read a cell."""
    return " ".join("\n".join(ln for ln in _raw() if ln.startswith("#")).split())


def _rows():
    body = "\n".join(ln for ln in _raw() if not ln.startswith("#"))
    return list(csv.DictReader(io.StringIO(body)))


def _cut():
    return json.load(open(_require(NULL), encoding="utf-8"))["method"]["min_duplex_bp"]


def _states():
    """The three states, partitioned on what the file itself records rather than on a token.

    CONDEMNED  — a verdict is present.
    CLEARED    — the quantity was measured and did not reach the criterion.
    UNMEASURED — the quantity is not a number, so nothing was read at any cut.
    """
    cut = _cut()
    condemned, cleared, unmeasured = [], [], []
    for row in _rows():
        measured = row[_DUPLEX].strip().isdigit()
        if row[_VERDICT].strip():
            condemned.append(row)
        elif measured and int(row[_DUPLEX]) < cut:
            cleared.append(row)
        elif not measured:
            unmeasured.append(row)
        else:                                          # measured, at the criterion, yet unflagged
            pytest.fail(
                f"row {row['sequence']} reaches the {cut}-base-pair criterion "
                f"({row[_DUPLEX]}) and carries no `{_VERDICT}` value. That is an orderable row the "
                "paper's central negative condemns, printed as though it were clear.")
    return condemned, cleared, unmeasured


def test_the_file_holds_three_verdict_states_and_not_two():
    """The partition is derived. If the third state ever emptied, this guard would be pointless."""
    condemned, cleared, unmeasured = _states()
    assert condemned and cleared and unmeasured, (
        f"the canonical file no longer holds three states: {len(condemned)} condemned, "
        f"{len(cleared)} cleared at the criterion, {len(unmeasured)} with no reading. Everything "
        "below is about telling the third from the first two.")


def test_no_unmeasured_row_reads_as_a_clearance_or_as_a_condemnation():
    """⭐ THE SUBSTANTIVE PROPERTY. A reader compares cells; the cells must differ.

    Asserted on the verdict columns as a tuple, so it holds whatever token the third state is given
    — and it fires if the third state is ever filled in with the zeros and Falses of a measured
    clearance, which is the shape the flag column carried until 2026-08-19.
    """
    condemned, cleared, unmeasured = _states()

    def cells(row):
        return tuple(row[c].strip() for c in _VERDICT_COLUMNS)

    clear_shapes = {cells(r) for r in cleared}
    collisions = sorted({cells(r) for r in unmeasured} & clear_shapes)
    assert not collisions, (
        f"{len(collisions)} unmeasured row shape(s) are cell-for-cell identical, across "
        f"{list(_VERDICT_COLUMNS)}, to a row where the screen RAN and cleared: {collisions}. A "
        "reader cannot tell an absent reading from a measured clearance, and only one of the two is "
        "safe to act on.")
    condemned_shapes = {cells(r) for r in condemned}
    assert not ({cells(r) for r in unmeasured} & condemned_shapes), (
        "an unmeasured row is cell-for-cell identical to a condemned one, so the file condemns a "
        "design on a screen that never ran over it.")


def test_the_header_gives_the_third_states_own_markers_a_meaning():
    """Whatever the third state's cells hold, the header has to define it.

    Two admissible shapes, and the guard takes either:
      * a visible sentinel — then the token itself must appear in the header; or
      * a blank cell — then the header must say, of that column, that a blank can mean the quantity
        was never measured.
    """
    _, _, unmeasured = _states()
    header = _header()
    undefined = []
    for column in _VERDICT_COLUMNS:
        markers = {row[column].strip() for row in unmeasured}
        for marker in sorted(markers):
            if marker and len(marker) <= 24:
                if marker not in header:
                    undefined.append(f"{column}={marker!r} (sentinel not defined in the header)")
            elif not marker:
                where = [s for s in re.split(r"(?<=\.)\s+", header) if column in s]
                if not any(_NOT_MEASURED.search(s) for s in where):
                    undefined.append(
                        f"{column}='' (no sentence naming this column says a blank can mean the "
                        f"quantity was never measured; {len(where)} sentence(s) name it)")
    assert not undefined, (
        f"the canonical file's header does not define what the {len(unmeasured)} unmeasured rows "
        "hold:\n  " + "\n  ".join(undefined)
        + "\n\nThose rows are at the intron-2 cryptic-exon seams, where the mature-parent screen "
          "never ran. §2.6's words are that their counts are 'absent rather than low and must not "
          "be read beside the panel's'. Either give the state a visible sentinel and name it in the "
          "header, or say in the header that a blank in that column can mean no reading was taken.")


def test_the_header_never_calls_an_absent_verdict_cell_a_reading():
    """⛔ THE DEFECTIVE SENTENCE. It is true of a cleared row and false of nine others.

    "an EMPTY value is a reading at that one cut and NOT a clearance" — the second half is the
    correct and hard-won warning, and the first half is false for every row where nothing was read.
    A sentence may keep saying it only if it also admits the unmeasured case.
    """
    header = _header()
    offenders = [s for s in re.split(r"(?<=\.)\s+", header)
                 if _BLANK_IS_A_READING.search(s) and not _NOT_MEASURED.search(s)]
    assert not offenders, (
        "the canonical file's header tells a reader that an absent verdict cell IS a reading:\n  "
        + "\n  ".join(s[:240] for s in offenders[:3])
        + "\n\nIt is not, for the rows where the screen never ran. The sentence has to be true of "
          "all three states — the reading that cleared, the reading that condemned, and the reading "
          "that was never taken.")


def test_the_duplex_cell_alone_is_never_the_verdict():
    """A blank duplex carries both verdicts in this file, so the header must route a reader elsewhere.

    Nine unmeasured rows have no verdict and one blank-duplex row is condemned outright, for the
    un-rearranged-allele reason the duplex column cannot express. A reader sorting on the duplex
    column sees the same blank for both.
    """
    condemned, _, unmeasured = _states()
    blank_and_condemned = [r for r in condemned if not r[_DUPLEX].strip().isdigit()]
    assert blank_and_condemned and unmeasured, (
        f"the file no longer holds both blank-duplex shapes ({len(blank_and_condemned)} condemned, "
        f"{len(unmeasured)} unmeasured); this test's premise has changed. Re-derive before relaxing "
        "it — the point is that the duplex cell does not determine the verdict.")
    header = _header()
    assert re.search(_VERDICT + r"[^.]{0,120}\b(?:first|verdict|means)\b", header, re.I), (
        f"the header no longer routes a reader to `{_VERDICT}` as the column the verdict is read "
        f"from. {len(blank_and_condemned)} row(s) carry a blank duplex cell AND a condemnation, so "
        "a reader who takes the duplex column for the verdict misses them.")
