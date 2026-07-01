# Selectivity FEP — spot-priced, parallel strategy (the "make FEP faster & cheaper" wiring)

> **Status (2026-07-01):** infra wired; **production FEP is GATED on trimcrae go-ahead** (this doc + the harness
> are the go-ahead deliverable). The compute protocol still needs a validation shakeout run before its numbers
> are trusted (like every prior pipeline here). Nothing auto-launches.

## Why FEP was the bottleneck
Selectivity FEP (relative binding free energy of the lead across NR4A3 vs NR4A1/NR4A2) is the affinity-grade,
machinery-independent tier that firms up the binder selectivity the red-team left as a "de-noised foothold, not
a fully-controlled result" (F16). The blockers were **cost** (a serial ABFE is hundreds of $ and ~1–3 weeks on
one GPU) and the **1× on-demand `ml.g5.xlarge` quota** (everything serializes behind one GPU).

## The two changes that fix both

### 1. Spot pricing → **use SageMaker *Training* jobs, not Processing jobs**
- **All current pipelines use `FrameworkProcessor` (SageMaker *Processing*).** Processing jobs **do not support
  managed spot** — there is no `use_spot_instances` on a Processor. That is *why* everything has been on-demand.
- **SageMaker *Training* jobs support managed spot** via `use_spot_instances=True` + `max_wait` (wall-clock incl.
  spot wait) + `checkpoint_s3_uri` (continuous checkpoint sync for interruption resume). Spot g5 is typically
  **~60–70 % cheaper** than on-demand.
- So the FEP compute is packaged as a **Training** job (`sagemaker.estimator.Estimator` / PyTorch estimator),
  which is the standard way to get cheap, interruption-resilient GPU on this stack.

### 2. Parallelism → **spot has a *separate quota*; fan out across windows**
- The **1-concurrent-`ml.g5.xlarge`** limit is the *on-demand* quota. **Spot instances draw on a separate
  quota** ("`ml.g5.xlarge` for spot training job usage"), so spot jobs can run concurrently with each other and
  with the on-demand Processing jobs (MM-GBSA, metad, ternary).
- FEP is embarrassingly parallel: **units = (receptor × leg × λ-window)**. E.g. 3 receptors × 2 legs
  (complex, solvent) × 12 λ-windows = **72 independent units**. We shard them across **K concurrent spot
  Training jobs**; wall-clock ≈ (total unit-hours / K) instead of the serial sum.
- **K is bounded by the spot g5 quota.** Default spot quota may be low or 0 — **request a Service Quotas
  increase** for *"ml.g5.xlarge for spot training job usage"* to the desired K (start K=8; 16 is plenty). This
  is the one manual AWS step; the harness reads K from a workflow input and shards to whatever quota allows.

## Interruption resilience (spot can be reclaimed mid-run — mandatory, per the checkpoint standing rule)
Each unit **checkpoints per λ-window to `/opt/ml/checkpoints`** (auto-synced to `checkpoint_s3_uri`), and on
(re)start **skips any window whose result file already exists in the checkpoint dir**. A reclaimed spot
instance resumes from the last completed window, never from zero. `max_retry_attempts` on the training job
re-queues after a spot interruption. This is the SageMaker-native version of the repo's
checkpoint+continuous-upload rule.

## The harness (what got wired)
- **`fep_sharding.py`** (pure, unit-tested): enumerate units, balance them across K shards, compute the
  resume set (pending vs done), and the ΔG_bind / ΔΔG_selectivity bookkeeping (leg ΔGs → per-receptor binding
  ΔG → paralogue ΔΔG). No IO / no OpenMM, so it is fully testable.
- **`nr4a3_fep.py`** + **`sagemaker_src/entry_fep.py`** (compute): openmmtools alchemical λ-windows for the
  assigned shard, per-window reduced-potential output, checkpoint/resume. **Heavy-dep, GPU; protocol needs a
  shakeout run before its numbers are trusted** (soft-core / Boresch-restraint / window-count / sampling-time
  choices are first-pass defaults).
- **`nr4a3_fep_sagemaker.py`** (fan-out submitter): launches K concurrent **spot Training** jobs, one per
  shard, with `use_spot_instances`, `max_wait`, `checkpoint_s3_uri=s3://<bucket>/nr4a3-fep/<tag>/ckpt/<shard>`,
  and outputs to `s3://<bucket>/nr4a3-fep/<tag>/out/<shard>`.
- **`report_fep.py`** (fan-in reducer, read-only/CPU): collect every shard's per-window reduced potentials,
  run MBAR per leg (pymbar), assemble ΔG_bind per receptor and the **NR4A3-vs-paralogue ΔΔG** with bootstrap
  error bars.
- **`.github/workflows/gpu-fep-aws.yml`**: dispatch. **Default `mode=plan` → dry-run (no GPU): prints the shard
  plan + the exact jobs it *would* launch + the cost estimate.** `mode=smoke` runs ONE tiny spot job to validate
  the spot+checkpoint+resume path (and surfaces a spot-quota-0 error if the increase is still pending).
  `mode=run` launches the full fleet — **only to be used on explicit go-ahead.**

## Early stopping — don't burn the fleet if the initial returns say it'll fail
Two failure modes are caught from the **pilot** returns (a short first pass) before the long production runs:
- **Selectivity fail** — the provisional ΔΔG = ΔG_bind(NR4A3) − ΔG_bind(paralogue) is *confidently* not
  selective enough (even its most-optimistic bound, ΔΔG − z·SE, is above the success target for some
  paralogue). The lead won't be NR4A3-selective → stop.
- **Convergence fail** — adjacent-λ overlap is too poor across too many windows → the estimate won't converge
  on this schedule → stop and flag "re-design with more windows," rather than pour sampling into a broken run.
- (Optional) **early success** — confidently selective vs both paralogues → stop the clear winner early.

How it's wired:
1. **Pilot-first compute (`nr4a3_fep.py`, two-pass):** every window runs a short `FEP_PILOT_PS` pilot *first*
   (pass 1), writing a provisional result, then the full `FEP_PROD_PS` production (pass 2). So a fast, complete
   ΔΔG *signal across all windows* exists long before production finishes.
2. **Central monitor (`fep_monitor.py`, one poll = one decision):** reads the partial/pilot results
   (`report_fep.estimate`), and once every receptor has ≥ `FEP_MIN_WINDOWS` windows applies the pure
   `fep_decision.early_stop` + `convergence_flag` rules. On a stop verdict it writes an S3 `STOP.json` record
   and calls **`StopTrainingJob` on every in-flight `<TAG>` spot job** — completed windows are already durable
   in the checkpoint prefix, so only in-flight windows are lost. Poll it (workflow `mode=monitor`) while a run
   is live, or from a babysit loop.
3. **Decision logic is pure + unit-tested** (`fep_decision.py`, `tests/test_fep_decision.py`): stop_fail /
   stop_success / stop_unconverged / continue, with the provisional numbers + reason attached for the log.

Tunables (workflow inputs): `target_ddg` (selectivity bar, default −1.0 kcal/mol), `z` (confidence on the ΔΔG
SE, default 1.0), `min_windows` (data before deciding, default 6).

## Cost math (order-of-magnitude, ml.g5.xlarge us-east-2)
- On-demand g5.xlarge ≈ $1.4/h; **spot ≈ $0.45–0.55/h** (~65 % off).
- A first-pass ABFE per (receptor, leg) ≈ 12 windows × ~1.0 ns × ~ (A10G ~ 20–40 ns/day for a ~40k-atom
  system) ≈ ~0.5–1.5 GPU-h/window → ~6–18 GPU-h per leg; × 2 legs × 3 receptors ≈ **~40–110 GPU-h total.**
- Serial on-demand: ~40–110 h wall-clock, ~$55–150. **Spot + K=8 parallel: ~5–14 h wall-clock, ~$18–60.**
  (Selectivity only needs ΔΔG, so the solvent leg is shared where the same ligand is used — a further saving.)
- These are planning numbers; the shakeout run calibrates window count + sampling time to the real convergence.

## AWS prerequisites — the two manual steps (discovered by the smoke test, 2026-07-01)
`mode=plan` passed (shard plan + cost, no spend). `mode=smoke` got all the way to the SageMaker API and failed
with **`AccessDeniedException: sagemaker:CreateTrainingJob`** — so the wiring is correct; two account-side
changes are needed before any spot FEP can run:

1. **IAM (blocking, do first).** The CI user `nr4a3-ci-submitter` can create *Processing* jobs (all current
   pipelines) but not *Training* jobs. Add a policy statement allowing the Training + monitor actions
   (`iam:PassRole` on the SageMaker execution role is already granted — Processing uses it):
   ```json
   { "Effect": "Allow",
     "Action": [
       "sagemaker:CreateTrainingJob", "sagemaker:DescribeTrainingJob",
       "sagemaker:StopTrainingJob", "sagemaker:ListTrainingJobs", "sagemaker:AddTags"
     ],
     "Resource": "*" }
   ```
   (`ListTrainingJobs` has no resource-level scoping → `"*"`; the others may be scoped to
   `arn:aws:sagemaker:us-east-2:<acct>:training-job/nr4a3-*` if you prefer least-privilege. `StopTrainingJob`
   + `ListTrainingJobs` are what the early-stop monitor needs.)
2. **Spot quota (sets parallel width).** Service Quotas → Amazon SageMaker → **"ml.g5.xlarge for spot training
   job usage"** (region us-east-2) → *Request increase at account level* → set to the parallel width you want
   (**8** matches the default `n_shards` for 12 windows; 16 for headroom). This is separate from the 1×
   on-demand "…for training job usage" quota. Until raised it may be low/0; the fan-out degrades gracefully
   (launches up to the quota, resume picks up the rest).

After both: re-run `mode=smoke` (validates spot + checkpoint + resume for cents and confirms the quota), then
`mode=run` on go-ahead. `n_shards` should be ≤ the spot quota.

## Pre-FEP candidate-robustness checklist (do on the on-demand path while the spot quota is pending)
FEP is the expensive tier — de-risk the candidate on cheap on-demand Processing jobs first, so we FEP a
*correct, stable, well-defined* molecule and don't waste the spend. (No spot / quota / new IAM needed for any
of these.)
- [ ] **Stereochemistry — denovo_401 is 1 of 16 (RDKit, 2026-07-01).** All 4 stereocenters are assigned
      (3S,10R,13S,18R) but by **DiffSBDD**, whose chirality is arbitrary. **Dock + MM-GBSA the stereoisomer set
      and confirm the generated isomer is competitive (or switch to the best) before FEP.** Otherwise we FEP an
      arbitrary 1-of-16. (denovo_401 is otherwise clean: neutral, no ionizable groups, no tautomer ambiguity.)
- [ ] **Protonation — denovo_111 has a basic pyrrolidine → cationic at pH 7.4 (RDKit, 2026-07-01).** Confirm
      which protonation state prior scores used and which to FEP; a buried cation ≠ neutral. Only 2 stereoisomers.
- [ ] **Pose-stability MD (highest-value).** Short unbiased MD replicas of the lead–NR4A3 (and NR4A1/2)
      complex: does the docked pose hold (ligand RMSD, key contacts) in this cryptic/induced-fit pocket? Pick
      the stable frame as the FEP start. A collapsing pose ⇒ FEP is moot — learn it for ~$5, not ~$50.
- [ ] **Ensemble selectivity over the druggable release sub-ensemble** (primary+alt1+alt3) + matching decoy
      null — confirm the selectivity is not a single-frame artifact (closes the F16 frame-dependence residual)
      before FEP.
- [ ] **FEP-protocol shakeout on-demand:** run one window / the solvent leg as an *on-demand Processing* job
      and check a checkable number (e.g. ligand hydration ΔG vs a known value) — validate the openmmtools
      alchemy machinery before the spot fleet spends on it.
Each also strengthens the preprint regardless of the eventual FEP result.

## Guardrails
- **Do NOT launch `mode=run` (production FEP) without trimcrae's explicit go-ahead** (standing FEP carve-out).
- `mode=plan` and `mode=smoke` are safe/cheap and are how we validate the wiring.
- Report FEP at its true weight when it lands: even converged FEP on a cryptic/AF2/induced-fit pocket is
  sampling-limited; it is the strongest in-silico affinity tier, not a wet-lab result.
