# EMC treatment research — collaborator brief

> **A short, evidence-backed proposal for a sarcoma wet-lab or clinical collaborator.** It states two
> candidate programs, what we would ask a partner to do, and what we would contribute. Every claim
> traces to `research/atlas/` with a source and a verification level. This is a research proposal, not a
> treatment recommendation; nothing here is established EMC therapy, and nothing has been validated in EMC.

## Who we are and what this is

An independent, unaffiliated researcher (Tristan McRae) has built the **EMC Open Target & Drug Atlas** —
a versioned, curated synthesis of *identified public* evidence on extraskeletal myxoid chondrosarcoma
(NR4A3-rearranged EMC) as of July 2026, with a transparent triage heuristic. It is **not** a systematic
review and does not claim to capture everything known. It draws on the 3 modern patient-derived models,
the 2 published drug screens, the clinical reports, public expression, and public dependency databases.
We would contribute computational analysis and drafting; we would ask a partner to provide models/tissue
and run the assays. **Authorship would follow substantive contribution per standard (e.g. ICMJE/COPE)
criteria — it is not something we ask a partner to "supply."**

---

## Program 1 (highest-ranked preclinical, by an unvalidated triage heuristic) — a proteostasis/chromatin hypothesis

**Hypothesis (unproven).** NR4A3-fusion-driven transcription *may* create dependence on protein quality
control and/or chromatin maintenance. Note: "proteostasis-chromatin" groups biologically distinct
mechanisms (proteasome, HSP90, HDAC) under one label — a convenience framing, not a demonstrated shared
dependency.

**Why it ranks highest by this heuristic (all in `claims.json` / `drug_screens.json`):**
- Two independent modern screens nominate hits: the **USZ** models (EWSR1 + TAF15) — proteasome
  (**carfilzomib**) + HSP90 (**PU-H71**) — but note these specific compound identities are
  **secondary-source / unconfirmed** (the paper's abstract does not name them); and the **NCC-EMC1-C1**
  model — two HDAC inhibitors (**panobinostat + romidepsin**, primary-abstract confirmed). Two HDAC
  inhibitors active in one model is *consistent with* class-level HDAC activity but does **not** prove
  HDAC caused the effect (single model, no genetic perturbation).
- FET-fusion sarcomas *plausibly* impose a high-output transcriptional state → proteostasis load (a rationale, not evidence).

**What the atlas already corrected (so a partner doesn't chase ghosts):** HDM201/MDM2–MDM4 did **not**
survive verification as a USZ hit (demoted to hypothesis); the carfilzomib+doxorubicin combination is
reported as *additive and synergistic in both models* (venetoclax also in the panel), not a one/other
split; and the USZ single-agent identities are secondary-source pending author/full-text confirmation.

**The ask — a class-vs-compound validation** (proposal: `evidence_score.json → validation_panel`).
Test ≥2 members of each class so an effect can be attributed toward a target class. **The proposed
concentration ranges still require final pharmacology and primary-source review — this is not an
"exposure-matched" or "ready-to-run" panel** (`panel-exposure.json` holds verbatim FDA-label PK quotes,
not a completed active-vs-unbound-exposure table). Minimum readouts: short + clonogenic
viability, apoptosis, **fusion-protein abundance**, a target-engagement PD marker (proteasome activity /
histone acetylation / HSP70 induction), 6 h + 24 h RNA, and Bliss/Loewe/ZIP combination matrices with
washout. Models: USZ20-EMC1 (EWSR1), USZ22-EMC2 (TAF15), NCC-EMC1-C1, + non-malignant mesenchymal and
fusion-positive non-EMC sarcoma controls.

**Go/no-go (pre-registered):** activity in ≥2 EMC models; not restricted to one fusion partner without
a biomarker; target engagement shown; effective concentration compatible with achievable exposure;
selectivity margin over normal controls; a combination that improves *depth/durability*, not just a
short-term curve.

---

## Program 2 (highest-ranked clinically-anchored) — a possible EWSR1-vs-TAF15 antiangiogenic association

**Hypothesis (unproven).** EWSR1::NR4A3 and TAF15::NR4A3 *may* establish different vascular/stromal
programs. Small early reports suggest a **possible association** between fusion subtype and TKI response
that **requires prospective validation** — not an established biomarker, and not a demonstration that a
subtype "confers" sensitivity or resistance.

**The clinical signal (`citations.json`):**
- **Pazopanib** phase 2 (Stacchiotti 2019): ORR 18% (95% CI 1–36), median PFS 19 mo; responders EWSR1::NR4A3.
- **Sunitinib** (Stacchiotti 2014): 6 PR/2 SD/2 PD — the paper reports that responders expressed
  EWSR1::NR4A3 while refractory cases carried TAF15::NR4A3 (small N, one group; an association, not proof).
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

## What we would contribute vs what a partner would provide

| We would contribute (computational) | A partner would provide |
|---|---|
| The atlas: sample registry, cited evidence claims, compound–target table, the triage heuristic | EMC models (or a subset) + appropriate controls |
| A pre-registered analysis + statistical plan, a proposed panel, and go/no-go criteria | The wet-lab assays in the two proposals above |
| Reprocessed public expression + fusion-junction *predictions*, reproducible per the documented workflows | Molecular annotation (fusion partner/breakpoint) per sample |
| Drafting, figures, and analysis of new results (as time allows — not an open-ended labor commitment) | Institutional governance (consent/ethics/data) |

**Authorship & governance.** Authorship on any resulting work would follow substantive intellectual or
experimental contribution, drafting/revision, approval, and accountability (ICMJE/COPE) — for everyone,
including us. We do not ask a partner to grant authorship, affiliation, or endorsement, and we do not
imply any that do not yet exist. Any grant application would be led by an eligible institutional PI under
the funder's rules.

## Honest limitations (stated up front)
- **No wet lab on our side** — this package is explicitly designed to be *executed by a partner*; nothing has been validated in EMC.
- The three modern EMC models are the entire modern preclinical base; TAF15 has a single model (USZ22-EMC2). **No EMC cell line exists in DepMap — all dependency reads are non-EMC surrogates.**
- USZ screen hit identities are **secondary-source/unconfirmed** (Bangerter full text not open-access); IC50s not retrieved; the proposed panel's concentrations still need final pharmacology.
- Nearly all systemic-therapy evidence originates from **one group** (Stacchiotti / European sarcoma network).
- The evidence score is a **judgment-based triage heuristic**, not calibrated probabilities. Sources carry a `verification_level`; the atlas reports what did *not* survive verification.

**Contact / next step:** we can share the full atlas repository, a tailored plate map, and a draft figure
set on request, and adapt the panel to the models and assays a partner already runs.
