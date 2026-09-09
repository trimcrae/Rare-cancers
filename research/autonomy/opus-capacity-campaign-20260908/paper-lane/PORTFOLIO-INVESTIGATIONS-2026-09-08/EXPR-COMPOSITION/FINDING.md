---
id: DOC-PORTFOLIO-INVESTIGATION-EXPR-COMPOSITION-2026-09-09
title: "EXPR-COMPOSITION — about half the broad two-platform EMC expression contrast is carried by a frozen tumour/stroma marker score; the residual is real but much weaker than KINASE-2's headline"
level: L4
kind: investigation
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: EXPR-COMPOSITION
continues: KINASE-2
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# EXPR-COMPOSITION — composition-adjusted EMC expression contrast

Repo HEAD at lane start `1e35538daee86e1a34345340f7562d1e91147fa0` (2026-09-09T01:05:19Z).
Writes confined to this directory. No `git add`/`commit`/`push`, no `preflight.sh`, no subagent,
no worktree, no repo copy, no network, no GPU, no paid API, no shared-file edit.

## 1 · Question

FOLLOWTHROUGH-DISCOVERY rank 1, executed as specified: **is the broad two-platform EMC expression
contrast tumour/stroma composition, or EMC biology?** KINASE-2 proved the 65.2 % direction
concordance is a real shared **contrast** (permuted labels give 0.499, r(t₁,t₂) ≈ 0) and named this
as the one alternative its nulls could not touch — its §6 (a2). It adjusted for no sample
composition. No lane had.

## 2 · Merit

The expression arm is what an EMC kinase- or target-selection claim leans on when it says a gene is
"higher in EMC on both platforms". KINASE-2 showed that sentence needs a strength term. If the broad
contrast is largely a matrix-rich, immune-poor myxoid tumour being compared with differently
composed comparator tumours, then the concordance the arm cites is partly an artefact of what tissue
was in the block, and the leads' already-weak placement gets weaker. That is a paper-level statement
about what these two series can and cannot support — attainable at $0 from data already committed.

## 3 · Evidence gap this closes, and what distinguishes it from prior work

KINASE-2's two nulls both randomise something *other* than composition: gene identity, or the EMC
label. Both destroy composition confounding and EMC biology together. The missing input was a
**per-sample covariate** — and the committed artifact has one: `gene_reads` carries per-sample
`z_vs_array` for 22 canonical stromal/immune/epithelial/proliferation markers, readable on **both**
platforms for **all** 35 GPL6244 and 16 GPL3290 labelled samples. Nobody had used them.

## 4 · Step taken

A rank-based partial-association re-analysis of exactly KINASE-2's two frames, with the marker list,
the primary score, the leave-one-out rule, the seed and the ordering **frozen in
`PREREGISTRATION.md` (sha256 `6386ac16…`) before any statistic was read** — the only prior reads
were symbol presence, `readable` flags and arm sizes.

* **Composition score `C`** = per-sample mean `z_vs_array` over **20** frozen markers (13 stromal /
  matrix / vascular / pericyte + 7 immune). MKI67 and EPCAM were frozen **out** of `C` and reported
  separately. A gene that is itself a marker is adjusted for a **leave-one-out** score.
* **Unadjusted statistic** = Spearman r of the gene with the EMC indicator. **Adjusted statistic** =
  the rank partial correlation holding `C` constant. **Attenuation** = 1 − |r_adj| / |r_unadj|.

### Ordering, honoured as the proposal required

1. **Known-answer control ran FIRST** and gated everything (`checks/02`, exit 0; repeated inside the
   full run, `checks/04`). **103 comparisons against KINASE-2's committed artifact, 0 mismatches** —
   per-frame n, concordance counts and rates, cross-platform Pearson and Spearman r, all five min|t|
   quantiles, arm sizes, and every placed lead gene's min|t|, direction and gene-resampling joint p
   on both frames. The script returns **exit 2** and computes no adjustment on any mismatch.
   (Scope stated in the artifact: KINASE-2's *observed* statistics. Its permutation quantiles depend
   on an RNG call path and are deliberately excluded rather than pseudo-reproduced.)
2. **Negative control ran second**, before the headline was formed.
3. Only then the adjusted statistics and their label-permutation null, on both frames.

## 5 · ⭐ Result

**The frozen composition score is strongly, and consistently, associated with the EMC label itself.**

| | GPL6244 (6 EMC / 29 comparator) | GPL3290 (10 / 6) |
|---|---|---|
| Spearman(`C`, EMC label) | **−0.578** | **−0.504** |
| mean `C` z, EMC arm vs comparator arm | 0.925 vs 1.512 | 0.029 vs 0.401 |
| Spearman(`C_stromal`, label) | −0.465 | −0.532 |
| Spearman(`C_immune`, label) | −0.623 | +0.028 |

The EMC arms are **lower** on the marker score than their comparators on both platforms. The
stromal component is directionally consistent across platforms; the immune component is not.

**Holding `C` constant removes roughly half of the excess concordance on the primary frame.**

| Frame | genes paired | concordance unadjusted | **composition-adjusted** | change | **attenuation of the excess over 0.5** | cross-platform Pearson r, unadj → adj |
|---|---|---|---|---|---|---|
| primary (background draw) | 434 | 0.6521 | **0.5668** | −0.0853 | **0.561** | 0.405 → **0.251** |
| secondary (curated per-sample) | 413 | 0.6368 | **0.5981** | −0.0387 | **0.283** | 0.447 → **0.281** |

**The residual survives, but far more weakly than the unadjusted contrast.** Against a
label-permutation null recomputed *with the adjustment in place* (2000 permutations, seed 20260909,
arm sizes fixed, `C` staying attached to its sample; permuted mean 0.500):
**p = 0.022** (primary) and **p = 0.0085** (secondary). KINASE-2's unadjusted contrast was beyond
all 2000 permutations (p ≤ 0.0005). The contrast is not abolished; it is **substantially reduced,
by one to two orders of magnitude in p**.

**Negative control PASSES** (`checks/04`, primary frame, 500 permuted composition scores, real
labels): a shuffled score gives an adjusted rate of **0.6469** (sd 0.0135, 95 % [0.613, 0.668], min
0.592) — i.e. it returns essentially to the unadjusted 0.6521, distance 0.0052 against the real
score's 0.0853, and **0 of 500** shuffled draws reached the real score's 0.5668. The attenuation is
attributable to the score's real per-sample alignment, not to the adjustment machinery.

### Lead genes (secondary frame, per-sample z; full per-gene and per-frame values in the artifact)

| Gene | GPL6244 r unadj → adj (atten.) | GPL3290 r unadj → adj (atten.) | concordant unadj / adj |
|---|---|---|---|
| **NR4A3** (driver, positive control) | +0.540 → **+0.610** (−0.13) | +0.373 → **+0.474** (−0.27) | yes / **yes** |
| **RET** (lead 1) | +0.473 → +0.316 (**+0.33**) | +0.700 → +0.747 (−0.07) | yes / yes |
| **GFRA2** (route's counter-evidence) | −0.405 → −0.663 (−0.64) | −0.768 → −0.743 (+0.03) | yes / yes |
| **NDRG1** (lead 4 substrate) | +0.398 → +0.150 (**+0.62**) | +0.504 → +0.324 (**+0.36**) | yes / yes |
| EGFR | −0.480 → −0.687 | −0.476 → −0.455 | yes / yes |
| PRKDC (lead 3) | −0.248 → −0.195 | +0.252 → +0.200 | **no / no** |
| SGK1 (lead 4) | −0.090 → +0.214 | +0.224 → +0.368 | no / yes |
| XRCC5 / XRCC6 (lead 3) | −0.180 → −0.119 / +0.060 → −0.165 | −0.196 → −0.341 / +0.112 → −0.093 | yes / yes |
| ROS1 (lead 2) | +0.068 → +0.081 | +0.063 → −0.089 | yes / **no** |
| GFRA1, GDNF, HDAC3 | see artifact | see artifact | mixed |
| ALK (lead 2) | — | **not readable on GPL3290** | absent reading, not a reading of absence |

Two readings, both stated: **NR4A3's association strengthens** under adjustment on both platforms
(attenuation negative), which is what a genuinely tumour-intrinsic driver should do and is the most
interpretable single line here. **NDRG1 loses most of its association on both platforms** (+0.62,
+0.36) — the largest consistent attenuation among the leads, and the lead-4 quantity that KINASE-2
had placed at p = 0.088. RET attenuates on the larger platform only. For genes whose unadjusted r is
near zero (SGK1, GFRA1, GDNF, HDAC3, XRCC6) the attenuation ratio is a **ratio of small numbers and
is uninformative**; their large negative values are reported for completeness, not as findings.

**No sign is read as biology.** That EMC arms score *lower* on stromal and immune markers than these
particular comparator sets is a property of the comparator choice (LGFMS / desmoid / fibrosarcoma /
DFSP / GIST), not a statement about EMC.

## 6 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `composition-adjusted-contrast.json` (21 KB) — per lead gene and per frame: the
unadjusted statistic, the composition score (and its association with the EMC label, with the
stromal/immune/MKI67/EPCAM breakdown), the rank-based composition-adjusted statistic, and the
attenuation; plus per-frame paired rates, the adjusted label-permutation null, the gate record and
the negative control. **Generators.** `composition_adjusted_contrast.py`,
`vectorised_equivalence_check.py`. **Prereg.** `PREREGISTRATION.md`.

**Validation.** (1) Known-answer gate, 103 comparisons vs KINASE-2, **0 mismatches**, hard exit 2 on
any mismatch — `checks/02` and `checks/04`. (2) Negative control, PASS, 0/500 — `checks/04`.
(3) Two independent frames, two different data paths into the same series, same qualitative answer.
(4) `checks/05-vectorised-equivalence`, exit 0: the vectorised permutation core equals the plain
per-gene rank partial correlation to **5.6e-16** over 1703 gene × platform × frame comparisons.
(5) `checks/01-locator-sha256`, exit 0: `research/modalities/emc-expression-panels.json` re-hashed
at dispatch **matches** the sha256 declared in `../FOLLOWTHROUGH-DISCOVERY/proposals.json`.

**Preserved failed/aborted attempt.** `checks/03-composition-adjusted-contrast` (**exit 143**) — the
first full run, using the plain per-gene loop, was killed by this lane for runtime, not for a data or
gate failure; its `NOTE.txt` says so and `script-as-run.py` preserves the exact version. Its
known-answer gate had already passed with 0 mismatches inside that same run. It is not overwritten.

**Provenance.** Sole data input `research/modalities/emc-expression-panels.json`, sha256
`59bccb55…`, `generated_utc` 2026-08-29T12:51:32+00:00, committed, read read-only. KINASE-2's
artifact `f799e5ed…` read read-only as the gate target. Background seeds as recorded by KINASE-2.
Runtime 34.4 s, single core, stdlib + numpy.

**Limitations — these bound the result hard.**
- **The marker score is not a cell fraction.** It is 20 marker transcripts in undeconvolved bulk
  archival tissue. It is a *proxy* for composition and an imperfect one; "composition score"
  throughout means the frozen §2 score, never a measured composition.
- **Composition and biology are not separable here, even in principle.** In a mesenchymal tumour the
  stromal programme is partly the tumour's own. Adjusting for `C` therefore removes some genuine EMC
  biology along with any composition confounding, so **0.561 is an upper bound on the composition
  share, not an estimate of it**, and the surviving p values are conservative.
- **Small arms.** 6 EMC on GPL6244, 10 on GPL3290; the GPL3290 exact label space is only C(16,10) =
  8008. A first-order partial correlation on n = 16 with a covariate that is itself correlated
  −0.50 with the label is unstable, and 48–95 genes per platform flip direction under adjustment.
- The 434-gene primary frame is 3 genes larger than KINASE-2's 431 because rank scorability and
  Welch-t scorability differ slightly; the **gate** compares like with like (Welch t, 431) and
  passed exactly.
- **No multiple-testing correction**, no deconvolution, no third series, no protein, no activation
  state, no drug response.
- **The two-covariate (`C_stromal`, `C_immune`) sensitivity adjustment named in the prereg was NOT
  run** — the lane stopped at its declared stop condition. The single-score result stands alone.
- ⛔ **Nothing here establishes efficacy, safety, selectivity, a therapeutic window, target
  attribution or clinical readiness for any agent in any disease, and nothing here is advice about
  a patient.** The attenuation is **an association in owned data and nothing more**; it licenses no
  biological or clinical conclusion.

**Stop condition (preregistered).** Stop when the adjusted statistic and its null are computed on
the primary and secondary frames, or immediately on a reproduction failure. **Met, on the
reproducing branch.**

## 7 · What this owes KINASE-2 and PUB-KINASE-LEADS (not applied — shared files)

KINASE-2 §6 lists (a2) as open. It is now **partly closed and partly answered against the
biological reading**: a frozen tumour/stroma marker score, measured per sample, accounts for roughly
half the excess concordance on the primary frame and about 28 % on the secondary, and the residual
contrast's label-permutation p moves from ≤ 0.0005 to 0.022 / 0.0085. Any prose that cites the
65.2 % concordance as evidence that EMC is a coherent *biological* contrast should carry that
qualification. **No shared file is edited by this lane and no diff is proposed**: the correct
downstream text belongs to the owners of `KINASE-2/FINDING.md` and the `PUB-KINASE-LEADS` endpoint,
who already hold a queue of repairs.

## 8 · Next credible independent work (not done, not authorised here)

1. The preregistered **two-covariate** (`C_stromal`, `C_immune`) and **MKI67/EPCAM** sensitivity
   adjustments, and a stratified rather than covariate-adjusted contrast.
2. A real **deconvolution** with a reference signature would replace the proxy score — no such
   reference is identified as available at $0 in this repository, and no download is authorised.
3. A **third series**, as KINASE-2 already said, still does more for this arm than any further
   reanalysis of these two.
