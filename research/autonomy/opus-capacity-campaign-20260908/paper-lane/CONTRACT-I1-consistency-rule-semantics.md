# I1 — code contract, recorded BEFORE launch (reproducible-code lane)

`date -u` **Tue Sep  8 09:27:18 UTC 2026**. Input revision **d3e5e04c5cfaa62ba3c3c8c3942e5f9c49c52241**. Same session, sole parent/launcher, `claude-opus-5`
**medium**, existing saved first-party subscription — no overage, no credits, no paid fallback, no new
controller. Deadline 2026-09-09T02:37:19Z. Disk: 20 GiB free, floor 10 GiB.

**This is a separately scoped reproducible-code decision.** It is **NOT** an F1 source-verification
reopening and **NOT** permission to bypass a failed guard.

## Question

Does `S-card_ratio_4090_over_3090_2_10` mistakenly treat a digit sequence **inside a DOI or other
identifier** as an assertion of a superseded numeric measurement?

**Observed trigger:** `lint_consistency` exits 1 with
`emc-mtap-prmt5-hypothesis.md:673: ERROR [S-card_ratio_4090_over_3090_2_10] superseded value '2.102'
stated without marking it superseded`. The matched `2.102` lies inside
`10.1016/j.jbc.2022.102434` (…202**2.102**434).

⚠ **My previous "naive substring false positive" wording was withdrawn as an unestablished
interpretation.** I1 must **establish or refute it from the implementation**, not inherit it.

## Exact inputs

| path | role |
|---|---|
| `research/manuscripts/lint_consistency.py` | implementation, 33,659 B at the revision above |
| `research/manuscripts/pinned-figures.json` | registry; the rule is `"id": "card_ratio_4090_over_3090_2_10"` at line 1731 |
| `research/modalities/tests/test_lint_consistency.py` | existing tests |

## Order of work — inspection FIRST

1. Read the implementation's matching path, the registry's semantics for a superseded entry, and the
   existing tests **before proposing anything**. Establish what the rule is **intended** to assert.
2. Only if inspection establishes erroneous literal/substring matching, implement the **smallest
   general semantic correction**.

## Finite acceptance

1. **General, not special-cased.** ⛔ **PROHIBITED: any paper-specific or DOI-specific exclusion**, any
   allowlist naming this manuscript, this DOI, or this rule id. The correction must be a semantic
   improvement to how a numeric assertion is recognised — e.g. identifier/boundary context — that
   would behave the same for any paper.
2. **True positives preserved, demonstrated by test.** Regression tests must include **real superseded
   measurement positive cases**, among them **the originally flagged measurement this rule exists to
   catch** (the RTX 4090 / RTX 3090 card ratio, current value 1.745x, superseded 2.102), and the
   supported formats and boundaries the registry actually uses. A correction that silences the DOI
   case by also weakening detection is a **NO-GO**.
3. **Negative case included.** A DOI-containing string must be shown not to trigger. The identifier
   `10.1016/j.jbc.2022.102434` **may be used as a test string WITHOUT confirming the publication** —
   it is a lexical fixture here, and the publisher/cross-version status stays unconfirmed.
4. **Boundary tradeoffs explained in your report**: what the new rule would now miss or still catch at
   the edges (e.g. a genuine value adjacent to punctuation, a version string, a page range).
5. ⛔ **PROHIBITED, any of which is an automatic stop:** fake superseded labels; relaxing a threshold;
   deleting an assertion; rebaselining errors away; changing any scientific claim or the source ledger;
   suppressing another gate; editing a manuscript. **A failing gate must not be weakened merely to
   obtain a pass.**
6. **If the rule's intent cannot be established, or the correction cannot preserve true positives:
   record an exact NO-GO with the evidence and STOP.** A supported NO-GO is a successful result.

## Isolation — binding

**Work in your own path `/tmp/claude-0/i1-lane/`.** Copy in only the three files above (small,
task-scoped copies — **no large or full checkout**). **⛔ Make NO edit to the shared tree**: do not
modify `research/manuscripts/lint_consistency.py`, `pinned-figures.json`, the tests, or any
manuscript in `/home/user/Rare-cancers`. A manuscript worker's linter baseline must stay
undisturbed. Deliver your corrected file and tests **as files under your own path**; the parent
integrates explicitly owned code and test paths after adjudication.

**⛔ No git write of any kind** — no commit, add, stash, checkout, restore. Read-only git only.
**⛔ No network, no publisher lookup, no source retrieval** — none is needed or permitted in this lane.
**⛔ No paid API, GPU, CI or model-access bypass.** Do not run `scripts/preflight.sh`.

## Verification you must actually run

Run your tests and the linter **against your copies**, capturing the **exact command, stdout, stderr
and exit code** for each. Show the flagged case failing before and passing after, and every true
positive still detected after. Measure free disk at start and end and **leave ≥10 GiB**.

## Retention — CLAUDE.md §8 applies

Preserve under `/tmp/claude-0/i1-lane/`: the **original** copies as taken, your modified code, the
unified diff, the test files, and every command's stdout/stderr/exit code as generated.
**⛔ DELETE NOTHING**, including your own scratch — cleanup requires a directory-specific local
receipt that does not yet exist. Nothing is re-run to recreate evidence.

## Stop conditions

Stop at a supported NO-GO; if inspection shows the match is **correct** (the rule is doing its job and
the DOI genuinely asserts a superseded value); if any acceptance item cannot be met without a
prohibited action; or at **~40 tool calls / ~40 minutes**, whichever is earlier. Returning early with a
supported result or block is success; padding is not.

## Standing regardless of outcome

The MTAP/PRMT5 **publisher-level confirmation**, **cross-version identity/content**, and **Appendix A
[2]/[3] attribution** blockers remain open whatever this lane concludes. **No publication acceptance
follows from a green gate.**
