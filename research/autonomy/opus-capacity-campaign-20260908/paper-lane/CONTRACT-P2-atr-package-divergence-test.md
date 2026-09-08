# P2 — READ-ONLY contract, recorded BEFORE launch

Input revision **6eb48cce706cfa9d943afa5ef195d7e0d543676c**. `claude-opus-5` **medium**, saved first-party subscription, no paid fallback.
Deadline 2026-09-09T02:37:19Z. **⛔ READ-ONLY: this worker writes NOTHING into the repository.**

## Task

Apply one specific, bounded test to **one** paper:
`research/manuscripts/dependency/emc-atr-collaborator-package.md` and its
`…-review-response-2026-08-10.md`.

**The test:** for each item the response records as **APPLIED**, does the committed manuscript
actually carry it? This is the test that found four real defects on the repurposing paper. It is
**not** a census: one paper, one response document, one question.

## Why this is worth doing

The response claims 41 of 47 items applied in full. A parent spot-check found no divergence, but only
sampled — the "frame rule" claim, for instance, is present in substance under different wording, which
is exactly why a careful reading is needed rather than a grep.

## Finite acceptance

1. For **each** APPLIED item, report: **present**, **present in different wording** (quote both), or
   **ABSENT**. Do not guess — quote the manuscript.
2. For the 5 partial and 1 declined items, confirm the stated reason still holds; flag any that has
   since become doable from committed inputs.
3. **⛔ Report only. Change nothing.** Any defect you find is written up in your final message for the
   parent to contract separately.
4. Distinguish **wording differences** from **missing content**. A claim present in different words is
   **not** a divergence — say so explicitly.
5. If the response's items cannot be enumerated reliably, **STOP and say so**.

## Isolation and retention — binding

⛔ You may **not** write, copy, move or restore any file over a shared repository path for a baseline,
comparison or test. Baselines go **out** to your lane via `git show HEAD:<path> >` or by copying out —
never in. **No git write** of any kind; read-only git only.
⛔ No network, no source retrieval, no paid API, no GPU, no `scripts/preflight.sh`.
⛔ No census, no review-all sweep, no reopening of any earlier contract, no DFSP work.
There is no wet lab: no EMC efficacy, safety, selectivity or clinical-readiness claim. Invent no fact,
source, patient datum or measurement. If any request of yours is refused by content policy, stop that
branch, record the refusal verbatim, never route around it.
⛔ Do **not** weaken, relax, reorder or edit any gate. A tripped gate is a **finding to report**.
⚠ `lint_citations` fails repo-wide at exit 1 and is **pre-existing** — attribute it, and **do not
describe all gates as green**.
⛔ **DELETE NOTHING**, including your own lane.
Record `date -u`, `git rev-parse HEAD`, `git status --porcelain` at start and end.

Retain under `/tmp/claude-0/p2-lane/`: your notes and any quoted extracts.
Stop at ~35 calls / ~35 minutes.
