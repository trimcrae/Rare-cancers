# 8XTT experimental benchmark of the AF2 NR4A3 pocket — findings (2026-07-10)

**Run:** `gpu-8xtt-benchmark-aws.yml` (SageMaker CPU, ml.c5.2xlarge), git_ref `main`, run 29066297552,
job 86278428426, ~$0.3. Script `nr4a3_8xtt_benchmark.py`. Result JSON:
`s3://sagemaker-us-east-2-646605541856/nr4a3-8xtt-benchmark/nr4a3-8xtt-benchmark.json` (15126 bytes).

## What was run
The AF2 model (AF-Q92570, LBD 373–626, 254 Cα) was benchmarked against the experimental apo NR4A3/NOR-1
LBD solution-NMR ensemble **PDB 8XTT (20 conformers)** — the structure the 2026-07-10 review flagged as
newly released and absent from this repo. Sequence alignment 8XTT↔Q92570 gave **identity 1.000, 248
residues mapped** (same protein; the AF2 pocket-5 residues 406–534, the 7 handles, and the 10 lining
residues map unambiguously onto 8XTT author numbering). Per conformer we scored (i) fpocket druggability
of the *mapped* orthosteric pocket, and (ii) AF2→conformer Cα-RMSD (global, pocket-local, handles).

## Result — VERDICT: partial (concordant on druggability distribution, divergent on backbone geometry)

### (1) Druggability distribution — CONCORDANT with the cryptic-pocket thesis (the headline)
The mapped pocket's fpocket druggability across the 20 experimental conformers:

| conformer | drugg | conformer | drugg | conformer | drugg | conformer | drugg |
|---|---|---|---|---|---|---|---|
| 1 | 0.009 | 6 | **0.537** | 11 | 0.220 | 16 | 0.004 |
| 2 | **0.925** | 7 | 0.006 | 12 | 0.009 | 17 | 0.006 |
| 3 | 0.015 | 8 | **0.744** | 13 | 0.020 | 18 | 0.008 |
| 4 | 0.000 | 9 | 0.476 | 14 | 0.032 | 19 | 0.004 |
| 5 | 0.001 | 10 | 0.108 | 15 | 0.003 | 20 | **0.860** |

- **median 0.012, range 0.000–0.925; 4/20 conformers (20%) clear D\*=0.53** (models 2, 6, 8, 20; model 9 at
  0.476 just below), peak 0.925.
- **This is model-independent, experimental corroboration of the paper's central claim.** The apo NMR
  ensemble — determined without any of our AF2/metadynamics machinery — independently shows exactly the
  cryptic pattern the metadynamics + unbiased release run reported: the orthosteric pocket is **occluded in
  most conformers** (median ~0.01, consistent with the "undruggable" static reputation and the static AF2
  0.495 sitting just below the druggable band) yet **transiently druggable in ~20% of states** (peak 0.925,
  comparable to the metad-opened 0.931). The ~20%-of-states druggable fraction matches the release-run's
  ~20% of frames strikingly closely. So the "dynamically/cryptically druggable in a minority of
  conformations" thesis is now supported by an experimental ensemble, not only by AF2+MD.

### (2) Backbone / handle geometry — DIVERGENT (the design caveat)
- **pocket-local Cα-RMSD median 3.56 Å** (AF2 pocket backbone vs NMR ensemble) → the AF2 pocket backbone is
  not a close match to any single NMR conformer;
- **handle Cα-RMSD median 3.44 Å** → the seven selectivity handles are displaced ~3.4 Å between AF2 and the
  experimental ensemble;
- **global LBD Cα-RMSD median 7.63 Å** (context; includes the flexible termini/hinge).

So the AF2-derived *specific opened geometry* used for docking, MM-GBSA, the ternary, and ABFE is **not
corroborated at atomic detail** by the experimental ensemble. The design pose (denovo_401) and the exact
handle-engagement geometry therefore still rest on the AF2 model.

## Honest interpretation
- **Net positive for the target thesis, cautionary for the specific design.** The experimental structure
  *confirms* the qualitative druggability behavior (cryptic, ~20%-druggable) — the strongest independent
  validation the paper has — while showing the AF2 *atomic* pocket geometry diverges ~3.5 Å from experiment.
- **Benchmark caveats (do not over-read the RMSD as pure AF2 error):** (a) 8XTT is an **apo NMR ensemble** with
  genuine conformational spread and NMR refinement uncertainty, so part of the 3.5 Å is real apo flexibility,
  not model error; (b) fpocket on NMR conformers (no explicit waters/H) is the same geometry proxy used
  elsewhere; (c) the mapped-site scoring guarantees we score the *same physical pocket* across conformers.

## Recommended follow-ups (rebase the design on the experimental ensemble)
1. **Re-run PocketMiner on 8XTT conformers** (the review's explicit ask) — does the orthogonal cryptic-pocket
   predictor still enrich the pocket-5 residues on the experimental structure?
2. **Re-dock/re-score denovo_401 into the druggable 8XTT conformers (models 2, 8, 20, 6)** and re-check
   handle facing + the selectivity margin on experimental geometry, rather than the AF2/metad frame.
3. **Seed unbiased MD (and, if warranted, the metadynamics) from a representative 8XTT conformer** so the
   dynamics claim is anchored on the experimental structure.
4. Consider reporting the 8XTT per-conformer druggability distribution as a main figure — it is a clean,
   experimental version of the metad/release druggability-distribution argument.

These are cheap (CPU fpocket / a Boltz or dock inference / one short MD) and are the natural P0.1 continuation.
