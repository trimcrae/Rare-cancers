---
id: DOC-NEW-EVIDENCE-SESSION-PROMPTS
title: Hand-off prompts — one per route from the new-evidence memo
level: L4
kind: memo
status: live
purpose: "Carry the four startable routes from new-evidence-routes.md as copyable, self-contained session prompts, so each can be run in its own session without re-deriving the state."
scope: "Hand-off only. It states no finding, owns no number, and grades nothing. Every fact it quotes has its home in nr4a3-program-map.md, new-evidence-routes.md or the route's own generated view; where any of them differs from this file, they win."
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-24
last_verified: 2026-08-24
---

# Hand-off prompts

⛔ **This file is a convenience, not a register.** It restates nothing it owns — each prompt points at the
document that does. If a prompt and its target document disagree, **the document wins and the prompt is
stale**; fix it here rather than working from it.

Written for trimcrae, 2026-08-24, to start each route in its own session. Route rationale and the state
each one starts from live in [`new-evidence-routes.md`](./new-evidence-routes.md) §5.1–5.2.

---

## 1 · Junction search — make it specific

Branch `claude/emc-junction-specificity`. See [`new-evidence-routes.md`](./new-evidence-routes.md) §2, §5.1, §5.2.

The instrument is built and has run twice. The positive control (FLI1) fires at 4.6× the negative control
(GAPDH), so the 5'-depletion signature is real and detectable in the `srav3h` index. **But NR4A3's
candidate rate is only ~1.9× the negative control's, so its 1,642 candidates are dominated by the same
background — that number is not a finding and must not be quoted as one.** The job is specificity, not
more searching, and every tightening must be re-scored on all three genes in the same run.

## 2 · Methylation labels — find where the diagnoses live

Branch `claude/emc-methylation-labels`. See [`new-evidence-routes.md`](./new-evidence-routes.md) §3, §5.1, §5.2.

All 1,505 sample records of the pan-sarcoma deposit were read and **none names any disease** — they are
titled *"sarcoma classifier reference case N"*. That is a fact about the LABELS, not the samples. The
article fetch returned a 3,038-byte stub, so the supplementary tables were never reached. The EBI mirror
answered with a real record and was truncated only by this module's own byte cap; an ArrayExpress SDRF
exists to carry per-sample characteristics. Try that, then PMC.

## 3 · The diagnostic code — measure the contamination

Branch `claude/emc-icdo-contamination`. See [`L2-rt-diagnostic-pathway.md`](../../../systems/views/L2-rt-diagnostic-pathway.md)
and `emc-care-delivery-evidence.json` → `icd_o_9231_3`.

⭐ **The contradiction is already ANSWERED at $0 and quoted from both papers' own Methods.** What is
missing is its SIZE, and the route's readiness note says why that matters: *a paper that can state the
problem but not its magnitude is weaker than one that can.* The full prompt is §3 below.

## 4 · Retrodiction — test the portfolio against the treatment record

Branch `claude/emc-retrodiction`. Not yet written up; see [`new-evidence-routes.md`](./new-evidence-routes.md)
for why it ranks first among the second tier. `"held out"` appears throughout this repository and **always
inside one instrument** — never at the level of whether the programme's own view of this disease agrees
with what has actually been given to patients and published.
