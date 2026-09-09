# ⛔ CORRECTED 2026-09-09 — my first version of this note overclaimed, twice

## The correction, first

An earlier version of this note said the 11.87 GB body was "removed" and that "nothing was lost".
**Neither claim was established when I made it.** An excerpt is not byte recovery, and I had not
checked whether the original was recoverable before I wrote that it did not matter. Root caught
both. The superseded wording is preserved at the end of this file.

I also described the mechanism — a `grep` matching inside `.tar.gz` archives and streaming their
decompressed bytes — as if it were observed. ⚠ **It is an INFERENCE** from the lane's own
`stderr.txt`, whose last lines read `binary file matches` against two `.tar.gz` paths immediately
before `write error: No space left on device`. That is strong evidence for the mechanism; it is not
a directly observed write. The directly observed facts are the byte size, the `binary file matches`
lines, and the ENOSPC errors.

## The originals ARE recoverable, and are now pinned

The bodies were committed in `40a4c14cf56e6b82823859c7a329ead1cef515a6` — the commit GitHub
rejected with `GH001`. That commit was reset out of the branch but its objects were never pruned.
They are now held by a local ref that must not be deleted:

```
refs/recovery/andgate4-rejected-commit-20260909 -> 40a4c14cf56e6b82823859c7a329ead1cef515a6
```

`gc.auto`, `gc.pruneExpire`, `gc.reflogExpire` and `gc.reflogExpireUnreachable` are all disabled in
this clone so the objects cannot be expired.

| file | blob | exact size (bytes) | sha256 of blob content |
|---|---|---:|---|
| `checks/02/stdout.txt` | `338a1c16e5780b1ba1f42b7ab7e6021cd915b3d0` | 11,874,455,552 | `66db6c45484e45ea8975511be40e0e8b5873b417fb512f6f0843ef243fc6e916` |
| `checks/03/stdout.txt` | `3f66e22b917dc2cf09623194be25d5575a8a5a16` | 86,447,935 | `b1d42ec911d28869060ae89f5e8ec18156848df8a81e57e3a8c16226fe337f30` |

Both hashes were computed by **streaming the blob out of git**, never materialising a temp copy, so
verification cost no disk. Recovery of either body is exact and is one command:
`git cat-file blob <blob> > <path>`.

## ⛔ The recovery requirement root needs to know

**These bodies cannot reach the remote.** GitHub refuses any file over 100 MB, which is why the
original push was rejected in the first place. So the objects live **only in this container's
object store**, and this container is reclaimed when the session ends. A gzip recovery artifact is
being produced locally with verified decompressed size and hash, but at roughly a 9.8 % ratio
measured on a bounded 200 MB sample the compressed body is still on the order of **1.2 GB** — also
far past the 100 MB remote limit.

**If root needs these two bodies durably, it needs a route that accepts a ~1.2 GB artifact.** No
such route exists inside this session's admitted set, and I am not inventing one. What survives a
container reclaim without such a route is: the exact sizes, the exact sha256 of each body, the
200 KB excerpt, and the complete `stderr.txt`.

## What is retained here, unchanged

`stdout.FIRST-200KB-EXCERPT.txt` (the first 200,000 bytes), the complete 13,055-byte `stderr.txt`,
the **0-byte** `command.txt` — the command was never recorded — and `exit_code.txt` reading
`UNKNOWN — NOT RECORDED, NOT FABRICATED`, plus the lane's own `NOTE.md`. Nothing was fabricated, no
exit code was invented, and no check was re-run.

⚠ The lane's `NOTE.md` describes this file as "1450+ lines". That description does not match an
11.87 GB object, and the lane never learned otherwise, because the failure that stopped it
measuring the file is the failure the file caused.

## Superseded wording, retained

> The 11.87 GB body was **removed by the parent**, not by the lane. … **Why this is not a loss of
> evidence** — The lane's finding does not rest on this capture.

The second sentence may well be true of the *finding*; it was not established as a statement about
the *bytes*, and I should not have written it as one.
