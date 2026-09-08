# Retention gap — E1n narrowing check logs, recorded honestly rather than recreated

**Asked:** retain the already-produced E1n check logs from `/tmp/claude-0/e1n-retained/` before
cleanup **if still present**; if unavailable, record the exact gap; re-run nothing to recreate them.

**Measured 2026-09-08 09:04 UTC:** `ls /tmp/claude-0/e1n-retained` →
`No such file or directory`. **The directory is gone.**

## Why, stated plainly

**I deleted it myself**, at ~09:00 UTC, in the cleanup step of the previous turn
(`rm -rf /tmp/claude-0/f1-retained /tmp/claude-0/e1n-retained /tmp/claude-0/repurposing-PRE-NARROWING.md`),
immediately after verifying the F1 and E1 in-repo manifests. That deletion was **premature for the
E1n set**: unlike `f1-retained`, whose contents I had already copied into
`F1-executed-artifacts/`, the E1n logs had **not** been copied into the repository first. The E1
narrowing commit `a9ff3c67` retained the *qualification record* and the manuscript bytes, but not the
raw linter stdout/stderr files.

## What is lost, and what is not

**Lost — the original bytes:** `BEFORE.md`, `AFTER.md`, `GIT-HEAD-BASELINE.md`, `narrowing.diff`, and
`lint_consistency/lint_style/lint_claims/lint_submission_residue/lint_asymmetry/submission_metrics`
`.out` and `.err` for the narrowing pass. **No hashes were computed for that set before deletion**, so
no hash record of it exists either. That is the exact gap.

**Not lost — the recorded outcomes.** `QUALIFICATION-E1-acceptance-3-overclaim.md` (committed at
`a9ff3c67`) carries the measured results of that same pass: five linters exit 0; `lint_consistency`
exit 1 with its single ERROR attributed to `mtap-prmt5/emc-mtap-prmt5-hypothesis.md:673` and naming
`repurposing` 0 times; word count 5,724 → 5,769 of 8,000; `submission_metrics` exit 0 with 0 limits
exceeded; hedge greps. The manuscript's pre- and post-narrowing bytes are both recoverable from git
(`d5d3ea2d` and `a9ff3c67`) — but a git-derived copy is **not** the original retained artifact and is
not being presented as one.

**Nothing has been re-run to reconstruct any of it**, and original E1 is not reopened. The E1 and F1
retained sets are untouched and still verify (13/13 and 40/40).

## Standing

Recorded as an **unrecovered retention gap**, not a closed item. The procedural lesson, for this
campaign's remaining children: **copy a retained set into the repository and hash it before any
`rm -rf`** — verifying the *other* sets' manifests is not verification of the one being deleted.
