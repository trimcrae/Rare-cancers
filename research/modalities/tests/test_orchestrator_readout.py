"""The board must come out of the tool in the form it is REPORTED in — not in a form a hand then reformats.

★★ WHY (trimcrae, 2026-08-01: *"That board formatting is bad."*, after *"The top row has an ETA in the
past. Come on man."*). `orchestrator_readout` already existed to stop rows being carried forward from a
previous message — but it returned STRUCTURE, and the last step, turning that structure into the markdown
table trimcrae actually reads, was still done by hand. That step is where the errors kept landing:

  * a leg reported RUNNING at 98.9% had already LANDED — its row was simply gone from the artifact;
  * a subagent's PROSE guess sat in the ETA column for six consecutive reports, for a lane that emits no
    board row at all;
  * a `.chk` prune smoke was carried as "status unknown" for hours while one API call answered it.

None of those was a fleet problem. All three were transcription. So the last hand is removed: `board_table`
returns finished markdown, and these tests pin the properties that make it safe to paste without reading it
first — because "paste without reading" is exactly what will happen at 3 AM.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

MOD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MOD))

import inflight_board as ifb          # noqa: E402
import orchestrator_readout as orc    # noqa: E402

NOW = 1_785_600_000.0


def _frag(lane, rows, age_min=0.0, note=None):
    return json.dumps(ifb.build_fragment(lane, rows, now_epoch=NOW - age_min * 60.0, note=note))


def _install(monkeypatch, by_lane, ternary_md=None):
    """Serve fragments from a dict instead of `git show origin/main:…`, so a board can be constructed."""
    def fake(rel):
        for lane, blob in by_lane.items():
            if rel.endswith(f"{lane}.json"):
                return json.loads(blob)
        if ternary_md is not None and rel.endswith(ifb.TERNARY_BOARD_MD):
            return ternary_md
        return None
    monkeypatch.setattr(orc, "_read", fake)


ROW_PAYING = {"name": "5aks_d0_to_d ternary nr4a1 r1", "pct": 80.0, "eta_s": 3600.0,
              "usd_per_ns": "RTX 3090 $0.00412/ns · 1.21× basis [bid]", "state": "RUNNING",
              "why": "56.3 s/iter"}
ROW_REFUSED = {"name": "cw_ms r1", "pct": None, "eta_s": None,
               "usd_per_ns": "⛔ REFUSED at $0.007282/ns · 2.13× basis — $0 spent",
               "state": "HELD — NOT BUYING",
               "why": "board_depth 23 -> 5 qualifying -> 5 priceable -> 1 used_for_mean. " + "x" * 400}


def test_every_registered_lane_reaches_the_table(monkeypatch):
    """A lane that VANISHES from a report is indistinguishable from a lane with nothing running — the exact
    conflation `merge_board` iterates `LANES` to prevent. The table must inherit that, not undo it."""
    _install(monkeypatch, {ifb.TERNARY: _frag(ifb.TERNARY, [ROW_PAYING])})
    out = orc.board_table(now_epoch=NOW)
    for lane, _h, _w in ifb.LANES:
        assert f"| {lane} |" in out, f"lane {lane!r} is registered but never reaches the table"


def test_a_lane_with_no_readable_fragment_says_so_rather_than_rendering_empty(monkeypatch):
    """An ABSENT reading is not a reading of absence (CLAUDE.md §4). The lane with no fragment must carry
    UNKNOWN and name what could not be read — never a blank row that reads as 'idle'."""
    _install(monkeypatch, {})
    out = orc.board_table(now_epoch=NOW)
    for lane, _h, _w in ifb.LANES:
        line = next(l for l in out.splitlines() if l.startswith(f"| {lane} |"))
        assert ifb.UNKNOWN in line and "no readable fragment" in line


def test_an_idle_lane_and_an_absent_lane_do_not_render_alike(monkeypatch):
    """The pair of facts this whole board exists to keep apart: 'nothing is running' vs 'we cannot see
    whether anything is running'."""
    _install(monkeypatch, {ifb.FANOUT: _frag(ifb.FANOUT, [])})
    out = orc.board_table(now_epoch=NOW)
    idle = next(l for l in out.splitlines() if l.startswith(f"| {ifb.FANOUT} |"))
    absent = next(l for l in out.splitlines() if l.startswith(f"| {ifb.NRV04_RETRO} |"))
    assert "no GPU legs" in idle and "idle, not absent" in idle
    assert ifb.UNKNOWN in absent and "no readable fragment" in absent
    assert idle != absent


def test_the_usd_per_ns_cell_is_never_clipped(monkeypatch):
    """⚠ CLAUDE.md §1: a row we are PAYING and a row the gate REFUSED must never render alike, and that
    distinction lives entirely inside this cell (`⚠ PAYING OVER THE …× LINE` vs `⛔ REFUSED … — $0 spent`).
    Truncating it could turn a refusal into what looks like a purchase — which is the precise complaint
    that made the distinction a rule in the first place."""
    _install(monkeypatch, {ifb.FANOUT: _frag(ifb.FANOUT, [ROW_REFUSED])})
    out = orc.board_table(now_epoch=NOW)
    assert ROW_REFUSED["usd_per_ns"] in out
    assert "$0 spent" in out, "the refusal's own words must survive into the cell"


def test_a_clipped_why_says_it_was_clipped(monkeypatch):
    """A partial reason must never be able to read as a complete one."""
    _install(monkeypatch, {ifb.FANOUT: _frag(ifb.FANOUT, [ROW_REFUSED])})
    out = orc.board_table(now_epoch=NOW)
    row = next(l for l in out.splitlines() if l.startswith(f"| {ifb.FANOUT} |"))
    why = row.rstrip("| ").rsplit("|", 1)[-1].strip()
    assert why.endswith("…") and len(why) <= orc.WHY_CLIP + 2
    assert "board_depth" in why, "the operative clause is written first and must survive the clip"
    assert "inflight-board-all.md" in out, "and the full text must be pointed at"


def test_a_pipe_in_a_cell_cannot_break_the_table(monkeypatch):
    """One stray `|` in a lane's prose would silently shift every column to its right — a corrupted row that
    still looks like a row."""
    _install(monkeypatch, {ifb.FANOUT: _frag(ifb.FANOUT, [dict(ROW_PAYING, why="a|b|c", name="x|y")])})
    out = orc.board_table(now_epoch=NOW)
    body = [l for l in out.splitlines() if l.startswith("|") and not set(l) <= set("|-: ")]
    assert body and all(l.count("|") - l.count("\\|") == 8 for l in body), \
        "every row must have exactly the header's cell count once escapes are discounted"


def test_a_stale_lane_loses_its_eta_and_says_the_row_is_a_past_report(monkeypatch):
    """The staleness RULE has one home — `inflight_board.stale_rows` — and the table must apply it rather
    than restate it. A stale ETA re-projected forward is a promise nobody measured."""
    _install(monkeypatch, {ifb.FANOUT: _frag(ifb.FANOUT, [ROW_PAYING], age_min=99.0)})
    out = orc.board_table(now_epoch=NOW)
    row = next(l for l in out.splitlines() if l.startswith(f"| {ifb.FANOUT} |"))
    assert "| — |" in row, "a stale row must not carry an ETA"
    assert ifb.UNKNOWN in row and "80.0%" in row, "the % survives — a committed checkpoint does not un-happen"
    assert "not a current reading" in row
    assert "has not reported inside" in out, "and the footer must count the stale rows"


def test_a_fresh_lane_keeps_its_eta_in_et_twelve_hour(monkeypatch):
    """CLAUDE.md §1: ET, 12-hour, always. A board that emitted UTC or 24-hour would be wrong in the one
    column a reader acts on."""
    _install(monkeypatch, {ifb.FANOUT: _frag(ifb.FANOUT, [ROW_PAYING])})
    out = orc.board_table(now_epoch=NOW)
    row = next(l for l in out.splitlines() if l.startswith(f"| {ifb.FANOUT} |"))
    eta = row.split("|")[3].strip()
    assert eta == ifb._fmt_eta_at(NOW + 3600.0, now_epoch=NOW), eta
    assert ("AM" in eta or "PM" in eta) and "Z" not in eta


# ── the pre-fragment bridge ────────────────────────────────────────────────────────────────────────────────

def test_the_rendered_block_round_trips_through_the_parser():
    """`_parse_rendered_block` must recover exactly what `render` put in, for a lane that has not yet
    published a structured fragment. The LEG and `$/ns` columns are sized FROM THE ROWS, so the offsets are
    read off the header — a typed constant would be wrong the first time a unit id grew, and the truncation
    that hid `nr4a1` vs `nr4a3` from four 5a-KS rows already cost an hour of misaimed diagnosis."""
    rows = [ROW_PAYING, dict(ROW_REFUSED, why="short reason")]
    block = ifb.render([dict(r) for r in rows], now_epoch=NOW)
    got = orc._parse_rendered_block(block)
    assert got is not None and len(got) == 2
    for src, out in zip(rows, got):
        assert out["name"] == src["name"]
        assert out["usd_per_ns"] == src["usd_per_ns"]
        assert out["state"] == src["state"]
        assert out["why"] == src["why"]


def test_a_block_the_parser_cannot_read_returns_none_rather_than_empty():
    """Empty means 'this lane has no legs'. Unreadable means 'we cannot see this lane's legs'. They are
    opposite findings and the parser must not be the place they finally merge."""
    assert orc._parse_rendered_block("some text with no header at all") is None
    assert orc._parse_rendered_block("") is None
    assert orc._parse_rendered_block(ifb.render([], now_epoch=NOW)) is None


def test_the_ternary_bridge_is_used_only_when_the_fragment_is_missing(monkeypatch):
    """The fragment is authoritative the moment it exists; the text parse is a bridge, not a fallback that
    quietly stays in service."""
    md = ("# In-flight board\n\nGenerated 2:40 PM ET Sat Aug 1, 2026 by `task=collect`.\n\n```\n"
          "---- TVAST-BOARD ----\n" + ifb.render([ROW_PAYING], now_epoch=NOW) +
          "---- END TVAST-BOARD ----\n```\n")
    _install(monkeypatch, {}, ternary_md=md)
    out = orc.board_table(now_epoch=NOW)
    assert ROW_PAYING["name"] in out and "RUNNING" in out

    _install(monkeypatch, {ifb.TERNARY: _frag(ifb.TERNARY, [dict(ROW_PAYING, name="FROM-FRAGMENT")])},
             ternary_md=md)
    out = orc.board_table(now_epoch=NOW)
    assert "FROM-FRAGMENT" in out and ROW_PAYING["name"] not in out


def test_the_table_is_generated_from_the_fragments_not_the_merged_cache(monkeypatch):
    """⚠ THE MERGED BOARD IS A CACHE AND MAY LAG. Measured 2026-08-01, 2:44 PM ET: the GCP fragment was 1.8
    min old with an ETA of 4:36 AM Aug 2 while `inflight-board-all.md` rendered that lane at '16 min ago,
    STALE (> 15 min)' with a blank ETA, because the merge only runs when some lane ticks. That was fixed at
    the source — but a report must not be able to inherit that lag at all, so a table built while the cache
    is absent entirely must still be complete."""
    calls = []
    real = orc._read

    def spy(rel):
        calls.append(rel)
        return None if rel.endswith("inflight-board-all.md") else real(rel)
    monkeypatch.setattr(orc, "_read", spy)
    _install(monkeypatch, {ifb.FANOUT: _frag(ifb.FANOUT, [ROW_PAYING])})
    out = orc.board_table(now_epoch=NOW)
    assert ROW_PAYING["name"] in out
    assert not any("inflight-board-all.md" in c for c in calls), \
        "board_table must not read the merged cache — it is regenerated by whichever lane last ticked"


def test_the_generated_stamp_is_et_twelve_hour(monkeypatch):
    _install(monkeypatch, {})
    out = orc.board_table(now_epoch=NOW)
    assert ifb.et_stamp(NOW) in out.splitlines()[0]
    assert "ET" in out.splitlines()[0]


def test_it_runs_against_the_live_repo_without_a_stack():
    """$0 smoke: the real thing, on whatever `origin/main` currently holds. It must never raise — a readout
    that crashes when a lane is mid-publish is a readout nobody can rely on at 3 AM."""
    out = orc.board_table(now_epoch=time.time())
    assert out.startswith("**In flight**") and out.count("\n|") >= len(ifb.LANES)


def test_a_stale_row_is_graded_against_the_account_not_the_lanes_own_last_word(monkeypatch):
    """⚠ STALE SHOUTS BECAUSE A LANE MIGHT BE BILLING UNSUPERVISED — so a reader needs to know whether
    anything IS billing, and the stale lane's own last report is precisely the reading just declared
    untrustworthy. Measured 2026-08-01: the selcal panel completed 12/12, reaped its host, and then drifted
    stale forever, printing the billing alarm on a lane that could not bill. The ACCOUNT census is the one
    source that sees every instance regardless of which lane claims it."""
    _install(monkeypatch, {ifb.FANOUT: _frag(ifb.FANOUT, [ROW_PAYING], age_min=99.0)})
    monkeypatch.setattr(orc, "billing_now", lambda: {
        "n": 1, "age_min": 3.0, "stale": False,
        "instances": [{"id": 1, "label": "tvast-5aks-r1", "gpu": "RTX 3090", "status": "running"}]})
    out = orc.board_table(now_epoch=NOW)
    assert "1 live instance(s)" in out and "tvast-5aks-r1" in out

    # …and an UNREADABLE census must never render as "nothing is billing" (CLAUDE.md §4).
    monkeypatch.setattr(orc, "billing_now", lambda: {"unreadable": "census absent"})
    out = orc.board_table(now_epoch=NOW)
    assert "UNKNOWN" in out and "absent reading is not a reading of absence" in out
    assert "0 live" not in out


def test_a_fresh_board_does_not_pay_for_the_account_cross_check(monkeypatch):
    """The cross-check exists to grade a stale row. With nothing stale there is nothing to grade, and a
    board that reads the census anyway would put an irrelevant line under every healthy report."""
    # EVERY lane fresh — a lane with no fragment is itself a stale row, which is the correct behaviour
    # and was this test's own first bug: it asserted "nothing stale" while three lanes had no fragment.
    _install(monkeypatch, {l[0]: _frag(l[0], [ROW_PAYING]) for l in ifb.LANES})
    called = []
    monkeypatch.setattr(orc, "billing_now", lambda: called.append(1) or {"n": 0, "instances": []})
    out = orc.board_table(now_epoch=NOW)
    assert not called, "billing_now must not be consulted when no row is stale"
    assert "live instance" not in out
