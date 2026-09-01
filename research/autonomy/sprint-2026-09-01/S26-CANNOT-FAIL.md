---
id: DOC-SPRINT-S26-CANNOT-FAIL
title: "S26-CANNOT-FAIL — the test that could not fail, and a sweep of the five suites for its class"
level: L3
kind: memo
status: live
date: 2026-09-01
last_verified: 2026-09-01
purpose: "Reproduce and repair scripts/tests/test_affected_tests.py::test_the_committed_record_matches_the_committed_gatekeepers, then sweep 607 test files across the five suites for every mechanism by which a test cannot fail, and build a meta-guard scoped to the mechanisms actually found."
scope: "The five pytest suites (scripts/tests, systems/tests, research/manuscripts/tests, research/modalities/tests, research/autonomy/tests), swept statically by AST on 2026-09-01. NOT a claim that any test in this repository can fail — 'can this test fail?' is undecidable and nothing here approximates it."
audience: [autonomous research agents, maintainers]
---

# S26-CANNOT-FAIL — a test that could not fail, and the sweep for its class

**Item(s):** S6-COMMITLOOP ledger row 3 (new), row 5 (new)
**Owned paths:** `scripts/tests/test_affected_tests.py`,
`research/manuscripts/tests/test_a_guard_that_cannot_fail_is_not_a_guard.py` (new),
`.claude/skills/repo-gates/SKILL.md` (the commit-loop cost figure only), this file
**Started (UTC):** 2026-09-01T20:0xZ   **Finished (UTC):** 2026-09-01T20:5xZ

## Verdict

**FIXED, and the fix is RED ON PURPOSE.** S6's finding reproduces exactly. The repaired test now
binds the committed record and **fails**, naming `scripts/preflight.sh` — which is the correct
outcome and the whole point: **gate 13 is red until somebody re-stamps
`scripts/selector-validation.json`, and that is a state the repository has been in for eighteen
commits without an instrument that could say so.** The sweep for the class found **one live
instance — the one already known — and no second one.** Three candidate mechanisms were checked and
**refuted as classes** (16/16 `except` swallowers are the deliberate raises idiom; 10/10
"no-assertion" tests are the `# must not raise` idiom; 7/7 loop-vacuity candidates were non-empty
when counted). A new meta-guard enforces the two mechanisms that do exist, carries a guard on
itself, and states in its own docstring the five things it cannot see.
⛔ **Separately and not mine: `research/manuscripts/tests/test_no_guard_can_silently_not_run.py` is
RED on the trunk right now, and the sprint put it there** — see §5.

## What I measured

### 1 · S6's finding, reproduced — two commands, one contradiction

```
$ python3 -c "import sys; sys.path.insert(0,'scripts'); import affected_tests as A;
              print(A.VALIDATION_RECORD); print(A._unvalidated_gatekeepers())"
/home/user/Rare-cancers/scripts/selector-validation.json
{'scripts/preflight.sh'}

$ python3 -c "<import the test module, call the function with no fixture>"
RESULT: AssertionError -> ['scripts/preflight.sh'] do not match scripts/selector-validation.json…

$ python3 -m pytest scripts/tests/test_affected_tests.py -q
17 passed in 49.27s
```

The function raises when called. The suite that contains it reports 17 passed. **The mechanism is
the `@pytest.fixture(autouse=True) _validated` at the top of the file**, which rewrites
`A.VALIDATION_RECORD` to a temp record built from the hashes ON DISK — so the one test whose subject
is the COMMITTED record is handed a record that matches by construction. The fixture's own docstring
said *"The two tests that are about the record patch it themselves"*: true of the two that patch it,
**false of the third, which did not**.

### 2 · The repair, and the mutation test that proves it discriminates

`COMMITTED_RECORD = A.VALIDATION_RECORD` is now captured at **module import**, before any fixture can
run, and the test re-points the module at it and asserts that the path it read is the committed one —
so a future fixture cannot silence this test without that assertion naming it.

⛔ **Mutation-tested in a scratch copy of `scripts/` (`tempfile` + `cp`), never in the live tree**
(charter §7). A whole scratch `scripts/` tree was built, its record re-stamped so the hashes matched,
and the test run there:

| scratch state | result |
|---|---|
| record re-stamped to match the scratch tree | **1 passed** |
| one gatekeeper edited after the stamp (`>> preflight.sh`) | **1 failed** |
| record made unreadable (`not json`) | **1 failed** |

It passes when the record is current, fails when a gatekeeper drifts, fails when the record is
unreadable. Before the repair it did none of those things. In the live tree:

```
$ python3 -m pytest scripts/tests/test_affected_tests.py -q
FAILED …::test_the_committed_record_matches_the_committed_gatekeepers
1 failed, 16 passed in 50.32s
```

⛔⛔ **THIS IS THE FINDING, NOT A REGRESSION.** `scripts/preflight.sh` has not matched its recorded
hash since 2026-08-26, CLAUDE.md §6 calls that a *"permanent tripwire"*, and the guard written to
shout about it was silent for eighteen commits. **Gate 13 is now red and will stay red until
`PREFLIGHT_FULL=1 ./scripts/preflight.sh` goes green on a settled tree and
`python3 scripts/record_selector_validation.py` is run and committed with it.** That is the driver's
call and it needs a quiet tree, which is exactly what S6 said it was waiting on. **Do not silence
it.**

### 3 · The sweep — 607 files, five mechanisms, and what each one actually found

Static AST sweep over `scripts/tests`, `systems/tests`, `research/manuscripts/tests`,
`research/modalities/tests`, `research/autonomy/tests` — `test_*.py` and `conftest.py`, **607
files**. Every candidate below was then READ, because a detector's hit list is a hypothesis.

| mechanism | candidates | after reading | live instances |
|---|---|---|---|
| **M1** autouse fixture rewrites a module attribute a test then reads | **5** | 4 correct, 1 defect | **1** (the one above) |
| **M2** a test with no failure path at all | 28 → **10** after resolving local helpers | **0** — all 10 are the deliberate `# must not raise` idiom, and an unhandled exception fails a test | **0** |
| **M3** every failure point inside a loop that could be empty | **327**, of which **7** loop over a filtered comprehension / `glob` / `listdir` | **0** vacuous today, counted | **0** |
| **M4** a `try/except` that swallows the assertion | **16** | **0** — 12 are `try: f(); assert False; except ValueError: pass`, 4 are `except Exception: continue` on `yaml.safe_load` with a named sibling test that owns unparseable YAML | **0** |
| **M5** `parametrize` over an empty literal | **0** | — | **0** |

⭐ **M2 and M4 are REFUTED AS CLASSES, and that is a result.** M2's detector was wrong, not the
tests: `importlib.reload(kd)`, `ppmx._split_topology_guard(str(tmp_path))  # must not raise` and
`wcc.what_you_are_buying(key)  # raises if unclassified` all fail loudly on an exception. M4's
`assert False` sits **before** the `except`, so the handler is only reached when the call raised as
demanded. The hand-off in the four `yaml` cases was checked rather than believed:
`test_workflows_parse.py:142::test_all_workflows_parse_and_declare_triggers` exists and owns it.

⭐ **M3 is the largest class and it is LATENT, NOT LIVE — counted, not assumed.** Each of the seven
filtered/globbed loops was measured against the tree it reads:

| site | its collection, counted today |
|---|---|
| `systems/tests/test_autonomy_priority.py::test_a_prerequisite_inherits_the_parents_value_not_its_penalty` | **15** ledger rows carry `prerequisite_of` |
| `research/modalities/tests/test_scope_rungs_and_steric_rule.py::test_free_tiers_are_free_and_need_no_nod` | **2** rungs match `R13-a`/`R14-a` |
| `research/modalities/tests/test_lanes_run_from_main.py::test_every_fleet_branch_input_defaults_to_main` | **5** workflows carry `fleet_branch \|\|` |
| `systems/tests/test_systems_check.py::test_a_preregistration_is_never_archived` | **10** files under `archive/` |
| `research/modalities/tests/test_gate_exit_codes_render_distinctly.py::…_not_by_accident` | the workflow directory, non-empty |
| `research/modalities/tests/test_no_push_notifications.py::test_nothing_still_calls_the_deleted_escalation` | as above |
| `research/modalities/tests/test_antihandle_constraint.py::test_the_artifact_makes_no_licensing_claim` | occurrences of banned phrases |

Three of the seven (`_never_archived`, `_nothing_still_calls_`, `_makes_no_licensing_claim`) are
**correct when empty by construction** — they assert *no occurrence of X exists*, and zero
occurrences is the state they want. The other four would pass vacuously if their collection emptied,
which is a real hazard and is **not** one that has fired. ⛔ **A guard over a class with no live
instance would be an allowlist of seven names and no measurement**, which is this seat's own defect
one level up, so it is written down here and deliberately not enforced.

### 4 · The meta-guard, and its mutation test

`research/manuscripts/tests/test_a_guard_that_cannot_fail_is_not_a_guard.py` — new, stdlib + pytest
only, **5.9 s**, three tests. It sits beside `test_no_guard_can_silently_not_run.py`, which asks
whether a guard RAN; this one asks whether a guard that ran could ever have said no. ⚠ It is in
`research/manuscripts/tests/`, so it runs under `PREFLIGHT_TESTS=1` and in CI — **it adds nothing to
the default commit loop.**

* **R1** — no test may read a module attribute its own module's `autouse` fixture rewrote.
  Offenders today: **4**, all `P.OUT` in the two pooling-check files, all read and all **correct**
  (the fixture redirects the producer's `OUT` at a tmp copy precisely so no test writes to the
  tracked tree, and those tests' subject IS the copy). Each is in `AUDITED_R1` **with its reason**,
  and a reason under 40 characters fails.
* **R2** — no `parametrize` over an empty literal. Zero today; a free ratchet.
* **Scope floor** — fewer than 500 files matched is a hard failure. ⭐ **It fired on its own first
  run**, catching a wrong `REPO` in my own file (`../..` where the layout needed `../../..`), which
  is the entire argument for having it.
* ⭐⭐ **`test_the_detector_still_fires_on_every_audited_site` — the guard on the guard.** Every
  `AUDITED_R1` key must still be *detected*. An allowlist whose entries the detector no longer finds
  is indistinguishable from a detector that finds nothing, and *"narrow the detector until the red
  goes away"* is the obvious way to defeat this file.

⛔ **Mutation-tested against a `cp -r` scratch copy of all five test directories (611 files, 9.5 MB),
`REPO` re-pointed at the copy. The live tree was never mutated.**

| mutation (scratch only) | R1 | guard-on-guard | R2 |
|---|---|---|---|
| 0 unmutated | PASS | PASS | PASS |
| 1 a new autouse rewrite + a test that reads it | **RED** | PASS | PASS |
| 2 `@parametrize("x", [])` | PASS | PASS | **RED** |
| 3 an audited site renamed away | **RED** | **RED** | PASS |
| 4 `_r1_offenders` narrowed to return `{}` | PASS | **RED** | PASS |
| 5 the scope matches no file | **RED** | **RED** | **RED** |
| 6 restored | PASS | PASS | PASS |

Mutation 4 is the one that matters: **weakening the detector into uselessness is caught.**

⛔ **WHAT IT CANNOT SEE, and this is written into the file's own docstring rather than only here,
because a meta-guard that overstates its coverage is the same defect one level up.** *"Can this test
fail?"* is undecidable; this detects two syntactic mechanisms. It does not see a fixture that rebinds
a dict key, a list element, an env var or a dotted path; a `conftest.py` rewrite reaching another
file (R1 is per-module **on purpose** — `research/modalities/tests/conftest.py` legitimately
neutralises `gpu_backend.vast_rental_hold` suite-wide, and the hold's own test defends itself by
binding the real function at import, **verified**: `_real_hold = gb.vast_rental_hold` at
`test_vast_account_rental_hold.py:35`); an assertion that is true but about the wrong object; a
parametrisation over a computed list that empties at run time; or the whole M3 loop class.

### 5 · ⛔ NOT MINE, AND LIVE: the existing meta-guard is RED on the trunk, and the sprint put it there

```
$ python3 -m pytest research/manuscripts/tests/test_no_guard_can_silently_not_run.py -q
FAILED …::test_every_remaining_skip_in_the_deposit_suite_is_a_decision_somebody_took
  research/manuscripts/tests/test_the_census_artifact_and_the_guard_corpus_are_a_pair.py:279
  research/manuscripts/tests/test_the_deposit_the_papers_cite_is_current.py:270
1 failed, 3 passed
```

Attributed rather than guessed: neither file differs from HEAD, both skips are **absent at
`origin/main`**, and `git log -S` names the commit — **`062a48ae1`, "sprint wave 1 lands"**. So wave
1 landed two unmarked `pytest.skip` calls and the repository's own silent-skip guard has been red
ever since.

⭐ **And the second one is this seat's exact class.**
`test_a_widened_guard_pattern_alone_turns_the_check_red` — a *mutation-style* guard, whose whole
value is going red on a widened pattern — skips itself when the manifest is unreadable at the
published revision. **A mutation harness that declines to run scores the same as one that finds
nothing**, which is the "mutation harness that scored 0/8" instance found earlier tonight, in a
different file, in a different disguise. Neither path is mine; both need either a `SKIP IS
DELIBERATE` marker with a reason or a `pytest.fail`.

## What I changed

**`scripts/tests/test_affected_tests.py`** — `COMMITTED_RECORD` captured at import; the record test
takes `monkeypatch`, re-points `A.VALIDATION_RECORD` at it, and asserts the path it read is the
committed one; a ⛔⛔ comment block records the incident with its measurement; the `_validated`
fixture's docstring, which stated the false half of the fact, is corrected and now says every test
about the record must re-point it itself. **No assertion was weakened and none was removed.** The
file went from 17 passed to **1 failed, 16 passed**, and the failure is the true state of the tree.

**`research/manuscripts/tests/test_a_guard_that_cannot_fail_is_not_a_guard.py`** — new, as above.

**`.claude/skills/repo-gates/SKILL.md`** — the commit-loop bullet only. `"every fast gate, and **no
test**. ~**30 s**"` is replaced by the measured tier: fast gates **81.3 s**, gate 13 **446.3 s**
quiet / **1 247.8 s** contended, **~9 minutes**, gate 13 **85–94 %** of the loop, with S6's
attribution (scope + population, not a per-test regression) and the `ledger_versions()` hot spot.
⭐ **The "no test" half was checked at the source rather than taken from prose**:
`scripts/preflight.sh:1218` runs `scripts/tests research/autonomy/tests $SYSTEMS_TESTS`
**unconditionally, outside the `RUN_TESTS` block**, so the default tier has run tests since
2026-08-27. Both retired claims are kept verbatim on `⚠ Superseded, retained (rule 1.2)` lines.
⚠ **The block's other figures (`31.4 s` fast gates, `176.1 s` manuscripts) are NOT touched**: they
are past-tense readings of a 2026-08-23 decision, correctly framed as such, and registering their
supersession would require `pinned-figures.json`, which this seat does not own.
`python3 research/manuscripts/lint_consistency.py` → **`0 ERROR across 26 target file(s)`**.

⛔ **ANTI-GAMING.** No gate checks less. One guard went from unable-to-fail to able-to-fail (and is
now failing); one new guard was added with four audited exemptions, each carrying a written reason
and each still required to be *detected*; one documentation figure moved in the direction that makes
this repository's commit loop look **more** expensive. Nothing was exempted, scoped down or
re-tiered. The self-serving edit was available and is named: deleting the record test, or marking it
`xfail`, would have made gate 13 green in one line.

## What I could not do, and what it is actually waiting on

1. **Re-stamping `scripts/selector-validation.json` to make the repaired test green.**
   `record_selector_validation.py` may only be run after a green `PREFLIGHT_FULL=1`, which cannot be
   obtained while twelve seats mutate the tree — and `scripts/preflight.sh` is not mine tonight
   anyway. ⚠ Waiting on: **a settled tree plus one FULL run.** Until then gate 13 is red **for the
   reason it was built to be red**, and the failure message names the two commands.
2. **The two unmarked skips in §5.** Both are in files this seat does not own. ⚠ Waiting on: the
   driver assigning them. One-line fix each (a marker with a reason, or `pytest.fail`).
3. **Enforcing the M3 loop class.** Not blocked — **declined, with the count**. Zero live instances,
   so a guard would be an allowlist and no measurement. Re-derivable in one command; the seven names
   and their live counts are in §3.
4. **A sweep of `conftest.py`-to-other-file rewrites.** R1 is deliberately per-module. Widening it
   would need the cross-file import graph, which `scripts/affected_tests.py::build_graph` already
   builds — a real follow-up, not a blocker, and named as a ledger row below.

## Amendment record for the driver

⛔ Not appended by this seat — `amendments.jsonl` is driver-only while a wave is in flight. One per
governed path.

```json
{
  "cycle_id": "<driver fills>",
  "utc": "<driver fills>",
  "path": "scripts/tests/test_affected_tests.py",
  "what_changed": "test_the_committed_record_matches_the_committed_gatekeepers now binds the COMMITTED record. COMMITTED_RECORD is captured at module import, before any fixture runs; the test takes monkeypatch, re-points A.VALIDATION_RECORD at it, and asserts the path it read is scripts/selector-validation.json. The _validated autouse fixture's docstring, which said 'the two tests that are about the record patch it themselves', is corrected to state that every test about the record must re-point it itself, and a comment block records the incident with its measurement.",
  "old_value": "The test read A.VALIDATION_RECORD as the autouse fixture had left it: a temp record built from the on-disk hashes, matching by construction. _unvalidated_gatekeepers() returned {'scripts/preflight.sh'} and the function raised when called directly, while pytest reported 17 passed.",
  "new_value": "1 failed, 16 passed. The failure names scripts/preflight.sh, which has been unvalidated since 2026-08-26 across eighteen commits.",
  "why": "S6-COMMITLOOP ledger row 3. CLAUDE.md §6 describes the stale record as a permanent tripwire; the guard written to shout about it could not fail.",
  "self_serving_check": "ANSWERED: NO, and the self-serving option was the cheap one. Deleting the test or marking it xfail turns gate 13 green in one line; this change makes it red instead and reports that as the finding. No assertion was weakened or removed. Mutation-tested in a scratch copy of scripts/: passes when the record matches, fails when a gatekeeper drifts, fails when the record is unreadable — none of which it did before.",
  "mutation_tested": true
}
```

```json
{
  "cycle_id": "<driver fills>",
  "utc": "<driver fills>",
  "path": "research/manuscripts/tests/test_a_guard_that_cannot_fail_is_not_a_guard.py",
  "what_changed": "New meta-guard over 607 test files in the five suites. R1: no test may read a module attribute its own module's autouse fixture rewrote (4 audited exemptions, each with a written reason, each still required to be DETECTED). R2: no parametrize over an empty literal. Plus a >=500-file scope floor and a guard-on-the-guard that reddens if the detector stops finding the audited sites.",
  "old_value": "No guard existed for this class. The mechanism had produced one instance that went eighteen commits unnoticed.",
  "new_value": "3 tests, 5.9 s, in research/manuscripts/tests (PREFLIGHT_TESTS + CI; nothing added to the default commit loop). The file's docstring names the five things it cannot see, including the whole loop-vacuity class.",
  "why": "S6-COMMITLOOP ledger row 3 asked for the instance to be fixed; the seat prompt asked for the class. Four instances of one shape were found in a single night.",
  "self_serving_check": "ANSWERED: NO. It adds refusals and removes none. The four exemptions are the only sites the detector finds today, all four were read before being recorded, all four carry a reason a reader can check, and none of them can be a silencer because a separate test demands the detector still flag them. Coverage is deliberately understated rather than overstated: the largest class found (327 loop-conditional tests, 7 that could empty) is measured and explicitly NOT enforced, because zero of the seven is vacuous today.",
  "mutation_tested": true,
  "_mutation_evidence": "cp -r of all five test dirs (611 files) to a scratch root with REPO re-pointed; the live tree was never mutated. 5 mutations, 5 caught by the right test: a new autouse-rewrite-plus-read (R1 red); an empty literal parametrize (R2 red); an audited site renamed away (both red); _r1_offenders narrowed to return {} (guard-on-guard red); an empty scope (all three red). Unmutated and restored: all pass."
}
```

```json
{
  "cycle_id": "<driver fills>",
  "utc": "<driver fills>",
  "path": ".claude/skills/repo-gates/SKILL.md",
  "what_changed": "The default-tier bullet's cost figure only. 'every fast gate, and no test. ~30 s' replaced by the 2026-09-01 measurement: fast gates 81.3 s, gate 13 446.3 s quiet / 1247.8 s contended, ~9 minutes, gate 13 85-94 % of the loop, with the scope-and-population attribution and the ledger_versions() hot spot. The 'no test' half is corrected against scripts/preflight.sh:1218, which runs the pure-logic suites unconditionally.",
  "old_value": "'**`./scripts/preflight.sh`** -- every fast gate, and **no test**. ~**30 s**. **This is the commit loop.**'",
  "new_value": "The measured tier, with both retired claims kept verbatim on '⚠ Superseded, retained (rule 1.2)' lines.",
  "why": "S6-COMMITLOOP ledger row 5, left for this seat. The skill loads before every commit and told its reader ~30 s against a measured ~9 minutes -- an 18x understatement of the thing a session uses to decide whether it can afford the gate.",
  "self_serving_check": "ANSWERED: NO. Every number moved in the direction that makes this repository's commit loop look more expensive, which is the opposite of a self-serving edit. Not one line of gate selection, scope, ordering or tiering was touched; re-tiering gate 13 remains trimcrae's call and is not taken. The 31.4 s / 176.1 s figures elsewhere in the block were deliberately left alone because registering their supersession needs pinned-figures.json, which this seat does not own.",
  "mutation_tested": false,
  "_verification": "python3 research/manuscripts/lint_consistency.py -> 0 ERROR across 26 target file(s)."
}
```

## Ledger rows the driver should write

**1 · Close S6-COMMITLOOP row 3 as FIXED-AND-RED.** The guard binds the committed record, is
mutation-tested, and fails. ⛔ **The row that replaces it is not a bug row — it is the re-stamp.**

**2 · NEW — re-stamp `scripts/selector-validation.json`; gate 13 is red until it happens.**
`kind: process_defect`, `state: queued`, `cost_class: free` (25 min of CPU),
`requires_trimcrae: false`, serves `RT-AUTONOMY`.
*what:* `scripts/preflight.sh` has not matched its recorded hash since 2026-08-26 (eighteen commits,
and this sprint has added more). The guard that reports it could not fail and now can, so gate 13
fails on every commit until `PREFLIGHT_FULL=1 ./scripts/preflight.sh` goes green on a **settled**
tree and `python3 scripts/record_selector_validation.py` is committed with it. ⛔ Do not silence the
test; the red is the correct reading. ⚠ Every seat that edits `preflight.sh` invalidates it again,
so the re-stamp must be the **last** thing the sprint does.
*Paths:* `scripts/selector-validation.json`, `scripts/record_selector_validation.py`.

**3 · NEW — the sprint landed two unmarked skips and the silent-skip guard has been red since.**
`kind: process_defect`, `state: queued`, `cost_class: free`, `requires_trimcrae: false`.
*what:* `test_no_guard_can_silently_not_run::test_every_remaining_skip_in_the_deposit_suite_is_a_decision_somebody_took`
fails on `test_the_census_artifact_and_the_guard_corpus_are_a_pair.py:279` and
`test_the_deposit_the_papers_cite_is_current.py:270`. Both skips are absent at `origin/main`;
`git log -S` puts both in **`062a48ae1` ("sprint wave 1 lands")**. ⭐ The second is a *mutation-style*
guard that skips itself when the manifest is unreadable — a mutation harness that declines to run
scores exactly what one that finds nothing scores. Each needs a `SKIP IS DELIBERATE` marker with a
reason, or a `pytest.fail`.

**4 · NEW — widen the cannot-fail detector to cross-file `conftest.py` rewrites.**
`kind: process_defect`, `state: queued`, `cost_class: free`, `requires_trimcrae: false`.
*what:* R1 is per-module by design, so a `conftest.py` fixture that rewrites a module attribute read
by a test in a **different** file is invisible to it. That shape exists and is currently correct
(`research/modalities/tests/conftest.py` neutralises `gpu_backend.vast_rental_hold`; the hold's own
test defends itself with `_real_hold = gb.vast_rental_hold` at import — verified), but nothing checks
that the next one will. The import graph needed already exists in
`scripts/affected_tests.py::build_graph`.
*Path:* `research/manuscripts/tests/test_a_guard_that_cannot_fail_is_not_a_guard.py`.

**5 · NEW (low) — four loop-vacuity sites that would pass if their collection emptied.**
`kind: process_defect`, `state: parked`, `cost_class: free`.
*what:* Of 327 tests whose every failure point is inside a loop, seven iterate a filtered
comprehension, a `glob` or a `listdir`; **all seven were non-empty when counted**, and three are
additionally correct-when-empty by construction. The remaining four
(`test_a_prerequisite_inherits_the_parents_value_not_its_penalty`,
`test_free_tiers_are_free_and_need_no_nod`, `test_every_fleet_branch_input_defaults_to_main`,
`test_the_advisory_snapshot_is_excluded_for_the_stated_reason_not_by_accident`) would each be fixed
by one line — an assertion that the collection is non-empty. **Parked rather than queued: no
instance has fired, and a guard over an empty class is this seat's own defect one level up.**
