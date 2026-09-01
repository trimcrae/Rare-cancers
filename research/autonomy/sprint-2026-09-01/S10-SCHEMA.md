---
id: DOC-SPRINT-S10-SCHEMA
title: "S10-SCHEMA — a hand-typed fact beside the machine-derived one, twice"
level: L3
kind: process
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
---

# S10-SCHEMA — a hand-typed fact beside the machine-derived one, twice

**Item(s):** AUT-PD-030, AUT-PD-181
**Owned paths:** `research/autonomy/ledger_io.py`, `research/autonomy/receipt_schema.py`,
`research/autonomy/ledger_schema.py` (NEW), `research/autonomy/tests/`, `scripts/tests/`,
this file
**Started/Finished (UTC):** 2026-09-01T18:33Z / 2026-09-01T19:15Z

## Verdict

**FIXED (AUT-PD-030) · PARTIAL (AUT-PD-181).** Both defects were reproduced before being touched;
AUT-PD-030 is closed by a new `ledger_schema.py` bound at the one programmatic write choke point and
at a default-tier test, and the reproduction turned up **two near-miss field names already live in
the committed ledger** that nobody had found; AUT-PD-181's guard is built and green, but the
*honest* fix — deriving the sentence in the generator — needs
`research/modalities/census_route_expression_grading.py`, a path this seat does not own.

---

## What I measured

### AUT-PD-030 — the defect is live, and it is not only a residual risk

**Reproduction, on a scratch copy of the ledger** (`/tmp/.../scratchpad/tree/autonomy/`, never the
live file). A row was appended whose `what` names no outward verb — *"Regenerate the route-expression
grading table and refresh the derived counts."* — carrying `require_trimcrae: true`, one deletion
from `requires_trimcrae`. Against that copy:

| checker | reading |
|---|---|
| `continuity.ready()` | **offers the row as ready to run** (`'AUT-PD-999' in ids` → `True`) |
| `continuity.unclassified_outward()` | **does not flag it** (`False`) |
| `prepush_ledger_guard.py` | exit 0, no output — it checks duplicate ids and nothing else |
| `admissibility.py`, `health.py` | not one line naming the row or the key |

That is AUT-PD-017's category (c) — the failure that reads GREEN — on the one field CLAUDE.md §3
exists to protect. `continuity._why_not_ready` (line 181) tests `requires_trimcrae` for
**truthiness**, so a misspelling is indistinguishable from an absent key, and
`unclassified_outward` (line 269) only rescues the row when its own `what` matches a regex over
publish/submit/deposit verbs.

**And the drift has already happened, twice, in the committed file.** Every one of the 89 field names
in the ledger was run back through the new detectors as if it were unknown. Two are near-misses of a
field a reader keys off:

| drifted spelling | rows | governed spelling | the reader that cannot see it |
|---|---|---|---|
| `_closed_by` | 3 (AUT-068, AUT-PD-129, AUT-PD-146) | `closed_by` | `claim.py:429` reads `closed_by` only — those three rows report **no closer** while the cycle id sits in the row |
| `_outcome` | 5 (AUT-PD-099, AUT-PD-166, AUT-PROP-051/053/054) | `outcome` | `stuck_clock.PROGRESS_FIELDS` and `out_of_ideas.py` list `outcome` only — an edit to `_outcome` **is not progress** in the instrument that measures progress |

A third fork is **half**-mitigated. `lease_released` / `_lease_released` are both carried by
`stuck_clock.py:184-185`, so progress is seen either way — but `queue_view.DELIVERABLE_FIELDS` is
`("what", "lease_released")` and knows only the bare spelling, so a row recording its deliverable in
`_lease_released` alone is invisible to `already_landed()`. **AUT-PROP-012 carries both at once, with
different text in each.**

Two more forked pairs are currently safe only because **the readers were patched to accept both
spellings** rather than the drift being fixed: `requires_trimcrae_why` (79 rows) /
`_requires_trimcrae_why` (87 rows) sit side by side in `stuck_clock.py:162-163` and
`out_of_ideas.py:161-162`. So the vocabulary has forked five times already, and in three of the five
some reader cannot see one of the spellings. What had not happened yet is a fork onto a name **no**
reader knows — which is what the gate now prevents.

**One thing refuted:** the ledger header's five typed totals (`n_by_kind`, `n_by_state`, `n_clamped`,
`n_unscored`, `n_unscored_open`) all **agree exactly** with the rows today. They are derived by
`priority.py --write`; nothing was measuring the agreement, so a check was added, but there is no
live drift.

### AUT-PD-181 — the instance is closed, the class was still unguarded

`git log` shows the RT-ALK-HIT sentence was corrected in `35fb816f5` (AUT-PD-110). Confirmed on the
committed artifact: the false sentence is gone and survives only as a quoted retraction inside the
corrected paragraph. **`grep -rln census_route_expression_grading --include=*.py` returns exactly one
file** (`census_novelty_audit.py`, an unrelated consumer) — **no test, no linter, no gate anywhere
reads that module or its artifact for prose/table agreement.** So the instance was fixed and the
class was not.

The row also asks two specific questions, and both are now answered from the data rather than
assumed:

- **RT-NR2F1's absolute claim is TRUE.** *"NR2F1 is NOT READABLE on either platform"* checks out
  against its own table: `readable=False` on both `GSE24369` and `GSE4303-GPL3290`. The row warned
  against assuming it wrong; it is right.
- **The sweep of the other 15 route blocks finds no second contradiction.** 21 machine-checked
  assertions across all 16 blocks, 0 failures.

Coverage, stated honestly because a guard whose reach is invisible is worthless:

```
readability assertions checked   5   (RT-ALK-HIT 3, RT-NR2F1 2)
direction  assertions checked   16   (7 routes)
routes with zero assertions      7   — their prose speaks about MODULES and GROUPS, not about a
                                       gene on a platform, and is not reducible to a table cell
clauses reported unreducible     1   — RT-ALK-HIT.observed, a conjunction that mixes polarities
```

`build() == committed` holds, so the artifact is current and the prose checked is the prose read.

---

## What I changed

### `research/autonomy/ledger_schema.py` — NEW (why a new module, and what it chose)

AUT-PD-030 asked for exactly this ("a `ledger_schema.py` … that owns a whitelist"), and it is
separate from `receipt_schema.py` on purpose: `contract_check.py` derives receipt requirements from
that module's `*_KEY` constants and covers *"the enforcer that FAILS THE COMMIT … and no other
reader"*, and the two vocabularies have opposite failure modes — receipts are immutable history that
needs a grandfather cutoff, the ledger is one live-edited file that does not. **`receipt_schema.py`
was not touched.**

**The design question, answered rather than dodged.** A schema that rejects every unknown field
breaks the next legitimate field addition and gets switched off; one that accepts every unknown field
catches nothing. Neither is the defect. The defect is *a name that looks like a name a reader uses*:

```
a key in the vocabulary                                   -> fine
a key not in the vocabulary, FAR from every governed name -> fine, no registration needed
a key not in the vocabulary, NEAR a governed name         -> REFUSED, naming the reader it fools
```

"Near" is four detectors, all stdlib: **alias** (normalised equality — casing, stray or leading
underscore), **edit** (whole-name Levenshtein, budget 1 under 10 chars / 2 at or above), **stem**
(leading tokens *exactly* one edit apart), **reorder** (same tokens, different order). The stem rule
exists because pure edit distance **does not reach the ledger row's own worked example**: `owned_by`
is four edits from `owner` and would have sailed through any sane distance budget; `owned` is one
edit from `owner`. "Exactly one" and not "zero" because `blocked_by` and `blocked_evidence` are both
real and share a stem — a zero-distance stem rule refuses every legitimate sibling field.

Detector targets are the **governed** names only (44 of them, each annotated with the reader a
misspelling would fool). A typo of an unread annotation costs nothing, and making dated one-offs like
`_CORRECTION_2026_09_01` detector targets would be a permanent maintenance tax for no protection.

**What it cannot catch, written into the module so nobody reads the gate for more than it measures:**

1. **An absent field.** Omitting `requires_trimcrae` is the default (163 of 344 rows) and is
   indistinguishable from forgetting. That question is `unclassified_outward()`'s, and it answers it
   with a regex over the row's own prose — therefore only partly. **A field-name schema cannot help
   with a name that was never typed.** This is the largest residual.
2. **A typo that is itself a real field** — writing `evidence` for `blocked_evidence`.
3. **A typo of a descriptive (unread) field** — deliberate, see above.
4. **A wrong value under a right name** — `value_problems()` covers `requires_trimcrae` (must be a
   real bool, because `null`/`0`/`""` fall through to *ready* exactly as an absent key does) and
   `state` (must be one of the six live values), and nothing else.

**The value-shaped half, added after the coordinator's mid-task notice.** `ids.next_entry_id` began
minting `AUT-PD-204-6b009680` tonight — a session discriminator, because two concurrent sessions
provably minted `AUT-PD-204` from one committed ledger. `id_problems()` accepts **both** shapes and
does so by calling **`ids.parse_entry_id`, never by writing a second regex**: a module about one fact
having one home may not open a second home for the id format on its way to saying so, and a test
(`test_the_id_shape_is_read_from_its_one_home`) proves it by monkeypatching `ids.parse_entry_id` to
refuse and watching the schema's verdict follow. It also points the **same four detectors at the id
prefix**, because a prefix is a namespace — `ids.next_entry_id` counts ordinals within one — so
`AUT-PDD-201` opens a private namespace that collides with nothing and is read by nobody. Measured:
all 344 committed ids parse; none carries a discriminator yet; the seven live prefixes are AUT-PD
(199), AUT (81), AUT-PROP (56), AUT-BIX (3), AUT-RT (2), AUT-COV (2), AUT-INC (1).

⚠ **One relaxation, measured rather than assumed, and it is exactly one thing.** Enforcing the id
shape inside `write_ledger` refused **seven existing tests at once**, all of them laying fixtures
like `AUT-X` and `AUT-TEST-APPEND` on temp paths. A fixture id is not a ledger id and there is
nothing to protect there — a real writer takes its id from `ids.next_entry_id`, which mints a valid
one by construction, so the only malformed ids that can reach the committed file are hand-authored,
and those never pass through `write_ledger` at all. The write path therefore tolerates an unparseable
id; **the near-miss prefix is still refused on both paths**, and the committed-file gate keeps the
shape check at full strength. `test_the_write_path_tolerates_a_fixture_id_but_not_an_invented_namespace`
pins all three halves of that so the relaxation cannot quietly widen.

**Anti-circularity.** The vocabulary is a reviewed snapshot of the committed ledger, so the file
passes it by construction; the gate is **prospective**. Rather than let that pass unremarked, every
committed name is run back through the detectors as if unknown
(`test_no_committed_field_name_is_a_near_miss_of_a_governed_one`) — that is what found `_closed_by`
and `_outcome`. They are grandfathered in a named `LIVE_ALIASES` block that `main()` **prints on
every run**, on `receipt_schema.py`'s own precedent (*"the pre-cutoff drift is REPORTED rather than
hidden, because the ledger item was filed against a checker that hid what it could not read"*), and
the test asserts that set can only **shrink**. One further detector hit, `_CLOSED_2026_09_01` against
`closes_clause`, is a real stem-rule false positive on a dated one-off note and is dismissed **by
name with its reason**, not by a heuristic that would dismiss the next one too.

**Adding a field is one line.** A new name far from everything needs nothing at all
(`blocked_since`, `review_round`, `gpu_hours`, `seat`, `_sprint_2026_09_01` all pass untouched — this
is tested). A new name that genuinely sits beside a governed one goes in `DESCRIPTIVE_FIELDS`, and
the point of that line is that adopting a near-name becomes a **decision instead of an accident**.

### `research/autonomy/ledger_io.py` — the schema bound to the one choke point

`write_ledger` already refuses an inadmissible score (`admissibility.check_write`); it now also
refuses a near-miss field name (`ledger_schema.check_write`), under the same `check` flag, raising
before anything is written. Header-total drift is **deliberately excluded** from this path: a writer
mid-way through adding rows has not re-derived the header yet, and `priority.py --write` — the thing
that fixes it — is itself a writer.

⚠ **This is not the whole gate and the module says so:** most ledger rows are hand-authored JSON that
never passes through this function. The test below is the other half.

### `research/autonomy/tests/test_a_near_miss_field_name_cannot_enter_the_ledger.py` — NEW

50 tests, **all failing before the module existed and passing after**. `research/autonomy/tests` runs
in `preflight.sh`'s **default** tier (the gate-13 line, `preflight.sh:1160`), so a hand edit is caught
at the commit rather than by CI minutes later. It asserts: the sharpest edge is refused *and the
message names the reader*; twelve concrete typos are caught; ten plausible new fields are allowed
with no registration; the anti-circularity sweep; the two live aliases are reported; the bool and
state value checks; the header totals; and — the binding — that `write_ledger` actually calls the
schema and leaves **no partial file** when it refuses; both id shapes are legal; an id that is
not an id, and an id prefix one edit from a real one, are refused; and the write-path relaxation is
exactly one thing and no wider.

### `scripts/tests/test_a_generated_prose_summary_cannot_contradict_its_own_table.py` — NEW

8 tests, green. `scripts/tests` is in the same default preflight tier. It imports the generator and
checks the prose **as the generator emits it** (not only as committed), so there is no window where
the source is wrong and the guard is green because nobody has regenerated; it also asserts
`build() == committed`.

Two false-positive hazards are handled explicitly rather than discovered later in a red build:

1. **A retracted sentence quoted inline.** RT-ALK-HIT's corrected paragraph quotes the false sentence
   so a reader can see what changed; a naive checker fires on the retraction the correction was
   written to record. A quoted span is stripped **only** when a retraction cue sits in the 220
   characters before it — the shape `lint_consistency.py` already uses. ⛔ And that is an escape
   hatch, so it is mutation-tested in both directions: a quoted claim with **no** cue in front of it
   must still be checked, or quoting becomes a way to smuggle an unchecked claim past the guard.
2. **A group claim that names a member.** *"the GDNF-family ligands are LOWER on both"* is about a
   group mean, and GDNF-the-gene is **+0.027** on GPL6244. Measured: without the group-noun exclusion
   this clause is the **only** failure on a green artifact. Direction clauses containing group
   language are skipped, and so are ones where the symbol is not the clause's subject.

**Mutation-tested, on deep copies in memory, never on the tree.** Restoring the original twenty-day
sentence turns the guard red; flipping RT-ARGININE's direction turns it red; claiming the genuinely
unreadable NR2F1 *is* readable turns it red — the polarity the historical error never ran in.
Coverage floors (`checked >= 5`, `checked >= 16`) are asserted so the guard cannot go green by
quietly ceasing to check.

The ledger-schema guards were mutation-tested the same way (`scratchpad/mutate_schema.py`, seven
mutations, all behaved as predicted): disabling `near_misses` silences `field_problems`; disabling
the stem rule lets `owned_by` escape `owner`; disabling normalisation lets `requiresTrimcrae` escape;
unbinding the schema from `write_ledger` lets the typo row **land on disk**.

---

## What I could not do, and what it is actually waiting on

- **AUT-PD-181's honest fix — deriving the readability sentence — is not done.** It requires editing
  `research/modalities/census_route_expression_grading.py` so each route block emits its readability
  claim from `genes` instead of typing it. **Waiting on: path ownership, nothing else.** Charter rule
  2 says write the requirement rather than take the file. The guard shipped here is explicitly the
  second-best fix and its own docstring says it should be **deleted, not extended**, the day the
  sentence is derived.
- **The prose guard has no standalone `--check` entry point**, because its natural home
  (`research/modalities/prose_table_agreement.py`, plus a `preflight.sh` gate) is two more paths this
  seat does not own. It runs under pytest in the default tier, which makes it a build-failing gate
  today; a module would make it runnable by hand. **Waiting on: path ownership.**
- **The eight rows on drifted spellings were not renamed.** `_closed_by` → `closed_by` (3 rows) and
  `_outcome` → `outcome` (5 rows) is a `research-ledger.json` edit, and no seat may touch that file
  this sprint (AUT-PD-171). **Waiting on: the driver.** Deleting `LIVE_ALIASES` afterwards makes the
  detectors refuse those spellings for good; the test asserting the set can only shrink is already in
  place.
- **I did not run `./scripts/preflight.sh`.** Charter §6: that is the driver's, once, on a settled
  tree. A full `pytest research/autonomy/tests` run from a seat also measures nothing here — the
  suite's `conftest.py` installs `tracked_tree_guard`, which asserts the tracked tree is unchanged at
  session finish, and eleven seats are mutating it. I ran the scoped sets instead.

**⚠ ONE THING THE DRIVER SHOULD KNOW BEFORE COMMITTING.**
`test_the_headers_typed_totals_are_checked_against_the_rows` compares the ledger's five typed header
counters against the rows. They agree right now. **If the driver hand-writes this sprint's ledger
rows without re-running `python3 research/autonomy/priority.py --write`, that test reds the default
preflight tier.** That is the check working as intended (CLAUDE.md §1: a total is DERIVED, never
typed) and the failure message names the exact command — but it is a new way for the sprint's final
commit to go red, and it is better read here than at 3 a.m. in a preflight log.

---

## Gates I ran

| command | result |
|---|---|
| `python3 research/autonomy/ledger_schema.py --check` | exit 0 — 344 rows, 44 governed names, 0 problems, 2 live aliases reported |
| `pytest research/autonomy/tests/test_a_near_miss_field_name_cannot_enter_the_ledger.py -q` | **50 passed** in 0.77 s |
| `pytest scripts/tests/test_a_generated_prose_summary_cannot_contradict_its_own_table.py -q` | **8 passed** in 0.65 s |
| `pytest` over the 8 existing suites that call `write_ledger`, plus `test_ids_cannot_collide.py` | **187 passed** in 5.44 s — the new refusals break no existing writer. ⚠ An interim version refused 7 of them by enforcing the id SHAPE on the write path; that is the measurement behind the one relaxation, not a hypothetical |
| `scratchpad/mutate_schema.py` (7 in-memory mutations) | all behaved as predicted; module restored and still green |

---

## Ledger rows the driver should write

**1 — close AUT-PD-030.**
`state`: `done` · `closed_by`: this seat · `outcome`:
> ⭐ CLOSED, AND THE REPRODUCTION FOUND LIVE DRIFT THE ROW ONLY PREDICTED. `research/autonomy/ledger_schema.py` owns a 44-name governed vocabulary, each annotated with the reader a misspelling would fool, and refuses an unknown key that is an alias / edit-distance / stem / reorder near-miss of one while allowing an unknown key that is far from all of them — so a future field costs no edit and a typo costs a red build. Bound at `ledger_io.write_ledger` (programmatic writers) and at `research/autonomy/tests/test_a_near_miss_field_name_cannot_enter_the_ledger.py`, which runs in preflight's DEFAULT tier (hand-authored rows). ⛔ REPRODUCED FIRST, on a scratch copy: a row carrying `require_trimcrae: true` on prose with no outward verb was OFFERED AS READY by `continuity.ready()`, NOT flagged by `unclassified_outward()`, and drew nothing from `prepush_ledger_guard.py`. ⭐ THE STEM RULE IS WHAT REACHES THIS ROW'S OWN EXAMPLE: `owned_by` is FOUR edits from `owner` and unreachable by distance; `owned` is one edit from `owner`. ⭐ AND IT GREW A VALUE-SHAPED HALF THE SAME NIGHT THE ID FORMAT MOVED: `id_problems()` accepts BOTH `AUT-PD-030` and the new discriminated `AUT-PD-204-6b009680`, reading the shape from `ids.parse_entry_id` rather than a second regex (pinned by a test that monkeypatches that function and watches the verdict follow), and points the same detectors at the id PREFIX because a prefix is a namespace. ⚠ WHAT IT CANNOT CATCH IS STATED IN THE MODULE: an ABSENT field (the largest residual, and `unclassified_outward`'s regex is the only instrument for it), a typo that is itself a real field, and a typo of an unread annotation.

**2 — NEW, `process_defect`, `state: queued`, `cost_class: free`, `requires_trimcrae: false`.**
> ⛔ EIGHT COMMITTED LEDGER ROWS RECORD A FACT UNDER A SPELLING THEIR READER CANNOT SEE, AND IT WAS FOUND BY THE SCHEMA RATHER THAN BY ANYBODY READING THEM. `_closed_by` on AUT-068, AUT-PD-129 and AUT-PD-146 carries a cycle id; `claim.py:429` reads `closed_by` and nothing else, so all three report NO CLOSER while the id sits in the row. `_outcome` on AUT-PD-099, AUT-PD-166 and AUT-PROP-051/053/054 records the result; `stuck_clock.PROGRESS_FIELDS` and `out_of_ideas.py` list `outcome` only, so an edit to `_outcome` IS NOT PROGRESS in the instrument that measures progress. ⭐ THE FIX IS A RENAME OF EIGHT ROWS, then deleting `ledger_schema.LIVE_ALIASES`, at which point the detectors refuse those spellings for good — `test_no_committed_field_name_is_a_near_miss_of_a_governed_one` already asserts the set can only shrink. ⭐ A THIRD PAIR IS HALF-MITIGATED AND BELONGS IN THE SAME SWEEP: `stuck_clock.py:184-185` reads BOTH `lease_released` and `_lease_released`, but `queue_view.DELIVERABLE_FIELDS` is `("what", "lease_released")` and knows only the bare one, so a row recording its deliverable in `_lease_released` alone is invisible to `already_landed()` — and AUT-PROP-012 carries both spellings at once with different text in each. ⚠ NOT DONE IN THE SAME CHANGE because no seat may touch `research-ledger.json` while AUT-PD-171's id allocator collides across concurrent writers.

**3 — AUT-PD-181, `state`: `in_progress` (NOT done), or a new row if it is closed to the instance.**
> ⭐ THE GUARD EXISTS AND THE SWEEP IS CLEAN; THE DERIVATION IS NOT DONE. `scripts/tests/test_a_generated_prose_summary_cannot_contradict_its_own_table.py` reduces each route block's prose to clauses and checks 5 readability and 16 direction assertions against the `genes` table the same function emits — 0 contradictions across all 16 blocks, and the row's two named questions are answered from the data: RT-NR2F1's *"NOT READABLE on either platform"* is TRUE (`readable=False` on both), and no second contradiction exists. It is mutation-tested by restoring the original twenty-day sentence, by flipping a direction, and by claiming the genuinely unreadable gene readable. ⛔ IT IS THE SECOND-BEST FIX AND SAYS SO: the honest fix is to DERIVE the readability sentence inside `research/modalities/census_route_expression_grading.py`, which a sprint seat did not own, and the guard should be DELETED rather than extended the day that lands. ⚠ COVERAGE IS 7 OF 16 BLOCKS AT ZERO ASSERTIONS — their prose speaks about modules and groups, not about a gene on a platform, and is not reducible to a table cell. One clause is reported as unreducible rather than silently skipped.

**4 — NEW, `process_defect`, `state: queued`, `cost_class: free`, `requires_trimcrae: false`.**
> ⚠ `contract_check.py` COVERS ONE ENFORCER AND THERE ARE NOW TWO. Its own docstring says it covers *"the enforcer that FAILS THE COMMIT (`receipt_schema.py`) and no other reader"*, and `ledger_schema.py` is now a second module whose refusal fails a commit. The receipt case needed it because `research-loop` §2 step 10 is the prose a cycle follows when it hand-authors a receipt, and that text could omit a field the schema requires. ⛔ WHETHER THE LEDGER HAS AN EQUIVALENT CONTRACT TEXT IS UNKNOWN AND WAS NOT CHECKED — file this to ANSWER that question, not on the assumption that it does. If it does not, the correct outcome is a one-line note in `contract_check.py` saying why the ledger is out of its scope, which is cheaper than the doubt.

---

## Amendment record for the driver

`**/tests/**` is governed and this seat did not append to `amendments.jsonl`. Ready to paste:

```json
{"utc": "2026-09-01T19:05:00Z", "actor": "sprint-2026-09-01/S10-SCHEMA", "kind": "add", "paths": ["research/autonomy/tests/test_a_near_miss_field_name_cannot_enter_the_ledger.py", "scripts/tests/test_a_generated_prose_summary_cannot_contradict_its_own_table.py"], "items": ["AUT-PD-030", "AUT-PD-181"], "why": "Two new guards, no existing test weakened, loosened or deleted. (1) AUT-PD-030: the ledger had no field-name schema, so a one-edit misspelling of `requires_trimcrae` was offered as ready work by continuity.ready() with no warning anywhere — reproduced on a scratch copy before the fix. The new test binds research/autonomy/ledger_schema.py to the committed ledger and to ledger_io.write_ledger. (2) AUT-PD-181: a generator's hand-typed prose could contradict the machine table beside it (RT-ALK-HIT, false for 20 days, corrected in 35fb816f5) and nothing measured the agreement; the new test asserts 21 prose claims against the table the same function emits. Both are mutation-tested — the ledger guard through seven in-memory mutations, the prose guard by restoring the original false sentence and by two synthetic inversions — on deep copies and scratch trees, never on the live tree.", "mutation_tested": true, "coverage_floors_asserted": true}
```
