# W2 — resolve the ATR Figure 1 legend dependency from code and data

## Why

U1 read the figure and found Panel A has **no key at all**: the dashed boxes and internal ticks are
unlabelled. U1 flagged its own reading of them (RG dipeptides; RGG regions) as **inference, not
pixels**. That inference now needs a source — or an honest unresolved.

## Question

**What do Panel A's dashed boxes and ticks actually encode**, according to the committed generator and
its data — and **what minimal caption/key wording is justified** by that?

## Inputs

`research/manuscripts/figures/emc_fusion_frame_figure.py` (the generator) and the committed data it
reads. **U1's panel map and pixel observations are in `paper-lane/U1-executed-artifacts/` — reuse
them; ⛔ do NOT repeat the visual inspection and do not re-open the image.**

## Deliver, in `/tmp/claude-0/w2-lane/`

- **The exact generator lines and data fields** that draw the dashed boxes and the ticks, quoted with
  file and line numbers.
- A **concise proposed caption/key wording** justified by those lines — or an **exact
  UNSUPPORTED/UNRESOLVED result** if the code does not settle it.

⛔ **Do not claim the code alone proves what is legibly rendered.** Code shows intent; U1's pixels show
appearance. Where they agree, say so; where the code is silent, say **unresolved**. ⛔ No figure
regeneration, no new biological claim, no manuscript edit, no full review.

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

