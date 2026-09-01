---
id: DOC-SPRINT-S5-READABILITY
title: "S5-READABILITY — the readability splitter did not break before a callout glyph"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S5-READABILITY — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S5-READABILITY — the splitter miscount, its fix, and the blast radius

**Item(s):** AUT-PD-142
**Owned paths:** `research/manuscripts/lint_readability.py`,
`research/manuscripts/tests/test_the_readability_splitter_breaks_where_a_sentence_does.py`,
this file
**Started/Finished (UTC):** 2026-09-01 — 2026-09-01

## Verdict

**FIXED.** AUT-PD-142 reproduced on live files and repaired; the corrected splitter drops the
corpus-wide over-ceiling count from **276 to 218** sentences across 30 documents and clears
`publish_bar` clause 7 (`readable_enough_to_review`) for **three publication endpoints —
PUB-ATR, PUB-BIOMARKER-DEP and PUB-TXN-DEPENDENCY — which were held by a measurement artefact and
not by their prose.** The other 17 held documents still have real over-length prose: **213 of the
218 remaining flags are genuine sentences**, and the largest holder (PUB-DEGRADER, 145) is real.

⛔ **No bar moved.** `SENTENCE_CEILING` is still 60, `publish_bar.py` was not touched, and a test
pins both facts. The count fell because the count was wrong, not because the line was.

---

## What I measured

### 1 · Refute-by-default: the defect still exists

The row was filed 2026-08-28 against `emc-fusion-partner-stratification.md`, whose 17 flagged
sentences CYC-0070 then split in the prose. That document now reads **0 over-ceiling**, so the row's
own evidence file no longer demonstrates it. The defect does, on other files:

```
$ python3 research/manuscripts/lint_readability.py --report \
      research/manuscripts/aso/fusion-junction-aso-journal-references.md
fusion-junction-aso-journal-references.md   76  15.5   25   82     2  11.1          0.9
```

The two flagged "sentences" at line 25, verbatim from the splitter, are each two sentences:

| reported | real parts | joined at |
|---|---|---|
| 67 w | 43 w + 24 w | `… checked by nothing. ⛔ The banner once claimed …` |
| 82 w | 54 w + 28 w | `… the list is its own home.) What holds it …` |

Both real parts are **under** the 60-word ceiling. Both reported values are **over** it. The whole
of that document's clause-7 exposure was the artefact.

Three distinct join mechanisms, all confirmed against live files:

1. **A callout glyph opens a sentence and the opener class did not contain one.** The pattern was
   `(?<=[.!?])\s+(?=[A-Z(“"])`. Census of the corpus (`research/manuscripts/**/*.md`, extracted
   prose only, occurrences of a terminal stop followed by a non-alphanumeric opener):
   ⚠ 641 · ⛔ 379 · ⭐ 89 · ✅ 70 · ★ 61 · ⭑ 49 · ✓ 27 · ⚙ 9 · ✗ 8 · ◐ 5 · ⚑ 2 · ❌ 2 · ⚪ 1.
2. **`§` opens a sentence** — 271 occurrences after a terminal stop.
3. **The stop sits inside a closer** — `… own home.) What holds it …`, `… EMCs.” So the honest
   reading …`. The lookbehind read the last character (`)`, `”`) rather than the stop.

### 2 · A third defect the fix exposed, in the dangerous direction

Splitting correctly handed each all-caps callout sentence to the fragment filter
`re.search(r"[a-z]{3}", p)`, which requires three consecutive **lowercase** letters — so the filter
**deleted** it. While the sentence was glued to a lowercase neighbour the joined string passed;
split, it vanished.

Measured on `research/manuscripts/dependency/emc-atr-vulnerability-assessment.md`: six sentences
dropped, including `⚠ THE TIER DOES NOT MOVE, AND NEITHER DOES THE RANK.`, taking two caution
markers ("does not", "neither") with them — **caution 17.1 → 16.8 markers per 1000 words**. A
readability fix quietly spending caution is precisely the failure `scientific-writing` §4 exists to
stop, so it is repaired in the same change and pinned by a test.

⭐ **The exemption is deliberately narrow: a leading callout glyph, and nothing else.** A general
case-insensitive filter also admits 44 reference-list stubs (`PMID 31765367; PMC6894367.`,
`Int J Mol Sci 19:E1855.`) as prose, which is a different wrong answer. With the narrow rule every
caution figure in the corpus returns to its pre-fix value except two unpinned documents that
**rise** (`nr4a3-monovalent-pocket-route.md` 17.2 → 17.5) or fall by rounding
(`cancer-modality-census.md` 13.7 → 13.6) as previously-invisible sentences enter the denominator.

### 3 · The pinned caution baselines did not move

`readability-baseline.json` pins 11 documents. Every one of them measures the same
`caution_per_1000w` before and after the fix — as it must, since a splitting change repartitions
text without removing any. **I did not touch the baseline file (not an owned path) and it does not
need re-pinning.**

⚠ **Two documents were ALREADY below their pinned baseline at `HEAD`, before my change**, proved by
running the pristine module from `git show HEAD:…` against the same tree:
`fusion-junction-aso-supplementary-information.md` 7.8 → 7.7 and
`fusion-junction-aso-journal-tables.md` 11.2 → 10.2. **Pre-existing, not mine, and unrelated to this
fix** — but `--check` is red on them and nothing in the commit loop runs `--check`
(`preflight.sh:634` runs `--report` only), so nobody has seen it. Ledger row proposed below.

### 4 · Mutation testing (scratch copy, live tree never mutated)

Copy at `…/scratchpad/mut/manuscripts/`; the live file was only ever read from.

| # | mutation | result |
|---|---|---|
| M0 | control | 65 passed |
| M1 | pre-fix splitter restored | **39 failed** |
| M2 | closer-aware lookbehind branch removed | **6 failed** |
| M3 | `§` removed from the opener class | **1 failed** |
| M4 | terminal-stop guard removed (splits on a bare glyph) | **9 failed** |
| M5 | `— → ⇒ ≈ ± − [` added to the opener class | **8 failed** |
| M6 | all-caps callout exemption reverted | **1 failed** |
| M7 | `SENTENCE_CEILING` raised to 200 | **4 failed** |
| M8 | a glyph added to the splitter but not to the suite | **1 failed** |
| M9 | restored control | 65 passed |

M4, M5 and M7 are the loosening mutations — the ones that would let a genuinely long sentence past
the gate — and all three are caught.

### 5 · End-to-end through the bar it feeds

`publish_bar.clause_7_readable_enough_to_review(pid, HEAD)`, run directly:

- `PUB-ATR` → **PASS** (`no sentence over 60w (longest 53w …)`), was FAIL with 7
- `PUB-BIOMARKER-DEP` → **PASS** (longest 51w), was FAIL with 1
- `PUB-TXN-DEPENDENCY` → **PASS** (longest 59w), was FAIL with 1
- `PUB-DEGRADER` → **FAIL**, 145 sentences over, longest 175w at line 2575 — correctly still held

---

## ⭐ Blast radius — over-ceiling sentences per document, BEFORE and AFTER

Every document a `PUB-*` endpoint names in `systems/graph/publications.json`, plus the five
`lint_style.TARGETS` documents no endpoint names. Measured on the working tree, 2026-09-01.

| publication | document | over B | over A | longest B | longest A | moves toward the bar? |
|---|---|---:|---:|---:|---:|---|
| PUB-ATR | `dependency/emc-atr-vulnerability-assessment.md` | 7 | **0** | 77 | 53 | ✅ **clause 7 now PASSES** |
| PUB-BIOMARKER-DEP | `dependency/emc-biomarker-selected-classes.md` | 1 | **0** | 77 | 51 | ✅ **clause 7 now PASSES** |
| PUB-TXN-DEPENDENCY | `dependency/emc-transcriptional-proteostatic-dependency.md` | 1 | **0** | 107 | 59 | ✅ **clause 7 now PASSES** |
| — | `aso/fusion-junction-aso-journal-references.md` | 2 | **0** | 82 | 54 | ✅ clears `--check` (no endpoint) |
| PUB-METHODS | `methods-record/degrader-methods-failure-record.md` | 9 | 1 | 87 | 61 | ◐ 8 of 9 were artefact; **1 real, 61 w** |
| PUB-MODALITY-CENSUS | `modality-census/cancer-modality-census.md` | 3 | 1 | 96 | 64 | ◐ 2 of 3 were artefact |
| PUB-CLOSED-ROUTES | `methods-record/closed-routes-negative-record.md` | 6 | 3 | 94 | 79 | ◐ half artefact; 3 real |
| PUB-EMC-PROGRAM | `program/emc-treatment-roadmap.md` | 11 | 8 | 130 | 130 | ◐ 3 artefact; 8 real, one 130 w |
| PUB-NEOANTIGEN | `neoantigen/fusion-junction-neoantigen-paper.md` | 7 | 4 | 110 | 80 | ◐ 3 artefact; 4 real |
| PUB-FUSION-OUTPUT | `fusion-output/nr4a3-fusion-transcriptional-output.md` | 19 | 15 | 104 | 89 | ◐ 4 artefact; 15 real |
| PUB-HLA-COVERAGE | `neoantigen/hla-coverage-emc.md` | 6 | 4 | 87 | 80 | ◐ 2 artefact; 4 real |
| PUB-DEGRADER | `degrader/nr4a3-degrader-paper.md` | 165 | 145 | 177 | 175 | ⛔ 20 artefact; **145 real** |
| PUB-ANDGATE | `degrader/fusion-selective-andgate-degrader-paper.md` | 4 | 3 | 92 | 76 | ◐ 1 artefact; 3 real |
| PUB-MONOVALENT | `occupancy/nr4a3-monovalent-pocket-route.md` | 3 | 2 | 97 | 80 | ◐ 1 artefact; 2 real |
| PUB-STRATEGY-ARCH | `care-delivery/emc-trial-reachability.md` | 1 | 1 | 90 | 61 | ⛔ real (shortened, still over) |
| PUB-EMC-CLASSIFICATION | `care-delivery/emc-icdo-9231-classification.md` | 3 | 3 | 84 | 84 | ⛔ all real |
| PUB-VACCINE-PATH | `neoantigen/emc-vaccine-development-path.md` | 18 | 18 | 108 | 108 | ⛔ all real |
| PUB-SURFACE-TARGETS | `surface-targets/emc-surface-target-landscape.md` | 2 | 2 | 80 | 80 | ⛔ all real |
| PUB-ATR-PANEL-ASK | `dependency/emc-atr-collaborator-package.md` | 1 | 1 | 66 | 66 | ⛔ real |
| PUB-REPURPOSING | `repurposing/repurposing-hypotheses.md` | 1 | 1 | 64 | 64 | ⛔ real |
| PUB-SYNLETH | `dependency/degrader-vs-synthetic-lethal.md` | 1 | 1 | 62 | 62 | ⛔ real |
| — | `aso/fusion-junction-aso-supplementary-information.md` | 3 | 3 | 103 | 103 | ⛔ all real |
| — | `aso/fusion-junction-aso-journal-tables.md` | 1 | 1 | 75 | 75 | ⛔ real |
| — | `mtap-prmt5/emc-mtap-prmt5-hypothesis-SI.md` | 1 | 1 | 134 | 134 | ⛔ **artefact of a DIFFERENT bug** (below) |
| PUB-ASO | `aso/fusion-junction-aso-journal-article.md` | 0 | 0 | 54 | 54 | already clear |
| PUB-ENDPOINT | `endpoint/response-endpoint-indolent-tumours.md` | 0 | 0 | 53 | 53 | already clear |
| PUB-FUSION-PARTNER | `fusion-partner/emc-fusion-partner-stratification.md` | 0 | 0 | 60 | 60 | already clear |
| PUB-MTAP-PRMT5 | `mtap-prmt5/emc-mtap-prmt5-hypothesis.md` | 0 | 0 | 58 | 58 | already clear |
| PUB-TCIP | `tcip/tcip-induced-interface-preprint.md` | 0 | 0 | 57 | 57 | already clear |
| — | `surface-targets/emc-surface-target-landscape-si.md` | 0 | 0 | 49 | 49 | already clear |
| **TOTAL** | 30 documents | **276** | **218** | | | **10 at zero, was 6** |

**Said plainly.** The fix moves **four documents** all the way to zero, three of them publication
endpoints whose clause 7 now passes. It substantially reduces — but does not clear — nine more. And
it leaves **17 documents with genuinely over-length prose that must be split by a writer**, headed
by `nr4a3-degrader-paper.md` (145 real sentences, longest 175 w) and
`emc-vaccine-development-path.md` (18, longest 108 w). ⛔ Those papers were **not** being held by a
bug and the fix does not help them.

### Classification of the 218 that remain

| class | count | what it is |
|---|---:|---|
| real prose | **213** | genuinely one sentence, over the ceiling, needs splitting by a writer |
| list-item join | **5** | a separate extractor defect, not the splitter — see below |

---

## What I changed

### `research/manuscripts/lint_readability.py`

1. **`_CALLOUT_OPENERS`** (new module constant) and **`_SENTENCE_SPLIT`** (new compiled pattern)
   replace the inline `re.split(...)` in `sentences()`. The pattern now (a) accepts a terminal stop
   that sits inside a closer `” ’ " ' ) ]` via a second fixed-width lookbehind branch, and
   (b) adds `§` and the callout glyphs to the opener class.
2. **The fragment filter** now also keeps a ≥3-word fragment that opens with a callout glyph, so an
   all-caps callout sentence is measured rather than deleted (§2 above).

**Glyphs handled** (30, each with a test row):
`⛔ ⚠ ★ ⭐ ⭑ ✅ ✓ ✔ ✗ ✕ ✖ ❌ ◐ ○ ◆ ⏸ ⏳ ⚑ ⚙ ⚖ ⚫ ⚪ 🔒 📦 📏 📞 🗺 ⏱ ✍ ↯` — plus `§`.

**Deliberately NOT handled, each with its reason** (all pinned as negative tests, because a false
split *understates* a length and that is the direction that lets a long sentence past the gate):

| excluded opener | why |
|---|---|
| `→ ⇒ − ± ≈ ≥ ≤ √ ∈ ≠` | operators, not openers; they occur mid-formula (`i.e. ≈190 ns/day`, `⇒` reading as "implies") |
| `—` (em dash) | this repository's commonest **mid**-sentence mark; the 131 post-stop occurrences are list artefacts, not sentences |
| `[` | ambiguous with a trailing citation (`… breakpoint. [7]`), which belongs to the sentence **before** it |
| a bare digit or lowercase letter | no sentence in these manuscripts opens with one; the false-split cost is asymmetric |
| a glyph with **no** preceding terminal stop | `A sequence printed with ⚑ beside it …` — the glyph is the subject matter |

### `research/manuscripts/tests/test_the_readability_splitter_breaks_where_a_sentence_does.py` (new)

65 tests: one per glyph class, `§`, six closer forms, the all-caps regression, seven negative
operator cases, two mid-sentence-glyph cases, the abbreviation guard, a pinned real-corpus example,
a one-of-a-pair guard (any glyph added to `_CALLOUT_OPENERS` and not to the suite fails), a
pattern-level guard that the terminal-stop requirement cannot be silently dropped, and two
bar-did-not-move guards. All fail before the fix (M1: 39 failed) and pass after.

**Gates run** (scoped to the change, per charter §6): `pytest` on both readability test files plus
`research/autonomy/tests/test_the_clause_count_is_never_typed.py` → **69 passed**.
⚠ A first run tripped `tracked_tree_guard` on `research/manuscripts/line_citations.py` — **another
seat's concurrent edit, not mine**; my two files are the only ones I touched.

## What I could not do, and what it is actually waiting on

- **Nothing is blocked.** No manuscript was edited (charter, and the seat prompt forbids it).
- `readability-baseline.json` needed no change and is not an owned path — verified rather than
  assumed: all 11 pinned values are byte-identical before and after.
- `publish_bar.py` untouched.

## Ledger rows the driver should write

Three, none of which I may write myself.

1. **`what`:** ⛔ `lint_readability.paragraphs()` DOES NOT BREAK AT A LIST ITEM, THOUGH ITS OWN
   DOCSTRING SAYS IT DOES — *"A paragraph break, a list item, a table row, a heading and a
   horizontal rule are hard boundaries"*. Headings, rules and table rows are dropped by `body()` and
   so become line-number gaps; a list item is not — `body()` strips the bullet and leaves the line
   adjacent, so a bulleted list is joined into one paragraph and measured as one sentence.
   ⭐ Measured 2026-09-01 with a scratch implementation of the boundary: it removes **5** further
   over-ceiling flags (218 → 213) across four documents and clears
   `mtap-prmt5/emc-mtap-prmt5-hypothesis-SI.md` entirely (its only flag is a 134-word "sentence"
   that is really six bullets of a `Every number … resolves to one of:` list). Caution counts are
   unchanged in every document, so no baseline re-pin is needed. Same direction of harm as
   AUT-PD-142 — strict-only, nothing let through.
   **`kind`:** `process_defect` · **`state`:** `queued` · `cost_class`: free.

2. **`what`:** ⛔ `lint_readability.body()` STRIPS ONLY SINGLE-LINE HTML COMMENTS, SO A MULTI-LINE
   `<!-- … -->` BLOCK IS MEASURED AS PROSE. `re.sub(r"<!--.*?-->", …)` is applied per line, so a
   comment opened on one line and closed on another is counted in full. Both flagged sentences in
   `aso/fusion-junction-aso-journal-references.md` and the editorial block at
   `dependency/emc-atr-collaborator-package.md:41` are inside such comments. ⚠ **Direction is not
   safe here and this is the one that differs from AUT-PD-142:** the comment text also enters
   `words`, so it moves `caution_per_1000w` in **either** direction and therefore touches the pinned
   baseline. Fixing it requires `--write-baseline` in the same commit, with the moved values named.
   **`kind`:** `process_defect` · **`state`:** `queued` · `cost_class`: free.

3. **`what`:** ⚠ `lint_readability --check` IS RED ON TWO PRE-EXISTING CAUTION FALLS AND NOTHING IN
   THE COMMIT LOOP RUNS IT. `preflight.sh:634` runs `--report` only (advisory, `|| true`), so the
   ratchet in `--check` is enforced **only** through `publish_bar` clause 7, and only for documents
   a `PUB-*` endpoint names. Measured 2026-09-01 against the pristine module at `HEAD`, so it is not
   a side effect of AUT-PD-142's fix: `aso/fusion-junction-aso-supplementary-information.md` 7.8 →
   7.7 and `aso/fusion-junction-aso-journal-tables.md` 11.2 → 10.2 markers per 1000 words. Neither
   document is named by an endpoint, so nothing has ever reported it. Decide whether the drop is a
   real caution loss to restore or a deliberate change to re-pin — and whether `--check` belongs in
   the commit loop.
   **`kind`:** `process_defect` · **`state`:** `queued` · `cost_class`: free.

**And close AUT-PD-142** (`state: done`), with the note that the fix landed with the baseline
UNCHANGED — the row anticipated a re-pin, and the measurement says none is needed, because a
splitting change repartitions text without removing any of it.

## Amendment record for the driver

**Exactly one of my two code paths is governed**, checked rather than assumed —
`amendment_guard.is_governed()` answers `True` for the new test file (`**/tests/**`) and `False` for
`research/manuscripts/lint_readability.py`, which is not in `GOVERNED`. So one record, for the test
file, in the schema `check_log()` requires (`cycle_id`, `utc`, `path`, `what_changed`, `old_value`,
`new_value`, `why`, `self_serving_check` — all non-empty, and `declared()` matches on
**`path` + `cycle_id`**).

⛔ **`cycle_id` below is a placeholder — replace it with the driver's real cycle id before
appending, or `declared()` will not match and the guard will report UNDECLARED.** `utc` should be
the append time.

```json
{"cycle_id": "<DRIVER-CYCLE-ID>", "utc": "<APPEND-TIME-UTC>", "path": "research/manuscripts/tests/test_the_readability_splitter_breaks_where_a_sentence_does.py", "what_changed": "New test file, 65 tests, for `lint_readability.sentences()`, which had no boundary tests at all. One case per callout glyph class (30), the section sign, six closing-quote/bracket forms, the all-caps callout sentence the fix itself would otherwise have deleted, seven negative operator cases, two mid-sentence-glyph cases, the abbreviation guard, a pinned real-corpus example, a one-of-a-pair guard binding `_CALLOUT_OPENERS` to the suite, a pattern-level guard that the terminal-stop requirement cannot be dropped, and two guards that the ceiling did not move.", "old_value": "No test file existed for the splitter. The opener class was `[A-Z(“\"]`, so a sentence opening with ⛔ ⚠ ★ ⭐ ⭑ ✅, with §, or following a stop that sits inside a closer (`… own home.) What holds it …`) was glued to the sentence before it and the pair was reported at their combined length. 276 over-ceiling sentences across 30 documents.", "new_value": "65 tests, all passing; 8/8 mutations caught (M1 pre-fix splitter 39 failed, M2 closer lookbehind removed 6, M3 section sign removed 1, M4 terminal-stop guard removed 9, M5 operators added to the opener class 8, M6 all-caps callout exemption reverted 1, M7 ceiling raised to 200 4, M8 undocumented glyph widening 1; both controls 65 passed). 218 over-ceiling sentences across the same 30 documents.", "why": "AUT-PD-142. `lint_readability` is the instrument behind publish_bar clause 7 (`readable_enough_to_review`), and the miscount was holding PUB-ATR, PUB-BIOMARKER-DEP and PUB-TXN-DEPENDENCY below the bar on sentences that were never over it. The row was filed rather than fixed in 2026-08-28 because research-loop §6 forbids the cycle a bar blocked from changing it; this is the later cycle the row says may make the identical change.", "self_serving_check": "ANSWERED: NO, and the direction is checked rather than asserted. (1) NO BAR MOVED: SENTENCE_CEILING is unchanged at 60, pinned by two tests, and research/autonomy/publish_bar.py was not modified. (2) THE BASELINE DID NOT MOVE AND NEEDS NO RE-PIN: all 11 pinned caution_per_1000w values in readability-baseline.json are identical before and after, because a splitting change repartitions text without removing any of it; the file was not touched. (3) THE SUITE CONSTRAINS THE SPLITTER MORE, NOT LESS: 10 of the 65 tests are NEGATIVE cases pinning openers that must NOT split (em dash, arrows, math operators, a bare citation bracket, a mid-sentence glyph, a glyph with no preceding stop), because a FALSE split understates a length and an understated length walks past the ceiling. The three loosening mutations M4, M5 and M7 are all caught. (4) THE FIX DOES NOT RESCUE THE PAPERS THAT WANTED RESCUING: 213 of the 218 remaining flags are real prose, PUB-DEGRADER still fails with 145, and this seat edited no manuscript."}
```
