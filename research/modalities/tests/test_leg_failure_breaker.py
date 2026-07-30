#!/usr/bin/env python3
"""Buying a fourth host for a unit that died on three is not a retry, it is a habit.

The tension these pin: a failed record must NEVER permanently block its own retry (run_ternary_leg.sh is
explicit — testing for existence meant no fix could ever be validated), yet a unit dying at the same phase on
host after host must stop being bought. The discriminator is the COUNT, not the record.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import leg_failure_breaker as lfb  # noqa: E402

MOD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "leg_failure_breaker.py")
LAUNCH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ternary_vast_launch.py")

FAILED = {"status": "failed", "phase": "warmup", "rc": 1}

# ★ r2's EXACT SHAPE, 2026-07-29. `calib_hi_to_lo__ternary_vhl_r2_dt4.0fs_wu1.0_edge_reps` carried a
# `status=failed` record written by an EARLIER attempt, then ran on a fresh host and ADVANCED (committed
# census warmup/384 -> warmup/576, log uploaded until 12:33 UTC), and at 12:37 UTC `collect` destroyed that
# host on `⛔ DESTROYED this pass (capacity refusal on machine 29711; destroy: a qualifying replacement is on
# the board)`. The record was still `failed`, the archive stood at 51, and the breaker blocked the unit
# permanently — a correct market teardown turned into a permanent block on a leg that was working.
R2_RECORD = {"status": "failed", "phase": "warmup", "rc": 1, "updated_utc": "2026-07-29T09:41:00Z"}
R2_NEWEST_COMMIT = "2026-07-29T12:33:00Z"
R2_EVICTION = {"utc": "2026-07-29T12:37:00Z", "machine_id": 29711,
               "why": "capacity refusal on machine 29711; destroy: a qualifying replacement is on the board"}
R2_ATTEMPTS = 51

# ★ THE CLASS THE BREAKER MUST KEEP STOPPING: 84 rentals burned on units dying at `proto.create`. Its
# high-water mark is FROZEN at warmup/832, inherited from an older attempt — which is precisely why the
# VALUE of `committed` is a known-bad discriminator and only its TIMESTAMP can be used.
SETUP_DEATH_RECORD = {"status": "failed", "phase": "proto.create", "rc": 1,
                      "updated_utc": "2026-07-29T09:00:00Z"}
SETUP_DEATH_STALE_COMMIT = "2026-07-28T22:14:00Z"     # warmup/832, written by an attempt a day earlier


# ---------------------------------------------------------------- it trips
def test_it_blocks_at_the_threshold():
    d = lfb.decide(FAILED, lfb.DEFAULT_THRESHOLD)
    assert d["block"] is True and d["verdict"] == lfb.BLOCK


def test_it_blocks_above_the_threshold():
    assert lfb.decide(FAILED, lfb.DEFAULT_THRESHOLD + 5)["block"] is True


# ---------------------------------------------------------------- it must NOT trip
def test_one_failure_is_noise_not_a_fault():
    # A spot preemption or a bad host produces exactly this. Blocking here would stop the lane on a transient.
    assert lfb.decide(FAILED, 1)["block"] is False


def test_two_failures_can_still_be_one_unlucky_machine():
    # Machine 28164 served two of the observed deaths, which is precisely why 2 is not the threshold.
    assert lfb.decide(FAILED, 2)["block"] is False


def test_a_unit_that_has_never_run_is_never_blocked():
    assert lfb.decide(None, 99)["block"] is False


def test_a_done_unit_is_never_blocked():
    assert lfb.decide({"status": "done"}, 99)["block"] is False


def test_an_unrecognised_status_fails_OPEN():
    # This module exists to stop waste. Refusing to rent on a status it does not recognise would let one
    # schema change silently halt the lane, which is far worse than one extra rental.
    assert lfb.decide({"status": "running"}, 99)["block"] is False
    assert lfb.decide({}, 99)["block"] is False


def test_an_unreadable_attempt_listing_fails_OPEN():
    # count_attempts returns None on a listing failure. Opposite of the market gate's fail-CLOSED rule, and
    # deliberately: there, guessing wrong SPENDS blind; here, guessing wrong costs at most one purchase.
    assert lfb.decide(FAILED, None)["block"] is False


# ---------------------------------------------------------------- a block must explain itself
def test_a_block_carries_its_evidence():
    d = lfb.decide(FAILED, 4)
    assert "4 separate rented hosts" in d["why"]
    assert "NOT permanent" in d["why"], "a block that reads as terminal will be worked around, not fixed"
    assert d["n_attempts"] == 4 and d["threshold"] == lfb.DEFAULT_THRESHOLD


def test_a_block_never_renders_like_a_price_hold():
    # CLAUDE.md §1, one glyph one meaning. This is not a market decision and must not read as one.
    line = lfb.render("u1", lfb.decide(FAILED, 3))
    assert "NOT RENTING" in line and "$0 spent" in line
    assert "DRIFT" not in line and "PAYING" not in line


# ---------------------------------------------------------------- purity and reach
def test_the_decision_is_pure():
    src = open(MOD).read()
    head = src.split("def count_attempts", 1)[0]
    for banned in ("time.time(", "datetime.now(", "boto3", "requests"):
        assert banned not in head, banned


def test_it_cannot_touch_a_running_host():
    # It acts at the moment of RENTING only — same boundary as the relaunch market gate. Asserted against
    # CODE, not the whole file: the module docstring necessarily describes the teardown loop it exists to
    # break, so a plain scan trips over its own rationale.
    import ast
    tree = ast.parse(open(MOD).read())
    names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    names |= {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    for banned in ("destroy", "terminate", "stop_instance", "destroy_instance"):
        assert not any(banned in str(n) for n in names), banned


def test_the_threshold_is_not_per_lane_tunable():
    # A per-lane override is how a breaker gets quietly raised until it never trips.
    src = open(MOD).read()
    assert src.count("DEFAULT_THRESHOLD = ") == 1


# ============================================================================================================
# ★ THE CALL SITE. `needed` is what the gate prices and the launcher buys.
# ============================================================================================================
def _launch_src():
    return open(LAUNCH).read()


def test_outstanding_units_consults_the_breaker():
    src = _launch_src()
    assert "leg_failure_breaker" in src, "the launcher no longer imports the breaker"
    assert "lfb.decide(" in src, "the launcher no longer CALLS the breaker"


def test_blocked_units_are_removed_from_needed():
    src = _launch_src()
    i = src.index('return {"needed":')
    assert "not in _blocked" in src[i:i + 200], "a blocked unit would still be priced and rented"


def test_blocked_units_are_returned_not_dropped():
    # CLAUDE.md §6: never silently drop units. A hold the readout cannot see is the failure mode.
    src = _launch_src()
    i = src.index('return {"needed":')
    assert '"blocked": _blocked' in src[i:i + 300]


def test_the_on_host_retry_rule_is_untouched():
    # run_ternary_leg.sh must keep re-running a failed leg. If this ever flips to blocking on existence, no
    # fix could be validated — the exact regression the breaker exists to avoid needing.
    # The rule lives in the onstart script the launcher embeds, not in run_ternary_leg.sh.
    assert "re-running rather than exiting" in _launch_src()


# ============================================================================================================
# ★★ A STALLED LANE AND A FINISHED LANE MUST NOT RENDER ALIKE.
#
# Measured on the breaker's first live tick (2026-07-29, run 30442395727). The breaker correctly withheld 2 of
# edge_reps' 4 units, which dropped the gate's count to zero and landed on the n==0 branch — which then
# announced `nothing-to-launch`, "every unit already done or hosted", over a lane stalled on a code fault.
# Its own numbers did not even sum: "2 done, 0 already running" for a 4-unit mode. That is CLAUDE.md §6's
# named prohibition, and the breaker CREATED it, so it is pinned here rather than beside the gate.
# ============================================================================================================
import unittest.mock as _m  # noqa: E402

import ternary_vast_launch as _t  # noqa: E402


def _out(blocked=None, done=("u_bin_r1", "u_bin_r2")):
    return {"needed": [], "blocked": blocked or {}, "done": list(done), "live": [],
            "live_hosts": {}, "dead_hosts": {}, "listing_ok": True, "listing_error": None}


def _blocked_two():
    return {"u_tern_r1": lfb.decide(FAILED, 3), "u_tern_r2": lfb.decide(FAILED, 4)}


def test_blocked_units_do_not_make_the_lane_look_finished():
    with _m.patch.object(_t, "outstanding_units", return_value=_out(_blocked_two())):
        action, r = _t.gate_for_mode("edge_reps")
    assert action == "blocked", "a stalled lane reported itself as nothing-to-launch"
    assert r["nothing_to_launch"] is False
    assert "NOT finished" in r["reason"]


def test_a_blocked_lane_is_not_filed_as_a_price_hold():
    # The board is never consulted, so it must not run the hold clock or fire the hold warning.
    with _m.patch.object(_t, "outstanding_units", return_value=_out(_blocked_two())):
        action, r = _t.gate_for_mode("edge_reps")
    assert action != "hold" and r["hold"] is False
    assert "NOT price-held" in r["reason"]


def test_every_blocked_unit_is_named_with_its_count():
    with _m.patch.object(_t, "outstanding_units", return_value=_out(_blocked_two())):
        _, r = _t.gate_for_mode("edge_reps")
    got = {b["unit_id"]: b["n_attempts"] for b in r["units_blocked"]}
    assert got == {"u_tern_r1": 3, "u_tern_r2": 4}
    assert all(b["why"] for b in r["units_blocked"]), "a block must carry its evidence into the snapshot"


def test_a_genuinely_finished_lane_still_says_nothing_to_launch():
    # The fix must not turn every quiet tick into an alarm.
    with _m.patch.object(_t, "outstanding_units", return_value=_out(None)):
        action, r = _t.gate_for_mode("edge_reps")
    assert action == "nothing-to-launch" and r["nothing_to_launch"] is True
    assert "units_blocked" not in r


def test_blocked_gets_an_exit_code_distinct_from_finished_and_from_hold():
    src = open(LAUNCH).read()
    i = src.index('"nothing-to-launch": 3')
    assert '"blocked": 4' in src[i - 200:i + 200], \
        "blocked must not share an exit code with a finished lane or a price hold"


def test_the_workflow_records_blocked_under_its_own_word():
    wf = open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))),
        ".github", "workflows", "gpu-ternary-fep-vast.yml")).read()
    assert 'RC" = 4' in wf, "exit 4 falls through to the hold branch and is filed as a price hold"
    assert "--record blocked" in wf


# ============================================================================================================
# ★★ THE BREAKER MUST GATE THE PURCHASE, NOT JUST THE QUOTE.
#
# Measured 2026-07-29 and it cost a rental. `outstanding_units` filtered `needed`, so `gate_for_mode`
# correctly reported `n_units 1` with r2 blocked on 49 failed hosts — and then `submit()`, which never
# called the breaker, rebuilt its own list from `units_for(mode)` and rented BOTH r1 and r2. The receipt
# names two instances 6 minutes after the readout said one. A guard that filters the quote and not the
# purchase is not a guard.
# ============================================================================================================
def test_submit_consults_the_breaker_before_renting():
    src = _launch_src()
    i = src.index("def submit(")
    body = src[i:i + 9000]
    assert "breaker_verdicts(" in body, "submit() rents without ever asking the breaker"


def test_a_blocked_unit_is_removed_from_what_submit_rents():
    src = _launch_src()
    i = src.index("def submit(")
    body = src[i:i + 9000]
    j = body.index("keep = [j for j in jobs")
    line = body[j:body.index("\n", j)]
    assert "_brk" in line, f"blocked units are still rented; keep-line is: {line.strip()}"


def test_the_gate_and_the_launcher_share_ONE_breaker_call_site():
    # ★★ THIS TEST USED TO BE `src.count("lfb.decide(") >= 2` — AND THAT IS WHY IT NEVER FIRED.
    #
    # It named the right property ("the gate and the launcher use the SAME verdict") and asserted something
    # that cannot check it: a COUNT OF CALLS. Two loops calling `lfb.decide` with independently-gathered
    # arguments satisfy `>= 2` perfectly and can still return different answers — which is exactly what the
    # two loops did, since each built its own record map and its own attempt count. The assertion passed on
    # every commit while the property it names was unverified.
    #
    # There is now one call site, `breaker_verdicts`, and both paths go through it. The structural half is
    # below; the behavioural half — running both paths against the same state and comparing what they
    # withhold — is `test_the_gate_and_submit_withhold_the_SAME_units`.
    # Counted from the AST, not from the text — the old assertion's own failure mode. A source-text count of
    # `lfb.decide(` is satisfied by a docstring that MENTIONS the call (this file's docstrings now do), which
    # is one more way a text assertion can be true while the code is not.
    import ast
    src = _launch_src()
    calls = [n for n in ast.walk(ast.parse(src))
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "decide" and getattr(n.func.value, "id", None) == "lfb"]
    assert len(calls) == 1, \
        "more than one place decides a breaker verdict — that is the drift this test exists to stop"
    i = src.index("def outstanding_units(")
    assert "breaker_verdicts(" in src[i:i + 4000], "the gate path no longer routes through breaker_verdicts"
    j = src.index("def submit(")
    assert "breaker_verdicts(" in src[j:j + 9000], "the launch path no longer routes through breaker_verdicts"


def test_submit_still_fails_CLOSED_on_an_unreadable_instance_list():
    # The breaker fails OPEN; the instance-list check must keep failing CLOSED. Opposite directions, and
    # conflating them would let an unreadable listing double-buy on top of running legs.
    src = _launch_src()
    i = src.index("def submit(")
    body = src[i:i + 9000]
    assert "REFUSING TO RENT" in body


# ============================================================================================================
# ★★ AN EVICTED UNIT IS NOT A FAILED UNIT (measured 2026-07-29; it cost r2 a permanent block).
#
# The conditional-teardown ruling (trimcrae, 2026-07-27) makes `collect` destroy a capacity-refused host once
# a qualifying replacement is on the board. That is a MARKET decision about a HOST. The breaker read the
# unit's stale `status=failed` record plus a growing attempt archive and filed our own correct teardown as
# another strike — so the teardown slowly poisoned every unit it evicted, and a cost decision became a
# permanent block on a leg whose checkpoint was advancing.
#
# The discriminator is NOT "did it fail" and NOT "has it made progress". It is: **is the failed record still
# the NEWEST fact about this unit?** Everything below pins that, in both directions.
# ============================================================================================================
def test_r2s_exact_shape_is_not_blocked():
    # Advancing leg, evicted on a capacity refusal, stale failed record, 51 archived attempts.
    sup = lfb.superseding_evidence(R2_RECORD, newest_commit_utc=R2_NEWEST_COMMIT, eviction=R2_EVICTION)
    d = lfb.decide(R2_RECORD, R2_ATTEMPTS, superseding=sup)
    assert d["block"] is False, "the unit that was working when we took its host away is still blocked"
    assert d["verdict"] == lfb.ALLOW_SUPERSEDED
    # The eviction is the NEWER of the two facts (12:37 vs the 12:33 commit), so it is the one cited.
    assert d["superseded_by"]["kind"] == lfb.KIND_EVICTION
    assert d["n_attempts"] == R2_ATTEMPTS, "the strike count must not be forgiven, only out-dated"


def test_a_commit_after_the_record_is_enough_on_its_own():
    # The eviction receipt is a later addition; a unit evicted before it existed (or by a path that does not
    # write one) must still be re-placed on the strength of the science having advanced.
    sup = lfb.superseding_evidence(R2_RECORD, newest_commit_utc=R2_NEWEST_COMMIT, eviction=None)
    assert sup["kind"] == lfb.KIND_COMMIT
    assert lfb.decide(R2_RECORD, R2_ATTEMPTS, superseding=sup)["block"] is False


def test_an_eviction_alone_is_enough_when_nothing_was_committed():
    # The case the commit store cannot see: evicted during staging, before the first iteration landed.
    sup = lfb.superseding_evidence(R2_RECORD, newest_commit_utc=None, eviction=R2_EVICTION)
    assert sup["kind"] == lfb.KIND_EVICTION
    assert lfb.decide(R2_RECORD, R2_ATTEMPTS, superseding=sup)["block"] is False


# ---------------------------------------------------------------- and it must NOT weaken the real guard
def test_the_setup_death_class_is_still_blocked():
    # 84 rentals were burned on units dying at `proto.create`. They commit nothing new and are destroyed on
    # "unit FAILED — nothing left to produce", never on the capacity branch, so nothing supersedes.
    sup = lfb.superseding_evidence(SETUP_DEATH_RECORD, newest_commit_utc=SETUP_DEATH_STALE_COMMIT,
                                   eviction=None)
    assert sup is None
    assert lfb.decide(SETUP_DEATH_RECORD, 84, superseding=sup)["block"] is True


def test_a_frozen_high_water_mark_cannot_lift_a_block():
    # The known-bad discriminator, pinned. `committed=warmup/832` on a unit dying at setup is a VALUE
    # inherited from an older attempt; only its TIMESTAMP carries recency, and that timestamp is old.
    assert lfb.superseding_evidence(SETUP_DEATH_RECORD, newest_commit_utc=SETUP_DEATH_STALE_COMMIT) is None


def test_a_commit_at_the_same_instant_does_not_supersede():
    # Strictly newer. A leg writes its commit and then its failed record; equal stamps are the rounding of
    # that same moment, not evidence of a later life.
    same = {"status": "failed", "updated_utc": "2026-07-29T12:33:00Z"}
    assert lfb.superseding_evidence(same, newest_commit_utc="2026-07-29T12:33:00Z") is None


def test_supersession_is_self_limiting():
    # ONE more rental, not amnesty: if that rental dies and files a fresh record, the record is newest again
    # and the unit blocks at the SAME count on the very next tick.
    after = {"status": "failed", "phase": "proto.create", "rc": 1, "updated_utc": "2026-07-29T13:40:00Z"}
    sup = lfb.superseding_evidence(after, newest_commit_utc=R2_NEWEST_COMMIT, eviction=R2_EVICTION)
    assert sup is None
    assert lfb.decide(after, R2_ATTEMPTS, superseding=sup)["block"] is True


def test_an_undateable_record_leaves_the_block_standing():
    # Opposite direction to `count_attempts`'s fail-OPEN, and deliberately: failing open on the COUNT costs
    # one rental, failing open on SUPERSESSION re-opens the loop that burned 84.
    undateable = {"status": "failed", "phase": "warmup", "rc": 1}
    assert lfb.superseding_evidence(undateable, newest_commit_utc=R2_NEWEST_COMMIT,
                                    eviction=R2_EVICTION) is None
    assert lfb.decide(undateable, R2_ATTEMPTS, superseding=None)["block"] is True


def test_supersession_cannot_unblock_below_the_threshold_path():
    # Sanity: it only ever reaches the carve-out at/above the threshold, and never flips an allow to a block.
    sup = lfb.superseding_evidence(R2_RECORD, newest_commit_utc=R2_NEWEST_COMMIT)
    assert lfb.decide(R2_RECORD, 1, superseding=sup)["block"] is False
    assert lfb.decide({"status": "done"}, 99, superseding=sup)["block"] is False


# ---------------------------------------------------------------- the rejected discriminators, pinned
def test_the_phase_marker_and_the_log_are_NOT_inputs():
    # ⛔ THE MOST DANGEROUS CANDIDATE, and the one that looks right in a diagnostic. `phase.txt` is rewritten
    # by EVERY attempt on its way IN (start/cloned/staging) — before it dies — and `run.log` is pushed by the
    # sync loop every ~2 min regardless of progress. A container that crash-loops never returns and so never
    # files a `leg.json` (CLAUDE.md §6), which would leave its phase marker permanently newer than the last
    # failed record: the discriminator would read true on every tick and the 84-rental loop would return.
    # There must be no way to feed either one in.
    import inspect
    params = set(inspect.signature(lfb.superseding_evidence).parameters)
    assert params == {"record", "newest_commit_utc", "eviction"}, \
        f"a freshness signal that is not durable progress leaked into the discriminator: {params}"


def test_record_predates_host_is_three_valued():
    # `_record_is_newer_than_instance` collapses "older" and "unreadable" both to False — right for a
    # teardown (never reap on a guess), wrong for authorising an eviction receipt that can lift a block.
    assert lfb.record_predates_host({"updated_utc": "2026-07-29T09:41:00Z"}, 1785325803.0) is True
    assert lfb.record_predates_host({"updated_utc": "2026-07-29T23:41:00Z"}, 1785325803.0) is False
    assert lfb.record_predates_host({}, 1785325803.0) is None
    assert lfb.record_predates_host({"updated_utc": "2026-07-29T09:41:00Z"}, None) is None


def test_a_lifted_block_does_not_render_like_an_applied_one():
    # CLAUDE.md §1, one glyph one meaning: "the breaker never fired" and "the breaker fired and evidence
    # overrode it" must not be the same silence, and must not be the same glyph either.
    sup = lfb.superseding_evidence(R2_RECORD, newest_commit_utc=R2_NEWEST_COMMIT, eviction=R2_EVICTION)
    line = lfb.render("u_tern_r2", lfb.decide(R2_RECORD, R2_ATTEMPTS, superseding=sup))
    assert "↻ RE-PLACING" in line and "NOT RENTING" not in line and "⛔" not in line
    assert "51" in line, "a lifted block must still name the count it lifted"
    assert "DRIFT" not in line and "PAYING" not in line


def test_the_eviction_receipt_has_one_home_for_its_key():
    assert lfb.eviction_key("ternary-vast", "u1") == "ternary-vast/legs/u1/_evicted.json"
    assert lfb.eviction_key("ternary-vast/", "u1") == lfb.eviction_key("ternary-vast", "u1")


# ============================================================================================================
# ★★ THE THREE READOUT GAPS OF 2026-07-29, ALL THE SAME SHAPE: A WITHHELD UNIT THAT NOBODY CAN SEE.
#
# Measured from the committed artifacts, not remembered:
#
#   ternary-vast-market-hold.json @ 2026-07-29T11:07:23Z   n_units 0 -> units_blocked names r1 (35) and
#                                                          r2 (49). The n == 0 branch. Correct.
#   ternary-vast-market-hold.json @ 2026-07-29T11:46:13Z   n_units 1, units_needing_host = [r1].
#   ternary-vast-market-hold.json @ 2026-07-29T13:01:41Z   n_units 1, units_needing_host = [r1].
#       -> on BOTH of those CLEAR ticks r2 appears in NO list in the file: not done, not live, not needed,
#          not blocked. It vanished, because `units_blocked` was only ever built inside the n == 0 branch.
#   ternary-vast-rental-receipt.json @ 2026-07-29T13:05:24Z  n_requested 0, note "every unit for this mode
#          is already done or running". r1 really was running (its host's `actual_status` flipped from
#          `exited` at 13:01 to `running` by 13:05 — a transient terminal status, documented in `submit`).
#          r2 was neither done nor running: it was withheld on 51 strikes. The receipt asserted otherwise.
# ============================================================================================================
def _blocked_one(uid="u_tern_r2", n=51):
    return {uid: lfb.decide(FAILED, n)}


def test_a_withheld_unit_is_named_even_when_the_gate_CLEARS():
    # THE 11:46 / 13:01 GAP. `n > 0` means some unit is being priced; it does not mean every other unit is
    # accounted for. Before the fix this branch emitted only done/live/needed and the withheld unit was
    # invisible by construction — on the branch the lane spends most of its time in.
    out = {"needed": ["u_tern_r1"], "blocked": _blocked_one(), "unblocked": {},
           "done": ["u_bin_r1", "u_bin_r2"], "live": [], "live_hosts": {}, "dead_hosts": {},
           "listing_ok": True, "listing_error": None}
    with _m.patch.object(_t, "outstanding_units", return_value=out), \
         _m.patch.object(_t, "market_gate", return_value=(False, {"reason": "board is cheap", "hold": False})):
        action, r = _t.gate_for_mode("edge_reps")
    assert action == "clear", "the unit that CAN be rented must still be rented"
    assert "units_blocked" in r, "a withheld unit vanished from a CLEAR readout — the 13:01:41Z defect"
    assert [b["unit_id"] for b in r["units_blocked"]] == ["u_tern_r2"]
    assert r["units_blocked"][0]["n_attempts"] == 51
    assert "WITHHELD" in r["reason"] and "u_tern_r2" in r["reason"]
    # Every unit of the mode must be findable somewhere in the snapshot — that is the whole property.
    named = set(r["units_done"]) | set(r["units_live"]) | set(r["units_needing_host"]) \
        | {b["unit_id"] for b in r["units_blocked"]}
    assert named == {"u_bin_r1", "u_bin_r2", "u_tern_r1", "u_tern_r2"}


def test_a_clear_gate_with_nothing_withheld_stays_quiet():
    # The fix must not turn every ordinary tick into an alarm.
    out = {"needed": ["u_tern_r1"], "blocked": {}, "unblocked": {}, "done": [], "live": [],
           "live_hosts": {}, "dead_hosts": {}, "listing_ok": True, "listing_error": None}
    with _m.patch.object(_t, "outstanding_units", return_value=out), \
         _m.patch.object(_t, "market_gate", return_value=(False, {"reason": "board is cheap", "hold": False})):
        action, r = _t.gate_for_mode("edge_reps")
    assert action == "clear" and "units_blocked" not in r and "WITHHELD" not in r["reason"]


def test_a_withheld_unit_survives_an_unreadable_instance_listing():
    out = {"needed": [], "blocked": _blocked_one(), "unblocked": {}, "done": [], "live": [],
           "live_hosts": {}, "dead_hosts": {}, "listing_ok": False, "listing_error": "HTTPError: 403"}
    with _m.patch.object(_t, "outstanding_units", return_value=out):
        action, r = _t.gate_for_mode("edge_reps")
    assert action == "hold", "the unreadable-listing branch must still fail CLOSED"
    assert [b["unit_id"] for b in r["units_blocked"]] == ["u_tern_r2"]


# ---------------------------------------------------------------- the receipt
def test_the_receipt_names_a_withheld_unit_instead_of_calling_it_done_or_running():
    # THE 13:05:24Z DEFECT. `n_requested: 0` with the note "every unit for this mode is already done or
    # running" over a mode where one unit was running and one was withheld on 51 strikes.
    doc = _t.write_rental_receipt(
        "edge_reps", requested=[], submitted=[], failed=[],
        withheld=[{"unit_id": "u_tern_r2", "reason": "failure-breaker", "n_attempts": 51,
                   "why": "51 separate rented hosts"}],
        skipped=[{"unit_id": "u_tern_r1", "why": "running"}],
        path=_t.receipt_path())
    assert doc["n_withheld"] == 1
    assert doc["withheld"][0]["unit_id"] == "u_tern_r2"
    assert "WITHHELD" in doc["note"] and "u_tern_r2" in doc["note"]
    assert "NOT" in doc["note"] and "finished" in doc["note"]
    assert "already done or running" not in doc["note"], \
        "the receipt still claims a withheld unit is done or running"
    # And the unit that genuinely WAS running is named as such, separately — the two facts must not merge.
    assert doc["skipped"] == [{"unit_id": "u_tern_r1", "why": "running"}]


def test_a_genuinely_finished_mode_still_gets_the_quiet_note():
    doc = _t.write_rental_receipt("edge_reps", requested=[], submitted=[], failed=[],
                                  skipped=[{"unit_id": "u_bin_r1", "why": "done"}],
                                  path=_t.receipt_path())
    assert "already done or running" in doc["note"] and "WITHHELD" not in doc["note"]
    assert "n_withheld" not in doc


def test_the_caller_no_longer_asserts_the_wording():
    # ONE HOME for the sentence (CLAUDE.md §1). `submit` used to hand this branch a hard-coded note that was
    # false whenever the breaker had withheld something.
    src = _launch_src()
    i = src.index("if not keep:")
    body = src[i:i + 1600]
    assert 'note="every unit for this mode is already done or running' not in body, \
        "submit() is asserting the receipt's wording again instead of passing the facts"
    assert "withheld=_withheld_rows" in body


# ============================================================================================================
# ★★ THE SAME-VERDICT PROPERTY, RUN RATHER THAN GREPPED.
# ============================================================================================================
class _FakeS3:
    """The three reads `breaker_verdicts` makes, served from a per-unit fixture. No network, no boto3."""

    def __init__(self, units):
        self.units = units          # {uid: {"attempts": n, "commit_utc": str|None, "eviction": dict|None}}

    def _u(self, prefix_marker, prefix):
        for uid in self.units:
            if f"/{uid}/" in prefix or prefix.endswith(f"/{uid}"):
                return uid
        return None

    def get_paginator(self, _name):
        outer = self

        class _P:
            def paginate(self, Bucket=None, Prefix=""):      # noqa: N803 — boto3's own kwarg names
                uid = outer._u(None, Prefix)
                f = outer.units.get(uid) or {}
                if "/attempts/" in Prefix:
                    return [{"Contents": [{"Key": f"{Prefix}a{i}.log"} for i in range(f.get("attempts", 0))]}]
                if "/commits/" in Prefix:
                    c = f.get("commit_utc")
                    if not c:
                        return [{"Contents": []}]
                    import datetime as _dt
                    lm = _dt.datetime.strptime(c, "%Y-%m-%dT%H:%M:%SZ")
                    return [{"Contents": [{"Key": f"{Prefix}warmup/iter-576/x.nc", "LastModified": lm}]}]
                return [{"Contents": []}]
        return _P()

    def put_object(self, **_kw):
        return {}

    def get_object(self, Bucket=None, Key=""):               # noqa: N803
        uid = self._u(None, Key)
        ev = (self.units.get(uid) or {}).get("eviction")
        if Key.endswith("/_evicted.json") and ev:
            import io
            import json as _json
            return {"Body": io.BytesIO(_json.dumps(ev).encode())}
        raise KeyError(Key)


class _Job:
    def __init__(self, uid):
        self.env = {"UNIT_ID": uid}
        self.name = uid
        self.resources = _m.MagicMock()


_R1, _R2 = "u_tern_r1", "u_tern_r2"


def _fixture_r2_stuck(r1_done=True):
    """r1 out of the way; r2 in the exact stuck shape — failed record, 51 attempts, nothing newer than it."""
    return ({_R1: {"status": "done"} if r1_done else None, _R2: R2_RECORD},
            _FakeS3({_R1: {"attempts": 3}, _R2: {"attempts": R2_ATTEMPTS}}))


def _fixture_r2_evicted():
    """The same, plus the durable evidence the teardown now leaves: a commit written after the record, and
    the eviction receipt saying WE took the host on a capacity refusal."""
    return ({_R1: {"status": "done"}, _R2: R2_RECORD},
            _FakeS3({_R1: {"attempts": 3},
                     _R2: {"attempts": R2_ATTEMPTS, "commit_utc": R2_NEWEST_COMMIT,
                           "eviction": R2_EVICTION}}))


class _NoOffers:
    """A backend that answers every rental with `NoQualifyingOffer`. Nothing is bought, nothing is billed —
    but `requested` on the receipt still records WHICH units the launcher tried to rent, which is the fact
    these tests are after."""

    def submit(self, job):
        from gpu_backend import NoQualifyingOffer
        raise NoQualifyingOffer("no board in a unit test")


def _run_both(records, s3, live_hosts=None):
    """(gate's withheld set, launcher's withheld set, gate answer, receipt) from ONE state.

    Both paths are driven against the same fakes in the same `with` block, which is the point: the property
    "the gate and the launcher use the same verdict" cannot be checked by counting call sites, only by
    running both and comparing.
    """
    recs = {u: r for u, r in records.items() if r}
    jobs = {u: _Job(u) for u in records}
    hosts = {"live": live_hosts or {}, "dead": {}}
    with _m.patch.object(_t, "_s3", return_value=s3), \
         _m.patch.object(_t, "leg_records", return_value=recs), \
         _m.patch.object(_t, "unit_hosts", return_value=hosts), \
         _m.patch.object(_t, "units_for", return_value=[(u, 0, "fwd") for u in records]), \
         _m.patch.object(_t, "build_jobspec", side_effect=lambda l, *a, **k: jobs[l]), \
         _m.patch.object(_t, "rented_rate_row", side_effect=lambda u, i: {"unit_id": u}), \
         _m.patch.object(_t, "blocked_machine_ids", return_value=[]), \
         _m.patch.object(_t, "get_backend", return_value=_NoOffers()), \
         _m.patch.dict(os.environ, {"VAST_API_KEY": "test-key"}):
        gate = _t.outstanding_units("edge_reps")
        _t.submit("edge_reps")
    import json as _json
    receipt = _json.load(open(_t.receipt_path()))
    return set(gate["blocked"]), {w["unit_id"] for w in (receipt.get("withheld") or [])}, gate, receipt


def test_the_gate_and_submit_withhold_the_SAME_units():
    # ★★ THE BEHAVIOURAL FORM OF THE PROPERTY THE OLD SOURCE-TEXT TEST ONLY NAMED. Both paths are run
    # against one fixed state and the sets they withhold are compared — which is the only assertion that
    # would catch two loops gathering different arguments for the same `decide`.
    records, s3 = _fixture_r2_stuck()
    gate_blocked, launch_withheld, gate, receipt = _run_both(records, s3)
    assert gate_blocked == {_R2} == launch_withheld
    assert receipt["n_requested"] == 0 and receipt["n_rented"] == 0


def test_the_receipt_of_a_withheld_tick_does_not_claim_the_mode_is_finished():
    records, s3 = _fixture_r2_stuck()
    *_, receipt = _run_both(records, s3)
    assert "already done or running" not in receipt["note"]
    assert _R2 in receipt["note"] and "WITHHELD" in receipt["note"]


def test_r2_is_RE_PLACED_once_the_eviction_is_recorded():
    # ★★ THE END-TO-END ANSWER TO "will r2 re-place itself on the next tick, with no manual intervention?"
    # Same unit, same 51 strikes, same untouched `status=failed` record and same untouched attempt archive —
    # the only difference is the durable evidence that its last attempt was ended by US and that it had
    # committed work since the record. It goes back into `needed`, and the launcher tries to rent it.
    records, s3 = _fixture_r2_evicted()
    gate_blocked, launch_withheld, gate, receipt = _run_both(records, s3)
    assert gate_blocked == set() and launch_withheld == set()
    assert _R2 in gate["needed"], "r2 is still not being re-placed"
    assert receipt["requested"] == [_R2], "the launcher did not even TRY to rent r2"
    assert [u["unit_id"] for u in receipt["unblocked"]] == [_R2], \
        "renting a 51-strike unit must be visible in the artifact, not only in a log line"
    assert _R2 in gate["unblocked"], "an un-blocked unit must be visible, not silently allowed"
    assert gate["unblocked"][_R2]["superseded_by"]["kind"] == lfb.KIND_EVICTION
    assert gate["unblocked"][_R2]["n_attempts"] == R2_ATTEMPTS, "the strike count was reset — it must not be"


def test_a_live_unit_and_a_withheld_unit_are_told_apart_in_the_receipt():
    # THE 13:01 -> 13:05 PAIR, reproduced. r1's host reads live by the time `submit` runs (a transient
    # terminal status, seconds earlier, is what put it in the gate's `needed`); r2 is withheld. The old
    # receipt filed BOTH under "already done or running".
    records, s3 = _fixture_r2_stuck(r1_done=False)
    *_, receipt = _run_both(records, s3, live_hosts={_R1: {"id": 46191306, "machine_id": 28164}})
    assert {s["unit_id"]: s["why"] for s in receipt["skipped"]} == {_R1: "running"}
    assert [w["unit_id"] for w in receipt["withheld"]] == [_R2]


# ============================================================================================================
# ★★ THE FOURTH DOOR: THE LEDGER'S OUTCOME WORD.
#
# `blocked` was added to the ledger's vocabulary on 2026-07-29 precisely so a stalled lane could not be filed
# as a finished one — and the GATE path recorded it correctly. The LAUNCH path did not: `record()` derived
# the word from `n_rented == 0` plus `n_requested`, and `n_requested == 0` has two causes. The 13:05:24Z tick
# had one unit genuinely running and one withheld on 51 strikes, so it was filed `nothing-to-launch` — "no
# unit needed a host" — for exactly the state the gate had just filed as `blocked`. Same prohibition, second
# door.
# ============================================================================================================
def test_a_withheld_tick_is_filed_blocked_not_nothing_to_launch(tmp_path):
    import ternary_launch_ledger as _tll
    receipt = {"n_requested": 0, "n_rented": 0, "n_withheld": 1,
               "withheld": [{"unit_id": "u_tern_r2", "reason": "failure-breaker", "n_attempts": 51}],
               "already_live": [{"unit_id": "u_tern_r1", "usd_per_ns": 0.00356}]}
    e = _tll.record("launched", receipt=receipt, path=str(tmp_path / "ledger.json"))
    assert e["outcome"] == "blocked", "a stalled lane was filed as a finished one"
    assert e["n_withheld"] == 1 and e["withheld"][0]["unit_id"] == "u_tern_r2"


def test_a_genuinely_satisfied_tick_is_still_nothing_to_launch(tmp_path):
    import ternary_launch_ledger as _tll
    e = _tll.record("launched", receipt={"n_requested": 0, "n_rented": 0},
                    path=str(tmp_path / "ledger.json"))
    assert e["outcome"] == "nothing-to-launch" and "n_withheld" not in e


def test_a_real_shortfall_is_still_a_fault(tmp_path):
    import ternary_launch_ledger as _tll
    e = _tll.record("launched", receipt={"n_requested": 2, "n_rented": 0},
                    path=str(tmp_path / "ledger.json"))
    assert e["outcome"] == "submit-failed"


def test_the_eviction_receipt_is_written_only_where_the_teardown_knows_why():
    # ⛔ THE ONE WAY THIS FIX COULD WEAKEN THE GUARD. An eviction receipt LIFTS a block, so it must be
    # written only from the capacity-refusal teardown — the branch that is unreachable once `crashed` is
    # True — and only after `record_predates_host` returns an explicit True. A unit whose failed record
    # cannot be dated must get no receipt: crediting an eviction on a guess is how the 84-rental loop
    # returns. Asserted structurally because exercising `collect` needs a live Vast API.
    src = _launch_src()
    calls = [i for i in range(len(src)) if src.startswith("lfb.record_eviction(", i)]
    assert len(calls) == 1, "the eviction receipt is written from more than one place"
    window = src[calls[0] - 2200:calls[0]]
    assert "record_predates_host" in window, "the receipt is written without dating the record first"
    assert "_pre is True" in window, "an undateable record is being credited with an eviction"
    assert "_td[\"destroy\"]" in window, "the receipt is written outside the capacity-refusal teardown"


# ============================================================================================================
# ★★ SELF-COLLISION: WE KEPT RENTING A SECOND UNIT ONTO A MACHINE WE WERE ALREADY SITTING ON.
#
# Measured 2026-07-29, 9:25 -> 9:37 AM ET (run 30456795710, job 90592347882), VERBATIM from the collect board:
#
#     TVAST ...r1..._edge_reps instance=46191306 machine=28164 up=running committed=warmup/1024 ▲ ADVANCING
#     TVAST ...r2..._edge_reps instance=46197224 machine=28164 up=loading  committed=warmup/576
#         ⛔ DESTROYED this pass (capacity refusal on machine 28164; destroy: a qualifying replacement is on
#            the board)
#
# BOTH on machine 28164. The machine had room for one of our GPUs, not two, so the second rental was refused
# and torn down twelve minutes after it was bought — and 28164 kept winning selection because it was the
# cheapest thing on the board. The committed snapshot shows the same thing hours earlier:
# `ternary-vast-market-hold.json` @ 2026-07-29T13:01:41Z prices exactly ONE offer, machine 28164, in the same
# file whose `units_replacing_a_dead_host` names our own instance 46191306 on machine 28164.
#
# WHY NOTHING CAUGHT IT. `submit` spreads units one-per-machine, but only WITHIN one launch: `used` starts
# from `blocked_machine_ids()` and grows as that same call rents. `blocked_machine_ids()` has exactly one
# source, the `resources_unavailable` branch — so no path could exclude a machine merely for already
# carrying our own work, and a machine occupied on an EARLIER tick was invisible.
#
# THE FIX IS PREVENTION, NOT MEMORY: occupancy is recomputed from the live instance list every tick and
# never written down, so it cannot become the durable cross-lane blacklist trimcrae ruled against.
# ============================================================================================================
class _CapturingBackend:
    """Records the exclusion set each rental was given, then declines. Nothing is bought."""

    def __init__(self):
        self.seen = []

    def submit(self, job):
        from gpu_backend import NoQualifyingOffer
        self.seen.append(set(job.resources.exclude_machine_ids or ()))
        raise NoQualifyingOffer("captured, not rented")


def _submit_capturing(records, s3, live_hosts=None, occupied=(), blocked_machines=()):
    recs = {u: r for u, r in records.items() if r}
    jobs = {u: _Job(u) for u in records}
    hosts = {"live": live_hosts or {}, "dead": {}, "occupied_machines": set(occupied)}
    backend = _CapturingBackend()
    with _m.patch.object(_t, "_s3", return_value=s3), \
         _m.patch.object(_t, "leg_records", return_value=recs), \
         _m.patch.object(_t, "unit_hosts", return_value=hosts), \
         _m.patch.object(_t, "units_for", return_value=[(u, 0, "fwd") for u in records]), \
         _m.patch.object(_t, "build_jobspec", side_effect=lambda l, *a, **k: jobs[l]), \
         _m.patch.object(_t, "rented_rate_row", side_effect=lambda u, i: {"unit_id": u}), \
         _m.patch.object(_t, "blocked_machine_ids", return_value=list(blocked_machines)), \
         _m.patch.object(_t, "get_backend", return_value=backend), \
         _m.patch.dict(os.environ, {"VAST_API_KEY": "test-key"}):
        _t.submit("edge_reps")
    return backend.seen


def test_a_machine_we_already_occupy_is_never_offered_to_the_next_rental():
    # r1 live on 28164; r2 needs a host. The rental for r2 must be told to avoid 28164.
    records = {_R1: None, _R2: None}
    s3 = _FakeS3({_R1: {"attempts": 0}, _R2: {"attempts": 0}})
    seen = _submit_capturing(records, s3,
                             live_hosts={_R1: {"id": 46191306, "machine_id": 28164}},
                             occupied={"28164"})
    assert seen, "no rental was attempted, so the exclusion was never exercised"
    assert all("28164" in s for s in seen), \
        f"r2 was offered the machine r1 is already on — the 9:25 AM ET collision: {seen}"


def test_the_refusal_list_and_the_occupancy_list_are_both_applied():
    records = {_R1: None, _R2: None}
    s3 = _FakeS3({_R1: {"attempts": 0}, _R2: {"attempts": 0}})
    seen = _submit_capturing(records, s3, occupied={"28164"}, blocked_machines=["29711"])
    assert all({"28164", "29711"} <= s for s in seen)


def test_no_occupancy_means_no_extra_exclusion():
    # The fix must not quietly narrow the board when we hold nothing.
    records = {_R1: None}
    s3 = _FakeS3({_R1: {"attempts": 0}})
    seen = _submit_capturing(records, s3)
    assert seen == [set()]


def test_occupancy_counts_every_instance_we_hold_not_only_the_working_ones():
    # ⚠ `exited` on Vast is routinely transient — r1's own instance read `exited` at 13:01:41Z and `running`
    # by 13:05:24Z — and a `stopped` box can be restarted and reclaim its GPU. Keying occupancy on
    # `vast_instance_occupies_slot` would therefore re-open the collision every time a live host was observed
    # mid-flicker. A machine carrying an instance we have not destroyed is occupied.
    listing = {"instances": [
        {"id": 1, "machine_id": 28164, "label": "tvast-x", "actual_status": "exited",
         "cur_state": "running"},
        {"id": 2, "machine_id": 29711, "label": "tvast-y", "actual_status": "running",
         "cur_state": "running"},
    ]}
    with _m.patch.object(_t, "_vast_request", return_value=listing):
        h = _t.unit_hosts(["u_none"], key="k")
    assert h["occupied_machines"] == {"28164", "29711"}


def test_occupancy_spans_lanes():
    # The step 1 fan-out's boxes are on the same account and take the same GPUs. One API call already
    # returns them, so ignoring them would be a self-inflicted cross-lane collision.
    listing = {"instances": [
        {"id": 3, "machine_id": 46392, "label": "step1-fanout-edge-7", "actual_status": "running"},
    ]}
    with _m.patch.object(_t, "_vast_request", return_value=listing):
        h = _t.unit_hosts(["u_none"], key="k")
    assert h["occupied_machines"] == {"46392"}
    assert h["live"] == {} and h["dead"] == {}, "another lane's box must not be mistaken for one of ours"


def test_the_gate_does_not_price_a_machine_we_occupy():
    # The gate and the launcher must ask the SAME question, and the exclusion set is part of the question.
    # The 13:01:41Z snapshot quoted $0.052/hr on machine 28164 while our instance sat on machine 28164.
    out = {"needed": [_R2], "blocked": {}, "unblocked": {}, "done": [], "live": [_R1],
           "live_hosts": {}, "dead_hosts": {}, "occupied_machines": ["28164"],
           "listing_ok": True, "listing_error": None}
    seen = {}

    def _mg(n, key=None, excluded=(), max_ratio=None, mode=None):
        seen["excluded"] = set(excluded)
        return False, {"reason": "board is cheap", "hold": False}

    with _m.patch.object(_t, "outstanding_units", return_value=out), \
         _m.patch.object(_t, "market_gate", side_effect=_mg):
        action, r = _t.gate_for_mode("edge_reps", excluded=("29711",))
    assert action == "clear"
    assert seen["excluded"] == {"28164", "29711"}, \
        "the gate priced a machine the launcher could not have bought"
    assert r["machines_we_already_occupy"] == ["28164"], \
        "an exclusion that changes the quote must be visible in the snapshot"


def test_occupancy_never_becomes_a_blacklist_entry():
    # ⛔ trimcrae, 2026-07-27: a capacity refusal is PERISHABLE and must never become a durable cross-lane
    # exclusion. Occupancy is not a refusal record at all — it is recomputed from the live instance list
    # every tick — so it must never be written to `_blocked_machines` or published to the shared set.
    src = _launch_src()
    i = src.index('new_state["_blocked_machines"]')
    assert "occupied" not in src[i:src.index("\n", i)], \
        "occupancy is being persisted as a machine blacklist"
    j = src.index("vmb.publish(")
    assert "occupied" not in src[j:src.index(")", j)], "occupancy is being published to the shared blacklist"
    # and the launcher keeps the two sets separate rather than merging them into one reported list
    k = src.index("def submit(")
    body = src[k:k + 14000]
    assert "known to refuse starts" in body and "already occupies" in body, \
        "a self-collision must not be reported as a refusal, or vice versa"


# ── a lifetime count is not a failure streak (2026-07-30, 10:13 PM ET) ───────────────────────────────
# valB r2 committed production/1760 of 2000 at 02:05:13Z; its host aborted (rc=134) three seconds later.
# The breaker refused to re-rent at n_attempts=55 vs threshold 3, saying "55 separate rented hosts with no
# intervening success ... buying another host tests nothing". There HAD been intervening success — hours of
# it — and the 55 included the since-fixed partial-charge defect. `count_attempts` counted every attempt
# ever archived, so once a unit accumulated `threshold` attempts the breaker became a one-way latch.

import datetime as _dt


class _StubS3:
    """Minimal paginator stub — only what count_attempts touches."""

    def __init__(self, stamps):
        self._stamps = stamps

    def get_paginator(self, _op):
        outer = self

        class _P:
            def paginate(self, **kw):
                yield {"Contents": [{"Key": "a%d" % i, "LastModified": s}
                                    for i, s in enumerate(outer._stamps)]}
        return _P()


def _stamp(s):
    return _dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=_dt.timezone.utc)


def test_attempts_before_the_last_commit_are_not_part_of_the_streak():
    """The 2026-07-30 case: 55 lifetime attempts, all but one older than the newest commit."""
    stamps = [_stamp("2026-07-2%dT10:00:00Z" % (7 + i % 3)) for i in range(55)]
    stamps.append(_stamp("2026-07-30T02:05:20Z"))                     # the one after the commit
    s3 = _StubS3(stamps)
    assert lfb.count_attempts(s3, "b", "p", "u") == 56, "precondition: the lifetime count is large"
    streak = lfb.count_attempts(s3, "b", "p", "u", since_utc="2026-07-30T02:05:13Z")
    assert streak == 1, streak


def test_that_streak_no_longer_blocks_a_leg_that_was_88_percent_done():
    rec = {"status": "failed", "phase": None, "rc": 134}
    assert lfb.decide(rec, 56)["block"] is True, "precondition: the lifetime count blocked it"
    assert lfb.decide(rec, 1)["block"] is False, "the streak count must let the decisive retry happen"


def test_the_protection_still_fires_on_a_genuine_repeated_abort():
    """Three consecutive post-commit failures still block — the guard is re-based, not weakened."""
    stamps = [_stamp("2026-07-30T0%d:00:00Z" % h) for h in (3, 4, 5)]
    s3 = _StubS3(stamps)
    streak = lfb.count_attempts(s3, "b", "p", "u", since_utc="2026-07-30T02:05:13Z")
    assert streak == 3
    assert lfb.decide({"status": "failed", "phase": None, "rc": 134}, streak)["block"] is True


def test_no_commit_yet_keeps_the_original_lifetime_behaviour():
    """A unit that has never committed has no streak boundary; the two counts coincide."""
    stamps = [_stamp("2026-07-27T10:00:00Z"), _stamp("2026-07-27T11:00:00Z")]
    s3 = _StubS3(stamps)
    assert lfb.count_attempts(s3, "b", "p", "u", since_utc=None) == 2


def test_an_undateable_attempt_is_counted_rather_than_dropped():
    """Dropping it would shorten the streak — i.e. guess toward buying another host."""
    s3 = _StubS3([_stamp("2026-07-27T10:00:00Z")])

    class _S(_StubS3):
        def get_paginator(self, _op):
            class _P:
                def paginate(self, **kw):
                    yield {"Contents": [{"Key": "a", "LastModified": None}]}
            return _P()
    assert _S([]).__class__ is not None
    assert lfb.count_attempts(_S([]), "b", "p", "u", since_utc="2026-07-30T02:05:13Z") == 1
    assert lfb.count_attempts(s3, "b", "p", "u", since_utc="2026-07-30T02:05:13Z") == 0


def test_both_call_sites_pass_the_commit_cutoff():
    """The launcher gates on this number and the diagnostic explains it — they must read the same one."""
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    for f in ("ternary_vast_launch.py", "ternary_reps_diag.py"):
        src = open(os.path.join(here, "..", f)).read()
        assert "since_utc=_commit_utc" in src, (
            "%s still counts LIFETIME attempts — the breaker is a one-way latch again" % f)
