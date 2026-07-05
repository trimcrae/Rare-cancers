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
| **Degrader — NR4A3-LBD PROTAC** | **LEADING driver-directed route; in-silico druggability case COMPLETE (2026-06-26 — gates pass).** 30 ns metadynamics: the orthosteric pocket opens to fpocket **0.931** (Gate 2) and a druggable conformation is thermally accessible at **0.76 kcal/mol** (Gate 3); calibrated D\*=0.53, static 0.495 is conservative. Handle-facing CONFIRMED (5/7 handles engageable) + warhead screen RAN (NR4A3-favoured chemotypes, margins triage-only). **Now building a FAMILY-WIDE SELECTIVITY MATRIX: same 30 ns metad on NR4A1+NR4A2 (in flight) → state-matched opened ensembles → per-candidate selectivity fingerprint (NR4A3-only / pan / anti-target NR4A1+NR4A3). Resume guide: `modalities/nr4a3-degrader-next-steps.md`.** Orthosteric LBD pocket carries all 7 selectivity handles — druggability and selectivity coincide. *(A 2026-06-25 claim that this pocket was ~0.026 was a self-inflicted enumeration bug, retracted same day; regeneration from the count-fixed pipeline reconfirms 0.495 — see `emc-treatment-strategy.md` feasibility check + `modalities/ASSUMPTIONS.md`.)* Degradation is *mechanistically ideal* (NOR-1 activity scales with expression level). **Fusion-addiction premise supported by analogy — a bet-justifying prior, NOT EMC proof: FLI1 in Ewing = −0.93 gene effect, 74% dependent → FET-fusion sarcomas are fusion-addicted, raising the prior that degrading EWSR1::NR4A3 could be lethal in EMC; the dTAG test remains the make-or-break** (`depmap-insilico-findings.md`). NR4A3-specific warhead starting points exist (inverse NOR-1 agonists, Munck 2022); NR4A1 PROTAC works but doesn't cross-degrade NR4A3. Design spec: `nr4a3-degrader-design-spec.md`. | ★ **Make-or-break: ANSWERED** — cryptic-pocket MD shows the pocket reaches druggable (0.93) at low energetic cost (Gate 3 pass). ★ **DONE:** handle-facing (run 28249776934) + warhead screen (run 28252182123). ★ **IN FLIGHT:** family-wide metad NR4A1 (28256669839) + NR4A2 (28256671172) for state-matched opened ensembles → selectivity matrix. ★ **NEXT:** dock library into all three opened pockets → selectivity fingerprint; MM-GBSA/FEP for the defensible margin; de-novo binder design (`generate_denovo` stub) for selective AND pan scaffolds; then the ternary model per paralogue. Publish the cryptic-pocket result + addiction-analogy + designed warhead together; dTAG test = what the paper asks others to run. |
| **PRAME-directed (brenetafusp ImmTAC / PRAME CAR-TCR)** | **NEW antigen-directed lead — best of the CTAs.** In-silico: PRAME expressed in **53% of sarcoma lines, HIGH in myxoid (7.6) & synovial (7.2)** — EMC is myxoid-class (`depmap-insilico-findings.md`). brenetafusp runs a tumour-agnostic basket → access without a bespoke product. Beats MAGE-A4/NY-ESO-1 (both confirmed low). | ★ Confirm PRAME in EMC tissue / public proteomics (cell-line CTA reads are lower bounds). If +, brenetafusp basket eligibility (PRAME⁺/HLA-A\*02⁺). |
| **ImmTAC / soluble-TCR bispecific (off-the-shelf)** | **Weak — same antigen gate as TCR-T.** Targets a peptide-HLA (PRAME/MAGE-A4 on HLA-A\*02); EMC is PRAME-/MAGE-A4-low. `immunotherapy-options-emc.md` §2b. | One thread: **brenetafusp (PRAME ImmTAC) runs a tumour-agnostic basket** → a PRAME⁺/A\*02⁺ EMC patient could enrol without a bespoke product (small prior). EMC-specific = fusion-junction-pHLA ImmTAC (hard, same weak-junction problem). |
| **Synthetic-lethal (BRD9/ncBAF via EWSR1-prion→BAF)** | **DOWNGRADED.** DepMap 24Q4 transfer prior **negative**: BRD9 not a sarcoma dependency, not even in Ewing; BET/CDK pan-essential, no selectivity window (`depmap-sarcoma-dependency.json`). | No cheap shortcut; needs a **de-novo CRISPR screen in patient-derived EMC lines**. Don't spend a wet-lab slot on a transfer-justified BRD9 test. |
| **AF3 on a druggable interface** | Deferred; method not strategy. | ★ Only once the degrader route picks a ternary/PPI interface (fusion↔CBP/p300 or fusion↔E3). |
| **Fusion-junction ASO / siRNA** (`manuscripts/fusion-junction-aso-paper.md`; `novel-modalities.md` §3.2) | **PRIORITY PAPER (2026-06-26) — one of the two to publish first, with the degrader.** Fusion-EXCLUSIVE (spares wild-type NR4A3, which the degrader cannot); most-likely-to-work fusion-unique route. In-silico arc complete: design → transcriptome-wide off-target → per-breakpoint favorability scan (canonical junction GC-rich/specificity-poor, but **62% of modelled breakpoints favorable**) → gap-mismatch-resolved screen finds **predicted-clean gapmers (2/5) at a favorable breakpoint**. | ★ DONE: gapmer + siRNA design, off-target screen, breakpoint scan, gap-resolved cleavage-risk (all CPU, via GitHub Actions). ★ DONE (2026-07-03): full **real exon-3 junction panel** (EWSR1 e7/9/10/11/12/13::e3) gapmer+siRNA+off-target, **gap-level discrimination margin** (retires the overstating oligo-wide margin, red-team F3). ★ **GPU TO-DO (one high-value run):** physics-based **RNase-H1 cleavage-discrimination MD** to retire the conservative "gap-mismatch ⇒ non-cleaving" heuristic and lift the paper to the degrader's rigor tier on specificity (spec in `manuscripts/fusion-junction-aso-paper.md` §8; small/cheap; validate-one-shard-first; **not a gate on preprinting**). **Remaining dominant gate = tumour DELIVERY** (engineering, not biology; not in-silico-solvable today — now watched two ways in `method-watch.md`: a delivery *predictor* AND a delivery *technology/candidate* incl. an EMC-enriched surface antigen). Wet-lab ask: junction-knockdown + parental-sparing in EMC lines. |
| **Vaccine / HLA-coverage paper** | **PARKED** (done, not a treatment path; self-adjacent junction in a cold tumour = weak immunogen). `hla-coverage-emc.md`. | Never built: (a) reality filters (distance-to-self/tolerance + anchor-vs-TCR position); (b) breakpoint-recurrence quant. `coverage_scan.py` §3.3 numbers + `coverage-curve.png` await a `modalities-cache` snapshot. **Reusable:** its HLA-A\*02 coverage feeds TCR-T eligibility above. |

**Shared rate-limiter for every route:** EMC is nearly absent from public functional-genomics data.
**Correction (2026-07-03): DepMap DOES contain one EMC line — ACH-001519 / H-EMC-SS (OncotreeSubtype
"Extraskeletal Myxoid Chondrosarcoma")** — so "EMC has no DepMap line" (repeated across these memos) is
wrong; there is one (n=1, expression only; CRISPR-dependency/authentication [to verify]). Its surface
transcriptome is used in the surface-target preprint. Still, n=1 + the new patient-derived lines
(NCC-EMC1-C1 2025; USZ-EMC) are the real data; that bottleneck, not idea-generation, is the constraint.

**Surface-target routes are being consolidated into their own paper (2026-07-03).** The B7-H3 ADC/CAR-T,
FAP-RLT, CD56 and PRAME surface/immuno routes above share one input — *which antigen is on an EMC cell* —
and one modality logic (less delivery-gated than the ASO, but not fusion-exclusive). They now feed a
**full, red-teamed preprint**, [`manuscripts/emc-surface-target-landscape.md`](./manuscripts/emc-surface-target-landscape.md)
(+ [`emc-surface-target-redteam.md`](./manuscripts/emc-surface-target-redteam.md), [`emc-surface-target-outreach.md`](./manuscripts/emc-surface-target-outreach.md)).
Honest headline after two red-team passes + the H-EMC-SS discovery: **B7-H3 is NOT selective (BH q=1.0);
CD56/CDH11/PTK7/KIT carry normal-tissue/immune liabilities; the intersection of selective AND
normal-tissue-restricted is empty among classic antigens.** The surviving leads follow EMC's neuroendocrine
differentiation: **SSTR2** (approved ¹⁷⁷Lu-DOTATATE theranostic) and **GD2**. Real EMC data (USZ/NCC lines;
H-EMC-SS is only n=1) is the gate — outreach emails drafted. Modalities: ADC/CAR/TCE/RLT — less oligo-delivery-
gated but hit EMC's myxoid-matrix penetration barrier; and they sacrifice fusion-exclusivity.

**Speculative / forward-looking (AI-era), kept honest:** de-novo binder/TCR design (diffusion
models) to manufacture the warhead or TCR a route lacks; AI structure (AF3) for ternary/PPI
interfaces; combination therapy (anti-angiogenic TKI — EMC's one real clinical signal — + IO).
Lower-credibility for *near* term: CAR-T (no good EMC surface antigen), ADCs (ditto), "nanobots"
(not a near-term clinical reality). Don't over-invest in these until a concrete target is in hand.

## Considered & back-burnered (in-silico)

- **Broadened FET-fusion-addiction class prior (DepMap) — considered 2026-06-27, back-burnered.** We
  scoped extending the single FLI1-in-Ewing datapoint into a systematic class prior: compute the *selective*
  dependency of each translocation sarcoma's fusion-TF/driver across DepMap (Ewing/FLI1, synovial/SS18,
  ARMS/FOXO1, myxoid-lipo/DDIT3, DSRCT/WT1, clear-cell/ATF1) to show fusion-addiction is a robust **class**
  property, not one example. **Decision: not now.** It would make the prior more *robust* but does **not**
  change its category — still transfer evidence, still cannot establish EMC dependence (the exact thing we
  and reviewers discount), so its marginal value over the existing FLI1 datapoint is low. The genuinely
  EMC-specific computation that *would* add a new kind of signal — NR4A3-target **regulon-dominance** on real
  EMC transcriptomes — is blocked on data (no cleanly fetchable EMC RNA-seq; the cited EWSR1::NR4A3 target
  set PPARG/NDRG2/SGK1/SIX3 is small and partly indirect). Instead we (a) tightened the analogy's framing in
  the degrader paper (§5: prior-not-proof + the EWS-LC-domain-vs-NR4A3-effector caveat) and (b) foregrounded
  the EMC-specific **direct-target** evidence (PPARG response element, Filion 2009 — non-transfer support
  that the fusion is a functional transcriptional driver, though functional-driver ≠ addiction).
  **Unblocks if:** a real public EMC expression dataset becomes fetchable (→ run the higher-value
  regulon-dominance test), or a reviewer specifically wants the robust class prior on record (→ cheap to
  build via `depmap-dependency.yml`; note pandas/figshare aren't reachable from a dev sandbox, so it must run
  in CI, not locally).

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

---

## Platform / vision — scale the selective-degrader pipeline (trimcrae, 2026-07-04)
Three linked ideas that form a flywheel (publish tool → apply broadly → aggregate outputs). **All are
DOWNSTREAM of the EMC/NR4A3 north star** — the concrete NR4A3 result is what earns the pipeline credibility
to publish, the justification to apply, and the content to populate a DB. Sequence AFTER the preprint; they
**serve** the EMC mission (democratize selective-degrader design for underfunded diseases), not replace it.
Unifying guardrail: in-silico output is a **hypothesis for someone with a wet lab to test — never a validated
drug**; the medical-integrity labeling discipline gets MORE important as this goes public, not less.

1. **Publish the pipeline as a skill/repo** (open the selective-degrader-design methodology so others can run
   it). High-value + on-ethos. Friction: it's currently bespoke/fragile (see the Yank/SageMaker debugging
   saga) — real hardening + generalizing (de-NR4A3-hardcode) + docs, ideally on the **maintained ABFE stack**
   (next-steps.md "ABFE ENGINE POLICY"), plus a methods paper for citability. Do it AFTER the result lands.
2. **Run the pipeline on other underfunded degrader targets** (rare cancers / neglected diseases with a clear
   driver but no wet-lab funding). Highest-leverage use — cheap per target, each a publishable hypothesis +
   candidate. Needs: (a) a **target-selection rubric** (defined oncogenic driver; AF-modelable structure;
   plausible ligandable/cryptic pocket; real selectivity need) or it's garbage-in; (b) **cheap-triage-before-
   FEP** funnel (FEP only on winners); (c) must NOT dilute the EMC #1 priority — post-EMC-momentum track. This
   is the direct consumer of idea 1's published tool.
3. **Public database of computational degrader candidates across targets** ("computational degrader atlas",
   the aggregation layer for 1+2). Highest RISK — medical-integrity: unvalidated in-silico candidates for
   disease targets are easily misread as validated leads or misused. Requires ruthless honest labeling
   (unvalidated-hypothesis + confidence + provenance + **negative results** to avoid pub-bias distortion) and
   differentiation from existing DBs (PROTAC-DB etc. are literature-curated KNOWN degraders; ours = COMPUTED
   candidates — a distinct niche). Furthest out; gated on 1+2; start as a simple structured output format, not
   a platform.
