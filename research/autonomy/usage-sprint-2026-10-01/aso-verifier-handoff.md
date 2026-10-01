---
id: DOC-ASO-VERIFIER-INTEGRITY-SPRINT-2026-10-01
title: ASO verifier integrity sprint handoff
kind: memo
status: live
date: 2026-10-01
last_verified: 2026-10-01
purpose: Preserve the bounded implementation, actual verification scope and next action.
scope: Independent mature-parent verification tooling and live archive metadata; no manuscript or publication readiness claim.
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
A later bounded CPU validation ran through GitHub Actions as recorded below; no scientific result,
frozen release artifact or manuscript was regenerated.

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
archive mismatch is new or that all baseline gates were green. At that first validation checkpoint, the manifest and frozen scientific package were preserved;
the subsequently authorized live metadata repair is recorded below.

The workflow triggers only on this exact work branch. Its settled path filter covers its own
file, the verifier and two targeted test files, plus the live archive generator and manifest. It uses `contents: read`, `persist-credentials: false`, no project secrets,
no GPU/fleet dispatch and no commit/publication step. Receipt-only changes do not rerun it. There
is no live scheduler or pending CI job from this task. No pull request, merge or publication was made.

## Live archive packaging coherence — actual runtime receipt

The coordinator subsequently authorized a separate live metadata repair. The archive generator's
`reimplementation_crosscheck` promise now includes the new integrity test. Its actual Python
output was generated from clean source checkpoint `cf5fec7189e1031bf4bcefc13a4c2c6b704792e6`
in [preview run 36937661787](https://github.com/trimcrae/Rare-cancers/actions/runs/36937661787).
Generation, strict `--check` and tracked-input restoration all passed. The recovered bytes were
committed exactly: 385,999 bytes, Git blob `52003a887cf634b6af9739bc111c80100616db40`, SHA-256
`af95942f696302b975bfd88f44bef4d0509d62b9759d1f7a79d352826d72e83d`.

The inventory grows from 520 to 521 files. It adds only the integrity regression file and updates
only the existing verifier and archive-generator file entries. Every other inventory entry,
scientific/frozen-file hash, recorded gap and DOI is unchanged. The crosscheck promise covers four
files: verifier source, unchanged verification JSON, existing tests and the new integrity tests.
A separate reader verified this exact scope against settled packaging revision `943acf4578df9e23617d9464cb9e2cf126f26434`.

[Run 36937939668](https://github.com/trimcrae/Rare-cancers/actions/runs/36937939668) then passed
37 tests and both verifier/archive checks, but default preflight exited 1 because the downstream
operational deposit-drift declaration still described the old inventory. This was a real dependent
metadata failure. The coordinator extended the bounded scope to its generated block alone.

The actual `aso_deposit_drift.py` output was obtained in
[preview run 36938925751](https://github.com/trimcrae/Rare-cancers/actions/runs/36938925751)
from source checkpoint `39f6e75a6c2da52caf379dcc1e2420f9e10c3170`. Generator, `--check`,
byte-identical surrounding-text assertions and tracked-input restoration passed. The exact output
checklist is Git blob `34c1be544f69e6e5d239fea8120cce307d8c5643`, SHA-256
`10234b4c3861b8012d1a96651f1b47604a88fd089e72c611ef241acfab5553ae`.
Only the generated block changed: 36 paths differ from the published record at `4fd4698daec0`
(30 changed, 6 added, 0 removed), adding the changed verifier and new integrity-test rows to the
previous declaration. Every surrounding checklist line is unchanged. The checklist and its producer
are outside the archive inventory, so this correction does not change the live manifest again.
The producer names no other generated output.
A separate reader recomputed the drift from the published 515-file manifest and live 521-file
manifest, matched every generated path in order, verified the original surrounding text and exact
preview/committed block bytes, and found no blocking issue at the final settled revision.

### Final settled validation

Tested revision: `a88d6916b09ea72f4a13e5e389252aa5ecb18d06`.
[GitHub Actions run 36939159934](https://github.com/trimcrae/Rare-cancers/actions/runs/36939159934),
job `110626365220`, concluded **success**. Job elapsed time: 175 seconds
(23:08:40–23:11:35 UTC), using Python 3.11.16 and pytest 9.1.1.
The full original job log is preserved at
[aso-verifier-ci-job-110626365220.log](aso-verifier-ci-job-110626365220.log).

| Executed check | Actual result |
|---|---|
| Two verifier test files | Exit 0; **37 passed in 5.03s**, zero skips/failures |
| Two existing operational drift guards | Exit 0; **2 passed in 2.18s**, zero skips/failures |
| Verifier `--check` | Exit 0; committed verification artifact current |
| Archive `--check-archive` | Exit 0; committed live inventory current |
| Operational drift `--check` | Exit 0; generated declaration current |
| Normal `./scripts/preflight.sh` | Exit 0; `PREFLIGHT OK (fast gates only (doc + artifact linters))` |
| Tracked status/diff | Empty status, exit 0; `PINNED_SHA=a88d6916b09ea72f4a13e5e389252aa5ecb18d06` |

All 18 generated-artifact checks and the other default fast gates passed. Broader manuscript,
modality and governance suites were not requested; this is not `PREFLIGHT_FULL=1` publication
verification. Original advisories remain in the full log. No acceptance rule was weakened.
Temporary metadata-preview workflows were removed; the remaining branch workflow has read-only
permissions, no persisted Git credentials, finite CPU timeouts and no commit/publication step.
No manuscript, frozen/deposited ZIP/PDF/DOCX, scientific output, shared queue, publication authority
or GPU guard was changed. No deposit/upload, publication, pull request or main merge occurred.

## Next bounded action

The original source-entry mismatch is addressed by the live metadata repair recorded above.
The coordinator should recheck main and outstanding ownership before integration. Preserve the
frozen/deposited bundle and its scientific assets; do not open a pull request unless asked. A new
release/distribution would require its own payload review and publication checks. This bounded
code/packaging validation is not full publication evidence and does not authorize a GPU run.

After actual validation, a separate bounded task may audit the frame arm's graded-pair set and
`grade_counts` consistency: those fields were not hardened by this mature-parent repair. Require
an independently demonstrated failure mode and keep manuscript review bounded.
