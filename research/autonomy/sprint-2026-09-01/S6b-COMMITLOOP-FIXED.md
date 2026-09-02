---
id: DOC-SPRINT-S6B-COMMITLOOP-FIXED
title: "S6b-COMMITLOOP-FIXED — the commit loop, from ~9 minutes to 131 seconds"
level: L3
kind: memo
status: live
date: 2026-09-02
last_verified: 2026-09-02
purpose: "Take S6-COMMITLOOP's named hot spot and the one beside it, measure the result, and record what the commit loop now costs (AUT-PD-164 / AUT-PD-172 / AUT-PD-183 follow-on)."
scope: "Wall-clock cost of `./scripts/preflight.sh` at its DEFAULT tier, measured in this dev sandbox (4 cores) on 2026-09-02. NOT a re-measurement of the PREFLIGHT_TESTS or PREFLIGHT_MODALITIES tiers, and NOT a decision about re-tiering gate 13, which CLAUDE.md §6 reserves for trimcrae."
audience: [autonomous research agents, maintainers]
---

# S6b-COMMITLOOP-FIXED — the commit loop, from ~9 minutes to 131 seconds

**Item(s):** the fixes S6-COMMITLOOP named and did not take
**Owned paths:** `research/autonomy/stuck_clock.py`, `research/manuscripts/lint_citations.py`,
`research/manuscripts/lint_citation_types.py`, their two new guard files, `CLAUDE.md` (§6 cost
figures only), `.claude/skills/repo-gates/SKILL.md` (the same figures), `scripts/preflight.sh`
(comments only), `research/manuscripts/pinned-figures.json` (this figure only), this file

## Verdict

**FIXED, measured end to end.** One timestamped default `./scripts/preflight.sh` on this box:
**130.7 s total, of which gate 13 is 57.1 s over 1 030 tests.** Against S6's reading of the same
tier — fast gates 81.3 s + gate 13 446.3 s, ~9 minutes — that is **about a 4x cut on the loop and
about 8x on gate 13, on a suite that has since GROWN from 789 tests to 1 030.**

⛔ **Not one assertion changed, and that is the whole character of this work.** Every fix here is a
duplicate computation deleted or a process spawn batched. Both linters print byte-identical output;
the ledger walk returns a list identical to the one it replaced, compared element by element.

## The three fixes

### 1 · `stuck_clock.ledger_versions()` — memoised per HEAD

S6 counted it with a shim in front of `git` on PATH: **48 230 of gate 13's 50 270 git calls — 96 % —
were `git show <sha>:research-ledger.json`**, i.e. ~130 complete walks of the ledger's history per
gate run, ~7.5 s each, ~55 % of a 446 s gate, *growing with the repository's commit count rather
than with anything a test measures.*

Memoised on `(repo, path, HEAD)` in `8f0ad7e06`. Re-counted with the same shim on 2026-09-02:

| | before | after |
|---|---|---|
| git calls in one gate-13 run | 50 270 | **3 783** |
| of those, `show <sha>:research-ledger.json` | 48 230 | **1 140** |
| gate 13 wall clock | 446.3 s / 789 tests | **54.0 s / 1 022 tests** |

⭐ **HEAD is in the key, not just (repo, path).** History is append-only, so two reads at the same
HEAD must agree — but a process that commits between them is the ordinary case in this repository,
not an exotic one. Keying on HEAD makes the cache a memo of a pure function instead of a bet that
nothing moved.

### 1b · …and the memo's price, which was 16x the fair one

⛔ **A MEMO OF A GROWING HISTORY IS ITSELF A THING THAT GROWS WITH COMMIT COUNT** — the same
accretion, moved from CPU to memory, and it was not noticed when the memo landed. The walk returns
380 versions holding **84 792 row objects, of which only 2 319 are distinct states** (36.6x), because
the ordinary commit changes one ledger row and re-serialises the other 144.

A row that did not change is now the *same object* as in the version before it. Two fresh processes,
resident bytes from `/proc/self/statm` after `gc.collect()`:

| | walk | holding the memo | after dropping it | **retained by the memo** |
|---|---|---|---|---|
| un-interned | 7.33 s | 466 MB | 340 MB | **126 MB** |
| interned | 2.79 s | 245 MB | 237 MB | **8 MB** |

⚠ **THE RETAINED COLUMN IS THE ONE A CASUAL MEASUREMENT MISSES, AND THE FIRST DRAFT OF THIS SECTION
GOT IT WRONG.** `ru_maxrss` is a peak dominated by transient parse arenas, and CPython does not
return freed pages, so an in-process before/after delta read **652 MB** — which is transient plus
retained, not what the cache holds. The number that matters is the one that persists, four times
over under `pytest -n 4`, and grows with every commit this loop makes. Corrected before it reached
a comment anyone would later quote.

### 2 · `ledger_versions()` — one `git cat-file --batch` instead of 372 `git show`

The memo cut 130 walks to ~3; a walk was still **one process per commit**. `git cat-file --batch`
takes every rev on stdin and answers on one stream.

**6.71 s → 2.76 s over 380 versions, output compared element by element and IDENTICAL.**

⛔ It fails to `{}` — never to a guess — and the caller falls back to the per-commit `git show`. The
dangerous failure here is not slowness but a **shorter** history: fewer versions move the horizon
forward and make stuck rows look younger than they are, which is the stall detector talked out of
its own finding.

### 3 · Gate 6 walked the whole prose corpus TWICE

The largest fast gate was citation provenance at 44.4 s (55 % of the fast tier). cProfile over one
run, 2026-09-02: **101.6 s, of which `_scan` was 95.4 s in two disjoint halves of 47.6 s each.**
`lint_citations.check()` computed `survey()`; it then called `lint_citation_types.check()`, whose
`retraction_sweep()` computed the identical `survey()` again over the identical tree.

The prose half is now handed over — `_types.check(prose=prose)` — and `prose=None` still means
"compute it yourself" for every standalone caller. Second, `_redact_failed_fetches` ran **13 004 074
times** rebuilding every dict and list it walked; it now returns the input node when nothing needed
redacting.

**72.4 s → 37.7 s on this box, byte-identical output** (diffed, not eyeballed).

## What guards each fix

⛔ **NONE OF THIS IS VISIBLE TO ANY EXISTING TEST, WHICH IS EXACTLY THE `subagent_width` SHAPE** —
a rule measured by nothing. `_types.check()` and `_types.check(prose=prose)` differ by one keyword;
both are green, both print the same numbers, and the only symptom of the slow one is minutes of wall
clock. So each property is now asserted:

* `research/manuscripts/tests/test_the_citation_scan_is_not_run_twice.py` — 14 tests. Counts
  `survey()` calls through one gate run (seeding `sys.modules` so the type guard's own
  `import lint_citations as LC` resolves to the instrumented module — without that the counter reads
  1 whether or not the duplicate happened); pins the redaction against a deliberately dumb
  always-rebuild reference, on fixtures and on 120 of the repository's real `.json` artifacts.
* `research/autonomy/tests/test_the_ledger_history_is_read_in_one_git_process.py` — 8 tests. Equality
  against the per-commit walk it replaced (including an unparseable version, which must still be
  SKIPPED rather than read as an empty ledger); no `git show` per commit; the batch reader's
  protocol; the memo's HEAD key.

**Mutation-tested, 15 mutations, 15 caught**, each asserted to have LANDED before its result was
read, each run against a byte-identical restore afterwards (sha256 compared). Three of them attack
the interning specifically, and the one that matters most is *"share the object even when the row
CHANGED"*: that would make `compute_clocks` see no change at all — every clock frozen, every stall
invisible, the module reporting the deadest rows as the liveliest, which is precisely the failure it
exists to catch. Five tests go red on it.

⚠ **TWO MUTATIONS SURVIVED THE FIRST PASS AND BOTH WERE THE TEST'S FAULT, NOT THE GUARD'S.**
Recorded because the second one is the more instructive failure in this repository's usual style:

* *"a missing rev consumes a body"* survived because the reader re-synchronises by searching for the
  next newline, so `pos += 1` corrupts only the oid string, which nothing reads. The mutation was
  not a regression. The real one — consume a whole line — is caught.
* *"frame the body by characters instead of bytes"* survived because the fixture wrote its
  non-ASCII text through `json.dumps` with the default `ensure_ascii=True`, which escapes it to
  `\uXXXX`. **The blob was pure ASCII, so byte count and character count were equal and the test
  could not tell the two framings apart.** A fixture that contains none of the thing it is testing
  is a green test measuring nothing — the defect this repository keeps paying for, here inside a
  test written to prevent it. With `ensure_ascii=False`, three tests catch it.

## What did NOT change, and what is still open

* **The tiering.** Gate 13 still runs unconditionally in the default loop; `systems/tests`,
  the manuscripts suite and the modalities suite still sit behind their flags. CLAUDE.md §6
  reserves any move for trimcrae and this changes none of it — it makes the existing tier cheap.
* **`test_affected_tests.py::test_the_committed_record_matches_the_committed_gatekeepers` is still
  red**, as it was before this work: `scripts/selector-validation.json` records hashes of
  `preflight.sh` and `affected_tests.py` that only a `PREFLIGHT_FULL=1` run re-stamps. Pre-existing,
  unrelated to these fixes, and named here so a reader of the 130.7 s run does not attribute it.
* **The fast tier's next-largest item is now the `dev-setup.sh --if-needed` start-up**, whose cost is
  dominated by `_deepen_ledger_history`'s `git fetch --shallow-since`. That is a network call that
  buys the clocks their horizon; it is not obviously removable and was not touched.
