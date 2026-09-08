# P1 — collection and adjudication against `CONTRACT-P1-mtap-prmt5-appendix-attribution.md`

Collected 2026-09-08 11:17-11:20 UTC. **Scope note:** this P1 is a *new* lane in this cycle and is
distinct from the earlier campaign's closed P1-P6 intake tasks despite the reused label.

## Child identity — from the transcript

| item | measured |
|---|---|
| child | `aeef648a37893844e` |
| original JSONL | `P1-executed-artifacts/ORIGINAL-CHILD-TRANSCRIPT-aeef648a37893844e.jsonl`, **129,076 B**, `cmp`-identical |
| model strings | **`claude-opus-5` only, 0 others** — parsed from the transcript's model fields, **not** inferred from contract text |
| tool pairs | **13** (self-reported 9) |
| **full lifetime** | **11:13:44.357Z -> 11:15:50.524Z** (~2 m 6 s) of a ~30 min bound |

## The correction

Appendix A's register attributed *"a peer-reviewed fusion-dependent PRMT5 requirement in a second
EWSR1-fusion sarcoma"* to **[2]** — the bioRxiv preprint, which the same reference entry says *"is not
certified by peer review"*. The peer-reviewed Ewing result is **[3]**. One character changed:
`[2]` -> `[3]`.

**A register that mis-cites its own evidence undermines the register**, and this one credited peer
review to a source the paper is elsewhere careful to label as not peer-reviewed.

## Parent verification — measured, not accepted

| check | result |
|---|---|
| diff size | `git diff --numstat`: **1 insertion, 1 deletion** — a single line |
| §9 reference list | lines 671-682 **byte-identical** before and after (`diff` empty) |
| marker totals | **24 -> 24**; the only movement is `[2]` 3 -> 2 and `[3]` 9 -> 10 |
| search-index grade | mentions **2 -> 2**, unchanged |
| references added/removed/renumbered | **none** |

So exactly one pointer moved and nothing else in the file did.

## What P1 checked and deliberately did not change

- **Line 491** (§4.4 body) was **already correct** — it carries `[3]`. The contract anticipated it
  might be unmarked; P1 verified rather than assumed, and left it.
- **Lines 124 and 571** cite `[2]` for the preprint's *own* findings and for its non-certification
  statement — correct as-is, preserved. Preprint-read attributions therefore stay with the preprint.
- **Line 617** carries no marker and does not claim peer review — consistent, left alone.
- Reference [2]'s entry retains verbatim *"the findings cited here were read from this preprint"* and
  the full search-index-only grade on the apparent JBC counterpart.

## Gates — my own run, and NOT all green

`lint_consistency` **exit 0** (`0 ERROR across 29 files` — the I1 repair holds), `submission_metrics`,
`lint_style`, `lint_claims`, `lint_submission_residue`, `lint_asymmetry` all **exit 0**.
**`lint_citations` exits 1** — pre-existing and repo-wide; its hard errors are `TYPE CLAIM WITH NO
CACHED METADATA` in campaign report files, none in this manuscript and none concerning [2] or [3].
The `mtap-prmt5` strings in its output are **advisory NOT-SWEPT lines**, including the JBC DOI and
PMCID that are unsweepable precisely because the counterpart was never retrieved — **the search-index
grade doing its job, not a regression.** No gate was weakened, relaxed, reordered or edited.

Main text 5,588 w, abstract 249 w, 5 items, **refs 11** — all unchanged.

## Standing

The mtap-prmt5 blockers recorded in `BLOCKERS-mtap-prmt5-publication-readiness.md` are **unchanged**:
publisher-level confirmation and cross-version identity remain unconfirmed, and the four blocked
routes stay unretried. **This closes the third blocker on that list — the Appendix A attribution —
and only that one.** Not publication acceptance.

## Retention

`/tmp/claude-0/p1-lane/` **intact, nothing deleted**, pending an exact-directory receipt.
