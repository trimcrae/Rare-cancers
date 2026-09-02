---
id: DOC-SPRINT-S40-COVERAGE-INFLATION
title: "S40-COVERAGE-INFLATION — twelve sentences are marked covered and nothing guards their numbers, because one half of a 2026-09-01 fix landed and the other did not"
level: L3
kind: incident
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  Record why PREFLIGHT_FULL is legitimately red on the claim-coverage ablation gate, name the
  one-of-a-pair defect that causes it, and state plainly that the selector-validation record must not
  be re-stamped until it is fixed.
scope: >
  Two manuscripts measured at full ablation depth on commit ad87aa4c7. Does not fix the defect: the
  crediting rule lives in a governed file and the change needs mutation tests it has not had.
last_verified: 2026-09-02
---

# S40 — twelve covered sentences with nothing guarding their numbers

**Measured 2026-09-02 at commit `ad87aa4c7`**, by running the ablation gate at full depth
(`PREFLIGHT_FULL=1`, which takes EVERY covered sentence rather than a six-sentence sample):

    11 of 91 perturbed research/manuscripts/aso/fusion-junction-aso-journal-article.md
     1 of 87 perturbed research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md

Twelve sentences the census marks `covered` had their number changed in a clone, every witness the
census names for them was re-run, and **nothing went red**.

## ⭐ Every blind perturbation is a quantity written in WORDS

Fourteen perturbations across the twelve sentences, and not one is a digit:

    six->ten   seven->three   ten->six   fourth->eighth   second->fourth   five->nine
    two->six   four->nine     Two->Six

Five of the twelve credit the same witness — `test_universal_claims_are_scoped_to_what_was_measured.py`
— which checks whether a universal claim is scoped to what was measured. It reads the sentence's
*wording*. It cannot see a number, so it cannot notice when one changes.

## ⛔⛔ THE CAUSE IS ONE HALF OF A PAIR, AND THE OTHER HALF SHIPPED WITHOUT IT

`AUT-PD-148` (2026-09-01) established that a quantity written in words was unfalsifiable by
construction and fixed it — in `claim_ablation.py`. `states_a_quantity` and the perturbation set both
learned about words, so these sentences became ABLATABLE for the first time.

**`claim_coverage.py` was not touched.** Its rule is still `"covered": bool(hits)` — a sentence counts
as covered if ANY witness names the file, regardless of whether that witness binds the sentence's
quantity. So:

| half | changed 2026-09-01 | effect |
|---|---|---|
| what can be PERTURBED | ✅ `claim_ablation.py` | word-quantities became testable |
| what counts as COVERED | ⛔ `claim_coverage.py` | a prose-only witness still credits a numeric claim |

★ The fix made the population visible without making the crediting rule correct for it, so the
defect it exposed reads as a NEW failure when it is an OLD one that was previously unmeasurable.

## ⚠ WHY IT SAT UNSEEN, AND WHY THAT IS THE STRUCTURAL PART

`_sample` takes **six** evenly spaced sentences per paper unless `PREFLIGHT_FULL` is set, in which
case it takes every one. Twelve blind sentences out of 178 perturbed are unlikely to land in a
six-sentence sample — and `PREFLIGHT_FULL` is reserved by CLAUDE.md §6 for publication. So the gate
that measures whether coverage is real runs at 3% depth on every ordinary commit.

⛔ **A driver very nearly cleared this as a flake.** Seeing the failure only under FULL, the driver
re-ran the gate in isolation, got green, and reported it as load-sensitive. That green was a
SIX-SENTENCE run: a weaker test, whose sample did not contain the failing sentences. Reading it as
clearing the red is an absent reading taken as a reading of absence — the same §4 defect this sprint
spent the night finding elsewhere. What settled it was reading `_sample` and finding the
`PREFLIGHT_FULL` branch, not re-running anything.

## What this blocks, deliberately

`scripts/selector-validation.json` can only be re-stamped after a `PREFLIGHT_FULL` that exits 0, and
this failure is a legitimate reason for it not to. **The record must not be re-stamped until the
crediting rule is fixed**, and the trunk cannot honestly report a green full run before then.

## Not fixed here, and why

The crediting rule is in a governed path and the correct change — requiring that a sentence stating a
quantity be credited only to a witness that binds a quantity — will move the `covered` count on every
manuscript at once. That needs mutation tests and its own amendment record. Filed rather than rushed
at the end of a long session; a coverage rule edited carelessly is how the number gets inflated in the
first place.
