# P3 — READ-ONLY contract, recorded BEFORE launch

Input revision **6eb48cce706cfa9d943afa5ef195d7e0d543676c**. `claude-opus-5` **medium**, saved first-party subscription, no paid fallback.
Deadline 2026-09-09T02:37:19Z. **⛔ READ-ONLY: this worker writes NOTHING into the repository.**

## The issue — a serious claim-level flag already on file

`research/manuscripts/nr4a3-program-map.md` records, of the neoantigen lane:
*"the neoantigen lane still owes a correction — its 26 binders span seams that do not exist"*.

If that is true of the committed neoantigen manuscript, the paper reports predicted binders across
junction seams that the corrected arithmetic says are not there — a **claim-level defect**, not
hygiene.

## Task — verify, do not fix

1. Establish what the committed neoantigen manuscript
   (`research/manuscripts/neoantigen/emc-vaccine-development-path.md`) actually claims about its
   binders and their seams: how many, spanning what, and on what artifact.
2. Establish, from **committed artifacts only**, whether those seams are the ones the 2026-08-06
   route-framing audit (`systems/AUDIT-2026-08-06-routes.md`) invalidated — the audit that found
   `junction_aso.py`'s real-mode path did the defective exon->CDS mapping, producing a seam at NR4A3
   CDS nt 1081 resuming at residue 361 against a corrected range of `[1, 1]`.
3. Report precisely: **is the defect live in the committed manuscript, already corrected, or
   undecidable from committed inputs?** All three are acceptable answers. **Undecidable is a real
   result** — say exactly what is missing.

## Bounds

⛔ **Change nothing.** ⛔ **Do not regenerate any artifact** — the program map notes regeneration needs
Ensembl and must run in CI; that is **out of scope and not to be attempted**. ⛔ Do not touch the ASO
lane, any frozen asset, or any patient-facing file. ⛔ Make no claim about vaccine efficacy or clinical
readiness — this is about internal arithmetic consistency only.

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

Retain under `/tmp/claude-0/p3-lane/`: your notes and quoted extracts.
Stop at ~35 calls / ~35 minutes.
