---
name: paper-hardening
description: Review a research manuscript or verify a repair against its evidence, with a finite scope and a concrete submission decision.
---

# Paper review

Follow `research/autonomy/OPERATING_PROTOCOL.md`, especially "Review with an endpoint".
Every paper needs a documented independent ultra-reasoning pass before submission, as directed
by the user on 2026-09-05. Include it in the existing bounded review batch. Record actual model,
effort, frozen inputs, findings and disposition; never infer ultra effort from a review label.
The coordinator checks this requirement before readiness or submission handoff. Reuse matching
ultra evidence; focused repair verification does not automatically restart full-paper review.
Read the outgoing artifacts, existing reviews, and actual publish-bar requirements. Reuse a
completed review when the deliverable digest matches; do not restart because unrelated main
commits moved. An already-reviewed manuscript does not need another baseline round.

Budget one independent review batch, one batched repair, and a focused independent verification
of changed claims and dependencies. Further full review needs a named material reason. If existing
publication evidence requirements remain unsatisfied, report that fact rather than claiming ready.

Findings distinguish current submission blockers, maintenance gaps, and optional editorial changes.
Every finding names the exact outgoing claim, source, consequence, and minimum repair. A correct
sentence without a guard is maintenance. Zero findings is a valid result. Verify objections against
the evidence before editing. Keep limitations; replace wrong text without adding defensive padding.

Do not repeatedly mutate the paper while another agent reviews it. Pin the review inputs. Existing
blind-seat and hardening records remain the publication evidence format; do not fabricate or
silently alter past reviews. `record_bar_evidence.py` records them and `publish_bar.py` decides
whether all required evidence and authority hold. A review's iteration budget is not permission to
post an unresolved paper.

The [legacy reference](references/legacy-2026-09-04.md) preserves incident evidence and specialized
procedures. Read only the relevant passage when investigating an actual regression. Its repeated
whole-paper rounds, automatic guard expansion, and retired stopping rules are superseded.
