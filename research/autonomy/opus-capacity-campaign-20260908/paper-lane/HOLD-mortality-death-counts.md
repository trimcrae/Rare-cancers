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

# ⭐ CLEARED 2026-09-08 — the corrected tally is 50 documented deaths

**Resolved.** Neither 52 nor 51 was right, and the answer is neither.

Classified row by row on the retained quoted sentences, and re-derived independently by the parent
before applying: exactly **two** of the 18 rows state no death.

- **PMID 23213584**, label `visceral_metastasis_complication`, n = 1 — a NAMED mechanism, so removing
  it moves numerator and denominator together, exactly as feared.
- **PMID 21941486**, label `mechanism_unstated`, n = 1 — "transitioned to supportive care"; the death
  is not described.

So: **50 documented deaths**, **14** with a named mechanism, **27** unstated. The share is
**28.0 %**, not 28.8 % and not 29.4 %. Check: 14 + 27 + 8 emc-progressive + 1 ambiguous = 50.

⛔ **Neither exclusion asserts that the patient survived.** Both are statements about what the
record documents.

⚠ **The 50 is a count of RECORDS, not of people.** Two of the contributing reports are literature
reviews collecting previously published intracranial cases, and whether they share patients with each
other or with two case reports is undetectable from what was retrieved. The paper now says so, and
"recur across independent reports" became "recur across separate reports, whose independence is not
established".

⚠ **PMID 21941486 cannot be classified from what is retained** — the sentence proves neither death
nor survival. It is labelled `death_not_documented`, which is a statement about the record.

⚠ The memo's **388** had no artifact basis at all — not 328, 400, 600, 162, nor any query's
`retrieved`. Its provenance is unrecoverable from what is retained, so each site was corrected to the
figure right for it rather than guessed at: the palliative-care title-level scan is **25** records
from one query, and the general retrieved corpus is **328**.

## The hold as it stood, retained

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
