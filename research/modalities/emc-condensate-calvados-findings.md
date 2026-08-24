---
id: DOC-EMC-CONDENSATE-CALVADOS-FINDINGS
title: "CALVADOS single-chain arm — what the run measured"
level: L4
kind: generated
status: generated
generator: research/modalities/emc_condensate_report.py
canonical_for: [emc-condensate-calvados-result]
purpose: >
  The measured result of the frozen CALVADOS single-chain arm, rendered from its artifacts so
  that no number here is typed.
scope: >
  The CALVADOS 2 single-chain arm only. No slab phase-coexistence run and no multi-domain run
  is reported, because neither was performed.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-24
last_verified: 2026-08-24
---
# CALVADOS single-chain arm — what the run measured

> ⚙ **GENERATED FILE — do not hand-edit.** Rendered by `emc_condensate_report.py` from
> [`emc-condensate-calvados.json`](./emc-condensate-calvados.json) and
> [`emc-condensate-window-eligibility.json`](./emc-condensate-window-eligibility.json).
> Every rule applied here was frozen in [`emc-condensate-calvados-prespecification.md`](./emc-condensate-calvados-prespecification.md) **before any simulation**;
> the prose for each verdict and each negative is fixed in the generator, so this note cannot
> say something the run did not produce.

## 1 · Verdict

**NO_SEPARATION — no prespecified pair separates under rule D1.** ⭐ This is a RESULT, not a failure. It says the model does not distinguish the reported partners' retained segments on this axis, which contradicts the differential prediction the route memo was about to build on.

**N2 · no partner stratification.** No length-matched FET-vs-TCF12 pair separates. The differential prediction across the chimeras is not supported on this axis.

**N4 · FET identity carries no signal here.** None of the three length-matched pairs separates, so the clinical reading — that a TCF12-partnered patient is different on this axis — is unsupported by this instrument.

**N3 · the wild-type control does not separate.** NR4A3's own disordered AF1 is indistinguishable from the EWSR1 low-complexity window on this readout. The manuscript's central fusion-versus-wild-type asymmetry survives at the composition level and fails at the phase-behaviour level, and the manuscript has to say so.

**N1 · composition-only.** Neither scrambled parent's ν moved from its parent by the separation threshold. Composition-preserving shuffles change the *order* of the sequence and nothing else, so the simulation is resolving nothing beyond amino-acid composition — and composition counting is already the manuscript's existing evidence. ⚠ Read with the verdict above: if partners also separate, that separation is real but is a composition effect, and CALVADOS has added a more expensive route to a number the paper already had.

## 2 · What was run

- Constructs in the frozen manifest: **15**; runs: **55**; analyses reduced: **55**.
- Protocol: CALVADOS 2, 293.15 K, 0.19 M ionic strength, pH 7.5, 10 fs timestep, 1010 frames × 7000 steps, first 10 discarded, 150 nm box, CPU platform.
- Pooled replicate SD of ν: **0.0191**; separation threshold (3 SD): **0.0574**.

### 2.1 · Window eligibility (AlphaFold pLDDT, fetched before any simulation)

Entry criterion, fixed before the fetch: at least 75% of window residues below pLDDT 50.

| construct | window | residues read | mean pLDDT | fraction < 50 | eligible |
|---|---|---:|---:|---:|---|
| `E264` | EWSR1 1-264 | 264 | 38.81 | 0.9811 | yes |
| `E360` | EWSR1 1-360 | 360 | 40.44 | 0.9333 | yes |
| `T161` | TAF15 1-161 | 161 | 39.0 | 0.9938 | yes |
| `C161` | TCF12 1-161 | 161 | 44.92 | 0.8075 | yes |
| `C264` | TCF12 1-264 | 264 | 43.48 | 0.8712 | yes |
| `C360` | TCF12 1-360 | 360 | 43.41 | 0.8556 | yes |
| `N260` | NR4A3 1-260 | 260 | 37.66 | 0.9654 | yes |
| `F212` | FUS 1-212 | 212 | 41.03 | 0.9575 | yes |

All primary windows eligible: **yes**.

## 3 · Measured ν per construct

| construct | role | window | N | n | ν mean | ν SD | ν min | ν max |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `E264` | TEST | EWSR1 1-264 | 264 | 5 | 0.4785 | 0.0318 | 0.4330 | 0.5198 |
| `E360` | TEST | EWSR1 1-360 | 360 | 5 | 0.4754 | 0.0224 | 0.4509 | 0.5050 |
| `T161` | TEST | TAF15 1-161 | 161 | 5 | 0.4959 | 0.0205 | 0.4683 | 0.5231 |
| `C161` | TEST | TCF12 1-161 | 161 | 5 | 0.5027 | 0.0081 | 0.4933 | 0.5124 |
| `C264` | TEST | TCF12 1-264 | 264 | 5 | 0.4813 | 0.0197 | 0.4584 | 0.5047 |
| `C360` | TEST | TCF12 1-360 | 360 | 5 | 0.4636 | 0.0060 | 0.4562 | 0.4696 |
| `N260` | CONTROL | NR4A3 1-260 | 260 | 5 | 0.4897 | 0.0210 | 0.4613 | 0.5141 |
| `F212` | CONTROL | FUS 1-212 | 212 | 5 | 0.4762 | 0.0078 | 0.4623 | 0.4811 |
| `E264_scr1` | NULL | EWSR1 1-264 shuffled, seed 20260824 | 264 | 2 | 0.4887 | 0.0003 | 0.4885 | 0.4889 |
| `E264_scr2` | NULL | EWSR1 1-264 shuffled, seed 20260825 | 264 | 2 | 0.4852 | 0.0190 | 0.4718 | 0.4986 |
| `E264_scr3` | NULL | EWSR1 1-264 shuffled, seed 20260826 | 264 | 2 | 0.4663 | 0.0222 | 0.4507 | 0.4820 |
| `C264_scr1` | NULL | TCF12 1-264 shuffled, seed 20260824 | 264 | 2 | 0.4713 | 0.0129 | 0.4622 | 0.4804 |
| `C264_scr2` | NULL | TCF12 1-264 shuffled, seed 20260825 | 264 | 2 | 0.4259 | 0.0004 | 0.4256 | 0.4262 |
| `C264_scr3` | NULL | TCF12 1-264 shuffled, seed 20260826 | 264 | 2 | 0.4606 | 0.0405 | 0.4319 | 0.4892 |
| `E264_E15` | INSTRUMENT | EWSR1 1-264 with 15% of positions substituted to Glu, seed 20260827 | 264 | 3 | 0.5604 | 0.0105 | 0.5506 | 0.5716 |

## 4 · Prespecified comparisons

`D1` is the frozen rule: |Δν̄| ≥ 3 pooled replicate SDs **and** disjoint replicate ranges. `p` is an exact two-sided permutation test; Holm is applied across the primary family only.

| pair | family | Δν̄ | separated (D1) | p | arrangements | powered | Holm |
|---|---|---:|---|---:|---:|---|---|
| `E264_vs_C264` | primary | -0.0028 | no | 0.8651 | 252 | yes | no |
| `E360_vs_C360` | primary | 0.0117 | no | 0.2857 | 252 | yes | no |
| `T161_vs_C161` | primary | -0.0067 | no | 0.5317 | 252 | yes | no |
| `E264_vs_E360` | secondary | 0.0031 | no | 0.8651 | 252 | yes | — |
| `E264_vs_F212` | secondary | 0.0023 | no | 0.8492 | 252 | yes | — |
| `E264_vs_N260` | secondary | -0.0112 | no | 0.5556 | 252 | yes | — |
| `E264_vs_T161` | secondary | -0.0174 | no | 0.3413 | 252 | yes | — |
| `E360_vs_T161` | secondary | -0.0205 | no | 0.1667 | 252 | yes | — |
| `F212_vs_C264` | secondary | -0.0051 | no | 0.5635 | 252 | yes | — |
| `T161_vs_N260` | secondary | 0.0062 | no | 0.6429 | 252 | yes | — |

## 5 · The composition-only null

Each parent against the mean of its three composition-preserving scrambles. A shuffle changes sequence *order* and preserves composition exactly, so a parent that does not move from its scrambles is a parent whose ν carries no information beyond composition.

| parent | Δν̄ vs scramble mean | exceeds the 3-SD threshold |
|---|---:|---|
| `E264` | -0.0016 | no |
| `C264` | 0.0287 | no |

### 5.1 · The composition baseline these ν have to beat

The manuscript's own sequence-derived descriptors (`fusion_idr_features.features`, imported rather than copied), computed on **exactly the windows simulated here** — the manuscript's own table uses different ones, and characterises TAF15 1–205 while the only reported TAF15::NR4A3 coding junction retains 1–161.

| construct | N | SYGQ | aromatic (FYW) | FCR | NCPR | entropy (bits) | SCD |
|---|---:|---:|---:|---:|---:|---:|---:|
| `E264` | 264 | 0.5606 | 0.1402 | 0.0303 | -0.0152 | 3.154 | 0.218 |
| `E360` | 360 | 0.5278 | 0.1167 | 0.0944 | -0.0222 | 3.499 | 0.561 |
| `T161` | 161 | 0.7267 | 0.1491 | 0.1118 | -0.0745 | 3.107 | 2.6196 |
| `C161` | 161 | 0.3975 | 0.0807 | 0.1615 | -0.0124 | 3.835 | -0.2612 |
| `C264` | 264 | 0.3788 | 0.0795 | 0.1591 | 0.0 | 3.854 | -0.5765 |
| `C360` | 360 | 0.3778 | 0.075 | 0.1417 | -0.0028 | 3.837 | -0.4254 |
| `N260` | 260 | 0.2577 | 0.0769 | 0.1077 | -0.0231 | 3.875 | 0.0281 |
| `F212` | 212 | 0.816 | 0.1274 | 0.0236 | -0.0236 | 2.728 | 0.4639 |
| `E264_scr1` | 264 | 0.5606 | 0.1402 | 0.0303 | -0.0152 | 3.154 | 0.1944 |
| `E264_scr2` | 264 | 0.5606 | 0.1402 | 0.0303 | -0.0152 | 3.154 | 0.144 |
| `E264_scr3` | 264 | 0.5606 | 0.1402 | 0.0303 | -0.0152 | 3.154 | 0.0619 |
| `C264_scr1` | 264 | 0.3788 | 0.0795 | 0.1591 | 0.0 | 3.854 | -0.4979 |
| `C264_scr2` | 264 | 0.3788 | 0.0795 | 0.1591 | 0.0 | 3.854 | -2.8437 |
| `C264_scr3` | 264 | 0.3788 | 0.0795 | 0.1591 | 0.0 | 3.854 | -1.0263 |
| `E264_E15` | 264 | 0.4848 | 0.1288 | 0.178 | -0.1629 | 3.288 | 30.5695 |

⚠ **Read the scramble rows, because they bound what N1 can prove.** A composition-preserving shuffle leaves **every composition descriptor byte-identical** to its parent and moves only **SCD**, which is order-dependent. Both facts are asserted by the guard suite rather than eyeballed here. So a scramble-sensitive ν shows the simulation exceeds *composition* — it does **not** by itself show it exceeds the manuscript's full descriptor set, because SCD is in that set and the scramble does not hold it fixed. That is a limit of the prespecified null, stated rather than glossed.

## 6 · Convergence

ν on the second half of each trajectory against ν on the whole post-equilibration trajectory. Largest drift **0.0519**; **14 of 55** runs drift by more than the pooled replicate SD (25%). Converged by the frozen rule: **no**.

⚠ **Every ν above is therefore labelled PROVISIONAL** — reported, never withheld, per Amendment 1.

## 6.2 · The same seed, run twice on different machines

The pilot run and the matrix's own `T161_r1` carry the **same deterministic seed** and the same protocol, on two different GitHub runners. This was not designed as a control; it fell out of running a pilot before the matrix, and it turned out to be the most useful single check in the arm.

| | pilot | matrix | 
|---|---:|---:|
| seed | 1714282698 | 1714282698 |
| ν | 0.5011 | 0.5231 |
| R_g (nm) | 3.3674 | 3.4503 |
| trajectory SHA-256 | `3fc44ac77d63afa5…` | `e99455803c2fe5d9…` |

**The trajectories are not identical and |Δν| = 0.0219.** A fixed seed does not make the CPU platform bit-reproducible across machines. ⭐ The number that matters is the comparison: that gap is **1.15× the pooled replicate SD** of 0.0191. Two runs that were meant to be the same differ by about as much as two deliberately independent replicates do — which confirms the noise floor by a second, independent route rather than from the replicate design that defines it.

## 7 · Claim ceiling

nu is a single-chain conformational observable. A difference in nu between two retained partner segments is a difference in nu between two retained partner segments. No saturation concentration, phase diagram, condensate, efficacy, patient-level selectivity, safety, therapeutic window or clinical readiness is measured or claimed.

## 8 · What was not run

- **The slab phase-coexistence arm** — multi-chain direct coexistence, the arm that would make *phase behaviour* a measurement rather than the model's premise. It needs a GPU, it is a real-dollar spend, and nothing here authorises it.
- **The multi-domain (CALVADOS 3) reading** of the full type-1 retained segment (EWSR1 1–431, which runs into the folded RRM at 361–442) and of the full-length chimeras.
- **Mpipi**, the other member of the model family.

