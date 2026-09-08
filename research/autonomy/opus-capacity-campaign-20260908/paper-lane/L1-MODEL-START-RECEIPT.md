# L1 — served-model receipt, parsed from the child transcript

Verified by the parent 2026-09-08 ~10:37 UTC, after the L1 contract commits `5e1b8387` and its repair
`b16a077a`, from `…/subagents/agent-a050ed6a7259902e8.jsonl`. Start-time snapshot while running.

| item | observed |
|---|---|
| child | `a050ed6a7259902e8` |
| requested | `claude-opus-5`, **medium** effort |
| route | existing saved first-party subscription; no overage, no credits, no paid fallback |
| task | peer review Minor 16/17 — replace the salted-hash figure jitter with a deterministic offset |

Parsed from the transcript, not from the dispatch parameter or a self-report. At collection the parent
takes the tool-call count **and the full lifetime span** from the JSONL: self-reported counts have
undercounted **six** times running (E1 18/37, G1 13/21, H1 14/18, I1 23/33, J1 14/22, K1 18/30).

**Live counts:** newly executing research children **1** (L1); helpers **1** (the legacy Bash waiter —
computes nothing, not research). E1, F1, G1, H1, I1, J1, K1 are terminal and collected.

**Retention:** L1 works from `/tmp/claude-0/l1-lane/`, deletes nothing, may not copy any file into a
shared repository path, and must use the offline wheel cache rather than installing anything.
