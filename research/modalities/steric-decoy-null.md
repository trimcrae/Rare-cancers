# `C25` — the cross-system decoy null for the steric-exclusion axis (`S3`)

**contrast (a) UNGRADEABLE_too_few_graded_rows · contrast (b) UNGRADEABLE_too_few_graded_rows — primary background `partner_swap`, n = 3 / 3**

INSTRUMENT CALIBRATION. $0 CPU/CI. Nothing here is a claim about binding, affinity, reactivity, degradation, efficacy, safety or clinical readiness.

> This calibrates the STERIC SCREEN, not NR4A3. A contrast is only evidence about NR4A3 to the extent that an arbitrary close paralogue pair does NOT reproduce it.

## The plain reading

- CONTRAST (a) — bulkier-in-both vs the conserved/shared null. NR4A3 (matched index row) signal_minus_null = 0.625. Background over 3 graded arms: median 0.583, q75 0.666, max 0.75. NR4A3 sits above 0.6667 of the background (resolution 0.3333). VERDICT: UNGRADEABLE_too_few_graded_rows.
- CONTRAST (b) — the unique-but-NOT-bulkier class, which fires at 0.000 on NR4A3. Background over 3 graded arms: frac_exactly_zero = 1.0 (Wilson 95% [0.4385, 1.0]), median 0.0. VERDICT: UNGRADEABLE_too_few_graded_rows.
- ⛔ THE INDEX ARM'S VALUE IS EXACTLY THE BACKGROUND'S MODAL VALUE (0.0, 3 of 3 rows). Its percentile IS that modal frequency — ONE measurement, not two. Do not quote them as independent evidence.
- SECONDARY (`full_trio`, target and both partners swapped): filtered clash contrast 0 graded arms, verdict UNGRADEABLE_empty_background — and the pre-registration PREDICTED this from the smoke, because transporting a pose set docked into NR4A3 into another target's frame drops the poses (attrition: [0, 0]). The unfiltered sensitivity, biased DOWNWARD on decoys, graded 0 arms at verdict UNGRADEABLE_empty_background. ⭑ The half that is immune to all of this is the POSE-FREE volume axis: 0 graded arms, index 1.0, verdict UNGRADEABLE_empty_background.
- ⛔ AND THE CEILING IS UNCHANGED BY ANY OF THIS: the paralogue RELOCATES these molecules by a median ~5.3 A rather than refusing them (`M4`), so `S3` constrains a POSE and never 'the paralogue cannot bind this molecule'. The transfer is rigid, and the target's absence of clash is guaranteed by construction and carries no information in any arm.

## The known-answer check

| check | committed | recomputed here | agrees |
|---|---|---|---|
| `M3` class rates | `{'unique_and_both_bulkier': 0.923, 'unique_not_bulkier': 0.0, 'conserved_or_shared': 0.173}` | `{'unique_and_both_bulkier': 0.923, 'unique_not_bulkier': 0.0, 'conserved_or_shared': 0.173}` | **True** |
| denied-lobe volumes | `11.78` | `11.78` | **True** |

⛔ the backgrounds in this file MUST be discarded — the code, not the biology, would be the finding.

## Background `partner_swap` (PRIMARY)

target = the committed NR4A3 opened model (`results/nr4a3-matrix/nr4a3-opened.pdb`), poses = the 13 committed docked molecules, positions = Pocket-5 (`C5`). The two proteins playing the paralogue ROLES are an arbitrary close pair from the universe, superposed onto NR4A3 by the same `superpose_paralogue` call `M3` makes.

**contrast (a) · signal − null** — index `0.625`, n = 3, resolution 0.3333, percentile (favourable direction) **0.6667**, verdict **UNGRADEABLE_too_few_graded_rows**. Background: min 0.583 / median 0.583 / max 0.75, `frac_exactly_zero` 0.0.

**contrast (a) · enrichment ratio** — index `2.667`, n = 2, resolution 0.5, percentile (favourable direction) **0.0**, verdict **UNGRADEABLE_too_few_graded_rows**. Background: min 4.491 / median 4.491 / max 4.491, `frac_exactly_zero` 0.0.

**contrast (b) · unique-not-bulkier rate** — index `0.0`, n = 3, resolution 0.3333, percentile (favourable direction) **0.0**, verdict **UNGRADEABLE_too_few_graded_rows**. Background: min 0.0 / median 0.0 / max 0.0, `frac_exactly_zero` 1.0.
  - ⛔ THE INDEX ARM'S VALUE IS EXACTLY THE BACKGROUND'S MODAL VALUE (0.0, 3 of 3 rows). Its percentile IS that modal frequency — ONE measurement, not two. Do not quote them as independent evidence.

**volume axis · fraction of signal positions clearing the arm's own bar** — index `1.0`, n = 3, resolution 0.3333, percentile (favourable direction) **0.6667**, verdict **UNGRADEABLE_too_few_graded_rows**. Background: min 0.0 / median 0.5 / max 1.0, `frac_exactly_zero` 0.333.

## Background `full_trio` (SECONDARY)

a trio {T, A, B} from the universe. T is superposed into the NR4A3 pose frame by `superpose_paralogue(T, nr4a3_opened)`; A and B are then superposed onto T-as-placed by the same function, so the partners are fitted to THEIR OWN target exactly as in `M3`. Positions = Pocket-5 mapped onto T through the same `corr_from_ref` chain. Poses = the same 13 molecules, unmoved.

**contrast (a) · signal − null** — index `0.625`, n = 0, resolution None, percentile (favourable direction) **None**, verdict **UNGRADEABLE_empty_background**. Background: min None / median None / max None, `frac_exactly_zero` None.

**contrast (a) · enrichment ratio** — index `2.667`, n = 0, resolution None, percentile (favourable direction) **None**, verdict **UNGRADEABLE_empty_background**. Background: min None / median None / max None, `frac_exactly_zero` None.

**contrast (b) · unique-not-bulkier rate** — index `0.0`, n = 0, resolution None, percentile (favourable direction) **None**, verdict **UNGRADEABLE_empty_background**. Background: min None / median None / max None, `frac_exactly_zero` None.

**volume axis · fraction of signal positions clearing the arm's own bar** — index `1.0`, n = 0, resolution None, percentile (favourable direction) **None**, verdict **UNGRADEABLE_empty_background**. Background: min None / median None / max None, `frac_exactly_zero` None.

## ⛔ Limits

- ⛔ This calibrates the SCREEN, not the protein. A distinctive contrast would say the steric predicate separates NR4A3 from an arbitrary close nuclear-receptor pair; it would still say nothing about binding, affinity, degradation, efficacy or safety, none of which is computed anywhere here.
- ⚠ RIGID TRANSFER, every arm. Partner side chains are held in their own modelled conformer and could rotate away. Every rate and every lobe is 'denied in this conformer', never 'denied'.
- ⚠ The target's absence of clash is guaranteed by construction (the poses were docked into NR4A3) and carries no information. Only the between-class contrast is gradeable — which is why `score_pose` refuses to emit a signal without its matched null, and why this file always reports both.
- ⚠ The decoy arms are ALPHAFOLD models trimmed to `C24`'s reference-anchored LBD window; the index target is the committed metadynamics-OPENED NR4A3 conformer. The partner source is matched (the index row's partners are AlphaFold models too); the TARGET source is not matched in `full_trio`.
- ⚠ A nuclear-receptor universe is not the proteome. Nothing here bounds the rate over the proteome, and no proteome-wide selectivity claim is made or implied.
- ⚠ Clustering: pairs and trios share proteins under `max_per_protein = 2`, and the three arms of one trio share all three proteins. The effective n is below `n_graded` and every Wilson interval here is, if anything, optimistic.
- ⚠ One superposition per partner, by iterative core refinement. Post-fit deviation is carried on every position so a reader can down-weight the worst ones, exactly as `M3` does.
- ⛔ Conditional on `R5`. The whole steric axis assumes the cryptic pocket is the right site, and the pose known-answer test `V3` returned INCONCLUSIVE on site selection. A background cannot repair that.
- ⛔ `C5`'s Pocket-5 lining set is mapped onto every decoy target by sequence alignment, so a decoy position is 'NR4A3's site, mapped', never 'this protein's own pocket'. That is the same convention the committed paralogue contrast uses and it has the same reading.
- ⚠ 13 poses is a small pose set and it is the committed selectivity-matrix library, not the carried candidate. The per-arm filter can only shrink it.

*Generated 2026-08-03 02:33 PM ET by `steric_decoy_null.py`.*
