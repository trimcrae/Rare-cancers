---
id: DOC-EMC-SURFACE-TARGET-LANDSCAPE-PEER-REVIEW
title: "Simulated peer review — emc-surface-target-landscape.md (British Journal of Cancer)"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: A simulated journal peer review of the surface-antigen manuscript, and the revision list it generates.
scope: Review of one manuscript. Reports no new result and asserts nothing about any disease or agent.
audience: [maintainers, external reviewers]
date: 2026-08-10
last_verified: 2026-08-10
---

# Simulated peer review — surface-antigen prioritisation in extraskeletal myxoid chondrosarcoma

> **THIS IS A SIMULATED INTERNAL REVIEW WRITTEN BY AN AI REVIEWER. IT IS NOT A REAL JOURNAL REVIEW, IT
> IS NOT CORRESPONDENCE FROM THE BRITISH JOURNAL OF CANCER OR FROM SPRINGER NATURE, AND NO EDITOR,
> REFEREE OR EMPLOYEE OF ANY JOURNAL HAS SEEN THIS MANUSCRIPT. The manuscript has not been submitted.
> The reviewer role, the venue framing and the recommendation are all internal exercise. Do not quote
> any line of this file as a journal decision, a referee report, or evidence that the work was
> reviewed by anyone.**

Manuscript under review: `research/manuscripts/emc-surface-target-landscape.md`, with
`emc-surface-target-landscape-si.md` and `emc-surface-target-landscape-cover-letter.md` as submitted
material. Reviewed against the committed artifacts, not against the prose alone.

## Verification note: what was traced, and what was checked against source

Every load-bearing number in Tables 1 to 5 and Tables S1 to S7 was traced to the artifact that produced
it. The surfaceome derivation (2,820 UniProt genes, 47-antigen seed, 41 overlapping, 2,826 unique, 2,692
scanned), the class size (76 by subtype string), the Benjamini-Hochberg selectivity values for every
antigen in Table 1, the three cohort arm sizes, all 24 array contrasts and t values in Tables 3 to 5,
all 14 sequencing medians in Table S6, all nine panel scores in Table S5, the three instrument controls
in Table S4 and the seven cross-platform state counts in Table S7 reproduce exactly from
`emc-surfaceome-scan.json`, `emc-surface-normal-window.json`, `emc-expression-panels.json`,
`gse28866-tumour-vs-normal.json` and `surfaceome-instrument-limits.json`. ALCAM at 0.578 versus 0.631
versus 0.377, CSPG4 at +0.885 (t = 7.42) and −0.189 (t = −0.40), and B7-H3/CD276 at q = 1.0 are all
correct as printed. Arithmetic accuracy is not this manuscript's problem, and that is worth saying
plainly because it is unusual.

The problems found are of three kinds: numbers that are right but described in a way the artifact does
not support; sets whose membership rule cannot be reproduced; and a statistical criterion that the
Methods disclaim as "a readability aid rather than a test" and that then carries every headline count.

**On the withdrawn cell line, checked because it is the most damaging thing a reviewer could find.** I
searched the manuscript, the supplementary file, all five tables, the figure script and the rendered
figure for residue of the framing in which a DepMap line was treated as "the one real EMC line". **I
found none in the live text.** The Methods name the line once, state that the curated record does not
support the fusion label, and treat it as one of 45 class members rather than as disease evidence. The
SI does the same. Every other occurrence is inside Appendix A, which is explicitly the correction
register and quotes the withdrawn wording as withdrawn. The figure is rendered from the two stage-1
JSON files and plots no line-level quantity. The cover letter describes the reclassification accurately.
The one residual risk is presentational rather than scientific and is raised as Minor 15.

## Recommendation

**Major revision** on the science, with the honest caveat below on what would actually happen to this
submission at this venue.

The study asks a question worth asking and answers part of it. The design, a surrogate ranking followed
by a test of that ranking in the disease's own tissue, is sound, the instrument controls are real and
they pass, and the discipline about what a transcript can and cannot say is better than most papers of
this type manage. But the central conclusion is stated as an asymmetry, "the surrogate's negatives
transferred and its positives did not", and that asymmetry is contradicted by the manuscript's own
Table 5: the two most strongly negative rows in the surrogate that have a tissue reading, CD44 at
−3.89 log2TPM and ALCAM at −1.45, are two of the five genes the paper reports as concordantly elevated
in EMC tissue. The half of the conclusion that survives, that the surrogate's positives were not
reproduced, is real and gets stronger under correction. Separately, every headline count in the
abstract, Results and Conclusion is a count of genes crossing an uncorrected |t| >= 2 threshold that the
Methods describe as not a test, and at these degrees of freedom that threshold is more permissive than
a 95% confidence interval. The single antigen the paper carries forward, ALCAM, falls in exactly that
gap: on the second array its t is 2.214 at 8.5 degrees of freedom, two-sided p = 0.056, and its 95%
confidence interval crosses zero. None of this requires new data. All of it is recoverable by
re-analysing values already committed, and the corrected result is a better paper than the current one:
the negative gets firmer and the one positive that should not have survived stops surviving.

**Acceptance realism at this venue, stated without flattery.** I do not think this manuscript is sent
out for review at the British Journal of Cancer. It is an all-negative in-silico study on public data,
in a tumour with an incidence near one per million, from a single author with no institutional
affiliation and no ORCID, with no protein-level measurement, on array platforms deposited in 2005 and
2010, at n = 6, n = 10 and n = 4. BJC screens on translational significance and breadth of interest to
a general oncology readership, and desk-rejects a large majority of what it receives. My estimate is
that desk rejection is the most likely single outcome by a wide margin, and that if it does go out, the
defects listed below would push a careful referee to reject rather than to revise.

**The single change that would most improve the odds** is to change what the paper is about. As
written, the subject is EMC and the answer is that nothing works, which is a narrow result in a rare
disease. The generalisable finding is in the Discussion already and is buried there: surrogate-based
target lists are how surface-antigen programmes for rare tumours are built when the tumour has no data,
and this is a measurement of how far such a list transfers. Retitle and rebuild around that question,
with EMC as the worked case, the corrected statistics as the result, and an explicit statement of the
effect size the design can and cannot exclude. That is a claim about a method the field uses routinely,
which is the only available route to "broad interest" for a study this size.

**If a different venue is the honest answer, it is.** Given the constraint that publication must cost
the author nothing, the reasoning behind choosing a hybrid journal with a free subscription route is
correct, and BJC does have one. But *Genes, Chromosomes and Cancer* is the better fit on every other
axis: a fusion-driven-sarcoma genomics readership that will recognise why the GPL3290 accession bridge
matters and why an EMC-versus-DFSP contrast is not an EMC-versus-normal one, an editorial appetite for
cross-platform expression analyses of rare translocation sarcomas, and a subscription route that is
also free to the author. The repository already carries that venue profile in `submission_metrics.py`.
I would send it there and I would expect it to be reviewed rather than desk-rejected. This review is
completed for BJC as submitted.

## Major points

**1. The concordance criterion is not a test, and every headline count depends on it.**
*Applies to: Methods, "Controls and multiple testing"; Results, all subsections; Abstract; Conclusion;
Tables 3 to 5.*
The Methods state that "A threshold on |t| in a verdict string is a readability aid rather than a test"
and that "No multiple-testing correction is applied anywhere in the tissue read". The Abstract,
Results and Conclusion then consist almost entirely of counts of genes crossing that threshold: none of
eight concordantly elevated, two concordantly lower, exactly five concordantly elevated across the
board, none of eleven addresses elevated. A criterion cannot be disclaimed as a readability aid in the
Methods and carry the conclusion in the Abstract.

Two specific consequences, both computed from the committed Δ, t and degrees of freedom without any new
data. First, at these degrees of freedom |t| >= 2 is more permissive than a conventional 95% interval:
the two-sided critical value is 2.48 at df 5.7, 2.31 at df 8.0 and 2.17 at df 12.4. ALCAM's GPL3290
contrast, t = 2.214 at df 8.5, is therefore counted as movement while its exact two-sided p is 0.056 and
its 95% confidence interval is [−0.02, +1.53], which includes no difference. EGFR's GPL3290 contrast,
t = −2.019 at df 8.5, p = 0.076, is likewise counted as movement, and it is half the evidence for the
paper's asymmetry claim. NCAM1's GPL3290 contrast at t = 1.972 is counted as flat. Second, applying
Benjamini-Hochberg within platform across the readable genes on the 100-gene board, which is the same
standard stage 1 used, changes the results: on GPL6244 24 of 95 readable genes reach q < 0.05, on
GPL3290 16 of 78, and the set of genes concordantly elevated on both arrays falls from five to three.
ALCAM drops out (GPL3290 q = 0.16) and GPC1 drops out (GPL6244 q = 0.066). VCAN, BGN and CD44 survive,
and all three are the matrix or proteoglycan genes the paper already discounts as products the tumour
deposits rather than addresses a binder would find. FGFR1 and PTK7 survive as concordantly lower on
both platforms (all four q values below 0.02), so the paper's negative gets firmer. CD276's GPL6244
contrast (p = 0.034, q = 0.088) and CD248's (p = 0.054, q = 0.128) do not survive.

*What would resolve it.* State an alpha. Report the exact two-sided p and the 95% confidence interval
beside every Δ in Tables 3, 4, 5 and S5. Apply Benjamini-Hochberg within platform across the 100-gene
board and re-derive every count in the Abstract, Results and Conclusion from the corrected values. Then
say, in one sentence in the Abstract, that the corrected two-platform test leaves no cell-surface
adhesion molecule concordantly elevated. That is a stronger and cleaner headline than the current one
and it costs the paper nothing it should want to keep.

**2. The asymmetry between negatives and positives is not supported by the paper's own data.**
*Applies to: Abstract, Conclusions sentence; Results, "Surrogate priorities in EMC tumour tissue",
paragraph 1; Discussion, paragraph 1.*
"The surrogate's negatives transferred and its positives did not" is the most quotable sentence in the
manuscript. Its evidence is two antigens: EGFR concordantly down, and CD276 lower on the one platform
that reads it. But Table 1 marks six antigens non-selective (CD276, FAP, LRRC15, ERBB2, ALCAM, EGFR),
and the scan artifact contains many more. Of the surrogate's negatives that have a tissue reading, two
are concordantly elevated: ALCAM at enrichment −1.45, q = 1.0, and CD44 at −3.89, q = 1.0, the
surrogate's most strongly negative row. Those two are precisely the genes the tissue read nominates.
The manuscript states this itself, in "Genes concordantly elevated on both arrays" and in SI Note S4,
and then draws the opposite generalisation two pages later. Adding Major 1, neither of the two
supporting negatives survives correction. The asymmetry is therefore constructed by choosing two of six
negatives and reading them at an uncorrected threshold.

*What would resolve it.* Replace the asymmetry with what the data support: the surrogate ranking
carried no information about EMC tissue behaviour in either direction, since neither its top-ranked
antigens nor its most strongly rejected ones predicted their tissue reading. If the asymmetry is
retained in any form, the same sentence must name the full non-selective set, its tissue states, and
the two counterexamples.

**3. "Eight antigens were selective in the surrogate" cannot be reproduced from the artifact and
disagrees with Table 1.**
*Applies to: Abstract, Results sentence; Results, "Stage-1 selectivity", sentence 1; Table 1; Table 3.*
Table 1 marks nine antigens "Selective: yes", including CD248 at +2.29 with q = 0.0. The Results
sentence lists eight and omits CD248; Table 3, headed "Surrogate-selective antigens read in EMC tumour
tissue", contains the same eight and puts CD248 in Table 4 instead. In the scan artifact, 18 of the 47
seeded actionable antigens are BH-significant: the eight named, plus CD248, FGFR4, ALK, ENPP1, STEAP1,
PDGFRB, ROR1, PDGFRA, DLL3 and SLC34A2. Thirteen of those 18 have a tissue reading on the 100-gene
board, and none of the thirteen is concordantly elevated. A reader cannot recover the rule that
produced "eight" from anything published or committed.

*What would resolve it.* Pre-specify the selective set as every BH-significant antigen in the actionable
set, report all 18 in Table 1 or Table S1 with their q values, report the 13 with a tissue reading in
Table 3, and name the five that have none. The headline becomes "none of the thirteen surrogate-selective
antigens with a tissue reading is concordantly elevated on both arrays", which is a stronger claim over
a reproducible set.

**4. The empty selective-and-restricted intersection, and Figure 1's shaded quadrant, are contradicted
by DLL3 in the same two artifacts.**
*Applies to: Abstract; Results, "Stage-1 selectivity", paragraph 4; Figure 1 and its caption; SI Table
S2.*
The manuscript states that "the normal-tissue prior left no evaluated antigen both selective and
restricted" and captions Figure 1 "which is unpopulated for the antigens the filter evaluated". DLL3
carries enrichment +0.29 with BH q = 0.0079 (selective) in the scan artifact and window RESTRICTED in
the normal-tissue artifact. It is excluded from the intersection only because it is bookkept as a
positive control for the classifier, a fact stated nowhere in the sentence that makes the claim. DLL3
is also a genuine clinical surface target, so the exclusion is not obviously innocent. GPC3 is the same
shape one step away: RESTRICTED, q = 0.053.

Figure 1 makes this worse rather than better. The shaded rectangle spans x > 0 and the RESTRICTED tier
and is annotated "target-worthy (selective and restricted) — EMPTY", and the rendered figure has a
marker inside it: B4GALNT1, plotted at x = 0 and labelled "(sel n/a)". A gene with no selectivity value
is being placed at a measured selectivity of zero, inside a region captioned empty. The display list in
`emc_surface_figure.py` contains 13 antigens and omits DLL3, GPC3, ALCAM, CD248, ERBB2, LRRC15 and
CSPG4, so the emptiness is a property of that list rather than of the evaluated set.

*What would resolve it.* Either state explicitly that classifier controls are excluded from the
intersection by definition and report DLL3 and GPC3 by name as the nearest members with their q values,
or re-scope the claim to "no non-control antigen". Do not leave the current unqualified form. Redraw or
replace the figure (see the display-item recommendation below); at minimum, no marker may sit in a
region annotated as empty, and a gene with no selectivity value must be shown off-axis rather than at
zero.

**5. Half the GPL3290 comparator arm was not processed like the EMC arm, and the confound is not
disclosed.**
*Applies to: Methods, "EMC tumour-tissue cohorts"; Limitations; SI S4; every GPL3290 column in Tables 3,
4, 5 and S5; Results, "CSPG4, a gene outside the stage-1 scan".*
The verbatim deposit annotations committed in `emc-expression-panels.json` show that the ten EMC arrays
and the three dermatofibrosarcoma protuberans arrays were hybridised against a "CRH" reference and are
mRNA, while the three gastrointestinal stromal tumour arrays are total RNA against a "UHR" reference. On
a two-colour platform every value is a log-ratio against the reference channel, so half of a
six-sample comparator arm differs from the EMC arm in both reference pool and RNA input. The
Limitations correctly say that only the between-group contrast is interpretable on this platform, but
the between-group contrast is exactly the quantity this confound sits inside. It affects all 78 GPL3290
gene contrasts, the +0.599 route-panel score that disagrees with GPL6244, and the CSPG4 discordance for
which the paper offers two explanations and not this one.

*What would resolve it.* State the confound in Methods and Limitations. Recompute the GPL3290 contrasts
against the three DFSP arrays alone as a sensitivity analysis, report which conclusions change, and add
the reference-channel and RNA-input mismatch as a third live explanation for CSPG4 in Results and SI
Note S3. This is a re-analysis of data already in hand.

**6. Sample selection in GSE24369 is undeclared, and the discarded samples include the only normal soft
tissue in the study.**
*Applies to: Methods, "EMC tumour-tissue cohorts"; Table 2; Limitations.*
The deposit carries 42 samples. The analysis uses 35: 6 EMC and 29 comparators. Seven are dropped by
the string matcher as unclassified, and the artifact shows what they are: five solitary fibrous tumour
arrays and two pooled normal skeletal-muscle arrays. Neither the exclusion nor its rule appears
anywhere in the manuscript, and Table 2 presents 6 versus 29 as though it were the deposit. Solitary
fibrous tumour is a legitimate soft-tissue sarcoma comparator whose inclusion would move every Δ and t
on the paper's primary lineage platform. The two pooled skeletal-muscle arrays matter more: the paper's
stated binding limitation on its exposure axis is that its normal arm is visceral organs "containing
almost no soft tissue", and here are two normal soft-tissue libraries on the same array as the primary
cohort, discarded without mention.

*What would resolve it.* Declare the 42 to 35 reduction and the classification rule in Methods, and list
the excluded samples in the SI. Report a sensitivity analysis with solitary fibrous tumour added to the
comparator arm, or state why it is excluded. For the antigens carried forward, either report the two
pooled skeletal-muscle arrays as a qualitative normal soft-tissue anchor with explicit n = 2 and
pooled-RNA caveats, or state in the Limitations why they cannot be used. Silently dropping the only
normal soft tissue available while naming its absence as the binding limitation is the version that
cannot stand.

**7. A calibration the committed artifact already computes is not reported, and two summary sentences
disagree with it.**
*Applies to: Results, "Route-named therapeutic addresses"; Results, "SSTR2 and the GD2 proxy",
paragraph 3; Discussion, paragraph 2; Table 4; SI Table S6.*
`gse28866-tumour-vs-normal.json` carries a `ratio_calibration` block that expresses each gene's
EMC-over-comparator ratio as a percentile of the same ratio computed for every gene in the deposit
(13,708 with a normal ratio, 13,247 with a sarcoma ratio; the median gene sits at 1.05 both ways). The
artifact's own note says this exists because "a fold-change is not a reading until an arbitrary gene's
fold-change is known", and calls it the manuscript's own standard applied to the arm that lacked it. The
manuscript reports the raw ratios and not the percentiles. On the calibrated scale, CSPG4 is at the 99th
and 98th percentiles, SSTR2 at the 89th and 84th, FAP at the 91st and 92nd, CD276 at the 77th and 86th,
ALCAM at the 33rd and 90th, CD248 at the 26th and 7th.

Two sentences are contradicted by that. The SSTR2 summary, "the first EMC transcript readings show no
elevation over other soft-tissue tumours and no striking absolute signal", is a statement about the
array readings that reads as a statement about all three cohorts, and in the third cohort SSTR2 sits in
the top sixth of the transcriptome against other sarcomas. The Discussion's "B7-H3 is not a
differentially expressed EMC address on either instrument" excludes the sequencing cohort, where CD276
is 1.42 times the other-sarcoma median at the 86th percentile. Neither reading is strong, and neither
overturns the paper's position, but the prose must not describe a direction its own table contradicts.

*What would resolve it.* Add the two percentile columns to Table 4 and Table S6. Rewrite the SSTR2
sentence to name the instrument it is about and to report the sequencing percentile beside it. Rewrite
the B7-H3 sentence as "not differentially expressed on either array platform" and state the sequencing
reading and its n = 4, three-peak basis in the same clause.

**8. The surrogate class definition in Methods and SI does not match the artifact, and the abstract
misstates the sample size.**
*Applies to: Abstract, Methods sentence; Methods, "Expression and selectivity in the surrogate class";
SI S2; SI Table S1.*
The artifact's `class_oncotree_subtypes_present` is Alveolar Rhabdomyosarcoma, Alveolar Soft Part
Sarcoma, Clear Cell Sarcoma, Ewing Sarcoma, Extraskeletal Myxoid Chondrosarcoma and Synovial Sarcoma.
Desmoplastic small round cell tumour, named in both the Methods and SI S2, contributed no line at all.
Alveolar rhabdomyosarcoma, named in neither, did. In a paper whose entire argument is about the validity
of a lineage surrogate, the composition of the surrogate has to be right, and a skeletal-muscle-lineage
tumour entering the class unannounced is exactly the kind of thing a referee will use to doubt the rest.
Separately, the Abstract says the surfaceome was ranked "across a translocation-sarcoma DepMap class
(n = 76 lines)". Seventy-six is the count by subtype string; only 45 carry expression data, and every
per-gene row in the artifact reports n_class = 45. The Abstract also says "a 2,826-gene human surfaceome
was ranked" where 2,692 were scanned.

*What would resolve it.* Correct the subtype list in Methods and SI S2 to the six actually present, and
say that desmoplastic small round cell tumour was sought and matched nothing. Give both figures in the
Abstract: 2,826 candidates of which 2,692 were scanned, and 76 class members of which 45 carried
expression data.

**9. The Abstract omits the paper's one live lead and leaves a stronger negative impression than the
body supports.**
*Applies to: Abstract, Results and Conclusions; Conclusion section.*
CSPG4 is one of the eleven route-named addresses. It is +0.885 SD at t = 7.42 on GPL6244, which survives
within-platform BH at q = 0.0017, it is the largest absolute row in the sequencing deposit at 3.31 times
normal and 2.51 times other sarcomas (99th and 98th percentiles on the calibrated scale), and on the
second array it is uninformative rather than negative: Δ = −0.189 with a 95% interval of [−1.23, +0.86].
The Abstract says only that none of the eleven was concordantly elevated. That is true under the
concordance rule and it leaves a reader who stops at the abstract with an all-negative summary that the
body, which devotes a full subsection to holding CSPG4 open, does not support. The result is a paper
that undersells its most robust tissue finding while overselling a demoted one.

*What would resolve it.* One clause in the Abstract's Results, naming CSPG4 as elevated on one array and
in the sequencing cohort, uninformative on the second, never evaluated at stage 1, and held open. Say in
the same breath that this is a transcript reading on one peak at n = 4 and one probe at n = 6.

**10. Panel-level and gene-level movement are judged by different standards.**
*Applies to: Results, "Route-named therapeutic addresses", paragraph on FAP; Discussion, paragraph 2;
Table S5.*
The 13-gene stromal and matrix panel is described as "lower in EMC on both platforms" at t = −1.89 and
t = −1.80, and that reading is then promoted into the Discussion as one of three surviving negatives
with a named basis. Neither contrast reaches the |t| >= 2 threshold that makes a gene "flat" everywhere
else in the paper. The antigen-presentation panel is handled correctly two paragraphs earlier, where the
non-significant platform is flagged as such, which makes the inconsistency harder to defend rather than
easier.

*What would resolve it.* Apply one rule. Either report the stromal panel as not moving on either
platform and remove it from the Discussion's surviving negatives, or report both panels the same way
with p, confidence interval and the correction status stated.

**11. Two novelty and priority claims exceed what the prior-art screen can support, and the screen was
run at a fraction of its available depth.**
*Applies to: Background, paragraphs 3 and 4; Results, "Route-named therapeutic addresses", last sentence
of paragraph 1; SI S6.*
"Surface-antigen prioritisation for EMC has had to run on surrogates because the disease was taken to be
absent from usable public expression data" is a claim about the field. The paper cites, as reference 7,
the originating publication of one of its own cohorts, which is an EMC gene-expression profiling study,
and the SI states that what changed was the probe-to-symbol bridge and not the deposit. "Six of these
genes gained their first EMC-tissue array contrast in this work" is a priority claim resting on a screen
that the same paragraph says matched titles and abstracts only and "would be invisible to" a result
inside a supplementary table. The artifact records 322 records retrieved with 238 full-text files
present, so the full texts that would let the screen answer the question were fetched and not searched.

*What would resolve it.* Reword the first claim to describe this programme's own prior state rather than
the field's, and to say that the deposits were known and the symbol bridge was not. Drop the priority
sentence, or run the term screen across the 238 retrieved full texts and report the result, which costs
nothing and is a re-analysis of data already held. If the sentence is kept, it must be qualified in the
same sentence by the screen's stated blind spot.

**12. The stated provenance chain for seven references is wrong in the direction that looks worst.**
*Applies to: References preamble; Data availability; Appendix A4; Limitations, last sentence.*
References 4, 5, 6, 13, 16, 17 and 18 carry full author lists, journal names, volumes, issues and pages.
The References preamble names two retrieval artifacts as the source of those fields. Appendix A4 states
that five of them "are in neither retrieval and still carry their identifier alone", that two "resolved
with an author list, year, DOI and identifiers but no journal or pagination", and that "Nothing was
written for any of the seven, because a field that is not in a retrieval is left missing". That is no
longer true of the manuscript: all seven carry complete records. I checked whether the records exist,
and they do. A third committed artifact, `research/literature/remaining-reference-metadata-2026-08-09.json`,
carries complete and matching bibliographic records for all seven. So the citations are traceable and
the statements describing them are stale, which is the worst possible arrangement: a referee who follows
the paper's own stated chain concludes that seven references carry bibliographic detail nobody fetched.
The Limitations compound it by referring to "citations marked in the reference list as not yet retrieved"
when no reference carries such a mark.

*What would resolve it.* Name the third artifact in the References preamble and add it to Data
availability. Rewrite Appendix A4 to record that the seven were subsequently resolved and where. Delete
the stale Limitations sentence. This is bookkeeping, but in a manuscript that makes a virtue of its
correction register, a correction register that is itself out of date is a target.

## Minor points

1. *Table 1.* ALCAM's BH q is given as "not significant" where every other row carries a number. The
   artifact records q = 1.0. Print the value.
2. *Table 1.* LRRC15's normal-tissue verdict is given as "not scored in this filter". The window
   artifact carries LRRC15 as ENHANCED_BROAD. Print the verdict, or say why it is being withheld.
3. *Methods, "Expression and selectivity in the surrogate class".* "Four limits of this instrument were
   computed" against SI Note S1 and the artifact, both of which carry five. The fifth, that the scan
   holds no observation of FAP in this disease, is the one omitted, and it is load-bearing for the FAP
   discussion. Say five, or say four and name the fifth where it applies.
4. *Methods, paragraph 1.* "Supplementary Tables S1 to S8". The SI ends at S7.
5. *SI structure.* Supplementary Methods S1 to S6 and Supplementary Notes S1 to S5 share their labels, so
   "Supplementary Note S1" in the main text is ambiguous with "S1. Surfaceome construction". Renumber the
   notes N1 to N5.
6. *SI Table S2.* Titled "Complete normal-tissue classification". It carries 25 rows; the artifact holds
   46 antigens with window verdicts, among them CD44, GPC1, VCAN, LRRC15, MSLN, L1CAM, CDH17, PDGFRB,
   ROR1 and TNC. Either give all 46 or retitle it as the antigens discussed in the main text.
7. *SI Table S2 and Table 5.* The window artifact carries a `plasma_membrane_confirmed` field for every
   antigen, and it is false for ALCAM, whose only recorded subcellular annotation is vesicles. In a paper
   about surface antigens, the field belongs in Table S2 for every row, with one sentence noting that the
   annotation is immunofluorescence-based and that its absence is not evidence against surface
   localisation. Table 5 should also carry the window verdict for the concordantly elevated genes, which
   the artifact holds for four of the five (VCAN reads as a vital or immune liability, CD44 as broad,
   GPC1 as enhanced-broad, ALCAM as restricted).
8. *Results, "Stage-1 selectivity", paragraph 3.* CD248 is grouped with FAP under "the surrogate
   instrument has no stromal compartment". The instrument-limits artifact explicitly narrows that limit
   and says so: CD248 and PDGFRB read as expressed and selectivity-significant because mesenchymal tumour
   cells genuinely transcribe them, and the honest limit is that the scan cannot see a gene that only the
   stroma expresses. Carry the narrowing into the manuscript; the wide form is the version the artifact
   warns against.
9. *Results, "Route-named therapeutic addresses"; Discussion.* Two clinical precedents committed in this
   repository bear directly on two named antigens and appear nowhere in the manuscript. A CD166-directed
   antibody-drug conjugate has been given to patients in a phase I/II trial, and it is a masked,
   protease-activated format chosen because of the antigen's normal-tissue distribution, which is
   independent corroboration of the paper's own exposure-axis demotion of ALCAM. For CD248, a randomised
   trial of a CD248-directed agent in soft-tissue sarcoma was negative, and CD248 protein has been scored
   by immunohistochemistry in a 514-case soft-tissue sarcoma series. Both are citations, not experiments,
   and both strengthen the paper's negatives. The relevant retrieval records are already committed.
10. *Table 4.* The sequencing columns are headed as ratios, and the PRAME row prints "normal median
    0.000" in the ratio column. Keep the column type constant and put the undefined-ratio note in the
    caption, as SI Table S6 already does.
11. *Results and Methods.* RET, a cell-surface receptor tyrosine kinase with approved inhibitors, sits at
    the 99th percentile against both the normal and other-sarcoma arms in the same sequencing panel the
    paper reports, and is not mentioned. Either state in Methods that the sequencing panel carries genes
    requested by other reads and is not a surface-antigen panel, or say why RET is out of scope for a
    manuscript titled as a surface-antigen landscape.
12. *Methods, "EMC tumour-tissue cohorts"; Limitations.* One GPL3290 EMC sample is annotated with a
    parenthetical repeat marker in the deposit. State whether the 10 EMC arrays are 10 patients.
13. *Methods; Limitations.* The sequencing artifact records technical-replicate ties among the non-EMC
    sarcoma libraries. State whether 32 libraries are 32 tumours, or report the arm as libraries with the
    replicate structure named.
14. *Appendix A.* The subsections are ordered A5, A1, A2, A3, A4.
15. *Appendix A, packaging.* The main body is clean of repository register: I found no glyph warnings, no
    em-dashes and no mid-sentence bolding outside legitimate run-in headings and table labels in the
    entire text above the appendix, which is a real strength and should be protected. Appendix A is the
    opposite, and it sits inside the manuscript file after the references. A first submission that
    carries a "Correction and supersession register" reads oddly to an editor, because a paper that has
    never been published cannot carry corrections. Move it to the SI as a version-history note, or to the
    cover letter, and strip the glyphs and mid-sentence bolding wherever it lands in the submission
    package. Also remove the "EDITORIAL, NOT FOR SUBMISSION" comment block and fill the ORCID placeholder
    or delete the line.
16. *Figure 1.* The jitter is computed from Python's string hash, which is salted per process, so the
    figure is not reproducible between runs. Use a deterministic offset.
17. *Figure 1.* The EPHB4 and MCAM labels overprint in the rendered image.
18. *Methods, "Cross-platform state and readability".* "CD248, CD276 and SSTR2 are unreadable on GPL3290"
    reads as a complete list; the Limitations give five, adding GPC2 and B4GALNT1. Make the Methods
    sentence consistent or scope it to the route-named panel.
19. *Methods, "Surfaceome definition".* The manuscript states that an established machine-learning
    surfaceome resource "was not used" and that "the two sets are not interchangeable" without
    quantifying the difference. That resource's membership table is public and the intersection with the
    2,826-gene set is a free computation. One sentence giving the overlap would convert an assertion into
    a measurement and would tell a reader how much the construction choice could matter.
20. *Discussion, paragraph 3.* "a marker-grade result" for ALCAM is an interpretive upgrade the data do
    not carry: no sensitivity, specificity or discrimination statistic is computed anywhere, the second
    array's contrast does not survive correction, and the sequencing arm has no test. Weaken to a
    statement of the directional consistency across cohorts, and drop "marker-grade".
21. *Declarations and Methods.* "Use of large language models" in Methods and "Use of artificial
    intelligence" in Declarations say the same thing twice, at a combined cost of about 140 words in a
    manuscript that needs the budget. Keep the Declarations version.

## Display items, word budget and figures

The manuscript uses 6 of BJC's 8 display items (5 tables plus one figure caption; the internal counter
reports 5 because the figure is not embedded in the file). Main text is 4,755 of 5,000 words, abstract
194 of 200, references 18 of 80 (the internal counter's 21 includes a numbered list inside Appendix A).

**Zero figures would be the wrong call, and one figure is the right number.** A paper whose result is
"these effects were not detected" is precisely a paper that must show its uncertainty, and five dense
tables of point estimates cannot do that. Figure 1 as it stands should not survive: it renders the
surrogate stage only, its central annotation is contradicted by a marker inside it (Major 4), and it
displays the stage the paper is not actually about.

**Replace it with a two-panel greyscale forest plot of the transfer result.** Panel a, GPL6244; panel b,
GPL3290. One row per antigen: the 18 BH-significant surrogate antigens plus the eleven route-named
addresses, ordered by surrogate enrichment descending, with the surrogate q printed beside each label so
the two stages sit on one page. The x-axis is Δ in standard-deviation units of that array's probe
distribution, with a vertical rule at zero. Each row shows the point estimate and its exact 95%
confidence interval. Encode significance by fill and shape, not colour: filled square where the
within-platform BH q < 0.05, open square otherwise, and a small open triangle drawn at the axis for
"not readable on this platform" so that an instrument statement is visibly different from a null result.
Everything is black, white and one 40 per cent grey, so it costs nothing in print and loses nothing in
greyscale.

That figure carries the paper's whole argument. It shows that no surrogate-selective antigen has an
interval excluding zero in the positive direction on both panels; that several intervals, KIT and NCAM1
and EPHB4 on GPL3290 among them, are so wide that the data are uninformative rather than negative; and
that FGFR1 and PTK7 are the two robust reversals. It is also the honest answer to the objection that a
non-transfer conclusion is indistinguishable from noise.

**Paying for the additions.** The revisions above add roughly 400 to 450 words. There are 245 spare, and
these cuts free about 400 more. Move the prior-art screen paragraph out of Background into SI S6, which
already carries it in full (about 160 words). Delete the Methods "Use of large language models"
subsection, which the Declarations duplicate (about 90 words, Minor 21). Compress the four-explanations
paragraph in "Genes concordantly elevated on both arrays" to one sentence plus a pointer to SI Note S4,
which carries it verbatim (about 100 words). Cut Table 3 entirely, since the new figure supersedes it,
along with its two-sentence preamble (about 60 words and one display item).

## On the central question: is the headline right?

Asked directly, because the manuscript deserves a direct answer.

**Right.** That the surrogate's positives were not reproduced in EMC tissue. Thirteen of the eighteen
BH-significant antigens have a tissue reading and none is concordantly elevated; two are concordantly
lower and survive correction on both platforms. This is a real finding and correction makes it firmer.

**Overstated.** The asymmetry (Major 2), the empty selective-and-restricted intersection (Major 4), and
the survival of ALCAM as anything (Major 1). "The surrogate's negatives transferred" is contradicted by
the paper's own concordant-up list, and ALCAM does not survive the correction the paper applied one
stage earlier.

**Understated.** CSPG4, which is the most robust tissue result in the manuscript and is absent from the
abstract (Major 9).

**Is non-transfer distinguishable from underpowered noise?** For individual antigens, often not: the
minimum detectable |Δ| at the paper's own |t| = 2 threshold has a median of 0.23 SD on GPL6244 but 0.81
SD on GPL3290, and the two-platform concordance requirement is governed by the weaker platform. So the
criterion is defensible as a specificity-first rule, but it has a floor near 0.8 SD, and it cannot
exclude a real elevation below that no matter how clean the first array is. In aggregate, though, the
distinction can be made and the paper should make it: the same design detected FGFR1 and PTK7 as
concordantly lower and VCAN, BGN and CD44 as concordantly higher, all surviving correction on both
platforms, so the instrument demonstrably resolves effects of roughly 0.7 SD and above. The correct
statement is therefore not "these antigens are not elevated" but "no antigen in the surrogate-selective
set shows an elevation of the size this design can resolve, which is about 0.8 SD on the limiting
platform". That sentence belongs in the Abstract and in the Conclusion, and it is the difference between
a negative result and an absence of evidence.

**Are the three cohorts comparable enough to read together?** They are read together only as three
independent looks with a common direction, never pooled, and the manuscript is scrupulous about that.
Two caveats it does not make: the two lineage cohorts have different comparator arms, which the paper
states, but one of them also has an internally inhomogeneous comparator arm (Major 5); and the third
cohort is the only one carrying a normal comparison, so a gene's behaviour there is answering a
different question and the calibrated percentiles should be shown when it is quoted (Major 7).

**Is the normal-tissue prior applied consistently between stages?** No, and this is worth one sentence
in the paper. At stage 1 the prior is the decisive filter and is applied to every candidate. At stage 2
it disappears: the five concordantly elevated genes are reported with no window verdict, although the
artifact holds verdicts for four of them and one of those is a vital or immune liability (Minor 7). The
same instrument is decisive in one stage and silent in the other.

## Revision list

Work top to bottom. Every item is met by re-analysis of committed data, restructuring, or a change of
wording. None requires a new experiment, and none asks for protein-level or immunohistochemical
validation as a condition of acceptance.

1. `emc-surface-target-landscape.md`, Methods "Controls and multiple testing": state an explicit alpha
   for the tissue read and stop describing the |t| threshold as a readability aid while using it as a
   test. (Major 1)
2. `emc-expression-panels.json` consumers: compute the exact two-sided p, the 95% confidence interval,
   and a within-platform Benjamini-Hochberg q for every gene on the 100-gene board on each platform.
   Commit them into the artifact so the manuscript can cite rather than restate. (Major 1)
3. `emc-surface-target-landscape.md`, Tables 3, 4 and 5, and SI Table S5: add p, 95% CI and BH q columns
   to every contrast. (Major 1)
4. `emc-surface-target-landscape.md`, Results, Abstract and Conclusion: re-derive every count from the
   corrected values. Report that the concordantly elevated set falls from five to three and that ALCAM
   and GPC1 do not survive; report that FGFR1 and PTK7 survive on both platforms; report that the CD276
   and CD248 single-platform reads do not survive. (Major 1)
5. `emc-surface-target-landscape.md`, Abstract Conclusions, Results "Surrogate priorities in EMC tumour
   tissue" paragraph 1, and Discussion paragraph 1: delete the negatives-transferred asymmetry and
   replace it with the statement that the surrogate ranking predicted tissue behaviour in neither
   direction, naming ALCAM and CD44 as the counterexamples in the same sentence. (Major 2)
6. `emc-surface-target-landscape.md`, Results "Stage-1 selectivity" and Table 1; SI Table S1: define the
   selective set as every BH-significant antigen in the actionable set, report all 18 with q values, and
   reconcile Table 1's nine with the text's eight. (Major 3)
7. `emc-surface-target-landscape.md`, Table 3 and Results: report the 13 BH-significant antigens that
   have a tissue reading, name the five that do not, and restate the headline as "none of thirteen".
   (Major 3)
8. `emc-surface-target-landscape.md`, Abstract, Results "Stage-1 selectivity" paragraph 4, and the
   Figure 1 caption: qualify the empty-intersection claim by stating that classifier controls are
   excluded by definition, and name DLL3 (q = 0.0079, RESTRICTED) and GPC3 (q = 0.053, RESTRICTED)
   explicitly as the nearest members. (Major 4)
9. `research/modalities/emc_surface_figure.py`: retire the current figure. Do not plot a gene with no
   selectivity value at x = 0, do not annotate a region as empty while a marker sits in it, and replace
   the salted-hash jitter with a deterministic offset. (Major 4, Minor 16, Minor 17)
10. `research/modalities/emc_surface_figure.py`, new Figure 1: build the two-panel greyscale forest plot
    specified above, with 95% confidence intervals, fill and shape encoding of within-platform BH
    significance, and an explicit not-readable marker. (Display items section)
11. `emc-surface-target-landscape.md`: delete Table 3, which the new figure supersedes, and its
    two-sentence preamble. (Display items section)
12. `emc-surface-target-landscape.md`, Methods "EMC tumour-tissue cohorts" and Limitations; SI S4:
    disclose that the GPL3290 EMC and DFSP arrays share a reference pool and RNA input that the three
    GIST arrays do not. (Major 5)
13. `emc-expression-panels.json` and the manuscript: recompute the GPL3290 contrasts against the three
    DFSP arrays alone as a sensitivity analysis, and report which conclusions survive. (Major 5)
14. `emc-surface-target-landscape.md`, Results "CSPG4, a gene outside the stage-1 scan"; SI Note S3: add
    the reference-channel and RNA-input mismatch as a third live explanation for the CSPG4 platform
    disagreement. (Major 5)
15. `emc-surface-target-landscape.md`, Methods "EMC tumour-tissue cohorts" and Table 2: declare that
    GSE24369 carries 42 samples and that 35 enter the analysis, state the classification rule, and list
    the seven excluded samples in the SI. (Major 6)
16. `emc-surface-target-landscape.md` and `emc-expression-panels.json`: report a sensitivity analysis
    with the five solitary fibrous tumour arrays added to the GPL6244 comparator arm, or state why they
    are excluded. (Major 6)
17. `emc-surface-target-landscape.md`, Limitations and Results: either report the two pooled normal
    skeletal-muscle arrays in GSE24369 for the antigens carried forward, with explicit n = 2 and
    pooled-RNA caveats, or state why the only normal soft tissue in the study cannot be used. (Major 6)
18. `emc-surface-target-landscape.md`, Table 4; SI Table S6: add the EMC-over-normal and
    EMC-over-sarcoma ratio percentiles from `gse28866-tumour-vs-normal.json` -> `ratio_calibration`.
    (Major 7)
19. `emc-surface-target-landscape.md`, Results "SSTR2 and the GD2 proxy" paragraph 3: rewrite so the
    "no elevation" statement names the array platform it is about and reports the sequencing percentile
    beside it. (Major 7)
20. `emc-surface-target-landscape.md`, Discussion paragraph 2: rewrite "not a differentially expressed
    EMC address on either instrument" to scope it to the array platforms and to state the sequencing
    reading and its basis. (Major 7)
21. `emc-surface-target-landscape.md`, Methods "Expression and selectivity in the surrogate class"; SI
    S2: correct the subtype list to the six present in the artifact, note that alveolar rhabdomyosarcoma
    is among them, and state that desmoplastic small round cell tumour matched no line. (Major 8)
22. `emc-surface-target-landscape.md`, Abstract Methods: give 2,826 candidates of which 2,692 were
    scanned, and 76 class members of which 45 carried expression data. (Major 8)
23. `emc-surface-target-landscape.md`, Abstract Results and Conclusion: add the CSPG4 clause, held open,
    with its one-array, one-peak basis stated in the same sentence. (Major 9)
24. `emc-surface-target-landscape.md`, Results paragraph on FAP and Discussion paragraph 3: apply one
    movement rule to panels and genes alike, and either remove the stromal panel from the surviving
    negatives or report it with its non-significance stated. (Major 10)
25. `emc-surface-target-landscape.md`, Background paragraph 3: reword the "absent from usable public
    expression data" claim as a statement about this programme's prior state, noting that the deposits
    were known and the symbol bridge was not. (Major 11)
26. `emc-surface-target-landscape.md`, Results "Route-named therapeutic addresses": drop the "first EMC
    tissue array contrast" priority sentence, or re-run the term screen across the 238 already-retrieved
    full texts and report the result. (Major 11)
27. `emc-surface-target-landscape.md`, References preamble and Data availability: name
    `research/literature/remaining-reference-metadata-2026-08-09.json` as the third retrieval source.
    (Major 12)
28. `emc-surface-target-landscape.md`, Appendix A4: rewrite to record that references 4, 5, 6, 13, 16,
    17 and 18 were subsequently resolved, and where. (Major 12)
29. `emc-surface-target-landscape.md`, Limitations, last sentence: delete the reference to citations
    "marked in the reference list as not yet retrieved"; no such mark exists. (Major 12)
30. `emc-surface-target-landscape.md`, Table 1: print ALCAM's q as 1.0, and print LRRC15's window verdict
    as ENHANCED_BROAD. (Minor 1, Minor 2)
31. `emc-surface-target-landscape.md`, Methods: change "Four limits" to five, or name the omitted fifth
    limit where the FAP discussion relies on it. (Minor 3)
32. `emc-surface-target-landscape.md`, Methods paragraph 1: correct "Supplementary Tables S1 to S8" to
    S1 to S7. (Minor 4)
33. `emc-surface-target-landscape-si.md`: renumber the Supplementary Notes N1 to N5 so they no longer
    collide with Supplementary Methods S1 to S6, and update the main-text pointer. (Minor 5)
34. `emc-surface-target-landscape-si.md`, Table S2: either give all 46 antigens the artifact holds or
    retitle the table as the antigens discussed in the main text. (Minor 6)
35. `emc-surface-target-landscape-si.md`, Table S2: add the `plasma_membrane_confirmed` field for every
    row, with one sentence on what an immunofluorescence-based annotation can and cannot show, and note
    that it is false for ALCAM. Add a normal-tissue verdict column to Table 5. (Minor 7)
36. `emc-surface-target-landscape.md`, Results "Stage-1 selectivity" paragraph 3; SI Note S1 L2: carry
    the artifact's narrowing of the stromal-blindness limit, so CD248 and PDGFRB are not presented as the
    LRRC15 case. (Minor 8)
37. `emc-surface-target-landscape.md`, Results and Discussion: cite the CD166 antibody-drug conjugate
    precedent and its masked format beside the ALCAM demotion, and the negative randomised CD248 trial
    plus the 514-case sarcoma immunohistochemistry series beside the CD248 inversion, drawing both from
    the committed retrieval records. (Minor 9)
38. `emc-surface-target-landscape.md`, Table 4: keep the sequencing columns as ratios and move the PRAME
    undefined-ratio note into the caption. (Minor 10)
39. `emc-surface-target-landscape.md`, Methods: state that the sequencing panel carries genes requested
    by other reads, or explain RET's exclusion from a surface-antigen landscape. (Minor 11)
40. `emc-surface-target-landscape.md`, Methods and Limitations: state whether the 10 GPL3290 EMC arrays
    are 10 patients, and whether the 32 non-EMC sarcoma libraries are 32 tumours given the recorded
    technical-replicate ties. (Minor 12, Minor 13)
41. `emc-surface-target-landscape.md`, Appendix A: reorder A1 to A5, then move the whole appendix into
    the supplementary file as a version-history note and strip its glyphs and mid-sentence bolding.
    (Minor 14, Minor 15)
42. `emc-surface-target-landscape.md`, header: remove the editorial comment block and either supply the
    ORCID or delete the placeholder line before submission. (Minor 15)
43. `emc-surface-target-landscape.md`, Methods "Cross-platform state and readability": make the
    unreadable-on-GPL3290 list consistent with the Limitations, or scope it to the route-named panel.
    (Minor 18)
44. `emc-surface-target-landscape.md`, Methods "Surfaceome definition": add the measured overlap between
    the 2,826-gene set and the published machine-learning surfaceome. (Minor 19)
45. `emc-surface-target-landscape.md`, Discussion paragraph 3: delete "marker-grade" and describe
    ALCAM's directional consistency instead. (Minor 20)
46. `emc-surface-target-landscape.md`, Methods: delete the "Use of large language models" subsection and
    keep the Declarations statement. (Minor 21)
47. `emc-surface-target-landscape.md`, Background: move the prior-art screen paragraph into SI S6, which
    already carries it. (Word budget)
48. `emc-surface-target-landscape.md`, Results "Genes concordantly elevated on both arrays": compress the
    four-explanations paragraph to one sentence and point to SI Note S4. (Word budget)
49. `emc-surface-target-landscape.md`, Abstract and Conclusion: add the sentence stating the effect size
    the design can resolve, roughly 0.8 SD on the limiting platform, so that "not elevated" is not read
    as "absent". (Central question section)
50. `emc-surface-target-landscape.md`, title, Abstract Background and Discussion paragraph 1, plus
    `emc-surface-target-landscape-cover-letter.md`: reframe the subject as the transferability of
    lineage-surrogate surface rankings for rare tumours, with EMC as the worked case. Then decide the
    venue: this reviewer's honest advice is to submit to a fusion-sarcoma genomics journal with a free
    subscription route rather than to a selective general-oncology journal, where the most likely outcome
    is desk rejection. (Recommendation section)
