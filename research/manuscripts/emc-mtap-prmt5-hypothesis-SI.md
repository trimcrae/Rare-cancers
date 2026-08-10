---
id: DOC-EMC-MTAP-PRMT5-SI
title: Supplementary information — PRMT5 in extraskeletal myxoid chondrosarcoma
level: L3
kind: manuscript
status: live
canonical_for: ["the methods and full tables behind the 2026-08-09 EMC PRMT5/MTAP reading"]
purpose: >
  Carry every method, every per-gene reading and every negative control behind the main text, so a
  reader can check each number against the artifact that owns it.
scope: >
  L3 supplementary. Two public archival expression series, one public sarcoma-line CRISPR panel, and
  a sequence analysis of committed fusion protein sequences.
  No experiment in EMC cells, no drug exposure, no patient.
audience: [maintainers, external reviewers, autonomous research agents, collaborators]
date: 2026-08-10
last_verified: 2026-08-10
related: [DOC-EMC-MTAP-PRMT5]
---

# Supplementary information

*Supplement to "The PRMT5 methylosome in extraskeletal myxoid chondrosarcoma: a fusion-class
rationale that survives and an MTAP-locus rationale that does not". Section numbers of the form 3.2
refer to the main text. Nothing here asserts efficacy, safety, a therapeutic window or clinical
readiness for any agent in any disease.*

---

## S1. Data sources and their reach

| source | what it is | what it can support | what it cannot |
|---|---|---|---|
| GSE24369 / GPL6244 | 6 EMC against 29 comparator sarcomas (17 low-grade fibromyxoid sarcoma, 6 desmoid fibromatosis, 6 myxofibrosarcoma), single-channel intensity; 42 samples deposited, 35 analysed | a within-array contrast between EMC and its comparators | absolute expression; anything about protein |
| GSE4303 / GPL3290 | 10 EMC against 6 comparators (3 dermatofibrosarcoma protuberans, 3 gastrointestinal stromal tumour), two-colour cDNA log-ratio; EMC hybridised against `CRH-mRNA`, DFSP against `CRH`, GIST against `UHR` | the same contrast, independently | absolute levels, since every value is a ratio against a reference pool; and a comparison of EMC with the GIST comparators that is free of the reference-pool difference |
| DepMap sarcoma CRISPR panel, public 24Q4 release (figshare article 27993248) | 91 screened sarcoma cell lines, of 176 sarcoma models in the release | whether a gene is required in this tissue class | anything about EMC, since the panel contains no EMC line; and any statement of selectivity, which S4 reports separately |

The comparator classes named for GSE24369 are the classifier's buckets read against the verbatim GEO
annotations. One bucket name and the annotation disagree, and the annotation governs: the six samples
the classifier buckets `fibrosarcoma` are annotated `Myxofibrosarcoma`, which the bucket matches on a
substring. Myxofibrosarcoma is a different entity, and it is the name used in the main text, in
figure 4 and here.

The third row is the binding limit of the whole study. No EMC cell line carrying the fusion appears
in any public dependency dataset. The one line on the curated record labelled EMC is recorded by
Cellosaurus as not harbouring an EWSR1 fusion, and it carries no CRISPR data. Every dependency figure
in the main text is therefore a transfer from other sarcomas, limited by the complete absence of an
EMC observation rather than by sample size.

## S2. Scoring rules

Per gene, each value in each sample is converted to a *z*-score against that array's own full probe
distribution, so a value is a position within that array and not a quantity comparable across
platforms. Each sample also carries its array percentile.

Per group, a score is the mean of its member genes' *z*, contrasted between EMC and the comparator
arm by Welch's *t* with Welch degrees of freedom. A *t* and its exact permutation *p* are uncorrected
for the number of genes examined; the correction is a separate procedure, reported in S5c and in main
text section 3.5, and every uncorrected value should be read beside its adjusted counterpart.

A curated group emits no score unless at least three genes are readable and coverage is at least 0.5.
A group failing that floor is reported as underpowered with no score emitted, which is an instrument
statement rather than a null result.

A gene with no probe mapping is recorded as unreadable, and its verdict states that the read could
not be taken. A missing probe is never recorded as an absence of expression.

## S3. Full per-group readings

| group | genes | GPL6244 | GPL3290 |
|---|---|---|---|
| PRMT5 methylosome | PRMT5, WDR77, RIOK1, CLNS1A | *t* = +3.11, Δ = +0.090, 4/4 readable | *t* = +3.89, Δ = +0.478, 3/4 readable |
| methionine-salvage context | MAT2A, AHCY, MTR, ADI1 | *t* = +4.26, Δ = +0.139, 4/4 | *t* = +2.07, Δ = +0.283, 4/4 |
| the locus | MTAP, CDKN2A, CDKN2B | *t* = −4.06, Δ = −0.188, 3/3 | underpowered, no score, 2/3 readable |
| PRMT family, control | PRMT1/2/3, CARM1, PRMT6/7/8/9 | *t* = +0.33, Δ = +0.013, 7/8 | *t* = +1.34, Δ = +0.126, 6/8 |
| proliferation, control | 11 cell-cycle genes | *t* = +0.44, Δ = +0.090, 11/11 | *t* = +2.91, Δ = +0.446, 11/11 |
| chondroid lineage, control | COL2A1, COL9A1, COL11A2, SOX5, SOX6 | *t* = +0.42, Δ = +0.027, 5/5 | *t* = −0.83, Δ = −0.179, 5/5 |
| Sm proteins, context only | SNRPB, SNRPD1/D3/E/G | *t* = +0.22, Δ = +0.014, 5/5 | *t* = +3.15, Δ = +0.296, 4/5 |

Δ is the EMC-minus-comparator difference in standard-deviation units of that array. The last four
rows are controls and context rather than four further hypothesis tests. The Sm row is context in the
strictest sense, because an array cannot see a methyl mark, so the abundance of PRMT5's canonical
substrates says nothing about whether PRMT5 is acting on them. The proliferation and chondroid group
scores in this table use the panel's own coverage rule and member list, while the adjustment in main
text section 3.6 uses a twelve-gene and an eight-gene score with a per-sample coverage floor, so the
two are close but not the same instrument (S10).

The locus reading gene by gene, which closed that rationale:

| gene | GPL6244 (powered) | GPL3290 | genome-wide rank of \|*t*\| |
|---|---|---|---|
| MTAP | +0.053 SD, flat, *t* = +0.69 | −0.607 SD, opposite sign | top 74% / top 26% |
| CDKN2A | −0.481 SD, *t* = −5.40 | +0.175 SD, reversed | top 3.5% / top 49% |
| CDKN2B | −0.136 SD | unreadable | top 34% / not applicable |

The group's *t* of −4.06 is accurate but is not a reading of MTAP. The therapeutic window selects on
MTAP loss, and MTAP does not move where the read is powered. A group score cannot distinguish the
two, and the gene-level reading is what closed the rationale.

## S4. The dependency prior in full

| gene | mean gene effect across the 91 screened sarcoma lines | fraction of those lines dependent | fraction of the non-sarcoma lines dependent | selectivity (rest mean minus sarcoma mean) |
|---|---:|---:|---:|---:|
| PRMT5 | −1.015 | 94.5% | 94.1% | +0.013 |
| MAT2A | −1.471 | 96.7% | 98.9% | −0.285 |
| MTAP | −0.075 | 0.0% | 0.1% | +0.007 |

This table bounds the route rather than supporting it, and the two right-hand columns bound it
harder than the two left-hand ones. A gene required in almost every line of a tissue class offers
little to select on; a gene required in almost every line of every tissue class offers nothing. PRMT5
is a dependency in 94.1% of the non-sarcoma lines as well, so its sarcoma selectivity is 0.013 on the
gene-effect scale, which is not distinguishable from none. The proliferation half of the transferred
result is therefore close to expected, and the part that could be specific to this disease is the
effect on fusion-driven transcription, which no public data measures.

The same panel says the same thing more sharply about a different route in this portfolio. Read on
2026-08-09 for the proteasome inhibitor carfilzomib, the only agent in this programme with ex-vivo
activity in patient-derived EMC models, the same 91 lines give PSMB1, PSMC1, PSMD1 and VCP at 100%
dependent and carfilzomib's own target PSMB5 at 97.8%, with selectivity against the rest of DepMap of
−0.10 to +0.17. A target required in every line of the class, and equally required outside it, offers
nothing to select on.

The group unit fails in both directions. For the locus, the group score reported a signal its
decisive gene (MTAP) did not have. For the methylosome, the group score hid a signal its decisive
gene (PRMT5) does have, since pooled across four genes EMC ranks second of four comparator classes
while PRMT5 alone is highest. Neither is visible without reading the constituent genes, so a curated
group score is treated here as a summary and not as a unit of evidence.

MTAP reading as a non-dependency is consistent with the panel being read correctly, and is weaker
than a positive control. A biomarker should not be a dependency and a target should, and the panel
separates them in the expected direction; but a gene can be a non-dependency for reasons that have
nothing to do with the instrument, so this is weak evidence and not a control the panel passes.

## S5. Negative and internal controls

A FET-fusion comparator sits inside the comparator arm. GSE24369's comparators include low-grade
fibromyxoid sarcoma (FUS::CREB3L2), a fusion sarcoma of the same family as EMC's driver. Main text
figure 4 plots the methylosome against each comparator class separately for that reason, since a
pooled arm would hide whether the reading is simply what a FET-fusion sarcoma looks like.

The source artifact's control block names six genes, each with an expectation written down before the
data were read. NR4A3 is expected up, because the fusion places NR4A3 sequence under the partner's
promoter and a read that does not recover it is an instrument failure rather than a biological
finding; the block also carries the pre-specified caveat that on a 3′-biased or EST-annotated array
the probe may sit in the region the fusion replaces, so a null there is a probe-placement question.
ENO3 is expected up as a published direct transactivation target of an NR4A3 fusion. MKI67 is
expected approximately flat, because a large proliferation difference would say the contrast is being
driven by cellularity. EWSR1, TAF15 and FUS carry no directional expectation and are FET-family
context. The block contains no housekeeping gene and no marker designated as comparator-high.

| control gene | expectation | GPL6244 | GPL3290 |
|---|---|---|---|
| NR4A3 | up in EMC | *t* = +4.66 | no panel contrast: *n* = 9 versus 2, below the three-per-arm floor. The genome-wide path, floor 2, gives +1.70 |
| ENO3 | up in EMC | *t* = +3.61 | *t* = +13.22 |
| MKI67 | approximately flat | *t* = +0.53 | *t* = +2.30, +1.24 SD |

MKI67 is the cellularity control and it moves on one platform. It reads as specified on the
35-tumour array and not on the 16-tumour one, in the same direction and on the same platform as the
twelve-gene proliferation score, so the two agree with each other and both disagree with the
expectation on GPL3290.

No proliferation-matched series exists, and the in-silico substitute for one disagrees between
platforms. Main text section 3.6 adjusts PRMT5 for a twelve-gene proliferation score read on all 35
and all 16 samples. It leaves the contrast largely intact on GPL6244 (*t* 6.24 to 5.23, where the
score is flat at *t* = 0.45) and takes most of it on GPL3290 (*t* 6.67 to 2.71, where the score is
itself elevated in EMC at *t* = 3.00 and correlates with PRMT5 at *r* = 0.60). The retained fractions
are 0.84 and 0.41 against the 60% threshold of main text section 2.4. The adjustment measures the
confound without resolving it, and falsifier F7 remains the most likely way both readings turn out to
be artefacts of cellularity or growth fraction.

### S5a. The reference-channel split on GPL3290

Every value on GPL3290 is a ratio to a reference channel, and the deposit records three references
(S1). Splitting the six-sample comparator arm by reference gives the following, with the pooled
contrast for comparison. Each split arm has three samples, so nothing here is a test; it is a check
on whether the pooled contrast is carried by the half that differs in the denominator of the
measurement.

| gene | vs 3 DFSP (`CRH`) | vs 3 GIST (`UHR`) | pooled, 6 comparators |
|---|---:|---:|---:|
| PRMT5 | +5.97 | +4.32 | +6.67 |
| MAT2A | +2.18 | +4.79 | +4.10 |
| MTAP | −1.59 | −2.60 | −2.27 |
| CDKN2A | +1.11 | +1.10 | +1.33 |
| ENO3 | +13.52 | +9.29 | +13.22 |
| MKI67 | +1.09 | +2.06 | +2.30 |
| CLNS1A | +1.17 | +2.40 | +1.99 |

The primary contrast keeps its direction and most of its size against either half, so the
reference-pool difference does not manufacture it. Two readings are less stable. MAT2A falls from
4.10 pooled to 2.18 against the label-matched half. MKI67, the cellularity control, falls from 2.30
to 1.09 against that half, which is the direction that would be expected if part of the GPL3290
proliferation signal were a reference-pool artefact rather than a growth-fraction difference. That
does not decide the platform disagreement of main text section 3.6, and a three-sample arm could not;
it names a candidate the manuscript did not previously disclose.

### S5b. Excluded samples and the exclusion sensitivity

GSE24369 deposits 42 samples and the analysis scores 35. Two pooled skeletal-muscle RNA samples were
excluded by design. Five solitary fibrous tumours were excluded because the classifier carried no
pattern for that histology; that was not a designed exclusion, and it is disclosed for that reason.
Restoring the five to the comparator arm moves the primary contrasts very little.

| gene | as reported, 6 versus 29 | with the five restored, 6 versus 34 |
|---|---:|---:|
| PRMT5 | +6.24 | +6.31 |
| MAT2A | +4.13 | +3.98 |
| MTAP | +0.69 | +0.70 |
| CDKN2A | −5.40 | −5.66 |
| NR4A3 | +4.66 | +3.61 |
| ENO3 | +3.61 | +3.66 |

The per-class comparison is affected where the pooled contrasts are not. Per-class medians on
GPL6244, drawn in figure 4, are: for PRMT5, EMC +1.30, solitary fibrous tumour +1.05, desmoid
fibromatosis +1.05, low-grade fibromyxoid sarcoma +1.04, myxofibrosarcoma +0.94, and the two pooled
skeletal-muscle samples +1.34; for the four methylosome genes pooled, pooled muscle +1.11, desmoid
fibromatosis +0.95, solitary fibrous tumour +0.94, EMC +0.93, low-grade fibromyxoid sarcoma +0.86,
myxofibrosarcoma +0.83. EMC is therefore highest of the tumour classes on PRMT5 alone and third of
five on the pooled score, and the class that sits second on PRMT5 is the one that was dropped. The
two normal-muscle samples are not a comparator and are drawn as such, but their position above EMC on
PRMT5 is the plainest available statement of what a within-array *z* does and does not show.

### S5c. The multiplicity correction

The procedure is described in main text section 2.3. On GPL3290 all 8,008 labellings are enumerated,
so that column is exact; on GPL6244 20,000 labellings were drawn under a fixed seed and the
Monte-Carlo standard error on an adjusted *p* near 0.2 is about 0.003.

| gene | GPL6244 adjusted *p* | GPL3290 adjusted *p* |
|---|---:|---:|
| PRMT5 | 0.21 | 0.24 |
| MAT2A | 0.98 | 0.97 |
| WDR77 | 1.00 | unreadable |
| MTAP | 1.00 | 1.00 |
| CDKN2A | 0.51 | 1.00 |
| CDKN2B | 1.00 | unreadable |
| NR4A3 | 0.85 | not scored, arm of two |
| ENO3 | 1.00 | 0.010 |
| MKI67 | 1.00 | 1.00 |

The family is 5,449 symbols on GPL6244 and 4,848 on GPL3290, against mapped-symbol universes of
18,724 and 14,932, so each value is a lower bound. How fast the bound rises with the number of
symbols scanned is measured on the random symbols alone, which are a uniform sample of the array:
PRMT5's adjusted *p* on GPL6244 is 0.016 over 250 random symbols, 0.055 over 1,000 and 0.168 over
3,973; on GPL3290 it is 0.037, 0.062 and 0.208 over the same three family sizes. The curve is still
rising at the largest family the committed data supports, which is roughly a quarter of each array.
Reaching the whole array would need the full probe matrix, which exists only inside the fetch step
and is not carried by any committed file.

An adjusted *p* is a statement about how often a labelling of these samples produces a statistic this
large somewhere in the family. It is not a statement that a reading is absent, which matters most for
the two controls that read as expected and still do not clear a threshold.

## S6. Figures and their sources

| figure | drawn from | reading |
|---|---|---|
| 1, readings per tumour | `emc-expression-panels.json`, `gene_reads[*].per_sample` | every tumour is visible; medians are bars |
| 2, the locus gene by gene | same | closed the MTAP rationale: MTAP flat, CDKN2A carrying the signal and reversing across platforms |
| 3, dependency qualifier | `depmap-sarcoma-dependency.json` | argues against the proliferation reading |
| 4, pooled against single gene, per class | `emc-expression-panels.json`, plus `emc-prmt5-multiplicity.json` for the classes the panel's arms exclude | pooled, EMC is third of five tumour classes; PRMT5 alone separates it from the other tumour classes, and two pooled normal-muscle samples read above it |
| 5, the motif map | `emc-prmt5-substrate-motif-map.json` | the commonest EMC fusion and two of the three reported clear cell junctions keep the same four sites; the third clear cell junction and EWSR1::FLI1, drawn beside them, keep none |

Provenance hashes for all five are stamped in
`research/manuscripts/figures/mtap-prmt5-figure-provenance.json`, and `--check` compares them against
the artifacts, so a stale figure is detectable.

## S7. Failure modes

1. The contrasts are cellularity or proliferation artefacts. Both readings would then be real
   measurements of the wrong thing, and nothing here excludes it.
2. This failure mode has already occurred. The locus reading is a CDKN2A shadow: MTAP is flat where
   the read is powered and CDKN2A reverses on the second platform. The MTAP rationale is closed at
   transcript level, and figure 2 is where it became visible. The entry is retained rather than
   deleted because it records a failure mode that fired.
3. The clear cell sarcoma transfer does not hold. EWSR1-ATF1 and EWSR1::NR4A3 share a 5′ partner and
   an architecture, not a DNA-binding domain or a target repertoire. Two things now argue against
   this failure mode without removing it: a second EWSR1-fusion sarcoma with a fusion-dependent PRMT5
   requirement, and the finding that the commonest fusion of each disease retains the same number of
   PRMT5-motif sites (S9). Both are arguments about plausibility, neither is an observation in EMC,
   and this entry stays open until one is.
4. The methylosome elevation is generic. Elevated PRMT5 is reported across many malignancies, and
   abundance is not dependency.
5. Every reading above is at transcript level. No claim in the manuscript has been tested in a cell
   carrying this fusion, because no such cell is available to this work.

## S8. Artifacts

Every number in the main text and in this supplement resolves to one of:

- `research/modalities/emc-expression-panels.json`, the readings, and the one home of every *z*,
  percentile and group score
- `research/modalities/census-route-expression-grading.json`, the grading of this route against its
  own selection criterion
- `research/modalities/depmap-sarcoma-dependency.json`, the sarcoma-line dependency prior
- `research/modalities/emc-prmt5-route-controls.json`, the control calculations of main text
  section 3.6
- `research/modalities/emc-prmt5-substrate-motif-map.json`, the motif counts of S9 and the two
  double-entry checks against the artifacts that already held the RG numbers
- `research/modalities/emc-fet-construct-designs.json` and
  `research/modalities/emc-fet-idr-census.json`, the committed protein sequences and sourced
  breakpoints the motif map reads; neither was produced for this manuscript, which is why they can
  check it
- `research/literature/mtap-prmt5-emc-citations.json`, the citation anchor, in which every identifier
  used in the main text appears, read from a retrieval rather than recalled
- `research/literature/emc-prior-art-2026-08-09.json`, the Europe PMC prior-art screen of main text
  section 1.3, with its retrieval record and its own statement of what a title-and-abstract screen
  can and cannot show

## S9. The substrate-motif map

The motif is GRG, taken from a retrieval rather than from recollection: PRMT5's preference for
arginine flanked by glycines is reported from genome-wide methylation profiling after selective PRMT5
inhibition, with in vitro methylation used to validate the hits (main text reference 8). That
reference was verified at metadata and abstract level from the retrieved Europe PMC record; its full
text is not open access and was not read, which is stated because the motif definition is the
foundation of this whole section. A mapping experiment in a different substrate agrees, since only
the DDX5 fragment carrying the C-terminal RGG/RG motif was methylated by PRMT5 (main text
reference 9), and that one was read in full.

Three EWSR1::ATF1 junctions are recorded in the source artifact and all three are reported: EWSR1
exon 8 retaining 324 residues and four GRG sites, exon 10 retaining 348 residues and four sites, and
exon 7 retaining 264 residues and none. The main text and figure 5 previously showed the first alone.
Two of three matching the commonest EMC fusion is what the artifact supports, and the third shows
that the match is a property of particular junctions rather than of the fusion class.

Occurrences are counted by exact string scan on the committed protein sequences, with overlaps
included, because GRGRG is two sites and two methylatable arginines and a non-overlapping scan would
report one and silently halve a poly-RG tract. A fusion's retained 5′ sites are those at or before
`five_prime_residues_fully_encoded`, excluding the seam residue, because every one of these junctions
splits a codon and the seam residue is encoded by both partners.

GRG is computed nowhere else in this repository, so nothing can check it directly. What can be
checked is the half this module shares with two existing artifacts:

| check | result |
|---|---|
| every re-derived RG count against the count `emc-fet-idr-census.json` and `emc-fet-construct-designs.json` already hold | agrees for all four wild-type proteins and all four measured comparator fusions |
| each fusion's own RG count against its retained 5′ half plus NR4A3's contribution, which exercises the construct sequences that the check above never touches | holds for all four constructs |

The RG axis and the GRG axis are not the same quantity, and both are reported side by side. This
repository's RG counts were adopted for a different mechanism, FET protein suppression of ATM
signalling and double-strand-break recruitment, and carry no methylation meaning; one must not be
substituted for the other.

The map cannot show that any fusion is methylated, name the enzyme, or predict response. The one
disease in which a PRMT5 requirement has been shown to be fusion-dependent, Ewing sarcoma with
EWSR1::FLI1, retains zero sites. That fact is stated in the artifact's own limits and asserted by a
test, and it is why the table cannot be read as a response predictor.

## S10. The control calculations

Exact permutation. Every assignment of the observed *z* values to arms of the observed sizes is
enumerated and Welch's *t* recomputed; the two-sided *p* is the fraction with |*t*| at least the
observed. No random sampling is used anywhere in this implementation of the test, so the value is
exactly reproducible. On GPL3290 the smallest attainable *p* is 1/8,008, so the test's resolution is
the sample size.

Confound adjustment. A per-sample score is the mean *z* of the readable members of the named set;
PRMT5 is regressed on it by ordinary least squares with one covariate and an intercept, and the
EMC-versus-comparator contrast recomputed on the residuals. A contrast is called surviving if it
keeps its sign and at least 60% of its magnitude, a threshold chosen for this work rather than taken
from an established convention; the raw and adjusted values are both reported.

Coverage. The proliferation score uses twelve genes and scores all 35 and all 16 samples; the
chondroid score uses eight and scores 35 and 14. A proxy still makes a null weak evidence, since a
confound the proxy measures badly passes through the adjustment untouched, so a surviving result is
a much weaker statement than a failing one; the failure on GPL3290 is the stronger direction of the
same instrument.

Group scores for the adjustment. A per-sample score is the mean *z* of the member genes that sample
has a value for, provided it has at least 60% of them. It is a coverage-weighted mean rather than an
intersection: requiring every member gene would drop GPL3290 from 16 samples to 9, so adding genes
to the definition would have reduced the sample without that being visible in the output. The floor
stops a sample scoring off one stray gene while keeping all sixteen.

The genome-wide null. The same statistic is computed for every symbol the platform's probes map to
(18,688 on GPL6244; 14,404 of the 14,932 carrying a probe on GPL3290), and each gene of interest
placed in that distribution. It is computed at fetch time because that is the only point at which the
full probe matrix exists. It double-enters the panel, since the null recomputes from the raw matrix,
by a separate code path, the statistic the panel computes from reduced per-gene values, and a wanted
gene's *t* must agree between them. It does, for every gene both paths score on both platforms: 404
genes on GPL6244 and 362 on GPL3290, none disagreeing. The two paths do not use the same minimum arm
size, the null requiring two values per arm and the panel three, so the check cannot vouch for a gene
the panel did not score.

Missing values. A sample with no value for a gene is dropped from that gene's contrast and never
imputed. On GPL6244 every cached gene has a value in every sample. On GPL3290 578 of 1,662 cached
genes (34.8%) have at least one missing value and 51 (3.1%) have an arm below three, which is why one
instrument control carries a genome-wide rank and no panel contrast.

The multiplicity correction. Its method is in main text section 2.3 and its results in S5c. It
re-derives every observed *t* from the input cache and refuses to run if any disagrees with the
committed panel value, so the correction cannot be computed on a statistic that is not the published
one.

Status. The PRMT family, the fuller proliferation set, the Sm substrates, the additional chondroid
markers and the genome-wide null were added to the panel definition on 2026-08-09 and fetched the
same day; every figure in main text sections 3.5 and 3.6 is read from that fetch.

---

## Appendix S1. Corrections register

Per [CLAUDE.md](../../CLAUDE.md) rule 1.2, superseded numbers are recorded rather than silently
dropped. A retracted value stays quotable unless the record says it was retracted, and a live text
carrying a "was X, now Y" narrative leaves both in circulation. So the live text carries only the
current figure and this appendix carries the rest. It is the full register; the main text's Appendix
A carries the subset that lived in the main text.

| where | was | is | why it moved |
|---|---|---|---|
| §S10 and main text §2.3, the genome-wide null's symbol counts | 18,474 and 14,402 | **18,688 on GPL6244; 14,404 of 14,932 with a probe on GPL3290** | ⛔ **THE SUPERSEDED PAIR IS IN NO COMMITTED ARTIFACT AT ANY POINT IN THIS REPOSITORY'S HISTORY**, which is the same failure class as the *MTAP* −0.023 row below and was found the same way — by reading the artifact instead of the prose. Both correct values are carried independently by `emc-prmt5-route-controls.json` (`per_platform.*.genome_wide_placement.n_symbols_scored`) and `emc-expression-panels.json` (`platforms.*.genome_wide_null`). ⚠ It also falsified main text §2.6's claim that every reported value had been verified against its artifact, so that sentence was rewritten to say what was checked |
| §S2, on multiplicity | *Superseded, retained: "No multiplicity correction is applied anywhere, and every reported t must be read with that in mind."* | a max-statistic permutation correction is run and reported (§S5c) | it was true when written and is no longer. The uncorrected values are not withdrawn — they answer a different question and are reported beside the adjusted ones |
| §S5, the instrument-control paragraph | *Superseded, retained: "The instrument-control read, covering housekeeping recovery and a marker expected high in the comparator arm rather than in EMC, is carried in the source artifact's control block and is not restated here."* | the six genes actually in the block, with their pre-specified expectations and both platforms' values | ⛔ **THE SENTENCE DESCRIBED A CONTROL THAT WAS NEVER RUN.** The block contains NR4A3, ENO3, MKI67, EWSR1, TAF15 and FUS: no housekeeping gene, and no marker designated comparator-high. A reader was told a control existed that did not, and one that DID exist — the pre-specified MKI67 cellularity reference, which moves on GPL3290 — was not reported anywhere. Suppressing a pre-specified control that fires is the one thing a paper of this kind cannot do, and this was inadvertent rather than deliberate, which is exactly why the register records it |
| §S6, figure 4's reading | "pooled, EMC ranks second below desmoid; PRMT5 alone separates" | EMC is third of five tumour classes pooled; PRMT5 alone separates it from the other tumour classes | the figure drew only the samples inside the panel's arms, so five solitary fibrous tumours and two pooled skeletal-muscle references were absent from a figure whose subject is the comparison between classes (§S5b) |
| §S9, the motif comparison | one EWSR1::ATF1 junction shown, retaining four sites | all three reported junctions: four, four and none | three are recorded in the source artifact and the cleanest was the one shown |
| §3, *PRMT5* EMC-minus-comparator | +0.266 and +0.744 SD | **+0.263 and +0.816 SD** | the values had drifted from `emc-expression-panels.json`, which is their one home. Checked 2026-08-09 against the committed artifact; the second differs by 0.07 SD and the reading is unchanged in direction or size class |
| §3, the statistic quoted for route 1 | the methylosome **group** *t* (3.11, 3.89) | additionally the **gene's own** *t* (6.24, 6.67) | the group score is not the unit route 1 depends on — the same error §S4 records in the other direction for the locus. The group figures are not withdrawn; they were simply the wrong ones to lead with |
| §3/§S3, the locus genes | *MTAP* −0.023 / −0.389; *CDKN2A* −0.399 / +0.173; *CDKN2B* −0.096 | **+0.053 / −0.607; −0.481 / +0.175; −0.136** | ⛔ **CAUSE NOT ESTABLISHED, AND AN EARLIER EXPLANATION HERE WAS WRONG.** *Superseded, retained: "a re-fetch ran on a NARROWER probe→symbol bridge (0.931 against 0.984), and a narrower bridge changes which probes map."* That was a story built on a coincidence. Checked against every committed version of the artifact: ***MTAP* reads +0.053 in all of them — at bridge rates 0.984, 0.931 AND 0.981**, and always on one mapped probe. Bridge width does not move this gene. The −0.023 appears in **no committed artifact at all**, so it entered the prose from a source this repository cannot show, and the live values are the ones the artifact has always carried |
| §3.1/§S4, the dependency denominator | "across 176 sarcoma cell lines" | **"across the 91 screened sarcoma cell lines"** | ⛔ a real error, in the direction that overstated the evidence base, and it was in four places including the abstract. The release lists 176 sarcoma MODELS; only **91** carry CRISPR gene-effect data, and every per-gene record in the artifact says `n_sarcoma: 91`. The percentages themselves are unchanged — they were always computed on the screened subset — but they were being attributed to a denominator almost twice its true size. Caught 2026-08-09 by a later run that added a second gene group and printed the same 91 |
| §7, the fusion-class transfer | "an assumption" | "argued rather than assumed" | a peer-reviewed fusion-dependent PRMT5 result in a second EWSR1-fusion sarcoma, and the motif match of §S9. ⚠ Still not an EMC observation |
| §S5, the proliferation control | *Superseded, retained: "No proliferation-matched control exists."* | one is now run, and it disagrees between platforms | the in-silico substitute is reported in §S5 and in main text §3.6. It is a measurement, not a resolution |
| §S11 status line | *Superseded, retained: an earlier version reported the added panel members as pending.* | they were fetched on 2026-08-09 | the re-fetch landed the same day |
| this file's own register | §S10, numbered in sequence with the method sections | Appendix S1 | `lint_style.py` exempts sections under an `Appendix` heading, because superseded-value bookkeeping is required by rule 1.2 and belongs in an appendix rather than in running text. The content is unchanged |
| both files' register | repository house style throughout: glyph warnings, bold on the load-bearing clause, sentence-shaped headings, running commentary on the paper's own honesty | journal register in the running text, with the house-style rows preserved verbatim inside this appendix | the register was correct for a maintainer and wrong for a journal reader. No measured statement was removed. The rows above are left in their original wording rather than rewritten, because a corrections register that is itself edited is no longer a record |

⭐ **AND THE THIRD ROW IS A LESSON ABOUT THIS WORK'S OWN METHOD, WHICH IS WHY IT IS NOT JUST
BOOKKEEPING.** A plausible mechanism was available — the annotation bridge narrowed on the same day
the numbers were noticed to differ — and it was written down as the cause without the one check that
could separate it from coincidence. The check was a `git log` over the artifact, it was free, and it
refutes the explanation: **four committed versions, three different bridge rates (0.984, 0.931,
0.981), and *MTAP* reads +0.053 in every one of them.** ⛔ **The −0.023 is in no committed artifact**,
so what was corrected was a stale figure in the prose rather than a value that moved.
⭐ **What survives, and is now measured rather than asserted: every figure this manuscript quotes is
stable across three independent annotation bridges** — *PRMT5* +0.2632 and *MTAP* +0.053 at all
three — which is a stronger statement about reproducibility than the one it replaces.

⚠ **The bridge itself is volatile and the values are not, which is the useful pair.** The
accession→symbol step was re-run four times on 2026-08-09 and resolved 0.984, 0.931, 0.931 and 0.981
of GPL6244's accessions — the middle two returning **zero** gene links from NCBI in ~15 minutes each,
the endpoint having briefly stopped answering and then recovered. **None of that moved a number this
manuscript quotes.** The bridge now has a committed home so a future outage cannot narrow it at all.
