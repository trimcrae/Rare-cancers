---
id: DOC-OPUS-CAMPAIGN-PST-CURRENT-PACKET
title: "P-ST current package binding (R7) — the revised pair, its baselines, its source locator and the applied F03 receipt"
level: L4
kind: package-binding
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# P-ST current package binding — R7, 2026-09-08

This is a **dated addition beside** `../P-ST-correction/packet/PACKET-MANIFEST.json`, not a rewrite of
it. Where the two disagree, this document states the current identities and the manifest remains valid
as the historical record of what was checked on 2026-09-08 at repository HEAD `a6a21fc5`.

## 1. CURRENT — the revised main and SI

Written 2026-09-08 by the sole admitted residual author. Candidate and canonical copies are
byte-identical (verified, `checks/RUN-06-integrate`, exit 0, and `checks/RUN-11-residual-integrity`
check `R7-current-pair …`, exit 0).

| Role | Exact path | Bytes | SHA256 |
|---|---|---:|---|
| **Current main** | `research/manuscripts/surface-targets/emc-surface-target-landscape.md` | 146,042 | `371ec8d92c3238b09f2117e14613184c422db1f094e83f431bad07d46e93179e` |
| **Current SI** | `research/manuscripts/surface-targets/emc-surface-target-landscape-si.md` | 56,124 | `290212776b2f103d64a270f12936245be00bfc6c97f5678b492589bc3680ad16` |
| Candidate copy of current main | `research/autonomy/opus-capacity-campaign-20260908/paper-lane/P-ST-correction/revised/emc-surface-target-landscape.md` | 146,042 | `371ec8d92c3238b09f2117e14613184c422db1f094e83f431bad07d46e93179e` |
| Candidate copy of current SI | `…/P-ST-correction/revised/emc-surface-target-landscape-si.md` | 56,124 | `290212776b2f103d64a270f12936245be00bfc6c97f5678b492589bc3680ad16` |

**Pin.** These bytes were produced in the working tree of branch `claude/confident-bardeen-ji76cd` on
2026-09-08 and are **uncommitted at the time of writing**: no commit, push or preflight was run from
this lane, and the parent integrates. The delivery pin of the pre-residual candidate these were derived
from is **`b57754a83524f95240995edf32621aca408e4587`**; the retained execution record of the F01–F13
batch names repository HEAD **`a6a21fc591d2451038cdf53449b91e3990d59cfb`** at its final check. No new
commit identifier is claimed here, and none should be quoted until the parent creates one.

## 2. HISTORICAL INPUTS — the baseline pair and the pre-residual candidate

These remain valid historical inputs. They are not superseded evidence; they are what the reviews read.

| Role | Retained at | Bytes | SHA256 |
|---|---|---:|---|
| Baseline main (what the original review read) | `…/P-ST-correction/frozen/emc-surface-target-landscape.md`; also `PST-residual/BEFORE-2026-09-08/canonical--…` and Git history | 99,615 | `8931895d65bf6cc7de0d83b8cbd6c644b3eb664de221b56861a2a0940584df6f` |
| Baseline SI | `…/P-ST-correction/frozen/emc-surface-target-landscape-si.md`; also `BEFORE-2026-09-08/canonical--…` and Git history | 41,853 | `92a7c49fc406a391d519912108fe888dc499c635ec29d1c3f834445665cdafd1` |
| Pre-residual candidate main (what the focused verification read) | `PST-residual/BEFORE-2026-09-08/revised--emc-surface-target-landscape.md` | 132,856 | `ebce0a9db28d3c5a7187a10005fc73b5666232a20a1cd110fa74c59d58bee6e3` |
| Pre-residual candidate SI | `PST-residual/BEFORE-2026-09-08/revised--emc-surface-target-landscape-si.md` | 54,084 | `105fc8732dfdb367b6793932b663815f74ae76ea483c1c1daf5a40991794a368` |

The two `PACKET-MANIFEST.json` manuscript entries are the **99,615 / 41,853-byte baseline pair**. Those
entries are correct as history and are **superseded as a statement of the current manuscript** by
section 1 above. The manifest is left byte-unchanged.

## 3. The already-held GEO source locator

| Item | Value |
|---|---|
| Exact path | `research/autonomy/opus-capacity-campaign-20260908/paper-lane/PST-source-locators/geo_esummary_emc.txt` |
| Bytes | 30,740 |
| SHA256 | `1726d018625bd4d4afdadd9364a7447d650ae5c88e9a2c228fe4463845aaac0c` |
| Git blob (as recorded by the focused verification) | `64621bda29a49a155b08d00c5e407a59a53c9481` |
| Original path | `literature/ct-reverify-c3b-2026-08-07/geo_esummary_emc.txt` |

Verified in place, not reacquired: `checks/RUN-11-residual-integrity`, check `R7-esummary-locator`,
exit 0. **Nothing was fetched, and no source was reacquired anywhere in this batch.**

**What it provides.** The compact JSON at line 6 carries sample titles and publication links, supporting
GSE24369 → PMID 21536545, GSE28866 → PMID 22929540, GSE4303 → PMID 15920699, and the GSE24369
myxofibrosarcoma sample titles.

**What it does not provide.** It is **not** an original probe-annotation audit, it does not supply the
blocked B4 PNAS supplement, and it does not supply independently inspected full texts of those three
publications. The manuscript's links are stated as links only.

**A public DOI is not a prerequisite.** The packet is local and versioned in the repository. No public
immutable release locator exists, none was created, and the manuscript says so.

## 4. The bound F03 applied receipt (R8) — the parent's act, not this author's

The sole integrating parent applied the admitted annotation-only F03 change **once, on 2026-09-08**,
before dispatching this lane. This author did **not** re-apply it and executed **no** producer,
normalisation, recalibration, inversion or renderer. The receipt, exact diffs, field map and execution
records are at
`…/P-ST-correction/annotation-correction/APPLIED-2026-09-08/APPLIED-RECORD.md`.

| File | Before bytes / SHA256 | **After — current** bytes / SHA256 |
|---|---|---|
| `research/modalities/gse28866-tumour-vs-normal.json` | 27,256 / `ac0a17bd81dd8bc2ecc3b5bb380de5ae00921ae2d32b5a9595bd1449720be407` | **28,606 / `386a035175d94ef8eccd3719d74ef39cff5e93461ed2470983777333a1962cee`** |
| `research/modalities/gse28866_tumour_vs_normal.py` | 30,914 / `6dcea81de63a4dd9ab66f39144b2ba531351efd9f1a8d51b233388456bfbdb78` | **31,856 / `404fe28582d9891a498b5407dc980e5ce7a16ac94a11eee267f7f6b7d8d4b46a`** |

Both "after" identities were re-measured on the live tree by this author
(`checks/RUN-11-residual-integrity`, checks `R8-receipt-binds …`, exit 0), and the three annotation
keys — the corrected `_contrast`, the verbatim `_contrast_superseded_2026-09-08` and the dated
`_annotation_correction_2026-09-08` — were confirmed present (check `R8-three-annotation-keys`).

The parent's invariance evidence is a **leaf-by-leaf comparison of the whole JSON in both directions**
— 669 leaves before, 671 after, 244 non-string; exactly two keys added, one value changed, none
removed, zero leaves moved outside the three annotation keys — **not** merely a six-entry Table S6 spot
check.

## 5. ⚠ `check_pst_correction.py` `packet-manifest-reproduces` now FAILS, correctly

Re-running the retained checker after this batch gives **52 passed, 2 failed, exit 1**
(`checks/RUN-08-pst-checker/`). The packet check names exactly four CHANGED entries:

* `research/modalities/gse28866_tumour_vs_normal.py` — changed by the **parent's F03 application**;
* `research/modalities/gse28866-tumour-vs-normal.json` — same;
* `research/manuscripts/surface-targets/emc-surface-target-landscape.md` — changed by **R7 integration**;
* `research/manuscripts/surface-targets/emc-surface-target-landscape-si.md` — same.

`PACKET-MANIFEST.json` is a **dated historical identity record of the pre-correction bytes and was
deliberately not rewritten**, so the check reports precisely the four files that changed and nothing
else. That containment is itself confirmation. **No check, matcher, floor or manifest was weakened to
obtain a pass.** `tableS6-sequencing-bindings` still **PASSES** — 6 genes, all match — which is the
binding that would move if any measured value had moved.

The second failure, `F11-sequencing-not-per-sample`, is a **limited hard-coded string check** and is
discussed in `RESIDUAL-LIMITATIONS.md`.

## 6. Reproduction boundary, as it now stands

* **Retrieval and recalculation available:** every array contrast, ordinary pointwise interval,
  within-platform Benjamini-Hochberg *q* and decision, the cross-platform states, the three recorded
  sensitivity summaries, the panel scores, and — from the retained **final gene-level sequencing
  medians** — retrieval of those medians with ratio and descriptive-band arithmetic over them.
* **Not available:** the **two-stage sequencing reduction** (median across libraries per peak, then
  median across a gene's peaks), because the per-library values and the separate per-peak arm medians
  are not retained; the surrogate scan's complete universe, per-line observations and *p*-value family;
  an audited probe-to-symbol chain; and the original peak table.
* `accession-symbol-cache.json` is **upstream mapping provenance** for the statistics generator's
  inputs, not a runtime dependency of that generator.
* The omitted Figure 1's original PNG remains untouched at
  `research/modalities/emc-surface-prioritization.png`, sha256 `130042b6…c439bd` (verified, exit 0).
