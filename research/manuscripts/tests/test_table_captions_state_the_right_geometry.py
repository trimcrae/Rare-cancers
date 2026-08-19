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

⛔ REPAIRED 2026-08-19 (lane C-b). Two ways this file reported PASS on an unread document:

  1. `test_a_caption_claiming_one_architecture_is_true_of_every_sequence_it_prints` matched ONE
     literal sentence — "Every sequence in this table is an antisense N-mer, tiled in the a-b-c" —
     and `return`ed silently on no match. Four of the seven tables took that early return, so the
     guard's coverage was a property of the generator's current wording rather than of the tables.
     Rewriting the clause to "All sequences here are 16-mers at 5-6-5" would have switched the
     check off in every table at once, without a single test turning red. It now PARSES the
     caption's own `N-mer` and `a-b-c` tokens, asserts that something was parsed for every table
     printing a sequence, and holds the caption's declared vocabulary against the printed lengths
     — so a caption naming one architecture is checked however it is phrased.
  2. `test_the_controls_that_have_no_row_really_have_none` opened with a `pytest.skip` keyed to an
     exact caption string. The substantive property — that no row of Table 5 names one of §4's
     three controls, none of which IS one molecule — was therefore guarded only while that string
     survived. The row check now runs unconditionally and the caption is asserted separately.
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

#: The caption's own vocabulary, read as tokens rather than as a sentence. `16-mer` states a length;
#: `5-6-5` states an architecture. Both are how this deposit names a geometry, in any wording.
_MER_TOKEN = re.compile(r"\b(\d{1,3})-mers?\b")
_ARCHITECTURE_TOKEN = re.compile(r"\b(\d+-\d+-\d+)\b")


def _tables():
    """(name, text) per table, split at each `**Table N.` caption opener."""
    if not os.path.exists(TABLES):
        # ⛔ NOT A SKIP. An absent document leaves every caption claim below unread, and a suite of
        # skips reads as green. `test_the_document_splits_into_tables_at_all` turns that into one
        # loud failure instead.
        return []
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


def _caption(text):
    """A table's caption: everything from the `**Table N.` opener down to its first row."""
    out = []
    for line in text.splitlines():
        if line.lstrip().startswith("|"):
            break
        out.append(line)
    return "\n".join(out)


@pytest.mark.parametrize("name,text", TABLES_FOUND, ids=[n for n, _ in TABLES_FOUND])
def test_every_caption_over_a_sequence_declares_a_geometry_in_its_own_vocabulary(name, text):
    """⛔ THE EARLY RETURN THIS FILE USED TO TAKE. Parsed, not pattern-matched on one sentence.

    A table printing an orderable string has to say what molecule the string denotes, and this
    deposit says it two ways at once: a length (`16-mer`) and an architecture (`5-6-5`). Both
    tokens are parsed out of the caption, something must have been parsed, and the two must
    correspond — so a caption that names an architecture whose length it misstates is caught even
    if it never uses the sentence the old regex was written against.
    """
    lengths = {len(s) for s in _SEQUENCE.findall(text)}
    if not lengths:
        return
    caption = _caption(text)
    mers = {int(m) for m in _MER_TOKEN.findall(caption)}
    architectures = set(_ARCHITECTURE_TOKEN.findall(caption))
    assert mers and architectures, (
        f"{name} prints {len(lengths)} sequence length(s) {sorted(lengths)} and its caption names "
        f"mer-lengths {sorted(mers)} and architectures {sorted(architectures)}. A caption over an "
        "orderable string must state the geometry the string is only meaningful under; parsing "
        "found none, which is also the state in which every geometry check here goes silent.")
    for architecture in sorted(architectures):
        known = _ARCHITECTURE_LENGTH.get(architecture)
        assert known is not None, (
            f"{name}'s caption names architecture {architecture}, which this deposit does not "
            "define. Add it to _ARCHITECTURE_LENGTH with its length, or the caption is naming a "
            "molecule nothing in the paper describes.")
        assert known in mers, (
            f"{name}'s caption names {architecture} but never states its length ({known}-mer) "
            f"— it states {sorted(mers)}. The two halves of the geometry must agree in the caption "
            "before they can be checked against the rows.")
    assert lengths <= mers, (
        f"{name} prints sequence(s) of length {sorted(lengths - mers)} while its caption's declared "
        f"vocabulary is {sorted(mers)}-mer. A reader has no architecture for those rows.")
    # A caption declaring exactly one geometry is a single-architecture claim however it is worded.
    if len(mers) == 1 and len(architectures) == 1:
        only = next(iter(mers))
        assert lengths == {only}, (
            f"{name}'s caption declares one geometry ({next(iter(architectures))}, {only}-mer) and "
            f"the table prints lengths {sorted(lengths)}.")


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

# ⛔ THE STRING THIS FILE USED TO SKIP ITSELF ON, kept only as the record of what it was:
#   "The three controls §4 requires have no row and can have none"
# Nothing reads it now. The row property and the caption property are separate assertions below.

#: The three §4 controls, as Table 5's caption names them. If one ever gained a row it would appear
#: with a sequence cell like every other row, and a reader would order a control that is specified
#: as a CLASS — "a gapmer against an abundant housekeeping transcript" — or as a draw from a
#: shuffling procedure, neither of which is one molecule.
_CONTROL_ROW_LABELS = ("isogenic comparator", "positive control", "scrambled control")


def _table(name):
    for found, text in TABLES_FOUND:
        if found == name:
            return text
    # ⛔ NOT A SKIP: the table's absence is itself the condition under which nothing below is
    # checked, and Table 5 is the coverage table §4 is read from.
    pytest.fail(f"{name} is not in the built document, so its caption claims are unchecked")


def test_the_controls_that_have_no_row_really_have_none():
    """⛔ THIS RAN ONLY WHILE ONE SENTENCE SURVIVED VERBATIM (repaired 2026-08-19).

    The `pytest.skip` above it keyed on the caption's exact words, so rewording the caption
    switched off the substantive check as well as the caption check. The two are now separate: the
    ROW property holds whatever the caption says, because none of §4's three controls is one
    molecule — the comparator is a cell line, the positive control a class, the scrambled control a
    draw from a procedure — so a row carrying a sequence cell for any of them is a reader ordering
    something the paper never specified.
    """
    rows = [line for line in _table("Table 5").splitlines() if line.startswith("|")]
    assert rows, "Table 5 has no rows at all; the row check below would be vacuous"
    for label in _CONTROL_ROW_LABELS:
        offenders = [r for r in rows if label in r.lower()]
        assert not offenders, (
            f"Table 5 carries a row naming {label!r}: {offenders[0][:120]}. None of §4's three "
            "controls is one molecule — the comparator is a cell line, the positive control is "
            "specified as a class and the scrambled control as a draw from a procedure — so a row "
            "for it puts a sequence cell where no sequence exists.")


def test_table_five_still_tells_a_reader_the_three_controls_have_no_row():
    """The caption half, asserted on the claim's substance rather than on its sentence.

    A reader who takes Table 5 for the whole of §4 must be told that three of §4's requirements are
    deliberately absent, or their absence reads as an omission. Any wording that names the three
    and states the absence passes.
    """
    caption = _caption(_table("Table 5")).lower()
    missing = [label for label in _CONTROL_ROW_LABELS if label not in caption]
    assert not missing, (
        f"Table 5's caption no longer names {missing} — the §4 controls it has no row for. Their "
        "absence from the table is only legible if the caption accounts for it.")
    # ⚠ THE ABSENCE PHRASE HAS TO BE ATTACHED TO THE CONTROLS. This caption says "no row" about
    # something else two sentences earlier (a qualifying junction), so a document-wide search for
    # the phrase would pass a caption that never accounts for the controls at all.
    absence = re.compile(r"\b(no row|no rows|have none|has none|none of the three|has no row)\b")
    about_controls = [s for s in re.split(r"(?<=\.)\s+", caption)
                      if "control" in s or any(l in s for l in _CONTROL_ROW_LABELS)]
    assert any(absence.search(s) for s in about_controls), (
        "Table 5's caption names §4's three controls but no sentence about them states that they "
        f"have no row here (searched {len(about_controls)} sentence(s)), so a reader cannot tell a "
        "deliberate absence from an omitted one.")


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
