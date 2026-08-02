# GPU / compute PRICING — single source of truth (every number links to a justifying test)

> **This file is authoritative for "what does step X cost, and how do we know."** nr4a3-program-map.md's economics block
> summarizes it; this file carries the evidence. **Rule: a MEASURED number (with a linked run/artifact) always
> beats an ESTIMATE.** Never quote a cost without a `status` and a `source`. The canonical RBFE map
> (`research/modalities/congeneric-rbfe-map.json`) still holds `est_gpu_h: null` and "forbids trusting stub
> GPU-hour numbers" — honor that: an extrapolation is not a measurement.

**Status legend:** `MEASURED` (a completed run on the target hardware) · `MEASURING` (a run is in flight this
session; will be updated on completion) · `ESTIMATED` (derived/extrapolated — flagged, not certified).

---

## A. Live per-card price on Vast (MEASURED)

**★ GO-FORWARD LANE (trimcrae, 2026-07-24): ALL production runs are on Vast.** GCP L4 / SageMaker / Modal are
**NOT** the cost basis going forward. **Never quote the L4-on-demand figure as a go-forward cost.**

> **L4 THROUGHPUT, WHEN YOU NEED IT FOR HOURS RATHER THAN DOLLARS.** That refusal is about *money*; a leg still
> takes the wall clock it takes, and the free-credit lane has to be sized in hours. Two measured L4 numbers
> exist and they answer different questions — a card benchmark and a real step-1 fan-out leg, differing by the
> HREX/alchemy/commit-barrier overhead between them. Both live in
> [gcp-gpu-facts.md](./gcp-gpu-facts.md) §1c and §1e, derived from
> [`gcp-card-bench.json`](../modalities/gcp-card-bench.json) and
> [`gcp-s1f-rep-rate.json`](../modalities/gcp-s1f-rep-rate.json). No figure is restated here (rule 1), and
> **neither one becomes a cost basis by being measured** — GCP trial credit is a SEPARATE LEDGER (CLAUDE.md §6).

**⚠ THE "RTX 4090 DEFAULT, 3090 FALLBACK" RULE IS RETIRED (2026-07-25).** It rested on a **withdrawn** bench
(the 2026-07-24 23:08 grid — single 0.9–4.5 s windows, which also ranked a 4080 SUPER above a 4090 and a
mislabelled Quadro RTX 8000 as cheapest per ns) and on the assumption that the two cards cost about the same per
hour. Neither survives:

- **Measured throughput @84,534 particles.** Table of record: `vast_cost_model.MEASURED_NS_PER_DAY_84K`,
  re-anchored 2026-07-27 onto a **median over N≥3 independent hosts** — see Appendix T below. Current:
  **4090 = 804.06**, **4080 = 693.35**, **3090 = 460.91** ns/day, so **4090/3090 = 1.745×** and the 4080 is
  ~**14 %** behind a 4090. *(Superseded, retained for the record: the single-host figures **4090 = 755.36**,
  **4080 = 703.51**, **3090 = 359.36**, from which the retired **2.10×** ratio and the retired claim that the
  4080 is within **7 %** of a 4090 were derived. Appendix T says what retired them.)*
- **Prices are nowhere near equal.** Live board 2026-07-25 (445 interruptible offers; 148 pass our launch
  filters): cheapest 3090 floor **$0.0147/hr** against **$0.1310/hr** for the cheapest 4090 — **8.8×**, which
  more than covers being slower (the ratio itself is superseded — see Appendix T).

> **The card is not the decision — the OFFER is.** Rank on all-in `$/ns` and take whatever wins; the top 10
> offers routinely contain both cards. Hard-coding a card is how you pay 2.6× to run on the "faster" one.

**Live board, all-in `$/ns`** (`$/ns = (bid + storage) ÷ (ns_per_day ÷ 24)`) — regenerate with
`python research/modalities/vast_cost_model.py`:

| | $/ns | **per reference (4090) GPU-hour** |
|---|---|---|
| best offer | 0.00181 | **$0.057** |
| **best-10 mean — THE PLANNING NUMBER** | 0.00436 | **$0.137** |
| median offer | 0.00983 | $0.309 |
| *what `step1_fanout` actually paid* | — | *$0.35–0.39* |

Best-to-median spread is **5.43×**, so selection is the dominant lever — worth several times the bid policy
(the whole `×1.9 → floor` bid change is 1.48×). Bid policy, evidence and the retired rules:
**[bid-strategy.md](./bid-strategy.md)**.

**Storage is a real line, not a rounding error.** It bills continuously whether the box is running or paused
(Vast docs), median **$0.20/GB/month** → ~$0.011/hr at the 40 GB the launcher requests. On the *best* offer that
is **42 % of all-in cost**; asking for 20 GB instead cuts all-in cost **21 %**.

**Honest limits:** the validated grid covers **one system size** (84,534 particles) — card *ratios* are far more
size-stable than absolute rates, so ranking is sound, but an absolute ns/day at 146k or 466k is **not** measured.
A 3090 also needs **1.745× the wall clock**, so a leg with a hard continuity requirement is proportionally more
exposed on it (`JobProfile.min_uninterrupted_h` scales that per card and flags it). *(The **2.10×** this line
carried is superseded — Appendix T.)*

### ⚠ A.1 — `$/ns` RANKING CANNOT SEE A WORKLOAD WHOSE THROUGHPUT DEPENDS ON THE HOST CPU (2026-07-26)

Four LANE-13 metadynamics legs, each reporting its own ns/day in `run.log`, alongside the Vast board's
`gpu_util` at the same moment:

| instance | card | `gpu_util` | realised ns/day | $/hr |
|---|---|---|---|---|
| 45854620 | RTX 4090 | 75 % | **141** | 0.193 |
| 45853652 | RTX 4090 | ~74 % | **146** | 0.153 |
| 45878836 | RTX 4080S | 44 % | **~77** | 0.130 |
| 45896793 | RTX 4080S | 33 % | **~47** | 0.207 |

**ns/day tracks `gpu_util`, not the card.** Per utilisation-point the four legs give 1.88 / 2.06 / 1.75 / 1.42
ns/day-per-%, i.e. roughly one constant, whereas the benched card ratio *(as it stood then: 4080 within
**7 %** of a 4090 — that figure is superseded, Appendix T)*
would predict the two 4080S rows to land near the 4090 rows and they land **1.8–3.0× below**. So this is not the
card ratio failing to transfer to a PLUMED workload — it is **hosts handing the job a fraction of their GPU**.

**Why the ranking cannot see it:** `$/ns` is `(bid + storage) ÷ (ns_per_day ÷ 24)` where `ns_per_day` is a
**card constant** from `MEASURED_NS_PER_DAY_84K`. A starved host therefore scores as if it were healthy, and can
win selection while being **both slower and dearer** — 45896793 is 3× slower than the 4090 it replaced *and*
costs more per hour. This is the same blind spot as a host that never starts (infinite realised $/ns, invisible
to the ranking, which is why `ResourceSpec.exclude_machine_ids` exists): **realised throughput is not fed back
into selection.**

**★ ESTABLISHED 2026-07-26 7:15 AM ET — IT IS PLUMED ON A WEAK HOST CPU, AND THE HOST IS NOT THE VARIABLE THE
TABLE ABOVE MAKES IT LOOK.** The discriminating observation arrived free, when NR4A2 crossed the
**metad → release** boundary **on the same instance, the same card, minutes apart**:

| instance | card | phase | `gpu_util` | realised |
|---|---|---|---|---|
| 45896793 | RTX 4080S | metadynamics | **24–33 %** | ~47 ns/day |
| 45896793 | RTX 4080S | **release (plain MD, no bias)** | **74 %** | **~8.7 ns/h ≈ 209 ns/day** |

A co-tenant does not vanish exactly at a phase boundary, and a throttled card does not un-throttle for the next
phase. What changes at that boundary is **PLUMED's CPU-side bias computation**, which metadynamics needs every
step and release does not. So the low utilisation is a **CPU-bound metadynamics bias on a weak host**, and the
GPU on the very same box runs at 74 % once the bias is gone — faster, in fact, than the 4090 hosts' *metad*
rate. That also explains why the 4090 hosts held 71–75 % *during* metad: they were paired with CPUs that could
keep up.

**Superseded by that, and stated so it is not re-quoted:** "hosts handing the job a fraction of their GPU",
and the operational rule that followed it (exclude any machine showing low `gpu_util`). Excluding on
utilisation alone would have discarded a host that is **perfectly good for every non-metadynamics leg**.

**What survives, and is the point of this section:** `$/ns` is `(bid + storage) ÷ (ns_per_day ÷ 24)` with
`ns_per_day` a **card constant** from `MEASURED_NS_PER_DAY_84K`, so it cannot represent a workload whose
throughput depends on the **host CPU** — 45896793 scored as healthy and won selection while being 3× slower
*and* dearer per hour than the 4090 it replaced. Same blind spot as a host that never starts (infinite realised
$/ns, invisible to the ranking, which is why `ResourceSpec.exclude_machine_ids` exists): **realised throughput
is not fed back into selection.** The correct rule is therefore narrower than the one withdrawn above —
**for CPU-coupled workloads (PLUMED metadynamics, and anything else with per-step host-side work) the card
constant is not a throughput model, and host CPU has to enter selection.** For plain-MD legs the existing
ranking is fine.

### ⚠ A.2 — THE TABLE HOLDS **THREE** CARDS, AND VARIANT SKUs USED TO BORROW THEIR NUMBER BY ACCIDENT (2026-07-27)

`card_of` matched an offer's `gpu_name` by **unanchored substring**, so any name containing a benched key
inherited that card's throughput. Three live cases, and the direction was **not** consistent:

| marketplace name | inherited | direction | effect on `$/ns` |
|---|---|---|---|
| `RTX 3090 Ti` | RTX 3090 | strict spec **superset** (10752 vs 10496 cores, 1008 vs 936 GB/s) | overstated → we **under-buy**. Safe |
| `RTX 4080 SUPER` | RTX 4080 | strict spec **superset** (10240 vs 9728 cores, 736.3 vs 716.8 GB/s) | overstated → safe, and load-bearing: a 4080S was the cheapest gradeable offer on this board |
| `RTX 4090D` | RTX 4090 | **cut-down** China SKU (14592 vs 16384 cores) | **understated → lures a rental in. Unsafe** |

**Rule now in force:** matching is **suffix-anchored** (a vendor prefix is free, a trailing qualifier is fatal)
plus an explicit `vast_cost_model.CONSERVATIVE_ALIASES` allow-list admitting **only strict spec supersets**, for
which the borrowed figure is a **lower bound** and the resulting `$/ns` an **upper bound** — the estimate can
only ever make a card look worse than it is. `throughput_provenance()` labels an alias as **derived**, and both
aliased variants are on the bench shortlist so this is a bridge, not a resting place. Everything else resolves
to `None` and is excluded from ranking. **The three measured figures and `REFERENCE_NS_PER_H` are unchanged**
(pinned by `tests/test_vast_board_census.py`). A second copy of the matcher lived in
`gpu_backend.measured_ns_per_day` and now defers.

**Why a labelled one-sided bound rather than refusing the aliases outright:** refusing drops the 8:29 AM ET
board from 11 priceable to 9 and deletes the single cheapest gradeable offer, exactly when a per-unit gate
needs cheap gradeable supply to place units against.

### A.3 — WHY MOST OF A QUALIFYING BOARD IS UNPRICEABLE, AND WHICH CARDS CAN BE RULED OUT FOR $0

The 2026-07-27 8:00 AM ET fan-out snapshot read **48 qualifying → 10 priceable against 19 needed**: every
dropped offer cleared the hard filters and fell at the `$/ns` step for want of a benched `ns/h`. Regenerate the
breakdown with `python research/modalities/vast_board_census.py` (read-only, `$0`; CI route
`vast-price-sample.yml mode=census`) → [`vast-board-census.json`](../modalities/vast-board-census.json).

The census answers **rule-out** and **rule-in** separately, because they need opposite bounds:

- **Rule OUT** needs an **upper** bound on `ns/h`, and costs `$0`. Three predictors (manufacturer FP32,
  manufacturer memory bandwidth, Vast's `dlperf`) are each fitted proportionally on the benched cards, inflated
  by their own **worst leave-one-out under-prediction**, and the **maximum** is taken — the friendliest reading
  three disagreeing heuristics can defend — then a further ×1.25 margin is required before anything is called
  dead.
- **Rule IN** needs a **lower** bound, which no spec sheet supplies. That is the only thing a bench buys.

**The derived-throughput route is refuted, not merely distrusted** (`--proxy-audit`, leave-one-out over the
benched cards, n=3 so each fit is on two): worst error **FP32 +41%**, **bandwidth +116%**, **`dlperf` +28%** —
against a board whose gradeable offers span ~4× in `$/ns`, so any of these can invert a ranking. **No card may
acquire a `$/ns` from them.** They appear only inside the one-sided rule-out ceiling.

---

## B. COST BASES — the per-unit anchors everything else is priced from

| Basis | Value | Status | Justifying test / artifact |
|---|---|---|---|
| **Card decision** ($/ns per card) | **⚠ SUPERSEDED 2026-07-25 — the card is not the decision, the OFFER is (§A).** Validated: 4090 **755.36** / 4080 **703.51** / 3090 **359.36** ns/day @84,534 → 4090/3090 = **2.10×**. Rank offers on all-in `$/ns`. | **MEASURED** (validated 2026-07-24 grid) | The `1549 / 669 / 175.6` and `72.5 @444k` figures this row used to carry are from the **WITHDRAWN** 23:08 grid (single 0.9–4.5 s windows). Validated re-run: 3 × ~20 s independent blocks per leg, physics-checked (final T 298.7–301.0 K), CV < 1.4%, with a rejection gate that threw out a contended host (CV 18.5%) and a mislabelled card. Table of record: `vast_cost_model.MEASURED_NS_PER_DAY_84K` — the single source of truth, imported by `gpu_backend` and `vast_bid_optimizer` (a second copy is exactly how the withdrawn 669 survived for a day) |
| **Endpoint MD leg** (covalent, ~466k atoms) | **~$0.43/leg on 3090** (measured) → **~1.38 reference-4090 GPU-h ≈ ~$0.19/leg** at the $0.137/ref-GPU-h planning rate | **MEASURED** (3090 real, full-panel ledger; the 4090 conversion is inferred) | **⚠ UPDATED 2026-07-24, converted 2026-07-25 — supersedes "~$0.6/leg" (interim, 6 legs), "~$0.45", and "~$0.26/leg on 4090".** The panel **COMPLETED**: NR-V04 covalent panel, **17 of 18 legs finished**, S3-persisted `dph_total` price ledger, **mean ~$0.43/leg over a 15-leg ledger → ~$8 for the 18-leg panel** (`dph_total` ~$0.10–0.21/hr, 6 ns/leg, ~466–650k atoms, ~19–116 ns/day, host-variance-dominated). Milestone `nrv04_feasibility_covalent` → `cost_measured` in `research/manuscripts/degrader-paper-schedule.json` carries the full as-run ledger. **4090 conversion:** $0.43/leg ÷ ~$0.10–0.21/hr ≈ 2–4 3090-GPU-h ÷ the **validated 2.102×** card ratio ≈ **1.38 ref GPU-h**, × $0.137 ≈ **$0.19**. *(The retired $0.26 used the **withdrawn** 2.42× ratio and a different $/hr assumption; 1.38 ref GPU-h is the figure `vast_cost_model` uses for the 5c row — 24 legs × 1.38 = 33.1 ref GPU-h — so this row and §C now agree.)* This is the one basis in this table that **is** a completed multi-leg measurement on the card quoted. |
| **Alchemical RBFE edge** (complex+solvent, ~35k) | **⚠ SUPERSEDED FOR THE NR4A3 SYSTEM — see the note below this table. Current basis: ~13.7 ref GPU-h ≈ ~$1.9/edge.** *(This row's original value — complex leg ≈ ~3.6 GPU-h; edge ≈ ~5–6 GPU-h ≈ ~$0.6–1.4 — was measured on the **public TYK2** system and must not be used to price NR4A work.)* | **MEASURED on TYK2** (Vast 4090); **re-measured on the real NR4A3 system** (see note) | **firm RBFE, live-diagnosed on instance 45654998 (2026-07-24):** OpenFE HREX complex leg (TYK2 valA, 12 λ-windows, 5 ns production) ran at **~5.2 s/iter × 2000 production iters = ~2 h52 m sampler**, + ~43 min boot/setup → **~3.6 GPU-h billed** at the instance's **$0.122/hr** (~$0.44). Solvent leg (smaller box) extrapolated ~1.5–2 GPU-h. **The cost stands on the measured per-iteration RATE (two independent working 4090 CUDA runs: 45654998 at prod iter 92/2000, 45658414 at equil 71/400, both ~5.1 s/iter, phases advancing normally) × the hardcoded phase counts** — a clean end-to-end ΔG was NOT captured this cycle: both working spot instances were preempted before finishing the ~3 h leg, and because the firm jobspec is `resume=False` neither reached the summary step, so the S3 `firm.json` is a stale PRE-FIX attempt (CUDA-platform fail, predates the OPENMM_PLUGIN_DIR/Dockerfile fix). Getting a completed ΔG needs `resume=True` (+ the equilibration.nc-collision fix) and is a step1_fanout-execution concern, not a pricing one. **The old ~55 GPU-h AWS anchor is REFUTED for Vast, not just de-anchored:** it was a 2026-07-13 A10G leg that was **~65 % GPU-idle (CPU-bottlenecked by 12× per-window am1bcc re-charging)**; the Vast run charges once in setup and keeps the GPU busy → ~15× fewer GPU-h. See `research/modalities/nr4a3-post-pilot-sequence.md` for the pathology |


> **⚠ SUPERSEDED FOR THE NR4A3 SYSTEM (MEASURED 2026-07-24, step1_fanout wave 1).** The ~5.2 s/iter above was
> measured on the **public TYK2 valA** system. The **real cmpd19/NR4A3 complex** samples at **~13.6 s/iter** —
> measured on THREE independent Vast 4090 hosts in the same wave (14.42 / 12.76 / 13.70 s/iter, 16 iteration
> samples each), a tight enough spread to rule out host variance. **Aggregate MD throughput on the same card
> class: TYK2 ~498 ns/day vs NR4A3 ~190 ns/day** (12 windows x 2.5 ps per iteration). ⚠ **The MECHANISM of the
> 2.6× is NOT established** — an earlier revision of this note asserted the NR4A3 complex is "simply a heavier
> system", which was a plausible story, not a measurement. The two candidate drivers are **particle count** (no
> NR4A3 binary-RBFE particle count is recorded anywhere in this repo — the ternary's 146,509 is, the binary's is
> not) and **timestep ceiling** (4 fs vs 2 fs is a clean 2×, and is a documented PER-EDGE property here).
> **TIMESTEP IS NOW EXCLUDED (measured 2026-07-24, free CPU).** Reading the EFFECTIVE protocol settings off a
> real hybrid build instead of assuming them: `forcefield_settings.constraints == "hbonds"`,
> `hydrogen_mass == 3.0` — that is **OpenFE's default**, so the production lanes (which set nothing) build a
> system where **every X-H is a constraint**. Measured on both known-answer anchors: `xh_total = 0` against
> 1771 / 4997 total constraints, and the alchemical valence CustomBondForce (11 / 28 bonds) contains **no X-H
> at all**. Nothing is left flexible to cap the timestep, so **the fan-out ran at 4 fs and there is no 2×
> timestep lever**. That conclusion is about WORK, and it survives; the ~$91–101 it was attached to does
> not — that figure is superseded by ~$36 (2026-07-25, the $/hr axis). That leaves **particle count as the sole remaining
> candidate** for the 2.6×, and it is still unrecorded for the NR4A3 binary complex. What IS established is the rate itself, and that a TYK2 rate must not be used
> to price NR4A3 work.
> Recomputed on the repo's own hardcoded leg length (400 equil + 2000 production = 2400 iters,
> `nr4a3_rbfe.py:364-365`): complex leg **~9.1 GPU-h** (not 3.6), solvent ~4.1, **unit ≈ 13.7 GPU-h**.
> Realized bid on this wave was **$0.35–0.39/hr** (current 4090 market, `min_bid × 1.5`), not the $0.122/hr the
> old row used — so **~$4.80–5.30 per edge** and **~$91–101 for the 19-edge `step1_fanout`** *(⚠ SUPERSEDED 2026-07-25: the $0.35–0.39/hr was what `× 1.5` on a `min_bid`-ranked offer costs, not the market — at the measured $0.137/ref-GPU-h it is **~$1.9/edge and ~$36 for the fan-out**)*, against a pinned
> estimate of $12–26. The two errors compound: a 2.6× slower system on a 3× pricier bid.
> **⚠ The "card choice is NOT the lever" conclusion that stood here is RETIRED (2026-07-25).** It computed a
> 4090 and a 3090 at ~$0.0014/iteration each, but on the *two specific prices then in hand* and the
> **withdrawn** 2.42× ratio. Neither generalises: the validated ratio is **2.10×**, and across the live board
> the cheapest 3090 floor is **8.8×** below the cheapest 4090 while the spread *within* the 4090 class alone is
> 2.3×. **Neither card is the answer — rank live offers on all-in `$/ns` (§A).** What survives is the wall-clock
> caveat: a 3090 needs proportionally more time, so a leg with a hard continuity requirement is more exposed on
> it. *(The **2.10×** stated here is superseded — Appendix T.)*
> ⚠ **CORRECTION 2026-07-26 — the L4→4090 card ratio of "~2.06× (33 → 16 s/iter)" compares a WARMUP rate against
> a PRODUCTION rate.** The 33 s/iter figure is the 33.91 s/iter measured during **warmup** on a spot L4; the
> 4090's 16 s/iter is a **production** median. Production-to-production, measured in-log and flat over 600
> consecutive production iterations (GH run 30210933840): **L4 = 56.5 s/iter**, so the ratio is **~3.53×**, not
> 2.06×. Independently corroborated by memory bandwidth — L4 ~300 GB/s vs 4090 ~1008 GB/s is 3.36×, and OpenMM
> PME on a 142k-particle system is bandwidth-bound, so the two agree to ~5 %.
>
> **What this changes:** the **L4-on-demand** as-run figure. At 2800 iterations × 56.5 s = 43.9 L4-h/leg and
> 6 legs/edge, an edge is **~264 L4-h ≈ $187**, not ~$94. That figure is already marked *not a go-forward cost
> basis* here, so **the ladder pricing is unaffected** — but it is the number the **GCP free-credit runway**
> depends on, and that runway is now the binding constraint on the GCP lane (see credit-status.json).
> **What this does NOT change:** every Vast/4090-based figure in this table, which was measured directly on the
> 4090 and never used the L4 rate.

| **Alchemical ternary cooperativity edge** (3-replica, ~146k particles, **12** windows) | **~$10.2 ($3.7–26)** for the full 3-replica edge — **~65–84 ref GPU-h** ★ **CORRECTED 2026-07-25: the as-run leg is 2800 iterations, not 2400 — warmup iterations derive from the WARMUP integrator at 1 fs (800, not 400), each the same 1250 steps, so every 2 fs ternary figure below was ~17 % low. The prose beneath this cell still reads 2400 in places and is superseded by this line.** *(was ~$8.8 on the 2400 basis)* at the measured **$0.137/ref-GPU-h** *(REPRICED 2026-07-25; was ~$10–16 on a ~$0.15–0.25/hr assumption, ~$26 at ~$0.40/hr, and ~$20–28 at the $0.35–0.39/hr actually realized. The GPU-h are unchanged.)* | **RATE measured directly on Vast 4090; LEG LENGTH now OBSERVED — valB_mini's ternary seed 0 reached 2000/2000 production iterations. No ternary edge has completed end-to-end on a 4090, so the dollar figure is still rate x length.** | **⚠ RECONCILED 2026-07-24 — combines a direct 4090 rate measurement with the corrected leg length; supersedes BOTH the ~$3–6 and the ~$4–7 that preceded it.** **LEG LENGTH NOW CONFIRMED FROM THE COMMITTED TRAJECTORY (forensic read, GH run 30117943561, 2026-07-24).** `mode=forensic` on `calib_hi_to_lo__ternary_vhl` seed 0 opened the committed generations and reports `reporter_checkpoint_interval: 40`, `analysis_last_iteration: 1560`, `checkpoint_last_iteration: 1560`, `TORN: false`, 12 generations all at interval 40. So the ternary leg's production target is **2000 iterations**; it read 1560 committed (~78 %) mid-flight, and has since reached **2000/2000** (convergence run 30157501491, MBAR ΔG 47.511 ± 0.045). **This also root-causes the ~920 figure both prior estimates were built on: 920 = 23 x 40 and 1560 = 39 x 40 are CHECKPOINT BOUNDARIES, not leg lengths** — the sampler line `binary_vhl leg at iter 913/920` meant "at 913, next checkpoint 920", and it was the BINARY arm, not the ternary one. Leg = 400 warmup + 2000 production = **2400 iterations** at 2.5 ps/iter. *Rate (theirs, better than a card-ratio guess):* the firm ternary leg on the Vast rtx4090 nr4a3fep image (`run_ternary_leg.sh`, 12 windows, self-staged 8G1Q, 146,284 particles) cleared warmup with no NaN and held production steady at **~14–18 s/iter (median ~16)**. *Leg length (corrected):* the protocol hardcodes **1 ns equilibration + 5 ns production** (`nr4a3_ternary_fep.py:343-344`, `nr4a3_rbfe.py:364-365`) and iterations = sim_length / 2.5 ps, so a leg is **2400 iterations (400 equil + 2000 production)** — confirmed by the openmmtools `.chk` history `iters 0,20,…,2000`. **The ~920-iteration figure that both prior estimates used as 'a full leg' is ~38 % of one**, which is why ~$3–6 and ~$4–7 are each ~2.6× low. Arithmetic: 2400 × ~16 s ≈ **~10.7 4090-GPU-h/leg**; edge = binary+ternary × 3 replicas = 6 legs ≈ **~64 GPU-h** ≈ **~$8.8** at the $0.137/ref-GPU-h policy *(the ~$10–16 this arithmetic first gave assumed ~$0.15–0.25/hr)*. *What the 4090 measurement DID settle:* the **L4→4090 card ratio is validated at ~2.06×** (33 → 16 s/iter) — a ratio of rates is independent of the iteration count, so that conclusion survives the leg-length correction intact and the old spec-based ~2.3× 'soft spot' is closed. ΔG is not the cost basis (throughput is); the ΔG comes from the GCP valB production lane (ΔG_morph 47.28). No clean end-to-end ΔG has been captured on Vast — the firm path is `commit store: LOCAL`, `resume=False`, and the instance was spot-preempted late in production. Old ~$65–110 (off the refuted 55-GPU-h anchor) superseded; **L4-on-demand ~$94 as-run is NOT a go-forward cost — Vast only.** |
| **Co-fold / docking** (basin nomination) | **~$0–50, cheap** (CPU docking + short Boltz/AF3 co-fold inference) | **ESTIMATED** (known-cheap class) | prior smina/Vina warhead screen + NR-V04 Boltz co-folds; CPU or short GPU. Weak/biased predictor — used to *nominate*, never to kill a small wedge |

### ★ B.0 — TWO PRICING IDENTITIES ADOPTED 2026-07-24 (they change stage costs without changing any basis)

Both come from the [ternary-selectivity strategy revision](../manuscripts/nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md);
neither adds or removes science, and both were previously mis-priced.

1. **A PARALOGUE PANEL IS N TERNARY *LEGS* + ONE SHARED BINARY + ONE SHARED SOLVENT — NOT N EDGES.**
   `nr4a3_ternary_fep.py` defines `binary_<e3>` as **E3 machinery + PROTAC with NO target**, and `solvent` as
   ligand-in-water. Both are **paralogue-independent**, so for any morph
   `ΔΔG_coop(P) − ΔΔG_coop(P′) = ΔG_ternary,P − ΔG_ternary,P′` **exactly**. Pricing a 3-paralogue comparison as
   "3 ternary edges" pays for the shared legs three times over: 18 legs where 12 suffice (−33 %), or 9 if only
   the selectivity *contrast* is needed (−50 %). Affected rows below: `valB_full` module 3,
   `nrv04_retrospective`, `local within-basin FEP`, and the new 5a-KS primary test.
2. **4 fs TERNARY PRODUCTION HALVES EVERY TERNARY LEG — PROPOSED, not yet adopted.** Iterations are
   ⚠ **CORRECTED 2026-07-25: NOT timestep-independent, and NOT half.** Iterations are `steps ÷ steps_per_iteration`
   and steps depend on dt, so 2.5 ps/iter holds only *at 2 fs*. 4 fs halves the force evaluations **in production
   only** — the warmup is pinned at 1 fs either way — giving 2.25e6 vs 3.5e6 steps, a **0.643× conversion, i.e. a
   1.56× saving, not 2×**. `ternary-rbfe-runbook.md`
   §1c records production **40/40 at 4 fs with zero NaN** after plain-MD pre-equilibration, but the runbook also
   requires validation and production at the **same** timestep and 40 iterations is not 2000.
   **⚠ The as-run baseline was VERIFIED against the live lane, not the doc (2026-07-24 4:12 PM ET, GH run
   30123894814 `mode=tail` on VM `gcp-ternary-30112102294`): `[tfep] timestep=2.0 fs` with
   `warmup_dt_override="WARMUP timestep overridden to 1.0 fs"`, `NaN_seen=no`.** So the lane is 1 fs warmup →
   **2 fs production**; the "4 fs" people remember is the §1c pre-equilibration demonstration, and the workflow
   defaults are `timestep_fs: 2.0` / `use_preequil: 0`. **Until the ~$4.4 matched re-calibration edge (schedule
   `ternary_4fs_recalibration`) runs, keep quoting the 2 fs base**; the 4 fs figures below are the post-adoption
   value. The adoption run must pass `use_preequil=1` (4 fs only held with pre-equilibration) and
   `reset_commits=1` (OpenFE refuses to resume a checkpoint whose protocol timestep differs, so a dt change is a
   fresh edge, not a continuation).

**What reduces to a basis — and the one thing that does NOT:**
1. **LIGAND-alchemy stages (binary RBFE, ternary cooperativity, local within-basin FEP) reduce to the RBFE-edge
   and ternary-edge bases** — they are the same OpenFE `RelativeHybridTopologyProtocol` machinery differing only
   in system size and window count, so they are priced per edge, not as separate tests.
2. **Endpoint-MD stages (covalent panel, ensemble/CRL refinement MD) reduce to the endpoint-MD basis** — same
   engine, scaled by system size.
3. **⚠ PROTEIN-MUTATION FEP DOES *NOT* REDUCE TO THESE BASES — CORRECTED 2026-07-24.** This file previously
   asserted that the mutation cycle (`ΔG_mut^ternary − ΔG_mut^binary`, the 5a-KS wedge) "is the same OpenFE
   alchemical machinery, so it is priced per (binary edge + ternary edge)." **That is false, and it was the
   load-bearing assumption under the 5a-KS price.** Evidence:
   - OpenFE's `RelativeHybridTopologyProtocol` (what `nr4a3_rbfe.py` and `nr4a3_ternary_fep.py` both drive) is a
     **small-molecule** RBFE protocol: it builds its hybrid topology from a **ligand-to-ligand atom mapping**
     (LOMAP/Kartograf). Every "mutation" in this repo's alchemical code is a **ligand substituent** swap
     (`nr4a3_rbfe.py:221`; `rbfe_map.py:30,464`, guarded `single_site`). Nothing in either driver mutates a
     protein residue.
   - The repo's **only** protein-mutation path is `nr4a3_resistance_ddg.py:53`
     (`fixer.applyMutations([mutation], CHAIN)` → PDBFixer rebuild), scored by
     `endpoint_dG` / `endpoint_dG_multisnapshot` — i.e. **MM-GBSA endpoint scoring, which is not alchemical and
     not a free-energy calculation of the kind the wedge claims.**
   - **Consequence at the time:** the mutation wedge had **no implementing engine in this repo**, so its
     "~$5–10 for 1 alchemical direction" was unfounded and the row was carried as UNPRICED.
   - **★ RESOLVED 2026-07-25, in two steps.** (1) The 2026-07-24 ternary-selectivity revision made the
     **ligand-side double difference** the *primary* causal test — it is ordinary ternary-lane alchemy and needs
     no protein-mutation engine at all, so the ladder's gate was never really blocked on this (§C, `5a-KS
     primary`). (2) The **confirmatory** mutation line then got a real engine: perses was retired the same day
     it was tried (its core residue atom map round-trips through a licence-gated OpenEye OEMol), the lane was
     rebuilt on **pmx + GROMACS**, and its known-answer benchmark **passed** — so the row moves from UNPRICED to
     **PROJECTED**, with the projection basis stated in §C. An engine that exists is still not an NR4A-scale
     rate; only a completed NR4A-scale leg would give one.
   - The *other* 5a-KS blocker stands as a permanent design constraint: the mutation wedge is the repo's one
     **cross-lane subtraction**, and the two lanes run **different charge models** (binary = am1bcc, ternary =
     NAGL), so a single `CHARGE_METHOD` must be pinned across both legs and stamped into both result JSONs
     before any wedge is computed. `nr4a3_protein_fep.assert_charge_consistency` enforces this as a refusal.

So of the four cost bases, three (card, endpoint-MD leg, RBFE edge) are MEASURED; the ternary edge is a measured
**rate** × a now-**observed** leg length (valB_mini's ternary seed 0 reached 2000/2000 production iterations),
but **no ternary edge has completed end-to-end on a 4090**, so the Vast figure remains a projection; and the
mutation-cycle stages have a **qualified engine with a particle-count-projected cost**, not a measured basis.

---

## C. STAGE COSTS — each = a cost basis × a count

| Stage | = basis × count | cost (Vast 4090) | status |
|---|---|---|---|
| RUNG 0 (charge fix, EMC E3, pocket) | CPU/CI | **~$0** | MEASURED (done) |
| `valA_mini` (TYK2 build-consistency) | 1 RBFE edge (reduced) | **~$0–15** | MEASURED (done, GCP L4) |
| `step0` RBFE shakeout | infra | **~$1–2** | MEASURED (done) |
| `step1_pilot` cmpd19 | 1–2 RBFE edges (14–27 ref GPU-h) | **~$2.8** ($0.8–8.5) | REPRICED 2026-07-25 |
| `step1_fanout` cmpd19 map | **19 RBFE edges** × ~13.7 ref GPU-h = **260** | **~$36** ($15–80) | REPRICED 2026-07-25. **The old ~$12–26 was stale on BOTH axes** — it used the ~3.6-GPU-h TYK2 leg (the real cmpd19/NR4A3 complex is ~2.6× heavier, unit ≈ 13.7 GPU-h) and a $0.122/hr instance. Measured-as-run was **$91–101** at $0.35–0.39/hr; the GPU-h correction stands, the $/hr one is what this reprice fixes |
| `valB_mini` ternary | 1 ternary edge, 56–72 ref GPU-h | **~$8.8** ($3.2–22) | REPRICED 2026-07-25 (was ~$10–16 at $0.15–0.25/hr, ~$20–28 at the realized $0.35–0.39). **~$94 as-run on L4 on-demand is not a go-forward cost.** ⚠ The GPU-h are from a **SMARCA2/VHL** leg used to price **NR4A** — see the transferability warning below |
| `valB_full` ternary cube | 2–3 ternary edges + CRL-MD, 112–216 ref GPU-h | **~$22.5** ($6–67) | REPRICED 2026-07-25 (was ~$20–65) |
| `nrv04_feasibility_covalent` | 18 endpoint-MD legs | **~$8 total for the 18-leg panel** | MEASURED (endpoint MD; not a per-edge alchemical base) |
| `nrv04_retrospective` | NR4A1/2/3: **3 ternary LEGS + 1 shared binary + 1 shared solvent** (B.0-1), + endpoint-MD ensembles | **~$24** ($5.6–78) | ★ REPRICED 2026-07-26 onto the **as-run 2800-iteration** ternary leg (warmup iterations derive from the WARMUP integrator at 1 fs → **800**, not 400, each the same 1250 steps; verified in `rbfe_spot_driver._iters_from_time`), so **98–252 ref GPU-h**. The prior ~$21 / 84–216 used the retired 2400 basis and was **~17 % low**. ⚠ **This line prices Arm F (alchemical), which the preregistration does NOT authorise and which is BLOCKED** — what a GO would actually spend is **Arm E: 18 legs ≈ $7.7** at the measured $0.43/leg. PROJECTED on the ternary component |
| `5a` orientation-basin search (now multi-E3, pose-marginalised, + 2 categorical terms) | CPU $0 + optional MM-GBSA rescore | **~$0–50** | MEASURED-derived |
| **TIER-0 `nr4a_unique_residues`** (paralogue-unique Cys/Lys map) | CI CPU, no GPU | **$0** | DONE 2026-07-24, CI run 30123828812 (nothing to measure) |
| **`ternary_4fs_recalibration`** (cost lever 1) | 1 ternary edge @4 fs, 28–36 ref GPU-h | **~$4.4** ($1.6–11) | REPRICED 2026-07-25; settles B.0-2 |
| **5a-KS kill-switch — PRIMARY (ligand-side double difference)** | Tier-0 map ($0) + basin ($0–50) + **ternary legs only** for one matched pair (B.0-1) | **~$12** ($1.6–45) | REPRICED 2026-07-25 (was ~$5–25); 28–144 ref GPU-h. No protein-mutation engine involved |
| 5a-KS **CONFIRMATORY** (protein-mutation direction) | 1 protein-mutation direction — **pmx + GROMACS engine QUALIFIED 2026-07-25** (perses retired 2026-07-24: OpenEye-gated) | **~$4.6 PROJECTED (3 replicates)** / ~$3.1 (2 rep) — *excluded from the ladder total* | **★ THE BENCHMARK RAN AND PASSED, so this row is no longer UNPRICED — but it is a PROJECTION, not a rate.** Full set on Vast (equilibrium λ windows + BAR), scored by `protfep_reduce` against SKEMPI 2.0-verified references → [`protfep-benchmark-result.json`](../modalities/protfep-benchmark-result.json): **Y29A +4.424 ± 1.077** vs +3.40 (err 1.024) and near-null **Y29F −0.370 ± 0.175** vs −0.13 (err 0.240), both inside ±1.5 and **correctly ordered**; `qualified: true`. **Measured rate: 1.058 ± 0.432 GPU-h/leg** over 11 legs at a 25,187-particle mean → **$0.212/leg** at the reducer's assumed $0.20/hr. The NR4A figure comes from `protfep_reduce.price_from_legs`, which scales that by **linear particle count** to 146,284 (ternary) and ~35,000 (binary) — a standard first-order assumption for PME MD at fixed cutoff, **an assumption and not a measurement**, so it may not be quoted as a rate and the row stays out of the pinned total. Sequence still applies: smoke ~$0.10 → pilot ~$1–3 (abort gate) → set ~$5–10. **Also unresolved:** between-setup scatter is effect-size dependent by **6.2×** (±1.08 on the hot spot, ±0.18 on the near-null) while within-leg MBAR SEs are 0.05–0.13, so **no benchmark yet probes the wedge's own ~1 kcal/mol regime**. **Role: CONFIRMATORY second line, not the ladder's gate.** |
| full reciprocal mutation cycle (3→1 + 3→2 + 1/2→3) | ~3 protein-mutation directions | **~$14 PROJECTED** (3 × the row above) — *excluded from the ladder total* | Same engine, same projection basis and the same caveat: particle-count-scaled, not measured at NR4A scale |
| `5b` inverse linker design | mostly CPU $0 + occasional rescore | **~$0–20** | MEASURED-derived |
| ensemble refinement / CRL MD (5c) | endpoint MD, 24–~200 legs × ~1.38 ref GPU-h | **~$21** ($1.9–85) | REPRICED 2026-07-25 (was ~$15–100). Per-leg ref GPU-h backed out of the completed 18-leg covalent panel (~$0.43/leg on a 3090 at ~$0.10–0.21/hr ÷ the 2.102× card ratio). Still the biggest swing item — the leg COUNT, not the rate, now dominates |
| local within-basin FEP | 3–6 ternary **comparisons** (ternary legs only, B.0-1), 56–260 ref GPU-h | **~$22** ($3–80) | REPRICED 2026-07-25 |
| `ternary_prospective_matrix` (now 5a–5d ladder) | ~4–12 constructs via 5c/5d | **folded into 5c+5d above** | MEASURED-derived |

**★ Whole gated ladder ≈ ~$169 mid-range (~$46–626) for the PRICEABLE stages, GO at every gate** *(the **~$158 (~$44–578)** carried here until 2026-07-30 is superseded: RUNG 5a-KS went from 2 ternary legs to 4 — n = 2 seeds per arm — and NOTHING else moved, same market snapshot and same rate; STRATEGY Appendix A row 54)* *(the
**~$185 (~$51–614)** that stood here is superseded — Appendix T)* — repriced
2026-07-25 onto the measured Vast policy (**$0.137 per reference GPU-hour**, best-10-offer planning rate; range
$0.057 best offer .. $0.309 median). Regenerate the alchemical/MD stages with
`python research/modalities/vast_cost_model.py`; JSON in
[`vast-ladder-repricing.json`](../modalities/vast-ladder-repricing.json).

**Derivation, so all three places can be checked against each other.** The tool prices 9 stages at
**$149.4 ($38.2–466.4)**. The ladder figure adds what the tool does not cover: step0 ~$1–2 (mid $1.5),
`valA_mini` ~$0–15 (**realized ~$0** on GCP credit), the ~$8 measured covalent panel, 5a basin ~$0–50 (mid $25),
5b linker ~$0–20 (mid $10). So `149.4 + 1.5 + 0 + 8 + 25 + 10 ≈ 194`; low `38.2 + 1 + 8 ≈ 47`; high
`466.4 + 2 + 15 + 8 + 50 + 20 ≈ 561`. nr4a3-program-map.md's per-step `Cum.` chain and
[bid-strategy.md §6](./bid-strategy.md) end on the same numbers. *(The `~$46–544` this line previously carried
did not sum; corrected 2026-07-25. Superseded totals: ~$467 (~$249–685), ~$240 (~$90–390), ~$390 (~$170–610),
and a stray ~$128 that was bid-strategy §6's table with the 5c row missing.)*

**Excluded from the total:** Optional/HELD ΔG_open + ABFE; and the 5a-KS **confirmatory** protein-mutation wedge
+ reciprocal cycle — their engine **qualified on 2026-07-25**, but the NR4A cost is a particle-count projection
(~$4.6 for 3 replicates), not a measured NR4A-scale rate.

**⚠⚠ THIS REPRICE FIXES THE `$/hr` AXIS ONLY — THE GPU-HOUR AXIS KEEPS EVERY UNCERTAINTY IT HAD.** The reference
GPU-hours above are the repo's own work estimates; this multiplies them by a measured rate, it does not
re-derive them. In particular the ternary base is **a rate measured on the SMARCA2/VHL 8G1Q assembly being used
to price NR4A ternaries** — the *same* non-transferability that cost **2.6×** on the binary lane when the real
cmpd19/NR4A3 complex turned out to sample at ~13.6 s/iter against TYK2's ~5.2. **If the GPU-hours are 2.6× low,
these costs are 2.6× low no matter what we bid.** Expect an NR4A ternary leg to be heavier, not lighter, and
time one before treating the ternary rows as firm.

**⚠ "Now that every base is measured, the ladder totals cleanly" was wrong when it stood here, and it is still
wrong. What is and is not settled, as of 2026-07-25:**
- **Ternary edge — a measured rate × a now-observed leg length, but still a projection.** The *rate* is measured
  (~33 s/iter on L4; ~16 s/iter on a Vast 4090, giving a validated L4→4090 ratio of **~2.06×**, count-independent).
  The *leg length* is no longer a projection either: valB_mini's ternary seed 0 reached **2000/2000** production
  iterations, confirming the hardcoded 400 + 2000 = 2400. **But no ternary edge has completed end-to-end on a
  4090**, so **~$8.8/edge** is rate × length, not a realized bill (~$94/edge as actually run on L4 on-demand).
  *(The earlier ~$3–6 and ~$4–7 each treated 920 iterations — a checkpoint boundary on the **binary** arm — as a
  finished leg, ≈38 % of one; the intermediate ~$7–15 predates the $0.137/ref-GPU-h policy.)*
- **RBFE edge — measured on the real system, and it is the cautionary tale.** The Vast-4090 rate is now taken on
  the actual cmpd19/NR4A3 complex on three independent hosts, giving **~13.7 ref GPU-h ≈ ~$1.9/edge** and
  `step1_fanout` ≈ **~$36**. The retired ~5–6 GPU-h / ~$0.6–1.4 was a **public TYK2** rate; applying it to NR4A
  is exactly the error that cost 2.6×.
- **Mutation-cycle stages — a qualified engine with a projected cost.** pmx + GROMACS passed its known-answer
  benchmark 2026-07-25 at a measured **1.058 ± 0.432 GPU-h/leg**, but the NR4A number is particle-count-scaled
  (~$4.6, 3 replicates) and stays **excluded from the ladder total** (B.3, §C).

Remaining swings, in order: the **ensemble-MD leg count** (5c refinement + the retrospective), the **ternary
transferability risk** (a SMARCA2/VHL rate pricing NR4A ternaries), then the mutation projection. Price and gate
each rung individually at its gate.

---

## D. PROVENANCE — the actual tests (how to reproduce / verify each number)

- **Card decision + per-card $/hr** — `fusion-cpu-extras.yml` `task=nrv04_vast_launch`, `vast_launch_mode` ∈
  {`probe_offers`, `bench`, `bench_grid`, `bench_collect`}. Bench engine: `gpu_md_bench.py` (self-contained TIP3P
  box). Results: `s3://sagemaker-us-east-2-646605541856/vast-bench-results/<tag>/bench.json`.
- **Endpoint-MD leg** — NR-V04 covalent panel; `nrv04_covalent_md.py`; S3 price ledger under
  `nrv04-covalent-results/`. Launch/collect via `vast_launch_mode` ∈ {`pilot`,`full`,`collect`}.
- **RBFE edge — MEASURED on Vast 4090 by the firm run (this session).** `fusion-cpu-extras.yml`
  `vast_launch_mode=firm firm_kind=rbfe`. Runs `nr4a3_rbfe.py` on the OpenFE Vast image
  `triskit23/nr4a3fep:latest` (openfe 1.12 + ambertools + gemmi/pdbfixer + awscli), self-staging the public TYK2
  valA edge. Results `s3://…/vast-firm-results/firm-rbfe-rtx4090/firm.json` (+ `firm.log`). Gotchas baked/set:
  `OPENMM_PLUGIN_DIR`, `SSL_CERT_FILE`, `openfe>=1.12`, 24 h ceiling. **This is the ONLY Vast-4090 alchemical
  timing anywhere.** **MEASURED 2026-07-24** by live-diagnosing the running sampler on instance **45654998**
  (`Iteration 92/2000 · ~5.2 s/iter · est. total wall 2:52:26`) → complex leg = ~2 h52 m production + ~43 min
  boot/setup ≈ **~3.6 GPU-h** at **$0.122/hr** ≈ **~$0.44**. **A clean completed `firm.json` (ns/day + ΔG) was
  NOT captured** — both working spot instances (45654998, 45658414) were preempted before the ~3 h `resume=False`
  leg finished, so the S3 `firm.json` remains a stale pre-fix CUDA-fail artifact; the cost rests on the measured
  per-iteration rate, which needs no completed run. (Two known execution bugs surfaced, both step1_fanout/valB
  concerns not pricing: some Vast hosts fail the CUDA platform lookup pre-fix; and the ternary firm hit an
  `equilibration.nc already exists` spot-restart collision despite openfe≥1.12 — fix with `resume=True` + a
  fresh-vs-restore guard when that rung is authorized.) **Note** `N_ITER` does NOT truncate production — `nr4a3_rbfe.py` hardcodes
  5 ns / 2000 iters (`:364-365`), so the leg always runs full; the earlier "ran ~2 h without finishing" was the
  leg on track to finish at ~2 h52 m, **not** evidence of a 55-GPU-h leg. Caveat: the probe re-runs the
  (already-passed) TYK2 valA edge; to make it *real science + cost*, point it at a live cmpd19 `step1_fanout`
  edge (needs a go + S3 pose staging).
- **Ternary edge — a measured RATE, PROJECTED to a leg (2026-07-24; corrected same day).** The `valB_mini` Wurz
  cmpd1→cmpd4 cooperativity FEP is running for real on GCP L4 (`gpu-ternary-fep-gcp.yml`, branch
  `claude/rung-2-parallel-7asnpk`, detached on-demand VM tailed hourly). What it has produced so far is a
  **per-iteration rate**: 146,509 particles, **12** windows (`gpu-ternary-fep-gcp.yml:29,70` — the code's
  `N_WINDOWS` default of 16 is never used), **~33 s/iter**, `total wall clock time 8:40:29` at ~920 iterations.
  **⚠ 920 iterations is NOT a finished leg** — the protocol hardcodes 1 ns equilibration + 5 ns production at
  2.5 ps/iteration = **400 + 2000 = 2400 iterations** (`nr4a3_rbfe.py:364-365`; the openmmtools `.chk` history
  `iters 0,20,…,2000` confirms the production count). 920/2400 ≈ **38 %**, so the earlier "~8.7 GPU-h per leg"
  was ~2.6× low and every ternary cost derived from it was correspondingly low. **Projected** full leg ≈
  2400 × 33 s ≈ **~22 L4-GPU-h**. Edge = binary + ternary leg; `min_replicas_per_leg=3` (prereg) → full 3-replica
  edge ≈ **~132 L4-GPU-h ≈ ~57 4090-GPU-h**. **⚠ The old parenthetical here — "conservative: the binary leg is a
  smaller box and should run faster, not yet separated" — is REFUTED (2026-07-24, live log of GH run 30123894814
  reading VM `gcp-ternary-30112102294`): the `calib_hi_to_lo__binary_vhl` leg ran at **~28.6–38.2 s/iter
  (median ≈33)** on L4, i.e. the SAME rate as the ternary leg's ~33 s/iter. Do not discount a binary leg; it is a
  full-price leg. This makes the B.0-1 sharing identity worth MORE, not less.** Cost: **~$8.8 Vast 4090**
  ($3.2–22 at the $0.137/ref-GPU-h policy), **~$94 L4-on-demand** — provider/card dominates because the edge is
  GPU-h-heavy. **★ UPDATED 2026-07-25 on two points.** (i) The line that stood here — *"No ternary leg has ever
  completed, so the leg length itself is unverified"* — is retired: valB_mini's `calib_hi_to_lo__ternary_vhl`
  seed 0 reached **2000/2000** production iterations (convergence run 30157501491, MBAR ΔG 47.511 ± 0.045), so
  the 2400-iteration leg is now **observed**, not assumed. What is still true, and still the reason this is a
  projection: **no ternary edge has completed end-to-end on a 4090.** (ii) The L4→4090 ratio is no longer
  spec-based — a direct 4090 ternary leg held ~14–18 s/iter (median ~16) against L4's ~33, **validating ~2.06×**;
  a ratio of rates is count-independent, so it survived the leg-length correction intact.
  **Direct Vast-4090 firm-ternary measurement — a first attempt was blocked by a
  warmup NaN (2026-07-24), a later one produced the rate.** The first firm-ternary path was given the required
  plain-MD pre-equilibration (`ternary_preequil.py`, wired into `nrv04_vast_launch.py`), which ran clean (~7 min,
  relaxed complex overlaid) and got the alchemy from λ-state 0 to **state 5** before a `SimulationNaNError` at
  warmup — the softcore instability of the rough SMARCA4→SMARCA2 homology model. A subsequent firm leg
  (`run_ternary_leg.sh`, 12 windows, self-staged 8G1Q, 146,284 particles) cleared warmup with no NaN and held
  production at **~14–18 s/iter (median ~16)**, which is the 4090 rate the **~$8.8** figure uses. What it did
  **not** do is finish: the instance was spot-preempted late in production with `commit store: LOCAL` and
  `resume=False`, so there is still no completed Vast edge. The NR-V04 "NR4A1 degrader" sims are the **covalent
  panel = endpoint MD** (celastrol is covalent), feeding the endpoint-MD basis, not this one.
- **De-anchored AWS RBFE baseline** — `research/modalities/nr4a3-post-pilot-sequence.md` (2026-07-13) +
  `sm_gpu_util.py` (live CloudWatch GPU-util probe). Kept only as historical context; **not** the Vast number.
- **Design/count sources (unpinned)** — `research/modalities/congeneric-rbfe-map.json` (19 RBFE edges,
  `est_gpu_h: null`); the prospective-matrix + mutation-cycle counts in `nr4a3-program-map.md`.

---

## E. Operational Vast setup (bid, image, gotchas)

The go-forward lane is Vast (4090 default / 3090 fallback). The operational settings below are the hard-won
defaults; the code of record is `research/modalities/gpu_backend.py` (`VAST_BID_FLOOR_MULT`) +
`nrv04_vast_launch.py` (launch modes) + `research/compute/Dockerfile.nr4a3fep`.

- **Bid = the market floor plus a staleness tick** (`min_bid × 1.02`, minimum +$0.0005), **capped at that
  machine's on-demand price**, and **never at or below `min_bid`** (a below-floor bid leaves the box
  created-but-stopped). Set by `vast_cost_model.recommended_bid`; `gpu_backend._vast_bid_price` delegates.
  **This replaces `× 1.5` here, `× 1.9` in bid-strategy.md and `× 1.25` in the code — all three were live at
  once.** Measured 2026-07-25 by renting one offer at three bid multiples: **`charged = min(your bid, the
  machine's on-demand price)`** (×1.0 → $0.00930 on a $0.00930 bid; ×2.5 and ×8.0 both → $0.021333, matching
  that machine's on-demand `dph_base` to 17 s.f.). So a premium is paid on **every hour**, and per Vast's docs
  it cannot buy safety from on-demand renters at all — break-even needs the hazard to fall >100/hr per $/hr.
  Retention is bought with **checkpoint frequency**, which is free.
  ⚠ **The >100/hr break-even rests on two disputed inputs (2026-07-25)** — see
  [vast-churn-observations-2026-07-25.md](./vast-churn-observations-2026-07-25.md). It is computed with a
  hazard of 0.10/h and a reload-free preemption; the 5a-KS run saw a hazard 2.5–4× that, and a dominant
  failure mode (`resources_unavailable`) which cannot be resumed at any bid and so pays a full image pull
  per occurrence. A cheaper-looking preemption makes a premium look less justified, so the threshold is
  soft in the direction of *under*-stating the case for a margin. **The bid itself is NOT known to be
  wrong** — raising a stuck leg's bid 26% bought nothing, which independently supports "tick, not premium",
  and retention was never tested. What needs re-deriving is the justification, against measured λ and R. `VAST_BID_FLOOR_MULT` survives as an unset
  escape hatch for a leg that genuinely cannot be paused. Full derivation: [bid-strategy.md](./bid-strategy.md).
- **Rank offers by all-in `$/ns`, not `$/hr` and not `min_bid`.** Ranking by the floor is the single most
  expensive habit this file used to endorse: best-to-median spread on the live board is **5.43×**.
- **Ask for the disk the job needs.** Storage bills continuously, running *or paused*; at the cheap end of the
  board it is 42% of all-in cost, and halving it beats the entire bid change.
- **Pin OpenMM's CUDA in the image, and filter the host driver to match.** An unpinned env pulls a too-new
  CUDA-13+ OpenMM whose PTX won't JIT on an older host driver (`CUDA_ERROR_UNSUPPORTED_PTX_VERSION`) — control
  our build, don't chase bleeding-edge hosts. ⚠ **The driver floor is NOT restated here: its one home is
  `gpu_backend.ResourceSpec.min_cuda`**, which carries the value in force and the evidence behind it — this
  line used to name a value of its own and drifted out of step with the code. ⚠ **The value in force is
  MEASURED to be too high for the ternary image and has not yet been changed** —
  [vast-placement-facts.md §4](./vast-placement-facts.md) carries the probe, the board cost and the pending
  edit. Also filter `reliability2 ≥ 0.90` and require ≥24 GB VRAM. *Superseded, retained: this
  line also used to end "rank offers by `min_bid`" — which contradicted the `$/ns` ranking bullet two above it
  in this same list. That bullet is the rule; ranking is not restated here.*
- **OpenFE image** `triskit23/nr4a3fep:latest` (public) — openfe ≥1.12 + ambertools/am1bcc + lomap/kartograf +
  OpenMM CUDA 12.6; the enabler for `nr4a3_rbfe.py` + `nr4a3_ternary_fep.py` on Vast (the covalent-MD `nrv04vast`
  image has OpenMM only). Built by the `fep_bake` task.
- **Alchemical-lane env vars the firm/fanout pipelines set** (in `nrv04_vast_launch.py` firm preamble +
  Dockerfile): `OPENMM_PLUGIN_DIR=/opt/mamba/envs/rbfe/lib/plugins` (conda-pack relocation breaks OpenMM plugin
  auto-load → OpenFE's internal `getPlatformByName("CUDA")` fails without it); `SSL_CERT_FILE=/etc/ssl/certs/
  ca-certificates.crt` (else RCSB fetches `CERTIFICATE_VERIFY_FAILED`); a runtime ceiling ≥4 h (a real HREX leg
  runs ~3 h on one 4090 — don't reap mid-run).
- **Spot-restart safety:** a fresh-vs-restore guard in `rbfe_spot_driver.py` clears any stale `equilibration.nc` /
  `simulation.nc` that `restore()` rejected, preventing the `Storage file … already exists` crash on resume.
- **Tooling:** `nrv04_vast_launch.py` modes — `probe_offers` (live per-card $/hr), `bench`/`bench_grid`
  (throughput → `$/ns`), `firm`/`firm_collect` (real RBFE/ternary edge timing). All driven by
  `fusion-cpu-extras.yml` (`task=nrv04_vast_launch`).

---

*Maintenance: when a `firm`/`bench` run completes, update the matching row here (MEASURING → MEASURED, with the
run id + the realized number) and reconcile the nr4a3-program-map.md economics summary to it.*

---

## Appendix T — the throughput table's re-anchoring (2026-07-27)

*Corrections live here, not inline. The live text above carries only current values.*

**What changed.** `vast_cost_model.MEASURED_NS_PER_DAY_84K` was re-measured onto a single estimator — the
**median over N ≥ 3 independent hosts**, all on the anchors' own protocol (`gpu_md_bench.py`, 84,534-particle
TIP3P/PME box, 4 fs HMR, CUDA, 3 timed blocks ≈ 60 s) and all through `vast_bench_sweep.py`'s admission gate.

| card | retired | current | estimator |
|---|---|---|---|
| RTX 4090 (reference) | 755.36 *(retired)* | **804.06** | median of 6 hosts |
| RTX 4080 | 703.51 *(retired)* | **693.35** | median of 4 hosts |
| RTX 3090 | 359.36 *(retired)* | **460.91** | median of 3 hosts |

`REFERENCE_NS_PER_H` is derived from the reference card's entry, so it moves with it: **31.473 → 33.503
ns/reference-GPU-hour**. Six cards benched earlier the same day as *single hosts* (RTX 5090, RTX 5080,
RTX PRO 4000, RTX 3090 Ti, RTX 5060 Ti, RTX A4000) were re-measured onto the same estimator in the same pass;
their single-host values are registered in [`pinned-figures.json`](../manuscripts/pinned-figures.json).

**Why — two independent causes, and the second is larger for one card.**

1. **The old figures were not the same statistic.** Each was ONE host. Measured host spread on the identical
   protocol: RTX 5080 **14 %**, RTX 3090 **9.5 %**, RTX 4090 **4.1 %**, RTX 4080 **4.0 %**. By accident the old
   RTX 4080 host sat within 0.3 % of the best of four while the old RTX 4090 host sat 6.7 % below the best of
   five — so every card *ratio* carried that sampling difference. The retired table said 4090/4080 = 1.074;
   the median-of-N measurement says **1.160**.
2. **They measured a stack we no longer run.** The retired figures come from the conda-pack'd `md`
   environment; the current ones from the `nr4a3fep` image's `rbfe` environment, which is what the production
   lanes execute. The gap is **not uniform** (RTX 4080 ≈ unchanged, RTX 4090 +6 %, RTX 3090 **+28 %**), so it
   is not a scale factor and cannot be corrected for. A bench must measure the CUDA/OpenMM build the science
   runs on, or its ns/day prices a stack nobody uses.

**Two entries are honestly under-sampled** and say so in the table itself: **A100 PCIe** (1 host) and
**RTX 3090 Ti** (2 hosts) — the board carried only two qualifying offers of each. An under-sampled entry errs
conservatively: every rental confounder is one-sided downward, so it understates throughput and therefore
*overstates* `$/ns`, and we under-buy rather than over-buy.

**What this does NOT license.** It is not a claim that ~804 is the RTX 4090's peak. A median is deliberately
not a maximum: a max over hosts ratchets upward with every host added and drifts anti-conservative. It is the
throughput of a *typical healthy rental*, which is the quantity the `$/ns` ranking actually needs.

**How the loss of the original evidence was found.** The disagreement surfaced as an S3 bench record reading
726.79 ns/day against the then-anchor's 755.36. Those were never two readings of one object:
`nrv04_vast_launch.bench()` names its result by a **deterministic** key, so a re-run overwrote the validated
2026-07-24 grid's raw artifacts in place. The grid's per-block values survive only because they were copied
into [`throughput-bench-provenance.json`](../modalities/throughput-bench-provenance.json). `vast_bench_sweep`
scopes every result key by wave and replicate for exactly this reason.

**Reproduce:** `vast-bench-sweep.yml` → `mode=launch` (`replicates≥3`, `include_measured=1`, a fresh `wave`),
then `mode=collect` (prints the per-card host distribution and the estimator), then `mode=ladder` (regenerates
[`vast-ladder-repricing.json`](../modalities/vast-ladder-repricing.json) from a fresh market snapshot).
Total GPU cost of the re-anchoring: **≈$1.74**.

---

## Appendix U — the buy line re-expressed (2026-07-27)

*Corrections live here, not inline.*

**What changed, and what did not.** Nothing about the spending decision. The line trimcrae approved is an
absolute rate — **`$0.006539` per nanosecond** — and it is unchanged. Only its *expression* moved, because the
denominator it was written against was corrected:

| | basis `$/ns` | line as a multiple | line as an absolute rate |
|---|---|---|---|
| as ruled, morning of 2026-07-27 | 0.004359 *(superseded)* | 1.5× *(superseded)* | **$0.006539/ns** |
| after the throughput re-anchoring | **0.003412** | **≈1.92×** | **$0.006539/ns** |

**Why the basis fell 22 %, decomposed** (same offers file, so the market is held constant except where noted):

| factor | effect on basis | detail |
|---|---|---|
| market snapshot moved | ×1.039 | plan rate $0.1372 → $0.1426/ref-GPU-h on the newer board |
| **throughput table widened** | **×0.802** | plan rate $0.1426 → $0.1143 — gradeable offers went **132 → 229**, and newly-priceable cheap supply entered the best-10 mean (mix went `{3090×5, 4090×5}` → `{3090×5, RTX PRO 4000×3, 5090×1, 4090×1}`) |
| reference anchor re-measured | ×0.939 | `REFERENCE_NS_PER_H` 31.473 → 33.503 |
| **net** | **×0.783** | the superseded $0.004359 → $0.003412/ns |

**The reference CARD did not change** — it is still the RTX 4090. The anchor correction accounts for only
**6.1 %** of the 22 %; the dominant term is that the widened table let the planning rate see supply it
previously could not price. The basis is defined as the best-10 mean `$/reference-GPU-hour`, i.e. *what a
policy that always takes a top-10 offer achieves* — a measure of purchasing **capability**, not of prices. So
it fell for a real reason: we can now buy things we previously could not grade.

**The consequence, stated plainly so nobody has to infer it.** Because the basis is the denominator, a smaller
basis makes every multiple LARGER. Expressed as a multiple, the line therefore had to move from 1.5× to ≈1.92×
*to stay the same rule*. Had it been left at 1.5×, the approved rate would have silently tightened by 22 % and
every board seen that day would have failed a line it had been passing.

**The trap this creates, and how it is closed.** §1's threshold is both the buy line and the ⚠ DRIFT reporting
flag, and trimcrae's earlier ruling is that they are the same number (*"Why are there so many high `$/ns` rows
that are flagged but you're still paying for them?"*). If the buy line moved to ≈1.92× and the flag stayed at
1.5×, rows would print ⚠ DRIFT **and be bought** — the original complaint, recreated by the fix. Both now read
one derived value, and [`tests/test_buy_line_invariant.py`](../modalities/tests/test_buy_line_invariant.py)
sweeps the rate axis across the line and fails if the flag and the refusal ever disagree at any point.

**The effect, on the board of 2026-07-27 (339 offers, 18 viable fan-out units).** This is the number that
shows the re-expression preserved trimcrae's intent rather than changing it:

| ceiling used | units placeable | fleet mean `$/ns` of the placed units |
|---|---|---|
| **re-expressed line** (`$0.006539/ns` = the approved rate) | **18 / 18** | 0.004560 |
| if `1.5×` had been left typed against the new basis | 9 / 18 | 0.003810 |

Leaving the multiple typed would have halved the tranche the same authorisation was meant to buy. **valB's
4-leg replicate pair clears both ceilings** — best board rate `$0.002012/ns` (0.59× basis) against the 1.92×
rate line, and a projected `$4.31` against the rung's `$20.74` dollar ceiling.

*(18, not 19: `cw_bio_nmethyl_amide` — a methyl ester → N-methyl amide O→N substitution — is permanently
BLOCKED because no available mapper maps it above the 20-atom provable floor.)*

**Where the invariant lives:** [`inflight_usd_per_ns.APPROVED_USD_PER_NS`](../modalities/inflight_usd_per_ns.py)
(the absolute rate, derived from the two constants that defined it at the moment of the ruling) and
`drift_multiple()` (the multiple, derived against the current basis). `congeneric_fanout`,
`relaunch_market_gate` and `ternary_vast_launch` all import it rather than carrying a copy. **A future basis
correction re-derives the multiple instead of silently changing the rule — which is the entire point.**
