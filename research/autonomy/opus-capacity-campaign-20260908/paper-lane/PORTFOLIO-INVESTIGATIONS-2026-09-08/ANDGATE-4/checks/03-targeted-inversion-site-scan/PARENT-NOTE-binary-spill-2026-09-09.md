# ⛔ CORRECTED 2026-09-09 — the original 86 MB body IS recoverable, and I said otherwise by omission

## Corrections

I wrote two versions of this note before this one. The **first** said the readable grep hits were
retained; they were not — extracting every NUL-free line yielded **zero bytes**, so all 1,669 of
1,669 lines were binary and this capture never held a readable hit. I corrected that within the
minute. The **second** still implied the body was gone. **It is not.** The original is intact as a
git object and I had not checked before writing. Root caught it.

## The original, pinned and verified

The body was committed in `40a4c14cf56e6b82823859c7a329ead1cef515a6`, the commit GitHub rejected
with `GH001`. It is held by `refs/recovery/andgate4-rejected-commit-20260909`, and `gc.auto`,
`gc.pruneExpire`, `gc.reflogExpire` and `gc.reflogExpireUnreachable` are disabled in this clone so
its objects cannot be expired.

| field | value |
|---|---|
| blob | `3f66e22b917dc2cf09623194be25d5575a8a5a16` |
| exact size | **86,447,935 bytes** |
| sha256 of content | `b1d42ec911d28869060ae89f5e8ec18156848df8a81e57e3a8c16226fe337f30` |

Hashed by streaming out of git, no temp copy. Exact recovery is
`git cat-file blob 3f66e22b917dc2cf09623194be25d5575a8a5a16 > stdout.txt`.

⚠ Like its sibling, **this body cannot reach the remote**: 86 MB is under GitHub's 100 MB hard
limit but the commit containing it also carried the 11.87 GB file, so the push was refused as a
whole. It could be pushed alone; it has not been, because committing 86 MB of binary spill into the
permanent history is a cost root should choose, not one I should impose.

## What this capture is, and what it means for the finding

1,669 of 1,669 lines contain NUL — the same `.tar.gz` spill inferred in the sibling note. Unlike
`checks/02`, this directory **does** have a real recorded `command.txt` and a real recorded
`exit_code.txt` (0). But that exit 0 attaches to a command whose entire output was binary.

⛔ **So ANDGATE-4's site-list result is carried by `FINDING.md` and `SITE-LIST.md`, not by this
capture.** Anyone re-verifying it must re-run the scan with binary files excluded
(`--binary-files=without-match`), not read this directory.

## Retained here, unchanged

`command.txt`, `exit_code.txt` (0), `stderr.txt`. No exit code was invented and the check was not
re-run to manufacture a replacement.
