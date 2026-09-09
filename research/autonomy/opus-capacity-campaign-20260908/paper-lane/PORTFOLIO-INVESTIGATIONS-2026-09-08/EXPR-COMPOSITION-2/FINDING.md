---
id: DOC-PORTFOLIO-INVESTIGATION-EXPR-COMPOSITION-2-2026-09-09
title: "EXPR-COMPOSITION-2 — the composition attenuation was carried by a sample-dependent marker set; with a fixed marker set it is 0.26, and none of it is separable from generic covariate shrinkage"
level: L4
kind: investigation
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: EXPR-COMPOSITION-2
follows: EXPR-COMPOSITION, ASSESS-EXPR-COMPOSITION
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# EXPR-COMPOSITION-2 — following through the defect and the qualification

Writes confined to this directory. No shared file edited, no lane file edited, nothing applied.
No `git add`/`commit`/`push`, no `preflight.sh`, no subagent, no worktree, no repo copy, no network,
no GPU, no paid API. The corrections to `../EXPR-COMPOSITION/` are delivered as an **unapplied**
diff (`CORRECTIONS.diff`), proved with `git apply --check` (exit 0) and left unapplied — the target
files are byte-unchanged and clean in `git status`.

## 1 · Question

`ASSESS-EXPR-COMPOSITION` found that EXPR-COMPOSITION's frozen composition score is **not** the
fixed 20-marker score its preregistration describes: on GPL3290 it is a NaN-skipping mean over a
sample-dependent 16–20 marker subset. **What is the headline attenuation when the score is instead
a fixed marker set present on every sample, and how much of whatever remains is generic to any
label-correlated covariate rather than specific to composition?**

## 2 · Merit

The number at issue — "adjusting for tumour/stroma composition removes ~56 % of the excess
cross-platform concordance" — is the qualification that any downstream EMC expression claim would
have to carry. If it is an artefact of a covariate whose *definition changes between samples in a
label-correlated way*, then the qualification as written misstates both the size and the nature of
the confounding, in a direction that would make an honest paper wrong. Fixing it costs seconds on
data already committed, and the fix is falsifiable in the same run.

## 3 · Evidence gap

`EXPR-COMPOSITION` never recomputed with a complete-markers-only score (it names this only as
future work), and `ASSESS-EXPR-COMPOSITION` bounded the defect at the level of the **covariate**
(Spearman(C, label) −0.504 → −0.476; corr 0.918) without carrying it through to the **headline**.
The generic-vs-specific split was likewise estimated only for the published, defective score. Both
are closed here. The inputs are exactly the frozen ones: `research/modalities/emc-expression-panels.json`
and the two KINASE-2 frames.

## 4 · Step taken

An independent reimplementation (`complete_markers_recompute.py`), importing **nothing** from
`../EXPR-COMPOSITION/composition_adjusted_contrast.py` — ranks and correlations from
`scipy.stats.rankdata` / `spearmanr`, partial rank correlation from the first-order formula, the
concordance-rate and permutation machinery rewritten. Only the frozen input JSON, the frozen marker
list and the frozen frame definitions are taken from the lane. Convention throughout: **no
leave-one-out**, applied identically to every covariate, which reproduces the lane's published
primary-frame pair 0.6521 → 0.5668 exactly and so is not doing any of the work.

### 4.1 Re-derivation of the assessor's four numbers — **all four reproduce digit for digit**

| quantity | assessor | this lane (`checks/01`) |
|---|---|---|
| GPL3290 per-marker missingness | DCN 8, CD3E 4, MS4A1 3, PTPRC 2, CD8A 1, HLA-DRA 1, MKI67 1 (of 16) | **identical** (EMC-arm share: 4, 2, 2, 2, 0, 0, 1) |
| GPL6244 completeness | 20/20 complete on all 35 | **identical** |
| Spearman(markers entering `C`, label), GPL3290 | +0.21 | **+0.2105** |
| complete-markers-only Spearman(C, label), GPL3290 | −0.476 (corr 0.918 with published `C`) | **−0.4761** (corr **+0.9176**) |
| sham regression generic prediction at `C`'s label r | 0.6077 | **0.6077** (slope −0.0727, intercept 0.6470, r = −0.401) |
| matched-sham bands | 0/14 (±0.10), 0/26 (±0.15), 1/42 (±0.20) | **identical**; p = 0.0667 / 0.0370 / 0.0465 |

Nothing failed to reproduce. The published `C` on GPL3290 is a mean over **16–20** markers (EMC arm
mean 19.00, comparator arm 18.50); 14 of the 20 primary markers are complete on every labelled
sample of both platforms, and the six that are not are DCN, PTPRC, CD3E, CD8A, MS4A1, HLA-DRA.

### 4.2 ⭐ The headline with a **fixed** marker set on every sample

`C_fixed` = mean `z_vs_array` over the **14 markers complete on every labelled sample of both
platforms** (COL1A1, COL1A2, COL3A1, LUM, FN1, POSTN, THY1, FAP, PDGFRB, ACTA2, PECAM1, VWF, CD68,
B2M). No NaN-skipping anywhere; the same 14 markers define the score for every sample on both
platforms. `C_platform_complete` is the intermediate that fixes only GPL3290 (20 markers there
being complete on GPL6244, 14 on GPL3290).

| frame | covariate | unadjusted | adjusted | drop | **attenuation of the excess over 0.5** |
|---|---|---|---|---|---|
| primary (434 genes) | published `C` (16–20 markers) | 0.6521 | 0.5668 | 0.0853 | **0.5606** *(published: 0.561)* |
| primary | `C_platform_complete` (GPL3290 fixed only) | 0.6521 | 0.5945 | 0.0576 | **0.3788** |
| primary | **`C_fixed` (14 markers, fixed everywhere)** | 0.6521 | **0.6129** | 0.0392 | **0.2576** |
| secondary (413 genes) | published `C` | 0.6368 | 0.5956 | 0.0412 | 0.3009 *(published: 0.283, with LOO)* |
| secondary | `C_platform_complete` | 0.6368 | 0.5981 | 0.0387 | 0.2832 |
| secondary | **`C_fixed`** | 0.6368 | **0.6199** | 0.0169 | **0.1239** |

**The published attenuation more than halves when the covariate is made a single fixed score.**
Roughly half of the reduction comes from repairing GPL3290 alone (0.561 → 0.379) and the rest from
using the same marker set on both platforms (0.379 → 0.258).

**The residual gets *stronger*, not weaker.** Against 2000 label permutations recomputed with the
`C_fixed` adjustment in place (seed 20260909, arm sizes fixed, the score staying attached to its
sample): primary **p = 0.0010** (1/2000 ≥ observed, permuted mean 0.5001, sd 0.0343); secondary
**p = 0.0015** (2/2000, mean 0.4990, sd 0.0401). The published adjusted p values (0.022 / 0.0085)
were depressed by over-removal.

### 4.3 The generic component, separated

Using the assessor's own 300 label-correlation-matched sham covariates (20 random non-marker genes
each, same machinery, seed 4242), re-derived here and extended to the corrected score
(`checks/01` §D, `checks/02`):

| score | mean \|label r\| | adjusted rate | generic prediction | **composition-specific drop** | matched shams attenuating ≥ as much |
|---|---|---|---|---|---|
| published `C` | 0.541 | 0.5668 | 0.6077 | 0.0408 → **0.2686 of the excess** | 0/14, 0/26, 1/42 (p = 0.067, 0.037, 0.047) |
| **`C_fixed`** | 0.467 | 0.6129 | **0.6130** | **0.0001 → 0.0009 of the excess** | **4/14, 14/39, 30/76 (p = 0.33, 0.38, 0.40)** |

The published score's total attenuation 0.5606 splits into **generic 0.2920 + specific 0.2686**,
confirming the assessor's "nearer 0.27 than 0.561". But once the defect is repaired, the corrected
score's attenuation of 0.2576 splits into **generic 0.2566 + specific 0.0009**: it lands within
0.0001 of the generic regression line (0.0 residual sd; 95 % CI for the fitted mean 0.6089–0.6171),
and the non-parametric matched-sham test — the assessor's own primary falsifier, re-run against the
corrected score — **no longer separates it from a random 20-gene covariate of the same label
correlation**.

## 5 · Which number should be quoted going forward

**Quote the fixed-marker figure, and quote it as an upper bound with no established
composition-specific component:**

> *Adjusting the cross-platform EMC expression contrast for a fixed 14-marker tumour/stroma
> transcript score removes **≈ 0.26** of the excess concordance over 0.5 on the primary frame
> (0.6521 → 0.6129) and **≈ 0.12** on the secondary (0.6368 → 0.6199). Label-correlation-matched
> sham covariates built from random non-marker genes remove as much (one-sided p ≈ 0.33–0.40), so
> **none of this attenuation is separable from the shrinkage any covariate correlated with the EMC
> label produces**, and no composition-specific share is established. The adjusted contrast
> survives at p = 0.0010 (primary) and 0.0015 (secondary) against 2000 label permutations.*

**Do not quote 0.561, 0.56, or "roughly half".** It is computed from a covariate that is not one
score: on GPL3290 its marker set varies between samples and the variation itself tracks the label
(+0.2105). **Do not quote 0.27 either.** That figure is the composition-specific share *of the
defective score*; it does not survive the repair. The honest summary is that the corrected analysis
gives a **smaller** attenuation and a **stronger** residual than the published one, and attributes
none of the attenuation to composition specifically.

## 6 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `complete_markers_recompute.py` and `fixed_marker_sham_check.py` (this directory),
their captured output in `checks/`, and `CORRECTIONS.diff` — an **unapplied** unified diff adding a
**dated appended correction** to `../EXPR-COMPOSITION/PREREGISTRATION.md` (C1 the false readability
claim with the per-marker table, C2 the undisclosed `N_PERM_COMP` 2000 → 500 deviation) and to
`../EXPR-COMPOSITION/FINDING.md` (the same two plus the corrected headline). **Both edits are pure
appends: every byte of the frozen text is preserved and the appendix says so.** A preregistration
is not silently editable, so no in-place rewrite was produced.

**Validation / baseline.** (a) The independent reimplementation reproduces the lane's published
primary-frame pair 0.6521 → 0.5668 exactly, which is the baseline that licenses the corrected
numbers. (b) All six of the assessor's numbers reproduce digit for digit under a different
implementation. (c) `git apply --check` on `CORRECTIONS.diff` exits **0** (`checks/04`), and the
target files remain clean in `git status`; the earlier failed invocation is preserved as
`checks/03-git-apply-check-failed-attempt` (exit 1, a shell redirection path error, git never ran).

**Provenance.** `research/modalities/emc-expression-panels.json` (sha256
`59bccb55…c62a7f8d`, as pinned by EXPR-COMPOSITION `checks/01`); frames and arm definitions from
that file exactly as KINASE-2 and EXPR-COMPOSITION define them; marker list from
`PREREGISTRATION.md` §2; sham construction and seed 4242 from
`../ASSESS-EXPR-COMPOSITION/work/sham_matched_control.py`; permutation seed 20260909 from
`PREREGISTRATION.md` §3.

**Limitations.**
* **The 14-marker fixed set is not just "the same score with the gaps closed".** It necessarily
  drops all six incomplete markers, which are DCN plus **every** immune marker except CD68 and B2M.
  So `C_fixed` is a stromal-dominant score with a weaker label correlation (−0.458 / −0.476 vs
  −0.578 / −0.504), and the fall in attenuation confounds *removing the sample-dependent marker
  set* with *removing the immune component*. The intermediate `C_platform_complete` row separates
  them roughly half and half, but not cleanly. **A complete-markers-only score is the analysis the
  defect calls for; it is not a strictly more powerful measurement of composition.**
* The generic/specific split rests on a linear fit with r = −0.401 and residual sd 0.0230; the
  point estimate at a single x is weak, which is why the non-parametric matched-sham bands are
  quoted alongside it. Band membership is small (n = 14–76).
* The shams share two disanalogies with the real score (drawn from the background `z` path, not the
  curated `z_vs_array` path; they may themselves carry stromal signal) — both push shams toward
  attenuating, so the *specific* share is if anything overstated, which strengthens rather than
  weakens the conclusion in §5.
* A marker-transcript score in undeconvolved bulk archival tissue is **not** a cell-fraction
  measurement, and adjusting for a mismeasured confounder leaves residual confounding: none of these
  numbers bounds the true composition share in either direction.
* ⛔ Everything here is **an association in owned data**. It licenses no biological, mechanistic,
  target-attribution, efficacy, safety, selectivity, therapeutic-window or clinical-readiness
  conclusion, and no advice about any patient.
* Out of scope by instruction and not run: the two-covariate (`C_stromal`, `C_immune`) and
  MKI67 / EPCAM sensitivity analyses; no assessment of KINASE-2 itself.

**Stop condition.** Met: the four assessor numbers are independently re-derived, the
complete-markers-only headline and its null are computed on both frames, the generic component is
separated for both the published and the corrected score, and the correction diff is produced and
proved unapplied. Anything further belongs to the owner of `../EXPR-COMPOSITION/`.

## 7 · Note for the coordinator — a real resource problem, no evidence deleted

At the start of this lane every Bash call failed with `ENOSPC` on the harness temp filesystem;
`df -h /` reports **252 G total, 100 % used, 712 K available** on `/dev/vda`, which is the same
device carrying the repository and every campaign evidence directory. Per CLAUDE.md §8 I deleted
**nothing** — no evidence, no scratch, no other lane's files — and worked within the remaining
headroom. **This is reported, not resolved**: the disk floor is a live risk to any lane still
writing evidence, and it needs the owner's attention rather than a cleanup by a worker.
