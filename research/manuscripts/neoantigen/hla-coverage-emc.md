---
id: DOC-HLA-COVERAGE-EMC
title: "Modelled HLA coverage of predicted EWSR1::NR4A3 junction binders in extraskeletal myxoid chondrosarcoma"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: >-
  Report the fraction of a modelled population whose HLA alleles could present predicted
  EWSR1::NR4A3 junction binders, globally and by sub-region, from committed reference allele
  frequencies, and state what that projection does and does not establish.
scope: >-
  Predicted class-I and class-II binders for the resolved fusion junctions, and pooled public
  allele-frequency surveys. A modelled projection. It contains no patient, no measured presentation
  or immunogenicity result, and no claim that any treatment works.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-05
last_verified: 2026-09-08
---
# Modelled HLA coverage of predicted EWSR1::NR4A3 junction binders in extraskeletal myxoid chondrosarcoma

**Tristan D. McRae**

*Independent researcher, unaffiliated.* ORCID 0000-0002-1823-1451.
Correspondence: trimcrae@gmail.com

**Status.** Draft v0.2, prose regenerated from the committed artifacts, pre-clinician-review, not
for submission.

*A modelled projection over public allele-frequency surveys. No patient was HLA-typed for it, no
peptide was tested in a laboratory, and no claim is made that any treatment works. Analyses were
carried out with AI assistance (see section 6). A sarcoma immuno-oncology and immunogenetics
collaborator is recommended before any version is circulated.*

> **Route status.** The vaccine and coverage route is not active: the immunogen is weak in a cold
> tumour, and the economics favour a platform this project does not control
> ([`IDEAS.md`](../../IDEAS.md)). The analysis is reusable as HLA input to TCR-T and ADC
> eligibility questions. The active manuscript for the programme is
> [`emc-treatment-roadmap.md`](../program/emc-treatment-roadmap.md); the folder map is
> [`README.md`](../README.md).

## Provenance of every value below

Every coverage, allele-frequency, interval and sample-size value in the Abstract and in sections
2.1 to 2.5, 3.1, 3.2 and 3.3 is read from two committed artifacts and from nothing else:
[`hla-coverage.json`](../../modalities/hla-coverage.json), which holds global and per-region
coverage, per-allele pooled frequencies, Wilson intervals, the class-II arm and the both-arms
product, and [`coverage-curve.json`](../../modalities/coverage-curve.json), which holds the
expanded-panel scan of section 3.3. Section 3.4's construct values, meaning the assembled window,
the minimal SLP, the epitope counts and their allele attributions, come from a third artifact,
`vaccine-construct.json`, and are reported on a reading of that file recorded in this project's
earlier N2 review pass, which read `assembled_window`, `minimal_SLP` and the CD8 and CD4 epitope
entries directly. Section 1's 0.495 cavity score comes from
[`novel-modalities.md`](../modality-census/novel-modalities.md) section 2 and is attributed there,
not to either coverage artifact.

The two coverage artifacts record their own upstream provenance: allele frequencies from the Allele
Frequency Net Database (AFND) via the MIT-licensed `slowkow/allelefrequencies` mirror
(`_source_urls.allele_frequencies`), region labels from the ISO 3166 and UN M49 table
(`_source_urls.region_mapping`), and source state `AFND frequencies retrieved from MIT-licensed
mirror` (`_source_status`). The class-II arm is read from `patient-cd4-demo.json` through
`hla-coverage.json`'s own class-II provenance record, which holds
`class_ii_junction_context: QYSQQSSSYGQQ|NMPCVQAQYSPS`,
`corrected_junction_context: SQQSSSYGQQ|NMPCVQAQYSP` and `matches_corrected_seam: true`. The
class-II input therefore sits on the corrected transcript-model seam, not on the retracted one.

The 2026-08-07 supersession record, the superseded pre-2026-08-07 values and the retained
"superseded, retained" notes are reproduced in
[`hla-coverage-emc-history.md`](./hla-coverage-emc-history.md). That file carries the text of those
blocks. It is not a byte-level archive of the files they were assembled from, and this document
makes no claim that nothing was deleted on their behalf; the retention note in section 7 states the
limit exactly. Nothing below carries a supersession banner, because nothing below is the superseded
build.

## Three kinds of statement

A predicted peptide-MHC binding score is the output of a sequence model, MHCflurry for class I and
MHCnuggets for class II. Modelled HLA carrier coverage is arithmetic over pooled population allele
frequencies, a projection rather than an observation of patients. A measured presentation or
immunogenicity result, whether mass-spectrometric ligandome evidence or a T-cell assay, is absent
from this analysis, because there is no wet lab.

That absence is specific to presentation and immunogenicity, and is not a claim that the document
rests on no observations at all: the upstream AFND allele surveys are observations, secondary and
pooled, and the frequency and sample-size columns below inherit whatever those surveys measured. A
predicted binding score is not evidence of presentation, and modelled coverage is not observed
coverage in any patient series. Neither is converted into the other anywhere below.

The coverage numbers are generated by `research/modalities/hla_coverage.py` from public databases
and are reported here as frozen in the committed artifacts, which is what makes this text
reproducible: a reader can re-derive every figure from the two committed JSONs without a network.
Because the upstream allele-frequency mirror updates, a regenerated build would be a distinct,
later version of this analysis, an optional future act rather than a gate to be cleared before this
frozen version is read or circulated.

---

## Abstract

**Background.** Extraskeletal myxoid chondrosarcoma (EMC) is defined by an *NR4A3* rearrangement,
most often EWSR1::NR4A3. The fusion junction is a tumour-specific sequence and therefore a candidate
public neoantigen for an off-the-shelf vaccine or TCR-T product, but only for patients who carry an
HLA allele predicted to present the junction peptide. This analysis addresses the modelled size of
that carrier fraction. Whether such a product would work in patients is not addressed here at all.

**Methods.** Junction peptides scoring as strong binders were taken from the project's
breakpoint-neoantigen pipeline, rebuilt on the transcript junction model on 2026-08-07. Every such
score is a model prediction, not a measured presentation event. HLA allele frequencies were pooled
from the Allele Frequency Net Database (AFND) via its MIT-licensed mirror, a secondary source, using
denominator (2N) weighted proportions, af = Σcopies / Σ2N, with Wilson score 95% CIs (`_method`).
Carrier frequency for one allele = 1 − (1 − af)². Coverage of an allele set is computed as the
artifact implements it, 1 − ∏(1 − af)², an approximation whose independence assumption this analysis
does not establish: the product runs over several alleles at the *same* locus, where independence
does not hold, so this is an unresolved model limitation and not a demonstrated exact formula
(section 2.3). The coverage interval is propagated from the per-allele Wilson bounds and is
approximate (`_method`). Coverage was computed globally and per UN M49 sub-region. Three distinct
allele populations are reported and never pooled: the base class-I set derived from the resolved
breakpoints, a separate 34-allele expanded class-I scan (section 3.3), and a 23-allele class-II
panel (section 2.4).

**Results.** The commonly reported EWSR1 exon 7 :: NR4A3 exon 3 public junction is predicted to be
presented on a single allele, B\*15:01, giving modelled global coverage of 8.51% (95% CI
8.26–8.76%). Pooling all three class-I alleles that present any strong predicted binder across the
resolved breakpoints (A\*01:01, B\*07:02, B\*15:01) raises modelled coverage to 27.37% (95% CI
26.63–28.14%), so the modelled reach of a single public junction, and of the full base panel, are
both well below half of patients. Coverage is strongly population-dependent: any-strong-binder
coverage runs from 60.43% (Northern Europe, 95% CI 55.93–64.95%) down to 1.37% (Melanesia, 95% CI
0.54–3.49%), and is UNKNOWN rather than zero for Micronesia, where no class-I allele of the set has
regional AFND data. The e7::e3 junction alone runs from 16.11% (Northern Europe, 95% CI
13.83–18.71%) to 0.76% (Northern Africa, 95% CI 0.26–2.19%), and is UNKNOWN for Polynesia and
Micronesia. Three of the sixteen sub-regions, Micronesia, Polynesia and Melanesia, have incomplete
class-I allele data, leaving thirteen regions with all three base alleles present.

The class-II (CD4 helper) arm is reported and it is thin: exactly one DRB1 allele in the tested
23-allele panel, DRB1\*14:01, presents a strong predicted helper, covering 6.49% globally (95% CI
6.30–6.70%). Requiring both ≥1 class-I and ≥1 class-II allele gives 1.78% globally
(`coverage_cd8_and_cd4_combined`, the product of the two coverages under cross-locus independence;
the artifact publishes no interval for this figure). **That product mixes two different antigen
scopes and is therefore an artifact-level quantity, not a joint eligibility estimate for any one
construct:** its class-I factor (27.37%) is the base binder set pooled across all resolved
junctions, while its class-II factor (6.49%) is a screen of the e7::e3 junction only. It is not
demonstrated joint eligibility for one specified construct, and it is not a stated requirement that
a durable vaccine response must meet.

**Conclusions.** Within this model, and conditional on its assumptions, a single public junction's
predicted binder is carried by a small minority of the modelled population, and the modelled class-I
figure spans 60.43% to 1.37% between the best and worst *computed* sub-regions, so a single global
number is not a usable summary of the modelled spread. Combining the two arms as the artifact does
yields a modelled figure under two per cent, with the scope mismatch above. These are model
estimates about allele carriage, not estimates of how many patients a product would reach or
benefit: the panels are limited, the independence assumptions are unverified, and a panel-limited
coverage number is not a guaranteed lower bound on true patient eligibility in either direction. The
results are consistent with a patient-specific matching step, in which the patient's breakpoint is
sequenced, junction epitopes are predicted, and those are matched to the patient's own class-I and
class-II HLA, being informative. Nothing here establishes that such a pipeline is clinically
indicated, and no equity, efficacy or benefit conclusion follows from this arithmetic. Predicted
binding is a screen, not proof of presentation and not proof of immunogenicity; all figures are
hypothesis-generating and none is a clinical claim.

---

## 1. Background

### 1.1 The case for an immunological target

A structure assessment recorded in
[`novel-modalities.md`](../modality-census/novel-modalities.md) section 2 predicts EWSR1::NR4A3 to
be either intrinsically disordered or folded but pocket-less, with a best cavity druggability score
of 0.495, below the threshold that assessment uses. That is a predicted score on predicted models,
AlphaFold2 structures from the AlphaFold DB scored with fpocket, retained here from that document
and not re-derived in this analysis. It does not establish that small-molecule targeting is
precluded: a sub-threshold cavity score in one modelling pipeline is a discouraging prediction, not
a demonstrated impossibility. It is, however, one reason attention has turned to the tumour-specific
fusion junction as an immunological target.

EMC's near-universal *NR4A3* rearrangement creates a fusion protein whose junction peptides do not
exist in the normal proteome. Such junctions are attractive immunotherapy targets: if a recurrent
breakpoint is shared across patients, its junction epitopes are public and could in principle
support an off-the-shelf vaccine or engineered-TCR product rather than a bespoke per-patient build.
A fusion neoantigen is also often argued to have an advantage over the random somatic-mutation
neoantigens that dominate personalised-vaccine programmes, on the grounds that the fusion is the
truncal driver. **No source in this analysis establishes that the fusion is present in every tumour
cell of every patient, that it is never subclonally lost, or that a response against it could not be
escaped.** Clonality, antigen loss and immune escape are not measured anywhere in this work, and the
argument is recorded as a hypothesis about fusion antigens in general, not as a property of EMC
established here.

Two further facts bound the promise. First, the project's breakpoint analysis found no pan-EMC
epitope: strong predicted binders are breakpoint-specific, and the most commonly reported breakpoint,
EWSR1 exon 7 :: NR4A3 exon 3, is only one of several in-frame junctions. Second, every epitope is
useful only in a patient whose HLA presents it, and whether it is presented is here predicted and
never measured. Translating an *in-silico* binder into a clinical claim therefore requires an honest
population-coverage estimate, which is the contribution of this analysis.

### 1.2 Why no therapy exists

The obstacle is not that the biology is unknown, but that the steps past knowing the variant are
hard. The breakpoint varies between patients, so there is no single off-the-shelf product. The
junction is mostly self-sequence: EWSR1 and NR4A3 are both self proteins, only the seam is foreign,
and central tolerance may have pruned reactive T cells. Sarcomas are low-mutational-burden cold
tumours, and a bespoke per-patient product for an ultra-rare cancer has no commercial pull and
cannot easily be trialled at scale. Personalised neoantigen vaccines are nonetheless in late-phase
trials in other tumours, and fusion-directed approaches are being explored in other sarcomas; EMC
simply has no champion. The later results ask what an in-silico analysis can contribute toward
closing that gap: how modelled coverage scales with the number of alleles targeted (section 3.3),
and a concrete candidate antigen construct (section 3.4).

## 2. Methods

### 2.1 Epitopes and presenting alleles (class I)

Every value in this section is a prediction rather than a measurement. Strong MHC-I binders for each
resolved in-frame junction were read from the project's breakpoint-neoantigen pipeline (MHCflurry on
Ensembl-derived junction sequences), rebuilt on the transcript junction model on 2026-08-07 (see the
history record). "Strong binder" throughout means a predicted binding score below the model's strong
threshold. It is not a measured peptide-MHC complex and not an observed T-cell response.

Two class-I allele sets are analysed, read directly from `hla-coverage.json`:

- the e7::e3 public set, alleles presenting a strong predicted binder of the commonly reported
  EWSR1 e7 :: NR4A3 e3 junction: `global.e7e3_public_epitope_alleles` = B\*15:01, one allele;
- the all-strong base set, every allele presenting any strong predicted breakpoint binder:
  `global.all_strong_binder_alleles` = A\*01:01, B\*07:02, B\*15:01, three alleles.

A third, separate class-I population, the 34-allele expanded scan of section 3.3, is not the same
set and is never pooled with these two. Its presenting alleles differ (`presenting_alleles` in
`coverage-curve.json` adds A\*30:02), so its numbers answer a different question and carry a
different denominator.

### 2.2 Allele frequencies, a secondary source, and the pooling

Per-population allele frequencies were obtained from the Allele Frequency Net Database (AFND) [1]
via the MIT-licensed `slowkow/allelefrequencies` mirror [2], a stable raw tab-delimited
republication of AFND. This is a secondary source. AFND itself was not queried, because its site
returns only its interactive search form to a non-browser client and is therefore not reproducibly
fetchable in CI, whereas the mirror is pinned and re-runnable; any error or lag in the mirror
propagates here unchecked. For each allele, per-population copy counts were reconstructed as
copies = round(af × 2N) and pooled as a denominator (2N) weighted proportion af = Σcopies / Σ2N,
with a Wilson score 95% CI [4] on (Σcopies, Σ2N), the same conservative pooling the project uses
for clinical proportions (see
[`systems/POLICY-evidence.md`](../../../systems/POLICY-evidence.md)). These are the definitions
recorded verbatim in the artifact's own `_method` field.

### 2.3 Coverage as a modelled projection, on an unjustified approximation

Carrier (phenotype) frequency for one allele = 1 − (1 − af)² (Hardy-Weinberg, ≥1 copy). Coverage of
an allele set is computed by the artifact as 1 − ∏ᵢ(1 − afᵢ)², the modelled fraction carrying ≥1
predicted presenting allele. **This is reported as the implemented artifact approximation, not as a
demonstrated exact formula.** The artifact's own `_method` names it as "independence across loci;
IEDB population-coverage formula" [3], but that justification does not cover what the expression
actually does in this build: the product runs over B\*07:02 and B\*15:01, two alleles at the same
locus, which are not independent draws, since a person carrying B\*07:02 on one chromosome cannot
also carry B\*15:01 there, and cross-locus independence says nothing about that case. Linkage
disequilibrium between A and B is not modelled either. The direction and size of the resulting bias
are not established here, so this stands as an unresolved model limitation (section 4.8) rather than
a caveat that can be signed off. No number in this document was recomputed under any alternative;
every coverage value is the artifact's value as committed. A coverage interval is propagated from
the per-allele Wilson bounds and is approximate (`_method`).

One denominator distinction runs through every table below. An allele frequency is per chromosome,
copies over 2N; a carrier frequency is per person for one allele; a coverage figure is per person
over a *set* of alleles. They are not interchangeable.

### 2.4 Class II (CD4 help) and the both-arms figure

CD4 helper epitopes were taken from the project's class-II screen (`patient-cd4-demo.json`,
MHCnuggets on the EWSR1 e7::e3 junction). `hla-coverage.json`'s class-II provenance record shows
that this input sits on the corrected transcript-model seam
(`class_ii_junction_context: QYSQQSSSYGQQ|NMPCVQAQYSPS` against
`corrected_junction_context: SQQSSSYGQQ|NMPCVQAQYSP`, `matches_corrected_seam: true`); the earlier
retracted-seam status is retained in the history record and is no longer current.
`global.class_ii_cd4_helper_alleles` contains exactly one allele, DRB1\*14:01, carried through the
identical AFND pooling.

That screen tested a 23-allele class-II panel, enumerated verbatim in `hla-coverage.json`'s
`_class_ii_note`, so class-II coverage is, in the artifact's own words, a floor over a tested panel
rather than a complete class-II scan. **That is a statement about what this panel could find, not a
bound on true patient eligibility** (section 4.4). Untested alleles that also present the helper
would change it in a direction this analysis cannot state, because the untested alleles' frequencies
and binding behaviour are both unknown.

The both-arms figure (`coverage_cd8_and_cd4_combined`) is, in the artifact's own words,
`P(>=1 class-I allele) x P(>=1 class-II allele)`, treating HLA-A/B and DRB1 as independent loci. It
is computed and reported here; the artifact publishes no confidence interval for it, and none is
invented.

**Its two factors do not describe the same antigen.** The class-I factor is
`coverage_any_strong_binder_allele` (27.37%), pooled over the alleles presenting a strong predicted
binder of any resolved junction; the class-II factor is `coverage_cd4_classii` (6.49%), from a
screen of the e7::e3 junction only (`_class_ii_note`). Their product is therefore an artifact-level
quantity, the number the producer emits, and not the modelled joint eligibility of any one specified
construct, for which both arms would have to be scored on the same junction. It is also not a
statement of what a durable vaccine response requires: this analysis neither establishes nor tests
any such requirement.

### 2.5 Regional breakdown as a heterogeneity check

Because HLA frequencies vary enormously between populations, coverage was also computed within each
UN M49 sub-region. AFND free-text population labels were resolved to a country by longest
leading-country-name match, with a small curated alias table for AFND's informal spellings and a few
territories, and the country mapped to its sub-region using the ISO 3166 and UN M49 table [5]. This
is a sourced, reproducible approximation of IEDB's geographic-area breakdown, IEDB's own
population-to-area table not being reproducibly CI-fetchable. In the current build
`_region_mapping.unassigned_populations` = 0 and `_region_mapping.unassigned_individuals` = 0, so no
population was dropped; any unresolved population would be pooled into an "Unassigned" bucket,
reported, and would still count toward the global figures.

A regional allele leaf can be absent. Where a region has no AFND population for one of the alleles,
that allele's entry is `null` and the regional coverage is computed over the alleles that do have
data (`coverage_all_alleles_used`); where none does, the coverage leaf is itself `null`. **A `null`
is UNKNOWN, never 0**, and a coverage computed over one allele is not comparable to one computed
over three. Both facts are shown explicitly in section 3.2.

## 3. Results

### 3.1 Global coverage, modelled and prediction-derived

Reading `hla-coverage.json` at `global`:

- e7::e3 public junction (class I, presented as predicted on B\*15:01 alone,
  `e7e3_public_epitope_alleles`): modelled coverage 8.51%, 95% CI 8.26–8.76%
  (`coverage_e7e3_public`, `coverage_e7e3_public_95ci`).
- All strong binders, base set (class I, A\*01:01, B\*07:02, B\*15:01,
  `all_strong_binder_alleles`): modelled coverage 27.37%, 95% CI 26.63–28.14%
  (`coverage_any_strong_binder_allele`, `..._95ci`).
- CD4 helper arm (class II, DRB1\*14:01 alone, `class_ii_cd4_helper_alleles`): modelled coverage
  6.49%, 95% CI 6.30–6.70% (`coverage_cd4_classii`, `..._95ci`). Bounded by the tested 23-allele
  panel (section 2.4), which is a within-model bound and not a bound on patient eligibility.
- Both arms as the artifact computes them (≥1 class-I allele from the all-junction base set × ≥1
  class-II allele from the e7::e3-only screen): 1.78% (`coverage_cd8_and_cd4_combined`). No interval
  is published for this figure in the artifact, and, per section 2.4, this is an artifact-level
  product across two different antigen scopes rather than joint eligibility for a single construct.

Per-allele pooled global frequencies follow. `global.allele_frequencies` contains exactly four
alleles, three class I and one class II, and every one of them is listed here:

| Allele | Locus class | Pooled global allele frequency | Wilson 95% CI | Carrier frequency 1−(1−af)² | AFND populations pooled | Individuals pooled |
|---|---|---|---|---|---|---|
| HLA-A\*01:01 | class I | 6.41% | 6.22–6.60% | 12.40% | 210 | 32,777 |
| HLA-B\*07:02 | class I | 4.80% | 4.64–4.98% | 9.38% | 175 | 30,647 |
| HLA-B\*15:01 | class I | 4.35% | 4.22–4.48% | 8.50% | 265 | 45,574 |
| DRB1\*14:01 | class II (DRB1) | 3.30% | 3.20–3.41% | 6.50% | 365 | 53,005 |

Denominators, stated once: the *allele frequency* column is copies over 2N chromosomes, the
*carrier* column is persons carrying ≥1 copy of that one allele, and the coverage figures above are
persons carrying ≥1 allele of a set. "AFND populations pooled" and "individuals pooled" are that
allele's own survey base; they differ between alleles and are not a study n.

The modelled CD8 read-out is that a single public junction's binder is carried by 8.51% of the
modelled population, and the full three-allele base panel leaves the clear majority carrying no
allele predicted to present any strong binder. These are modelled carriage fractions over pooled
survey populations. They are not counts of patients reached, and the panel limits below mean they
are not guaranteed floors on true eligibility either.

The modelled CD4 read-out is that the one qualifying strong-helper DRB1 allele covers 6.49%
globally, and the artifact's product of the two arms is 1.78%, subject to the antigen-scope mismatch
in section 2.4. The class-II figure is bounded by the tested 23-allele panel (sections 2.4 and 4).
Taken together, these modelled figures are consistent with a public, single-junction product
addressing only a small modelled fraction, which is a reason to take a patient-specific matching
step seriously as a design option. They do not establish that such a step is clinically indicated,
and none of these numbers is a statement about outcomes in any patient.

### 3.2 Population dependence, the caveat that governs interpretation

The global average hides a wide spread. Across the 16 UN M49 sub-regions in
`hla-coverage.json.regions`, modelled any-strong-binder coverage runs from 60.43% (Northern Europe)
down to 1.37% (Melanesia) among regions where it is computed at all, and is UNKNOWN for Micronesia.
The e7::e3 public junction runs from 16.11% (Northern Europe, 13.83–18.71%) down to 0.76% (Northern
Africa, 0.26–2.19%), and is UNKNOWN for Polynesia and Micronesia. **A single global coverage figure
is therefore not a usable summary of the modelled regional spread and must not be quoted alone.** It
is a statement about modelled allele carriage in pooled survey populations, not about benefit to any
patient in any region.

Every cell of the table below is copied from `hla-coverage.json.regions[<sub-region>]`. Rows are
ordered by any-strong-binder coverage, UNKNOWN last. The CD8 columns are the class-I e7::e3 public
junction and the class-I base three-allele panel; the CD4 column is the class-II DRB1 arm. **These
are three different allele sets with three different denominators, never combined within a row.**
"Class-I alleles with regional data" is `coverage_all_alleles_used`: where it lists fewer than the
three base alleles, the coverage in that row is computed over *only* those alleles, making it the
coverage of a smaller allele set rather than a like-for-like comparison with a three-allele row.
"Largest single-allele survey" is `max_total_individuals`, the biggest single-allele survey base in
the region, a conservative sample-size indicator rather than a study n. "Populations" is
`max_n_populations`.

| Sub-region | e7::e3 public (class I, CD8) | 95% CI | Any strong binder (class I, CD8) | 95% CI | CD4 helper (class II, DRB1) | 95% CI | Class-I alleles with regional data | Largest single-allele survey (individuals) | Populations |
|---|---|---|---|---|---|---|---|---|---|
| Northern Europe | 16.11% | 13.83–18.71% | 60.43% | 55.93–64.95% | 4.10% | 3.23–5.17% | A\*01:01, B\*07:02, B\*15:01 | 1,598 | 9 |
| Western Europe | 8.24% | 7.32–9.27% | 41.57% | 38.99–44.28% | 6.86% | 6.12–7.67% | A\*01:01, B\*07:02, B\*15:01 | 4,045 | 11 |
| Eastern Europe | 7.09% | 5.64–8.91% | 37.03% | 32.39–42.15% | 8.28% | 7.28–9.43% | A\*01:01, B\*07:02, B\*15:01 | 2,456 | 32 |
| Southern Europe | 5.95% | 5.11–6.92% | 32.12% | 29.32–35.12% | 6.34% | 5.75–6.97% | A\*01:01, B\*07:02, B\*15:01 | 5,982 | 36 |
| Northern America | 7.96% | 7.22–8.76% | 31.60% | 29.59–33.72% | 4.94% | 4.37–5.58% | A\*01:01, B\*07:02, B\*15:01 | 5,478 | 23 |
| Western Asia | 2.60% | 1.69–3.98% | 27.83% | 23.46–33.06% | 6.20% | 5.33–7.19% | A\*01:01, B\*07:02, B\*15:01 | 2,543 | 23 |
| Southern Asia | 3.98% | 3.08–5.11% | 25.11% | 22.21–28.43% | 6.65% | 5.89–7.49% | A\*01:01, B\*07:02, B\*15:01 | 3,580 | 26 |
| Australia and New Zealand | 4.98% | 3.33–7.36% | 23.88% | 18.93–29.96% | 14.33% | 11.88–17.19% | A\*01:01, B\*07:02, B\*15:01 | 702 | 8 |
| Northern Africa | 0.76% | 0.26–2.19% | 21.20% | 16.34–27.84% | 2.46% | 1.79–3.35% | A\*01:01, B\*07:02, B\*15:01 | 1,537 | 15 |
| Latin America and the Caribbean | 7.84% | 7.46–8.24% | 21.09% | 19.33–23.00% | 3.17% | 2.80–3.61% | A\*01:01, B\*07:02, B\*15:01 | 17,277 | 113 |
| Sub-Saharan Africa | 2.01% | 1.43–2.82% | 20.39% | 18.08–23.02% | 2.27% | 1.65–3.08% | A\*01:01, B\*07:02, B\*15:01 | 3,066 | 27 |
| Eastern Asia | 15.40% | 14.66–16.17% | 19.96% | 18.63–21.37% | 9.84% | 9.33–10.39% | A\*01:01, B\*07:02, B\*15:01 | 11,585 | 68 |
| South-eastern Asia | 3.67% | 3.02–4.45% | 14.04% | 12.09–16.29% | 5.87% | 5.15–6.68% | A\*01:01, B\*07:02, B\*15:01 | 3,556 | 29 |
| Polynesia | UNKNOWN | — | 1.95% | 0.34–10.41% | 6.76% | 4.82–9.46% | B\*07:02 | 450 | 9 |
| Melanesia | 0.86% | 0.36–2.01% | 1.37% | 0.54–3.49% | 7.26% | 5.99–8.82% | B\*07:02, B\*15:01 | 1,269 | 19 |
| Micronesia | UNKNOWN | — | UNKNOWN | — | 6.86% | 3.67–12.58% | none | 129 | 2 |

**UNKNOWN is not zero, and exactly three regions have incomplete class-I allele data.** Micronesia
has no regional AFND data for A\*01:01, B\*07:02 or B\*15:01, all three allele entries being `null`,
so both its class-I coverage leaves are `null`: its class-I coverage is not computed and is UNKNOWN.
Polynesia has data for B\*07:02 only, so its 1.95% rests on one allele and its e7::e3 leaf, which
needs B\*15:01, is `null` and UNKNOWN. Melanesia's 1.37% is a two-allele figure. **Those three rows,
Micronesia, Polynesia and Melanesia, must not be read against the thirteen rows that carry all three
base alleles as if they measured the same thing.** Thirteen of the sixteen sub-regions have the
complete three-allele set, `coverage_all_alleles_used` listing A\*01:01, B\*07:02 and B\*15:01.
Australia and New Zealand is one of those thirteen and its class-I data are complete; it appears
below only in the separate discussion of small survey bases, which is a different concern from
missing alleles.

Sample size is a separate concern from the missing-allele one above. The smallest regional bases are
Micronesia (129 individuals, 2 populations), Polynesia (450, 9), Australia and New Zealand (702, 8)
and Melanesia (1,269, 19); the largest is Latin America and the Caribbean (17,277, 113). Intervals
in the small regions are correspondingly wide, Polynesia's any-strong CI spanning 0.34–10.41%. Treat
those four rows as indicative only. Australia and New Zealand belongs to this small-survey group and
not to the three incomplete-allele regions: its three base alleles all carry regional data, so its
coverage is computed over the same allele set as the other twelve complete rows and is comparable
with them, and only its precision is limited.

On the relationship between the two arms, the superseded build claimed that CD8-best regions were
CD4-worst, an anti-correlation. **That claim is not carried forward, and no correlation of any sign
is asserted in its place.** Read from the table: the highest computed e7::e3 coverage is Northern
Europe at 16.11% (13.83–18.71%), whose CD4 coverage is 4.10%, low but not the lowest; the next
highest is Eastern Asia at 15.40%, whose CD4 coverage is 9.84%, the second highest in the table. The
lowest computed e7::e3 coverage is Northern Africa at 0.76% (CD4 2.46%), while the lowest computed
CD4 coverage is a different region, Sub-Saharan Africa at 2.27% (e7::e3 2.01%). The highest CD4
coverage sits in Australia and New Zealand (14.33%), whose class-I coverage is mid-table. **Extremes
are not a correlation.** Four ordered pairs cannot establish, or rule out, an association between the
arms. No correlation statistic is computed here, computing one would be a new analysis, and no
relationship of any sign should be inferred from these rows in either direction.

### 3.3 Allele-panel scaling, over a separate and larger allele population

The figures in sections 3.1 and 3.2 use only the alleles that won best-binder per peptide, which is
the coverage of that base set alone. The design question is different: as a public vaccine presents
the junction on more HLA alleles, how fast does modelled coverage rise, and where does it plateau?
`coverage_scan.py` scans a broad common HLA-A and HLA-B panel through MHCflurry and keeps every
allele presenting a strong predicted junction binder (figure `coverage-curve.png`, data
`coverage-curve.json`). Because under 1 − ∏(1 − af)² the greedy-optimal order is simply descending
allele frequency, the curve is cumulative coverage against number of alleles.

**This is a third allele population, not the section 3.1 set.** `panel_size` = 34 alleles scanned;
`n_presenting_alleles` = 4 present a strong predicted binder; `presenting_alleles` = A\*01:01,
A\*30:02, B\*07:02, B\*15:01. It differs from the base set of section 2.1 by A\*30:02, so its
numbers may not be quoted as if they were the base-set numbers.

The global curve (`global_curve`, in the order the scan adds alleles):

| Alleles presented | Allele added | Pooled global af | Cumulative modelled coverage |
|---|---|---|---|
| 1 | HLA-A\*01:01 | 6.41% | 12.41% |
| 2 | HLA-B\*07:02 | 4.80% | 20.62% |
| 3 | HLA-B\*15:01 | 4.35% | 27.37% |
| 4 | HLA-A\*30:02 | 2.11% | 30.40% |

`global_max_coverage` = 30.40%. Each added allele buys steeply less, and every entry of
`global_alleles_to_reach` (`50pct`, `80pct`, `90pct`, `95pct`) is `null`: within this 34-allele
panel, not one of those thresholds is attained globally. Regionally, only Northern Europe reaches
50%, and it does so at 2 alleles (`regions["Northern Europe"].alleles_to_reach.50pct` = 2), topping
out at `max_coverage` 61.10%. The next-highest region is Western Europe at 42.28%, and no region
reaches 80%, 90% or 95%, `alleles_to_reach` being `null` at every one of those thresholds in every
region. Within this model, that bears on the design question "how many
alleles would a public product have to present?", and it shows that a fixed allele panel produces
very different modelled carriage figures in different populations. Whether that difference would
translate into differential clinical benefit is outside what these numbers can say, and no equity
conclusion is drawn from them here.

### 3.4 A candidate antigen construct

The values in this subsection come from a third artifact, `vaccine-construct.json`, not from the two
coverage JSONs. They are not unsourced: this project's earlier N2 review pass read that file
directly and recorded `assembled_window` `PSQYSQQSSSYGQQNMPCVQAQYSPSP`, `minimal_SLP`
`SYGQQNMPCVQAQYS` (15 aa), two CD8 epitope entries both attributed to B\*15:01, and one CD4 epitope
entry on DRB1\*14:01, which is what is printed below. The alleles named are consistent with the
current `hla-coverage.json`. The subsection is descriptive of that committed artifact, it designs
nothing new, and every epitope in it is a model prediction rather than a measured presentation
event.

To make the output concrete, `vaccine_construct.py` turns the predicted epitopes into something
synthesisable (`vaccine-construct.json`). For the public EWSR1 e7::NR4A3 e3 junction it reconstructs
the local fusion window by overlap-assembly of the junction-spanning peptides and finds the minimal
synthetic long peptide (SLP) carrying every strong predicted epitope of both arms:

> Assembled window `PSQYSQQSSSYGQQNMPCVQAQYSPSP` (27 aa, seam `SQQSSSYGQQ|NMPCVQAQYSP`), whose
> minimal SLP is `SYGQQNMPCVQAQYS` (15 aa): a single junction-spanning peptide carrying 2
> predicted-strong CD8 epitopes (`NMPCVQAQY` and `QQNMPCVQAQY`, both B\*15:01) and 1
> predicted-strong CD4 helper (`SYGQQNMPCVQAQYS`, DRB1\*14:01) in native context.

Keeping CD8 and CD4 epitopes contiguous in one SLP is a standard design rationale, the intent being
to preserve processing context and co-deliver help. **Nothing in this analysis tests whether it does
either**, and no durability, potency or response claim is made for this construct. The script also
emits a multi-epitope string-of-beads alternative, distinct epitopes joined by AAY class-I cleavage
linkers and GPGPG class-II spacers, for a construct spanning multiple junctions and alleles. This is
an engineering proposal from predictions rather than a tested immunogen. Nothing in it has been
shown to work in a laboratory or in a patient. It is a defensible starting point for synthesis and a
T-cell assay, which is where computation hands off to a bench this project does not have.

## 4. Limitations

1. **Binding ≠ presentation ≠ immunogenicity.** Every "strong binder" here is a predicted score
   from a sequence model. Nothing in this analysis measures whether the peptide is processed,
   transported, actually presented on a cell surface, or recognised by a T-cell receptor. A
   junction peptide that is mostly self-sequence with a single junction residue is a weaker
   T-cell target than a fully foreign peptide, and tolerance is not modelled. **There is no wet lab,
   and therefore no measured presentation or immunogenicity result anywhere in this analysis.**
   That is the precise scope of the absence. The document does rest on observations of a different
   kind, the pooled AFND allele surveys of section 2.2, whose limitations are limitation 3 rather
   than limitation 1.
2. **Coverage is a modelled projection, not an observation.** No patient was HLA-typed for this
   analysis. Coverage is arithmetic over pooled population allele frequencies; clinical
   eligibility requires the *individual's* HLA type.
3. **Frequencies are a SECONDARY source and can go stale.** They come from an AFND *mirror*
   (section 2.2), not from AFND directly, and the artifact records only that they were "retrieved
   from MIT-licensed mirror", so mirror lag, AFND revisions and survey composition all propagate
   here unchecked. A refreshed retrieval would give a different model estimate on a later date; it is an
   optional distinct future version of this analysis, not a gate on reporting the frozen build.
4. **Class-II coverage is bounded by a 23-allele panel, and that does not make it a guaranteed
   floor on eligibility.** The class-I binders come from a broad allele scan; the class-II screen
   tested the 23 alleles enumerated in `_class_ii_note` for one junction, and exactly one of them,
   DRB1\*14:01, qualified. *Within the model*, adding untested DR/DQ/DP alleles that also presented
   the helper would raise the computed number. **But the CD4 (6.49%) and both-arms (1.78%) figures
   must not be read as clinical "at least" statements about patient eligibility.** The binding calls
   are predictions that can be false positives as well as false negatives, presentation and
   immunogenicity are unmeasured, the coverage arithmetic rests on the unjustified independence
   approximation of section 2.3, and the 1.78% product mixes an all-junction
   class-I factor with an e7::e3-only class-II factor (limitation 12). They are conditional model
   estimates, and a fuller class-II scan would produce a different model estimate, not a correction
   toward a known truth.
5. **`null` regions are UNKNOWN, not zero, and there are exactly three of them.** Micronesia,
   Polynesia and Melanesia are the three sub-regions with incomplete class-I allele data: Micronesia
   has no class-I coverage at all, Polynesia none for e7::e3, and Polynesia's and Melanesia's
   any-strong figures rest on one and two alleles respectively. The other thirteen sub-regions carry
   all three base alleles. Reading any of the three incomplete rows as low coverage rather than as
   absent data would be a straightforward error (section 3.2).
6. **Small regional samples.** Micronesia (129 individuals), Polynesia (450), Australia and New
   Zealand (702) and Melanesia (1,269) are small enough that their intervals are wide and their
   point estimates unstable.
7. **Three allele populations, three denominators.** The base class-I set (3 alleles), the
   34-allele expanded scan (4 presenting alleles) and the 23-allele class-II panel (1 qualifying
   allele) answer different questions. Sections 3.1 and 3.2, section 3.3 and the class-II column
   must not be cross-quoted as if they shared a denominator.
8. **Two-field resolution, and an independence approximation this analysis does not justify.** AFND
   data here are 2-field (e.g. A\*01:01), and linkage disequilibrium between loci is ignored. More
   than that: 1 − ∏(1 − af)² multiplies terms for B\*07:02 and B\*15:01, two alleles at the same
   locus, which are not independent, and cross-locus independence does not license that step. The
   same objection applies to the CD8 × CD4 product. **This is an unresolved model limitation, not a
   quantified correction.** The direction and magnitude of the bias are not established here, and
   nothing in this document should be read as a claim that the approximation is conservative.
9. **Region assignment is heuristic.** Populations are mapped by leading country name, AFND's
   sampling is itself uneven (Latin America is heavily sampled at 113 populations and 17,277
   individuals, some regions thinly), and "sub-region" is a coarse proxy for the genuine diversity
   within it.
10. **Upstream epitope set.** Coverage inherits every limitation of the breakpoint-neoantigen
   predictions it is built on (see
   [`novel-modalities.md`](../modality-census/novel-modalities.md) section 3.3),
   including the 2026-08-07 coordinate-system correction recorded in the history record.
11. **The coverage curve is bounded by its panel.** Section 3.3 scans a 34-allele common HLA-A and
   HLA-B panel; the true ceiling is whatever fraction of patients carry *any* presenting allele,
   which a larger panel could raise. Conversely, an allele counts as covered if it presents *any*
   strong predicted binder, so the construct need not actually include every such epitope. The curve
   answers how many alleles must be presented, not whether each epitope is immunogenic
   (limitation 1).
12. **The 1.78% both-arms figure combines two different antigen scopes.** Its class-I factor is
   `coverage_any_strong_binder_allele` (27.37%), pooled over binders of all resolved junctions; its
   class-II factor is `coverage_cd4_classii` (6.49%), from a screen of the e7::e3 junction only. The
   product is what the producer emits, an artifact-level quantity. **It is not demonstrated joint
   eligibility for any one specified construct, nor a universal requirement that a durable vaccine
   response must satisfy.** A single-construct joint estimate would require both
   arms scored on the same junction, which no committed artifact currently provides.

## 5. Reproducibility

`python research/modalities/hla_coverage.py` fetches the two public sources, the AFND frequencies
and the ISO and UN M49 region map, and reads the project's class-I and class-II epitope JSONs for
the presenting alleles. It recomputes every number in sections 3.1 and 3.2 and writes
`hla-coverage.json`, holding global and per-region figures for class I, class II and the combined
arm, with CIs, sample sizes and the unassigned-population audit. `coverage_scan.py` builds the
section 3.3 curve and chart from an MHCflurry broad-panel scan, writing `coverage-curve.json` and
`coverage-curve.png`. `vaccine_construct.py` builds the section 3.4 construct
(`vaccine-construct.json`) without network access, deterministically from the committed epitope
JSONs. The MHCflurry and matplotlib steps run in CI (`.github/workflows/modalities-run.yml`). If a
source is unreachable the script records `source_unavailable` rather than emitting a fabricated
number.

**No producer was run to prepare this text.** Every figure above is read from the committed
artifacts as they stand, which is what makes the document reproducible offline: the JSONs are in the
repository and each printed value names its key path. A regeneration against a refreshed upstream
mirror would produce a distinct, later version of this analysis, and is an optional future act
rather than a precondition for reading, reviewing or circulating this frozen version.

## 6. Declarations

**Author contributions.** Tristan D. McRae designed the analysis, ran it, and wrote the manuscript,
and is responsible for its content.

**Funding.** None was received for this work.

**Competing interests.** The author declares none.

**Ethics.** This is an analysis of public data. It involved no new recruitment, no new sampling and
no clinical intervention, and no ethics approval was sought or obtained for it. No institution or
committee has determined whether any approval would be required, and no such determination is
claimed here.

**AI assistance.** Code, data retrieval and drafting were carried out with Claude (Anthropic) and
OpenAI models under the author's direction. The author is responsible for the content. This
manuscript has not been peer reviewed by a human reviewer.

**Status.** This is a modelled projection and not a medical device, and nothing in it is clinical
advice.

## 7. Version and supersession history

The pre-2026-08-07 build of this document, its superseded values, the supersession banner and the
retained "superseded, retained" notes are reproduced in
[`hla-coverage-emc-history.md`](./hla-coverage-emc-history.md), so that no supersession banner sits
over current numbers.

What the history file retains is stated exactly rather than as a blanket assurance. It carries the
*text* of those blocks as they stood in the live manuscript body immediately before this
regeneration, together with its source pin. **It is not a byte-level archive.** The manuscript's own
Git history in this repository is the record of the file's earlier bytes, and this document does not
claim to reproduce them.

Separately, the build lane that assembled this text deleted six intermediate working fragments after
assembly. Their content is contained in the delivered files. **Containing the content is not proof
that the original bytes survive.** Those originals were not recovered, and they are not
recreated here: that is a recorded choice rather than an oversight, and the limitation travels with
this document.

## 8. References

1. Gonzalez-Galarza FF, McCabe A, Santos EJMD, et al. Allele frequency net database (AFND)
   2020 update: gold-standard data classification, open access genotype data and new query
   tools. *Nucleic Acids Res.* 2020;48:D783–D788. doi:10.1093/nar/gkz1029.
2. Slowikowski K. *allelefrequencies*: HLA allele frequencies in tab-delimited format,
   downloaded from AFND. GitHub repository (MIT). github.com/slowkow/allelefrequencies.
3. Bui HH, Sidney J, Dinh K, Southwood S, Newman MJ, Sette A. Predicting population coverage
   of T-cell epitope-based diagnostics and vaccines. *BMC Bioinformatics.* 2006;7:153.
   doi:10.1186/1471-2105-7-153.
4. Wilson EB. Probable inference, the law of succession, and statistical inference. *J Am
   Stat Assoc.* 1927;22:209–212. doi:10.1080/01621459.1927.10502953.
5. ISO 3166 country codes with UN M49 region / sub-region classification.
   github.com/lukes/ISO-3166-Countries-with-Regional-Codes.
