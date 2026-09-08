<!-- BEFORE, chunk 1 of 2: Abstract, hla-coverage-emc.md lines 70-113 (verbatim) -->
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

<!-- BEFORE, chunk 2 of 2: sections 3.1 and 3.2, lines 203-261 (verbatim) -->
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
