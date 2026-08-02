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


# =============================================================================================================
# the ETA — and the hard-coded sentence that was still FALSE after 22 legs landed
# =============================================================================================================
import datetime as _dt  # noqa: E402


def _epoch(s):
    return _dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=_dt.timezone.utc).timestamp()


_NOW = _epoch("2026-08-02T02:30:00Z")
_HOSTS = [{"id": "1", "actual_status": "running", "dph_total": 0.07}]
_MINS = [30.0, 35.0, 38.0, 40.0, 41.0, 42.0, 44.0, 48.0, 52.0, 56.0]


def _row(rented, mins=_MINS, hosts=_HOSTS):
    h = [{"unit": "selcal-smarca4-m2-r0", "instance": "1", "utc": rented}]
    return B.md_rows(h, hosts=hosts, landed=21, n_units=22, now=_NOW, leg_minutes=mins)[0]


def test_the_false_hard_coded_sentence_is_gone():
    """⛔ THE BUG. `md_rows` printed 'this lane has never run an MD leg to its terminus' UNCONDITIONALLY. It
    was true when written (zero legs had landed) and was still being printed after TWENTY-TWO had, because a
    hard-coded sentence is not a measurement. A board whose job is to say what is happening asserted a
    falsehood on every tick."""
    src = open(os.path.join(HERE, "selcal_board.py")).read()
    body = src[src.index("def md_rows("):]
    body = body[:body.index("\ndef ", 10)]
    assert "has never run an MD leg to its terminus" not in body.replace("# ", "") or \
        body.count("has never run an MD leg to its terminus") == 1, \
        "the claim may survive only as the comment recording that it was wrong, never as an emitted string"
    r = _row("2026-08-02T02:10:00Z")
    assert "has never run an MD leg" not in r["why"]


def test_a_normal_leg_gets_an_ETA_from_the_lanes_own_landed_legs():
    # ⚠ THE EXPECTED FIGURES ARE DERIVED FROM THE SAME ONE HOME, never typed: a hand-copied median is how a
    # test starts asserting the fixture the author had in mind rather than the one on the page.
    med = _MINS[len(_MINS) // 2]
    r = _row("2026-08-02T02:10:00Z")           # 20 min in
    assert r["eta_s"] is not None and r["eta_s"] > 0
    assert f"median {med:.0f} min" in r["why"] and "banked a leg" in r["why"]
    assert "PROJECTION off elapsed time, not a frame count" in r["why"], \
        "the cell must not imply it read the leg's actual progress"


def test_the_REAL_INCIDENT_renders_as_an_OVERRUN_with_its_multiple():
    """★★ 275 min against a p90 of 56. This is the row that did not exist on the night it mattered: with no
    ETA and no rate, a host running 8x slower per frame than the fleet looked identical to a healthy one."""
    import lane_staleness_watch as LSW
    p90 = LSW.p90_minutes(_MINS)
    r = _row("2026-08-01T21:55:00Z")           # 275 min
    assert r["eta_s"] is None, "an overrun must not also project a finish time"
    assert "⚠ OVERRUN" in r["why"]
    assert "275 min" in r["why"]
    assert f"{275.0 / p90:.1f}×" in r["why"], "the multiple is the point, not the raw minutes"
    assert f"p90 of {p90:.0f} min" in r["why"]


def test_the_overrun_is_explicitly_NOT_a_condemnation():
    """⛔ THE LESSON FROM DESTROYING ONE. The host that triggered this was at frame 400/500, checkpointing
    normally — it was slow, not dead, and killing it was wrong. The cell must say so, in the place someone
    reads at 3 AM before deciding what to do."""
    r = _row("2026-08-01T21:55:00Z")
    assert "NOT a condemnation" in r["why"] and "nothing reaps on it" in r["why"]
    assert "still buying work" in r["why"]
    assert "diag" in r["why"], "it must name the action that turns the flag into a diagnosis"


def test_with_no_landed_legs_it_refuses_rather_than_inventing_a_duration():
    r = _row("2026-08-02T02:10:00Z", mins=[])
    assert r["eta_s"] is None
    assert "no rental has yet banked a leg" in r["why"]
    assert "$/ns" in r["why"], "the refusal must say WHY this lane has no better signal"


def test_an_unreadable_rental_stamp_is_not_a_fabricated_zero():
    r = _row("not-a-timestamp")
    assert r["eta_s"] is None and "ETA UNKNOWN" in r["why"]


def test_a_dead_host_gets_no_ETA():
    r = _row("2026-08-02T02:10:00Z", hosts=[])
    assert r["eta_s"] is None


def test_the_p90_and_the_selection_have_ONE_home_shared_with_the_watcher():
    """⛔ The same two numbers are quoted in this board cell AND in `lane_staleness_watch`'s overrun warning.
    Two copies would drift by an off-by-one nobody reads, and the board would then promise an ETA the watcher
    was simultaneously calling an overrun. The first draft of `banked_leg_minutes` re-derived the p90 inline
    while its docstring claimed to import it."""
    import lane_staleness_watch as LSW
    src = open(os.path.join(HERE, "selcal_board.py")).read()
    body = src[src.index("def md_rows("):]
    body = body[:body.index("\ndef ", 10)]
    assert "LSW.p90_minutes(" in body, "the board must import the p90, not compute one"
    assert "int(round(0.9" not in body, "…and must not carry its own copy of the arithmetic"
    rentals = [{"uptime_s": m * 60.0, "why": "work banked, no remaining role"} for m in _MINS]
    assert B.banked_leg_minutes(rentals) == LSW.banked_leg_minutes(rentals)
    budget, _ = LSW.overrun_budget_min(rentals)
    assert budget == LSW.p90_minutes(B.banked_leg_minutes(rentals)), \
        "the watcher's warning line and the board's overrun line must be the SAME number"
