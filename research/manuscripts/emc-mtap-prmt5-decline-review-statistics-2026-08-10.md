---
id: DOC-EMC-MTAP-PRMT5-DECLINE-STATISTICS
title: "Grounds to decline — statistical lens (emc-mtap-prmt5-hypothesis.md)"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: An adversarial statistical assessment hunting every quantitative ground on which the PRMT5 manuscript would be declined.
scope: Review of one manuscript. Reports no new result and asserts nothing about any disease or agent.
audience: [maintainers, external reviewers]
date: 2026-08-10
last_verified: 2026-08-10
---

# Grounds to decline — statistical lens

> **THIS IS A SIMULATED INTERNAL REVIEW, WRITTEN BY AN AI REVIEWER AT THE AUTHOR'S REQUEST. IT IS NOT
> CORRESPONDENCE FROM *GENES, CHROMOSOMES AND CANCER* OR FROM ANY OTHER JOURNAL, NOT A REAL PEER
> REVIEW, AND NOT A DECISION. No editor, no journal and no external referee has seen this manuscript.
> It exists to find the quantitative objections a hostile statistical referee would raise.**

Manuscript under review: `research/manuscripts/emc-mtap-prmt5-hypothesis.md`, with
`emc-mtap-prmt5-hypothesis-SI.md` and the five figures under `research/manuscripts/figures/`.
Read after forming an independent view: `emc-mtap-prmt5-hypothesis-peer-review-2026-08-10.md` and
`emc-mtap-prmt5-hypothesis-review-response-2026-08-10.md`.

Every number below is either (a) read from a committed artifact and named, or (b) computed by this
reviewer from `emc-expression-panels-inputs.json` and `emc-hypoxia-null-background.json` using the
same reduction the manuscript uses. Computations (b) are marked **[recomputed]** and the procedure is
stated so they can be repeated.

---

## Verdict

**Decline.**

The single strongest quantitative ground: **after the correction the paper itself elects to apply,
no reading in this manuscript that bears on its surviving hypothesis clears any conventional
threshold, and the paper nonetheless carries "a fusion-class rationale that survives" in its title,
"survives as a hypothesis" in its Discussion and Conclusion, and "reads higher in EMC … and ranks
first of the readable PRMT family" in its abstract.** The transcript evidence for the surviving
rationale is null. That is a defensible thing to publish; it is not a defensible thing to title.

Two secondary judgements follow from the work below and both cut against the paper:

- The corrected *p* the paper reports is not a property of the data. It is a property of two
  undeclared analysis choices. On the same code path, PRMT5's family-wise adjusted *p* is **0.00015
  and 0.000125** over the nine and six genes the paper actually reports, **0.097 and 0.064** over the
  curated panel cache, **0.208 and 0.238** over the merged family the paper chose, and **0.031** on
  GPL3290 if genes with missing data are excluded from that same merged family. The paper quotes one
  point from that range to two significant figures.
- Where the record settles which of those families is right, it settles it against the paper. The
  pre-specified endpoint of this read was *MTAP* loss, not *PRMT5* elevation, and the paper's own
  Appendix A records that the statistic was moved from the group to the gene during figure
  preparation. So the array-wide family is the correct one, the adjusted *p* really is ≈0.21/0.24 or
  worse, and there is no positive transcript result. The framing must change to match.

Counts: **15 grounds — 12 FIXABLE, 3 STRUCTURAL** (two of the three survivable at the cost of the
paper's thesis; one survivable with disclosure).

**What I checked and found sound**, because a decline is only credible if the verification is
symmetric: `emc_prmt5_multiplicity.py --check` reports REPRODUCES; I independently reproduced PRMT5's
adjusted *p* as 0.2081 and 0.2376 from the caches, and the null-max median of 5.418 that §3.5 quotes;
C(35,6) = 1,623,160 and C(16,10) = 8,008 are the correct labelling counts for a two-arm relabelling
of these designs; the Monte-Carlo standard error of 0.0029 is right for *p* ≈ 0.21 at *B* = 20,000;
the direction of the lower-bound claim in §2.3 is correct (the family-wide maximum is monotone in the
family as a set, so a subset family gives an adjusted *p* no larger than the full array's); *PRMT5*
does rank first of the 8 and 7 readable PRMT-family members **[recomputed]**; the correction is *not*
driven by degenerate low-variance genes, which was my first hypothesis and it failed — deleting the
bottom quartile of the family by minimum within-arm SD moves PRMT5's adjusted *p* only from 0.2376 to
0.2228 and from 0.2081 to 0.1683 **[recomputed]**; the figure provenance check passes on 10 files
against 5 artifacts; and the review response's two corrections to round one (solitary fibrous tumour
at +1.05 rather than +1.14, and not first on the pooled score) both reproduce exactly
**[recomputed: +1.0525; desmoid +0.95 > SFT +0.94 > EMC +0.93]**.

---

## GROUNDS TO DECLINE

### 1. The paper's framing asserts survival for a hypothesis whose transcript evidence is null on the paper's own analysis — FIXABLE

**Where.** Title; abstract; §4.1 "The fusion rationale survives as a hypothesis"; §5; falsifier
table F2/F7; cover letter.

**What is wrong.** §3.5, §4.4 and §5 all state the arithmetic correctly — adjusted *p* of 0.21 and
0.24, nothing below 0.05 but an instrument control — and then the surrounding prose carries a verb
the arithmetic does not support. "Survives" is doing the work of a result. What actually survives
correction, on the paper's own accounting, is: *ENO3* on GPL3290 at 0.010, which is a positive
control; and *MTAP* at 1.00, which is a non-rejection and not a finding (ground 5). The two
supports the Discussion then names for the surviving rationale — the Ewing result [3] and the motif
count of §3.7 — are respectively an experiment in another disease and a string scan on a committed
sequence. Neither is a measurement in EMC, which §4.1 concedes in the next sentence.

**Evidence.** §5 lists the rationale as "limited on three sides", one of which is "a family-wise
adjusted *p* that clears no conventional threshold on either" platform. A rationale limited by the
fact that its own primary statistic is null is not limited; it is unsupported by that statistic.

**Fix.** State in the abstract, §4.1 and §5 that the transcript evidence is null after correction and
that the hypothesis rests on the external literature and the sequence analysis alone. Retitle so the
first clause does not assert survival — the honest pair of clauses is a rationale that the transcript
data cannot support either way and an *MTAP* rationale the transcript data cannot close either
(ground 5).

---

### 2. The correction's family is undeclared and determines the result — FIXABLE

**Where.** §2.3 ("The family is every symbol two committed input caches hold"); §3.5 table; §4.4;
SI §S5c.

**What is wrong.** A max-statistic permutation controls the family-wise error rate *of a family*. The
paper never states which family its inference is over; it computes one and reports it as the answer.
§4.4 then says, correctly, that a family-wise correction "asks whether a maximum this large arises by
chance across the genes scanned, which is the right question for a gene chosen after a curated panel
and a genome-wide scan were examined, and the wrong question for a gene named in advance by a
rationale from another disease; both descriptions apply to *PRMT5* here." That sentence concedes the
inference is ambiguous and then leaves the reader with only one of the two numbers.

**Evidence [recomputed]**, same reduction, same labellings (all 8,008 on GPL3290; 20,000 fixed-seed
draws on GPL6244), only the family varied:

| family | n on GPL6244 / GPL3290 | PRMT5 adjusted *p*, GPL6244 | GPL3290 |
|---|---|---:|---:|
| the genes the paper reports (§3.5 table + *MKI67*) | 9 / 6 | 0.00015 (3 of 20,000) | 0.000125 (1 of 8,008, exact) |
| the curated panel cache | 1,857 / 1,611 | 0.0971 | 0.0642 |
| the merged family the paper uses | 5,449 / 4,848 | 0.2081 | 0.2376 |

The paper's conclusion — that the primary contrast does not survive — is produced entirely by the
third row. Note also that on GPL3290 the first row equals 1/8,008, i.e. the correction over the
reported genes is *identical* to the uncorrected exact *p*, because PRMT5's |*t*| is the family
maximum in the only labelling that reaches it. A reader is entitled to see that.

**Fix.** Report all three families in SI §S5c, name the one the inference is made over, and give the
reason (ground 3 supplies it). Do not report a single adjusted *p* without its family.

---

### 3. On GPL3290 disease class is perfectly collinear with submission batch, reference channel and within-study platform assignment — STRUCTURAL, survivable only by demoting the platform

**Where.** §2.1 table and paragraph; §3.6 "Splitting the comparator arm by reference is the
discriminating comparison"; SI §S1, §S5a; and everywhere GPL3290 supplies "the replication".

**What is wrong.** The paper discloses one of four perfectly-aligned strata and treats the other
three as absent. On this platform the EMC arm and the comparator arm differ simultaneously in
histology, in GEO submission block, in two-colour reference pool, and in the fact of having been
assigned to this array at all. Nothing in the data can separate them, and a permutation that
relabels these sixteen samples is therefore not exchangeable under any null the paper is testing.

**Evidence.**

- GSM accession blocks, from `emc-expression-panels-inputs.json` **[recomputed]**: DFSP =
  GSM89883–GSM89924 (reference `CRH`); GIST = GSM91381–GSM91405 (reference `UHR`); EMC =
  GSM98495–GSM98513 (reference `CRH-mRNA`). Three disjoint accession blocks, three references, three
  histologies, no crossing.
- Array-level covariates track the arms **[recomputed]**: per-array background mean −0.580 (EMC),
  −0.259 (DFSP), −0.426 (GIST); background SD 1.741 / 1.555 / 1.696; probes carrying a value per
  array 33,278 / 36,840 / 28,814 on average, with a whole-series range of 23,015 to 41,510 of 43,008.
  Because the *z* is taken against each array's own probe distribution, a *z* on this platform is a
  position within a probe set that differs by up to 18,000 probes between arrays. That is not
  disclosed anywhere.
- Platform assignment is itself confounded *within the source study*. The deposited summary the paper
  quotes in §2.1 describes GSE4303 as "ten EMCs and 26 other sarcomas"; §2.1 states that 36 samples
  are deposited across two platforms and that the 16 on GPL3290 are analysed. Those 16 are all 10 EMC
  plus 6 comparators, so **all EMC and only 6 of the study's own 26 comparator sarcomas landed on
  this array**. The paper never says this and never asks how the 6 were selected.
- The paper's own disclosure defeats its own remedy. §2.1 states that the deposit does not say whether
  `CRH` and `CRH-mRNA` name one pool or two, so the DFSP comparators are "matched by label" only;
  SI §S1 states the source cannot support "a comparison of EMC with the GIST comparators that is free
  of the reference-pool difference." Both halves therefore differ from every EMC tumour in the
  denominator of the measurement, and §S5a's conclusion — "The primary contrast keeps its direction
  and most of its size against either half, so the reference-pool difference does not manufacture it"
  — does not follow. Agreement between two confounded halves is not evidence against the confound.

**Why STRUCTURAL.** The confounding is in the deposit. No re-analysis, and no revision, can produce
an unconfounded contrast on this platform.

**Survivable how.** Demote GPL3290 from evidence to consistency check: report it as a second series
whose direction agrees and which cannot separate disease from batch, and remove it from any sentence
that says a claim replicates. That is survivable arithmetically and costly rhetorically, because
§4.1's "What survives correction is the replication" is the paper's only remaining positive
statement.

*(One thing the paper could have said and did not, in its own favour: the only reference-informative
contrast available is DFSP against GIST, and PRMT5 gives t = +0.24 across it — the reference pools do
not move this gene between the two comparator halves* **[recomputed]***. That is mild reassurance and
it belongs in §S5a. It does not rescue the arm, because neither half shares EMC's reference label.)*

---

### 4. The adjusted *p* is not robust to a second undeclared choice: on GPL3290 it moves from 0.238 to 0.031 when genes with missing data are excluded from the family — FIXABLE

**Where.** §2.3; §3.5; SI §S5c ("How fast the bound rises with the number of symbols scanned is
measured on the random symbols alone").

**What is wrong.** The correction's family on GPL3290 includes genes measured in a minority of the
sixteen samples. Under permutation, such genes hit the panel's three-per-arm floor, their arms
collapse toward *n* = 3, their Welch *t* becomes wildly unstable, and they dominate the family-wide
maximum — which is the quantity the adjusted *p* is read off. The paper's only sensitivity analysis
varies family *size*, which is the wrong axis; the sensitive axis is family *composition*.

**Evidence [recomputed]**, exhaustive over all 8,008 labellings both times:

| family | n | PRMT5 adjusted *p* | null max \|*t*\| p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| as built | 4,848 | 0.2376 | 5.634 | 9.698 | 17.812 |
| genes measured in all 16 samples | 3,126 | **0.0312** | 4.558 | 6.352 | 14.470 |

Supporting detail: 35.5% of the GPL3290 family has at least one missing value; the twenty genes that
most often attain the family maximum account for 23.9% of all 8,008 labelling maxima, and every one
of the top six (`SPATA31A1`, `LOC100506314`, `GUCA2B`, `MYO15A`, `MGAT5B`, `LOC285500`) is missing 9
or 10 of the 16 samples. A null-max 99th percentile of 12.3 and a maximum of 17.8, at Welch degrees
of freedom in the low teens, is a measurement artefact, not multiplicity.

An undisclosed convention compounds this: `_t_matrix` in `emc_prmt5_multiplicity.py` sets a gene's
|*t*| to **0.0** for any labelling where either arm falls below the floor. So the effective family
size varies by labelling, and the max is *deflated* for the affected genes. That biases the adjusted
*p* downward, which happens to be the direction favourable to the paper, and it is stated nowhere in
either document.

**Fix.** Report the complete-case family alongside the as-built one in §S5c, state the arm-floor
zeroing convention in §2.3, and replace the single quoted value in §3.5 and the abstract with the
range across defensible family definitions.

---

### 5. The *MTAP* closure reads a non-significant statistic as evidence of absence, and the paper's own SI says that is invalid — FIXABLE

**Where.** §3.2; §4.1; §5; abstract; falsifier F5. Against: SI §S5c.

**What is wrong.** §3.2 states: "It is also at a multiplicity-adjusted *p* of 1.00 on both platforms,
which is the one place in this paper where correcting for the number of genes examined strengthens
the argument rather than weakening it: the closure of this rationale is exactly what an adjusted *p*
of 1.00 states." It is not. An adjusted *p* of 1.00 states that in every one of 8,008 (or 20,000)
labellings, *some* gene in a family of ~5,000 produced a larger |*t*| than *MTAP* did. It carries no
information about whether *MTAP*'s difference is zero. SI §S5c says so in terms: "An adjusted *p* is
… not a statement that a reading is absent."

The asymmetry is the decisive problem. The same non-significance is read as *absence of evidence* for
*PRMT5* (§4.4, §5) and as *evidence of absence* for *MTAP* (§3.2, §4.1, §5, abstract, F5). One
statistic cannot mean both things in one paper.

**Evidence.** `emc-prmt5-multiplicity.json` records *MTAP*'s expected number of array symbols
reaching its observed |*t*| per labelling as 9,778 (GPL6244) and 592 (GPL3290). Those figures say the
family maximum swamps *MTAP*; they say nothing about *MTAP*.

**Fix.** Delete the sentence in §3.2 and its echoes in §4.1, §5 and the abstract. Replace with the
power statement of ground 6 and the per-sample statement of ground 7, which is what actually bears on
the closure.

---

### 6. The *MTAP* negative is not powered, no detectable effect size is given, and the test is mis-specified for the alternative — FIXABLE

**Where.** §3.2; §4.1 "The *MTAP*-locus rationale is closed at transcript level by the data reported
here"; §5; §4.4 "the locus result rests on six tumours".

**What is wrong.** Three separate defects, all in one negative.

**(a) No power or interval is reported anywhere in the paper.** **[recomputed]** On GPL6244, 6 versus
29, *MTAP*'s difference is **+0.121 log2 (95% CI −0.197 to +0.439)**, i.e. **1.09-fold, CI 0.87 to
1.36-fold**; on the *z* scale +0.053 (CI −0.105 to +0.211). The minimum detectable standardised effect
at 80% power and a two-sided uncorrected 0.05 is **1.26 pooled SD**, which for this gene is 0.288 *z*
≈ 0.66 log2 ≈ **1.6-fold**. Against the *corrected* threshold the paper actually applies — a family
maximum whose median is |*t*| = 5.42 — the detectable effect is several times larger again. A test
that cannot see a 1.5-fold mean difference is not an instrument that closes a deletion hypothesis.

**(b) The alternative is a mixture, not a location shift.** Homozygous 9p21 deletion is a
subset phenomenon; the biological alternative is "some tumours at the floor", not "the mean is
lower". A Welch *t* on six tumours is the wrong statistic for that alternative, and the right one —
a per-sample outlier or floor count — is free and is not run.

**(c) When the right statistic is applied, the two platforms give opposite answers.**
**[recomputed]** On GPL6244 all six EMC tumours sit at *z* between +0.46 and +0.88 and **none** falls
below the lowest comparator (−0.15); that is a genuinely reassuring per-sample negative, stronger than
the mean test the paper reports, and it is not in the paper. On GPL3290 the EMC values are −0.48,
−0.63, −0.65, −0.67, −1.02, −1.21, −1.60, −1.65, −1.85, −2.79 against a comparator range of −1.06 to
−0.10, so **5 of 10 EMC tumours fall below every comparator** — which is the mixture pattern the
hypothesis predicts (see ground 7).

**Fix.** Add the interval and the minimum detectable effect to §3.2; add the per-sample floor count
for both platforms; replace "closed at transcript level" with a statement of what the data can and
cannot exclude at this sample size.

---

### 7. The *MTAP* reading on GPL3290 points toward the rationale the paper closes, and is reported below its own strength — FIXABLE

**Where.** §3.1 (array percentiles); §3.2 table and text; figure 2 and its caption; §4.1; §5.

**What is wrong.** Selective reporting of a pre-specified read-out, in the direction that supports the
paper's conclusion. Four instances, all checkable against the same artifacts:

1. **The array percentile is omitted for the one gene it matters for.** §3.1 reports four array
   percentiles: *MAT2A* at the 99th and 84th, *PRMT5* at the 91st and 59th. The same artifact
   (`gene_reads`, verdict strings) records **MTAP at the 72nd percentile on GPL6244 and the 13th on
   GPL3290**. The pre-specified criterion in the source read block is "MTAP DOWN in EMC, **at the
   floor**". The 13th percentile is what "at the floor" looks like, and it appears nowhere in the
   manuscript or the SI.
2. **The effect size on GPL3290 is not stated on any interpretable scale.** **[recomputed]** *MTAP* is
   **−1.377 log2 = 0.39-fold (95% CI 0.22 to 0.68)** lower in EMC. §3.2's table renders this as
   "−0.607 SD, opposite sign", which reads as an inconsistency rather than as a 2.6-fold reduction.
3. **The table is asymmetric.** §3.2's *MTAP* row gives a *t* for GPL6244 (+0.69) and no *t* for
   GPL3290; the −2.27 appears only two sections later in a table about *PRMT5*.
4. **Figure 2's caption describes the wrong gene.** The caption reads "*MTAP* is flat on the powered
   platform, while *CDKN2A* carries what signal the locus score has and then reverses on the second
   platform." In the right-hand panel of that same figure, the *MTAP* column shows the EMC points
   displaced below the comparator points with five below all of them. The caption is silent about it.

**Why this is not a request to reopen the rationale.** The pre-specified criterion is a conjunction —
*MTAP* down at the floor **together with** *CDKN2A* — and neither platform satisfies it (*CDKN2A* is
down on GPL6244 where *MTAP* is flat, and up at the 71st percentile on GPL3290 where *MTAP* is low).
That is a good reason to call the rationale unsupported. It is a different reason from the one the
paper gives, it is weaker, and it should be the one stated.

**Fix.** Add *MTAP*'s two array percentiles to §3.1; give the GPL3290 fold-change and *t* in §3.2's
table; rewrite figure 2's caption to describe both genes in both panels; state the closure as failure
of the pre-specified conjunction rather than as an adjusted *p* of 1.00.

---

### 8. The reported hypothesis is post hoc with respect to the pre-specification the paper invokes — FIXABLE

**Where.** §2.6 "the reads, thresholds and controls were specified before the corresponding data were
retrieved"; §4.4 "the wrong question for a gene named in advance by a rationale from another disease
… both descriptions apply"; Appendix A.

**What is wrong.** §2.6's sentence is true and is being used to license something it does not cover.
The pre-specified read exists and is committed, and its endpoint is not this paper's claim.

**Evidence**, all from `emc-expression-panels.json` → `reads`:

- The read is `read_9_MTAP_PRMT5`. Its `question` is "Is the *MTAP* locus deleted in EMC …" and its
  `direction_that_supports_the_lane` is "**MTAP DOWN in EMC, at the floor, together with CDKN2A**".
  There is **no directional expectation recorded for *PRMT5* anywhere in the block.** *PRMT5* is in
  the panel as the methylosome that *MTAP* loss would sensitise, i.e. as a consequence of the
  rationale the paper closes.
- The same artifact carries **18 numbered reads plus a control block**, all run on the same fetch of
  the same 16 EMC tumours (`read_1_ASS1` … `read_18_PROTEOSTASIS`). This paper is the write-up of one
  of them, after that one's own pre-specified endpoint failed.
- The paper's Appendix A records that "the restatement of the fusion rationale on the gene rather
  than the group" was "found during figure preparation, after the prose had been written the other
  way", and that the methylosome group *t* (3.11, 3.89) "was the wrong one to lead with". That is
  explicit selection of the reported statistic from within a four-gene group after the figures were
  seen.

**Consequence.** §4.4's even-handed "both descriptions apply" is not even-handed on the record: only
the post-hoc description applies. This resolves ground 2 against the paper — the array-wide family is
the right one — and it is the strongest available defence of the paper's own pessimistic number, so
stating it costs the paper nothing it has not already lost.

**Fix.** In §2.6 and §4.4, state what was pre-specified (the *MTAP* endpoint and its direction), state
that the *PRMT5* claim and the choice of the gene over the group were made after the data were seen,
and state that this is why the array-wide family is the family the correction uses. Add one sentence
naming that this read is one of eighteen run on the same tumours.

---

### 9. Every effect is reported as a *t* on an unnamed scale; the *t* is large because the standard error is small, and the result does not survive variance moderation — FIXABLE

**Where.** Abstract; §3.5; §3.6; §4.1; §5; SI §S3.

**What is wrong.** The paper reports *t* = 6.24 and 6.67 twelve times between the two documents and
never once says how large the difference is in a unit a reader of this journal can interpret, nor
gives a confidence interval for any effect anywhere.

**Evidence [recomputed]**, on each array's own log2 scale:

| gene | platform | difference | fold | *t* | SE percentile within the correction's family |
|---|---|---:|---:|---:|---:|
| *PRMT5* | GPL6244 | +0.544 log2 | 1.46× | 6.24 | **22.8th** |
| *PRMT5* | GPL3290 | +1.094 log2 | 2.13× | 6.67 | **6.4th** |
| *MTAP* | GPL6244 | +0.121 log2 | 1.09× | 0.69 | 60.0th |
| *ENO3* | GPL6244 | +1.568 log2 | 2.96× | 3.61 | 92.5th |

The pattern is the finding: *PRMT5*'s *t* is not large because its difference is large. Its
within-arm SD on GPL6244 is 0.140 log2 across six tumours, which puts its standard error in the
bottom quartile of the ~5,000-gene family it is being corrected against; the control gene *ENO3* has
a three-times-larger difference and a much smaller *t*. At *n* = 6 the field standard is a moderated
variance (limma-style empirical Bayes) precisely because raw per-gene variances are unreliable; the
paper uses none, and §2.6 states that no statistical package supplies its tests.

Sensitivity **[recomputed]**, flooring the standard error at a family quantile as a crude stand-in for
moderation, with the family maximum recomputed the same way:

| SE floor | GPL6244 PRMT5 \|*t*\| → adjusted *p* | GPL3290 |
|---|---|---|
| family 25th percentile | 6.24 → 6.03, *p* = 0.143 | 6.67 → 4.49, *p* = 0.796 |
| family 50th percentile | 6.24 → 4.10, *p* = 0.812 | 6.67 → 3.03, *p* = 0.9999 |

**Fix.** Report every contrast as a difference on the array's log2 scale with a 95% interval beside
the *t*, in §3.2, §3.5, §3.6 and SI §S3; state that no variance moderation was applied and report the
sensitivity above in §S5c.

---

### 10. Multiplicity is corrected for 15 quantities out of roughly 113 the two documents report, and for none of the seventeen other reads run on the same tumours — FIXABLE

**Where.** §2.3; §3.5; SI §S5c.

**What is wrong.** The correction covers exactly the nine genes in `REPORTED` on the platforms where
they score. Every other quantity in the paper is an uncorrected comparison, and several of them carry
claims in the abstract and Conclusion.

**Count**, enumerated so it can be checked: SI §S3 group contrasts, 13 emitted; §3.5 gene table, 13;
*CDKN2B* on GPL6244, 1; *MKI67* on both, 2; PRMT-family members other than *PRMT5*, 13; confound-score
contrasts, 4; proliferation- and lineage-adjusted *PRMT5* contrasts, 4; correlations, 3; §S5a
reference-channel split, 14; §S5b exclusion sensitivity, 6; genome-wide percentile placements, 13;
§3.1 array percentiles, 4; per-class medians in figure 4 and §S5b, 12; DepMap quantities, 9; the two
exact permutation *p*-values, 2. **Total 113; corrected 15** (the §S5c table).

Behind those sit the panel run itself: `emc-expression-panels.json` carries **404 + 362 per-gene Welch
contrasts, 135 curated group scores and 25 signature scores across 18 numbered reads**, all computed
on the same fetch of the same 16 EMC tumours, plus **18,688 + 14,404 genome-wide contrasts**. None of
that appears in the paper's multiplicity accounting except implicitly through the array-wide family.

**Fix.** Add a sentence to §2.3 stating how many comparisons the paper reports and which of them are
corrected; label the uncorrected ones as uncorrected wherever they carry a claim (§3.1, §3.4, §3.6,
§S5a, §S5b); and state in §2.6 that this read is one of eighteen on the same samples.

---

### 11. "Exact" overstates what the permutation delivers, because the arms are strongly heteroscedastic — FIXABLE

**Where.** §2.3 "The two-sided *p* is the fraction with |*t*| at least the observed value. No random
sampling is used, so the value is exactly reproducible"; §3.5; SI §S10; abstract ("exact permutation
*p* of 0.000142 and 0.000125").

**What is wrong.** A permutation test is exact for the sharp null of full exchangeability — that the
two arms are draws from the same distribution — not for the null of equal means. When the arms differ
in variance, permuting a Welch *t* is only asymptotically valid for a location null, and rejection can
be produced by a scale difference. At these sample sizes the asymptotics do not apply.

**Evidence [recomputed]**, between-arm variance ratios across all scored panel genes: **51.5% of genes
on GPL6244 and 58.4% on GPL3290 have var(EMC)/var(comparator) outside [0.5, 2]**. Individual cases
the paper interprets: *MKI67* on GPL3290 has a ratio of **0.07** (SD 0.345 versus 1.285) and its
*t* = 2.30 is produced by two comparator arrays at *z* = −3.72 and −3.88 — the cellularity control the
review response calls "the item that most needed accepting" is a two-point artefact; *MTAP* on
GPL3290 has a ratio of 4.73; *ENO3* on GPL6244 has 4.56.

**Fix.** Replace "exact" with "exact under the null of exchangeability" in §2.3, §3.5, SI §S10 and the
abstract; state the variance-ratio distribution in §2.3; and note in §3.6 and §S5 that *MKI67*'s
GPL3290 reading is driven by two comparator arrays.

---

### 12. The reference-channel disclosure names the confound and the paper then computes fourteen contrasts across it — FIXABLE

**Where.** §2.1; §3.6 "Splitting the comparator arm by reference is the discriminating comparison:
against the three comparators sharing EMC's reference label, *PRMT5* reads *t* = 5.97"; SI §S5a.

**What is wrong.** Round one's contribution was to make the confound visible. The revision named it
accurately — including the correction that `CRH` and `CRH-mRNA` are matched by label only — and then
kept using the confounded arms as though naming them had resolved them. §3.6 calls the DFSP split "the
discriminating comparison", but the DFSP arm does not share EMC's reference: it shares a label that
the deposit does not define. There is no reference-matched contrast on this platform, so nothing in
§S5a discriminates.

Compounding it: §S5a's arms are *n* = 3, and it reports seven genes against each half, i.e. fourteen
contrasts on three-sample arms, presented in a table with signed *t* values. §S5a does say "nothing
here is a test", which is right; the table is nonetheless read in §3.6 as ranking two explanations.

**Fix.** In §3.6, state that no unconfounded contrast exists on GPL3290 and delete "discriminating";
in §S5a, present the split as a descriptive display without *t* values, or keep the *t* values and
state that both halves are reference-different from EMC so agreement between them is uninformative
about the confound. Add the DFSP-versus-GIST reading (*PRMT5* *t* = +0.24) as the only
reference-informative comparison available.

---

### 13. The central class-separation claim is asserted from medians with no test — FIXABLE

**Where.** §3.4 "*PRMT5* alone does, with a median of +1.30 against +1.05, +1.05, +1.04 and +0.94";
figure 4 right panel, titled "PRMT5 alone: EMC highest of the tumours"; §4.1; §5; abstract.

**What is wrong.** Figure 4's left panel correctly declines to test pooled gene-by-sample values. The
right panel has one value per sample and could be tested, and is not. The claim it supports appears in
the abstract and Conclusion.

**Evidence [recomputed]**, exact permutation on the means, EMC against each class separately on
GPL6244:

| comparison | Δ median | exact *p* | ×4 |
|---|---:|---:|---:|
| EMC (6) vs LGFMS (17) | +0.262 | 4/100,947 | 0.0002 |
| EMC vs desmoid fibromatosis (6) | +0.254 | 0.0065 | 0.026 |
| EMC vs solitary fibrous tumour (5) | +0.252 | 0.0087 | 0.035 |
| EMC vs myxofibrosarcoma (6) | +0.367 | 0.0152 | 0.061 |

So the claim is defensible on three of four classes at a within-figure Bonferroni, and the paper does
not say so. It is also weaker than "separates": **9 of the 34 comparator tumour samples exceed the EMC
minimum**, and **one of the two pooled normal-muscle arrays exceeds the EMC median**. And none of
these *p*-values is corrected for the ~18,700 genes on the array, so they do not rescue ground 2.

**Fix.** Report the four tests and their within-figure correction in §3.4 or §S5b; replace "separates
it from the other tumour classes" with the overlap count; and state that these tests carry no
genome-wide correction.

---

### 14. The paper's primary gene is a single probe on each platform, on one of which the symbol bridge resolves 58.2% of accessions, and the per-gene probe count is never stated — STRUCTURAL, survivable with disclosure

**Where.** §2.1 (aggregate mapping rates); §3.5; SI Appendix S1.

**What is wrong.** §2.1 gives platform-level rates and never gives the reader the number that governs
whether the paper's own gene is trustworthy: how many probes carry it.

**Evidence**, `gene_reads[*].n_probes_mapping`: ***PRMT5* maps to exactly one probe on GPL6244 and one
on GPL3290**; *MTAP* to one and two; *CDKN2A* to one and one. On GPL3290 the probe-to-symbol bridge
resolved **0.582** of distinct accessions (37,919 of 65,180), 27,271 of them by live NCBI query, and
the platform's probes are ESTs. So the entire GPL3290 half of the paper's replication is one cDNA spot
whose gene assignment runs through a 58%-complete archival bridge — the same bridge SI Appendix S1
records as having returned zero gene links on two of four runs on 2026-08-09.

There is no cross-probe agreement check available for *PRMT5* on either platform, and none is
possible.

**Why STRUCTURAL.** No revision can add probes to a decade-old array.

**Survivable how.** State the per-gene probe count for every gene in §3.5's table and add one sentence
to §4.4: on both platforms the primary reading rests on a single probe, so a mis-annotated or
cross-hybridising spot is not excluded by anything in this work. (The SI's finding that the values are
stable across three annotation bridges is about the *bridge*, not about the *probe*, and does not
address this.)

---

### 15. Figure, caption and text discrepancies against the artifacts — FIXABLE

**Where.** Figure 2 caption; figure 3; SI §S5c; §2.3.

1. **Figure 2's caption is silent about the pattern in its own panel** — see ground 7(4).
2. **Figure 3 does not plot the comparison its caption makes.** The figure is titled "PRMT5 and MAT2A
   are pan-essential across sarcoma lines" and draws three sarcoma fractions; the manuscript's caption
   then makes the load-bearing point with a number that is not drawn ("PRMT5 is a dependency in 94.1%
   of the non-sarcoma lines as well"). No bar carries an interval: 94.5% of 91 lines has a Wilson 95%
   interval of roughly 88% to 98%, and the sarcoma-versus-rest difference the caption relies on is 0.4
   percentage points. The *x*-axis also runs to 120% for a quantity bounded at 100.
3. **SI §S5c misstates its own family sizes.** It reads "on GPL3290 it is 0.037, 0.062 and 0.208 over
   the same three family sizes". The artifact's keys are 250 / 1,000 / **3,640** on GPL3290 against
   250 / 1,000 / **3,973** on GPL6244, so the third size is not the same.
4. **§2.3 describes a family it did not use.** "The family is every symbol two committed input caches
   hold … That family is 5,449 symbols on GPL6244 and 4,848 on GPL3290." The caches hold 5,449 and
   **5,216**; 368 GPL3290 symbols fail the arm floor and are dropped. This is the same error class the
   paper's own Appendix A registers for the phrase "every symbol the platform's probes map to".
5. **Two sample-identity questions are not addressed.** GPL3290 sample 16 is titled
   "STT2528(2)-Myxoid Chondrosarcoma" and the parenthetical is unexplained; the deposit's other 20
   samples are never checked for tumour overlap with the 16 analysed. If any two of the ten EMC arrays
   are the same tumour, C(16,10) = 8,008 is not the right labelling count.

**Fix.** Rewrite figure 2's caption; add the non-sarcoma bars and Wilson intervals to figure 3 and cap
its axis at 100; correct §S5c's family sizes; correct §2.3's family description and register the old
wording; add one sentence to §2.1 on the unexplained sample title and on what is known about the
deposit's other platform.

---

## Round-one response claims checked and found overstated

**(a) "They remain lower bounds: … adding symbols can only raise the permuted maximum."**
*Direction correct, implication overstated.* The monotonicity claim is right and I verified it. But
the response and §4.4 use it to argue that 0.21/0.24 is if anything optimistic, while the same
procedure on the same labellings gives **0.031** on GPL3290 once genes with missing data leave the
family (ground 4) and **0.000125** over the genes the paper reports (ground 2). Family *composition*
is a larger and opposite-signed degree of freedom than family *size*, and only the size axis is
reported.

**(b) "the two series are independent, so *PRMT5* ranking first of the readable PRMT family on both
platforms is a replication statement" (round one M2, adopted in §4.1 and §5 as "two independently
collected series").**
*Not established anywhere in the record.* The pre-posting checklist states that "GSE24369's source
publication is not identified" and that GEO's own esummary carries a null PubMed field, which the
committed `emc-cohort-search-inputs.json` confirms. Nothing in the repository shows that the six EMC
tumours in one series and the ten in the other are different patients or different centres. The
paper's one surviving positive statement rests on an independence it asserts and does not show.
Worse, the same artifact records that **GSE24369's deposited title is "Gene expression profiling of
low-grade fibromyxoid sarcoma (LGFMS)"** and its summary describes 17 LGFMS "compared to that of
histologically similar tumors" — so the 35-tumour platform the paper calls "the powered platform" is
an LGFMS study in which EMC is one comparison group and 17 of the 29 comparators are the depositors'
index class. §2.1 quotes GSE4303's deposited summary and does not quote this one.
*Classification: STRUCTURAL. Survivable only by dropping the replication claim, which is the paper's
last positive statement.*

**(c) Round one's own statistical error, now quoted as authority.** Round one wrote: "The *closure* of
the MTAP rationale is unaffected — *MTAP* is at an adjusted *p* of 1.00 on both platforms, which is
exactly the paper's point and is the one place where correction helps the argument rather than
hurting it." The revision adopted it verbatim into §3.2. It is wrong for the reason in ground 5, and
the manuscript's own SI §S5c contradicts it.

**(d) "On GPL3290 all 8,008 labellings are enumerated, so that correction is exact and carries no
sampling error."** *True of the labellings only.* It is exact conditional on the family (ground 2), on
the arm-floor zeroing convention (ground 4), and on exchangeability (ground 11) — none of which is
stated beside the word "exact".

**(e) "the pre-specified cellularity control … stated to corroborate the paper's weakest reading."**
*Accepted correctly, reported without its basis.* *MKI67*'s GPL3290 *t* = 2.30 comes from a comparator
arm with an 18-fold larger variance than the EMC arm and two arrays at *z* = −3.72 and −3.88
**[recomputed]**. The control fires, but not for the reason the text implies.

**(f) Two round-one numbers that the response corrected — and the response is right.** Solitary
fibrous tumour's *PRMT5* median is +1.0525, not +1.14, and it does not rank first on the pooled
four-gene score (desmoid +0.95, SFT +0.94, EMC +0.93). Both reproduce exactly **[recomputed]**. The
revision's arithmetic is better than the review's on every point where they disagree.

---

## Fix list

Ordered. Only the FIXABLE grounds appear; grounds 3, 8(b) and 14 are structural and are handled by
scoping and disclosure rather than by a change that removes them.

1. `emc-mtap-prmt5-hypothesis.md` — title, abstract, §4.1, §5: remove "survives" as a description of
   the fusion rationale's transcript evidence; state that the transcript evidence is null after
   correction and that the hypothesis rests on the external literature and the sequence analysis.
   *(Ground 1)*
2. `emc-mtap-prmt5-hypothesis-SI.md` §S5c and main §3.5 — report PRMT5's adjusted *p* over all three
   families (reported genes 0.00015 / 0.000125; curated panel 0.0971 / 0.0642; merged 0.2081 /
   0.2376), name which family the inference is over, and give the reason. *(Ground 2)*
3. `emc-mtap-prmt5-hypothesis.md` §2.6 and §4.4 — state that the pre-specified endpoint was *MTAP*
   loss with a recorded direction, that no direction was pre-specified for *PRMT5*, that the statistic
   was moved from the group to the gene after the figures, and that this read is one of eighteen run
   on the same tumours; conclude that the array-wide family is therefore the correct one. *(Ground 8)*
4. `emc-mtap-prmt5-hypothesis-SI.md` §S5c and main §2.3 — add the complete-case family result on
   GPL3290 (3,126 genes, adjusted *p* = 0.0312) beside the as-built one, and state the arm-floor
   zeroing convention in `_t_matrix`. *(Ground 4)*
5. `emc-mtap-prmt5-hypothesis.md` §3.2, §4.1, §5 and abstract — delete the claim that an adjusted *p*
   of 1.00 states a closure; replace with the pre-specified conjunction that failed. *(Ground 5)*
6. `emc-mtap-prmt5-hypothesis.md` §3.2 — add *MTAP*'s 95% interval and fold-change on both platforms
   (+1.09-fold, CI 0.87–1.36 on GPL6244; 0.39-fold, CI 0.22–0.68 on GPL3290), the minimum detectable
   effect (1.26 pooled SD ≈ 1.6-fold at 80% power), and the per-sample floor counts (0 of 6; 5 of 10).
   *(Ground 6)*
7. `emc-mtap-prmt5-hypothesis.md` §3.1 and §3.2 — add *MTAP*'s array percentiles (72nd on GPL6244,
   13th on GPL3290) and its GPL3290 *t*; make the table symmetric across platforms. *(Ground 7)*
8. `research/modalities/emc_mtap_prmt5_figures.py` and figure 2's caption — rewrite the caption to
   describe both genes in both panels, including *MTAP*'s GPL3290 separation. *(Grounds 7, 15)*
9. `emc-mtap-prmt5-hypothesis.md` §3.2, §3.5, §3.6 and SI §S3 — report every contrast as a log2
   difference with a 95% interval beside the *t*; state that no variance moderation was applied and
   add the SE-floor sensitivity to §S5c. *(Ground 9)*
10. `emc-mtap-prmt5-hypothesis.md` §2.3 and §2.6 — state how many comparisons the two documents report
    (113) and how many are corrected (15); label every uncorrected claim as uncorrected. *(Ground 10)*
11. `emc-mtap-prmt5-hypothesis.md` §2.3, §3.5, abstract and SI §S10 — qualify "exact" as exact under
    exchangeability; report the between-arm variance-ratio distribution; note *MKI67*'s two-array
    basis on GPL3290. *(Ground 11)*
12. `emc-mtap-prmt5-hypothesis.md` §3.6 and SI §S5a — delete "discriminating comparison"; state that
    no reference-matched contrast exists on GPL3290; add the DFSP-versus-GIST reading (*PRMT5*
    *t* = +0.24) as the only reference-informative comparison. *(Ground 12)*
13. `emc-mtap-prmt5-hypothesis.md` §3.4 and SI §S5b — add the four per-class exact tests and their
    within-figure correction; replace "separates" with the overlap counts (9 of 34 comparator tumours
    above the EMC minimum; 1 of 2 normal-muscle arrays above the EMC median). *(Ground 13)*
14. `emc-mtap-prmt5-hypothesis.md` §3.5 table and §4.4 — state the per-gene probe count for every gene
    reported, and that both primary readings rest on a single probe. *(Ground 14, disclosure)*
15. `emc-mtap-prmt5-hypothesis.md` §2.1, §3.6, §4.4 and SI §S1 — state that on GPL3290 class,
    submission block, reference pool and within-study platform assignment are collinear (all 10 EMC
    and 6 of the deposit's 26 comparator sarcomas on this array), that per-array probe counts range
    23,015 to 41,510 so the *z* background is not a constant reference, and demote GPL3290 from
    replication to consistency check. *(Ground 3, scoping)*
16. `emc-mtap-prmt5-hypothesis.md` §2.1 and §4.4 — quote GSE24369's deposited title and summary as
    §2.1 already quotes GSE4303's, state that its source publication is unidentified, and state that
    nothing establishes that the two series' EMC tumours are from different patients or centres; drop
    "independently collected" wherever it carries weight. *(Ground 8b, scoping)*
17. `emc-mtap-prmt5-hypothesis.md` §2.3 and SI §S5c — correct the family description (caches hold
    5,449 and 5,216; family is 5,449 and 4,848) and §S5c's "the same three family sizes" (3,973 versus
    3,640), and register both in the corrections appendices. *(Ground 15)*
18. `research/modalities/emc_mtap_prmt5_figures.py` — figure 3: add the non-sarcoma fractions as
    drawn bars, add Wilson intervals, cap the *x*-axis at 100. *(Ground 15)*
19. `emc-mtap-prmt5-hypothesis.md` §2.1 — state what is known about the "(2)" in the GPL3290 sample
    title and about tumour overlap with the deposit's other platform, or state that neither can be
    determined from the deposit. *(Ground 15)*
