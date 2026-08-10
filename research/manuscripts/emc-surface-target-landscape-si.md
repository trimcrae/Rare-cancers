---
id: DOC-EMC-SURFACE-TARGET-LANDSCAPE-SI
title: "Supplementary information: how far a lineage-surrogate surface-antigen ranking transfers to the tumour it was built for"
level: L3
kind: manuscript
status: live
canonical_for:
  - the supplementary methods, tables and notes of PUB-SURFACE-TARGETS
purpose: >
  Supplementary companion to emc-surface-target-landscape.md. Carries the material moved out of the
  main body: full surfaceome and normal-tissue methods, the complete normal-tissue classification,
  the measured limits of the surrogate instrument, panel-level scores with their p values, the
  accession-bridge detail, the excluded-sample list, the sensitivity analyses, the instrument
  controls, the extended limitations and the version-history register.
scope: >
  Public expression data only. Transcript abundance, never protein; never surface localisation,
  receptor density, selectivity, safety, a therapeutic window or clinical readiness.
audience: [external reviewers, collaborators, maintainers, autonomous research agents]
date: 2026-08-10
last_verified: 2026-08-10
related: [DOC-EMC-SURFACE-TARGET-LANDSCAPE]
---

# Supplementary information: how far a lineage-surrogate surface-antigen ranking transfers to the tumour it was built for

**Tristan McRae**

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com

Companion to [`emc-surface-target-landscape.md`](./emc-surface-target-landscape.md). Sections
prefixed S are Supplementary Methods, tables prefixed S are Supplementary Tables, and notes prefixed
N are Supplementary Notes; unprefixed section names refer to the main text. Every value below is read
from a committed artifact named in the main text under Data availability.

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
output artifact, only the counts, which is the reason the CSPG4 coverage question in Note N3 is
undecidable rather than resolvable.

### S2. Expression matrix, class definition and the selectivity test

Expression values are DepMap OmicsExpression protein-coding transcripts per million, log2(TPM+1). The
surrogate class was defined by matching OncotreeSubtype against the strings *Ewing*, *synovial*,
*alveolar*, *desmoplastic small round*, *clear cell sarcoma*, *myxoid* and *extraskeletal*, giving 76
class members of which 45 carry expression data. Every per-gene row in the artifact reports n = 45.

The six subtypes actually present in the class are alveolar rhabdomyosarcoma, alveolar soft part
sarcoma, clear cell sarcoma, Ewing sarcoma, extraskeletal myxoid chondrosarcoma and synovial sarcoma.
Two consequences of matching by string rather than by an enumerated subtype list are recorded here
because the composition of a surrogate is the whole argument of this paper. Desmoplastic small round
cell tumour was sought and matched no line, so it contributes nothing despite being named in the
matching rule. Alveolar rhabdomyosarcoma was not sought by name and entered through the *alveolar*
string; it is a skeletal-muscle-lineage tumour, so the class is broader in lineage than
"translocation sarcoma" implies, and a reader should treat the class as the six subtypes above rather
than as the rule that produced them.

The single line annotated with the disease subtype, ACH-001519, is recorded by Cellosaurus as not
harbouring the fusion and is not read as disease evidence anywhere in this work; the record, what it
establishes and what it cannot establish are in Appendix A1.

For each scanned gene the artifact records the class mean, the fraction of class lines expressing it,
the fraction detectable, the mean across non-sarcoma lineages, an effect size as the difference of those
means, a one-sided Mann-Whitney *p* that the class exceeds the rest, and the Benjamini-Hochberg-corrected
*q*. The selective set is every actionable antigen with *q* < 0.05, which is 18 of the 47 seeded. The
contrast is cross-cancer rather than tumour-versus-normal, and the DepMap panel is
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

Four controls were specified before the run and all four behaved as specified: DLL3 and GPC3, both
tumour-restricted, returned RESTRICTED; B2M returned a broad verdict; and the hard control CD3E, an
immune antigen, returned VITAL_OR_IMMUNE_LIABILITY rather than RESTRICTED. The CD3E control is the one
that tests both of the classifier's difficult branches at once, namely that tissue-enhanced is not
restricted and that immune expression is caught.

Because DLL3 and GPC3 entered as controls rather than as candidates, they are members of the
selective-and-restricted intersection by construction rather than by nomination. The main text reports
DLL3 as its one member and states the size of its surrogate margin and its flat tumour-tissue reading;
GPC3 does not reach selectivity significance (*q* = 0.053). Neither observation is a statement about
protein, surface localisation or any DLL3- or GPC3-directed agent.

Human Protein Atlas RNA is bulk normal tissue. It is a prior on where an antigen is likely to be found,
not a safety assessment, and it does not measure protein. Its subcellular annotations are
immunofluorescence-based, so a `plasma_membrane_confirmed` value of false in Table S2 records that the
resource holds no immunofluorescence evidence of plasma-membrane localisation for that antigen. It is
not evidence that the protein is absent from the membrane, and for a paper about surface antigens it is
the column most likely to be over-read in either direction.

### S4. Tumour-tissue cohorts, value kinds and the rule against pooling

The three deposits, their arms and the axis each supplies are in Table 2 of the main text. Three separate
value kinds appear and are never combined.

GPL6244 is a single-channel array. An absolute level is interpretable only relative to that array's own
probe distribution, which is why every row carries an EMC array percentile alongside its contrast.

GPL3290 is a two-colour cDNA platform whose values are log-ratios against a reference pool. An absolute
level there means relative to the pool, only the between-group contrast is interpretable, and an array
percentile on GPL3290 is a percentile of log-ratios rather than a statement that a gene is expressed.

**The GPL3290 comparator arm is internally inhomogeneous.** The verbatim deposit annotations
committed in `emc-expression-panels.json` record the ten EMC arrays and the three
dermatofibrosarcoma protuberans arrays as mRNA hybridised against a reference labelled CRH, and the
three gastrointestinal stromal tumour arrays as total RNA against a reference labelled UHR. On a
two-colour platform every value is a log-ratio against the reference channel, so half of a
six-sample comparator arm differs from the EMC arm in both reference pool and RNA input, and the
between-group contrast is the quantity that mismatch sits inside. It affects all 78 GPL3290 gene
contrasts and the panel scores computed from them. Every GPL3290 contrast is therefore also computed
against the three dermatofibrosarcoma arrays alone, which is reference-matched and RNA-input-matched
on both sides, and both sets of values are committed in `emc-tissue-read-statistics.json`. The
reference-matched analysis leaves the concordantly elevated set unchanged (VCAN, BGN, CD44) and adds
EGFR and PDGFRB to the concordantly lower set; 15 of the 70 genes readable in both analyses change
sign. The two largest gains in significance, KIT and PDGFRB, are what dropping a
gastrointestinal-stromal-tumour arm should produce, which is a check on the analysis rather than a
finding about EMC.

GSE28866 is 3'-end sequencing. Values are read densities at 3' peaks, summarised as medians of per-peak
medians within each arm. No test is computed on them, and the ratios reported in the main text are
ratios of those medians. Each ratio is also placed as a percentile of the same ratio computed for every
gene in the deposit, 13,708 genes with a normal ratio and 13,247 with a sarcoma ratio, whose median gene
sits at 1.05 either way. A fold-change on this arm is not readable until an arbitrary gene's
fold-change is known, so the percentile is the calibrated form and the raw ratio is not.

Array contrasts are Welch two-sample comparisons of EMC against the comparator arm, expressed as Δ, the
difference of group mean z values in standard deviation units of that array's probe distribution, with
*t*, degrees of freedom, an exact two-sided *p*, a 95% confidence interval and a within-platform
Benjamini-Hochberg *q*. Read densities and array z scores are never combined.

**Sample classification and what it excludes.** Samples are assigned by matching the verbatim deposit
annotation. In GSE24369 that rule classifies 35 of the 42 deposited samples and leaves seven
unclassified: five solitary fibrous tumour arrays and two pooled normal skeletal-muscle arrays, listed
individually in Table S8. Neither group enters the primary contrast, and both are used in the
sensitivity analyses reported in the main text and in Note N5. In GSE4303 every one of the 16 samples
is classified. One GSE4303 EMC sample is titled with a parenthetical repeat marker, so the ten EMC
arrays are ten libraries and this analysis does not assert that they are ten patients; the sequencing
artifact likewise records replicate ties among the non-EMC sarcoma libraries, so that arm is 32
libraries rather than 32 tumours.

### S5. Readability, the accession bridge and cross-platform states

GPL3290 probes carry expressed-sequence-tag accessions only. Mapping them to gene symbols requires a
bridge, built from a curated accession dictionary, a UniGene archive and live queries. A gene can
therefore be unreadable on that platform purely because its accession did not resolve, with no
implication about its expression.

Of the 100 genes on the cross-platform board, 95 produced a contrast on GPL6244 and 78 on GPL3290.
Every gene consequently carries one of seven cross-platform states: CONCORDANT_UP_ON_BOTH,
CONCORDANT_DOWN_ON_BOTH, DISCORDANT_OPPOSITE_SIGNS, MOVED_ON_ONE_FLAT_ON_THE_OTHER, FLAT_ON_BOTH,
READABLE_ON_ONE_PLATFORM_ONLY and NOT_READABLE_ON_EITHER_PLATFORM. The last two are statements about the
instrument rather than about the gene. The states in Table S7 are computed under the corrected
criterion, in which "moved" means within-platform Benjamini-Hochberg *q* < 0.05 rather than |*t*| >= 2.
The measured accession-resolution rate is recorded on every run and compared against the previous run's,
because a wider bridge changes which genes are readable, and a gene readable now and unreadable before
is explained by the bridge rather than by biology.

Curated panels are scored only above a floor of 3 readable genes and 0.5 coverage. Panels below the floor
emit no score at all rather than a score computed from too few members. Two panels fall below the floor
and are reported in Table S5 as unscored.

### S6. Prior-art screens

A Europe PMC retrieval returned 322 EMC-linked records with 238 full-text files, hand-screened for
surfaceome, surface antigen, cell-surface protein, chimeric antigen receptor, radioligand, antibody-drug
conjugate and immunotherapy terms. Three EMC-specific records matched, none of them a systematic
surface-antigen map. No positive control was included in the query, because no record was known in
advance to be both relevant and returnable by this query, and an earlier control chosen on relevance
alone had caused a whole corpus to be discarded; the corpus was screened by hand instead. That screen
matched titles and abstracts rather than full text, so an absence in it is evidence that nothing is
indexed on the pairing and is not evidence that no such work exists.

That blind spot was subsequently closed against the same corpus, whose full texts were already
retrieved. Of the 237 full-text files, 129 name the disease or one of its fusions, 151 carry a
surface-antigen or immunotherapy term, and 81 carry both. In none of the 81 does any of ALCAM/CD166,
CD248/endosialin, CD276/B7-H3, FAP, PRAME or SSTR2 appear within 2,000 characters of a mention of the
disease. The screen is committed as `emc-prior-art-fulltext-screen-2026-08-10.json` with its exact
term patterns.

What that measurement can and cannot support is worth stating precisely, because the manuscript no
longer makes a priority claim of any kind. The corpus is one Europe PMC query's return and is
open-access full text only, so a result in a subscription-only paper, in a supplementary file not
carried in the full text, or under terms this screen does not match, lies outside it. The finding is a
measured absence in a named corpus and nothing wider, and the main text describes this programme's own
prior state rather than the state of the field.

## Supplementary Tables

**Table S1.** Surfaceome construction and self-checks.

| Quantity | Value |
|---|---|
| UniProt plasma-membrane genes with transmembrane or GPI topology | 2,820 |
| Curated actionable-antigen seed | 47 |
| Seed members already in the UniProt set | 41 |
| Unique candidate genes | 2,826 |
| Genes present in the DepMap matrix and scanned | 2,692 |
| Class members by OncotreeSubtype string match | 76 |
| Class members carrying expression data | 45 |
| Distinct subtypes present in the class | 6 |
| Actionable antigens with Benjamini-Hochberg *q* < 0.05 | 18 of 47 |
| Of those 18, with a tumour-tissue reading | 13 |
| Sarcoma lines in the DepMap release | 176 |
| Housekeeping genes in the scanned output | excluded by construction |
| CD276 recovery | broadly expressed, as expected |

**Table S2.** Complete normal-tissue classification: every antigen the filter holds, with the four
controls. `Plasma membrane` reports the resource's `plasma_membrane_confirmed` field with the
subcellular annotation it rests on; the annotation is immunofluorescence-based, so "no" records the
absence of that evidence and is not evidence of absence from the membrane.

| Antigen | RNA tissue specificity | Tissue distribution | Blood-cell specificity | Verdict | Plasma membrane |
|---|---|---|---|---|---|
| ALCAM | Tissue enriched | Detected in many | Immune cell enhanced | RESTRICTED | no (Vesicles) |
| ALPP | Group enriched | Detected in some | Not detected in immune cells | RESTRICTED | yes (Plasma membrane) |
| ALPPL2 | not returned by the resource | — | — | not scored | — |
| ANTXR1 | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD | no (Vesicles) |
| B2M (negative control) | Low tissue specificity | Detected in all | Low immune cell specificity | BROAD_LIABILITY | yes (Golgi apparatus, Plasma membrane, Cytosol) |
| B4GALNT1 | Tissue enriched | Detected in many | Not detected in immune cells | RESTRICTED | no (none recorded) |
| CD248 | Tissue enhanced | Detected in many | Immune cell enriched | VITAL_OR_IMMUNE_LIABILITY | yes (Plasma membrane) |
| CD276 | Low tissue specificity | Detected in many | Not detected in immune cells | BROAD_LIABILITY | no (Vesicles) |
| CD3E (hard control) | Tissue enriched | Detected in many | Group enriched | VITAL_OR_IMMUNE_LIABILITY | yes (Endoplasmic reticulum, Golgi apparatus, Plasma membrane) |
| CD44 | Tissue enhanced | Detected in all | Low immune cell specificity | BROAD_LIABILITY | yes (Golgi apparatus, Plasma membrane) |
| CD70 | Tissue enhanced | Detected in some | Immune cell enhanced | ENHANCED_BROAD | no (Nucleoplasm) |
| CDH11 | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD | no (none recorded) |
| CDH17 | Tissue enriched | Detected in some | Immune cell enriched | VITAL_OR_IMMUNE_LIABILITY | no (Nucleoplasm, Cell Junctions) |
| CSPG4 | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD | yes (Plasma membrane) |
| CTAG1B | Tissue enriched | Detected in single | Not detected in immune cells | RESTRICTED | no (Golgi apparatus, Vesicles) |
| DLL3 (positive control) | Tissue enriched | Detected in some | Immune cell enhanced | RESTRICTED | yes (Nucleoplasm, Golgi apparatus, Plasma membrane) |
| EGFR | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD | yes (Golgi apparatus, Plasma membrane, Cell Junctions, Primary cilium, and four further sites) |
| EPHA2 | Tissue enhanced | Detected in many | Immune cell enriched | VITAL_OR_IMMUNE_LIABILITY | yes (Nuclear speckles, Golgi apparatus, Plasma membrane, Cell Junctions) |
| EPHB4 | Low tissue specificity | Detected in many | Immune cell enhanced | BROAD_LIABILITY | no (none recorded) |
| ERBB2 | Low tissue specificity | Detected in all | Immune cell enhanced | BROAD_LIABILITY | yes (Nucleoplasm, Plasma membrane, Cytosol) |
| FAP | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD | no (none recorded) |
| FGFR1 | Low tissue specificity | Detected in all | Low immune cell specificity | BROAD_LIABILITY | no (Microtubules, Cytokinetic bridge, and five further sites) |
| GPC1 | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD | yes (Plasma membrane, Cytosol) |
| GPC2 | Tissue enhanced | Detected in some | Not detected in immune cells | ENHANCED_BROAD | no (none recorded) |
| GPC3 (positive control) | Tissue enriched | Detected in many | Immune cell enhanced | RESTRICTED | yes (Plasma membrane) |
| IGF1R | Low tissue specificity | Detected in many | Immune cell enhanced | BROAD_LIABILITY | yes (Nucleoli, Nucleoli rim, Plasma membrane, Primary cilium) |
| KIT | Tissue enhanced | Detected in many | Group enriched | VITAL_OR_IMMUNE_LIABILITY | yes (Nucleoli fibrillar center, Plasma membrane) |
| L1CAM | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD | yes (Nucleoplasm, Plasma membrane) |
| LRRC15 | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD | yes (Vesicles, Plasma membrane) |
| MAGEA4 | Tissue enriched | Detected in some | Not detected in immune cells | RESTRICTED | no (Nuclear speckles, Cytosol) |
| MCAM | Group enriched | Detected in all | Not detected in immune cells | BROAD_LIABILITY | yes (Plasma membrane) |
| MMP14 | Low tissue specificity | Detected in all | Not detected in immune cells | BROAD_LIABILITY | no (Intermediate filaments, Cytosol) |
| MSLN | Tissue enhanced | Detected in many | Immune cell enhanced | ENHANCED_BROAD | yes (Vesicles, Plasma membrane) |
| NCAM1 | Tissue enhanced | Detected in many | Immune cell enriched | VITAL_OR_IMMUNE_LIABILITY | yes (Plasma membrane, Cytosol) |
| PDGFRB | Low tissue specificity | Detected in many | Immune cell enhanced | BROAD_LIABILITY | no (Golgi apparatus, Vesicles) |
| POSTN | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD | no (Golgi apparatus) |
| PRAME | Tissue enriched | Detected in some | Not detected in immune cells | RESTRICTED | yes (Nucleoplasm, Plasma membrane) |
| PTK7 | Low tissue specificity | Detected in many | Immune cell enriched | VITAL_OR_IMMUNE_LIABILITY | yes (Vesicles, Plasma membrane, Cytosol) |
| ROR1 | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD | no (none recorded) |
| ROR2 | Low tissue specificity | Detected in many | Immune cell enriched | VITAL_OR_IMMUNE_LIABILITY | no (none recorded) |
| SDC1 | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD | no (Focal adhesion sites) |
| SSTR2 | Tissue enhanced | Detected in many | Low immune cell specificity | ENHANCED_BROAD | no (Nucleoplasm, Cytosol) |
| TAP1 | Low tissue specificity | Detected in all | Low immune cell specificity | BROAD_LIABILITY | no (Endoplasmic reticulum, Centriolar satellite) |
| THY1 | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD | yes (Nucleoplasm, Plasma membrane) |
| TNC | Tissue enhanced | Detected in all | Not detected in immune cells | BROAD_LIABILITY | no (none recorded) |
| VCAN | Tissue enhanced | Detected in many | Group enriched | VITAL_OR_IMMUNE_LIABILITY | no (Vesicles, Mid piece, Principal piece, End piece) |

Note on ALCAM. The prior classes it RESTRICTED, while the exposure axis of the sequencing cohort places
its EMC median below the normal-organ median at the 33rd ratio percentile. The two normal-tissue
instruments disagree about this antigen, neither measures protein, and the disagreement is not resolved
in either document. The resource records ALCAM's only subcellular annotation as vesicles.

**Table S3.** Curated panel membership.

| Panel | Members |
|---|---|
| Route-named therapeutic addresses (11) | CD276, SSTR2, PRAME, FAP, CD248, CSPG4, MSLN, L1CAM, GPC3, ALPP, CDH17 |
| Stromal and matrix antigens (13) | FAP, CD248, LRRC15, PDGFRA, PDGFRB, ANTXR1, TNC, MMP14, POSTN, THY1, FN1, COL11A1, ACTA2 |
| Antigen-presentation precondition (12) | B2M, HLA-A, HLA-B, HLA-C, TAP1, TAP2, TAPBP, NLRC5, PSMB8, PSMB9, CIITA, ERAP1 |
| Glycan-antigen synthases, not the antigen (5) | B4GALNT1, ST8SIA1, ST3GAL5, B3GALT4, FUT4 |
| Somatostatin-receptor family (5) | SSTR1, SSTR2, SSTR3, SSTR4, SSTR5 |

The route-named panel membership is a repository-curated list assembled from the therapeutic addresses
that candidate surface-directed routes for this disease name, plus two coverage corrections. It is not a
published gene set or a validated signature, and any statement resting on it inherits that.

**Table S4.** Tissue-instrument controls.

| Control | Expected | GPL6244 | GPL3290 | 3'-end sequencing |
|---|---|---|---|---|
| NR4A3 | up in EMC | Δ +0.741 (*t* = 4.66, df 7.2), 76th array percentile | no contrast: 2 comparator samples against a floor of 3 | EMC median 0.216 against 0.000 across 32 non-EMC sarcoma libraries |
| ENO3 | up in EMC | Δ +0.808 (*t* = 3.61, df 5.5) | Δ +3.811 (*t* = 13.22) | 2.53× versus normal, 2.02× versus other sarcomas |
| MKI67 | approximately flat | Δ +0.129 (*t* = 0.53) | not reported | not reported |

A working control licenses reading the other rows and is not evidence for any of them. The NR4A3 null on
GPL3290 is a sample-count statement, and on an expressed-sequence-tag-annotated array a null could also
be a probe-placement question, since a probe can sit in the region the fusion replaces rather than the
one it retains. Both positive controls read higher in the two pooled normal skeletal-muscle arrays than
in EMC (Note N5), which is expected for two muscle-expressed genes and means that neither control
discriminates this disease from that tissue.

**Table S5.** Panel-level scores. Δ is the panel mean z difference with its exact two-sided *p*;
coverage is readable members divided by requested members. Panels are judged by the same rule as genes,
so a panel that does not reach significance is reported as not moving. Panels below the floor emit no
score.

| Panel | GPL6244 Δ (*p*), readable | GPL3290 Δ (*p*), readable |
|---|---|---|
| Route-named addresses | −0.0935 (0.121), 11 of 11 | +0.599 (0.025), 8 of 11 |
| Stromal and matrix antigens | −0.328 (0.095), 13 of 13 | −0.467 (0.097), 12 of 13 |
| Antigen-presentation precondition | −0.216 (0.022), 12 of 12 | −0.228 (0.433), 11 of 12 |
| Glycan-antigen synthases | −0.147 (<0.0001), 5 of 5 | −1.050 (0.005), 4 of 5 |
| Somatostatin-receptor family | −0.008 (0.849), 5 of 5 | no score: 1 of 5 readable, coverage 0.20 |
| Oncofetal-chondroitin-sulfate carrier proteoglycans | −0.021 (0.733), 18 of 18 | +0.393 (0.005), 18 of 18 |
| Sarcoma cell-surface addresses | −0.151 (0.006), 29 of 30 | +0.090 (0.387), 25 of 30 |
| Alkaline-phosphatase family | −0.201 (0.023), 3 of 4 | +1.108 (0.002), 3 of 4 |
| HLA-presented intracellular antigens, not surface | −0.035 (0.245), 7 of 10 | no score: 4 of 10 readable, coverage 0.40 |

The route-named panel disagrees between platforms, and the three genes missing from the GPL3290 score are
CD248, CD276 and SSTR2, which are three of the four reading down or flat on GPL6244. The two scores are
therefore not computed over the same set and the disagreement is partly a coverage artefact. The per-gene
tables in the main text are the interpretable presentation of that panel. Panel *p* values are not
Benjamini-Hochberg corrected across panels, because nine panels chosen in advance for different
questions are not a multiple-testing family in the sense the gene-level correction addresses; the
uncorrected *p* is given so a reader can apply their own rule.

**Table S6.** Exposure-axis values from the 3'-end sequencing cohort. Medians of per-peak medians;
4 EMC libraries, 27 normal-organ libraries, 32 non-EMC sarcoma libraries. Percentiles place each ratio
among all genes in the deposit with that ratio defined, whose median gene sits at 1.05 either way.

| Gene | Peaks | EMC median | Normal median | Other-sarcoma median | EMC/normal (percentile) | EMC/sarcoma (percentile) |
|---|---|---|---|---|---|---|
| CSPG4 | 1 | 8.730 | 2.636 | 3.484 | 3.31× (99th) | 2.51× (98th) |
| BGN | 4 | 1.225 | 0.641 | 0.491 | 1.91× (95th) | 2.49× (98th) |
| ALCAM | 2 | 0.578 | 0.631 | 0.377 | 0.92× (33rd) | 1.53× (90th) |
| FAP | 1 | 0.571 | 0.350 | 0.358 | 1.63× (91st) | 1.59× (92nd) |
| VCAN | 8 | 0.473 | 0.142 | 0.235 | 3.33× (99th) | 2.01× (96th) |
| CD44 | 7 | 0.433 | 0.256 | 0.265 | 1.69× (92nd) | 1.64× (92nd) |
| SSTR2 | 2 | 0.352 | 0.228 | 0.257 | 1.54× (89th) | 1.37× (84th) |
| CD276 | 3 | 0.286 | 0.220 | 0.202 | 1.30× (77th) | 1.42× (86th) |
| MSLN | 2 | 0.257 | 0.941 | 0.209 | 0.27× (5th) | 1.23× (73rd) |
| CD248 | 2 | 1.767 | 2.107 | 2.715 | 0.84× (26th) | 0.65× (7th) |
| PRAME | 1 | 0.102 | 0.000 | 0.194 | undefined | 0.53× (5th) |
| GPC3 | 1 | 0.102 | 1.129 | 0.211 | 0.09× (3rd) | 0.48× (4th) |
| L1CAM | 1 | 0.082 | 0.245 | 0.050 | 0.33× (6th) | 1.62× (92nd) |
| CDH17 | 3 | 0.066 | 0.073 | 0.131 | 0.91× (33rd) | 0.50× (4th) |

The PRAME normal median is zero, so its ratio against normal tissue is undefined and is not reported. A
cancer-testis antigen being absent from normal organs is expected and says nothing about this disease.
GPC3, MSLN, L1CAM and CDH17 are the exposure-axis negative controls: four antigens with no reason to be
present in a soft-tissue sarcoma, all of which read below normal tissue. This panel was assembled from
genes requested by several reads of the same deposit rather than as a surface-antigen panel, so it also
contains genes outside this manuscript's scope, among them RET at the 99th percentile against both arms;
those are not surface-antigen readings and are not interpreted here.

**Table S7.** Cross-platform states across the 100-gene board, under the corrected criterion
(within-platform Benjamini-Hochberg *q* < 0.05).

| State | Count | Genes |
|---|---|---|
| CONCORDANT_UP_ON_BOTH | 3 | BGN, CD44, VCAN |
| CONCORDANT_DOWN_ON_BOTH | 4 | ANTXR1, B3GALT4, FGFR1, PTK7 |
| DISCORDANT_OPPOSITE_SIGNS | 1 | PSMB9 |
| FLAT_ON_BOTH | 48 | includes ACTA2, ALPP, DLL3, EPHB4, ERBB2, FAP, HLA-A, KIT, LRRC15, MCAM, MSLN, NCAM1, PDGFRA, POSTN, PRAME, TAP1, TNC |
| MOVED_ON_ONE_FLAT_ON_THE_OTHER | 22 | ALCAM, ALPI, B2M, CD24, CD99, CDH11, CDH17, CSPG4, DLK1, EGFR, EPCAM, ERAP1, FN1, GPC1, GPC3, L1CAM, MET, NLRC5, PDGFRB, SDC1, ST3GAL5, TAP2 |
| READABLE_ON_ONE_PLATFORM_ONLY | 17 | ACAN, B4GALNT1, CD248, CD276, CTAG2, DCN, GPC2, HLA-B, MAGEA1, MAGEA4, MAGEC2, MUC16, ROR1, SSTR2, SSTR3, SSTR4, SSTR5 |
| NOT_READABLE_ON_EITHER_PLATFORM | 5 | ALPPL2, CTAG1B, MAGEA3, NECTIN4, SSX2 |

The last two rows are statements about the instrument. Nothing in either document treats a gene in them
as low or absent.

**Table S8.** The seven GSE24369 samples the classification rule leaves unclassified, with their
verbatim deposit annotations. None enters the primary contrast; all are used in the sensitivity
analyses in Note N5.

| GSM | Verbatim deposit annotation | Used as |
|---|---|---|
| GSM600963 | Solitary fibrous tumor 1 \| soft tissue \| sample type: tumor biopsy \| tissue: Solitary fibrous tumor | added comparator, sensitivity analysis |
| GSM600964 | Solitary fibrous tumor 2 \| soft tissue \| sample type: tumor biopsy \| tissue: Solitary fibrous tumor | added comparator, sensitivity analysis |
| GSM600965 | Solitary fibrous tumor 3 \| soft tissue \| sample type: tumor biopsy \| tissue: Solitary fibrous tumor | added comparator, sensitivity analysis |
| GSM600966 | Solitary fibrous tumor 4 \| soft tissue \| sample type: tumor biopsy \| tissue: Solitary fibrous tumor | added comparator, sensitivity analysis |
| GSM600967 | Solitary fibrous tumor 5 \| soft tissue \| sample type: tumor biopsy \| tissue: Solitary fibrous tumor | added comparator, sensitivity analysis |
| GSM600968 | Skeletal muscle pooled RNA 1 \| soft tissue \| sample type: pooled RNA \| tissue: Skeletal muscle | normal soft-tissue anchor |
| GSM600969 | Skeletal muscle pooled RNA 2 \| soft tissue \| sample type: pooled RNA \| tissue: Skeletal muscle | normal soft-tissue anchor |

## Supplementary Notes

### N1. Measured limits of the surrogate instrument

Five limits of the surrogate instrument were computed, and each bears on a conclusion in the main text.

**L1, no compartment for a stroma-only antigen.** The scanned population is immortalised tumour cell
lines cultured as monoculture. A cancer-associated fibroblast is a different cell that is not present in
the culture, so an antigen carried only by fibroblasts has no compartment in which it could be counted.
This is a structural absence rather than low sensitivity: the observation does not exist.

**L2, the floor demonstrated, and the narrowing that goes with it.** LRRC15, an established sarcoma
fibroblast antigen with a clinical antibody-drug conjugate programme behind it, reads at class mean 0.14
log2TPM with an expressed fraction of 0.0 and no selectivity. FAP reads at class mean 1.37 with an
expressed fraction of 0.16. Those are what a stroma-only antigen looks like in this instrument, which is
indistinguishable from a genuinely absent one. The limit is narrower than "the scan cannot see stroma",
and the artifact records the counter-reading that narrows it: CD248 reads at class mean 3.01 with an
expressed fraction of 0.44 and PDGFRB at 2.14 with 0.24, and both are selectivity-significant, because
mesenchymal tumour cells genuinely transcribe them, so there is something in the culture to measure. The
honest limit is that the scan cannot see a gene that *only* the stroma expresses. LRRC15 and FAP are that
case; CD248 and PDGFRB are not, and the main text does not group them with LRRC15.

**L3, a glycan cannot be ranked.** Oncofetal chondroitin sulfate is a post-translational sulfation
pattern on a carrier proteoglycan. There is no gene for it, so no gene-expression ranking can return it.
The sulfation machinery panel is sourced from a published set and is a proxy
for the machinery rather than for the epitope.

**L4, the CSPG4 coverage gap.** CSPG4 is not in the 47-antigen seed, has no row in the scan's top
candidates, no row among its actionable antigens, no row in the single-line profile and no row in the
normal-tissue prior artifact of that stage. Whether it was ever scanned is recorded as undecidable,
because the artifact stores gene counts rather than the gene list. Its absence from the
selective-and-restricted intersection is therefore a coverage gap and not a rejection.

**L5, no disease observation of FAP.** The scan holds no observation of FAP in this disease, for two
independent reasons. FAP is a fibroblast antigen and there is no fibroblast compartment, per L1. And the
only class line annotated with the disease subtype is the line whose identity the curated record
contradicts, so it does not supply a disease observation either. Its FAP row reads 0.0 log2TPM, which is
a single value from a line that is not read as disease evidence. This is the limit the main text's FAP
discussion rests on.

Together, L1 and L2 mean that the surrogate verdicts on FAP and LRRC15 are partly statements about what
monoculture can contain, which is why the bulk-tissue read is not a redundant second opinion.

### N2. The accession bridge and its consequences

The earlier assessment that the GSE4303 deposit was unusable was true of the instrument that existed when
it was written, and it was carried forward as though it were a property of the deposit. Nothing about the
deposit changed. What changed is the probe-to-symbol bridge: GPL3290 probes carry expressed-sequence-tag
accessions only, and resolving them through a curated dictionary, a UniGene archive and live queries turns
"probes lack gene symbols" into a partial gene index, with 10 EMC and 6 comparator samples readable on
that platform.

That bridge is the weak link on this platform. A gene can be unreadable purely because its accession did
not resolve, which is why CD248, CD276, SSTR2, GPC2, ROR1 and B4GALNT1 carry a single-platform state
rather than a low reading. The general point extends past this dataset: a finding that public data is
unusable can be a property of the tool applied to it rather than of the data, and here the correction
required no new data.

### N3. CSPG4, held open

CSPG4 is the largest absolute row in the sequencing deposit and a gene the surrogate stage never
evaluated. The main text states its values. Two points bear repeating here.

The classifier records movement on one platform with flatness on the other, rather than opposite signs,
because the GPL3290 value is negative in sign but flat in magnitude with a 95% interval of
[−1.24, +0.86]. The distinction licenses different next steps: "strongly up here, silent there" is a row
that does not replicate, while "up here, down there" would be a row that is contradicted.

Three explanations for the platform disagreement are live and none is settled. The GPL3290 comparator arm
is 6 samples with an unusually high CSPG4 mean, and dermatofibrosarcoma protuberans is a dermal
fibroblastic tumour while CSPG4 is a melanocytic and pericytic antigen, so a high comparator arm would
flatten the contrast for reasons about the comparator rather than about the disease. The third is the
reference-pool and RNA-input mismatch inside that comparator arm described in S4, and it is the one of
the three that can be tested here: against the three reference-matched dermatofibrosarcoma arrays alone
CSPG4 reads Δ = −0.518 with *p* = 0.096 and *q* = 0.18, still negative and still not significant, so the
mismatch does not account for the disagreement. The sequencing row rests on one peak and 4 libraries, and
the normal-tissue prior already places CSPG4 on the broad-liability list, so its behaviour in normal
tissue beyond those six organ types is unaddressed by anything here.

### N4. The disagreement between the two instruments

The surrogate scan and the tissue read invert on the three genes where they can be compared. CD248 is the
surrogate's only selectivity-significant antigen among the route-named set and is lower in tissue. ALCAM
was scored and rejected by the surrogate and is higher in tissue on GPL6244. CD44 is the surrogate's most
strongly negative row of all 47 and is concordantly higher in tissue.

Four explanations are live and nothing in either artifact discriminates them. The two instruments ask
different questions, and opposite answers to different questions are not inconsistent. They read
different populations, since the surrogate holds no verified fusion-positive line. They read different
compartments, since monoculture is tumour cells only while bulk tissue adds stroma, vasculature, immune
infiltrate and matrix. And they use different measurements, transcripts per million in cultured lines
against array intensity in archival tissue on two decade-old platforms.

The compartment explanation is the one a single measurement could test. A single-cell or spatial dataset
for this disease separates the tumour-cell compartment from the stromal one and would settle it directly.
None is in hand, and neither document selects among the four explanations in its absence.

### N5. Sensitivity analyses, the normal soft-tissue anchor and extended limitations

**Reference-matched GPL3290.** Described in S4. The concordantly elevated set is unchanged; EGFR and
PDGFRB join the concordantly lower set; 15 of 70 genes readable in both analyses change sign, none of
them an antigen the main text carries forward. Full per-gene values are in
`emc-tissue-read-statistics.json`.

**Solitary fibrous tumour added to the GPL6244 comparator arm.** Adding the five arrays in Table S8
gives 6 EMC against 34 comparators. Five of 95 genes change sign, none of them carried forward, and both
concordance sets are identical to the primary analysis: BGN, CD44 and VCAN up, ANTXR1, B3GALT4, FGFR1 and
PTK7 down. The exclusion of those five arrays therefore changes no conclusion in this paper, which is
what the analysis was run to establish rather than something assumed.

**The two pooled normal skeletal-muscle arrays.** These are the only normal soft tissue anywhere in the
study, and the exposure axis's binding limitation is that its normal arm is visceral organs containing
almost no soft tissue, so they are reported rather than dropped. On the same array as the primary cohort,
EMC mean z against pooled-muscle mean z reads: ALCAM 2.33 against −0.52, VCAN 2.93 against 0.25, BGN 2.62
against 0.75, CD44 2.68 against 0.93, FAP 1.40 against −0.11, CSPG4 0.86 against 0.05, CD276 0.81 against
0.18, GPC1 0.74 against 1.16, SSTR2 0.27 against 0.35 and CD248 0.35 against 0.37. Four qualifications
apply and none of them is small: n = 2; the libraries are pooled RNA rather than individual donors, so
between-donor variation is unmeasurable; skeletal muscle is one tissue and not a normal-tissue panel;
and no test is computed. Read as a control rather than as a result, the anchor behaves as normal muscle
should, and that is what makes the last observation worth stating: both of the instrument's positive
controls are higher in pooled muscle than in EMC (*ENO3* 2.76 against 0.46, *NR4A3* 1.37 against 0.72),
because both are muscle-expressed, so neither control discriminates this disease from that tissue.

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
fibromatosis and myxofibrosarcoma; the other against dermatofibrosarcoma protuberans and gastrointestinal
stromal tumour, 6 samples in total. A gene can move in one and not the other because the comparator
changed rather than because the disease did.

**Bulk tissue, not deconvolved.** The disease is matrix-dominated, so tumour-cell content varies between
samples and every reading is a mixture of tumour cells, fibroblasts, endothelium, immune infiltrate and
matrix. A stromal or pericyte antigen can read high because the compartment is present rather than
because the tumour cell carries it.

**Sample classification is string matching** on the verbatim deposit annotation. Every annotation is
reproduced in the artifact, so a mis-bucketed sample is auditable without another run, and the seven
GSE24369 samples the rule does not classify are listed in Table S8.

**Resolution.** On GPL6244 the median 95% interval is ±0.26 SD wide and the smallest elevation reaching
Benjamini-Hochberg significance was 0.06 SD; on GPL3290 the corresponding figures are ±0.96 SD and 0.66
SD. Concordance requires both platforms, so the design is governed by the weaker one, and an elevation
below roughly 0.7 SD there is not excluded.

**Transcript, not protein.** Every address named is a protein or glycan question. Transcript-to-protein
correlation for membrane proteins is modest and is not measured here, and nothing here measures surface
localisation, receptor density or epitope accessibility. A high transcript reading is a reason to
perform a stain and is not an antigen call.

**No safety statement.** The normal-tissue prior is bulk RNA and the sequencing normal arm is six organ
types across 27 libraries. Neither is a safety assessment, no therapeutic window is computed anywhere, and
no agent named in either document has been given to a patient on the basis of anything in them.

---

## Appendix A. Version history and correction register

This appendix is the version-history record for the manuscript. It is not part of the main body, it
reports no new result, and it exists so that every superseded value and every withdrawn claim stays
quotable and attributable. The live text carries only current values.

### Appendix A1 — Amendment 1 (2026-08-05): the cell line this manuscript once called "the one real EMC line" is recorded as NOT carrying the fusion

**What the 2026-07-03 version claimed, verbatim and still quotable:** the abstract said the DepMap
translocation-sarcoma class *"— contrary to the common assumption — **also contains one genuine EMC line
(H-EMC-SS / ACH-001519)** whose surface transcriptome we report directly (n = 1, descriptive)"*; §3.1 was
headed *"The one EMC line in public data — H-EMC-SS"* and called its top surface antigens *"the most
EMC-specific in-silico signal available"*; §2.2 recorded that line's *"authentication and EWSR1::NR4A3
status flagged [to verify]"*; and the 2026-07-03 banner read *"surfaces one real EMC cell line's own
profile"*.

**What resolved it.** Three independent readouts, recorded in
[`../modalities/emc-atr-vulnerability.json`](../modalities/emc-atr-vulnerability.json) →
`part_a_hemcss_identity` (verdict `NOT_FUSION_POSITIVE_PER_CURATED_RECORD`) and narrated in
[`emc-atr-vulnerability-assessment.md` §2](./emc-atr-vulnerability-assessment.md):

1. **Cellosaurus `CVCL_1238` carries an explicit curated caution, verbatim:** *"Caution: Does not harbor
   a gene fusion involving EWSR1 which is a hallmark of extraskeletal myxoid chondrosarcoma
   (PubMed=34413129)."*
2. **DepMap's filtered fusion caller** (`OmicsFusionFiltered.csv`, 24Q4, 1,670 models) has the model
   **present** with **2** calls, `AL158209.1--NEBL` and `VIM--RPS25`, and **neither names NR4A3, EWSR1,
   TAF15 or FUS**. The model being *in* the file is what makes this a reading of absence rather than an
   absent reading.
3. **NR4A3 transcript, independent of the caller:** **0.941 log2(TPM+1)**, 83rd percentile of 1,673
   lines, against a panel **median of 0.214**. A fusion transcript carries the NR4A3 body under EWSR1's
   promoter and would be expected to read far higher. **Weak corroboration only.**

**What this amendment does NOT claim.** Cell-line identity is settled by STR authentication against the
donor and RT-PCR for the fusion. Neither is in public data at the resolution needed and neither is
something this programme can perform. So this establishes that **the public record does not support** the
label the manuscript applied; it does **not** establish what the line is instead, that the original
characterisation was wrong, or that the line is not EMC. A line can be misidentified, can drift in
culture, or can be a genuine fusion-negative tumour of the same histology, which is a real category since
a minority of EMC carries no identified FET partner. Cellosaurus also records an 18-locus STR profile
cross-referenced to DepMap `ACH-001519`, COSMIC-CLP `907290` and RIKEN `RCB0508`: the line is a real,
profiled entity, and the open question is what it is rather than whether it exists.

**What was withdrawn.**

| element | status |
|---|---|
| Title's *"one cell line"*, the abstract's *"one genuine EMC line"*, the banner's *"surfaces one real EMC cell line's own profile"*, §3.1's *"the most EMC-specific in-silico signal available"*, §7's *"DepMap additionally holds H-EMC-SS"* | **WITHDRAWN.** These read the line as EMC-and-fusion-positive, which the public record does not support |
| §3.1 **Table 1**, the line's own top surface transcripts | **WITHDRAWN AS AN EMC READING; RETAINED AS DATA** and re-labelled a single sarcoma line of disputed identity. Its values, log2(TPM+1), were: APP 9.9, CD63 9.5, FGFR1 9.3, SLC38A2 9.0, GPRC5B 8.9, PERP 8.8, SLC3A2 8.6, CD81 8.5, CD164 8.5, DNER 8.5, BSG/CD147 8.2, RTN4 8.2, MMP14 8.1, ITGB1 7.9, PMP22 7.8, ALCAM 7.7. The list is dominated by ubiquitous membrane proteins, which is a statement about single-line expression as an instrument and holds for any line |
| §3.1's reading that DNER / RTN4 / PMP22 is *"loosely consistent with EMC's neuroendocrine/neural differentiation"* | **WITHDRAWN.** It was a corroboration of the SSTR2/GD2 hypothesis taken from this line. The manuscript already graded it *"a suggestion, not evidence"*; it is now not even that. FGFR1's appearance there is doubly uninformative, since FGFR1 is concordantly down on both arrays in EMC tissue |
| §3.2 **selectivity** (incl. *B7-H3 is not selective, BH q = 1.0*) | **SURVIVES, RE-LABELLED.** The line is **1 of 45** class members carrying expression data. Recomputing every actionable antigen's `enrichment_vs_rest` with the line dropped moves it by **≤ 0.13 log2TPM** (largest: GPC3 0.93→0.81; CD276 0.14→0.15; CDH11 3.18→3.29), with **no sign flips**. Honest limit: the rank-based Mann–Whitney *p* cannot be recomputed from the committed artifact, which stores summary statistics rather than per-line values, so the *q*-values are **not** re-derived — the effect-size bound is what is offered |
| §3.3 **normal-tissue window** | **UNAFFECTED.** Built entirely from Human Protein Atlas normal tissue; no cell line enters it |

**The general lesson.** The `[to verify]` flag on this line was written honestly and carried faithfully
in four places for a month. **Carrying a flag is not resolving one.** What resolved it was one free API
call that could have been made on day one. Every repository file that leaned on the line now carries its
own dated amendment, and the line's status is registered as an object (`OBJ-LINE-HEMCSS`) in
[`emc-systems-map.json`](./emc-systems-map.json) so that a future claim reading EMC biology off it fails a
checker rather than a reader.

### Appendix A2 — the surrogate-basis framing is superseded (2026-08-07)

**Superseded claim, retained verbatim.** The endpoint register and §6 both stated that every negative this
manuscript reported was *"bounded by that surrogate basis rather than by an EMC tissue measurement"*, from
*"one cell line and a translocation-sarcoma comparison set"*. That limit no longer holds, because the
measurement now exists: **GSE24369 on GPL6244**, **GSE4303 on GPL3290** and **GSE28866 on 3SEQ** are read,
the third carrying **27 normal-organ libraries** and so supplying the on-target/off-tumour exposure axis
this analysis had never been able to ask for.

**Also superseded, retained verbatim.** The 2026-08-05 banner read that the analysis *"reports what an
honest in-silico surface-antigen analysis for EMC can and cannot establish from public data"* and that its
finding was that **"a rigorous selectivity test plus a hard normal-tissue-window filter leaves essentially
no classic protein surface antigen that is both tumour-selective and normal-tissue-restricted."** That
sentence is a statement about the **surrogate**, and it is further corrected by Appendix A6: the
intersection is not empty, and DLL3 populates it.

**Superseded abstract sentence, retained verbatim.** *"The value of the work is to de-risk over-optimistic
assumptions (especially B7-H3), to expose antigen-specific liabilities, and to nominate the neuroendocrine
SSTR2/GD2 route"*, and, before Appendix A1, *"to surface the one available EMC line's profile"*.

**Superseded conclusion sentence, retained verbatim.** *"rigorous selectivity testing plus a normal-tissue
window shows the field-default B7-H3 is not selective and that the selective candidates carry specific
window liabilities, leaving a favourable-normal-tissue-window GD2 (EMC expression unknown) and a
grounded-but-unmeasured-in-EMC SSTR2/DOTATATE neuroendocrine hypothesis as the questions most worth
testing"*.

**What this amendment changed, element by element.**

| element | status |
|---|---|
| The framing that the negatives are bounded by the surrogate rather than by an EMC measurement | **SUPERSEDED.** Three EMC tumour cohorts are read; the surrogate is one instrument among several |
| The **SSTR2 / GD2 neuroendocrine hypothesis**, nominated as one of the two questions "most worth testing" | **DOWNGRADED, not closed.** SSTR2's array reading shows no elevation over comparator sarcomas; the somatostatin-receptor family panel could not be scored on GPL3290; the GD2 proxy B4GALNT1 is flat and its synthase panel is lower on both platforms. Further corrected by Appendix A6: on the sequencing arm SSTR2 sits at the 89th and 84th ratio percentiles, so the downgrade is an array statement and not a statement about all three cohorts. None of this measures receptor protein density, so the hypothesis is weakened and **not** refuted |
| The headline that **B7-H3/CD276 is not selective** | **STRENGTHENED and re-based.** CD276 also reads lower in EMC tumour tissue than in comparator sarcomas on the one platform that can read it, though that single-platform read does not survive correction (Appendix A6). It is **not readable at all** on GPL3290, which is an instrument statement and never a low reading |
| The list of **eight significantly-selective antigens** | **SUPERSEDED BY APPENDIX A6.** The count was eight; the reproducible set is 18 |
| The conclusion that the **selective-and-restricted intersection is empty** | **WITHDRAWN BY APPENDIX A6.** DLL3 is in it |
| The finding that **GSE4303 is unusable** | **SUPERSEDED BY AN INSTRUMENT CHANGE, not by new data.** Superseded text, retained verbatim: *"The only usable, dedicated public EMC tumour transcriptome we could identify, GSE4303, is a seven-platform two-colour cDNA-clone microarray (three EMC samples per platform) whose values are reference-pool log-ratios and whose probes lack gene symbols; zero shortlist genes resolved. It cannot rank surface antigens."* One of its seven platforms, GPL3290, is now readable through an accession bridge; the earlier "zero shortlist genes resolved" was a property of the symbol lookup rather than of the deposit |
| The **collaboration request** | **SURVIVES, with a changed ask.** Superseded sentence, retained verbatim: *"Those models are now the ONLY route to real EMC data for this analysis"*, true on 2026-08-05 and not true once GPL3290 became readable. The decisive missing datum is now **protein and surface localisation**, plus a cohort large enough to carry a distribution |

**The general lesson.** A search that cannot see its own subject will still return a ranked list, and the
list will look like a result. Nothing in the original ranking was miscomputed and every stage-1 number is
reproducible and unretracted. What was wrong was the implicit inference from *"selective in the surrogate"*
to *"worth measuring in EMC"*. The four candidate reasons the two instruments disagree are all live, so this
amendment does not replace one instrument's authority with another's.

### Appendix A3 — restructuring record (2026-08-09)

The manuscript was rewritten from an 11,740-word internal working document carrying two stacked amendment
blocks into a single current narrative in journal Article format. Nothing measured was
withdrawn in the restructure. Material moved out of the main text is in this file: the full normal-tissue
classification, the instrument-limit derivations, the panel-level scores, the accession-bridge detail, the
control tables and the extended limitations. The repository-register house style (glyph warnings,
mid-sentence emphasis, running commentary on the paper's own candour) was removed from the main text as
out of register for a journal, and survives here, where the bookkeeping belongs.

**Superseded framing, retained:** the previous version presented itself as *"an instrument and its
audit"* with the demotion announced in a banner before the abstract. The demotion is unchanged; the banner
is not, because a submission text states its result in the abstract rather than warning the reader in
advance of it.

### Appendix A4 — reference-list completion record (2026-08-09, closed 2026-08-10)

Eleven of the eighteen references carried an identifier and no bibliographic detail. They were completed
from
[`submission-reference-metadata-2026-08-09.json`](../literature/submission-reference-metadata-2026-08-09.json)
and [`emc-prior-art-2026-08-09.json`](../literature/emc-prior-art-2026-08-09.json). Two entries changed
in substance rather than merely gaining fields, and both are registered here:

**Reference 14 was attributed to the wrong first author and carried a paraphrase in place of its
title.** *Superseded, retained:* *"Wu M, et al. Chondroitin sulfate sulfation machinery. Front Cell Dev
Biol 2021."* The record for PMID 34966741 names **Wu ZY** as first author and titles the work *"Glycogenes
in oncofetal chondroitin sulfate biosynthesis are differently expressed and correlated with immune
response in placenta and colorectal cancer."* No committed source carries "Wu M" or the paraphrased
title, so both entered the prose from something the repository cannot show. This is the 2026-08-07
failure mode in its milder form: a real identifier wearing a description nobody fetched.

**Reference 11 was dated "2022/2023".** The record for PMID 36316541 gives 2023, volume 36, issue 1,
pages 446-455. The hedge is replaced by the retrieved year.

**SUPERSEDED, RETAINED, AND THE SUPERSESSION IS THE POINT.** This appendix previously ended: *"Five
entries (6, 13, 16, 17, 18) are in neither retrieval and still carry their identifier alone; two (4, 5)
resolved with an author list, year, DOI and identifiers but no journal or pagination. Nothing was written
for any of the seven, because a field that is not in a retrieval is left missing."* That statement was
true when written and became false without being updated, which is the worst arrangement available: all
seven carried complete records in the live text while the paper's own provenance chain said nobody had
fetched them. The records exist. A third committed retrieval,
[`remaining-reference-metadata-2026-08-09.json`](../literature/remaining-reference-metadata-2026-08-09.json),
carries complete and matching bibliographic records for PMIDs 35974707, 34340159, 25613900, 30373828,
10537274, 12378528 and 28076709, and it is now named in the References preamble and in Data availability.
A Limitations sentence referring to *"citations marked in the reference list as not yet retrieved"* was
deleted in the same pass, because no reference carries such a mark. One entry, the NETTER-1 trial report
(PMID 28076709), was cited for a sentence about approved somatostatin-receptor radioligand therapy that
the 2026-08-10 revision removed, so it no longer appears in the reference list.

### Appendix A5 — reference-list repairs (2026-08-09)

| What it said | What it says now | Why |
|---|---|---|
| Reference 16 read *"Sjögren H, et al. EWSR1/NR4A3 fusion in extraskeletal myxoid chondrosarcoma"*, with no identifier | Sjögren H, Meis-Kindblom J, Kindblom LG, Aman P, Stenman G. Fusion of the EWS-related gene TAF2N to TEC in extraskeletal myxoid chondrosarcoma. *Cancer Res* 1999;59(20):5064-5067. PMID 10537274 | The original entry described no real paper. A retrieval returned three Sjögren papers on this disease and none is an EWSR1-fusion report: PMID 10537274 is the TAF15 fusion, PMID 11156374 the TCF12 fusion, PMID 12598313 a cytogenetic and microarray study. Tracing the entry through the pre-rewrite draft showed it entered as the placeholder *"[Sjögren; Panagopoulos; whole-genome characterisation citation to verify]"* attached to the sentence defining the fusion and its variant 5' partners. The entry is now the primary report of the variant that sentence names, and the two rejected candidates are recorded here so the identification can be checked |
| References 13 to 18 appeared in the list with no citation marker anywhere in the text | Each is cited at the sentence it supports | The cut from 11,740 to 4,553 words removed the citing sentences and left the entries. Each claim was located in the current text before a marker was restored, and no marker was placed on a sentence the source does not support |
| Reference 13, the machine-learning surfaceome resource, had no place in the text at all | Cited in Methods, with an explicit statement that it was *not* used and why | The surfaceome here is built from UniProt annotation. Citing that resource at the construction step would have implied it was the source. Stating that an established alternative exists and was not used is the accurate form, and it answers a question a reviewer would otherwise ask |
| Reference 14 sat nearest a sentence calling a cited work *"founding"* | Cited instead at the statement that a glycan is a pathway product rather than a gene product | That paper is a 2021 glycogene expression study, not the founding description of the antigen. Attaching it to *"founding"* would have misattributed it |

### Appendix A6 — the tissue read's criterion, and every count it changed (2026-08-10)

**THE SUPERSEDED CRITERION.** Until this revision the tissue read called a gene "moved" when |*t*| >= 2
on a platform, and every headline count in the abstract, Results and Conclusion was a count of genes
crossing that threshold. The Methods simultaneously described it as *"a readability aid rather than a
test"* and stated that *"No multiple-testing correction is applied anywhere in the tissue read"*. Two
things were wrong with that. A criterion cannot be disclaimed in Methods and carry the conclusion in the
abstract. And at these degrees of freedom the threshold is not conservative: the two-sided 95% critical
value is 2.48 at df 5.7, 2.31 at df 8.0 and 2.17 at df 12.4, so |*t*| >= 2 is **more permissive** than a
95% interval. The stage-1 surrogate scan had used Benjamini-Hochberg correction one step earlier, so the
two stages were held to different standards in the direction that flattered stage 2.

**What replaced it.** Alpha 0.05 with Benjamini-Hochberg correction within each platform, across every
gene on the 100-gene board that produced a contrast there: 95 genes on GPL6244, of which 24 reach
*q* < 0.05, and 78 on GPL3290, of which 16 do. Every contrast is recomputed from the committed
per-sample values, and every recomputed Δ, *t* and degrees-of-freedom value reproduces the committed one
before the statistics artifact is written. One home for the arithmetic:
[`emc_tissue_read_statistics.py`](../modalities/emc_tissue_read_statistics.py) →
`emc-tissue-read-statistics.json`.

**Every count the correction changed. Superseded values on the left, retained and quotable.**

| Claim, as previously written | Corrected |
|---|---|
| *"Eight antigens were selective in the surrogate"* | **18 of 47.** The eight named were CDH11, KIT, FGFR1, NCAM1, GPC2, PTK7, MCAM and EPHB4; Table 1 simultaneously marked nine "Selective: yes" by including CD248, and no published or committed rule produced either number. The reproducible rule is every actionable antigen with BH *q* < 0.05, which adds CD248, FGFR4, ALK, ENPP1, STEAP1, PDGFRB, ROR1, PDGFRA, DLL3 and SLC34A2 |
| *"None of the eight was concordantly elevated on both arrays"* | **None of the 13 with a tumour-tissue reading**, and the five without one (ALK, ENPP1, FGFR4, SLC34A2, STEAP1) are named rather than dropped |
| *"exactly five are concordantly elevated on both arrays: VCAN, BGN, CD44, GPC1 and ALCAM"* | **Three: VCAN, BGN and CD44.** GPC1 does not survive (GPL6244 *q* = 0.067) and ALCAM does not survive (GPL3290 *p* = 0.056, 95% interval [−0.02, +1.53], *q* = 0.16) |
| *"the surrogate's negatives transferred and its positives did not"* | **WITHDRAWN.** Its evidence was two antigens chosen from the six the table marked non-selective, and neither survives correction: EGFR is not significant on GPL3290 (*p* = 0.076, *q* = 0.19) and CD276's single-platform read is *p* = 0.034, *q* = 0.088. The paper's own table refuted it in the other direction, since CD44 at enrichment −3.89 and ALCAM at −1.45 are among the genes the tissue read nominates. The corrected statement is that the ranking predicted tissue behaviour in neither direction |
| *"the normal-tissue prior left no evaluated antigen both selective and restricted"*, and Figure 1's shaded quadrant annotated *"target-worthy (selective and restricted) — EMPTY"* | **WITHDRAWN.** DLL3 carries enrichment +0.29 at BH *q* = 0.0079 and a RESTRICTED window in the same two artifacts, so the intersection has exactly one member. DLL3 entered the prior as a classifier control, its margin is +0.29 log2TPM at a class mean of 1.53 with 11% of class lines above the expressed threshold, and it is flat in EMC tumour tissue on both arrays. Nothing about it is a statement about protein, surface localisation, receptor density, safety, a therapeutic window or any DLL3-directed agent |
| *"ALCAM rose on both arrays"* and the Discussion's *"a marker-grade result"* | **CORRECTED and WEAKENED.** ALCAM is elevated on GPL6244 (*q* = 0.0004) and uninformative on GPL3290. "Marker-grade" is withdrawn as an interpretive upgrade the data do not carry: no sensitivity, specificity or discrimination statistic is computed anywhere in this work. What remains is directional consistency across cohorts |
| *"the whole 13-gene stromal and matrix panel is lower in EMC on both platforms"*, promoted into the Discussion as a surviving negative | **WITHDRAWN as a negative.** *p* = 0.095 and *p* = 0.097, so the panel does not move on either platform under the rule applied to genes. Panels and genes are now judged alike |
| *"Six of these genes gained their first EMC-tissue array contrast in this work"* | **DELETED.** It was a priority claim resting on a screen the same paragraph said matched titles and abstracts only. The full-text screen that replaces it (S6) measures an absence in a named corpus and supports no priority claim |
| *"Surface-antigen prioritisation for EMC has had to run on surrogates because the disease was taken to be absent from usable public expression data"* | **RESCOPED** to this programme's own prior state. The deposits were known and cited, including as reference 7, which is the originating publication of one of the cohorts; what was missing was the probe-to-symbol bridge |
| *"Four limits of this instrument were computed"* | **Five.** The omitted fifth, that the scan holds no observation of FAP in this disease, is the one the FAP discussion rests on |
| *"CD248 and CD276 and SSTR2 are unreadable on GPL3290"*, read as a complete list | **Six**: CD248, CD276, SSTR2, GPC2, ROR1 and B4GALNT1 |
| Table 1's ALCAM *q* given as *"not significant"*; LRRC15's window given as *"not scored in this filter"* | ***q* = 1.0** and **ENHANCED_BROAD**; both values are in the artifacts and are now printed |
| Methods and SI S2 naming desmoplastic small round cell tumour as a class member | **CORRECTED.** It matched no line. Alveolar rhabdomyosarcoma, named in neither, did |
| Abstract's *"a 2,826-gene human surfaceome was ranked across a translocation-sarcoma DepMap class (n = 76 lines)"* | **2,826 candidates of which 2,692 were scanned; 76 class members of which 45 carry expression data** |
| Methods' *"Supplementary Tables S1 to S8"* against an SI that ended at S7 | The SI now ends at **S8**, and the added table is the excluded-sample list |

**What the correction did NOT change.** Every table value traced in review reproduced exactly, and no
arithmetic error was found anywhere in the previous version. The corrections above are all consequences
of the criterion and of set definitions, not of miscomputation. The negative gets firmer under
correction and the one antigen the paper carried forward stops surviving, so the direction of the
change is toward the paper's own conclusion rather than away from it.

### Appendix A7 — Figure 1 replaced (2026-08-10)

**THE WITHDRAWN FIGURE PLOTTED A COORDINATE NOTHING COMPUTED.** The previous Figure 1 placed candidate
antigens by cross-cancer selectivity against normal-tissue window tier, shaded the selective-and-restricted
region and annotated it *"target-worthy (selective and restricted) — EMPTY"*. The rendered image had a
marker inside that region: B4GALNT1, labelled *"(sel n/a)"* and drawn at x = 0, because the generator
substituted zero for a missing selectivity value. B4GALNT1 has no selectivity value in the scan artifact,
so a gene with no measurement was displayed at a measured selectivity of zero, inside a region captioned
empty. Two further defects: the display list was 13 antigens chosen by hand and omitted DLL3, GPC3, ALCAM,
CD248, ERBB2, LRRC15 and CSPG4, so the region's emptiness was a property of the list rather than of the
evaluated set; and the marker jitter came from Python's salted string hash, so the figure did not
reproduce between runs.

**The replacement** is a two-panel greyscale forest plot of the tissue read, one panel per array platform,
with the point estimate and exact 95% interval for every surrogate-selective antigen, every route-named
address and every gene elevated before correction. Significance is carried by fill and shape rather than
colour, and a gene not readable on a platform is drawn as an open triangle at the axis so an instrument
statement is visibly different from a null result. Every plotted coordinate is a computed value, there is
no hand-chosen display list, and the ordering is deterministic. Rendered by
[`emc_surface_figure.py`](../modalities/emc_surface_figure.py); source hashes in
`figures/emc-surface-figure-provenance.json`. The withdrawn PNG was deleted rather than retained, because
a figure containing a fabricated coordinate should not remain in the tree where it could be reused.

---
*Provenance: consolidates the stage-1 surfaceome scan (BH-corrected selectivity plus the ACH-001519
profile, whose EMC label is withdrawn by Appendix A1), the normal-tissue prior (controls behaved as
specified), the EMC-line data probe, the GSE4303 cross-check (superseded by the accession bridge), the
stage-2 EMC tumour-tissue read across three cohorts and three platform families with exact p, confidence
intervals and within-platform Benjamini-Hochberg correction, the two comparator-arm sensitivity analyses,
the measured limits of the stage-1 instrument, the 2026-08-09 prior-art screen and its 2026-08-10
full-text extension, two red-team passes
([`emc-surface-target-redteam.md`](./emc-surface-target-redteam.md)) and the 2026-08-05 line-identity
readout. All committed CPU/CI outputs; no GPU compute and no wet-lab work. No antigen is asserted as an
EMC-validated target, and no claim of safety, selectivity, efficacy or clinical readiness is made
anywhere.*
