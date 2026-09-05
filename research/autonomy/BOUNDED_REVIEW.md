---
id: DOC-BOUNDED-REVIEW-DISPATCH
title: Bounded review dispatch
kind: runbook
status: live
date: 2026-09-05
last_verified: 2026-09-05
purpose: Enforce finite review batches while preserving scientific publication requirements.
scope: Review dispatch, frozen evidence reuse and readiness readers.
audience: [maintainers, autonomous research agents]
---

# Bounded review dispatch

`bounded_review.py` reads existing hardening and seat records. The subscription runner,
legacy claim path, continuity report, successor handoff and seat-opening CLI use its decision.
It does not create a second queue or replace `publish_bar.py`.

A new review task supplies `review_request`, for example:

```json
{
  "scope": "baseline",
  "lenses": ["claims-citations", "methods-results"]
}
```

Freeze that JSON before opening seats, then pass it to `seat_scratch.py --open-seat-record
--review-request FILE` with the paper, exact revision and a named lens. The seat record preserves
the request and refuses to change it when closing. The remaining lenses may complete the same
batch; a completed batch cannot expand or repeat through the dispatch interface.
Resuming an open seat preserves its frozen request, document identity and partial notes. Conflicting
values are refused. Completed focused seats enforce the budget even before the hardening summary
has been updated to their revision.

A batched repair uses `scope: focused_verification`, nonempty `changed_claims`, and `depends_on`
repository paths naming the evidence to verify. For another whole-paper review, supply
`scope: full_review` and a `reason` object with `kind: material_error`, `changed_evidence`, or
`external_review`, a concrete `summary`, and `evidence` repository paths. The coordinator verifies
that the cited evidence actually supports the reason. File existence alone is not scientific proof.

An unchanged completed review is reused even with P1 maintenance findings. An unguarded correct
sentence is maintenance; it cannot authorize another full review. A stale legacy `kind: harden`
row without a focused scope or material reason is withheld with an explicit reason. Closed rows
and historical seat findings remain unchanged.

Dispatch permission is not publication readiness. `publish_bar` still checks blocker evidence,
actual independent reviewers, full verification, claim strength, identifiers, endpoints, document
digests and rendering. A focused verification that does not satisfy existing release evidence
requirements must report the precise outstanding clause; do not commission an automatic broader
round merely to chase a green label. Submission authority remains separate.

Readiness notifications compare deliverable bytes and the requested author action. Unrelated
commits do not notify again. Goal tracking checks current committed deliverables unless its
`done_condition.sha` explicitly names a frozen release revision.
