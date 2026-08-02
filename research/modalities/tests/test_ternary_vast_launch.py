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
    assert body.index("DONE leg.json is already in S3") < body.index("run_ternary_leg.sh")


def test_a_failed_leg_does_not_block_its_own_retry():
    """The idempotency check must key on a leg that FINISHED, not on the file existing.

    `fail()` writes a leg.json with status=failed, so an existence test meant that once a leg had failed,
    every re-dispatch rented a host which immediately exited "nothing to do", produced nothing, and reported
    green. The 5a-KS smoke leg failed in preequil on 2026-07-26 and left exactly that record, so the next
    re-launch after the fix would have been a wasted rental.
    """
    body = tv.build_jobspec("calib_hi_to_lo__ternary_vhl", bucket="b", prefix="p").command[-1]
    # it must inspect the CONTENT for a done status, not merely `s3 ls` the key
    assert '"status"' in body and '"done"' in body
    assert "NOT done (a failed attempt)" in body, (
        "the pipeline no longer distinguishes a failed leg.json from a finished one")
    # and the short-circuit must still come before any billed work
    assert body.index("DONE leg.json is already in S3") < body.index("mark staging")


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


# ---------------------------------------------------------------- Vast's 16,384-char onstart cap
def test_rendered_onstart_is_under_vasts_hard_limit():
    """Vast caps the onstart at 16,384 characters and says so ONLY at rental time, as HTTP 400
    'invalid_args'. The launcher's per-unit `except` turns that into a printed line inside a GREEN job — a
    launch that rents nothing and reports success, with the watch list armed and no GPU running. Observed
    2026-07-25 re-launching the probe after a preemption: the onstart had reached 17,017 characters because
    three safety fixes had been added since the launch that worked."""
    from gpu_backend import VastBackend, _vast_onstart
    for mode in tv.MODES:
        for (leg, seed, direction) in tv.units_for(mode):
            j = tv.build_jobspec(leg, seed, direction, mode=mode)
            # measured with a realistic credential env, because _vast_onstart prepends one export per var
            n = len(_vast_onstart(j, VastBackend().self_terminate_cmd(),
                                  extra_env={"AWS_ACCESS_KEY_ID": "A" * 24,
                                             "AWS_SECRET_ACCESS_KEY": "S" * 44,
                                             "AWS_DEFAULT_REGION": "us-east-2"}))
            assert n <= tv.MAX_ONSTART_CHARS, (
                f"{mode}/{leg}: onstart is {n} chars, cap is {tv.MAX_ONSTART_CHARS}")


def test_comment_stripping_preserves_executable_meaning():
    """Comments stay in the SOURCE and are stripped at RENDER — the repo keeps the reasoning, the host gets
    the executable subset. Only lines whose first non-space character is `#` are dropped, so an inline `#`
    inside a string or a command is never touched."""
    body = "a=1\n  # a comment\nb='has # inside'\n\n\nc=2  # trailing\n"
    out = tv._render_pipeline(body)
    assert "# a comment" not in out
    assert "b='has # inside'" in out and "c=2  # trailing" in out and "a=1" in out


def test_the_rendered_pipeline_is_valid_bash_and_its_python_heredocs_compile():
    """Stripping is only safe if it cannot break either language embedded in the script."""
    import re
    import subprocess
    body = tv.build_jobspec("calib_hi_to_lo__ternary_vhl", bucket="b", prefix="p").command[-1]
    assert subprocess.run(["bash", "-n"], input=body, text=True).returncode == 0
    blocks = re.findall(r"<<'PYEOF'[^\n]*\n(.*?)\nPYEOF", body, re.S)
    assert len(blocks) == 2, f"expected 2 python heredocs, found {len(blocks)}"
    for i, b in enumerate(blocks):
        compile(b, f"<heredoc{i}>", "exec")


# ---------------------------------------------------------------- valB_mini replicates (r1 + r2)
def test_edge_reps_runs_two_independent_seeds_and_no_solvent_leg():
    """The replicate mode's shape IS a scientific claim, so it is asserted rather than trusted.

    Two claims, both checkable here:
      * SEEDS 1 AND 2, not 0 twice. `ternary_fep_reduce.per_replicate_ddg_coop` pairs legs BY SEED, so two
        legs at one seed are one replicate, not two, and the between-replicate cycle SD the frozen gate
        needs would not exist. SEED also keys the stage cache (starting_model_index = seed % n_models),
        the pre-equil cache and the commit prefix, so a re-used seed is not merely uninformative — it can
        resume into the other replicate's trajectory.
      * NO SOLVENT LEG. The solvent morph enters ΔΔG_alch,binary and ΔΔG_alch,ternary with the same sign
        and cancels EXACTLY inside each replicate's cycle, so a per-replicate solvent leg buys a full
        rental for a term that algebraically drops out.
    """
    units = tv.units_for("edge_reps")
    assert sorted({s for (_l, s, _d) in units}) == [1, 2]
    assert all(d == "fwd" for (_l, _s, d) in units)
    assert not any("solvent" in leg for (leg, _s, _d) in units)
    # exactly one ternary and one binary per seed — the two legs ΔΔG_coop = ternary − binary needs
    for seed in (1, 2):
        legs = sorted(leg for (leg, s, _d) in units if s == seed)
        assert legs == ["calib_hi_to_lo__binary_vhl", "calib_hi_to_lo__ternary_vhl"], legs


def test_each_replicate_gets_its_own_seed_keyed_caches_and_commit_prefix():
    """Two seeds that shared a stage cache would start from the SAME relaxed SMARCA2 model, and the spread
    this programme uses as its error bar would be sampling noise only — quietly narrower than the truth."""
    keys = {}
    for (leg, seed, direction) in tv.units_for("edge_reps"):
        e = tv.build_jobspec(leg, seed, direction, mode="edge_reps", bucket="b", prefix="p").env
        keys[(leg, seed)] = (e["STAGE_CACHE"], e["PE_CACHE"], e["COMMIT_S3"], e["UNIT_ID"])
    assert len(set(keys.values())) == len(keys), "two replicate units share a cache or commit prefix"
    for leg in ("calib_hi_to_lo__ternary_vhl", "calib_hi_to_lo__binary_vhl"):
        assert "seed1" in keys[(leg, 1)][0] and "seed2" in keys[(leg, 2)][0]


def test_calibration_legs_carry_an_explicit_mcs_budget_and_a_fail_closed_map_assert():
    """★ THE ONE THAT MATTERS. `LomapAtomMapper(time=N)` is an MCS TIMEOUT in seconds and a timed-out MCS
    returns its best PARTIAL match SILENTLY — so what the alchemical transformation IS depended on how fast
    the rented host happened to be (measured: 111 atoms on two hosts, 80-with-31-dummies on a third). A
    short map is a different experiment that still converges and still returns a confident ΔG, and nothing
    downstream sees it: protocol_hash covers settings, system identity covers particle counts (unchanged by
    dummy-isation), and the 5-part gate reads unmapped atoms as evidence of "a real perturbation"."""
    for (leg, seed, direction) in tv.units_for("edge_reps"):
        e = tv.build_jobspec(leg, seed, direction, mode="edge_reps", bucket="b", prefix="p").env
        assert int(e["RBFE_LOMAP_TIME_S"]) >= 300, "the MCS budget must be set explicitly, not inherited"
        assert e["RBFE_MAP_ASSERT"] == "1", "a calibration leg must fail closed on a short map"


def test_only_seed_can_recover_one_replicate_without_re_renting_its_sibling():
    """`--only` filters by LEG id, which cannot separate two replicates of the SAME leg — and edge_reps
    carries exactly that. Without a seed filter, recovering one preempted arm means re-listing all four."""
    sel = [u for u in tv.units_for("edge_reps") if u[1] == 2]
    assert len(sel) == 2 and {s for (_l, s, _d) in sel} == {2}


def test_strict_provenance_is_on_for_the_fresh_replicate_units_and_off_for_the_rest():
    """`fingerprint_mismatch_reason` ACCEPTS an unstamped committed generation unless RBFE_STRICT_PROVENANCE
    is set, because refusing one would make a leg already running with pre-stamping generations throw away
    paid GPU hours on its next preemption. The replicate units' commit prefixes do not exist yet, so nothing
    unstamped can ever need resuming and the concession buys nothing — but it must stay OFF elsewhere, where
    another lane has legs in flight whose generations predate stamping."""
    for (leg, seed, direction) in tv.units_for("edge_reps"):
        e = tv.build_jobspec(leg, seed, direction, mode="edge_reps", bucket="b", prefix="p").env
        assert e["RBFE_STRICT_PROVENANCE"] == "1"
    for mode in ("edge", "probe", "5aks"):
        leg, seed, direction = tv.units_for(mode)[0]
        e = tv.build_jobspec(leg, seed, direction, mode=mode, bucket="b", prefix="p").env
        assert e["RBFE_STRICT_PROVENANCE"] == "0", f"{mode} must not refuse an unstamped resume"


def test_supersede_refuses_a_done_record_and_archives_a_failed_one():
    """A stale `status=failed` leg.json is not untidy, it is dangerous: `classify` returns FAILED only when
    `has_failed_record AND not instance_alive`, so a relaunch SUPPRESSES the record rather than clearing it.
    When the new attempt exits without a leg.json the old record fires again — an alert pointing at a cause
    already fixed — and the watchdog's refusal-to-relaunch-a-failed-unit then blocks the very recovery it
    exists to trigger, overnight, with nobody awake.

    Two properties are load-bearing and are pinned here without touching S3:
      * a `status=done` record is REFUSED (this must never be able to destroy a result);
      * a `status=failed` record is ARCHIVED, not deleted, so the forensic trail survives.
    """
    import types
    calls = {"copied": [], "deleted": []}

    class _FakeS3:
        def head_object(self, **kw):
            return {}

        def copy_object(self, **kw):
            calls["copied"].append((kw["CopySource"]["Key"], kw["Key"]))

        def delete_object(self, **kw):
            calls["deleted"].append(kw["Key"])

    recs = {
        "unit_FAILED": {"unit_id": "unit_FAILED", "status": "failed", "rc": 1, "phase": "preequil"},
        "unit_DONE": {"unit_id": "unit_DONE", "status": "done", "dg_morph_kcal": -1.0},
    }
    orig_s3, orig_recs = tv._s3, tv.leg_records
    try:
        tv._s3 = lambda: _FakeS3()
        tv.leg_records = lambda **kw: recs
        out = tv.supersede_failed_record("unit_", bucket="b", prefix="p")
    finally:
        tv._s3, tv.leg_records = orig_s3, orig_recs

    cleared = [c["unit_id"] for c in out["cleared"]]
    assert cleared == ["unit_FAILED"], f"only the failed record may be cleared, got {cleared}"
    assert any("done" in s["why"] and s["unit_id"] == "unit_DONE" for s in out["skipped"]), \
        "a status=done record must be refused by name, not silently skipped"
    # archived before deleted, and to a superseded/ key that keeps the evidence
    assert calls["copied"], "the record must be ARCHIVED, not just deleted"
    assert all("/superseded/" in dest for _src, dest in calls["copied"]), calls["copied"]
    assert all("unit_DONE" not in k for k in calls["deleted"]), "a result was deleted"


def test_supersede_dry_run_touches_nothing():
    class _FakeS3:
        def head_object(self, **kw):
            return {}

        def copy_object(self, **kw):
            raise AssertionError("dry run must not copy")

        def delete_object(self, **kw):
            raise AssertionError("dry run must not delete")

    orig_s3, orig_recs = tv._s3, tv.leg_records
    try:
        tv._s3 = lambda: _FakeS3()
        tv.leg_records = lambda **kw: {"u": {"unit_id": "u", "status": "failed", "rc": 1}}
        out = tv.supersede_failed_record("u", bucket="b", prefix="p", dry_run=True)
    finally:
        tv._s3, tv.leg_records = orig_s3, orig_recs
    assert out["dry_run"] and [c["unit_id"] for c in out["cleared"]] == ["u"]


# ---------------------------------------------------------------- market gate ($/ns), CLAUDE.md §6
def test_the_market_ceiling_is_this_rungs_own_band_not_a_fleet_sized_one():
    """The guard must enforce THIS rung's authorisation. LANE 21's fan-out ceiling is the top of a $15-80
    band for nineteen edges; pricing two replicates against that — or against any fixed fleet-sized
    threshold — would refuse a small authorised spend for a reason that does not apply to it. Both the plan
    and the ceiling are DERIVED from the ladder artifact, so they re-derive themselves on a repricing."""
    plan1, ceil1 = tv.rung_band_usd(1)
    plan4, ceil4 = tv.rung_band_usd(4)
    # proportional in the unit count (each figure is rounded to the cent, so allow that much per unit)
    assert plan4 == pytest.approx(plan1 * 4, abs=0.04) and ceil4 == pytest.approx(ceil1 * 4, abs=0.04)
    assert plan4 < ceil4, "the ceiling must be the TOP of the band, above the plan figure"
    # The four-leg replicate pair, against the figure STRATEGY publishes for this edge.
    # ⚠ REPRICED 2026-07-27 (was 8.78 / 22.28): the throughput table was re-anchored onto a median-of-N-hosts
    # estimator and the ladder REGENERATED from it — pricing.md Appendix T. The GPU-hours are unchanged; only
    # the $/reference-GPU-hour moved, so these figures move with the artifact exactly as the docstring says
    # they should ("both the plan and the ceiling are DERIVED from the ladder artifact, so they re-derive
    # themselves on a repricing"). Re-pinning them is the correct response to a repricing, not a loosening.
    assert plan4 == pytest.approx(7.32, abs=0.05)
    assert ceil4 == pytest.approx(20.74, abs=0.05)


def test_the_gate_holds_above_breakeven_and_clears_below_it():
    """Arithmetic only — no board read. The break-even is the $/ns at which the projected cost equals the
    rung's ceiling; anything above it must HOLD and anything below must CLEAR, so the guard cannot be
    accidentally inverted or made unreachable."""
    n = 4
    ns_unit = tv.rung_ns_per_unit()
    _plan, ceiling = tv.rung_band_usd(n)
    breakeven = ceiling / (ns_unit * n)
    assert round(breakeven * ns_unit * n, 2) == pytest.approx(ceiling, abs=0.01)
    assert breakeven * 1.01 * ns_unit * n > ceiling     # just above -> hold
    assert breakeven * 0.99 * ns_unit * n < ceiling     # just below -> clear


def test_the_gate_prices_against_this_lanes_own_host_filter():
    """`market_snapshot` in the fan-out lane ranks against the fan-out's ResourceSpec. A ternary leg needs
    32 GB RAM / 8 vCPU / 24 GB VRAM — setup is CPU+RAM bound and a 16 GB box measured 4x slower — so pricing
    this fleet against a different spec would price hosts the launcher would never actually rent."""
    res = tv.resource_spec()
    assert res.ram_gb >= 32 and res.vcpus >= 8 and res.min_vram_gb >= 24


def test_the_ratio_ceiling_binds_even_when_the_dollar_ceiling_passes():
    """★ THE CASE THAT DECIDED THE LAUNCH ON 2026-07-27. Four legs at 2.05x basis projected $17.99 against a
    $22.28 authorisation: it CLEARED the dollars and was still double per ns. trimcrae's stated preference —
    "I'd rather pause until availability opens than pay double per ns" — is a different test from "do not
    spend past what was approved", and a guard with only the dollar test would have bought.

    1.5 is the repo's own number: CLAUDE.md §1 already calls >=1.5x basis drift and requires every in-flight
    row to say so, so buying at a multiple the reporting rules classify as drift contradicts the same
    document twice on one line."""
    from congeneric_fanout import basis_usd_per_ns
    basis = basis_usd_per_ns()
    n, ns_unit = 4, tv.rung_ns_per_unit()
    _plan, ceiling = tv.rung_band_usd(n)
    # 2.048 is a HISTORICAL BOARD READING — a measurement from the night this case documents — so it is
    # correctly typed. What must NOT be typed is the ceiling it is compared against, and the margin between
    # them is now only ~0.13x: another upward correction of the basis would flip this silently. So the
    # relationship is asserted against the DERIVED cap, and the fixture is pinned as what it is.
    at_205 = 2.048 * basis
    assert round(at_205 * ns_unit * n, 2) <= ceiling, "the night's board did clear the DOLLAR ceiling"
    assert 2.048 > tv.MARKET_MAX_RATIO_VS_BASIS, "...and must still be refused on the RATIO ceiling"
    assert tv.MARKET_MAX_RATIO_VS_BASIS < 2.048, ("if a basis correction ever lifts the derived cap past "
                                                  "this historical reading, this case stops testing a "
                                                  "REFUSAL and starts silently testing an approval")
    # DERIVED from the approved absolute rate, not typed (2026-07-27 re-expression).
    import inflight_usd_per_ns as _iu
    assert tv.MARKET_MAX_RATIO_VS_BASIS == pytest.approx(_iu.drift_multiple(), rel=1e-9)


def test_the_ratio_ceiling_is_reachable_and_not_a_permanent_refusal():
    """A ceiling nobody can clear turns into an idle night, so the threshold must sit above what the board
    has actually delivered. It ran ~1.0x basis earlier the same evening (a 3090 at $0.0643/hr)."""
    assert tv.MARKET_MAX_RATIO_VS_BASIS > 1.0


# ---------------------------------------------------------------- the 2026-07-27 lost-window regression
#
# WHAT HAPPENED, from the job logs. The `market_gate` job read the board at 9:13:04 AM ET (1.261x basis, 64
# offers, 31 priceable), CLEARED, and dispatched the launch. The `launch` job then spent 2 m 35 s pulling the
# ternary-fep image for the atom-map pre-flight and re-read the board at 9:16:28 AM ET: 2.436x, 49 offers, 9
# priceable. HOLD, exit 1, nothing rented. Repeated at 9:23 -> 9:26 AM ET (1.455x -> 1.904x).
#
# Two defects, and this block pins the fix to each:
#   1. THE PURCHASE WAS DECIDED TWICE. A launch needed two independent board reads, minutes apart, to both
#      clear — so the gate could clear and still buy nothing. The refusal now lives at SELECTION, per offer.
#   2. THE FAILURE WAS INVISIBLE. The launch's HOLD snapshot overwrote the gate's CLEAR in the same file, so
#      a cleared-then-died launch and an ordinary hold were byte-indistinguishable afterwards.
#
# These are tested here rather than left to the next clear board because a clear board is RARE — that is the
# whole problem. A guard exercised only on the path that almost never runs is a guard nobody has tested.
def test_the_buy_line_travels_with_the_jobspec_so_no_host_above_it_can_be_rented():
    """★ DEFECT 1. The binding refusal must be on the OFFER, not on a board mean beside it.

    `rank_offers_by_usd_per_ns` drops every offer above `ResourceSpec.max_usd_per_ns` before selection sees
    it, so a capped spec cannot rent an over-line host on any path — first choice or the fallback after a
    capacity refusal. A JobSpec built without the cap is one a thin board can overcharge."""
    j = tv.build_jobspec("calib_hi_to_lo__ternary_vhl", 1, "fwd", mode="edge_reps",
                         timestep_fs="4.0", warmup_timestep_fs="1.0",
                         git_branch="b", bucket="bk", prefix="pfx")
    assert j.resources.max_usd_per_ns is not None, \
        "the JobSpec handed to submit() MUST carry the buy line — this is the 2026-07-27 defect"
    assert j.resources.max_usd_per_ns == pytest.approx(tv.buy_ceiling_usd_per_ns())


def test_the_buy_line_is_the_drift_line_times_the_ladder_basis_and_is_never_typed():
    """Rule 1: one home per number. The buy line is DERIVED from the same two facts the gate reports
    against, so a repricing or a change to the drift multiple moves both together and they cannot disagree."""
    from congeneric_fanout import basis_usd_per_ns
    assert tv.buy_ceiling_usd_per_ns() == pytest.approx(
        tv.MARKET_MAX_RATIO_VS_BASIS * basis_usd_per_ns())
    # and it is the SAME line the gate publishes as its own break-even-at-max-ratio
    import inflight_usd_per_ns as _iu
    assert tv.buy_ceiling_usd_per_ns() == pytest.approx(_iu.APPROVED_USD_PER_NS)


def test_the_gate_still_sees_the_expensive_offers_it_exists_to_report():
    """★ THE TRAP IN FIXING DEFECT 1, and it would look exactly like the bug being fixed.

    If the cap were put on `resource_spec()`'s default, the gate's own board read would be pre-filtered by
    it: every over-line offer would vanish before `market_gate` could price it, the ratio could never exceed
    1.5x, and a thin board would report "nothing priceable" instead of "2.44x". A gate blind to the offers
    it exists to refuse is a gate that measures nothing — the failure family this repo keeps paying for. So
    the DEFAULT spec must stay uncapped and only the submit path may carry the line."""
    assert tv.resource_spec().max_usd_per_ns is None
    assert tv.resource_spec(max_usd_per_ns=0.0065).max_usd_per_ns == 0.0065


def test_an_over_line_offer_is_unselectable_while_the_same_board_stays_visible_to_the_gate():
    """The two halves above, exercised together on one synthetic board through the REAL ranking code.

    The board carries one offer under the line and one over it. Uncapped (the gate's view) both are
    priceable, which is what lets the gate say how far above the line the board sits. Capped (the renter's
    view) only the under-line offer survives, and `_select_cheapest_offer` can never return the other."""
    from gpu_backend import rank_offers_by_usd_per_ns, _select_cheapest_offer
    import dataclasses
    res = tv.resource_spec()
    offer = dict(machine_id=1, gpu_name="RTX 4090", num_gpus=1, gpu_ram=24564, cpu_ram=64 * 1024,
                 cpu_cores=16, disk_space=200, reliability2=0.99, cuda_max_good=13.0, rentable=True,
                 dph_total=0.20, dph_base=0.20, min_bid=0.02, storage_cost=0.10)
    cheap = dict(offer, machine_id=1, min_bid=0.02)
    dear = dict(offer, machine_id=2, min_bid=4.00)
    measured, _cap = rank_offers_by_usd_per_ns([cheap, dear], res)
    if len(measured) < 2:
        pytest.skip("RTX 4090 is not in the throughput bench on this checkout — nothing to rank")
    line = measured[0][0] * 1.5                       # a line the cheap offer clears and the dear one cannot
    assert measured[-1][0] > line, "the synthetic board must actually straddle the line"
    capped = dataclasses.replace(res, max_usd_per_ns=line)
    kept, _ = rank_offers_by_usd_per_ns([cheap, dear], capped)
    assert [t[2]["machine_id"] for t in kept] == [1], "an over-line offer must not survive the cap"
    assert _select_cheapest_offer([dear], capped) is None, \
        "with only over-line offers the renter must refuse, not fall back to the cheapest of them"


def test_a_launch_that_wanted_units_and_rented_none_is_distinguishable_from_one_with_nothing_to_do():
    """Both return an empty handle list, and conflating them is what let a launch that rented nothing exit
    0. Now that the buy line can legitimately refuse every offer on a thin board, that ambiguity would turn
    the price guard itself into a silent no-op — a fleet that never launched looking identical to one that
    finished, which CLAUDE.md §6 names as worse than the problem."""
    assert hasattr(tv.submit, "__call__")
    tv.submit.last_requested = 0                      # nothing needed renting -> green
    assert not getattr(tv.submit, "last_requested", 0)
    tv.submit.last_requested = 4                      # wanted four, got none -> red
    assert getattr(tv.submit, "last_requested", 0) and not []


# ---------------------------------------------------------------- the 11:06 AM ET provider-403 regression
#
# The morning's SECOND lost window, and a different cause from the first. The gate cleared at 11:07 AM ET
# (1.483x basis, 54 offers) and dispatched. The launch's every Vast call then answered a bare nginx
# `403 Forbidden` — the board read at 11:08:18, `/instances/`, and all four `/search/asks/` inside submit at
# 11:10:50 — so it rented 0/4. A `collect` on the same key at 11:13:56 listed instances normally, which is
# what proves the 403 transient rather than an authorisation problem.
#
# Two defects, both pinned below:
#   1. `_vast_request` retried 410 and 429 but NOT 403, so a throttle aborted the launch on the first try.
#   2. The launcher reported "every offer above the buy line OR every create failed" — one red job meaning
#      either "the guard worked" or "the launcher is broken", which is exactly the alert everyone learns to
#      ignore.
def test_a_transient_403_on_a_read_is_retried_rather_than_losing_the_window():
    """★ DEFECT 1. A bare 403 from the edge is a throttle; the same key worked either side of it."""
    import gpu_backend as gb
    import urllib.error
    calls = []

    def flaky(req, timeout=None):
        calls.append(req.full_url)
        if len(calls) < 3:                                 # 403 twice, then serve
            raise urllib.error.HTTPError(req.full_url, 403, "Forbidden", {},
                                         __import__("io").BytesIO(b"<html>403 Forbidden</html>"))
        class R:
            def read(self): return b'{"offers": [1, 2]}'
            def __enter__(self): return self
            def __exit__(self, *a): return False
        return R()

    orig_open, orig_sleep = gb.urllib.request.urlopen, __import__("time").sleep
    try:
        gb.urllib.request.urlopen = flaky
        __import__("time").sleep = lambda *_a: None        # don't actually wait out the backoff
        out = gb._vast_request("GET", "/search/asks/", "k")
    finally:
        gb.urllib.request.urlopen = orig_open
        __import__("time").sleep = orig_sleep
    assert out == {"offers": [1, 2]}, "a retried read must return the eventual success"
    assert len(calls) == 3, "it must actually have retried, not swallowed the error"


def test_a_403_on_a_MUTATION_is_never_retried_because_that_could_double_rent():
    """The safety limit on the retry above, and the reason it is scoped to GET. A 403 arriving after Vast
    accepted an instance create would, on retry, buy a SECOND host — paying twice for one unit and leaving
    an instance no watch list knows about. A read is idempotent; a create is not."""
    import gpu_backend as gb
    import urllib.error
    calls = []

    def always403(req, timeout=None):
        calls.append(req.get_method())
        raise urllib.error.HTTPError(req.full_url, 403, "Forbidden", {},
                                     __import__("io").BytesIO(b"<html>403 Forbidden</html>"))

    orig_open, orig_sleep = gb.urllib.request.urlopen, __import__("time").sleep
    try:
        gb.urllib.request.urlopen = always403
        __import__("time").sleep = lambda *_a: None
        with pytest.raises(RuntimeError):
            gb._vast_request("PUT", "/instances/1/", "k", body={"state": "running"})
    finally:
        gb.urllib.request.urlopen = orig_open
        __import__("time").sleep = orig_sleep
    assert len(calls) == 1, "a mutation must fail on the FIRST 403, never be retried"


def test_nothing_affordable_and_a_provider_fault_are_different_types():
    """★ DEFECT 2, at its root. Both used to be a bare RuntimeError, so both printed `0/N submitted` and
    failed the job identically. `NoQualifyingOffer` is raised only when the board was READ and had nothing
    buyable — the guard working — and it stays a RuntimeError so existing handlers are unaffected."""
    from gpu_backend import NoQualifyingOffer
    assert issubclass(NoQualifyingOffer, RuntimeError)
    assert not isinstance(RuntimeError("vast API GET /search/asks/ -> 403"), NoQualifyingOffer)


def test_a_clear_board_actually_rents_and_a_capped_board_holds_without_erroring():
    """★★ THE SYNTHETIC CLEAR BOARD. Real clear boards are rare — that is the whole problem with this lane —
    so the path that runs only on one is exercised here instead of waiting for the market.

    Same four units, same launcher, two boards. Under the line: four hosts rented, exit 0, no hold warning.
    Above the line: zero rented, and the launcher must report a HOLD (green, the guard working) rather than
    a FAULT. Getting this backwards in either direction is the bug the 2026-07-27 signal fix addresses."""
    import gpu_backend as gb

    class FakeBackend:
        def __init__(self, affordable): self.affordable, self.n = affordable, 0
        def submit(self, spec):
            if not self.affordable:
                raise gb.NoQualifyingOffer("vast: no rentable verified offer for <spec> (of 40 offers)")
            self.n += 1
            return type("H", (), {"job_id": "i%d" % self.n,
                                  "extra": {"machine_id": self.n, "min_bid": 0.05, "bid": 0.05, "dph": 0.06}})()

    def run(affordable):
        # cwd -> a scratch dir: `submit` writes `ternary-vast-handles.json` beside the process, and a test
        # that drops artifacts into the repo root is a test that edits the repo. Found immediately — the
        # file turned up in `git status` on the first run.
        import os as _os, tempfile
        orig = (tv.get_backend, tv.leg_records, tv._vast_request, tv._s3)
        cwd = _os.getcwd()
        tmp = tempfile.mkdtemp()
        _os.chdir(tmp)
        try:
            tv.get_backend = lambda _n: FakeBackend(affordable)
            tv.leg_records = lambda *a, **k: {}
            tv._vast_request = lambda *a, **k: {"instances": []}
            tv._s3 = lambda: type("S", (), {"put_object": lambda self, **kw: None})()
            got = tv.submit(mode="edge_reps")
            return got, tv.submit.last_requested, tv.submit.last_failure_kind
        finally:
            _os.chdir(cwd)
            tv.get_backend, tv.leg_records, tv._vast_request, tv._s3 = orig

    got, wanted, kind = run(True)
    assert wanted == 4 and len(got) == 4 and kind is None, "a clear board must rent every unit"
    assert len({h["machine_id"] for h in got}) == 4, "one unit per machine, not four on the cheapest"

    got, wanted, kind = run(False)
    assert wanted == 4 and got == [] and kind == "market", \
        "an unaffordable board is a MARKET hold, never a fault"


def test_one_provider_fault_among_price_refusals_still_reports_a_fault():
    """A launch is only entitled to say "the market refused us" if it got a clean answer from the market. If
    any unit died on a 403 we never learned what the board cost, so the benign classification would be a
    claim we cannot support — and it would hide a real defect behind an expected one."""
    import gpu_backend as gb

    class MixedBackend:
        def __init__(self): self.n = 0
        def submit(self, spec):
            self.n += 1
            if self.n == 1:
                raise RuntimeError("vast API GET /search/asks/ -> 403: <html>403 Forbidden</html>")
            raise gb.NoQualifyingOffer("vast: no rentable verified offer (of 40 offers)")

    orig = (tv.get_backend, tv.leg_records, tv._vast_request, tv._s3)
    try:
        tv.get_backend = lambda _n: MixedBackend()
        tv.leg_records = lambda *a, **k: {}
        tv._vast_request = lambda *a, **k: {"instances": []}
        tv._s3 = lambda: type("S", (), {"put_object": lambda self, **kw: None})()
        got = tv.submit(mode="edge_reps")
    finally:
        tv.get_backend, tv.leg_records, tv._vast_request, tv._s3 = orig
    assert got == [] and tv.submit.last_failure_kind == "fault", \
        "one fault among three price refusals must dominate the verdict"


# =============================================================================================================
# ★★ A GATE THAT RE-BOUGHT A SATISFIED LANE EVERY TICK (2026-07-27)
# =============================================================================================================
# The workflow called `--market-gate 4`. That 4 was the size of the MODE, not of the purchase, so it stayed 4
# after all four units were rented — and the gate went on pricing a four-unit fleet, clearing, and dispatching
# a launch that could only print "nothing to rent". It did so at 12:08, 12:26 and 12:35 PM ET. Left alone it
# would have re-dispatched on every future tick forever.
#
# `submit()` was never the bug: it lists live instances and skips units that already have a host, which is why
# $0 was actually spent. The bug was that the gate IN FRONT of it had no such notion, so the two disagreed
# about how many units were for sale — and a ledger row saying `launched` at 2.032x basis was the result.
def _fake_inst(uid, **kw):
    import ternary_vast_launch as tv
    d = {"id": 1, "machine_id": 9, "label": tv.unit_label(uid), "gpu_name": "RTX 5090",
         "num_gpus": 1, "dph_total": 0.1177, "dph_base": 0.101, "cur_state": "running",
         "actual_status": "running"}
    d.update(kw)
    return d


def _hosts(live, dead=None):
    """`unit_hosts`'s shape. The seam the gate and the launcher share is this SPLIT one, not the old flat
    dict — a fake that returns only "the instances that exist" cannot express the state that broke the lane."""
    return {"live": dict(live), "dead": dict(dead or {})}


def test_outstanding_units_excludes_units_that_already_hold_a_host(monkeypatch):
    """The shared question both the gate and the launcher must ask, from the same code."""
    import ternary_vast_launch as tv
    uids = [tv.unit_id(l, s, d, 4.0, 1.0, "edge_reps") for (l, s, d) in tv.units_for("edge_reps")]
    monkeypatch.setattr(tv, "leg_records", lambda *a, **k: {})
    monkeypatch.setattr(tv, "unit_hosts", lambda u, key=None: _hosts({x: _fake_inst(x) for x in uids[:3]}))
    out = tv.outstanding_units("edge_reps")
    assert len(out["live"]) == 3 and len(out["needed"]) == 1
    assert out["needed"] == [uids[3]]


def test_a_lane_whose_units_are_all_hosted_is_not_a_launch_candidate(monkeypatch):
    """The exact 12:29/12:39 PM ET state: four units, four live hosts. The gate must NOT dispatch."""
    import ternary_vast_launch as tv
    uids = [tv.unit_id(l, s, d, 4.0, 1.0, "edge_reps") for (l, s, d) in tv.units_for("edge_reps")]
    monkeypatch.setattr(tv, "leg_records", lambda *a, **k: {})
    monkeypatch.setattr(tv, "unit_hosts", lambda u, key=None: _hosts({x: _fake_inst(x) for x in uids}))

    def _boom(*a, **k):
        raise AssertionError("the market must not even be priced when nothing needs a host")
    monkeypatch.setattr(tv, "market_gate", _boom)

    action, readout = tv.gate_for_mode("edge_reps")
    assert action == "nothing-to-launch"
    # ⚠ AND IT IS NOT A HOLD. Filing it as one would run the price-escalation clock and fire the hold
    # warning for a lane that is working perfectly, which is the mirror-image false alarm.
    assert readout["hold"] is False and readout["nothing_to_launch"] is True
    assert "NOT a price hold" in readout["reason"]
    # the rate we are ALREADY paying is the only $/ns that means anything on a tick that is not buying
    assert len(readout["live_host_rates"]) == 4
    assert all(r["usd_per_ns"] for r in readout["live_host_rates"])


def test_a_completed_unit_is_not_a_launch_candidate_either(monkeypatch):
    import ternary_vast_launch as tv
    uids = [tv.unit_id(l, s, d, 4.0, 1.0, "edge_reps") for (l, s, d) in tv.units_for("edge_reps")]
    monkeypatch.setattr(tv, "leg_records", lambda *a, **k: {u: {"status": "done"} for u in uids})
    monkeypatch.setattr(tv, "unit_hosts", lambda u, key=None: _hosts({}))
    action, readout = tv.gate_for_mode("edge_reps")
    assert action == "nothing-to-launch" and len(readout["units_done"]) == 4


def test_the_gate_prices_only_the_units_that_still_need_a_host(monkeypatch):
    """A partially-hosted lane must be priced for the REMAINDER, not for the whole mode."""
    import ternary_vast_launch as tv
    uids = [tv.unit_id(l, s, d, 4.0, 1.0, "edge_reps") for (l, s, d) in tv.units_for("edge_reps")]
    monkeypatch.setattr(tv, "leg_records", lambda *a, **k: {})
    monkeypatch.setattr(tv, "unit_hosts", lambda u, key=None: _hosts({x: _fake_inst(x) for x in uids[:3]}))
    seen = {}

    def _gate(n, **kw):
        seen["n"] = n
        return False, {"reason": "ok", "hold": False}
    monkeypatch.setattr(tv, "market_gate", _gate)
    action, _ = tv.gate_for_mode("edge_reps")
    assert action == "clear" and seen["n"] == 1, "must price 1 unit, not the mode's 4"


def test_nothing_to_launch_has_its_own_exit_code_so_the_caller_cannot_dispatch(monkeypatch):
    """0 = dispatch, 1 = hold, 3 = nothing to launch. A shared code would put the satisfied lane back on the
    dispatch path (exit 0) or on the hold path (exit 1); both are wrong and one of them re-buys."""
    import ternary_vast_launch as tv
    uids = [tv.unit_id(l, s, d, 4.0, 1.0, "edge_reps") for (l, s, d) in tv.units_for("edge_reps")]
    monkeypatch.setattr(tv, "leg_records", lambda *a, **k: {})
    monkeypatch.setattr(tv, "unit_hosts", lambda u, key=None: _hosts({x: _fake_inst(x) for x in uids}))
    monkeypatch.setattr(tv, "blocked_machine_ids", lambda *a, **k: [])
    assert tv.main(["--mode", "edge_reps", "--gate-for-mode"]) == 3


def test_the_workflow_gate_derives_its_unit_count_instead_of_hardcoding_four():
    """The literal `--market-gate 4` is what could not notice that the lane was already satisfied."""
    import os
    wf = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))), ".github", "workflows", "gpu-ternary-fep-vast.yml")
    body = open(wf).read()
    assert "--gate-for-mode" in body
    # Comments stripped: the fix's own rationale quotes the retired flag, and a test that could not tell an
    # explanation from a call site would forbid writing down why the change was made.
    live = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("#"))
    assert "--market-gate 4" not in live, \
        "a hardcoded unit count cannot tell a satisfied lane from an empty one"
    assert 'RC" = 3' in body, "the workflow must handle 'nothing to launch' as its own, non-dispatching state"


# =============================================================================================================
# ★ WHAT WE PAID vs WHAT THE BOARD COST — two different quantities that must never be substituted
# =============================================================================================================
def test_rented_usd_per_ns_prices_the_instance_not_the_offer():
    """CLAUDE.md §1: a launcher's `dph≈` line reads LOW and must not be used. The instance's `dph_total` is
    bid + the real volume's disk line, i.e. what Vast actually charges."""
    import ternary_vast_launch as tv
    import vast_cost_model as vcm
    inst = _fake_inst("x", gpu_name="RTX 5090", dph_total=0.11766666666666667)
    got = tv.rented_usd_per_ns(inst)
    assert got == pytest.approx(0.11766666666666667 / vcm.ns_per_hour("RTX 5090"))
    # an ungradeable card must return None, never a fabricated zero in a price field
    assert tv.rented_usd_per_ns(_fake_inst("x", gpu_name="NOT A CARD")) is None
    assert tv.rented_usd_per_ns(_fake_inst("x", dph_total=0)) is None


def test_the_rate_row_flags_a_host_over_the_buy_line():
    import ternary_vast_launch as tv
    cheap = tv.rented_rate_row("u", _fake_inst("u", gpu_name="RTX 5090", dph_total=0.1177))
    # ⚠ DERIVED, NOT TYPED. This read `< 1.9166` — the drift multiple, hand-carried. That is the exact
    # shape that went stale when the ladder basis was re-anchored on 2026-07-27 ($0.004359 -> $0.003412/ns:
    # no price moved, the yardstick did), and it is the third instance of the pattern found that day. The
    # invariant is the ABSOLUTE rate; the multiple is derived from it (CLAUDE.md §1), so the assertion must
    # ask the cost model rather than remember a number the cost model can correct underneath it.
    import congeneric_fanout as _cf
    assert cheap["over_buy_line"] is False and cheap["x_basis"] < _cf.drift_buy_line_x_basis()
    dear = tv.rented_rate_row("u", _fake_inst("u", gpu_name="RTX 5090", dph_total=1.5))
    assert dear["over_buy_line"] is True


def test_the_rate_row_never_leaks_a_credential():
    """It gets COMMITTED to a public repo, and a Vast instance record carries jupyter_token / ssh_host /
    public_ipaddr. Allow-list, not redaction-list — same discipline as vast_rate_forensics.SAFE_FIELDS."""
    import ternary_vast_launch as tv
    import json as _json
    row = tv.rented_rate_row("u", _fake_inst(
        "u", jupyter_token="SECRET", ssh_host="1.2.3.4", ssh_port=22, public_ipaddr="1.2.3.4"))
    blob = _json.dumps(row)
    for leaked in ("SECRET", "1.2.3.4", "jupyter_token", "ssh_host", "public_ipaddr"):
        assert leaked not in blob, f"{leaked} must never reach a committed artifact"


# =============================================================================================================
# ⛔ THE ONE PATH BY WHICH THIS LANE COULD GENUINELY OVER-RENT — fail closed on an unreadable instance list
# =============================================================================================================
# The 2026-07-27 alarm was that three `launched` rows in 25 minutes might mean 12 hosts for a 4-leg job. They
# did not: the launcher lists live instances and skips units that already hold one. But that skip depends on a
# provider API call, and when it FAILED the launcher printed "duplicates are possible" and rented anyway —
# which is exactly the 12-hosts-for-4-legs outcome, arriving through the error path instead of the happy one.
# Not hypothetical: the sibling `/search/asks/` endpoint 403'd at 11:10 AM ET the same day.
def test_the_gate_refuses_to_dispatch_when_the_instance_list_cannot_be_read(monkeypatch):
    import ternary_vast_launch as tv
    monkeypatch.setattr(tv, "leg_records", lambda *a, **k: {})

    def _403(*a, **k):
        raise RuntimeError("vast API GET /instances/ -> 403")
    monkeypatch.setattr(tv, "unit_hosts", _403)
    monkeypatch.setattr(tv, "market_gate", lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("must not price, let alone clear, on an unreadable instance list")))

    action, readout = tv.gate_for_mode("edge_reps")
    assert action == "hold", "an unreadable instance list must never clear the gate"
    assert readout["hold"] is True and readout["nothing_to_launch"] is False
    assert "403" in readout["reason"] and "double-buy" in readout["reason"]


def test_outstanding_units_reports_that_it_could_not_read_the_list(monkeypatch):
    """`needed` is only trustworthy when `listing_ok` — on a failure everything looks unhosted."""
    import ternary_vast_launch as tv
    monkeypatch.setattr(tv, "leg_records", lambda *a, **k: {})
    monkeypatch.setattr(tv, "unit_hosts",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    out = tv.outstanding_units("edge_reps")
    assert out["listing_ok"] is False and "boom" in out["listing_error"]
    # the trap: every unit looks like it needs a host, which is why callers must check listing_ok
    assert len(out["needed"]) == 4


def test_submit_refuses_to_rent_when_it_cannot_see_what_it_already_holds(monkeypatch, capsys):
    """Refusing costs a delayed launch the next tick recovers from checkpoints. Proceeding costs a duplicate
    GPU-hour bill for work already in flight."""
    import ternary_vast_launch as tv
    monkeypatch.setenv("VAST_API_KEY", "x")
    monkeypatch.setattr(tv, "leg_records", lambda *a, **k: {})
    monkeypatch.setattr(tv, "unit_hosts",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("403 Forbidden")))

    def _never(*a, **k):
        raise AssertionError("submit must not reach the backend when the instance list is unreadable")
    monkeypatch.setattr(tv, "get_backend", _never)

    got = tv.submit(mode="edge_reps")
    assert got == [], "nothing may be rented"
    # and it must be a FAULT, not the benign price-hold word — we never learned what we already hold
    assert tv.submit.last_failure_kind == "fault"
    assert tv.submit.last_requested == 4, "renting zero of four wanted units must read as a shortfall"
    out = capsys.readouterr().out
    assert "REFUSING TO RENT" in out and "TVAST LAUNCHER FAULT" in out
    assert "duplicates are possible" not in out, "the old rent-anyway wording must not come back"


# =============================================================================================================
# ★★ A GATE THAT COUNTED INSTANCES THAT EXIST INSTEAD OF INSTANCES THAT RUN (measured 2026-07-27, 6:12 PM ET)
# =============================================================================================================
# `task=collect` at 6:17 PM ET printed, for the four RUNG 2b replicate units:
#
#     ternary_vhl_r1  46040507  up=exited   committed=none/0    RTX 5090
#     binary_vhl_r1   46040514  up=running  committed=warmup/832 RTX 5090
#     ternary_vhl_r2  46040577  up=exited   committed=none/0    RTX 4090
#     binary_vhl_r2   46040659  up=exited   committed=warmup/256 RTX 4090
#
# ONE of four was working. Five minutes earlier the gate's own snapshot said "no unit of mode edge_reps needs
# a host — 0 done, 4 already running. The market was not consulted", because `live_unit_hosts` returned every
# LABELLED instance regardless of state. Nothing in the loop would ever have re-placed the three dead legs:
# the count that decides whether to even look at the board was made from EXISTENCE, and an exited instance
# exists until something destroys it. Same defect class as `ternary_vast_watchdog.classify`'s
# `instance_alive = inst is not None`, fixed earlier the same day, in a different file, by hand.
#
# The predicate now has ONE home (`gpu_backend.vast_instance_occupies_slot`) and both sites import it.
def test_an_exited_instance_does_not_occupy_its_units_slot(monkeypatch):
    """The exact 6:17 PM ET board: one running host, three corpses. Three units must be for sale."""
    import ternary_vast_launch as tv
    uids = [tv.unit_id(l, s, d, 4.0, 1.0, "edge_reps") for (l, s, d) in tv.units_for("edge_reps")]
    # uids[1] is binary_vhl_r1 — the one leg that was genuinely running.
    insts = [_fake_inst(uids[0], id=46040507, actual_status="exited", cur_state="stopped"),
             _fake_inst(uids[1], id=46040514, actual_status="running", cur_state="running"),
             _fake_inst(uids[2], id=46040577, actual_status="exited", cur_state="stopped"),
             _fake_inst(uids[3], id=46040659, actual_status="exited", cur_state="stopped")]
    monkeypatch.setenv("VAST_API_KEY", "x")
    monkeypatch.setattr(tv, "_vast_request", lambda *a, **k: {"instances": insts})
    got = tv.unit_hosts(uids)
    assert list(got["live"]) == [uids[1]], "only the box that is actually running holds a slot"
    assert sorted(got["dead"]) == sorted([uids[0], uids[2], uids[3]])


def test_a_fresh_rental_still_pulling_its_image_DOES_occupy_its_slot(monkeypatch):
    """⚠ THE HALF OF THE OLD CONSERVATISM THAT MUST SURVIVE. A just-rented box reads
    actual_status=loading / cur_state=stopped for as long as 2 h 57 min on this account. Calling that free
    is how a launcher rents a SECOND GPU for work it has already paid to start."""
    import ternary_vast_launch as tv
    uids = [tv.unit_id(l, s, d, 4.0, 1.0, "edge_reps") for (l, s, d) in tv.units_for("edge_reps")]
    monkeypatch.setenv("VAST_API_KEY", "x")
    for status in ("loading", "created", "scheduling", "starting"):
        monkeypatch.setattr(tv, "_vast_request", lambda *a, s=status, **k: {
            "instances": [_fake_inst(uids[0], actual_status=s, cur_state="stopped")]})
        got = tv.unit_hosts(uids)
        assert list(got["live"]) == [uids[0]], f"a host at {status!r} is still ours and still starting"
        assert not got["dead"]


def test_the_gate_reprices_the_market_for_the_units_whose_hosts_died(monkeypatch):
    """The consequence that matters: three dead legs must send the gate back to the board, not to
    'nothing-to-launch'. With the old count this returned `nothing-to-launch` forever."""
    import ternary_vast_launch as tv
    uids = [tv.unit_id(l, s, d, 4.0, 1.0, "edge_reps") for (l, s, d) in tv.units_for("edge_reps")]
    dead = {u: _fake_inst(u, id=460405 + n, actual_status="exited", cur_state="stopped")
            for n, u in enumerate(u_ for u_ in uids if u_ != uids[1])}
    monkeypatch.setattr(tv, "leg_records", lambda *a, **k: {})
    monkeypatch.setattr(tv, "unit_hosts",
                        lambda u, key=None: _hosts({uids[1]: _fake_inst(uids[1])}, dead))
    seen = {}

    def _gate(n, **kw):
        seen["n"] = n
        return False, {"reason": "ok", "hold": False}
    monkeypatch.setattr(tv, "market_gate", _gate)
    action, readout = tv.gate_for_mode("edge_reps")
    assert action == "clear" and seen["n"] == 3, "three corpses are three units for sale"
    assert readout["units_live"] == [uids[1]]
    # ...and the snapshot must SAY they are replacements, with the state that condemned each box. A reader
    # hours later cannot otherwise tell a never-launched cohort from one whose hosts are corpses.
    rep = {r["unit_id"]: r for r in readout["units_replacing_a_dead_host"]}
    assert set(rep) == set(dead)
    assert all(r["actual_status"] == "exited" and r["dead_instance"] for r in rep.values())


def test_submit_NEVER_destroys_the_corpse_of_a_unit_it_re_places(monkeypatch, capsys):
    """★★ THE LAUNCHER DID DESTROY IT, AND THAT WAS WRONG (7:05 PM ET 2026-07-27).

    `exited` on Vast is routinely a TRANSIENT status, not a dead container. Measured on the step 1 fan-out the
    same evening: three instances read a terminal status and, twenty-one minutes later, all three were
    `running` again at ages 114/112/45 min — with the committed-iteration census proving they had never
    stopped working (warmup@380 -> production@40 on one, +80 production iterations on another).

    Freeing the unit's SLOT on that observation is still right: a duplicate submission costs one instance
    that the dedupe kills next pass, on checkpointed work that is idempotent to resume. Destroying the BOX on
    the same observation costs every hour since its last commit and cannot be undone. Same evidence, opposite
    costs — so this test exists to stop the destroy being re-added as an "obvious" tidy-up."""
    import ternary_vast_launch as tv
    uids = [tv.unit_id(l, s, d, 4.0, 1.0, "edge_reps") for (l, s, d) in tv.units_for("edge_reps")]
    dead = {uids[0]: _fake_inst(uids[0], id=46040507, actual_status="exited", cur_state="stopped")}
    monkeypatch.setenv("VAST_API_KEY", "x")
    monkeypatch.setattr(tv, "leg_records", lambda *a, **k: {})
    monkeypatch.setattr(tv, "unit_hosts",
                        lambda u, key=None: _hosts({x: _fake_inst(x) for x in uids[1:]}, dead))
    monkeypatch.setattr(tv, "blocked_machine_ids", lambda *a, **k: [])
    destroyed = []

    def _req(method, path, key, **kw):
        if method == "DELETE":
            destroyed.append(path)
            return {"success": True}
        raise AssertionError(f"unexpected {method} {path}")
    monkeypatch.setattr(tv, "_vast_request", _req)

    class _Backend:
        def submit(self, j):
            raise RuntimeError("no market in this test — the (absence of a) reap is what is under test")
    monkeypatch.setattr(tv, "get_backend", lambda *a, **k: _Backend())

    tv.submit(mode="edge_reps")
    assert destroyed == [], "a terminal status must never, on one observation, destroy an instance"
    out = capsys.readouterr().out
    assert "NOT destroying it" in out and "often transient" in out, \
        "the launcher must say why it is stepping over the box rather than reaping it"


def test_a_live_replacement_outranks_an_older_corpse_in_the_dedupe(monkeypatch):
    """`collect` kept the OLDEST instance per label — correct when a corpse blocked re-placement forever,
    and exactly backwards now that it does not: after a re-place the oldest record IS the dead one."""
    import gpu_backend as gb
    old_dead = _fake_inst("u", id=1, start_date=100, actual_status="exited", cur_state="stopped")
    new_live = _fake_inst("u", id=2, start_date=200, actual_status="running", cur_state="running")
    group = [old_dead, new_live]
    group.sort(key=lambda x: (not gb.vast_instance_occupies_slot(x), float(x.get("start_date") or 0)))
    assert group[0] is new_live, "destroying the replacement and keeping the corpse is the same bug returning"


def test_the_liveness_predicate_has_exactly_one_home():
    """CLAUDE.md §1. Three sites have now been wrong about this in three different ways; a fourth private
    copy of the status comparison is how they get to disagree again."""
    import os
    import re
    d = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for fn in ("ternary_vast_launch.py",):
        live = "\n".join(l for l in open(os.path.join(d, fn)).read().splitlines()
                         if not l.lstrip().startswith("#"))
        # `collect`'s nudge/reap branch legitimately asks "is this box stopped RIGHT NOW" to decide whether to
        # re-issue a start — a different question from "does it hold the slot". What must not exist is a
        # second answer to the OCCUPANCY question, i.e. a status compare used to build a hosts mapping.
        assert "def unit_hosts" in live
        body = live.split("def unit_hosts", 1)[1].split("\ndef ", 1)[0]
        assert "vast_instance_occupies_slot" in body
        assert not re.search(r'(actual_status|cur_state)\s*(==|!=)', body), \
            f"{fn}: unit_hosts must IMPORT the predicate, never re-type the status comparison"


def test_the_dead_unit_marker_never_labels_a_fresh_retry_host():
    """A unit's `status=failed` is a fact about the LAST attempt, not about the host in front of you.

    Caught on run 30319083631 (2026-07-27, 9:03 PM ET) by the marker itself: two fresh hosts had just been
    rented to RETRY the two dead `calib_lo_to_lo2` units, and the summary line called both of them dead
    while they were still `loading`. This pins the property the fix restores — the marker is keyed on the
    per-instance verdict (which applies `_record_is_newer_than_instance`), never on the unit record alone.
    """
    import inspect
    import ternary_vast_launch as tv
    src = inspect.getsource(tv.collect)
    assert "dead_instances" in src, "the dead-unit marker lost its per-instance keying"
    assert "leg_died_on_this_host=(_iid in dead_instances)" in src, (
        "the marker must read the instance-level verdict; keying it on the unit record re-introduces the "
        "stale-record trap that mislabels a retry host as dead")
    # and the verdict that feeds it must still be the recency-checked one
    assert "_record_is_newer_than_instance" in src


# =============================================================================================================
# THE SUMMARY ROW'S STATE TOKEN — one glyph, one meaning
# =============================================================================================================
# These pin the behaviour of `summary_marker` against the board that actually motivated it: run 30325339528,
# job 90169487825, 2026-07-27 11:14 PM ET. Read the header comment above `summary_marker` for what that board
# really showed (five TRUE-positive ☠ rows, every one of them torn down in the same pass and none of them
# saying so) before changing any expectation here.
_DEAD_REC = {"status": "failed", "rc": 1, "updated_utc": "2026-07-28T02:13:05Z"}


def test_a_destroyed_host_and_a_billing_host_never_render_alike():
    """CLAUDE.md §1's `⚠ PAYING` / `⛔ REFUSED` rule, applied to the teardown decision.

    The 11:14 PM ET board printed `up=running … dph=$0.193 ☠ … its leg is DEAD` for five hosts it had just
    destroyed, because the teardown line lives in the per-instance detail — the part GitHub truncates — while
    the summary is printed last precisely because it survives. A reader concluded money was burning on dead
    hosts and the board offered nothing to contradict them.
    """
    torn = tv.summary_marker(_DEAD_REC, leg_died_on_this_host=True,
                             destroyed={"ok": True, "why": "unit FAILED — nothing left to produce"})
    still = tv.summary_marker(_DEAD_REC, leg_died_on_this_host=True, destroyed=None)
    assert "☠" in torn and "☠" in still, "both rows are genuinely dead legs"
    assert torn != still, "a torn-down host and a billing host must not render alike"
    assert "⛔" in torn and "billing STOPPED" in torn and "$0" in torn
    assert "⛔" not in still and "⚠ STILL BILLING" in still
    # and a teardown that RAISED leaves the meter running — it must read like the billing case, not the
    # stopped one, or a failed DELETE becomes invisible.
    raised = tv.summary_marker(_DEAD_REC, leg_died_on_this_host=True,
                               destroyed={"ok": False, "why": "unit FAILED; DELETE raised HTTPError: 502"})
    assert "⛔" not in raised and "⚠" in raised and "STILL BILLING" in raised


def test_a_stale_failed_record_on_a_fresh_host_is_never_a_skull():
    """The recency gate's correct answer must be VISIBLE, not silent.

    A unit's `status=failed` is a fact about the LAST attempt. When the record predates the host in front of
    you — a fresh retry rented after the crash — the destroy path already refuses to condemn the box
    (`_record_is_newer_than_instance`). The summary used to render that correct restraint as an empty string,
    so "there is a stale failed record here that we are knowingly ignoring" looked exactly like "this unit is
    clean". Three states, three renderings.
    """
    stale = tv.summary_marker(_DEAD_REC, leg_died_on_this_host=False)
    assert "☠" not in stale, "a record older than the host must never render as a dead leg"
    assert "⏳" in stale and "STALE" in stale and "PREDATES" in stale
    assert "2026-07-28T02:13:05Z" in stale, "name the record being ignored, or it cannot be checked"
    # a genuinely clean host carries no state token at all, so ⏳ is not confusable with silence
    assert tv.summary_marker(None, leg_died_on_this_host=False) == ""
    assert tv.summary_marker({"status": "done"}, leg_died_on_this_host=False) == ""


def test_an_advancing_host_under_a_stale_record_says_both():
    """★ THE 46057228 SHAPE — an advancing census must NEVER be labelled dead on an older record.

    Instance 46057228 is the case cited as the marker's false positive. On the real board it was a TRUE
    positive (its leg died ON it at 02:13:05Z against a host started ≈00:16Z — see `summary_marker`'s header),
    but the shape it was BELIEVED to have is the one invariant worth pinning permanently, because it is the
    shape a retry host genuinely takes: committed census rising while an older failed record is still in S3.
    That combination must render as work in progress, never as a corpse.
    """
    row = tv.summary_marker(_DEAD_REC, leg_died_on_this_host=False, progress_advanced=True)
    assert "☠" not in row, "a host whose census is rising is not dead, whatever an older record says"
    assert "⏳" in row, "the stale record is still worth naming"
    assert "▲" in row and "ADVANCING" in row
    assert "⚠" not in row and "⛔" not in row, "nothing was spent or refused here"


def test_a_dead_leg_never_also_claims_to_be_advancing():
    """A stale `prev` in `_lane_state.json` can make a dead unit's census look like it rose — it did exactly
    that for 46057228, whose scalar read 320 against prev=192 while its log had been silent for 61 minutes.
    The dead verdict wins, the same precedence `vast_idle_guard.classify_idle` gives `unit_failed` over
    `progress_advanced`, so the board can never print `▲ ADVANCING` about a leg that is over."""
    row = tv.summary_marker(_DEAD_REC, leg_died_on_this_host=True, progress_advanced=True,
                            destroyed={"ok": True, "why": "unit FAILED — nothing left to produce"})
    assert "▲" not in row and "ADVANCING" not in row
    assert "☠" in row and "⛔" in row


def test_the_teardown_outcome_is_shown_even_when_the_leg_is_healthy():
    """A box destroyed for any other reason — done, runtime backstop, capacity refusal — is money that
    stopped, and the summary is where that has to be readable. Without this a `done` unit's host renders as
    `up=running … dph=$0.22` forever, which is the same misreading in a different costume."""
    row = tv.summary_marker(None, leg_died_on_this_host=False,
                            destroyed={"ok": True, "why": "unit done"})
    assert "⛔" in row and "unit done" in row and "billing STOPPED" in row
    assert "☠" not in row and "⏳" not in row


def test_every_teardown_in_collect_records_its_outcome():
    """One destroy path, one ledger. A raw `_vast_request("DELETE", ...)` added beside `_destroy` would tear
    a box down without the summary ever learning that billing stopped — reintroducing exactly the gap these
    tests exist to close. The dedupe branch is exempt: it runs before the per-instance loop and REMOVES its
    victims from `mine`, so they never reach the summary at all."""
    import inspect
    src = inspect.getsource(tv.collect)
    body = src.split("dead_instances = set()", 1)[1]
    raw = [ln.strip() for ln in body.splitlines() if '_vast_request("DELETE"' in ln]
    assert len(raw) == 1, (
        f"every teardown after the dedupe must go through _destroy so its outcome reaches the summary; "
        f"found {len(raw)} raw DELETE call(s): {raw}")
    assert "destroyed_this_pass[iid]" in body


# ---- RUNG 5a-KS at n = 2 seeds per arm (trimcrae go, 2026-07-30; STRATEGY Open decision 11) ----------------
#
# The lane went from 2 ternary legs to 4 because at one seed per arm `S` has no replicate SD and cannot
# report a null -- its own pre-registered likely outcome. That change has one sharp edge: the stage cache is
# keyed PER SEED and `5aks` sets `stage_required: True`, so a seed whose cache was never seeded is not a slow
# path, it is a dead rented host. These tests guard that edge, and one of them guards a bug that was written
# and caught during the change itself.

def test_5aks_declares_two_seeds_per_arm_and_both_arms_at_each_seed():
    """S is a DOUBLE difference: a seed present on one arm and missing on the other contributes nothing and
    silently unbalances the replicate SD."""
    units = tv.units_for("5aks")
    by_seed = {}
    for leg_id, seed, _dir in units:
        by_seed.setdefault(seed, set()).add(leg_id)
    assert sorted(by_seed) == [0, 1], "n = 2 seeds per arm is the decided configuration"
    assert by_seed[0] == by_seed[1], "every seed must carry BOTH arms, or S loses its pairing"
    assert len(units) == 4


def test_every_declared_seed_gets_its_OWN_stage_cache_key():
    """★ THE BUG THIS CATCHES WAS WRITTEN DURING THE n=2 CHANGE AND CAUGHT BY READING THE CODE BACK.
    `seed_stage_cache` filters units by seed and then built the key with the CALLER's filter value rather
    than the unit's own seed. That was invisible while the filter was a single number; the moment the filter
    became `None` ("every declared seed") it would have written every leg to a seed-None key, leaving BOTH
    real seeds with a cache MISS -- which `stage_required` turns into a dead rented host, not a slow path."""
    keys = {(leg, seed): tv.stage_cache_key(leg, "5aks", seed=seed, bucket="b", prefix="p")
            for leg, seed, _d in tv.units_for("5aks")}
    assert len(set(keys.values())) == len(keys), "each (leg, seed) must map to a DISTINCT cache key"
    for (leg, seed), uri in keys.items():
        other = tv.stage_cache_key(leg, "5aks", seed=1 - seed, bucket="b", prefix="p")
        assert uri != other, f"{leg}: seed {seed} and {1 - seed} share a cache key"


def test_seed_zero_units_are_untouched_so_the_parked_checkpoints_still_resume():
    """The two parked legs hold intact checkpoints. If anything about their identity moved, a resume would
    either start over (losing production/800) or silently resume a different configuration."""
    units = dict(((l, s), d) for l, s, d in tv.units_for("5aks"))
    assert ("5aks_d0_to_d__ternary_nr4a3", 0) in units
    assert ("5aks_d0_to_d__ternary_nr4a1", 0) in units
    for leg in ("5aks_d0_to_d__ternary_nr4a3", "5aks_d0_to_d__ternary_nr4a1"):
        uid = tv.unit_id(leg, 0, "fwd", tv.DEFAULT_TIMESTEP_FS, tv.DEFAULT_WARMUP_TIMESTEP_FS, "5aks")
        assert uid == f"{leg}_r0_dt4.0fs_wu1.0_5aks", "the parked units' identity strings must not move"


def test_the_new_seed_one_legs_are_on_the_watch_list():
    """A lane that launches four legs and watches two has two uncovered -- and assumed-but-absent coverage is
    how ternary-leg-watchdog.yml sat unparseable for days while everyone believed it was watching."""
    import json
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(here, "ternary-vast-watch.json")) as fh:
        watch = json.load(fh)
    watched = {e["unit_id"] for e in watch["watch"]}
    for leg, seed, _d in tv.units_for("5aks"):
        uid = tv.unit_id(leg, seed, "fwd", tv.DEFAULT_TIMESTEP_FS, tv.DEFAULT_WARMUP_TIMESTEP_FS, "5aks")
        assert uid in watched, f"{uid} can be launched but nothing watches it"


# ---------------------------------------------------------------- which legs the $0 pose diagnostic reads
#
# ★★ THE BUG THESE PIN, IN FULL. `gpu-ternary-fep-vast.yml`'s converge job hardcoded `--mode edge` on its
# `--fetch-trajectories` call. nr4a3-program-map.md and the guard audit both instruct that the pose diagnostic be run
# on the CLOSURE TRIANGLE's legs and that `R_binary` NOT be interpreted without it — but the triangle runs at
# a pinned 2 fs under mode `triangle`, and `unit_id` embeds BOTH. So the dispatch that the plan asks for would
# have listed `..._dt4.0fs_wu1.0_edge`, a prefix the triangle never wrote, downloaded nothing, and printed a
# clean convergence summary over zero legs: `resolve_timesteps.__doc__`'s "reports success while measuring
# nothing" shape, arriving green.
def test_converge_task_still_means_the_2b_edge_legs_byte_for_byte():
    """The published RUNG 2b comparison (audit §L.3d, GH run 30210676030) must stay reproducible. Repointing
    `task=converge` at anything else silently changes what an already-cited number was measured on."""
    assert tv.converge_mode_for_task("converge", env={}) == "edge"


def test_the_triangle_converge_task_reaches_the_triangles_own_units():
    """The whole point: the mode must reconstruct the unit ids the triangle ACTUALLY wrote."""
    mode = tv.converge_mode_for_task("triangle-converge", env={})
    assert mode == "triangle"
    dt, wdt = tv.resolve_timesteps(mode)
    ids = {tv.unit_id(leg, seed, d, dt, wdt, mode) for leg, seed, d in tv.units_for(mode)}
    assert ids == {
        "calib_lo_to_lo2__ternary_vhl_r0_dt2.0fs_wu1.0_triangle",
        "calib_lo_to_lo2__binary_vhl_r0_dt2.0fs_wu1.0_triangle",
        "calib_hi_to_lo2__ternary_vhl_r0_dt2.0fs_wu1.0_triangle",
        "calib_hi_to_lo2__binary_vhl_r0_dt2.0fs_wu1.0_triangle",
    }
    # and BOTH binary legs are present, because they are the arms the prereg's prediction is about
    assert sum("__binary_" in i for i in ids) == 2


def test_the_old_hardcoded_edge_mode_could_not_have_seen_a_single_triangle_unit():
    """The regression stated as an identity, so it cannot be argued about. Every id the hardcoded `edge`
    call reconstructs is disjoint from every id the triangle wrote — hence an empty directory, not a
    partial one, and hence a green run that measured nothing rather than an obvious failure."""
    edt, ewdt = tv.resolve_timesteps("edge")
    edge_ids = {tv.unit_id(l, s, d, edt, ewdt, "edge") for l, s, d in tv.units_for("edge")}
    tdt, twdt = tv.resolve_timesteps("triangle")
    tri_ids = {tv.unit_id(l, s, d, tdt, twdt, "triangle") for l, s, d in tv.units_for("triangle")}
    assert not (edge_ids & tri_ids)
    assert all(i.endswith("_dt4.0fs_wu1.0_edge") for i in edge_ids)
    assert all(i.endswith("_dt2.0fs_wu1.0_triangle") for i in tri_ids)


def test_an_unregistered_converge_task_raises_instead_of_guessing():
    """Adding a converge task to the workflow's options without a map entry must fail the STEP, loudly.
    A default would put us straight back in the failure above, one rename later."""
    with pytest.raises(ValueError):
        tv.converge_mode_for_task("triangle-conv", env={})
    with pytest.raises(ValueError):
        tv.converge_mode_for_task("", env={})


def test_the_env_override_is_validated_not_trusted():
    """`TVAST_CONVERGE_MODE` buys a mode without spending a dispatch-input slot (the lane is AT GitHub's cap
    of 10). A typo in it must be an error, never a silent fallback to `edge` — which would look exactly like
    a correct run."""
    assert tv.converge_mode_for_task("converge", env={"TVAST_CONVERGE_MODE": "triangle"}) == "triangle"
    assert tv.converge_mode_for_task("converge", env={"TVAST_CONVERGE_MODE": "  "}) == "edge"
    with pytest.raises(ValueError):
        tv.converge_mode_for_task("converge", env={"TVAST_CONVERGE_MODE": "triangel"})


def test_every_registered_converge_mode_is_a_real_mode():
    for task, mode in tv.CONVERGE_TASK_MODES.items():
        assert mode in tv.MODES, f"task {task} maps to unknown mode {mode}"


# ---------------------------------------------------------------- the workflow must stay wired to the map
def _vast_workflow_text():
    here = os.path.abspath(__file__)                       # research/modalities/tests/<this file>
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(here))))
    with open(os.path.join(root, ".github/workflows/gpu-ternary-fep-vast.yml")) as fh:
        return fh.read()


def test_the_converge_job_no_longer_hardcodes_a_mode_on_fetch_trajectories():
    """The literal defect. `--mode edge --fetch-trajectories` is the line that made the diagnostic
    un-runnable on any lane but RUNG 2b's."""
    text = _vast_workflow_text()
    assert "--mode edge --fetch-trajectories" not in text, (
        "the converge job hardcodes `--mode edge` again — it can then only ever analyse the 4 fs RUNG 2b "
        "legs, and any other lane's dispatch returns an empty directory and a green run")
    assert "--converge-mode-for-task" in text, "the mode must be DERIVED from the dispatched task"


def test_every_converge_task_in_the_workflow_has_a_registered_mode():
    """The allowlist test in test_workflows_parse.py stops a task from silently downgrading to `test`.
    This is the same guard one layer in: a dispatchable converge task with no mode would reach the job and
    then have to guess which legs it is about."""
    import re
    text = _vast_workflow_text()
    m = re.search(r"^\s*options: \[(.+?)\]", text, re.M)
    assert m, "could not read the task input's options"
    options = [o.strip() for o in m.group(1).split(",")]
    converge_tasks = [o for o in options if "converge" in o]
    assert converge_tasks, "no converge task is dispatchable at all"
    assert set(converge_tasks) == set(tv.CONVERGE_TASK_MODES), (
        f"the workflow offers {sorted(converge_tasks)} but CONVERGE_TASK_MODES registers "
        f"{sorted(tv.CONVERGE_TASK_MODES)} — one of them will analyse the wrong legs or fail at dispatch")
    # ...and the job's own `if:` must admit exactly those tasks, or a dispatchable one is a no-op run.
    gate = re.search(r"\n  converge:\n(?:.*\n)*?\s*if: (.+)\n", text)
    assert gate, "could not find the converge job's if: condition"
    for t in converge_tasks:
        assert f"'{t}'" in gate.group(1), f"task {t} is dispatchable but the converge job would skip it"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# A `done` RECORD THAT PREDATES THE HOST MUST NOT REAP IT (2026-08-01)
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# MEASURED, not hypothetical. The `.chk` prune shakeout rented instance 46459452 at 10:02 PM ET on
# 2026-07-31 and produced NOTHING — no `[prune]` line, no `chk_pruned` manifest, no `run.log`, not even a
# `status.json`. The 10:04:46 PM collect says why, verbatim:
#
#     vast 46459452 (...-f495e0fc) loading up=0.04h ... msg='0eee12ace5f3: Verifying Checksum'
#       -> destroying 46459452 (unit done)
#
# `finished = uid in done` was true because that unit's leg.json had said `status=done` since 2026-07-26 —
# the ORIGINAL smoke, five days earlier. Our own reaper killed a host 2 min 23 s in, mid image-pull, before
# it executed one line of the entry script. Every artifact then read byte-identically to "no rental ever
# happened", which is what made it cost a forensic rather than a glance.
#
# It generalises to every deliberate re-run of a landed unit — a shakeout, a re-measurement, a
# supersede-and-recompute — so this is the gate on the whole `.chk` prune ladder, not a smoke quirk.

def test_the_done_reap_requires_the_result_to_postdate_the_host():
    """`crashed` has been guarded by `_record_is_newer_than_instance` since the protfep lane learned the
    same lesson about stale FAILED records. `finished` never was — the identical question about the
    identical kind of stale record."""
    src = open(tv.__file__).read()
    body = src[src.index("    for i in mine:"):src.index("    dead_instances = set()")] \
        if "    dead_instances = set()" in src[src.index("    for i in mine:"):] \
        else src[src.index("    for i in mine:"):]
    body = src[src.index("        finished_record = uid in done"):src.index("        row_record[iid] = _rec")]
    assert "_record_is_newer_than_instance(_done_rec, i)" in body, (
        "the 'unit done' reap is back to trusting a leg.json of any age — a re-run of a landed unit will "
        "be destroyed mid image-pull again")
    assert "finished = bool(finished_record and _done_is_ours)" in body


def test_declining_to_reap_on_a_stale_done_record_is_ANNOUNCED():
    """A guard that silently stops firing is indistinguishable from a guard that was removed — and this one
    used to destroy. The pass must state that it saw a done record and declined to act on it."""
    src = open(tv.__file__).read()
    body = src[src.index("        finished_record = uid in done"):src.index("        row_record[iid] = _rec")]
    assert "if finished_record and not finished:" in body
    assert "written BEFORE this host started" in body


def test_the_reap_reason_chain_still_puts_unit_done_first():
    """Ordering is load-bearing for the REASON, not just the action: a leg that landed stops writing its log
    by design, so on the next poll it also reads WEDGED. 'unit done' must win, or the destroy is attributed
    to the idle guard and the readout lies about why."""
    src = open(tv.__file__).read()
    why = src[src.index('        why = ("unit done" if finished else'):]
    why = why[:why.index("\n        if autostop")]
    assert why.index('"unit done"') < why.index("idle guard")
