# R1 — ATR reconciliation proposal (isolated lane, no shared writes)

## Why this exists

`BLOCKER-atr-package-uncommitted-revision.md` establishes that the committed
`emc-atr-collaborator-package.md` is the **pre-revision draft**: none of the 41 items its 2026-08-10
response records as applied is present, while the revision's **side-products were committed** — the
changelog, `emc_fet_frame_and_composition.py`, its artifact, and `emc-fusion-frame-fig1.png/.pdf`.

**"Owner decision" is not a reason to stop preparing it.** Your job is to make that decision
**concrete and reviewable**.

## Deliverable — a concrete proposed patch, not an inventory

Produce, under `/tmp/claude-0/r1-lane/`, a **candidate revised manuscript** (or a unified diff against
the committed one) plus a decision memo. **A 41-row status table is NOT this contribution** — that
already exists.

## How to build it — grounded, not transplanted

⛔ **Do not mechanically transplant 41 claims because the response says APPLIED.** For each item:

1. **Resolve it against the committed evidence where possible.** The revised module, its artifact, the
   changelog and the figure are committed and are your ground truth — e.g. the 176 vs 177 arithmetic
   is settled by `emc-fet-frame-and-composition.json` and the test at
   `research/modalities/tests/test_emc_fet_frame_and_composition.py:32`, **which does exist** (a
   previous lane wrongly reported it missing).
2. **Where the committed evidence supports the response's version, draft the text.**
3. **Where it does not, or where the response asserts something no committed input establishes, mark
   the item UNRESOLVED** with the exact missing input. Do not invent the revision's wording.
4. **Name the scientific and structural decisions a human must take** — retitling, dropping
   predictions P4/P5, moving tables to supplementary, inserting the figure — separately from the
   mechanical corrections. These are judgements, not transcription.

## Acceptance

- A candidate revision or diff exists in your lane and is coherent as a document.
- Every included change is **traceable to a committed input you cite**, or is flagged as a proposed
  editorial judgement.
- Every unsupported item appears in an **explicit UNRESOLVED list**.
- The memo states plainly: **this is a proposed reconstruction, not a recovered original.**
- If you cannot make progress within bounds, **record that exact finite result and stop** — a
  supported stop is a successful outcome.

## Bounds — binding

Input revision **fb6f7028a420a7bf383e2974bebf9a18f38f4b6d**. `claude-opus-5` **medium**, saved first-party subscription — **no paid
fallback, no overage, no credits, no GPU**. Deadline **2026-09-09T02:37:19Z**.

⛔ **Do NOT edit the shared manuscript, any clinical or patient-facing artifact, the registry, any
gate, or any committed scientific artifact.** Your proposal lives **entirely in your own lane**.
⛔ You may **not** write, copy, move or restore any file over a shared repository path, for any reason.
Baselines go **out** via `git show HEAD:<path> >`. **No git write** — read-only git only.
⛔ **Do not rerun unchanged gates.** ⛔ No network, source retrieval, denied-route retry, or
`scripts/preflight.sh`. ⛔ No history hunt, no census, no whole-paper re-review, no reopening of a
closed contract.
⛔ **Distinguish a PROPOSED RECONSTRUCTION from a RECOVERED ORIGINAL.** You are not recovering a lost
draft and must never imply you have. Say "proposed" everywhere.
⛔ Leave anything you cannot support **explicitly UNRESOLVED**. An honest unresolved list is part of
the deliverable, not a failure.
There is no wet lab: no EMC efficacy, safety, selectivity or clinical-readiness claim. Invent no fact,
source, patient datum or measurement. If a request of yours is refused by content policy, stop that
branch, record the refusal verbatim, never route around it.
⛔ **DELETE NOTHING**, including your lane. Record `date -u`, `git rev-parse HEAD`,
`git status --porcelain` at start and end, and confirm you changed nothing shared.

Stop at ~40 tool calls / ~40 minutes.
