# FEP status + one-step resume (2026-07-03, overnight)

## ⛔ BLOCKER (as of ~04:10 UTC): GitHub MCP token expired
Workflow **dispatch** and **job-log reads** go through the GitHub MCP server, whose token expired mid-session
(non-interactive, so I can't re-auth it). **git commit/push still works** (separate credentials), so all code
below is committed and pushed to `claude/red-team-degrader-paper-l1hukn`. **To resume: re-authorize the GitHub
connector** (claude.ai connector settings), then dispatch the one command in "RESUME" below.

## FEP is READY — the env is fully validated, only the dispatch is blocked
The FEP was rewritten on **Yank** (absolute binding FEP: explicit solvent, Boresch restraints + standard-state
correction, HREX, MBAR — one experiment per receptor). Getting the unmaintained yank 0.25.2 (2020) to build on
a modern SageMaker image took a single-shard shakeout that resolved **7 env/config issues**, each caught for
~$0.20 (never fanned out on an unproven env). The **free deep env-check
(`.github/workflows/yank-env-check.yml`, run 28637753417) PASSED** — the exact fep env imports yank cleanly:
`python=3.9 + yank 0.25.2 + openmmtools=0.21.2 + openbabel + setuptools<81`, with `ExperimentBuilder` +
`alchemy._ALCHEMICAL_REGION_ARGS` present.

### The 7 fixes (all in `sagemaker_src/entry_fep.py` + `nr4a3_fep.py`, committed)
1. **PYTHONPATH leak** — clear `PYTHONPATH` for `conda run -n fep` (base container's numpy 1.x shadowed the env's).
2. **openmmtools=0.21.2** — yank needs `alchemy._ALCHEMICAL_REGION_ARGS`, removed in 0.25 (conda's loose pin).
3. **SDF→MOL2** — yank's SDF reader needs commercial OpenEye; MOL2 path is AmberTools-only.
4. **openbabel `-h`** — the docked pose is heavy-atom-only; antechamber mistyped carbons as sp → add explicit H.
5. **ref + git_ref BOTH = feature branch** — `entry_fep.py` is uploaded from the workflow's `ref` checkout,
   `nr4a3_fep.py` from the `git_ref` clone; if they differ the env + code diverge.
6. **setuptools<81** — yank imports legacy `pkg_resources`, removed in setuptools≥81 (openbabel bumped it).
7. **python=3.9** — yank uses `collections.MutableMapping`, removed in py3.10 (openbabel/setuptools pulled 3.10+).

## ▶ RESUME (one dispatch, once MCP is re-authorized)
Single-shard validation of the *run* path (GPU/OpenCL + LEaP + Boresch + HREX — the only thing the free
env-check can't test). If it reaches HREX sampling, kill it and fan out `n_shards=3` (full FEP):
```
gpu-fep-aws.yml  mode=run  n_shards=1  ligand=denovo_401  n_windows=12
                 target_ddg=-1.0  z=1.0  min_windows=6
                 ref=claude/red-team-degrader-paper-l1hukn  git_ref=claude/red-team-degrader-paper-l1hukn
# on sampling:  fep-stop-aws.yml (kill the 1-shard) then the same with n_shards=3  → full 3-receptor FEP (~$35, ~9h)
# monitor early-stop:  gpu-fep-aws.yml mode=monitor   |   final ΔΔG:  gpu-fep-aws.yml mode=reduce
```
Reduce (`report_fep.py`) + early-stop monitor (`fep_monitor.py`) are already adapted to the per-receptor Yank
ΔG_bind model (unit-tested). `selectivity_ddg` gives NR4A3-vs-NR4A1/NR4A2 ΔΔG (negative = NR4A3-selective).

## Also pending on MCP (GPU-result folding)
- **metad** (cryptic-pocket opening free energy) — the ~10h Processing job was due ~07:00 UTC. Read `fes.dat`
  from `s3://<bucket>/nr4a3-metad` (via a report/status workflow) → converged ΔG(apo→open) + barrier → fold
  into paper §2.1–§2.2 (firms up the provisional Gate-3 numbers).
