---
id: DOC-CHECKPOINT06-REGISTRY-V2-FINDINGS
title: Bounded family context repair
kind: memo
status: live
date: "2026-10-02"
audience: [maintainers, external reviewers]
purpose: "Record the bounded repair, source-preservation contracts and actual tests."
last_verified: "2026-10-02"
scope: Synthetic contracts for a separate v2 implementation; no clinical validation.
---

The separate companion_v2.py repairs three lexical/context mechanisms: ordinary who pronouns no longer imply WHO criteria; explicit full RECIST names and iwCLL are recognized; versions may follow parentheses and a fixed criteria phrase. WHO requires its uppercase acronym or full organization name plus an adjoining criteria phrase. Lowercase organization acronyms and broader paraphrases can still abstain. Historical assessment wording causes conservative abstention. Conflicting families, versions, negation and modifiers retain conservative handling.

The scope and synthetic tests were frozen before implementation. The initial 20-test suite passed, but independent review then demonstrated an introduced history-context regression: current assessment in previously treated patients or against historical controls incorrectly abstained. Paired synthetic expectations were frozen before repair; five subcases failed on the initial code. One bounded correction now requires history words to modify an assessment or study-use phrase. All 22 tests then passed, including retained historical-assessment abstention. The initial code, 20-test receipt, scope and review remain preserved byte-for-byte in initial evidence files; history-repair-receipt.json binds the changed code and before/after logs. The initial Python Store alias failure also remains recorded.

Accepted v1 is unchanged. The earlier independent result remains 2/9 joint agreement; no frozen trial corpus was executed by this worker. Any coordinator replay of those cases is seen-case regression only. This is a limited grammar, not clinical criteria implementation, and no extraction accuracy or generalization claim follows from these synthetic tests.

Class-title and aggregate-description roles remain outside the category-title mapper. The earlier category-role coverage gap is not repaired. Literal input rows, denominators, measurement payloads and copied outcome context retain the v1 preservation path. New tests verify exact equality, and pre-existing tests retain confirmation-state and numeric-cell safeguards.

Run synthetic checks with `python -Xutf8 -B -m unittest -v test_companion_v2 test_v1_contract_on_v2 test_historical_repair` from this directory. The public functions remain `classify_context(outcome)` and `accompany(unit, source_row, outcome, coordinates)`; the coordinator can import companion_v2 for its cloud wrapper. The inherited standalone CLI still expects the original accepted575 ZIP, manifest and reviewed27 files; it is not a CLI for the nine-case source slice.

Next: integrate these exact hashes and perform one cloud seen-case regression. A future generalization test requires a separately frozen source slice and blind oracle.
