---
id: DOC-OPUS-CAMPAIGN-DISCOVERY-2-PROPOSALS
title: "Ten new-science questions across the 33-endpoint portfolio, 2026-09-09"
level: L4
kind: proposal
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# Ten proposals — new analysis, not another audit

⛔ **PROVENANCE OF THIS FILE, STATED FIRST.** The DISCOVERY-2 worker completed its survey but
**could not write a single file**: the session's writable allowance was exhausted mid-run, and
`Write` failed with `ENOSPC` on the very `mkdir` for its lane directory. Per the campaign's own
disk-floor rule it **deleted nothing** and reported the condition instead of freeing space. The
parent resolved the disk condition afterwards and transcribed this content verbatim from the
worker's return.

⚠ **CONSEQUENCE: NO sha256 IN THIS FILE WAS COMPUTED.** The worker could not run `sha256sum` even
once. Byte counts and structural facts below come from successful `json.load` / `ls` calls made
before the disk filled. **Every locator must be re-hashed at the moment of dispatch.** Repo HEAD at
survey time: `65328136ec847a2ae4192cc8274cb6d5a12a6de2`. Environment measured before the failure:
numpy 2.4.6, scipy 1.17.1, Bio 1.88 present; pandas, sklearn, MDAnalysis, mdtraj, statsmodels
**absent**.

**Ranking rationale.** 1–4 can each return a decisive negative that removes or rescues a premise a
manuscript already leans on, on data held entirely locally. 5–7 create genuinely new evidence
objects with a real chance of a null. 8–10 are sound new analyses whose result is more likely to
confirm than to overturn.

## 1 · CISTROME-1 — is NR4A occupancy at RET distinguishable from background at all?

`research/modalities/emc-ret-cistrome.json` (1,469,536 B) holds `part_2_intersection.per_peakset`
with **110 peaksets**, each scoring a *multi-locus* panel (RET, ENO3, …) with `n_peaks_total`,
promoter (−10 k/+15 k) and gene-body window counts, and a `positive_control` verdict per peakset —
but `empirical_p_vs_background` is **reported only for RET**. Nobody has read the rest of the panel.
**Output** `ret-cistrome-locus-panel-null.json`: per locus × peakset, occupancy against the file's
own background null, restricted to peaksets that recover a known positive, with RET's rank in the
panel. **Check**: peaksets flagged `NO KNOWN POSITIVE RECOVERED` must show no enrichment; a
locus-label permutation must flatten the ranking; RET's recomputed p must reproduce the stored
0.4472 / 1.0. **Stop** at the panel table. Minutes CPU, <5 MB. Bears on the RET-inhibitor
repurposing premise; no efficacy claim follows.

## 2 · CISTROME-MOTIF-1 — does the NBRE motif scan predict measured occupancy?

Inputs `research/modalities/emc-ret-target-scan-inputs.json` (5,274,199 B),
`research/modalities/emc_ret_target_scan.py`, and the measured occupancy from proposal 1's inputs.
**Output** `motif-vs-occupancy-benchmark.json`: per locus, motif score against measured
promoter-window peak presence, with concordance and a discrimination statistic. **Check**: a
score-label shuffle must give chance concordance; known NR4A-target positive controls must sit
above the median, or the benchmark is reported as failing. **A negative here is high-value** —
several repository arguments rest on motif scans standing in for occupancy. **Stop** after one pass.

## 3 · EXPR-HYPOXIA-1 — is the residual EMC expression contrast a hypoxia program?

EXPR-COMPOSITION showed roughly half the two-platform contrast is a tumour/stroma marker score.
The untouched `research/modalities/emc-hypoxia-null-background.json` (7,975,969 B) holds, for both
series, a seeded (`_sample_seed` 20260807) random-background symbol set, `background_per_sample`,
and 118 named confound genes — a purpose-built null universe. With
`research/modalities/emc-expression-panels.json` (13,254,759 B; **mtime 2026-09-08 23:23, working
tree — re-hash and state which version**). **Output** `hypoxia-residual-attribution.json`.
**Check**: reproduce EXPR-COMPOSITION's attenuation exactly before adjusting, and abort otherwise;
the seeded random background must **not** attenuate. **Stop** at primary + secondary frames.

## 4 · METAD-CONVERGENCE-1 — is the pocket-opening free energy resolved beyond replica noise?

`results/nr4a3-metad-analysis-r{1,2,3}/{fes_blocks.json,fes2d_rg_gate.json,metad_analysis_summary.json}`
— three independent replicas, all small; `results/nr4a3-metad-r{1,2,3}/` hold checkpoints and
MANIFEST. **Output** `metad-cross-replica-convergence.json`: within-replica block error against
between-replica spread on the opening free-energy difference, with a stated resolution floor.
**Check**: the within-replica half-block estimate must bound the published per-replica error, and
the comparison must be run blind to which replica is which. **Decisive negative available** (spread
≥ signal). No GPU, no re-simulation.

## 5 · PARALOGUE-SHAPE-1 — does NR4A3's pocket visit states the paralogues never do?

`results/nr4a1-pocket-ensemble/`, `results/nr4a2-pocket-ensemble/`,
`results/nr4a3-pocket-reharmonize/` (≈98 MB total, **read in place, never copied**). Distinct from
DEGRADER-2 (per-cysteine RSA) and MONOVALENT-3 (clash sweep): per-frame *pocket geometry* —
lining-residue distance matrix and pocket Rg — with a variance decomposition into species against
replica. **Output** `paralogue-pocket-shape.json`. **Check**: a species-label permutation must
abolish separation, and replica-against-replica within a species is the baseline the species
contrast must beat. Bio.PDB only. Geometry only — no selectivity, efficacy or window claim.

## 6 · ORPHAN-CENSUS-1 — is EWSR1::NR4A3's "orphan" status real or a retrieval artefact?

`research/modalities/fusion-junction-orphan-census.json` (705,801 B): 198 fusion pairs already
fetched from Europe PMC with modality and junction term hits, carrying its own
`⚠_short_symbols_stay_noisy` caveat. No lane has used it. **Output**
`junction-modality-coverage-benchmark.json`: coverage across the 198 pairs, EWSR1::NR4A3's
position, and orphan status stratified by symbol length. **Check**: BCR::ABL1, EWSR1::FLI1 and
PAX3::FOXO1 must be non-orphan; ≤3-character symbols reported separately. No egress — held rows
only.

## 7 · THRESHOLD-CALIB-1 — the class I threshold PUB-VACCINE-PATH says is unmeasured

`research/modalities/iedb-validated-epitope-cache.json` (433,695 B; `arm_F_records` 988,
`arm_N_records` 965, from 6,108 / 6,000 raw rows) and
`research/modalities/epitope-allele-matrix-mhcnuggets.json` (588,303 B; 174 peptides × 34 alleles =
5,916 cached calls, `alleles_without_a_model` 0). **Output** `threshold-calibration.json`:
discrimination of the repository's threshold on the overlapping peptide/allele set — **or**, if the
cached call set does not intersect the IEDB arms, the exact missing predictor-call set, recorded as
a decisive negative. MHCnuggets is not installed and its weights are a large download, so no
re-scoring. **Check**: label-shuffled discrimination ≈ chance. HLA-C stays excluded (B8).

## 8 · REPURPOSE-DECOY-1 — is the repurposing shortlist separable from property-matched decoys?

`research/modalities/nr4a3-repurpose-candidates.json` (1,437,223 B),
`research/modalities/property_matched_control.py`, `research/modalities/repurpose_dock_core.py`,
`results/nr4a3-decoy/`, `results/nr4a3-genmatched-control-c/`. **Output**
`repurpose-decoy-enrichment.json` — enrichment / AUC of the shortlist against property-matched
decoys. **Check**: the generation-matched scramble set must land at chance; a shortlist that does
not beat it is reported as such. Docking scores are not affinity and not efficacy.

## 9 · ASO-CHANCE-1 — how much junction specificity exceeds chance?

The ~20 held `junction-aso-offtarget-*-deep500-b{1,2}.json` files plus
`research/modalities/offtarget_chance_baseline.py` and `aso-control-oligos.json`. Read-only
comparison of observed off-target hit counts against a dinucleotide-preserving shuffled-oligo
baseline. **Output** `aso-offtarget-chance-baseline.json`. **Check**: the committed scramble
controls must land at baseline. ⛔ **Fence: reads only — frozen ASO and submitted assets are not
edited and no pin is touched.** If the parent judges any proximity to the frozen package
unacceptable, drop this one.

## 10 · UNIQUE-RESIDUE-ADDRESSABILITY-1 — are NR4A3's unique indel residues addressable geometry?

`research/modalities/nr4a-reciprocal-uniqueness-census.json` (512,443 B; pairwise and three-way
indel census) mapped onto the paralogue ensembles of proposal 5: are unique residues
surface-exposed and pocket-proximal, or scattered and buried? **Output**
`unique-residue-addressability.json`. **Check**: a uniqueness-label permutation must abolish any
clustering. Distinct from DEGRADER-2, which scored cysteines, not indels.

## Dropped as ineligible, each for a real fence

Per-line DepMap CSVs (large download plus egress); HPA / surfaceome (B4 closed); the HLA-C panel
(B8, excluded); Ensembl FASTA (B1/B2); a clinicaltrials.gov ablation (egress refused, curl exit
56); an MHCflurry re-run (not installed, large weights); the four GSE170983 peak files in the
cistrome record (build-ambiguous **and** needing GEO egress); anything touching
PUB-EMC-CLASSIFICATION (user-rejected); MF1, P-ST, TCIP and FP (closed accepted science); any
GPU-requiring MD extension.
