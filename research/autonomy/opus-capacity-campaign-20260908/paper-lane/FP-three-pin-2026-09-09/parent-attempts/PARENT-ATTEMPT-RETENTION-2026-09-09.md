---
id: DOC-OPUS-CAMPAIGN-FP-THREE-PIN-PARENT-ATTEMPTS-20260909
title: "FP three-pin — the PARENT's own verification attempts, retained separately"
level: L4
kind: record
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# The parent's own attempts, kept distinct from the author's

Root asked that the separately reported PARENT lint, negative-fixture and preflight attempts be
retained if still available, **kept distinct from the author's attempts**, and **never reconstructed
or rerun to recreate evidence**. Nothing here was rerun for this record.

These are the attempts reported in commit `91798e2e8afcabce725924fff684c08395699dca`. They are the
parent's own re-derivation before committing the author's change — they are NOT the author's two
lint executions and NOT the author's C0–C7 / C8–C9 fixture passes, which live in
`../VALIDATION-2026-09-09.md` and remain author-reported.

## Retained here

| file | bytes | sha256 | what it is |
|---|---:|---|---|
| `parent-lint_consistency.stdout.txt` | 51 | `1c7d66cd81731b27…` | the parent's `lint_consistency.py` run; the single line `lint_consistency: 0 ERROR across 29 target file(s)` |
| `parent-lint_consistency.stderr.EMPTY.txt` | 0 | `e3b0c44298fc1c14…` | that run's stderr, genuinely empty; the sha256 shown is the sha256 of the empty string. Retained empty and renamed away from a `.json` suffix rather than padded with content it never had |
| `parent-preflight-run1.combined.txt` | 534,225 | `8e4ce0f1ce575b28…` | the full combined stream of the parent's `scripts/preflight.sh` run, the one whose exit code the commit reported as **1** |

## Never retained as streams, and stated as unavailable

* **The parent's negative-fixture run has no retained stream and no retained harness file.** It was
  executed as an inline heredoc against `lint_consistency.check_artifact_figures` on
  `TemporaryDirectory` copies; no script was written to disk and no stdout capture was redirected to
  a file. Its results — five perturbations firing `A-figure-mismatch` with exactly one captured
  number each, and the neighbouring local-recurrence row's identical `1/16 = 6.2 %` correctly **not**
  firing — survive only as the text of commit `91798e2e8`. That text is a contemporaneous report,
  not a retained execution stream, and is not offered as one.
* ⚠ **Five, not six.** The parent ran five rejection fixtures (artifact 42.9→41.9, artifact 6.2→7.2,
  artifact p→0.0772, manuscript 42.9→41.9, manuscript p→0.0772) plus one no-fire specificity check.
  The manuscript-side `6.2 → 7.2` perturbation was not among them. The count is five rejections and
  is not expanded to six.
* **No exit code was captured for the parent's lint run as a file.** The commit reports exit 0 and
  the retained stdout is consistent with it, but the exit integer itself was read from the shell at
  the time and not written to a sidecar. It is reported as parent-reported, not as a retained code.
* The `parent-preflight-run1.combined.txt` stream merges stdout and stderr, so the two cannot be
  separated after the fact. Its exit code was likewise read from the shell and not written to a
  sidecar.

## One characterisation of mine that root did not independently establish

Commit `91798e2e8` described the preflight result as the "unchanged inherited failure set". Root
records that this characterisation is not independently established there. It is a parent
measurement — the error count and its attribution by diff — not a root-confirmed fact, and it should
be read that way. The preflight failure itself, exit 1, stands.
