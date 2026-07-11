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
compound's known mass, which rejects a name that resolved to a derivative/salt of the wrong mass. The four
data-quality issues the cross-check caught are documented below — this is the verification layer doing its
job, not a curation of convenience.

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
17(16):e202200259; PMC9542104): a <1 %-hit-rate Prestwick drug-fragment screen against a Gal4-NR4A3-LBD
reporter returned three scaffolds (fragments 1 & 2 inverse agonists; 3 a weak agonist at a distinct site).
The **elaborated lead is compound 19 = methyl 5-bromoindole-3-carboxylate** — an indole-3-carboxylate whose
5-position tolerated substitution (5-Cl → 3.5×; 5-Br/5-Ph → single-digit µM), transcribed from the **OA full
text** (fetched via `fetch-literature` → `literature-cache`, 2026-07-11) and now a **resolved** registry entry
(`zaienne_cmpd19`, InChIKey MFOKOKHNSVUKON, MW 254.08). Compound 19 blocks the NOR-1↔SMRT (IC50 9 µM) /
NCoR1 (IC50 12 µM) corepressor interactions and derepresses MYC in cells — **the most experimentally-anchored
NR4A3-directed warhead structure in the registry**, and its tolerated 5-position is a candidate degrader exit
vector. The OA text also yields two more NR4A3 ligands: **PGA2** (weak *direct* NR4A3-LBD agonist, a reactive
cyclopentenone) and **6-mercaptopurine** (enhances NR4A3 but via the N-terminal AF-1, **not** the LBD → an
NR4A3 functional-non-binder control). The individual fragments 1/2/3 and chloro-scan analogues remain
unresolved (the series row is kept as context).

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

## Data-quality catches (the cross-check working) — and why the docking benchmark must use verified SMILES

The cross-check surfaced four name-resolution problems; each is handled honestly rather than papered over.
**The load-bearing consequence:** a docking benchmark must consume the registry's **InChIKey-verified SMILES**,
**not** a single database's name lookup — because the ChEMBL name resolver (which the existing `nr4a3_dock.py`
uses) returns the *wrong structure* for several of these compounds.

- **NR-V04 name collision.** Name-resolving "NR-V04" returns **CHEMBL4779766, a CRBN/glutarimide-PEG PROTAC**,
  which *contradicts* Wang 2024's **VHL-recruiting celastrol** NR-V04 (brief 3.3). The auto-resolved record is
  **rejected**, not trusted; NR-V04 is kept as a verified composite of its (independently resolved) celastrol
  warhead + VH032 VHL ligand. (Golden rule: verify or leave unresolved.)
- **DHI derivative substitution.** ChEMBL's search for "5,6-dihydroxyindole" returned an
  N-ethyl-indole-2-carboxylic-acid **derivative** (~221 Da) while CACTUS returned the correct parent indole
  (~149 Da). The `expected_mw = 149.15` disambiguator selects the parent (high confidence after correction).
- **THPN mis-match.** ChEMBL's "THPN" name resolves to **CHEMBL575966 (MW 361)**, not THPN
  (1-(3,4,5-trihydroxyphenyl)nonan-1-one, C15H22O4 = 266.3). The multi-resolver consensus + `expected_mw = 266.33`
  recover the correct structure (PubChem/CACTUS via the IUPAC synonym) — but a ChEMBL-name-only docking of "THPN"
  would dock the **wrong molecule**.
- **C-DIM8 / C-DIM12 conflation.** "DIM-C-pPhOH" and "DIM-C-pPhtBu" both resolve to the **same** record
  (CHEMBL6196044, MW ~255), inconsistent with a bis-indolyl-methane (~338 / ~378 Da). Both entries carry a
  `structure_caveat`; their name-resolved structures must not be trusted (source SMILES from the Safe-lab paper).

**Implication for Phase 5 (Gate 2 docking benchmark).** Dock the **`structure_confidence: high`** panel members
by their registry SMILES: cytosporone B (pan-NR4A), amodiaquine + chloroquine (NR4A2/pan), THPN + TMPA
(NR4A1-leaning), with celastrol/PGA1/DHI as flagged covalent extras. C-DIM12 is the intended non-binder control
but only once its structure is sourced from the primary paper. **Do not** extend `nr4a3_dock.LIGAND_NAMES` by
name for THPN or the C-DIMs — feed verified SMILES.

## Reproduce / read

```
# rebuild on a CPU runner (open internet + RDKit); publishes to modalities-cache:
#   gh workflow run warhead-chem-profile.yml --ref <branch>   (this workflow now also builds the registry)
git fetch origin modalities-cache
git show origin/modalities-cache:research/modalities/published-warhead-registry.json | jq '.summary'
```

### Resolved-structure census (from the runner build, v1.0.0)

| compound | role | evidence class | conf | MW | InChIKey (skeleton) |
|----------|------|----------------|------|----|--------------------|
| Zaienne 2022 NOR-1 fragment->inverse | warhead_source | functional_plus_fragment | unresolved | — | — |
| Zaienne compound 19 (methyl 5-bromoi | warhead_source | functional_target_engagement | medium | 254.1 | MFOKOKHNSVUKON |
| Prostaglandin A2 (PGA2) | nr4a3_direct_binder | direct_binding_functional | medium | 352.5 | BHMBVRSPMRCCGG |
| 6-Mercaptopurine (6-MP) | nr4a3_functional_modulator | functional_nonbinder | high | 152.2 | GLVAUDGFNGKCSF |
| Cytosporone B (Csn-B) | pan_nr4a_direct_binder | direct_binding_structural_and_nmr | medium | 322.4 | UVVWQQKSNZLUQA |
| THPN (1-(3,4,5-trihydroxyphenyl)nona | nr4a1_direct_binder | direct_binding_structural | high | 266.3 | NVFRHTFJDGAFQS |
| TMPA (ethyl 2-[2,3,4-trimethoxy-6-(1 | nr4a1_functional_modulator | functional_modulator | high | 380.5 | WCYMJQXRLIDSAQ |
| C-DIM8 / DIM-C-pPhOH (1,1-bis(3'-ind | nr4a1_functional_modulator | functional_modulator | medium | 246.3 | VFTRKSBEFQDZKX |
| Amodiaquine | nr4a2_direct_binder | direct_binding_nmr | high | 355.9 | OVCDSSHSILBFBN |
| Chloroquine | nr4a2_direct_binder | direct_binding_nmr | high | 319.9 | WHTVZRBIWZFKQO |
| 5,6-Dihydroxyindole (DHI) | nr4a2_covalent_binder | covalent_crystal | high | 149.1 | SGNZYJXNUURYCH |
| Prostaglandin A1 (PGA1) | nr4a2_covalent_binder | covalent_crystal | high | 336.5 | BGKHCLZFGPIKKU |
| C-DIM12 / DIM-C-pPhtBu | nr4a2_functional_modulator | functional_nonbinder | medium | 246.3 | VFTRKSBEFQDZKX |
| Celastrol | nrv04_warhead | reactive_covalent_functional | high | 450.6 | KQJSQWZMSAGSHN |
| VH032 (VHL ligand) | e3_ligand_vhl | e3_ligand | medium | 472.6 | GFVIEZBZIUKYOG |
| NR-V04 (celastrol-VHL NR4A1 PROTAC) | reference_degrader | reference_degrader | unresolved | — | — |
| Lenalidomide (CRBN ligand) | e3_ligand_crbn | e3_ligand | high | 259.3 | GOTYRUGSSMKFNF |

_Confidence: high = ≥2 resolvers agree on the InChIKey skeleton; medium = 1 resolver or a flagged
disagreement; unresolved = no resolver (recorded null, never invented). The Zaienne LEAD (compound 19)
is resolved from the OA text; the series-context row + NR-V04 stay unresolved. C-DIM8/C-DIM12 carry
name-collision caveats; PGA2 is medium (reactive prostaglandin)._
