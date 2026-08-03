# The NR4A1-SPARING axis — the inverse of NR-V04, enumerated and measured

> **The question, from trimcrae:** *"Is there anything to the idea of doing the inverse of NR-V04 here? Like making something that will degrade every NR4A paralogue EXCEPT NR4A1 using the same mechanism as NR-V04 but in reverse?"*

**Generated** 2026-08-02 10:03 PM ET by `research/modalities/nr4a1_sparing_axis.py` — MEASURED at $0 — CPU only: cached UniProt sequences, committed opened models, committed docked poses. No GPU, no rental, no dispatch, no network. Nothing here is a claim about binding, reactivity, degradation, efficacy, safety or clinical readiness.

⚠ **Every number below is rendered from [`nr4a1-sparing-axis.json`](nr4a1-sparing-axis.json).** This file is a reading of that artifact, never a second home for any figure.

---

## ⛔ First, what does NOT work — the covalent mechanism does not invert

NR-V04 achieves NR4A1 selectivity by covalently labelling **NR4A1 Cys551**, a residue NR4A2 and NR4A3 do not carry at the aligned position (NR4A3 has T579). That is POSITIVE selection on a PRESENCE. Sparing NR4A1 requires selecting on an ABSENCE — and an electrophile cannot label a residue that is not there.

**So:** there is no 'NR-V04 in reverse' as chemistry, and no amount of warhead engineering creates one. Any NR4A1-sparing design must use a NON-covalent mechanism. This is stated plainly so the idea is not re-proposed as a covalent one.

⚠ the CATEGORICAL logic survives — 'a residue the other proteins do not have' is still a set-membership fact rather than an energy difference. What changes is which observable can read it: a bond cannot, a SHAPE can. That is why the measured half of this file is steric.

## The answer

PARTLY. ⛔ The COVALENT mechanism does not invert and there is no version of it that does — NR-V04 selects positively on NR4A1 Cys551 and sparing NR4A1 means selecting on an ABSENCE, which no electrophile can do. ★ A DIFFERENT mechanism does invert: steric exclusion (S3) needs a bulkier side chain rather than a labelable one, and bulk is a property NR4A1 can have uniquely. That axis is measured here for the first time, and the measurement is thin.

- **Measured or speculative?** MEASURED, at $0, with its matched null and both controls — and the measurement is what makes it thin rather than promising. Nothing here is a projection or an intention.
- **The axis in one line:** 58 alignment-robust NR4A1-unique-vs-BOTH LBD positions exist (against 68 for NR4A3, so the reciprocal set is comparably large and the idea is not vacuous), but at the pocket the signal class is [407] and over the whole ligand-envelope lining set it is [407, 487, 525].
- **Recommended register state:** ⏸ PARKED — the axis is not empty — NR4A1-unique-and-bulkier pocket-lining positions EXIST — but the signal class fires at or BELOW its own matched null (0.0 vs 0.038 at the pocket, 0.077 vs 0.08 over the lining envelope), and the inverted denied lobe clears no measured volume ceiling. ⛔ This is ⏸ and not ✕ on purpose. §6's bar for ✕ is POSITIVE EVIDENCE OF IMPOSSIBILITY, and what is measured here is a null result on ONE static conformer per species — an instrument statement. The conformer-INDEPENDENT half (no NR4A1-unique lining position exceeds a +1 heavy-atom bulk margin) points at ✕ and is a fact about the protein, but +1 is not zero and the lining set itself is model-dependent, so it does not reach the bar on its own. 'We looked and found nothing promising' is explicitly not ✕.

> ★ The forward (NR4A3-selective) steric test fires at 5.34x its own null. The inverse (NR4A1-sparing) test fires at 0.96x its own null over the same frame, the same 13 poses and the same hard_clash_A. The mechanism does not invert on this protein — not because nobody looked, but because it was looked at with the matched control and came back at the null.

★ **The structural reason, and it is conformer-independent.** In the S3 (NR4A3-selective) direction the best pocket margin is +4 heavy atoms at position 484 (I -> Y/Y) — most of an aromatic ring of extra bulk. In the NR4A1-sparing direction the best margin ANYWHERE in the pocket or its lining envelope is +1, at 407 (T -> L/V), and every position in the signal class sits at that same +1. That is the structural reason the inverse fires at its own null while the forward fires well above it: NR4A1 is not BULKIER than its paralogues anywhere that matters — it is DIFFERENT from them, which uniqueness captures and steric exclusion cannot use.

⚠ **The one cell that does fire above null:** NR4A3 N487 / NR4A1 K456 / NR4A2 N456 — 3 of 13 poses, bulk margin +1 heavy atom. one position out of 31 in the lining set, 13 poses, a +1 heavy-atom margin, and it is selected POST HOC as the largest of the signal class — the multiplicity that makes a per-position rate uninterpretable is exactly why the CLASS rate carries the verdict and a cell does not. It is named rather than dropped because a sweep that reports only what survives is a sweep nobody can grade.

## 1 · The reciprocal enumeration — which positions are unique to which paralogue, against BOTH others

nr4a_paralogue_unique_residues.classify_positions with `ref` set to each species in turn, `others` set to the other two, and residue_types widened from the committed ('C','K') to all 20. Uniqueness is a claim ABOUT AN ALIGNMENT, so it is computed twice with independent aligners (linear-gap NW + affine-gap BLOSUM62) and only `unique_vs_both AND alignment_robust` rows are admitted — identical to the forward enumeration, which is what makes the two comparable.

| species | positions scanned | unique vs BOTH (alignment-robust) | of those, in the LBD |
|---|---|---|---|
| **NR4A1** (P22736) | 598 | 164 | **58** |
| **NR4A2** (P43354) | 598 | 126 | **48** |
| **NR4A3** (Q92570) | 626 | 174 | **68** |

### NR4A1-unique LBD positions that LINE the pocket envelope

*(the full 58-position list is in the JSON; this table is the subset the steric test can act on)*

| NR4A3 frame | NR4A3 | NR4A1 | NR4A2 | NR4A1 heavy atoms vs NR4A2 / NR4A3 | class |
|---|---|---|---|---|---|
| 407 | T407 | L373 | V373 | 4 vs 3 / 3 | `nr4a1_unique_and_bulkier` |
| 410 | T410 | G376 | N376 | 0 vs 4 / 3 | `nr4a1_unique_not_bulkier` |
| 412 | R412 | A380 | T380 | 1 vs 3 / 7 | `nr4a1_unique_not_bulkier` |
| 487 | N487 | K456 | N456 | 5 vs 4 / 4 | `nr4a1_unique_and_bulkier` |
| 525 | Q525 | H494 | Q494 | 6 vs 5 / 5 | `nr4a1_unique_and_bulkier` |
| 528 | N528 | L497 | N497 | 4 vs 4 / 4 | `nr4a1_unique_not_bulkier` |
| 529 | L529 | V498 | I498 | 3 vs 4 / 4 | `nr4a1_unique_not_bulkier` |
| 531 | I531 | V500 | I500 | 3 vs 4 / 4 | `nr4a1_unique_not_bulkier` |

## 2 · The steric test, run in the NR4A1-only direction

Are there positions where NR4A1's side chain is strictly bulkier than BOTH NR4A2's and NR4A3's, and where that bulk lines the pocket — i.e. a lobe NR4A1 alone denies?

13 committed NR4A3-docked poses against the shared frame (results/nr4a3-matrix/nr4a3-opened.pdb; paralogues superposed by nr4a3_basin_search.superpose_paralogue). A position clashes when its side-chain heavy atoms come within 3.0 A of a ligand heavy atom — the same hard_clash_A M3 used. The NR4A1-ONLY predicate is: NR4A1 clashes AND NR4A2 does not AND NR4A3 does not.

⚠ Exactly as in M3: a rate without its matched null is not a result. The null is the same predicate evaluated at conserved-or-shared positions, where no categorical difference exists and any firing is a measured false positive of the superposition.

**Pocket-5, matched to `M3`** — 10 positions × 13 poses

| class | positions | hits / trials | rate |
|---|---|---|---|
| `nr4a1_unique_and_bulkier` | [407] | 0 / 13 | **0.0** |
| `nr4a1_unique_not_bulkier` | [410, 412, 531] | 0 / 39 | **0.0** |
| `conserved_or_shared` | [406, 411, 481, 484, 485, 534] | 3 / 78 | **0.038** |

signal − null = **-0.038** · enrichment = **None**

**ligand-envelope lining set** — 31 positions × 13 poses

| class | positions | hits / trials | rate |
|---|---|---|---|
| `nr4a1_unique_and_bulkier` | [407, 487, 525] | 3 / 39 | **0.077** |
| `nr4a1_unique_not_bulkier` | [410, 412, 528, 529, 531] | 0 / 65 | **0.0** |
| `conserved_or_shared` | [403, 406, 409, 414, 416, 448, 451, 477, 480, 481, 484, 485, 490, 494, 521, 524, 527, 530, 534, 535, 538, 575, 577] | 24 / 299 | **0.08** |

signal − null = **-0.003** · enrichment = **0.96**

### ⛔ The forward-direction self-check — proof the null is not a bug

a null result is indistinguishable from a broken measurement, so the same code path is run with M3's forward predicate and compared to the committed M3 rates

| class | recomputed here | committed `M3` |
|---|---|---|
| `unique_and_both_bulkier` | 0.923 | 0.923 |
| `conserved_or_shared` | 0.173 | 0.173 |

**Reproduces committed `M3`: YES.** 

### The inverted denied lobe

the sub-volume a ligand heavy atom may occupy in NR4A3 AND at NR4A2's residue, and may NOT occupy at NR4A1's — the S3 design-rule lobe with the roles inverted. Computed by steric_design_rule.denied_lobe, reused unchanged.

Measured volume ceiling from the null class: **23.81 Å³** at position 484. Design targets clearing it: **none**.

| NR4A3 frame | NR4A3 / NR4A1 / NR4A2 | class | lobe Å³ | clears the bar |
|---|---|---|---|---|
| 406 | L / H / H | `conserved_or_shared` | 18.5 | — |
| 407 | T / L / V | `nr4a1_unique_and_bulkier` | 0.32 | — |
| 410 | T / G / N | `nr4a1_unique_not_bulkier` | 0.0 | — |
| 411 | P / P / P | `conserved_or_shared` | 0.13 | — |
| 412 | R / A / T | `nr4a1_unique_not_bulkier` | 23.55 | — |
| 481 | R / R / R | `conserved_or_shared` | 8.32 | — |
| 484 | I / Y / Y | `conserved_or_shared` | 23.81 | — |
| 485 | R / R / R | `conserved_or_shared` | 4.48 | — |
| 531 | I / V / I | `nr4a1_unique_not_bulkier` | 17.47 | — |
| 534 | L / F / F | `conserved_or_shared` | 10.18 | — |

## 3 · The controls — and why one of them is the whole story here

- **★ the relocation control is this axis's central problem not a footnote** — M4 measured that the paralogue's OWN docking relocates the same molecules rather than reproducing the pose: median centroid shift 5.31 A (NR4A1), 5.26 A (NR4A2). For S3 that caps a claim at 'this POSE is denied', which a design rule can live with. An NR4A1-SPARING claim cannot: sparing requires NR4A1 not to be engaged AT ALL, and a molecule that binds NR4A1 5.3 A away in a different sub-site may still recruit an E3 and be degraded there. A steric result in this direction therefore licenses strictly LESS than the same result licenses for S3.
- **⚠ construction bias and why the contrast survives it** — The 13 poses were docked INTO NR4A3, so 'NR4A3 does not clash' is guaranteed by construction and carries no information — and the NR4A1-only predicate contains that free term. The bias inflates every class IDENTICALLY, so the signal-vs-null CONTRAST remains gradeable and the absolute rate does not. Grade the contrast, never the rate. (Identical to M3's own limit, inherited whole.)
- **⚠ rigid transfer** — NR4A1's side chain is held in its own opened conformer and could rotate away. This measures 'clash in NR4A1's modelled conformer with the ligand held fixed', never 'NR4A1 cannot bind'.
- **⚠ the NR4A2 half is NOT construction guaranteed and that is the one real signal** — Of the three species in the predicate, only NR4A2's non-clash is a free measurement — NR4A3's is by construction and NR4A1's is the thing being tested. So the informative content of any firing cell is 'NR4A1 clashes where NR4A2 does not', and that is how it must be read.
- **⚠ a single static conformer per species** — One opened model each. The forward pocket-detection contrast was replicated over matched unbiased ensembles (paralogue-pocket-contrast.json); nothing here is.
- **⚠ no p value is computed and that is deliberate** — Cells are not independent: positions within one pose share the same superposition and the same ligand, and poses share the same three models — the spatial-correlation caveat Route A already carries. A rate is reported against its matched null and nothing is converted into a test. The verdict does not need one: the signal is AT the null, not near a threshold.
- **⛔ no energy is computed anywhere in this file** — no affinity, no ddG, no selectivity ratio, no degradation, no efficacy, no safety, no therapeutic window, no clinical readiness, and no proteome-wide selectivity of any kind — the comparison set is three paralogues.

## 4 · The therapeutic trade, both halves

⚠ Every figure below is READ from research/modalities/nr4a2-sparing-bound.json at generation time. This is a citation, not a second home.

**What the profile BUYS**

- `Nr4a1 + Nr4a3` — 21 annotations, survival terms ['postnatal lethality, complete penetrance'] (PMID 17515897). this is the named mouse AML genotype a NON-selective NR4A3 degrader reconstitutes, and it is the whole reason roadmap §2.4 calls the NR4A1 half MANDATORY. A molecule that spares NR4A1 cannot reconstitute it.
- NR4A1 single-gene MGI: 8 annotations, survival terms **none**. 0 survival/viability terms on 8 single-gene annotations. ⛔ THIS IS NOT A LICENCE — an absent record is an absence of evidence. It is stated because the asymmetry runs the other way from intuition: the mandatory anti-target is mandatory because of a COMBINATION, not because its own null is severe.

**What the profile COSTS**

- **NR4A2 single null is lethal with complete penetrance** — the paralogue this profile DEGRADES is the one whose own single knockout is neonatal-lethal at complete penetrance — while the paralogue it SPARES has no survival term at all. The trade buys the combination and pays on the single.
- **a conditional deletion lands closer to a degrader and is still lethal** — a dopaminergic-restricted (Slc6a3/DAT-Cre) Nr4a2 deletion — tissue-restricted and post-developmental, i.e. the closest genotype on record to what a degrader does — still carries 'lethality at weaning, complete penetrance' with neuron degeneration and decreased dopamine. ⛔ Still a genetic deletion, still complete and still lifelong within its lineage; a degrader is partial and reversible.
- **tissue distribution cannot rescue it** — NR4A2 and NR4A3 are co-expressed in 47 of 51 HPA tissues and NR4A2 is the dominant family member in 0, so there is no tissue window in which degrading NR4A3 reaches NR4A2 less. ⛔ AND THE CONVERSE MISREADING IS FORBIDDEN by that artifact: a bulk average dilutes the substantia nigra to invisibility, so this measures exposure breadth and not the dopaminergic requirement.

⚠ **The combination IS on record and carries NO survival/viability term — and that is NOT evidence of tolerability, for a reason visible in the genotype string itself: the annotated animal is Nr4a2 HETEROZYGOUS (Nr4a2<tm1Tpe>/Nr4a2<+>) with Nr4a3 homozygous null. A double NULL of Nr4a2 and Nr4a3 has no MGI record at all. So the comparison is not 'Nr4a1;Nr4a3 is lethal and Nr4a2;Nr4a3 is not' — it is 'one double null is phenotyped as lethal and the other has never been reported'. AN ABSENT READING IS NOT A READING OF ABSENCE (CLAUDE.md §4).**

**In one sentence:** Sparing NR4A1 removes the one genotype the program treats as disqualifying — the AML double null — and it removes it BY CONSTRUCTION rather than by a margin any instrument here can resolve; but the profile it buys degrades the paralogue whose own single knockout is neonatal-lethal at complete penetrance, in a tissue distribution that offers no window, against a double-null genotype nobody has reported. This file does not decide that trade.

## 5 · What already existed, and what is new

**Already committed:**

- `research/modalities/nr4a-paralogue-unique-residues.json` → `reciprocal_paralogue_unique` — PAIRWISE reciprocal uniqueness: positions where a paralogue carries a Cys or Lys and NR4A3 does not, one paralogue at a time. NR4A1 14 rows, NR4A2 5 rows, whole sequence.
  - ⛔ could not answer: it is not 'unique vs BOTH'. 2 of NR4A1's rows are shared with NR4A2 at the same position (C534, K558), so they are NOT NR4A1-unique and cannot support an NR4A1-sparing design. It is also restricted to two residue types, and a steric argument needs all twenty.
- `research/modalities/nr4a3-linker-covalent-reach.json` → `paralogue_control.reciprocal_uniqueness` — the beginning of the reciprocal set, as named in the task: NR4A1 C551 -> NR4A3 T579 and NR4A1/NR4A2 C534 -> NR4A3 S565.
  - ⛔ could not answer: same two limits, plus it is scoped to the chemoselectivity WINDOW (which cysteine closes a linker's reach envelope first), not to a design axis. And C534 is present in BOTH paralogues, so of the two named sites only C551 is NR4A1-unique at all.
- `research/modalities/categorical-axis-audit.json` → `residue_identity` — the correction that keeps this honest: NR4A1 C505 aligns to NR4A3 C536, so it is NOT a reciprocal-uniqueness site, and naming 'C534' alone mislabels the majority through-space closer.
  - ⛔ could not answer: it audits the pairwise set; it does not compute a vs-both one.
- `research/modalities/selectivity-mechanism-options.json` → `measurements.M3 / mechanisms S3` — the steric-exclusion measurement and its null, in the NR4A3-selective direction only (both paralogues bulkier than NR4A3).
  - ⛔ could not answer: the NR4A1-only direction was never evaluated — M3's predicate requires BOTH paralogues to clash, which by construction can never fire on an NR4A1-specific bulge.

**Computed here for the first time:**

- the vs-BOTH reciprocal set for NR4A1 over all 20 residue types under the two-aligner robustness rule — 58 alignment-robust NR4A1-unique positions in the LBD
- the same enumeration for NR4A2 and NR4A3 as denominators, so the NR4A1 count can be graded
- the NR4A1-ONLY steric clash rate, with the matched null and the uniqueness-alone control, over the same 13 poses and the same hard_clash_A M3 used
- the same measurement over the ligand-envelope lining set rather than fpocket's 10 residues, using a union-over-species lining definition
- the inverted denied lobe (occupiable in NR4A3 and at NR4A2's residue, denied at NR4A1's) with its own measured volume ceiling

⚠ Every uniqueness enumeration in this repo ran NR4A3-first. The reciprocal fragments that existed were pairwise-against-NR4A3 and Cys/Lys-only, which is the wrong shape for an NR4A1-sparing design: that design needs positions NR4A1 does not SHARE WITH NR4A2, because a feature NR4A2 also carries cannot spare one and degrade the other.

## 6 · Reconciliation with the mechanism register

- **vs `S15`** — different observable — S15 is covalent reach to a reactive residue; this is steric occlusion by side-chain volume, and the two sets barely intersect (a Cys is small, and this axis needs bulk) **DISTINCT. It is not S15 measured for the first time — S15 is already measured (the closure data is committed, 30 of 30 graded cells). A new number is warranted.**
  - different pairwise structure — S15's set is 'paralogue has it, NR4A3 lacks it' and includes positions NR4A1 SHARES with NR4A2 (C534, K558), which are useless here by construction
  - different target product — S15 improves an NR4A3-selective degrader; this describes a pan-NR4A-except-NR4A1 degrader, which is a different molecule with a different brief
  - opposite sign on the same protein — S15 says AVOID NR4A1's unique residues; this says SEEK one and design INTO the space around it
- **vs `S3`** — SAME MECHANISM CLASS, DIFFERENT DIRECTION AND DIFFERENT TARGET PROFILE. It must not be folded into S3's row: S3's rate (0.923/0.173) answers 'can NR4A3 be selected positively', and merging a second predicate into that row would put two measurements behind one number.
- **Proposed id:** `S18` — ★ Inverse steric exclusion — an NR4A1-unique bulge that denies NR4A1 the pose (the 'pan-NR4A except NR4A1' profile)
- ⛔ selectivity-mechanism-options.json is GENERATED by selectivity_mechanism_options.py and regenerating it rebuilds M1-M7 as well. The row is proposed here with its measurement already owned by this artifact; whoever adds S18 must IMPORT these numbers, never re-type them.

## 7 · A defect found on the way

`research/modalities/selectivity-mechanism-options.json` → `measurements.M3.positions.*.partners.<paralogue>[1]`: the paralogue residue NUMBERS are labelled with NR4A3's local offset (372) instead of the paralogue's own (348 for NR4A1, 344 for NR4A2), so every one is high by 25 (NR4A1) / 29 (NR4A2): M3 reports NR4A3 L406's NR4A1 partner as 'H, 397' where the residue is H372.

- **Why it matters:** the wrong numbers name REAL residues of the same protein — NR4A1 397 is a lysine that appears in this repo's own reciprocal list — so the field reads as measured and is not. CLAUDE.md §4: a populated field is not a measured one.
- **Blast radius:** NONE for any conclusion. Every downstream use quotes the residue LETTERS (L406->His/His, I484->Tyr/Tyr, L534->Phe/Phe), which are correct, and steric-design-rule.json carries letters only.
- **Fix:** selectivity_mechanism_options.m3_steric_exclusion line `(rp + U.LOCAL_OFFSET)` must use the paralogue's own recovered offset — nr4a1_sparing_axis.uniprot_offset() derives it from the model sequence rather than hard-coding it. Not applied here: regenerating that artifact rebuilds M1-M7 and it is owned by another lane.

## ⛔ Limits

- SEQUENCE UNIQUENESS IS EXACT; EVERYTHING ELSE IS A HYPOTHESIS. The vs-both enumeration is a fact about two alignments of three FASTA sequences. The steric measurement is a fact about three static models and 13 poses.
- ONE STATIC OPENED CONFORMER PER SPECIES, rigidly transferred. A rotamer modelled away here could be a real bulge, and vice versa.
- THE POSES WERE DOCKED INTO NR4A3, so 'NR4A3 does not clash' is free. Only the class contrast is gradeable — never the absolute rate.
- CONDITIONAL ON R5. The whole pocket-level analysis assumes the cryptic pocket is the right site, and the pose known-answer test V3 returned INCONCLUSIVE.
- NO ENERGY, ANYWHERE. No affinity, ddG, selectivity ratio, degradation, efficacy, safety, therapeutic window or clinical readiness is computed or implied, and no proteome-wide selectivity of any kind is claimed — the comparison set is three paralogues.
- THE THERAPEUTIC TRADE IS CITED, NOT DECIDED. Germline and lineage knockouts bound developmental loss; a degrader is adult, transient and incomplete.

