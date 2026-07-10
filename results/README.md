# `results/` — the permanent home for computational outputs

**Why this exists (2026-07-10).** GPU jobs write to the SageMaker default bucket
`s3://sagemaker-us-east-2-<acct>/<prefix>/`, which is **ephemeral** — old raw outputs (the DiffSBDD
generation pools `nr4a3-denovo*.json`, the `nr4a3-matrix` docking poses) were **lost**, almost certainly
to an S3 lifecycle expiration. The `report-*-aws.yml` workflows only *printed* results; they committed
nothing. This directory + the archival workflow fix that: **every load-bearing result is mirrored into
git**, which is permanent, versioned, and the thing a Zenodo/DOI deposit is cut from.

## The durability rule (for every new job)
A result is not "saved" until it is in git. S3 + continuous-checkpoint upload keeps a job *crash-safe*;
it does **not** make the result *durable*. So:
1. **Small artifacts** (JSON/txt/csv/dat/HILLS/COLVAR/small PDB/SDF/manifests, ≤ 5 MB) → committed here
   under `results/<s3-prefix>/`.
2. **Large artifacts** (trajectories `.dcd/.nc/.xtc`, arrays) → too big for git; listed in the per-prefix
   `MANIFEST.json` as `too-big` and deposited to **Zenodo** for the DOI archive (not committed).
3. **Scratch** (fpocket `pocket*_atm.pdb/.pqr`, PyMOL/VMD `.pml/.tcl/*_PYMOL.sh`, dock work dirs) → never
   archived (and jobs should stop uploading it to S3 in the first place — see the anti-pattern note below).

## How to archive
- **Normal:** dispatch `archive-results-aws.yml` with `mode=diagnose` first (prints the bucket lifecycle
  = root cause, + per-prefix counts), then `mode=archive` (downloads durable files + commits `results/`).
- **Fallback when dispatch/MCP is down:** bump `research/modalities/.archive-trigger` and push — the same
  workflow runs on that path and sweeps the default load-bearing prefix set.
- Classification logic: `research/modalities/archive_results.py` (pure, unit-tested).

## Anti-pattern to fix
`nr4a3_8xtt_benchmark.py` uploaded **thousands** of fpocket scratch files (`fpocket_runs/.../pockets/*`)
to S3 — jobs must upload only their result JSON + essential artifacts, not fpocket scratch. Track under
the reproducibility ledger (`PROVENANCE.md`).

See `PROVENANCE.md` for where each result currently lives (git / S3 / LOST) and how to regenerate it.
