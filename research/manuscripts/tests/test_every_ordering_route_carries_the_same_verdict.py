#!/usr/bin/env python3
"""Every route a reader can take to a sequence must reach the same do-not-order verdict.

⛔⛔ WHY THIS EXISTS — THE SAME DEFECT, THREE TIMES, IN THREE DIFFERENT CARRIERS.

  2026-08-18  §2.4, §2.7 and §4.4 each named "the three" *TCF12* exon-7 designs and meant three
              different sets. A laboratory ordering from §2.4's list got a design §2.7 excludes for
              an eleven-base-pair duplex with wild-type *TCF12*.
  2026-08-19  Table 3's do-not-order key never reached the manuscript build at all, because the
              manuscript style never calls `render_float`.
  2026-08-19  (this file) A blind order-walkthrough followed the ONE selection rule the paper
              states for its canonical CSV — rank by gap-level margin — and at five of the 36 panel
              junctions it returned a design that pairs a wild-type parent through the whole
              catalytic gap at eleven base pairs, four of them against wild-type *NR4A3*. Table 3
              marks every one of those ⚑ "do not order". The CSV carried `do_not_order` on 3 of 780
              rows, and 83 rows flagged as pairing a parent carried nothing. In the same pass Table
              4 was found printing five ⚑ designs with no marker and a final column reading "yes".

★ THE PATTERN, WHICH IS WHY THIS IS A TEST AND NOT THREE FIXES. Each carrier was individually
correct: Table 3 marked its rows, §2.6 named its three, the CSV held a `role` column with the right
answer in it. The hazard is never inside one carrier — it is that a reader takes ONE route, and the
routes disagreed about which molecules must not be ordered. So the assertion is agreement across
routes, not correctness within one.

⚠ WHAT "DO NOT ORDER" MEANS HERE IS A THRESHOLD VERDICT, NOT A CLEARANCE. The flag is set at ten
base pairs; 175 of 190 panel designs pair a parent through the whole gap at seven and 181 at any
length. Every carrier must therefore say that an unflagged row is a reading at one cut — asserted
below — because a reader who takes absence of a flag for safety has been misled by a true statement.
"""
from __future__ import annotations

import csv
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
ASO = os.path.join(MANUSCRIPTS, "aso")
CSV_PATH = os.path.join(ASO, "fusion-junction-aso-sequences.csv")
FASTA = os.path.join(ASO, "fusion-junction-aso-sequences.fasta")
TABLES = os.path.join(ASO, "fusion-junction-aso-submission-tables.md")
PAPER = os.path.join(ASO, "fusion-junction-aso-research-article.md")

#: The criterion the paper is stated on.
MIN_PARENT_DUPLEX_BP = 10


def _need(path):
    if not os.path.exists(path):
        pytest.skip(f"{os.path.basename(path)} is not present in this checkout")
    return path


def _csv_rows():
    lines = [l for l in open(_need(CSV_PATH), encoding="utf-8") if not l.startswith("#")]
    return list(csv.DictReader(lines))


def test_every_parent_pairing_row_of_the_canonical_record_says_do_not_order():
    """⛔ 83 rows were flagged as pairing a wild-type parent and told a reader nothing."""
    rows = _csv_rows()
    flagged = [r for r in rows if r["pairs_a_wild_type_parent_through_the_gap"] == "True"]
    assert flagged, "no row pairs a wild-type parent — the column has stopped being computed"
    silent = [r["sequence"] for r in flagged if not r["do_not_order"]]
    assert not silent, (
        f"{len(silent)} rows pair a wild-type parent through the whole gap and carry no "
        f"`do_not_order`: {silent[:6]}. The paper tells a reader to order from this file INSTEAD "
        "of the PDF, so a verdict that lives only in Table 3 does not reach them.")


def test_the_selection_rule_the_paper_states_does_not_return_a_condemned_design():
    """★ THE WALKTHROUGH ITSELF, kept as a test rather than as a paragraph in a report.

    Rank the panel by the one rule the paper states — gap-level margin — and check what comes back.
    This is allowed to return a condemned design; what is NOT allowed is for the file to be silent
    about it, so the assertion is that every such design carries its verdict.
    """
    rows = [r for r in _csv_rows() if r["geometry"] == "5-6-5"
            and r["role"] in ("screened design", "best available at this junction")]
    by_junction: dict[str, list[dict]] = {}
    for r in rows:
        by_junction.setdefault(r["junction"], []).append(r)
    assert len(by_junction) >= 30, len(by_junction)
    unguarded = []
    for junction, group in by_junction.items():
        top = max(group, key=lambda r: (int(r["gap_level_margin"]), r["sequence"]))
        if top["pairs_a_wild_type_parent_through_the_gap"] == "True" and not top["do_not_order"]:
            unguarded.append((junction, top["sequence"]))
    assert not unguarded, (
        f"ranking by gap-level margin returns an unflagged parent-pairing design at {unguarded}")


def test_the_canonical_record_says_which_column_to_select_on():
    """The paper's answer lives in `role`, and a reader who does not know that cannot reach it."""
    rows = _csv_rows()
    assert any(r["role"] == "best available at this junction" for r in rows)
    paper = " ".join(open(_need(PAPER), encoding="utf-8").read().split())
    assert "`role` column carries" in paper, (
        "§6 must name the column that encodes the paper's own selection; gap-level margin is the "
        "only rule it states and that rule returns condemned designs")


def test_the_fasta_carries_the_verdict_and_the_role_on_the_defline():
    """A FASTA record is the form most likely to be pasted straight into an order form."""
    text = open(_need(FASTA), encoding="utf-8").read()
    deflines = [l for l in text.splitlines() if l.startswith(">")]
    assert deflines, "the FASTA holds no records"
    csv_by_seq = {r["sequence"]: r for r in _csv_rows()}
    missing_tag, missing_role = [], []
    for line in deflines:
        seq = line[1:].split()[0]
        row = csv_by_seq.get(seq)
        if row is None:
            continue
        if row["do_not_order"] and "DO NOT ORDER" not in line:
            missing_tag.append(seq)
        if row["role"] and "role=" not in line:
            missing_role.append(seq)
    assert not missing_tag, f"deflines without the do-not-order tag: {missing_tag[:6]}"
    assert not missing_role, f"deflines without `role`: {missing_role[:6]}"
    assert "AN UNTAGGED RECORD IS NOT A CLEARANCE" in text, (
        "the FASTA header must say that an untagged record is a reading at one threshold")


def _tables():
    return open(_need(TABLES), encoding="utf-8").read()


def _table_span(text, number):
    start = text.find(f"**Table {number}.")
    end = text.find(f"**Table {number + 1}.")
    return text[start:end if end > 0 else len(text)]


@pytest.mark.parametrize("number", [3, 4])
def test_a_table_printing_orderable_designs_marks_the_ones_not_to_order(number):
    """⛔ TABLE 4 IS IN THIS LIST BECAUSE IT FAILED. It printed five ⚑ designs unmarked, under a
    final column reading "yes" — a near-match verdict a reader took for a verdict on the design."""
    span = _table_span(_tables(), number)
    assert span, f"Table {number} is not in the tables file"
    csv_by_seq = {r["sequence"]: r for r in _csv_rows() if r["geometry"] == "5-6-5"}
    unmarked = []
    for line in span.splitlines():
        if not line.startswith("| 5′-"):
            continue
        seq = re.match(r"\| 5′-([ACGT]+)-3′", line)
        if not seq:
            continue
        row = csv_by_seq.get(seq.group(1))
        if row and row["pairs_a_wild_type_parent_through_the_gap"] == "True" and "⚑" not in line:
            unmarked.append(seq.group(1))
    assert not unmarked, (
        f"Table {number} prints {len(unmarked)} design(s) that pair a wild-type parent through the "
        f"whole gap with no ⚑: {unmarked}. Every table printing an orderable sequence carries the "
        "same verdict, or a reader who reads only this one is misled.")
    assert "⚑" in span, f"Table {number} lost its do-not-order marker entirely"


def test_no_carrier_lets_an_absent_marker_read_as_a_clearance():
    """The flag is a verdict at ten base pairs, and every carrier has to say so."""
    tables = _tables()
    for number in (3, 4):
        span = _table_span(tables, number)
        assert "not a clearance" in span, (
            f"Table {number}'s notes must state that an unmarked row is a reading at the "
            "ten-base-pair cut and not a clearance")


def test_the_tables_preamble_reaches_the_deposit_pdf():
    """⛔ The block that exists to be checked against was dropped from every build.

    `fusion-junction-aso-submission-tables.md` opens with three things a reader needs before the
    first row: the research-use banner, the chemistry paragraph that defines 5-6-5/5-8-5/5-10-5, and
    a "Do not order these three sequences" block that PRINTS the three condemned designs so a reader
    holding a transcribed sequence has something to check it against. `split_tables` keyed its
    blocks from `^\\*\\*Table N\\.` onward, so all three were discarded: measured 2026-08-19, the
    string "Do not order these three sequences" occurred zero times in the 66-page deposit.

    ⚠ THE CLOSEST PRINTED SEQUENCE SHARES 15 OF 16 BASES with one of the three, which is the whole
    reason that block prints them rather than describing them.
    """
    pdf = os.path.join(ASO, "fusion-junction-aso-research-article-manuscript.pdf")
    if not os.path.exists(pdf):
        pytest.skip("the deposit PDF is not built in this checkout")
    try:
        import pymupdf
    except ImportError:  # pragma: no cover - environment without the renderer
        pytest.skip("pymupdf is not installed in this sandbox")
    text = " ".join(" ".join(page.get_text().split()) for page in pymupdf.open(pdf))
    source = open(_need(TABLES), encoding="utf-8").read()
    for opener in ("Do not order these three sequences",
                   "Research use only, and not for administration to any person or animal",
                   "what the `geometry` column"):
        flat = opener.replace("`", "")
        assert flat in source.replace("`", ""), (
            f"the tables file no longer opens with {opener!r}; re-anchor this guard")
        assert flat in text, (
            f"{opener!r} is in the tables file and NOT in the built deposit — the preamble is being "
            "dropped again. It carries the three condemned sequences a reader checks a transcription "
            "against, and a reader of the PDF alone would never meet it.")
