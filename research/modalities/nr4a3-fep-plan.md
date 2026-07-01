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
4. **"Why did it fail" is captured BEFORE any stop** (`fep_decompose.py`, `tests/test_fep_decompose.py`): the
   coupled-endpoint per-residue ligand-interaction decomposition → per-residue selectivity attribution
   (drivers vs eroders, handle-annotated) + a redesign hint. The monitor **gates stop_fail on this diagnostic
   being ready** (`diagnostic_ready`), so we never stop a fail without knowing which residues caused it. The
   attribution + hint are written into `STOP.json` and printed. (The per-residue MD decomposition in
   `nr4a3_fep.py` is first-pass/shakeout-pending like the rest of the real compute; the smoke path emits a
   synthetic map so the gating + attribution are validated end-to-end.)

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
- [x] **Stereochemistry — denovo_401 (RESOLVED 2026-07-01, dock 28538579322 → MM-GBSA 28540078644/28542048560).**
      Docked+scored all 16 diastereomers: **selectivity is stereochemistry-robust** (nearly all confirmed_selective),
      the DiffSBDD-generated isomer is **near-optimal** (de-noised +9.54 ± 4.26), co-best with its C13-epimer
      **iso08** (+11.36 ± 5.25, within SD). **FEP subject = iso08 + as-generated epimer pair** (FEP resolves which).
      So prior denovo_401 results stand on a good isomer.
- [x] **Protonation — denovo_111 WITHDRAWN (RESOLVED 2026-07-01).** Basic pyrrolidine → cationic at pH 7.4; the
      cation **reverses** selectivity (multi-snapshot −15.01 ± 5.14, NR4A1 −36.81 < NR4A3 −21.80). Its neutral-form
      selectivity was an artifact → not an FEP candidate. denovo_401 is the sole robust lead.
- [~] **Pose-stability MD — SKIPPED (trimcrae 2026-07-01, redundant with FEP).** FEP's complex-leg
      equilibration already stress-tests the pose, and the early-stop monitor catches a collapsing pose in the
      pilot windows (bad energies / poor overlap → StopTrainingJob), so a separate pose-stability MD (~$10–20
      incl. new-pipeline shakeout) buys only earlier detection, not new information. Decision: rely on
      FEP + early-stop as the pose safety net.
- [ ] **Ensemble selectivity over the druggable release sub-ensemble** (primary+alt1+alt3) + matching decoy
      null — confirm the selectivity is not a single-frame artifact (closes the F16 frame-dependence residual)
      before FEP.
- [ ] **FEP-protocol shakeout on-demand:** run one window / the solvent leg as an *on-demand Processing* job
      and check a checkable number (e.g. ligand hydration ΔG vs a known value) — validate the openmmtools
      alchemy machinery before the spot fleet spends on it.
Each also strengthens the preprint regardless of the eventual FEP result.

## FEP outcome → next step (the failure mode is diagnostic)
"FEP fails" is not one thing; the *mode* points to different next moves. The run is diagnostic: per-receptor
ΔG + λ-overlap **and** a **per-residue selectivity attribution** (`fep_decompose.py` + a coupled-endpoint
per-residue decomposition in `nr4a3_fep.py`). **The early-stop is COUPLED to this diagnostic (trimcrae
2026-07-01): the monitor will NOT reclaim the fleet on a selectivity fail until the per-residue WHY-map is
captured for all three receptors** (`fep_decompose.diagnostic_ready`); until then a fail signal *holds the run
sampling* rather than stopping blind. So a fail always tells us *why* (which residues erode selectivity) before
we stop — directly feeding the next-candidate design.
- **Mode 1 — doesn't converge** (poor λ-overlap / hysteresis / huge error bars; convergence early-stop trips).
  = **receptor/protocol failure, not a candidate failure** — says nothing about denovo_401. Next: better
  protocol (more windows, longer, HREX, restraints) → ensemble FEP over the druggable release sub-ensemble → if
  still stuck, this is the **AF2-cryptic-pocket ceiling**: honest SOTA finding that in-silico affinity-grade
  selectivity needs an **experimental structure**. Points to **wet-lab/structural outreach**, NOT a new molecule.
- **Mode 2 — converges but NOT selective.** Sub-shape matters (per-residue decomposition tells which):
  - *reversed / paralogues comparable* → MM-GBSA selectivity was a scoring/frame artifact (F16 realized); the
    **binder route is pocket-limited** → pivot selectivity to the **ternary-linker** toward the divergent
    C-terminal patch (E545/T563/Q570/S571/L576/E580/V588) and/or the **ASO**.
  - *right direction, small ΔΔG (near-miss)* → **FEP-informed scaffold optimization around denovo_401**
    (engage the handles the decomposition flags), NOT brute-force generation (funnel hit-rate ~2/11).
  - *weak absolute NR4A3 affinity* → affinity-focused generation / grow into the pocket.
- **Mode 3 — converges and confirms selectivity** = the win; proceed to ternary/linker + outreach.
- **More denovo vs different pocket?** More denovo only for the near-miss (as targeted scaffold-opt). A
  *different pocket* is a downgrade for a *binder* (the orthosteric cryptic pocket is the MOST paralogue-
  divergent zone) — the real "different site" pivot is the **ternary PPI interface** or the **ASO modality**.
- **Meta:** several failure modes converge on "need an experimental structure," which is the project's
  wet-lab-handoff endgame anyway — so a FEP failure strengthens the outreach case, it doesn't dead-end it.

## Guardrails
- **Do NOT launch `mode=run` (production FEP) without trimcrae's explicit go-ahead** (standing FEP carve-out).
- `mode=plan` and `mode=smoke` are safe/cheap and are how we validate the wiring.
- Report FEP at its true weight when it lands: even converged FEP on a cryptic/AF2/induced-fit pocket is
  sampling-limited; it is the strongest in-silico affinity tier, not a wet-lab result.
