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


---

# Timestamp correction, appended 2026-09-08 10:57 UTC — original text preserved

**The header's "~10:54 UTC" is wrong** and is corrected here from existing timestamp evidence, with
**no new check and no rerun**:

| event | actual, from the record |
|---|---|
| M1 contract commit `29e2516b` | 2026-09-08 ~10:41 UTC |
| parent's model verification (`grep` over the child JSONL) | **10:42:41 UTC** |
| child first transcript timestamp | **10:42:24.532Z** |
| child last transcript timestamp | **10:45:18.532Z** |

So **M1 had already finished before 10:54**, and the receipt's "~10:54" was my approximation written
while composing the file rather than a clock reading — the same error class as the E1 contract's
"08:18" and the H1 receipt's "09:17/09:18". **No contract term, bound, acceptance item or finding
changes**, and the collection record already used the transcript's real span.
