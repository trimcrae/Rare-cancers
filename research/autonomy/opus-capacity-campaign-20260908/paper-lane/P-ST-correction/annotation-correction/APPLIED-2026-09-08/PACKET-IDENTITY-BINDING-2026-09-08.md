---
id: DOC-OPUS-CAMPAIGN-PST-PACKET-IDENTITY-BINDING
title: "P-ST packet identity binding — current bytes, 2026-09-08"
level: L4
kind: binding
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# P-ST packet identity binding — current bytes

**Additive. `PACKET-MANIFEST.json` is NOT edited and NOT regenerated**, and the
`packet-manifest-reproduces` failure it produces is **preserved unchanged**. That manifest is a dated
historical identity record of the pre-correction bytes; this file is the **current** binding beside
it. Neither replaces the other.

## Why the manifest check fails, entry by entry

`check_pst_correction.py` reports **52 passed, 2 failed**, `packet-manifest-reproduces` naming
exactly four CHANGED entries. **All four are intended, admitted changes**, and none is a defect:

| entry | why it changed | admitted by |
|---|---|---|
| `research/modalities/gse28866_tumour_vs_normal.py` | the F03 producer string literal | F03, applied by the sole parent |
| `research/modalities/gse28866-tumour-vs-normal.json` | the F03 `_contrast` + two dated annotation keys | F03, applied by the sole parent |
| `…/emc-surface-target-landscape.md` | the R1–R8 residual batch | P-ST residual admission, R7 |
| `…/emc-surface-target-landscape-si.md` | the R1–R8 residual batch | P-ST residual admission, R7 |

**The check is right and is left failing.** A manifest that reproduced after an admitted correction
would mean the correction had not landed.

## Current identities, measured 2026-09-08

| path | bytes | sha256 |
|---|---:|---|
| `research/modalities/gse28866-tumour-vs-normal.json` | 28606 | `386a035175d94ef8eccd3719d74ef39cff5e93461ed2470983777333a1962cee` |
| `research/modalities/gse28866_tumour_vs_normal.py` | 31856 | `404fe28582d9891a498b5407dc980e5ce7a16ac94a11eee267f7f6b7d8d4b46a` |
| `research/manuscripts/surface-targets/emc-surface-target-landscape.md` | 146042 | `371ec8d92c3238b09f2117e14613184c422db1f094e83f431bad07d46e93179e` |
| `research/manuscripts/surface-targets/emc-surface-target-landscape-si.md` | 56124 | `290212776b2f103d64a270f12936245be00bfc6c97f5678b492589bc3680ad16` |

Pre-correction identities for the two F03 files are in `APPLIED-RECORD.md` and in the retained
`BEFORE-*` byte copies; the pre-residual manuscript identities are in `PST-residual/`. Both remain
valid as history.

## ⚠ One cited identity is NOT resolvable in this worktree

The `_annotation_correction_2026-09-08` key attributes the finding to
`FINAL-SCIENTIFIC-REVIEW-P-ST.md`, sha256
`6dd9fd532e853d3ac5b1d8605dad79d585bdd1356598cc407eef8415adc4cf1a`.

**That file is not present in this repository under that name.** The hash is cited consistently
across five lane documents, so the citation is internally coherent, but the artifact itself lives in
the reviewer's packet and was never transported here. It is therefore **an identity, not a
retrievable source, from inside this checkout.**

⛔ I did **not** invent a locator for it, and I did **not** alter the annotation key to remove or
soften the citation — the key stays exactly as admitted. The limitation is recorded here instead.

## The second failure is out of this correction's scope

`F11-sequencing-not-per-sample` fails because the check **hard-codes the literal phrase**
*"group-level peak summaries and not per-sample values"* — the exact wording the P-ST residual R4
required replacing. That is a stale matcher pinned to retired prose, **not** a defect in the
annotation, the producer literal or the packet binding, and it is outside the admitted scope of this
correction.

⛔ **The check was not edited, relaxed, or rescoped**, and no guard criterion was changed. Its
artifact half was independently re-verified by the P-ST residual author: 19 genes, `n_peaks` plus
three arm medians, and **no per-sample, per-library or per-peak field** — so the artifact does store
grouped summaries, exactly as the check's substance requires. Only the check's frozen sentence no
longer matches the manuscript's current wording. Recorded, and left for its owner.

## Verification re-run at this state

`verify_applied.py` — **exit 0, 9 of 9 PASS**, unchanged: 669 → 671 leaves, two keys added, one
value changed, none removed, **zero leaves moved outside the three annotation keys**; producer diff
one hunk inside the `_contrast` literal; module still **not executed**. No producer, renderer, new
calculation or regeneration was run for this binding.

The original `verify_applied.py` **RUN-01 EXIT=1** and the original
`packet-manifest-reproduces` failure stay exactly as recorded. **No retroactive success label is
applied to either.**
