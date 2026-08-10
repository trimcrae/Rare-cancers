---
id: DOC-NR4A3-FUSION-TRANSCRIPTIONAL-OUTPUT-REVIEW-RESPONSE
title: "Response to review — nr4a3-fusion-transcriptional-output.md (2026-08-10)"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: A point-by-point response to the simulated internal review of the transcriptional-output manuscript, recording what changed, where, and what was declined and why.
scope: Response to one review of one manuscript. Reports no new disease result and asserts nothing about efficacy, selectivity, safety, a therapeutic window or clinical readiness for any agent, target or gene.
audience: [maintainers, external reviewers]
date: 2026-08-10
last_verified: 2026-08-10
---

> **THIS RESPONDS TO A SIMULATED INTERNAL REVIEW WRITTEN BY AN AI REVIEWER INSIDE THIS REPOSITORY.**
> It is not correspondence with *Genes, Chromosomes and Cancer*, with Wiley, or with any journal,
> editor or referee. No journal has seen this manuscript, and nothing here may be quoted or forwarded
> as if it were a reply to a real referee report. The review it answers is
> [`nr4a3-fusion-transcriptional-output-peer-review-2026-08-10.md`](./nr4a3-fusion-transcriptional-output-peer-review-2026-08-10.md).

# Response to review

**Manuscript (revised title):** *The published direct-target catalogue of the EWSR1::NR4A3 fusion is
three genes wide, and none is separable from disease association in the available EMC expression
record.*

**Summary of the outcome.** 36 of the 37 revision items were applied: 31 in full, and 5 in a
qualified form that is stated at the item (12, the class-B split, without the primary/sensitivity
swap; 15, the occupancy multiplicity, in the second form the reviewer offered; 17, seed sensitivity,
with the half that is not computable named as such; 27, an SI label corrected in prose but not by
hand-editing a producer's artifact; 31, references, with two carrying no identifier). **One item, 36,
is declined**: an ORCID belongs to a person and cannot be invented, so the placeholder is retained
and recorded as a residual author step. Separately, the structural moves of major point 13 were made
in full but its word target was not reached, which is stated under that point rather than counted as
applied. The central reframing was accepted. Everything reported below is offline, CPU-only and free;
no new bench work was done and no money was spent.

**New computation added in revision.** Nine sensitivity analyses the review asked for are computed
by a new producer, `research/modalities/nr4a3_fusion_targets_review_sensitivity.py`, writing
`research/modalities/nr4a3-fusion-targets-review-sensitivity.json`. It reads the committed inputs and
the committed primary artifact, re-derives every scored set's delta from the cached expression
values, and refuses to write unless all 22 re-derived deltas match the committed ones. They do, to
0.0.

**New literature retrieved in revision.** The gene-set-testing prior art was fetched rather than
recalled, through three dispatches of `.github/workflows/fetch-literature.yml` (query path, Europe
PMC, runs 31379169742, 31379451790 and 31380107406). The retrieved records are committed as
`research/literature/gene-set-null-prior-art.json`, which is what anchors the new identifiers for
`lint_citations.py`. Two references could not be retrieved and carry no identifier; see item 31.

---

## The central question: does the contribution survive?

The reviewer's arithmetic is correct, and I verified it independently before deciding what to do
about it.

**`null_sd × sqrt(n)` is constant, and the null is an independence null.** Over every scored set on
both platforms the product is 0.2528–0.2683 on GPL6244 (set sizes 10 to 250) and 0.6623–0.6969 on
GPL3290 (sizes 10 to 230), a spread of 5.9% and 5.1%. That is the signature of a mean of *n*
independent gene-level contrasts, and the residual decline at the largest sizes is the
finite-population correction for drawing without replacement from a 4,000-symbol pool. The
computation is `closed_form` in the new artifact.

**The closed form reproduces the band, but not exactly, and the difference is worth reporting.**
With σ = 0.261 (GPL6244) and 0.678 (GPL3290), `offset ± 1.96 σ / sqrt(n_readable)` reproduces the
resampled band edges to within 3–13% on GPL3290 and 14–36% on GPL6244. The larger GPL6244 error is
not noise: that platform's null delta distribution is left-skewed, so its empirical 2.5th and 97.5th
percentiles are not the normal ones (at n = 19 the resampled band is [−0.142, +0.105] against a
closed-form [−0.126, +0.109]). So the reviewer's "reproducible on the back of an envelope" is right
about the scale and about the independence property, and slightly overstated as a claim that the
resampling buys nothing. Both facts are now in §2.3.2, which states the closed form, gives σ per
platform, and gives the error of the approximation on each platform.

**The correlation correction was computed, and it does what the reviewer predicted.** For every set,
ρ̄ is the mean pairwise correlation between member genes' per-sample z after centring each gene
within each arm, so a set that genuinely separates the arms cannot inflate its own ρ̄; the variance
inflation factor is 1 + (n−1)ρ̄. Measured, at n = 17 on GPL3290 the aggregate's ρ̄ is +0.037 and the
factor is 1.60, so the aggregate falls from 88% to 69% of threshold. That is a smaller correction
than the reviewer's assumed ρ̄ of 0.05–0.10 would give (which would have put it at 55–63%), and it is
in the same direction. The asymmetry the reviewer identified is real and is now stated in the text:
the negatives are strengthened, and every positive scored against the competitive null alone sits on
the unprotected side. Under inflation, **none of the six PPARγ arms in SI §S4 clears**, which is a
substantive correction to the SI and is reported there.

**Conclusion, and what the paper now claims.** The size-matched empirical null is a competitive
gene-set null of a standard kind, implemented without the correlation term the prior art exists to
supply. It is not a contribution and is no longer presented as one. Every sentence presenting the
calibration as supplied, new, or this paper's contribution has been deleted from the title, the
abstract, §1, the Discussion and the cover letter. The contribution is now scoped to: the
evidence-typed catalogue and the negative it yields on real rare-tumour series; the measurement that
the native-to-fusion transfer assumption fails in both directions; the comparator-stratum dissection
and circularity finding; the calibrated occupancy audit; and the mapped absence of any chromatin
experiment on EMC material, with the discriminating experiment specified. The one method-side
element kept is a reporting convention (effect as a fraction of the detectability threshold), and
§2.3.1 says in as many words that it is presentational rather than a method.

**On the reframing and the venue.** Accepted, and carried through the title, the abstract, §1, the
Discussion, the Conclusion, the cover letter and the submission checklist rather than only the
introduction. The reviewer's suggested title is used essentially verbatim. The recommendation not to
split is also accepted, and the checklist now records that the GCC recommendation is conditional on
the reframing, with the fallback stated if it were declined.

---

## Major points

**1. No prior art cited, and the central methodological claim is a re-derivation.** Applied in full.
(a) Every sentence presenting the calibration as supplied or new is deleted: the title, abstract
sentence 4 ("We supply the calibration that refuses such a read"), §1.1's "That calibration is the
instrument this paper supplies", §4.2's first bullet and cover-letter ¶2. (b) §2.3.1 is a new Methods
subsection naming the competitive/self-contained distinction (Goeman and Bühlmann, PMID 17303618;
Irizarry *et al.*, PMID 20048385; Rivals *et al.*, PMID 17182697), restandardization (Efron and
Tibshirani 2007), CAMERA (PMID 22638577), ROAST (PMID 20610611), `singscore` (PMID 30400809),
expression-bin-matched control sets (PMID 27124452), GSVA (PMID 23323831), ssGSEA (PMID 19847166) and
GSEA (PMID 16199517), and stating that the only non-standard element is the fraction-of-threshold
reporting convention. (c) Retitled per point 12. (d) No methods note is attempted, and §2.3.1 says
that presenting this as a method would require a CAMERA benchmark (PMID 32026945).

**2. The null is an independence null.** Applied in full. See the section above. `null_sd × sqrt(n)`
constancy, the closed form with its per-platform error, ρ̄, the variance inflation factor and the
inflated threshold are all in §2.3.2, in Table 4 of the main text and in Table S2 for every scored
set. Unqualified competitive-null language is confined to the negatives, and the three PPARγ arms
the SI already flagged as resting on the competitive null alone are now joined by the other three:
under inflation none of the six clears, and SI §S4 says so before the permutation results.

**3. The 17-gene band quoted as 19, and the illustrative *t*.** Applied in full, and the artifact
was checked first. `set_scores.A_plus_B_all_dna_binding` on GPL3290 records `n_genes_readable: 17`,
`genes_not_readable: [ICAM1, MYH7]`, `null_q025: −0.29715`, `null_q975: 0.37648`. All three
occurrences now read 17 and say it is the readable size. (b) The *t* is attributed to this paper's
own aggregate rather than to an arbitrary set, in the abstract, §1.3 and §3.4. (c) The null
distribution of *t* was computed from the same 4,000 draws: at n = 17 on GPL3290 the 95% band for
*t* is [−3.31, +4.35] and 9.9% of random sets print a larger absolute *t*, so the claim now has a
computed basis on the scale it is made on. The superseded values are in Appendix A.

**4. Set D is neither independent nor a fair benchmark.** Applied in full. Set D shares *DKK1*,
*MAN1A1* and *NMB* with set E, and all three are among its 18 GPL3290-readable members. Re-scored
without them in one resampler, the clearance falls from 11.5-fold to 10.6-fold on GPL6244 and from
4.1-fold to 2.7-fold on GPL3290; both values are in Table 4 and Table S2's companion in SI §S3.7.
Set D is relabelled throughout as "a published EMC expression signature" and, in the text, as "a
positive control selected on the same contrast", with the winner's-curse argument stated. "The
instrument reads this disease, not this set" is deleted as a general instrument claim and replaced
by the narrower statement the reviewer proposed.

**5. "A bounded negative, not an underpowered one".** Applied in full; the phrase and every
equivalent are deleted. Replaced with an interval statement, computed by inverting the exact
label-permutation test: the aggregate's delta on GPL3290 is +0.330 with a 95% permutation confidence
interval of [+0.092, +0.565] (all 8,008 assignments enumerated), and on GPL6244 +0.040 with
[−0.082, +0.163] (sampled, 20,000 seeded assignments per shift, because C(35,6) = 1,623,160 cannot
be enumerated 40 times per bisection; the method is labelled as sampled). The detectability figure
is stated as what it is: a true shift larger than 0.15 SD on GPL6244 or 0.46 SD on GPL3290 would
fall outside the size-matched band four times in five, and smaller shifts are not excluded.

**6. The occupancy multiplicity arithmetic.** Applied in the second of the two forms the reviewer
offered, and the first is declined with a reason. The binomial tail is withdrawn from §3.8, Table S9
and the figure caption, and the reason is stated in the text: the empirical p-values are ranks within
a 198-gene panel of small integer peak counts, heavily tied (*PPARG* returns exactly 1.00 in 11 of
its 12 experiments), and the 36 tests share three genes, one background panel and peak sets that
overlap by construction. The raw counts against the panel column are reported instead, which the
reviewer described as the honest and sufficient reading. **The permutation over panel genes at fixed
peak-set depth is not computable from the committed artifacts**: `nr4a3-fusion-targets-occupancy.json`
records `n_panel_genes_at_or_above` per focus gene and the panel's overall hit rate, not the panel's
per-gene peak counts, and `emc-ret-cistrome.json` carries the same summary. Running it would require
re-intersecting the peak files, which are not in the repository. That limit is stated in Table S9's
note rather than left for a reader to discover.

**7. §3.12 miscounts the occupancy hits.** Applied in full, and verified against
`per_gene_summary`: *ENO3* has `n_experiments_enriched_at_0_05: 2`, at p = 0.0348 (normal parotid
gland, NR4A3) and p = 0.0498 (`SRX1653203`, NR4A1); *PPARG* and *SEMA3C* have none. Both of the two
hits are therefore *ENO3*'s, and §3.8, §3.9 and the Conclusion now say so. "No class-A gene exceeds a
background panel in any NR4A peak set" is deleted as written and replaced by the correct statement,
that none exceeds it after accounting for the 36 tests.

**8. The size-1 null applied to genes measured on fewer samples.** Applied in full, all three parts.
(a) `n_EMC / n_comparator` columns are printed in Table S3 and stated in §3.3 for the two genes where
it matters (*PLAGL1* 8 versus 6, *PPARG* 10 versus 5; only 42 of the 78 readable genes have the full
10 versus 6). (b) The size-1 null was redrawn under each gene's own observed sample set, over the
same pool: the gene-specific bands are 1.6–3.4% wider than the platform-wide band and **no grade
changes**. *PLAGL1* on GPL3290 remains outside its own band at p_emp 0.012 against 0.013. The full
table is SI §S3.4. (c) The assignment-count sentence in Methods is corrected: it now says every
reported permutation p is exact for the design that gene or set actually has, that the enumeration is
complete in every case, that it ranges from 286 to 1,623,160, and that *PLAGL1* and *PPARG* each
enumerate 3,003.

**9. Class B is not one evidence class.** Applied, except for the primary/sensitivity swap, which is
declined with a reason. B1 (6 genes: *SMPX*, *CDKN2AIP*, *GLS2*, *SDHA*, *COX5A*, *PDP1*) and B2 (10
genes) are defined in §2.1, labelled per row in Table S1, and scored. **The result is not neutral and
is reported at full weight**: A+B1 does clear its uninflated size-matched threshold on both platforms
(110% at p_emp 0.039 on GPL6244; 191% at p_emp 0.0015 on GPL3290), while A+B does not. It does not
clear the inflated threshold on GPL6244. **B1 alone clears nothing** (22% and 20%), so the A+B1
clearance is carried by the three class-A genes, whose individual readings are already reported and
are separately confounded (*ENO3* is the positive control, *PPARG*'s GPL3290 cell is circular,
*SEMA3C* is comparator-driven). **Declined: making A+B1 the primary aggregate.** The subset was
defined on evidence grounds rather than on the data, but it is the subset that clears, and
re-designating the primary set after seeing which one clears is the manoeuvre the calibration exists
to prevent. Both are reported, with A+B primary and A+B1 as a sensitivity, and §3.7 states the reason
so a reader can disagree with it.

**10. *MYH7* is both a class-B target and a muscle control, and the muscle control has no
calibration.** Applied in all three parts, with (a) taken in the second form the reviewer offered.
*MYH7* is kept in the marker panel and the conflict is stated explicitly in §3.5, in Table S7 and in
Limitation 13; removing a marker after seeing its value is a choice a reader cannot check, which is
why it is flagged rather than dropped. (b) All four markers are put through the same size-1 null the
class-A genes face: on GPL6244, *ACTA1* p_emp 0.161, *MYH7* 0.294, *MYL1* 0.064 and *PYGM* 0.105, all
inside their band, while *ENO3* is outside it at 0.023. (c) The sentence is weakened exactly as
asked: three of the four sit at or below zero and the fourth moves +0.142, about 45% of *ENO3*'s
+0.315. Note that *PYGM* is not readable in the primary input cache and was merged from the secondary
cache the confound module already unions, under a guard that the sample order and the per-sample
background match exactly.

**11. §3.3's instrument-control count is arithmetically wrong.** Applied in full, and the census was
recomputed from `controls.checks` rather than re-read from prose: 8 cells, 7 computable, 6 gradeable,
6 agreeing, 0 disagreeing, and 4 of the 6 agreements outside-band and therefore falsifiable. §3.3 is
rewritten to the reviewer's proposed form, with the per-gene n added. The superseded count, and the
fact that the sentence had already been corrected once from "four of four", are in Appendix A.

**12. The paper does two jobs.** Accepted, and carried through every document. The title is the
reviewer's. The abstract opens on the disease and reaches the catalogue in its third sentence. §1 now
runs disease, then the two questions, then the limits of an uncalibrated read; the calibration is
Methods §2.3 with its prior art in §2.3.1. The cover letter's first substantive paragraph is the
catalogue and the second is the mapped absence; the null appears once, in a methods paragraph, and
says it is not new. The submission checklist §1 records that the recommendation was re-examined a
second time and now depends on the reframing, with the fallback if it were declined. **The
recommendation not to split is accepted**, for the reviewer's reason.

**13. Length and display items.** Applied, and partially: the structural moves were made in full,
the word target was not reached. Moved to the Supplementary Information in full: Appendix B
(compressed into §4.3 and Table S10), the NBRE motif scan (SI §S6, with three sentences retained in
§3.8), the fourth-cohort search and its table (SI §S8, with the result compressed into §2.2 and
Limitation 1), the cohort-search method (SI §S8), the second half of the confound-audit method
(SI §S5), the occupancy search narrative (SI §S7), and Tables 1, 4, 6, 7 and 9 (now prose in §2.1 and
Tables S3, S5, S8 and S9). Figure 2 and Figure 5 moved to the SI as Figures S1 and S2. Kept in the
main text: Tables 1–4 and Figures 1–3, which is seven display items, down from 15. **Appendix A is
retained in the main-text file but marked as repository record stripped at submission**, alongside
the YAML frontmatter, because this repository's own rules require a superseded value to stay
recorded and an appendix is where that bookkeeping belongs; it is not part of the submitted PDF.
**The main text fell from 12,160 words to 9,015, not to 5,000–6,000.** That is a 26% cut against a
50% target and I have not closed the gap, for a reason worth stating plainly: the same review
required a new prior-art subsection, a measurement of the null's independence property, a
correlation correction reported for every set, six further sensitivity analyses and an extra
limitation, all of which are main-text content. A further cut to 6,000 would come out of the results
this revision has just been asked to strengthen. If length is a condition of acceptance, the next
material to move is §3.8's surrogate-occupancy paragraphs and §3.5's stratified paragraph, both of
which have fuller versions in the SI already.

**14. The abstract.** Applied in full. The factual error is fixed: "In three cohorts on three
platforms" is gone, and the aggregate is reported "on the two readable array platforms", since the
3SEQ arm carries no set score. The four cuts the reviewer specified are made, the 19→17 correction
lands in the rewritten sentence, and the abstract is **250 words** by the packet's counting rule
(`submission_metrics.py`), which no longer flags this manuscript. The believed 250-word limit remains
search-derived and unverified, and the checklist says so.

**15. Repository register in a submission text.** Applied in full. Both files are added to
`lint_style.py`'s `TARGETS` and the gate is at zero errors for both. All decorative glyphs are gone
from both files, mid-sentence bold is removed, sentence-shaped headings are converted to noun
phrases, em-dash density is down from 12.2 to 1.2 per 1000 in the main text and from 15.8 to 0.0 in
the SI, bold density from 16.7 to 4.6 and from 23.1 to 6.2, the full-capital sentences are gone, and
the sentences asserting the paper's own candour ("Stated at full honesty", "and that has to be said
plainly", "rather than merely conceded") are deleted. Appendix A is exempt by the gate's own rule,
which is where the supersession bookkeeping belongs.

---

## Minor points

**1. The 42–70% citation share.** Applied. The committed probe supports 42% (Filion, 22/52), 54%
(Subramanian, 27/50) and 33% (Kim, 4/12); Brenca's total-citation query returned `hit_count: null`,
so no share is available for it and the 70% traces to nothing. §1.2 now gives the three measured
shares and states that Brenca's cannot be computed. The full table is SI §S2.1.

**2. Kim 2016's exclusion from the "four to six EMC reviews" claim.** Applied. The counts are Filion
4, Subramanian 6, Brenca 5 and **Kim 0**, and §1.2 now names Kim's figures and says in the same
sentence that it is the source of the gene that survives every test below.

**3. The percentile denominator.** Applied. 14,120 is the deposit's gene count; the percentile ranks
within the 13,708 genes with a computable EMC/normal ratio and the 13,247 with an EMC/sarcoma ratio.
Corrected in §2.5, §3.7, §3.9 and Table S8, and in Figure 3's column header.

**4. 198 versus 203 background-panel genes.** Applied. §3.8 now carries the clause: 211 genes resolve
on hg38 and minus the 8 focus genes gives 203 for the GSE243553 intersection, while the motif scan
resolves 198 windows, and the two counts are not interchangeable.

**5. *ENO3*'s GPL6244 delta at two values.** Applied by weakening the claim, which is the honest of
the two options: the two implementations give +0.8075 and +0.8074, so §3.3 now says three decimal
places rather than four. Recorded in Appendix A.

**6. Table 6's duplicate strata.** Applied. Table 6 has moved to the SI as Table S5, whose column
headers now record that `class_desmoid_fibromatosis_only` and `non_myxoid_comparators_only` are the
same six samples on GPL6244, and that `class_DFSP_only` and `reference_pool_matched_only` are the
same three on GPL3290. §3.5 states "five stratified contrasts over four distinct comparator sets",
and Figure 3's stratum cell prints "worst of 5 contrasts over 4 sub-arms".

**7. The stratum whose p §3.6 quotes.** Applied. §3.5 now cites the myxofibrosarcoma-only stratum by
name and points at Table S5, where the value lives.

**8. "Least favourable stratum".** Applied. §3.5 defines the summary rule explicitly as the largest
permutation p, and then says in the same paragraph that this definition is the wrong one for
*SEMA3C*, whose scientifically worst stratum is the significant reversal against desmoid fibromatosis
(−0.645, p = 0.015), an effect in the opposite direction.

**9. `class_fibrosarcoma_only` in SI Table S4.** Applied at the level a text edit can reach: the
column in what is now Table S5 is relabelled `class_myxofibrosarcoma_only`, with a note that the
producing artifact still carries the internal label `fibrosarcoma` in `class_counts`. **The artifact
itself is not hand-edited**, because it is a producer output and editing it by hand would break the
one property that makes it trustworthy; renaming the key is a producer change that would invalidate
the committed `class_counts` comparison in the confound module's own parity check, and it is recorded
in Appendix A as an open cosmetic defect rather than silently patched.

**10. Table 8 labelled by requested size.** Applied. What is now Table 4 prints "(readable size,
GPL6244 / GPL3290)" in its stub and gives both numbers per row; Table S2 prints requested and
readable in separate columns for every set.

**11. "12-fold" versus 11.9-fold.** Applied; the heading is gone entirely in the restructure and the
value is 11.9-fold throughout, matching the committed artifact.

**12. "42,000-spot" versus 43,008.** Applied; Table 1 says 43,008 probes.

**13. The seeded 4,000-symbol pool.** Applied in part, and the part that cannot be done is stated
rather than implied. Redrawing the 4,000 random *sets* under 20 further seeds moves the 97.5th
percentile by a relative standard deviation of 1.6–3.1%, which is the reviewer's ±2% estimate
confirmed to be about the right size; the committed percentile sits 2.9% above the mean of those 20
draws. No verdict changes. **The pool itself cannot be redrawn from a committed artifact**, because
`nr4a3-fusion-targets-inputs.json` carries the 4,000 symbols that were drawn and not the platform
universe they were drawn from, so pool-composition error is not bounded, and SI §S3.2 and Limitation
18 say exactly that rather than presenting the seed spread as the whole uncertainty. Why a subsample
was used at all is not recoverable from the record and is not asserted.

**14. Expression-matched control sets.** Applied, and the reviewer was right that this is the most
valuable free addition; it is also the one that damages the paper's own case most. Two
composition-matched nulls were computed for the aggregate and for set D, matching each draw's decile
composition to the real set's on mean value and on detection rate. On GPL6244 the aggregate reaches
42% and 36% of the two matched thresholds, so the negative is unchanged. On GPL3290 it reaches 87% of
the detection-rate-matched threshold and **106% of the expression-decile-matched one, clearing it at
p_emp 0.047**. That is reported in §3.7 and SI §S3.3, with the honest qualification that on a
two-colour platform the matched mean value is a mean log-ratio against a reference pool rather than
an expression level, so detection rate is the closer analogue there; both are reported and neither is
preferred. The aggregate negative holds under three of the four composition-matched nulls, is
marginal in the fourth, and holds under all four once the correlation inflation is applied.
Limitation 18 records it.

**15. No statistical method carries a citation.** Applied for Welch (PMID 20287819), the empirical-p
smoothing (Phipson and Smyth, PMID 21044043), the permutation framework and the gene-set methodology
(§2.3.1). **Benjamini–Hochberg is cited without an identifier**; see item 31 below.

**16. Figure 4's text collision.** Applied. The figure is regenerated at 18.4 inches wide with
shorter headers on three lines at 7.9 pt; the "NBRE motif" and "NR4A occupancy" headers no longer
overlap.

**17. Figure 4's 3SEQ colour rule.** Applied in the second form the reviewer offered, which is the
one that removes the contradiction rather than documenting it. The 3SEQ column is now neutral grey
for all three genes, with a legend entry "a rank, not a test"; the printed percentiles speak. The
undocumented ≥95th-percentile threshold that made *PPARG* "supported" at 84.0/96.4 while *SEMA3C* was
not at 94.2/92.6 is deleted from the generator, and
`test_every_cell_of_the_convergence_matrix_resolves_to_a_real_statistic` now asserts that the column
stays neutral.

**18. Figure 4's stratum column.** Applied. The header reads "GPL6244 comparator strata" and each
cell prints "worst of 5 contrasts over 4 sub-arms", computed rather than typed.

**19. A percentile used as an instrument.** Applied. §2.5 now ends by saying the axis contributes an
ordering and never a test; §3.9 and the Conclusion say "which is a rank and not a test" where the
3SEQ percentile appears; and Figure 3's column is neutral (minor point 17).

**20. Disambiguating Subramanian et al. 2005.** Applied. §2.3.1 names the GSEA paper as "Subramanian
*et al.*, PMID 16199517, a different paper from the Subramanian *et al.* 2005 EMC expression cohort
of §2.2 (PMID 15920699)", and both reference-list entries carry a cross-note.

**21. §2.7 did not disclose the query repair.** Applied. §2.7 has moved to SI §S8 in the
restructure, and the compressed cohort-search paragraph that remains in Methods (§2.2) discloses the
repair in its own sentence: four of the six queries first returned zero through a shared field
restriction, and both forms are recorded.

**22. Zenodo DOI timing.** Applied. Both the manuscript and the checklist now say **at submission**,
and the checklist records the superseded "at acceptance".

**23. ORCID placeholder.** **Declined, necessarily.** An ORCID is an identifier belonging to a
person, and inventing one would be exactly the class of fabrication the repository's first golden
rule forbids. The placeholder is retained in both the title block and the cover letter, and it is
recorded as residual author step 1 in the checklist. It is not a defect an agent can close.

**24. Cover letter paragraph 2.** Applied. The letter now leads with the three-gene catalogue and
then the mapped absence of an EMC chromatin experiment; the null appears once, in a methods
paragraph that states it is not new.

---

## Revision list, item by item

| # | disposition | where |
|---|---|---|
| 1 | applied | title, running title, frontmatter, cover letter, checklist |
| 2 | applied | §1.1–§1.3 rewritten; the novelty framing deleted |
| 3 | applied | abstract, §1.3, §3.4; the *t* attributed and the *t*-scale null computed |
| 4 | applied | new §2.3.1 |
| 5 | applied | §2.3.2, with the closed form's error measured per platform |
| 6 | applied | new producer; Table 4, Table S2, §2.3.2, SI §S4 |
| 7 | applied | §3.7; permutation CI and detectability replace the power language |
| 8 | applied | §3.7, Table 4, SI §S3.7; set D relabelled and re-scored |
| 9 | applied | §2.4, §3.3, SI §S3.4 |
| 10 | applied | §2.6 |
| 11 | applied | §3.3, Table S3 |
| 12 | applied, except the primary/sensitivity swap | §2.1, §3.1, §3.7, Table S1, SI §S3.6 |
| 13 | applied | §3.5, Table S7, Limitation 13 |
| 14 | applied | §3.5 |
| 15 | applied in the reviewer's second form | §3.8, Table S9, Figure 3 caption |
| 16 | applied | §3.8, §3.9, Conclusion |
| 17 | applied, with the pool-composition half stated as not computable | SI §S3.2, Limitation 18 |
| 18 | applied | §3.7, SI §S3.3, Limitation 18 |
| 19 | applied | abstract, now 250 words |
| 20 | applied, except Appendix A, which is retained as repository record stripped at submission (major point 13) | SI §S3, §S5, §S6, §S7, §S8, §S10 |
| 21 | applied | Tables S3, S5, S8, S9; Figures S1, S2 |
| 22 | applied | §1.2, SI §S2.1 |
| 23 | applied | §2.5, §3.7, §3.9, Figure 3 |
| 24 | applied | §3.8 |
| 25 | applied | §3.3, Appendix A |
| 26 | applied | §3.5, Table S5 |
| 27 | applied in the prose and the SI table; the artifact key is not hand-edited | Table S5, Appendix A |
| 28 | applied | Table 4 stub, Table S2 |
| 29 | applied | §3.7, Table 1 |
| 30 | applied | `nr4a3_fusion_targets_figures.py`, regenerated |
| 31 | applied, with two references carrying no identifier | References 15–29 |
| 32 | applied | §2.2 |
| 33 | applied | Data and code availability; checklist §7.2 |
| 34 | applied | `lint_style.py` TARGETS; both files at zero |
| 35 | applied | cover letter ¶1–¶4 |
| 36 | **declined** | an ORCID cannot be invented; residual author step |
| 37 | applied | checklist §1 |

---

## Item 31 in detail: the two references that carry no identifier

The revised Methods names Benjamini and Hochberg (1995, *Journal of the Royal Statistical Society
Series B*) for the false-discovery-rate correction and Efron and Tibshirani (2007, *Annals of Applied
Statistics*) for restandardization. **Neither reference carries a volume, a page range or a DOI in
the reference list, and neither may be completed from memory.** Three dispatches of the repository's
literature-fetch route returned no record for either, because neither journal is indexed by Europe
PMC; the queries tried and their outcomes are recorded in
`research/literature/gene-set-null-prior-art.json` under `not_retrieved`.

**Pre-submission task for the author, stated explicitly.** Read the volume, issue and page range of
both papers off the primary sources and complete references 28 and 29 before submitting. This is also
residual author step 3b in the submission checklist. An honest, flagged gap is the correct state for
these two entries until then; a plausible-looking identifier written from recollection is the
specific failure `research/manuscripts/lint_citations.py` was built to catch, and it would pass every
other gate in this repository.

Everything else in the reference list is reproduced from a retrieved record: references 15–27 from
`gene-set-null-prior-art.json`, and the rest from the machine-readable target catalogue, the
set-definition blocks or an existing curated reference list.

---

## Two numbers that exist twice, and why

Supplementary §S3.6 and §S3.7 score their comparisons in the independently implemented resampler of
the new sensitivity module rather than in the producer behind Table S2, because a within-table
comparison is only meaningful if both of its columns come from one draw. That leaves the A+B
aggregate and set D each printed at two slightly different values across the SI: 91% and 72% in
§S3.6 against 88% and 69% in Table S2, and 4.14× and 11.47× in §S3.7 against 4.25× and 11.94×. The
difference is the Monte-Carlo spread measured in §S3.2 and nothing else. **Table S2 and the primary
artifact own the reported figures; every value quoted in the main text, the abstract and the
Conclusion is theirs**, and both SI sections now say so in the paragraph above their table, so a
reader meeting the second value cannot mistake it for a correction of the first.

---

## One known follow-up the revision creates

Renumbering the Results sections leaves stale pointers in four producer docstrings and comments that
cite the manuscript by section: `nr4a3_fusion_targets_confounds.py` (§3.10, §3.12),
`gse243553_eno3_overlap.py` (§3.10, §3.11, Table 9), `emc_ret_target_scan.py` and `emc_sra_study.py`.
None of them reads a section number as a value, so nothing computed is affected and no artifact
changed; they are comments pointing at headings that have moved (§3.10 and §3.11 are now §3.8, §3.12
is now §3.9, and Table 9 is now Table S9). They are left for a pass that can re-run those lanes'
tests rather than edited here, and are recorded so the next reader finds them from this file rather
than by following a dead pointer.

---

## What a reader of the revised manuscript should notice that the old one did not say

Three readings added in revision damage the paper's own case and are reported at full weight rather
than buried.

**A+B1 clears where A+B does not.** Restricting the aggregate to the nine genes whose primary assay
paper was retrieved gives 110% and 191% of the uninflated threshold, against A+B's 39% and 88%. B1
alone clears nothing, so the clearance is carried by the three class-A genes; but a reader who
believes the review-asserted class-B rows should never have been in the aggregate has a numerically
different paper, and §3.7 says so.

**The aggregate negative is marginal under one composition-matched null.** On GPL3290 the aggregate
reaches 106% of an expression-decile-matched threshold, clearing at p_emp 0.047. It does not clear
the detection-rate-matched threshold, either threshold on GPL6244, or any of the four after
correlation inflation. Reporting only the uniform-draw null would have concealed this.

**The correlation correction removes all six PPARγ positives.** SI §S4 previously reported six arms
of which five were set-specific on at least one platform. Under the inflated threshold none clears,
and the section now says that before it reports the permutation results.
