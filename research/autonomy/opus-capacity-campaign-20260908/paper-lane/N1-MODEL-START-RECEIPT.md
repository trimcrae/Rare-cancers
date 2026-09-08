# N1 — served-model receipt, parsed from the child transcript

Verified by the parent 2026-09-08 ~10:57 UTC, after the N1 contract commit `d8fab1c8`, from
`…/subagents/agent-a585eff566c8eae0d.jsonl`. Start-time snapshot while running.

| item | observed |
|---|---|
| child | `a585eff566c8eae0d` |
| requested | `claude-opus-5`, **medium** effort |
| route | existing first-party saved subscription; no paid fallback, no overage, no credits |
| paper | `repurposing-hypotheses.md` — review items 24 and 26, submission hygiene only |

Parsed from the transcript, not from the dispatch parameter or a self-report. At collection the parent
takes the tool-call count **and full lifetime span** from the JSONL.

**Live counts:** newly executing research children **1** (N1); helpers **1** (the legacy Bash waiter —
computes nothing, not research). E1, F1, G1, H1, I1, J1, K1, L1, M1 are terminal and collected.


---

# Timestamp qualification, appended 2026-09-08 11:16 UTC — original text preserved

**The header's "~10:57 UTC" is inconsistent with the original events** and is corrected here from
those events alone — **no new check, no rerun, no audit**:

| event | actual, from the original record |
|---|---|
| parent's model verification (`grep` over the child JSONL) | **10:51:23 UTC** |
| child first transcript timestamp | **10:51:00.205Z** |
| child last transcript timestamp | **10:54:38.244Z** |

So the child had **started before** my stated receipt time and **finished before** it too. The
"~10:57" was my approximation written while composing the file rather than a clock reading — the same
error class already corrected for the E1 contract ("08:18"), the H1 receipt ("09:17/09:18") and the M1
receipt ("~10:54"). **No contract term, bound, acceptance item or finding changes**, and
`COLLECTION-N1-adjudication.md` already used the transcript's real span.
