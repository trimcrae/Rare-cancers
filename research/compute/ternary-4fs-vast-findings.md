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

**STRATEGY.md → monitoring/infrastructure.** Record that the Vast lane has its own session-independent
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
