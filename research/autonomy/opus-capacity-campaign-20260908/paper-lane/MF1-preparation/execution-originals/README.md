# MF1 execution originals — what survives, and the precise gap

**2026-09-08, parent. Normal small-original collection. ⛔ No check was re-run, no output was
reconstructed, and no exit code was invented.**

## ⛔ The missing-original gap, stated precisely

**The MF1 lane wrote NO separate stdout, stderr or exit-code files.** Its returned delta contained
exactly two files — `HANDOFF-MF1-methods-record-frozen.md` and
`SETTLED-figure-and-text-presentation.md`. The per-file check table in handoff section 4 is a
**transcription** of results into prose; the raw captures it transcribes were never written to disk
as separate artifacts.

So the gap is: **no standalone original capture file exists for any MF1 check.** That is reported,
not filled. ⛔ Nothing here reconstructs one.

## What DOES survive, and is collected here

`agent-a1e5e7fe0843f7bb6.jsonl` — the completed MF1 child's own execution transcript, **416,776
bytes**, sha256 `157e09f3a60d6cf14b778af0910815112db0e041ff0925b70e025306ade6efda`, copied
byte-for-byte from the runtime's retained subagent record. It contains the actual tool invocations
and their returned output for the checks handoff section 4 describes — 18 lines reference the check
commands (`lint_style`, `lint_claims`, `lint_readability`, `submission_metrics`) and 22 reference an
exit code or an argparse usage error.

⚠ **This is the execution record, not a re-derivation.** It includes the **failed and usage-error
attempts**: the three repo-wide linters (`lint_consistency`, `lint_asymmetry`,
`lint_submission_residue`) that rejected a per-file argument with **EXIT=2 argparse usage errors**,
which are recorded as non-passes and must never be read as passes, and the `lint_style` EXIT=1 run.

## ⚠ Status clarification carried at root's instruction — the handoff itself is NOT edited

Handoff **section 5 item 9**'s P1-versus-P6 framing and submission-authority language is **historical
process wording**. Root's MF1 admission stated that the old discretionary framing permission is
**already superseded by standing preprint authority**. ⛔ Do not revive an author-framing permission
wait on the strength of that sentence, and ⛔ do not treat working-tree item 10 as the
post-integration state.

⚠ Publication still requires the existing final-review and actual applicable requirements. **No new
permission and no publication act follows from this collection.** The original handoff is preserved
unedited; this is an ordinary status clarification beside it, not a rerun of the preparation.

⛔ This is not a new review, not a new worker, and not a gate before root's final scientific review.
