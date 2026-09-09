---
id: DOC-PORTFOLIO-INVESTIGATION-PUB-DEGRADER-20260908
title: "PUB-DEGRADER portfolio investigation — is the covalent axis's exposure separation reproducible across the independent replicas it is pooled from?"
level: L4
kind: investigation-finding
status: live
date: 2026-09-08
last_verified: 2026-09-08
lane: PUB-DEGRADER
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# PUB-DEGRADER — exposure separation, read per replica

## 1 · The question

The manuscript's covalent categorical axis rests on one exposure statement read from **pooled**
75-frame unbiased ensembles: every NR4A1/NR4A2 LBD cysteine has an RSA that *"never exceeds 0.2126"*
(§2.10 audit paragraph 2), while NR4A3's unique **C397** sits above it (pooled p10 0.298, median
0.416). Those 75 frames are **three independent release replicas pooled**. **Does the separation hold
inside each replica, or is it a property of the pool?** — and does replicate structure change
anything about `V17`'s failed positive control (NR4A1 **C551**)?

## 2 · Paper-level merit

Patient relevance is indirect but real: the covalent handle is the one selectivity axis in this paper
that does **not** inherit the free-energy engine's unvalidated status, so it carries the paralogue
argument that a future EMC degrader would be designed around. The paper's own abstract names
**cross-replica convergence** as a principal unresolved limitation and applies that scepticism to the
pocket/free-energy blocks — but the exposure figure under the categorical axis is quoted **pooled and
unqualified**. Checking whether a load-bearing number survives the replicate structure it was pooled
from is a non-trivial contribution, cheap, and it can only strengthen or correctly qualify the
paper's most model-independent claim.

## 3 · The exact evidence gap, and how it differs from completed and held work

* **Completed and NOT re-done here:** the pooled exposure read (`nr4a3-covalent-handle-ensemble.json`,
  `nr4a-paralogue-dynamics.json`), the reach-only categorical verdict (`categorical_verdict`, C9–C12),
  the 8XTT experimental-ensemble exposure of C397/C420/C559, the `C7` cutoff's known-defective status
  and the §2.10 audit that already records the C551 false negative and the 0.2126 ceiling.
* **Held / out of scope and NOT touched:** every free-energy construct (`abfe_conditional` + λ-repair,
  `dg_open_paralogue`, `valB_full`, Arm F, the restrained binary re-run, MM-GBSA rescore, `V4`), the
  MF1 record and its R1–R5 residuals, R1–R4, the unadmitted R2 work.
* **Failed source attempts NOT re-opened:** the cysteine-chemoproteomics precheck
  (`cys-chemoproteomics-precheck.json`, `STOP_NO_REFERENCE`, proxy-blocked tables), `pmx`
  `STOP_NO_REFERENCE`, and the closed B1/B2/B4 routes. No network read was made in this lane.
* **The gap:** `nr4a-paralogue-dynamics.json` publishes RSA distributions **per ensemble**
  (`release_rep0/1/2`, 25 frames each, per species, per cysteine). Nothing in the manuscript, the
  program map or that artifact's own summary reads the exposure separation **per replica** — every
  quoted exposure figure is the pooled one. The inputs were already computed; only the reading was
  missing.

## 4 · The bounded step taken

`exposure_separation_per_replica.py` (pure stdlib, $0, read-only) re-reads
`research/modalities/nr4a-paralogue-dynamics.json` → `term_a.by_species[*].ensembles[release_rep*]`
and, **per replica**, compares NR4A3 C397/C420/C559 against the **ceiling over every NR4A1 and NR4A2
cysteine in that same replica**. The biased `metad` ensemble is excluded exactly as the source
artifact excludes it. Output: `artifacts/exposure-separation-per-replica.json`.

### Result — the separation is reproducible at the p10 level and materially replica-dependent below it

| replica | paralogue ceiling (any Cys, any frame) | C397 min / p10 / median | margin @p10 | margin @min |
|---|---|---|---|---|
| release_rep0 | **0.1737** (NR4A2 C534) | 0.1082 / 0.1988 / 0.3312 | +0.0251 | **−0.0655** |
| release_rep1 | 0.1940 (NR4A2 C534) | 0.2722 / 0.3556 / 0.4542 | +0.1616 | +0.0782 |
| release_rep2 | 0.2126 (NR4A1 C465) | 0.2993 / 0.3225 / 0.4128 | +0.1099 | +0.0867 |

1. **C397's p10 exceeds its own replica's paralogue ceiling in 3/3 replicas** — the pooled separation
   is *not* an artifact of pooling. That is a genuine strengthening of the paper's most
   model-independent axis.
2. **But the margin spans 0.025 → 0.162, a ~6.5× range**, and in `release_rep0` the separation is
   **negative at the frame floor** (C397's least-exposed frames fall below that replica's paralogue
   ceiling). "No overlap at any frame" is **not** supported; "separated for ≥90 % of frames within a
   replica" is.
3. **Treating the replicas as the exchangeable draws they are, the worst-case cross-replica margin at
   p10 is −0.0138** (rep0's C397 p10 0.1988 against rep2's ceiling 0.2126). A statement of the form
   *"90 % of C397 frames are more exposed than any paralogue cysteine"* therefore holds
   replica-matched and **fails** in the worst replica pairing. The pooled figure sits at the
   favourable end of its own replicate spread.
4. **C420's exposure edge is not reproducible**: its median exceeds the paralogue ceiling in
   `release_rep0` **only** (0/3 for C559). The paper's "one residue deep" reading, established on
   *reach*, is independently confirmed on *exposure* — and the second handle's apparent exposure
   advantage is a single-replica effect that should not be quoted.
5. **The positive control fails identically in every replica.** NR4A1 C551 max RSA = 0.091 / 0.133 /
   0.120, below its replica ceiling in all three. Replicate structure does **not** repair `V17`'s
   false negative; it shows the failure is reproducible rather than a pooling accident. No cutoff
   above the paralogue ceiling can retain the one proposed real covalent NR4A site.

**Artifact** `artifacts/exposure-separation-per-replica.json` + the script.
**Validation / baseline** the script reproduces the manuscript's quoted pooled ceiling exactly
(**0.2126, NR4A1 C465**) from the same file before splitting by replica; the pooled C397 quantiles it
recovers (min 0.108 / p10 0.298 / median 0.416) match the values already committed in §2.10 and the
program map, so the re-read is anchored to published numbers on both sides.
**Provenance** single input `research/modalities/nr4a-paralogue-dynamics.json` (landed artifact,
75 unbiased frames/species over 3 replicas, Shrake–Rupley RSA, `metad` excluded); no network, no GPU,
no paid compute, nothing outside this directory written.
**Limitations** (a) the source publishes **quantile summaries, not per-frame RSA**, so per-replica p10
over 25 frames is coarse and no exact frame-level overlap fraction can be computed here; (b) replica
indices are **not** physically paired across species — the replica-matched comparison is a
within-run reading and the cross-replica worst case is reported alongside it precisely because the
pairing is arbitrary; (c) these are biased-CV-released MD ensembles, **not** Boltzmann-weighted, so
frame fractions are heterogeneity statements, not populations; (d) RSA is a geometric quantity —
**nothing here bears on thiol pKa, nucleophilicity, adduct stability, promiscuity, degradation,
selectivity in cells, efficacy, safety or any therapeutic window**, and there is no wet lab; (e) this
qualifies a *reading*, it retracts nothing: the 12-atom gate is carried by reach, not exposure.
**Stop condition** met — the per-replica question is answered in both directions from committed
inputs. This lane stops here; it does **not** re-open the C7 cutoff, the chemoproteomics route, or
any held free-energy construct.

## 5 · Proposed prose qualifier — UNAPPLIED, for the paper owner

No shared file was edited. Suggested qualification where §2.10 quotes the pooled ceiling (exact
wording is the owner's):

> The paralogue ceiling (RSA ≤ 0.2126) is a **pooled** figure over three release replicas. Read per
> replica, C397's p10 exceeds its own replica's paralogue ceiling in 3/3 replicas, but the margin
> spans 0.025–0.162 and is negative at the frame floor in one replica; the worst-case cross-replica
> p10 margin is −0.014. C420's exposure advantage appears in one replica only.

## 6 · Next credible independent work (not started)

A per-frame RSA export from the same committed conformers would convert the quantile bounds above
into exact overlap fractions and a proper replica-level confidence statement, at $0 CPU — it needs
the conformer sets under `results/nr4a{1,2,3}-*-ensemble`, not new sampling. **It would still not
supply a known answer for covalent ligandability**; that dependency remains the recorded
`STOP_NO_REFERENCE`, and no exposure statistic can substitute for it.
