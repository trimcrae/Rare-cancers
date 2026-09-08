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



---

# Dated amendment, appended Tue Sep  8 11:40:04 UTC 2026 — U1's scope is EXPANDED in flight

**U1 (`af3a14e566b943e5e`) is live and has already inspected the figure** (panel crops present in its
lane). This amendment expands that **same child**; **no duplicate ATR reviewer is launched, U1 is not
restarted, and no image it has already read is re-inspected.**

## Why U1 and not a new lane

The scientific coordinator wants **one independent review of R1's concrete proposal** at `67050fcc`.
**U1 is already independent of R1's author** and already holds the figure evidence that review needs.

## Added deliverable — a focused DECISION MEMO on the proposed reconstruction

Not another 47-item inventory, not a history hunt, not a broad audit, not a publication clearance, and
**not an author self-review**.

1. **Verify R1's included substantive changes against the named committed inputs** —
   `emc_fet_frame_and_composition.py`, `emc-fet-frame-and-composition.json`,
   `research/modalities/tests/test_emc_fet_frame_and_composition.py`, and
   `emc-atr-collaborator-package-changelog.md`. For each: **supported**, **partly supported**, or
   **unsupported**, with the committed line or field cited. **Reuse the figure work already done.**
2. **Assess R1's seven proposed editorial/scientific decisions** (retitle; delete Appendix A; insert
   the figure and cut to six tables; reduce P1-P5 to three; move the scope blockquote; renumber into a
   Discussion; add §2.3/§4.1 and supplementary tables). Say for each whether R1's recommendation is
   **sound, premature, or unsupported**, and why. ⚠ Note that the predictions table is
   **preregistration-shaped** and this repository preserves preregistrations.
3. **Assess R1's eight unresolved items** — are they genuinely unresolvable from committed inputs, or
   did R1 miss an available input? Name any that is actually resolvable, with the input.
4. **Return: concrete unsupported claims, remaining dependencies, and a recommended COHERENT SCOPE for
   integration** — what could sensibly be applied together, and what must wait. A recommendation, not
   an application.

## Bounds — unchanged, and reinforced

⛔ Read **only existing inputs**. No source or network recovery, **no image or science regeneration**,
**no rerun of an unchanged gate**, no shared manuscript/artifact/registry edit, no held-scope
continuation. ⛔ **Change nothing shared; no git write.** Retain original inspection evidence, commands
and results.

**Stop at 35 TOTAL tool calls / 30 minutes for this child — counting the work already done — or
earlier on a supported finite result.** A partial but supported memo beats an exhausted budget.

**Shared integration remains the scientific coordinator's decision** after this independent review.
Nothing here creates a user/root approval queue.
