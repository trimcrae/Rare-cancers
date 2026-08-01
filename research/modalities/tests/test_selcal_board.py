"""THE SENSITIVITY-CONTROL LANE'S BOARD ROWS — % DONE is a count, the ETA is earned or absent.

The defect these exist to prevent is not a crash: it is a number that LOOKS derived. This lane rendered
nowhere on the all-lane board while it billed (`grep -ci selcal inflight-board-all.md` -> 0), so a prose ETA
invented from a FAILURE run was quoted beside real figures for six consecutive reports. Every test here fails
if a cell can be produced without a measurement behind it.
"""
from __future__ import annotations

import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import inflight_board as IB  # noqa: E402
import selcal_board as B  # noqa: E402
import selcal_panel as SP  # noqa: E402

ARMS = [a.arm_id for a in SP.ARMS]
NSEED = len(SP.COFOLD_MODEL_SEEDS)
T0 = 1785600000.0


def _census(**per_arm):
    return {"per_arm": {a: list(per_arm.get(a, [])) for a in ARMS}}


def _arr(**per_arm):
    return {a: list(per_arm.get(a, [])) for a in ARMS}


# ── % DONE: a COUNT, and never blank while the census is readable ────────────────────────────────────────
@pytest.mark.parametrize("n", range(0, 7))
def test_pct_is_never_blank_while_the_census_is_readable(n):
    rows = B.board_rows(_census(**{ARMS[0]: list(range(1, n + 1))}), _arr(), now=T0)
    r = [x for x in rows if x["name"].startswith(ARMS[0])][0]
    assert r["pct"] == round(100.0 * n / NSEED, 1)
    assert r["pct_of"] is None, "pct_of REPLACES the percentage in the renderer; it must stay None"


def test_an_unreadable_census_renders_UNKNOWN_not_zero_percent():
    """An absent reading is not a reading of absence (§4). 0 % would say "nothing has landed", which is a
    measurement nobody made."""
    for bad in ({}, {"per_arm": None}, None):
        rows = B.board_rows(bad, _arr(), now=T0)
        assert all(r["pct"] is None and r["state"] == IB.UNKNOWN for r in rows)
        assert all("absent reading" in r["why"] for r in rows)


def test_every_arm_gets_a_row_even_with_nothing_landed():
    rows = B.board_rows(_census(), _arr(), now=T0)
    assert sorted(r["name"] for r in rows) == sorted("%s co-fold" % a for a in ARMS)


# ── ETA: refused until it is earned, and NAMES the count when it refuses ─────────────────────────────────
@pytest.mark.parametrize("n_intervals", [0, 1, 2])
def test_no_eta_below_the_interval_threshold_and_the_refusal_names_the_count(n_intervals):
    ep = [T0 + 600 * i for i in range(n_intervals + 1)] if n_intervals >= 0 else []
    rows = B.board_rows(_census(**{ARMS[0]: list(range(1, len(ep) + 1))}),
                        _arr(**{ARMS[0]: ep}), now=T0)
    r = [x for x in rows if x["name"].startswith(ARMS[0])][0]
    assert r["eta_s"] is None
    assert "ETA UNKNOWN" in r["why"]
    assert str(B.MIN_RATE_INTERVALS) in r["why"] and "MIN_RATE_INTERVALS" in r["why"]


def test_the_threshold_is_reached_not_a_permanent_refusal():
    """`ETA UNKNOWN` forever is indistinguishable from a broken estimator. Four arrivals = three intervals."""
    ep = [T0 + 600 * i for i in range(4)]
    rows = B.board_rows(_census(**{a: [1, 2, 3, 4] for a in ARMS}),
                        _arr(**{a: ep for a in ARMS}), now=T0)
    r = rows[0]
    assert r["eta_s"] == (NSEED - 4) * 600.0
    assert "ETA UNKNOWN" not in r["why"]


def test_n_arrivals_give_n_minus_1_intervals():
    """The FIRST arrival has no predecessor, so how long it took is not observable from S3 timestamps.
    Counting it would manufacture the one number this module refuses to manufacture."""
    assert B.arm_intervals([]) == []
    assert B.arm_intervals([T0]) == []
    assert B.arm_intervals([T0, T0 + 60]) == [60.0]
    assert B.arm_intervals([T0 + 120, T0, T0 + 60]) == [60.0, 60.0]  # order-independent


def test_an_unstarted_arm_makes_the_eta_a_LOWER_BOUND():
    """★ THE GCP LANE'S LESSON, in this lane's physics: the first seed of an arm pays for the MSA search and
    the model load and later seeds do not, so no measurable INTERVAL contains that cost. Projecting onto an
    arm that has produced nothing understates it."""
    ep = [T0 + 600 * i for i in range(4)]
    rows = B.board_rows(_census(**{ARMS[0]: [1, 2, 3, 4]}), _arr(**{ARMS[0]: ep}), now=T0)
    assert all("LOWER BOUND" in r["why"] for r in rows), "an arm with zero arrivals is a floor for every row"
    assert all("MSA + model-load" in r["why"] for r in rows)


def test_a_fully_started_panel_is_not_labelled_a_lower_bound():
    """The negative control: a caveat that is always on carries no information."""
    ep = [T0 + 600 * i for i in range(4)]
    rows = B.board_rows(_census(**{a: [1, 2, 3, 4] for a in ARMS}),
                        _arr(**{a: ep for a in ARMS}), now=T0)
    assert not any("LOWER BOUND" in r["why"] for r in rows)


def test_a_varying_seed_cost_is_REPORTED_not_averaged_away():
    """If the seeds do not cost the same, the mean is a summary of an unsummarisable thing."""
    ep = [T0, T0 + 60, T0 + 120, T0 + 1200]  # 60 s, 60 s, 1080 s
    rows = B.board_rows(_census(**{a: [1, 2, 3, 4] for a in ARMS}),
                        _arr(**{a: ep for a in ARMS}), now=T0)
    assert any("spread" in r["why"] for r in rows)
    q = B.quoted_rate(B.arm_intervals(ep))
    assert q["spread"] == 18.0


def test_the_rate_uses_a_trailing_window_not_a_whole_run_mean():
    ep = [T0] + [T0 + 1000 + 60 * i for i in range(8)]   # one huge first interval, then eight 60 s ones
    q = B.quoted_rate(B.arm_intervals(ep))
    assert q["n_used"] == B.RATE_WINDOW and q["s_per_model"] == 60.0
    assert "trailing %d" % B.RATE_WINDOW in q["why"]


# ── the $/ns cell ───────────────────────────────────────────────────────────────────────────────────────
def test_no_row_quotes_a_dollars_per_nanosecond():
    """A co-fold integrates no dynamics. A `$/ns` here would have no denominator — a fabricated figure in the
    one column CLAUDE.md §1 exists to make gradeable."""
    ep = [T0 + 600 * i for i in range(4)]
    rows = B.board_rows(_census(**{a: [1, 2, 3, 4] for a in ARMS}), _arr(**{a: ep for a in ARMS}), now=T0)
    for r in rows:
        assert r["usd_per_ns"] == "— no ns: co-fold is inference, not MD"
        assert "no ns denominator" in r["why"]
        assert not re.search(r"\$\d", r["usd_per_ns"]), "no dollar figure may appear in this lane's $/ns cell"


# ── done / host states ──────────────────────────────────────────────────────────────────────────────────
def test_a_complete_arm_is_DONE_with_no_eta():
    rows = B.board_rows(_census(**{a: list(SP.COFOLD_MODEL_SEEDS) for a in ARMS}), _arr(), now=T0)
    assert all(r["state"] == "DONE" and r["eta_s"] is None and r["pct"] == 100.0 for r in rows)


def test_an_incomplete_arm_with_no_host_says_so():
    rows = B.board_rows(_census(**{ARMS[0]: [1]}), _arr(**{ARMS[0]: [T0]}), now=T0)
    r = [x for x in rows if x["name"].startswith(ARMS[0])][0]
    assert r["state"] == IB.NO_HOST and "No host" in r["why"]


def test_a_live_host_is_named_on_the_row():
    host = {"id": 46524315, "actual_status": "running", "label": SP.LABEL_PREFIX + ARMS[0]}
    rows = B.board_rows(_census(**{ARMS[0]: [1]}), _arr(**{ARMS[0]: [T0]}), hosts=[host], now=T0)
    r = [x for x in rows if x["name"].startswith(ARMS[0])][0]
    assert r["state"] == IB.RUNNING and "46524315" in r["why"]


# ── registration must be TRUTHFUL ───────────────────────────────────────────────────────────────────────
def test_the_lane_is_registered_on_the_all_lane_board():
    """`merge_board` iterates `LANES`, never the fragments on disk, so a fragment for an unregistered lane
    would be written and rendered nowhere — invisible in exactly the way that caused this."""
    ids = [l[0] for l in IB.LANES]
    assert B.LANE in ids, "%s is not in inflight_board.LANES" % B.LANE


def test_the_declared_publisher_exists_and_is_runnable():
    """A publisher name nobody can run is the same defect as a declared artifact nothing writes."""
    writer = dict((l[0], l[2]) for l in IB.LANES)[B.LANE]
    assert os.path.exists(os.path.join(HERE, writer.split()[0]))


def test_the_workflow_offers_the_mode_that_publishes_it():
    wf = os.path.join(os.path.dirname(HERE), "..", ".github", "workflows", "selectivity-control-vast.yml")
    text = open(os.path.normpath(wf)).read()
    assert "selcal_board.py" in text, "nothing in the workflow ever writes the fragment it commits"
    assert "inflight-board.d/selcal-cofold.json" in text


def test_the_fragment_round_trips_through_the_board(tmp_path):
    """End to end: publish, then read it back through the real renderer. A fragment the merger cannot read
    is a lane that renders as ABSENT — which is the failure, not a symptom of it."""
    ep = [T0 + 600 * i for i in range(4)]
    # ⚠ `handles=[]` EXPLICITLY. Since 2026-08-01 `publish` also emits one row per RENTED MD LEG, read
    # from `selcal-handles.json` when the caller does not supply them — so an unpinned call here would pick
    # up whatever the live lane happens to hold and this test would pass or fail on the fleet's state.
    # The MD rows have their own coverage in test_every_lane_remerges_the_board.py; this test is about the
    # CO-FOLD rows round-tripping through the real renderer.
    frag, board = B.publish(_census(**{a: [1, 2, 3, 4] for a in ARMS}),
                            _arr(**{a: ep for a in ARMS}), hosts=[], now=T0, root=str(tmp_path),
                            handles=[])
    doc = IB.read_fragment(B.LANE, str(tmp_path))
    assert doc and len(doc["rows"]) == len(ARMS)

    # …and with a leg rented, the fragment carries it ALONGSIDE the arms rather than replacing them.
    frag2, _b2 = B.publish(_census(**{a: [1, 2, 3, 4] for a in ARMS}),
                           _arr(**{a: ep for a in ARMS}), hosts=[], now=T0, root=str(tmp_path),
                           handles=[{"unit": "selcal-smarca2-m1-r0", "instance": "1", "utc": "x"}])
    doc2 = IB.read_fragment(B.LANE, str(tmp_path))
    assert len(doc2["rows"]) == len(ARMS) + 1
    assert any(r["name"] == "selcal-smarca2-m1-r0" for r in doc2["rows"])
    text = open(board).read()
    assert "SENSITIVITY CONTROL" in text and ARMS[0] in text
    assert os.path.basename(frag) == "%s.json" % B.LANE


def test_a_stale_fragment_renders_STALE_rather_than_vanishing(tmp_path):
    """⚠ DOUBLY IMPORTANT HERE: this lane's census is written by a long-running watch whose commits arrive
    late, so 'the fragment is old' must never render as 'the lane does not exist'."""
    ep = [T0 + 600 * i for i in range(4)]
    B.publish(_census(**{a: [1, 2, 3, 4] for a in ARMS}), _arr(**{a: ep for a in ARMS}),
              hosts=[], now=T0, root=str(tmp_path))
    text = IB.merge_board(now_epoch=T0 + 86400, root=str(tmp_path))
    assert "STALE" in text and "SENSITIVITY CONTROL" in text
    assert "has published nothing" not in text.split("SENSITIVITY CONTROL")[1][:400]


def test_a_never_published_lane_still_renders_a_section(tmp_path):
    text = IB.merge_board(now_epoch=T0, root=str(tmp_path))
    assert "SENSITIVITY CONTROL" in text


def test_an_unattributable_host_does_not_render_as_NO_HOST():
    """⚠ The committed census records instances WITHOUT their labels, so `--from-census` cannot say which
    arm a host serves. "I cannot attribute it" must never render as "there is none" (§4) — that is the same
    absent-reading-as-absence error one column over."""
    rows = B.board_rows(_census(**{ARMS[0]: [1]}), None, hosts=(), now=T0, unattributed_hosts=2)
    r = [x for x in rows if x["name"].startswith(ARMS[0])][0]
    assert "No host" not in r["why"]
    assert "UNATTRIBUTABLE" in r["why"] and "2 host(s)" in r["why"]


def test_unread_arrivals_are_not_reported_as_zero_intervals():
    """`arrivals=None` means the timestamps were never READ. Saying "0 intervals measured" would imply a
    measurement nobody attempted, and the next tick would look like progress when nothing had changed."""
    rows = B.board_rows(_census(**{ARMS[0]: [1, 2, 3, 4]}), None, now=T0)
    r = [x for x in rows if x["name"].startswith(ARMS[0])][0]
    assert r["eta_s"] is None and "NOT READ" in r["why"] and "not a rate of zero" in r["why"]
