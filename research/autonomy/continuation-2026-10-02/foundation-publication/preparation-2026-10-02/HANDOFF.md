---
id: DOC-FOUNDATION-PREP-HANDOFF
title: Foundation correspondence preparation handoff
kind: memo
status: live
audience: [maintainers, external reviewers]
date: 2026-10-02
last_verified: 2026-10-02
purpose: Record the prepared correspondence, verification and publication boundary.
scope: Task-specific Foundation source-identity correspondence preparation and handoff.
---

# Foundation correspondence preparation

Preparation target: Human Genetics, Correspondence, subscription route with no APC.
The contribution remains a correction of source identifiers in one pinned derivative export.
Editorial acceptance and submission clearance are not established.

The original manuscript, three-page PDF, scientific data and reviews remain unchanged at
`5d2f2e2116f43c0bb56a46120902a1332f27720b`. New material is confined to this preparation
directory and task-specific validation workflows. The continuation branch, campaign state,
daily watch, paused sprint and methylation branch are not written by this task.

## Files

- `human-genetics-correspondence.docx`: editable venue copy; Markdown source and build script retained.
- `online-resource-1.pdf`: text supplement generated from its Markdown and Word sources after render verification.
- `cover-letter.txt`: unsent draft, including prior public manuscript disclosure and data-licence separation.
- `reproducibility.zip`: compact offline package preserving the original archived inputs, recovery/check scripts, saved results, exact HGNC responses and separate licence notices.
- `venue-and-licensing.json`: official source URLs, preparation decision and remaining limits.
- `readiness-and-gates.json`: scientific evidence, actual legacy FULL requirement, protocol drift and author requirements.
- `base-audit.json`: byte verification, archive inventory, branch/ownership check and preservation record.

## Review and verification

Original scientific/editorial reviews and three-page visual QA remain valid for their exact hashes.
The venue copy has a 169-word abstract, author-year references, expanded HGNC name, source-attributed table
caption and explicit event-order limitation. It has not acquired a new scientific result.
Focused initial review, repair verification and final URL/transport review passed (`review/focused-final.json`, `review/transport-final.json`). All six new rendered pages were inspected; complete text and all Markdown links matched (`validation/render-final/qa.json`). The four-page journal render is QA only; the two-page supplement PDF is an outgoing file. Normal/default preflight passed in run 37079377220 at `2345c92cc25c175ccc8665d240dac11a780523cd` (exit 0); the initial metadata failure and cancelled duplicate remain preserved.
The original independent primary extraction from run 37035103326 is reused, not repeated.

The package integrity verifier checked 15 packaged files, four primary archive members and 14 HGNC
members. A changed annotation payload was rejected in a negative control; no scientific rerun occurred.
The integrity verifier is not an independent reanalysis of the primary workbook.

## Publication boundary

FULL run 37058750900 timed out with exit 124 after approximately one hour. Its original files remain
in `../full-initial/`. No passing FULL receipt exists and no automatic retry is authorized.
The actual enforcer requires unscoped FULL evidence against the candidate revision; a default or
paper-specific check cannot replace it. No gate was weakened, result relabeled or submission made.

Human Genetics does not prescribe licences for external repository data in its guidelines. The ODbL database remains
outside the proposed publisher-exclusive article licence. Primary-source attribution/CC BY exceptions,
HGNC CC0 and original Apache 2.0 code terms are retained. This resolves the documented venue-policy
mismatch for preparation, not all possible third-party rights or the future agreement itself.

The current remote operating protocol at `3294988f2e60db009ff8045e1e16e655b6403c3b` matches the
continuation revision and requires a hash-bound independent LLM editorial review. That requirement is
covered by the focused review and render bindings here. The older local checkout contains different
ultra wording; it is recorded as protocol drift, not an extra gate for this continuation. Existing and
new review configuration is reported without inventing unavailable backend serving telemetry. The
FULL enforcer is unchanged. Future publication must bind its actual outgoing files and candidate revision.

Author items remain city/country, final approval, current exclusive-submission/publication status, and
applicable ethics/consent declarations. Funding and competing interests reuse standing declarations.
No author approval, ethics exemption, public deposit DOI or publisher acceptance is invented.

## Execution and ownership

Root is the sole writer to `codex/foundation-correspondence-prep-2026-10-02`.
Workers perform finite read-only venue/gate/focused-review tasks. No shared campaign state is changed.
Local free space was 8.36GiB, so no local checkout/runtime was created. Small scoped files and Git/API
objects are used; remote render/normal jobs have their own storage guards leaving 10GiB free.
Daily 06:00â€“10:00 America/New_York restriction applies to every worker and rendering job.
The September 12 early release has expired. No UI or browser automation is required for this task.

The reproduction ZIP and its README are frozen at `d187c779f9f528a657048a13e849fe8d4834c666`;
the final Word sources were rendered at `ffb048d079cd8bf8f18bac4040dbdcb5f1d71709` in
run `37078989634`. The ZIP SHA-256 is
`01d7a8ea7d92ae1a6d1c79d33c7b89d8b31a68453f9b82ad095de3234b53b98f`.
The settled package revision is `2345c92cc25c175ccc8665d240dac11a780523cd`. Its immediate child commit seals the receipts and handoff only; all outgoing bytes are identical. `closure.json` binds that candidate, file manifest, normal receipt and completed-job status. The exact seal commit is reported in the task and its local `final-revision.json` receipt.
No merge to main or cleanup of any existing checkout was performed; this branch remains the owned handoff.

## Rendering-tool licence remediation

A bundled OpenAI rendering helper was mistakenly copied into six task-created commits. Its licence
prohibits redistribution. It and its copied notices were removed from all six commits on this task
branch; the verified continuation base, paper, input archives and failed receipts were preserved.
`review/renderer-distribution-remediation.json` records the exact old-to-clean revision mapping.
An independent reviewer verified that each rewritten tree differs only by the three removed helper
paths. Future rendering uses independently written standard LibreOffice/Poppler commands.
The revised links point to the clean archive revision and were independently fetched and verified.

Removal from reachable branch history does not certify deletion from GitHub unreferenced objects,
caches or historical runner storage. Any required provider-side expungement remains unresolved;
no support outreach was authorized or performed. The current outgoing files and data package do not
contain the restricted helper. The history rewrite triggered an old render that failed for the
removed helper and a redundant default check that was cancelled; both are preserved in validation
and neither is represented as passing. No FULL/modalities retry occurred.

## Final state

Scientific claims remain restricted to the pinned derivative export. Paper-specific evidence, focused
review, package integrity, all-page render/text/link verification and the default preflight passed.
Submission readiness remains false: no passing exact-revision FULL receipt exists; author details,
final approval and the actual publishing agreement remain outstanding. No manuscript was submitted
and no preprint or outreach was sent. All task jobs and finite reviewers have finished; neither the
paused sprint nor the daily watch was changed.

Three original render ZIPs were integrity-verified against every extracted file and page-image hash.
Automatic approval review blocked deletion of their disposable extractions with only “blocked by
policy” as its reason. The extractions and verified original ZIPs were retained; no deletion workaround
was attempted. No local checkout/runtime or unrelated filesystem content was removed.

## Main integration checkpoint

The Foundation-only candidate `3b5759ecc2ae86fb80df6b10d9106e75d2151ac9` passed normal/default preflight in run 37083509274. The current reader PDF preserves the exact inspected four-page render. The final integration commit adds only this handoff and validation receipts after that check. Full/modalities CI was intentionally not rerun; no submission clearance is claimed. The complete preparation branch and original evidence remain preserved.
