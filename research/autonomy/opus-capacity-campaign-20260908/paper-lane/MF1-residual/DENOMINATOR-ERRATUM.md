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
| the focused post-repair verification (`FOCUSED-SCIENTIFIC-VERIFICATION-MF1.md`, R4) | identified the split and stated *"the SI's 18 is correct for the combined prefixes"* | ⭐ **correct** — this is the finding being implemented. |
| the root adjudication memo (`MF1-focused-residual-root-adjudication-20260908.md`) | carried the correction, and separately transposed several reference/result pairs (see `BENCHMARK-FACTS.md`) | left **immutable**; the transposition is recorded, not edited. |
| the manuscript, §9.4 (`M:702` in the pinned text) | *"finds **17** final per-leg readout records"* for the combined census | ⭐ **corrected in this batch.** |
| corrective interpretation **C7** | *"17 `leg_result` records"* for the combined census | ⭐ **corrected in this batch**, with the original mistaken sentence quoted inside the erratum block so the supersession is visible at the record. |
| the generated supplement, S1 covalent row | **18** | ⭐ **it was right all along** — the extraction sums the two survey counts (`n_leg = sum(...)`). The supplement is now also explicit about the split. |

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
