#!/usr/bin/env python3
"""Deterministic P-ST correction batch (findings F01-F13 of FINAL-SCIENTIFIC-REVIEW-P-ST.md).

Applies exact string replacements to the frozen main and SI. Every edit must match exactly
once or the script fails with a non-zero exit; nothing is regenerated, no producer is run,
no measurement is recomputed and no numeric value is changed except the three arithmetic /
labelling corrections named in F07 (42-6-29 = 7 remaining arrays; residual fibrosarcoma ->
myxofibrosarcoma; 238 full-text files -> 237 text files plus an index).

Usage:  python3 apply_pst_correction.py <frozen_dir> <out_dir>
"""
import hashlib
import pathlib
import sys

MAIN = "emc-surface-target-landscape.md"
SI = "emc-surface-target-landscape-si.md"

# ---------------------------------------------------------------- main text
EDITS_MAIN = [

# ---- F02/F12: title and front matter set the claim once -------------------
("F02-title-frontmatter",
 'title: "Surface-antigen prioritisation in extraskeletal myxoid chondrosarcoma: a lineage-surrogate ranking tested against three tumour-tissue cohorts"',
 'title: "Surface-antigen prioritisation in extraskeletal myxoid chondrosarcoma: an archival comparison of a lineage-surrogate ranking with three tumour-tissue transcript cohorts"'),

("F02-title-heading",
 "# Surface-antigen prioritisation in extraskeletal myxoid chondrosarcoma: a lineage-surrogate ranking tested against three tumour-tissue cohorts",
 "# Surface-antigen prioritisation in extraskeletal myxoid chondrosarcoma: an archival comparison of a lineage-surrogate ranking with three tumour-tissue transcript cohorts"),

("F02-F11-purpose",
 """  Submission text for PUB-SURFACE-TARGETS, prepared to British Journal of Cancer Article format with a
  bioRxiv preprint as the free open copy. Reports a two-stage in-silico study: a lineage-surrogate
  surfaceome ranking with a normal-tissue prior, and the test of that ranking in three EMC
  tumour-tissue cohorts. Supplementary material is in emc-surface-target-landscape-si.md.""",
 """  Submission text for PUB-SURFACE-TARGETS, prepared to British Journal of Cancer Article format with a
  bioRxiv preprint as the free open copy. Reports a retrospective, descriptive comparison of two
  archival transcript instruments: a historical lineage-surrogate surfaceome ranking with a custom
  normal-tissue annotation heuristic, and three EMC tumour-tissue transcript cohorts. The two
  instruments measure different contrasts in different compartments; no transfer-accuracy or
  ranking estimand is defined or estimated anywhere in this work. Supplementary material is in
  emc-surface-target-landscape-si.md."""),

("F01-F03-scope-frontmatter",
 """  Public expression data only. Transcript abundance, never protein; never surface localisation,
  receptor density, selectivity, safety, a therapeutic window or clinical readiness. None of those
  quantities is computed in this document or in any artifact it cites.""",
 """  Public expression data only. Transcript abundance and deposited summary scores, never protein;
  never surface localisation, receptor density, selectivity, safety, a therapeutic window or clinical
  readiness. None of those quantities is computed in this document or in any artifact it cites. The
  normal-tissue annotation used here is a custom category heuristic over incompletely observed
  records, not a validated normal-tissue filter."""),

# ---- F01/F09: scope-of-claims box ----------------------------------------
("F01-scope-box",
 """> paper or in any artifact it cites. Nothing here asserts that any antigen is a validated target in
> extraskeletal myxoid chondrosarcoma, that any agent is safe or effective in it, that any therapeutic
> window exists, or that any route is ready for clinical use.""",
 """> paper or in any artifact it cites. Nothing here asserts that any antigen is a validated target in
> extraskeletal myxoid chondrosarcoma, that any agent is safe or effective in it, that any therapeutic
> window exists, or that any route is ready for clinical use. The normal-tissue verdicts reported here
> are historical labels from a custom category heuristic whose quantitative tissue and blood fields are
> null for every classified record (Methods, Supplementary Methods S3); no clean normal-tissue window,
> no absence from any vital tissue and no exposure bound is established by anything in this paper."""),

# ---- Abstract -------------------------------------------------------------
("F02-abstract-background",
 """differently from driver-directed routes, but EMC surface-antigen expression is not systematically
mapped, leaving prioritisation to lineage surrogates.""",
 """differently from driver-directed routes. Public EMC surface-antigen expression has not been assembled
into a map that this work's bounded prior-art retrieval could find, and prioritisation for this disease
has in practice run on lineage surrogates."""),

("F02-F03-F05-F07-abstract-methods",
 """**Methods.** A 2,826-gene surfaceome was ranked across a translocation-sarcoma DepMap class
(76 lines) by a rank-based, Benjamini-Hochberg-corrected selectivity test, then filtered by a Human
Protein Atlas normal-tissue prior. Priorities were tested in three EMC tumour-tissue cohorts:
GSE24369 (6 EMC versus 29 sarcomas), GSE4303/GPL3290 (10 versus 6) and GSE28866 (4 EMC, 27
normal-organ, 32 sarcoma libraries). Array contrasts carry exact *p*, a 95 % confidence interval and a
Benjamini-Hochberg *q* corrected within platform across the 100-gene board at alpha 0.05; three
prespecified sensitivity analyses test the comparator arms. The sequencing cohort carries no test.""",
 """**Methods.** A 2,826-gene surfaceome, 2,692 genes of which were present in the expression matrix and
stated as scanned, was ranked across a translocation-sarcoma DepMap class (76 class members, of which
45 carry expression data and enter the tested rows) by a rank-based, Benjamini-Hochberg-corrected
selectivity test, and annotated with a custom normal-tissue category heuristic built on Human Protein
Atlas fields. Those historical priorities are compared here with three archival EMC tumour-tissue
cohorts: GSE24369 (6 EMC versus 29 sarcomas, GPL6244), GSE4303/GPL3290 (10 versus 6) and GSE28866
(4 EMC libraries, 27 normal-organ libraries of which 17 are adult and 10 fetal, and 32 non-EMC sarcoma
libraries from 30 specimens). Array contrasts carry a Welch two-sided *p* on Welch-Satterthwaite
approximate degrees of freedom, an ordinary pointwise 95 % confidence interval, and a
Benjamini-Hochberg *q* corrected within platform across the 100-gene board at alpha 0.05; three
recorded sensitivity analyses vary the comparator arms. The sequencing cohort carries no test, and its
values are deposit-normalised, square-root-compressed summary scores rather than linear abundances.
The two instruments measure different contrasts in different compartments, so no transfer-accuracy or
ranking estimand is defined or estimated."""),

("F01-F02-F07-abstract-results",
 """**Results.** Nine of the evaluated classic antigens were selective in the surrogate, and 18 of the
47 retained actionable antigens were selective overall; B7-H3/CD276 was not (q = 1.0). The
normal-tissue prior left no classic antigen both selective and restricted, and exactly one member of
the wider actionable set, DLL3. Thirteen of those 18 carry a tumour-tissue reading and five have no row
on the cross-platform board. Under within-platform correction none of the 13 was concordantly elevated
on both arrays and two, FGFR1 and PTK7, were concordantly lower. None of eleven route-named therapeutic
addresses was concordantly elevated. Three genes on the 100-gene board were concordantly elevated:
BGN, CD44 and VCAN. ALCAM had a positive point estimate on both arrays, significant on GPL6244
(*q* < 0.001) but not on GPL3290 after correction (*q* = 0.162, interval crossing zero), and its EMC
median sat below the normal-organ median in the sequencing cohort. CSPG4, never evaluated at stage 1,
rose on one array and in the sequencing cohort, was uninformative rather than negative on the second,
and is held open.""",
 """**Results.** Nine of the 15 evaluated classic antigens carried a significant surrogate selectivity
flag, and 18 of the 47 retained actionable antigens did; B7-H3/CD276 did not (q = 1.0). Intersecting
the 18 with the heuristic's stored RESTRICTED labels leaves no classic antigen and exactly one member
of the wider actionable set, DLL3 — a stored-label intersection only, over records whose quantitative
tissue and blood fields are null throughout, and six of the 18 carry no normal-tissue record at all. Of
the 18, ten carry contrasts on both arrays, three (CD248, GPC2, ROR1) on one array only, and five have
no row on the cross-platform board. Of the ten eligible for a two-platform rule, none met the upward
rule on both arrays and two, FGFR1 and PTK7, met the downward rule on both; these are conditional
observations under one operational rule and not a measurement of biological transfer. None of eleven
route-named therapeutic addresses met the upward rule on both arrays. Three genes on the 100-gene board
did: BGN, CD44 and VCAN. ALCAM had a positive point estimate on both arrays, significant on GPL6244
(*q* < 0.001) but not on GPL3290 after correction (*q* = 0.162, ordinary interval crossing zero), and
its EMC summary score sat below the pooled normal-organ score in the sequencing cohort. CSPG4, which
has no retained selectivity result, rose on one array and in the sequencing scores, was uninformative
rather than negative on the second, and is held open."""),

("F02-F09-abstract-conclusions",
 """**Conclusions.** Surface priorities derived from the lineage surrogate were not reproduced in EMC
tumour tissue. Neither instrument measures protein, and the readings support a prioritisation of which
antigens to stain rather than any target, safety or efficacy claim.""",
 """**Conclusions.** The historical surrogate priorities did not meet this study's two-platform
statistical rule in the different comparisons the tissue cohorts support. Because the two instruments
ask different questions of different compartments, that is a conditional observation rather than a
measured failure of biological transfer or of surrogate methods in general. Neither instrument measures
protein, and the readings support a prioritisation of which antigens to stain rather than any target,
safety or efficacy claim."""),

# ---- Background: F12 -------------------------------------------------------
("F12-background-prior-art",
 """Surface-antigen prioritisation for EMC has had to run on surrogates because the disease was taken to be
absent from usable public expression data. A prior-art screen run for this work supports the underlying
gap. A Europe PMC retrieval of 322 EMC-linked records, 238 of them with full text, was hand-screened for
surfaceome, surface antigen, cell-surface protein, chimeric antigen receptor, radioligand,
antibody-drug conjugate and immunotherapy terms. It returned three EMC-specific records, none of which
is a systematic surface-antigen map: a radiotherapy case report [3], a single case describing an
immunosuppressive tumour microenvironment in EMC with pleural metastases [4], and a multidisciplinary
review of uncommon soft-tissue sarcomas [5]. That screen matched titles and abstracts, not full text, so
it establishes that nothing is indexed on those pairings rather than that no such work exists; a
surface-antigen analysis inside a supplementary table of a larger sarcoma paper would be invisible to
it.""",
 """Surface-antigen prioritisation for EMC has in this programme run on surrogates, on the working
assumption that the disease was absent from usable public expression data. That was a programme
assumption, not a demonstrated property of the field. A bounded prior-art retrieval run for this work
is the only evidence offered for it here. A Europe PMC retrieval of 322 EMC-linked records, with 237
retained text files plus an index file, was screened for surfaceome, surface antigen, cell-surface
protein, chimeric antigen receptor, radioligand, antibody-drug conjugate and immunotherapy terms. It
returned three EMC-specific records, none of which is a systematic surface-antigen map: a radiotherapy
case report [3], a single case describing an immunosuppressive tumour microenvironment in EMC with
pleural metastases [4], and a multidisciplinary review of uncommon soft-tissue sarcomas [5]. The screen
matched titles and abstracts, and its follow-up full-text pass applied a narrower algorithmic rule over
a limited antigen list, so the retained result is a bounded screening outcome and not a systematic
negative: it does not establish that nothing is indexed on those pairings, that no such work exists, or
that the field lacked EMC surface-antigen information. The three deposits reanalysed below are
themselves prior work by their depositors and are credited as such (Methods, Data availability)."""),

# ---- Methods: F01 normal prior --------------------------------------------
("F01-methods-normal-prior",
 """### Normal-tissue prior

Each antigen was queried against the Human Protein Atlas [6] for RNA tissue specificity, tissue
distribution, per-tissue nTPM, blood-cell specificity and subcellular location, and given a verdict with
Human Protein Atlas semantics. Only tissue-enriched or group-enriched antigens with a restricted
distribution, no vital-tissue signal and no strong immune or circulating signal were classed RESTRICTED.
Tissue-enhanced antigens, detected broadly with a peak, were classed ENHANCED_BROAD. Low tissue
specificity, or a detected-in-all distribution, gave BROAD_LIABILITY. Expression in a vital tissue, or a
confined blood signal, overrode all others as VITAL_OR_IMMUNE_LIABILITY. Controls behaved as specified:
DLL3 and GPC3 returned RESTRICTED, B2M returned BROAD, and the hard control CD3E returned a vital or
immune liability. Human Protein Atlas RNA is bulk normal tissue and a prior, not a safety statement.""",
 """### Normal-tissue annotation heuristic, and what it did not observe

Each antigen was queried against the Human Protein Atlas [6] for RNA tissue specificity, tissue
distribution, per-tissue nTPM, blood-cell specificity and subcellular location. The stored verdicts are
the output of a **custom category heuristic written for this programme**, not a Human Protein Atlas
tier, and they are reported throughout this paper as historical labels rather than as a filter this
study validated. The declared rule was that tissue-enriched or group-enriched antigens with a restricted
distribution, no vital-tissue signal and no strong immune or circulating signal were classed RESTRICTED;
tissue-enhanced antigens, detected broadly with a peak, ENHANCED_BROAD; low tissue specificity or a
detected-in-all distribution, BROAD_LIABILITY; and expression in a vital tissue or a confined blood
signal overrode all others as VITAL_OR_IMMUNE_LIABILITY.

**The implemented classifier did not run the quantitative half of that rule.** The
quantitative tissue-specific and blood-specific nTPM fields are null for **all 45 classified records**;
the code substitutes an empty string for the missing tissue value before searching it for vital-tissue
names, so the vital-tissue branch never inspected an expression level for any antigen in this study. All
nine VITAL_OR_IMMUNE_LIABILITY labels therefore arise from the blood-category branch alone. The
classifier also does not implement the "restricted distribution" conjunct: ALCAM, B4GALNT1 and GPC3
carry a "Detected in many" distribution and still receive RESTRICTED. RESTRICTED is consequently a
category label from an incompletely observed heuristic. It is **not** evidence of absence from any vital
tissue, not a validated therapeutic window, and not a coverage statement about tissues the record does
not contain; even a non-null tissue-specific nTPM field would not be a per-tissue expression matrix. Six
of the 18 selectivity-flagged actionable antigens (ALK, ENPP1, FGFR4, PDGFRA, SLC34A2, STEAP1) carry no
record at all, so the wider set is not exhaustively annotated.

The recorded controls are development checks on this heuristic and not an independent calibration of its
clinical meaning. DLL3 and GPC3 returned RESTRICTED, B2M returned a broad verdict, and CD3E returned a
vital-or-immune liability — CD3E is tissue-enriched in its record and reaches the **immune** branch, so
it does not exercise the tissue-enhanced branch; the rule additionally exempts weak immune enhancement,
which is a heuristic tuned around its own controls. No Human Protein Atlas query was re-run for this
correction and no missing quantitative value was imputed. Human Protein Atlas RNA is bulk normal tissue
and a prior, not a safety statement."""),

# ---- Methods: F07 cohort arithmetic + F04 sequencing panel + F03 scale ----
("F07-F04-F03-methods-cohorts",
 """comparator sarcomas (17 low-grade fibromyxoid sarcoma, 6 desmoid fibromatosis, 6 myxofibrosarcoma —
the deposit's own annotations read "Myxofibrosarcoma") form the primary contrast and supply a lineage
axis. The remaining 13 arrays are 5 solitary fibrous tumours and 2 pooled normal skeletal-muscle
samples; neither enters the primary contrast, and both are used in the sensitivity analyses below.
GSE4303 on GPL3290 carries 10 EMC against 6 comparators (3 dermatofibrosarcoma protuberans, 3
gastrointestinal stromal tumour) and supplies a second lineage axis with different comparators; the
cohort was first published by Subramanian and colleagues [7]. GSE28866, a 3'-end sequencing deposit,
carries 4 EMC libraries, 27 normal-organ libraries (bowel, breast, colon, kidney, lung, uterus) and 32
non-EMC sarcoma libraries, and supplies both a lineage axis and the on-target off-tumour exposure axis.""",
 """comparator sarcomas (17 low-grade fibromyxoid sarcoma, 6 desmoid fibromatosis, 6 myxofibrosarcoma —
the deposit's own annotations read "Myxofibrosarcoma", verbatim for GSM600957 to GSM600962) form the
primary contrast and supply a lineage axis. 42 arrays minus those 35 leaves **7** remaining arrays:
5 solitary fibrous tumours and 2 pooled normal skeletal-muscle samples. Neither enters the primary
contrast, and both are used in the sensitivity analyses below. The GEO summary record links this series
to PMID 21536545. GSE4303 on GPL3290 carries 10 EMC against 6 comparators (3 dermatofibrosarcoma
protuberans, 3 gastrointestinal stromal tumour) and supplies a second lineage axis with different
comparators; the cohort was first published by Subramanian and colleagues [7], and the GEO summary
record gives the same link (PMID 15920699). GSE28866, a 3'-end sequencing deposit whose GEO summary
record links it to PMID 22929540, carries 4 EMC libraries, 27 normal-organ libraries and 32 non-EMC
sarcoma libraries, and supplies a lineage comparison and a descriptive normal-organ comparison.

Two composition facts about GSE28866 govern how far its normal arm can be read. The 27 normal
libraries are **17 adult and 10 fetal** (three bowel, three kidney, four lung), and the six organ
labels are unequally weighted: five breast, nine lung, one uterus, three colon, three bowel and six
kidney. A pooled median across that mixture is neither a population normal baseline nor a bound on
adult exposure in any organ, and the fetal component matters directly wherever oncofetal antigens are
discussed. The 32 non-EMC sarcoma libraries come from **30 specimens**, because the deposit's own
design names two tumours (ESS STT5520 and LMS STT516) with duplicate libraries and the reader retains
both columns; no test is computed on this cohort, so this is a weighting statement rather than an
inflated sample size.

The scale of the sequencing values is set by the deposit, not by this analysis. The retained GEO series
record states, verbatim, that "Expression data was normalized using the sequencing depth of each sample
by scaling the data using the mean value of each sample" and that "Data was further compressed to
reduce outliers by taking the square root of each value." The analysis reads those deposited values
directly and does not invert the transformation. Every sequencing value and ratio in this paper is
therefore a **deposited square-root-compressed summary score**, or a ratio of such summaries, and is not
a linear expression fold, a read density or a "times expression" statement. The reduction order actually
implemented is the **median across the libraries within an arm for each peak, then the median across
that gene's peaks**; the two orders do not generally commute, and squaring the reported aggregate ratios
would not recover a linear fold."""),

("F03-methods-value-kinds",
 """Sequencing figures are ratios of medians of per-peak medians and carry no test.""",
 """Sequencing figures are ratios of per-peak medians reduced across a gene's peaks, on the deposited
square-root-compressed score scale, and carry no test."""),

# ---- Methods: F06 controls -------------------------------------------------
("F06-methods-controls",
 """Three genes with known answers were read on the same platforms before any antigen. *NR4A3* must rise,
because its over-expression defines the disease; *ENO3*, a reported direct transactivation target of an
NR4A3 fusion [8], must rise; *MKI67* must be approximately flat, because EMC is slow-cycling and a large
proliferation difference would indicate a contrast driven by cellularity. That expectation was written
for GSE24369 and is met there; on GPL3290 the same gene is not flat, and the two readings are reported
separately in Supplementary Table S4.""",
 """Three reference genes were read on the same platforms. They are biological reference genes and reader
regression checks, not an independent known-answer calibration and not external validation, and this
paper does not treat them as licensing any other reading. *NR4A3* is expected to rise because its
over-expression defines the disease. *ENO3* is a reported direct transactivation target of an NR4A3
fusion [8] — the reported fusion in that work is TFG::NR4A3 rather than EWSR1::NR4A3, so it is not a
guarantee that every EMC-versus-comparator contrast must be positive — and its stored expectation
explicitly rests on ENO3 having **already been measured up in these same two series** in a cached
earlier subset, which makes it a consistency check across readers rather than an independent dataset.
*MKI67* was expected to be approximately flat on the reasoning that EMC is slow-cycling; that is a
motivated expectation and not a known answer, and non-significance cannot show the absence of a
cellularity confound. The MKI67 expectation was written for GSE24369 and is met there. On GPL3290 the
same gene reads *t* = 2.30 at about 5.5 degrees of freedom, which does **not** pass an ordinary
two-sided 0.05 Welch test; the older |*t*| >= 2 label that called it "not flat" is a readability label
and not the two-sided test used elsewhere in this paper. Both readings are reported in Supplementary
Table S4."""),

# ---- Methods: F05 statistics ----------------------------------------------
("F05-methods-statistics",
 """Every contrast on the 100-gene cross-platform board carries an exact two-sided *p*, a 95 % confidence
interval and a Benjamini-Hochberg *q* at alpha 0.05, corrected within platform across every gene that
produced a contrast on that platform. The two platforms are corrected separately because they are
different instruments with different comparator arms, and concordance requires both. Every count
reported below is taken from that corrected file rather than from a threshold on |*t*|; a |*t*| ≥ 2
verdict string in the underlying panel artifact is a readability label, more permissive than a 95 %
interval at these degrees of freedom, and is never a test. Under correction 24 of the 95 genes readable
on GPL6244 and 16 of the 78 readable on GPL3290 are significant. The median half-width of the 95 %
interval is 0.259 standard deviation units on GPL6244 and 0.957 on GPL3290, so the design's resolution
is governed by the wider platform and a null on GPL3290 excludes very little.

Three prespecified sensitivity analyses accompany the primary contrast.""",
 """Every contrast on the 100-gene cross-platform board carries a Welch two-sided *p*, an ordinary
pointwise 95 % confidence interval and a Benjamini-Hochberg *q* at alpha 0.05, corrected within platform
across every gene that produced a contrast on that platform. The *p* value is evaluated from a Student-t
distribution on Welch-Satterthwaite approximate degrees of freedom; it is a conventional calculation
under its assumptions and is not an exact distribution-free calibration, and the word "exact" is not
used of it anywhere in this paper. **The intervals are not multiplicity-adjusted.** Significance
throughout is decided by *q* >= 0.05 versus *q* < 0.05, which is a separate operation from whether an
ordinary interval contains zero: 14 non-significant GPL6244 rows and 8 non-significant GPL3290 rows have
ordinary intervals that exclude zero. KIT on GPL6244 is one such row, with an interval of 0.2433 to
2.4633 at *q* = 0.076; MCAM is another, at -0.5346 to -0.0413 with *q* = 0.080. A "(ns)" mark in any
table below therefore means *q* >= 0.05 and never that the printed interval contains zero. Every count
reported below is taken from the corrected file rather than from a threshold on |*t*|; a |*t*| >= 2
verdict string in the underlying panel artifact is a readability label, more permissive than a 95 %
interval at these degrees of freedom, and is never a test. Under correction 24 of the 95 genes readable
on GPL6244 and 16 of the 78 readable on GPL3290 are significant.

Resolution is reported as a **half-width** throughout. The median half-width of the ordinary 95 %
interval is 0.259 standard deviation units on GPL6244 and 0.957 on GPL3290, so the corresponding full
widths are about 0.52 and 1.90. The stored GPL3290 figure of 0.957 uses the upper middle of an
even-length list; the conventional median half-width is 0.952475 and its full width 1.90495, a
difference of convention rather than of substance. A half-width describes the uncertainty around the
estimate, not an elevation measured from zero, and neither a median half-width nor the smallest
observed significant effect is a power analysis or an equivalence test. A wide interval on GPL3290
means the design resolves little there; it does not demonstrate absence.

Three recorded sensitivity analyses accompany the primary contrast. No dated pre-outcome specification
for them was identified in the material reviewed for this paper, so they are described as recorded and
conducted rather than as prespecified."""),

("F03-F05-methods-sensitivity-tail",
 """no test, and it is qualified by its own controls, since *ENO3* and *NR4A3* both read higher in pooled
skeletal muscle than in EMC. The 3'-end sequencing cohort carries no test anywhere in this study: its
figures are ratios of medians of per-peak medians at n = 4, and a ratio is a descriptive quantity, not a
significance statement.""",
 """no test, and it is qualified by its own controls, since *ENO3* and *NR4A3* both read higher in pooled
skeletal muscle than in EMC. The 3'-end sequencing cohort carries no test anywhere in this study: its
figures are ratios of deposited square-root-compressed summary scores, reduced per peak across libraries
and then across a gene's peaks, at n = 4 EMC libraries, and a ratio is a descriptive quantity on that
compressed scale, not a significance statement and not a fold change."""),

# ---- Methods: F11 verification statement ----------------------------------
("F11-methods-verification",
 """That is a check of
manuscript against artifact. It is not an independent reproduction of the pipeline that produced the
artifacts from their public sources, and no such reproduction is claimed.""",
 """That is a check of
manuscript against artifact. It is not an independent reproduction of the pipeline that produced the
artifacts from their public sources, and no such reproduction is claimed. What can and cannot be
recalculated offline is stated exactly under Data availability: the retained derived records support
recalculation of the reported contrasts, corrections and reductions, while the surrogate scan's complete
gene universe, its per-line observations and its rank-test *p* values, the full probe-annotation audit
trail for the arrays, and the original sequencing peak table are **not** in hand, so the results that
depend on those inputs are not independently reproducible from what is released."""),

# ---- Results: F01 stage-1 and the prior -----------------------------------
("F02-results-selectivity-absent",
 """Selectivity was absent for B7-H3/CD276 at q = 1.0, for EGFR, and for FAP at q = 0.156 (Table 1).""",
 """No significant selectivity flag was returned for B7-H3/CD276 at q = 1.0, for EGFR, or for FAP at
q = 0.156 (Table 1); each of those is a non-significant result under this one-sided rank test rather
than a demonstration that the antigen is not expressed."""),

("F01-results-prior-decisive",
 """The normal-tissue prior is the decisive filter. Among the nine selective classic antigens, none was
also classed RESTRICTED (Figure 1). Over the wider retained set the intersection is not empty but holds
one member: DLL3 is selectivity-significant at q = 0.0079 and classed RESTRICTED, and it is the only
antigen in these artifacts that is both (the classification semantics are in Supplementary Methods S3;
its tissue reading is in Table 3). Its selectivity rests on a small enrichment, +0.29 log2TPM,
with 11 % of class lines expressing it, and it is flat in EMC tumour tissue on both arrays (Table 3),
so it is a coherent output of the filter rather than a lead this study can promote.""",
 """The normal-tissue annotation narrows the historical list, and what it can support is bounded by what
it observed. Among the nine selectivity-flagged classic antigens, none carries a stored RESTRICTED
label. Over the wider retained set the **stored-label intersection** is not empty but holds one member:
DLL3 is selectivity-flagged at q = 0.0079 and carries the RESTRICTED label, and it is the only antigen
in these artifacts that has both, over the records that carry such a label at all (the classification
semantics and their missing quantitative coverage are in Supplementary Methods S3; its tissue reading is
in Table 3). Six of the 18 flagged antigens have no normal-tissue record, so this intersection is not an
adjudication of the wider biological set. Because the quantitative tissue and blood fields are null for
every classified record and the vital-tissue branch never inspected an expression level (Methods), a
RESTRICTED label here is a historical category assignment and not a demonstrated clean normal-tissue
window. DLL3's flag rests on a small enrichment, +0.29 log2TPM, with 11 % of class lines expressing it,
and it is non-significant in EMC tumour tissue on both arrays (Table 3), so it is a coherent output of
the heuristic rather than a lead this study can promote."""),

("F01-results-classic-fails",
 """Within the classic subset each selective candidate fails the filter for an identifiable reason.
NCAM1/CD56 sits on natural killer cells and neural tissue, carrying a fratricide risk for cell products
and a circulating compartment; the CD56 antibody-drug conjugate lorvotuzumab mertansine was clinically
developed and discontinued [9,10]. CDH11 is broadly expressed in normal fibroblasts, synovium and bone,
and its high cross-cancer enrichment is the mesenchymal-versus-epithelial artefact described above.
B7-H3, EGFR and FAP are non-selective or broad; FGFR1, MCAM and EPHB4 carry liabilities on this prior.
Two classic antigens carry a restricted prior without selectivity: B4GALNT1, the GD2 synthase, and
ALCAM. Whether EMC expresses GD2 is not measured by anything in this study.""",
 """Within the classic subset each selectivity-flagged candidate carries a non-RESTRICTED label, and the
narrative reason for each is stated as background rather than as a measurement made here. NCAM1/CD56
sits on natural killer cells and neural tissue, which is a fratricide consideration for cell products
and a circulating compartment; the CD56 antibody-drug conjugate lorvotuzumab mertansine was studied in
a phase I and a phase 1/2 trial [9,10], and no retained source in this work establishes the status of
that programme, so no statement about its discontinuation is made. CDH11 is broadly expressed in normal
fibroblasts, synovium and bone, and its high cross-cancer enrichment is the mesenchymal-versus-epithelial
property described above. B7-H3, EGFR and FAP carry no significant selectivity flag or a broad label;
FGFR1, MCAM and EPHB4 carry liability labels from the heuristic, which as set out in Methods are
category assignments from blood and distribution fields rather than measured vital-tissue exposure. Two
classic antigens carry a RESTRICTED label without a selectivity flag: B4GALNT1, the GD2 synthase, and
ALCAM — both with a "Detected in many" distribution, which is one of the places the heuristic departs
from its own written rule. Whether EMC expresses GD2 is not measured by anything in this study."""),

# ---- Results: F07 CSPG4 scope ---------------------------------------------
("F07-results-cspg4-scan",
 """CSPG4 is a separate case and is often described inaccurately, so it is stated precisely here. CSPG4 has
no per-gene row in the **selectivity scan**, so it could not enter a selective-and-restricted
intersection at all; that is a measured coverage gap in the ranking instrument.""",
 """CSPG4 is a separate case and is often described inaccurately, so it is stated precisely here. CSPG4 has
**no retained selectivity result** — no per-gene row in the retained selected output of the selectivity
scan — so it could not enter a selective-and-restricted intersection at all. Because the complete
scanned gene list was never written to the artifact, absence from the retained selected rows does not
establish that the scan never evaluated it; the supported state is "no retained selectivity result",
not "never evaluated"."""),

# ---- Results: F02 eligibility split ---------------------------------------
("F02-F07-results-transfer",
 """The claim tested here is about the whole surrogate-selective set, so the whole set is reported. Of the
18 selectivity-significant actionable antigens, 13 carry a row on the 100-gene cross-platform board and
five — ALK, ENPP1, FGFR4, SLC34A2 and STEAP1 — were never placed on that board and therefore have no
EMC-tissue reading in this study at all. Their status is unmeasured, not negative. Of the 13 that are
measured, none is concordantly higher in EMC than in comparator sarcomas on both arrays under
within-platform correction, and two, FGFR1 and PTK7, are concordantly lower on both (Table 3).""",
 """The comparison reported here is an exploratory cross-context one, and the whole flagged set is
reported so the eligibility is visible. Of the 18 selectivity-flagged actionable antigens, **ten carry
contrasts on both arrays, three (CD248, GPC2, ROR1) on one array only, and five — ALK, ENPP1, FGFR4,
SLC34A2 and STEAP1 — were never placed on the 100-gene board** and therefore have no EMC-tissue reading
in this study at all. Their status is unmeasured, not negative. The operational rule used throughout is
that a gene counts as concordant only if it is significant in the same direction on both platforms after
within-platform correction; only the ten with two contrasts can satisfy it. **Zero of those ten** are
significantly higher in EMC than in comparator sarcomas on both arrays, and two, FGFR1 and PTK7, are
significantly lower on both (Table 3). These counts are conditional on that rule, on these comparator
arms and on this study's resolution; they are not a measurement of how well the surrogate ranking
transfers, because the two instruments compare different groups in different compartments and no
transfer or ranking estimand was defined or evaluated anywhere in this work."""),

("F02-F07-results-individual-states",
 """The individual states behind that count are worth separating, because several rows are directional
without being significant. CDH11 is significantly lower on GPL3290 (*q* = 0.034) while its GPL6244
estimate is positive and does not survive correction (*q* = 0.055). PDGFRB and ROR1 are significantly
lower on GPL6244 alone. CD248 and GPC2 are readable on one platform only. KIT, NCAM1, MCAM, EPHB4,
PDGFRA and DLL3 are flat on both, which under this correction means that neither platform's interval
excludes zero and not that the antigen is absent: on GPL3290 the median 95 % interval is nearly one
standard deviation wide, so a flat row there is compatible with a substantial difference.""",
 """The individual states behind that count are worth separating, because several rows are directional
without being significant. CDH11 is significantly lower on GPL3290 (*q* = 0.034) while its GPL6244
estimate is positive and does not survive correction (*q* = 0.055, ordinary interval 0.069 to 0.566,
which excludes zero — a *q* decision, not an interval containing zero). PDGFRB is significantly lower on
GPL6244 and non-significant on GPL3290; ROR1 is significantly lower on the single platform that reads
it. CD248, GPC2 and ROR1 are readable on one platform only. KIT, NCAM1, MCAM, EPHB4, PDGFRA and DLL3 are
non-significant on both, which means *q* >= 0.05 on each platform and not that the antigen is absent: on
GPL3290 the median half-width of the ordinary 95 % interval is 0.957 standard deviation units, so a
non-significant row there is compatible with a substantial difference in either direction."""),

("F02-results-three-qualifications",
 """Three qualifications apply to Table 3. It does not refute the surrogate, which asked a different
question, in monoculture, and answered it correctly. A flat or single-platform row does not demonstrate
that an antigen is absent. And the earlier statement in this programme's drafts that "the surrogate's
negatives transferred and its positives did not" is withdrawn: the corrected table does not support a
directional asymmetry between the surrogate's positives and its negatives, because the surrogate's
negatives are not concordantly reproduced either.""",
 """Four qualifications apply to Table 3. It does not refute the surrogate, which asked a different
question, in monoculture, and answered it correctly. A non-significant or single-platform row does not
demonstrate that an antigen is absent. The table is a comparison of two differently designed contrasts
and not a validation exercise, so "did not meet the two-platform rule" is the only claim it carries and
"not reproduced" is not used as a synonym for measured biological failure. And the earlier statement in
this programme's drafts that "the surrogate's negatives transferred and its positives did not" is
withdrawn: the corrected table does not support a directional asymmetry between the surrogate's
positives and its negatives, because the surrogate's negatives do not meet the rule either."""),

# ---- Results: route-named / panels: F10, F04, F09 -------------------------
("F02-results-route-panel-none",
 """Eleven genes make up the panel of therapeutic addresses named by candidate surface-directed routes for
this disease, assembled from the addresses those routes name plus two coverage corrections, and none of
the eleven is concordantly elevated in EMC tumour tissue under correction (Table 4). CD248 and CD276
have negative, non-significant estimates on the one platform that reads them; FAP, PRAME, ALPP and MSLN
are flat on both; SSTR2 is readable on one platform only; and CSPG4, GPC3, L1CAM and CDH17 move on one
platform and are flat on the other.""",
 """Eleven genes make up the panel of therapeutic addresses named by candidate surface-directed routes for
this disease, assembled from the addresses those routes name plus two coverage corrections, and none of
the eleven meets the two-platform upward rule in EMC tumour tissue under correction (Table 4). CD248 and
CD276 have negative, non-significant estimates on the one platform that reads them; FAP, PRAME, ALPP and
MSLN are non-significant on both; SSTR2 is readable on one platform only; and CSPG4, GPC3, L1CAM and
CDH17 are significant on one platform and non-significant on the other. None of that is a statement
about protein on an EMC cell surface, and none of it rejects a therapeutic route."""),

("F04-results-alcam-exposure",
 """On the exposure axis ALCAM's EMC median in the sequencing cohort, 0.578, sits below the normal-organ
median of 0.631 while remaining above the other-sarcoma median of 0.377. That cohort carries no test,
so these are descriptive ratios at n = 4 on two peaks and not a demonstration of equivalence with
normal organs. The two normal-tissue instruments in this study point different ways: the Human Protein
Atlas prior classes ALCAM RESTRICTED (tissue enriched, detected in many, immune-cell enhanced), while
the sequencing normal arm places its EMC median marginally below the normal-organ median. Neither
instrument measures protein, and the disagreement is not resolved here.""",
 """In the sequencing cohort ALCAM's EMC summary score, 0.578, sits below the pooled normal-organ score of
0.631 while remaining above the other-sarcoma score of 0.377, all on the deposited
square-root-compressed scale. That cohort carries no test, so these are descriptive ratios at n = 4 EMC
libraries on two peaks, against a pooled panel that is 17 adult and 10 fetal libraries with unequal
organ weighting; they are not a demonstration of equivalence with normal organs, not an adult
normal-exposure estimate and not a safety statement. The two records say **different things about
different quantities** and are not a validation test of one another: the stored heuristic label
(tissue enriched, detected in many, immune-cell enhanced, verdict RESTRICTED) is a category assignment
over records with null quantitative fields, while the sequencing figure is a tumour-to-pooled-normal
ratio of compressed scores. A gene can carry a restricted category label and still sit below a pooled
normal median, and the converse, without either reading being wrong; the earlier presentation of this
as an instrument disagreement or a failed normal-window validation is withdrawn."""),

("F09-results-cd248-cd276-fap",
 """Those ratios are descriptive, carry no test, and are not evidence that CD276 is elevated; the
stored FLAT label attached to the 1.42 ratio is a banding rule applied to a ratio, not a significance
test. Taken together the rows describe an antigen that is expressed and non-discriminating on the array
that reads it, and they do not establish that B7-H3 is lower in EMC than in comparator sarcomas. FAP is
flat, and the comparator arm is why that matters: GSE24369
compares EMC with desmoid fibromatosis and fibrosarcoma, fibroblastic lesions in which FAP is expected
to be high, and EMC itself sits at the 88th array percentile, so this is not a reading that EMC lacks
FAP.""",
 """Those ratios are descriptive, on the compressed score scale, carry no test, and are not evidence that
CD276 is elevated; the stored FLAT label attached to the 1.42 ratio is a banding rule applied to a
ratio, not a significance test. Taken together the rows describe an antigen whose single readable array
contrast is negative and non-significant, and they do not establish that B7-H3 is lower in EMC than in
comparator sarcomas, nor that it is present or absent on any cell surface. FAP is non-significant on
both arrays, and the comparator arm is why that matters: GSE24369 compares EMC with desmoid fibromatosis
and myxofibrosarcoma, fibroblastic lesions in which FAP is expected to be high, and EMC itself sits at
the 88th percentile of that array's own probe distribution, so this is not a reading that EMC lacks
FAP."""),

("F09-results-prame-floor",
 """PRAME reads at the floor of every readable cohort:
30th array percentile on GPL6244 with Δ near zero, 11th percentile of log-ratios on GPL3290 where its
nominally positive Δ is flat at |*t*| = 1.43, and a sequencing EMC median of 0.102 against an
other-sarcoma median of 0.194, on a single peak.""",
 """PRAME reads low in every readable cohort, on rank rather than on any calibrated detection limit:
the 30th percentile of the GPL6244 probe distribution with Δ near zero, the 11th percentile of GPL3290
log-ratios where its nominally positive Δ is non-significant at |*t*| = 1.43, and a sequencing EMC
summary score of 0.102 against an other-sarcoma score of 0.194 on a single peak. A percentile is a rank
across probes and not an assay limit of detection, so none of these readings shows that PRAME transcript
is absent."""),

("F10-results-hla-panel",
 """The precondition for the two human-leukocyte-antigen-directed routes points the wrong way. The
12-gene antigen-presentation panel reads lower in EMC than in comparator sarcomas on GPL6244
(Δ = −0.216, *t* = −2.90, *p* = 0.022, 12 of 12 readable) and has a negative estimate on GPL3290
(Δ = −0.228, *t* = −0.84, *p* = 0.433, 11 of 12). The second is not significant on any reading, and the
panel is a precondition rather than a target, but a T-cell-receptor-directed route needs class-I
presentation.""",
 """One exploratory panel bears on the two human-leukocyte-antigen-directed routes, and it is reported as
exploratory. The 12-gene antigen-presentation composite is lower in EMC than in comparator sarcomas on
GPL6244 (Δ = −0.216, *t* = −2.90, *p* = 0.022, 12 of 12 readable) and has a negative, non-significant
estimate on GPL3290 (Δ = −0.228, *t* = −0.84, *p* = 0.433, 11 of 12). Panel *p* values are **not**
entered into any multiplicity correction: the 17 available panel tests across the nine curated panels are
uncorrected and exploratory (Supplementary Table S5). The panel is a repository-curated transcript
composite of mixed function, including the regulator CIITA, and not a measurement of surface
peptide-HLA. A reduced composite on one platform without panel multiplicity control does not establish
defective class-I presentation and does not show that a peptide-HLA-directed route would fail; it is a
hypothesis worth a direct measurement."""),

("F10-results-route-panel-coverage",
 """The panel-level score for the route-named addresses disagrees between platforms and is reported as such:
negative and not significant on GPL6244 (Δ = −0.0935, *t* = −1.66, *p* = 0.121, 11 of 11 readable) and
positive on GPL3290 (Δ = +0.599, *t* = 2.91, *p* = 0.025, 8 of 11). The three genes missing from the
GPL3290 score are CD248, CD276 and SSTR2, three of the four that read down or flat on GPL6244, so the
two panel scores are not computed over the same set and the disagreement is partly a coverage
artefact. The per-gene table is therefore the interpretable
presentation and the panel scores are not.""",
 """The exploratory panel score for the route-named addresses disagrees between platforms and is reported as
such: negative and not significant on GPL6244 (Δ = −0.0935, *t* = −1.66, *p* = 0.121, 11 of 11 readable)
and positive on GPL3290 (Δ = +0.599, *t* = 2.91, *p* = 0.025, 8 of 11), both uncorrected. The three genes
missing from the GPL3290 score are CD248, CD276 and SSTR2, three of the four reading down or
non-significant on GPL6244, so the two scores are **not computed over the same gene set**. That
difference in membership is a reason the two scores are not comparable; no matched-member comparison was
run, so it is not demonstrated to be the cause of the disagreement. The per-gene table is therefore the
interpretable presentation and the panel scores are not."""),

("F09-results-sstr2",
 """On GPL6244, SSTR2 sits at the 60th percentile of the array's own probe distribution with Δ = −0.042
(*t* = −0.40) against comparator sarcomas, so it is present, mid-distribution and indistinguishable from
the comparators. It is not readable on GPL3290, and the somatostatin-receptor family panel could not be
scored there at all, with 1 of 5 genes readable against a coverage floor of 0.50, so the artifact emits
no score. On GPL6244 the family panel is flat (Δ = −0.008, *t* = −0.20, *p* = 0.849). In the sequencing
cohort EMC sits at 1.54 times the normal-organ median and 1.37 times the other-sarcoma median, on two
peaks and n = 4; those are descriptive ratios with no test behind them.""",
 """On GPL6244, SSTR2 sits at the 60th percentile of the array's own probe distribution with Δ = −0.042
(*t* = −0.40) against comparator sarcomas: a mid-distribution rank with a small, non-significant
contrast, which is not a statement about absolute receptor level. It is not readable on GPL3290, and the
somatostatin-receptor family panel could not be scored there at all, with 1 of 5 genes readable against a
coverage floor of 0.50, so the artifact emits no score. On GPL6244 that exploratory, uncorrected family
panel is non-significant (Δ = −0.008, *t* = −0.20, *p* = 0.849). In the sequencing cohort EMC sits at
1.54 times the pooled normal-organ score and 1.37 times the other-sarcoma score, on two peaks and n = 4
libraries; those are descriptive ratios of compressed scores with no test behind them."""),

("F10-results-gd2",
 """The GD2 proxy B4GALNT1 is flat on GPL6244 (Δ = −0.069, *t* = −1.00, 49th array percentile) and not
readable on GPL3290, and the whole five-gene glycan-synthase panel is lower in EMC on both platforms
(Δ = −0.147, *t* = −4.96; Δ = −1.050, *t* = −3.44). GD2 is a glycolipid and B4GALNT1 is a synthase, so
this is a proxy for a proxy and cannot exclude the antigen.""",
 """The GD2 proxy B4GALNT1 is non-significant on GPL6244 (Δ = −0.069, *t* = −1.00, 49th array percentile)
and not readable on GPL3290, and the exploratory, uncorrected five-gene glycan-synthase panel is lower in
EMC on both platforms (Δ = −0.147, *t* = −4.96; Δ = −1.050, *t* = −3.44). GD2 is a glycolipid and
B4GALNT1 is a synthase, so this is a proxy for a proxy and cannot exclude the antigen."""),

# ---- Results: CSPG4 section, F03/F07 --------------------------------------
("F07-results-cspg4-section-head",
 """CSPG4 has no per-gene row in any committed artifact of the surrogate instrument, and whether it was ever
scanned is undecidable because the artifact stores gene counts rather than the gene list.""",
 """CSPG4 has no per-gene row in the retained selected output of the surrogate instrument, and whether it
was ever scanned is undecidable because the artifact stores gene counts rather than the gene list. It is
present in the normal-tissue annotation artifact, so "absent from the surrogate instrument's retained
selectivity rows" is the exact statement and "absent from every committed artifact" is not."""),

("F03-results-cspg4-values",
 """In EMC tissue CSPG4 is the largest absolute row in the sequencing deposit, with an EMC median of 8.730,
roughly five times the next-largest row in that panel (CD248, 1.767; the ratio is 4.94, and a previous
draft's "an order of magnitude" overstated it about twofold), 3.31 times the normal-organ median and
2.51 times the other-sarcoma median. Those are descriptive ratios and carry no test.""",
 """In EMC tissue CSPG4 is the largest row in the sequencing deposit on the deposited score scale, with an
EMC summary score of 8.730, roughly five times the next-largest row in that panel (CD248, 1.767; the
ratio is 4.94 on that scale, and a previous draft's "an order of magnitude" overstated it about
twofold), 3.31 times the pooled normal-organ score and 2.51 times the other-sarcoma score. Those are
descriptive ratios of square-root-compressed deposited summaries, carry no test, and are not linear
expression folds; squaring them would not recover one, because the transformation and the two-stage
median reduction do not commute."""),

("F03-results-cspg4-tail",
 """The sequencing row rests on one peak and n = 4, and the Human Protein Atlas
prior classifies CSPG4 as tissue-enhanced, that is detected broadly with a peak rather than restricted,
so its normal-tissue behaviour beyond those six organs is unaddressed. CSPG4 is therefore held open.""",
 """The sequencing row rests on one peak and 4 EMC libraries, and the normal-tissue heuristic labels CSPG4
tissue-enhanced, that is detected broadly with a peak rather than restricted, over a record whose
quantitative tissue field is null, so its normal-tissue behaviour is unaddressed both beyond and within
those six organ labels. CSPG4 is therefore held open."""),

# ---- Results: concordant genes, F09 ---------------------------------------
("F09-results-saturation",
 """Three considerations weaken that reading. The background is saturated: VCAN's EMC samples sit
at the 99.7th and 97.5th array percentiles against comparators at the 97.8th and 91.2nd, so the
separation is small on top of a signal that is high everywhere, and a matrix proteoglycan being abundant
in a myxoid tumour is expected rather than discriminating. These are largely secreted or
matrix-associated products rather than cell-surface addresses, so a versican or biglycan transcript is a
statement about what the tumour deposits rather than about what a binder would find on a cell. And bulk
archival tissue cannot deconvolve compartments, so a matrix or stromal signal may report the
compartment's presence rather than the tumour cell's.""",
 """Three considerations weaken that reading. VCAN's EMC samples sit at the 99.7th and 97.5th percentiles
of the array's own probe distribution against comparators at the 97.8th and 91.2nd, so the separation is
small on top of a rank that is high everywhere; those are ranks across probes and not evidence of
detector saturation, and a high rank does not make a significant between-group contrast
non-discriminating. VCAN and BGN carry extracellular-matrix annotations, so a versican or biglycan
transcript is more plausibly a statement about what the tissue deposits than about what a binder would
find on a cell; CD44 is a transmembrane receptor and is not collapsed into that description, and bulk
transcript data do not establish which cells deposited any protein compartment. And bulk archival tissue
is not deconvolved, so a matrix or stromal signal may report a compartment's presence rather than the
tumour cell's — a hypothesis these data cannot test."""),

("F09-results-four-explanations",
 """A single-cell or spatial EMC
dataset would discriminate the compartment explanation directly, and none is in hand.""",
 """A single-cell or spatial EMC dataset would bear directly on the compartment explanation, though one
such measurement would not discriminate all four, since the comparator, culture and platform
explanations concern the design rather than the compartment. None is in hand."""),

# ---- Results: instrument controls, F06 ------------------------------------
("F06-results-controls",
 """### Instrument controls

The tissue instrument reproduced its known answers (Supplementary Table S4).""",
 """### Reference genes and reader checks

The tissue instrument returned its expected directions for the reference genes (Supplementary Table S4).
These are biological reference genes and reader regression checks, not independent known-answer
calibration, and they do not license any other reading in this paper."""),

("F06-results-mki67",
 """*MKI67* was flat on GPL6244 (Δ = +0.129, *t* = 0.53, df 8.7), the
cohort its expectation was written for; on GPL3290 the same gene is not flat (Δ = +1.236, *t* = 2.30,
df 5.5), which is reported rather than folded into the control.""",
 """*MKI67* was non-significant on GPL6244 (Δ = +0.129, *t* = 0.53, df 8.7), the cohort its expectation was
written for; on GPL3290 its estimate is larger (Δ = +1.236, *t* = 2.30, df 5.5), which does not pass an
ordinary two-sided 0.05 Welch test at those degrees of freedom even though the older |*t*| >= 2 label
called it "not flat". It is reported rather than folded into the control, and neither reading shows the
presence or absence of a cellularity confound."""),

("F06-results-negative-controls",
 """On the exposure axis, four antigens
with no reason to be present in a soft-tissue sarcoma have EMC medians below normal tissue: GPC3 at
0.09 times, MSLN at 0.27 times, L1CAM at 0.33 times and CDH17 at 0.91 times, as untested ratios.""",
 """In the sequencing cohort, four biologically motivated reference antigens with no expected role in a
soft-tissue sarcoma have EMC scores below the pooled normal score: GPC3 at 0.09 times, MSLN at 0.27
times, L1CAM at 0.33 times and CDH17 at 0.91 times, as untested ratios of compressed scores. They are
reference genes chosen on biology, not demonstrated negatives for these EMC samples."""),

("F06-results-anchor-licence",
 """It is an anchor, not a comparator arm, and no normal-tissue claim rests on it. A
working control licenses reading the other rows and is not evidence for any of them.""",
 """It is an anchor, not a comparator arm, and no normal-tissue claim rests on it. A reference gene
behaving as expected is a consistency check on the reader; it does not license the other rows and is not
evidence for any of them."""),

# ---- Discussion: F02, F09, F12 --------------------------------------------
("F02-discussion-opening",
 """In-silico surface-target discovery for this disease does not deliver a clean target, and when its
output is checked against the disease's own tissue the leads largely do not reproduce. The
contribution is therefore an estimate of how far a lineage-surrogate surface ranking transfers to the
disease it was built for, rather than a target list. One mechanism is testable and is offered as an
explanation rather than a result: a cross-lineage selectivity test measures mesenchymal rather than
epithelial character, which is a property EMC shares with every comparator in the tissue cohorts, so it
cannot discriminate within them. The caution applies to every surrogate-based rare-tumour target list,
not only to this one.""",
 """This in-silico analysis does not deliver a clean target, and the historical priorities it inherited do
not meet the two-platform rule applied to the tissue cohorts. The contribution is the explicit
side-by-side comparison of two differently designed archival instruments and the limitations that
comparison exposes — not a target list, and not an estimate of how far a surrogate ranking transfers,
which would require a defined transfer task and estimand that this work does not have. One explanation
is offered as a hypothesis rather than a result: a cross-lineage selectivity test rewards mesenchymal
rather than epithelial character, which is a property EMC shares with every comparator in the tissue
cohorts, so it would not discriminate within them. As a methodological consideration this may be worth
weighing whenever a surrogate list is built for a rare tumour; it is not an empirically demonstrated
prescription for other studies."""),

("F02-F09-discussion-three-outputs",
 """taken together those readings remove the
transcriptomic case for treating it as the obvious first EMC address and do not establish that it is
low. The stromal panel's estimate is negative on both platforms without reaching significance on
either. PRAME reads at the floor of every readable cohort.""",
 """taken together those readings remove the
transcriptomic case for treating it as the obvious first EMC address and do not establish that it is
low, absent, or unsuitable. The exploratory stromal panel's estimate is negative on both platforms
without reaching significance on either. PRAME reads at a low rank in every readable cohort, which is a
rank and not a detection limit."""),

("F07-discussion-cspg4-never",
 """Third, a held-open lead with a stated defect: CSPG4,
which the original search never evaluated.""",
 """Third, a held-open lead with a stated defect: CSPG4, for which the surrogate stage retains no
selectivity result."""),

("F02-discussion-suffice",
 """A surrogate ranking plus a normal-tissue prior did not suffice to prioritise scarce validation effort
for this rare tumour, and the check that showed as much required no new data.""",
 """A surrogate ranking plus this normal-tissue heuristic did not, in this instance, produce priorities
that survived a different archival comparison, and making that visible required no new data. Whether a
surrogate ranking can prioritise validation effort for a rare tumour is not measured here."""),

("F09-F12-discussion-modality",
 """The modality axis carries its own gates. The abundant myxoid and chondroid extracellular matrix is a
diffusion and binding-site barrier to antibodies, adoptive cells and radioligands, and adult sarcoma has a poor record for cell products and engagers in cold,
immune-excluded tumours; a single reported EMC case describes exactly such an immunosuppressive
microenvironment [4]. The genes concordantly elevated in EMC tissue are largely the matrix itself, so the
compartment that most complicates delivery is also the compartment carrying most of the differential
signal.""",
 """The modality axis carries its own gates, and they are named here as considerations rather than as
results of this study. The abundant myxoid and chondroid extracellular matrix is a plausible diffusion
and binding-site barrier to antibodies, adoptive cells and radioligands; nothing in this work measures
that barrier, and no claim about the performance of any modality class is made, because no retained
source in this work supports one. A single reported EMC case describes an immunosuppressive
microenvironment [4], which is one case. Two of the three genes meeting the upward rule in EMC tissue
carry matrix annotations, so the compartment that plausibly complicates delivery may also be the one
carrying part of the differential signal — a hypothesis about compartment that bulk transcript data
cannot settle."""),

# ---- Limitations: F04, F05, F07, F11 --------------------------------------
("F02-limitations-opening",
 """The binding limitation of this work is no longer its comparator basis, which three EMC tissue cohorts
now replace. It is twofold.""",
 """The comparator basis remains a central limitation of this work and is not replaced by the three EMC
tissue cohorts: those cohorts introduce their own, different comparator arms, and the surrogate stage's
own comparator problem is unchanged. Two further limitations bind everything above."""),

("F04-limitations-normal-panel",
 """The 27 normal libraries
are a tissue panel rather than matched adjacent tissue, covering six organ types.""",
 """The 27 normal libraries are a mixed panel rather than matched adjacent tissue: 17 adult and 10 fetal
libraries across six unequally weighted organ labels, so their pooled median is not an adult
normal-organ baseline and bounds nothing about exposure. The 32 non-EMC sarcoma libraries come from 30
specimens, two of which contribute duplicate libraries."""),

("F05-limitations-resolution",
 """Multiple-testing correction is applied within platform and not across platforms, and the study's
resolution is limited by the wider platform: the median 95 % interval is 0.259 standard deviation units
on GPL6244 and 0.957 on GPL3290, so a null on GPL3290 excludes very little and every "flat" row there
should be read as uninformative rather than as an absence.""",
 """Multiple-testing correction is applied within platform and not across platforms. Each platform's
Benjamini-Hochberg family is internally consistent; intersecting two separately corrected lists gives an
operational concordance and **not** a set with a calibrated joint replicability false-discovery rate,
which was not estimated anywhere in this work. Panel-level scores are uncorrected and exploratory. The
study's resolution is limited by the wider platform: the median **half-width** of the ordinary 95 %
interval is 0.259 standard deviation units on GPL6244 and 0.957 on GPL3290 — full widths of about 0.52
and 1.90 — so a non-significant row on GPL3290 excludes very little and should be read as uninformative
rather than as an absence. Ordinary pointwise intervals are not multiplicity-adjusted, so a
non-significant *q* does not imply that the printed interval contains zero, and neither the median
half-width nor the smallest significant effect is a power or equivalence analysis."""),

("F07-F11-limitations-tail",
 """Five of the 18 selectivity-significant
antigens have no row on the tissue board at all and are unmeasured here. On the surrogate side, no
verified EMC observation enters it, the surrogate is lineage-generic, the scanned gene list was never
recorded, and the instrument has no stromal compartment.""",
 """Five of the 18 selectivity-flagged antigens have no row on the tissue board at all and are unmeasured
here, and three more carry only one platform's contrast. Six carry no normal-tissue record. These
missing-evidence states are distinct and are kept distinct throughout: no normal-tissue record; no
retained selectivity result; no row on the tissue board; a contrast excluded for insufficient comparator
observations; a measured but non-significant contrast; and a significant decrease. None of them is a low
or negative reading. On the surrogate side, no verified EMC observation enters it, the surrogate is
lineage-generic, the scanned gene list was never recorded — so absence from the retained selected output
is not proof that a gene was never evaluated — and the instrument has no stromal compartment. The
reproducibility limits in Data availability bind every result: the scan's complete universe, per-line
observations and *p* values, the full array probe-annotation audit trail, and the original sequencing
peak table are not in hand."""),

# ---- Conclusion: F02, F04 -------------------------------------------------
("F02-F04-conclusion",
 """This in-silico analysis does not deliver a clean EMC surface target, and when its output
is checked against the disease's own tumour tissue the leads largely do not reproduce. None of the
eleven therapeutic addresses named by candidate routes is concordantly elevated in EMC relative to
comparator sarcomas; of the 18 surrogate-selective antigens, the 13 that carry a tissue reading include
none that is concordantly elevated on both arrays and five carry no tissue reading at all; and ALCAM,
the antigen with the strongest positive tissue signal, is significant on one array only and shows no
separation from normal visceral organ tissue in the one cohort able to look, which carries no test.
What survives is a set of readings that lower priors without excluding antigens, a lineage marker whose
evidence is uneven across platforms, one held-open lead the original search never evaluated, and a
caution about surrogate-based target lists for rare tumours.""",
 """This in-silico analysis does not deliver a clean EMC surface target, and the historical priorities it
inherited do not meet this study's two-platform rule in the different comparisons the tissue cohorts
support. None of the eleven therapeutic addresses named by candidate routes meets that rule; of the 18
surrogate-flagged antigens, ten carry contrasts on both arrays and none of those meets the upward rule,
three carry one platform's contrast and five carry none at all; and ALCAM, the antigen with the largest
positive tissue estimate, is significant on one array only, with a positive non-significant estimate on
the other, and its EMC summary score sits marginally below a pooled, mixed adult-and-fetal normal-organ
score in the one untested cohort able to look — which bounds nothing about adult normal exposure. What
survives is a set of readings that lower priors without excluding antigens, a lineage marker whose
evidence is uneven across platforms, one held-open lead with no retained selectivity result, and a
methodological consideration about surrogate-based target lists for rare tumours."""),

("F09-conclusion-tail",
 """A single-cell or spatial EMC dataset
would be worth more than any of these individually, because it is the one measurement that discriminates
the four explanations for the disagreement between the two instruments.""",
 """A single-cell or spatial EMC dataset would bear on the compartment question more directly than any of
these; it would not by itself discriminate the comparator, culture and platform explanations for the
difference between the two instruments, and no single measurement here resolves all four."""),

# ---- Display items: captions ----------------------------------------------
("F01-table1-caption",
 """Enrichment is class mean minus rest mean, log2(TPM+1); *q* is the Benjamini-Hochberg-corrected
one-sided Mann-Whitney value; the verdict is the Human Protein Atlas window classification.""",
 """Enrichment is class mean minus rest mean, log2(TPM+1); *q* is the Benjamini-Hochberg-corrected
one-sided Mann-Whitney value. The verdict column is the **stored label of this programme's custom
category heuristic** over Human Protein Atlas fields, not a Human Protein Atlas tier and not a validated
window: the quantitative tissue and blood fields are null for all 45 classified records, so no verdict
here reflects a measured vital-tissue level (Methods; Supplementary Methods S3).""",),

("F07-table1-caption-notinscan",
 """carries no record for ALK, ENPP1, FGFR4, STEAP1, SLC34A2 or PDGFRA.""",
 """carries no record for ALK, ENPP1, FGFR4, STEAP1, SLC34A2 or PDGFRA. Of the 18 rows in this table, 15
carry a retained selectivity result; the three that do not are marked as having no retained selectivity
result, which is not evidence that they were never evaluated."""),

("F07-table1-rows-notevaluated",
 """| B4GALNT1 (GD2 synthase) | not in the scan output | not in the scan output | not evaluated | RESTRICTED |
| SSTR2 | not in the scan output | not in the scan output | not evaluated | ENHANCED_BROAD |
| CSPG4 | no per-gene row (coverage gap) | no per-gene row | not evaluated | ENHANCED_BROAD |""",
 """| B4GALNT1 (GD2 synthase) | no retained selectivity result | no retained selectivity result | no retained result | RESTRICTED (label) |
| SSTR2 | no retained selectivity result | no retained selectivity result | no retained result | ENHANCED_BROAD (label) |
| CSPG4 | no retained selectivity result (coverage gap) | no retained selectivity result | no retained result | ENHANCED_BROAD (label) |"""),

("F04-table2-sequencing-row",
 """| GSE28866 | 3'-end sequencing, read density | 4 | 27 normal-organ libraries and 32 non-EMC sarcoma libraries | exposure and lineage |""",
 """| GSE28866 | 3'-end sequencing, deposited square-root-compressed summary scores | 4 libraries | 27 normal-organ libraries (17 adult, 10 fetal; unequal organ weighting) and 32 non-EMC sarcoma libraries from 30 specimens | descriptive normal-organ comparison and lineage |"""),

("F05-F07-table3-caption",
 """z in standard deviation units of that array's probe distribution, with Welch *t*. The *q* column is the
Benjamini-Hochberg value corrected within platform across the 100-gene board at alpha 0.05; "(ns)" marks
a contrast whose 95 % interval includes zero after correction. Cross-platform states are the corrected
states. Five antigens were never placed on the cross-platform board and have no tissue reading in this
study; that is an absence of measurement and not a low reading, and the same holds for a row marked
"not readable" on one platform.""",
 """z in standard deviation units of that array's probe distribution, with Welch *t*. The *q* column is the
Benjamini-Hochberg value corrected within platform across the 100-gene board at alpha 0.05; "(ns)" marks
*q* >= 0.05 and **not** an interval containing zero — the intervals reported in this study are ordinary
pointwise 95 % intervals and are not multiplicity-adjusted, and 14 GPL6244 and 8 GPL3290 non-significant
rows have intervals that exclude zero. Cross-platform states are the corrected states. Ten of the 18
flagged antigens carry contrasts on both platforms, three on one platform only, and five were never
placed on the cross-platform board and have no tissue reading in this study; that is an absence of
measurement and not a low reading, and the same holds for a row marked "not readable" on one
platform."""),

("F03-F05-table4-caption",
 """tissue, with ALCAM added as the antigen no route names that carries the strongest positive tissue
signal. Array *q* values are Benjamini-Hochberg corrected within platform; "(ns)" marks a contrast
whose 95 % interval includes zero after correction. Sequencing columns are ratios of medians, carry no
test, and are descriptive: a ratio above or below 1 in that cohort is not a significance statement.""",
 """tissue, with ALCAM added as the antigen no route names that carries the largest positive tissue
estimate. Array *q* values are Benjamini-Hochberg corrected within platform; "(ns)" marks *q* >= 0.05
and not an interval containing zero. Sequencing columns are ratios of **deposited
square-root-compressed summary scores** (median across libraries per peak, then median across a gene's
peaks), carry no test, and are descriptive: they are not linear expression folds, and a ratio above or
below 1 in that cohort is not a significance statement. The normal column is a pooled panel of 17 adult
and 10 fetal libraries with unequal organ weighting and is not an adult exposure estimate."""),

("F03-table5-caption",
 """arrays and reach significance on one platform only, so they are classified as moved on one and flat on
the other; they are shown because withholding a positive estimate would be as misleading as promoting
it. Sequencing columns carry no test.""",
 """arrays and reach significance on one platform only, so they are classified as moved on one and flat on
the other; they are shown because withholding a positive estimate would be as misleading as promoting
it. "Concordantly elevated" is an operational two-platform rule, not a set with an estimated joint
replicability false-discovery rate. Sequencing columns are ratios of deposited square-root-compressed
summary scores and carry no test."""),

("F04-table4-normal-header",
 """| Address | GPL6244 Δ (*t*), *q*, EMC percentile | GPL3290 Δ (*t*), *q* | vs 27 normal organs | vs 32 other sarcomas | State |""",
 """| Address | GPL6244 Δ (*t*), *q*, EMC percentile | GPL3290 Δ (*t*), *q* | vs 27 pooled normal libraries (17 adult, 10 fetal) | vs 32 other-sarcoma libraries (30 specimens) | State |"""),

("F04-table5-normal-header",
 """| Gene | GPL6244 Δ (*t*), *q* | GPL3290 Δ (*t*), *q* | vs 27 normal organs | vs 32 other sarcomas | Corrected state |""",
 """| Gene | GPL6244 Δ (*t*), *q* | GPL3290 Δ (*t*), *q* | vs 27 pooled normal libraries (17 adult, 10 fetal) | vs 32 other-sarcoma libraries (30 specimens) | Corrected state |"""),

# ---- F08: omit Figure 1 ---------------------------------------------------
("F08-figure1-omitted",
 """**Figure 1.** Candidate surface antigens placed by cross-cancer selectivity against normal-tissue
window tier. The figure is drawn over the classic antigens of Table 1. A usable classic antigen would
sit in the selective and restricted quadrant, which is unpopulated for those antigens; no marker is
drawn inside it. Over the wider retained actionable set the quadrant is not empty — DLL3 occupies it
(Table 3) — and DLL3 is not among the antigens this figure plots. Antigens with no
selectivity value in the scan output are not placed on the selectivity axis, because a marker at
zero would assert a measured selectivity that was never obtained; they appear instead in the
separate hatched "NOT EVALUATED" band at the right of the figure, which carries no selectivity
scale. In the current artifacts that band holds B4GALNT1 (GD2 synthase) and SSTR2, both recorded in
Table 1 as not in the scan output and not evaluated. Rendered by `emc_surface_figure.py` to
`emc-surface-prioritization.png`. The figure renders the surrogate stage only; the EMC-tissue axis is
presented in Tables 3 to 5.""",
 """**Figure 1 is omitted from this version, deliberately and without replacement.** The previously
included prioritisation figure (`research/modalities/emc-surface-prioritization.png`, 1610 x 896,
SHA256 `130042b6afab8aea28874d37dd684cde96886ab25b488ab65b83dac391c439bd`) plotted 13 antigens and so
omitted five rows now in Table 1 (ALCAM, CD248, CSPG4, ERBB2, LRRC15) while its caption described it as
drawn over that table; it printed "clean window" and "target-worthy" inside the image, which the null
quantitative normal-tissue fields do not support; it carried a "NOT EVALUATED" band that asserts an
execution history the retained artifacts cannot establish; and its quadrant boundary used a positive
selectivity effect rather than the *q*-based decision used everywhere else in this paper. Those are
assertions printed in pixels, so a caption-only repair could not correct them, and no figure was
redrawn for this version: the original PNG and its provenance are retained unaltered in the repository
as historical bytes (Appendix A7). Tables 1 and 3 to 5 carry the descriptive content the figure
attempted."""),

("F08-figure1-call",
 """Among the nine selectivity-flagged classic antigens, none carries a stored RESTRICTED
label.""",
 """Among the nine selectivity-flagged classic antigens, none carries a stored RESTRICTED label."""),

# ---- Declarations: F11, F12 -----------------------------------------------
("F11-data-availability",
 """**Data availability.** All primary data are public. Gene-expression deposits: GSE24369 (GPL6244),
GSE4303 (GPL3290) and GSE28866 (3'-end sequencing, supplementary peak table
`GSE28866_36048_normalized_peaks_cancer_and_normal.txt.gz`). Annotation and reference resources:
UniProt, DepMap, Cellosaurus and the Human Protein Atlas. Derived per-gene values, per-sample values and
verbatim deposit annotations are committed as `emc-expression-panels.json` (`reads.read_8_SURFACE_ANTIGEN`,
`reads.control`, `gene_reads`) and `gse28866-tumour-vs-normal.json` (`per_gene.values`). Every exact
*p*, 95 % confidence interval, within-platform Benjamini-Hochberg *q*, corrected cross-platform state,
panel *p* and sensitivity analysis reported here is committed as `emc-tissue-read-statistics.json`. The
per-antigen lineage and exposure summaries are committed as `aso-delivery-antigen.json`. The surrogate
stage is committed as `emc-surfaceome-scan.json`, `emc-surface-normal-window.json` and
`surfaceome-instrument-limits.json`. The prior-art screen is committed as
`emc-prior-art-2026-08-09.json`.

**Code availability.** `emc_expression_panels.py`, `emc_surfaceome_scan.py`,
`emc_surface_normal_window.py`, `surfaceome_instrument_limits.py`, `emc_line_data_probe.py`,
`emc_gse4303_crosscheck.py` and `emc_surface_figure.py`.""",
 """**Data availability.** All primary data are public. Gene-expression deposits: GSE24369 (GPL6244; the
GEO summary record links the series to PMID 21536545), GSE4303 (GPL3290; PMID 15920699, cited as [7])
and GSE28866 (3'-end sequencing, supplementary peak table
`GSE28866_36048_normalized_peaks_cancer_and_normal.txt.gz`; PMID 22929540). Those deposits are prior
work by their depositors and are the originating sources for everything reanalysed here; the PubMed
identifiers are taken from the retained GEO summary record and no further bibliographic or full-text
detail of those articles was retrieved for this work. Annotation and reference resources: UniProt,
DepMap, Cellosaurus and the Human Protein Atlas.

Derived per-gene values and verbatim deposit annotations are committed as `emc-expression-panels.json`
(`reads.read_8_SURFACE_ANTIGEN`, `reads.control`, `gene_reads`), which retains per-sample derived gene
values, probe identifiers and sample labels for the arrays, and as `gse28866-tumour-vs-normal.json`
(`per_gene.values`), which retains **group-level peak summaries and not per-sample values** — an earlier
version of this statement described the sequencing artifact as carrying per-sample values and was
wrong. Every *p*, ordinary 95 % confidence interval, within-platform Benjamini-Hochberg *q*, corrected
cross-platform state, panel *p* and sensitivity analysis reported here is committed as
`emc-tissue-read-statistics.json`. The per-antigen lineage and normal-organ summaries are committed as
`aso-delivery-antigen.json`. The surrogate stage is committed as `emc-surfaceome-scan.json`,
`emc-surface-normal-window.json` and `surfaceome-instrument-limits.json`. The prior-art screen is
committed as `emc-prior-art-2026-08-09.json` with its full-text follow-up in
`emc-prior-art-fulltext-screen-2026-08-10.json`. A versioned, hash-manifested local packet of these exact
files and the scripts below is maintained with the repository. **No public immutable release locator
exists for it at the time of writing, and none is claimed.**

**What can and cannot be reproduced.** From the retained derived records a reader can recalculate
offline: every array contrast, interval and within-platform Benjamini-Hochberg decision reported here;
the cross-platform state assignments; the three sensitivity summaries; the panel scores; and the
sequencing reductions from the retained grouped summaries. A reader **cannot** reproduce, from anything
released here: the surrogate scan's rank-test *p* and *q* values, because the artifact retains selected
output rows rather than the complete scanned universe, its per-line observations or its full *p*-value
family; the array probe-to-symbol mapping as an audited chain, because the accession cache is a resolved
lookup rather than a complete platform-annotation audit trail with source versions and ambiguity
handling; or the sequencing values from their original public source, because the original peak table is
not retained here. No independent reproduction of any analysis from its original public source is
claimed. The original execution outputs are preserved unaltered; any later annotation correction is kept
separate from them and identified as such (Appendix A7).

**Code availability.** The statistics reported in this paper are generated by
`emc_tissue_read_statistics.py`, which consumes `emc-expression-panels.json` and
`emc-expression-panels-inputs.json` and depends on `accession-symbol-cache.json` for probe-to-symbol
resolution. The other producers are `emc_expression_panels.py`, `gse28866_tumour_vs_normal.py`,
`emc_surfaceome_scan.py`, `emc_surface_normal_window.py`, `surfaceome_instrument_limits.py`,
`emc_line_data_probe.py` and `emc_gse4303_crosscheck.py`. `emc_surface_figure.py` produced the omitted
Figure 1 and reads a mutable remote cache, so re-running it does not reproduce the retained image; it is
listed for provenance only."""),

# ---- Appendix A1: F13 -----------------------------------------------------
("F13-appendix-three-readouts",
 """**What resolved it.** Three independent readouts, recorded in""",
 """**What resolved it.** Three information sources — not three independent confirmations, since their
error mechanisms are related and none was independently validated — recorded in"""),

("F13-appendix-reading-of-absence",
 """   **present** with **2** calls, `AL158209.1--NEBL` and `VIM--RPS25`, and **neither names NR4A3, EWSR1,
   TAF15 or FUS**. ⭑ The model being *in* the file is what makes this a reading of absence rather than an
   absent reading.""",
 """   **present** with **2** calls, `AL158209.1--NEBL` and `VIM--RPS25`, and **neither names NR4A3, EWSR1,
   TAF15 or FUS**. ⭑ The model being *in* the file establishes that it was represented and that this
   filtered caller reported no qualifying call. ⚠ That is **no reported filtered fusion call**, not
   verified biological absence of a fusion: read coverage, caller sensitivity, the filter and transcript
   structure all remain relevant, and the Cellosaurus caution concerns an *EWSR1* fusion specifically
   while EMC has other recorded NR4A3 partners."""),
]

# ------------------------------------------------------------------ SI text
EDITS_SI = [

("SI-F02-purpose",
 """  Supplementary companion to emc-surface-target-landscape.md. Carries the material moved out of the
  5,000-word main body: full surfaceome and normal-tissue methods, the complete normal-tissue
  classification, the measured limits of the surrogate instrument, panel-level scores, the
  accession-bridge detail, the instrument controls and the extended limitations.""",
 """  Supplementary companion to emc-surface-target-landscape.md. Carries the material moved out of the
  5,000-word main body: full surfaceome and normal-tissue methods, the complete stored normal-tissue
  classification and its missing quantitative coverage, the measured limits of the surrogate instrument,
  exploratory panel-level scores, the accession-bridge detail, the reference-gene checks and the
  extended limitations."""),

("SI-F07-S1-universe",
 """The seed is therefore a small and largely redundant minority of the scanned set, and the scan is largely
though not strictly unbiased. Two consequences follow. An antigen can enter the ranking because it was
placed in the seed rather than because a topology annotation captured it, which is why the seed size
and overlap are reported above. And the scanned gene list itself was not written to the
output artifact, only the counts, which is the reason the CSPG4 coverage question in Note S3 is
undecidable rather than resolvable.""",
 """The seed is therefore a small and largely redundant minority of the scanned set, and the scan is largely
though not strictly unbiased. Three consequences follow. An antigen can enter the ranking because it was
placed in the seed rather than because a topology annotation captured it, which is why the seed size
and overlap are reported above. The scanned gene list itself was not written to the output artifact,
only the counts, which is the reason the CSPG4 coverage question in Note S3 is undecidable rather than
resolvable — and, more generally, why absence from the retained selected output rows is **not** evidence
that a gene was never evaluated. And the successive denominators are different quantities that are kept
separate throughout both documents: 2,826 source surface genes; 2,692 stated present in the expression
matrix and scanned; 47 curated retained actionable genes; 18 carrying the selectivity flag; and, in the
classic table of the main text, 18 rows of which 15 carry a retained selectivity result and 9 are
flagged. "Whole" always means the whole retained actionable set and never an exhaustive presentation of
the scan or an unbiased target universe."""),

("SI-F07-S2-class",
 """That gives 76 class members of which 45 carry expression data.""",
 """That gives 76 class members by annotation, of which **45 carry expression data and are the lines the
retained actionable rows are computed over**; 76 is a class-membership count and is not the number of
tested lines."""),

("SI-F06-S2-selfchecks",
 """Two self-checks were specified in advance. Housekeeping genes are excluded by construction, which is a
minimal sanity check rather than a validation. And CD276 recovers as broadly expressed across the panel,
which is the known answer for that antigen.""",
 """Two self-checks accompany the scan and are development checks rather than validation. Housekeeping
genes are excluded by construction, which is a minimal sanity check. And CD276 recovers as broadly
expressed across the panel, which matches the expectation for that antigen. No dated pre-outcome
specification for either check was identified in the material reviewed, so they are described as
recorded rather than as prespecified."""),

("SI-F01-S3-prior",
 """### S3. Normal-tissue prior and its classification semantics

Each antigen was queried against the Human Protein Atlas for RNA tissue specificity, RNA tissue
distribution, per-tissue nTPM, blood-cell specificity and subcellular location. The classification uses
Human Protein Atlas semantics rather than a threshold on expression:""",
 """### S3. The normal-tissue annotation heuristic, its declared rule, and what it actually observed

Each antigen was queried against the Human Protein Atlas for RNA tissue specificity, RNA tissue
distribution, per-tissue nTPM, blood-cell specificity and subcellular location. The classification is a
**custom category heuristic written for this programme**; its verdicts are not Human Protein Atlas tiers
and are reported throughout both documents as historical labels. Its declared rule was:"""),

("SI-F01-S3-vital-list",
 """The vital-tissue list applied was: heart, cerebral cortex, brain, cerebellum, hippocampus, amygdala,
basal ganglia, spinal cord, nerve, liver, lung, kidney, pancreas, colon, small intestine, duodenum,
stomach, bone marrow, skeletal muscle, smooth muscle and cardiac tissue.""",
 """The vital-tissue list applied was: heart, cerebral cortex, brain, cerebellum, hippocampus, amygdala,
basal ganglia, spinal cord, nerve, liver, lung, kidney, pancreas, colon, small intestine, duodenum,
stomach, bone marrow, skeletal muscle, smooth muscle and cardiac tissue.

⚠ **The vital-tissue branch never operated on any record in this study.** The quantitative
tissue-specific nTPM field is null for all 45 classified records, and so is the blood-specific nTPM
field; the implementation converts the missing tissue value to an empty string before searching it for
the names above, so no expression level was ever inspected. All nine VITAL_OR_IMMUNE_LIABILITY labels
therefore come from the blood-**category** branch alone. The "restricted distribution" conjunct of the
RESTRICTED rule is also not enforced: ALCAM, B4GALNT1 and GPC3 carry "Detected in many" and are
nonetheless labelled RESTRICTED. A verdict in this artifact is consequently a category assignment from
incompletely observed records. It is not a measurement of expression in any tissue, not evidence of
absence from a vital tissue, and not a therapeutic window; a non-null tissue-specific nTPM field would
not have been a per-tissue expression matrix either. Nothing was re-queried and no missing value was
imputed for this correction."""),

("SI-F01-S3-intersection",
 """The current artifact classifies 46 antigens. Forty-five carry a window verdict; the forty-sixth,
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
restricted and that immune expression is caught.""",
 """The current artifact classifies 46 antigens. Forty-five carry a window verdict; the forty-sixth,
ALPPL2, is a record the instrument discarded because the Human Protein Atlas search returned a
different gene (ALPG), so no verdict exists for the gene asked for. That is an instrument statement and
never a biological one. Eight antigens carry the RESTRICTED label: ALCAM, ALPP, B4GALNT1, CTAG1B, DLL3,
GPC3, MAGEA4 and PRAME. Intersecting that **stored-label** set with the 18 selectivity-flagged
actionable antigens of the surrogate scan leaves exactly one antigen, DLL3. That is an intersection of
stored labels over the records that carry them, and not a demonstration that DLL3 is absent from normal
tissue; six of the 18 flagged antigens (ALK, ENPP1, FGFR4, PDGFRA, SLC34A2, STEAP1) carry no record at
all, so the wider set is not exhaustively annotated.

Four controls accompany the run and all four returned the expected label: DLL3 and GPC3 returned
RESTRICTED; B2M returned a broad verdict; and CD3E returned VITAL_OR_IMMUNE_LIABILITY rather than
RESTRICTED. ⚠ These are **development checks on a heuristic tuned around them**, not an independent
calibration of what the labels mean clinically, and the CD3E claim previously made here is corrected:
CD3E is tissue-**enriched** in its record and reaches the immune branch, so it does not exercise the
tissue-enhanced branch. The rule additionally exempts weak immune enhancement, which is a choice made so
that familiar positive controls are not flagged."""),

("SI-F03-F04-S4-sequencing",
 """GSE28866 is 3'-end sequencing. Values are read densities at 3' peaks, summarised as medians of per-peak
medians within each arm. No test is computed on them, and the ratios reported in the main text are
ratios of those medians.""",
 """GSE28866 is 3'-end sequencing. The deposited values are **not** raw read densities: the retained GEO
series record states verbatim that "Expression data was normalized using the sequencing depth of each
sample by scaling the data using the mean value of each sample" and that "Data was further compressed to
reduce outliers by taking the square root of each value." The analysis reads those deposited values
directly and does not invert the transformation, so every value and ratio here is on a
square-root-compressed deposited-score scale and is not a linear expression fold. The reduction actually
implemented takes, for each peak, the **median across the libraries in an arm**, and then the **median
across that gene's peaks**; that order is what the main text's "medians of per-peak medians" describes.
The orders do not generally commute, and squaring an aggregate ratio does not recover a linear fold. No
test is computed on this cohort, and the retained artifact stores group-level summaries rather than
per-sample values.

The two arms also have composition limits that bind their interpretation. The 27 normal libraries are 17
adult and 10 fetal (three bowel, three kidney, four lung), with unequal organ weighting: five breast,
nine lung, one uterus, three colon, three bowel, six kidney. The 32 non-EMC sarcoma libraries come from
30 specimens, since the deposit's design names ESS STT5520 and LMS STT516 as duplicated and the reader
retains both columns. A pooled median across either arm is a descriptive summary of that specific
mixture and is not a population baseline, an adult normal-organ exposure estimate or a safety bound."""),

("SI-F12-S6-priorart",
 """A Europe PMC retrieval returned 322 EMC-linked records with 238 full-text files, hand-screened for
surfaceome, surface antigen, cell-surface protein, chimeric antigen receptor, radioligand, antibody-drug
conjugate and immunotherapy terms. Three EMC-specific records matched, none of them a systematic
surface-antigen map.""",
 """A Europe PMC retrieval returned 322 EMC-linked records with 237 retained text files plus an index file
— an earlier count of 238 included the index — screened for surfaceome, surface antigen, cell-surface
protein, chimeric antigen receptor, radioligand, antibody-drug conjugate and immunotherapy terms. Three
EMC-specific records matched, none of them a systematic surface-antigen map. The full-text follow-up
screen applies a narrower algorithmic rule than a systematic review: its antigen-near-EMC test is nested
inside a general surface/immunotherapy term condition and examines a limited antigen list, so the
retained files are a screening corpus and not 237 independently assessed papers."""),

("SI-F12-S6-tail",
 """The screen
matched titles and abstracts rather than full text, so an absence in it is evidence that nothing is
indexed on the pairing and is not evidence that no such work exists.""",
 """The initial screen matched titles and abstracts rather than full text. An absence in these screens is a
bounded retrieval outcome: it is not evidence that nothing is indexed on the pairing, that no such work
exists, or that the field lacked EMC surface-antigen information. No field-wide first, absence or
frequency claim is supported by them."""),

("SI-F05-S7-header",
 """Every contrast on the 100-gene cross-platform board carries an exact two-sided *p*, a 95 % confidence
interval and a Benjamini-Hochberg *q* at alpha 0.05, corrected **within platform** across every gene
that produced a contrast on that platform.""",
 """Every contrast on the 100-gene cross-platform board carries a Welch two-sided *p* evaluated from a
Student-t distribution on Welch-Satterthwaite approximate degrees of freedom — a conventional
calculation under its assumptions, not an exact distribution-free calibration — together with an
**ordinary pointwise, not multiplicity-adjusted** 95 % confidence interval and a Benjamini-Hochberg *q*
at alpha 0.05, corrected **within platform** across every gene that produced a contrast on that
platform."""),

("SI-F05-S7-resolution",
 """Resolution. Under correction, 24 of the 95 genes readable on GPL6244 and 16 of the 78 readable on
GPL3290 are significant. The median half-width of the 95 % interval is 0.259 standard deviation units on
GPL6244 and 0.957 on GPL3290, and the smallest significant absolute Δ is 0.06 and 0.658 respectively.
The half-width is the elevation a gene's own data cannot exclude, so on GPL3290 a flat row is
uninformative over a wide range and concordance across the two platforms is governed by the wider one.""",
 """Significance and intervals are separate operations. Non-significance means *q* >= 0.05; it does **not**
mean that the ordinary interval contains zero. Fourteen non-significant GPL6244 rows (ALPL, CD276, CD99,
CDH11, CSPG5, DCN, GPC1, KIT, LRRC15, LUM, MCAM, MMP14, MSLN, SDC4) and eight non-significant GPL3290
rows (AXL, CEACAM5, CSPG5, FOLR1, MMP14, ROR2, SSX1, THY1) have ordinary intervals that exclude zero.
Any "(ns)" mark in either document means *q* >= 0.05.

Resolution. Under correction, 24 of the 95 genes readable on GPL6244 and 16 of the 78 readable on
GPL3290 are significant. The median **half-width** of the ordinary 95 % interval is 0.259 standard
deviation units on GPL6244 and 0.957 on GPL3290 — full widths of about 0.5173 and 1.90495 — and the
smallest significant absolute Δ is 0.06 and 0.658 respectively. The stored GPL3290 half-width of 0.9571
takes the upper middle of an even-length list; the conventional median half-width is 0.952475. That is a
convention difference and not a substantive one. A half-width describes uncertainty around the estimate
and is **not** an elevation measured from zero, correcting an earlier statement in this section that
called it "the elevation a gene's own data cannot exclude". Neither a median half-width nor the smallest
observed significant effect is a power calculation or an equivalence test. On GPL3290 a non-significant
row is uninformative over a wide range, and the two-platform rule is governed by the wider platform."""),

("SI-F05-S7-sensitivity-label",
 """Sensitivity analysis 1, reference-matched GPL3290.""",
 """The three sensitivity analyses below are recorded and conducted; no dated pre-outcome specification for
them was identified in the material reviewed, so they are not described as prespecified.

Sensitivity analysis 1, reference-matched GPL3290."""),

("SI-F01-tableS2-caption",
 """**Table S2.** Normal-tissue classification for every antigen either document names that the artifact
classifies, plus the four controls.""",
 """**Table S2.** Stored normal-tissue **labels** — the output of the custom category heuristic described in
Supplementary Methods S3 — for every antigen either document names that the artifact classifies, plus the
four controls. ⚠ The quantitative tissue-specific and blood-specific nTPM fields are null for all 45
classified records, so no row below reports a measured expression level, no row establishes absence from
a vital tissue, and the three columns before the verdict are categorical annotation fields."""),

("SI-F04-tableS2-alcam-note",
 """Note on ALCAM. The prior classes it RESTRICTED, while the exposure axis of the sequencing cohort places
its EMC median marginally below the normal-organ median as an untested ratio. The two normal-tissue
instruments point different ways for this antigen, neither measures protein, and the disagreement is not
resolved in either document.""",
 """Note on ALCAM. The heuristic stores the label RESTRICTED for it, on a record whose quantitative fields
are null and whose distribution field reads "Detected in many"; separately, the sequencing cohort places
its EMC summary score marginally below the pooled normal-organ score as an untested ratio of compressed
scores. ⚠ These are **different quantities and not a validation test of one another**: a categorical
restriction label and a tumour-to-pooled-normal ratio can differ without either being wrong, and a gene
can be restricted to some normal tissues yet sit below their pooled median. The earlier framing of this
as two instruments pointing different ways, or as a failed normal-window validation, is withdrawn.
Neither measures protein."""),

("SI-F06-tableS4-caption",
 """**Table S4.** Tissue-instrument controls.""",
 """**Table S4.** Tissue-instrument reference genes. These are biological reference genes and reader
regression checks, not independent known-answer calibration and not external validation."""),

("SI-F06-tableS4-note",
 """The MKI67 expectation was written for GSE24369, where it is met. The GPL3290 reading is not flat, and it
is reported rather than folded into the control: a proliferation difference on that platform is one more
reason its contrasts are read with the wide intervals recorded in Supplementary Methods S7. A working
control licenses reading the other rows and is not evidence for any of them.""",
 """The MKI67 expectation was written for GSE24369, where it is met. ⚠ It is a motivated expectation and not
a known answer: slow clinical behaviour does not imply equal proliferation relative to these particular
comparator groups, and a non-significant result cannot show the absence of a cellularity confound. The
GPL3290 reading (*t* = 2.30 at about 5.5 df) does **not** pass an ordinary two-sided 0.05 Welch test; the
older |*t*| >= 2 label that called it "not flat" is a readability label rather than the test used
elsewhere. ⚠ The ENO3 expectation rests on ENO3 having already been measured up in these same two series
in a cached earlier subset, so it is a regression check across readers rather than an independent
dataset, and the transactivation result it cites concerns TFG::NR4A3. A reference gene behaving as
expected is a consistency check on the reader; it does not license the other rows and is not evidence for
any of them."""),

("SI-F10-tableS5-caption",
 """**Table S5.** Panel-level scores. Δ is the panel mean z difference; coverage is readable members divided
by requested members. Panels below the floor emit no score. Panel *p* is the exact two-sided value for
that panel's own score; panels are not entered into the gene-level Benjamini-Hochberg correction, so
these are uncorrected and are read as such.""",
 """**Table S5.** Exploratory panel-level scores. Δ is the panel mean z difference; coverage is readable
members divided by requested members. Panels below the floor emit no score. Panel *p* is the Welch
two-sided value for that panel's own score. ⚠ **The 17 available panel tests below are exploratory and
uncorrected**: panels are not entered into the gene-level Benjamini-Hochberg correction and no
panel-level multiplicity control was applied. Membership and coverage differ between the platforms, so a
same-named panel can be a different gene composite on each; no matched-member comparison was run. No
functional conclusion — about class-I presentation, a peptide-HLA route, or a demonstrated coverage
artefact — follows from any row."""),

("SI-F10-tableS5-note",
 """The route-named panel disagrees between platforms, and the three genes missing from the GPL3290 score are
CD248, CD276 and SSTR2, which are three of the four reading down or flat on GPL6244. The two scores are
therefore not computed over the same set and the disagreement is partly a coverage artefact. The per-gene
tables in the main text are the interpretable presentation of that panel.""",
 """The route-named panel disagrees between platforms, and the three genes missing from the GPL3290 score are
CD248, CD276 and SSTR2, which are three of the four reading down or non-significant on GPL6244. The two
scores are therefore not computed over the same gene set, which is a reason they are not comparable; that
difference has not been shown to cause the disagreement, because no matched-member comparison was run.
The per-gene tables in the main text are the interpretable presentation of that panel."""),

("SI-F03-tableS6-caption",
 """**Table S6.** Exposure-axis values from the 3'-end sequencing cohort. Medians of per-peak medians;
4 EMC libraries, 27 normal-organ libraries, 32 non-EMC sarcoma libraries.""",
 """**Table S6.** Descriptive summary scores from the 3'-end sequencing cohort, on the deposit's
depth-normalised, **square-root-compressed** scale. Each value is the median across the libraries in an
arm for each peak, reduced by the median across a gene's peaks; they are not linear abundances and no
test is computed. Arms: 4 EMC libraries; 27 normal-organ libraries (17 adult, 10 fetal, unequally
weighted across six organ labels); 32 non-EMC sarcoma libraries from 30 specimens."""),

("SI-F06-tableS6-note",
 """GPC3, MSLN, L1CAM and CDH17 are the exposure-axis negative controls: four antigens with no reason to be
present in a soft-tissue sarcoma, all of which read below normal tissue.""",
 """GPC3, MSLN, L1CAM and CDH17 are biologically motivated reference antigens with no expected role in a
soft-tissue sarcoma, and all four read below the pooled normal score. They were chosen on biology and
are not demonstrated negatives for these samples."""),

("SI-F05-tableS7-note",
 """The last two rows are statements about the instrument. Nothing in either document treats a gene in them
as low or absent. FLAT_ON_BOTH is likewise a classification and not a finding of absence: on GPL3290 the
median 95 % interval is 0.957 standard deviation units wide, so a flat row there is compatible with a
substantial difference in either direction.""",
 """The last two rows are statements about the instrument. Nothing in either document treats a gene in them
as low or absent. FLAT_ON_BOTH is likewise a classification, meaning *q* >= 0.05 on both platforms, and
not a finding of absence: on GPL3290 the median **half-width** of the ordinary 95 % interval is 0.957
standard deviation units, a full width of about 1.90, so such a row is compatible with a substantial
difference in either direction. ⚠ The three-gene CONCORDANT_UP_ON_BOTH intersection is an **operational**
intersection of two separately corrected per-platform families; no joint replicability false-discovery
rate was estimated for it, and none is claimed."""),

("SI-F07-noteS1-L4",
 """**L4, the CSPG4 coverage gap.** CSPG4 is not in the 47-antigen seed, has no row in the scan's top
candidates, no row among its actionable antigens and no row in the single-line profile.""",
 """**L4, the CSPG4 coverage gap.** CSPG4 is not in the 47-antigen seed, and has no row in the scan's
retained top candidates, none among its retained actionable antigens and none in the single-line
profile. That is the exact state — **no retained selectivity result** — and not a demonstration that the
scan never evaluated it."""),

("SI-F09-noteS1-L5",
 """The second is about identity, not compartment: the only class line carrying the disease subtype
annotation is ACH-001519, whose EMC identity the curated record contradicts, so that line supplies no
disease observation of any antigen. Its FAP row reads 0.0 log2TPM, which is
a single value from a line that is not read as disease evidence.""",
 """The second is about identity, not compartment: the only class line carrying the disease subtype
annotation is ACH-001519, whose EMC identity the curated record contradicts, so that line supplies no
disease observation of any antigen. Its FAP row reads 0.0 log2TPM, which is a single value from a line
that is not read as disease evidence. ⚠ Neither limit shows that the culture contains no FAP-expressing
cells: the FAP row across the class has 16 % of lines above the expression threshold and 56 % detectable,
and LRRC15's expressed fraction of 0.0 means that no line passed the chosen threshold rather than that
the transcript is literally absent."""),

("SI-F09-noteS4-compartment",
 """The compartment explanation is the one a single measurement could test. A single-cell or spatial dataset
for this disease separates the tumour-cell compartment from the stromal one and would settle it directly.
None is in hand, and neither document selects among the four explanations in its absence.""",
 """The compartment explanation is the one a single measurement could most directly address: a single-cell
or spatial dataset for this disease separates the tumour-cell compartment from the stromal one. ⚠ It
would not by itself discriminate the other three, which concern the comparator groups, the culture system
and the measurement platform rather than the compartment. None is in hand, and neither document selects
among the four explanations in its absence."""),

("SI-F04-noteS5-normal-arm",
 """**The normal arm is a tissue panel.** Bowel, breast, colon, kidney, lung and uterus contain almost no soft
tissue, and the libraries are not matched adjacent tissue. The arm is an on-target off-tumour exposure
axis and not a lineage-specificity axis, and it covers six organ types.""",
 """**The normal arm is a mixed tissue panel.** Bowel, breast, colon, kidney, lung and uterus contain almost
no soft tissue, and the libraries are not matched adjacent tissue. The 27 libraries are 17 adult and 10
fetal, unequally weighted across the six organ labels (five breast, nine lung, one uterus, three colon,
three bowel, six kidney). It supports a descriptive tumour-versus-pooled-normal comparison for this
specific mixture, and it is not a lineage-specificity axis, not an adult normal-organ baseline and not a
bound on exposure anywhere. The fetal component is directly relevant wherever an oncofetal antigen is
discussed."""),

("SI-F07-noteS5-comparators",
 """**Different comparator arms.** One lineage cohort compares against low-grade fibromyxoid sarcoma, desmoid
fibromatosis and fibrosarcoma; the other against dermatofibrosarcoma protuberans and gastrointestinal
stromal tumour, 6 samples in total.""",
 """**Different comparator arms.** One lineage cohort compares against low-grade fibromyxoid sarcoma, desmoid
fibromatosis and myxofibrosarcoma; the other against dermatofibrosarcoma protuberans and gastrointestinal
stromal tumour, 6 samples in total. The 32 non-EMC sarcoma libraries of the sequencing cohort come from
30 specimens, with two contributing duplicate libraries."""),

("SI-F05-F10-noteS5-correction",
 """The correction is not applied across the two platforms, and panel-level
scores are not entered into it. The study's resolution is the binding limit rather than the correction:
the median 95 % interval is 0.957 standard deviation units wide on GPL3290, so a null there excludes
very little and a concordance requirement is governed by that platform.""",
 """The correction is not applied across the two platforms, and panel-level scores are not entered into it,
so the 17 available panel tests are exploratory and uncorrected. Intersecting the two separately
corrected per-platform families gives an operational concordance; a joint replicability false-discovery
rate was not estimated and is not claimed. The study's resolution is the binding limit rather than the
correction: the median **half-width** of the ordinary 95 % interval is 0.957 standard deviation units on
GPL3290, a full width of about 1.90, so a non-significant row there excludes very little and the
two-platform rule is governed by that platform. Ordinary intervals are not multiplicity-adjusted, so a
non-significant *q* does not mean the interval contains zero."""),

("SI-F07-noteS5-fivegenes",
 """**Five selective antigens carry no tissue reading.** ALK, ENPP1, FGFR4, SLC34A2 and STEAP1 are
selectivity-significant in the surrogate and were never placed on the 100-gene cross-platform board.
They are unmeasured in EMC tissue by this study, and no statement in either document treats them as
negative.""",
 """**Missing-evidence states are distinct and are kept distinct.** ALK, ENPP1, FGFR4, SLC34A2 and STEAP1
carry the selectivity flag and were never placed on the 100-gene cross-platform board; they are
unmeasured in EMC tissue by this study. CD248, GPC2 and ROR1 carry one platform's contrast only. ALK,
ENPP1, FGFR4, PDGFRA, SLC34A2 and STEAP1 carry no normal-tissue record. NR4A3 emits no GPL3290 contrast
because only two comparator observations are available against a floor of three. CSPG4, B4GALNT1 and
SSTR2 have no retained selectivity result, which is not the same as never having been evaluated. None of
these states is a low, negative or absent reading, and no statement in either document treats any of them
as one; a measured but non-significant contrast and a significant decrease are two further, different
states."""),

("SI-F11-noteS5-reproducibility",
 """**No safety statement.** The normal-tissue prior is bulk RNA and the sequencing normal arm is six organ
types across 27 libraries. Neither is a safety assessment, no therapeutic window is computed anywhere, and
no agent named in either document has been given to a patient on the basis of anything in them.""",
 """**Reproducibility is partial and its boundary is stated.** The retained derived records support offline
recalculation of the array contrasts, intervals, within-platform corrections, cross-platform states,
sensitivity summaries, panel scores and sequencing reductions. They do **not** support reproduction of
the surrogate scan's rank-test *p* and *q* values, because the artifact retains selected output rows
rather than the full scanned universe, its per-line observations or its complete *p*-value family; nor an
audited probe-to-symbol mapping chain, because the accession cache is a resolved lookup rather than a
platform-annotation audit trail with source versions and ambiguity handling; nor the sequencing values
from their original public source, because the original peak table is not retained here. No independent
reproduction of any analysis from its original public source is claimed anywhere in either document.
Original execution outputs are preserved unaltered and are kept separate from any later annotation
correction.

**No safety statement.** The normal-tissue annotation is a category heuristic over records with null
quantitative fields, and the sequencing normal arm is a pooled mixture of 17 adult and 10 fetal libraries
across six unequally weighted organ labels. Neither is a safety assessment, neither establishes a clean
window or absence from any tissue, no therapeutic window is computed anywhere, and no agent named in
either document has been given to a patient on the basis of anything in them."""),
]


def apply(text, edits, label):
    log = []
    for eid, old, new in edits:
        n = text.count(old)
        if n != 1:
            raise SystemExit("FAIL %s/%s: matched %d times (expected 1)" % (label, eid, n))
        text = text.replace(old, new, 1)
        log.append((eid, len(old), len(new)))
    return text, log


def main():
    src = pathlib.Path(sys.argv[1])
    out = pathlib.Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    total = 0
    for name, edits in ((MAIN, EDITS_MAIN), (SI, EDITS_SI)):
        raw = (src / name).read_text(encoding="utf-8")
        before = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        new, log = apply(raw, edits, name)
        (out / name).write_text(new, encoding="utf-8")
        after = hashlib.sha256(new.encode("utf-8")).hexdigest()
        print("%s: %d edits applied" % (name, len(log)))
        print("  before %s (%d bytes)" % (before, len(raw.encode("utf-8"))))
        print("  after  %s (%d bytes)" % (after, len(new.encode("utf-8"))))
        for eid, lo, ln in log:
            print("    %-40s %5d -> %5d chars" % (eid, lo, ln))
        total += len(log)
    print("TOTAL EDITS: %d" % total)


if __name__ == "__main__":
    main()
