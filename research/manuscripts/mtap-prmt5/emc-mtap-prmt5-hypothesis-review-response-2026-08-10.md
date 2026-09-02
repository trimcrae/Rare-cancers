---
id: DOC-EMC-MTAP-PRMT5-REVIEW-RESPONSE
title: "Response to review — emc-mtap-prmt5-hypothesis.md"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: Record what changed in the PRMT5 manuscript in response to the 2026-08-10 simulated review, and why each declined item was declined.
scope: One manuscript's revision. Reports no new experiment; every number it cites lives in a committed artifact named beside it.
audience: [maintainers, external reviewers]
date: 2026-08-10
last_verified: 2026-08-10
---

# Response to review — "The PRMT5 methylosome in extraskeletal myxoid chondrosarcoma"

> **THIS RESPONDS TO A SIMULATED INTERNAL REVIEW, WRITTEN BY AN AI REVIEWER AT THE AUTHOR'S REQUEST.
> IT IS NOT CORRESPONDENCE WITH *GENES, CHROMOSOMES AND CANCER*, NOT a reply to a real referee, and
> NOT part of any submission. No editor, no journal and no external referee has seen this manuscript.
> The review is `emc-mtap-prmt5-hypothesis-peer-review-2026-08-10.md`; this file records what the
> revision did with it.**

Files changed: `emc-mtap-prmt5-hypothesis.md`, `emc-mtap-prmt5-hypothesis-SI.md`,
`emc-mtap-prmt5-hypothesis-cover-letter.md`, `emc-mtap-prmt5-prepost.md`, figures 4 and 5 and their
provenance stamp, `research/modalities/emc_mtap_prmt5_figures.py`, and
`research/manuscripts/pinned-figures.json`. New: `research/modalities/emc_prmt5_multiplicity.py` and
`research/modalities/emc-prmt5-multiplicity.json` (the multiplicity correction and three disclosure
analyses), and `research/literature/prmt5-ccs-preprint-publication-status-2026-08-10.json` (the
literature check on reference 2).

Where the reviewer computed a value on a subset, it was recomputed here on everything available and
the reviewer's figure is not quoted. Two of those recomputations disagree with the review and are
flagged below (M5).

---

## Major points

**M1 — a Methods number that traces to no artifact. Accepted in full, and the sentence it falsified
was rewritten as well.**

§2.3 now reads 18,688 symbols scored on GPL6244 and 14,404 of the 14,932 carrying a probe on
GPL3290, which is what `emc-prmt5-route-controls.json` and `emc-expression-panels.json` both record.
SI §S10 and the "Multiple testing" row of the pre-posting checklist carry the same values. The
superseded pair 18,474 / 14,402 is registered in main text Appendix A and in SI Appendix S1, both
noting that it appears in no committed artifact at any point in this repository's history. The
reviewer's second observation is also taken: the parenthesis now states how many symbols were scored
out of how many carried a probe, on each platform, so it no longer describes a computation that was
not performed.

The reviewer is right that this falsified §2.6's verification sentence. That sentence has been
rewritten to say what was checked ("every statistic, percentile, count and dependency figure
reported here was checked against the committed artifact that owns it") and to record that where a
value could not be reconciled it was corrected and registered, "which includes one Methods count
that traced to no artifact at all". A blanket claim that everything was verified is exactly the
claim this incident refutes, so the paper no longer makes it.

**M2 — multiplicity is result-changing. Accepted, and the correction was run on more than the
reviewer could reach.**

A max-statistic permutation correction is now implemented in
`research/modalities/emc_prmt5_multiplicity.py` and committed to `emc-prmt5-multiplicity.json`. Arm
labels are permuted exactly as §2.3's exact test permutes them; Welch's *t* is recomputed for every
gene in the family at every labelling; the family-wide maximum |*t*| is recorded per labelling; a
gene's adjusted *p* is the fraction of labellings whose maximum reaches its observed |*t*|.

Two improvements on the reviewer's own run. On **GPL3290 all 8,008 labellings are enumerated**, so
that correction is exact and carries no sampling error, which matches the paper's existing refusal
to use random sampling where enumeration is possible; on GPL6244, 20,000 labellings are drawn under
a fixed seed against B = 500. And the **family is roughly three times larger**. The reviewer used
the 1,857 and 1,662 genes in the panel cache. `emc-hypoxia-null-background.json`, a second committed
fetch of the same two matrices, additionally holds a **seeded uniform random sample of about 4,000
symbols drawn from each platform's whole mapped-symbol universe**. The two caches were checked to
agree value for value on every symbol they share, on identical samples and identical per-sample
backgrounds, before being merged; the merge is refused if they do not. The family is therefore 5,449
symbols on GPL6244 and 4,848 on GPL3290, against universes of 18,724 and 14,932.

| gene | platform | reported \|*t*\| | FWER-adjusted *p*, this work | reviewer's figure |
|---|---|---:|---:|---:|
| *PRMT5* | GPL6244 | 6.24 | 0.21 | 0.13 |
| *PRMT5* | GPL3290 | 6.67 | 0.24 (exact) | 0.07 |
| *CDKN2A* | GPL6244 | 5.40 | 0.51 | 0.32 |
| *MAT2A* | GPL6244 | 4.13 | 0.98 | 0.84 |
| *MAT2A* | GPL3290 | 4.10 | 0.97 (exact) | 0.76 |
| *NR4A3* (control) | GPL6244 | 4.66 | 0.85 | 0.61 |
| *ENO3* (control) | GPL6244 | 3.61 | 1.00 | 0.97 |
| *ENO3* (control) | GPL3290 | 13.22 | 0.010 (exact) | 0.006 |
| *MTAP* | GPL6244 / GPL3290 | 0.69 / 2.27 | 1.00 / 1.00 | 1.00 / 1.00 |

Every value is higher than the reviewer's, in the direction the review predicted, because the family
is larger. They remain lower bounds: the manuscript's own scan covers three to four times more
symbols still, and adding symbols can only raise the permuted maximum. How fast it rises is now
measured rather than asserted, on the random symbols alone, and reported in SI §S5c: *PRMT5*'s
adjusted *p* on GPL6244 goes 0.016 at 250 random symbols, 0.055 at 1,000, 0.168 at 3,973; on GPL3290
0.037, 0.062, 0.208. The curve is still rising at the largest family the committed data supports.
The whole-array value cannot be computed from anything committed, because the full probe matrix
exists only inside the fetch step; the artifact also carries a Markov upper estimate off the random
sample, which is reported there with the note that it is too noisy to use at extreme thresholds and
is not quoted in the manuscript.

What changed in the paper as a result:

- **The abstract** now carries the adjusted values beside the exact ones and says the contrast does
  not survive correction. It is 248 words against a believed 250-word limit; the room was found by
  compressing the data-source sentence, as m9 suggested.
- **§3.5's placement table** carries an adjusted *p* column, and its closing paragraph states that a
  |*t*| of *PRMT5*'s size is not uncommon among the per-permutation maxima, with the null's own
  median (5.4) beside it.
- **§3.2** no longer asserts that "the locus signal on the powered platform is *CDKN2A*"; it says
  what signal the score has is carried by *CDKN2A*, which does not survive correction either
  (0.51), and it adds that *MTAP* is at 1.00 on both platforms, which is where correction
  strengthens the paper.
- **§4.4** names which readings survive and which do not, and gives the three qualifications the
  review asked to be made explicit rather than left to the reader: the values are lower bounds; a
  family-wise correction asks the right question for a gene chosen after a scan and the wrong one
  for a gene named in advance, and both descriptions apply here; and no single-platform correction
  sees the replication across two independent series.
- **§4.1, §5 and the cover letter** are re-weighted accordingly. The exact permutation *p* is kept
  everywhere it appeared, labelled as exact for the labelling of one gene.

**M3 — the reference-channel confound on GPL3290. Accepted, and the sensitivity analysis is
reported.**

§2.1 now carries the reference-channel composition in the series table and a paragraph naming it:
all ten EMC tumours against `CRH-mRNA`, three DFSP comparators against `CRH`, three GIST comparators
against `UHR`. One correction to the review: the deposit does **not** state whether `CRH` and
`CRH-mRNA` name one pool or two, so the DFSP comparators are described as matched **by label** rather
than as reference-matched, and the artifact records that distinction.

§3.6 now ranks the reference difference beside the biological explanation for the platform
disagreement, and says the mundane one is the simpler. The split is in SI §S5a. Recomputed here, and
in agreement with the review: *PRMT5* gives *t* = 5.97 against the three DFSP comparators and 4.32
against the three GIST comparators, against 6.67 pooled; *MAT2A* falls from 4.10 to 2.18 against the
label-matched half. One reading the review did not compute is the sharpest of them: *MKI67*, the
pre-specified cellularity control of M7(b), falls from 2.30 pooled to **1.09** against the
label-matched half, which is the direction expected if part of the GPL3290 proliferation signal were
a reference-pool artefact.

**M4 — the *NR4A3* control on GPL3290. Accepted, with the row kept and annotated rather than
deleted.**

The row now reads "+1.70, top 38.5%; *n* = 9 versus 2" and the paragraph beneath it gives both
candidate explanations and identifies which is measured. Deleting the row would have hidden a
reading a checker can find in the artifact; annotating it says what it is. The text now states that
only two of six comparator samples and nine of ten EMC samples carry a value, that this is below the
panel's three-per-arm floor so the panel emits no contrast at all, and that the +1.70 comes from the
genome-wide path with its floor of two. The probe-placement caveat is retained as the pre-specified
explanation and labelled as such, since it is genuinely in the artifact's control block; the sample
count is labelled as the measured one, and a comparator arm of two is stated to be sufficient on its
own.

Per-gene missingness is disclosed in §2.1 and SI §S10, recomputed here and matching the review: on
GPL3290 578 of 1,662 cached genes (34.8%) have at least one missing value and 51 (3.1%) have an arm
below three; on GPL6244 there are none. The differing floors of the two paths are stated in §2.3.

**M5 — seven dropped samples. Accepted; disclosed, redrawn and reported. Two of the review's numbers
do not reproduce, and the corrected ones are used.**

§2.1 states that GSE24369 deposits 42 samples and 35 were analysed, separates the defensible
exclusion (two pooled skeletal-muscle RNA samples, normal tissue) from the accidental one (five
solitary fibrous tumours, for which the classifier carried no pattern), and says which is which.
Figure 4 is redrawn with every deposited class, including both excluded ones; the caption marks the
normal-tissue column as not a comparator. SI §S5b reports the exclusion sensitivity, which reproduces
the review exactly: *PRMT5* 6.24 → 6.31, *MTAP* 0.69 → 0.70, *CDKN2A* −5.40 → −5.66.

The two disagreements, both computed by the figure's own method (medians of gene-by-sample *z*
pooled across the four methylosome genes, and of *PRMT5* alone), and both reproducing the
manuscript's existing published medians to the decimal:

1. The review puts the excluded class at a *PRMT5* median of **+1.14**. It is **+1.05** (1.0525).
   The class does rank second, but it sits 0.002 above desmoid fibromatosis rather than clearly
   above it, and EMC at +1.30 remains highest of the tumour classes. §3.4 and the figure caption say
   "+1.30 against +1.05, +1.05, +1.04 and +0.94".
2. The review says the excluded class ranks **first** on the pooled four-gene score, above desmoid
   fibromatosis and EMC. It does not: desmoid fibromatosis +0.95, solitary fibrous tumour +0.94, EMC
   +0.93. The ranking claim in §3.4 therefore becomes "third of the five tumour classes, below
   desmoid fibromatosis and solitary fibrous tumour", not a change of leader.

A third fact the review did not reach is now in the paper because it qualifies the reading rather
than supporting it: the **two pooled skeletal-muscle samples read +1.34 on *PRMT5*, above EMC**.
They are normal tissue and are not a comparator, and that is stated; but a within-array *z* that puts
normal muscle above the tumour is the plainest available statement of what this measurement does not
show, so it is drawn in the figure and stated in §3.4 and SI §S5b.

**Not accepted: restoring the five samples to the primary comparator arm.** The reason is
instrumental rather than editorial. Every genome-wide percentile in §3.2 and §3.5, and the
genome-wide null that the multiplicity correction's family is checked against, are computed at fetch
time on the arms as defined; widening the arm without a re-fetch would leave the paper's percentiles
and its contrasts computed on two different comparator arms, which is worse than either. The
sensitivity analysis shows the primary contrasts are insensitive to the choice, so nothing is gained
by taking that risk from a sandbox that cannot reach GEO. A re-fetch with the classifier widened is
recorded in the pre-posting checklist as the way to change it properly.

**M6 — one of three clear cell breakpoints shown. Accepted in full.**

§3.7's table now carries all three reported EWSR1::ATF1 junctions with their retained-site counts
(EWSR1 exon 8, 324 residues, 4 sites; exon 10, 348 residues, 4 sites; exon 7, 264 residues, none),
and figure 5 plots all three; the filter in `emc_mtap_prmt5_figures.py` that dropped rows labelled
"reported type" is removed, with the reason recorded in the code. The concluding sentence now reads
that two of three reported clear cell junctions retain four sites and the third retains none, and
that the match is a property of the commonest junction of each disease rather than of the fusion
class. Falsifier F9 is updated to record that it is partially answered. The reviewer's further
observation is taken up in §3.7 and §4.2: clear cell sarcoma already offers within its own
breakpoints the contrast the two-construct experiment proposes to build in EMC.

**M7 — three readings in the artifacts that were not reported.**

*(a) PRMT5's pan-DepMap selectivity. Accepted.* §3.3 now states that PRMT5 is a dependency in 94.1%
of non-sarcoma lines, giving a sarcoma selectivity of 0.013 against MAT2A's −0.285, and that on this
panel PRMT5 is not distinguishable from a pan-essential gene inside sarcoma or outside it. SI §S4's
table gains two columns carrying both figures for all three genes. §4.1 carries it as a third stated
limit and §5 as one of three.

*(b) The unreported MKI67 control. Accepted, and it is the item that most needed accepting.* It is
now a fourth pre-specified control in §3.6 with both platform values (*t* = 0.53 on GPL6244, *t* =
2.30 and +1.24 SD on GPL3290) and its pre-specified expectation of flatness, stated to corroborate
the paper's weakest reading rather than its strongest. It appears in SI §S5's control table, in the
reference-channel split of §S5a, in the adjusted-*p* table of §S5c, in falsifier F7, and in §1.1,
which no longer asserts an uncited slow-cycling natural history but points at this control as the
place the expectation is tested.

*(c) SI §S5 describing a control block that does not exist. Accepted.* The sentence claiming
housekeeping recovery and a comparator-high marker is deleted, and replaced by the six genes the
block actually contains (NR4A3, ENO3, MKI67, EWSR1, TAF15, FUS) with their recorded expectations.
The deletion is registered in SI Appendix S1, because a reader had been told a control existed that
did not.

**M8 — eleven references are not enough. Accepted in part; four items declined with reasons, and
the reviewer's separate point about the preprint is accepted and closed.**

Added, each from a committed retrieval record with full bibliographic metadata: GSE4303's source
publication [12]; the four sourced records behind the *NR4A3*-fusion breakpoints [13–16]; *ENO3* as
a published direct target [17]; and the two published EMC models with the drug sensitivities their
holders validated in them [18]. The natural-history claim is not cited but removed and replaced by a
measurement (M7b). The modality census is given a locator in §8 rather than a number in prose
without one, which is the reviewer's own alternative for item 29.

Declined, with reasons:

1. **GSE24369's source publication.** GEO's own esummary record for the series, retrieved and
   committed in `emc-cohort-search-inputs.json`, carries a null PubMed field, and no retrieval
   record in this repository names a publication for it. Citing one would be writing a citation from
   recollection, which is the failure `lint_citations.py` exists to catch. §2.1 now states that
   neither series carries a linked publication in GEO and identifies the deposits by accession; for
   GSE4303 it gives the basis for the attribution (the deposited summary describes ten EMC and 26
   other sarcomas on 42,000-spot cDNA arrays, which is [12]). A Europe PMC search from CI would
   settle GSE24369 and is listed in the pre-posting checklist.
2. **The Chronos method citation.** No committed record carries its bibliographic metadata. The
   release itself is now identified by its figshare article ID (27993248) in §2.2 and §8, which is
   what makes the data retrievable and is the substance of m13.
3. **A methylosome review for MEP50/WDR77.** No committed record carries one. Rather than invent a
   citation, §1.2 keeps [6], which is a primary structural paper supporting precisely the claim made
   (that MEP50 is required for PRMT5-catalysed activity and binds substrate independently).
4. **The EWSR1 activation-domain claim.** Rather than cite a source this repository does not hold,
   the claim is removed. §1.2 now says only that both fusions retain the same N-terminal EWSR1
   segment, which is what §3.7 measures in this work.
5. **The clear cell and Ewing breakpoints.** These are recorded in `emc-fet-construct-designs.json`
   as exon numbers and cumulative coding positions with no published quotation, unlike the four
   *NR4A3* junctions. §2.5 now says so explicitly rather than implying a source exists.

*The preprint's status.* Accepted and closed. A literature search on 2026-08-10 found that the
preprint was published in a peer-reviewed journal; reference 2 is now that version, with the preprint
identifier and posting date retained beside it. The record, including the fact that neither the
publisher page nor the PMC record was reachable from this environment and that the bibliographic
details therefore come from a search index and must be confirmed before submission, is in
`research/literature/prmt5-ccs-preprint-publication-status-2026-08-10.json`. §4.4 now states what was
found and that the statements attributed to the source were read from the preprint's full text.
"Not certified by peer review" is removed from §1.2 and §4.4 because it is no longer true.

**M9 — the Methods would not let an independent group reproduce this. Accepted in full.**

§2 grew by about 800 words, covering each of the eight items: sample classification and the
exclusions (§2.1); the composition of both comparator arms (§2.1 table); the *z*-score background,
stated as per sample over every probe on the array carrying a value, mapped or not (§2.1);
multi-probe collapse, stated as averaging on the array's own scale before standardisation (§2.1); the
probe-to-symbol bridge, its three sources in order and its measured resolution rates of 0.981 and
0.582 on accessions and 0.711 and 0.633 on probes (§2.1); missing-value handling and both minimum
arm sizes (§2.1, §2.3); the two-colour reference channel (§2.1); and the software, with the point
that no statistical package supplies the tests, which is what makes exact enumeration possible
(§2.6). The multiplicity correction's method is a new part of §2.3.

---

## Minor points

**m1.** Accepted. Appendix A's first row cites [3], the peer-reviewed Ewing result, not [2].

**m2.** Accepted. §3.1 keeps the GPL6244 percentiles and states of the GPL3290 pair that they are
percentiles of a distribution of log-ratios against a reference pool and carry no absolute meaning.

**m3.** Accepted. §3.6 reads "Eight family members are readable on GPL6244 and seven on GPL3290,
counting *PRMT5* itself", which removes the apparent contradiction with SI §S3's 7/8 and 6/8.

**m4.** Accepted. §2.5 states that reference [8] was verified at metadata and abstract level and that
its full text is not open access and was not read; SI §S9 repeats it where the motif is defined,
noting that reference [9] was read in full.

**m5.** Accepted. "[sic]" is inside the quotation.

**m6.** Accepted. The abstract, the conclusion and the cover letter now all say that no clinically
validated agent directly targets NR4A3. Registered in Appendix A.

**m7.** Accepted, and the count changed twice over: figure 4's caption no longer calls EMC a
comparator, and it now names five tumour classes plus a normal-tissue column.

**m8.** Accepted. Figure 5's caption states that TAF15::NR4A3 is tabulated but not plotted, because
TAF15 is a different 5′ protein and therefore a different ruler.

**m9.** Accepted; the trade was planned before the additions were made. The abstract is 248 words,
measured by `submission_metrics.py`, and carries both the adjusted and the exact *p*.

**m10.** Accepted. The title drops its third clause and is now 19 words: "The PRMT5 methylosome in
extraskeletal myxoid chondrosarcoma: a fusion-class rationale that survives and an MTAP-locus
rationale that does not". The SI, the cover letter and the generated systems views follow it, and
the old title is registered in Appendix A.

**m11.** Accepted. §2.4 gives 5.23/6.24 = 0.84 and 2.71/6.67 = 0.41 against the author-chosen 60%
threshold, and says the failure on the second platform is not marginal. SI §S5 repeats them.

**m12.** Accepted. §4.2's outcome table is deleted; its two positive branches are one sentence of
prose, and its distinct negative branches are folded into F2, F6 and F10, which already asked the
same questions. No row was lost.

**m13.** Accepted. §8 names the figshare article the DepMap release is distributed as, and the two
files read from it.

**m14.** Accepted. The manuscript's ORCID placeholder is deleted; the cover letter's statement that
no ORCID accompanies the submission stands as the single statement. Recorded in the pre-posting
checklist so that supplying one later updates both.

**m15.** Accepted. The editorial HTML comment block is deleted from the manuscript. Its content —
venue reasoning, the verified $0 fee route, the article-type decision, the identifier-form note and
the open-at-submission items — is moved into the pre-posting checklist, which is where it belongs
and where it is not one conversion pass away from being published.

**m16.** Accepted. §3.4's "The two figures illustrate the same methodological point in opposite
directions" and §4.1's "the gene-level cut makes it more precise rather than less" are gone; §4.4's
"an argument is not a result" is kept. The style gate reports no glyph, mid-sentence bold or
em-dash findings in the running text of either file.

**m17.** Accepted. §3.3 splits the clause: MTAP reading as a non-dependency is stated as the expected
profile for a biomarker, and separately as consistent with the panel being read correctly and weaker
than a positive control, "since a gene can be a non-dependency for reasons that have nothing to do
with the instrument".

---

## Two things the revision changed that the review did not ask for

**The comparator class named `fibrosarcoma` is myxofibrosarcoma.** Reading the verbatim GEO
annotations for M5 showed that the six samples the classifier buckets as `fibrosarcoma` are
annotated `Myxofibrosarcoma`; the bucket matches on a substring, and myxofibrosarcoma is a different
entity. The manuscript, figure 4 and SI §S1 now name the samples rather than the bucket, and SI §S1
says why the two differ. The bucket name is left alone in the artifact, which is a record of what the
classifier did.

**One pinned-figure pattern was fixed, not loosened.** `pinned-figures.json` carried a superseded
compute figure with the pattern `2\.10\s*[x×]|2\.102`, whose second alternative had no boundary and
matched inside any longer numeric string. It fired on the DOI `10.1016/j.jbc.2022.102434` in the new
reference 2. Lookarounds now require the figure to stand alone; a real quotation of the retired 2.102
still fails the gate, which was checked both ways. The change and its reason are recorded in the
registry entry itself.

---

## Gate status after the revision

| gate | result |
|---|---|
| `lint_consistency.py` | 0 ERROR |
| `lint_style.py` | 0 ERROR |
| `lint_claims.py` | 0 ERROR |
| `systems_check.py --check` | 0 ERROR; views regenerated for the new title |
| `emc_systems_map_check.py --check` | 0 ERROR |
| `lint_citations.py` | 0 ERROR, 0 new unanchored identifiers. Every identifier added by this revision anchors to a tracked retrieval record |
| `emc_mtap_prmt5_figures.py --check` | OK, 10 files against 5 committed artifacts |
| `emc_prmt5_multiplicity.py --check` | REPRODUCES |
| `submission_metrics.py` | abstract 248 words against a believed 250; main text 7,219 words against no stated limit; 5 display items; flagged over nothing |

One operational note for a future revision of this paper: `lint_citations.py` reads `git ls-files`,
so an identifier whose only home is a new and still-untracked artifact reads as unanchored until that
artifact is tracked. The two new artifacts here carry reference 2's published identifiers and must
land in the same commit as the reference list, which is the same rule CLAUDE.md 1.3 states for a
pinned figure.
---

## Where this response's section pointers now resolve (relocation pass, 2026-08-10)

The manuscript was cut from 11,537 to about 6,500 words of main text by **relocating** material into
the supplementary file, not by deleting it. Nothing this response records as applied has been
withdrawn, and no disclosure, caveat, confound statement, sensitivity analysis or limitation was
dropped; each either stayed in the main text or moved to a numbered supplementary section that the
main text points at by name. Where a pointer in this document names a main-text section, the finding
is still stated there and the working is now in the supplement:

| what moved | from | to, in full |
|---|---|---|
| the two source reports' designs, mechanisms and inhibitor results by class | §1.2, §4.2 | S11 |
| the corpus and screen composition, and the pan-sarcoma panel arithmetic | §1.3 | S12 |
| the *z*-score background, multi-probe collapse, the probe-to-symbol bridge and its measured rates, the coverage floors, both minimum arm sizes and the realised missingness | §2.1 | S2 |
| the deposit summaries, accession blocks, reference-label caveat and per-array covariates | §2.1 | S1 |
| the family construction, the arm-floor convention and the variance-ratio distribution | §2.4 | S5c, S10 |
| the software stack and what the value-by-value checking does and does not establish | §2.7 | S13 |
| the per-sample controls, the neighbouring 9p21 genes and the ladder of *CDKN2A* cuts | §3.2 | S3a |
| the reference-channel split, including the DFSP-against-GIST contrast | §3.6 | S5a |
| the exclusion sensitivity (*PRMT5* 6.24 to 6.31, *MTAP* 0.69 to 0.70, *CDKN2A* −5.40 to −5.66), the three qualifications on the corrected figures, the count of comparisons and the transfer argument | §4.4, §4.1 | S14 |

Figure and table legends moved to a display-item legends section after the references, which is the
journal's submission format and is why the counted main text falls without any legend being changed.
