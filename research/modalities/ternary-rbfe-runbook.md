---
id: DOC-TERNARY-RBFE-RUNBOOK
title: Ternary RBFE / cooperativity-FEP runbook (GCP L4 spot — and now Vast, see §0)
level: L4
kind: memo
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `memo` from its location under research/modalities/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# Ternary RBFE / cooperativity-FEP runbook (GCP L4 spot — **and now Vast, see §0**)

## 0 · THE VAST LANE — where new ternary legs go from 2026-07-25

**trimcrae's directive: all production GPU runs go on Vast.** The GCP lane below still works and its failure
chain is still the authoritative account of *why* the recipe looks the way it does, but a new ternary leg
belongs on Vast. Read this section, then §1b/§1c for the physics.

| | GCP lane | **Vast lane** |
|---|---|---|
| workflow | `gpu-ternary-fep-gcp.yml` | **`gpu-ternary-fep-vast.yml`** |
| launcher | inline in the workflow | **`ternary_vast_launch.py`** |
| recipe | inlined invocation | **`run_ternary_leg.sh`** (shared, never re-implemented) |
| env | built on the VM per run | **`docker.io/triskit23/ternary-fep`** (pull, do not solve) |
| object store | GCS | **S3** (`ternary-vast/` prefix) |
| concurrency | 1 GPU, quota-capped | **N instances, one per leg** |
| watchdog | `ternary-leg-watchdog.yml` (GCP-only) | **`ternary-vast-watchdog.yml`** |

**Tasks** (`workflow_dispatch`, or a `[tvast:<task>]` marker in a pushed commit message while the workflow is
not yet on `main`): `test` · `dry-run` · `smoke` · `probe` · `edge` · `collect` · `reduce` · `stop`.
Nothing auto-fires; a push with no marker runs the $0 `test`.

**Things that are different from GCP and will bite you if you assume otherwise:**
- **A capacity refusal is not a preemption.** `{"success": false, "error": "resources_unavailable"}` means
  that machine has no free GPU and no bid fixes it. Destroy, exclude the machine, pick another host. Never
  queue, never raise the bid. `collect` does this automatically and persists the blocked list in S3.
- **"Alive" is not "advancing."** A rented box can sit up with a dead container. `collect` and the watchdog
  both require the **committed iteration count** to have gone up, and pair it with the on-host phase marker
  and log tail so the cold start (stage → pre-equilibrate → setup → minimise), during which the commit store
  is legitimately empty, is distinguishable from a hang.
- **The commit prefix is keyed by timestep**, so changing `dt` starts a clean trajectory by construction.
  There is no `reset_commits` to remember and nothing to wipe.
- **No setup cache yet.** The Vast host builds the ~146k-atom hybrid itself (~5–15 min observed). The stage
  tree and the pre-equilibrated complex ARE cached to S3, which is the expensive part (~8 min + ~7.6 min
  measured on a 4090).
- **Every leg persists a strided solute trajectory** (`RBFE_POSITIONS_WRITE_PS`, default 50 ps = a
  20-iteration stride, velocities off). This is a requirement, not a nicety — see §0b.
- **The relaxed `ligands.sdf` is a COORDINATE file and its charges are not this protocol's charges.** The
  pre-equil cache's SDF arrives stamped with the relaxation force field's partial charges, at *two* RDKit
  levels; stripping one and shipping the other killed every ternary leg on this lane for a day. Mechanism,
  dates and the three failure modes have their one home in
  [`nr4a3_rbfe.strip_foreign_partial_charges`](./nr4a3_rbfe.py); the measured per-attempt evidence is
  committed as `valb-triangle-attempt-forensic.json` (regenerate with `task=triangle-diag`). Operational
  consequence: **`task=triangle-diag` reads every ARCHIVED attempt, not just the newest** — a unit that has
  been relaunched dozens of times has its whole history there, and a leg that SUCCEEDED has its log only
  there (a later re-dispatch exits on the idempotency check and overwrites `run.log` with a two-line stub).
- **★ A `partial_charge_method = nagl` LOG LINE IS NOT EVIDENCE OF WHAT A LEG SAMPLED — read the System
  (`task=charge-provenance`, $0).** The third failure mode above is silent: a COMPLETE inherited set raises
  nothing and OpenFE simply prefers it, so the log keeps reporting the configured method. The stored
  setup-cache `System` records what was actually parameterised, and reading it is a bare-runner job over both
  object stores (~3 min, no docker, no GPU). Run it before folding any leg into a cycle whose argument is
  *"the charge model cancels"*. **What it found on the banked valB legs (2026-07-29):** the inheritance DID
  happen on every forward leg — and changed nothing, because the relaxed file's charges **are** the
  protocol's NAGL charges (`ternary_preequil._build_physical_system` conditions with
  `assign_rbfe_charges(off_lig, CHARGE_METHOD)`, and NAGL is graph-based, so the conformer is irrelevant).
  Per-leg evidence, including the two controls that make that reading load-bearing:
  [`charge-provenance-forensic.json`](./charge-provenance-forensic.json).

### 0b · Why the trajectory setting exists (do not turn it off to save space)
`nr4a3_rbfe._protocol` sets `positions_write_frequency = None` to avoid a ~1 GB analysis `.nc`. That is the
right instinct and the wrong extreme. A read-only census of the NR-V04 covalent panel on 2026-07-25 found
**72 objects across 19 units and ZERO trajectory objects** — one pre-minimisation frame, a 1.35 GB `System`
carrying forces and parameters but no coordinates over time, and scalars already reduced against the wrong
chain split. Three known analysis defects in that panel were therefore correctable in principle and none in
practice; it has to be re-run or abandoned. A **strided** write is the resolution: ~50 MB over a full leg,
against the ~112 MB System XML the same driver already uploads without comment. `rbfe_spot_driver` logs the
resolved stride every run, and shouts if it is zero.

---

# The GCP lane (below) — still the authoritative account of the recipe's failure chain

**Purpose:** everything a fresh session needs to run a ternary cooperativity-FEP leg (valB and the prospective
matrix) on GCP L4 spot **without re-discovering the 2026-07-18 failure chain.** Every item below cost real
debugging time; read this before launching a ternary leg.

The ternary lane is `nr4a3_ternary_fep.py` (engine) → `nr4a3_rbfe.execute_hybrid_dag_spot_safe` (shared spot-safe
driver) → `rbfe_spot_driver.run_spot_safe` (MultiState warmup/production) → GCS CommitStore. Workflow:
`.github/workflows/gpu-ternary-fep-gcp.yml`. CPU pre-bake: `.github/workflows/ternary-setup-prime-cpu.yml`.

---

## Quick start (the correct way to run one leg)

**★ THE PROCESS IS CPU-PRIME → GPU, AND IT IS ENFORCED IN CODE. NEVER let a GPU VM build setup.**
Setup (solvate + parameterize the 146k-atom hybrid system) is 100% CPU and takes ~8–40 min. Doing it on the GPU VM
means paying for an idle L4 the whole time — the exact anti-pattern the CPU pre-bake exists to kill. So the GPU run
now **FAILS FAST** (`RBFE_REQUIRE_PRIMED_SETUP=1`, the default) if the setup cache for its `(leg, charge)` is missing,
pointing you back here. There is no "recommended" — priming is mandatory.

1. **CPU-prime the setup cache FIRST (REQUIRED)** — `ternary-setup-prime-cpu.yml` (free, non-preemptible, ~30 min)
   builds the solvated/parameterized system on a CPU runner and writes it to the GCS setup-cache. Dispatch it once per
   `(leg, charge_method)`. *(Workflow must be on `main` — gotcha 6.)* The **nagl** cache for the frozen valB legs is
   already primed, so in practice you only prime a **new** leg or a **different charge**.
2. **Then dispatch the GPU leg** — `gpu-ternary-fep-gcp.yml` `mode=run leg_id=<leg> seed=<0/1/2>`. It **restores** the
   setup cache in seconds and does only the checkpointed MD, so a spot preemption costs ≤ one checkpoint interval.
   - **Charge: `nagl` is the DEFAULT and what every valB leg uses** (openff-nagl ML charges — fast, deterministic,
     reproduces am1bcc; the `openff-nagl` + `openff-nagl-models` packages are baked into the env-cache image, so nagl
     is always available on every VM). Only pass `charge_method=am1bcc` for a deliberate reviewer/rigor concordance
     check — and CPU-prime am1bcc first (its cache is separate; a bare am1bcc dispatch is what caused the 40-min
     GPU-idle stall on 2026-07-19).
   - **Timestep:** production `timestep_fs=4.0` with `warmup_timestep_fs=1.0` (reduced-dt warmup relaxes the rough
     ternary start; equilibration is discarded so it does not affect ΔG). See §1b.
   - **`restrain=1` — the flat-bottom pocket restraint. FOR THE BINARY ARM ONLY.** Default `0`; every existing
     lane is byte-identical without it. The binary leg's ligand left its pocket in **8 of 12** replicas in **both**
     cycles, so ΔG_binary was not a free energy of the bound state and ΔΔG_coop was not a cooperativity — audit
     §L.3a–§L.3d. Three things to know before you use it, all settled in **audit §L.3f**:
     - **Only the binary arm is re-run restrained.** The ternary arm is measured clean (0/12 displaced, both
       cycles, both directions) and keeps its existing trajectories. That is a **ruling**, with the falsifiable
       condition that reopens it stated there.
     - **No standard-state correction.** This is RBFE, not ABFE: the ligand is never decoupled, the restraint is
       λ-independent, and it cancels from ΔG(A→B). Importing ABFE's Boresch release term would be **wrong**, not
       conservative. Pinned by an AST test.
     - **It changes the Hamiltonian, so it keys the commit prefix (`_rst`) and the system fingerprint.** A
       restrained leg can never resume an unrestrained trajectory and vice versa — and unlike the fwd/rev
       collision, **a particle-count mismatch could not catch this**: the two systems are identical in
       composition. Do **not** hand-edit a prefix around it.
     - **Do NOT extend the existing binary trajectories** — they are *contaminated*, not under-converged
       (§L.3c: the departure is irreversible on this timescale and unbound configurations enter MBAR at physical
       λ). Use a fresh `restrain=1` prefix, which is what the `_rst` key gives you automatically.
   - Escape hatch: `allow_gpu_setup_build=1` lets the GPU build setup anyway (only for the very first prime of a
     brand-new leg/charge when no CPU prime has run).
3. **Monitor** — `mode=tail leg_id=<leg>` (SSHes the VM: nvidia-smi + `/tmp/tfep_run.log` + GCS commit census +
   post-mortem grep; the summary's verdict fields read the LIVE VM, `src=live`). Re-dispatch `mode=run` after a
   preemption (idempotent GCS skip + cache restore = fast resume).
4. **Reduce** — when all legs' `leg_*.json` land, `mode=reduce` → ΔΔG_coop vs the frozen target.

---

## The failure chain and its fixes (2026-07-18)

### 1. Warmup NaN at "replica 0 / state 1" — ⚠ **ROOT CAUSE BELOW IS SUPERSEDED — READ §1b/§1c FIRST**

> **⚠ Superseded 2026-07-19.** The "unconstrained alchemical C–H" root cause and the "run at 1 fs" fix stated in
> this section were both **refuted** — the ligand C–H are in fact constrained, and a reduced timestep does not
> prevent the NaN. The settled account is **§1b** (why the C–H story was a counter artifact) and **§1c** (plain-MD
> pre-equilibration is the actual fix). §1 is retained only as the record of what was ruled out — the clash census
> below is still valid evidence; the mechanism and the fix are not.
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

#### 1b. Timestep ceiling — **the ligand C–H ARE constrained; the ternary 4 fs NaN is a softcore/large-assembly issue, not a C–H one; the timestep is EMPIRICAL (settled 2026-07-19)**
- **This section was wrong TWICE; here is the measured truth.** A perses force-layout dump
  (`rbfe_edge_timestep_scan.py` → `constrain_diag`, 2026-07-19) showed the hybrid has TWO `CustomBondForce`s: (A) an
  alchemical **valence-bond** force (`length1/K1/length2/K2`) and (B) an alchemical **nonbonded-exception** force
  (`chargeProd/sigma/epsilon`). The `[hmr-diag]` counter had been counting (B)'s exception PAIRS as "X–H bonds" — so
  the pilot's 14 exception pairs read as "14 unconstrained bonds." **Both prior stories** (the original
  edge-specific "N→CH grows an unconstrained C–H", AND its correction "the whole ligand is unconstrained") were
  artifacts of that miscount. The ligand's real C–H stretch terms appear in **no** bond force, which in OpenMM means
  they **are constraints** — the ligand C–H **are constrained** (they sit inside `total_constraints`; the pilot's
  1771 ≈ 1761 water + ~10 ligand). `constrain_nonalchemical_xh()` correctly added **0** because there was nothing
  to add.
- **The corrected counter (skips force B) validates and settles it.** Counting only genuine valence stretch bonds:
  **pilot → 0 unconstrained → 4 fs** (matches step1's real 4 fs convergence, anchor PASSES) and **calib → 0
  unconstrained** as well — **yet calib empirically NaN'd at 4 fs.** So both edges have their C–H constrained and 0
  unconstrained valence X–H, but one survives 4 fs and one doesn't. **∴ the ternary 4 fs failure is NOT a
  C–H/constraint problem** — it is the **softcore alchemical (dis)appearing region in a large, rough
  homology-built assembly** (calib blew up in warmup at a softcore λ-state, `nonfinite=0`). There is **no static
  predictor** for the ternary timestep.
- **Guidance:** the ligand-C–H constraint state is NOT the lever (they're already constrained; `constrain_ligand_ch`
  is confirmed unnecessary). **Binary warhead RBFE runs at 4 fs** (OpenFE default; step1-proven; 0 unconstrained).
  The **ternary timestep is empirical** — determine it by an actual warmup-survival test, not a static count. As of
  2026-07-19 a **valB @ 3 fs** GPU baseline is the live arbiter (2 fs is the known-safe fallback; calib NaN'd at
  4 fs). If a larger ternary timestep is wanted, the real levers are a **gentler restrained equilibration / softcore
  schedule**, not C–H constraints. Whatever timestep the ternary survives, run **validation and production at the
  same one** (they must match).

#### 1c. RESOLVED (2026-07-19) — **plain-MD PRE-EQUILIBRATION is the fix; a reduced-dt warmup is NOT.** ★
- **The decisive experiment.** A 1 fs reduced-dt warmup (`warmup_timestep_fs=1.0`) — fed straight from the raw
  assembled complex — **fires correctly but does NOT prevent the NaN**: two runs blew up on **warmup iteration 1**
  (v3nagl → state 4, v3fast → state 0), both with **0 real clashes** (the only close contacts were hybrid/alchemical
  dummy pairs at ~0.6 Å), independent of timestep AND of minimization depth (25000 steps didn't help). This is the
  softcore/endpoint instability of a **rough SMARCA4→SMARCA2 homology model** fed into the alchemical λ-states — the
  documented OpenFE failure mode. **A smaller production OR warmup dt cannot fix it.**
- **The fix that WORKS: relax the fully-interacting physical complex with plain MD BEFORE the alchemical RBFE.**
  `ternary_preequil.py` (workflow `mode=preequil`) builds protein+ligA+solvent, runs minimize → restrained NVT heat
  (1 fs) → restrained NPT (100 ps) → release → short 4 fs production, and writes a **relaxed `complex.pdb` +
  `ligands.sdf`** cached to `preequilcache/`. The RBFE then runs with **`use_preequil=1`** (overlays the relaxed tree;
  keys the setup cache to `…__nagl__v1pe`).
- **VALIDATED end-to-end (2026-07-19).** With the relaxed structure the calib ternary leg ran clean:
  **warmup 48/48 (1 fs) → production 40/40 (4 fs), ZERO NaN, ΔG_morph = 47.28 ± 0.53 kcal/mol** — where every prior
  run died at warmup iteration 1. **This is THE ternary fix; do not chase the reduced-dt warmup.**
- **Process now:** `mode=preequil` (once per leg, cached) → `mode=run use_preequil=1` (first run needs
  `allow_gpu_setup_build=1` to build the `v1pe` setup cache). Keep the 1 fs warmup as cheap belt-and-suspenders.
- **Known minor follow-up:** the pre-equil writes ligB via O3A-align to the relaxed ligA; ~3 ligand atoms show
  OpenFE "mapping … deviates by more than 1.0" warnings. They were **benign** here (leg converged), but tightening
  the ligB alignment (or using a consistent conformer for the near-identical calib endpoints) removes the warning.

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
