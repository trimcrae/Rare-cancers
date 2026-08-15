---
name: gpu-compute
description: Rules and hard-won provider facts for spending real GPU money — renting a host, launching a fleet or fan-out, picking a provider, pricing a rung, or diagnosing a job that stalled, died or kept billing. Load BEFORE any rental, relaunch, fleet launch or market gate, before writing a job that checkpoints, and before diagnosing a Vast or GCP provisioning, quota, capacity or teardown problem. Covers: never build an environment on a machine we are paying for (the baked Docker images and the parity reading); checkpoint-and-upload-continuously; default every GPU run to spot; serialize only when one result could cancel the rest; Vast capacity refusals, the retired durable machine blacklist, the $/ns market gate and board-depth holds; a relaunch is a new purchase and faces the same ceiling; the host cannot stop its own billing; GCP us-central1-only, GPUS_ALL_REGIONS=1 and the VMs-do-not-self-delete correction.
---

# Running compute that costs money

Extracted from CLAUDE.md §6 on 2026-08-15. Every rule below is **verbatim** — attributions,
dates, superseded-value bookkeeping and incident evidence are preserved, because in this
repository the incident *is* the reason the rule survives re-litigation (CLAUDE.md rule 1.2).

⚠ **This file is a `pinned-figures.json` target.** The figures in it are checked by
`lint_consistency.py` exactly as they were when they lived in CLAUDE.md.

## Environments — CI *and* every rented host


- **★★ NEVER BUILD AN ENVIRONMENT ON A MACHINE WE ARE PAYING FOR — ANYWHERE. THE STACKS ARE PRE-BAKED.
  PULL, DON'T SOLVE (trimcrae, 2026-07-25; scope corrected 2026-08-01 after the framing below hid it).**
  ⚠ **THIS RULE USED TO READ "…IN CI" AND SAT UNDER A HEADING THAT SAID "CI environments", AND THAT IS
  EXACTLY HOW IT WAS MISSED.** On 2026-08-01 the selectivity-control co-fold lane was found renting an
  RTX 4090 and then, on that billing host, running `apt-get install`, `pip install boltz==2.2.1
  cuequivariance-torch cuequivariance-ops-torch-cu12`, and a **~3 GB** `download_boltz2` fetch — a full
  environment build off the stock upstream `pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime`, before one
  second of science. The agent had cited §6 correctly all day and still did not fire on this, because the
  rule was filed as a *CI* rule and this was a *GPU* host. **A rule filed where it cannot fire is absent.**
  The reasoning was always scope-independent and is STRONGER on a rented GPU than in CI: a CI runner is
  free and a 4090 is not, so the measured "~15–25 min solve vs ~2–4 min pull" is 15–25 min of *billed* time.
  It also removes the most dangerous phase from the rental — three of four dead hosts on that lane died
  inside the fetch window, and a truncated CCD reached inference and failed six seeds at 7.2 s each on a
  missing **cysteine**. ★ An image pull is retried by the runtime, digest-verified and layer-cached; a
  bespoke in-container download has no integrity guarantee, and a failed *pull* means the job never starts
  rather than half-starting and dying with `rc=1` and no attribution. **So: a new lane's first question is
  "which baked image?", never "what do I install?"** — and if no image fits, bake one (below) rather than
  solving on the host. Superseded, retained: the "IN CI" phrasing and its CI-only heading.
  ⚠ Corollary, same incident: when a host-side environment problem appears, the fix is the image, **not** a
  cache workaround. An S3 cache for the missing data was proposed and was the wrong answer — Docker Hub
  credentials and eight `Dockerfile.*` siblings already existed.
  Docker Hub account `triskit23`, `secrets.DOCKERHUB_TOKEN` already wired. One image per stack, each with a
  `Dockerfile.*` in `research/compute/`:

  | image | Dockerfile | stack |
  |---|---|---|
  | `triskit23/ternary-fep` | `Dockerfile.ternaryfep` | openfe≥1.12 · openmmtools · pymbar · netcdf4 · numpy/scipy · ambertools≥23 · openff-toolkit/nagl · rdkit · lomap2 · kartograf · gemmi · pdbfixer · biopython · boto3/awscli/gcs — re-bake via `ternary-fep-bake.yml` |
  | `triskit23/pmxfep` | `Dockerfile.pmxfep` | pmx + GROMACS protein-mutation FEP |
  | `triskit23/nr4a3fep` | `Dockerfile.nr4a3fep` | the binary NR4A3 RBFE lane |
  | `triskit23/nrv04vast` | `Dockerfile.nrv04vast` | the NR-V04 covalent/co-fold panel |
  | `triskit23/bioemu` | `Dockerfile.bioemu` | BioEmu |

  A `setup-micromamba` solve of this stack costs **~15–25 min every run** against a **~2–4 min pull**. The image
  supplies the ENV; the checked-out repo supplies the CODE — **mount `research/modalities` or you silently run
  the stale copy baked at build time**:
  ```yaml
  - run: echo "${{ secrets.DOCKERHUB_TOKEN }}" | docker login -u triskit23 --password-stdin
  - run: |
      docker run --rm --entrypoint python \
        -v "$PWD/research/modalities:/work/research/modalities" \
        -v /tmp/conv:/tmp/conv -e CKPT_DIR=/tmp/conv -e INPUT_DIR=/tmp/conv \
        docker.io/triskit23/ternary-fep:latest /work/research/modalities/<script>.py
  ```
  `--entrypoint python` bypasses the image's `autoteardown.py` ENTRYPOINT (for billed GPU legs, not $0 analysis).
  **Log in even for public images** — anonymous pulls share the runner IP and get rate-limited.
  **★ PARITY IS THE SCIENTIFIC ARGUMENT, NOT JUST SPEED**, because **analysing an OpenFE trajectory with a
  different pymbar/openmmtools than PRODUCED it can change the MBAR numbers.** An ad-hoc `micromamba create`
  in an analysis step is a silent protocol deviation.
  ⚠ **BUT THE PARITY IS A SUPERSET, NOT AN IDENTITY, AND THE DIFFERENCE LANDS ON THE PARITY-CRITICAL PACKAGE
  (measured 2026-08-05).** *Superseded, retained: "`Dockerfile.ternaryfep` is byte-for-byte the spec
  `gpu-ternary-fep-gcp.yml` builds" — and `Dockerfile.ternaryfep`'s own header said the same.* Token-diffing
  the two `mamba create` lines: the scientific core is identical package-for-package and in the same order;
  the image adds exactly four — **`netcdf-fortran`, `openmmtools`, `boto3`, `awscli`** — for the portable
  driver. ⛔ **`openmmtools` and `pymbar` are named explicitly in the image and installed by NAME nowhere in
  the GCP workflow**, which nonetheless imports both (`gpu-ternary-fep-gcp.yml:653`), so there they arrive
  TRANSITIVELY through `openfe>=1.12`. Explicit-unpinned and transitive can float to different versions.
  ✅ **MEASURED 2026-08-05 AND THE PARITY HOLDS** — `ternary-fep-bake.yml mode=parity` reads the baked
  image, solves the GCP lane's spec (extracted from that workflow, never copied) and diffs them:
  **openfe 1.12.0 · openmmtools 0.26.0 · pymbar 4.2.0 · openmm 8.4, identical on both sides**, zero
  disagreements. One home: [`ternary-env-parity.json`](./research/modalities/ternary-env-parity.json). So a
  leg produced on one and analysed on the other cannot move an MBAR number through a version difference —
  which is now a **reading**, not the assertion it replaced.
  ⭐ **AND THE TWO SOLVES WERE 13 DAYS APART, WHICH IS THE POINT.** The image was baked 2026-07-23; the GCP
  spec was solved fresh 2026-08-05. Neither side pins `openmmtools`/`pymbar`, so agreement across that gap
  is evidence about the drift RATE, which agreement across two minutes would not have been. (Verified in the
  same pass: the baked image carries HEAD's spec — the 26-package `create` at commit `07f2dd345` is
  package-identical to the current one, so this is not an old image being compared to a new spec.)
  ⚠ **Still a reading of a date, and only one side is immutable.** The image is baked; the GCP lane solves
  on the fly, so that side can drift while the image cannot. Re-run `mode=parity` after any openfe bump or
  before quoting cross-provider comparability in the paper — the job records both dates so a future reader
  can see the gap rather than having to dig it out of the Actions history, which is how it was got here. Dep genuinely missing → add it to the `Dockerfile.*` and **re-bake once**. Only if you truly
  cannot re-bake, use `setup-micromamba` **with `cache-environment: true`**. *(Cost of learning this: ~20 min of
  solve per run, three runs in a row, while the image already carried every package.)*


## Long runs, checkpointing and spend shape


- **CHECKPOINT + UPLOAD CONTINUOUSLY — never guess-and-lose (trimcrae standing rule).** Any job whose runtime you
  are estimating MUST (1) checkpoint after *each* unit of work (ligand/frame/candidate/leg), (2) upload those
  checkpoints **as they are written** (`s3_upload_mode="Continuous"`; a default end-of-job upload loses **all**
  partial work on a timeout or crash), (3) scale the overall timeout to the work with a **per-unit** timeout as
  the real hang-guard, and (4) treat the partial checkpoint as the deliverable on a timeout. Full rule + the
  MM-GBSA incident: [next-steps.md](./research/modalities/nr4a3-degrader-next-steps.md) → "Infra gotchas".
- **DEFAULT EVERY GPU RUN TO SPOT.** It is safe **because** of the checkpoint rule — the two go together. On
  SageMaker: `use_spot_instances=True`, `max_wait >= max_run`, `checkpoint_s3_uri` +
  `checkpoint_local_path=/opt/ml/checkpoints` gives native resume (prior checkpoints download on start, so a
  re-dispatch with the same prefix resumes and extends). Use `submit_spot`, never `FrameworkProcessor`; entries
  read `sm_io.channel("name")` and write `sm_io.out_dir()`; monitor with `job_type=training`. **The ~60–70 %
  saving arrives as FEWER BILLED HOURS, not a lower rate** — a `SpotTraining` line can show a rate ≥ on-demand
  and still be far cheaper, so never diagnose "no discount" from the rate (`list-sagemaker-aws.yml mode=savings`).
  Stay on-demand only when the job truly cannot checkpoint or the instance type has no spot quota.
- **★★ SERIALIZE ONLY WHEN ONE RESULT COULD CANCEL THE REST — otherwise fan out immediately.** Three related
  rules, one decision:
  1. **Plumbing shakeout (always):** `mode=smoke` → **one real leg/shard** → fleet. The smoke skips the heavy MD
     env so it cannot catch env bugs; the single real shard can (a `PYTHONPATH` leak imported the base
     container's numpy 1.x into a numpy-2 env, invisible to smoke). Nothing is wasted — per-unit checkpoints mean
     the fan-out resumes from the shakeout.
  2. **Scientific early-abort (when abortable):** before a multi-leg spend that you would **abandon** if one
     representative leg came back unfavorable, run **one decision-relevant leg first** — the one with the highest
     abort information (the known-answer positive control, or the paralogue the conclusion hinges on). A pilot is
     about the RESULT; if its host won't start, move hosts and read the result there.
  3. **The litmus test:** *"Is there a result this shard could return that would make me NOT run the rest?"*
     **No** → serializing is pure wasted wall-clock for zero decision value; **fan out everything at once.**
     Parallel costs the same GPU-$ as serial. *(Not this rule: units that physically cannot split — HREX λ-windows
     exchanging configs inside one transformation — are serial by physics.)*


## Provider facts


- **★ NAME THE PROVIDER AND CONFIRM IT BEFORE ANY SUBSTANTIAL GPU RUN (trimcrae, 2026-07-12)** — in the *same*
  advance confirmation as the >$50 spend nod. Never silently default. The repo is provider-agnostic
  (`gpu_backend.py` + `autoteardown.py` + `object_store.py`; accounts and offers in
  [cheap-gpu-plan.md](./research/compute/cheap-gpu-plan.md)), so this is config, not a rewrite. **Production runs
  go on Vast**; the one standing exception is **spending expiring free credit** (the GCP trial closes
  **2026-10-10**), which means **realized spend and ladder spend are different ledgers** — track them separately.
- **★★ THE HOST CANNOT STOP ITS OWN BILLING — ONLY THE CONTROL PLANE CAN (measured 2026-07-27; this rule
  previously said "the auto-teardown wrapper guarantees no idle-GPU billing anywhere", and that was false).**
  An unprivileged container cannot end itself: `poweroff`/`shutdown` need an init it does not have, `kill -9 -1`
  excludes PID 1 and kills the caller, and `kill -9 1` **returns success while being ignored** — which is why
  the failure was silent. Reproduced under `unshare`; pinned by `tests/test_vast_idle_guard.py`. So the EXIT
  trap and `autoteardown.py` stop the JOB, not the METER, and a container that **crash-loops never returns at
  all**, so neither ever fires — two 5a-KS legs billed ~53 min at `gpu_util: 0.0` while `actual_status:
  running`. **The guarantee is [`vast_idle_guard.py`](./research/modalities/vast_idle_guard.py) acting from CI**,
  where the key lives: a box that is up and producing no evidence of work (log silent, or restart churn) is
  destroyed in ~15 min instead of hours. Its one inviolable rule — **GPU idleness NEVER condemns a box** —
  is what stops it reaping a legitimately CPU-bound staging phase; only a measured absence of *writes* does.
- **★ ON VAST, A CAPACITY REFUSAL MEANS PICK ANOTHER HOST — DO NOT WAIT IT OUT (trimcrae, 2026-07-25; replaces
  the old AWS wait-out rule).** On `{"success": false, "error": "resources_unavailable"}` that machine's GPU is
  taken: **destroy the instance and launch elsewhere — do not queue, do not raise the bid.** Both alternatives
  were tried and failed (a 26 % bid raise left it queued; the box sat `stopped` for 45 min across ~13 attempts).
  Vast is ~23 independently-priced hosts visible at once and **the floor is flat**, so a different host today
  costs what this one will tomorrow. AWS managed spot is a *pool* with no host choice, which is why waiting is
  right there and wrong here. Implemented in `protfep_vast_launch.collect` + `ResourceSpec.exclude_machine_ids`
  — a host that never starts has infinite realised $/ns, invisible to $/ns ranking, so without the skip it keeps
  winning selection inside the same placement call and keeps failing. ⚠ **That skip is BOUNDED to the call —
  see the no-durable-blacklist rule immediately below**, which retires the reading of this line under which the
  same exclusion was allowed to persist across lanes and days.
- **★★ NO DURABLE MACHINE BLACKLIST — A HOST WE REFUSED ONCE IS SELECTABLE AGAIN ON THE NEXT CALL (trimcrae,
  2026-07-31: *"You've gotta just stop doing the blacklist. It seems like it only ever bites us in the ass and
  clearing it always makes things better."*).** Nothing that excludes a machine may outlive the placement call
  or the launch wave that learned it. **KEPT, because both are bounded and neither can accumulate:**
  `used_machines` (`congeneric_fanout_vast.mode_launch`) stops one wave double-renting a host we already hold
  and **dies with the wave**; `gpu_backend.submit`'s in-call retry skip drops a machine that just answered
  `resources_unavailable` for the *remaining offers of that same call*, on a **copy** of the spec. **RETIRED:**
  the cross-lane, host-scoped, never-ageing set — not because any single entry was wrong, but because it had
  **no evidence that could ever retire one**, so it only ratcheted the board narrower; re-learning a bad host
  costs one **free** failed submit, while over-excluding costs capacity on every lane, silently.
  One home for the decision: **`vast_machine_blacklist.DURABLE_EXCLUSIONS_ENABLED = False`**, held by
  `tests/test_blacklist_retired.py`, reversible via `VAST_DURABLE_EXCLUSIONS=1` — **which is an escape hatch
  for a diagnosis, not a setting to leave on.**
  ⚠ **So when placement fails, suspect OUR FILTERS BEFORE THE MARKET** — that has been the cause every time it
  was checked. Incidents, evidence and what is still open (a card floor, `min_cuda`, the label-scoped guard):
  [vast-placement-facts.md §1](./research/compute/vast-placement-facts.md).
  *Superseded, retained: the reading of the bullet above under which `exclude_machine_ids` justified a durable
  cross-lane set — [STRATEGY.md Appendix A](./STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 59.*
- **★★ A THIN, EXPENSIVE MARKET IS A REASON TO PAUSE, NOT TO PAY — GATE EVERY FLEET LAUNCH ON $/ns
  (trimcrae, 2026-07-26: *"I'd rather pause until availability opens than pay double per ns"*).** The rule above
  says a *capacity refusal* on one host is never worth waiting out, because the floor is flat and another host
  costs the same. **That premise fails when the whole board thins.** Measured that night: **5 offers visible
  against the ~23 baseline, `min_floor` $0.200/hr and `median_floor` $0.333/hr**, hours after the same lane
  rented at **$0.048–$0.139**. Selection was working correctly and still could only reach ~1.8× the $/ns it had
  been getting.
  So before any **multi-unit fan-out**, take a market snapshot and compare the **best achievable `$/ns`** — not
  `$/hr`, and not the bid — against the rung's own basis. If the fleet cannot be bought at a sane `$/ns`, the
  launcher **HOLDS and says why**, and the next scheduled tick re-checks; it does **not** buy in and it does
  **not** silently drop units. Waiting costs nothing here — the work is checkpointed, the ladder has no
  deadline, and an hour of a flat market is cheaper than a tranche bought at double.
  Two failure modes this must avoid, both worse than the problem: **holding silently** (a fleet that never
  launches looks identical to one that finished — every hold must be visible in the readout with the snapshot
  that caused it), and **a ceiling nobody can clear** (if the market stays bad, that is a decision for trimcrae,
  so surface it rather than idling forever).
- **★★ A HOLD ON PRICE MUST REPORT BOARD WIDTH, OR IT CANNOT BE TOLD FROM A FILTER BUG (2026-07-31 — this cost
  most of a session, and it is the SECOND time the same confusion was diagnosed as an expensive market).**
  A gate that finds one acceptable offer prints a high `$/ns` and holds — and that reads identically whether
  the market is thin or **our own filters left one host**. Opposite remedies: one says wait, the other says
  widen. So every hold quotes `board_depth` beside the ratio — `offers_returned → qualifying → priceable →
  used_for_mean` (`relaunch_market_gate.price_offers` is the one home of the arithmetic).
  **`qualifying` far below `offers_returned` is a FILTER diagnosis wearing a price label**: say so with the
  existing `hold_cause: exclusions_or_spec_not_price` instead of holding on price. ⚠ **A low `used_for_mean`
  is NOT a symptom** — it is `min(needed, priceable)` and equals 1 by design for a single unit.
  **The tell: a ratio that swings ~2× within minutes.** A market floor does not move like that; a spec does.
  Both measured instances, the discriminating fields, and the gate artifact that still does not record which
  spec produced it: [vast-placement-facts.md §2](./research/compute/vast-placement-facts.md).
- **★★ A RELAUNCH IS A NEW PURCHASE, NOT A CONTINUATION — SO IT FACES THE SAME CEILING (trimcrae, 2026-07-27:
  *"Why are there so many high `$/ns` rows that are flagged but you're still paying for them? The whole point
  is to pause the test if it gets that expensive."*).** The gate above is **not** scoped to fan-outs. The test
  is **"would waiting actually lose work?"** — and for a checkpointed unit it would not: by the time a relaunch
  is considered the host is already gone, and the only surviving state is a durable object store. So **every
  rental of a new host is gated, resume and cold single unit included.** A single host is judged on the **§1
  drift line** (a rate) rather than a tranche's dollar band, because a resume re-enters a leg at an unknown
  fraction of its work and any dollar projection would be the whole unit's cost — which also means **a row that
  prints `⚠ DRIFT` is exactly a row the gate would refuse to buy.** One implementation:
  [`relaunch_market_gate.py`](./research/modalities/relaunch_market_gate.py), whose `EXEMPTIONS` is the complete
  list of cases where waiting genuinely does lose work. **Work already executing is never touched** — the gate
  acts at the moment of renting and must never be given reach over a live host. That boundary rests on
  *the rate you rent at is the rate you pay*, which is **measured, not assumed**: `vast_rate_forensics.py`
  reads the live instance record and the lane's rental ledger, and a rented rate has never moved.
- **★ SPOT PREEMPTIONS ARE ROUTINE — MENTION LIGHTLY (trimcrae, 2026-07-16).** A preempted VM is expected
  behaviour and routine self-doable recovery: re-dispatch to resume from checkpoint, re-arm the check-in. A
  one-line note is fine; **no alarm, no `AskUserQuestion`, no write-up**, even if it repeats. Reserve real
  surfacing for a result, a decision-relevant reading, or a genuine non-preemption failure (env build error,
  quota error, a real traceback). *(Distinct from the capacity refusal above: that host never started.)*
- **★ GCP GPU = us-central1 ONLY (trimcrae, 2026-07-16).** Quota exists **only** there. Never pass a non-central
  zone, never add `us-east*`/`us-west*` to a `ZONES` list, never "try another region" to dodge a stockout — those
  regions have no quota, so the create just fails and wastes attempts. Diversify across the four central zones
  (a/b/c/f) only.
- **★★ GCP HARD FACTS — read [gcp-gpu-facts.md](./research/compute/gcp-gpu-facts.md) before diagnosing any GCP
  GPU provisioning/quota problem** (each cost real debugging). The critical few: **(1) `GPUS_ALL_REGIONS = 1` is
  the BINDING cap** — at most 1 GPU concurrent, any region or type; the per-type regional quotas are real but
  non-binding, so replicate seeds and edges run **sequentially**, never in parallel (`gcp-quota-check.yml`).
  **(2) Quota usage is the zombie test** — usage ≥ 1 means a zombie holds a GPU; usage = 0 with no VM listed
  means a provision failure is real capacity or a bad request. **(3) On-demand create MUST pass
  `--instance-termination-action` whenever `--max-run-duration` is set** (true for standard too, not spot-only) —
  omitting it silently broke on-demand for months, mislabelled "stocked out". **(4) Spot working while on-demand
  fails is backwards** → a broken command, not capacity. **(5) ⚠ VMs DO NOT self-delete — the in-VM trap runs
  and GCE REFUSES it** (`Required 'compute.instances.delete' permission`, measured 2026-07-27), so a finished
  leg leaves a RUNNING VM holding the single GPU; the reap is the CONTROL PLANE's job (the ternary watchdog's
  DONE branch), and `gcp-reap-vms.yml` is **not** a backstop — it has no `schedule:` and never fires by itself.
  **Superseded, retained:** "VMs self-delete on exit, so a dead leg shows `live_vms=0`; `gcp-reap-vms.yml` is
  the backstop." Evidence and the whole correction: [gcp-gpu-facts.md](./research/compute/gcp-gpu-facts.md) §6/§6b.

