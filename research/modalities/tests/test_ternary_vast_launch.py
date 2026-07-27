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
    at_205 = 2.048 * basis
    assert round(at_205 * ns_unit * n, 2) <= ceiling, "the night's board did clear the DOLLAR ceiling"
    assert 2.048 > tv.MARKET_MAX_RATIO_VS_BASIS, "...and must still be refused on the RATIO ceiling"
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
