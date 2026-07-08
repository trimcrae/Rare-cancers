import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import repurpose_dock_core as core  # noqa: E402


def test_done_labels_basic():
    lines = ['{"label": "rep00000", "dG_NR4A3": -7.1}',
             '{"label": "rep00001", "dG_NR4A3": null}']
    assert core.done_labels(lines) == {"rep00000", "rep00001"}


def test_done_labels_tolerates_partial_final_line():
    # a spot kill mid-append leaves a truncated last line — it must be ignored (that drug re-docks),
    # not crash the resume.
    lines = ['{"label": "rep00000", "dG_NR4A3": -7.1}',
             '',
             '{"label": "rep00001", "dG_N']            # truncated
    assert core.done_labels(lines) == {"rep00000"}


def test_done_labels_skips_records_without_label():
    lines = ['{"dG_NR4A3": -5.0}', '{"label": "", "dG_NR4A3": -5.0}', '{"label": "rep2"}']
    assert core.done_labels(lines) == {"rep2"}


def test_remaining_preserves_order_and_skips_done():
    alllabs = ["a", "b", "c", "d"]
    assert core.remaining(alllabs, {"b", "d"}) == ["a", "c"]


def test_rank_rows_most_negative_first():
    rows = [{"label": "x", "dG_NR4A3": -6.0, "handle_contacts": 5},
            {"label": "y", "dG_NR4A3": -8.2, "handle_contacts": 2},
            {"label": "z", "dG_NR4A3": -7.0, "handle_contacts": 4}]
    assert [r["label"] for r in core.rank_rows(rows)] == ["y", "z", "x"]


def test_rank_rows_ties_broken_by_handle_contacts():
    rows = [{"label": "lo", "dG_NR4A3": -7.0, "handle_contacts": 2},
            {"label": "hi", "dG_NR4A3": -7.0, "handle_contacts": 5}]
    assert [r["label"] for r in core.rank_rows(rows)] == ["hi", "lo"]


def test_rank_rows_failures_sink_to_bottom():
    rows = [{"label": "fail", "dG_NR4A3": None, "handle_contacts": 0},
            {"label": "ok", "dG_NR4A3": -5.0, "handle_contacts": 1}]
    assert [r["label"] for r in core.rank_rows(rows)] == ["ok", "fail"]


def test_summarize_counts_and_ranks():
    rows = [{"label": "a", "dG_NR4A3": None},
            {"label": "b", "dG_NR4A3": -8.0, "handle_contacts": 3},
            {"label": "c", "dG_NR4A3": -6.0, "handle_contacts": 1}]
    s = core.summarize(rows, meta={"tag": "shard-02"})
    assert s["n_candidates"] == 3 and s["n_docked"] == 2 and s["n_failed"] == 1
    assert s["tag"] == "shard-02"
    assert [r["label"] for r in s["candidates"]] == ["b", "c", "a"]
