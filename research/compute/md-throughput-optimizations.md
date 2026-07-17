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
- **Memory-bandwidth is the ceiling** (MD is bandwidth-bound, not FLOP-bound): L4 = 300 GB/s, A10G = 600,
  L40S ≈ 864, RTX 4090 = 1008. The L4 is the **slowest** of our candidates.

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

## TIER 1 — GPU sharing (NVIDIA MPS): the big untapped lever

**Are we using MPS? NO.** And our workload is close to the textbook case for it.

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

### The gate (now instrumented — free)
Both sub-levers are sized by **one number: single-sim GPU utilization on the L4.** Guessing it violates repo
rule #1, so as of 2026-07-16 every GCP leg runs a **background `[gpu-util]` logger** (`gpu-rbfe-gcp.yml`
startup: `nvidia-smi --query-gpu=utilization.gpu,utilization.memory,memory.used,power.draw` every 30 s → serial;
surfaced by `gpu-rbfe-gcp-tail.yml`). The **next real leg** will report it. Reading:
- util persistently **< ~60%** on the complex leg → real headroom → **build 1A** (MPS launcher; pack 2–3
  edges/legs/GPU), validate on one packed leg (~$5–15), then apply to the matrix.
- solvent leg (~5k atoms) will show the **most** idle SMs → strong MPS case there regardless.
- util near **~90%+** → the complex leg already saturates → 1A gain is small for complex (still worth it for
  solvent + ABFE); skip 1B.

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
string — composes directly with `cheap-gpu-plan.md` (provider is a config, not a rewrite) and MPS Tier 1
(a faster card with headroom packs *more* MPS processes).

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

## Priority-ordered action list

1. **[free, in flight]** `[gpu-util]` logger merged → **read single-sim L4 utilization off the next leg.** Gates Tier 1 & 2.
2. **[free eng + 1 cheap leg]** If headroom: build the **MPS multi-process launcher (Tier 1A)** — pack K
   independent edges/legs/ABFE-windows per GPU. Biggest effort:value item; slashes matrix GPU-hours.
3. **[~zero code + 1 cheap leg]** Add `ns/day` readout → **benchmark $/ns on L4 vs A10G (± 4090)** → pick the
   **matrix** GPU by measured $/ns (Tier 2).
4. **[held]** Intra-HREX MPI+MPS (Tier 1B) — only if 1A's utilization shows large single-sim headroom.
5. **[reviewed no-ops]** online-analysis interval, cutoff/PME, precision — leave as-is (documented above).

**Spend discipline:** items 2–3 each need one **< $50** validation leg (autonomy threshold = just-do-it, but
name the provider first per the standing rule). The matrix GPU choice + any MPS rollout to the matrix is where
real $ lands → present at its gate with the measured $/ns + utilization in hand. Everything else here is free
engineering or a documented no-op.
