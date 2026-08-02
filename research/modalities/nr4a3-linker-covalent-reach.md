# Is a linker-borne covalent NR4A3 handle geometrically available?

Can a linker anchored at the warhead attachment point present an electrophile at an NR4A3-unique cysteine SG while the E3 ligand still projects to solvent — across the experimental ensemble, without also reaching a cysteine the paralogues keep?

**Status:** GEOMETRY ONLY. No reactivity, potency, selectivity, developability or feasibility claim is made or implied. Geometry can refute a route; it cannot license one.

*Method:* Reach by `linker_design.branch_position_window` / `min_linker_atoms_exact` (the exact three-ball rule the committed library was built with), from anchors READ out of nr4a3-orientation-basins.json at the five basins that survived term-(b), both placements each. Two conventions reported side by side: `through_space` (the committed rule, an upper bound on reachability) and `corridor` (additionally requires a non-clashing branch position with a clash-free straight arm to the SG). Pure stdlib, $0 CPU.

## 0 · The premise, corrected before anything was measured

**does a linker-borne electrophile plus an E3 arm need a TWO-branch template?** — NO — it is a ONE-branch molecule and the committed library already contains 21 of them

`build_smiles(e3_key, wh_key, seg1_key, seg2_key=None, pendant=None)` builds `E3-NH-C(=O)-[SEG1]-C(=O)NH-CH(pendant)-C(=O)NH-[SEG2]-<warhead tail>`. the E3 sits at a chain TERMINUS, not on a branch, so the single `pendant` slot is free for the electrophile. `linker_branch_reach.py`'s two-branch requirement is for the electrophile AND the RUNG-5a causal wedge on one chain — a different molecule for a different experiment.

the architecture is not the blocker; reach, chemoselectivity and the paralogue control are. Those are what this module measures.

## 1 · The two reach conventions, and why both are reported

| convention | what it requires | what it is |
|---|---|---|
| `through_space` | the committed three-ball rule, unchanged | an **upper bound** on reachability — it will place a branch atom inside the protein |
| `corridor` | additionally: a non-clashing branch position with a clash-free straight arm to the SG | a **necessary** condition, still not sufficient — no backbone threading, no torsions, no solvent-connectivity test |

Clash cutoff sweep **[2.0, 2.6, 3.0, 3.4] Å**, primary **3.0 Å**. No repo constant answers 'how close may a linker backbone atom come to a protein heavy atom', so this is NOT imported and must not pretend to be. The whole sweep is computed and reported so no single value is load-bearing. The primary is deliberately permissive toward reach (0.4 A inside a C...C van der Waals contact of ~3.4 A), which makes the CONSERVED competitor easier to reach — i.e. it biases against the route under test, not for it.

## 2 · Reach across the experimental ensemble (PDB 8XTT)

20 of 20 deposited conformers analysed.

Cavity-bearing conformers (`site_druggability >= 0.53`, read from the committed benchmark): **[2, 6, 8]**. Conformers scored below that reference: [1, 3, 4, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19] — placing a warhead in them is a geometric operation and not a physical one.

⚠ Conformers **[20]** were never scored (the committed benchmark matched no site in them). They are **not** cavity-free, they are unmeasured, and they are excluded from both groups rather than counted as negatives.

**Does the E3 still project to solvent?** In 5 of 200 (conformer × placement) cells the E3 anchor is BURIED in that conformer's own backbone, so the placement does not exist there and the cell is excluded from the spread below rather than pooled into it (8xtt_m20). 31 cell(s) have a warhead anchor with no room at the same permissive threshold — reported, not excluded, for the reason in `placement_admissibility`.

Minimum linker backbone atoms to present a `dab_branch` pendant (8.75 Å arm) on each cysteine SG, min–median–max across the analysed conformers, at the **term-(a) exemplar** placements (the optimistic end of each basin):

| cysteine | unique | placement | through-space min–med–max | corridor min–med–max | conformers within 24 atoms (TS / corridor) |
|---|---|---|---|---|---|
| C397 | **yes** | crbn\|M0 | 11–11–12 | 11–12–16 | 19 / 19 |
| C397 | **yes** | vhl\|M14 | 7–9.0–10 | 9–11.0–16 | 20 / 20 |
| C397 | **yes** | vhl\|M2 | 9–9–9 | 9–9–13 | 19 / 19 |
| C397 | **yes** | vhl\|M3 | 11–11–11 | 11–11–14 | 19 / 19 |
| C397 | **yes** | vhl\|M4 | 14–14–15 | 14–14–21 | 19 / 19 |
| C420 | **yes** | crbn\|M0 | 49–50–53 | 61–62–64 | 0 / 0 |
| C420 | **yes** | vhl\|M14 | 40–41.0–44 | 53–54.0–55 | 0 / 0 |
| C420 | **yes** | vhl\|M2 | 48–49–52 | 60–61–62 | 0 / 0 |
| C420 | **yes** | vhl\|M3 | 49–50–53 | 61–62–64 | 0 / 0 |
| C420 | **yes** | vhl\|M4 | 48–49–52 | 60–61–63 | 0 / 0 |
| C496 | no | crbn\|M0 | 22–27–28 | 30–33–35 | 1 / 0 |
| C496 | no | vhl\|M14 | 14–19.0–20 | 22–25.0–27 | 20 / 4 |
| C496 | no | vhl\|M2 | 20–24–26 | 28–30–32 | 16 / 0 |
| C496 | no | vhl\|M3 | 21–25–27 | 29–32–34 | 1 / 0 |
| C496 | no | vhl\|M4 | 24–28–29 | 29–36–38 | 1 / 0 |
| C506 | no | crbn\|M0 | 41–42–44 | 50–52–54 | 0 / 0 |
| C506 | no | vhl\|M14 | 33–34.5–35 | 42–44.0–47 | 0 / 0 |
| C506 | no | vhl\|M2 | 40–40–42 | 48–50–53 | 0 / 0 |
| C506 | no | vhl\|M3 | 41–41–43 | 48–51–53 | 0 / 0 |
| C506 | no | vhl\|M4 | 40–41–42 | 48–50–53 | 0 / 0 |
| C536 | no | crbn\|M0 | 13–14–14 | 22–25–26 | 19 / 7 |
| C536 | no | vhl\|M14 | 10–11.0–11 | 19–23.0–24 | 20 / 20 |
| C536 | no | vhl\|M2 | 11–12–13 | 20–23–25 | 19 / 16 |
| C536 | no | vhl\|M3 | 12–12–13 | 19–22–24 | 19 / 19 |
| C536 | no | vhl\|M4 | 15–15–15 | 20–23–25 | 19 / 18 |
| C559 | **yes** | crbn\|M0 | 27–28–29 | 38–38–40 | 0 / 0 |
| C559 | **yes** | vhl\|M14 | 25–26.0–27 | 36–37.0–38 | 0 / 0 |
| C559 | **yes** | vhl\|M2 | 26–26–27 | 36–37–39 | 0 / 0 |
| C559 | **yes** | vhl\|M3 | 24–25–26 | 35–35–37 | 2 / 0 |
| C559 | **yes** | vhl\|M4 | 25–26–27 | 35–36–37 | 0 / 0 |
| C594 | no | crbn\|M0 | 35–36–40 | 46–49–50 | 0 / 0 |
| C594 | no | vhl\|M14 | 30–31.0–35 | 41–44.0–45 | 0 / 0 |
| C594 | no | vhl\|M2 | 34–35–38 | 45–48–49 | 0 / 0 |
| C594 | no | vhl\|M3 | 34–34–38 | 44–47–48 | 0 / 0 |
| C594 | no | vhl\|M4 | 33–34–37 | 44–46–47 | 0 / 0 |

Spread across conformers is itself the result: a reach that holds in one conformer is not a reach. A conformer **count is not a probability** — the 8XTT ensemble is restraint-satisfying, not Boltzmann-weighted.

## 3 · The counter-test — what a conserved cysteine does to it

The decision quantity is not *can it reach* but the **chemoselectivity margin**: the interval of backbone-atom counts over which the NR4A3-unique cysteine is in reach and **no** conserved cysteine is. Conserved cysteines are the ones NR4A1 and NR4A2 keep, so a conserved cysteine reachable at or before the unique one voids the entire paralogue-uniqueness argument.

**through-space convention**

| cysteine | placement | window (backbone atoms) | width | first conserved cysteine in reach |
|---|---|---|---|---|
| C397 | crbn\|M0 | [12, 12] | 1 | C536 at 13 |
| C397 | vhl\|M14 | [9, 9] | 1 | C536 at 10 |
| C397 | vhl\|M2 | [9, 11] | 3 | C536 at 12 |
| C397 | vhl\|M3 | [11, 11] | 1 | C536 at 12 |
| C397 | vhl\|M4 | **none** | 0 | C536 at 15 |
| C420 | crbn\|M0 | **none** | 0 | — |
| C420 | vhl\|M14 | **none** | 0 | — |
| C420 | vhl\|M2 | **none** | 0 | — |
| C420 | vhl\|M3 | **none** | 0 | — |
| C420 | vhl\|M4 | **none** | 0 | — |
| C559 | crbn\|M0 | **none** | 0 | — |
| C559 | vhl\|M14 | **none** | 0 | — |
| C559 | vhl\|M2 | **none** | 0 | — |
| C559 | vhl\|M3 | **none** | 0 | — |
| C559 | vhl\|M4 | **none** | 0 | — |

**corridor convention**

| cysteine | placement | window (backbone atoms) | width | first conserved cysteine in reach |
|---|---|---|---|---|
| C397 | crbn\|M0 | [13, 21] | 9 | C536 at 22 |
| C397 | vhl\|M14 | [13, 20] | 8 | C536 at 21 |
| C397 | vhl\|M2 | [9, 20] | 12 | C536 at 21 |
| C397 | vhl\|M3 | [12, 19] | 8 | C536 at 20 |
| C397 | vhl\|M4 | [16, 21] | 6 | C536 at 22 |
| C420 | crbn\|M0 | **none** | 0 | — |
| C420 | vhl\|M14 | **none** | 0 | — |
| C420 | vhl\|M2 | **none** | 0 | — |
| C420 | vhl\|M3 | **none** | 0 | — |
| C420 | vhl\|M4 | **none** | 0 | — |
| C559 | crbn\|M0 | **none** | 0 | — |
| C559 | vhl\|M14 | **none** | 0 | — |
| C559 | vhl\|M2 | **none** | 0 | — |
| C559 | vhl\|M3 | **none** | 0 | — |
| C559 | vhl\|M4 | **none** | 0 | — |

## 3b · The family-wide window — the quantity that actually decides it

THE DECISION QUANTITY: the interval of backbone-atom counts over which the electrophile reaches NR4A3 C397 and reaches NO other cysteine in NR4A3, NR4A1 or NR4A2. The intra-NR4A3 margin is the easy half; the route's whole claim is cross-paralogue, so the window that decides it is closed by the FIRST cysteine to come into reach anywhere in the family.

*the nr4a3-opened.pdb frame and the two superposed opened paralogue models — single conformers, not ensembles. See `paralogue_control.aligned_pair_displacement` for how far the paralogue atom counts may be trusted.*

**through_space convention, `dab_branch` pendant (8.75 Å arm), term-(a) exemplar placements**

| placement | C397 | intra-NR4A3 width | family-wide window | width | closed first by |
|---|---|---|---|---|---|
| crbn\|M0 | 11 | 5 | [11, 11] | **1** | NR4A1 C505 at 12 |
| vhl\|M14 | 7 | 7 | [7, 8] | **2** | NR4A1 C505 at 9 |
| vhl\|M2 | 9 | 6 | [9, 9] | **1** | NR4A1 C505 at 10 |
| vhl\|M3 | 11 | 4 | **none** | **0** | NR4A1 C505 at 11 |
| vhl\|M4 | 14 | 2 | **none** | **0** | NR4A1 C505 at 14 |

**corridor convention, `dab_branch` pendant (8.75 Å arm), term-(a) exemplar placements**

| placement | C397 | intra-NR4A3 width | family-wide window | width | closed first by |
|---|---|---|---|---|---|
| crbn\|M0 | 12 | 12 | [12, 15] | **4** | NR4A2 C534 at 16 |
| vhl\|M14 | 16 | 5 | **none** | **0** | NR4A1 C505 at 16 |
| vhl\|M2 | 11 | 12 | [11, 14] | **4** | NR4A2 C534 at 15 |
| vhl\|M3 | 11 | 11 | [11, 11] | **1** | NR4A2 C534 at 12 |
| vhl\|M4 | 14 | 8 | [14, 14] | **1** | NR4A2 C534 at 15 |

## 4 · The paralogue control

*The claim under test is that NR4A1 and NR4A2 have no cysteine where the electrophile lands. That is a statement about three aligned positions; what actually decides the route is whether either paralogue presents **any** cysteine inside the same tether geometry.*

### 4a · Uniqueness runs BOTH ways — the half that had never been checked

| paralogue cysteine | aligned NR4A3 residue | NR4A3 has a cysteine here? |
|---|---|---|
| NR4A1 C465 | C496 | yes |
| NR4A1 C475 | C506 | yes |
| NR4A1 C505 | C536 | yes |
| NR4A1 C534 | S565 | **no** |
| NR4A1 C551 | T579 | **no** |
| NR4A1 C566 | C594 | yes |
| NR4A2 C465 | C496 | yes |
| NR4A2 C475 | C506 | yes |
| NR4A2 C505 | C536 | yes |
| NR4A2 C534 | S565 | **no** |
| NR4A2 C566 | C594 | yes |

### 4b · How far a paralogue atom count may be trusted

| pair | ΔCA after superposition (Å) | ΔSG (Å) | ΔSG/ΔCA |
|---|---|---|---|
| NR4A1 C465 ↔ NR4A3 C496 | 2.97 | 5.94 | 2.0 |
| NR4A1 C475 ↔ NR4A3 C506 | 1.45 | 0.93 | 0.6 |
| NR4A1 C505 ↔ NR4A3 C536 | 1.19 | 4.06 | 3.4 |
| NR4A1 C566 ↔ NR4A3 C594 | 1.04 | 3.16 | 3.0 |
| NR4A2 C465 ↔ NR4A3 C496 | 2.55 | 3.47 | 1.4 |
| NR4A2 C475 ↔ NR4A3 C506 | 2.22 | 2.17 | 1.0 |
| NR4A2 C505 ↔ NR4A3 C536 | 0.35 | 3.34 | 9.5 |
| NR4A2 C566 ↔ NR4A3 C594 | 1.22 | 1.1 | 0.9 |

A ratio near 1 means the two models agree about that residue. A ratio well above 1 means the BACKBONES agree and the SIDE CHAINS do not, i.e. the gap is rotamer placement in independently built models. Every paralogue atom count below inherits that uncertainty and must not be quoted to better than the rotamer it rests on.

### 4c · The three NR4A3-unique cysteines, at their aligned paralogue positions

| NR4A3 unique cysteine | NR4A1 | NR4A2 | cysteine in either? |
|---|---|---|---|
| C397 | N363 | S363 | no |
| C420 | Q388 | A389 | no |
| C559 | Q528 | Q528 | no |

- **metad_ensemble/NR4A1** — 158 (cysteine x placement x pendant x convention) cell(s) put a PARALOGUE cysteine inside an NR4A3 design window — the uniqueness argument does not survive at those geometries
- **metad_ensemble/NR4A2** — 156 (cysteine x placement x pendant x convention) cell(s) put a PARALOGUE cysteine inside an NR4A3 design window — the uniqueness argument does not survive at those geometries
- **opened/NR4A1** — 114 (cysteine x placement x pendant x convention) cell(s) put a PARALOGUE cysteine inside an NR4A3 design window — the uniqueness argument does not survive at those geometries
- **opened/NR4A2** — 128 (cysteine x placement x pendant x convention) cell(s) put a PARALOGUE cysteine inside an NR4A3 design window — the uniqueness argument does not survive at those geometries

⚠ **NR4A1 C551** fall outside the superposition core, so their positions in this frame are UNRELIABLE and every atom count involving them is flagged rather than quoted. (NR4A1 C551 is the site NR-V04's selectivity is ATTRIBUTED to — proposed, never structurally confirmed — so this is exactly the residue a reader will look for, and this is what can honestly be said about it here.)

## 5 · Electrophile classes — options, with sources, and no assessment

⛔ OPTIONS WITH SOURCES — no reactivity, selectivity or feasibility claim is made or implied

The general position in the covalent-drug literature is that a covalent inhibitor's selectivity is dominated by the reversible recognition step that positions the electrophile, with intrinsic electrophile reactivity setting the promiscuity floor rather than the selectivity (Singh, Petter, Baillie & Whitty, Nat Rev Drug Discov 2011, 10:307-317). A geometric window is therefore a necessary input to that choice and not a substitute for it.

| class | what the trade-off is | primary sources |
|---|---|---|
| acrylamide (Michael acceptor) | the most-used cysteine warhead in approved covalent drugs | Honigberg et al., PNAS 2010, 107:13075-13080 (ibrutinib, BTK Cys481); Cross et al., Cancer Discov 2014, 4:1046-1061 (osimertinib, EGFR Cys797) |
| chloroacetamide / alpha-haloacetamide | higher intrinsic thiol reactivity than acrylamide; the two classes label systematically different cysteine sets in proteome-wide fragment screens, which is the trade-off a designer is choosing between | Backus et al., Nature 2016, 534:570-574 (isoTOP-ABPP ligandability map; chloroacetamide vs acrylamide fragment sets); Flanagan et al., J Med Chem 2014, 57:10072-10079 (glutathione reactivity across covalent reactive groups) |
| alpha-cyanoacrylamide (REVERSIBLE covalent) | the class the committed NR4A3 library already carries (`PENDANT.cyac_me`, `cyac_ph`); the alpha-cyano group acidifies the adduct alpha-proton so retro-Michael is fast, and residence time is tuned by the beta-substituent | Serafimova et al., Nat Chem Biol 2012, 8:471-476 (reversible targeting of noncatalytic cysteines with chemically tuned electrophiles); Bradshaw et al., Nat Chem Biol 2015, 11:525-531 (tunable residence time, reversible covalent kinase inhibitors) |
| vinyl sulfone / sulfonyl fluoride | sulfonyl fluorides are NOT cysteine-restricted — they also engage Ser/Thr/Tyr/Lys/His, so the residue-uniqueness argument this whole route rests on would not transfer | Narayanan & Jones, Chem Sci 2015, 6:2650-2659 (sulfonyl fluorides as privileged warheads in chemical biology) |

**Uncomputed and decision-relevant:** thiol pKa / local electrostatics at each NR4A3 cysteine — an exposed cysteine is not necessarily a nucleophilic one; intrinsic electrophile reactivity (GSH t1/2 or k_chem) for any pendant enumerated here; adduct stability, and for the reversible classes the residence time that decides whether catalytic turnover survives; off-target cysteine engagement outside the NR4A family — nothing here looks beyond three proteins, so no statement about wider selectivity is available.

## 6 · Cross-checks (rule 1 — this module must not mint a second value)

- `committed_anchor_distances`: **AGREES** (n = 60, max |Δ| 0.010 Å)
- `unique_cysteine_partition`: **AGREES**

## 7 · The answer

**Only C397 of the three NR4A3-unique cysteines is within tether range; C420, C559 are refuted at every placement, pendant and convention. A family-wide window survives in 25 of 30 graded (placement x pendant) cells, median width 4.0 backbone atoms. In 30 of the 30 graded cells the FIRST cysteine to come into reach is a PARALOGUE one, not an NR4A3 one, and the paralogue control costs a median of 5.0 backbone atoms of window — so the binding constraint on this route is the paralogues' own cysteines, not NR4A3's conserved ones. The correction that would reopen the window (6.25 A) exceeds every side-chain disagreement observed between these models at aligned cysteine pairs (max 5.94 A), so the closure is larger than the model noise measured for it.**

- **At which cysteine:** C397
- **Refuted unique cysteines:** C420, C559
- **Family-wide window (through_space):** 27 of 30 cells open, median width 3.0 atoms; window closed first by NR4A1 C505, NR4A2 C534; 30 cell(s) closed by a PARALOGUE cysteine; median 5.0 atoms of window lost to the paralogue control
- **Family-wide window (corridor):** 25 of 30 cells open, median width 4.0 atoms; window closed first by NR4A1 C505, NR4A2 C534; 30 cell(s) closed by a PARALOGUE cysteine; median 5.0 atoms of window lost to the paralogue control
- **What would defeat it:** NOT an NR4A3 conserved cysteine. The window is closed first by a PARALOGUE cysteine in 30 of the graded cells under the corridor convention — including NR4A1/NR4A2 C534, which aligns to NR4A3 S565 and is therefore a cysteine the PARALOGUES have and NR4A3 lacks. Uniqueness runs both ways, and the reciprocal direction was never checked before this module.
- **Trust bound on the paralogue numbers:** max ΔSG/ΔCA at aligned cysteine pairs = **9.5**. A ratio near 1 means the two models agree about that residue. A ratio well above 1 means the BACKBONES agree and the SIDE CHAINS do not, i.e. the gap is rotamer placement in independently built models. Every paralogue atom count below inherits that uncertainty and must not be quoted to better than the rotamer it rests on.

⛔ a feasibility statement. Geometry can refute a route; it cannot license one. No reactivity, potency, selectivity, developability, efficacy or safety claim is made or implied.

## Honest limits

- GEOMETRY ONLY. Reach is a necessary condition for a covalent handle and never a sufficient one. Thiol pKa, intrinsic electrophile reactivity, adduct formation, adduct stability, permeability and degradation are all uncomputed here.
- `through_space` is an UPPER BOUND on reachability: it places the branch atom anywhere in a three-ball intersection, including inside the protein.
- `corridor` is a NECESSARY condition, not a sufficient one: it tests one branch position and a straight arm, and does NOT thread the linker backbone, score torsions or test whether a clash-free region is connected to bulk solvent.
- Both conventions treat the protein as RIGID within a conformer. Induced fit is not modelled, and the ensemble is used as the only source of conformational freedom.
- The anchors are inherited from a DOCKED pose whose known-answer test has not returned (program map, `Ligand pose prediction (dock + MM-GBSA)` — running). Every number here is conditional on that pose, and none of it can be more reliable than the pose is.
- 16 of the 20 8XTT conformers do not carry a detectable cryptic site, so placing a warhead in them is a geometric operation and not a physical one. The cavity-bearing subset is reported separately for that reason.
- The paralogue ensembles are metadynamics, biased along a pocket-opening collective variable and not Boltzmann-weighted. They are a heterogeneity comparator; their spread is NOT comparable to the 8XTT spread. There is no experimental NR4A1/NR4A2 ensemble — that is a missing input, not a negative result.
- No claim of NR4A3 selectivity, efficacy, safety, a therapeutic window or clinical readiness is made or implied anywhere in this artifact.
