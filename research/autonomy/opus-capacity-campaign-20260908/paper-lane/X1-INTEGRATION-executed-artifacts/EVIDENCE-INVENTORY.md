# X1 INTEGRATION — execution evidence directory

Collected 2026-09-08 by the campaign parent, in place, from the executing session. Retained here so
the sole local collector can issue a directory-specific receipt against
`research/autonomy/opus-capacity-campaign-20260908/paper-lane/X1-INTEGRATION-executed-artifacts/`.

The commit and the integration narrative in `INTEGRATION-X1-atr-working-revision.md` do **not**
substitute for this directory. This directory is the execution evidence.

**Nothing was re-run to produce it.** No gate was re-executed, no view regenerated, no baseline
restored, no lost byte recreated, and nothing was deleted. The X1 candidate lane at
`paper-lane/X1-executed-artifacts/` is unchanged and is a separate retained set.

## What is here, and where each file came from

### Original working directory, copied verbatim
`/tmp/claude-0/x1-integrate/` was copied byte-for-byte with `cp -a`, then verified with
`diff -rq` (no differences). These files were written during execution and are originals:

| file | what it is |
|---|---|
| `apply.py` | the edit script that applied the seven authorized corrections, exactly as executed |
| `INTEGRATED-emc-atr-collaborator-package.md` | the manuscript as `apply.py` left it, **before** the two later style fixes |
| `baseline/emc-atr-collaborator-package.md` | the committed manuscript replaced, copied before any write |
| `baseline/emc-atr-collaborator-package-cover-letter.md` | the cover letter before any write |
| `baseline/L3-publications.md`, `baseline/L2-rt-atr-panel.md` | the two generated views before regeneration |
| `checks/lint_style.txt` | first `lint_style` run over the three files (the run that exited 1) |
| `checks/lint_claims.txt` | `lint_claims` over the three files |
| `checks/lint_consistency.txt`, `checks/consistency.txt` | the failed argument-passing attempt, then the repo run |
| `checks/lint_submission_residue.txt`, `checks/lint_asymmetry.txt` | the failed argument-passing attempts |
| `checks/lint_citations.txt` | the full `lint_citations` output, 258,097 B, exit 1 |
| `checks/systems_check.txt` | `systems_check` before the QA-note frontmatter fix |
| `checks/systems_check-after.txt` | `systems_check` after that fix |

### Written at collection time, from retained bytes only
| file | how it was made |
|---|---|
| `after/*` (5 files) | copies of the committed post-integration files, taken from the working tree |
| `diffs/*.diff` | `diff -u` between the `baseline/` copies retained above and the `after/` copies. Derived at collection time from retained bytes; **not** a record captured during execution. |
| `diffs/post-apply-vs-final-manuscript.diff` | shows exactly the two later style fixes, so the gap between the two manuscript states is visible rather than asserted |
| `diffs/x1-candidate-vs-final-manuscript.diff` | the accepted candidate against what was committed |
| `EXTRACTED-FROM-PARENT-TRANSCRIPT-commands-and-results.txt` | see below |
| this inventory, and `SHA256SUMS.txt` | |

### Bounded extraction from the parent transcript
Several edit scripts were written as shell heredocs rather than as files, and most stdout and stderr
was never redirected to a file. That material survives only in the parent session transcript
`/root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71.jsonl`.

`EXTRACTED-FROM-PARENT-TRANSCRIPT-commands-and-results.txt` carries **59 Bash calls**, each as the
literal `tool_use` input and the literal `tool_result` body the transcript stored, with both
timestamps and the tool_use id. Extraction is bounded to calls timestamped at or after
`2026-09-08T12:29:00`, the start of the integration turn. Nothing in it was re-run, reconstructed or
paraphrased. It is an **extraction from a parent transcript**, not standalone execution output, and
it is labelled as such in its own header. The transcript file itself was not copied into the
repository.

It contains the heredoc bodies for: the cover-letter C1-C4/T1-T2 edits (including the first attempt
that aborted on `AssertionError: ('C1', 0)` because of line wrapping), the QA-note style fixes, the
two manuscript style fixes, the section 3.5 reflow, and the Y1 dated append.

## Honest gaps

1. **Exit codes are partial.** Where a command echoed `EXIT=$?` the code is in the result body;
   where a command failed, the harness recorded `Exit code 1`. For commands that did neither, no
   exit code was captured and none is asserted here. They were not re-run to obtain one.
2. **No after-copy of the cover letter or QA note was taken during execution.** The copies in
   `after/` were taken at collection time from the committed tree. They are the committed bytes, not
   a mid-execution snapshot.
3. **`git stash` was used once** to compare the `systems_check` error count with and without the
   tracked changes. The untracked QA note was therefore present in both runs, so that comparison
   bounds the tracked changes only. The tree was restored and verified. This is recorded because it
   touched the shared tree, which the campaign's own rules discourage.
4. **`submission_metrics.py --help` executed and wrote** `submission-metrics.json`. `--help` is not
   implemented by that script. The invocation was not deliberate. It is in the extraction verbatim,
   including its output.
5. **`lint_consistency.py`, `lint_submission_residue.py` and `lint_asymmetry.py` were first invoked
   with file arguments they do not accept** and exited 2 on usage. Those failures are retained in
   `checks/` rather than discarded, and the successful re-invocations are in the extraction.
6. `INTEGRATED-emc-atr-collaborator-package.md` (62,299 B) is **not** the committed manuscript
   (62,271 B). The difference is the two style fixes, and `diffs/post-apply-vs-final-manuscript.diff`
   shows it exactly.
