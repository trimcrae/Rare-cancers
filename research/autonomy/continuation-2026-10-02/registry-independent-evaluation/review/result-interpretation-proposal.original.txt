---
id: DOC-CHECKPOINT05-REGISTRY-RESULT-INTERPRETATION-PROPOSAL
title: Interpretation of the frozen nine-outcome registry evaluation
kind: memo
status: proposed
date: "2026-10-02"
last_verified: "2026-10-02"
purpose: Account for agreements, abstentions, and literal-preservation limits without retuning.
scope: Actual run 37044191718, nine prospectively screened eligible outcomes from six studies.
audience: [maintainers, reviewers]
---

The actual evaluation has two of nine joint exact-string agreements across status, family, version, and modifier. One is a source-supported RECIST 1.1 assignment for NCT04276493 outcome 5 (DCR); the other is appropriate unknown family for NCT02657486 outcome 0 (cystoscopy/cytology tumor response). The seven disagreements all withhold a family: five ambiguous and two unknown. No wrong assigned family is observed among these nine outcomes, but supported family assignments are missed.

| Study and zero-based outcome | Frozen source label | Actual output | Interpretation from emitted evidence |
|---|---|---|---|
| NCT04008706 / 1 | iwCLL 2018 | unknown | Explicit iwCLL wording absent from recognized mentions; incidental lowercase who is listed as WHO without assessment context. Family coverage miss. |
| NCT05508867 / 2 | Lugano 2014 | ambiguous | Lowercase who is treated as WHO beside the named Lugano family. Source has no actual paired-family conflict. Lugano 2014 version is also unrecognized. |
| NCT05327530 / 7 | RECIST 1.1 | ambiguous | Ordinary who produces spurious WHO conflict despite recognition of RECIST v1.1 in description. |
| NCT05327530 / 8 | RECIST 1.1 | ambiguous | Same source-context parsing pattern as outcome 7. |
| NCT05327530 / 9 | RECIST 1.1 | ambiguous | Same source-context parsing pattern as outcome 7. |
| NCT04557956 / 2 | RECIST 1.1 | unknown | Source spells out Response Evaluation Criteria in Solid Tumors 1.1; no mentions detected. Its malformed stable-disease prose is retained but does not erase the explicit family name. |
| NCT04276493 / 1 | RECIST 1.1 | ambiguous | Ordinary who creates spurious WHO conflict beside RECIST; the version after parenthesized acronym is also missed. |

These are coverage and context-parsing failures with conservative abstention, not seven wrong positive family assignments. This diagnosis is based on saved emitted mentions and exact source, not a classifier rerun or code change. The five ambiguous outputs do not reflect genuine paired named-family ambiguity in the frozen source. Modifier agreement is 9/9 because every compared modifier is null; it does not establish modifier-detection capability.

The source contains 68 outcomes and 421 measurements. The literal-fidelity file reports 460 literal rows, 45 companion rows, and fullOutcomeLiteralsEqual=true. This review independently matches all 442 category/denominator container hashes and all 1084 coordinate hashes (421 measurement and 663 denominator references) to the frozen source. Measurement coverage matches all 421 measurement pointers. The saved result set does not include extracted acceptance rows or their full literal payloads, so 460-row preservation and full-outcome equality remain wrapper assertions supported by coordinate/hash evidence, not a fresh row-by-row inspection of an exported acceptance table.

Family agreement is separate from category-role performance. Of 23 oracle role assertions, only two category-title assertions are automatically comparable; both return null familyRole and neither agrees. The five class-title roles in NCT04557956 and description-defined components are retained but outside the automatic comparison. Reader, confirmation, and aggregate roles are likewise not automatically adjudicated.

The amended oracle rows embedded in comparisons exactly match the frozen oracle plus its two mechanical patches. Source/oracle/amendment hashes and agreement arithmetic match the summary. No labels, reasons, classifier code, or frozen amendments were changed. Three closely related ORR endpoints belong to the same study; these nine outcomes are not independent clinical validations. This tiny capped convenience snapshot and LLM oracle do not support a population accuracy estimate or independent clinical adjudication claim.
