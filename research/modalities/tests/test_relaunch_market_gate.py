#!/usr/bin/env python3
"""Tests for the $/ns gate on a SINGLE-HOST rental — a relaunch, a resume, or a cold unit.

WHAT THESE PIN, and why each one is a regression rather than a feature:

  1. **A relaunch at a bad `$/ns` is HELD.** This is the defect the gate was written for: CLAUDE.md §6's
     first cut exempted "a single unit already running", so overnight spot churn re-rented the same two lanes
     again and again, each time a fresh purchase, each time unpriced — at 1.76x and 1.51x the ladder basis
     with `⚠ DRIFT` printed on the board — while a fan-out at 2.05x was correctly refused.
  2. **A relaunch at a good `$/ns` is ALLOWED.** A gate that never clears is a ceiling nobody can clear, which
     §6 names as one of the two failure modes worse than the problem.
  3. **A RUNNING leg is never disturbed.** The gate applies at the moment of RENTING. Killing a live host to
     save $/ns would discard paid-for work to avoid paying for work.
  4. **A hold is VISIBLE.** The other failure mode §6 names: a silent hold is indistinguishable from a
     finished unit. Every pass writes the snapshot that caused it.
  5. **The ceiling is IMPORTED, not typed.** The drift line has one home; three copies of 1.5 is the rule-1
     bug this repo already paid for.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import congeneric_fanout as cf  # noqa: E402
import gpu_backend as gb  # noqa: E402
import inflight_usd_per_ns as iu  # noqa: E402
import relaunch_market_gate as rmg  # noqa: E402
import vast_machine_blacklist as vmb  # noqa: E402
import vast_watchdog as vw  # noqa: E402

RES = gb.ResourceSpec(gpu="rtx4090", min_vram_gb=24, vcpus=8, ram_gb=32, disk_gb=80, interruptible=True)


def _offer(machine_id, min_bid, gpu="RTX 4090"):
    """An offer shaped the way `rank_offers_by_usd_per_ns` reads one. Deliberately built for the REAL filter
    rather than for a stub: a test that priced offers a launcher would reject would prove nothing."""
    return {"machine_id": machine_id, "min_bid": min_bid, "dph_total": min_bid, "dph_base": min_bid,
            "gpu_name": gpu, "num_gpus": 1, "rentable": True, "gpu_ram": 24576, "cuda_max_good": 13.0,
            "reliability2": 0.99, "cpu_cores_effective": 16, "cpu_ram": 64000, "disk_space": 200,
            "storage_cost": 0.1, "inet_down": 1000, "inet_up": 1000}


def _usd_h_at_ratio(ratio):
    """The $/hr that lands a 4090 exactly at `ratio` x the ladder basis. DERIVED from the same cost model the
    gate uses, never typed — a hand-picked dollar figure would silently stop testing the boundary the moment
    the ladder is repriced."""
    import vast_cost_model as vcm
    return cf.basis_usd_per_ns() * ratio * vcm.ns_per_hour("RTX 4090")


# =============================================================================================================
# 1 + 2 — the two verdicts
# =============================================================================================================
def test_relaunch_is_held_at_a_bad_usd_per_ns(tmp_path):
    """1.76x basis — the exact multiple the step 1 shakeout was resuming at, unpriced, on 2026-07-27."""
    offers = [_offer("46392", _usd_h_at_ratio(1.76))]
    hold, doc = rmg.gate("step1_fanout", "shakeout-unit", RES, offers=offers,
                         readout_path=str(tmp_path / "hold.json"))
    assert hold is True
    assert doc["ratio_vs_basis"] > rmg.RELAUNCH_MAX_RATIO_VS_BASIS
    assert "drift line" in doc["reason"]
    # The reason must state WHY waiting is free, or a reader at 3 AM cannot grade the hold.
    assert "NEW PURCHASE" in doc["reason"]


def test_relaunch_is_allowed_at_a_good_usd_per_ns(tmp_path):
    hold, doc = rmg.gate("ternary", "5aks-nr4a3", RES, offers=[_offer("111", _usd_h_at_ratio(0.95))],
                         readout_path=str(tmp_path / "hold.json"))
    assert hold is False
    assert doc["ratio_vs_basis"] < rmg.RELAUNCH_MAX_RATIO_VS_BASIS
    assert doc["offers_priced"] and doc["offers_priced"][0]["machine_id"] == "111"


def test_the_boundary_is_the_drift_line_exactly():
    """At the line it CLEARS; above it it HOLDS. Pinned because a `>=` here and a `>=` in the reporting rule
    would disagree about the row that prints `⚠ DRIFT` — and the whole point of choosing this number was to
    make the board and the gate say the same thing."""
    basis = cf.basis_usd_per_ns()
    at = rmg.RELAUNCH_MAX_RATIO_VS_BASIS * basis
    assert rmg.verdict(at)[0] is False
    assert rmg.verdict(at * 1.001)[0] is True


def test_an_unreadable_or_unpriceable_board_holds(tmp_path):
    """An unreadable market is not a cheap one — the same discipline the fan-out guard already uses. This is
    the case where nobody is awake to check, which is exactly when guessing is worst."""
    hold, doc = rmg.gate("ternary", "u", RES, offers=[], readout_path=str(tmp_path / "h.json"))
    assert hold is True and "unpriceable" in doc["reason"]
    # A card that has never been benched has no $/ns, so it cannot be graded and must not be bought blind.
    hold2, _ = rmg.gate("ternary", "u", RES, offers=[_offer("9", 0.05, gpu="RTX 5090 Ti Imaginary")],
                        readout_path=str(tmp_path / "h2.json"))
    assert hold2 is True


# =============================================================================================================
# 3 — the boundary: renting is gated, RUNNING work is not
# =============================================================================================================
def test_a_board_emptied_by_exclusions_is_not_reported_as_a_price_hold(tmp_path):
    """The shared blacklist only grows, so a set large enough to disqualify the whole board would hold this
    gate forever while the readout blamed the market. The discriminating observation is that the board
    RETURNED offers and none survived the filter — that must be named, or a night is spent re-pricing a
    ceiling that was never the problem."""
    offers = [_offer("46392", _usd_h_at_ratio(0.5)), _offer("28164", _usd_h_at_ratio(0.6))]
    hold, doc = rmg.gate("ternary", "u", RES, offers=offers, excluded=["46392", "28164"],
                         readout_path=str(tmp_path / "r.json"))
    assert hold is True
    assert doc.get("hold_cause") == "exclusions_or_spec_not_price"
    assert "NOT A PRICE HOLD" in doc["reason"]
    # ...and the same board WITHOUT the exclusions clears, which is what proves the diagnosis.
    hold2, _ = rmg.gate("ternary", "u", RES, offers=offers, readout_path=str(tmp_path / "r2.json"))
    assert hold2 is False


def test_a_running_leg_is_never_reached_by_the_gate(monkeypatch):
    """THE BOUNDARY. Both watchdogs consult the gate only on the DIED branch — the branch where the host is
    already gone. A RUNNING verdict must reach `continue` without the gate being consulted at all, because a
    gate that could act on a live leg is a gate that can destroy paid-for work to avoid paying for work."""
    import ternary_vast_watchdog as tvwd
    called = []
    monkeypatch.setattr(rmg, "gate", lambda *a, **k: called.append(a) or (True, {}))
    monkeypatch.setattr(vw.rmg, "gate", lambda *a, **k: called.append(a) or (True, {}))
    monkeypatch.setattr(tvwd.rmg, "gate", lambda *a, **k: called.append(a) or (True, {}))

    # `classify` is the shared policy both watchdogs route through. A live instance whose scalar advanced is
    # RUNNING, and RUNNING is not an authorised relaunch — which is what keeps the gate out of its path.
    import watchdog_policy as wp
    verdict, _stall = wp.classify(has_result=False, has_failed_record=False, instance_alive=True,
                                  instance_age_min=120.0, container_started=True,
                                  progress_scalar=500, prev_scalar=100, prev_stall=0,
                                  setup_grace_min=90.0, stall_ticks=2)
    assert verdict == "RUNNING"
    assert wp.should_relaunch(verdict, 0, 8)[0] is False, \
        "only DIED may relaunch; if RUNNING ever becomes relaunchable the gate would gain reach over a live leg"
    assert called == [], "the gate must not be consulted for a leg that is still running"


def test_only_died_authorises_a_rental_at_all():
    """The gate sits behind `should_relaunch`, so its reach is exactly the set of verdicts that can rent."""
    import watchdog_policy as wp
    for v in ("RUNNING", "STALLED", "SETUP_STALL", "DONE", "FAILED"):
        assert wp.should_relaunch(v, 0, 8)[0] is False
    assert wp.should_relaunch("DIED", 0, 8)[0] is True


# =============================================================================================================
# 4 — a hold must be visible
# =============================================================================================================
def test_a_hold_is_written_to_a_readout_that_carries_the_snapshot(tmp_path):
    """§6: a silent hold is indistinguishable from a finished unit. The readout must carry the numbers that
    caused it, not merely the fact of it."""
    out = tmp_path / "relaunch-market-hold.json"
    hold, doc = rmg.gate("step1_fanout", "unit-A", RES, offers=[_offer("46392", _usd_h_at_ratio(2.0))],
                         readout_path=str(out))
    assert hold is True
    written = json.loads(out.read_text())
    row = written["units"]["unit-A"]
    assert row["held"] is True
    assert row["ratio_vs_basis"] == doc["ratio_vs_basis"]
    assert row["first_held_utc"]
    assert "CLAUDE.md §6" in written["_rule"]


def test_a_pass_that_clears_is_also_written(tmp_path):
    """Written on EVERY pass, not only on holds — otherwise a stale hold file outlives the market that caused
    it and the next reader grades a launch against last night's board."""
    out = tmp_path / "r.json"
    rmg.gate("ternary", "unit-B", RES, offers=[_offer("7", _usd_h_at_ratio(0.9))], readout_path=str(out))
    written = json.loads(out.read_text())
    assert written["units"]["unit-B"]["held"] is False


def test_both_fanout_workflows_commit_the_single_host_hold_readout():
    """A readout written into a runner and never committed is a silent hold with extra steps. The two
    workflows that can drive a single-unit launch must both carry the file back to the branch."""
    wf = os.path.join(os.path.dirname(os.path.dirname(MOD)), ".github/workflows")
    for name in ("step1-fanout-autoscale.yml", "fusion-cpu-extras.yml"):
        with open(os.path.join(wf, name)) as fh:
            assert rmg.STATE_BASENAME in fh.read(), f"{name} does not commit {rmg.STATE_BASENAME}"


def test_the_watchdogs_surface_a_hold_without_needing_write_access():
    """The two watchdogs are `permissions: contents: read` BY DESIGN — a relauncher that can push is a
    relauncher that can rewrite the trail it is judged on. So their holds are surfaced through GitHub
    annotations and the S3 snapshot instead, and the gate must emit both."""
    src = open(rmg.__file__).read()
    assert "::notice title=RELAUNCH HELD ON PRICE::" in src, "a routine hold must still be visible"
    assert "::error title=RELAUNCH HELD" in src, "an escalated hold must fail the job"
    assert "_save_state" in src and "state_prefix" in src, "the snapshot must also land in S3"


def test_the_escalation_clock_runs_off_persisted_state(tmp_path):
    """A ceiling nobody can clear must become trimcrae's decision rather than an idle night. The clock is
    per-unit and lives in S3, because a CI job has no memory between ticks."""
    class _S3:
        def __init__(self):
            self.store = {}

        def get_object(self, Bucket, Key):
            if Key not in self.store:
                raise KeyError(Key)
            return {"Body": _B(self.store[Key])}

        def put_object(self, Bucket, Key, Body):
            self.store[Key] = Body

    class _B:
        def __init__(self, b):
            self.b = b

        def read(self):
            return self.b

    s3 = _S3()
    bad = [_offer("1", _usd_h_at_ratio(3.0))]
    kw = dict(offers=bad, s3=s3, state_bucket="bkt", state_prefix="pfx",
              readout_path=str(tmp_path / "r.json"))
    hold, first = rmg.gate("ternary", "u", RES, now=1_000_000, **kw)
    assert hold and first["held_hours"] == 0.0 and first["escalated"] is False
    # Same unit, still held, RELAUNCH_ESCALATE_H later -> escalates and says so.
    later = 1_000_000 + int(rmg.RELAUNCH_ESCALATE_H * 3600) + 60
    hold2, second = rmg.gate("ternary", "u", RES, now=later, **kw)
    assert hold2 and second["first_held_utc"] == first["first_held_utc"]
    assert second["escalated"] is True
    # ...and the clock RESETS once the market clears, so a later bad night starts its own window.
    _, cleared = rmg.gate("ternary", "u", RES, now=later + 60, s3=s3, state_bucket="bkt",
                          state_prefix="pfx", readout_path=str(tmp_path / "r.json"),
                          offers=[_offer("1", _usd_h_at_ratio(0.9))])
    assert cleared["hold"] is False and cleared["first_held_utc"] is None


def test_without_persistence_the_gate_still_holds_but_says_the_clock_is_dead(tmp_path):
    """Degradation must be in the SAFE direction: the ceiling keeps working when the state store does not,
    and the readout admits that the escalation cannot fire."""
    hold, doc = rmg.gate("ternary", "u", RES, offers=[_offer("1", _usd_h_at_ratio(3.0))],
                         readout_path=str(tmp_path / "r.json"))
    assert hold is True
    assert "UNAVAILABLE" in doc["escalation_clock"]
    assert doc["escalated"] is False


# =============================================================================================================
# 5 — one fact, one place
# =============================================================================================================
def test_the_ceiling_is_the_repos_own_drift_line_not_a_new_number():
    # DERIVED, not 1.5: the buy line is an absolute $/ns and the multiple falls out of the current basis
    # (2026-07-27 re-expression). What must hold is that this gate uses the SAME line as the drift flag.
    assert rmg.RELAUNCH_MAX_RATIO_VS_BASIS == pytest.approx(iu.drift_multiple(), rel=1e-9)
    assert iu.drift_multiple() * cf.basis_usd_per_ns() == pytest.approx(iu.APPROVED_USD_PER_NS)
    import ternary_vast_launch as tv
    assert tv.MARKET_MAX_RATIO_VS_BASIS == iu.DRIFT_MULTIPLE, \
        "the ternary lane's fleet gate and the relaunch gate must quote ONE drift line"


def test_the_gate_does_not_reimplement_pricing(monkeypatch):
    """It must call the SAME ranker the renting path calls, or it can price a host the launcher would refuse
    (and, worse, clear a fleet nobody could actually buy)."""
    seen = []
    real = gb.rank_offers_by_usd_per_ns
    monkeypatch.setattr(gb, "rank_offers_by_usd_per_ns",
                        lambda offers, res, *a, **k: seen.append(res) or real(offers, res, *a, **k))
    rmg.price_offers([_offer("1", 0.10)], RES)
    assert seen and seen[0] is RES


def test_basis_comes_from_the_ladder_not_from_tonights_board():
    """Anchoring the ceiling to observations is self-ratcheting — a bad night would raise the ceiling until
    the gate permitted exactly the market it exists to refuse."""
    _h, _r, basis, _w = rmg.verdict(0.001)
    assert basis == cf.basis_usd_per_ns()


# =============================================================================================================
# the exemptions — narrow, enumerated, and each one real
# =============================================================================================================
def test_default_is_gated_not_exempt():
    """A caller that does not know must be GATED. The safe direction, and it makes a forgotten call site show
    up as a hold rather than as a silent bypass."""
    assert rmg.exemption() == (None, "")


def test_an_instance_we_already_hold_is_exempt():
    """Re-starting a box this account already rents is not a purchase: the rate was fixed at rental time and
    a stopped Vast box bills for its disk meanwhile, so holding costs money and saves none."""
    key, why = rmg.exemption(already_held_instance=True)
    assert key == "already_held_instance" and "billing disk" in why


def test_an_expiring_checkpoint_is_exempt_only_inside_the_window():
    import calendar
    import time
    now = 1_700_000_000
    soon = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now + 3600))
    far = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now + 30 * 24 * 3600))
    assert rmg.exemption(checkpoint_expires_utc=soon, now=now)[0] == "checkpoint_expiring"
    assert rmg.exemption(checkpoint_expires_utc=far, now=now)[0] is None
    # An unparseable expiry is not an expiry. Gate it; do not let a typo become a bypass.
    assert rmg.exemption(checkpoint_expires_utc="whenever", now=now)[0] is None
    assert calendar  # (import kept honest)


def test_the_exemption_list_is_closed_and_documented():
    """A new exemption must arrive with its reason written down. The rule's whole failure mode was an
    exemption cut on a plausible-sounding axis nobody had to justify."""
    assert set(rmg.EXEMPTIONS) == {"already_held_instance", "checkpoint_expiring"}
    for k, why in rmg.EXEMPTIONS.items():
        assert len(why) > 40, f"{k} needs a reason, not a label"


# =============================================================================================================
# every relaunching KIND can be priced
# =============================================================================================================
def test_every_watchdog_kind_supplies_a_relaunch_resource_spec():
    """The generic watchdog holds rather than renting when a kind cannot say what it would buy. That refusal
    is correct but useless if it fires in production, so the contract is pinned here: a new kind that forgets
    the method fails this test instead of silently never relaunching."""
    for name, kind in vw.KINDS.items():
        assert hasattr(kind, "relaunch_resource_spec"), \
            f"kind {name} cannot be priced by the $/ns gate, so its relaunches would all be held"


def test_the_step1_kind_prices_the_lanes_own_spec(monkeypatch):
    """The step 1 kind must hand the gate the LANE'S `FANOUT_RES`, not a spec of the watchdog's invention.

    ⚠ WHY THIS IS MOCKED AT `_lane` RATHER THAN DRIVEN THROUGH IT. `congeneric_fanout_vast` reads BUCKET /
    RESULT_PREFIX / FEP_IMAGE at IMPORT time, and `_lane` deliberately REFUSES if the already-imported module
    resolved a different environment — a guard that is right in production (a fresh CI process) and makes the
    call untestable in a pytest session where some earlier test imported the module first. Asserting identity
    with `FANOUT_RES` tests the thing that could actually be wrong (a hand-written spec drifting from the one
    the launcher rents against) without asserting the import guard away."""
    import congeneric_fanout_vast as cfv
    monkeypatch.setattr(vw.Step1FanoutKind, "_lane", staticmethod(lambda entry: cfv))
    spec = vw.KINDS["step1_fanout"].relaunch_resource_spec({"bucket": "b"}, [])
    assert spec is cfv.FANOUT_RES
    assert spec.min_vram_gb >= 24 and spec.interruptible is True


def test_the_kinds_specs_are_the_lanes_own_not_a_shared_default():
    """A ternary leg needs 32 GB RAM / 8 vCPU / 24 GB VRAM and a paralogue MD leg does not. Pricing one
    against the other's filter would grade a market the lane cannot buy from."""
    t = vw.KINDS["ternary"].relaunch_resource_spec({}, [])
    p = vw.KINDS["paralogue_md"].relaunch_resource_spec({}, [])
    assert (t.ram_gb, t.min_vram_gb) != (p.ram_gb, p.min_vram_gb)


# =============================================================================================================
# the shared machine blacklist — ⛔ RETIRED 2026-07-31, and these tests pin the RETIRED machinery
# =============================================================================================================
# trimcrae that day: *"You've gotta just stop doing the blacklist. It seems like it only ever bites us in the
# ass and clearing it always makes things better."* The durable list is now inert at the read path unless
# `VAST_DURABLE_EXCLUSIONS=1`, so the three tests below turn it on deliberately: the scope split they check
# (host crosses lanes, lane-scoped does not) is still CORRECT and still worth keeping green, because the
# retirement is a switch and a switch that flips back into untested code is a trap. What is live by default
# is pinned in `test_blacklist_retired.py`.
@pytest.fixture
def _durable_exclusions_on(monkeypatch):
    monkeypatch.setenv("VAST_DURABLE_EXCLUSIONS", "1")


class _FakeS3:
    def __init__(self):
        self.store = {}

    def get_object(self, Bucket, Key):
        if Key not in self.store:
            raise KeyError(Key)
        return {"Body": type("B", (), {"read": lambda s, b=self.store[Key]: b})()}

    def put_object(self, Bucket, Key, Body):
        self.store[Key] = Body


def test_a_host_scoped_exclusion_crosses_lanes(_durable_exclusions_on):
    """The 6:37 AM defect: the fan-out rented machine 46392 while the 5a-KS lane already knew it refuses
    starts. A host that never starts has infinite realised $/ns and is invisible to $/ns ranking, so without
    the union every lane pays a rental to rediscover the same box.

    ⚠ THE REASON IN THIS TEST CHANGED ON 2026-07-27, AND THE MECHANISM IT GUARDS DID NOT. It used to assert
    the union on a `resources_unavailable` reason. trimcrae's ruling that evening — "clear it out and don't
    add anything back unless you have a real reason" — reclassified capacity refusals as PERISHABLE: a claim
    about a moment, not about the host, and the class that grew the shared set to 48 permanent machines until
    it blocked 2 of 2 authorised placements on a healthy board. Capacity is now excluded for the current wave
    only and never published.

    So the cross-lane union is exercised here with a DURABLE reason instead. What that costs: a capacity
    refusal no longer crosses lanes, so a sibling lane may re-attempt a momentarily-busy host. That is a
    FAILED SUBMIT, which bills nothing — deliberately traded against a permanent, compounding capacity loss.
    """
    s3 = _FakeS3()
    assert vmb.publish(s3, "bkt", "46392", "container never started", lane="ternary") is True
    assert vmb.publish(s3, "bkt", "46392", "again", lane="ternary") is False   # idempotent
    assert vmb.union(["28164"], s3, "bkt") == ["28164", "46392"]


def test_the_shared_set_never_blocks_a_launch_when_unreadable(_durable_exclusions_on):
    """An optimisation that can fail a rental is a liability. Falling back to the lane's own list is exactly
    the previous behaviour."""
    class _Broken:
        def get_object(self, **k):
            raise RuntimeError("no network")

    assert vmb.union(["5"], _Broken(), "bkt") == ["5"]
    assert vmb.union(["5"], None, None) == ["5"]
    assert vmb.load(None, None) == ([], {})


def test_lane_scoped_exclusions_are_not_shared(monkeypatch, _durable_exclusions_on):
    """`pricing.md` A.1 WITHDREW the broad 'exclude any low-util machine' rule because a metadynamics leg's
    low utilisation was PLUMED's CPU-side bias and the same host ran at 74 % unbiased. Sharing a lane-scoped
    verdict would re-adopt the withdrawn rule by the back door."""
    import congeneric_fanout_vast as cfv
    published = []
    monkeypatch.setattr(vmb, "publish", lambda *a, **k: published.append(a) or True)
    monkeypatch.setattr(cfv, "_get_json", lambda *a, **k: {})
    s3 = _FakeS3()
    cfv._record_exclusion(s3, "bkt", "999", "gpu_util 12% for 2 checks")            # default scope="lane"
    assert published == [], "a workload-dependent verdict must stay local"
    cfv._record_exclusion(s3, "bkt", "888", "container never started", scope="host")
    assert published, "a machine that never starts is a property of the machine and must cross lanes"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))



def test_a_capacity_refusal_no_longer_crosses_lanes(monkeypatch):
    """The other half of the 2026-07-27 ruling, pinned where the union is consumed.

    A momentary "no free GPU" must not become a permanent cross-lane verdict. If this ever starts passing
    machines into the shared set again, the set will regrow to the state that blocked placement.
    """
    s3 = _FakeS3()
    assert vmb.publish(s3, "bkt", "46392", "resources_unavailable on start", lane="ternary") is False
    ids, _ = vmb.load(s3, "bkt")
    assert ids == []
