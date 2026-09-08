---
id: DOC-MF1-RESIDUAL-IDENTITIES
title: "MF1 residual — before/after identities of every file touched"
level: L4
kind: memo
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Before / after identities — MF1 residual batch, 2026-09-08

Byte counts and SHA-256 of every file this author wrote, measured with `stat -c%s` and `sha256sum` in
the working tree. Byte-exact BEFORE copies are in `BEFORE-20260908/` with their own `SHA256SUMS-BEFORE.txt`;
exact unified diffs are in `DIFFS/`.

## Files written

| file | before bytes | before sha256 | after bytes | after sha256 |
|---|---:|---|---:|---|
| `research/manuscripts/methods-record/degrader-methods-failure-record.md` | 73,844 | `4a99804f9f50ac687ad709b5ea0aad4bc5c9a48a351934aa24ee94364a64430e` | **88,695** | `b5036d4fe44b8a5e55318a50ea0d961e5b19d4eb4a53802b9edb155ac3c12e31` |
| `research/manuscripts/methods-record/degrader-methods-failure-record-SI.md` | 26,791 | `7e988f0a10118d9d1ec038e7d37c2b5d3527005c4f1f2b3b71971f95c04ea66a` | **40,004** | `36fcdc3b3a32c34a6730933cc8b335ad68609d7839e4dd99d74e4ca29b1cf819` |
| `research/manuscripts/methods-record/corrective-interpretations-2026-09-08.md` | 15,137 | `e77e8c8a0cccd1acc3633344f5fe250f4e5203cb181789eed185443ae700877c` | **21,655** | `6f921fa832de0f2d979c000ea73de36db12a41c4bb6d028090e6983ca1bdf7f3` |
| `…/MF1-repair/extract_mf1_inventory.py` | 36,960 | `446c4a65c5ffffe7927f1ff71a10e7c04074910c5f49b21c941096eca8835994` | **48,913** | `66049edd41124305467258aa224eb263215a1fee914e62e3f50557a797088de6` |
| `…/MF1-repair/MF1-dependency-manifest.json` | 4,349 | `c763bad95ef612e9ce330340db6539ea2fe552740a5a6e1e5978cd156cc42959` | **7,287** | `e95c925e0e1cb36419122a58a4277e3beff5e5e44d3fa3d822d122a9e3f14773` |
| `…/MF1-repair/MF1-instrument-inventory.md` | 14,660 | `42c199d37b2952909db51fbb9ee40986fee79fcf8d7604448bac64071fc51065` | **25,317** | `4be846b1317f567a2e07a947a39e851acbbf42a3b08d2abbacddac8d46bcc34e` |
| `…/MF1-repair/MF1-quantitative-results.md` | 9,406 | `2662ead3d470517ff0f88b9fb608808ca5814d534388c57833f778660da7e751` | **9,897** | `62bf3d41fd8a9d025d859a863c35caed315d8b230395644162af9ba3244bc530` |

⭐ **The last four were written by the one admitted MF1 extraction**, not by hand. The SI carries a
`DO-NOT-HAND-EDIT` banner and was not hand-edited: every change in it comes from the generating script.

## Files deliberately NOT written

| file | bytes | sha256 | why |
|---|---:|---|---|
| `research/manuscripts/nr4a3-program-map.md` | 618,584 | `c4c60cec16984c62d8861f145971433a8daa5d3d89c366cafee07e15b31a6663` | **parent-owned shared file** — verified byte-identical before and after this batch. The exact correction is filed unapplied at `patches/0001-roadmap-four-live-residues.patch`. |
| `research/modalities/instrument-census.json` | 30,692 | `8abe8d50c83b0a70a09b2fb5056668643c4fa265abf87252237913693de39722` | **generated, never hand-edited**, and shared. It changes only when the roadmap changes and the census is regenerated — the one admitted census update was **not spent** (see `patches/README.md` step 2). |
| `research/modalities/instrument-census.md` | 21,835 | `7e83fdd29f6757905497327ec607f198c111593f5409c9bb0677747f61a7d473` | same, generated view. |
| `systems/graph/publications.json`, `systems/views/*` | — | — | parent-owned; P1/P2 and the view regeneration already landed at `a6a21fc5…`. Not reapplied. |
| `MF1-repair/patches/CURRENT-SUMMARY-PATCHES.md` | 11,940 | `d455f14daabe8937c26233c74ebc05e28bd011d52b3a137c5339de713074658a` | its verified identity is cited in the intake and the integration record. Its false "no regeneration needed" instruction is superseded **beside** it, in `DATED-SUPERSESSIONS-of-retained-package-notes.md`. |
| `MF1-repair/checks/*` and `MF1-repair/checks/README.md` | — | — | retained original execution streams. **Nothing was rerun, replaced or relabelled.** The README's two inaccurate summary statements are corrected beside it, not in it. |
| `MF1-integration-record/originals/*` | — | — | the surviving b577 originals (1,472 B stdout, 0 B stderr, exit `0`, 4,498 B target pairs). Untouched. |

## Exact final source identities read by the extraction

The one admitted extraction recorded **18 inputs at commit `8f1fe1c5e548dd016c21329d99a16e2db6d9719a`**,
and — new in this batch — verified that the bytes it actually read match the `HEAD` blob at the same path
for **18 of 18** inputs (`n_inputs_not_bound_to_head_blob: 0`). The per-input path, byte count,
working-tree SHA-256, git blob id, `head_blob_sha256` and `bytes_match_head_blob` are in
`…/MF1-repair/MF1-dependency-manifest.json`.

⛔ **These are working-tree and version-control identities in this repository. No immutable public
archive or release has been created or checked, and none is claimed.**
