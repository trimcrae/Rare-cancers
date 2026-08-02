# RUNG 5b — inverse linker design on the confirmed orientation basins

> **Lane doc.** The record for nr4a3-program-map.md's RUNG 5b: the **$0 CPU** step that turns RUNG 5a's nominated
> basins into linker requirements, a virtual library, and — the deliverable that matters most — the matched
> `d`/`d₀` pair RUNG 5a-KS cannot run without. It is subordinate to [nr4a3-program-map.md](nr4a3-program-map.md); where
> they differ, nr4a3-program-map.md wins and this file is reconciled to it. Proposed nr4a3-program-map.md deltas are collected
> at the end rather than applied here.
>
> **Status:** DONE, and **RE-ENUMERATED 2026-07-26 (LANE 14) against the corrected 10⁶ basin artifact.** The
> live numbers are in §10; everything above §10 that this supersedes is listed in [§11 · Appendix](#11--appendix--superseded-numbers).
> Kernels and driver built and unit-tested (**62 tests**, each against a closed-form answer, a hand-constructed
> case, or an identity the module must share with `basin_geom`); the design driver run at BOTH placements; the
> library emitted and RDKit-verified on CI, with every backbone length and branch position re-derived from the
> parsed molecule rather than trusted from the geometry that proposed it.
> **No GPU was used and none is requested by this rung. $0 realized.**
>
> **★ THE CURRENT LIBRARY IS 36 CONSTRUCTS AT THE TERM-(a) EXEMPLAR + 18 AT THE REPRESENTATIVE.** Any "21" or
> "22" below is a superseded count — see §10.2 and §11.
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
| [`tests/test_linker_design.py`](../modalities/tests/test_linker_design.py) | 33 kernel tests |
| [`tests/test_nr4a3_linker_design.py`](../modalities/tests/test_nr4a3_linker_design.py) | 29 driver tests — SMILES assembly, the backbone-index identity, the filter's preregistration, the single wedge-site selector |
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

## 3. ★★ SUPERSEDED BY §3b — the representative is the wrong placement, and correcting it reverses this section

> **Read §3b before §3.** The analysis below is computed at each basin's **representative** placement, and it
> concluded that linker tractability inverts the basin ranking — that `crbn|M0`, the strongest nomination,
> needs ~29 backbone atoms and is the least buildable. **That conclusion does not survive.** The
> representative is the highest-scoring member of the largest member basin; the member that actually carries
> the term-(a) mechanism is a different placement, and the basin-search re-run built for this rung now emits
> it. At the mechanism-carrying placement **every confirmed basin is within routine linker range, and
> `crbn|M0` is among the most tractable.** §3 is retained because it is the correctly-computed answer to a
> question posed at the wrong placement, and because the size of the error — 29 atoms versus 15 — is the
> argument for why the exemplar had to be emitted at all.

## 3a. At the REPRESENTATIVE placement (superseded)

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

## 3b. ★★ THE CORRECTED RESULT — at the mechanism-carrying placement, every basin is routine

> **⚠ THE NUMBERS IN THIS SECTION ARE SUPERSEDED — see [§10](#10--re-enumerated-on-the-corrected-10-artifact-lane-14-2026-07-26).**
> They were computed against the **pre-correction** basin artifact, i.e. with the relaxed reach rule still in
> the basin search. The *finding* — that designing at the exemplar rather than the representative changes the
> answer completely, and that the reported minimum's achieving member is not the published representative —
> **survives unchanged and is the reason the exemplar is emitted at all.** The table's values do not; the
> corrected ones are in §10.1.

The basin-search re-run (CI 30175026755, 71.6 min, **$0**) **reproduced the Tier-2 gate exactly** — 58
meta-basins, **7** term-(a), **40** term-(b), 28 nominally discriminating, basis CATEGORICAL, pass — so the
change was purely additive and every published RUNG-5a number stands. What it adds is the
`exemplar_placement`: per basin and per unique cysteine, the sampled member that **achieves** the reported
minimum, with its landmarks, so its full rigid transform is recoverable (verified to 0.0004–0.0007 Å).

Designing on it instead of on the representative changes the answer completely:

| meta-basin | span at rep | **exact C397 at rep** | span at **exemplar** | **exact C397 at exemplar** | comfortable length at exemplar |
|---|---|---|---|---|---|
| **`crbn\|M0`** | 23.3 Å | **25** | **13.4 Å** | **11** | **~15 atoms** (1.1 kT) |
| `vhl\|M3` | 9.7 Å | 14 | 12.6 Å | **11** | ~13–15 |
| `vhl\|M2` | 17.7 Å | 15 | 12.3 Å | **10** | ~12–14 |
| `vhl\|M4` | 21.7 Å | 22 | 16.8 Å | **14** | ~18–20 |
| `vhl\|M14` | 24.2 Å | 20 | 8.3 Å | **7** | ~9 |

*(exact = three-ball rule, integer branch positions, Dab-type pendant at 8.75 Å)*

**Three consequences, and the first one reverses §3.**

1. **`crbn|M0` — RUNG 5a's strongest nomination — is not the least buildable. It is among the most.** At its
   exemplar it needs a **15-backbone-atom** linker, not 29, and reaches C397 at 11. The "linker tractability
   inverts the basin ranking" finding was an artifact of the placement.
2. **The exit-vector geometry is much kinder at the exemplars too** — α = 33–70° and turn penalties of 1–3
   backbone atoms, against α up to 100° at the representatives. The linker does not have to double back.
3. **The exemplar's wedge sites are cleaner than any representative's.** Recomputed at the exemplar (they had
   to be — the exemplar minimises the *C397* focal sum, so nothing guarantees the wedge geometry carries
   over), `crbn|M0` offers **five** divergent, exposed, linker-reachable sites, every one with **8.6–14.3 Å**
   of E3 clearance — more than any VHL basin provides anywhere.

⚠ **The exemplar is a best-of-N member and therefore the OPTIMISTIC end of its basin; the representative is a
typical one.** The truth for any real molecule lies between them. Both are emitted, side by side, for exactly
that reason — quoting either alone misleads, in opposite directions.

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

> **⚠ COUNTS SUPERSEDED — the live ones are in [§10.2](#102--the-library-survives-the-corrected-geometry-intact-and-a-different-defect-took-three-of-it).**
> The **filter** described below is unchanged and still preregistered; only the enumeration totals moved, and
> they moved because the library is now built at both placements against the corrected artifact.

**1,995 constructs enumerated, 21 retained** by a **preregistered** filter — fixed before enumeration and never
tuned to a result, the same discipline the E3 downselect and the Tier-2 gate were held to. It is a set of
thresholds, not a tunable scalar, because a tunable scalar is what nr4a3-program-map.md's load-bearing piece 5 forbids.

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
- **2-cyanobutanamide**, the saturated, non-electrophilic control — `cyac_me` with the Michael acceptor
  reduced and nothing else changed, so anything attributable to the warhead is attributable to the C=C.

⚠ **And a saturated control of a Michael acceptor cannot be perfectly matched — this one is matched in
constitution but not in stereochemistry.** Reducing the acceptor turns its sp² α-carbon into an sp³ centre
bearing four different groups (nitrile, amide, ethyl, H), so **the control has a stereocentre the electrophile
does not have.** That is a property of the transformation, not a flaw in this control. It is declared as a
single **(S)** diastereomer rather than left unspecified — an unspecified centre would make the "control" two
compounds — and the **(R)** epimer is the obvious second control if the centre needs to be shown not to
matter. This surfaced because the RDKit verifier refuses an unassigned stereocentre; it would have been
invisible to inspection.

### ★★ The chemistry axis is ONE RESIDUE DEEP, and there is no geometric fallback

C397 itself is **robust**: over a 100-conformer MD ensemble its RSA median is **0.416** (the committed 0.395
sits at the median, not at an optimistic tail) and it reaches the 12-atom gate in **96 %** of unbiased frames.

But **C420 and C559 reach that gate in 0 of 75 frames** — C420 needs 16 backbone atoms and C559 needs 20, both
paid out of the same contour that must *also* span to the E3. So if C397 fails **chemically** — an unreactive
microenvironment, a competing conserved cysteine, an unacceptable promiscuity profile — **no other
NR4A3-unique cysteine can take its place, and the categorical chemistry axis closes.** This is a
single-point-of-failure and it must be reported as one.

**What this library can and cannot hedge, honestly:**

- **It cannot hedge with a second cysteine, because there is not one.** No enumerated construct, at any
  pendant length in the sweep, brings C420 or C559 inside a chemically routine linker at these placements.
  Lengthening the pendant does not fix it: the deficit is 4–8 backbone atoms, and buying them lengthens the
  linker, which costs permeability and brings *conserved* cysteines into reach at the same time.
- **It does hedge by not being all-covalent.** Constructs carrying **no electrophile at all** are in the
  retained set, and they are designed against the **paralogue-unique LYSINE axis (term b)** — K572/K518/K592 —
  which is independent of C397 entirely. If the covalent handle fails, the library does not go to zero; it
  falls back to a second categorical mechanism with its own, separately nominated basins.
- **The matched pair for 5a-KS is deliberately on the non-covalent axis**, so the program's causal test does
  not itself depend on C397 surviving.

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

**It has already paid for itself.** On its first complete run it verified **the matched pair** — d and d₀ come
back as **C₄₇H₅₅N₉O₉S** and **C₄₈H₅₆N₈O₉S**, identical at **66 heavy atoms**, identical in net charge,
rotatable bonds and stereocentre count, with the backbone length (11) and branch position (*k* = 6) re-derived
from the parsed molecules rather than taken from the geometry that proposed them. "Differs only in the wedge
element" is therefore a **measurement**, not a claim. It also found two further defects nothing else would
have: a branch-attachment check that assumed direct bonding and so failed on every side-chain-mounted
electrophile, and the stereocentre the saturated control creates.

It exists because four defects had already been found by hand, and reading strings does not scale:

| defect | what it produced | how it was caught |
|---|---|---|
| the VHL handle ended at `NC(=O)` and the assembler added a second carbonyl | an **α-ketoamide** at every E3 junction | reading the emitted SMILES |
| a PEG segment placed after an amide nitrogen | an **N,O-acetal** (`N-CH₂-O-`), hydrolytically labile | reading the emitted SMILES |
| the branch residue abutting the warhead acyl | an **acylurea** instead of two amides | reading the emitted SMILES |
| `k_warhead = n − k_E3` | every electrophile **one atom too close to the warhead** | re-deriving the index: an atom that is the *i*-th from one end is the *(n+1−i)*-th from the other |
| the saturated control was α-cyano-**propan**amide | **one carbon short** of its own electrophile — missing the β-methyl, so a difference between them would have been partly a methyl group and not the alkene | a test comparing the two skeletons with bond orders erased |

All five are now refusals in the assembler or assertions in the test suite. The off-by-one is pinned by an
**identity** (`k_warhead + k_E3 = n + 1`) rather than by restating the formula under test; the control is
pinned by requiring its skeleton to equal the electrophile's once `=` is removed.

**And the verifier's own first two attempts failed, which is worth recording.** Hand-written anchor patterns
were wrong twice — first a SMARTS whose positional index named the phthalimide carbonyl **oxygen** instead of
the aniline nitrogen (seven bonds out, and precisely the 24-vs-31 length discrepancy it then reported), then
`MolFromSmiles` patterns that failed against **their own reference molecules** on 4 of 5 anchors. *(The exact
RDKit reason for the second failure was not isolated: a diagnostic was written to discriminate the candidate
causes, but the approach was replaced before it returned, so no cause is claimed here.)* Anchors are now found
**structurally** — match the two truncated cores, take the shortest path between them, and the anchor on each
side is the first path atom outside its own core. That is the chemical definition of the anchors verbatim,
with nothing hand-transcribed, and one rule covers all three warhead handles instead of three patterns.

---

## 6. ★★ The matched pair for RUNG 5a-KS — RECOMMENDED

> **⚠ THE PAIR ITSELF IS SUPERSEDED — the live specification is
> [§10.3](#103--the-matched-pair-the-basin-and-the-wedge-site-stand-the-shared-length-does-not).**
> The *basin*, the *wedge element*, the *wedge site* and the *reason for each* are unchanged; the **molecules,
> the length, the branch position and the clearance are not**, and §6b's block was additionally stale against
> its own committed artifact by two CI runs before this lane touched it (see §11). Read §10.3 for what to build;
> read §6 for why it is that shape.

### 6a. RECOMMENDED — `crbn|M0` at its term-(a) exemplar

| | |
|---|---|
| **basin** | **`crbn\|M0`** — 0.92 pose persistence (11/12), **7.5×** over the term-(b) null: RUNG 5a's strongest nomination |
| **placement** | the **term-(a) exemplar**, not the representative |
| **linker** | **15 backbone atoms** (span floor 11, exemplar span 13.4 Å, **1.1 kT** of chain strain) |
| **wedge element** | 3-(3-pyridyl)-L-alanine (d) vs L-phenylalanine (d₀) — an aza-scan branch residue |
| **wedge target** | **Thr407** — **Leu** in NR4A1, **Val** in NR4A2: the donor is removed in *both* paralogues |
| **E3 clearance at the wedge** | **8.6 Å** |
| **and the same geometry carries the covalent handle** | C397 reachable at **11** backbone atoms with a Dab pendant — so the wedge pair and the reversible-covalent series can be built on **one** placement instead of two |

**Why T407 and not the site with the most clearance.** Geometry alone picked **Ile396** (Ile → Ala/Val, 12.6 Å
— the most E3-clear position available) and that is the **wrong chemistry**: the wedge element is an H-bond
*acceptor*, and a pyridyl nitrogen against an isoleucine is a desolvation cost with no compensating
interaction — in NR4A3 *and* in both paralogues, so the double difference would be near zero by construction.
A preregistered one-line chemistry rule now applies alongside the geometry: **NR4A3 must present a side-chain
H-bond donor and both paralogues must not.** That selects T407 (Thr → Leu/Val) over I396, N400 (Asn → Thr/Ser
— both paralogues keep a donor) and Q532 (Gln → Pro/Ser — Ser keeps one). It is also, independently, the site
the representative-placement analysis had already chosen on its own chemistry.

⚠ **What is and is not enumerated.** This block specifies the design target exactly — basin, placement,
length, branch-position window, wedge site, clearance. The **SMILES in `virtual_library` were enumerated at
representative geometry** and are not re-derived here. Re-enumerating the library at exemplar geometry is the
obvious next **$0** step and is listed in §9.

### 6b. The representative-placement pair (fully enumerated and RDKit-verified)

**Proposed pair, on `vhl|M3` at 11 backbone atoms:**

| | |
|---|---|
| **wedge element** | **3-(3-pyridyl)-L-alanine (d) vs L-phenylalanine (d₀)** as the linker's branch residue — an aza-scan |
| **wedge target** | **Thr407** — NR4A1 **Leu**, NR4A2 **Val**; non-conservative (polar → hydrophobic); RSA 0.28 |
| **branch position** | *k* = 6 of 11, counted from the warhead |
| **E3 clearance at the wedge** | **10.3 Å** from the nearest E3 atom in the modelled placement |
| **basin** | `vhl\|M3` — 0.75 pose persistence, span 9.67 Å, held at ~0 kT by this linker |
| **d** | `CC1=C(SC=N1)C2=CC=C(C=C2)CNC(=O)[C@@H]3C[C@H](CN3C(=O)[C@H](C(C)(C)C)NC(=O)CCC(=O)N[C@@H](Cc7cccnc7)C(=O)NCCC(=O)Nc4ccc5[nH]cc(C(=O)OC)c5c4)O` |
| **d₀** | `CC1=C(SC=N1)C2=CC=C(C=C2)CNC(=O)[C@@H]3C[C@H](CN3C(=O)[C@H](C(C)(C)C)NC(=O)CCC(=O)N[C@@H](Cc7ccccc7)C(=O)NCCC(=O)Nc4ccc5[nH]cc(C(=O)OC)c5c4)O` |

### Why this basin, and not the strongest one — stated because the obvious wrong reason was available

An earlier framing of the RUNG-5a result held that *"CRBN's null is 0.81–0.96, so the discrimination lives on
VHL."* **That claim is retracted** (Lane 7): 0.81–0.96 is the **any-lysine** null, while term (b)'s enrichment
is over the **unique-lysine** null — a different denominator from the one the gate uses — and the number is
itself an exit-vector artefact that **halves, 0.858 → 0.399**, when the CRBN arm is restaged assembly-native
(CRBN's exit vector had moved 16.5 Å between constructions; VHL's only 0.99 Å). CRBN remains the sole
Pareto-front member; VHL is a **labelled backfill and E3-choice sensitivity control**.

**No CRBN-vs-VHL preference is asserted here, and the pair above does not rest on one.** `vhl|M3` was selected
on basin evidence only — pose persistence, then measured E3 clearance at the wedge — among the basins that can
actually host a matched pair. `crbn|M0` is excluded for exactly one reason, and it is **chemical, not
recruiter-related**: holding its representative span at ≤3 kT needs **~29 backbone atoms**, past the 24-atom
routine cap this rung uses. The per-basin audit is emitted in the output so the selection can be checked
rather than trusted.

**★ And the alternative is worth the orchestrator's explicit call, not a silent filter.** `crbn|M0` is the
strongest single basin (0.92 pose persistence, 7.5× over the term-(b) background) **and it carries the best
wedge residue in the entire set: D413 — LYSINE in NR4A1 and SERINE in NR4A2, i.e. a charge REVERSAL rather
than a deletion — at 10.1 Å of E3 clearance.** An Asp→Lys difference is a far stronger discriminator than the
Arg→Ala the `vhl|M3` pair engages, because the paralogue does not merely lose a partner, it presents the
opposite charge. The price is a ~26–29-atom linker: long, but not unprecedented for a PROTAC, and the cap is a
stated convention rather than a law. That trade — a stronger basin and a much stronger wedge residue, paid for
in linker length, permeability, and ternary entropy — is a judgement worth making deliberately.

### Why "differs only in the wedge element" holds — three checks, not an assertion

**(i) One element, and it is one atom.** An aza-scan is the cleanest matched pair available: net formal charge,
heavy-atom count, rotatable-bond count and the (S) stereocentre are **identical**, and exactly one property
changes — the H-bond acceptor at the wedge site. Both members are catalogue amino acids (Fmoc-L-Phe-OH and
Fmoc-3-(3-pyridyl)-L-Ala-OH), so the pair is a one-reagent swap in an otherwise identical synthesis. A charged
wedge (a carboxylate on Arg412) would have been a stronger interaction and a **worse experiment**: a
net-charge change under PME needs a finite-size correction that does not cancel between differently-sized
boxes, and the repo's own `assert_charge_consistency` refuses such a wedge outright.

**(ii) The wedge engages a target-side difference.** Thr407 is **Leu in NR4A1 and Val in NR4A2** — a polar
hydroxyl replaced by pure hydrocarbon in both paralogues, so the pyridyl nitrogen finds an H-bond donor in
NR4A3 and nothing at all in either paralogue. It is **within pendant reach of the linker path in all five
confirmed basins**, as is Arg412, so the pair is not an artefact of one basin's geometry.

*Why T407 rather than R412, since both qualify:* the selector took the site with the greater measured E3
clearance (10.3 Å vs 8.7 Å in this basin), and the chemistry supports the same choice independently. **Arg412
is more exposed (RSA 0.78) and far more flexible** — a long, multi-rotamer side chain in a rigid model, so a
pendant designed against it inherits more conformational uncertainty, and an H-bond formed at high solvent
exposure competes with water and is worth less. **Thr407 (RSA 0.28) is small, has one χ₁, and sits partly
shielded**, so both its geometry and the magnitude of the interaction are better determined. Arg412 is one of
the program's seven selectivity handles and remains the natural **second** wedge in the same basin, which makes
the two corroborating rather than redundant.

**(iii) The wedge does not touch the E3.** This is the check that makes the double difference mean what it
says. `S` isolates a *target-side* interaction only because the ligand's solvation, its internal strain and its
entire interaction with the E3 are identical in the two paralogue legs and cancel exactly — the shared binary
and solvent legs are paralogue-independent, which is also why the test needs **ternary legs only**. If the
wedge element could touch the E3, that cancellation would fail. Measured clearance at the chosen position is
**10.3 Å**, and the basin was selected on that measurement.

### Remaining confounds — stated with the proposal, not in a footnote

1. **Thr407's side chain is rigid in this model.** One χ₁ is far less uncertainty than an arginine would
   carry, but it is still a modelled rotamer and the pair is conditional on it.
2. **NR4A1 carries leucine and NR4A2 valine at the aligned position**, so the wedge does not meet an
   unfavourable partner there — it meets a hydrocarbon that simply cannot donate. The expected signal is an
   **NR4A3 gain**, not a paralogue penalty, and its magnitude is bounded by a single partly-buried H-bond:
   roughly **0.5–1.5 kcal/mol against a best-case resolvable difference of 1.12**. A null is a likely outcome
   and must be interpreted accordingly.
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

## 8. Exact nr4a3-program-map.md deltas proposed by this lane

*This lane does not edit nr4a3-program-map.md (several lanes run concurrently and the orchestrator owns it). These are
the precise changes to apply, each with its evidence.*

**D1 — RUNG 5b status.** `[ ] 5b · Inverse linker design — ~$0–20 (mostly $0 CPU)` → **`[x]` … DONE
2026-07-25, re-enumerated 2026-07-26 · $0 REALIZED** — for the construct counts use **L14-6 in §10.7**, not the
number that used to sit here. The `$0–20` band's mid should become the realized **$0**, by the same convention
`valA_mini` already uses; regenerate the ladder total with `vast_cost_model.py` rather than typing it, and
register the superseded value in `pinned-figures.json` in the same commit.

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

**D6b — record the single-residue risk where the design ladder can see it.** RUNG 5a already says "the
categorical chemistry axis rests on a single residue"; RUNG 5b makes it sharper and it belongs beside 5b/5c:
**C397 reaches the 12-atom gate in 96 % of unbiased MD frames, while C420 and C559 reach it in 0 of 75** — a
4–8 backbone-atom deficit that cannot be bought back, because buying it lengthens the linker and pulls
*conserved* cysteines into reach at the same time. **There is no geometric fallback.** The library's only
honest hedge is that it is not all-covalent: the electrophile-free constructs ride the paralogue-unique
**lysine** axis instead, and the 5a-KS matched pair is deliberately non-covalent so the causal test does not
depend on C397 surviving.

**D6c — do not let the retracted CRBN-null claim steer the arm choice.** `vhl|M3` hosts the proposed pair for
a chemical reason (`crbn|M0`'s representative span needs ~29 backbone atoms), **not** because of any
CRBN-vs-VHL preference — that framing is retracted and CRBN remains the sole Pareto-front member. Worth an
explicit decision: `crbn|M0` is the strongest basin *and* carries the best wedge residue anywhere in the set,
**D413, which is Lys in NR4A1 and Ser in NR4A2 — a charge reversal, not a deletion** — at 10.1 Å of E3
clearance. Running the pair there costs a ~26–29-atom linker and buys a much stronger discriminator.

**D6 — the pendant-reach convention.** RUNG 5a's 3.0 Å electrophile arm is shorter than every real pendant
(4.0–8.75 Å for named catalogue branches), so term (a) is **conservative**. Going to a Dab branch shortens the
exact C397 requirement by 8–9 atoms on `vhl|M3`. The counterweight belongs in the same sentence: a longer
pendant relaxes reach to **conserved** cysteines too, degrading intra-NR4A3 chemoselectivity, while leaving the
paralogue argument (a sequence fact) untouched.

---

## 8b. Reconciled against the 2026-07-25 STRATEGY.md corrections

Three orchestrator corrections landed while this rung was running. All three were applied; none changes the
library, and one changes how the matched pair must be justified.

| correction | effect on RUNG 5b |
|---|---|
| **"the discrimination lives on VHL" is RETRACTED** — 0.81–0.96 was the *any-lysine* null, not the *unique-lysine* null the gate uses, and it halves (0.858 → 0.399) when the CRBN arm is restaged assembly-native (CRBN's exit vector had moved **16.5 Å**; VHL's 0.99 Å) | **The pair's justification is rewritten.** It never depended on the retracted claim — the selector ranks on pose persistence and measured E3 clearance among basins that can host a pair — but that was luck, not design, so the arm choice now emits a per-basin audit and states explicitly that `crbn|M0` is excluded for a **chemical** reason (~29 backbone atoms) and **not** for a recruiter preference. |
| **the transfer-anchor conflict is RESOLVED** — registry A (5T35) validated to **0.09 Å** against a solved intact assembly | The feared ~40 Å of transfer-zone variation does not exist, so the term-(b) geometry these constructs are designed to is sound. §6 of the RUNG-5a lane doc listed this as its top unresolved follow-up; it can be closed. |
| **the chemistry axis is one residue deep, quantified** — C397 reaches the 12-atom gate in **96 %** of unbiased MD frames (RSA median 0.416), while **C420 and C559 reach it in 0 of 75** | Added as a stated risk in both the output JSON's `_limits` and §5 above, with an honest account of what the library can and cannot hedge. |

## 9. What RUNG 5b did NOT do, and what should come next

- **No GPU, and none is warranted here.** The next spend on the ladder is still 5a-KS.
- ~~**Re-enumerate the library at the EXEMPLAR placements.**~~ **DONE (LANE 10, then LANE 14 against the
  corrected artifact) — see §10.**
- ~~**Use the span deciles.**~~ **DONE** — every construct now carries `span_window_A.deciles_A`, with the
  3-point summary retained beside it.
- **Linker conformer populations are unmeasured.** Whether the chain actually visits the branch position that
  presents the electrophile to C397 — or the wedge to Thr407 — is a 5c question, and 5b's windows are
  necessary conditions, not populations.
- **★ NEW (§10.5): the segment grid cannot place a branch closer than k = 6 from the warhead**, which is why
  the shortest *realisable* wedge pair on `crbn|M0`'s exemplar is 19 backbone atoms when the *geometry* admits
  one at 16. $0 to close, but it touches a preregistered enumeration and re-opens a known chemical refusal —
  so it is named here rather than done quietly.

---

## 10. ★★ RE-ENUMERATED ON THE CORRECTED 10⁶ ARTIFACT (LANE 14, 2026-07-26, $0 CPU/CI)

> **This section is the live record. Where it and anything above disagree, this section wins; the superseded
> values are listed once in [§11](#11--appendix--superseded-numbers) and nowhere else.**

Inputs: `nr4a3-orientation-basins.json` as committed at **`0fed418c`** — the **matched 10⁶-sample, 12-pose,
seed-20260725 corrected run** (runtime **4303.6 s** against the published run's 4294.9 s), and the driver at
this branch's HEAD. Verification: `nr4a_linker_chem` on CI, run **30184078775**, **GREEN — 54/54 constructs,
0 failures**, RDKit 2025.09.6.

### 10.1 ★★ THE HEADLINE: THE TERM-(a) GATE IS PASSED, NOT FAILED — 7 → **3**, not 7 → 0

**Three meta-basins place an electrophile on C397 inside the preregistered 12-atom gate under the corrected
exact rule.** The gate was not moved and is not being argued with; it is met.

| meta-basin | poses | **exact C397 (3.0 Å gate arm)** | relaxed, superseded | reach fraction at the gate | term (b) |
|---|---|---|---|---|---|
| **`vhl\|M2`** | 6/12 = 0.50 | **10** | 9 | **0.057** | exceeds, 1.43× |
| **`vhl\|M3`** | 9/12 = 0.75 | **11** | 8 | 0.021 | exceeds, 1.4× |
| **`crbn\|M17`** | 3/12 = 0.25 | **12** | 12 | 0.045 | exceeds, **3.87×** |

Gate block, verbatim from the artifact: **58 meta-basins / 192 basins · term (a) 3 · term (b) 40 · nominal 28 ·
basis CATEGORICAL · pass**. Term (b) and the nominal limb are **identical to the published pre-correction run**
(40 and 28), exactly as LANE 10's controlled A/B predicted — so **term (a) is the only limb that moved, and the
comparison is rule-attributable.**

**Why the record said 0, diagnosed rather than guessed.** The "term (a) 7 → 0" reading comes from the artifact
committed at **`d83bb368`** — `samples_per_arm_pose` **250 000**, runtime **1082 s**, term (b) **31**, nominal
**27**. Term (b) is untouched by the reach rule and had no business moving, which is the discriminating
observation; LANE 10 diagnosed it in its own §5.0 as an omitted `--samples 1000000` on the dispatch and re-ran.
The matched 10⁶ successor landed at **8:35 PM ET on 2026-07-25** and is the artifact above. Every figure that
came with the zero is the 250 k run's and is retired in §11: **shortest C397 13 → 10, C420 16 → 16, C559 31 →
27**, and the "three basins reach C397 at 13 (`vhl|M2`, `vhl|M6`, `vhl|M7`)" reading with it. *(Meta-basin IDs
are positional and not comparable across runs at different sampling — LANE 10's finding 0 — so `vhl|M6` and
`vhl|M7` do not denote anything in the corrected run.)*

**And nothing is rescued by a surface the published run never nominated.** Matched on interface patch under the
search's own meta-basin cutoff (Jaccard ≥ 0.6): `vhl|M2` and `vhl|M3` **are** two of the five confirmed basins,
and `crbn|M17` matches **`crbn|M0`** — RUNG 5a's strongest nomination — at Jaccard **0.600**, sharing residues
389, 390, 393, 396, 400, 404, 407, 408, 412. The gate-passing CRBN placement is on the strongest basin's own
surface, reached by a different member.

⚠ **`crbn|M0` itself misses the gate by one atom: exact C397 = 13, reach fraction 0.0.** The strongest basin
does not personally clear the term-(a) gate; the surface it sits on does, via `crbn|M17`.

**Requirements at both placements, corrected** *(exact rule, integer branch positions; "3.0 Å" is the
preregistered gate arm, "Dab" the 8.75 Å catalogue branch the electrophile constructs actually use)*:

| meta-basin | placement | span | floor | comfortable | **C397 @ 3.0 Å** | **C397 @ Dab** |
|---|---|---|---|---|---|---|
| **`crbn\|M0`** | exemplar | 13.42 Å | 11 | **14** | 13 | **11** |
| `vhl\|M3` | exemplar | 12.61 Å | 11 | 13 | **11** | 11 |
| `vhl\|M2` | exemplar | 10.66 Å | 9 | 10 | **10** | 9 |
| `vhl\|M4` | exemplar | 16.84 Å | 14 | 18 | 15 | 14 |
| `vhl\|M14` | exemplar | 8.28 Å | 7 | 8 | 13 | 7 |
| `crbn\|M0` | representative | 23.25 Å | 19 | 29 | 33 | 25 |
| `vhl\|M3` | representative | 9.67 Å | 8 | 9 | 23 | 14 |
| `vhl\|M2` | representative | 17.73 Å | 15 | 20 | 16 | 15 |
| `vhl\|M4` | representative | 21.75 Å | 18 | 26 | 30 | 22 |
| `vhl\|M14` | representative | 24.22 Å | 20 | 31 | 21 | 20 |

The **confirmed-basin identity check passes at Jaccard 1.000 on all five** against the published patches, so
the five IDs denote the same surfaces they were confirmed on and the re-enumeration is matched.

### 10.2 The library survives the corrected geometry intact — and a DIFFERENT defect took three of it

**Casualties from the reach correction: ZERO. Constructs that only ever worked because of the pendant-credit
bug: NONE — and the reason is structural, not lucky.**

Re-running the enumerator against the corrected artifact returns the 21 representative-geometry constructs
**field-for-field identical** — same SMILES, same lengths, same branch positions, same branch windows, same
fidelity numbers. The only differences are metadata the placement work added (`designed_at_placement`,
`placement_basin_id`, and the span deciles replacing the 3-point summary).

**Why, and it is the answer to "which constructs only worked because of the bug".** RUNG 5b never used the
relaxed rule. Branch positions and lengths here come from `linker_design.branch_position_window` /
`min_linker_atoms_exact` — the exact three-ball, integer-branch-position kernel — and **both pre-date the
correction**. The defect lived in `basin_geom.linker_can_visit`, which only `nr4a3_basin_search` consumed.
So the correction changes **which placements are worth designing on**; it cannot change a molecule this rung
drew, and it did not. *(Verified by diff, not by reading the code: the 21 records are identical.)*

**What DID cost constructs is a defect this lane found — see §10.4.** Applying the preregistered wedge
chemistry rule inside the enumerator drops every pyridyl/phenyl construct aimed at a site that fails it:

| library | before the wedge fix | **after** |
|---|---|---|
| at the **term-(a) exemplar** | 45 | **36** (9 · 9 · 6 · 6 · 6 across `crbn\|M0` · `vhl\|M3` · `vhl\|M2` · `vhl\|M4` · `vhl\|M14`) |
| at the **representative** | 21 | **18** (1 · 9 · 6 · 1 · 1) |
| combined, RDKit-verified | — | **54 / 54, 0 failures** |

The twelve dropped constructs were aimed at **C397** (nine of them) or **N400** (three) — neither of which
satisfies "NR4A3 presents a donor and BOTH paralogues do not". They are not weak wedges; they are wedges that
cannot report.

**The filter's own control still reads honestly at both placements** (`filter_control_reading`): at the
exemplar all five basins are retained on merit; at the representative `crbn|M0`, `vhl|M4` and the weak control
`vhl|M14` survive only as labelled failures. The filter tests whether a *linker* can hold a basin, not whether
the *basin* is good — unchanged, and still the correct reading.

### 10.3 The matched pair: the basin and the wedge site stand, the shared LENGTH does not

**RECOMMENDED — `crbn|M0` at its term-(a) exemplar (`crbn|exitvec_07|b0`, pose `exitvec_07`, span 13.42 Å):**

| | |
|---|---|
| **basin** | **`crbn\|M0`** — 11/12 = 0.917 pose persistence, **7.5×** over the term-(b) null: RUNG 5a's strongest nomination |
| **wedge element** | 3-(3-pyridyl)-L-alanine (*d*) vs L-phenylalanine (*d₀*) — an aza-scan branch residue |
| **wedge target** | **Thr407** — **Leu** in NR4A1, **Val** in NR4A2, RSA 0.279: the donor is removed in *both* paralogues |
| **linker** | **19 backbone atoms**, branch at **k = 6** from the warhead (window k ∈ [2, 6]), **0.27 kT** of chain strain |
| **E3 clearance at the wedge** | **9.04 Å**, measured at *this construct's own* (n, k) — the site-derivation probe value is 8.60 Å |
| ***d*** | `crbnM0@ex_5amide_e4-a2_pyr3` — `C1CC(=O)NC(=O)C1N2C(=O)C3=C(C2=O)C(=CC=C3)NC(=O)COCCOCCOCCC(=O)N[C@@H](Cc7cccnc7)C(=O)NCCC(=O)Nc4ccc5[nH]cc(C(=O)OC)c5c4` |
| ***d₀*** | `crbnM0@ex_5amide_e4-a2_ph` — the same string with `Cc7cccnc7` → `Cc7ccccc7` |
| **RDKit measurement** | **C₄₃H₄₆N₈O₁₃** vs **C₄₄H₄₇N₇O₁₃**, identical at **64 heavy atoms**, identical net charge, rotatable bonds and (S) centre; delta = one aromatic C–H → N |

**Every property the pair had to preserve is preserved, and each is measured rather than asserted:** one
element and it is one atom; identical formal charge / heavy atoms / rotatable bonds / (S) centre; the wedge
engages a target-side difference of the right *kind* under the preregistered chemistry rule; and the wedge does
not touch the E3, so the shared binary and solvent legs still cancel exactly and **only ternary legs are
needed**. The clearance is now filtered on the **construct's** value (≥ 6 Å), not the site probe's.

**★ WHAT DOES NOT SURVIVE: the "one placement, one molecule" reading.** §6a sold the pair on *"the same
geometry carries the covalent handle … so the wedge pair and the reversible-covalent series can be built on one
placement instead of two."* Checked directly on the corrected geometry rather than inferred:

| on `crbn\|M0`'s term-(a) exemplar | shortest backbone that admits it |
|---|---|
| the **covalent** handle (Dab pendant → C397 SG) | **13** atoms (11 by the artifact's own exemplar reach; the enumerated series sits at **14**) |
| the **wedge** (aryl branch residue → T407) | **16** atoms geometrically; **19** as actually realisable — see §10.5 |
| **both on one chain** | **16** atoms — T407 opens at k ∈ [2, 3] at n = 16, C397 is open from n = 13 |

So **the placement claim survives verbatim** — one placement does host both mechanisms, and §6a's specific
figure *"C397 reachable at 11 backbone atoms with a Dab pendant"* is **exactly unchanged** at the corrected
geometry. What fails is the implication that they share a *length*: the covalent series is at 14 and the wedge
pair at 19, five atoms apart, and five atoms is now a measured selectivity cost (§10.6). **A single molecule
carrying both needs 16 atoms and the current segment grid cannot build it (§10.5).**

**The best replacement, if length is allowed to lead.** Every enumerated *d*/*d₀* pair, shortest first:

| n | basin | placement | wedge | E3 clearance | basin evidence | collision bracket at this length |
|---|---|---|---|---|---|---|
| **16** | `vhl\|M3` | representative | T407, k = 11 | **10.5 Å** | 0.75 poses, 1.4× | **exactly 0.081** (a measured point) |
| 18 | `vhl\|M3` | exemplar | T407, k = 6 | — | 0.75 poses, 1.4× | between 0.081 and 0.258 |
| **19** | **`crbn\|M0`** | **exemplar** | **T407, k = 6** | **9.04 Å** | **0.92 poses, 7.5×** | between 0.081 and 0.258 |

The recommendation leads on **basin evidence**, which is what Tier 2 measured, and `crbn|M0` wins that on both
axes by a wide margin. The 16-atom `vhl|M3` pair is the answer if **length** leads. The two disagree, the
disagreement is the finding, and it is emitted as `matched_pair_alternatives_by_length` rather than resolved by
a threshold. *(Note the wedge pair carries no electrophile, so the collision bracket is not a liability of that
molecule as drawn — it is the price its length would carry once the covalent handle is installed on the same
chain, which is the design the library exists to enable.)*

### 10.4 ★★ THE DEFECT: the pair reported one wedge site and its molecules were built for another

**Found here, and it reached the recommended pair.** The preregistered wedge chemistry rule — *NR4A3 must
present a side-chain H-bond donor and BOTH paralogues must not* — was made binding in `matched_pair()` but
**not** in `enumerate_library()`, which went on taking the site with the most E3 clearance. The emitted record
therefore read `wedge_target_residue: T407` while its own *d*/*d₀* molecules carried `branch_target: C397`.

**Why that is not cosmetic.** C397 is **Asn** in NR4A1 and **Ser** in NR4A2 — *both paralogues keep an H-bond
partner*. A pyridyl nitrogen there is precisely the "`S` ≈ 0 by construction" trap the rule exists to prevent,
and worse than the Ile396 case the rule was written against, because the paralogue may make the *better*
contact. Nothing crashed; the metadata simply described a different molecule from the one emitted.

**Measured, not estimated:** over the corrected artifact the two selections disagreed on **8 of 10**
(basin × placement) records —

| placement | enumerator picked | pair record claimed |
|---|---|---|
| `crbn\|M0` exemplar | **C397** (14.29 Å) | T407 (8.6 Å) |
| `vhl\|M3` exemplar | C397 (7.07 Å) | T407 (6.4 Å) |
| `vhl\|M2` · `vhl\|M4` exemplar | C397 | *no valid site* |
| `vhl\|M14` exemplar | N400 | *no valid site* |
| `crbn\|M0` representative | D413 (10.41 Å) | *no valid site* |
| `vhl\|M2` representative | C397 (8.23 Å) | *no valid site* |
| `vhl\|M14` representative | L406 (8.41 Å) | T407 (6.29 Å) |
| `vhl\|M3` · `vhl\|M4` representative | T407 | T407 ✔ (agreed by luck) |

**Fixed by having ONE selector, not two agreeing conventions** — an agreeing convention is exactly what
drifted. `select_wedge_site()` applies the clearance test, the chemistry rule and an explicit C397 exclusion
(the categorical handle's cysteine must not host the marginal wedge, or a null from 5a-KS is unreadable), and
both call sites go through it. `matched_pair()` additionally **refuses** if the emitted molecules'
`branch_target` is not the site it is about to report. Three new tests pin it.

**Second fix in the same area.** `e3_clearance_A` on a wedge site is a **probe** value, measured at
`n = span floor + 4` with *k* at the middle of that site's window, because the sites are derived before any
molecule exists. The pair was reporting that number against a molecule of a different length and branch
position. It is now **re-measured at the proposed construct's own (n, k)**, the 6 Å validity test is applied to
*that* value, and the probe value is kept beside it under its own key so the two cannot merge again.

### 10.5 Why the shortest realisable wedge pair is 19 atoms when the geometry admits 16

Not a geometric limit — a **grid** limit, and it is worth naming because it costs three backbone atoms on the
recommended pair. A branched construct's backbone is `handle-ish (4) + SEG1 + branch node (3) + SEG2`, and the
branch index counted from the warhead is `k = |SEG2| + 4`. The smallest amine-side segment in the enumeration
is `a2` (2 atoms), and zero-length segments are refused (a branch residue directly acylating the warhead
aniline is the acylurea the assembler already refuses). **So the grid's floor is k = 6**, verified over every
enumerated and rejected construct.

T407's branch window on `crbn|M0`'s exemplar is k ∈ [2, 3] at n = 16 and only reaches k = 6 at n = 19. Hence
19. Closing this means adding a shorter, chemically sound amine-side segment — **$0**, but it edits a
preregistered enumeration and re-opens a known chemical refusal, so it is listed in §9 rather than done here.

### 10.6 ★ The selectivity-vs-length ranking, and where the honest cut-off is

LANE 13's matched-construct test (5 657 placements, same placement / warhead exit anchor / E3 anchor / budget)
priced backbone length as a **selectivity** cost: P(a paralogue cysteine is also reached | an NR4A3-unique one
is) = **0.000 at 12, 0.000 at 14, 0.081 at 16, 0.258 at 20**. A construct reaching C397 at 13 atoms is
therefore *more selective* than one reaching at 16, not merely more synthesisable. The full ranking is emitted
as `selectivity_vs_length_ranking`; the shape of it:

| n | what sits there | collision bracket |
|---|---|---|
| **14** | the whole `crbn\|M0` **and** `vhl\|M3` exemplar covalent series — 12 constructs | **0.000**, a measured point |
| 16 | the `vhl\|M3` representative series (incl. the shortest wedge pair) and the `vhl\|M2` exemplar series | **0.081**, a measured point |
| 18 | `vhl\|M3`'s exemplar wedge pair, `vhl\|M4`'s series, the weak control's series | between 0.081 and 0.258 |
| 19–20 | the recommended `crbn\|M0` wedge pair; `vhl\|M2`'s representative series | between 0.081 and 0.258 |
| 21–24 | the labelled-failure constructs at the representative | **above 0.258, and open** — the measurement stops at 20 and the trend is rising |

**★ The honest cut-off is 14 backbone atoms**, and it is read off the measurement rather than chosen: 14 is the
longest length at which the reach-only collision probability is still a **measured** zero. Two things stop it
being a gate, and both must travel with it:

1. **No construct in this library reaches C397 at or below the 12-atom term-(a) gate at any placement** — the
   shortest is 14 — so a cut-off at 12 would empty the covalent series entirely. The gate is met by the
   *basin*'s best member (10–12 atoms, §10.1); the *enumerated molecules* start at 14.
2. **On reach AND exposure the collision probability is 0.000 at every measured length.** What the bracket
   bounds is the reach-only number. The axis is currently held up by paralogue-cysteine *burial* — one number
   per residue from one conformer — and the matched paralogue MD ensembles that turn it into a distribution
   were in flight when this was written. **Four measured points are not a curve**: a construct at 18 atoms sits
   *between* 0.081 and 0.258 and that is the whole statement.

### 10.7 Exact nr4a3-program-map.md deltas from THIS lane (additional to §8)

*This lane does not edit nr4a3-program-map.md.*

| # | where | change |
|---|---|---|
| **L14-1** | §WHERE WE ARE, "✅ RESOLVED 2026-07-26 — the covalent route survives; it missed the gate by ONE ATOM" | **Rewrite: it did not miss.** On the matched 10⁶ corrected run (`0fed418c`) term (a) is **3**, not 0 — `vhl\|M2` at **10** atoms, `vhl\|M3` at **11**, `crbn\|M17` at **12**, all inside the preregistered 12-atom gate. The 7 → 0 reading came from the **superseded 250 000-sample** artifact (`d83bb368`, term (b) 31 vs 40), which LANE 10 had already diagnosed as an omitted `--samples`. **The headline is "a gate PASSED", not "a threshold artifact".** |
| **L14-2** | same block, "Shortest corrected reach per residue: C397 13, C420 16, C559 31" | **C397 10 · C420 16 · C559 27.** C559 stays out of contention at any usable length; that conclusion is unchanged. |
| **L14-3** | same block, "3 basins reach C397 at 13 (`vhl\|M2`, `vhl\|M6` at 0.75, `vhl\|M7`)" | **Retire.** Those IDs are the 250 k run's and meta-basin IDs are positional (LANE 10 finding 0), so they denote nothing in the corrected run. Replace with the L14-1 table. |
| **L14-4** | §Tier-2 result in full, "C397 reach" column and item 1 | Corrected exact values at the **12-pose 10⁶** run; label the column **"C397 reach (EXACT rule, 3.0 Å arm)"**. `crbn\|M0` reads **13** and **misses the gate by one atom**; the surface still passes via **`crbn\|M17`**, which matches `crbn\|M0`'s patch at Jaccard **0.600**. |
| **L14-5** | §Tier-2, ⚠ "Every reported C397 reach figure is a LOWER BOUND" | Replace with LANE 10's ✅ CORRECTED text (their delta table), **plus**: the correction moved term (a) 7 → 3 and left term (b) 40 and the nominal limb 28 bit-identical. |
| **L14-6** | §RUNG 5b entry, "1,995 enumerated → 21 retained" | **"at the term-(a) exemplar 3 544 → 36; at the representative 1 791 → 18; 54 combined, RDKit-verified 54/54 (CI 30184078775). The exemplar library is primary and is labelled OPTIMISTIC (best-of-N)."** |
| **L14-7** | §RUNG 5a-KS matched-pair block | **The pair stands** — `crbn\|M0` exemplar, 3-(3-pyridyl)-L-Ala vs L-Phe at **Thr407** — but at **19 backbone atoms**, k = 6, **9.04 Å** of E3 clearance (re-measured on the construct), C₄₃H₄₆N₈O₁₃ / C₄₄H₄₇N₇O₁₃ at **64 heavy atoms**. **Drop "the same geometry carries the covalent handle at 11 atoms so both can be built on one placement" as a one-molecule claim**: the placement hosts both, but the covalent series is at 14 and the wedge pair at 19, and a single chain carrying both needs 16. |
| **L14-8** | **new bullet**, §MECHANISM-FIRST → "Consequence for the design: keep the linker SHORT" | Make it quantitative from the library: **the covalent series starts at 14 backbone atoms, the measured zero-collision ceiling.** Every wedge pair is 16+, i.e. already in the 0.081+ band. **The honest cut-off is 14 and no enumerated molecule reaches the 12-atom gate.** |
| **L14-9** | **new bullet**, wherever the 5b library is described | **The 21-construct library never used the buggy reach rule** — 5b's enumerator has always called the exact three-ball kernel; the defect was in `basin_geom.linker_can_visit`, consumed only by the basin search. Re-enumeration returns the 21 field-identical. **The library lost three constructs to a different defect** (the enumerator ignored the preregistered wedge chemistry rule, §10.4), not to the reach correction. |

---

## 11. Appendix — superseded numbers

*Registered rather than deleted, per CLAUDE.md §1.2. None of these may be quoted; each line's replacement is
named.*

| superseded | where it came from | current |
|---|---|---|
| term (a) **7** (published) and term (a) **0** | pre-correction 10⁶ run `ec6aaf66`; corrected but **250 k** run `d83bb368` | **3** (`0fed418c`, matched 10⁶) — §10.1 |
| shortest corrected reach **C397 13 · C420 16 · C559 31** | the 250 k run | **10 · 16 · 27** — §10.1 |
| "3 basins reach C397 at 13: `vhl\|M2`, `vhl\|M6`, `vhl\|M7`" | the 250 k run; IDs are positional | `vhl\|M2` 10, `vhl\|M3` 11, `crbn\|M17` 12 — §10.1 |
| library **21 constructs** / **22 constructs** | §5 and the old status line; 22 was itself stale by two CI runs | **36 exemplar + 18 representative = 54** — §10.2 |
| exemplar C397 **`crbn\|M0` 11 · `vhl\|M3` 11 · `vhl\|M2` 10 · `vhl\|M4` 14 · `vhl\|M14` 7** at the 3.0 Å arm | §3b, computed on the pre-correction artifact | **13 · 11 · 10 · 15 · 13** — §10.1 *(the Dab-pendant figures 11 · 11 · 9 · 14 · 7 are unchanged)* |
| recommended pair at **15 backbone atoms** | §6a | **19** — §10.3 |
| recommended pair **8.6 Å** of E3 clearance | §6a — a site-derivation *probe* value | **9.04 Å** measured on the construct; 8.60 Å retained as `e3_clearance_at_wedge_site_probe_A` — §10.3, §10.4 |
| representative pair at **11 backbone atoms**, *k* = 6, **66** heavy atoms, **C₄₇H₅₅N₉O₉S / C₄₈H₅₆N₈O₉S**, and the two SMILES printed in §6b | §6b — **stale against its own committed artifact by two CI runs before this lane** | **16** atoms, *k* = 11, **71** heavy atoms, **C₅₂H₆₅N₉O₉S / C₅₃H₆₆N₈O₉S**, clearance **10.5 Å** — the SMILES in `matched_pair_at_representative_geometry` |
| §3a's "`crbn\|M0` needs ~29 backbone atoms and is the least buildable" | already marked superseded by §3b | unchanged as a *representative-placement* statement (29 at the representative); it is not a statement about the basin |
| "52 tests" (31 kernel + 21 driver) | the old status line and the §1 table | **62** (33 kernel + 29 driver) |
