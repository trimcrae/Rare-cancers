# W1 — assemble a PROPOSED Supplementary Table S3

## Why

U1's review found R1's unknown **U3 partly resolvable**: Table S3 is **buildable from committed
inputs**. Build it.

## Input — one file, digest pinned

`research/modalities/emc-fet-construct-designs.json`, **73,415 B**, sha256 begins
`726aae02ae38b41c34d4398363e3581c`. It contains `registered_predictions`.

Scope comes from what the **R1 proposal, U1's memo and the changelog** say the table is for — read
those, in `paper-lane/R1-executed-artifacts/`, `paper-lane/U1-executed-artifacts/` and
`research/manuscripts/dependency/emc-atr-collaborator-package-changelog.md`.

## Deliver, in `/tmp/claude-0/w1-lane/`

1. **The proposed table** (markdown), built **only from existing recorded entries**.
2. **A reproducible, scoped assembly script** that reads the committed JSON and emits the table.
3. **The exact input digest** and **row/field provenance** — for every cell, which JSON path it came
   from.
4. **A faithfulness check you actually run**: verify the assembled output carries its selected
   original fields unaltered, and show the command and result.

⛔ **Preserve `registered_predictions` and every original fact.** No new design, protocol, analysis,
tier or rule change. ⛔ **If a column has no defensible source, mark it UNRESOLVED** — do not derive,
guess or infer it.

## Bounds — binding

Input revision **c365b4e836358274703cef278417193f615629f3**. `claude-opus-5` **medium**, saved first-party subscription — no paid fallback,
overage, credits or GPU. Deadline **2026-09-09T02:37:19Z**.

⛔ **No write to any shared repository path** — everything in your own lane. **No git write**;
read-only git only. ⛔ No manuscript, registry, tier, rule, figure or shared-artifact edit. ⛔ No
unchanged gate rerun, no `scripts/preflight.sh`. ⛔ No broad review, 47-item audit, census, history
reconstruction or publication step.
⛔ **Mark anything you cannot source as UNRESOLVED. Never invent a value to fill a column or a claim.**
There is no wet lab: no EMC efficacy, safety, selectivity or clinical-readiness claim. Invent no fact,
source, patient datum or measurement. If a request of yours is refused by content policy, stop that
branch, record the refusal verbatim, never route around it.
⛔ **DELETE NOTHING.** Retain your inputs' digests, your exact commands and their results. Record
`date -u`, `git rev-parse HEAD`, `git status --porcelain` at start and end; confirm you changed
nothing shared.

Final title, preregistration amendments, manuscript integration and publication remain with the
existing decision process. Stop at a supported finite result, or ~35 tool calls / ~30 minutes.

