---
id: DOC-FP-RESIDUAL-COUNT-MAP
title: "COUNT-MAP — molecular confirmation (26/58/12/67) versus named partner (24/57/11/62)"
level: L4
kind: evidence
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# COUNT-MAP — the two sets of integers, stage by stage

⛔ **These are two DIFFERENT sets of integers describing two DIFFERENT ascertainment stages.** The focused
verification found the manuscript printing a "molecularly characterised" column of **24 / 57 / 12 / 62**,
which duplicated the named-partner counts for three of the four series. It is corrected here.

⚠ **NOT ALL NUMBERS IN THIS PAPER ARE INVARIANT UNDER THIS BATCH.** The molecular-confirmation cells moved.
The named-partner cells did not, and the prevalence arithmetic that rests on them is unchanged.

## The mapping

| series | (1) total in series | (2) molecular confirmation / successful test | (3) named partner assigned — **the prevalence denominator** | (4) followed for outcome | (2) − (3) and what it is |
|---|---:|---:|---:|---:|---|
| Agaram 2014 (MSKCC, USA) | 26 | **26** | 24 | 26 | 2 — *NR4A3*-rearranged with no identified 5′ partner |
| Huang 2023 (Taiwan) | 58 | **58** | 57 | **UNKNOWN** | 1 — *NR4A3*-rearranged, partner not identified |
| Lenz 2023 (Czech Republic) | 17 | **12** | **11** | **UNKNOWN** | 1 — *NR4A3*-positive, no other alteration identified. **Plus 5 cases outside (2) entirely**, in which molecular testing did not succeed |
| Paioli 2021 (Italian Sarcoma Group) | 67 | **67** | 62 | **UNKNOWN** | 5 — **unexplained by the abstract**, and not characterised as an unassigned-partner residue of a known kind |
| **totals** | 168 | **26 / 58 / 12 / 67** | **24 / 57 / 11 / 62 = 154** | — | — |

## What each confirmation cell means — the assay and result definition differ and are NOT harmonised

- **Agaram 26.** All 26 received *NR4A3*/*EWSR1* FISH and all 26 had an *NR4A3* rearrangement (retained full
  text, line 626). Two of the 26 had no identified 5′ partner. Follow-up is reported for all 26.
- **Huang 58.** FISH confirmed 58 EMC (retained primary abstract, PMID 36948401); one of the 58 was
  *NR4A3*-rearranged with no identified partner.
- **Lenz 12.** 17 in the series; molecular testing was successfully performed in 12/17 (authentic primary
  abstract, PMID 36563884, sha256 of the retained container
  `158c5005e6493416d0620d4ab49975b67b0d9182e9fcc2d0c34a4aa9358d35ae`); one of the 12 was *NR4A3*-positive with
  no other identified alteration. **This is the one series where all three stages differ from each other.**
- **Paioli 67.** The 67 were identified under an inclusion rule requiring a molecularly confirmed *NR4A3*
  rearrangement, so confirmation and series total **coincide by construction** rather than by measurement.
  Named-partner counts account for 62 and the five-case residue is not explained.

## Unknown denominators, named as unknown

⛔ **Stage (4), followed for outcome, is UNKNOWN for Huang, Lenz and Paioli.** No retained source supports a
value for any of them.

⛔ **Huang's "53 followed" is NOT reinstated.** That figure came from the withdrawn Table 1 reading. It is
quarantined at `cohorts[huang-2023-outcome].withdrawn_2026_09_08.removed_denominators` and is not used to
complete any table. The citation's current `population` field no longer carries it.

⛔ **Paioli's five-case residue is recorded as unexplained**, not imputed and not classified.

## What did NOT change

- The **named-partner** counts **24 / 57 / 11 / 62** and their sum **154**.
- The partner totals over them: EWSR1 120/154, **TAF15 28/154 = 18.2 % (95 % CI 12.9–25.0)**, TCF12 5/154,
  TFG 1/154, and the per-cohort TAF15 range 15.8–29.2 % (spread 13.4 points).
- Every event cell in analysis A and analysis B, and every source exclusion.
- Verified mechanically after the regeneration: **0 numeric leaves changed, 0 removed, 13 added**, and all 13
  added leaves are inside the new, documented `analyses.C_partner_prevalence.ascertainment_stages` block.
  Evidence: `checks/04-check-after-regeneration/`.

## What this mapping does not establish

Nothing about clinical selection, patient independence between series, or population representativeness. The
prevalence figure remains a **conditional share among named-partner-assigned cases in four selected series**.
The differences between stages are not a missingness model; no imputation is performed and no
missing-at-random assumption is made.
