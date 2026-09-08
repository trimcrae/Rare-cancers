# Y1 - provenance of an unsourced frequency claim

Input revision **545e6cf7c1dd7099f5072444d4dd166c4536206e**. `claude-opus-5` **medium**, saved subscription - no paid fallback, overage,
credits or GPU. Deadline **2026-09-09T02:37:19Z**. **~30 tool calls / ~30 minutes.**

## The claim

`research/manuscripts/dependency/emc-atr-collaborator-package.md` line 382, opening section 3.5:

> "**Roughly 3 to 4 per cent of EMC carries TCF12::NR4A3**, and TCF12 is not a FET-family gene."

**It carries no citation marker.** X1 inherited it, could not locate its provenance in the inputs it
read, and **left it unchanged and flagged** - correctly, since inventing a source would be worse than
leaving it open.

⭐ **It is load-bearing:** the very next sentence turns it into a testable class prediction. A
frequency with no source underwrites a prediction.

## The question

**Does any committed input support "roughly 3 to 4 per cent"?** Answer one of:

1. **SUPPORTED** - name the committed file, path and exact figure, and quote it. If a retained
   reference record supports it, give the citation that should be attached.
2. **PARTIALLY** - a related figure exists but not this one (e.g. a different denominator, a different
   series, a range that does not match). **Quote both and state the mismatch precisely.**
3. **UNSOURCED IN COMMITTED INPUTS** - nothing found. Say exactly where you looked, so the negative is
   bounded and reproducible.

⛔ **All three are successful outcomes.** Do not strain to reach "supported".

## Where to look

The committed literature and modalities JSONs, the ATR manuscript's own references and its review and
response, the changelog, and the retained R1/U1/W1-W3/X1 records. **Search on the numbers as well as
the words** - "3 to 4", "3-4", "3%", "4%", "0.03", counts over a denominator - because the claim may
exist as a fraction rather than a percentage.

## Deliver, in `/tmp/claude-0/y1-lane/`

A short memo with the verdict, the exact places searched, quotations, and - **only if SUPPORTED or
PARTIALLY** - a **proposed** minimal wording or citation fix. ⛔ **Do not edit the manuscript.**

## Bounds

⛔ No network, no retrieval, no new source, no census beyond this one question. ⛔ No write to any
shared repository path; everything in your lane. **No git write** - read-only git only. ⛔ No gate
rerun, no preflight, no figure or artifact change, no publication step. ⛔ Do not reopen a closed
contract or a held scope.
⛔ **Invent no source and no figure.** There is no wet lab: no EMC efficacy, safety, selectivity or
clinical-readiness claim, and **no epidemiological claim of your own** - you are tracing provenance,
not establishing a frequency. On a content-policy refusal, stop that branch, record it verbatim, never
route around it. ⛔ **DELETE NOTHING.** Record `date -u`, `git rev-parse HEAD`,
`git status --porcelain` at start and end.
