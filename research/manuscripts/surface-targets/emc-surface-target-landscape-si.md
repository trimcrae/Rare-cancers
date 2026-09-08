---
id: DOC-EMC-SURFACE-TARGET-LANDSCAPE-SI
title: "Supplementary information: surface-antigen prioritisation in extraskeletal myxoid chondrosarcoma"
level: L3
kind: manuscript
status: live
canonical_for:
  - the supplementary methods, tables and notes of PUB-SURFACE-TARGETS
purpose: >
  Supplementary companion to emc-surface-target-landscape.md. Carries the material moved out of the
  5,000-word main body: full surfaceome and normal-tissue methods, the complete normal-tissue
  classification, the measured limits of the surrogate instrument, panel-level scores, the
  accession-bridge detail, the instrument controls and the extended limitations.
scope: >
  Public expression data only. Transcript abundance, never protein; never surface localisation,
  receptor density, selectivity, safety, a therapeutic window or clinical readiness.
audience: [external reviewers, collaborators, maintainers, autonomous research agents]
date: 2026-08-09
last_verified: 2026-09-08
related: [DOC-EMC-SURFACE-TARGET-LANDSCAPE]
---

# Supplementary information: surface-antigen prioritisation in extraskeletal myxoid chondrosarcoma

**Tristan McRae**

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com

Companion to [`emc-surface-target-landscape.md`](./emc-surface-target-landscape.md). Section numbers
prefixed S refer to this document; unprefixed section names refer to the main text. Supplementary
Methods, Tables and Notes are numbered in parallel S-series, so "Methods S3" and "Note S3" are different
sections. Every value below is read from a committed artifact named in the main text under Data
availability.

**Declarations.** No ethics approval was sought and no exemption determination was requested from any
committee. This document analyses public gene-expression deposits and public annotation resources only.
Analysis code, data processing and drafting were carried out with substantial assistance from large
language models (Anthropic Claude and OpenAI models) under the author's direction; no large language
model is an author. Funding: none. Competing interests: none.

## Supplementary Methods

### S1. Surfaceome construction

The candidate set was assembled from UniProt-reviewed human proteins carrying the plasma-membrane
subcellular location SL-0039 together with either the transmembrane keyword KW-0812 or the GPI-anchor
keyword KW-0336. That query returned 2,820 genes. A curated seed of 47 actionable surface antigens was
unioned in so that established clinical targets were always evaluated rather than filtered out by a
topology annotation; 41 of the 47 were already present in the UniProt set, so the union is 2,826 unique
genes. Of those, 2,692 carried a row in the DepMap expression matrix and were scanned.

The seed is therefore a small and largely redundant minority of the scanned set, and the scan is largely
though not strictly unbiased. Two consequences follow. An antigen can enter the ranking because it was
placed in the seed rather than because a topology annotation captured it, which is why the seed size
and overlap are reported above. And the scanned gene list itself was not written to the
output artifact, only the counts, which is the reason the CSPG4 coverage question in Note S3 is
undecidable rather than resolvable.

### S2. Expression matrix, class definition and the selectivity test

Expression values are DepMap OmicsExpression protein-coding transcripts per million, log2(TPM+1). The
surrogate class was defined by substring match on OncotreeSubtype against seven terms: *ewing*,
*synovial*, *myxoid*, *alveolar*, *desmoplastic small round*, *clear cell sarcoma* and *extraskeletal*.
Six subtypes were actually present in the release and were returned: alveolar rhabdomyosarcoma,
alveolar soft part sarcoma, clear cell sarcoma, Ewing sarcoma, extraskeletal myxoid chondrosarcoma and
synovial sarcoma. That gives 76 class members of which 45 carry expression data. Two consequences are
recorded rather than glossed. No desmoplastic small round cell tumour line matched, so that subtype is
named by the rule and contributes nothing. And alveolar rhabdomyosarcoma entered through the term
*alveolar*, which was written for alveolar soft part sarcoma; it is a fusion-driven sarcoma of a
different lineage and is part of the class as scored.
The single subtype-annotated line is recorded by Cellosaurus as not harbouring the fusion and is not
read as disease evidence anywhere in this work; the record, what it establishes and what it cannot
establish are in Appendix A of the main text.

For each scanned gene the artifact records the class mean, the fraction of class lines expressing it, the
fraction detectable, the mean across non-sarcoma lineages, an effect size as the difference of those
means, a one-sided Mann-Whitney *p* that the class exceeds the rest, and the Benjamini-Hochberg-corrected
*q*. The contrast is cross-cancer rather than tumour-versus-normal, and the DepMap panel is
epithelial-dominated, so the test rewards mesenchymal character. A large positive effect size for a
mesenchymal antigen is largely a statement that carcinoma lines do not carry it.

Two self-checks were specified in advance. Housekeeping genes are excluded by construction, which is a
minimal sanity check rather than a validation. And CD276 recovers as broadly expressed across the panel,
which is the known answer for that antigen.

### S3. Normal-tissue prior and its classification semantics

Each antigen was queried against the Human Protein Atlas for RNA tissue specificity, RNA tissue
distribution, per-tissue nTPM, blood-cell specificity and subcellular location. The classification uses
Human Protein Atlas semantics rather than a threshold on expression:

- RESTRICTED requires tissue-enriched or group-enriched specificity, a restricted distribution, no
  vital-tissue signal and no strong immune or circulating signal.
- ENHANCED_BROAD covers tissue-enhanced antigens, which are detected broadly with a peak.
  Tissue-enhanced is not restricted and is not treated as restricted here.
- BROAD_LIABILITY covers low tissue specificity, and also any antigen whose distribution is
  detected-in-all regardless of its specificity label. The distribution override is what demotes MCAM,
  which is group-enriched yet detected in all tissues.
- VITAL_OR_IMMUNE_LIABILITY overrides all others and is triggered by expression in a vital tissue or by a
  confined blood signal. Immune-cell-enriched and group-enriched blood signals trigger it; the weaker
  immune-cell-enhanced label does not.

The vital-tissue list applied was: heart, cerebral cortex, brain, cerebellum, hippocampus, amygdala,
basal ganglia, spinal cord, nerve, liver, lung, kidney, pancreas, colon, small intestine, duodenum,
stomach, bone marrow, skeletal muscle, smooth muscle and cardiac tissue.

The current artifact classifies 46 antigens. Forty-five carry a window verdict; the forty-sixth,
ALPPL2, is a record the instrument discarded because the Human Protein Atlas search returned a
different gene (ALPG), so no verdict exists for the gene asked for. That is an instrument statement and
never a biological one. Eight antigens are classed RESTRICTED: ALCAM, ALPP, B4GALNT1, CTAG1B, DLL3,
GPC3, MAGEA4 and PRAME. Intersecting that set with the 18 selectivity-significant actionable antigens
of the surrogate scan leaves exactly one antigen, DLL3, which is therefore the only antigen in these
artifacts that is both selective and restricted.

Four controls were specified before the run and all four behaved as specified: DLL3 and GPC3, both
tumour-restricted, returned RESTRICTED; B2M returned a broad verdict; and the hard control CD3E, an
immune antigen, returned VITAL_OR_IMMUNE_LIABILITY rather than RESTRICTED. The CD3E control is the one
that tests both of the classifier's difficult branches at once, namely that tissue-enhanced is not
restricted and that immune expression is caught.

Human Protein Atlas RNA is bulk normal tissue. It is a prior on where an antigen is likely to be found,
not a safety assessment, and it does not measure protein.

### S4. Tumour-tissue cohorts, value kinds and the rule against pooling

The three deposits, their arms and the axis each supplies are in Table 2 of the main text. Three separate
value kinds appear and are never combined.

GPL6244 is a single-channel array. An absolute level is interpretable only relative to that array's own
probe distribution, which is why every row carries an EMC array percentile alongside its contrast.

GPL3290 is a two-colour cDNA platform whose values are log-ratios against a reference pool. An absolute
level there means relative to the pool, only the between-group contrast is interpretable, and an array
percentile on GPL3290 is a percentile of log-ratios rather than a statement that a gene is expressed.

GSE28866 is 3'-end sequencing. Values are read densities at 3' peaks, summarised as medians of per-peak
medians within each arm. No test is computed on them, and the ratios reported in the main text are
ratios of those medians.

Array contrasts are Welch two-sample comparisons of EMC against the comparator arm, expressed as Δ, the
difference of group mean z values in standard deviation units of that array's probe distribution, with
*t* and degrees of freedom. Read densities and array z scores are never combined.

### S5. Readability, the accession bridge and cross-platform states

GPL3290 probes carry expressed-sequence-tag accessions only. Mapping them to gene symbols requires a
bridge, built from a curated accession dictionary, a UniGene archive and live queries. A gene can
therefore be unreadable on that platform purely because its accession did not resolve, with no
implication about its expression.

Every gene consequently carries one of seven cross-platform states: CONCORDANT_UP_ON_BOTH,
CONCORDANT_DOWN_ON_BOTH, DISCORDANT_OPPOSITE_SIGNS, MOVED_ON_ONE_FLAT_ON_THE_OTHER, FLAT_ON_BOTH,
READABLE_ON_ONE_PLATFORM_ONLY and NOT_READABLE_ON_EITHER_PLATFORM. The last two are statements about the
instrument rather than about the gene. The measured accession-resolution rate is recorded on every run
and compared against the previous run's, because a wider bridge changes which genes are readable, and a
gene readable now and unreadable before is explained by the bridge rather than by biology.

Curated panels are scored only above a floor of 3 readable genes and 0.5 coverage. Panels below the floor
emit no score at all rather than a score computed from too few members. Two panels fall below the floor
and are reported in Table S5 as unscored.

### S6. Prior-art screen

A Europe PMC retrieval returned 322 EMC-linked records with 238 full-text files, hand-screened for
surfaceome, surface antigen, cell-surface protein, chimeric antigen receptor, radioligand, antibody-drug
conjugate and immunotherapy terms. Three EMC-specific records matched, none of them a systematic
surface-antigen map. No positive control was included in the query, because no record was known in
advance to be both relevant and returnable by this query, and an earlier control chosen on relevance
alone had caused a whole corpus to be discarded; the corpus was screened by hand instead. The screen
matched titles and abstracts rather than full text, so an absence in it is evidence that nothing is
indexed on the pairing and is not evidence that no such work exists.

### S7. Corrected tissue statistics and the three sensitivity analyses

Every contrast on the 100-gene cross-platform board carries an exact two-sided *p*, a 95 % confidence
interval and a Benjamini-Hochberg *q* at alpha 0.05, corrected **within platform** across every gene
that produced a contrast on that platform. The two platforms are corrected separately because they are
different instruments with different comparator arms, and a concordance claim requires both. The
corrected file reproduces every Δ, *t* and degrees-of-freedom value in the panel artifact before it is
written; a disagreement between the two is a hard failure of that module. Every count in the main text
is taken from the corrected file rather than from a threshold on |*t*|. A |*t*| ≥ 2 verdict string is a
readability label that is more permissive than a 95 % interval at these degrees of freedom, and it is
never a test; the labels FLAT, UP and DOWN are classifications under that rule and are not findings of
presence or absence.

Resolution. Under correction, 24 of the 95 genes readable on GPL6244 and 16 of the 78 readable on
GPL3290 are significant. The median half-width of the 95 % interval is 0.259 standard deviation units on
GPL6244 and 0.957 on GPL3290, and the smallest significant absolute Δ is 0.06 and 0.658 respectively.
The half-width is the elevation a gene's own data cannot exclude, so on GPL3290 a flat row is
uninformative over a wide range and concordance across the two platforms is governed by the wider one.

Sensitivity analysis 1, reference-matched GPL3290. Dropping the three gastrointestinal stromal tumour
arrays leaves ten EMC against three dermatofibrosarcoma protuberans arrays, mRNA against a CRH reference
on both sides. BGN, CD44 and VCAN remain concordantly up with GPL6244 and ANTXR1, B3GALT4, EGFR, FGFR1,
PDGFRB and PTK7 concordantly down. Fifteen of the seventy genes it can read change sign relative to the
full comparator arm: ACTA2, B2M, EPCAM, EPHA2, EPHB4, ERBB2, HLA-C, HSPG2, IGF1R, MAGEA10, NLRC5, PSMB8,
SDC1, SRGN and TAP1. CSPG4 reads Δ = −0.518, *t* = −1.84, 95 % CI −1.15 to 0.11, *q* = 0.182, so the
processing mismatch does not by itself explain the flat GPL3290 CSPG4 contrast. ALCAM reads Δ = +1.233,
*t* = 3.45, 95 % CI 0.15 to 2.31, *q* = 0.082 on three comparator arrays: positive, and still not
significant after correction.

Sensitivity analysis 2, GPL6244 with solitary fibrous tumour. Adding the five solitary fibrous tumour
arrays to the comparator arm gives 6 against 34. BGN, CD44 and VCAN remain concordantly up with GPL3290
and ANTXR1, B3GALT4, FGFR1 and PTK7 concordantly down. Five genes change sign relative to the 29-sample
arm: MAGEC2, PRAME, SDC2, THY1 and TNC. ALCAM (Δ = +1.074, *q* = 0.00051) and CSPG4 (Δ = +0.927,
*q* = 0.0011) are unchanged; GPC1 does not survive correction here either (*q* = 0.060).

Sensitivity analysis 3, the normal skeletal-muscle anchor. The two pooled skeletal-muscle arrays in
GSE24369 are the only normal soft tissue read anywhere in this study, on the same platform as the
primary cohort. In EMC minus pooled muscle, expressed in standard deviation units of the array's probe
distribution: ALCAM +2.85, VCAN +2.68, BGN +1.87, CD44 +1.76, CSPG4 +0.81, CD276 +0.62, CD248 −0.02,
GPC1 −0.42. The anchor is n = 2, pooled RNA rather than individual donors, one tissue rather than a
panel, and carries no test. Its own controls qualify it: *ENO3* (−2.30) and *NR4A3* (−0.65), the
instrument's two positive controls, both read higher in pooled skeletal muscle than in EMC, because both
are muscle-expressed. It is an anchor, not a comparator arm, and no normal-tissue claim in either
document rests on it.

## Supplementary Tables

**Table S1.** Surfaceome construction and self-checks.

| Quantity | Value |
|---|---|
| UniProt plasma-membrane genes with transmembrane or GPI topology | 2,820 |
| Curated actionable-antigen seed | 47 |
| Seed members already in the UniProt set | 41 |
| Unique candidate genes | 2,826 |
| Genes present in the DepMap matrix and scanned | 2,692 |
| Class members by OncotreeSubtype | 76 |
| Class members carrying expression data | 45 |
| Sarcoma lines in the DepMap release | 176 |
| Housekeeping genes in the scanned output | excluded by construction |
| CD276 recovery | broadly expressed, as expected |

**Table S2.** Normal-tissue classification for every antigen either document names that the artifact
classifies, plus the four controls. The rows below are a subset of the artifact, which classifies 46
antigens in total; the antigens named in either document that carry **no** classification are listed
under the table, and their absence is an instrument statement rather than a verdict.

| Antigen | RNA tissue specificity | Tissue distribution | Blood-cell specificity | Verdict |
|---|---|---|---|---|
| B4GALNT1 | Tissue enriched | Detected in many | Not detected in immune cells | RESTRICTED |
| ALCAM | Tissue enriched | Detected in many | Immune cell enhanced | RESTRICTED |
| PRAME | Tissue enriched | Detected in some | Not detected in immune cells | RESTRICTED |
| ALPP | Group enriched | Detected in some | Not detected in immune cells | RESTRICTED |
| MAGEA4 | Tissue enriched | Detected in some | Not detected in immune cells | RESTRICTED |
| CTAG1B | Tissue enriched | Detected in single | Not detected in immune cells | RESTRICTED |
| CDH11 | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD |
| GPC2 | Tissue enhanced | Detected in some | Not detected in immune cells | ENHANCED_BROAD |
| FAP | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD |
| SSTR2 | Tissue enhanced | Detected in many | Low immune cell specificity | ENHANCED_BROAD |
| EGFR | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD |
| CSPG4 | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD |
| GPC1 | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD |
| L1CAM | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD |
| LRRC15 | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD |
| MSLN | Tissue enhanced | Detected in many | Immune cell enhanced | ENHANCED_BROAD |
| ROR1 | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD |
| FGFR1 | Low tissue specificity | Detected in all | Low immune cell specificity | BROAD_LIABILITY |
| MCAM | Group enriched | Detected in all | Not detected in immune cells | BROAD_LIABILITY |
| EPHB4 | Low tissue specificity | Detected in many | Immune cell enhanced | BROAD_LIABILITY |
| CD276 | Low tissue specificity | Detected in many | Not detected in immune cells | BROAD_LIABILITY |
| ERBB2 | Low tissue specificity | Detected in all | Immune cell enhanced | BROAD_LIABILITY |
| CD44 | Tissue enhanced | Detected in all | Low immune cell specificity | BROAD_LIABILITY |
| PDGFRB | Low tissue specificity | Detected in many | Immune cell enhanced | BROAD_LIABILITY |
| CD248 | Tissue enhanced | Detected in many | Immune cell enriched | VITAL_OR_IMMUNE_LIABILITY |
| KIT | Tissue enhanced | Detected in many | Group enriched | VITAL_OR_IMMUNE_LIABILITY |
| NCAM1 | Tissue enhanced | Detected in many | Immune cell enriched | VITAL_OR_IMMUNE_LIABILITY |
| PTK7 | Low tissue specificity | Detected in many | Immune cell enriched | VITAL_OR_IMMUNE_LIABILITY |
| VCAN | Tissue enhanced | Detected in many | Group enriched | VITAL_OR_IMMUNE_LIABILITY |
| CDH17 | Tissue enriched | Detected in some | Immune cell enriched | VITAL_OR_IMMUNE_LIABILITY |
| DLL3 (positive control) | Tissue enriched | Detected in some | Immune cell enhanced | RESTRICTED |
| GPC3 (positive control) | Tissue enriched | Detected in many | Immune cell enhanced | RESTRICTED |
| B2M (negative control) | Low tissue specificity | Detected in all | Low immune cell specificity | BROAD_LIABILITY |
| CD3E (hard control) | Tissue enriched | Detected in many | Group enriched | VITAL_OR_IMMUNE_LIABILITY |

Antigens named in either document with no classification in this artifact. Six of the 18
selectivity-significant actionable antigens — ALK, ENPP1, FGFR4, PDGFRA, SLC34A2 and STEAP1 — were never
queried against the normal-tissue prior and carry no verdict. ALPPL2 was queried and its record was
discarded, because the Human Protein Atlas search returned a different gene (ALPG); no verdict exists
for the gene asked for. In every one of these cases the absence is a statement about what the instrument
holds, and none of them is read as broad, restricted or anything else.

Note on ALCAM. The prior classes it RESTRICTED, while the exposure axis of the sequencing cohort places
its EMC median marginally below the normal-organ median as an untested ratio. The two normal-tissue
instruments point different ways for this antigen, neither measures protein, and the disagreement is not
resolved in either document.

**Table S3.** Curated panel membership.

| Panel | Members |
|---|---|
| Route-named therapeutic addresses (11) | CD276, SSTR2, PRAME, FAP, CD248, CSPG4, MSLN, L1CAM, GPC3, ALPP, CDH17 |
| Stromal and matrix antigens (13) | FAP, CD248, LRRC15, PDGFRA, PDGFRB, ANTXR1, TNC, MMP14, POSTN, THY1, FN1, COL11A1, ACTA2 |
| Antigen-presentation precondition (12) | B2M, HLA-A, HLA-B, HLA-C, TAP1, TAP2, TAPBP, NLRC5, PSMB8, PSMB9, CIITA, ERAP1 |
| Glycan-antigen synthases, not the antigen (5) | B4GALNT1, ST8SIA1, ST3GAL5, B3GALT4, FUT4 |
| Somatostatin-receptor family (5) | SSTR1, SSTR2, SSTR3, SSTR4, SSTR5 |
| Oncofetal-chondroitin-sulfate carrier proteoglycans (18) | CSPG4, CD44, VCAN, ACAN, BCAN, NCAN, SDC1, SDC2, SDC4, GPC1, GPC3, GPC6, BGN, DCN, SRGN, CSPG5, HSPG2, LUM |
| Sarcoma cell-surface addresses (30) | CD276, EGFR, ERBB2, IGF1R, ROR1, ROR2, CD70, NECTIN4, TACSTD2, EPCAM, PTK7, GPC2, FOLH1, FOLR1, CEACAM5, DLK1, MUC16, ALCAM, CD24, CD99, MET, AXL, EPHA2, EPHB4, MCAM, CDH11, FGFR1, KIT, NCAM1, DLL3 |
| Alkaline-phosphatase family (4) | ALPP, ALPPL2, ALPL, ALPI |
| HLA-presented intracellular antigens, not surface (10) | PRAME, MAGEA1, MAGEA3, MAGEA4, MAGEA10, CTAG1B, CTAG2, SSX1, SSX2, MAGEC2 |

All nine panels are repository-curated lists rather than published gene sets or validated signatures,
and any statement resting on one inherits that. The route-named panel is assembled from the therapeutic
addresses that candidate surface-directed routes for this disease name, plus two coverage corrections.
The last panel is named as what it is: those antigens are intracellular and are reachable only through
class-I presentation, so the panel is a precondition check and not a list of surface addresses.

**Table S4.** Tissue-instrument controls.

| Control | Expected | GPL6244 | GPL3290 | 3'-end sequencing |
|---|---|---|---|---|
| NR4A3 | up in EMC | Δ +0.741 (*t* = 4.66, df 7.2), 76th array percentile | no contrast: 2 comparator samples against a floor of 3 | EMC median 0.216 against 0.000 across 32 non-EMC sarcoma libraries |
| ENO3 | up in EMC | Δ +0.808 (*t* = 3.61, df 5.5) | Δ +3.811 (*t* = 13.22) | 2.53× versus normal, 2.02× versus other sarcomas |
| MKI67 | approximately flat **in GSE24369** | Δ +0.129 (*t* = 0.53, df 8.7) | Δ +1.236 (*t* = 2.30, df 5.5) | not reported |

The MKI67 expectation was written for GSE24369, where it is met. The GPL3290 reading is not flat, and it
is reported rather than folded into the control: a proliferation difference on that platform is one more
reason its contrasts are read with the wide intervals recorded in Supplementary Methods S7. A working
control licenses reading the other rows and is not evidence for any of them. The NR4A3 null on
GPL3290 is a sample-count statement, and on an expressed-sequence-tag-annotated array a null could also
be a probe-placement question, since a probe can sit in the region the fusion replaces rather than the
one it retains.

**Table S5.** Panel-level scores. Δ is the panel mean z difference; coverage is readable members divided
by requested members. Panels below the floor emit no score. Panel *p* is the exact two-sided value for
that panel's own score; panels are not entered into the gene-level Benjamini-Hochberg correction, so
these are uncorrected and are read as such.

| Panel | GPL6244 Δ (*t*), *p*, readable | GPL3290 Δ (*t*), *p*, readable |
|---|---|---|
| Route-named addresses | −0.0935 (−1.66), *p* = 0.121, 11 of 11 | +0.599 (+2.91), *p* = 0.025, 8 of 11 |
| Stromal and matrix antigens | −0.328 (−1.89), *p* = 0.095, 13 of 13 | −0.467 (−1.80), *p* = 0.097, 12 of 13 |
| Antigen-presentation precondition | −0.216 (−2.90), *p* = 0.022, 12 of 12 | −0.228 (−0.84), *p* = 0.433, 11 of 12 |
| Glycan-antigen synthases | −0.147 (−4.96), *p* < 0.001, 5 of 5 | −1.050 (−3.44), *p* = 0.005, 4 of 5 |
| Somatostatin-receptor family | −0.008 (−0.20), *p* = 0.849, 5 of 5 | no score: 1 of 5 readable, coverage 0.20 |
| Oncofetal-chondroitin-sulfate carrier proteoglycans | −0.021 (−0.35), *p* = 0.733, 18 of 18 | +0.393 (+3.44), *p* = 0.005, 18 of 18 |
| Sarcoma cell-surface addresses | −0.151 (−3.74), *p* = 0.006, 29 of 30 | +0.090 (+0.93), *p* = 0.387, 25 of 30 |
| Alkaline-phosphatase family | −0.201 (−2.91), *p* = 0.023, 3 of 4 | +1.108 (+4.74), *p* = 0.002, 3 of 4 |
| HLA-presented intracellular antigens, not surface | −0.035 (−1.20), *p* = 0.245, 7 of 10 | no score: 4 of 10 readable, coverage 0.40 |

The route-named panel disagrees between platforms, and the three genes missing from the GPL3290 score are
CD248, CD276 and SSTR2, which are three of the four reading down or flat on GPL6244. The two scores are
therefore not computed over the same set and the disagreement is partly a coverage artefact. The per-gene
tables in the main text are the interpretable presentation of that panel.

**Table S6.** Exposure-axis values from the 3'-end sequencing cohort. Medians of per-peak medians;
4 EMC libraries, 27 normal-organ libraries, 32 non-EMC sarcoma libraries.

| Gene | Peaks | EMC median | Normal median | Other-sarcoma median |
|---|---|---|---|---|
| CSPG4 | 1 | 8.730 | 2.636 | 3.484 |
| BGN | 4 | 1.225 | 0.641 | 0.491 |
| CD248 | 2 | 1.767 | 2.107 | 2.715 |
| ALCAM | 2 | 0.578 | 0.631 | 0.377 |
| FAP | 1 | 0.571 | 0.350 | 0.358 |
| VCAN | 8 | 0.473 | 0.142 | 0.235 |
| CD44 | 7 | 0.433 | 0.256 | 0.265 |
| SSTR2 | 2 | 0.352 | 0.228 | 0.257 |
| CD276 | 3 | 0.286 | 0.220 | 0.202 |
| MSLN | 2 | 0.257 | 0.941 | 0.209 |
| PRAME | 1 | 0.102 | 0.000 | 0.194 |
| GPC3 | 1 | 0.102 | 1.129 | 0.211 |
| L1CAM | 1 | 0.082 | 0.245 | 0.050 |
| CDH17 | 3 | 0.066 | 0.073 | 0.131 |

The PRAME normal median is zero, so its ratio against normal tissue is undefined and is not reported. A
cancer-testis antigen being absent from normal organs is expected and says nothing about this disease.
GPC3, MSLN, L1CAM and CDH17 are the exposure-axis negative controls: four antigens with no reason to be
present in a soft-tissue sarcoma, all of which read below normal tissue.

**Table S7.** Cross-platform states across the 100-gene board, assigned from the within-platform
Benjamini-Hochberg-corrected contrasts at alpha 0.05. ⚠ Superseded, retained: an earlier version of this
table assigned states from verdict strings that threshold |*t*| at 2, and reported 5 concordantly up,
7 concordantly down, 8 discordant, 26 flat on both and 32 moved on one. That threshold is more permissive
than a 95 % interval at these degrees of freedom, and the counts below replace it.

| State | Count | Genes |
|---|---|---|
| CONCORDANT_UP_ON_BOTH | 3 | BGN, CD44, VCAN |
| CONCORDANT_DOWN_ON_BOTH | 4 | ANTXR1, B3GALT4, FGFR1, PTK7 |
| DISCORDANT_OPPOSITE_SIGNS | 1 | PSMB9 |
| FLAT_ON_BOTH | 48 | ACTA2, ALPL, ALPP, AXL, BCAN, CD70, CEACAM5, CIITA, COL11A1, CSPG5, DLL3, EPHA2, EPHB4, ERBB2, FAP, FOLH1, FOLR1, FUT4, GPC6, HLA-A, HLA-C, HSPG2, IGF1R, KIT, LRRC15, LUM, MAGEA10, MCAM, MMP14, MSLN, NCAM1, NCAN, PDGFRA, POSTN, PRAME, PSMB8, ROR2, SDC2, SDC4, SRGN, SSTR1, SSX1, ST8SIA1, TACSTD2, TAP1, TAPBP, THY1, TNC |
| MOVED_ON_ONE_FLAT_ON_THE_OTHER | 22 | ALCAM, ALPI, B2M, CD24, CD99, CDH11, CDH17, CSPG4, DLK1, EGFR, EPCAM, ERAP1, FN1, GPC1, GPC3, L1CAM, MET, NLRC5, PDGFRB, SDC1, ST3GAL5, TAP2 |
| READABLE_ON_ONE_PLATFORM_ONLY | 17 | ACAN, B4GALNT1, CD248, CD276, CTAG2, DCN, GPC2, HLA-B, MAGEA1, MAGEA4, MAGEC2, MUC16, ROR1, SSTR2, SSTR3, SSTR4, SSTR5 |
| NOT_READABLE_ON_EITHER_PLATFORM | 5 | ALPPL2, CTAG1B, MAGEA3, NECTIN4, SSX2 |

The last two rows are statements about the instrument. Nothing in either document treats a gene in them
as low or absent. FLAT_ON_BOTH is likewise a classification and not a finding of absence: on GPL3290 the
median 95 % interval is 0.957 standard deviation units wide, so a flat row there is compatible with a
substantial difference in either direction.

## Supplementary Notes

### S1. Measured limits of the surrogate instrument

Five limits of the surrogate instrument were computed, and each bears on a conclusion in the main text.
The limits are recorded in `surfaceome-instrument-limits.json`; where a field of that artifact has since
been overtaken by a later run of another artifact, the discrepancy is stated below rather than corrected
in place.

**L1, no stromal compartment.** The scanned population is immortalised tumour cell lines cultured as
monoculture. A cancer-associated fibroblast is a different cell that is not present in the culture, so an
antigen carried by fibroblasts has no compartment in which it could be counted. This is a structural
absence rather than low sensitivity: the observation does not exist.

**L2, the stromal floor demonstrated.** LRRC15, an established sarcoma fibroblast antigen with a clinical
antibody-drug conjugate programme behind it, reads at class mean 0.14 log2TPM with an expressed fraction
of 0.0 and no selectivity. FAP reads at class mean 1.37 with an expressed fraction of 0.16. CD248 reads
at class mean 3.01 with an expressed fraction of 0.44 and *q* = 0.0, and PDGFRB at class mean 2.14 with
an expressed fraction of 0.24 and *q* = 0.0001; both are selectivity-significant. These values show what
a stroma-only antigen looks like in this instrument, which is indistinguishable from a genuinely absent
one. They also narrow the limit, and the narrower version is the one this study uses. CD248 and PDGFRB
are routinely called stromal or pericyte antigens and both read significant here, because mesenchymal
tumour cells genuinely transcribe them and there is therefore something in the culture to measure. The
limit is not that the scan cannot see stroma; it is that the scan cannot see a gene that **only** the
stroma expresses. LRRC15 and FAP are that case and CD248 and PDGFRB are not.

**L3, a glycan cannot be ranked.** Oncofetal chondroitin sulfate is a post-translational sulfation
pattern on a carrier proteoglycan. There is no gene for it, so no gene-expression ranking can return it.
The sulfation machinery panel is sourced from a published set and is a proxy
for the machinery rather than for the epitope.

**L4, the CSPG4 coverage gap.** CSPG4 is not in the 47-antigen seed, has no row in the scan's top
candidates, no row among its actionable antigens and no row in the single-line profile. ⚠ The recorded
limit also carries a field stating that CSPG4 has no row in the normal-tissue prior
(`in_emc_surface_normal_window: false`). That field is a **stale historical statement**: it was written
when the prior artifact classified 18 antigens, and the current prior classifies 46 and lists CSPG4
among the genes added in that run, with the verdict ENHANCED_BROAD. The field is left unaltered in the
artifact rather than restamped, and the correct current reading is that CSPG4 is absent from the
**selectivity scan** and present in the **normal-tissue prior**. The coverage gap that matters is
therefore in the ranking instrument alone. Whether CSPG4 was ever scanned is recorded as undecidable,
because the artifact stores gene counts rather than the gene list. Its absence from the
selective-and-restricted intersection is therefore a coverage gap and not a rejection. The rendered
figures are produced from the same JSON, so a gene with no row has nothing to plot.

**L5, no disease observation of FAP.** The scan holds no observation of FAP in this disease, for two
independent reasons, both stated here rather than cross-referenced. The first is compartmental: FAP is a
fibroblast antigen and this instrument's population is monoculture with no fibroblast compartment (L1).
The second is about identity, not compartment: the only class line carrying the disease subtype
annotation is ACH-001519, whose EMC identity the curated record contradicts, so that line supplies no
disease observation of any antigen. Its FAP row reads 0.0 log2TPM, which is
a single value from a line that is not read as disease evidence.

Together, L1 and L2 mean that the surrogate verdicts on FAP and CD248 are partly statements about what
monoculture can contain, which is why the bulk-tissue read is not a redundant second opinion.

### S2. The accession bridge and its consequences

The earlier assessment that the GSE4303 deposit was unusable was true of the instrument that existed when
it was written, and it was carried forward as though it were a property of the deposit. Nothing about the
deposit changed. What changed is the probe-to-symbol bridge: GPL3290 probes carry expressed-sequence-tag
accessions only, and resolving them through a curated dictionary, a UniGene archive and live queries turns
"probes lack gene symbols" into a partial gene index, with 10 EMC and 6 comparator samples readable on
that platform.

That bridge is the weak link on this platform. A gene can be unreadable purely because its accession did
not resolve, which is why CD248, CD276, SSTR2, GPC2 and B4GALNT1 carry a single-platform state
rather than a low reading. The general point extends past this dataset: a finding that public data is
unusable can be a property of the tool applied to it rather than of the data, and here the correction
required no new data.

### S3. CSPG4, held open

CSPG4 is the largest absolute row in the sequencing deposit and a gene the surrogate stage never
evaluated. The main text states its values. Two points bear repeating here.

The classifier records movement on one platform with flatness on the other, rather than opposite signs,
because the GPL3290 value is negative in sign but flat in magnitude. The distinction licenses different
next steps: "strongly up here, silent there" is a row that does not replicate, while "up here, down
there" would be a row that is contradicted.

Three explanations for the platform disagreement are live and none is settled. The GPL3290 comparator
arm is 6 samples with an unusually high CSPG4 mean, and dermatofibrosarcoma protuberans is a dermal
fibroblastic tumour while CSPG4 is a well-known melanocytic and pericytic antigen, so a high
comparator arm would flatten the contrast for reasons about the comparator rather than about the
disease. And half of that comparator arm, the three gastrointestinal stromal tumour arrays, was not
processed like the EMC arm: the deposit annotates all ten EMC arrays and the three dermatofibrosarcoma
protuberans arrays with a "CRH" reference and an mRNA input ("STT3699-Myxoid Chondrosarcoma |
CRH-mRNA", "STT3126-DFSP | CRH | STT3126-DFSP mRNA") and the three gastrointestinal stromal tumour
arrays with a "UHR" reference and a total-RNA input ("STT2001c-GIST-Total RNA-WT | UHR |
STT2001c-GIST-Total RNA"), so on a platform where every value is a log-ratio against the reference
channel a processing mismatch is a third unexcluded reason for a flat GPL3290 contrast. It does not
show the reported contrast to be wrong. The main text's Methods states these annotations in full.

⚠ **Superseded, retained verbatim:** *"No reprocessing was performed and no sensitivity analysis
recomputing the GPL3290 contrasts against the three dermatofibrosarcoma protuberans arrays alone was
run, here or elsewhere in this study, so the mismatch is disclosed rather than excluded."* The deposit
was indeed never reprocessed, and that half stands. The second half is false: that exact sensitivity
analysis is committed in `emc-tissue-read-statistics.json` under
`sensitivity_reference_matched_GPL3290_DFSP_only`, and it is reported in Supplementary Methods S7. Its
CSPG4 row is Δ = −0.518, *t* = −1.84, df 9.8, 95 % CI −1.15 to 0.11, *q* = 0.182: not significant, not
positive, and therefore not an explanation of the flat GPL3290 contrast by processing mismatch alone.
The comparator-composition and antigen-biology explanations remain live, and none of the three is
settled.

The sequencing row rests on one peak and 4 libraries. The normal-tissue prior classifies CSPG4 as
tissue-enhanced, that is detected broadly with a peak rather than restricted, so its behaviour in normal
tissue beyond those six organ types is unaddressed by anything here. ⚠ Superseded, retained: an earlier
version of this note said the prior "already places CSPG4 on the broad-liability list", which names the
wrong verdict tier.

### S4. The disagreement between the two instruments

The surrogate scan and the tissue read invert on the three genes where they can be compared. CD248 is the
surrogate's only selectivity-significant antigen among the route-named set, and its tissue estimate is
lower on the one array that reads it, though not significantly. ALCAM was scored and rejected by the
surrogate at −1.45 log2TPM and is positive in tissue on both arrays, significantly on GPL6244 and not on
GPL3290 after correction. CD44 is the surrogate's most strongly negative row among these genes, at
−3.89 log2TPM, and is concordantly higher in tissue on both arrays.

Four explanations are live and nothing in either artifact discriminates them. The two instruments ask
different questions, and opposite answers to different questions are not inconsistent. They read
different populations, since the surrogate holds no verified fusion-positive line. They read different
compartments, since monoculture is tumour cells only while bulk tissue adds stroma, vasculature, immune
infiltrate and matrix. And they use different measurements, transcripts per million in cultured lines
against array intensity in archival tissue on two decade-old platforms.

The compartment explanation is the one a single measurement could test. A single-cell or spatial dataset
for this disease separates the tumour-cell compartment from the stromal one and would settle it directly.
None is in hand, and neither document selects among the four explanations in its absence.

### S5. Extended limitations

**Cohort size.** The exposure axis rests on 4 tumour libraries. Those are medians of four values, with no
confidence interval, no test and no distribution. The array arms are 6 and 10 archival tumours. Neither
document supports a population-level statement.

**Single peaks and single probes.** Several genes rest on one peak in the sequencing deposit, among them
CSPG4, FAP, GPC3, L1CAM and PRAME, and one peak has no internal replication. Several array rows rest on
one probe, including ALCAM, CD248, CD276, SSTR2, FAP, PRAME and CSPG4 on GPL6244. Where several probes
map to a gene they are collapsed by mean, and probe-level disagreement is not surfaced.

**The normal arm is a tissue panel.** Bowel, breast, colon, kidney, lung and uterus contain almost no soft
tissue, and the libraries are not matched adjacent tissue. The arm is an on-target off-tumour exposure
axis and not a lineage-specificity axis, and it covers six organ types.

**Different comparator arms.** One lineage cohort compares against low-grade fibromyxoid sarcoma, desmoid
fibromatosis and fibrosarcoma; the other against dermatofibrosarcoma protuberans and gastrointestinal
stromal tumour, 6 samples in total. A gene can move in one and not the other because the comparator
changed rather than because the disease did.

**Bulk tissue, not deconvolved.** The disease is matrix-dominated, so tumour-cell content varies between
samples and every reading is a mixture of tumour cells, fibroblasts, endothelium, immune infiltrate and
matrix. A stromal or pericyte antigen can read high because the compartment is present rather than
because the tumour cell carries it.

**Sample classification is string matching** on the verbatim deposit annotation. Every annotation is
reproduced in the artifact, so a mis-bucketed sample is auditable without another run.

**Multiple-testing correction is within platform, not across platforms.** ⚠ Superseded, retained
verbatim: *"No multiple-testing correction is applied anywhere in the tissue read, by design, and every
*t* and degrees-of-freedom value is reported so that a reader can apply their own."* That statement is
false. Benjamini-Hochberg correction is applied within each platform across every gene on the board that
produced a contrast there, at alpha 0.05, and every count in the main text is derived from the corrected
file (Supplementary Methods S7). The correction is not applied across the two platforms, and panel-level
scores are not entered into it. The study's resolution is the binding limit rather than the correction:
the median 95 % interval is 0.957 standard deviation units wide on GPL3290, so a null there excludes
very little and a concordance requirement is governed by that platform.

**Five selective antigens carry no tissue reading.** ALK, ENPP1, FGFR4, SLC34A2 and STEAP1 are
selectivity-significant in the surrogate and were never placed on the 100-gene cross-platform board.
They are unmeasured in EMC tissue by this study, and no statement in either document treats them as
negative.

**Transcript, not protein.** Every address named is a protein or glycan question. Transcript-to-protein
correlation for membrane proteins is modest and is not measured here, and nothing here measures surface
localisation, receptor density or epitope accessibility. A high transcript reading is a reason to
perform a stain and is not an antigen call.

**No safety statement.** The normal-tissue prior is bulk RNA and the sequencing normal arm is six organ
types across 27 libraries. Neither is a safety assessment, no therapeutic window is computed anywhere, and
no agent named in either document has been given to a patient on the basis of anything in them.
