# RUNG 2b on Vast — the 4 fs ternary test, and what it corrects in the cost base

**Lane:** `gpu-ternary-fep-vast.yml` → `ternary_vast_launch.py` → `run_ternary_leg.sh` → `nr4a3_ternary_fep.py`.
**Provider:** Vast RTX 4090 (trimcrae, 2026-07-25 — all production GPU runs on Vast).
**Status of each number below is stated explicitly: DERIVED FROM CODE, MEASURED, or PENDING.**

This file is the evidence for the RUNG 2b entries; STRATEGY.md and `pricing.md` own the live figures and should
point here rather than restate the derivations.

---

## 1 · The 4 fs saving is ~1.56×, not 2× — DERIVED FROM CODE, and it changes the RUNG 2b headline

STRATEGY's cost lever 1 says: *"Iterations are timestep-independent (2.5 ps/iter), so 4 fs is exactly half the
force evaluations → ~$8.8/edge → ~$4.4."* The first clause is right and the conclusion does not follow, because
**it applies to production only**.

**The mechanism, from the code rather than from the claim.** `rbfe_spot_driver._iters_from_time` computes

```python
steps_per_iter = integrator.n_steps                 # = time_per_iteration / dt, fixed when the move is built
timestep       = from_openmm(integrator.timestep)
total_steps    = get_simsteps(sim_length, timestep, steps_per_iter)
return int(total_steps / steps_per_iter)
```

so `iterations = sim_length / time_per_iteration` — the two dt's cancel. That is the timestep-independence.
**But the warmup is measured with the WARMUP integrator** (`rbfe_spot_driver.py:365-366`), and the reduced-dt
warmup is built by overriding `.timestep` on a move whose `n_steps` was already fixed at the PRODUCTION dt
(`rbfe_spot_driver.py:349-351`). So the warmup covers `equilibration_length` **in real time at 1 fs**, and its
step count does not depend on the production timestep at all.

For the as-run protocol (`EQUILIBRATION_NS = 1.0`, `PRODUCTION_NS = 5.0`, `nr4a3_ternary_fep.py:358-359`), per
replica:

| production dt | warmup steps @1 fs | production steps | total | leg cost |
|---|---|---|---|---|
| 2 fs | 1.00e6 (800 iters × 1250 steps) | 2.50e6 (2000 × 1250) | **3.50e6** | 1.00× |
| 4 fs | 1.00e6 (1600 iters × 625 steps) | 1.25e6 (2000 × 625) | **2.25e6** | **0.643×** |

**Leg-level speedup = 3.50/2.25 = 1.556×, not 2×.** Asserted by
`tests/test_ternary_vast_launch.py::test_four_fs_speedup_is_not_two_because_the_warmup_does_not_shrink`, and the
same test shows the ratio only approaches 2× as the warmup goes to zero.

**Consequence for the ladder:** the 4 fs ternary leg is ~0.64× the 2 fs leg, not ~0.5×. Whatever the 2 fs base
is, the 4 fs base is that × 0.643.

## 2 · The as-run leg is 2800 iterations, not 2400 — DERIVED FROM CODE

STRATEGY's ternary basis row says *"Leg length confirmed at 2400 iterations (400 equil + 2000 production at
2.5 ps/iter)"*. The 400 is what you get if the warmup runs at the **production** timestep. The as-run valB
protocol sets `warmup_timestep_fs=1.0` against `timestep_fs=2.0`, and by §1 that makes the warmup **800**
iterations, each with the **same 1250 steps** as a production iteration — i.e. the same wall time per iteration.

So the as-run 2 fs leg is **800 + 2000 = 2800 iterations of equal cost**, and a leg priced as `2400 × s/iter`
understates it by **~17 %**. This is a pure bookkeeping correction to the *count*; it does not change the
measured per-iteration rate, and it is the same correction in both timestep arms, so it does not affect §1's
ratio.

At 4 fs the count is **1600 + 2000 = 3600 iterations**, but each is half the steps — which is why iteration
counts are a misleading unit here and **steps (force evaluations) are the right one.** Any future per-leg price
should be built from steps × measured seconds-per-step, not from an iteration count carried between protocols.

## 2b · The 4 fs arm changes TWO things, not one — and the record does not say what the 2 fs arm did

**This has to be stated before any GO/NO-GO is read.** The 4 fs arm necessarily runs **with**
pre-equilibration: 4 fs held in the runbook's §1c demonstration *only because* the physical complex had been
relaxed by plain MD first, and every prior attempt without it died at warmup iteration 1. So `use_preequil=1`
is not a free choice in the 4 fs arm — it is part of the arm.

**What the 2 fs arm did is not recorded.** The as-run baseline was verified against the live VM for
`timestep=2.0 fs`, the 1 fs warmup override, `nagl` and `minimization_steps=5000` (GH run 30123894814,
`mode=tail` on VM `gcp-ternary-30112102294`). `use_preequil` was **not** among the verified fields; what
STRATEGY and the schedule actually record is that the *workflow default* is `use_preequil: 0`. A default is
not an observation of the run.

**Why this cannot be resolved from here, and how to resolve it.** The commit prefix
(`commits/<leg>/<seed>_dt<dt>fs_clig<c>_wu<wu>[_salt][_dir]`) has no pre-equilibration component, so the
checkpoint layout cannot answer it. The one artifact that can is the **setup-cache version**: the GCP lane
keys the cache to `…__nagl__v2pe` when `use_preequil=1` and to the plain version otherwise. So a single
`gcloud storage ls gs://<bucket>/valB-6hax/setupcache/ | grep calib` settles it. This lane has no GCS
credentials and is under instruction not to touch the GCP workflow while another session is running a leg on
it, so it is logged here as an **open check for whoever holds GCS**, not guessed at.

**How the GO/NO-GO must therefore be worded.** The comparison is not "2 fs vs 4 fs with everything else
held"; it is **the 2 fs baseline against the protocol we would actually deploy**, which is
`4 fs production + 1 fs warmup + pre-equilibration` as a package. That is the decision-relevant comparison,
because there is no deployable "4 fs without pre-equilibration" arm to choose. Consequences:

- **AGREE within replicate SD → adopt.** The package reproduces the baseline, which is what adoption needs.
- **DISAGREE → NO-GO, and do NOT attribute it to the timestep.** With `use_preequil` unknown in the baseline,
  a shift could be the timestep, the starting structure, or both. The correct response is to stay at 2 fs and,
  if the decomposition is wanted, run the cheap missing arm (2 fs **with** pre-equilibration) rather than
  reason about which change did it.

*(In principle pre-equilibration should not move ΔG at all: it is a different force field used only as a
coordinate conditioner, the engine explicitly excludes it from `protocol_signature` as a starting-coordinate
choice like the per-replica seed, and OpenFE discards the equilibration from MBAR by construction. In practice
a rough homology model plus finite sampling can make the starting structure matter, which is why this is
recorded as a confound rather than argued away.)*

## 3 · Why the warmup checkpoint interval is per-mode — DERIVED, to be confirmed by measurement

A commit costs a reporter sync plus a ~25 MB `.nc`/`.chk` pair copied and PUT to S3; the MD between commits
costs `interval × seconds-per-iteration`. The GCP lane's warmup interval of **8** was chosen against an
800-iteration warmup. At 4 fs the warmup is **1600** iterations, so 8 would mean ~200 commits. The Vast lane
therefore uses **64** for `edge` (25 commits; first resumable snapshot ~8 min in, far inside a preemption
window) and keeps **8** for `probe` — partly because 48 must remain a multiple of the interval, and partly
because a short interval is exactly what **measures** the per-commit overhead. The probe's `[timing]` lines
versus its wall clock give that number; it is **PENDING**, not assumed.

## 4 · The first NR4A-adjacent ternary rate on Vast — PENDING

STRATEGY flags that the ternary cost base is a **SMARCA2/VHL 8G1Q** rate being used to price **NR4A** ternaries
— *"the same move that just cost 2.6× on the binary lane"* — and says not to treat it as transferable until an
NR4A ternary leg has been timed. This lane records per-phase `median/min/max/mean` seconds-per-iteration into
every `leg.json` (`timing.warmup`, `timing.production`) together with the card name, so the rate is a
deliverable rather than a log line.

Note what this lane can and cannot settle: `calib_hi_to_lo` **is** the SMARCA2/VHL 8G1Q system, so it re-measures
the *existing* basis on a full leg rather than transferring it to NR4A. It removes the "rate came from a
60-iteration probe" caveat; it does **not** remove the NR4A transferability warning. That still needs an
`nrv04_active_to_epimer__ternary_nr4a1` leg.

## 4b · Every ternary leg now persists a strided solute trajectory — SHIPPED

Lane 3's read-only census of the NR-V04 covalent panel found **72 objects, 19 units, zero trajectory
objects**: one pre-minimisation frame, a 1.35 GB `System` (forces and parameters, no coordinates over time),
and scalars already reduced against the wrong chain split. Three known analysis defects in that panel were
therefore correctable in principle and none in practice, and it has to be re-run or abandoned.

The ternary lane sat between two failure modes, not one. `nr4a3_rbfe._protocol` explicitly sets
`positions_write_frequency = None` ("energy-only .nc; avoids the ~1 GB trajectory bloat") — the
*destroy-re-analysability* extreme. `nr4a3_ternary_fep._protocol` never touched `output_settings` at all, so
it inherited whatever OpenFE's default was, and the same measurement that motivated the binary lane's `None`
says that default writes **every iteration** at ~0.5 MB/iter → ~1 GB per leg — which this lane then
**re-uploads whole at every spot commit**. Neither was a choice anyone made.

**Shipped:** `RBFE_POSITIONS_WRITE_PS` (default **50 ps** = a 20-iteration stride at the 2.5 ps
`time_per_iteration`), velocities off. That is **~50 MB over a full leg** against the ~112 MB System XML the
driver already uploads unremarked, and it is `output_indices`-filtered (solute, not the water box).
`rbfe_spot_driver` now logs the resolved stride, and a zero stride prints
`** NO POSITIONS WILL BE STORED — this leg will not be re-analysable **`, so the question is answered in the
run log rather than inferred from a file size months later.

⚠ **The stage-1 probe predates this change** (launched from commit `06dc6e04`; the host pulls the branch
tarball at container start). Its trajectory is whatever the OpenFE default gave. That is acceptable for a
200-iteration survival probe with no re-analysis value; the stage-2 edge carries the setting.

## 4c · First measurements from the Vast lane (stage-1 probe, instance 45827166, RTX 4090)

Machine 12697, bid **$0.136/hr** against a market floor of $0.1333 and an on-demand cap of $0.36; billed
`dph_total` **$0.1527/hr**. Driver 580.173.02, 24564 MiB.

**Cold-start budget (all measured, ET):**

| phase | wall | note |
|---|---|---|
| rental → container start | 2.8 min | 3.35 GB image pull |
| staging (RCSB + SMARCA4→SMARCA2 model + assembly) | ~8 min | cache MISS; cached to S3 for every later leg |
| pre-equilibration (0.5 ns, 191,713-atom solvated box) | **456 s** | cached to S3; endpoint map 109 atoms, **max mapped displacement 0.00 Å**, graph identical, chirality and net charge conserved — the runbook §1c "~3 ligand atoms deviate" follow-up does not reproduce |
| setup (hybrid solvate + parameterise) | ~6 min | on the GPU host; faster than the GCP lane's ~8 min |
| **total before the first MD iteration** | **~25 min** | of which ~15 min is now cached and will not repeat |

**Per-iteration rate.** A warmup iteration at a 4 fs *production* configuration is 625 steps (`n_steps` is fixed
at the production dt; the warmup only overrides `.timestep`), so warmup and production cost the **same wall time
per iteration** here — which is what makes the warmup the expensive half.

- pure MD: **~6.6–8.5 s/iter** (openmmtools per-chunk estimates)
- commit-inclusive at `warmup_ckpt_iters=8`: **11.4 s/iter** (24→32 committed in 91 s)
- ⇒ **per-commit overhead ≈ 23 s.** At the probe's ci=8 that is ~34 % overhead; at the edge's **ci=64 it is
  ~0.4 s/iter, under 5 %.** The per-mode checkpoint interval was chosen from this reasoning before the run and
  the run confirms the magnitude.

**Projected full 4 fs ternary leg:** 1600 warmup + 2000 production = 3600 iterations × ~8.9 s (commit-inclusive
at ci=64) ≈ **8.9 GPU-h**, plus ~25 min cold start ≈ **9.3 h ≈ $1.42** at this host's rate.

**Against the STRATEGY basis.** The ternary row carries ~16 s/iter at **2 fs** (1250 steps). This lane measures
~8.5 s/iter at 625 steps, i.e. **~17 s per 1250 steps** — the existing rate is **confirmed**, on the same 8G1Q
system, on a full leg rather than a 60-iteration probe. It does **not** discharge the NR4A transferability
warning: `calib_hi_to_lo` *is* the SMARCA2/VHL 8G1Q assembly.

## 5 · Test status

| claim | status |
|---|---|
| 4 fs leg-level speedup = 1.556× | DERIVED FROM CODE + unit-tested |
| as-run 2 fs leg = 2800 equal-cost iterations | DERIVED FROM CODE |
| 4 fs production survives ≫40 iterations | **RUNNING** — warmup 48/48 clean, production advancing (see §7) |
| ΔΔG_coop at 4 fs agrees with the 2 fs value | **PENDING** — RUNG 2b stage 2 (matched edge) |
| measured s/iter for warmup and production on a Vast 4090 | **PENDING** — recorded by both stages |
| per-commit checkpoint overhead | **PENDING** — read from the probe |

---

## 6 · Proposed edits to STRATEGY.md and pricing.md

Written as exact deltas so the owner of those files can apply them without re-deriving anything. Nothing here
is applied by this lane; STRATEGY.md is not edited by anyone but its owner.

**STRATEGY.md → "Cost levers adopted 2026-07-24", lever 1.** Replace *"so 4 fs is exactly half the force
evaluations → ~$8.8/edge → ~$4.4"* with the ratio that survives the warmup:

> Iterations are timestep-independent, so 4 fs halves the force evaluations **in production**. The warmup is
> not halved: its iteration count is derived from the WARMUP integrator (1 fs), so 1 ns of equilibration is
> 1e6 steps at either production timestep. Per replica: 2 fs = 1.0e6 + 2.5e6 = 3.5e6 steps; 4 fs = 1.0e6 +
> 1.25e6 = 2.25e6. **Leg-level saving 1.56×, not 2×** (derivation + unit test:
> `research/compute/ternary-4fs-vast-findings.md` §1).

**STRATEGY.md → per-edge bases table, "Ternary cooperativity edge" row.** The parenthetical
*"(400 equil + 2000 production at 2.5 ps/iter, `nr4a3_ternary_fep.py:343-344`)"* is the count for a warmup at
the **production** timestep. The as-run protocol sets `warmup_timestep_fs=1.0`, which makes it **800** warmup
iterations of the **same 1250 steps each** — so the as-run 2 fs leg is **2800 equal-cost iterations, not
2400**, and pricing it as `2400 × s/iter` understates by ~17 % (§2). Prefer pricing in **steps**: iterations
are not comparable across protocols.

**STRATEGY.md → RUNG 2b entry.** Add the confound, because it changes what a NO-GO licenses (§2b): the 4 fs
arm necessarily carries pre-equilibration, `use_preequil` was never verified for the 2 fs baseline (only the
workflow default is recorded), and the settling observation is one `gcloud storage ls` of the setup-cache
prefix for a `v2pe` suffix. Agreement authorises adoption; disagreement is a NO-GO that must **not** be
attributed to the timestep.

**STRATEGY.md → the trajectory requirement.** Record that it is now implemented, not just required:
`RBFE_POSITIONS_WRITE_PS` defaults to 50 ps (a 20-iteration stride, ~50 MB/leg, solute only) in
`nr4a3_ternary_fep._protocol`, and `rbfe_spot_driver` logs the resolved stride and shouts when it is zero
(§4b). Note that this changes the **GCP** ternary lane too, since both call the same engine.

**pricing.md → the ternary row's provenance.** Two amendments: (i) the 4 fs conversion factor is **0.643×**,
not 0.5×; (ii) the leg is 2800 iterations as run, not 2400. Both are arithmetic on the existing measured
per-iteration rate — neither requires a new measurement, and neither changes that rate.

**pricing.md → the "time one before treating these rows as firm" warning.** This lane re-measures the
existing `calib_hi_to_lo` (SMARCA2/VHL 8G1Q) basis on a full leg, on a 4090, per phase. It therefore removes
the "the rate came from a 60-iteration probe" caveat. It does **not** remove the NR4A transferability
warning — `calib_hi_to_lo` *is* 8G1Q. That still needs an `nrv04_active_to_epimer__ternary_nr4a1` leg, and
the warning should say so explicitly rather than being read as discharged.

---

## 7 · Stage-1 probe — live record

`calib_hi_to_lo__ternary_vhl_r0_dt4.0fs_wu1.0_probe` · instance 45827166 · machine 12697 · RTX 4090 ·
bid $0.136/hr · billed $0.1527/hr. All times ET.

| time | event | evidence |
|---|---|---|
| 1:36 PM | rented | floor $0.1333, on-demand cap $0.36 |
| 1:39 PM | container up, **CUDA present** | `openmm 8.4 platforms ['Reference','CPU','CUDA']`, driver 580.173.02 |
| 1:47 PM | staged from 8G1Q | `[smarca2] model 1/2 relaxed (15 muts)` |
| 1:55 PM | **pre-equilibration done, 456 s** | 191,713 atoms; endpoint map 109 atoms, max mapped displacement **0.00 Å** |
| 2:01 PM | setup done, S3 commit store bound | `[spot-safe] commit store: s3://…/ternary-vast/commits/…_dt4.0fs_wu1.0_probe` |
| 2:04 PM | **warmup iteration 1 SURVIVED** | `Iteration 3/8` — the exact point every prior 4 fs attempt died with `SimulationNaNError` |
| 2:08 PM | warmup 24/48 committed | S3 census |
| 2:11 PM | **warmup 48/48, production started at 4 fs** | `committed=warmup/48`, then `Iteration 3/40` |
| 2:14 PM | production 19/40 of the first chunk, steady | ~7.7 s/iter |

**Two distinct NaN risk points are now passed:** warmup iteration 1 at the softcore λ-states, and the
warmup→production hand-off where the sampler moves to the full 4 fs timestep.

**Recorded caveat on this probe specifically:** it was launched from commit `06dc6e04`, before the strided
trajectory setting landed, and before `PYTHONUNBUFFERED=1`. Its `[timing]`/`[barrier]` lines are therefore
block-buffered — which is how that defect was found (§4c) — and the per-iteration numbers above come from
openmmtools' own per-chunk estimates and from the S3 commit census, both of which are independent of the
buffered stream.
