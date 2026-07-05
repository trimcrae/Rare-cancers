# PocketMiner cryptic-pocket cross-check — run notes

**Purpose.** Independent, orthogonal test of the degrader paper's central claim — that the "undruggable"
NR4A3 LBD harbours a cryptic *druggable* pocket. Our own evidence is metadynamics + fpocket (one method
family). **PocketMiner** (Meller et al., *Nat Commun* 14:1177, 2023) is a **GVP graph neural network** that
predicts cryptic-pocket-forming residues **from a single static structure**, trained on a **separate**
cryptic-pocket MD dataset (shares no code or training data with our route). If, run on the apo AF2 LBD, it
independently flags our fpocket **Pocket-5** site, that is genuine cross-method corroboration.

## Verified run recipe (what I confirmed from the source)

| Item | Value |
|---|---|
| Repo | `https://github.com/Mickdub/gvp` |
| Branch | `pocket_pred` |
| License | **MIT** — verified from `LICENSE` (Meller/Ward/Borowsky/Lotthammer/Kshirsagar/Oviedo/Lavista Ferres/Bowman 2022; bundled GVP code (Jing et al. 2020) and Ingraham et al. 2019 code also MIT). **Use permitted, with attribution.** |
| Weights | **In-repo**, `models/pocketminer.index` + `models/pocketminer.data-00000-of-00001` (a TensorFlow checkpoint). **No separate download step** — they come with the clone. |
| Run entrypoint (upstream) | `cd src && python xtal_predict.py`, after editing `strucs`, `output_name`, `output_folder`, `nn_path` in the `__main__` block. |
| Inference API used | `from validate_performance_on_xtals import process_strucs, predict_on_xtals` and `from models import MQAModel`. Model is built with fixed hyperparameters `node_features=(8,50), edge_features=(1,32), hidden_dim=(16,100), num_layers=4, dropout=0.1`; weights via `nn_path="../models/pocketminer"`. |
| Output format | Per-residue cryptic-pocket **probability in [0,1]**, one value per residue in input order. Upstream writes `{name}-preds.npy` + `{name}-predictions.txt` (`%.4g`, one per line). |
| Env | conda `pocketminer.yml`: channels conda-forge/defaults; deps `python, numpy, scipy, pandas, tensorflow, tqdm, mdtraj, yaml`. **Authors deliberately removed version pins** ("worked better across OSes"); README notes TF **2.1.0** tested, also compatible with **2.6.2 / 2.9.1**. GPU **not** required. |

### How our job runs it (differs slightly from upstream, on purpose)
Instead of editing `xtal_predict.py`, `entry.py` writes a small generated driver (`nr4a3_pm_driver.py`)
into the cloned `src/` (so the relative imports resolve) that calls the **same** `process_strucs` /
`predict_on_xtals` API on our one structure, then dumps `nr4a3_lbd-preds.npy` + a `residue_order.json`
(read independently via mdtraj) so scores map **exactly** back to UniProt residue numbers.

## Input-structure decision (the circularity guard — important)

- Input = **apo AF2 model, AFDB `AF-Q92570-F1-model_v4`, trimmed to the LBD, residues 373-626**, original
  UniProt numbering preserved.
- By **default the job fetches this fresh from the AlphaFold DB** (`api/prediction/Q92570` → `pdbUrl`) and
  trims — so the input is provably the **pre-metadynamics apo** structure.
- **We deliberately do NOT feed a metadynamics-opened frame.** PocketMiner's whole value is predicting a
  pocket that is *cryptic* (closed) in the static structure; feeding an already-opened frame would be
  circular and would destroy the independence of the test.
- A PDB mounted from S3 is used **only** if `PM_ALLOW_INPUT_PDB=1` (off by default) — and it is still
  trimmed to 373-626. Do not enable this unless you have verified the mounted PDB is the apo model.

## Comparison set (what "overlap" means)

fpocket **Pocket-5** lining residues on the AF2 model (Q92570 numbering), from
`nr4a3_fpocket_enumerate.py` / `nr4a3_resistance_map.py`:
`406, 407, 410, 411, 412, 481, 484, 485, 531, 534` (the 7 selectivity handles `406,407,410,412,484,531,534`
are a subset). The job reports, honestly and at several thresholds:
- PocketMiner residues at ≥0.7 (high) and ≥0.5 (moderate), plus the top-15;
- which Pocket-5 residues fall in each flagged set (and the fraction);
- Pocket-5 mean/max score vs the LBD-wide mean, and the **enrichment ratio** (Pocket-5 mean ÷ LBD mean);
- each Pocket-5 residue's **percentile rank** among all LBD residues.

Read the result as a *degree* of corroboration, not pass/fail: strong overlap **or** clear enrichment
(>~1) is real independent support; partial overlap / modest enrichment is a weaker-but-real signal, not a
null. It never replaces the metadynamics evidence — it is a single static-structure cross-check.

## How to dispatch + read results

Dispatch (manual): **Actions → "NR4A3 PocketMiner cryptic-pocket cross-check (AWS SageMaker)"
(`gpu-pocketminer-aws.yml`) → Run workflow.** Inputs: `instance` (default `ml.c5.2xlarge`), `tf_version`
(default `2.9.1`), `region` (default `us-east-2`). Needs the usual `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`, `SAGEMAKER_ROLE_ARN` secrets. CPU job — **no GPU quota contention** with the ABFE
fleet.

Result: `s3://<default-bucket>/nr4a3-pocketminer/pocketminer_nr4a3_result.json`
(per-residue scores, flagged sets, and the `overlap` block). Uploaded **Continuous**, so a partial is
captured even on a timeout.

**Cost:** ml.c5.2xlarge on-demand ≈ $0.41/hr (us-east-2); runtime is dominated by the one-off conda/TF env
build (~10–20 min), inference is seconds → **well under $0.25/run, no GPU spend.**

## Risks / unverified assumptions the dispatcher MUST know (validate-first)

1. **TensorFlow env fragility (the main risk).** The upstream `pocketminer.yml` is **unpinned**; TF↔numpy
   compatibility is the usual breakage. We pin `tensorflow==2.9.1`, `numpy<1.24`, `python=3.9`, mdtraj from
   conda-forge. **Validate with ONE run before trusting the numbers.** If it fails at import/build, override
   `PM_TF_VERSION` (try `2.6.2`, or `2.1.0` with an older python) / `PM_PY_VERSION` via the workflow input /
   env. This is a per-CLAUDE.md "validate a fan-out on one shard first" situation — here there's only one
   shard, so just confirm the single run is green before citing it.
2. **`predict_on_xtals` output shape** (per-structure vs `(1, n_res)`) is squeezed to 1-D in the driver; the
   `n_pred` vs topology-residue count is logged and asserted-by-warning in `analyse()`. If they disagree,
   inspect `residue_order.json` before trusting the residue mapping. (For the complete-standard-residue AF
   LBD, expect exactly **254** residues 373–626.)
3. **Weights path** assumed `models/pocketminer{.index,.data-00000-of-00001}` (verified present on
   `pocket_pred` at time of writing). The job aborts loudly if the checkpoint isn't there — if upstream
   moves it, update `PM_NN`.
4. **`process_strucs` residue handling.** PocketMiner uses mdtraj; if it silently drops any non-standard or
   incomplete residue the score count would shrink. The AF apo LBD is all-standard/complete, so this should
   not trigger — but the length check (risk 2) is the guard.
5. **No commit / dispatch was done here** — files only. Confirm the `sagemaker>=2.200,<3` pin still resolves
   in CI before dispatch (same pin as the other AWS jobs).
