#!/usr/bin/env python3
"""EVERY BILLING LANE GETS A ROW — and a lane that stops reporting must go STALE, never vanish.

WHAT THIS PINS, and why each assertion exists rather than being obvious:

  * Until 2026-07-31 `inflight_board` had exactly ONE importer (`ternary_vast_launch`). The NR-V04
    retrospective panel and the step 1 congeneric fan-out both rent GPUs from their own launchers and had NO
    row anywhere. "One row per GPU leg" was therefore false, and a board that omits a whole billing lane is
    worse than no board — it reads as complete. These tests fail if either lane's wiring is removed.
  * A lane with no fragment renders a row SAYING so. An absent lane and an idle lane are opposite facts
    ("nothing is running" vs "we cannot see whether anything is running") and this repo's board has a history
    of rendering those two identically.
  * The `⚠ PAYING` / `⛔ REFUSED` glyphs must never collide (CLAUDE.md §1, 2026-07-27): one means money is
    going out at a rate the gate would refuse today, the other means the gate declined and `$0` was spent.
  * A missing MEASURED rate yields `—`. Never a planning-rate guess: an ETA nobody can trace is the column
    that got called useless.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import inflight_board as B    # noqa: E402


# ── a fake object store: enough for the two lanes' board reads, and nothing more ──────────────────────────
class _Body:
    def __init__(self, data):
        self._d = data

    def read(self):
        return self._d


class FakeS3:
    """`get_object` with the `Range` the lanes use. A key that is absent RAISES, exactly as boto3 does — the
    lanes' helpers must turn that into None, not into an empty string that parses as 'no progress'."""

    def __init__(self, objects):
        self.objects = dict(objects)

    def get_object(self, Bucket=None, Key=None, Range=None):  # noqa: N803 — boto3's own spelling
        if Key not in self.objects:
            raise KeyError(Key)
        data = self.objects[Key]
        if isinstance(data, str):
            data = data.encode()
        return {"Body": _Body(data)}

    def head_object(self, Bucket=None, Key=None):  # noqa: N803
        if Key not in self.objects:
            raise KeyError(Key)
        return {}


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# STEP 1 FAN-OUT — a real unit renders a real row
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════

# Verbatim shapes: `rbfe_spot_driver` prints the targets line at startup, and `congeneric_fanout_vast._LEG`
# uploads that leg's log to `<results>/<unit>/<leg>.log` when the leg ends.
_LEG_LOG = ("[spot-driver] trajectory persistence: positions every 20 iteration(s)\n"
            "[spot-driver] warmup_target=400 (ci=20) prod_target=2000 (ci=40)\n"
            "[spot-driver] restore -> none (fresh)\n")

_UNIT = {"unit_id": "e_zaienne_cmpd19__cw_ev_5cooh__neutral__neutral_acid",
         "ligand_b": "cw_ev_5cooh", "receptor": "nr4a3", "edge_id": "e1", "leg_id": "l1",
         "frame": "f1"}


def _fanout(objects=None, live=(), obs=None, prev=None, unreadable=None, hold_doc=None):
    import congeneric_fanout_vast as F
    s3 = FakeS3(objects or {})
    return F.board_rows(s3, "bkt", [_UNIT], {}, set(), obs or {}, list(live), unreadable,
                        prev or {}, hold_doc=hold_doc if hold_doc is not None else {})


def _live_host(gpu="RTX 4090", dph=0.25, age_min=120.0):
    """A host well past `vast_idle_guard.MIN_INSTANCE_AGE_MIN`, so the cold-start floor is not what these
    tests are measuring. `start_date: 0` would read as age 0 — `_age_min` treats an unusable start_date as
    brand new, which is the safe direction for the guard and would silently mute every stall assertion."""
    import time
    import congeneric_fanout_vast as F
    return {"id": 1, "label": F.unit_label(_UNIT, 0), "gpu_name": gpu, "dph_total": dph,
            "start_date": time.time() - age_min * 60.0, "actual_status": "running", "gpu_util": 92.0}


def test_a_fanout_unit_renders_a_row_with_a_percent_from_its_own_driver_log():
    """The denominator is PARSED from the driver's line, never recomputed and never typed here."""
    import congeneric_fanout_vast as F
    key = f"{F.RESULT_PREFIX}/{_UNIT['unit_id']}/complex.log"
    rows, _ = _fanout(objects={key: _LEG_LOG}, live=[_live_host()],
                      obs={_UNIT["unit_id"]: {"phase": "leg-complex-running",
                                              "detail": "complex/production@1200"}})
    assert len(rows) == 1
    r = rows[0]
    # whole UNIT: complex(400+2000) + solvent(400+2000) = 4800; done = 400 + 1200
    assert r["pct"] == pytest.approx(100.0 * 1600 / 4800)
    assert "cw_ev_5cooh" in r["name"]
    assert B.render(rows).count("\n") >= 3


def test_the_fanout_percent_is_none_when_no_leg_log_has_landed_yet():
    """A unit on its FIRST leg has no durable target anywhere — `—` and the reason, never a borrowed one."""
    rows, _ = _fanout(live=[_live_host()],
                      obs={_UNIT["unit_id"]: {"phase": "leg-complex-running",
                                              "detail": "complex/warmup@120"}})
    assert rows[0]["pct"] is None
    assert "warmup_target" in rows[0]["why"] and "unknowable" in rows[0]["why"]
    assert "—" in B.render(rows)


def test_the_fanout_eta_is_a_dash_until_a_rate_has_been_MEASURED():
    """One poll cannot produce a rate. A planning-rate substitute is the thing trimcrae called useless."""
    import congeneric_fanout_vast as F
    key = f"{F.RESULT_PREFIX}/{_UNIT['unit_id']}/complex.log"
    rows, _ = _fanout(objects={key: _LEG_LOG}, live=[_live_host()],
                      obs={_UNIT["unit_id"]: {"phase": "leg-complex-running",
                                              "detail": "complex/production@1200"}})
    assert rows[0]["eta_s"] is None
    assert "no measured iteration rate" in rows[0]["why"]


def test_the_fanout_eta_appears_once_two_polls_have_measured_one():
    import congeneric_fanout_vast as F
    key = f"{F.RESULT_PREFIX}/{_UNIT['unit_id']}/complex.log"
    prev = {_UNIT["unit_id"]: {"stage": "complex/production", "iteration": 1000,
                               "utc": "2026-07-31T10:00:00Z", "no_advance_polls": 0}}
    rows, _ = _fanout(objects={key: _LEG_LOG}, live=[_live_host()], prev=prev,
                      obs={_UNIT["unit_id"]: {"phase": "leg-complex-running",
                                              "detail": "complex/production@1200"}})
    assert rows[0]["eta_s"] is not None and rows[0]["eta_s"] > 0
    assert rows[0]["state"] == B.RUNNING


def test_a_fanout_unit_with_no_host_still_renders_with_its_checkpoint():
    rows, _ = _fanout(obs={_UNIT["unit_id"]: {"phase": "leg-complex-running",
                                              "detail": "complex/production@1200"}})
    assert rows[0]["state"] == B.NO_HOST
    assert "complex/production@1200" in rows[0]["why"]
    assert rows[0]["eta_s"] is None, "an ETA off a host we do not have is a promise nothing can keep"


def test_an_unreadable_instance_list_is_unknown_not_a_host_death():
    rows, _ = _fanout(unreadable="RuntimeError: vast API GET /instances/ -> 403",
                      obs={_UNIT["unit_id"]: {"detail": "complex/production@1200"}})
    assert rows[0]["state"] == B.UNKNOWN and "403" in rows[0]["why"]


def test_an_unreadable_commit_store_is_never_counted_as_a_non_advance():
    """`committed_progress` returns a negative scalar for an unlistable store; treating it as zero
    manufactures a stall out of a network blip."""
    prev = {_UNIT["unit_id"]: {"stage": "complex/production", "iteration": 1200,
                               "utc": "2026-07-31T10:00:00Z", "no_advance_polls": 1}}
    _, state = _fanout(live=[_live_host()], prev=prev,
                       obs={_UNIT["unit_id"]: {"detail": None, "unreadable": True}})
    assert state[_UNIT["unit_id"]]["no_advance_polls"] == 1, "an unreadable poll must not tick the counter"


def test_a_busy_gpu_between_two_checkpoints_is_not_a_stall():
    """This lane commits every 20/40 iterations (~5-10 min) and a supervising agent may poll every 3, so
    'no advance this poll' is the ORDINARY state of a healthy leg. The guard's GPU-busy rule saves it."""
    import congeneric_fanout_vast as F
    key = f"{F.RESULT_PREFIX}/{_UNIT['unit_id']}/complex.log"
    obs = {_UNIT["unit_id"]: {"phase": "leg-complex-running", "detail": "complex/production@1200"}}
    prev, state = {}, None
    for _ in range(4):                      # four polls at the same committed iteration, GPU at 92 %
        rows, state = _fanout(objects={key: _LEG_LOG}, live=[_live_host()], obs=obs, prev=prev)
        prev = state
    assert rows[0]["state"] != B.STALLED, "a box the guard's own rule calls busy must not be called stalled"


def test_an_idle_gpu_that_never_advances_IS_a_stall_with_a_real_reason():
    """The other direction: the GPU rule only ever SAVES a row, so it cannot mute a genuine stall."""
    import congeneric_fanout_vast as F
    key = f"{F.RESULT_PREFIX}/{_UNIT['unit_id']}/complex.log"
    host = _live_host()
    host["gpu_util"] = 0.0
    obs = {_UNIT["unit_id"]: {"phase": "leg-complex-running", "detail": "complex/production@1200"}}
    prev, state = {}, None
    for _ in range(3):
        rows, state = _fanout(objects={key: _LEG_LOG}, live=[host], obs=obs, prev=prev)
        prev = state
    assert rows[0]["state"] == B.STALLED
    assert "consecutive board polls" in rows[0]["why"] and "GPU 0.0%" in rows[0]["why"]


def test_a_first_census_is_not_evidence_of_advance():
    assert B.advanced_since_last_poll(None, {"stage": "md", "iteration": 5}) is False
    assert B.advanced_since_last_poll({}, {"stage": "md", "iteration": 5}) is False
    assert B.advanced_since_last_poll({"stage": "md", "iteration": 5},
                                      {"stage": "md", "iteration": 6}) is True
    assert B.advanced_since_last_poll({"stage": "md", "iteration": 5},
                                      {"stage": "md", "iteration": 5}) is False
    # an unreadable reading claims nothing in either direction
    assert B.advanced_since_last_poll({"stage": "md", "iteration": 5},
                                      {"stage": "md", "iteration": None}) is False


def test_the_gpu_busy_line_is_imported_and_only_ever_saves_a_row():
    import vast_idle_guard as vig
    assert B.gpu_is_busy(vig.GPU_BUSY_PCT) is True
    assert B.gpu_is_busy(vig.GPU_BUSY_PCT - 0.1) is False
    assert B.gpu_is_busy(None) is False, "'the host is not telling us' is not 'the GPU is idle'"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# NR-V04 RETROSPECTIVE — 18 endpoint-MD legs
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════

def _retro_unit_names():
    import nrv04_retro_panel as retro
    return [retro.unit_name(a, m, r) for a, m, r in retro.enumerate_units()]


def _retro(objects=None, live=(), phases=None, have=(), prev=None, unreadable=None):
    import nrv04_vast_launch as N
    s3 = FakeS3(objects or {})
    return N.retro_board_rows(s3, "bkt", phases or {}, set(have), list(live), unreadable, prev or {})


def test_the_retrospective_panel_renders_one_row_per_pending_leg():
    """One row per pending authorized R1 leg; a board that shows none of them is the omission this whole
    file exists for.

    ⚠ THE COUNT IS DERIVED, NOT TYPED. This assertion used to read `== 18` and it fired correctly when
    prereg AMENDMENT 4 (2026-07-31) took the panel to 16 by excluding nr4a3 co-fold seed 3 on a measured
    input fault. The guard's intent is "the board's denominator FOLLOWS the panel", so it now says exactly
    that — a hard-coded count re-tests the constant instead of the invariant."""
    import nrv04_retro_panel as _panel
    names = _retro_unit_names()
    assert len(names) == len(_panel.enumerate_units()) == 16, (
        "the board's denominator must follow the authorized panel")
    rows, _ = _retro()
    assert len(rows) == len(names)
    assert all(r["name"] for r in rows)


def test_a_retro_leg_gets_its_percent_from_the_drivers_own_frame_census():
    # ⚠ THE TOTAL IS THE PANEL'S OWN PRODUCTION FRAME COUNT, not an arbitrary round number. Since
    # 2026-07-31 a census whose denominator is NOT that count renders its label instead of a percentage
    # (`retro_board_rows`, `pct_of`), so a fixture that invents a total no longer exercises this path — and
    # pinning to the derived count is the stronger test anyway.
    import nrv04_retro_panel as retro
    import nrv04_vast_launch as N
    name = _retro_unit_names()[0]
    total = retro.expected_production_frames()
    objects = {f"{N.RETRO_RESULT_PREFIX}/{name}/run.log":
               "[nrv04-md] checkpoint @ frame %d/%d -> S3\n" % (total // 4, total)}
    rows, _ = _retro(objects=objects, phases={name: "md-running"})
    row = [r for r in rows if r["name"] == N._retro_short_name(name)][0]
    assert row["pct"] == pytest.approx(25.0)
    assert row.get("pct_of") is None, "a production census must render as a percentage"


def test_a_retro_leg_whose_census_is_a_smoke_run_renders_smoke_not_100_percent():
    """THE REGRESSION: 16 rows of the committed 1:38 PM ET board read `100.0%` off a 5-frame smoke log."""
    import nrv04_vast_launch as N
    name = _retro_unit_names()[0]
    objects = {f"{N.RETRO_RESULT_PREFIX}/{name}/run.log":
               "[nrv04-md] checkpoint @ frame 5/5 -> S3\n"}
    rows, _ = _retro(objects=objects, phases={name: "uploaded"})
    row = [r for r in rows if r["name"] == N._retro_short_name(name)][0]
    assert row["pct"] is None and row["pct_of"] == "smoke"
    assert row["eta_s"] is None, "a smoke census must not project a production completion time"
    assert "100.0%" not in B.render(rows)


def test_a_retro_leg_with_no_checkpoint_yet_is_a_dash_not_a_zero_percent_promise():
    name = _retro_unit_names()[0]
    live = [{"id": 7, "label": name, "gpu_name": "RTX 3090", "dph_total": 0.12,
             "start_date": 0, "actual_status": "running"}]
    rows, _ = _retro(live=live, phases={name: "staged"})
    assert rows[0]["pct"] is None
    assert "checkpoint @ frame" in rows[0]["why"]


def test_a_retro_leg_with_no_host_says_so_rather_than_wearing_a_cell_excuse():
    """A non-RUNNING verdict must be justified by the thing that made it non-RUNNING, never by a `—` cell."""
    rows, _ = _retro()
    assert rows[0]["state"] == B.NO_HOST
    assert "no live host" in rows[0]["why"] and rows[0]["eta_s"] is None


def test_a_landed_retro_leg_is_counted_not_rowed():
    names = _retro_unit_names()
    rows, _ = _retro(have=names[:3])
    assert len(rows) == len(names) - 3, "landed legs are counted in the note, not rowed"


def test_a_retro_row_refuses_to_invent_a_dollars_per_ns():
    """These legs are endpoint MD; the ONLY throughput table benches 84k-atom RBFE. `—` beats a substitution."""
    import nrv04_vast_launch as N
    name = _retro_unit_names()[0]
    live = [{"id": 7, "label": name, "gpu_name": "RTX 3090", "dph_total": 0.1234,
             "start_date": 0, "actual_status": "running"}]
    rows, _ = _retro(live=live, phases={name: "md-running"})
    cell = [r for r in rows if r["name"] == N._retro_short_name(name)][0]["usd_per_ns"]
    assert cell.startswith("—"), "an unpriceable row must never lead with a figure"
    assert "$0.1234/hr" in cell, "the rate we ARE paying is measured and must still be reported"
    assert "no measured ns/h" in cell and "basis" not in cell, "no fabricated multiple of the ladder basis"


def test_a_retro_leg_that_never_advances_becomes_stalled_only_after_two_polls_and_with_a_reason():
    import nrv04_vast_launch as N
    name = _retro_unit_names()[0]
    objects = {f"{N.RETRO_RESULT_PREFIX}/{name}/run.log":
               "[nrv04-md] checkpoint @ frame 250/1000 -> S3\n"}
    live = [{"id": 7, "label": name, "gpu_name": "RTX 3090", "dph_total": 0.12,
             "start_date": 0, "actual_status": "running"}]
    prev, state = {}, None
    for _ in range(3):                       # three polls at the SAME frame count
        rows, state = _retro(objects=objects, live=live, phases={name: "md-running"}, prev=prev)
        prev = state
    row = [r for r in rows if r["name"] == N._retro_short_name(name)][0]
    assert row["state"] == B.STALLED
    assert "consecutive board polls" in row["why"] and "md-running" in row["why"]


def test_one_flat_retro_poll_is_not_yet_a_stall():
    import nrv04_vast_launch as N
    name = _retro_unit_names()[0]
    objects = {f"{N.RETRO_RESULT_PREFIX}/{name}/run.log":
               "[nrv04-md] checkpoint @ frame 250/1000 -> S3\n"}
    live = [{"id": 7, "label": name, "gpu_name": "RTX 3090", "dph_total": 0.12,
             "start_date": 0, "actual_status": "running"}]
    rows, state = _retro(objects=objects, live=live, phases={name: "md-running"})
    rows, _ = _retro(objects=objects, live=live, phases={name: "md-running"}, prev=state)
    row = [r for r in rows if r["name"] == N._retro_short_name(name)][0]
    assert row["state"] != B.STALLED


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# PAYING vs REFUSED — one glyph, one meaning
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════

def test_paying_over_the_line_and_a_gate_refusal_never_render_alike():
    """trimcrae, 2026-07-27: held lanes and billed legs printed the same ⚠ and a working gate looked broken."""
    import inflight_usd_per_ns as ifn
    plan = B.planning_usd_per_ref_gpu_h()
    assert plan, "the ladder repricing artifact is the one home for the planning rate"
    dear = ifn.APPROVED_USD_PER_NS * 1.5 * ifn.vcm.ns_per_hour("RTX 4090")
    paying = B.usd_per_ns_cell("RTX 4090", dear)
    refused = B.usd_per_ns_cell("RTX 4090", dear, stance=ifn.REFUSED)
    assert "⚠ PAYING OVER THE" in paying and "⛔" not in paying
    assert "⛔ REFUSED" in refused and "$0 spent" in refused and "⚠" not in refused
    assert paying != refused


def test_a_fanout_unit_held_on_price_renders_REFUSED_not_a_bill():
    """No host + a recorded price hold is the gate WORKING: the multiple on the row is what we DECLINED."""
    import inflight_usd_per_ns as ifn
    dear = ifn.APPROVED_USD_PER_NS * 2.0
    hold = {"held": True, "decision": "price_hold",
            "offers_priced": [{"gpu": "RTX 4090", "usd_per_ns": dear, "machine_id": 1}]}
    rows, _ = _fanout(obs={_UNIT["unit_id"]: {"detail": "complex/production@1200"}}, hold_doc=hold)
    cell = rows[0]["usd_per_ns"]
    assert "⛔ REFUSED" in cell and "$0 spent" in cell
    assert rows[0]["state"] == B.NO_HOST


def test_a_fanout_unit_with_a_live_host_renders_PAYING_not_a_refusal():
    import congeneric_fanout_vast as F
    import inflight_usd_per_ns as ifn
    key = f"{F.RESULT_PREFIX}/{_UNIT['unit_id']}/complex.log"
    dear = ifn.APPROVED_USD_PER_NS * 1.5 * ifn.vcm.ns_per_hour("RTX 4090")
    rows, _ = _fanout(objects={key: _LEG_LOG}, live=[_live_host(dph=dear)],
                      obs={_UNIT["unit_id"]: {"detail": "complex/production@1200"}})
    assert "⚠ PAYING OVER THE" in rows[0]["usd_per_ns"]
    assert "REFUSED" not in rows[0]["usd_per_ns"]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# THE MERGED BOARD — a lane that reports nothing goes UNKNOWN, and never disappears
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════

_TERNARY_MD = """<!-- GENERATED by gpu-ternary-fep-vast.yml task=collect. -->
# In-flight board

Generated 7:04 AM ET Fri Jul 31, 2026 by `task=collect`.

```
---- TVAST-BOARD ----
LEG                 % DONE  ETA (ET)         $/ns                       STATE     WHY (when not running)
T3 ternary            16.2%  9:31 PM          $0.00456/ns · 1.34x basis  RUNNING
---- END TVAST-BOARD ----
```
"""


def _ternary_epoch():
    import calendar
    import time as t
    return calendar.timegm(t.strptime("7:04 AM Jul 31, 2026", "%I:%M %p %b %d, %Y")) + 4 * 3600


def test_every_registered_lane_gets_a_section_even_with_no_fragment(tmp_path):
    """Iterating the REGISTRY, not the fragments on disk, is what stops a whole billing lane going missing."""
    txt = B.merge_board(now_epoch=_ternary_epoch(), root=str(tmp_path))
    for lane, heading, _writer in B.LANES:
        assert heading in txt, f"lane {lane} has no section"
    assert txt.count("UNKNOWN") >= 2


def test_a_lane_with_no_fragment_renders_a_row_saying_so_rather_than_an_empty_section(tmp_path):
    txt = B.merge_board(now_epoch=_ternary_epoch(), root=str(tmp_path))
    assert "has never published one" in txt
    assert "step1-fanout" in txt and "nrv04-retro" in txt


def test_a_fresh_fragment_renders_its_rows_and_a_stale_one_renders_stale_but_still_renders(tmp_path):
    (tmp_path / "inflight-board.md").write_text(_TERNARY_MD)
    now = _ternary_epoch()
    B.write_fragment(B.FANOUT, [{"name": "cw_ev_5cooh", "pct": 33.3, "eta_s": 7200.0,
                                 "usd_per_ns": "$0.004/ns · 1.2x basis", "state": B.RUNNING, "why": ""}],
                     now_epoch=now, root=str(tmp_path))
    fresh = B.merge_board(now_epoch=now + 60, root=str(tmp_path))
    assert "cw_ev_5cooh" in fresh and "RUNNING" in fresh and "STALE" not in fresh.split("## STEP 1")[1]

    stale = B.merge_board(now_epoch=now + 60 * 60 * 3, root=str(tmp_path))
    seg = stale.split("## STEP 1")[1].split("## NR-V04")[0]
    assert "cw_ev_5cooh" in seg, "a stale lane's rows must NOT vanish"
    assert "STALE" in seg and "UNKNOWN" in seg
    assert "it then read: RUNNING" in seg, "the original verdict must survive inside the WHY"


def test_a_stale_row_drops_its_ETA_because_nobody_re_measured_the_rate(tmp_path):
    now = _ternary_epoch()
    B.write_fragment(B.NRV04_RETRO, [{"name": "nr4a2 m1 r0", "pct": 40.0, "eta_s": 3600.0,
                                      "usd_per_ns": "— $0.12/hr (no measured ns/h: endpoint MD)",
                                      "state": B.RUNNING, "why": ""}],
                     now_epoch=now, root=str(tmp_path))
    seg = B.merge_board(now_epoch=now + 60 * 60 * 5, root=str(tmp_path)).split("## NR-V04")[1]
    assert "nr4a2 m1 r0" in seg and "40.0%" in seg
    rows = [ln for ln in seg.splitlines() if "nr4a2 m1 r0" in ln]
    assert rows and " — " in rows[0].replace("40.0%", ""), "the ETA cell must be an em dash"


def test_the_ternary_section_is_transcluded_verbatim_from_its_own_file(tmp_path):
    """Its rows' one home is the block its collect rendered; re-deriving them here would be a second home."""
    (tmp_path / "inflight-board.md").write_text(_TERNARY_MD)
    txt = B.merge_board(now_epoch=_ternary_epoch() + 60, root=str(tmp_path))
    assert "T3 ternary            16.2%  9:31 PM          $0.00456/ns · 1.34x basis  RUNNING" in txt


def test_the_merged_board_says_loudly_that_the_other_file_is_one_lane_only(tmp_path):
    """Anyone who opens `inflight-board.md` must be able to learn it is not the whole board."""
    txt = B.merge_board(now_epoch=_ternary_epoch(), root=str(tmp_path))
    assert "IS ONE LANE ONLY" in txt and B.MERGED_BOARD_MD != B.TERNARY_BOARD_MD


def test_no_two_lanes_share_a_fragment_path():
    """The whole write-race resolution: one writer per file, so no lane can erase another lane's rows."""
    paths = [B.fragment_path(l) for l, _h, _w in B.LANES if l != B.TERNARY]
    assert len(paths) == len(set(paths))
    assert all(os.path.basename(B.TERNARY_BOARD_MD) not in p for p in paths)
    assert os.path.basename(B.MERGED_BOARD_MD) not in " ".join(paths)


def test_publishing_one_lane_never_drops_another_lanes_rows(tmp_path):
    """The property that makes the merged file safe to overwrite: it is derived, never a home."""
    now = _ternary_epoch()
    B.write_fragment(B.FANOUT, [{"name": "edgeA", "pct": 10.0, "eta_s": None, "usd_per_ns": None,
                                 "state": B.RUNNING, "why": ""}], now_epoch=now, root=str(tmp_path))
    B.publish(B.NRV04_RETRO, [{"name": "nr4a3 m2 r1", "pct": 20.0, "eta_s": None, "usd_per_ns": None,
                               "state": B.RUNNING, "why": ""}], now_epoch=now, root=str(tmp_path))
    board = (tmp_path / B.MERGED_BOARD_MD).read_text()
    assert "edgeA" in board and "nr4a3 m2 r1" in board


def test_a_fragment_stores_an_ABSOLUTE_eta_so_re_merging_cannot_re_project_it(tmp_path):
    now = 1_800_000_000
    B.write_fragment(B.FANOUT, [{"name": "edgeA", "pct": 1.0, "eta_s": 3600.0, "usd_per_ns": None,
                                 "state": B.RUNNING, "why": ""}], now_epoch=now, root=str(tmp_path))
    doc = json.loads((tmp_path / B.FRAGMENT_DIR / f"{B.FANOUT}.json").read_text())
    assert "eta_s" not in doc["rows"][0]
    assert doc["rows"][0]["eta_epoch"] == now + 3600.0


def test_the_staleness_line_is_imported_not_typed():
    import vast_idle_guard as vig
    assert B.stale_after_min() == vig.LOG_SILENCE_MIN


# ── the wiring itself, pinned: a lane can lose its board by deletion as easily as by a bug ────────────────

def test_both_launchers_actually_publish_to_the_shared_renderer():
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    fan = open(os.path.join(here, "congeneric_fanout_vast.py")).read()
    ret = open(os.path.join(here, "nrv04_vast_launch.py")).read()
    assert "import inflight_board as _ifb" in fan
    assert "_ifb.publish(_ifb.FANOUT" in fan, "the fan-out no longer publishes its rows"
    assert "_ifb.publish(\n            _ifb.NRV04_RETRO" in ret or "_ifb.publish(" in ret, (
        "the NR-V04 retrospective no longer publishes its rows")
    assert "_ifb.NRV04_RETRO" in ret
    for src, lane in ((fan, "fan-out"), (ret, "NR-V04")):
        assert "state_of(" in src, f"the {lane} lane no longer uses the shared state rule"


def test_neither_lane_writes_the_other_lanes_file():
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    for name in ("congeneric_fanout_vast.py", "nrv04_vast_launch.py"):
        src = open(os.path.join(here, name)).read()
        assert "inflight-board.md" not in src, (
            f"{name} names the ternary lane's own board file — a second writer of a single-writer path is "
            f"the race this design exists to make impossible")


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# A PERCENTAGE OF THE WRONG PROTOCOL MUST NOT RENDER AS A PERCENTAGE (measured 2026-07-31)
#
# The committed NR-V04 retro board carried SIXTEEN rows reading `100.0%` for legs that are not landed legs
# at all: their census came from a `mode=smoke` run.log, which reaches `frame 5/5` in 4-20 s. A banner above
# the table said so — and `100.0%` is exactly the cell that gets quoted away from its banner.
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════

def test_a_row_whose_census_is_not_the_protocol_never_prints_a_percentage():
    txt = B.render([{"name": "nr4a3 m1 r0", "pct": 100.0, "pct_of": "smoke", "eta_s": None,
                     "usd_per_ns": None, "state": B.UNKNOWN, "why": "smoke census"}])
    assert "100.0%" not in txt, "a smoke census must never render as a completion percentage"
    assert "smoke" in txt


def test_a_normal_row_is_unaffected():
    txt = B.render([{"name": "x", "pct": 42.5, "eta_s": 60.0, "usd_per_ns": None,
                     "state": B.RUNNING, "why": ""}])
    assert "42.5%" in txt


def test_the_retro_lane_keys_pct_of_off_the_census_total_not_a_stale_leg_record():
    """The discriminator matters: a smoke-recorded unit re-placed at mode=run is running PRODUCTION, and
    keying off its stale record would mislabel a real leg. See nrv04_vast_launch.retro_board_rows."""
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    src = open(os.path.join(here, "nrv04_vast_launch.py")).read()
    assert "retro.expected_production_frames()" in src, (
        "the expected production frame count has one home in nrv04_retro_panel; a literal here would drift")
    assert '"pct_of": pct_of' in src, "the retro lane no longer labels a non-production census"


# ── the heartbeat: the ternary lane's OWN board fragment (coordinator ruling, 2026-08-01) ─────────────────
#
# The GCP lane's audit found the same defect there first and it is recorded at the line it governs; this is
# the ternary lane's copy of the rule, pinned where the ternary lane's tests live.
def _tvast_wf():
    import pathlib
    return (pathlib.Path(__file__).resolve().parents[3]
            / ".github/workflows/gpu-ternary-fep-vast.yml").read_text()


def test_the_ternary_boards_commit_is_unconditional():
    """★★ **THE REDUNDANT-LOOKING COMMIT IS THE MECHANISM.** Ruled 2026-08-01 on measured volume (1,591
    commits on `main` in 24 h, 1,392 of them fragment churn, `.git` at 267 MB) — KEPT, because that history
    is load-bearing and THIS lane supplied two of the proofs: the `5aks-market-hold.json` series exposed two
    differently-configured gates writing one file, and the `ternary-vast-rental-receipt.json` series is the
    only reason the lane's session-length distribution exists, since it records no `billed_h`.

    The forbidden shape is a `git diff --cached --quiet -- "$BOARD"` guard around the commit. It never fires
    while the generation stamp is in the file, which is precisely what makes it a LANDMINE and not a bug: it
    does nothing until someone stabilises the timestamp as an "optimisation", and from that moment a healthy
    IDLE lane commits nothing and renders byte-identically to a DEAD one.

    Comments are stripped before the assertion so the prose above the code can still NAME what it forbids —
    a rule you may not write down is a rule the next author re-derives from scratch."""
    step = _tvast_wf().split("- name: Commit the in-flight board so it is readable without a log download")[1]
    step = step.split("- name: ")[0]
    code = "\n".join(l for l in step.splitlines() if not l.strip().startswith("#"))
    assert 'git diff --cached --quiet -- "$BOARD"' not in code, \
        "the board commit must never be skipped on 'no content change' — the timestamp IS the heartbeat"
    assert code.count("git commit -q --allow-empty") == 2, \
        "--allow-empty in BOTH the first commit and the rebase-retry, so the step can neither silently " \
        "skip (the old landmine) nor fail red on a no-diff (the naive fix)"


def test_only_the_lanes_OWN_heartbeat_is_unconditional_not_every_artifact():
    """⚠ THE BOUNDARY, because over-applying this is its own defect. Guards on ORDINARY artifacts — gate
    records, forensics JSON, reduction outputs — are fine to skip: nobody infers liveness from them. The
    rule is about a lane's own heartbeat fragment, and this lane still has many legitimate skip-guards.

    ⚠ COUNTS BOTH SPELLINGS (re-pointed 2026-08-01). This used to count only the inlined
    `git diff --cached --quiet`, which is a MECHANISM; when those steps moved to
    `publish_artifacts.sh` the identical semantics arrived as `PUBLISH_IF_CHANGED=1` and the count
    collapsed from 13 to 7 — a red build on a refactor that changed no behaviour at all. That is the third
    time in one session a test pinned a workflow's shell instead of its property (the others blocked a
    rental and blinded a board detector), so the assertion is on the PROPERTY: how many publishes in this
    lane are conditional. The one that must NOT be is asserted directly above.
    """
    code = "\n".join(l for l in _tvast_wf().splitlines() if not l.strip().startswith("#"))
    conditional = code.count("git diff --cached --quiet") + code.count("PUBLISH_IF_CHANGED=1")
    assert conditional >= 10, (
        "the ordinary-artifact skip guards are correct and must not be swept away with the heartbeat one; "
        f"found only {conditional} conditional publishes in this lane")
    # …and the heartbeat itself must be none of them.
    board = _tvast_wf().split("- name: Commit the in-flight board so it is readable without a log download")[1]
    board = board.split("- name: ")[0]
    assert "PUBLISH_IF_CHANGED" not in board, \
        "the board is the lane's HEARTBEAT — making its commit conditional is the landmine by another name"


def test_the_ternary_board_carries_a_fresh_stamp_on_every_write():
    """The heartbeat only works if every write carries a NEW timestamp. The stamp is generated in the step
    itself from `date`, so it cannot be memoised — but it must also not be moved into the rendered block,
    which `inflight_board.render` produces from the rows alone and would be constant for an idle lane."""
    step = _tvast_wf().split("- name: Commit the in-flight board so it is readable without a log download")[1]
    step = step.split("- name: ")[0]
    assert "date '+%-I:%M %p ET" in step, "the stamp must be generated at write time, not carried in"
    assert "$BOARD" in step


def test_an_idle_lane_and_a_dead_lane_differ_only_by_that_stamp():
    """The property the ruling protects, stated as a test rather than as prose. `render` is PURE given the
    rows, so an idle lane's board text is byte-identical tick after tick — the ONLY thing separating
    'idle and reporting' from 'stopped reporting' is a fresh timestamp outside that block."""
    rows = [{"leg": "nr4a3_r0", "state": "IDLE", "pct": None, "why": "no host"}]
    assert B.render(rows, now_epoch=1_800_000_000) == B.render(rows, now_epoch=1_800_000_000)
    assert B.render([], now_epoch=1_800_000_000) == B.render([], now_epoch=1_800_000_000)
