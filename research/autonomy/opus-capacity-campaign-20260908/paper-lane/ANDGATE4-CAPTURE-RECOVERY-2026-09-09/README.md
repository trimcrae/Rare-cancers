---
id: DOC-OPUS-CAMPAIGN-ANDGATE4-CAPTURE-RECOVERY-20260909
title: "ANDGATE-4 capture bodies — recovered, verified lossless, one published and one not"
level: L4
kind: record
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# The two ANDGATE-4 capture bodies: recovered from git, compression verified lossless

## Additive correction to what I asserted earlier

Two of my earlier statements were **not established when I made them** and are corrected here
rather than edited away:

1. I wrote that the bodies were "removed" and that "nothing was lost". **An excerpt is not byte
   recovery.** I had not checked recoverability before writing that the loss did not matter. Both
   bodies were in fact intact in the git object store the whole time.
2. I described the mechanism — a `grep` matching inside `.tar.gz` archives and streaming their
   decompressed bytes — **as if observed. It is an INFERENCE.** What was directly observed is: the
   byte sizes; the lane's `stderr.txt` ending in `binary file matches` against two `.tar.gz` paths
   immediately followed by `write error: No space left on device`; and that 1,669 of 1,669 lines in
   the `checks/03` body contained NUL. The decompression step itself was never watched.

The superseded wording is preserved verbatim in both per-check notes under
`../PORTFOLIO-INVESTIGATIONS-2026-09-08/ANDGATE-4/checks/`.

## The originals, pinned and not expirable

```
refs/recovery/andgate4-rejected-commit-20260909 -> 40a4c14cf56e6b82823859c7a329ead1cef515a6
```

That is the commit GitHub rejected with `GH001`. In this clone `gc.auto`, `gc.pruneExpire`,
`gc.reflogExpire` and `gc.reflogExpireUnreachable` are all disabled, so its objects cannot be
pruned. ⛔ **Do not delete that ref and do not run `git gc --prune` in this clone.**

| capture | blob | exact original bytes | sha256 of original content |
|---|---|---:|---|
| `checks/02/stdout.txt` | `338a1c16e5780b1ba1f42b7ab7e6021cd915b3d0` | 11,874,455,552 | `66db6c45484e45ea8975511be40e0e8b5873b417fb512f6f0843ef243fc6e916` |
| `checks/03/stdout.txt` | `3f66e22b917dc2cf09623194be25d5575a8a5a16` | 86,447,935 | `b1d42ec911d28869060ae89f5e8ec18156848df8a81e57e3a8c16226fe337f30` |

Exact recovery of either is one command: `git cat-file blob <blob> > <path>`.

## Compression, and the losslessness proof

Each blob was streamed out of git through `gzip -6`, then the compressed file was decompressed and
**both its byte count and its sha256 recomputed and compared to the original**. Verbatim output is
in `RECOVERY-VERIFICATION.txt`:

| capture | original B | gzip B | ratio | round-trip size | round-trip sha256 | match |
|---|---:|---:|---:|---:|---|---|
| checks/02 | 11,874,455,552 | 535,363,406 | 4.51 % | 11,874,455,552 | `66db6c45…e916` | **YES** |
| checks/03 | 86,447,935 | 2,158,576 | 2.50 % | 86,447,935 | `b1d42ec9…7f30` | **YES** |

⚠ The actual ratios (4.51 % and 2.50 %) are **better than the ~9.8 % I projected** from a bounded
200 MB sample. My projection of "about 1.2 GB" for the large body was therefore wrong: it is
535 MB. Correcting that here rather than leaving the estimate standing.

## What is published, and what is not

* **PUBLISHED**: `checks03-stdout.3f66e22b.orig.gz` — 2,158,576 B, sha256
  `a9abfcc45dea2d50b90aa7632967536a85c2a56ac9d407bf9db7b0f7ff33ca71`. This is the **complete**
  `checks/03` body, losslessly compressed, comfortably inside the 100 MB remote limit. Decompress
  and it is byte-identical to the original, hash proven above.
* ⛔ **NOT PUBLISHED**: `checks02-stdout.338a1c16.orig.gz` — 535,363,406 B, sha256
  `7df6d7082c3e35f7d75e5fb1c1de5d173be6f3d705e95016bd1b52d42289d507`. It exists **only in this
  container** at
  `<session scratchpad>/recovery/338a1c16e5780b1ba1f42b7ab7e6021cd915b3d0.gz`. At 535 MB it is
  five times the remote's 100 MB per-file limit, so there is no admitted route that can carry it
  off this machine. **The uncompressed 11.87 GB blob is never published, under any circumstances.**

## The precise recovery requirement, for root

The `checks/02` body — 11.87 GB raw, 535 MB compressed — **cannot leave this container** through
any route this session holds. It survives only as long as the container does. If root needs it
durably, that requires a transport accepting a 535 MB artifact; none exists in the admitted set and
I have not invented one.

What survives a container reclaim without such a transport: the exact original size, the exact
sha256 of the original content, the sha256 of its verified-lossless gzip, the recovery ref and blob
id, the 200,000-byte excerpt, and the complete 13,055-byte `stderr.txt` — plus the whole of
`checks/03`, whose compressed original is published here.

## What the bodies do and do not carry

`checks/03`'s body has **no readable line at all** — every one of its 1,669 lines contains NUL.
So ANDGATE-4's site-list result rests on its `FINDING.md` and `SITE-LIST.md`, and its recorded
`exit 0` attaches to a command whose entire output was spill. Re-verification must re-run the scan
with binary files excluded, not read that capture. `checks/02`'s `command.txt` is **0 bytes** and
its `exit_code.txt` honestly reads `UNKNOWN — NOT RECORDED, NOT FABRICATED`; no exit code was
invented and no check was re-run.
