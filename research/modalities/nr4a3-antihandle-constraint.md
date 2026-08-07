---
id: DOC-NR4A3-ANTIHANDLE-CONSTRAINT
title: Q3 / S15 — the reciprocal anti-handle set as an executable design constraint
level: L4
kind: memo
status: generated
generator: research/modalities/antihandle_constraint.py
canonical_for: []
purpose: "Carry the reciprocal-unique paralogue cysteines as a design-time FILTER over the committed construct set, marginalised over poses, rather than reporting paralogue closure after the fact."
scope: Geometry only, over committed geometry. No binding, reactivity, degradation, selectivity, efficacy or safety statement. A filter removes liabilities; it adds no signal.
audience: [maintainers, autonomous research agents]
date: 2026-08-07
last_verified: unverified
---

# Q3 / S15 — the reciprocal anti-handle set carried as a DESIGN CONSTRAINT, as an executable predicate over the committed construct set

**Status.** GEOMETRY-ONLY DESIGN FILTER. $0 CPU, pure stdlib, no new compute of any kind — every atom count is read from the committed enumeration. Nothing here is a claim about binding, reactivity, degradation, proteome-wide selectivity, efficacy, safety, a therapeutic window or clinical readiness. A filter removes liabilities; it adds no signal and widens no margin.

**Question.** Does any committed construct's reach envelope admit a cysteine that a PARALOGUE has and NR4A3 does not — i.e. a residue at which the molecule acquires a paralogue liability no NR4A3-side analysis would ever look at?

## The constraint

`antihandle_constraint.admits_antihandle(competitor_atoms, n, antihandles) — reach is monotone in chain length, so a construct of n backbone atoms admits exactly the cysteines whose requirement is <= n.`

**NO COMMITTED CONSTRUCT SURVIVES THE ANTI-HANDLE CONSTRAINT UNDER THE UNION-OVER-POSES RULE — 54 of 54 rejected. The filter's failure mode IS its result: the enumeration has been optimising reach TO C397 while admitting the reciprocal-unique paralogue liability the constraint exists to refuse. ⚠ AND THE RULE TRAVELS WITH THE SENTENCE, BECAUSE IT IS LOAD-BEARING: 0 constructs are rejected in EVERY cell, so every rejection here rests on SOME committed cell rather than on all of them. That is the conservative reading R5 forces — the second pose method disagrees with the first, so the program cannot name which cell is real — and it is not the same claim as 'no geometry exists in which these constructs are clean'.**

| quantity | value |
|---|---|
| committed constructs screened | 54 |
| REJECTED (an anti-handle admitted in **any** cell) | 54 |
| rejected in **every** cell | 0 |
| surviving | 0 |

## The anti-handle set — derived, not typed

| residue | NR4A3 aligned | NR4A3 has a Cys here | band |
|---|---|---|---|
| NR4A1 C465 | C496 | True | shared_position |
| NR4A1 C475 | C506 | True | shared_position |
| NR4A1 C505 | C536 | True | shared_position |
| NR4A1 C534 | S565 | False | antihandle |
| NR4A1 C551 | T579 | False | antihandle |
| NR4A1 C566 | C594 | True | shared_position |
| NR4A2 C465 | C496 | True | shared_position |
| NR4A2 C475 | C506 | True | shared_position |
| NR4A2 C505 | C536 | True | shared_position |
| NR4A2 C534 | S565 | False | antihandle |
| NR4A2 C566 | C594 | True | shared_position |

### ⚠ The roadmap's prose set and the derived set **DISAGREE**

- prose (`§10.1a` `Q3`): `NR4A1 C505`, `NR4A1 C551`, `NR4A2 C534`
- derived: `NR4A1 C534`, `NR4A1 C551`, `NR4A2 C534`
- ⛔ `NR4A1 C505` is in the prose and is **not** reciprocal-unique — it is at a position NR4A3 also carries a cysteine at, so it is a shared-position off-target liability, not a reciprocal anti-handle
- ⛔ `NR4A1 C534` **is** reciprocal-unique and the prose omits it

## Pose marginalisation

**Rule.** REJECT iff an anti-handle is admitted in ANY committed cell (the UNION). The intersection would be the false-negative direction — it would certify a construct whose liability appears under five of six poses.

**Why.** R5 is unresolved and got worse on 2026-08-06: the second pose method DISAGREES with the first, so the program cannot name which cell is the real one.

no vector-specific or pose-specific statement is made anywhere in this artifact. The per-placement columns are DIAGNOSTIC and are labelled as such.

## ★ The constraint as a function of length

anti-handle admission is monotone in backbone length, and so is P(a paralogue cysteine is also reached | an NR4A3-unique one is) (Q4 / S6). Both LIABILITY quantities are therefore minimised at short length — which is the composition §10.1b's ⊕ COMPOSER set asserts and no artifact had measured.

| backbone atoms | cells admitting an anti-handle | cells admitting a shared-position Cys | cells reaching C397 | ★ reaching C397 **without** an anti-handle | |
|---|---|---|---|---|---|
| 8 | 0 / 120 | 0 / 120 | 2 / 120 | **2** / 120 |  |
| 10 | 2 / 120 | 3 / 120 | 9 / 120 | **7** / 120 |  |
| 11 | 4 / 120 | 4 / 120 | 28 / 120 | **24** / 120 |  |
| **12 | 7 / 120 | 7 / 120 | 35 / 120 | **28** / 120 | **← the categorical gate** |
| 13 | 9 / 120 | 7 / 120 | 39 / 120 | **30** / 120 |  |
| 14 | 14 / 120 | 11 / 120 | 51 / 120 | **37** / 120 |  |
| 16 | 33 / 120 | 28 / 120 | 71 / 120 | **38** / 120 |  |
| 18 | 48 / 120 | 48 / 120 | 74 / 120 | **26** / 120 |  |
| 20 | 66 / 120 | 65 / 120 | 82 / 120 | **16** / 120 |  |
| 24 | 79 / 120 | 85 / 120 | 93 / 120 | **14** / 120 |  |

⛔ **The design-target column peaks at 16 atoms (38 cells), NOT at the 12-atom gate.** MEASURED HERE, AND IT CORRECTS THE SENTENCE ABOVE RATHER THAN DECORATING IT. The two LIABILITY columns are monotone and agree; the DESIGN-TARGET column — cells reaching C397 while admitting no anti-handle — is NOT monotone and does NOT peak at the gate. It rises to a maximum above the gate and then collapses, because engagement and liability grow at different rates. ⛔ THIS DOES NOT LICENSE THE LONGER LENGTH: at any length above the gate the CATEGORICAL statement inherits V17's false negative (linker_length_principle.principle() refuses to emit it there), so the extra clean cells are reach without a statable discrimination. The honest reading is that the two constraints agree about liability and DISAGREE about where the most buildable cells are, and the gate is set by what can be SAID rather than by what can be reached.

⛔ **The shortest committed construct is 14 backbone atoms, above the 12-atom categorical gate** — so no committed construct sits where either constraint is at its minimum.

## Per construct — marginalised over poses

| construct | backbone atoms | cells admitting an anti-handle | witnesses | verdict |
|---|---|---|---|---|
| `vhlM4@ex_5amide_e6_none` | 18 | 48 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM4@ex_5amide_a2-a9_cyac_me` | 18 | 48 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM4@ex_5amide_a3-m3_cyac_me` | 18 | 48 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM4@ex_5triazole_e5_none` | 18 | 48 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM4@ex_5amide_a2-a9_acrylamide` | 18 | 48 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM4@ex_5amide_a2-a9_cyanoprop` | 18 | 48 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM3@ex_5amide_a9-a2_pyr3` | 18 | 48 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM3@ex_5amide_a9-a3_pyr3` | 19 | 60 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `crbnM0@ex_5amide_e4-a2_pyr3` | 19 | 60 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM3@ex_5amide_a9-a2_ph` | 18 | 48 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `crbnM0@ex_5amide_e4-a2_ph` | 19 | 60 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `crbnM0@ex_5amide_a11-a2_pyr3` | 20 | 66 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM3@ex_5amide_a2-a5_cyac_me` | 14 | 14 / 120 | NR4A1 C534, NR4A2 C534 | REJECT |
| `vhlM3@ex_5amide_a2-m2_cyac_me` | 14 | 14 / 120 | NR4A1 C534, NR4A2 C534 | REJECT |
| `vhlM3@ex_5triazole_a9_none` | 14 | 14 / 120 | NR4A1 C534, NR4A2 C534 | REJECT |
| `vhlM3@ex_5piperazine_a9_none` | 14 | 14 / 120 | NR4A1 C534, NR4A2 C534 | REJECT |
| `crbnM0@ex_5amide_a2-a5_cyac_me` | 14 | 14 / 120 | NR4A1 C534, NR4A2 C534 | REJECT |
| `crbnM0@ex_5amide_a2-m2_cyac_me` | 14 | 14 / 120 | NR4A1 C534, NR4A2 C534 | REJECT |
| `crbnM0@ex_5triazole_a9_none` | 14 | 14 / 120 | NR4A1 C534, NR4A2 C534 | REJECT |
| `crbnM0@ex_5piperazine_a9_none` | 14 | 14 / 120 | NR4A1 C534, NR4A2 C534 | REJECT |
| `vhlM3@ex_5amide_a2-a5_acrylamide` | 14 | 14 / 120 | NR4A1 C534, NR4A2 C534 | REJECT |
| `vhlM3@ex_5amide_a2-a5_cyanoprop` | 14 | 14 / 120 | NR4A1 C534, NR4A2 C534 | REJECT |
| `crbnM0@ex_5amide_a2-a5_acrylamide` | 14 | 14 / 120 | NR4A1 C534, NR4A2 C534 | REJECT |
| `crbnM0@ex_5amide_a2-a5_cyanoprop` | 14 | 14 / 120 | NR4A1 C534, NR4A2 C534 | REJECT |
| `vhlM2@ex_5amide_a2-a7_cyac_me` | 16 | 33 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM2@ex_5amide_a7-a2_cyac_me` | 16 | 33 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM2@ex_5triazole_a11_none` | 16 | 33 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM2@ex_5piperazine_a11_none` | 16 | 33 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM2@ex_5amide_a2-a7_acrylamide` | 16 | 33 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM2@ex_5amide_a2-a7_cyanoprop` | 16 | 33 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM14@ex_5amide_e6_none` | 18 | 48 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM14@ex_5amide_a2-a9_cyac_me` | 18 | 48 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM14@ex_5amide_a3-m3_cyac_me` | 18 | 48 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM14@ex_5triazole_e5_none` | 18 | 48 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM14@ex_5amide_a2-a9_acrylamide` | 18 | 48 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM14@ex_5amide_a2-a9_cyanoprop` | 18 | 48 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM4@rep_5triazole_e7_none` | 24 | 79 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM14@rep_5triazole_e7_none` | 24 | 79 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM2@rep_5amide_a2-a11_cyac_me` | 20 | 66 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM2@rep_5amide_a2-m4_cyac_me` | 20 | 66 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM2@rep_5amide_e7_none` | 21 | 72 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM2@rep_5triazole_e6_none` | 21 | 72 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM2@rep_5amide_a2-a11_acrylamide` | 20 | 66 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM2@rep_5amide_a2-a11_cyanoprop` | 20 | 66 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `crbnM0@rep_5triazole_e7_none` | 24 | 79 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM3@rep_5amide_a2-a7_cyac_me` | 16 | 33 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM3@rep_5amide_a2-a7_cyac_ph` | 16 | 33 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM3@rep_5amide_a2-a7_pyr3` | 16 | 33 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM3@rep_5amide_a7-a2_pyr3` | 16 | 33 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM3@rep_5triazole_a11_none` | 16 | 33 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM3@rep_5piperazine_a11_none` | 16 | 33 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM3@rep_5amide_a2-a7_acrylamide` | 16 | 33 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM3@rep_5amide_a2-a7_cyanoprop` | 16 | 33 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |
| `vhlM3@rep_5amide_a2-a7_ph` | 16 | 33 / 120 | NR4A1 C534, NR4A1 C551, NR4A2 C534 | REJECT |

## ⛔ What a pass does not license

- any selectivity, potency, reactivity or window claim — no energy is computed anywhere
- an increase in NR4A3 engagement. A filter removes liabilities; it adds no signal.
- a proteome-wide statement — an electrophile does not know it is meant to be selective, and this constraint is evaluated over three proteins
- a pose-specific or vector-specific design rule. Every verdict is marginalised over poses and may only be quoted that way.
