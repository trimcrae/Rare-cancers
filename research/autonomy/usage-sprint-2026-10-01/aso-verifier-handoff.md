---
id: DOC-ASO-VERIFIER-INTEGRITY-SPRINT-2026-10-01
title: ASO verifier integrity sprint handoff
kind: memo
status: live
date: 2026-10-01
last_verified: 2026-10-01
purpose: Preserve the bounded implementation, actual verification scope and next action.
scope: Independent mature-parent verification tooling; no manuscript or publication readiness claim.
audience: [maintainers, autonomous research agents]
---

# ASO verifier integrity sprint handoff

The independent verifier could previously accept a current serialized `DISAGREES` artifact in
`--check` mode. Its mature-parent arm also silently discarded duplicate rows, ignored extra
designs and unverified corpus summaries, and accepted a differing parent as a tie without proving
the recorded parent coordinate. This branch makes those inputs fail verification.

- Branch: `codex/usage-sprint-2026-10-01-aso-verifier`.
- Base revision: `b88d623f6ed72fcc1e873d8416cfa81dcadb4e77`.
- Implementation source revision: `8510e3f17aeeff199e8682cbdc753bcb3a2d9d43`.
  The subsequent handoff commit restores the source's original Git mode `100644`.
- Source: `research/modalities/aso_independent_verification.py`.
- Regression file: `research/modalities/tests/test_aso_independent_verification_integrity.py`;
  26 new cases are defined and were executed successfully in the runtime validation below.

The new checks compare design sets without collapsing duplicates, independently reproduce each
reported parent/start witness, require null witnesses for zero runs, validate row margins and
liability flags, recount all four corpus summaries, and check the stated screen and atlas geometry.
Valid equal-length parent ties remain allowed; released parent summaries follow the validated
recorded witness rather than an arbitrary independent traversal winner. A fresh verification
artifact must also have verdict `AGREES` for `--check` to succeed.

No committed scientific result, manuscript, frozen release package, shared ownership record,
acceptance criterion, publication authority, GPU configuration or compute workload was changed.
The implementation stage made no pull request, merge, publication, outbound message or compute dispatch.
A later bounded CPU validation ran through GitHub Actions as recorded below; no scientific result
or publication artifact was regenerated.

## Actual validation and its limits

A separate read-only reviewer recomputed the mature-parent screen in JavaScript over the six
committed spliced parents: all 190 rows matched their maximal run and recorded coordinates,
with 87 threshold-defined liabilities and 61 attributed to NR4A3. All current summary groups
matched, there were no duplicate keys, and every actual parent tie was below the liability
threshold. The reviewer also compared explicit window scanning with the substring algorithm on
3,000 deterministic synthetic cases, with zero differences.

These are algorithmic JavaScript corroborations, not execution of the Python implementation.
They establish no off-target activity, efficacy, safety or clinical readiness. The regression suite
includes valid ties and deliberate temporary corruption of the real artifacts.

The reviewer read the exact implementation revision and new tests and found no blocking defect.
Their JavaScript recomputation reproduced the existing `D_mature_parent_screen` and `D_ties`
receipt fields exactly. They also verified that the real first-row start-zero corruption and the
synthetic shifted-coordinate regression are invalid witnesses. This was a tooling review, not a
new manuscript review or publication-bar receipt.

The agents used the inherited session model and effort without override. Exact model/effort and subscription usage were not exposed by this execution environment; remaining
capacity stays unknown. The GitHub Actions validation elapsed time is recorded below.

Before the runtime follow-up, Python, pytest and preflight had **not run**: the authoring session
had GitHub connector access and an isolated JavaScript orchestration runtime, with no shell/Python.
GitHub reported zero implementation workflow runs/checks at 2026-10-01 22:33 UTC. The existing
`tests.yml` runs on main pushes and pull requests; this work branch required a scoped workflow.

## Actual Python runtime validation — 2026-10-01

- Tested revision: `c40477e2e2260a2429a0b118446d01ad645d9ea3`, which adds only
  `.github/workflows/usage-sprint-aso-verifier.yml` to the implementation/handoff revision
  `b7c47f7afe424401a621f68b1b12afc37f4721a8`.
- [GitHub Actions run 36936291537, attempt 1](https://github.com/trimcrae/Rare-cancers/actions/runs/36936291537),
  job `110617223111`, ended with overall conclusion **failure** because normal preflight failed.
- Runner: Ubuntu 24.04.5, Python 3.11.16, pytest 9.1.1. Job elapsed time: 283 seconds
  (22:38:43–22:43:26 UTC). The CPU job is capped at 20 minutes; preflight at 10 minutes.
- The original decoded full job log, including bootstrap, all advisories, commands and the
  nonzero preflight exit, is preserved at [aso-verifier-ci-job-110617223111.log](aso-verifier-ci-job-110617223111.log).
- A separate reviewer read the exact workflow and source/test blobs and found no blocking concern.
  The reviewed source blob `719ccfb4b3b86f35362e419570fcf717f47faea3` and integrity-test blob
  `f402ff465fd3ab5f1ac86d4fbd407d3aba66ef62` match the implementation content reviewed earlier.
  Both Git modes remain `100644`.

| Executed check | Actual result | Scope |
|---|---|---|
| `python3 -m pytest research/modalities/tests/test_aso_independent_verification.py research/modalities/tests/test_aso_independent_verification_integrity.py -q --durations=10` | Exit 0; **37 passed in 6.21s**, zero skips/failures | 11 existing cases plus all 26 new integrity cases |
| `python3 research/modalities/aso_independent_verification.py --check` | Exit 0; `independent-verification artifact is current` | Exact committed verifier artifact reproduced; verdict must be AGREES |
| `./scripts/preflight.sh` | **Exit 1**; `PREFLIGHT FAILED -- do not commit.` | Default fast gates only; broader test suites were not requested |
| `git status --short` and `git diff --exit-code` | Empty status, exit 0 | Validation preserved every tracked input |

The sole failing preflight item was `aso_archive_manifest.py --check-archive`:
`STALE: the archive inventory would change — re-run without --check`. Every other fast gate
and the other 17 generated-artifact checks passed. The environment bootstrap succeeded, including
its normal Ghostscript and LibreOffice Writer installation; every probed Python dependency imported.
This is not a missing-dependency failure. Citation/retraction and readability advisories remain in
the full log and are not claims of publication readiness.

At least one inventory mismatch is caused by this implementation: the unchanged manifest lists
`research/modalities/aso_independent_verification.py` as 24,400 bytes with SHA-256
`739c609707c6adf30dc886eb547b447efdf68b1b78ebb4300100953046f383c6`, while the tested source is
27,772 bytes. The manifest generator explicitly inventories that source. The new integrity test
is not in its current explicit crosscheck promise patterns. A separate reader confirmed that the manifest blob is unchanged from base `b88d623` and
that the base source is also 24,400 bytes, establishing that this source-entry drift was introduced
by the repair. Full baseline preflight was not executed, so this receipt does not claim that every
archive mismatch is new or that all baseline gates were green. The manifest and frozen scientific package remain unchanged under this task's bounded scope.

The workflow triggers only on this exact work branch and only for its own file, verifier or two
targeted test files. It uses `contents: read`, `persist-credentials: false`, no project secrets,
no GPU/fleet dispatch and no commit/publication step. Receipt-only changes do not rerun it. There
is no live scheduler or pending CI job from this task. No pull request, merge or publication was made.

## Next bounded action

The verifier repair now has actual Python regression and artifact-reproduction evidence. It remains
a draft checkpoint with a **red normal preflight**, not a green integration gate or publication
candidate. The coordinator should route a separate packaging coherence task against the intended clean
integration source, while preserving frozen release artifacts. The generator's current
`reimplementation_crosscheck` promise explicitly names the original test only; adding the new
integrity regression file to that promise is a packaging decision for that task.

The exact metadata-refresh command is `python3 research/manuscripts/aso_archive_manifest.py`,
followed by `python3 research/manuscripts/aso_archive_manifest.py --check-archive` and normal
preflight against the settled revision. Inspection of the generator confirms that regeneration
reads/hashes the tracked inventory and writes only
`research/manuscripts/aso/fusion-junction-aso-archive-manifest.json`. It does not rebuild a ZIP,
PDF/DOCX, scientific result or deposition, and it makes no network call. This live JSON inventory
refresh is what addresses the repository gate. Distributing the changed code would additionally
require a separately reviewed payload ZIP built from the refreshed `files` list; it must not
silently overwrite an existing frozen/deposited bundle. Do not weaken the manifest gate or regenerate a frozen scientific result merely
to make a check pass. Recheck main and outstanding ownership before integration; do not open a pull
request unless asked and do not launch GPU runs or retry a GPU-ban-rejected workflow.

After actual validation, a separate bounded task may audit the frame arm's graded-pair set and
`grade_counts` consistency: those fields were not hardened by this mature-parent repair. Require
an independently demonstrated failure mode and keep manuscript review bounded.
