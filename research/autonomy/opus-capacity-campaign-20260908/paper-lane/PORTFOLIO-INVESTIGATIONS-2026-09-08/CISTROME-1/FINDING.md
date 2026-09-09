---
id: DOC-OPUS-CAMPAIGN-CISTROME-1-FINDING
title: "CISTROME-1 — is NR4A occupancy at RET distinguishable from background, and which panel loci pass?"
level: L4
kind: investigation-finding
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# CISTROME-1 — the whole locus panel against the file's own null

## Question

`emc-ret-cistrome.json` reports `empirical_p_vs_background` **only for RET**, although each of its
110 peaksets scores a 13-locus panel. Is NR4A occupancy at RET distinguishable from that file's own
background null at all, and **which loci in the panel actually pass** — with RET placed in the
panel's rank order rather than read alone?

## Merit rationale

The RET-inhibitor repurposing premise for EMC rests on RET being an NR4A3 target. The source file's
headline ("measured NR4A occupancy at the RET locus in 15 of 64 public experiments") is a
single-locus reading with no stated comparator inside the panel it already scored. Reading RET
*against its own panel* is the cheapest available test of whether that reading is a signal or a
sampling of a generically occupied promoter set. Patient relevance is direct and the contribution is
non-trivial precisely because a **negative** here narrows a repurposing lane before anyone spends on
it. **No efficacy, safety, selectivity, therapeutic-window or clinical-readiness claim follows from
occupancy; occupancy is not target validation.**

## Evidence gap this closes

The file stores, per peakset, `loci{13}` promoter (−10 k/+15 k) and gene-body window counts, a
`positive_control_verdict`, and a `background` summary of a 198–200-gene panel drawn from
`emc-atr-vulnerability-inputs.json` (seed 20260807). Nobody had read the twelve non-RET loci, and
nobody had asked whether the peaksets producing RET's low p-values recover a positive control at
all. **No new intersection was computed and no new dataset was fetched** — every count is read in
place from the source file.

## Step taken

`panel_null.py` reads the source in place, re-hashes it at the moment of use, and emits
`ret-cistrome-locus-panel-null.json`: per locus × peakset occupancy against the file's own panel
null, restricted to the **25 peaksets flagged `A KNOWN POSITIVE IS RECOVERED`**, with RET's
competition rank in each panel, plus three checks that can fail.

### Result 1 — RET is indistinguishable from a permuted locus label

Mean competition rank across the 25 positive-recovering peaksets (rank 1 = most promoter-window
peaks), against a 20 000-draw locus-label permutation null (mean 5.11, sd 0.54):

| locus | observed mean rank | permutation p |
|---|---|---|
| ENO3 (positive control) | 2.52 | 0.00005 |
| NR4A2 | 2.56 | 0.00005 |
| VEGFA | 2.64 | 0.00005 |
| NR4A1 | 3.40 | 0.00105 |
| NR4A3 | 3.96 | 0.0167 |
| **RET** | **5.04** | **0.45248** |
| NRTN | 5.84 | 0.91905 |
| SEMA3C | 6.40 | 0.9921 |
| GDNF | 6.56 | 0.9972 |
| KDR / PPARG | 6.68 | 0.99845 / 0.99905 |
| GFRA1 | 6.72 | 0.9991 |
| GFRA2 | 7.52 | 1.0 |

**RET ranks 6th of 13 and sits inside its own permutation null (p = 0.45).** The test is not blunt:
ENO3, NR4A2, VEGFA and NR4A1 clear it decisively in the same run.

### Result 2 — in every NR4A3 ChIP peakset that recovers a positive, RET has zero promoter peaks

All four NR4A3 ChIP peaksets (AciCC1, AciCC2, AciCC3, Parotid_Gland3; ZENODO1483691) give
`RET n_peaks_promoter_window = 0`, stored p = **1.0**. The only RET p-values below 0.05 among
positive-recovering peaksets come from **NR4A1 ChIP in Kasumi-1 (blood)**: SRX1653203@hg19
p = 0.005, SRX1653204@hg19 p = 0.0199, SRX1653204@hg38 p = 0.0151 — none in an EMC-lineage cell,
none of the assayed protein. In those peaksets the panel null is near-degenerate (only 0–3 of 200
panel genes reach RET's count), which is what makes the p small.

**Build instability across the 0.05 line:** the *same experiment* SRX1653203 gives p = **0.005** on
hg19 and p = **0.0503** on hg38 (counts 3 vs 2). A single reprocessing swaps the verdict.

### Result 3 — the positive-control filter is not assay-specific

Only **11 of 25** positive-recovering peaksets are an NR4A ChIP at all. The remainder are H3K4me3,
H3K27ac, CTCF and super-enhancer tracks, which mark active promoters generically and so recover
ENO3 by construction.

## Validation — three checks, each able to fail

| check | verdict | detail |
|---|---|---|
| 1 · RET's stored p reproduces | **PASS** | 103/103 peaksets with a `background` block reproduce `empirical_p_RET_vs_background` at 4 dp from `(n_panel_ge_RET_count + 1)/(n_panel_resolved + 1)`. The two named values reproduce digit for digit: REMAP2022_NR4A1 → **0.4472**; SRX092299@hg19 → **1.0**. No discrepancy; the run therefore continued past the stop condition. |
| 2 · no-positive peaksets show no enrichment | **FAIL — 4 violations, preserved** | Four of 78 `NO KNOWN POSITIVE RECOVERED` peaksets carry RET promoter-window peaks with p below 1.0: AciCC1_H3K27me3 (2 peaks, p = 0.1393), AciCC2_H3K27me3 (3, p = 0.0846), AciCC3_H3K27me3 (4, **p = 0.0398**), Parotid_Gland3_H3K27me3 (4, **p = 0.0448**). |
| 3 · locus-label permutation flattens the ranking | **PASS** | Under permutation every label's null mean rank converges to 5.109–5.124 (spread 0.0146 vs mean sd 0.5379), while observed means span 2.52–7.52. |

**Check 2's failure is itself the sharpest result.** Every violating peakset is **H3K27me3** — a
*repressive* mark, in a peakset that recovered no known positive — yet the file's own panel assigns
RET a nominally significant p as low as 0.0398. A low p against this panel therefore does not mean
NR4A occupancy; it means "more promoter-window intervals than a 200-gene comparison set", which a
silencing mark achieves. The check is recorded as failing and was not weakened to pass.

## Provenance

* Input `research/modalities/emc-ret-cistrome.json`, **1 469 536 bytes**, sha256
  `08b249ebb3d4f2d7ba468d0a482c63fa2f4968b620b0b923311c2cd210015da1`, hashed at the moment of use
  (attempt 02) and re-verified unchanged after the run. DISCOVERY-2 established no digest; this is
  the first recorded one.
* Windows, panel source, panel seed (20260807) and the `(ge+1)/(n+1)` convention are the source
  file's own, quoted into the artifact, not re-chosen here.
* Permutation seed 20260908, 20 000 draws, `random.Random`, recorded in the artifact.
* Attempts: `checks/01-panel-null/` (exit 0; check-3 flatness criterion miscoded against
  `(n+1)/2`, which competition ranking with ties does not centre on) and
  `checks/02-panel-null-rerun/` (exit 0; criterion corrected to label exchangeability, check-2
  diagnostic added). Attempt 01 is preserved in full. The artifact is attempt 02's output.

## Limitations

* The stored null retains only **two points** of each panel's count distribution (`#genes ≥ 1 peak`
  and `#genes ≥ RET's count`). An empirical p is therefore **exact only** where a locus's count is
  0, 1, or equal to RET's count in that peakset; every other locus is reported as a **bounded
  interval** from the monotone survival function. No point value was interpolated.
* The panel is not composition-matched for accessibility, mappability or GC — the source file says
  so and this inherits it.
* A window is a scope choice; an element outside −10 k/+15 k is untested by construction.
* The assayed protein is **wild-type NR4A**, never EWSR1::NR4A3, and never in an EMC tumour. No
  EWSR1::NR4A3 cistrome exists.
* Competition rank across a 13-locus panel is coarse; ties are frequent because most counts are 0.
* **Nothing here is an efficacy, safety, selectivity, therapeutic-window or clinical-readiness
  claim.** This does not establish that RET is *not* an EMC target — only that this evidence base
  does not distinguish it from background.

## Stop condition — reached

Stop was at the panel table. It is delivered. Result: **RET is not distinguishable from a permuted
locus label against this file's own null (p = 0.45), ranks 6th of 13, and reads zero in every
NR4A3 ChIP peakset that recovers a positive control.** The loci that do pass are ENO3, NR4A2,
VEGFA, NR4A1 and NR4A3. No further computation on this input can strengthen the RET reading; the
next credible independent step would require an EWSR1::NR4A3 cistrome in EMC-lineage cells, which
does not exist publicly and is out of scope here.
