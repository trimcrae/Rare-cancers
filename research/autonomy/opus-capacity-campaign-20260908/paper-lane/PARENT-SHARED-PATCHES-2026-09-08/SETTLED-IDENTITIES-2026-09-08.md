---
id: DOC-OPUS-CAMPAIGN-PARENT-SETTLED-IDENTITIES
title: "Settled source and output identities after the shared-patch integration"
level: L4
kind: binding
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Settled identities — the rebinding

**Settled extraction:** `13-mf1-extraction-SETTLED`, **exit 0**, stderr **0 bytes**, at commit
`91609d30fdc672f4dbc9eb191e6342a7ddd4f61d`:

```
results rows: 10
inventory rows: 22  route 4+16  census 22
manifest inputs: 18 at commit 91609d30fdc672f4dbc9eb191e6342a7ddd4f61d
inputs NOT bound to their HEAD blob: 0 of 18
author-current scope overrides: 4 (V11, V16, V20, V5)
```

**0 of 18 unbound.** The pre-settlement attempt (`10-…`, 1 of 18 unbound, the uncommitted
regenerated census) is retained beside it exactly as measured, and is **not** relabelled.

## Final bytes

| what | file | bytes | sha256 |
|---|---|---:|---|
| MF1 main | `degrader-methods-failure-record.md` | 88695 | `b5036d4fe44b8a5e55318a50ea0d961e5b19d4eb4a53802b9edb155ac3c12e31` |
| MF1 SI | `degrader-methods-failure-record-SI.md` | 41072 | `c4e2f1e969233888dafa99dfca1c457a59f3121e1073191532889152402de18c` |
| MF1 corrective interpretations | `corrective-interpretations-2026-09-08.md` | 21655 | `6f921fa832de0f2d979c000ea73de36db12a41c4bb6d028090e6983ca1bdf7f3` |
| manifest (settled extraction) | `MF1-dependency-manifest.json` | 7287 | `489a12fa8fd8f77ef5fc367d20348aec705eef8ab41bd989ae3504aab5d2b1a4` |
| inventory (settled extraction) | `MF1-instrument-inventory.md` | 26385 | `484f2590e489b9291f6714011a4765f296f62936f068627f76fc19c3b97e2f9f` |
| results (settled extraction) | `MF1-quantitative-results.md` | 9897 | `62bf3d41fd8a9d025d859a863c35caed315d8b230395644162af9ba3244bc530` |
| roadmap (source, patched) | `nr4a3-program-map.md` | 620062 | `8d92e9e8656de3fa8fa371137772fcc051e5f26da28c4ed6179746a52950af48` |
| census JSON (regenerated) | `instrument-census.json` | 31770 | `f484afe4bb5795283dab8131cf47d3fe2d4204b401c559a41ad406366228526a` |
| census MD (regenerated) | `instrument-census.md` | 22903 | `76847795b561893855fbdc7aa8e1a4dc285a4fa3d88b106dfb56bc0626258829` |
| publications graph (patched) | `publications.json` | 68537 | `e31fa506bc2fd8ff7e594c0284aa4e30cd2c5c0da65f7e864e1bc05b0d61c6f9` |

## What the rebinding did and did not touch

**The MF1 main and SI carry no sha256 references at all** (measured: 0 occurrences of `sha256` or
`SHA256` in either file), so there was no stale identity embedded in the prose to rebind. Their bytes
are unchanged by the extraction — the extractor writes only the three `MF1-repair/` outputs.

The only references to the **pre-settlement** inventory and manifest hashes live inside the MF1
residual author's own `IDENTITIES.md` and its `checks/05-…/identities-after.txt`. Those are
**historical records of that run** and are left byte-unchanged; this file is the current binding
beside them, not a replacement.

`MF1-instrument-inventory.md` moved 25,317 → 26,385 B against the author's run, because the
extraction now reads the corrected roadmap and the regenerated census. That is the propagation
working, not a discrepancy.

⭐ **Precisely which run moved it, corrected 2026-09-08:** that move happened at the
**pre-settlement** run `10-…`, whose outputs were committed in `91609d30f`. The **settled** run
`13-…` changed **only `MF1-dependency-manifest.json`** — the binding commit and the
`bytes_match_head_blob` flags, 1-of-18-unbound to 0-of-18. An earlier sentence here attributed the
inventory's move to the settled run; that attribution was wrong and this is the measured record.

## Preserved

The two extraction runs, both real, neither reconstructed. Every command, full stdout, full stderr
and measured exit is under `checks/`. MF1 remains on **HOLD**; nothing here establishes all-green or
scientific clearance, and the inherited preflight failure is untouched and unadjudicated.
