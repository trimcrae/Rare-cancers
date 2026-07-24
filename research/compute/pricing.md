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
| **Alchemical ternary cooperativity edge** (3-replica, ~146,509 particles, 16 windows) | **INTERIM ~$3–6 on Vast 4090** for the full 3-replica edge (~$1–2/replicate) — being replaced by a DIRECT 4090 measurement (in flight). Interim = L4 leg (~8.7 GPU-h) ÷ ~2.3 card ratio → ~23 4090-GPU-h. | **MEASURING** (direct Vast-4090 firm ternary in flight; interim from L4) | **Interim** from the parallel `valB_mini` on **GCP L4** (`gpu-ternary-fep-gcp.yml`): live sampler `total wall clock 8:40:29` per leg (~920 iters × ~33 s) = ~8.7 L4-GPU-h/leg; edge = binary+ternary × 3 replicas ≈ ~52 L4-GPU-h; ÷ a spec-based ~2.3× L4→4090 ratio (the soft spot). **Direct 4090 measurement now in flight** — firm ternary on the Vast rtx4090 nr4a3fep image (fusion-cpu-extras `firm firm_kind=ternary`), self-stages the 8G1Q system; the `equilibration.nc` spot-restart collision that blocked it earlier is now FIXED (`rbfe_spot_driver.py`). System size **146,509 particles CONFIRMED**. Old ~$65–110 (scaled off the refuted 55-GPU-h RBFE anchor) is superseded. **L4-on-demand (~$37) is NOT a go-forward cost — Vast only.** |
| **Co-fold / docking** (basin nomination) | **~$0–50, cheap** (CPU docking + short Boltz/AF3 co-fold inference) | **ESTIMATED** (known-cheap class) | prior smina/Vina warhead screen + NR-V04 Boltz co-folds; CPU or short GPU. Weak/biased predictor — used to *nominate*, never to kill a small wedge |

**Two facts that make B the whole story:**
1. **Alchemical stages (RBFE, ternary, mutation-cycle, local FEP) all reduce to the RBFE-edge and ternary-edge
   bases** — a protein-mutation FEP (`ΔG_mut^ternary − ΔG_mut^binary`) is the same OpenFE alchemical machinery, so
   it is priced per (binary edge + ternary edge), NOT a separate test.
2. **Endpoint-MD stages (covalent panel, ensemble/CRL refinement MD) reduce to the endpoint-MD basis** — same
   engine, scaled by system size.

So the *only* cost bases that need real GPU tests are the four above; **RBFE and ternary edges are being measured
this session**, and everything else is either MEASURED or a cheap-and-known class.

---

## C. STAGE COSTS — each = a cost basis × a count

| Stage | = basis × count | cost (Vast 4090) | status |
|---|---|---|---|
| RUNG 0 (charge fix, EMC E3, pocket) | CPU/CI | **~$0** | MEASURED (done) |
| `valA_mini` (TYK2 build-consistency) | 1 RBFE edge (reduced) | **~$0–15** | MEASURED (done, GCP L4) |
| `step0` RBFE shakeout | infra | **~$1–2** | MEASURED (done) |
| `step1_pilot` cmpd19 | 1–2 RBFE edges | **~$1–3** (Vast 4090; ran Modal L4) | MEASURED-derived |
| `step1_fanout` cmpd19 map | **19 RBFE edges** (~5–6 GPU-h ea) | **~$12–26** | **MEASURED-derived** (from the ~3.6-GPU-h complex leg) |
| `valB_mini` ternary | 1 ternary edge | **~$3–6 Vast 4090** (~$37 as-run on L4 on-demand) | **MEASURED** (~52 L4-GPU-h) |
| `valB_full` ternary cube | 2–3 ternary edges + CRL-MD module | **~$20–60 Vast 4090** | MEASURED-derived |
| `nrv04_feasibility_covalent` | 18 endpoint-MD legs | **~$8** | MEASURED |
| `nrv04_retrospective` | NR4A1/2/3 ternary ensembles | **~$25–55** (swing: ensemble-MD leg count) | MEASURED-derived |
| **5a-KS kill-switch decision** (atlas + basin + 1 mutation direction) | $0 + $0–50 + 1 alchemical direction (binary+ternary ~$5–10) | **~$5–60** | MEASURED-derived |
| full reciprocal mutation cycle (3→1 + 3→2 + 1/2→3) | ~3 alchemical directions | **~$15–30** | MEASURED-derived (RBFE+ternary basis) |
| ensemble refinement / CRL MD | endpoint MD, dozens–~200 legs | **~$20–150** | MEASURED-derived (swing item) |
| local within-basin FEP | 3–6 ternary edges | **~$9–36** | MEASURED-derived |
| `ternary_prospective_matrix` (now 5a–5d ladder) | ~4–12 constructs via 5c/5d | **folded into 5c+5d above** | MEASURED-derived |

**★ Whole gated ladder ≈ ~$270 mid-range (~$150–450), Vast 4090, GO at every gate** (optional/HELD ΔG_open + ABFE
excluded, ~$200–500 more). Now that every base is measured, the ladder totals cleanly. The RBFE side is
**settled and cheap**: the measured Vast-4090 edge (~5–6 GPU-h ≈ ~$0.6–1.4) is right in line with what the old
$840 schedule assumed per edge (5–15 GPU-h), and Vast is ~2–3× cheaper/GPU-h than AWS g5, so **RBFE stages are a
few tens of dollars, not hundreds** (`step1_fanout` ≈ ~$12–26); the ternary is measured too (~$3–6/edge). The only
real swing left is the **ensemble-MD leg count** (5c refinement + the retrospective) — not the per-edge cost.
Price and gate each rung individually at its gate; the kill-switch stops most NO-GO paths under ~$150.

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
- **Ternary edge — MEASURED from the PARALLEL real benchmark (2026-07-24).** The `valB_mini` Wurz cmpd1→cmpd4
  cooperativity FEP ran for real on GCP L4 (`gpu-ternary-fep-gcp.yml`, branch `claude/rung-2-parallel-7asnpk`,
  detached on-demand VM tailed hourly). The live OpenFE sampler gives **~8.7 GPU-h per alchemical leg** (146,509
  particles, 16 windows, ~33 s/iter × 920 iters; `total wall clock time 8:40:29`). Edge = binary + ternary leg;
  `min_replicas_per_leg=3` (prereg) → full 3-replica edge ≈ **~52 L4-GPU-h ≈ ~23 4090-GPU-h**. Cost: **~$3–6 Vast
  4090**, ~$13 L4-spot, **~$37 L4-on-demand** — provider/card dominates because the edge is GPU-h-heavy. The
  4090 figure uses a spec-based ~2.3× L4→4090 MD ratio (no same-system bench yet — the one soft spot; a Vast-4090
  ternary firm leg would harden it, but the L4-GPU-h itself is a hard measurement). A duplicate firm ternary was
  launched then **stopped** once this was confirmed — **compute not wasted.** The NR-V04 "NR4A1 degrader" sims are
  the **covalent panel = endpoint MD** (celastrol is covalent), feeding the endpoint-MD basis, not this one.
- **De-anchored AWS RBFE baseline** — `research/modalities/nr4a3-post-pilot-sequence.md` (2026-07-13) +
  `sm_gpu_util.py` (live CloudWatch GPU-util probe). Kept only as historical context; **not** the Vast number.
- **Design/count sources (unpinned)** — `research/modalities/congeneric-rbfe-map.json` (19 RBFE edges,
  `est_gpu_h: null`); the prospective-matrix + mutation-cycle counts in `STRATEGY.md`.

---

*Maintenance: when a `firm`/`bench` run completes, update the matching row here (MEASURING → MEASURED, with the
run id + the realized number) and reconcile the STRATEGY.md economics block to it.*
