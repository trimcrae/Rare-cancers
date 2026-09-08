# Parent documentation-only qualification to L1's integrated docstring

Recorded 2026-09-08 10:48 UTC. **This is a parent edit to prose, not part of L1's executed
artifacts.** L1's original code, outputs, logs and PNGs are preserved unchanged in
`L1-executed-artifacts/`; nothing there is rewritten, and **no figure experiment was repeated and no
review was started.**

## What was too strong

The docstring L1 integrated said:

> "Deterministic: the only decorative freedom in the plot, the within-tier vertical offset, is derived
> from the gene's index in SHOW, so the same committed inputs render **byte-identical output in any
> process, under any PYTHONHASHSEED, on any machine**."

**"On any machine" overreaches the evidence.** The claim conflates two different things:

- **The offset formula** — `0.12 * (SHOW.index(g) % 5 - 2)` — genuinely is independent of the
  per-process hash seed, of iteration order, of the clock and of any RNG. That part is sound.
- **The rendered PNG bytes** — which also depend on the Matplotlib, Pillow, FreeType and font
  versions, the backend, and other environment details. **No cross-machine rendering experiment was
  ever run.**

What was actually measured is repeatable output across **fresh processes and hash seeds in one
recorded environment**: L1's four runs (`PYTHONHASHSEED` unset, `12345`, `7`) and my three
(unset, `999`, `42`), all yielding sha256 `130042b6...` at 128,250 B.

## What the docstring now says

It states the determinism claim **about the offset**, lists what the offset does not depend on, cites
the seven measured runs, and then says plainly that this is not a promise of byte-identical PNGs
anywhere — naming Matplotlib, Pillow, FreeType, fonts and backend as further influences on the
rendered bytes, and recording that **no cross-machine rendering experiment was run**.

## Scope of this edit

**Prose only.** Unchanged and verified after the edit: the offset line at `jitter = 0.12 *
(SHOW.index(g) % 5 - 2)`, all data and mappings, every caption including "no EVALUATED antigen here",
and **the committed PNG, which was not regenerated** (`git status` showed only the source file
modified). `git diff --stat` is 11 insertions / 3 deletions, entirely inside the module docstring.

## Gates after the edit

`lint_consistency`, `lint_style`, `lint_claims`, `lint_submission_residue`, `lint_asymmetry` and
`submission_metrics` **exit 0**. **`lint_citations` exits 1** — pre-existing and repo-wide, unrelated
to this file. **Not all gates are green.**
