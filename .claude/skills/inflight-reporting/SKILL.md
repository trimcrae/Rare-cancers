---
name: inflight-reporting
description: The exact format of the end-of-turn "In flight" board, and the $/ns drift line that doubles as the buy line. Load whenever your final message will leave real compute running (GPU or CI jobs, subagents doing real work), when you need to decide whether a row gets a $/ns column at all, or when you are about to rent, relaunch or refuse a host on price. Covers: one scannable line per item with state, ET ETA, cost and $/ns against its basis; cost is part of the format, not an extra; the absolute buy line $0.006539/ns (approximately 1.92x basis) and why it is an absolute rate rather than a multiple; the drift line IS the buy line, a hard gate; and why a row we are paying and a row the gate refused must never render alike.
---

# The end-of-turn in-flight board

Extracted from CLAUDE.md §1 on 2026-08-15, **verbatim**. CLAUDE.md keeps the tripwire (a board
is required at all); this file keeps the format and the buy-line arithmetic.

⚠ **This file is a `pinned-figures.json` target** — it carries `$0.006539/ns`, the superseded
`$0.004359/ns` basis and the current `$0.003412/ns`, all of which `lint_consistency.py` checks.

- **⏱️ END-OF-TURN "IN FLIGHT" BOARD (trimcrae, 2026-07-11).** Whenever your final message leaves work running,
  the LAST thing in it is a compact **"In flight:"** board — one scannable line per item (bullet/table, not
  prose): **what it is · current state · ETA in ET 12-hour · cost · $/ns** (or an explicit "ETA unknown — why"),
  plus what you'll do when it lands if non-obvious. **List ONLY real compute** (GPU/CI jobs, subagents doing real work).
  Do **NOT** list your own wake mechanisms (self-timers, pollers, heartbeats) or **scheduled routines** — a
  schedule is not running compute. Nothing running → "Nothing in flight", one line. This REPLACES long status
  narration.
  - **⛔⛔ EVERY ROW MUST NAME WHAT WILL BRING THE SESSION BACK FOR IT, AND A ROW THAT CANNOT IS NOT
    IN FLIGHT — IT IS ABANDONED** (trimcrae, 2026-08-27: *"you said something was in flight 2 hours ago
    and it looks like it just stalled after that"*). ⚠ **Measured that day, and the board was the only
    thing that looked healthy.** A cycle ended its turn with `In flight: CI tests on 8b22933, adda6f6,
    0743ac1`. All three went green; the session never came back, because **the harness wakes a session
    when a backgrounded command exits or a subagent lands, and it does not know GitHub Actions
    exists.** So the board named three things the session had no mechanism to follow up on, and sat
    idle for two hours until a human asked.
    ★ **THE TEST IS CLAUDE.md §1's, POINTED AT THE REPORT INSTEAD OF THE SHELL:** *after this turn, is
    there anything that will bring the session back for this row?* A backgrounded command → yes, its
    exit is the wake. A subagent → yes. **A CI run, a GitHub workflow, a remote job → NO, not by
    itself.** Arm the wake in the same turn:

        python3 research/autonomy/await_ci.py --sha $(git rev-parse HEAD) > ci.log 2>&1; echo "EXIT=$?" >> ci.log

    run with the tool's own `run_in_background`, so its exit IS the wake. It returns **0 green, 1 red,
    2 UNKNOWN** — and never reads an empty run list as green, because a push that has not registered
    yet would otherwise pass.
    ⛔ **The waiter itself never appears ON the board** — §1 already forbids listing your own pollers.
    It is what makes the CI row honest, not a row of its own.
    ⚠ **And if you genuinely will not follow a thing up, say that instead of listing it.** "CI is
    running; I am not waiting on it" is honest and costs nothing. A row that implies a return you have
    not arranged is the failure this rule exists to stop.

  - **⛔⛔ "NOTHING IN FLIGHT" IS NOT A STOPPING CONDITION, AND A TURN THAT ENDS ON IT MUST ALSO SAY
    WHAT CONTINUES THE WORK** (trimcrae, 2026-08-27: *"What's the mechanism that lets you say 'in
    flight: nothing running' and end a turn? We want this to continue autonomously so we should fix
    that."*). ⚠ **The hole is structural, not a slip.** This board reports RUNNING COMPUTE, and §1
    above forbids listing wake mechanisms or scheduled Routines on it — so *"Nothing in flight"* is a
    true statement about GPUs and CI that says **nothing about whether the work resumes.** A session
    can hold three pieces of unfinished work, report it, end, and be compliant with every rule here
    while the work dies with the turn.
    ⚠ *Measured that day: PUB-ASO's publish bar read 4/7 and **not one** of the three open clauses was
    a ledger item. They existed only as sentences in a reply. A fresh cycle re-scores the LEDGER, so
    the whole "next I'll close these" plan was one session-death from being lost — while the loop kept
    looking healthy: cycles firing, receipts landing, and the only paper with a public DOI parked.*
    ★ **THE RULE: before a turn ends, every piece of work you are holding is a QUEUED LEDGER ITEM, or
    it does not exist.** A reply is not a queue and a context window is not a durable medium. Check it
    rather than remember it:

        python3 research/autonomy/continuity.py --check

    It exits 1 when a clause is blocking a paper and nothing queued closes it, and it matches on a
    declared `closes_clause` field rather than on prose — the first version grepped the item text and
    reported three filed items as missing, because they said "clause 2" where the clause is named
    `preflight_full_green`.
    ⛔⛔ **AND THE SCHEDULED ROUTINE IS A BACKSTOP AGAINST STALENESS, NEVER A REASON TO STOP**
    (trimcrae, 2026-08-27, correcting the first version of this very clause: *"why do we need to wait
    for the driver routine? That's more of a backup to make sure things never get stale, not a reason
    to intentionally stall."*). ⚠ **The first draft of this rule offered *"N items queued, the driver
    Routine takes them"* as an honest ending — which quietly licensed a four-hour wait for work that
    was free, ready and in hand.** Naming a future scheduler is not continuation; it is a deferral
    with a citation.
    ★ **THE ORDER IS: DO IT NOW, HAND IT OFF IF IT WILL NOT FIT, AND ONLY THEN LET THE SCHEDULE CATCH
    IT.** CLAUDE.md §2 — warranted, cheap and ready means DO IT NOW, and "a cycle will pick it up" is
    the same offer-instead-of-act the phrasing test forbids. The queue exists so that work is not LOST
    when a session genuinely ends; it does not exist to schedule work a session could finish.
    ⛔ So the honest ending, when nothing is running, names **why nothing is running**: the backlog is
    empty, or every remaining item genuinely cannot proceed in this session (needs a spawn, a human
    act, or an external result) — and it says which. *"Nothing in flight"* with free, ready work in
    hand is the failure this rule exists to stop, whether or not a Routine would eventually get to it.

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
    ⚠ **THE DASH IS FOR A MIXED BOARD. WITH NO GPU ROW AT ALL, THE COLUMN GOES TOO (trimcrae,
    2026-08-14: *"Why are you reporting `$/ns` on something that has nothing to do with that?"*).** A
    `—` earns its place next to a row that IS being billed. A board whose every row is CI or analysis
    has nothing to compare, so it carries **no `$/ns` column** — a drift guard printed where no drift
    can occur is one the eye learns to skip, which costs the guard exactly where it matters. And a
    single $0 row is a **line, not a table**: §1 asks for one scannable line per item, bullet *or*
    table. *Superseded, retained: the reading under which every board rendered the column.*
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
