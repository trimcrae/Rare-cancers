---
id: DOC-HLA-COVERAGE-EMC-HISTORY
title: "Version and supersession history — hla-coverage-emc.md"
level: L3
kind: historical
status: live
purpose: >
  Hold the superseded text of blocks that were moved out of hla-coverage-emc.md, so the live body can
  carry current values without a supersession banner sitting over them.
scope: >
  L3. A record of earlier wording only. It retains the TEXT of those blocks at a pinned commit; it is
  not a byte-level archive and makes no claim that nothing was deleted anywhere.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Version and supersession history — hla-coverage-emc.md

Companion history record for [`hla-coverage-emc.md`](./hla-coverage-emc.md), held as a sibling file
alongside it. Its placement is settled; no approval is outstanding for it.

**Source pin and provenance.** Every block below is the text of the corresponding block of
`research/manuscripts/neoantigen/hla-coverage-emc.md` as it stood in the working tree at HEAD
`d775c80f8e64bc64b67e8c2fb46edeaa2cca2911`, read on 2026-09-08 immediately before the regeneration
that produced the current live body. It was moved here, unaltered in wording, so that the live body
can carry current values without a supersession banner sitting over them. The HW2 correction pass of
2026-09-08 changed nothing in the blocks below; it added only this header.

**What is retained, stated exactly.** This file retains the **text** of those blocks. It is **not** a
byte-level archive of the earlier file, and it carries no claim that "nothing was deleted" anywhere.
Two specific limits travel with it:

1. The manuscript's own earlier bytes live in this repository's Git history, not here. This file does
   not reproduce them and should not be cited as if it did.
2. The lane that assembled the regenerated text **deleted six intermediate working fragments**
   (`_part_head.md`, `_part_body.md`, `_part_c.md`, `_t1.md`, `_t2.md`, `_maprows.md`) after
   assembly. Their content is contained in the delivered files, but **content containment is not
   proof that the original bytes survive**. Those originals were not recovered and are deliberately
   **not** recreated.

Nothing below is current. Every figure in it is superseded; the live values are in
`hla-coverage-emc.md`.

## 1. The 2026-08-07 supersession banner (verbatim, retained)

> ⛔⛔ **EVERY COVERAGE NUMBER BELOW IS SUPERSEDED (2026-08-07). DO NOT QUOTE THEM.** This
> includes the class-II CD4 column and the DRB1 rows, the both-arms figure, and the per-region
> maximum-sample-size column, none of which is a class-I coverage number and all of which are
> superseded too.
> This document was written against `fusion-breakpoint-neoantigens.json` before that artifact was
> found to be built in the wrong coordinate system. Its junctions were rebuilt on the **transcript**
> model on 2026-08-07 — the acceptor exon is now retained whole, 5′UTR included — and the corrected
> junction set is *disjoint* from the one this analysis used. Coverage is a function of the allele
> set the epitopes are presented on, and that set moved:
>
> | figure | in this document (superseded) | regenerated `hla-coverage.json` |
> |---|---|---|
> | e7::e3 public junction, alleles | A\*11:01 + B\*08:01 | **B\*15:01 alone** |
> | e7::e3 coverage, global | 29.7% (29.0–30.3) | **8.51% (8.26–8.76)** |
> | all strong-binder alleles | A\*02:01, A\*11:01, B\*07:02, B\*08:01, B\*15:01 | **A\*01:01, B\*07:02, B\*15:01** |
> | any-strong coverage, global | 58.0% (57.1–59.0) | **27.4% (26.6–28.1)** |
> | any-strong regional range | 36% (Sub-Saharan Africa) → 79% (N. Europe) | **1.4% (Melanesia) → 60% (N. Europe)** |
> | CD8∧CD4 both-arms | 16.5% | **1.78%** — one strong class II binder survives (DRB1\*14:01; see below) |
>
> ⛔ **⚠ Superseded, retained (updated 2026-08-22): "The class-II arm is withheld rather than
> restated … `patient-cd4-demo.json` … is still built on the retracted seam (`…IVRTDSLKGRRG`) and has
> not been regenerated".** That was true when written and is no longer. The class II demo has been
> rebuilt on the transcript model: `patient-cd4-demo.json` now carries
> `junction_context: QYSQQSSSYGQQ|NMPCVQAQYSPS` with `grade: EMITTABLE`, and `hla_coverage.py`'s own
> `⛔_class_ii_provenance` records `matches_corrected_seam: true`. The arm is reported, and it is
> negative: 44 predicted binders, of which 1 is strong (`SYGQQNMPCVQAQYS` on DRB1\*14:01, predicted IC50 66.1 nM), over a 23-allele class-II panel. The both-arms figure is
> **not computed** rather than withheld — with no qualifying class II allele the coverage script's
> class II branch never evaluates — and what it would compute is a floor over a three-allele panel
> that untested alleles could only raise. Both statements have one home,
> [`emc-vaccine-development-path.md`](./emc-vaccine-development-path.md) §B4.
> ⚠ This paragraph stood contradicting the committed artifact until the vaccine paper's first
> adversarial review enumerated every document that states this arm's status.
> The **method** in this document — AFND pooling, Wilson CIs, the IEDB coverage formula, the
> population→region mapping — is unchanged and was never in question; only the input allele set was.
> Regenerate this prose from
> [`hla-coverage.json`](../../modalities/hla-coverage.json) before circulating. Corrected narrative:
> [`fusion-junction-neoantigen-paper.md`](./fusion-junction-neoantigen-paper.md) §2–§3.

## 2. The superseded Abstract (verbatim, retained — pre-2026-08-07 build)

## Abstract (structured)

- **Background:** Extraskeletal myxoid chondrosarcoma (EMC) is defined by an *NR4A3*
  rearrangement, most often **EWSR1::NR4A3**. The fusion junction is a tumour-specific
  sequence and therefore a candidate **public neoantigen** for an off-the-shelf vaccine or
  TCR-T product — but only for patients who carry an HLA class-I allele that presents the
  junction peptide. The clinically decisive question is *what fraction of patients that is.*
- **Methods:** Strong-binding junction peptides for the resolved in-frame breakpoints were
  taken from the project's breakpoint-neoantigen pipeline (`fusion-breakpoint-neoantigens.json`).
  HLA class-I allele frequencies were pooled from the **Allele Frequency Net Database (AFND)**
  via its MIT-licensed mirror, using **denominator(2N)-weighted** proportions with **Wilson
  95% CIs** (the project's standard pooling method). Population coverage = 1 − ∏(1 − af)²
  (the IEDB population-coverage formula, ≥1 presenting allele under Hardy–Weinberg and
  cross-locus independence). Coverage was computed **globally** and, as a heterogeneity check,
  **per UN M49 sub-region** (AFND population label → country → region, sourced from ISO 3166).
  The same machinery was applied to the **class-II (CD4 helper)** DRB1 alleles that present a
  strong junction binder, and a **both-arms** figure (≥1 class-I *and* ≥1 class-II allele) was
  derived as the product of the two (independent loci).
- **Results:** The commonly-reported **EWSR1 exon 7 :: NR4A3 exon 3** public junction is
  predicted to be presented on **B\*15:01** and covers **8.51% of patients globally**
  (29.7%, 95% CI 29.0–30.3%). Pooling **all** strong-binder alleles across the resolved
  breakpoints (A\*02:01, A\*11:01, B\*07:02, B\*08:01, B\*15:01) raises coverage to
  **≈58% (58.0%, 95% CI 57.1–59.0%)** — i.e. a *single* public junction reaches under a
  third of patients, and even the full multi-allele panel leaves ~40% uncovered. Coverage is
  **highly population-dependent**: the any-strong-allele figure ranges from **36%
  (Sub-Saharan Africa)** to **79% (Northern Europe)**, and the e7::e3 public junction
  specifically ranges from **~10% (Sub-Saharan Africa, Latin America)** to **~53%
  (Melanesia)** / **42% (Eastern Asia)**, tracking the high frequency of A\*11:01 in East
  Asian/Oceanian populations. **CD4 help is the limiting arm:** the DRB1 alleles presenting
  strong helpers (DRB1\*03:01, DRB1\*07:01) cover only **28.4% globally (95% CI 27.9–28.9%)**,
  and — critically — this is **anti-correlated** with the e7::e3 CD8 coverage (high in Africa,
  Southern Asia and Europe; near-zero in Melanesia/Polynesia and low in East Asia, the very
  populations where the public CD8 junction does best). Requiring **both** a class-I and a
  class-II allele therefore covers only **≈16% of patients globally**.
- **Conclusions:** A public, off-the-shelf fusion-neoantigen approach to EMC is **partial by
  construction** and **inequitable if framed by a single global number**. The most "public"
  junction misses ~70% of patients overall and ~90% of Sub-Saharan African and Latin American
  patients. Demanding both CD8 *and* CD4 coverage from public epitopes drops the addressable
  fraction to ~16%, with the CD8-best and CD4-best populations barely overlapping. This is the
  quantitative argument for a **personalised** pipeline (sequence the patient's breakpoint →
  predict junction epitopes → match to the patient's own class-I *and* class-II HLA), with
  public junctions reserved for the specific allele groups where coverage is genuinely high.
  Predicted binding is a screen, not proof of immunogenicity; the class-II figure in particular
  is a floor over a 3-allele test panel; all figures are hypothesis-generating.

## 3. The superseded §3.1 and §3.2 (verbatim, retained)

### 3.1 Global coverage
The single most "public" junction (**EWSR1 e7 :: NR4A3 e3**, predicted to be presented on B\*15:01)
covers **29.7% of patients globally (95% CI 29.0–30.3%)**. The full multi-allele panel across
all resolved breakpoints covers **58.0% (95% CI 57.1–59.0%)**. Per-allele pooled global
frequencies (2N-weighted; n populations / individuals in the JSON):

| Allele | Global allele freq | 95% CI | Carrier freq (≥1 copy) |
|---|---|---|---|
| A\*02:01 | 15.2% | 14.9–15.5% | 28.1% |
| A\*11:01 | 12.6% | 12.4–12.9% | 23.7% |
| B\*07:02 | 4.8% | 4.6–5.0% | 9.4% |
| B\*08:01 | 4.0% | 3.9–4.2% | 7.9% |
| B\*15:01 | 4.4% | 4.2–4.5% | 8.5% |
| DRB1\*03:01 (CD4) | 6.7% | 6.5–6.8% | 12.9% |
| DRB1\*07:01 (CD4) | 9.3% | 9.2–9.5% | 17.8% |

**CD8 read-out:** a single public junction reaches under a third of patients; even the full
class-I panel leaves ~40% with no predicted strong-binding allele.

**CD4 read-out:** the strong-helper DRB1 alleles cover **28.4% globally (95% CI 27.9–28.9%)**,
and requiring **both** a class-I and a class-II allele — what a durable vaccine needs — covers
only **16.5%** of patients globally. (The class-II figure is a floor over a 3-allele test
panel; see §2.4 and §4.) This is the quantitative case that EMC fusion-neoantigen therapy is
**personalised-first**, not off-the-shelf.

### 3.2 Coverage is strongly population-dependent (the caveat that governs interpretation)
The global average hides a wide spread. The any-strong-allele coverage ranges from **36% to
79%** across sub-regions; the e7::e3 public junction ranges even more (≈10% to ≈53%) because
it rides on A\*11:01, which is common in East Asian and Oceanian populations and uncommon in
sub-Saharan Africa. **A global coverage figure therefore overstates benefit for some patients
and understates it for others, and must not be quoted alone.** Full table (from
`hla-coverage.json`; "N≤" is the largest single-allele survey size in the region, a
conservative sample-size indicator):

CD8 columns are the class-I e7::e3 public junction and the any-strong-allele panel; the CD4
column is the class-II DRB1 helper coverage. Note how the **CD8-best regions (Melanesia, East
Asia, Oceania) are the CD4-worst**, and vice-versa — the two arms barely overlap.

| Sub-region | e7::e3 (CD8) | 95% CI | Any strong (CD8) | 95% CI | CD4 (DRB1) | 95% CI | N≤ |
|---|---|---|---|---|---|---|---|
| Northern Europe | 31.0% | 27.4–34.9 | **78.9%** | 74.9–82.6 | 38.0% | 35.0–41.1 | 1,641 |
| Western Europe | 22.7% | 19.9–26.1 | 68.9% | 64.5–73.3 | 38.4% | 35.5–41.4 | 3,077 |
| Northern America | 22.3% | 20.8–23.9 | 62.0% | 59.8–64.3 | 32.4% | 30.6–34.1 | 5,936 |
| Southern Europe | 19.0% | 17.0–21.1 | 61.3% | 58.3–64.4 | 39.1% | 37.6–40.7 | 6,692 |
| Eastern Asia | 41.8% | 40.7–43.0 | 61.3% | 59.6–63.0 | 17.9% | 17.0–18.9 | 11,275 |
| Eastern Europe | 21.9% | 18.7–25.4 | 58.6% | 53.3–63.9 | 28.3% | 26.1–30.7 | 2,531 |
| Australia & New Zealand | 31.4% | 27.4–36.0 | 55.7% | 49.3–62.4 | 15.1% | 10.7–21.0 | 743 |
| Melanesia | **53.3%** | 49.5–57.2 | 54.4% | 50.0–59.6 | 0.6% | 0.2–2.4 | 707 |
| Western Asia | 21.7% | 18.7–25.1 | 54.4% | 49.2–60.0 | 37.2% | 34.6–39.8 | 2,385 |
| Latin America & Caribbean | 10.3% | 8.9–11.9 | 53.0% | 50.6–55.6 | 22.6% | 21.6–23.6 | 21,914 |
| South-eastern Asia | 35.9% | 34.1–37.8 | 49.1% | 46.3–52.1 | 28.9% | 27.0–30.8 | 3,680 |
| Polynesia † | 28.9% | 18.8–42.2 | 46.9% | 30.9–67.3 | 2.9% | 1.1–7.8 | 251 |
| Northern Africa | 15.4% | 11.9–19.9 | 43.2% | 36.2–51.4 | **47.0%** | 43.9–50.1 | 1,610 |
| Southern Asia | 29.3% | 26.9–31.9 | 43.0% | 39.0–47.3 | 42.1% | 40.1–44.1 | 3,694 |
| Sub-Saharan Africa | 10.5% | 8.9–12.3 | **35.9%** | 32.5–39.6 | 26.0% | 24.2–28.0 | 3,902 |
| Micronesia † | n/a | — | n/a | — | 0.0% | 0.0–2.9 | 129 |

† Polynesia and Micronesia are single small populations (N≈51 / 129 for the class-I and CD4
surveys respectively); wide CIs / class-I gaps reflect that — treat as indicative only.

## 4. The superseded §2.1 / §2.4 allele sets and §4 limitation 3 (verbatim, retained)

### 2.1 Epitopes and presenting alleles
Strong MHC-I binders for each resolved in-frame junction were read from
`fusion-breakpoint-neoantigens.json` (project pipeline; MHCflurry on Ensembl-derived junction
sequences). Two allele sets were analysed: (a) the **e7::e3 public** set — alleles presenting
strong binders of the commonly-reported EWSR1 e7 :: NR4A3 e3 junction (**A\*11:01, B\*08:01**);
and (b) the **all-strong** set — every allele presenting any strong breakpoint binder
(**A\*02:01, A\*11:01, B\*07:02, B\*08:01, B\*15:01**).

### 2.4 Class II (CD4 help) and the both-arms figure
CD4 helper epitopes were taken from the project's class-II screen (`patient-cd4-demo.json`;
MHCnuggets on the EWSR1 e7::e3 junction). The DRB1 alleles presenting a **strong** helper
(DRB1\*03:01, DRB1\*07:01) were carried through the identical AFND pooling. **Important
constraint:** that screen tested a **23-allele class-II panel**, enumerated in
`hla-coverage.json`'s `_class_ii_note`, so class-II coverage is a **floor over a tested panel**,
not a complete class-II scan — untested alleles that also present the helpers would only raise it. The "both-arms" coverage (a patient
with ≥1 class-I presenting allele **and** ≥1 class-II helper allele, as a durable vaccine
needs) is the product of the two coverages, treating HLA-A/B and DRB1 as independent loci.

3. **Class-II coverage is a floor over a 23-allele panel.** The class-I binders come from a
   broad allele scan, and the class-II screen tested a 23-allele class-II panel for one
   junction. Coverage over the two strong-helper alleles is therefore a *lower bound*: other
   untested DR (or DQ/DP) alleles that also present the helpers would raise it. The both-arms
   (16.5%) and CD4 (28.4%) figures should be read as "at least", and a full class-II scan is
   the obvious next step before any of these numbers is quoted as final.

## 5. The superseded §3.3 paragraph (verbatim, retained)

The scan is committed (`coverage-curve.json`): of the 34-allele panel, only **4** alleles
present a strong junction binder (A\*01:01, A\*30:02, B\*07:02, B\*15:01), and the global
curve rises 12.4% → 20.6% → 27.4% → **30.4%** — so each added allele buys steeply less, and
90% is unreachable in every region within this panel. Only Northern Europe reaches even 50%
(at 2 alleles, 61.1% at 4); no other region exceeds 42.3%. This quantifies both "how big must a public product be?" and the equity gap: a
fixed allele panel tuned on one population under-serves others.
