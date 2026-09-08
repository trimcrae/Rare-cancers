# COLLECTION MM1 and BM1 — mortality mechanisms, and biomarker-selected classes

Collected 2026-09-08 by the campaign parent. Two distinct papers, two independent workers.

| worker | paper | model entries | tool pairs | self-reported |
|---|---|---|---|---|
| MM1 | `research/manuscripts/emc-mortality-mechanisms-paper.md` | `claude-opus-5` only | 34 / 34 | 29 |
| BM1 | `research/manuscripts/dependency/emc-biomarker-selected-classes.md` | `claude-opus-5` only | 46 / 46 | 33 |

Both transcripts are retained and `cmp`-verified. The observed tool counts govern; both self-reports
understate.

---

## MM1 — mortality mechanisms

47 quantities adjudicated: 38 MATCH, 4 MISMATCH, 5 NO SOURCE LOCATED. The parent re-derived every
claim it acted on:

| MM1 claim | parent's independent read | outcome |
|---|---|---|
| the pooled cause split has no leaf and the field designed for it is unset | `emc-mortality-decomposition.json → direct_cause_split` has exactly **2** rows; `emc-relative-survival.json → convergence.cause_split_overall_competing_share_pct` = **None**, while `cause_split_competing_share_pct` = **[30.8, 10.0]** | **CONFIRMED** |
| a completed background check with an unfavourable result is omitted | `background_mortality_check` = `status: RUN`, observed 20.0% against expected 11.3%, `ratio_observed_to_expected` **1.77**, with the artifact's own reading that a ratio far above 1 makes the decomposition unquotable | **CONFIRMED** |
| 400 is a cap, not a retrieval count | `emc-mortality-probe.json → caps.fulltext` **400**, `summary.fulltext_attempted` **400**, `summary.fulltext_retrieved` **328** | **CONFIRMED** |
| "roughly threefold" is unsupported | `corpus.death_sentences_in_those_papers` **116** against `headline.classified_deaths` 52 — about 2.2×, and the summed per-paper sentence indices are fewer than the deaths | **CONFIRMED** |

**Applied, thirteen replacements plus a new Table 2 note.** The pooled 21.7 % is no longer offered as
a measured share in four places: the Abstract now spans the two stratum values, Table 2's combined row
is labelled the author's sum and carries a note saying the artifact declines to pool because the
strata differ in follow-up and by a factor of three in competing share, §3.5's convergence is stated
against both strata, and Appendix A.1's supersession names them. §3.6 now reports the 1.77 ten-year
ratio and what the artifact says it means, instead of ending on the two favourable horizon-matched
ratios alone. "Between a fifth and a third" became "between a tenth and a third, depending on stage",
which is what the paper's own Table 2 says. The Chinese trial's recorded internal inconsistency
travels with the citation. "The only non-antitumour intervention class" is scoped to the classes this
study screened. "It has not been measured" became "no measurement was found in the open-access record
searched here". The sentence-inflation claim now gives the two counts instead of a ratio, and the
palliative-care search names its 25-record denominator.

`lint_style` 0 ERROR before and after.

---

## BM1 — biomarker-selected classes

5 classes and 31 quantities: 30 MATCH, 1 NO SOURCE LOCATED, 0 MISMATCH.

**The failure mode this lane was sent to hunt is not present.** BM1 looked for class inheritance
stated as an EMC result and found none: §1 carries the DepMap panel's "contains no EMC line" warning
inline, and §2.5 repeats it in the sentence that uses a dependency figure. That is worth recording as
a negative finding, not passed over.

The parent re-derived the two structural claims:

| BM1 claim | parent's independent read | outcome |
|---|---|---|
| every gene group is a repo-curated membership list whose artifact requires the paper to say so | all **20** panels in `emc-expression-panels.json` carry `provenance` beginning "⚠ REPO-CURATED pathway-membership list. This is NOT a published gene set or signature. Any statement resting on it must say so."; the manuscript contained **0** occurrences of "curated", "gene set" or "signature" | **CONFIRMED** |
| the incidence sentence has no artifact and the registry points the other way | no artifact holds an annual worldwide count; `emc-clinical-registry.json → overview.howCommon` = "Roughly 1-3% of all soft-tissue sarcomas. Estimated incidence is well under 1 per million per year." | **CONFIRMED** |

**Applied, four.** The motivating sentence now cites the registry's own recorded incidence instead of
an unsourced "few hundred patients per year". §2.4's "the class is not indicated" — an
indication-register claim the transcript evidence cannot carry, in a paper whose own opening says
every conclusion is about a selection criterion and never about whether a drug works — now says the
selection criterion is not met in these data. §2.2's methods paragraph now states, as the producing
artifact requires, that every group scored is a repository-curated membership list and not a published
signature. §2.3 now separates the four-subunit group score from the per-subunit claim.

**One correction to my own first pass.** Rewriting the §2.3 sentence broke a pinned figure:
`pinned-figures.json → biomarker_prc2_core_t_gpl3290` declares its context as the exact phrase "no
SWI/SNF tumour-suppressor subunit reads anywhere near a floor", and my rewrap moved that phrase off
the line carrying 1.71, so `lint_consistency` failed with `A-figure-not-stated`. I restored the phrase
intact on its original line and added the group qualifier after it. **The pin was not edited** — the
prose was fixed to satisfy it. `lint_consistency` is back to 0 ERROR across 29 files.

`lint_style` goes 48 → 49; the single addition is a `⚠` glyph in the new provenance sentence, matching
the file's own register.

---

## Recorded, not applied

- MM1's Appendix A.2 superseded 2.4 % has no retained leaf. It is a record of a withdrawn figure, not
  a live claim.
- BM1's five prior blind review seats were recorded at an earlier commit. Two `seat-statistics`
  blockers are already repaired in the current text — the parent confirmed both against the artifact —
  and that seat's `not_supported_as_written` verdict must not be quoted against the text as it now
  stands.

Neither verdict generalises beyond its own paper.
