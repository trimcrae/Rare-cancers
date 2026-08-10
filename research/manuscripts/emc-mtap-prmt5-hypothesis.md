---
id: DOC-EMC-MTAP-PRMT5
title: "PRMT5 and the MTAP locus in extraskeletal myxoid chondrosarcoma: two rationales tested against the available public data, neither supported"
level: L3
kind: manuscript
status: live
canonical_for: ["the 2026-08-09 EMC PRMT5/MTAP reading and its hypothesis"]
purpose: >
  Test the two rationales that would place the PRMT5 methylosome in front of this disease against
  the only public data able to address them; report that neither is supported, with the bound on
  each; record an original sequence observation about where PRMT5's substrate motif falls in the
  fusion protein; and specify the inexpensive experiments that would settle each rationale.
scope: >
  L3. Two public archival expression series, 16 EMC tumours, transcript level only; a public sarcoma
  CRISPR dependency panel containing no EMC line; a sequence analysis of where PRMT5's reported
  substrate motif falls in the fusion protein; and published preclinical results in two other
  EWSR1-fusion sarcomas. It reports no experiment in EMC cells, no drug exposure and no patient.
  The YAML frontmatter and the appendix are repository record and are removed at submission.
audience: [maintainers, external reviewers, autonomous research agents, collaborators]
date: 2026-08-10
last_verified: 2026-08-10
related: [DOC-MODALITY-CENSUS, DOC-EMC-UNEXPLORED-LANES]
---

# PRMT5 and the MTAP locus in extraskeletal myxoid chondrosarcoma: two rationales tested against the available public data, neither supported

**Tristan D. McRae**

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com

Running title: PRMT5 and MTAP in extraskeletal myxoid chondrosarcoma

*Keywords:* extraskeletal myxoid chondrosarcoma; EWSR1::NR4A3; PRMT5; MTAP; arginine methylation; fusion-driven transcription; rare sarcoma

*A re-analysis of public data. No experiment in an EMC cell, no drug exposure and no patient are
reported. Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness for any
agent in any disease. Analyses, figures and drafting were carried out with AI assistance, disclosed
in section 2.7.*

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare sarcoma driven by an *NR4A3* fusion,
usually EWSR1::NR4A3, and no clinically validated agent directly targets NR4A3. Two rationales would
place the PRMT5 methylosome in front of it: transfer from other EWSR1-fusion sarcomas, and selection
on *MTAP* loss. We tested both against the only publicly deposited data able to address them: two
archival expression series holding 16 EMC tumours, a public sarcoma CRISPR dependency panel, and
PRMT5's reported substrate motif in the fusion protein. Neither is supported. A group-mean test is
mis-specified for *MTAP*, since 9p21 deletion is a subset event, so every tumour was read
individually. Five of ten EMC tumours on one platform sit below every comparator for *MTAP*, and
none carries the low *CDKN2A* that 9p21 co-deletion requires: all five sit at or above their own
array's median, and two further 9p21 genes agree. No tumour of sixteen is deletion-consistent,
bounding the frequency at 17%. For the fusion rationale, *PRMT5* reads higher in EMC on both
platforms (*t* = 6.24 and 6.67) at a family-wise adjusted *p* of 0.21 and 0.24 over the array-wide
family; that value ranges from 0.0001 to 0.24 across defensible families, one platform confounds
class with submission block and reference pool, and no EMC cell line exists in any dependency
dataset. In EWSR1, four of eleven Gly-Arg-Gly sites lie at residues 301 to 320 and the next at 463,
so any breakpoint across a 142-residue window retains exactly four. Two inexpensive experiments
would settle each.

---

## 1. Introduction

### 1.1 The disease and its treatment options

Extraskeletal myxoid chondrosarcoma is an ultra-rare translocation sarcoma defined by an *NR4A3*
gene fusion, most often EWSR1::NR4A3. Despite its name it does not show true cartilaginous
differentiation and is classified as a mesenchymal tumour of uncertain differentiation [1], which
bears on every comparator arm used below, none of which is cartilage-lineage either. The most recent
comprehensive review of the disease states that no clinically validated agent directly targets
NR4A3, and reports pazopanib with an objective response rate of 18% and a median progression-free
survival of 19 months (NCT02066285) [1]. A modality census carried out for this work, and deposited
with it as an unpublished supporting analysis, counts eight classes in clinical use of which two are
local therapies; only the antiangiogenic class has a meaningful systemic response record.
Mitotic activity in this tumour is usually low [1], which is the pre-specified basis of the
cellularity control of section 3.6.

### 1.2 Two rationales for the PRMT5 methylosome

The first rationale runs through the fusion, and what each of the two reports it transfers from
shows is narrower than the transfer needs; Supplementary S11 gives both designs, both proposed
mechanisms and the inhibitor results in full.

A study of clear cell sarcoma identifies PRMT5 as "a new EWSR1-ATF1 binding co-activator to
stimulate its transcription activity" [2], on co-immunoprecipitation, promoter occupancy and shPRMT5
experiments. It does not show that the fusion protein is methylated, contains no domain mapping
localising the interaction to the EWSR1 portion, and detects CREB1 in the same immunoprecipitate, so
an equally documented route into the complex runs through the half EWSR1::NR4A3 does not share. Its
statements were read from a preprint full text (section 4.4).

In Ewing sarcoma the effect of single-agent GSK591 was "largely supressed [sic] by partial depletion
of EWSR1::FLI1" [3], on one engineered line with a partial depletion and viable cell number at four
days, so the readout falls with the growth rate the depletion itself lowers. That report attributes
PRMT5 dependence to replication-stress buffering and to BRCA1 sequestration by the fusion, with
olaparib alone fusion-dependent in the same figure: both are properties of the ETS half rather than
of the EWSR1 N-terminus the two diseases share.

The second rationale runs through a genetic selection window rather than through the fusion. Two
2016 reports established it independently: MTAP loss "confers a selective dependence on protein
arginine methyltransferase 5 (PRMT5) and its binding partner WDR77" [4], and a short-hairpin screen
identified MAT2A and PRMT5 "as vulnerable enzymes in cells with MTAP deletion" [5]. The mechanism
both describe is metabolic rather than genetic, the MTAP substrate methylthioadenosine accumulating
when the enzyme is lost and inhibiting PRMT5 directly, which is why the class the rationale calls
for is an MTA-cooperative one; that axis has reached patients with an MTA-cooperative PRMT5
inhibitor selected on *MTAP* deletion [6]. The sensitivity is comparative, and a differential
established in engineered and pan-cancer settings is not a therapeutic window in a patient. The
window also has a known asymmetry that this work uses as its test, since *MTAP* is lost through its
proximity to *CDKN2A* [4,5]: *MTAP* loss implies *CDKN2A* loss while *CDKN2A* loss does not imply
*MTAP* loss [7], so a three-gene locus score can fall on a *CDKN2A* event alone. The two rationales
therefore call for different agent classes, which is not always stated: an MTA-cooperative inhibitor
is the wrong tool in an *MTAP*-intact model, while the fusion rationale needs a first-generation
compound, and [2] found that the choice within that generation changed the answer. Reference [3]
raises both rationales for its own disease, so this work is a transposition of that discussion; the
methylosome is read as a unit rather than as PRMT5 alone because MEP50 (WDR77) is required for
PRMT5-catalysed activity and binds substrate independently [8].

### 1.3 Absence of the question from the published record

A modality census of this disease enumerated 217 categories of cancer treatment and found that
classes selected by a molecular state had been dismissed as a group, largely because the biomarker
was never read. A corpus of 591 open-access full texts retrieved for this work contains no *MTAP*,
*PRMT5* or *MAT2A* datum for this histology, and a Europe PMC screen of 322 records returned one hit
on the pairing: a 2007 review of chondrosarcomas that names methylthioadenosine phosphorylase among
therapeutic targets "validated by translational research", while treating EMC as a distinct
fusion-defined entity [9].

Neither screen is a full-text search from the disease side to the target side, so the claim made
here is narrow: nothing indexed pairs the PRMT5 methylosome with extraskeletal myxoid
chondrosarcoma, which is a statement about what is indexed rather than about what has been done. The
census and the two screens are the author's own unpublished analyses, deposited with the manuscript
rather than cited as literature; Supplementary S12 states each one's reach and resolves the one
candidate counterexample, inside [3], whose 137-sample pan-sarcoma panel excludes [10]'s three EMC
tumours.

---

## 2. Materials and methods

### 2.1 Expression series, sample classification and per-gene scoring

Two public archival series contain this histology and are the only publicly deposited EMC expression
data a GEO search of six committed queries returned, which returned no deposit for the three further
EMC tumours [10] profiled; neither analysed series links a publication in GEO.

**Table 1.** The two series.

| series | deposited title | platform | measurement | EMC | comparator arm | reference channel |
|---|---|---|---|---:|---|---|
| GSE24369 | Gene expression profiling of low-grade fibromyxoid sarcoma (LGFMS) | GPL6244 | single-channel log2 intensity | 6 | 17 low-grade fibromyxoid sarcoma, 6 desmoid fibromatosis, 6 myxofibrosarcoma | not applicable |
| GSE4303 | Gene expression profile of extraskeletal myxoid chondrosarcoma | GPL3290 | two-colour log2 ratio | 10 | 3 dermatofibrosarcoma protuberans, 3 gastrointestinal stromal tumour | EMC against `CRH-mRNA`, DFSP against `CRH`, GIST against `UHR` |

The first is not an EMC study: GSE24369 is deposited as a study of low-grade fibromyxoid sarcoma, so
its six EMC cases were assembled as morphological mimics of another entity and the 17-sample
FET-fusion control used here is that study's index arm. Neither deposit records whether *NR4A3*
rearrangement was confirmed, so the *NR4A3* instrument control of section 3.5 is the only evidence
here bearing on the diagnoses, and nothing establishes that the sixteen tumours are sixteen
patients. Samples were assigned by pattern-matching the verbatim GEO annotation, in a step separate
from the data fetch so that every assignment is auditable: of GSE24369's 42 deposited samples 35
were analysed, two pooled skeletal-muscle RNA samples being excluded by design and five solitary
fibrous tumours by a classifier that carried no pattern for that histology, which was accidental and
is reported here for that reason (section 4.4, Supplementary S5b). GSE4303, whose deposit
corresponds to the published study of that series [11], carries 36 samples across two platforms, of
which the 16 on GPL3290 are used here. Supplementary S1 gives both deposits verbatim, with what else
the record leaves unresolved.

GPL3290 carries a confound that no analysis removes, and section 3.6 and section 4.4 report what
follows from it. On that platform disease class coincides with three other strata at once: the three
histologies occupy three disjoint GEO accession blocks; each class carries its own two-colour
reference pool, so class is collinear with the denominator of every value; and all ten EMC tumours
but only 6 of that deposit's 26 comparator sarcomas were assigned to this array, so class is
collinear with platform assignment inside the source study. Array-level covariates track the arms in
consequence (Supplementary S1), and a permutation that relabels these sixteen samples is therefore
not exchangeable with respect to any of the four strata.

Each gene's value is a *z*-score against its own array's probe distribution, so it is a position
within one array rather than a quantity comparable across arrays; a group score is the mean of its
members' *z*, contrasted by Welch's *t*; a gene with no probe mapping is unreadable rather than
unexpressed, which matters below because one locus gene has no probe on GPL3290; and every contrast
also carries a difference on the array's own log2 scale with a 95% Welch interval, a fold difference
on GPL6244 only. Supplementary S2 gives the rest: multi-probe collapse, the probe-to-symbol bridge
and its resolution rates, the coverage floors, both minimum arm sizes, the realised missingness and
the absence of variance moderation.

### 2.2 Per-sample reading of the 9p21 locus

Homozygous 9p21 deletion is present in some tumours and absent in others, so a difference of group
means is mis-specified for it and a family-wise adjusted *p* still more so. Every tumour was
therefore read individually: an EMC tumour is an *MTAP*-low candidate when its *MTAP* reading sits
below every comparator on the same platform, on both the within-array *z* and the array percentile,
and because *MTAP* loss implies *CDKN2A* loss [7] a tumour is deletion-consistent only if its
*CDKN2A* also sits below the 25th percentile of its own array. That cut is stated in advance, and
the count is also reported at the 5th, 10th and 50th percentiles. Two controls have to fail for a
candidate to mean anything, array dimness and the reference label of every sample in the arm, and
frequencies consistent with an observed count of zero are given as one-sided 95% binomial upper
bounds. Supplementary S3a carries all of that in full.

### 2.3 Dependency panel

Gene-effect scores come from the DepMap public 24Q4 release, distributed as figshare article
27993248, restricted to sarcoma models on the Chronos scale [12]. The release lists 176 sarcoma
models, of which 91 carry CRISPR gene-effect data and every figure here is computed on those 91. A
gene is a dependency in a line at a gene effect below −0.5, and selectivity is the difference
between the mean gene effect outside sarcoma and inside it.

### 2.4 Exact permutation, genome-wide placement and multiplicity correction

Both designs are small enough to enumerate completely, so no normal approximation and no random
sampling are used: every assignment of the observed *z* values to arms of the observed sizes was
evaluated and Welch's *t* recomputed, giving C(35,6) = 1,623,160 labelings on GPL6244 and
C(16,10) = 8,008 on GPL3290, and the two-sided *p* is the fraction with |*t*| at least the observed
value. That *p* is exact with respect to the labellings and under the null of exchangeability rather
than of equal means, and the arms are not homoscedastic.

Because it says nothing about how many genes were examined, the same statistic was computed for
every symbol the platform's probes map to and each gene of interest placed in that distribution:
18,688 symbols on GPL6244, and 14,404 of the 14,932 carrying a probe on GPL3290. That placement is
not a correction either, so a max-statistic permutation correction was run over an array-wide family
of 5,449 symbols on GPL6244 and 4,848 on GPL3290, against mapped-symbol universes of 18,724 and
14,932: a gene's family-wise adjusted *p* is the fraction of labellings whose family-wide maximum
|*t*| reaches its observed value, enumerated exactly on GPL3290 and drawn at 20,000 seeded
labellings on the other.

An adjusted *p* is a property of a family, and the family is a choice. Each family is a subset of
its array and adding symbols can only raise the permuted maximum, so every value reported is a lower
bound; three other defensible families span three orders of magnitude, and section 3.5 reports all
four with the reason for choosing the array-wide one. Supplementary S5c gives each family's
construction, the variance-ratio distribution behind the exchangeability qualification and the
arm-floor convention that biases an adjusted *p* downward; S10 gives the genome-wide path's double
entry against the panel and the two irreconcilable resolutions of the GPL6244 platform table, whose
0.2% difference moves no adjusted *p*.

### 2.5 Confound adjustment

A per-sample confound score is the mean *z* of the readable members of a named gene set. *PRMT5* is
regressed on that score by ordinary least squares with one covariate and an intercept, and the
EMC-versus-comparator contrast recomputed on the residuals; a contrast survives if it keeps its sign
and at least 60% of its magnitude, a threshold chosen for this work rather than taken from an
established convention. Against the proliferation score *PRMT5* retains 5.23/6.24 = 0.84 of its
magnitude on GPL6244 and 2.71/6.67 = 0.41 on GPL3290, so the failure on the second platform is not
marginal. Supplementary S10 gives each score's membership and coverage.

### 2.6 Substrate-motif map

Occurrences of the motif GRG were counted by exact string scan on committed protein sequences, with
overlaps included, since GRGRG contains two sites and two methylatable arginines. The motif
definition is taken from reference [13], whose abstract was retrieved but whose full text is not
open access and was not read, a limit that matters because the motif is the foundation of this
section. A fusion's retained 5′ sites are those at or before the last residue
fully encoded by the 5′ partner, excluding the seam residue, because each of these junctions splits
a codon. This work has no EMC cohort of its own: the *NR4A3*-fusion junctions are those reported in
[14], [15] and [16], none resting on a single source, while the EWSR1::ATF1 and EWSR1::FLI1
comparator junctions carry an exon number and a cumulative coding position in the source artifact
but no separate published quotation, and are reported on that footing. Supplementary S9 lists each
junction with the verbatim sentence it came from and two double-entry checks.

### 2.7 Reproduction, pre-specification and AI assistance

Every figure, table and number is regenerable from public data by scripts in the accompanying public
repository, `github.com/trimcrae/Rare-cancers`; section 8 names the artifact owning each value.
Analysis, figures and drafting were carried out with substantial assistance from an AI coding agent
operating on a version-controlled repository under my direction, using Anthropic Claude; the agent
is not an author and cannot be one, and I take responsibility for the content. I re-derived each
statistic, percentile, count and dependency figure against the committed artifact that owns it, and
read each cited source against its committed verbatim record; a per-value check of that kind cannot
detect a quantity reported correctly in two places at two different values, and one such is
disclosed in section 2.4. Supplementary S13 states the software stack, what that checking caught and
what it cannot show.

The reads, thresholds and controls of the expression panel were specified before the corresponding
data were retrieved, and what was pre-specified is narrower than this paper's subject: the
pre-specified read asks whether the *MTAP* locus is deleted in EMC, and records the supporting
direction as *MTAP* down at the floor together with *CDKN2A*. No directional expectation is recorded
anywhere for *PRMT5*, which entered the panel as the enzyme that *MTAP* loss would sensitise; the
choice to state the fusion rationale on *PRMT5* rather than on the four-gene group was made after
the figures were seen, and is registered as a correction in the appendix; and this read is one of
eighteen numbered reads run on the same fetch of the same 16 EMC tumours. Those facts decide the
family in section 3.5. The two documents together report about 110 quantities of which 15 are
corrected, and every other value is labelled as uncorrected where it carries a claim.

---

## 3. Results

### 3.1 Group-level readings

The PRMT5 methylosome group reads higher in EMC than in the comparator arm on both platforms
(*t* = 3.11 and 3.89), and the methionine-salvage context group likewise (*t* = 4.26 and 2.07);
neither is corrected for the number of genes examined.
*MAT2A* sits at the 99th percentile of its array on GPL6244 and *PRMT5* at the 91st.
The corresponding GPL3290 figures, the 84th and the 59th,
are percentiles of log-ratios against a reference pool and carry no absolute meaning, so on that
platform only the between-group contrast is interpretable. Scored as *MTAP* plus *CDKN2A* plus
*CDKN2B*, the locus reads lower in EMC on GPL6244 with all three genes readable, *t* = −4.06; on
GPL3290 only two of three are readable, which falls below the panel's three-gene minimum although
its coverage of 0.667 clears the 0.5 floor, so no score is emitted, which is an instrument limit
rather than a reading of the biology.

![Figure 1](./figures/mtap-prmt5-fig1-readings.png)

An elevated methylosome is consistent with the fusion rationale without being evidence for it, since
abundance is not dependency, and PRMT5, PRMT1 and MEP50 read higher across multiple sarcoma types
than in breast and lung cancer [3]. The low locus group score is likewise consistent with the *MTAP*
rationale without supporting it (section 3.2). Supplementary S3 gives every group's membership and
its full reading.

### 3.2 The locus, gene by gene and tumour by tumour

Read gene by gene the locus does not support selection on *MTAP*, and the two platforms disagree
about which gene moves.

**Table 2.** The three locus genes.

| gene | GPL6244 difference (95% CI) | fold | GPL6244 *t* | GPL3290 difference (95% CI) | GPL3290 *t* | array percentile, EMC | genome-wide rank of \|*t*\| |
|---|---|---:|---:|---|---:|---|---|
| *MTAP* | +0.121 (−0.223, +0.465) | 1.09 | +0.69 | −1.377 (−2.244, −0.510) | −2.27 | 72nd / 13th | top 74% / top 26% |
| *CDKN2A* | −0.923 (−1.292, −0.555) | 0.53 | −5.40 | +0.090 (−0.403, +0.583) | +1.33 | 53rd / 71st | top 3.5% / top 49% |
| *CDKN2B* | −0.254 (−0.556, +0.049) | 0.84 | −2.03 | unreadable | not applicable | 57th / not applicable | top 34% / not applicable |

The pre-specified criterion is a conjunction, *MTAP* down at the floor together with *CDKN2A*, and
neither platform satisfies it: on the 35-tumour platform *CDKN2A* is lower in EMC and *MTAP* is
flat, at 1.09-fold with an interval spanning 0.86 to 1.38, while on the 16-tumour platform *MTAP* is
lower, as the rationale predicts, and *CDKN2A* is not. That failure is why the rationale is not
supported here, and it claims less than the corrected statistics appear to license:
*MTAP* is at a multiplicity-adjusted *p* of 1.00 on both platforms, but that is a failure to reject
rather than a measurement that anything is absent, and the same procedure assigns 0.85 to *NR4A3*.
Nor is a difference of group means the right instrument for a subset event: the smallest difference
this design would detect in 80% of repetitions is 1.48-fold for *MTAP* on GPL6244 and 2.59-fold on
GPL3290. Every tumour was therefore read individually.

**Table 3.** The five *MTAP*-low EMC tumours on GPL3290.

| sample | *MTAP* percentile | *MTAP* *z* | *CDKN2A* percentile | *CDKN2A* *z* |
|---|---:|---:|---:|---:|
| GSM98511 | 1.1 | −2.79 | 89.3 | +1.08 |
| GSM98506 | 4.0 | −1.85 | 68.3 | +0.35 |
| GSM98503 | 4.6 | −1.65 | 73.2 | +0.48 |
| GSM98510 | 5.5 | −1.60 | 86.5 | +0.96 |
| GSM98499 | 10.4 | −1.21 | 50.5 | +0.09 |

Five of the ten EMC tumours on GPL3290 read below every comparator for *MTAP*, which no group
statistic can see, and not one of them reads low for *CDKN2A*: all five sit at or above the median
of their own array, and the tumour with the lowest *MTAP* reading carries the highest *CDKN2A* in
the arm. No tumour on either platform is deletion-consistent at the 25th-percentile cut, or at the
5th, 10th or 50th. Four further checks agree, and Supplementary S3a gives each in full: two more
9p21 genes read normally in those five samples, the within-arm rank association runs opposite to
co-deletion, the five are not globally dim arrays, and all ten EMC tumours share one reference
label, so a split within the EMC arm cannot come from the denominator of the measurement. On GPL6244
no EMC tumour is an *MTAP* low outlier at all.

![Figure 2](./figures/mtap-prmt5-fig2-locus-genewise.png)

Zero deletion-consistent tumours in sixteen bounds the frequency of such a tumour at 17% with 95%
confidence, against a survey in which MTAP protein loss reaches up to 20% in various sarcomas
without naming this histology [17]. The rationale is therefore not supported and is not closed:
sixteen archival tumours bound it loosely, and MTAP protein can be lost by mechanisms leaving the
gene present, so the test proposed in section 4.2 is a stain.

### 3.3 The sarcoma dependency prior

Across the 91 screened sarcoma cell lines, PRMT5 and MAT2A are dependencies in 94.5% and 96.7%
respectively. MTAP is not a dependency in any of them, which is the expected profile for a biomarker
rather than a target; that is consistent with the panel being read correctly, and it is weaker than
a positive control, since a gene can be a non-dependency for reasons that have nothing to do with
the instrument. PRMT5 is also a dependency in 94.1% of the release's non-sarcoma lines, giving a
sarcoma selectivity of 0.013 on a gene-effect scale where MAT2A reads −0.285, so on this panel it is
not distinguishable from a pan-essential gene. A growth effect in EMC would therefore be close to
expected, and the part any transfer must rest on is the effect on fusion-driven transcription. This
does not refute the class: the therapeutic argument for the *MTAP*-selected axis is a differential
between *MTAP*-deleted and *MTAP*-intact cells, which a gene-effect score cannot express, since an
MTA-cooperative inhibitor exploits a metabolic state rather than the raw dependency [6].

![Figure 3](./figures/mtap-prmt5-fig3-dependency-qualifier.png)

### 3.4 Comparator classes, pooled group against single gene

![Figure 4](./figures/mtap-prmt5-fig4-comparator-classes.png)

Pooled across the four methylosome genes, EMC ranks third of the five tumour classes, below desmoid
fibromatosis and solitary fibrous tumour. On *PRMT5* alone EMC has the highest class median, +1.30
against +1.05, +1.05, +1.04 and +0.94, and that comparison can be tested where the pooled one
cannot: exact permutation of the class means places EMC above low-grade fibromyxoid sarcoma at
*p* = 0.00004, above desmoid fibromatosis at 0.0065, above solitary fibrous tumour at 0.0087 and
above myxofibrosarcoma at 0.0152, of which the first three clear a within-figure Bonferroni, none
carrying any correction for the number of genes on the array. The sample-level picture is weaker
than separation: 9 of the 34 comparator tumour samples read at or above the lowest EMC tumour, and
one of the two pooled normal-muscle arrays reads above the EMC median (Supplementary S5b). For the
locus a group score reported a signal its decisive gene did not have; for the methylosome it hid one
its decisive gene does have. Neither is visible without reading the constituent genes, so a curated
group score is treated here as a summary rather than a unit of evidence.

### 3.5 PRMT5's statistic and the family behind its correction

*PRMT5* alone, the gene the fusion rationale depends on, reads *t* = 6.24 on GPL6244 and 6.67 on
GPL3290: a difference of +0.544 log2 intensity units (95% CI +0.375 to +0.713), or 1.46-fold, and of
+1.094 in log-ratio units (95% CI +0.688 to +1.499).

**Table 4.** The exact permutation of the labelling.

| platform | *PRMT5 t* | labelings enumerated | at least as extreme | exact two-sided *p* |
|---|---:|---:|---:|---:|
| GSE24369 / GPL6244 | +6.24 | 1,623,160 | 230 | 0.000142 |
| GSE4303 / GPL3290 | +6.67 | 8,008 | 1 | 0.000125 |

On GPL3290 the exact *p* cannot fall below 1/8,008 whatever the effect size, so that test's
resolution is the sample size rather than the biology, and both values are exact under an
exchangeability the arms do not satisfy.

**Table 5.** Genome-wide placement and multiplicity-adjusted *p*.

| gene | probes, GPL6244 / GPL3290 | SE percentile, GPL6244 / GPL3290 | GPL6244: *t*, rank of \|*t*\|, adjusted *p* | GPL3290: *t*, rank of \|*t*\|, adjusted *p* |
|---|---|---|---|---|
| *PRMT5* | 1 / 1 | 11th / 4th | +6.24, top 1.9%, 0.21 | +6.67, top 1.0%, 0.24 |
| *MAT2A* | 1 / 1 | 45th / 13th | +4.13, top 8.5%, 0.98 | +4.10, top 6.3%, 0.97 |
| *WDR77* | 1 / none | 7th / not applicable | +2.82, top 20.5%, 1.00 | unreadable |
| *MTAP* | 1 / 2 | 44th / 37th | +0.69, top 74.0%, 1.00 | −2.27, top 26.1%, 1.00 |
| *CDKN2A* | 1 / 1 | 49th / 9th | −5.40, top 3.5%, 0.51 | +1.33, top 49.3%, 1.00 |
| *NR4A3* (control) | 1 / 1 | 74th / 23rd | +4.66, top 5.9%, 0.85 | +1.70, top 38.5%; *n* = 9 versus 2 |
| *ENO3* (control) | 1 / 1 | 85th / 54th | +3.61, top 12.0%, 1.00 | +13.22, top 0.05%, 0.010 |

Every primary reading here rests on a single probe, and on GPL3290 through a bridge resolving 58.2%
of accessions on an array of expressed-sequence tags, so no cross-probe agreement check is available
for *PRMT5*. The standard-error column carries the pattern
behind its *t*, which sits in the bottom tenth of genes scored on GPL6244 and the bottom twentieth
on GPL3290, while *ENO3*, a published direct target of an NR4A3 fusion [18], has a smaller *t*
despite a difference three times larger. The adjusted
values are lower bounds and the GPL6244 column carries a Monte-Carlo standard error of about 0.003;
only *ENO3* on GPL3290 falls below 0.05.

**Table 6.** *PRMT5*'s family-wise adjusted *p* over four families.

| family | genes, GPL6244 / GPL3290 | adjusted *p*, GPL6244 | GPL3290 |
|---|---|---:|---:|
| the genes this paper reports (Table 5 plus *MKI67*) | 9 / 6 | 0.00015 | 0.000125 |
| the curated panel cache | 1,857 / 1,611 | 0.097 | 0.064 |
| the merged array-wide family, as used above | 5,449 / 4,848 | 0.208 | 0.238 |
| the same family restricted to genes measured in every sample | 5,449 / 3,126 | 0.208 | 0.031 |

Quoting one point from that range without naming the family would be uninterpretable. The array-wide
family is the one quoted, and the record of section 2.7 decides it: for a gene arrived at after a
curated panel and a genome-wide scan were examined, with no pre-specified direction, the right
question is how often a maximum this large arises across the genes scanned, and it answers 0.21 and
0.24. The fourth row is the largest single sensitivity and runs the other way, so on GPL3290 the
value turns on a convention as much as on the data.

The two controls do not behave alike. *ENO3* sits at the extreme of GPL3290, as a working instrument
should, while *NR4A3* is only mid-table there because two of the six comparator samples carry a
value for it, below the panel's floor, so its +1.70 comes from the genome-wide path; Supplementary
S5 gives that measured explanation and the pre-specified probe-placement alternative. A rank is in
any case not a corrected *p*: across labellings the family's largest |*t*| exceeds 5.4 in half of
them and reaches 6.24 in at least a fifth.

### 3.6 Four prespecified controls

Each control was specified against a named weakness before it was run, and is a control rather than
an additional hypothesis test. None of these values is corrected for multiplicity; Supplementary S5
carries all four in full.

The first asks whether the elevation is *PRMT5* or the PRMT family, which matters because the Ewing
report finds PRMT1 and PRMT5 elevated together across sarcoma types [3]. Eight family members are
readable on GPL6244 and seven on GPL3290, counting *PRMT5* itself; it ranks first on both while the
family as a group is flat (*t* = 0.33 and 1.34), though separation is clear only on GPL6244, since
*CARM1* reads +5.44 and *PRMT3* +3.47 on the other platform. The same table carries a
disanalogy with the source disease: *PRMT1* is flat in EMC on both platforms, at *t* = 0.18 and
1.36, whereas [3]'s largest effect is PRMT1 and PRMT5 inhibition combined.

The second control adjusts for proliferation, and on one platform takes most of the contrast.

**Table 7.** Confound adjustment.

| axis | platform | score elevated in EMC | *PRMT5 t*, raw to adjusted | reading |
|---|---|---|---:|---|
| proliferation, 12 genes | GPL6244, *n* = 35 | no, *t* = 0.45 | 6.24 to 5.23 | survives |
| proliferation, 12 genes | GPL3290, *n* = 16 | yes, *t* = 3.00 | 6.67 to 2.71 | most of the contrast goes with it |
| chondroid-marker lineage, 8 genes | GPL6244, *n* = 35 | no, *t* = 0.99 | 6.24 to 6.20 | untouched |
| chondroid-marker lineage, 8 genes | GPL3290, *n* = 14 | no, *t* = 0.36 | 6.67 to 6.52 | survives |

The second row weakens the transcript half of the fusion rationale. On GPL3290 the proliferation
score is itself higher in EMC, correlates with *PRMT5* at *r* = 0.60, and adjusting for it takes
*PRMT5* from 6.67 to 2.71; on GPL6244 the score is flat and the contrast barely moves. The platforms
disagree and the mundane explanation ranks above the biological: half the GPL3290 comparator arm was
hybridised against a different reference pool from every EMC tumour and the other half against a
third, which in a two-colour design shifts every ratio, and no reference-matched contrast exists
there, so splitting the comparator arm cannot discriminate the confound (Supplementary S5a).

The third control tests chondroid markers, whose premise needs care: EMC does not show true
cartilaginous differentiation [1] and no comparator is cartilage-lineage, so this is a check against
myxoid and matrix-associated transcription rather than a lineage control, and a null in it is
uninformative rather than reassuring. *PRMT5* and chondroid markers do not move together within
these samples (*r* = 0.05 and −0.04).

The fourth is a single-gene cellularity reference, specified in advance as approximately flat
because a large proliferation difference would say the contrast was being driven by how much tumour
each sample contains. *MKI67* reads *t* = 0.53 on GPL6244 as expected and *t* = 2.30 at +1.24 SD on
GPL3290, which is not flat, in the same direction and on the same platform as the twelve-gene score;
that reading is carried by two extreme comparator arrays rather than by EMC, and it survives the
multiplicity correction on neither platform. None of these adjustments removes a confound the proxy
measures badly, so a surviving result is much weaker than a failing one.

### 3.7 The substrate motif in the fusion protein

This section addresses where PRMT5's reported substrate motif sits in the fusion protein. Profiling
arginine methylation genome-wide after selective PRMT5 inhibition identifies a preference for
"arginine sandwiched between two neighboring glycines (a Gly-Arg-Gly, or 'GRG,' sequence)" [13],
which is a preference and not a rule: PRMT5 methylates arginines outside GRG, a GRG site is not
necessarily methylated, and a mapping experiment in a different substrate narrows it the same
way [19]. EWSR1 is itself extensively arginine-methylated [20], which is what makes the location of
the motif worth computing; that last reference was verified at title level only.

EWSR1 is 656 residues and carries eleven GRG sites, at residues 301, 303, 316, 320, 463, 489, 564,
574, 591, 602 and 635. The N-terminal SYGQ-rich low-complexity region every EWSR1 fusion retains
contains no site: every site lies beyond residue 300, in the two RGG-rich regions the fusion
truncates, and residue 301 of 656 falls at 46% of the protein, so they are not confined to the
C-terminal half. That is the observation this section supports, and it holds for the segment the two
diseases share.

**Table 8.** Retained 5′ GRG sites by fusion.

| fusion | 5′ residues retained | GRG sites kept | fraction of the 5′ partner's sites |
|---|---:|---:|---:|
| EWSR1::NR4A3 type 1, the commonest EMC fusion | 431 | 4 | 0.364 of EWSR1's 11 |
| EWSR1::NR4A3 type 2 | 264 | 0 | 0.000 of EWSR1's 11 |
| EWSR1::NR4A3 type 5 | 472 | 5 | 0.455 of EWSR1's 11 |
| EWSR1::FLI1, Ewing sarcoma, type 1 | 264 | 0 | 0.000 of EWSR1's 11 |
| EWSR1::ATF1, clear cell sarcoma, EWSR1 exon 8 | 324 | 4 | 0.364 of EWSR1's 11 |
| EWSR1::ATF1, clear cell sarcoma, EWSR1 exon 7 | 264 | 0 | 0.000 of EWSR1's 11 |
| EWSR1::ATF1, clear cell sarcoma, EWSR1 exon 10 | 348 | 4 | 0.364 of EWSR1's 11 |
| TAF15::NR4A3 | 161 | 0 | 0.000 of TAF15's 9 |

![Figure 5](./figures/mtap-prmt5-fig5-motif-map.png)

An earlier version of this analysis read the shared count of four between the commonest EMC fusion
and the commonest clear cell junction as quantitative support for transferring between the two
diseases. It is not, for a reason that is arithmetic rather than a matter of degree: the
retained-site count is a step function with one large plateau, since four sites cluster within
twenty residues and the next lies 143 residues away, so any breakpoint between residues 321 and 462
retains exactly four, across a window spanning 142 residues or 21.6% of the protein. EWSR1::NR4A3
type 1 cuts at 431 and EWSR1::ATF1 exon 8 at 324, 107 residues apart and both inside it, as is
EWSR1::ATF1 exon 10 at 348, and across all eight fusions the count takes three values, 0, 4 and 5.
The agreement is metric-dependent as well: counted as RG dipeptides, EWSR1::NR4A3 type 1 retains 8
and EWSR1::ATF1 exon 8 retains 7.

The table therefore does not license a prediction that retained-site count determines response.
EWSR1::FLI1 retains no sites and is the fusion in which a PRMT5 inhibitor's effect was shown to be
fusion-dependent [3], so whatever PRMT5 does in a FET-fusion sarcoma it does not require the fusion
protein to be the substrate, and EMC type 2 and TAF15::NR4A3 are correspondingly not predicted to be
unresponsive; wild-type FET proteins, Sm proteins and R-loop-resolution factors [19] carry their
motifs regardless of the breakpoint. Supplementary S9 names the junctions this analysis does not
hold. These counts do not show that any NR4A3 fusion is methylated, that PRMT5 is the enzyme, or
that methylation would be functionally consequential.

---

## 4. Discussion

### 4.1 Status of the two rationales

The 2025 comprehensive review of this disease considers neither rationale examined here [1]. Read
against the only public data able to address them, neither is supported, and the two fail
differently.

The *MTAP*-locus rationale fails on a per-sample reading. The pre-specified conjunction is satisfied
on neither platform, and the tumour-by-tumour reading is the stronger form of the same statement:
five of ten EMC tumours on one platform do sit below every comparator for *MTAP*, none carries the
*CDKN2A* reading that 9p21 co-deletion requires, two further 9p21 genes agree, and both alternative
explanations for the tail fail. Zero deletion-consistent tumours in sixteen is not a demonstration
of absence: it bounds the frequency at 17%, against a class prior in which sarcoma MTAP loss reaches
20% [17]. What the transcript data can say is that the pattern is not the one this rationale
predicts; what it cannot say is that no EMC tumour has lost MTAP protein, which is what an
MTA-cooperative agent's biology turns on and what a transcript could not have seen in any case.

The fusion rationale fails differently: this data does not support it and cannot test it. *PRMT5*
reads higher in EMC on both platforms and ranks first of the readable PRMT family on both, and after
correction for the number of genes examined neither reading clears a conventional threshold, at 0.21
and 0.24. Three further things stand between the readings and the rationale: the corrected value is
a property of the family and ranges over three orders of magnitude; on the 16-tumour platform
disease class cannot be separated from submission block, reference pool and platform assignment; and
the proliferation control disagrees between the platforms. Directional concordance is therefore the
most that can be claimed for the pair, and it is less than replication, since the deposits have not
been shown to contain different patients or centres and the larger is a study of a different disease
in which EMC is one comparison group.

Nor does the rest of the case establish the transfer, for reasons Supplementary S14 sets out in
full: the fusion-dependent PRMT5 requirement in a second EWSR1-fusion sarcoma [3] rests on one
engineered line whose authors attribute the dependence to Ewing-specific mechanisms, the clear cell
report [2] shows binding rather than methylation of the fusion, and section 3.7 shows that the
shared segment carries none of PRMT5's motif sites. What remains is that two other EWSR1-fusion
sarcomas show PRMT5 dependence, that EMC is a third, and that nobody has looked, which is a reason
to run an experiment rather than a result. Two further limits sit on any version of the
rationale: elevated PRMT5 is not specific to this disease on the published comparison [3], and
nothing here separates "higher than other sarcomas" from "a sarcoma-wide feature"; and PRMT5 is
required in 94.1% of non-sarcoma lines as well.

### 4.2 Two decisive experiments

For the *MTAP* rationale, MTAP immunohistochemistry on archival EMC tissue. The stain is routine and
is an accepted surrogate for homozygous 9p21 deletion, which was found in 90% to 100% of cases with
complete MTAP expression loss across a survey of 13,067 tumours from 149 tumour types [17]. That
survey does not name this histology, and the validity quoted runs from loss to deletion: the
converse requires a sensitivity [17] is not cited for, so a retained stain excludes the protein-loss
state rather than the deletion. Protein is nonetheless the right analyte, because an MTA-cooperative
agent depends on the metabolic consequence of MTAP protein loss however it arises; the clinical
selection reported for that class is genomic [6], so a stain and a trial's entry criterion are not
the same test.

For the fusion rationale, a PRMT5 inhibitor in a patient-derived EMC model with a readout that can
discriminate. Two are published, USZ20-EMC1 carrying EWSR1-NR4A3 and USZ22-EMC2 carrying
TAF15-NR4A3, used by their holders in a 40-agent panel run once on sarco-spheres, in which
carfilzomib showed high sensitivity and doxorubicin good-to-moderate sensitivity in both,
venetoclax no monotherapy response in the validation, and two combinations synergy in one model and
an additive effect in the other [21]. Whether any screen is currently running there is not
something this work can state.

The readout matters more than the compound. Section 3.3 shows that a growth effect is close to
expected in any line, so viability alone would discriminate nothing; the endpoint that bears on the
transfer is fusion-driven transcription, for which [2] supplies the precedent of a CRE reporter and
target-gene qPCR, together with a concurrent non-EMC comparator line. The compound's class must also
be named in advance, because it decides the answer in the source disease: of the three inhibitors
[2] tested, the two substrate-competitive compounds inhibited fusion-driven transcription in neither
line while the dual-site compound was potent in both, and [3] obtained its fusion-dependent effect
with one of the two that failed, so a negative in an EMC model with a substrate-competitive compound
would be hard to interpret. Supplementary S11 gives those results by class and one further arm [3]
suggests.

Outcome interpretations are fixed in advance, and the negative branch of each is the falsifier table
below. The positive branches are quickly said: PRMT5 inhibition active on a fusion-output readout in
an EMC model would be a fusion-class-transferred vulnerability not reported before in this disease,
and MTAP protein lost in a subset would define a genetically selected group in it. Both negative
branches are the more likely ones, which is what makes a hypothesis of this shape affordable in an
ultra-rare disease.

### 4.3 Falsification criteria

| # | claim | the observation that would kill it |
|---|---|---|
| F1 | PRMT5 supports fusion-driven transcription in EWSR1-fusion sarcoma | failure to reproduce the clear cell sarcoma result, or a demonstration that its mechanism is ATF1-specific and does not run through EWSR1 |
| F2 | the transfer from EWSR1-ATF1 to EWSR1::NR4A3 is reasonable | PRMT5 inhibition inactive on a fusion-output readout in an EMC model, the decisive test for the fusion rationale. That negative is worth publishing, because the fusion-class transfer is the interesting claim. The transfer already rests on one engineered line with partial fusion depletion in a third disease, whose authors attribute the dependence to a mechanism specific to that disease |
| F3 | *PRMT5* reads higher in EMC than in a sarcoma comparator arm and ranks first of the readable PRMT family | a third EMC series in which *PRMT5* is null or lower than its comparator arm, or does not rank first of the family. Already qualified: the reading does not clear a family-wise threshold on either platform |
| F4 | fired, and merged into F5. The claim that the locus reads low in EMC was a group-score claim, and the group score is not a unit of evidence here | superseded by F5 and F6, which are stated on the genes |
| F5 | fired. The low locus group read is not a reading of *MTAP*: *MTAP* is flat where the read is powered, the pre-specified conjunction with *CDKN2A* fails on both platforms, and no tumour of sixteen shows the joint *MTAP*-low and *CDKN2A*-low pattern that 9p21 co-deletion produces | already fired; only MTAP protein retained or lost can now move it |
| F6 | MTAP protein is lost in some EMC | MTAP immunohistochemistry retained across an EMC series, the decisive test for the *MTAP* rationale and now the only thing that could reopen it. A retained stain excludes the protein-loss state the window turns on; it does not exclude a 9p21 deletion, which needs a sensitivity [17] is not cited for |
| F7 | the readings are not proliferation or cellularity effects | partially fired, on one platform. Section 3.6: adjustment leaves *PRMT5* largely intact on GPL6244 (6.24 to 5.23, *n* = 35) and takes most of the contrast on GPL3290 (6.67 to 2.71, *n* = 16), where the score is itself elevated in EMC and the pre-specified *MKI67* reference moves with it. The platforms disagree, and this is the likeliest way the transcript reading is wrong |
| F8 | specificity rests on fusion-driven transcription, not on growth | a demonstration that PRMT5 inhibition slows EMC growth no more than it slows any other line's; the dependency of section 3.3, near-universal inside sarcoma and equally so outside it, makes this the likeliest way the fusion rationale fails |
| F9 | fired. The shared retained-site count between the commonest EMC and clear cell junctions carried quantitative content | already fired, by arithmetic in section 3.7: four sites cluster in twenty residues and the next is 143 residues away, so any breakpoint across a 142-residue window returns four. What survives is the narrower observation that the segment every EWSR1 fusion retains carries no site |
| F10 | the fusion protein is itself the relevant PRMT5 substrate | contradicted at one point already: EWSR1::FLI1 retains no site and PRMT5 inhibition is still fusion-dependent there [3], and reference [2] proposes PRMT5 as a binding co-activator rather than showing the fusion methylated. It is listed rather than deleted because it remains the mechanistic fork behind the transfer, and section 4.4 states why no experiment available to this work can settle it |

### 4.4 Limitations

The evidence base is sixteen EMC tumours on two decade-old array platforms. Three limitations are
structural, meaning no re-analysis of these data removes them. First, on GPL3290
disease class is collinear with GEO submission block, with the two-colour reference pool and with
within-study platform assignment (section 2.1), so a permutation that relabels those sixteen
samples is not exchangeable and that platform is reported as a consistency check rather than as
independent evidence. Second, every primary reading rests on a single probe per gene per platform,
and on GPL3290 through a symbol bridge resolving 58.2% of accessions on an expressed-sequence-tag
array, so a mis-annotated or cross-hybridising spot is excluded by nothing in this work. Third, no
EMC cell line carrying the fusion appears in any public dependency dataset, so no dependency
evidence for this axis in this disease exists or can be generated computationally, and the
mechanistic fork of F10 cannot be settled here: separating "the fusion protein is the substrate"
from "PRMT5 acts on something the fusion depends on" would need isogenic constructs and an
arginine-substitution mutant, and the two published models differ in their 5′ partner rather than
in transcript type.

What survives multiplicity correction should be stated plainly. Just one reading falls below 0.05
once the number of genes examined is accounted for, and it is an instrument control, *ENO3* on
GPL3290 at 0.010; the primary contrast does not, at 0.21 and 0.24, nor *CDKN2A* at 0.51. Those figures are lower bounds, they depend on the family, and a non-rejection is not a
demonstration of absence, which is why the *MTAP* result is argued from the per-sample conjunction
of section 3.2. The two documents report about 110 quantities and correct 15; Supplementary S14
gives those qualifications with the count of comparisons behind them.

The original source of the fusion rationale was posted as a preprint and has since been published in
a peer-reviewed journal [2]; its statements were read from the preprint full text and the published
version was identified by literature search rather than read, so the bibliographic record in [2] is
to be confirmed at the publisher, and that caveat attaches to every statement drawn from it,
including the inhibitor-class result. The fusion-class transfer is argued rather than assumed, and
an argument is not a result: EWSR1::ATF1 and EWSR1::NR4A3 do not share a DNA-binding domain, a
target repertoire or a disease biology, and no result presented here is an observation in EMC.

Three further limits are elaborated in Supplementary S14: the primary contrasts are insensitive to
the accidental exclusion of five deposited samples while the per-class comparison of Figure 4 is
not, so Figure 4 is reported with the class included; the motif analysis is a sequence argument on
constructs rather than patients and cannot be read as a response predictor; and the prior-art
screens matched titles and abstracts rather than full text. Nothing here has been tested in an EMC
cell, and no agent in this class has been given to a patient with this disease.

---

## 5. Conclusion

Two independent rationales place the PRMT5 methylosome in front of a disease for which no clinically
validated agent directly targets the driver, and the only public data able to address them supports
neither. Selection on *MTAP* loss fails its own pre-specified test on both platforms, and tumour by
tumour as well: five of ten EMC tumours on one platform read below every comparator for *MTAP*, none
carries the low *CDKN2A* that 9p21 co-deletion requires, and no tumour of sixteen is
deletion-consistent, which bounds rather than excludes the event. The fusion-class rationale is not
tested by this data: *PRMT5* reads higher in EMC on both platforms and first of the readable PRMT
family on both, but that reading clears no conventional threshold once the number of genes examined
is accounted for, rests on a corrected value ranging across three orders of magnitude with the
family chosen, comes on one platform from a deposit in which disease class cannot be separated from
batch, and names a target required in almost every screened cell line. The sequence analysis
contributes one durable observation, that the segment every EWSR1 fusion retains carries none of
PRMT5's reported motif sites, and withdraws another. Each rationale ends at an inexpensive and
decisive experiment, and neither has been run.

---

## 6. Declarations

**Competing interests.** The author declares no competing interests. He holds no position, equity,
consultancy or patent relating to PRMT5, MAT2A, MTAP or any agent named here, and has no financial
relationship with any entity developing them.

**Funding.** None. The work was funded by no grant, institution or company, and was carried out by
one unaffiliated individual using public data and personal compute. No experiment was possible, and
every claim here is therefore an argument from data generated by others.

**Ethics.** No human subjects, no animal work and no identifiable patient data. Every dataset used is
public and de-identified at source.

**Patient consent.** Not applicable; no human participants were involved and no identifiable patient
data are reported.

**Permission to reproduce.** Not applicable; no third-party figure, table or text is reproduced.

**Clinical trial registration.** Not applicable. The trial identifier cited in section 1.1 belongs
to a published third-party study and no trial is reported here.

**Author contributions.** Sole author. In CRediT terms: conceptualization, methodology, software,
formal analysis, investigation, data curation, visualization, writing (original draft), writing
(review and editing).

**Data availability.** Section 8, which names the public accessions and the artifact that owns each
reported value.

**Preprint.** The author intends to deposit this manuscript as a preprint on bioRxiv and to link the
preprint to any published version.

**Generative AI.** Analysis, figures and drafting were carried out with substantial assistance from
an AI coding agent, Anthropic Claude, operating on a version-controlled repository under the
author's direction. Its use, its influence on two of the corrections registered in the appendix, and
what the author personally re-derived and re-read are described in section 2.7. The agent is not an
author and the author takes responsibility for the content.

---

## 7. Supplementary information

The accompanying supplementary file
[`emc-mtap-prmt5-hypothesis-SI.md`](./emc-mtap-prmt5-hypothesis-SI.md) carries the methods and full
readings behind the main text in sections S1 to S10, and in S11 to S14 the material summarised above
in a sentence and a pointer: the two source reports of the fusion rationale as they read (S11), the
prior-art screens and the pan-sarcoma panel reconciliation (S12), the software stack and what the
verification does and does not establish (S13), and the limitations in full (S14). The modality
census, the 591-text corpus record and the 322-record prior-art screen of section 1.3 are deposited
with it as the author's unpublished supporting analyses.

---

## 8. Data and code availability

Both expression series (GSE24369, GSE4303) and the DepMap CRISPR release are public. The DepMap
public 24Q4 release is distributed as figshare article 27993248, from which `CRISPRGeneEffect.csv`
and `Model.csv` are read. Analysis code and every artifact below are in the public repository
`github.com/trimcrae/Rare-cancers`; an archived release of the state this manuscript is built on
will be deposited at submission. No data generated by the author is withheld, because this study
creates no new measurement.

| item | location |
|---|---|
| Expression readings, every *z*, percentile and group score | [`emc-expression-panels.json`](../modalities/emc-expression-panels.json) |
| Per-sample values as fetched, both platforms | [`emc-expression-panels-inputs.json`](../modalities/emc-expression-panels-inputs.json) |
| Multiplicity correction, reference-channel split, exclusion sensitivity, per-class medians | [`emc-prmt5-multiplicity.json`](../modalities/emc-prmt5-multiplicity.json) |
| Per-sample 9p21 locus reading, the *CDKN2A* conjunction and its controls (section 3.2) | [`emc-mtap-locus-persample.json`](../modalities/emc-mtap-locus-persample.json) |
| Effect sizes with intervals, minimum detectable effects, family sensitivity, per-class tests | [`emc-prmt5-effect-sizes.json`](../modalities/emc-prmt5-effect-sizes.json) |
| The seeded random symbol sample the correction's family draws on | [`emc-hypoxia-null-background.json`](../modalities/emc-hypoxia-null-background.json) |
| Grading of this route against its selection criterion | [`census-route-expression-grading.json`](../modalities/census-route-expression-grading.json) |
| Sarcoma-line dependency prior | [`depmap-sarcoma-dependency.json`](../modalities/depmap-sarcoma-dependency.json) |
| Control calculations of section 3.6 | [`emc-prmt5-route-controls.json`](../modalities/emc-prmt5-route-controls.json) |
| Modality census of section 1.1 and section 1.3 | [`cancer-modality-census.md`](./cancer-modality-census.md) |
| GEO cohort search behind section 2.1 | [`emc-cohort-search-inputs.json`](../modalities/emc-cohort-search-inputs.json) |
| Substrate-motif counts and their double-entry checks | [`emc-prmt5-substrate-motif-map.json`](../modalities/emc-prmt5-substrate-motif-map.json) |
| Committed protein sequences and sourced breakpoints | [`emc-fet-construct-designs.json`](../modalities/emc-fet-construct-designs.json), [`emc-fet-idr-census.json`](../modalities/emc-fet-idr-census.json) |
| Citation anchor, every identifier read from a retrieval | [`mtap-prmt5-emc-citations.json`](../literature/mtap-prmt5-emc-citations.json) |
| Prior-art screen of section 1.3, with its retrieval record | [`emc-prior-art-2026-08-09.json`](../literature/emc-prior-art-2026-08-09.json) |
| Composition of the pan-sarcoma panel behind reference [3] (section 1.3) | [`prmt5-ewing-expression-panel-composition-2026-08-10.json`](../literature/prmt5-ewing-expression-panel-composition-2026-08-10.json) |
| Figure provenance hashes, artifacts and images | [`mtap-prmt5-figure-provenance.json`](./figures/mtap-prmt5-figure-provenance.json) |

---

## 9. References

1. Remiszewski P, Falkowski S, Szumera-Ciećkiewicz A, Spałek MJ, Rutkowski P, Czarnecka AM. From pathogenesis to the patient's bedside: a comprehensive review of extraskeletal myxoid chondrosarcoma. *Journal of Cancer Research and Clinical Oncology* 2025;151(11):283. PMID 41055792. PMC12504171. doi 10.1007/s00432-025-06316-5.
2. Li BX, David LL, Davis LE, Xiao X. Protein arginine methyltransferase 5 is essential for oncogene product EWSR1-ATF1-mediated gene transcription in clear cell sarcoma. *Journal of Biological Chemistry* 2022;298(10):102434. doi 10.1016/j.jbc.2022.102434. PMC9513783.
3. Ward CM, Brockwell C, McNee GS, Orton E, Prowse ENP, Gatz SA, et al. Arginine methylation regulates Ewing sarcoma cell viability in a EWSR1::FLI1 dependent manner and provides a therapeutic opportunity. *Frontiers in Oncology* 2025;15:1538208. PMID 40823091. PMC12354397. doi 10.3389/fonc.2025.1538208.
4. Kryukov GV, Wilson FH, Ruth JR, Paulk J, Tsherniak A, Marlow SE, et al. MTAP deletion confers enhanced dependency on the PRMT5 arginine methyltransferase in cancer cells. *Science* 2016;351(6278):1214-1218. PMID 26912360. PMC4997612. doi 10.1126/science.aad5214.
5. Marjon K, Cameron MJ, Quang P, Clasquin MF, Mandley E, Kunii K, et al. MTAP Deletions in Cancer Create Vulnerability to Targeting of the MAT2A/PRMT5/RIOK1 Axis. *Cell Reports* 2016;15(3):574-587. PMID 27068473. doi 10.1016/j.celrep.2016.03.043.
6. Engstrom LD, Aranda R, Waters L, Moya K, Bowcut V, Vegar L, et al. MRTX1719 Is an MTA-Cooperative PRMT5 Inhibitor That Exhibits Synthetic Lethality in Preclinical Models and Patients with MTAP-Deleted Cancer. *Cancer Discovery* 2023;13(11):2412-2431. PMID 37552839. PMC10618744. doi 10.1158/2159-8290.CD-23-0669.
7. Bou Zerdan M, Ashok Kumar P, Haroun E, Srivastava N, Ross J, Sivapiragasam A. Genomic landscape of metastatic breast cancer (MBC) patients with methylthioadenosine phosphorylase (MTAP) loss. *Oncotarget* 2023;14:178-187. PMID 36913304. PMC10010627. doi 10.18632/oncotarget.28376.
8. Ho MC, Wilczek C, Bonanno JB, Xing L, Seznec J, Matsui T, et al. Structure of the arginine methyltransferase PRMT5-MEP50 reveals a mechanism for substrate specificity. *PLoS ONE* 2013;8(2):e57008. PMID 23451136. PMC3581573. doi 10.1371/journal.pone.0057008.
9. Chow WA. Update on chondrosarcomas. *Current Opinion in Oncology* 2007;19(4):371-376. PMID 17545802. doi 10.1097/cco.0b013e32812143d9.
10. Filion C, Motoi T, Olshen AB, Laé M, Emnett RJ, Gutmann DH, et al. The EWSR1/NR4A3 fusion protein of extraskeletal myxoid chondrosarcoma activates the PPARG nuclear receptor gene. *The Journal of Pathology* 2009;217(1):83-93. PMID 18855877. PMC4429309. doi 10.1002/path.2445.
11. Subramanian S, West RB, Marinelli RJ, Nielsen TO, Rubin BP, Goldblum JR, et al. The gene expression profile of extraskeletal myxoid chondrosarcoma. *The Journal of Pathology* 2005;206(4):433-444. PMID 15920699. doi 10.1002/path.1792.
12. Dempster JM, Boyle I, Vazquez F, Root DE, Boehm JS, Hahn WC, et al. Chronos: a cell population dynamics model of CRISPR experiments that improves inference of gene fitness effects. *Genome Biology* 2021;22(1):343. PMID 34930405. PMC8686573. doi 10.1186/s13059-021-02540-7.
13. Musiani D, Bok J, Massignani E, Wu L, Tabaglio T, Ippolito MR, et al. Proteomics profiling of arginine methylation defines PRMT5 substrate specificity. *Science Signaling* 2019;12(575):eaat8388. PMID 30940768. doi 10.1126/scisignal.aat8388.
14. Nishio J, Iwasaki H, Nabeshima K, Naito M. Cytogenetics and molecular genetics of myxoid soft-tissue sarcomas. *Genetics Research International* 2011;2011:497148. PMID 22567356. PMC3335514. doi 10.4061/2011/497148.
15. Cerrone M, Cantile M, Collina F, Marra L, Liguori G, Franco R, et al. Molecular strategies for detecting chromosomal translocations in soft tissue tumors (review). *International Journal of Molecular Medicine* 2014;33(6):1379-1391. PMID 24714847. PMC4055444. doi 10.3892/ijmm.2014.1726.
16. Agaram NP, Zhang L, Sung YS, Singer S, Antonescu CR. Extraskeletal myxoid chondrosarcoma with non-EWSR1-NR4A3 variant fusions correlate with rhabdoid phenotype and high-grade morphology. *Human Pathology* 2014;45(5):1084-1091. PMID 24746215. PMC4015728. doi 10.1016/j.humpath.2014.01.007.
17. Gorbokon N, Wößner N, Lennartz M, Dwertmann Rico S, Kind S, Reiswich V, et al. Prevalence of S-methyl-5'-thioadenosine Phosphorylase (MTAP) Deficiency in Human Cancer: A Tissue Microarray Study on 13,067 Tumors From 149 Different Tumor Types. *American Journal of Surgical Pathology* 2024;48(10):1245-1258. PMID 39132873. PMC11404761. doi 10.1097/PAS.0000000000002297.
18. Kim AY, Lim B, Choi J, Kim J. The TFG-TEC oncoprotein induces transcriptional activation of the human β-enolase gene via chromatin modification of the promoter region. *Molecular Carcinogenesis* 2016;55(10):1411-1423. PMID 26310886. doi 10.1002/mc.22384.
19. Mersaoui SY, Yu Z, Coulombe Y, Karam M, Busatto FF, Masson JY, et al. Arginine methylation of the DDX5 helicase RGG/RG motif by PRMT5 regulates resolution of RNA:DNA hybrids. *The EMBO Journal* 2019;38(15):e100986. PMID 31267554. PMC6669924. doi 10.15252/embj.2018100986.
20. Belyanskaya LL, Gehrig PM, Gehring H. Exposure on cell surface and extensive arginine methylation of Ewing sarcoma (EWS) protein. *Journal of Biological Chemistry* 2001;276(22):18681-18687. PMID 11278906. doi 10.1074/jbc.m011446200.
21. Bangerter JL, Harnisch KJ, Chen Y, Hagedorn C, Planas-Paz L, Pauli C. Establishment, characterization and functional testing of two novel ex vivo extraskeletal myxoid chondrosarcoma (EMC) cell models. *Human Cell* 2023;36(1):446-455. PMID 36316541. PMC9813045. doi 10.1007/s13577-022-00818-x.

Author lists, journal titles, volumes and pages are taken from the retrieval records in
[`submission-reference-metadata-2026-08-09.json`](../literature/submission-reference-metadata-2026-08-09.json),
[`remaining-reference-metadata-2026-08-09.json`](../literature/remaining-reference-metadata-2026-08-09.json)
and [`emc-prior-art-2026-08-09.json`](../literature/emc-prior-art-2026-08-09.json). The published
version of reference 2 was identified by literature search on 2026-08-10 and its record is in
[`prmt5-ccs-preprint-publication-status-2026-08-10.json`](../literature/prmt5-ccs-preprint-publication-status-2026-08-10.json);
neither the publisher page nor the PubMed Central record was reachable from the working environment,
so that entry's bibliographic details come from a search index and are to be confirmed at the
publisher before submission. Where a record lists more than six authors the first six are given.

---

## 10. Display-item legends

Legends for the eight tables and five figures called out in sections 2 to 4.

### Tables

Table 1. The two series.

Table 2. The three locus genes, as log2 differences with 95% Welch intervals; fold applies to
GPL6244 only (section 2.1).

Table 3. The five EMC tumours on GPL3290 whose *MTAP* reading falls below every comparator, with
*CDKN2A* in the same samples, as percentiles within each sample's own array.

Table 4. The exact permutation of the labelling.

Table 5. Genome-wide placement and multiplicity-adjusted *p*, with each gene's probe count and
standard-error percentile. *NR4A3* and *ENO3* [18] are instrument controls.

Table 6. *PRMT5*'s family-wise adjusted *p* over four families, on the same labellings.

Table 7. Confound adjustment.

Table 8. Retained 5′ GRG sites by fusion, ordered as Figure 5 plots them.

### Figures

**Figure 1.** Every tumour in the analysed arms, on both platforms. Per-sample *z* against each
array's own probe distribution; bars are medians. The five solitary fibrous tumours GSE24369
deposits are not in the analysed arms and appear in Figure 4 (section 2.1). The two platforms share
no axis, because one is single-channel intensity and the other a two-colour log-ratio. A gene with
no probe is marked unreadable, which records a missing measurement and not an absence of expression.

**Figure 2.** The locus read per tumour. Filled circles are EMC tumours and open squares comparator
sarcomas; bars are medians, while Table 2 reports differences of means, so the two need not agree in
direction for a gene as flat as *MTAP*. The left panel shows all three genes on GPL6244, where all
three are readable. The right panel plots *MTAP* against *CDKN2A* per tumour on GPL3290, where a
homozygous 9p21 deletion would place a tumour low on both; no tumour on either platform falls in
that lower-left quadrant.

**Figure 3.** The dependency prior, inside and outside sarcoma, with Wilson 95% intervals. PRMT5 and
MAT2A are dependencies in almost every line on either side, so a growth effect on silencing them is
close to expected and the panel supports no statement of tissue selectivity; MTAP is not a
dependency in either group. The panel contains no EMC line, so every value is a transfer from other
sarcomas, limited by the complete absence of an EMC observation rather than by sample size.
Supplementary S4 gives the panel in full.

**Figure 4.** Pooled group against single gene, for every class GSE24369 deposits. One comparator
class, low-grade fibromyxoid sarcoma, is FUS::CREB3L2 and therefore a FET-fusion control on whether
the reading is simply what a fusion sarcoma looks like. Solitary fibrous tumour is drawn although it
is not in the comparator arm, because it is deposited in the series and was excluded only by the
classifier's want of a pattern for it (section 2.1); the two pooled skeletal-muscle samples are
normal tissue, are marked as not a comparator, and read higher than EMC on *PRMT5*. Left-panel axis
labels give the number of gene-by-sample values, which is the class's sample count times four genes,
so those points are not independent observations and no test is run on them.

**Figure 5.** The motif, the RGG regions, and where each fusion cuts. EWSR1 is drawn once at full
length with its eleven GRG sites and its two RGG-rich regions; below it, each fusion's retained 5′
segment on the same ruler. The shaded band marks the 142-residue window from 321 to 462 across which
every breakpoint retains exactly four sites. EWSR1::FLI1 keeps no site, and it is the fusion in which
a PRMT5 requirement has been shown to be fusion-dependent. TAF15::NR4A3 is in Table 8 but not
plotted, because TAF15 is a different 5′ protein and therefore a different ruler.

---

## Appendix A. Superseded numbers and retracted claims

A corrected value is registered here rather than dropped, and the live text above carries only the
current value. This appendix and the YAML frontmatter are repository record and are removed at
submission. The full corrections register, including the values that only ever appeared in the
supplementary file, is in the SI appendix.

| superseded | current | where it lived | why it changed |
|---|---|---|---|
| The title, *"The PRMT5 methylosome in extraskeletal myxoid chondrosarcoma: a fusion-class rationale that survives and an MTAP-locus rationale that does not"*, and every clause resting on the verb "survives" in the abstract, §4.1 and §5 | the present title, and a statement in each place that neither rationale is supported | title, abstract, §1, §3, §4.1, §5, cover letter, pre-posting checklist | ⛔ The strongest single objection to the previous draft, raised independently by three simulated adversarial reviews. Nothing bearing on the fusion rationale cleared 0.05 after the correction the paper itself elected to apply; the only reading that did is an instrument control (§4.4). "Survives" was doing the work of a result that did not exist, and the claim structure rather than the adjectives had to change |
| *"the commonest EMC fusion and two of three reported clear cell fusions retain four [sites]"* offered in §3.7, §4.1, §5 and the abstract as quantitative content supporting the fusion-class transfer | the plateau is disclosed and the inference withdrawn; what §3.7 concludes is that the retained segment carries no site | §3.7, figure 5 caption, §4.1, §5, abstract, F9 | ⛔ Arithmetically near-inevitable rather than informative. EWSR1's GRG sites cluster at 301, 303, 316 and 320 with the next at 463, so **every** breakpoint in residues 321 to 462 retains exactly four: a 142-residue plateau spanning 21.6% of the protein, and both matched breakpoints fall inside it, 107 residues apart. The agreement is also metric-dependent (8 against 7 retained RG dipeptides) |
| *"It is also at a multiplicity-adjusted p of 1.00 on both platforms, which is the one place in this paper where correcting for the number of genes examined strengthens the argument rather than weakening it: the closure of this rationale is exactly what an adjusted p of 1.00 states."* | the closure argument now rests on the failure of the pre-specified conjunction and on the per-sample *CDKN2A* cross-check of §3.2 | §3.2, with echoes in §4.1, §5, the abstract and F5 | ⛔ A statistical error imported verbatim from a round-one review. An adjusted *p* of 1.00 is a failure to reject, not a demonstration of absence, and the paper's own SI §S5c said so. The same procedure assigns 0.85 to *NR4A3* on GPL6244, the transcript the disease-defining fusion places under a new promoter |
| The *MTAP* rationale described as "closed at transcript level by the data reported here" | not supported, with the frequency bounded at 17% in sixteen tumours and the question left to a stain | §3.2, §4.1, §5, title, F5, F6 | A mean test is mis-specified for a subset event and cannot close one. The per-sample analysis of §3.2 is the right test, and it is stronger evidence than the group mean was, but zero of sixteen bounds a frequency rather than excluding an event |
| *"What survives correction is the replication … two independently collected series"* | directional concordance between two deposits, with independence not established | §4.1, §4.4 | §4.4 already said in the same section that two series are not a replication set. Nothing in the record shows the two deposits' EMC tumours are different patients or centres, GSE24369 carries no linked publication, and GPL3290 is structurally confounded (§2.1) |
| *"the other three members are flat or lower in EMC and dilute it"*, of the methylosome group | *WDR77* and *CLNS1A* are higher in EMC but much smaller, at *t* = +2.82 and +2.53, and *RIOK1* is lower, so the group mean is diluted | §4.1 | Contradicted by §3.5's own table two sections earlier, which prints the *WDR77* figure. The weaker statement is the true one |
| "eight systemic classes in clinical use" | eight classes in clinical use, of which two are local therapies | §1.1 | The census the sentence cites lists radiotherapy and surgery among its eight, so the systemic count is six. The word "systemic" was introduced by the previous revision while re-attributing the number |
| "On GPL3290 only two of three are readable, which falls below the panel's coverage floor" | below the panel's three-gene minimum, although its coverage of 0.667 clears the 0.5 floor | §3.1 | The artifact records coverage 0.667 against a floor of 0.5, so the criterion named was the one the group passed |
| "elevated methylosome expression is reported across many malignancies [3]" | PRMT5, PRMT1 and MEP50 read higher across multiple sarcoma types than in breast and lung cancer [3] | §3.1 | [3] says the former of PRMTs generally, in its introduction and on a citation of its own; the latter is what [3] measured, and it is the proposition the citation ledger records |
| Reference [21] cited for venetoclax among "drug sensitivities … validated in both", for "two synergistic pairs … validated in both", and for "a screen that already runs" | the source's own findings: carfilzomib high and doxorubicin good-to-moderate in both models, no venetoclax monotherapy response in the validation, synergy in one model and an additive effect in the other, from a 40-agent panel run once and published in 2023 | §4.2 and the abstract | The manuscript's sentence tracked that paper's Methods, which name what was tested; its Results record venetoclax as a validated non-responder. "A screen that already runs" is a present-tense claim about another laboratory that no source supports, and it was load-bearing in the affordability argument |
| "Both fusions retain the same N-terminal EWSR1 segment, which is the region the sequence analysis of section 3.7 measures" | the descriptions of [2] and [3] in §1.2, stated from their committed full texts | §1.2 | Self-defeating as written: §3.7's own finding is that the shared segment carries no site, so §3.7 measures the region the fusions do not share. The activation-domain statement it had replaced is citable to [1] and the transfer is now argued from what each source shows |
| "a fusion-dependent PRMT5 requirement measured in a disease that is not EMC", given without the design or the source's own mechanism | [3]'s design and proposed mechanism stated in §1.2 and §4.1 | §1.2, §4.1, F2 | One engineered line, partial fusion depletion, four-day viability; and a mechanism the source attributes to Ewing-specific replication stress and BRCA1 sequestration, with olaparib alone fusion-dependent in the same figure. Omitting the second decides whether the transfer is a fusion-class argument or a disease-specific one |
| "a clinical-stage PRMT5 inhibitor inhibited growth in vitro and in vivo [2]" | the three compounds [2] tested, their two mechanistic classes and their differing results | §1.2, §4.2 | True of one of three, and the other two are the class that [3] used. A cited result described more favourably than its source supports |
| The two-construct experiment, offered as one of two decisive experiments and as the settling test for F10 | deleted; §4.4 states why no experiment available to this work settles that fork | §4.2, F10 | The two published models are EWSR1-NR4A3 and TAF15-NR4A3, not type 1 and type 2, so the comparison as described cannot be run; and type 1 and type 2 differ by 167 residues of EWSR1 and in the NR4A3 moiety, so a difference between them could not be attributed to four glycine-flanked arginines |
| "the only readable EMC expression data" | the only publicly deposited EMC expression data returned by a committed six-query GEO search | §2.1 | Reference [10] profiled three further EMC tumours on Affymetrix U133A. No deposit for it was returned, and its comparison set is recorded as unpublished data, so it could not be re-analysed; but the earlier phrasing claimed more than a search of GEO can support |
| "18,474 on GPL6244 and 14,402 on GPL3290" symbols scored in the genome-wide placement | 18,688 on GPL6244; 14,404 of the 14,932 carrying a probe on GPL3290 | §2.4, SI §S10 and the pre-posting checklist | ⛔ The superseded pair appears in **no committed artifact at any point in the history of this repository**. Both correct values are carried by two artifacts independently: `per_platform.*.genome_wide_placement.n_symbols_scored` in [`emc-prmt5-route-controls.json`](../modalities/emc-prmt5-route-controls.json) and `platforms.*.genome_wide_null` in [`emc-expression-panels.json`](../modalities/emc-expression-panels.json). This is the same failure class as the *MTAP* row below: a number that entered the prose from a source the repository cannot show |
| "every symbol the platform's probes map to" | 18,688 scored of 18,688 with a probe on GPL6244; 14,404 scored of 14,932 on GPL3290 | §2.4 | On GPL3290, 528 symbols carry a probe and yielded no statistic, so the original phrasing described a computation that was not performed |
| "The family is every symbol two committed input caches hold. That family is 5,449 symbols on GPL6244 and 4,848 on GPL3290" | the caches hold 5,449 and 5,216; on GPL3290 368 fail the arm floor, so the families are 5,449 and 4,848 | §2.4 | The same error class as the row above: the description named a set larger than the one used, without saying what was dropped |
| The mapped-symbol universe of GPL6244 stated as 18,688 in one paragraph of §2.4 and 18,724 in the next, with no reconciliation | both values retained, with their two platform-table resolutions and dates named, and the 0.2% difference stated not to move an adjusted *p* | §2.4, SI §S5c | ⛔ One quantity reported at two values two paragraphs apart, which is exactly the failure a per-value check cannot detect and the reason §2.7's account of the checking was rewritten again. The two come from a 2026-08-07 and a 2026-08-09 resolution of the same platform table; reconciling them needs a network re-fetch this environment cannot make |
| "EMC ranks second of four comparator classes, below desmoid fibromatosis" | third of the five tumour classes, below desmoid fibromatosis and solitary fibrous tumour | §3.4, figure 4, SI §S4 and §S6, and the pre-posting checklist | The figure drew only the samples in the panel's arms, and GSE24369 deposits two classes that are not in them: five solitary fibrous tumours the classifier had no pattern for, and two pooled skeletal-muscle references excluded by design. Both are now drawn. The primary contrasts are unaffected (§4.4); the ranking claim was not. ⚠ The correction reached §3.4 and figure 4 in the previous revision and did not reach SI §S4 or the checklist, which is what rule 1.3's registry exists to catch and was not given anything to catch it with |
| "*PRMT5* alone does, with a median of +1.30 against +1.05, +1.04 and +0.94" | +1.30 against +1.05, +1.05, +1.04 and +0.94 | §3.4 and figure 4 | Same cause. The added class, solitary fibrous tumour, sits at +1.05 and ranks second on *PRMT5*, so EMC remains highest of the tumour classes and the gap is narrower than three comparator classes suggested |
| "four comparator classes" | "the five tumour classes", with EMC named as the index class rather than a comparator | figure 4 caption | EMC is not a comparator, and the count changed with the row above |
| "*PRMT5* alone separates it from the other tumour classes" | EMC has the highest class median on *PRMT5*, with the four per-class exact tests and the sample overlap reported | §3.4, §4.1 | "Separates" is true of class medians and false of samples: 9 of 34 comparator tumours read at or above the lowest EMC tumour, and one of the two normal-muscle arrays reads above the EMC median. The tests were available and had not been run |
| Falsifiers F3 and F4 stated on curated group scores | F3 restated on *PRMT5*; F4 fired and merged into F5 and F6 | §4.3 | §3.4 concludes that a group score is not a unit of evidence here, and F4 tested a rationale that F5 in the next row records as already fired |
| "for which no targeted agent exists" | no clinically validated agent directly targets NR4A3 | the abstract | The stronger form is not what reference [1] supports. The weaker form is what [1] states and is unassailable |
| "The locus signal on the powered platform is *CDKN2A*" | what signal the locus group score has is carried by *CDKN2A*, which does not survive multiplicity correction either (adjusted *p* = 0.51) | §3.2 | A positive claim about *CDKN2A* was resting on an uncorrected statistic |
| "The natural history is indolent and the tumour is slow-cycling" | mitotic activity in this tumour is usually low, cited to [1], and tested by the *MKI67* control of §3.6 | §1.1 | The claim was uncited and load-bearing twice over. Reference [1] does support the weaker form and the previous revision withdrew it for want of a citation the reference list already held |
| "The systemic classes with any disease-specific evidence number about eight" | see the "eight systemic classes" row above | §1.1 | Same number, re-attributed and then re-corrected |
| The title's third clause, "and two inexpensive tests" | dropped | the title | 22 words and 166 characters is long for the journal, and the clause promised what the other two clauses already imply |
| *"The fusion-class transfer is an assumption."* | the transfer is argued rather than assumed, and the argument's two legs are stated at the strength their sources support | §4.4 | ⚠ This row is itself narrowed by the first two rows of this appendix. Neither leg lifts the transfer above an assumption: the motif match carries no information, and the Ewing result's own mechanism is disease-specific |
| "Its status since 2022 was not established here", of the preprint behind reference [2] | the preprint has been published in a peer-reviewed journal, and the reference is now that version, with the caveat carried at every point of use | §1.2, §4.4 and §9 | A caveat about not having looked is not a caveat. The search was made on 2026-08-10 and its record, including what could not be reached from the working environment, is in [`prmt5-ccs-preprint-publication-status-2026-08-10.json`](../literature/prmt5-ccs-preprint-publication-status-2026-08-10.json) |
| Reference 16 of the previous draft, "Biology. *Sarcoma* 2001;5(S1):S37-43", carrying no author list | removed from the reference list; the junctions it corroborated are independently sourced by [14] and [15] | §2.6, §9 | A reference whose title is one word and whose retrieval record carries no author list, cited among the sources for figure 5. It was never a sole source for any junction, so removing it costs no evidence |
| *PRMT5* EMC-minus-comparator of +0.266 and +0.744 SD | +0.263 and +0.816 SD, and now reported as log2 differences with intervals | §3.5 | The values had drifted from [`emc-expression-panels.json`](../modalities/emc-expression-panels.json), which is their one home. Checked 2026-08-09 against the committed artifact; the second differs by 0.07 SD and the reading is unchanged in direction or size class |
| The methylosome **group** *t* (3.11, 3.89) quoted as the statistic the fusion rationale rests on | the gene's own *t* (6.24, 6.67), with the group figures retained in §3.1 as the group figures they are | §3.1 and §3.5 | The group score is not the unit the rationale depends on. The group figures are not withdrawn; they were the wrong ones to lead with. ⚠ §2.7 now records that this change was made after the figures were seen, which is what decides the family in §3.5 |
| Locus gene values of *MTAP* −0.023 / −0.389; *CDKN2A* −0.399 / +0.173; *CDKN2B* −0.096 | +0.053 / −0.607; −0.481 / +0.175; −0.136, now reported as log2 differences with intervals in Table 2 | §3.2 | Cause not established, and an earlier explanation was wrong. *Superseded, retained: "a re-fetch ran on a NARROWER probe-to-symbol bridge (0.931 against 0.984), and a narrower bridge changes which probes map."* Checked against every committed version of the artifact, *MTAP* reads +0.053 in all of them, at bridge rates 0.984, 0.931 and 0.981, and always on one mapped probe. Bridge width does not move this gene. The −0.023 appears in no committed artifact, so it entered the prose from a source the repository cannot show |
| "across 176 sarcoma cell lines" | "across the 91 screened sarcoma cell lines" | §3.3 and the abstract | A real error, in the direction that overstated the evidence base, and it was in four places including the abstract. The release lists 176 sarcoma models; only 91 carry CRISPR gene-effect data. The percentages themselves are unchanged, having always been computed on the screened subset, but they were attributed to a denominator almost twice its true size |
| "family-wise adjusted *p* at least 0.21 and 0.24" | 0.21 and 0.24, with §3.5 carrying the lower-bound explanation | the abstract | The measured value is 0.2081, so "at least 0.21" claimed marginally more than was measured. Inside the Monte-Carlo standard error and material to nothing, but "at least" invites the check |
| "Every statistic, percentile, count and dependency figure reported here was checked against the committed artifact that owns it" | §2.7's account of what was checked, what that check cannot detect, and what it missed | §2.6 of the previous draft, now §2.7 | ⛔ Falsified twice. The universal claim was rewritten once, in a way that moved the quantifier without weakening it, and the appendix then recorded that it had been weakened. Both the sentence and the appendix row describing it were wrong, in the section whose subject is the paper's trustworthiness |
| The paper's own framing as a repository memo, with per-section warning banners and a five-figure inventory in the front matter | a journal Research Article in IMRaD form, with the warnings folded into the abstract's scope statement, section 4.4 and this appendix | throughout | The register was correct for a maintainer and wrong for a journal reader. Nothing measured was removed; the honest statements the pre-posting checklist requires to survive are all present in sections 3.2, 3.3, 3.5, 3.6, 3.7, 4.1 and 4.4 |
