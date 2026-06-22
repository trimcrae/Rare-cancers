# EMC treatment tracker + parked-ideas backlog

**This file's main content is the EMC treatment-discovery route board below — the repo's crux**
(paired with the `emc-treatment-strategy.md` capstone). Genuinely *parked* side-ideas (not the
treatment routes) live further down under "Parked ideas". Add to this rather than losing ideas in
chat; keep the board current as candidates move.

---

## EMC treatment-discovery — route status board (updated 2026-06-21)

**Start with `research/manuscripts/emc-treatment-strategy.md`** — the capstone that ranks every
route into a prioritized portfolio (per-route detail in the other memos; the synth-lethal-vs-
degrader head-to-head is `degrader-vs-synthetic-lethal.md`). This board is the one-screen summary
of what's shelved vs. active and the next step for each. The goal pivoted away from the vaccine/coverage work (rigorous but unlikely to
*yield a treatment*; economics favour a tumour-agnostic platform we don't control) toward routes
that could actually drug or immuno-target EWSR1::NR4A3 EMC.

**No wet lab — read next-steps through that lens.** Our two levers are (1) **publish-to-convince**
(make the case so a lab/clinician runs it) and (2) **in-silico evaluation** (★ items we can run
ourselves — design, modelling, public-data mining — now or with near-future virtual-cell/
perturbation models). Wet-lab items in the table (dTAG, IHC, CRISPR screen) are **not our to-do** —
they're what a convincing paper should get *others* to do, or what we replace with an in-silico
proxy. See `emc-treatment-strategy.md` → "two paths" + "in-silico work program".

| Route | Status | Next step (★ = computational, no wet lab) |
|---|---|---|
| **Checkpoint inhibitor + anti-angiogenic TKI combination** | **TOP NEAR-TERM LEAD (best EMC evidence).** ImmunoSarc (sunitinib+nivolumab) had an actual **EMC partial responder**; mechanistically the TKI remodels the cold TME (cold→hot) and EMC is already TKI-sensitive — synergy, not coincidence. All drugs approved. See `immunotherapy-options-emc.md` §2. | ★ Grade the EMC IO/TKI response evidence into a table; pick the best TKI+ICI pairing (pazopanib/sunitinib/anlotinib/regorafenib + anti-PD-1). Vehicle = sarcoma/basket trial. |
| **Trabectedin (± RT or combo)** | **NEAR-TERM LEAD (approved, mechanism-fit).** Displaces fusion-TFs from target promoters (its MoA in myxoid liposarcoma); EMC is the same class and has a reported **impressive EMC responder**. `emerging-modalities-scan-emc.md` §1. | ★ Curate EMC trabectedin response evidence; consider rational trabectedin + TKI/IO combos (non-overlapping mechanisms). |
| **Carfilzomib ± anthracycline (± venetoclax)** | **NEAR-TERM LEAD — best *ex-vivo EMC* evidence.** Only 1/17 drugs with high sensitivity across **2 patient-derived EMC models**, with carfilzomib+doxorubicin/+venetoclax synergy (Bangerter 2023). Already in the repurposing track. | ★ Preclinical confirmation → combination arm on EMC's anthracycline backbone. See `repurposing-hypotheses.md`. |
| **B7-H3 (CD276) → ADC / bispecific / CAR-T** | **Emerging, broadly applicable — gated by one cheap check.** B7-H3 expressed in 97% of STS (69% high); ADC ifinatamab deruxtecan, CC-3 bispecific, B7-H3 CAR-T all ready. A *surface* target (unlike the intracellular fusion/CTAs). `emerging-modalities-scan-emc.md` §3. | ★ **EMC-specific B7-H3 IHC** = the single confirm/kill that opens 3 modalities. If +, ADC is fastest; CAR-T = the Phase-3 route. |
| **FAP-targeted radioligand therapy (FAPI-RLT)** | **Emerging, plausible.** ⁹⁰Y/¹⁷⁷Lu/²²⁵Ac-FAPI controlled disease in ~half of advanced-sarcoma pts; EMC's myxoid stroma is likely FAP⁺. Tracer is also diagnostic (FAP-PET). `emerging-modalities-scan-emc.md` §2. | ★ Confirm EMC FAP-PET avidity/expression; if avid, off-the-shelf theranostic via RLT programs. |
| **PPARG downstream-effector (repurpose TZDs)** | **Novel, speculative, druggable.** The fusion *transactivates PPARG* (a druggable NR with approved agonists). Attack the pathway where it's tractable, not the undruggable TF. `emerging-modalities-scan-emc.md` §4. | ★ Pull EMC PPARG-axis + TZD-in-sarcoma data; resolve agonism-vs-antagonism direction before weighting. |
| **CAR-T for EMC** | **Hard but not closed.** Driver is nuclear (no surface target) + cold myxoid stroma. Surface options: B7-H3 (lead), **CD56/NCAM** (EMC NE-phenotype angle), FAP (anti-stroma), GD2/HER2 (fallback). Among surface modalities, ADC/FAPI-RLT likely beat CAR-T to a patient; CAR-T is the higher-ceiling follow-on. `car-t-strategies-emc.md`. | ★ EMC B7-H3 + CD56 IHC; ★ **surfaceome screen** of the fusion's transcriptional output to find an EMC-enriched surface target. Constructs: CAR-T **+ TKI** (crack cold TME), armored/IL-12, SynNotch/dual (B7-H3∧CD56) logic gate, **allogeneic** (rare-disease economics). |
| **TCR-T / engineered T cells vs a cancer-testis antigen (synovial-sarcoma port)** | **DOWNGRADED to weak (gating fact resolved, mostly negative).** EMC is CTA-low: NY-ESO-1 rare (used to tell myxoid liposarcoma *apart from* EMC), PRAME ~8% in chondrosarcoma, MAGE-A4 not reported high. afami-cel/letetresgene don't port. `immunotherapy-options-emc.md` §1. | ★ Only remaining door (low prior): a dedicated **EMC MAGE-A4/PRAME IHC series** × HLA-A\*02:01 carrier freq (computable via `hla_coverage.py`) — a cheap confirm/kill for a single-digit-% subset, not a lead. |
| **Degrader — NR4A3-LBD PROTAC** | **LEADING small-molecule route, and stronger than first thought.** Degradation is *mechanistically ideal*: NOR-1 is constitutively active and activity scales with expression level, so lowering protein lowers oncogenic output. NR4A3-*specific* warhead starting points exist (fragment-derived **inverse NOR-1 agonists**, low-µM; Munck 2022). An NR4A1 PROTAC works but doesn't cross-degrade NR4A3 → need an NR4A3 warhead. Fusion retains the ordered LBD; first approved PROTAC (vepdegestrant 2025) degrades an NR. `immunotherapy`/`degrader-vs-synthetic-lethal.md` §1. | ★ Map NR4A-ligand contacts onto fpocket Pocket-5 (406–534); ★ confirm CRBN/VHL expression (ubiquitous → high prior). **AI accelerator:** de-novo binder design (RFdiffusion/AF) to mature the inverse-agonist hit into a selective warhead. Wet-lab gate: dTAG fusion-addiction test. |
| **ImmTAC / soluble-TCR bispecific (off-the-shelf)** | **Weak — same antigen gate as TCR-T.** Targets a peptide-HLA (PRAME/MAGE-A4 on HLA-A\*02); EMC is PRAME-/MAGE-A4-low. `immunotherapy-options-emc.md` §2b. | One thread: **brenetafusp (PRAME ImmTAC) runs a tumour-agnostic basket** → a PRAME⁺/A\*02⁺ EMC patient could enrol without a bespoke product (small prior). EMC-specific = fusion-junction-pHLA ImmTAC (hard, same weak-junction problem). |
| **Synthetic-lethal (BRD9/ncBAF via EWSR1-prion→BAF)** | **DOWNGRADED.** DepMap 24Q4 transfer prior **negative**: BRD9 not a sarcoma dependency, not even in Ewing; BET/CDK pan-essential, no selectivity window (`depmap-sarcoma-dependency.json`). | No cheap shortcut; needs a **de-novo CRISPR screen in patient-derived EMC lines**. Don't spend a wet-lab slot on a transfer-justified BRD9 test. |
| **AF3 on a druggable interface** | Deferred; method not strategy. | ★ Only once the degrader route picks a ternary/PPI interface (fusion↔CBP/p300 or fusion↔E3). |
| **Fusion-junction ASO** (`novel-modalities.md` §3.2) | Designed; 5 gapmers exist. | GC-rich (75–81%) + tumour delivery unsolved. |
| **Vaccine / HLA-coverage paper** | **PARKED** (done, not a treatment path; self-adjacent junction in a cold tumour = weak immunogen). `hla-coverage-emc.md`. | Never built: (a) reality filters (distance-to-self/tolerance + anchor-vs-TCR position); (b) breakpoint-recurrence quant. `coverage_scan.py` §3.3 numbers + `coverage-curve.png` await a `modalities-cache` snapshot. **Reusable:** its HLA-A\*02 coverage feeds TCR-T eligibility above. |

**Shared rate-limiter for every route:** EMC is nearly absent from public functional-genomics data
(only new patient-derived lines: NCC-EMC1-C1 2025; USZ-EMC). The decisive experiment of *every*
route needs those lines — that bottleneck, not idea-generation, is the real constraint.

**Speculative / forward-looking (AI-era), kept honest:** de-novo binder/TCR design (diffusion
models) to manufacture the warhead or TCR a route lacks; AI structure (AF3) for ternary/PPI
interfaces; combination therapy (anti-angiogenic TKI — EMC's one real clinical signal — + IO).
Lower-credibility for *near* term: CAR-T (no good EMC surface antigen), ADCs (ditto), "nanobots"
(not a near-term clinical reality). Don't over-invest in these until a concrete target is in hand.

---

# Parked ideas (side-projects, not EMC treatment routes)

## Modernize & help maintain the TxGNN repo (upstream contribution)

**Status:** parked / idea only (filed 2026-06-20).
**Origin:** while running the real TxGNN model for EMC predictions (roadmap #3, see
`hypotheses/METHODOLOGY.md §7` and `txgnn_predict.py` / `.github/workflows/txgnn-run.yml`)
we hit the exact dependency-rot wall that limits TxGNN's reach.

### The idea
Contribute to [`mims-harvard/TxGNN`](https://github.com/mims-harvard/TxGNN): port the
2023-era stack to a modern one and/or refresh the knowledge graph, so the model is
runnable out-of-the-box in 2026+.

### Why it could be high-value
- **The dependency rot is a real, shared barrier.** TxGNN pins **DGL 0.5.2** + an old
  PyTorch; its `model.py` uses DGL 0.5.2 heterograph/message-passing APIs that broke in
  DGL 0.6→0.7→1.0→2.x. Anyone trying to run it today hits this (we did). A clean
  torch-2.x / DGL-2.x port would unblock many rare-disease researchers — high leverage
  for a small, well-scoped repo.
- **Public good aligned with this project's mission** (lower the information cost of
  repurposing for neglected diseases; see METHODOLOGY §7.4 economics).
- Candidate contributions, roughly in increasing effort:
  1. A **CPU-friendly, pinned, reproducible "run inference for one disease" recipe**
     (basically what we built in `txgnn_predict.py` + the workflow) — could be a docs PR
     or an `examples/` script. Lowest effort, immediately useful.
  2. **Dependency modernization** (torch 2.x + DGL 2.x) — non-trivial: rewrite the
     heterograph layers; the released weights are tied to the old DGL, so behavior must
     be re-validated (likely a retrain or careful weight port).
  3. **Refreshed knowledge graph** (newer PrimeKG / MONDO / DrugBank) — bigger, would
     change predictions, needs re-training and re-benchmarking.

### Effort / risk
- (1) is small and self-contained. (2) and (3) are real research-engineering projects
  (weeks), and a faithful port must preserve or transparently re-validate model behavior,
  or it's no longer "the published TxGNN."

### Open questions — check these BEFORE investing
- **Does the maintainer accept/merge PRs?** Check recent commit date, open/merged PR
  activity, issue responsiveness, and whether a `CONTRIBUTING` exists. As of this note the
  repo looks publication-frozen (README still pins DGL 0.5.2; PyPI `TxGNN` at 0.0.3), so
  confirm it isn't effectively archived before sinking effort. (Our GitHub tooling is
  scoped to `trimcrae/rare-cancers`, so this needs a manual look or a widened scope.)
- Is there an **official successor / maintained fork** already (e.g., a newer Zitnik-lab
  release, or PrimeKG v2 tooling) that's the better contribution target?
- Would a **lightweight standalone "txgnn-runner"** (our pinned wrapper, published
  separately) deliver most of the value (1) without needing upstream buy-in?

### Pointers
- Repo: https://github.com/mims-harvard/TxGNN · Explorer: http://txgnn.org
- Paper: Huang et al., *A foundation model for clinician-centered drug repurposing*,
  Nat Med 2024 (doi:10.1038/s41591-024-03233-x).
- KG on Harvard Dataverse: doi:10.7910/DVN/IXA7BM.
- Our working runner: `research/hypotheses/txgnn_predict.py` + `txgnn-run.yml`.
