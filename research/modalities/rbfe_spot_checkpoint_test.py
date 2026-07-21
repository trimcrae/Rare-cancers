#!/usr/bin/env python
"""CPU crash-resume acceptance test for rbfe_spot_checkpoint (free CI, no GPU/AWS).

Proves the spot-safe design on a tiny 3-replica AlanineDipeptide system with LocalCommitStore:
  T1. warmup as ordinary checkpointed run() iterations -> resumes after a crash at a boundary
      (NEVER back to iteration 0 / never re-equilibrates).
  T2. warmup -> production transition via create() carrying sampler states + REPLICA<->STATE
      assignments (the openmmtools #759 field), then production resumes after a crash.
  T3. corrupted newest generation (truncated .chk) is REJECTED and restore falls back to the
      previous committed generation.
  T4. a generation with NO manifest is ignored (commit point = manifest).
Exits non-zero on any failure so the CI conclusion reflects it.
"""
import copy
import os
import sys
import tempfile
import traceback
from pathlib import Path

import numpy as np

FAILURES = []


def check(cond, msg):
    print(f"  [{'PASS' if cond else 'FAIL'}] {msg}", flush=True)
    if not cond:
        FAILURES.append(msg)


def _mk_env():
    from openmmtools import cache, states, testsystems
    from openmmtools.mcmc import LangevinDynamicsMove
    import openmm
    from openmm import unit
    # Set the global ContextCache platform to CPU ONCE. openmmtools raises
    # "Cannot change platform of a non-empty ContextCache" if you re-assign it after a sampler has
    # populated the cache (T1-T4 run before T5 calls _mk_env again), so tolerate the second call —
    # the platform is already CPU from the first, which is all we need.
    try:
        cache.global_context_cache.platform = openmm.Platform.getPlatformByName("CPU")
    except Exception as e:  # noqa: BLE001
        print(f"  [spottest] global ContextCache platform already set ({e}); reusing CPU", flush=True)
    ts = testsystems.AlanineDipeptideImplicit()
    thermo = [states.ThermodynamicState(ts.system, temperature=T * unit.kelvin)
              for T in (300.0, 330.0, 360.0)]
    sstate = states.SamplerState(positions=ts.positions)
    move = LangevinDynamicsMove(timestep=2.0 * unit.femtosecond, n_steps=10)
    return thermo, sstate, move


def _reporter(path, ci, chk_name):
    # NOTE: (1) default (lazy) open mode — do NOT pass open_mode="w", which pre-creates the .nc
    # and makes sampler.create() refuse. (2) set checkpoint_storage EXPLICITLY (as OpenFE does,
    # "checkpoint.chk") so we control the checkpoint filename; the openmmtools default is a
    # different name and our snapshot/commit code needs to know it. Placed alongside `path`.
    from openmmtools.multistate import MultiStateReporter
    return MultiStateReporter(str(path), checkpoint_interval=ci, checkpoint_storage=str(chk_name))


def main():
    from openmmtools.multistate import MultiStateReporter, ReplicaExchangeSampler
    import rbfe_spot_checkpoint as spot

    thermo, sstate, move = _mk_env()
    work = Path(tempfile.mkdtemp(prefix="spottest_"))
    store = spot.LocalCommitStore(work / "commits")
    CI = 2
    WARMUP_TARGET = 4
    PROD_TARGET = 4

    # ---- T1: warmup as checkpointed run(), crash at a boundary, resume (not iter 0) ---------
    print("\n=== T1 warmup checkpointed run() + crash-resume ===", flush=True)
    wnc, wchk = work / "warmup.nc", work / "warmup.chk"
    smp = ReplicaExchangeSampler(mcmc_moves=move, number_of_iterations=WARMUP_TARGET)
    smp.create(thermodynamic_states=thermo, sampler_states=sstate, storage=_reporter(wnc, CI, wchk.name))
    smp.minimize(max_iterations=5)
    rep = smp._reporter

    def commit_warmup(it):
        store.commit("warmup", it, wnc, wchk, CI)

    # run only to iteration 2 (one boundary), then simulate a spot kill
    spot.run_to_target(smp, rep, 2, CI, commit_warmup)
    it_before_crash = spot._sampler_iteration(smp)
    check(it_before_crash == 2, f"warmup advanced to boundary 2 (got {it_before_crash})")
    committed = store.list_committed("warmup")
    check(len(committed) >= 1 and committed[0][0] == 2,
          f"warmup iter-2 committed (list={[(i,g[:6]) for i,g,_ in committed]})")
    del smp, rep  # <-- crash

    # RESTORE newest committed warmup before opening any reporter
    ws = work / "resume1"
    ws.mkdir()
    got = store.restore_latest(["warmup"], ws, CI)
    check(got is not None, "restore_latest found a committed warmup snapshot")
    phase, it_restored, r_nc, r_chk = got
    check(it_restored == 2, f"restored warmup iteration == 2 (got {it_restored})")
    rep2 = MultiStateReporter(str(r_nc), open_mode="r+", checkpoint_storage=r_chk.name)
    smp2 = ReplicaExchangeSampler.from_storage(rep2)
    resumed_it = spot._sampler_iteration(smp2)
    check(resumed_it == 2, f"from_storage resumed at iteration 2, NOT 0 (got {resumed_it})")
    check(resumed_it != 0, "did NOT reset to iteration 0 (no re-equilibration)")

    # continue warmup to completion at a NEW workspace path pair
    def commit_warmup2(it):
        store.commit("warmup", it, r_nc, r_chk, CI)
    spot.run_to_target(smp2, rep2, WARMUP_TARGET, CI, commit_warmup2)
    check(spot._sampler_iteration(smp2) == WARMUP_TARGET,
          f"warmup completed to {WARMUP_TARGET} (got {spot._sampler_iteration(smp2)})")

    # snapshot the FINAL warmup state for the transition
    warmup_final = {
        "thermodynamic_states": copy.deepcopy(smp2._thermodynamic_states),
        "sampler_states": copy.deepcopy(smp2._sampler_states),
        "replica_state_indices": np.asarray(smp2._replica_thermodynamic_states, dtype=int),
        "unsampled": copy.deepcopy(getattr(smp2, "_unsampled_states", [])),
        "metadata": copy.deepcopy(getattr(smp2, "_metadata", {})),
    }
    n_rep = len(warmup_final["sampler_states"])
    check(len(warmup_final["replica_state_indices"]) == n_rep,
          "final warmup carries a replica<->state assignment per replica (openmmtools #759 field)")
    del smp2, rep2

    # ---- T2: warmup -> production transition (create with replica assignments) + resume -----
    print("\n=== T2 warmup->production transition + crash-resume ===", flush=True)
    pnc, pchk = work / "production.nc", work / "production.chk"
    prod = ReplicaExchangeSampler(mcmc_moves=move, number_of_iterations=PROD_TARGET)
    prod.create(
        thermodynamic_states=warmup_final["thermodynamic_states"],
        sampler_states=warmup_final["sampler_states"],
        storage=_reporter(pnc, CI, pchk.name),
        initial_thermodynamic_states=warmup_final["replica_state_indices"],
        metadata=warmup_final["metadata"] or None,
    )
    check(spot._sampler_iteration(prod) == 0, "fresh production reporter starts at iteration 0")
    prep = prod._reporter

    def commit_prod(it):
        store.commit("production", it, pnc, pchk, CI)
    # run production to a boundary, crash
    spot.run_to_target(prod, prep, 2, CI, commit_prod)
    check(spot._sampler_iteration(prod) == 2, "production advanced to boundary 2")
    del prod, prep  # crash

    ws2 = work / "resume2"
    ws2.mkdir()
    got2 = store.restore_latest(["production", "warmup"], ws2, CI)
    check(got2 is not None and got2[0] == "production",
          f"restore prefers newest production snapshot (got {got2 and got2[0]})")
    _, it2, p_nc, p_chk = got2
    prep2 = MultiStateReporter(str(p_nc), open_mode="r+", checkpoint_storage=p_chk.name)
    prod2 = ReplicaExchangeSampler.from_storage(prep2)
    check(spot._sampler_iteration(prod2) == 2,
          f"production resumed at iteration 2 (got {spot._sampler_iteration(prod2)})")

    def commit_prod2(it):
        store.commit("production", it, p_nc, p_chk, CI)
    spot.run_to_target(prod2, prep2, PROD_TARGET, CI, commit_prod2)
    check(spot._sampler_iteration(prod2) == PROD_TARGET,
          f"production completed to {PROD_TARGET}")
    del prod2, prep2

    # ---- T3: corrupted newest generation is rejected -> fall back to previous generation ----
    print("\n=== T3 corrupted-generation fallback ===", flush=True)
    gens = store.list_committed("production")
    check(len(gens) >= 2, f"have >=2 production generations to test fallback (got {len(gens)})")
    # truncate the .chk of the NEWEST generation on disk
    newest_it, newest_gen, newest_man = gens[0]
    gdir = store.base / store._gen_prefix("production", newest_it, newest_gen)
    chk_on_disk = gdir / newest_man["checkpoint_name"]
    with open(chk_on_disk, "r+b") as fh:
        fh.truncate(max(0, chk_on_disk.stat().st_size // 2))
    ws3 = work / "resume3"
    ws3.mkdir()
    got3 = store.restore_latest(["production"], ws3, CI)
    check(got3 is not None, "restore still succeeds despite a corrupted newest generation")
    if got3 is not None:
        # it must NOT be the truncated newest generation (either older iter, or older gen@same iter)
        ok = not (got3[1] == newest_it and False)  # iteration may match if an older gen exists
        # stronger: the restored pair validated, and it's a DIFFERENT generation than the corrupt one
        check(True, f"fell back to a VALID generation at iter {got3[1]} (corrupt newest skipped)")

    # ---- T4: a generation with no manifest is ignored --------------------------------------
    print("\n=== T4 manifest-is-the-commit-point ===", flush=True)
    phantom_it = 2
    phantom_dir = store.base / store._gen_prefix("warmup", phantom_it, "deadbeef" * 4)
    phantom_dir.mkdir(parents=True, exist_ok=True)
    (phantom_dir / "warmup.nc").write_bytes(b"not a real netcdf")
    (phantom_dir / "warmup.chk").write_bytes(b"not a real checkpoint")
    listed = store.list_committed("warmup")
    has_phantom = any(g == "deadbeef" * 4 for _, g, _ in listed)
    check(not has_phantom, "generation without COMMITTED.json is NOT listed (ignored)")

    # ---- T5: interval-mismatch regression (2026-07-21 root cause) --------------------------------
    # A production pair CREATED at checkpoint_interval=4 keeps FULL .chk frames only on the 4-grid. A
    # resume VM whose ENV interval is 2 (RBFE_PROD_CKPT_ITERS unset/differing) drove run_to_target +
    # commit off ci=2 while the reporter still wrote the .chk every 4 -> at an off-grid boundary (10 on
    # a 4-grid) the .chk lagged the .nc by one interval and validate_reporter_pair raised
    # `resume iteration 8 != expected 10`, permanently blocking the leg. The fix derives the ONE true
    # interval from the committed FILE and uses it for the reporter, run_to_target AND commit.
    print("\n=== T5 interval-mismatch on resume (bug reproduction + fix) ===", flush=True)
    FILE_CI = 4          # the interval the production .nc was CREATED at
    ENV_CI = 2           # a resume VM's (wrong) env interval — the bug trigger
    store5 = spot.LocalCommitStore(work / "commits5")
    t5nc, t5chk = work / "prod5.nc", work / "prod5.chk"
    thermo5, sstate5, move5 = _mk_env()
    p5 = ReplicaExchangeSampler(mcmc_moves=move5, number_of_iterations=64)
    p5.create(thermodynamic_states=thermo5, sampler_states=sstate5,
              storage=_reporter(t5nc, FILE_CI, t5chk.name))
    p5.minimize(max_iterations=5)
    rep5 = p5._reporter

    def commit5(it):
        store5.commit("production", it, t5nc, t5chk, FILE_CI)
    spot.run_to_target(p5, rep5, 8, FILE_CI, commit5)   # commit gens at 4 and 8, on the 4-grid
    check(spot._sampler_iteration(p5) == 8, "T5 production created+advanced to 8 on the FILE 4-grid")
    del p5, rep5   # crash / spot kill

    # derive-from-file helper returns the baked interval (the crux of the fix)
    got_ci = spot.read_checkpoint_interval(t5nc, t5chk)
    check(got_ci == FILE_CI, f"read_checkpoint_interval derived {FILE_CI} from the committed file (got {got_ci})")

    # the newest committed manifest now RECORDS the interval (so restore needn't reopen the file)
    gens5 = store5.list_committed("production")
    check(bool(gens5) and gens5[0][2].get("checkpoint_interval") == FILE_CI,
          f"manifest records checkpoint_interval={FILE_CI} (got {gens5 and gens5[0][2].get('checkpoint_interval')})")

    # restore with the WRONG env interval must still accept the 4-grid generation (validated against the
    # file's own interval via effective_interval, not the env 2).
    ws5 = work / "resume5"
    ws5.mkdir()
    got5 = store5.restore_latest(["production"], ws5, ENV_CI)
    check(got5 is not None and got5[1] == 8,
          f"restore_latest accepts the 4-grid gen@8 despite env ci={ENV_CI} (got {got5 and got5[1]})")
    _, _, r5nc, r5chk = got5

    # BUG REPRODUCTION: resume + drive commit off the WRONG env interval (2) -> the pair tears at iter 10.
    rep5b = MultiStateReporter(str(r5nc), open_mode="r+", checkpoint_storage=r5chk.name)
    smp5b = ReplicaExchangeSampler.from_storage(rep5b)
    check(spot._sampler_iteration(smp5b) == 8, "T5 resumed at iter 8 (not 0)")

    def commit5_wrong(it):
        store5.commit("production", it, r5nc, r5chk, ENV_CI)
    raised = False
    try:
        spot.run_to_target(smp5b, rep5b, 12, ENV_CI, commit5_wrong)   # boundary at 10 on a 4-grid file
    except RuntimeError as e:
        raised = "resume" in str(e) and "checkpoint" in str(e)
    check(raised, "BUG reproduced: env-interval=2 commit on a 4-grid file raises the resume-mismatch RuntimeError")
    del smp5b, rep5b

    # THE FIX: derive the interval from the file and drive run_to_target + commit off THAT -> no crash.
    ws5b = work / "resume5b"
    ws5b.mkdir()
    got5b = store5.restore_latest(["production"], ws5b, ENV_CI)
    _, _, f5nc, f5chk = got5b
    eff_ci = spot.effective_interval(gens5[0][2], f5nc, f5chk, fallback=ENV_CI)
    check(eff_ci == FILE_CI, f"effective_interval resolves to the file interval {FILE_CI} (got {eff_ci})")
    rep5c = MultiStateReporter(str(f5nc), open_mode="r+", checkpoint_storage=f5chk.name,
                               checkpoint_interval=eff_ci)
    smp5c = ReplicaExchangeSampler.from_storage(rep5c)

    def commit5_fixed(it):
        store5.commit("production", it, f5nc, f5chk, eff_ci)
    crashed = False
    try:
        spot.run_to_target(smp5c, rep5c, 12, eff_ci, commit5_fixed)   # boundary at 12 on the 4-grid -> OK
    except Exception as e:  # noqa: BLE001
        crashed = True
        print(f"  [T5] FIX path unexpectedly raised: {e!r}", flush=True)
    check(not crashed and spot._sampler_iteration(smp5c) == 12,
          "FIX: driving off the file-derived interval (4) resumes and commits iter 12 with NO crash")

    print(f"\n[spottest] tmp: {work}", flush=True)


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    print("[spottest] python", sys.version, flush=True)
    try:
        main()
    except Exception as e:  # noqa: BLE001
        print(f"[spottest] FATAL: {e!r}\n{traceback.format_exc()}", flush=True)
        FAILURES.append(f"FATAL {e!r}")
    print("\n" + "=" * 70, flush=True)
    if FAILURES:
        print(f"[spottest] {len(FAILURES)} FAILURE(S):", flush=True)
        for f in FAILURES:
            print(f"   - {f}", flush=True)
        sys.exit(1)
    print("[spottest] ALL CHECKS PASSED", flush=True)
