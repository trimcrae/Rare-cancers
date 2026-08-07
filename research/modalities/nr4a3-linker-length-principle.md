---
id: DOC-NR4A3-LINKER-LENGTH-PRINCIPLE
title: Q4 / S6 — the linker-length design principle, stated at its categorical gate and only there
level: L4
kind: memo
status: generated
generator: research/modalities/linker_length_principle.py
canonical_for: []
purpose: "State the measured length dependence as a design principle in a form whose gate travels with it, and refuse to emit it above the gate where it would inherit V17's false negative."
scope: Geometry only, over committed enumerations. No reactivity, potency, selectivity, efficacy or safety statement. Length sets a geometric discrimination; discrimination is not selectivity.
audience: [maintainers, autonomous research agents]
date: 2026-08-07
last_verified: unverified
---

# Q4 / S6 — the linker-length design principle, STATED AT THE 12-ATOM GATE AND ONLY THERE

**Status.** A STATEMENT OVER COMMITTED DATA. $0 CPU, pure stdlib, no new compute — every figure is read from nr4a-paralogue-dynamics.json. Nothing here is a claim about reactivity, potency, proteome-wide selectivity, efficacy, safety, a therapeutic window or clinical readiness. Length sets a geometric discrimination; discrimination is not selectivity.

**What was missing.** not the data — S6's own cheapest decisive test reads '$0, already computed and committed'. What was missing was the STATEMENT, in a form whose gate travels with it so tightly that quoting it outside the gate is not possible by accident.

## ★ The principle — at the 12-atom gate

> LINKER-LENGTH DESIGN PRINCIPLE, AT THE 12-BACKBONE-ATOM CATEGORICAL GATE AND ONLY THERE. Prefer the shortest backbone that reaches C397. Over 3 independently-computed scopes and 73,867 enumerated placements, P(a paralogue cysteine is also reached | an NR4A3-unique one is) is 0.000–0.003 at 12 backbone atoms, and it climbs monotonically with length (12 atoms 0.000–0.003 · 14 atoms 0.009–0.032 · 16 atoms 0.054–0.133 · 20 atoms 0.263–0.383). Length is therefore not merely a tractability axis: it is the variable that sets the geometric discrimination. ⛔ THE GATE IS PART OF THE PRINCIPLE, NOT A CAVEAT ON IT. At 12 atoms the result holds ON REACH ALONE — the reach-only band (0.000–0.003) and the exposure-filtered band (0.000–0.000) agree, so nothing here rests on V17. Above the gate they diverge and the entire length dependence moves into cysteines V17 calls buried, so the 16- and 20-atom columns are NOT a selectivity statement and this principle may not be quoted at them. ⛔ WHAT IT LICENSES: a design preference and a publishable negative (C420 and C559 are not usable at routine length). WHAT IT DOES NOT: any claim about the chemoselectivity WINDOW being NR4A3-limited — the window is closed by a PARALOGUE cysteine in 30 of 30 graded cells — and no claim about reactivity, potency, proteome-wide selectivity, efficacy, safety, a therapeutic window or clinical readiness. Discrimination is geometry; it is not selectivity.

## ⛔ Refused above the gate

| requested atoms | status | reason |
|---|---|---|
| 14 | `REFUSED` | ABOVE THE GATE. At 14 backbone atoms the reach-only band is 0.009–0.032 while the exposure-filtered band is 0.000–0.000 — 0.8% of the reach signal survives the exposure filter, so the length dependence at this length lives in cysteines V17 calls buried. V17's false negative is that it calls the family's one literature-anchored covalent site (NR4A1 Cys551 / celastrol) buried, so a selectivity statement here inherits a known false negative. |
| 16 | `REFUSED` | ABOVE THE GATE. At 16 backbone atoms the reach-only band is 0.054–0.133 while the exposure-filtered band is 0.000–0.002 — 1.3% of the reach signal survives the exposure filter, so the length dependence at this length lives in cysteines V17 calls buried. V17's false negative is that it calls the family's one literature-anchored covalent site (NR4A1 Cys551 / celastrol) buried, so a selectivity statement here inherits a known false negative. |
| 20 | `REFUSED` | ABOVE THE GATE. At 20 backbone atoms the reach-only band is 0.263–0.383 while the exposure-filtered band is 0.000–0.002 — 0.5% of the reach signal survives the exposure filter, so the length dependence at this length lives in cysteines V17 calls buried. V17's false negative is that it calls the family's one literature-anchored covalent site (NR4A1 Cys551 / celastrol) buried, so a selectivity statement here inherits a known false negative. |

## The length dependence

| backbone atoms | reach-only band | exposure-filtered band | fraction of the reach signal surviving the filter |
|---|---|---|---|
| **12 (gate)** | 0.000–0.003 | 0.000–0.000 | 0.000 |
| 14 | 0.009–0.032 | 0.000–0.000 | 0.008 |
| 16 | 0.054–0.133 | 0.000–0.002 | 0.013 |
| 20 | 0.263–0.383 | 0.000–0.002 | 0.005 |

### ⛔ Correction to `S6`'s phrasing

S6 writes 'P(categorical | exposed) is 1.000 at EVERY length'. MEASURED, per scope, over every length: metad_biased 0.998–1.000; static_opened_model 1.000–1.000; unbiased_release 1.000–1.000. The scopes where it is exactly 1.0 are static_opened_model, unbiased_release; where it is not, metad_biased (min 0.99805). The correction does not weaken the argument — a ruler that low still sees almost nothing — but a principle whose whole point is that a number must be stated at its gate may not itself round a number past where it holds.

## ★ Composition with `Q3`

the anti-handle LIABILITY (Q3) and the categorical length dependence (Q4) are both monotone in the SAME variable and both minimised at short length. They are independent measurements — one is reciprocal-uniqueness geometry, the other is conditional reach probability — so their agreement is evidence, not tautology. ⛔ And no committed construct sits at the gate.

At the 12-atom gate: **7 of 120** cells admit a reciprocal anti-handle and **35 of 120** reach C397. The shortest committed construct is **14** atoms.

⛔ MEASURED, AND IT REFINES THE LINE ABOVE. Q3's DESIGN-TARGET column — cells reaching C397 while admitting no anti-handle — is not monotone and peaks ABOVE the gate, because engagement and liability grow at different rates. ⛔ That does not license the longer length: above the gate the categorical statement inherits V17's false negative and principle() refuses to emit it, so those extra cells are reach without a statable discrimination. The gate is set by what can be SAID, not by what can be reached — and a composition claim that hid this disagreement would be the drift Q4 exists to stop.

## ⛔ What this does not license

- the 16- and 20-atom columns as a SELECTIVITY statement — that is the whole point of the gate
- any claim that the chemoselectivity WINDOW is NR4A3-limited. It is closed by a PARALOGUE cysteine in 30 of 30 graded cells, and in 24 of 30 through-space cells by NR4A1 C505, a position NR4A3 SHARES (C536)
- reactivity, thiol pKa, adduct stability, potency, proteome-wide selectivity, efficacy, safety, a therapeutic window or clinical readiness
- a pose-specific or vector-specific reading of the same numbers
