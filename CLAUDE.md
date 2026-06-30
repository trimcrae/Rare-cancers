# CLAUDE.md

This project's full maintenance guide lives in **[AGENTS.md](./AGENTS.md)** —
read it before making changes.

## TL;DR for agents

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
  **Also: the AWS account allows only ONE concurrent `ml.g5.xlarge` (GPU) job — serialize all GPU jobs
  (MM-GBSA, metad/denovo generation); CPU `ml.c5` docks can overlap.**
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
