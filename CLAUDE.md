# CLAUDE.md

This project's full maintenance guide lives in **[AGENTS.md](./AGENTS.md)** —
read it before making changes.

## TL;DR for agents

- **⏰ TIMES: ALWAYS US EASTERN (ET), 12-HOUR AM/PM, NEVER UTC / NEVER 24-HOUR (trimcrae standing rule).** Every
  time you report to trimcrae — ETAs, job timestamps, "as of HH:MM", watch cadences, anything — MUST be Eastern
  (EDT = UTC−4) AND written in 12-hour AM/PM format (e.g. "1:00 PM ET", not "13:00 ET"). Convert before writing;
  do not surface UTC or 24-hour time even if the tool/log emits it. (You keep slipping into UTC and 24-hour — this is why it's rule #1.)
- **★ PRIMARY FOCUS (UPDATED 2026-07-11, trimcrae — SUPERSEDES the 2026-06 "two papers first" plan):**
  the repo's #1 priority remains **advancing/publishing work that drives forward an EMC treatment**, but the
  approach is **BROADENING**. The NR4A3-degrader and fusion-junction ASO papers **both hit major snags**, so
  they are **no longer the first-in-line deliverables** (still active routes, NOT dead). The program now runs
  on the **full multi-route EMC strategy**, anchored by the **EMC Open Target & Drug Atlas
  ([research/atlas/](./research/atlas/))** — the integrating, provenance-checked evidence system that scores
  every route (proteostasis-chromatin; fusion-subtype antiangiogenic biomarker; fusion-junction + lineage
  antigens; direct fusion targeting) and drives **collaborator outreach** (strategy Phase B). Read
  `research/atlas/README.md` + `STATUS.md` first when resuming treatment work. **The 2026-06 detail below is
  retained FOR REFERENCE (route status), no longer "publish these two first":**
- **[PRIOR 2026-06 detail — reference only]** the earlier plan: the repo's #1 priority is **publishing work that drives
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
- **AUTONOMY THRESHOLD (trimcrae, 2026-07-05):** proceed on **cheap** in-silico steps WITHOUT asking (rule of
  thumb: ≲$50 / single-digit GPU-hours / a single inference or one-shard validation — e.g. a Boltz co-fold, a CPU
  reduce, a shakeout shard). **Come back for confirmation only when something gets EXPENSIVE** (a multi-leg GPU
  fleet, hundreds of $, or a multi-day commitment). Composes with breadth-first: adding a cheap new-axis technique
  is default-yes-just-do-it; a big depth spend still needs a nod.
- **★★ BIAS TO ACTION ON FREE/CHEAP WARRANTED WORK — DON'T SURFACE-AND-WAIT, JUST DO IT (trimcrae, 2026-07-10,
  after I identified two ready reviewer analyses, confirmed they were free CPU work, and then ASKED instead of
  running them — wasting turns).** When a piece of work is (a) clearly **warranted** (on the plan / reviewer
  list / obviously needed), (b) **cheap or free** to run (CPU/$0, or buildable via "engineering is free"), and
  (c) **ready or ready-to-build**, then **DO it immediately** — build it and launch it — do NOT stop to ask
  permission and do NOT merely report that it *could* be done. "It hasn't been run yet, it's needed, and it's
  free" is a trigger to **run it**, not to flag it. If several such items exist, batch and launch them all, then
  report what you started (not what you're about to maybe start). Asking/surfacing-first is reserved ONLY for
  work that is **expensive** (multi-leg GPU, hundreds of $, multi-day) or **genuinely ambiguous / a real
  judgment call**. Sitting on obvious, free, doable work is the anti-pattern this rule exists to kill.
- **★★ RUN AUTONOMOUSLY TO EXHAUSTION — DO EVERYTHING POSSIBLE, STOP ONLY WHEN BLOCKED BY A trimcrae DECISION
  (trimcrae standing rule, 2026-07-11).** When given a goal, do **everything you possibly can** toward it
  without checking back — build it, run it, verify it, commit it, iterate — across *all* independent
  workstreams, not just one. Do **NOT** stop to report progress, ask permission, or "surface and wait" for
  anything you can act on yourself (this composes with BIAS-TO-ACTION and ENGINEERING-IS-FREE above: cheap/free
  in-silico + CI work is default-just-do-it). **The ONLY thing that halts you is being *genuinely blocked by a
  decision that is trimcrae's to make*** — a real strategic fork, a spend that crosses the expensive threshold
  (multi-leg GPU / hundreds of $ / multi-day), or an outward-facing/irreversible action needing sign-off.
  Everything *not* blocked by that specific decision must keep moving in the meantime. **When you DO hit such a
  block, ask via `AskUserQuestion`** (it fires a phone notification) with a crisp, mutually-exclusive choice
  (recommended option first, "(Recommended)" in the label), give enough context to answer without scrolling,
  then **continue on every other unblocked thread** while waiting. Batch decisions: if several forks exist,
  put them in one AskUserQuestion (up to 4) rather than trickling them out. Reserve the ask for true
  decisions — never for "is this okay?" on work you can just do and show. The failure mode this kills: doing
  one thing, then stopping to ask "what's next?" when there was a pile of obvious, free, warranted work left.
- **★★ EXHAUST ALL SELF-DOABLE WORK *BEFORE* SURFACING ANYTHING — only come to trimcrae when COMPLETELY STUCK
  and you have a concrete thing for THEM to do (trimcrae standing rule, 2026-07-11; sharpens the rule above).**
  Before sending trimcrae *any* message, question, or status, ask: "is there anything at all I can still do
  myself?" — build/fix/run/verify/commit/iterate/route-through-CI, chase the fix rather than reporting the
  failure, try the next approach rather than asking which to try. **If yes, DO it first and do not surface.**
  Only interrupt trimcrae when you are **genuinely, completely blocked** AND the thing that unblocks you is a
  **specific action or decision that is theirs alone** (approve an outward-facing/irreversible step, resolve a
  true strategic fork, authorize an expensive spend, provide access/data only they have). When that happens,
  hand them a **concrete, ready-to-act choice** (`AskUserQuestion`, recommended-first) — not an open "what
  next?", not a progress update, not an "is this okay?". A bare status report with nothing for them to decide
  is a violation of this rule. Batch any real decisions into one ask and keep every other thread moving.
  **★ A "which direction / what should I prioritise next?" question is NEVER a trimcrae decision when every
  option on the table is work you could just do yourself — choosing the order of self-doable work IS
  self-doable. Do NOT ask which to do: pick a sensible sequence and DO THEM ALL, then report what you did.**
  (Example that triggered this rule: after finishing the atlas I asked trimcrae "outreach prep vs deepen vs
  pivot?" — all three were things I could just do; the correct move was to do all of them.) A
  direction/prioritisation call only rises to a real trimcrae decision if the options are **mutually
  exclusive AND at least one is outward-facing / irreversible / expensive, or it changes the GOAL itself** —
  not merely "which valuable thing first." Outreach *preparation* (drafting, tailoring, building the
  materials) is self-doable and must just be done; only the outward-facing **act of sending** needs sign-off.
- **★ ENGINEERING EFFORT IS FREE — only real compute $ is a cost (trimcrae, 2026-07-08).** trimcrae runs
  this on a **Claude Max flat-rate subscription**, so agent/engineering time (writing code, refactoring a
  pipeline, converting a job to spot, adding checkpoint/resume, building a new workflow, more unit tests) costs
  **nothing** and must **never** be weighed against a saving. The ONLY quantity that counts as "cost" in any
  cost/benefit call is **actual AWS/GPU dollars** (and, secondarily, wall-clock for a genuine race — which
  §Operating-regime says we almost never are). Practical consequences: (1) "not worth the engineering effort to
  save \$X" is **never** a valid reason — if converting a Processing job to spot saves even a few real $ OR just
  adds robustness, **do it**; (2) default every job to the cheapest *real-dollar* path (spot + checkpoint/resume)
  and invest whatever code it takes to make that safe; (3) prefer more tests, more hardening, cleaner resumability
  — they're free. This REFINES the cost guardrails above: the "$1000s CI-tightening" ceiling is about **compute**
  dollars, not effort; a breadth-vs-depth call is about **compute** dollars, not effort.
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
  **SINGLE SOURCE OF TRUTH (2026-07-10, trimcrae decision):** there is **no separate preprint** — the
  journal manuscript **[research/manuscripts/nr4a3-degrader-paper.md](./research/manuscripts/nr4a3-degrader-paper.md)**
  (+ its SI) IS both the ChemRxiv preprint and the JCIM submission. The old
  `nr4a3-degrader-preprint.md` / `-preprint-si.md` are retired redirect stubs (a maintained parallel
  condensed draft drifted out of sync and briefly self-contradicted — don't recreate one). Edit the paper
  once; that's the deliverable. **Pre-posting checklist (still relevant):**
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
- **★ EGRESS-PROXY BLOCK IS NOT "INACCESSIBLE" — ROUTE THE FETCH THROUGH A CI RUNNER (trimcrae standing rule,
  2026-07-11).** The dev sandbox's egress proxy **403s many data hosts at CONNECT** — NCBI/GEO, PMC,
  EuropePMC, Springer, UniProt, and similar. When a `curl`/`urllib`/WebFetch to one of these fails with a
  403/CONNECT-tunnel error, that is a **sandbox limitation, NOT a dead end** — do **NOT** report the data as
  inaccessible, the verification as impossible, or fall back to abstract-only. **GitHub Actions runners have
  unrestricted internet and are FREE — prefer them** (AWS jobs also work, use only if you already need AWS).
  Pattern (verified 2026-07-11 for GEO reprocessing + EuropePMC full-text verification): (1) write a
  **pure-stdlib** `urllib` script (no pip — matches the CPU-workflow convention); (2) add a
  `workflow_dispatch` workflow (`permissions: contents: write`) that runs it and **commits the outputs back
  to the triggering branch** (`git push origin HEAD:${{ github.ref_name }}`) or a cache branch; (3) dispatch
  it (`mcp__github__actions_run_trigger`); (4) **poll the public Actions API with a `run_in_background` Bash
  poller** (the self-wake rule above) and, on completion, `git pull` + integrate the raw outputs into the
  interpreting artifact (add caveats, flip citation `verified` flags). **Exemplars to copy:**
  `.github/workflows/atlas-data.yml` + `research/atlas/expression_reprocess.py` +
  `research/atlas/fulltext_verify.py` (GEO/PMC); `.github/workflows/fusion-cpu-extras.yml` (older CPU-extras
  pattern → `modalities-cache` branch). This is how EMC expression datasets and any PMID/PMCID full text get
  verified to primary-source standard despite the proxy.
- **GITHUB AUTH "EXPIRED" IS A FALSE ALARM — RETRY ON YOUR OWN, NEVER ESCALATE TO trimcrae (standing rule,
  2026-07-09).** When any `mcp__github__*` call returns "requires re-authorization / token expired" (or the
  harness reports the github server disconnected / needs auth), **assume YOU are wrong, not the token** — it
  refreshes on its own. **Just retry the same call.** If the first retry still fails, wait briefly (a
  `run_in_background` Bash `sleep` ~60-120 s, since foreground short sleeps are blocked) and retry again,
  looping several times over a few minutes. Do **NOT** tell trimcrae the connection is down, do **NOT** halt the
  work, and do **NOT** ask them to reconnect — that interrupts them for something that self-heals. Only even
  consider surfacing it if many spaced retries across a genuinely long window (tens of minutes) ALL fail.
- **COMMIT-SIGNATURE / "Unverified" STOP-HOOK WARNING IS FINE TO IGNORE (standing rule, 2026-07-10).** The
  `stop-hook-git-check.sh` warning that commits show as **Unverified (missing signature)** is a known,
  benign environment limitation — **do NOT act on it, and do NOT rewrite/force-push history to chase it.**
  Root cause: this repo is set up for SSH commit signing (`gpg.format=ssh`, a `user.signingkey` `.pub` is
  registered) but the **private signing key is not mounted in the agent session**, so git cannot produce a
  signature and every commit lands unsigned. The committer identity itself is already correct
  (`Claude <noreply@anthropic.com>`), so the hook's suggested `git commit --amend --reset-author` / `rebase
  --exec` fixes change nothing (there is nothing to sign with). Force-rewriting `main` (shared with sibling
  sessions) for a signature you cannot generate is strictly harmful. Just commit normally and move on; the
  "Unverified" badge only clears if trimcrae makes the private signing key available to the session.
  **Also: the AWS account allows only ONE concurrent `ml.g5.xlarge` on-demand *Processing* job — serialize
  those (MM-GBSA, metad/denovo generation); CPU `ml.c5` docks can overlap. The spot *Training* quota is
  SEPARATE (raised to 8), so the FEP spot fleet can run concurrently with an on-demand Processing job.**
- **★ UNEXPECTED SLOWNESS IS A SIGNAL — INVESTIGATE, DON'T REASSURE (trimcrae standing rule, 2026-07-08,
  after I repeatedly reported "on track" while a job was actually stuck).** When something takes materially
  longer than you predicted, or sits in one phase with no new output past what that phase should take, treat
  it as evidence that **something is wrong** and go find out — do NOT keep waiting and re-asserting "it's fine"
  and do NOT make trimcrae be the one to notice. Concretely, on any "why is this slow?" moment: (1) **pull the
  live log** (`tail-cloudwatch-aws.yml`) and read what phase it's actually in and the timestamp of the last
  event; (2) form a concrete hypothesis (stuck vs slow-but-progressing vs silent phase) and **verify** it
  against the log, not against your prior estimate; (3) if it's genuinely stuck or pathologically slow, **fix
  the root cause** (kill + re-run differently, cache the slow step, shard it, raise a cap) rather than reporting
  status again. **Own your ETAs:** if you gave one and it's blown, that is itself the trigger to dig — the
  first time reality diverges from your estimate, investigate, don't wait for the second data point. This
  composes with (does not override) the spot-capacity rule below: **investigate first to DIAGNOSE**; if the
  diagnosis is a known-benign spot capacity-wait, *then* wait it out — but you only know that by looking.
- **ALWAYS WAIT OUT SPOT CAPACITY — never switch to on-demand because a job is stuck "Starting / Insufficient
  capacity" (trimcrae standing rule, 2026-07-05).** A spot job that can't get an EC2 instance is *not* a
  problem — it is exactly what spot + per-iteration checkpointing was designed for: it waits, and when capacity
  frees it acquires an instance and resumes losing ≤1 iteration (fast reload). The binding constraint is often
  real EC2 spot *availability* (~5-6 g5 some days), which is *below* the account quota (8) — that's fine, the
  fleet just runs fewer legs concurrently and the rest queue. Do NOT diagnose a capacity-wait as a stall, and do
  NOT reach for on-demand to "unblock" it. The ONLY action a capacity-wait warrants: if a job hits `max_wait`/
  `max_run` and FAILS, **re-dispatch it** (same tag → resumes from checkpoint). Keep `max_wait` generous
  (≥ run + expected wait; ABFE uses 20h vs 12h run). On-demand is only for jobs that genuinely can't be spot
  (no spot quota for the type, or truly can't checkpoint) — never as a capacity workaround.
- **DEFAULT EVERY GPU RUN TO MANAGED SPOT — reframe on-demand jobs to spot *Training* whenever possible
  (trimcrae standing rule, 2026-07-03).** Spot is ~60-70% cheaper AND draws on the larger spot *Training* quota
  (8) instead of the on-demand *Processing* quota (1), so spot jobs also run more-concurrently. **The ~60-70%
  savings is delivered as FEWER BILLED HOURS, not a lower per-hour rate — the `SpotTraining` bill line can show a
  rate ≥ on-demand and still be far cheaper; NEVER diagnose "no discount" from the rate. Check realized savings
  with `list-sagemaker-aws.yml` `mode=savings` (billable vs training hours). Full mechanics + the mis-read that
  prompted this: next-steps.md → "HOW MANAGED-SPOT BILLING ACTUALLY WORKS".** **Spot is safe
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
