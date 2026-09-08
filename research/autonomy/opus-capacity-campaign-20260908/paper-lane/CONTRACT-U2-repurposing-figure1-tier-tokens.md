# U2 — repurposing Figure 1: does it render tier tokens?

## Why

R2's proposal left this **explicitly unknown**: whether `repurposing-fig1-design.png` renders the tier
token, recorded as *"unknown, not zero"* because R2 **did not open it**. The manuscript's caption at
line ~275 says the firewall admits *"only tier T3"*, so the figure is a **dependency of the proposed
T3 -> T2 regrade**.

⚠ **Path correction:** the file is at `research/manuscripts/figures/repurposing-fig1-design.png`, **not**
`research/figures/`. Bytes **177,415**, sha256 begins `f711ea7f2c4fd3e4c3d26cfacc61519d`.

R2's proposal and memo are in `paper-lane/R2-executed-artifacts/`; the blocker is
`BLOCKER-repurposing-canonical-draft-identity.md`.

## Deliver

1. **Read the image.** Report **every legible text label verbatim** — especially whether the tokens
   `T0`, `T1`, `T2`, `T3` appear, and whether any **T3-only admission rule** is rendered in the figure
   itself (for example a firewall box reading "admitting only tier T3").
2. **State exactly which visual text depends on the tier decision**, quoting it.
3. **For each of R2's two options** — **Option A**, keep four tiers with T3 defined but empty; **Option
   B**, collapse to three tiers — give the **minimal candidate change** to the figure's text. Describe
   it in words; ⛔ **do not modify the figure, and do not regenerate it.**
4. **Leave unknowns unknown.** If a label is illegible or ambiguous, say so rather than guessing. If
   the figure renders **no** tier token, that is a clean result that **removes** a dependency — say it
   plainly.

⛔ Do not change the figure, tier, registry, manuscript or reference list. **The final scientifically
justified choice stays with the coordinator.**

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

