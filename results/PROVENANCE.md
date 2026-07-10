# Provenance ledger — where each load-bearing result lives

Status legend: **GIT** = committed (permanent) · **S3** = in the SageMaker bucket only (run the archival
sweep to mirror to git) · **LOST** = expired from S3, regenerable via the listed script · **ZENODO** =
too large for git, for the DOI deposit.

_Last reconciled 2026-07-10. Run IDs for individual jobs are recorded in
`research/modalities/nr4a3-degrader-next-steps.md`; this ledger tracks durability, not every run._

## Manuscript-cited summary results — SAFE (committed in `research/modalities/*.json`)
These carry the numbers the paper cites; they survived the S3 loss because they were hand-committed.

| Result | git path | Status |
|---|---|---|
| fpocket NR-panel calibration (D*=0.53) | `nr4a-selectivity.json`, calibration in-repo | GIT |
| PocketMiner on AF2 (1.36× enrichment) | `nr4a3-pocketminer-result.json` | GIT |
| PocketMiner on 8XTT (1.40×, "enriches") | in `nr4a3-8xtt-benchmark-findings.md`; JSON at S3 `nr4a3-8xtt-pocketminer` | GIT (numbers) / S3 (raw) |
| 8XTT benchmark (druggability dist + RMSD) | `nr4a3-8xtt-benchmark-findings.md`; JSON at S3 `nr4a3-8xtt-benchmark` | GIT (numbers) / S3 (raw) |
| denovo_401 re-dock on 8XTT ("survives" 4/4) | `nr4a3-8xtt-benchmark-findings.md`; JSON at S3 `nr4a3-8xtt-redock` | GIT (numbers) / S3 (raw) |
| Selectivity handles / paralogue divergence | `nr4a-selectivity.json` | GIT |
| Superfamily liability screen | `nr4a-superfamily-selectivity.json` | GIT |
| Safety genetics (gnomAD/DepMap) | `nr4a-safety-genetics.json` | GIT |
| Repurposing shards + candidates | `nr4a3-repurpose-candidates.json`, `nr4a3-repurpose-shard-*.json` | GIT |
| Antitarget panel (denovo_401) | `nr4a3-antitarget-denovo401.json`, `nr4a3-antitarget-candidates.json` | GIT |
| Pan-NR4A readout (denovo_9) | `nr4a3-pan-readout.json` | GIT |
| Degradation-window model | `nr4a3-degradation-model.json` | GIT |
| ABFE calibration (methane, T4L) | `nr4a3-abfe-calibration.json` | GIT |
| Binary co-fold (Boltz-2) | `nr4a3-binary-cofold-result.json` | GIT |
| Lead-opt candidates | `nr4a3-leadopt-candidates.json` | GIT |
| ASO / fusion designs | `junction-aso-*.json`, `fusion-*.json` | GIT |

## Raw intermediates — LOST or S3-only (the reproducibility gap)
| Result | S3 prefix | Status | Regenerate via |
|---|---|---|---|
| DiffSBDD generation pool (denovo_401 era) | `nr4a3-denovo`, `-v2`, `-affinity` | **LOST** | `gpu-denovo-aws.yml` (`nr4a3_denovo.py`, seeds in blueprint) |
| Docking-matrix poses (SDF/scores) | `nr4a3-matrix` | **LOST** | `gpu-denovo-dock-aws.yml` / `nr4a3_matrix.py` |
| Selectivity ABFE windows / reduced potentials | `nr4a3-abfe` / `nr4a3-fep` | **S3?** (archive to confirm) | `gpu-fep-aws.yml` / `nr4a3_abfe.py` |
| Metad HILLS/COLVAR/fes/trajectory (r1/r2/r3) | `nr4a3-metad-r{1,2,3}` | **S3** (running 2026-07-10) → archive on completion | `gpu-metad-aws.yml` |
| MM-GBSA multi-snapshot outputs | `nr4a3-mmgbsa*` | **S3?** | `mmgbsa-aws.yml` |
| MD release trajectories | `nr4a3-release*` | **ZENODO** (`.dcd`) | `gpu-release-aws.yml` |

**Consequence for publication:** the *headline numbers are reproducible from git*, but the raw
generation pools + poses behind denovo_401's best-of-N selection are gone, so the winner's-curse
(generation-matched-null) control and a from-scratch DiffSBDD replication now require **re-generating** a
fresh pool rather than re-reading the original. This does not change any published value; it does mean the
DOI archive must be built from (a) the committed git results, (b) a fresh archival sweep of surviving S3
prefixes, and (c) re-generated pools where the originals expired.

## Action items
1. Run `archive-results-aws.yml mode=diagnose` → confirm the lifecycle rule (root cause) and what survives.
2. Run `archive-results-aws.yml mode=archive` → mirror all surviving durable results into `results/`.
3. Disable the S3 lifecycle expiration on the bucket (or route results to a no-expiry bucket) — **owner action** (needs AWS console).
4. Deposit the `too-big` (trajectory) manifest to Zenodo for the DOI archive.
5. Stop `nr4a3_8xtt_benchmark.py` (and any fpocket job) from uploading scratch to S3.
