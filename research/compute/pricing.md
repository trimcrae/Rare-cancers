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

| Card | $/hr (interruptible) | Source |
|---|---|---|
| **RTX 4090** | **~$0.145 min-bid → ~$0.15–0.25 realized** (×1.5 bid) | `probe_offers` 2026-07-23 (fusion-cpu-extras `vast_launch_mode=probe_offers`, CI run 30039473430) |
| **RTX 3090** | **~$0.10–0.16 `dph_total`** | same probe + the covalent panel's realized `dph_total` ledger |

`$/ns = ($/hr) ÷ (ns_per_day ÷ 24)`. Provider/GPU are independent choices; pick by `$/ns`, not headline $/hr.

---

## B. COST BASES — the per-unit anchors everything else is priced from

| Basis | Value | Status | Justifying test / artifact |
|---|---|---|---|
| **Card decision** ($/ns per card) | **4090 wins $/ns at every size, incl. 466k covalent (2.42× the 3090)** | **MEASURED** (this session) | `gpu_md_bench` grid on Vast: 4090 = **1549 / 669 / 175.6** ns/day at 35k/85k/444k atoms; 3090 = **72.5** @444k. Single-host-per-point. Fusion-cpu-extras `bench`/`bench_grid`; results `s3://…/vast-bench-results/*/bench.json` |
| **Endpoint MD leg** (covalent, ~466k atoms) | **~$0.6/leg on 3090** (measured) → **~$0.36/leg on 4090** (from the card ratio) | **MEASURED** (3090 real; 4090 inferred) | NR-V04 covalent panel, 6 completed legs 2026-07-23, S3-persisted price ledger (`dph_total`, ~40–61 ns/day, ~2 h prod). Milestone `nrv04_feasibility_covalent` |
| **Alchemical RBFE edge** (complex+solvent, ~35k) | **$ cheap (~$5–20); real constraint is WALL — leg is ~5–40 h depending on per-window am1bcc charging** | **MEASURING** (firm run live, this session) | firm RBFE on Vast 4090 (fusion-cpu-extras `firm` `firm_kind=rbfe`, self-stages the public TYK2 valA edge). Prior AWS anchor (**de-anchored**): a 2026-07-13 A10G leg measured **30 GPU-h through 6–7 of 12 windows** → extrapolated ~55 GPU-h; that run was **~65 % GPU-idle (CPU-bottlenecked)**; see `research/modalities/nr4a3-post-pilot-sequence.md` |
| **Alchemical ternary cooperativity edge** (3-replica, ~146,509 particles, 16 windows) | **ESTIMATED ~$65–110; being measured by the REAL benchmark** | **MEASURING** (parallel session's real valB_mini) | **Priced from the parallel `valB_mini` run** — the real Wurz cmpd1→cmpd4 ternary cooperativity FEP on **GCP L4**, `gpu-ternary-fep-gcp.yml`, branch `claude/rung-2-parallel-7asnpk` (hourly, spot-resuming). Its realized GPU-h × the measured L4→4090 card ratio = the Vast-4090 ternary cost — **no separate throwaway test needed** (a duplicate firm ternary was launched then STOPPED once this was confirmed). System size **146,509 particles CONFIRMED** by the firm-run setup |
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
| `step1_pilot` cmpd19 | 1 RBFE edge | **~$15–40** | done (Modal L4) |
| `step1_fanout` cmpd19 map | **19 RBFE edges** | **~$100–380** (range = un-optimized vs charge-once-fixed) | ESTIMATED — firms from the live RBFE test |
| `valB_mini` ternary | 1 ternary edge | **~$65–110** | ESTIMATED — firms from the live ternary test |
| `valB_full` ternary | +1–2 ternary edges | **~$130–330** | ESTIMATED |
| `nrv04_feasibility_covalent` | 18 endpoint-MD legs | **~$6.5–11** | MEASURED |
| `nrv04_retrospective` | NR4A1/2/3 ternary ensembles | (several ternary edges) | ESTIMATED — dominant, count not pinned |
| **5a-KS kill-switch decision** (atlas + basin + 1 mutation direction) | $0 + $0–50 + 1 alchemical direction | **~$40–140** | ESTIMATED (alchemical direction = RBFE-basis) |
| full reciprocal mutation cycle (3→1 + 3→2 + 1/2→3) | ~3 alchemical directions | **~$100–350** | ESTIMATED (RBFE/ternary-basis) |
| ensemble refinement / CRL MD | endpoint MD, large assembly | **~$100–250** | ESTIMATED (endpoint-MD-basis) |
| local within-basin FEP | alchemical | **~$150–500** | ESTIMATED (alchemical-basis) |
| `ternary_prospective_matrix` | 6–12 ternary constructs | (basis × count) | ESTIMATED — dominant, count not pinned |

**★ DO NOT quote a single whole-program total.** Two corrections push opposite ways and cancel to an unknown:
Vast 4090 is ~2–3× cheaper per GPU-h than AWS g5 (↓), but the real per-edge GPU-h is ~5–15× what the old $840
AWS schedule implicitly assumed (↑, so $840 was itself an underestimate). The total is dominated by the
**unpinned ternary retrospective + matrix edge counts**. Price and gate each rung individually at its gate.

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
  timing anywhere — genuinely needed.** Caveat: it re-runs the (already-passed) TYK2 valA edge as a
  representative cost probe; to make it *real science + cost*, point it at a live cmpd19 `step1_fanout` edge
  (needs a go + S3 pose staging).
- **Ternary edge — priced from the PARALLEL real benchmark, not a throwaway.** The `valB_mini` Wurz cmpd1→cmpd4
  cooperativity FEP is already running for real on GCP L4 (`gpu-ternary-fep-gcp.yml`, branch
  `claude/rung-2-parallel-7asnpk`). Its realized GPU-h × the L4→4090 card ratio gives the Vast-4090 ternary cost.
  A duplicate firm ternary was launched then **stopped** (`firm_stop firm_kind=ternary`) once the parallel run was
  confirmed — **compute not wasted.** The NR-V04 "NR4A1 degrader" sims are the **covalent panel = endpoint MD**
  (celastrol is covalent), so they feed the endpoint-MD basis (already measured), not the alchemical ternary basis.
- **De-anchored AWS RBFE baseline** — `research/modalities/nr4a3-post-pilot-sequence.md` (2026-07-13) +
  `sm_gpu_util.py` (live CloudWatch GPU-util probe). Kept only as historical context; **not** the Vast number.
- **Design/count sources (unpinned)** — `research/modalities/congeneric-rbfe-map.json` (19 RBFE edges,
  `est_gpu_h: null`); the prospective-matrix + mutation-cycle counts in `STRATEGY.md`.

---

*Maintenance: when a `firm`/`bench` run completes, update the matching row here (MEASURING → MEASURED, with the
run id + the realized number) and reconcile the STRATEGY.md economics block to it.*
