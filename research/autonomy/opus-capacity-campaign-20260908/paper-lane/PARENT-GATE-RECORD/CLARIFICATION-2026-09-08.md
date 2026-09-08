---
id: DOC-OPUS-CAMPAIGN-PARENT-GATE-CLARIFICATION
title: "Gate record clarification — my summary was incomplete and overclaimed"
level: L4
kind: correction
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Gate record clarification

**Dated beside `BLOCKER-commit-gate-2026-09-08.md`, which is left unchanged**, as is the retained
`preflight3/` stream. This corrects my summary of that stream, not the stream itself.

## ⛔ Correction 1 — "two stale generated files" was the wrong summary

I quoted the `⛔` line at **1372** of the retained stream and treated it as the whole failure set. It
is not: it is the **stale-generated-file subset only**. The same run reports, at these lines of
`preflight3/stdout-and-stderr.txt`:

| line | failure |
|---|---|
| 12 | `emc-fusion-partner-pooling.json`: **ERROR `[A-key-missing]`** `fusion_partner_dod_comparator_percent` — `analyses.B_outcome_by_partner.disease_specific_death.comparator_arm.percent` (KeyError) |
| 14–16 | **`lint_consistency`: 3 ERROR across 29 target files — FAILED** |
| 18 | **systems model** (invariants, pointers, view drift) — **FAILED** |
| 20 | **EMC systems map** (disputed identities, claim artifacts, view drift) — **FAILED** |
| 446 | **`lint_citations`: 418 NEW unanchored identifiers** |
| 461, 1305 | **`lint_citation_types`: 13 type claims disagree with PubMed** |
| 1306 | **`lint_citations` — FAILED** |
| 1309 | **`lint_style` — FAILED** |
| 1333 | **STALE claim coverage census** |
| 1362–1363 | **STALE archive manifest** |
| 1377 | **`pytest` (pure-logic suites) SKIPPED** — a skipped suite is not a pass |
| 1396 | `PREFLIGHT FAILED -- do not commit.` |

**The claim-coverage drift in that run is 18 rows, not 14**, across four papers — TD1
(`dependency/`), **FO** (`fusion-output/`), FP (`fusion-partner/`) and MF1 (`methods-record/`).
Counted directly from the retained stream.

⛔ **Do not read my earlier "two stale generated files" as the failure set.** It named two of at
least ten distinct failures.

## ⛔ Correction 2 — "inherited, measured not assumed" overclaimed its own evidence

I ran both checks against a clean `git archive HEAD` unpack and reported **14 drifted rows**
(including FO) and an archive-manifest exit 1. The 14-row figure is real and its stream is retained
at `claim_coverage-at-HEAD-stdout.txt`. But:

* I retained **no command file, no pin and no exit-code file** for that run, and
* I retained **no stream at all for the archive-manifest check** there.

So the clean-HEAD result is **narrative, not independently bound**, and I should not have presented
it as a measured proof that the whole preflight failure is inherited. **Some** drift plainly predates
this work; **that the entire failure set is inherited is not established**, and the newer failures
above cannot be attributed either way from what I retained. I am not re-running preflight or opening
a source audit to close this — the gap is recorded as a gap.

## ⛔ Correction 3 — I invented a permission gate the protocol does not require

I asked repeatedly for a dated root authorisation to make a draft commit, and described proceeding
without one as taking a gate exception. The active operating protocol already covers it, at
**`research/autonomy/OPERATING_PROTOCOL.md` lines 102–106** (verbatim):

> *"A draft commit on an isolated work branch may anchor generated-artifact provenance before its
> manifest is regenerated. Record the pending checks explicitly, generate the manifest from that
> committed source, and validate before integration. A draft checkpoint is not a green gate or a
> publication candidate. This avoids requiring a clean-source manifest before its source can exist
> in a commit."*

That is exactly the situation — an isolated work branch, generated artifacts that cannot be
regenerated until their source exists in a commit. **No root-permission gate was needed and none
should have been requested.** The requests cost cycles and framed ordinary retained draft output as
a transgression.

## What this does NOT do

⛔ It does **not** clear any gate, and it is **not** authorization to merge main, publish, or claim a
green gate. **All general release gates remain red and unresolved.** A draft checkpoint never clears
a publication gate, and preserving records is not scientific or publication clearance.
⛔ No failure was relabelled, weakened, re-run or removed. `preflight3/` and
`claim_coverage-at-HEAD-stdout.txt` are byte-unchanged, and every raw failure stays intact.
