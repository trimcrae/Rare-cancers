# I1 — collection and adjudication against `CONTRACT-I1-consistency-rule-semantics.md`

Collected 2026-09-08 09:34–09:40 UTC. **Result: erroneous identifier matching ESTABLISHED; the
smallest general semantic correction is implemented, independently re-verified by the parent, and
integrated.**

## Child identity — from the transcript

| item | measured |
|---|---|
| child | `a4d3dbe19da70eef9` |
| original JSONL | `I1-executed-artifacts/ORIGINAL-CHILD-TRANSCRIPT-a4d3dbe19da70eef9.jsonl`, **284,793 B**, `cmp`-identical at copy |
| model strings | **55 × `claude-opus-5`, 0 others** — requested medium, saved first-party subscription |
| tool pairs | **33** (self-reported 23 — a **fourth** consecutive undercount; the transcript is authoritative) |
| span | 09:27:44.484Z → 09:34:12.453Z (~6 m 28 s) |

Bounds ~40 calls / ~40 min: met.

## Isolation — verified by the parent, not assumed

`git status --porcelain` was empty before integration, and all three inputs were **md5-identical
across HEAD, the working tree and the child's `orig/` copies**:
`lint_consistency.py a583a33e…`, `pinned-figures.json 771670ed…`,
`test_lint_consistency.py 318d726e…`. **The child edited nothing in the shared tree**, so no
manuscript worker's linter baseline moved. No git write, no network, no publisher lookup.

## The question, answered on evidence

**ESTABLISHED — the rule did treat digits inside an identifier as a stated measurement.** Three
independent strands, each of which I checked:

1. **The code.** `check_superseded` used a plain unanchored `re.search`; there is no boundary, token
   or context logic anywhere in the S path. `is_cleared` only asks whether a *found* match is
   disclaimed, never whether the match is a value at all.
2. **The flagged line.** At `emc-mtap-prmt5-hypothesis.md:673` the only occurrence of `2.102` sits at
   offset 17 of `10.1016/j.jbc.2022.102434` — inside `2022.102434`. The line is a bibliographic
   reference and states no card ratio.
3. **The registry names this exact failure class already.** `pinned-figures.json:1332`, which I read
   verbatim: *"⚠ The regex binds the number to its SURROUNDING PROSE, not to bare digits. A loose
   `10\.3` matched inside a DOI on the reference line and produced a false positive on first run — and
   a guard that cries wolf is a guard someone switches off."* That precedent was fixed **one pattern
   at a time by hand**; the recognition rule was never fixed. The `_README` states the intent
   directly: *"a bare number is not a pattern."*

So the gate was reporting a paper as asserting a retired measurement it does not assert. **My earlier
withdrawn "false positive" wording is now replaced by an established finding — not reinstated as an
assumption.**

## The correction

`_begins_mid_number` plus `search` → `finditer`: *a superseded value is asserted only where its number
begins*. A digit-initial match is ignored when preceded by a digit, or by a dot that itself follows a
digit. The `finditer` change matters — the scan continues **past** a fragment instead of stopping at
it, so a genuine restatement later on the same line as an identifier is still caught.

**General, with no prohibited shortcut.** No paper-specific or DOI-specific exclusion, no allowlist, no
rule id named in the logic, no threshold relaxed, no assertion deleted, no rebaselining, no fake
supersession label, no registry edit, no manuscript edit, no other gate suppressed. The child
explicitly **declined** to fix this by editing the `2\.102` pattern in the registry, on the ground that
the 2026-08 `_context_note` shows hand-patching does not generalise. That was the right call.

## Parent re-verification — I ran these myself

- **Real-tree before/after:** `orig` exit **1**, `work` exit **0**.
- **Set difference of findings, computed by me:** exactly **one removed**
  (`S-card_ratio_4090_over_3090_2_10`, `emc-mtap-prmt5-hypothesis.md:673`) and **zero added**.
  Retained as `PARENT-RERUN-{orig,work}-findings.json`.
- **My own predicate table, 8 cases, all as required:** DOI interior **suppressed**; the real card
  ratio `"A 4090 does 2.102 times the work of a 3090"` **still fires**; `2.10x`, table cell, bold and
  the registry's truncating idiom `0\.00435\d` on `0.0043593` **all still fire**; a prefix-of-longer
  match still fires; and **a DOI and a genuine value on the same line still fires**.
- **After integration into the shared tree:** `lint_consistency` **exit 0**, "0 ERROR across 29 target
  files", and `lint_style`, `lint_claims`, `lint_submission_residue`, `lint_asymmetry`,
  `submission_metrics` all **exit 0** — no other gate moved.

## Boundary tradeoffs, as adjudicated

**Left-edge only, deliberately.** A right-edge rule would break the registry's own truncating idiom
(`0\.00435\d` is written to match the leading digits of a longer figure), so a match that is a
**prefix** of a longer number still fires; what is suppressed is a **suffix or interior** match, which
is the shape every identifier collision takes. The asymmetry is the price of not weakening detection.

**Now missed:** a genuine value written immediately after a digit with no separator
(`Table 32.102x`). Judged unwritable in practice, and the opposite error — silently suppressing a real
retired value — is the failure this repository treats as worse.

**Version strings:** `v1.2.102` is suppressed (dot after digit); `v2.102` still fires (letter is not
numeric continuation). **Page ranges:** `-`, `–` and `/` were deliberately excluded from the
continuation set, so `pp. 100–2.102` still fires — a hyphen commonly separates the endpoints of a real
range. Non-digit-initial patterns (`\$128`, prose patterns) are never examined by the predicate.

## ⚠ Honest limitation on the test

**The delivered pytest file has NOT been executed by pytest.** `python3 -m pytest` reports
`No module named pytest` in this container and no network is permitted to install it. The child
verified its 24 cases through a **stdlib shim** it wrote (`shim/`), which reproduced the bug against
`orig` (12 passed / 12 failed, exit 1) and passed fully against `work` (24 passed, exit 0). A shim run
is **not** a pytest run. The test file is integrated to `research/modalities/tests/` — matching the
existing `test_lint_consistency.py`, which also imports pytest — so it will execute wherever pytest is
available, but **its status here is: written, shim-verified, not pytest-executed.** The parent's own
8-case predicate check above is independent of the shim.

## Integrated paths

- `research/manuscripts/lint_consistency.py` — the corrected implementation.
- `research/modalities/tests/test_lint_consistency_identifier_boundary.py` — the new regression tests.

Both integrated only after I1 and H1 had finished and the result was adjudicated. Nothing else was
staged; no `git add -A`, no shared stash or checkout.

## Standing — unchanged by a green gate

**A green gate is not a publication decision.** The MTAP/PRMT5 **publisher-level confirmation**,
**cross-version identity/content**, and **Appendix A [2]/[3] attribution** blockers all remain open.
What this lane removes is one blocker of a different kind: a commit gate that was failing on a
misrecognition rather than on a defect in the paper.

## Retention — nothing deleted

`/tmp/claude-0/i1-lane/` **is intact**, including its `shim/` and originals. The in-repo copy is
`I1-executed-artifacts/` (35 files, 781,077 B) with its own self-exclusive manifest, holding the
child's `orig/`, `work/`, `evidence/`, `shim/`, the diff, every captured stdout/stderr/exit code, and
my two parent re-run JSONs. Cleanup of any directory awaits its own directory-specific receipt.

---

# Limitation RESOLVED, appended 2026-09-08 09:44 UTC — original text above preserved

**The "not pytest-executed" limitation recorded above no longer holds. The tests have now been run
under real pytest.** No network and no install was used: **pytest 9.1.1 and its dependencies were
already present in the local uv cache** (`/root/.cache/uv/archive-v0/…` for `pytest`, `pluggy`,
`iniconfig`, `packaging`, `pygments`). `python3 -m pytest` fails only because those paths are not on
the default `sys.path`; adding them via `PYTHONPATH` runs the real thing.

⚠ **The gap was mine, not the child's.** I recorded "no network to install pytest" without first
checking whether pytest was already on the machine. "Blocked" was a claim I had not established, and
the $0 reading disproved it.

| run | command (with the cache paths on `PYTHONPATH`) | exit | result |
|---|---|---|---|
| new tests, fixed impl | `python3 -m pytest research/modalities/tests/test_lint_consistency_identifier_boundary.py -q` | **0** | **24 passed** |
| existing suite, fixed impl | `python3 -m pytest research/modalities/tests/test_lint_consistency.py -q` | **0** | **27 passed** — no regression |
| new tests, ORIGINAL impl | same, `LINT_CONSISTENCY_DIR` pointed at the retained `orig/` | **1** | **23 failed, 1 passed** — the tests do catch the bug |

The existing suite is **fully green in the real tree** (27 passed), which also resolves the child's
"26 passed / 1 failed": that failure was the path artifact of its isolated lane, exactly as it
reported.

## ⚠ The shim was not equivalent to pytest, and the numbers differ

Against the original implementation the child's stdlib shim reported **12 passed / 12 failed**; real
pytest reports **23 failed / 1 passed**. The parametrised predicate cases cannot even be collected
against the original, because `_begins_mid_number` does not exist there — the shim absorbed that as
passes. **Both runs agree on the conclusion** (the tests fail against the original and pass against
the fix), and no integrated result rests on the shim, but the shim's counts should not be quoted as
pytest's. The shim is retained as evidence of what the child actually ran, not as a substitute.

Raw stdout/stderr for all three runs: `I1-executed-artifacts/parent-pytest/`.

---

# Two corrections to my own pytest reporting, appended 2026-09-08 10:04 UTC — originals preserved

**No test was re-run for having arrived late.** The native pytest execution pushed at `20f19e5f`
stands and covers the integrated linter and both modules against the real repository fixture: **24
passed** (new module) and **27 passed** (existing module), both exit 0. Those are unchanged and were
not repeated. What follows corrects **my own characterisation**, and one genuinely defective run.

## Correction 1 — my pre-fix run used an incomplete fixture, so it established nothing

I reported "23 failed, 1 passed … so the tests do catch the bug". **That run was invalid, and the
fault was mine:** I copied only `lint_consistency.py` into the comparison directory and **not
`pinned-figures.json`**. Reading the retained log, its 23 failures decompose as **15
`FileNotFoundError`** — the missing registry — and **8 `AttributeError`** for the absent
`_begins_mid_number`. **Not one of the 23 was a reproduction of the DOI bug.** The original log is
retained unaltered at `parent-pytest/new-vs-orig.out`.

Re-run with the registry present (`parent-pytest/new-vs-orig-COMPLETE-FIXTURE.out`, exit 1):

| outcome | count | what it means |
|---|---|---|
| **12 passed** | 12 | true-positive and clearing tests that fire correctly on the **original** too — as they should |
| `test_begins_mid_number_predicate` | **8** | `AttributeError`: the helper does not exist pre-fix. **A missing-helper artifact, NOT a bug reproduction** |
| `test_the_measured_case_a_doi_does_not_state_the_card_ratio`, `test_a_bare_identifier_alone_does_not_fire`, `test_a_longer_number_ending_in_the_pattern_is_not_that_number`, `test_a_version_string_is_not_a_measurement` | **4** | `AssertionError`: genuine behavioural differences — **these four are the independent reproductions** |

**So the accurate claim is: four tests independently reproduce the identifier bug**, eight fail only
because the new helper is absent, and twelve pass on both implementations. My "23 failures = the tests
catch the bug" was an overclaim and is withdrawn.

## Correction 2 — my criticism of the child's shim was wrong

I wrote that the shim "was not equivalent to pytest", citing its 12 passed / 12 failed against
pytest's 23 failed / 1 passed. **The shim's numbers were right and mine were wrong.** With a complete
fixture, real pytest reports **12 failed / 12 passed against the original — exactly what the shim
reported.** The discrepancy was my broken fixture, not the shim. That criticism is withdrawn; the
shim's counts are corroborated, not contradicted. The earlier text stands above as the record of what
I claimed.

## Scope of the correction itself, stated so it is not overread

The integrated change is a **left-edge numeric-fragment rule plus `finditer` continuation**. It
addresses the observed **DOI interior** case while preserving the tested genuine assertions. **It is
not a general identifier recogniser**: `v2.102` still fires (a letter is not numeric continuation),
and a match that is a **prefix** of a longer number still fires, deliberately, to protect the
registry's truncating idiom.

## ⚠ Not all gates are green

`lint_citations` **still exits 1 repo-wide and was NOT made green by I1** — it was never in scope.
`lint_consistency` is green, five other gates are green, and both pytest modules pass; **that is not
"all gates and tests green"** and must not be reported as such. The F1 source and publication
blockers — publisher-level confirmation, cross-version identity/content, Appendix A [2]/[3] — remain
open and untouched by any of this.

All logs above, including the defective run, are retained; **no record has been rewritten to erase a
failed attempt or an overclaim.**

---

# Correction 3, appended 2026-09-08 10:10 UTC — the shim did NOT absorb the predicate cases

At `20f19e5f` I wrote that the shim "absorbed that as passes", explaining its 12/12 against pytest's
23/1. **That is contradicted by the shim's own retained log and is withdrawn.**

`evidence/05-newtests-BEFORE-final.stdout` — the original shim run against the pre-fix code, retained
unaltered — records **all eight predicate cases as FAILED**:

```
FAIL test_begins_mid_number_predicate[0] … [7]     ← all eight, explicitly FAILED
FAIL test_a_bare_identifier_alone_does_not_fire
FAIL test_a_longer_number_ending_in_the_pattern_is_not_that_number
FAIL test_a_version_string_is_not_a_measurement
FAIL test_the_measured_case_a_doi_does_not_state_the_card_ratio
summary: 12 passed, 12 failed, 0 skipped
exit=1
```

**The shim's accounting was correct in every respect** — its 12 failed / 12 passed is exactly what
native pytest reports once the registry is present. My three successive claims about it were all
wrong, and all three are now withdrawn: that it was non-equivalent, that it under-reported, and that
it absorbed the predicate failures as passes.

**Also corrected:** native pytest **did collect all 24 cases**. Its 23/1 was 15 missing-registry plus
8 missing-helper **exceptions** — a fixture defect of mine, **not** an inability to collect, and not
semantic reproduction. My phrasing "cannot even be collected" was wrong.

**The distinct evidence, stated once and correctly:**

| evidence | what it shows |
|---|---|
| fixed-code native runs — **24 passed**, **27 passed** | the integrated linter and both modules pass on the real repository fixture |
| the original CLI before/after on the real tree — exit **1 → 0**, one finding removed, none added | the observed DOI interior case is addressed |
| **four** semantic negative failures (corrected-fixture run) | the identifier-semantics tests genuinely reproduce the bug |
| 8 missing-helper failures | an artifact of the helper's absence — **not** bug reproductions |
| the invalid 23/1 run | preserved as the record of my fixture defect |

No rerun, second shim, source lookup or log hunt was performed for this correction — it is a reading
of one already-retained file.
