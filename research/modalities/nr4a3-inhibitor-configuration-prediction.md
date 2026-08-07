---
id: DOC-NR4A3-INHIBITOR-CONFIGURATION-PREDICTION
title: Q10 — the inhibitor configuration at C397, and whether the TCIP interface-floor ablation's prediction holds
level: L4
kind: memo
status: generated
generator: research/modalities/inhibitor_configuration_prediction.py
canonical_for: []
purpose: "Test the interface-floor ablation's prediction against the committed monovalent reach run on both axes it could be read on, and report which one it is about."
scope: Geometry only, over committed artifacts. No new compute. No reactivity, potency, selectivity, efficacy or safety statement.
audience: [maintainers, autonomous research agents]
date: 2026-08-07
last_verified: unverified
---

# Q10 — the TCIP interface-floor ablation predicts the inhibitor configuration gains admissible space. Does it hold, and does it rescue the route?

**Status.** $0 CPU, pure stdlib, NO NEW GEOMETRY. Every atom count is read from the committed artifacts and both configurations go through ONE reader, so a difference cannot be an artefact of two different readers. Nothing here is a claim about reactivity, potency, proteome-wide selectivity, efficacy, safety, a therapeutic window or clinical readiness.

## ⭑ The free observation nobody had taken

- **The board says:** roadmap §10.1a Q10 — 'the enumeration has never been run in that configuration'; path-family-synthesis.md §3 row 10 — 'unchanged and still under-run'.
- **What is committed:** nr4a3-monovalent-reach.json + nr4a3_monovalent_reach.py, written 2026-08-06 at 7:12 AM ET.
- **The committed answer:** `WORSE`

> Removing the E3 arm does NOT rescue the categorical axis, and on the conservative convention it destroys it outright. Corridor: of the 37 bivalent cells that had an open family-wide window at C397, **0** retain one when the E3 arm is removed, and **0** gain one — a complete, one-directional collapse. Through-space (an upper bound on reachability, which scores buried sulfurs as reachable): 24 of 48 retained and 8 gained, so the permissive rule reads MIXED. The intuition that one fewer terminus is 'a strictly smaller search problem' is true about REACH and irrelevant to SELECTIVITY: dropping the |p-b| term shortens every competitor's chain as well as the target's, and it removes the geometric constraint that was ORDERING them.

the free observation was available the whole time. A row that says 'never run' about an artifact sitting on the same branch is an unanswered question wearing the costume of a status.

## The prediction

| `min_contact_residues` | single/multi acceptance ratio |
|---|---|
| 12 (committed) | 0.896 |
| 6 | 1.121 |
| 0 | 1.254 |

an inhibitor has neither an E3 arm nor an induced interface, so it sits at floor 0 with no second body — the configuration the ablation says gains orientation space.

⚠ the ablation measures a SECOND BODY's orientation acceptance; the reach enumeration measures a backbone-atom window over cysteines. Testing it on one axis only would conflate 'the prediction held' with 'the route is rescued'.

## ★ Axis A — admissible space (the ablation's own axis)

| refusal | cells | retired by removing the E3 arm? |
|---|---|---|
| E3 anchor is buried | 5 / 200 | **yes** |
| warhead anchor has no room | 31 / 200 | ⛔ **no** |

⛔ a monovalent molecule still needs room at the warhead, so the warhead-anchor refusal survives the configuration change untouched. Counting both as 'gained' would overstate the prediction by the larger term.

| convention | closed → open | open → closed | net |
|---|---|---|---|
| corridor | 0 | 37 | -37 |
| through_space | 8 | 24 | -16 |

**Prediction holds on this axis: True**

## ★ Axis B — the selectivity window (the quantity `Q10` was closed on)

| convention | config | cells | open windows | median margin (atoms) | median rank of C397 | target first |
|---|---|---|---|---|---|---|
| corridor | bivalent | 60 | 37 | 3 | 1 | 47 |
| corridor | monovalent | 30 | 0 | -2 | 3 | 2 |
| through_space | bivalent | 60 | 48 | 3 | 1 | 60 |
| through_space | monovalent | 30 | 11 | 0 | 1 | 18 |

## ★ The discriminator test

a pure COST preserves margin and rank; a DISCRIMINATOR degrades both. This is the observation that separates them.

THE E3 TERM WAS A DISCRIMINATOR, NOT ONLY A COST — margin and rank both degrade on corridor. The interface-floor ablation's mechanism (a filter that, once removed, admits more) does NOT transfer to this axis, because what is removed here is not a filter but the term that was ORDERING the cysteines.

## ★ Verdict

**THE PREDICTION HOLDS ON THE AXIS IT IS ABOUT AND DOES NOT RESCUE THE ROUTE. Axis A (admissible space, the ablation's own axis): removing the E3 arm retires the E3-anchor-buried refusal — 5 of 200 ensemble cells — and 8 of 60 paired cells gain a window under the permissive convention. Axis B (the selectivity window, the quantity Q10 was closed on): the conservative convention goes from 37 of 60 open cells to 0 of 30, a complete one-directional collapse, and the committed monovalent verdict is 'WORSE'. ⛔ THE TWO ARE NOT IN CONFLICT AND THE ABLATION NEVER PREDICTED THE SECOND.**

**Why both are true.** an interface FLOOR and the |p-b| LENGTH TERM do different work. The floor is a FILTER on a second body's orientations — remove it and more orientations qualify, which is exactly what the ablation measured. The |p-b| term is a per-cysteine DISCRIMINATOR inside the length arithmetic: it penalises each cysteine by a different amount, so removing it removes the ordering along with the cost. THE E3 TERM WAS A DISCRIMINATOR, NOT ONLY A COST — margin and rank both degrade on corridor. The interface-floor ablation's mechanism (a filter that, once removed, admits more) does NOT transfer to this axis, because what is removed here is not a filter but the term that was ORDERING the cysteines.

**What `Q10` now holds.** the 30-of-30 chemoselectivity closure SURVIVES the removal of the E3 arm — which is the falsifier §10.1a wrote for this row, resolved in the direction that closes it. The counter-result was never an artefact of the E3 constraint, and the mechanism that looked like it might reopen the row acts on a different quantity.

## ★ What picking this configuration costs

- **Retires:** R9 — OUR ternary is correctly assembled; R10 — a ternary forms; R12 — compatible with DEGRADATION (productive unique-lysine geometry)
- **Loses:** the degradation mechanism — the program's stated reason for choosing degradation over inhibition. An inhibitor must carry occupancy-driven pharmacology instead, which this repository has measured nothing about.
- **Gains:** one fewer terminus to satisfy, and the E3-anchor admissibility refusal is retired.
- ⛔ these are a route's TERMS, not a recommendation. §10.1b records this as an ⚖ ALTERNATIVE and the choice is trimcrae's.

## ⛔ What this does not license

- any claim that a monovalent covalent probe at C397 is selective — the window question is answered against it on the conservative convention
- any claim that a NON-covalent monovalent pocket modulator is refuted. It has no cysteine to reach and is untouched by this measurement — the monovalent artifact says so itself.
- reactivity, thiol pKa, adduct stability, potency, proteome-wide selectivity, efficacy, safety, a therapeutic window or clinical readiness
- a pose-specific or vector-specific reading of any number here
