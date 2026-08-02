# RUNG 2b on Vast — the 4 fs ternary test, and what it corrects in the cost base

**Lane:** `gpu-ternary-fep-vast.yml` → `ternary_vast_launch.py` → `run_ternary_leg.sh` → `nr4a3_ternary_fep.py`.
**Provider:** Vast RTX 4090 (trimcrae, 2026-07-25 — all production GPU runs on Vast).
**Status of each number below is stated explicitly: DERIVED FROM CODE, MEASURED, or PENDING.**

This file is the evidence for the RUNG 2b entries; nr4a3-program-map.md and `pricing.md` own the live figures and should
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

**✅ THE OPEN CHECK ABOVE IS CLOSED — from the trajectory, not from a cache listing. See [§2d](#2d--the-particle-counts-differ-and-the-solute-does-not--measured-and-it-settles-what-2b-left-open).**
The r0 2 fs ternary leg is the pre-equilibrated `v2pe` build, so **both** arms were pre-equilibrated and this
particular confound is gone. §2d also shows the arms differ in more than the timestep — independently
constructed builds, not one system with a dial turned — and sizes what that is worth.

## 2c · The stage-2 decision rule, PRE-SPECIFIED (written before the number exists)

STRATEGY's RUNG 2b gate says *"ΔΔG_coop consistent with the 2 fs run within replicate SD"*. **There is no
replicate SD.** The 2 fs arm is a single cycle (r0), and the whole valB_mini verdict turns on the fact that
r1/r2 were never run. So the gate as written has no threshold in it, and picking one after seeing the 4 fs
number would be exactly the retune-after-a-failing-result this program has already refused once.

So, declared now:

- **Comparator:** ΔΔG_coop(4 fs) against **−0.534 kcal/mol**, the r0 cycle
  (binary 48.0046 / ternary 47.4701 / solvent 47.8060, `valB-mini-r0-verdict-2026-07-25.md`).
- **Threshold: 0.7 kcal/mol**, which is *this repo's own assumed replicate SD* — the number STRATEGY uses
  when it computes that a perfectly accurate method passes the first round only 9 % of the time. It is not
  invented here and it is not chosen to make anything pass.
- **PASS (adopt 4 fs):** no NaN across the full leg **AND** |ΔΔG_coop(4 fs) − (−0.534)| ≤ 0.7.
- **FAIL (stay at 2 fs):** any NaN, **or** a difference > 0.7.
- **Reported either way**, with the difference stated numerically rather than as a verdict word.

**One confound is removed and should be said so.** Ternary seed *s* uses the *s*-th relaxed SMARCA2 model
(`starting_model_index = seed % n_models`), so a different seed would compare two *different structures*. Both
arms are **seed 0**, hence the same starting model. What remains uncontrolled is only the pre-equilibration
conditioner (§2b) — one confound, not two.

**And a limit worth stating plainly:** this is a comparison of two single cycles. A 0.7 threshold on n=1 vs
n=1 detects a gross protocol shift and nothing finer. It cannot certify that 4 fs and 2 fs agree to within,
say, 0.2 kcal/mol, and no claim of that kind should be built on it.

## 2d · The particle counts differ, and the SOLUTE does not — MEASURED, and it settles what §2b left open

**The question.** The committed ternary trajectories carry different `atom` dimensions. A bare integer cannot
say whether that is bulk water or a different molecule, and those two readings license opposite conclusions:
bulk water cancels out of ΔΔG_coop, a different solute means the 4 fs and 2 fs cycles are not measuring the
same thing and may not be compared at all. So the composition was measured rather than argued about
(`ternary_system_census.py`, `ternary-system-census.yml`, $0 CPU, no VM — it recovers the whole `openmm.System`
that openmmtools serializes into `simulation.nc` and partitions every particle by bonded connectivity).

**First, a misattribution to clear, because it changes which numbers are even relevant.** The three counts the
question was raised about — 7,388 / 7,398 / 7,392 — all come from one **GCS** listing (GH run 30312683166,
`mode=provenance`). **The RUNG 2b 4 fs cycle did not run there.** It ran on the Vast lane, which writes to
**S3** and, per `ternary_vast_launch.py`'s own de-confliction note, "never touches GCS"; its reduction pulled
the three legs from `s3://…/ternary-vast/legs/` (GH run 30208761567). The `dt4.0fs` prefixes sitting in GCS are
**earlier GCP 4 fs attempts**, and the same provenance run lists exactly four leg-result JSONs in that bucket,
all of them r0 — so those attempts produced no result and are in no cycle. The RUNG 2b ternary leg's real
count is **7,384**, a fourth number, which nobody had measured.

**The census ([GH run 30443804729](https://github.com/trimcrae/Rare-cancers/actions/runs/30443804729), the
authoritative one).** `total = solute + ions + 3 × waters` closes exactly on every row, so nothing is
unaccounted for and the water model is 3-site. *(The first run of this, 30353705917, produced the same
measurements but reported them with two rows missing: the GCP layout puts the leg id one level up, so the
ternary, binary and solvent legs of one cycle shared a label and overwrote each other's records. Fixed, and a
collision is now a loud refusal — `ternary_census_targets.label_for`.)*

| leg | store | total | subset | solute | chains | lig | waters | Na⁺ / Cl⁻ | net q |
|---|---|---|---|---|---|---|---|---|---|
| **ternary r0 fwd** `…_v2pe` | GCS | 141,968 | 7,388 | **7,140** | 2343/1925/1433/1329 | 110 | 44,860 | 126 / 122 | 0 |
| **ternary r0 rev** `…_v2pe_dirrev` | GCS | 141,968 | 7,388 | **7,140** | 2343/1925/1433/1329 | 110 | 44,860 | 126 / 122 | 0 |
| **ternary RUNG 2b 4 fs** `…_dt4.0fs_wu1.0_edge` | S3 | 139,939 | **7,384** | **7,140** | 2343/1925/1433/1329 | 110 | 44,185 | 124 / 120 | 0 |
| ternary RUNG 2b 4 fs probe | S3 | 139,939 | 7,384 | **7,140** | 2343/1925/1433/1329 | 110 | 44,185 | 124 / 120 | 0 |
| ternary GCP 4 fs `…_pe1` *(no leg result — not in any cycle)* | GCS | 143,742 | 7,392 | **7,140** | 2343/1925/1433/1329 | 110 | 45,450 | 128 / 124 | 0 |
| binary RUNG 2b 4 fs | S3 | 90,702 | 5,376 | **5,215** | 2343/1433/1329 | 110 | 28,442 | 84 / 77 | 0 |
| binary restrained re-run `…_wu_rst` | GCS | 94,142 | 5,384 | **5,215** | 2343/1433/1329 | 110 | 29,586 | 88 / 81 | 0 |
| binary replicate r1 / r2 | S3 | 90,324 / 90,720 | 5,376 | **5,215** | 2343/1433/1329 | 110 | 28,316 / 28,448 | 84 / 77 | 0 |
| solvent RUNG 2b 4 fs | S3 | 5,304 | 120 | **110** | — | 110 | 1,728 | 5 / 5 | 0 |

**THE SOLUTE IS IDENTICAL ATOM-FOR-ATOM WITHIN EVERY ARM.** Ternary 7,140 = four chains of
2343/1925/1433/1329 plus a 110-atom ligand; binary 5,215 = the same minus the 1,925-atom SMARCA2 bromodomain;
solvent 110. Every difference in the totals is bulk water and the counter-ions that scale with it. The tool's
own verdict, verbatim:

> **SAME ALCHEMICAL SYSTEM PER ARM** — within every arm actually compared (ternary, binary) the protein chains,
> the ligand and the net charge agree atom-for-atom, so any remaining particle-count difference is bulk
> solvent. Arms with fewer than two censused legs are UNTESTED, not agreed: solvent.

The comparison is **per arm and never pooled**: a ternary leg (4 chains), a binary leg (3) and a solvent leg (0)
are different systems by construction, so demanding one solute across them is a category error — and an arm
with one censused leg reports UNTESTED rather than passing, which is why `solvent` is named rather than
quietly counted as agreement.

**Two independent corroborations, because "the solute is the same" is the load-bearing claim:**

1. **The neutralising ion EXCESS is invariant within an arm.** `SolventComponent()` neutralises, so Na⁺ − Cl⁻
   *is* the solute's formal charge with the sign flipped. It is **+4 in all five ternary builds**
   (126−122, 124−120, 128−124) and **+7 in all four binary builds** (84−77, 88−81) — across two lanes, two
   timesteps and independent solvations. **A different protonation or tautomer state would move this number
   and it does not**, which is the observation that discriminates the hypothesis the question raised.
2. **The salt tracks the water at a fixed molarity.** Cl⁻ per water is 2.7196e-3 / 2.7159e-3 / 2.7283e-3 across
   the three ternary builds and 2.7073e-3 / 2.7378e-3 in the binary ones — constant to ~0.5 %, and equal to
   0.15 M (0.15/55.5 = 2.70e-3). So the ion count is **derived** from the water count, and the water count is
   set by the padding-based solvation box around an independently relaxed complex. That is the mechanism, and
   it is measured rather than assumed.

**What the census CANNOT see, stated so nobody reads it as more than it is.** A λ-independent flat-bottom
restraint adds a *force*, not atoms, so a restrained and an unrestrained leg are **identical in composition**
and this instrument is blind to the difference by construction. Restraint state is legible only from the commit
prefix (`_rst`) and the manifest's `RBFE_RESTRAIN` — which is exactly why those keys exist.

**What this closes, and what it does not.**

- **§2b's open confound is closed for the ternary arm.** The r0 2 fs ternary leg is the pre-equilibrated
  `v2pe` build: its 141,968 particles and 7,388 subset match the *known*-`v2pe` reverse leg field for field,
  and differ from the non-pre-equilibrated GCS builds. Both arms of the 2b comparison were pre-equilibrated.
- **The two arms are NOT "the same system with only the timestep changed."** They are two **independently
  constructed builds of the same system**, on different lanes, providers and GPUs, each with its own RCSB
  fetch, its own SMARCA2 relaxation, its own solvation and its own pre-equilibration — which is precisely why
  the water counts differ. The solute is identical; the box is not.
- **Bulk-solvent difference, sized against the gate.** ΔΔG_coop is a difference of alchemical morphs, and bulk
  water is present at both λ endpoints of a leg, so it cancels to first order; the morph is charge-neutral
  (110 atoms both ends, net charge 0, neutralising excess unchanged), so the finite-size terms that scale with
  the square of a net charge *change* are identically zero here. For a magnitude, use this cycle's own
  measurement: replacing the **entire** environment — a 1,728-water box holding only the ligand — with the full
  four-chain ternary assembly moves ΔG_morph by 47.7982 − 47.6131 = **0.185 kcal/mol**. The two ternary builds
  differ by 675 waters, **1.5 %** of 44,185, with an identical solute; scaling gives **~3e-3 kcal/mol**. That is
  ~40× below the per-leg MBAR SE (0.10–0.13), ~7× below the observed |Δ| = 0.0215, and ~230× below the 0.7
  threshold. **This is an order-of-magnitude scaling argument anchored on a measured quantity, not a rigorous
  bound**, and it is not offered as one.

**⚠ MAY THESE LEGS BE COMBINED? Yes on system identity — and that is a narrower statement than it sounds.**
Within each arm the alchemical system is the same, so pairing a ternary and a binary leg into one ΔΔG_coop is
sound whichever build each came from. **This specifically clears the restrained binary re-run for use in the
r0 cycle**, which `ternary-watch.json` flagged as needing verification before the leg was folded in — *"a
v1-vs-v2pe mismatch is audit J.2–J.4's exact defect and the particle counts differ, so the leg's own record
settles it."* It does: the restrained leg's solute is 5,215 atoms over chains 2343/1433/1329 plus the 110-atom
ligand, with the same +7 neutralising excess as every other binary build, so the v1/v2pe difference here is
**solvation, not solute**, and the ΔΔG_coop that swap produces is a difference of like systems.

Three things it does **not** license: **(a)** it says nothing about *protocol* equality, which is
`protocol_hash`'s job; **(b)** it must not be used to pair a **restrained** binary arm with an **unrestrained**
one — the restraint is deliberately a different Hamiltonian, the census is blind to it, and such a cycle would
measure the restraint. That is why the RUNG 2b gate's comparator stays the **unrestrained** r0 value (see
nr4a3-program-map.md's ratified-threshold note); **(c)** it is not a licence to pool legs into a replicate SD, which is
a sampling question, not an identity one.

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

## 4c · The checkpoint interval is PER ARM, because exposure is measured in SECONDS (2026-07-28)

Host churn is the dominant cost of wall-clock on this lane and the warmup checkpoint interval is the single
lever that decides how much work each churn event destroys. What a reclaim costs is

    EXPOSURE = warmup_ckpt_iters × seconds-per-iteration        ← SECONDS, not iterations

and seconds-per-iteration is a property of the **arm** (how big the solvated system is) while
`warmup_ckpt_iters` was a property of the **mode**. One shared number therefore bought the two arms two
different exposures and nothing in the readout said so.

**No figures are restated here** (CLAUDE.md §1). The measured rates have one home,
[`ternary-arm-iteration-rates.json`](../modalities/ternary-arm-iteration-rates.json), regenerated from the
legs' own `leg.json` timing blocks by [`ternary_arm_rates.py`](../modalities/ternary_arm_rates.py) (CI:
`gpu-ternary-fep-vast.yml` task `reps-diag`), which also prints the derived cadence and the exposure it buys.
The derivation itself is `ternary_vast_launch.warmup_ckpt_iters_for`; §4's per-commit overhead above is the
other half of its trade-off and is not re-derived anywhere else.

Three things that file refuses to do, each because the repo has already been bitten by the equivalent:

* **pool across the production timestep** — a 2 fs iteration is 1250 MD steps and a 4 fs one 625 (§1/§2);
* **pool across phase** — pricing.md's superseded ~2.06× L4→4090 ratio was a warmup rate against a
  production rate. The one cross-phase step taken is production→warmup at the *same* timestep, which §4
  above licenses (same `n_steps`, so the same wall time per iteration), and the artifact measures the
  warmup/production ratio on every leg that recorded both so the substitution is checked rather than assumed;
* **let a card ratio pose as an arm ratio** — the fleet is mixed (4080S / 4090 / 5090), so the artifact also
  reports each arm per GPU model and a test requires the two arms' ratio on the shared card to agree with
  the mixed-fleet one.

**What the asymmetry looks like in the lane's own numbers** (`ternary-reps-diag.json`, 2026-07-28): both arms
churn on the same market, and at the shared interval of 64 the binary legs banked ~105 and ~250 iterations
per archived attempt and **finished**, while the ternary legs banked ~32 and ~64 — r1 taking **26 attempts to
reach 13 commits**, i.e. its average attempt did not reach one checkpoint boundary. Same churn, different
cost per churn event.

**⚠ WHAT IT DOES NOT EXPLAIN.** Those ternary leg records read `status=failed`, and none of this diagnoses
why. Exposure is one lever — the one that decides what each reclaim costs — and it is worth pulling on its
own measured terms; the setup-side failure is `reps-setup-rss`'s subject.

### 4c-i · ⚠ A DEFECT THIS TURNED UP AND DELIBERATELY DID **NOT** FIX IN FLIGHT

`rbfe_spot_driver` rounds each phase target DOWN to a multiple of the interval, so an interval that does not
**divide** the derived warmup target silently shortens the equilibration. At 4 fs the target is
1600 = 2⁶ × 25 and every `MODES` interval divides it. At 2 fs it is 800 = 2⁵ × 25, and **64 does not divide
800**: `MODES["triangle"]` therefore runs **768 of its 800 warmup iterations, 4 % short** — while T1 *is* r0,
which ran on the GCP lane at `RBFE_WARMUP_CKPT_ITERS=8` (`gpu-ternary-fep-gcp.yml`) and equilibrated the full
800. The triangle mode's own comment is the argument for why that matters: *"anything that makes T2/T3's
protocol differ from T1's converts R from a path-error detector into a protocol-difference detector."*

It is **left alone** because those legs are billing. On a resume the interval baked into the committed `.nc`
overrides the environment (the driver's single-interval invariant), so re-cadencing the mode today would
leave started legs on 64 → 768 and give a fresh leg 50 → 800 — a protocol difference *within* the triangle,
strictly worse than the uniform one it has. The fix belongs to that lane, between rounds. Pinned by
`tests/test_ternary_ckpt_exposure.py::test_no_mode_silently_shortens_its_own_equilibration_except_the_one_already_known_to`,
which fails if any *other* mode acquires the same gap.

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

## 6 · Proposed edits to nr4a3-program-map.md and pricing.md

Written as exact deltas so the owner of those files can apply them without re-deriving anything. Nothing here
is applied by this lane; nr4a3-program-map.md is not edited by anyone but its owner.

**nr4a3-program-map.md → "Cost levers adopted 2026-07-24", lever 1.** Replace *"so 4 fs is exactly half the force
evaluations → ~$8.8/edge → ~$4.4"* with the ratio that survives the warmup:

> Iterations are timestep-independent, so 4 fs halves the force evaluations **in production**. The warmup is
> not halved: its iteration count is derived from the WARMUP integrator (1 fs), so 1 ns of equilibration is
> 1e6 steps at either production timestep. Per replica: 2 fs = 1.0e6 + 2.5e6 = 3.5e6 steps; 4 fs = 1.0e6 +
> 1.25e6 = 2.25e6. **Leg-level saving 1.56×, not 2×** (derivation + unit test:
> `research/compute/ternary-4fs-vast-findings.md` §1).

**nr4a3-program-map.md → per-edge bases table, "Ternary cooperativity edge" row.** The parenthetical
*"(400 equil + 2000 production at 2.5 ps/iter, `nr4a3_ternary_fep.py:343-344`)"* is the count for a warmup at
the **production** timestep. The as-run protocol sets `warmup_timestep_fs=1.0`, which makes it **800** warmup
iterations of the **same 1250 steps each** — so the as-run 2 fs leg is **2800 equal-cost iterations, not
2400**, and pricing it as `2400 × s/iter` understates by ~17 % (§2). Prefer pricing in **steps**: iterations
are not comparable across protocols.

**nr4a3-program-map.md → RUNG 2b entry.** Add the confound, because it changes what a NO-GO licenses (§2b): the 4 fs
arm necessarily carries pre-equilibration, `use_preequil` was never verified for the 2 fs baseline (only the
workflow default is recorded), and the settling observation is one `gcloud storage ls` of the setup-cache
prefix for a `v2pe` suffix. Agreement authorises adoption; disagreement is a NO-GO that must **not** be
attributed to the timestep.

**nr4a3-program-map.md → the trajectory requirement.** Record that it is now implemented, not just required:
`RBFE_POSITIONS_WRITE_PS` defaults to 50 ps (a 20-iteration stride, ~50 MB/leg, solute only) in
`nr4a3_ternary_fep._protocol`, and `rbfe_spot_driver` logs the resolved stride and shouts when it is zero
(§4b). Note that this changes the **GCP** ternary lane too, since both call the same engine.

**pricing.md → the ternary row's provenance.** Two amendments: (i) the 4 fs conversion factor is **0.643×**,
not 0.5×; (ii) the leg is 2800 iterations as run, not 2400. Both are arithmetic on the existing measured
per-iteration rate — neither requires a new measurement, and neither changes that rate.

**nr4a3-program-map.md → monitoring/infrastructure.** Record that the Vast lane has its own session-independent
watchdog (`.github/workflows/ternary-vast-watchdog.yml` + `ternary_vast_watchdog.py` +
`ternary-vast-watch.json`), and that `ternary-leg-watchdog.yml` remains **GCP-only** — it authenticates by
WIF, reads GCS, looks for `gcp-ternary-*` VMs and re-dispatches the GCP workflow, so pointing a Vast leg at
it yields monitoring that watches nothing. The Vast one requires the **committed iteration to have advanced**
before it says RUNNING, separates a recorded crash (FAILED, no relaunch) from a preemption (DIED, relaunch
from checkpoint), delegates capacity refusals to the launcher's destroy-and-exclude policy, and reads back
after arming so a leg cannot end up billing with an empty watch list. **It only fires once on `main`** — a
`schedule:` trigger does not run from a feature branch.

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
| 2:43 PM | **PREEMPTED at production ≥120/200** — routine spot behaviour; the capacity policy fired correctly on its first real encounter | `cur_state=stopped intended=stopped` → nudge → `{"success": false, "error": "resources_unavailable"}` → machine 12697 recorded blocked → instance destroyed rather than queued |
| 2:45 PM | relaunch **rented nothing and reported success** — Vast's 16,384-char onstart cap | HTTP 400 `invalid_args`, rendered onstart 17,017 chars (§8) |
| 3:03 PM | setup rebuilt on the new host; stage + pre-equil caches restored in seconds | `up=running`, `committed=production/120` |
| 3:22 PM | **resumed cleanly across a DIFFERENT GPU MODEL — production/160** | 4090 → 4080S; the checkpoint is platform-independent, as expected |
| 3:27 PM | **preempted a SECOND time** at production/160; same handling | machine 29668 → `resources_unavailable` → blocked → destroyed |
| 2:51 PM | resumed on a new host after stripping comments at render | instance 45832599, machine 29668, **RTX 4080S** $0.2196/hr; stage + pre-equil caches HIT, resumes from `production/120` |
| 2:19 PM | **production 40 committed at 4 fs** — equals the ENTIRE prior 4 fs evidence base, on a freshly built system | `instance=45827166 machine=12697 up=running committed=production/40` |

**Attribution.** Every reading above is keyed to the instance actually rented, not inferred from a poller: the
Vast query filters on the `tvast-` label, the S3 reads live under the `ternary-vast/` prefix, and the commit
prefix carries the unit id including `dt4.0fs`, which no other lane writes. The instance and machine id are
now printed on every progress line so this is evidence rather than an argument — the shared scratchpad turned
out to be shared across all five lanes, and a poller script there was overwritten between lanes, so "my poll
said it was advancing" is not on its own a statement about *this* box.

**Two distinct NaN risk points are now passed:** warmup iteration 1 at the softcore λ-states, and the
warmup→production hand-off where the sampler moves to the full 4 fs timestep.

**Recorded caveat on this probe specifically:** it was launched from commit `06dc6e04`, before the strided
trajectory setting landed, and before `PYTHONUNBUFFERED=1`. Its `[timing]`/`[barrier]` lines are therefore
block-buffered — which is how that defect was found (§4c) — and the per-iteration numbers above come from
openmmtools' own per-chunk estimates and from the S3 commit census, both of which are independent of the
buffered stream.


## 8 · Two infrastructure findings from the probe, both of the silent-success class

**(a) Vast caps the onstart script at 16,384 characters, and the failure is a GREEN job that rents nothing.**
Diagnosed from the API's own reply rather than inferred: the post-preemption relaunch returned
`HTTP 400 {"success": false, "error": "invalid_args", "msg": "...len(args) > 16384..."}`. The rendered
onstart had reached **17,017** characters — over by 633 — because three safety fixes had been added to the
pipeline since the launch that worked. Nothing in the code was wrong; it was simply too long. The shape is
what makes it dangerous: the launcher's per-unit `except` turns a create failure into a printed line inside
a job that exits 0, so the launch reported success, `--verify-armed` passed, and **no GPU was running**.

The fix is **not** fewer comments — 6,122 of those characters were full-line comments, the part that
explains why each step exists, which is exactly what this repo keeps paying for losing. Comments now stay in
the **source** and are stripped at **render** (15,136 → 9,013 pipeline chars; 17,017 → 10,774 onstart; 5.6 kB
headroom). `#`-leading lines are comments in both bash and Python, so the rule is safe inside the embedded
heredocs — asserted by `bash -n` on the rendered script and by `compile()` on both heredocs.
`build_jobspec` now **raises** over the cap, making it a build-time error a unit test catches.

**(b) `rbfe_spot_driver`'s progress lines are block-buffered.** It logs with a bare `print` and contains
**zero** `flush=True` (grep). Behind a pipe, Python block-buffers stdout at ~8 kB. Diagnosed by differential:
at 2:03 PM the S3 `run.log` carried every line printed with `flush=True` and not one `[spot-driver]` line
from the same process. Those lines are `[timing] … s/iter` and `[barrier] committed checkpoint at iteration
N` — the entire progress signal an unproven pipeline is monitored on. `PYTHONUNBUFFERED=1` fixes the class
without touching a file the GCP lane also runs.

**(c) A strict host filter costs real money in selection.** The lane asks for 8 vCPU / 32 GB / ≥60 GB disk /
`cuda_max_good ≥ 13.0` because the host builds the ~146k-atom hybrid itself. That narrows the offer pool, and
the resume landed on an **RTX 4080S at $0.2196/hr** against the first host's 4090 at $0.1527 — the best
all-in `$/ns` available *under that filter* at that moment, which is `_select_cheapest_offer` working as
designed ("the card is not the decision — the OFFER is"), not a bug. The lever that would relax it is an S3
**setup** cache (the stage and pre-equilibration caches already exist); with setup restored rather than
built, the RAM floor could drop and the pool would widen. Not built here; recorded as the next cheap
infrastructure win.

---

## 9 · State at hand-off (2026-07-25, 3:41 PM ET)

| unit | instance | machine | card | $/hr | state |
|---|---|---|---|---|---|
| probe (stage 1) | 45835634 | 46392 | RTX 4080S | 0.2071 | resuming from **production/160** of 200 |
| edge ternary_vhl | 45835957 | 114237 | RTX 4090 | 0.2237 | loading |
| edge binary_vhl | 45835971 | 46392 | RTX 4080S | 0.2105 | loading |
| edge solvent | 45835977 | 114273 | RTX 4090 | 0.2348 | loading |

All four are armed in `ternary-vast-watch.json` and `--verify-armed` passed for both modes.

**Realised $/hr is running ~50 % above the $0.137 planning rate** ($0.207–0.235 vs $0.137). The cause is
identified in §8c: the host filter (8 vCPU / 32 GB / ≥60 GB disk / `cuda_max_good ≥ 13.0`) exists so the host
can build the hybrid setup, and it thins the offer pool enough that selection has little to rank. Now that an
S3 setup cache exists, that floor is the next thing to lower.

**Two units share machine 46392.** `submit()` spreads one unit per machine *within a call*, and the probe was
rented by an earlier call — so the spreading rule does not see it. Not harmful (both are running), but a host
that loses its GPU would take two units with it; the exclusion set should be seeded from live instances as
well as from the blocked list.

**Projected spend for the whole lane ≈ $5.4** against a $25 ceiling: probe ~$0.34 across three hosts, edge
~$3.8 at these rates plus preemption overhead.
