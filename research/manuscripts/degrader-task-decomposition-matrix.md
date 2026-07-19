# Task Decomposition Matrix — REWRITE Step 4 (Direct Mode, N=1)

> The single most important REWRITE diagnostic (plan §7 Step 4). It scores the founder's recurring
> tasks for agent-readiness and assigns a disposition, so agents absorb the high-coordination /
> low-judgment work and the founder's scarce judgment concentrates on the irreversible, high-stakes
> calls. This is the concrete fix for the **Tokenmaxxing "Latency"** finding (plan §2.4): cycle time
> to a shipped outcome is limited by the founder/decision layer, not by compute — so collapse the
> decision layer, don't buy more tools.

**Category:** J = judgment · P = pattern · C = coordination · Cr = creation.
**Agent-readiness (1–5):** 1 = human-only (irreversible / high-judgment) → 5 = fully agent-executable.
**Disposition:** AGENT (execute within envelope) · AGENT+REVIEW (agent drafts, human signs off) ·
HUMAN-GATE (human decides; agents prepare only).

| Task (recurring) | Category | Agent-ready | Disposition | Notes |
|---|---|---|---|---|
| Assemble the status board / daily digest | C | 5 | **AGENT** | Pure coordination; already partly automated (daily email). Wave-1 candidate. |
| Literature / data fetch + reproducibility packaging | C/P | 5 | **AGENT** | Route networked fetches via CI; deterministic. |
| Emit decision traces per gate | C | 5 | **AGENT** | `scripts/decision-trace.mjs`; agent fills, human owns the `by` field. |
| Run the GOVERN over-claim lint on any draft | P | 5 | **AGENT** | `scripts/govern-overclaim-lint.mjs`; a $0 automatic gate. |
| Draft grant / client-deliverable prose | Cr | 4 | **AGENT+REVIEW** | Agent drafts against the MTP + eval; human signs off (esp. any claim wording). |
| Draft manuscript / SI sections | Cr | 3 | **AGENT+REVIEW** | Agent drafts; the over-claim risk means mandatory human review at fold time. |
| Design a new benchmark / gate (what to run, what GO means) | J | 2 | **HUMAN-GATE** | Scientific judgment; agents cost/prepare, human decides. |
| Interpret a converged result → GO/NO-GO | J | 2 | **HUMAN-GATE** | The load-bearing scientific call; agent summarizes evidence, human decides. |
| Approve a GPU-spend rung (>$50) | J | 1 | **HUMAN-GATE** | Constraint-Layer rule; never agent-autonomous. |
| Post preprint / submit grant / send client deliverable | J | 1 | **HUMAN-GATE** | The three irreversible acts; GOVERN eval Layer 2 + sign-off. |
| Reword a flagged over-claim in a claim artifact | J | 2 | **HUMAN-GATE** | Agent proposes wording; human owns the final claim (Fiduciary Wedge). |
| Choose funder / commercial partner | J | 1 | **HUMAN-GATE** | Strategic + relationship; agents research, human decides. |
| Monitor spot jobs / re-dispatch on preemption | C | 5 | **AGENT** | Routine recovery; already automated via checkpoint/resume + pollers. |

## Reading of the matrix

- **~half the recurring load is disposition AGENT** (coordination + reproducibility + monitoring + the
  two new tools) — this is the congestion relief: it removes founder time from the *coordination* layer
  so it concentrates on the *decision* layer.
- **The HUMAN-GATE rows are almost all judgment or irreversibility** — exactly where a solo founder's
  attention should be scarce and protected. None of them should ever drift to autonomous execution
  (Constraint Layer).
- **The AGENT+REVIEW rows are the productivity frontier** — drafting under the MTP + GOVERN eval, with
  the falling human-override rate (plan §7 Step 5 cold-start) as the signal that the drafting twin is
  becoming real rather than "workflow automation with a chat box."

## Decision Handover Waves (Step 5, from this matrix)

1. **Wave 1 (do first, lowest risk):** status board, reproducibility packaging, decision-trace emission,
   the GOVERN lint — all disposition AGENT, all reversible. Parallel-run alongside the founder until the
   override rate falls, then deprecate the manual version.
2. **Wave 2:** grant / client-deliverable drafting under AGENT+REVIEW (the GOVERN eval is the guardrail).
3. **Wave 3 (highest judgment):** manuscript / selectivity-narrative drafting — agent draft, mandatory
   human review at fold time.

**Never handed over:** the GO/NO-GO scientific calls, the >$50 spend approvals, and the three outward
acts. These are the founder's permanent seat.
