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
    assert len(out["awaiting_authorization"]) == len(retro.enumerate_units()) == 18


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
    assert "retro_launch(bucket, authorize=False)" in src
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


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
