---
id: DOC-VIEW-ST-OCCUPANCY
title: ST-OCCUPANCY — Direct small-molecule engagement of the NR4A3 ligand-binding domain
level: L1
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Can a molecule that merely OCCUPIES the NR4A3 pocket — reversibly or covalently — change the fusion's behaviour, without recruiting anything?
scope: Level 1. 3 routes.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# ST-OCCUPANCY — Direct small-molecule engagement of the NR4A3 ligand-binding domain

**Thesis.** If the ligand-binding domain is a functional handle in the chimera, then occupying it is enough, and the entire ternary-assembly problem disappears. The bet is on the pocket being actionable rather than merely bindable.

**Portfolio role:** `hedge` · **state:** ○ blocked · scoped · confidence low

> The hedge against the proximity family: it retires the ternary-geometry blocker outright. What it cannot retire is the requirement that something binds the pocket, and it adds one the proximity family does not have — that occupancy alone does something.

## What this family may NOT be used to claim

- Whether the ligand-binding domain is a functional handle in the fusion — whose other end is a strong independent activator — has never been tested by anyone.
- Nobody has stated how much paralogue selectivity this family would need, so 'the requirement is smaller here' is not a claim this repository can make.
- The covalent sub-form's negative result rests on an exposure criterion that fails its own positive control, so it is a rank and not a verdict.

## Routes

| route | state | maturity | readiness today | next action |
|---|---|---|---|---|
| **[RT-ASYMMETRIC](L2-rt-asymmetric.md)**<br/>Asymmetric selectivity — NR4A1-sparing mandatory, NR4A2-sparing best-effort | ✓ ready | computed | `reproducible_workflow` | Ensure the asymmetry is carried in every selectivity statement across the model rather than asserted once — a  |
| **[RT-COVALENT-PROBE](L2-rt-covalent-probe.md)**<br/>Covalent probe at C397 — as a REAGENT, not a drug | ✓ blocked | computed | `internal_note` | Build a reactivity-weighted accessibility criterion and calibrate it against the known covalent site, then re- |
| **[RT-MONOVALENT](L2-rt-monovalent.md)**<br/>Monovalent LBD pocket modulation — a molecule that only OCCUPIES the NR4A3 LBD | ○ blocked | scoped | `internal_note` | Write down the selectivity requirement this route would have to meet, with its basis. It is $0 and it is what  |
## What this family buys the portfolio — blockers it RETIRES

- **BLK-FUNCTIONAL-ACTIONABILITY** (`requires_wet_lab`) — Is the LBD a FUNCTIONAL handle in the chimera, whose other end is a strong independent activator?
- **BLK-INDUCED-COMPLEX** (`requires_better_structure_prediction`) — An induced ternary/bivalent complex is still required (a second protein must be placed)
- **BLK-PARALOGUE-DDG** (`requires_better_simulation_accuracy`) — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** (`requires_better_structure_prediction`) — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer

## Best next action

State the selectivity requirement this family would actually have to meet — it is currently unsized, and an unsized requirement cannot be shown to be met or missed.

*Cost:* $0

[← L0](L0-ecosystem.md)
