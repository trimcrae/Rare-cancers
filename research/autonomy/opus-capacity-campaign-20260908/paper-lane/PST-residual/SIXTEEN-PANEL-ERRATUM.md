---
id: DOC-OPUS-CAMPAIGN-PST-SIXTEEN-PANEL-ERRATUM
title: "Erratum — sixteen scored panel contrasts, not seventeen"
level: L4
kind: erratum
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Erratum, 2026-09-08 — the panel count is SIXTEEN

## What is corrected

**There are 16 scored panel contrasts: NINE on GPL6244 and SEVEN on GPL3290.**

The superseded number is **17**. It was stated in the original P-ST scientific review (finding F10,
baseline report line 169), accepted by the adjudicating root, and carried into the first correction
batch's revised main text, SI and response map. The focused verification identified it and corrected
its own count in residual **R6**; the reviewer explicitly took responsibility for it and did not
attribute it to the correction author. This document is the dated erratum that sits beside the
original.

## The two unscored panels stay unscored

On **GPL3290** the following two panels carry `scored: false` in
`research/modalities/emc-tissue-read-statistics.json`, `panel_scores_with_p.rows`, because they fall
below the stored coverage floor of 3 readable genes and 0.5 coverage:

| Panel (artifact key) | Table S5 name | GPL3290 state |
|---|---|---|
| `somatostatin_receptor_family` | Somatostatin-receptor family | **no score: 1 of 5 readable, coverage 0.20** |
| `hla_presented_intracellular_antigens_NOT_surface` | HLA-presented intracellular antigens, not surface | **no score: 4 of 10 readable, coverage 0.40** |

Both remain unscored. **No score, test or p value has been added, computed or invented to make the
count seventeen**, and every existing panel value in Table S5 is unchanged — verified byte-identical
against the pre-residual candidate (`checks/RUN-11-residual-integrity`, `R6-panel-values-unchanged`,
10 table lines identical).

## How 16 was measured

By reading the stored `scored` flags in the retained artifact — no calculation:
`checks/RUN-02-panel-count/` (exit 0) and, re-run inside the residual check suite,
`checks/RUN-11-residual-integrity/` check `R6-artifact-scored-9-plus-7` (exit 0).

```
panels in artifact: 9
GPL6244 scored=9 unscored=0 unscored panels: []
GPL3290 scored=7 unscored=2 unscored panels: ['hla_presented_intracellular_antigens_NOT_surface', 'somatostatin_receptor_family']
SCORED CONTRAST TOTAL = 16
```

An earlier attempt at this count (`checks/RUN-01-panel-count-FAILED/`, exit 1) crashed on the
artifact's structure and is preserved as a failure rather than deleted.

## Every occurrence corrected

| # | File | Location | Was | Now |
|---|---|---|---|---|
| 1 | `research/manuscripts/surface-targets/emc-surface-target-landscape.md` (and the identical candidate) | Results, "Route-named therapeutic addresses", live prose (line 615 of the current file) | "the 17 available panel tests across the nine curated panels are uncorrected and exploratory" | "the **16 scored panel contrasts** across the nine curated panels — nine on GPL6244 and seven on GPL3290 — are uncorrected and exploratory", plus a sentence naming the two GPL3290 panels that emit no score and are therefore not tests |
| 2 | same file | Appendix A7 register row F10 (line 1438) | "The 17 available panel tests are exploratory and uncorrected, with differing membership and coverage between platforms." | The same sentence without the count, followed by a dated **⚠ Erratum, 2026-09-08** stating 16 = 9 + 7, naming both unscored GPL3290 panels, recording that the superseded number came from the review, and stating that no score or test was added |
| 3 | same file | New Appendix A8 register, row R6 (line 1462) | *(new)* | The superseded quotation `"The 17 available panel tests"` retained verbatim beside the corrected statement |
| 4 | `research/manuscripts/surface-targets/emc-surface-target-landscape-si.md` (and the identical candidate) | Table S5 caption (line 405) | "⚠ **The 17 available panel tests below are exploratory and uncorrected**" | "⚠ **The 16 scored panel contrasts below — nine on GPL6244 and seven on GPL3290 — are exploratory and uncorrected**" |
| 5 | same file | Supplementary Note S5, multiple-testing paragraph (line 673) | "so the 17 available panel tests are exploratory and uncorrected" | "so the 16 scored panel contrasts — nine on GPL6244 and seven on GPL3290 — are exploratory and uncorrected" |
| 6 | `../P-ST-correction/F01-F13-RESPONSE-MAP.md` | F10 response summary, line 169 | "The **17 available panel tests** are labelled exploratory and unadjusted…" | The original line is **retained verbatim** with a dated `⚠ SUPERSEDED 2026-09-08 — the count is 16, not 17` marker inserted immediately beside it, naming both unscored panels and pointing here |

The string `17 available panel` now survives in exactly one place in the whole pair: the retained
superseded quotation inside the dated Appendix A8 register row (verified by check
`R6-17-only-in-dated-register`, exit 0). It appears nowhere in live prose.

## What is *not* changed

The substantive qualification is unchanged: panel scores are **exploratory and uncorrected**, panels
are not entered into the gene-level Benjamini-Hochberg correction, no panel-level multiplicity control
was applied, membership and coverage differ between the platforms, and no joint replicability
false-discovery rate was estimated. No functional conclusion follows from any panel row. Every panel
Δ, *t*, *p* and coverage figure in Table S5 is exactly as it was.
