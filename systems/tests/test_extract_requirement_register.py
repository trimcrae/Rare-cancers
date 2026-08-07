"""The requirement-register extractor must agree with the register that already exists.

⛔ WHY THESE TESTS ARE AGAINST THE REAL CHECKOUT AND NOT AGAINST FIXTURES. CLAUDE.md §6:
*"Mock the thing under test and you test the mock."* The whole risk in this extractor is that its plain-text
projection does not reproduce what the graph already stores — in which case a run would silently rewrite
rows nobody touched. A fixture cannot see that; only the real 16 rows can.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import extract_requirement_register as ex  # noqa: E402


def _graph():
    return json.loads(ex.GRAPH.read_text())


def test_the_projection_reproduces_the_stored_plain_form_for_every_row_but_the_known_exception():
    """15 of 16 must round-trip byte-for-byte; `R11` is the one editorial exception.

    ⚠ If this ever fails on a NEW id, do not widen the exception — it means the roadmap grew a markdown
    construct the projection does not handle, and the projection is what should change.
    """
    mismatches = [r["id"] for r in _graph() if ex.plain(r["claim_ceiling_raw"]) != r["claim_ceiling"]]
    assert mismatches == ["R11"], (
        f"expected only R11 to differ (its stored plain form deliberately drops a trailing "
        f"'Superseded, retained' clause); got {mismatches}"
    )


def test_the_graph_agrees_with_the_roadmap_so_a_check_run_is_a_no_op():
    """The build gate `[M4]` and this extractor must never disagree about whether work is pending."""
    rows = ex.roadmap_rows()
    stale = [
        r["id"] for r in _graph()
        if r["id"] in rows
        and len(rows[r["id"]]) > ex.CEILING_CELL
        and rows[r["id"]][ex.CEILING_CELL] != r["claim_ceiling_raw"]
    ]
    assert stale == [], f"graph is behind the roadmap for {stale} — run systems/extract_requirement_register.py --write"


def test_every_graph_requirement_has_a_register_row_in_the_roadmap():
    """A row the extractor cannot find is a row it silently leaves stale forever, so name them loudly."""
    rows = ex.roadmap_rows()
    orphans = [r["id"] for r in _graph() if r["id"] not in rows]
    assert orphans == [], f"no roadmap register row for {orphans}"


def test_the_projection_never_leaves_markdown_emphasis_or_link_syntax_behind():
    """The stored plain form is what non-markdown consumers read; leftover syntax there is a defect."""
    for r in _graph():
        got = ex.plain(r["claim_ceiling_raw"])
        assert "**" not in got, f"{r['id']}: bold markers survived the projection"
        assert "`" not in got, f"{r['id']}: code markers survived the projection"
        assert "](" not in got, f"{r['id']}: link syntax survived the projection"
