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

**INCOMPLETE — the run set does not match the frozen manifest, so no verdict about any partner is emitted.** This is not a negative result and must never be read as one. An absent reading is not a reading of absence; the missing runs are named below and the arm is finished when they land.

Conditions that fired:

- C161: 0 of 5 replicates carry a nu — the run set does not match the frozen manifest, so no verdict about any partner is emitted
- C264: 0 of 5 replicates carry a nu — the run set does not match the frozen manifest, so no verdict about any partner is emitted
- C264_scr1: 0 of 2 replicates carry a nu — the run set does not match the frozen manifest, so no verdict about any partner is emitted
- C264_scr2: 0 of 2 replicates carry a nu — the run set does not match the frozen manifest, so no verdict about any partner is emitted
- C264_scr3: 0 of 2 replicates carry a nu — the run set does not match the frozen manifest, so no verdict about any partner is emitted
- C360: 0 of 5 replicates carry a nu — the run set does not match the frozen manifest, so no verdict about any partner is emitted
- E264: 0 of 5 replicates carry a nu — the run set does not match the frozen manifest, so no verdict about any partner is emitted
- E264_E15: 0 of 3 replicates carry a nu — the run set does not match the frozen manifest, so no verdict about any partner is emitted
- E264_scr1: 0 of 2 replicates carry a nu — the run set does not match the frozen manifest, so no verdict about any partner is emitted
- E264_scr2: 0 of 2 replicates carry a nu — the run set does not match the frozen manifest, so no verdict about any partner is emitted
- E264_scr3: 0 of 2 replicates carry a nu — the run set does not match the frozen manifest, so no verdict about any partner is emitted
- E360: 0 of 5 replicates carry a nu — the run set does not match the frozen manifest, so no verdict about any partner is emitted
- F212: 0 of 5 replicates carry a nu — the run set does not match the frozen manifest, so no verdict about any partner is emitted
- N260: 0 of 5 replicates carry a nu — the run set does not match the frozen manifest, so no verdict about any partner is emitted
- T161: 0 of 5 replicates carry a nu — the run set does not match the frozen manifest, so no verdict about any partner is emitted

## 2 · What was run

- Constructs in the frozen manifest: **15**; runs: **55**; analyses reduced: **0**.
- Protocol: CALVADOS 2, 293.15 K, 0.19 M ionic strength, pH 7.5, 10 fs timestep, 1010 frames × 7000 steps, first 10 discarded, 150 nm box, CPU platform.
- Pooled replicate SD of ν: **—**; separation threshold (3 SD): **—**.

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

## 7 · Claim ceiling

ν is a single-chain conformational observable. No efficacy, no selectivity in a patient, no safety, no therapeutic window, no clinical readiness.

## 8 · What was not run

- **The slab phase-coexistence arm** — multi-chain direct coexistence, the arm that would make *phase behaviour* a measurement rather than the model's premise. It needs a GPU, it is a real-dollar spend, and nothing here authorises it.
- **The multi-domain (CALVADOS 3) reading** of the full type-1 retained segment (EWSR1 1–431, which runs into the folded RRM at 361–442) and of the full-length chimeras.
- **Mpipi**, the other member of the model family.

