# FEP status + one-step resume (2026-07-03, overnight)

## ⛔ BLOCKER (confirmed ~05:5x UTC after a container restart): dispatch + all AWS/log reads are gated on GitHub MCP
Everything that advances the FEP empirically routes through the GitHub MCP connector, which is **down
(needs interactive re-auth)**. I verified from inside the container that there is **no side channel**:
- **`GH_TOKEN` in-env can READ the Actions API** (run/job status) **but CANNOT dispatch** — `workflow_dispatch`
  returns `403 Resource not accessible by integration` (read-only integration token).
- **Job-log downloads are policy-blocked** — the REST logs endpoint 302-redirects to
  `productionresultssa7.blob.core.windows.net`, which the egress proxy rejects with `403 CONNECT`
  (org policy; do not retry). So I cannot read a run's logs via curl — only MCP `get_job_logs` (server-side text)
  works, and it's down with the connector.
- **In-env AWS creds are INVALID** (`sts:GetCallerIdentity` → `InvalidClientTokenId`). S3 (the metad `fes.dat`,
  the FEP LEaP logs) is reachable **only from inside a GitHub Action**, which has its own creds. So no direct
  S3 read either.
- **git commit/push still works** (separate git credentials) — all code below is committed + pushed to
  `claude/red-team-degrader-paper-l1hukn`.

**To resume: re-authorize the GitHub connector** (claude.ai connector settings), then dispatch the one command
in "RESUME" below. That single dispatch restores BOTH dispatch and `get_job_logs`.

## ✅ SOLVENT-leg LEaP failure DIAGNOSED + FIXED (2026-07-03 06:26Z) — it was the WATER MODEL, not the ligand
The `_dump_setup_logs` instrumentation surfaced the real `solvent.leap.log`: **3262 errors, all**
`For atom (.R<WAT ...>.A<EPW 4>) could not find vdW parameters for type (EP)`, plus Yank's own warning
`solvent_model tip4pew may not work for loaded leaprc.water.X files`. Root cause: **Yank defaults
`solvent_model` to tip4pew (4-point water with an EPW extra-point of type EP), but the YAML loaded
`leaprc.water.tip3p` (3-point, no EP params)** → every water fails. The ligand was fine all along
(`lig.frcmod` = normal GAFF). The gaff/gaff2 + obabel-valence hypotheses were WRONG — which is exactly why
the log-first discipline mattered. **Fix: pin `solvent_model: tip3p` in the `solvents.pme` block** so the built
water matches the loaded leaprc.water.tip3p. Committed; re-dispatched single-shard to validate past LEaP.

## (historical) Current FEP state: single-shard shakeout, one error left — the SOLVENT-leg LEaP failure
The last real single-shard run got through imports → antechamber charges → and died in Yank's tleap at system
setup: `RuntimeError: Solvent pme: Some things went wrong with LEaP`. The failing leg is the **solvent leg
(ligand-only in water)**, so this is a **ligand-parametrization** problem, not the receptor. Yank's error is an
opaque wrapper; the real diagnostic (missing GAFF param? antechamber valence? obabel bond mis-perception?) is in
a `*.leap.log` file the harness never surfaced.

**Fix staged this session (diagnostics, non-behavior-changing):** `nr4a3_fep.py :: _dump_setup_logs(out_dir)` now
runs on any `yank script` failure and echoes the tail of every setup log (`*.leap.log`, antechamber logs,
`tleap.in`, `*.frcmod`) to stdout — so the **next** single dispatch reveals the exact LEaP cause in
`get_job_logs`, no S3 round-trip. Leading hypotheses to check against that log, most→least likely:
  1. **gaff/gaff2 mismatch** — YAML loads `leaprc.gaff2` but Yank's antechamber may type the ligand as GAFF1;
     if the log says "could not find parameter", switch the leap param to `leaprc.gaff` (one line in `_yank_yaml`).
  2. **obabel bond mis-perception** — the docked pose is heavy-atom-only; `obabel -h` can mis-order an aromatic
     bond → antechamber valence error. Fix would be to rebuild ligand topology from the known SMILES and borrow
     only the pose coordinates.
  denovo_401 is plain C/H/O (methoxymethyl, phenyl, cyclopentane, t-Bu, 2° alcohol) — GAFF2 covers it fully, so
  genuinely-missing params is unlikely; typing/valence is the more probable cause. **Read the surfaced log first;
  do not blind-change parametrization** (a wrong guess wastes the single validation shard).

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
Re-run the SAME single-shard validation. It will now hit the same LEaP error BUT dump the real setup log — read
it via MCP `get_job_logs`, apply the matching fix above, re-dispatch. Once it reaches HREX sampling, kill and
fan out `n_shards=3` (full FEP). Single-shard validation of the *run* path (GPU/OpenCL + LEaP + Boresch + HREX —
the only thing the free env-check can't test):
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
