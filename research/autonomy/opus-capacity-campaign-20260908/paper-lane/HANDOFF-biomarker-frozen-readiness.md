---
id: DOC-OPUS-CAMPAIGN-FROZEN-BIOMARKER
title: "Frozen review handoff — biomarker-selected classes"
level: L4
kind: memo
status: live
purpose: >
  Hand the updated biomarker preprint candidate to review with its exact revision, its data and code
  provenance, its declarations, its original blind-seat disposition, and the checks that have and
  have not run.
scope: >
  L4. A handoff. It authorises no publication act, asserts no green gate, and creates no reviewer
  record.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Frozen handoff — `dependency/emc-biomarker-selected-classes.md`

## Exact revision and content identity

- **Git revision:** `69c82ff6` (this branch's HEAD at handoff), branch `claude/confident-bardeen-ji76cd`.
  The manuscript itself last changed at **`7d89e52b`**, the BP1 claim-ceiling batch; nothing has
  touched it since.
- **Manuscript:** `research/manuscripts/dependency/emc-biomarker-selected-classes.md`, **21,448 bytes**,
  sha256 `fe4f95abb1476c95cf60ea21a2570692328de0ada379f6c542329599b566c766`, computed at handoff time.
  3,022 words by `lint_style`'s own count.
- **Record:** `systems/graph/publications.json` → `PUB-BIOMARKER-DEP`, state **`drafted`**, target venue
  **`preprint`**, `outcome_potential: negative_or_methods`, `patient_path: none`, companion of
  `PUB-MODALITY-CENSUS`.

## What changed to make this the updated candidate

Three commits, in order, none of which altered a quantity or an identifier:

1. **`9ec78c4f`** — author block.
2. **`9953e7ef`** — preprint register conversion: 29 house glyphs removed by rewriting their
   sentences, bold 19.3 → 2.8 per 1000, em-dashes 10.5 → 0, four sentence-form headings recast, ORCID
   and a truthful AI-assistance statement added. ⛔ The conversion **broke five pinned-figure
   bindings**, caught only because `lint_consistency` was run; all repaired **in the prose**, with no
   pin edited, no context loosened and no guard touched.
3. **`7d89e52b` — the BP1 claim ceiling**, which is what makes this a candidate rather than a draft:
   - The Summary's "four states are **absent**" and "four classes are **ruled out**" contradicted
     §2.1, §2.3, §2.4 and §5, where protein loss and HR defect are unmeasured. It now says four
     proposed **transcript-level selection arguments** are unsupported or weakened, at four clearly
     different strengths, **none of them an exclusion of the class** — carried into the frontmatter
     purpose, §3 and falsifiers F1, F3 and F4.
   - Global novelty and absence claims narrowed to what is retained: "for none of the five had the
     lookup been reported" → "among the sources this programme has retained we found no report"; "no
     EMC cell line appears in ANY public dependency dataset" → a statement about the panel read here,
     with the absence of any EMC dependency reading preserved.
   - "Two scored gene groups" → "**the scored gene groups**" (eight are scored).
   - **Declarations corrected.** The study-type line now says no **NEW** recruitment, sampling or
     clinical intervention, and that the records were deposited publicly by others. ⛔ The invented
     determination that ethics approval was "not required" is **gone**: the text now says none was
     sought, none was obtained, and **no institution or committee has determined whether any is
     required**.

## Declarations, as they now stand

**Funding:** none. **Competing interests:** none. **Ethics:** none sought, none obtained, no
institutional determination made; the analysis reads public archival tumour-expression series and
public dependency data deposited by others, with no new recruitment, no new sampling, no clinical
intervention and no patient contact. **AI assistance:** analysis and drafting carried out with Claude
(Anthropic) and OpenAI models under the author's direction, author responsible for content, **not
peer reviewed by a human reviewer**. **Data and code:** §11 / the availability table below.

## Data and code provenance

Every value is read from artifacts committed in this repository; nothing was retrieved for the paper,
and **no producer was run to write it**. Five artifacts, hashed at handoff time:

| what it supplies | artifact | sha256 |
|---|---|---|
| scored expression panels per platform, group means, *t*, coverage | `research/modalities/emc-expression-panels.json` | `123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9` |
| per-route grading, verdict, hedge and action | `research/modalities/census-route-expression-grading.json` | `5bc3c80c034dde7781394554aa3bc18888248ad4cf1aa0153e4c7e4d5e4f07a8` |
| public sarcoma-line CRISPR dependency panel | `research/modalities/depmap-sarcoma-dependency.json` | `d88bed62a80dcb51675f0f7a5a27771a6c1f732e977200d39fa389cb8dd27546` |
| class definitions and selecting features | `research/literature/biomarker-class-definitions-2026-08-09.json` | `4cbd8b46adbd5954294b43c7b13718f9768a984b56662c3e06487504afeee69c` |
| clinical registry rows cited | `research/data/emc-clinical-registry.json` | `6f3b31b352c29592a4657d64aff872a93cf65f280837096008e59ab82e502bdd` |

All five relative links resolve on disk. ⚠ The scored gene groups are **repo-curated
pathway-membership lists, not published gene sets or signatures**; each panel's `provenance` field
says so, and the paper states it. **No figure has been rendered** — the display items are the tables
in the running text.

## Checks that actually ran, with their exit codes

| check | result | exit |
|---|---|---|
| `lint_style.py <target>` | clean · 0 ERROR across 1 file (bold 2.6/1000, em-dash 0.0/1000) | 0 |
| `lint_consistency.py` (repo-wide) | **0 ERROR across 29 target files**; the manuscript is `targets[19]` | 0 |
| `lint_claims.py <target>` | 0 ERROR, 0 WARN | 0 |
| `test_pinned_figures_every_home.py` | **292 passed** | 0 |
| `test_emc_expression_panels.py`, `test_emc_expression_datasets_workflow.py` | 45 passed | 0 |

⭐ **Ten pinned figures bind this manuscript** (`artifact_figures[89..98]`), each by regex context on a
line, and all ten contexts are intact. The pinned values 92, −2.203, −1.126, 2.423 and 1.744 are
unchanged from the artifacts.

## Checks that did NOT run, or do not cover this file — stated rather than implied

- ⛔ **No full `scripts/preflight.sh`, and no `PREFLIGHT_FULL` receipt exists for this revision.**
- ⚠ **This file is NOT in `lint_style.TARGETS`.** The clean result above is an **explicit-path
  measurement, not gate coverage**: the register would not be enforced on it by the gate as it stands.
  Adding it is an owner decision, not a lane edit, and is not made here.
- ⚠ **No test binds this manuscript's prose to its artifacts** the way the fusion-partner paper's does.
  The ten pinned figures are the only automatic prose-to-artifact binding it has.
- ⚠ `lint_citations.py` still exits 1 **repo-wide**, and **zero of its errors name this file**. ⛔ Its
  summary line "13 type claim(s) disagree with PubMed" remains wrong: all 13 are `MISSING` — no cached
  metadata — and **zero** are `MISMATCH`.
- ⛔ `systems_check.py --check`: **2,394 ERROR / 271 WARN / 6 INFO across 620 objects**, measured now.
  Pre-existing, not cleared, and no full-preflight pass is implied by it.
- ⛔ **The producers were not re-run.** This handoff shows the paper's numbers match their stored
  artifacts; it does not re-establish that those artifacts re-derive from their inputs.

## Original disposition — the blind five-seat review, unmodified

Reviewed blind at commit `20d33f3478fa34940552d26ea8ae05cdd7a23ad2` (2026-09-01):

| seat | verdict |
|---|---|
| arithmetic | `supported_with_reservations` |
| citations-and-instruments | `supported_with_reservations` |
| hostile-referee | `supported_with_reservations` |
| regression | `supported_with_reservations` |
| **statistics** | **`not_supported_as_written`** · `major_revision` |

The statistics seat's four blockers, and what the **current** text does about each — read line by line
against the seat record at handoff time, ⚠ **as my own measurement; no formal re-adjudication of these
seat verdicts is on record**:

1. *Seven of GSE24369's 42 samples silently dropped, five of them solitary fibrous tumours.* **Now
   stated**: §1 carries a "Sample accounting, GSE24369" paragraph naming the five solitary fibrous
   tumours as soft-tissue sarcoma biopsies on the same array.
2. *NOXA's second platform reads t = 0.628 and the paper printed no statistic.* **Now printed**:
   "0.23 SD, *t* = 0.63, with 76% of that array's symbols at least as extreme", followed by "This is a
   one-platform observation."
3. *The genome-wide empirical null makes the nominal Welch t anticonservative.* **Now in §5**, with the
   seat's own figures: |*t*| ≈ 2.2 sits where 0.29–0.32 of GPL6244 and 0.26–0.29 of GPL3290 symbols
   sit, ASS1 at 0.069/0.046, and "that placement controls no error rate and is not a significance
   claim … it cuts both ways".
4. *MKI67 is not clean on GPL3290, and F8 was deferred.* **Now stated in the text and in F8**: the
   control passes on GPL6244 (*t* = 0.53) and **fails** on GPL3290 (+1.24 SD, *t* = 2.30).

Other seats' blockers, same reading: the "only readable EMC expression data that exists" exhaustiveness
claim is **gone**, replaced by an enumeration of GSE28866, GSE43632, GSE80126 and GSE299349 with what
each can and cannot supply; the "three of the five" undercount is **gone**; the dropped POLQ
weak-read correction is **restored** ("the route's own primary gene is the weakest reading in the
module", no probe on GPL3290, 21st percentile on GPL6244); and the NHEJ specificity claim is now
scoped — "specific against NHEJ … not shown to be specific more broadly, and on GPL3290 not shown to
be specific at all", with HR rising more than alt-EJ there.

⚠ **One seat point is not addressed by name.** The statistics seat's p2 observed that **BCL2L2**, one
of the five guardians, is *higher* in EMC on GPL6244 at *t* = 2.908. The current text makes the
guardian claim at **group** level ("all five druggable guardians together are lower … *t* = −4.57 and
−2.54") and names only MCL1 and BCL2L1 individually, so it no longer asserts what that point refutes —
but it does not report the individual reversal either. A reviewer should decide whether that is
sufficient.

## What this handoff is not

⛔ It is not publication permission, not a reviewer record, and not a claim that any gate is green. It
asserts no EMC efficacy, safety, selectivity or clinical readiness: nothing here has been tested in an
EMC cell, no drug exposure was performed, and the paper's own ceiling is that four **transcript-level
selection arguments** are unsupported or weakened — **not** that any class is excluded.
