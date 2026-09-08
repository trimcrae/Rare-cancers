# P-AB2 — the census stripper used one column convention for two different ones

**Owner:** P-AB2 (sole). **Scope:** `research/manuscripts/claim_coverage.py` and its directly
applicable focused mechanism test
`research/manuscripts/tests/test_the_census_credits_only_executable_references.py`. Nothing else was
edited. **Not committed and not pushed** — the parent integrates.

**Frozen module the defect was reproduced against:** `f43f1495f40d8aff7b4f34bd385d55aac521a500`,
`claim_coverage.py` sha256 `d6f47d118f854969371f8c2b5aa5ac48bcf5580f644ed72d63e94c393d4b8379` —
byte-identical to the `source_sha256` recorded in root's counterexample, so the reproduction ran
against exactly the source root reviewed.
**Repaired module:** sha256 `094a20684fc7db99ad383f60e032a48c3ca853d65d5686c414ea6ae67b6462af`.

## Root's evidence, intake

Both original byte streams are retained unmodified under `evidence/root-reviewer-originals/`,
CRLF endings and non-ASCII bytes untouched, alongside the transfer manifest:

| file | bytes | sha256 (re-measured after copy) |
| --- | --- | --- |
| `unicode-comment-counterexample.json` | 989 | `bb0fd14f6bf3cea3b2f179ac6fa4022089b93a949cce22a9c044a595ea37f800` |
| `retained-two-helper-functions.py` | 2729 | `d9e398f90dac5ad0e573d8779ac2d5f5f23196d068b38d944f4e56e8bd785119` |

Both match their stated identities exactly. The retained helper module was **read, not executed**;
the counterexample is replayed by `evidence/counterexample_repro.py`, which reads the fixture and
root's recorded defect output **from the original JSON** rather than retyping either.

## The defect

`_executable_source` blanks comment and docstring characters so that the census decides which
document a guard reads from text the interpreter actually evaluates. It converted **both** kinds of
column offset with one `offset()` helper that decoded a UTF-8 **byte** prefix:

* `ast.Constant.col_offset` / `end_col_offset` really are **byte** offsets into the line — the
  decode is correct there;
* `tokenize.TokenInfo.start[1]` / `end[1]` are Python **character** offsets — the decode is wrong
  there, and drags the comment span one position left per non-ASCII character earlier on the line.

On root's fixture (81 `é` in an executable literal, then a trailing comment naming a manuscript) the
comment span slid off the comment and onto the string: **24 characters were blanked out of the
executable literal and the comment's manuscript basename survived intact** — the ghost-witness path
this whole repair exists to close, reopened by an encoding bug. `evidence/attempt-02` reproduces
root's `actual_blank` **byte for byte** (`reproduces root's defect output: True`, EXIT=1).

## Exact changes

### 1. `claim_coverage.py` — `_executable_source`: two conversions, one per convention

Before:

```python
    def offset(lineno, col):
        # `col_offset` is a UTF-8 byte offset; every source here is read as text, so convert.
        line_start = starts[lineno - 1]
        line = src[line_start:starts[lineno]]
        return line_start + len(line.encode("utf-8")[:col].decode("utf-8", "ignore"))
```
…used for the AST docstring spans **and** the `tokenize` comment spans.

After: `ast_offset(lineno, col)` keeps the byte decode verbatim and is used only for
`node.col_offset` / `node.end_col_offset`; a new `token_offset(lineno, col)` returns
`min(line_start + col, starts[lineno])` and is used only for `tok.start` / `tok.end`. The comment
above each states which convention it serves and names the counterexample. Full hunk:
`evidence/claim_coverage.py.diff`.

### 2. Focused non-ASCII cases — both channels

In `test_the_census_credits_only_executable_references.py`:

* **inline comment**, mechanism level —
  `test_a_comment_after_non_ascii_code_is_blanked_and_the_code_is_not`: the executable non-ASCII
  literal must survive and the comment (basename included) must be blanked.
* **docstring**, mechanism level —
  `test_a_non_ascii_docstring_is_blanked_to_its_last_character`: a single-line docstring whose
  non-ASCII runs to the closing quote must be blanked **to its tail**, and the executable non-ASCII
  literal on the next line must survive. This holds the AST side from the other direction, so
  "just use character offsets everywhere" cannot pass either.
* **scope level**, through `_test_patterns`: three new parametrized fixtures —
  `comment_only_non_ascii` (must NOT be credited), `docstring_only_non_ascii` (must NOT be
  credited), `code_reference_non_ascii` (MUST stay credited, so a stripper that simply blanked more
  could not pass the first two by destroying real coverage).
* ⚠ **A fixture geometry note is written into the test, because the first version passed for the
  wrong reason.** `evidence/attempt-03` is retained: with a long trailing note the mis-converted
  span reached back across the `#` and clipped the front of the basename, so the ghost witness
  escaped detection at scope level. The comment was shortened relative to the padding
  (`evidence/attempt-04`) and the case then fails on the frozen module as it must.

### 3. `_test_patterns` docstring — corrected, it described code that is not there

Before: *"…IN THIS MODULE OR ONE IT IMPORTS … imports are followed so that a guard naming its
document through a registry or a runtime lookup is not dropped. See `_executable_source` and
`_reachable_code` above…"* plus a paragraph beginning *"ONLY APPLICABILITY FOLLOWS IMPORTS"*.

The final implementation reverted that: imports are **not** followed and there is **no**
`_reachable_code` in this module. After: the docstring says the scope test and the harvest run over
this module's own source only, that following imports (and a `_reachable_code` helper to do it) was
written, measured and **reverted** — pointing at the block comment above the function that records
the measurement — and that a guard reaching its document only through an import or a runtime lookup
**is** dropped, which are the reported false negatives, not a gap the docstring papers over.

### 4. The global "upper bound" claim — removed, three sites plus the test module

The acknowledged false **negatives** (a guard that computes exposes no literal; a guard reaching its
document through an import is not credited at all) run opposite to the acknowledged false
**positives**, so there is no global bound on actual coverage in either direction.

* module docstring: *"Treat the covered count as an upper bound and the uncovered list as the
  finding"* → *"The finding is the uncovered list"*, followed by an explicit note that `covered` is
  not a bound in either direction and why, dated and attributed to this repair.
* the ablation-exemption comment, which justified itself by citing *"this module's own docstring
  calls the covered count an upper bound"* → now argues from what the census actually says
  (a selective pattern matched the sentence; matching words is not asserting about digits).
* the P-AB block comment's *"and `covered` is still an upper bound"* → the two failure directions
  named, and `covered` stated to bound actual coverage neither above nor below.
* the test module docstring carried the same sentence and is corrected in step.

The reported false positives and false negatives themselves are **preserved verbatim** — the
measured fusion-output `7 → 0` and fusion-partner `95 → 87` losses, the rejected import-following
widening and its measurement, the `claim_ablation.guards_reading` sibling channel, and the AUT-PROP-025
counterexample are all untouched. No floor moved, no filename was planted, no endpoint source
binding was changed.

## Checks — every attempt preserved, none overwritten

| file | what it ran | module | exit |
| --- | --- | --- | --- |
| `attempt-01-BEFORE-counterexample.txt` | counterexample replay | frozen | **1** — harness path bug (repo root), not the census; kept |
| `attempt-02-BEFORE-counterexample.txt` | counterexample replay | frozen `d6f47d11…` | **1** — DEFECT REPRODUCED, byte-identical to root's `actual_blank` |
| `attempt-03-BEFORE-focused-mechanism-tests.txt` | new test file vs frozen helper | frozen `d6f47d11…` | **1** — 2 failed, 9 passed; the scope case passed for the wrong reason |
| `attempt-04-BEFORE-focused-mechanism-tests.txt` | same, tightened fixture | frozen `d6f47d11…` | **1** — 3 failed, 8 passed (ghost witness now caught at scope level) |
| `attempt-05-AFTER-focused-mechanism-tests.txt` | focused mechanism test | repaired `094a2068…` | **0** — 11 passed |
| `attempt-06-AFTER-counterexample.txt` | counterexample replay | repaired `094a2068…` | **0** — literal preserved, basename erased |
| `attempt-07-AFTER-census-check-endpoint.txt` | `claim_coverage.py --check` | repaired | **1** — see below |
| `attempt-08-BEFORE-census-check-endpoint.txt` | `--check` from a frozen-HEAD copy | frozen | **1** — identical output |
| `attempt-09-binding-identity-diff.txt` | diff of the two `--check` runs | — | **0** — no difference |

Every file records the actual command, the module sha256, stdout+stderr and a real exit code
(`${PIPESTATUS[0]}` where a pipe was used). No test was skipped or deselected.

**The `--check` exit 1 is pre-existing and is not this repair's.** It reports only that
`claim-coverage.json` is stale for `methods-record/degrader-methods-failure-record.md`
(sentences 124 → 194, with_a_number 54 → 102), a manuscript another owner has modified in the shared
tree in this session. The frozen module produces that **same output, byte for byte**
(`attempt-09`, no difference), which is the evidence that this repair moved **no** census binding:
repaired and frozen disagree with the committed artifact in exactly the same four fields and nowhere
else. The artifact is not regenerated here — it is not P-AB2's to write, and doing so would fold
another owner's manuscript change into this repair.

## Scope limits, stated rather than glossed

* ⛔ The BEFORE runs used a **copy** of the frozen module in a scratch directory (and, for
  `--check`, a temporary same-directory copy that was deleted immediately); the original P-AB
  report, code and partials are untouched, and P-AB2 modified no committed file outside the two it
  owns. Other files do show as modified in this shared tree (`build_submission_pdf.py`, the degrader
  methods record, the fusion-output manuscript); those are other owners' in-flight work, not this
  repair's.
* This closes an **encoding** defect in an existing screen. It does not make the census a
  measurement: it remains a static screen over harvested literals, and `claim_ablation` is what runs
  the guards.
* Only Python **comment** and **docstring** spans are covered. `_executable_source` still derives its
  line table from `str.splitlines(keepends=True)`, which also splits on `\x0c`, ` ` and kin — a
  separate offset hazard, unexercised by any case here, not repaired, and recorded rather than
  claimed closed.
* The `claim_ablation.guards_reading` sibling channel is still open, as the existing comment says.
* No broad suite, no ablation, no census or gate amnesty, no source query, no manuscript revision,
  no re-audit of the P-AB whole report, and no reopening of RUN11/RUN12.
