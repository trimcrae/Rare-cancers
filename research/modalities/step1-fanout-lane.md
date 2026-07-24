# STEP 1 FAN-OUT — the cmpd19 congeneric RBFE lane (built 2026-07-24; run HALTED on cost)

**Status: BUILT and proven to sample; HALTED by trimcrae before any result.** 0 of 19 units produced a ΔΔG,
so there is **no scientific output from this run** — do not cite anything from it. What it produced was a
measurement that repriced the rung by ~4×, and four infrastructure defects found and fixed.

Schedule entry: `step1_fanout_cmpd19` in
[degrader-paper-schedule.json](../manuscripts/degrader-paper-schedule.json) (status back to `pending`).
Live prices: [research/compute/pricing.md](../compute/pricing.md) §A.

---

## 1. What the lane is

RUNG 4 of [STRATEGY.md](../../STRATEGY.md): turn the frozen perturbation map
(`congeneric-rbfe-map.json`) into RBFE ΔΔG values across the cmpd19 congeneric series.

**Unit = one map edge, at one microstate leg, on one receptor frame.** One rented GPU runs BOTH alchemical
legs (complex-morph + solvent-morph) and reduces them to ΔΔG_bind, so one instance yields one ΔΔG.

| file | role |
|---|---|
| `congeneric_fanout.py` | **pure core** (stdlib only): unit enumeration, scoping, cycle-closure bookkeeping, anchor-rooted ranking. Unit-tested, so the scoping decisions below cannot drift silently. |
| `congeneric_pose_stage.py` | RDKit, free CPU: builds the common-mode poses + per-pose QC. |
| `congeneric_fanout_vast.py` | Vast launcher: `plan / stage / precheck / launch / launch_confirm / collect / monitor / diag / stop`. |
| `nr4a3_rbfe.py` | the **unchanged** OpenFE engine each unit runs (`MODE=splittest`). |
| `tests/test_congeneric_fanout.py` | 19 tests; the CI job refuses to launch if they fail. |

Driven by `fusion-cpu-extras.yml` with `task=step1_fanout`, dispatched with `ref=<branch>`.

---

## 2. Scope — read before quoting the map as anything

The frozen map has three multiplicative axes. **Only the first was going to run.**

- **AXIS 1 — 19 edges × charge-CONSERVING (Δq=0) microstate leg, PRIMARY frame.** This is tranche 1, and the
  only thing the ~$12–26 line item ever covered.
- **AXIS 2 — 8 charge-CHANGING microstate legs. EXCLUDED, and blocked, not merely deferred.** The map's own
  `microstate_policy` requires a co-alchemical / analytical charge correction. `nr4a3_rbfe.py` implements
  neither, so these legs would carry an uncontrolled offset. `charge_changing_units()` enumerates them so the
  paper can say exactly which species were not computed, and why.
- **AXIS 3 — 6 receptor frames** (4 NR4A3 conformers + matched NR4A1/NR4A2 open frames). Each is another full
  tranche-1 spend.

**Consequence for the claim.** Tranche 1 yields a **single-conformer conditional relative-FE map**. It is
**not** the selectivity readout and **not** the "sensitivity ranges" the schedule title promises — those need
axis 3. `congeneric_fanout.plan()` emits the exclusion list machine-readably so this cannot be quietly lost.

Every ΔΔG is conditional on a **hypothesised** cmpd19 pose: there is no solved NR4A3 cocrystal, only functional
target engagement. Accuracy is not established by this lane; it rests on valA_mini + OpenFE's published
benchmark for this protocol.

---

## 3. Pose staging — why not re-docking

RBFE's cost advantage rests on the common-mode assumption: both endpoints share a binding mode so the shared
scaffold cancels. That has to hold **geometrically**, not just chemically — otherwise LOMAP's distance filter
rejects a valid topological map (the 2026-07-14 `n_mapped=1` root cause).

Independently re-docking the 17 analogues would **not** give that: smina places each in its own local optimum,
and a 0.5–1.5 Å core displacement is invisible to a docking score and fatal to the morph. So every analogue
**inherits the anchor's core coordinates atom-for-atom** from the one docked cmpd19 pose (smina, frozen
nr4a3_design Pocket-5 box, run 29175736795), then MMFF-relaxes the substituent with that core held fixed.

17/17 staged clean. QC per pose: core size, core RMSD (~0 by construction — verified, not assumed), and
receptor fit at two cutoffs. A 1.6–2.0 Å contact is a soft overlap the MD's own minimisation relieves
(recorded only); under 1.6 Å flags `needs_pose_revalidation` — a finding about the 5-position exit-vector
hypothesis, not a staging bug. Neither blocks the edge.

---

## 4. The run

Launched 2026-07-24 ~4:19 PM ET, wave 1 = 8 of 19 units, Vast RTX 4090 interruptible. Halted ~5:15 PM ET.
**Realized spend ~$2**; teardown verified `live_instances=0`, nothing idle-billing.

**The lane works.** Three hosts reached 95–99% GPU utilisation on the real cmpd19/NR4A3 system and advanced
steadily to iteration ~124–160 at ~13.6 s/iter. The only thing that stopped it was the spend decision.

Preserved for resume: partial sampler checkpoints under `nr4a3-step1-fanout/results/<unit>/ckpt`, staged poses
under `nr4a3-step1-fanout/stage/`. A re-dispatch **resumes**, it does not restart.

```
fusion-cpu-extras.yml  task=step1_fanout  fanout_mode=precheck        # free, confirms the staged tree
                       task=step1_fanout  fanout_mode=launch_confirm  # SPENDS; tops the fleet up to width
```

---

## 5. Why the cost estimate was ~4× off

The pinned $12–26 became a measured **~$91–101**. Two independent errors that multiplied, plus a process
failure that let both through.

**(a) Wrong molecule — 2.6×.** The rate labelled **MEASURED** was the *public TYK2* benchmark edge, not
cmpd19/NR4A3. Same card class, same 12 windows, same 2.5 ps/iteration; aggregate MD throughput **498 ns/day
(TYK2) vs 190 ns/day (NR4A3)**, from three independent hosts (14.42 / 12.76 / 13.70 s/iter, 16 samples each —
tight enough to rule out host variance).

**(b) Wrong bid basis — 3×.** $0.122/hr came from **one instance**. Wave 1 drew 8 hosts at $0.35–0.39/hr.

**(c) The process failure.** The caveat was already written *in the same file, three lines below the number*:
"the probe re-runs the (already-passed) TYK2 valA edge; to make it real science + cost, point it at a live
cmpd19 step1_fanout edge". `git log -S` shows the $12–26 and the 5.2 s/iter row landed in the **same commit**
(`8f4c0dd`) — caveat and number authored together, then the number propagated into STRATEGY.md, the rung table
and the schedule while the caveat stayed put. **The bolded MEASURED label conferred authority that suppressed
the scrutiny the adjacent sentence was requesting.** It *was* measured — of the wrong thing.

### ⚠ Still unresolved: the mechanism of the 2.6×

Two candidates, **both unmeasured for these edges**:

1. **Particle count.** No NR4A3 *binary*-RBFE particle count is recorded anywhere in this repo (the ternary's
   146,509 is). The wave-1 setup logs that carried it were lost to defect (d) below; the fix is in, so a
   resumed run captures it.
2. **Timestep ceiling.** 4 fs vs 2 fs is a clean 2× and is a documented **per-edge** property here.

### ✅ RESOLVED 2026-07-24 (free CPU, no GPU) — timestep is EXCLUDED, and there is no 2× lever

Reading the **effective** protocol settings off a real hybrid build instead of assuming them:
`forcefield_settings.constraints == "hbonds"`, `hydrogen_mass == 3.0`. That is **OpenFE's default**, which the
production lanes inherit because they set nothing. Under it, **every X-H is a constraint**: `xh_total = 0` on
both known-answer anchors against 1771 / 4997 total constraints, and the alchemical valence `CustomBondForce`
(11 / 28 bonds) contains **no X-H at all**. Nothing is left flexible to cap the timestep, so **the fan-out ran
at 4 fs** and the ~$91–101 stands on that axis.

**Particle count is therefore the sole remaining candidate for the 2.6×**, and it is still unrecorded for the
NR4A3 binary complex. Capture it on any resumed run — the leg log now uploads unconditionally, so the setup
line survives.

Three defects in the scan itself, all now fixed:

1. **`RBFE_FORCE_CONSTRAINTS=hbonds` was always a no-op** — it set what was already the default. The header
   comment justifying it ("run-1 diag: `xh_total == xh_unconstrained` for every edge") does not match any
   build observed here.
2. **The gate was unsatisfiable by construction.** Under an all-constrained build `xh_unconstrained` is
   structurally 0, so every edge verdicts 4 fs — yet the calib anchor expected 2 fs. No build could satisfy it,
   which is the entire reason 0/19 designed edges were ever scanned. The expectation is now **4 fs**, corrected
   with evidence: `pricing.md` attributes the Wurz ternary NaN to the **homology model's softcore instability**,
   not to a timestep ceiling, and the build has nothing unconstrained to cap a timestep with.
3. **It measured a system production does not build** — production forces nothing. Default is now `production`;
   `SCAN_CONSTRAINTS=hbonds` reproduces the old behaviour for comparison.

**The per-edge scan is largely moot under this build**: it cannot discriminate what the constraint setting
makes uniform. Its remaining value is the force census + effective-settings record, not a per-edge verdict.
A hypothesis worth keeping honest: `count_morphing_xh()` was added to count X-H whose existence/geometry
changes between endpoints — a property of the *perturbation* rather than the setting. It reports 0 on both
anchors here, which under an all-constrained build is expected and therefore **does not validate it**. It would
only become meaningful on a build that leaves ligand X-H flexible.

---

## 6. Bid logic — how $0.37/hr passed a $0.30 estimate

```python
_VAST_BID_FLOOR_MULT = 1.9
bid = min_bid × 1.9          # and on Vast you PAY YOUR BID
```

`min_bid` is the market clearing floor, so we bid **90% above market by policy**. Working back from the
realized $0.35–0.39/hr, the floors were **$0.184–0.204** — a **~$0.17/hr premium per instance**, ~$1.30 per
13.7-hour unit.

**The defect (FIXED).** `_select_cheapest_offer` compared its ceiling `max_hourly_usd` to **`min_bid`** — the
floor — not to the bid. With `hourly_usd(vast, rtx4090)=$0.30` → cap $0.60 and a 1.9× multiplier, the guard
permitted an effective **$1.14/hr** before rejecting anything: no ceiling on the billed rate at all. The
ceiling now governs the effective bid for interruptible offers (ranking still uses `min_bid`; a constant
multiplier preserves ordering). On-demand is unchanged — it is billed at `dph_total`, so its check was always
correct. Regression test pins the boundary at `ceiling/mult` in both directions.

**Why 1.9 is wrong for this lane.** `27bd327` (2026-07-23) raised it 1.5→1.9 for the **covalent endpoint-MD
panel**, where a preemption cost a ~20-minute fat-image reload on long legs. The RBFE fan-out checkpoints
every 20–40 iterations, so a preemption costs **~5–9 minutes of sampling** — an order of magnitude less. The
multiplier is global and was silently inherited. It did not even work: s1f-03 was preempted anyway at 1.9×.

**The lever, not yet pulled:** `VAST_BID_FLOOR_MULT` is already an env var and can be set per lane. ~1.2 is
defensible for a per-iteration-checkpointed fan-out — at today's floors ~$0.22/hr instead of $0.37, taking the
tranche from ~$95 to ~$57 on bid alone. **Left at 1.9**: changing the default is a policy call across every
lane, and one of them was tuned into it deliberately.

On the $0.122 basis: 1.9 was *already* in force when it was measured, so that instance's floor was ~$0.064 —
the single cheapest 4090 on the market at that moment, vs $0.184 today. A genuine ~3× market move, not our own
policy change. The eight realized rates clustered within 11%, so "needing 8 hosts instead of 1" cost almost
nothing — the market moved and there was no ceiling to catch it.

---

## 7. Defects found and fixed (all live in the lane now)

**(a) Pose staging froze the embedding error in place.** Four poses failed QC, three at an identical 1.12 Å.
First hypothesis — symmetry-equivalent atom mapping — was **refuted** by instrumenting: all four reported
`n_core_candidates: 1`, so there was no alternative mapping to choose wrongly. Real cause:
`MMFFAddPositionConstraint(idx, 0.0, 1e3)` restrains an atom to **where it already is** after the embed. ETKDG
treats `coordMap` as distance bounds only, so the 3-methyl-ester (3 heavy atoms of a 13-atom core) could settle
in the opposite rotamer — 3 atoms displaced ~2.2 Å over 13 is ~1.1 Å RMSD, matching the observed values
exactly. Now the core is copied atom-for-atom and minimised with those atoms **fixed**.

**(b) The reaper read the host's uptime as our rental age.** `age_min` showed 209141 (145 days) on
freshly-rented boxes: on a Vast instance object `duration` is the **host machine's** uptime; the rental start
is `start_date`. Collect reaps on age, so **the first collect would have destroyed all 8 units mid-leg.**

**(c) A failing leg discarded its log.** The leg ran as `$PY nr4a3_rbfe.py | tee log` under `set -e` +
`pipefail`, so a non-zero exit aborted the function **before** the `s3 cp` — the diagnostic was thrown away in
exactly the case it was needed. Now errexit is disarmed around the engine, the rc is captured, the log ships
unconditionally, and the phase marker records the failure code. `DIAG=1` also pulls container stdout straight
off the instance, which survives when the pipeline died before uploading anything.

**(d) The Vast create/start race.** s1f-01 sat at `cur_state=stopped` with an **empty** `status_msg` for 30
minutes — distinct from instances also showing "loading" whose `status_msg` reported an image pull in
progress. `gpu_backend._ensure_running` documents the race but retries only ~48 s at submit. Every progress
check now re-issues the start for any `s1f-*` at `cur_state=stopped` whose unit has no result yet; idempotent,
and a finished unit is never restarted.

---

## 8. Operational notes for whoever resumes

- **A CI job log is only readable from its tail, and the tail is always runner boilerplate.** `monitor`,
  `collect` and `diag` write their readouts to files that CI commits back to the branch. Read those, not the log.
- **All three cycle-closure edges are in the LAST wave** (units 16–18). As ordered, no partial run can check
  internal consistency — reorder if a reduced tranche is ever wanted.
- **Card choice is not a saving.** At current rates a 4090 and a 3090 cost essentially the same per iteration,
  and the 3090 takes 2.4× the wall-clock. Do not "economise" by downgrading.
- **A transient `exited` is not a failure.** s1f-04 read `exited` at 10 min and came back `running` on its own.
  Spot churn is routine; the checkpoints absorb it.
- **Pre-existing and untouched:** 3 failures in `tests/test_ternary_convergence_pure.py`, verified identical on
  a clean tree. Another lane's.
