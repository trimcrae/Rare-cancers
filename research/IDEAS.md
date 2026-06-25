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
| **B7-H3 (CD276) → ADC / bispecific / CAR-T** | **Promoted — surrogate expression now supports it.** In-silico: **CD276 expressed in 99% of sarcoma lines, high across *every* subtype incl. myxoid** (`depmap-insilico-findings.md`), on top of 97% pan-STS IHC. ADC ifinatamab deruxtecan / CC-3 bispecific / B7-H3 CAR-T ready. A *surface* target (unlike the intracellular fusion/CTAs). | ★ Confirm in EMC tissue / public proteomics (HPA) — expression prior is now favourable, not a coin-flip. If +, ADC is fastest; CAR-T = Phase-3 route. |
| **FAP-targeted radioligand therapy (FAPI-RLT)** | **Emerging, plausible.** ⁹⁰Y/¹⁷⁷Lu/²²⁵Ac-FAPI controlled disease in ~half of advanced-sarcoma pts; EMC's myxoid stroma is likely FAP⁺. Tracer is also diagnostic (FAP-PET). `emerging-modalities-scan-emc.md` §2. | ★ Confirm EMC FAP-PET avidity/expression; if avid, off-the-shelf theranostic via RLT programs. |
| **PPARG downstream-effector (repurpose TZDs)** | **Novel, speculative, druggable.** The fusion *transactivates PPARG* (a druggable NR with approved agonists). Attack the pathway where it's tractable, not the undruggable TF. `emerging-modalities-scan-emc.md` §4. | ★ Pull EMC PPARG-axis + TZD-in-sarcoma data; resolve agonism-vs-antagonism direction before weighting. |
| **CAR-T for EMC** | **Hard but not closed.** Driver is nuclear (no surface target) + cold myxoid stroma. Surface options: B7-H3 (lead), **CD56/NCAM** (EMC NE-phenotype angle), FAP (anti-stroma), GD2/HER2 (fallback). Among surface modalities, ADC/FAPI-RLT likely beat CAR-T to a patient; CAR-T is the higher-ceiling follow-on. `car-t-strategies-emc.md`. | ★ EMC B7-H3 + CD56 IHC; ★ **surfaceome screen** of the fusion's transcriptional output to find an EMC-enriched surface target. Constructs: CAR-T **+ TKI** (crack cold TME), armored/IL-12, SynNotch/dual (B7-H3∧CD56) logic gate, **allogeneic** (rare-disease economics). |
| **TCR-T / engineered T cells vs a cancer-testis antigen (synovial-sarcoma port)** | **DOWNGRADED to weak (gating fact resolved, mostly negative).** EMC is CTA-low: NY-ESO-1 rare (used to tell myxoid liposarcoma *apart from* EMC), PRAME ~8% in chondrosarcoma, MAGE-A4 not reported high. afami-cel/letetresgene don't port. `immunotherapy-options-emc.md` §1. | ★ Only remaining door (low prior): a dedicated **EMC MAGE-A4/PRAME IHC series** × HLA-A\*02:01 carrier freq (computable via `hla_coverage.py`) — a cheap confirm/kill for a single-digit-% subset, not a lead. |
| **Degrader — NR4A3-LBD PROTAC** | **LEADING driver-directed route; premise in-silico-supported.** Orthosteric LBD pocket is borderline-druggable (fpocket 0.495, residues 406–534) and carries all 7 selectivity handles — druggability and selectivity coincide. *(A 2026-06-25 claim that this pocket was ~0.026 was a self-inflicted enumeration bug, retracted same day; regeneration from the count-fixed pipeline reconfirms 0.495 — see `emc-treatment-strategy.md` feasibility check + `modalities/ASSUMPTIONS.md`.)* Degradation is *mechanistically ideal* (NOR-1 activity scales with expression level). **Fusion-addiction premise supported by analogy: FLI1 in Ewing = −0.93 gene effect, 74% dependent → FET-fusion sarcomas are fusion-addicted, so degrading EWSR1::NR4A3 should be lethal** (`depmap-insilico-findings.md`). NR4A3-specific warhead starting points exist (inverse NOR-1 agonists, Munck 2022); NR4A1 PROTAC works but doesn't cross-degrade NR4A3. Design spec: `nr4a3-degrader-design-spec.md`. | ★ **Make-or-break:** per-frame fpocket druggability over the cryptic-pocket MD — does the borderline 0.495 orthosteric pocket reach ≥0.5? ★ **CPU-now:** dock NOR-1 inverse agonists into the orthosteric pocket + enumerate Pocket-5 residues. ★ **AI:** de-novo binder design for a selective warhead. Publish the addiction-analogy + designed warhead together; dTAG test = what the paper asks others to run. |
| **PRAME-directed (brenetafusp ImmTAC / PRAME CAR-TCR)** | **NEW antigen-directed lead — best of the CTAs.** In-silico: PRAME expressed in **53% of sarcoma lines, HIGH in myxoid (7.6) & synovial (7.2)** — EMC is myxoid-class (`depmap-insilico-findings.md`). brenetafusp runs a tumour-agnostic basket → access without a bespoke product. Beats MAGE-A4/NY-ESO-1 (both confirmed low). | ★ Confirm PRAME in EMC tissue / public proteomics (cell-line CTA reads are lower bounds). If +, brenetafusp basket eligibility (PRAME⁺/HLA-A\*02⁺). |
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

## Cross-cutting strategy: broaden any promising candidate to OTHER (esp. common) cancers

**The motivation problem (user insight, 2026-06-22).** Even a genuinely promising EMC candidate may
not get developed — EMC is *too rare* to create commercial/translational pull on its own (the same
economics that sank the vaccine route). A convincing paper about an EMC-only drug is necessary but
may not be *sufficient* to make someone actually build it.

**The fix.** For any candidate that firms up, also assess and write up **which other cancers its
mechanism/target fits — prioritising common cancers and those with poor existing treatments / high
unmet need.** Positioning EMC as the *entry* indication of a broader oncology opportunity widens the
addressable market and gives a developer a real reason to act. (EMC's clean, single-driver biology
also makes it a good *proof-of-concept* indication for a mechanism that then scales to messier common
tumours.)

**This is cheap to do in-silico with what we already built** — our DepMap pipeline already covers
**all lineages, not just sarcoma**, so a pan-cancer expression/dependency readout is a one-flag
extension:
- **NR4A3 / NR4A degrader:** NR4A receptors (NR4A1/2/3) are implicated across leukemia, melanoma,
  prostate, breast, colorectal, etc.; a degrader/the "degrade an undruggable nuclear-receptor TF via
  its LBD" *platform* may generalise. ★ pull pan-cancer NR4A expression + any NR4A dependency from
  DepMap.
- **B7-H3, PRAME, FAP** are already **pan-cancer targets** (B7-H3 ADC in lung/prostate; PRAME in
  melanoma/lung/ovarian/uterine; FAP pan-tumor) — frame EMC as one indication in a broader program;
  ★ pan-cancer expression is already computable with `depmap_target_expression.py` (drop the
  sarcoma-only filter).
- **Repurposed drugs** (trabectedin, carfilzomib, TKI+ICI) already have other-cancer footprints —
  cite them.

**When to do it:** only once a candidate is concrete (don't pre-spread effort). The deliverable is a
"broader-indication" section appended to that candidate's write-up: which cancers share the
target/mechanism, their unmet need, and the supporting public-data evidence. Add it to the
`emc-treatment-roadmap.md` discussion when the lead candidate is chosen.

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
