# Ternary RBFE / cooperativity-FEP runbook (GCP L4 spot)

**Purpose:** everything a fresh session needs to run a ternary cooperativity-FEP leg (valB and the prospective
matrix) on GCP L4 spot **without re-discovering the 2026-07-18 failure chain.** Every item below cost real
debugging time; read this before launching a ternary leg.

The ternary lane is `nr4a3_ternary_fep.py` (engine) → `nr4a3_rbfe.execute_hybrid_dag_spot_safe` (shared spot-safe
driver) → `rbfe_spot_driver.run_spot_safe` (MultiState warmup/production) → GCS CommitStore. Workflow:
`.github/workflows/gpu-ternary-fep-gcp.yml`. CPU pre-bake: `.github/workflows/ternary-setup-prime-cpu.yml`.

---

## Quick start (the correct way to run one leg)

1. **(recommended) Pre-bake setup on CPU first** — `ternary-setup-prime-cpu.yml` (free, non-preemptible) builds the
   solvated/parameterized system and writes it to the GCS setup-cache. Dispatch it once per `(leg, charge_method)`.
   *(Requires the workflow to be on `main` — see gotcha 6.)*
2. **Then dispatch the GPU leg** — `gpu-ternary-fep-gcp.yml` `mode=run leg_id=<leg> seed=<0/1/2>
   charge_method=nagl timestep_fs=1.0`. It **restores** the setup cache (skips the ~460 s build) and does only the
   checkpointed MD, so a spot preemption costs ≤ one checkpoint interval.
3. **Monitor** — `mode=tail leg_id=<leg>` (SSHes the VM: nvidia-smi + `/tmp/tfep_run.log` + GCS commit census +
   post-mortem grep). Re-dispatch `mode=run` after a preemption (idempotent GCS skip + cache restore = fast resume).
4. **Reduce** — when all legs' `leg_*.json` land, `mode=reduce` → ΔΔG_coop vs the frozen target.

---

## The failure chain and its fixes (2026-07-18)

### 1. Warmup NaN at "replica 0 / state 1" — **unconstrained alchemical C–H, not a clash**
- **Symptom:** `SimulationNaNError: Propagating replica 0 at state 1 resulted in a NaN`, on warmup iteration 1,
  reproducible, surviving 25000 minimization steps + 20 integration retries.
- **NOT a starting-structure clash:** a CPU clash census (`ternary_stage_validate._clash_check`) proved the
  assembled complex clean — worst inter-residue non-bonded pair was a **1.33 Å peptide bond**, worst
  protein↔ligand was a **1.59 Å H-bond**. No coincident atoms.
- **Root cause:** the edge (e.g. cmpd1→cmpd4 is an **N→CH** change) grows a C–H bond that exists in state B but
  not A. A bond whose **constraint changes between endpoints is left UNCONSTRAINED** by OpenFE's hybrid factory,
  and an unconstrained C–H (period ~10 fs) is unstable at a 2 fs timestep once the softcore turns on at state 1.
- **Fix:** run at **1 fs** — `timestep_fs=1.0` input (→ `RBFE_TIMESTEP_FS`, read in `nr4a3_ternary_fep._protocol`).
  A binary RBFE with no such bond change is fine at 2–4 fs; this is ternary-edge-specific.
- **Instrumentation left in place:** `rbfe_spot_driver` catches the NaN, loads openmmtools' saved `nan-error-logs`
  state, and prints a `[clash-diag]/[nan-diag]` report naming the offending atoms.

#### 1b. Timestep ceiling — **the WHOLE alchemical ligand is unconstrained, so 2 fs is a LANE property, not an edge property (CORRECTED 2026-07-19)**
- **CORRECTION of an earlier wrong mechanism.** An earlier version of this section claimed the 2 fs ceiling was
  *edge-chemistry-specific* — that only morphs which change the H-count on a mapped atom (ring N→CH, sp²→sp³) grow
  an "unconstrained alchemical C–H", and that terminal-group swaps stay 4 fs-safe. **That was wrong.** It rested
  on the first `[hmr-diag]` counter, which scanned only the `HarmonicBondForce` and so saw ~3 X–H bonds when the
  alchemical bonds actually live in a separate `CustomBondForce`. A free per-edge scan
  (`rbfe_edge_timestep_scan.py`, 2026-07-19) that builds the REAL OpenFE solvent-leg hybrid and reads
  `system.getNumConstraints()` proved the truth: on the pilot 5-Br→5-NH₂ edge, `constraints='hbonds'`,
  `hydrogen_mass=3.0`, `total_constraints=1771` — but that is **water only** (~590 waters × 3 SETTLE); **all 14 of
  the ligand's X–H bonds are UNCONSTRAINED.** So OpenFE's HybridTopologyFactory leaves the **entire alchemical
  ligand's C–H flexible** (HMR'd to 3 amu, period ~18 fs); `constraints=hbonds` rigidifies only water/protein.
- **Consequence — the 2 fs ceiling is uniform, not edge-specific.** Every edge (warhead swap, N→CH, terminal) has
  ~all of its ligand C–H unconstrained, so a static "unconstrained-X–H count" **cannot** discriminate edges (the
  scan's anchor self-check correctly caught this: it could not reproduce pilot→4 fs). Whether 4 fs actually
  survives is driven by **system size + starting-structure roughness**, not by which bond morphs:
  - **Binary congeneric warhead RBFE** (small, clean, drug-like ligand; step1 lane): **4 fs runs** — this is
    OpenFE's benchmarked default and step1's pilot edge converged at 4 fs with no NaN. dt/period ≈ 0.22 is
    marginal-but-OK for a small clean system.
  - **Ternary cooperativity FEP** (large assembled PROTAC complex, homology-modeled/relaxed start; valB lane):
    **4 fs NaNs** — the empirical `calib_hi_to_lo` run (2026-07-19, ~7 h, 6 crashes) blew up in **warmup at
    replica 0 / state 5**, `nonfinite_atoms=0`, close pair `EXCLUDED-hybrid(benign)` (a real integration blow-up,
    not a clash). The many extra unconstrained DOF + a rough ternary start push dt/period past what 4 fs tolerates.
- **Guidance (lane-based, not edge-based):** run the **binary warhead RBFE at 4 fs** (OpenFE default; step1-proven).
  Run the **ternary cooperativity FEP at 2 fs** (`timestep_fs=2.0`; calib NaN'd at 4 fs — the large assembly needs
  it), falling back to 1 fs only if a specific ternary leg still NaNs. Within each lane the timestep is uniform, so
  validation and production always match (no "validate at one frequency, run science at another"). The root cause
  is the unconstrained alchemical ligand, NOT the morph chemistry.

### 2. Setup time varied 8 min ↔ 30 min "on the same machine" — **it was two different machines**
- **Symptom:** identical code/leg, setup (`SETUP done in Ns`) sometimes ~461 s, sometimes 30+ min → the long ones
  got preempted mid-setup before any checkpoint.
- **Root cause (serial console proof):** the provisioner's fallback list `g2-standard-8 g2-standard-4` silently
  dropped to **`g2-standard-4` (4 vCPU / 16 GB)** when the 8-vCPU box was spot-stocked-out. Setup (openff
  `interchange` parameterizing 146k atoms) is **CPU + RAM bound**; 16 GB is marginal → swapping → ~4× slower.
  Same L4 GPU on both, so *MD* is unaffected — only the CPU-side setup.
- **Fix:** pin `MACHINES="g2-standard-8 g2-standard-12 g2-standard-16"` (all ≥8 vCPU / 32 GB, all exactly 1× L4 =
  no GPU-cost change). Setup is now consistently ~8 min, shrinking the preemption-exposure window.

### 3. Preemption during the uncheckpointed setup lost everything — **checkpoint the setup, not just the MD**
- **Symptom:** the MD is spot-safe (per-interval GCS commits), but the ~460 s **setup** ran fresh on every VM and
  was un-checkpointed → a preemption during setup lost all of it and the run never reached the first MD checkpoint.
- **Fix — GCS setup-cache** (`nr4a3_rbfe.execute_hybrid_dag_spot_safe`, env `RBFE_SETUP_CACHE_GCS`): after the
  setup unit builds, the **whole `setup_outputs`** (files + a manifest; non-file values pickled) is cached to
  `gs://…/valB-6hax/setupcache/<tag>__<charge>__<version>`. A re-dispatch **restores it in seconds** and skips the
  rebuild. Generic over the full dict so the shared binary-RBFE path benefits identically; unset env = old
  behavior (Modal/step1 unaffected). Bump `SETUP_CACHE_VERSION` if staging/forcefield changes.

### 4. Land the first resumable checkpoint sooner
- Warmup checkpoint interval **20 → 8** (`RBFE_WARMUP_CKPT_ITERS=8` in the workflow's COMMIT_ENV). Once any
  checkpoint exists, later preemptions just resume. Production stays at 40.
- `rbfe_spot_checkpoint.run_to_target` logs **`[timing] N iters in Ns = X s/iter`** every chunk, so a live tail
  reads the real per-iteration wall time directly.

### 5. Pre-bake setup on a free CPU runner — **the definitive fix**
- Setup touches **no GPU** until the MD, so run it on a **free, non-preemptible GitHub CPU runner** and cache it,
  then the GPU VM restores it and does only the checkpointed MD. `RBFE_PRIME_ONLY=1` exits after the cache write
  (forces CPU platform so the CUDA probe can't fail). Workflow `ternary-setup-prime-cpu.yml` restores the **same**
  cached openfe env tarball the GPU VMs use (identical toolchain → coop-cycle-consistent parameterization).
- The serialized OpenMM `System` is platform-agnostic, so a CPU-built cache is identical to a GPU-built one.

### 6. Dispatching a NEW workflow off a feature branch
- A brand-new `workflow_dispatch` file 404s until it's on the **default branch**. So `ternary-setup-prime-cpu.yml`
  is dispatchable only after it reaches `main` (merge the branch, or push the workflow file to `main`). An
  already-on-`main` workflow (like `gpu-ternary-fep-gcp.yml`) can be dispatched with `ref=<branch>` and runs the
  branch's version of the file + code.

---

## GCP spot economics + mechanics (why we stay on spot)

- **Preemption is capacity-driven, price is not.** GCP Spot price is **set by Google** (no bid/auction), varies by
  **SKU (L4/GPU, vCPU, RAM) × region**, and changes **at most once / 30 days**. You do **not** get a bigger
  discount for being interrupted more; interruptions and price are independent (both track demand, so high-demand
  windows mean *more* preemptions *and* a smaller discount at once — e.g. midday L4 in us-central1).
- **30 s** preemption warning (vs AWS's 2 min), **no** minimum runtime; GCE Spot DELETEs the VM (unlike SageMaker
  managed-spot, which parks + auto-resumes via `max_wait`).
- **Spot ≥ on-demand only if wasted-hours > `(ondemand/spot − 1)`.** GCP's published Spot discount is 60–91% off
  → break-even waste is **150 %–1000 %** of useful compute. Post-fix waste per leg is ~4 % (setup cached/paid
  once, preemptions lose ≤ minutes). **Conclusion: spot is decisively cheaper; do not switch to on-demand for a
  capacity blip** (also matches the standing "wait out spot" rule; on-demand g2 quota is 1 = serial anyway).
- **us-central1 only** (project L4 quota); diversify across zones **a/b/c/f**, never other regions.

---

## Status of the fixes

| Fix | State |
|---|---|
| 1 fs timestep (NaN) | **Validated** — VMs get past state 1 with no `nan-error-logs` dir (2 fs produced one). |
| Machine pin ≥8 vCPU | **Validated** — re-dispatch landed g2-standard-8 (serial: "Total of 8 processors activated"). |
| GCS setup-cache save+restore | **Validated** — a run built+wrote the cache; a re-dispatch logged `SETUP RESTORED … skipped the ~460s`, loaded the 146925-particle system, and minimized on GPU (1 fs). Restore reconstructs file outputs as `pathlib.Path` (openfe `deserialize` calls `.parent`), not `str`. |
| Warmup ckpt 20→8 + `[timing]` | Shipped. |
| CPU pre-bake (`RBFE_PRIME_ONLY`) | **Validated** — on a CPU runner: env restored + imported, leg staged, CPU platform forced, GCS auth, cache restored. Dispatch once per `(leg, charge)`; bump `SETUP_CACHE_VERSION` to force a fresh CPU build. |

### Stage cache (done 2026-07-18)
- **The ~15 min staging (RCSB + SMARCA2 model + assembly) is now cached too.** The staged tree is tarred to
  `gs://…/valB-6hax/stagecache/<leg>__<template>__seed<seed>__v1.tar` (seed-keyed — `model_idx = seed % n_models`).
  The GPU startup restores it in seconds; the CPU pre-bake (or the first GPU run) populates it. Bump the `v1`
  suffix in **both** `gpu-ternary-fep-gcp.yml` and `ternary-setup-prime-cpu.yml` if staging code changes.
- **Net effect:** with stage + setup both cached, a GPU VM does boot → restore stage (s) → restore setup (s) →
  minimize + MD. The only un-checkpointed GPU window left is minimize + warmup-to-first-checkpoint (~minutes).
