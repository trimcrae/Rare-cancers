# FO candidate — figure/estimand mismatch carried forward for adjudication

**Date 2026-09-08. Carried at root's instruction. NOT resolved here, and no figure was redrawn.**

⚠ **The record root named does not exist.** There is no fusion-output (FO) candidate handoff in this
lane — the seven handoffs present are ATR, FP (two), biomarker, HLA, mortality and endpoint. Rather
than defer the item or invent a container for it, it is filed here as a standalone adjudication
record for the FO candidate, and this paragraph is the named gap.

## The mismatch, re-derived by the parent

**The figure label carries a denominator the manuscript has already corrected.**

- `research/modalities/nr4a3_fusion_targets_figures.py:354` — the `fig_matrix` 3SEQ column header
  still reads `"3SEQ cohort\nratio · percentile of 14,120 genes"`.
- `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md:315-316, 612-613`
  distinguishes three quantities: **14,120** genes present in the deposit, **13,708** with a
  computable EMC/normal ratio, **13,247** with an EMC/sarcoma ratio.
- The manuscript's own correction register, line 1329, records this **as already corrected on
  2026-09-08**: *"14,120 is the number of genes in the deposit, not the number ranked. The
  percentile distributions exclude any gene whose comparator median is zero, so the denominators
  are 13,708 on the EMC/normal axis and 13,247 on the EMC/sarcoma axis
  (`gse28866-tumour-vs-normal.json` → `ratio_calibration.n_genes_with_a_{normal,sarcoma}_ratio`).
  Each site now states the scope its own number was computed on. No percentile changed."*

So the prose was repaired and the figure label was not. The figure states a percentile against a
denominator the paper itself says is not the number ranked.

## What is NOT established

⛔ **Nobody has looked at the rendered figure.** This is a reading of the generator's source text
against the manuscript's source text. Neither root nor the parent has visually inspected the
committed `fig2`/`fig_matrix` pixels in this heartbeat, and **it is not claimed that the rendered
image shows this label** — the generator could have been edited after the last draw. That is
precisely one of the things adjudication has to settle.

⛔ The figure-provenance source-equivalence entry recorded today does **not** cover this. That entry
establishes only that the two occupancy fields the figures read are unchanged across `143d7f3f6`. It
is explicitly not proof that any label, plotted value or estimand is correct, and it says so.

⛔ No percentile value is disputed. The register states no percentile changed; this is about the
denominator a label names.

## What adjudication needs

1. Whether the committed rendered figure actually displays "14,120" — read from the artifact, not
   from the generator source.
2. Which denominator that column's values were computed against — the definition in
   `gse28866-tumour-vs-normal.json` → `ratio_calibration`, not an inference from the label.
3. Whether the fix is a label correction, a per-axis split (the two axes have different
   denominators, and one column header can only name one), or no change because the column is
   already computed on the deposit and the label is right for it.

⛔ **No redraw, no figure producer run, no fresh whole-paper review, and no new source retrieval
follows from this item.** Root admitted it as a carry-forward for adjudication and nothing more.
