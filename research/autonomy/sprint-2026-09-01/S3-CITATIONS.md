---
id: DOC-SPRINT-2026-09-01-S3
title: "S3-CITATIONS — the roadmap's line-citation checker was reading a third of its own file, and the fusion-partner years were bound to nothing"
level: L3
kind: process
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
---

# S3-CITATIONS — the line-citation checker's denominator, and the fusion-partner year binding

**Item(s):** AUT-PD-134, AUT-PD-133, AUT-PD-031
**Owned paths:** `research/manuscripts/line_citations.py` · `research/manuscripts/tests/test_line_citations.py` ·
`research/manuscripts/tests/test_fusion_partner_author_years_are_bound_to_the_citation_map.py` (new) ·
`research/autonomy/sprint-2026-09-01/S3-CITATIONS.md`
**Started/Finished (UTC):** 2026-09-01T18:33Z / 2026-09-01T19:15Z

## Verdict

**FIXED (all three), with one hand-off the driver must complete in two commands.**

- **AUT-PD-134 — CONFIRMED LIVE and fixed.** The checker reached **18 of the roadmap's 56 citations (32 %)**
  and reported a denominator of 42; **14 citations produced no output at all.** Four distinct resolver
  mechanisms were behind it, each measured. It now reaches **27 of 56 (48 %)** and reports **every** one.
  ⛔ **Nine roadmap citations point at the wrong line and were invisible to the old resolver** (eight of
  them confident enough for `--fix`), so `line_citations.py` exits 1 and one test is red until the driver
  runs `--fix` on a settled tree. See the hand-off below — and note that a **concurrent seat was editing
  the degrader paper while I measured**, so the total drift count moves; the nine are identified there by
  their quoted phrase rather than by a line number.
- **AUT-PD-133 — CONFIRMED LIVE and fixed, with NO manuscript edit needed.** Every author-year mention in
  the fusion-partner corpus is already correct against the citation map; what was missing was the binding.
  A new guard supplies it. **`emc-fusion-partner-stratification.md` was not touched.**
- **AUT-PD-031 — the merged fix is REFUTED as a live defect; its named residual is now half-settled.**
  `--fix` already names the downstream copies and exits non-zero. The residual ("the tool NAMES 16
  hand-written carriers and CHECKS none, and deciding which are pinned-by-design is a reading job nobody has
  done") is narrowed: the tool now reports which carriers name a basis commit in their own header.

---

## What I measured

### AUT-PD-134 — the denominator was the defect

`python3 research/manuscripts/line_citations.py`, on the trunk before any change:

```
line_citations: 18 correct · 0 DRIFTED · 24 unresolved (42 quoted citations)
```

Independently re-derived, because that line is the claim under test:

```
total `:NNNN` citations in the roadmap:            56
citations that reached scan() (had a quote):       42
citations scan() resolved to a line:               18
→ 32.1 % of the file's citations were CHECKED. 25 % were never mentioned in any line of output.
```

**How the 14 disappear:** `scan()` looked back 400 characters for a `*"…"*` and `continue`d when it found
none — no record, no print, and not in the denominator. Their contexts, read out of the roadmap: eight are
the **second member of a citation list** (`` (`:387–394`, `:2549`) ``), five carry **no quote at all**, and
one is the **trailing form** `` `:2508`: *"…"* `` the backwards-only search cannot see.

**The 24 "unresolved" were not one defect.** The row said the two halves must not be fixed as one, and the
reading confirms it — four separate mechanisms, each reproduced:

| # | mechanism | evidence, on the 2026-09-01 trunk |
|---|---|---|
| 1 | **The lookback window manufactured phantom quotes.** `text[start-400:start]` cuts through an earlier quote, leaving its closing `"*` to pair with the next opening `*"`. | `:2140` was attached to `'* (`:2200–2203`) \| ✓ **PASSES, in scope** \| `R11` \|…'` — a string that appears in no manuscript and never could. |
| 2 | **`*"…"*` matched inside `**"…"**`.** Bold-plus-quotes is ordinary prose; the old pattern matched the second asterisk of a `**"`. | A span opening at `**"no" outcome that SAVES the program effort**` ran ~900 characters on and swallowed the genuine quote `*"**four** NR4A3-unique cysteines"*` (roadmap :2651). |
| 3 | **A quote can follow its citation.** Three spellings on the trunk: `` `:2508`: *"…"* ``, `` `:2478` says *"…"* ``, `` SI `:229` — *"…"* ``. | All three missed; worse, `:2478` then reached BACK past `` SI `:229` `` and took its quote, so one gap produced one lost citation and one mis-attributed one. |
| 4 | **A quote can wrap over more than two lines**; `_find` joined at most two. | `:2409` is wrong by **+68** lines and `:552` by **+15**; both were reported as unresolvable paraphrases. (Absolute targets are not quoted here — a concurrent seat moved the paper mid-measurement. The offsets are the finding.) |
| 5 | **`_norm` did not fold the markdown backslash escape.** The roadmap quotes from inside a TABLE CELL, where `\|` must be escaped; the paper writes `\|` bare. | `*"a wedge contribution of roughly **\\\|S\\\| ≳ 0.65 kcal/mol** (2σ)"*` (`:1798`) failed for that alone, and the citation is wrong by **+73** lines. |

**The remaining unresolved really are staleness, and that is now a measured statement rather than an
assumption.** After the five fixes, 14 citations are `not_found`. A second, independently written
normaliser (in the test file, sharing no code with `_norm`) can locate the quoted text for **none** of
them. Two are the same phrase cited twice at different lines (`:387`/`:2549`, `:1405`/`:1425`), which is
the shape that makes a first-match fixer dangerous.

**Two cases genuinely cannot be resolved and are now labelled, not counted as rot:** three citations quote
*"must clear"* (10 characters — under the resolver's own floor, so it declines to look rather than fails to
find), and one `:546` sits INSIDE a quoted phrase and is part of the quotation.

**The guard on the guard permitted all of it.** `assert len(resolved) >= 10` sat below the live count of 18
and far below 56, so the checked share could halve without anything going red.

### AUT-PD-133 — the years were unbound, and they are also all correct

Read out of `emc-fusion-partner-pooling.json` → `citations` (a machine-readable row per source: `authors`,
`year`, `pmid`) and checked against every tracked `.md` beside it:

```
emc-fusion-partner-stratification.md      61 author-year mentions bound, 0 mismatched
emc-fusion-partner-correction-register.md 45 author-year mentions bound, 0 mismatched
partner-event-counts-2026-08-08.md        24 author-year mentions bound, 0 mismatched
author-year mentions written beside a PMID:  13, 0 mismatched
```

⭐ **So the manuscript needed no correction and did not get one.** AUT-PD-133 asked for a *binding*, not a
repair, and writing a "correction" into a document whose years are right would have been a fabricated fix.

**Why nothing saw it, established by reading the instruments rather than assuming:** `lint_claims` reads
claim STRENGTH and a wrong year is a claim of identical strength about a different paper; `lint_citations`
anchors identifier PROVENANCE and an author-year mention carries no identifier to anchor; the sibling
guard `test_fusion_partner_prose_asserts_the_relations_its_artifact_computes.py` owns a `_NAMED_SERIES`
regex that does read author-year pairs — but it is applied only inside the superlative-comparison sentences
that test decides (`_NAMED_SERIES` appears at one call site, line 497). A year drifting anywhere else
passed every instrument in the repository.

### AUT-PD-031 — the merged half holds; the residual is narrowed

Reproduced end to end on a **scratch copy of the tree**, never the live one: insert a blank line into the
paper, run `--fix`.

```
rewrote 7 citation(s) in research/manuscripts/nr4a3-program-map.md
⛔ THIS IS NOT THE WHOLE TREE. …
⛔ THE REWRITE SUCCEEDED AND THE TREE IS NOT CONSISTENT YET. 1 generator reports its committed copy stale:
     python3 research/modalities/instrument_census.py
        instrument-census.json has DRIFTED from the roadmap -- regenerate it
        instrument-census.md has DRIFTED from the roadmap -- regenerate it
→ exit 1
```

The 2026-08-27 incident does not reproduce: the fixer names the second copy and cannot be read as done.
`instrument_census.py --check` is confirmed in `scripts/preflight.sh:747`'s generated-artifact loop.

**The residual, read rather than guessed** — 430 citations across 16 hand-written carriers:

| citations | carrier | header |
|---:|---|---|
| 131 | `research/manuscripts/program/map-audit-strategy.md` | **names basis commit `f67d0781`** |
| 9 | `research/manuscripts/aso/fusion-junction-aso-paper-redteam-round7.md` | **names basis commit `100816ab3`** — *"every finding below is anchored on a verbatim quote and a line number at commit"* |
| 3 | `research/manuscripts/aso/fusion-junction-aso-paper-redteam-round8.md` | **names basis commit `4cc0799`** |
| 287 | the other thirteen | declare nothing either way |

⛔ **143 of the 430 are pinned by design and must never be advanced.** The other 287 are **unchecked, not
clean** — an absent declaration is not a declaration of currency, and the tool now says exactly that.

---

## What I changed

### `research/manuscripts/line_citations.py`

- **`scan()` returns one record per citation, always**, each carrying a `status` from a new `STATUSES`
  tuple (`ok`, `drifted`, `not_found`, `ambiguous`, `quote_too_short`, `no_quote`, `inside_a_quote`).
  Nothing is dropped; the summary's denominator is the file's own citation count.
- **Quotes are located over the whole file once** (`QUOTE.finditer(text)`), killing the phantom-quote class.
- **`QUOTE` gained `(?<!\*)` on the opening only.** The closing deliberately has no matching guard: the
  trunk writes a citation quote inside a bold run (`**SI `:229` — *"…"***`), and `(?!\*)` drops it. The
  asymmetry is measured (mutation M2), not aesthetic.
- **`TRAILING`** handles a quote that follows its citation, with a deliberately narrow grammar —
  punctuation and one attributive verb, read off the trunk. Widening it to "the nearest quote in either
  direction" was tried and rejected on measurement: it gave `:92–99`, a citation with no quote at all, the
  quote of the next sentence.
- **`_find` returns every match**, so a quote occurring twice is `ambiguous` and is never rewritten; the
  join window is derived from the needle's length instead of fixed at two lines; a match must BEGIN on the
  returned line (without that anchor a long window matches from almost any start and everything reads
  ambiguous — the failure that looks like strictness).
- **`_norm` folds the markdown backslash escape**, symmetrically on both sides.
- **`_attach` returns a confidence.** An attachment separated from its quote by another citation or a
  sentence boundary is `confident=False`: still checked, still reported, **never rewritten by `--fix`**.
  This is how the two halves the ledger row said must not be fixed as one are kept apart — correctness is
  answered by refusing to act where the attachment is unclear, staleness by `not_found`, unchanged.
- **`declared_pin` / `PIN_DECL`**, and `report_carriers` now prints each hand-written carrier's citation
  count and whether its header names a basis commit.
- ⛔ **No match was loosened to raise a count.** Every status is still reached by requiring the quoted text
  verbatim under the same typography folding. The elided form `*"A … B"*` now requires each part verbatim
  and in order — its literal meaning, and strictly stronger than matching either part alone. It resolves
  **zero** new citations, which is the finding: the five elided quotes are genuine rot, not resolver blindness.

### `research/manuscripts/tests/test_line_citations.py`

`assert len(resolved) >= 10` is gone. Replacing it:

- `test_every_citation_in_the_roadmap_is_accounted_for` — the record count must equal a `git grep -o` count
  of the roadmap's citations. **Derived twice, by two implementations.**
- `test_the_checker_resolves_every_citation_an_independent_reader_can_resolve` — **the derived floor.** A
  second, independently written normaliser says which attached quotes are genuinely present; every one of
  those must reach a status meaning the checker found it. The bound moves with the tree instead of ageing
  into a formality, and it is deliberately not an equality so `not_found` stays available for real rot.
- Six behavioural tests on a **synthetic tree**, one per mechanism, so a dead resolver fails where the
  message names the cause rather than as "fewer than expected resolved".
- `test_an_unconfident_drift_is_reported_rather_than_swallowed` — `confident=False` buys exemption from the
  fixer, never from the report.
- Two pin-detector tests, including the one-of-a-pair trap (this module quotes a basis-commit declaration
  in its own docstring; a widened header window makes it classify itself).

### `research/manuscripts/tests/test_fusion_partner_author_years_are_bound_to_the_citation_map.py` (new)

Five tests. Every author-year mention in every tracked `.md` beside the artifact must name the year
`emc-fusion-partner-pooling.json` records; an identifier written beside one must be that source's PMID;
the corpus and the citation-row index are each re-derived by a second implementation (`git ls-files`, and
the artifact's own row count) so a silently narrowed scope goes red; and a synthetic positive control
breaks each fact and requires the checker to notice.

⚠ The expectation is keyed off the artifact's `authors` field, **not** its `short` field — `short` already
contains the string the prose uses (`"Huang 2023"`), so deriving from it would compare the prose against a
copy of itself and pass however far both had drifted.

### Mutation testing — 21 of 21 killed, all in an isolated full-tree copy

Never in the live tree (CLAUDE.md §6: a mutation window is a commit window). The scratch tree also made
the runs immune to the concurrent-seat tree-guard hazard the coordinator flagged.

| | mutation | killed by |
|---|---|---|
| M1 | `QUOTE` loses the `(?<!\*)` open guard | `…bold_quoted_phrase…` |
| M2 | `QUOTE` gains a `(?!\*)` close guard | `…bold_quoted_phrase…` |
| M3 | the trailing form is not consulted | `…quote_that_follows_its_citation…` |
| M4 | the trailing grammar is widened to any nearby quote | 4 tests |
| M5 | the join window goes back to two lines | `…wrapped_over_more_than_two_lines…`, derived floor |
| M6 | a match need not begin on the returned line | 6 tests |
| M7 | `_find` returns only its first hit | `…occurs_twice_is_ambiguous…` |
| M8 | a too-short quote is reported as `not_found` | `…too_short…`, derived floor |
| M9 | every attachment is confident | `…crosses_another_citation…`, drift test |
| M10 | `scan()` drops the citations it cannot check | `…accounted_for…` |
| M11 | `_norm` stops folding the backslash escape | derived floor |
| M12 | `--fix` rewrites unconfident drifts too | `…crosses_another_citation…` |
| N1 | `Huang 2023` → `Huang 2027` in the prose (the row's own ablation) | `…year_the_citation_map_records` |
| N2 | a PMID beside an author-year swapped for another real one | `…that_source_s_identifier` |
| N3 | the diacritic fold is removed | `…covered_whole`, positive control |
| N4 | `_mismatches` never reports anything | positive control |
| N5 | the document corpus narrowed to one file | `…covered_whole`, `…reaches_the_prose` |
| N6 | only citation rows carrying a PMID are indexed | `…covered_whole` |
| N7 | the identifier pattern may cross a full stop | positive control |
| P1 | the header window widened to the whole file | both pin tests |
| P2 | `PIN_DECL` stops matching a basis commit | both pin tests |

⚠ **Two of these were test defects found by the mutation, not by writing:** M1 survived its first fixture
(`**"aside"**` closes one word later and harms nothing — the trunk's shape is `**"quoted" then more words**`,
where the span finds no close until the next real quote), and N3 survived because the assertion ran through
`_mismatches`, which an identity fold also satisfies — `NAMED` never matches `Sjögren`, and a mention nobody
sees cannot mismatch. Both fixtures were rebuilt to the trunk's real shape and both mutations then died.
The fold is load-bearing: **5 accented author-year mentions** (`Sjögren 2003` ×4, `Klubíčková 2022`) would
otherwise drop out silently.

### Gate readings for my change (scoped, per charter §6)

```
pytest research/manuscripts/tests/test_line_citations.py                → 20 passed, 1 FAILED (see hand-off), 15.6 s
pytest research/manuscripts/tests/test_fusion_partner_author_years…py   →  5 passed, 0.44 s
pytest …/test_no_guard_can_silently_not_run.py …/test_no_test_may_write_to_the_tracked_tree.py
                                                                        → 18 passed, 1 FAILED — NOT MINE (below)
```

No run of mine ended in `assert_tree_unchanged` or named a modified path, so none of these timings is void.

---

## ⛔ HAND-OFF THE DRIVER MUST COMPLETE — TWO COMMANDS

`line_citations.py` now exits **1** and `test_no_resolvable_line_citation_points_at_the_wrong_line` is
**red**, because **seven confident drifts are real and the roadmap is not my path.** `line_citations.py`
runs in `tests.yml:165` and in `scripts/fast_checks.py`, so this is visible in CI until it is done.

```bash
python3 research/manuscripts/line_citations.py --fix   # rewrites 7; exits 1 naming the stale census
python3 research/modalities/instrument_census.py       # regenerates the two downstream copies
```

Verified in an isolated copy of the whole tree (taken before the concurrent edit above): after those two
commands the checker reported `26 correct · 0 DRIFTED · 1 drifted-but-unconfident` and the suite was
**19 passed**. The counts will differ on the settled tree; the shape — zero confident drifts remaining,
one unconfident one left for a reader — is what to expect.

⛔ **RUN IT ON A SETTLED TREE, AND DO NOT COPY LINE NUMBERS OUT OF THIS FILE.** While I was writing this,
`git status` showed **another seat editing `research/manuscripts/degrader/nr4a3-degrader-paper.md`**
(53 insertions, 51 deletions, net +2 lines), which moved eleven citations by exactly +2 between two of my
own runs. Every derived line number is a function of a moving tree; `--fix` derives them fresh.

⚠ **AND IT KEPT MOVING.** Three readings of the same checker against the live tree during this seat's
work: `18 correct · 8 DRIFTED`, then `0 correct · 27 DRIFTED`, then `0 correct · 19 DRIFTED · 8
unconfident` — the paper was edited under each. **The stable quantities are the coverage (27 of 56, 48 %),
the full accounting (all 56 reported), and the nine citations the old resolver cannot see.** A raw drift
count taken tonight measures the sprint, not the roadmap.

**The discriminating measurement, and it is clean.** Running the PREVIOUS `line_citations.py`
(`git show HEAD:…`) against the same current tree, beside the new one:

```
OLD resolver, today's tree:  42 quoted · 18 DRIFTED · 24 unresolved
NEW resolver, today's tree:  56 citations · 27 DRIFTED · 14 not-found · 11 no-quote · 3 too-short · 1 quoted
```

The old resolver's 18 are the ordinary +2 shift from that seat's edit — it would have caught those. The
**nine it cannot see** are this seat's finding, identified by the quote rather than by a line number so the
list survives the next edit:

| citation | the phrase it cites | why it was invisible |
|---|---|---|
| `:2508` | *"This paper's claimed contribution is the target's **computational druggability/selectivity, not EMC efficacy**"* | trailing form `` `:2508`: *"…"* `` |
| `:2478` | *"**Every paralogue-selectivity statement in this work is therefore an unvalidated prediction.**"* | trailing form `` `:2478` says *"…"* `` |
| SI `:229` | *"Lead — NR4A3-selective (the validated path)"* | trailing form `` SI `:229` — *"…"* `` |
| `:2200–2203` | *"validates **one contact in one pair**. It does **not** validate E1 …"* | quote wraps over four lines |
| `:2409–2412` | *"**No benchmark yet probes the regime this cross-check would occupy** …"* | quote wraps over four lines |
| `:552–566` | *"…computed under the **pre-harmonized** tracker and **not** re-run under the harmonized one…"* | quote wraps over four lines |
| `:1277–1280` | *"**It is not currently running: the whole ABFE block is deliberately held** …"* | quote wraps over three lines |
| `:1798–1800` | *"a wedge contribution of roughly **\|S\| ≳ 0.65 kcal/mol** (2σ)"* | `\|` escaped in the roadmap's table cell, bare in the paper |
| `:2600–2601` | same quote as `:1277–1280` | **unconfident** — separated from its quote by another citation and a full stop; reported, never auto-fixed |

⚠ **One of them deserves a reader before it is trusted, and the fixer cannot tell.** The roadmap's §4232
calls **SI `:229`** *"Lead — NR4A3-selective (the validated path)"* **the strongest residual over-claim**.
The SI no longer carries that as a heading; the phrase survives only inside a *"⚠ Superseded, retained:"*
note recording that the heading was CHANGED. `--fix` will repoint it there, which is where the string is —
but the roadmap's sentence about it is then stale in a way no line number expresses. **That is a content
correction for whoever owns the roadmap, not a fixer's job.**



## What I could not do, and what it is actually waiting on

- **The roadmap itself** (`research/manuscripts/nr4a3-program-map.md`) — not my path, and it is the file
  most likely to have a second seat in it. Waiting on the driver's two commands above. Not blocked on
  anything outside the repository.
- **The 287 unchecked citations in thirteen hand-written carriers** — waiting on a *reading*, not on code.
  A fixer cannot help: this repository uses the same `:NNNN` syntax for lines in `.py` files, in sibling
  `.md` files and in the roadmap, so "repair" would mean guessing a target, which is how a fabricated
  citation gets written. The machine-settleable half is done. Proposed follow-up row below.
- **Whether a correctly-dated citation is APT** — the new year guard answers "is this the year the artifact
  records" and nothing else. A correct year on the wrong paper is invisible to it, and it says so.

## ⚠ Not mine, for the driver's attention

`pytest research/manuscripts/tests/test_no_guard_can_silently_not_run.py` is RED on
`test_every_remaining_skip_in_the_deposit_suite_is_a_decision_somebody_took`, naming
`test_the_census_artifact_and_the_guard_corpus_are_a_pair.py:279` (a new untracked file) and
`test_the_deposit_the_papers_cite_is_current.py:270` (modified). Both belong to another seat this wave.
Each needs `NOT IN CI` / `SKIP IS DELIBERATE` beside the skip, or the skip turned into a `pytest.fail`.

## Ledger rows the driver should write

| id | `what` | `kind` | `state` |
|---|---|---|---|
| **AUT-PD-134** | *close.* `line_citations.py` reached 18 of 56 citations (32 %) and never mentioned 14 of them; five resolver mechanisms measured and fixed, coverage 27/56 (48 %) with all 56 reported; the typed `>= 10` floor replaced by a derived floor against an independent normaliser plus a synthetic liveness suite; 12/12 mutations killed. **Residual, stated rather than implied: 14 citations remain `not_found` and an independent reader can locate none of them — that is measured staleness, not resolver blindness.** | `process_defect` | `done` |
| **AUT-PD-133** | *close.* Author-year mentions in the fusion-partner corpus are now bound to `emc-fusion-partner-pooling.json`'s citation rows by `test_fusion_partner_author_years_are_bound_to_the_citation_map.py`; the row's own ablation (`Huang 2023`→`Huang 2027`) is mutation N1 and goes red. **130 mentions across three documents were already correct, so no manuscript was edited** — the defect was the missing binding, not a wrong year. 7/7 mutations killed. | `process_defect` | `done` |
| **AUT-PD-031** | *keep open, narrowed.* The merged fix holds — reproduced on a scratch tree: `--fix` names the stale census and exits non-zero. The residual is now measured rather than described: **430 citations across 16 hand-written carriers; 143 are pinned by design in three files that name their basis commit in their own header (`f67d0781`, `100816ab3`, `4cc0799`) and must never be advanced; 287 in thirteen files declare nothing and are UNCHECKED, not clean.** `report_carriers` prints the split. What remains is a reading job per carrier, and a fixer cannot do it: the same `:NNNN` syntax addresses `.py` files, sibling `.md` files and the roadmap, so a target would have to be guessed. | `process_defect` | `queued` |
| **NEW (propose)** | ⚠ **ELEVEN ROADMAP CITATIONS CARRY NO QUOTED PHRASE, SO NOTHING CAN EVER CHECK THEM, AND THREE MORE QUOTE TOO LITTLE TO IDENTIFY A LINE.** Measured 2026-09-01: after the AUT-PD-134 fix, 11 of 56 citations are `no_quote` and 3 quote *"must clear"* (10 characters, under the resolver's floor). These are not resolver defects — the tool reports them correctly — they are citations written in a form that is unverifiable by construction, three of the eleven are the second member of a citation list (`` (`:387–394`, `:2549`) ``) where the quote sits on the first, and the other eight cite the paper with no quotation at all. **The remedy is a prose convention, not code:** give the second member its own short quote, or drop it. Cheap, and it converts 14 permanently-unverifiable references into checkable ones. | `process_defect` | `queued` |
| **NEW (propose)** | ⚠ **TWO PAIRS OF ROADMAP CITATIONS SHARE ONE QUOTED PHRASE WHILE CITING DIFFERENT LINES** — `:387–394`/`:2549` and `:1405`/`:1425`. Both pairs are `not_found` today, so nothing has gone wrong yet. If either phrase becomes findable, a first-match fixer collapses both onto one line silently, with every citation still pointing at a real line. `_find` now refuses (`ambiguous`) rather than picking, so the hazard is contained in the tool; the **documents** still carry two references that cannot both be right about the same quote, and that is a reading job. | `process_defect` | `queued` |

## Amendment record for the driver

`**/tests/**` is governed and I may not append to `amendments.jsonl`. Ready to paste:

```json
{"utc": "2026-09-01T19:15:00Z", "seat": "S3-CITATIONS", "sprint": "sprint-2026-09-01", "items": ["AUT-PD-134", "AUT-PD-133", "AUT-PD-031"], "paths": ["research/manuscripts/line_citations.py", "research/manuscripts/tests/test_line_citations.py", "research/manuscripts/tests/test_fusion_partner_author_years_are_bound_to_the_citation_map.py"], "kind": "guard_widened_and_guard_added", "what": "line_citations.py checked 18 of the roadmap's 56 citations (32%) and dropped 14 without reporting them; five resolver mechanisms measured and fixed (phantom quotes from a truncated lookback window, `*\"` matching inside `**\"`, the trailing quote form, a two-line join limit, and an unfolded markdown backslash escape), taking coverage to 27/56 with every citation reported under an explicit status. The typed `assert len(resolved) >= 10` guard-on-the-guard is replaced by a floor derived from an independently written normaliser plus a synthetic liveness suite. `--fix` now refuses to rewrite an attachment separated from its quote by another citation or a sentence boundary, which keeps the correctness half and the staleness half apart. A new guard binds every author-year mention in the fusion-partner corpus to emc-fusion-partner-pooling.json's citation rows (AUT-PD-133's own ablation, Huang 2023 -> Huang 2027, is mutation N1). report_carriers now reports which hand-written carriers name a basis commit in their header, settling the machine-settleable half of AUT-PD-031's residual.", "mutations_run": 21, "mutations_killed": 21, "mutation_venue": "isolated full-tree copy under the seat scratchpad, never the live tree", "no_match_was_loosened": "every status is still reached by requiring the quoted text verbatim under the same typography folding; the elided form now requires each part verbatim and in order and resolves zero new citations, which is the evidence that the five elided quotes are genuine rot", "manuscript_edited": false, "hand_off": "the driver must run `python3 research/manuscripts/line_citations.py --fix` then `python3 research/modalities/instrument_census.py`: seven confident drifts in the roadmap are real and that path was not this seat's to edit"}
```
