# H1 — served-model receipt, parsed from the child transcript

Verified by the parent 2026-09-08 09:18 UTC from `…/subagents/agent-a44b7543b77ae627f.jsonl` while
the child was running — a start-time snapshot, not a final count.

| item | observed |
|---|---|
| child | `a44b7543b77ae627f` |
| dispatched | 2026-09-08 ~09:17 UTC |
| model strings | all `claude-opus-5` (count below, as read) |
| route | existing first-party saved subscription; no overage, no credits, no paid fallback |

Parsed from the transcript, not from the dispatch parameter or any self-report. ⚠ Self-reported
tool-call counts have undercounted the transcript twice in this campaign (E1: 18 reported / 37 actual;
G1: 13 / 21), so the parent's collection will take the count from the JSONL.

**Live counts:** research children **1** (H1); helpers **1** (the legacy Bash waiter — computes
nothing, not research).

**Retention:** H1 was instructed to delete nothing, including its own scratch, per CLAUDE.md §8.
