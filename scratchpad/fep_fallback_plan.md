# FEP runbook — live state (2026-07-04)

## ⛔ HARD DECISION (trimcrae, 2026-07-04): if the CURRENT NR4A3 run FAILS → DONE WITH YANK.
Do NOT restart NR4A3 on Yank. Switch the WHOLE ΔΔG (all 3 legs) to a modern stack with a spot-friendly
execution model — OpenFE per-unit OR independent-λ-window openmmtools (small per-unit checkpoints, no
monolithic .nc). Ride the current run to completion; a clean finish keeps us on Yank for THIS result only.

## 🚫 NO-RESUME WATCH (trimcrae, 2026-07-04): if the current NR4A3 job spot-INTERRUPTS, do NOT let it auto-resume
on Yank — StopTrainingJob it and switch to modern stack. Can't disable managed-spot resume on a live job, so
MONITOR ~every 40min: if status resets to Starting/Downloading or iteration drops toward 500 → `fep-status
stop_names=nr4a3-fep-sn-0-2026-07-04-15-58-00-010`. (A crash/exit-failure does NOT auto-resume — only spot
interruptions do.) Clean finish ~11:12pm ET 07-04 → read verdict. ALL TIMES ET (EDT=UTC-4).

## Goal
Converged selectivity **ΔΔG = ΔG_bind(NR4A3) − ΔG_bind(NR4A1/NR4A2)** for lead `denovo_401`.
Negative ΔΔG = NR4A3-selective (the paper's headline). Yank ABFE, one experiment per receptor.

## Where we are RIGHT NOW (updated ~13:40 UTC)
- **Bug 1 (numba):** openmmtools 0.21.2 numba `_mix_all_replicas_numba` crashed at ~iter 630 with
  `NumbaTypeError: Unsupported array type: numpy.ma.MaskedArray`. Fix = `replica_mixing_scheme: swap-neighbors`
  (pure-Python neighbor swap) + `online_analysis_interval: null` (disable online MBAR, likely masked-array src).
- **Bug 2 (schema, hit on g5):** `replica_mixing_scheme` is a ReplicaExchangeSampler CTOR arg, NOT a valid
  `options:` key — Yank died with `YamlParseError: found unknown parameter replica_mixing_scheme` in ~seconds
  (job nr4a3-fep-sn-0-...-11-16-46, wrote nothing → ckpt/0 empty). **Fix = configure sampler EXPLICITLY via
  `mcmc_moves:` + `samplers:` headers** (samplers schema is allow_unknown → ctor args pass through), reference
  via `experiments: sampler: sampler`. **VALIDATED FREE** via yank-env-check (ExperimentBuilder parse →
  `YAML_SCHEMA_OK`, only a no-OpenCL-platform error AFTER schema validation, expected on CPU). Commit 8b965ad.
  (Also fixed a yank-env-check silent no-op: `conda run python - <<EOF` doesn't forward stdin → validated
  nothing → false green. Now runs from a file + PASS-marker grep guard.)
- **NR4A3 validation run RE-DISPATCHED ~13:40 UTC:** `gpu-fep-aws.yml` mode=run, **tag `nr4a3-fep-sn`**
  (reused — prior prefix empty), only_receptors=nr4a3, phase=full, spot=1, git_ref=branch. Runs pilot(0→500)
  then prod(500→3000). ~25 min setup + ~12 h HREX @ ~12.8 s/iter on 1 A10G spot (once an instance is acquired).
- **THE GATE:** this run must sample **past iter 630** (old numba crash point) to prove the fix. Clock starts
  when an instance is acquired (spot capacity was intermittently out earlier today). Intermediate pilot ΔG at
  ~2 h (500 iters). Old superseded number: nr4a3-fep-trim pilot ΔG −10.5 ± 2.3 (swap-ALL, proves setup only).
- **Old banked number (do NOT confuse):** nr4a3-fep-trim/ckpt/0/nr4a3.json = pilot ΔG **−10.5 ± 2.3** from the
  swap-ALL run that then crashed. Proves setup+binding; does NOT prove the fix. Superseded by nr4a3-fep-sn.

## ★ SAMPLING at last (2026-07-04 ~16:28 UTC) — all 4 bugs cleared
Job `nr4a3-fep-sn-0-2026-07-04-15-58-00-010` **InProgress/Training**, live HREX at **iter 106/500** (pilot),
~12.5 s/iter, "swap only neighboring replicas" + "No online analysis" confirmed. Bugs cleared: (1) numba →
swap-neighbors; (2) schema → samplers header; (3) LEaP exit 31 → `_clean_pdb_for_leap` pure-python receptor
clean (pdb4amber absent); (4) online analysis disabled. Pilot ΔG ETA ~17:49 UTC → auto-extends to prod (3000).
iter-630 gate de-risked (swap-all routine no longer used). WATCH: swap acceptance 0/12 at iter ~105 (normal
early; widen λ ladder if it stays ~0 — feeds convergence check, not a blocker).
Next: pilot ΔG → confirm past 630 → launch nr4a1,nr4a2 (on pre-baked image if build pushed) → reduce ΔΔG.

## ★ iter-630 GATE CLEARED (2026-07-04 18:59 UTC) — NR4A3 at iter 692/3000, stable, past the old numba crash point. swap-neighbors definitively fixes it. Converged ETA ~03:12 UTC 07-05 (~8h). Job survived a container restart (AWS-side).

## NR4A3 PILOT ΔG (2026-07-04 ~18:21 UTC) — NOT a verdict yet
`report_fep`: **NR4A3 ΔG_bind = −15.7 ± 19.7 kcal/mol (pilot, 500 iters)**. Central value negative (suggests
binding) BUT error ±19.7 is HUGE (> the value) → NOT a binding verdict; consistent with anything. Do NOT
over-read (same discipline that discarded the old −10.5). Cause: 500 iters is short + swap-neighbors mixes
slower than swap-all (acceptance 0/12 @ iter105 → 42.9% @ iter502, now healthy) → looser early error than the
old swap-all pilot's ±2.3. NR4A3 now at **iter 502/3000 PROD**, stable, ETA converged ~05:38 UTC 07-05 (~11h).
GATE UPDATE: pilot too noisy to gate NR4A2/NR4A1 — wait for PROD error to tighten to a clear sign. WATCH: if
error still huge by ~iter 950 (~2h), that flags a convergence/overlap problem to investigate.

## FLEET STATE + NR4A2 GATE (2026-07-04 ~16:45 UTC)
- **nr4a3** shard 0 (STOCK image): sampling pilot, the validated control.
- **nr4a1** shard 1 (`nr4a3-fep-sn-1-2026-07-04-16-40-50-945`, PRE-BAKED image): **FAILED — NaN at Iteration 1**,
  "replica 3 at state 2" (state 2 = Boresch restraint first at full 1.0). Image WORKED (no conda build) + receptor
  clean WORKED (past LEaP). Root cause = bad initial contact in the nr4a1 complex: likely a **clash in the nr4a1
  docked pose** OR a **strained auto-selected Boresch restraint geometry** — an INPUT/structure issue, engine-
  independent (not a Yank tripwire; not a sampling-param knob). **FIX DEFERRED behind the nr4a3 binding gate**
  (only matters if nr4a3 binds). Candidate fixes when resumed: relax/re-minimize the nr4a1 docked pose before
  Yank; and/or constrain Boresch restraint atom selection; clear ckpt/1 before relaunch.
- **nr4a2 HELD ON PURPOSE** — early-stopping gate: launch it ONLY after the nr4a3 pilot ΔG (~17:49) confirms
  denovo_401 BINDS NR4A3 (strongly negative). If nr4a3 pilot comes back weak/non-binding → STOP nr4a1
  (`fep-status stop_names=nr4a3-fep-sn-1-...`), do NOT launch nr4a2, reassess. Launch nr4a2 via:
  `gpu-fep-aws mode=run tag=nr4a3-fep-sn only_receptors=nr4a2 phase=full spot=1 git_ref=branch image_uri=<the ECR image>`.
- Pre-baked ECR image: `646605541856.dkr.ecr.us-east-2.amazonaws.com/nr4a3-fep:latest` (build-fep-image.yml; ECR IAM granted 2026-07-04).


## CONVERGENCE PLOT CADENCE (trimcrae, 2026-07-04): every 250 ITERATIONS (was 500 — smaller = smaller spot-loss window), not hourly.
- Paralogue jobs emit a `<receptor>_conv.jsonl` point per 500-iter prod segment (FEP_CONV_INTERVAL=250).
- Retrieve: `fep-status ckpt_prefix=nr4a3-fep-sn/ckpt` cats all `*_conv.jsonl` (added to `wanted`).
- Plot: `python plot_fep_convergence.py out.png <conv.jsonl>` overlays NR4A3+paralogues; SendUserFile.
- Poll ~every 1.8h (=250 iters @ ~13s/iter); re-plot + send when max-iter advanced by 250.
- Starts once paralogues launch (post NR4A3 verdict). NR4A3 itself: pilot(500)+final(3000) only (single-shot).

## Monitoring
- Self-wake = **background bash `sleep` → re-invokes agent on exit** (CLAUDE.md verified pattern). Current
  timer: `bdga0are8` (~35 min → first setup/sampling check).
- To read job state: dispatch `fep-status-aws.yml` (inputs: `cw_job`=live CloudWatch yank tail,
  result-json cat, SecondaryStatusTransitions). Public GH API for run status (no auth).

## Next actions (in order)
1. ~35 min: confirm env built + LEaP done + HREX sampling started (catch env/OpenCL failure cheap).
   **Also pre-flight paralogue inputs:** list `s3://<bucket>/nr4a3-denovo-matrix-v2/` — confirm
   `nr4a1-opened.pdb`, `nr4a2-opened.pdb`, `docked_nr4a1.sdf`, `docked_nr4a2.sdf` exist (else fan-out fails).
2. ~2.7 h (gate): confirm nr4a3-fep-sn is **past iter 630**. If clean → step 3. If crash → diagnose (residual
   masked-array elsewhere; candidate: raise/disable `online_analysis_interval`).
3. Fan out paralogues: `gpu-fep-aws.yml` mode=run **tag=nr4a3-fep-sn** only_receptors=**nr4a1,nr4a2**
   phase=full spot=1 git_ref=branch. Canonical indices 1 & 2 → two parallel spot jobs (quota 8, fine).
4. ~13 h: all three at prod. `mode=reduce` (`report_fep.py`) → per-receptor ΔG + ΔΔG.
5. Merge branch → main; fold ΔΔG into nr4a3-degrader paper + preprint plan.

## ON CONFIRMED SELECTIVE ΔΔG — rename the lead (trimcrae, 2026-07-04)
If the FEP confirms denovo_401 binds NR4A3 AND spares NR4A1/NR4A2 (selective ΔΔG), give it a proper lead name
(it earns the upgrade only on a confirmed result — don't name it before). KEEP `denovo_401` as the provenance
ID (401st de-novo candidate — reproducibility/methods trail); layer a name on top with a name↔denovo_401 map.
Naming lean: preserve the 401 lineage, e.g. `ND-401`/`NR4A3d-1` (NR4A3 Degrader). It's a clean one-time
find-and-map pass (denovo_401 is a stable string across code/data/manuscript). Do it once, when justified.

## Downstream pipeline — AUDITED SOUND (2026-07-04)
- Standard-state/Boresch correction: baked into each leg (`_parse_dg` reads `yank analyze` "Free energy of
  binding", which is Yank's fully-corrected ΔG). Nothing to add in reducer.
- `selectivity_ddg`: ΔΔG = ΔG(NR4A3) − ΔG(other), negative = selective. Correct sign.
- `combine_error`: quadrature sqrt(se1²+se2²), treats legs independent = CONSERVATIVE. (Shared ligand →
  identical solvent leg cancels in ΔΔG, so true error is if anything tighter. Honest/safe direction.)

## ENV FROZEN + ENGINE POLICY (2026-07-04)
- Reproducibility freeze: `sagemaker_src/environment-fep.yml` (pinned spec) + `sagemaker_src/Dockerfile.fep`
  (buildable) + `sagemaker_src/fep.lock` (authoritative `conda list --explicit` — capture from yank-env-check
  between `----FEP_LOCK_BEGIN/END----` and commit).
- Policy: current denovo_401 run FINISHES on Yank; NEXT fresh FEP (Yank re-failure OR new candidate) → MODERN
  stack (OpenFE-ABFE / openmmtools-scripted). Full rationale: next-steps.md → "ABFE ENGINE POLICY".

## Working env pins (entry_fep.py conda create — do NOT change without a yank-env-check run)
python=3.9, yank, openmmtools=0.21.2, ocl-icd-system, openbabel, setuptools<81, libnetcdf<4.9, parmed, pymbar<4.
Isolation: `conda run -n fep` with PYTHONPATH="" (base-container numpy 1.x leak fix).
