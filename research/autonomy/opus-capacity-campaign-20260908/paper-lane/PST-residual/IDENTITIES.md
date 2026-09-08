---
id: DOC-OPUS-CAMPAIGN-PST-RESIDUAL-IDENTITIES
title: "Before and after identities for every file touched by the P-ST residual batch"
level: L4
kind: identity-record
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Identities — P-ST residual batch R1 to R8, 2026-09-08

Byte copies of every "before" state are in `BEFORE-2026-09-08/` with `SHA256SUMS-BEFORE.txt`.

## Files this author changed

| File | Before bytes | Before SHA256 | After bytes | After SHA256 |
|---|---:|---|---:|---|
| `…/P-ST-correction/revised/emc-surface-target-landscape.md` | 132,856 | `ebce0a9db28d3c5a7187a10005fc73b5666232a20a1cd110fa74c59d58bee6e3` | **146,042** | `371ec8d92c3238b09f2117e14613184c422db1f094e83f431bad07d46e93179e` |
| `…/P-ST-correction/revised/emc-surface-target-landscape-si.md` | 54,084 | `105fc8732dfdb367b6793932b663815f74ae76ea483c1c1daf5a40991794a368` | **56,124** | `290212776b2f103d64a270f12936245be00bfc6c97f5678b492589bc3680ad16` |
| `research/manuscripts/surface-targets/emc-surface-target-landscape.md` | 99,615 | `8931895d65bf6cc7de0d83b8cbd6c644b3eb664de221b56861a2a0940584df6f` | **146,042** | `371ec8d92c3238b09f2117e14613184c422db1f094e83f431bad07d46e93179e` |
| `research/manuscripts/surface-targets/emc-surface-target-landscape-si.md` | 41,853 | `92a7c49fc406a391d519912108fe888dc499c635ec29d1c3f834445665cdafd1` | **56,124** | `290212776b2f103d64a270f12936245be00bfc6c97f5678b492589bc3680ad16` |
| `…/P-ST-correction/F01-F13-RESPONSE-MAP.md` | 16,250 | `7951619753f7ea87096460fee2a4962eda46edab700c48ebacc66d49c668d4ff` | **18,559** | `21106f6a14c8e812881ca3931bcf38c0ee430ced125414e9e7209f52ff7eae1d` |
| `…/P-ST-correction/CORRECTION-RECORD-P-ST.md` | 10,413 | `4f462c3b7f4857cd80aeacd4d8a12de859a327bdf9a31d67b139a5e4b374c143` | **12,631** | `2f8b2cbd6a8a2617ce8dfe17f8dd76b2ea9a14a08fa9ace64ec9679d7e974d5c` |

The two canonical manuscript paths carry the residual-corrected pair, byte-identical to the candidate
copies (verified). The 99,615 / 41,853-byte baseline bytes are preserved unaltered in
`…/P-ST-correction/frozen/`, in `BEFORE-2026-09-08/`, and in Git history.

## Files this author read and did NOT change

| File | Bytes | SHA256 | Note |
|---|---:|---|---|
| `…/P-ST-correction/packet/PACKET-MANIFEST.json` | 8,996 | *(unchanged; dated historical identity record)* | Deliberately not rewritten; superseded by `CURRENT-PACKET.md` as a statement of the current pair |
| `…/P-ST-correction/frozen/emc-surface-target-landscape.md` | 99,615 | `8931895d…0584df6f` | Historical input |
| `…/P-ST-correction/frozen/emc-surface-target-landscape-si.md` | 41,853 | `92a7c49f…65cdafd1` | Historical input |
| `…/PST-source-locators/geo_esummary_emc.txt` | 30,740 | `1726d018625bd4d4afdadd9364a7447d650ae5c88e9a2c228fe4463845aaac0c` | Located, verified in place, not reacquired |
| `research/modalities/emc-tissue-read-statistics.json` | — | *(read only)* | Stored `scored` flags read for the sixteen-panel erratum |
| `research/modalities/emc-surface-prioritization.png` | — | `130042b6afab8aea28874d37dd684cde96886ab25b488ab65b83dac391c439bd` | Omitted Figure 1's historical bytes, verified untouched |

## Files changed by the PARENT before this lane was dispatched (R8) — not this author's edits

| File | Before bytes / SHA256 | After bytes / SHA256 |
|---|---|---|
| `research/modalities/gse28866-tumour-vs-normal.json` | 27,256 / `ac0a17bd81dd8bc2ecc3b5bb380de5ae00921ae2d32b5a9595bd1449720be407` | 28,606 / `386a035175d94ef8eccd3719d74ef39cff5e93461ed2470983777333a1962cee` |
| `research/modalities/gse28866_tumour_vs_normal.py` | 30,914 / `6dcea81de63a4dd9ab66f39144b2ba531351efd9f1a8d51b233388456bfbdb78` | 31,856 / `404fe28582d9891a498b5407dc980e5ce7a16ac94a11eee267f7f6b7d8d4b46a` |

Both "after" identities were re-measured on the live tree by this author and match the receipt exactly.
No producer was executed by anyone in this batch.

## Artifacts this author created

`R1-R8-RESPONSE.md`, `SIXTEEN-PANEL-ERRATUM.md`, `CURRENT-PACKET.md`, `RESIDUAL-LIMITATIONS.md`,
`IDENTITIES.md`, `CHECK-RUN-RECORD.txt`, `BEFORE-2026-09-08/`, `DIFFS/`, `checks/`, `execution/`,
`patches/`.
