---
id: DOC-PORTFOLIO-INVESTIGATION-EXPR-COMPOSITION-PREREG-20260909
title: "EXPR-COMPOSITION — frozen marker list, seed and analysis rules, written before any statistic was read"
level: L4
kind: preregistration
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: EXPR-COMPOSITION
continues: KINASE-2
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# EXPR-COMPOSITION — preregistration

Written **2026-09-09T01:0xZ**, before any statistic, correlation, t value or concordance rate from
this lane was computed or read. What had been read at the time of writing: the shared contract, the
FOLLOWTHROUGH-DISCOVERY rank-1 proposal, `../KINASE-2/FINDING.md`,
`../KINASE-2/label_permutation_null.py`, and a **presence-only** probe of the input artifact
(gene symbol present / `readable` flag / number of per-sample rows / arm sizes). No z value, t
value, correlation or rate was inspected. Repo HEAD at lane start: `1e35538daee86e1a34345340f7562d1e91147fa0`.

## 1 · Frozen inputs

* `research/modalities/emc-expression-panels.json`, sha256
  `59bccb553148c7100172456835957434b1349d701d4e0504e632a367c62a7f8d` — **re-hashed at dispatch,
  MATCHES the value declared in `../FOLLOWTHROUGH-DISCOVERY/proposals.json`** (`checks/01-locator-sha256`, exit 0).
* `../KINASE-2/label-permutation-vs-gene-resampling-null.json` sha256
  `f799e5ed962c09ff1bc05d2354c8fb4b12cc803e2aaf0475edaa8bea67edfb65` (known-answer target).
* `../KINASE-2/label_permutation_null.py` sha256
  `4fd18faf80cf4cf4174bf00f94746f39d93e91f9c50acf9555a3f1f497c6211c` (read-only reference).
* `../KINASE-2/reproduce_lane1_check.py` sha256
  `9d7bcde7223e90ec95a138a7baed93bddf9bc66ac5e3b749a4613f1b3fd98edd` (read-only reference).

## 2 · FROZEN composition marker list (22 symbols)

All 22 verified present in `gene_reads`, `readable` on **both** platforms, with per-sample
`z_vs_array` for all 35 GPL6244 and all 16 GPL3290 labelled samples.

* **Stromal / matrix / vascular / pericyte (13):** COL1A1, COL1A2, COL3A1, DCN, LUM, FN1, POSTN,
  THY1, FAP, PDGFRB, ACTA2, PECAM1, VWF
* **Immune / haematopoietic (7):** PTPRC, CD68, CD3E, CD8A, MS4A1, HLA-DRA, B2M
* **Not in the primary score, reported as separate sensitivity covariates (2):** MKI67
  (proliferation), EPCAM (epithelial) — neither is a tumour/stroma composition marker in a
  mesenchymal tumour and both are excluded from the primary score by this preregistration.

**Primary composition score `C`** for a sample = the mean of that sample's `z_vs_array` over the
**20 stromal+immune markers**, NaN-skipping. Sensitivity scores: `C_stromal` (13), `C_immune` (7),
and a two-covariate adjustment on (`C_stromal`, `C_immune`) jointly.

**Leave-one-out rule, frozen:** when the gene being tested is itself one of the 20 markers, that
marker is removed from `C` for that gene. A gene is never adjusted for a score containing itself.

## 3 · FROZEN seed and permutation counts

* `SEED = 20260909` (the same seed KINASE-2 declared).
* `N_PERM = 2000` label permutations for the adjusted concordance null, arm sizes fixed within
  platform, composition score staying attached to its sample.
* `N_PERM_COMP = 2000` composition permutations for the negative control (the composition score is
  shuffled across samples within platform; the labels stay real).

## 4 · Statistics, fixed in advance

Per gene per platform, over that platform's labelled samples:

* **Unadjusted rank statistic** `r_u` = Spearman correlation between the gene's per-sample z and the
  EMC indicator (1 = EMC, 0 = comparator), over samples where both are defined.
* **Composition-adjusted rank statistic** `r_a` = the first-order rank partial correlation
  `(r_gl − r_gc·r_lc) / sqrt((1−r_gc²)(1−r_lc²))`, all three components Spearman, `c` = the frozen
  composition score. The two-covariate version uses the corresponding second-order partial.
* Both are converted to a signed t for display: `t = r·sqrt((n−k−2)/(1−r²))`, k = number of covariates.
* **Attenuation** per gene per platform = `1 − |r_a| / |r_u|` (positive = the association shrinks
  when composition is held constant; negative = it grows). Frame-level attenuation is reported on
  the direction-concordance rate and on the cross-platform Pearson r of the per-gene statistics.
* Frames: **primary** = genes present in both committed background draws (KINASE-2's 431-gene
  frame, background `z`); **secondary** = curated `gene_reads` genes readable on both (413).

## 5 · Ordering, non-negotiable

1. **Known-answer control FIRST.** Recompute KINASE-2's observed Welch t, concordance counts and
   rates, cross-platform Pearson/Spearman r, and all thirteen placed joint p values, and compare to
   `../KINASE-2/label-permutation-vs-gene-resampling-null.json`. **Require 0 mismatches; exit 2
   otherwise and compute no adjustment.**
2. **Negative control.** A *permuted* composition score must **not** attenuate: the mean attenuation
   under 2000 composition permutations must be centred near 0 and the observed attenuation must sit
   outside it for any attenuation claim to be made.
3. Only then the adjusted statistics and their label-permutation null, on both frames.

## 6 · No outcome is preferred

A null — no attenuation, i.e. the contrast survives composition adjustment — is as publishable a
result here as attenuation, and is reported as found. **If attenuation is found it is an association
in this owned data and nothing more**: it licenses no biological, mechanistic, efficacy, safety,
selectivity, therapeutic-window, target-attribution or clinical-readiness conclusion. Marker
transcript abundance in undeconvolved bulk archival tissue is **not** a cell-fraction measurement;
"composition score" throughout means "the frozen marker-transcript score defined in §2", never a
measured cellular composition.

## 7 · Stop condition

Stop when the adjusted statistic and its null are computed on the primary and secondary frames, or
**immediately** on a known-answer reproduction failure — whichever comes first. No wet lab, no
network, no GPU, no paid API, no publication, no shared-file write.
