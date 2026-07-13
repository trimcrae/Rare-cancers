# CLAUDE.md

This project's full maintenance guide lives in **[AGENTS.md](./AGENTS.md)** —
read it before making changes.

## TL;DR for agents

- **⏰ TIMES: ALWAYS US EASTERN (ET), 12-HOUR AM/PM, NEVER UTC / NEVER 24-HOUR (trimcrae standing rule).** Every
  time you report to trimcrae — ETAs, job timestamps, "as of HH:MM", watch cadences, anything — MUST be Eastern
  (EDT = UTC−4) AND written in 12-hour AM/PM format (e.g. "1:00 PM ET", not "13:00 ET"). Convert before writing;
  do not surface UTC or 24-hour time even if the tool/log emits it. (You keep slipping into UTC and 24-hour — this is why it's rule #1.)
- **⏱️ END-OF-TURN "IN FLIGHT" BOARD — when your final message just leaves work running, close with one line + ETA
  per job (trimcrae standing rule, 2026-07-11).** trimcrae can't keep up with many concurrent runs from prose.
  So whenever you end a turn while WAITING on background/AWS work, the LAST thing in your message is a compact
  **"In flight:"** board — **one scannable line per running item** (bullet or table, NOT prose), each stating
  **(a)** what it is, **(b)** its current state/progress, and **(c)** an **ETA in ET 12-hour AM/PM** (or an
  explicit "ETA unknown — <why>", e.g. waiting on spot capacity, when genuinely unknowable). Include what you'll
  do when each finishes if it's non-obvious, in the same line. **List ONLY actual tests/jobs — the real compute
  runs trimcrae cares about (SageMaker jobs, CI analysis/reduce/benchmark runs, subagents doing real work). Do
  NOT list your own internal wake mechanisms — background self-timers, pollers, heartbeat sleeps; those are how
  YOU stay awake, not work trimcrae needs to track (trimcrae, 2026-07-11). ALSO do NOT list SCHEDULED ROUTINES
  (e.g. the weekly field-scan newsletter cron) — a schedule is not running compute; only list things actually
  executing now (trimcrae, 2026-07-13).** If no actual jobs are running, say
  "Nothing in flight" in one line (even if you have a self-timer armed). This composes with rule #1 (ET 12-hour)
  and the "nothing needs your input" sign-off; it REPLACES long status narration — keep the board terse.
- **★★ PRIMARY FOCUS (UPDATED 2026-07-11 PM, trimcrae + gate-AI — SUPERSEDES the atlas-anchor reframe from
  earlier the same day; that reframe is retained just below for reference).** The repo's #1 research program is
  **again the NR4A3-SELECTIVE DEGRADER / computational method-development**, NOT the atlas. Rationale (gate-AI,
  decisive): an unaffiliated no-wet-lab researcher should optimize for **"the largest novel, technically
  defensible contribution using resources under his control"** — and the degrader/method work (structural
  modeling, ligand/linker generation, free-energy calcs, **ternary-ensemble modeling**, paralogue
  counter-screening, microstate analysis, benchmarking, reproducible manuscripts+software) is *entirely
  self-executable*, whereas the atlas's highest-impact claims ultimately depend on **other groups choosing to
  run EMC experiments** — an external dependency you cannot solve by making the atlas more comprehensive.
  **Allocation ≈ 70–80% degrader/method-dev, 20–30% atlas/supporting-biology.** Two linked tracks:
  - **Track A — qualify an NR4A3-engaging WARHEAD.** Finish the repaired ABFE validation (matched NR4A1/2 +
    multiple NR4A3 conformers + explicit microstates + T4L benchmark + independent replicas + honest
    receptor-state limits). The question is whether **denovo_401 is a credible INPUT to degrader design**, NOT
    whether ABFE proves a drug. ($40–80 ABFE-repair spend AUTHORIZED, trimcrae 2026-07-11.)
  - **Track B — a PARALOGUE-DISCRIMINATING TERNARY workflow (the higher-value long-term contribution).** Do
    **NOT** get trapped chasing perfect *binary* NR4A3 selectivity before addressing ternary — the real
    hypothesis is that selectivity emerges from the combined **warhead × linker × E3 × ternary-interface
    geometry** even if binary selectivity is incomplete. **First benchmark is RETROSPECTIVE + blinded against
    NR-V04**, the family-matched positive control: can an ensemble ternary workflow distinguish the
    experimentally-selective NR4A1/VHL assembly from the (not-degraded) NR4A2 and NR4A3 assemblies? Compare
    **ensembles, not one docked pose** — accessible ternary populations, linker strain, PPI-interface
    stability, predicted cooperativity/relative ternary stability, persistence across starting models, Lys
    presentation / ubiquitination-compatible geometry, paralogue counterexamples, E3-choice sensitivity.
    Reliable ternary *ranking* is a known open methodological challenge → that gap is exactly where a rigorous,
    honestly-benchmarked contribution is valuable (a benchmarked NR4A-family ternary-selectivity framework,
    THEN prospective NR4A3 designs — only after the workflow passes the NR-V04 control).
  - **★ WARHEAD-STRATEGY SHARPENING (2026-07-11, external reviewer-AI redirection, ADOPTED; see
    [research/manuscripts/nr4a3-degrader-strategy-ternary-first.md](./research/manuscripts/nr4a3-degrader-strategy-ternary-first.md)).**
    The flagship deliverable is now a **synthesis-ready degrader MATRIX (~6–12 compounds)** getting selectivity
    JOINTLY from a modest binary preference + ternary cooperativity + ubiquitination-compatible geometry — NOT a
    single de novo "selective warhead." Concretely: (1) warheads come from a **congeneric campaign anchored on
    Zaienne compound 19** (methyl 5-bromoindole-3-carboxylate, `zaienne_cmpd19`; functional target-engagement,
    NOT a proven binder), not de novo generation; (2) the primary quantitative tool shifts to **RBFE within the
    congeneric series** (ABFE demoted to secondary calibration); (3) **ternary is the CENTRAL selectivity
    variable** (co-fold stays architecture-triage-only — the epimer control forbids affinity/cooperativity
    ranking; use physics-based ternary calcs). **denovo_401 = benchmark, not lead.** De-prioritized: broad de
    novo generation, generic ML degrader prediction, AF-2 molecular glue, fusion-junction small-molecule
    degrader. This SHARPENS (does not contradict) Track B; the NR-V04 retrospective control still gates all
    prospective ternary ranking.
  - **NR-V04 (Wang 2024) is the CENTRAL positive control.** It degraded NR4A1 but not NR4A2/NR4A3, with
    PLA/co-IP complex evidence + VHL/proteasome dependence — **strong event-level proof that family-selective
    NR4A degradation is achievable** (rebuts "the family is too homologous"). *Justified* inference: a
    computational NR4A3-selective degrader program is credible. *UNjustified* (do NOT claim): that the
    structural mechanism of NR-V04's selectivity is known/solved and directly transferable (no solved ternary
    structure, no matched cross-paralogue cooperativity measurements).
  - **Atlas = SUPPORT infrastructure, not the anchor:** biological rationale for NR4A3 degradation; separate
    fusion-vs-WT biology; anti-target liabilities; assay roadmap for future collaborators; **backup route** if
    degrader design fails; keeps the structural program biologically tethered. It must NOT absorb most effort
    via indefinite evidence aggregation.
  - **Coordination note:** the parallel session (PR #3, `claude/emc-research-strategy-kdz9kn`) set atlas-primacy
    earlier today; THIS decision overrides that ranking. The atlas WORK stays valuable (as support); only its
    *strategic primacy* is demoted. Reconcile PRIMARY FOCUS toward degrader-primary when the branches merge.
- **[SUPERSEDED same-day — atlas-anchor reframe, retained for reference]** the repo's #1 priority is advancing
  an EMC treatment via the full multi-route strategy anchored by the **EMC Open Target & Drug Atlas
  ([research/atlas/](./research/atlas/))** (proteostasis-chromatin; fusion-subtype antiangiogenic biomarker;
  fusion-junction + lineage antigens; direct fusion targeting) + collaborator outreach. Read
  `research/atlas/README.md` + `STATUS.md` for the atlas's own state. **The 2026-06 detail below is
  reference (route status):**
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
- **★★ NEVER OFFER SELF-DOABLE WORK — DO IT, DON'T OFFER IT (trimcrae standing rule, 2026-07-11; the
  "just say the word" anti-pattern this rule exists to kill).** If you catch yourself about to write any of:
  "want me to X?", "I can also X", "should I also X?", "**say the word and I'll X**", "let me know if
  you'd like X", "happy to X if useful", "I could X" — and X is work you could do yourself — **that phrasing
  is the violation. Delete the offer and DO X right now, then report X as done.** The instant you think "X is
  doable" is the trigger to *do* X, not to ask permission for it or dangle it. This applies even when X is
  *optional / additive / nice-to-have* — additive self-doable work is still just-do-it; "it's extra" is not a
  reason to offer instead of act. Ending a turn with a menu of things you *could* do next, when you could have
  just done them, is the precise failure mode. The ONLY time you may surface instead of act is when X is
  genuinely **outward-facing / irreversible / expensive**, needs **access or data only trimcrae has**, or is a
  **real goal-changing decision** (per the autonomy rules above) — never merely because X is optional. When in
  doubt, do it and show it; a thing built is worth infinitely more than a thing offered.
- **★★ APPROVAL IS A GREEN LIGHT TO BUILD, NOT A CHECKPOINT TO REPORT — and finishing ONE deliverable is not a
  stopping point while approved work remains (trimcrae standing rule, 2026-07-11, after I TWICE stopped to
  "report completion / present next steps" while sitting on reviewer-approved, free, no-spend engineering that
  I could just write — trimcrae had to prod "are you writing that code?").** The moment a piece of work becomes
  **{approved/blessed by trimcrae or the reviewer-AI, OR self-doable without needing approval} AND free/no-spend
  AND ready-or-ready-to-build**, that is the trigger to **WRITE IT NOW** and keep going through the *entire*
  approved/self-doable backlog — NOT to summarize, "close the loop," or hand off. Specifically **these are NOT
  stopping points** and must not end a turn while such work remains:
  - a reviewer-AI or trimcrae **approval / "APPROVED" / "go build (a)(b)(c)" / "no further check-in needed"** —
    approval means *execute*, not *report that it was approved*;
  - **completing the one discrete thing that was explicitly asked** when the same plan has more approved/free
    steps queued behind it (finishing the prereg ≠ done, if the harness/pilot/curation it unlocks are free);
  - a "**natural review checkpoint**", a clean commit, or "this feels like a good place to update trimcrae."
  The **reviewer-review-block rule below does NOT require pausing self-doable no-spend work**: produce the block
  only when an **outward-facing/irreversible** step is actually imminent, and keep building everything else in
  the meantime. The ONLY things that legitimately halt the build are the usual real blockers — a spend crossing
  the **expensive** threshold (multi-leg GPU / hundreds of $ / multi-day), an **outward-facing/irreversible**
  action, **access/data only trimcrae has**, or a **genuine goal-changing decision**. Absent one of those,
  "I'll report where things stand and continue next turn" is the violation: continue THIS turn until you hit a
  real blocker or genuinely run out of self-doable work. A report is what you write **after** the backlog is
  exhausted or a real blocker is hit — never instead of doing the next approved, free, ready thing.
- **★★ RESERVE REVIEWER-AI REVIEW BLOCKS FOR (a) MAJOR PROGRAM-SHIFTING DECISIONS or (b) SIGNIFICANT (>$50)
  GPU SPEND — everything else with a good plan, JUST DO IT YOURSELF (trimcrae standing rule, 2026-07-12,
  CORRECTS the earlier "every hand-off gets a block" rule after I over-escalated: routing a review for
  finished free work + panel curation I should have just completed).** trimcrae routes work through a more
  powerful reviewer AI, but that channel is **expensive and interrupts him**, so it is ONLY for the two triggers
  above (plus any genuinely **outward-facing/irreversible** act — sending emails, cutting a release/DOI,
  publishing, submitting). **A review block is NOT for:** finished free/no-spend engineering, curation you can
  verify yourself, choosing the order of self-doable work, "closing the loop," reporting completion, or
  cheap (≤$50) authorized runs. For all of those: **if you have a good plan, execute it and report the result**
  — do not manufacture a review request. **The default is DO, not ASK.** When one of the two triggers *does*
  apply, produce the block as the first thing in your reply (a self-contained, copyable, fenced code box with
  enough standalone context for an informed evaluation — the reviewer sees only what's in the block), and fire
  the phone notification per the rule below. Include, at minimum:
  1. **Role + what to do** — "You are the final reviewer before an unaffiliated researcher (Tristan McRae)
     acts. Approve, or return a specific list of fixes."
  2. **Project + goal** — one paragraph (what the repo/effort is, the objective).
  3. **What was done** — the concrete work/artifacts produced this round (with repo/PR/file paths).
  4. **The exact proposed next action(s)** requiring sign-off (verbatim: which emails to whom, which release,
     etc.), including anything permanent/outward-facing and why now.
  5. **Known risks / uncertainties / judgment calls** — over-claim vs verification level, medical-integrity,
     ethics/tone, scope of a DOI, anything you're unsure about — stated honestly, not hidden.
  6. **Specific questions** you want the reviewer to answer, and a request to return either approval or an
     itemised change list.
  Keep it tight but complete; a reviewer with no other context should be able to judge it. After trimcrae
  returns the verdict, apply the changes (self-doable) and only then proceed to the outward-facing step.
- **★★ PHONE-NOTIFY THE MOMENT A COPYABLE REVIEWER-AI BLOCK IS READY — trimcrae shouldn't have to keep checking
  (trimcrae standing rule, 2026-07-12).** trimcrae routes reviewer/decision blocks to a separate reviewer AI and
  is often away from the chat. So **every time you present a copyable reviewer-AI review/decision block (or any
  hand-off asking trimcrae to route something and paste a response back), fire a phone notification IN THE SAME
  turn.** This is an explicit opt-in, so it OVERRIDES PushNotification's default "err toward not sending." Use
  **belt-and-braces** for reliability (phone delivery is flaky and each single channel can silently miss):
  1. **Always** call **`PushNotification`** (`status: proactive`) with a one-line body (<200 chars, no markdown)
     naming what's ready and any deadline-ish context, e.g. `"Reviewer block ready to route: NR4A3 ternary
     method + budget decision"`. It pushes to the phone when Remote Control is connected and harmlessly no-ops
     ("not sent") if trimcrae is already at the terminal — that's fine.
  2. **Also**, unless there is genuinely nothing for trimcrae to decide, raise the accompanying choice via
     **`AskUserQuestion`** (the repo's PROVEN-reliable phone ping — see the autonomy rules), recommended-option
     first, referencing the block. There is almost always a legitimate question to attach ("route this; meanwhile
     should I proceed on <self-doable X> or hold?" / which fork), so in practice BOTH fire — AskUserQuestion is
     the guaranteed ping, PushNotification the extra nudge. Keep the copyable block itself in the message text;
     the notification is just the ALERT that it's there.
  Only skip the notification if trimcrae is CLEARLY actively chatting in this session right now (the chat already
  reached them). Never fire it for routine progress — ONLY for a ready-to-route reviewer/decision block or an
  explicit "notify me" ask.
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
- **★★ THE DEV SANDBOX IS NOT YOUR EXECUTION LIMIT — AWS + GITHUB ACTIONS ARE THE WAY OUT (trimcrae standing
  rule, 2026-07-12, after I repeatedly declared work "can't be done / can't be tested / needs an env I don't
  have in this sandbox" and STOPPED, when I had two standing escape hatches the whole time).** "I can't run
  X in this sandbox" (no GPU, no OpenFE/OpenMM/RDKit/MD stack, no network to a host, no PDF library, no
  compiler, …) is **NEVER a reason to defer, mark deferred, or hand back to trimcrae.** You have **AWS
  (SageMaker spot GPU/CPU) + GitHub Actions runners** — both are full Linux environments with internet,
  `pip`/`apt`, GPUs, and the repo's conda containers. **The correct move is ALWAYS: build it, then RUN and
  VALIDATE it out there**, not shelve it. Decision rule when something "can't run here":
  1. **Networked / data / light-CPU / PDF / scraping / pip-needs** → a **GitHub Actions runner** (free,
     unrestricted internet, `pip install` + `apt-get install` allowed — e.g. `pip install pdfplumber`,
     `apt-get install poppler-utils`). Dispatch an on-main `workflow_dispatch` with `ref=<branch>` (the
     run-CI-off-a-feature-branch rule) and commit/print the output.
  2. **GPU / MD / FEP / heavy compute** → a **SageMaker managed-spot Training job** (the existing
     `submit_spot` + entry-shim infra; the openfe/openmm/amber containers already exist). VALIDATE-FIRST:
     `mode=smoke` → `n_shards=1` (one real leg) → full fleet; checkpoint per unit.
  3. **"I can't TEST it here"** → that's what the **spot smoke / single-shard shakeout** is for: the job runs
     the real stack on real hardware and tells you if it works. Untestable-in-sandbox ≠ untestable.
  So: writing "hundreds of lines of code that can't be exercised here" is **fine** — you exercise it on AWS.
  A production MD engine, an OpenFE RBFE run, a PDF-table parse, a structure download — all are **DOABLE NOW**
  via (1) or (2). Reserve "deferred" for things blocked by a **real** external dependency (a spend crossing
  the >$50 review gate, data only trimcrae has, an upstream capability that genuinely does not exist yet) —
  never merely because the *dev sandbox* lacks the tool. This SHARPENS the egress-proxy rule below (which is
  the special case of this for networked fetches) and composes with pilot-one-leg-first + wait-out-spot.
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
- **RUN A FEATURE BRANCH'S CI WITHOUT MERGING TO main — DISPATCH AN ON-main `workflow_dispatch` WITH
  `ref=<your-branch>` (verified 2026-07-11).** A NEW `workflow_dispatch` workflow can only be dispatched once
  it exists on the **default branch** (a fresh workflow file on a feature branch 404s on
  `actions_run_trigger`). But an **already-on-main** `workflow_dispatch` workflow **CAN** be dispatched with
  `ref=<feature-branch>`, and GitHub then runs **that branch's version of the workflow file + its code**. So to
  run new/edited CI off a feature branch without touching main: (1) EDIT an existing on-main workflow on your
  branch to also run your new step (or, for a SageMaker job, just pass its `git_ref=<branch>` input so the
  container clones your branch); (2) `actions_run_trigger` with `ref=<branch>`. This session used it to run a
  new registry builder via the on-main `warhead-chem-profile.yml` and to run the Gate-2 matrix off the branch —
  no merge-to-main required. Composes with the egress-proxy/CI-runner rule above (both keep heavy/networked work
  on free runners) and with "never push to main without permission."
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
  **Also (UPDATED 2026-07-11): the repo now has NO on-demand Processing submitters — every SageMaker job was
  converted to managed-spot Training (`sagemaker_submit.submit_spot` + the `sm_io` entry-path shim; the old
  "only ONE concurrent `ml.g5.xlarge` on-demand *Processing* job, serialize MM-GBSA/metad/denovo" constraint is
  therefore RETIRED — they all draw on the 8-wide spot *Training* quota now and can run concurrently). To add a
  new GPU job, use `submit_spot` (never `FrameworkProcessor`); entries read inputs via `sm_io.channel("name")`
  and write to `sm_io.out_dir()`. NOTE: these jobs are now Training, so monitor/stop them with
  `job_type=training` (tail-cloudwatch/list/stop auto-detect too). Each converted job still needs a one-off spot
  smoke before its next production run.**
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
- **★ EVERY SUBSTANTIAL GPU RUN NAMES A PREFERRED CLOUD PROVIDER, CONFIRMED WITH trimcrae IN ADVANCE (trimcrae
  standing rule, 2026-07-12).** Before kicking off any big/fleet GPU run, state the **recommended provider** and
  confirm it with trimcrae *before* launch — do NOT silently default to AWS. The repo is now provider-agnostic
  (`research/modalities/gpu_backend.py` + `autoteardown.py` + `object_store.py`; full plan + accounts +
  free-credit offers in **[research/compute/cheap-gpu-plan.md](./research/compute/cheap-gpu-plan.md)**), so the
  provider is a config, not a rewrite. Default mapping: **Modal** for free/validation first runs (free credits +
  zero-idle-by-design, but PRICIER/hr — not the cheapest); **Salad** (cheapest) or Vast for bulk short-sampling
  triage; **RunPod Secure** or **ACCESS** (free HPC) for long full-sampling terminal legs (a stable host so
  preemption doesn't force costly MD-env reloads); **AWS SageMaker** only when specifically warranted. Compose
  this with the existing >$50 / expensive-spend confirmation — state the provider in the SAME advance
  confirmation. The auto-teardown wrapper guarantees no idle-GPU billing on any provider.
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
- **★★ PILOT ONE LEG/REPLICATE *FOR ITS RESULT* BEFORE FANNING OUT AN ABORTABLE MULTI-LEG SPEND (trimcrae
  standing rule, 2026-07-11).** Distinct from the env/wiring shakeout above (that validates PLUMBING): this is
  a **scientific early-abort** gate. Whenever a multi-leg / multi-replicate / multi-paralogue GPU spend (FEP,
  ABFE, a ternary-ensemble fleet, any fan-out where legs are semi-independent) **could be abandoned early if
  one representative leg comes back UNFAVORABLE or uninformative**, run **ONE decision-relevant leg first**,
  read its result, and only commit the rest of the spend if that pilot leg is favorable/promising. Pick the
  leg with the **highest abort information** — the one most likely to kill the whole idea if it fails (e.g. the
  known-answer POSITIVE CONTROL, or the single paralogue/replicate whose result the conclusion most hinges on).
  This composes with the per-unit checkpoint rule (a pilot leg's completed windows are reused when you DO fan
  out, so the pilot is not wasted) and with the "wait out spot capacity" rule (a pilot is about the RESULT, not
  a capacity probe). Examples: the ABFE λ-repair already does this (validate r1's soft-core-tail overlap before
  spending on r2/r3 error-bar replicates); a retrospective NR-V04 ternary benchmark should run **one paralogue
  (or the CRBN/lenalidomide control) first** and abort if the workflow can't even recover the known geometry,
  before paying for the full NR4A1/2/3 × seeds × linkers fleet. Don't fan out a big spend on a hypothesis a
  single cheap leg could have falsified.
- **★★ SINGLE-SHARD-FIRST *ONLY* WHEN THE RESULT CAN SHORT-CIRCUIT THE FLEET — ONCE YOU'D RUN THE WHOLE FLEET
  NO MATTER WHAT, GO FULL PARALLEL IMMEDIATELY (up to the 8-wide spot quota) (trimcrae, 2026-07-12; sharpens
  pilot-one-leg-first).** The ONLY reason to run one shard/leg at a time is **early-abort/short-circuit value**:
  a real chance that that one result comes back unfavorable/uninformative and **kills the desire to run the
  rest**, saving the fleet spend. **Litmus test before serializing:** *"Is there a result this shard could
  return that would make me NOT run the rest of the fleet?"* If **yes** → run the one shard first (pick the
  highest-abort-information one). If **no** — you're going to run the entire fleet regardless of what this shard
  shows — then **serializing is pure wasted wall-clock for zero decision value; fan out ALL shards at once**
  (bounded by the ~8 spot-Training shards available). Parallelizing costs the **same GPU-$** as serial (same
  total compute, just spread across concurrent instances) so once the abort-decision is settled there is never
  a reason to drip one-at-a-time. Applies at whatever granularity the fan-out is abortable: pilot ONE edge
  before a multi-edge RBFE tranche (edge-level abort value), but once committed to that tranche run its legs
  8-way parallel — don't serialize legs whose results can't change the go-decision. (Caveat that is NOT this
  rule: coupled units that physically cannot be split — e.g. HREX λ-windows exchanging configs within one
  OpenFE transformation — are serial by *physics*, not by this choice; parallelize by adding more independent
  legs/shards, not by trying to split a coupled simulation.)
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
