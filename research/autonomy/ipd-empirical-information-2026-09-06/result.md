---
id: DOC-IPD-EMPIRICAL-RESULT-20260906
title: Negative empirical development result
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Preserve source evidence, exact execution scope and limitations for the current research checkpoint.
scope: Reader metadata added at integration; scientific source body unchanged.
audience: [maintainers, autonomous research agents]
---

# Empirical pilot completed: do not expand the disagreement rule

The frozen development pilot completed all 120 planned cases in 576.672 seconds. Both published reconstructors returned usable, independently checked statistics in every case. The prospective continuation gate failed: there were too few distinct-source errors, and the primary apparent gain came from two precision variants of one LUAD pseudoarm assignment. The eleven reserved source groups remain unopened. No held-out expansion or manuscript is supported by this checkpoint.

## What was actually measured

The [public benchmark](https://doi.org/10.5281/zenodo.18320575) supplies single-curve TCGA/GEO records, not randomized treatment comparisons. The outcome-blind source manifest selected ten patient-ID-disjoint TCGA cohorts: STAD, CESC, KIRC, LUAD, OV, UCEC, LGG, GBM, SARC and BRCA. Their 4,416 distinct source patient IDs supplied 30 deterministic random pseudoarm assignments. Each assignment produced two probability-precision by two risk-density variants, giving 120 dependent benchmark cases. All ten cohorts were usable; no source exclusion, timeout, unrun case or independent-statistic discrepancy occurred.

Ground truth was the original realized ordinary logrank statistic for each exact assignment. One of the 30 original assignments rejected at p<.05; its four reporting variants account for all four original-positive cases. The other 116 variants were original-negative. The always-nonsignificant baseline therefore made 4/120 errors. These are errors relative to realized original IPD, not population type-I errors, treatment effects or disease-specific efficacy.

The experiment released exact event times, rounded survival probabilities at two or three decimals, initial sample sizes, event totals and two or four pre-event risk counts. This is generous, idealized numerical information. It does not model image extraction or uncertain event coordinates. Source time units are unspecified in the inspected archive metadata; all statistics compare pseudoarms within the same cohort, with no cross-source time comparison. TCGA SARC is not asserted to contain EMC.

## Fixed results and allocation decision

| Measure | IPDfromKM | CIFresolve approximate QP |
|---|---:|---:|
| Successful returned cases / attempted | 120 / 120 | 120 / 120 |
| Threshold errors, all cases | 3 | 2 |
| Source groups containing threshold errors | 2 | 1 |
| False rejects / false nonrejects versus realized original | 3 / 0 | 2 / 0 |
| Signed-Z sign changes, all cases | 10 | 2 |

Sign changes are recorded separately from threshold errors; they do not imply statistically established effects.

At the primary 75% retention, each rule retained 90 cases and used the same incumbent IPDfromKM decisions:

| Fixed triage rule | Errors among retained cases |
|---|---:|
| Own distance from the significance threshold | 2 / 90 |
| Own margin minus continuous between-method signed-Z disagreement | 0 / 90 |
| Binary decision agreement, then own margin | 0 / 90 |

The two removed errors are LUAD seed 61003 with sparse risk tables, once at each probability precision. This is one pseudoarm assignment and one source, not two independent successes. The continuous rule shows no advantage over the binary-disagreement baseline at the primary retention. Both primary 75% selections contained zero original-positive cases, emphasizing the null-heavy scope. At 90% retention the continuous rule retained all four original-positive variants, but that secondary observation cannot replace the prospective primary gate. The full retention/error curves and original/predicted class counts are in `development/summary.json`.

The frozen gate required at least eight incumbent error cases across three sources and beneficial primary changes across two sources, in addition to coverage and effect-size criteria. Observed incumbent errors were three across two sources, and the primary gain occurred in one source. Those requirements fail. The numerical two-case/20% gain and no leave-one-source-out reversal conditions pass, but do not rescue the failed gate. No extra sources, seeds or rules were searched to meet it.

Dense risk reporting removed all three IPDfromKM errors seen with sparse reporting (two LUAD precision variants and one OV variant). CIFresolve had two OV errors at two-decimal precision, one sparse and one dense, for no net density benefit. These paired developmental observations are preserved; they do not establish population information savings. Counts repeated across reporting variants and seeds are dependent. No binomial confidence interval treating 120 cases as independent was calculated, and no claim of a calibrated population error guarantee is made.

## Validation, provenance and execution

The coordinator authorized the exact original protocol, source-manifest and both pre-outcome amendments. `authorization.json` and `development/execution-freeze.json` preserve the four hashes, actual command, runtime locations and source-code hashes. No empirical outcome was inspected before that authorization; metadata preparation accessed labels, headers and patient IDs only.

Original IPDfromKM 0.1.10 and CIFresolve 0.1.1 package calls were retained. The installed survival 3.8.6 interface leaks an explicit timefix argument into model.frame. The documented local wrapper changes only the formal default to FALSE, checks an identical function body and leaves installed package files unchanged. Actual R fixtures verify exact and near ties and zero variance. Degenerate results cannot be converted to confident nonsignificance.

Every reconstructed R Q/p was independently checked by the Python event/risk-set calculation during execution. `verify_original.py` and `verify_original.R` separately reconstructed all 30 original assignments from the authorized source records and verified their signed Z, Q and p in R; all passed. Synthetic tests cover tied-event arithmetic, distinct near ties, zero variance, arm-swap sign, release risk counts, durable discrepancy/unrun accounting and the fixed matched-retention comparison. No discrepancy, package failure or invalid source required empirical repair.

This is an empirical development test of a separate triage question. It does not repair the prior inverse solver's 0/4 stress certification result. Generic bounds, reconstruction and abstention novelty remain withdrawn; the primary benchmark and Titman/CIFresolve are prior art. The small null-only result does not justify a paper. Preserve its negative allocation outcome and proceed with stronger independent research.

The source base is ea974de61c99f0b282af55eee584c637a7955bbd. All tracked writes are confined to this packet in the reserved writer worktree. No commit, push, manuscript, publication, full preflight, paid API or GPU work was performed. Worker model/effort identifiers and token usage were not exposed; routine medium was requested by the coordinator. Scientific run and verification processes are finished; nothing remains running. Coordinator independent packet review and integration remain outstanding.
