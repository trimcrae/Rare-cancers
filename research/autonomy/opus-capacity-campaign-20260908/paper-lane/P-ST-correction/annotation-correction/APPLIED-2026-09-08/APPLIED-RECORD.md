---
id: DOC-OPUS-CAMPAIGN-PST-F03-APPLIED
title: "P-ST-F03 applied — the GSE28866 aggregation-order annotation repair, as executed"
level: L4
kind: applied-record
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# P-ST-F03 — APPLIED, 2026-09-08

Applied by the **sole integrating parent** under root's concrete admission of this date, from the
retained specification `../ANNOTATION-CORRECTION-gse28866-aggregation-order.md` as it stands at
`b57754a83524f95240995edf32621aca408e4587`, which root read in full before admitting it.

**Status: SPECIFIED → APPLIED.** This is an **annotation-only** repair. No producer was executed, no
output was regenerated, and no measured value changed.

## The immutable binding

| file | before bytes | before sha256 | after bytes | after sha256 |
|---|---|---|---|---|
| `research/modalities/gse28866-tumour-vs-normal.json` | 27,256 | `ac0a17bd81dd8bc2ecc3b5bb380de5ae00921ae2d32b5a9595bd1449720be407` | 28,606 | `386a035175d94ef8eccd3719d74ef39cff5e93461ed2470983777333a1962cee` |
| `research/modalities/gse28866_tumour_vs_normal.py` | 30,914 | `6dcea81de63a4dd9ab66f39144b2ba531351efd9f1a8d51b233388456bfbdb78` | 31,856 | `404fe28582d9891a498b5407dc980e5ce7a16ac94a11eee267f7f6b7d8d4b46a` |

Both **before** hashes were measured on the live tree immediately before the edit and match the
values the specification recorded. The retained byte copies are `BEFORE-*` in this directory and are
re-hashed by `verify_applied.py` (`V1`, `V2`).

Exact applied diffs: `DIFFS/gse28866-tumour-vs-normal.json.diff` (15 lines; **1 value replaced,
2 keys added**) and `DIFFS/gse28866_tumour_vs_normal.py.diff` (27 lines; **one hunk**, 3 source lines
→ 13, entirely inside the `"_contrast"` string literal).

## Field map — exactly what moved

| path | before | after |
|---|---|---|
| `$.per_gene._contrast` | the reverse-order string | the corrected order + the deposit's square-root compression, stated at the point of use |
| `$.per_gene._contrast_superseded_2026-09-08` | *(absent)* | the superseded string, **verbatim**, so it stays quotable inside the artifact that carried it |
| `$.per_gene._annotation_correction_2026-09-08` | *(absent)* | the dated ANNOTATION-ONLY note naming finding P-ST-F03 |
| `gse28866_tumour_vs_normal.py` `"_contrast"` literal | the reverse-order string | the same corrected text as the JSON |

**Nothing else.** No other key, value, ordering, membership or byte.

## Invariance — measured, not assumed

Root's instruction was explicit that **a Table S6 pass alone is not evidence of all-value
invariance**, so the JSON was compared leaf by leaf in both directions rather than spot-checked:

* **669 leaves before, 671 after**; **244 of the 669 are non-string**.
* added `= {$.per_gene._contrast_superseded_2026-09-08, $.per_gene._annotation_correction_2026-09-08}`
* removed `= {}` · changed `= {$.per_gene._contrast}`
* **0 leaves moved outside the three annotation keys, in either direction.** `per_gene.values`,
  `n_peaks`, every median and every calibration percentile are byte-identical.
* Top-level key order identical; the two dated keys were inserted **in place** after `_contrast`.
* The writer format was proven **byte-exact round-trip** (`indent=2`, `ensure_ascii=False`, trailing
  newline) on the untouched original **before** any edit, so the file was not reformatted.
* The producer diff is **one contiguous hunk**, every line of it inside the `_contrast` literal, and
  the module still `ast.parse`s. **It was not executed.**

## Executions — real commands, real exits, every attempt

| run | command | exit |
|---|---|---|
| `checks/APPLY-stdout.txt` | `python3 apply_pst_f03.py` | **0** |
| `checks/RUN-01-verify-FAILED/` | `python3 verify_applied.py` | **1** — PRESERVED FAILURE: my `ROOT` walked 5 parent directories where the path needs 7, so the live files could not be opened. A check that cannot recompute its quantity must fail, and it did. |
| `checks/RUN-02-verify/` | `python3 verify_applied.py` | **0** — 9 of 9 pass (V1–V9 above) |
| `checks/RUN-03-pst-check/` | `python3 …/check_pst_correction.py . …/revised …/packet/PACKET-MANIFEST.json` | **1** — see below |

## ⭐ The expected, correct failure in RUN-03

`check_pst_correction.py` reports **53 passed, 1 failed**:

* ✅ `tableS6-sequencing-bindings` — **6 genes; all match.** This is the binding that would move if
  any value had moved. It did not.
* ⛔ `packet-manifest-reproduces` — **25 entries**, naming exactly
  `research/modalities/gse28866_tumour_vs_normal.py CHANGED` and
  `research/modalities/gse28866-tumour-vs-normal.json CHANGED`.

That failure is **correct and is being left in place.** `PACKET-MANIFEST.json` is a **dated
historical identity record** of the pre-correction bytes — the bytes the revised manuscript's Table
S6 values were checked against. Editing it to absorb this correction would rewrite original evidence
to turn a check green. It names precisely the two files this admission changed, and nothing else,
which is itself confirmation that the change was contained.

**Current annotation authority, stated here rather than by overwriting history:**

> As of 2026-09-08, the authoritative current bytes of these two files are the **after** hashes in
> the binding table above. `PACKET-MANIFEST.json` and every other dated packet or frozen artifact
> continue to record the **before** identities, and remain valid as history of what was checked when.

## What this correction does and does not say

It says: the annotation stated the reduction order backwards relative to the code that produced the
numbers, and the deposit's square-root compression was not stated where the values are used. Both are
now stated correctly, and the superseded text is retained verbatim beside them.

It does **not** rest on any new source. The aggregation order is established by the producer code
itself (`_extract`, and `_calibrate` in the same file), and the square-root scale by the already
retained GEO series record (`geo-gse28866-brunner-series.json`,
`series_record.overall_design`). **No new source was needed and none was sought.**

The specification's incidental remark that this annotation was the *only* place the scale could have
been recorded is **not carried forward as a claim** here, and nothing in this record depends on it.

This is a provenance repair inside one artifact and its producer. It is **not** whole-paper
acceptance, and it is separate from the pending P-ST focused scientific review.
