---
id: DOC-OPUS-CAMPAIGN-PORTFOLIO-INVESTIGATION-CONTRACT
title: "Shared contract — portfolio paper-family investigations, 2026-09-08"
level: L4
kind: contract
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Shared contract — portfolio investigations

Each worker owns **ONE** candidate lane. This is a **prospective research investigation**, not a
review of an existing paper and not an audit.

## Grounding — read the real evidence before proposing anything

* `systems/graph/publications.json` — 33 endpoints. Follow your entry's `document.file`, and its
  `routes[].publication → routes[].artifacts → artifacts[].path` connections.
* The real manuscript directory for your lane, and the **actual study results** it points at.
* `research/autonomy/portfolio-2026-09-05/recommendation.md` — **dated**. It lists prospects that
  have since been completed, held or refuted. **Reconcile it against later results**; do not treat an
  old prospect as untested.

## What to deliver

1. A **compact concrete question** — one or two sentences, answerable.
2. A **provisional paper-level merit rationale**: patient relevance, non-trivial contribution,
   attainable evidence. **Scientific strength comes before execution convenience.**
3. The **exact unfinished evidence gap**, and what distinguishes it from prior completed or held
   results — name the actual inputs.
4. Then **pursue the best useful bounded next step.** Do not stop at "not ready."

Examples of a good step — not a requirement to manufacture a paper: extracting or verifying an
accessible primary dataset; checking a real dataset's cohort and assay identities; producing a
reusable evidence table or benchmark definition from existing measurements; writing and running a
small reproducible analysis on available inputs; a decisive feasibility or falsification result.

Every selected step states: **artifact · validation or baseline · provenance · limitations · stop
condition.**

## Honest outcomes

**A genuine bounded no-go is a valid result.** Record it with the next credible independent work or
the actual missing dependency. **Never manufacture a positive outcome, and preserve every negative
finding.** If a computation would be uninterpretable, or its validation data absent, the useful task
is to **establish or resolve that concrete dependency with evidence** — not to restate a generic
blocker. A paper-level HOLD does not forbid a distinct legitimate question; equally, **a new label
does not cure old missing evidence.**

## Fences — all real, none negotiable

* ⛔ No wet lab. No fabricated observation. No patient-specific advice. **No clinical efficacy,
  safety or therapeutic-window claim from computation.**
* ⛔ No GPU, no paid API, no usage credit, no publication, no outreach.
* ⛔ No edits to frozen ASO or submitted assets, and none to the user-rejected EMC-classification
  project.
* ⛔ **Do not bypass, reword, model-switch or proxy around any refusal or denied source.** The closed
  **B1 / B2 / B4** routes stay closed. A new legitimate public source may be investigated by its
  ordinary permitted access; a previously denied source is **not** re-openable.
* ⛔ Do not restart **R1** or **R4** (closed duplicates), the unadmitted **R2** simulation, or the
  **R3** cohort execution. **Do not manufacture independent validation out of a reused cohort.**
* ⛔ No new baseline review of a current repaired paper, no broad gate sweep, no gate amnesty.
* ⛔ Never weaken a guard, floor, gate, matcher, pin or test. Never fabricate an exit code — use
  `${PIPESTATUS[0]}` or no pipes. A skipped or deselected test is not a pass. **Preserve every failed
  execution.**

## Ownership and storage

**Read the existing checkout concurrently; do not copy it.** Measured headroom at dispatch:
**13 GiB free** — so no repo copies, no worktrees for investigation lanes, and **no worker fetches a
corpus another worker is already fetching.** Reuse existing runtime and data.

⛔ **No worker edits another paper's current manuscript, the canonical graph
(`systems/graph/*.json`), the source registry, or any acceptance criterion.** Writes go **only** to
your own directory under
`research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/<LANE>/`.
If a shared file needs changing, prepare an exact **unapplied** unified diff and say so.

⛔ Do **not** `git add`, `commit`, `push`, or run `scripts/preflight.sh`. **The parent alone records
shared state.** Do not spawn subagents.

## Timing

**Checkpoint at 20–30 minutes** — earlier if you reach a decisive result. Return what you have; do
not run silently to the campaign stop (**2026-09-09T02:37:19Z**).

## Return

`FINDING.md` with the question, merit rationale, evidence gap, the step taken, and its artifact /
validation / provenance / limitations / stop condition; the artifact itself; and `checks/` with one
directory per execution attempt — `command.txt`, `stdout.txt`, `stderr.txt`, `exit_code.txt` — every
attempt, failures included.
