# RUNG 5b — inverse linker design on the confirmed orientation basins

> **Lane doc.** The record for STRATEGY.md's RUNG 5b: the **$0 CPU** step that turns RUNG 5a's nominated
> basins into linker requirements, a virtual library, and — the deliverable that matters most — the matched
> `d`/`d₀` pair RUNG 5a-KS cannot run without. It is subordinate to [STRATEGY.md](../../STRATEGY.md); where
> they differ, STRATEGY.md wins and this file is reconciled to it. Proposed STRATEGY.md deltas are collected
> at the end rather than applied here.
>
> **Status:** kernels built and unit-tested (31 tests, each against a closed-form answer or an identity the
> module must share with `basin_geom`); the design driver run; the library emitted and RDKit-verified on CI.
> **No GPU was used and none is requested by this rung.**
>
> **Language discipline applies throughout.** Every construct is a **predicted selective candidate** and the
> set is *a computationally prioritized, structure-defined, retrosynthetically annotated candidate matrix for
> synthesis and experimental testing* — never a "hit", never "synthesis-ready". Nothing here implies efficacy,
> safety, a therapeutic window, or clinical readiness.

---

## 0. What this rung was asked to produce

> "For each confirmed basin, derive linker requirements (endpoint distance, exit-vector dihedral, strain,
> reach), enumerate a virtual library, filter by basin fidelity, annotate exact structures + synthetic
> feasibility → ~12–20 virtual constructs. For basins carrying the covalent handle, the library enumerates the
> **electrophile position on the linker** as a design variable, and **prefers reversible-covalent** chemistry."

and, downstream of it, the matched pair for the program's designated causal kill-switch:

```
S = ΔΔG_coop(d₀→d | NR4A3) − ΔΔG_coop(d₀→d | NR4A1)
```

which needs a candidate *d* and a control *d₀* differing **only** in the element that engages the wedge.

---

## 1. What was built

| file | what it is |
|---|---|
| [`linker_design.py`](../modalities/linker_design.py) | pure-stdlib kernels: convex three-ball feasibility, the electrophile branch-position window, the WLC window probability, exit-vector angles |
| [`nr4a3_linker_design.py`](../modalities/nr4a3_linker_design.py) | the driver — per-basin requirements, the virtual library, the filter, the matched pair |
| [`linker_chem_check.py`](../modalities/linker_chem_check.py) | RDKit verification that the emitted molecules *are* what the geometry said |
| [`tests/test_linker_design.py`](../modalities/tests/test_linker_design.py) | 31 unit tests |
| `nr4a3-linker-design.json` · `nr4a3-linker-library-chem.json` | the outputs |

Everything is pure stdlib except the verification, which runs on a free CI runner inside the pre-baked
`triskit23/ternary-fep` image.

---

## 2. Four things this rung found that change how RUNG 5a's numbers read

Each was produced by a measurement or a controlled re-derivation, not by reasoning about the code, and each is
reproduced in the output JSON with the observation that forced it.

### 2.1 ★ `min_linker_atoms` is a best-of-N, and the placement that achieves it is not the published one

RUNG 5a reports, per meta-basin, the shortest linker that reaches C397. Those figures are **8–12 backbone
atoms** for the five confirmed basins. But the figure is a **minimum over a few hundred sampled member
placements**, while the only placement whose coordinates the artifact publishes is the **representative** —
the highest-scoring member of the largest member basin. They are not the same placement, and the difference is
large:

| meta-basin | reported `min_linker_atoms` (C397) | **exact requirement at the representative** (3.0 Å pendant) |
|---|---|---|
| `vhl\|M3` | 8 | **23** |
| `vhl\|M2` | 9 | **16** |
| `crbn\|M0` | 11 | **33** |
| `vhl\|M4` | 12 | **30** |
| `vhl\|M14` | 12 | **21** |

Nothing here is wrong as defined — the reach *fractions* already say only **2–6 %** of a basin's placements
achieve the minimum, so a 20-atom gap between the best member and a typical one is exactly what a 2–6 % tail
looks like. What it means is that **a chemist cannot design at a statistic.** The basin search now emits the
achieving placement itself (`exemplar_placement`, with its landmarks so the full rigid transform is
recoverable), and it must be reported as the **optimistic end** of the basin, not as the basin.

### 2.2 ★ RUNG 5a's reach criterion credits the pendant arm with shortening the SPAN

The criterion is `|q−a| + |q−b| ≤ L + 2e`. For a nucleophile sitting on the anchor-to-anchor segment the left
side is just the span, so the rule reads `span ≤ L + 2e` — i.e. **a linker shorter than the distance it has to
bridge is admitted, because the pendant is credited with 2e of the span.** No pendant can do that: the linker
must physically connect the warhead exit vector to the E3 exit atom, and needs `L ≥ span` however long the
pendant is.

The construction that shows it is closed-form and is a unit test: anchors 16 Å apart, nucleophile on the
segment. The relaxed rule returns **8** atoms; the truth is **13**.

**This is a bound, not an error.** Audited over all **576** (basin × unique cysteine) records in
`nr4a3-orientation-basins.json`, **zero** have a reported `min_linker_atoms` below the same record's own
`min_linker_atoms_for_span`, so no published figure is internally impossible. But every one of them is a
**lower bound on the length a linker actually has to be**, by up to `2e ≈ 5` backbone atoms at the 3.0 Å arm
the gate was read with. RUNG 5b quotes the exact rule (three balls, integer branch positions) and reports both.

### 2.3 ★ `best_linker_atoms = 19` on 188 of 192 basins is a grid edge

19 is the last point of the accessibility scan (`range(3, 21, 2)`), and the mean-density profile is still
rising there for any span above ~12 Å — for a 20 Å span the true argmax is **~53** backbone atoms. The field is
therefore a scan boundary, not an optimum, and must not be read as "a 19-atom linker is the right length".

The fix took three attempts, and the two failures are instructive:

1. the mean **density** over member spans (5a's own quantity) is the right *form* — it is the likelihood of the
   basin's spans under the linker's end-to-end distribution — but its argmax was censored;
2. a **probability** integrated over the basin's `[min, max]` span range fixes the units and the censoring but
   is nearly vacuous: a basin is an **interface patch**, not a span class, so its members' spans run from ~5 to
   ~25 Å. Integrating over that window just rewards long chains, and it returned an "optimum" of 34–39 atoms
   for every basin.
3. What a chemist needs is neither: the **fraction of the basin's members a linker can hold without
   straining**, plus the strain at the specific placement being designed on. That is what the output reports.

The unconstrained entropic optimum is *also* reported, precisely so it can be seen to be a bad design target.

### 2.4 The 3.0 Å electrophile arm is conservative, and lengthening it is not free

RUNG 5a read its term-(a) gate with a pendant reach of 3.0 Å. Every realistic pendant is longer, and each
value below is the extended length of a **named catalogue building block** at the same 1.25 Å/atom projection
the rest of the rung uses:

| pendant | reach | what it is |
|---|---|---|
| 3.0 Å | — | the RUNG-5a convention |
| 4.0 Å | aryl bonded to a backbone carbon | |
| 5.0 Å | a directly N-acylated Michael acceptor | |
| 7.5 Å | Dap branch + acrylamide | Fmoc-L-Dap(Boc)-OH |
| 8.75 Å | Dab branch + acrylamide | Fmoc-L-Dab(Boc)-OH |

So the gate is **conservative on term (a)** — going from 3.0 to 8.75 Å shortens the exact C397 requirement by
**8–9 backbone atoms** on `vhl|M3` (23 → 14). But the same relaxation applies to **conserved** cysteines, so
intra-NR4A3 chemoselectivity degrades with pendant length. The paralogue argument is untouched (NR4A1/NR4A2
carry *no* nucleophile at the aligned positions — a sequence fact, not a geometric one), but the promiscuity
liability is real and the trade-off is reported per basin. *(In this receptor frame, at the representative
placements, no conserved cysteine comes within an exact 16-atom linker even at 10 Å of pendant reach — but
that is one static conformer and it is not a chemoselectivity claim.)*

---

## 3. ★ The result that matters most: linker tractability nearly INVERTS the basin ranking

Per basin, at the representative placement, the number of backbone atoms needed to hold the span at ≤3 kT of
worm-like-chain strain:

| meta-basin | RUNG-5a rank signal | span | span floor | **atoms for a comfortable span** |
|---|---|---|---|---|
| `vhl\|M3` | 0.75 poses, term (b) **1.4×** (weakest) | **9.7 Å** | 8 | **9** |
| `vhl\|M2` | 0.50 poses, 1.43× | 17.7 Å | 15 | 20 |
| `vhl\|M4` | 0.42 poses, exceeds | 21.7 Å | 18 | 26 |
| **`crbn\|M0`** | **0.92 poses, 7.5×** (strongest) | 23.3 Å | 19 | **29** |
| `vhl\|M14` | 0.25 poses, does **not** exceed | 24.2 Å | 20 | 31 |

**RUNG 5a's strongest nomination is its least buildable one.** `crbn|M0` — 0.92 pose persistence, 7.5×
enrichment over the term-(b) null — needs roughly **29 backbone atoms** at its representative placement, about
twice a typical published PROTAC linker, *before* any detour for the electrophile. `vhl|M3`, the basin with the
weakest term-(b) signal of the five, is held by a **9-atom** linker at essentially zero strain.

This is a cost the basin ranking could not see, because the basin search scores orientations and never asks
what molecule would realise one. It does not overturn the ranking — it adds an axis to it, and the honest
statement is that **the two axes disagree and the disagreement is the finding.**

Two qualifications, both load-bearing:

- **A basin is a region, so a short linker does not fail a wide basin outright** — it accesses the small-span
  tail of it. Member spans run from 5.4 to 25 Å, so the right quantity is the *fraction of members* a length
  can hold, which is what the output reports. The table above is the *representative* placement specifically.
- `crbn|M0` is **retained in the library anyway**, as the best construct available within the chemically
  routine cap, **with the thresholds it fails attached**. Dropping it would have produced a clean-looking
  library that silently omitted the best basin for a reason no reader could see.

---

## 4. Linker requirements, per basin

All at the representative placement, whose rigid transform is recovered from the stored landmarks and
**verified** by reproducing the placement's own recorded E3 anchor to **0.002–0.008 Å** (limited only by the
two-decimal rounding of the stored coordinates). A recovery worse than 0.05 Å is a refusal, not a warning.

| meta-basin | span | floor | α (warhead exit) | β (E3 exit) | dihedral | turn cost | wedge sites |
|---|---|---|---|---|---|---|---|
| `vhl\|M3` | 9.67 Å | 8 | 100.1° | 79.7° | −127.9° | 3 atoms | 2 |
| `vhl\|M2` | 17.73 Å | 15 | 79.8° | 72.9° | +149.0° | 2 atoms | 6 |
| `vhl\|M4` | 21.75 Å | 18 | 70.6° | 128.4° | −54.4° | 3 atoms | 2 |
| `vhl\|M14` | 24.22 Å | 20 | 34.7° | 122.1° | +72.1° | 2 atoms | 5 |
| `crbn\|M0` | 23.25 Å | 19 | 65.2° | 98.8° | −138.4° | 2 atoms | 3 |

- **α** is the angle between the warhead's exit direction and the vector toward the E3 anchor; **β** the same
  on the E3 side. Both are 35–130°, i.e. **no basin lets the linker run taut** — every one requires a turn at
  at least one end, costing 2–3 backbone atoms of contour over the straight span. That cost is a **lower
  bound**: it models the exit-bond constraint for one bond at each end, where a real substituent biases several.
- **The dihedral matters and is reported for a reason.** Two designs with identical α, β and span still differ
  in whether the linker sweeps across the target surface or out into solvent — the difference between a linker
  that reinforces the basin's interface and one that fights it. `vhl|M2` (+149°) and `vhl|M3` (−128°) are on
  opposite sides.
- **Definitional slack, stated because it is comparable to what is being resolved.** The geometric anchors are
  the pose's pocket-mouth exit point and the crystal ligand's derived exit atom; the *chemical* anchors are the
  warhead's C5 substituent atom and the E3 handle's attachment heteroatom. These are within one to two bonds of
  each other, so **every backbone-atom count carries about ±2 atoms of definitional slack.** That is why
  lengths are enumerated as a ladder and never asserted as a value.

---

## 5. The virtual library

**2,141 constructs enumerated, 22 retained** by a **preregistered** filter — fixed before enumeration and never
tuned to a result, the same discipline the E3 downselect and the Tier-2 gate were held to. It is a set of
thresholds, not a tunable scalar, because a tunable scalar is what STRATEGY.md's load-bearing piece 5 forbids.

**The filter:** must span the anchor-to-anchor floor (hard); must comfortably hold ≥25 % of its basin's
members; ≤3 kT of chain strain at the designed placement; ≤24 backbone atoms; ≤2 per (basin × pendant class);
controls retained where they match a kept design; one construct retained per confirmed basin even on failure,
with its failures attached.

**Parsimony is the tie-break, and it had to be added.** Comfortable coverage increases monotonically with
length, so ranking on it alone drove every construct to the length cap — the first filtered library was 16
constructs all at exactly 24 backbone atoms. Length is a real cost (permeability, synthetic steps, the entropic
price the ternary assembly pays), so among constructs clearing the thresholds the **shortest wins**.

**Chemistry, all from staged artifacts or named catalogue reagents:**

- **warhead** — methyl 5-X-indole-3-carboxylate, the cmpd19 anchor, with X taken from the **already-staged**
  congeneric exit-vector series (`cw_ev_5nh2` → aniline amide; `cw_ev_5opropargyl` → CuAAC 1,4-triazole;
  `cw_ev_5piperazine` → N4-acyl piperazine). Not drawn fresh for this rung.
- **E3 handle** — VH032 with the linker on the *tert*-leucine nitrogen (the MZ1/ARV-771 vector), or
  pomalidomide on the 4-amino nitrogen.
- **linker** — a short peptide-like chain, `E3-NH-C(=O)-[SEG1]-C(=O)-NH-CH(R)-C(=O)-NH-[SEG2]-`, alkyl or PEG.
- **branch** — an **L-amino-acid residue**, not a substituent on an arbitrary backbone carbon. This fixes three
  things at once: the stereocentre becomes a defined **(S)** centre inherited from a catalogue building block
  instead of an unspecified one; the pendant installs by standard orthogonal-protection chemistry; and it
  avoids the α-alkoxy stereocentre that branching a PEG carbon produced in the first version.

### The electrophile position on the linker, as the design variable

For each basin and length, the **exact** branch-position window is computed: the set of backbone atoms *k*
(counted from the warhead end) from which a pendant of the given reach can touch C397's Sγ, as the
intersection of three balls — radius `k·1.25 Å` from the warhead anchor, `(n−k)·1.25 Å` from the E3 anchor, and
the pendant reach from Sγ. Representative windows:

| basin | n | branch window *k* (Dab pendant, 8.75 Å) | E3 clearance at the best *k* |
|---|---|---|---|
| `vhl\|M2` | 15 | 11–13 | 7.0 Å |
| `vhl\|M2` | 21 | 11–19 | 8.5 Å |
| `vhl\|M14` | 22 | 7–12 | 5.1 Å |
| `vhl\|M3` | 15 | at *k* = 10 in the retained construct | — |

The window is **narrow at the shortest feasible length and widens with it** — which is the design statement:
at a 15-atom linker on `vhl|M2` the electrophile has essentially one place to be, and that is a testable
prediction rather than a preference.

### Reversible-covalent chemistry, and why

**β-methyl α-cyanoacrylamide** is the default electrophile, with the β-phenyl variant as the residence-time
tuning axis. The α-cyano group acidifies the adduct's α-proton so retro-Michael is fast; a β-substituent slows
the forward addition and speeds the reverse, which is what makes the class tunable. **Reversibility is what
preserves catalytic turnover** — an irreversible adduct makes the degrader stoichiometric and forfeits the one
property that makes a degrader worth building.

Two controls are in the library so this is a *tested choice* rather than an assertion:

- **acrylamide**, the irreversible comparator the reversible design is argued against;
- **α-cyano-propanamide**, the saturated, non-electrophilic control — same heavy atoms, same charge, same
  amide, no Michael acceptor, so anything attributable to the warhead is attributable to the C=C and nothing
  else.

⚠ **A covalent handle is an unresolved liability, not an upgrade.** Electrophile promiscuity cannot be checked
without chemoproteomics, which this program does not have, and it must be reported alongside the parent cmpd19
warhead's published **MYC induction** — parent-warhead pharmacology is a potential liability, not evidence of
benefit.

### RDKit verification — a refusal, not a report

The enumerator derives length and branch position from **geometry** and then emits a SMILES by
**concatenation**. Those are two independent descriptions of the same molecule and nothing forces them to
agree. `linker_chem_check.py` re-derives both from the **parsed molecule** (topological shortest path between
the two anchor atoms), matches the required cores and the declared pendant as exact substructures, checks a
list of junction motifs that must never appear, refuses any unassigned stereocentre, and **fails the build** on
a mismatch.

It exists because four defects had already been found by hand, and reading strings does not scale:

| defect | what it produced | how it was caught |
|---|---|---|
| the VHL handle ended at `NC(=O)` and the assembler added a second carbonyl | an **α-ketoamide** at every E3 junction | reading the emitted SMILES |
| a PEG segment placed after an amide nitrogen | an **N,O-acetal** (`N-CH₂-O-`), hydrolytically labile | reading the emitted SMILES |
| the branch residue abutting the warhead acyl | an **acylurea** instead of two amides | reading the emitted SMILES |
| `k_warhead = n − k_E3` | every electrophile **one atom too close to the warhead** | re-deriving the index: an atom that is the *i*-th from one end is the *(n+1−i)*-th from the other |

All four are now refusals in the assembler and assertions in the self-test. The off-by-one is pinned by an
**identity** (`k_warhead + k_E3 = n + 1`) rather than by restating the formula under test.

---

## 6. ★ The matched pair for RUNG 5a-KS

**Proposed pair, on `vhl|M3` at 11 backbone atoms:**

| | |
|---|---|
| **wedge element** | **3-(3-pyridyl)-L-alanine (d) vs L-phenylalanine (d₀)** as the linker's branch residue — an aza-scan |
| **wedge target** | **Arg412** — NR4A1 **Ala**, NR4A2 **Thr**; non-conservative; RSA 0.78 |
| **branch position** | *k* = 6 of 11, counted from the warhead |
| **E3 clearance at the wedge** | **10.3 Å** from the nearest E3 atom in the modelled placement |
| **basin** | `vhl\|M3` — 0.75 pose persistence, span 9.67 Å, held at ~0 kT by this linker |
| **d** | `CC1=C(SC=N1)C2=CC=C(C=C2)CNC(=O)[C@@H]3C[C@H](CN3C(=O)[C@H](C(C)(C)C)NC(=O)CCC(=O)N[C@@H](Cc7cccnc7)C(=O)NCCC(=O)Nc4ccc5[nH]cc(C(=O)OC)c5c4)O` |
| **d₀** | `CC1=C(SC=N1)C2=CC=C(C=C2)CNC(=O)[C@@H]3C[C@H](CN3C(=O)[C@H](C(C)(C)C)NC(=O)CCC(=O)N[C@@H](Cc7ccccc7)C(=O)NCCC(=O)Nc4ccc5[nH]cc(C(=O)OC)c5c4)O` |

### Why "differs only in the wedge element" holds — three checks, not an assertion

**(i) One element, and it is one atom.** An aza-scan is the cleanest matched pair available: net formal charge,
heavy-atom count, rotatable-bond count and the (S) stereocentre are **identical**, and exactly one property
changes — the H-bond acceptor at the wedge site. Both members are catalogue amino acids (Fmoc-L-Phe-OH and
Fmoc-3-(3-pyridyl)-L-Ala-OH), so the pair is a one-reagent swap in an otherwise identical synthesis. A charged
wedge (a carboxylate on Arg412) would have been a stronger interaction and a **worse experiment**: a
net-charge change under PME needs a finite-size correction that does not cancel between differently-sized
boxes, and the repo's own `assert_charge_consistency` refuses such a wedge outright.

**(ii) The wedge engages a target-side difference.** Arg412 is one of the program's seven selectivity handles;
it is Ala in NR4A1 and Thr in NR4A2, non-conservatively, at RSA 0.78. And it is **within pendant reach of the
linker path in all five confirmed basins** — as is T407 — so the pair is not an artefact of one basin's
geometry.

**(iii) The wedge does not touch the E3.** This is the check that makes the double difference mean what it
says. `S` isolates a *target-side* interaction only because the ligand's solvation, its internal strain and its
entire interaction with the E3 are identical in the two paralogue legs and cancel exactly — the shared binary
and solvent legs are paralogue-independent, which is also why the test needs **ternary legs only**. If the
wedge element could touch the E3, that cancellation would fail. Measured clearance at the chosen position is
**10.3 Å**, and the basin was selected on that measurement.

### Remaining confounds — stated with the proposal, not in a footnote

1. **Arg412's side chain is rigid in this model.** A pendant designed against one modelled rotamer is
   conditional on it, and an Arg at RSA 0.78 is exactly the side chain that samples most widely.
2. **NR4A1 carries alanine at the aligned position**, so the wedge does not meet an unfavourable partner there
   — it meets a solvent-exposed gap. The expected signal is an **NR4A3 gain**, not an NR4A1 penalty, and its
   magnitude is bounded by a single solvent-exposed H-bond: roughly **0.5–1.5 kcal/mol against a best-case
   resolvable difference of 1.12**. A null is a likely outcome and must be interpreted accordingly.
3. **Double conditionality.** The construct rests on the hypothesised cmpd19 pose × one receptor frame.
4. **The basin is a rigid-body nomination, not a modelled complex.** The linker conformer that places the wedge
   on Arg412 is one of many the chain can adopt and its population is unmeasured — that is 5c's job.
5. **The E3 downselect that produced these arms is blind to recruiter-intrinsic pharmacology**, a required
   input to this gate that this rung does not supply.

### ★★ And the thing that most needs saying: **a non-covalent double difference cannot test the categorical mechanism**

RUNG 5a's Tier-2 GO was taken on the **CATEGORICAL** basis: NR4A1 and NR4A2 have **no nucleophile** at the
position aligned with C397 (Asn363 / Ser363). That is a bond that can form in one paralogue and *cannot form*
in the other — not a free-energy difference.

`S` is an ordinary **non-covalent** relative alchemical quantity. It sees the **pre-covalent** complex only. So
**RUNG 5a-KS as specified tests the MARGINAL axis — the very axis the mechanism-first reframe demoted for
operating at its resolution limit — while the gate that nominated the basins was passed on the categorical
one.** The consequence is a semantic one and it is important:

> **A NO-GO from 5a-KS falsifies the marginal induced-interface wedge. It does NOT falsify the program**,
> whose selectivity argument rests on a categorical mechanism that no non-covalent double difference can
> reach.

This is not an argument for skipping 5a-KS — a positive `S` would be a genuine second axis of selectivity on
top of the categorical one, and that is worth ~$12. It is an argument for **writing down what a null means
before it is observed**, which is what a preregistered kill-switch is for.

**A second pair is therefore proposed**, addressing the pre-covalent half of the categorical axis:
**d = β-methyl α-cyanoacrylamide** at the C397 branch position, **d₀ = the saturated α-cyano-propanamide** at
the same position. It asks whether the electrophile-bearing arm's *non-covalent recognition* already
discriminates Cys397 from Asn363. In reversible-covalent chemistry selectivity is `K_i × k_inact`; this
addresses `K_i` only, and **a null leaves the categorical (`k_inact`) argument standing** — which is exactly
why it must not be run as though it were the kill-switch either.

---

## 7. Honest scope

- **Double conditionality** — everything is conditional on the hypothesised cmpd19 binary pose × the chosen
  receptor frame. This repo holds no cmpd19 pose in the matched-model frame.
- Designed on **rigid-body placements** with rigid side chains, no solvation and no induced fit. A construct is
  a hypothesis about where a linker *could* go, not a prediction that it will.
- ±2 backbone atoms of **definitional slack** in every length, from the geometric-vs-chemical anchor mismatch.
- The WLC strain is an **ideal semi-flexible-chain** estimate — no excluded volume, no solvent, no torsional
  preferences. It is not a force-field strain energy and no ranking turns on a small difference in it.
- **Synthetic annotations are routes, not validated syntheses**: building-block availability was not checked
  against a live commercial catalogue and no step was attempted.
- Descriptors are **reported, not gated**: a bifunctional degrader is beyond-rule-of-5 by construction and a
  Ro5 filter would reject the entire modality.
- A covalent handle is a liability to be reported, alongside the parent warhead's **MYC induction**.
- Language: **"predicted selective candidate"**. The set is *a computationally prioritized, structure-defined,
  retrosynthetically annotated candidate matrix for synthesis and experimental testing*. No efficacy, safety,
  therapeutic-window or clinical claim is made or implied.

---

## 8. Exact STRATEGY.md deltas proposed by this lane

*This lane does not edit STRATEGY.md (several lanes run concurrently and the orchestrator owns it). These are
the precise changes to apply, each with its evidence.*

**D1 — RUNG 5b status.** `[ ] 5b · Inverse linker design — ~$0–20 (mostly $0 CPU)` → **`[x]` … DONE
2026-07-25 · $0 REALIZED**, 22 constructs across all five confirmed basins, RDKit-verified. The `$0–20`
band's mid should become the realized **$0**, by the same convention `valA_mini` already uses; regenerate the
ladder total with `vast_cost_model.py` rather than typing it, and register the superseded value in
`pinned-figures.json` in the same commit.

**D2 — the Tier-2 result block gains the linker-tractability axis.** In "★ Tier-2 result in full", the table
of five basins should carry a column for **backbone atoms needed to hold the span at ≤3 kT**: `vhl|M3` **9**,
`vhl|M2` 20, `vhl|M4` 26, **`crbn|M0` 29**, `vhl|M14` 31. **The strongest basin is the least buildable**, and
the two rankings disagree. This is an addition to the ranking, not a reversal of it.

**D3 — two corrections to how RUNG 5a's own numbers are quoted.** Neither changes a gate verdict:
- `min_linker_atoms` is a **best-of-N over a basin's members** and the achieving member is not the published
  representative — at the representative of all five confirmed basins the exact requirement is **14–33** atoms
  against a reported 8–12. Quote it as the optimistic end of the basin, with the reach fraction beside it.
- the reach criterion `|q−a| + |q−b| ≤ L + 2e` **credits the pendant with shortening the span**, so every
  reported figure is a **lower bound**, by up to ~5 backbone atoms. Audited over all 576 records, none is
  internally impossible.

**D4 — the reconciliation note on `best_linker_atoms` needs one more sentence.** The existing note is right
that it is a different quantity from the gate; what was not known when it was written is that the **reported
value 19 is the last point of the scan**, on 188 of 192 basins. It is a grid edge, not an optimum, and should
not be quoted as a recommended linker length.

**D5 — ★ RUNG 5a-KS's kill-switch semantics must be written down before it runs.** Tier 3 currently reads *"No
discrimination ⇒ STOP"*. But `S` is a **non-covalent** relative alchemical quantity and the Tier-2 GO was taken
on the **CATEGORICAL** axis — a bond that forms in NR4A3 and cannot form in NR4A1/NR4A2. A non-covalent double
difference cannot reach that mechanism. Tier 3 should read: **"No discrimination ⇒ the marginal
induced-interface wedge is absent; the selectivity claim rests on the categorical axis alone and the
manuscript must say so. STOP only if the categorical axis has also failed."** Without this the program is
one cheap negative away from stopping on a category error.

**D6 — the pendant-reach convention.** RUNG 5a's 3.0 Å electrophile arm is shorter than every real pendant
(4.0–8.75 Å for named catalogue branches), so term (a) is **conservative**. Going to a Dab branch shortens the
exact C397 requirement by 8–9 atoms on `vhl|M3`. The counterweight belongs in the same sentence: a longer
pendant relaxes reach to **conserved** cysteines too, degrading intra-NR4A3 chemoselectivity, while leaving the
paralogue argument (a sequence fact) untouched.

---

## 9. What RUNG 5b did NOT do, and what should come next

- **No GPU, and none is warranted here.** The next spend on the ladder is still 5a-KS.
- The designs are built on the **representative** placements. The basin search now emits the term-(a)
  **exemplar** placement; re-running this rung against a basin artifact carrying it will move the covalent
  constructs onto the geometry that actually achieves the reach, and is expected to **shorten** them.
- The span distribution is currently a **3-point approximation** from `{min, median, max}`; the search now
  emits deciles, and re-running against them replaces every coverage number with an exact one.
- **Linker conformer populations are unmeasured.** Whether the chain actually visits the branch position that
  presents the electrophile to C397 — or the wedge to Arg412 — is a 5c question, and 5b's windows are
  necessary conditions, not populations.
