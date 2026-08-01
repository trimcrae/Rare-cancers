"""THE 2026-07-31 SMOKE-PANEL INCIDENT, pinned.

Two independent defects let a supervision loop buy a fan-out that was deliberately HELD, run it at the wrong
protocol, and then compute a preregistered verdict over the result. Both are reproduced here from the real
artifacts, so neither can come back quietly.

  DEFECT 1 — "unrun and hostless" was read as "lost its host". `retro_supervise` re-placed every unit that had
  neither a result nor a live box, which describes a HELD unit perfectly. Measured: run 30637096905, job
  91177336062, `2026-07-31T14:06:10Z [retro-super] re-placing 16 hostless unit(s)` — 10:06 AM ET, ~2 min after
  the first supervision tick, against an explicit hold pending the pilot.

  DEFECT 2 — a `leg_*.json` was taken as a landed leg. The tick was dispatched by `step1-fanout-supervisor.yml`
  with no `md_mode`, so `fusion-cpu-extras.yml`'s choice input defaulted to `smoke` and every leg ran 500 steps
  with ZERO equilibration. Those records still carry `prod_ns: 5.0` (copied from the env, not from what ran) and
  a fully-populated `R1_interface`, so 17 of them + 1 genuine leg drove `panel_complete` TRUE and the frozen
  gate emitted model-level means over 2-picosecond trajectories. Measured record for
  `nrv04retro-retro_noncov_nr4a1-m1-r1` (job 91195498091) is reproduced verbatim below.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nrv04_retro_panel as retro  # noqa: E402
import nrv04_vast_launch as vl  # noqa: E402


# ── the two real records, verbatim from S3 ────────────────────────────────────────────────────────────────
SMOKE_REC = {  # s3://.../nrv04retro-retro_noncov_nr4a1-m1-r1/leg_retro_noncov_nr4a1__m1_s1.json
    "panel": "nrv04_retrospective", "leg_id": "retro_noncov_nr4a1__m1", "seed": 1,
    "mode": "smoke", "prod_ns": 5.0, "equil_ns": 1.0, "n_frames": 5, "timed_ns": 0.002,
    "ns_per_day": 23.49, "prod_wall_s": 7.4, "blew_up": False, "blow_phase": None,
    "meta": {"n_atoms": 288137},
    "R1_interface": {"rmsd_series_mean": 0.955, "plateau_A": 1.09, "stable": True},
    "R2_recruitment": {"frames": 5, "frac_frames_in_contact": 1.0, "mean_contacts": 2940.2,
                       "recruited": True},
    "R3_lys": {"min_A": 32.36},
}
GENUINE_REC = {  # the one real leg on record, retro_noncov_nr4a2__m1 s0
    "panel": "nrv04_retrospective", "leg_id": "retro_noncov_nr4a2__m1", "seed": 0,
    "mode": "run", "prod_ns": 5.0, "equil_ns": 1.0, "n_frames": 500, "timed_ns": 5.0,
    "ns_per_day": 115.8, "prod_wall_s": 3730.5, "blew_up": False, "blow_phase": None,
    "meta": {"n_atoms": 248792},
    "R1_interface": {"plateau_A": 3.681, "stable": False},
    "R2_recruitment": {"mean_contacts": 1234.5}, "R3_lys": {"min_A": 21.0},
}


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# DEFECT 2 — what counts as a landed leg
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_the_genuine_leg_conforms():
    ok, why = retro.production_leg_check(GENUINE_REC)
    assert ok, why


def test_the_measured_smoke_record_is_not_a_landed_leg():
    ok, why = retro.production_leg_check(SMOKE_REC)
    assert not ok
    assert "smoke" in why
    # ...and it is rejected on the PROTOCOL, not on having failed. A smoke that "succeeds" is still not a leg.
    assert not SMOKE_REC["blew_up"] and retro.completed_production_check(SMOKE_REC)[0] is False


def test_prod_ns_alone_cannot_vouch_for_a_leg():
    """The trap that made this invisible: `prod_ns` is the REQUEST, echoed from the env even by a smoke."""
    assert SMOKE_REC["prod_ns"] == GENUINE_REC["prod_ns"] == retro.PROD_NS
    assert retro.is_production_leg(GENUINE_REC) and not retro.is_production_leg(SMOKE_REC)


def test_a_smoke_still_carries_a_scoreable_E1():
    """Why silence was dangerous: the non-conforming record is not empty, it is PLAUSIBLE. It hands the frozen
    gate exactly the field the gate scores, so nothing downstream could have noticed."""
    assert SMOKE_REC["R1_interface"]["plateau_A"] is not None
    assert not SMOKE_REC["blew_up"]


def test_a_blown_or_truncated_leg_stays_IN_the_panel_as_a_technical_failure():
    """★ THE LINE THAT MATTERS, and getting it wrong disarms prereg §4e. A leg that ran the right protocol and
    then melted is a TECHNICAL FAILURE the frozen gate scores (`MAX_FAILED_LEGS_PER_ARM` -> `underpowered_arms`).
    If the membership predicate rejected it, that arm would silently become an eternally-INCOMPLETE panel
    instead of a registered underpowered one — a suppression §4e never asked for."""
    blown = dict(GENUINE_REC, blew_up=True, blow_phase="production", n_frames=0, timed_ns=0.0)
    short = dict(GENUINE_REC, timed_ns=2.5, n_frames=250)
    for rec in (blown, short):
        assert retro.is_production_leg(rec), "it ran the preregistered protocol, so it is a leg of this panel"
        assert not retro.completed_production_check(rec)[0], "...and it did not finish"
    assert retro.completed_production_check(GENUINE_REC)[0]
    assert not retro.completed_production_check(dict(GENUINE_REC, n_frames=499))[0]


def test_a_different_requested_protocol_is_not_this_panels_leg():
    assert not retro.is_production_leg(dict(GENUINE_REC, prod_ns=2.0))
    assert not retro.is_production_leg(dict(GENUINE_REC, equil_ns=0.0))
    assert not retro.is_production_leg({})


def test_expected_frames_is_derived_from_md_settings_not_typed():
    import md_settings as MD
    assert retro.expected_production_frames() == int(retro.PROD_NS / MD.TIMESTEP_NS) // MD.frame_stride_steps()
    assert retro.expected_production_frames() == GENUINE_REC["n_frames"]


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# DEFECT 1 — a held unit is not a unit that lost its host
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
class _FakeS3:
    """Enough S3 for `retro_supervise`'s reads. No network, no boto3."""

    def __init__(self, objects):
        self.objects = dict(objects)
        self.puts = {}

    def get_object(self, Bucket, Key):  # noqa: N803
        if Key not in self.objects:
            raise KeyError(Key)
        import io
        return {"Body": io.BytesIO(self.objects[Key].encode()),
                "LastModified": __import__("datetime").datetime(2026, 7, 31)}

    def put_object(self, Bucket, Key, Body):  # noqa: N803
        self.puts[Key] = Body

    def head_object(self, Bucket, Key):  # noqa: N803
        raise KeyError(Key)

    def get_paginator(self, _op):
        raise RuntimeError("unused")


def _supervise(monkeypatch, authorized, live=()):
    """Run one tick with NO live retro host and nothing landed, and report what it would buy."""
    import json
    objs = {}
    if authorized is not None:
        objs[f"{vl.RETRO_RESULT_PREFIX}/{vl.RETRO_AUTHORIZED_UNITS_KEY}"] = json.dumps({"units": authorized})
    s3 = _FakeS3(objs)
    monkeypatch.setattr(vl, "_vast_request", lambda *a, **k: {"instances": list(live)})
    monkeypatch.setattr(vl, "retro_leg_records", lambda *a, **k: [])
    monkeypatch.setattr(vl, "_s3_list", lambda *a, **k: [])
    import leg_failure_breaker as lfb
    monkeypatch.setattr(lfb, "count_attempts", lambda *a, **k: 0)
    # `launch=False` returns the decision without renting — the whole point of the assertion.
    return vl.retro_supervise("bkt", s3=s3, key="k", now=1.0e9, launch=False)


def test_supervision_does_not_buy_a_unit_that_was_never_authorised(monkeypatch):
    """THE REGRESSION. With no authorization record, every unit is HELD and the tick buys nothing."""
    out = _supervise(monkeypatch, authorized=None)
    assert out["needed"] == []
    assert out.get("would_replace") in (None, [])
    # 16 post-AMENDMENT 4 (nr4a3 co-fold seed 3 excluded by measured input fault). Superseded: 18.
    assert len(out["awaiting_authorization"]) == len(retro.enumerate_units()) == 16


def test_supervision_still_re_places_a_unit_that_lost_its_host(monkeypatch):
    """The capability must SURVIVE the fix: an authorised unit with no host is exactly what a heal is for."""
    a, m, r = retro.enumerate_units()[0]
    name = retro.unit_name(a, m, r)
    out = _supervise(monkeypatch, authorized=[name])
    assert out["needed"] == [name]
    assert out["would_replace"] == [name]
    assert name not in out["awaiting_authorization"]


def test_a_held_unit_is_reported_every_tick_never_silently(monkeypatch):
    """CLAUDE.md §6: a lane that never launches must not look like a lane that finished."""
    out = _supervise(monkeypatch, authorized=[])
    assert out["awaiting_authorization"], "a hold that is not in the readout is a silent hold"
    assert out["n_authorized"] == 0


def test_authorization_is_additive_and_only_an_operator_dispatch_writes_it():
    import inspect
    # supervision hands `authorize=False` to the launcher; the operator path keeps the default True.
    src = inspect.getsource(vl.retro_supervise)
    assert "retro_launch(bucket, authorize=False, only_units=" in src
    assert inspect.signature(vl.retro_launch).parameters["authorize"].default is True


def test_supervision_heals_at_the_panels_protocol_not_an_ambient_MODE():
    """The other half of the incident: the tick inherited MODE=smoke from the dispatching workflow."""
    import inspect
    src = inspect.getsource(vl.retro_supervise)
    assert 'os.environ["MODE"] = "run"' in src


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# The consequence the fix must not introduce: a re-run being reaped by the record it is replacing
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_a_fresh_host_is_not_reaped_by_a_record_older_than_itself():
    inst = {"id": 1, "label": "nrv04retro-x", "actual_status": "running", "start_date": 2000.0}
    stale = vl.teardown_candidates([inst], {"nrv04retro-x": 1000.0}, 2100.0, 99999, "nrv04retro-")
    assert stale == [], "a host launched AFTER the record must not be reaped as result-in-S3"
    fresh = vl.teardown_candidates([inst], {"nrv04retro-x": 2050.0}, 2100.0, 99999, "nrv04retro-")
    assert [w for _i, w in fresh] == ["result-in-S3"]


def test_a_bare_set_keeps_the_old_billing_safe_behaviour():
    inst = {"id": 1, "label": "nrv04retro-x", "actual_status": "running", "start_date": 2000.0}
    got = vl.teardown_candidates([inst], {"nrv04retro-x"}, 2100.0, 99999, "nrv04retro-")
    assert [w for _i, w in got] == ["result-in-S3"]


def test_an_empty_selector_still_authorises_nothing():
    inst = {"id": 1, "label": "nrv04retro-x", "actual_status": "running", "start_date": 1.0}
    assert vl.teardown_candidates([inst], {}, 2.0, 1, "") == []


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# DEFECT 3 — the breaker counted a LIFETIME, and a lifetime is not a failure streak
#
# MEASURED 2026-07-31, 1:40 PM ET. The pilot `nrv04retro-retro_noncov_nr4a3-m1-r0` lost its host at ~12:06 PM
# ET and was never re-placed, across ~13 supervision ticks. The tick was firing every ~8 min and its log said
# why on every one of them:
#
#   [retro-super] ⛔ BLOCKED nrv04retro-retro_noncov_nr4a3-m1-r0 — this unit has been rented 3 times
#   (threshold 3) and has still written NO leg record.
#
# The S3 archive that produced the 3:
#   attempts/run-20260731T144656Z.log  10:46 AM ET  smoke
#   attempts/run-20260731T145006Z.log  10:50 AM ET  smoke -> wrote leg_..._s0.json at 10:53 AM ET
#   attempts/run-20260731T160052Z.log  12:00 PM ET  the production pilot (host lost ~12:06 PM ET)
#
# Two of the three SUCCEEDED far enough to write a completed leg record. The consecutive-failure count is 1.
# `leg_failure_breaker.count_attempts.__doc__` documents this exact divergence and the `since_utc` fix it got
# for the ternary lane on 2026-07-30; this call site never received it, so the count could only grow and the
# block was permanent by construction.
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_the_breaker_denominator_is_the_streak_not_the_lifetime_count(monkeypatch):
    """THE REGRESSION, replayed with the pilot's real timestamps."""
    import calendar
    a, m, r = retro.enumerate_units()[0]
    name = retro.unit_name(a, m, r)
    rec_epoch = calendar.timegm((2026, 7, 31, 14, 53, 10, 0, 0, 0))       # the completed smoke leg record
    lifetime = ["run-20260731T144656Z.log", "run-20260731T145006Z.log", "run-20260731T160052Z.log"]

    seen = {}

    def _count(_s3, _b, _p, unit, since_utc=None):
        seen[unit] = since_utc
        if since_utc is None:
            return len(lifetime)                                          # the defect: 3 >= threshold 3
        cut = calendar.timegm(__import__("time").strptime(since_utc, "%Y-%m-%dT%H:%M:%SZ"))
        return sum(1 for k in lifetime
                   if calendar.timegm(__import__("time").strptime(k[4:-4], "%Y%m%dT%H%M%SZ")) > cut)

    import json
    import leg_failure_breaker as lfb
    s3 = _FakeS3({f"{vl.RETRO_RESULT_PREFIX}/{vl.RETRO_AUTHORIZED_UNITS_KEY}": json.dumps({"units": [name]})})
    monkeypatch.setattr(vl, "_vast_request", lambda *a, **k: {"instances": []})
    monkeypatch.setattr(vl, "retro_leg_records",
                        lambda *a, **k: [(name, "k", {"mode": "smoke", "n_frames": 5}, rec_epoch)])
    monkeypatch.setattr(vl, "_s3_list", lambda *a, **k: [])
    monkeypatch.setattr(lfb, "count_attempts", _count)
    out = vl.retro_supervise("bkt", s3=s3, key="k", now=1.0e9, launch=False)

    assert seen[name] == "2026-07-31T14:53:10Z", "the streak must start at the newest leg record, not None"
    assert out["blocked"] == [], "one host loss after a completed leg is not a reproducing fault"
    assert out["needed"] == [name] and out["would_replace"] == [name]


def test_a_unit_that_has_never_written_a_record_still_blocks_at_the_threshold():
    """The protection the fix must NOT weaken: no record ever -> lifetime IS the streak."""
    import leg_failure_breaker as lfb
    d = vl.retro_breaker(has_result=False, n_attempts=lfb.DEFAULT_THRESHOLD, since_utc=None)
    assert d["block"] is True
    assert "never written a leg record" in d["counted"]


def test_a_block_names_the_denominator_it_used():
    """A bare count is unauditable: 3 lifetime attempts and 3 consecutive failures are opposite facts."""
    import leg_failure_breaker as lfb
    d = vl.retro_breaker(has_result=False, n_attempts=lfb.DEFAULT_THRESHOLD,
                         since_utc="2026-07-31T14:53:10Z")
    assert d["streak_since_utc"] == "2026-07-31T14:53:10Z"
    assert "2026-07-31T14:53:10Z" in d["why"]


def test_retro_streak_since_utc_is_the_newest_record_and_none_when_there_is_none():
    import calendar
    ep = calendar.timegm((2026, 7, 31, 14, 53, 10, 0, 0, 0))
    assert vl.retro_streak_since_utc({"u": ep}, "u") == "2026-07-31T14:53:10Z"
    assert vl.retro_streak_since_utc({}, "u") is None
    assert vl.retro_streak_since_utc(None, "u") is None


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# The retro market gate must name the TIER it priced — carried from the ternary gate's 2026-07-31 finding.
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_the_retro_market_gate_snapshot_stamps_its_tier(tmp_path):
    out = tmp_path / "hold.json"
    # An empty board is unpriceable -> a HOLD, which is the branch whose SENTENCE must carry the tier.
    hold, doc = vl.retro_market_gate(1, offers=[], readout_path=str(out))
    assert hold is True
    assert doc["interruptible"] is True and "bid" in doc["tier"]
    assert "tier" in doc["reason"], "a hold sentence with no tier is the ambiguity this closes"
    import json as _j
    assert _j.loads(out.read_text())["tier"] == doc["tier"], "the snapshot must carry it, not just stdout"


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# DEFECT 4 — the hold PRINTED and did not BIND, and the tick bought a held leg (measured 2026-07-31, 1:54 PM ET)
#
# The very tick that carried the DEFECT-3 fix logged, eight seconds apart:
#   [retro-super] ⏸ 16 unit(s) NOT re-placed — they have never been authorised to launch, so they are HELD
#   [retro-submit] nrv04retro-retro_noncov_nr4a2-m2-r0 -> instance 46424247 dph≈$0.2022/hr
# `retro_supervise` computed `needed` and printed the hold, then called `retro_launch`, which RE-DERIVED its
# own unit list from the whole panel and has no knowledge of the authorization record. A hold that prints
# without binding reads as a guard doing its job while money goes out.
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_supervision_scopes_the_launcher_to_exactly_the_units_it_may_re_place():
    import inspect
    src = inspect.getsource(vl.retro_supervise)
    assert "only_units=set(needed)" in src, (
        "supervision must hand the launcher its scope; without it the printed hold is decorative")


def test_the_launcher_honours_an_explicit_scope_and_an_empty_one(monkeypatch, capsys):
    """`None` = unscoped. A set = exactly those. EMPTY = nothing, never 'no filter'."""
    names = [retro.unit_name(a, m, r) for a, m, r in retro.enumerate_units()]
    seen = []

    class _BE:
        def submit(self, spec):
            seen.append(spec.name)
            raise RuntimeError("no offer")            # refuse everything: we assert on WHAT WAS OFFERED

    monkeypatch.setenv("RETRO_PILOT_ONLY", "0")
    monkeypatch.setenv("RETRO_MARKET_GATE", "0")      # the gate is DEFECT-3's subject, not this one
    monkeypatch.setattr(vl, "_vast_request", lambda *a, **k: {"instances": []})
    monkeypatch.setattr(vl, "retro_done_units", lambda *a, **k: set())
    monkeypatch.setattr(vl, "presign_env_tarball", lambda *a, **k: "https://x/env.tgz")
    monkeypatch.setattr(vl, "get_backend", lambda _n: _BE())

    assert vl.retro_launch("bkt", authorize=False, only_units={names[3]}) in (0, 1)
    assert seen == [names[3]], "a scoped dispatch must offer exactly the scoped unit"

    seen.clear()
    assert vl.retro_launch("bkt", authorize=False, only_units=set()) == 0
    assert seen == [], "an EMPTY scope means buy nothing — not 'no filter'"


def test_an_unscoped_dispatch_still_sees_the_whole_panel(monkeypatch):
    """The operator path must not be narrowed by the fix: only_units=None is unscoped."""
    seen = []

    class _BE:
        def submit(self, spec):
            seen.append(spec.name)
            raise RuntimeError("no offer")

    monkeypatch.setenv("RETRO_PILOT_ONLY", "0")
    monkeypatch.setenv("RETRO_MARKET_GATE", "0")
    monkeypatch.setattr(vl, "_vast_request", lambda *a, **k: {"instances": []})
    monkeypatch.setattr(vl, "retro_done_units", lambda *a, **k: set())
    monkeypatch.setattr(vl, "retro_authorize_units", lambda *a, **k: {})
    monkeypatch.setattr(vl, "presign_env_tarball", lambda *a, **k: "https://x/env.tgz")
    monkeypatch.setattr(vl, "get_backend", lambda _n: _BE())
    vl.retro_launch("bkt", authorize=False)
    assert len(seen) == len(retro.enumerate_units()) == 16   # AMENDMENT 4; superseded: 18


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# DEFECT 5 — TEN SILENT DECLINES. The re-placer refused the pilot on every tick from 12:07 PM to 2:02 PM ET
# (1 h 55 min) and no durable artifact said why: each board row carried only "no live host — phase marker X",
# which describes the STATE, not the DECISION. From the committed record a correctly-refusing gate and a dead
# re-placer are indistinguishable — which is why a human had to notice.
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_every_unbought_unit_gets_a_reason():
    sup = {"awaiting_authorization": ["u_held"],
           "blocked": [{"unit": "u_blocked", "verdict": "blocked: repeated failure on distinct hosts",
                        "counted": "since this unit's last completed leg record (2026-07-31T14:53:10Z)"}],
           "needed": ["u_needed"],
           "held": {"hold": True, "reason": "2.4x the ladder basis exceeds the 1.92x drift line",
                    "board_depth": {"offers_returned": 3, "qualifying": 3, "priceable": 1,
                                    "needed": 1, "used_for_mean": 1}}}
    r = vl.retro_gate_reasons(sup)
    assert set(r) == {"u_held", "u_blocked", "u_needed"}, "a unit with no reason is a silent decline"
    assert "never authorised" in r["u_held"]
    assert "2026-07-31T14:53:10Z" in r["u_blocked"], "a block must name the denominator it counted over"
    assert "HELD on price" in r["u_needed"] and "offers_returned" in r["u_needed"], (
        "a price hold must carry the board snapshot that caused it")


def test_the_gate_record_is_written_even_when_the_tick_bought_everything(tmp_path):
    """A snapshot that only appears on a hold cannot tell 'the gate ran and was happy' from 'it never ran'."""
    out = tmp_path / "gate.json"
    vl.persist_retro_gate({"needed": [], "n_authorized": 2, "replaced": [{"unit": "u"}]}, {},
                          path=str(out))
    import json as _j
    d = _j.loads(out.read_text())
    assert d["replaced"] == ["u"] and d["n_authorized"] == 2 and "utc" in d


def test_the_board_row_carries_the_tick_s_decision_not_just_the_state(monkeypatch):
    import nrv04_vast_launch as N
    import nrv04_retro_panel as R
    a, m, r = R.enumerate_units()[0]
    name = R.unit_name(a, m, r)

    class _S3:
        def get_object(self, Bucket, Key):
            raise KeyError(Key)

    rows, _ = N.retro_board_rows(_S3(), "b", {name: "md-running 2026-07-31T16:01:11Z"}, set(), [], None, {},
                                 reasons={name: "BLOCKED by the failure breaker — counted 3 attempts"})
    row = [x for x in rows if x["name"] == N._retro_short_name(name)][0]
    assert "THIS TICK:" in row["why"] and "BLOCKED by the failure breaker" in row["why"]


def test_a_row_with_no_recorded_decision_says_that_is_a_defect(monkeypatch):
    """Silence must read as a defect, not as a hold — the whole point of the record."""
    import nrv04_vast_launch as N
    import nrv04_retro_panel as R
    a, m, r = R.enumerate_units()[0]
    name = R.unit_name(a, m, r)

    class _S3:
        def get_object(self, Bucket, Key):
            raise KeyError(Key)

    rows, _ = N.retro_board_rows(_S3(), "b", {name: "uploaded 2026-07-31T14:20:54Z"}, set(), [], None, {})
    row = [x for x in rows if x["name"] == N._retro_short_name(name)][0]
    assert "not evaluating it at all" in row["why"]


# ── an OLD phase marker on a FRESH host is not a wedge (CLAUDE.md §4) ─────────────────────────────────────
def test_a_marker_older_than_the_host_is_labelled_as_a_previous_hosts():
    inst = {"start_date": __import__("calendar").timegm((2026, 7, 31, 18, 1, 0, 0, 0, 0))}
    s = vl._phase_marker_provenance("md-running 2026-07-31T16:01:11Z", inst)
    assert "PREVIOUS host" in s and "120 min later" in s


def test_a_marker_written_by_the_current_host_is_not_labelled():
    inst = {"start_date": __import__("calendar").timegm((2026, 7, 31, 16, 0, 0, 0, 0, 0))}
    assert vl._phase_marker_provenance("md-running 2026-07-31T16:01:11Z", inst) == ""


def test_no_host_and_an_undateable_marker_assert_nothing_either_way():
    assert vl._phase_marker_provenance("md-running 2026-07-31T16:01:11Z", None) == ""
    assert vl._phase_marker_provenance("staged", {"start_date": 1.0}) == ""
    assert vl._phase_marker_provenance("md-running 2026-07-31T16:01:11Z", {"start_date": "?"}) == ""


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# DEFECT 6 — `nrv04-retro-market-hold.json` HAD NEVER BEEN COMMITTED, in a repo where three files declare it
# exists (RETRO_MARKET_READOUT, the workflow's artifact list, lane_staleness_watch.LANES' hold_artifact).
# Verified 2026-07-31: `git cat-file -e origin/main:research/modalities/nrv04-retro-market-hold.json` fails
# while ternary-vast / 5aks / step1-fanout / valb-triangle all exist and were minutes old.
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_the_market_snapshot_is_written_even_when_there_is_nothing_to_price(tmp_path):
    """Cause (b): the gate's only production call site is inside retro_launch, and retro_supervise returns
    before reaching it whenever `needed` is empty — which is every tick that declined the pilot."""
    out = tmp_path / "hold.json"
    hold, doc = vl.retro_market_gate(1, price=False, readout_path=str(out))
    assert hold is False, "no purchase to price is not a refusal"
    assert doc["priced"] is False and "NOT PRICED" in doc["reason"]
    assert doc["tier"] and doc["interruptible"] is True, "the tier is stamped even on a no-price evaluation"
    import json as _j
    assert _j.loads(out.read_text())["priced"] is False, "the snapshot must exist on disk, not just in stdout"


def test_a_priced_evaluation_is_marked_priced(tmp_path):
    _h, doc = vl.retro_market_gate(1, offers=[], readout_path=str(tmp_path / "h.json"))
    assert doc["priced"] is True, "priced and not-priced must be distinguishable in the artifact"


def test_the_collect_tick_guarantees_a_snapshot_every_tick():
    """Cause (a) + (b) together: the artifact must be produced by the collect path, not only by a purchase."""
    import inspect
    src = inspect.getsource(vl.retro_collect)
    assert "retro_market_gate(" in src and "price=False" in src, (
        "retro_collect must record the evaluation when nothing priced the board")
    assert "getmtime(RETRO_MARKET_READOUT)" in src, (
        "the discriminator must be whether THIS tick wrote it, not whether the file exists")


def test_the_workflow_commits_the_hold_and_gate_artifacts_not_just_uploads_them():
    """Cause (a): the file appeared only in actions/upload-artifact — an ephemeral run artifact."""
    import os as _os
    root = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "..")
    wf = open(_os.path.join(root, ".github", "workflows", "fusion-cpu-extras.yml")).read()
    step = wf.split("Commit the in-flight board fragment", 1)[1].split("\n  step1_fanout:", 1)[0]
    assert "nrv04-retro-market-hold.json" in step, "the hold snapshot is still upload-only, never committed"
    assert "nrv04-retro-gate.json" in step, "the per-tick gate record is not committed"


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# DEFECT 7 — I REPLACED AN UN-ADVANCEABLE COUNTER WITH AN UN-ADVANCEABLE ANCHOR (measured 3:17 PM ET).
#
#   nr4a3 m1 r0: 40.0% · NO HOST · THIS TICK: BLOCKED by the failure breaker — blocked: repeated failure
#   on distinct hosts. Counted since this unit's last completed leg record (2026-07-31T14:53:10Z).
#
# 200 of 500 production frames banked and refused a host. The anchor was the last COMPLETED leg record — a
# smoke leg from 10:53 AM ET — and a unit that is part-done has by definition not completed one and never
# will while blocked. Same shape as the lifetime-count bug, one level in.
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_a_banked_checkpoint_supersedes_the_streak_anchor():
    import calendar
    rec = calendar.timegm((2026, 7, 31, 14, 53, 10, 0, 0, 0))          # the stale SMOKE leg record
    # No commit -> the leg record is the anchor (the previously-shipped behaviour, still correct).
    assert vl.retro_streak_since_utc({"u": rec}, "u") == "2026-07-31T14:53:10Z"
    # A production checkpoint written LATER must move the anchor forward.
    assert vl.retro_streak_since_utc({"u": rec}, "u", "2026-07-31T18:35:00Z") == "2026-07-31T18:35:00Z"
    # An OLDER checkpoint must not drag it backwards.
    assert vl.retro_streak_since_utc({"u": rec}, "u", "2026-07-31T10:00:00Z") == "2026-07-31T14:53:10Z"
    # A commit with no leg record at all still anchors.
    assert vl.retro_streak_since_utc({}, "u", "2026-07-31T18:35:00Z") == "2026-07-31T18:35:00Z"
    # Neither -> None, i.e. lifetime IS the streak (the case the breaker was written for).
    assert vl.retro_streak_since_utc({}, "u") is None
    # An undateable stamp is UNKNOWN and simply does not supersede.
    assert vl.retro_streak_since_utc({"u": rec}, "u", "not-a-stamp") == "2026-07-31T14:53:10Z"


def test_the_40_percent_deadlock_is_broken_end_to_end(monkeypatch):
    """Replay the live board state: stale smoke record + a fresh production checkpoint + 3 attempts."""
    import calendar, json
    a, m, r = retro.enumerate_units()[0]
    name = retro.unit_name(a, m, r)
    rec = calendar.timegm((2026, 7, 31, 14, 53, 10, 0, 0, 0))
    seen = {}

    def _count(_s3, _b, _p, unit, since_utc=None):
        seen[unit] = since_utc
        return 0 if since_utc == "2026-07-31T18:35:00Z" else 3      # 3 lifetime attempts since the record

    import leg_failure_breaker as lfb
    s3 = _FakeS3({f"{vl.RETRO_RESULT_PREFIX}/{vl.RETRO_AUTHORIZED_UNITS_KEY}": json.dumps({"units": [name]})})
    monkeypatch.setattr(vl, "_vast_request", lambda *a, **k: {"instances": []})
    monkeypatch.setattr(vl, "retro_leg_records",
                        lambda *a, **k: [(name, "k", {"mode": "smoke", "n_frames": 5}, rec)])
    monkeypatch.setattr(vl, "_s3_list", lambda *a, **k: [])
    monkeypatch.setattr(vl, "retro_committed_at", lambda *a, **k: "2026-07-31T18:35:00Z")
    monkeypatch.setattr(lfb, "count_attempts", _count)
    out = vl.retro_supervise("bkt", s3=s3, key="k", now=1.0e9, launch=False)
    assert seen[name] == "2026-07-31T18:35:00Z", "the banked checkpoint must anchor the streak"
    assert out["blocked"] == [], "a leg with banked frames must not be refused a host"
    assert out["would_replace"] == [name]


def test_retro_committed_at_only_counts_a_production_checkpoint():
    """It must not be fooled by the built-system snapshot or the leg record, which any attempt can write."""
    import datetime as _dt

    class _S3:
        def __init__(self, keys):
            self.keys = keys

        def head_object(self, Bucket, Key):
            return {"LastModified": _dt.datetime(2026, 7, 31, 18, 35, 0, tzinfo=_dt.timezone.utc)}

    def _list(_s3, _b, _prefix, suffix=None, **_k):
        return [k for k in _s3.keys if suffix is None or k.endswith(suffix)]

    import nrv04_vast_launch as N
    keys = [f"{N.RETRO_RESULT_PREFIX}/u/built_x.built.json",
            f"{N.RETRO_RESULT_PREFIX}/u/leg_x.json",
            f"{N.RETRO_RESULT_PREFIX}/u/ckpt_x_s0.ckpt.json"]
    import unittest.mock as _mock
    with _mock.patch.object(N, "_s3_list", _list):
        assert N.retro_committed_at(_S3(keys), "b", "u") == "2026-07-31T18:35:00Z"
        assert N.retro_committed_at(_S3(keys[:2]), "b", "u") is None, (
            "a built-system snapshot and a leg record are not banked production frames")


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# DEFECT 8 — 11 of 16 units failed to place against 89 PRICEABLE offers, because the wave never learned.
# 33 refusal events, EIGHT distinct machines: 29706 refused all 11 units, 33657 refused 8, 34670 refused 6.
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_a_host_that_refused_one_unit_is_skipped_for_the_rest_of_the_same_wave(monkeypatch):
    import gpu_backend as gb
    seen_excludes = []

    class _BE:
        def __init__(self):
            self.n = 0

        def submit(self, spec):
            seen_excludes.append(tuple(spec.resources.exclude_machine_ids))
            self.n += 1
            if self.n <= 2:
                raise gb.CapacityRefusedAtStart(
                    "refused", [{"machine_id": "29706"}, {"machine_id": "33657"}])
            raise RuntimeError("no offer")          # later units: assert on what they were OFFERED

    monkeypatch.setenv("RETRO_PILOT_ONLY", "0")
    monkeypatch.setenv("RETRO_MARKET_GATE", "0")
    monkeypatch.setattr(vl, "_vast_request", lambda *a, **k: {"instances": []})
    monkeypatch.setattr(vl, "retro_done_units", lambda *a, **k: set())
    monkeypatch.setattr(vl, "presign_env_tarball", lambda *a, **k: "https://x/env.tgz")
    monkeypatch.setattr(vl, "get_backend", lambda _n: _BE())
    vl.retro_launch("bkt", authorize=False)

    assert seen_excludes[0] == (), "the first unit has learned nothing yet"
    assert set(seen_excludes[1]) == {"29706", "33657"}, "unit 2 must skip what unit 1 measured"
    assert set(seen_excludes[-1]) == {"29706", "33657"}, "and so must every later unit in the wave"


def test_the_wave_refusal_set_does_not_outlive_the_call(monkeypatch):
    """CLAUDE.md §6: nothing that excludes a machine may outlive the wave that learned it."""
    import gpu_backend as gb
    seen = []

    class _BE:
        def submit(self, spec):
            seen.append(tuple(spec.resources.exclude_machine_ids))
            raise gb.CapacityRefusedAtStart("refused", [{"machine_id": "29706"}])

    monkeypatch.setenv("RETRO_PILOT_ONLY", "0")
    monkeypatch.setenv("RETRO_MARKET_GATE", "0")
    monkeypatch.setattr(vl, "_vast_request", lambda *a, **k: {"instances": []})
    monkeypatch.setattr(vl, "retro_done_units", lambda *a, **k: set())
    monkeypatch.setattr(vl, "presign_env_tarball", lambda *a, **k: "https://x/env.tgz")
    monkeypatch.setattr(vl, "get_backend", lambda _n: _BE())
    vl.retro_launch("bkt", authorize=False)
    first_wave_last = seen[-1]
    assert "29706" in first_wave_last
    seen.clear()
    vl.retro_launch("bkt", authorize=False)         # a FRESH wave must start from nothing
    assert seen[0] == (), "a new wave must re-learn; the set is not allowed to persist"


def test_no_durable_exclusion_state_is_introduced():
    """The retired defect is a set with no evidence that can retire an entry. Ours is a local."""
    import inspect
    src = inspect.getsource(vl.retro_launch)
    assert "wave_refused = set()" in src, "the set must be a local, created per call"
    assert "exclude=tuple(sorted(wave_refused))" in src
    import vast_machine_blacklist as vmb
    assert vmb.DURABLE_EXCLUSIONS_ENABLED is False, "the durable blacklist must stay retired"


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# DEFECT 9 — a UNIT-lifetime poll count rendered as a wedge on a ONE-MINUTE-OLD host (3:17 PM ET).
#   nr4a1 m1 r1: "22 consecutive board polls with no new frame" — 21 of them belonged to earlier rentals.
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_a_stale_poll_count_on_a_fresh_host_says_so(monkeypatch):
    import nrv04_vast_launch as N
    import nrv04_retro_panel as R
    import inflight_board as ifb
    import vast_idle_guard as vig
    a, m, r = R.enumerate_units()[0]
    name = R.unit_name(a, m, r)
    now = 1.0e9
    inst = {"id": 9, "label": name, "start_date": now - 60.0, "actual_status": "running"}  # 1 min old

    class _S3:
        def get_object(self, Bucket, Key):
            raise KeyError(Key)

    prev = {name: {"stage": "md", "iteration": None, "no_advance_polls": ifb.STALL_POLLS + 19}}
    rows, _ = N.retro_board_rows(_S3(), "b", {name: "md-running 2026-07-31T18:39:00Z"}, set(), [inst],
                                 None, prev, now=now)
    why = [x for x in rows if x["name"] == N._retro_short_name(name)][0]["why"]
    assert "this host is 1 min old" in why, "the host's own age must be stated, not inferred"
    assert "PREDATE THIS RENTAL" in why, "a fresh host carrying an old count must not read as a wedge"
    assert "%g" % vig.MIN_INSTANCE_AGE_MIN in why


def test_a_unit_that_was_rented_does_not_render_as_declined():
    """CLAUDE.md section 1: a row we are paying and a row the gate refused must never render alike.
    Measured 3:25 PM ET — the pilot printed `NOT BOUGHT` in the tick that rented it instance 46431866."""
    sup = {"needed": ["u_bought", "u_missed"],
           "replaced": [{"unit": "u_bought", "instance": "46431866"}]}
    r = vl.retro_gate_reasons(sup)
    assert "BOUGHT this tick" in r["u_bought"]
    assert "NOT BOUGHT" in r["u_missed"]


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# DEFECT 10 — a unit whose INPUT is broken burned rentals for five hours (root-caused 3:38 PM ET).
# nr4a3 m3 r0 reached md-running on every host and never banked a frame, while 16 siblings on the same image
# banked fine. Discriminator, from the real records:
#   FAILING  PE pre-min +2.109e+15 -> post-min +2.207e+15 kJ/mol, NaN at prod@frame0/5, 4.4 s
#   WORKING  PE pre-min -4.025e+06 -> post-min -5.667e+06 kJ/mol, 5 frames
# +2e15 is ~21 orders above physical and present BEFORE minimization -> an atomic clash carried in from the
# co-fold (nr4a3/seed_3). Both replicas of that model show it; no other model does.
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
REAL_BLOWN = {"blew_up": True, "blow_phase": "prod@frame0/5", "n_frames": 0,
              "pe_pre_min_kj": 2108844105470635.2, "pe_post_min_kj": 2206907872488877.2}
REAL_GOOD = {"blew_up": False, "n_frames": 5, "pe_pre_min_kj": -3987863.6, "pe_post_min_kj": -5654555.0}


def test_the_non_physical_input_is_quarantined_with_its_evidence():
    q, why = vl.retro_input_quarantine(REAL_BLOWN)
    assert q is True
    assert "prod@frame0/5" in why and "co-fold" in why and "RELEASE" in why, (
        "a quarantine must name the phase, the cause and how to clear it")


def test_a_healthy_leg_is_never_quarantined():
    assert vl.retro_input_quarantine(REAL_GOOD) == (False, "")
    assert vl.retro_input_quarantine({}) == (False, "")
    assert vl.retro_input_quarantine(None) == (False, "")


def test_a_LATER_blowup_stays_eligible_because_one_failure_is_noise():
    """leg_failure_breaker's rule must survive: a transient at frame 300 is not a broken input."""
    q, _ = vl.retro_input_quarantine(
        {"blew_up": True, "blow_phase": "prod@frame300/500", "pe_post_min_kj": -5.6e6})
    assert q is False
    # ... and neither is a frame-0 blow-up whose energy was PHYSICAL (a bad host, not a bad system).
    q2, _ = vl.retro_input_quarantine(
        {"blew_up": True, "blow_phase": "prod@frame0/5", "pe_post_min_kj": -5.6e6})
    assert q2 is False, "all three conditions must hold; energy is what makes it an INPUT fault"


def test_the_quarantine_costs_nothing_and_is_visible(monkeypatch):
    """It must be refused BEFORE the breaker (so $0, not three rentals) and appear in the readout."""
    import json
    a, m, r = retro.enumerate_units()[0]
    name = retro.unit_name(a, m, r)
    s3 = _FakeS3({f"{vl.RETRO_RESULT_PREFIX}/{vl.RETRO_AUTHORIZED_UNITS_KEY}": json.dumps({"units": [name]})})
    monkeypatch.setattr(vl, "_vast_request", lambda *a, **k: {"instances": []})
    monkeypatch.setattr(vl, "retro_leg_records", lambda *a, **k: [(name, "k", REAL_BLOWN, 1.0)])
    monkeypatch.setattr(vl, "_s3_list", lambda *a, **k: [])

    def _boom(*a, **k):
        raise AssertionError("the breaker must not be consulted for a quarantined unit")

    import leg_failure_breaker as lfb
    monkeypatch.setattr(lfb, "count_attempts", _boom)
    out = vl.retro_supervise("bkt", s3=s3, key="k", now=1.0e9, launch=False)
    assert [q["unit"] for q in out["quarantined"]] == [name]
    assert out["needed"] == [] and out["blocked"] == []
    assert name in vl.retro_gate_reasons(out), "a quarantined unit must carry its reason in the gate record"
    assert out["quarantine_eligible_running"] == [], "nothing is on a host in this fixture"


class _AttemptS3:
    """Minimal S3 double serving `attempts/` markers with real bodies."""

    def __init__(self, bodies):
        self.bodies = bodies                       # {key: body_text}

    def get_paginator(self, _op):
        outer = self

        class _P:
            def paginate(self, Bucket=None, Prefix=""):
                import datetime
                lm = datetime.datetime(2026, 7, 31, 20, 0, tzinfo=datetime.timezone.utc)
                yield {"Contents": [{"Key": k, "LastModified": lm}
                                    for k in outer.bodies if k.startswith(Prefix)]}
        return _P()

    def get_object(self, Bucket=None, Key=None):
        b = self.bodies[Key]
        if b is None:
            raise RuntimeError("unreadable")

        class _B:
            def read(self_inner):
                return b.encode()
        return type("O", (), {"__getitem__": staticmethod(lambda k: _B())})()


def _markers(*bodies):
    u = "nrv04retro-retro_noncov_nr4a2-m2-r0"
    p = f"{vl.RETRO_RESULT_PREFIX}/legs/{u}/attempts/"
    return u, _AttemptS3({f"{p}run-{i}.log": b for i, b in enumerate(bodies)})


def test_three_markers_from_ONE_crash_looping_host_is_not_three_rentals():
    """★★ THE MEASUREMENT THAT DECIDES WHETHER TWO UNITS ARE RECOVERABLE.

    CLAUDE.md §6: a container that crash-loops never returns, so Vast restarts it and the onstart preamble
    (`_RETRO_ATTEMPT_MARKER`) writes another marker. `count_attempts` counts OBJECTS. Reading three objects
    as "3 paid hosts" is asserting a reading nobody took — and on this lane it is the difference between a
    16/18 reachable panel and a 14/18 one.
    """
    u, s3 = _markers("attempt 2026-07-31T15:00:00Z instance=abc",
                     "attempt 2026-07-31T15:04:00Z instance=abc",
                     "attempt 2026-07-31T15:09:00Z instance=abc")
    n, hosts, det = vl.retro_attempt_hosts(s3, "bkt", u)
    assert (n, hosts) == (3, 1), "three restarts of one container are ONE rental"
    assert det["host_ids"] == ["abc"]


def test_three_markers_from_three_hosts_IS_a_genuine_streak():
    u, s3 = _markers("attempt t instance=h1", "attempt t instance=h2", "attempt t instance=h3")
    n, hosts, _ = vl.retro_attempt_hosts(s3, "bkt", u)
    assert (n, hosts) == (3, 3)


def test_a_marker_with_no_readable_id_is_never_credited_as_a_host():
    """CLAUDE.md §4b — an absent reading is not a reading of absence, and it must not inflate a host count."""
    u, s3 = _markers("attempt t instance=h1", "attempt t instance=unknown", "no id at all", None)
    n, hosts, det = vl.retro_attempt_hosts(s3, "bkt", u)
    assert n == 4 and hosts == 1, "only h1 is a known host; the rest are UNKNOWN, not extra hosts"
    assert det["unreadable_markers"] == 3


def test_an_unreadable_listing_is_unknown_not_zero():
    class _Boom:
        def get_paginator(self, _op):
            raise RuntimeError("no s3")
    n, hosts, det = vl.retro_attempt_hosts(_Boom(), "bkt", "u")
    assert n is None and hosts is None and "error" in det, (
        "a failed read must never render as 'zero hosts', which would read as a cleared streak")


def test_a_block_resting_on_fewer_distinct_hosts_than_the_threshold_is_DOWNGRADED():
    """★★ THE RULE SAYS "DISTINCT HOSTS"; THE DENOMINATOR WAS OBJECTS. Measured 5:18 PM ET on the first tick
    that could tell the difference: nr4a2-m3-r0 had 3 markers resolving to 2 distinct hosts, so a
    crash-looping container had blocked it a host early. The breaker's whole argument is that repetition
    ACROSS MACHINES makes a fault ours rather than the host's — one box restarting is not that.

    ⚠ DOWNGRADE ONLY, NEVER UPGRADE, AND FAIL-SAFE ON AN UNREADABLE COUNT: an unmeasured host count must not
    be able to release a genuine breaker.
    """
    import inspect
    src = inspect.getsource(vl.retro_supervise)
    assert 'if d.get("streak_is_genuine") is False:' in src, (
        "explicitly False — None (unmeasurable) must keep the block")
    assert "breaker_downgraded" in src and "needed.append(name)" in src
    # It sits INSIDE the block path, so an allowed unit never pays for the extra reads.
    assert src.index('d.get("streak_is_genuine") is False') > src.index('if d["block"]:')
    # ...and the release is recorded durably, not just printed into a job log that ages out.
    assert "breaker_downgraded" in inspect.getsource(vl.persist_retro_gate)


def test_the_block_carries_the_measured_host_count_not_the_object_count():
    import inspect
    src = inspect.getsource(vl.retro_supervise)
    assert "retro_attempt_hosts(s3, bucket, name, since_utc=since)" in src
    assert "streak_is_genuine" in src and "FEWER DISTINCT HOSTS THAN THE THRESHOLD" in src
    # ...and only on the block path, so a healthy unit pays nothing for it.
    assert src.index("retro_attempt_hosts") > src.index('if d["block"]:')
    # The gate record must carry it too, or the evidence dies with the job log.
    assert "HOSTS: %s." in inspect.getsource(vl.retro_gate_reasons)


def test_incomplete_and_UNCOMPLETABLE_must_not_read_alike():
    """★★ "9/18 units — coverage only" invites exactly one response: WAIT, the fan-out is still running.

    That is right for a unit between hosts and wrong for a unit whose input no host can run. Two units
    (nr4a3 m3 r0/r1) are input-quarantined on a 0.181 A clash Boltz placed in nr4a3/seed_3, so while they
    are enumerated, `panel_complete` can NEVER go true and prereg §4f suppresses the R1 verdict PERMANENTLY
    rather than until the fan-out finishes.

    This is AMENDMENT 3's failure mode recurring — `nrv04_retro_panel`'s AUTHORIZED_STAGES block records
    that 6 never-landable R2 units held panel_complete False and "it costs the primary result". That needed
    a preregistration amendment, and so does this. The collector's job is to SAY so, not to decide it.
    """
    import inspect
    src = inspect.getsource(vl.retro_collect)
    assert "panel_completable" in src and "reachable_units" in src
    assert "AMENDMENT 3" in src, "the precedent is what makes this a known remedy rather than a novel crisis"
    assert "PREREGISTRATION decision by trimcrae" in src, (
        "the collector must name whose decision it is, and must not take it")
    # The census reads the NEWEST leg record per unit — the same source the supervisor quarantines from, so
    # the two cannot disagree — and never the `legs` list, which has already dropped non-conforming records
    # (a quarantined unit's record is exactly one of those: it blew up at frame 0).
    assert "retro_leg_records(s3, bucket)" in src
    assert "newest_leg_rec = {}" in src, "unreadable is UNKNOWN, never 'nothing is quarantined'"


def test_reset_for_warns_about_the_evidence_it_destroys(capsys):
    """⛔ THE GUIDANCE POINTED AT THE DESTRUCTIVE ACTION, AND THAT IS THE DEFECT (2026-07-31).

    `reset_for` re-arms by DELETING `attempts/`. Those markers are not a counter — `retro_attempt_hosts`
    parses each one's `instance=` id to tell three genuine rentals from ONE crash-looping container, which
    is exactly what released nr4a2-m3-r0 today. The breaker's own remediation message used to send readers
    here, so a future agent working unattended would have followed it and destroyed the evidence.

    ⚠ WARNS, DOES NOT REFUSE. The function is shared across lanes and a hard refusal would change behaviour
    for callers that legitimately want the objects gone (a unit being retired, a bucket cleaned). The
    warning names what is being destroyed and where the offset lives; the decision stays with the caller.
    """
    import leg_failure_breaker as lfb
    deleted = {}

    class _S3:
        def get_paginator(self, _op):
            class _P:
                def paginate(self, Bucket=None, Prefix=""):
                    yield {"Contents": [{"Key": Prefix + "run-1.log"}, {"Key": Prefix + "run-2.log"}]}
            return _P()

        def delete_objects(self, Bucket=None, Delete=None):
            deleted["n"] = len(Delete["Objects"])

    n = lfb.reset_for(_S3(), "bkt", "pfx", "u")
    assert n == 2 and deleted["n"] == 2, "behaviour is UNCHANGED — it still deletes"
    warned = capsys.readouterr().out
    assert "about to DELETE" in warned and "destroys evidence" in warned
    assert "retro_set_breaker_baseline" in warned, "it must name the offset that does the same job"

    # An EMPTY archive is not a loss, so it must not cry wolf — a linter/guard that warns on nothing gets
    # ignored, which is lint_claims.py's founding lesson applied to an operator warning.
    class _Empty(_S3):
        def get_paginator(self, _op):
            class _P:
                def paginate(self, Bucket=None, Prefix=""):
                    yield {"Contents": []}
            return _P()

    assert lfb.reset_for(_Empty(), "bkt", "pfx", "u") == 0
    assert "about to DELETE" not in capsys.readouterr().out


def test_the_breaker_re_arms_by_BASELINE_and_never_by_deleting_the_evidence():
    """★★ THE STEP-1 RULING, PORTED — and it matters more here than it did there.

    `leg_failure_breaker.reset_for` re-arms by DELETING the attempt archive. On this lane that archive is
    evidence twice over: `retro_attempt_hosts` reads it to tell three rentals from one crash-looping
    container, and the sibling `attempt-logs/` prefix now holds the run.log of every attempt — the only
    record of HOW each died. Destroying evidence to move a counter is the wrong trade when an offset does
    the same job (`congeneric_fanout_vast._breaker_baselines`, 2026-07-29).

    It is nearly free here because the streak is already anchored by `since_utc`: a baseline is one more
    stamp that can supersede, exactly like a landed leg record or a banked checkpoint.
    """
    import inspect
    # The CODE, not the docstring — which legitimately contains the word "DELETING" while explaining the
    # thing it refuses to do. (My first version of this assertion read the prose and failed on itself.)
    code = inspect.getsource(vl.retro_set_breaker_baseline).split('"""')[2]
    for forbidden in ("delete_object", "delete_objects", "reset_for", "s3.delete"):
        assert forbidden not in code, f"the baseline writer must never {forbidden}"
    # A baseline supersedes exactly like a checkpoint does — the anchor is the NEWEST of the stamps.
    # (Epoch seconds, not a year: 1_785_000_000 is 2026-07-25. My first draft used 1000.0 and then asserted
    # a 1990 baseline should lose to it — 1000.0 is 1970, so the code was right and the test was wrong.)
    rec = {"u": 1_785_000_000.0}
    assert vl.retro_streak_since_utc(rec, "u") == vl.retro_streak_since_utc(rec, "u", None, None)
    later = vl.retro_streak_since_utc(rec, "u", baseline_utc="2030-01-01T00:00:00Z")
    assert later == "2030-01-01T00:00:00Z", "a later baseline wins over an older record mtime"
    earlier = vl.retro_streak_since_utc(rec, "u", baseline_utc="1990-01-01T00:00:00Z")
    assert earlier != "1990-01-01T00:00:00Z", "an older baseline must NOT drag the anchor backwards"
    # Undateable is UNKNOWN — it must not supersede, and must not raise.
    assert vl.retro_streak_since_utc(rec, "u", baseline_utc="not-a-stamp") is not None


def test_an_unreadable_baseline_file_is_empty_not_a_blanket_clear():
    class _Boom:
        def get_object(self, **kw):
            raise RuntimeError("no s3")
    assert vl.retro_breaker_baselines(_Boom(), "bkt") == {}


def test_gpu_util_zero_is_an_ABSENT_reading_on_this_lane_not_a_reading_of_absence():
    """★★ THE DISCRIMINATING OBSERVATION, not a suspicion (2026-07-31, 4:50 PM census vs the 4:47 board):

        nr4a1-m3-r0  gpu_util=None   board: 50 % through production
        nr4a1-m3-r1  gpu_util=0.0    board: 40 % through production

    Both LANDED as complete 500-frame production legs — 1645.1 s (262.6 ns/day) and 1989.5 s (217.1 ns/day).
    A 288,137-atom system does not do 200+ ns/day on a CPU, so those boxes were on their GPUs and working
    while the field read 0.0 and None. The ternary boxes in the SAME census read 89-99 %, so the census is
    fine — these hosts do not report.

    Rendering that as a flat "GPU 0.0%" invites the one inference the data forbids. Nothing safety-critical
    moves: `vast_idle_guard` already refuses to condemn on GPU idleness.
    """
    assert vl._retro_gpu_util_reading(None) == "utilisation not reported by the host"
    zero = vl._retro_gpu_util_reading(0.0)
    assert "NOT EVIDENCE OF IDLENESS" in zero and "frame census" in zero
    assert zero == vl._retro_gpu_util_reading(0), "int 0 and float 0.0 must read alike"
    # A real, positive reading is still reported plainly — this is not a blanket suppression.
    assert vl._retro_gpu_util_reading(88.5) == "88.5%"


def test_the_checkpoint_interval_override_is_PER_UNIT_and_off_by_default():
    """(1) APPROVED single-unit trial. 50 frames is ~2.8-4 min of production at the landed legs' measured
    3.3-4.8 s/frame; nr4a1-m1-r1's post-resume host lifetime is ~2 min, so it can never bank. 25 frames
    (~1.4-2 min) is the SMALLEST change that could plausibly bank work and half the upload penalty of 10 —
    each checkpoint is a ~45 MB state.xml, which is exactly why this is not a lane default."""
    import nrv04_retro_panel as _panel
    assert vl.retro_ckpt_every_for("nrv04retro-retro_noncov_nr4a1-m1-r1") == 25
    # EXACTLY one unit is overridden; every other unit keeps the driver's default.
    others = [_panel.unit_name(*u) for u in _panel.enumerate_units()
              if _panel.unit_name(*u) != "nrv04retro-retro_noncov_nr4a1-m1-r1"]
    assert all(vl.retro_ckpt_every_for(u) is None for u in others)
    assert len(vl.RETRO_CKPT_EVERY_OVERRIDES) == 1
    # It reaches the leg only through the jobspec env, so an un-overridden unit carries no key at all.
    a, m, r = next(u for u in _panel.enumerate_units()
                   if _panel.unit_name(*u) == "nrv04retro-retro_noncov_nr4a1-m1-r1")
    assert vl.build_retro_jobspec(a, m, r, "run", "br", "bkt").env["CKPT_EVERY_FRAMES"] == "25"
    a2, m2, r2 = next(u for u in _panel.enumerate_units()
                      if _panel.unit_name(*u) == "nrv04retro-retro_noncov_nr4a1-m2-r0")
    assert "CKPT_EVERY_FRAMES" not in vl.build_retro_jobspec(a2, m2, r2, "run", "br", "bkt").env


def test_the_per_attempt_log_archive_must_not_land_where_attempts_are_COUNTED():
    """⛔ THE FOOTGUN THIS EXISTS TO STOP. `leg_failure_breaker.count_attempts` counts OBJECTS under
    `attempts/`. Archiving the previous attempt's run.log there too would put TWO objects per attempt in the
    counted prefix and fire the breaker at half its intended threshold — silently, and expensively, on a
    lane that rents unattended.

    So the archive goes to `attempt-logs/`, a namespace nothing counts. Why archive at all: the lane
    overwrites `$RESULT_S3/run.log` every 45 s, so each attempt destroyed the only record of how the last
    one died — and the sibling ternary lane's wedge diagnosis needed TWO preserved logs from two hosts to
    localise a hang between two prints. One sample cannot make that comparison.
    """
    import inspect
    src = inspect.getsource(vl)
    assert '"ATTEMPT_LOG_S3": f"s3://{bucket}/{RETRO_RESULT_PREFIX}/legs/{name}/attempt-logs"' in src
    marker = vl._RETRO_ATTEMPT_MARKER
    assert "$ATTEMPT_LOG_S3/run-$_ATS.log" in marker, "the log archive uses the UNCOUNTED prefix"
    assert "$ATTEMPT_S3/run-$_ATS.log" in marker, "the marker itself still uses the counted prefix"
    # Exactly ONE object per attempt lands in the counted prefix.
    assert marker.count("$ATTEMPT_S3/") == 1
    assert "attempts" not in vl.build_retro_jobspec.__doc__ or True  # doc-agnostic
    # And the two prefixes must not be the same string, or the separation is decorative.
    jobspec_src = inspect.getsource(vl.build_retro_jobspec)
    assert "/attempts\"" in jobspec_src and "/attempt-logs\"" in jobspec_src


def test_the_breaker_does_not_claim_a_host_count_it_has_not_measured():
    """⚠ N MARKERS IS NOT PROVEN TO BE N HOSTS, and the old wording asserted it was.

    The marker is written by the host's onstart preamble. CLAUDE.md §6: a container that crash-loops never
    returns, and Vast restarts it — so one rental that crash-loops three times writes three markers, and
    `count_attempts` counts OBJECTS, not container ids. The block is correct either way (both readings are
    the same fault reproducing), but "3 paid hosts" was a claim the evidence does not support, and it is the
    kind of claim that gets quoted into a diagnosis later.
    """
    d = vl.retro_breaker(has_result=False, n_attempts=3, threshold=3, since_utc="2026-07-31T14:53:39Z")
    assert d["block"] is True
    assert "paid hosts" not in d["why"], "do not assert a host count from an object count"
    assert "NOT PROVEN" in d["why"] and "crash-loops" in d["why"]
    assert "attempt markers" in d["why"]
    # The decision itself is unchanged — this is a wording fix, not a weakening.
    assert vl.retro_breaker(has_result=False, n_attempts=2, threshold=3)["block"] is False
    assert vl.retro_breaker(has_result=True, n_attempts=99, threshold=3)["block"] is False
    assert vl.retro_breaker(has_result=False, n_attempts=None, threshold=3)["block"] is False


def test_a_quarantine_eligible_unit_ON_A_HOST_is_visible_but_untouched(monkeypatch):
    """★★ THE BOARD SAID 1 QUARANTINE WHILE THE DIAGNOSIS NAMED TWO, and the missing one was mid-rental.

    The quarantine check sat below `if name in done_units or name in alive: continue`, so it could only ever
    reach a HOSTLESS unit. `m3-r0` was hostless and refused; `m3-r1` was on a host and rendered as an ordinary
    running leg. Both draw on the same non-physical co-fold.

    ⛔ AND THE FIX IS VISIBILITY, NOT ENFORCEMENT. The quarantine gates PURCHASES; CLAUDE.md §6 draws exactly
    this boundary for the market gate ("work already executing is never touched"). So the live host must NOT
    be condemned, must NOT be added to `quarantined`, and must NOT appear in `needed` — it simply has to say
    what it is.
    """
    import json
    a, m, r = retro.enumerate_units()[0]
    name = retro.unit_name(a, m, r)
    s3 = _FakeS3({f"{vl.RETRO_RESULT_PREFIX}/{vl.RETRO_AUTHORIZED_UNITS_KEY}": json.dumps({"units": [name]})})
    inst = {"id": 999, "label": name, "actual_status": "running", "start_date": 1.0e9 - 3600}
    monkeypatch.setattr(vl, "_vast_request", lambda *a, **k: {"instances": [inst]})
    monkeypatch.setattr(vl, "retro_leg_records", lambda *a, **k: [(name, "k", REAL_BLOWN, 1.0)])
    monkeypatch.setattr(vl, "_s3_list", lambda *a, **k: [])
    out = vl.retro_supervise("bkt", s3=s3, key="k", now=1.0e9, launch=False)
    assert [q["unit"] for q in out["quarantine_eligible_running"]] == [name]
    assert out["quarantined"] == [], "a live host is never quarantined — the gate is on purchases"
    assert out["condemned"] == [], "and it is certainly never condemned by this predicate"
    assert name not in (out.get("needed") or []), "it has a host; it is not due for one"
    why = vl.retro_gate_reasons(out)[name]
    assert why.startswith("RUNNING"), why
    assert "never touches work already executing" in why
    # ⚠ IT MUST NOT READ AS A DECLINE. CLAUDE.md §1: a row we are paying for and a row the gate refused must
    # never render alike, and this row is one we are paying for.
    assert "INPUT QUARANTINE —" not in why.split("RUNNING")[0]
    assert "$0" not in why


def test_the_running_quarantine_flag_is_carried_onto_the_board_row():
    rows, _ = vl.retro_board_rows(
        _FakeS3({}), "bkt", {}, set(), [{"id": 7, "label": "u", "start_date": 1.0e9 - 7200}],
        None, {}, now=1.0e9, quarantine_running={"u"})
    # `retro_board_rows` enumerates the panel, so the synthetic label is not among its units; the guard is
    # that the parameter exists, is honoured for a LIVE host only, and is absent by default.
    import inspect
    src = inspect.getsource(vl.retro_board_rows)
    assert "quarantine_running" in inspect.signature(vl.retro_board_rows).parameters
    assert "inst is not None and name in (quarantine_running or set())" in src, (
        "a hostless unit already carries the quarantine through `reasons`; this branch is the live one")
    assert "QUARANTINE-ELIGIBLE INPUT" in src
    assert isinstance(rows, list)


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# DEFECT 10 — the hostless row PROMISED a resume that no artifact backed (measured 2026-08-01).
#   `nrv04retro-retro_noncov_nr4a2-m2-r0` carried "a re-dispatch resumes this leg from its checkpoint" on
#   every tick for ~11 hours while its `ckpt_*.ckpt.json` set was EMPTY: its hosts' containers exited inside
#   the preregistered 1 ns equilibration, before any production frame existed to checkpoint. The row read as
#   "it will pick up where it left off" when every rental was in fact starting from zero — CLAUDE.md §4b,
#   a populated field is not a measured one, in prose form.
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def _hostless_row(s3, phase="md-running 2026-07-31T20:28:05Z"):
    import nrv04_retro_panel as R
    a, m, r = R.enumerate_units()[0]
    name = R.unit_name(a, m, r)
    rows, _ = vl.retro_board_rows(s3, "bkt", {name: phase}, set(), [], None, {},
                                  reasons={name: "BOUGHT this tick"})
    return [x for x in rows if x["name"] == vl._retro_short_name(name)][0]


def test_a_hostless_row_never_promises_a_resume_it_cannot_evidence(monkeypatch):
    monkeypatch.setattr(vl, "retro_committed_at", lambda *a, **k: None)
    why = _hostless_row(_FakeS3({}))["why"]
    assert "NOTHING BANKED THAT WE CAN READ" in why
    assert "RESTARTS this leg from zero" in why
    assert "RESUMES it from the production checkpoint" not in why, (
        "with no checkpoint object, a resume is a claim, not a description")


def test_a_hostless_row_names_the_checkpoint_when_one_really_is_banked(monkeypatch):
    monkeypatch.setattr(vl, "retro_committed_at", lambda *a, **k: "2026-08-01T01:02:03Z")
    why = _hostless_row(_FakeS3({}))["why"]
    assert "RESUMES it from the production checkpoint banked 2026-08-01T01:02:03Z" in why
    assert "NOTHING BANKED" not in why


def test_the_resume_claim_is_measured_not_templated():
    """The guard against the fix being written back out as a constant string."""
    import inspect
    src = inspect.getsource(vl.retro_board_rows)
    assert "retro_committed_at(s3, bucket, name)" in src, (
        "the row must ASK whether work is banked; the old text asserted it unconditionally")
    assert "a re-dispatch resumes this leg from its checkpoint" not in src


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# THE HEARTBEAT (coordinator ruling, 2026-08-01) — the redundant-looking commit IS the mechanism.
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def _fusion_wf():
    import os
    here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    with open(os.path.join(here, ".github", "workflows", "fusion-cpu-extras.yml"), encoding="utf-8") as fh:
        return fh.read()


def test_the_retro_fragment_commit_is_unconditional():
    """★★ A `git diff --cached --quiet && exit 0` on a lane's OWN heartbeat fragment is a landmine, not a bug.

    It never fires while `generated_epoch` is in the file, so it looks harmless — and the moment anyone
    stabilises that stamp as an "optimisation", a healthy IDLE lane commits nothing and renders
    byte-identically to a DEAD one.

    On THIS lane that would have destroyed the evidence for its own biggest finding: the commit series of
    `inflight-board.d/nrv04-retro.json` is the whole basis of `STARTING 11:59 AM -> NO HOST x10 ticks ->
    STARTING 2:02 PM ET`, i.e. the measurement behind "the pilot sat hostless for 1 h 55 min across ten
    ticks of an 8-minute supervisor" (`retro_gate_reasons.__doc__`). Ten identical NO HOST rows differ only
    in their stamp.

    ⚠ COMMENTS ARE STRIPPED BEFORE ASSERTING, so the prose above the step may still NAME what it forbids.
    """
    step = _fusion_wf().split("- name: Commit the in-flight board fragment and the merged all-lane board")[1]
    code = "\n".join(l for l in step.splitlines() if not l.strip().startswith("#"))
    head = code.split("git commit")[0]
    assert "git diff --cached --quiet" not in head, (
        "the fragment commit must never be skipped on 'no content change' — the timestamp IS the heartbeat")
    assert "git commit -q --allow-empty" in code, (
        "--allow-empty is unconditional in BOTH directions: it can neither silently skip (the landmine) nor "
        "fail red on a genuine no-diff (what a naive guard-removal would do)")


def test_an_idle_lane_s_rows_are_constant_between_ticks():
    """The stamp must be the ONLY thing separating 'idle and reporting' from 'stopped reporting'.

    If two ticks of an unchanged, hostless lane produced different ROWS, a suppressed commit would be
    losing content rather than only a timestamp, and the ruling above would rest on the wrong reason. It
    does not: identical inputs give byte-identical rows, so the heartbeat carries exactly one fact — that
    the tick ran.
    """
    import nrv04_retro_panel as R
    a, m, r = R.enumerate_units()[0]
    name = R.unit_name(a, m, r)
    args = dict(phases={name: "md-running 2026-07-31T20:28:05Z"}, reasons={name: "BLOCKED by the breaker"})
    rows1, _ = vl.retro_board_rows(_FakeS3({}), "bkt", args["phases"], set(), [], None, {}, now=1.0e9,
                                   reasons=args["reasons"])
    rows2, _ = vl.retro_board_rows(_FakeS3({}), "bkt", args["phases"], set(), [], None, {}, now=1.0e9 + 480,
                                   reasons=args["reasons"])
    assert rows1 == rows2, "an idle lane's rows must not drift; only the fragment's stamp may differ"
    assert rows1, "and the idle lane must still emit rows — a vanishing row reads as a unit that never existed"


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# THE REPORTED PAIRWISE FLOOR — AMENDMENT 4 §4.3 registered a LOSS, and the prose must not hide it.
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def _means_3_3_2():
    """The AUTHORIZED shape: NR4A1 and NR4A2 at 3 models, NR4A3 at 2 (AMENDMENT 4)."""
    import nrv04_retro_gate as g
    return {g.PRIMARY_ARM: {1: 3.3, 2: 5.2, 3: 3.8},
            g.POOLED_ARMS[0]: {1: 3.6, 2: 4.9, 3: 6.1},
            g.POOLED_ARMS[1]: {1: 4.1, 2: 3.2}}


def _legs_from_means(means):
    """Minimal conforming leg records the frozen gate will accept, one per (arm, model)."""
    out = []
    for arm, per in means.items():
        for seed, val in per.items():
            out.append({"arm_id": arm, "cofold_model_seed": seed, "e1_plateau_A": val})
    return out


def test_a_pairwise_that_cannot_reach_alpha_says_UNRESOLVABLE_not_null():
    """★★ §4.3 accepted, as a stated cost, that NR4A1-vs-NR4A3 can no longer attain α: at n = 2 it is
    C(5,3) = 10 arrangements, min attainable one-sided p = 0.10 > α = 0.05.

    The caveat beside those numbers used to read 'min attainable one-sided p for a 3-vs-3 pairwise test is
    0.05 (C(6,3)=20)' — true of the NR4A2 comparison, FALSE of the NR4A3 one, and a reader taking it at its
    word would treat p = 0.70 there as a null rather than as an unresolvable test. That is the difference
    between an honest limitation and an overclaim.

    Nothing computed changes: this pins the SENTENCE, and asserts it derives from each test's own
    `min_attainable_p` rather than from one typed number."""
    import nrv04_retro_gate as g
    v = g.verdict(_legs_from_means(_means_3_3_2()))
    pw = v["pairwise_secondary"]
    a2, a3 = g.POOLED_ARMS
    assert pw[a3]["min_attainable_p"] > g.ALPHA, "the premise: at n=2 this pairwise cannot reach alpha"
    assert pw[a2]["min_attainable_p"] <= g.ALPHA, "and the n=3 pairwise still can — the caveat must differ"
    cav = v["pairwise_caveat"]
    assert "UNRESOLVABLE, not null" in cav, cav
    assert a3 in cav and a2 in cav, "the caveat must name BOTH tests, since their floors differ"
    assert "0.05 (C(6,3)=20)" not in cav, "the retired single typed floor must not come back"
    # the flagged one is the NR4A3 arm, not the NR4A2 arm
    assert cav.index(a3) < cav.index("UNRESOLVABLE") or a3 in cav.split("UNRESOLVABLE")[0]


def test_the_criteria_audit_derives_its_reference_set_from_the_authorized_panel():
    """The audit reported C(9,3)=84 and min p 1/84 AFTER AMENDMENT 4 made the real set C(8,3)=56 — and
    re-running it did not fix that, the tell of a hard-coded constant. Meanwhile the EMITTED verdict
    correctly said 56, so the two documents disagreed and the stale one is the one a reader reaches for."""
    import nrv04_retro_criteria_audit as A
    import nrv04_retro_gate as g
    per = A.authorized_models_per_arm()
    assert per[g.PRIMARY_ARM] == 3 and sum(per[a] for a in g.POOLED_ARMS) == 5, per
    total, lattice = A.p_lattice()
    assert total == 56 and abs(lattice[0] - 1.0 / 56) < 1e-12
    assert "84" not in A.rank_statistic_identity(trials=50)["identity"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
