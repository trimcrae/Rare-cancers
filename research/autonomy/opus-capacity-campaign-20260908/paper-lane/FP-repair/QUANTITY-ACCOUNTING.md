---
id: DOC-OPUS-CAMPAIGN-FP-REPAIR-QUANTITY-ACCOUNTING
title: "FP repair — every dependent quantity of the corrected sunitinib classification, before and after"
level: L4
kind: memo
status: live
purpose: >
  Account, quantity by quantity, for what the REF-B-2 source-classification correction did and did not
  move in the fusion-partner artifact, and record the one regeneration that produced it.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Quantity-by-quantity accounting for the REF-B-2 correction

**Method.** Both columns are read from the artifact itself — `BEFORE-emc-fusion-partner-pooling.json`
(the committed copy at `8c76f51bb`, sha256 `f60c550c…`) and the regenerated
`research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json`. Nothing here is retyped from prose.
The machine comparison over **every numeric leaf of the whole artifact** is
[`regeneration/numeric-delta.txt`](./regeneration/numeric-delta.txt).

| quantity | before | after | moved? |
|---|---|---|---|
| sunitinib TAF15 arm | `0/2` | `0/2` | **no** |
| sunitinib comparator arm — the stratum whose label changed | `6/8`, keyed `EWSR1::NR4A3` | `6/8`, keyed `non-TAF15` | **counts no; label yes** |
| primary (pazopanib alone) TAF15 arm | `0/3` | `0/3` | **no** |
| primary TAF15 Wilson 95 % upper bound | `56.1` | `56.1` | **no** |
| primary comparator arm | `4/19 = 21.1 %` | `4/19 = 21.1 %` | **no** |
| primary post-hoc Fisher p | `1.0` | `1.0` | **no** |
| secondary (both cohorts) TAF15 arm | `0/5` | `0/5` | **no** |
| secondary TAF15 Wilson 95 % upper bound | `43.4` | `43.4` | **no** |
| secondary comparator arm | `10/27 = 37.0 %` | `10/27 = 37.0 %` | **no** |
| secondary post-hoc Fisher p | `0.155` | `0.155` | **no** |
| secondary per-cohort rates | `[21.1, 75.0]` | `[21.1, 75.0]` | **no** |
| secondary per-cohort spread | `53.9` | `53.9` | **no** |
| overlap-sensitivity TAF15 denominator range | `[3, 5]` | `[3, 5]` | **no** |
| overlap-sensitivity comparator denominator range | `[19, 27]` | `[19, 27]` | **no** |
| overlap-sensitivity TAF15 upper-CI range | `[43.4, 56.1]` | `[43.4, 56.1]` | **no** |
| sensitivity analysis, TAF15 patient not evaluable, `0/2` upper bound | `65.8` | `65.8` | **no** |
| analysis B pooled TAF15 disease-specific death (PRIMARY prognostic) | `7/15 = 46.7 %` | `7/15 = 46.7 %` | **no** |
| analysis B comparator Wilson 95 % upper bound (PRIMARY prognostic) | `20.8` | `20.8` | **no** |

## Why nothing moved, and why that is not numeric invariance forced onto an invalid classification

⭐ **The secondary comparator arm was already a `non-TAF15` union.** The pazopanib comparator has carried
the `non-TAF15` label since before this repair; the sunitinib comparator carried `EWSR1::NR4A3` on an
inference the sources do not license. Correcting the sunitinib label makes the union **`non-TAF15` +
`non-TAF15`**, which is coherent, and leaves the estimand it supports — TAF15 versus non-TAF15 — identical
to the primary analysis's estimand on a larger denominator.

⛔ **No stratum is pooled as confirmed EWSR1 anywhere after this repair.** The key rename is accompanied by
a rewritten `stratum_definition` stating the directional reason, a new `assumptions` list separating what
the sources license from what they do not, a corrected `citations.davis2017.verification_note`, a corrected
`cohorts[sunitinib-2012-two-cases].overlap_note` (its two EWSR1 typings cover two of the eight, not eight of
eight), a corrected per-cohort heterogeneity key, and a verdict that names the comparator as `non-TAF15` in
both analyses and states that no rate on the page is a rate in EWSR1::NR4A3 patients.

⛔ **Nothing had to be withdrawn, because no comparison against a *verified EWSR1* arm existed.** The
partner-comparative secondary estimand that survives is TAF15 vs non-TAF15. Had the secondary estimand been
TAF15-vs-EWSR1, it would have been withdrawn rather than re-keyed; it was not, and §4.6 of the manuscript now
says so explicitly so that a reader cannot mistake the corrected pool for an EWSR1 comparison.

⛔ **No replacement rate was invented and no new source was consulted.** No network request was made.

⭐ **The primary prognostic counts are untouched.** Agaram 2014's and Huang 2023's `EWSR1::NR4A3` outcome
strata are typed by their own sources, keep that label, and every count and interval derived from them is
byte-identical (last two rows above).
