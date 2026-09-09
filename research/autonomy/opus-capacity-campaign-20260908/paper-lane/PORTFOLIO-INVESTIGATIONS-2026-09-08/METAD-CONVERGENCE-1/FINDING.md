---
id: DOC-OPUS-CAMPAIGN-METAD-CONVERGENCE-1
title: "METAD-CONVERGENCE-1 — the NR4A3-LBD pocket-opening free energy is not resolved beyond replica noise"
level: L4
kind: investigation-finding
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# METAD-CONVERGENCE-1

## Question

Across the three committed NR4A3-LBD well-tempered metadynamics replicas, is the pocket-opening
free-energy difference `dF_open` resolved beyond replica-to-replica noise — and what is the
smallest free-energy difference this ensemble can distinguish from noise at all?

## Merit rationale

The degrader program's pocket-opening argument rests on a *magnitude*: a claim that the opened,
ligandable state of the NR4A3 ligand-binding domain sits at a particular free-energy cost relative
to the closed state. Every downstream statement that leans on that number — how populated the open
state is, how it ranks against other conformations — inherits its uncertainty. The published
per-replica convergence diagnostic is a *within-run* block-to-block residual, which measures only
whether one trajectory stopped moving; it cannot see a run that converged confidently to the wrong
place. Three independent replicas exist and were never compared against each other. Establishing the
resolution floor of the existing ensemble is cheap, uses only committed data, and either supports
the magnitude or bounds every claim resting on it. Patient relevance is indirect and remote: it
governs whether a computational pocket argument in a rare-cancer target program is worth carrying
forward, not any clinical property.

## Evidence gap

`results/nr4a3-metad-analysis-r{1,2,3}/metad_analysis_summary.json` each report a
`final_block_to_block_max_dF_kJ` (0.281, 1.65, 0.256 kJ/mol) as the replica's convergence error.
Those three numbers were never differenced against one another, and DISCOVERY-2 recorded no hashes
for the inputs. The unfinished gap is the *between-replica* term: the spread of the same observable
across independent runs, set against the within-replica error, with a stated resolution floor. This
is distinct from prior completed work, which established per-replica convergence signatures,
recrossing counts and an orthogonal gate-distance corroboration — all of them single-replica
statements.

## Step taken

Recomputed `dF_open` directly from the committed block free-energy profiles of all three replicas,
in place, and compared the within-replica half-block error against the between-replica spread.

`dF_open` = min F over sampled Rg > 0.9 nm minus min F over sampled Rg <= 0.9 nm, inside the
metadynamics wall region [0.45, 2.2] nm. The 0.9 nm boundary is the published `boundary_rg_nm` from
the recrossing analysis. Grid points sitting exactly at a block's ceiling value are unsampled filler
and are excluded from basin minima. Within-replica error is the half-block estimate
`|dF_open(20.0 ns block) − dF_open(30.2 ns block)|`. The resolution floor is the larger of the
between-replica range and the worst within-replica half-block error.

**The between-replica comparison was run blind.** Replica labels were replaced by pseudonyms under
a seeded permutation (seed 20260908; A→r2, B→r3, C→r1), the spread, the floor and the resolved/not
verdict were all computed from the pseudonymous set, and the mapping was applied only afterwards.
The blinded record is retained in the artifact under `blinding.blinded_record`, so the between-
replica spread could not have been tuned to a known replica identity.

### Result — the decisive negative

| replica | dF_open (kJ/mol) | within-replica half-block error | published per-replica error |
|---|---|---|---|
| r1 | 5.321 | 5.315 | 0.281 |
| r2 | 78.591 | 15.155 | 1.650 |
| r3 | 172.598 | 17.820 | 0.256 |

* Signal (mean `dF_open`): **85.5 kJ/mol**
* Between-replica range: **167.3 kJ/mol**; SD across replicas 83.9 kJ/mol
* Worst within-replica half-block error: **17.8 kJ/mol**
* **Resolution floor: 167.3 kJ/mol**
* **Resolved beyond replica noise: NO** (85.5 < 167.3)

The between-replica spread is roughly two times the signal, and roughly ten times the worst
within-replica error — the three runs disagree with each other far more than any of them wavers
internally. The published per-replica errors (0.26–1.65 kJ/mol) understate the true uncertainty of
this observable by two orders of magnitude; they are within-run residuals, not error bars on
`dF_open`.

The negative does not depend on where the closed/open boundary is drawn. At every boundary from
0.80 to 1.00 nm the signal stays below the floor (`boundary_sensitivity` in the artifact; all rows
reported, none preferred). At 0.80 nm the three replicas do not even agree on the **sign**
(−27.9, +24.3, +54.4 kJ/mol). Beyond 1.05 nm one side of the boundary is entirely unsampled and
`dF_open` is undefined. The underlying cause is visible in the profiles: each replica explored a
different narrow Rg window and placed its global minimum in a different place (0.87, 0.73, 0.74 nm),
so the open side of the boundary is a well-sampled basin in r1 and an unsampled barrier shoulder in
r3.

**Consequence.** The NR4A3-LBD pocket-opening free-energy difference is **not resolved** by this
three-replica ensemble. Any claim that rests on its magnitude is bounded by a 167 kJ/mol resolution
floor — which is to say, unbounded in practice. No sub-window, reweighting or replica subset was
sought under which it would become resolved, and none should be: with an inter-replica range larger
than the value itself, such a selection would be fitting the answer.

## Artifact

`metad-cross-replica-convergence.json` — inputs with re-computed SHA-256 and byte counts, the
observable definition, per-block and per-replica `dF_open`, the blinded record and the unblinding
map, the between-replica spread, the resolution floor, the three checks, and the boundary
sensitivity table.

Scripts: `cross_replica_convergence.py`, `boundary_sensitivity.py`.

## Validation / baseline

Three checks, each able to fail:

1. `half_block_error_bounds_published_per_replica_error` — **PASS**. For every replica the
   half-block estimate (5.3 / 15.2 / 17.8 kJ/mol) bounds the published per-replica error
   (0.281 / 1.65 / 0.256). Had it come in below, the half-block estimate would have been the
   defective one; it did not.
2. `between_replica_comparison_run_blind` — **PASS**. Seeded label permutation applied before the
   spread was computed; both blinded and unblinded records retained.
3. `signal_exceeds_resolution_floor` — **FAIL**, and this failure is the finding. 85.5 kJ/mol
   signal against a 167.3 kJ/mol floor.

Baseline: the published within-replica convergence diagnostic, which the between-replica term
exceeds by roughly a factor of ten.

## Provenance

All inputs read in place from the committed tree; no copies made. SHA-256 re-computed at use and
recorded in the artifact (`inputs`):

```
6cc3a657a85f68a46b3463892327d134d57dc1a126059f0a365f365e14ad97e3  results/nr4a3-metad-analysis-r1/fes_blocks.json
88513ff8f709d16beaf33b88d983c9e135a6669ea4ffc79960a703a835a13302  results/nr4a3-metad-analysis-r2/fes_blocks.json
1ac0046abe14eb1903917aeddd0980f9f55f6e11dad05df757d4a71969a3a84f  results/nr4a3-metad-analysis-r3/fes_blocks.json
39a1dc48aa8cc690bf5d3d49e9b878da385ef02f7ee102481240745e903ba04c  results/nr4a3-metad-analysis-r1/metad_analysis_summary.json
623e3c57cab7b787d7978f7041d971ea2080904ac172c5d060e5b29576f9ccae  results/nr4a3-metad-analysis-r2/metad_analysis_summary.json
20194b72b5aa4ea50188f2338a478bcfc53c952e48fee38ee8c86ffea42835b5  results/nr4a3-metad-analysis-r3/metad_analysis_summary.json
```

`fes2d_rg_gate.json` and `MANIFEST.json` for each replica are hashed in the artifact as well.
DISCOVERY-2 recorded no hashes; these are first-recorded at this use and are not a check against a
prior record.

## Limitations

* Three replicas is a very small sample; the SD and range are themselves poorly determined. This
  weakens any *positive* statement about the size of the noise, but not the negative — a range
  exceeding the signal at n=3 already denies resolution.
* The half-block error uses the 20.0 ns block against the 30.2 ns block, the finest split the
  committed block files allow. A true half-and-half split of independent halves is not
  reconstructible without the trajectories, and no re-simulation was performed (no GPU, no
  re-simulation, per the standing deferral).
* `dF_open` is a one-dimensional projection onto Rg. The committed 2D `F(Rg, gate)` reweightings
  were hashed but not differenced across replicas; a 2D cross-replica comparison would be a
  separate step and would not rescue a 1D observable whose sign is replica-dependent.
* Unsampled ceiling masking is a per-block heuristic; where a basin minimum sits near the ceiling
  (r3's open side) the value is barrier-limited rather than a basin depth. This makes r3's
  `dF_open` conservative in the direction of a *larger* value, and so the spread reported here.
* **Scope.** A free-energy difference computed here is a property of this simulation ensemble. It
  is not evidence of druggability, selectivity, efficacy, safety or a therapeutic window, and no
  such claim is made or implied by this document.

## Stop condition

Met and stopped. Three replicas compared, resolution floor stated, decisive negative reached. No
fourth replica, no re-simulation, no sub-window or reweighting search for a configuration under
which the difference would appear resolved. The next credible independent work — not undertaken
here and requiring authority this lane does not hold — is additional independent replicas or a
longer, better-converged sampling protocol sufficient to bring the between-replica spread below the
claimed magnitude; until that exists, the pocket-opening free-energy magnitude should not be cited.
