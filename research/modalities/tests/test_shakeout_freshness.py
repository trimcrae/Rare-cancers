"""A shakeout's evidence expires; a real result's never does — and a landed unit is not disarmed
while its host is still up.

WHAT THIS PINS, and why it is worth a file of its own. On 2026-07-31 `task=5aks-smoke` was dispatched to
shake out the 5a-KS pipeline before the four real legs were bought. It rented nothing and reported green,
because the smoke unit's `leg.json` had been `status=done` in S3 since 2026-07-26 — so `outstanding_units`
put it in `done`, the gate answered `nothing-to-launch`, and the ladder step that exists to catch a broken
image or a rotated credential measured nothing at all while printing `[verify-armed] … all 1 unit(s)
present and enabled`. The same morning NR-V04's pilot printed `[skip] … result already in S3`.

The two halves below have to hold TOGETHER. Expiring a shakeout's certificate without the watchdog guard
would turn a silent no-op into a silent UNWATCHED RENTAL: the entry is armed by the launch, and the very
next `reap_landed` pass would read the stale `done` record and set `enabled=false` under a billing host.
"""
import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ternary_vast_launch as tv  # noqa: E402
import ternary_vast_watchdog as tvw  # noqa: E402


def _stamp(hours_ago):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - hours_ago * 3600))


# ---------------------------------------------------------------------------------------------------------
# which modes are shakeouts at all
# ---------------------------------------------------------------------------------------------------------

def test_every_smoke_mode_is_flagged_a_shakeout():
    """A mode whose name says smoke but which is not flagged would keep the old, silent behaviour."""
    for mode in tv.MODES:
        if mode.endswith("smoke"):
            assert tv.is_shakeout(mode), f"{mode} looks like a shakeout but carries no shakeout flag"


def test_no_science_mode_is_a_shakeout():
    """The blast radius. If a production mode were ever flagged, this rule would expire a REAL result and
    the lane would re-buy landed work — the exact harm CLAUDE.md §7 records as costing a day."""
    for mode in ("probe", "edge", "edge_reps", "5aks", "triangle"):
        assert not tv.is_shakeout(mode), f"{mode} is a science mode and must never expire its result"


# ---------------------------------------------------------------------------------------------------------
# the shelf life itself
# ---------------------------------------------------------------------------------------------------------

def test_a_fresh_shakeout_record_is_not_stale():
    assert not tv.shakeout_evidence_is_stale({"_s3_last_modified": _stamp(0.5)})


def test_the_five_day_old_record_that_caused_this_is_stale():
    """The measured case: 2026-07-26 evidence standing in front of a 2026-07-31 spend."""
    assert tv.shakeout_evidence_is_stale({"_s3_last_modified": _stamp(24 * 5)})


def test_the_boundary_is_the_named_constant_and_not_a_second_copy_of_it():
    just_inside = tv.SHAKEOUT_EVIDENCE_MAX_AGE_H - 0.1
    just_outside = tv.SHAKEOUT_EVIDENCE_MAX_AGE_H + 0.1
    assert not tv.shakeout_evidence_is_stale({"_s3_last_modified": _stamp(just_inside)})
    assert tv.shakeout_evidence_is_stale({"_s3_last_modified": _stamp(just_outside)})


@pytest.mark.parametrize("rec", [{}, {"_s3_last_modified": None}, {"_s3_last_modified": "not-a-date"}])
def test_an_undatable_record_is_treated_as_stale(rec):
    """Cheap side, safe side: being wrong here re-runs a ~$0.15 shakeout, while being wrong the other way
    is the silent no-op this whole file is about."""
    assert tv.shakeout_evidence_is_stale(rec)


# ---------------------------------------------------------------------------------------------------------
# the watchdog half — the guard that makes the shelf life safe rather than dangerous
# ---------------------------------------------------------------------------------------------------------

def _watch_doc(uid):
    return {"watch": [{"unit_id": uid, "leg_id": "l", "seed": 0, "direction": "fwd", "mode": "5aks_smoke",
                       "timestep_fs": "4.0", "warmup_timestep_fs": "1.0", "git_branch": "main",
                       "max_relaunches_per_day": 8, "enabled": True}]}


def test_a_landed_unit_with_no_host_is_still_reaped(tmp_path, monkeypatch):
    """The ordinary path must keep working — this guard is a narrowing, not a disabling."""
    uid = "u1"
    p = tmp_path / "watch.json"
    tvw.save_watch(_watch_doc(uid), str(p))
    reaped = tvw.reap_landed(path=str(p), recs={uid: {"status": "done"}}, live_uids=set())
    assert reaped == [uid]
    assert tvw.load_watch(str(p))["watch"][0]["enabled"] is False


def test_a_landed_unit_whose_host_is_still_up_is_NOT_disarmed(tmp_path):
    """The regression that making a shakeout re-runnable would otherwise have introduced: an armed, billing
    host silently dropped off the only list the watchdog reads."""
    uid = "u1"
    p = tmp_path / "watch.json"
    tvw.save_watch(_watch_doc(uid), str(p))
    reaped = tvw.reap_landed(path=str(p), recs={uid: {"status": "done"}}, live_uids={uid})
    assert reaped == []
    assert tvw.load_watch(str(p))["watch"][0]["enabled"] is True


def test_an_unreadable_instance_list_reaps_nothing(tmp_path, monkeypatch):
    """No evidence is never a licence to act — same discipline as the unreadable leg-record branch."""
    uid = "u1"
    p = tmp_path / "watch.json"
    tvw.save_watch(_watch_doc(uid), str(p))

    def _boom(*a, **k):
        raise RuntimeError("vast api 503")

    monkeypatch.setattr(tvw.tv, "unit_hosts", _boom)
    reaped = tvw.reap_landed(path=str(p), recs={uid: {"status": "done"}})
    assert reaped == []
    assert tvw.load_watch(str(p))["watch"][0]["enabled"] is True


# ── WHICH STAMP DECIDES (measured 2026-08-01) ────────────────────────────────────────────────────────────
#
# ⚠ THE TEST GAP THAT LET THE BUG THROUGH IS THE POINT OF THIS BLOCK. Every case above sets ONLY
# `_s3_last_modified`, so all of them pass under either precedence — they could not tell a guard that reads
# the run's stamp from one that reads the storage layer's. The bug was invisible to a test suite that looked
# thorough, and it made the whole shakeout rung inert: `task=5aks-smoke` returned `nothing-to-launch`
# against a `leg.json` whose own content says 2026-07-26T21:07:19Z. Every case below sets BOTH.

def test_a_record_whose_CONTENT_is_old_is_stale_however_recently_the_object_was_touched():
    """★★ THE REGRESSION. `updated_utc` is written by the HOST when the leg finished — a property of the
    RUN. `_s3_last_modified` is a property of the OBJECT and moves for reasons that have nothing to do with
    the science: a re-upload, a copy, an archival sweep, a lifecycle transition. CLAUDE.md §4: a populated
    field is not a measured one."""
    assert tv.shakeout_evidence_is_stale(
        {"status": "done", "updated_utc": _stamp(24 * 6), "_s3_last_modified": _stamp(0.1)})


def test_a_genuinely_fresh_record_is_still_accepted():
    """The fix must not turn every shakeout into a re-rent — that would buy a host on every dispatch."""
    assert not tv.shakeout_evidence_is_stale(
        {"status": "done", "updated_utc": _stamp(0.5), "_s3_last_modified": _stamp(0.5)})


def test_a_fresh_run_whose_object_looks_old_is_ALSO_accepted():
    """The other direction of the same principle: an object that has not been touched since it was written
    says nothing about the run, so a recent run must not be expired by a stale-looking object."""
    assert not tv.shakeout_evidence_is_stale(
        {"status": "done", "updated_utc": _stamp(0.5), "_s3_last_modified": _stamp(24 * 6)})


def test_the_object_mtime_is_used_only_when_the_record_carries_no_stamp_of_its_own():
    """It remains a FALLBACK rather than being dropped: a record written before `updated_utc` existed still
    gets a usable answer instead of being force-expired on every tick."""
    assert not tv.shakeout_evidence_is_stale({"status": "done", "_s3_last_modified": _stamp(0.5)})
    assert tv.shakeout_evidence_is_stale({"status": "done", "_s3_last_modified": _stamp(24 * 6)})


def test_an_unparseable_content_stamp_falls_through_to_stale_not_to_the_object():
    """A corrupt `updated_utc` must not silently hand the decision to the field that caused the incident."""
    assert tv.shakeout_evidence_is_stale(
        {"status": "done", "updated_utc": "not-a-date", "_s3_last_modified": _stamp(0.1)})


def test_the_precedence_matches_the_one_the_rest_of_this_file_already_used():
    """`unit_row` had it right all along — `updated_utc or _s3_last_modified`. One fact, one home: the two
    readers of the same pair of fields must not disagree about which one means 'when did this run'."""
    src = open(tv.__file__).read()
    body = src[src.index("def shakeout_evidence_is_stale"):src.index("def outstanding_units")]
    assert 'record.get("updated_utc") or record.get("_s3_last_modified")' in body
    assert 'record.get("_s3_last_modified") or record.get("updated_utc")' not in body


def test_both_branches_print_both_stamps_so_a_SKIP_is_as_legible_as_an_EXPIRY():
    """A shakeout that skips is the dangerous outcome — it reads as a shakeout that passed. Until this was
    measured, the skip printed nothing at all and the expiry printed only the object mtime, i.e. only the
    field that was making the wrong call."""
    body = _fn_bodies()["done_units"]
    assert "content_updated_utc=" in body and "s3_object_mtime=" in body
    assert "SHAKEOUT certificate accepted as current" in body, "the skip branch must announce itself"
    assert body.count("{st}") >= 2, "both branches must print the same stamp pair"


# ── ONE DECIDER OF "ALREADY DONE" (measured 2026-08-01) ──────────────────────────────────────────────────
#
# ★★ THE SHAKEOUT RUNG STAYED INERT THROUGH ITS OWN FIX. The expiry was added to the gate's copy of the
# `done` set and not to `submit`'s, so the gate correctly decided the unit needed a host and `submit` then
# printed `[launch] skipping (already done, no rental)` and rented nothing. BOTH runs were green. This is
# the same drift `test_the_gate_and_the_launcher_share_ONE_breaker_call_site` exists to stop for the
# failure breaker, on the fact sitting immediately next to it.

def _launch_src():
    return open(tv.__file__).read()


def _fn_bodies():
    import ast
    src = _launch_src()
    return {n.name: ast.get_source_segment(src, n) or ""
            for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef)}


def test_the_gate_and_the_launcher_share_ONE_done_decision():
    b = _fn_bodies()
    for fn in ("outstanding_units", "submit"):
        assert "done_units(" in b[fn], f"{fn} decides 'already done' on its own again"


def test_only_NON_RENTING_readers_may_compute_a_done_set_of_their_own():
    """Not a count — a count is the brittle-proxy shape that turned a healthy build red an hour earlier in
    this same session. The property is about WHICH functions, and why each exception is legitimate:

      * `done_units`   — the one home; this IS the shared decision.
      * `collect`      — a read-only reporter. It builds a board, rents nothing, and must show a stale
                         shakeout as done because that is what is stored.
      * `retire_host`  — destroys a box whose leg finished. Applying the expiry here would INVERT it:
                         a shakeout whose certificate went stale would stop its host being retired, i.e.
                         keep paying for an idle box. Opposite direction, deliberately excluded.
    """
    import ast
    src = _launch_src()
    tree = ast.parse(src)
    fns = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    offenders = set()
    for n in ast.walk(tree):
        if not isinstance(n, (ast.SetComp, ast.DictComp)):
            continue
        seg = ast.get_source_segment(src, n) or ""
        if '"done"' not in seg or "status" not in seg:
            continue
        owner = next((f.name for f in fns if f.lineno < n.lineno <= (f.end_lineno or 0)), "<module>")
        offenders.add(owner)
    assert offenders <= {"done_units", "collect", "retire_host"}, (
        f"{sorted(offenders - {'done_units', 'collect', 'retire_host'})} computes its own done set. If it "
        "can cause or prevent a RENTAL it must call `done_units`; if it genuinely cannot, add it here with "
        "the reason, the way the three above are justified.")


def test_the_expiry_lives_in_the_shared_function_not_at_a_call_site():
    b = _fn_bodies()
    assert "shakeout_evidence_is_stale(" in b["done_units"]
    for fn in ("outstanding_units", "submit"):
        assert "shakeout_evidence_is_stale(" not in b[fn], \
            f"{fn} re-implements the expiry instead of inheriting it"


def test_a_science_mode_is_never_expired_by_the_shared_function():
    """The blast radius, checked on the shared path rather than on the old per-call-site one: expiring a
    REAL result would re-buy landed science."""
    recs = {"u1": {"status": "done", "updated_utc": _stamp(24 * 30)}}
    assert tv.done_units("5aks", records=recs, uids=["u1"]) == {"u1"}
    assert tv.done_units("5aks_smoke", records=recs, uids=["u1"]) == set()


def test_the_expiry_is_scoped_to_the_units_this_dispatch_is_about():
    """A stale record for some OTHER unit must not be silently dropped from the returned set — the caller
    uses it for reporting as well as for renting."""
    recs = {"mine": {"status": "done", "updated_utc": _stamp(24 * 30)},
            "theirs": {"status": "done", "updated_utc": _stamp(24 * 30)}}
    assert tv.done_units("5aks_smoke", records=recs, uids=["mine"]) == {"theirs"}
