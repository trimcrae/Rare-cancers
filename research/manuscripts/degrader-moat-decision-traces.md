# The Value Moat — decision traces + open-core reproducibility

> Rung B of [degrader-startup-plan-exo.md](./degrader-startup-plan-exo.md) §6.2, and the LEARN-layer
> of §5. The moat for a one-person computational shop is **not** the smartest model or the biggest GPU
> budget — both are rentable. It is the **validated pipeline + the accumulated, benchmarked decision
> history**: a competitor can rent the same GPUs but cannot clone the trace log, the benchmark library,
> or the reproducibility record. Per the skill: *turning inference cost into compounding corporate
> capital* is the asymmetric bet the industry's 5-layer stack has no equivalent for (the LEARN gap).

## 1. Decision traces (the why-layer)

**Mechanism:** every spend-gated rung / campaign decision emits one append-only structured record.
The repo's spend-gated ladder (STRATEGY.md) already produces exactly these — each GO/NO-GO is a
decision. `scripts/decision-trace.mjs` makes them a machine-readable, queryable log.

- **Substrate:** `research/degrader/decision-traces.jsonl` — append-only ("the log is the agent":
  the log is the deepest lock-in layer, beneath model and API).
- **Schema (`decision-trace/v1`):** `at, rung, decision (GO|NO-GO|HOLD|INDETERMINATE|SKIP|NOTE),
  inputs, result, gate, cost_usd, gpu_h, rationale, by (named human owner), final_call`.
- **Emit:** `node scripts/decision-trace.mjs --rung <id> --decision GO --result "…" --cost_usd N --gpu_h N --by trimcrae`
- **Read:** `node scripts/decision-trace.mjs --list`

**Why it compounds:** the trace log is simultaneously (a) the **reproducibility record** a reviewer or a
paying client can audit — "show me every decision, its cost, and the result it keyed on"; (b) the
**COGS ledger** (`cost_usd` / `gpu_h` per rung) that makes per-outcome pricing exact (plan §6.3); and
(c) the **portfolio memory** that lets the Domain Collapse Engine reuse calibrations across target
families instead of re-deriving them. Each campaign adds rows; the asset appreciates.

The log has been **backfilled with the program's real decisions to date** (step0, valA_mini,
step1_pilot, valB_mini) so it is a genuine record from day one, not a demo.

## 2. Open-core boundary (what is public vs. what is the moat)

The Steinberger flywheel — public reproducibility → reputation → inbound — only works if the *right*
things are public. The boundary:

| Layer | Disposition | Rationale |
|---|---|---|
| **Method + protocol** (OpenFE-based RBFE/ternary wiring, charge model, gates) | **Public** | Cite-able, incremental methods contribution; publishing it builds trust and reputation (Trust Loop). Not itself the moat. |
| **Public benchmarks** (valA TYK2, valB known-answer PROTAC results) | **Public** | Credibility; lets others verify the pipeline is sound. |
| **The paper + SI** | **Public** (on sign-off) | The credibility anchor / MTP artifact. |
| **The full decision-trace log across all targets** | **Private** | The compounding reproducibility + COGS history — the Value Moat. |
| **Per-client campaign inputs/results** | **Private, contract-bound** | Client IP; governed by the Six-Questions + codesigned liability boundary (plan §4-E). |
| **The target-agnostic pipeline as a service** | **Private / commercial** | The productized capability sold per-outcome (Rung D). |

**Rule:** publish the *method and its benchmarks* (reputation); keep the *accumulated decision history and
per-client work* (the compounding capital). Publishing the method does not give away the moat, because the
moat is the validated history, not the code.

## 3. Reproducibility packaging (the artifact)

To make Rung B real, the public artifact is a reproducible bundle:
- The pipeline code + pinned container / env (already in-repo: OpenFE env with `ambertools>=23`, am1bcc).
- The public-benchmark results with the exact protocol (valA_mini; valB_mini when run).
- The decision-trace schema + the *public* subset of traces (method-development decisions; not client work).
- A one-command reproduce path for each public benchmark edge.

This is the "productize the moat" deliverable — no new spend, pure packaging of what the spend-gated
ladder already produced.

## 4. Cognitive-captivity note

Keep the method, prompts, gates, and data **model-portable** (they live in the repo, not a vendor). The
foundation model is a swappable component — "own your loop; swap the model, keep the veteran." Re-check
periodically that no single vendor supplies compute + orchestration + the reasoning layer at once.
