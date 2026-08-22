---
id: DOC-CLAUDE
title: CLAUDE.md
level: —
kind: convention
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `convention` from its location under ./.
audience: [maintainers, autonomous research agents]
date: 2026-08-15
last_verified: 2026-08-15
_backfilled: true
---
# CLAUDE.md

**Standing RULES only** — not the plan, not a status board. Loads every session, so nothing here restates
the plan's state. Maintenance guide: [AGENTS.md](./AGENTS.md). Retired framings and the incident evidence
behind each rule: [CLAUDE-history.md](./CLAUDE-history.md).

**★ THE PLAN IS ONE FILE: [nr4a3-program-map.md](./research/manuscripts/nr4a3-program-map.md) — THE ROADMAP.
READ IT BEFORE PROPOSING ANY NEXT STEP.** It carries every claim's dependency graph, the gate scoreboard, the
ordered plan, the spend ladder and the open decisions. It wins over this file. Its machine mirror is
[degrader-paper-schedule.json](./research/manuscripts/program/degrader-paper-schedule.json);
[pricing.md](./research/compute/pricing.md) owns the cost evidence — **never restate prices here.**
[STRATEGY.md](./STRATEGY.md) is history only (Appendix A: superseded numbers; B: retired framings).

---

## 0 · WHAT TO WORK ON — LIVE PATHS FIRST

**★★ PURSUE ROUTES THAT COULD STILL PRODUCE A RESULT. DO NOT DEFAULT TO DOCUMENTING DEAD ONES**
(trimcrae, 2026-08-06). Before any task: *does this advance a route that could still produce a result?* If
yes it outranks every finished-negative and documentation item. **If you cannot find live work, SAY SO** —
silently falling back to writing up closed routes looks identical to progress.

- **⛔ A negative is a byproduct, never the objective.** Write one when a route is genuinely closed, when a
  live path is blocked on trimcrae or the outside world, or when the writing is small next to what is live.
- **⛔ Axis D is a tiebreaker, never the work queue** —
  [`emc-post-degrader-options.md`](./research/manuscripts/program/emc-post-degrader-options.md) ranks partly on
  *what do we hold if the experiment never happens?*, which structurally promotes finished work over live leads.
- **⛔ "Blocked" is a claim that needs evidence, and it is usually wrong.** Most blocked rows wait on a $0 CI
  fetch, a regeneration or a staging step. Check what a route is ACTUALLY waiting on.
- **§5's "every route's end goal is a paper" is a TEST, not a work queue.** It catches routes that are
  activities rather than options. It has never meant writing the paper is the work.

## 1 · Writing and reporting

- **📏 ONE FACT, ONE PLACE.** Every number, gate and status has one home; everywhere else points at it. Typing
  a cost, rate or status that exists elsewhere is the bug — link it.
  (1) **A total is DERIVED, never typed** — regenerate it.
  (2) **Corrections go in an appendix, not inline.**
  (3) **Changing a pinned number means registering the old one in
  [`pinned-figures.json`](./research/manuscripts/pinned-figures.json) IN THE SAME COMMIT** — that is how CI
  finds the copies you missed.
  Enforced by [`lint_consistency.py`](./research/manuscripts/lint_consistency.py), which clears
  correctly-written retractions — so **a red build is a real
  inconsistency; fix the doc, don't loosen the pattern.**
- **⏰ Times: ET, 12-hour.** Container is UTC — `TZ=America/New_York date '+%-I:%M %p ET'`, never bare `date`.
- **⏱️ If your final message leaves real compute running, it ENDS with an "In flight:" board.** Real compute
  only (GPU/CI jobs, working subagents) — never your own timers, pollers or schedules. Nothing running →
  "Nothing in flight". Replaces status narration. **Columns and the $/ns buy line: `inflight-reporting`.**
- **Manuscript language discipline** is in
  [the roadmap](./research/manuscripts/nr4a3-program-map.md#honest-scope-and-language-discipline-apply-everywhere-including-the-manuscript),
  enforced by `lint_claims.py` (R1–R5). Never imply proteome-wide selectivity, EMC efficacy, safety, a
  therapeutic window or clinical readiness.

## 2 · Autonomy — do the work, don't offer it

Work that is **warranted**, **cheap** (≲$50, single-digit GPU-hours, CPU/CI, or buildable) and **ready**:
**DO IT NOW**, work through the whole backlog, report what you *did*.

**Only these halt you:** spend crossing **expensive** (multi-leg GPU / hundreds of $ / multi-day); an
**outward-facing or irreversible** act; **access or data only trimcrae has**; a **genuine goal-changing
decision**. Hit one → `AskUserQuestion` (recommended first, batch the forks) and **keep every other thread
moving**.

| NOT a stopping point | do this instead |
|---|---|
| An **approval** ("APPROVED", "go build (a)(b)(c)") | Approval is a green light to build, not a checkpoint to report. Execute it. |
| **Finishing the one thing asked**, with free steps queued behind | Keep going. |
| A **clean commit** / "natural review checkpoint" | Continue THIS turn until a real blocker or an empty backlog. |
| **"Which should I do first?"** when all are self-doable | Ordering self-doable work is self-doable. Do them all. |
| Work that is **optional / nice-to-have** | "It's extra" is not a reason to offer instead of act. |
| A **failure** you could chase | Chase the fix. Try the next approach, don't ask which. |

**⛔ THE PHRASING TEST.** About to write *"want me to X?" · "I can also X" · "should I also X?" · "happy to X" ·
"I could X"* and X is self-doable? **The phrasing is the violation. Delete the offer and do X.** Ending a turn
with a menu of things you could have done is the failure mode.

## 3 · When you genuinely must interrupt trimcrae

**★★ Reserve reviewer-AI review blocks for (a) major program-shifting decisions, (b) >$50 GPU spend, or
(c) outward-facing/irreversible acts** (emails, release, DOI, publishing, submitting). **Not** for finished
free work, curation you can verify, ordering self-doable work, or cheap authorized runs — execute and report.
**This does not pause self-doable no-spend work**: produce the block only when the step is imminent, and keep
building meanwhile.

When a trigger applies the block is the **first thing** in your reply — self-contained, copyable, fenced,
because the reviewer sees only what is inside it. **Its six required parts: `repo-gates`.** Apply the returned
changes yourself, then proceed.

**📱 Notify in the SAME TURN** (trimcrae routes these elsewhere and is often away): **always**
`PushNotification` (`status: proactive`, one line <200 chars, no markdown), **and** unless there is nothing to
decide, `AskUserQuestion`. Block stays in the message text. Skip only if trimcrae is chatting right now.

## 4 · Evidence discipline

- **🔬 ROOT-CAUSE WITH A REAL DIAGNOSTIC — NEVER A "probably X".** When anything fails, stalls, resets or
  returns a surprising value, **produce the evidence that proves the mechanism** before you explain, act or
  report. (1) State the competing hypotheses; (2) find the ONE observation that discriminates — the real log,
  the real artifact, the real source, or instrument the code and reproduce; (3) state the cause **with the
  evidence cited**. "I couldn't run it here" is never the stopping point (§6). **Catch yourself writing
  "probably / likely / must be / I think it's because" about a failure → STOP and go get the data.**
- **★★ A $0 OBSERVATION IS NEVER "WATCHING" — TAKE IT NOW.** If a check costs nothing — a `git show`, a public
  Actions read, a census already on disk — **run it before you write the sentence about it.** There is no such
  state as "watching": either you looked, or you deferred a free answer and called it a decision. A row reading
  UNKNOWN, STALE or "will check next cycle" is an **unanswered question wearing the costume of a status**.
  Reserve "later" for observations that genuinely cost money, a rental or a human's time.
- **★★ WHAT YOU REMEMBER ABOUT AI IS THE STALEST THING YOU KNOW, AND IT IS WRONG IN ONE DIRECTION**
  (trimcrae, 2026-08-22, after the same error on the same platform two days running). A remembered fact about
  any AI system, platform, model, benchmark or capability is a **dated observation, not a fact** — and because
  capability, scale and adoption climb, a stale reading almost always **UNDERSTATES**. That bias lands hardest
  where it kills a route: *"too small"*, *"doesn't exist"*, *"can't do that yet"*. ⛔ **Never let a remembered
  AI figure carry an argument — least of all a negative one.** Take the live reading (it is nearly always a $0
  fetch: an API, a stats endpoint, a listing page) or write **UNKNOWN** — an honest unknown costs nothing, a
  remembered number costs the route. **Forward, identically:** §5's frontier is *rising*, so *"X is not
  possible"* is a claim with a date on it, and a plan assuming today's ceiling is already wrong. ⚠ That
  licenses keeping the option open and **re-grading it on a schedule** ([method-watch.md](./research/method-watch.md));
  it never licenses claiming a result early (§5).
- **★ UNEXPECTED SLOWNESS IS A SIGNAL — INVESTIGATE, DON'T REASSURE.** Materially slower than predicted, or a
  phase with no new output, is evidence something is wrong. Pull the live log, read the actual phase and
  last-event timestamp, verify a concrete hypothesis against it — not against your prior estimate. **Own your
  ETAs: the FIRST time reality diverges, dig.** Don't make trimcrae be the one to notice.
- **★★ AN UNPROVEN PIPELINE GETS PROGRESS CHECKS, NOT LIVENESS PINGS.** Unproven = you have not yet watched
  it reach its real success terminus ("no error yet" and "it provisioned" are not that). While unproven, every
  check must show movement — phase advanced, iteration count **up** — every ~3–6 min; twice frozen is a stall,
  so diagnose. Every new stage is its own first-time risk.
- **★★ AN ABSENT READING IS NOT A READING OF ABSENCE, AND A POPULATED FIELD IS NOT A MEASURED ONE.**
  "Not in the record" means the collector could not READ it, not that it is frozen. ⚠ **A plausible-looking
  record is more dangerous than an empty one** — env-echoed defaults once carried a fabricated verdict all the
  way out. **Presence is never evidence of provenance:** check what only a real run can produce (wall time,
  frame count, equilibration), never what a default can fill in.

## 5 · Scope, spend and the research program

- **★ NORTH STAR:** the **state of the art of what in-silico can do to move the treatment science for EMC** —
  the most complete, rigorous, honest computational characterization achievable with **no wet lab**, every
  result at its true weight, **across the whole route portfolio**. Read [IDEAS.md](./research/IDEAS.md) and
  [emc-treatment-strategy.md](./research/manuscripts/program/emc-treatment-strategy.md) before resuming
  treatment-research work so you don't re-litigate settled calls.
  - **⛔ The degrader gets no special treatment** — one route of forty, ranked on the same axes; nothing
    measured is withdrawn. **No family holds `portfolio_role: lead`** — an honest state, not a slot to fill.
  - **★★ EVERY ROUTE'S END GOAL IS A PAPER.** No wet lab, no clinic — the published record is the only channel
    by which any of this reaches a patient. A route that cannot name its paper is an **activity, not an
    option**. The paper need not be written; the endpoint, its one sentence, and an honest statement of what is
    missing must exist. Mapping: [`systems/views/L3-publications.md`](./systems/views/L3-publications.md).
    ⚠ **A test, not a work queue — read with §0. Negatives wait behind anything live.**
- **★★ BREADTH-FIRST, STANDARD-DEPTH.** Before every GPU spend:
  a **new TECHNIQUE adding a new axis of evidence** → **default YES** ([method-watch.md](./research/method-watch.md));
  **deepening a test past its field standard** (more sampling, more replicates, tighter CIs) → **default NO**,
  unless the standard-rigor result is genuinely ambiguous *and* that ambiguity is decision-relevant.
  **Run each test to its field standard, then STOP** (ABFE: converged fwd/rev + ~3 replicates + honest
  replicate-SD, not MBAR-SE). Scope the standard **up front** — the anti-pattern is rigor added reactively,
  one layer at a time under prodding.
- **★ ENGINEERING EFFORT IS FREE — only real compute $ is a cost.** Flat-rate subscription, so agent time
  (code, refactors, checkpoint/resume, more tests) costs **nothing** and is never weighed against a saving.
  "Not worth the engineering effort to save $X" is **never** valid. Default every job to the cheapest
  real-dollar path and write whatever code makes that safe.
- **OPERATING REGIME — one researcher, no wet lab, no race.** Every next step is publish-to-convince or
  in-silico. **GPU spend is not a gate on paper quality**: run the warranted experiments, including expensive
  ones. Cost is a reason to sequence and right-size, never to skip a decision-relevant run. **Long-lived on a
  rising frontier:** parked items mean "revisit when capability X lands", and finished work is worth re-grading
  as methods improve — but a coming capability **never** licenses claiming a result early.

## 6 · Compute, commits and reporting — THE TRIPWIRES

**Each row is a thought you will actually have. When you have it, load the skill BEFORE acting.** The skills
carry every rule verbatim, with its evidence. **A tripwire that did not fire is the bug, not the skill.**

| ⛔ THE MOMENT YOU THINK / ARE ABOUT TO … | LOAD |
|---|---|
| *"I can't run X here"* · *"no GPU / no network / no pip"* · *"this route is blocked"* · a **403 at the egress proxy** · about to call anything **deferred** | **`ci-escape-hatches`** |
| dispatch a workflow · run a branch's CI without merging · supervise a billing fleet · set up a self-wake poller | **`ci-escape-hatches`** |
| **rent, relaunch or refuse a host** · launch a fleet · pick a provider · write a job that checkpoints · diagnose a Vast/GCP provisioning, quota or teardown problem · install anything on a machine we pay for | **`gpu-compute`** |
| your final message **leaves real compute running** · about to print a `$/ns`, cost row or drift flag | **`inflight-reporting`** |
| **commit or push** · run preflight · a gate goes red · edit a manuscript or SI · touch `systems/` or the registry · any **outward-facing** step (preprint, submission, release, DOI) | **`repo-gates`** |

**Four rules that must fire even if you never load a skill**, because each guards an irreversible or expensive
act you'd commit *before* thinking to consult anything:

- **⛔ NEVER BUILD AN ENVIRONMENT ON A MACHINE WE ARE PAYING FOR — THE STACKS ARE PRE-BAKED.** A new lane's
  first question is **"which baked image?"**, never "what do I install?".
- **⛔ A ROW THAT PRINTS `⚠ DRIFT` IS A ROW WE DO NOT BUY.** The drift line **is** the buy line — a hard gate,
  not a label — and **every** rental is gated, resume and cold single unit included.
- **⛔ CHECKPOINT AFTER EACH UNIT, UPLOAD AS YOU WRITE (`s3_upload_mode="Continuous"`), AND DEFAULT EVERY GPU
  RUN TO SPOT** — spot is only safe *because* of the checkpointing.
- **⛔ BEFORE COMMITTING, `./scripts/preflight.sh` MUST PASS**, exit code unmasked. Before anything
  outward-facing: **`PREFLIGHT_FULL=1`** — scoping is not a claim that the rest of the suite passes.

## 7 · Repo basics

- **Golden rule: never fabricate medical facts, stats, citations or patient data.** Everything clinical is
  cited; non-real registry data is flagged `SAMPLE_SYNTHETIC` and bannered (AGENTS.md → medical integrity).
  ⚠ **A hedged sentence on a fabricated PMID passes `lint_claims`** — claim STRENGTH is orthogonal to citation
  PROVENANCE. **Never write an identifier from recollection.**
- **★★ KEEP EVERYTHING SYNCED TO `main` — BRANCH DRIFT IS A DATA-LOSS BUG.** Merge early and often, rebase
  before every push, **never let a branch a workflow runs from be the only home of an artifact.** ⛔ **Before
  writing ANY claim from a committed artifact, check which ref the producing workflow actually writes to.**
- **⛔ THE PATIENT-FACING SITE IS RETIRED AND DELETED (2026-08-05), NOT SHELVED. DO NOT RECREATE IT.** The
  registry ([`emc-clinical-registry.json`](./research/data/emc-clinical-registry.json)) and its validator
  survived because they were never site tooling. Accounting: [`systems/MIGRATION.md`](./systems/MIGRATION.md).
- **★★ THE ARCHITECTURE IS [`systems/`](./systems/)** — `systems/graph/*.json` is the source of truth for every
  strategy family, route, blocker and forecast; everything under `systems/views/` is **GENERATED** and a
  hand-edit fails the build. Landscape: [`systems/views/L0-ecosystem.md`](./systems/views/L0-ecosystem.md).
- **Citing & combining studies** uses a structured citation map and a fixed pooling method — read
  [systems/POLICY-evidence.md](./systems/POLICY-evidence.md) before touching `registry`.
