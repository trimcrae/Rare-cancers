---
id: DOC-OPUS-CAMPAIGN-HOLD-MORTALITY
title: "Paper-specific hold — mortality death counts"
level: L4
kind: memo
status: live
purpose: >
  Hold the mortality paper's death-count claims while a scoped correction runs, and record exactly why
  both the current figure and the first proposed replacement are wrong.
scope: >
  L4. A hold and its evidence. It changes no count and proposes none.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# HOLD: death-count claims in `emc-mortality-mechanisms-paper.md`

⛔ **Every death-count claim in this paper is on hold** until a scoped correction lands and is
verified. That includes §3.1's "Fifty-two deaths were described", the 15/52 = 28.8 % mechanism share,
and every downstream percentage, table cell and abstract sentence that rests on them.

## Why the current figure is wrong

`emc-terminal-events-classified.json` holds 18 rows summing to **52** — verified independently. At
least two of those rows are not documented deaths:

- **PMID 23213584** carries its own note: *"⚠ Not a death sentence. … Counted in the mechanism table
  only as a complication, never as a death."*
- **PMID 21941486** describes a transition to supportive care; **the death itself is not described.**

So 52 is the **mechanism-table sum**, not a count of confirmed deaths, and the paper's "fifty-two
deaths were described" overstates what the artifact holds.

## ⛔ Why the first proposed replacement is ALSO wrong

An earlier pass proposed 15/51 = 29.4 %. **Do not use it.** PMID 23213584 also contributes to the 15
labelled mechanisms, so removing it moves the **numerator and the denominator together** — and a
second row (21941486) is affected as well. Neither 52 nor 51 is established, and swapping one
unexamined number for another would have shipped a second wrong figure under the appearance of a
correction.

## Reopening condition

A correction that, using **only** the 18 existing rows, their retained quoted sentences and the
existing producer:
1. classifies every row explicitly as documented death versus nonfatal or undocumented-death,
   quoting the sentence it judges on;
2. derives the death-only tally **and every affected numerator, percentage, table cell, category
   total and prose claim** consistently;
3. treats the summed reports as selected descriptive literature records, claiming no cross-report
   unique patients or independent cases;
4. preserves every original quote, source byte and dated history;

together with its targeted-check execution and an explicit statement of any row the retained evidence
cannot settle.

⛔ No new source hunt, no denied-route retry, no natural-history or clinical-efficacy inference. At
most one producer run on the same cached sources, only if a dependent output needs refreshing.

## Related, separately owned

The memo `emc-mortality-mechanisms.md` cites a "388-paper retrieved corpus" with no artifact basis;
the probe records 600 enumerated, 400 attempted, 328 retrieved, 162 with death sentences. ⚠ The
palliative-care title-level search ran over `early_palliative_care_survival.retrieved = 25`, not the
328 general corpus — so 388 must not be replaced by a single figure everywhere. That correction is in
the same lane under explicit ownership.
