---
id: DOC-METHOD-WATCH-LLM-METRICS
title: Which LLM metrics align with this program — a graded answer
level: L3
kind: memo
status: live
canonical_for: [LLM/agent metric selection for this loop, the anti-aligned metric list]
purpose: >
  Answer one question trimcrae asked on 2026-09-03 — "what LLM metrics best align with what we're
  trying to do in this repo?" — as a durable reading rather than a conversation. It ranks the
  external benchmarks by how much of this program's actual work they measure, names the internal
  metrics that are the load-bearing half, and lists the metrics this repository must keep refusing.
scope: >
  Metric SELECTION only. It owns no mechanism and computes nothing. It does not restate the
  BixBench3 readings (`method-watch-bixbench3-calibration.md`), the aiXiv Rating findings
  (`.claude/skills/aixiv-submission/SKILL.md`), the publication clauses (`autonomy/publish_bar.py`),
  the health board's conditions (`autonomy/health.py`) or any capability trigger
  (`method-watch.md`). It contains no EMC or NR4A3 science.
audience: [maintainers, autonomous research agents]
date: 2026-09-03
last_verified: 2026-09-03
related: [DOC-METHOD-WATCH, DOC-METHOD-WATCH-BIXBENCH3, DOC-METHOD-WATCH-AUTONOMY-PRIOR-ART, DOC-EMC-AUTONOMY-ARCHITECTURE]
---

# Which LLM metrics align with this program — a graded answer

**Asked by trimcrae, 2026-09-03.** Answered from this repository's own instruments plus a dated
external reading taken the same day.

---

## 0 · The short answer

**No external LLM metric can tell us this loop is working, and one of them can tell us where the
model we run is weakest.** Those are different jobs and the repository keeps conflating them.

The best-aligned external reading already exists here and is graded:
[`method-watch-bixbench3-calibration.md`](method-watch-bixbench3-calibration.md). Its transferable
part was never the leaderboard position — it is the **grading design** and the **failure-mode
vocabulary**, both of which that memo §5 already identified as the thing to borrow, and both of
which are still sitting in the ledger untaken (`AUT-BIX-001`, `AUT-BIX-002`).

The load-bearing metrics are internal and five of them exist in some form. ⛔ **The one that measures
distance to the objective is reachable from no code path** (§3). Its sibling looks unwired and is not
— that is a recorded decision, and §3.2 takes the reading the decision asked for.

⛔⛔ **And the finding that outranks the whole question is §3a: the graders this repository already
has do not run.**

---

## 1 · Three different questions wear the phrase "LLM metric"

| sense | what it grades | who owns it here | can it grade this loop? |
|---|---|---|---|
| **A — leaderboard** | the model we run, against other models, on somebody's task set | this memo | **No.** It grades a model on a supplied method. |
| **B — self-grading** | our own agent output, using an external grading *design* | this memo | **Yes — this is the only sense that can.** |
| **C — scientific model accuracy** | co-folders, structure predictors, ASO efficacy predictors | [`method-watch.md`](method-watch.md)'s trigger table | Different question. Not this memo. |

⛔ **Sense C is not what this memo is about** and must not be folded into it. A structure
predictor's accuracy gates a research route; it says nothing about whether an agent executed the
route honestly.

---

## 2 · Sense A — the external benchmarks, ranked by how much of our work they contain

### 2.1 · BixBench3 — first by construction, and already read

Closest thing that exists to an external measurement of what this loop does: an agent executing a
multi-step computational-biology pipeline from raw data to programmatically graded artifacts. Graded
in full in [`method-watch-bixbench3-calibration.md`](method-watch-bixbench3-calibration.md) on
2026-08-27; every number lives there and is not restated here.

⭐ **The aligned reading is not the topline score.** Three things in it are about us:

1. **The failure-mode tag count**, which correlated with task score far more strongly than any
   capability proxy did. It is a *behavioural* metric computable from a transcript, which means it
   is computable from our receipts.
2. **The output-format-contract axis**, which is where the model this repository runs measurably
   loses, and which is exactly the axis a repository built on generated artifacts is most exposed on.
3. **The depth and working-set findings**, which confirm two rules CLAUDE.md already carries rather
   than adding new ones.

### 2.2 · Long-horizon agentic instruction-following — second, and newly relevant

⚠ **SEARCH-grade, taken 2026-09-03. The papers were NOT fetched and their identifiers are
deliberately not written here** (CLAUDE.md §7: never write an identifier from recollection, and a
search snippet is not a fetch product). Titles only, and nothing below may be quoted in a manuscript
until somebody reads the source.

Three families surfaced. **None was graded in this repository's 2026-08-27 calibration**, which read
a single paper:

- *HANDBOOK.md: A Benchmark for Long-Context Agentic Instruction Following* — reported June 2026,
  with no evaluated model clearing roughly a quarter of tasks on strict single-attempt scoring.
- *Long-Horizon Terminal-Bench* — hundreds of dependent actions in a container, graded by a hidden
  verifier paying continuous partial credit.
- *Beyond pass@1: A Reliability Science Framework for Long-Horizon LLM Agents*, and *The Long-Horizon
  Task Mirage? Diagnosing Where and Why Agentic Systems Break*.

★ **Why this family aligns better than a general capability leaderboard.** Our unit of work is not a
question with an answer. It is a hardening cycle that has run past thirty rounds on one paper, and a
research loop whose failures are named in CLAUDE.md as *declaring a half-finished job done*, *losing
track of an earlier decision*, and *quietly drifting from the goal*. That is this family's stated
subject, and it is nobody else's.

⛔ **And it is the family whose stale reading would hurt most.** CLAUDE.md §4 says a remembered AI
figure understates. These benchmarks are months old and their numbers move; anything cited from them
needs a live read at the time of citing.

### 2.3 · Research-integrity and citation-grounding — third, and already load-bearing

Also SEARCH-grade, same caveat: *SciIntBench*, *SciIntegrity-Bench*, *CiteCheck*, *MisCiteBench*,
and a fabricated-citation taxonomy coded from a 2025 conference corpus.

**One of these is already enforced here and nobody framed it as a metric.** SciIntegrity-Bench's
completion-pressure finding is why every blind-seat prompt in
[`paper-hardening`](../.claude/skills/paper-hardening/SKILL.md) ends by stating that no findings is a
complete answer, and why four pressure shapes are banned from a seat brief. That is an external LLM
metric already converted into a control.

★ **This family maps onto the golden rule** (CLAUDE.md §7: never fabricate medical facts, stats,
citations or patient data) more directly than any capability benchmark does, and this repository
already knows claim STRENGTH and citation PROVENANCE are orthogonal — the two linters that enforce
them are separate for that reason.

### 2.4 · The ceiling on all of Sense A

Every benchmark above supplies the method and grades the execution. BixBench3's authors draw that
line themselves, in the sentence quoted in
[`method-watch-bixbench3-calibration.md`](method-watch-bixbench3-calibration.md) §3. So the honest
statement is:

> **An external LLM metric can tell us which model to run and where it is weak. It cannot tell us
> that this loop is producing science, because no benchmark contains the part where the question is
> chosen.**

`TRG-AUTONOMOUS-RESEARCH-AGENT` states the same exclusion in its own trigger text, and BixBench3 was
recorded as a graded non-fire against it. That precedent holds for every benchmark named in §2.2 and
§2.3: **none of them fire it either.**

---

## 3 · Sense B — the five internal metrics that actually align, and their state today

| # | metric | what it would measure | exists? | wired to anything? |
|---|---|---|---|---|
| 1 | **Artifact-contract pass rate** | fraction of agent-written artifacts a gate would reject if emitted with a renamed key, a missing required field, or right values under the wrong schema | **no** — filed as `AUT-BIX-001` | n/a, still `queued` |
| 2 | **Failure-mode tag rate** | BixBench3's ten-tag closed vocabulary applied to our own receipts and transcripts | **no** — filed as `AUT-BIX-002` | n/a, still `queued` |
| 3 | **Derivation-depth pass rate** | our claim DAG's pass rate stratified by depth, since external grading collapses at depth 3+ | **partly** — `lint_consistency.py` checks derivations but does not stratify | gated, unstratified |
| 4 | **Learning rate** | ledger rows *transitioning into* a closed state per window, split by whether the closure served the loop's own upkeep | **yes** — [`learning_rate.py`](autonomy/learning_rate.py) | **reports on demand, BY DECISION** — see §3.1 |
| 5 | **Goal distance** | clauses passed against clauses required, recomputed at the pinned commit | **yes** — [`goal_progress.py`](autonomy/goal_progress.py) | ⛔ **no automated caller.** [`goals.json`](autonomy/goals.json) names the command; no hook, gate or workflow runs it. |

★★ **Rows 4 and 5 are the answer to the question as asked.** Row 5 is the only instrument here that
measures distance to the objective; [`goals.json`](autonomy/goals.json) exists precisely because a
full session of warranted work once moved the bar not at all and nothing could say so. Row 4 is the
only instrument that distinguishes *the loop did work* from *the loop did work on itself* — a
distinction it was written for after nine cycles closed six rows of which five were the loop's own
upkeep.

### 3.1 · ⛔ One of them is a decision, and this memo nearly recorded it as a defect

**`learning_rate.py` is unwired ON PURPOSE, and the reasoning is recorded rather than assumed.** The
ledger row that built it settled the question on 2026-08-28 in the same breath as wiring its sibling:
`queue_view`'s already-landed check went into the turn-end hook, and the learning-rate verdict
deliberately did not, because it is a **portfolio judgement** — *"you have only been working on
yourself for a window"* — and a gate that blocks a commit on that would block the very
self-maintenance cycles that repair the loop. Its declared home is a digest or a human's read.

★ **So the honest finding is narrower and more useful than "wire it".** The decision carries a named
revisit condition — *revisit if the distribution stays concentrated across several windows; one window
is not a trajectory* — and **that reading had never been taken.** The open work was running the
detector across several windows and checking the condition, not overturning the decision. §3.2 takes
it.

### 3.2 · ⭐ The revisit reading, taken 2026-09-03 — the decision stands

The open work §3.1 names is the multi-window reading, so this memo takes it rather than filing it.
Four windows, `python3 research/autonomy/learning_rate.py --hours <N> --json`:

| window | verdict | distinct routes | self-route share |
|---:|---|---:|---:|
| 16 h | LEARNING | 5 | — |
| 32 h | LEARNING | 14 | — |
| 72 h | LEARNING | 18 | — |
| 168 h | LEARNING | 36 | **0.47** |

**The revisit condition is not met.** No window reads CONCENTRATED, and the week's self-route share
sits well under the threshold that would trigger one. **The 2026-08-28 decision to leave this
detector a report rather than a gate is therefore standing on evidence taken today, not on
inheritance.**

⚠ **Two honest caveats.** The clone is shallow (`shallow_clone: true`), though the horizon falls
outside every window read, so none of these four is censored. And **nearly half of the week's
closures still served the loop's own upkeep** — under the bar, and not a number to look away from.

⚠ **A reading, not a constant.** Re-run it; do not quote this table.

★★ **Row 5 is the one with no defence.** `goal_progress.py` is correct, committed, tested and
reachable from no hook, gate or workflow; only [`goals.json`](autonomy/goals.json)'s prose names the
command. That is the repository's standard failure shape again — `subagent_width` governed nothing
until `health.py` measured it, and the version cap was declared in JSON and read by no code while
eleven versions shipped. **A metric nothing calls is not a metric.**

---

## 3a · The finding that outranks the metric choice

⛔⛔ **This repository's metric problem is not selection. It is that the graders do not run.** Three
readings taken 2026-09-03, each a census rather than a constant — **re-take them rather than quoting
these**:

1. **The capability scanners fire and the grading queue does not drain.** Every scan hit lands in a
   `pending_signals[]` array on a `TECH-*` row in
   [`technologies.json`](../systems/graph/technologies.json), which
   [`systems/MAINTENANCE.md`](../systems/MAINTENANCE.md) §3 assigns to a weekly human grading pass.
   Counted today, the graded fraction of that queue is **one signal**, and the single graded row is
   the BixBench3 non-fire. The largest ungraded backlog belongs to `TECH-AUTONOMOUS-AGENT` — the
   technology row that is *about this loop*.
   ```
   python3 - <<'EOF'
   import json; g=json.load(open('systems/graph/technologies.json'))
   rows=g['technologies'] if isinstance(g,dict) else g
   tot=sum(len(t.get('pending_signals') or []) for t in rows)
   graded=sum(1 for t in rows for s in (t.get('pending_signals') or []) if s.get('verdict') or s.get('graded'))
   print(tot,'signals;',graded,'graded')
   EOF
   ```
2. **The forecast re-grade has never run as a pass.** Most rows in
   [`forecasts.json`](../systems/graph/forecasts.json) still carry their seeding `last_reviewed`
   date; the handful that moved did so as a side effect of other work.
3. **⛔ And the check meant to catch that CANNOT FIRE.** `render` in
   [`systems_check.py`](../systems/systems_check.py) computes forecast staleness against a
   **hardcoded date literal**, not a rolling window:
   ```python
   stale = [c["id"] for c in g["forecasts"] if c.get("last_reviewed", "") < "2026-02-05"]
   ```
   Every `last_reviewed` in the register is later than that literal, so
   [`roadmap-5yr.md`](../systems/views/roadmap-5yr.md) prints *"Every forecast has been reviewed
   within the last two quarters"* unconditionally, and will keep printing it however long nobody
   re-grades. The same view's prose two sections above claims the opposite property — *"one older
   than two quarters is flagged rather than silently trusted"*.
   ⚠ **The fix is not a one-line swap and should not be made as one.** A wall-clock cutoff makes a
   GENERATED view change on a day nobody edited a source file, which reddens the generated-artifact
   gate for no author — the shape CLAUDE.md §6 calls a gate people learn to re-run. The freshness
   *verdict* belongs in a check-time finding; only the review dates belong in the view. **Raised, not
   taken.**

★ **Read §3's table against this.** Adopting a new metric while the existing graders sit unrun buys
nothing, and this repository has now recorded the same shape four times: `subagent_width`, the
version cap, `goal_progress.py` (§3), and a staleness literal that can never fire.

---

## 4 · Metrics this repository must keep refusing

| ⛔ metric | why it is anti-aligned | already refused? |
|---|---|---|
| **aiXiv Rating** | written by an unauthenticated endpoint; a target rating is reachable by posting your own review. Findings in [`aixiv-submission`](../.claude/skills/aixiv-submission/SKILL.md) | **yes** — named in `priority-weights.json` `_forbidden_inputs` |
| **Per-round blocker count as convergence** | does not descend to a floor; a round's count tracks how many new lenses it introduced, not defects remaining. Evidence in [`paper-hardening`](../.claude/skills/paper-hardening/SKILL.md) §8 | **yes** — convergence reads blockers on the *posted commit*, not a trend |
| **A readability score as a target** | gating on a mean is an instruction to shorten sentences by any means available, including deleting the difficult truth. trimcrae set this line himself | **yes** — `lint_readability --report` is advisory; only a hard ceiling and a caution-loss check gate |
| **Turns, tokens or agent-hours as productivity** | the only external datum points the other way, and CLAUDE.md §5's "engineering effort is free" covers writing code, not spending turns. See [`method-watch-bixbench3-calibration.md`](method-watch-bixbench3-calibration.md) §5 item 2 | **partly** — stated in that memo, enforced by no instrument |
| **Any benchmark topline as evidence of autonomy** | `TRG-AUTONOMOUS-RESEARCH-AGENT` excludes benchmark scores by its own text | **yes** — recorded as a graded non-fire |

---

## 5 · What this changes

1. **⭐⭐ Nothing new should be adopted before the existing graders run.** §3a is the answer that
   outranks the metric list. Three acts, each smaller than importing any external metric: give
   `goal_progress.py` an automated caller, drain the signal-grading queue, and repair the staleness
   check. ⛔ **Wiring `learning_rate.py` is NOT on that list** — §3.1; what is open there is taking
   its multi-window reading against the revisit condition.
2. **⭐ `AUT-BIX-001` and `AUT-BIX-002` are the correct next metric work and are both still queued**
   seven days after filing. They were filed as the answer to this question before it was asked.
   ⚠ **And neither is near the front of the queue.** A census on 2026-09-03 put `AUT-BIX-001` at
   rank 82 of 172 scored queued rows — mid-pack, not starved and not prioritised. ⛔ **Why it scores
   there is UNEXAMINED and is not asserted here.** Its `serves.route` is `null` (the S51 remap: the
   loop's own upkeep is not a treatment route), which is a hypothesis about the scorer and not a
   diagnosis — CLAUDE.md §4 wants the discriminating observation before the explanation, and nobody
   has taken it. **Re-take the rank rather than quoting it; it is a census, not a constant.**
3. **The §2.2 family is a new watch item, not a new metric.** Long-horizon reliability benchmarks did
   not exist in a usable form at the last calibration and their subject is this loop's named failure
   modes. What they justify is a **re-read on a schedule**, not a claim.
4. **The three unmatched failure modes stay unmatched.** Input misinterpretation, wrong method
   substitution and method misconfiguration have no dated incident here, and
   [`method-watch-bixbench3-calibration.md`](method-watch-bixbench3-calibration.md) §4 already gives
   the non-benign reading: an operational failure is loud and a method misconfiguration is silent.
   **No metric proposed in this memo would catch one either.** That is the honest gap.

## 6 · Provenance limits of this memo

- §2.1 rests on a paper read in full; its numbers live in the calibration memo.
- **§2.2 and §2.3 are SEARCH-grade**: web-search result summaries taken 2026-09-03, sources not
  fetched, identifiers deliberately not written. They are sufficient to say *this family exists and
  is relevant* and insufficient for any number or any manuscript sentence.
- §3, §3a and §4 are read from this repository's committed code and artifacts. The §3a counts are
  censuses taken 2026-09-03 with the command shown; re-take them rather than quoting them.
