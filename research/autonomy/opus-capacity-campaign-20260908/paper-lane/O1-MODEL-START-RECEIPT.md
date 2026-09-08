# O1 — served-model receipt, parsed from the child transcript

Verified by the parent 2026-09-08 ~11:04 UTC, after the O1 contract commit `d0078258`, from
`…/subagents/agent-a24f906c6b0bf30f6.jsonl`. Start-time snapshot while running.

| item | observed |
|---|---|
| child | `a24f906c6b0bf30f6` |
| requested | `claude-opus-5`, **medium** effort |
| route | existing first-party saved subscription; no paid fallback, no overage, no credits |
| paper | `repurposing-hypotheses.md` — correct a claim the paper's own review calls false in fact |

**Scope of the claim being corrected:** the manuscript says imatinib is "eligible to graduate into the
cited clinical registry, pending clinician review"; `research/data/emc-clinical-registry.json` already
lists it. The child corrects the **manuscript sentence to match the registry**, never the reverse: the
registry and every patient-facing artifact are **read-only** for this task, no tier or admission rule
may change, and **no citation or reference may be added** — a reference-count mismatch elsewhere is
explicitly not licence to add sources.

Parsed from the transcript, not from the dispatch parameter or a self-report. At collection the parent
takes the tool-call count **and full lifetime span** from the JSONL.

**Live counts:** newly executing research children **1** (O1); helpers **1** (the legacy Bash waiter —
computes nothing, not research). E1, F1, G1, H1, I1, J1, K1, L1, M1, N1 are terminal and collected.
