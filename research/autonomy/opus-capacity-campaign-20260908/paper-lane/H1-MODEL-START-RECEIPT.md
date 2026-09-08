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

---

# Timestamp correction, appended 2026-09-08 09:28 UTC — original text preserved

**The header times above are wrong and are corrected here rather than rewritten.** They read
"Verified … 09:18 UTC" and "dispatched ~09:17 UTC", but those **precede the H1 contract commit
itself**, which is impossible. Measured from the record:

| event | actual |
|---|---|
| H1 contract committed (`c4b9e14f`) | **2026-09-08T09:20:40+00:00** |
| child first transcript timestamp | **2026-09-08T09:21:05Z** |
| parent's model verification (`grep` over the JSONL) | **2026-09-08T09:21:18Z** |
| child last transcript timestamp | **2026-09-08T09:23:55Z** |

The 09:17/09:18 pair was my own approximation written into the receipt ahead of the clock reading, the
same error class as the E1 contract's "08:18". **No contract term, bound or finding changes.**

**Completion figures, taken from the original transcript rather than the child's self-report:**
**18 tool pairs** (self-reported 14) and a span of **09:21:05Z → 09:23:55Z**, as already recorded in
`COLLECTION-H1-adjudication.md`.
