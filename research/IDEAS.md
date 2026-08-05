---
id: DOC-IDEAS
title: EMC treatment tracker + parked-ideas backlog
level: —
kind: index
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `index` from its location under research/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
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
of what's shelved vs. active and the next step for each.

> **★ Read alongside it: [`manuscripts/target-route-options.md`](./manuscripts/target-route-options.md)
> (2026-08-02).** This board ranks routes by *likelihood of helping a patient*; that memo ranks the same
> space on the axis neither this board nor the strategy capstone carries — **what each route does to the
> NR4A-paralogue-selectivity requirement** (removes it / reshapes it / merely relocates it), graded
> against the roadmap's failure record. It is where the "accept paralogue cross-reactivity instead of
> engineering around it" question is answered (**no for any systemic molecule** — the NR4A1+NR4A3 pair is
> the named AML anti-target — but the requirement is asymmetric, which is a real and free reduction).
> It also proposes one addition to *this* board: the **TCIP** row auto-captured on 2026-07-13 below, whose
> citation must clear `verify-refs` first.

> **★★ AND READ [`manuscripts/emc-post-degrader-options.md`](./manuscripts/emc-post-degrader-options.md)
> (2026-08-03) BEFORE PICKING THE NEXT ROUTE.** It answers the question this board does not: *if the
> degrader cannot deliver a candidate — which is where it is trending — what does?* Its organising
> finding is that **every one of the degrader program's blocking failures is a property of the
> DEGRADER ARCHITECTURE (ternary geometry + a ~1 kcal/mol paralogue ΔΔG), not of the target**, so a
> route needing only a *binder* inherits none of them. Three things it adds to this board, integrated
> into the table below: the **ATR-inhibitor synthetic-lethality route** (inherited by EMC as a
> FET-rearranged cancer), a **new all-approved-drug combination** (trabectedin + PPARγ agonist on the
> fusion's own documented PPARG axis), and **two routes closed on their own pharmacology**
> (RXR-heterodimer modulation; 6-mercaptopurine/AF-1 agonism).
>
> ⚠ **ITS RANKING WAS CORRECTED THE SAME DAY, AND THE CORRECTION CHANGES WHAT TO START.** The first
> tiering graded the wet-lab ask on **cheapness**, which silently assumes a collaborator with a bench
> — and there is none. Cheapness only counts conditional on somebody existing who would run it. So
> the axis was split into **W1** (*is there a plausible, self-interested taker?*) and **W2** (*the
> ask's size, conditional on W1*), and ⭑ **Axis D** was added — ***what do we end up holding if the
> experiment never happens?*** — which is the decisive axis for a programme that cannot execute.
> **What that re-ranked, and it is the ordering this board now follows:**
> **(1)** the ⭐ **methods paper on the degrader program's own failure record** — a complete
> deliverable requiring nobody's cooperation — moves from #3 to **#1**;
> **(2)** the **fusion-junction ASO** holds rank 2, because its in-silico arc was already finished and
> red-teamed, which is exactly the profile that survives the reframe;
> **(3)** the ATR route **splits**: its **computed vulnerability assessment** is Tier 1 rank 3
> (it produces a result either way), while the **cell panel is the ASK** — Tier 2, with the best W1
> in the portfolio because EMC's nuclear-receptor partner is the missing fourth TF-partner class in
> the FET/ATR authors' own published argument, and it is **not something this programme executes**;
> **(4)** **TCIP, the covalent probe and SSTR2 all DROP to Tier 3**, each for its own reason, and
> **trabectedin + PPARγ** is now explicitly an ask (good W1, thin Axis D).
> ⚠ **Nothing was refuted or removed.** Superseded tiers, kept quotable:
> [that memo's §6](./manuscripts/emc-post-degrader-options.md#6--appendix--the-superseded-ranking-and-what-was-wrong-with-its-axis)
> and [STRATEGY.md Appendix B](../STRATEGY.md#appendix-b--superseded-strategy-framings).

> **🗺 WHICH ROW IS WHICH, AND WHOSE GRADE IS IT — [`manuscripts/emc-systems-map.md`](./manuscripts/emc-systems-map.md)
> (2026-08-03), generated from [`emc-systems-map.json`](./manuscripts/emc-systems-map.json) and
> checked in CI by [`emc_systems_map_check.py`](./manuscripts/emc_systems_map_check.py).** It adds no
> grade and no number — it records, machine-readably, **where each one already lives** and fails the
> build when a pointer stops resolving. Use it when the same thing appears twice under different
> names: it carries every route's **aliases** across the memos' three separate numbering schemes,
> each fusion type as a **separate object** at exon and residue level, every source keyed by
> **PMID/DOI with all the names it travels under**, which **instruments have no passing
> known-answer control**, and which quoted figures resolve to a real artifact field **on `main`**.
> It also names, per pair, **which routes must never be conflated and the opposite blockers they
> fail on** — the covalent probe and the monovalent modulator being the worked case.

The goal pivoted away from the vaccine/coverage work (rigorous but unlikely to
*yield a treatment*; economics favour a tumour-agnostic platform we don't control) toward routes
that could actually drug or immuno-target EWSR1::NR4A3 EMC.

**No wet lab — read next-steps through that lens.** Our two levers are (1) **publish-to-convince**
(make the case so a lab/clinician runs it) and (2) **in-silico evaluation** (★ items we can run
ourselves — design, modelling, public-data mining — now or with near-future virtual-cell/
perturbation models). Wet-lab items in the table (dTAG, IHC, CRISPR screen) are **not our to-do** —
they're what a convincing paper should get *others* to do, or what we replace with an in-silico
proxy. See `emc-treatment-strategy.md` → "two paths" + "in-silico work program".

> **⛔ AND THERE IS NO THIRD LEVER — SCOPED AND CLOSED 2026-08-03:
> [`manuscripts/what-a-civilian-can-buy.md`](./manuscripts/what-a-civilian-can-buy.md).** The obvious
> question underneath "no wet lab" is *what can a private individual with a credit card buy outright
> — mail-order products and contracted services?* That was scoped against three filters (≲$1,000 · no
> hands-on bench work by trimcrae · a negative that MEANS something), and **the buyable tier came back
> EMPTY: every open question in this repo is either in-silico or needs a lab we do not have.** Read it
> before proposing a purchase, so this is not re-litigated. The two facts worth knowing without
> opening it: **(1)** the cell-line repositories exclude individuals *by published policy, not by
> price* — DSMZ states *"Only institutions and companies are eligible to order from the DSMZ"* and
> ATCC's account application rejects a residential shipping address — so **route 1's cheap wet-lab ask
> is gated on a collaborator, and no budget changes that**; **(2)** ⭑ a **catalogue recombinant NR4A3
> ligand-binding domain does exist** (Cayman 40344, aa 398–626), so the blocker on `R4` is **not**
> protein supply — it is that a binding assay reports a binding *event* and `R4` asks about a *site*.

| Route | Status | Next step (★ = computational, no wet lab) |
|---|---|---|
| **ATR inhibitor — synthetic lethality EMC inherits as a FET-rearranged cancer** | **★ NEW 2026-08-03 — and it is TWO things, which the corrected ranking separates.** ⭑ **(a) The in-silico vulnerability assessment is a Tier-1 DELIVERABLE** (it produces a computed result whether or not any cell is ever plated); ⭑ **(b) the cell panel is the repo's best-positioned ASK, and is not something this programme executes** — best **W1** on the board because EMC's nuclear-receptor partner is the missing fourth TF-partner class in the FET/ATR authors' own published argument (beside their ETS, bZIP and zinc-finger partners), and smallest **W2**. ⚠ *Superseded, retained: this row read* **"NEW TOP CANDIDATE … and the cheapest wet-lab ask on this board"** *— cheapness was graded as if a collaborator existed to spend it; see the pointer block above.* FET fusion oncoproteins impair ATM activation at double-strand breaks through their shared N-terminal IDR, leaving the ATR axis load-bearing → ATR inhibitors are synthetic lethal (PMID 37205599). It is already **partner-agnostic in the tested set** — ETS (Ewing), bZIP (clear cell sarcoma, EWSR1::ATF1) and zinc-finger (DSRCT, EWSR1::WT1) partners, elimusertib IC50 20–60 nM, significant anti-tumour response in all **5** FET-rearranged PDX models. **≈89–95 % of EMC carries a FET-family 5′ partner** (EWSR1/TAF15/FUS), so EMC is a FET-rearranged cancer by construction, with a **fourth, untested TF-partner class** (a nuclear receptor). Needs **no NR4A-paralogue selectivity, no ternary and no ΔΔG** — it inherits none of the degrader program's blockers. ⚠ Class inheritance, NOT an EMC measurement: no NR4A3 fusion has been tested for the ATM phenotype. ⚠ The ATR class has retreated commercially (ceralasertib ph3 miss; elimusertib/berzosertib/camonsertib deprioritised) — that is not a mechanistic refutation but it changes the deliverable to *hypothesis + biomarker*. Full route: [`manuscripts/emc-post-degrader-options.md`](./manuscripts/emc-post-degrader-options.md) route 1. | ★ **DONE — the structural precondition is COMPUTED and it holds** ([`emc_fet_idr_census.py`](./modalities/emc_fet_idr_census.py)): EMC's canonical fusion retains **EWSR1(1–264), byte-identical to the Ewing type-1 retained half** in which ATM suppression was measured, keeping **0 of 30** RG dipeptides — and the controls calibrate it, since the commonest clear-cell type keeps 7 of 30 and the mechanism was measured there anyway. ★ **DONE — the preregistration is written before anyone is approached** ([`emc-atri-prereg.md`](./modalities/emc-atri-prereg.md)), carrying a **PARP-inhibitor negative-translation control** because PARPi monotherapy already failed clinically in Ewing despite a LARGER in-vitro FET-line signal. ★ DONE: DepMap **knockout** scan — reported as a **failed instrument** (ATR axis at the common-essential floor, −1.578 FET vs −1.601 non-FET sarcoma, delta 0.02 on SD 0.12–0.15), plus the $0 finding that the DepMap model labelled EMC, **ACH-001519/H-EMC-SS, has no CRISPR data** (closes an open `[to verify]`; ✅ **unaffected by the 2026-08-05 identity correction above** — it is a statement about data availability, and no dependency number in this repo rests on that model). ★ **DONE — and it cuts both ways:** the ATRi sensitivity re-cut by FET status (GDSC2 8.5; the source paper split only Ewing-vs-rest) shows the ATR effect survives a general-chemosensitivity correction (AZD6738 Δ −0.491, *t* −5.08) **but PARP inhibitors are 2–4× larger in the same lines** ([`fet_ddr_axis_scan.py`](./modalities/fet_ddr_axis_scan.py)). ★ **DONE 2026-08-05 — the four-part in-silico vulnerability assessment is graded: tier `WEAK`** ([`emc-atr-vulnerability-assessment.md`](./manuscripts/emc-atr-vulnerability-assessment.md)). ⭐ **And the standing blocker "no cleanly fetchable EMC RNA-seq" is RETIRED: two readable EMC expression series exist** — GSE24369/GPL6244 (6 EMC vs 29 comparators, 17 of them LGFMS, i.e. another FET fusion) and GSE4303/GPL3290 (10 EMC, rescued from 1.0 % to 58.2 % probe annotation by the archived UniGene build). Both say the same thing and it is the WEAK criterion verbatim: EMC's DDR/replication-stress transcripts are elevated only as far as generic proliferation is, and two UNRELATED control sets move as much. ⛔ **That bounds the hypothesis's transcriptional shadow, NOT the hypothesis** — no expression matrix can measure a recruitment-and-phosphorylation event at a DSB. ⛔ **Parts C and D are NEGATIVE about the hypothesis's COMPUTATIONAL support:** a matched fusion-negative *sarcoma* comparator does not un-blind the DepMap knockout readout, and ATRi sensitivity does **not** track the mechanism — 1 of 4 pre-registered tests passes, and the mechanism's load-bearing predictor (low ATM signalling) returns ρ −0.090, the **wrong sign**. ⚠ The group difference above is **not** contradicted; a group difference and mechanism-tracking are different claims and only the first is supported. ✅ **The ASK is unaffected** — the structural precondition census, the construct designs, the RGG dose-calibration prediction and the TCF12 negative control are sequence arguments, not public-data correlations. **The ask survives; its computed support is weaker than first represented.** ★ **NEXT:** trimcrae's call on approaching a model-holding group — outward-facing, so gated per CLAUDE.md §3. **Wet-lab ask:** catalogue ATR inhibitor, 7-point dose–response on the existing EMC lines vs a non-FET sarcoma control, γH2AX readout (the reliable PD biomarker in this setting), **plus a PARP-inhibitor arm and a proliferation index** — both required by the prereg. |
| **Trabectedin + PPARγ agonist (all approved drugs)** | **★ NEW (2026-08-03) — a synthesis this board had as two separate rows and never joined.** ⭑ **Under the corrected axes it is an ASK with a good taker and a thin deliverable:** all drugs approved and the pioglitazone + trabectedin authors have a genuine class-extension interest in a second myxoid sarcoma (**good W1**, **small W2**), but if nobody runs the matrix we hold a literature synthesis plus at best an expression read on the single `n = 1` EMC model (**thin Axis D**), which is why it ranks below the ATR panel. The fusion **transactivates PPARG directly** (Filion 2009, PMC4429309); trabectedin's mechanism **is** displacing fusion TFs from promoters and EMC has a reported responder; and the combination **already worked in the sibling myxoid sarcoma** — pioglitazone + trabectedin induced adipocyte differentiation and overcame trabectedin resistance in myxoid liposarcoma (*Clin Cancer Res* 2019;25:7565). ⚠ **The direction question is real and cuts against the naive version:** in myxoid liposarcoma FUS::DDIT3 *blocks* differentiation and the agonist restores it, whereas in EMC the fusion turns PPARG *on*, so an agonist may be redundant. Honest hypothesis: EMC's driver has already installed a differentiation-competent nuclear receptor and promoter-displacement may unmask it. | ★ **NEXT (\$0):** pull EMC PPARG-axis expression to settle agonism-vs-redundancy before weighting. **Wet-lab ask:** a two-drug matrix on the existing EMC lines — approved drugs, catalogue reagents, one plate. |
| **Checkpoint inhibitor + anti-angiogenic TKI combination** | **TOP NEAR-TERM LEAD (best EMC evidence).** ImmunoSarc (sunitinib+nivolumab) had an actual **EMC partial responder**; mechanistically the TKI remodels the cold TME (cold→hot) and EMC is already TKI-sensitive — synergy, not coincidence. All drugs approved. See `immunotherapy-options-emc.md` §2. | ★ Grade the EMC IO/TKI response evidence into a table; pick the best TKI+ICI pairing (pazopanib/sunitinib/anlotinib/regorafenib + anti-PD-1). Vehicle = sarcoma/basket trial. |
| **Trabectedin (± RT or combo)** | **NEAR-TERM LEAD (approved, mechanism-fit).** Displaces fusion-TFs from target promoters (its MoA in myxoid liposarcoma); EMC is the same class and has a reported **impressive EMC responder**. `emerging-modalities-scan-emc.md` §1. | ★ Curate EMC trabectedin response evidence; consider rational trabectedin + TKI/IO combos (non-overlapping mechanisms). |
| **Carfilzomib ± anthracycline (± venetoclax)** | **NEAR-TERM LEAD — best *ex-vivo EMC* evidence.** Of **17 chemotherapeutics** in a **40-drug** screen, carfilzomib was the **only** one showing high sensitivity — ⚠ *that screen was run on **USZ20-EMC1 alone**; carfilzomib, doxorubicin and venetoclax were then validated in **both** models (USZ20-EMC1, USZ22-EMC2), where **venetoclax showed no response as a monotherapy**. Superseded, retained: "1/17 drugs with high sensitivity across 2 patient-derived EMC models", which read the single-model screen as a two-model result.* Synergy — carfilzomib + doxorubicin and carfilzomib + venetoclax — is additive/synergistic in both (Bangerter 2023, PMID 36316541, doi:10.1007/s13577-022-00818-x). Already in the repurposing track. | ★ Preclinical confirmation → combination arm on EMC's anthracycline backbone. See `repurposing-hypotheses.md`. |
| **B7-H3 (CD276) → ADC / bispecific / CAR-T** | **Promoted — surrogate expression now supports it.** In-silico: **CD276 expressed in 99% of sarcoma lines, high across *every* subtype incl. myxoid** (`depmap-insilico-findings.md`), on top of 97% pan-STS IHC. ADC ifinatamab deruxtecan / CC-3 bispecific / B7-H3 CAR-T ready. A *surface* target (unlike the intracellular fusion/CTAs). | ★ Confirm in EMC tissue / public proteomics (HPA) — expression prior is now favourable, not a coin-flip. If +, ADC is fastest; CAR-T = Phase-3 route. |
| **FAP-targeted radioligand therapy (FAPI-RLT)** | **Emerging, plausible.** ⁹⁰Y/¹⁷⁷Lu/²²⁵Ac-FAPI controlled disease in ~half of advanced-sarcoma pts; EMC's myxoid stroma is likely FAP⁺. Tracer is also diagnostic (FAP-PET). `emerging-modalities-scan-emc.md` §2. | ★ Confirm EMC FAP-PET avidity/expression; if avid, off-the-shelf theranostic via RLT programs. |
| **PPARG downstream-effector (repurpose TZDs)** | **Novel, speculative, druggable.** The fusion *transactivates PPARG* (a druggable NR with approved agonists). Attack the pathway where it's tractable, not the undruggable TF. `emerging-modalities-scan-emc.md` §4. | ★ Pull EMC PPARG-axis + TZD-in-sarcoma data; resolve agonism-vs-antagonism direction before weighting. |
| **CAR-T for EMC** | **Hard but not closed.** Driver is nuclear (no surface target) + cold myxoid stroma. Surface options: B7-H3 (lead), **CD56/NCAM** (EMC NE-phenotype angle), FAP (anti-stroma), GD2/HER2 (fallback). Among surface modalities, ADC/FAPI-RLT likely beat CAR-T to a patient; CAR-T is the higher-ceiling follow-on. `car-t-strategies-emc.md`. | ★ EMC B7-H3 + CD56 IHC; ★ **surfaceome screen** of the fusion's transcriptional output to find an EMC-enriched surface target. Constructs: CAR-T **+ TKI** (crack cold TME), armored/IL-12, SynNotch/dual (B7-H3∧CD56) logic gate, **allogeneic** (rare-disease economics). |
| **TCR-T / engineered T cells vs a cancer-testis antigen (synovial-sarcoma port)** | **DOWNGRADED to weak (gating fact resolved, mostly negative).** EMC is CTA-low: NY-ESO-1 rare (used to tell myxoid liposarcoma *apart from* EMC), PRAME ~8% in chondrosarcoma, MAGE-A4 not reported high. afami-cel/letetresgene don't port. `immunotherapy-options-emc.md` §1. | ★ Only remaining door (low prior): a dedicated **EMC MAGE-A4/PRAME IHC series** × HLA-A\*02:01 carrier freq (computable via `hla_coverage.py`) — a cheap confirm/kill for a single-digit-% subset, not a lead. |
| **Degrader — NR4A3-LBD PROTAC** | **LEADING driver-directed route; the in-silico druggability case is BUILT AND PARTLY REFUTED — as of 2026-08-02 the roadmap scoreboard reads 7 gates passed · 4 FAILED · 1 delivered-but-not-graded ([the roadmap](manuscripts/nr4a3-program-map.md) is its one home).** ⚠ *Superseded, retained: "in-silico druggability case COMPLETE (2026-06-26 — gates pass)". Gate 1 FAILED as pre-registered and the `denovo_401` generation-frame audit is CLOSED and FAILED; a row saying "gates pass" on the repository's idea board contradicted both the roadmap and the paper.* 30 ns metadynamics: the orthosteric pocket opens to fpocket **0.931** (Gate 2) and a druggable conformation is thermally accessible at **0.76 kcal/mol** (Gate 3); calibrated D\*=0.53, static 0.495 is conservative. Handle-facing CONFIRMED (5/7 handles engageable) + warhead screen RAN (NR4A3-favoured chemotypes, margins triage-only). **Now building a FAMILY-WIDE SELECTIVITY MATRIX: same 30 ns metad on NR4A1+NR4A2 (**DONE 2026-06-28**) → state-matched opened ensembles → per-candidate selectivity fingerprint (NR4A3-only / pan / anti-target NR4A1+NR4A3). Resume guide: `modalities/nr4a3-degrader-next-steps.md`.** Orthosteric LBD pocket carries all 7 selectivity handles — druggability and selectivity coincide. *(A 2026-06-25 claim that this pocket was ~0.026 was a self-inflicted enumeration bug, retracted same day; regeneration from the count-fixed pipeline reconfirms 0.495 — see `emc-treatment-strategy.md` feasibility check + `modalities/ASSUMPTIONS.md`.)* Degradation is *mechanistically ideal* (NOR-1 activity scales with expression level). **Fusion-addiction premise supported by analogy — a bet-justifying prior, NOT EMC proof: FLI1 in Ewing = −0.93 gene effect, 74% dependent → FET-fusion sarcomas are fusion-addicted, raising the prior that degrading EWSR1::NR4A3 could be lethal in EMC; the dTAG test remains the make-or-break** (`depmap-insilico-findings.md`). NR4A3-specific warhead starting points exist (inverse NOR-1 agonists, **Zaienne 2022, PMID 35704774**, PMC9542104). ⭐ **AND THE DOMAIN QUESTION IS NOW ANSWERED, VERBATIM, IN THE ROUTE'S FAVOUR (2026-08-03):** those hits were read out on `pFA-CMV-hNOR-1-LBD`, *"coding for the **hinge region and LBD** of the canonical isoform of NOR-1"* — a Gal4 chimera that **does not contain the AF-1 the EMC fusion deletes**, so the domain the disease protein loses is not the domain the published pharmacology rests on. ⚠ Site still **unassigned** (competition only), **no purified protein and no biophysical binding measurement anywhere in the paper**, and **no NR4A1/NR4A2 counter-screen** — so this is ligandability of `hinge+LBD`, NOT an answer to `R4` (does anything bind the modelled cryptic Pocket-5). Evidence + limits: [`modalities/nr4a3-druggability-reconciliation.md` §5a](./modalities/nr4a3-druggability-reconciliation.md). ⛔ *Superseded, retained: this row cited the same paper as* **"Munck 2022"** *— an attribution measured in CI on 2026-08-03 to name no paper in Europe PMC or PubMed ([§5b](./modalities/nr4a3-druggability-reconciliation.md)). ★ It is a finding in its own right: the field's one positive NR4A3 ligand-discovery result sat in THIS row under a name that could not be looked up, while a route was demoted elsewhere for lacking an experimental anchor.* NR4A1 PROTAC works but doesn't cross-degrade NR4A3. Design spec: `nr4a3-degrader-design-spec.md`. | ★ **Make-or-break: ANSWERED** — cryptic-pocket MD shows the pocket reaches druggable (0.93) at low energetic cost (Gate 3 pass). ★ **DONE:** handle-facing (run 28249776934) + warhead screen (run 28252182123). ★ **DONE, NOT IN FLIGHT:** the family-wide metad matrix finished **2026-06-28** and everything the old "NEXT" list named ran between 2026-06-28 and 2026-07-01 — docking into all three opened pockets, MM-GBSA/FEP, de-novo design, and the per-paralogue ternary. ⚠ *Superseded, retained: "★ **IN FLIGHT:** family-wide metad NR4A1 (28256669839) + NR4A2 (28256671172)". Measured on the public Actions API 2026-08-05: **28256669839 = `failure`, 28256671172 = `cancelled`**, both 2026-06-26. The work was redone as SageMaker jobs `nr4a1-metad-2026-06-27-11-44-08` / `nr4a2-metad-2026-06-27-22-00-03`. A board advertising two dead runs as live work for six weeks is the exact shape §4 forbids — an unanswered question wearing the costume of a status.* Current state: [`modalities/nr4a3-degrader-next-steps.md`](./modalities/nr4a3-degrader-next-steps.md). Publish the cryptic-pocket result + addiction-analogy + designed warhead together; dTAG test = what the paper asks others to run. |
| **PRAME-directed (brenetafusp ImmTAC / PRAME CAR-TCR)** | **NEW antigen-directed lead — best of the CTAs.** In-silico: PRAME expressed in **53% of sarcoma lines**, vs MAGE-A4 (7%) and NY-ESO-1 (5%) — **the RELATIVE ordering across the whole panel is the claim** (`depmap-insilico-findings.md`). brenetafusp runs a tumour-agnostic basket → access without a bespoke product. ⛔ **2026-08-05:** the myxoid-proximity half of this row is **withdrawn** — the `myxoid` group is `n = 1` and that line's identity is disputed (see the CORRECTION-OF-A-CORRECTION above), so *(superseded, retained)* "**HIGH in myxoid (7.6) & synovial (7.2)** — EMC is myxoid-class" is not an EMC-proximal read. **The grade is NOT re-set here** — its relative support survives, its subtype support does not; that is a call for whoever owns this row. | ★ Confirm PRAME in EMC tissue / public proteomics (cell-line CTA reads are lower bounds). If +, brenetafusp basket eligibility (PRAME⁺/HLA-A\*02⁺). |
| **ImmTAC / soluble-TCR bispecific (off-the-shelf)** | **Weak — same antigen gate as TCR-T.** Targets a peptide-HLA (PRAME/MAGE-A4 on HLA-A\*02); EMC is PRAME-/MAGE-A4-low. `immunotherapy-options-emc.md` §2b. | One thread: **brenetafusp (PRAME ImmTAC) runs a tumour-agnostic basket** → a PRAME⁺/A\*02⁺ EMC patient could enrol without a bespoke product (small prior). EMC-specific = fusion-junction-pHLA ImmTAC (hard, same weak-junction problem). |
| **Synthetic-lethal (BRD9/ncBAF via EWSR1-prion→BAF)** | **DOWNGRADED.** DepMap 24Q4 transfer prior **negative**: BRD9 not a sarcoma dependency, not even in Ewing; BET/CDK pan-essential, no selectivity window (`depmap-sarcoma-dependency.json`). | No cheap shortcut; needs a **de-novo CRISPR screen in patient-derived EMC lines**. Don't spend a wet-lab slot on a transfer-justified BRD9 test. |
| **AF3 on a druggable interface** | Deferred; method not strategy. | ★ Only once the degrader route picks a ternary/PPI interface (fusion↔CBP/p300 or fusion↔E3). |
| **Fusion-junction ASO / siRNA** (`manuscripts/fusion-junction-aso-paper.md`; `novel-modalities.md` §3.2) | **PRIORITY PAPER (2026-06-26) — one of the two to publish first, with the degrader.** Fusion-EXCLUSIVE (spares wild-type NR4A3, which the degrader cannot); most-likely-to-work fusion-unique route. In-silico arc complete: design → transcriptome-wide off-target → per-breakpoint favorability scan (canonical junction GC-rich/specificity-poor, but **62% of modelled breakpoints favorable**) → gap-mismatch-resolved screen finds **predicted-clean gapmers (2/5) at a favorable breakpoint**. | ★ DONE: gapmer + siRNA design, off-target screen, breakpoint scan, gap-resolved cleavage-risk (all CPU, via GitHub Actions). ★ DONE (2026-07-03): full **real exon-3 junction panel** (EWSR1 e7/9/10/11/12/13::e3) gapmer+siRNA+off-target, **gap-level discrimination margin** (retires the overstating oligo-wide margin, red-team F3). ★ **GPU TO-DO (one high-value run):** physics-based **RNase-H1 cleavage-discrimination MD** to retire the conservative "gap-mismatch ⇒ non-cleaving" heuristic and lift the paper to the degrader's rigor tier on specificity (spec in `manuscripts/fusion-junction-aso-paper.md` §8; small/cheap; validate-one-shard-first; **not a gate on preprinting**). **Remaining dominant gate = tumour DELIVERY** (engineering, not biology; not in-silico-solvable today — now watched two ways in `method-watch.md`: a delivery *predictor* AND a delivery *technology/candidate* incl. an EMC-enriched surface antigen). Wet-lab ask: junction-knockdown + parental-sparing in EMC lines. |
| **RXR-heterodimer modulation of the fusion** | **✕ CLOSED 2026-08-03.** NR4A1 and NR4A2 form permissive RXR heterodimers and RXR ligands modulate them; **NR4A3 does not heterodimerise with RXR**, so the one pharmacology solved in this receptor family does not reach our paralogue. Reasoning + citation: [`manuscripts/emc-post-degrader-options.md`](./manuscripts/emc-post-degrader-options.md) tier 4. | None. Recorded so it is not re-proposed. |
| **6-mercaptopurine / AF-1 agonism of the fusion** | **✕ CLOSED 2026-08-03.** 6-MP is the one approved drug that activates NR4A3, but it acts **through the AF-1, independently of the LBD** — and the AF-1 is exactly the domain EWSR1's low-complexity region replaces in the fusion. Reasoning + citation: [`manuscripts/emc-post-degrader-options.md`](./manuscripts/emc-post-degrader-options.md) tier 4. ⚠ **Scoped 2026-08-03 so it is not over-read:** this closes *6-MP*, **not** LBD-directed modulation generally — the one published LBD-borne functional result on NOR-1 was read out on a **Gal4-NOR-1-LBD** reporter, itself AF-1-less. See the monovalent row below. | None. Recorded so it is not re-proposed. |
| **Monovalent LBD pocket modulation (a molecule that only OCCUPIES the NR4A3 LBD)** ⭑ **NEW 2026-08-03** | **★ REGISTERED, NOT PROMOTED — and it is a DOWNGRADE of what "the covalent probe at C397" implies about a monovalent *drug*.** The third framing of C397, never previously stated: no second protein, no linker, no exit vector, no ubiquitin geometry, **no ternary** — so it retires `R9`/`R10`/`R11`/`R12` outright and is strictly cleaner than TCIP on that axis, which still inherits the induced-complex problem. ★ **One free promotion inside it, now INDEPENDENTLY VERIFIED against the primary source (2026-08-03):** the AF-1 deletion is *not* a defeater — the published LBD-borne functional result used a Gal4 construct that already lacks NR4A3's AF-1 (Zaienne, ChemMedChem 2022, **PMID 35704774**). ⭐ **The plasmid, verbatim, and it is one range WIDER than the repo had been relaying:** `pFA-CMV-hNOR-1-LBD` *"coding for the **hinge region and LBD** of the canonical isoform of NOR-1"* — so the correct scope is **`hinge+LBD`**, not `LBD`; the adjudication is unaffected because both lie entirely outside the AF-1, but a claim scoped to "the LBD" is wider than the evidence. Quotes, limits and provenance: [`modalities/nr4a3-druggability-reconciliation.md` §5a](./modalities/nr4a3-druggability-reconciliation.md). ⛔ *The "Munck 2022" attribution this row flagged as a resolution item is* **RESOLVED and retained as superseded** *— measured to name no paper ([§5b](./modalities/nr4a3-druggability-reconciliation.md)), corrected in all five files, pinned by `modalities/tests/test_munck_attribution_retired.py`.* ⛔ **Two blockers that hold it down.** (i) The route splits into two sub-forms that fail on *opposite* blockers: non-covalent occupancy is still an `exp(−ΔΔG/RT)` ratio, i.e. the requirement the program has failed to measure four ways; covalent occupancy escapes that categorically — **but the E3-arm-free reach enumeration was built and run and closes the categorical window at C397 on the conservative convention in every cell that had one.** (ii) It is the **only** LBD route needing the pocket to be a *functional* handle in the chimera, whose other end is a strong independent activator — and the delegated dTAG test does not answer that. Full route, evidence and grade: [`manuscripts/nr4a3-monovalent-pocket-route.md`](./manuscripts/nr4a3-monovalent-pocket-route.md). | ★ **DONE ($0):** the paired monovalent-vs-bivalent reach enumeration ([`modalities/nr4a3_monovalent_reach.py`](./modalities/nr4a3_monovalent_reach.py) → [`nr4a3-monovalent-reach.json`](./modalities/nr4a3-monovalent-reach.json), 18 tests; its bivalent half replicates the committed artifact cell-for-cell). ★ **DONE ($0):** the route-specific half of the purchasability question — the repo-wide verdict is owned by [`manuscripts/what-a-civilian-can-buy.md`](./manuscripts/what-a-civilian-can-buy.md) (`R4` is **not buyable**), and this route adds one consequence its audit did not draw: the single catalogue recombinant NR4A3 LBD spans UniProt **398–626**, so it **excludes C397 by one residue** and an intact-mass covalent-probe readout on it would be blind to the programme's headline handle. ⭐ **AND THE ROUTE IS TWO ROWS, NOT ONE — stated here so a demotion of one is never read onto the other.** This row is the **monovalent modulator (a drug)**; [`manuscripts/emc-post-degrader-options.md`](./manuscripts/emc-post-degrader-options.md) route 5 is the **covalent probe at C397 (a reagent)**. They share exactly one instrument, and only for this row's covalent sub-form. ⛔ **Route 5's Tier-3 demotion rests on `V17` failing its own positive control and on no thiol pKa or intrinsic reactivity being computed — and `V17` is a CYSTEINE-EXPOSURE criterion, so it has NO bearing on the non-covalent sub-form, which has no cysteine.** Applying that demotion across the board would be applying a cysteine instrument's failure to a route with no cysteine. ★ **NEXT ($0):** re-run the same paired configuration for the **TCIP** arm (a different second terminus — not answered by this result). **No wet-lab ask is made** — the route's make-or-break is a functional cell assay nobody has run. |
| **Vaccine / HLA-coverage paper** | **PARKED** (done, not a treatment path; self-adjacent junction in a cold tumour = weak immunogen). `hla-coverage-emc.md`. | Never built: (a) reality filters (distance-to-self/tolerance + anchor-vs-TCR position); (b) breakpoint-recurrence quant. `coverage_scan.py` §3.3 numbers + `coverage-curve.png` await a `modalities-cache` snapshot. **Reusable:** its HLA-A\*02 coverage feeds TCR-T eligibility above. |

**Shared rate-limiter for every route:** EMC is nearly absent from public functional-genomics data.
**⛔ CORRECTION-OF-A-CORRECTION (2026-08-05) — and the irony is the point.** The 2026-07-03 entry below
*corrected* this repo's belief that EMC had no DepMap line. **That correction was itself wrong in the way that
mattered**, and it stood for a month because the `[to verify]` it carried was carried rather than resolved.
**Cellosaurus `CVCL_1238` records, citing a primary source:** *"Caution: Does not harbor a gene fusion
involving EWSR1 which is a hallmark of extraskeletal myxoid chondrosarcoma (PubMed=34413129)."* DepMap's own
filtered fusion caller returns 2 calls for the model and **none names NR4A3 or any FET gene**; NR4A3 reads
0.941 log2(TPM+1). Verdict `NOT_FUSION_POSITIVE_PER_CURATED_RECORD`
([`modalities/emc-atr-vulnerability.json`](./modalities/emc-atr-vulnerability.json) →
`part_a_hemcss_identity`). ⚠ **This does NOT establish that the line is not EMC, nor what it is instead** —
identity needs STR authentication + RT-PCR, which are not public and which this programme cannot perform. What
is established is that **the public record does not support the label**. So the operative statement is the
one the 2026-07-03 entry retired: **for the purpose of reading EMC biology, DepMap gives this repo nothing**,
and the patient-derived lines (NCC-EMC1-C1 2025; USZ-EMC) are the only real data. Propagation across the repo:
[`manuscripts/emc-surface-target-landscape.md` → Amendment 1](./manuscripts/emc-surface-target-landscape.md).

⛔ *Superseded, retained verbatim and quotable:* **"Correction (2026-07-03): DepMap DOES contain one EMC line — ACH-001519 / H-EMC-SS (OncotreeSubtype
"Extraskeletal Myxoid Chondrosarcoma")** — so "EMC has no DepMap line" (repeated across these memos) is
wrong; there is one (n=1, expression only; CRISPR-dependency/authentication [to verify]). Its surface
transcriptome is used in the surface-target preprint. Still, n=1 + the new patient-derived lines
(NCC-EMC1-C1 2025; USZ-EMC) are the real data; that bottleneck, not idea-generation, is the constraint."
*(The CRISPR half of that `[to verify]` was separately answered and is unaffected: the model has no CRISPR
gene-effect data — [`modalities/fet-ddr-axis-scan.json`](./modalities/fet-ddr-axis-scan.json) →
`/emc_line/has_crispr_gene_effect`.)*

**Surface-target routes are being consolidated into their own paper (2026-07-03).** The B7-H3 ADC/CAR-T,
FAP-RLT, CD56 and PRAME surface/immuno routes above share one input — *which antigen is on an EMC cell* —
and one modality logic (less delivery-gated than the ASO, but not fusion-exclusive). They now feed a
**full, red-teamed preprint**, [`manuscripts/emc-surface-target-landscape.md`](./manuscripts/emc-surface-target-landscape.md)
(+ [`emc-surface-target-redteam.md`](./manuscripts/emc-surface-target-redteam.md), [`emc-surface-target-outreach.md`](./manuscripts/emc-surface-target-outreach.md)).
Honest headline after two red-team passes: **B7-H3 is NOT selective (BH q=1.0);
CD56/CDH11/PTK7/KIT carry normal-tissue/immune liabilities; the intersection of selective AND
normal-tissue-restricted is empty among classic antigens.** ⛔ **Amended 2026-08-05:** these results **survive**
the line-identity correction above — dropping ACH-001519 from the 45-line class moves every actionable
antigen's enrichment by ≤ 0.13 log2TPM with no sign flips — but the paper's real-EMC readings are withdrawn.
*(Superseded, retained: the headline was credited to "two red-team passes **+ the H-EMC-SS discovery**", and
the gate read "Real EMC data (USZ/NCC lines; **H-EMC-SS is only n=1**) is the gate".)* The surviving leads
follow EMC's neuroendocrine differentiation from **reported IHC**: **SSTR2** (approved ¹⁷⁷Lu-DOTATATE
theranostic) and **GD2**. Real EMC data (USZ/NCC lines **only**) is the gate — outreach emails drafted. Modalities: ADC/CAR/TCE/RLT — less oligo-delivery-
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
  PyTorch; upstream PocketMiner's `model.py` (not ours) uses DGL 0.5.2 heterograph/message-passing APIs that broke in
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
4. **Cryptic-pocket *druggability* atlas for neglected targets** (trimcrae, 2026-07-05) — **★ HIGH-PRIORITY
   NEXT MAJOR PROGRAM after the NR4A3 degrader preprint posts.** Full concept memo:
   **[`cryptic-pocket-atlas-concept.md`](./manuscripts/cryptic-pocket-atlas-concept.md)** (funnel, Phase-0 gate, compute
   budget, staged plan, integrity guardrails). In brief — the **upstream**
   layer that feeds 2+3: before you can design a selective degrader/binder you need a *druggable pocket*, and
   for "undruggable" targets that pocket is often **cryptic** (only opens under dynamics). This is a public,
   **structurally-explicit, druggability-scored** cryptic-pocket resource for neglected / undruggable human
   disease targets (fusion-TFs, orphan nuclear receptors, Tdark drivers), built from **enhanced-sampling MD +
   fpocket-over-frames** — i.e. exactly the NR4A3 pipeline, generalized. **Honest novelty (the gap is real):**
   *predictors* (PocketMiner, CryptoSite) only say *where* a pocket might form — no opened structure, no
   druggability, no design-ready geometry; *static-pocket* DBs (DoGSite, CavityPlus) miss cryptic pockets by
   construction; the one deep-MD cryptic-pocket *campaign* at proteome scale (Bowman / Folding@home) was the
   **SARS-CoV-2** proteome, not curated human disease targets, and not a druggability-scored resource. A
   druggability-scored cryptic-pocket atlas for neglected disease targets does **not** appear to exist. **Feasibility
   crux = the compute wall** (NR4A3 alone was days of metadynamics; a proteome is impossible solo). Two
   resolutions: **(a) focused target class** — dozens of fusion-TF / orphan-NR rare-cancer drivers, deep
   per-target, each entry a genuine lead (feasible NOW; a clean *Scientific Data* / NAR-Database paper with
   NR4A3 as the worked exemplar); **(b) ride the cheap-ensemble wave** — generative equilibrium-ensemble models
   (BioEmu, AlphaFlow, subsampled-MSA AlphaFold) could collapse the per-target "open the pocket" cost from
   GPU-days to pennies, which is what makes the *proteome-scale* version stop being science-fiction (watched in
   `method-watch.md`). Same medical-integrity guardrail as 1–3: every entry is an **unvalidated hypothesis with
   calibrated confidence**, credible only if the pipeline demonstrably re-finds a held-out set of *known* cryptic
   sites (CryptoSite / PocketMiner benchmark). **Strategic caveat:** strictly post-first-two-papers; it is the
   classic scope-expansion that quietly eats months meant for the EMC lead program — scope now, build only once
   the degrader + ASO preprints are posted. *(An orthogonal PocketMiner cross-check on the NR4A3 LBD itself is
   being run now as a paper-strengthening step — task #15 — independent of this atlas idea.)*

## 🔄 Auto-captured field-scan advances (review + integrate into the board above)

Items here are NEW routes/advances not yet integrated into the curated route board above — review + fold in.
Dated + sourced; no fabrication. These are unvalidated leads with the same medical-integrity guardrail as the
rest of the board.

**Who actually appends here (checked 2026-08-03 against committed history, because the previous sentence was
wrong).** ⚠ *Superseded, retained: "Appended automatically by the weekly field-scan Routine (and manual
scans)."* The **weekly field-scan Routine has never appended anything** — every bullet below is dated
2026-07-13 and came from the manual catch-up whose own commit title is *"manual catch-up: automated Routine
failed to deliver"*, and `research/field-scan-log.md` has carried no entry since. Two writers are real:
**(a) a session doing a manual scan**, and **(b)** ⭑ **the reopening-trigger scan** —
[`scripts/trigger_scan.py`](../scripts/trigger_scan.py) via
[`.github/workflows/method-watch-triggers.yml`](../.github/workflows/method-watch-triggers.yml) — which
searches for the **specific named capabilities** that would reopen a parked route
([`method-watch-triggers.json`](method-watch-triggers.json)) and appends each hit **with the routes,
requirements and blockers it would reopen**, so a line here carries its consequence rather than just a paper.
Its bullets are prefixed with the trigger id and marked as machine-matched. ⚠ **A quiet week here is not
evidence that nothing landed** — CLAUDE.md §6 records that this repo's crons are throttled and need manual
dispatch; the run history that says whether the scan fired lives in
[`method-watch-trigger-scan.md`](method-watch-trigger-scan.md).

- **2026-07-13 — ★ NEW candidate route: bivalent fusion-TF "rewiring" / TCIP (Transcriptional Chemical-Induced
  Proximity).** Bivalent small molecules that *co-opt* a tumour-specific fusion TF (recruit a transcriptional
  effector) rather than degrading it — demonstrated on **EWSR1::FLI1** in Ewing sarcoma. Directly conceptually
  transferable to **EWSR1::NR4A3** (a fusion TF); a small-molecule route distinct from the LBD degrader and the
  ASO. ⚠ may warrant a new row on the route board — for human review.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC12851799/
- **2026-07-13 — Fusion-junction neoantigen immunotherapy: external validation for the (currently "hard")
  fusion-junction TCR/ImmTAC idea.** **Tecelra (afami-cel)** got FULL FDA approval for synovial sarcoma (age
  ≥12; ASCO 2026 update) — first engineered TCR-T for a fusion-driven sarcoma; plus fusion-derived public-
  neoantigen TCRs for **SYT-SSX** (synovial) and **EWSR1-WT1** (DSRCT) show fusion-junction TCRs CAN work in
  other FET/fusion sarcomas. Raises the prior on an EWSR1::NR4A3-junction TCR/ImmTAC (still gated by the weak-
  junction-pHLA problem noted on the board). https://www.mskcc.org/news/immunotherapy-clinical-trial-shows-promise-for-treating-rare-sarcomas
  · https://aacrjournals.org/cancerres/article/84/6_Supplement/6/738983 · https://pmc.ncbi.nlm.nih.gov/articles/PMC11821884/
- **2026-07-13 — ASO delivery advances (relevant to the fusion-junction ASO route's delivery gate).**
  Imaging-assisted tumour-targeted ASO delivery (https://pmc.ncbi.nlm.nih.gov/articles/PMC11503958/),
  MOF-nanoparticle ASO delivery (https://pubmed.ncbi.nlm.nih.gov/41712689/), and **AZD8701** (FOXP3 ASO) in a
  Phase-I solid-tumour trial — clinical precedent for systemic ASO in solid tumours
  (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11995004/). Chip away at the ASO route's one remaining gate.
- **2026-08-03 — trigger `TRG-COFOLD-TERNARY-ASSEMBLY` matched: A co-folder evaluated on ternary ASSEMBLY rather than per-chain pocket accuracy.** ⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** **Would reopen:** roadmap `V12`, `R10` · routes `RT-DEGRADER`, `RT-ANDGATE`, `RT-AF3-INTERFACE` · blockers `BLK-TERNARY-GEOMETRY`. Hit: *Drug-likeness defects drive carrier-free cyanine-PROTAC self-assembly for tumor-specific protein degradation* (J Control Release, 2026-07-29, MED/42526644) https://europepmc.org/article/MED/42526644 . If it holds: Re-run the ternary rebuild by the assembly route against the new predictor and re-grade V12; do NOT read a global-accuracy number as an assembly claim — check the paper reports an interface metric on held-out ternaries. Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json).
- **2026-08-03 — trigger `TRG-TERNARY-GEN-NO-SITES` matched: A ternary generator that does not require both binding sites to be supplied.** ⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** **Would reopen:** roadmap `R10`, `R9` · routes `RT-DEGRADER`, `RT-GLUE` · blockers `BLK-TERNARY-GEOMETRY`, `BLK-INDUCED-COMPLEX`. Hit: *TriGlue: a Biology-Inspired Generative Model for Generating Molecular Glue-Induced Ternary Complex* (arXiv, 2026-07-24, arXiv/2607.22143v1) http://arxiv.org/abs/2607.22143v1 . If it holds: Re-open R10 and re-run the three-paralogue ternary rebuild from a recorded SMILES; check explicitly whether the method requires site inputs before crediting it. Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json).
- **2026-08-03 — trigger `TRG-CRYPTIC-POCKET-PREDICTION` matched: Robust cryptic-pocket prediction — good enough to re-grade an undruggability prior without GPU MD.** ⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** **Would reopen:** roadmap `R4`, `R5` · routes `RT-DEGRADER`, `RT-MONOVALENT`, `RT-COVALENT-PROBE` · blockers `BLK-R4-BINDS`. Hit: *Computational strategies for allosteric drug discovery: from cryptic pocket detection to rational design* (Chem Commun (Camb), 2026-07-20, MED/42473809) https://europepmc.org/article/MED/42473809 . If it holds: Re-grade the LBD undruggability prior and say plainly that a prediction does not answer whether anything binds. Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json).
- **2026-08-03 — trigger `TRG-E3-RECRUITER-STRUCTURE` matched: A deposited PARTNER-FREE LIGANDED structure for one of the blocked E3 recruiters.** ⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** **Would reopen:** roadmap `R9`, `R12` · routes `RT-DEGRADER` · blockers `BLK-TERNARY-GEOMETRY`. Hit: *Structure-Guided Discovery of Novel Dual-Site FEM1B Ligands and Assessment of Their Use in Targeted Protein Degradation* (J Med Chem, 2026-07-15, MED/42456065) https://europepmc.org/article/MED/42456065 . If it holds: Re-run the recruiter downselect with the new structure staged; the test is partner-free liganded, not merely deposited. Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json).
- **2026-08-03 — trigger `TRG-GLUE-PROSPECTIVE-DESIGN` matched: A validated PROSPECTIVE molecular-glue design, or a glue-interface selectivity predictor.** ⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** **Would reopen:** roadmap `R7`, `R9`, `R10` · routes `RT-GLUE` · blockers `BLK-INDUCED-COMPLEX`, `BLK-PARALOGUE-DDG`. Hit: *TriGlue: a Biology-Inspired Generative Model for Generating Molecular Glue-Induced Ternary Complex* (arXiv, 2026-07-24, arXiv/2607.22143v1) http://arxiv.org/abs/2607.22143v1 . If it holds: Re-grade route 10 from 'watch, do not build'. A retrospective rationalisation of a found glue does NOT fire this trigger; the test is prospective. Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json).
- **2026-08-03 — trigger `TRG-VIRTUAL-CELL-NO-LINE` matched: A virtual-cell / perturbation foundation model that predicts dependencies for a disease with NO cell line.** ⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** **Would reopen:** routes `RT-SYNLETH-DEP`, `RT-ATR-ASSESS`, `RT-DEGRADER`, `RT-ASO` · blockers `BLK-NO-EMC-DATA`, `BLK-FUNCTIONAL-ACTIONABILITY`, `BLK-CLASS-INHERITANCE`. Hit: *Towards Principled Evaluation of Single-Cell Perturbation Prediction Models* (PPR, 2026-07-27, PPR/PPR1286571) https://europepmc.org/article/PPR/PPR1286571 . If it holds: Test EMC EWSR1::NR4A3 fusion-dependence in the new model AND state its held-out performance on diseases absent from its panel — a model that only works where data exists does not fire this trigger. Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json).
- **2026-08-03 — trigger `TRG-VIRTUAL-CELL-NO-LINE` matched: A virtual-cell / perturbation foundation model that predicts dependencies for a disease with NO cell line.** ⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** **Would reopen:** routes `RT-SYNLETH-DEP`, `RT-ATR-ASSESS`, `RT-DEGRADER`, `RT-ASO` · blockers `BLK-NO-EMC-DATA`, `BLK-FUNCTIONAL-ACTIONABILITY`, `BLK-CLASS-INHERITANCE`. Hit: *PerturbPFN: Probing the Limits of Synthetic Priors in Drug Perturbation Modelling* (arXiv, 2026-07-26, arXiv/2607.23447v1) http://arxiv.org/abs/2607.23447v1 . If it holds: Test EMC EWSR1::NR4A3 fusion-dependence in the new model AND state its held-out performance on diseases absent from its panel — a model that only works where data exists does not fire this trigger. Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json).
- **2026-08-03 — trigger `TRG-OLIGO-DELIVERY-TECH` matched: Oligonucleotide DELIVERY to non-hepatic SOLID TUMOURS — a technology or candidate.** ⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** **Would reopen:** routes `RT-ASO`, `RT-ASO-ASK`, `RT-B7H3` · blockers `BLK-DELIVERY`. Hit: *Green synthesized cobalt doped graphene quantum dots derived from Boswellia serrata for dual ligand targeted bioimaging and delivery of exemestane* (Discov Nano, 2026-07-17, MED/42467326) https://europepmc.org/article/MED/42467326 . If it holds: Name a concrete junction-oligo delivery CANDIDATE and re-grade the ASO route's dominant gate. Clinical precedent in a different solid tumour is a prior, not a solution for EMC. Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json).
- **2026-08-03 — trigger `TRG-OLIGO-DELIVERY-PREDICTOR` matched: An IN-SILICO oligonucleotide/nanoparticle tumour-delivery predictor.** ⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** **Would reopen:** routes `RT-ASO`, `RT-B7H3` · blockers `BLK-DELIVERY`. Hit: *Machine Learning Enables Rapid Prediction of Acid-Reducing Agent Drug Interactions: A Streamlined Complement to PBPK Modeling* (CPT Pharmacometrics Syst Pharmacol, 2026-08-01, MED/42538618) https://europepmc.org/article/MED/42538618 . If it holds: Score the B7-H3-targeted junction-siRNA/AOC design and re-grade ASO route feasibility, stating explicitly that the grade is computational. Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json).
- **2026-08-03 — trigger `TRG-OLIGO-DELIVERY-PREDICTOR` matched: An IN-SILICO oligonucleotide/nanoparticle tumour-delivery predictor.** ⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** **Would reopen:** routes `RT-ASO`, `RT-B7H3` · blockers `BLK-DELIVERY`. Hit: *Predicting First-in-Human Pharmacokinetics: Comparative Evaluation of Standard PBPK, High-Throughput PBPK, and Machine Learning* (Mol Pharm, 2026-08-01, MED/42418317) https://europepmc.org/article/MED/42418317 . If it holds: Score the B7-H3-targeted junction-siRNA/AOC design and re-grade ASO route feasibility, stating explicitly that the grade is computational. Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json).
- **2026-08-03 — trigger `TRG-ASO-EFFICACY-ACCESSIBILITY` matched: An improved ASO/siRNA efficacy + target-site-accessibility predictor.** ⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** **Would reopen:** routes `RT-ASO`. Hit: *Evolution of peptide-mediated siRNA delivery - from early design to next generation platform* (Nanomedicine (Lond), 2026-08-01, MED/42541443) https://europepmc.org/article/MED/42541443 . If it holds: Re-rank the junction designs for potency and replace the accessibility proxy. Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json).
- **2026-08-03 — trigger `TRG-ASO-EFFICACY-ACCESSIBILITY` matched: An improved ASO/siRNA efficacy + target-site-accessibility predictor.** ⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** **Would reopen:** routes `RT-ASO`. Hit: *Structural Optimization of Guanidinium-Linked Morpholino Phosphorodiamidate Morpholino Oligonucleotide Chimeras to Improve &lt;i&gt;In Vitro&lt;/i&gt; Antisense Efficacy* (Bioconjug Chem, 2026-07-21, MED/42482424) https://europepmc.org/article/MED/42482424 . If it holds: Re-rank the junction designs for potency and replace the accessibility proxy. Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json).
- **2026-08-03 — trigger `TRG-JUNCTION-PHLA` matched: A validated way to make a WEAK fusion-junction peptide-HLA into a target.** ⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** **Would reopen:** routes `RT-TCR-IMMTAC`, `RT-JUNCTION-NEOANTIGEN`, `RT-VACCINE` · blockers `BLK-ANTIGEN-COLD`. Hit: *Quantum convolutional HLA immunogenic peptide prediction (Q-CHIPP): Next-generation neoantigen prediction with quantum neural network* (Sci Adv, 2026-07-24, MED/42497272) https://europepmc.org/article/MED/42497272 . If it holds: Re-grade the three junction-antigen routes together and state whether the evidence is about presentation, about abundance, or only about a different fusion. Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json).
- **2026-08-03 — trigger `TRG-JUNCTION-PHLA` matched: A validated way to make a WEAK fusion-junction peptide-HLA into a target.** ⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** **Would reopen:** routes `RT-TCR-IMMTAC`, `RT-JUNCTION-NEOANTIGEN`, `RT-VACCINE` · blockers `BLK-ANTIGEN-COLD`. Hit: *Benchmarking sequence-based and AlphaFold-based methods for pMHC-II binding core prediction: distinct strengths and consensus approaches* (BMC Med Genomics, 2026-07-22, MED/42509551) https://europepmc.org/article/MED/42509551 . If it holds: Re-grade the three junction-antigen routes together and state whether the evidence is about presentation, about abundance, or only about a different fusion. Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json).
- **2026-08-03 — trigger `TRG-NR4A3-DIRECT-MATTER` matched: Any direct chemical or biological matter against NR4A3 or the EWSR1::NR4A3 fusion.** ⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** **Would reopen:** roadmap `R4` · routes `RT-DEGRADER`, `RT-MONOVALENT`, `RT-COVALENT-PROBE`, `RT-TCIP` · blockers `BLK-R4-BINDS`. Hit: *NOR-1 as a Context-Dependent Rheostat of Vascular and Cardiac Remodeling* (FASEB J, 2026-08-01, MED/42522710) https://europepmc.org/article/MED/42522710 . If it holds: Fold into the relevant route memo IMMEDIATELY and re-check R4. Verify the compound is against NR4A3 rather than a family-wide pan-NR4A tool before crediting it. Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json).
- **2026-08-03 — trigger `TRG-EMC-EXPRESSION-DATASET` matched: A public EMC / FET-fusion-sarcoma EXPRESSION or functional-genomics dataset.** ⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** **Would reopen:** routes `RT-B7H3`, `RT-CART-SURFACE`, `RT-PPARG-DOWNSTREAM`, `RT-TCRT-CTA`, `RT-SYNLETH-DEP`, `RT-TRABECTEDIN-PPARG` · blockers `BLK-NO-EMC-DATA`, `BLK-CLASS-INHERITANCE`. Hit: *Oncological Outcomes and Prognostic Factors in Soft Tissue Sarcoma of Children, Adolescents, and Young Adults: A Retrospective Single-Center Cohort Study* (Cancers (Basel), 2026-07-19, MED/42512391) https://europepmc.org/article/MED/42512391 . If it holds: Re-grade the surface-antigen and repurposing routes against the actual EMC data, and check FIRST whether the dataset contains EMC itself or only a related fusion sarcoma — the whole point of this trigger is the difference. Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json).
- **2026-08-03 — trigger `TRG-EMC-EXPRESSION-DATASET` matched: A public EMC / FET-fusion-sarcoma EXPRESSION or functional-genomics dataset.** ⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** **Would reopen:** routes `RT-B7H3`, `RT-CART-SURFACE`, `RT-PPARG-DOWNSTREAM`, `RT-TCRT-CTA`, `RT-SYNLETH-DEP`, `RT-TRABECTEDIN-PPARG` · blockers `BLK-NO-EMC-DATA`, `BLK-CLASS-INHERITANCE`. Hit: *Predicting Interval Pulmonary Metastasis in Extremity Soft Tissue Sarcoma Treated with Preoperative Radiotherapy: A Risk-Stratified Cohort Study of 378 Patients* (JB JS Open Access, 2026-07-13, MED/42428037) https://europepmc.org/article/MED/42428037 . If it holds: Re-grade the surface-antigen and repurposing routes against the actual EMC data, and check FIRST whether the dataset contains EMC itself or only a related fusion sarcoma — the whole point of this trigger is the difference. Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json).
