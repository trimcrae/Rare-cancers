# EXPR-HYPOXIA-1 — preregistration (frozen before any statistic was read)

Frozen 2026-09-09. The only reads preceding this file are: input byte sizes / sha256 / git
provenance, the JSON key structure of `research/modalities/emc-hypoxia-null-background.json`, its
118 `_confound_genes_requested_by_name`, its `_random_background_symbols` counts, its sample
lists and one example gene record (`A2ML1`, `A2M`) shown to establish the value schema. **No
association, correlation, concordance or attenuation of any kind has been computed.**

## 1 · Question
Is the residual EMC cross-platform expression contrast that survives EXPR-COMPOSITION's
tumour/stroma adjustment a **hypoxia programme**?

## 2 · Frozen covariate definitions

Source: `emc-hypoxia-null-background.json`, `targets[<series>].genes[<symbol>]`.
Per-sample value used: **`array_percentile`** — the gene's rank position within that array's own
probe distribution. This is the direct analogue of the `z_vs_array` quantity EXPR-COMPOSITION used,
it is comparable across the one-channel (GPL6244) and two-colour (GPL3290) platforms, and it is the
only per-sample quantity in this file whose scale does not depend on `value_kind`.

**Primary hypoxia score `H`** = per-sample mean `array_percentile` over the frozen HIF-target /
glycolytic-effector set, drawn only from the file's own named confound genes:

`ADPGK, ALDOA, CA9, EGLN3, ENO1, GPI, HK2, LDHA, PDK1, PFKFB3, PFKFB4, PFKL, PFKP, PGAM1, PGK1,
PKM, SLC16A1, SLC16A3, SLC2A1, SLC2A3, TPI1, VEGFA` (22 requested).

**Reported separately, NOT in `H`:**
* *Oxygen-sensing regulators* — `HIF1A, EPAS1, ARNT, VHL, HIF1AN, EGLN1, EGLN2`. Their mRNA is a
  poor hypoxia readout (regulation is post-translational), so they are described, not scored.
* *Vascular score `V`* — `PECAM1, VWF, KDR, FLT1, TEK, CDH5, ESAM, EMCN, ROBO4, CLDN5, ANGPT1,
  ANGPT2, PGF`. A secondary, separately reported covariate.

## 3 · Missingness rule — decided before computing
ASSESS-EXPR-COMPOSITION showed a NaN-skipping score has a sample-dependent marker set on GPL3290.
**This lane does not NaN-skip.** A gene enters `H` (or `V`) only if it is present with a non-null
`array_percentile` on **every labelled sample of both platforms** — complete-case *gene* selection.
The surviving set is therefore one fixed definition on both platforms. Every dropped gene is named
in the artifact. **If fewer than 8 genes survive for `H`, the lane aborts and reports that.**
A gene that is itself in the scored set is adjusted for a **leave-one-out** score.

## 4 · Gate — non-negotiable, runs first
Reproduce EXPR-COMPOSITION's published primary-frame rank concordance **0.6521 unadjusted →
0.5668 composition-adjusted** (and secondary 0.6368 → 0.5981), exactly, to 1e-9, using its own
committed machinery on the same input. **On any mismatch the run exits 3 and no hypoxia statistic
is computed or written.**

## 5 · Control — the seeded random background must NOT attenuate
300 sham covariates, each the per-sample mean `array_percentile` of `k` genes drawn without
replacement from `targets[...]._random_background_symbols` (seed 20260807; that universe **excludes
all 118 named confound genes** by construction), `k` = the surviving size of `H`, built through the
identical path and put through the identical machinery. Draw seed 20260909.
Reported: the sham distribution of the adjusted primary rate, and — following
ASSESS-EXPR-COMPOSITION — the **label-correlation-matched generic baseline**, i.e. the OLS
prediction of the adjusted rate at the sham covariate's own mean |Spearman(cov, label)| evaluated at
`H`'s label correlation. **A hypoxia covariate that attenuates no more than that generic prediction
is a NULL and is reported as one.**

## 6 · Statistics, frozen
Exactly EXPR-COMPOSITION's frames and machinery: primary (background-`z`) and secondary
(curated `z_vs_array`) frames of `emc-expression-panels.json`; rank (Spearman) gene–label
association; first-order rank partial correlation for a single covariate; **second-order** rank
partial correlation for the two-covariate `C + H` adjustment. Attenuation of the excess over 0.5 is
`(rate_unadj − rate_adj) / (rate_unadj − 0.5)`. Reported to 2 significant figures only —
ASSESS-EXPR-COMPOSITION showed one borderline gene moves it by ~0.01.

## 7 · Frames
Primary and secondary, as in EXPR-COMPOSITION. **STOP there.** No third frame, no new series.

## 8 · Declared outcomes — a null is publishable
The pre-stated readings:
* **NULL** — `H` attenuates no more than the label-correlation-matched generic baseline. Expected
  outcome; reported cleanly.
* **Partial** — `H` attenuates beyond the generic baseline but the residual survives `C + H`.
* **Positive-association** — `H` accounts for the composition-adjusted residual (`C + H` drives the
  adjusted rate to ≈ 0.5). Even this licenses **no** biological, target or clinical conclusion; it
  is an association in owned data.

## 9 · Stop condition
Stop when `H` (and `V`) adjusted statistics, the `C + H` two-covariate statistic, and the seeded
random-background control are computed on the primary and secondary frames — or immediately on gate
failure or on fewer than 8 surviving `H` genes.
