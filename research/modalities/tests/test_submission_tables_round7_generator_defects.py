#!/usr/bin/env python3
"""The three round-7 §3.7 generator defects in `submission_tables.py`, one guard each.

⛔ ALL THREE WERE INVISIBLE FROM THE RENDERED TABLE, which is why they need tests rather than a
reading. A mislabelled column reads perfectly; a missing row cannot be found by looking at the rows
that are there; and a coverage figure suppressed by a `setdefault` leaves a table whose remaining
figures still add up. Each test below therefore asserts against the ARTIFACT the generator reads,
never against a number typed here.

The three (round-7 ledger §3.7):
  1. B2-F5 — Table 6's "transcript records" column is the per-locus gap-paired HIT count, captioned
     as RefSeq annotation depth.
  2. A5-F2 — the coverage-ladder table omits `TFG_e7__NR4A3_e3`, which the coverage ladder qualifies exactly as it
     qualifies rows the table keeps.
  3. B3-F1 — a `setdefault` in `_ladder_coverage` let a ladder entry reach the table only through a
     junction no earlier entry contained, so the 94.8% bound — which adds three UNNAMED reagents and
     no junction — was deleted from the table with nothing to show it had been.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MOD))
MAN = os.path.join(REPO, "research", "manuscripts")
sys.path.insert(0, MAN)

import submission_tables as ST  # noqa: E402

TABLES = os.path.join(MAN, "aso", "fusion-junction-aso-submission-tables.md")
LADDER = os.path.join(MAN, "aso", "fusion-junction-aso-coverage-ladder.json")
EXPR = os.path.join(MOD, "aso-offtarget-tissue-expression.json")


def _tables():
    return open(TABLES, encoding="utf-8").read()


def _section(text, n):
    """The caption and rows of one table, up to the next table's caption."""
    start = text.index(f"**Table {n}.")
    nxt = text.find(f"**Table {n + 1}.", start)
    return text[start:] if nxt < 0 else text[start:nxt]


def _ladder():
    return json.load(open(LADDER, encoding="utf-8"))


def _expr():
    return json.load(open(EXPR, encoding="utf-8"))


# ──────────────────────────────────────────────────────────────────────────────
# 1 · B2-F5 — the record column is a hit count and must not be labelled otherwise
# ──────────────────────────────────────────────────────────────────────────────

def assert_table6_record_column_is_labelled_as_a_hit_count(text, expr):
    """The assertions, factored out so they can also be run against an OLD copy of the file."""
    t6 = _section(text, 6)
    hdr = next(ln for ln in t6.splitlines() if ln.startswith("| junction | gene locus |"))
    assert "gap-paired hit records" in hdr, hdr
    assert "transcript records" not in hdr, (
        "the column is the per-locus gap-paired hit count, not a count of RefSeq records", hdr)
    # and the caption must not restore the claim the header used to make
    for dead in ("Transcript records are how many accessions RefSeq",
                 "that is annotation depth",
                 "is a different axis from the"):
        assert dead not in t6, f"the annotation-depth caption is back: {dead!r}"
    # the printed total is the panel's whole gap-paired hit count, derived both ways
    total = sum(L["screen_records"]["n_transcript_records"] for L in expr["per_locus"])
    hits = sum(s["n_gap_paired_hybridisable"] for s in expr["panel"]["panel"])
    assert total == hits, (total, hits)
    assert f"the column totals {total}" in " ".join(t6.split()), t6[:400]


def test_table6_record_column_is_named_for_what_the_generator_counts():
    """⛔ `n_transcript_records` IS INCREMENTED ONCE PER GAP-PAIRED HIT, PER DESIGN.

    `aso_offtarget_tissue_expression._seam_rows` adds one for every gap-paired hit of every design
    tiled at a seam and then merges seams by addition, so the column sums to the panel's entire
    gap-paired hit count — the identity that module's own `selftest` asserts. It is therefore a
    property of what the SEARCH returned, and the two facts below are the ones the old caption
    ("how many accessions RefSeq lists for the gene, that is annotation depth") made unreadable.
    """
    expr = _expr()
    assert_table6_record_column_is_labelled_as_a_hit_count(_tables(), expr)

    rows = {L["locus"]: L for L in expr["per_locus"]}
    # *NRP1*: five records over ONE accession, because all five registers of its seam return it. If
    # the column were annotation depth this number could not depend on the design count.
    nrp1 = rows["NRP1"]
    assert nrp1["screen_records"]["n_transcript_records"] == nrp1["n_designs_hitting_it"], nrp1
    # and the record count is never below the register count, because each register contributes ≥1
    for L in expr["per_locus"]:
        assert L["screen_records"]["n_transcript_records"] >= L["n_designs_hitting_it"], L["locus"]


def test_the_generator_refuses_to_build_if_the_record_column_stops_being_a_hit_count():
    """The label is only right while the identity holds, so the identity is a build gate.

    ⚠ FIRES: the artifact is perturbed by one record and `_gap_paired_records` must raise. Without
    the guard a future upstream change could make the column mean something else and the header
    would go on asserting the old meaning, which is the defect this file is fixing.
    """
    expr = _expr()
    expr["per_locus"][0]["screen_records"]["n_transcript_records"] += 1
    with pytest.raises(SystemExit) as e:
        ST._gap_paired_records(expr)
    assert "gap-paired hit count" in str(e.value)


# ──────────────────────────────────────────────────────────────────────────────
# 2 · A5-F2 — every junction the ladder qualifies has a coverage-ladder row
# ──────────────────────────────────────────────────────────────────────────────

def assert_every_qualifying_junction_has_a_ladder_row(text, ladder):
    t5 = _section(text, 5)
    for j in ladder["best_supported_buildable_panel"]["panel_membership"]["junctions"]:
        lab = j.replace("__", "::").replace("_", " ")
        assert f"| {lab} |" in t5, f"the coverage-ladder table has no row for {j}, which the ladder qualifies"


def test_the_ladder_table_carries_every_junction_the_coverage_ladder_qualifies():
    """⛔ TFG e7::NR4A3 e3 WAS THE MISSING ONE, AND NOTHING COULD NOTICE.

    The ladder's `panel_membership` applies two conditions, both read from the tables that own them:
    a published exon-resolved breakpoint, and a reagent through all five deep screens. Nine junctions
    satisfy both; `_TABLE5_ROWS` named eight. TFG e7 is in the same
    `⛔_qualifying_but_contributing_exactly_zero` bucket as PGR e2::NR4A3 e2, which HAS a row, and
    §2.3 resolves its exon from a deposited chimeric mRNA exactly as it resolves TCF12 e5's.
    """
    ladder = _ladder()
    assert_every_qualifying_junction_has_a_ladder_row(_tables(), ladder)
    assert "TFG_e7__NR4A3_e3" in (
        ladder["best_supported_buildable_panel"]["panel_membership"]["junctions"])
    # the row's cells are the artifact's, not typed here
    per = json.load(open(os.path.join(MOD, "aso-per-junction-table.json"), encoding="utf-8"))
    tfg = next(j for j in per["junctions"] if j["junction_label"] == "TFG_e7__NR4A3_e3")
    b = tfg["best_available"]
    row = next(ln for ln in _section(_tables(), 5).splitlines()
               if ln.startswith("| published seam in the panel | TFG e7::NR4A3 e3 |"))
    assert f"5′-{b['antisense_5to3']}-3′" in row, row
    assert f"| {b['gap_specificity_margin']} |" in row, row
    assert f"| {b['n_gap_paired']} → {b['n_gap_paired_loci']} |" in row, row
    # a qualifying junction whose partner is outside the denominator buys nothing, and says so
    assert "adds nothing" in row and "partner absent from the cohort" in row, row


def test_dropping_a_qualifying_junction_from_the_row_spec_fails_the_build(monkeypatch):
    """⚠ FIRES: the row spec is editorial and typed, so the guard is what makes it checkable.

    Removing TFG e7 restores the exact pre-fix state of `_TABLE5_ROWS`; the generator must refuse
    rather than emit a table captioned as complete and short a row.
    """
    monkeypatch.setattr(ST, "_TABLE5_ROWS",
                        tuple(r for r in ST._TABLE5_ROWS if r[2] != "TFG_e7__NR4A3_e3"))
    per = json.load(open(os.path.join(MOD, "aso-per-junction-table.json"), encoding="utf-8"))
    nonc = json.load(open(os.path.join(MOD, "noncoding-acceptor",
                                       "aso-noncoding-acceptor-screened-table.json"),
                          encoding="utf-8"))
    gap = json.load(open(os.path.join(MOD, "aso-gap-length-tradeoff.json"), encoding="utf-8"))
    with pytest.raises(SystemExit) as e:
        ST.table5(per, nonc, gap, _ladder())
    assert "TFG_e7__NR4A3_e3" in str(e.value)


# ──────────────────────────────────────────────────────────────────────────────
# 3 · B3-F1 — no ladder entry may be deleted by first-rung-wins
# ──────────────────────────────────────────────────────────────────────────────

def assert_every_ladder_entry_reaches_the_ladder_table(text, ladder):
    t5 = _section(text, 5)
    for rung in ladder["ladder"]:
        cell = f"{rung['coverage_percent']:.1f}%"
        assert cell in t5, f"the ladder's {rung['panel']!r} figure {cell} is in no coverage-ladder row"
        delta = rung.get("delta_percent_vs_previous")
        if delta is not None:
            assert f"{cell}" in t5 and f"(+{delta:.1f})" in t5, (rung["panel"], delta)


def test_the_94_8_bound_is_deleted_by_first_rung_wins_and_the_generator_no_longer_does_that():
    """⛔ THE DEFECT, RECONSTRUCTED FROM THE ARTIFACT, THEN THE FIX ASSERTED AGAINST THE TABLE.

    The first half rebuilds the old `out.setdefault(j, ...)` semantics and shows the *EWSR1* bound
    claims no junction at all — its junction list is identical to the rung below it, because what it
    adds is three reagents nobody can name rather than a seam. Under first-rung-wins that entry had
    no route into the table. The second half requires the generator to return it as unclaimed AND
    the rendered table to carry its figure, so reverting to `setdefault` fails here rather than
    silently dropping a row again.
    """
    ladder = _ladder()
    claimed, first_rung_wins = set(), {}
    for i, rung in enumerate(ladder["ladder"]):
        for j in rung["junctions"]:
            if j not in first_rung_wins:
                first_rung_wins[j] = i
                claimed.add(i)
    orphan = [i for i in range(len(ladder["ladder"])) if i not in claimed]
    assert orphan, "the ladder no longer has an entry that adds no junction; re-read this test"
    for i in orphan:
        r = ladder["ladder"][i]
        assert r["kind"] == "bound" and r["n_reagents_additional_unnamed"] > 0, r["panel"]

    cover, unclaimed = ST._ladder_coverage(ladder)
    assert [i for i, _ in unclaimed] == orphan, (unclaimed, orphan)
    assert_every_ladder_entry_reaches_the_ladder_table(_tables(), ladder)

    # the orphan's row names no reagent, because there is none to name
    t5 = _section(_tables(), 5)
    for i in orphan:
        r = ladder["ladder"][i]
        row = next(ln for ln in t5.splitlines() if f"{r['coverage_percent']:.1f}%" in ln)
        assert r["panel"] in row, row
        assert f"{r['n_reagents_additional_unnamed']} further reagents, none named" in row, row
        assert "5′-" not in row, "a bound with no named reagent must print no sequence"


def test_every_junction_row_still_carries_its_own_first_rung_figure():
    """⚠ THE FIX MUST NOT MOVE THE JUNCTION ROWS. "Cumulative through this row" is the coverage of
    the FIRST rung containing that junction — the two leads share one figure — and a repair that
    gave each junction its LAST rung would inflate every early row."""
    ladder, t5 = _ladder(), _section(_tables(), 5)
    cover, _ = ST._ladder_coverage(ladder)
    for i, rung in enumerate(ladder["ladder"]):
        for j in rung["junctions"]:
            assert cover[j][2] <= i, (j, cover[j], i)
    for j, (cell, _basis, idx) in cover.items():
        if idx is None:
            continue
        lab = j.replace("__", "::").replace("_", " ")
        row = next((ln for ln in t5.splitlines() if ln.startswith(f"| lead reagent | {lab} |")
                    or f"| {lab} | 5′-" in ln), None)
        assert row and cell in row, (j, cell, row)
