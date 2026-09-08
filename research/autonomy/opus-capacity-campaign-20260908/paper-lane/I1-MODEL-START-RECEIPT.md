# I1 — served-model receipt, parsed from the child transcript

Verified by the parent at **2026-09-08 09:27:49 UTC**, after the contract commit `8622818a`, from
`…/subagents/agent-a4d3dbe19da70eef9.jsonl`. Start-time snapshot while running, not a final count.

| item | observed |
|---|---|
| child | `a4d3dbe19da70eef9` |
| requested | `claude-opus-5`, **medium** effort |
| first transcript timestamp | **2026-09-08T09:27:44.484Z** |
| model strings in transcript | **2 × `claude-opus-5`, 0 others** |
| route | existing saved first-party subscription; no overage, no credits, no paid fallback |

Parsed from the transcript, **not** from the dispatch parameter or a self-report. Final counts will be
taken from the JSONL at collection — self-reported tool-call counts have undercounted three times
running (E1 18/37, G1 13/21, H1 14/18).

**Live counts:** research children **1** (I1, code lane); helpers **1** (legacy Bash waiter — computes
nothing, not research). H1 is terminal and collected at `d3e5e04c`.

**Retention:** I1 is instructed to delete nothing, including its own `/tmp/claude-0/i1-lane/`, and to
make **no edit to the shared tree** so no manuscript worker's linter baseline moves.
