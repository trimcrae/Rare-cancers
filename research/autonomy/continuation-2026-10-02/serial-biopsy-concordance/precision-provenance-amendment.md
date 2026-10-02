---
id: MEMO-CHECKPOINT04-CD8-PRECISION-AMENDMENT
title: Post-result clarification of CD8 decimal provenance
kind: memo
status: live
level: cross-cutting
purpose: Clarify numerical precision after independent review without rewriting the frozen analysis record.
scope: Three included IHC cells and interpretation of exact ties in the paired CD8 analysis.
audience: [maintainers, autonomous research agents]
date: 2026-10-02
last_verified: 2026-10-02
---

This dated amendment follows the executed analysis and independent review. The frozen plan, executed script, results, findings and receipt remain unchanged. No additional computation was performed for this amendment.

The executed script calculated decimal differences from the accepted extraction's normalized `distinctNumericValues`, rather than directly from preserved `sourceValues.valueLiteral` strings. Accordingly, its exact-tie rule means exact equality of those normalized decimal inputs. It should not be described as preserving every original source-literal decimal digit. Three included IHC cells differ at trailing decimal precision:

| Patient | Timepoint | Preserved source literal | Normalized input used |
|---|---|---|---|
| C-4DV3D5 | On-Treatment | 4.1500000000000004 | 4.15 |
| C-H7RF5A | Baseline | 4.6100000000000003 | 4.61 |
| C-LX87X3 | On-Treatment | 1.1000000000000001 | 1.1 |

The independent reviewer reconstructed the calculation from the source literals using exact rational arithmetic and an independently implemented rank calculation. That calculation retained all 13 shared pairs, six concordant and seven discordant directions, no zero changes, and 13 distinct changes for each assay. All change ranks and direction results were preserved; Spearman rho remained 11/182 (0.06043956043956044). Thus this is a provenance/precision clarification, not an aggregate-result correction. It does not establish accuracy beyond the published measurements.

The review is recorded in `checkpoint04-serial-review/review.json`, with literal differences in `independent-results.json`. The independently executed result has SHA256 `43c96810c9bca8ab464428671463e442ef3647e8348bc530b0c37a0f93d48d8b`; its script has SHA256 `1f2519bab5b14db6a6314285a2ba0b884d123ecdcd84624e9dae13739a928800`. Review scope did not include a new primary IHC workbook extraction or raw-RNA reprocessing. The review records final execution exit code 0 and an initial exact-value assertion failure that exposed these precision differences.
