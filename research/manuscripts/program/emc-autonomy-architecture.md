---
id: DOC-EMC-AUTONOMY-ARCHITECTURE
title: The autonomous EMC researcher — architecture, build order and authority model
level: L3
kind: architecture
status: live
canonical_for: [autonomy loop architecture, cycle contract, publication authority model, budget governor]
purpose: >
  The design for running this repository's EMC research program without a human in the cycle —
  what picks the work, what does it, what checks it, what may go outward without asking, and what
  is still allowed to reach trimcrae. It is a BUILD PLAN, not a status board.
scope: >
  Owns the autonomy loop's architecture and its invariants. It does NOT own the research plan
  (the roadmap does), the commit gates (`repo-gates`), the hardening cycle (`paper-hardening`),
  the aiXiv mechanics (`aixiv-submission`), or any cost figure (pricing.md).
audience: [maintainers, autonomous research agents]
date: 2026-08-26
last_verified: 2026-08-26
related: [DOC-NR4A3-PROGRAM-MAP, DOC-AGENTS, DOC-METHOD-WATCH, DOC-DAILY-EMAIL-SYSTEM]
---

# The autonomous EMC researcher

**The ask (trimcrae, 2026-08-26):** *"complete automation of EMC research in this repo … complete
automation so that I never have to check in on it."*

**The answer in one paragraph.** Four of the five layers this needs already exist and are load-bearing
today; what is missing is the layer that decides *what research to do next* and the contract that lets a
cycle finish without a human. This document specifies that missing layer, the invariants that keep it
honest, and the one thing it can never grant itself — permission to speak in trimcrae's name.

⚠ **Read [CLAUDE.md](../../../CLAUDE.md) §0 first.** The single largest failure risk in this design is
not a crash. It is a loop that runs forever, commits daily, and advances nothing — because writing up a
closed route always looks like progress and is always easier than the live one. Every invariant in §7
exists to make that failure *visible*.

---

## 0 · Does this belong in a skill?

**Partly — and the split is the design.** A skill is loaded-on-demand instruction text. It has no
memory, no clock, and no way to survive the session that read it. Complete automation needs all three.

| what | why it cannot be a skill | where it goes |
|---|---|---|
| **The clock** | A skill cannot fire. Something outside the session must start a cycle. | Claude Routines + Actions `schedule:` — §2 |
| **The queue and its state** | A skill is text, not memory. A session that dies mid-cycle must be resumable from *committed state*, which is the only thing that survives. | `research/autonomy/*.json` — §3 |
| **The hands** | Network, pip, PDF, GPU and secrets are not in the sandbox. | Actions workflows — already built |
| **The operating loop** | ✅ This one IS instruction text: what a fired session does, in what order, and what it may never do. | **a new skill, `research-loop`** — §4 |

⛔ **And the new skill must restate nothing.** `repo-gates`, `paper-hardening`, `aixiv-submission`,
`gpu-compute`, `ci-escape-hatches` and `inflight-reporting` already own their mechanics. `research-loop`
is an **orchestrator**: it names which skill to load at which step and owns only the cycle contract
(§4.2) and the stop conditions (§8). CLAUDE.md rule 1 applies to skills exactly as to manuscripts.

⭐ **Why a skill at all rather than more CLAUDE.md?** CLAUDE.md loads every session, including the
hundreds that are ordinary interactive work. The cycle contract is dead weight in those. A skill
triggered by the cycle prompt is loaded exactly when it binds.

---

## 1 · What already exists — build on it, do not rebuild it

**⭐ This repository already has an orchestrator, and it works.** `research/modalities/work_ledger.py`
+ `research/modalities/work-ledger.json`, ticked by
[`lane-staleness-watch.yml`](../../../.github/workflows/lane-staleness-watch.yml), already does the hard
half: it holds 50+ entries with `owner`, `state`, `blocked_by`, `attempts`, `retry_budget` and
`next_evidence_due_utc`; it emits a machine dispatch plan (`--emit-dispatch`) that the workflow turns
into real `workflow run` calls; it caps and deduplicates that plan; and the in-flight board is
*generated from it* precisely so a session cannot invent an owner.

Its premise — ***"work with no owner is indistinguishable from work in progress"*** — is the correct
premise for the whole autonomy problem.

⛔ **Its scope is compute lanes, not research.** It tracks *is a GPU host being watched*, not *is the
NR4A3 paralogue-discrimination question being answered*. **The build is to generalize it, not to
duplicate it** (§3), and the generalization must keep every property that made it work: machine-emitted
dispatch, retry budgets, staleness that is *measured* rather than asserted, and a board that cannot
render a row the ledger does not carry.

| layer | state | what carries it |
|---|---|---|
| Hands (network, pip, GPU, secrets, PDF, browser) | ✅ live | ~167 Actions workflows; `AIXIV_TOKEN`, `ZENODO_TOKEN`, `MAIL_PASSWORD` already set |
| Gates (claims, citations, consistency, style, model, registry) | ✅ live | `scripts/preflight.sh` — see `repo-gates` |
| Compute orchestration + watchdogs + reapers | ✅ live | `work-ledger.json`, `vast-account-reaper.yml`, `fleet-supervision-alarm.yml` |
| Field/capability watch | ✅ live — layer 1 repaired 2026-08-24, cadence unconfirmed (§8.2) | `method-watch.md` layers 1–3 |
| Human channel | ✅ live | weekly Friday newsletter (`method-watch.yml`) |
| **Research prioritization + cycle contract** | ✅ **BUILT 2026-08-26** | `research/autonomy/priority.py` + the `research-loop` skill — §3, §4 |
| **Publication authority** | ✅ **GRANTED and GATED 2026-08-26** | `publish_bar.py` (six clauses) + `publication-authority.json` — §6 |

---

## 2 · Layer A — the clock, and its two measured failure modes

Two clocks exist. **Neither is reliable alone, and the design uses both because their failure modes are
independent.**

### 2.1 · Actions `schedule:` — throttled, and the repo has measured it

Delivered gaps of **125–222 min against a `*/15` request** are recorded across this repo's workflow
headers, and `fleet-supervision-alarm.yml` is the only live measurement of the gap. ⛔ **A cron
interval is a request, not a cadence** — never make a safety property depend on one firing.

### 2.2 · Claude Routines — fire reliably, but an agent-created one is born crippled

★★ **This is the single most important operational fact in this document, it is measured twice, and it
was re-confirmed live on 2026-08-26 while this file was being written.**

A Routine created by an agent (`create_trigger`, `created_via: meta_mcp`) carries **no `sources:`
grant**. Its fired sessions get **no repo checkout and no `mcp__github__*` tools**. It fires on schedule
forever and delivers nothing. The evidence, three independent readings:

- The **field-scan Routine** (`trig_01X5xHy1cmkLjkATEijZSNJf`) has fired every Friday since 2026-07-13
  and written **zero** entries to `research/field-scan-log.md`. Its STEP 0 is `git checkout main`, which
  has nothing to check out.
- The **newsletter Routine** (`trig_01Rjh49ujsZttmDSbTki58tT`, `created_via: http_api` — the claude.ai
  UI) carries `sources: [git_repository trimcrae/Rare-cancers]` and **has delivered on every fire**.
- `create_trigger` itself now returns the warning verbatim: *"this trigger stores no MCP connectors, so
  the sessions it fires will run without connector tools … ask the user to create it from the claude.ai
  routines UI."*

⛔⛔ **A FIRED ROUTINE IS NOT A DELIVERED ONE. Read the artifact it was supposed to write, never its
fire record.** This is why every cycle in §4 ends by committing a **receipt**, and why §5's watcher
alarms on a missing receipt rather than on a missing fire.

**⭐ RE-TESTED DIRECTLY ON 2026-08-26 RATHER THAN INHERITED, AND THE RESULT IS DECISIVE.** CLAUDE.md §4
forbids carrying a remembered platform fact into a plan, so the constraint was re-run as an experiment: a
one-shot `create_trigger` Routine whose prompt asked the fired session to inventory its own tools, call
`add_repo`, clone the repository over HTTPS, and push a probe file to a branch — a chain in which **any**
working rung would have left a visible artifact.

| observation | reading |
|---|---|
| Fired 14:47:28Z, ran **4 m 03 s**, `ROUTINE_RUN_STATUS_SUCCEEDED`, 7,961 output tokens spent | It really ran. This is not a non-fire. |
| Branch `automation-probe` **does not exist** on the remote | Every rung of the chain failed — including `add_repo` and a plain `git clone`. |
| The fired session's `session_context` carries **no `sources` key at all** | No repo, exactly as the two prior readings said. |
| The platform tags it **`config:routine-lineage-none`** and **`routine:agent-minted`** | ⭐ The platform names the defect itself. An agent-minted Routine has no lineage to inherit a grant from. |

⛔ **So the constraint HOLDS as of 2026-08-26, and it is not a bug to be worked around from inside.**
A "SUCCEEDED" run that burned four minutes and produced nothing is the exact shape of the failure that
went six weeks unnoticed — which is why §5.2 alarms on receipts and never on fire records.

★★ **AND THE PROBE CAUGHT A SECOND THING NOBODY WAS LOOKING FOR: the fired session ran on
`claude-sonnet-5`, not the parent's `claude-opus-5`.** A Routine-fired session does **not** inherit the
creating session's model. ⛔ **The driver Routine must pin its model explicitly**, or the research loop
silently runs on a different model than every measurement in this repository was taken with — a
model-swap nobody would see in any artifact.

★ **CONSEQUENCE FOR "I never have to check in": there is exactly one irreducible human setup step, and
it is a one-time click.** trimcrae must create the driver Routine **from the claude.ai Routines UI with
`trimcrae/Rare-cancers` attached as a source.** Nothing in this repository can grant that. After that
one action the loop is self-sustaining — and §5's watcher is what detects it if the grant is ever lost.

⭐ **The positive control exists and it is recent.** The field-scan Routine was recreated from the UI on
2026-08-24; its stored config carries `sources: [git_repository trimcrae/Rare-cancers]`, and it
committed a full dated entry to `research/field-scan-log.md` on `main`. **The mechanism works.** ⚠ Its
delivery so far is from its *creation-time* fire; a delivery on a *scheduled* fire has not yet been
observed, and the first one due is Friday 2026-08-28. Read that Friday's artifact, not its fire record.

### 2.3 · The clock design

| Routine | cadence | fires | why this cadence |
|---|---|---|---|
| **Driver** | every 4 h | a fresh session running the §4 cycle | Short enough that a lost cycle costs little; long enough that a stuck cycle is not amplified. |
| **Escalation sweep** | daily | a fresh session that reads receipts only | Cheap; its whole job is §5's four escalation triggers. |
| **Weekly digest** | Fridays | the existing newsletter | Already live; becomes the "you never have to check in" channel. |

⛔ **Both new Routines must pin the model explicitly and attach the repo as a source** — §2.2 measured a
fired session silently running on a different model with no repo. **Neither property is a default.**

⛔ **Do NOT build a self-wake poller for this.** `ci-escape-hatches` records that `CronCreate` vanished
twice inside 25 min even with `durable: true`, and `ScheduleWakeup` did not fire outside `/loop`. The
background-bash poller is the right tool for *supervising one billing fleet inside one session*; it is
the wrong tool for a cycle that must survive the session's death.

---

## 3 · Layer B — the queue, and how it ranks work

**One new file is the source of truth: `research/autonomy/research-ledger.json`.** It is to research
what `work-ledger.json` is to compute, and it is generated-then-hand-amendable: a scorer projects the
graph into it, and a session may add an entry the graph cannot express.

### 3.1 · Entry schema

Deliberately mirrors `work-ledger.json` so the two can share the staleness and retry machinery.

```
entries[]:
  id                  AUT-### — stable, never reused
  what                one sentence, falsifiable, in the imperative
  serves              {route: RT-*, requirement: R*, publication: PUB-*}   ← the join to systems/graph
  kind                experiment | analysis | write | harden | fetch | regrade | venue | negative
  state               queued | running | blocked | done | abandoned
  owner               the cycle id that took it, or null
  cost_class          free | cheap | expensive        ← CLAUDE.md §2's ladder, never a typed $
  cost_points_at      the rung or ladder row that owns the figure   ← never a number here
  blocked_by          BLK-* | a named external fact | null
  blocked_evidence    what was OBSERVED to establish the block, with its date
  retry_budget        int, decremented on a fruitless attempt
  attempts            int
  last_evidence_utc   when this entry last changed on EVIDENCE, not on a tick
  score               written by the scorer, never by hand
  score_inputs        the field values the score was computed from  ← auditable
```

### 3.2 · The scorer — `research/autonomy/priority.py`

Deterministic, stdlib-only, no model in the loop. Weights live in **one** file,
`research/autonomy/priority-weights.json`; the script never types one. It reads
`systems/graph/routes.json`, `publications.json`, `requirements.json`, `blockers.json` and
`technologies.json` — all of which already carry the needed fields (`state.status`,
`timing.recommendation`, `next.blocked_on`, `readiness.attainable_today`, `patient_path`,
`revival_trigger`).

**The objective function is the north star, stated as arithmetic:**

```
score =   W_live      · is_live                      # state.status ∈ {ready, active}; work_state ≠ complete
        + W_patient   · patient_path_without_bench   # publications.json — 6 of 31 endpoints qualify
        + W_pursue    · (timing.recommendation == pursue_now)
        + W_tier1     · grade.value startswith "Tier 1"
        + W_endpoint  · (readiness.attainable_today ∈ {preprint, journal_submission})
        + W_unblocks  · count(routes this would unblock)
        − W_cost      · cost_class_rank
        − W_blocked   · blocked_on_human
        − W_stale     · attempts_without_evidence
```

⛔⛔ **Three hard rules the scorer enforces in code, not in prose — each is a CLAUDE.md §0 rule made
mechanical:**

1. **A `kind: negative` entry may never outrank ANY entry with `is_live`.** Not by weights — by a hard
   clamp applied after scoring. §0 is explicit that a negative is a byproduct, never the objective, and
   weights alone will eventually let one win.
2. **Axis D is not an input.** [`emc-post-degrader-options.md`](./emc-post-degrader-options.md) grades
   partly on *what do we hold if the experiment never happens*, which structurally promotes finished
   work. It is a tiebreaker for a human, and the scorer does not see it.
3. **`blocked` is a claim that must carry evidence.** An entry with `state: blocked` and an empty
   `blocked_evidence` is **not** filtered out — it is promoted to a `kind: fetch` entry that re-tests
   the block, because §0 records that most blocked rows are waiting on a $0 check.

### 3.3 · Seeding it

The first ledger is projected from the graph and is expected to be wrong at the margins. That is fine:
the loop corrects it, because every cycle that touches an entry writes back what it *observed*.

---

## 4 · Layer C — the executor, and the session shapes

### 4.1 · Three session shapes, chosen by context cost — not by preference

★ **Context is the scarce resource, and the shapes exist to bound it.** A cycle that reads the whole
repo dies of its own success.

| shape | when | why |
|---|---|---|
| **Driver session** (Routine-fired, fresh every cycle) | every cycle | Fresh context is a *feature*: it cannot inherit a stale belief from the last cycle. Reads the ledger + the top item's owner files, and nothing else. |
| **Parallel subagents** (in-session) | ≥2 independent items, or the 5 blind seats of a hardening round | Wall-clock. Each returns a **structured verdict**, never prose — the driver must not pay context for the search that produced it. |
| **A new session** (`create_session`) | any item that will not fit one context: a full hardening cycle, a multi-round review, a large corpus read | The driver spawns it, records its session id on the entry, and **ends its own turn**. The child commits its own receipt. |

⛔ **The driver never waits.** CLAUDE.md §1 and §6: it dispatches, records, and ends. A cycle that
blocks on a subagent is a cycle that can be killed by a rate limit while holding uncommitted work.

⛔ **And parallel width is governed, not chosen.** See §9 — an ungoverned fan-out is what burned the
weekly cap once already.

### 4.2 · The cycle contract — what one fired session does

**Ten steps. A cycle that cannot complete step 10 has failed, however much it wrote.**

1. **Orient cheaply.** Read `research/autonomy/autonomy-state.json` (last cycle, budget posture,
   backoff level) and `research-ledger.json`. Nothing else yet.
2. **Refuse to start if the loop is unhealthy.** Backoff level at max, or an unresolved §5 escalation
   older than its deadline → write a receipt saying so and stop. A loop that keeps working through its
   own alarm is the alarm failing.
3. **Re-score.** Run `priority.py`. It is $0 and deterministic; never trust a score from a previous
   cycle's context.
4. **Take the top item whose `cost_class` fits the current budget posture.** Free work always fits.
5. **Take the free observations first.** CLAUDE.md §4: any `UNKNOWN`/`STALE` field on the chosen item
   that a `git show`, a public Actions read or a `WebSearch` would settle is settled **now**, before any
   sentence is written about it.
6. **Do the work**, loading the owning skill for the step (`gpu-compute` to rent, `paper-hardening` to
   harden, `aixiv-submission` to post, `ci-escape-hatches` to route out of the sandbox).
7. **Self-check** — §5's dimensions, run as gates, not as a vibe.
8. **Commit** through `./scripts/preflight.sh` per `repo-gates`. Checkpoint after **each item**, never
   batched — the rate-limit design in §9 depends on this.
9. **Write back what was observed** onto the entry: `last_evidence_utc`, the new state, and for a
   failure, the *diagnostic* — CLAUDE.md §4 forbids a "probably".
10. **Write the receipt** to `research/autonomy/receipts/<cycle-id>.json`: what was taken, what changed,
    what it cost, what is now queued, and **`route_advanced`** — the id of the live route this cycle
    moved, or the literal `none`.

⭐ **`route_advanced: none` is the design's own honesty instrument.** A loop that writes it three cycles
running is doing documentation, not research, and §5 escalates on exactly that.

---

## 5 · Layer D — self-checking, on every dimension that can go wrong

Two kinds, and conflating them is how a loop passes its own tests while producing nothing.

### 5.1 · Artifact correctness — already built, do not rebuild

Every gate in `./scripts/preflight.sh` (enumerated in `repo-gates`, and the list is *derived from the
script* by `systems_check.py::_preflight_gates()` so it cannot drift) already covers claim strength
(R1–R5), citation provenance, cross-document numeric consistency, changed-prose qualifier loss, prose
style, the systems model, the registry evidence contract and generated-artifact reproduction.

⛔ **The autonomy loop adds no new manuscript linter.** It *runs* these, and it treats a red gate as a
stop, per `repo-gates`.

### 5.2 · Loop health — new, and it is what "never check in" actually requires

These have no gate today because nothing was running unattended. Checked by
`.github/workflows/autonomy-tick.yml` (mechanical, $0, no model), which writes
`research/autonomy/health.json` in the `alarm-state.json` idiom already used in this repo
(`_generated_utc`, `_stale_after_utc`, `_stale_after_means`, so a reader can tell the file is dead
without running anything):

⛔ **EVERY ROW DECLARES WHAT ITS RED DOES TO THE LOOP** (`health.py`'s `CONDITION_ON_RED`), and that column did not exist until 2026-08-27, when its absence killed the loop. `research-loop` §1 stopped a cycle on ANY red; every condition written before that day happened to be one a cycle could act on, so the rule held by luck. Two conditions were then added whose subject is **immutable committed history** — `cycles_are_sized` and `fanout_is_governed` read receipts — and nothing in any future session could clear them. The driver fired, read the red board, refused, and pushed *"health check permanently red, needs your call."*
**`blocks`** a cycle must not start · **`redirects`** the cycle runs and fixing this is its work · **`advises`** report, never stop. `--check` exits non-zero for `blocks` only; `--check-any` keeps the old any-red answer. Retrospective conditions are windowed to `RECEIPT_WINDOW` so good behaviour clears them, and every receipt-reading condition declares its recovery in `RECEIPT_SCOPE`.

| condition | on red | red when | why it exists |
|---|---|---|---|
| `cycle_delivering` | no receipt within 2 expected cycle periods | §2.2 — a fired Routine is not a delivered one |
| `advancing_live_work` | 3 consecutive receipts with `route_advanced: none` | CLAUDE.md §0 — the documentation-drift failure |
| `evidence_moving` | an entry `running` with `last_evidence_utc` unchanged over 2 cycles | §4's unproven-pipeline rule: progress checks, not liveness pings |
| `blocks_are_real` | any `blocked` entry with empty `blocked_evidence` | §0 — "blocked" usually means "nobody checked" |
| `queue_is_takeable` | no entry is unowned, unblocked and still holding retry budget | added 2026-08-26 — every other row asks whether the loop works WELL; this asks whether there is work it CAN do. A fully-owned queue makes a loop that fires, finds nothing, writes a receipt saying so, and repeats: a stall wearing the costume of a quiet week. ⚠ *Declared late — the condition shipped before this row existed.* |
| `cycles_are_sized` | one `session_id` carries more than `max_cycles_per_session` receipts | added 2026-08-26 — **the session-shape rule (§4.1, skill §3) had no measurement at all, and it failed by being UNREACHABLE rather than unheeded.** It lived only in `.claude/skills/research-loop/SKILL.md`, a skill binds only when loaded, and every one of that skill's load triggers was a Routine firing a cycle — so on the INTERACTIVE path, where a human asks for research work directly, it never bound. Measured: `"name":"Skill"` appears **0 times** in the transcript of the session that broke it, which ran CYC-0005 and CYC-0006 end to end, compacted 23 times and reached 7.6 MB; an earlier session ran three cycles. Reachability was repaired in CLAUDE.md §6, which loads every session; this row is the enforcement half, because a rule nothing measures decays into a suggestion. ⚠ It bounds CYCLES, a proxy for context — one enormous single cycle passes it. Nothing here can read a context window, and receipts already carry `session_id`. |
| `fanout_is_governed` | a receipt records `subagents.max_concurrent` above `subagent_width` | added 2026-08-26 — **§9's most important dial had never been read by anything.** `grep -rn subagent_width` over the whole repository returned TWO hits: the JSON defining it and one test asserting it equals 5. No code consulted it and no receipt recorded a dispatch, so compliance was luck. The unit had never been written down either, which made it UNENFORCEABLE rather than unenforced — now CONCURRENT agents, recorded in `_subagent_width_means`. ⚠ Retrospective: nothing can intercept a dispatch, so prevention lives at CLAUDE.md §1's spawn authorisation and this row makes an overrun visible. ⚠ It governs concurrency and NOT the serial total, which stays honestly ungoverned until `utilisation_denominator` has an observed value. |
| `budget_recovering` | backoff level > 0 for > 24 h | §9 — a limit that never clears is a stuck loop |
| `gates_green` | preflight red on `main` for > 24 h | a red trunk stops every cycle at step 8 |
| `authority_respected` | any outward act in the log without a matching grant in `publication-authority.json` | §6 — the one thing that must never be self-granted |

⛔ **`autonomy-tick.yml` adopts `fleet_armed.py`'s discipline: no work, no commit.** The measured cost
of ignoring this was 1,476 commits in 24 h, 703 of which said they did nothing.

---

## 6 · Layer E — the publication ladder, and the authority model

### 6.1 · What "publish-worthy" means here — and what it explicitly does not

⛔⛔ **NOT the aiXiv Rating.** `POST /api/submit-review` is **unauthenticated** with a free-text
`reviewer` field: any party can post any rating on any paper, and the corpus contains a 10 whose entire
review text is `Nah`. Eleven versions of one paper never moved above 6 and trended **down** as the paper
improved. `aixiv-submission` §0/§3 owns this finding. **A rating is never a gate, a target, or a
quality claim in this system.**

**The bar is a conjunction, and every clause is machine-checkable:**

1. **Hardening converged** — no blockers and no P1s in the last round, per `paper-hardening`'s
   convergence test, recorded in the paper's hardening state file.
2. **`PREFLIGHT_FULL=1` green** on the exact commit being posted (`repo-gates`: this is one of the four
   things FULL is for).
3. **Claim ceiling honoured** — `lint_claims.py` R1–R5 clean, and the endpoint's claim does not exceed
   `requirements.json[].claim_ceiling`.
4. **Every identifier resolvable** — `lint_citations.py` clean. Claim strength and citation provenance
   are orthogonal; both are required.
5. **The endpoint exists as a falsifiable sentence** in `publications.json` and the paper defends *that*
   sentence.
6. **An independent adversarial seat**, blind to the authoring context, reports the central claim
   supported by the committed artifacts.

### 6.2 · The two rungs, and why they are governed differently

| rung | act | authority |
|---|---|---|
| **aiXiv preprint** | post / new version | ⭐ **Candidate for a standing grant** — see §6.3 |
| **Journal submission** | submit to a named venue | ⛔ **Always escalates.** Costs money, is slow to undo, and picks an identifier a reader may cite. |

### 6.3 · The authority model — `research/autonomy/publication-authority.json`

★★ **This is the one genuinely new permission in the whole design, and the loop cannot grant it to
itself.** As written today, [AGENTS.md](../../../AGENTS.md) says *"Human-in-the-loop, always … no
automated preprint or journal posting"*, and [CLAUDE.md](../../../CLAUDE.md) §3 requires that trimcrae
named **that** paper for **that** act. Automating aiXiv contradicts both.

⛔ **So the grant is not a config value the loop writes — it is a rule change trimcrae makes, and the
file, AGENTS.md and CLAUDE.md §3 must change in the SAME COMMIT.** A `publication-authority.json` that
disagrees with CLAUDE.md is not an authority, it is a bug.

**★ DECIDED 2026-08-26 (D1): the grant is BAR-SCOPED, not paper-scoped.** trimcrae chose *"Broad: any
paper meeting the bar"* over the narrow named-paper list, having been shown in the same question that
this is the inference CLAUDE.md §3 forbids. **It is his rule and his call, and it is now recorded as an
amendment rather than an exception.**

```
{
  "aixiv": {
    "standing_grant": true,
    "granted_by": "trimcrae, 2026-08-26, AskUserQuestion D1: 'Broad: any paper meeting the bar'",
    "granted_against": [                   ← the backdrop the grant was given against. If any of these
      "the bar is the six clauses of §6.1, all machine-checkable",   changes, RE-ASK. It was not
      "aiXiv only — no other venue, ever",                           granted in general.
      "every journal submission still escalates (D4)"
    ],
    "scope": {
      "papers": "ANY PUB-* passing all six clauses of §6.1",
      "acts": ["submit", "new_version"],
      "max_versions_per_paper": N,         ← aixiv-submission §3: eleven versions of one paper never
                                              moved its rating and it trended DOWN. A version cap
                                              stops the loop rediscovering that at trimcrae's expense.
      "notify_after_each_post": true       ← not a gate. He does not approve it; he learns of it.
    }
  },
  "journal": { "standing_grant": false }   ← constant. Not a parameter. Not reachable by any bar.
}
```

⛔ **THE BAR IS NOW THE PERMISSION, SO THE BAR IS LOAD-BEARING IN A WAY IT WAS NOT BEFORE.** Every
clause of §6.1 must be a script that returns a boolean, and a clause that cannot be checked
mechanically fails closed. **A clause the loop grades for itself is not a clause** — it is the loop
deciding it may publish.

⛔ **And three things this grant still does NOT authorise, because he did not grant them:** any venue
other than aiXiv; reshaping or retitling a paper to clear the bar (CLAUDE.md §3 — the title is what a
reader searches); and posting a paper whose *claim* exceeds its endpoint's recorded `claim_ceiling`,
which is clause 3 and is not negotiable by any grant.

★ **The rule amendment is part of phase 7 and lands in ONE commit** — `publication-authority.json`,
AGENTS.md's *"Human-in-the-loop, always … no automated preprint posting"*, and CLAUDE.md §3, together.
A `publication-authority.json` that disagrees with CLAUDE.md is not an authority, it is a bug.

⛔ **And the loop may never reshape a named paper.** Retitling or reframing to chase a venue's taste
publishes something he did not ask for under the identifier he did — CLAUDE.md §3, and the title is what
a reader searches.

### 6.4 · Journal fit — `research/autonomy/venue-fit.json`

The repo already holds the hard-won inputs and they are primary-source, not remembered:
`venue-fee-routes-2026-08-10.json` (verified $0 routes, OpenAlex `apc_usd`, DOAJ presence),
`venue-fee-pages-2026-08-24.json`, `venue-policy-browser-fetch.json`,
`venue-typeset-geometry.json` (built because one venue charges **per printed page**, so page count is a
*cost* question), and the five-test rubric in
[`preprint-host-decision.md`](./preprint-host-decision.md)/`-round2.md`.

**What is missing is the join: manuscript → ranked venues.** Build it as a scored table on: verified $0
route · unaffiliated author permitted · scope match to the endpoint's claim · PubMed/Europe PMC indexed
· preprint-friendly · page-charge exposure. **Cheap first** is the ask, so the $0-route clause is a
filter, not a weight. Escalation carries the top three **with their evidence**, never a
recommendation alone.

---

## 7 · The escalation contract — the only four things that reach trimcrae

**Everything else is silent.** The weekly newsletter is the ambient channel; it already exists and needs
no build.

| # | trigger | channel |
|---|---|---|
| 1 | **A journal submission is recommended** — a paper passed §6.1 and a venue fits | `AskUserQuestion` + `PushNotification` **immediately** (D4), with the top three venue fits and the evidence behind each. ⚠ *An aiXiv post is no longer an escalation under D1 — it is a **notification after the fact**, per `notify_after_each_post`.* |
| 2 | Spend crossing **expensive** (CLAUDE.md §2), or a `⚠ DRIFT` row we would otherwise buy | `AskUserQuestion` + `PushNotification` |
| 3 | A genuinely goal-changing fact: the north-star route closes, or a capability lands that reorders the portfolio | `AskUserQuestion` + `PushNotification` |
| 4 | **The loop itself is unhealthy** — any §5.2 condition red past its deadline | `PushNotification` + the weekly digest |

⛔ **Trigger 4 is the one that makes "I never check in" honest.** Without it, a silent loop and a dead
loop look identical — which is precisely how the field-scan Routine went six weeks unnoticed.

⛔ **Nothing else escalates.** Not a finished cycle, not a green gate, not a clean commit, not a
question whose answer is orderable by the loop itself (CLAUDE.md §2).

---

## 8 · Monitoring — the two watches that would change the plan

Both extend `method-watch.md`'s layer 3 (`trigger_scan.py` +
[`method-watch-triggers.json`](../../method-watch-triggers.json)), which already has the right shape:
a named capability, a `revival_trigger`, and the routes a hit would reopen. **A hit is an unvalidated
lead and never changes a status by itself** — that rule is inherited unchanged.

### 8.1 · The AI-preprint-landscape watch — new `trigger_kind: venue`

What would make us change where we post: aiXiv API-surface or policy change; a host's screening clause
changing (this is what moved the last decision — Research Square declined, Qeios won on the no-screening
test); indexing changes (a host gaining or losing Europe PMC / PubMed); APC changes on a shortlisted
venue; a **new** agent-friendly host appearing. Rung 0 (`WebSearch`) settles most of it; a claim
heading for a decision memo goes to rung 1 and lands as a committed artifact.

### 8.2 · The science / AI-capability watch — mostly re-pointing what exists

`technologies.json` (27 records with `scan_trigger`), `forecasts.json` (27 with
`what_would_move_this`) and 43 routes carrying a `revival_trigger` already encode *what would reopen
what*. The gap is that a `revival_trigger` is **recorded and never re-tested**.

⭐ **So the loop adds one entry kind: `regrade`.** Every parked route with a `revival_trigger` gets a
scheduled re-test, and the re-test is a ledger entry like any other — which means it is scored, owned,
and visible when it stops happening. CLAUDE.md §4 is the justification and it is unusually pointed:
*a remembered AI figure is a dated observation that almost always **understates***, and that bias lands
hardest on *"too small"*, *"doesn't exist"*, *"can't do that yet"* — the three sentences that close a
route.

⚠ **CORRECTION — layer 1 is NOT dead, and `research/method-watch.md` is stale on this.** That file
names `trig_01X5xHy1cmkLjkATEijZSNJf` and says repair "requires trimcrae". Checked live 2026-08-26 (a
$0 `list_triggers` read): the field-scan Routine is now **`trig_01KJhjjkD57Ke9F37SayypKd`**, created
2026-08-24 via the UI, carrying the `sources` grant — and it delivered a full dated entry to
`research/field-scan-log.md`. **The repair already happened; the doc never learned.** Layer 1's scope —
immunotherapy, neoantigen, *any* new solid-tumour modality — is the widest of the three, so this matters.

⛔ **Two things follow, and neither is "declare it fixed".** (a) The stale pointer in `method-watch.md`
is corrected as part of phase 8, because a doc that names a dead trigger id will send the next session
chasing a ghost. (b) Its delivery so far is from the creation-time fire; **the first scheduled fire is
2026-08-28**, and per §2.2 that is verified by reading the artifact, not the fire record. The driver
Routine should absorb layer 1's prompt (archived at `research/routines/field-scan-routine-prompt.md`)
only *after* that Friday confirms the cadence — folding a working Routine into an unproven one is a
downgrade.

---

## 9 · Rate limits — the budget governor

★★ **This has already happened here, and it is the reason the design is shaped this way.** A 107-agent
fan-out hit the account weekly usage limit: **40 completed, 67 errored, and the synthesis step failed**,
so the tool's returned result was a truncation artifact. The resumed run reached 102 results and then
died when the container restarted. **The synthesis never ran in either pass**, and the findings had to
be recovered by hand from `journal.jsonl`.

**Four properties, and they are the same four that make spot GPU safe:**

1. **⛔ Checkpoint after each unit, commit as you go.** A cycle holding five items' work in context is a
   cycle that loses five items to one limit. §4.2 step 8 is not a style preference.
2. **⛔ State lives in git, never in context.** A killed session loses nothing but its turn; the next
   Routine fire re-reads the ledger and continues. **This is the whole recovery mechanism** — there is
   no resume protocol to write, because there is no in-context state worth resuming.
3. **⭐ Backoff on the *observed* signal, not a guess.** `autonomy-state.json` carries a `backoff_level`.
   A cycle that ends without a receipt increments it; a clean cycle decrements it. Level controls two
   dials: **cycle interval** (4 h → 8 h → 24 h) and **parallel width** (the subagent cap: 5 → 2 → 1).
   Width is the more important dial — the incident above was a *width* failure, not a depth one.
4. **⭐⭐ Degrade to the free lane rather than stopping.** Actions workflows consume **no Claude budget
   at all**. At backoff level ≥ 2 the cycle stops taking `analysis`/`write`/`harden` items and takes only
   `fetch` and `regrade` items, which are dispatch-and-exit. **The loop keeps making progress on a
   spent budget**, which is exactly what *"not letting usage limits kill progress forever"* requires.

### 9.1 · ⭐⭐ The limit is DIRECTLY READABLE — do not infer it

**Measured 2026-08-26, and it replaces the inference this section was first drafted around.** A session
calling `get_session` on **itself** (session_id omitted) gets back, at $0 and with no network of its own:

```
external_metadata.rate_limit_info = {
    "status":          "allowed",        ← the live verdict
    "rateLimitType":   "five_hour",      ← WHICH limit is binding
    "resetsAt":        <unix seconds>,   ← exactly when it clears
    "isUsingOverage":  false             ← whether metered spend has begun
}
```

⛔ **So the governor never guesses, never backs off on a hunch, and never sleeps blind.** It reads
`status` before taking an item, and on a limit it reads `resetsAt` and **schedules the next cycle for
just after it** rather than retrying into a wall. *"Restart work when limits clear"* is therefore not a
heuristic in this design — it is a timestamp.

⚠ **`isUsingOverage` is the one that must be watched, not celebrated.** Overage means the work has
crossed from the flat-rate subscription into **metered dollars**, and CLAUDE.md §5's *"engineering
effort is free"* stops being true at that moment. A cycle that observes `isUsingOverage: true` treats it
as a spend event under §7's trigger 2, not as headroom.

⭐ **Cycles can also be costed after the fact:** `list_sessions` returns per-session
`usage.{cost_usd, input_tokens, output_tokens, cache_read_tokens}`. A receipt records its own session id,
so what a cycle actually cost is recoverable — which is what makes property 3's width dial tunable on
evidence instead of taste.

⚠ **What is still NOT readable is how much of the window REMAINS** — only whether it is currently spent.
So property 3's backoff ladder stays as the fallback for what the reading cannot cover: it degrades on
the one signal that is always available, a cycle that ended without a receipt. An absent reading is not
a reading of absence (CLAUDE.md §4).

### 9.2 · The target — trimcrae's "about 80% of the max budget" (D3)

⭐ **He did not pick a cadence, and that is a better instruction than the ones offered.** A fixed 4-hour
interval is a guess about consumption; **80% is a measurable target**, and §9.1 makes the measurement
available. So the governor is a **controller, not a schedule**:

- **The measurement.** Each receipt records its cycle's session id. `list_sessions` returns that
  session's `usage.cost_usd` and token counts, so the loop knows what a cycle actually consumed —
  it does not estimate.
- **The target.** Keep observed consumption at **~80% of what the window allows**, leaving ~20% as
  trimcrae's interactive headroom. ⛔ **The denominator is not readable yet** (`rate_limit_info` gives
  a verdict, not a quota), so it is **calibrated, not assumed**: the loop records the consumption at
  which `status` last flipped away from `allowed`, and that observed figure becomes the denominator.
  Until a first flip is observed the loop runs at the conservative start point below and **says the
  denominator is UNKNOWN** rather than inventing one.
- **The dials, in order of preference.** Raise or lower **cycle frequency** first (it is smooth), then
  **items per cycle**, and only then **subagent width** — width is the dial that failed catastrophically
  in the incident above, so it moves last and moves down faster than it moves up.
- **The start point**, until a window has been calibrated: a 4-hour cycle, one item at a time, subagent
  width 5. **Deliberately below target** — the controller's first job is to measure the ceiling by
  approaching it, not to find it by hitting it.

⛔ **80% is a target for the CONTROLLER, never a floor for the WORK.** An empty queue means an idle
loop, not make-work to hit a number. §5.2's `advancing_live_work` is the guard: a cycle that consumed
budget and advanced no live route is a failure whatever the utilisation says.

⚠ **One real cost, stated plainly:** the ANTHROPIC_API_KEY lane (already used by the newsletter
summariser) is **metered dollars**, not the flat-rate subscription. CLAUDE.md §5's *"engineering effort
is free"* does **not** extend to it. It stays where it is — a small summarisation fallback — and the
autonomy loop does not run its research on it.

---

## 10 · Self-improvement, free rein, and the one edit it may not make

**★ GRANTED BY trimcrae, 2026-08-26:** *"It should also have the ability to self-improve if it finds
issues in its process. And have free rein to edit the repo and merge to main whenever it wants. Ideally
to make and manage triggers too."*

### 10.1 · The grant, stated plainly

- **Edit anything in this repository, commit, and merge to `main`, unattended.** No approval step. The
  only gate is `./scripts/preflight.sh`, which CLAUDE.md §6 already establishes as the ordinary commit
  loop — *"a merge or push to `main` is the commit loop, NOT publication"*. So this grant adds no new
  ceremony; it removes a permission that was never actually required.
- **Work on `main` and merge early.** CLAUDE.md §7: branch drift is a data-loss bug, and a long-lived
  autonomy branch is exactly the shape that loses work.
- **Manage its own schedule** — §10.2.
- **Change its own process**, including this file, the weights, the cycle contract and the skill —
  §10.3, under the one restriction in §10.4.

### 10.2 · What "manage triggers" can and cannot mean — measured, not assumed

| the loop wants to … | can it | mechanism |
|---|---|---|
| Delete or retime a Routine **it created itself** | ✅ | `delete_trigger` / `update_trigger` — both exercised today on the §2.2 probe, prompt edit included |
| Change the **UI-created driver's** cron or prompt | ⛔ **No** | ★ **Measured 2026-08-26:** `update_trigger` refuses — *"this routine was created via http_api, not by an agent. Agents can only update routines they created."* |
| **Fire** the UI-created driver off-schedule | ⛔ **No** | ★ **Measured 2026-08-26, after `update_trigger` had already been refused and this row still said ✅:** *"fire_trigger: this routine was created via http_api… Agents can only fire routines they created."* |
| **Disable** the UI-created driver | ⚠ only from a session THAT ROUTINE ITSELF FIRED | The server's wording is narrow: *"a routine's own session may still disable itself (enabled=false only)"*. So a loop that detects it is broken can stop itself **from inside a cycle**; no other session can reach it. |

⛔⛔ **SO THE HONEST SUMMARY IS SHORTER THAN THIS TABLE WAS TWICE WRITTEN TO SAY: an agent has NO
control over a UI-created Routine from outside it.** Not the prompt, not the cron, not a manual
fire. Its own fired sessions may disable it and nothing more. Everything in the ✅ rows above applies
only to triggers the loop MINTED ITSELF.

⚠ **This row was wrong twice in one afternoon, in the same direction both times** — first claiming
the loop could rewrite the driver's prompt, then claiming it could fire it. Both were written from
what the tool descriptions imply rather than from a call, and both were corrected only by trying.
CLAUDE.md §4 is the rule that keeps being relearned here: **the tool's own refusal is the
observation; a capability nobody has exercised is UNKNOWN, not available.**
| Create a trigger that wakes a session **already holding** the repo grant | ✅ | a self-bind / `persistent_session_id` trigger — the fired turn runs *inside* that session, so it inherits the repo and every tool. ✅ **Delivery VERIFIED by probe, 2026-08-26 — §10.2b.** |
| Create a **fresh-session** Routine that has the repo | ⛔ **No** | §2.2 — agent-minted lineage carries no `sources`. Unchanged. |

### 10.2b · The self-bind probe — the second half of the trigger result

⭐ **The two trigger experiments of 2026-08-26 are a matched pair, and the contrast IS the finding.**
Both were agent-minted. One delivered nothing; the other delivered everything. The difference is not
permission — it is **whether the fired turn lands in a session that already holds the grant.**

| | fresh-session Routine (§2.2) | self-bind trigger (this probe) |
|---|---|---|
| created by | `create_trigger`, agent | `send_later`, agent |
| where the turn lands | a **new** session, minted with no lineage | **this** session, already repo-attached |
| repo present | ⛔ no `sources` at all | ✅ `git rev-parse` returned the working branch, and the session's own commits were on disk |
| tools | ⛔ no `mcp__github__*` | ✅ full tool surface, unchanged |
| outcome | ran 4 m 03 s, `SUCCEEDED`, **left no artifact** | **fired 15:20:53Z and delivered a real working turn**, carrying its full prompt |

⛔ **And note what "SUCCEEDED" was worth in each case** — it was returned by *both*. In the first it
described four minutes of nothing. **The status field is not the deliverable in either direction**;
§2.2's rule stands and this probe is the second measurement behind it.

⭐⭐ **THIS IS WHAT MAKES §9.1'S RATE-LIMIT RECOVERY REAL RATHER THAN A HOPE.** The design says a cycle
that hits a limit reads `resetsAt` and schedules its own resumption just past it. **That scheduling act
is exactly this probe**, and it is now measured working. So the recovery path is fully specified with
nothing left to assume: *read the limit → read the reset timestamp → self-bind a wake past it → the
turn lands back in a session that still has the repo → continue from the committed ledger.*

★ **Which fixes the division of labour between the two clocks:**

- **Self-bind triggers = WITHIN a cycle's life** — resume after a rate limit, re-check a CI run that is
  still going, follow up on a dispatch. The loop creates these itself, freely (D7).
- **The UI Routine = BETWEEN cycles** — the recurring fresh session that starts each cycle with clean
  context (§4.1). Only trimcrae can create it, once.

⛔ **Do not collapse the two by keeping one long-lived hub session alive as the scheduler.** It would
work, and it would quietly undo §4.1: a session that never ends accumulates context until it dies, and
it inherits every stale belief from the cycle before. **Fresh context between cycles is a feature that
was paid for, not an accident of the platform.**

★ **So the honest shape is narrower than "one seed, then the loop owns the schedule", and that
earlier phrasing was wrong.** ⛔ *Superseded, retained: "Everything after that — retiming it,
rewriting its prompt as the contract improves, retiring it — is the loop's."* **It is not.** The UI
Routine is trimcrae's object: the loop may fire it, and may DISABLE it, and may create and manage
its own self-bind triggers freely — but **retiming or rewriting the driver is a human edit, every
time.**

⭐ **Which changes where the cycle contract must live, and the design already had this right by
accident.** Because the driver's prompt cannot be revised by the loop, the prompt must stay a thin
TRIGGER and the contract must live in `.claude/skills/research-loop/SKILL.md` — a file in the
repository, which the loop CAN edit. **A contract written into the Routine prompt would be frozen at
whatever trimcrae last pasted.** So: prompt says "read the skill and follow it"; the skill is where
improvement lands.

⚠ **And the fired session's tool surface is narrower than an interactive one's** — measured on both
new Routines: `Bash, Read, Write, Edit, Glob, Grep, WebFetch, WebSearch`, with **no `Skill` and no
`Task`**. So the prompt must name the skill's PATH as a fallback (`cat
.claude/skills/research-loop/SKILL.md`), and §4.1's parallel-subagent shape may simply be
unavailable to a driver cycle. One item per cycle is the default posture anyway, so this costs
wall-clock, not correctness.

⛔ **Every trigger the loop creates carries its cycle id in the name**, so an orphan is attributable to
the cycle that made it. This repository has already paid twice for orphaned pollers trimcrae had to
spot himself (CLAUDE.md §6). **And a retrospective cycle reaps its own orphans** — a trigger whose
cycle is long finished and whose entry is `done` is deleted, not left firing.

### 10.3 · Where self-improvement comes FROM — receipts, never introspection

⛔ **A loop asked to "reflect on its process" will invent problems, because producing a finding looks
like working.** This one may only improve on **recorded friction**:

- **Every cycle that hits friction files a `kind: process_defect` entry** — with the evidence, not the
  impression. A retry that was needed, a gate that failed for an unrelated reason, an entry whose
  `what` was unactionable, a skill that did not say the thing the cycle needed.
- **A retrospective cycle** (every Nth, and after any §5.2 condition goes red) reads the last N
  receipts plus `health.json` and looks for *patterns*: the same failure twice, an entry stuck across
  cycles, a clamp firing constantly, escalations that turned out not to need him.
- **Its output is a change with a diff, or nothing.** ⭐ **"Nothing to improve this round" is a valid
  and expected retrospective** — and a retrospective that always finds something is itself a defect.

⛔ **A process change with no receipt behind it is a redesign, not an improvement.** CLAUDE.md §4: the
diagnostic comes before the explanation, and *"probably"* is not a cause.

### 10.4 · ⛔⛔ THE ONE THING IT MAY NOT DO — MOVE ITS OWN GOALPOSTS

**Improving the mechanism and making your own success easier are both edits, and only one is honest.**
★ **The test is a single question, and it is answerable: *does this change make it easier for the loop
to report success?*** If yes, it is not an improvement, whatever else is true about it.

| class | examples | rule |
|---|---|---|
| **Free, unlogged** | fix a bug, add a check, refactor, sharpen a prompt, correct a stale doc, add or retire a ledger entry, retime a Routine | Just do it. This is the bulk of self-improvement and it needs no ceremony. |
| **Free, but DECLARED** | `priority-weights.json` · the six clauses of §6.1 · `publication-authority.json` · CLAUDE.md, AGENTS.md or this file's rules · any §5.2 health condition · deleting or weakening any test | Allowed unattended — **and appended to the amendment log (§10.5) and carried in the Friday digest.** These are the edits that change what "doing well" MEANS, so they are never silent. |
| **⛔ Refused** | see the invariant below | Filed as a proposal and escalated (§7 trigger 3), never applied by that cycle. |

⛔⛔ **THE ANTI-GAMING INVARIANT, and it is mechanically checkable:**

> **A bar may not be changed by the cycle that the bar just blocked.**

The receipt records what blocked the cycle; the commit records what the cycle changed. **A cycle that
does both is the failure mode**, and it is the one that ends with a paper published because the
standard moved rather than because the work got better. A later cycle, with the blockage no longer in
front of it, may make the same change — declared, per the table above.

⛔ **Two more, absolute:** never weaken a guard test to make a change pass — mutation-test the guard
instead (`paper-hardening`); and never edit or remove an entry from the amendment log.

### 10.5 · The amendment log — `research/autonomy/amendments.jsonl`

Append-only. One record per declared change:

```
{ cycle_id, utc, path, what_changed, why (the receipt or defect entry id),
  old_value, new_value,
  self_serving_check   ← "did this cycle's own work get easier?" ANSWERED, not assumed.
                          An honest "yes, and here is why that is still correct" is fine.
                          An unanswered field is a red health condition. }
```

★ **This is the file trimcrae reads to tell improvement from drift**, and it is the reason the grant in
§10.1 can be as wide as it is: the loop may change anything, and **cannot change anything quietly.**

---

## 11 · Build order

Each phase is independently useful and ends in a committed, checkable artifact. **Phases 1–2 need no
new permission from anyone.**

| phase | build | done when |
|---|---|---|
| **1 ✅ BUILT · See the work** | `research-ledger.json` seeded from the graph; `priority.py` + `priority-weights.json`; the three hard clamps of §3.2 with a test each | The ranked queue is committed and its top item is one a human would also have picked |
| **2 · Prove one cycle by hand** | Run §4.2's ten steps manually, end to end, on the top item; write the first receipt | A receipt exists with a real `route_advanced` |
| **3 ✅ BUILT · The loop's own health** | `autonomy-tick.yml` + `health.json` + the seven §5.2 conditions; `fleet_armed` no-work-no-commit discipline | A deliberately skipped cycle turns `cycle_delivering` red |
| **4 ✅ BUILT · The skill** | `.claude/skills/research-loop/SKILL.md` — cycle contract, session shapes, stop conditions, and **pointers only** to the six existing skills | A fresh session given only the cycle prompt completes a cycle correctly |
| **5 ✅ BUILT (awaiting his click) · Hand trimcrae the clock** | The driver + escalation Routine prompts, written out for him to paste into the claude.ai Routines UI **with the repo attached and the model pinned** (§2.2) | Two consecutive Routine-fired cycles deliver receipts — read the receipts, never the fire records |
| **6 ✅ BUILT · The publication ladder** | `venue-fit.json`; the §6.1 bar as a checkable script; escalation trigger 1 | A paper is correctly escalated rather than posted |
| **7 ✅ BUILT · Authority** | The six §6.1 clauses each as a script returning a boolean, then `publication-authority.json` + the AGENTS.md / CLAUDE.md §3 amendment in **one** commit | A paper passing all six posts unattended and notifies; a paper failing any one escalates instead. ⛔ The clauses ship BEFORE the grant — a bar-scoped grant with an ungated bar is the grant with no bar |
| **8 ✅ BUILT · The watches** | §8.1's `venue` trigger kind; §8.2's `regrade` entries; layer 1 absorbed into the driver | A parked route's `revival_trigger` is re-tested on schedule and the re-test is visible when it stops |
| **9 ✅ BUILT · Self-improvement** | `amendments.jsonl`; the `process_defect` entry kind; the retrospective cycle; the §10.4 anti-gaming check as a **script** that reads a receipt and a diff together; orphan-trigger reaping | A cycle that tries to change a bar which blocked it is refused by the check and files a proposal instead — **proved by a deliberate attempt, not by assertion** |

⭐ **Phase 9's check is the one that must exist before the loop runs unattended for long.** Phases 1–8
make it work; phase 9 is what keeps it working *on the problem it was pointed at*. Build it early if
anything slips.

⚠ **And the whole order is now the loop's to revise** (D5/D6). If a cycle finds a better order, it
changes this table and logs the amendment — this is a plan, not a contract with the future.

---

## 12 · Decisions on record — trimcrae's, and the loop must not infer them

**★ ALL SEVEN WERE ANSWERED BY trimcrae ON 2026-08-26** — D1–D4 as answers to a question, D5–D7
unprompted in his own words. Recorded verbatim because each is a standing authorisation the loop will
act on, and CLAUDE.md §3 requires every grant be traceable to him.

| # | decision | his answer | consequence |
|---|---|---|---|
| **D1** | Standing aiXiv posting authority | **"Broad: any paper meeting the bar"** | §6.3 is rewritten to a bar-scoped grant. ⚠ **This is a deliberate amendment of CLAUDE.md §3 and AGENTS.md** — see §6.3. |
| **D2** | Who creates the Routines | **"Yes — give me the prompts"** | Phase 5 delivers pasteable prompts; he creates them once in the UI. |
| **D3** | Budget the loop may hold | **"Like 80% of the max budget"** | ⭐ Not one of the offered cadences — so the governor targets **measured utilisation**, not a fixed interval. §9.2. |
| **D4** | Journal escalation timing | **"Immediately"** | Escalation trigger 1 fires on the spot, not into the Friday digest. |
| **D5** | Self-improvement | **"the ability to self-improve if it finds issues in its process"** | §10.3 — improvement is sourced from recorded friction, never from introspection. |
| **D6** | Repo and `main` | **"free rein to edit the repo and merge to main whenever it wants"** | §10.1. Adds no ceremony: CLAUDE.md §6 already holds that a merge to `main` is the commit loop, gated by preflight alone. |
| **D7** | Triggers | **"Ideally to make and manage triggers too"** | §10.2 — granted for everything except minting a fresh-session Routine, which the platform does not permit. One UI seed, then the loop owns the schedule. |

⚠ **D1 carries a real risk and it is stated rather than smoothed over.** A bar-scoped grant means the
first paper the loop judges ready is posted under trimcrae's name and ORCID **without him seeing it
first**. That is precisely the inference CLAUDE.md §3 was written to forbid, and he has now decided
otherwise for aiXiv specifically. The risk is bounded by three things that did **not** change: the bar
in §6.1 is a conjunction of six machine-checkable clauses, the grant covers **aiXiv only**, and every
journal submission still escalates (D4). ⛔ **If any one of those three is ever relaxed, this decision
must be put to him again — it was granted against that backdrop, not in general.**

---

## 13 · What this design refuses to do

- **Grant itself an authority.** ⚠ *Amended 2026-08-26 (D1): the loop MAY now post to aiXiv any paper
  clearing §6.1's six clauses, because trimcrae granted that — and the grant is bounded by the backdrop
  recorded in `granted_against`.* What is unchanged and absolute: it may not extend that grant to
  another venue, widen it, or lower a clause to fit a paper through. **When the only way to satisfy a
  goal is an act nobody authorised, the goal yields** — CLAUDE.md §3.
- **Treat a rating as quality.** §6.1.
- **Write a negative because the live route is hard.** §3.2 clamp 1, and §5.2's `advancing_live_work`.
- **Report a fire as a delivery.** §2.2.
- **Say "probably" about a failure.** CLAUDE.md §4 — a cycle that cannot diagnose a failure records
  `UNKNOWN` and queues the diagnostic as its own entry.
- **Go quiet when it is broken.** Escalation trigger 4.
- **Change a bar in the cycle that bar just blocked.** §10.4. The wide edit grant of §10.1 is survivable
  *because* of this one line: the loop may change anything, and may not change it to get past the thing
  standing in front of it right now.
- **Change quietly what "doing well" means.** §10.5 — an edit to the weights, the bar, the authority or
  a health condition that is not in the amendment log is the defect, however good the edit was.
