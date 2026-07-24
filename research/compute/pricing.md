# GPU / compute PRICING — single source of truth (every number links to a justifying test)

> **This file is authoritative for "what does step X cost, and how do we know."** STRATEGY.md's economics block
> summarizes it; this file carries the evidence. **Rule: a MEASURED number (with a linked run/artifact) always
> beats an ESTIMATE.** Never quote a cost without a `status` and a `source`. The canonical RBFE map
> (`research/modalities/congeneric-rbfe-map.json`) still holds `est_gpu_h: null` and "forbids trusting stub
> GPU-hour numbers" — honor that: an extrapolation is not a measurement.

**Status legend:** `MEASURED` (a completed run on the target hardware) · `MEASURING` (a run is in flight this
session; will be updated on completion) · `ESTIMATED` (derived/extrapolated — flagged, not certified).

---

## A. Live per-card price on Vast (MEASURED)

**★ GO-FORWARD LANE (trimcrae, 2026-07-24): ALL production runs are on Vast — RTX 4090 (default, measured $/ns
winner) or RTX 3090 (fallback).** GCP L4 / SageMaker / Modal are **NOT** the cost basis going forward. Where an
estimate below still traces to an L4 run (the valB_mini ternary), it is flagged INTERIM and is being replaced by
a direct Vast-4090 measurement — **never quote the L4-on-demand figure as a go-forward cost.**

| Card | $/hr (interruptible) | Source |
|---|---|---|
| **RTX 4090** (default) | **~$0.145 min-bid → ~$0.15–0.25 realized** (×1.5 bid) | `probe_offers` 2026-07-23 (fusion-cpu-extras `vast_launch_mode=probe_offers`, CI run 30039473430) |
| **RTX 3090** (fallback) | **~$0.10–0.16 `dph_total`** | same probe + the covalent panel's realized `dph_total` ledger |

`$/ns = ($/hr) ÷ (ns_per_day ÷ 24)`. **4090 vs 3090:** the 4090 is ~2.4× faster (measured: 175.6 vs 72.5 ns/day
@444k) for only ~1.5× the $/hr → the **4090 wins $/ns at every size**, so it's the default; a compute-bound
alchemical edge on the 3090 costs roughly **~1.5–2× the 4090 $/edge** (slower, only partly offset by cheaper
$/hr). Use the 3090 only when 4090 capacity is short.

---

## B. COST BASES — the per-unit anchors everything else is priced from

| Basis | Value | Status | Justifying test / artifact |
|---|---|---|---|
| **Card decision** ($/ns per card) | **4090 wins $/ns at every size, incl. 466k covalent (2.42× the 3090)** | **MEASURED** (this session) | `gpu_md_bench` grid on Vast: 4090 = **1549 / 669 / 175.6** ns/day at 35k/85k/444k atoms; 3090 = **72.5** @444k. Single-host-per-point. Fusion-cpu-extras `bench`/`bench_grid`; results `s3://…/vast-bench-results/*/bench.json` |
| **Endpoint MD leg** (covalent, ~466k atoms) | **~$0.6/leg on 3090** (measured) → **~$0.36/leg on 4090** (from the card ratio) | **MEASURED** (3090 real; 4090 inferred) | NR-V04 covalent panel, 6 completed legs 2026-07-23, S3-persisted price ledger (`dph_total`, ~40–61 ns/day, ~2 h prod). Milestone `nrv04_feasibility_covalent` |
| **Alchemical RBFE edge** (complex+solvent, ~35k) | **complex leg ≈ ~3.6 GPU-h; edge (complex+solvent) ≈ ~5–6 GPU-h ≈ ~$0.6–1.4 on Vast 4090** | **MEASURED** (this session, Vast 4090) | **firm RBFE, live-diagnosed on instance 45654998 (2026-07-24):** OpenFE HREX complex leg (TYK2 valA, 12 λ-windows, 5 ns production) ran at **~5.2 s/iter × 2000 production iters = ~2 h52 m sampler**, + ~43 min boot/setup → **~3.6 GPU-h billed** at the instance's **$0.122/hr** (~$0.44). Solvent leg (smaller box) extrapolated ~1.5–2 GPU-h. **The cost stands on the measured per-iteration RATE (two independent working 4090 CUDA runs: 45654998 at prod iter 92/2000, 45658414 at equil 71/400, both ~5.1 s/iter, phases advancing normally) × the hardcoded phase counts** — a clean end-to-end ΔG was NOT captured this cycle: both working spot instances were preempted before finishing the ~3 h leg, and because the firm jobspec is `resume=False` neither reached the summary step, so the S3 `firm.json` is a stale PRE-FIX attempt (CUDA-platform fail, predates the OPENMM_PLUGIN_DIR/Dockerfile fix). Getting a completed ΔG needs `resume=True` (+ the equilibration.nc-collision fix) and is a step1_fanout-execution concern, not a pricing one. **The old ~55 GPU-h AWS anchor is REFUTED for Vast, not just de-anchored:** it was a 2026-07-13 A10G leg that was **~65 % GPU-idle (CPU-bottlenecked by 12× per-window am1bcc re-charging)**; the Vast run charges once in setup and keeps the GPU busy → ~15× fewer GPU-h. See `research/modalities/nr4a3-post-pilot-sequence.md` for the pathology |
| **Alchemical ternary cooperativity edge** (3-replica, ~146,509 particles, **12** windows) | **~$7–15 on Vast 4090** for the full 3-replica edge (~$2–5/replicate). From a **projected** full L4 leg (~22 GPU-h) ÷ ~2.3 card ratio → ~57 4090-GPU-h. Direct Vast-4090 firm measurement ATTEMPTED but NaN'd at warmup (see notes). | **RATE measured (L4) → leg PROJECTED → 4090 via card ratio.** No ternary leg has ever completed. | **⚠ CORRECTED 2026-07-24 — the previous ~$3–6 was built on a PARTIAL leg.** What was measured on the parallel `valB_mini` GCP L4 run (`gpu-ternary-fep-gcp.yml`, branch `claude/rung-2-parallel-7asnpk`) is a **per-iteration rate**: `total wall clock 8:40:29` at ~920 iters × **~33 s/iter**. That 920 is **not a finished leg** — this same file (§ RBFE notes below) records that the protocol hardcodes **5 ns production at 2.5 ps/iteration = 2000 production iterations** (`nr4a3_rbfe.py:364-365`; the openmmtools `.chk` history `iters 0,20,…,2000` confirms it), plus 1 ns equilibration = 400 more. **920 iters ≈ 38 % of a 2400-iteration leg**, so "8.7 GPU-h/leg" was ~2.6× low. Projected full leg ≈ 2400 × 33 s ≈ **~22 L4-GPU-h**; edge = binary+ternary × 3 replicas ≈ **~132 L4-GPU-h** (conservative — the binary leg is a smaller box and will run faster; not yet separated); ÷ a spec-based ~2.3× L4→4090 ratio (still the soft spot). Cost: **~$7–15 Vast 4090**, ~$33 L4-spot, **~$94 L4-on-demand**. System size **146,509 particles CONFIRMED**; window count is **12**, not 16 (`gpu-ternary-fep-gcp.yml:29,70`; `git log -L 29,29` shows the default was always 12 — the code's own `N_WINDOWS` default of 16 is never used). Old ~$65–110 (scaled off the refuted 55-GPU-h RBFE anchor) remains superseded. **L4-on-demand is NOT a go-forward cost — Vast only** — but note valB_mini is *as-run* on L4 on-demand, so its real burn is ~$94/edge against the expiring GCP trial, not ~$37. |
| **Co-fold / docking** (basin nomination) | **~$0–50, cheap** (CPU docking + short Boltz/AF3 co-fold inference) | **ESTIMATED** (known-cheap class) | prior smina/Vina warhead screen + NR-V04 Boltz co-folds; CPU or short GPU. Weak/biased predictor — used to *nominate*, never to kill a small wedge |

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
   - **Consequence:** the 5a-KS kill-switch — the manuscript's designated *primary causal* result — currently has
     **no implementing engine in this repo**, so its "~$5–10 for 1 alchemical direction" line below is unfounded.
     Pricing it requires an **engine-scoping step first** (adopt a protein-mutation FEP protocol — e.g. an
     OpenFE/perses-style residue transformation, or a non-OpenFE tool — then measure one direction). Until that
     scoping is done, treat the 5a-KS row as **UNPRICED**, not cheap.
   - This compounds the *other* known 5a-KS blocker recorded in `STRATEGY.md` (RUNG 5): the wedge is the repo's
     one **cross-lane subtraction**, and the two lanes currently run **different charge models** (binary =
     am1bcc, ternary = NAGL), which must be pinned to a single `CHARGE_METHOD` before any wedge is computed.

So of the four cost bases, three (card, endpoint-MD leg, RBFE edge) are MEASURED, the ternary edge is a measured
**rate** projected to a full leg (no ternary leg has ever completed), and the mutation-cycle stages have **no
basis at all** pending engine scoping.

---

## C. STAGE COSTS — each = a cost basis × a count

| Stage | = basis × count | cost (Vast 4090) | status |
|---|---|---|---|
| RUNG 0 (charge fix, EMC E3, pocket) | CPU/CI | **~$0** | MEASURED (done) |
| `valA_mini` (TYK2 build-consistency) | 1 RBFE edge (reduced) | **~$0–15** | MEASURED (done, GCP L4) |
| `step0` RBFE shakeout | infra | **~$1–2** | MEASURED (done) |
| `step1_pilot` cmpd19 | 1–2 RBFE edges | **~$1–3** (Vast 4090; ran Modal L4) | MEASURED-derived |
| `step1_fanout` cmpd19 map | **19 RBFE edges** (~5–6 GPU-h ea) | **~$12–26** | **MEASURED-derived** (from the ~3.6-GPU-h complex leg) |
| `valB_mini` ternary | 1 ternary edge | **~$7–15 Vast 4090** (**~$94 as-run on L4 on-demand**) | **PROJECTED** from a measured rate (~132 L4-GPU-h; no leg has completed) |
| `valB_full` ternary cube | 2–3 ternary edges + CRL-MD module | **~$35–100 Vast 4090** | PROJECTED (same ternary base) |
| `nrv04_feasibility_covalent` | 18 endpoint-MD legs | **~$8** | MEASURED |
| `nrv04_retrospective` | NR4A1/2/3 ternary ensembles | **~$25–55** (swing: ensemble-MD leg count) | MEASURED-derived |
| **5a-KS kill-switch decision** (atlas + basin + 1 mutation direction) | $0 + $0–50 + **1 protein-mutation direction — NO ENGINE EXISTS** | **UNPRICED** (was "~$5–60") | **⚠ NOT DERIVABLE** — see B.3: OpenFE RHTP is ligand-only; the repo's sole protein-mutation path is MM-GBSA endpoint scoring. Needs engine scoping before any price |
| full reciprocal mutation cycle (3→1 + 3→2 + 1/2→3) | ~3 protein-mutation directions | **UNPRICED** (was "~$15–30") | **⚠ NOT DERIVABLE** — same missing engine as above |
| ensemble refinement / CRL MD | endpoint MD, dozens–~200 legs | **~$20–150** | MEASURED-derived (swing item) |
| local within-basin FEP | 3–6 ternary edges | **~$21–90** | PROJECTED (ternary base ×3–6) |
| `ternary_prospective_matrix` (now 5a–5d ladder) | ~4–12 constructs via 5c/5d | **folded into 5c+5d above** | MEASURED-derived |

**★ Whole gated ladder ≈ ~$320 mid-range (~$190–520) for the PRICEABLE stages, Vast 4090, GO at every gate**
(optional/HELD ΔG_open + ABFE excluded, ~$200–500 more; **the 5a-KS wedge and the reciprocal mutation cycle are
NOT in this total — they are UNPRICED pending engine scoping, see B.3**).

**⚠ CORRECTED 2026-07-24 — the previous line here read "Now that every base is measured, the ladder totals
cleanly." It does not, on two counts:**
- The **ternary base is a projection, not a measurement.** What was measured is a per-iteration *rate*
  (~33 s/iter on L4); no ternary leg has ever run to completion, and the previous ~$3–6/edge was built on
  920 iterations treated as a finished leg when a leg is 2400 (≈38 %). Corrected base: **~$7–15/edge** on Vast
  4090 (~$94/edge as actually run on L4 on-demand). The L4→4090 ratio (~2.3×, spec-based) is still unmeasured on
  the same system — the softest number in this file.
- The **mutation-cycle stages have no cost basis at all**, because they have no implementing engine (B.3).

What IS settled: the RBFE side. The measured Vast-4090 edge (~5–6 GPU-h ≈ ~$0.6–1.4) is in line with what the old
$840 schedule assumed per edge (5–15 GPU-h), and Vast is ~2–3× cheaper/GPU-h than AWS g5, so **RBFE stages are a
few tens of dollars, not hundreds** (`step1_fanout` ≈ ~$12–26). The remaining swings are the **ensemble-MD leg
count** (5c refinement + the retrospective), the **ternary leg length** (unconfirmed until one finishes), and the
**unscoped mutation engine**. Price and gate each rung individually at its gate.

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
  edge ≈ **~132 L4-GPU-h ≈ ~57 4090-GPU-h** (conservative: the binary leg is a smaller box and should run faster,
  not yet separated). Cost: **~$7–15 Vast 4090**, ~$33 L4-spot, **~$94 L4-on-demand** — provider/card dominates
  because the edge is GPU-h-heavy. **No ternary leg has ever completed**, so the leg length itself is unverified;
  the first completed leg should replace this projection with a measurement. The
  4090 figure uses a spec-based ~2.3× L4→4090 MD ratio (no same-system bench yet — the one soft spot; the
  L4-GPU-h itself is a hard measurement). **Direct Vast-4090 firm-ternary measurement — ATTEMPTED, blocked by a
  warmup NaN (2026-07-24).** The firm-ternary path was given the required plain-MD pre-equilibration
  (`ternary_preequil.py`, wired into `nrv04_vast_launch.py`), which ran clean (~7 min, relaxed complex overlaid)
  and got the alchemy from λ-state 0 to **state 5** before a `SimulationNaNError` at warmup — the softcore
  instability of the rough SMARCA4→SMARCA2 homology model. The proven GCP `valB_mini` lane clears this through its
  converged conditioning (it's deep in production); porting that recipe to the Vast lane is future work, so the
  ~$3–6 figure rests on the L4 measurement × card ratio. The NR-V04 "NR4A1 degrader" sims are the **covalent
  panel = endpoint MD** (celastrol is covalent), feeding the endpoint-MD basis, not this one.
- **De-anchored AWS RBFE baseline** — `research/modalities/nr4a3-post-pilot-sequence.md` (2026-07-13) +
  `sm_gpu_util.py` (live CloudWatch GPU-util probe). Kept only as historical context; **not** the Vast number.
- **Design/count sources (unpinned)** — `research/modalities/congeneric-rbfe-map.json` (19 RBFE edges,
  `est_gpu_h: null`); the prospective-matrix + mutation-cycle counts in `STRATEGY.md`.

---

## E. Operational Vast setup (bid, image, gotchas)

The go-forward lane is Vast (4090 default / 3090 fallback). The operational settings below are the hard-won
defaults; the code of record is `research/modalities/gpu_backend.py` (`VAST_BID_FLOOR_MULT`) +
`nrv04_vast_launch.py` (launch modes) + `research/compute/Dockerfile.nr4a3fep`.

- **Bid = `min_bid × 1.5`.** A margin above the market floor so the box wins AND holds its slot. **Never bid below
  `min_bid`** — a below-floor bid leaves the box created-but-stopped. On Vast you pay your bid; the multiplier
  trades a little $/hr for far fewer preemptions, which matters because the ~6 GiB image reloads in **~20 min**, so
  each preemption is expensive (a floor-hugging bid is false economy). Preemptions that still happen are absorbed
  by per-unit checkpoint + idempotent re-dispatch (resume, not restart).
- **Pin OpenMM to CUDA 12.6** + filter `cuda_max_good ≥ 12.6`. An unpinned env pulls a too-new CUDA-13+ OpenMM
  whose PTX won't JIT on any host driver (`CUDA_ERROR_UNSUPPORTED_PTX_VERSION`). Control our build, don't chase
  bleeding-edge hosts. Also filter `reliability2 ≥ 0.90`, require ≥24 GB VRAM, rank offers by `min_bid`.
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
run id + the realized number) and reconcile the STRATEGY.md economics summary to it.*
