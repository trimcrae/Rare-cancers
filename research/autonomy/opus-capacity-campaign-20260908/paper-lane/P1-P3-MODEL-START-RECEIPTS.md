# P1, P2, P3 — served-model receipts, parsed from the child transcripts

Verified by the parent 2026-09-08 ~11:16 UTC, after the contract commit `78cbbf7d`. Start-time
snapshots while running; final counts and **full lifetime spans** come from the JSONLs at collection.

| lane | child | requested | writes? | scope |
|---|---|---|---|---|
| **P1** | `aeef648a37893844e` | `claude-opus-5` medium | **writing owner** | `emc-mtap-prmt5-hypothesis.md` only — Appendix A `[2]`/`[3]` attribution |
| **P2** | `ad4d830b7eb83d367` | `claude-opus-5` medium | **read-only** | ATR collaborator package: response-vs-committed divergence test, report only |
| **P3** | `ad4934c3bf967bca7` | `claude-opus-5` medium | **read-only** | neoantigen: do the 26 binders rest on the seams the 2026-08-06 audit invalidated? |

All three parsed from their transcripts, not from dispatch parameters or self-reports. Route:
existing first-party saved subscription — **no paid fallback, no overage, no credits, no GPU**.

**One owner per writing scope:** only P1 may write, and only to one manuscript. P2 and P3 write
nothing at all, so they cannot collide with P1 or with each other. **Parent integration alone owns
shared files** — `submission-metrics.json` and every other shared path.

## Actual concurrency, reported honestly

**3 research children executing. 1 helper** (the legacy Bash waiter — computes nothing, not research).
Completed-and-collected lanes (E1, F1, G1, H1, I1, J1, K1, L1, M1, N1, O1) are **not** counted as
running.

**Why 3 and not 20 — the concrete limiting dependency is ready work, not slots.** No desktop or
Codex-slot cap applies here. What bounds the count is that each additional worker needs a *distinct,
already-evidenced, executable* issue, and the campaign has now closed most of them:

- **surface-targets** — set down; item 44 blocked with a tested route, the abstract residue does not
  fit at 200/200, DFSP recomputation out of scope.
- **repurposing** — set down at the canonical-draft blocker; the remaining item is a tier regrade that
  must not be applied unilaterally.
- **mtap-prmt5** — P1 has its one ready item; publisher confirmation and cross-version identity stay
  blocked.
- **ATR package, neoantigen** — being *assessed* right now by P2 and P3 precisely to find whether they
  contain ready work. Their reports are what would justify further writing lanes.
- **fusion-output / W25, NR4A Perspective, P6 successor, ASO / RNA / frozen assets** — held, and not
  to be counted as available.

⭐ **Manufacturing more workers would mean inventing eligibility or duplicating closed reviews**, which
the standing instruction forbids. The honest number is 3, and P2/P3 exist to raise it on evidence.
