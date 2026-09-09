# Dated retirement record — three pooled disease-specific-death pins

Date: 2026-09-09 UTC. Author: FP author, campaign OPUS-CAPACITY-CAMPAIGN-20260908,
branch `claude/confident-bardeen-ji76cd`. Scope: guard maintenance only. No manuscript number,
source JSON, producer arithmetic or clinical record was changed by this batch.

## What was retired, and why

Three `artifact_figures` entries in `research/manuscripts/pinned-figures.json` bound

    analyses.B_outcome_by_partner.disease_specific_death

in `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json`. That path held the
**pooled** object `dod_pooled_agaram2014_huang2023`: Agaram 2014 + Huang 2023 over 73 patients,
7/15 = 46.7 % against 6/58 = 10.3 %, Fisher two-sided 0.0034.

§3.3 line 402 of `emc-fusion-partner-stratification.md` **withdraws** that pooled quantity — its
Huang inputs were removed as source-unverified, a scoped absence rather than proof the published
counts are wrong — and the object no longer exists in the artifact. All three pins had therefore
been failing `A-key-missing`, and were already failing before the FP residual batch.

⚠ The 46.7 % / 10.3 % / 0.0034 text still present in §3.3 lines 403–405 is inside an explicit
`Superseded, retained:` quotation. That is why the three old context regexes still matched, and it
is what made the failure look like a live headline that had been lost. It was not one. The parent
already recorded the dated correction withdrawing that "lost live headline" diagnosis at commit
**b58e0ed89**; this record reuses it rather than restating it. The correction register's N14
historical-origin wording is unchanged.

## Retirement disposition

Their **active** role as checks of a current pooled quantity is removed: the three entries are
deleted from `artifact_figures`. Their exact bytes are preserved below, and a dated pointer note
was appended to the registry's own `_artifact_figures_note`, alongside that list's existing
`⛔ ONE HOME RETIRED, 2026-08-28` precedent.

The pooled figures were **not** added to the registry's `superseded[]` list. They are already
carried in the manuscript under an explicit supersession marker, and adding a `superseded` entry
would be a new guard on a quantity outside this admitted batch.

## Retired entries, verbatim

```json
[
 {
  "id": "fusion_partner_dod_fisher_p",
  "description": "⛔ THE PAPER'S HEADLINE STATISTIC, AND IT WAS UNBOUND. Found 2026-08-26 by two independent blind seats (research/autonomy/review-seats/): §4.8's Limitations guarded a p = 0.0672 that appears NOWHERE else in the document — the retired Agaram-only value — while the live headline p = 0.0034 carried no caveat at all. Nothing cross-checked this paper's prose against its artifact: pinned-figures had no entry for it, and the generator's --check closes only the generator↔artifact loop. Three of that review's four blockers walked through this one gap.",
  "artifact": "research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json",
  "key": "analyses.B_outcome_by_partner.disease_specific_death.fisher_exact_two_sided_p",
  "context": "Fisher p = 0\\.0034",
  "must_appear_in": [
   "research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md"
  ],
  "_context_note": "⚠ The regex binds the number to its SURROUNDING PROSE, not to bare digits. A loose `10\\.3` matched inside a DOI on the reference line and produced a false positive on first run — and a guard that cries wolf is a guard someone switches off.",
  "regenerate": "python3 research/manuscripts/emc_fusion_partner_pooling.py --write, then update every prose quotation of the figure IN THE SAME COMMIT (CLAUDE.md rule 1.3)"
 },
 {
  "id": "fusion_partner_dod_taf15_percent",
  "description": "The TAF15 arm's disease-specific death proportion, quoted in the abstract, §3.3 and the §3.3 table. A typed value disagreeing with the artifact is the bug, not the artifact.",
  "artifact": "research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json",
  "key": "analyses.B_outcome_by_partner.disease_specific_death.taf15_arm.percent",
  "context": "7/15 = 46\\.7 ?%",
  "must_appear_in": [
   "research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md"
  ],
  "regenerate": "python3 research/manuscripts/emc_fusion_partner_pooling.py --write"
 },
 {
  "id": "fusion_partner_dod_comparator_percent",
  "description": "The EWSR1::NR4A3 comparator arm's disease-specific death proportion. Pairs with the TAF15 figure; the gap between them is the paper's central magnitude.",
  "artifact": "research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json",
  "key": "analyses.B_outcome_by_partner.disease_specific_death.comparator_arm.percent",
  "context": "6/58 = 10\\.3 ?%",
  "must_appear_in": [
   "research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md"
  ],
  "regenerate": "python3 research/manuscripts/emc_fusion_partner_pooling.py --write"
 }
]
```

## Replacement bindings

Coverage is replaced by three **distinctly named** entries on the Agaram-only object
`dod_agaram2014`, at
`analyses.B_outcome_by_partner.source_verified_recorded_outcomes.disease_specific_death`
(cohort `agaram-2014-outcome`, sourceId `agaram2014`, PMID 24746215):

| new id | key leaf | value |
|---|---|---:|
| `fusion_partner_agaram2014_dod_taf15_percent` | `taf15_arm.percent` | 42.9 |
| `fusion_partner_agaram2014_dod_comparator_percent` | `comparator_arm.percent` | 6.2 |
| `fusion_partner_agaram2014_dod_fisher_p` | `fisher_exact_two_sided_p` | 0.0672 |

★ **This is a disclosed change of guarded quantity, not a path fix.** 3/7 against 1/16 in one
consecutive series is not a corrected reading of 7/15 against 6/58 over 73 patients. The old ids
were not reused for the new quantity.

The new quantity is a crude proportion of RECORDED events over unequal, uncensored observation
windows; its intervals are marginal and its Fisher value post-hoc and descriptive. One further
EWSR1 patient died of unknown cause and is outside the numerator. Those qualifications are the
artifact's and the manuscript's own, and were not altered here.
