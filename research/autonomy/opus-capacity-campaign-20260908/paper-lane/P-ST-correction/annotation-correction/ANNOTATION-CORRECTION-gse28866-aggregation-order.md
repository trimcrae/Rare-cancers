# Annotation correction: the GSE28866 aggregation-order annotation contradicts the code that wrote it

**Finding:** P-ST-F03. **Owner:** P-ST correction lane, 2026-09-08.
**Status: SPECIFIED, NOT APPLIED.** This lane holds no write authority outside its own directory and no
commit authority. The two edits below are byte-exact and ready for the integrating owner to apply.

## What is wrong

`research/modalities/gse28866-tumour-vs-normal.json` → `per_gene._contrast` reads, verbatim:

> `Median across a gene's 3SEQ peaks, then median across libraries in each arm. EMC n=4; normals n=27 (bowel/breast/colon/kidney/lung/uterus); other sarcomas = DDLPS, ESS, EWS, GIST, LMS, MLPS, SS.`

That names the **reverse** of the order the producing code implements. In
`research/modalities/gse28866_tumour_vs_normal.py`, `_extract` builds, for each gene, a list of peaks
where each peak carries the per-library value lists for the three arms, and then reduces:

```
    for g, peaks in per.items():
        e = [med(p[0]) for p in peaks if p[0]]     # per PEAK: median across the libraries in the arm
        n = [med(p[1]) for p in peaks if p[1]]
        s = [med(p[2]) for p in peaks if p[2]]
        out[g] = {"n_peaks": len(peaks), "emc_median": med([x for x in e if x is not None]),
                  ...                                     # then: median across the gene's peaks
```

So the implemented order is **median across the libraries in an arm for each peak, then median across
that gene's peaks** — which is what the manuscript's phrase "medians of per-peak medians" describes, and
what `_calibrate` (same file, `e = med([med(p[0]) for p in peaks if p[0]])`) also does. The two orders do
not generally commute, particularly with even-length medians, so the annotation is not a harmless
paraphrase: it is a wrong provenance statement sitting beside correct numbers.

The annotation is also the **only** place the deposit's scale transformation could have been recorded at
the point of use and is not. The retained GEO series record
(`research/modalities/geo-gse28866-brunner-series.json` → `series_record.overall_design`) states,
verbatim: *"Expression data was normalized using the sequencing depth of each sample by scaling the data
using the mean value of each sample. Data was further compressed to reduce outliers by taking the square
root of each value."*

## What must not happen

- ⛔ **No numeric value changes.** `per_gene.values`, `n_peaks`, every median and every calibration
  percentile stay exactly as they are. This is an annotation repair, not a recomputation.
- ⛔ **The producer is not re-run** and no output is regenerated. Re-running would overwrite an original
  execution record that this correction batch is required to preserve.
- ⛔ The original execution artifact is not rewritten in a way that erases what it said. Edit 2 below
  therefore **adds** the corrected annotation and **retains** the superseded string verbatim in the same
  object, so the original text stays quotable inside the artifact that carried it.

## Edit 1 — the generator, so a future run emits the correct order

File: `research/modalities/gse28866_tumour_vs_normal.py` (string literal at approximately line 475).

Replace, exactly:

```python
                "_contrast": ("Median across a gene's 3SEQ peaks, then median across libraries in "
                              "each arm. EMC n=4; normals n=27 (bowel/breast/colon/kidney/lung/"
                              "uterus); other sarcomas = DDLPS, ESS, EWS, GIST, LMS, MLPS, SS."),
```

with, exactly:

```python
                "_contrast": ("For each 3SEQ peak, the median across the libraries in an arm; then "
                              "the median across that gene's peaks. This is the order _extract "
                              "implements; the reverse order was stated here in error and does not "
                              "commute with it. Values are the deposit's own depth/sample-mean "
                              "normalized scores AFTER a square-root compression applied by the "
                              "depositors (see geo-gse28866-brunner-series.json, "
                              "series_record.overall_design), so they are compressed summary scores "
                              "and NOT linear abundances; a ratio of them is not a fold change and "
                              "squaring it does not recover one. EMC n=4 libraries; normals n=27 "
                              "libraries (17 adult, 10 fetal; bowel/breast/colon/kidney/lung/"
                              "uterus, unequally weighted); other sarcomas = 32 libraries from 30 "
                              "specimens (DDLPS, ESS, EWS, GIST, LMS, MLPS, SS; two specimens "
                              "contribute duplicate libraries)."),
```

## Edit 2 — the artifact, as an additive annotation repair

File: `research/modalities/gse28866-tumour-vs-normal.json`, object `per_gene`.

Set `per_gene._contrast` to the same corrected text as Edit 1, and **add** these two sibling keys so the
superseded statement remains readable in place:

```json
"_contrast_superseded_2026-09-08": "Median across a gene's 3SEQ peaks, then median across libraries in each arm. EMC n=4; normals n=27 (bowel/breast/colon/kidney/lung/uterus); other sarcomas = DDLPS, ESS, EWS, GIST, LMS, MLPS, SS.",
"_annotation_correction_2026-09-08": "ANNOTATION ONLY. The reduction order stated in the superseded string is the reverse of the order _extract implements, and the deposit's square-root compression was not stated at the point of use. No value in this file was recomputed, no producer was re-run and no measurement changed; only the provenance annotation was repaired. Finding P-ST-F03 of FINAL-SCIENTIFIC-REVIEW-P-ST.md (sha256 6dd9fd532e853d3ac5b1d8605dad79d585bdd1356598cc407eef8415adc4cf1a)."
```

## Verification the integrating owner should run after applying

1. `python3 -c "import json;d=json.load(open('research/modalities/gse28866-tumour-vs-normal.json'))"` —
   the file still parses.
2. Compare `per_gene.values` before and after byte-for-byte; the diff must touch only the three
   `_contrast*` / `_annotation_correction*` keys.
3. `research/autonomy/opus-capacity-campaign-20260908/paper-lane/P-ST-correction/execution/check_pst_correction.py`
   re-run: `tableS6-sequencing-bindings` must still pass, which is what proves no value moved.

## Current state, measured

As of this lane's HEAD read (`c6d97dcc2043bd2a21c749339637286915a29a82`), neither edit is applied. The
artifact still carries the superseded `_contrast` string, and
`research/modalities/gse28866-tumour-vs-normal.json` has sha256
`ac0a17bd81dd8bc2ecc3b5bb380de5ae00921ae2d32b5a9595bd1449720be407` (27,256 bytes) — the bytes the
revised manuscript's Table S6 values were checked against — and
`research/modalities/gse28866_tumour_vs_normal.py` has sha256
`6dcea81de63a4dd9ab66f39144b2ba531351efd9f1a8d51b233388456bfbdb78` (30,914 bytes). Both hashes were
measured with `sha256sum` in this lane, not carried over from any earlier record.
