#!/usr/bin/env python3
"""Offline tests for the NR-V04 retrospective Vast lane (pure JobSpec construction — no Vast, no S3, no GPU).

The load-bearing thing these pin is that a retrospective leg starts from the co-fold model its unit name says
it does. The co-fold model is the unit of independence in the frozen statistics (prereg §4a), so a leg that
globbed a system directory instead of a pinned model prefix would quietly corrupt the model-level means the
verdict is computed from — and nothing downstream would notice.
"""
import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nrv04_retro_panel as retro       # noqa: E402
import nrv04_vast_launch as launch      # noqa: E402

BUCKET = "test-bucket"


def _spec(arm_id="retro_noncov_nr4a2", model=2, replica=1):
    return launch.build_retro_jobspec(retro.arm_by_id(arm_id), model, replica, "run", "br", BUCKET)


def test_cofold_prefix_is_pinned_to_the_units_model_seed():
    spec = _spec(model=3)
    assert spec.env["COFOLD_PREFIX_S3"] == f"s3://{BUCKET}/{retro.COFOLD_PREFIX}/nr4a2/seed_3/"
    assert spec.env["COFOLD_MODEL_SEED"] == "3"
    assert "-m3-" in spec.name, "the unit name must agree with the model prefix it stages from"


def test_every_authorized_unit_gets_a_distinct_checkpoint_and_result_prefix():
    specs = [launch.build_retro_jobspec(a, m, r, "run", "br", BUCKET) for a, m, r in retro.enumerate_units()]
    assert len(specs) == 18, "AMENDMENT 3 retired R2 — the authorized panel is R1 only"
    assert len({s.checkpoint_uri for s in specs}) == 18, "two units sharing a checkpoint would race"
    assert len({s.env["RESULT_S3"] for s in specs}) == 18


def test_retro_results_do_not_collide_with_the_feasibility_panels_prefix():
    """The feasibility panel's results are a cross-check, not part of this panel — they must not be collected
    into it by a shared prefix."""
    assert launch.RETRO_RESULT_PREFIX != launch.RESULT_PREFIX
    assert _spec().env["RESULT_S3"].startswith(f"s3://{BUCKET}/{launch.RETRO_RESULT_PREFIX}/")


def test_staging_patch_applied_and_pins_exactly_one_cif():
    assert launch._RETRO_PIPELINE != launch._PIPELINE
    assert "assemble_unit" in launch._RETRO_PIPELINE
    assert "leg_by_id" not in launch._RETRO_PIPELINE, "retro units carry no covalent-panel Leg"
    assert "wc -l" in launch._RETRO_PIPELINE, "a second CIF under the pinned prefix must fail, never be guessed"


def test_covalent_flags_only_on_the_nr4a1_arm():
    cov = _spec("retro_cov_nr4a1", 1, 0)
    assert cov.env["COVALENT"] == "1" and cov.env["COV_RESNUM"] == "551"
    for arm_id in ("retro_noncov_nr4a1", "retro_noncov_nr4a2", "retro_noncov_nr4a3"):
        assert _spec(arm_id, 1, 0).env["COVALENT"] == "0"


def test_specs_are_spot_safe_and_resumable():
    spec = _spec()
    assert spec.resources.interruptible is True
    assert spec.resume is True, "a preempted leg must resume from its checkpoint, not restart"
    assert spec.checkpoint_uri


def _clear_pilot_env(monkeypatch):
    monkeypatch.setenv("RETRO_PILOT_ONLY", "1")
    for v in ("RETRO_PILOT_UNIT", "RETRO_PILOT_ARM", "RETRO_PILOT_MODEL", "RETRO_PILOT_REPLICA"):
        monkeypatch.delenv(v, raising=False)


def test_pilot_is_a_paralogue_leg_not_nr4a1(monkeypatch):
    """The pilot's abort information is structural: the assembler has never read an NR4A2/NR4A3 co-fold.
    Piloting NR4A1 would leave the only real staging risk unexercised."""
    _clear_pilot_env(monkeypatch)
    units = launch.retro_units_to_run()
    assert len(units) == 1
    arm, model, replica = units[0]
    assert arm.target in ("NR4A2", "NR4A3") and not arm.covalent


# =============================================================================================================
# ★★ THE PILOT MUST BE ABLE TO POINT AT A UNIT THAT HAS NOT RUN (regression, 2026-07-31).
#
# `retro_units_to_run` returned the CONSTANT `retro_noncov_nr4a2` m1 r0. That was the one unit of 18 with a
# result already in S3 (run 30633508333 / job 91165301927: `1 of 18 authorized R1 leg(s) landed`, and that unit
# is the one absent from `missing_units`). So every `retro_pilot` dispatch printed
# `[skip] … result already in S3`, `to_rent=0`, rented nothing and returned 0 — a green run indistinguishable
# from a pilot that worked. The lane could not take §6's first ladder step at all, and the other 17 legs stayed
# blocked behind a pilot that could never run.
# =============================================================================================================

def test_pilot_advances_past_a_unit_that_already_landed(monkeypatch):
    _clear_pilot_env(monkeypatch)
    landed = {retro.unit_name(*u) for u in [(retro.arm_by_id("retro_noncov_nr4a2"), 1, 0)]}
    units = launch.retro_units_to_run(done=landed)
    assert len(units) == 1
    assert retro.unit_name(*units[0]) not in landed, "a pilot pinned to a finished unit can never run"


def test_pilot_keeps_the_prereg_paralogue_arm_when_it_advances(monkeypatch):
    """Advancing must not silently fall back to NR4A1 — prereg §7 picked a paralogue on purpose."""
    _clear_pilot_env(monkeypatch)
    arm2 = retro.arm_by_id("retro_noncov_nr4a2")
    landed = {retro.unit_name(arm2, 1, 0)}
    (arm, model, replica), = launch.retro_units_to_run(done=landed)
    assert arm.arm_id == "retro_noncov_nr4a2" and (model, replica) == (1, 1)


def test_pilot_returns_nothing_when_every_unit_has_landed(monkeypatch):
    _clear_pilot_env(monkeypatch)
    everything = {retro.unit_name(a, m, r) for a, m, r in retro.enumerate_units()}
    assert launch.retro_units_to_run(done=everything) == []


@pytest.mark.parametrize("sel", [
    "nrv04retro-retro_noncov_nr4a3-m2-r1",
    "retro_noncov_nr4a3 m2 r1",
    "retro_noncov_nr4a3:m2:r1",
    "nr4a3-m2-r1",
    "nr4a3 2 1",
    "NR4A3,m2,r1",
])
def test_selector_spellings_all_resolve_to_the_same_unit(monkeypatch, sel):
    _clear_pilot_env(monkeypatch)
    monkeypatch.setenv("RETRO_PILOT_UNIT", sel)
    (arm, model, replica), = launch.retro_units_to_run()
    assert (arm.arm_id, model, replica) == ("retro_noncov_nr4a3", 2, 1)


def test_a_bare_arm_selector_takes_that_arms_first_authorized_unit(monkeypatch):
    _clear_pilot_env(monkeypatch)
    monkeypatch.setenv("RETRO_PILOT_UNIT", "nr4a1")
    (arm, model, replica), = launch.retro_units_to_run()
    assert (arm.arm_id, model, replica) == ("retro_noncov_nr4a1", 1, 0)


@pytest.mark.parametrize("sel", ["retro_cov_nr4a1", "retro_epi_nr4a1", "retro_epi_nr4a3", "nr4a4", "nr4a3 m9 r0"])
def test_selector_cannot_reach_an_unauthorized_unit(monkeypatch, sel):
    """AMENDMENT 3 retired R2 and R3 is conditional. `arm_by_id` returns those arms happily, so a selector that
    resolved against ARMS instead of `enumerate_units()` would let one env var rent a unit no GO covers — and
    a retired covalent unit crash-loops on a live meter (nrv04_retro_panel.arms_for_stages)."""
    _clear_pilot_env(monkeypatch)
    monkeypatch.setenv("RETRO_PILOT_UNIT", sel)
    with pytest.raises(SystemExit):
        launch.retro_units_to_run()


@pytest.mark.parametrize("raw,expect_sel,expect_force", [
    ("", "", False),
    ("nr4a3 m2 r1", "nr4a3 m2 r1", False),
    ("!nr4a3 m2 r1", "nr4a3 m2 r1", True),
    ("nr4a3 m2 r1 force", "nr4a3 m2 r1", True),
])
def test_force_flag_rides_inside_the_selector_not_a_26th_input(raw, expect_sel, expect_force):
    assert launch.retro_pilot_force(raw) == (expect_sel, expect_force)


def test_an_explicit_pilot_that_gets_skipped_fails_the_job(monkeypatch, tmp_path):
    """The exact shape of the 2026-07-31 stall: the operator NAMES a unit, it is skipped for having a result,
    and the run goes green having rented nothing. That must fail — §6's 'holding silently' failure mode."""
    import types
    monkeypatch.chdir(tmp_path)
    _clear_pilot_env(monkeypatch)
    monkeypatch.setenv("RETRO_PILOT_UNIT", "nr4a2 m1 r0")
    monkeypatch.setenv("RETRO_MARKET_GATE", "0")
    monkeypatch.setattr(launch, "_vast_request", lambda *a, **k: {"instances": []})
    monkeypatch.setattr(launch, "presign_env_tarball", lambda b: "https://example/env.tgz")
    landed_key = f"{launch.RETRO_RESULT_PREFIX}/nrv04retro-retro_noncov_nr4a2-m1-r0/leg_x.json"
    monkeypatch.setattr(launch, "_s3_list", lambda *a, **k: [landed_key])
    import boto3
    monkeypatch.setattr(boto3, "client", lambda *a, **k: types.SimpleNamespace())
    rented = []
    monkeypatch.setattr(launch, "get_backend", lambda _n: types.SimpleNamespace(
        submit=lambda spec: (rented.append(spec.name),
                             types.SimpleNamespace(job_id=1, extra={"dph": 0.05}))[1]))

    assert launch.retro_launch(BUCKET) == 1, "a named pilot that rented nothing must not go green"
    assert rented == []

    # ...and `!` re-runs it on purpose, overwriting its own leg_*.json — nothing is deleted.
    monkeypatch.setenv("RETRO_PILOT_UNIT", "!nr4a2 m1 r0")
    assert launch.retro_launch(BUCKET) == 0
    assert rented == ["nrv04retro-retro_noncov_nr4a2-m1-r0"]


def test_default_pilot_rents_the_unrun_unit_when_the_pinned_one_has_landed(monkeypatch, tmp_path):
    """End-to-end of the fix: no selector, the prereg unit already landed -> the pilot rents the NEXT unrun
    paralogue unit instead of rendering a green no-op."""
    import types
    monkeypatch.chdir(tmp_path)
    _clear_pilot_env(monkeypatch)
    monkeypatch.setenv("RETRO_MARKET_GATE", "0")
    monkeypatch.setattr(launch, "_vast_request", lambda *a, **k: {"instances": []})
    monkeypatch.setattr(launch, "presign_env_tarball", lambda b: "https://example/env.tgz")
    monkeypatch.setattr(launch, "_s3_list", lambda *a, **k: [
        f"{launch.RETRO_RESULT_PREFIX}/nrv04retro-retro_noncov_nr4a2-m1-r0/leg_x.json"])
    import boto3
    monkeypatch.setattr(boto3, "client", lambda *a, **k: types.SimpleNamespace())
    rented = []
    monkeypatch.setattr(launch, "get_backend", lambda _n: types.SimpleNamespace(
        submit=lambda spec: (rented.append(spec.name),
                             types.SimpleNamespace(job_id=7, extra={"dph": 0.05}))[1]))
    assert launch.retro_launch(BUCKET) == 0
    assert rented == ["nrv04retro-retro_noncov_nr4a2-m1-r1"]


def test_full_fanout_is_the_whole_authorized_panel(monkeypatch):
    monkeypatch.setenv("RETRO_PILOT_ONLY", "0")
    units = launch.retro_units_to_run()
    assert len(units) == 18
    assert not any(a.covalent for a, _m, _r in units), (
        "a covalent unit raises in build_system BEFORE writing a leg JSON, so Vast re-runs the onstart and the "
        "box crash-loops on a live meter — and it can never complete the panel")


def test_arms_differ_only_in_target_and_covalency(monkeypatch):
    """Prereg §2c: identical protocol across arms. The env of two R1 legs at the same model/replica may differ
    only in the fields that identify the arm — any sampling-length or charge drift would be invisible bespoke
    treatment of a paralogue."""
    a = _spec("retro_noncov_nr4a2", 1, 0).env
    b = _spec("retro_noncov_nr4a3", 1, 0).env
    differing = {k for k in set(a) | set(b) if a.get(k) != b.get(k)}
    assert differing <= {"LEG_ID", "TARGET", "ENV_ASSEMBLY", "COFOLD_PREFIX_S3", "RESULT_S3"}
    for shared in ("PROD_NS", "EQUIL_NS", "LIGAND", "COVALENT", "MODE"):
        assert a[shared] == b[shared]


def test_empty_prefix_env_falls_back_instead_of_writing_to_the_bucket_root(monkeypatch):
    """A workflow input that is present-but-empty used to set the prefix to "" via os.environ.get(k, DEFAULT),
    which would send every staged read and every result to the bucket ROOT. `or DEFAULT` is the fix."""
    import importlib
    for var, attr, default in (("NRV04_COFOLD_PREFIX", "COFOLD_PREFIX", "nrv04-covalent-cofold"),
                               ("NRV04_RESULT_PREFIX", "RESULT_PREFIX", "nrv04-covalent-results"),
                               ("NRV04_RETRO_RESULT_PREFIX", "RETRO_RESULT_PREFIX", "nrv04-retro-results")):
        monkeypatch.setenv(var, "")
        mod = importlib.reload(launch)
        assert getattr(mod, attr) == default, f"{var}='' must fall back, not blank the prefix"
        monkeypatch.delenv(var, raising=False)
    importlib.reload(launch)


# ---------------------------------------------------------------- Vast co-fold lane (provider correctness)
def test_cofold_lane_runs_the_same_science_entry_point_as_sagemaker():
    """The Vast and SageMaker co-fold lanes must predict the same thing: same script, same env contract. If
    they drifted, two providers would silently produce different structures for the same panel."""
    spec = launch.build_cofold_jobspec("br", BUCKET, "nrv04-descriptive-v5",
                                       script="nrv04_ternary.py",
                                       extra_args="--skip-control --targets NR4A1,NR4A2,NR4A3", seeds="1,2,3")
    assert spec.env["TERNARY_SCRIPT"] == "nrv04_ternary.py"
    assert spec.env["SEEDS"] == "1,2,3"
    assert "--targets NR4A1,NR4A2,NR4A3" in spec.env["TERNARY_EXTRA_ARGS"]
    assert "nrv04_ternary.py" not in launch._COFOLD_PIPELINE, "the script must come from env, never hardcoded"
    assert '"$TERNARY_SCRIPT" --run' in launch._COFOLD_PIPELINE


def test_cofold_boltz_version_is_pinned():
    """An unpinned Boltz would make a rerun silently a different model — the SageMaker lane pins it and so
    must this one, at the same version."""
    assert launch.BOLTZ_SPEC.startswith("boltz==")
    assert launch.build_cofold_jobspec("br", BUCKET, "p").env["BOLTZ_SPEC"] == launch.BOLTZ_SPEC


def test_cofold_uploads_continuously_and_is_spot_safe():
    """Standing rule: a preemption or timeout after prediction N must still leave 1..N in S3."""
    spec = launch.build_cofold_jobspec("br", BUCKET, "p")
    assert spec.resources.interruptible is True
    assert "s3 sync" in launch._COFOLD_PIPELINE and "sleep 60" in launch._COFOLD_PIPELINE
    assert "SYNC_PID" in launch._COFOLD_PIPELINE


def test_cofold_runs_on_vast_gpu_not_a_cloud_default():
    spec = launch.build_cofold_jobspec("br", BUCKET, "p")
    assert spec.resources.gpu == "rtx4090" and spec.resources.min_vram_gb >= 24


def test_cofold_propagates_the_prediction_exit_code():
    """A Boltz crash must fail the run, not report false-green — the SageMaker lane learned this the hard way."""
    assert "exit $RC" in launch._COFOLD_PIPELINE


def test_cofold_requires_a_fresh_output_prefix(monkeypatch):
    monkeypatch.delenv("COFOLD_OUTPUT_PREFIX", raising=False)
    with pytest.raises(SystemExit, match="FRESH"):
        launch.cofold(BUCKET)


# ------------------------------------------------- OOM / post-mortem fixes (2026-07-24 pilot failures)
def test_md_lane_requests_enough_ram_for_a_466k_atom_system():
    """Both pilot legs were OOM-killed at 16 GB. Solvating/parameterizing the assembly is RAM-bound; VRAM is
    not the constraint (<4 GB used)."""
    assert launch.TERNARY_RES.ram_gb >= 48
    assert launch.TERNARY_RES.min_vram_gb == 24, "VRAM was never the problem — do not inflate it instead"


def test_cofold_lane_requests_enough_ram_for_boltz_diffusion():
    assert launch.build_cofold_jobspec("br", BUCKET, "p").resources.ram_gb >= 64


@pytest.mark.parametrize("pipeline_name", ["_PIPELINE", "_RETRO_PIPELINE", "_COFOLD_PIPELINE"])
def test_pipelines_are_idempotent_across_an_oom_restart(pipeline_name):
    """Vast re-runs onstart after an OOM kill. A surviving extraction/clone made the restart die on setup
    instead of retrying the work, so a recoverable failure became a permanent one."""
    p = getattr(launch, pipeline_name)
    assert "rm -rf" in p, f"{pipeline_name} must clear stale repo state before fetching"


@pytest.mark.parametrize("pipeline_name", ["_PIPELINE", "_RETRO_PIPELINE", "_COFOLD_PIPELINE"])
def test_pipelines_stream_stdout_to_s3_for_a_post_mortem(pipeline_name):
    """An OOM kill tears the host down with the EXIT trap. Without streamed stdout there is no traceback and a
    crash is indistinguishable from a slow leg — which is exactly what happened."""
    p = getattr(launch, pipeline_name)
    assert "tee -a /tmp/run.log" in p and "run.log" in p


# =============================================================================================================
# ⛔ THE BUY LINE — this lane rented at ANY price until 2026-07-31
# =============================================================================================================
def test_the_submitted_spec_carries_the_approved_buy_line():
    """`TERNARY_RES` never set `max_usd_per_ns`, so it defaulted to None and the ceiling clause in
    `gpu_backend.rank_offers_by_usd_per_ns` was INERT: this lane had no price refusal at all."""
    from inflight_usd_per_ns import APPROVED_USD_PER_NS
    for spec in (_spec(), launch.build_jobspec(
            __import__("nrv04_covalent_panel").PANEL[0], 0, "run", "br", BUCKET)):
        assert spec.resources.max_usd_per_ns == APPROVED_USD_PER_NS, (
            "every endpoint-MD rental must face the repo's approved $/ns (CLAUDE.md §1/§6)")


def test_the_buy_line_is_derived_from_the_one_home_never_typed():
    """CLAUDE.md §1: the invariant is an ABSOLUTE $/ns and the multiple of the ladder basis derives from it. A
    literal here would silently become a different rule the next time the throughput table is re-anchored."""
    import inspect
    from inflight_usd_per_ns import APPROVED_USD_PER_NS
    assert launch.buy_ceiling_usd_per_ns() == APPROVED_USD_PER_NS
    src = inspect.getsource(launch.buy_ceiling_usd_per_ns)
    assert "APPROVED_USD_PER_NS" in src
    assert not re.search(r"return\s+\d", src), "the ceiling must be imported, never a literal"


def test_the_gate_facing_spec_is_UNCAPPED_so_it_can_see_the_expensive_offers():
    """`ResourceSpec.max_usd_per_ns`'s own contract: a market gate must SEE the offers above the line in order
    to report how far above it the board sits. Only the spec handed to `submit` carries the cap."""
    assert launch.TERNARY_RES.max_usd_per_ns is None
    assert launch.endpoint_md_resources().max_usd_per_ns is None
    assert launch.endpoint_md_resources(max_usd_per_ns=0.5).max_usd_per_ns == 0.5


def test_this_lanes_own_historical_rate_band_is_mostly_above_the_line():
    """Not decoration — this is the measurement that makes the ceiling load-bearing rather than theoretical.
    The lane's recorded rentals are $0.10-0.21/hr on an RTX 3090 (prereg §7 / the 15-leg S3 ledger). Priced
    per NANOSECOND against the repo's approved rate, most of that band is a refusal."""
    import vast_cost_model as vcm
    from inflight_usd_per_ns import APPROVED_USD_PER_NS
    ns_h = vcm.ns_per_hour("RTX 3090")
    assert ns_h, "the 3090 must be in the throughput table or this lane cannot be graded at all"
    assert vcm.usd_per_ns(0.10, 0.0, ns_h) < APPROVED_USD_PER_NS, "the bottom of the band still clears"
    assert vcm.usd_per_ns(0.21, 0.0, ns_h) > APPROVED_USD_PER_NS, "the top of the band must be refused"


def test_the_card_stays_a_hint_so_a_faster_card_can_clear_the_same_line():
    """`require_gpu` must stay False: ranking is by $/ns, so a 4090 that clears the line beats a 3090 that does
    not. Making the card hard here would turn a price ceiling into an availability deadlock."""
    assert _spec().resources.require_gpu is False


# =============================================================================================================
# ⛔ THE CI-SIDE REAPER — scoped, and it must never reach another lane
# =============================================================================================================
_NOW = 1_000_000.0


def _inst(iid, label, status="running", age_s=60, **kw):
    d = {"id": iid, "label": label, "actual_status": status, "start_date": _NOW - age_s}
    d.update(kw)
    return d


def test_the_reaper_sees_a_finished_RETRO_leg_as_done():
    """THE BUG: `collect()` derived `done_units` from `RESULT_PREFIX` (the COVALENT panel's prefix) while the
    retrospective writes to `RETRO_RESULT_PREFIX`. A finished retro leg was therefore never recognised and
    never torn down — it billed to the 240-min backstop, or indefinitely if the container crash-looped."""
    assert launch.RETRO_RESULT_PREFIX != launch.RESULT_PREFIX
    done = {"nrv04retro-retro_noncov_nr4a2-m1-r0"}
    insts = [_inst(1, "nrv04retro-retro_noncov_nr4a2-m1-r0"),
             _inst(2, "nrv04retro-retro_noncov_nr4a3-m1-r0")]
    got = launch.teardown_candidates(insts, done, _NOW, 240 * 60, retro.LABEL_PREFIX)
    assert [(i["id"], w) for i, w in got] == [(1, "result-in-S3")]


def test_the_reaper_can_never_reach_another_lanes_instances():
    """THE OTHER BUG, and the dangerous one: `collect()` listed `owner=me` — EVERY instance on an account that
    is shared across concurrent sessions — and applied its over-age backstop to all of them. Running the NR-V04
    collect while a sibling lane was billing would have destroyed that lane's hosts."""
    stale = 99_999
    insts = [_inst(1, "nrv04retro-retro_noncov_nr4a2-m1-r0", age_s=stale),
             _inst(2, "nrv04cov-cov_nr4a1-s0", age_s=stale),
             _inst(3, "ternary-calib_hi_to_lo__ternary_vhl", age_s=stale),
             _inst(4, "s1f-edge-7", status="exited", age_s=stale),
             _inst(5, "bench-rtx4090-9p5nm", status="exited", age_s=stale),
             _inst(6, None, age_s=stale)]
    got = launch.teardown_candidates(insts, set(), _NOW, 240 * 60, retro.LABEL_PREFIX)
    assert [i["id"] for i, _w in got] == [1], "only the retro-labelled host may be a candidate"
    cov = launch.teardown_candidates(insts, set(), _NOW, 240 * 60, "nrv04cov-")
    assert [i["id"] for i, _w in cov] == [2]


@pytest.mark.parametrize("selector", ["", None, "   "])
def test_an_absent_label_selector_reaps_NOTHING(selector):
    """FAIL CLOSED. No selector means no authority — never a fallback to 'everything'. A reaper that destroys
    the wrong box is worse than one that is late."""
    insts = [_inst(1, "nrv04retro-x", age_s=99_999), _inst(2, "someone-elses-lane", age_s=99_999)]
    assert launch.teardown_candidates(insts, {"nrv04retro-x"}, _NOW, 240 * 60, selector) == []


def test_an_outbid_box_is_not_mistaken_for_a_dead_one():
    """An outbid interruptible instance looks exactly like a dead one ('stopped') but its disk is intact and
    Vast resumes it. Destroying it buys a ~20-min image reload we never owed. Over-age still reaps it."""
    outbid = _inst(1, "nrv04retro-a", status="stopped", is_bid=True,
                   intended_status="running", min_bid=0.30, price=0.10)
    assert launch.teardown_candidates([outbid], set(), _NOW, 240 * 60, retro.LABEL_PREFIX) == []
    old = launch.teardown_candidates([dict(outbid, start_date=_NOW - 99_999)], set(), _NOW,
                                     240 * 60, retro.LABEL_PREFIX)
    assert len(old) == 1 and "backstop" in old[0][1]


def test_a_duplicate_instance_on_one_label_is_reaped_but_the_running_one_is_kept():
    """Two instances under one label double-compute the leg and clobber its S3 checkpoint."""
    insts = [_inst(1, "nrv04retro-a", status="created", age_s=10),
             _inst(2, "nrv04retro-a", status="running", age_s=500)]
    got = launch.teardown_candidates(insts, set(), _NOW, 240 * 60, retro.LABEL_PREFIX)
    assert [i["id"] for i, _w in got] == [1]


def test_retro_reap_refuses_without_a_key_instead_of_silently_doing_nothing(monkeypatch, capsys):
    monkeypatch.delenv("VAST_API_KEY", raising=False)
    n, stopped = launch.retro_reap(BUCKET)
    assert (n, stopped) == (0, [])
    assert "cannot stop its own billing" in capsys.readouterr().out


# =============================================================================================================
# ⛔ THE MARKET GATE — a thin, expensive market is a reason to PAUSE, not to pay
# =============================================================================================================
def _offer(mid, gpu="RTX 4090", min_bid=0.10):
    return {"machine_id": mid, "id": mid, "gpu_name": gpu, "min_bid": min_bid, "dph_base": min_bid * 2,
            "num_gpus": 1, "gpu_ram": 24576, "cuda_max_good": 13.0, "reliability2": 0.99, "rentable": True,
            "storage_cost": 0.10, "inet_down": 500.0, "inet_up": 500.0, "cpu_cores_effective": 8.0,
            "cpu_ram": 64000, "disk_space": 200.0}


def test_the_market_gate_holds_on_an_expensive_board(tmp_path):
    hold, doc = launch.retro_market_gate(18, offers=[_offer(i, min_bid=3.0) for i in range(20)],
                                         readout_path=str(tmp_path / "hold.json"))
    assert hold is True
    assert doc["best_usd_per_ns"] > doc["buy_line_usd_per_ns"]
    assert json.loads((tmp_path / "hold.json").read_text())["hold"] is True, (
        "a hold that exists only in a job log is a SILENT hold — indistinguishable from a finished fleet")


def test_the_market_gate_clears_a_cheap_board(tmp_path):
    hold, doc = launch.retro_market_gate(18, offers=[_offer(i, min_bid=0.02) for i in range(30)],
                                         readout_path=str(tmp_path / "hold.json"))
    assert hold is False and doc["best_usd_per_ns"] < doc["buy_line_usd_per_ns"]


def test_the_market_gate_prices_the_FLEET_not_the_single_best_offer(tmp_path):
    """A fan-out of N buys the N CHEAPEST offers, not the best one N times. One cheap offer on an otherwise
    expensive, shallow board must not clear an 18-wide launch."""
    board = [_offer(0, min_bid=0.02)] + [_offer(i, min_bid=3.0) for i in range(1, 20)]
    one, _ = launch.retro_market_gate(1, offers=board, readout_path=str(tmp_path / "a.json"))
    many, doc = launch.retro_market_gate(18, offers=board, readout_path=str(tmp_path / "b.json"))
    assert one is False, "the single cheap host is buyable"
    assert many is True, "eighteen of them are not"
    assert doc["board_depth"]["used_for_mean"] > 1


def test_an_unreadable_board_is_a_HOLD_not_a_launch(tmp_path, monkeypatch):
    """CLAUDE.md §6 discipline: an unreadable market is not a cheap one, and this gate exists precisely for
    the case where nobody is awake to check."""
    monkeypatch.delenv("VAST_API_KEY", raising=False)
    hold, doc = launch.retro_market_gate(18, offers=None, key="", readout_path=str(tmp_path / "h.json"))
    assert hold is True and "board" in doc["reason"].lower()
    assert doc["board_error"], "the refusal must say it was for lack of evidence, not for a price"


def test_the_gate_and_the_spec_ceiling_are_the_same_number():
    """If the board-level gate cleared on one figure and `submit` bound a different one, a launch could pass
    the gate and still rent above the line."""
    import relaunch_market_gate as rmg
    from inflight_usd_per_ns import APPROVED_USD_PER_NS
    assert rmg.RELAUNCH_MAX_RATIO_VS_BASIS == pytest.approx(rmg.DRIFT_MULTIPLE)
    assert launch.buy_ceiling_usd_per_ns() == APPROVED_USD_PER_NS
    _hold, _r, basis, _why = rmg.verdict(APPROVED_USD_PER_NS)
    assert _hold is False, "a rental exactly AT the approved rate must CLEAR (documented boundary rule)"
    assert rmg.verdict(APPROVED_USD_PER_NS * 1.01)[0] is True


def test_a_launch_that_rented_nothing_does_not_report_success(monkeypatch, tmp_path):
    """CLAUDE.md §6's 'holding silently' failure mode: a fan-out that rents zero hosts renders in the Actions
    list identically to one that finished. If the buy line refuses every offer, that must be LOUD."""
    import types
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("RETRO_PILOT_ONLY", "0")
    monkeypatch.setenv("RETRO_MARKET_GATE", "0")     # isolate the per-offer refusal from the board gate
    monkeypatch.setenv("VAST_API_KEY", "")
    monkeypatch.setattr(launch, "_vast_request", lambda *a, **k: {"instances": []})
    monkeypatch.setattr(launch, "presign_env_tarball", lambda b: "https://example/env.tgz")
    monkeypatch.setattr(launch, "_s3_list", lambda *a, **k: [])
    import boto3
    monkeypatch.setattr(boto3, "client", lambda *a, **k: types.SimpleNamespace())

    refuse = types.SimpleNamespace(submit=_raise_no_offer)
    monkeypatch.setattr(launch, "get_backend", lambda _n: refuse)
    assert launch.retro_launch(BUCKET) == 1, "every unit refused -> the job must FAIL, not go green"

    ok = types.SimpleNamespace(submit=lambda spec: types.SimpleNamespace(job_id=1, extra={"dph": 0.05}))
    monkeypatch.setattr(launch, "get_backend", lambda _n: ok)
    assert launch.retro_launch(BUCKET) == 0
    assert len(json.loads((tmp_path / "nrv04-retro-handles.json").read_text())) == 18


def _raise_no_offer(spec):
    raise RuntimeError("no offer qualifies under the ceiling")


# =============================================================================================================
# ⛔ THE VERDICT MUST SURVIVE THE RUNNER
# =============================================================================================================
class _FakeS3:
    def __init__(self):
        self.put = {}

    def put_object(self, Bucket, Key, Body):        # noqa: N803 — boto3's own signature
        self.put[Key] = json.loads(Body.decode())


def test_the_collect_verdict_is_persisted_durably(tmp_path, monkeypatch):
    """It was written to a file on an ephemeral GitHub runner and thrown away: the workflow's upload step did
    not run in retro_collect mode and did not list the file. A paid-for panel's only deliverable cannot have a
    home that disappears with the runner."""
    monkeypatch.chdir(tmp_path)
    s3 = _FakeS3()
    out = {"panel_complete": True, "verdict": {"tier": "CONCORDANT"}}
    keys = launch.persist_retro_collect(out, bucket=BUCKET, s3=s3, utc="20260731T120000Z")
    assert len(keys) == 2 and all(k.startswith(f"{launch.RETRO_RESULT_PREFIX}/collect/") for k in keys)
    assert any(k.endswith("-latest.json") for k in keys), "a stable pointer for readers"
    assert any("20260731T120000Z" in k for k in keys), (
        "a timestamped copy, so re-running a collect cannot erase what an earlier one said")
    assert all(s3.put[k]["verdict"]["tier"] == "CONCORDANT" for k in keys)
    assert json.loads((tmp_path / launch.RETRO_COLLECT_READOUT).read_text())["panel_complete"] is True


def test_the_persisted_verdict_cannot_be_mistaken_for_a_leg_json(tmp_path, monkeypatch):
    """`retro_collect`, `retro_launch`'s skip set and the reaper all key off `leg_*.json` under the result
    prefix. A readout that matched would be parsed as a leg."""
    monkeypatch.chdir(tmp_path)                      # the local write must not land in the repo
    s3 = _FakeS3()
    launch.persist_retro_collect({}, bucket=BUCKET, s3=s3)
    for k in s3.put:
        assert not k.rsplit("/", 1)[-1].startswith("leg_")


# =============================================================================================================
# the preregistration itself
# =============================================================================================================
def test_the_starting_structure_asymmetry_is_a_registered_dated_limitation():
    """Pre-spend audit §6 gate 3 asked for EITHER a dated registered limitation OR a preregistered
    admissibility criterion. The limitation is what is registered; no new criterion was invented."""
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "nr4a3-nrv04-retrospective-prereg.md")
    txt = open(p, encoding="utf-8").read()
    assert "§2a/§2c LIMITATION — 2026-07-31" in txt, "the addition must be DATED"
    assert "1.05" in txt and "nr4a2/seed_1" in txt, "the pilot's measured overlap must be named"
    assert "No criterion is amended" in txt
    for direction in ("A NULL R1", "A POSITIVE"):
        assert direction in txt, "both a null and a positive must have their interpretation stated"


def test_the_machine_mirror_agrees_with_the_panel_module():
    """CLAUDE.md §1 — the JSON mirror and the code cannot disagree about what is authorized."""
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "nrv04-retrospective-prereg.json")
    d = json.load(open(p, encoding="utf-8"))
    assert tuple(d["panel"]["authorized_stages"]) == retro.AUTHORIZED_STAGES
    assert tuple(d["panel"]["retired_stages"]) == retro.RETIRED_STAGES
    assert d["panel"]["n_units_authorized"] == len(retro.enumerate_units())
    assert d["panel"]["label_prefix"] == retro.LABEL_PREFIX
    import nrv04_retro_gate as gate
    lo, hi = gate.EXTENSION_P_WINDOW
    assert f"({lo}, {hi}]" in d["statistics"]["extension_rule"]["trigger"]
    assert "leave-one-model-out" not in d["verdict_tiers"]["CONCORDANT"]


@pytest.mark.parametrize("pipeline_name", ["_PIPELINE", "_RETRO_PIPELINE", "_COFOLD_PIPELINE"])
def test_mark_no_longer_swallows_s3_failures(pipeline_name):
    """`mark() { ... 2>/dev/null || true; }` hid every write failure. The preflight must also fail HARD: a leg
    that cannot write to its result prefix cannot deliver a result, so it must not burn GPU."""
    p = getattr(launch, pipeline_name)
    assert "2>/dev/null || true; }" not in p, "mark() must not swallow its own errors"
    assert "preflight" in p and "exit 4" in p
