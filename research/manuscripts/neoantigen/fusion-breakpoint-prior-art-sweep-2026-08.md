---
id: DOC-FUSION-BREAKPOINT-SWEEP-2026-08
title: Looking backward through the hole — the first run of the fusion-breakpoint watch row
level: L4
kind: memo
status: live
canonical_for: []
purpose: Report what the fusion-BREAKPOINT-directed immunotherapy watch row surfaces on its first ever execution, with no date limit, having been added on 2026-08-24 to close a gap no existing row could match.
scope: Fusion-breakpoint-directed immunotherapy prior art ONLY. Not a route re-grade and not a manuscript edit.
audience: [maintainers, autonomous research agents]
date: 2026-08-24
last_verified: 2026-08-24
---
# Looking backward through the hole

**Why this exists.** On 2026-08-24 a watch row was added for fusion-BREAKPOINT-directed immunotherapy,
because no existing literature row could match such a paper — the only FET row required a *model* word
(`cell line`/`organoid`/`PDX`/…) alongside the disease term, so it caught new experimental systems and
structurally could not catch a therapeutic result in the same disease. Adding the row closed the hole
**going forward**. The npj Ewing vaccine paper had been found by accident, through a news feed; the SYT-SSX
trials surfaced only because chasing that one paper dragged its neighbourhood along. That is luck, not a
search. This is the search: the new row's query, widened to the sibling fusion sarcomas, run with **no date
limit** for the first time. 161 records; 14 titles pair a breakpoint/fusion term with an immunology term.

⚠ **Identifier provenance:** every record below is copied from
[`research/literature/fusion-breakpoint-sweep-2026-08-24.json`](../../literature/fusion-breakpoint-sweep-2026-08-24.json),
itself copied from a committed Europe PMC fetch product. Nothing here was typed from recollection.
⚠ **These are TITLES AND ABSTRACTS-level reads.** Where a claim about a paper's contents appears below it is
flagged; the full texts have not been read.

## 1 · The one that bears on the manuscript's weakest point

**Endogenous T cell responses to fusion-derived neoantigens in pediatric acute leukemias.** *Leukemia*,
PMID **40707674**, PMC**12463655**, doi:10.1038/s41375-025-02710-7. **Open access.**

The vaccine paper's sharpest self-criticism (its B2) is that a vaccination study measures T-cell responses to
peptides **that were injected**, which is not evidence that the same sequence is naturally processed out of
the endogenous fusion protein and displayed on a tumour cell. **An *endogenous* response is that missing
evidence class** — an immune response arising without anyone administering a peptide implies the epitope was
processed and presented by the tumour itself.

⛔ **This is a lead, not a conclusion.** It is a different fusion, a different disease, and a haematological
malignancy rather than a solid tumour. Whether it supports B2, partially answers it, or is irrelevant to it
depends entirely on what the paper actually measured, and **the full text has not been read**. It is open
access, so reading it costs nothing. **That is the single highest-value next read in this file.**

## 2 · An entire prior clinical programme class the repository had nothing on

Fusion-breakpoint peptide vaccination has clinical history in **leukaemia**, not only in sarcoma:

- **Synthetic tumor-specific breakpoint peptide vaccine in patients with chronic myeloid leukemia and minimal
  residual disease: a phase 2 trial.** *Cancer*, PMID **19536894**, PMC**5534348**. A **Phase 2** trial of a
  breakpoint peptide vaccine — a larger clinical study of this modality than anything previously cited here.
- **Identification of a novel p190-derived breakpoint peptide suitable for peptide vaccine therapeutic
  approach in Ph+ acute lymphoblastic leukemia patients.** *Leukemia Research and Treatment*,
  PMID **23198152**, PMC**3505930**. **Open access.**

⚠ **Read across with care.** BCR-ABL is a fusion breakpoint, so the *antigen* logic transfers. The disease
does not: a circulating leukaemic cell is not an EMC nodule, and the delivery and microenvironment problems
that dominate this repo's solid-tumour routes do not arise there. The value is that the modality has a
longer and larger clinical record than the sarcoma trials alone suggest — in **both** directions, since
outcomes are not read here.

## 3 · Directly on the route's named blocker

**Harnessing gene fusion-derived neoantigens for 'cold' breast and prostate tumor immunotherapy.**
*Immunotherapy*, PMID **36043380**, doi:10.2217/imt-2022-0081.

`RT-VACCINE` is parked on `BLK-ANTIGEN-COLD`. This paper's stated subject is fusion-derived neoantigens
**for cold tumours specifically** — the blocker by name. Whether it offers anything actionable is unknown
until read; the title is the only thing established here.

## 4 · What this says about the watch, beyond the papers

The row was added to stop a repeat. Its first backward run returned **a Phase 2 trial of this exact modality
and a paper addressing the route's named blocker** — neither of which any prior row could reach. So the gap
was not one missed paper in August 2026; **it was a standing blind spot over the whole prior literature**,
and the two months of missing clinical news merely exposed it.

⛔ **Nothing here re-grades a route, and nothing here has been added to any manuscript.** The manuscript's
prior-art additions were made separately and are already committed; this file is a queue of reads, best first:
1. PMID 40707674 full text — does it evidence endogenous processing and presentation? (open access)
2. PMID 19536894 — what did a Phase 2 breakpoint vaccine actually produce?
3. PMID 36043380 — anything usable against `BLK-ANTIGEN-COLD`?
