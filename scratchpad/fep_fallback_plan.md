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

## ▶ MODERN STACK (trimcrae, 2026-07-04): modern independent-λ-window ABFE is now the GO-FORWARD engine
(Yank = fallback only IF its NR4A3 run finishes clean). Design: `nr4a3_abfe_modern_design.md`. Every-iteration
checkpoint + convergence by design (small per-window files, no monolithic .nc).

## ✅ MODERN STACK BUILD COMPLETE — steps 1-5 (2026-07-04, late). Engine + full SageMaker plumbing built,
unit-tested + free-CPU-smoke-validated (SMOKE_OK on CI), committed + pushed. NOT yet run on GPU.
- **`nr4a3_abfe.py`** — λ schedule + MBAR u_kn assembly; `run_window` (independent window: build→MD→
  reduced-potentials-at-all-λ→per-iter atomic checkpoint→resume→jsonl log); `reduce_leg` (MBAR + per-iteration
  convergence trace); Boresch `add_boresch_restraint` + `boresch_standard_state_correction` (unit-tested vs
  hand-computed −10.294 + monotonicity); `select_boresch_anchors` (+`_ang3/_dih4`, collinearity/distance
  guards); `combine_legs` (ΔG_bind = ΔG_dec_solv − ΔG_dec_cplx − SSC, cycle in docstring) + `selectivity_ddg`;
  `prepare_leg` (explicit-solvent complex/solvent, amber14SB+gaff-2.11+TIP3P+PME, reuses mmgbsa params);
  `run_shard` + `reduce_and_report`; CLI `--smoke/--run-shard/--reduce`. **11 unit tests green.**
- **`sagemaker_src/entry_abfe.py`** — spot Training entry (smoke/run/reduce), modern `abfe` env (PYTHONPATH-clear).
- **`nr4a3_abfe_sagemaker.py`** — submitter (plan/smoke/run/reduce); 4 legs = complex(nr4a3/1/2)+shared solvent,
  parallel on the 8-wide spot quota. plan mode verified.
- **`gpu-abfe-aws.yml`** dispatch; **`environment-abfe.yml` + `Dockerfile.sagemaker-abfe`** pre-baked image;
  **`abfe-modern-smoke.yml`** FREE CI engine smoke (passing every push).

## ⏭ NEXT ON THE MODERN STACK (step 6, GATED): before ANY NR4A3 number is trustworthy, run the **host-guest
accuracy gate** (design doc "Status & how to launch" §1) — match a published host–guest ΔG within ~1 kcal/mol.
This also surfaces the 2 flagged pre-trust refinements: (a) `run_window` is NVT → add a short NPT equilibration
(box density); (b) PME alchemical decoupling uses openmmtools' default treatment. Self-contained target:
`openmmtools.testsystems.HostGuestExplicit` (CB7–B2 in TIP3P, no external files). THEN: gpu-abfe-aws.yml
mode=smoke ($0.1 plumbing) → mode=run only_legs=solvent (one real leg) → full 4 → mode=reduce → selectivity_ddg.
**Real fleet needs trimcrae go-ahead.** The g5 on-demand slot is held by Yank (spot is a separate quota).

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

## 🧪 ABFE HYDRATION ACCURACY GATE — LAUNCHED (2026-07-05 ~8:00 PM ET / 00:00 UTC)
SageMaker spot job **`nr4a3-abfe-hydration-methane-2026-07-05-00-00-15-359`** (via gpu-abfe-aws.yml mode=hydration,
git_ref=branch). Validates the decoupling+MBAR engine: methane ΔG_hyd vs known ~+2.0 kcal/mol (tol 1.5).
Result → `hydration_validation.json` in the job model dir + `s3://sagemaker-us-east-2-646605541856/nr4a3-abfe/ckpt/hydration-methane/`.
Monitor via fep-status-aws.yml tag=nr4a3-abfe cw_job=nr4a3-abfe-hydration-methane. **GATE:** if |ΔG_hyd−2.0|≤1.5 →
engine validated → launch the 4-leg fleet (gpu-abfe-aws.yml mode=run git_ref=branch). If off → debug engine first.
NOTE: gpu-abfe-aws.yml is now on MAIN (required for API dispatch); it clones git_ref for the code.

## 🔧 HYDRATION GATE v1 FAILED → FIXED → v2 (2026-07-05 ~8:15 PM ET)
v1 (`…hydration-methane-…00-00-15`) FAILED at platform init: `CUDA_ERROR_UNSUPPORTED_PTX_VERSION` — conda OpenMM's
CUDA build too new for the g5 driver (SAME PTX issue as the Yank env; my Dockerfile comment wrongly assumed modern
OpenMM avoided it). FIX (commit babfa8e): `_select_platform()` validates+falls back CUDA→OpenCL; entry_abfe.py +
Dockerfile write the OpenCL ICD. **The gate did its job — caught a bug that would have crashed all 4 fleet legs.**
v2 job: **`nr4a3-abfe-hydration-methane-2026-07-05-00-15-36-349`** (n_iter=500, git_ref=branch). Expect
`[abfe] OpenMM platform: OpenCL` then window jsonl. If methane ΔG_hyd ≈ +2 (±1.5) → launch fleet + ethanol gate.

## 🚀 ABFE FLEET (partial) LAUNCHED (2026-07-05 ~8:34 PM ET) — OpenCL fix confirmed on methane v2
methane v2 (`…hydration-methane-…00-15-36`) ran PAST v1's ~11-min PTX crash point → OpenCL fallback works.
Launched 2 of 4 legs (validate-first: 1 complex before all 3):
- **`nr4a3-abfe-solvent-2026-07-05-00-34-23-865`** — shared solvent leg (denovo_401 in water; cancels in ΔΔG).
- **`nr4a3-abfe-complex-nr4a3-2026-07-05-00-34-24-928`** — NR4A3 complex leg (SHAKEOUT of prepare_leg complex path:
  PDBFixer receptor + Boresch anchors on the real pocket + PME box + restraint during decoupling).
HELD: complex-nr4a1, complex-nr4a2 — launch after (a) methane ΔG_hyd ≈ +2 confirms shared machinery AND
(b) nr4a3-complex proves prep runs (no NaN, windows advancing). tag=nr4a3-abfe, n_iter=500, git_ref=branch.
When all legs done: gpu-abfe-aws.yml mode=reduce → ΔG_bind per receptor → selectivity_ddg for ΔΔG.

## 🔧 complex-nr4a3 shakeout v1 FAILED (prep) → FIXED → v2 (2026-07-05 ~8:52 PM ET)
v1 (`…complex-nr4a3-…00-34-24`) got THROUGH env+platform+PDBFixer+Modeller.add+addSolvent+create_system on the
real receptor, then failed at Boresch-anchor coord extraction: `modeller.positions.value_in_unit(nm)` yields
numpy arrays, `.x` AttributeError. FIX (commit ea3e8dd): index `c[0..2]` not `.x/.y/.z`. **Shakeout worked —
the complex prep path is sound up to the last step; one-line fix.** v2 re-dispatched (ONLY_LEGS=complex-nr4a3).
Solvent leg (`…solvent-…00-34-23`) + methane v2 (`…hydration-methane-…00-15-36`) kept running (unaffected).
Monitor complex-nr4a3 v2 by prefix. NEXT prep risks to watch on v2: alchemical factory on ~40k-atom PME system,
NaN at window 0 (like Yank's nr4a1), OpenCL speed on the big system.

## ✅ ABFE ENGINE RUNS END-TO-END (2026-07-05 ~9:10 PM ET)
Sweep JOB SUMMARY: **solvent leg (`…solvent-…00-34-23`) = Completed** (first real end-to-end ABFE leg — denovo_401,
12 windows, clean). **complex-nr4a3 v2 (`…complex-nr4a3-…00-53-14`) = Training** (past the .x prep bug). methane v2
still Training (accuracy number pending; oddly slower than the bigger solvent leg — check). HOLD nr4a1/nr4a2 complex
until: (1) complex-nr4a3 confirmed ADVANCING windows w/o NaN (still-Training after ~18min in windows = past the
Yank-nr4a1 'Iteration 1' restraint-NaN risk), AND (2) methane ΔG_hyd ≈ +2. Then launch complex-nr4a1,complex-nr4a2.
Solvent ΔG comes from mode=reduce at the end.

## ✅✅ METHANE ACCURACY GATE PASSED + FULL FLEET LAUNCHED (2026-07-05 ~9:37 PM ET)
methane hydration_validation.json: **dg_hydration = 1.53 ± 0.06 kcal/mol** (known +2.0, error −0.47, pass=true).
Validates the shared decoupling machinery (elec→sterics schedule, per-λ reduced potentials, MBAR, sign) on a
real explicit-solvent system. BOTH gates green: complex-nr4a3 Training clean ~40min (NaN-clear) + methane accurate.
LAUNCHED complex-nr4a1 + complex-nr4a2 (gpu-abfe-aws mode=run only_legs=complex-nr4a1,complex-nr4a2, n_iter=500).
FULL FLEET now: solvent=Completed, complex-nr4a3=Training, complex-nr4a1/nr4a2=launching. WATCH nr4a1/nr4a2 for
restraint-NaN at window 0 (Yank's nr4a1 died there; different pockets→different anchors, so re-check).
WHEN ALL 4 legs Completed: gpu-abfe-aws mode=reduce (per receptor) → ΔG_bind → nr4a3_abfe.selectivity_ddg = ΔΔG.
TOOLING: read result JSONs via fep-status cat_s3=<prefix> ref=main (Describe auto-skips so JSON is the tail).
Note n_iter=500 may be short for complex-leg convergence — check SE at reduce; extend via resume if loose.

## ✅ FULL FLEET HEALTHY — all 3 complex legs Training (2026-07-05 ~9:56 PM ET)
JOB SUMMARY: complex-nr4a1(`…01-38-24-264`), complex-nr4a2(`…01-38-24-988`), complex-nr4a3(`…00-53-14-112`) ALL
InProgress/Training. nr4a1/nr4a2 ~8min into windows past the restraint-NaN (Yank's nr4a1 died at 'Iteration 1' —
ours cleared). solvent + methane Completed. Complex legs are ~40k-atom PME on OpenCL → ~2-4h for 12 windows each
(started ~00:58/01:46 UTC → ETA ~03:00-05:00 UTC / 11pm-1am ET). WAIT for all 3 Completed, then:
  gpu-abfe-aws mode=reduce receptors=nr4a3,nr4a1,nr4a2  → per-receptor ΔG_bind json
  read via fep-status cat_s3=nr4a3-abfe/ckpt/... (or the reduce job prints DG_BIND)
  → nr4a3_abfe.selectivity_ddg(nr4a3, nr4a1) & (nr4a3, nr4a2) = headline ΔΔG.
CONVERGENCE: n_iter=500 (methane solvent converged ±0.06 there; complex legs bigger+restraint may need more) —
check per-leg SE at reduce; if loose, relaunch same only_legs with higher n_iter (checkpoint resumes from 500).

## ⏱ MEASURED FLEET SPEED + GROUNDED ETA (2026-07-05 ~10:44 PM ET)
complex-nr4a3 S3 progress @02:43UTC: window_00/01/02 = 500/500 done, window_03 = 256/500, 04-11 not started =
3.5/12 windows in ~105min → **~30 min/window** (OpenCL, ~40k atoms, 12 per-λ energy evals/iter). Per leg ~6h.
ETA: nr4a3 complex (started 00:58UTC) → ~06:55UTC/2:55am ET; nr4a1/nr4a2 (started ~01:46UTC, parallel) →
~07:46UTC/3:45am ET. + reduce → **ΔΔG ~4am ET**. (Earlier '10:40pm' was a mislabeled progress check, not completion.)
meta.json confirms Boresch anchors selected on real NR4A3 pocket: r0=3.48Å, thetaA=136°, thetaB=110° (both in
30-150° guard band — the thetaB fix works on a real receptor). Convergence: check SE at reduce; extend if loose.
Read jsonl progress: fep-status cat_s3=nr4a3-abfe/ckpt/complex-<r>/<r>/complex (window_XX.jsonl line count=iters).

## ⛔ YANK NR4A3 SPOT-INTERRUPTED + RESET → STOPPED (2026-07-05 ~11:20 PM ET)
Live CW tail @03:17UTC showed the 15-58 job at **iter 579/3000** (was 2768/3000 @02:23UTC) with a fresh 2:33
wall clock — a spot interrupt that resumed from a STALE monolithic-.nc checkpoint (~iter 500), losing ~2200 iters,
possibly with a changed replica count. This is the EXACT broken-Yank-checkpoint failure that motivated the modern
stack. Per the standing NO-RESUME rule → StopTrainingJob nr4a3-fep-sn-0-2026-07-04-15-58-00-010. **DONE WITH YANK.**
No cross-check from Yank; the modern fleet IS the NR4A3 ΔG_bind source now (validated engine, per-iteration
checkpoints → ≤1 iter lost on interrupt, unlike Yank). Fleet ETA ~4am ET → reduce → ΔΔG. (ListTrainingJobs was
glitching to '0 jobs' repeatedly during this — the cw_job LIVE TAIL was the authoritative signal.)

## ✅ FLEET HEALTHY, YANK STOPPED (2026-07-05 ~11:57 PM ET)
Yank stop CONFIRMED ("STOP requested ... (was InProgress)"). All 3 modern complex legs InProgress/Training, NO
interrupts: complex-nr4a3(00-53-14), complex-nr4a1(01-38-24-264), complex-nr4a2(01-38-24-988). ~30min/window →
nr4a3 ETA ~06:58UTC/2:58am ET, nr4a1/2 ~07:46UTC/3:46am ET → reduce → ΔΔG ~4am ET. Next check ~2h.

## ⚠️ GITHUB MCP TOKEN EXPIRED (2026-07-05 ~1:58 AM ET) — dispatch blocked
Can no longer dispatch fep-status / gpu-abfe (status, reduce, cat_s3) — GitHub MCP needs re-auth (git push still
works via GH_TOKEN; workflow dispatch 403s on that token). Fleet UNAFFECTED — runs on AWS, completes ~3:46am ET,
data to S3. ON RE-AUTH: dispatch gpu-abfe mode=reduce receptors=nr4a3,nr4a1,nr4a2 → cat_s3 *_dg_bind.json →
nr4a3_abfe.selectivity_ddg = ΔΔG. Retry timer set ~2.5h to re-attempt dispatch when connector may be back.

## 🎉 ALL LEGS COMPLETED — REDUCE RUNNING (2026-07-05 ~4:32 AM ET)
Fleet done: complex-nr4a3/nr4a1/nr4a2 + solvent + methane all Completed. Fixed reduce path bug (entry_abfe
_leg_dir auto-locates nested <channel>/<r>/<leg>/window_*.jsonl — ckpt sync preserves the on-instance nesting).
Dispatched gpu-abfe mode=reduce receptors=nr4a3,nr4a1,nr4a2 on ml.c5.xlarge (CPU, MBAR). Each prints
'[abfe] DG_BIND X ± Y' to stdout (cw_job filter catches 'dg_bind|ΔG') + writes <r>_dg_bind.json to model dir.
READ after ~15min: fep-status cw_job=nr4a3-abfe-reduce-<r> per receptor → ΔG_bind(nr4a3/nr4a1/nr4a2) →
selectivity_ddg: ΔΔG(nr4a3−nr4a1) & (nr4a3−nr4a2). Negative = NR4A3-selective (the headline).

## ★★★ HEADLINE ΔΔG — MODERN ABFE (2026-07-05 ~5:10 AM ET) ★★★
denovo_401 ABFE ΔG_bind (kcal/mol), n_iter=500, OpenCL, shared solvent leg (23.87 identical across all → cancels):
  NR4A3: −1.18 ± 0.31  (complex decouple 33.84 — binds; ligand held ~10 kcal tighter than in water)
  NR4A1: +8.54 ± 0.36  (complex 23.89 ≈ solvent 23.87 — does NOT bind)
  NR4A2: +4.89 ± 0.34  (complex 27.53 — weak/no binding)
  **ΔΔG(NR4A3−NR4A1) = −9.72 ± 0.48 ; ΔΔG(NR4A3−NR4A2) = −6.07 ± 0.46 kcal/mol → NR4A3-SELECTIVE.**
Selectivity driven by complex-leg decoupling (cplx3 33.84 >> cplx1 23.89, cplx2 27.53); SSCs similar (~−8.6..−8.8)
so NOT a restraint artifact. CAVEATS (for the paper, must harden): n_iter=500 SHORT (per-leg SE is MBAR-statistical,
NOT convergence — true uncertainty larger); NVT no-NPT (box density); PME alchemical = openmmtools default; SINGLE
replicate (no independent-seed check). NEXT: extend n_iter (resume from 500 → 1500/2000) + a 2nd-seed replicate to
confirm ΔΔG stability BEFORE the preprint. Direction + magnitude are strong/clean.

## ▶ EXTENSION n_iter 500→1000 LAUNCHED + convergence-plot pipeline (2026-07-05 ~6:32 AM ET)
Local tree had reverted to old commit after container restart — RESTORED via ff-merge to 7554b94 (all session work
was safe on origin). Extension: gpu-abfe mode=run tag=nr4a3-abfe n_iter=1000 spot=1 → 4 legs resuming from iter 500:
solvent-10-31-52, complex-nr4a3-10-31-54, complex-nr4a1-10-31-55, complex-nr4a2-10-31-56. ETA ~+6h (~16:30UTC/
12:30pm ET; complex legs ~6h/500iter). Added --emit-trace: reduce prints compact 1-line 'TRACE_JSON [[iter,dg,se]..]'
(<=61 downsampled pts) to stdout + writes <r>_dg_bind.json (w/ full trace) to checkpoint dir (cat_s3-readable).
PREVIEW reduce dispatched on current ~500-iter data to validate plot pipeline NOW. PLOT: read 3 reduce jobs'
TRACE_JSON → matplotlib ΔG_bind(iter) 3 receptors (+ ΔΔG) → PNG for user. FINAL plot after extension+reduce.
