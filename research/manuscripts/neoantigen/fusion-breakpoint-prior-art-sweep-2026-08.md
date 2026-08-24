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
⚠ **Reading depth is per item.** §1 is a **full-text read** from the committed fetch product. Everything
else is titles-and-abstracts level, flagged as such where a claim about contents appears.

## 1 · READ. Endogenous, tumour-processed fusion-breakpoint neoepitopes in humans

**Endogenous T cell responses to fusion-derived neoantigens in pediatric acute leukemias.** *Leukemia*,
PMID **40707674**, PMC**12463655**, doi:10.1038/s41375-025-02710-7. Open access; **full text read** from the
committed fetch product `literature/fusion-breakpoint-immunotherapy-sweep/PMC12463655.txt`.

**What it establishes, and why it is the evidence class this manuscript said was missing.** The vaccine
paper's sharpest self-criticism (B2) is that a vaccination study measures responses to peptides **that were
injected**, which is not evidence the sequence is naturally processed from the endogenous fusion protein and
displayed on a tumour cell. This study never vaccinates anyone. T cells were expanded from patient **bone
marrow**, co-cultured with **autologous leukaemic blasts**, and the reactive population sorted on activation
markers (4-1BB on CD8; 4-1BB/OX40 on CD4). Reactivity therefore arose against antigen the tumour itself
processed and presented. Reactive TCRs were then cloned and tested against the **fusion sequence versus
wild-type** on patient-matched HLAs in several presentation systems (patient APCs, K562, 293T-CIITA), so
fusion specificity is established rather than assumed:

- **KMT2A::AFF1** (breakpoint KMT2A exon 10 / AFF1 exon 4) — restricted to **HLA-DPA1\*02:01/DPB1\*01:01**
- a second KMT2A::AFF1 (KMT2A exon 10 / AFF1 exon 5) — restricted to **HLA-DQA1\*03:03/DQB1\*03:01**
- **PICALM::MLLT10** — restricted to **HLA-B\*51:01**, from a CD8 clone

One KMT2A::AFF1-specific TCR also improved survival in mice engrafted with that patient's own blasts.

⚠ **A CONVERGENCE WORTH NOTICING, AND IT BEARS ON B4.** Two of the three fusion-specific restrictions
above are **class II**, and the 2026 Ewing breakpoint-vaccine case's only de novo response was **CD4+**.
Three independent lines, three different fusions, and the class II arm carries the signal in most of them.
The vaccine paper treats class II as the lesser result; the accumulating human evidence does not support
that ranking. This repo's own `lead_public_construct` carries a strong class II epitope, so the point is
not academic. ⛔ Three observations is a pattern to test, **not** a rule — say it that way.

⛔ **WHAT IT DOES NOT ESTABLISH, and the first limit is the authors' own.** They attribute the finding partly
to anatomy: *"Leukemia is frequently found in tissues where T cells reside, and this proximity is conducive
for frequent engagement between T cells and leukemic blasts."* **An EMC nodule is not that tissue.** This is
a haematological malignancy; nothing here speaks to a T-cell-excluded solid-tumour microenvironment, which
is `RT-VACCINE`'s actual parked blocker (`BLK-ANTIGEN-COLD`). Further limits, all from the paper:
- The fusion-reactive clones sat at **0.0062%, 0.001% and 0.001%** frequency — vanishingly rare.
- They were detected **only at diagnosis or relapse**, i.e. off therapy, and at **no later timepoint even
  with deep sequencing**.
- Of five samples taken forward, four had major clonotypes; one had **no reactivity to either** the fusion
  neoantigen or the blasts.
- Different fusions, different disease, and KMT2A breakpoints cluster in a way EWSR1::NR4A3 need not.

**Net:** it removes "no one has shown a fusion breakpoint is naturally processed and presented in humans"
from the list of things this route cannot claim. It does **not** move the blocker the route is parked on.

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
1. ~~PMID 40707674 full text~~ — **DONE, see §1.** It does evidence endogenous processing and
   presentation, in leukaemia, with the authors' own anatomical caveat against reading it into a solid tumour.
2. PMID 19536894 — what did a Phase 2 breakpoint vaccine actually produce?
3. PMID 36043380 — anything usable against `BLK-ANTIGEN-COLD`?
