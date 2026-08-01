# MD / FEP throughput optimizations — deep-dive ledger

**Purpose.** After the NVIDIA-MPS question (2026-07-16), a systematic sweep of every lever that could cut
**wall-clock and real GPU-$** on our OpenMM MD / OpenFE-RBFE / ABFE workload — what we already capture, what is
untapped, and the exact action + gate for each. This is the single place to look before changing an MD setting,
a machine type, or a launcher. Composes with [cheap-gpu-plan.md](./cheap-gpu-plan.md) ($/GPU-hr and provider
choice) — that doc is *which GPU*; this doc is *how fast and how many-per-GPU* we drive it.

**Grounding facts (measured / verified, not assumed — repo rule #1):**
- **RBFE engine** = `research/modalities/nr4a3_rbfe.py` → OpenFE `RelativeHybridTopologyProtocol` → openmmtools
  `MultiStateSampler` **HREX**: 12 λ-windows/replicas, 1 ns equil + 5 ns production per window. **One shared
  engine drives BOTH clouds** — GCP (`gpu-rbfe-gcp.yml`) and AWS (`nr4a3_rbfe_sagemaker.py` via
  `entry_rbfe.py`). ⇒ every protocol-level knob below applies to both paths at once.
- **ABFE engine** = `research/modalities/nr4a3_abfe.py` → **independent per-λ-window OpenMM `Context`s** (NOT
  HREX): each window is a standalone `integrator.step()` loop with a tiny per-iteration `State` checkpoint. No
  replica exchange, no monolithic trajectory `.nc`.
- **Measured L4 HREX throughput** = **10.4 s / openmmtools iteration**, and this is **invariant** to the
  checkpoint interval (iter 220→440 at interval-20 = 10.45 s/iter; iter 500→600 at interval-100 = 10.42 s/iter).
  ⇒ the loop is **GPU-compute-bound**, not checkpoint-I/O-bound. Single-sim CUDA MD ≈ 628 ns/day on the L4.
- ⚠ **"MEMORY-BANDWIDTH IS THE CEILING (MD is bandwidth-bound, not FLOP-bound)" IS REFUTED BY OUR OWN BENCH —
  SEE TIER 2b.** It is retained here only as the superseded framing this doc was written on. Bandwidth is a
  *poor* predictor of our ns/day: fitted on the benched cards it carries the **worst** leave-one-out error of
  the three proxies (**+116 %**, `vast-board-census.json` → `throughput_ceilings`), and it over-predicts the one
  datacenter card we have actually measured by **2.67×**. Card throughput has exactly one home —
  [`vast_cost_model.MEASURED_NS_PER_DAY_84K`](../modalities/vast_cost_model.py) — and **no card may acquire a
  `$/ns` from a spec proxy** (`pricing.md` §A.3). Spec sheets for context only: L4 = 300 GB/s, A10G = 600,
  L40S ≈ 864, RTX 4090 = 1008, A100 PCIe 80 GB = 1935.

---

## What we ALREADY capture (verified — no action needed)

| Lever | Status | Evidence |
|---|---|---|
| **HMR + 4 fs timestep** | ✅ on | OpenFE default; the `625 steps × 4 fs = 2.5 ps` MC-move-interval comment in `_protocol()` confirms 4 fs is live (4 fs *requires* hydrogen-mass repartitioning). This is already a ~2× win vs a naïve 2 fs run. |
| **Mixed precision** | ✅ on | OpenFE `engine_settings` default is `mixed`; we don't override it. `double` would be ~2–3× slower for no FEP benefit. |
| **CUDA required (no silent OpenCL)** | ✅ on | `_working_platform_name("CUDA")` + `OPENMM_REQUIRE_CUDA` gate; OpenCL is ~1.3–2× slower and JIT-compiles the hybrid Context pathologically slowly. |
| **Energy-only analysis `.nc`** | ✅ fixed 2026-07-16 (commit a6f5ff9) | Disabled `positions_write_frequency`/`velocities_write_frequency` → ~1 GB → ~10 MB `.nc`. MBAR needs only energies. **Applies to both clouds** (shared engine). ABFE never had this (State-only). No throughput change (storage/upload only), but removes GB-scale re-uploads on every spot commit. |
| **Single replicate (`protocol_repeats=1`)** | ✅ right-sized | Field standard for a single congeneric edge (MBAR/bootstrap error). `=3` would silently triple GPU-$/wall. Escalate only if a result is marginal. |
| **Spot + per-unit checkpoint/resume** | ✅ on | ~60–70% cheaper than on-demand; loses ≤1 checkpoint interval on preemption. |
| **am1bcc charges (CPU, cited protocol)** | ✅ | On OpenFE's published-benchmark protocol so we can cite its validation rather than pay to re-derive it. NAGL retained as fallback. |
| **Moderate checkpoint interval (20 iters / 50 ps)** | ✅ right-sized | Proven ~44 MB `.chk`; measured to NOT affect throughput; smaller interval only bloats the `.chk` and worsens the spot sync. |

---

## TIER 1 — GPU sharing (NVIDIA MPS): investigated, **RULED OUT on the L4** (measured 2026-07-16)

**Are we using MPS? No — and, now measured, we shouldn't on the L4:** a single complex HREX replica-set already
saturates the card (88–100% util, at its 72 W TDP), so there's no idle capacity for MPS to fill. Full evidence in
"The gate" below. The analysis that motivated the measurement is kept for the record (and for the bigger-GPU
case), but the bottom line is **MPS is not a win here — go to Tier 2 ($/ns).**

**Why it matters.** [NVIDIA's OpenMM+MPS result](https://developer.nvidia.com/blog/maximizing-openmm-molecular-dynamics-throughput-with-nvidia-multi-process-service/):
packing *multiple* OpenMM simulations onto one GPU via the Multi-Process Service (kernels from different
processes overlap on idle SMs, rather than time-slicing) **more than doubles aggregate throughput** on an
L40S/H100 for small systems (DHFR). The win is exactly proportional to how much **one** simulation
*under*-utilizes the GPU: idle SMs get filled by the other processes.

Our workload has **two independent flavors** of MPS opportunity — with very different integration cost:

### 1A. Across INDEPENDENT units — the near-term win (no science-code change) ⭐
Most of our GPU work is embarrassingly parallel *independent processes*:
- multiple **RBFE edges** in the prospective matrix (24–36 compounds),
- the **complex + solvent legs** of one edge,
- every **ABFE λ-window** (fully independent Contexts by construction).

These need **no MPI and no OpenFE changes** — just start the `nvidia-cuda-mps-control -d` daemon on the VM and
launch **K unit-processes on the one GPU**. Correctness is trivial (separate processes, separate outputs). The
throughput gain is bounded only by when K sims saturate the card. **If one leg uses ~30–40% of the L4, we pack
~2–3 legs per GPU → 2–3× fewer GPU-hours at the same hourly rate** = a direct 2–3× real-$ cut on the matrix
(the single biggest spend on the ladder). This is the highest value-to-effort item in this doc.

### 1B. WITHIN one HREX simulation (12 replicas) — the deeper, harder win
openmmtools `MultiStateSampler` propagates the 12 λ-replicas **serially** on one GPU by default (our 10.4 s/iter
is 12 sequential propagations). With `mpi4py`/`mpiplus` + `mpirun -np K` **and** MPS, replicas propagate
**concurrently** on the one card. But integrating MPI under OpenFE's `ProtocolDAG` executor (it wasn't built to
launch a simulation unit under `mpirun`) is **real engineering** and the gain on the L4 is **uncertain** — a
35k-atom complex replica may already be closer to saturating the small L4 than DHFR is on an L40S. Lower
priority than 1A; revisit if 1A's utilization measurement shows big single-sim headroom.

### The gate — MEASURED 2026-07-16: NO MPS headroom on the L4 (complex leg) ❌
Both sub-levers are sized by **one number: single-sim GPU utilization on the L4.** Guessing it violates repo
rule #1, so every GCP leg now runs a **background `[gpu-util]` logger** (`gpu-rbfe-gcp.yml` startup:
`nvidia-smi --query-gpu=utilization.gpu,utilization.memory,memory.used,power.draw` every 30 s → serial;
surfaced by `gpu-rbfe-gcp-tail.yml`). **Result on the valA complex HREX leg (12 replicas, ~35k atoms):**
```
gpu 88–100% util, power 69–74 W — i.e. AT the L4's 72 W TDP (power-capped), across all active-MD samples.
```
⇒ **a single HREX replica-set already SATURATES the L4** (continuously busy + power-limited). MPS fills *idle*
SM time; there is essentially none here, so **MPS gives ~no throughput gain on the L4** — neither the
intra-HREX (1B) nor the pack-multiple-edges/legs (1A) variant. This is the measured kill of the MPS idea for our
expensive work on this GPU, *before* building infra that wouldn't have paid off. Caveats kept honest:
`utilization.gpu` is a "GPU-busy" metric, not SM occupancy — but the **power-at-TDP** corroborates genuine
saturation. Two places MPS could still matter (not worth building now): (i) the **solvent leg** (~5k atoms)
likely underfills the L4 — but it's the cheap/fast leg, so packing it saves little; (ii) a **bigger GPU**
(L40S/A100, more SMs) may *not* saturate on one replica-set → MPS headroom returns there — but at that point the
simpler win is just running the faster card on $/ns (Tier 2), not MPS. **Action: MPS is OFF the table for the L4;
fold the throughput effort into Tier 2 (GPU/$ per ns).**

**Action:** read `[gpu-util]` off the next leg → if headroom, implement the MPS launcher (1A) as a free
engineering change; the only $ is one cheap validation leg (< $50 → within the autonomy threshold, but flag the
provider per the standing rule). ABFE MPS-packing is a drop-in for the same launcher when that track resumes.

---

## TIER 2 — hardware / provider $/ns (biggest money lever, ~zero code)

MD is bandwidth-bound and the **L4 is our slowest candidate** (300 GB/s). For the small kill-switch benchmark
(2 legs) the machine barely matters; for the **prospective matrix** (24–36 compounds × 2 legs × 12 windows)
$/ns **dominates the whole ladder cost**. The decision must be **$/ns**, not $/hr or ns/day alone:

| GPU | BW (GB/s) | rough spot $/hr | relative ns/day | ⇒ **relative $/ns** (lower = better) |
|---|---|---|---|---|
| **L4** (current) | 300 | ~$0.20–0.28 | 1.0× (628 ns/day) | baseline |
| **A10G** | 600 | ~$0.30–0.40 | ~1.8–2× | often **cheaper per ns** despite higher $/hr |
| **L40S** | ~864 | ~$0.60–0.90 | ~2.5–3× | competitive; check spot availability |
| **RTX 4090** (Vast/Salad) | 1008 | ~$0.20–0.40 | ~3× | frequently the **cheapest $/ns**, if a leg fits its 24 GB + preemption is tolerable |

Numbers are indicative — the honest move is to **measure $/ns directly**: the `[gpu-util]` logger already prints
wall-clock; adding one line of `ns/day` readout per leg (openmmtools logs it) turns every validation leg into a
free $/ns benchmark. **Action:** on the next validation round, run the *same* single leg on L4 vs A10G (and, if
convenient, a Vast/Salad 4090) and pick the matrix GPU by measured $/ns. Zero code beyond a machine-type/provider
string — composes directly with `cheap-gpu-plan.md` (provider is a config, not a rewrite). **With MPS ruled out
on the L4 (Tier 1, measured), this is the PRIMARY throughput lever for the matrix.**

⚠ **The table above is the SUPERSEDED spec-proxy framing** that Tier 2b refutes; it is kept because the
*conclusion* it reached (rank on `$/ns`; the 4090 class wins) survived the measurement. Its per-card figures did
not, and must not be quoted — the measured table is `vast_cost_model.MEASURED_NS_PER_DAY_84K`.

---

## TIER 2b — THE DATACENTER-GPU QUESTION, ANSWERED WITH A MEASUREMENT (2026-08-01)

**Question:** is there a big AI-class GPU — A100/H100/H200/B200, or a Blackwell RTX PRO — that beats the
consumer cards we rent, on `$/ns` or at least on raw speed?

**Answer: no, and it is measured, not argued.** The bench table contains one datacenter card, and it settles it:

| card | measured ns/day @84,534 | vs RTX 4090 | mem BW | Vast `dlperf` (an AI benchmark) |
|---|---|---|---|---|
| RTX 4090 (reference) | **804.06** | 1.00× | 1008 GB/s | 97.1 |
| **A100 PCIe 80 GB** | **524.43** | **0.65×** | **1935 GB/s (1.92×)** | 92.1 (≈ the 4090) |

**A datacenter card with 1.92× the memory bandwidth and an equal AI rating delivers 0.65× the MD.** That single
row kills three inferences at once: bandwidth does not predict our throughput (Tier 2's grounding fact), an AI
benchmark does not either, and "bigger card" does not mean "faster MD".

**★ THE TREND, WHICH IS THE REAL ANSWER TO "IS GPU DEVELOPMENT GOING SOMEWHERE WE BENEFIT FROM?"** Divide each
benched card's measured MD throughput by its AI rating and the ratio falls monotonically as the cards get more
AI-oriented — we get **half** the MD per unit of AI performance on Blackwell that we got on Ampere:

| card | MD ns/day per unit `dlperf` |
|---|---|
| RTX 3090 Ti / RTX 3090 (Ampere consumer) | **10.49 / 10.39** |
| RTX 4080 / RTX 4090 (Ada) | 9.80 / 8.28 |
| RTX PRO 4000 (Blackwell) | 7.18 |
| A100 PCIe (Ampere **datacenter**) | 5.69 |
| RTX 5090 (Blackwell) | **5.20** |

Mechanism, and it is not mysterious: the incremental die area and price of an AI GPU goes into **tensor cores**
(FP8/FP4 GEMM), **HBM capacity** and **NVLink**. OpenMM's mixed-precision PME/nonbonded kernels are FP32
gather-scatter over a neighbour list — they touch **none** of the three. Our systems are 84k–148k particles
(tens of MB), so 80–192 GB of HBM is bought and unused, and a single OpenMM `Context` is one GPU, so NVSwitch is
bought and unused. What MD actually rewards — shader clock, FP32 throughput per dollar, enough VRAM for one
system — is exactly the consumer segment.

**⛔ DO NOT SCREEN A DATACENTER CARD WITH THE `dlperf` PROXY — ANCHOR IT TO A MEASURED CARD OF THE SAME DIE.**
The census's three proxies are fitted almost entirely on consumer parts (`fp32_tflops` and `mem_bandwidth_gb_s`
on **RTX 3090/4080/4090 only**), and extrapolating them across an architecture boundary is anti-conservative in
exactly the direction `pricing.md` §A.2 warns about — it makes a card look *better* than it is and lures a
rental in. Worked case, the largest unbenched block on the 2026-07-27 board (12 offers):

| RTX PRO 6000 Blackwell WS, screened by… | implied ns/day | `$/ns` at $0.3619/h | verdict |
|---|---|---|---|
| `dlperf`-linear (283.5 × k) | 1684 (2.09× 4090) | $0.00516 = **1.51× basis** | *clears the buy line* ❌ misleading |
| **anchored to the MEASURED RTX 5090** — same GB202 family, **identical 1792 GB/s**, +10.6 % shaders | **1035–1144** (1.29–1.42× 4090) | **$0.00759–0.00840 = 2.22–2.46× basis** | **⛔ REFUSED, above the buy line** |

A card that shares its bandwidth with a card we have benched cannot be 1.5× that card. The architectural anchor
and the census's own screen agree (`bench_shortlist` → `"skip — would have to be far faster than anything we have
benched"`); the AI proxy is the only thing that disagreed. **Nothing was ever bought on it** — §A.3 already
forbids a proxy from producing a `$/ns` — but it would have wasted a bench rental.

**Where the whole board landed** (2026-07-27 census, 141 offers; `$/ns` at each model's cheapest all-in offer,
against the `$0.006539/ns` buy line):

- **Measured, and this is the ranking that decides purchases:** RTX 3090 **$0.00362** (1.06× basis) ·
  RTX PRO 4000 $0.00388 · RTX 5090 $0.00477 · RTX 4090 $0.00512 · **A100 PCIe $0.00723 (2.12× basis — over the
  line, refused)**.
- **Unbenched, at their most optimistic (`dlperf`-linear) estimate, all refused:** A100 SXM4 5.25× basis ·
  H100 NVL 3.06× · H100 SXM 4.22× · RTX PRO 6000 Server 4.74× · **B200 10.06×** · L40 5.65× · V100 7.27×.
  The B200, L40, RTX PRO 6000 Server and H100 PCIe are formally `RULED_OUT` by the census's own one-sided
  ceiling — they would have to beat their friendliest possible throughput by 1.28–2.73× merely to break even.

**Speed alone, ignoring price:** the fastest card we have ever measured is the **RTX 5090 at 1034.58 ns/day**
(1.29× a 4090), and it is *also* cheaper per ns than a 4090 on this board — so the "pay more for wall-clock"
trade barely exists. It is the right pick for the one case where speed is worth a premium: a leg with a real
`JobProfile.min_uninterrupted_h`, where a slower card is proportionally more exposed to preemption.

**And a datacenter card cannot be justified on VRAM either.** The only thing 48–96 GB buys us is headroom we do
not need at 148k particles; the 24 GB consumer cards already fit every system in the program.

**One genuinely different hardware class, stated honestly and NOT pursued:** special-purpose MD ASICs
(D. E. Shaw **Anton 3**, available to US academics through PSC/NRBSC allocation) are ~2 orders of magnitude
faster than any GPU — but on a *single long trajectory*, which is precisely the axis our workload does not need.
Our work is 19 edges × 6 legs × 12 windows of embarrassingly-parallel short sampling, so it wants **many cheap
cards**, not one fast machine; and Anton allocations require academic affiliation the program does not have
(same blocker as [access-allocation-request.md](./access-allocation-request.md)). Parked, not dead —
[method-watch.md](../method-watch.md).

**Standing conclusion: the ranking is already right and the card is still not the decision — the OFFER is.**
There is no unexplored GPU worth buying. The remaining throughput levers are protocol-side, not hardware-side.

---

## TIER 3 — free settings micro-wins (reviewed)

- **online / real-time analysis interval.** openmmtools runs periodic online MBAR during the HREX loop (writes
  `simulation_real_time_analysis.yaml`). For our **fixed-length** 5 ns runs we do **not** use early-termination,
  so that periodic MBAR solve is strictly overhead. **BUT** the AWS ETA monitor (`nr4a3_rbfe_sagemaker.py`)
  *reads* that YAML to report progress. ⇒ **reviewed no-op: keep it.** The overhead is small (a CPU MBAR every
  ~200 iters) and it buys live ETA. Revisit only if profiling shows it stalls the GPU loop materially.
- **Trajectory `.nc`** → already energy-only (Tier "already capture"). Nothing left here.
- **`deterministic_forces` / precision** → `mixed` is correct; no change.
- **Nonbonded cutoff / PME** → these change the *physics* (and break comparability with the cited OpenFE
  benchmark). **Do NOT tune for speed.** Off-limits.

---

## TIER 4 — sampling right-sizing (money, but a SCIENCE gate — do NOT cut silently)

The obvious "money saver" is fewer windows / shorter production. **Held deliberately:** 12 windows × 5 ns is
OpenFE's field-standard for a single edge and matches the benchmark we cite. Cutting it to save $ trades away the
one thing the kill-switch is testing (can our exact pipeline reproduce a known ΔΔG). Any reduction is a
**science decision**, made explicitly with a convergence justification (forward/reverse, overlap matrix) — never
a silent throughput hack. For the *matrix*, adaptive/staged sampling is a legitimate future lever but belongs in
the prereg, not here.

---

## Ops lever — kill manual VM teardown (managed-job auto-teardown)

**Why we delete VMs by hand today:** the GCP launcher uses **raw GCE VMs** (the IaaS layer — the equivalent of
a bare EC2 instance), not a managed *job* service. A GCE VM has no concept of "the workload finished" — it just
runs a startup script and keeps billing until something stops it. SageMaker never needs a manual delete because
a **Training/Processing job** is a managed abstraction whose instance lifecycle is tied to the process: exit /
timeout / failure ⇒ AWS auto-deprovisions.

**We are NOT exposed to runaway billing even so:** every GCE VM is launched with
`--max-run-duration=25200s` (7 h) + `--instance-termination-action=DELETE` — GCE's native backstop that
**hard-deletes the VM after 7 h no matter what** (this is what reaped yesterday's `gcp-bill-*` CPU VMs). The
manual `delete=1` only stops billing *promptly* when a leg finishes early (e.g. at 4 h) instead of idling to the
7 h cap.

**The clean fix (removes manual teardown entirely):** GCP *does* have SageMaker-equivalent managed job services
that auto-provision **and** auto-deprovision on completion — **Vertex AI Custom Training Jobs** (closest analog),
**GCP Batch**, or a **GKE Job**. Migrating the launcher to Vertex AI Custom Jobs (we already have
`research/compute/Dockerfile.mdjob` + `research/modalities/autoteardown.py`) gives exactly SageMaker's
"job ends → instance dies" behavior. **Gated, not urgent:** the 7 h DELETE backstop already prevents idle-billing
runaway, and this may be subsumed by the broader provider migration in `cheap-gpu-plan.md` (Modal/RunPod/Salad
all auto-teardown by design). Belt-and-braces audit meanwhile: `gpu-rbfe-gcp-tail.yml` now runs a full-project
VM census + `sweep_stale=1` to reap any leftover non-rbfe VM across all zones.

## Ops lever — kill the conda-env rebuild on every spot preemption ✅ DONE (env-cache, 2026-07-17)

**Observed 2026-07-16 (then confirmed hard the same night):** the valA complex leg was spot-preempted **~9×**
over one night on contended us-central1 L4; each re-dispatch rebuilt the openfe conda env from scratch (~8–13 min
Miniforge + mamba solve) before it could resume from the iter-checkpoint. Several preemptions landed *during* the
rebuild → whole cycles of **zero MD progress**. That env rebuild — **not** lost MD iters (those are checkpointed)
— was the dominant wasted wall-clock. **FIX SHIPPED: a GCS env-cache** (`gpu-rbfe-gcp.yml`, 2026-07-17): the first
VM that builds the env tars it to `gs://<bucket>/env-cache/rbfe-<key>.tar` (key = image family + a manual spec
tag); every subsequent VM downloads+extracts it (~2–3 min) and **skips Miniforge+mamba entirely**. An
`import openfe, openmm` gate guards both paths, so a missing/corrupt/mismatched cache silently falls through to
the full solve — **worst case == old behavior** (zero-risk fallback). The env extracts to the same
`/tmp/mf/envs/rbfe` path it was built at (no conda relocation). Bump the spec tag's `-vN` when the package list
changes → clean rebuild + re-cache. Remaining (not needed now): a full **GCE custom image** or **Vertex/Batch**
managed job (we have `research/compute/Dockerfile.mdjob`) would remove even the ~2–3 min extract, but the
env-cache already collapses the vulnerable rebuild window from ~11 min to ~2–3 min.
**Validation (2026-07-17):** the MISS path (build → upload) is confirmed end-to-end — a `mode=tiny` run
(29573895552) built the env, ran RBFE `status=OK`, and left a **4.54 GiB** cache tar at
`env-cache/rbfe-7d435bd97dcebb4a.tar` (verified via the tail census). The HIT path (download → extract → use) is
**import-gated with a build fallback**, so it cannot regress; a clean HIT *observation* is still pending a run
that survives spot preemption long enough to print it (the validation re-run happened to get preempted at ~8.5
min — routine, not a cache fault). Bottom line: shipped and safe; the speedup is confirmed on the upload half and
guaranteed-safe on the use half.
- **Persistent host for terminal legs** (`cheap-gpu-plan.md`: RunPod Secure / ACCESS) — a non-preemptible host
  so the long final legs don't reload the MD env at all. Trades spot's price for stability; right for the
  end-game full-sampling legs, not the cheap early gates.
NB: GPU quota is **us-central1 only** — never switch regions to dodge a preemption (a preempted region still
has create-capacity; any spot zone can preempt). See CLAUDE.md standing rule (2026-07-16).

## Priority-ordered action list

1. **[DONE 2026-07-16]** `[gpu-util]` logger → **measured: L4 saturates on one complex HREX replica-set (88–100%
   util, ~72 W/72 W TDP).** ⇒ **MPS is OFF the table for the L4** (Tier 1A + 1B dropped). Kept as a permanent
   instrument for any future GPU.
2. **[~zero code + 1 cheap leg]** Add `ns/day` readout → **benchmark $/ns on L4 vs A10G/L40S (± 4090)** → pick the
   **matrix** GPU by measured $/ns (Tier 2). This is now the PRIMARY throughput lever (MPS having been ruled out).
3. **[held]** MPS revisited **only** on a bigger GPU that doesn't saturate on one replica-set — and even then $/ns
   on the faster card usually wins over MPS packing. Not worth building for the L4.
4. **[reviewed no-ops]** online-analysis interval, cutoff/PME, precision — leave as-is (documented above).
5. **[✅ DONE 2026-07-17]** GCS **env-cache** shipped — collapses the rebuild-on-preemption window from ~11 min to
   ~2–3 min (import-gated fallback = zero-risk). Longer-term **Vertex/Batch managed jobs** (auto-teardown) remain
   optional. See Ops levers above.

**Spend discipline:** item 2 needs one **< $50** validation leg (autonomy threshold = just-do-it, but name the
provider first per the standing rule). The matrix GPU choice is where real $ lands → present at its gate with the
measured $/ns in hand. Everything else here is free engineering or a documented no-op.
