# M1 — served-model receipt, parsed from the child transcript

Verified by the parent 2026-09-08 ~10:54 UTC, after the M1 contract commit `29e2516b`, from
`…/subagents/agent-a5956710c3213c7aa.jsonl`. Start-time snapshot while running.

| item | observed |
|---|---|
| child | `a5956710c3213c7aa` |
| requested | `claude-opus-5`, **medium** effort |
| route | existing first-party saved subscription; **no paid fallback**, no overage, no credits |
| task | test whether the surfaceome membership table is obtainable for PMID 30373828 / PMC6243280 |

Parsed from the transcript, not from the dispatch parameter or a self-report. At collection the parent
takes the tool-call count **and full lifetime span** from the JSONL: self-reported counts have
undercounted **seven** times running (E1 18/37, G1 13/21, H1 14/18, I1 23/33, J1 14/22, K1 18/30,
L1 13/19).

**Live counts:** newly executing research children **1** (M1); helpers **1** (the legacy Bash waiter —
computes nothing, not research). E1, F1, G1, H1, I1, J1, K1, L1 are terminal and collected.

**Bound deliberately tight:** ~25 tool calls / ~25 minutes, because this is a narrow retrieval
question. **An early stop on missing or blocked access is a successful result**, and any negative must
be scoped to the tested route and identifier — never a global absence claim.
