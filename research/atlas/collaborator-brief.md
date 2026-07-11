# EMC treatment research — collaborator brief

> **A two-page, evidence-backed package for a sarcoma wet-lab or clinical collaborator.** It states
> two ready-to-run programs, exactly what we ask a partner to do, and exactly what we bring. Every
> claim traces to `research/atlas/` (provenance-checked; `node research/atlas/build.mjs`). This is a
> research proposal, not a treatment recommendation; nothing here is established EMC therapy.

## Who we are and what this is

An independent computational researcher has built the **EMC Open Target & Drug Atlas** — the first
reproducible, version-controlled integration of the fragmented extraskeletal myxoid chondrosarcoma
(EMC) evidence base (3 modern patient-derived models, 2 drug screens, the clinical cohorts, public
expression, and public dependency databases), with a transparent evidence score and honest
provenance. Two programs are ready to hand to a lab. We provide all computation, analysis, and
manuscript support; we ask a partner to provide the cells and the assays.

---

## Program 1 (best experimental bet) — the proteostasis–chromatin vulnerability

**Hypothesis.** NR4A3-fusion-driven transcription creates dependence on protein quality control and
chromatin maintenance; inhibiting two complementary nodes selectively collapses the fusion program.

**Why it's the strongest preclinical signal (all in `claims.json` / `drug_screens.json`):**
- Two independent modern screens nominate *different nodes of one system*: the **USZ** models
  (EWSR1 + TAF15) — proteasome (**carfilzomib**, strongest single agent) + HSP90 (**PU-H71**); the
  **NCC-EMC1-C1** model — two HDAC inhibitors (**panobinostat + romidepsin**, primary-abstract
  confirmed). Two HDAC hits in one model ⇒ the effect tracks the *target*, not one chemical.
- FET-fusion sarcomas plausibly impose a high-output transcriptional state → proteostasis load.

**What the atlas already corrected (so a partner doesn't chase ghosts):** HDM201/MDM2–MDM4 did **not**
survive verification as a USZ hit (demoted to hypothesis); the carfilzomib+doxorubicin combination is
*additive **and** synergistic in **both** models* (venetoclax also in the panel), not a one/other split.

**The ask — a class-vs-compound validation** (full protocol: `evidence_score.json → validation_panel`).
Test ≥2 members of each class so effects attribute to the target, at concentrations overlapping
achievable human free exposure (see the compound–exposure table). Minimum readouts: short + clonogenic
viability, apoptosis, **fusion-protein abundance**, a target-engagement PD marker (proteasome activity /
histone acetylation / HSP70 induction), 6 h + 24 h RNA, and Bliss/Loewe/ZIP combination matrices with
washout. Models: USZ20-EMC1 (EWSR1), USZ22-EMC2 (TAF15), NCC-EMC1-C1, + non-malignant mesenchymal and
fusion-positive non-EMC sarcoma controls.

**Go/no-go (pre-registered):** activity in ≥2 EMC models; not restricted to one fusion partner without
a biomarker; target engagement shown; effective concentration compatible with achievable exposure;
selectivity margin over normal controls; a combination that improves *depth/durability*, not just a
short-term curve.

---

## Program 2 (best clinically-anchored bet) — the EWSR1-vs-TAF15 antiangiogenic biomarker

**Hypothesis.** EWSR1::NR4A3 and TAF15::NR4A3 establish different vascular/stromal programs; one
confers sensitivity to VEGFR/PDGFR/RET-active TKIs, the other primary resistance.

**Why it's the most credible clinical signal (all primary-abstract confirmed, `citations.json`):**
- **Pazopanib** phase 2 (Stacchiotti 2019): ORR 18% (95% CI 1–36), median PFS 19 mo; responders EWSR1::NR4A3.
- **Sunitinib** (Stacchiotti 2014): 6 PR/2 SD/2 PD — and the paper states in-text that **responders
  expressed EWSR1::NR4A3 while refractory cases carried TAF15::NR4A3** (the load-bearing differential).
- **IMMUNOSARC II** (ASCO 2025): sunitinib+nivolumab, 6-mo PFS 77%, median PFS 13.2 mo.
- Independent reprocessing (GSE24369, this atlas) reproduces **RET** elevation in EMC (AUC 0.86) — a
  marker of the fusion state, *not* proven dependency.

**The ask.** (1) A response-linked, molecularly-annotated cohort scored with **growth-rate-adjusted**
endpoints (pre- vs on-treatment growth, growth-modulation index, time-to-next-treatment) — never
stable-disease alone, because untreated EMC is indolent. (2) Mechanistic validation in **co-culture**
(EMC + endothelial/fibroblast/macrophage), phosphoproteomics after short TKI exposure, and CRISPR/RNAi
of the top implicated kinases/guidance receptors — angiogenic sensitivity will not reproduce in
tumor-cell monoculture. See `antiangiogenic-mechanism.md` for the kinome-level TKI comparison and the
response-linked common data model / CRF.

**Go/no-go:** a biomarker must predict *growth-rate-adjusted* benefit, survive leave-one-patient-out,
not be a mere proxy for EWSR1-vs-TAF15 unless that itself is validated, and be measurable on archival tissue.

---

## What we bring vs what we ask

| We provide (computational, $0 to the partner) | We ask the partner to provide |
|---|---|
| The full atlas: sample registry, evidence claims with provenance, compound–target–exposure table, evidence score | The three EMC models (or a subset) + appropriate controls |
| Pre-registered analysis + statistical plan, plate-map-ready panels, go/no-go criteria | The wet-lab assays in the two protocols above |
| Reprocessed public expression + fusion-junction antigen computation, all reproducible | Molecular annotation (fusion partner/breakpoint) per sample |
| Manuscript drafting, figures, and data-analysis of the new results | Named senior/clinical authorship and institutional governance |

## Honest limitations (stated up front)
- **No wet lab on our side** — this package is explicitly designed to be *executed by a partner*.
- The three modern EMC models are the entire modern preclinical base; TAF15 has a single model (USZ22-EMC2).
- USZ screen hit identities are secondary-source (Bangerter full text not open-access); IC50s not yet retrieved.
- Nearly all systemic-therapy evidence originates from **one group** (Stacchiotti / European sarcoma
  network) — the obvious first clinical collaborator, and a real concentration limitation.
- Every clinical number carries a `verification_level`; the atlas reports what did *not* survive verification.

**Contact / next step:** we can share the full atlas repository, a tailored plate map, and a draft figure
set on request, and adapt the panel to the models and assays a partner already runs.
