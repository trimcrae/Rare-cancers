# U2 — collection: the tier dependency is REAL, and my own brief was the mismatch

⛔ **Nothing applied.** The figure, manuscript, tier, registry and reference list are untouched.

| item | measured |
|---|---|
| child | `affb0de2019218802` |
| model strings | **`claude-opus-5` only** |
| tool pairs | **9** (self-reported 7) |
| image read | `research/manuscripts/figures/repurposing-fig1-design.png`, **177,415 B**, sha256 `f711ea7f2c4fd3e4c3d26cfacc61519db5018fb40dcf87c208e1b45ac3ca2075`, 2786x1526 RGBA — **byte-identical at end** |
| shared writes | **none** |

## The answer R2 could not give: tier tokens ARE rendered

R2 recorded this as *"unknown, not zero"*. It is now **known**: **`T3` appears twice** — as the
endpoint of `14 existing drugs, tiers T0–T3`, and standalone on the edge label leaving the Firewall.
**`T1` and `T2` appear nowhere.** So the proposed regrade **does** have a figure dependency; it is not
removed.

**Exactly two strings depend on the tier decision:**
(a) `14 existing drugs, tiers T0–T3` · (b) `T3 plus clinician review only`

**Minimal candidate changes, proposal only:** under **Option A** (four tiers, T3 defined but empty) no
change is strictly required — the range stays true and the edge states an admission *rule*, not a
population — with an optional parenthetical if emptiness must be visible. Under **Option B** (collapse
to three) **two label edits and no structural change**: the endpoint becomes `T0–T2` and the edge token
becomes `T2`. No box, arrow, layout or line-wrap change either way.

## ⭐ The flagged mismatch was mine, and it is resolved

U2 observed that the figure's rule reads **"T3 plus clinician review only"** — a **two-condition** rule
— where my contract quoted the caption as *"only tier T3"*, and it correctly refused to call that a
caption diff because **it had not opened the caption**.

**I checked the caption myself.** It reads: *"A firewall governs what may reach patient-facing
material, admitting only tier T3 **after clinician review**."* **The caption and the figure agree** —
both are two-condition. **The mismatch was my contract's partial quotation**, not a defect in the
paper. Withdrawn.

## Discipline worth recording

Every content claim rests on **pixels**; only dimensions and bit depth rest on the file's IHDR chunk.
U2 **did not open the generator, the manuscript, or any prior lane's description**, so nothing rests on
a generator — which is exactly what the contract demanded and what makes the finding independent.

**UNKNOWN, left unknown:** the dash codepoint in `T0–T3`; **whether T3 is in fact empty** (no registry
opened — unknown, not zero); which option is correct — **the coordinator's call**.

**Bounds held:** no figure modification or regeneration, no manuscript/tier/registry/reference/gate
edit, no git write, no network, nothing deleted.
