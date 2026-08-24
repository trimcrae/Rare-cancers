---
id: DOC-METHOD-WATCH-BACKFILL-2026-08
title: Backfill triage — the clinical news nobody was watching, 2026-06-15 → 2026-08-24
level: L4
kind: memo
status: live
canonical_for: []
purpose: Curated triage of the one-off backfill sweep run after the clinical/treatment-news watch landed, covering the ~2 months in which neither automated layer was reading clinical news.
scope: Clinical/treatment news and trial-registry movement ONLY. Does NOT cover the field-scan Routine's other scopes (GPU market, model policy, library releases), which were also unread in this window.
audience: [maintainers, autonomous research agents]
date: 2026-08-24
last_verified: 2026-08-24
---
# Backfill triage — clinical news, 2026-06-15 → 2026-08-24

**Why this exists.** The clinical/treatment-news watch landed 2026-08-24. Before it, the newsletter had no
source that could carry a readout, an approval or a program halt, and the weekly field-scan Routine that was
supposed to cover the same ground by web search has delivered nothing since 2026-07-13. Both layers were
blind for roughly two months. The raw sweep is
`research/method-watch-backfill.md` on the **`method-watch-cache`** branch (794 distinct headlines, 6 news
rows × 5 slices, 0 failed queries, plus a 4-row registry sweep). This file is the triage of it.

⚠ **EVIDENCE GRADE IS MARKED PER ITEM AND IS NOT UNIFORM.**
**[VERIFIED]** = traced to the primary record with an identifier. **[PRESS]** = a dated news headline and
nothing more — reported, not verified, no identifier, and **not citable** (CLAUDE.md §7). A [PRESS] line
records *that something was reported on a date*, which is all a news feed can establish.

⚠ **AND THIS IS A RECONSTRUCTION, NOT A RECORDING.** Google News ranks and caps per query and indexes what
is reachable *today*; the sweep lists at most 12 per slice per row against up to 30+ available. **Absence
here is not evidence that nothing happened.** Where a row says "and N more not listed", it means exactly that.

---

## 1 · The finding that matters most

**[VERIFIED] An off-the-shelf EWSR1–FLI1 *fusion-breakpoint* peptide vaccine produced durable human
immunologic responses in metastatic Ewing sarcoma.**
*Durable clinical and immunologic response to an off-the-shelf EWSR1-FLI1 peptide vaccine in metastatic Ewing
sarcoma.* **npj Precision Oncology**, PMID **42570981**, DOI **10.1038/s41698-026-01642-4**.
⚠ *The news feed attributed this to "Nature"; it is npj Precision Oncology, a Nature-portfolio journal. The
identifier above comes from the Europe PMC fetch (`literature/ewsr1-fli1-peptide-vaccine/_index.json` on
`literature-cache`), not from the headline.*

**Why it outranks everything else here:** this is **this repository's junction-vaccine route's exact
modality, in a sibling FET fusion, with human data.** An off-the-shelf multi-peptide vaccine spanning the
type 1 EWSR1–FLI1 breakpoint; de novo polyfunctional **CD4⁺** T-cell responses against **all four**
fusion-derived peptides, first detected around month 7 and persisting beyond two years.
`research/modalities/vaccine-construct.json` proposes precisely this design class for EWSR1::NR4A3 — a
`lead_public_construct`, off-the-shelf, with a CD4 epitope carried in native junction context.

⛔ **It is a single patient.** n=1, after multimodal therapy, with GM-CSF and topical imiquimod as adjuvants.
It is a proof that the class can raise durable junction-specific T-cell immunity in a human; it is **not**
efficacy, and the headline word "clinical" must not be allowed to inflate into one.

**Owed action — for trimcrae, not to be taken unilaterally.** The aiXiv vaccine paper
(`aixiv.260822.000005`) is under an hourly revision Routine. This paper is the closest prior art its central
premise has, and adding it is a substantive edit to a **named** manuscript mid-iteration — CLAUDE.md §3
territory, and a live collision risk. **Raised, not applied.**

## 2 · Prior art the repository never had

Surfaced by the same Europe PMC fetch. **None of these PMIDs appears anywhere in this repository**, and the
neoantigen manuscripts reach synovial sarcoma only through TCR-T (afami-cel, NY-ESO-1) — never through the
junction-**vaccine** work, which is the matching modality.

- **[VERIFIED]** *SYT-SSX breakpoint peptide vaccines in patients with synovial sarcoma: a study from the
  Japanese Musculoskeletal Oncology Group.* Cancer Science, PMID **22726592**.
- **[VERIFIED]** *Phase I vaccination trial of SYT-SSX junction peptide in patients with disseminated
  synovial sarcoma.* J Transl Med, PMID **15647119**.
- **[VERIFIED]** *Vaccination using peptides spanning the SYT-SSX tumor-specific translocation.* Expert Rev
  Vaccines, PMID **23252384**.
- **[VERIFIED]** *Immunogenic neoantigens derived from gene fusions stimulate T cell responses.* Nature
  Medicine, PMID **31011208**.
- **[VERIFIED]** *Routine EWS Fusion Analysis in the Oncology Clinic to Identify Cancer-Specific Peptide
  Sequence Patterns That Span Breakpoints in Ewing Sarcoma and DSRCT.* Cancers, PMID **36900411**.

★ **This is a prior-art gap, not a news gap, and it predates the window** — the SYT-SSX junction-vaccine
trials are the only previous clinical programme of this modality and are over a decade old. A backfill of
*news* found them only because chasing one 2026 paper pulled its neighbourhood in with it.

## 3 · Route-relevant items, by route

**Junction-vaccine route (RT-VACCINE).** Beyond §1:
- **[PRESS]** 2026-08-19 — Merck/Moderna INTerpath-001: intismeran autogene + pembrolizumab met RFS and DMFS
  in resected stage IIB–IV melanoma; reported as the first positive Phase 3 for an individualized neoantigen
  therapy. *Already handled — this is the item that started the whole episode.*
- **[PRESS]** 2026-06-15 — Elicio: Phase 2 AMPLIFY-7P missed; company pinned hopes on a post-hoc signal.
  ⚠ **A negative, and it cuts against §1's direction:** a shared/off-the-shelf peptide vaccine failing where
  an individualized mRNA approach succeeded is the comparison this route most needs to take seriously.
- **[PRESS]** 2026-06-26 — Zelluna: Phase II Dovacc trial did not meet its primary endpoint.
- **[PRESS]** 2026-07-16 → 08-07 — KRAS peptide vaccine in high-risk individuals reported to trigger immune
  responses (reported as 18 of 20 patients). Shared-neoantigen, prevention setting.
- **[PRESS]** 2026-07-23 — Infinitopes dosed first patient with an "off-the-shelf" therapeutic cancer vaccine.

**ASO / junction-oligo route — the gate is delivery.**
- **[PRESS]** 2026-08-11 — a cellular delivery route for antisense therapies reported (multiple outlets).
  Directly on this route's dominant blocker; worth reading the primary source.
- **[PRESS]** 2026-07-29 — Silexion initiated a Phase 2/3 of SIL204 in locally advanced pancreatic cancer.
- **[PRESS]** 2026-08-11/21 — Silence Therapeutics reported positive siRNA results in a rare blood cancer.
- **[VERIFIED-registry]** NCT — *EphA2 siRNA in Advanced or Recurrent Solid Tumors* (Phase 1), record updated
  2026-07-21. An siRNA with a solid-tumour indication actually on the registry.

**Degrader route.**
- **[PRESS]** 2026-07-07 / 08-04 — vepdegestrant (Veppanu) reported approved by FDA and described as the
  first PROTAC cancer therapy. ⚠ *Company attribution varied across outlets; not asserted here.*
- **[PRESS]** 2026-08 — a CELMoD reported to receive accelerated FDA approval in multiple myeloma.
- **[PRESS]** 2026-07-01 — Roche/Nurix collaboration on the BTK degrader bexobrutideg.
- **[VERIFIED-registry]** Degrader trials moving in the window include BGB-16673, NX-5948, BG-75098,
  BMS-986365.

**Sarcoma / disease area.**
- **[PRESS]** 2026-06-22/29 — afami-cel (TECELRA) reported to receive **full** FDA approval in advanced
  synovial sarcoma, indication expanded to patients 12 and older. ⚠ A translocation-driven sarcoma getting a
  full engineered-cell-therapy approval is the strongest immunotherapy precedent in this window for a
  fusion-driven sarcoma, and it is the disease closest to EMC in the portfolio's reasoning.
- **[PRESS]** 2026-07-14 — selpercatinib granted traditional approval for RET fusion-positive solid tumours.

## 4 · The two structural blind spots this exposed

1. **No clinical source at all** — fixed 2026-08-24; see the section comment in `scripts/method-watch.mjs`.
2. **No literature row for fusion-breakpoint THERAPEUTICS.** The only FET row required a *model* word
   (`cell line`/`organoid`/`patient-derived`/`xenograft`/`PDX`/`model`) alongside the disease term, so §1's
   paper could not match it — it catches new experimental *systems* and structurally cannot catch a
   *therapeutic* result in the same disease. Fixed the same day by the
   `fusion-BREAKPOINT-directed immunotherapy in FET / translocation sarcomas` row.
   ⚠ **This one is worse than the first**, because the literature watch was running the whole time and
   therefore looked like coverage.

## 5 · What this sweep does NOT cover

The field-scan Routine's scope was wider than clinical news: **GPU-market pricing, frontier-model policy
changes (the Fable bio-restriction watch), and in-silico library releases** (OpenFE, OpenMM, RDKit, Boltz…).
All were unread for the same period and are **not** backfilled here. Stated so this file is not mistaken for
full coverage of the gap.
