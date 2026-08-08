---
id: DOC-NR4A3-FUSION-TRANSCRIPTIONAL-OUTPUT-SUBMISSION-CHECKLIST
title: "Submission checklist and journal-fit rationale — EWSR1::NR4A3 transcriptional-output manuscript"
level: L3
kind: memo
status: live
canonical_for: []
purpose: >
  Record the journal recommendation and its reasoning, confirm the manuscript meets the target
  journals' author standards, and list the residual author-only steps that must be completed before
  the manuscript is actually submitted — so that "submission-ready" is auditable rather than asserted.
scope: >
  Submission logistics and standards compliance for the transcriptional-output manuscript. Contains no
  scientific result.
audience: [maintainers, external reviewers, collaborators]
related: [DOC-NR4A3-FUSION-TRANSCRIPTIONAL-OUTPUT]
date: 2026-08-07
last_verified: 2026-08-07
---

# Submission checklist and journal-fit rationale

Companion to [`nr4a3-fusion-transcriptional-output.md`](./nr4a3-fusion-transcriptional-output.md) and
[`nr4a3-fusion-transcriptional-output-cover-letter.md`](./nr4a3-fusion-transcriptional-output-cover-letter.md).

## 1 · Recommended venue

**Primary: *Genes, Chromosomes & Cancer* (Wiley), Original Research Article.** It is the field's
dedicated journal for the genetics and genomics of neoplasia, and specifically for fusion-driven
sarcomas — the exact audience that reads and cites EMC fusion biology. It is receptive to focused
genomic re-analyses of the kind this manuscript is, which makes it a realistic home for a careful,
explicitly incremental result. Crucially, it is a **hybrid** journal: open access is optional (an
article-processing charge of roughly US$4,810 applies *only if* the open-access option is chosen), and
the traditional subscription route carries **no author charge**. Publishing via the subscription route,
with a free bioRxiv preprint as the open copy, satisfies the standing constraint that the author pays
nothing.

**Aspirational alternative: *The Journal of Pathology* (Wiley).** This is the natural home in one
respect — it published the three primary papers this manuscript synthesises (Subramanian 2005, Filion
2009, Brenca 2019). It is also hybrid (subscription route free; open access optional at ~US$5,450), so
the $0 constraint is met. It carries a higher desk-reject risk for an explicitly incremental,
single-author re-analysis and a tighter length preference (see §3), so it is the second choice, not the
first.

**Realistic fallback: *British Journal of Cancer* (Springer Nature)** — hybrid, subscription route
free, broad cancer-genomics scope.

**Preprint (open copy, free): bioRxiv**, Cancer Biology / Genomics. bioRxiv accepts computational
re-analyses of public data at no charge, and both Wiley journals above permit bioRxiv preprints.

> **Why not the obvious open-access venues.** Several journals that would fit topically have moved to
> gold open access with a mandatory APC and are therefore excluded by the $0 constraint unless a full
> waiver is granted: e.g. *BMC Cancer*, *Cancer Medicine*, *ESMO Open*, and — verified 2026-08-07 —
> *The Oncologist* (~US$3,668) and the *Journal of Cancer Research and Clinical Oncology* (~US$4,390),
> both of which flipped from hybrid to full OA. Journal fee models change; confirm the subscription/no-
> APC route in writing at submission.

## 2 · Standards compliance (target: GCC; also satisfies J Pathol)

| requirement | target | status in manuscript |
|---|---|---|
| Article type | Original Research Article | ✔ declared |
| Abstract | GCC: flexible · J Pathol: unstructured ≤300 words | ✔ unstructured, 299 words by the command in §3 (which counts markdown emphasis tokens, so the prose count is slightly lower); at the J Pathol limit |
| Keywords | 5–7 | ✔ 7 keywords |
| Structure | Introduction · Methods · Results · Discussion · Conclusion | ✔ full IMRaD, plus Limitations, two appendices and a Supplementary Information file |
| References | GCC: any consistent style · J Pathol/EJC: ≤40–50 | ✔ 12 primary + gene-set resources, Vancouver style |
| Data availability statement | required | ✔ public accessions + open code repository, Zenodo archive planned |
| Funding statement | required | ✔ "None" |
| Competing-interests statement | required | ✔ "None" |
| Ethics / consent statement | required | ✔ not required — public de-identified data only, stated |
| Author contributions | required | ✔ sole author |
| Generative-AI disclosure | required (Wiley/Elsevier policy) | ✔ explicit statement; AI not an author; author takes responsibility |
| Reproducibility | encouraged | ✔ seeded, offline `--check`, independent second implementation |

## 3 · Element counts

⚠ **These were measured, not estimated.** The previous version of this section understated the main
text by roughly a quarter and miscounted the body tables, because both figures were carried forward by
hand from an earlier draft. Re-measure after any material revision rather than editing these numbers
from memory:

```bash
P=research/manuscripts/nr4a3-fusion-transcriptional-output.md
awk '/^## Abstract/,/^## Data and code availability/' $P | grep -v '^|' | grep -v '^> ' | grep -v '^!\[' | wc -w
grep -c '^|---' $P          # all tables; subtract those after "## Data and code availability"
grep -c '^!\[Figure' $P
```

- **Abstract:** 299 words by the command above, which counts markdown emphasis tokens as words; the prose count is slightly lower. At GCC's flexible limit and at J Pathol's ≤300.
- **Main text:** ~7,090 words of prose from Abstract to Conclusion, excluding tables, figure captions
  and back matter. GCC sets no fixed limit. **For *The Journal of Pathology* this would need trimming
  toward ~4,000**; the material that would go first is §3.6's stratified narrative and §2.6's method
  prose, both of which already have fuller versions in the SI.
- **Display items:** **5 figures** (per-sample dots, the size-matched null, the evidence catalogue, the
  instrument-convergence matrix, the muscle-admixture control) and **9 numbered tables in the body**,
  plus 4 unnumbered tables in Data availability and the two appendices.
- **Supplementary Information:** `nr4a3-fusion-transcriptional-output-SI.md`, ~5,480 words, 6 numbered
  supplementary tables (S1–S6) and six method sections (§S1–§S6).
- **References:** 12 numbered primary references plus separately listed gene-set resources and the GEO
  series record.

## 4 · Reporting-guideline note

This is a re-analysis of previously published, publicly deposited datasets, not a de-novo systematic
review, so no single EQUATOR checklist applies in full. Study/dataset selection is stated transparently
in Methods §2.2 (three EMC cohorts on three platform families, with the comparator arm of each named and
the exclusions accounted for). The synthesis is a cross-platform sign-concordance reading rather than a
pooled effect estimate, and the manuscript states in Limitation 2 that the three cohorts are never
pooled. Where a reviewer requests it, a MOOSE- or SWiM-style summary of dataset identification can be
added as a supplementary item.

## 5 · In-silico strengthening — done, and still available

### Done (2026-08-07, offline, $0)

A robustness package was added — now Methods §2.6 and Results §3.5, with the full panel as Supplementary Table S3 — produced by
`nr4a3_fusion_targets_robustness.py` → `nr4a3-fusion-targets-robustness.json` with a `--check` mode.
It closes two of the manuscript's own stated limitations and adds two orthogonal axes:

- **Exact sample-label permutation test** — the self-contained null that preserves gene–gene
  correlation, which the size-matched (competitive) null cannot see. Because the arms are 6-vs-29 and
  10-vs-6, all 1,623,160 and 8,008 label assignments were **enumerated completely**, so the p-values are
  exact rather than sampled. This is the single most reviewer-relevant addition: it directly answers
  Limitation 9, which had conceded the empirical p was "a screen, not a test".
- **Leave-one-out jackknife** over the EMC arm — no row in the panel changes sign when any single EMC
  tumour is dropped.
- **Rank-based re-read** on within-array percentiles — every row keeps its sign, so nothing rests on the
  z-scoring convention.
- **Benjamini–Hochberg** q-values across the per-gene permutation p-values (Limitation 8).

⚠ **It was not uniformly flattering, and the manuscript now says so.** *ENO3* survives everything
(q = 0.0004 / 0.0006); *PPARG* survives on GPL3290; **SEMA3C does not reach significance under the
permutation test on either platform**, and the **PPARγ KO_UP falsifier does not either**. Those two
demotions are stated in §3.12 and back-referenced from §3.5 and §3.9 rather than left in the artifact.

### Also done (2026-08-07) — the NBRE motif scan, via CI

Discussion §4.2 item 4 named an NBRE scan as the paper's free next step. The scanner already existed
(`emc_ret_target_scan.py`, built for the RET lane) with a dinucleotide-preserving shuffle null and a
198-window background panel — but it had **never been run**: its artifact read `_status: NOT_RUN`,
because the Ensembl fetch needs egress the dev sandbox does not have. It was one $0 CI dispatch away.

`SEMA3C` was added to the scanner's focus panel (`ENO3` and `PPARG` were already there), the workflow
was dispatched with `ref=<branch>` so the run used this branch's code, and the module was then extended
to compute the background-panel rank for **every** focus gene rather than for RET alone — the
RET-specific keys and verdict are untouched. Results are Methods §2.6 and Results §3.10:

- ***ENO3*** carries 4 exact NBREs and clears **both** nulls (shuffle p = 0.034; panel p = 0.025;
  GC-matched p = 0.018) — the only class-A gene enriched above its own composition.
- ***PPARG*** carries 3, not above composition. ***SEMA3C*** carries **none**.
- So the sequence axis converges with §3.12: *ENO3* is supported by every instrument applied,
  *SEMA3C* by neither the permutation test nor the motif scan.
- ⚠ Stated in the paper: a motif is not occupancy; *SEMA3C*'s zero does not contradict Brenca *et al.*,
  who reported an NBRE-**like** site; and the hit positions do not reproduce the published coordinates
  for either *ENO3* or *PPARG*.

*(Side finding for the RET lane, not this paper: RET's own window scores `ELEMENT_PRESENT_BUT_NOT_ABOVE_CHANCE`
— 1 NBRE, shuffle p = 0.577, panel p = 0.663. That is the RET lane's answer to its own question and is
recorded in its artifact.)*

### Also done (2026-08-08) — the one-mismatch (NBRE-like) null, offline

The remaining sequence question was whether *SEMA3C*'s 39 one-mismatch matches — the most of any gene
scanned, and the form of site Brenca *et al.* actually reported — meant anything. Computed on the same
shuffles (one extra scan per shuffle, no second pass, every exact figure unchanged): **it does not.**
Against its own composition the null mean is 33.7 (p = 0.203) and the GC-matched panel gives p = 0.118;
only the composition-naive raw panel rank suggests enrichment (p = 0.040), and *SEMA3C*'s window is the
most AT-rich of the set. *ENO3*'s one-mismatch count is likewise not enriched (p = 0.336), so its
signal sits in exact NBREs rather than degenerate ones.

**Nothing further on the sequence axis is worth running.** Sequence cannot settle occupancy; the
discriminating experiment is a cistrome in a fusion-expressing cell, which no computation supplies.

### Also done (2026-08-08) — the confound audit, offline

Produced by `nr4a3_fusion_targets_confounds.py` → `nr4a3-fusion-targets-confounds.json`, and reported
as main-text §3.4–§3.7 with the full tables as Supplementary S4–S6:

- **comparator composition read from the GEO sample titles**, which corrected "6 fibrosarcoma" to 6
  *myxofibrosarcomas* and established that 23 of 29 GPL6244 comparators are themselves myxoid;
- **every comparator stratum contrasted separately**, each with its own exact permutation p — the test
  that shows *ENO3* invariant across strata and *SEMA3C* reversing sign;
- **the reference-pool-matched contrast** on GPL3290, where 3 GIST comparators sit on a different pool
  from all 10 EMC samples;
- **covariate-adjusted sensitivity** against an 11-gene matrix panel filtered by provenance so no
  EMC-selected gene enters it;
- **the skeletal-muscle admixture control** for *ENO3*, using the two pooled-muscle samples GSE24369
  carries in neither arm;
- **a percentile calibration of the 3SEQ arm** against all 14,120 genes in that deposit
  (`gse28866_tumour_vs_normal.py` → `ratio_calibration`), which was the one arm reported without the
  calibration the paper's own §1.3 demands.

### Also done (2026-08-08) — the occupancy axis, offline

Produced by `nr4a3_fusion_targets_occupancy.py` → `nr4a3-fusion-targets-occupancy.json`, reported as
main-text §3.11 Table 9 and as a sixth column of Figure 4. It closes the paper's largest structural
gap — it had **no chromatin data at all** — using 86 NR4A ChIP-seq peak sets already cached in this
repository, with **no fetch**. It has since grown to 110 peak sets; see the Haller entry below.

⚠ **It is a bounded negative, and the first pass got it backwards.** Read as raw counts, *ENO3*
looked like the top of 13 loci. Calibrated against a 198-gene background panel it is not: the deepest
catalogue puts a promoter peak in **82.8% of arbitrary genes**, so a bare count is the same
uncalibrated reading §1.3 of the manuscript exists to refuse. No class-A gene carries unusual NR4A
occupancy — so the surrogates cannot substitute for the missing fusion cistrome, which is the point.
⚠ *The counts in the first version of this entry (86 peak sets, 8 informative experiments, 1 of 24
tests against 1.2 expected) are superseded by the Haller deposit below; the conclusion is unchanged.*

### Also done (2026-08-08) — the Haller NR4A3 cistrome, and what it changed

The one option this checklist listed as still available was retrieved. Zenodo 10.5281/zenodo.1483691
(Haller *et al.*, PMID 30664630) carries NR4A3 ChIP-seq in three acinic cell carcinomas and one
normal parotid gland at **8,501–18,666 peaks** — 55–121× the deepest NR4A3 peak set the repository
previously held (154), and the first NR4A3 occupancy data in human tissue this paper has.

⚠ **It is not a fusion and the manuscript says so in every place it appears.** Acinic cell carcinoma
activates *wild-type* NR4A3 by enhancer hijacking. §3.2 records native NR4A3 failing to activate the
*PPARG* promoter the fusion activates, so a native cistrome is *expected* to disagree with a fusion
one at exactly that gene.

- **The build was measured, not assumed.** A BED file carries no genome build, and on chr10 an
  intersection on the wrong one does not fail — it silently reports another locus. H3K4me3 marks
  active promoters, so on the correct build it must recover most of the background panel: **90.6–93.9%
  on hg19 against 32.2–33.6% on hg38**, all four samples independently. Both an absolute floor and a
  ratio are required, because the builds agree over much of the genome and ~33% is the wrong-build
  floor rather than noise.
- **The axis is now 110 peak sets, 12 informative experiments, 36 tests**, and the conclusion is
  unchanged and better supported: 2 hits at p < 0.05 against 1.8 expected, **binomial p = 0.54**.
- ⭐ ***PPARG*'s zero became a real negative.** It carries no promoter-window peak in any of the four
  deep NR4A3 experiments, which recover 49–68% of the background panel — so they can find an
  arbitrary gene and did not find this one. That sits against Filion *et al.*'s perfect NBRE at
  −675 bp and band shift, and §3.11 reports the tension rather than resolving it.
- ***ENO3*'s single nominal hit is in the NORMAL parotid gland** (p = 0.035), not any carcinoma —
  the opposite shape from a tumour-driven signal.
- ⛔ **Two defects the new data exposed, both one commit from the manuscript.** The occupancy module
  recorded each peak set's antigen and never filtered on it, so the deposit's 20 CTCF/H3K27ac/
  H3K27me3/H3K4me3/super-enhancer files entered an *NR4A occupancy* test. And the verdict decided
  significance with `observed > expected`, which is not a test when expected is fractional: at 2
  against 1.8 it flipped to "at least one class-A gene exceeds the background panel more often than
  chance would give." Both fixed; the second is now a binomial tail.

### Also done (2026-08-08) — the fourth-cohort question, asked and answered

This checklist carried "**a fourth EMC expression cohort**, if one exists" as an open row for as long
as it has existed. It was never a blocked item; it was an unasked question, and the whole cost of
asking it was one $0 CI dispatch. `emc_cohort_search.py` (mode `cohort-search`) puts six deliberately
overlapping queries to GEO, records every one including those returning nothing, and grades what
comes back. **No fourth cohort.** Main-text §2.7 (method) and §3.13 Table 10 (result); Limitation 1
is now bounded rather than merely stated.

⚠ **Three things about it are worth more than the answer**, and two were found only by running it.

- **A positive control, because a null from a search that finds nothing proves nothing.** The same
  queries had to recover the three cohorts already in use — and their EMC arm sizes, 6, 10 and 4,
  read from GEO **sample titles** rather than from the series matrices the paper scores. All three
  agreed. Had they not, the module withholds the negative as uninterpretable rather than reporting
  it, and the headline keys on the whole control (an early version keyed on recovery alone, so an
  arm-size disagreement could set `passes: false` and still print a clean negative).
- **A three-level dedup, because the trap is real.** `GSE170983` is 99 samples, four of them EMC,
  under its own accession — and it is the same Brunner deposit as `GSE28866`, already the paper's
  3SEQ arm, with the same four tumours. Counting it would have raised the apparent EMC total to 24
  without adding a patient. Candidates are checked at accession, linked publication, and GSM identity
  against all 157 samples the three cohorts read. Stated in the paper at §2.2.
- **Sample-level reads for every series, not a title screen.** The first version gated the sample
  read on whether a series' prose named EMC, which would have discarded `GSE43632` (*Large scale
  screening for fusion genes in sarcoma patient samples*) and `GSE80126` on their titles — and, worse,
  would have skipped `GSE24369`, the cohort titled after LGFMS that carries six EMC tumours and is
  this paper's own standing example that a GEO title is a claim rather than a measurement.
- ⛔ **And a broken query returns zero exactly like an empty one does.** Four of the six queries first
  returned zero, all four sharing an `"expression profiling"[Filter]` clause the two productive
  queries lacked — one of them asking GEO for human chondrosarcoma expression series, which it cannot
  honestly answer with nothing. Re-asked with the restriction lifted, three returned **2, 4 and 32**
  records, taking the search from 7 series to **22** and supplying **15 of the 17 sample-level zeros**
  that give the negative its weight. The fourth returned zero again and is the only zero read as an
  absence. **The unrepaired search would have rested on two queries while presenting itself as six** —
  and it was caught only because the per-query counts were measured against the artifact while
  drafting SI Table S7 rather than carried over from the draft.

### Still available (not required for submission)

| option | what it would add | cost | blocked on |
|---|---|---|---|
| **Intersect with the Haller 2019 NR4A3 ChIP-seq peaks** (Zenodo doi 10.5281/zenodo.1483691, open) | Whether the NR4A3 DNA-binding domain reaches these genes in a human tumour. ⛔ Must be framed exactly as §4.3 frames it — acinic cell carcinoma carries *native* NR4A3, not a fusion, so it can never be cited as a fusion cistrome | $0, CPU | dispatched 2026-08-08 (`ret-cistrome` at this branch); result pending |

## 6 · Optional presentation work (not required for submission)

- ✅ **Five figures now exist**, generated with matplotlib from the committed artifacts by
  `nr4a3_fusion_targets_figures.py` and emitted as 300 dpi PNG plus vector PDF. The earlier
  hand-emitted SVG was retired: `AGENTS.md` bans hand-computed SVG because it has no text measurement
  and cannot be rasterised for inspection before commit, and the retired figure was exactly that.
  Staleness is checked against a stamped content hash of every artifact each figure was drawn from —
  by `--check` locally, and in CI by
  `tests/test_nr4a3_fusion_targets_figures.py::test_the_provenance_stamp_matches_the_committed_artifacts`,
  so changing a number a figure draws without regenerating it turns the build red.
- ✅ **The promoter NBRE-motif scan is done** and is main-text §3.10 with full parameters in
  Supplementary §S6. *(This bullet previously said the scan was future work while §5 of this same
  document reported it as complete — two states of the same fact in one file.)*
- **Converting the instrument-control panel (§3.3) into a sixth figure** remains optional.
- **In-text citation style.** The manuscript uses a consistent author-name + PMID inline style with a
  full numbered reference list — accepted by GCC at initial submission ("any consistent style"). The
  PMID on each inline citation is a deliberately robust provenance anchor. Converting the in-text
  citations to the journal's numbered superscript (Vancouver) format is a one-pass reference-manager
  step at submission or first revision, and journals reformat references at production regardless.

## 7 · Residual author-only steps before clicking "submit"

These are outward-facing or identity-bound actions that only the author can take; the manuscript
content itself is submission-ready.

1. **Add an ORCID** to the title page and cover letter (bracketed placeholder present).
2. **Mint a Zenodo DOI** by archiving the code repository at the submitted commit, and paste it into the
   Data and code availability section (the section already states this is planned at acceptance; some
   journals prefer the DOI at submission).
3. **Verify the remaining gene-set-resource identifiers** (Enrichr, ChEA, TRRUST, MSigDB Hallmark)
   against their primary sources and add full bibliographic identifiers; the manuscript currently cites
   them to the depth the held source supplies and flags this explicitly, in line with the project's
   citation-provenance discipline.
4. **Elect the subscription (non-open-access) route** at the fee step so no APC is charged, unless a
   full waiver for open access has been secured.
5. **Fill the bracketed fields** in the cover letter (date, ORCID) and confirm the current editor
   addressee on the journal masthead.
6. **Deposit the bioRxiv preprint** and, after it posts, add the preprint DOI to the cover letter.
