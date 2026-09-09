---
id: DOC-OPUS-CAMPAIGN-RESOURCE-INCIDENT-20260909
title: "Disk exhaustion during the portfolio wave — measured cause and actual recovery"
level: L4
kind: record
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# ENOSPC across the lane pool — what it actually was

At about 01:38Z every write in this session began failing with `ENOSPC`. Three lanes reported it
independently and correctly: DISCOVERY-2 could not `mkdir` its own lane directory and therefore
wrote **nothing**; ENDPOINT-2 lost its `FINDING.md`, its regeneration check and its `regenerated/`
tree; MODALITY-CENSUS-2's run 04 emitted no exit code at all. **All three refused to free space**,
citing the campaign's disk-floor rule, and reported the condition instead. That was the right call
and it is why this record can be written.

## Measured, not guessed

| measurement | value |
|---|---|
| filesystem | `/dev/vda`, **one volume mounted at `/`** |
| bytes total / used / available | 258,020 MB / 33,984 MB / **3,955 MB (90 % used)** after recovery |
| inodes used / total | 360,357 / 16,777,216 = **3 %** |
| repository working tree | 14,965 MB, of which `.git` is 2,637 MB |

⛔ **INODES WERE NEVER THE CONSTRAINT — 3 % used.** The constraint was bytes.

⛔ **AND THERE IS NO SECOND FILESYSTEM TO REDIRECT SCRATCH TO.** `/tmp` and
`/home/user/Rare-cancers` are the **same** device, `/dev/vda` on `/`. Pointing new scratch at
another volume is not available here; the only lever is not generating the bytes.

## Cause: full checkout copies, and this session was the largest recoverable consumer

Before recovery my session scratchpad held **4,416 MB**. Four of its entries were **plain copies of
the repository tree** — `head` (665 MB), `head-clone` (729 MB), `headtree` (783 MB) and `pert`
(729 MB) — plus `s4` (1,138 MB), the scratch of the already-completed and already-committed
IPD-SURVIVAL-4. That is roughly 4 GB of duplication of content that is committed and
byte-recoverable from git.

The other large directories under `/tmp/claude-0` belong to **other sessions and lanes**, not to
this one: `w03f` 1,222 MB, `md1-lane` 1,133 MB, `b2-lane` 673 MB, `w34` 617 MB, `w27b` 614 MB,
`w16f` 612 MB, `w09h` 431 MB, `w26b` 429 MB, and four `w14b_w*` at ~423 MB each. **None was
touched.**

## What was actually recovered, and what was verified first

Deleted, all of it proven redundant before removal:

* `head`, `head-clone`, `headtree`, `pert` — repository tree copies. Verified: content committed,
  recoverable by `git checkout`. **~2,906 MB.**
* `s4` — scratch of IPD-SURVIVAL-4, whose lane directory and every check are committed at
  `97533a402`. Verified idle: no file modified in the preceding 8 minutes. **~1,138 MB.**
* Completed subagent transcripts in the harness `tasks/` directory. These are harness records, not
  research evidence; every one of their results is quoted in a commit message. **~38 MB.**

Scratchpad **4,416 MB → 374 MB**. Available bytes **~0 → 3,955 MB**.

**Not touched, deliberately:** every lane directory in the repository; every uncommitted working
file; every other session's scratch under `/tmp/claude-0`; and the caches
`ctg-cache-216bd1b5` (151 MB) and `kmcache` (36 MB), which are retrieval products other lanes may
still read.

## The one real loss

ENDPOINT-2's byte-level demonstration that its regenerated artifact "differs in exactly the
expected places and no others" **was not produced**. Its predicted six-number delta is recorded in
its FINDING as a prediction, **not as a verified result**, and must be re-run before anyone relies
on it. Nothing else was lost: every other affected lane either completed or reported cleanly.

## Prevention, in force from now

1. **No lane creates a full checkout copy.** Read the working tree in place. Where a lane must
   perturb files, copy only the specific files it perturbs, into a `TemporaryDirectory` that is
   destroyed on exit — the pattern the FP negative fixtures already used.
2. **A lane's scratch is deleted by its own author when the lane returns**, once its evidence is in
   its lane directory. A completed lane's scratch is not campaign evidence.
3. Because there is only one volume, **`CLAUDE_CODE_TMPDIR` cannot help** and must not be offered
   as a fix.
4. High-output dispatch is throttled until measured headroom is restored, and headroom is
   **measured** before each wave rather than assumed.
