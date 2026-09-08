# Receipt — G1 artifact intake, recorded from the collector's verification

Recorded 2026-09-08 09:16 UTC. **G1 is closed. No restart, no re-audit.**

| item | verified |
|---|---|
| pin | `d2ea5a7e63dde32de77296c17311c4ac0ea22c99` |
| retained set | `paper-lane/G1-executed-artifacts/` — 29 files, 1,005,788 B |
| manifest | 25 original hash checks, **all pass** |
| original child JSONL | 169,979 B, sha256 `5b0f9ce454c4db1a35767d8a29ee5ddf07302b73e8c25b091badd285fe8537a8` |
| served model | assistant turns **only `claude-opus-5`**; **21 tool pairs** |
| BEFORE | matches the initial commit |
| AFTER | matches the committed final |
| lint_consistency | baseline and post **byte-identical** |

## What this receipt does and does not authorise

It verifies **the named retained repository set**. It is **not** a comparison against the deleted
`/tmp/claude-0/g1-retained` scratch — that scratch is gone, I deleted it at ~09:12 UTC, before the
stronger rule was delivered at 09:13:25, and no byte-level comparison to it is possible now. **It is
not authorisation for wildcard cleanup of anything.**

## Campaign retention, unchanged and not relaxed

Every remaining campaign evidence directory stays intact until this sole local collector issues a
**directory-specific exact receipt** for it. Every follow-up is included. No generic, wildcard or
partial cleanup. 20 GiB free is adequate and is not a reason to delete. Currently protected on disk,
pending their own receipts: `/tmp/claude-0/{a1,a2,a3,b1,c1,d1,d2,d3,s5,s6,s7}-retained`.

These obligations **outlive the campaign deadline** — 2026-09-09T02:37:19Z is not cleanup permission.
