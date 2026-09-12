---
id: DOC-INDEPENDENT-LLM-READABILITY-REVIEW
title: Independent LLM readability review
kind: runbook
status: live
date: 2026-09-12
last_verified: 2026-09-12
purpose: Require an actual independent reader judgment before publication.
scope: Editorial evidence, complete prose coverage and exact artifact binding.
audience: [maintainers, autonomous research agents]
---

# Independent LLM readability review

The author's September 12, 2026 instruction requires an LLM pass. Sentence
metrics and page legibility cannot approve prose. The publication readability
clause requires a committed independent LLM review as well as its existing
sentence and caution safeguards.

The writer applies `.claude/skills/scientific-writing/SKILL.md`. A separate LLM
reader reads the proposed manuscript and reader-facing supplementary text. The
abstract should make sense to an interested nonspecialist; the remainder should
be followable by a working scientist unfamiliar with this project. Explain
necessary terms before relying on them. Preserve exact methods, numbers,
negative findings, uncertainty and limits on interpretation.

The reviewer explains the question, what was compared or merely proposed, the
main finding, the strongest limitation or contrary result, and the justified
next step. Identify confusing passages and the smallest repairs. Check revised
claims against the original. Resolve findings in one batch and verify those
repairs once; unchanged science does not need another whole scientific review.
Preserve the actual response and execution provenance. Never fill a receipt for
a review that did not happen.

## Evidence contract

The separately governed `research/autonomy/editorial-prose-inventory.json` lists
all required outgoing prose sources for each paper. Its schema is
`emc-editorial-prose-inventory/1`, with a `papers` mapping from paper ID to a list
of repository-relative source paths. The reviewer cannot omit a supplement by
leaving it out of their receipt. Reconcile this inventory with the actual release
package and registered manuscript before promotion. Unknown papers fail closed.
New editorial proposals are not an approval of older registered/exported bytes.
After export, compare the outgoing text with the reviewed source and inspect the
rendered files; any substantive difference requires a focused LLM review of it.

Commit `PUB-ID.json` in this directory alongside the candidate, with:

- `schema`: `emc-llm-readability-review/1`; matching `paper_id`.
- `review_kind`: `independent_llm_editorial`; timezone-aware ISO `reviewed_at`.
- `reviewer`: `agent_id`, `model`, `execution_evidence`. Describe the actually
  observable model; a configured/inherited model is not served-model attestation.
- `writer_ids`: all prose writers, excluding the independent reviewer.
- `decision`: `pass`; `unresolved_blockers`: empty only after actual resolution.
- `reader_explanation`: substantive `question`, `approach`, `main_finding`,
  `main_limitations`, and `next_step` answers from the reviewer.
- `checks`: true actual findings for `reader_facing_text_reviewed`,
  `abstract_understandable`, `terms_explained`, `narrative_followable`,
  `scientific_meaning_preserved`, and `limitations_preserved`.
- `report`: repository-relative `path` and exact `sha256` of the retained report.
- `artifacts`: every outgoing prose source including the registered manuscript
  and applicable supplement; each supplies repository-relative `path`, exact
  `sha256`, and `sections_reviewed`. Explain immutable archival/protocol material
  retained verbatim and its reader-facing context in the report.

The checker reads receipt, report and artifacts at the candidate revision.
Missing evidence, self-review, unresolved blockers or changed prose/report fails.
Unrelated commits can reuse the review when artifact bytes are unchanged.

This verifies recorded LLM judgment; it cannot automatically establish clarity
or scientific validity. A superficial receipt is still a review failure. The
coordinator must read the report. Other publication checks, rendered-artifact
inspection, venue requirements and author approval remain necessary. Preserve
historical publication records; do not manufacture retrospective signoffs.
