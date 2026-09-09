---
id: DOC-OPUS-CAMPAIGN-TD1-FINAL-DOC-APPLIED-20260909
title: "TD1 final documentation correction — parent direct application"
level: L4
kind: record
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# TD1 final two-file documentation correction, applied

Root disposition read IN FULL (`ROOT-DISPOSITION.md`, 9,992 B,
`f74572d8dee8f9d96a5a1372aff121b12f565873a58d0bcd829c417c6a754f37`). Parent direct integration.
**No TD1 author, reviewer, producer, classifier, source query, statistic or broad-check cycle was
run**, and none is needed.

## Capsule intake, verified by the parent

Ref `codex/opus-cloud-inputs-20260908` at commit `8b5851b0d6bc08f0ae242731ae4a30912e25b517`.

| object | bytes | sha256 | git blob |
|---|---:|---|---|
| `td1-root-final-doc-original-inputs.zip` | 89,757 | `e86a05636822b280fe94af4d34917ea30c975b46daeef8200dfd34d865ba732f` | `8afbbd74a984cde20c1a0e33f556d3e92c896b01` |
| `…​.manifest.json` | 2,351 | `69a9647975e9656e44edbaf3566143238419e4c1d8189f804baec241620a30d2` | `d49c77719420002e08a6ec74b061e7c2901d9530` |

13 ZIP members, **CRC-clean** (`testzip()` → None), **zero unsafe paths**. **12 of 12 manifest
rows matched on both byte count and sha256**; the 13th member is `PACKAGE-MANIFEST.json` itself,
which the manifest's own `qualification` says it does not hash. Twelve originals total
**247,854 B**, matching the packet's stated figure.

## Before-state matched exactly, so nothing concurrent was overwritten

| file | live before | packet `before/` |
|---|---|---|
| main | 48,268 B `9523555483f0…` | 48,268 B `9523555483f0…` |
| GP producer | 56,050 B `43447cd4a475…` | 56,050 B `43447cd4a475…` |

Both matched, so the "if the base differs, retain the actual difference" branch did **not** fire.

## Application

`git apply --check -v` exit **0**, then `git apply` exit **0**, using the packet's own
`FINAL-DOC-CORRECTION.patch` (5,113 B, `2cacc073d687…`) — not a whole-file copy. Two files,
20 insertions / 16 deletions.

| file | after | matches packet `proposed/` |
|---|---|---|
| main | 48,491 B `3061156574b9483346d7bb2516e78560f7c1da34c4ecd49c123a81ee96c5ac6d` | yes (`cmp -s`) |
| GP producer | 56,239 B `592b89df6c5ec8a3f5bd6b4ec986de1360a966806c868ba389293ebd1ca3e370` | yes (`cmp -s`) |

The GP blob id is `0df23bc25e63d2e64a3eb9442706824cd60f6bb6`, exactly the id root recorded.
`python3 -m py_compile` on the patched producer: exit **0**.

## The TCIP six-byte difference is preserved

`systems/graph/publications.json` is **71,006 B / `fc55087c5de17c4f…`**, unchanged by this patch —
still six bytes larger than the author-after `71,000 B / 7f923cc0…`, which is exactly the accepted
b42 `PUB-TCIP.what_it_would_claim` correction. Root required it to remain, and it remains. **This
packet edits no shared JSON and no scientific quantity.**

## What the two edits are

1. **GP**: the one omitted R2 `depmap()` docstring, replaced exactly. Only the docstring changes.
2. **Main §8**: three fixed-identity cells bound to the integrated C/G/GP annotation versions, and
   the obsolete "pending integration" wording removed — it described already-integrated changes as
   pending and omitted the producer. All 78 table lines remain.

## Boundary, carried forward unsoftened

The narrower descriptive synthesis remains viable. ⛔ **The stronger opposite-disagreement /
EMC-selectivity claim remains PARKED**, and this correction supplies nothing toward reopening it.
GPL3290 stays withheld from biological corroboration; normal-tissue selectivity and linked EMC
expression–dependency remain **unmeasured**; the literature, binding, depletion-mechanism and
reference questions remain distinct.

Root's own provenance clarifications are recorded and **not repaired**: the original
`HASHES.sha256` has 58 matching entries and one mismatching **self**-entry, which stands; check
group 07 has valid-JSON stdout but **no retained numeric exit sidecar**, so its exit 0 is narrative
rather than captured evidence; 06 has no stdout sidecar and 09 no stderr sidecar — **empty and
missing are different**. The frozen original report is not edited to conceal the C1/C2 → Q2/Q6
locator error; this memo is the addendum. No publication or style gate is waived.
