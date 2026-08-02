"""Regression tests for the cross-document numeric-consistency linter.

Two properties matter, and they pull against each other:

  1. It must CATCH a superseded value restated somewhere the correction did not reach.
     That is the whole failure mode -- on 2026-07-25 the repo held the ladder total at
     three different values at once, a high band that did not sum, and a table whose
     missing row produced a plausible-but-wrong total that then leaked into the plan.

  2. It must PASS a correctly-written retraction. A linter that flags "2.10x, not 2.42x"
     is a linter that gets switched off, and an ignored linter is worse than none --
     the same lesson that shaped lint_claims.py.

So every clearing path gets a test in both directions.
"""

import json
import os
import sys

import pytest

_HERE = os.path.abspath(__file__)  # research/modalities/tests/test_lint_consistency.py
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))
sys.path.insert(0, os.path.join(REPO, "research", "manuscripts"))

# NOT importorskip: stdlib-only, so a failed import is a real breakage.
import lint_consistency as lc  # noqa: E402


def _reg(tmp_path, **over):
    reg = {
        "targets": ["doc.md"],
        "supersession_markers": ["supersed", "retired", "previously"],
        "derivations": [],
        "table_completeness": [],
        "superseded": [
            {"id": "t", "pattern": r"\$128\b", "current": "$194", "retired_by": "a missing row"}
        ],
    }
    reg.update(over)
    p = tmp_path / "reg.json"
    p.write_text(json.dumps(reg), encoding="utf-8")
    return str(p)


def _run(tmp_path, text, **over):
    (tmp_path / "doc.md").write_text(text, encoding="utf-8")
    reg = json.loads(open(_reg(tmp_path, **over), encoding="utf-8").read())
    return lc.check_superseded(reg, repo=str(tmp_path))


# --------------------------------------------------------------------------
# It must CATCH
# --------------------------------------------------------------------------
def test_bare_superseded_value_is_an_error(tmp_path):
    out = _run(tmp_path, "The whole gated ladder is $128 for the priceable stages.\n")
    assert len(out) == 1 and out[0]["rule"] == "S-t"


def test_catches_it_even_inside_a_table_row(tmp_path):
    out = _run(tmp_path, "| total | $128 | GO at every gate |\n")
    assert len(out) == 1


def test_a_marker_three_lines_away_does_not_clear(tmp_path):
    """The window is deliberately small. A disclaimer paragraphs away is not a disclaimer."""
    out = _run(tmp_path, "superseded\n\n\n\nthe ladder is $128\n")
    assert len(out) == 1


# --------------------------------------------------------------------------
# It must PASS a correctly-written retraction
# --------------------------------------------------------------------------
def test_marker_on_the_same_line_clears(tmp_path):
    assert _run(tmp_path, "Superseded: the $128 total.\n") == []


def test_marker_on_a_wrapped_previous_line_clears(tmp_path):
    """Markdown wraps mid-sentence, so the marker routinely lands on a neighbouring line."""
    text = "This figure is superseded and retained only\nfor the record: $128.\n"
    assert _run(tmp_path, text) == []


def test_local_negation_clears_a_contrast(tmp_path):
    """'the total is $194, not $128' is the CORRECT way to write the correction."""
    assert _run(tmp_path, "The pinned total is $194, not $128.\n") == []


def test_enclosing_heading_clears_a_whole_retraction_section(tmp_path):
    """Appendix-A-style sections should not need the disclaimer repeated on every row."""
    text = "## Appendix A — superseded numbers\n\n| 1 | ladder total $128 | fixed |\n"
    assert _run(tmp_path, text, supersession_markers=["supersed"]) == []


def test_a_marker_far_away_on_the_SAME_physical_line_does_not_clear(tmp_path):
    """★★ THE REAL BUG, from the real file that hid it (2026-07-31).

    Clearing was scoped to a WINDOW OF LINES. `degrader-paper-schedule.json` stores each entry as one
    enormous single line, so that window was the whole entry — thousands of characters — and an unrelated
    "Superseded framing:" elsewhere in the same entry FALSELY CLEARED three genuinely stale panel counts
    ("R1, 18 legs" after prereg AMENDMENT 4 made it 16). A linter that vouches for a stale number is worse
    than no linter: it is the exact failure class CLAUDE.md §1 built it to catch, and nobody would have
    known if the counts had not been read by hand.

    ⚠ NOTE WHAT WOULD NOT HAVE FIXED IT. Scoping to "the enclosing JSON value" is no help here — the false
    clear happened INSIDE one string value. The unit that actually means "this retraction covers this text"
    is ADJACENCY, so proximity is now measured in CHARACTERS from the match, not in whole lines.
    """
    # The real shape: one line, a legitimate marker for a DIFFERENT figure, then the stale one far later.
    filler = "x" * 3000
    text = ('{"note": "Superseded framing: the old gate wording named valB_full. ' + filler +
            ' AUTHORIZED SCOPE IS ARM E ONLY -- R1, $128 legs"}\n')
    out = _run(tmp_path, text)
    assert len(out) == 1, "a marker 3,000 characters away is not a disclaimer of this figure"


def test_a_nearby_marker_on_a_long_line_still_clears(tmp_path):
    """The other direction, because over-tightening is how a linter gets switched off: a marker written
    right beside the figure must still clear it, even on a very long line."""
    filler = "y" * 3000
    text = ('{"note": "' + filler + ' the ladder was $128, superseded -- see the 2026-07-25 repricing"}\n')
    assert _run(tmp_path, text) == []


def test_negation_lookback_is_bounded(tmp_path):
    """A 'not' far earlier in the sentence must NOT clear a later assertion."""
    text = ("It is not the market rate that changed here at all, and separately "
            "the whole gated ladder is $128.\n")
    assert len(_run(tmp_path, text)) == 1


# --------------------------------------------------------------------------
# Derivation: a total must equal its parts
# --------------------------------------------------------------------------
def _tool(tmp_path, rows):
    d = {"ladder": {k: {"plan_usd": m, "range_usd": [lo, hi]} for k, (lo, m, hi) in rows.items()}}
    d["total_plan_usd"] = sum(v["plan_usd"] for v in d["ladder"].values())
    d["total_range_usd"] = [sum(v["range_usd"][0] for v in d["ladder"].values()),
                            sum(v["range_usd"][1] for v in d["ladder"].values())]
    os.makedirs(tmp_path / "t", exist_ok=True)
    (tmp_path / "t" / "tool.json").write_text(json.dumps(d), encoding="utf-8")
    return "t/tool.json"


def _deriv(tmp_path, rows, mid, low, high, doc_text=None):
    tj = _tool(tmp_path, rows)
    # By default the doc states exactly the total being asserted, so the D3
    # "every doc must quote the same total" check is satisfied and each test
    # isolates the arithmetic it is actually about.
    if doc_text is None:
        doc_text = f"total ~${mid} (~${low}–{high})\n"
    (tmp_path / "doc.md").write_text(doc_text, encoding="utf-8")
    reg = {
        "derivations": [{
            "id": "d", "tool_json": tj,
            "non_tool_stages": {"cpu": [0.0, 10.0, 20.0]},
            "expect_mid": mid, "expect_low": low, "expect_high": high,
            "tolerance_usd": 1.0, "must_appear_in": ["doc.md"],
        }]
    }
    return lc.check_derivations(reg, repo=str(tmp_path))


def test_derivation_passes_when_the_total_sums(tmp_path):
    # rows: 5..90..180  + cpu 0..10..20  => 5 / 100 / 200
    out = _deriv(tmp_path, {"a": (5.0, 90.0, 180.0)}, mid=100, low=5, high=200)
    assert out == []


def test_derivation_catches_a_high_band_that_does_not_sum(tmp_path):
    """The $544-vs-$561 bug: rows sum to one thing, the printed band says another."""
    out = _deriv(tmp_path, {"a": (5.0, 90.0, 180.0)}, mid=100, low=5, high=150,
                 doc_text="total ~$100 (~$5–150)\n")
    assert any(f["rule"] == "D-ladder-total" for f in out)


def test_derivation_requires_every_declared_doc_to_state_the_same_total(tmp_path):
    """$194 in two files and $128 in a third is the bug this catches."""
    out = _deriv(tmp_path, {"a": (5.0, 90.0, 180.0)}, mid=100, low=5, high=200,
                 doc_text="the ladder is ~$128\n")
    assert any(f["rule"] == "D-total-not-stated" for f in out)


def test_derivation_catches_a_tool_whose_own_total_drifts_from_its_rows(tmp_path):
    tj = _tool(tmp_path, {"a": (5.0, 90.0, 180.0)})
    blob = json.loads((tmp_path / tj).read_text(encoding="utf-8"))
    blob["total_plan_usd"] = 42.0          # corrupt it
    (tmp_path / tj).write_text(json.dumps(blob), encoding="utf-8")
    (tmp_path / "doc.md").write_text("total ~$100 (~$5–200)\n", encoding="utf-8")
    reg = {"derivations": [{
        "id": "d", "tool_json": tj, "non_tool_stages": {"cpu": [0.0, 10.0, 20.0]},
        "expect_mid": 100, "expect_low": 5, "expect_high": 200,
        "tolerance_usd": 1.0, "must_appear_in": ["doc.md"]}]}
    out = lc.check_derivations(reg, repo=str(tmp_path))
    assert any(f["rule"] == "D-tool-total-mismatch" for f in out)


# --------------------------------------------------------------------------
# Table completeness: the exact shape of the $128 bug
# --------------------------------------------------------------------------
def _table_reg(tmp_path, tj):
    return {"table_completeness": [{
        "id": "t", "file": "tbl.md", "section": "## 6. LADDER", "tool_json": tj,
        "row_key_hints": {}, "tolerance_usd": 1.0}]}


def test_table_completeness_passes_when_every_row_is_present(tmp_path):
    tj = _tool(tmp_path, {"alpha": (1.0, 10.0, 20.0), "beta": (2.0, 20.0, 40.0)})
    (tmp_path / "tbl.md").write_text(
        "## 6. LADDER\n\n| alpha | 10 |\n| beta | 20 |\n| **TOTAL** | ~$30 |\n", encoding="utf-8")
    assert lc.check_table_completeness(_table_reg(tmp_path, tj), repo=str(tmp_path)) == []


def test_table_completeness_catches_a_missing_row(tmp_path):
    """Dropping 5c made the table read $128; the total still looked plausible."""
    tj = _tool(tmp_path, {"alpha": (1.0, 10.0, 20.0), "beta": (2.0, 20.0, 40.0)})
    (tmp_path / "tbl.md").write_text(
        "## 6. LADDER\n\n| alpha | 10 |\n| **TOTAL** | ~$10 |\n", encoding="utf-8")
    out = lc.check_table_completeness(_table_reg(tmp_path, tj), repo=str(tmp_path))
    assert any(f["rule"] == "T-missing-row" for f in out)
    assert any(f["rule"] == "T-total-mismatch" for f in out)


def test_missing_row_is_not_cleared_by_prose_that_mentions_the_stage(tmp_path):
    """THE ESCAPE THAT ACTUALLY HAPPENED. First version of this check searched the whole
    section, and the section's own note said "previously omitted the `5c` row" -- so
    deleting the 5c row still passed. Rows only, never the prose around them."""
    tj = _tool(tmp_path, {"alpha": (1.0, 10.0, 20.0), "beta": (2.0, 20.0, 40.0)})
    (tmp_path / "tbl.md").write_text(
        "## 6. LADDER\n\nNote: this table once omitted the beta row.\n\n"
        "| alpha | **10** |\n| **TOTAL** | ~$30 |\n", encoding="utf-8")
    out = lc.check_table_completeness(_table_reg(tmp_path, tj), repo=str(tmp_path))
    assert any(f["rule"] == "T-missing-row" for f in out), "prose mentioning the stage must not clear it"


def test_rows_must_sum_to_the_printed_total(tmp_path):
    """The decisive check: a deleted row leaves a total that still matches the tool if
    nobody re-added the column. Only the table's internal sum catches that."""
    tj = _tool(tmp_path, {"alpha": (1.0, 10.0, 20.0), "beta": (2.0, 20.0, 40.0)})
    (tmp_path / "tbl.md").write_text(
        "## 6. LADDER\n\n| alpha | **10** |\n| beta | **20** |\n| **TOTAL** | ~$99 |\n",
        encoding="utf-8")
    out = lc.check_table_completeness(_table_reg(tmp_path, tj), repo=str(tmp_path))
    assert any(f["rule"] == "T-rows-do-not-sum" for f in out)


# --------------------------------------------------------------------------
# X: a summary must not contradict what it summarises
# --------------------------------------------------------------------------
_SUBSET = {"subset_checks": [{
    "id": "spine", "file": "doc.md",
    "superset_name": "ladder", "superset_pattern": r"Cum\. ~\$([0-9]+)",
    "subset_name": "spine", "subset_pattern": r"Cum ~\$([0-9]+)"}]}


def test_subset_passes_when_the_summary_agrees(tmp_path):
    (tmp_path / "doc.md").write_text(
        "Cum. ~$13\nCum. ~$48\nCum. ~$194\n\n```\nRUNG3 (Cum ~$48)\nend (Cum ~$194)\n```\n",
        encoding="utf-8")
    assert lc.check_subsets(_SUBSET, repo=str(tmp_path)) == []


def test_subset_catches_a_spine_that_contradicts_the_ladder(tmp_path):
    """$97 in the spine against $48 in the ladder -- the real 2026-07-25 bug."""
    (tmp_path / "doc.md").write_text(
        "Cum. ~$13\nCum. ~$48\nCum. ~$194\n\n```\nRUNG3 (Cum ~$97)\n```\n", encoding="utf-8")
    out = lc.check_subsets(_SUBSET, repo=str(tmp_path))
    assert any(f["rule"] == "X-summary-contradicts-source" for f in out)
    assert "97" in out[0]["message"]


def test_subset_fails_loudly_if_a_pattern_matches_nothing(tmp_path):
    """A reformat that breaks the regex must fail, not silently pass forever."""
    (tmp_path / "doc.md").write_text("no cumulative values here at all\n", encoding="utf-8")
    out = lc.check_subsets(_SUBSET, repo=str(tmp_path))
    assert any(f["rule"] == "X-pattern-found-nothing" for f in out)


# --------------------------------------------------------------------------
# The gate that matters
# --------------------------------------------------------------------------
def test_the_real_repo_is_consistent():
    """nr4a3-program-map.md, pricing.md, bid-strategy.md, CLAUDE.md, the schedule, the paper, the SI
    and the NR-V04 prereg must agree on every pinned figure. This is the check that
    actually prevents the 2026-07-25 mess from recurring."""
    findings = lc.lint(REPO)
    errors = [f for f in findings if f["severity"] == "ERROR"]
    assert not errors, "cross-document inconsistency:\n" + "\n".join(
        f"  {f['file']}:{f['line']} [{f['rule']}] {f['message']}" for f in errors)


def test_no_marker_clears_a_reprice_style_assertion():
    """THE OTHER ESCAPE THAT ACTUALLY HAPPENED. 'REPRICED' was in the marker list, so an
    injected '★ REPRICED → ~$128 mid-range' CLEARED ITSELF -- the linter would have missed
    the exact bug it was written for. A marker must mean 'this value is no longer current',
    never merely 'something changed here'. This pins that policy against future additions."""
    reg = lc.load_registry()
    assertive = "★ REPRICED → ~$128 mid-range (~$36–381), corrected and now confirmed as the total."
    hits = [m for m in reg["supersession_markers"] if m.lower() in assertive.lower()]
    assert not hits, (
        f"marker(s) {hits} clear a sentence that ASSERTS a superseded value as current — "
        "see pinned-figures.json _marker_note")


def test_registry_patterns_are_not_bare_numbers():
    """Policy check: a bare number is not a pattern. Tight patterns are what keep this
    linter from crying wolf, and a loose one added later is how it starts."""
    reg = lc.load_registry()
    for e in reg["superseded"]:
        pat = e["pattern"]
        assert len(pat) > 6 and any(c in pat for c in r"\|["), (
            f"{e['id']}: pattern {pat!r} looks too loose — anchor it with $, a word, or an alternation")
