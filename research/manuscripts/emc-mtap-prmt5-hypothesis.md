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
differentiation, and it is classified as a mesenchymal tumour of uncertain differentiation rather
than as a conventional chondrosarcoma; some tumours show areas of chondroid metaplasia [1]. That
distinction bears on every comparator arm used below, none of which is cartilage-lineage either.
The most recent comprehensive review of the disease states that no clinically validated agent
directly targets NR4A3, and reports pazopanib with an objective response rate of 18% and a median
progression-free survival of 19 months (NCT02066285) [1]. A modality census carried out for this
work, and deposited with it as an unpublished supporting analysis, counts eight classes in clinical
use for this disease of which two are local therapies; only the antiangiogenic class carries a
meaningful systemic response record. Mitotic activity in this tumour is usually low [1], which is
the pre-specified basis of the cellularity control reported in section 3.6. Both rationales examined
here act elsewhere: one on transcription, one on a metabolic state.

### 1.2 Two rationales for the PRMT5 methylosome

The first rationale runs through the fusion, and the two reports it transfers from must be described
precisely, because what each shows is narrower than the transfer needs.

A study of clear cell sarcoma identifies PRMT5 as "a new EWSR1-ATF1 binding co-activator to
stimulate its transcription activity" [2]. The evidence is interactome proteomics, a Flag
co-immunoprecipitation of an EWSR1(2-325)-ATF1(66-271) construct in HEK293T cells in which PRMT5 was
detected in the anti-Flag immunoprecipitate, chromatin immunoprecipitation in the clear cell line
DTC-1 showing that the CRE site of the c-Fos promoter is occupied by PRMT5 as well as by CREB1, and
shPRMT5 reducing c-Fos transcript and CRE reporter activity. That report does not show that the
fusion protein is methylated, and it contains no domain-mapping experiment localising the
interaction to the EWSR1 portion. In the same co-immunoprecipitation CREB1 was detected, which the
authors attribute to heterodimerisation through the ATF1 bZIP domain retained in the fusion, so an
equally documented route into the complex runs through the half that EWSR1::NR4A3 does not share.
Of the three PRMT5 inhibitors that report tested, only one was potent, and section 4.2 sets out why
the mechanistic class matters to any experiment built on it. The statements attributed to [2] here
were read from its preprint full text; section 4.4 records what could and could not be confirmed
about the published version.

A second disease reports a fusion-dependent requirement. In Ewing sarcoma, PRMT5 and PRMT1
inhibitors cause growth arrest and apoptosis, and the effect of single-agent GSK591 was "largely
supressed [sic] by partial depletion of EWSR1::FLI1" [3]. The design behind that sentence is one
engineered line, A673-tetON-shEWSR1::FLI1, chosen because it "enables controllable suppression of
the oncogenic fusion without a major compromise in cell viability"; the depletion is partial and the
readout is viable cell number at four days. A partially fusion-depleted line proliferates more
slowly, and the measurable effect of an antiproliferative agent shrinks with it, which is the same
confound section 3.3 raises against the transfer generally. That report's own proposed mechanism is
also disease-specific: it attributes PRMT5 dependence to the replication-stress response buffering
"EWS-FLI1-dependent promotion of CDK9-mediated RNA Polymerase II activation", and notes that the
fusion protein sequesters BRCA1, with the consequence in the same figure that "olaparib was only
effective in reducing the survival of A673 cells when EWS-FLI1 was expressed". Both are properties
of the ETS half and of Ewing biology rather than of the EWSR1 N-terminus the two diseases share, and
because a PARP inhibitor alone was fusion-dependent in the same system, fusion dependence there is
shared by replication-stress agents generally. The same report cuts against the rationale in a
further respect: PRMT5, PRMT1 and MEP50 read higher across multiple sarcoma types than in breast and
lung cancer, and depleting EWSR1::FLI1 did not change PRMT transcript levels, so an elevated PRMT5
transcript is not a read-out of the fusion.

The second rationale runs through a genetic selection window rather than through the fusion. Two
2016 reports established it independently: an integration of genomic profiling with functional
dependency data found that "loss of the enzyme methylthioadenosine phosphorylase (MTAP) confers a
selective dependence on protein arginine methyltransferase 5 (PRMT5) and its binding partner WDR77"
[4], and a short-hairpin screen identified MAT2A and PRMT5 "as vulnerable enzymes in cells with MTAP
deletion" [5]. The mechanism both describe is metabolic rather than genetic: the MTAP substrate
methylthioadenosine accumulates when the enzyme is lost and inhibits PRMT5 directly, which is why
the class the rationale calls for is an MTA-cooperative one. That axis has reached patients with an
MTA-cooperative PRMT5 inhibitor selected on *MTAP* deletion [6]. The sensitivity is comparative. A
differential established in engineered and pan-cancer settings is not a therapeutic window in a
patient, and none is claimed here. The window also has a known asymmetry that this work uses as its
test: *MTAP* is lost through its proximity to *CDKN2A* [4,5], so *MTAP* loss implies *CDKN2A* loss
while *CDKN2A* loss does not imply *MTAP* loss [7]. The two genes sit about 100 kb apart on 9p21, so
a homozygous deletion removing one removes the other, and a three-gene locus score can fall on a
*CDKN2A* event alone.

The two rationales call for different agent classes, which is not always stated. An MTA-cooperative
inhibitor of the class [6] describes depends on MTA accumulation in *MTAP*-deleted cells and is the
wrong tool in an *MTAP*-intact model; the fusion rationale calls for a first-generation compound,
and [2] found that the choice within that generation changed the answer.

Reference [3] raises both of these rationales for its own disease, proposing that "the fusion itself
could potentially serve as predictive biomarker for responses to first-generation PRMT5 inhibitors"
and noting that "12% of patients have CDKN2A deletion, an event that often leads to co-deletion of
MTAP". The structure of the present work is a transposition of that discussion to a different
disease, and is stated as such.

The methylosome is read as a unit rather than as PRMT5 alone because MEP50 (WDR77) is required for
PRMT5-catalysed activity and binds substrate independently [8].

### 1.3 Absence of the question from the published record

A modality census of this disease completed on 2026-08-09 enumerated 217 categories of cancer
treatment and found that classes selected by a molecular state had been dismissed as a group,
largely because the biomarker had never been read. A corpus of 591 open-access full texts retrieved
for this work contains no *MTAP*, *PRMT5* or *MAT2A* datum for this histology; its four incidental
mentions of the histology are diagnostic-pathology asides. That corpus was retrieved on a
target-side query, so a report of PRMT5 in this histology that mentioned neither *MTAP* nor
synthetic lethality would not be in it.

A separate Europe PMC prior-art screen of 322 records, 238 of them with full text, returned one hit
on the pairing of this histology with either target: a 2007 review of chondrosarcomas that names
methylthioadenosine phosphorylase among therapeutic targets "validated by translational research" in
that disease, while treating EMC as a distinct fusion-defined entity [9]. That review concerns the
parent histology, conventional chondrosarcoma, and predates the *MTAP*-deletion and PRMT5
synthetic-lethality literature entirely, so it speaks to the target's standing in chondrosarcoma
broadly rather than in this histology. That screen matched titles and abstracts rather than full
text. Neither screen is therefore a full-text search from the disease side to the target side, and
the claim made here is correspondingly narrow: nothing indexed pairs the PRMT5 methylosome with
extraskeletal myxoid chondrosarcoma, which is a statement about what is indexed on a pairing and not
about what has been done. A result inside a supplementary table of a larger paper would be invisible
to both screens. The census and the two screens are the author's own unpublished analyses and are
deposited with the manuscript rather than cited as literature.

One candidate counterexample sits inside reference [3] and was resolved as far as public description
allows. Its pan-sarcoma comparison uses an expression panel it describes as "Filion (n=137; 7
different fusion positive sarcoma subtypes including n=24 EWSR1-FLI1 and n=4 EWSR1-ERG)" on
Affymetrix U133A. The study of that name profiled three EWSR1::NR4A3-positive EMC tumours on U133A
against 137 samples of five other sarcoma types, comprising 28 Ewing sarcomas, 23 alveolar
rhabdomyosarcomas, 28 desmoplastic small round cell tumours, 12 alveolar soft part sarcomas and 46
synovial sarcomas [10]. The 137 in [3] therefore matches the comparison set that excludes the EMC
cases, and its Ewing split of 24 plus 4 reconciles with the 28 in [10], so EMC is very probably not
in the panel. That is a reconciliation of two published descriptions rather than an inspection of
the deposited dataset, which was not reachable here.

---

## 2. Materials and methods

### 2.1 Expression series, sample classification and per-gene scoring

Two public archival series contain this histology and are the only publicly deposited EMC expression
data a GEO search of six committed queries returned. Reference [10] profiled three further EMC
tumours, but no corresponding deposit was returned by that search and its own comparison set is
recorded as unpublished data, so it could not be re-analysed here. Neither GEO record of the two
analysed series links a publication.

**Table 1.** The two series.

| series | deposited title | platform | measurement | EMC | comparator arm | reference channel |
|---|---|---|---|---:|---|---|
| GSE24369 | Gene expression profiling of low-grade fibromyxoid sarcoma (LGFMS) | GPL6244 | single-channel log2 intensity | 6 | 17 low-grade fibromyxoid sarcoma, 6 desmoid fibromatosis, 6 myxofibrosarcoma | not applicable |
| GSE4303 | Gene expression profile of extraskeletal myxoid chondrosarcoma | GPL3290 | two-colour log2 ratio | 10 | 3 dermatofibrosarcoma protuberans, 3 gastrointestinal stromal tumour | EMC against `CRH-mRNA`, DFSP against `CRH`, GIST against `UHR` |

What each series is matters to what it can support, and the first is not an EMC study. GSE24369's
deposited summary reads "Analysis of gene expression in 17 low-grade fibromyxoid sarcoma (LGFMS)
samples compared to that of histologically similar tumors… The results identifies a LGFMS-specific
gene expression profile". Its six EMC cases were therefore assembled as morphological mimics of
another entity rather than as a consecutive or representative EMC series, and the 17-sample class
used here as a FET-fusion control is that study's index arm. The summary deposited with GSE4303
describes profiling of ten EMC and 26 other sarcomas on 42,000-spot cDNA microarrays, which
corresponds to the published study of that series [11]. Neither deposit records whether *NR4A3*
rearrangement was confirmed in any case, and EMC's differential diagnosis includes the myxoid
tumours in the comparator arm of the first series, so the *NR4A3* instrument control of section 3.5
is the only evidence available here bearing on the diagnoses. Nothing in the record establishes that
the six EMC tumours of one series and the ten of the other are different patients or different
centres, and no overlap check is possible from the deposits; the same is true of the 20 samples
GSE4303 carries on its other platform. One GPL3290 sample is titled `STT2528(2)-Myxoid
Chondrosarcoma`, and the parenthetical is unexplained in the deposited annotation.

Samples were assigned to EMC or to a comparator class by pattern-matching the verbatim GEO
annotation, in a step separate from the data fetch so that every assignment is auditable against the
text that produced it. GSE24369 deposits 42 samples and 35 were analysed. Two pooled skeletal-muscle
RNA samples were excluded by design, since a comparator arm of tumours should not contain normal
tissue. Five solitary fibrous tumours were excluded because the classifier carried no pattern for
that histology and they fell through to an unclassified bucket: that exclusion was accidental rather
than designed, it is reported here for that reason, and section 3.4 and the supplement give both its
effect on the figure and its effect on the primary contrasts. GSE4303 deposits 36 samples across two
platforms, of which the 16 on GPL3290 are analysed here.

GPL3290 carries a confound that cannot be removed by analysis, and section 3.6 and section 4.4
report what follows from it. On that platform disease class coincides with three other strata at
once. The three histologies occupy three disjoint GEO accession blocks, GSM89883 to GSM89924 for
DFSP, GSM91381 to GSM91405 for GIST and GSM98495 to GSM98513 for EMC, so class is collinear with
submission block. Each class carries its own two-colour reference pool, so class is collinear with
the denominator of every value; whether `CRH` and `CRH-mRNA` name one pool or two is not stated in
the deposit, so the DFSP comparators are described here as matched by label rather than as
identical. All ten EMC tumours and only 6 of that deposit's 26 comparator sarcomas were assigned to
this array, so class is collinear with platform assignment within the source study itself, and how
those six were chosen is not recorded. Array-level covariates track the arms in consequence: the
per-array probe count carrying a value ranges from 23,015 to 41,510 of 43,008 and the per-array
background mean differs by arm, both given per sample in the supplement. A permutation that relabels
these sixteen samples is therefore not exchangeable with respect to any of the four strata.

Each gene's value in each sample was converted to a *z*-score against that array's own probe
distribution: the mean and standard deviation are taken per sample over every probe on that array
carrying a value, mapped or not, so a value is a position within one array rather than a quantity
comparable across platforms or across samples' hybridisation intensities. Each sample also carries
its array percentile. Where more than one probe maps to a symbol, the probes are averaged on the
array's own scale before standardisation. The probe-to-symbol bridge is built from the GEO platform
table's accession column, resolved through a curated dictionary, a UniGene archive and live NCBI
queries in that order; the fraction of distinct accessions resolved was 0.981 on GPL6244 and 0.582
on GPL3290, and the fraction of probes carrying a symbol was 0.711 and 0.633. The number of probes
carrying each reported gene is given in Table 5, because a platform-level mapping rate does not tell
a reader whether a particular gene is trustworthy.

A group score is the mean of its member genes' *z*, contrasted between EMC and the comparator arm by
Welch's *t*. A curated group emits no score unless at least three genes are readable and coverage is
at least 0.5; a group failing either floor is reported as underpowered rather than as a null result.
A gene with no probe mapping is recorded as unreadable and never as unexpressed, which matters below
because one locus gene has no probe on the second platform. Samples with no value for a gene are
dropped from that gene's contrast rather than imputed, and a gene is scored only with at least three
values in each arm. Missingness is not uniform: on GPL6244 every cached gene has a value in every
sample, while on GPL3290 578 of 1,662 (34.8%) have at least one missing value and 51 (3.1%) have an
arm below three.

Every contrast is reported as a difference on the array's own log2 scale with a 95% Welch interval
beside its *t*, because a *t* alone states no magnitude. On GPL6244 that difference is a difference
of log2 intensities and converts to a fold difference. On GPL3290 every value is a log2 ratio to a
reference pool and the arms do not share one, so a difference there is a relative difference between
arms and is not a fold difference in transcript abundance; fold values are given for GPL6244 only.
No variance moderation was applied. At six tumours per arm a raw per-gene variance is unreliable,
and the standard-error percentile of each reported gene within its platform is given in Table 5 so a
reader can see whether a *t* is large because the difference is large or because the standard error
is small.

### 2.2 Per-sample reading of the 9p21 locus

Homozygous 9p21 deletion is present in some tumours and absent in others, so a difference of group
means is mis-specified for it and a family-wise adjusted *p* still more so. Every tumour was
therefore read individually for each locus gene. An EMC tumour is called an *MTAP*-low candidate if
its *MTAP* reading sits below every comparator tumour on the same platform, on both the within-array
*z* and the array percentile. Because *MTAP* loss implies *CDKN2A* loss [7], a candidate carrying a
homozygous deletion must also read low for *CDKN2A*, and a tumour is called deletion-consistent when
it is an *MTAP*-low candidate and its *CDKN2A* sits below the 25th percentile of its own array. That
cut is stated in advance of the count and the count is also reported at the 5th, 10th and 50th
percentiles so it does not rest on one threshold. Two controls have to fail for a candidate to mean
anything, and both are reported: the fraction of each sample's cached genes below the 5th percentile
of its own array, since a globally dim array makes every gene look low, and the reference label of
every sample in the arm, since on a two-colour platform a different reference pool shifts every
ratio. Two further 9p21 genes present in the committed random-symbol cache are read in the same
samples. Frequencies consistent with an observed count of zero are given as one-sided 95% binomial
upper bounds.

### 2.3 Dependency panel

Gene-effect scores come from the DepMap public 24Q4 release, distributed as figshare article
27993248, restricted to sarcoma models; the gene-effect scale is Chronos [12]. The release lists 176
sarcoma models, of which 91 carry CRISPR gene-effect data; every figure here is computed on those
91. A gene is called a dependency in a line at a gene effect below −0.5, and selectivity is the
difference between the mean gene effect outside sarcoma and inside it.

### 2.4 Exact permutation, genome-wide placement and multiplicity correction

Both designs are small enough to enumerate completely, so no normal approximation is used. Every
assignment of the observed *z* values to arms of the observed sizes was evaluated and Welch's *t*
recomputed, giving C(35,6) = 1,623,160 labelings on GPL6244 and C(16,10) = 8,008 on GPL3290. The
two-sided *p* is the fraction with |*t*| at least the observed value, and no random sampling is
used, so the value is exactly reproducible. It is exact under the null of exchangeability, which is
the null that the two arms are draws from one distribution, rather than under a null of equal means.
The arms are not homoscedastic: across the genes scored on each platform, the ratio of within-arm
variances falls outside 0.5 to 2 for 49.5% of genes on GPL6244 and 59.1% on GPL3290, with a median
of 0.90 and 0.77. Where the arms differ in scale, a permuted Welch *t* can reject for that reason.

The permutation is exact for the labelling and says nothing about how many genes were examined. That
question is asked separately by computing the same statistic for every symbol the platform's probes
map to and placing each gene of interest in that distribution: 18,688 symbols were scored on
GPL6244, and 14,404 of the 14,932 carrying a probe on GPL3290. The genome-wide computation runs at
fetch time, when the full probe matrix exists, and re-derives from the raw matrix the statistic the
panel computes from reduced per-gene values by a separate code path; the two agree for every gene
both paths score on both platforms. The two paths do not apply the same minimum arm size: the panel
requires three values per arm and the genome-wide path two, so a gene can carry a genome-wide rank
and no panel contrast, which is the case for one instrument control in section 3.5.

Neither of those procedures corrects for the number of genes examined, so a third does. A
max-statistic permutation correction was run: arm labels are permuted exactly as the single-gene
exact test permutes them, Welch's *t* is recomputed for every gene in the family at every labelling,
and the largest |*t*| across the family is recorded per labelling. A gene's family-wise adjusted *p*
is the fraction of labellings whose maximum reaches its observed |*t*|. On GPL3290 all 8,008
labellings were enumerated, so that correction is exact with respect to the labellings; on GPL6244,
where enumerating 1,623,160 labellings against a family of this size is not affordable, 20,000 were
drawn under a fixed seed and the Monte-Carlo standard error is reported with the value. Under a
labelling that leaves either arm below the panel's three-value floor, a gene contributes |*t*| = 0
rather than leaving the family, so the effective family size varies by labelling and the maximum is
deflated for genes with missing values. That convention biases the adjusted *p* downward.

An adjusted *p* is a property of a family, and the family is a choice. The one used for the values
quoted in section 3.5 is every symbol two committed input caches hold that clears the arm floor:
the genes the panel requested, and a seeded uniform random sample of about 4,000 symbols drawn from
the platform's whole mapped-symbol universe for an unrelated null. The two caches were fetched
separately and were checked to agree value for value on every symbol they share, on identical
samples and identical per-sample backgrounds, before they were merged. Together they hold 5,449
symbols on GPL6244 and 5,216 on GPL3290; on the second platform 368 fail the arm floor, so the
families are 5,449 and 4,848, against mapped-symbol universes of 18,724 and 14,932. Because each
family is a subset of the array, and because adding symbols can only raise the permuted maximum,
every adjusted *p* reported here is a lower bound on the value the full array would give. Three
other defensible families give values spanning three orders of magnitude, and all four are reported
in section 3.5 with the reason for choosing the array-wide one.

The two universes just quoted are not the same resolution of the platform table. The random half of
the family was drawn from a 2026-08-07 resolution of GPL6244 that maps 18,724 symbols, while the
genome-wide placement scored a 2026-08-09 resolution that maps 18,688; the two also differ on the
probe count mapping to a symbol, 20,235 against 20,221. Reconciling them would need the platform
table re-fetched. The 0.2% difference moves no adjusted *p*, and the merge is refused unless the two
caches agree on every shared symbol, which they did.

### 2.5 Confound adjustment

A per-sample confound score is the mean *z* of the readable members of a named gene set, provided
the sample carries at least 60% of them. *PRMT5* is then regressed on that score by ordinary least
squares with one covariate and an intercept, and the EMC-versus-comparator contrast recomputed on
the residuals. A contrast is called surviving if it keeps its sign and at least 60% of its
magnitude, a threshold chosen for this work rather than taken from an established convention; raw
and adjusted values are both reported, and the realised fractions are given so a reader can apply a
different threshold. The proliferation score uses twelve genes and scores all 35 and all 16 samples;
the lineage score uses eight and scores 35 and 14. Against the proliferation score *PRMT5* retains
5.23/6.24 = 0.84 of its magnitude on GPL6244 and 2.71/6.67 = 0.41 on GPL3290, so the failure on the
second platform is not marginal.

### 2.6 Substrate-motif map

Occurrences of the motif GRG were counted by exact string scan on committed protein sequences, with
overlaps included, since GRGRG contains two sites and two methylatable arginines and a
non-overlapping scan would halve a poly-RG tract. The motif definition is taken from reference [13],
whose bibliographic record and abstract were retrieved but whose full text is not open access and
was not read, a limit that matters because the motif is the foundation of this section. A fusion's
retained 5′ sites are those at or before the last residue fully encoded by the 5′ partner, excluding
the seam residue, because each of these junctions splits a codon.

Breakpoints are transcript exon boundaries, and this work has no EMC cohort of its own. The
*NR4A3*-fusion junctions are the ones reported in [14], [15] and [16], each recorded in the source
artifact with the verbatim sentence it was taken from: EWSR1 exon 12 to *NR4A3* exon 3 (type 1),
exon 7 to exon 2 (type 2), exon 13 to exon 3 (type 5), and TAF15 exon 6 to *NR4A3* exon 3. The type
5 and TAF15 junctions each carry a further corroborating record in the source artifact, and no
junction rests on a single source. The EWSR1::ATF1 and EWSR1::FLI1 junctions used as comparators
carry an exon number and a cumulative coding position in the same artifact but no separate published
quotation, and are reported on that footing. Two double-entry checks are run against artifacts that
predate this analysis: each re-derived RG count against the counts those artifacts already held, and
each fusion's own RG count against the sum of its retained 5′ half and NR4A3's contribution.

### 2.7 Reproduction and AI assistance

Every figure, table and number is regenerable from public data by scripts in the accompanying public
repository, `github.com/trimcrae/Rare-cancers`, and section 8 names the artifact that owns each
value; an archived release of the state this manuscript is built on will be deposited at submission.
Analysis, figures and drafting were carried out with substantial assistance from an AI coding agent
operating on a version-controlled repository under my direction, using Anthropic Claude. The agent
is not an author and cannot be one, and I take responsibility for the content. The analysis is
written in Python 3.11, using only the standard library for the fetch, the scoring, the group
statistics and the exact permutation, and NumPy for the max-statistic permutation of section 2.4;
figures are drawn with Matplotlib. No statistical package supplies the tests: Welch's *t*, its
Satterthwaite degrees of freedom and both permutation procedures are implemented directly, which is
what makes exact enumeration possible at these sample sizes.

What was checked, and how, should be stated at the strength it holds. I re-derived each statistic,
percentile, count and dependency figure in this manuscript against the committed artifact that owns
it, value by value, and where a value could not be reconciled it was corrected and the superseded
value registered in the appendix, which includes one Methods count that traced to no artifact at
all. A per-value check of that kind cannot detect a quantity reported correctly in two places at two
different values, and one such quantity is disclosed in section 2.4; the appendix records what the
check missed as well as what it caught. I also read each cited source against its committed verbatim
record, and rewrote the descriptions of the clear cell report, the Ewing report and the EMC-models
paper where the manuscript had described them more favourably than they read. Every bibliographic
identifier below was taken from a retrieval record and is checked against a tracked artifact by an
automated linter; that check establishes that an identifier came from a retrieval rather than from
recollection, and it does not establish that a citation is apt.

The reads, thresholds and controls of the expression panel were specified before the corresponding
data were retrieved, and what was pre-specified is narrower than this paper's subject. The
pre-specified read asks whether the *MTAP* locus is deleted in EMC and records the direction that
would support it as *MTAP* down in EMC, at the floor, together with *CDKN2A*. No directional
expectation is recorded anywhere for *PRMT5*, which entered the panel as the enzyme that *MTAP* loss
would sensitise. The choice to state the fusion rationale on *PRMT5* rather than on the four-gene
group was made after the figures were seen, and is registered as a correction in the appendix. This
read is one of eighteen numbered reads run on the same fetch of the same 16 EMC tumours. Both facts
bear on section 3.5: a gene selected after a curated panel and a genome-wide scan were examined is a
gene for which the array-wide family is the right correction, and that is why the array-wide family
is the one whose value is quoted. The two documents together report about 110 quantities of which 15 are
corrected, being nine genes on GPL6244 and six on GPL3290, tabulated in full in the supplement;
every other value in them is uncorrected and is labelled as such where it carries a claim.

---

## 3. Results

### 3.1 Group-level readings

The PRMT5 methylosome group reads higher in EMC than in the comparator arm on both platforms
(*t* = 3.11 and 3.89), and the methionine-salvage context group likewise (*t* = 4.26 and 2.07).
Neither is corrected for the number of genes examined.
*MAT2A* sits at the 99th percentile of its array on GPL6244 and *PRMT5* at the 91st.
The corresponding GPL3290 figures, the 84th and the 59th,
are percentiles of a distribution of log-ratios against a reference pool and carry no absolute
meaning: on that platform only the between-group contrast is interpretable.

Scored as *MTAP* plus *CDKN2A* plus *CDKN2B*, the locus reads lower in EMC on GPL6244 with all three
genes readable, *t* = −4.06. On GPL3290 only two of three are readable, which falls below the
panel's three-gene minimum although its coverage of 0.667 clears the 0.5 floor, so no score is
emitted; that is an instrument limit rather than a reading of the biology.

![Figure 1](./figures/mtap-prmt5-fig1-readings.png)

**Figure 1.** Every tumour in the analysed arms, on both platforms. Per-sample *z* against each
array's own probe distribution; bars are medians. The five solitary fibrous tumours GSE24369
deposits are not in the analysed arms and appear in Figure 4; see section 2.1. The two platforms are
not placed on a shared axis, because one is single-channel intensity and the other a two-colour
log-ratio. A gene with no probe is marked unreadable, which records a missing measurement and not an
absence of expression.

An elevated methylosome is consistent with the fusion rationale without being evidence for it, since
abundance is not dependency, and PRMT5, PRMT1 and MEP50 read higher across multiple sarcoma types
than in breast and lung cancer [3]. The low locus group score is likewise consistent with the *MTAP*
rationale without supporting it, for the reason developed in section 3.2.

### 3.2 The locus, gene by gene and tumour by tumour

Read gene by gene, the locus does not support selection on *MTAP*, and the two platforms disagree
about which gene moves.

**Table 2.** The three locus genes. Differences are on each array's own log2 scale with a 95% Welch
interval; the fold column applies to GPL6244 only, for the reason in section 2.1.

| gene | GPL6244 difference (95% CI) | fold | GPL6244 *t* | GPL3290 difference (95% CI) | GPL3290 *t* | array percentile, EMC | genome-wide rank of \|*t*\| |
|---|---|---:|---:|---|---:|---|---|
| *MTAP* | +0.121 (−0.223, +0.465) | 1.09 | +0.69 | −1.377 (−2.244, −0.510) | −2.27 | 72nd / 13th | top 74% / top 26% |
| *CDKN2A* | −0.923 (−1.292, −0.555) | 0.53 | −5.40 | +0.090 (−0.403, +0.583) | +1.33 | 53rd / 71st | top 3.5% / top 49% |
| *CDKN2B* | −0.254 (−0.556, +0.049) | 0.84 | −2.03 | unreadable | not applicable | 57th / not applicable | top 34% / not applicable |

The pre-specified criterion for this rationale is a conjunction, being *MTAP* down at the floor
together with *CDKN2A*, and neither platform satisfies it. On the 35-tumour platform *CDKN2A* is
lower in EMC and *MTAP* is flat, at 1.09-fold with an interval spanning 0.86 to 1.38. On the
16-tumour platform *MTAP* is lower, in the direction the rationale predicts, and *CDKN2A* is not.
The failure of that conjunction is the reason the rationale is not supported here. It claims less
than the corrected statistics appear to license, and it is the claim that holds: *MTAP* is at a
multiplicity-adjusted *p* of 1.00 on both platforms, but that is a failure to reject rather than a
measurement that anything is absent. The same procedure assigns 0.85 to *NR4A3* on GPL6244, the
transcript the fusion defining this disease places under a new promoter, so it cannot be read as
stating a negative about any gene.

Neither is a difference of group means the right instrument. Homozygous 9p21 deletion is a subset
event, and a mean test has little power against a minority of tumours: the smallest difference this
design would detect in 80% of repetitions against an uncorrected two-sided 0.05 is 1.48-fold for
*MTAP* on GPL6244 and 2.59-fold on GPL3290, before any correction for multiplicity. Every tumour was
therefore read individually.

**Table 3.** The five EMC tumours on GPL3290 whose *MTAP* reading falls below every comparator, with
*CDKN2A* in the same samples. Percentiles are within each sample's own array. The lowest comparator
sits at the 11.0th percentile for *MTAP* and the 56.7th for *CDKN2A*.

| sample | *MTAP* percentile | *MTAP* *z* | *CDKN2A* percentile | *CDKN2A* *z* |
|---|---:|---:|---:|---:|
| GSM98511 | 1.1 | −2.79 | 89.3 | +1.08 |
| GSM98506 | 4.0 | −1.85 | 68.3 | +0.35 |
| GSM98503 | 4.6 | −1.65 | 73.2 | +0.48 |
| GSM98510 | 5.5 | −1.60 | 86.5 | +0.96 |
| GSM98499 | 10.4 | −1.21 | 50.5 | +0.09 |

Five of the ten EMC tumours on GPL3290 read below every comparator for *MTAP*, which no group
statistic can see and which the group mean on that platform understates. Not one of them reads low
for *CDKN2A*. All five sit at or above the median of their own array for *CDKN2A*, and the tumour
with the lowest *MTAP* reading in the series carries the highest *CDKN2A* in the arm. No tumour on
either platform is deletion-consistent at the 25th-percentile cut, and none at the 5th, 10th or 50th
either. Within the EMC arm the rank association between the two genes is negative, at Spearman
*rho* = −0.31 with an exact two-sided *p* of 0.39 over all 3,628,800 rank permutations, which is the
opposite sign to co-deletion and is not itself significant. Two 9p21 genes present in the committed
random-symbol cache read the same way in those five samples: *MIR31HG* between the 29th and 56th
percentiles against a comparator range of 30th to 67th, and *MLLT3* between the 63rd and 91st
against a comparator range of 5th to 74th.

Two explanations for a low *MTAP* tail other than deletion were tested and neither holds. It is not
array quality: those five samples carry between 3.8% and 7.6% of their cached genes below the 5th
percentile of their own arrays, inside a cohort range of 1.4% to 8.9%. It is not the reference
channel: all ten EMC tumours share one reference label, so a split within the EMC arm cannot come
from the denominator of the measurement. On GPL6244 no EMC tumour is an *MTAP* low outlier at all,
every one sitting between the 67th and 82nd percentiles of its own array and above the array mean.

![Figure 2](./figures/mtap-prmt5-fig2-locus-genewise.png)

**Figure 2.** The locus read per tumour. Filled circles are EMC tumours and open squares comparator
sarcomas; bars are medians, while Table 2 reports differences of means, so the two need not agree in
direction for a gene as flat as *MTAP*. The left panel shows all three genes on GPL6244, the
platform on which all three are readable and on which the locus group score is emitted: *MTAP* is
flat and *CDKN2A* carries what signal that score has. The right panel plots *MTAP* against *CDKN2A*
per tumour on GPL3290, where a homozygous 9p21 deletion would place a tumour low on both. Five EMC
tumours sit below every comparator for *MTAP*, and all five carry *CDKN2A* above their arrays'
median, which is the opposite of the co-deletion pattern; no tumour on either platform falls in the
lower-left quadrant.

Zero deletion-consistent tumours in sixteen bounds the frequency of such a tumour in this disease at
17% with 95% confidence, and at 39% for the six-tumour platform alone, against a survey in which
MTAP protein loss reaches up to 20% in various sarcomas without naming this histology [17]. The
rationale is therefore not supported and is not closed: sixteen archival tumours bound it loosely, a
transcript is not a copy number, and *MTAP* protein can be lost by mechanisms that leave the gene
present. Only MTAP protein can settle the question, and the test proposed in section 4.2 is
accordingly a stain.

### 3.3 The sarcoma dependency prior

Across the 91 screened sarcoma cell lines, PRMT5 and MAT2A are dependencies in 94.5% and 96.7%
respectively. MTAP is not a dependency in any of them, which is the expected profile for a biomarker
rather than a target. That is consistent with the panel being read correctly, and it is weaker than
a positive control, since a gene can be a non-dependency for reasons that have nothing to do with
the instrument.

This weakens the specificity of the proliferation half of the transferred result, and the same table
weakens it further. PRMT5 is a dependency in 94.1% of the non-sarcoma lines of the release as well,
giving a sarcoma selectivity of 0.013 on a gene-effect scale where MAT2A reads −0.285; on this panel
PRMT5 is not distinguishable from a pan-essential gene, in sarcoma or outside it. Silencing PRMT5
impairs proliferation in nearly every line, so a growth effect in EMC would be close to expected;
the part that could be specific to this disease, and the part any transfer must rest on, is the
effect on fusion-driven transcription rather than on growth.

It does not refute the class. The therapeutic argument for the *MTAP*-selected axis is a
differential between *MTAP*-deleted and *MTAP*-intact cells, and a gene-effect score cannot express
a differential of that kind, since an MTA-cooperative inhibitor exploits a metabolic state rather
than the raw dependency [6]. A near-universal dependency and a genetic window are compatible.

![Figure 3](./figures/mtap-prmt5-fig3-dependency-qualifier.png)

**Figure 3.** The dependency prior, inside and outside sarcoma, with Wilson 95% intervals. PRMT5 and
MAT2A are dependencies in almost every sarcoma line and in almost every non-sarcoma line, so a
growth effect on silencing them is close to expected and the panel supports no statement of tissue
selectivity; only an effect on fusion-driven transcription would be specific to this disease. MTAP
is not a dependency in either group. The panel contains no EMC line, so every value is a transfer
from other sarcomas.

No EMC cell line carrying the fusion appears in any public dependency dataset, so this prior is a
transfer from other sarcomas, limited by the complete absence of an EMC observation rather than by
sample size.

### 3.4 Comparator classes, pooled group against single gene

![Figure 4](./figures/mtap-prmt5-fig4-comparator-classes.png)

**Figure 4.** Pooled group against single gene, for every class GSE24369 deposits. One comparator
class, low-grade fibromyxoid sarcoma, is FUS::CREB3L2 and therefore a FET-fusion control on whether
the reading is simply what a fusion sarcoma looks like. Solitary fibrous tumour is drawn although it
is not in the comparator arm, because it is deposited in the series and was excluded only by the
classifier's want of a pattern for it (section 2.1); the two pooled skeletal-muscle samples are
normal tissue, are marked as not a comparator, and read higher than EMC on *PRMT5*. Pooled across
the four methylosome genes, EMC ranks third of the five tumour classes, below desmoid fibromatosis
and solitary fibrous tumour, so the group does not separate this disease. On *PRMT5* alone EMC has
the highest class median, +1.30 against +1.05, +1.05, +1.04 and +0.94. Left-panel axis labels give
the number of gene-by-sample values, which is the class's sample count times four genes; left-panel
points are therefore not independent observations and no test is run on them.

The single-gene comparison can be tested and was not previously. Exact permutation of the class
means places EMC above low-grade fibromyxoid sarcoma at *p* = 0.00004, above solitary fibrous
tumour at 0.0087, above desmoid fibromatosis at 0.0065 and above myxofibrosarcoma at 0.0152; under
a Bonferroni correction for the four comparator classes the first three clear 0.05 and the fourth
does not. None of those values carries any correction for the number of genes on the array, so they
do not bear on section 3.5. The word that fits the sample-level picture is weaker than separation:
9 of the 34 comparator tumour samples read at or above the lowest EMC tumour, and one of the two
pooled normal-muscle arrays reads above the EMC median.

For the locus, a group score reported a signal that its decisive gene did not have; for the
methylosome, a group score hid a signal that its decisive gene does have. Neither is visible without
reading the constituent genes, so a curated group score is treated here as a summary and not as a
unit of evidence.

### 3.5 PRMT5's statistic and the family behind its correction

*PRMT5* alone, the gene the fusion rationale depends on, reads *t* = 6.24 on GPL6244 and 6.67 on
GPL3290. On GPL6244 that is a difference of +0.544 log2 intensity units (95% CI +0.375 to +0.713),
or 1.46-fold; on GPL3290 it is +1.094 in log-ratio units (95% CI +0.688 to +1.499).

**Table 4.** The exact permutation of the labelling.

| platform | *PRMT5 t* | labelings enumerated | at least as extreme | exact two-sided *p* |
|---|---:|---:|---:|---:|
| GSE24369 / GPL6244 | +6.24 | 1,623,160 | 230 | 0.000142 |
| GSE4303 / GPL3290 | +6.67 | 8,008 | 1 | 0.000125 |

On GPL3290 the exact *p* cannot fall below 1/8,008 whatever the effect size: with 10 versus 6
tumours the resolution of the test is the sample size rather than the biology. Both values are exact
under exchangeability, which section 2.4 shows the arms do not satisfy.

Placing each gene of interest against every gene on its own array gives the following, with the
multiplicity-adjusted *p* of section 2.4 beside it and two instrument controls: *NR4A3*, the
disease-defining fusion transcript, and *ENO3*, a published direct target of an NR4A3 fusion [18].

**Table 5.** Genome-wide placement and multiplicity-adjusted *p*, with the number of probes carrying
each gene and its standard-error percentile among the genes scored on that platform.

| gene | probes, GPL6244 / GPL3290 | SE percentile, GPL6244 / GPL3290 | GPL6244: *t*, rank of \|*t*\|, adjusted *p* | GPL3290: *t*, rank of \|*t*\|, adjusted *p* |
|---|---|---|---|---|
| *PRMT5* | 1 / 1 | 11th / 4th | +6.24, top 1.9%, 0.21 | +6.67, top 1.0%, 0.24 |
| *MAT2A* | 1 / 1 | 45th / 13th | +4.13, top 8.5%, 0.98 | +4.10, top 6.3%, 0.97 |
| *WDR77* | 1 / none | 7th / not applicable | +2.82, top 20.5%, 1.00 | unreadable |
| *MTAP* | 1 / 2 | 44th / 37th | +0.69, top 74.0%, 1.00 | −2.27, top 26.1%, 1.00 |
| *CDKN2A* | 1 / 1 | 49th / 9th | −5.40, top 3.5%, 0.51 | +1.33, top 49.3%, 1.00 |
| *NR4A3* (control) | 1 / 1 | 74th / 23rd | +4.66, top 5.9%, 0.85 | +1.70, top 38.5%; *n* = 9 versus 2 |
| *ENO3* (control) | 1 / 1 | 85th / 54th | +3.61, top 12.0%, 1.00 | +13.22, top 0.05%, 0.010 |

Every primary reading in this paper rests on a single probe, and on GPL3290 that probe's gene
assignment runs through a bridge resolving 58.2% of accessions on an array of expressed-sequence
tags. No cross-probe agreement check is available for *PRMT5* on either platform and none is
possible. The standard-error column carries the pattern behind *PRMT5*'s *t*: its standard error
sits in the bottom tenth of genes scored on GPL6244 and the bottom twentieth on GPL3290, while
*ENO3*, whose difference is three times larger on GPL6244, has a smaller *t*. *PRMT5*'s *t* is large
because its within-arm variance is small, not because the difference between arms is large.

The adjusted values are lower bounds, for the reason section 2.4 gives, and the GPL6244 column
carries a Monte-Carlo standard error of about 0.003. On this correction only *ENO3* on GPL3290 falls
below 0.05, on a family that is a third of that array; the primary contrast does not clear
conventional thresholds on either platform.

The value of that adjusted *p* is decided by the family, and the family is a choice. Recomputed on
the same labellings and the same reduction, varying only which symbols are in the family:

**Table 6.** *PRMT5*'s family-wise adjusted *p* over four families.

| family | genes, GPL6244 / GPL3290 | adjusted *p*, GPL6244 | GPL3290 |
|---|---|---:|---:|
| the genes this paper reports (Table 5 plus *MKI67*) | 9 / 6 | 0.00015 | 0.000125 |
| the curated panel cache | 1,857 / 1,611 | 0.097 | 0.064 |
| the merged array-wide family, as used above | 5,449 / 4,848 | 0.208 | 0.238 |
| the same family restricted to genes measured in every sample | 5,449 / 3,126 | 0.208 | 0.031 |

Quoting one point from that range without naming the family would be uninterpretable. The
array-wide family is the one whose value is quoted, and the record decides it: section 2.7 records
that the pre-specified endpoint of this read was *MTAP* loss with a stated direction, that no
direction was pre-specified for *PRMT5*, that the statistic was moved from the group to the gene
after the figures were seen, and that this read is one of eighteen run on the same tumours. A gene
arrived at that way is a gene for which the question "how often does a maximum this large arise
across the genes scanned" is the right one, and that question answers 0.21 and 0.24. The fourth row
is reported because it is the largest single sensitivity and it runs the other way: excluding genes
with missing values from the family removes the genes that most often attain the permuted maximum on
GPL3290, and the adjusted *p* falls to 0.031. On that platform the value therefore turns on a
convention as much as on the data.

The two controls do not behave alike, and the second is not the read it appears to be. *ENO3* sits
at the extreme of GPL3290, as a working instrument should show. *NR4A3* is only mid-table there, and
the measured explanation is the sample count: only two of the six comparator samples and nine of the
ten EMC samples carry a value for it on that array, which is below the three-per-arm floor, so the
panel emits no contrast and the +1.70 comes from the genome-wide path with its floor of two. A
comparator arm of two is a sufficient explanation on its own; the pre-specified alternative, carried
in the control block before the data were read, is that on a 3′-biased array the probe can sit in
the region the fusion replaces. GPL3290's ranking should not be read as if every row on it were
equally trustworthy.

A rank is not a corrected *p*, which is why the adjusted column is reported beside it. It controls
no error rate, is computed over a distribution containing real biology rather than a null, and is
inflated in effective sample size by correlation between transcripts. Taken alone it supports only
the narrow statement that on these arrays a *t* of *PRMT5*'s size is uncommon among individual genes
and a *t* of *MTAP*'s size is not. It is not uncommon among the maxima that arise by chance when this
many genes are scanned at this sample size: across labellings of the arms, the largest |*t*| in the
family exceeds 5.4 in half of them, and reaches *PRMT5*'s observed 6.24 in at least a fifth.

### 3.6 Four prespecified controls

Each control was specified against a named weakness before it was run, and each is a control rather
than an additional hypothesis test. None of the values in this section is corrected for multiplicity.

The first asks whether the elevation is *PRMT5* or the PRMT family, which matters because the Ewing
report finds PRMT1 and PRMT5 elevated together across sarcoma types [3]. Eight family members are
readable on GPL6244 and seven on GPL3290, counting *PRMT5* itself, and *PRMT5* ranks first on both.
As a group the family is flat (*t* = 0.33 and 1.34) while *PRMT5* alone reads 6.24 and 6.67. The
separation is incomplete on the second platform, where *CARM1* reads +5.44 and *PRMT3* +3.47, so a
family-wide reading is weakened rather than excluded; only on GPL6244, where the next member is
*PRMT3* at +1.62, is *PRMT5* clearly separated. The same table carries a disanalogy with the disease
the transfer comes from: *PRMT1* is flat in EMC on both platforms, at *t* = 0.18 and 1.36, whereas
[3]'s premise is that PRMT1 and PRMT5 are elevated together in Ewing sarcoma and its largest effect
is the combination of PRMT1 and PRMT5 inhibition rather than either alone.

The second control adjusts for proliferation, and on one platform it takes most of the contrast.

**Table 7.** Confound adjustment.

| axis | platform | score elevated in EMC | *PRMT5 t*, raw to adjusted | reading |
|---|---|---|---:|---|
| proliferation, 12 genes | GPL6244, *n* = 35 | no, *t* = 0.45 | 6.24 to 5.23 | survives |
| proliferation, 12 genes | GPL3290, *n* = 16 | yes, *t* = 3.00 | 6.67 to 2.71 | most of the contrast goes with it |
| chondroid-marker lineage, 8 genes | GPL6244, *n* = 35 | no, *t* = 0.99 | 6.24 to 6.20 | untouched |
| chondroid-marker lineage, 8 genes | GPL3290, *n* = 14 | no, *t* = 0.36 | 6.67 to 6.52 | survives |

The second row weakens the transcript half of the fusion rationale. On GPL3290 the proliferation
score is itself higher in EMC, correlates with *PRMT5* at *r* = 0.60, and adjusting for it takes
*PRMT5* from 6.67 to 2.71; on that platform the reading is consistent with a proliferation effect.
The platforms disagree and neither is clearly preferable. GPL6244 has 35 tumours, a flat
proliferation score and a *PRMT5* contrast that barely moves; GPL3290 has 16, a two-colour
log-ratio measurement, a proliferation score that moves with everything, and the four collinear
strata of section 2.1.

Explanations for that disagreement should be ranked, and the more mundane ones are not biological.
The platforms measure different quantities, which is the general statement. The specific difference
their own annotation records is that half the GPL3290 comparator arm was hybridised against a
different reference pool from every EMC tumour on it, and the other half against a third; in a
two-colour design that changes every ratio systematically, and it applies to the proliferation genes
as much as to *PRMT5*. No reference-matched contrast exists on that platform, because neither
comparator half shares the EMC arm's reference label, so splitting the comparator arm cannot
discriminate the confound: agreement between two halves that are both reference-different from EMC
is uninformative about it. The supplement reports the full split as a description rather than as a
test. The one reference-informative contrast the platform admits is comparator against comparator,
and *PRMT5* reads *t* = +0.24 across it, so the two comparator reference pools do not move this gene
between the two halves. That is mild reassurance and it does not make either half matched to EMC.

The third control tests chondroid markers, and section 1.1 states why its premise needs care. EMC
does not show true cartilaginous differentiation [1], so this is a check against myxoid and
matrix-associated transcription rather than a lineage control, and a null in it is uninformative
rather than reassuring. No comparator in either series is cartilage-lineage. It can ask whether
*PRMT5* and chondroid markers move together within these samples, and they do not (*r* = 0.05 and
−0.04).

The fourth control is a single-gene cellularity reference, specified in advance as approximately
flat because a large proliferation difference would say the contrast was being driven by how much
tumour each sample contains. *MKI67* reads *t* = 0.53 on GPL6244, as expected, and *t* = 2.30 at
+1.24 SD on GPL3290, which is not flat. It therefore passes on one platform and moves on the other,
in the same direction and on the same platform as the twelve-gene proliferation score. The GPL3290
reading is carried by the comparator arm rather than by EMC: both arms sit below their arrays' means,
at mean array percentiles of 15th for EMC and 6th for the comparators, and the comparator arm's *z*
values are −3.88, −3.72, −1.89, −1.62, −1.45 and −0.74, so the contrast is produced by two extreme
comparator arrays. The confound this control fires on may therefore be a comparator measurement
artefact rather than higher proliferation in EMC. It does not survive the multiplicity correction on
either platform (adjusted *p* = 1.00 for both), which for a control expected to be flat is the
uninformative direction.

None of these adjustments can remove a confound that the proxy measures badly. Regressing out a
transcript score removes the part of the contrast the proxy linearly predicts and nothing more, so a
surviving result is a much weaker statement than a failing one.

### 3.7 The substrate motif in the fusion protein

The readings above are measurements on tumours and on cell lines. This section addresses where
PRMT5's reported substrate motif sits in the fusion protein.

Profiling arginine methylation genome-wide after selective PRMT5 inhibition, and validating hits by
in vitro methylation, identifies a preference for "arginine sandwiched between two neighboring
glycines (a Gly-Arg-Gly, or 'GRG,' sequence)" [13]. That is a preference and not a rule: PRMT5
methylates arginines outside GRG, and a GRG site is not necessarily methylated. A mapping experiment
in a different substrate narrows it the same way, since of three DDX5 fragments only the one
carrying the C-terminal RGG/RG motif was methylated by PRMT5, and mutating five arginines inside
that motif abolished it [19]. The EWSR1 protein is itself extensively arginine-methylated [20],
which is what makes the location of the motif in the fusion a question worth computing; that last
reference was verified at title level only.

EWSR1 is 656 residues and carries eleven GRG sites, at residues 301, 303, 316, 320, 463, 489, 564,
574, 591, 602 and 635. The N-terminal segment that every EWSR1 fusion retains is the SYGQ-rich
low-complexity region, and it contains no site. Every site lies beyond residue 300, in the two
RGG-rich regions the fusion truncates. Residue 301 of 656 falls at 46% of the protein, so the sites
are not confined to the C-terminal half; the retained N-terminal segment contains none of them. That
is the observation this section supports, and it holds for the segment the two diseases actually
share.

**Table 8.** Retained 5′ GRG sites by fusion, ordered as Figure 5 plots them.

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

**Figure 5.** The motif, the RGG regions, and where each fusion cuts. EWSR1 is drawn once at full
length with its eleven GRG sites and its two RGG-rich regions; below it, each fusion's retained 5′
segment on the same ruler. Four of the eleven sites lie at residues 301, 303, 316 and 320 and the
fifth at 463, so every breakpoint in the 142-residue window from 321 to 462, which is 22% of the
protein, retains exactly four sites; the shaded band marks that window. Three EMC and three clear
cell junctions fall inside it or below the cluster, and a shared count of four is what the cluster
structure returns for almost any mid-protein breakpoint rather than a correspondence between the two
diseases. EWSR1::FLI1 keeps no site, and it is the fusion in which a PRMT5 requirement has been
shown to be fusion-dependent. TAF15::NR4A3 is tabulated above but not plotted here, because TAF15 is
a different 5′ protein and therefore a different ruler.

An earlier version of this analysis read the shared count of four between the commonest EMC fusion
and the commonest clear cell junction as quantitative support for transferring between the two
diseases. It is not, for a reason that is arithmetic rather than a matter of degree. The
retained-site count is a step function with one large plateau: four sites cluster within twenty
residues and the next lies 143 residues away, so any breakpoint between residues 321 and 462 retains
exactly four. That window spans 142 residues, 21.6% of the protein. EWSR1::NR4A3 type 1 cuts at 431
and EWSR1::ATF1 exon 8 at 324, which are 107 residues apart and both inside it, as is EWSR1::ATF1
exon 10 at 348. Across all eight fusions tabulated the count takes three values, 0, 4 and 5. The
agreement is what the arithmetic returns for most mid-protein cuts, it carries no information about
the two diseases, and it is metric-dependent as well: counted as RG dipeptides on the same
sequences, EWSR1::NR4A3 type 1 retains 8 and EWSR1::ATF1 exon 8 retains 7.

The table does not license a prediction that retained-site count determines response. EWSR1::FLI1
retains no sites, and it is in EWSR1::FLI1 that a PRMT5 inhibitor's effect was shown to be
fusion-dependent [3]. Whatever PRMT5 does in a FET-fusion sarcoma, it does not require the fusion
protein to be the substrate. EMC type 2 and TAF15::NR4A3, which retain none, are therefore not
predicted to be unresponsive; the fusion protein is one candidate substrate among several, and the
others, including wild-type FET proteins, Sm proteins and R-loop-resolution factors [19], carry
their motifs regardless of the breakpoint. Reference [2], on which the clear cell transfer rests,
proposes PRMT5 as a binding co-activator and does not show that the fusion is a substrate at all.

The denominators on both sides are the junctions this analysis holds rather than the reported sets.
Reference [2] records that besides type 1, "6 other types of EWSR1-ATF1 fusion and EWSR1-CREB1 have
also been reported" in clear cell sarcoma, and the three junctions tabulated here are the three
recorded in the source artifact. On the EMC side, FUS::NR4A3 and TCF12::NR4A3 are reported fusions
[1] and are not tabulated; FUS is a FET protein with its own RGG content and is the most informative
missing row.

A motif marks a site at which an enzyme can act. These counts do not show that any NR4A3 fusion is
methylated, that PRMT5 is the enzyme that would methylate it, or that methylation would be
functionally consequential.

---

## 4. Discussion

### 4.1 Status of the two rationales

The 2025 comprehensive review of this disease reaches the same categorical conclusion about the
absence of a targeted agent, and considers neither of the rationales examined here [1]. Read against
the only public data able to address them, neither rationale is supported, and the two fail
differently.

The *MTAP*-locus rationale is not supported, and the reason is a per-sample one. The pre-specified
conjunction, *MTAP* down at the floor together with *CDKN2A*, is satisfied on neither platform, and
the tumour-by-tumour reading that a group mean cannot give is the stronger form of the same
statement: five of ten EMC tumours on one platform do sit below every comparator for *MTAP*, and
none of them carries the *CDKN2A* reading that 9p21 co-deletion requires, with two further 9p21
genes agreeing and both alternative explanations for the tail failing. Zero deletion-consistent
tumours in sixteen is not a demonstration of absence: it bounds the frequency at 17%, against a
class prior in which sarcoma MTAP loss reaches 20% [17]. What the transcript data can say is that
the pattern here is not the pattern this rationale predicts. What it cannot say is that no EMC
tumour has lost MTAP protein, and protein loss is what an MTA-cooperative agent's biology turns on,
so a transcript could not have seen it in any case. What remains of the rationale is a question that
MTAP immunohistochemistry would answer directly.

The fusion rationale fails differently: this data does not support it and cannot test it. *PRMT5*
reads higher in EMC than in the comparator arm on both platforms and ranks first of the readable
PRMT family on both, and after correction for the number of genes examined neither reading clears a
conventional threshold, at 0.21 and 0.24. Three further things stand between the readings and the
rationale. The corrected value is a property of the family and ranges over three orders of magnitude
across defensible families, so no single value carries the argument. On the 16-tumour platform
disease class is collinear with submission block, reference pool and within-study platform
assignment, so its contribution cannot be separated from batch, and no re-analysis removes a
property of the deposit. And the proliferation control disagrees between the platforms, taking most
of the contrast on the smaller one.

Directional concordance between the two deposits is the most that can be claimed for the pair, and
it is less than replication. Both put *PRMT5* first of the readable PRMT family and both put the
contrast in the same direction. But the deposits have not been shown to contain different patients
or different centres, the larger carries no linked publication and is a study of a different disease
in which EMC is one comparison group, and the smaller is confounded as described.

Nor does the rest of the case establish the transfer. The fusion-dependent PRMT5 requirement in a
second EWSR1-fusion sarcoma [3] rests on one engineered line with partial fusion depletion and a
viability readout, and that report attributes the dependence to Ewing-specific replication stress
and BRCA1 sequestration rather than to the EWSR1 segment the two diseases share, with a PARP
inhibitor alone fusion-dependent in the same experiment. The clear cell report [2] shows binding and
promoter occupancy rather than methylation of the fusion, localises the interaction to no part of
it, and documents an equally good route into the complex through the ATF1 half. Section 3.7 shows
that the segment every EWSR1 fusion retains carries none of PRMT5's motif sites, which is a real
observation about the shared region, and it shows no correspondence between the diseases, because
the shared retained-site count is what the cluster structure returns for almost any mid-protein
breakpoint. What remains is that two other EWSR1-fusion sarcomas show PRMT5 dependence, that EMC is
a third such sarcoma, and that nobody has looked. That is a reason to run an experiment rather than
a result.

Two further limits sit on any version of this rationale. Elevated PRMT5 is not specific to this
disease on the comparison that has been published, since PRMT5, PRMT1 and MEP50 read higher across
multiple sarcoma types than in breast and lung cancer [3]; the comparator arm used here is other
sarcomas, which is the harder contrast, but "higher than other sarcomas" in 16 tumours and "a
sarcoma-wide feature" are not mutually exclusive and nothing here separates them. And on the
dependency panel PRMT5 is required in 94.1% of non-sarcoma lines as well as 94.5% of sarcoma ones,
so nothing in the public data makes it a selective target in this tissue class or any other.

### 4.2 Two decisive experiments

For the *MTAP* rationale, MTAP immunohistochemistry on archival EMC tissue. The stain is routine,
runs on formalin-fixed archival material, and is an accepted surrogate for homozygous 9p21 deletion:
homozygous deletion was found in 90% to 100% of cases with complete MTAP expression loss, checked
against FISH, across a survey of 13,067 tumours from 149 tumour types in which MTAP loss reached up
to 20% in various sarcomas [17]. That survey does not name this histology, so it supplies a class
prior rather than an answer. The validity quoted runs from loss to deletion, and the converse
requires a sensitivity that [17] is not cited for, so a retained stain excludes the protein-loss
state rather than excluding 9p21 deletion. Protein is nonetheless the right analyte, because an
MTA-cooperative agent depends on the metabolic consequence of MTAP protein loss however it arises,
while noting that the clinical selection reported for that class is genomic [6], so a stain and a
trial's entry criterion are not the same test.

For the fusion rationale, a PRMT5 inhibitor in a patient-derived EMC model, with a readout that can
discriminate. Two such models are published, USZ20-EMC1 carrying EWSR1-NR4A3 and USZ22-EMC2 carrying
TAF15-NR4A3, established by one group and used by it for drug testing: a 40-agent panel run once on
sarco-spheres, in which carfilzomib showed high sensitivity and doxorubicin good-to-moderate
sensitivity in both models, venetoclax showed no monotherapy response in the validation, and two
combinations gave synergy in one model and an additive effect in the other [21]. Whether any screen
is currently running in that laboratory is not something this work can state.

The readout matters more than the compound. Section 3.3 shows that a growth effect is close to
expected in any line, so viability alone would discriminate nothing; the endpoint that bears on the
transfer is fusion-driven transcription, for which reference [2] supplies the precedent of a CRE
reporter and target-gene qPCR, together with a concurrent non-EMC comparator line. The compound and
its class must also be named in advance, because the two rationales need different classes and
because the class decides the answer in the source disease. Reference [2] tested three inhibitors of
two mechanistic classes: the substrate-competitive compounds GSK591 and GSK3326595 were "only weakly
active in DTC-1 and SU-CCS-1 cells with GI50s in the high µM concentration range" and "neither of
these two substrate-competitive inhibitors significantly inhibited EWSR1-ATF1's transcription
activity", while the dual-site compound JNJ-64619178 gave GI50 values of 377 and 347 nM in those
lines and an IC50 of 422 nM in the reporter assay. Reference [3] obtained its fusion-dependent
effect with GSK591, one of the two that failed in clear cell sarcoma. A negative in an EMC model
with a substrate-competitive compound would therefore be hard to interpret, since the transfer's own
source disease has already produced that negative. Reference [3] also suggests one further arm:
PRMT5 inhibition sensitised Ewing cells to olaparib and the combination's cytotoxicity was only
partially rescued by fusion depletion, and its largest single effect was PRMT5 combined with PRMT1
inhibition rather than either alone.

Outcome interpretations are fixed in advance, and the negative branch of each is the falsifier table
of section 4.3. The positive branches are quickly said. PRMT5 inhibition active in an EMC model, on
a fusion-output readout, would be a fusion-class-transferred vulnerability in this disease that has
not been reported before; MTAP protein lost in a subset would define a genetically selected group in
it. Every branch is publishable and the negative branches are the more likely ones, which is what
makes a hypothesis of this shape affordable in an ultra-rare disease.

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

The evidence base is sixteen EMC tumours on two decade-old array platforms, six of them on one and
ten on the other. The genome-wide placement of section 3.5 provides context for that limit rather
than a correction of it; the correction is separate, and section 3.5 reports it.

Three limitations are structural, meaning that no revision or re-analysis of these data removes
them. First, on GPL3290 disease class is collinear with GEO submission block, with the two-colour
reference pool and with within-study platform assignment (section 2.1), so a permutation that
relabels those sixteen samples is not exchangeable and that platform cannot be treated as
independent evidence for anything. It is reported as a consistency check. Second, every primary
reading rests on a single probe per gene per platform, and on GPL3290 through a symbol bridge
resolving 58.2% of accessions on an expressed-sequence-tag array; a mis-annotated or
cross-hybridising spot is excluded by nothing in this work, and no decade-old array can be given
more probes. Third, no EMC cell line carrying the fusion appears in any public dependency dataset,
so no dependency evidence for this axis in this disease exists or can be generated computationally,
and the mechanistic fork of F10 cannot be settled here: separating "the fusion protein is the
substrate" from "PRMT5 acts on something the fusion depends on" would need isogenic constructs and
an arginine-substitution mutant within one construct, and the two published models differ in their
5′ partner rather than in transcript type, so they cannot stand in for that comparison.

What survives multiplicity correction and what does not should be stated plainly. Only one reading
in this paper falls below 0.05 once the number of genes examined is accounted for: *ENO3* on
GPL3290, an instrument control, at 0.010. The primary contrast does not, at 0.21 and 0.24. Neither
does *CDKN2A* at 0.51, nor the *NR4A3* control on GPL6244 at 0.85, nor the *ENO3* control on GPL6244
at 1.00. Three things qualify how much weight the corrected figures carry. The adjusted values are
lower bounds computed on about a third of each array, so they can only rise. They depend on the
family, and Table 6 gives the range. And a non-rejection is not a demonstration of absence, which is
why the *MTAP* result is argued from the per-sample conjunction in section 3.2 rather than from an
adjusted *p* of 1.00; the same procedure assigns 0.85 to *NR4A3* in the disease that fusion defines.

The count of comparisons should be read with that. The two documents report about 110 quantities and
correct 15 of them, being nine genes on GPL6244 and six on GPL3290, and the panel behind them carries 404 and 362 per-gene contrasts, 135 curated
group scores and both genome-wide scans across eighteen numbered reads on the same tumours, none of
which enters the multiplicity accounting except through the array-wide family.

A transcript is not a copy number, which is why the proposed experiments carry more weight here than
the readings do.

The original source of the fusion rationale was posted as a preprint and has since been published in
a peer-reviewed journal [2]; the statements attributed to it here were read from the preprint full
text, and the published version was identified by literature search rather than read, so the
bibliographic record in [2] is to be confirmed at the publisher before it is relied on. That caveat
attaches to every statement drawn from it in section 1.2 and section 4.2, including the
inhibitor-class result, which is the most consequential of them.

The fusion-class transfer is argued rather than assumed, and an argument is not a result. EWSR1::ATF1
and EWSR1::NR4A3 still do not share a DNA-binding domain, a target repertoire or a disease biology,
and no result presented here is an observation in EMC.

Five of GSE24369's forty-two deposited samples were excluded from the comparator arm by a classifier
that carried no pattern for their histology rather than by design (section 2.1). The primary
contrasts are insensitive to that: including them moves *PRMT5* from *t* = 6.24 to 6.31, *MTAP* from
0.69 to 0.70 and *CDKN2A* from −5.40 to −5.66. The per-class comparison of Figure 4 is not
insensitive to it, and is reported with the class included.

The motif analysis is a sequence argument, and the fusions it compares are constructs rather than
patients. It cannot show that any fusion is methylated, and it cannot be read as a response
predictor, since the one disease in which the mechanism was measured retains no sites.

The prior-art screen of section 1.3 matched titles and abstracts rather than full text, so its
absences are statements about what is indexed on a pairing rather than about what has been done, and
neither screen ran from the disease side to the target side over full text.

Nothing here has been tested in an EMC cell, and no agent in this class has been given to a patient
with this disease.

---

## 5. Conclusion

Two independent rationales place the PRMT5 methylosome in front of a disease for which no clinically
validated agent directly targets the driver, and the only public data able to address them supports
neither. Selection on *MTAP* loss fails its own pre-specified test on both platforms, and fails it
tumour by tumour as well: five of ten EMC tumours on one platform read below every comparator for
*MTAP*, none of them carries the low *CDKN2A* that 9p21 co-deletion requires, and no tumour of
sixteen is deletion-consistent, which bounds rather than excludes the event. The fusion-class
rationale is not tested by this data. *PRMT5* reads higher in EMC on both platforms and first of the
readable PRMT family on both, and that reading clears no conventional threshold once the number of
genes examined is accounted for, rests on a corrected value that ranges across three orders of
magnitude with the family chosen, comes on one platform from a deposit in which disease class cannot
be separated from batch, and names a target required in almost every screened cell line whether or
not it is a sarcoma. The sequence analysis contributes one durable observation, that the segment
every EWSR1 fusion retains carries none of PRMT5's reported motif sites, and withdraws another: the
shared retained-site count between two diseases' commonest junctions is what the cluster structure
returns for almost any mid-protein breakpoint. Each rationale ends at an inexpensive and decisive
experiment, a stain and a fusion-output readout in a published model, and neither has been run.

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

Full methods, every per-gene reading, the controls, the corrections register and an explicit list of
what would have to be true for this paper to be wrong are in the accompanying supplementary file,
[`emc-mtap-prmt5-hypothesis-SI.md`](./emc-mtap-prmt5-hypothesis-SI.md). The modality census, the
591-text corpus record and the 322-record prior-art screen of section 1.3 are deposited with it as
the author's unpublished supporting analyses.

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
