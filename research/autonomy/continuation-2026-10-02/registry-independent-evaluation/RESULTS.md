---
id: DOC-CHECKPOINT05-REGISTRY-COMPLETED-RESULT
title: "Source-separated response-context evaluation"
kind: memo
status: live
date: "2026-10-02"
last_verified: "2026-10-02"
purpose: "Record the bounded checkpoint result and its evidence."
audience: [maintainers, autonomous research agents]
scope: "Named public sources and exact computations; no publication clearance."
---

The source-separated snapshot contains 10 trials and all 68 outcome records, captured once using the frozen amendment to ResultsFirstPostDate:asc. Date ties follow server snapshot order; the ten-record cap truncates the eligible source population. No NCT identifier overlaps the previously used corpus. This is a small post-development, date-defined evaluation slice, not a random sample or estimate of clinical extraction accuracy.

A separate LLM reviewer screened all 68 outcomes before predictions: nine response outcomes across six trials were eligible and 59 were excluded with reasons. The frozen oracle assigned six RECIST 1.1, one Lugano 2014 and one iwCLL 2018 outcome; one cystoscopy/cytology-based outcome remained unknown. The oracle is source-bound annotation, not independent clinical adjudication. The original oracle remains unchanged; pre-prediction amendments repair one literal offset and mark two genuinely absent optional source fields explicitly. The first cloud attempt failed before classification while dereferencing an absent field. Initial code, failure logs and amendments are preserved.

[Repaired execution passed](https://github.com/trimcrae/Rare-cancers/actions/runs/37044191718) at 05bf6349b389349e17b86835615237fc6ef371ec after five synthetic wrapper tests. The classifier itself remains pinned to 52a9fd8b8bf119d30912dca308baa0cc5541df69. The wrapper reports retention of 68 outcomes and 460 class/group rows; the eligible outcomes produced 45 companion rows. The complete output, input bytes and exact execution receipts are preserved in results/full-execution.zip, whose digest is independently verified in results/artifact-receipt.json.

Only two of nine eligible outcomes jointly agreed on status, family, version and modifier: one RECIST 1.1 disease-control outcome and the appropriately unknown cystoscopy/cytology outcome. The other seven predictions abstained: five ambiguous and two unknown. None assigned a wrong family in this slice. All five ambiguous outputs include the ordinary lower-case pronoun “who” as WHO alongside an explicit RECIST or Lugano mention. One unknown output omits explicit iwCLL 2018; the other omits a spelled-out RECIST 1.1 definition. Some parenthesized or intervening-word version syntax also lacks a captured version. These are observed coverage/context defects, not evidence of clinical harm or a population error rate.

Category-role comparison is narrower than family comparison. Only two whole category-title annotations were automatically comparable; both received null family roles under an unknown family. Five class-title annotations and description/aggregate definitions were retained but outside that automatic comparison. Consequently this run does not establish successful CR/PR/SD/PD category mapping on new studies. An abstention can preserve uncertainty while still limiting practical coverage.

The failed and successful runs are retained without tuning the classifier on these cases. Next work may isolate pronoun/acronym context, spelled-out family and version grammar, and class-versus-category role coverage in a changed implementation with independent synthetic checks. Replaying this now-seen snapshot would be regression testing, not a fresh independent validation. A subsequent generalization claim needs another prospectively frozen source slice and blind oracle. Preserve the original 575-unit conformance evidence; it is not contradicted by having weaker coverage in these new contexts.

[Independent result review](review/result-review.json) verified all 442 source container hashes, 1,084 coordinate hashes and coverage of all 421 measurements, plus the preserved oracle and comparison arithmetic. The reviewer inspected summary/comparison/fidelity files, not the exported accepted-row payloads. Those full exports are present in the complete execution ZIP; independent row-by-row export verification was not performed. Nine-outcome modifier agreement is all-null and does not test modifier recognition. Three similar ORR outcomes belong to one trial, so the nine outcomes are not independent clinical validations.
