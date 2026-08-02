# Every mechanism by which paralogue selectivity could be argued for an NR4A3 degrader

**Breadth first, then honest grading.** 17 mechanisms, 7 measurements taken to settle them, **$0 — no GPU, no rental, no priced rung dispatched.** Nothing here is a claim about binding, reactivity, degradation, efficacy, safety or clinical readiness; several rows exist precisely to record that a mechanism **cannot** be claimed.

Regenerate with `python3 research/modalities/selectivity_mechanism_options.py`. Every figure taken from an existing artifact is a **citation** carrying the artifact that owns it; the seven measurements below are new and this file is their one home. This document is about **which mechanism**; [`selectivity-resolution-options.md`](./selectivity-resolution-options.md) is about **how much resolution** — they are orthogonal and neither restates the other.

---

## If you read only this

1. **The shortlist was three; the enumeration is 17.** Nine mechanisms in this register had no row, node or mention anywhere in the program before this file, and two of the nine are graded above the incumbent's nearest rival.
2. **★ The best genuinely-new option is STERIC EXCLUSION (`S3`, B+)** — three Pocket-5 positions where both paralogues carry a strictly bulkier side chain. Measured here with its own null: 0.923 paralogue-only clash against a 0.173 null at conserved/shared positions (5.34×). It scores a structure rather than generating one, its claim is a shape constraint rather than a ~1 kcal/mol ΔΔG, and it is the only new mechanism for which an unconfounded positive control is straightforwardly constructible.
3. **★ The categorical axis is not one residue.** Sweeping 11 reactive classes instead of the committed two finds 35 paralogue-unique, alignment-robust LBD positions, of which 5 are exposed, tetherable and belong to a class with credible ligand-directed chemistry (`S11`). Route B's single point of failure is a gap in the enumeration, not a fact about the protein.
4. **⛔ Two mechanisms are refuted here on committed data.** The paralogues are **not** lysine-poor — matched over 75 conformers per species the transfer zone reaches a lysine 0.4396 / 0.4279 / 0.3692 of the time, and the NR4A3−NR4A1 gap is under one replicate-SD (`S7`). And the cryptic pocket is **not** NR4A3-specific — both paralogues reach its druggable CV under matched metadynamics and fpocket rates NR4A1's opened frame *more* druggable (`S14`).
5. **⛔ E3 choice is not measurable at current staging precision (`S8`, D).** Changing only how the E3 arm is assembled swings the maximum term-(b) enrichment 16.60 → 6.07 on VHL and halves CRBN's any-lysine null. The program's one E3-preference claim was already retracted for this reason.
6. **The three cheapest high-value moves are all $0 and none needs authorization:** rung `5b-T` (`S5`, already roadmap row 1), the anti-handle design filter (`S15`), and asking for the two-branch template decision that unblocks the only compounding mechanism in the register (`S13`, roadmap row 8, *never asked*).
7. **One quoted figure needs its ensemble labels.** The triple `NR4A3 0.438 / NR4A1 0.387 / NR4A2 0.363` mixes a 75-conformer pooled median with two single static frames. The like-for-like values are given in M1. ⚠ The error is **conservative** for the conclusion drawn from it — nothing downstream needs revising.

---

## The register

Grades: **A** live, measured, and the claim it licenses is already defensible today · **B** live and buildable now — a $0/cheap decisive test exists and no instrument it needs has failed · **C** live but ceiling-limited — either the instrument is unvalidated in the needed regime, or a valid positive control cannot exist here, so a pass would license less than it appears to · **D** blocked — the instrument it needs has FAILED, or the mechanism reduces to a ddG smaller than any instrument here resolves · **F** refuted on committed evidence — do not retry this form of it

| grade | id | mechanism | new? | instrument passed a known-answer test **in the needed regime**? | could a valid positive control exist here? |
|---|---|---|---|---|---|
| **A-** | `S1` | Categorical covalent capture at a paralogue-unique cysteine (C397) | — | NO, and the failure is named: V17 FAILS its own positive control (NR4A1 Cys551, RSA 0 | PARTIALLY |
| **B** | `S15` | ★ Reciprocal anti-handle avoidance — design AWAY from the paralogues' own unique residues | ★ **NEW** | NO in the free-energy sense and it does not need one: avoiding a residue is a geometric constraint of exactly  | YES, and it is the best-supported one in the entire register: NR4A1 Cys551 / celastrol is the family's one lit |
| **B** | `S5` | Ternary interface discrimination (rung 5b-T) | — | PARTIALLY — the strongest pair in the program | YES for assembly (9DTY, post-horizon, already recovered) |
| **B** | `S6` | Linker length AS the selectivity filter — 'shortest viable linker' as a design principle | — | N/A for the reach half (it is enumeration, and its exactness was independently corrected in 2026-07-26 from a  | YES in the weak sense that the enumeration is checkable against geometry, and the artifact already carries a c |
| **B+** | `S3` | ★ Steric exclusion / negative design — a subpocket both paralogues deny | ★ **NEW** | NOT YET RUN as such — but this file supplies its own internal null, which is the thing that was missing: signa | YES, and unusually cleanly — steric-gatekeeper selectivity is the best-documented structure-based selectivity  |
| **B-** | `S11` | ★ Categorical covalent at a NON-cysteine unique nucleophile (Tyr / Met / Lys) | ★ **NEW** | NO — it inherits V17's demonstrated false negative exactly as S1 does, and adds a second untested layer: the c | YES for the geometry (same as S1) |
| **B-** | `S13` | ★ Two-point AND-gate engagement (cryptic pocket AND C397 simultaneously) | ★ **NEW** | N/A — it is a design architecture, not a measurement | YES in the literature (bivalent/AND-gate degraders are an established class) |
| **C** | `S17` | ★ Expression-context selectivity — a tissue-restricted E3, or a paralogue that is not there | ★ **NEW** | N/A — it is a data lookup, not an estimator | YES — tissue-restricted E3 degraders are an established concept with published examples |
| **C** | `S7` | Degradation-competence selectivity — a unique lysine in the transfer zone | — | NO — none exists for V18, and the roadmap says so | ⛔ NOT WITH ANY SYSTEM NAMED HERE |
| **C+** | `S12` | ★ Fusion-junction selectivity — target EWSR1::NR4A3, not NR4A3 | ★ **NEW** | N/A — nothing is built | ⚠ HARD |
| **C+** | `S16` | ★ Pharmacological window as an amplifier — dose, Dmax and the hook | ★ **NEW** | N/A — it is an equilibrium identity, not an estimator | YES trivially (published DC50/Dmax series), but nothing here needs one |
| **C+** | `S4` | ★ Categorical PHARMACOPHORE handles — a functional group both paralogues lack | ★ **NEW** | NO — identical to Route A | same as Route A: the V4 binary control, unauthorized and insufficient |
| **D** | `S10` | Cooperativity (alpha) differences between paralogues | — | ⛔ RUN AND FAILED | YES — it exists, is built, and is exactly what failed |
| **D** | `S14` | ★ Conformational-selection selectivity — differential cryptic-pocket opening | ★ **NEW** | NO | ⛔ Not with this instrument |
| **D** | `S2` | Divergent pocket handles resolved by free energy (Route A) | — | NO | YES and it is built — CREBBP vs BRD4(1)/SGC-CBP30, same ligand, two holo crystals, experimental ddG ~2 |
| **D** | `S8` | E3 recruiter choice as a selectivity lever | — | NO — and worse, the readout is not stable under a nuisance variable | In principle yes (a target with published VHL-vs-CRBN degradation selectivity), but it is moot until the stagi |
| **D** | `S9` | Kinetic / residence-time selectivity | — | NO, and the prior is bad: the program's metadynamics on a much simpler CV failed cross-replica reproducibility | YES in the literature (residence-time series with measured k_off exist), but building the instrument is a mult |

---

## The seven measurements taken here

### M1 — Is the transfer zone able to reach a lysine on NR4A3 more often than on NR4A1/NR4A2 — i.e. does DEGRADATION COMPETENCE discriminate on lysine availability alone?

NON-DISCRIMINATING against NR4A1 and weakly directional against NR4A2. Like-for-like over the same 75 unbiased conformers per species: NR4A3 0.4396, NR4A1 0.4279, NR4A2 0.3692. The NR4A3-vs-NR4A1 gap is +0.0118 against a replicate-SD of 0.0175 — under 1 SD, i.e. no measured difference — and the matched-frame win rate is 0.653, barely above a coin. NR4A2 is the only consistent direction (win rate 1.000, ratio 1.19x), and a 1.19x coverage ratio is not a selectivity mechanism.

> ⚠ correction to a quoted triple: The roadmap's Tier-2 block and the lane doc quote 'NR4A3 0.438 / NR4A1 0.387 / NR4A2 0.363' as a comparable triple. It is not: 0.438 is NR4A3's pooled-unbiased MEDIAN over 75 conformers, while 0.387 and 0.363 are SINGLE static opened models (the lane doc's own table labels the ensembles correctly; the roadmap's one-line restatement drops the labels). The like-for-like static triple is 0.4035 / 0.3914 / 0.3650 and the like-for-like pooled triple is 0.4396 / 0.4279 / 0.3692. ⚠ The error is CONSERVATIVE for the conclusion drawn from it — matching the ensembles makes the NR4A1 gap SMALLER (+0.051 implied -> +0.012 measured), so 'already non-discriminating on the any-lysine measure' is if anything understated. Nothing downstream needs revising; the row needs its ensemble labels.

### M2 — Is the categorical covalent axis one residue (C397) or a family of handles?

The categorical axis is NOT one residue. Across 11 reactive classes NR4A3 carries 35 paralogue-unique, alignment-robust positions in the LBD; 18 are both solvent-exposed under the V17 cutoff and within linker reach of the cryptic pocket, and 5 of those belong to a residue class with routine or precedented ligand-directed covalent chemistry. ★ The genuinely NEW candidates are Y419 (SuFEx tyrosine, RSA 0.221, exit-vector band, one residue from C420) and M398/M399 (oxaziridine methionines). Route B as drawn has a single point of failure — C397 — and this is the first enumeration showing the failure is not structural.

Limits:
- Sequence uniqueness is exact; every geometric annotation is one static opened conformer.
- 'exposed' is adjudicated by V17 (EXPOSED_RSA = 0.25), which FAILS its own positive control (NR4A1 Cys551) — so this column is a RANK, not a threshold, exactly as for the cysteine axis.
- Chemistry credibility is a literature judgement carried as a label, not a computed quantity. No thiol/phenol pKa, nucleophilicity, adduct stability or electrophile promiscuity is modelled.
- Ser/Thr/Asp/Glu/Arg/Trp are enumerated for completeness and graded 'not a handle'. Counting them as options would be the same error as counting a reachable buried cysteine.

### M3 — Is there a subpocket that NR4A3 offers and BOTH paralogues sterically deny — a NEGATIVE-DESIGN categorical handle, answered by SHAPE rather than by free energy?

MEASURED AND CONTROLLED. Paralogue-only clash rate is 0.923 at the three positions where NR4A3's residue is paralogue-unique AND both paralogue side chains are strictly bulkier (L406->His/His, I484->Tyr/Tyr, L534->Phe/Phe), against a null of 0.173 at conserved-or-shared positions — an enrichment of 5.34x. The three paralogue-unique-but-NOT-bulkier positions (T407, T410, R412) fire at 0.000, which is the correct behaviour: uniqueness alone does not create a steric exclusion. ⚠ The null is NOT zero — I531 (Ile in NR4A3 AND in NR4A2) accounts for 6 of the 9 null hits, i.e. a pure superposition/rotamer artifact, which is exactly what a null is for.

Limits:
- RIGID TRANSFER. The paralogue side chain is held in its own opened conformer; it could rotate away. This measures 'clash in the paralogue's modelled conformer with the ligand held fixed', never 'the ligand cannot bind'.
- The absence of NR4A3 clash is guaranteed by construction (these poses were docked into NR4A3) and carries no information. Only the between-class contrast is gradeable.
- Conditional on the two opened paralogue models and on the superposition: post-fit deviation at R412 is the largest in the set, so R412's geometry in this frame is the least trustworthy.
- The 13 molecules are the committed selectivity-matrix library, not the carried candidate.

### M4 — Does the paralogue accommodate the same molecule in the same place, or relocate it? This is the control that decides whether M3's steric exclusion is categorical or soft.

The paralogue relocates the ligand rather than reproducing the pose: median centroid shift 5.31 A (NR4A1) and 5.26 A (NR4A2). So M3's exclusion is real about the POSE and says nothing about whether the paralogue binds the molecule at all — which is the honest ceiling for a negative-design argument, and it is a design rule rather than a claim.

> ⛔ the scores are NOT evidence: The per-species docking dG values are reproduced here for completeness and must not be read as a selectivity margin: single-snapshot scoring as a selectivity verdict is the instrument the roadmap's closed-route register lists as REFUTED (V20 — 22 of 38 unrelated marketed drugs score a positive NR4A3 margin). Two rows of this very table are the reason: resveratrol scores better on NR4A1 than NR4A3, and CHEMBL4755698 better on NR4A2 — and celastrol, the one molecule in the panel with a literature-anchored NR4A-family preference (NR4A1, via a covalent bond at Cys551), is scored BEST on NR4A3. A non-covalent score does not see the covalent step, which is the argument for the categorical axis, not against it — but it disposes of the margins.

### M5 — Does the cryptic pocket open only in NR4A3 — i.e. is there conformational-selection selectivity available before any chemistry?

THE CATEGORICAL FORM IS DEAD ON COMMITTED DATA. Both paralogues reach NR4A3's druggable CV value (Rg = 0.717 nm) inside their own matched metadynamics — NR4A1 exactly, NR4A2 within 0.004 nm — and in the opened frames fpocket rates NR4A1 (0.981) MORE druggable than NR4A3 (0.931). 'Only NR4A3 has the cryptic site' is not available as an argument.

> ✓ what survives: The QUANTITATIVE form: the paralogues may pay a different FREE-ENERGY price to reach that state. That is exactly requirement R6 (dg_open_paralogue) — a requirement with no instrument, held on an explicit nod, and whose only demonstrated single-profile reading is in the closed-route register. A biased ensemble reaching a CV value says nothing about its population.

### M6 — Is one E3 recruiter paralogue-discriminating — and does the answer survive a restaging?

EVERY APPARENT E3 PREFERENCE MEASURED HERE HAS TRACKED THE STAGING CONSTRUCTION RATHER THAN THE RECRUITER. Changing only how the E3 arm is assembled — composed vs assembly-native, no change to recruiter, sampling or criteria — moves CRBN's any-lysine null from 0.760-0.980 to 0.320-0.445 while VHL's barely moves, swings VHL's maximum term-(b) enrichment 16.60 -> 6.07, and takes the term-(a) count 0 -> 2. The roadmap already records the one E3-preference claim this program made ('the discrimination lives on VHL') as RETRACTED the same day, for exactly this reason. A recruiter preference is not measurable at the current staging precision.

> ⚠ which registry the headline run used: The definitive 12-pose Tier-2 run reads `nr4a3-e3-arm-registry.json`, NOT the assembly-native registry — so its CRBN null (0.765-0.945) is the composed-like value. The matched pair exists precisely so that this is checkable rather than assumed.

### M7 — How much true margin does a degradation WINDOW need, and can a cooperativity difference substitute for an affinity difference?

Cooperativity is the higher-leverage lever, and it is the one whose instrument failed. With alpha = 3 on target and alpha = 1 on the paralogue and ZERO binary margin, the model gives a 7.9x DC50 separation; a 1.0 kcal/mol binary margin at matched alpha gives a Dmax gap of only 0.12 and a 2.0 kcal/mol margin 0.30. That ordering is why the roadmap's ~2.0 kcal/mol requirement for a useful window is the right scale for the AFFINITY route — and why the cooperativity route would need far less margin if its instrument worked. It does not: the ternary cooperativity calculator returned the WRONG SIGN in all three replicates at ~34x its own uncertainty, and the closure triangle localised the miss to an endpoint-state error that more sampling will not fix.

---

## Every mechanism in full

### `S1` Categorical covalent capture at a paralogue-unique cysteine (C397) — grade **A-**

**Status:** LIVE — the program's incumbent  ·  **current**

- **Physical basis.** NR4A1 and NR4A2 carry a non-nucleophile at the aligned position (Asn363 / Ser363), so no electrophile can form the adduct on them at all. Set membership, not an energy difference.
- **Instrument.** reach enumeration + V17 exposure criterion; 73,867 matched E3 placements
- **Known-answer test in the needed regime?** NO, and the failure is named: V17 FAILS its own positive control (NR4A1 Cys551, RSA 0.165, 0 of 25 metadynamics frames). What survives is a threshold-free RANK.
- **Could a valid positive control exist here?** PARTIALLY. NR-V04/celastrol is the family's one literature-anchored covalent site and it is the reciprocal of this mechanism — which is why the roadmap files it as a CONFOUND for a selectivity readout and simultaneously as a PRECEDENT for this one. Those are compatible: a system that cannot serve as a control for detecting selectivity can still demonstrate that the mechanism exists in this family.
- **Cheapest decisive test.** $0 — already taken. The design gate holds on REACH alone (reach-only collision 0.000-0.003 at 12 atoms), so the discredited exposure cutoff carries almost no load there.
- **A pass would license:**
  - a short-linker design preference, measured and monotonic
  - a refutation of C420 and C559 as handles at routine linker length
  - a narrowed TARGET-ENGAGEMENT geometry statement over a construct class
- **⛔ A pass would NOT license:**
  - degradation, affinity, efficacy, safety or a therapeutic window
  - proteome-wide selectivity — the comparison set is two paralogues
  - that a covalent bond forms at all (pKa, reactivity, adduct stability are untested)
- **Why this grade.** The strongest available mechanism and the only one immune to the free-energy resolution gap — but it rests on ONE residue, its exposure adjudicator has a demonstrated false negative, and the chemoselectivity window is closed by a PARALOGUE cysteine in 30 of 30 graded cells, at a position NR4A3 SHARES in 24 of those 30.

### `S15` ★ Reciprocal anti-handle avoidance — design AWAY from the paralogues' own unique residues — grade **B**

**Status:** LIVE — free, and it is already the binding constraint  ·  **NEW as an explicit axis**

- **Physical basis.** The mirror of S1. NR4A1 carries 14 reciprocal-unique reactive residues and NR4A2 carries 5 — sites where a paralogue is chemically addressable and NR4A3 is not. These are not a curiosity: they are what actually CLOSES the chemoselectivity window, in 30 of 30 graded cells, and NR4A2 C534 (a position NR4A3 lacks) closes 23 of 30 corridor cells.
- **Instrument.** the committed reciprocal-uniqueness map + the reach kernel — both already exist
- **Known-answer test in the needed regime?** NO in the free-energy sense and it does not need one: avoiding a residue is a geometric constraint of exactly the kind S1 already relies on.
- **Could a valid positive control exist here?** YES, and it is the best-supported one in the entire register: NR4A1 Cys551 / celastrol is the family's one literature-anchored covalent site, and it is an ANTI-handle. A construct reaching C551 is a demonstrated NR4A1 liability — the confound that ruins NR-V04 as a positive control for detecting selectivity is a clean positive control for AVOIDING one.
- **Cheapest decisive test.** $0 — the closure data is committed. What is missing is that the anti-handle set is not carried as a design CONSTRAINT anywhere: the enumeration optimises reach TO C397 and only reports the paralogue closure afterwards.
- **A pass would license:**
  - a hard design filter — reject any construct whose reach envelope admits NR4A1 C505/C551 or NR4A2 C534 — which is free and strictly tightens every other row here
- **⛔ A pass would NOT license:**
  - an increase in NR4A3 engagement. It removes liabilities; it adds no signal.
  - a proteome-wide claim — an electrophile does not know it is meant to be selective
- **Why this grade.** Free, already measurable, uses only instruments that have not failed, and it has the register's cleanest positive control. It is capped at B because it is a filter rather than a mechanism: it can only ever narrow the design space, never widen the margin.

### `S5` Ternary interface discrimination (rung 5b-T) — grade **B**

**Status:** LIVE — $0, unauthorized-free, and on the roadmap as row 1  ·  **current**

- **Physical basis.** the induced target-E3 interface differs between paralogues; V1 reads it structurally
- **Instrument.** V2 (assembly-route generator, PASSES in scope) -> V1 (interface descriptor, PASSES in scope)
- **Known-answer test in the needed regime?** PARTIALLY — the strongest pair in the program. V2 rebuilt post-horizon 9DTY at DockQ 0.839 (best of 16 seeds, median 0.442, one arm only — the SMARCA4 arm was refused and no SMARCA4 number exists). V1 recovered the published SMARCA2 Gln1469 contact — ONE contact in ONE pair, and it makes no NR4A3 prediction correct.
- **Could a valid positive control exist here?** YES for assembly (9DTY, post-horizon, already recovered). NO, currently, for the SELECTIVITY read: the E1 interface-stability endpoint has two attempts and no pass (p = 0.393 DISCORDANT, p = 0.747 NULL on an adequately-powered design).
- **Cheapest decisive test.** $0 CPU — rung 5b-T, priced at $0, needs no authorization, and has a pre-registered three-arm gate
- **A pass would license:**
  - that an NR4A3 ternary can be assembled at all — currently NO ternary for this target has been
  - R11's reproducibility bar: 16 models per arm against a bar of 3, currently met by 1
- **⛔ A pass would NOT license:**
  - any thermodynamic statement — the output is structural, never energetic
  - selectivity, unless a readout with power exists, and V11 has failed twice
- **Why this grade.** The best-instrumented live mechanism and the cheapest big move on the board: both instruments have passed a known-answer test IN SCOPE, it scores rather than generates (lesson 1), and it costs $0 with no nod required. Capped at B because its selectivity readout is the one that has already failed twice.

### `S6` Linker length AS the selectivity filter — 'shortest viable linker' as a design principle — grade **B**

**Status:** LIVE — publishable as a principle, with one caveat that must travel with it  ·  **current**

- **Physical basis.** P(a paralogue cysteine is also reached | an NR4A3-unique one is) climbs monotonically with backbone length: 0.000-0.003 at 12 atoms, 0.009-0.032 at 14, 0.054-0.133 at 16, 0.263-0.383 at 20, over three ensembles. Length is therefore not merely a tractability axis — it is the variable that sets the discrimination.
- **Instrument.** geometric enumeration over 73,867 placements — no free energy anywhere
- **Known-answer test in the needed regime?** N/A for the reach half (it is enumeration, and its exactness was independently corrected in 2026-07-26 from a bound to an exact three-ball kernel). NO for the exposure half — V17 again.
- **Could a valid positive control exist here?** YES in the weak sense that the enumeration is checkable against geometry, and the artifact already carries a cross-convention agreement check. There is no experimental positive control, and there cannot be one without a bench.
- **Cheapest decisive test.** $0 — already computed and committed
- **A pass would license:**
  - a genuine, quantitative design principle: prefer 11-12 backbone atoms; a construct drifting to 16+ trades away the axis it exists to exploit
  - a publishable negative: C420 and C559 are not usable at routine length
- **⛔ A pass would NOT license:**
  - the 16- and 20-atom columns as a SELECTIVITY statement. P(categorical | exposed) is 1.000 at EVERY length, so the entire length dependence lives in cysteines that the discredited V17 cutoff calls buried. At 12 atoms the result holds on reach alone; past 14 it does not.
  - any statement about the chemoselectivity WINDOW being NR4A3-limited — it is closed by a PARALOGUE cysteine in 30 of 30 graded cells, and in 24 of 30 through-space cells by NR4A1 C505, a position NR4A3 SHARES (C536)
- **Why this grade.** A real, measured, publishable design principle that costs nothing and needs no instrument this program lacks — provided it is stated at the 12-atom gate, where it does not depend on the failed exposure criterion. Stated at 16-20 atoms it inherits V17's false negative.

### `S3` ★ Steric exclusion / negative design — a subpocket both paralogues deny — grade **B+**

**Status:** LIVE — NEW, and measured in this file  ·  **NEW**

- **Physical basis.** At three Pocket-5 positions NR4A3's residue is paralogue-unique AND both paralogues carry a strictly bulkier side chain: L406->His/His, I484->Tyr/Tyr, L534->Phe/Phe. A ligand substituent that fills that lobe in NR4A3 has nowhere to sit in either paralogue. The quantity is a CLASH, which is tens of kT, not a ~1 kcal/mol preference — and the question 'does this atom fit' is answered by shape, not by a free-energy engine.
- **Instrument.** shape/steric evaluation on an already-generated structure — the SCORING side of lesson 1, not the generating side
- **Known-answer test in the needed regime?** NOT YET RUN as such — but this file supplies its own internal null, which is the thing that was missing: signal 0.923 vs null 0.173 (5.34x). A known-answer test is cheap and obvious: any published kinase/NR selectivity pair whose selectivity is attributed to a single gatekeeper-size difference.
- **Could a valid positive control exist here?** YES, and unusually cleanly — steric-gatekeeper selectivity is the best-documented structure-based selectivity mechanism in the literature, so a known-answer pair with a measured selectivity ratio and two crystal structures is findable. This is the ONLY new mechanism here for which an unconfounded, adequately-powered positive control is straightforwardly constructible.
- **Cheapest decisive test.** $0 — taken here, including its decisive control. M4: the paralogue's own docking relocates the same molecule by a median 5.31 A (NR4A1) / 5.26 A (NR4A2), so the paralogue does not reproduce the pose.
- **A pass would license:**
  - a POSITIVE DESIGN RULE with a measured basis: grow the warhead into the L406/I484/L534 lobe
  - a falsifiable prediction — a matched pair differing only in that substituent
- **⛔ A pass would NOT license:**
  - that the paralogue does not bind the molecule. It binds it somewhere else (M4).
  - any affinity, degradation or selectivity RATIO — no energy is computed anywhere here
  - escape from R5: it is conditional on the cryptic pocket being the right site
- **Why this grade.** The strongest of the new options. It scores a structure rather than generating one (lesson 1), its claim is a shape constraint rather than a ~1 kcal/mol ddG (lesson 2), it arrives with its own null already measured, and a valid positive control could exist (lesson 3). It is capped at B+ because it is conditional on the docked pose and on the rigid-transfer assumption, and because the mechanism constrains the POSE, not binding.

### `S11` ★ Categorical covalent at a NON-cysteine unique nucleophile (Tyr / Met / Lys) — grade **B-**

**Status:** LIVE — NEW, and enumerated here for the first time  ·  **NEW**

- **Physical basis.** The categorical argument is about a residue type the paralogues lack — nothing in it is specific to sulfur. Sweeping 11 reactive classes instead of the committed two finds 35 paralogue-unique, alignment-robust LBD positions, of which 5 are exposed, within linker reach, AND belong to a class with routine or precedented ligand-directed covalent chemistry.
- **Instrument.** identical to S1 — the same reach enumeration and the same exposure rank
- **Known-answer test in the needed regime?** NO — it inherits V17's demonstrated false negative exactly as S1 does, and adds a second untested layer: the chemistry credibility label is a literature judgement, not a measurement.
- **Could a valid positive control exist here?** YES for the geometry (same as S1). For the chemistry, published SuFEx tyrosine-targeting and oxaziridine methionine-targeting probes exist as precedent, but no positive control for THIS site is possible without a bench.
- **Cheapest decisive test.** $0 — taken here (M2); the reach envelope per new handle is the same $0 kernel already written for cysteines
- **Measured here.** The categorical axis is NOT one residue. Across 11 reactive classes NR4A3 carries 35 paralogue-unique, alignment-robust positions in the LBD; 18 are both solvent-exposed under the V17 cutoff and within linker reach of the cryptic pocket, and 5 of those belong to a residue class with routine or precedented ligand-directed covalent chemistry. ★ The genuinely NEW candidates are Y419 (SuFEx tyrosine, RSA 0.221, exit-vector band, one residue from C420) and M398/M399 (oxaziridine methionines). Route B as drawn has a single point of failure — C397 — and this is the first enumeration showing the failure is not structural.
- **A pass would license:**
  - removal of Route B's single point of failure — the paper currently states the only insurance against a C397-specific chemical failure is the unique-LYSINE degradation term, which is a different requirement; this supplies engagement-level redundancy
  - a prioritised second and third handle: Y419 (SuFEx) and M398/M399 (oxaziridine)
- **⛔ A pass would NOT license:**
  - the 'not a handle' classes (Ser/Thr/Asp/Glu/Arg/Trp) as options — counting them would be the same error as counting a buried cysteine
  - any statement that these adducts form; only that the residue is unique and reachable
- **Why this grade.** Cheap, already computed, and it fixes a structural weakness the paper names about itself. Held to B- because the chemistry credibility of Tyr/Met handles is a judgement rather than a measurement, Y419 sits at RSA 0.221 — BELOW the exposure cutoff whose false negative is the reason we distrust it in the other direction — and each new handle re-opens the chemoselectivity-window question that S1 already answers uncomfortably.

### `S13` ★ Two-point AND-gate engagement (cryptic pocket AND C397 simultaneously) — grade **B-**

**Status:** BLOCKED ON A DECISION NOBODY HAS ASKED FOR  ·  **NEW framing**

- **Physical basis.** If binding requires BOTH a pocket interaction and a covalent capture at a unique residue, the selectivity ratios multiply rather than add. It is the only mechanism in the register whose margin COMPOUNDS.
- **Instrument.** RDKit enumeration + the same reach kernel — no new instrument needed
- **Known-answer test in the needed regime?** N/A — it is a design architecture, not a measurement.
- **Could a valid positive control exist here?** YES in the literature (bivalent/AND-gate degraders are an established class).
- **Cheapest decisive test.** $0, and it is a DECISION rather than a computation: the one-pendant linker grid is in the closed-route register as architecturally incapable of emitting such a molecule (branch floor k = 3 + SEG2 + tail, no grid change reaches k < 4). The fix is a two-branch template at n = 18 with existing segments — a design change to a preregistered enumeration that 'has never been put to trimcrae'.
- **A pass would license:**
  - a multiplicative selectivity argument built from two independently-measured terms
- **⛔ A pass would NOT license:**
  - either term individually being any stronger than its own row here
  - any claim before the template decision is taken — enumerating over the current grid searches a space that structurally cannot contain the answer
- **Why this grade.** Highest compounding upside of anything buildable, zero new instrument risk, and blocked only by a $0 decision that the roadmap already lists as row 8 and records as never having been asked. It is not higher because the two terms it multiplies are themselves A- and C+/D, and multiplying an unvalidated term by a validated one does not validate it.

### `S17` ★ Expression-context selectivity — a tissue-restricted E3, or a paralogue that is not there — grade **C**

**Status:** REFUTED for the E3 half on committed data; UNTESTED for the paralogue half  ·  **NEW**

- **Physical basis.** A degrader is only active where its full CRL arm is expressed, and a paralogue that is not expressed in the tissue at risk does not need to be spared. Neither requires any molecular discrimination at all.
- **Instrument.** committed expression artifacts (Human Protein Atlas arms; DepMap for the target)
- **Known-answer test in the needed regime?** N/A — it is a data lookup, not an estimator.
- **Could a valid positive control exist here?** YES — tissue-restricted E3 degraders are an established concept with published examples.
- **Cheapest decisive test.** $0. The E3 half is already answered: all 10 recruiter arms in the widened panel are BROADLY EXPRESSED and complete, so no arm in the panel offers tissue restriction. The paralogue half is NOT answered — the committed DepMap artifact carries NR4A3 only (sarcoma mean log2TPM 1.03, expressed in 0.09 of lines) and holds no NR4A1 or NR4A2 row. Widening the existing gene list is a one-line change to an existing $0 CI job.
- **A pass would license:**
  - a claim-scope statement: WHICH paralogue actually needs sparing, and where
  - a re-weighting of every other row — the roadmap names NR4A2 as carrying the dopaminergic-loss liability, and it is also the paralogue Route A is 20% thinner against
- **⛔ A pass would NOT license:**
  - ⛔ any molecular selectivity. Expression context changes what a margin BUYS, never whether the molecule discriminates.
  - safety or a therapeutic window — neither is computed anywhere in this program
- **Why this grade.** The E3 half is closed on committed data and should stop being proposed. The paralogue half is a $0 CI job that nobody has run and that would sharpen the scope of every selectivity sentence in the paper — which is worth more than it sounds, because the program's selectivity claim is currently bounded to two paralogues by an unrun cross-binding check.

### `S7` Degradation-competence selectivity — a unique lysine in the transfer zone — grade **C**

**Status:** SPLIT: the availability form is refuted here; the joint form is live but uncalibrated  ·  **current (the roadmap's third route)**

- **Physical basis.** A PROTAC can be selective at the ubiquitin-transfer step rather than at binding: a lysine that is not present cannot be ubiquitinated. NR4A3 has 4 unique lysines, 3 exposed (K518/K572/K592), against a MEASURED 17.1 A transfer distance.
- **Instrument.** V18, the transfer-zone lysine-identity term
- **Known-answer test in the needed regime?** NO — none exists for V18, and the roadmap says so.
- **Could a valid positive control exist here?** ⛔ NOT WITH ANY SYSTEM NAMED HERE. A positive control needs a degrader whose selectivity is ATTRIBUTED to lysine placement, with the ubiquitinated site mapped. Real degraders often ubiquitinate several lysines and lysine-less substrates are still degraded, so even a correct prediction would be weakly diagnostic. This is the same shape as lesson 3: the confound is in the biology, not the instrument.
- **Cheapest decisive test.** $0 — taken here (M1)
- **Measured here.** NON-DISCRIMINATING against NR4A1 and weakly directional against NR4A2. Like-for-like over the same 75 unbiased conformers per species: NR4A3 0.4396, NR4A1 0.4279, NR4A2 0.3692. The NR4A3-vs-NR4A1 gap is +0.0118 against a replicate-SD of 0.0175 — under 1 SD, i.e. no measured difference — and the matched-frame win rate is 0.653, barely above a coin. NR4A2 is the only consistent direction (win rate 1.000, ratio 1.19x), and a 1.19x coverage ratio is not a selectivity mechanism.
- **A pass would license:**
  - the JOINT form only: a basin whose transfer zone covers an NR4A3-unique lysine while both paralogue zones stay bare — max 0.152 over 58 meta-basins, 37 of 58 non-zero
- **⛔ A pass would NOT license:**
  - ⛔ the AVAILABILITY form. Measured here: matched over 75 conformers per species the transfer zone reaches a lysine on NR4A3 0.4396, NR4A1 0.4279, NR4A2 0.3692 of the time. The NR4A3-NR4A1 gap is under one replicate-SD. The paralogues are NOT lysine-poor.
  - any degradation rate — the term is set membership, and no composed RING or E2 may carry it
- **Why this grade.** The mechanism is real and is the program's only insurance against a C397-specific chemical failure — but it has no known-answer test, no constructible positive control, and its intuitive form (the paralogues lack lysines) is measured here to be false. Its surviving form is a rare coincidence read off a best-of-N-prone statistic.

### `S12` ★ Fusion-junction selectivity — target EWSR1::NR4A3, not NR4A3 — grade **C+**

**Status:** NO RUNG, NO GATE, NO PRICE — the largest unclaimed mechanism on the board  ·  **NEW framing of R13**

- **Physical basis.** The disease object is the fusion oncoprotein. It carries an EWSR1 N-terminal moiety and a junction that NO wild-type NR4A has — including wild-type NR4A3. Selectivity against the fusion is therefore categorically stronger than paralogue selectivity: it spares NR4A1, NR4A2 AND the patient's own NR4A3. The committed uniqueness map already carries EWSR1 lysine counts under three documented breakpoint scenarios.
- **Instrument.** ⛔ none. Every structure in this program is an isolated LBD construct (373-626); C166, one of the four unique cysteines, is already outside it.
- **Known-answer test in the needed regime?** N/A — nothing is built.
- **Could a valid positive control exist here?** ⚠ HARD. The EWSR1 moiety is a low-complexity prion-like region with no folded structure, so the generation problem is the WORST case of lesson 1 — a de novo structure of a disordered region, which is the failure mode that put the two halves 32 A apart. A sequence-level and lysine-inventory analysis needs no structure and is $0.
- **Cheapest decisive test.** $0 — extend the existing uniqueness sweep across the junction and inventory EWSR1-moiety lysines under each breakpoint scenario. The producer function already exists (`fusion_lysine_scenarios`) and is already committed with 1-2 lysines per scenario.
- **A pass would license:**
  - a claim-SCOPE upgrade: selectivity against the oncoprotein rather than against a paralogue
  - validation requirement 5's explicit ask — model the real biological object
- **⛔ A pass would NOT license:**
  - any geometry claim. A disordered fusion moiety cannot be modelled by anything in this repo, and a co-fold of it would be the exact generation problem that already failed.
- **Why this grade.** The highest CEILING in the register and the lowest readiness. It is graded C+ rather than lower because its cheapest useful form — a sequence-level lysine and uniqueness inventory across the junction — is $0, needs no structure, and would give the paper a scope sentence it currently cannot write. It is graded no higher because everything past that needs a structure of a disordered region.

### `S16` ★ Pharmacological window as an amplifier — dose, Dmax and the hook — grade **C+**

**Status:** NOT A SELECTIVITY MECHANISM — a conversion between one and an observable  ·  **NEW**

- **Physical basis.** Degradation is not linear in binding. A given margin becomes an observable window through the three-body equilibrium, so the question 'how much margin do we need?' has a computable answer that does not depend on measuring the margin.
- **Instrument.** the committed three-body cooperative-equilibrium model
- **Known-answer test in the needed regime?** N/A — it is an equilibrium identity, not an estimator. Its INPUTS (Kd, alpha) are the unvalidated quantities, and the model's own header says it is illustrative.
- **Could a valid positive control exist here?** YES trivially (published DC50/Dmax series), but nothing here needs one.
- **Cheapest decisive test.** $0 — taken here (M7)
- **Measured here.** Cooperativity is the higher-leverage lever, and it is the one whose instrument failed. With alpha = 3 on target and alpha = 1 on the paralogue and ZERO binary margin, the model gives a 7.9x DC50 separation; a 1.0 kcal/mol binary margin at matched alpha gives a Dmax gap of only 0.12 and a 2.0 kcal/mol margin 0.30. That ordering is why the roadmap's ~2.0 kcal/mol requirement for a useful window is the right scale for the AFFINITY route — and why the cooperativity route would need far less margin if its instrument worked. It does not: the ternary cooperativity calculator returned the WRONG SIGN in all three replicates at ~34x its own uncertainty, and the closure triangle localised the miss to an endpoint-state error that more sampling will not fix.
- **A pass would license:**
  - an honest statement of the REQUIRED margin per mechanism, which is what the register above grades against
  - a reporting frame: report the margin needed for a window, not a raw ddG
- **⛔ A pass would NOT license:**
  - any DC50, Dmax or dose for any molecule. The parameters are illustrative and the artifact says so.
  - the idea that a window can substitute for a margin — it converts one, it does not create one
- **Why this grade.** Included because it changes how every other row is graded and it costs nothing. It is not higher because it produces no selectivity of its own.

### `S4` ★ Categorical PHARMACOPHORE handles — a functional group both paralogues lack — grade **C+**

**Status:** LIVE — NEW framing of an existing measurement  ·  **NEW**

- **Physical basis.** Six of Route A's divergent pocket residues are not merely different but CATEGORICALLY unique: T407 (Leu/Val in the paralogues — only NR4A3 can donate/accept an H-bond there), R412 (Ala/Thr — only NR4A3 offers a cation), T410 (Gly/Asn). Designing to a functional group the paralogues do not possess is a larger expected ddG than designing to a size difference between similar residues — a buried H-bond or salt bridge is conventionally 1-3 kcal/mol, against Route A's ~0.6 kcal/mol resolvable.
- **Instrument.** the same free-energy engines as Route A — this changes the EFFECT SIZE, not the ruler
- **Known-answer test in the needed regime?** NO — identical to Route A. V4 is unrun.
- **Could a valid positive control exist here?** same as Route A: the V4 binary control, unauthorized and insufficient
- **Cheapest decisive test.** $0 — the uniqueness call is taken here (S4's three positions are the `unique_not_bulkier` class of M3, and they fire at 0.000 on the steric test, which is correct: they are electronic handles, not steric ones).
- **A pass would license:**
  - a pharmacophore constraint on the warhead, stated as a hypothesis
- **⛔ A pass would NOT license:**
  - any margin — it still needs a free-energy number in the unvalidated regime
  - R412 in particular: the roadmap records it facing into the pocket in only 0.25 of druggable frames, from an S3-only artifact NOT committed to this repo; and its post-fit superposition deviation is the largest of the ten positions measured in M3
- **Why this grade.** Strictly better than Route A as drawn — a bigger expected effect for the same instrument — but it does not escape lesson 2, and its best residue (R412) has both a facing caveat resting on an uncommitted artifact and the worst geometry reliability in the set.

### `S10` Cooperativity (alpha) differences between paralogues — grade **D**

**Status:** HIGH LEVERAGE, INSTRUMENT FAILED  ·  **current**

- **Physical basis.** alpha multiplies the ternary population; a paralogue with lower alpha is spared at the same occupancy
- **Instrument.** V5 (alchemical ternary ddG_coop, valB_mini)
- **Known-answer test in the needed regime?** ⛔ RUN AND FAILED. Target +0.944 kcal/mol, returned -0.599 — WRONG SIGN in all three replicates at ~34x the statistical uncertainty. The closure triangle localises the miss to an endpoint-state error, so more sampling will not fix it, and the triangle is separately REFUTED as a diagnostic for that miss.
- **Could a valid positive control exist here?** YES — it exists, is built, and is exactly what failed. That is the strongest possible form of this answer and it is why this row is D rather than C: the control was available, was run, and returned a refutation of the instrument.
- **Cheapest decisive test.** $0 — the leverage calculation, taken here (M7)
- **Measured here.** Cooperativity is the higher-leverage lever, and it is the one whose instrument failed. With alpha = 3 on target and alpha = 1 on the paralogue and ZERO binary margin, the model gives a 7.9x DC50 separation; a 1.0 kcal/mol binary margin at matched alpha gives a Dmax gap of only 0.12 and a 2.0 kcal/mol margin 0.30. That ordering is why the roadmap's ~2.0 kcal/mol requirement for a useful window is the right scale for the AFFINITY route — and why the cooperativity route would need far less margin if its instrument worked. It does not: the ternary cooperativity calculator returned the WRONG SIGN in all three replicates at ~34x its own uncertainty, and the closure triangle localised the miss to an endpoint-state error that more sampling will not fix.
- **A pass would license:**
  - a degradation window from cooperativity alone — the model gives 7.9x DC50 at zero binary margin
- **⛔ A pass would NOT license:**
  - anything today. valB_full's module 1 has failed and the decision declined to amend or decouple it, so the prospective NR4A ternary matrix stays unrun and cooperativity claims stay exploratory.
- **Why this grade.** Leverage A, instrument F. This row is the clearest case in the register where the size of the prize must not be allowed to raise the grade — and it is the reason the whole prospective tail is blocked.

### `S14` ★ Conformational-selection selectivity — differential cryptic-pocket opening — grade **D**

**Status:** CATEGORICAL FORM REFUTED HERE; quantitative form is requirement R6  ·  **NEW test of an old assumption**

- **Physical basis.** a binder requiring the open state is selective if the paralogues open less readily
- **Instrument.** V13 (metadynamics F(Rg)) — its only demonstrated reading is in the closed-route register
- **Known-answer test in the needed regime?** NO. Gate 1 FAILED as registered; three seeds do not reconstruct a common F(Rg).
- **Could a valid positive control exist here?** ⛔ Not with this instrument. The cross-replica failure is a reproducibility failure, which no positive control repairs.
- **Cheapest decisive test.** $0 — taken here (M5)
- **Measured here.** THE CATEGORICAL FORM IS DEAD ON COMMITTED DATA. Both paralogues reach NR4A3's druggable CV value (Rg = 0.717 nm) inside their own matched metadynamics — NR4A1 exactly, NR4A2 within 0.004 nm — and in the opened frames fpocket rates NR4A1 (0.981) MORE druggable than NR4A3 (0.931). 'Only NR4A3 has the cryptic site' is not available as an argument.
- **A pass would license:**
  - nothing in the categorical form
- **⛔ A pass would NOT license:**
  - ⛔ 'only NR4A3 has the cryptic pocket'. Both paralogues reach NR4A3's druggable CV inside their own matched metadynamics, and fpocket rates NR4A1's opened frame MORE druggable (0.981) than NR4A3's (0.931).
- **Why this grade.** Filed so it is not re-proposed. The quantitative version is not dead — it is R6, a requirement with NO instrument, held on an explicit nod, and the one term validation requirement 2 says can REVERSE the margin. Reporting everything conditional on the open state remains $0 and fully defensible.

### `S2` Divergent pocket handles resolved by free energy (Route A) — grade **D**

**Status:** BLOCKED  ·  **current**

- **Physical basis.** 7 of 10 Pocket-5 lining residues are paralogue-divergent and all 10 are ortholog-invariant.
- **Instrument.** V4 (selectivity ABFE) — never run; V7 (absolute ABFE) FAILS by ~7.1 kcal/mol
- **Known-answer test in the needed regime?** NO. No instrument in this program has ever recovered a known selectivity ddG across two pockets. V6 passes WITHIN one pocket and one charge model; V10 passes on a LARGE effect.
- **Could a valid positive control exist here?** YES and it is built — CREBBP vs BRD4(1)/SGC-CBP30, same ligand, two holo crystals, experimental ddG ~2.2 kcal/mol. It is not authorized, and even a clean pass would be a BINARY control that would not discharge the paralogue/ternary statement.
- **Cheapest decisive test.** not $0 — it is the V4 benchmark, unpriced and on no rung
- **A pass would license:**
  - that the free-energy engine can resolve selectivity between two proteins
- **⛔ A pass would NOT license:**
  - the NR4A3 paralogue margin — a passing instrument does not supply R6 (dG_open per paralogue), which validation requirement 2 says can MISS OR REVERSE selectivity
  - closing the size-of-prize gap: ~2.0 kcal/mol needed against ~0.60 best-case resolvable
- **Why this grade.** Three independent blocks and only one is the instrument. Graded down further by lesson 2: the whole claim reduces to a ~1 kcal/mol ddG in exactly the regime nothing here is validated in.

### `S8` E3 recruiter choice as a selectivity lever — grade **D**

**Status:** BLOCKED — not by capability but by measurement precision  ·  **current**

- **Physical basis.** different recruiters give different ternary interfaces and different lysine reach
- **Instrument.** the orientation-basin search, per arm
- **Known-answer test in the needed regime?** NO — and worse, the readout is not stable under a nuisance variable.
- **Could a valid positive control exist here?** In principle yes (a target with published VHL-vs-CRBN degradation selectivity), but it is moot until the staging precision problem is fixed.
- **Cheapest decisive test.** $0 — taken here (M6)
- **Measured here.** EVERY APPARENT E3 PREFERENCE MEASURED HERE HAS TRACKED THE STAGING CONSTRUCTION RATHER THAN THE RECRUITER. Changing only how the E3 arm is assembled — composed vs assembly-native, no change to recruiter, sampling or criteria — moves CRBN's any-lysine null from 0.760-0.980 to 0.320-0.445 while VHL's barely moves, swings VHL's maximum term-(b) enrichment 16.60 -> 6.07, and takes the term-(a) count 0 -> 2. The roadmap already records the one E3-preference claim this program made ('the discrimination lives on VHL') as RETRACTED the same day, for exactly this reason. A recruiter preference is not measurable at the current staging precision.
- **A pass would license:**
  - nothing today
- **⛔ A pass would NOT license:**
  - any recruiter preference. The program's one E3-preference claim was retracted the same day it was made, and the numbers still swing 2-3x on staging construction alone.
- **Why this grade.** A measured instability, not an untested hope: the answer changes more with how the arm is assembled than with which arm it is. Reopening it needs a staging precision argument first, and that is a methods problem with no rung.

### `S9` Kinetic / residence-time selectivity — grade **D**

**Status:** NO INSTRUMENT — and the nearest one has already failed on a simpler quantity  ·  **current**

- **Physical basis.** equal Kd with unequal k_off gives unequal occupancy under washout, and degradation is a kinetic readout
- **Instrument.** nothing in this repo computes k_off, residence time or an unbinding barrier. The only classes that could are infrequent-metadynamics / weighted-ensemble unbinding.
- **Known-answer test in the needed regime?** NO, and the prior is bad: the program's metadynamics on a much simpler CV failed cross-replica reproducibility outright — three independent seeds do not reconstruct a common F(Rg), which is in the closed-route register. A k_off estimate needs strictly more convergence than that.
- **Could a valid positive control exist here?** YES in the literature (residence-time series with measured k_off exist), but building the instrument is a multi-month methods project with a known-hard convergence problem, on a cryptic induced-fit pocket — the exact regime the closed-route register already parked Track A for.
- **Cheapest decisive test.** none is cheap. The honest answer is that nothing here could test it.
- **A pass would license:**
  - n/a
- **⛔ A pass would NOT license:**
  - n/a
- **Why this grade.** Enumerated for completeness and for the record that it was considered and costed as unbuildable here.

---

## What this changes about the plan

- **Nothing here amends a preregistration, a gate or a plan.** It is an options register; trimcrae chooses. The roadmap remains the single steering document and no row below is scheduled by this file.
- `S3` (steric exclusion) and `S11` (non-cysteine categorical handles) are **new candidate rows for the roadmap's ordered list**, both at $0, both needing a rung/gate/price they do not have.
- `S15` (anti-handle avoidance) is **free and strictly tightens every other row** — the enumeration currently optimises reach TO C397 and only reports paralogue closure afterwards, rather than carrying the anti-handle set as a constraint.
- `S8` (E3 choice) and `S14` (conformational selection) should be recorded as **closed in their categorical form**, so they are not re-proposed. Neither belongs in the DEAD register: `S14`'s quantitative form is requirement `R6`, and `S8` needs a staging-precision argument, not a retry.
- `S12` (fusion-junction) is the register's **highest ceiling and lowest readiness**, and it maps exactly onto the roadmap's `R13` hole — which has no rung, gate or price anywhere in the program. Its $0 form (a sequence-level junction uniqueness and lysine inventory) needs no structure.
- **The grading rule applied throughout:** leverage never raises a grade. `S10` (cooperativity) has the highest leverage of any mechanism measured here — 7.9× DC50 separation at zero binary margin — and is graded **D**, because the control for its instrument was available, was run, and refuted it.

---

## ⛔ Scope of this document

- Nothing here is a claim about binding, affinity, reactivity, degradation, efficacy, safety, a therapeutic window or clinical readiness. None of those is computed anywhere in this file.
- No claim of proteome-wide selectivity is made or implied. The comparison set throughout is NR4A1 and NR4A2, and the program's own scope is separately bounded by an unrun AR/MR cross-binding check.
- Grades rank mechanisms against each other for PLANNING. A grade is not evidence, and an A- row is still an unvalidated prediction under the roadmap's claim-ceiling rule.
- Every measurement is conditional on the artifacts it reads, including the docked poses (whose known-answer test returned INCONCLUSIVE on site selection) and the matched opened models.

*Generated 2026-08-02 7:28 PM ET by `selectivity_mechanism_options.py`.*
