---
id: DOC-MF1-RESIDUAL2-IDENTITIES
title: "MF1 residual-2 — the one new extraction, its four output identities, and every file touched"
level: L4
kind: memo
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# The one new extraction — real execution record

Run **after** the display and template changes settled, as explicitly admitted. Raw streams are in
`checks/01-mf1-extraction-residual2/` (`command.txt`, `stdout.txt`, `stderr.txt`, `exit-code.txt`,
`head-commit.txt`), written by the run itself.

**Command**

```
python3 research/autonomy/opus-capacity-campaign-20260908/paper-lane/MF1-repair/extract_mf1_inventory.py
```

**Measured exit: `0`.  stderr: 0 bytes (empty file, not "no stderr captured").**

**stdout, verbatim**

```
results rows: 10
inventory rows: 22  route 4+16  census 22
manifest inputs: 18 at commit b58e0ed897cbc3efc62894518fb7661777c36592
inputs NOT bound to their HEAD blob: 0 of 18
author-current scope overrides: 4 (V11, V16, V20, V5)
result-display omissions applied: 1 of 1 declared (V5)
```

The last line is new in this batch and is the R1 disclosure: the source still carried the fragment,
and the display omitted it.

## ⭐ ALL FOUR output identities of this extraction

| # | output | bytes | sha256 |
|---:|---|---:|---|
| 1 | `…/MF1-repair/MF1-quantitative-results.md` | 9,897 | `62bf3d41fd8a9d025d859a863c35caed315d8b230395644162af9ba3244bc530` |
| 2 | `…/MF1-repair/MF1-instrument-inventory.md` | 27,463 | `eba262a828246be2370d4d0e204d74d3994c1e57e23a937d111a217f3430635f` |
| 3 | `…/MF1-repair/MF1-dependency-manifest.json` | 7,287 | `05c5d82b8acc5148e47a56e520b43dfc537f9521f9679846ba425ea22b73fe83` |
| 4 | `research/manuscripts/methods-record/degrader-methods-failure-record-SI.md` | 43,261 | `2f39caf7ea31179c8120fe243dd428c9ee35398147470161f00dc03f9f4079d6` |

⭐ **Output 4 is the SI.** It is written by `main()` alongside the other three; the claim that this
extractor "writes only the three `MF1-repair/` outputs" is false and is corrected (residue 3).

Output 1 is **byte-identical** to the settled `13-…` run (`62bf3d41…`): the results table carries no
inventory display and none of this batch's changes reach it. Output 3 differs from `489a12fa…` only
in the recorded binding commit; the input set, sizes and hashes are unchanged, and it still records
**0 of 18 unbound**.

## Every file this batch wrote

| file | before bytes / sha256 | after bytes / sha256 | by |
|---|---|---|---|
| `…/MF1-repair/extract_mf1_inventory.py` | 48,913 / `66049edd41124305467258aa224eb263215a1fee914e62e3f50557a797088de6` | **57,251** / `0ed74b49f2b3071de5061b1d4f71e2b3db9120de32a45426781fa2dc1efc16f0` | hand (R1, R2, R3, R5) |
| `…/methods-record/degrader-methods-failure-record.md` | 88,695 / `b5036d4fe44b8a5e55318a50ea0d961e5b19d4eb4a53802b9edb155ac3c12e31` | **91,275** / `6b38ac4e545c990c0317a52154e8c1e4cebfc4013b6a22ec0e4411faf69f530f` | hand (R2, R3, R5) |
| `…/methods-record/corrective-interpretations-2026-09-08.md` | 21,655 / `6f921fa832de0f2d979c000ea73de36db12a41c4bb6d028090e6983ca1bdf7f3` | **21,913** / `a0d8a4dd7dbfddcb2b3ceb465c7cee93e98357114556fc6700f1fbc6d48dcfba` | hand (R2) |
| `…/methods-record/degrader-methods-failure-record-SI.md` | 41,072 / `c4e2f1e969233888dafa99dfca1c457a59f3121e1073191532889152402de18c` | **43,261** / `2f39caf7ea31179c8120fe243dd428c9ee35398147470161f00dc03f9f4079d6` | **generated** (output 4) |
| `…/MF1-repair/MF1-instrument-inventory.md` | 26,385 / `484f2590e489b9291f6714011a4765f296f62936f068627f76fc19c3b97e2f9f` | **27,463** / `eba262a828246be2370d4d0e204d74d3994c1e57e23a937d111a217f3430635f` | **generated** (output 2) |
| `…/MF1-repair/MF1-dependency-manifest.json` | 7,287 / `489a12fa8fd8f77ef5fc367d20348aec705eef8ab41bd989ae3504aab5d2b1a4` | **7,287** / `05c5d82b8acc5148e47a56e520b43dfc537f9521f9679846ba425ea22b73fe83` | **generated** (output 3) |
| `…/MF1-residual/DENOMINATOR-ERRATUM.md` | 4,068 / (prior batch) | **6,154** / `ce1c37718120d5600d16ab50ad9dec8f4af7373364487bc4fb50b1ddc1a9fa4b` | hand (R4, additive) |
| `…/MF1-residual/R1-R5-CLOSURE-MAP.md` | 13,535 / (prior batch) | **14,304** / `c256420d16c94bd83ee657e8737156e2f7b3ee6fa347c7de9be9356b98870d4c` | hand (R4, additive) |
| `…/MF1-residual-2/*` | — | new this batch | hand |

The exact unified diff of all eight tracked files is `DIFFS/APPLIED-residual2-all-files.diff`.

## Files deliberately NOT written

| file | why |
|---|---|
| `…/PARENT-SHARED-PATCHES-2026-09-08/SETTLED-IDENTITIES-2026-09-08.md` | **parent-owned.** Byte-unchanged. The exact correction is filed **UNAPPLIED** at `patches/UNAPPLIED-0001-parent-settled-identities-four-outputs.diff` |
| `…/PARENT-SHARED-PATCHES-2026-09-08/APPLIED-RECORD.md` | parent-owned; its record is accurate as written and needed no change |
| `research/manuscripts/nr4a3-program-map.md`, `research/modalities/instrument-census*.{json,md}`, `systems/graph/publications.json`, `systems/views/*` | shared, parent-owned, generated. ⛔ Not regenerated, not hand-edited, not reapplied |
| `…/MF1-residual/patches/*`, `…/MF1-repair/patches/*`, all `checks/` from earlier runs, `…/MF1-residual/BEFORE-20260908/*`, `MF1-integration-record/originals/*` | retained originals of already-executed work. **Nothing rerun, replaced or relabelled**; corrections about them are filed beside them |
| any file outside this manuscript's lane (other lanes were running concurrently) | not this author's to touch |

⛔ No `git add`, `git commit`, `git push`, no preflight, no repository gate, no subagent.
⛔ These are working-tree and version-control identities in this repository. **No immutable public
archive or release has been created or checked, and none is claimed.**
