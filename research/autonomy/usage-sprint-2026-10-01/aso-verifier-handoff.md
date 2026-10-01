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
  26 cases are defined, not reported as executed.

The new checks compare design sets without collapsing duplicates, independently reproduce each
reported parent/start witness, require null witnesses for zero runs, validate row margins and
liability flags, recount all four corpus summaries, and check the stated screen and atlas geometry.
Valid equal-length parent ties remain allowed; released parent summaries follow the validated
recorded witness rather than an arbitrary independent traversal winner. A fresh verification
artifact must also have verdict `AGREES` for `--check` to succeed.

No committed scientific result, manuscript, frozen release package, shared ownership record,
acceptance criterion, publication authority, GPU configuration or compute workload was changed.
No pull request, merge, publication, outbound message or compute dispatch was made.

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

The agents used the inherited session model and effort without override. Exact model/effort,
elapsed runtime and subscription usage were not exposed by this execution environment; remaining
capacity stays unknown.

Python, pytest and the repository preflight were **not run**: this session had GitHub connector
access and an isolated JavaScript orchestration runtime, with no shell/Python execution
environment. GitHub reported zero workflow runs and status checks for the implementation commit
when checked at 2026-10-01 22:33 UTC. The existing tests workflow runs on main pushes and pull
requests, so pushing this work branch does not by itself execute it.

## Next bounded action

Use an isolated worktree at this branch and execute these commands with the repository's supported
Python environment:

```bash
python3 -m pytest research/modalities/tests/test_aso_independent_verification.py research/modalities/tests/test_aso_independent_verification_integrity.py
python3 research/modalities/aso_independent_verification.py --check
./scripts/preflight.sh
```

Preserve the exact revision, exit codes, full logs and preflight's actual scope. Stop and repair any
failure in one batch. Confirm the unchanged verifier artifact is still reproduced; do not regenerate
a frozen scientific artifact merely to make a check pass. Recheck main for conflicting writers
before proposing integration. This branch is a draft checkpoint, not a green gate or publication
candidate. Do not launch GPU runs or retry a deliberately GPU-ban-rejected workflow.

After actual validation, a separate bounded task may audit the frame arm's graded-pair set and
`grade_counts` consistency: those fields were not hardened by this mature-parent repair. Require
an independently demonstrated failure mode and keep manuscript review bounded.
