"""No table caption may assert an architecture that the table's own sequences contradict.

⛔ WHY. On 2026-08-17 a blind screen of the built manuscript PDF filed a BLOCKER: Table 7's caption
read "Every sequence in this table is an antisense 16-mer, tiled in the 5-6-5 …/DNA/LNA architecture"
while the table's own column headers read "5-8-5 (18-mer)" and "5-10-5 (20-mer)" and its design row
printed an 18-mer and a 20-mer. Table 5 carried the same sentence over a 5-8-5 gap-length control.

⛔⛔ AND THE SENTENCE WAS ADDED AS A SAFETY FIX. A previous round found Tables 5 and 7 printing
orderable sequences with no chemistry stated, and the remedy — a clause written for the all-5-6-5
panel tables — was pasted onto them unchanged. The clause's own words are "the bases alone, ordered
as unmodified DNA, are a different molecule": this paper's whole position is that the architecture,
not the base string, IS the reagent. So the fix for an ordering hazard told a reader the wrong
architecture for two named oligonucleotides. A remedy does not become correct by being about safety,
and pasting one uniformly across items it was not written for is how it stops being true.

★ WHAT THIS ASSERTS. For every table in the built document: if its caption states a single
architecture, every sequence the table prints must actually have that architecture. Length is read
from the printed sequence itself, so the check cannot be satisfied by the generator agreeing with
itself.
"""
from __future__ import annotations

import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
TABLES = os.path.join(os.path.abspath(os.path.join(HERE, "..")), "aso",
                      "fusion-junction-aso-submission-tables.md")

#: architecture -> the oligonucleotide length it denotes. Five-nucleotide wings throughout, so the
#: name is wing + gap + wing and the length follows from it.
_ARCHITECTURE_LENGTH = {"5-6-5": 16, "5-8-5": 18, "5-10-5": 20}

_SINGLE_GEOMETRY_CLAIM = re.compile(
    r"Every sequence in this table is an antisense (\d+)-mer, tiled in the (\d+-\d+-\d+)\b")
_MIXED_GEOMETRY_CLAIM = "antisense gapmers at more than one geometry"
_SEQUENCE = re.compile(r"5[′']-([ACGT]{12,25})-3[′']")
_TABLE_OPENER = re.compile(r"^\*\*(Table \d+)\.")


def _tables():
    """(name, text) per table, split at each `**Table N.` caption opener."""
    if not os.path.exists(TABLES):
        pytest.skip("the submission tables document has not been generated")
    name, buf, out = None, [], []
    for line in open(TABLES, encoding="utf-8"):
        m = _TABLE_OPENER.match(line)
        if m:
            if name:
                out.append((name, "".join(buf)))
            name, buf = m.group(1), [line]
        elif name:
            buf.append(line)
    if name:
        out.append((name, "".join(buf)))
    return out


TABLES_FOUND = _tables()


def test_the_document_splits_into_tables_at_all():
    assert len(TABLES_FOUND) >= 7, (
        f"found {len(TABLES_FOUND)} tables — the caption parser has lost the document's shape and "
        "every check below would be vacuously true")


@pytest.mark.parametrize("name,text", TABLES_FOUND, ids=[n for n, _ in TABLES_FOUND])
def test_a_caption_claiming_one_architecture_is_true_of_every_sequence_it_prints(name, text):
    claim = _SINGLE_GEOMETRY_CLAIM.search(text)
    if not claim:
        return
    stated_len, architecture = int(claim.group(1)), claim.group(2)
    assert _ARCHITECTURE_LENGTH.get(architecture) == stated_len, (
        f"{name}: the caption says {architecture} and {stated_len}-mer, which do not correspond "
        f"({architecture} is a {_ARCHITECTURE_LENGTH.get(architecture)}-mer)")
    wrong = sorted({s for s in _SEQUENCE.findall(text) if len(s) != stated_len})
    assert not wrong, (
        f"{name}'s caption asserts every sequence is a {stated_len}-mer at {architecture}, but the "
        f"table prints {len(wrong)} sequence(s) of another length: "
        + ", ".join(f"{s} ({len(s)}-mer)" for s in wrong[:4])
        + ". Pass mixed_geometry=True to _ordering_clause() for this table.")


@pytest.mark.parametrize("name,text", TABLES_FOUND, ids=[n for n, _ in TABLES_FOUND])
def test_a_table_printing_more_than_one_length_does_not_claim_a_single_architecture(name, text):
    lengths = {len(s) for s in _SEQUENCE.findall(text)}
    if len(lengths) <= 1:
        return
    assert not _SINGLE_GEOMETRY_CLAIM.search(text), (
        f"{name} prints sequences of lengths {sorted(lengths)} and its caption still states one "
        "architecture for all of them")
    assert _MIXED_GEOMETRY_CLAIM in text, (
        f"{name} prints sequences of lengths {sorted(lengths)}, so it must say so rather than "
        "leaving a reader to assume the panel geometry")


@pytest.mark.parametrize("name,text", TABLES_FOUND, ids=[n for n, _ in TABLES_FOUND])
def test_every_table_printing_a_sequence_says_where_the_machine_readable_copy_is(name, text):
    """The other half of the ordering clause, which must survive the split into two wordings."""
    if not _SEQUENCE.search(text):
        return
    assert "fusion-junction-aso-sequences.csv" in text, (
        f"{name} prints orderable sequences and never names the canonical machine-readable file, so "
        "a reader's only route to them is transcription out of a PDF")


@pytest.mark.parametrize("name,text", TABLES_FOUND, ids=[n for n, _ in TABLES_FOUND])
def test_every_table_printing_a_sequence_states_a_backbone(name, text):
    if not _SEQUENCE.search(text):
        return
    assert "phosphorothioate" in text, (
        f"{name} prints orderable sequences without naming the backbone; ordering the bases as "
        "unmodified DNA gives a different molecule")


# ── the other caption claims in the reagent-hazard family ─────────────────────────────────────
#
# ⚠ DELIBERATELY NARROW. The repository's own linter lesson is that a checker which flags true
# statements gets ignored, which is worse than no checker. So this does NOT parse arbitrary
# "every/all/none" English out of the captions — it asserts the specific structural claims whose
# failure would put a wrong reagent in a reader's hands, which is the class the geometry defect
# belonged to.

_CONTROLS_HAVE_NO_ROW = "The three controls §4 requires have no row and can have none"

#: The three §4 controls, as Table 5's caption names them. If one ever gained a row it would appear
#: with a sequence cell like every other row, and a reader would order a control that is specified
#: as a CLASS — "a gapmer against an abundant housekeeping transcript" — or as a draw from a
#: shuffling procedure, neither of which is one molecule.
_CONTROL_ROW_LABELS = ("isogenic comparator", "positive control", "scrambled control")


def _table(name):
    for found, text in TABLES_FOUND:
        if found == name:
            return text
    pytest.skip(f"{name} is not in the built document")


def test_the_controls_that_have_no_row_really_have_none():
    text = _table("Table 5")
    if _CONTROLS_HAVE_NO_ROW not in text:
        pytest.skip("Table 5's caption no longer makes this claim")
    rows = [line for line in text.splitlines() if line.startswith("|")]
    for label in _CONTROL_ROW_LABELS:
        offenders = [r for r in rows if label in r.lower()]
        assert not offenders, (
            f"Table 5's caption says the three §4 controls have no row, but a row names "
            f"{label!r}: {offenders[0][:120]}. Either the row is wrong or the caption is.")


def test_no_table_row_carries_a_sequence_without_a_geometry_the_document_defines():
    """A sequence cell is orderable; a length the document never names is not interpretable.

    Every sequence this deposit prints is 16, 18 or 20 nucleotides, which are the three
    architectures §6 specifies. A cell of any other length means either a typesetting corruption or
    a design from a geometry nothing in the paper describes — and both reach a reader as an
    orderable string.
    """
    stray = {}
    for name, text in TABLES_FOUND:
        for seq in set(_SEQUENCE.findall(text)):
            if len(seq) not in set(_ARCHITECTURE_LENGTH.values()):
                stray.setdefault(name, []).append(f"{seq} ({len(seq)}-mer)")
    assert not stray, (
        "sequences printed at a length no architecture in this paper defines: "
        + "; ".join(f"{k}: {', '.join(v)}" for k, v in sorted(stray.items())))
