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
short by construction: no cost figures, no rung-by-rung ladder, no history. Those live in the roadmap, and
anything here that restates them is a bug — see rule 1.

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
  exists): [`lint_consistency.py`](./research/manuscripts/lint_consistency.py) runs in CI over the roadmap,
  this file, pricing.md, bid-strategy.md, the schedule JSON, the paper, the SI and the NR-V04 prereg. Run it
  before committing doc changes: `python3 research/manuscripts/lint_consistency.py`. It clears correctly-written
  retractions, so **a red build is a real inconsistency — fix the doc, don't loosen the pattern.**
- **⏰ TIMES: ALWAYS US EASTERN, 12-HOUR AM/PM. NEVER UTC, NEVER 24-HOUR.** Every time you report — ETAs, job
  timestamps, "as of", cadences — must be ET (EDT = UTC−4) in 12-hour form ("1:00 PM ET", not "13:00"). Convert
  before writing even if the tool emits UTC. *(You keep slipping. This is why it is near the top.)*
- **⏱️ END-OF-TURN "IN FLIGHT" BOARD (trimcrae, 2026-07-11).** Whenever your final message leaves work running,
  the LAST thing in it is a compact **"In flight:"** board — one scannable line per item (bullet/table, not
  prose): **what it is · current state · ETA in ET 12-hour · cost · $/ns** (or an explicit "ETA unknown — why"),
  plus what you'll do when it lands if non-obvious. **List ONLY real compute** (GPU/CI jobs, subagents doing real work).
  Do **NOT** list your own wake mechanisms (self-timers, pollers, heartbeats) or **scheduled routines** — a
  schedule is not running compute. Nothing running → "Nothing in flight", one line. This REPLACES long status
  narration.
  - **COST IS PART OF THE FORMAT, NOT AN EXTRA (trimcrae, 2026-07-26 — asked for it twice in one session).**
    Every in-flight row carries what it costs, on the same line as its ETA: the ladder figure for a priced rung,
    a stated estimate with its range for anything unpriced, `$0` for CI/analysis, and free credit named as such
    (**GCP trial credit is a SEPARATE LEDGER — never summed into realized or ladder spend**). An ETA without a
    cost is an incomplete row. Per rule 1 the figure is not typed fresh here: it POINTS at
    [`vast-ladder-repricing.json`](./research/modalities/vast-ladder-repricing.json) /
    [pricing.md](./research/compute/pricing.md), and only a genuinely-unpriced item carries an estimate — which
    then says it is one.
  - **AND `$/ns`, AGAINST ITS BASIS, ON EVERY GPU ROW (trimcrae, 2026-07-26: *"so that's easier to catch in the
    future if it drifts"*).** `$/hr` cannot show drift — a cheap slow card and an expensive fast one look the
    same — so every row on a GPU carries **`$/ns` and the multiple of the ladder basis** it represents, e.g.
    `$0.0077/ns · 1.8× basis`. **The multiple is the point**; a bare `$/ns` is a number nobody can grade at 3 AM.
    Basis = the `$/ref-GPU-h` planning rate in [pricing.md](./research/compute/pricing.md) ÷ the reference card's
    ns/h, and per rule 1 it is DERIVED from the validated card ratios there, never typed fresh — a row quoting a
    ratio the cost model does not produce is the bug. **The drift line is an ABSOLUTE rate — `$0.006539/ns`,
    which is ≈1.92× the current basis — and a row at or above it is drift and says so**; that is what the
    fleet-launch gate in §6 refuses to buy into. Rows with no GPU (CI, analysis, subagents) carry `—`
    rather than a fabricated figure.
    - **★★ THE LINE IS AN ABSOLUTE `$/ns`, NOT A MULTIPLE — `$0.006539/ns` ≈ **1.92× basis** (trimcrae,
      2026-07-27, re-expression ruling).** ⚠ **≈1.92× IS NOT A LOOSENING OF THE 1.5× STATED EARLIER THE SAME
      DAY. IT IS THE SAME DOLLARS PER NANOSECOND.** The throughput table was re-anchored that afternoon; the
      ladder basis fell 22 % (from a now-**superseded** `$0.004359/ns` to `$0.003412/ns`) because the reference card's measured throughput
      rose and the widened table admitted 97 more gradeable offers — **no price moved, the yardstick did.**
      `1.5 ×` the superseded `$0.004359` and `1.92 × $0.003412` are both `$0.006539/ns`. Pinning the rule to a multiple of a
      correctable denominator silently turned it into a much stricter rule than the one agreed (every board
      that day failed a line it had been passing), so the **invariant is now the absolute rate** and the
      multiple is DERIVED from it — [`inflight_usd_per_ns.APPROVED_USD_PER_NS`](./research/modalities/inflight_usd_per_ns.py)
      and `drift_multiple()`. A future basis change re-derives the multiple instead of breaking the rule.
      **The flag and the refusal must remain the same number** — if the buy line moved and the ⚠ DRIFT
      threshold did not, rows would print drift and still be bought, which is the very complaint below.
      [`tests/test_buy_line_invariant.py`](./research/modalities/tests/test_buy_line_invariant.py) fails if
      they ever diverge. Superseded, retained: the **1.5×** expression and the **$0.004359/ns** basis.
    - **★★ THE DRIFT LINE **IS** THE BUY LINE — A HARD GATE, NOT JUST A LABEL (trimcrae, 2026-07-27,
      ruling on the step 1 fan-out's per-unit ceiling after being shown the derived alternative).** Reason, in
      his words from earlier the same day: ***"What's the point of tracking that if we don't act on it?"***
      So **a row that prints `⚠ DRIFT` is a row we do not buy** — the flag and the refusal are the same
      number, and the gap between "we noticed" and "we declined" is closed. A rental must clear **BOTH** its
      rung's derived **dollar** ceiling (*is this inside the money that was authorised*) **and** the
      **rate** line above (*is this a rate we will pay at all*); the effective ceiling is the lower, and a refusal
      must NAME which one it hit — conflating them is what made an earlier round of hold readouts unreadable.
      **SUPERSEDED, retained for the record:** until this ruling 1.5× was *reporting only* — the framing "not
      a hard gate — the fleet-launch gate in the launcher is that" (`inflight_usd_per_ns.py`) — under which
      the fan-out's hard gate was its derived band top alone, ≈2.25× basis. That framing no longer stands and
      must not be quoted. Live rule and arithmetic:
      [`congeneric_fanout.unit_ceiling_components`](./research/modalities/congeneric_fanout.py).
    - **★★ A ROW WE ARE PAYING AND A ROW THE GATE REFUSED MUST NEVER RENDER ALIKE (trimcrae, 2026-07-27:
      *"the `$/ns` column still shows several rows over 1.5×. Why? Are we not stopping those runs?"*).** Held
      lanes at 3.25× and 1.96× printed the same `⚠` as legs actually being billed at 1.51× and 1.82×, so a
      guard doing its job read as a guard being ignored. **`⚠ PAYING OVER THE …× LINE` = money going out;
      `⛔ REFUSED at … — $0 spent` = the multiple is what we DECLINED.** One glyph, one meaning.
      Rendered by [`inflight_usd_per_ns.py`](./research/modalities/inflight_usd_per_ns.py) — **never typed, and
      never off a launcher's `dph≈` line**, which is the market floor plus the search's disk line and so reads
      LOW against the rate the instance is actually billed (`vast_rate_forensics.py`).
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
  completeness count believed them, `panel_complete` went true, and a frozen gate was ONE leg short of emitting
  a fabricated verdict ([STRATEGY.md Appendix A](./STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims)
  57; the predicate that closes it is `nrv04_retro_panel.production_leg_check`). **A field's PRESENCE is never
  evidence of its provenance** — check the thing only a real run can produce (wall time, frame count,
  equilibration), never the thing a default can fill in.

## 5 · Scope, spend and the research program

- **THE PLAN IS [nr4a3-program-map.md](./research/manuscripts/nr4a3-program-map.md)** — the gold-standard
  single source of truth for what's next, every step's GO/NO-GO gate, and every cost. It wins over any other
  doc, including this one. *(Superseded, retained: **"THE PLAN IS STRATEGY.md"** — true until 2026-08-02, when
  every live section was moved into the roadmap and STRATEGY.md became two history appendices.)* The schedule
  JSON [degrader-paper-schedule.json](./research/manuscripts/degrader-paper-schedule.json) is a machine mirror
  of the ordered plan; [pricing.md](./research/compute/pricing.md) owns the cost evidence. **Do not restate
  prices here** — this file carried a ladder total three times and it was stale every time. Superseded plan
  framings (atlas-anchor, Track A/B, the three-step spine, orientation-first) are in
  [STRATEGY.md → Appendix B](./STRATEGY.md#appendix-b--superseded-strategy-framings).
- **★ NORTH STAR (trimcrae, 2026-07-01):** the **state of the art of what in-silico can do for an NR4A3-selective
  degrader** — the most complete, rigorous, honest computational characterization achievable with **no wet lab**,
  every result at its true weight. The paper documents *that*, not a ship-when-adequate minimum. The program is
  ≈70–80% of repo effort; the broader EMC route portfolio ([IDEAS.md](./research/IDEAS.md),
  [emc-treatment-strategy.md](./research/manuscripts/emc-treatment-strategy.md)) is support beneath it — read
  those before resuming any treatment-research work so you don't re-litigate settled calls.
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
  **SINGLE DELIVERABLE:** [nr4a3-degrader-paper.md](./research/manuscripts/nr4a3-degrader-paper.md) + its SI
  **is** both the ChemRxiv preprint and the JCIM submission. `nr4a3-degrader-preprint*.md` are retired stubs — a
  parallel condensed draft drifted out of sync and self-contradicted; **don't recreate one.** Pre-post checklist:
  [preprint-plan.md](./research/manuscripts/nr4a3-degrader-preprint-plan.md); ready-to-send outreach:
  [outreach-emails.md](./research/manuscripts/nr4a3-degrader-outreach-emails.md).
  **This is long-lived on a rising frontier, not a one-shot:** parked items are "revisit when capability X lands",
  not dead, and completed work is worth re-grading as methods improve ([method-watch.md](./research/method-watch.md)).
  Guardrail: a coming capability justifies waiting or re-running, **never** claiming a result before the method
  supports it.

## 6 · Running compute

### The sandbox is not your execution limit

- **★★ "I can't run X here" is NEVER a reason to defer (trimcrae, 2026-07-12, after I repeatedly declared work
  undoable while holding two standing escape hatches).** No GPU, no MD stack, no compiler, no network to a host,
  a **403 at the egress proxy** (NCBI/GEO, PMC, EuropePMC, UniProt, Springer all block CONNECT) — none of these
  is a dead end. Route it out:
  1. **Networked / data / light-CPU / PDF / scraping / needs pip** → a **GitHub Actions runner** (free,
     unrestricted internet, `pip`/`apt` allowed). Write it **pure-stdlib** where you can, add a
     `workflow_dispatch` (`permissions: contents: write`) that commits outputs back to the triggering branch,
     dispatch it, then poll with a background poller. Exemplars: `atlas-data.yml` + `expression_reprocess.py` +
     `fulltext_verify.py` (GEO/PMC); `fusion-cpu-extras.yml` (→ `modalities-cache` branch).
  2. **GPU / MD / FEP / heavy compute** → a spot GPU job. Validate-first: `mode=smoke` → one real leg → fleet.
  3. **"I can't TEST it here"** → that is what the smoke / single-shard shakeout is for. Untestable-in-sandbox
     ≠ untestable. Writing hundreds of lines you can't exercise locally is **fine**; you exercise them out there.
  Reserve "deferred" for a **real** external dependency (a spend past the review gate, data only trimcrae has, a
  capability that does not exist yet) — never because the dev sandbox lacks a tool.
- **RUN A FEATURE BRANCH'S CI WITHOUT MERGING — dispatch an ON-main `workflow_dispatch` with `ref=<branch>`**
  (verified 2026-07-11). A *new* workflow file on a feature branch 404s (dispatch requires it on the default
  branch), but an **already-on-main** workflow dispatched with `ref=<branch>` runs **that branch's version of the
  file and its code**. So: edit an existing on-main workflow on your branch (or pass `git_ref=<branch>` to a job
  that clones), then dispatch with `ref=<branch>`. No merge to main required.
- **⏱ TIME A CI STEP FROM ITS *COMPLETED RECORD*, NEVER FROM A LIVE POLL (measured 2026-07-27, two misreads
  in one day).** The jobs API **lags**: it reported a finished 3-minute step as `in_progress` for ~18 minutes,
  and a finished 4.0-minute run as `in_progress` for ~50 minutes. Polling it while a run is live therefore
  manufactures a stall that is not there — and §4 says unexpected slowness must be investigated, so a fake one
  burns a real diagnostic. Read `started_at`/`completed_at` **after** the step completes. (The measured
  per-submit figure this rule came from has its one home in `congeneric_fanout_vast.mode_launch`, next to the
  per-rental ledger save it justifies — do not re-type it here.)
- **★★ A `schedule:` CRON DOES NOT SUPERVISE A BILLING FLEET — AN AGENT HAS BEEN DOING IT BY HAND (measured
  2026-07-27).** State this plainly to trimcrae rather than letting "there's a cron for it" stand: on the day
  it was measured, **25 of the last 30** step-1 autoscale runs were `workflow_dispatch`, not `schedule`. GitHub
  throttles this repo's schedules to a small fraction of what the cron asks for, so the automation is **not
  self-sustaining** — the gap between scheduled ticks has in practice been covered by an agent remembering to
  dispatch, and when the agent stopped, supervision stopped and nothing said so. Consequences, all binding:
  **(1)** never plan a fleet's safety around a cron interval, and never reassure from one; **(2)** a
  `*/N`-minute cron comment is a REQUEST, not a cadence — the delivered gaps are MEASURED and printed by
  [`fleet-supervision-alarm.yml`](.github/workflows/fleet-supervision-alarm.yml), which is their one home
  (per rule 1, do not re-type a remembered figure into a workflow comment — that is exactly how a stale
  "~55-65 min" survived into two files and made a normal silence look like an outage); **(3)** while any fleet
  is billing, **you** are the supervisor — dispatch the tick yourself on the cadence the work needs.
- **Self-wake = a BACKGROUND-BASH POLLER, not cron** (verified 2026-06-30; a sibling session ran 48 h this way).
  Launch the loop with `run_in_background: true`; its exit delivers a `<task-notification>` that re-invokes you —
  that completion *is* the wake-up, with no user message. Poll the public Actions API (no auth for a public repo,
  ~60 req/h so `sleep 70`) and exit early:
  ```
  for i in $(seq 1 60); do
    s=$(curl -s "https://api.github.com/repos/trimcrae/Rare-cancers/actions/runs/<RUN_ID>" \
        | python3 -c "import sys,json;print(json.load(sys.stdin).get('status'))")
    [ "$s" = completed ] && { echo DONE; break; }; sleep 70
  done
  ```
  On wake: read the output, act, launch a FRESH poller on the next run id. Restart-resilient — all state is in
  the repo/S3. Get a new run id via `curl .../actions/workflows/<wf>.yml/runs?per_page=1`. **`CronCreate` is NOT
  reliable** (vanished twice within ~25 min even with `durable:true`); **`ScheduleWakeup` did not fire** outside
  `/loop` dynamic mode.

### Environments — CI *and* every rented host

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
  **★ PARITY IS THE SCIENTIFIC ARGUMENT, NOT JUST SPEED:** `Dockerfile.ternaryfep` is byte-for-byte the spec
  `gpu-ternary-fep-gcp.yml` builds, and **analysing an OpenFE trajectory with a different pymbar/openmmtools than
  PRODUCED it can change the MBAR numbers.** An ad-hoc `micromamba create` in an analysis step is a silent
  protocol deviation. Dep genuinely missing → add it to the `Dockerfile.*` and **re-bake once**. Only if you truly
  cannot re-bake, use `setup-micromamba` **with `cache-environment: true`**. *(Cost of learning this: ~20 min of
  solve per run, three runs in a row, while the image already carried every package.)*

### Long runs, checkpointing and spend shape

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

### Provider facts

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

### Environment noise to ignore

- **GITHUB AUTH "EXPIRED" IS A FALSE ALARM — retry, never escalate (2026-07-09).** On any `mcp__github__*`
  "requires re-authorization / token expired", assume **you** are wrong: it refreshes itself. Retry the same
  call; if it still fails, wait (`run_in_background` sleep 60–120 s, foreground short sleeps are blocked) and
  loop several times over a few minutes. Do not tell trimcrae the connection is down, do not halt, do not ask
  them to reconnect. Only consider surfacing after many spaced retries across tens of minutes.
- **COMMIT-SIGNATURE / "Unverified" WARNINGS ARE FINE TO IGNORE (2026-07-10).** The repo is configured for SSH
  commit signing but the private key is not mounted, so commits land unsigned. The committer identity is already
  correct, so the hook's suggested `--amend --reset-author` / `rebase --exec` fixes change nothing, and
  force-rewriting shared history for a signature you cannot generate is strictly harmful. **Commit normally and
  move on.**

## 7 · Repo basics

- **★★ KEEP EVERYTHING SYNCED TO `main`, AND KEEP `main` CURRENT — BRANCH DRIFT IS A DATA-LOSS BUG, NOT AN
  INCONVENIENCE (trimcrae, 2026-07-29, after it cost a day).** Long-lived feature branches that a *workflow*
  runs from are the dangerous kind, because they hold **state as well as code**. Measured that morning:
  `step1-fanout-autoscale.yml` checks out `fleet_branch` (default `claude/max-effort-2dq11l`) and writes its
  map there, so `main` said the fan-out was **1 of 19 edges, $22.62** while the branch — where the lane really
  runs — said **14 of 19, $68.98, 197 rentals**. Three separate harms, all real:
  1. **The paper was wrong.** §2.9 was written off `main`'s artifact and understated the work by 13 computed
     ΔΔG edges. An artifact on the wrong branch is a stale fact that reads as a current one.
  2. **Fixes landed where nothing runs.** The exclusion-set repair (union 58 → 27), `leg_failure_breaker` and
     `teardown_decision` all went to `main`, which that lane does not check out — so they were inert.
  3. **Re-pointing the lane became expensive.** Flipping `fleet_branch` to `main` would have shown 13 finished
     edges as unrun and **re-bought them** (~$46) on a lane that rents unattended.
  So: **merge to `main` early and often; rebase working branches onto `main` before every push; never let a
  branch a workflow runs from be the only home of an artifact.** Before writing ANY claim from a committed
  artifact, check which ref the producing workflow actually writes to — `main` is not automatically it. If a
  lane must run off a branch, that branch's artifacts belong on `main` too, and reconciling them is
  **port-then-switch, never switch-then-discover**.
- **Golden rule: never fabricate medical facts, stats, citations or patient data.** Everything clinical must be
  cited. Non-real registry data must be flagged `SAMPLE_SYNTHETIC` and bannered — AGENTS.md → "medical integrity".
- **Citing & combining studies:** registry data uses a structured citation map (`registry.citations` +
  `sourceId`/`primaryRef`, primary vs secondary) and a fixed pooling method (crude denominator-weighted
  proportions + Wilson 95% CIs, non-overlapping cohorts only). Read **[METHODOLOGY.md](./METHODOLOGY.md)** before
  touching `registry`.
- **To add a cancer:** `node scripts/new-cancer.mjs <slug> "Name" "ABBR" "Category"`, then fill
  `data/cancers/<slug>.json` (the EMC file is the worked example). **A cancer page = one JSON file** — you rarely
  touch HTML/CSS/JS.
- **Before committing:** `node scripts/validate.mjs` must pass.
- **No dependencies, no build step.** Keep it that way. **Deploy:** GitHub Pages (`.github/workflows/pages.yml`)
  on push to `main`; keep all URLs relative.
- **The patient-facing site is shelved** — keep it working if you touch it, but don't invest new effort there
  without being asked.
