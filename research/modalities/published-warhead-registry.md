# Published warhead registry — the experimentally anchored NR4A chemistry (Workstream B)

**Phase-1 / Workstream-B deliverable of the NR4A3-selective-degrader master brief (deliverables 30–33).**
Machine-readable data: [`published-warhead-registry.json`](./published-warhead-registry.json) (version 1.0.0;
built on a CPU runner, published to the `modalities-cache` branch). Builder + tests:
[`published_warhead_registry.py`](./published_warhead_registry.py),
[`tests/test_published_warhead_registry.py`](./tests/test_published_warhead_registry.py).

> **Why this exists.** The master brief gives *published, experimentally anchored* NR4A chemistry the **same
> or greater** priority as internally generated molecules (rule 18): a de-novo candidate (denovo_401) must
> compete against real chemotypes, not be favoured because it was generated internally. Before this registry
> the program's docking used only a generic ChEMBL NR4A set; the specific published series — the Zaienne
> NOR-1 inverse agonists, the NR4A1/Nur77 and NR4A2/Nurr1 direct binders, and the NR-V04 degrader precedent —
> were cited in the manuscript but never assembled into one versioned, structure-verified, evidence-classed
> table. This is that table.

## What the registry is for

1. **A benchmark for the structural model (Gate 2 / Phase 5).** Docking these compounds into the harmonized
   NR4A3 ensemble + NR4A1/NR4A2 anti-target panels tests whether the receptor models *rationalize known
   active/inactive SAR and known paralogue preferences* — a credibility check the pocket must pass before more
   de-novo design. (The registry supplies the ligands; the docking benchmark is the next step.)
2. **Anti-target discrimination (§7.3).** The NR4A1 and NR4A2 panels are the molecular anti-targets an
   NR4A3-selective molecule must *not* resemble. A candidate that looks like amodiaquine (a cross-NR4A binder)
   is a red flag, not a lead.
3. **Warhead sourcing (Workstream D).** The NR4A3-anchored chemotypes (Zaienne series; cytosporone B) are
   candidate degrader warheads; their PROTAC exit-vector handles are profiled.
4. **The degradation precedent + ternary benchmark (Phase 15).** NR-V04 establishes that paralogue-selective
   NR4A degradation is experimentally real and is the benchmark for the ternary-modeling workflow.

## How structures are verified (never fabricated)

Structures are **not** hard-coded. For every named compound the builder resolves an isomeric SMILES +
InChIKey from up to **three independent public resolvers** — **ChEMBL**, **PubChem PUG-REST**, and **NCI
CACTUS** — and cross-checks them by **InChIKey connectivity skeleton** (the first 14-character block):

| `structure_confidence` | meaning |
|------------------------|---------|
| **high**   | ≥2 resolvers independently agree on the connectivity skeleton |
| **medium** | exactly 1 resolver returned a structure, **or** ≥2 disagree (flagged `skeleton_disagreement`) |
| **unresolved** | no resolver returned a structure — recorded honestly with `smiles: null`, **never invented** |

An optional **`expected_mw` disambiguator** prefers a resolver group whose molecular weight matches the
compound's known mass, which rejects a name that resolved to a derivative/salt of the wrong mass. Two
data-quality issues the cross-check caught on the first build are documented below — this is the verification
layer doing its job, not a curation of convenience.

## Evidence classes

Each compound carries an **evidence class** so functional activity is never silently upgraded to direct
binding (brief 3.2/7.2):

- **direct_binding_structural / _nmr** — a cocrystal or protein-NMR footprint places the ligand on the LBD
  (the strongest anchor).
- **functional_modulator** — modulates NR4A activity in cells but direct LBD binding is not established.
- **functional_nonbinder** — used as an NR4A "modulator" but shown **not** to bind the LBD (a key negative
  control for the docking benchmark — the model should *not* dock it as a strong binder).
- **covalent_crystal** — a covalent LBD cocrystal (special handling; not a clean reversible orthosteric probe).
- **reactive_covalent_functional** — a reactive electrophile warhead (celastrol) — must not go through an
  ordinary noncovalent workflow (brief 21.1).
- **reference_degrader / e3_ligand** — NR-V04 and the VHL/CRBN handles.

## The panels (real, sourced chemistry)

**NR4A3 / NOR-1 (warhead source).** The **Zaienne 2022** fragment-to-inverse-agonist series (ChemMedChem
17(16):e202200259; PMC9542104): a <1 %-hit-rate drug-fragment screen against a Gal4-NR4A3 reporter returned
three chemotypes, one elaborated to a **low-micromolar inverse NOR-1 agonist** that shifted a NOR-1-regulated
gene in cells. The individual member structures are behind the ChemMedChem paywall and are recorded
**unresolved** (series placeholder) rather than guessed; the OA full text (via `fetch-literature` →
`literature-cache`) is what would let a future pass transcribe the elaborated compound.

**NR4A1 / Nur77 (anti-target + warhead source).**
- **cytosporone B (Csn-B)** — the canonical Nur77 agonist (Zhan 2008, Nat Chem Biol) that **also** directly
  binds the Nurr1 LBD by NMR (Munoz-Tello 2021) → a genuine **pan-NR4A direct binder** (positive control, not
  a selectivity exemplar).
- **THPN** — Nur77 LBD **cocrystal** (PDB 4JGV); crystallographic NR4A1 direct-binding anchor.
- **TMPA** — Nur77 functional modulator that **does not** bind the Nurr1 LBD (Munoz-Tello) → an NR4A1-vs-NR4A2
  discriminator.
- **C-DIM8 (DIM-C-pPhOH)** — NR4A1 functional modulator.

**NR4A2 / Nurr1 (anti-target; the hardest paralogue to spare).**
- **amodiaquine**, **chloroquine** — 4-aminoquinolines that **directly bind the Nurr1 LBD** by NMR
  (Munoz-Tello 2021; chloroquinoline-amine Nurr1 activators, de Vera 2021). Cross-NR4A binders → strong
  anti-target controls.
- **5,6-dihydroxyindole (DHI)** and **prostaglandin A1 (PGA1)** — the only NR4A2 LBD cocrystal ligands, each
  **covalently** bound to Cys566 behind helix 12 (covalent, non-orthosteric).
- **C-DIM12 (DIM-C-pPhtBu)** — used as a Nurr1 "activator" but **does not bind the Nurr1 LBD** (Munoz-Tello) →
  a functional-non-binder negative control.

**NR-V04 reference degrader (Wang 2024, J Exp Med 221(3):e20231519).** The first NR4A1-selective PROTAC:
**celastrol** warhead (its C-28 **carboxylic acid** is the tethering vector) + linker + **VHL** recruiter;
degrades NR4A1 while **sparing NR4A2 and NR4A3**, proteasome- and VHL-dependent. Establishes that
paralogue-selective NR4A degradation is experimentally real and is the reason to prioritize **VHL** alongside
CRBN. Stored as a verified **composite** (celastrol + VH032 resolved separately) — see the NR-V04 catch below.

**E3 handles.** **VH032** (VHL; its *trans*-hydroxyproline is required, the epimer is the standard inactive
control) and **lenalidomide** (CRBN; the in-distribution ternary positive control that seats in the CRBN
tri-Trp pocket in this program's §2.4).

## Two data-quality catches (the cross-check working)

- **NR-V04 name collision.** Name-resolving "NR-V04" returns **CHEMBL4779766, a CRBN/glutarimide-PEG PROTAC**,
  which *contradicts* Wang 2024's **VHL-recruiting celastrol** NR-V04 (brief 3.3). The auto-resolved record is
  therefore **not** this compound and is **rejected** rather than trusted; NR-V04 is kept as a verified
  composite of its (independently resolved) celastrol warhead + VH032 VHL ligand. (Golden rule: verify or leave
  unresolved.)
- **DHI derivative substitution.** ChEMBL's name search for "5,6-dihydroxyindole" returned an
  N-ethyl-indole-2-carboxylic-acid **derivative** (wrong mass ~221 Da) while CACTUS returned the correct parent
  indole (~149 Da). The `expected_mw = 149.15` disambiguator selects the parent.

## Reproduce / read

```
# rebuild on a CPU runner (open internet + RDKit); publishes to modalities-cache:
#   gh workflow run warhead-chem-profile.yml --ref <branch>   (this workflow now also builds the registry)
git fetch origin modalities-cache
git show origin/modalities-cache:research/modalities/published-warhead-registry.json | jq '.summary'
```

<!-- CENSUS TABLE (resolved-structure summary) is appended from the runner build below. -->
