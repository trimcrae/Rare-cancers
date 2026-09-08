# R2 · Finding — is `NO_SEPARATION` a result, or an artifact of unconverged sampling?

**Short answer: the question was not settled by new sampling, because the sampling was neither
possible nor affordable here. On the evidence that could be obtained without new sampling, the
`NO_SEPARATION` verdict looks robust and the recorded non-convergence looks like noise rather
than a common drift — but the verdict remains PROVISIONAL by the prespecification's own terms,
and I am not lifting that label.**

Nothing below is a wet-lab, efficacy, selectivity, safety or clinical claim. ν is a single-chain
conformational exponent from a coarse-grained simulation and establishes none of those.

---

## 1 · Why no new sampling

Two independent stops, either one sufficient:

- **Environment.** `calvados`, `openmm`, `MDAnalysis`, `mdtraj` and `pandas` are all absent from
  this container (exit code 1 on each import, `checks/01`–`04`); no install exists anywhere on
  disk (`checks/06`); no conda (`checks/07`); PyPI is outside the egress path (`checks/09`).
  Acquiring them is forbidden by this task. Details and versions: `PRECONDITION.md`.
- **Clock.** The smallest targeted extension costs 13.2 CPU-hours and a scientifically clean
  whole-panel extension costs 103.6 h, against **3.75 h** remaining to the campaign stop.
  Arithmetic: `PLAN-AND-COST.md`.

## 2 · What the recorded non-convergence actually looks like

The committed artifact records `converged = false`, `n_exceeding_pooled_sd` 14 of 55
(fraction 0.2545) against the prereg's 20 % rule, `max_half_vs_full_delta` 0.05188.
Reading the per-run drifts (`checks/11`):

- **The drift has no direction.** Signed drift (second half − whole) over all 55 runs:
  mean **−0.00030**, SD 0.01778, **29 positive / 26 negative**. Amendment 1's mechanism — chains
  still collapsing out of their initial configuration — predicts a *systematic negative* drift.
  That signature is absent at the panel level.
- **The 14 exceeding runs are spread across 8 constructs** (C360 ×3, E264_E15 ×2, E264 ×2,
  E264_scr2 ×2, E360 ×2, E264_scr1, E264_scr3, N260 ×1 each), not concentrated in one arm of a
  contrast. Two of them are in the instrument control `E264_E15`.
- **Construct-mean drifts are small.** The largest is +0.01941 (`E264_scr1`, n=2, a composition
  null); among the six primary constructs none exceeds |0.0056|. `max_half_vs_full_delta` 0.05188
  is a single-run excursion, not a construct-level shift.

So the 25.45 % exceedance is driven by per-run scatter in a diagnostic computed on half the
frames — which is itself noisier than the full-trajectory fit — and not by a coherent relaxation.

## 3 · The decisive check: re-score with the frozen scorer on the later-time estimator

I passed the panel through the **unaltered** `score()` with `nu := nu_second_half` — the
second-half ν the prereg §2 already registers as a reported readout, and the estimate taken from
later in each trajectory. No guard, gate, range, threshold, seed or pair assignment was changed.

**Reproduction first** (`checks/11`): `score()` on the committed ν reproduces the committed panel
exactly — verdict `NO_SEPARATION`, `pooled_replicate_sd_nu` 0.019126,
`separation_threshold_nu` 0.057378. The scoring half is reproducible here.

**Second-half estimator:**

| | committed (whole trajectory) | second-half estimator |
|---|---|---|
| verdict | `NO_SEPARATION` | **`NO_SEPARATION`** |
| instrument-failure reasons | none | **none** |
| `pooled_replicate_sd_nu` | 0.019126 | 0.024905 |
| `separation_threshold_nu` | 0.057378 | 0.074716 |
| `E264_vs_C264` Δν, p | −0.00283, p 0.865 | −0.00291, **p 0.881** |
| `E360_vs_C360` Δν, p | +0.01173, p 0.286 | +0.01497, **p 0.444** |
| `T161_vs_C161` Δν, p | −0.00674, p 0.532 | −0.00017, **p 0.984** |
| `holm_reject_at_0.05` (all primary) | false | **false** |

All three primary pairs stay unseparated, and every primary p moves **away** from significance.
The validation criteria the specification names all hold under the alternative estimator:

- (a) **Instrument control holds.** `E264_E15 − E264` = **+0.08344** against a required
  +0.07472 (margin +0.00872); on the committed panel, +0.08190 against +0.05738 (margin +0.02452).
  It still expands, so the panel is still measuring what the prereg says it measures — but note
  the margin is much thinner on the noisier estimator, which is itself a reason not to treat the
  second-half read as a replacement for longer sampling.
- (b) **Composition nulls** still pass the scorer's own checks: `score()` returned
  `reasons: None`, i.e. no `INSTRUMENT_FAILED` or `INCOMPLETE` condition fired.
- (c) **`NU_BROKEN_RANGE` (0.15, 0.95) is not approached.** Whole-trajectory ν spans
  0.4256–0.5716; second-half ν spans 0.4171–0.5744. `outside_expected_range` is `{}` on the
  committed panel — every ν is also inside `NU_EXPECTED_RANGE` [0.30, 0.75].
- (d) **The prereg was not touched.** `emc_condensate_calvados.py` is byte-identical, its
  `--selftest` passes 78/78 (`checks/10`), and no threshold was altered (`IDENTITIES.md`).

## 4 · How far the drift would have to be from what was observed to flip a primary pair

Separation needs |Δν| ≥ 0.057378 (3 pooled SDs). Observed primary |Δν| are 0.00283, 0.01173 and
0.00674 — between **4.9× and 20× short**. Applying each construct's own observed mean drift in
the most separating direction (`checks/12`) moves them to 0.00838, 0.01975 and 0.01331: still
short by 2.9×–6.8×. **None clears.**

The honest residual: a fully adversarial bound, in which every replicate of one construct drifted
by the largest single-run excursion (0.05188) in one direction while every replicate of its
partner drifted the same amount the other way, reaches 0.107–0.116 and *would* clear the
threshold. That worst case is not excluded by arithmetic. It is contradicted by the data —
it requires a construct-correlated coherent drift, and the observed drift is near-zero-mean,
near-balanced in sign, and never exceeds |0.0056| at construct level among the primary six — but
"contradicted by the same data whose convergence is in question" is weaker than "measured on
converged trajectories". That gap is what longer sampling would close, and it is not closed here.

## 5 · Conclusion, stated at the strength the evidence supports

- **The `NO_SEPARATION` verdict is not visibly an artifact of the recorded non-convergence.** The
  drift is undirected, dispersed across constructs, and an order of magnitude too small at
  construct level to move any primary pair. Re-scoring with the frozen scorer on the later-time
  estimator returns the same verdict, with all guards passing and every primary p larger.
- **It does not follow that the verdict is converged, and I am not lifting `PROVISIONAL`.**
  The prereg's convergence rule is unmet (0.2545 > 0.20) and remains unmet; nothing here changes
  `converged = false`. Both halves come from the same 1,010-frame trajectory, so a slow common
  relaxation affecting both is untested.
- **The four registered negatives stand as they are** — `NEGATIVE_NO_STRATIFICATION`,
  `NEGATIVE_FET_NOT_SPECIAL`, `NEGATIVE_WILDTYPE_NOT_SEPARATED`, `NEGATIVE_COMPOSITION_ONLY` —
  PROVISIONAL, exactly as committed. Nothing here softens or hardens them.
- **In the specification's own terms: the verdict survives every test that could be run without
  new sampling; whether it survives convergence is still open, and closing it needs the
  103.6 CPU-hour whole-panel extension on the pinned Actions runner, not this session.**

## 6 · What a later session should do

Dispatch `.github/workflows/emc-condensate-calvados.yml` at `ref=<branch>` in `matrix` mode with
increased `n_frames` (and/or `discard_frames`) across the **whole** 55-run panel, then `reduce`;
emit the result as a new block beside the committed one; append a numbered Amendment 2 recording
the change. CPU-only, no paid compute. Budget ~104 CPU-hours of runner time.
