# P1 — contract, recorded BEFORE launch

Input revision **6eb48cce706cfa9d943afa5ef195d7e0d543676c**. `claude-opus-5` **medium**, saved first-party subscription, no paid fallback.
Deadline 2026-09-09T02:37:19Z. **Writing owner for `emc-mtap-prmt5-hypothesis.md`.**

## The issue — parent-verified

`research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis.md`, Appendix A, line 706, attributes
*"a peer-reviewed fusion-dependent PRMT5 requirement in a second EWSR1-fusion sarcoma **[2]**"*.

**Reference [2] is the bioRxiv preprint, which is NOT peer-reviewed.** The peer-reviewed Ewing result
is reference **[3]**. F1 found this and correctly declined to fix it as outside its named passages.
The same sentence appears in the body at line 491 without a marker.

⭐ A correction register that mis-cites its own evidence undermines the register's purpose, and this
one attributes peer review to a source the paper elsewhere is careful to label as not peer-reviewed.

## Finite acceptance

1. Correct the attribution so the peer-reviewed claim points at **[3]**, the Ewing result. Verify
   which reference is which **yourself** before editing.
2. Check line 491 and any sibling statement; make them consistent.
3. **⛔ No new reference, no reference-count change, no renumbering.** Only the pointer changes.
4. **⛔ Preserve the search-index-only grade** on the apparent JBC counterpart, and every
   preprint-read attribution: findings read from the preprint stay attributed to the preprint.
5. No other claim, number or hedge changes.
6. Report gate exit codes. If the fix would require adding a source or renumbering, **STOP and report
   that** — a supported stop is a successful result.

## Isolation and retention — binding

⛔ You may **not** write, copy, move or restore any file over a shared repository path for a baseline,
comparison or test. Baselines go **out** to your lane via `git show HEAD:<path> >` or by copying out —
never in. **No git write** of any kind; read-only git only.
⛔ No network, no source retrieval, no paid API, no GPU, no `scripts/preflight.sh`.
⛔ No census, no review-all sweep, no reopening of any earlier contract, no DFSP work.
There is no wet lab: no EMC efficacy, safety, selectivity or clinical-readiness claim. Invent no fact,
source, patient datum or measurement. If any request of yours is refused by content policy, stop that
branch, record the refusal verbatim, never route around it.
⛔ Do **not** weaken, relax, reorder or edit any gate. A tripped gate is a **finding to report**.
⚠ `lint_citations` fails repo-wide at exit 1 and is **pre-existing** — attribute it, and **do not
describe all gates as green**.
⛔ **DELETE NOTHING**, including your own lane.
Record `date -u`, `git rev-parse HEAD`, `git status --porcelain` at start and end.

Retain under `/tmp/claude-0/p1-lane/`: BEFORE, AFTER, unified diff, every gate's stdout/stderr/exit.
Stop at ~30 calls / ~30 minutes.
