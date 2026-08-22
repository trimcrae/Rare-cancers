"""The canonical sequence file must be joinable to the deposit's tables without a wrong answer.

⛔ WHY. `fusion-junction-aso-sequences.csv` exists so that nobody has to copy an oligonucleotide out
of a PDF. That only helps if a reader who joins it to a table gets the table's number back. Two
defects found on 2026-08-17 broke that in opposite directions, and neither was visible in any check:

  1. THREE PARENT-DUPLEX QUANTITIES, ONE COLUMN NAME. A mature-parent duplex found by SEARCH over
     all six parent transcripts, the gap DNA a design's OWN parent pairs by arithmetic, and that run
     plus its wing are three different measurements. The file shipped one column carrying the search
     quantity for rows sourced from the per-junction table and the arithmetic one for rows sourced
     from the gap-length artifact — the same header over two measurements, chosen by a provenance
     the CSV never printed. For the lead 16-mer two of the three read 8, from DIFFERENT genes, so
     the wrong join returns a right-looking number on the design a reader is likeliest to spot-check.

  2. TWO SPELLINGS OF ONE GEOMETRY, AND THE CONDEMNED DESIGNS WERE IN THE MINORITY SPELLING. 176
     rows said `5-6-5` and 30 said `5-6-5 (LNA-DNA-LNA)`; all three `do_not_order` designs were in
     the 30. Filtering on the majority spelling returned a 5-6-5 list with every design the paper
     condemns silently absent — a complete-looking list that is missing exactly the rows whose
     purpose is to stop somebody ordering them.

★ WHAT THIS ASSERTS. That the join works and the filters are safe, against the built tables document
rather than against the generator's own idea of itself.
"""
from __future__ import annotations

import collections
import csv
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MAN = os.path.abspath(os.path.join(HERE, ".."))
ASO = os.path.join(MAN, "aso")
CSV_PATH = os.path.join(ASO, "fusion-junction-aso-sequences.csv")
TABLES = os.path.join(ASO, "fusion-junction-aso-submission-tables.md")


def _rows():
    """Every data row of the canonical CSV, read the way a reader would.

    ⚠ THE HEADER BLOCK MOVES. It has been a 55-line `#` preamble ABOVE the header row and is now a
    block below it, so the comment filter has to be positional-agnostic — and the header itself has
    to be checked, because `csv.DictReader` will cheerfully treat the first prose line it meets as
    a header and hand back rows whose every key is wrong, which surfaces as a `KeyError` during
    collection rather than as a readable failure.
    """
    if not os.path.exists(CSV_PATH):
        pytest.fail(f"the canonical sequence file is missing: {CSV_PATH}")
    with open(CSV_PATH, encoding="utf-8") as fh:
        reader = csv.DictReader(line for line in fh if not line.lstrip().startswith("#"))
        fields = reader.fieldnames or []
        assert "sequence" in fields, (
            "the canonical CSV's first non-comment line is not its header — read as "
            f"{fields[:4]}. Every join below would silently compare the wrong columns.")
        return [r for r in reader if r.get("sequence")]


ROWS = _rows()
BY_SEQUENCE = {r["sequence"]: r for r in ROWS}

_ARCHITECTURE = re.compile(r"\d+-\d+-\d+")


def _architecture(geometry):
    """The bare wing-gap-wing architecture, with any parenthetical spelling variant stripped."""
    m = _ARCHITECTURE.search(geometry or "")
    return m.group(0) if m else (geometry or "")


def test_the_file_has_rows_at_all():
    assert len(ROWS) > 500, f"only {len(ROWS)} rows — the generator has lost a source block"


# ── 1. the three parent-duplex quantities stay distinguishable ────────────────────────────────

def test_each_parent_duplex_quantity_has_its_own_column():
    for column in ("mature_parent_duplex_through_gap_bp", "mature_parent_duplex_gene",
                   "parent_paired_gap_dna_nt", "parent_seam_hybrid_bp"):
        assert column in ROWS[0], (
            f"{column} is not a column. The three parent-duplex quantities must each be named for "
            "what they are; one shared column silently carries two measurements.")


def test_no_column_is_named_so_vaguely_that_it_invites_the_wrong_join():
    """The names this file shipped under, both of which read as 'the parent duplex' and were not."""
    for retired in ("longest_parent_duplex_bp", "parent_seam_duplex_bp", "parent_gene"):
        assert retired not in ROWS[0], (
            f"{retired} is back. It does not say WHICH parent-duplex quantity it holds, which is "
            "how one column came to carry two measurements decided by row provenance.")


#: The share of rows that must actually carry both halves of an arithmetic identity before the
#: identity has been checked on anything. ⛔ A SHARE, NOT A COUNT (2026-08-19): these read
#: `checked > 100` against yields of 750 of 780, so seven eighths of the file could have stopped
#: carrying the quantity — which is exactly the "the merge has stopped filling blanks" failure the
#: message names — and the assertion would still have passed. Same defect as the `>= 8` floor
#: against a yield of 36 one section below.
MIN_ARITHMETIC_COVERAGE = 0.80


def test_the_seam_arithmetic_is_the_complement_of_the_gap_level_margin():
    """`parent_paired_gap_dna_nt` is arithmetic, so it is checkable rather than merely carried."""
    gaps = {"5-6-5": 6, "5-8-5": 8, "5-10-5": 10}
    eligible = [r for r in ROWS if gaps.get(r["geometry"]) is not None]
    assert eligible, "no row carries a geometry this identity is defined for"
    checked = 0
    for r in eligible:
        paired, margin, gap = (r["parent_paired_gap_dna_nt"], r["gap_level_margin"],
                               gaps[r["geometry"]])
        if not paired or not margin:
            continue
        checked += 1
        assert int(paired) + int(margin) == gap, (
            f"{r['sequence']}: {paired} + {margin} != {gap}. The margin and the parent-paired run "
            "are complements within the gap; if they are not, one of them is the other quantity.")
    share = checked / len(eligible)
    assert share >= MIN_ARITHMETIC_COVERAGE, (
        f"only {checked} of {len(eligible)} rows with a known geometry ({share:.0%}) carry both a "
        f"parent-paired run and a gap-level margin, against a floor of "
        f"{MIN_ARITHMETIC_COVERAGE:.0%} — the merge has stopped filling blanks, and the identity "
        "above is being checked on whatever is left")


def test_the_seam_hybrid_is_the_paired_run_plus_one_five_nucleotide_wing():
    eligible = [r for r in ROWS if r["parent_paired_gap_dna_nt"]]
    assert eligible, "no row carries a parent-paired run at all"
    checked = 0
    for r in eligible:
        hybrid = r["parent_seam_hybrid_bp"]
        if not hybrid:
            continue
        checked += 1
        assert int(hybrid) - int(r["parent_paired_gap_dna_nt"]) == 5, (
            f"{r['sequence']}: seam hybrid {hybrid} is not the paired run "
            f"{r['parent_paired_gap_dna_nt']} plus a five-nucleotide wing — these are not the "
            "quantities their names claim")
    share = checked / len(eligible)
    assert share >= MIN_ARITHMETIC_COVERAGE, (
        f"only {checked} of {len(eligible)} rows carrying a parent-paired run ({share:.0%}) also "
        f"carry a seam hybrid, against a floor of {MIN_ARITHMETIC_COVERAGE:.0%}")


def test_a_design_carrying_both_eight_values_names_two_different_genes():
    """The coincidence that makes a wrong join look right must be visible in the file itself."""
    lead = BY_SEQUENCE.get("GGGCATATCATCAAAC")
    assert lead is not None, "the lead 16-mer is not in the canonical file"
    assert lead["mature_parent_duplex_through_gap_bp"] == "8"
    assert lead["parent_seam_hybrid_bp"] == "8"
    assert lead["mature_parent_duplex_gene"] == "TFG", (
        "the search quantity's gene is what distinguishes it from the seam arithmetic; without it "
        "the two 8s are indistinguishable")


# ── 2. one vocabulary per column, so a filter cannot silently drop rows ────────────────────────

def test_geometry_uses_one_spelling_per_architecture():
    spellings = {r["geometry"] for r in ROWS if r["geometry"]}
    assert spellings <= {"5-6-5", "5-8-5", "5-10-5"}, (
        f"geometry is spelled {sorted(spellings)}. Two spellings of one architecture make a filter "
        "on the common one return a list that looks complete and is not.")


def test_every_condemned_design_survives_a_filter_on_its_own_geometry():
    """The filter-safety property, stated as the hazard rather than as the spelling.

    ⚠ THE COUNT WAS 3 AND IS NOW 252, DELIBERATELY (2026-08-19). `do_not_order` used to carry only
    the three designs that pair the patient's own un-rearranged *NR4A3* allele. A blind
    order-walkthrough then followed the one selection rule the paper states for this file — rank by
    gap-level margin — and it returned designs pairing a wild-type PARENT through the whole gap,
    which Table 3 marks do-not-order and this file said nothing about. Every such row is flagged
    now. The property this test exists for was never the count; it is that a condemned design
    cannot be dropped by a filter on its own geometry, so the count assertion is replaced by one on
    the class that has a fixed size.
    """
    condemned = [r for r in ROWS if r["do_not_order"]]
    assert condemned, "no design is condemned at all — the column has stopped being written"
    allele = [r for r in condemned if "un-rearranged" in r["do_not_order"]]
    assert len(allele) == 3, (
        f"the un-rearranged-allele class is {len(allele)}, not 3; §2.6 names exactly three")
    #: ⚠ THREE REASONS SINCE ROUND 8, NOT TWO. The pre-mRNA screen's condemnations never reached
    #: this file: §3 of both papers said the two screens condemn 93 of 190 while the column carried
    #: 87, and the six missing records were five molecules, two of them at TCF12_e5__NR4A3_e3, a
    #: published exon-resolved breakpoint. This is a PARTITION assertion rather than a loosened one
    #: — every condemned row must still carry exactly one stated reason, and the three classes must
    #: still account for the whole condemned set with nothing over.
    parent = [r for r in condemned if "wild-type parent gene" in r["do_not_order"]]
    premrna = [r for r in condemned if "parent precursor RNA" in r["do_not_order"]]
    assert parent and premrna, "a stated condemnation class has stopped being written"
    for r in condemned:
        reasons = sum((r in allele, r in parent, r in premrna))
        assert reasons == 1, (
            f"{r['sequence']} carries {reasons} of the three stated condemnation reasons; "
            "each condemned row must carry exactly one")
    assert len(allele) + len(parent) + len(premrna) == len(condemned), (
        "every condemned row must carry one of the three stated reasons")
    for r in condemned:
        kept = [x for x in ROWS if x["geometry"] == r["geometry"]]
        assert r in kept, (
            f"{r['sequence']} is condemned but is dropped by a filter on its own geometry "
            f"{r['geometry']!r} — the spelling is inconsistent with the rest of the file")
        #: ⛔ THE MINORITY IS RELATIVE TO ITS OWN ARCHITECTURE, NOT TO THE FILE. This read
        #: `len(kept) > 50`, an absolute count that says nothing about whether a spelling is the
        #: minority one: the historical defect was 30 rows saying "5-6-5 (LNA-DNA-LNA)" beside 176
        #: saying "5-6-5", and a variant holding 87 of 206 rows of one architecture would clear any
        #: fixed count while still being the spelling a reader's filter misses. What has to hold is
        #: that a condemned row carries the DOMINANT spelling of its own architecture.
        architecture = _architecture(r["geometry"])
        siblings = collections.Counter(
            x["geometry"] for x in ROWS if _architecture(x["geometry"]) == architecture)
        dominant, dominant_n = siblings.most_common(1)[0]
        assert r["geometry"] == dominant, (
            f"{r['sequence']} is condemned and carries geometry {r['geometry']!r} "
            f"({siblings[r['geometry']]} rows) while the dominant spelling of the {architecture} "
            f"architecture is {dominant!r} ({dominant_n} rows). A reader filtering on the common "
            "spelling gets a list that looks complete and is missing exactly the forbidden rows.")


# ── 3. the join to the built tables actually returns the table's number ────────────────────────

#: Table cells print the duplex as `8 bp (*TFG*)` or `8 (*TFG*)`, and a measured zero as `0 bp`
#: or `0` with no gene.
#:
#: ⛔ THE ZERO FORM IS THE ONE THAT CAUGHT THE DEFECT, so it is matched here rather than skipped as
#: an unparseable cell. The shipped canonical file gave 9 bp and 10 bp for the 5-8-5 and 5-10-5
#: gap-length controls — designs Table 5 prints as named rows — where the paper prints no duplex at
#: all. Those two rows ARE the paper's gap-length result: a longer gap removes the through-gap
#: parent duplex. A reader checking that result against the deposit's own machine-readable record
#: would have found it contradicted, and a parser that only matched `N (*GENE*)` cells would have
#: passed over exactly the two rows where the file and the paper disagreed.
#:
#: ⛔⛔ AND THE MARKER FORM IS WHY IT HAD TO BE WIDENED (2026-08-19). The pattern ended at `$`
#: immediately after the optional gene, so a cell reading `11 (*NR4A3*) ⚑` did not match and was
#: dropped with a bare `if m:`. Fifteen of the 51 duplex cells in the tables document carry that
#: trailing ⚑ — and ⚑ is the DO-NOT-ORDER marker, so the rows the join was silently skipping were
#: precisely the condemned ones, the rows where a table and the canonical file disagreeing is most
#: dangerous. The parse now tolerates any trailing marker glyph, and `_table_duplex_claims` fails
#: on a duplex-looking cell it cannot read instead of passing over it.
#:
#: ⛔⛔ AND IT HAD TO BE WIDENED AGAIN THE SAME DAY (2026-08-19, lane C2). The generator began
#: appending a SECOND CUT's verdict to the cell — `8 bp (*TFG*); liable at seven`, `0 bp; clear at
#: seven` — and eleven cells stopped parsing, ten of them the paper's named reagents. The trailing
#: clause is not noise to be tolerated: it is a CLAIM, and it is derivable from the same cell, so
#: it is captured and asserted below rather than skipped over. A parser widened only to keep
#: quiet is how the ⚑ rows were lost the first time.
_DUPLEX_CELL = re.compile(
    r"^\s*(\d+)(?:\s*bp)?\s*(?:\(\*([A-Z0-9]+)\*\))?\s*[†‡⚑◆◇★*¹²³⁴⁵⁶⁷⁸⁹\s]*"
    r"(?:;\s*(liable|clear)\s+at\s+([a-z]+)\s*)?[†‡⚑◆◇★*¹²³⁴⁵⁶⁷⁸⁹\s]*$")

#: number words the cut clause may spell, so the guard follows a re-cut table instead of pinning 7
_CUT_WORD = {"six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
             "thirteen": 13}

#: A cell is a duplex CLAIM if it carries the unit or a gene. A bare numeral is not: margins,
#: counts and coverage figures are numerals too, and a bare `0` would sweep in every zero in the row.
_LOOKS_LIKE_A_DUPLEX_CELL = re.compile(r"\bbp\b|\(\*")

_SEQUENCE_CELL = re.compile(r"5[′'](-)?[ACGT]{12,25}(-)?3[′']")


def _sequence_bearing_rows():
    """Every pipe row of the built tables document that prints exactly one oligonucleotide.

    ⛔ NOT A SKIP IF THE DOCUMENT IS ABSENT. `fusion-junction-aso-submission-tables.md` is a
    committed, generated deposit artefact; if it is missing, the deposit cannot ship and this join
    is unchecked. Skipping would report that as "nothing to check".
    """
    assert os.path.exists(TABLES), (
        f"the submission tables document is missing: {TABLES}. It is a deposit artefact and this "
        "join test exists to compare it against the canonical sequence file; a missing file is a "
        "finding, not a reason to stop checking.")
    rows = []
    for line in open(TABLES, encoding="utf-8"):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        seqs = [re.sub(r"^5[′']-|-3[′']$", "", c) for c in cells
                if re.fullmatch(r"5[′']-[ACGT]{12,25}-3[′']", c)]
        if len(seqs) == 1:
            rows.append((seqs[0], cells))
    return rows


def _table_duplex_claims():
    """(sequence, bp, gene) for every table row printing both a sequence and a parent duplex."""
    claims = []
    for sequence, cells in _sequence_bearing_rows():
        for cell in cells:
            if not _LOOKS_LIKE_A_DUPLEX_CELL.search(cell):
                continue
            m = _DUPLEX_CELL.match(cell)
            if m:
                claims.append((sequence, int(m.group(1)), m.group(2) or ""))
    return claims


def _table_cut_verdicts():
    """(sequence, bp, verdict, cut_bp) for every duplex cell that also states a second-cut reading."""
    out = []
    for sequence, cells in _sequence_bearing_rows():
        for cell in cells:
            m = _DUPLEX_CELL.match(cell) if _LOOKS_LIKE_A_DUPLEX_CELL.search(cell) else None
            if m and m.group(3):
                out.append((sequence, int(m.group(1)), m.group(3), m.group(4), cell))
    return out


def test_the_second_cut_verdict_a_cell_states_is_the_one_its_own_length_implies():
    """⭐ THE CLAUSE IS READ, NOT TOLERATED (2026-08-19, lane C2).

    `8 bp (*TFG*); liable at seven` states TWO things: a duplex length, and a verdict at a cut
    other than the one the paper reports throughout. The second is not free — a length of 8 is
    liable at seven and a length of 0 is clear at it — so a cell whose clause disagrees with its
    own number is a table telling a reader two different things about one molecule, which is the
    hazard this whole file exists for.

    ⚠ THE CUT IS READ OUT OF THE CLAUSE, never typed here, so re-cutting the table moves the
    guard with it instead of turning it red.
    """
    verdicts = _table_cut_verdicts()
    assert verdicts, (
        "no duplex cell states a second-cut verdict. If the generator stopped printing the "
        "'liable/clear at <cut>' clause that is a real change and this test should be re-derived "
        "against the new form — not deleted, and not left matching nothing.")
    unknown = sorted({word for _, _, _, word, _ in verdicts if word not in _CUT_WORD})
    assert not unknown, (
        f"a duplex cell states its verdict at a cut this file cannot read: {unknown}. Add the "
        "number word to _CUT_WORD; do not let an unreadable cut pass as agreement.")
    wrong = [(seq, cell) for seq, bp, verdict, word, cell in verdicts
             if (bp >= _CUT_WORD[word]) != (verdict == "liable")]
    assert not wrong, (
        f"{len(wrong)} duplex cell(s) state a second-cut verdict their own printed length "
        "contradicts:\n  " + "\n  ".join(f"{s}: {c!r}" for s, c in wrong[:8])
        + "\n\nA parent duplex of L base pairs is liable at a cut of C exactly when L >= C.")


#: The share of sequence-bearing table rows that carry a joinable parent-duplex cell. MEASURED
#: 2026-08-19 on the generated tables document: 93 rows print exactly one oligonucleotide and 51
#: duplex cells among them parse, a ratio of 0.55. A ratio rather than a count because the tables
#: are regenerated and grow — the previous floor of 8 stood against a yield of 36, so four fifths
#: of the join could have been lost without the guard noticing. 0.25 is set well under the measured
#: ratio because not every table prints a duplex column at all.
MIN_DUPLEX_CLAIM_SHARE = 0.25


def test_the_tables_print_duplex_figures_this_file_can_be_joined_to():
    rows = _sequence_bearing_rows()
    claims = _table_duplex_claims()
    assert rows, (
        "no row of the tables document prints exactly one oligonucleotide, so the parser has lost "
        "the tables' shape entirely and every join assertion below is vacuous")
    share = len(claims) / len(rows)
    assert share >= MIN_DUPLEX_CLAIM_SHARE, (
        f"only {len(claims)} of {len(rows)} sequence-bearing table rows ({share:.0%}) pair a "
        f"sequence with a parent-duplex cell this file can be joined to, against a floor of "
        f"{MIN_DUPLEX_CLAIM_SHARE:.0%} — the parser has lost the tables' shape and this join test "
        "is no longer checking what it claims to. Check the duplex cell format before relaxing it.")


def test_no_duplex_looking_cell_is_silently_dropped_from_the_join():
    """⛔ THE DROP IS THE DEFECT, NOT THE MISMATCH. A cell the parser cannot read is not compared
    with anything, and every one of the fifteen it could not read before 2026-08-19 carried ⚑."""
    unreadable = []
    for sequence, cells in _sequence_bearing_rows():
        for cell in cells:
            if _LOOKS_LIKE_A_DUPLEX_CELL.search(cell) and not _DUPLEX_CELL.match(cell):
                unreadable.append((sequence, cell))
    assert not unreadable, (
        f"{len(unreadable)} table cell(s) carry a parent-duplex unit or gene and cannot be parsed, "
        "so they are compared against the canonical file by nothing:\n  "
        + "\n  ".join(f"{s}: {c!r}" for s, c in unreadable[:10])
        + "\n\nWiden _DUPLEX_CELL to read the new form. Do NOT let it fall through silently — the "
          "rows that stopped parsing last time were the condemned ones.")


@pytest.mark.parametrize("claim", _table_duplex_claims(), ids=lambda c: f"{c[0]}:{c[1]}bp")
def test_every_duplex_figure_a_table_prints_matches_the_canonical_file(claim):
    seq, bp, gene = claim
    row = BY_SEQUENCE.get(seq)
    assert row is not None, f"{seq} is printed in a table and is not in the canonical file"
    assert row["mature_parent_duplex_through_gap_bp"] == str(bp), (
        f"{seq}: the tables print {bp} bp, the canonical file says "
        f"{row['mature_parent_duplex_through_gap_bp']!r} for the same quantity. A reader joining "
        "the two gets a different number than the paper printed.")
    assert row["mature_parent_duplex_gene"] == gene, (
        f"{seq}: the tables name {gene or 'no gene'} as the parent forming the duplex, the "
        f"canonical file names {row['mature_parent_duplex_gene']!r}")
