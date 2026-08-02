# GCP GPU — hard facts (verified 2026-07-22, read BEFORE any GCP GPU work)

These are empirically verified, expensive-to-relearn facts about THIS GCP project
(`project-a7ebde30-e2ed-4b8d-9a9`). Every one cost real debugging time. Check them
before diagnosing a GPU provisioning/quota problem.

## 1. We have a **1-GPU TOTAL** quota — this is the binding limit

- **`GPUS_ALL_REGIONS = 1`** (project-global quota) is THE binding cap: **at most 1 GPU
  concurrently, across ALL regions and ALL GPU types (spot or on-demand).** Confirmed
  `limit=1.0 usage=1.0` on 2026-07-22.
- The **per-type regional** quotas are REAL but **NON-binding** because the global 1 caps
  below them:
  - `NVIDIA_L4_GPUS` (on-demand L4, us-central1) = **1**
  - `PREEMPTIBLE_NVIDIA_L4_GPUS` (spot L4, us-central1) = **3**  ← looks like 3, but you can
    never use more than 1 because GPUS_ALL_REGIONS=1 wins.
- **Consequence:** NEVER assume you can run >1 GPU job concurrently. Replicate seeds
  (0/1/2), multiple edges, or spot+on-demand together all run **strictly sequentially**.
  "The spot L4 quota is 3 so we can fan out" is **WRONG** — the global cap is 1.
- **How to check:** `gcp-quota-check.yml` prints BOTH the global `GPUS_ALL_REGIONS` and the
  per-type regional rows. Read GPUS_ALL_REGIONS for the real answer.

## 2. Quota ≠ capacity; and the zombie test

- **Quota** = your allowed ceiling. **Capacity** = whether GCE physically has an idle GPU to
  hand you right now. They are independent: quota can be free while capacity is exhausted
  (`ZONE_RESOURCE_POOL_EXHAUSTED`), even for on-demand at peak.
- **Zombie discriminator (definitive):** a zombie VM holding a GPU shows **quota usage ≥ 1**.
  If `NVIDIA_L4_GPUS`/`PREEMPTIBLE_NVIDIA_L4_GPUS` **usage = 0** AND no `gcp-ternary-*` VM is
  listed, there is **no zombie** — a provisioning failure then is real capacity or a bad
  request, NOT a zombie. `mode=tail` and `gcp-reap-vms.yml` both print live VMs + quota usage.

## 3. On-demand (`provisioning=standard`) create REQUIRES `--instance-termination-action`

- GCP requires `--instance-termination-action` (STOP or DELETE) **whenever
  `--max-run-duration` is set** — for BOTH spot AND standard VMs. (The old belief that
  termination-action is "spot-only" is WRONG; standard supports it.)
- Bug fixed 2026-07-22 in `gpu-ternary-fep-gcp.yml`: the standard branch omitted it, so every
  on-demand create **failed request-validation** and the leg had NEVER actually run on-demand.
  Both provisioning branches must carry `--instance-termination-action=DELETE`.

## 1b. WE ALREADY HOLD QUOTA FOR SEVERAL GPU TYPES — the cap is on COUNT, not TYPE

- Measured 2026-07-26 (`gcp-quota-check.yml`, now emitting a `GPU TYPES USABLE TODAY` annotation). us-central1
  metrics with a **non-zero** limit, all at **1.0**:
  `NVIDIA_L4_GPUS`, **`NVIDIA_V100_GPUS`**, **`NVIDIA_P100_GPUS`**, `NVIDIA_T4_GPUS`, `NVIDIA_P4_GPUS`,
  `NVIDIA_K80_GPUS`, `COMMITTED_NVIDIA_L4_GPUS`, plus the `_VWS_` variants.
- **A100 and H100 are absent** (limit 0) and would each need their own request.
- **So "can we get a faster GPU" needed no request at all.** `GPUS_ALL_REGIONS = 1` caps the COUNT; the per-type
  quotas above are what say WHICH card, and several are already granted. This was never asked before because the
  quota check only ever grepped `L4|G2|GPU` and printed the rows mid-log.
- **Why it might matter a lot:** the L4 is bandwidth-poor (GDDR6, ~300 GB/s) and OpenMM PME on a 142k-particle
  system is bandwidth-bound. P100 (HBM2, ~732 GB/s) and V100 (HBM2, ~900 GB/s) are 2.4× and 3.0× on that axis.
  Spec-derived, at approximate list prices, against ~$292 of remaining credit:

  ⛔ **SUPERSEDED 2026-07-31 — every non-L4 row below is WITHDRAWN and must not be cited as current.**
  The measurement that retired them, and what replaced it, is **§1c** below.

  | card | quota | ~×L4 | ~$/h | ~$/leg | legs on $292 | science/$ |
  |---|---|---|---|---|---|---|
  | L4 (current) | 1 | 1.00 | 0.71 | 31 | 9.4 | 1.41 |
  | **P100** ⛔ *superseded* | **1** | ~2.4 | 1.46 | **26** | **11.1** | **1.67** |
  | V100 ⛔ *superseded* | 1 | ~3.0 | 2.48 | 36 | 8.0 | 1.21 |
  | T4 ⛔ *superseded* | 1 | ~1.1 | 0.35 | 14 | 20.3 | 3.05 |

- ⚠ **SPEC-DERIVED, NOT MEASURED, AND THE T4 ROW IS THE LEAST TRUSTWORTHY.** The bandwidth heuristic is validated
  on exactly ONE pair — L4 vs Vast 4090, where it predicted the measured 3.53× to ~5% — and on that pair bandwidth
  and FP32 scale *together* (3.36× and ~2.8×), so it **cannot distinguish bandwidth-bound from compute-bound.**
  T4 vs L4 is precisely the discriminating case: near-identical bandwidth (320 vs 300) but **3.7× different FP32**
  (8.1 vs 30 TFLOPS). If the workload is even partly compute-bound the T4 is much slower than the table implies.
  This repo has already booked one card-ratio error from spec-style reasoning (the 2.06× that compared a warmup
  rate to a production rate), so **none of these rows may be used for planning until measured.**
  **STATUS 2026-07-31: the harness that measures them EXISTS and has run — see §1c. The L4 control is measured;
  the three non-L4 rows are still unmeasured, and still may not be used for planning.**
- **NOT a flag change.** P100/V100/T4 need `n1-*` machine types plus `--accelerator type=...,count=1`; the lane
  currently pins `g2-standard-8/12/16`, which are L4-only. Setup is CPU/RAM-bound and needs ≥8 vCPU / 32 GB, and
  the container's CUDA build has to support the older compute capability. Real work, not a one-line edit.
  **Built 2026-07-31** — `gpu-bench-gcp.yml` + [`gcp_card_bench.py`](../modalities/gcp_card_bench.py).

## 1c. ★★ THE CARD PROBE — what it measures, what it MEASURED, and the size mistake it exists to avoid

**The probe.** `gpu-bench-gcp.yml card=<l4|t4|p100|v100>` derives machine type and `--accelerator` together from
one input (`gcp_card_bench.CARDS`), so an `n1-*` with no accelerator — which boots CPU-only and reports a
perfectly plausible ns/day — is unrepresentable rather than merely discouraged; `OPENMM_REQUIRE_CUDA=1` makes a
CPU fallback raise instead of measure, and the reported CUDA `DeviceName` is checked against the card that was
asked for (`card_from_device`), so a measurement can never be filed under the wrong card.

**⚠ THE SIZE IS THE PART THAT DECIDES WHETHER THE ANSWER IS WORTH ANYTHING.** `gpu_md_bench.py` defaults to
`BENCH_EDGE_NM=7.1` ≈ 36k atoms, and `gpu-bench-gcp.yml` never passed the variable — so **every GCP bench ever
run in this project measured a box four times smaller than the lane's real system**, and would have answered a
different question with an equally confident number. The edge is now DERIVED from the repo's one exact anchor
(`vast_bench_sweep`: 9.5 nm ↔ 84,534 particles) rather than from a typed water density:
**11.29 nm → a measured 141,867 particles, 0.07 % from the ternary lane's real 141,968.**

Both sizes run in one boot, because the boot dominates the cost and the second measurement is ~2 min:
the **ternary size first** (a VM that dies early still yields the decision-relevant number), then **9.5 nm**,
which is the protocol of `vast_cost_model.MEASURED_NS_PER_DAY_84K` and is what makes a GCP card commensurable
with every Vast card. Protocol otherwise identical to the Vast anchors: TIP3P/PME, 1.0 nm cutoff, HBonds, HMR,
4 fs, CUDA mixed precision, 3 independent timed blocks ≈ 60 s, CV-gated, physics-checked.

**MEASURED — L4, the control arm.** One home: [`gcp-card-bench.json`](../modalities/gcp-card-bench.json),
written by CI from the probe's own result lines and never hand-edited. Regenerate this table with
`python3 research/modalities/gcp_card_bench.py --markdown-table`;
`tests/test_gcp_card_bench.py::test_the_documented_table_is_the_measured_table` re-checks it against the
artifact on every CI run, so the document cannot drift from the measurement.

<!-- GCP-CARD-BENCH-TABLE:BEGIN -->
| card | machine | ns/day @141,887p | ×L4 | ns/day @84,534p | $/h | $/ns @141,887p | ns per $ | ×L4 ns/$ |
|---|---|---|---|---|---|---|---|---|
| **L4** | `g2-standard-4` | **177.28** | **1.00×** | 298.96 | 0.708 | 0.0958 | **10.43** | **1.00×** |

**⚠ REFUSED BY THE ADMISSION GATE — a RANKING, not a rate.** These are not in the table above and must never be quoted as throughput. They are shown because `admit()`-refused is not the same claim as uninformative: where the implied ratio dwarfs the reason for refusal, the ordering it gives is still safe.

| card | ns/day @141,887p (PROVISIONAL) | implied ×L4 | refused because |
|---|---|---|---|
| T4 (`Tesla_T4`, spot) | 55.63 | **~0.31×** | cv=0.0561 exceeds 5% — block-to-block scatter, not a steady-state rate |
<!-- GCP-CARD-BENCH-TABLE:END -->

### ★★ THE RESULT: THE WORKLOAD IS COMPUTE-BOUND, SO THE BANDWIDTH ARGUMENT IN §1b DOES NOT HOLD

The T4 is the discriminating card **by construction**, because its two specs point opposite ways:

| hypothesis | the spec ratio it rests on | predicted T4 ÷ L4 | measured |
|---|---|---|---|
| bandwidth-bound (§1b's premise) | 320 vs 300 GB/s | **1.07×** | — |
| compute (FP32)-bound | 8.1 vs 30.3 TFLOPS | **0.27×** | — |
| **what the probe found** | — | — | **~0.31×** (0.314 at 141,867 p, 0.345 at 84,534 p) |

**0.31× is the FP32 prediction, not the bandwidth one.** So the heuristic that generated §1b's P100 and V100 rows
rests on a premise this measurement rejects, and those rows are unsupported — *not* independently refuted, since
neither card has a throughput number yet. On the decision axis the T4 delivers **~0.41×** the L4's
science-per-dollar where §1b promised **2.2×** — wrong by ~5×, and in the direction that would have bought the
worst card available.

⚠ **AND A PRICE ERROR IN §1b THAT NEEDED NO MEASUREMENT AT ALL.** Its `$/h` column compares the L4's
**whole-VM** rate (0.71 = a `g2-standard-4`, which *bundles* the L4) against **bare GPU** rates for the others
(1.46 / 2.48 / 0.35). A P100 cannot run without a host. Adding the `n1-standard-4` it needs (**$0.190/h** =
4 × $0.031611 + 15 × $0.004237), with §1b's own speed assumptions untouched, already takes P100 from **+18 % to
+3 %** and T4 from **2.16× to 1.44×**. Two independent errors, both flattering the alternatives.

**PRACTICAL ANSWER: STAY ON THE L4.** Of the four cards this project holds quota for, the L4 has by far the most
FP32 per dollar, and FP32 is what the measurement says this workload spends its time on.

### ⚠ P100: IT BOOTS AND HOLDS QUOTA, BUT OPENMM WILL NOT RUN ON IT — a BLOCKER, not a slow number

Run `30634431184` (spot, us-central1-c, 9:26–9:48 AM ET 2026-07-31), the first P100 ever provisioned in this
project. The VM created, booted and was confirmed RUNNING mid-probe. **Every attempt then failed**:
`status=ERROR attempts=3 err=OpenMMException:…` at **both** system sizes — i.e. all three rungs of
`gpu_md_bench`'s minimise ladder (200 → 2000 → 20000) raised, twice over. That is what the ~21-minute step was
doing: six failed system builds, not slow MD.

This is precisely the risk §1b flagged and nobody had tested — *"the container's CUDA build has to support the
older compute capability"*. P100 is **sm_60** (Pascal); the L4 is sm_89 and the T4 sm_75, and both ran fine on
the identical conda-forge OpenMM. **So the P100's blocker is the environment, not its speed**, and it cannot be
priced at all until that is resolved.

⚠ **THE EXACT EXCEPTION WAS LOST TO A PARSER BUG, NOW FIXED.** `gpu_md_bench.py` emits `k=v` pairs that the
launcher parses with `line.split()`, so any value containing a space is truncated at the first one — the file
already documented this for `device` (`'Quadro RTX 8000'` → `'Quadro'`) and then emitted the ONE field
guaranteed to contain spaces, `err=`, without the same treatment. The message therefore arrived as
`OpenMMException:Error`, naming the exception type and discarding the sentence that says why. Fixed
2026-07-31 (spaces underscored, message capped at 300 chars); **the next P100 attempt will report the real
cause**, and until it does the mechanism above is the hypothesis the evidence supports, not a confirmed
diagnosis.

⚠ **`$/h` IS A PUBLISHED LIST RATE, NOT AN INVOICE** (`gcp_card_bench.LIST_PRICE_USD_PER_H`). GCP exposes no
per-run cost without a BigQuery billing export, and the Cloud Billing Catalog probe built into the workflow
**returned nothing on 2026-07-31**, so every `$/ns` and `ns per $` here inherits that label.

**Two things the L4 arm settled that are worth more than one row:**

1. **REPRODUCIBLE TO 0.1 % ACROSS INDEPENDENT VMs.** Runs `30632062766` and `30632627483` (8:56 and 9:04 AM ET,
   separate VMs, both us-central1-b) returned **177.08 / 177.28** ns/day at the ternary size and
   **298.76 / 298.96** at the anchor size. That matters because the Vast table's whole 2026-07-27 re-anchoring
   was about single-host draws from an unmeasured distribution (spreads of 4–14 % across marketplace hosts).
   A dedicated GCE VM is **not** that: N = 1 here is worth far more than N = 1 there.
2. **THE COST IS LINEAR IN PARTICLE COUNT AT THIS SCALE.** 177.28 / 298.96 = **0.593** against **0.596** for
   pure O(N). So nothing about the smaller box was overhead- or occupancy-limited, and extrapolating between
   these two sizes is safe. ⚠ It does **not** discriminate bandwidth-bound from compute-bound — both scale
   linearly in N — which is exactly why the T4 arm is still the load-bearing measurement.

**⚠ AND A CROSS-CHECK THAT DISAGREES WITH A LIVE REPO FIGURE — stated, not resolved.** At the *identical*
84,534-particle protocol, `vast_cost_model.MEASURED_NS_PER_DAY_84K["RTX4090"]` = 804.06 ns/day against this
L4's 298.96, i.e. **4090/L4 = 2.69×**. The repo's live figure is **3.53×** (pricing.md), measured a different
way: production *ternary legs*, 2 fs, 12 HREX windows, in the `nr4a3fep` image's `rbfe` environment. Three
confounds separate them and none is negligible — the Vast entry is a median over 6 marketplace hosts while this
is one dedicated VM; a water box is not an alchemical hybrid topology with HREX exchange and per-iteration I/O;
and `vast_cost_model` itself records that the environment moved throughput non-uniformly across cards
(4080 unchanged, 4090 +6 %, 3090 +28 %). **So 3.53× is NOT retracted** — this is a same-protocol datum that
sits beside it, and the honest reading is that the L4→4090 ratio is somewhere in 2.7–3.5× depending on which
quantity you mean. Anyone quoting a single number should say which.

## 1e. ★★ THE FIRST STEP-1 FAN-OUT LEG EVER TIMED ON AN L4 — and why it is NOT the §1c number

§1c measures a **card**: a plain TIP3P water box, one simulation, no alchemy. This measures a **leg of the
actual science**: a 12-window HREX RBFE complex leg of `e_zaienne_cmpd19__cw_ms_free_acid` r1, the
`nr4a3fep` container, on a `g2-standard-8` L4, on GCP trial credit. Until 2026-08-01 no fan-out leg had ever
been timed on an L4 at all — `gcp_fanout_rep.MAX_RUN_S_RUN`'s own comment calls its 48 h cap an ESTIMATE for
exactly that reason — so **this is what makes an L4 fan-out leg priceable in hours instead of guessed.**

One home: [`gcp-s1f-rep-rate.json`](../modalities/gcp-s1f-rep-rate.json), written by CI from the unit's own
`COMMITTED.json` markers and never hand-edited. It stores the **raw marker series**, so every figure below
is a quotient that can be recomputed if `RATE_WINDOW` or the arithmetic changes.

**⛔ DO NOT HAND-EDIT THE FENCED BLOCK BELOW, AND DO NOT REGENERATE IT AS A SEPARATE CHORE.** It is written
by `gcp_fanout_rep.sync_rate_table_doc`, called from `write_rate_artifact` — **the same call that writes the
JSON** — and re-applied by the lane's publish step (`rate --sync-doc`) after its `reset --hard`, so the
measurement and the paragraph quoting it land in one commit and cannot be authored by different events.
`tests/test_gcp_fanout_rep.py::test_the_documented_table_is_the_measured_table` byte-compares the two on
every CI run. *(2026-08-01: it was previously a manual `rate --markdown-table` step, and CI went red
**3 min 41 s** after the last hand regeneration — the leg committed `production 80`, the rate window moved
out of warmup, and the measurement legitimately changed. See `RATE_ARTIFACT`'s comment for the incident.)*

**⚠ A CHANGED CELL HERE IS A MOVING MEASUREMENT, NOT A RETRACTION.** This leg is still running and every
tick republishes its trailing-window rate, so cells move by design and **no appendix entry or
`pinned-figures.json` registration is owed for a tick**. The durable record is the artifact's raw `marks`
series, from which any earlier reading is re-derivable. Registration is owed only if a figure from here is
ever quoted as a *settled* result somewhere else — which is exactly what the "no dollars, deliberately"
refusal below exists to stop.

<!-- GCP-S1F-REP-RATE-TABLE:BEGIN -->
| leg | commits | last committed | s / HREX iteration *(phase measured in)* | leg wall-clock h | ns/day per replica | ns/day aggregate (12 windows) |
|---|---|---|---|---|---|---|
| **complex** | 70 | production 2000 | **36.00** *(production)* | 24.0 | 6.00 | 72.00 |
| **solvent** | 34 | production 560 | **1.09** *(production)* | 0.7 | 198.17 | 2377.98 |

*2.50 ps of MD per replica per iteration, derived from the run's own `warmup_target=400 prod_target=2000` line and `nr4a3_rbfe.py`'s protocol lengths (1.0 ns equilibration / 5.0 ns production).*
<!-- GCP-S1F-REP-RATE-TABLE:END -->

**⚠ IT IS A REALIZED WALL-CLOCK RATE, NOT A BARE MD THROUGHPUT.** Each interval brackets 20 HREX iterations
**and** the GCS commit barrier that closes them (`[barrier] commit warmup@400 persisted 541.5 MiB in 4.5s`).
That is the right quantity for an ETA and for GPU-hours-per-leg — those are what the lane actually spends —
and the wrong one to put beside a single-simulation benchmark without saying so.

**⚠ THE RATE SETTLES; THE FIRST INTERVALS DO NOT.** The opening interval ran at **18.1 s/iter** and the last
ten sit within 1.7 % of each other. A rate quoted off one interval would have promised a landing roughly
twice too early, which is why `gcp_fanout_rep.MIN_RATE_INTERVALS` is a number in the code and the ETA cell
refuses below it and **renders above it**.

### How it compares to §1c's L4 — a DIFFERENT QUANTITY, and it supersedes nothing

| | §1c card probe | this leg |
|---|---|---|
| system | TIP3P water box, **141,887** particles | alchemical hybrid NR4A3+ligand, **112,953** atoms (`[clash-diag:initial]`) |
| sampling | one simulation | **12** HREX replicas + the full 12×12 energy matrix each iteration |
| I/O | none | trajectory + a ~540 MiB checkpoint committed to GCS every 20 iterations |
| ns/day | **177.28** | see the aggregate column above |

§1c established that cost is **linear in particle count** at this scale (0.593 measured vs 0.596 for pure
O(N)), so the water box scaled to this leg's 112,953 atoms would be ≈ **222.7 ns/day**. The measured
aggregate is roughly **a third** of that, and the gap is the HREX energy matrix, the softcore hybrid
topology, and the commit barrier — i.e. **the protocol overhead is about 3×**, which is a fact neither
measurement could give on its own. **Neither number supersedes the other; quoting one for the other is the
error this section exists to prevent.**

**⚠ NO DOLLARS, DELIBERATELY.** This ran on GCP trial credit — a SEPARATE LEDGER, never summed into realized
or ladder spend (CLAUDE.md §6), expiring 2026-10-10 — and the L4 list rate is **not** a go-forward cost basis
([pricing.md](./pricing.md)). The artifact records hours and iterations and no `$`.

### The one planning consequence, and the measurement that would settle it

The complex leg alone is the wall-clock figure in the table; the **unit** is that leg **plus** the solvent
leg, and the solvent leg has no measured L4 rate yet. `gcp_fanout_rep.MAX_RUN_S_RUN` is 48 h, fixed at CREATE
and **unraisable on a running instance** (§3b). So whether one VM can span a whole unit turns entirely on the
solvent number — which is why `unit_progress` refuses to project the unit off the complex rate and scopes its
ETA to the leg that has one. **If it does not span, the cost is a boundary, not sampling**: the commit store
is continuous and the leg is per-leg idempotent, so a resumed unit re-enters at its last committed generation
and the loss is detection latency. The solvent leg's first three commit intervals close this question, and
the artifact will carry them the moment they exist.

## 1f. ⚠ THE WARMUP→PRODUCTION TRANSITION KILLED AN L4 LEG — localised, NOT yet mechanised (2026-08-01)

Recorded here because it is a measured property of an L4 run in this project and the next occurrence must not
start the diagnosis over. `e_zaienne_cmpd19__cw_ms_free_acid` r1, VM `gcp-s1frep-30674349470`
(us-central1-a, on-demand, created 8:00 PM ET 2026-07-31):

```
INFO:   Iteration 400/400
INFO:   Iteration took 38.535s.
[timing] 20 iters in 700s = 35.0s/iter (1.71 iters/min) at iteration 400/400
[barrier] commit warmup@400 persisted 541.5 MiB in 4.5s
[barrier] committed checkpoint at iteration 400/400
[spot-driver] PRODUCTION created from warmup; run -> 2000
Traceback (most recent call last):
  ... multistatesampler._compute_energies -> energy_context_cache.get_context
  ... states.create_context -> openmm.Context(system, integrator, platform)
openmm.OpenMMException: No compatible CUDA device is available
```

**WHAT IS ESTABLISHED.** The warmup phase **completed** (400/400, committed and durable) and the exception
came **16 s later, at the first CUDA context creation of the production phase**. It is not a device that
vanished from the host: the same process had done 3 h 53 m of successful CUDA work, its last iteration taking
38.5 s, and it wrote a 541 MiB checkpoint seconds before. The boot-time probe had passed explicitly
(`[probe] CUDA CONTEXT OK device= NVIDIA L4`), so the `BOOTSTRAP-FAIL cuda-not-in-leg-container` guard added
earlier that evening was working and this is a **different** failure from the one it closes.

**WHAT IS NOT ESTABLISHED — and this section will not guess it.** Whether the cause is a driver/ECC/Xid event,
a context or memory limit reached when the production phase builds a second set of contexts over a
112,953-atom hybrid system × 12 replicas, or something else. Nothing in the leg's own log discriminates them,
and the only readings that would — `nvidia-smi -q`, the kernel ring buffer — live on the **host**, which the
reaper correctly destroyed 96 s later.

**WHAT WILL SETTLE IT, already armed.** `s1f_rep_gcp_startup.sh` now captures a post-mortem (`nvidia-smi -q`,
`dmesg | grep -iE 'xid|nvrm|nvidia|out of memory'`, memory, container exit codes) to
`<unit>/postmortem_<leg>.txt` on **any** leg failure, before the VM is reaped. And the resume is the
controlled reproduction: it restores warmup@400 and re-enters **the same transition within minutes**, so
"transient" and "systematic" separate on the next attempt at a cost of minutes rather than hours.
`gcp_fanout_rep.MAX_NOPROGRESS_LAUNCHES` bounds it at three.

## 1d. Capacity and permissions, measured 2026-07-31 (both cost a run to learn)

- **`gcloud compute project-info describe` returns rc=2 for `gpu-runner@`** — so **`GPUS_ALL_REGIONS` is not
  readable from a workflow using that service account**, even though `gcp-quota-check.yml` prints the *regional*
  rows fine. This is why the card probe's first pre-flight failed with no refusal message: the gate aborted on
  the reader, not on the condition. **A GPU-freeness check must therefore rest on `gcloud compute instances
  list` (quota can only be held by an instance — §2) plus the per-type regional row, both of which work.**
- **`ZONE_RESOURCE_POOL_EXHAUSTED` for `n1-standard-4` + `nvidia-tesla-t4` in ALL FOUR us-central1 zones**
  (a/b/c/f), on-demand, at 9:13 AM ET (run `30633564753`). Verbatim, per zone:
  `ERROR: (gcloud.compute.instances.create) Could not fetch resource: code: ZONE_RESOURCE_POOL_EXHAUSTED`.
  That is the §4 discriminator doing its job: a malformed request returns `Invalid`/`required`, not this — so
  this is **genuine capacity**, and the T4 arm is blocked by supply rather than by the harness. Corroborated
  the same morning by an **e2-micro** create failing `ZONE_RESOURCE_POOL_EXHAUSTED` in us-central1-c
  (`gcp-quota-check` run `30631015578`, 8:33 AM ET), i.e. the pressure is not GPU-specific.
  ⚠ **Consequence for planning: a granted per-type quota is NOT capacity.** §1b's "we already hold quota for
  several GPU types" remains true and remains the reason no quota request is worth filing — but holding
  `NVIDIA_T4_GPUS = 1` bought nothing on this particular morning. Re-try later; there is no other region to
  move to (§5).

## 3b. `max-run-duration` CANNOT be changed on a RUNNING instance — the boundary is fixed

- Measured 2026-07-26 on a **decoy** e2-micro (`gcp-quota-check.yml`), never on a live leg. Create at
  `--max-run-duration=7200s`, then `gcloud compute instances set-scheduling --max-run-duration=259200s`:

  ```
  ERROR: (gcloud.compute.instances.set-scheduling) Could not fetch resource:
   - Max run duration cannot be changed while the instance is running.
  ```

  rc=1, duration unchanged at 7200, instance still RUNNING (so the attempt is at least harmless).
- **Consequence, and it is a planning constraint not a bug:** a VM's cap is fixed at CREATE time. When a leg is
  going to outlive its cap you cannot buy more time later — you get a boundary, the leg resumes from its last
  committed checkpoint on a fresh VM, and the cost is the **detection latency**, not the extension.
- **So set the cap correctly at create.** `144000s` (40 h) is validated as acceptable at create time. A full
  ternary leg is ~2800 iterations at ~56.5 s/iter ≈ **44 h of MD**, so 40 h does NOT span a fresh leg and one
  boundary is structural. Validate a larger create-time value before assuming it is allowed.
- **What IS recoverable is the latency.** Recovery runs off the watchdog cron, which GitHub delivers at ~2–4 h
  intervals for this repo regardless of the expression. Dispatching `ternary-leg-watchdog.yml` by hand the moment
  the VM disappears turns 2–4 h of dead wall clock into minutes — which matters on GCP specifically, where the
  credits are free and expiring so **wall clock is the scarce resource, not money**.
- A `mode=extend` was built for this and then **removed**, because the operation can never succeed on a running
  instance. Kept here as the fact rather than as dead code that invites a retry.

## 4. "L4 stocked out" in a launcher log is NOT proof of capacity exhaustion

- The provision loop historically labeled ANY non-quota create failure as "stocked out",
  which masked a **malformed-request** bug as a capacity problem (see #3). The workflow now
  **echoes the real gcloud error** on each failed create (`ERROR/exhausted/Invalid/
  required/termination/...`). Read that line before concluding "capacity."
- Sanity check on any provisioning stall: **spot working but on-demand failing is backwards**
  (on-demand is normally EASIER to get than spot). That pattern means a broken command, not
  capacity.

## 5. us-central1 ONLY for L4/G2

- This project has L4/G2 quota **only in us-central1**. Diversify across zones a/b/c/f for
  spot-capacity resilience; never add other regions (they have no quota → wasted attempts).

## 6. ★★ VMs do NOT self-delete — the delete is REFUSED. Only the CONTROL PLANE can reap a GCP VM

⚠ **CORRECTED 2026-07-27, 2:04 PM ET.** This section previously asserted that the default compute SA had been
granted `compute.instances.delete` on 2026-07-22 "so VMs now self-delete on graceful exit → a finished/dead leg
shows `live_vms=0` (no zombie left)". **That is false, and it was never measured.** The superseded claim is
retained here because it is what the lane planned around for five days.

**THE MEASUREMENT.** `gcp-ternary-30215419909` (us-central1-a, g2-standard-16, on-demand), the valB_mini
`calib_hi_to_lo__ternary_vhl` dir=rev seed=0 leg. It finished its science normally — `[barrier] committed
checkpoint at iteration 2000/2000`, then `[tfep] LEG DONE calib_hi_to_lo__ternary_vhl: ΔG_morph=-47.79 ± 0.09
(MBAR SE)` at ~**12:03 PM ET on 2026-07-27** — and the startup script ran to its end and fired its EXIT trap.
Serial console, verbatim (kernel uptime seconds in brackets), read via `gpu-rbfe-gcp-tail.yml` run
`30291739779` at **2:00 PM ET**:

```
[76535.256985] startup-script: === TFEP-DONE TFEP_RESULT status=OK run leg=calib_hi_to_lo__ternary_vhl dg_morph=-47.795 se=0.086 ===
[76535.257198] startup-script: result in GCS; EXIT trap will delete the VM (avoid idle billing)
[76535.274394] startup-script: === SELF-DELETE (trap on EXIT): deleting gcp-ternary-30215419909 in us-central1-a ===
[76536.643544] startup-script: ERROR: (gcloud.compute.instances.delete) Could not fetch resource:
[76536.643690] startup-script:  - Required 'compute.instances.delete' permission for 'projects/project-a7ebde30-e2ed-4b8d-9a9/zones/us-central1-a/instances/gcp-ternary-30215419909'
[76536.838903] startup-script: self-delete no-op (already gone / no perm)
[76536.839063] startup-script exit status 0
[76536.839118] Finished running startup scripts.
```

Three independent corroborations from the same run, so this is not one ambiguous log line:

- **`testIamPermissions` as the VM's own identity** (non-destructive) returned **403**:
  `Required 'compute.instances.list' permission for 'projects/project-a7ebde30-e2ed-4b8d-9a9'` — the SA cannot
  even *ask* what it may do.
- **It is not a scope problem.** The VM reports SA `878095411563-compute@developer.gserviceaccount.com` with
  scopes `https://www.googleapis.com/auth/cloud-platform`, and `gcloud` is on PATH at `/snap/bin/gcloud`. The
  same script's `gcloud storage cp` calls all succeeded. Storage yes, compute no.
- **It is not a crashed or hung script.** `google-startup-scripts.service` = `inactive`, `Result=success`,
  `ExecMainStatus=0`; no leg process alive. The script exited cleanly *after* the delete was refused.

**WHY IT WAS INVISIBLE.** `gcloud` prints `ERROR:` in capitals, and every progress filter in this repo greps
case-sensitively for `error|Error` — so the one line naming the cause matched nothing and never reached a
readout. The trap's own fallback string, `self-delete no-op (already gone / no perm)`, then covered two
opposite outcomes and named neither. Fixed: `gpu-rbfe-gcp-tail.yml` now carries a TEARDOWN FORENSIC block
(case-insensitive trap grep, the raw serial window around the failed delete, the `testIamPermissions` probe),
and its own delete branch keeps stderr instead of `2>/dev/null`.

**THE RULE.** This is the GCP instance of a rule the repo already paid to learn on Vast (CLAUDE.md §6, *"THE
HOST CANNOT STOP ITS OWN BILLING — ONLY THE CONTROL PLANE CAN"*). The mechanism differs — on Vast an
unprivileged container cannot end its own machine; here the API call is simply refused — but the consequence
and the remedy are identical: **never plan a GCP leg's teardown around the in-VM EXIT trap.** Treat
`_self_delete` as best-effort only.

**WHAT ACTUALLY REAPS A FINISHED LEG NOW:** the ternary watchdog's DONE branch
(`research/modalities/watchdog_run.sh`), acting from CI where the key lives. It is safe without any age
heuristic because its condition is that the leg's own direction-keyed result JSON is already in GCS, so there
is no sampling left to lose. Pinned by `tests/test_watchdog_done_reaps_vm.sh`, which extracts the branch and
drives it against a stubbed `gcloud`.

**COST OF THE GAP:** the GPU sat idle and held from ~12:03 PM to 2:04 PM ET. On GCP the loss is not dollars —
it is `GPUS_ALL_REGIONS = 1` (#1), so for those ~2 h *every* GCP GPU job on the account was blocked, against
credit that expires 2026-10-10.

## 6b. The backstops behind it, and which of them are real

- **`--max-run-duration` + `--instance-termination-action=DELETE`** — real, but sized for the science, not
  against this failure: spot `25200s` (7 h), on-demand `259200s` (72 h). It cannot be raised on a running
  instance (§3b). ⚠ Every operator-facing message in `gpu-ternary-fep-gcp.yml` used to say "7h max-run
  backstop" regardless of branch, so on 2026-07-26 the launcher told the operator this 72 h VM would
  self-destruct within 7 h. Fixed: `MAXRUN` is published to `$GITHUB_ENV` and every message interpolates it;
  `tests/test_gcp_create_flags.py` extracts the create command and the emitted messages from the YAML and
  fails if a cap is hardcoded again, or if a branch sets `--max-run-duration` without
  `--instance-termination-action` (§3).
- **`gcp-reap-vms.yml` is NOT a backstop — it is a manual tool.** ⚠ **It has no `schedule:` trigger at all.**
  Measured 2026-07-27: **all 33 of its runs to date are `workflow_dispatch`, zero are `schedule`.** It did not
  fail to catch this zombie; it has no way to fire. And it must stay manual: its only automatic criterion is
  age, and a healthy ternary leg legitimately runs ~44 h, so age cannot tell a working leg from a wedged one
  (its own file records a dry_run that would have killed a mid-production leg at age 860 min). Progress, not
  age, is the safe discriminator — which is why the automatic reap lives in the watchdog.
- **A `schedule:` cron is not a safety mechanism here.** `ternary-leg-watchdog.yml` requests `*/15`; the gaps
  actually delivered across this incident were **125, 148, 177, 217 and 222 min** (measured 2026-07-27 from
  the run list). Anything whose safety depends on cadence is not a backstop — see CLAUDE.md §6.
- **The watchdog fired and still missed it, which is the real lesson.** Scheduled run `30287320911` at
  **1:00 PM ET 2026-07-27** — 57 min after the leg finished, with the VM still RUNNING — emitted a green
  `::notice title=WATCHDOG DONE -> CONVERGE`. It saw the leg was done, dispatched the analysis, and never
  looked at the VM list: the reap existed only in the CRASHED branch, which a DONE leg can never reach. A
  guard can be scheduled, running, and green while the thing it exists to prevent is happening.

## 6c. ★★ WHAT REAPS A VM NOW — and why the launcher refuses to buy one it cannot switch off (2026-07-31)

§6 established that a GCP VM cannot delete itself and §6b that `gcp-reap-vms.yml` is not a backstop. Neither said
what the *remaining* single point of failure was, and it was this: **the watchdog's DONE branch is inside a loop
over the ENABLED entries of `ternary-watch.json`.** `gcp_watch_reap` auto-disables a unit the moment it reaches
its terminal state, so **"no enabled entry" is the lane's RESTING state** — both entries are disabled today. In
that state `watchdog_run.sh` printed `WATCHDOG ORPHAN VM, NOTHING WATCHING IT` and *deliberately* refused to
delete. A leg launched into it would have run to its create-time cap, `--max-run-duration=259200s` = **72 h
≈ $51** of the ~$292 of expiring credit, holding `GPUS_ALL_REGIONS = 1` (#1) — i.e. every GCP GPU job on the
account — with a red workflow as the only signal.

**The gap was latent, not active, when it was found** (`gcp-quota-check` run 30626214303, 7:13 AM ET
2026-07-31: `GPUS_ALL_REGIONS` limit 1.0 **usage 0.0**, nothing held). Four layers now close it, ordered by
where they act. **Nothing weakens the refusal above — it is BOUNDED**, and the reason it existed still stands:
a VM name is `gcp-ternary-<GITHUB_RUN_ID>`, so an unidentified orphan could only be killed on AGE, and age
inverts (a healthy leg legitimately runs ~44 h; `gcp-reap-vms.yml` records a dry_run that would have destroyed
a mid-production leg at age 860 min).

1. **NO WATCHER, NO GPU.** [`gcp_launch_guard.py`](../modalities/gcp_launch_guard.py), called from the detached
   branch of `gpu-ternary-fep-gcp.yml` **before `provision` is called**, refuses to provision a `mode=run` leg
   unless an `enabled: true` entry reproducing it exists. **The watch entry is the teardown mechanism, not
   bookkeeping.** It validates **`origin/main`'s** copy, because `ternary-leg-watchdog.yml` checks out with no
   `ref` and will only ever read main's — a branch-local entry is not a watcher (CLAUDE.md §7).
2. **The VM says what it is.** The create now stamps GCE labels `tfep-leg / -dir / -seed / -rst / -mode`, so
   `orphan_sweep()` in `watchdog_run.sh` can resolve a forgotten VM's **own** restraint-keyed result key and
   apply the DONE branch's test unchanged: delete only when that object is already in GCS **and** the VM
   predates it. Unlabelled, non-`run`, no result, unreadable timestamp, or a result older than the VM — all
   still refused loudly, none reaped, **age never consulted**. It runs on every pass, cold ones included.
3. **A non-`run` mode is not a leg** and no longer inherits the 72 h cap (it writes no leg result, so neither
   reap path can retire it and the cap is its only bound). The leg cap is unchanged.
4. **The idempotent skip moved off the VM.** A redundant dispatch used to buy an L4, skip after ~37 s and sit
   idle — the one shape BOTH reapers deliberately spare, so that a real `force_rerun` is never destroyed. Not
   making the purchase is the only fix that does not weaken a reaper.

Pinned by `tests/test_watchdog_orphan_sweep.sh` (drives the extracted sweep against a stubbed `gcloud`; every
refusal path asserts **zero** deletes), `tests/test_gcp_launch_guard.py`, and four new checks in
`tests/test_gcp_create_flags.py`.

## Quick command reference (all via GitHub Actions, WIF auth)

- **Quota (global + regional):** dispatch `gcp-quota-check.yml`.
- **List VMs + reap strays:** `gcp-reap-vms.yml` (`mode=dry_run` to list, `mode=reap` to kill;
  `prefix=gcp-ternary-`, `max_age_min=20` protects a just-launched leg).
- **Live leg state (VMs, quota, preemption ops, run log):** `gpu-ternary-fep-gcp.yml mode=tail`.
- **On-demand (non-preemptible) run:** `gpu-ternary-fep-gcp.yml mode=run provisioning=standard`
  (+ `force_rerun=1` to bypass the idempotent-skip, else it exits without resuming).
