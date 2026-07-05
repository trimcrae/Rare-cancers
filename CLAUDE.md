# CLAUDE.md

This project's full maintenance guide lives in **[AGENTS.md](./AGENTS.md)** —
read it before making changes.

## TL;DR for agents

- **⏰ TIMES: ALWAYS US EASTERN (ET), NEVER UTC (trimcrae standing rule).** Every time you report to trimcrae —
  ETAs, job timestamps, "as of HH:MM", watch cadences, anything — MUST be Eastern (EDT = UTC−4). Convert before
  writing; do not surface UTC even if the tool/log emits it. (You keep slipping into UTC — this is why it's rule #1.)
- **PRIMARY FOCUS (2026-06):** the repo's #1 priority is **publishing work that drives
  forward an EMC treatment**. **As of 2026-06-26 (trimcrae decision), the TWO papers to publish first are:**
  **(1)** the split-out, target-centric **NR4A3-degrader result paper** —
  **[research/manuscripts/nr4a3-degrader-paper.md](./research/manuscripts/nr4a3-degrader-paper.md)**
  (EMC is its lead clinical application among several NR4A3/NR4A indications); and **(2)** the
  **fusion-junction ASO paper** — **[research/manuscripts/fusion-junction-aso-paper.md](./research/manuscripts/fusion-junction-aso-paper.md)** —
  the most-likely-to-work *fusion-exclusive* route (RNA-level silencing of the chimera that **spares
  wild-type NR4A3**, which the LBD-binding degrader cannot), now with a complete in-silico evidence arc
  (design → transcriptome-wide off-target → breakpoint-favorability scan → gap-mismatch-resolved
  predicted-clean gapmers; **delivery is its one remaining gate**). **Next tier, not the first two:** the
  **[research/manuscripts/emc-treatment-roadmap.md](./research/manuscripts/emc-treatment-roadmap.md)**
  (EMC-program paper) and the **fusion-exclusivity framework**
  ([research/manuscripts/fusion-selective-approaches-overview.md](./research/manuscripts/fusion-selective-approaches-overview.md),
  the 5-route design space for sparing wild-type NR4A3; AND-gate degrader / condensate / PPI / neoantigen).
  This serves, not replaces, the EMC goal (see
  **[research/manuscripts/nr4a3-degrader-paper-positioning.md](./research/manuscripts/nr4a3-degrader-paper-positioning.md)**).
  **Resuming the degrader in-silico work (program state + exactly how to run the next GPU step, e.g. the
  warhead screen): [research/modalities/nr4a3-degrader-next-steps.md](./research/modalities/nr4a3-degrader-next-steps.md)** —
  as of 2026-06-26 the cryptic-pocket druggability case is a **feasibility result stated honestly** (a
  2026-06-26 red-team corrected an earlier "all gates pass" overstatement: Gate 0/0b/2 pass; Gate 1 holds
  only in the weaker *basin-breathing* sense — F(Rg) is monotonic with no separate opened basin; Gate 3 is
  *provisional* pending the unbiased release run; the 0.931 opened-pocket score is a biased-MD **peak over
  frames**, best reported as a fraction-of-frames-druggable distribution — fpocket itself is standard, so
  no bespoke negative control is needed). See [research/manuscripts/nr4a3-degrader-paper-redteam.md](./research/manuscripts/nr4a3-degrader-paper-redteam.md).
  The next step is the built-but-idle selective-warhead screen (plus the queued release run).
  The crux of the portfolio is still **[research/manuscripts/emc-treatment-strategy.md](./research/manuscripts/emc-treatment-strategy.md)**
  and the board in **[research/IDEAS.md](./research/IDEAS.md)**. **No wet lab is available**, so every
  "next step" must be either (1) publish-to-convince or (2) in-silico evaluation — never a wet-lab to-do.
- **★ NORTH STAR (2026-07-01, trimcrae):** produce **the state of the art of what in-silico testing can do for
  an NR4A3-selective degrader** — the most complete, rigorous, honest computational characterization achievable
  with no wet lab (cryptic-pocket druggability → selective warhead → paralogue-selectivity controls → ternary /
  degradation geometry → FEP), every result at its true weight. The preprint documents *that*, not a
  ship-when-adequate minimum.
- **★★ WHAT "STATE OF THE ART" MEANS = BREADTH-FIRST, STANDARD-DEPTH (trimcrae, 2026-07-05 — clarifies the North
  Star; codified to stop it drifting into "spend $1000s for a marginal CI").** "State of the art" = cover every
  distinct *current technique* that adds a **NEW axis of evidence** (a new structure predictor, pose/complex
  method, ternary-geometry tool, ML potential, selectivity model — the "if an AlphaFold-class tool exists, use
  it" rule) — NOT exhaustively optimizing any ONE test past its field standard. **Decision rule (apply before
  every GPU spend):**
  - **Add a technique** (new axis / new failure-mode it can catch) → **default YES** — this is what buys "state
    of the art"; watch/trigger list = [research/method-watch.md](./research/method-watch.md).
  - **Deepen one already-run test past its field standard** (more FEP sampling, extra force fields, more
    replicates, tighter CIs, HREX-when-independent-windows-suffice) → **default NO**; allowed only when the
    standard-rigor result is **genuinely ambiguous AND that ambiguity is decision-relevant.** "It would be more
    rigorous / closer to gold" is **not** a reason.
  - **Run each test to its field standard, then STOP.** (ABFE standard = converged by forward/reverse + ~3
    independent replicates + honest **replicate-SD, not MBAR-SE** error bars. Past that is marginal.)
  - **Cost guardrail:** one test's validation must not balloon into $1000s for CI-tightening; a run that is
    "more of a test we've already done to standard" needs an explicit written *"why isn't standard enough here."*
    A breadth dollar (new technique, new axis) beats a depth dollar (one test, past standard) every time.
  - **Anti-pattern that triggered this:** rigor added *reactively* one layer at a time (HREX→replicates→
    conformers→2nd-FF). Scope the standard per test **up front**; don't escalate under prodding.
- **OPERATING REGIME (2026-07-01, trimcrae; UPDATED) — solo-researcher scale; make the paper as strong as
  in-silico allows BEFORE preprinting, then hand off to wet labs.**
  See **emc-treatment-strategy.md → "Operating regime (2026-07-01)"**. In short: one independent researcher,
  **no wet lab** (a self-funded wet-lab program $5–25k is **OFF the table** — a funded collaborator/foundation's
  budget, never propose it as a next step). **GPU spend is NOT a gate on paper quality** — the earlier
  low-hundreds-$ ceiling / "cheap completeness only" / "SKIP FEP" / "don't let testing delay shipping" directive
  is **removed** (it was deferring rigor-critical work to ship fast). New rule: **run the warranted in-silico
  experiments — including the expensive ones (selectivity FEP, generation-matched decoy null, ensemble scoring,
  the ternary) — to strengthen or honestly refute the claims, and post the preprint only once that work is done
  and folded in.** Cost is a reason to sequence + right-size (checkpoint/continuous-upload, serialize the single
  g5), not to skip a decision-relevant run. Deliverable = a rigorous, honest **preprint** (ChemRxiv degrader /
  bioRxiv ASO) + **targeted outreach** to NR4A/nuclear-receptor labs, the SGC, and EMC/sarcoma foundations
  (journal submission in parallel; don't wait on peer review — but do wait on the warranted GPU work).
  **Preprint conversion checklist:**
  [research/manuscripts/nr4a3-degrader-preprint-plan.md](./research/manuscripts/nr4a3-degrader-preprint-plan.md);
  **ready-to-send outreach emails** (send the day the preprint posts):
  [research/manuscripts/nr4a3-degrader-outreach-emails.md](./research/manuscripts/nr4a3-degrader-outreach-emails.md).
  **This is a LONG-LIVED project on a RISING in-silico frontier, NOT a one-shot:** the limits of in-silico today
  aren't its limits in 6–12 months, so parked/"SKIP" items (FEP; ASO delivery) are **"revisit when capability X
  lands," not dead**, and even *completed* work is worth re-grading as methods improve — mechanism +
  trigger table in [research/method-watch.md](./research/method-watch.md). Guardrail: a coming capability
  justifies waiting/re-running, **never** claiming a result before the method supports it.
- **What (now shelved):** a zero-build static site of one-page-per-rare-cancer information
  hubs (first page: EMC). The patient-facing UI is **deprioritized/shelved** — keep it
  working if touched, but don't invest new effort there without being asked.
- **Golden rule:** never fabricate medical facts, stats, citations, or patient
  data. Everything clinical must be cited. Non-real registry data must be
  flagged `SAMPLE_SYNTHETIC` and bannered. See AGENTS.md → "medical integrity".
- **Citing & combining studies:** registry data uses a structured citation map
  (`registry.citations` + `sourceId`/`primaryRef`, primary vs secondary) and a
  fixed pooling method (crude denominator-weighted proportions + Wilson 95% CIs,
  non-overlapping cohorts only). Read **[METHODOLOGY.md](./METHODOLOGY.md)** before
  touching `registry`.
- **To add a cancer:** `node scripts/new-cancer.mjs <slug> "Name" "ABBR" "Category"`,
  then fill `data/cancers/<slug>.json` (the EMC file is the worked example).
- **A cancer page = one JSON file.** You rarely touch HTML/CSS/JS.
- **Before committing:** `node scripts/validate.mjs` must pass.
- **GPU/long SageMaker runs — checkpoint + upload continuously, never guess-and-lose
  (trimcrae standing rule).** Any job whose runtime you're estimating MUST: (1) checkpoint
  partial results to `OUTPUT_DIR` after *each* unit of work (per ligand/frame/candidate),
  (2) set the `ProcessingOutput` to `s3_upload_mode="Continuous"` so those checkpoints reach
  S3 as written — **default EndOfJob uploads only on a clean exit, so a timeout/crash loses
  ALL partial work**, (3) make the overall timeout a config input scaled to the work (with a
  per-unit timeout as the real hang-guard), and (4) treat the partial S3 checkpoint as the
  deliverable on a timeout. Full rule + the MM-GBSA incident that prompted it:
  **[research/modalities/nr4a3-degrader-next-steps.md](./research/modalities/nr4a3-degrader-next-steps.md)
  → "Infra gotchas a fresh session MUST know"**.
- **Reliable self-wake for autonomous/overnight runs = a BACKGROUND-BASH POLLER, not cron/ScheduleWakeup
  (verified 2026-06-30; a sibling session ran 48 h this way).** Launch a polling loop as a **`run_in_background:
  true`** Bash command; when it exits, the harness delivers a `<task-notification>` that **re-invokes you** —
  that completion *is* the wake-up. Pattern: poll the **public GitHub Actions API** (no auth needed for a public
  repo, ~60 req/h limit so `sleep 70`) for the run you're waiting on and **exit early when it finishes**, with a
  loop bound that exceeds the job's wall time:
  ```
  for i in $(seq 1 60); do
    s=$(curl -s "https://api.github.com/repos/trimcrae/Rare-cancers/actions/runs/<RUN_ID>" \
        | python3 -c "import sys,json;print(json.load(sys.stdin).get('status'))")
    [ "$s" = completed ] && { echo DONE; break; }; sleep 70
  done
  ```
  (Empirically confirmed 2026-06-30 with a controlled test: a 90 s background `sleep` re-invoked the agent
  ~16 s after it exited, with **no** user message — so the wake is genuinely autonomous, not just delivered on
  the next user turn.) On wake: read the poller's output file, act (read results via `report-*-aws.yml`, dispatch the next job, fix
  failures, commit/merge), then launch a FRESH poller on the next run id. **Restart-resilient** because all state
  lives in the repo/S3, not the container — after a restart just relaunch the poller against the same branch/run
  state. Get a freshly-dispatched run's id via
  `curl .../actions/workflows/<wf>.yml/runs?per_page=1`. Only inefficiency: a mistuned bound can wake you early
  with nothing new (just re-poll). **`CronCreate` is NOT reliable here** — a cron *vanished twice* within ~25 min
  / at the context-window boundary (reported "session-only" even with `durable:true`, `CronList` empty after),
  so don't depend on it. **`ScheduleWakeup` did NOT fire** outside `/loop` dynamic mode.
  **Also: the AWS account allows only ONE concurrent `ml.g5.xlarge` on-demand *Processing* job — serialize
  those (MM-GBSA, metad/denovo generation); CPU `ml.c5` docks can overlap. The spot *Training* quota is
  SEPARATE (raised to 8), so the FEP spot fleet can run concurrently with an on-demand Processing job.**
- **DEFAULT EVERY GPU RUN TO MANAGED SPOT — reframe on-demand jobs to spot *Training* whenever possible
  (trimcrae standing rule, 2026-07-03).** Spot is ~60-70% cheaper AND draws on the larger spot *Training* quota
  (8) instead of the on-demand *Processing* quota (1), so spot jobs also run more-concurrently. **Spot is safe
  BECAUSE of the checkpoint rule above** — the two go together: a `PyTorch` Estimator with
  `use_spot_instances=True`, `max_wait >= max_run`, and `checkpoint_s3_uri` + `checkpoint_local_path=/opt/ml/checkpoints`
  gets SageMaker's native resume — it **downloads prior checkpoints to /opt/ml/checkpoints on start** (a spot
  interruption OR a fresh re-dispatch with the same prefix → RESUME + extend) and **uploads continuously**. So a
  job that checkpoints per unit loses at most one interval to a spot kill. **Exemplars to copy:**
  `nr4a3_fep_sagemaker.py` (spot Training fleet) and `nr4a3_md_release_sagemaker.py` (unbiased MD, converted
  from an on-demand Processing job to spot Training 2026-07-03). **When migrating a Processing job:** move
  outputs from `/opt/ml/processing/output` → `/opt/ml/checkpoints`, mount inputs as `TrainingInput` channels
  (`SM_CHANNEL_*`), pass params as `hyperparameters` (→ `--key value` CLI args), and set `RESUME_DIR` = the
  checkpoint dir. **Only stay on-demand when spot genuinely can't work:** the job truly cannot checkpoint, or the
  needed instance type has **no spot quota** (e.g. `ml.g5.4xlarge` spot quota was 0 — a bigger-RAM need may force
  on-demand or a quota-raise). Prefer spot; justify on-demand.
  - **A TRANSIENT SPOT-CAPACITY OUTAGE IS *NOT* A REASON TO SWITCH TO ON-DEMAND — WAIT (trimcrae, 2026-07-03,
    after I did exactly the wrong thing).** When a spot job sits in `[Starting] Insufficient capacity error from
    EC2 while launching instances, retrying!`, that is temporary EC2 capacity, **not** the "spot can't work"
    exception (which is *permanent*: can't-checkpoint, or spot-quota-0). The correct response is to **do nothing**:
    the job is checkpointed, `max_wait` is ~20 h, it burns $0 while parked, and it **auto-resumes the instant
    capacity returns** (a mass g5.xlarge outage on 2026-07-03 cleared within hours and all shards resumed on
    their own). **Do NOT** stop the parked jobs, spin up on-demand replacements, probe on-demand quota, or build
    stop/relaunch tooling to "rescue" the run — that whole detour was wasted effort + real $ and had to be fully
    reverted. **This is never a race** (§ Operating regime): no single result — not even the headline FEP ΔΔG —
    justifies paying the on-demand premium to dodge a temporary outage. Extra reasons on-demand was the wrong
    call here: on-demand *Training* g5.xlarge quota is **1**, so it runs **serial** (≈40–110 h for the 3-receptor
    FEP) — *slower* than parked spot that resumes and runs **parallel** (K≤8, ≈5–14 h) — while costing ~3× (real
    FEP: ~$18–60 spot vs ~$55–150 on-demand; do NOT trust the submitter's `UNIT_GPU_H=1` cost-note stub — it
    under-quotes ABFE by ~15–30×). If a run is truly time-critical AND spot capacity is out for many hours,
    **ask trimcrae before going on-demand** — don't decide it solo.
- **VALIDATE A FAN-OUT GPU FLEET ON A SINGLE SHARD FIRST, then scale (trimcrae rule, 2026-07-03).** Any job
  that fans out N parallel GPU shards (the FEP fleet; any future spot fleet) must be shaken out with
  `n_shards=1` before launching all N — a failed env/wiring test on 8 shards burns 8× the compute for the
  same information. Because every shard checkpoints per-unit to S3 (continuous upload), the validation shard's
  completed windows are NOT wasted: the full fan-out **resumes** from them. Sequence: `mode=smoke` (spot +
  checkpoint plumbing, no MD) → **`n_shards=1` real (the heavy MD env + import + first windows)** → `n_shards=8`
  full fleet. The middle rung matters because **the smoke test skips the heavy MD conda env**, so it cannot
  catch env/isolation bugs — e.g. the 2026-07-03 FEP failure was a `PYTHONPATH` leak importing the SageMaker
  base container's numpy 1.x into the `fep` env (which itself had numpy 2), invisible to smoke. Full incident +
  fix (`entry_fep.py` clears `PYTHONPATH` for the `conda run`): next-steps.md → "Infra gotchas".
- **No dependencies, no build step.** Keep it that way.
- **Deploy:** GitHub Pages (`.github/workflows/pages.yml`) on push to `main`;
  keep all URLs relative.
- **EMC treatment-discovery track (research, not the site):** the prioritized
  portfolio is **[research/manuscripts/emc-treatment-strategy.md](./research/manuscripts/emc-treatment-strategy.md)**
  (capstone ranking of every route); every active/shelved idea + next step is on the
  "route status board" in **[research/IDEAS.md](./research/IDEAS.md)**.
  **Read those before resuming any treatment-research work** so you don't
  re-litigate settled decisions (e.g. the synth-lethal/BRD9 route was downgraded
  by a DepMap transfer-prior result; the vaccine/HLA-coverage paper is parked).
