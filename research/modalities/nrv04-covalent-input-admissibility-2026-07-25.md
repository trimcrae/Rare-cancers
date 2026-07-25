# NR-V04 covalent panel — can an A1-admissible input be produced? (Lane 8, 2026-07-25)

**Question put to this lane.** Prereg [AMENDMENT 1](./nr4a3-nrv04-covalent-feasibility-prereg.md#amendment-1--2026-07-25-dated-defect-fix-trimcrae-delegated)
added binding criterion **A1**: a leg declared covalent must stage its electrophilic carbon within
`MAX_COVALENT_TETHER_A` (8.0 Å) of the **target-chain** Cys Sγ, against a ~1.8 Å C–S bond. It recorded A1
failing at **8.99 Å** (`cov_nr4a1`) and **16.39 Å** (`warhead_only`), and left the panel `[HELD]` with the
note that unblocking needs *input* work: *"re-fold the covalent systems … or drop the covalent legs and
re-scope — and say which."* This lane was asked to produce an admissible input or establish that it cannot be
produced, and to say which.

**Answer: no admissible input exists, and the reason is not the one the amendment recorded.** The 8.99 Å is
the distance to the **wrong cysteine**. Measured at the preregistered covalent site — NR4A1 **Cys551** — the
best co-fold in the entire bucket is **28.42 Å**, and the range across every clean model is **28.42–39.11 Å**.

**Recommendation: RE-SCOPE. Drop the covalent legs.** Reasoning in §5; the alternative (a steered re-fold) is
built and costed in §6 and is *not* recommended as the first move.

Total spend: **$0**.

| # | finding | evidence |
|---|---|---|
| 1 | **A1 has been measuring the wrong residue.** The 8.99 Å belongs to **C566**; the frozen site **C551** is 28.4–39.1 Å away in every clean model | `nrv04-covalent-input-audit.json`, 7 clean models, LBD↔full-length map fetched from UniProt (598 aa, residue 551 = Cys) |
| 2 | **"any co-fold in the bucket" had never been enumerated** — the pre-spend check samples **one** model per system out of an ensemble | `nrv04_prespend_check._pull_model` = `sorted([k for k in keys if k.endswith("_model_0.cif")])[0]` |
| 3 | **The miss is systematic, not seed noise** — 5 independent diffusion seeds across 4 prefixes, C551 distance 28.4–39.1 Å, never below 26.8 Å to *any* buried cysteine | audit table, §2 |
| 4 | **The repo had already measured this and not connected it** — `celastrol-end→Cys551 SG proxy = 27.4 Å`, recorded as a PASS of a review item | `nrv04-ternary-benchmark.json` → `review_fix_verification.5_cys551_evaluated` |
| 5 | **The warhead is not in the target pocket at all** — the celastrol moiety makes **more** contacts with the E3 machinery than with NR4A1 (40–135 vs 32–44); for free celastrol it is 135 vs 44 | audit `warhead.contacts_*`, §3 |
| 6 | **`cov_c551a` was mutating C566, not C551** — the same geometric rule picks the mutation site | `nrv04_covalent_md.build_system` (fixed here) |

---

## 1. What A1 actually measured, and why that is not what it says

A1's text is *"the celastrol electrophilic carbon must sit within bonding distance of the **target-chain** Cys
Sγ."* Its implementation is `nrv04_covalent_md._reactive_cys_by_geometry`, which returns the **nearest**
cysteine on the target chain. Those are different questions whenever the target chain has more than one
cysteine — and the NR4A1 LBD construct has **six**: C465, C475, C505, C534, **C551**, C566.

The preregistered covalent site is **C551** (`nrv04_covalent_panel.TARGET_COV_RESNUM = 551`, confirmed a
cysteine by Leg 0). It is also the experimentally established one:

> Zhang, D. *et al.* "Celastrol binds to its target protein via specific noncovalent interactions and
> reversible covalent bonds." *Chem. Commun.* **2018**, 54, 13000–13003. doi:10.1039/C8CC06140H
> (PMID 30376017). Celastrol is positioned by specific *noncovalent* interactions next to the **C551** thiol
> and then forms a **reversible** covalent bond. Of the six Nur77-LBD cysteines, C475/C505/C534 are buried,
> C465/C566 partially solvent-exposed, and **C551 highly exposed**.

The number A1 recorded is the distance to **C566**. Converting is one subtraction: NR4A1 (P22736) is 598 aa
and the frozen construct is its C-terminal 254 residues (`nr4a3_ternary.lbd_seq` → `full[-254:]`), so the
offset is 344 and co-fold residue **222 = C566**, **207 = C551**. The panel's own legs recorded
`reactive_cys = chain A resid 222` — C566 — throughout.

This is the **third instance of one defect class** in this driver, after the positional E3/target split and
the all-chain reactive-cysteine search: *a selection rule that ignores the dimension the data varies along,
and therefore returns a confident answer about the wrong thing.* Here the ignored dimension is **which
cysteine the chemistry actually uses**.

## 2. The exhaustive measurement

[`nrv04_covalent_input_audit.py`](./nrv04_covalent_input_audit.py) →
[`nrv04-covalent-input-audit.json`](./nrv04-covalent-input-audit.json). Every model CIF under every co-fold
prefix in the bucket — 13 prefixes, **34 models** — measured with the same template kernel the assembler uses
and the same frozen electrophile definition (`nrv04_ligands.electrophile_atom_index`).

27 of the 34 are rejected before measurement by the assembler's own contaminant rule (14-3-3 epsilon where
Elongin B belongs: `nrv04-descriptive-v3`, `nrv04-shakeout`, `nrv04-smoke-restart`, `nrv04-ternary-pilot`).
The **7 clean models** are the whole admissible universe:

| prefix | system | seed | nearest target Cys | **C551 Sγ → electrophile** | A1 |
|---|---|---|---|---|---|
| `nrv04-covalent-cofold` | `nr4a1` | 0 | C566 @ **8.99 Å** | **28.46 Å** | ✗ |
| `nrv04-covalent-cofold` | `neg_inactive` | 0 | C566 @ 8.87 Å | **28.42 Å** | ✗ |
| `nrv04-covalent-cofold` | `neg_celastrol` | 0 | C566 @ 16.39 Å | **36.43 Å** | ✗ |
| `nrv04-descriptive-v4` | `nr4a1` | 1 | C475 @ 18.83 Å | **34.42 Å** | ✗ |
| `nrv04-descriptive-v4` | `nr4a1` | 2 | C566 @ 10.17 Å | **29.87 Å** | ✗ |
| `nrv04-descriptive-v4` | `nr4a1` | 3 | C566 @ 18.62 Å | **39.11 Å** | ✗ |
| `nrv04-cofold-vast-shakeout` | `nr4a1` | 1 | C475 @ 19.13 Å | **34.66 Å** | ✗ |

Two things this settles that a sample of one could not:

- **The amendment's "in any co-fold currently in the bucket" was an extrapolation.**
  `nrv04_prespend_check._pull_model` selects `sorted([k for k in keys if k.endswith("_model_0.cif")])[0]` —
  one model per system. The conclusion happens to be right; the evidence for it did not exist until now.
- **The miss is systematic.** Five independent diffusion seeds across four prefixes span 28.4–39.1 Å at C551
  with no trend toward it. This is not a sampling problem that more seeds fix.

The repo had *already* measured this and filed it as a pass: `nrv04-ternary-benchmark.json` records
`"5_cys551_evaluated": "PASS — cys551_evaluated=True; celastrol-end→Cys551 SG proxy=27.4 Å"`. That 27.4 Å is
the same observation, on a different model, recorded as a satisfied review item rather than as a fact that
makes the covalent panel unbuildable.

## 3. Where the warhead actually is — and why this is worse than a near-miss

The audit separates the ligand into its **celastroyl warhead** and its **VH032 recruiter** fragments
structurally (free celastrol is *not* a substructure of NR-V04 — its C-28 acid is consumed into the linker
amide — so the naive substructure match silently returns nothing; the warhead is instead defined as the
fragment carrying the electrophile after every amide C–N bond is cut).

| model | warhead ↔ NR4A1 contacts (4.5 Å) | warhead ↔ E3 contacts | recruiter ↔ VHL contacts |
|---|---|---|---|
| `nrv04-covalent-cofold/nr4a1` | 32 | **40** | 193 |
| `nrv04-descriptive-v4/nr4a1` s1 | 35 | **41** | 193 |
| `nrv04-covalent-cofold/neg_celastrol` | 44 | **135** | — (no recruiter) |

The recruiter is well seated in VHL (193 contacts, min distance 2.6 Å) — that half of the co-fold is
behaving. The **warhead is not in the NR4A1 pocket**: it makes more contacts with the E3 machinery than with
its own target, i.e. it is draped over the VHL↔NR4A1 interface. For the `neg_celastrol` system — *free
celastrol, whose entire purpose is to be a warhead sitting on NR4A1 with no recruiter* — the ligand is
essentially bound to the E3 (135 vs 44).

So the covalent legs do not fail A1 by a few Ångström of pose error. Their starting structures do not place
the warhead on the protein the panel is about.

## 4. What "produce an admissible input" would have to overcome

Three obstacles, in increasing severity.

1. **Distance.** 28.4 Å against a 1.8 Å bond and an 8.0 Å admissibility limit.
2. **Reachability under the ternary constraint.** For `cov_nr4a1` the recruiter must stay in VHL while the
   electrophile reaches C551. Measured in
   [`nrv04_covalent_adduct_build.py`](./nrv04_covalent_adduct_build.py) → `reachability`.
3. **Evidence for the pose itself.** Even a geometrically valid constructed adduct is only as good as the
   claim that celastrol *sits* there. The literature the repo already cites is in tension on this: Zhang 2018
   reports subnanomolar covalent engagement at C551, while Muñoz-Tello 2020 protein-NMR footprinting — cited
   in [`nr4a3-degrader-paper.md`](../manuscripts/nr4a3-degrader-paper.md) §2.2 — finds that **celastrol does
   not directly bind the NR4A LBD** (amodiaquine, chloroquine and cytosporone B do). There is no deposited
   celastrol–NR4A1 structure. An MSA-based predictor therefore has no evidence for a specific celastrol pose,
   which is the most parsimonious explanation of finding 3 and is exactly what the probe in §6 tests.

## 5. Recommendation — RE-SCOPE, drop the covalent legs

**Say which: drop them.** Four reasons, in order of weight:

1. **The panel's crux is unevaluable and would stay unevaluable.** Frozen §5 criterion 2 asks whether
   covalency *swamps* the ternary signal, by comparing `cov_nr4a1` against `noncov_nr4a1`. Answering it needs
   a covalent model that differs from the noncovalent one **only** by the bond. Any input produced here —
   constructed or steered — differs from the co-fold by a **repositioned warhead**, so the comparison would
   confound the tether with a pose change. The measurement the criterion asks for cannot be made from these
   materials.
2. **The covalent legs' scientific job is already done, for $0, by Leg 0.** The panel exists (prereg §1)
   because celastrol's covalency could make NR-V04's selectivity a warhead-reactivity story the noncovalent
   machinery cannot represent. Leg 0 **settled that**: the reactive Cys is unique to NR4A1 (NR4A2 = Tyr,
   NR4A3 = Thr579, no cysteine in either ±5 window). That is the confound, established from sequence, with no
   GPU and no structure. The covalent MD legs were never the evidence for it.
3. **NR-V04 is no longer the calibrator.** STRATEGY.md already swapped the method calibrator to
   SMARCA2-vs-SMARCA4 and demoted NR-V04 to a **biological holdout**, explicitly *because* celastrol is
   covalent. Spending to model the covalency of a demoted holdout inverts the ladder's own priority order.
4. **What remains is defensible on its own.** A **noncovalent-only** panel — `noncov_nr4a1`,
   `recruiter_active`, `recruiter_epimer` rebuilt as the binary system §3 actually specifies — is exactly what
   endpoint MD from a co-folded start can support, needs no covalent input, and reports R1 (interface
   persistence) as descriptive feasibility with directional concordance only. That is what AMENDMENT 1 already
   says the panel may claim if re-run.

**What must be said, not buried:** dropping the covalent legs removes the panel's ability to say anything
about covalency, and the write-up must state that the covalent confound is documented **from sequence
(Leg 0)** and **from the literature (Zhang 2018)**, never from a simulation this program ran. The covalent
confound stays explicit in every NR-V04 statement: NR4A1 Cys551 is unique to NR4A1 (NR4A3 has Thr579), so a
concordant result may reflect **target engagement** rather than ternary cooperativity.

## 6. The alternative, built and costed but not recommended first

If the covalent question is judged worth re-opening later, the cheapest decisive experiment is **not** a
re-fold of the panel — it is one $0-to-read probe of whether the predictor knows the site at all.
[`nrv04_celastrol_site_probe.py`](./nrv04_celastrol_site_probe.py) runs three systems and is measured
afterwards for $0 by the audit:

| system | what it decides |
|---|---|
| `binary_free` — NR4A1-LBD + celastrol, unconstrained | Does the predictor place the warhead at C551 with no E3 to drape it on? **If it misses C551 here too, no re-fold can manufacture the input** and the re-scope becomes permanent rather than provisional. |
| `binary_pocket` — the same, steered to contact residue 207 | Can it be steered there at all, and is the steered pose sterically sane? |
| `ternary_pocket` — full ternary + NR-V04, same constraint | The candidate admissible input — worth running **only** if the two binary systems say steering works. |

Priced as a Vast RTX-4090 co-fold on the existing lane (`nrv04_vast_launch.py mode=cofold`,
`TERNARY_SCRIPT=nrv04_celastrol_site_probe.py`): the two binary systems are 254-residue monomers, far below
the ~800-residue ternary that set the lane's runtime, so the binary pair over 3 seeds is **well under $1**.
Run the binaries first; the ternary is gated on them.

**Honesty condition attached to any steered result:** a pocket-constrained prediction is a **steered**
prediction. Its confidence scores do not evidence the pose — the pose was imposed. It is an assumption made
explicit, never a prediction that celastrol binds there. This is stated in the script's own output so it
cannot be quoted without it.

## 7. Code defects fixed here (they propagate beyond this panel)

**A1 was scored at the nearest cysteine; it is now scored at the identified one.**
`nrv04_covalent_md._frozen_cys_by_construct` resolves the preregistered residue by construct arithmetic
(full-length 551 → construct 207, from P22736's 598 aa and the frozen 254-residue LBD) and **verifies it is a
cysteine with an Sγ**, failing closed rather than substituting a neighbour. `_reactive_cys_by_geometry` is
demoted to a diagnostic, and the disagreement between the two is recorded
(`geometry_agrees_with_frozen_site`) — that disagreement is what made an inadmissible input look marginal.

Three consequences, all live before this change:

1. The **A1 gate** was comparing the 8.0 Å limit against C566's distance. It now compares against C551's, so
   a covalent leg on any co-fold in the bucket now fails closed at ~28 Å instead of nearly passing at ~9 Å.
2. The **covalent restraint** would have been built onto **C566**.
3. The **`cov_c551a` control was mutating C566**, not C551 — so the leg named for removing covalent
   engagement at C551 did not remove it.

**This binds the NR-V04 retrospective (RUNG 4), which shares this driver**, and AMENDMENT 1 already declares
A1 "retrospective in force". Any covalent leg there was subject to all three.

Regression tests: [`tests/test_nrv04_covalent_input.py`](./tests/test_nrv04_covalent_input.py) — the
C551↔207↔C566 arithmetic, identification-beats-proximity with both cysteines present, fail-closed when the
site is not a cysteine or the construct is the wrong length, the structural warhead definition, the
constructed adduct's C–S bond length and thioether angle, and that construction is *gated* on A1 rather than
merely reporting it.

## 8. Exact deltas requested elsewhere (not applied here — both files are owned upstream)

**`nr4a3-nrv04-covalent-feasibility-prereg.md`** — append-only; proposed AMENDMENT 2 content:

- **A1's text must name the residue.** Replace *"within bonding distance of the **target-chain** Cys Sγ"*
  with *"within bonding distance of the **preregistered covalent residue's** Sγ (NR4A1 Cys551 =
  `TARGET_COV_RESNUM`), identified by construct position and verified to be a cysteine — never the nearest
  cysteine on the chain."*
- **Correct the recorded A1 numbers.** The table under "Measured on the current co-folds" reports 8.99 Å
  (`cov_nr4a1`) and 16.39 Å (`warhead_only`) as distances to the covalent site. They are distances to
  **C566**. At C551 the same two models are **28.46 Å** and **36.43 Å**. Per CLAUDE.md §1 the superseded
  values belong in an appendix line, with the live text carrying only the corrected ones.
- **Record the scope of "any co-fold in the bucket."** It was measured on one model per system; it is now
  measured on all 34 (7 clean), and the conclusion holds.
- **Record that `cov_c551a` mutated C566** in the committed panel, so the control did not do what its name
  says. This is independent of, and additional to, the chain-split and contamination defects.
- **Retire the covalent legs** (`cov_nr4a1`, `warhead_only`) from §3, or state explicitly that they are
  unrunnable on any available input and the panel proceeds noncovalent-only — with the covalent confound
  documented from Leg 0 and Zhang 2018 rather than from simulation.

**`STRATEGY.md`** — RUNG 3 `nrv04_feasibility_covalent`:

- Keep `[HELD]`. Replace *"Unblocking now needs INPUT work, not compute: re-fold the covalent systems with the
  electrophile seated at Cys551, or drop the covalent legs and re-scope — and say which"* with the answer:
  **the covalent legs are dropped; the panel re-scopes to noncovalent endpoint MD.** Cite this file.
- Correct the A1 figures where quoted (8.99 / 16.39 Å → **28.46 / 36.43 Å at C551**; the old pair are C566's).
- Add to the "two bugs found here propagate to the unlaunched NR-V04 retrospective" note a **third**: the
  covalent site was resolved by proximity rather than identified, so the A1 gate, the restraint and the C551A
  mutation all pointed at C566. Fixed in `nrv04_covalent_md._frozen_cys_by_construct`.

## Provenance / honesty

- Every distance is measured on a real deposited-structure-derived co-fold artifact in the bucket; nothing is
  fabricated or estimated.
- The LBD↔full-length mapping is derived from the live UniProt P22736 FASTA at run time (598 aa, residue
  551 = Cys), not from a hardcoded assumption.
- The covalent site's literature anchor is Zhang 2018 (doi:10.1039/C8CC06140H, PMID 30376017), read via a
  secondary search rather than the primary PDF (the sandbox's egress proxy 403s RSC); the tension with
  Muñoz-Tello 2020 is stated in §4 rather than resolved.
- No efficacy, affinity, safety, therapeutic-window or clinical claim is made or implied. Any NR-V04 statement
  is **directional concordance** only, with the covalent confound explicit.
