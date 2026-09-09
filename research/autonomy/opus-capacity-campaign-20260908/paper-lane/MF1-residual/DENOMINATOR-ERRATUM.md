---
id: DOC-MF1-RESIDUAL-DENOMINATOR-ERRATUM
title: "Erratum, 2026-09-08 — the covalent-panel result-object denominator is 17 + 1 = 18"
level: L4
kind: memo
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Erratum, 2026-09-08 — 17 is the first-prefix count; the combined total is 18

⛔ **This is a reviewer erratum AND a root erratum, not an author-only blame assignment.** The mistaken
combined figure originates in the independent final scientific review, was carried into the focused
verification's own framing of the finding, and was adopted by the root adjudication before the author
copied it into the manuscript and into corrective interpretation C7. All four records are named below and
all four stay **immutable**. This dated erratum stands beside them.

## The source, read directly

`research/modalities/nrv04-result-forensics.json` — a read-only object census over two named storage
prefixes:

| survey | field | value |
|---|---|---|
| `nrv04-covalent-results/` | `by_class.leg_result.n` | **17** |
| `nrv04-covalent-results-chainfix/` | `by_class.leg_result.n` | **1** |
| `nrv04-covalent-results/` | `recompute_verdict.trajectory_objects_found` (`:672`) | **0** |
| `nrv04-covalent-results-chainfix/` | `recompute_verdict.trajectory_objects_found` (`:1414`) | **0** |

**17 + 1 = 18 stored result objects across both surveyed prefixes, with zero multi-frame coordinate
objects in either.**

## Who said what

| record | what it said | status |
|---|---|---|
| the original independent final scientific review | **17** for the combined two-prefix census | ⛔ **wrong, and it is the origin of the error.** Its 17 is the first-prefix count generalised to both surveys. Left immutable. |
| the **first** root adjudication of that review (**6,673 B**, in the final-review capsule) | carried the review's **17** forward as the combined count | ⛔ **also wrong, and it is a root error, not the focused report's.** Left immutable. |
| the focused post-repair verification (`FOCUSED-SCIENTIFIC-VERIFICATION-MF1.md`, R4) | identified the split and stated *"the SI's 18 is correct for the combined prefixes"* | ⭐ **correct, and it is where the correction originates: 17 + 1.** ⛔ The focused report did **not** originate the 17-count error and must not be blamed for it. |
| the **later** root residual memo `MF1-focused-residual-root-adjudication-20260908.md` (**6,819 B**, sha256 `ecb01e1c…23d677ce2`) | states the combined total as **18** | ⭐ **correct.** Left immutable. |
| the manuscript, §9.4 (`M:702` in the pinned text) | *"finds **17** final per-leg readout records"* for the combined census | ⭐ **corrected in this batch.** |
| corrective interpretation **C7** | *"17 `leg_result` records"* for the combined census | ⭐ **corrected in this batch**, with the original mistaken sentence quoted inside the erratum block so the supersession is visible at the record. |
| the generated supplement, S1 covalent row | **18** | ⭐ **it was right all along** — the extraction sums the two survey counts (`n_leg = sum(...)`). The supplement is now also explicit about the split. |

## ⭐ CORRECTED 2026-09-09 — the transposition is NOT the root memo's

An earlier row of the table above said the root adjudication memo *"carried the correction, and
separately transposed several reference/result pairs"*. ⛔ **That attribution was wrong and is
withdrawn.** The measured position, which `BENCHMARK-FACTS.md` now states and which this file
adopts:

- The **6,819 B root residual memo** (sha256 `ecb01e1c…23d677ce2`) gives all five benchmark pairs
  **in source order — reference first, then result** — and is **correct**.
- The transposition was introduced **downstream**, in the derived **9,259 B**
  `CONTRACT-MF1-R1-R5-residual-author.md` (sha256
  `4f93302c8e335415e48ddf8b92ed0a4dab01d38306c313888233193e5d9e37e4`), which swapped the
  "reference" and "result" column headings while copying the memo's values. That contract was
  written by the integrating parent.
- The corrected `BENCHMARK-FACTS.md` (8,278 B, sha256
  `5c717270cfe1de723d5fa3faf044885a472b079cad544dd273abdbba3fbef4d8`) already carries this
  repair, together with the withdrawal of the invalid symmetric-absolute-error argument and of the
  invented quotations. ⭐ **That correction is accepted and is not redone here.**

⛔ Three separate things, kept separate: (1) the **count-17 mistake**, which originates in the
independent final review and was carried by the **first 6,673 B** root adjudication; (2) the
**focused report's 17 + 1**, which is the correction; (3) the **later 6,819 B** root residual
memo's **18**, which is right. None of these is the transposition, and the transposition is not any
of these.

⛔ No original record is edited by this correction. The review, both root memos, the focused report
and the contract stay **immutable**; this dated note stands beside them.

## What the corrected count does and does not mean

- ⛔ **18 STORED RESULT OBJECTS.** They are not 18 independent experiments, not 18 originally intended
  panel legs, and not a sample size.
- ⛔ **Nothing about the absent-coordinate conclusion changes.** `trajectory_objects_found` is **0** in
  both surveys, so the corrected-interface readouts still cannot be recomputed from what was retained
  under these prefixes.
- ⛔ **No newly discovered trajectory is implied**, and no new survey, re-run or object listing was
  performed for this erratum: the two counts were read from the retained JSON.
- ⚠ The conclusion remains scoped to the **two surveyed prefixes** and is not a proof about every possible
  external copy of the data.

## Where the correction now lives

- `research/manuscripts/methods-record/degrader-methods-failure-record.md` §9.4 — dated erratum in place.
- `research/manuscripts/methods-record/corrective-interpretations-2026-09-08.md` **C7** — dated erratum
  block beside the original wording, which is quoted rather than deleted.
- `research/manuscripts/methods-record/degrader-methods-failure-record-SI.md` S1 — the per-prefix split is
  now shown, generated from the source fields.
- This file.
