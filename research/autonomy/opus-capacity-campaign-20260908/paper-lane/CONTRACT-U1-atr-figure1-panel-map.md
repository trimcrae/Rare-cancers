# U1 — ATR Figure 1: what does it actually render?

## Why

R1's proposal left **U2 unresolved**: the Figure 1 caption and panel assignments, because **it did not
open the images**. R1 recommends inserting the figure (its decision **D3**) but drafted no caption. The
files are committed and readable under existing authority; a prior lane's finite scope is not an access
barrier.

## The exact inputs

| file | bytes | sha256 (first 32) |
|---|---|---|
| `research/manuscripts/figures/emc-fusion-frame-fig1.png` | **360,656** | `fa94675f436692344f5514ac1d08f7d4` |
| `research/manuscripts/figures/emc-fusion-frame-fig1.pdf` | 83,262 | `0d9aff26ec469e669a6ee1a6e310eaf9` — **only if the PNG is insufficient** |

Also available, as **corroboration only**: the committed generator and the committed data artifact
`research/modalities/emc-fet-frame-and-composition.json`. R1's proposal is in
`paper-lane/R1-executed-artifacts/`.

## Deliver

1. **Read the PNG.** Report what panels **A / B / C** (or whatever divisions actually exist) show:
   exact axes, units, scope, and every legible label, tick and annotation. **Quote what you can read;
   mark anything illegible as illegible.**
2. **A concrete proposed caption and panel map**, written to match **what is rendered**, not what the
   response or R1 supposed.
3. **Check R1's proposed arithmetic and caption references against the actual figure.** Does the figure
   show **177 nt / 59 codons**, or **176**, or neither? Does it depict the frame rule, the phase-1
   donor set, the symmetric sweep (**0.439 vs 0.400**), the margin (**13**)? **Report any demonstrated
   mismatch precisely** — a mismatch is a finding, not a problem to smooth over.
4. If the figure cannot be read well enough to answer, say **exactly what is unreadable and why**.

## Bounds — binding

Input revision **56070821303d6856b7108c4c948a0c45d3d37c0b**. `claude-opus-5` **medium**, saved first-party subscription — **no paid
fallback, no overage, no credits, no GPU**. Deadline **2026-09-09T02:37:19Z**.

⭐ **You must ACTUALLY READ THE IMAGE** with the Read tool. ⛔ Do **not** infer content from the
filename, the generator source, the manuscript caption, or any prior lane's description. If a claim
rests on the generator rather than the pixels, **say which**.
⛔ **Do not regenerate any figure**, rerun any science, change any data, or edit the manuscript,
registry, tier, reference list, generator or any gate. ⛔ No new whole-paper review, no census, no
source recovery, no reopening of a closed contract, no network.
⛔ No write to any shared repository path — everything lives in your lane. **No git write**; read-only
git only. ⛔ No `scripts/preflight.sh`, no paid API.
⛔ **Leave unknowns UNKNOWN.** A precise "unreadable" or "missing input" result is a **successful
outcome**, not a failure. Never invent rendered content.
There is no wet lab: no EMC efficacy, safety, selectivity or clinical-readiness claim. Invent no fact
or measurement. If a request of yours is refused by content policy, stop that branch, record the
refusal verbatim, never route around it.
⛔ **DELETE NOTHING**, including your lane. Retain the image identity (path, bytes, sha256), your exact
inspection evidence and your output. Record `date -u`, `git rev-parse HEAD`,
`git status --porcelain` at start and end; confirm you changed nothing shared.

Stop at ~30 tool calls / ~30 minutes. Early with a supported result is success.

