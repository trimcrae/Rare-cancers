# V1 — R2 follow-through: a NEW working revision on the committed baseline

Input revision **cc75a486b2ac13b86f69e5b20cefde1fa6fb7c96**. `claude-opus-5` **medium**, saved first-party subscription — no paid fallback,
overage, credits or GPU. Deadline **2026-09-09T02:37:19Z**.

## The coordinator's decision — this is the premise, not a question to reopen

After reviewing R2's memo, its Candidate A diff, the committed definitions and the firewall text:

1. **Baseline = the current committed manuscript**, and the product is an **explicitly NEW working
   revision**. ⛔ **Never a recovered original.**
2. **The T2 classification is ADOPTED**, on the assembled record's **case-level signal**.
3. **The FOUR-tier scale is RETAINED**, with **T3 defined but unoccupied**.
4. **No clinical efficacy finding follows.**

## Binding scope

### A · The firewall — correct the DESCRIPTION, never the rule

⭐ **KEEP the T3 admission threshold and the clinician-review requirement exactly as they are.**

What is unsupported is the claim that the firewall **is fully enforced**. Correct it to describe the
**stated/intended admission criterion**, then:

- **Explicitly disclose** that the existing **imatinib registry listing falls below that criterion**
  under the corrected **T2** grade; and
- **Mark registry conformance UNRESOLVED.**

⛔ **Do NOT invent** clinician approval, an authorised exception, a prospective-only policy, or any
resolution of clinical governance. ⛔ Do **not** change the clinical registry, any patient-facing
artifact, the evidence-tier definitions, or the admission threshold. **This corrects a description of
a mismatch; it does not relax the rule.**
⛔ **The registry mismatch must be visible in the manuscript body — NOT hidden inside an editorial
comment only.**

### B · The rationale — narrower than R2's

⛔ **Remove R2's overgeneralised "a single case is neither prospective nor substantial."** Replace with
the narrower, supported statement: **the assembled record supplies a case-level signal and does not
establish T3 evidence.**

⚠ **Neither R2 nor the coordinator has newly read the case report.** Say nothing that implies otherwise.
**Preserve the existing case citation, all counts, all stated uncertainty, and the ENTIRE reference
list** — ⛔ no new citation, no removal, no renumbering.

### C · Coverage — consistent across all of these

**§2.6**, **Figure 1 (alt text, caption, and the rendered text U2 identified)**, **§4**, **§5**.
**Preserve every scientific negative and limitation.**

## D · The figure — reuse U2's result, do NOT re-inspect

U2 is terminal and its result stands. The committed image is
`research/manuscripts/figures/repurposing-fig1-design.png`, **177,415 B**, sha256
`f711ea7f2c4fd3e4c3d26cfacc61519db5018fb40dcf87c208e1b45ac3ca2075`. It renders
**`14 existing drugs, tiers T0–T3`** and **`T3 plus clinician review only`**. The manuscript caption
already says *"after clinician review"*, so **there is no caption/figure mismatch** — that question is
settled; do not re-open it.

**Decide whether the labels actually need to change** under the adopted decision (four tiers retained,
T3 defined but unoccupied). ⭐ **If they do not, say so and change nothing** — that is the better
outcome.

**If and only if a label must change:** copy `research/manuscripts/figures/repurposing_design_figure.py`
into your lane, modify **the copy**, and regenerate **into your lane only**. ⛔ **No shared generator or
artifact edit. No new data analysis. No unchanged gate rerun.** Retain the original generator, your
exact changed copy, the before and after figures, every command with stdout/stderr/exit, and hashes.
**Inspect the resulting figure** and report any remaining visual or semantic dependency.
⛔ **Static relabelling validates nothing** — do not suggest it establishes clinical governance or
treatment evidence.

## Deliverables — all in `/tmp/claude-0/v1-lane/`

The **new proposed manuscript**, its **diff against the committed baseline**, a **memo**, any
**proposed figure and copied generator**, the **actual validation scope**, and the **exact remaining
dependencies**. **Retain R2's original proposal and this new candidate separately** — they are two
distinct artifacts.

## Bounds

⛔ **No write to any shared repository path**; everything in your lane. **No git write** — read-only git
only. ⛔ No broad review, new citation or source retrieval, census, history hunt, or publication step.
⛔ No network, no paid API, no GPU, no `scripts/preflight.sh`. There is no wet lab: **no EMC efficacy,
safety, selectivity or clinical-readiness claim.** Invent no fact, source, patient datum or
measurement. If a request of yours is refused by content policy, stop that branch, record the refusal
verbatim, never route around it. ⛔ **DELETE NOTHING.** Record `date -u`, `git rev-parse HEAD`,
`git status --porcelain` at start and end.

**Stop at the supported finite candidate plus its remaining-dependency list, or ~40 tool calls /
~40 minutes.** Shared integration remains the **scientific coordinator's** final decision.
