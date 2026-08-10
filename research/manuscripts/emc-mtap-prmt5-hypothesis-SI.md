---
id: DOC-EMC-MTAP-PRMT5-SI
title: Supplementary information — PRMT5 and the MTAP locus in extraskeletal myxoid chondrosarcoma
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
  The YAML frontmatter and the appendix are repository record and are removed at submission.
audience: [maintainers, external reviewers, autonomous research agents, collaborators]
date: 2026-08-10
last_verified: 2026-08-10
related: [DOC-EMC-MTAP-PRMT5]
---

# Supplementary information

*Supplement to "PRMT5 and the MTAP locus in extraskeletal myxoid chondrosarcoma: two rationales
tested against the available public data, neither supported". Section numbers of the form 3.2 refer
to the main text. Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness
for any agent in any disease.*

---

## S1. Data sources and their reach

| source | what it is | what it can support | what it cannot |
|---|---|---|---|
| GSE24369 / GPL6244 | 6 EMC against 29 comparator sarcomas (17 low-grade fibromyxoid sarcoma, 6 desmoid fibromatosis, 6 myxofibrosarcoma), single-channel log2 intensity; 42 samples deposited, 35 analysed | a within-array contrast between EMC and its comparators | absolute expression; anything about protein; anything about a representative EMC population, since the deposit is an LGFMS study |
| GSE4303 / GPL3290 | 10 EMC against 6 comparators (3 dermatofibrosarcoma protuberans, 3 gastrointestinal stromal tumour), two-colour cDNA log2 ratio; EMC hybridised against `CRH-mRNA`, DFSP against `CRH`, GIST against `UHR` | a description of the same contrast, as a consistency check | any contrast in which disease class is separable from batch, reference pool or platform assignment; absolute levels, since every value is a ratio against a reference pool |
| DepMap sarcoma CRISPR panel, public 24Q4 release (figshare article 27993248), Chronos gene effect | 91 screened sarcoma cell lines, of 176 sarcoma models in the release | whether a gene is required in this tissue class | anything about EMC, since the panel contains no EMC line; and any statement of selectivity, which S4 reports separately |

What GSE24369 is bears on every claim built on it. Its deposited title is "Gene expression profiling
of low-grade fibromyxoid sarcoma (LGFMS)" and its summary reads "Analysis of gene expression in 17
low-grade fibromyxoid sarcoma (LGFMS) samples compared to that of histologically similar tumors… The
results identifies a LGFMS-specific gene expression profile". GEO carries no linked publication for
it. Its six EMC cases were therefore selected as morphological mimics of a different entity, and the
17-sample class the main text uses as a FET-fusion control is the depositors' index arm. Neither
deposit records molecular confirmation of the EMC diagnoses.

GPL3290 is structurally confounded and section 2.1 of the main text sets out the four collinear
strata. The per-array covariates that follow from them:

| sample | class | reference label | probes with a value | background mean |
|---|---|---|---:|---:|
| GSM89883 | DFSP | `CRH` | 30,552 | −0.397 |
| GSM89898 | DFSP | `CRH` | 41,510 | −0.133 |
| GSM89924 | DFSP | `CRH` | 38,458 | −0.247 |
| GSM91381 | GIST | `UHR` | 32,032 | −0.426 |
| GSM91397 | GIST | `UHR` | 26,029 | −0.426 |
| GSM91405 | GIST | `UHR` | 28,381 | −0.425 |
| GSM98495 | EMC | `CRH-mRNA` | 34,303 | −0.644 |
| GSM98496 | EMC | `CRH-mRNA` | 29,752 | −0.574 |
| GSM98499 | EMC | `CRH-mRNA` | 23,015 | −0.634 |
| GSM98503 | EMC | `CRH-mRNA` | 40,721 | −0.345 |
| GSM98506 | EMC | `CRH-mRNA` | 26,861 | −0.521 |
| GSM98509 | EMC | `CRH-mRNA` | 35,438 | −0.707 |
| GSM98510 | EMC | `CRH-mRNA` | 26,929 | −0.608 |
| GSM98511 | EMC | `CRH-mRNA` | 41,450 | −0.392 |
| GSM98512 | EMC | `CRH-mRNA` | 39,476 | −0.704 |
| GSM98513 | EMC | `CRH-mRNA` | 34,834 | −0.676 |

Arm means are 33,278 probes and −0.581 background for EMC, 36,840 and −0.259 for DFSP, 28,814 and
−0.426 for GIST. Because the *z* is taken against each array's own probe distribution, a *z* on this
platform is a position within a probe set that differs by up to 18,000 probes between arrays.

The comparator classes named for GSE24369 are the classifier's buckets read against the verbatim GEO
annotations. One bucket name and the annotation disagree, and the annotation governs: the six samples
the classifier buckets `fibrosarcoma` are annotated `Myxofibrosarcoma`, which the bucket matches on a
substring. Myxofibrosarcoma is a different entity, and it is the name used in the main text, in
figure 4 and here.

The third row of the first table is the binding limit of the whole study. No EMC cell line carrying
the fusion appears in any public dependency dataset. The one line on the curated record labelled EMC
is recorded by Cellosaurus as not harbouring an EWSR1 fusion. Every dependency figure in the main
text is therefore a transfer from other sarcomas, limited by the complete absence of an EMC
observation rather than by sample size.

Reference [10] of the main text profiled three further EWSR1::NR4A3-positive EMC tumours on
Affymetrix U133A against 137 samples of five other sarcoma types. A GEO search of six committed
queries returned 56 records and no deposit corresponding to that study, and its own text records its
comparison sarcomas as unpublished data, so it could not be re-analysed here. The main text's claim
is accordingly about publicly deposited data.

## S2. Scoring rules

Per gene, each value in each sample is converted to a *z*-score against that array's own full probe
distribution, so a value is a position within that array and not a quantity comparable across
platforms. Each sample also carries its array percentile.

Per group, a score is the mean of its member genes' *z*, contrasted between EMC and the comparator
arm by Welch's *t* with Welch degrees of freedom. A *t* and its exact permutation *p* are uncorrected
for the number of genes examined; the correction is a separate procedure, reported in S5c and in main
text section 3.5, and every uncorrected value should be read beside its adjusted counterpart.

A curated group emits no score unless at least three genes are readable and coverage is at least 0.5.
A group failing either floor is reported as underpowered with no score emitted, which is an
instrument statement rather than a null result.

A gene with no probe mapping is recorded as unreadable, and its verdict states that the read could
not be taken. A missing probe is never recorded as an absence of expression.

Every contrast is also reported as a difference on the array's own log2 scale with a 95% Welch
interval. On GPL6244 that converts to a fold difference; on GPL3290 it does not, because the arms do
not share a reference pool. No variance moderation was applied, and the standard-error percentile of
each reported gene within its platform is given in main text Table 5.

## S3. Full per-group readings, and the locus per tumour

| group | genes | GPL6244 | GPL3290 |
|---|---|---|---|
| PRMT5 methylosome | PRMT5, WDR77, RIOK1, CLNS1A | *t* = +3.11, Δ = +0.090, 4/4 readable | *t* = +3.89, Δ = +0.478, 3/4 readable |
| methionine-salvage context | MAT2A, AHCY, MTR, ADI1 | *t* = +4.26, Δ = +0.139, 4/4 | *t* = +2.07, Δ = +0.283, 4/4 |
| the locus | MTAP, CDKN2A, CDKN2B | *t* = −4.06, Δ = −0.188, 3/3 | underpowered, no score, 2/3 readable |
| PRMT family, control | PRMT1/2/3, CARM1, PRMT6/7/8/9 | *t* = +0.33, Δ = +0.013, 7/8 | *t* = +1.34, Δ = +0.126, 6/8 |
| proliferation, control | 11 cell-cycle genes | *t* = +0.44, Δ = +0.090, 11/11 | *t* = +2.91, Δ = +0.446, 11/11 |
| chondroid markers, control | COL2A1, COL9A1, COL11A2, SOX5, SOX6 | *t* = +0.42, Δ = +0.027, 5/5 | *t* = −0.83, Δ = −0.179, 5/5 |
| Sm proteins, context only | SNRPB, SNRPD1/D3/E/G | *t* = +0.22, Δ = +0.014, 5/5 | *t* = +3.15, Δ = +0.296, 4/5 |

Δ is the EMC-minus-comparator difference in standard-deviation units of that array. None of these is
corrected for multiplicity. The last four rows are controls and context rather than four further
hypothesis tests. The Sm row is context in the strictest sense, because an array cannot see a methyl
mark, so the abundance of PRMT5's canonical substrates says nothing about whether PRMT5 is acting on
them. The proliferation and chondroid group scores in this table use the panel's own coverage rule
and member list, while the adjustment in main text section 3.6 uses a twelve-gene and an eight-gene
score with a per-sample coverage floor, so the two are close but not the same instrument (S10).

Effect sizes for every reported gene, on each array's own log2 scale with a 95% Welch interval. The
fold column applies to GPL6244 only, because on GPL3290 the arms do not share a reference pool.

| gene | GPL6244 difference (95% CI) | fold | GPL3290 difference (95% CI) |
|---|---|---:|---|
| PRMT5 | +0.544 (+0.375, +0.713) | 1.46 | +1.094 (+0.688, +1.499) |
| MAT2A | +0.722 (+0.344, +1.100) | 1.65 | +1.012 (+0.445, +1.579) |
| WDR77 | +0.213 (+0.062, +0.365) | 1.16 | unreadable |
| MTAP | +0.121 (−0.223, +0.465) | 1.09 | −1.377 (−2.244, −0.510) |
| CDKN2A | −0.923 (−1.292, −0.555) | 0.53 | +0.090 (−0.403, +0.583) |
| CDKN2B | −0.254 (−0.556, +0.049) | 0.84 | unreadable |
| NR4A3 | +1.457 (+0.724, +2.191) | 2.75 | +0.281 (−0.429, +0.991), arm of two |
| ENO3 | +1.568 (+0.475, +2.660) | 2.96 | +6.261 (+5.047, +7.474) |
| MKI67 | +0.266 (−0.835, +1.367) | 1.20 | +1.712 (−0.628, +4.053) |

Minimum detectable effects, being the smallest true difference the design would detect in 80% of
repetitions against a two-sided uncorrected 0.05, are 1.48-fold for *MTAP* on GPL6244 and a
relative difference of 2.59 on GPL3290; for *PRMT5* they are 1.22 and 1.46. Against the family-wise
threshold the main text actually applies they are several times larger.

The locus reading gene by gene:

| gene | GPL6244 (powered) | GPL3290 | array percentile in EMC | genome-wide rank of \|*t*\| |
|---|---|---|---|---|
| MTAP | +0.053 SD, flat, *t* = +0.69 | −0.607 SD, *t* = −2.27 | 72nd / 13th | top 74% / top 26% |
| CDKN2A | −0.481 SD, *t* = −5.40 | +0.175 SD, *t* = +1.33 | 53rd / 71st | top 3.5% / top 49% |
| CDKN2B | −0.136 SD, *t* = −2.03 | unreadable | 57th / not applicable | top 34% / not applicable |

### S3a. The per-sample 9p21 reading

A group mean is mis-specified for a subset event, so every tumour was read individually. An EMC
tumour is an *MTAP*-low candidate when its *MTAP* reading falls below every comparator on the same
platform, on both the within-array *z* and the array percentile; the two criteria select the same
samples. Because *MTAP* loss implies *CDKN2A* loss, a tumour is called deletion-consistent when it is
a candidate and its *CDKN2A* also sits below the 25th percentile of its own array.

| sample | MTAP percentile | MTAP *z* | CDKN2A percentile | CDKN2A *z* | MIR31HG percentile | MLLT3 percentile |
|---|---:|---:|---:|---:|---:|---:|
| GSM98511 | 1.1 | −2.79 | 89.3 | +1.08 | 52.2 | 62.8 |
| GSM98506 | 4.0 | −1.85 | 68.3 | +0.35 | 55.5 | 75.0 |
| GSM98503 | 4.6 | −1.65 | 73.2 | +0.48 | 28.7 | 91.0 |
| GSM98510 | 5.5 | −1.60 | 86.5 | +0.96 | 47.7 | 89.2 |
| GSM98499 | 10.4 | −1.21 | 50.5 | +0.09 | 40.6 | no value |

The lowest comparator sits at the 11.0th percentile for *MTAP*, the 56.7th for *CDKN2A*, the 29.6th
for *MIR31HG* and the 5.3rd for *MLLT3*. *MIR31HG* and *MLLT3* are 9p21 genes present in the
committed random-symbol cache rather than a designed panel, and no claim rests on them; they are
reported because a homozygous deletion large enough to remove *MTAP* and *CDKN2A* often removes
neighbours, so their reading is a second way the deletion story can fail. It does fail: no candidate
is low for any of the three.

Counts of deletion-consistent tumours, over a ladder of *CDKN2A* cuts so the answer does not rest on
one threshold: 0 of 5 candidates at the 5th, 10th, 25th and 50th percentile of their own arrays. At
the loosest criterion, *CDKN2A* below every comparator, one candidate qualifies at the 50.5th
percentile; that is not a floor criterion for this gene on this platform, because the comparator arm
reads high for *CDKN2A* and the criterion resolves to the 57th percentile. On GPL6244 no EMC tumour
is an *MTAP* low outlier at all, every one lying between the 67th and 82nd percentiles of its own
array. Within the EMC arm on GPL3290 the rank association between *MTAP* and *CDKN2A* is Spearman
*rho* = −0.31, exact two-sided *p* = 0.39 over all 3,628,800 rank permutations; on GPL6244 it is
+0.26, *p* = 0.66 over all 720.

Two controls on the candidate set, both of which had to fail for the candidates to mean anything.
Array dimness, being the fraction of each sample's cached genes below the 5th percentile of its own
array: the five candidates read 3.8%, 5.9%, 7.6%, 4.6% and 5.7% in the order tabulated above,
against a cohort range of 1.4% to 8.9%, so none is a globally dim array. Reference label: all ten
EMC tumours share `CRH-mRNA`, so a split within the EMC arm cannot come from the denominator of the
measurement.

One-sided 95% binomial upper bounds on the frequency of a deletion-consistent tumour, given the
observed count of zero: 39.3% on the six-tumour platform, 25.9% on the ten-tumour platform, and
17.1% across all sixteen. Reference [17] records MTAP protein loss reaching up to 20% in various
sarcomas and does not name this histology.

This is not a copy-number measurement. No threshold used here is a validated call, a transcript is
not a copy number, and an archival two-colour log-ratio carries no absolute level. It cannot
establish that any tumour does or does not carry a 9p21 deletion; it asks whether the per-sample
pattern is the one a co-deletion produces, and it is not. *MTAP* rests on one probe on GPL6244 and
two averaged probes on GPL3290, with no per-probe record committed, so a probe-level explanation for
the tail cannot be excluded here either.

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
gene (PRMT5) does have, since pooled across four genes EMC ranks third of the five tumour classes,
below desmoid fibromatosis and solitary fibrous tumour, while PRMT5 alone has the highest class
median. Neither is visible without reading the constituent genes, so a curated group score is treated
here as a summary and not as a unit of evidence.

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
context. The block contains no housekeeping gene and no marker designated as comparator-high. No
directional expectation is recorded anywhere for PRMT5, whose panel membership is as the enzyme MTAP
loss would sensitise.

| control gene | expectation | GPL6244 | GPL3290 |
|---|---|---|---|
| NR4A3 | up in EMC | *t* = +4.66 | no panel contrast: *n* = 9 versus 2, below the three-per-arm floor. The genome-wide path, floor 2, gives +1.70 |
| ENO3 | up in EMC | *t* = +3.61 | *t* = +13.22 |
| MKI67 | approximately flat | *t* = +0.53 | *t* = +2.30, +1.24 SD |

MKI67 is the cellularity control and it moves on one platform. It reads as specified on the
35-tumour array and not on the 16-tumour one, in the same direction and on the same platform as the
twelve-gene proliferation score, so the two agree with each other and both disagree with the
expectation on GPL3290. The GPL3290 reading is carried by the comparator arm rather than by EMC.
Both arms sit below their arrays' means, at mean array percentiles of 15th for EMC and 6th for the
comparators, and the comparator *z* values are −3.88, −3.72, −1.89, −1.62, −1.45 and −0.74, so two
extreme comparator arrays produce the contrast. The confound this control fires on may therefore be
a comparator measurement artefact rather than higher proliferation in EMC.

No proliferation-matched series exists, and the in-silico substitute for one disagrees between
platforms. Main text section 3.6 adjusts PRMT5 for a twelve-gene proliferation score read on all 35
and all 16 samples. It leaves the contrast largely intact on GPL6244 (*t* 6.24 to 5.23, where the
score is flat at *t* = 0.45) and takes most of it on GPL3290 (*t* 6.67 to 2.71, where the score is
itself elevated in EMC at *t* = 3.00 and correlates with PRMT5 at *r* = 0.60). The retained fractions
are 0.84 and 0.41 against the 60% threshold of main text section 2.5. The adjustment measures the
confound without resolving it, and falsifier F7 remains the most likely way the transcript readings
turn out to be artefacts of cellularity or growth fraction.

The PRMT-family control carries one reading the main text draws out. PRMT1 is flat in EMC on both
platforms, at *t* = 0.175 and 1.358, while reference [3]'s premise for its own disease is that PRMT1
and PRMT5 are elevated together and its largest effect is the combination of PRMT1 and PRMT5
inhibition rather than either alone.

### S5a. The reference-channel split on GPL3290

Every value on GPL3290 is a ratio to a reference channel, and the deposit records three references
(S1). Splitting the six-sample comparator arm by reference gives the following, with the pooled
contrast for comparison. Each split arm has three samples, so nothing here is a test.

This split cannot discriminate the confound and is presented as a description. Neither half shares
the EMC arm's `CRH-mRNA` label, so both halves differ from every EMC tumour in the denominator of the
measurement, and agreement between two confounded halves is uninformative about the confound. The
*t* values are retained so a reader can see the movement, not so a reader can test anything.

| gene | vs 3 DFSP (`CRH`) | vs 3 GIST (`UHR`) | pooled, 6 comparators |
|---|---:|---:|---:|
| PRMT5 | +5.97 | +4.32 | +6.67 |
| MAT2A | +2.18 | +4.79 | +4.10 |
| MTAP | −1.59 | −2.60 | −2.27 |
| CDKN2A | +1.11 | +1.10 | +1.33 |
| ENO3 | +13.52 | +9.29 | +13.22 |
| MKI67 | +1.09 | +2.06 | +2.30 |
| CLNS1A | +1.17 | +2.40 | +1.99 |

Two readings move more than the others. MAT2A falls from 4.10 pooled to 2.18 against the
label-matched half. MKI67, the cellularity control, falls from 2.30 to 1.09 against that half, which
is the direction expected if part of the GPL3290 proliferation signal were a reference-pool artefact
rather than a growth-fraction difference.

The one reference-informative contrast this platform admits is comparator against comparator, where
the reference pool differs and the disease class is held within the comparator arm: DFSP against
GIST gives PRMT5 *t* = +0.24. The two comparator reference pools therefore do not move this gene
between the two halves, which is mild reassurance and does not make either half matched to EMC.

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
myxofibrosarcoma +0.83. EMC therefore has the highest class median of the tumour classes on PRMT5
alone and is third of five on the pooled score, and the class that sits second on PRMT5 is the one
that was dropped. The two normal-muscle samples are not a comparator and are drawn as such, but their
position above EMC on PRMT5 is the plainest available statement of what a within-array *z* does and
does not show.

The single-gene comparison is testable and was not previously tested. Exact permutation of the class
means, EMC against each deposited class separately on GPL6244:

| comparison | Δ median | labelings | exact two-sided *p* | Bonferroni × 4 comparator classes |
|---|---:|---:|---:|---:|
| EMC (6) vs low-grade fibromyxoid sarcoma (17) | +0.262 | 100,947 | 0.00004 | 0.0002 |
| EMC (6) vs desmoid fibromatosis (6) | +0.254 | 924 | 0.0065 | 0.026 |
| EMC (6) vs solitary fibrous tumour (5) | +0.252 | 462 | 0.0087 | 0.035 |
| EMC (6) vs myxofibrosarcoma (6) | +0.368 | 924 | 0.0152 | 0.061 |
| EMC (6) vs pooled skeletal muscle (2) | −0.039 | 28 | 0.54 | not a comparator |

Three of the four comparator classes clear a within-figure Bonferroni and the fourth does not. None
of these values carries any correction for the number of genes on the array, so none of them bears
on S5c. At sample level the picture is weaker than separation: 9 of the 34 comparator tumour samples
read at or above the lowest EMC tumour, and one of the two pooled normal-muscle arrays reads above
the EMC median.

### S5c. The multiplicity correction

The procedure is described in main text section 2.4. On GPL3290 all 8,008 labellings are enumerated,
so that column is exact with respect to the labellings; on GPL6244 20,000 labellings were drawn under
a fixed seed and the Monte-Carlo standard error on an adjusted *p* near 0.2 is about 0.003. Under a
labelling that leaves either arm below the panel's three-value floor a gene contributes |*t*| = 0
rather than leaving the family, which deflates the maximum for genes with missing values and biases
the adjusted *p* downward.

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

The family is a choice and it determines the value. Recomputed on the same labellings and the same
reduction, with the owning module's own arm floor and maximum kernel, varying only which symbols are
in the family:

| family | genes, GPL6244 / GPL3290 | GPL6244 | GPL3290 |
|---|---|---:|---:|
| the genes the main text reports | 9 / 6 | 0.00015 | 0.000125 |
| the curated panel cache | 1,857 / 1,611 | 0.097 | 0.064 |
| the merged array-wide family, as used above | 5,449 / 4,848 | 0.208 | 0.238 |
| the same family restricted to genes measured in every sample | 5,449 / 3,126 | 0.208 | 0.031 |

The array-wide family is the one whose value the main text quotes, and main text section 2.7 gives
the reason: *PRMT5* was not the pre-specified endpoint, no direction was recorded for it, the
statistic was moved from the group to the gene after the figures were seen, and this read is one of
eighteen on the same tumours. The fourth row is the largest single sensitivity and runs the other
way, because excluding genes with missing values removes the genes that most often attain the
permuted maximum on GPL3290. On GPL6244 the third and fourth rows coincide, since every cached gene
there has a value in every sample.

The families of 5,449 and 4,848 sit against mapped-symbol universes of 18,724 and 14,932, so each
value is also a lower bound with respect to family size. How fast that bound rises with the number of
symbols scanned is measured on the random symbols alone, which are a uniform sample of the array:
PRMT5's adjusted *p* on GPL6244 is 0.016 over 250 random symbols, 0.055 over 1,000 and 0.168 over
3,973; on GPL3290 it is 0.037, 0.062 and 0.208 over 250, 1,000 and 3,640, the third of which is a
different family size from GPL6244's. The curve is still rising at the largest family the committed
data supports, which is roughly a quarter of each array. Reaching the whole array would need the full
probe matrix, which exists only inside the fetch step and is not carried by any committed file.

An adjusted *p* is a statement about how often a labelling of these samples produces a statistic this
large somewhere in the family. It is not a statement that a reading is absent, which matters most for
the two controls that read as expected and still do not clear a threshold, and which is why the main
text argues the *MTAP* result from the per-sample conjunction of S3a rather than from an adjusted
*p* of 1.00.

Two further conditions attach to the word exact. Both permutation procedures are exact under the
null of exchangeability rather than under a null of equal means, and the arms are not homoscedastic:
the ratio of within-arm variances falls outside 0.5 to 2 for 49.5% of genes scored on GPL6244 and
59.1% on GPL3290, with medians of 0.90 and 0.77 and 90th percentiles of 3.22 and 3.67. And on
GPL3290 the exchangeability the permutation assumes is defeated by the four collinear strata of S1
before any variance question arises.

## S6. Figures and their sources

| figure | drawn from | reading |
|---|---|---|
| 1, readings per tumour | `emc-expression-panels.json`, `gene_reads[*].per_sample` | every tumour in the analysed arms is visible; medians are bars |
| 2, the locus per tumour | same, plus `emc-mtap-locus-persample.json` | no tumour carries the joint MTAP-low and CDKN2A-low pattern that 9p21 co-deletion produces |
| 3, dependency prior | `depmap-sarcoma-dependency.json` | argues against the proliferation reading, inside and outside sarcoma, with Wilson intervals |
| 4, pooled against single gene, per class | `emc-expression-panels.json`, plus `emc-prmt5-multiplicity.json` for the classes the panel's arms exclude | pooled, EMC is third of five tumour classes; on PRMT5 alone EMC has the highest class median, and two pooled normal-muscle samples read above it |
| 5, the motif map | `emc-prmt5-substrate-motif-map.json` | the segment every EWSR1 fusion retains carries no site, and any breakpoint across a 142-residue window retains exactly four |

Provenance hashes for the five source artifacts and for every rendered PNG are stamped in
`research/manuscripts/figures/mtap-prmt5-figure-provenance.json`, and `--check` compares both sides,
so a stale figure and a hand-edited figure are both detectable. PDFs are listed and not hashed,
because Matplotlib writes a creation timestamp into each one and two runs of the same code produce
different bytes.

## S7. Failure modes

1. The contrasts are cellularity or proliferation artefacts. Both readings would then be real
   measurements of the wrong thing, and nothing here excludes it.
2. This failure mode has already occurred, for the locus. The low group score is not a reading of
   MTAP: MTAP is flat where the read is powered, and what signal the score has is carried by CDKN2A,
   which reverses between platforms and does not survive correction either. No evidence of a CDKN2A
   genetic event is presented anywhere; the reading is a transcript difference with no sample at
   floor. The entry is retained rather than deleted because it records a failure mode that fired.
3. The clear cell sarcoma transfer does not hold. EWSR1-ATF1 and EWSR1::NR4A3 share a 5′ partner and
   an architecture, not a DNA-binding domain or a target repertoire. Neither of the two supports
   that were offered for it survives inspection: the motif match of S9 is what the cluster structure
   returns for almost any mid-protein breakpoint, and the fusion-dependent PRMT5 requirement in
   Ewing sarcoma comes with a mechanism its authors attribute to that disease. This entry stays open.
4. The methylosome elevation is generic. PRMT5, PRMT1 and MEP50 read higher across multiple sarcoma
   types than in breast and lung cancer, and abundance is not dependency.
5. Every reading above is at transcript level. No claim in the manuscript has been tested in a cell
   carrying this fusion, because no such cell is available to this work.
6. The GPL3290 readings are batch. Disease class on that platform is collinear with submission
   block, reference pool and within-study platform assignment, and no re-analysis separates them.

## S8. Artifacts

Every number in the main text and in this supplement resolves to one of:

- `research/modalities/emc-expression-panels.json`, the readings, and the one home of every *z*,
  percentile and group score
- `research/modalities/emc-expression-panels-inputs.json`, the per-sample values as fetched
- `research/modalities/emc-prmt5-multiplicity.json`, the multiplicity correction and its three
  disclosure analyses
- `research/modalities/emc-mtap-locus-persample.json`, the per-tumour 9p21 reading of S3a, its
  controls and its binomial bounds
- `research/modalities/emc-prmt5-effect-sizes.json`, the effect sizes and intervals of S3, the
  minimum detectable effects, the family-composition sensitivity of S5c, the per-class tests of S5b
  and the variance-ratio distribution
- `research/modalities/census-route-expression-grading.json`, the grading of this route against its
  own selection criterion
- `research/modalities/depmap-sarcoma-dependency.json`, the sarcoma-line dependency prior
- `research/modalities/emc-prmt5-route-controls.json`, the control calculations of main text
  section 3.6
- `research/modalities/emc-cohort-search-inputs.json`, the GEO cohort search behind S1
- `research/modalities/emc-prmt5-substrate-motif-map.json`, the motif counts of S9 and the two
  double-entry checks against the artifacts that already held the RG numbers
- `research/modalities/emc-fet-construct-designs.json` and
  `research/modalities/emc-fet-idr-census.json`, the committed protein sequences and sourced
  breakpoints the motif map reads; neither was produced for this manuscript, which is why they can
  check it
- `research/literature/mtap-prmt5-emc-citations.json` and
  `research/literature/mtap-prmt5-discovery-and-chronos-2026-08-10.json`, the citation anchors, in
  which every identifier used in the main text appears, read from a retrieval rather than recalled
- `research/literature/emc-prior-art-2026-08-09.json`, the Europe PMC prior-art screen of main text
  section 1.3, with its retrieval record and its own statement of what a title-and-abstract screen
  can and cannot show
- `research/literature/prmt5-ewing-expression-panel-composition-2026-08-10.json`, the reconciliation
  of the pan-sarcoma panel composition behind reference [3]

## S9. The substrate-motif map

The motif is GRG, taken from a retrieval rather than from recollection: PRMT5's preference for
arginine flanked by glycines is reported from genome-wide methylation profiling after selective PRMT5
inhibition, with in vitro methylation used to validate the hits (main text reference 13). That
reference was verified at metadata and abstract level from the retrieved Europe PMC record; its full
text is not open access and was not read, which is stated because the motif definition is the
foundation of this whole section. A mapping experiment in a different substrate agrees, since only
the DDX5 fragment carrying the C-terminal RGG/RG motif was methylated by PRMT5 (main text
reference 19), and that one was read in full. Main text reference 20, cited for EWSR1 being
extensively arginine-methylated, was verified at title level only.

Occurrences are counted by exact string scan on the committed protein sequences, with overlaps
included, because GRGRG is two sites and two methylatable arginines and a non-overlapping scan would
report one and silently halve a poly-RG tract. A fusion's retained 5′ sites are those at or before
`five_prime_residues_fully_encoded`, excluding the seam residue, because every one of these junctions
splits a codon and the seam residue is encoded by both partners.

EWSR1's eleven GRG sites lie at residues 301, 303, 316, 320, 463, 489, 564, 574, 591, 602 and 635.
Four of them fall inside twenty residues and the fifth is 143 residues later, so the retained-site
count is a step function with one plateau: every breakpoint between residues 321 and 462 retains
exactly four sites, across 142 residues or 21.6% of the protein. EWSR1::NR4A3 type 1 cuts at 431,
EWSR1::ATF1 exon 8 at 324 and EWSR1::ATF1 exon 10 at 348, all inside that window. An earlier version
of this analysis presented the shared count of four between the commonest EMC and clear cell
junctions as quantitative content supporting the transfer between the two diseases; it is not, and
the plateau is why. The agreement is also metric-dependent: on the RG axis the same two junctions
retain 8 and 7 dipeptides.

The junctions tabulated are those recorded in the source artifact rather than the reported sets. On
the clear cell side, main text reference 2 records that besides type 1 "6 other types of EWSR1-ATF1
fusion and EWSR1-CREB1 have also been reported" and three are held here. On the EMC side, FUS::NR4A3
and TCF12::NR4A3 are reported fusions of this disease and are not tabulated; FUS is a FET protein
with its own RGG content and is the most informative missing row.

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
test, and it is why the table cannot be read as a response predictor. Main text reference 2, the
source of the clear cell transfer, proposes PRMT5 as a binding co-activator of EWSR1-ATF1 and does
not show the fusion to be a substrate at all.

## S10. The control calculations

Exact permutation. Every assignment of the observed *z* values to arms of the observed sizes is
enumerated and Welch's *t* recomputed; the two-sided *p* is the fraction with |*t*| at least the
observed. No random sampling is used anywhere in this implementation of the test, so the value is
exactly reproducible. On GPL3290 the smallest attainable *p* is 1/8,008, so the test's resolution is
the sample size. Exactness is with respect to the labellings and to the null of exchangeability, and
S5c states both conditions.

Confound adjustment. A per-sample score is the mean *z* of the readable members of the named set;
PRMT5 is regressed on it by ordinary least squares with one covariate and an intercept, and the
EMC-versus-comparator contrast recomputed on the residuals. A contrast is called surviving if it
keeps its sign and at least 60% of its magnitude, a threshold chosen for this work rather than taken
from an established convention; the raw and adjusted values are both reported.

Coverage. The proliferation score uses twelve genes and scores all 35 and all 16 samples; the
chondroid-marker score uses eight and scores 35 and 14. A proxy still makes a null weak evidence,
since a confound the proxy measures badly passes through the adjustment untouched, so a surviving
result is a much weaker statement than a failing one; the failure on GPL3290 is the stronger
direction of the same instrument.

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

The two platform-table resolutions. The 18,688 above and the 18,724 in S5c are two resolutions of the
same GPL6244 platform table, taken on 2026-08-09 and 2026-08-07; the same pair of caches also
disagrees on the probe count mapping to a symbol, 20,235 against 20,221. The random half of the
correction's family was drawn from the older and 36-symbol-wider resolution. Reconciling the two
needs the platform table re-fetched, which is a network read this environment could not make. The
merge is refused unless the two caches agree on every shared symbol, and they do.

Missing values. A sample with no value for a gene is dropped from that gene's contrast and never
imputed. On GPL6244 every cached gene has a value in every sample. On GPL3290 578 of 1,662 cached
genes (34.8%) have at least one missing value and 51 (3.1%) have an arm below three, which is why one
instrument control carries a genome-wide rank and no panel contrast.

The multiplicity correction. Its method is in main text section 2.4 and its results in S5c. It
re-derives every observed *t* from the input cache and refuses to run if any disagrees with the
committed panel value, so the correction cannot be computed on a statistic that is not the published
one. The family-composition sensitivity of S5c is computed by a second module that imports that one
and varies the family alone, so the two cannot drift apart.

Status. The PRMT family, the fuller proliferation set, the Sm substrates, the additional chondroid
markers and the genome-wide null were added to the panel definition on 2026-08-09 and fetched the
same day; every figure in main text sections 3.5 and 3.6 is read from that fetch.

---

## Appendix S1. Superseded numbers and retracted claims

Superseded numbers are recorded rather than silently dropped. A retracted value stays quotable
unless the record says it was retracted, and a live text carrying a "was X, now Y" narrative leaves
both in circulation. So the live text carries only the current figure and this appendix carries the
rest. It is the full register; the main text's Appendix A carries the subset that lived in the main
text. This appendix and the YAML frontmatter are repository record and are removed at submission.

| where | was | is | why it moved |
|---|---|---|---|
| §S4 running text, and the pre-posting checklist | *"pooled across four genes EMC ranks second of four comparator classes"* | third of the five tumour classes, below desmoid fibromatosis and solitary fibrous tumour | ⛔ **THE PREVIOUS REVISION CORRECTED THIS IN THE MAIN TEXT, IN FIGURE 4 AND IN §S6, AND LEFT IT LIVE HERE**, so the two submitted files contradicted each other and this file contradicted itself two sections apart. The artifact is unambiguous: `per_class_medians_methylosome_pooled` gives desmoid fibromatosis 0.9496, solitary fibrous tumour 0.9354, EMC 0.9283. It survived because rule 1.3's registry held no entry for this manuscript and this file was not a `lint_consistency` target, so the gate built to catch exactly this was given nothing to catch it with. Both are fixed in the same commit as this row |
| §S1, the DepMap identity note | *"and it carries no CRISPR data"*, of the disputed EMC-labelled line | clause deleted | The first half of that sentence is verbatim from a committed `_identity_correction`. The second could not be traced to any artifact: no tracked file records that line's CRISPR status. It was not load-bearing, since the paragraph's conclusion rests on the fusion caution alone, and a factual assertion about a public dataset with nothing behind it does not belong in a supplement whose §S8 opens by claiming every number resolves to an artifact |
| §S5c, the family-size curve | *"0.037, 0.062 and 0.208 over the same three family sizes"* | 250, 1,000 and 3,640 on GPL3290, against 250, 1,000 and 3,973 on GPL6244 | The three *p* values were right and the description of them was not: the third family size differs between platforms |
| Appendix S1, a cross-reference | *"§S11 status line"* | §S10, closing status paragraph | §S11 does not exist. The file runs §S1 to §S10 and then this appendix |
| §S6, on the provenance stamp | *"`--check` compares them against the artifacts, so a stale figure is detectable"* | both the artifacts and every rendered PNG are hashed and compared | The claim overstated its instrument. `check()` hashed five input artifacts and no image, while the tool printed "10 files match", which reads as a statement about the ten files. A figure edited by hand, or left from an earlier run against the same artifact, passed. Image hashing was added rather than the sentence weakened |
| §S10 and main text §2.4, the genome-wide null's symbol counts | 18,474 and 14,402 | **18,688 on GPL6244; 14,404 of 14,932 with a probe on GPL3290** | ⛔ **THE SUPERSEDED PAIR IS IN NO COMMITTED ARTIFACT AT ANY POINT IN THIS REPOSITORY'S HISTORY**, which is the same failure class as the *MTAP* −0.023 row below and was found the same way — by reading the artifact instead of the prose. Both correct values are carried independently by `emc-prmt5-route-controls.json` (`per_platform.*.genome_wide_placement.n_symbols_scored`) and `emc-expression-panels.json` (`platforms.*.genome_wide_null`) |
| §S2, on multiplicity | *Superseded, retained: "No multiplicity correction is applied anywhere, and every reported t must be read with that in mind."* | a max-statistic permutation correction is run and reported (§S5c) | it was true when written and is no longer. The uncorrected values are not withdrawn — they answer a different question and are reported beside the adjusted ones |
| §S5, the instrument-control paragraph | *Superseded, retained: "The instrument-control read, covering housekeeping recovery and a marker expected high in the comparator arm rather than in EMC, is carried in the source artifact's control block and is not restated here."* | the six genes actually in the block, with their pre-specified expectations and both platforms' values | ⛔ **THE SENTENCE DESCRIBED A CONTROL THAT WAS NEVER RUN.** The block contains NR4A3, ENO3, MKI67, EWSR1, TAF15 and FUS: no housekeeping gene, and no marker designated comparator-high. A reader was told a control existed that did not, and one that DID exist — the pre-specified MKI67 cellularity reference, which moves on GPL3290 — was not reported anywhere. Suppressing a pre-specified control that fires is the one thing a paper of this kind cannot do, and this was inadvertent rather than deliberate, which is exactly why the register records it |
| §S6, figure 4's reading | "pooled, EMC ranks second below desmoid; PRMT5 alone separates" | EMC is third of five tumour classes pooled; on PRMT5 alone EMC has the highest class median | the figure drew only the samples inside the panel's arms, so five solitary fibrous tumours and two pooled skeletal-muscle references were absent from a figure whose subject is the comparison between classes (§S5b). "Separates" was also true of class medians and false of samples, and §S5b now reports the overlap |
| §S9, the motif comparison | one EWSR1::ATF1 junction shown, retaining four sites; then all three, with the shared count of four presented as quantitative content | all three junctions, with the plateau disclosed and the inference withdrawn | three are recorded in the source artifact and the cleanest was the one shown. The wider correction is that a shared count of four is what the cluster structure returns for any breakpoint across 142 residues, so the agreement was never informative |
| §S3, *PRMT5* EMC-minus-comparator | +0.266 and +0.744 SD | **+0.263 and +0.816 SD** | the values had drifted from `emc-expression-panels.json`, which is their one home. Checked 2026-08-09 against the committed artifact; the second differs by 0.07 SD and the reading is unchanged in direction or size class |
| §S3, the statistic quoted for route 1 | the methylosome **group** *t* (3.11, 3.89) | additionally the **gene's own** *t* (6.24, 6.67) | the group score is not the unit route 1 depends on — the same error §S4 records in the other direction for the locus. The group figures are not withdrawn; they were simply the wrong ones to lead with. ⚠ Main text §2.7 now records that this change was made after the figures were seen, which is what decides the family in §S5c |
| §S3, the locus genes | *MTAP* −0.023 / −0.389; *CDKN2A* −0.399 / +0.173; *CDKN2B* −0.096 | **+0.053 / −0.607; −0.481 / +0.175; −0.136** | ⛔ **CAUSE NOT ESTABLISHED, AND AN EARLIER EXPLANATION HERE WAS WRONG.** *Superseded, retained: "a re-fetch ran on a NARROWER probe→symbol bridge (0.931 against 0.984), and a narrower bridge changes which probes map."* That was a story built on a coincidence. Checked against every committed version of the artifact: ***MTAP* reads +0.053 in all of them — at bridge rates 0.984, 0.931 AND 0.981**, and always on one mapped probe. Bridge width does not move this gene. The −0.023 appears in **no committed artifact at all**, so it entered the prose from a source this repository cannot show |
| §S4, the dependency denominator | "across 176 sarcoma cell lines" | **"across the 91 screened sarcoma cell lines"** | ⛔ a real error, in the direction that overstated the evidence base, and it was in four places including the abstract. The release lists 176 sarcoma MODELS; only **91** carry CRISPR gene-effect data, and every per-gene record in the artifact says `n_sarcoma: 91`. The percentages themselves are unchanged — they were always computed on the screened subset — but they were being attributed to a denominator almost twice its true size |
| §S7, the fusion-class transfer | "an assumption", then "argued rather than assumed" | argued, and the argument's two legs restated at the strength their sources support | a peer-reviewed fusion-dependent PRMT5 result in a second EWSR1-fusion sarcoma, and the motif match of §S9. ⚠ Both have since been narrowed: the motif match carries no information, and the Ewing result's authors attribute the dependence to a mechanism specific to that disease |
| §S7, item 2 | *Superseded, retained: "The locus reading is a CDKN2A shadow."* | a transcript difference carried by CDKN2A, with no evidence of a CDKN2A genetic event | "shadow" implies an event casting it, and none is presented: no sample is at floor for CDKN2A on either platform |
| §S5, the proliferation control | *Superseded, retained: "No proliferation-matched control exists."* | one is now run, and it disagrees between platforms | the in-silico substitute is reported in §S5 and in main text §3.6. It is a measurement, not a resolution |
| §S5a, the reference-channel split | *Superseded, retained: "The primary contrast keeps its direction and most of its size against either half, so the reference-pool difference does not manufacture it."* | the split is a description and cannot discriminate the confound | neither half shares the EMC arm's reference label, so agreement between two confounded halves is uninformative about the confound. Main text §3.6 no longer calls it discriminating, and the one reference-informative contrast the platform admits is now reported instead |
| this file's own register | §S10, numbered in sequence with the method sections | Appendix S1 | `lint_style.py` exempts sections under an `Appendix` heading, because superseded-value bookkeeping is required and belongs in an appendix rather than in running text. The content is unchanged |
| both files' register | repository house style throughout: glyph warnings, bold on the load-bearing clause, sentence-shaped headings, running commentary on the paper's own honesty | journal register in the running text, with the house-style rows preserved verbatim inside this appendix | the register was correct for a maintainer and wrong for a journal reader. No measured statement was removed. The rows above are left in their original wording rather than rewritten, because a corrections register that is itself edited is no longer a record |

⭐ **AND ONE ROW IS A LESSON ABOUT THIS WORK'S OWN METHOD, WHICH IS WHY IT IS NOT JUST
BOOKKEEPING.** For the locus values a plausible mechanism was available — the annotation bridge
narrowed on the same day the numbers were noticed to differ — and it was written down as the cause
without the one check that could separate it from coincidence. The check was a `git log` over the
artifact, it was free, and it refutes the explanation: **four committed versions, three different
bridge rates (0.984, 0.931, 0.981), and *MTAP* reads +0.053 in every one of them.** ⛔ **The −0.023
is in no committed artifact**, so what was corrected was a stale figure in the prose rather than a
value that moved.
⭐ **What survives, and is now measured rather than asserted: every figure this manuscript quotes is
stable across three independent annotation bridges** — *PRMT5* +0.2632 and *MTAP* +0.053 at all
three — which is a stronger statement about reproducibility than the one it replaces.

⚠ **The bridge itself is volatile and the values are not, which is the useful pair.** The
accession→symbol step was re-run four times on 2026-08-09 and resolved 0.984, 0.931, 0.931 and 0.981
of GPL6244's accessions — the middle two returning **zero** gene links from NCBI in ~15 minutes each,
the endpoint having briefly stopped answering and then recovered. **None of that moved a number this
manuscript quotes.** The bridge now has a committed home so a future outage cannot narrow it at all.
