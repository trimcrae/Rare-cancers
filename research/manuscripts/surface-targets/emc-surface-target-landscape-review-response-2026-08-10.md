---
id: DOC-EMC-SURFACE-TARGET-LANDSCAPE-REVIEW-RESPONSE
title: "Response to the simulated peer review of emc-surface-target-landscape.md"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: A point-by-point response to the 2026-08-10 simulated internal review, recording what changed and where, and what was declined and why.
scope: Response to one review of one manuscript. Reports no new result and asserts nothing about any disease or agent.
audience: [maintainers, external reviewers]
date: 2026-08-10
last_verified: 2026-08-10
---

# Response to the simulated peer review of the surface-antigen manuscript

> **THIS RESPONDS TO A SIMULATED INTERNAL REVIEW WRITTEN BY AN AI REVIEWER. IT IS NOT
> CORRESPONDENCE WITH ANY JOURNAL. The manuscript has not been submitted, no editor or referee has
> seen it, and neither the review it answers nor this response is evidence that the work was
> reviewed by anyone. Do not quote any line of either file as a journal decision or a referee
> report.**

Review answered: [`emc-surface-target-landscape-peer-review-2026-08-10.md`](./emc-surface-target-landscape-peer-review-2026-08-10.md).
Files changed: the manuscript, its supplementary information, its cover letter, the figure generator
and the figure, plus three new committed artifacts and one systems-map registry entry.

## What changed, at a glance

Every statistical claim in the manuscript is now derived from
[`emc-tissue-read-statistics.json`](../../modalities/emc-tissue-read-statistics.json), a new artifact
that recomputes every array contrast from the committed per-sample values and adds the exact
two-sided *p*, the 95% confidence interval and a within-platform Benjamini-Hochberg *q*. The module
that writes it asserts that every recomputed Δ, *t* and degrees-of-freedom value reproduces the
committed contrast before it writes anything; all 173 contrasts reproduce, which is consistent with
the review's finding that arithmetic was not this manuscript's problem.

Under alpha 0.05 with within-platform correction the concordantly elevated set falls from five to
three (VCAN, BGN, CD44); ALCAM and GPC1 do not survive; FGFR1 and PTK7 survive as concordantly
lower; and neither of the two negatives that supported the withdrawn asymmetry survives. The
selective set is redefined as every actionable antigen with BH *q* < 0.05, which is 18 rather than
eight. The paper was reframed and its venue changed. Two sensitivity analyses and one normal
soft-tissue anchor, all runnable from committed data, were added. Figure 1 was replaced.

Of the review's 50 revision items, 46 are applied in full, 3 in part and 1 is declined. The
partials are items 23, 41 and 42, each for a stated reason; the decline is item 44. All four are
recorded in the final section.

## Major points

**1. The concordance criterion is not a test, and every headline count depends on it. — APPLIED.**
Verified independently before adopting. ALCAM's GPL3290 contrast recomputes to *t* = 2.214 at df 8.5
with exact two-sided *p* = 0.0560, 95% interval [−0.024, +1.531] and within-platform BH *q* = 0.162;
GPC1's GPL6244 *q* is 0.067; on GPL6244 24 of 95 readable genes reach *q* < 0.05 and on GPL3290 16 of
78. Every one of those figures matches the review. Methods now state alpha 0.05 with
Benjamini-Hochberg applied within each platform across every gene on the 100-gene board that
produced a contrast there, explain why the platforms are corrected separately, and record that a
threshold on |*t*| of 2 is more permissive than a 95% interval at these degrees of freedom rather
than describing it as a readability aid. Every count in the abstract, Results and Conclusion is
re-derived. Tables 3 and 4 carry the 95% interval and *q* beside every Δ; Table S5 carries panel *p*
values. The superseded criterion and every count it changed are in Appendix A6 of the supplementary
file, per the repository's one-fact-one-place rule.

**2. The asymmetry is contradicted by the paper's own Table 5. — APPLIED, withdrawn rather than
restated.** The sentence "the surrogate's negatives transferred and its positives did not" is gone
from the abstract, Results, Discussion and cover letter. It is replaced by what the data support:
the ranking predicted tumour-tissue behaviour in neither direction. The counterexample is named in
the same passage: CD44, the antigen the surrogate ranks lowest of all 47 at −3.89 log2TPM with
*q* = 1.0, is one of only three genes on the whole board concordantly elevated in EMC tissue, and
ALCAM at −1.45 is elevated on one array. The two supporting negatives are reported with their
corrected values, neither of which survives. One finding emerged while re-deriving this that the
review did not have: of the 13 surrogate-selective antigens with a tissue reading, five show
significant movement and all five are downward, which is now stated in Results.

**3. "Eight antigens were selective" cannot be reproduced. — APPLIED.** The selective set is
pre-specified in Methods as every actionable antigen with BH *q* < 0.05, which is 18 of the 47
seeded. Table 1 reports all 18 with their *q* values, their normal-tissue verdicts and their
corrected cross-platform states, followed by the non-selective antigens the text discusses. Results
report that 13 of the 18 have a tumour-tissue reading and name the five that do not (ALK, ENPP1,
FGFR4, SLC34A2, STEAP1). The headline is now "none of the 13". The previous count, and the
disagreement between the text's eight and Table 1's nine, are registered in Appendix A6.

**4. DLL3 contradicts the empty intersection and Figure 1's shaded quadrant. — APPLIED. Verified,
and the claim was wrong.** DLL3 carries enrichment +0.29 with `selectivity_q` 0.0079 and
`selectivity_significant` true in `emc-surfaceome-scan.json`, and window RESTRICTED in
`emc-surface-normal-window.json`. The intersection is therefore not empty and the unqualified claim
is withdrawn. The manuscript now states that the intersection contains exactly one member, DLL3, and
places three qualifications in the same passage: DLL3 entered the prior as a positive control for
the classifier rather than as a candidate; its surrogate margin is +0.29 log2TPM at a class mean of
1.53, below the scan's own expressed threshold of 3.0, with 11% of class lines above that threshold,
so it is a small difference between two low values; and in EMC tumour tissue DLL3 is flat on both
arrays (Δ = −0.041, *q* = 0.53; Δ = −0.026, *q* = 0.99). The passage then states in terms that
nothing here measures DLL3 protein, its presence on the EMC cell surface, its density, or any
property of any DLL3-directed agent. GPC3 is named as the nearest non-member at *q* = 0.053. The
figure caption no longer contains an emptiness claim of any kind, because the figure was replaced.

**5. Half the GPL3290 comparator arm was processed differently, undisclosed. — APPLIED, with the
sensitivity analysis.** Confirmed against the verbatim annotations: the ten EMC and three
dermatofibrosarcoma arrays read "CRH" and mRNA, the three gastrointestinal stromal tumour arrays
read "UHR" and total RNA. Methods now disclose the mismatch in its own paragraph, Table 2 carries it
per arm, and Supplementary Methods S4 gives it in full. Every GPL3290 contrast is recomputed against
the three dermatofibrosarcoma arrays alone, which is reference- and input-matched on both sides. The
concordantly elevated set is unchanged; EGFR and PDGFRB join the concordantly lower set; 15 of 70
genes readable in both analyses change sign, none of them an antigen carried forward. The two
largest gains in significance are KIT and PDGFRB, which is what dropping a gastrointestinal stromal
tumour arm should produce and is reported as a check rather than as a finding. The mismatch is added
as the third live explanation for the CSPG4 platform disagreement in Results and Note N3, and it is
the one of the three that can be tested here: reference-matched, CSPG4 reads Δ = −0.518 (*p* = 0.096,
*q* = 0.18), so the mismatch does not account for the disagreement.

**6. Seven GSE24369 samples dropped silently, including the only normal soft tissue. — APPLIED in
full, including both analyses the review asked for.** The per-sample values for all 42 deposited
samples, and each sample's whole-array mean and standard deviation, are committed in
`emc-expression-panels-inputs.json`, so neither analysis required new data. Methods and Table 2 now
declare that the deposit carries 42 samples and that 35 enter the analysis, state the classification
rule, and point to new Supplementary Table S8, which lists all seven excluded samples with their
verbatim annotations. Adding the five solitary fibrous tumour arrays to the comparator arm changes
5 signs of 95 and leaves both concordance sets identical, so the exclusion changes no conclusion,
which is now established rather than assumed. The two pooled normal skeletal-muscle arrays are
reported as a qualitative anchor with explicit n = 2, pooled-RNA and single-tissue caveats and no
test: ALCAM's EMC mean z of 2.33 against their −0.52, with CSPG4, CD44, VCAN, BGN and FAP likewise
above them and GPC1, CD248 and SSTR2 not. Read as a control the anchor produced something the review
did not anticipate and the manuscript now states: both instrument positive controls are higher in
pooled muscle than in EMC (*ENO3* 2.76 against 0.46, *NR4A3* 1.37 against 0.72), because both are
muscle-expressed, so neither control discriminates this disease from that tissue.

**7. A committed `ratio_calibration` block is not reported, and two sentences disagree with it. —
APPLIED.** Table 3 and Table S6 carry both percentile columns. The SSTR2 sentence now names the
platform it is about and reports the sequencing reading beside it: mid-distribution and
indistinguishable from comparators on GPL6244, and 1.54 and 1.37 times the two medians at the 89th
and 84th ratio percentiles in the sequencing cohort, "the top sixth of the transcriptome against
both arms", at n = 4 with no test. The B7-H3 sentence in the Discussion is rewritten to "not a
differentially expressed EMC address on either array platform" with the sequencing reading and its
n = 4, three-peak basis in the same clause.

**8. The class definition does not match the artifact, and the abstract misstates sizes. —
APPLIED.** Methods and Supplementary Methods S2 now name the six subtypes actually present, state
that desmoplastic small round cell tumour was sought and matched no line, and state that alveolar
rhabdomyosarcoma, a skeletal-muscle-lineage tumour, entered through the *alveolar* string. S2 adds
the reason this matters here specifically: the composition of the surrogate is the argument of the
paper. The abstract gives 2,826 candidates of which 2,692 were scanned, and 76 class members of
which 45 carry expression data. The class-lineage breadth is also added to the Limitations.

**9. The abstract omits CSPG4. — APPLIED.** The abstract's Results now carry "CSPG4, never scanned,
rose on one array and in the sequencing cohort and is held open". The one-array, one-peak, n = 4
basis is stated in Results and in the Conclusion rather than in the abstract, because the abstract
is at 199 of 200 words; the abstract's own resolution sentence prevents the clause from being read
as a positive result.

**10. Panel-level and gene-level movement judged by different standards. — APPLIED.** Panel *p*
values are computed from the committed *t* and degrees of freedom and reported in Table S5 and in
the text. The stromal and matrix panel is *p* = 0.095 and *p* = 0.097, so it does not move on either
platform under the rule applied to genes, and it is removed from the Discussion's surviving
negatives. The antigen-presentation panel is reported the same way. Table S5 also states why panel
*p* values are not corrected across panels and gives the uncorrected value so a reader can apply
their own rule.

**11. Two novelty and priority claims exceed the screen, which was run at a fraction of its depth. —
APPLIED, and the screen was re-run rather than the claim merely qualified.** The full texts were
already fetched and sat on the repository's `literature-cache` branch, so the deeper screen cost
nothing. Of the 237 full-text files, 129 name the disease or one of its fusions, 151 carry a
surface-antigen or immunotherapy term, and 81 carry both; in none of the 81 does ALCAM/CD166,
CD248/endosialin, CD276/B7-H3, FAP, PRAME or SSTR2 appear within 2,000 characters of a mention of the
disease. Committed as
[`emc-prior-art-fulltext-screen-2026-08-10.json`](../../literature/emc-prior-art-fulltext-screen-2026-08-10.json)
with its exact term patterns and its stated limits. The priority sentence is nonetheless deleted,
not rescued: a measured absence in one open-access corpus does not establish a first. The
field-level claim is rescoped to this programme's own prior state, noting that the deposits were
known and cited, including as reference 7, and that what was missing was the probe-to-symbol bridge.

**12. The stated provenance chain for seven references is wrong. — APPLIED.** Verified:
`remaining-reference-metadata-2026-08-09.json` carries complete records for PMIDs 35974707,
34340159, 25613900, 30373828, 10537274, 12378528 and 28076709. It is named in the References
preamble and in Data availability. Appendix A4 is rewritten to record that the seven were resolved
and where, quoting the superseded sentence verbatim and saying why a stale correction register is
the worst available arrangement. The Limitations sentence about citations "marked in the reference
list as not yet retrieved" is deleted. One of the seven, the NETTER-1 report, is no longer cited
because the sentence it supported was cut, and Appendix A4 records that too.

## Minor points

1. **ALCAM's Table 1 *q*. — APPLIED.** Printed as 1.0.
2. **LRRC15's window verdict. — APPLIED.** Printed as ENHANCED_BROAD.
3. **"Four limits" against five. — APPLIED.** Methods say five and name the fifth, that the scan
   holds no observation of FAP in this disease, at the point the FAP discussion rests on it.
4. **"Supplementary Tables S1 to S8" against an SI ending at S7. — APPLIED**, by making the
   statement true: the SI now ends at S8, the added table being the excluded-sample list.
5. **Note and Methods labels collide. — APPLIED.** Supplementary Notes are renumbered N1 to N5 and
   every main-text and cross-reference pointer is updated.
6. **Table S2 titled "complete" with 25 of 46 rows. — APPLIED.** All 46 antigens the artifact holds
   are given, controls labelled as controls.
7. **`plasma_membrane_confirmed`, and window verdicts in Table 5. — APPLIED.** Table S2 carries the
   field for every row with the subcellular annotation it rests on, and a sentence stating that the
   annotation is immunofluorescence-based so a false value records the absence of that evidence
   rather than evidence of absence. ALCAM's is false with vesicles as its only annotation, noted in
   both files. Table 4, the concordantly elevated table, carries a normal-tissue verdict column;
   VCAN reads as a vital or immune liability, CD44 as broad, GPC1 as enhanced-broad, ALCAM as
   restricted, and BGN is not in the filter, which the table says rather than leaving blank.
8. **CD248 grouped with FAP under stromal blindness. — APPLIED.** Methods carry the artifact's own
   narrowing: the instrument cannot see a gene that only stroma expresses, and mesenchymal tumour
   cells transcribe CD248 and PDGFRB, so those two are not the LRRC15 case. Note N1's L2 carries the
   counter-reading in full.
9. **Two clinical precedents. — APPLIED.** The masked, protease-activated CD166-directed conjugate
   is cited beside the ALCAM exposure demotion (PMC9365353, doi 10.1158/1078-0432.ccr-21-3656), and
   the negative randomised CD248 trial (PMC6618088, doi 10.1002/cncr.32084) and the 514-case
   soft-tissue sarcoma immunohistochemistry series (PMC4985356, doi 10.1038/bjc.2016.214) beside the
   CD248 inversion, each drawn from the committed precedent records and each stated as not an EMC
   observation. They are cited by identifier rather than by a numbered reference entry because the
   committed records carry title, journal, year and identifiers but no author list or pagination,
   and the References preamble now says so; writing an author list no retrieval holds is the failure
   this repository's citation gate exists to prevent.
10. **PRAME's undefined ratio in a ratio column. — APPLIED.** The cell reads "undefined" and the
    caption carries the explanation.
11. **RET. — APPLIED**, by the first of the two options offered. Methods state that the sequencing
    panel carries genes requested by other reads of the same deposit and was not assembled as a
    surface-antigen panel. Table S6's note repeats it and names RET and its percentile explicitly,
    so a reader who checks the artifact finds the gene accounted for rather than omitted.
12. **Whether the 10 GPL3290 EMC arrays are 10 patients. — APPLIED.** Methods state that one sample
    carries a parenthetical repeat marker in its deposit title, so they are 10 libraries and the
    analysis does not assert 10 patients.
13. **Whether the 32 sarcoma libraries are 32 tumours. — APPLIED.** Methods state that the artifact
    records replicate ties, so that arm is 32 libraries rather than 32 tumours.
14. **Appendix subsections out of order. — APPLIED.** A1 to A7, in order.
15. **Appendix packaging, the editorial comment block, the ORCID placeholder. — APPLIED, with the
    comment block kept for a stated reason (see the final section).** The whole appendix moved into
    the supplementary file as a version-history register, which also keeps the repository's
    correction-register rule satisfied, and its glyph warnings were stripped. The ORCID placeholder
    line is deleted and the cover letter states that the author holds none. Moving the register
    broke a correction-marker registry entry that pointed at the main text, which was repaired in
    the same pass and is recorded in the systems map.
16. **Salted-hash jitter. — APPLIED by replacement**, see Major 4 and the display-item note.
17. **EPHB4 and MCAM labels overprint. — APPLIED by replacement.** The new figure gives every
    antigen its own row.
18. **The unreadable-on-GPL3290 list is incomplete. — APPLIED.** Methods now give six: CD248, CD276,
    SSTR2, GPC2, ROR1 and B4GALNT1, consistent with the Limitations and with Note N2.
19. **Overlap with the published machine-learning surfaceome. — DECLINED, with reason.** The
    suggestion is right that this would convert an assertion into a measurement, and it should be
    done. It is declined here because that resource's membership table is not committed anywhere in
    this repository and this revision is scoped to re-analysis of committed data; computing the
    overlap requires fetching an external supplementary table, which is a retrieval rather than a
    re-analysis. The Methods sentence is unchanged in substance and continues to state that the
    resource exists, that it was not used, and why, without quantifying a difference nothing here
    measures.
20. **"Marker-grade". — APPLIED.** Deleted. The Discussion now states directional consistency across
    cohorts and says in the same sentence that no sensitivity, specificity or discrimination
    statistic is computed anywhere in this work.
21. **Duplicated AI-use statements. — APPLIED.** The Methods subsection is deleted and the
    Declarations statement keeps the reproducibility sentence that was the only content unique to
    the deleted version.

## Display items, word budget and figures

**Figure 1 replaced. — APPLIED.** The withdrawn figure placed a B4GALNT1 marker at x = 0, labelled
"(sel n/a)", inside a region annotated "target-worthy (selective and restricted) — EMPTY", because
the generator substituted zero for a missing selectivity value. That is a coordinate no artifact
carries, which makes it a figure-integrity defect rather than a presentation choice, and it is
treated as one. The replacement is the two-panel greyscale forest plot the review specified: one row
per antigen across the 18 surrogate-selective antigens, the 11 route-named addresses and the genes
elevated before correction, with the point estimate and exact 95% interval on each platform, the
surrogate *q* printed beside each label, significance carried by fill and shape rather than colour,
and an open triangle at the axis for "not readable on this platform" so an instrument statement is
visibly different from a null. Everything is black, white and one 40 per cent grey, so no colour
charge arises. Ordering is deterministic and the salted-hash jitter is gone. Rendered at 300 dpi with
a PDF companion at 7.4 inches wide, which the repository's figure-spec checker passes; source hashes
in `figures/emc-surface-figure-provenance.json`; the withdrawn PNG was deleted rather than left in
the tree. The figure generator is also added to the style linter's figure-source list, so its
rendered strings are now checked, which is the class of defect that list exists for.

**Table 3 deleted. — APPLIED.** The old Table 3, the surrogate-selective antigens read in tissue, is
superseded by the figure and is gone along with its preamble; the remaining tables are renumbered.
Display items are 4 tables and 1 figure.

**Word budget. — MET.** Main text 4,994 words of 5,000; abstract 199 of 200; 5 display items of 8;
17 references of 80. Measured with `research/manuscripts/submission_metrics.py`, which reports the
file as within limits. The cuts the review suggested were taken: the prior-art paragraph is
compressed into one sentence pointing at Supplementary Methods S6, the Methods AI subsection is
deleted, the four-explanations paragraph is compressed to one sentence pointing at Note N4, and
Table 3 and its preamble are gone. Further compression across Methods, Results and the Discussion
paid for the roughly 450 words the revisions added.

## Recommendation, framing and venue

**Reframed. — APPLIED.** The subject is now the transferability of a lineage-surrogate
surface-antigen ranking, with EMC as the worked case, carried through the title, the abstract's
Background and Conclusions, the opening paragraph of Background, the first paragraph of the
Discussion, the Conclusion and the cover letter. The reframe is not cosmetic: under correction the
transfer question is what the data actually answer, since the surrogate-selective set contains 18
antigens of which 13 read in tissue and none is concordantly elevated, while the antigen the
surrogate ranks lowest is one of the three that are.

**Venue changed to *Genes, Chromosomes and Cancer*. — APPLIED, with one deliberate divergence from
the review's implied consequence.** The editorial block records the change, its reasons and the
superseded framing, and the cover letter is rewritten to that journal. The divergence is in the
format envelope. The review's own note that "the repository already carries that venue profile in
`submission_metrics.py`" is true, but that profile sets `main_words` to `None` and the abstract to
250, because Wiley returns HTTP 403 for its per-journal author guidelines to CI and to a real
headless browser alike. Mapping this file to that profile would have traded the repository's only
publisher-page-verified limits for no limit at all, and let the manuscript grow because a page could
not be fetched. So the file is mapped to a new venue key,
`GCC-Research-Article-verified-envelope`, whose limits are the verified British Journal of Cancer
envelope applied as an explicit proxy and whose provenance string says in terms that these are not a
retrieved Wiley limit. The format is then valid at either journal and no rewrite is needed if the
submission is redirected. **The parent session should note that
`research/manuscripts/submission_metrics.py` now maps this file to that key rather than to
`BJC-Article`.** The zero-cost publication route is verified at primary source for both journals in
`research/literature/venue-fee-routes-2026-08-10.json`, so the venue change does not put the
no-cost constraint at risk.

**The resolution sentence. — APPLIED**, and computed here rather than quoted. On GPL6244 the median
95% interval half-width is 0.26 SD and the smallest elevation reaching significance was 0.06 SD; on
GPL3290 the corresponding figures are 0.96 SD and 0.66 SD. Concordance requires both platforms, so
the design is governed by the weaker one, and both the abstract and the Conclusion state that
elevations below about 0.7 SD on the limiting platform are not excluded. The Discussion states the
other half in the same paragraph: the same design did detect FGFR1 and PTK7 as concordantly lower
and VCAN, BGN and CD44 as concordantly higher, so the negative is a measurement rather than a
failure to measure.

**The normal-tissue prior is applied inconsistently between stages. — APPLIED.** Table 4 carries a
window verdict for every concordantly elevated gene, and the Results paragraph on those genes states
that the prior is decisive at stage 1 and silent at stage 2 elsewhere, then gives the verdicts:
VCAN a vital or immune liability, CD44 broad, GPC1 enhanced-broad.

## Declined and partial, with reasons

**Item 44 (Minor 19), the surfaceome overlap. DECLINED.** The suggestion is right and the
measurement should be made. It is declined for this revision because it requires an external
retrieval rather than a re-analysis of committed data: that resource's membership table is not
committed anywhere in this repository, and fetching a supplementary table from a publisher is
outside the scope of a correction pass. The Methods sentence continues to state that the resource
exists, that it was not used and why, without quantifying a difference nothing here measures.

**Item 23, the CSPG4 clause in the abstract. PARTIAL.** The clause is added. Its one-array,
one-peak, n = 4 basis is stated in Results and in the Conclusion rather than inside the abstract,
because the abstract is at 199 words of 200 and the sentence would not fit. The abstract's own
resolution sentence is what stops the clause reading as a positive result.

**Item 41, move the appendix and strip its glyphs. PARTIAL, then completed.** The appendix is
reordered A1 to A7 and moved into the supplementary file as a version-history register, which also
keeps the repository's correction-register rule satisfied. Its glyph warnings were stripped in a
second pass: the rule requires the superseded content, not the glyphs, and every superseded value,
verbatim quotation and status word is unchanged. Mid-sentence bold is retained in the register's
status tables, where it marks the verdict word in a table cell rather than emphasising inside a
sentence.

**Item 42, remove the editorial comment block. PARTIAL.** The ORCID placeholder line is deleted and
the cover letter states that the author holds none. The comment block is kept, rewritten, and
remains inside an HTML comment marked not for submission: it now carries the venue decision and its
reasons, the primary-source-verified fee route for both journals, and the format-envelope reasoning.
None of that reaches a rendered page or a submission portal, and a future session needs all of it.
Deleting it would move those facts nowhere, which is the failure the repository's one-fact-one-place
rule exists to prevent.

**A framing declined rather than an item.** The review states that including solitary fibrous tumour
"would move every Δ and t on the paper's primary lineage platform". Item 16 was run and every Δ does
move slightly, as adding five arrays to a comparator arm must; but 5 of 95 genes change sign and
both concordance sets are identical, so no conclusion in the paper moves. The manuscript reports the
second statement rather than the first.

**One item the review did not raise is corrected here.** The GSE24369 comparator arm was described
as "6 fibrosarcoma"; the verbatim deposit annotations read "Myxofibrosarcoma". Table 2, Methods and
Supplementary Note N5 now say myxofibrosarcoma. The artifact's internal class label is unchanged, so
the label and the annotation differ by design and the manuscript quotes the annotation.

**One of the review's own numbers is corrected.** The review states that the concordantly lower set
is FGFR1 and PTK7. Those are the two surrogate-selective members, and the manuscript says so, but
across the whole 100-gene board the corrected concordantly lower set has four members: ANTXR1,
B3GALT4, FGFR1 and PTK7. Table S7 reports all four. Similarly, the review describes CDH11 as
significant on both platforms with opposite signs; under correction CDH11 reaches significance on
GPL3290 only (*q* = 0.034) and not on GPL6244 (*q* = 0.055), so it is a single-platform movement and
the only discordant-opposite-signs gene on the corrected board is PSMB9.
