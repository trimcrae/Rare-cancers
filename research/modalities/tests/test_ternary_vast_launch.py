#!/usr/bin/env python3
"""Pure-logic tests for the Vast ternary lane (RUNG 2b).

Everything here runs with no network, no AWS and no GPU. What it guards is the class of bug that has
actually cost this repo money on the Vast lanes: an identity string that does not round-trip (so the reap
never fires and a finished leg keeps billing), a checkpoint prefix that is not keyed by the parameter that
makes two runs incompatible (so a 4 fs run silently resumes a 2 fs trajectory, or is "fixed" by wiping),
and a blank CI input arriving as an empty string rather than as unset.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ternary_vast_launch as tv  # noqa: E402


# ---------------------------------------------------------------- identity + label round-trip
def test_unit_id_is_keyed_by_timestep():
    """A dt change MUST produce a different unit id. OpenFE refuses to resume a checkpoint whose protocol
    timestep differs, so sharing an id between 2 fs and 4 fs is not a cosmetic collision — it is either a
    hard crash on resume or a wipe of someone else's trajectory."""
    a = tv.unit_id("calib_hi_to_lo__ternary_vhl", 0, "fwd", "2.0", "1.0", "edge")
    b = tv.unit_id("calib_hi_to_lo__ternary_vhl", 0, "fwd", "4.0", "1.0", "edge")
    assert a != b
    assert "dt2.0fs" in a and "dt4.0fs" in b


def test_unit_id_is_keyed_by_mode_seed_and_direction():
    base = dict(leg_id="calib_hi_to_lo__ternary_vhl", timestep_fs="4.0", warmup_timestep_fs="1.0")
    probe = tv.unit_id(seed=0, direction="fwd", mode="probe", **base)
    edge = tv.unit_id(seed=0, direction="fwd", mode="edge", **base)
    seed1 = tv.unit_id(seed=1, direction="fwd", mode="edge", **base)
    rev = tv.unit_id(seed=0, direction="rev", mode="edge", **base)
    assert len({probe, edge, seed1, rev}) == 4
    # forward carries NO direction suffix, so every pre-existing fwd key stays byte-identical
    assert "_dir" not in edge and "_dirrev" in rev


def test_label_round_trips_for_every_launchable_unit():
    """label_matches_unit is what `collect` reaps on. The protfep lane lost a reap because its label was a
    lossy encoding that could not be matched back — the host billed until the runtime backstop."""
    for mode in tv.MODES:
        for (leg, seed, direction) in tv.units_for(mode):
            uid = tv.unit_id(leg, seed, direction, "4.0", "1.0", mode)
            lab = tv.unit_label(uid)
            assert len(lab) <= 60, f"{lab} exceeds Vast's 60-char label limit"
            assert tv.label_matches_unit(lab, uid)
            assert not tv.label_matches_unit(lab, uid + "x")


def test_label_matches_unit_rejects_empties():
    assert not tv.label_matches_unit("", "u")
    assert not tv.label_matches_unit("tvast-u", "")
    assert not tv.label_matches_unit(None, None)


# ---------------------------------------------------------------- jobspec construction
def test_build_jobspec_probe_shape():
    j = tv.build_jobspec("calib_hi_to_lo__ternary_vhl", 0, "fwd", mode="probe",
                         timestep_fs="4.0", warmup_timestep_fs="1.0",
                         git_branch="b", bucket="bk", prefix="pfx")
    e = j.env
    assert e["RBFE_TIMESTEP_FS"] == "4.0" and e["RBFE_WARMUP_TIMESTEP_FS"] == "1.0"
    assert e["RBFE_PROD_ITERS"] == "200"          # the stage-1 survival probe length
    assert e["N_WINDOWS"] == "12"                 # 16 NaN'd at window 5; 12 is the proven recipe
    assert e["CHARGE_METHOD"] == "nagl"           # must match every other valB leg
    assert e["NEEDS_PREEQUIL"] == "1"
    assert e["COMMIT_S3"].startswith("s3://bk/pfx/commits/")
    assert "dt4.0fs" in e["COMMIT_S3"]
    assert j.image.endswith("ternary-fep:latest"), "must use the PARITY image, not a lookalike"
    assert j.resume is True


def test_solvent_leg_skips_preequilibration():
    """The pre-equilibration exists to relax a large, rough homology-built assembly before the softcore
    turns on. A ligand in a water box has no such assembly, so skipping is correct rather than a shortcut —
    and running it would fail, since there is no complex.pdb to relax."""
    j = tv.build_jobspec("calib_hi_to_lo__solvent", 0, "fwd", mode="edge", bucket="bk", prefix="pfx")
    assert j.env["NEEDS_PREEQUIL"] == "0"


def test_edge_mode_leaves_iteration_counts_derived():
    """Stage 2 must run the FULL science length; an accidental cap would silently produce a short leg whose
    dG looks like a real one."""
    j = tv.build_jobspec("calib_hi_to_lo__ternary_vhl", 0, "fwd", mode="edge", bucket="bk", prefix="pfx")
    assert j.env["RBFE_PROD_ITERS"] == "" and j.env["RBFE_WARMUP_ITERS"] == ""


def test_blank_bucket_falls_back_to_the_default_rather_than_to_nothing():
    """A blank CI input arrives as an EMPTY STRING, which is *set*, so `.get(k, default)` never fires and
    the URI resolves to `s3:///...` — a hole that once rented a 4090 whose uploads all failed silently
    behind `|| true`. The fix is `or`, not `.get`: an empty string must resolve to the module default."""
    j = tv.build_jobspec("calib_hi_to_lo__ternary_vhl", bucket="", prefix="")
    assert j.env["RESULT_S3"].startswith(f"s3://{tv.DEFAULT_BUCKET}/{tv.RESULT_PREFIX}/")
    assert "s3:///" not in j.env["RESULT_S3"] and "s3:///" not in j.env["COMMIT_S3"]


def test_an_actually_empty_location_is_refused(monkeypatch):
    """And if the default itself is ever emptied, the launcher must refuse rather than rent a host that
    uploads into the void."""
    monkeypatch.setattr(tv, "DEFAULT_BUCKET", "")
    with pytest.raises(ValueError):
        tv.build_jobspec("calib_hi_to_lo__ternary_vhl", bucket="", prefix="p")


def test_unknown_mode_rejected():
    with pytest.raises(ValueError):
        tv.build_jobspec("calib_hi_to_lo__ternary_vhl", mode="nope")
    with pytest.raises(ValueError):
        tv.units_for("nope")


def test_pipeline_calls_the_shared_recipe_and_never_reimplements_it():
    """A hand-copied ternary invocation is what made the last Vast attempt run 16 windows and NaN. The
    pipeline must call run_ternary_leg.sh and must NOT invoke the engine directly."""
    j = tv.build_jobspec("calib_hi_to_lo__ternary_vhl", bucket="b", prefix="p")
    body = j.command[-1]
    assert "bash run_ternary_leg.sh" in body
    for direct in ("python nr4a3_ternary_fep.py", "$PY nr4a3_ternary_fep.py",
                   "MODE=run", "N_ITER="):
        assert direct not in body, f"invoke the shared recipe, not the engine directly ({direct!r})"
    assert "SKIP_PREEQUIL=1" in body, "the lane overlays a cached relaxed complex itself"
    assert "RBFE_SPOT_COMMIT_S3" in body, "no commit store == a preemption loses the whole leg"


def test_pipeline_checks_cuda_before_paying_for_setup():
    """OpenMM silently falling back to CPU on a rented GPU is the worst outcome available: it bills a 4090
    to run ~200x slower and looks alive throughout."""
    body = tv.build_jobspec("calib_hi_to_lo__ternary_vhl", bucket="b", prefix="p").command[-1]
    assert "cuda-probe" in body
    assert body.index("cuda-probe") < body.index("run_ternary_leg.sh")


def test_pipeline_is_idempotent_before_any_gpu_work():
    body = tv.build_jobspec("calib_hi_to_lo__ternary_vhl", bucket="b", prefix="p").command[-1]
    assert body.index("leg.json already in S3") < body.index("run_ternary_leg.sh")


def test_caches_are_keyed_by_everything_that_changes_the_artifact():
    """Seed changes the starting homology model (starting_model_index = seed % n_models), so two seeds must
    not share a stage cache — sharing one would silently collapse the replicate spread this program uses as
    its error bar."""
    a = tv.build_jobspec("calib_hi_to_lo__ternary_vhl", seed=0, bucket="b", prefix="p").env
    c = tv.build_jobspec("calib_hi_to_lo__ternary_vhl", seed=1, bucket="b", prefix="p").env
    assert a["STAGE_CACHE"] != c["STAGE_CACHE"]
    assert a["PE_CACHE"] != c["PE_CACHE"]


def test_checkpoint_interval_never_truncates_its_phase():
    """The engine rounds each phase's target DOWN to a multiple of its checkpoint interval, so an interval
    larger than a short phase's requested length would SILENTLY shorten the run — a probe asking for 48
    warmup iterations at interval 64 would run 64, and one asking for 12 production at interval 40 would
    run 40. Both are wrong in a way no error message would report."""
    for mode, sizing in tv.MODES.items():
        for iters_key, ci_key in (("warmup_iters", "warmup_ckpt_iters"),
                                  ("prod_iters", "prod_ckpt_iters")):
            n, ci = sizing[iters_key], int(sizing[ci_key])
            if not n:
                continue           # derived (full science length) — always far above any interval
            assert int(n) % ci == 0, f"{mode}.{iters_key}={n} is not a multiple of {ci_key}={ci}"
            assert int(n) >= ci, f"{mode}.{iters_key}={n} is below {ci_key}={ci}"


def test_every_leg_persists_a_strided_trajectory():
    """THE RE-ANALYSABILITY REQUIREMENT. The NR-V04 covalent panel's read-only census found 72 objects across
    19 units and ZERO trajectory objects: everything kept was one pre-minimisation frame, a 1.35 GB System
    with no coordinates over time, or scalars already reduced against the wrong chain split. Three known
    analysis defects were therefore permanently uncorrectable and the panel has to be re-run or abandoned.
    Every leg this lane runs must store coordinates over time, and the stride must be a stride — OpenFE's
    every-iteration default was measured at ~1 GB per leg, re-uploaded whole at every spot commit."""
    for mode in tv.MODES:
        for (leg, seed, direction) in tv.units_for(mode):
            e = tv.build_jobspec(leg, seed, direction, mode=mode, bucket="b", prefix="p").env
            ps = float(e["RBFE_POSITIONS_WRITE_PS"])
            assert ps > 0, f"{mode}/{leg} would store NO positions — not re-analysable"
            assert ps >= 2.5, "a stride below one iteration is the every-iteration default in disguise"
            assert not e["RBFE_VELOCITIES_WRITE_PS"], "velocities double the size and buy no geometry"


def test_the_trajectory_setting_actually_reaches_the_engine():
    """Set in the jobspec but not forwarded past run_ternary_leg.sh would be a setting that exists only in a
    comment. The pipeline must name it in the env it hands the recipe."""
    body = tv.build_jobspec("calib_hi_to_lo__ternary_vhl", bucket="b", prefix="p").command[-1]
    assert "RBFE_POSITIONS_WRITE_PS" in body
    assert body.index("RBFE_POSITIONS_WRITE_PS") < body.index("bash run_ternary_leg.sh")


def test_md_timeout_is_inside_the_instance_runtime_cap():
    """The MD cap must fire BEFORE the instance cap, or the run is killed with the deliverable still on the
    host's disk and nothing uploaded."""
    j = tv.build_jobspec("calib_hi_to_lo__ternary_vhl", mode="edge", bucket="b", prefix="p")
    assert int(j.env["MD_TIMEOUT_S"]) < j.max_runtime_s


# ---------------------------------------------------------------- the ddG_coop identity
def test_ddg_coop_is_ternary_minus_binary_and_solvent_cancels():
    """The engine's own definition: ddG_coop = (ternary - solvent) - (binary - solvent) = ternary - binary.
    So a missing solvent leg is not a gap in this number, and including one must not change it."""
    legs = {"x__ternary_vhl": {"dg_morph_kcal": 47.4701},
            "x__binary_vhl": {"dg_morph_kcal": 48.0046}}
    r = tv.ddg_coop_identity(legs)
    assert r["ddg_coop_kcal"] == pytest.approx(-0.5345, abs=1e-4)   # reproduces the 2 fs r0 value
    legs["x__solvent"] = {"dg_morph_kcal": 47.8060}
    assert tv.ddg_coop_identity(legs)["ddg_coop_kcal"] == pytest.approx(-0.5345, abs=1e-4)


def test_cancellation_ratio_reports_how_little_survives_the_subtraction():
    """r0's answer was 1.1 % of the numbers being subtracted, which is why a 1.478 kcal/mol miss sat on top
    of a 0.045 statistical error. A reduction that does not surface this ratio hides its own fragility."""
    r = tv.ddg_coop_identity({"x__ternary_vhl": {"dg_morph_kcal": 47.4701},
                              "x__binary_vhl": {"dg_morph_kcal": 48.0046}})
    assert r["cancellation_ratio"] == pytest.approx(0.0111, abs=5e-4)


def test_ddg_coop_refuses_rather_than_guessing_when_a_leg_is_missing():
    assert tv.ddg_coop_identity({"x__ternary_vhl": {"dg_morph_kcal": 1.0}})["ddg_coop_kcal"] is None
    assert tv.ddg_coop_identity({})["ddg_coop_kcal"] is None
    assert tv.ddg_coop_identity({"x__ternary_vhl": {"dg_morph_kcal": None},
                                 "x__binary_vhl": {"dg_morph_kcal": 2.0}})["ddg_coop_kcal"] is None


def test_protocol_hash_mismatch_is_surfaced():
    """A cycle assembled from legs that did not run the same protocol is not a cycle. r0's hashes were
    consistent, which is how its miss could be attributed to physics rather than to a mismatch."""
    ok = tv.ddg_coop_identity({"x__ternary_vhl": {"dg_morph_kcal": 1.0, "protocol_hash": "a"},
                               "x__binary_vhl": {"dg_morph_kcal": 2.0, "protocol_hash": "a"}})
    bad = tv.ddg_coop_identity({"x__ternary_vhl": {"dg_morph_kcal": 1.0, "protocol_hash": "a"},
                                "x__binary_vhl": {"dg_morph_kcal": 2.0, "protocol_hash": "b"}})
    assert ok["protocol_hashes_consistent"] and not bad["protocol_hashes_consistent"]


# ---------------------------------------------------------------- the cost arithmetic under test
def test_four_fs_speedup_is_not_two_because_the_warmup_does_not_shrink():
    """THE CORRECTION RUNG 2b's headline number needs. Iteration counts are timestep-independent, so 4 fs
    halves production's force evaluations — but the warmup runs at 1 fs and its iteration count is derived
    from the WARMUP integrator, so 1 ns of equilibration costs 1e6 steps at either production dt. For the
    as-run protocol (1 ns warmup @1 fs + 5 ns production, 400 + 2000 iterations) the leg-level speedup is
    3.5e6/2.25e6 = 1.556x, not 2x."""
    s = tv.speedup_2fs_to_4fs(warmup_iters=400, prod_iters=2000, warmup_dt_fs=1.0)
    assert 1.55 < s < 1.56


def test_speedup_approaches_two_only_when_warmup_is_negligible():
    s = tv.speedup_2fs_to_4fs(warmup_iters=0, prod_iters=2000, warmup_dt_fs=1.0)
    assert abs(s - 2.0) < 1e-9


def test_cost_model_step_counts_match_openfe_derivation():
    m = tv.ternary_cost_model(16.0, warmup_iters=400, prod_iters=2000, prod_dt_fs=2.0)
    assert m["steps_per_iter_production"] == pytest.approx(1250.0)   # 2.5 ps / 2 fs
    assert m["steps_per_iter_warmup"] == pytest.approx(2500.0)       # 2.5 ps / 1 fs
    # a measured 16 s/iter at 2 fs => 2000 production iterations is ~8.9 h
    assert m["production_h"] == pytest.approx(2000 * 16.0 / 3600.0, rel=1e-6)


def test_stdout_is_unbuffered_so_progress_lines_arrive_when_they_happen():
    """rbfe_spot_driver logs with a bare `print` and contains zero `flush=True` — verified by grep, and
    observed on the stage-1 probe: the S3 run.log carried every flushed line from the engine and not one
    `[spot-driver]` line from the same process. Its lines are `[timing] ... s/iter` and `[barrier] committed
    checkpoint at iteration N`, i.e. the entire progress signal. Buffered at ~8 KB behind a pipe, they arrive
    in delayed bursts and a monitor cannot tell a stall from a buffer during the riskiest window."""
    for mode in tv.MODES:
        for (leg, seed, direction) in tv.units_for(mode):
            e = tv.build_jobspec(leg, seed, direction, mode=mode, bucket="b", prefix="p").env
            assert e.get("PYTHONUNBUFFERED") == "1"


def test_a_host_side_failure_leaves_no_leg_json_but_a_code_failure_does():
    """The distinction that decides whether the watchdog relaunches. A CUDA-probe failure means THIS HOST
    cannot run the job, so leaving no leg.json makes the unit read DIED and the launcher picks a different
    machine — correct. Any other phase failed for a reason that will reproduce, so it writes leg.json with
    status=failed and the watchdog's FAILED verdict refuses to relaunch; without that, a staging bug buys a
    fresh rental per attempt up to the daily cap, each dying identically."""
    body = tv.build_jobspec("calib_hi_to_lo__ternary_vhl", bucket="b", prefix="p").command[-1]
    assert '[ "$1" != cuda-probe ]' in body
    assert '"$RESULT_S3/leg.json"' in body
    assert "NOT writing leg.json" in body


def test_a_resume_archives_the_previous_attempts_log():
    """`exec > >(tee ...)` starts a fresh file and the sync loop overwrites the S3 copy, so without this the
    attempt that resumes destroys the only record of why the previous one ended."""
    body = tv.build_jobspec("calib_hi_to_lo__ternary_vhl", bucket="b", prefix="p").command[-1]
    assert "attempts/run-" in body
    assert body.index("attempts/run-") < body.index("bash run_ternary_leg.sh")
