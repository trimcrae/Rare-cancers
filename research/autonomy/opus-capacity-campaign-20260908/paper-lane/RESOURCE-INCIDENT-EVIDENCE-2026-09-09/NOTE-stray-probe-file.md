---
id: DOC-OPUS-CAMPAIGN-RESOURCE-INCIDENT-EVIDENCE-20260909
title: "A stray zero-byte probe file from the ENOSPC outage"
level: L4
kind: record
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# `.tmp-probe.txt` — what it is, and what I could not establish about it

A zero-byte file named `.tmp-probe.txt` appeared at the **repository root** at 01:39, during the
disk exhaustion described in `../RESOURCE-INCIDENT-2026-09-09.md`. Its shape says what it was for:
a lane testing whether writes were succeeding while the volume was full. ANDGATE-4's return
explicitly disclaimed it as another worker's.

**What is established:** it is 0 bytes, so its sha256 is
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, the sha256 of the empty string.
Its mtime is 2026-09-09 01:39, inside the outage window.

**What is NOT established: which lane created it.** No lane claimed it, and a zero-byte file carries
no content to attribute. I did not guess an owner.

**Disposition.** It was moved here rather than deleted, and renamed off the `.txt`-at-root position
that put a stray dotfile in the repository root — a lane-scoping violation in itself, whoever made
it. Its bytes are unchanged: still zero, still that hash. Nothing was written into it.

Deleting an artifact of the outage whose owner I could not establish would have been the easy call
and the wrong one; the campaign's rule is that unestablished ownership means preserve and report,
not tidy away.
