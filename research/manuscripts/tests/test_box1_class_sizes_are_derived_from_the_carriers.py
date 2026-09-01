"""Box 1's "second class not to be ordered" is sized against the carriers, never typed.

⛔ WHY. Box 1 is the page a hurried reader stops at. Its paragraph "A second class not to be
ordered, and it is much larger" carries five counts, and on 2026-08-19 one of them was a
CONFLATION that had survived every screen:

    Box 1 said 250 records carried the do-not-order flag. RECOMPUTED from the canonical CSV: 249
    rows carry `mature_parent_duplex_through_gap_bp >= 10`; 3 more carry `do_not_order` for the
    separate un-rearranged-allele reason; 252 carry the flag in all. 250 was the count of
    `pairs_a_wild_type_parent_through_the_gap == True`, which folds in ONE cryptic-exon record
    (`TGATGAGGGCCTTGTG`) whose duplex cell is BLANK and which appears in neither Table 3 nor
    Table 4 — a row where the quantity was never measured, counted as though it had been.

The prose has been corrected. Nothing guarded it: no test in the suite read Box 1's paragraph, so
the three populations it slides between — the panel designs, the canonical file's records at the
criterion, and the records flagged for any reason — could drift apart again in silence.

★ EVERY NUMBER HERE IS DERIVED. The record counts come from the canonical CSV, the panel counts and
the loose-cut reading from `aso-parent-null.json`, and "five of the nine" from Table 4's rows joined
back to the CSV. The un-rearranged class is kept separate on purpose: it is a different reason for
the same flag, and folding it in is how 250 happened.
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
ASO = os.path.join(MANUSCRIPTS, "aso")
ARTICLE = os.path.join(ASO, "fusion-junction-aso-research-article.md")
TABLES = os.path.join(ASO, "fusion-junction-aso-submission-tables.md")
CSV = os.path.join(ASO, "fusion-junction-aso-sequences.csv")
NULL = os.path.join(REPO, "research", "modalities", "aso-parent-null.json")

#: The column Box 1 names as the one the count is reproducible from. Naming it is the whole point:
#: it is what stops the next reader reproducing 250 off a different column.
_COLUMN = "mature_parent_duplex_through_gap_bp"

_WORDS = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
          "fifteen sixteen seventeen eighteen nineteen twenty").split()


def _require(path):
    if not os.path.exists(path):
        pytest.fail(f"{os.path.basename(path)} is missing; Box 1's class sizes are unchecked")
    return path


def _rows():
    """The canonical CSV's DESIGN rows. The header block is comment lines, and they are not rows.

    ⛔ CONTROLS ARE EXCLUDED, AND THE DENOMINATOR IS WHY (2026-08-24). Box 1 sizes the do-not-order
    class against "the records the canonical file holds", and that file gained two screened control
    oligonucleotides when the condensed article started naming them. A control is not a design: it
    spans no junction and was never a candidate, so counting it in the denominator would shrink the
    reported liability rate without a single design changing — the direction that flatters the
    paper. The population this claim is about is designs, so that is the population counted here.
    """
    raw = open(_require(CSV), encoding="utf-8").read().splitlines()
    body = "\n".join(ln for ln in raw if not ln.startswith("#"))
    rows = list(csv.DictReader(io.StringIO(body)))
    return [r for r in rows if not (r.get("role") or "").startswith("control")]


def _artifact():
    return json.load(open(_require(NULL), encoding="utf-8"))


def _box1():
    text = open(_require(ARTICLE), encoding="utf-8").read()
    m = re.search(r"^##\s*Box 1\b.*?(?=^##\s)", text, flags=re.S | re.M)
    assert m, "the manuscript has no `## Box 1` section; the page a hurried reader stops at is gone"
    return " ".join(m.group(0).split())


def _class_sizes():
    """(total records, at the criterion, flagged for the other reason, flagged in all)."""
    cut = _artifact()["method"]["min_duplex_bp"]
    rows = _rows()
    at_criterion = [r for r in rows
                    if r[_COLUMN].strip().isdigit() and int(r[_COLUMN]) >= cut]
    flagged = [r for r in rows if r["do_not_order"].strip()]
    other = [r for r in flagged if r not in at_criterion]
    return len(rows), len(at_criterion), len(other), len(flagged)


def test_the_criterion_class_is_the_size_box_1_prints_over_the_denominator_it_prints():
    """"249 of the 780 records the canonical file holds" — both halves, from the file itself."""
    total, at_criterion, _, _ = _class_sizes()
    box = _box1()
    # ⛔ "design records", NOT "records" — AND THE WORD IS THE REPAIR, NOT NOISE IN THE PATTERN.
    # Round 29's arithmetic seat: the prose read "249 of the 780 records the canonical file holds"
    # while the file holds 782 and says so four times in its own header, so a reader doing what the
    # sentence says gets 257 of 782 and cannot reproduce the printed denominator. 780 is the DESIGN
    # population, and it is the right one — this guard's own docstring explains why counting the two
    # controls would shrink the reported liability rate without a single design changing.
    # ⚠ The obvious fix, 780 → 782, would have made the prose agree with the CSV header and the
    # denominator dishonest. The repair was to name the population; this pattern has to follow it,
    # in the same commit, or the honest sentence reds the guard (`paper-hardening` §8b.1: a gate
    # that reds on true input is the one its reader learns to loosen).
    printed = re.search(r"(\d+)\s+of\s+the\s+(\d+)\s+(?:design\s+)?records", box)
    assert printed, (
        f"Box 1 no longer sizes the do-not-order class against the canonical file. It should read "
        f"{at_criterion} of the {total} records; without the denominator the count is a number "
        "with no population.")
    assert (int(printed.group(1)), int(printed.group(2))) == (at_criterion, total), (
        f"Box 1 prints {printed.group(1)} of {printed.group(2)} records; the canonical CSV holds "
        f"{total} rows of which {at_criterion} carry {_COLUMN} at or above the criterion.")


def test_box_1_names_the_column_the_count_is_reproducible_from():
    """⛔ THE 250/249 CONFLATION WAS A JOIN ON THE WRONG COLUMN, and naming it is the remedy.

    The canonical file carries three parent-duplex columns and its own header warns they are not
    interchangeable. A count printed without its column is a count the next reader reproduces off
    whichever one they reach first — which is exactly how a blank-celled cryptic-exon row was
    counted as a measurement.
    """
    assert _COLUMN in _box1(), (
        f"Box 1 states the size of the do-not-order class without naming `{_COLUMN}`, the column it "
        "is reproducible from. The canonical file holds three parent-duplex columns and says in its "
        "own header that they are not interchangeable.")


def test_the_un_rearranged_class_is_kept_separate_from_the_criterion_class():
    """Two reasons for one flag. Adding them silently is how 249 became 250."""
    total, at_criterion, other, flagged = _class_sizes()
    assert at_criterion + other == flagged, (
        f"the CSV's own arithmetic no longer closes: {at_criterion} at the criterion + {other} for "
        f"the other reason ≠ {flagged} flagged. Re-derive before touching Box 1.")
    box = _box1()
    assert str(flagged) in box, (
        f"Box 1 never gives the total number of flagged records ({flagged}). A reader who filters "
        "the canonical file on `do_not_order` gets that number and must be able to find it here.")
    assert re.search(r"\b" + str(flagged) + r"\b[^.]{0,80}\b(?:flag|in all|altogether|in total)\b", box), (
        f"Box 1 prints {flagged} without saying it is the count carrying the flag IN ALL, over both "
        f"reasons. {at_criterion} of them are at the criterion and {other} are the un-rearranged "
        "allele; a reader who cannot tell which number is which reproduces neither.")
    assert at_criterion != flagged, "the two classes have merged; this test's premise has changed"
    assert re.search(r"\b" + str(at_criterion) + r"\b", box), (
        f"Box 1 no longer prints the criterion class size ({at_criterion}) at all, so the flagged "
        f"total ({flagged}) reads as though every flag were the central negative.")


def test_the_panel_counts_in_box_1_are_the_measured_ones():
    """"87 of the 190 panel designs" and, at the loose cut, "175 of the 190"."""
    observed = _artifact()["observed"]
    loose = min(_artifact()["cut_sensitivity"]["cuts_bp"])
    at_loose = _artifact()["cut_sensitivity"]["observed_n_liable"][str(loose)]
    box = _box1()

    panel = re.search(r"(\d+)\s+of\s+the\s+(\d+)\s*panel\s*designs", box)
    assert panel, (
        f"Box 1 no longer states the panel rate ({observed['n_liable']} of "
        f"{observed['n_designs']}). It is this paper's central negative.")
    assert (int(panel.group(1)), int(panel.group(2))) == (observed["n_liable"], observed["n_designs"]), (
        f"Box 1 prints {panel.group(1)} of {panel.group(2)} panel designs; aso-parent-null.json's "
        f"observed arm gives {observed['n_liable']} of {observed['n_designs']}.")

    at_cut = re.search(r"at\s+(\w+),\s*(\d+)\s+of\s+the\s+(\d+)", box)
    assert at_cut, (
        f"Box 1 no longer carries the loose-cut reading ({at_loose} of {observed['n_designs']} at "
        f"{_WORDS[loose]}). Without it 'an unmarked row is not a clearance' has no evidence beside "
        "it, and the marker reads as a verdict rather than as a reading at one cut.")
    stated_cut = at_cut.group(1).lower()
    assert stated_cut in _WORDS and _WORDS.index(stated_cut) == loose, (
        f"Box 1's second reading is stated at {stated_cut!r}; the artifact's loose cut is "
        f"{_WORDS[loose]} (aso-parent-null.json:cut_sensitivity.cuts_bp).")
    assert (int(at_cut.group(2)), int(at_cut.group(3))) == (at_loose, observed["n_designs"]), (
        f"Box 1 prints {at_cut.group(2)} of {at_cut.group(3)} at the loose cut; the artifact gives "
        f"{at_loose} of {observed['n_designs']}.")


def _table4_designs():
    """(sequence, marked ⚑) for every row of Table 4 — the designs with no sense-strand near-match."""
    text = open(_require(TABLES), encoding="utf-8").read()
    start = text.find("**Table 4.")
    assert start != -1, "Table 4 is not in the built document; Box 1's 'of the nine' has no source"
    end = text.find("**Table 5.", start)
    out = []
    for line in text[start:end if end != -1 else len(text)].splitlines():
        m = re.match(r"\|\s*5[′']-([ACGT]+)-3[′']", line)
        if m:
            out.append((m.group(1), "⚑" in line))
    return out


def test_the_share_of_table_4s_designs_in_the_do_not_order_class_is_derived():
    """"Five of the nine designs §2.4 names … are in this class."

    Derived twice over: from Table 4's ⚑ marks, and independently by joining each of its designs
    back to the canonical CSV's criterion column. If those two ever disagree the table and the file
    are telling a reader different things about the same molecule, so that is asserted first.
    """
    cut = _artifact()["method"]["min_duplex_bp"]
    by_sequence = {r["sequence"]: r for r in _rows() if r["geometry"] == "5-6-5"}
    designs = _table4_designs()
    assert designs, "Table 4 prints no design rows; this test's evidence base has moved"

    from_csv, disagreed = 0, []
    for sequence, marked in designs:
        row = by_sequence.get(sequence)
        assert row, (
            f"Table 4 prints {sequence}, which the canonical CSV has no 5-6-5 row for. The table "
            "and the file must name the same molecules.")
        liable = row[_COLUMN].strip().isdigit() and int(row[_COLUMN]) >= cut
        from_csv += liable
        if liable != marked:
            disagreed.append(sequence)
    assert not disagreed, (
        f"Table 4's ⚑ marks disagree with the canonical file's {_COLUMN} at the {cut}-base-pair "
        f"criterion for {disagreed}. One of the two carriers is misleading a reader about an "
        "orderable sequence.")

    total = len(designs)
    box = _box1()
    stated = re.search(r"(\w+)\s+of\s+the\s+(\w+)\s+designs\s+§2\.4\s+names", box)
    assert stated, (
        f"Box 1 no longer says how many of §2.4's cleanest designs are in the do-not-order class "
        f"({from_csv} of {total}). Those are the molecules a reader is most likely to carry "
        "forward, and the whole point of the paragraph is that clean-on-one-screen is not clean.")

    def value(token):
        token = token.lower()
        return int(token) if token.isdigit() else (_WORDS.index(token) if token in _WORDS else None)

    assert (value(stated.group(1)), value(stated.group(2))) == (from_csv, total), (
        f"Box 1 prints '{stated.group(1)} of the {stated.group(2)}'; derived from Table 4 joined to "
        f"the canonical file it is {_WORDS[from_csv]} of {_WORDS[total]}.")
