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
