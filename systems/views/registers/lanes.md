---
id: DOC-VIEW-LANES
title: Lane register — executed work and how it ended
level: cross-cutting
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Every unit of work that has RUN, its state, how it ended, and the artifacts it owed — so that an artifact's absence is answerable by lookup rather than by reading prose.
scope: All lanes named anywhere in the repository. Enumerated, not curated.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# Lane register — executed work and how it ended

> **Role:** a ROUTE is a strategic option (*could we do X?*); a REQUIREMENT is *what must be TRUE*; a **LANE is *we ran X, and here is how it ended*.**

⛔ **WHY THIS EXISTS.** Executed work had no object in the model, so *"this lane closed"* lived only as a struck-through row in roadmap prose. Prose is not queryable — which is how, on 2026-08-05, an artifact belonging to a lane that had closed on 2026-07-30 was read as a gap to fill, and **88.5 minutes of CI went at it**. A state the model holds cannot be missed that way.

**17 lanes · 1 not yet complete.**

⚠ **A null result is `complete`, not a separate state.** The state answers exactly one question — *will this lane still produce what it owes?* — so a lane that ended with its gate FAILING is finished, with the verdict in its terminus. Collapsing those would make a settled negative look like an outstanding task, which is how dead work gets re-run.

| lane | state | how it ended / what it waits on | owed artifacts |
|---|---|---|---|
| **LANE-20**<br/>The restrained binary re-run | `held` | HELD ON PURPOSE — and ⚠ NOT behind `R`, which LANDED on 2026-07-30. Nothing is billing; it is off every host.<br/>⏸ **gate:** the pose diagnostic — gpu-ternary-fep-vast.yml task=triangle-converge | — |
| **LANE-1**<br/>The ligandable E3 recruiter panel — UniProt resolution, ligandability, | `complete` | Staged the widened recruiter set (VHL, CRBN, BIRC2, DCAF1, DCAF15, DCAF16, KEAP1, FEM1B, RNF114, MDM2) and downselected it. ⚠ Its own boundary is recorded and is the reason a separate adapter exists: it does NOT produce a receptor | — |
| **LANE-10**<br/>The reach-rule correction — the C397 reach figures are no longer lower | `complete`<br/>2026-07-26 | ✅ CORRECTED 2026-07-26. ⚠ Its own document still carries fifteen ⏳ markers for numbers to be filled from CI artifacts that never landed, so the correction is banked while parts of the write-up remain open. | — |
| **LANE-11**<br/>RUNG 4 Arm E — the genuine Arm E leg and the 2026-07-31 smoke fan-out  | `complete`<br/>2026-07-31 | Its rentals are ledgered in the realised-spend register, including the 17 rentals of the 2026-07-31 smoke fan-out. Off every host. | — |
| **LANE-13**<br/>Does the CATEGORICAL case survive paralogue dynamics? — matched NR4A1/ | `complete`<br/>2026-07-26 | ✅ DONE 2026-07-26 2:49 PM ET — YES. Legs, collect and analysis all landed. | ✓ `nr4a-paralogue-dynamics.json` |
| **LANE-14**<br/>Inverse linker design | `complete` | Recorded in the inverse-linker design document alongside LANE 10's corrected reach figures; no open legs and nothing on a host. | — |
| **LANE-16**<br/>RUNG 5a-KS — the ligand-side causal kill-switch | `complete`<br/>2026-08-02 | ✅ LANDED 2026-08-02 — all four legs (n = 2 seeds/arm). S = −0.1297 ± 0.3264 kcal/mol → the PREREGISTERED NULL. ⚠ Two further 5a-KS legs are PARKED (enabled: false) because a relaunch is a new purchase the price gate refuses — park | — |
| **LANE-17**<br/>Step 1 fan-out — 19 congeneric RBFE edges | `complete`<br/>2026-07-30 | ✅ COMPLETE — 18 of 18 computable edges landed; the 19th is not computable and is recorded as such. Off every host. The lane closed itself. | — |
| **LANE-18**<br/>The $/ns throughput bench sweep that re-anchored the ladder basis | `complete`<br/>2026-07-27 | Complete — it re-anchored the ladder basis, which is why the drift line is expressed as an absolute $/ns rather than a multiple of a correctable denominator (CLAUDE.md §1). | — |
| **LANE-19**<br/>valB_mini r1+r2 — the 4 replicate legs | `complete`<br/>2026-07-30 | ✅ CLOSED AT n=3 — and the gate FAILED on sign, so the decision is NO-GO. Off every host. The deliverable is the cycle SD, which is the number this lane existed to produce. | — |
| **LANE-2**<br/>Tier-2 12-pose run at corrected exact-kernel values, and the two measu | `complete`<br/>2026-07-25 | ★ TWO MEASUREMENTS LANDED HERE 2026-07-25 ($0), and BOTH correct assumptions the program was carrying. Later re-stated at corrected exact-kernel values after the LANE-10 reach correction. | — |
| **LANE-21**<br/>Step 1 fan-out autoscale — the rental/placement half of LANE 17 | `complete`<br/>2026-07-30 | Closed with LANE 17 on 2026-07-30 — the fan-out landed 18 of 18 computable edges and came off every host. | — |
| **LANE-22**<br/>The SMARCA2/4 endpoint-MD sensitivity control — co-folds plus the 22-l | `complete`<br/>2026-08-02 | Scored on its complete panel and returned NULL on an adequately-powered design — exact one-sided p = 0.7468, reference set 462, floor 0.00216, zero technical failures. That verdict is what retired the step-3 re-panel preregistrati | ✓ `selcal-verdict.json` |
| **LANE-3**<br/>Covalent celastrol-NR4A1 (C551) adduct + C551A control legs | `complete` | Recorded in the ordered plan with its as-run cost measured over 18 legs. Not on a host. | — |
| **LANE-5**<br/>The valB calibrator rescope — the P-series design | `complete`<br/>2026-07-25 | REFUTED for $0 by valb_pseries_chem.py: 6 of 10 pairs change formal charge and the 4 that do not perturb 58-80 heavy atoms against 2 for the running edge. The design is dead; the broader 'no such calibrator exists' statement is ex | ✓ `valb-pseries-chem.json` |
| **LANE-7**<br/>Registry-A / orientation basin audit — which crystal registry the Tier | `complete`<br/>2026-07-25 | ✅ RESOLVED 2026-07-25 — registry A (5T35) is CORRECT, and the Tier-2 result rests on it. A same-day claim about CRBN's null was RETRACTED in this lane rather than carried. | — |
| **LANE-9**<br/>The closure triangle — decides whether valB's miss is fixable at all | `complete`<br/>2026-07-30 | ✅ CLOSED. All four legs landed 5:11 PM ET Jul 30 and `R` is computed. Off every host. ⚠ Separately REFUTED as a DIAGNOSTIC for the wrong-sign miss (V5): it returns a clean R whether or not the program's actual problem exists. The  | ✓ `valb-triangle-reduction.json`<br/>✓ `valb-triangle-closure.json`<br/>✕ `valb-triangle-chem.json` |

## Artifacts a lane owed and never produced

⭐ **This table is the one that stops an absence being read as a gap.** A `complete` lane produces nothing further, so anything it never produced is a **withdrawn citation** — the document is what needs fixing, not the artifact. `check_artifacts` derives exactly that, which is why no human has to assert it.

| artifact | lane | lane state | ⇒ disposition |
|---|---|---|---|
| `valb-triangle-chem.json` | LANE-9 | `complete` | **withdrawn** |

[← L0](../L0-ecosystem.md)
