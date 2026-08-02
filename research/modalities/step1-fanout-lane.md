# STEP 1 FAN-OUT — the cmpd19 congeneric RBFE lane (built 2026-07-24; RESUMED 2026-07-26)

**Status: RUNNING (wave 2, resumed 2026-07-26 ~3:53 PM ET).** Wave 1 was halted on cost before any result and
produced **no scientific output** — do not cite anything from it. What it produced was a measurement that
repriced the rung by ~4×, four infrastructure defects, and partial checkpoints that wave 2 **resumes from**.

Schedule entry: `step1_fanout_cmpd19` in
[degrader-paper-schedule.json](../manuscripts/degrader-paper-schedule.json).
Live prices: [research/compute/pricing.md](../compute/pricing.md) §A. Bid policy:
[bid-strategy.md](../compute/bid-strategy.md) §7.

---

## 0. Wave 2 — the resume (2026-07-26)

**The shape of the run, and why it is not 19-wide from the first minute.** CLAUDE.md's litmus test — *is
there a result this shard could return that would make me NOT run the rest?* — answers **NO** for a congeneric
map, so there is no decision value in serialising and parallel costs the same GPU-dollars. But wave 1 left an
asymmetry that the litmus test does not cover: it proved the lane **SAMPLES** (three hosts at 95–99 % GPU on
the real cmpd19/NR4A3 system) and **0 of 19 units ever reached a ΔΔG**, so the *terminus* — reduce both legs,
write `ddg.json`, upload — has never once been observed. Fanning 19 wide into an unproven terminus risks
paying 19× for zero results, which is this lane's existing failure record, not a hypothetical.

So: **one unit first, chosen as the most-advanced checkpoint** (closest to the terminus ⇒ cheapest proof of
it), then **all 18 remaining at once**. That is maximum parallelism subject to proving the terminus once, and
it costs ~1 unit of wall-clock against the risk of 19 wasted rentals. `FANOUT_ONLY` is the lever; without it
"one unit" would have meant unit 00 rather than the one that is furthest along.

**The fan-out is released by a machine condition, not by an agent remembering to come back.**
[`step1-fanout-autoscale.yml`](../../.github/workflows/step1-fanout-autoscale.yml) ticks every 20 min —
progress check → collect → **terminus-gated** launch — and `FANOUT_REQUIRE_PROVEN_TERMINUS=1` refuses to
submit until a `ddg.json` exists in S3. So the remaining 18 go out the *minute* the shakeout unit lands one,
and cannot go out before. That is strictly more parallel than waiting for a human to notice and strictly
safer than launching early, which is the combination the shakeout rule is actually asking for.
Verified end-to-end 2026-07-26 (runs **30218758883**, **30218885472**): every step green, the gate correctly
**held** at one live instance, and `collect` assembled the map with cycle-closure bookkeeping reporting all
three cycles incomplete and naming their missing edges.

**The four wave-1 survivors, by committed iteration** (census over the spot commit store, 2026-07-26 3:47 PM
ET):

| unit | committed |
|---|---|
| **`…cw_ev_5cooh…neutral_acid`** ← **shakeout unit** | complex/warmup@**160** |
| `…cw_ev_5pegamine…` | complex/warmup@140 |
| `…cw_ev_5alkyne…` | complex/warmup@120 |
| `…cw_ev_5ch2nh2…` | complex/warmup@60 |

The other 15 units are cold and start from staging.

> **⚠ The warmup and production iteration TARGETS are deliberately not quoted here, because nothing in this
> repo has measured them for this leg and a derived one would be quotable within the hour.** They are
> `equilibration_length / time_per_iteration` and `production_length / time_per_iteration` — the lengths are
> set in `nr4a3_rbfe.py` (1.0 ns / 5.0 ns), but `time_per_iteration` is an inherited OpenFE default this lane
> has never read off a real build, and the repo carries an unreconciled 2.5 ps/iteration figure elsewhere. The
> authoritative value is the driver's own `[spot-driver] warmup_target=… prod_target=…` line, which ships to
> S3 with the leg log when the leg ends; the commit-store census also reveals the warmup target for free the
> moment a unit crosses to `complex/production@…`. **Until one of those lands, any ETA built on an iteration
> count is arithmetic on an assumption** — which is the exact defect STRATEGY.md's correction table row 19b
> records four times over.

### The bid, and what it says about the retracted $91–101

Wave 2's first rental: Vast **45936074** on machine **18857**, RTX 4090, **charged $0.1224/hr** — against
wave 1's **$0.35–0.39/hr** for the same card class on the same market days later. That gap is the retired
`×1.9` bid multiplier, not the market, exactly as §6 reconstructs. At ~13.7 reference-GPU-h per unit that is
**~$1.68/unit ⇒ ~$31.9 for the 19-unit tranche**, *under* nr4a3-program-map.md's **~$36** planning figure and nowhere
near the retracted $91–101.

**And the throughput reproduces the measurement.** The host advanced **160 → 260 committed iterations** across
~23 min of sampling = **~261 iter/h**, against the **~265 iter/h** implied by wave 1's three hosts
(12.76 / 13.70 / 14.42 s/iter). So this host runs at full card rate and the starvation question is answered
for it **with data**, which matters because the obvious signal did not survive contact: `gpu_util` read
**None under both spellings** while the box was demonstrably advancing. A monitor whose only health signal can
silently go absent watches nothing — so the committed-iteration **rate** is the throughput signal this lane
uses. It comes from our own object store rather than the provider's telemetry, and it measures the realised
throughput of *this* workload rather than a proxy for it.

⚠ **Read rates over long windows only.** The commit store advances in blocks (20 iterations in warmup, 40 in
production), so a short window is quantised: the same healthy host reads 109 iter/h and 300 iter/h across two
consecutive ~10-min windows, and only the multi-block window gives 261. This is the same commit-block
quantisation that produced three wrong ETAs in STRATEGY.md's correction table (row 19b) — it is a property of
the checkpoint interval, not of the host.

### ⚠ The 2 h 57 min that looked like a hung sampler and was an image pull (2026-07-26, LANE 21)

The shakeout unit was preempted off Vast **45936074** at 4:31 PM ET at `complex/warmup@260` and auto-resumed
onto **45938720**. `vast-watchdog` then reported the same verdict four passes running —
`STALLED … frozen at leg-complex-running/260` — and correctly declined to relaunch. The verdict was right and
useless: **the 260 was 45936074's last commit, and 45938720 had not executed one instruction.**

**The evidence, three independent records agreeing.** (1) Vast `actual_status` read `loading` on every
autoscale tick from 4:39 PM to 6:52 PM ET, with `status_msg` cycling docker layer lines
(`Pulling fs layer` → `79436a159dbf: Pull complete` → `4f4fb700ef54: Pull complete`) — the trail is in this
lane's own committed `step1-fanout-progress.json` history. (2) The container's stdout begins
`Sun Jul 26 23:31:48 UTC 2026`, i.e. **7:31 PM ET**, its first line. (3) `phase.txt`'s first write from that
box is `boot 2026-07-26T23:31:56Z`, eight seconds later — which incidentally proves the S3 upload path was
never the problem. Container start therefore lagged the rental by **2 h 57 min**, all of it billed.

That rules out every MD-level hypothesis at once — a dead sampler, a swallowed NaN, a hung resume, a broken
commit/upload path, a per-window stall in warmup. **None of them can happen on a container that has not run.**

**The rate, measured rather than assumed.** `triskit23/nr4a3fep:latest` is **2.91 GiB** compressed (the tag's
own `full_size`), so 177 min of pull is **~2.4 Mbit/s** — against the offer's advertised `inet_down` of
**142.4 Mbit/s**, a **~60× shortfall**. So an advertised-bandwidth floor in offer selection would **not** have
caught this: 142 Mbit/s passes any sane threshold. The only signal that separates a slow host from a normal
20–40 min pull is the **observed time to container start**, which is why that, and not `inet_down`, is what
the watchdog now measures. (`gpu_util` is likewise no help: it read `None` throughout the pull, then
`99.99 %` ninety seconds into boot, then `0.0` — LANE 17's finding that this field is not usable here holds.)

**Why the watchdog structurally could not say this.** `classify()` reached `SETUP_STALL` only via
`progress_scalar <= 0`. The scalar is **unit-scoped and durable in the object store**, so it survives the
host — a resumed unit arrives on a fresh box carrying its predecessor's number, and that gate is unreachable
for it ever after. The policy was reading a unit-scoped counter to answer an instance-scoped question. Fixed
by `watchdog_policy.classify(container_started=…)` + `vast_watchdog.container_started_from_phase()`, which
derives the bit from the phase marker's own timestamp against the rental's `start_date`, and by
`container_diag()`, which puts Vast's `actual_status`/`status_msg` **beside every stall alert** — those
fields were in the instance record the whole time.

**What now self-recovers.** A never-started container past the cold-start grace is `SETUP_STALL`, and
`Step1FanoutKind.quarantine()` destroys the box and adds its machine to the lane exclusion set. That is
**not** a relaunch — `should_relaunch` still authorises `DIED` alone, and a test pins it. The unit reads
`DIED` on the next pass and goes out through the existing capped, interlocked path, with the bad machine
already excluded: CLAUDE.md's rule for a Vast host that never starts, executed without a human.

**Two further defects the same incident exposed.**
- **An `exited` Vast instance is not provably dead.** 45938720 read `actual_status="exited"` at 7:49 PM ET
  and was re-marking `boot` on the **same instance id** two minutes later; the container stdout carries both
  boot sequences. `probe` treats `exited` as not-alive, so that unit reads `DIED`, and `DIED` relaunches —
  two hosts on one checkpoint prefix, arriving by a route the `owning_workflow` interlock cannot see.
  `Step1FanoutKind.reap_exited()` now destroys the ambiguous box **before** renting the replacement, and a
  failed destroy withholds the relaunch rather than risking two writers.
- **`mode_launch` crashed on its own success line.** `_lprint(…, flush=True)` — `_lprint` is not `print` —
  raised `TypeError` on the **first successful submission**, reachable only when money was being spent. In
  autoscale run **30226203566** it rented instance 45951628 and died *before* the rental-ledger write,
  `_arm_watchdog` and the launch readout: a host billing while invisible to realised spend **and** to the
  watch list. A second copy sat in the submit-**failure** handler, whose entire job is to survive a Vast
  capacity refusal. Both fixed; `tests/test_congeneric_fanout.py` now binds every internal call in these
  modules against its callee's signature statically, and `mode_monitor` **backfills** a live rental that has
  no ledger row.

**Realised cost of the stalled window: $0.159** (45938720, 3.33 h at $0.0476/hr, from the lane's own
`_rentals.json`), against $0.09 for the productive 45936074 rental. The lane's `STARVED HOST` guard finally
condemned 45938720 at 7:53 PM ET on `gpu_util=0.0 %` and excluded machine **28164** — the right outcome, but
reached through a field that reads `None` on other hosts, which is precisely why the container-start signal
above does not depend on provider telemetry.

**Recovered, and confirmed past the resume point** — the test that matters, because a relaunch that returns to
260 and stops again is the same bug, not a recovery. Third host **45951628** (RTX 4080S, **$0.2247/hr**)
started its container in **21 min** against 45938720's 177, marked `leg-complex-running` at **8:12 PM ET**,
and the watchdog read **`leg-complex-running/300`, prev 260, stall 0** at **8:29 PM ET** — two commit blocks
past the resume point, on a host whose GPU read 0 % → 81 % → 100 % as the sampler spun up.

**No iter/h is quoted for this host, and that is deliberate.** 40 iterations is TWO commit blocks, and §0
above records that the same healthy host reads 109 and 300 iter/h across consecutive short windows purely
from block quantisation; the window also contains an unknown amount of OpenFE resume setup. A rate off it
would be the row-19b defect again. What the two points DO establish is the only thing that was in question:
**the counter cleared 260**, so this is a recovery and not the same failure re-run.

⚠ **The tranche projection needs re-deriving before it is quoted again.** `~$31.9` was built on the
**$0.1224/hr** the first wave-2 host was charged; this host bills **$0.2247/hr**, ~1.8× that, because machine
28164's exclusion pushed selection onto a higher floor. One unit is not a market, so nothing is restated here
— but if the 18 land in that band the tranche is ~**$58**, over the ladder's **~$36**. Re-run
`vast_cost_model.py` off the real `_rentals.json` once the fan-out has a few hosts, and do not carry $31.9
forward on this evidence.

### Timestep — 4 fs here is NOT an import from the ternary lane

RUNG 2b's 4 fs adoption passed on 2026-07-26 on the **ternary VHL calibration system**, and it is deliberately
**not** what justifies 4 fs here. This lane's timestep is settled **on this system, by its own evidence**, and
predates that result:

1. **The RUNG 2 pilot ran clean at 4 fs on an edge of this very series** (`cmpd19 → cw_ev_5nh2`) and converged
   (ΔΔG_bind = +1.84 ± 0.36 kcal/mol). A converged, NaN-free production run *is* the stability test.
2. **A force census on a real hybrid build of that same edge** —
   [`congeneric-edge-timestep-table.json`](./congeneric-edge-timestep-table.json), `ANCHOR_pilot_5Br_to_5NH2`
   — records `constraints_setting: "hbonds"`, `hydrogen_mass_setting: "3.0"`, `xh_unconstrained: 0` against
   1771 total constraints, and therefore `max_stable_timestep_fs: 4.0`. Nothing is left flexible to cap the
   timestep. This was measured with **no MD and no GPU**.

`nr4a3_rbfe.py` sets no timestep at all — it inherits OpenFE's protocol default, which is what both the pilot
and wave 1 ran under, and wave 2 changes nothing. **There is no extrapolation to price**, and the ternary
result is not load-bearing for this lane in either direction.

---

## 1. What the lane is

RUNG 4 of [nr4a3-program-map.md](../manuscripts/nr4a3-program-map.md): turn the frozen perturbation map
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
(`8f4c0dd`) — caveat and number authored together, then the number propagated into nr4a3-program-map.md, the rung table
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
_VAST_BID_FLOOR_MULT = 1.9   # ⚠ HISTORICAL — retired 2026-07-25, see research/compute/bid-strategy.md
bid = min_bid × 1.9          # and on Vast you PAY YOUR BID (confirmed by measurement, up to an on-demand cap)
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

## 7b. What wave 2 added around the sampler (2026-07-26)

Wave 1's gap was never the sampler. It was everything around it: nothing could tell an *advancing* unit from a
*wedged* one, nothing stopped the fleet stacking on one host, and nothing recorded what was actually spent.
All three are why a ~4× cost error stood unnoticed for two days.

- **Committed-iteration census.** `phase.txt` says which phase; it structurally cannot say whether that phase
  is moving, and a rented box can sit up with a wedged container reporting `leg-complex-running` forever. The
  spot commit store can, so `monitor` now censuses it and **diffs against the previous check**. The scalar is
  leg- and phase-ranked because it legitimately **restarts twice** per unit (warmup→production,
  complex→solvent) and **freezes twice more** (MBAR at the end of each leg); tests walk a whole unit lifetime
  and assert monotonicity. An unlistable store returns **−1, never 0** — reading a network blip as zero
  progress manufactures a stall.
- **Cost is derived, never typed.** `UNIT_GPU_H` and `VAST_4090_USD_PER_H` were hand-carried and both wrong,
  in the same direction, at the same time. They now come from `vast_cost_model.LADDER_REFERENCE_GPU_H` and the
  `vast-ladder-repricing.json` market snapshot, so nr4a3-program-map.md's ~$36 and the launcher's own print cannot
  disagree.
- **Rental ledger** (`…/results/_rentals.json`). `step1-fanout-handles.json` is rewritten by every launch, so
  a two-stage fan-out loses the first stage's rental — the exact way the last cost figure became a memory
  instead of a measurement. The ledger is append-only in S3, prices on the **bid** (what Vast charges), and
  **freezes billed minutes before the reap**, because after the DELETE the instance is unreadable.
- **Host exclusion in S3** (`…/results/_excluded_machines.json`), not in a process, so a launch inherits what
  a previous run's monitor learned with no agent awake. `$/ns` ranking multiplies a **card constant**, so it
  is blind to a host slower than its card exactly as it is blind to one that never starts.
  **⚠ Scope deliberately narrow.** pricing.md §A.1 proposed "exclude any low-`gpu_util` machine" and then
  **withdrew** it: the low utilisation there was PLUMED's CPU-side metadynamics bias, and the same host ran at
  74 % on the next unbiased phase. That escape does not exist for this workload — plain RBFE, no bias, no
  per-step host-side work — so the card constant *is* the throughput model here and the narrow rule applies.
  The withdrawn broad rule is not being re-adopted.
- **Watchdog coverage.** A `step1_fanout` kind in `vast_watchdog.py`, so units are covered
  session-independently. Every question the shared policy asks is answered from this lane's own code — result
  key, commit store, the leg wrapper's own `FAILED`/`NORESULT` markers, `build_jobspec` for the relaunch.
  **Entries are armed as units are launched, never in advance:** an entry for an unlaunched unit has no phase
  marker and no instance, so past the cold-start grace the engine calls it DIED and relaunches it — the watch
  list would start renting GPUs nobody authorised.

## 7c. `cw_bio_nmethyl_amide` — the one edge that will NOT be computed, and why (2026-07-27)

**Unit `e_zaienne_cmpd19__cw_bio_nmethyl_amide__neutral__neutral` (label `s1f-09`) is BLOCKED. It is a
scientific result about that edge, not a retry candidate.** 18 of 19 tranche-1 edges remain live; no
cycle-closure edge is affected (the three are units 16–18).

**The symptom.** `phase.txt` read `leg-complex-FAILED-rc1` at **9:12 AM ET** (and once before, at 8:55 AM ET
— it had already re-rented itself once). `rc1` is a bare exit code and says nothing; the leg log, which this
lane now ships unconditionally, carries the actual abort:

```
[rbfe] LOMAP element_change=False: 17 mapped atoms for zaienne_cmpd19->cw_bio_nmethyl_amide
  ABORT: DEGENERATE atom map — mapped 17 atoms ... below the PROVABLE floor 20 (a complete map of 22
  atoms exists) ... Most likely the LOMAP MCS hit its 300s budget (RBFE_LOMAP_TIME_S); raise it and re-run.
```

**That last sentence is the abort message guessing about itself, and it is wrong.** The chemistry is a single
mid-chain heavy-atom substitution — `zaienne_cmpd19` is the methyl **ester** `COC(=O)c1c[nH]c2ccc(Br)cc12`,
`cw_bio_nmethyl_amide` the N-methyl **amide** `CNC(=O)…`, i.e. O→N. A strict-element MCS cannot cross it and
loses everything beyond: the O, the methyl C and its 3 H — exactly 5 atoms, and 22 − 5 = 17.

**Measured, on the PRODUCTION staged components** (`step1-map-diag.json`, not `atom_map_audit.maps`, whose
own docstring disclaims its fresh-ETKDG harness as not evidence about this lane):

| mapper / setting | mapped | wall |
|---|---|---|
| LOMAP `element_change=False` | 17 | 0.01 s at **both** t20 and t300 |
| LOMAP `element_change=True` | 19 | 0.01 s at **both** t20 and t300 |
| Kartograf (geometric) | 18 | — |
| **provable floor** | **20** | complete map = 22 |

Identical maps at 20 s and 300 s in 0.01 s is the observation that **refutes the timeout hypothesis**: the
budget is nowhere near binding. What separates the two settings is the element change, exactly as
`_mapping`'s own docstring predicts ("a real element-change asymmetry moves the two settings apart").

**Two things were fixed, and one deliberately was not.**

1. **`_mapping` now escalates** to `element_change=True` when — and only when — the strict map is below the
   provable floor. Scoped that tightly because a running leg has already passed `_check_mapping_sane` at or
   above the same floor, so the clause is unreachable for every unit in flight and their mappings are
   byte-identical; changing a mid-flight leg's perturbation would be a silent protocol deviation. Swept all
   19 edges: exactly one sits below its floor, and a test pins that, because a second would invalidate the
   argument.
2. **`block` (a UNIT) is now distinct from `reap` (a HOST).** `_pending` meant "no ddg.json yet", so an edge
   that *cannot* produce one never left it and every tick rented a fresh host to fail identically — small per
   attempt, unbounded in time. Blocks are durable in S3, announced by `_pending`, and named in the map
   artifact.
3. **NOT fixed: the edge itself.** The escalation takes it 17 → 19 and it still aborts at 20. No available
   mapper reaches the floor, so it is not runnable at the current field-standard settings and no rental will
   change that. **⚠ A CORRECTION REGISTERED, not dropped:** the first write-up of this said element_change=True
   "maps all 22" — that was an rdkit-MCS number read as a LOMAP prediction. LOMAP returns 19.

**Is the floor over-strict? Measured 2026-07-28 — no, and the 19 is worse than a near miss.** A count under a
floor is what retires an edge, so the count alone is not enough evidence to spend that: `n_mapped = 19` against
`floor = 20` is equally compatible with "the search nearly succeeded" and "the search failed and produced
nonsense". `step1_map_diag` now records **which** atoms each mapper leaves unmapped and **which element
substitutions the map itself makes**, on the production staged components. For this edge
(`step1-map-diag.json`, row `zaienne_cmpd19->cw_bio_nmethyl_amide`):

| mapper | mapped | atoms of A left unmapped | element changes the map makes |
|---|---|---|---|
| LOMAP `element_change=False` | 17 | `C12` (methyl C), `O13` (ester O), its 3 H | none |
| LOMAP `element_change=True` | 19 | the 3 methyl H only | **`O->N` and `C->H`** |
| Kartograf | 18 | `C12` and its 3 H | `O->N` |

**`C->H` is the finding.** To reach 19, LOMAP has to map the ester's methyl **carbon** onto a **hydrogen** of
the amide — a heavy atom to a hydrogen. That is not a near-complete map two atoms short; it is precisely the
degenerate correspondence the floor exists to reject, and it would define an alchemical transformation nobody
would run. The two mappers that stay chemically sane (strict LOMAP, Kartograf) top out at 17 and 18. So the
floor is not over-strict here: it is the only thing standing between this lane and a nonsense perturbation.

**And the exclusion is a statement about the MAPPERS, not about the chemistry — so it is revisitable.** A
complete 22-atom map provably exists (the two heavy-atom graphs are isomorphic up to the single O→N
substitution; `atom_map_audit.edge_bounds`). Nothing about this edge is unmappable in principle; what is
missing is a mapper that finds it. That is a `method-watch` item, not a dead end: if a mapper ever returns ≥ 20
here, `FANOUT_UNBLOCK=1` lifts the block and the edge runs like any other. Until then the lane's denominator is
**18 computable edges of a 19-edge map**, derived from the block map rather than typed
(`congeneric_fanout_vast.computable_units`).

**Second-order finding, recorded and deliberately NOT acted on mid-flight.** On every bioisostere edge the
strict map is 3–5 atoms smaller than the element-agnostic one (tetrazole 16 vs 21, hydroxamic 17 vs 20,
acylsulfonamide 17 vs 22 by rdkit MCS). Those clear their own — lower, non-provable — floors and so *run*,
with a strict map that annihilates and recreates atoms an element-agnostic map would have mapped 1:1.
`atom_map_audit` already classifies these edges `prefer_element_change: true`, and production never passes
that flag (`nr4a3_rbfe.py:662` and `:784` call `_mapping` positionally). Plumbing it through would change the
perturbation of legs that are currently sampling, so it is a **post-fleet** change, not a live one.

## 7d. The anti-idle guard is now wired to step 1 — and here is the evidence it rests on (2026-07-27)

**Why it could not be wired before.** `vast_idle_guard` keys on two signals and step 1 emitted **neither**:
`phase.txt` moves only at phase boundaries, and the leg log was uploaded once, at leg end. Between those, a
wedged box was indistinguishable from a healthy one — which is how instance **45996071 crash-looped on a dead
credential for over an hour at $0.2497/hr with 0 % GPU** while every existing guard passed it.

**What the pipeline emits now**, in the ternary lane's shapes unchanged, so one guard reads one convention:

- `$RESULT_S3/run.log`, re-PUT every `S1F_SYNC_S` (default 120 s) during **every** phase, plus at each `mark`.
  The engine's stdout goes to `/tmp/$L.log`, so run.log is legitimately silent for hours — the PUT refreshes
  the object's **mtime**, which is what the guard reads.
- `$RESULT_S3/attempts/run-<UTC>.log`, archived at container start **before** the first `mark` (the ordering
  the ternary lane paid seventeen 168-byte stubs to learn).

**The hazard this was designed against, and why it is not the obvious one.** A heartbeat that outlives its job
does not merely leak a process — it keeps run.log fresh forever, so the WEDGED clause never fires and the box
bills to the age backstop. **Strictly worse than having no heartbeat.** Three nets, failing differently: the
pipeline's EXIT trap; a **parent-death poll** (SIGKILL runs no trap, and `Killed` is exactly what the
2026-07-27 crash-loop logged — this is the one that matters); a hard TTL.

**The EXIT-trap interaction, reproduced rather than reasoned about** (`unshare -fp --mount-proc`, the same
method that caught `kill -9 1` returning 0): the onstart shell reaches `ct_selfstop` despite the background
child, and the PUT stream is already frozen before the trap could clean up after it. *Runs in the dev sandbox;
GitHub runners disable unprivileged user namespaces, so CI skips it on a functional probe.*

**Shakeout, in the §6 order, $0 — `step1-liveness-shakeout.json`:**

| stage | what it proved |
|---|---|
| smoke | rc 0; run.log + phase.txt in S3; **12 distinct `LastModified` values** observed from outside the container across two 20 s phases that produced **no output at all** (5 s interval). The false-positive question, answered by execution. |
| leg | the real `_vast_onstart` composition, 3 container starts: 2 archived attempts, **both keys parse under `_ATTEMPT_RE`**, `start_ages_min` → `[1.27, 0.64]` min; the crash-loop brake tripped on the **third** start only. |
| verdict | **both directions.** Fresh log (0.05 min) → `WATCHING`, spared. Same box at 16 min → `WEDGED`, **condemned**. A guard that can only spare is a guard that measures nothing. |

**Two defects the shakeout found in itself**, which is the argument for having one. (1) The first run went on
the bare runner and returned **rc=127 with an empty S3 listing** — `_PREAMBLE` hard-codes
`/opt/mamba/envs/rbfe/bin/{python,aws}` under `set -eo pipefail`. It now runs in `triskit23/nr4a3fep`. (2) It
reported that run **green**, because the script wrote its record and exited 0; each stage now declares what it
must have proven and exits non-zero otherwise. (3) Stage 2 originally pasted the brake, the trap and the
pipeline into **one shell** — but `_vast_onstart` ends with `bash -lc '<pipeline>'`, a **child**. In one shell
the pipeline's `trap s1f_stop_heartbeat EXIT` **replaces** `trap ct_selfstop EXIT`, silently deleting the
job-kill; its `selfstop_ran` column reading False is how that surfaced. The child-shell property is now pinned
by its own test.

**Where it acts:** one clause in `mode_collect`'s reap loop, after the cheaper `result in S3` / terminal-state
/ age clauses. Reaction time on a wedge goes from the 15 h age backstop to ~15 min of silence. **GPU idleness
never condemns** — only a measured absence of writes does, because a complex leg is legitimately at 0 % GPU
for its whole stage → parameterise → minimise cold start. The guard's `progress_advanced` reads a
**guard-owned** census (`_idle_prev.json`), never monitor's `_progress_prev.json`, which monitor overwrites
with the current census as its last act — sharing it would have compared every healthy leg against itself and
permanently disarmed the one clause that overrides every condemnation.

**First live pass, MEASURED not predicted** (`collect`, 10:05 AM ET, `step1-fanout-map.json → idle_guard`):
**12 live units observed, 0 condemned.** `log_age_min` is `null` on every row — the units pulled their code
before the heartbeat existed — so the log-silence channel correctly reports *no evidence* rather than *silent
for a long time*. Ten rows returned `WORKING` off the GPU-busy reprieve (85–100 % util; the fleet is genuinely
sampling) and two returned `UNKNOWN` (`gpu_util` 0.0 and `null`) — **left alone, because GPU idleness never
condemns.** `collect` prints a loud warning when *no* live unit has a readable run.log, precisely so
"measuring nothing" cannot pass for "all clear". Units pick the heartbeat up as they restart, at which point
the WEDGED channel arms itself for them.

`s1f-09` no longer appears in the fleet, and `blocked_units` in the map artifact carries its reason and
evidence — so the edge is neither being re-rented nor silently missing.

## 7e. Most of the "dead fleet" was the lane double-booking its own machines (2026-07-27, 3:44 PM ET)

**The reading that was wrong.** Eight of nineteen live hosts sat `cur_state=stopped` with an **empty
`status_msg`** — the documented never-started signature — and the obvious conclusion was that the board had
turned bad. It had not. No committed artifact carried `machine_id`, so "eight bad hosts" and "a few bad
machines rented repeatedly" were indistinguishable; adding that one field to the progress snapshot changed
the diagnosis completely.

**The discriminating observation** (CLAUDE.md §4), grouping the same nineteen hosts by machine:

| placement | started |
|---|---|
| the ONLY `s1f-*` instance this lane held on that machine | **8 of 10** |
| placed on a machine this lane was **already renting** | **0 of 7** |

Zero of seven. A Vast machine rents out a fixed number of GPUs, so a second container on a box whose GPU we
already hold has none to take: it sits `stopped` with an empty `status_msg` — **the same signature as a
genuine create/start race, reached by our own double-booking.** Five of the machines involved (19492, 31035,
31036, 53989, 24573) were at that moment running this lane's own legs at 76–98 % GPU.

**Why it started happening now.** `mode_launch`'s `used_machines` began as a copy of the exclusion set and
grew only from *this process's* submissions. That made a single wave land on distinct hosts and said nothing
about hosts the lane was already renting. Before the ramp that was invisible, because ticks placed one unit
and were hours apart. The ramp places to width every tick, so waves now arrive minutes apart — ten units went
out in two waves four minutes apart — and wave 2 began having forgotten every host wave 1 had just taken,
reading a board that was substantially the same board with the same offers ranked first. The board-read cache
sharpens this rather than causing it: within a wave one snapshot serves every unit, so only
`exclude_machine_ids` separates them.

**Fixed:** `mode_launch` seeds host-distinctness with the machines the lane is already renting. These are
*not* written to the exclusion set — a machine we are happily running on is a good machine, and it becomes
selectable again the moment its instance ends.

### ⚠ The remedies are opposite, so the classifier has four classes, not one

A blanket "never started ⇒ host-scoped exclusion" would have published five healthy, cheap machines to the
**permanent, cross-lane** set (`vast_machine_blacklist` ages nothing out) for a fault that was ours — the
expensive direction of the trade that module's own docstring names. `never_started_cohort` now returns:

| class | evidence | remedy |
|---|---|---|
| `double_booked` | never started; an OLDER instance of ours is on that machine | destroy the duplicate, record **nothing** against the machine |
| `stopped_on_a_proven_machine` | never started; that machine has **run our container before** | destroy, re-price through the market gate, **never** condemn |
| `host_fault` | never started; sole rental, machine never ran our image | destroy **and** publish HOST-scoped |
| `preempted` | non-empty `status_msg` — it ran and exited | resume; excluding its machine retires healthy supply |

**And the verdict must be stable.** Observed within seven minutes: instance 46031788 was correctly
`double_booked` behind our 46031535 on machine 53989; the collect reaped 46031535 for being terminal,
46031788 became the oldest thing we held there, and the *same instance* re-classified as `host_fault` — one
strike from condemning a machine that had just run two of our containers to 94–99 % GPU. A classification
that changes because the other instance was cleaned up is not a classification. `_started_machines.json`
accumulates every machine watched running one of our containers and is written **before** the reap that
destroys the evidence.

### The threshold, and the one that must not move

`STUCK_START_MIN` (45 min) buys exactly one thing — patience for a cheap host legitimately spending 20–40 min
pulling the ~6 GiB image. A duplicate with no GPU to pull onto has no pull to protect, so
`stuck_start_min_for()` derives its floor as `STUCK_START_MIN/3`; the cost of waiting is not the rental but
the **slot**, and these held 8 of the lane's 19. The **two-consecutive-strike** rule is unchanged for every
class: what it guards — an API blip, a listing caught mid-transition — is just as possible here, and this
path destroys a rental. Corroboration that age alone must never condemn: `s1f-00` carried the empty-msg
signature at 34 min and was *running* by 42.

### The exclusion set IS reaching the selector

Checked, because the opposite conclusion would have meant no amount of further excluding could help. The
launcher prints `excluding N machine(s) from offer selection` immediately before each wave, and that list
grew 1 → 11 → 13 → **21** across the day as the cross-lane union filled in. **None** of the never-started
machines (19499, 144071, 53989, 31036, 31035, 19492) was in the list printed for its own wave. Machine 144071
entered the set *after* this lane rented it — another lane reaching the same verdict independently, which is
corroboration of a host fault, **not** evidence of a selector bug. That distinction is now enforced: the
field is `machines_excluded_since`, and the only thing that could support the stronger claim is the
launcher's own `excluding …` line for the wave that placed the host.

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
