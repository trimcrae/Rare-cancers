---
id: DOC-NR4A3-SELECTIVITY-MARGIN-MODEL
title: How much selectivity margin does degradation need, and can the physics resolve it?
level: L4
kind: memo
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `memo` from its location under research/modalities/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# How much selectivity margin does degradation need, and can the physics resolve it?

Metric: the **best NR4A3 degradation reachable at any dose where the paralogue stays <=20%**, both arms at the SAME dose. With zero selectivity the two arms are identical, so the metric is pinned at the ceiling (0.2) - everything above that is what the mechanism bought.

## 1. Required thermodynamic margin (single reference scenario)

| margin (kcal/mol) | alpha(NR4A3) | dose (uM) | deg NR4A3 @ ceiling | deg paralogue |
|---|---|---|---|---|
| 0.00 | 3.0 | 0.0016 | 0.195 | 0.195 |
| 0.50 | 6.98 | 316.2278 | 0.342 | 0.185 |
| 1.00 | 16.22 | 316.2278 | 0.508 | 0.166 |
| 1.50 | 37.72 | 251.1886 | 0.72 | 0.191 |
| 2.00 | 87.73 | 251.1886 | 0.831 | 0.186 |
| 2.50 | 204.0 | 251.1886 | 0.893 | 0.184 |
| 3.00 | 474.39 | 251.1886 | 0.924 | 0.184 |
| 3.50 | 1103.16 | 251.1886 | 0.938 | 0.183 |
| 4.00 | 2565.32 | 251.1886 | 0.945 | 0.183 |
| 4.50 | 5965.47 | 251.1886 | 0.948 | 0.183 |
| 5.00 | 13872.25 | 251.1886 | 0.949 | 0.183 |
| 5.50 | 32258.9 | 251.1886 | 0.95 | 0.183 |
| 6.00 | 75015.69 | 251.1886 | 0.95 | 0.183 |
| 6.50 | 174443.46 | 251.1886 | 0.95 | 0.183 |
| 7.00 | 405655.41 | 251.1886 | 0.95 | 0.183 |
| 7.50 | 943321.74 | 251.1886 | 0.95 | 0.183 |
| 8.00 | 2193625.15 | 251.1886 | 0.95 | 0.183 |

**Margin required, across the whole scenario grid:**

| NR4A3 target | scenarios reachable | min | median | max | above MDD |
|---|---|---|---|---|---|
| 70% | 21/27 | 1.5 | 1.5 | 1.75 | 21 |
| 80% | 21/27 | 1.75 | 2.0 | 2.25 | 21 |
| 90% | 12/27 | 2.5 | 2.75 | 2.75 | 12 |

Margin applied to the NR4A3 ternary arm only (alpha_NR4A3 = alpha_baseline x exp(margin/RT)); binary warhead affinity held EQUAL across paralogues, the conservative assumption for a ~70%-conserved pocket. The ubiquitination drive is re-calibrated at every margin so the NR4A3 arm is always a working degrader (see calibrate_drive).

## 2. Resolvable difference (replicate-SD error model)

| replicate SD | n | MDD @95% |
|---|---|---|
| 0.4 | 2 | **0.78** |
| 0.4 | 3 | **0.64** |
| 0.4 | 5 | **0.5** |
| 0.4 | 8 | **0.39** |
| 0.7 | 2 | **1.37** |
| 0.7 | 3 | **1.12** |
| 0.7 | 5 | **0.87** |
| 0.7 | 8 | **0.69** |
| 1.0 | 2 | **1.96** |
| 1.0 | 3 | **1.6** |
| 1.0 | 5 | **1.24** |
| 1.0 | 8 | **0.98** |

MDD = z * replicate_SD * sqrt(2/n) for the difference of two independently-estimated ddG values; replicate SD (prereg), NOT MBAR SE. Separate from ACCURACY: OpenFE's public RBFE benchmark is ~1.7 kcal/mol RMSE, and the ternary/NAGL lane has no accuracy number of its own until Val B.

## 3. Categorical axes - the same metric at ZERO thermodynamic margin

| scenario | dose (uM) | deg NR4A3 @ ceiling | deg paralogue |
|---|---|---|---|
| interface_thermodynamics_only | 0.0016 | **0.195** | 0.195 |
| unique_lysine | 15.8489 | **0.828** | 0.194 |
| covalent_capture | 0.0016 | **0.237** | 0.174 |
| covalent_plus_unique_lysine | 0.0398 | **0.885** | 0.192 |
| covalent_capture_KINETIC | 1000.0 | **0.958** | 0.084 |

Median across the whole grid:

| scenario | median deg NR4A3 @ ceiling |
|---|---|
| interface_thermodynamics_only | **0.185** |
| unique_lysine | **0.824** |
| covalent_capture | **0.245** |
| covalent_plus_unique_lysine | **0.885** |
| covalent_capture_KINETIC | **0.915** |

(A 30.0x covalent effective-affinity gain == 2.02 kcal/mol - but it applies to NR4A3 ONLY, because the paralogues have no nucleophile at the aligned position.)

## Verdict

**To reach 80% NR4A3 degradation while a paralogue stays under 20%, the induced interface must supply a TRUE margin of ~2.00 kcal/mol (grid range 1.75-2.25 over 27 scenarios). The best-case RESOLVABLE difference is 1.12 kcal/mol (replicate SD 0.7, n=3), so the required effect is ~1.79x the noise floor and of the same order as the method's ACCURACY (~1.7 kcal/mol RMSE on the public RBFE benchmark). At ZERO thermodynamic margin the null gives 0.185 (the ceiling, by construction), while the categorical axes give a median 0.824 (unique lysine), 0.915 (covalent capture, time-integrating form; the equilibrium proxy's 0.245 is a lower bound) and 0.885 (affinity-proxy covalent + unique lysine) - selectivity bought with no free-energy contest at all.**

Rank the search axes by whether the mechanism is CATEGORICAL (present/absent) or MARGINAL (a free-energy contest). Spend the alchemy on CONFIRMING a categorical design, not on trying to WIN a contest at the edge of resolution.

## Honest limits

- Every K_d, alpha, concentration, rate and efficiency is an ILLUSTRATIVE ASSUMPTION - none is measured for NR4A3 or any degrader. This is a sensitivity analysis, not a prediction.
- 1:1:1 equilibrium with a steady-state degradation balance: no explicit E2~Ub kinetics, no processivity, no deubiquitinase competition, no permeability or exposure term.
- The margin is applied to the ternary arm only; a real design changes binary affinity, cooperativity and geometry together.
- Covalent capture is modelled as an effective-affinity gain, NOT a k_inact/K_I treatment; an IRREVERSIBLE covalent PROTAC also sacrifices catalytic turnover (hence the reversible-covalent recommendation in the write-up), which this model does not represent.
- The unique-lysine axis is modelled as a drop in ubiquitination efficiency, not as a geometric calculation - establishing the actual transfer-zone geometry is the ternary/CRL stage's job.
- No efficacy, safety, therapeutic-window or clinical claim is made or implied.
