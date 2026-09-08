# Independent verification — uncommitted `citation-provenance-ledger.json` repair

**Verifier:** independent lane (no authorship of the change). **Date:** 2026-09-08.
**Target:** working-tree modification of `research/manuscripts/citation-provenance-ledger.json`
against HEAD `593e8dece4810627c4681d1206bca789fb131c08`.
**Fences observed:** no file in the tracked tree was edited, staged, committed, pushed or stashed by
this verification; the only file written is this one (untracked). No network. No broad suite, no
preflight. One targeted single-file pytest run, reported below in full.

---

## RECOMMENDATION: **ACCEPT**

Every load-bearing claim the lane made about this diff is true as measured. The seven PMCIDs are
verbatim the `verified_pmcid` values of the seven named `verified` DOI rows that already exist at
HEAD; the identifiers reach prose in exactly one place; the added text describes a binding, not a
retrieval; and the guard is not weakened — the change admits **exactly seven** identifiers and
**zero** others, measured by set difference rather than by counting.

Two **non-blocking** recommendations are in §7. Two things the parent must not misread are in §8 —
in particular, **this repair does not make the gate green**, and the campaign tree is being written
by other lanes while it is measured.

---

## 1. Are the seven PMCIDs really the `verified_pmcid` of the named existing rows?

**YES — all seven, exactly, with no mismatch.** Each named DOI has exactly **one** row in the HEAD
ledger, each is `status: verified`, `verified_on: 2026-08-27`, and each new PMCID row copies that
row's `verified_pmcid` character-for-character. I also compared the other carried fields, since a
transplanted row that keeps the PMCID but drifts on title or PMID would be the more dangerous defect:

| new row `id` | named DOI row (HEAD) | `verified_pmcid` match | `verified_pmid` | `verified_title` | `verified_journal` | `verified_on` / `verified_by` / `verified_source` |
|---|---|---|---|---|---|---|
| PMC10015005 | 10.1038/s41467-023-37139-y | ✅ | ✅ 36918561 | ✅ | ✅ Nat Commun | ✅ / ✅ / ✅ |
| PMC10682748 | 10.1016/j.patter.2023.100858 | ✅ | ✅ 38035198 | ✅ | ✅ Patterns (N Y) | ✅ / ✅ / ✅ |
| PMC11833048 | 10.1038/s41467-024-55655-3 | ✅ | ✅ 39962040 | ✅ | ✅ Nat Commun | ✅ / ✅ / ✅ |
| PMC12872444 | 10.1038/s41586-025-09992-y | ✅ | ✅ 41554984 | ✅ | ✅ Nature | ✅ / ✅ / ✅ |
| PMC13345910 | 10.1038/s41586-026-10644-y | ✅ | ✅ 42156544 | ✅ | ✅ Nature | ✅ / ✅ / ✅ |
| PMC13346116 | 10.1038/s41586-026-10652-y | ✅ | ✅ 42156546 | ✅ | ✅ Nature | ✅ / ✅ / ✅ |
| PMC7727361  | 10.1093/jamia/ocaa163 | ✅ | ✅ 32940710 | ✅ | ✅ J Am Med Inform Assoc | ✅ / ✅ / ✅ |

Structural diff of the whole file, computed by parsing both versions rather than by reading the
patch: **HEAD 237 entries → working tree 244**; **zero HEAD entries removed**; **zero HEAD entries
modified**; **7 added**; **one top-level key added** (`_pmcid_crossform_class_added_2026_09_08`); no
other top-level value changed. The file parses as valid JSON and each new row satisfies the shape
`test_the_ledger_is_well_formed_and_says_what_an_entry_does_not_mean` pins (`key == "kind:id"`,
non-empty `files`, `status` in `STATUSES`) — that test passes in the run in §5b.

**No mismatch found. No serious finding on this axis.**

## 2. "They reach prose in exactly one place" — true?

**TRUE.** `git grep -l` for each of the seven returns an identical file set of 35 paths. Exactly
**one** is a `.md`:
`research/autonomy/opus-capacity-campaign-20260908/reports/W67-ledger-field-cross-check.md`, and
within it exactly one line, **:246**, contains all seven — the sentence beginning "**Seven
`verified_pmcid` NOT-CARRIED, zero AGREES**". That file is tracked (committed in `49ed4d4e9`).

The other 34 hits are *not* prose under this linter's definition and I checked that rather than
assuming it: `PROSE_SUFFIXES = (".md",)` (`lint_citations.py:82`), and every other hit is a captured
lint log — `.out`, `.err`, `.stdout`, `.stderr`, and one `.txt`
(`X1-INTEGRATION-executed-artifacts/checks/lint_citations.txt`). None ends in `.md`, so none is
scanned as prose; none ends in `.json`/`.jsonl` (`ANCHOR_SUFFIXES`, `:73`), so none anchors either.
The 35th hit is the ledger itself, which `survey()` explicitly excludes from the anchor scan.

Note the shape of those 34 hits, because it is the reason the repair was needed at all: they are
prior runs of this same gate *reporting the seven as unanchored*. The identifiers exist in the tree
almost entirely as the gate's own complaint about them.

## 3. Does `checked_by` honestly describe a binding-only operation?

**YES.** Each row's `checked_by` reads, in full:

> "Binding only, no new retrieval: read off the `verified_pmcid` field of this ledger's own
> DOI:*&lt;doi&gt;* row (verified_on 2026-08-27). No PubMed, DOI-resolver or network call was made to
> add this row."

That is an accurate description of what I can independently confirm happened: the value is a copy of
a field that already existed at HEAD, and nothing in the diff could have come from a fetch. The
`note` field additionally states "This row records the binding; it does **not** claim a second,
independent check," and the class key states plainly that "nobody re-checked these papers on
2026-09-08, and no fetch product in this repository carries these PMCIDs" — which I confirmed
independently in §5a (the seven remain in the *unanchored* set after the repair; only their *NEW*
status changes). The lane did not quietly convert W67's negative finding into a positive one.

The one place where a fast reader could be misled is `verified_by`, discussed in §7.1. It is a
copied field, not an invented one, and the surrounding fields correct it — hence non-blocking.

## 4. Does the change weaken the guard? Can any identifier anchor that could not before?

**NO. The change admits exactly these seven keys and nothing else.** Three independent reasons:

**(a) The key is exact and kind-qualified.** `_key()` (`lint_citations.py:400-409`) returns
`"%s:%s" % (kind, str(ident).strip().rstrip(TRAILING))`, and `check()` builds
`known = {_norm_stored_key(e["key"]) for e in led["entries"]}` and tests `_key(k, i) not in known`.
Membership is exact string equality in a set — there is no prefix, glob or substring path. A ledger
row keyed `PMCID:PMC10015005` cannot admit `PMCID:PMC10015006`, and cannot admit any DOI or PMID:
`_norm_stored_key` partitions on the **first** colon, so the kind prefix is preserved and cross-kind
leakage is impossible. The prose extractor for this kind is `\b(PMC\d{6,9})\b`, which produces the
identical bare form, so no normalisation gap exists either.

**(b) Adding rows cannot anchor anything.** Anchoring and ledgering are separate mechanisms.
`survey()` excludes the ledger from the anchor scan by path (`ledger_rel`), and the ledger is
`.json`, so it is never scanned as prose. Adding text to it therefore cannot move any identifier
from unanchored to anchored — confirmed empirically: the **unanchored total is identical before and
after (283 → 283)**. Only the *NEW* (unledgered) subset changes.

**(c) Measured, not argued.** I extracted the full set of `::error::UNANCHORED` identifiers from a
before-run and an after-run in the same process (method in §5a) and diffed the sets:

```
only in BEFORE (i.e. fixed by this change) — 7 items:
  PMCID PMC10015005  PMCID PMC10682748  PMCID PMC11833048  PMCID PMC12872444
  PMCID PMC13345910  PMCID PMC13346116  PMCID PMC7727361
only in AFTER (i.e. newly broken by this change) — 0 items
```

**No weakening found.** The blast radius is exactly the seven identifiers the change names.

## 5a. Linter run — exit code and unanchored counts, before and after

⛔ **The working tree was never modified to obtain the "before".** `git stash` was not used. I copied
`git show HEAD:research/manuscripts/citation-provenance-ledger.json` to a scratch file **outside the
repository**, imported `lint_citations.py` as a module, and monkeypatched **`load_ledger` only** —
deliberately *not* the `LEDGER` constant, because `survey()` derives its self-exclusion path from
`LEDGER`, and repointing that constant silently re-admits the ledger to the anchor scan and
reproduces the 2026-08-07 self-anchoring bug. (I made that mistake on a first attempt and discarded
the numbers; they are not reported here.) Both runs were executed in **one process, back to back**,
so the working tree seen by `survey()` is as close to identical as this live tree allows.

Plain `python3 research/manuscripts/lint_citations.py` on the tree as-is:

```
EXIT CODE: 1
lint_citations: 1613 prose identifier(s), 283 unanchored, 244 in ledger
                (known_absent_upstream=1, unverified_at_baseline=143, verified=100)
lint_citations: 185 NEW unanchored identifier(s)
lint_citation_types: 52 type claim(s) checked against 13 cached record(s), 13 error(s),
                     1 retraction advisory(ies)
```

Paired before/after, same process:

| | prose ids | unanchored | ledger rows | NEW unanchored | exit code |
|---|---|---|---|---|---|
| **BEFORE** (HEAD ledger) | 1627 | 283 | 237 (verified=93) | **192** | **1** |
| **AFTER** (working-tree ledger) | 1641 | 283 | 244 (verified=100) | **185** | **1** |

**Delta = exactly −7 NEW unanchored, and the 7 are exactly the target PMCIDs** (set diff in §4c).
`unanchored` is unchanged at 283 in both, which is the correct behaviour: the seven are still
uncorroborated by any fetch product, they are merely now *enumerated*. That is the honest outcome for
a binding-only row and it matches what the class key claims.

⚠ **Caveat, and it is a real one:** the "prose identifiers" total differed between the two calls in
the same process (1627 vs 1641) and again in the pytest run (1761). Nothing about the ledger can
cause that. `_tracked()` includes untracked-but-not-ignored files, and **other campaign lanes are
writing `.md` files into this tree while I measure it.** The *NEW*-count delta is nonetheless
trustworthy, because I verified it by set difference and the added-in-between identifiers appear in
both sets or neither, leaving a clean symmetric difference of exactly the seven.

**⛔ Do not read exit code 1 as a failure of this repair.** The tree is red for two unrelated,
pre-existing reasons that this change neither causes nor fixes: **185 other NEW unanchored
identifiers**, essentially all of them DOIs in other campaign `reports/W*.md` files, and **13
`lint_citation_types` errors** ("TYPE CLAIM WITH NO CACHED METADATA"), which alone would force a
non-zero exit via `return max(rc, _types.check(prose=prose))`. Both are red at HEAD too (the before
run also exits 1). The repair is a correct **partial** fix: it removes its seven and touches nothing
else.

## 5b. Targeted pytest — `research/modalities/tests/test_lint_citations.py`

```
5 failed, 17 passed in 90.04s        (exit code 1; 22 collected, 0 skipped, 0 deselected)

FAILED test_the_repository_currently_passes
FAILED test_and_that_control_can_actually_pass_when_the_identifier_is_anchored
FAILED test_a_ledgered_identifier_stays_green
FAILED test_the_ledger_does_not_anchor_itself
FAILED test_and_that_control_can_actually_pass_when_the_arxiv_id_is_anchored
```

No test was skipped or deselected; I am not calling anything a pass that did not run. **None of the
five failures is caused by this change** — all five fail identically for the tree-state and
control-isolation reasons in §5a and §6, and all five would fail with the HEAD ledger in place
(`test_the_ledger_does_not_anchor_itself` fails on the list of unanchored-and-unledgered identifiers,
which is *longer* at HEAD: 192 vs 185). The well-formedness test that would catch a malformed new row
(`test_the_ledger_is_well_formed…`) is among the 17 that **passed**.

⚠ **Tree-mutation notice, reported and not "fixed".** The first pytest invocation ended with
`tracked_tree_guard.assert_tree_unchanged()` raising: `M
research/autonomy/opus-capacity-campaign-20260908/paper-lane/HOLD-atr-release-path.md` and `M
systems/graph/artifact-refs.json`. Those two files are **not** written by this test file; they were
modified by a concurrent campaign lane during the run, and both were still modified in `git status`
before my second invocation began. Per AUT-PD-186 I did **not** revert them and did not inspect
further — the change is another lane's evidence. Flagging it so the parent knows the guard fired and
why, and so nobody attributes it to this repair.

## 6. The lane's CONTROL-ISOLATION diagnosis — is the mechanism real?

**YES, the mechanism is real, it is currently active, and its practical effect is worse than the lane
stated.** I did not apply the proposed patch.

The final line of `lint_citations.check()` is, verbatim (`research/manuscripts/lint_citations.py:483`):

```python
    return max(rc, _types.check(prose=prose))
```

and the guard it calls is, verbatim (`research/manuscripts/lint_citation_types.py:363, 387`):

```python
def check(argv_report=False, prose=None):
    ...
    found = claims()
```

`claims()` takes no argument and performs **its own** scan of the tree for type claims. The `prose`
parameter is documented in that function's own docstring as "a **cost parameter, not a behaviour
one**" and it feeds only `retraction_sweep()`, whose output is advisory. Therefore
`_types.check(prose=…)` returns a value that is **independent of whatever `prose` dict a test
monkeypatches into `lc.survey`** — it reflects the real repository's type-claim state.

Five tests in `research/modalities/tests/test_lint_citations.py` monkeypatch `lc.survey` and then
assert on `lc.check()`:

* `test_a_pmid_typed_from_memory_is_caught` (asserts `== 1`)
* `test_and_that_control_can_actually_pass_when_the_identifier_is_anchored` (asserts `== 0`)
* `test_a_ledgered_identifier_stays_green` (asserts `== 0`)
* `test_a_fabricated_arxiv_id_is_caught` (asserts `== 1`)
* `test_and_that_control_can_actually_pass_when_the_arxiv_id_is_anchored` (asserts `== 0`)

Because the tree currently produces 13 type-guard errors, `_types.check()` returns 1 no matter what,
so `max(rc, 1) == 1` for **all five**. The observed consequence, direct from the pytest run:

* The three tests asserting `== 0` **fail**, with captured stdout proving the provenance axis was
  green and the failure came from the other axis. In
  `test_and_that_control_can_actually_pass_when_the_identifier_is_anchored`, the captured stdout is
  `lint_citations: 1 prose identifier(s), 0 unanchored, …` immediately followed by
  `lint_citation_types: 52 type claim(s) checked against 13 cached record(s), 13 error(s)` — i.e.
  **zero** unanchored, and a red return anyway.
* The two tests asserting `== 1` **pass unconditionally**. They cannot distinguish "the fabricated
  PMID was caught" from "the type guard was red for unrelated reasons," and would pass with the
  provenance logic deleted outright. That is the lane's claim, and it holds. These are precisely the
  two tests whose own docstrings warn "A negative control that cannot pass is not a control — it is a
  constant"; the harness the docstring guards against is the one now in place, arriving through the
  third axis rather than through the anchoring logic.

One correction to how the finding should be stated: this is **not** an unconditional property of the
code. If the type guard were green, `_types.check()` would return 0 and all five tests would isolate
correctly. The defect is that the controls are **not isolated from a third axis** and silently lose
their meaning whenever that axis is red — which it is today. That is still a genuine and serious
control defect, and it should be recorded as "the controls are contaminated whenever the type guard
is non-green," not as "the code always returns 1."

**Out of scope by fence, and left undone:** I did not apply, draft or evaluate the proposed patch.

## 7. Non-blocking recommendations

1. **`verified_by` is a copied DOI-batch narrative sitting in a PMCID row.** Each new row carries the
   source row's `verified_by` verbatim, including "convert_article_ids(id_type=doi) resolved seven of
   the eight … the eighth (10.1016/j.jclinepi.2017.08.010) has no PMC mapping". In a row whose `id`
   is a PMCID, that sentence describes a batch this identifier was a *product* of, not a check
   performed *on* it. It is a faithful copy rather than an invention, and `checked_by` + `note` +
   the class key all correct it — but a reader skimming `status: verified` and `verified_by` alone
   could take it for an independent PMCID verification. A four-word prefix such as "Inherited from
   the DOI row:" would close the gap.
2. **The `verified=` readout now counts seven cross-form duplicates.** The gate's printed summary
   went `verified=93` → `verified=100` without a single additional *work* being verified. The class
   key discloses this in the file; the printed line does not. Worth a sentence wherever that count is
   quoted, and worth knowing before anyone reports "seven more citations verified".
3. **No test pins the PMCID class the way `test_every_arxiv_ledger_row_records_how_it_was_checked`
   pins the ARXIV class.** The ARXIV precedent requires `checked_on`, `checked_by`, a non-blank
   `note`, and the presence of the class key. The new rows satisfy all four *today*; nothing enforces
   it for the next row added to this class. Adding the analogous test is the natural follow-up (and
   is outside my fence here).

## 8. What the parent must not conclude from this ACCEPT

* **Not** that `lint_citations.py` is green. Exit code is **1** before and after; 185 other NEW
  unanchored identifiers and 13 type-guard errors remain, unrelated to this change.
* **Not** that the seven papers gained corroboration. They are still **unanchored** (the total stayed
  283), and W67's finding that `verified_pmcid` is the one ledger field with no corroboration
  anywhere else in the tree **stands unchanged**. The change enumerates them; it does not
  substantiate them.
* **Not** that the numbers here are reproducible to the digit. The tree is being written by
  concurrent lanes; prose-identifier totals moved between runs minutes apart. The reproducible
  quantity is the **set difference**, which is exactly the seven.
