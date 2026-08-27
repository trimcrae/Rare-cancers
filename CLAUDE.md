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
- **🗣️ TALKING TO TRIMCRAE: BE CONCISE, AND WRITE IT THE `eli5` WAY — THERE AND NOWHERE ELSE**
  (trimcrae, 2026-08-25). **Concise always**: the answer he asked for, not the transcript of how you
  got it. Every reply addressed to him is plain language — lead with the point, one idea per
  sentence, jargon replaced rather than glossed. Rewrite rules: `eli5`.
  ⛔ **AND ONLY THERE.** A manuscript, an SI, a commit message, this file, a code comment, a docstring
  or an artifact keeps its own register: those are written for reviewers and for the NEXT SESSION,
  and they are dense on purpose. Plain language in a reply to him is a service; plain language in a
  deposit artifact is lost precision.
  ⛔ **PLAIN NEVER MEANS WEAKER.** A hedge, a null, an UNKNOWN, a negative and a number keep exactly
  the strength they had. Making a result sound cleaner than its evidence is the one failure this
  rule can cause, and it is worse than the density it replaced.
- **📞 THE MAIN THREAD IS TRIMCRAE'S CHANNEL — KEEP IT FREE** (trimcrae, 2026-08-25: *"always leave
  the main thread of the session free for interactions with me… no tasks or shell scripts ever block
  you seeing my messages"*). He must be able to reach you instantly, so **nothing long-running may
  occupy the foreground.** A long shell command → `run_in_background`. Multi-step work → **a
  subagent, and that is standing authorisation to spawn one — UP TO `subagent_width` OF THEM AT
  ONCE, WHICH YOU READ FROM [`autonomy-state.json`](./research/autonomy/autonomy-state.json)
  RATHER THAN REMEMBER** (5 at `backoff_level` 0, falling 5 → 2 → 1 as the level rises).
  ⛔ **The unit is CONCURRENT agents, and the cap is the dial the architecture records as having
  failed catastrophically:** a 107-agent fan-out hit the account weekly limit — **40 completed,
  67 errored, the synthesis lost**, findings recovered by hand from `journal.jsonl`. Width moves
  last and moves down faster than it moves up.
  ⚠ *Added 2026-08-26 because the number governed nothing: `grep -rn subagent_width` over the
  whole repository returned TWO hits — the JSON defining it and one test asserting it equals 5.
  No code read it and no receipt recorded a dispatch, so compliance was luck. `health.py`'s
  `fanout_is_governed` now measures it, and a receipt that records no `subagents` block leaves
  that row UNMEASURED rather than green.* A gate, a suite, a build, a fetch →
  backgrounded, never awaited in the foreground.
  ⛔⛔ **AND `run_in_background` IS NOT THE SAME AS A SHELL `&` — ONE COMES BACK AND THE OTHER
  ORPHANS THE WORK.** `run_in_background: true` registers a job the harness TRACKS and wakes you
  for. A bare `&` detaches the process: nothing tracks it, nothing ever wakes you, and the turn
  ends with the work abandoned while you report it "in flight". **The test: after this command,
  is there anything that will bring the session back?**
  ⚠ *Measured 2026-08-27, twice in one session, and it is the shape that LOOKS responsible —
  `&` keeps the foreground free, satisfying the letter of the rule above while breaking the
  thing the rule is for. Two preflight runs abandoned, one dead at 35 lines with no exit marker,
  and trimcrae had to notice the silence. `.claude/hooks/no-detached-background.py` now REFUSES
  the call, because this is the fifth rule in two days that was correct and measured by nothing.*
    ⛔ **NO FOREGROUND WAIT LOOPS.** An `until … sleep` loop, a long blocking command, a poll — each is
  a window in which his message sits unread. **The test: if he messaged right now, how long until you
  saw it?** More than a few seconds means that call is in the wrong place.
  ⚠ **This is the responsiveness half of §6's gate rule and it is the stricter half:** §6 says a
  running gate must not stop the WORK; this says it must not stop the CONVERSATION either. A turn
  that ends with the foreground free is the normal shape — you are notified when background work
  lands.
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
| A **gate running** (preflight, CI, a suite) | It gates the COMMIT, not the work. Background it and take the next task — §6. **Polling is not work.** |

**⛔ THE PHRASING TEST.** About to write *"want me to X?" · "I can also X" · "should I also X?" · "happy to X" ·
"I could X"* and X is self-doable? **The phrasing is the violation. Delete the offer and do X.** Ending a turn
with a menu of things you could have done is the failure mode.

## 3 · When you genuinely must interrupt trimcrae

**★★ Reserve reviewer-AI review blocks for (a) major program-shifting decisions, (b) >$50 GPU spend, or
(c) outward-facing/irreversible acts** (emails, release, DOI, publishing, submitting). **Not** for finished
free work, curation you can verify, ordering self-doable work, or cheap authorized runs — execute and report.

- **⛔⛔ A GATE YOU COULD RESOLVE IS NEVER AN ESCALATION, AND "IT WOULD BE SELF-SERVING TO DECIDE" IS A
  REASON TO BE CAREFUL, NOT A REASON TO HAND IT OVER** (trimcrae, 2026-08-27: *"That's not the kind of
  thing that should be elevated to me. I'm only here to submit papers."*). ⚠ **Measured that day:** a
  cosmetic typography ceiling — two blown justification lines over its limit — was put to him as a
  decision, on the reasoning that re-pinning the ceiling would be the self-serving edit
  `amendment_guard` exists to catch. **That reasoning was sound and the conclusion was wrong.** The
  self-serving option was re-pinning; the honest option was to *do the work*, and the work was three
  more rewording attempts plus a search over meaning-preserving variants. It converged in one pass —
  two comma-and-verb swaps took 11 blown lines to 9, under the ceiling, with no guard touched.
  ★ **THE TEST: is there ANY action I could take that resolves this without weakening a bar?** If yes,
  take it — however tedious, and even where the tempting shortcut would have been governed. Engineering
  effort is free (§5); his attention is not. ⛔ **He is here for the four §3 triggers and to submit
  papers. A red gate, a stale artifact, a flaky suite and a tuning constant are all yours.**
**This does not pause self-doable no-spend work**: produce the block only when the step is imminent, and keep
building meanwhile.

- **⭑ AMENDED 2026-08-26 FOR aiXiv ONLY — THE RULE BELOW IS OTHERWISE UNCHANGED AND STILL BINDS.**
  trimcrae granted a **standing, bar-scoped** authority to post to **aiXiv** without naming the
  paper: *"Broad: any paper meeting the bar"*. The bar is the six clauses in
  [`publish_bar.py`](./research/autonomy/publish_bar.py), each computed from a committed artifact and
  each failing closed; the grant, its edges and the backdrop it was given against live in
  [`publication-authority.json`](./research/autonomy/publication-authority.json); the reasoning is
  [the autonomy architecture](./research/manuscripts/program/emc-autonomy-architecture.md) §6.3.
  ⛔ **The amendment reaches aiXiv and NOTHING else.** A journal submission, a Zenodo publication, a
  release, a DOI and any outreach still require that he named THAT paper for THAT act. **And a bar
  clause may never be loosened by the cycle it just blocked** — `amendment_guard.py` refuses that.
- **⛔⛔ PUBLISH ONLY THE PAPER TRIMCRAE NAMED, AS THE PAPER IT IS. PER PAPER, PER ACT**
  (trimcrae, 2026-08-23, after both halves were broken in one session). Submitting, posting a new
  version, or otherwise putting a manuscript in public under his name and ORCID requires that **he
  named THAT paper for THAT act**. Never infer the paper from a goal, a quality bar, a portfolio
  view or a previous approval of a different one. **A standing standard — "get everything to at
  least a 7" — is a BAR FOR WHAT WE SUBMIT, NOT A LICENCE TO SUBMIT**; it says how good a thing must
  be before it goes out, and says nothing about which thing goes out or when.
  - **⛔ BEING BLOCKED IS NOT AUTHORISATION.** A goal you cannot otherwise satisfy, a stop condition
    that will not clear, an instruction to "keep iterating" — none of these selects a paper. When the
    only way left to satisfy a goal is an act nobody authorised, **the goal is what yields**, and you
    say so. ⚠ The tell is reasoning of the form *"the standing goal must implicitly cover this"* —
    that is the sound of talking yourself into it, and on 2026-08-23 it followed two messages after
    writing *"picking which one to publish is yours, not mine."*
  - **⛔ AND DO NOT RESHAPE A NAMED PAPER INTO A DIFFERENT ONE.** Retitling or reframing the paper he
    asked for — to chase a score, a venue's taste or a reviewer's rubric — publishes something he did
    not ask for under the identifier he did. The claims may be untouched and it is still the wrong
    paper: **the title is what a reader searches and what the record says the work is.**
  - ✅ **What needs no permission is unchanged:** building the PDF, generating metadata, running the
    gates, dry runs, fetching reviews, calibrating. Prepare everything; post nothing.

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
| ⛔ about to **dispatch CI to answer a question** — *"let me fetch that to be sure"* · a conversational *"what is X / does Y exist / link me"* · escalating because the last rung failed | **`ci-escape-hatches` §0 — `WebSearch` is rung 0 and CI is rung 1. Escalate on the ANSWER'S VALUE, never on the previous rung's failure.** |
| dispatch a workflow · run a branch's CI without merging · supervise a billing fleet · set up a self-wake poller | **`ci-escape-hatches`** |
| **rent, relaunch or refuse a host** · launch a fleet · pick a provider · write a job that checkpoints · diagnose a Vast/GCP provisioning, quota or teardown problem · install anything on a machine we pay for | **`gpu-compute`** |
| ⛔ **take a ledger item** · *"I'll run a cycle"* · *"let me do a hardening round"* · run blind seats · write a receipt — **INCLUDING when trimcrae just asks for it in conversation, which is the path the rule was unreachable from** | **`research-loop` — §3 owns the SESSION SHAPE, and a hardening round is a SPAWNED SESSION, not more work in this one** |
| your final message **leaves real compute running** · about to print a `$/ns`, cost row or drift flag | **`inflight-reporting`** |
| **commit or push** (a merge to `main` included — that is the ordinary commit loop) · run preflight · a gate goes red · edit a manuscript or SI · touch `systems/` or the registry · **PUBLISH** — and publishing is the closed list *preprint, submission, release, DOI*, the only four things `PREFLIGHT_FULL=1` is for (the default run is fast gates only; `PREFLIGHT_TESTS=1` adds the manuscripts suite,
`PREFLIGHT_MODALITIES=1` the modalities one) | **`repo-gates`** |

**Four rules that must fire even if you never load a skill**, because each guards an irreversible or expensive
act you'd commit *before* thinking to consult anything:

- **⛔ `pgrep -f` / `pkill -f` MATCH THE SHELL THAT RUNS THEM — NEVER PATTERN-MATCH YOUR OWN COMMAND**
  (three times in one session, 2026-08-26). The pattern text sits in the wrapper's own command line, so
  `pkill -f preflight.sh` kills the shell issuing it and `until ! pgrep -f "bash ./scripts/preflight.sh"`
  never exits — it matches itself, forever. **Cost, measured: two orphan poll loops trimcrae had to spot in
  the task list, and one killed gate run.**
  ⭐ **Wait on an ARTIFACT, not a process:** have the command write a marker (`echo "EXIT=$?" >> log`) and
  `until grep -q "^EXIT=" log`. To stop a background job use **`TaskStop`**, which knows the job's real id.
  ⚠ And a poll loop is nearly always the wrong tool anyway — §1: the foreground stays free, and the harness
  notifies you when background work lands.

- **⛔ CONTEXT IS A RESOURCE THAT RUNS OUT SILENTLY, AND THE SESSION SPENDING IT IS THE ONE THAT
  CANNOT TELL.** A second full cycle in one session is the cap; a third is the bug. **`research-loop`
  §3 owns the three session shapes** — *this session* for the ordinary case, *parallel subagents* for
  independent items and for a hardening round's blind seats, and **a SPAWNED SESSION for anything that
  will not fit one context, which explicitly includes a full hardening cycle.**
  ⛔ **AND THE DRIVER NEVER WAITS: dispatch, record, END THE TURN.** Holding a turn open until a
  subagent lands is a cycle a rate limit can kill while it holds uncommitted work — and it spends the
  driver's context on the search instead of on the verdict, which is the whole reason the seat was a
  subagent.
  ⚠ *Measured 2026-08-26, and the failure was TOTAL RATHER THAN PARTIAL: the rule lives in a skill,
  a skill binds only when loaded, and `"name":"Skill"` appears **0 times** in the transcript of the
  session that broke it. Every one of that skill's four load triggers is a Routine firing a cycle, so
  on the interactive path — trimcrae asking for research work directly — the rule was not weak, it was
  **UNREACHABLE**. One session ran CYC-0005 and CYC-0006 end to end, compacted 23 times and reached a
  7.6 MB transcript; an earlier one ran three cycles. That is why this row is HERE, in the file that
  loads every session, and not only in the skill. `health.py`'s `cycles_are_sized` now measures it.*

- **⛔ NEVER BUILD AN ENVIRONMENT ON A MACHINE WE ARE PAYING FOR — THE STACKS ARE PRE-BAKED.** A new lane's
  first question is **"which baked image?"**, never "what do I install?".
- **⛔ A ROW THAT PRINTS `⚠ DRIFT` IS A ROW WE DO NOT BUY.** The drift line **is** the buy line — a hard gate,
  not a label — and **every** rental is gated, resume and cold single unit included.
- **⛔ CHECKPOINT AFTER EACH UNIT, UPLOAD AS YOU WRITE (`s3_upload_mode="Continuous"`), AND DEFAULT EVERY GPU
  RUN TO SPOT** — spot is only safe *because* of the checkpointing.
- **⛔ BEFORE COMMITTING, `./scripts/preflight.sh` MUST PASS**, exit code unmasked. **That plain command
  is the answer almost every time — it is the commit loop, it costs about **75 seconds**, and it runs
  EVERY fast gate: the doc linters, the systems model, medical integrity, citation provenance and the
  generated-artifact check, plus gate 13, the test selector's own contract.**
  ⚠ *Measured 2026-08-24: fast gates **31.4 s** + gate 13 **39.3 s** = **77.5 s**. Gate 13 was added
  to `main` as "a fast, offline, pure-logic suite"; it is half the loop, because each of its 55 tests
  builds the selector's import graph and shells out to git. Moving it behind `PREFLIGHT_TESTS=1`
  would take the commit loop back to ~31 s — that is trimcrae's call, not a silent one to make
  inside a merge.*
  - ⭐⭐ **A GATE RUNNING IS NOT A REASON TO STOP WORKING, AND POLLING IT IS NOT WORK**
    (trimcrae, 2026-08-25: *"it absolutely murders our wall clock time when we wait for preflight
    when we KNOW there's more work to be done"*). **Preflight and CI gate the COMMIT, not the
    work** — no edit, read, investigation, draft, CI dispatch, subagent or question to trimcrae is
    blocked by a running suite. Start it in the background and take the next task.
    ⛔ **If your next action is "check whether it's done", you have no plan.** A `tail` in a loop is
    the tell; take the next backlog item, or say the backlog is empty.
    ★ **AND RUN IT ONCE, WITH THE TREE SETTLED.** Every tree-touching edit invalidates the run in
    flight, so a preflight started before the edits AND their regenerations are done is one you will
    throw away — finish them, then one run, with the non-tree-touching work (reporting, dispatch,
    reading, the question for trimcrae) placed in the window it occupies. **An invalidated run is
    cheap and an idle wait is not** (§5: engineering and CPU are free), so kill a run the tree moved
    under rather than sit through it to protect it.
    ⛔ **What does not bend: the run you report green must be the run that saw the tree you commit.**
    ⚠ *Second complaint of this family — 2026-08-23 produced `PREFLIGHT_TESTS=1` and the failure
    survived it, because the cost was never the suites, it was the serialization. Measured evidence:
    [CLAUDE-history.md](./CLAUDE-history.md).*
  - ⭐⭐ **AND MODALITIES CAME OUT OF `PREFLIGHT_TESTS` ENTIRELY ON 2026-08-25 — `PREFLIGHT_MODALITIES=1`**
    (trimcrae: *"Just turn off modalities completely if it's that big an issue"*). Measured that day over
    four runs: modalities **481–535 s** against manuscripts **225–255 s**, fast gates ~31 s, selector suite
    ~55 s — **62% of a 13.5-minute gate**, every run of it the full 7,924 tests.
    ⛔ **AND THE "FULL" WAS NOT A CHOICE ANYBODY MADE.** `affected_tests.py` fails safe: if it or
    `preflight.sh` differ from what `scripts/selector-validation.json` says a FULL run validated, it
    answers FULL. **Both hashes are stale** — `preflight.sh` changed 2026-08-23, `affected_tests.py`
    arrived by merge 2026-08-24 — and **only a `PREFLIGHT_FULL=1` run re-stamps that record**, which this
    section reserves for publication. A tripwire clearable only by a rare act is a permanent tripwire.
    ⚠ **That diagnosis is still open and is NOT fixed by the flag** — re-stamping is a separate call.
    ⛔ **The cost, plainly: a modality break is no longer caught before the commit.** `tests.yml` runs
    both suites in full on every push with the real dependencies and is the authority, so it is caught
    minutes later and costs one more commit — the same trade already made for the manuscripts suite below.
  - ⭐ **THE TEST SUITES ARE OPT-IN AS OF 2026-08-23 — `PREFLIGHT_TESTS=1` — BECAUSE THEY WERE THE GATE**
    (trimcrae: *"change the rules so that it's not constantly running and blocking things"*). Measured
    that day: fast gates **31.4 s**, manuscripts suite **176.1 s on every single commit** including one
    against a clean tree, modalities ~0 s (already scoped). **CI runs both suites in full, on every push,
    with the real dependencies, and it is the authority** — the local copy was the slower, weaker
    duplicate, which is the same finding that scoped the modalities suite on 2026-08-12.
    ⚠ **Scoping this suite was tried first and the measurement refused it**: a selector validated
    against traced ground truth reached zero under-selection and still left a **132.5 s floor of the
    176.1 s**, because these guards bind to directory scans and to paths read out of committed
    artifacts. The honest finding is that the suite is not scopeable.
    ⛔ **This is a real cost, not a free win: gate 12 was put in the commit loop precisely so a citation
    guard would not "fire after the mistake is shared".** It now does fire later — caught by CI minutes
    later and fixed with another commit, which is exactly the content-vs-ceremony line drawn below.
    **Editing a manuscript, an SI, a citation or a deposit artifact? `PREFLIGHT_TESTS=1` is one word.**
  - ⭐ **A RED PREFLIGHT IN A FRESH SANDBOX IS USUALLY THE SANDBOX — RUN `./scripts/dev-setup.sh` FIRST.**
    On 2026-08-23 `main` was red on a clean tree at `origin/main`: gate 2 wanted `jsonschema`, and 29
    manuscript guards wanted `pdfminer.six`/`pypdf`. Nothing was wrong with the repository — CI was green
    on the same commit — and installing the packages, with no tracked file touched, took it to
    `0 ERROR` / `878 passed`. A `SessionStart` hook now runs `dev-setup.sh --if-needed`, so this should
    heal itself; if a gate still fails on an import, that is the fix, not a bug hunt in the manuscripts.
  - **`PREFLIGHT_FULL=1` IS FOR PUBLICATION AND NOTHING ELSE — A CLOSED LIST: a preprint, a journal or
    aiXiv submission, a release, a DOI/Zenodo deposit.** That is the whole list. It costs **~25 minutes**
    (the modalities suite alone is ~20), so running it where it is not required is not "being careful",
    it is spending half an hour to learn nothing the scoped run did not already tell you.
  - ⛔ **A MERGE OR PUSH TO `main` IS THE COMMIT LOOP, NOT PUBLICATION.** ⚠ *Added 2026-08-23 after this
    exact reasoning cost about two hours: `main` is the trunk every workflow runs from, which feels like
    it should raise the bar, and the rule as written never said otherwise — it defined FULL by four
    examples and named nothing on the other side, so the gap got filled with the expensive guess.*
    **The test is NOT how important the ref is, and it is NOT visibility — the repo is PUBLIC and a
    stranger CAN read `main`, but that is a permission, not a reader.** ★★ **THE TEST IS WHETHER
    ANYONE ACTUALLY READS IT, AND THE ANSWER FOR THIS REPOSITORY IS NO** (trimcrae, 2026-08-23:
    *"Nobody is reading this repo. The only time anyone reads anything is when we submit a paper."*).
    **This repository has exactly one reader — the project itself: trimcrae and the agent sessions.**
    Every mistake in it is found by us and fixed by us with another commit, and nobody outside ever
    had to care. **A submission is the ONLY moment anything here reaches an outside reader**, and it
    is undone only by a public correction against an identifier somebody may already have cited.
    **That is what the 25 minutes is for, and it is the only thing it is for.** So also just
    `preflight.sh`: a commit, a merge or push to any branch including `main`, a PR, a regenerated
    artifact, a CI dispatch.
  - ⛔ **AND THIS IS NOT A LICENCE TO BE SLOPPY IN THE REPO — IT SEPARATES TWO THINGS THAT KEEP GETTING
    CONFLATED.** *Rigour of CONTENT* — one fact one place, a derived total never typed, an honest
    UNKNOWN over a remembered number, a negative reported at its true weight — **does not scale with
    audience and never relaxes**, because the thing relying on it is the NEXT SESSION, which inherits
    every wrong number as a fact. *Ceremony of GATING* — how many minutes of checking an act buys —
    **scales with who reads the result**, which is nobody until we submit. **Get the content right
    every time; spend the 25 minutes only at the one door that opens outward.**
  - ⭐ **AND THE CASCADE IS THE REAL COST, NOT THE 25 MINUTES.** An unnecessary FULL run surfaces
    pre-existing failures that have nothing to do with your change, and chasing them is now your
    afternoon. **If FULL goes red on something you did not touch, the FIRST move is `git stash` and
    re-run on clean `origin/main`** — if it reproduces, it is not yours, and the decision to fix it is
    a SEPARATE task to raise, not to absorb silently into the one you were asked for.
  - **The one thing the default run does not do is claim any test passes — and it now says so in its own
    verdict line** rather than printing a bare `PREFLIGHT OK`. That is fine, because `tests.yml` runs
    both suites on every push, with the real dependencies, and it is the authority. **Watch CI; do not
    pre-run it locally.** ⚠ *Superseded, retained (rule 1.2): "the scoped run", written when the test
    suites were still in the default tier and only the modalities half was scoped.*

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
