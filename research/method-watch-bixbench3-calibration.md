---
id: DOC-METHOD-WATCH-BIXBENCH3
title: BixBench3 — the first external calibration of the thing this loop does
level: L3
kind: memo
status: live
canonical_for: [external agent-execution benchmark readings, BixBench3 grading design, agent failure-mode vocabulary]
purpose: >
  Grade one preprint — BixBench3 (arXiv:2608.25286v1, 26 Aug 2026) — against this program's own
  operation, and say what it changes here. It is the closest thing that exists to an external
  measurement of what this repository already does every day: an LLM agent executing a multi-step
  computational-biology pipeline from raw data to graded artifacts.
scope: >
  A dated reading of ONE paper. It owns no mechanism. It does not restate the autonomy architecture
  (`manuscripts/program/emc-autonomy-architecture.md`), the prior-art scan
  (`method-watch-autonomy-prior-art.md`), the capability trigger table (`method-watch.md`), or any
  cost figure (`compute/pricing.md`). It contains NO EMC or NR4A3 science, because the paper contains
  none.
audience: [maintainers, autonomous research agents]
date: 2026-08-27
last_verified: 2026-08-27
related: [DOC-METHOD-WATCH, DOC-METHOD-WATCH-AUTONOMY-PRIOR-ART, DOC-EMC-AUTONOMY-ARCHITECTURE]
---

# BixBench3 — the first external calibration of the thing this loop does

**Source.** Koch Z, Wassie AT, Valdes-Aleman J, Lee J, Hinks MM, Rodriques SG, White AD, Laurent JM.
*BixBench3: Benchmarking AI agents on research-study-scale computational biology tasks.*
Edison Scientific, Inc. **arXiv:2608.25286v1 [cs.AI], 26 Aug 2026** (preprint dated 27 Aug 2026).
Read in full from the PDF supplied by trimcrae, 2026-08-27 9:36 AM ET. Successor to BixBench, which
[`method-watch-autonomy-prior-art.md`](method-watch-autonomy-prior-art.md) §2 item 3 already lists
among the external benchmarks this loop is not measured against.

⛔ **This paper contains no EMC, NR4A3, sarcoma or fusion-oncoprotein content, and opens no route.**
Under CLAUDE.md §0 it is not a research lead. It is an **operating-environment reading**: a dated,
quantified, external measurement of the capability this program *is built out of*, which CLAUDE.md §4
says is the class of fact we are most likely to hold stale and to hold stale in the understating
direction.

---

## 1 · What was measured

An agent gets a research objective, method guidance derived from a published paper's Methods (tools,
parameters, contrasts, filters — but never the results), raw public data, and an exact output contract
naming each artifact's path and format. It must produce those artifacts. Each is graded
**programmatically** against the corresponding artifact from the original paper.

| dimension | reading |
|---|---|
| tasks / source papers | 20 |
| graded artifacts | 138 (median 5 per task, min 4, max 14) |
| models × runs × evaluations | 13 frontier models, 260 completed runs, 1,794 graded artifact evaluations |
| raw input per task | mean 67 GB, range 7–241 GB |
| host | GCP `n2-standard-32` — 32 vCPU, 128 GB RAM, 500 GB disk, **no GPU** |
| caps | 24 h wall clock, 5,000 messages, no token cap; Inspect AI ReAct loop, auto-compaction at 90% context |
| tools the agent had | persistent bash session, python, text editor, an adjudicated `request_web_access`, submit |

**Grading design, which is the transferable part.** Each artifact gets one or more of four metrics —
row/column identifier recovery (F1), numerical agreement (Lin's CCC, chosen over Pearson *because it
penalises a scale or offset change*), categorical-label agreement (macro F1), genomic-interval
recovery (overlap F1). The metrics are **multiplied** into one artifact score. Missing, empty or
unreadable files score zero. An artifact **passes at ≥ 0.80**, and that threshold is not arbitrary:
domain experts rated 25 agent-produced artifacts 1–5 on whether the main biological meaning survived,
ratings ≥ 4 averaged an artifact score of 0.80, and expert rating vs. artifact score correlated at
Spearman ρ = 0.76 (p = 1.3 × 10⁻⁵). A task's score is the fraction of its artifacts that pass.

## 2 · The readings

**Topline.** GPT 5.6 Sol 0.48 · Kimi K3 0.47 · GLM 5.2 0.46 · Claude Opus 4.8 0.46 ·
**Claude Opus 5 0.406 (7th)**. Gemini 3.1 Flash Lite 0.00 is the floor.

**⭐ The Opus 5 result is the one that is about us, and it is not a science result.** Opus 5 "scored
highly on most tasks" and was dragged to 7th by violating the artifact **output-format contract** on
tasks 5, 19 and 20 — on task 5 it replaced the contract's column names (`col0_gene_id`, `col0_tpm`)
with labels of its own (`Col-0`, `Ct-1`), so the grader read those columns as missing. The authors
call these "instruction-following errors that most other models did not make". Excluding those three
tasks from **every** model's average, Opus 5 ranks **second at 0.455**, behind GPT 5.6 Sol's 0.458.
**This repository runs Opus 5.** Its measured, externally-observed weak axis is emitting an artifact
in exactly the schema that was demanded — not choosing the analysis, not reasoning about the biology.

**Depth kills.** Mean binary artifact pass score by dependency depth: **0.30** at depth 1 (56
artifacts, direct from raw data), **0.44** at depth 2 (44), **0.24** at depth 3+ (38). Six of the 13
models fell significantly at depth 3+.

**Scale kills harder.** Mean model–task score by raw-data size: **0.37** under 50 GB, **0.34** at
50–100 GB, **0.10** above 100 GB.

**Cost and effort.** Per task attempt, averaged: **6.8 h, 102 M tokens, $43, 695 model turns**. The
longest attempt: 24 h, 1.07 B tokens, $525. Across models the per-task cost spanned 367-fold,
$0.35 to $129.14. Performance peaked at **intermediate** token use, run time and turns: models
scoring ≥ 0.40 used 28–179 M tokens and ~271–1,149 turns, against 8–285 M tokens and ~107–1,894 turns
for models below 0.40.

**Failure-mode tags predict the score.** An LLM judge assigned each model–task attempt 0–10 tags from
a closed ten-item vocabulary, with concrete evidence required per tag. Total tag count vs. mean task
score: **Spearman ρ = −0.92, p = 9.9 × 10⁻⁶** — 31–51 tags for the top three models, 102–117 for the
bottom two. **Premature termination** (~2.0×) and **repetitive retry loop** (~2.2×) were the most
enriched in the lowest score quantile; among the 65 attempts in the *highest* quantile, exactly one
terminated prematurely and **none** entered a retry loop.

**UNKNOWN, and left as such.** Claude Haiku 4.5's *score* is reported only in Figure 3A and is not in
the extracted text. The paper says Haiku 4.5, GPT 5.6 Sol and Gemini 3.1 Flash Lite were Pareto-optimal
on all four cost/efficiency frontiers — but Gemini 3.1 Flash Lite scored **0.00**, so Pareto-optimality
here includes "cheapest at any accuracy" and is **not** evidence that Haiku is accurate. Do not cite
Haiku's frontier membership as a quality claim.

## 3 · Trigger verdict — it does NOT fire, by design

`TRG-AUTONOMOUS-RESEARCH-AGENT` states its own exclusion: *"Not 'an agent wrote code' and **not a
single-task benchmark score**: a demonstrated end-to-end research thread — planning, running,
checking, revising — whose provenance a reviewer accepted."* Its `on_fire` note repeats it: *"Read
whether the claim is about a benchmark score or about a thread that was actually carried and reviewed.
Only the second is evidence here."*

**BixBench3 is a benchmark. It does not fire.** Recorded as a graded non-fire in
[`technologies.json`](../systems/graph/technologies.json) → `TECH-AUTONOMOUS-AGENT`.

⭐ **But it is exactly the right evidence for that technology's `current_state: partially_landed`**,
whose schema demands the record *say which half landed*. Before today that row's evidence was
internal and uncalibrated — "agents already execute this repository's compute lanes". BixBench3 puts
an external number and a clean split on it, and the authors draw the line themselves:

> "because each BixBench3 task supplies an explicit methodological plan, success here means agents can
> begin to execute a specified analysis pipeline – **not** that they can decide which questions or
> analyses are worth pursuing."

That is this program's operating model stated by someone else: trimcrae chooses the question, the
agent executes. It is also the honest ceiling on any autonomy claim this repository makes.

## 4 · The failure-mode vocabulary, against this repository's own incident record

BixBench3's ten closed tags, and whether CLAUDE.md already carries a **dated, measured incident** of
that shape. ⚠ These are analogies across different work — their failures are in bioinformatics
pipelines, ours in repository and compute operations — so read the column as *same failure shape*,
never as *same measurement*.

| BixBench3 failure mode | dated incident in this repository |
|---|---|
| **Repetitive retry loop** — retried substantially the same failing command without diagnosis | ✅ `pgrep -f`/`pkill -f` matching the shell that runs them, **three times in one session, 2026-08-26**; cost two orphan poll loops trimcrae had to spot and one killed gate run (CLAUDE.md §6) |
| **Premature termination** — stopped before writing all required outputs, or declared completion early | ✅ bare shell `&` instead of `run_in_background`, **twice in one session, 2026-08-27**; two preflight runs abandoned, one dead at 35 lines with no exit marker, reported as "in flight" (CLAUDE.md §1) |
| **Synthetic or placeholder output** — wrote dummy or formulaic values instead of deriving them from real data | ✅ env-echoed defaults carrying a fabricated verdict all the way out; "a plausible-looking record is more dangerous than an empty one" (CLAUDE.md §4) |
| **Output format violation** — wrong filename, location, index column, required columns, types or units | ✅ the whole generated-artifact regime: a hand-edit of a `systems/views/` file fails the build; a typed total instead of a regenerated one (CLAUDE.md §1) — **and it is the axis Opus 5 measurably loses on** |
| **Environment setup failure** — could not get tools, packages or paths into a usable state | ✅ red preflight in a fresh sandbox, 2026-08-23: gate 2 wanted `jsonschema`, 29 manuscript guards wanted `pdfminer.six`/`pypdf`; fixed by `dev-setup.sh`, no tracked file touched (CLAUDE.md §6) |
| **Incomplete data** — analysed fewer samples, conditions or features than specified | ✅ "an absent reading is not a reading of absence"; UNMEASURED rows rather than green ones (CLAUDE.md §4) |
| **Inefficient analysis** — poor ordering, missed parallelisation, repeated completed steps | ✅ serialized preflight — trimcrae 2026-08-25, *"it absolutely murders our wall clock time"*; "polling is not work" (CLAUDE.md §6) |
| **Input misinterpretation** | ⛔ no dated incident recorded here |
| **Wrong method substitution** | ⛔ no dated incident recorded here |
| **Method misconfigured** | ⛔ no dated incident recorded here |

**Seven of ten.** These rules were written one at a time from incidents, never from a taxonomy, and
they land on seven of the ten failure modes an external benchmark independently measured as the ones
that predict a bad run — including both of the two most enriched in the worst quantile. That is the
first external corroboration this loop has had that its incident log is the field's failure surface
rather than a local quirk, and it is a partial answer to
[`method-watch-autonomy-prior-art.md`](method-watch-autonomy-prior-art.md) §2 item 3, *"this loop has
no external calibration of any kind"*.

⚠ **The three misses are the informative half.** Input misinterpretation, wrong method substitution
and method misconfiguration are all *scientific* execution errors — using the wrong tool, the wrong
contrast, the wrong filter. This repository's rule file has no dated incident of any of them, and the
benign reading (we do not make them) is not the only one: **an operational failure is loud and a
method misconfiguration is silent**, and nothing here is instrumented to catch the second.

## 5 · What this changes here

1. **⭐ Output contracts are load-bearing for the model we actually run.** The single largest
   measured deficit for Opus 5 on this benchmark is emitting an artifact in the demanded schema. Every
   agent-written artifact in this repository that has **no machine-checked output contract** is
   therefore sitting on our model's measured weak axis. Filed as a ledger item to enumerate them.
2. **⭐⭐ "Engineering effort is free" needs one clause it did not have.** CLAUDE.md §5 says agent
   time costs nothing because the subscription is flat-rate, and that stays true *for writing code*.
   BixBench3 measures something it does not cover: **more agent turns on the same task did not buy
   accuracy** — the best models sat at intermediate token use, run time and turns.
   ⛔ **Do not over-read this.** The correlation is *across models*, not within one model given a
   larger budget, and high token use is confounded with weaker models flailing. It does **not**
   establish that capping a good model's turns improves it. What it does establish is that
   *"more turns are free, so more turns are harmless"* is an assumption with no support and a
   measured association pointing the other way. This is also the closest external datum to the
   107-agent fan-out that lost its synthesis (CLAUDE.md §1).
3. **Depth confirms the derived-not-typed rule.** Depth-3+ artifacts pass at 0.24 against 0.44 at
   depth 2. Our claim chains are deep DAGs. This is external support for "a total is DERIVED, never typed — regenerate it" and for keeping intermediates independently checkable — a confirmation of an
   existing rule, **not** a new one.
4. **Working-set size confirms reduce-on-host.** Above 100 GB of raw input the mean score collapses
   to 0.10. Our MD trajectories are in that class. External support for the existing
   checkpoint-and-upload-continuously discipline and for never staging raw trajectories into an
   agent's working set — again a confirmation, not a new rule.
5. **A calibrated grading design we could borrow if we ever self-grade.** Metric product, zero for
   unreadable, and a pass threshold **calibrated against expert ratings** rather than chosen. If this
   loop ever grades its own reproductions, that is the shape to copy, and the calibration step is the
   part that makes it honest.

## 6 · One incidental science lead, weighted honestly

The 20 source papers are listed in Appendix Table 1. Nineteen are unrelated to this program.
**Task 14 is not:** *"RUNX2 inhibition disrupts a PAX3::FOXO1-RUNX2 feed-forward loop and dismantles
oncogenic gene programs in fusion-positive rhabdomyosarcoma."*

That is a **transcription-factor-fusion sarcoma** whose oncogenic program is dismantled by inhibiting
a **cofactor** rather than the fusion. EMC's problem is the same shape — EWSR1::NR4A3 is the driver
and the driver is the hard thing to drug — and a $0 check of this repository finds the *idea* is not
in its vocabulary: `grep` over every markdown file returns **zero** hits for "feed-forward" or
"cofactor loop", and RUNX2 appears only inside an accession→symbol cache and a scraped journal index,
never as a target. The nearest existing routes are `RT-FUSION-OUTPUT`, `RT-TXN-CDK` and
`RT-PARTNER-STRAT`.

⚠ **Weight this correctly. It is a paper TITLE in the appendix of an unrelated benchmark, and nothing
more has been read.** It is not a route, it is not evidence, and BixBench3 says nothing whatsoever
about EMC. What makes it worth a $0 follow-up rather than a shrug is that BixBench3's inclusion
criteria guarantee two things about it: the **raw data are public**, and the study published at least
four **ground-truth derived artifacts**. Filed as `AUT-BIX-003`.

## 7 · What was filed

- `TECH-AUTONOMOUS-AGENT` — BixBench3 added to `evidence[]` (it dates the landed half) and recorded
  as a **graded non-fire** in `pending_signals`. `current_state` unchanged: a benchmark does not move it.
- `FC-AUTONOMOUS-AGENT` — `last_reviewed` re-dated; the date bands are unchanged, because BixBench3
  confirms the existing rationale rather than shifting it, with one sharpening: the gap is **not only**
  durability and provenance, it is measurably raw multi-step capability too (0.24 at depth 3+).
- Three ledger items — see [`research-ledger.json`](autonomy/research-ledger.json): `AUT-BIX-001`
  (output contracts), `AUT-BIX-002` (failure vocabulary), `AUT-BIX-003` (the §6 lead).
