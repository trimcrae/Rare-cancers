---
id: DOC-EMC-MTAP-PRMT5
title: "The PRMT5 methylosome in extraskeletal myxoid chondrosarcoma: a fusion-class rationale that survives, an MTAP-locus rationale that does not, and two inexpensive tests"
level: L3
kind: manuscript
status: live
canonical_for: ["the 2026-08-09 EMC PRMT5/MTAP reading and its hypothesis"]
purpose: >
  State a therapeutic hypothesis that has not been raised for this disease, that the PRMT5
  methylosome may be actionable in it; give the two independent rationales that raise it; bound each
  against the only public data able to address them; and specify the inexpensive assays that would
  confirm or kill each.
scope: >
  L3. Two public archival expression series, 16 EMC tumours, transcript level only; a public sarcoma
  CRISPR dependency panel containing no EMC line; a sequence analysis of where PRMT5's reported
  substrate motif falls in the fusion protein; and published preclinical results in two other
  EWSR1-fusion sarcomas. This document raises a hypothesis and names its falsifiers. It reports no
  experiment in EMC cells, no drug exposure and no patient.
audience: [maintainers, external reviewers, autonomous research agents, collaborators]
date: 2026-08-09
last_verified: 2026-08-09
related: [DOC-MODALITY-CENSUS, DOC-EMC-UNEXPLORED-LANES]
---

# The PRMT5 methylosome in extraskeletal myxoid chondrosarcoma: a fusion-class rationale that survives, an MTAP-locus rationale that does not, and two inexpensive tests

**Tristan D. McRae**

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com
ORCID: [ORCID TO BE SUPPLIED BY THE AUTHOR BEFORE SUBMISSION]

Running title: PRMT5 in extraskeletal myxoid chondrosarcoma

*Keywords:* extraskeletal myxoid chondrosarcoma; EWSR1::NR4A3; PRMT5; MTAP; arginine methylation; fusion-driven transcription; rare sarcoma

*A hypothesis-generating re-analysis of public data. No experiment in an EMC cell, no drug exposure
and no patient are reported. Nothing here asserts efficacy, safety, a therapeutic window or clinical
readiness for any agent in any disease. Analyses, figures and drafting were carried out with AI
assistance (section 2.6).*

<!-- EDITORIAL, NOT FOR SUBMISSION.
VENUE: bioRxiv (Cancer Biology) as the free open copy, then Genes, Chromosomes and Cancer (Wiley),
Research Article. Reasoning. (a) Audience: GCC is the field journal for the genetics and genomics of
neoplasia and specifically for fusion-driven sarcomas, which is the readership for EWSR1::NR4A3,
EWSR1::ATF1 and EWSR1::FLI1 biology; the transcript-type and breakpoint content of section 3.7 has no
better home. (b) Fee: GCC is hybrid, so the open-access charge is optional and the subscription route
carries no author charge, which satisfies the standing constraint that the author pays nothing.
(c) Precedent: nr4a3-fusion-transcriptional-output-submission-checklist.md selected GCC on the same
two grounds on 2026-08-08.
FEE ROUTE: THE $0 SUBSCRIPTION ROUTE IS NOW VERIFIED AT PRIMARY SOURCE (2026-08-10). The publisher
policy pages were retrieved from a GitHub Actions runner rather than from this sandbox, because the
per-journal pages return HTTP 403 to both. Full record with verbatim quotations, URLs and HTTP
statuses: research/literature/venue-fee-routes-2026-08-10.json.
Wiley states on its own author pages that under open access "the author pays an Article Publication
Charge", that hybrid open access is selected by the corresponding author AFTER acceptance, and that a
subscription article requires only a Copyright Transfer or Exclusive License Agreement. The journal
is recorded as not open access and not in DOAJ. Declining the optional open-access selection is the
$0 route.
STILL NOT VERIFIED, and stated as such: the per-journal author-guideline pages return 403 from CI as
well, so the word, abstract and display-item limits written into this manuscript remain
search-derived. Those affect FORMAT, which an editor returns, not COST, which is billed. And the
APC figure itself comes from a bibliographic database rather than the publisher page; it is not the
number the decision rests on, since the charge is being declined.
ARTICLE TYPE: Research Article rather than Brief Report, because the paper carries five figures and
the Brief Report limit is two display items.
OPEN AT SUBMISSION: reference author lists. research/literature/mtap-prmt5-emc-citations.json records
title, journal, year, PMID, PMCID and DOI for every source but no author list, so most entries in the
reference list below carry none; the two that do were taken from the prior-art screen record, which
does carry author strings. Author lists must be completed from the source records at submission and
must not be written from recollection. ORCID is absent from the repository and only the author can
supply one.
IDENTIFIER FORMS. Six of the eleven references carry a PMCID and a DOI but no bare PMID, and that is
not an oversight. lint_citations.py anchors a PMID only when a tracked artifact writes it as "PMID
nnnnnnnn", as a pubmed.ncbi.nlm.nih.gov URL, as EXT_ID, or as a bare quoted key in a lit-targets
corpus. The citation artifacts here store it as a JSON field named pmid, which none of those patterns
match, so writing those PMIDs in prose fails gate 4 as if they had been recalled. The DOI and the
PMCID of every one of them do anchor and are given instead. This affects Chow 2007 in particular,
whose PubMed identifier 17545802, recorded in research/literature/emc-prior-art-2026-08-09.json, is
cited here by DOI for that reason; add the PMIDs at submission once they anchor.
PRIOR ART: section 1.3 and section 4.1 engage the 2025 comprehensive review and the one indexed
MTAP-in-chondrosarcoma hit, and every absence claim is narrowed to what is indexed.
-->

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare sarcoma driven by an *NR4A3* gene fusion,
usually EWSR1::NR4A3, for which no targeted agent exists. No indexed study examines the PRMT5
methylosome in this histology. We tested two independent rationales for it against the only public
data able to address them: the two archival expression series containing this histology (16 EMC
tumours across two platforms), a public sarcoma CRISPR dependency panel, and a sequence analysis of
PRMT5's reported substrate motif in the fusion protein. The first rationale transfers from other
EWSR1-fusion sarcomas, in which PRMT5 supports fusion-driven transcription. *PRMT5* reads higher in
EMC than in the comparator arm on both platforms (*t* = 6.24 and 6.67; exact permutation *p* = 0.000142
and 0.000125) and ranks first of the readable PRMT family members on both. Adjusting for a
twelve-gene proliferation score leaves that contrast nearly intact on the 35-tumour platform and
removes most of it on the 16-tumour platform, so the two platforms disagree. In EWSR1 the eleven
Gly-Arg-Gly sites all lie beyond residue 300; the commonest EMC fusion and the commonest clear cell
sarcoma fusion each retain four, while EWSR1::FLI1 retains none. The second rationale, selection on
*MTAP* loss, is not supported: *MTAP* is flat where the read is powered and reverses sign on the
other platform, and the locus signal is carried by *CDKN2A*. Two inexpensive experiments would settle
each rationale: MTAP immunohistochemistry on archival tissue, and one clinical-stage PRMT5 inhibitor
added to a screen already running on published EMC models.

---

## 1. Introduction

### 1.1 The disease and its treatment options

Extraskeletal myxoid chondrosarcoma is an ultra-rare translocation sarcoma defined by an *NR4A3*
gene fusion, most often EWSR1::NR4A3. The most recent comprehensive review of the disease states that
no clinically validated agent directly targets NR4A3, and reports pazopanib with an objective
response rate of 18% and a median progression-free survival of 19 months (NCT02066285) [1]. The
systemic classes with any disease-specific evidence number about eight, and only one carries a
meaningful response record. The natural history is indolent and the tumour is slow-cycling, which is
the profile in which mechanisms that scale with division rate are weakest. Both rationales examined
here act elsewhere: one on transcription, one on a metabolic state.

### 1.2 Two rationales for the PRMT5 methylosome

The first rationale runs through the fusion. A preprint reports that PRMT5 enhances
EWSR1-ATF1-driven gene transcription in clear cell sarcoma, that silencing PRMT5 impaired both
proliferation and fusion-driven transcription, and that a clinical-stage PRMT5 inhibitor inhibited
growth in vitro and in vivo [2]. Clear cell sarcoma is, like EMC, an ultra-rare translocation
sarcoma whose driver fuses the same 5′ gene, *EWSR1*, to a transcription factor, and whose fusion is
constitutively active because the EWSR1 portion supplies the activation domain. EMC's driver has
that architecture. A second and peer-reviewed disease reports the same dependence more specifically.
In Ewing sarcoma, PRMT5 and PRMT1 inhibitors cause growth arrest and apoptosis, and the effect of
single-agent GSK591 was "largely supressed by partial depletion of EWSR1::FLI1" [3], which is a
fusion-dependent PRMT5 requirement measured in a disease that is not EMC. The same report cuts
against the rationale in one respect and is cited here for both directions: PRMT5, PRMT1 and MEP50
read higher across multiple sarcoma types than in breast and lung cancer, and depleting EWSR1::FLI1
did not change PRMT transcript levels, so an elevated PRMT5 transcript is not a read-out of the
fusion.

The second rationale runs through a genetic selection window rather than through the fusion.
Tumours that have lost *MTAP* are comparatively more sensitive to PRMT5 and MAT2A inhibition, an
axis that has reached patients with an MTA-cooperative PRMT5 inhibitor selected on *MTAP* deletion
[4]. That sensitivity is comparative. A differential established in engineered and pan-cancer
settings is not a therapeutic window in a patient, and none is claimed here. The window also has a
known ambiguity. *MTAP* loss implies *CDKN2A* loss, while
*CDKN2A* loss does not imply *MTAP* loss [5], so a three-gene locus score can fall on a *CDKN2A*
event alone.

The methylosome is read as a unit rather than as PRMT5 alone because MEP50 (WDR77) is required for
PRMT5-catalysed activity and binds substrate independently [6].

### 1.3 Absence of the question from the published record

A modality census of this disease completed on 2026-08-09 enumerated 217 categories of cancer
treatment and found that classes selected by a molecular state had been dismissed as a group,
largely because the biomarker had never been read. A corpus of 591 open-access full texts retrieved
for this work contains no *MTAP*, *PRMT5* or *MAT2A* datum for this histology; its four incidental
mentions of the histology are diagnostic-pathology asides.

A separate Europe PMC prior-art screen of 322 records, 238 of them with full text, returned one hit
on the pairing of this histology with either target: a 2007 review of chondrosarcomas that names
methylthioadenosine phosphorylase among therapeutic targets "validated by translational research" in
that disease, while treating EMC as a distinct fusion-defined entity [7]. That review concerns the
parent histology, conventional chondrosarcoma, and predates the *MTAP*-deletion and PRMT5
synthetic-lethality literature entirely, so it speaks to the target's standing in chondrosarcoma
broadly rather than in this histology. The claim made here is accordingly narrow: nothing indexed
pairs the PRMT5 methylosome with extraskeletal myxoid chondrosarcoma. The screen matched titles and
abstracts rather than full text, so an absence in it means that nothing is indexed on a pairing and
not that no such work exists; a result inside a supplementary table of a larger paper would be
invisible to it.

---

## 2. Materials and methods

### 2.1 Expression series and per-gene scoring

Two public archival series carry this histology in a form this array-based reader can score as a group of tumours. That is a statement about the instrument, not about what exists: the readability record names five GEO series with EMC-titled samples, and the other three — GSE28866 (4 EMC), GSE43632 (1), GSE80126 (1) — are unread here because no platform of theirs mapped probes to gene symbols, which is an absent reading and never a reading of absence.

| series | platform | EMC tumours | comparator arm |
|---|---|---:|---|
| GSE24369 | GPL6244 | 6 | 29 comparator sarcomas, including a FET-rearranged histology |
| GSE4303 | GPL3290 | 10 | 6 |

Each gene's value in each sample was converted to a *z*-score against that array's own full probe
distribution, so a value is a position within an array rather than a quantity comparable across
platforms. A group score is the mean of its member genes' *z*, contrasted between EMC and the
comparator arm by Welch's *t*. No multiplicity correction is applied anywhere, and every reported
*t* must be read with that in mind. A curated group emits no score unless at least three genes are
readable and coverage is at least 0.5; a group failing that floor is reported as underpowered rather
than as a null result. A gene with no probe mapping is recorded as unreadable and never as
unexpressed, which matters below because one locus gene has no probe on the second platform.

### 2.2 Dependency panel

Gene-effect scores come from the DepMap public 24Q4 release (Chronos), restricted to sarcoma models.
The release lists 176 sarcoma models, of which 91 carry CRISPR gene-effect data; every figure here is
computed on those 91. A gene is called a dependency in a line at a gene effect below −0.5.

### 2.3 Exact permutation and genome-wide placement

Both designs are small enough to enumerate completely, so no normal approximation is used. Every
assignment of the observed *z* values to arms of the observed sizes was evaluated and Welch's *t*
recomputed, giving C(35,6) = 1,623,160 labelings on GPL6244 and C(16,10) = 8,008 on GPL3290. The
two-sided *p* is the fraction with |*t*| at least the observed value. No random sampling is used, so
the value is exactly reproducible.

The permutation is exact for the labelling and says nothing about how many genes were examined. That
question is asked separately by computing the same statistic for every symbol the platform's probes
map to (18,474 on GPL6244 and 14,402 on GPL3290) and placing each gene of interest in that
distribution. The genome-wide computation runs at fetch time, when the full probe matrix exists, and
re-derives from the raw matrix the statistic the panel computes from reduced per-gene values by a
separate code path; the two agree for every gene on both platforms.

### 2.4 Confound adjustment

A per-sample confound score is the mean *z* of the readable members of a named gene set, provided the
sample carries at least 60% of them. *PRMT5* is then regressed on that score by ordinary least
squares with one covariate and an intercept, and the EMC-versus-comparator contrast recomputed on the
residuals. A contrast is called surviving if it keeps its sign and at least 60% of its magnitude, a
threshold chosen for this work rather than taken from an established convention; raw and adjusted
values are both reported. The proliferation score uses twelve genes and scores all 35 and all 16 samples;
the chondroid-lineage score uses eight and scores 35 and 14.

### 2.5 Substrate-motif map

Occurrences of the motif GRG were counted by exact string scan on committed protein sequences, with
overlaps included, since GRGRG contains two sites and two methylatable arginines and a
non-overlapping scan would halve a poly-RG tract. A fusion's retained 5′ sites are those at or before
the last residue fully encoded by the 5′ partner, excluding the seam residue, because each of these
junctions splits a codon. Breakpoint positions are as reported in the sources; this work has no EMC
cohort of its own. Two double-entry checks are run against artifacts that predate this analysis: each
re-derived RG count against the counts those artifacts already held, and each fusion's own RG count
against the sum of its retained 5′ half and NR4A3's contribution.

### 2.6 Reproduction and AI assistance

Every figure, table and number is regenerable from public data by scripts in the accompanying
repository, and section 8 names the artifact that owns each value. Analysis, figures and drafting
were carried out with substantial assistance from an AI coding agent operating on a version-
controlled repository under the author's direction, using Anthropic Claude. The agent is not an
author and cannot be one, and the author takes responsibility for the content. The author verified
every reported value against the committed artifact that produced it, and specified the reads,
thresholds and controls before the corresponding data were retrieved. Two of the corrections recorded in Appendix A, the closure of the
locus rationale and the restatement of the fusion rationale on the gene rather than the group, were
found during figure preparation, after the prose had been written the other way. Every bibliographic
identifier below was taken from a retrieval record and is checked against a tracked artifact by an
automated linter.

---

## 3. Results

### 3.1 Group-level readings

The PRMT5 methylosome group reads higher in EMC than in the comparator arm on both platforms
(*t* = 3.11 and 3.89), and the methionine-salvage context group likewise (*t* = 4.26 and 2.07).
*MAT2A* sits at the 99th percentile of its array on GPL6244 and the 84th on GPL3290;
*PRMT5* sits at the 91st and at the 59th.

Scored as *MTAP* plus *CDKN2A* plus *CDKN2B*, the locus reads lower in EMC on GPL6244 with all three
genes readable, *t* = −4.06. On GPL3290 only two of three are readable, which falls below the panel's
coverage floor, so no score is emitted; that is an instrument limit rather than a reading of the
biology.

![Figure 1](../figures/mtap-prmt5-fig1-readings.png)

**Figure 1.** Every tumour on both platforms. Per-sample *z* against each array's own probe
distribution; bars are medians. The two platforms are not placed on a shared axis, because one is
single-channel intensity and the other a two-colour log-ratio. A gene with no probe is marked
unreadable, which records a missing measurement and not an absence of expression.

An elevated methylosome is consistent with the fusion rationale without being evidence for it, since
abundance is not dependency and elevated methylosome expression is reported across many malignancies
[3]. The low locus group score is likewise consistent with the *MTAP* rationale without supporting
it, for the reason developed in section 3.2.

### 3.2 The locus gene by gene

Read gene by gene, the locus does not support selection on *MTAP*.

| gene | GPL6244 (powered) | GPL3290 | genome-wide rank of \|*t*\| |
|---|---:|---:|---|
| *MTAP* | +0.053 SD, *t* = +0.69 | −0.607 SD, opposite sign | top 74% / top 26% |
| *CDKN2A* | −0.481 SD, *t* = −5.40 | +0.175 SD, reversed | top 3.5% / top 49% |
| *CDKN2B* | −0.136 SD | unreadable | top 34% / not applicable |

*MTAP*, the only gene of the three that carries the therapeutic argument, is flat on the powered
platform, changes sign on the other, and is unremarkable on both when placed against every gene on
its own array, at the top 74% and top 26% of the |*t*| distribution against *PRMT5*'s top 1.9% and
1.0%. The locus signal on the powered platform is *CDKN2A*, which itself changes direction between
platforms. The group statistic of −4.06 is accurate but is not a reading of *MTAP*, and a group
score cannot distinguish the two. Since the genetic window depends on *MTAP* loss specifically, the
locus reading does not support it. Only MTAP protein can settle the question, and the test proposed
in section 4.2 is accordingly a stain.

![Figure 2](../figures/mtap-prmt5-fig2-locus-genewise.png)

**Figure 2.** The three genes of the locus do not read alike. *MTAP* is flat on the powered
platform, while *CDKN2A* carries the whole locus signal and then reverses on the second platform.

### 3.3 The sarcoma dependency prior

Across the 91 screened sarcoma cell lines, PRMT5 and MAT2A are dependencies in 94.5% and 96.7%
respectively. MTAP is not a dependency in any of them, which is the expected profile for a biomarker
rather than a target and serves as the panel's internal control.

This weakens the specificity of the proliferation half of the transferred result. Silencing PRMT5
impairs proliferation in nearly every sarcoma line, so a growth effect in EMC would be close to
expected; the part that could be specific to this disease, and the part any transfer must rest on, is
the effect on fusion-driven transcription rather than on growth.

It does not refute the class. The therapeutic argument for the *MTAP*-selected axis is a
differential between *MTAP*-deleted and *MTAP*-intact cells, and a gene-effect score cannot express a differential of that
kind, since an MTA-cooperative inhibitor exploits a metabolic state rather than the raw dependency
[4]. A near-universal dependency and a genetic window are compatible.

![Figure 3](../figures/mtap-prmt5-fig3-dependency-qualifier.png)

**Figure 3.** The sarcoma dependency prior. PRMT5 and MAT2A are dependencies in almost every sarcoma
line, so a growth effect on silencing them is close to expected; only an effect on fusion-driven
transcription would be specific to this disease. MTAP is not a dependency, and neither rationale
gains support from this panel.

The panel contains no EMC line. No EMC cell line carrying the fusion appears in any public dependency
dataset, so this prior is a transfer from other sarcomas, limited by the complete absence of an EMC
observation rather than by sample size.

### 3.4 Comparator classes, pooled group against single gene

![Figure 4](../figures/mtap-prmt5-fig4-comparator-classes.png)

**Figure 4.** Pooled group against single gene, per comparator class. One comparator class, low-grade
fibromyxoid sarcoma, is FUS::CREB3L2 and therefore a FET-fusion control on whether the reading is
simply what a fusion sarcoma looks like. Pooled across the four
methylosome genes, EMC ranks second of four comparator classes, below desmoid fibromatosis, so the
group does not separate this disease. *PRMT5* alone does, with a median of +1.30 against +1.05, +1.04
and +0.94. Left-panel points are gene-by-sample values pooled across four genes, so they are not
independent observations and no test is run on them.

The two figures illustrate the same methodological point in opposite directions. For the locus, a
group score reported a signal that its decisive gene did not have; for the methylosome, a group score
hid a signal that its decisive gene does have. Neither is visible without reading the constituent
genes, so a curated group score is treated here as a summary and not as a unit of evidence.

### 3.5 PRMT5's own statistic and its genome-wide placement

*PRMT5* alone, the gene the fusion rationale depends on, reads *t* = 6.24 on GPL6244 and 6.67 on
GPL3290, against +0.263 and +0.816 SD.

| platform | *PRMT5 t* | labelings enumerated | at least as extreme | exact two-sided *p* |
|---|---:|---:|---:|---:|
| GSE24369 / GPL6244 | +6.24 | 1,623,160 | 230 | 0.000142 |
| GSE4303 / GPL3290 | +6.67 | 8,008 | 1 | 0.000125 |

On GPL3290 the exact *p* cannot fall below 1/8,008 whatever the effect size: with 10 versus 6 tumours
the resolution of the test is the sample size rather than the biology.

Placing each gene of interest against every gene on its own array gives the following, with two
instrument controls: *NR4A3*, the disease-defining fusion transcript, and *ENO3*, a published direct
target of an NR4A3 fusion.

| gene | GPL6244: *t*, rank of \|*t*\| | GPL3290: *t*, rank of \|*t*\| |
|---|---|---|
| *PRMT5* | +6.24, top 1.9% | +6.67, top 1.0% |
| *MAT2A* | +4.13, top 8.5% | +4.10, top 6.3% |
| *WDR77* | +2.82, top 20.5% | unreadable |
| *MTAP* | +0.69, top 74.0% | −2.27, top 26.1% |
| *CDKN2A* | −5.40, top 3.5% | +1.33, top 49.3% |
| *NR4A3* (control) | +4.66, top 5.9% | +1.70, top 38.5% |
| *ENO3* (control) | +3.61, top 12.0% | +13.22, top 0.05% |

The two controls do not behave alike. *ENO3* sits at the extreme of GPL3290, as a working
instrument should show. *NR4A3* is only mid-table there, consistent with the probe-placement caveat
the source artifact carries, since on a 3′-biased array the probe can sit in the region the fusion
replaces; GPL3290's ranking should not be read as if every row on it were equally trustworthy.

A rank is not a corrected *p*. It reports where a gene sits among all genes, controls no error rate,
is computed over a distribution containing real biology rather than a null, and is inflated in
effective sample size by correlation between transcripts. It supports only the narrower statement
that on these arrays a *t* of *PRMT5*'s size is uncommon and a *t* of *MTAP*'s size is not.

### 3.6 Three prespecified controls

Each control was specified against a named weakness before it was run, and each is a control rather
than an additional hypothesis test.

The first asks whether the elevation is *PRMT5* or the PRMT family, which matters because the Ewing
report finds PRMT1 and PRMT5 elevated together across sarcoma types [3]. Eight family members are
readable on GPL6244 and seven on GPL3290, and *PRMT5* ranks first on both. As a group the family is
flat (*t* = 0.33 and 1.34) while *PRMT5* alone reads 6.24 and 6.67. The separation is incomplete on
the second platform, where *CARM1* reads +5.44 and *PRMT3* +3.47, so a family-wide reading is
weakened rather than excluded; only on GPL6244, where the next member is *PRMT3* at +1.62, is
*PRMT5* clearly separated.

The second control adjusts for proliferation, and on one platform it takes most of the contrast.

| axis | platform | score elevated in EMC | *PRMT5 t*, raw to adjusted | reading |
|---|---|---|---:|---|
| proliferation, 12 genes | GPL6244, *n* = 35 | no, *t* = 0.45 | 6.24 to 5.23 | survives |
| proliferation, 12 genes | GPL3290, *n* = 16 | yes, *t* = 3.00 | 6.67 to 2.71 | most of the contrast goes with it |
| chondroid lineage, 8 genes | GPL6244, *n* = 35 | no, *t* = 0.99 | 6.24 to 6.20 | untouched |
| chondroid lineage, 8 genes | GPL3290, *n* = 14 | no, *t* = 0.36 | 6.67 to 6.52 | survives |

The second row weakens the transcript half of the fusion rationale. On GPL3290 the proliferation
score is itself higher in EMC, correlates with *PRMT5* at *r* = 0.60, and adjusting for it takes
*PRMT5* from 6.67 to 2.71; on that platform the reading is consistent with a proliferation effect.
The platforms disagree and neither is clearly preferable. GPL6244 has 35 tumours, a flat
proliferation score and a *PRMT5* contrast that barely moves; GPL3290 has 16, a two-colour
log-ratio measurement, and a proliferation score that moves with everything. The transcript half
therefore survives on the larger platform and not on the smaller one.

The third control tests chondroid lineage and is the weakest of the three even where it passes. No
comparator in either series is cartilage-lineage. It can ask whether *PRMT5* and chondroid markers
move together within these samples, and they do not (*r* = 0.05 and −0.04), but it cannot exclude
that chondroid tumours generally express *PRMT5*.

None of these adjustments can remove a confound that the proxy measures badly. Regressing out a
transcript score removes the part of the contrast the proxy linearly predicts and nothing more, so a
surviving result is a much weaker statement than a failing one.

### 3.7 The substrate motif in the fusion protein

The readings above are measurements on tumours and on cell lines. This section addresses where
PRMT5's reported substrate motif sits in the fusion protein.

Profiling arginine methylation genome-wide after selective PRMT5 inhibition, and validating hits by
in vitro methylation, identifies a preference for "arginine sandwiched between two neighboring
glycines (a Gly-Arg-Gly, or 'GRG,' sequence)" [8]. That is a preference and not a rule: PRMT5
methylates arginines outside GRG, and a GRG site is not necessarily methylated. A mapping experiment
in a different substrate narrows it the same way, since of three DDX5 fragments only the one carrying
the C-terminal RGG/RG motif was methylated by PRMT5, and mutating five arginines inside that motif
abolished it [9]. The EWSR1 protein is itself extensively arginine-methylated [10], which is what
makes the location of the motif in the fusion a question worth computing.

EWSR1 is 656 residues and carries eleven GRG sites, the first at residue 301 and none before it. The
N-terminal segment that every EWSR1 fusion retains is the SYGQ-rich transactivation region, and it
contains no site. Every site lies beyond residue 300, in the two RGG-rich regions the fusion
truncates. Residue 301 of 656 falls at 46% of the protein, so the sites are not confined to the
C-terminal half; the retained N-terminal segment contains none of them.

| fusion | 5′ residues retained | GRG sites kept | fraction of EWSR1's 11 |
|---|---:|---:|---:|
| EWSR1::NR4A3 type 1, the commonest EMC fusion | 431 | 4 | 0.364 |
| EWSR1::NR4A3 type 5 | 472 | 5 | 0.455 |
| EWSR1::NR4A3 type 2 | 264 | 0 | 0.000 |
| TAF15::NR4A3 | 161 | 0 | 0.000, of TAF15's 9 |
| EWSR1::ATF1, clear cell sarcoma, commonest type | 324 | 4 | 0.364 |
| EWSR1::FLI1, Ewing sarcoma, type 1 | 264 | 0 | 0.000 |

![Figure 5](../figures/mtap-prmt5-fig5-motif-map.png)

**Figure 5.** The motif, the RGG regions, and where each fusion cuts. EWSR1 is drawn once at full
length with its eleven GRG sites and its two RGG-rich regions; below it, each fusion's retained 5′
segment on the same ruler. EWSR1::FLI1 is plotted in the same style and keeps no site, and it is the
fusion in which a PRMT5 requirement has actually been shown to be fusion-dependent.

The commonest EMC fusion and the commonest clear cell sarcoma fusion retain the same number of sites,
at different breakpoints, by coincidence of where the RGG boxes fall. The transfer between the two
diseases, previously stated as an assumption (Appendix A), therefore has quantitative content.

The table does not license a prediction that retained-site count determines response. EWSR1::FLI1
retains no sites, and it is in EWSR1::FLI1 that a PRMT5 inhibitor's effect was shown to be
fusion-dependent [3]. Whatever PRMT5 does in a FET-fusion sarcoma, it does not require the fusion protein to be the substrate. EMC type 2
and TAF15::NR4A3, which retain none, are therefore not predicted to be unresponsive; the fusion
protein is one candidate substrate among several, and the others, including wild-type FET proteins,
Sm proteins and R-loop-resolution factors [9], carry their motifs regardless of the breakpoint.

A motif marks a site at which an enzyme can act. These counts do not show that any NR4A3 fusion is
methylated, that PRMT5 is the enzyme that would methylate it, or that methylation would be
functionally consequential.

---

## 4. Discussion

### 4.1 Status of the two rationales

The 2025 comprehensive review of this disease reaches the same categorical conclusion about the
absence of a targeted agent, and considers neither of the rationales examined here [1]. Read against
the only public data able to address them, the two rationales separate: one is closed and one
survives with a stated limit.

The *MTAP*-locus rationale is closed at transcript level by the data reported here. The three-gene
locus score does read lower where the read is powered, but the gene that carries the therapeutic
argument does not move, and the signal belongs to *CDKN2A*, which reverses between platforms. Since
the window selects on *MTAP* loss specifically, a transcript reading of the locus cannot support it.
The rationale survives only as a question that MTAP immunohistochemistry would answer directly, and
protein loss is what the window selects on in any case, so a transcript could not have seen it.

The fusion rationale survives, and the gene-level cut makes it more precise rather than less. The
methylosome group reads higher in EMC on both platforms, but per comparator class the group does not
separate this disease, while *PRMT5* alone does; *PRMT5* is the gene the rationale depends on, and
the other three members are flat or lower in EMC and dilute it. The rationale no longer rests on an
assumption alone: a peer-reviewed result in a second EWSR1-fusion sarcoma shows a fusion-dependent
PRMT5 requirement [3], and the sequence analysis of section 3.7 shows that the commonest fusion of
each of two diseases retains the same number of motif sites. Both are arguments about plausibility;
neither is an observation in EMC.

Two limits sit on the surviving rationale and are not resolved here. The transcript half survives its
proliferation control on the 35-tumour platform and does not on the 16-tumour one, and nothing
available decides between them. Elevated PRMT5 is also not specific to this disease on the comparison
that has been published, since PRMT5, PRMT1 and MEP50 read higher across multiple sarcoma types than
in breast and lung cancer [3]. The comparator arm used here is other sarcomas, which is the harder
contrast. But "higher than other sarcomas" in 16 tumours and "a sarcoma-wide feature" are not
mutually exclusive statements, and nothing here separates them.

### 4.2 Two decisive experiments

For the fusion rationale, a PRMT5 inhibitor in a patient-derived EMC model. Two such models exist and
are published, and their holders have already run a multi-agent functional screen on them. Adding one
clinical-stage PRMT5 inhibitor to a screen that already runs is among the smallest asks available in
this disease, and it tests the surviving rationale directly rather than through a biomarker. The
Ewing report suggests one addition: PRMT5 inhibition sensitised Ewing cells to olaparib, and the
combination's cytotoxicity was only partially rescued by fusion depletion [3], so a PRMT5 inhibitor
with and without a PARP inhibitor is two arms rather than one, and the combination arm carries a
mechanism.

For the mechanism behind that rationale, two constructs in one experiment. Section 3.7 leaves a fork
that no expression or dependency data can settle: whether the fusion protein is itself a PRMT5
substrate, or PRMT5 acts on something else the fusion depends on. EMC answers this more cleanly than
any other disease in the family, because its transcript types differ in retained motif count while
sharing a driver, with type 1 retaining four GRG sites and type 2 none. Comparing PRMT5 inhibition
across the two separates the mechanisms. The Ewing result predicts they will behave alike, since a
zero-site fusion already shows fusion-dependent PRMT5 sensitivity; a difference would be the
surprising outcome, and it is the one that would make the fusion protein itself the target.

For the *MTAP* rationale, MTAP immunohistochemistry on archival EMC tissue. The stain is routine,
runs on formalin-fixed archival material, and is an accepted surrogate for homozygous 9p21 deletion:
homozygous deletion was found in 90% to 100% of cases with complete MTAP expression loss, checked
against FISH, across a survey of 13,067 tumours from 149 tumour types in which MTAP loss reached up
to 20% in various sarcomas [11]. That survey does not name this histology, so it supplies a class
prior rather than an answer.

Outcome interpretations are fixed in advance.

| result | interpretation |
|---|---|
| PRMT5 inhibition inactive in EMC models | the fusion rationale is dead, and the negative is worth publishing because the fusion-class transfer is the interesting claim |
| PRMT5 inhibition active | a fusion-class-transferred vulnerability in this disease, not previously reported |
| type 1 and type 2 constructs respond alike | PRMT5 acts on something other than the fusion protein, consistent with Ewing, and the motif count is irrelevant to who would be treated |
| type 1 responds and type 2 does not | the fusion protein is the substrate, and EMC has a transcript-type-defined treatment group |
| MTAP protein retained across EMC cases | the *MTAP* rationale is dead and the locus reading was a *CDKN2A* shadow |
| MTAP protein lost in a subset | a genetically selected treatment group in this disease, not previously defined |

Every branch is publishable and the negative branches are the more likely ones, which is what makes a
hypothesis of this shape affordable in an ultra-rare disease.

### 4.3 Falsification criteria

| # | claim | the observation that would kill it |
|---|---|---|
| F1 | PRMT5 supports fusion-driven transcription in EWSR1-fusion sarcoma | failure to reproduce the clear cell sarcoma result, or a demonstration that its mechanism is ATF1-specific and does not run through EWSR1 |
| F2 | the transfer from EWSR1-ATF1 to EWSR1::NR4A3 is reasonable | PRMT5 inhibition inactive in an EMC model, the decisive test for the fusion rationale |
| F3 | the methylosome reads high in EMC | a third EMC series in which the PRMT5 group is null or lower |
| F4 | the MTAP locus reads low in EMC | a third series in which the locus group is null or higher |
| F5 | fired. The low locus read is *CDKN2A* alone: *MTAP* is flat where the read is powered, and *CDKN2A* reverses on the second platform | already fired; only MTAP protein retained or lost can now move it |
| F6 | MTAP protein is lost in some EMC | MTAP immunohistochemistry retained across an EMC series, the decisive test for the *MTAP* rationale and now the only thing that could reopen it |
| F7 | the readings are not proliferation or cellularity effects | partially fired, on one platform. Section 3.6: adjustment leaves *PRMT5* largely intact on GPL6244 (6.24 to 5.23, *n* = 35) and takes most of the contrast on GPL3290 (6.67 to 2.71, *n* = 16), where the score is itself elevated in EMC. The platforms disagree, and this is the likeliest way the transcript half is wrong |
| F8 | specificity rests on fusion-driven transcription, not on growth | a demonstration that PRMT5 inhibition slows EMC growth no more than it slows any sarcoma line's; the near-universal dependency of section 3.3 makes this the likeliest way the fusion rationale fails |
| F9 | the fusion-class transfer holds because the fusions are matched on PRMT5's motif | a corrected breakpoint that moves EMC type 1 or clear cell's commonest type off 4 retained sites; asserted in a test, so a revision fails the build rather than passing unnoticed. It would weaken the argument rather than the class, since the Ewing result stands with zero sites |
| F10 | the fusion protein is itself the relevant PRMT5 substrate | contradicted at one point already: EWSR1::FLI1 retains no site and PRMT5 inhibition is still fusion-dependent there [3]. It is listed rather than deleted because the two-construct experiment would settle it in EMC directly |

### 4.4 Limitations

The evidence base is sixteen tumours on two decade-old array platforms, with no correction for
multiple testing. Two series are not a replication set, and the locus result rests on six tumours
from one of them. The genome-wide placement of section 3.5 provides context for that limit rather
than a correction of it.

A transcript is not a copy number, which is why the proposed experiments carry more weight here than
the readings do.

The original source of the fusion rationale is a preprint whose own pages state that it is not
certified by peer review [2]. Its status since 2022 was not established here, and that caveat travels
with every use of it. It is no longer the only support, since the Ewing result [3] is peer-reviewed
and is the one showing a fusion-dependent PRMT5 requirement.

The fusion-class transfer is argued rather than assumed, and an argument is not a result. EWSR1::ATF1
and EWSR1::NR4A3 still do not share a DNA-binding domain, a target repertoire or a disease biology,
and no result presented here is an observation in EMC.

The motif analysis is a sequence argument, and the fusions it compares are constructs rather than
patients. It cannot show that any fusion is methylated, and it cannot be read as a response
predictor, since the one disease in which the mechanism was measured retains no sites.

The transcript half of the fusion rationale survives its proliferation control on one platform and
not on the other.

No EMC cell line carrying the fusion appears in any public dependency dataset, so no dependency
evidence for this axis in this disease exists or can be generated computationally.

Abundance is not dependency, and the dependency prior that exists bounds both rationales without
supporting either.

The prior-art screen of section 1.3 matched titles and abstracts rather than full text, so its
absences are statements about what is indexed on a pairing rather than about what has been done.

Nothing here has been tested in an EMC cell, and no agent in this class has been given to a patient
with this disease.

---

## 5. Conclusion

Two independent rationales place the PRMT5 methylosome in front of a disease that has no targeted
agent, and the only public data able to address them separates the two. Selection on *MTAP* loss is
not supported at transcript level: the gene that carries the argument does not move where the read is
powered, and the locus signal belongs to *CDKN2A*. The fusion rationale survives, stated on *PRMT5*
rather than on the methylosome group, supported by a fusion-dependent PRMT5 requirement in a second
EWSR1-fusion sarcoma and by a motif match between the commonest fusion of two diseases, and limited
by a proliferation control that disagrees between platforms. Each rationale ends at an inexpensive
and decisive experiment, and neither has been run.

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

**Author contributions.** Sole author: conception, analysis, figures and writing.

**Generative AI.** Section 2.6.

---

## 7. Supplementary information

Full methods, every per-gene reading, the controls, the corrections register and an explicit list of
what would have to be true for this paper to be wrong are in the accompanying supplementary file,
[`emc-mtap-prmt5-hypothesis-SI.md`](./emc-mtap-prmt5-hypothesis-SI.md).

---

## 8. Data and code availability

Both expression series (GSE24369, GSE4303) and the DepMap CRISPR release are public. No data
generated by the author is withheld, because this study creates no new measurement.

| item | location |
|---|---|
| Expression readings, every *z*, percentile and group score | [`emc-expression-panels.json`](../../modalities/emc-expression-panels.json) |
| Grading of this route against its selection criterion | [`census-route-expression-grading.json`](../../modalities/census-route-expression-grading.json) |
| Sarcoma-line dependency prior | [`depmap-sarcoma-dependency.json`](../../modalities/depmap-sarcoma-dependency.json) |
| Control calculations of section 3.6 | [`emc-prmt5-route-controls.json`](../../modalities/emc-prmt5-route-controls.json) |
| Substrate-motif counts and their double-entry checks | [`emc-prmt5-substrate-motif-map.json`](../../modalities/emc-prmt5-substrate-motif-map.json) |
| Committed protein sequences and sourced breakpoints | [`emc-fet-construct-designs.json`](../../modalities/emc-fet-construct-designs.json), [`emc-fet-idr-census.json`](../../modalities/emc-fet-idr-census.json) |
| Citation anchor, every identifier read from a retrieval | [`mtap-prmt5-emc-citations.json`](../../literature/mtap-prmt5-emc-citations.json) |
| Prior-art screen of section 1.3, with its retrieval record | [`emc-prior-art-2026-08-09.json`](../../literature/emc-prior-art-2026-08-09.json) |
| Figure provenance hashes | [`mtap-prmt5-figure-provenance.json`](../figures/mtap-prmt5-figure-provenance.json) |

---

## 9. References

1. Remiszewski P, Falkowski S, Szumera-Ciećkiewicz A, Spałek MJ, Rutkowski P, Czarnecka AM. From pathogenesis to the patient's bedside: a comprehensive review of extraskeletal myxoid chondrosarcoma. *Journal of Cancer Research and Clinical Oncology* 2025;151(11):283. PMID 41055792. PMC12504171. doi 10.1007/s00432-025-06316-5.
2. PRMT5 as a Novel Druggable Vulnerability for EWSR1-ATF1-driven Clear Cell Sarcoma. bioRxiv preprint, posted 2022-03-23. doi 10.1101/2022.03.23.485409. The preprint states that it is not certified by peer review.
3. Ward CM, Brockwell C, McNee GS, Orton E, Prowse ENP, Gatz SA, et al. Arginine methylation regulates Ewing sarcoma cell viability in a EWSR1::FLI1 dependent manner and provides a therapeutic opportunity. *Frontiers in Oncology* 2025;15:1538208. PMID 40823091. PMC12354397. doi 10.3389/fonc.2025.1538208.
4. Engstrom LD, Aranda R, Waters L, Moya K, Bowcut V, Vegar L, et al. MRTX1719 Is an MTA-Cooperative PRMT5 Inhibitor That Exhibits Synthetic Lethality in Preclinical Models and Patients with MTAP-Deleted Cancer. *Cancer Discovery* 2023;13(11):2412-2431. PMID 37552839. PMC10618744. doi 10.1158/2159-8290.CD-23-0669.
5. Bou Zerdan M, Ashok Kumar P, Haroun E, Srivastava N, Ross J, Sivapiragasam A. Genomic landscape of metastatic breast cancer (MBC) patients with methylthioadenosine phosphorylase (MTAP) loss. *Oncotarget* 2023;14:178-187. PMID 36913304. PMC10010627. doi 10.18632/oncotarget.28376.
6. Ho MC, Wilczek C, Bonanno JB, Xing L, Seznec J, Matsui T, et al. Structure of the arginine methyltransferase PRMT5-MEP50 reveals a mechanism for substrate specificity. *PLoS ONE* 2013;8(2):e57008. PMID 23451136. PMC3581573. doi 10.1371/journal.pone.0057008.
7. Chow WA. Update on chondrosarcomas. *Current Opinion in Oncology* 2007. PMID 17545802. doi 10.1097/cco.0b013e32812143d9.
8. Musiani D, Bok J, Massignani E, Wu L, Tabaglio T, Ippolito MR, et al. Proteomics profiling of arginine methylation defines PRMT5 substrate specificity. *Science Signaling* 2019;12(575):eaat8388. PMID 30940768. doi 10.1126/scisignal.aat8388.
9. Mersaoui SY, Yu Z, Coulombe Y, Karam M, Busatto FF, Masson JY, et al. Arginine methylation of the DDX5 helicase RGG/RG motif by PRMT5 regulates resolution of RNA:DNA hybrids. *The EMBO Journal* 2019;38(15):e100986. PMID 31267554. PMC6669924. doi 10.15252/embj.2018100986.
10. Belyanskaya LL, Gehrig PM, Gehring H. Exposure on cell surface and extensive arginine methylation of Ewing sarcoma (EWS) protein. *Journal of Biological Chemistry* 2001;276(22):18681-18687. PMID 11278906. doi 10.1074/jbc.m011446200.
11. Gorbokon N, Wößner N, Lennartz M, Dwertmann Rico S, Kind S, Reiswich V, et al. Prevalence of S-methyl-5'-thioadenosine Phosphorylase (MTAP) Deficiency in Human Cancer: A Tissue Microarray Study on 13,067 Tumors From 149 Different Tumor Types. *American Journal of Surgical Pathology* 2024;48(10):1245-1258. PMID 39132873. PMC11404761. doi 10.1097/PAS.0000000000002297.

Author lists, journal titles, volumes and pages are taken from the retrieval records in
[`submission-reference-metadata-2026-08-09.json`](../../literature/submission-reference-metadata-2026-08-09.json)
and [`emc-prior-art-2026-08-09.json`](../../literature/emc-prior-art-2026-08-09.json). Reference 2 is a
preprint that neither retrieval returned, so it carries its identifier and posting date alone and must
be completed from the source record before submission. Where a record lists more than six authors the
first six are given.

---

## Appendix A. Superseded and corrected values

Per [CLAUDE.md](../../../CLAUDE.md) rule 1.2, a corrected value is registered rather than dropped, and
the live text above carries only the current value. The full corrections register, including the
values that only ever appeared in the supplementary file, is in the SI appendix.

| superseded | current | where it lived | why it changed |
|---|---|---|---|
| *"The fusion-class transfer is an assumption."* | The transfer is argued rather than assumed, and an argument is not a result | §7 of the earlier draft, now §4.4 | Two things changed it and neither is an EMC measurement: a peer-reviewed fusion-dependent PRMT5 requirement in a second EWSR1-fusion sarcoma [2], and the finding that the commonest EMC fusion and the commonest clear cell fusion retain the same number of PRMT5-motif sites (§3.7). What did not change: EWSR1::ATF1 and EWSR1::NR4A3 still do not share a DNA-binding domain, a target repertoire or a disease biology |
| *PRMT5* EMC-minus-comparator of +0.266 and +0.744 SD | +0.263 and +0.816 SD | §3.5 | The values had drifted from [`emc-expression-panels.json`](../../modalities/emc-expression-panels.json), which is their one home. Checked 2026-08-09 against the committed artifact; the second differs by 0.07 SD and the reading is unchanged in direction or size class |
| The methylosome **group** *t* (3.11, 3.89) quoted as the statistic the fusion rationale rests on | The gene's own *t* (6.24, 6.67), with the group figures retained in §3.1 as the group figures they are | §3.1 and §3.5 | The group score is not the unit the rationale depends on. The group figures are not withdrawn; they were the wrong ones to lead with |
| Locus gene values of *MTAP* −0.023 / −0.389; *CDKN2A* −0.399 / +0.173; *CDKN2B* −0.096 | +0.053 / −0.607; −0.481 / +0.175; −0.136 | §3.2 | Cause not established, and an earlier explanation was wrong. *Superseded, retained: "a re-fetch ran on a NARROWER probe-to-symbol bridge (0.931 against 0.984), and a narrower bridge changes which probes map."* Checked against every committed version of the artifact, *MTAP* reads +0.053 in all of them, at bridge rates 0.984, 0.931 and 0.981, and always on one mapped probe. Bridge width does not move this gene. The −0.023 appears in no committed artifact, so it entered the prose from a source the repository cannot show |
| "across 176 sarcoma cell lines" | "across the 91 screened sarcoma cell lines" | §3.3 and the abstract | A real error, in the direction that overstated the evidence base, and it was in four places including the abstract. The release lists 176 sarcoma models; only 91 carry CRISPR gene-effect data. The percentages themselves are unchanged, having always been computed on the screened subset, but they were attributed to a denominator almost twice its true size |
| The paper's own framing as a repository memo, with per-section warning banners and a five-figure inventory in the front matter | A journal Research Article in IMRaD form, with the warnings folded into the abstract's scope statement, section 4.4 and this appendix | throughout | The register was correct for a maintainer and wrong for a journal reader. Nothing measured was removed; the honest statements the pre-posting checklist requires to survive are all present in sections 3.2, 3.3, 3.6, 3.7, 4.1 and 4.4 |
