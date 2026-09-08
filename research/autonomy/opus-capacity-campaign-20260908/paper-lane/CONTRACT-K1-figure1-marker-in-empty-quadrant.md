# K1 — contract, recorded BEFORE launch

`date -u` **Tue Sep  8 10:19:28 UTC 2026**. Input revision **b0f0ffa450e89b44677f37e3c141a2f762955069**. Same parent/controller, same session, `claude-opus-5`
**medium**, saved first-party subscription — no overage, no credits, no paid fallback, no new
controller. Deadline **2026-09-09T02:37:19Z**, never extended.

## The issue — parent-verified, from ready review evidence

**Peer review item 4** (`emc-surface-target-landscape-peer-review-2026-08-10.md`) objects that the
figure places a marker **inside a region its own caption calls empty**:

> "a marker inside it: B4GALNT1, plotted at x = 0 and labelled '(sel n/a)'. A gene with no selectivity
> value is being placed at a measured selectivity of zero, inside a region captioned empty."
> … *What would resolve it.* "… Redraw or replace the figure … at minimum, **no marker may sit in a
> region annotated as empty, and a gene with no selectivity value must be shown off-axis rather than
> at a measured selectivity of zero**."

**Measured by me at the revision above, in `research/modalities/emc_surface_figure.py`:**
- line 52 — comment: *"B4GALNT1 is not in the actionable seed; enrichment may be absent -> place at
  x=0 with a flag."*
- line 79 — `lab = LABEL.get(g, g) + ("" if has_enr else " (sel n/a)")`
- line 90 — caption text: *"the selective-and-restricted quadrant is empty for classic protein
  antigens"*

⭐ **The defect is still exactly as the review described it.** The *text* half of item 4 was resolved
(the manuscript now re-scopes the empty intersection to "the antigens the filter saw", lines 284 and
833) — **the figure half was not.**

## Finite acceptance

1. **No marker sits in a region the caption calls empty.** A gene with **no selectivity value** must
   not be drawn at a measured selectivity of **0**. Place such genes **off-axis** — a visually
   separated "not evaluated" band or margin — or omit them from the plotted area and name them in the
   caption. The chosen treatment must be unmistakable to a reader who does not read the code.
2. **Caption and drawing must agree**, both in `emc_surface_figure.py` and in the manuscript's
   Figure 1 caption (manuscript line ~609). If the drawing changes, the caption changes with it.
3. **⛔ No measured value may move.** Every gene that *has* a selectivity value keeps its exact
   plotted position. You are changing the placement and annotation of genes **without** a value, and
   nothing else. Do not recompute, re-derive or adjust any number.
4. **Regenerate the figure and show it worked**: capture the exact command, stdout, stderr and exit
   code, and record the output artifact's path, byte size and sha256 before and after.
5. **No overclaim.** The figure must not imply B4GALNT1 was evaluated and found unselective — the
   manuscript's own table says "not in the scan output / not evaluated / RESTRICTED", and the drawing
   must be consistent with that.
6. Linters run and reported honestly with exit codes. ⛔ A tripped gate is a finding to report, never
   a reason to weaken, relax, reorder or edit a gate. ⚠ **`lint_citations` fails repo-wide at exit 1
   and is pre-existing** — attribute it, and **do not describe all gates as green.**
7. If the fix cannot be made without moving a measured value or inventing a position, **STOP and
   report that exactly.** A supported stop is a successful result.

## ⛔ Isolation — tightened after J1

**J1 copied its baseline over the live manuscript to run linters, then copied it back.** That is now
explicitly forbidden.

**You may not write, copy, move or restore ANY file over a shared repository path for the purpose of
a baseline, a comparison or a test.** Take baselines with `git show HEAD:<path> > /tmp/...` or by
copying **out** to `/tmp/claude-0/k1-lane/`. Never copy **in**. Your only writes to the repository
are the deliberate edits named in acceptance 1–2, plus the regenerated figure artifact in 4. **No git
write of any kind** — no commit, add, stash, checkout, restore; read-only git only.

## Out of scope

⛔ No DFSP-only sensitivity analysis and no recomputation of any contrast — that remains undone and is
not admitted here. ⛔ No edit to any other manuscript, to the SI, to the registry, or to the linters.
⛔ No network, no source retrieval, no denied-route retry. ⛔ No `scripts/preflight.sh`, no GPU, no
paid API. I1, J1, F1, G1, H1 contracts are closed and are not reopened. There is no wet lab: no EMC
efficacy, safety, selectivity or clinical-readiness claim. Invent no fact, source or measurement.

## Retention

Under `/tmp/claude-0/k1-lane/`: pre-edit copies of every file you touch, post-edit copies, unified
diffs, the figure before and after with hashes, and every command's stdout/stderr/exit code.
⛔ **DELETE NOTHING**, including your own lane — cleanup needs an exact-directory receipt that does not
exist.

## Stop conditions

Acceptance 7; the defect already being fixed on reading; any step needing a prohibited action; or
**~40 tool calls / ~40 minutes**. Early with a supported result or block is success; padding is not.
