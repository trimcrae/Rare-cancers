# Repurposing — the T2 revision is INTEGRATED into the shared manuscript

Applied by the parent 2026-09-08 ~12:04 UTC under the coordinator's explicit authorisation. **This is
manuscript reconciliation — not clinical-governance resolution and not publication acceptance.**

## What was applied

The exact authorised variant, hash-checked before use:
`V1-CAPTION-VARIANT/VARIANT-CANDIDATE-repurposing-hypotheses.md`, sha256
**`f18f3f268a903ed1970c9e090be06094c813bf6ba170df79fcf1605921d9a86d`** — confirmed identical to the
authorised value before copying.

Plus **one exact sentence correction** in Tranche 1. The replaced sentence read *"What remains open is
the clinical route set out above, together with that registry-conformance question; what is not open
is admission, because the entry already exists."* It now reads exactly:

> **The clinical route set out above and the conformance of the existing registry entry with the
> stated criterion remain unresolved.**

⭐ **Why that mattered:** the old clause asserted admission was settled *because an entry exists*.
**Presence of an entry does not settle whether its admission was valid** — the new sentence removes
that inference and leaves both questions open.

⚠ **A note on how I applied it:** the phrase was wrapped mid-sentence (`"What remains\nopen …"`), so my
first two literal replacements failed. I did **not** loosen the target to force a match — I used a
whitespace-tolerant pattern built from the exact authorised words, and printed the matched raw text
before writing.

## Preservation — verified, not assumed

| item | check |
|---|---|
| reference section | **byte-identical** to HEAD |
| citation tokens | **identical** across all references |
| tier definitions / four-tier scale | `T3 denotes …` present once, unchanged |
| T3 admission threshold + clinician review | present **verbatim** |
| §2.2 occupancy sentence | *"T3 is therefore defined but unoccupied"* — intact |
| alt text + visible caption | both carry *"no candidate in the assembled catalogue currently reaches T3"* |
| **diagram** | PNG **`f711ea7f…` untouched — no rerender**, as directed |
| registry / patient-facing bytes | **0 modified paths** |

`git status` showed **only** the manuscript modified.

## Checks — run ONCE, outputs retained

`lint_consistency` **0**, `submission_metrics` **0**, `lint_style` **0**, `lint_claims` **0**,
`lint_submission_residue` **0**, `lint_asymmetry` **0**. **`lint_citations` exits 1** — pre-existing
and repo-wide. **Not all gates are green.** Metrics: main **6,037 w**, abstract 238, 1 item, **22
refs**, within believed limits. Raw stdout/stderr and exit codes are retained in
`V1-CAPTION-VARIANT/integration-checks/`.

## Remaining paper-specific readiness blockers

1. **Registry conformance UNRESOLVED** — a clinical-governance decision for the responsible clinician
   or owner. The manuscript discloses the mismatch and does not resolve it.
2. **`lint_citations` red** — pre-existing, repo-wide, not this paper's.
3. **The 25-vs-22 reference-count divergence** with the 2026-08-10 response — untouched; **no
   reference was added, removed or renumbered.**

## ⛔ No longer open, and not to be listed as such

The **four-tier scale / T2 grade / committed-baseline** question is **settled by the coordinator's
decision and now reflected in the shared manuscript.** It is closed, and
`BLOCKER-repurposing-canonical-draft-identity.md` should be read with that in mind.

## Retained

R2's original proposal, V1's original candidate and memo, the caption variant, the
**INTEGRATION-BEFORE / INTEGRATION-AFTER pair**, the **final integration diff**, and the check outputs
— all preserved, nothing deleted.
