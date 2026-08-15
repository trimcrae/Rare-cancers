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

Full maintenance guide: **[AGENTS.md](./AGENTS.md)**.
**THE PLAN IS ONE FILE: [nr4a3-program-map.md](./research/manuscripts/nr4a3-program-map.md) — THE ROADMAP.
READ IT BEFORE PROPOSING ANY NEXT STEP.** It carries the dependency graph of every claim the paper has to
establish and which instrument each rests on, **and since 2026-08-02 it also carries the whole plan** — the
gate scoreboard, THE ORDERED PLAN, the spend ladder, the validation architecture, the language-discipline
rules and the open decisions, all moved out of STRATEGY.md rather than copied. Its reason for existing is that
those dependencies were prose-only, so they were re-derived every session and blockers were repeatedly
misattributed (trimcrae, 2026-08-02). **[STRATEGY.md](./STRATEGY.md) is now history only** — Appendix A
(superseded numbers, cited as data) and Appendix B (retired framings).

**This file is standing RULES, not the plan and not a status board.** It loads into every session, so it stays
short by construction: **no ladder, no gate scoreboard, no spend totals, no "what is running now".** Those
live in the roadmap, and anything here that restates them is a bug — see rule 1.
⚠ *Superseded, retained: "no cost figures … no history." Both were false of this file as written — it
carried `$0.006539/ns`, `$0.003412/ns`, `$0.200/hr`, `$22.62`, `$68.98`, and dated incident narratives
throughout §4, §6 and §7. The distinction that actually holds is not figure-vs-no-figure: **a number stays
here only when it IS a rule** (the buy line you refuse to cross), and **an incident stays only when it is
the evidence a rule rests on** — which is why nearly every rule below names the day it was learned. What
does not belong is the plan's own state.*

## ⚙ HOW THIS FILE IS SPLIT — READ ONCE, THEN USE §6

**Since 2026-08-15 the reference material lives in four project skills and only the REFLEX rules are
resident here.** The file was 902 lines / ~12,200 words, of which §6 alone was 45 %; every session paid for
all of it whether or not it went near a GPU. What moved is what you can *know in advance you need* — how to
rent a host, what the nine preflight gates are, the in-flight board's column format. What stayed is
everything that has to already be in your head **because it fires on a situation you don't yet know you are
in**: which work to pick, when not to offer, what to do when something fails, when you are allowed to say
"probably".

⛔ **THE SPLIT AXIS IS TRIGGER PREDICTABILITY, NOT TOPIC — AND GETTING THAT WRONG IS THIS REPOSITORY'S OWN
DOCUMENTED FAILURE.** §6's environment-build rule was once filed under a heading that said *"CI
environments"*, so it did not fire on a rented GPU host and a 4090 billed through a full `apt-get`/`pip`
build: ***"A rule filed where it cannot fire is absent."*** A skill that loads only when you already
realise the topic applies is a stronger version of exactly that hazard. So **every moved block leaves a
tripwire in §6 phrased as the thought you will actually be having** — "I can't run X here", "this is
blocked", "about to commit" — never as a topic you have to first classify yourself into. **If you ever
find a tripwire that did not fire, the tripwire is the bug, not the skill.**

*Superseded, retained: §6 "Running compute" and §7 "Repo basics" as ~7,300 words of inline text; §1's
in-flight board format and `$/ns` derivation; §5's deliverable file map. All are verbatim in the skills
below and are still `pinned-figures.json` targets, so `lint_consistency.py` checks them exactly as before.*

---

## 0 · WHAT TO WORK ON — LIVE PATHS FIRST

**★★ PURSUE ROUTES THAT COULD STILL PRODUCE A RESULT. DO NOT DEFAULT TO DOCUMENTING DEAD ONES
(trimcrae, 2026-08-06: *"We need to be pursuing live paths. That's the fundamental goal of the whole repo …
prioritizing actual results. Not publishing negatives."*).** This is first because it is the question every
session answers before it answers any other, and because a session that gets it wrong can spend an entire
day being rigorous about nothing that matters.

**The test, applied before starting ANY task:** *does this advance a route that could still produce a
result?* If yes, it outranks every finished-negative and every documentation item on the board. **If you
cannot find live work, SAY SO EXPLICITLY** — "no live $0 work is available, here is why" is a report
trimcrae can act on; silently falling back to writing up closed routes is not, because it looks identical
to progress.

- **⛔ A NEGATIVE IS A BYPRODUCT, NEVER THE OBJECTIVE.** Write one when a route is genuinely closed, when a
  live path is blocked on something only trimcrae or the outside world can supply, or when the writing is
  small next to what is live. **Never in preference to work that could still move a route.** Publishing is
  how a result reaches a patient; it is not a substitute for having one.
- **⛔ BEWARE THE AXIS THAT RANKS FINISHED THINGS FIRST.**
  [`emc-post-degrader-options.md`](./research/manuscripts/program/emc-post-degrader-options.md) grades routes partly
  on **Axis D — *what do we hold if the experiment never happens?*** That axis is real and was added for a
  good reason, but it **structurally promotes completed negatives over live leads**, because a finished
  write-up always scores full marks on it and a live lead never does. **Read Axis D as a tiebreaker, never
  as the work queue.** *(Measured 2026-08-06: a session took that ranking at face value and put four
  parallel agents on a failure-record paper, a closed-route paper and two housekeeping sweeps — with the
  ASO panel retracted, the neoantigen predictions carrying `⛔_RETRACTED_SEAMS` and the TCIP route one $0
  CI fetch from naming an effector. Zero of four were on a live path, and it took trimcrae asking to catch
  it.)*
- **⛔ "BLOCKED" IS A CLAIM THAT NEEDS EVIDENCE, AND IT IS USUALLY WRONG.** Most rows that read blocked are
  blocked on a **$0 CI fetch, a regeneration, or a staging step** — not on money, not on a wet lab, and not
  on a capability that does not exist. §6 says the sandbox is not your execution limit; §4 says a free
  observation is never "watching". **Before accepting any route as blocked, check what it is ACTUALLY
  waiting on** — the answer has repeatedly been something free that nobody had done.
- **This does NOT retire "every route's end goal is a paper" (§5), and the two are easy to confuse.** That
  rule is a **test of whether a route is a real option** — a route that cannot name the paper it is for is
  an activity, not an option. It has never meant that *writing* the paper is the work. Keep it as the test
  it is. ⚠ *Superseded, retained: the reading of §5 under which "a closed route is not exempt — a
  definitional closure is a publishable negative" made negative-writing a standing task. Closures are still
  worth publishing and the field still publishes almost none of them; what changes is that they wait behind
  anything live.*

---


## 1 · Writing and reporting

- **📏 ONE FACT, ONE PLACE — AND WHEN YOU CORRECT A NUMBER, REGISTER THE OLD ONE (trimcrae, 2026-07-25, after a
  cleanup found the ladder total at THREE values in one file, a high band that did not sum, a spine
  contradicting the table it summarised, and a rung recorded as both UNPRICED and PRICED).** Every number, gate
  and status has exactly **one home** and everywhere else **points at it**. If you catch yourself typing a cost,
  rate or status that already exists somewhere, that is the bug: link it.
  1. **A total is DERIVED, never typed** — regenerate it (`vast_cost_model.py` → `vast-ladder-repricing.json`)
     and let the checker verify it sums. Hand-carried totals drift silently.
  2. **Corrections go in an APPENDIX, not inline.** Never silently drop a superseded number — but never leave
     the "was X, then Y, both wrong, now Z" narrative in the live text either, because the old values stay
     quotable. One appendix line; the live text carries only the current value.
  3. **Changing a pinned number means adding the old one to
     [`pinned-figures.json`](./research/manuscripts/pinned-figures.json) IN THE SAME COMMIT.** Not paperwork —
     it is how CI finds the copies you missed.
  **Enforced, because prose discipline is exactly what already failed here** (the same reason `lint_claims.py`
  exists): [`lint_consistency.py`](./research/manuscripts/lint_consistency.py) runs in CI over every file in
  [`pinned-figures.json`](./research/manuscripts/pinned-figures.json) → `targets` — the roadmap, this file,
  the paper and SI, the schedule JSON, the NR-V04 prereg and the compute docs among them. ⚠ *Superseded,
  retained: an eight-file list typed out here. Nothing in it was wrong; it had silently fallen five short of
  the registry's 13, which is what restating a list instead of pointing at it always does.* Run it
  before committing doc changes: `python3 research/manuscripts/lint_consistency.py`. It clears correctly-written
  retractions, so **a red build is a real inconsistency — fix the doc, don't loosen the pattern.**
- **⏰ TIMES: ALWAYS US EASTERN, 12-HOUR AM/PM. NEVER UTC, NEVER 24-HOUR.** Every time you report — ETAs, job
  timestamps, "as of", cadences — must be ET (EDT = UTC−4) in 12-hour form ("1:00 PM ET", not "13:00"). Convert
  before writing even if the tool emits UTC. *(You keep slipping. This is why it is near the top.)*
  - **⛔ THIS CONTAINER IS `Etc/UTC`, SO BARE `date` IS UTC. USE
    `TZ=America/New_York date '+%-I:%M %p ET'` — NOTHING ELSE (trimcrae, 2026-08-07: *"There's no way
    that ETA is right. That would mean our preflight takes 5 hours"*).** Measured that evening:
    `date '+%-I:%M %p'` returned `9:44 PM` and `TZ=America/New_York date` returned `5:44 PM EDT` — the
    same instant, four hours apart. **The rule above was being obeyed in form and broken in fact**: the
    reading was measured rather than guessed, and then `ET` was typed after a UTC number, so the
    conversion the rule demands never happened. Every time reported in that session ran four hours
    fast until an ETA got absurd enough to notice.
    ⚠ **THE FIRST FIX FOR THIS FAILED IN A WAY WORTH RECORDING.** Earlier the same day the same
    complaint was raised (a 2:31 PM reported at 10:53 AM), diagnosed as *fabricating* timestamps, and
    fixed by measuring with `date` every time. That fix was correct about guessing and left the
    mislabelling untouched — so the error survived its own remediation and looked repaired. **A
    diagnosis that explains the symptom is not thereby the cause**; §4 says produce the evidence, and
    the discriminating observation here cost one shell command nobody ran. Subagents in this same
    container converted correctly, which is how the blast radius stayed in chat: no commit message and
    no tracked file carried a bad ET time.
- **⏱️ END-OF-TURN "IN FLIGHT" BOARD (trimcrae, 2026-07-11).** Whenever your final message leaves work running,
  the LAST thing in it is a compact **"In flight:"** board — one scannable line per item (bullet/table, not
  prose): **what it is · current state · ETA in ET 12-hour · cost · $/ns** (or an explicit "ETA unknown — why").
  **List ONLY real compute** (GPU/CI jobs, subagents doing real work) — **not** your own wake mechanisms
  (self-timers, pollers, heartbeats) and **not scheduled routines**; a schedule is not running compute.
  Nothing running → "Nothing in flight", one line. This REPLACES long status narration.
  **Cost is part of the format, not an extra**, and per rule 1 the figure POINTS at its home rather than being
  typed fresh. ⛔ **The full column rules — when a board carries a `$/ns` column at all, the `—` convention, the
  absolute buy line and why `⚠ PAYING OVER` and `⛔ REFUSED` must never render alike — are in
  `inflight-reporting`. Load it before you print a board with a GPU row.**
- **Language discipline for the manuscript** is in
  [the roadmap](./research/manuscripts/nr4a3-program-map.md#honest-scope-and-language-discipline-apply-everywhere-including-the-manuscript)
  → "Honest scope and language discipline" and enforced by `lint_claims.py` (R1–R5) in CI. Never imply proteome-wide selectivity, EMC
  efficacy, safety, a therapeutic window, or clinical readiness.


## 2 · Autonomy — do the work, don't offer it

**One rule, five ways it has been broken.** When work is (a) **warranted** (on the plan / reviewer list /
obviously needed), (b) **free or cheap** (≲$50, single-digit GPU-hours, a CPU/CI run, or buildable — see
"engineering is free"), and (c) **ready or ready-to-build**, then **DO IT NOW**, keep going through the entire
backlog, and report what you *did*. Not what you could do, not what you're about to start.

**The only things that halt you** are a real blocker that is trimcrae's alone: a spend crossing the **expensive**
threshold (multi-leg GPU / hundreds of $ / multi-day), an **outward-facing or irreversible** act, **access or
data only they have**, or a **genuine goal-changing decision**. Hit one → ask via `AskUserQuestion`
(recommended option first, enough context to answer without scrolling, batch multiple forks into one ask) and
**keep every other thread moving** while you wait.

These are **NOT** stopping points, each having caused a wasted turn:

| non-stopping point | what to do instead |
|---|---|
| An **approval** ("APPROVED", "go build (a)(b)(c)", "no further check-in needed") | Approval is a green light to **build**, not a checkpoint to report. Execute it. |
| **Finishing the one thing explicitly asked**, with approved/free steps queued behind it | Keep going. Finishing the prereg ≠ done if the harness and pilot it unlocks are free. |
| A **clean commit** / "natural review checkpoint" / "good place to update trimcrae" | Continue THIS turn until a real blocker or an empty backlog. |
| **"Which should I do first?"** when every option is self-doable | Choosing the order of self-doable work IS self-doable. Pick a sensible sequence and do them all. |
| Work that is **optional / additive / nice-to-have** | "It's extra" is not a reason to offer instead of act. |
| A **failure** you could chase | Chase the fix, don't report the failure. Try the next approach, don't ask which. |

**⛔ THE PHRASING TEST.** If you are about to write *"want me to X?" · "I can also X" · "should I also X?" ·
"say the word and I'll X" · "let me know if you'd like X" · "happy to X" · "I could X"* — and X is self-doable
— **the phrasing is the violation. Delete the offer and do X.** Ending a turn with a menu of things you could
have just done is the precise failure mode. A bare status report with nothing for trimcrae to decide is too.
When in doubt: do it and show it.


## 3 · When you genuinely must interrupt trimcrae

- **★★ RESERVE REVIEWER-AI REVIEW BLOCKS FOR (a) MAJOR PROGRAM-SHIFTING DECISIONS, (b) SIGNIFICANT (>$50) GPU
  SPEND, or (c) an OUTWARD-FACING/IRREVERSIBLE act** (emails, a release/DOI, publishing, submitting).
  **(trimcrae, 2026-07-12, correcting an earlier "every hand-off gets a block" after I over-escalated.)** That
  channel is expensive and interrupts him. A block is **NOT** for finished free work, curation you can verify,
  ordering self-doable work, "closing the loop", or cheap authorized runs — for those, **execute and report the
  result.** The default is DO, not ASK.
  When a trigger *does* apply, the block is the **first thing** in your reply: a self-contained, copyable, fenced
  box — the reviewer sees only what is inside it — containing (1) role + "approve, or return a specific list of
  fixes"; (2) project + goal, one paragraph; (3) what was done, with repo/PR/file paths; (4) the exact proposed
  next action(s) needing sign-off, verbatim; (5) known risks, uncertainties and judgment calls, stated honestly
  — over-claim vs verification level, medical integrity, ethics/tone; (6) your specific questions. Then apply
  the returned changes yourself and only then proceed.
  **This rule does NOT pause self-doable no-spend work** — produce the block only when the outward-facing step
  is actually imminent, and keep building meanwhile.
- **📱 PHONE-NOTIFY THE MOMENT A COPYABLE BLOCK IS READY (trimcrae, 2026-07-12).** trimcrae routes these to a
  separate reviewer AI and is often away, so fire the notification **in the same turn**. Explicit opt-in — this
  overrides PushNotification's default reticence. Belt-and-braces, because single channels silently miss:
  **always** `PushNotification` (`status: proactive`, one line <200 chars, no markdown), **and** unless there is
  genuinely nothing to decide, `AskUserQuestion` (the proven-reliable ping), recommended-first, referencing the
  block. Keep the block itself in the message text; the notification is only the alert. Skip only if trimcrae is
  clearly chatting right now. Never for routine progress.


## 4 · Evidence discipline

- **🔬 ALWAYS ROOT-CAUSE WITH A REAL DIAGNOSTIC — NEVER A "probably X" (trimcrae, 2026-07-14).** When anything
  fails, stalls, resets or returns a surprising value, **produce the evidence that proves the mechanism** before
  you explain, act or report. A plausible story is a HYPOTHESIS, not a diagnosis. **Method:** (1) state the
  competing hypotheses; (2) find the ONE observation that discriminates — pull the real log, inspect the real
  artifact (S3 sizes/mtimes/keys, `mode=forensic`/`ckpt`), read the real source, or **instrument the code and
  run a controlled reproduction** (engineering is free; a restart costing a few iterations is worth a definitive
  cause); (3) state the cause **with the evidence cited**. "I couldn't run it here" is never the stopping point
  — route the diagnostic through CI/AWS (§6). **If you catch yourself writing "probably / likely / must be / I
  think it's because" about a failure, STOP and go get the data.**
- **★★ A $0 OBSERVATION IS NEVER "WATCHING" — TAKE IT NOW (trimcrae, 2026-08-01: *"Is it expensive to
  investigate? Why wouldn't you just take a look now to be sure"*).** The instant something *might* be wrong,
  if the check costs nothing — a `git show` of a committed artifact, a public Actions API read, a census
  already on disk — **run it before you write the sentence about it.** There is no such state as "watching":
  either you looked, or you deferred a free answer and called the deferral a decision.
  **The measured cost of getting this wrong the same day it was written:** a lane's census was 16 min stale
  while its host billed. That was reported as "one tick past the line, watching" — and one public API call,
  costing nothing, showed the lane's watch loop had **exited 24 minutes earlier and never re-armed**, so the
  host had been billing unsupervised the whole time. **The "wait and see" framing was itself the error**; the
  observation that ended it was free and available the entire time.
  ⚠ This is the same shape as the two rules below and the reason they keep needing restating: a row that says
  UNKNOWN, STALE, "watching" or "will check next cycle" is an **unanswered question wearing the costume of a
  status**. §1's in-flight board makes that visible; this rule is what closes it. **Cheap to check ⇒ check
  now.** Reserve "later" for observations that genuinely cost money, a rental, or a human's time.
- **★ UNEXPECTED SLOWNESS IS A SIGNAL — INVESTIGATE, DON'T REASSURE (trimcrae, 2026-07-08, after I repeatedly
  reported "on track" while a job was stuck).** Materially slower than predicted, or one phase with no new
  output? That is evidence something is wrong. (1) Pull the live log and read the actual phase + last-event
  timestamp; (2) form a concrete hypothesis and verify it against the log, not against your prior estimate;
  (3) if stuck, **fix the root cause** — don't report status again. **Own your ETAs:** the *first* time reality
  diverges, dig. Don't make trimcrae be the one to notice.
- **★★ TIGHT MONITORING OF AN UNPROVEN PIPELINE (trimcrae, 2026-07-19, after it caught three silent failures on
  the ternary lane in one session).** A pipeline is **unproven** until you have watched it reach its **real
  success terminus at least once** — not "no error yet", not "it provisioned". While unproven, check every
  **~3–6 min**, and make every check a **PROGRESS check, not a liveness ping**: GPU actually busy, phase moved
  (setup→minimize→warmup→production), iteration count **up** since last time. Frozen phase + idle GPU across two
  consecutive checks = a **stall** → diagnose and fix. Every new stage is its own first-time risk. Once proven
  end-to-end, relax to a light heartbeat.
- **★★ AN ABSENT READING IS NOT A READING OF ABSENCE — AND A POPULATED FIELD IS NOT A MEASURED ONE (both did
  real damage on 2026-07-31, hours apart).** Two halves of one habit; the second is the dangerous one.
  **(a)** A census row saying `targets not in the record` / `no openmmtools rate line` means the collector could
  not READ that leg — **not** that the leg is frozen. A card floor was applied to a live lane on exactly that
  misreading, and reverted the same hour
  ([vast-placement-facts.md §3b](./research/compute/vast-placement-facts.md)).
  **(b)** ⚠ **A RECORD THAT LOOKS PLAUSIBLE IS MORE DANGEROUS THAN ONE THAT LOOKS EMPTY.** 17 smoke legs
  echoed `prod_ns: 5.0` and a filled `R1_interface` **from their ENV rather than from what ran**; a
  completeness count believed them, `panel_complete` went true — and the frozen gate **EMITTED a verdict on
  them**, carrying model-level E1 means for all three arms at `tier: INDETERMINATE`. It had to be withdrawn
  in full; no R1 result exists. ⚠ *Superseded, retained: "a frozen gate was ONE leg short of emitting a
  fabricated verdict." The board did read 17 of 18 at 10:54 AM ET — but the 18th landed sixteen minutes
  later and the verdict went out. Writing it as a near miss makes the guard sound like it held. It did not:
  what stopped this was a human reading the numbers.* An E1 near 1 Å on a smoke leg is 2 ps of sampling
  after ZERO equilibration, i.e. the minimised starting structure measured against itself
  ([STRATEGY.md Appendix A](./STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims)
  57; the predicate that closes it is `nrv04_retro_panel.production_leg_check`). **A field's PRESENCE is never
  evidence of its provenance** — check the thing only a real run can produce (wall time, frame count,
  equilibration), never the thing a default can fill in.


## 5 · Scope, spend and the research program

- **THE PLAN IS [nr4a3-program-map.md](./research/manuscripts/nr4a3-program-map.md)** — the gold-standard
  single source of truth for what's next, every step's GO/NO-GO gate, and every cost. It wins over any other
  doc, including this one. *(Superseded, retained: **"THE PLAN IS STRATEGY.md"** — true until 2026-08-02, when
  every live section was moved into the roadmap and STRATEGY.md became two history appendices.)* The schedule
  JSON [degrader-paper-schedule.json](./research/manuscripts/program/degrader-paper-schedule.json) is a machine mirror
  of the ordered plan; [pricing.md](./research/compute/pricing.md) owns the cost evidence. **Do not restate
  prices here** — this file carried a ladder total three times and it was stale every time. Superseded plan
  framings (atlas-anchor, Track A/B, the three-step spine, orientation-first) are in
  [STRATEGY.md → Appendix B](./STRATEGY.md#appendix-b--superseded-strategy-framings).
- **★ NORTH STAR (trimcrae, 2026-07-01; RESCOPED 2026-08-06):** the **state of the art of what in-silico can do
  to move the treatment science for EMC** — the most complete, rigorous, honest computational characterization
  achievable with **no wet lab**, every result at its true weight, **across the whole route portfolio**. Read
  [IDEAS.md](./research/IDEAS.md) and
  [emc-treatment-strategy.md](./research/manuscripts/program/emc-treatment-strategy.md) before resuming any
  treatment-research work so you don't re-litigate settled calls.
  - **⛔ THE DEGRADER IS NOT THE NORTH STAR AND GETS NO SPECIAL TREATMENT (trimcrae, 2026-08-06: *"We went down
    that path and ran into enough blockers that it no longer has special treatment."*).** ⚠ *Superseded,
    retained: "what in-silico can do for an **NR4A3-selective degrader**", and "The program is **≈70–80% of repo
    effort**; the broader EMC route portfolio … is **support beneath it**"* —
    [STRATEGY.md → Appendix B](./STRATEGY.md#appendix-b--superseded-strategy-framings). **This demotes a
    STANDING, not a RESULT:** nothing measured is withdrawn, and that route's limits are the best-characterised
    on the board precisely because of the effort. What ends is its claim on the front of the plan — it is one
    route of forty, ranked on the same axes as the rest, and **no strategy family holds `portfolio_role: lead`
    at all**, which is an honest state and not a slot to fill.
  - **★★ EVERY ROUTE'S END GOAL IS A PAPER (trimcrae, 2026-08-06).** No wet lab, no clinic — so the published
    record is the *only* channel by which any of this reaches a patient. A route that cannot name the paper it
    is for is an **activity, not an option**. The paper need not be written; the endpoint, the one sentence it
    would put into the field's record, and an honest statement of what is missing must all exist. One home for
    the mapping, generated and CI-checked:
    [`systems/views/L3-publications.md`](./systems/views/L3-publications.md) — **do not restate the endpoint
    list here.** ⛔ **A closed route is not exempt**: a definitional closure is a publishable negative, and the
    field publishes almost none of them.
    ⚠ **THIS IS A TEST, NOT A WORK QUEUE — READ [§0](#0--what-to-work-on--live-paths-first)
    WITH IT (trimcrae, 2026-08-06).** "Name the paper" exists to catch a route that is an activity rather than
    an option. It has never meant that writing papers is the work, and a session that reads it that way ends
    up documenting dead routes while live ones sit one free step from a result. **Negatives wait behind
    anything live.**
- **★★ "STATE OF THE ART" = BREADTH-FIRST, STANDARD-DEPTH (trimcrae, 2026-07-05 — codified to stop it drifting
  into "spend $1000s for a marginal CI").** Apply before every GPU spend:
  - **A new TECHNIQUE that adds a new axis of evidence** (structure predictor, pose/complex method,
    ternary-geometry tool, ML potential, selectivity model) → **default YES**. Watch list:
    [method-watch.md](./research/method-watch.md).
  - **Deepening a test past its field standard** (more sampling, extra force fields, more replicates, tighter
    CIs) → **default NO**, unless the standard-rigor result is genuinely ambiguous *and* that ambiguity is
    decision-relevant. "More rigorous" is not a reason.
  - **Run each test to its field standard, then STOP.** (ABFE standard: converged fwd/rev + ~3 independent
    replicates + honest **replicate-SD, not MBAR-SE** error bars.)
  - Scope the standard per test **up front**. The anti-pattern that triggered this was rigor added reactively,
    one layer at a time under prodding (HREX → replicates → conformers → 2nd force field).
- **★ ENGINEERING EFFORT IS FREE — only real compute $ is a cost (trimcrae, 2026-07-08).** This runs on a flat-rate
  subscription, so agent time (writing code, refactoring, adding checkpoint/resume, more tests) costs **nothing**
  and must never be weighed against a saving. The only "cost" in any trade-off is **actual GPU dollars**. So:
  "not worth the engineering effort to save $X" is **never** valid; default every job to the cheapest real-dollar
  path and write whatever code makes that safe; prefer more tests and cleaner resumability. The breadth-vs-depth
  guardrail above is about **compute** dollars, not effort.
- **OPERATING REGIME — one researcher, no wet lab, no race.** A self-funded wet-lab program is **off the table**
  (a funded collaborator's budget, never a next step), so every "next step" is either publish-to-convince or
  in-silico. **GPU spend is not a gate on paper quality**: run the warranted experiments — including expensive
  ones — to strengthen or honestly refute the claims, and post only once that work is folded in. Cost is a reason
  to sequence and right-size, not to skip a decision-relevant run.
  **ONE FILE PER DELIVERABLE**, the manuscript/SI file map, the retired preprint stubs and the pre-post
  checklist are in **`repo-gates`** — load it before editing a manuscript or taking an outward-facing step.
  **This is long-lived on a rising frontier, not a one-shot:** parked items are "revisit when capability X lands",
  not dead, and completed work is worth re-grading as methods improve ([method-watch.md](./research/method-watch.md)).
  Guardrail: a coming capability justifies waiting or re-running, **never** claiming a result before the method
  supports it.


## 6 · Running compute, committing, and reporting — THE TRIPWIRES

**Each row below is a thought you will actually have. When you have it, load the skill BEFORE acting — not
after.** The skills carry the rules verbatim, with their attributions, dates and incident evidence intact.

| ⛔ THE MOMENT YOU THINK / ARE ABOUT TO … | LOAD |
|---|---|
| *"I can't run X here"* · *"no GPU / no network / no pip / can't test locally"* · *"this route is blocked"* · a **403 at the egress proxy** · you are about to call anything **deferred** or **blocked** | **`ci-escape-hatches`** |
| dispatch a workflow · run a branch's CI without merging · time a CI step · supervise a billing fleet · set up a self-wake poller · see a GitHub auth or signature warning | **`ci-escape-hatches`** |
| **rent, relaunch or refuse a host** · launch a fleet or fan-out · pick a provider · write a job that checkpoints · diagnose a Vast/GCP provisioning, quota, capacity or teardown problem · install anything on a machine we are paying for | **`gpu-compute`** |
| your final message will **leave real compute running** · you are about to print a `$/ns`, a cost row or a drift flag | **`inflight-reporting`** |
| **commit or push** · run preflight · a gate goes red · edit a manuscript or SI · touch `systems/` or the registry · take any **outward-facing** step (preprint, submission, release, DOI) | **`repo-gates`** |

**The four rules that must fire even if you never load a skill** — kept here because each guards against
doing an irreversible or expensive thing *before* you would think to consult anything:

- **⛔ NEVER BUILD AN ENVIRONMENT ON A MACHINE WE ARE PAYING FOR. THE STACKS ARE PRE-BAKED — PULL, DON'T
  SOLVE (trimcrae, 2026-07-25; scope corrected 2026-08-01).** A new lane's first question is **"which baked
  image?"**, never "what do I install?". Full rule, the five images and the measured parity: **`gpu-compute`**.
- **⛔ A ROW THAT PRINTS `⚠ DRIFT` IS A ROW WE DO NOT BUY.** The drift line **is** the buy line — a hard
  gate, not a label — and **every** rental of a new host is gated, resume and cold single unit included.
  The rate, its basis and why a refusal must name which ceiling it hit: **`inflight-reporting`**.
- **⛔ CHECKPOINT AFTER EACH UNIT AND UPLOAD AS YOU WRITE (`s3_upload_mode="Continuous"`), AND DEFAULT EVERY
  GPU RUN TO SPOT** — the two go together; spot is only safe *because* of the checkpointing. Details:
  **`gpu-compute`**.
- **⛔ BEFORE COMMITTING, `./scripts/preflight.sh` MUST PASS**, and its exit code cannot be masked. Before
  anything outward-facing it is **`PREFLIGHT_FULL=1 ./scripts/preflight.sh`** — scoping is not a claim that
  the rest of the suite passes. The nine gates and what each catches: **`repo-gates`**.

## 7 · Repo basics — what stays resident

- **Golden rule: never fabricate medical facts, stats, citations or patient data.** Everything clinical must be
  cited. Non-real registry data must be flagged `SAMPLE_SYNTHETIC` and bannered — AGENTS.md → "medical integrity".
  ⚠ **A HEDGED SENTENCE ON A FABRICATED PMID PASSES `lint_claims` — IT HAPPENED, TWICE IN ONE PASS
  (2026-08-07)**, and six invented titles and author-lists went out with it. Claim STRENGTH is orthogonal to
  citation PROVENANCE. Never write an identifier from recollection. Gate 4 and its ledger: **`repo-gates`**.
- **★★ KEEP EVERYTHING SYNCED TO `main`, AND KEEP `main` CURRENT — BRANCH DRIFT IS A DATA-LOSS BUG
  (trimcrae, 2026-07-29, after it cost a day).** Merge to `main` early and often; rebase before every push;
  **never let a branch a workflow runs from be the only home of an artifact.** ⛔ **Before writing ANY claim
  from a committed artifact, check which ref the producing workflow actually writes to — `main` is not
  automatically it.** The measured incident (`main` said 1 of 19 edges / $22.62 while the branch said 14 of
  19 / $68.98), the three harms and the port-then-switch rule: **`repo-gates`**.
- **⛔ THE PATIENT-FACING SITE IS RETIRED AND DELETED (2026-08-05), NOT SHELVED. DO NOT RECREATE IT.** The
  HTML, assets, templates, the `add-cancer` skill and the Pages workflow are gone. Two things survived
  because they were never site tooling: the cited EMC clinical registry
  ([`research/data/emc-clinical-registry.json`](./research/data/emc-clinical-registry.json)) and its
  validator. Full accounting and the "what part of a feature is not a file" lesson: **`repo-gates`** and
  [`systems/MIGRATION.md`](./systems/MIGRATION.md).
- **★★ THE ARCHITECTURE IS [`systems/`](./systems/)** — `systems/graph/*.json` is the source of truth for
  every strategy family, route, blocker and forecast; everything under `systems/views/` is **GENERATED** and
  a hand-edit fails the build. One screen of landscape:
  [`systems/views/L0-ecosystem.md`](./systems/views/L0-ecosystem.md). Regeneration, conventions and the rest:
  **`repo-gates`**.
- **Citing & combining studies** uses a structured citation map and a fixed pooling method — read
  **[systems/POLICY-evidence.md](./systems/POLICY-evidence.md)** before touching `registry`.
