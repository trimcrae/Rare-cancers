# NR4A3-only drug-repurposing dock — interruption-robust spot pipeline (runbook)

**What:** Option-1 triage of the 5,988-compound Broad Repurposing Hub library against the **cryptic NR4A3
Pocket-5 only** — the funnel-correct first tier. Docking-level *selectivity* is within docking noise, so this
ranks the library by NR4A3-pocket fit alone (⅓ the compute of the 3-receptor matrix); the top hits then
promote to the real selectivity tier (3-receptor + MM-GBSA + decoy-null). dG here is a **screening prior,
not an affinity**.

**Why the rebuild (2026-07-08):** the earlier 3-receptor waves (shards 00/01) ran the whole shard through a
single smina call per receptor as an on-demand Processing job — a timeout lost the whole shard. This pipeline
is (1) **spot** CPU (≈60-70% cheaper; separate quota from the on-demand Processing docks → more concurrency),
(2) **per-drug checkpointed** (a JSONL line per drug in the SageMaker checkpoint dir, uploaded continuously +
re-downloaded on restart → a kill loses ≤1 drug and the job **resumes**), and (3) **NR4A3-only**.

## Files
- `nr4a3_repurpose_dock.py` — driver: builds the release-frame receptor + box once, docks one drug at a time,
  appends to `<tag>.results.jsonl`, aggregates to `nr4a3-repurpose-<tag>.json`.
- `repurpose_dock_core.py` (+ `tests/test_repurpose_dock_core.py`, 8 tests) — pure resume/rank/summarize.
- `sagemaker_src/entry_repurpose_dock.py` — spot Training entry (git-clones the shard, builds the `mx` env).
- `nr4a3_repurpose_dock_sagemaker.py` — submitter (spot PyTorch Estimator, checkpoint_s3_uri resume).
- `.github/workflows/gpu-repurpose-dock-aws.yml` — dispatch.

## Run
Validate ONE shard first (fan-out rule), then scale:
```
gpu-repurpose-dock-aws.yml  shard=nr4a3-repurpose-shard-02.json  git_ref=main
```
Then dispatch the rest (spot Training quota permitting — shards run concurrently):
```
shard=nr4a3-repurpose-shard-03.json … shard-10.json   (00/01 optional re-dock for a uniform NR4A3-only rank)
```
**Resume/extend:** re-dispatch the SAME `shard` + `output_prefix` — SageMaker re-downloads the checkpoint and
the driver skips every drug already in the JSONL. A timeout/spot-kill is a non-event: just re-dispatch.

## Read
Results live at `s3://<bucket>/nr4a3-repurpose-nr4a3only/<tag>-ckpt/`:
- `<tag>.results.jsonl` — one line per drug (label, drug, moa, phase, smiles, dG_NR4A3, handle_contacts).
- `nr4a3-repurpose-<tag>.json` — ranked summary (best NR4A3 dG first), self-describing `n_docked`/`n_failed`.

## Next
Pool the per-shard rankings, take the top ~250 by NR4A3 dG + handle contacts, and promote them into the
existing 3-receptor + MM-GBSA + decoy-null selectivity tier (`nr4a3_matrix.py` candidate mode → `mmgbsa-aws.yml`).

## TWO valued outputs, not one (trimcrae, 2026-07-08)
Selectivity is NOT a dealbreaker for this screen. The 3-receptor promote tier yields two first-class shortlists:
1. **NR4A3-selective** (low NR4A3 dG, positive margin vs NR4A1/NR4A2, survives decoy-null) → the *systemic EMC
   degrader* angle.
2. **Pan-NR4A** (engages all three LBDs well; `selectivity_fingerprint` `pan_nr4a` cell) → the **CAR-T section**:
   an approved, human-safety-backed drug that suppresses the whole NR4A family is an asset for the ex-vivo
   NR4A-family-knockdown-relieves-exhaustion angle. Pan hits have a LOWER bar (no selectivity margin needed —
   just genuine engagement of all three). Surface BOTH lists; do not discard pan-NR4A as "non-selective." (A
   binder ≠ a degrader — the degrader/ternary framing is downstream — but a pan-NR4A binder with human safety
   data is the starting point the CAR-T section wants.)
