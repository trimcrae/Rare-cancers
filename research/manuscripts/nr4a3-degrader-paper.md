# Computational design of a selective NR4A3 degrader: opening a cryptic pocket in a "ligand-independent" nuclear receptor

> **ACTIVE LEAD MANUSCRIPT (result paper).** Target-centric paper on the NR4A3 degrader, split out from
> the EMC-program roadmap ([`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md)) on 2026-06-25 per
> [`nr4a3-degrader-paper-positioning.md`](./nr4a3-degrader-paper-positioning.md). The roadmap remains
> the EMC-program paper (driver framing + the fusion-specific ASO / immuno / registry routes); this
> paper is the degrader's own publish-to-convince deliverable, led by the target, with EMC as the lead
> clinical application among several NR4A3/NR4A-degradation indications.

*Draft (2026-06). Authors/affiliations TBD. In-silico design + feasibility study — no wet lab; no
molecule synthesized. Every claim is sourced or computed and labelled with its weight. The 30 ns
production metadynamics is **complete (converged)**; the headline numbers below are from it, and the 5 ns
validation is retained only where explicitly labelled as the preliminary cross-check.*

## Abstract
NR4A nuclear receptors (NR4A1/2/3) are textbook "undruggable" transcription factors: the canonical
Nurr1/NR4A2 crystal structure shows a ligand-binding pocket occluded by bulky side chains, and NR4A3 has
no experimental structure at all. Yet NR4A3 is a compelling **selective** degradation target — it drives
two cancers by *gain of NR4A3*: extraskeletal myxoid chondrosarcoma (EMC; EWSR1/TAF15::NR4A3 fusion,
which retains a near-intact NR4A3 ligand-binding domain) and acinic cell carcinoma of the salivary glands
(AciCC; NR4A3 over-expression via enhancer hijacking), and in both the goal is to remove NR4A3 while
**sparing NR4A1/2** (whose loss is toxic, notably leukaemogenic). We present a **computation-only**
program to design a **selective NR4A3 degrader**. (1) Calibrated against a
nuclear-receptor panel, the NR4A3 orthosteric pocket is borderline/occluded in the static AlphaFold
model (fpocket druggability 0.495, below the calibrated drug-bound band of 0.53–0.68), consistent with
the family's reputation — and we show the apparent "0.80 druggable" reads reported for Nurr1 are a
*non-orthosteric* cavity present even in the occluded crystal, not a model artifact. (2) **Well-tempered
metadynamics opens a cryptic druggable pocket**: the orthosteric Rg coordinate expands and the opened
conformations reach fpocket druggability **0.931** on the converged 30 ns run (the 5 ns validation gave
0.751) — above every experimentally drug-bound NR pocket in our panel — the first pocket-dynamics
evidence for NR4A3, paralleling the experimentally demonstrated dynamic pocket of Nurr1 (de Vera 2019)
and an MD-revealed cryptic pocket in Nur77. (3) We map 7
NR4A3-vs-NR4A1/NR4A2 divergent pocket residues as **selectivity handles** (5 of which stay pocket-facing
in the opened, druggable ensemble — a measured, not assumed, property), enabling a tunable selectivity
profile. (4) Treating the opened pocket as a *programmable* design axis, we run the **same cryptic-pocket
metadynamics on NR4A1 and NR4A2** to build **state-matched opened-pocket ensembles for all three
paralogues**, and dock one candidate library into each — yielding a per-candidate **selectivity
fingerprint across the NR4A family** (tunable from NR4A3-selective to pan-NR4A) and removing the
opened-target-vs-static-off-target bias that confounds naive selectivity docking. We prime a degrader/E3
ternary-complex design on the opened pocket. The work is governed by a **pre-registered falsification
scheme** (calibrated thresholds fixed before the production results). The NR4A3-selective agent — binding
the NR4A3 LBD shared by the EMC fusion and over-expressed wild-type NR4A3 — is the lead, addressing
**EMC, acinic cell carcinoma, and the broader NR4A3-rearranged sarcoma spectrum**; a deliberately
**pan-NR4A** agent is a distinct second design mode for *ex-vivo* immuno-oncology (reversing T-cell
exhaustion, which needs all three NR4As degraded; Chen 2019), while the AML-causing NR4A1+NR4A3
combination is an explicit **anti-target** the matrix is used to design *away* from. The set is bounded by NR4A3's
tumour-suppressor roles elsewhere (AML, HCC). EMC is the entry point, not the endpoint.

## 1. Background and rationale
NR4A receptors are constitutively active orphan nuclear receptors whose canonical ligand pocket is
collapsed/occluded in crystal structures (Nurr1, PDB 1OVL; Wang 2003), the structural basis of their
"undruggable" reputation. That reputation is a statement about *static* structures: Nurr1's pocket is in
fact **dynamic and expands** from the collapsed crystal conformation to bind fatty acids (de Vera 2019),
an MD study reported a cryptic druggable pocket in Nur77, and validated NR4A ligands engage
cryptic/surface sites. NR4A3 itself has **no experimental structure and no published pocket-dynamics
analysis** — the gap this paper fills. Full reconciliation of the "undruggable" reputation with our
findings, with references and the NR4A-family precedent, is in
[`../modalities/nr4a3-druggability-reconciliation.md`](../modalities/nr4a3-druggability-reconciliation.md).

Because occupancy pharmacology is precluded by the collapsed pocket, the apt modality is **degradation**:
recruit the retained, ordered NR4A3 LBD to an E3 ligase and remove the protein. This is target-generic
(it degrades NR4A3 whether wild-type or in the EMC fusion), which is why the program is framed around
NR4A3 rather than EMC specifically.

## 2. Results

### 2.1 The static orthosteric pocket is borderline — calibrated, not just asserted
fpocket assigns the NR4A3 orthosteric pocket (Pocket 5, residues 406–534, carrying all 7 selectivity
handles) a druggability of **0.495**. To make that interpretable we ran the same pipeline on a
nuclear-receptor calibration panel ([`../modalities/nr4a3_calibration.py`](../modalities/nr4a3_calibration.py)):
- experimentally **drug-bound** NR pockets score **0.53–0.68** (PPARγ/rosiglitazone 0.599, ERα/estradiol
  0.586, Nurr1-holo 0.677, Nur77-holo 0.529) → calibrated druggable threshold **D\* = 0.53**;
- fpocket **`max` is non-discriminating** (even the occluded 1OVL crystal scores 0.864 at a
  *non-orthosteric* cavity) — so the widely-quoted "Nurr1 ~0.8" is **not** the orthosteric pocket, and is
  present in both model (0.801) and crystal (0.864), i.e. **not an AlphaFold artifact**;
- our AF2 model does **not** over-call (NR4A2 model 0.801 ≈ 1OVL crystal 0.864), so NR4A3's static
  **0.495 is conservative**.
Thus the static orthosteric pocket sits *just below* the validated druggable band — concordant with
"undruggable", and the right starting point for the cryptic-pocket question.

### 2.2 Metadynamics opens a druggable cryptic pocket (30 ns production)
Well-tempered metadynamics on the radius of gyration of the Pocket-5 lining Cα atoms (method:
[`../modalities/metad-methods-appendix.md`](../modalities/metad-methods-appendix.md)) drives the pocket
open (CV Rg ~0.5 → ~1.05 nm). On the converged **30 ns** run (600 frames), per-frame fpocket on the
opened conformations reaches druggability **0.931** (`crosses_0.5 = True`) — **above every drug-bound NR
pocket in the calibration panel** and well above D\* = 0.53; SASA of the lining residues rises (+6.1 nm²,
86.8 % of frames more open than baseline). (A 5 ns validation gave a consistent 0.751.) This is the
**first evidence of a dynamic druggable pocket in NR4A3**, paralleling Nurr1 (de Vera 2019). Gate scoring
([`../modalities/nr4a3-druggability-prereg.md`](../modalities/nr4a3-druggability-prereg.md)): **Gate 2
(opened state druggable) PASSES** and **Gate 3 (energetic accessibility) PASSES**. The naive
closed→fully-open cost is ~38 kcal/mol, but that is the cost to reach the *most-open* edge (Rg 1.06, the
under-converged sampling frontier), not a *druggable* state: correlating per-frame druggability with
F(Rg) shows the pocket is **already druggable (fpocket 0.80) at Rg ≈ 0.72, in the well-sampled basin, at
only ~0.76 kcal/mol** — thermally accessible. So the single static structure (0.495) understated
druggability; the thermally-populated ensemble is robustly druggable at negligible cost, rising to 0.93
toward the open edge. *(Registered Gate-2 sub-check — now COMPLETE and CONFIRMED. The handle-facing analysis
(`../modalities/nr4a3_handle_facing.py`, run 2026-06-26 on the 30 ns trajectory) shows the opened,
druggable frames keep the selectivity handles pocket-facing: across the druggable frames (fpocket ≥
D\*=0.53) a mean of **5.0/7** handles point into the cavity and **87.5 %** keep ≥4 facing. Five are
reliably pocket-facing — **L406, T410, I484, I531, L534** (≥0.875 of druggable frames) — while **T407
and R412 mostly splay outward** (facing in 0.0 and 0.25 of druggable frames), so the demonstrated
selective-engagement set is those five, not all seven. This is also the precondition for the warhead
screen's handle-contact scoring (§2.4). An unbiased "release" run was attempted as orthogonal
confirmation of metastability but is not required — Gate 3 is resolved by the energetics above — and its
pipeline's startup crash is now fixed (pending a confirmation run).)*

### 2.3 Selectivity handles for an NR4A3-selective (NR4A1/2-sparing) warhead
Aligning the NR4A3 pocket to NR4A1/NR4A2 ([`../modalities/nr4a-selectivity.json`](../modalities/nr4a-selectivity.json))
identifies **7 divergent Pocket-5 residues** — L406, T407, T410, R412, I484, I531, L534 — as selectivity
handles. All 7 are within the metadynamics CV; of these the opened, druggable ensemble keeps **5
pocket-facing** (L406, T410, I484, I531, L534 — §2.2), so those five are the realistically *engageable*
handles a warhead can exploit (T407 and R412 mostly splay outward). This design specification lets the
*same* opened pocket be tuned **NR4A3-selective** (engaging the divergent handles; for the fusion sarcomas,
sparing the NR4A1/NR4A3 myeloid tumour-suppressor function) or deliberately **pan-NR4A** (engaging the
conserved pocket residues; for ex-vivo immuno-oncology) — §3.

### 2.4 Warhead screen + the family-wide selectivity matrix (in progress)
With the pocket validated as druggable and accessible, we screen a **selective warhead** against the
*opened* conformer (`nr4a3_warhead.py` + `gpu-warhead-aws.yml`): it extracts the most-druggable opened
conformer (frame 300, fpocket 0.931), docks a real ChEMBL NR4A library into NR4A3-opened **and** the
aligned NR4A1/NR4A2 pockets, and ranks by a selectivity margin + engagement of the **5 pocket-facing**
handles (§2.3). A first screen returns NR4A3-favoured chemotypes (e.g. an NR4A3-active scaffold,
ΔdG ≈ +1.7 kcal/mol vs the paralogues); these docking margins are **triage priors, not affinities**.

**The selectivity matrix.** A central methodological point: docking the *opened* NR4A3 pocket against
*static* NR4A1/2 models biases toward apparent selectivity, because — by our own argument (de Vera 2019;
the Nur77 cryptic pocket) — the paralogue pockets are likely cryptic too. We therefore run the **same
metadynamics on NR4A1 and NR4A2** (one pipeline; paralogue CV/LBD mapped to NR4A3 by BLOSUM62 alignment)
to obtain **state-matched opened-pocket ensembles** for all three, and dock one library into each. Each
candidate then carries a **selectivity fingerprint** across the family, partitioning the library into
NR4A3-selective (EMC/AciCC), pan-NR4A (ex-vivo immuno), and the AML-associated NR4A1+NR4A3 **anti-target**
cells (§3). This makes the divergent-handle map a *demonstrated, tunable* design axis rather than an
assertion. A de-novo structure-based generative layer (DiffSBDD/Pocket2Mol), conditioned on the divergent
handles (selective) or the conserved residues (pan), is primed to populate empty cells. **Docking
nominates; quantitative selectivity requires endpoint free energy** — MM-GBSA with per-residue
decomposition, and selectivity FEP on the leads — which the state-matched ensembles enable. Once a warhead
SMILES exists, the NR4A3–PROTAC–E3 ternary-complex model (`nr4a3_ternary.py`) scores degradable-lysine
geometry per paralogue (degradation selectivity ≠ warhead-binding selectivity). **No molecule is
synthesized; this is design prep.** Run instructions + program state:
[`../modalities/nr4a3-degrader-next-steps.md`](../modalities/nr4a3-degrader-next-steps.md).

## 3. Indication landscape — a programmable selectivity matrix (EMC is the entry point, not the endpoint)
Detail + references: [`nr4a3-degrader-broader-indications.md`](./nr4a3-degrader-broader-indications.md).
The family-wide ensembles (§2.4) let a degrader be designed for a chosen NR4A *combination*. A cell of
that matrix is a real application only where the disease wants those paralogue(s) **degraded** (direction
matters: degrading neuroprotective Nurr1/NR4A2 in Parkinson's would be the *wrong* direction, so most
single-paralogue cells are not degrader indications) — and some combinations are actively harmful. So the
matrix has three kinds of cell:

**Lead — NR4A3-selective (the validated path):**
1. **EMC** — EWSR1/TAF15::NR4A3 fusion; clean single-driver proof-of-concept.
2. **Acinic cell carcinoma (AciCC) of the salivary glands** — driven by **NR4A3 over-expression via
   enhancer hijacking** (Haller, *Nat Commun* 2019; cooperates with MYB). NR4A3 is the diagnostic driver;
   a selective degrader removes it directly. **More common than EMC**, materially enlarging the market.
3. **Other NR4A3-rearranged sarcomas** — the EMC fusion-variant spectrum.

**Second design mode — pan-NR4A (a distinct molecule, not a contingency):** reversing CD8⁺ T-cell
exhaustion (NR4A-deficient CAR-T cells control solid tumours better; Chen, *Nature* 2019) **requires
degrading all three NR4As**. This is the *opposite* selectivity profile, deliberately designed for from
the conserved pocket residues, and scoped to **ex-vivo / transient** use (CAR-T manufacturing) so the
systemic-toxicity bound below does not apply. The same matrix that yields the selective lead yields this.

**Anti-target — NR4A1+NR4A3 (design *away* from):** NR4A1/NR4A3 are myeloid **tumour suppressors** —
combined loss causes AML (Mullican, *Nat Med* 2007); NR4A3 is also tumour-suppressive in HCC/breast/
lymphoma (Safe & Karki 2021). This cell is a liability, not an indication; the matrix is explicitly used
to *avoid* it (and is *why* NR4A1-sparing selectivity (§2.3) is mandatory for the systemic lead). Showing
the method can design **into** NR4A3-only and **away from** NR4A1+NR4A3 is itself a safety-design result.

## 4. Methods (reproducible, no wet lab)
Scripted in `research/modalities/`, run as managed AWS SageMaker GPU/CPU jobs (GitHub Actions
`gpu-*-aws.yml`). Structure: AlphaFold2 (AFDB) + fpocket (file→pocket mapping derived from data,
`fpocket_lib.py`). Cryptic pocket: OpenMM + PLUMED well-tempered metadynamics with checkpoint/restart and
fail-loud pre-flight guards ([`../modalities/metad-methods-appendix.md`](../modalities/metad-methods-appendix.md)).
Calibration: NR-LBD panel ([`../modalities/nr4a3_calibration.py`](../modalities/nr4a3_calibration.py)).
Falsification: pre-registered gates ([`../modalities/nr4a3-druggability-prereg.md`](../modalities/nr4a3-druggability-prereg.md)).
Selectivity: Biopython BLOSUM62 alignment vs NR4A1/NR4A2. **Family-wide ensembles:** the *same*
metadynamics pipeline is run on NR4A1 (P22736) and NR4A2 (P43354) — one target-agnostic script whose
paralogue LBD trim + Pocket-5 CV residues are mapped to NR4A3 by the same BLOSUM62 alignment, with
fail-loud guards + an audit log — to produce state-matched opened-pocket ensembles for the selectivity
matrix (§2.4). **Warhead / matrix:** smina docking of a real ChEMBL NR4A library into each paralogue's
metad-opened conformer; per-candidate matrix cells assigned by `selectivity_fingerprint.py` (engage/margin
thresholds; unit-tested). **Quantitative tier (planned):** MM-GBSA with per-residue decomposition, then
selectivity FEP on the leads — enabled by the state-matched ensembles; docking scores are used only as
triage priors. All parsing/mapping/classification logic is in pure, unit-tested modules (TESTING.md).

## 5. Limitations
In-silico throughout; no molecule synthesized; broader indications (§3) are **motivation, not
demonstrated efficacy**. The structure is an AF2 model (NR4A3 is uncrystallized) — the MD addresses
exactly the single-snapshot limitation. The headline druggability **0.931** is from the converged **30 ns
biased (metadynamics)** run (the 5 ns validation gave 0.751); the metadynamics samples are biased toward
opening, so per-frame druggability is a structural-feasibility readout, with the free-energy cost of
reaching a druggable state taken from F(Rg) (§2.2, Gate 3). The registered handle-facing check is now **complete and CONFIRMS** the
handles stay pocket-facing in the druggable frames (mean 5.0/7; §2.2) — with the caveat that two of the
seven (T407, R412) mostly point outward, so the demonstrated selective-engagement set is five handles,
not seven. fpocket druggability is a geometric screen, not affinity. Selectivity handles are a
specification (now with a measured pocket-facing fraction), not a demonstrated binding margin.
**Selectivity methodology:** docking margins are **triage priors, not affinities**; a quantitative
selectivity claim needs endpoint free energy (MM-GBSA with per-residue decomposition, selectivity FEP on
the leads), and even then FEP on a cryptic/induced-fit pocket is sampling-limited. The selectivity matrix
(§2.4) is only credible because the paralogues are treated **state-matched** (same metadynamics), not
opened-target-vs-static-off-target; until the NR4A1/NR4A2 runs complete, the first warhead margins use
static paralogue pockets and are upper bounds on selectivity. With no wet lab, the strongest honest claim
is **"computationally designed for, and predicted to have, the intended selectivity profile,"** not
"selective." Matrix cells are gated by degradation *direction* and bounded by the AML anti-target (§3).

## 6. Falsification (pre-registered)
Every gate has a fixed pass/fail set *before* the production numbers
([`../modalities/nr4a3-druggability-prereg.md`](../modalities/nr4a3-druggability-prereg.md)); a
pre-registration deviation (Gate 0 metric) is disclosed in that file's deviation log. The route is
abandoned (weight shifting to ASO/immuno backups in the roadmap) if the opened state is not druggable,
not energetically accessible, or no selective drug-like binder can be designed.

## References (verified; collate to journal format; run verify-refs before submission)
- Wang Z, et al. *Structure and function of Nurr1 identifies a class of ligand-independent nuclear
  receptors.* **Nature** 423:555–560 (2003). PubMed 12774125. (PDB 1OVL.)
- de Vera IMS, et al. *Defining a Canonical Ligand-Binding Pocket in the Orphan Nuclear Receptor Nurr1.*
  **Structure** 27(1):66–77.e5 (2019). PubMed 30416039.
- *In Silico Adoption of an Orphan Nuclear Receptor NR4A1* (PMC4535767). *[locator to confirm].*
- Haller F, et al. *Enhancer hijacking activates oncogenic transcription factor NR4A3 in acinic cell
  carcinomas of the salivary glands.* **Nat Commun** 10:368 (2019). PMC6341107 / PubMed 30664630.
  (AciCC = NR4A3-over-expression-driven; the second NR4A3-selective indication.)
- Chen J, et al. *NR4A transcription factors limit CAR T cell function in solid tumours.* **Nature**
  567:530–534 (2019). (T-cell exhaustion — needs *triple*-NR4A; the pan-NR4A second design mode, ex-vivo.)
- Mullican SE, et al. *Abrogation of nuclear receptors Nr4a3 and Nr4a1 leads to development of acute
  myeloid leukemia.* **Nat Med** 13:730–735 (2007). PubMed 17515897.
- Safe S, Karki K. *The Paradoxical Roles of Orphan Nuclear Receptor 4A (NR4A) in Cancer.* **Mol Cancer
  Res** 19(2):180–191 (2021). PMC7864866.
- Controls: PPARγ LBD + rosiglitazone (PDB 2PRG; Nolte 1998, Nature 395:137); ERα LBD + estradiol
  (PDB 1ERE; Brzozowski 1997, Nature 389:753). NR4A holo: Nur77 4JGV (THPN), 6KZ5 (cytosporone B);
  Nurr1 5Y41 (PGA1).
- Methods: AlphaFold2 (Jumper 2021, Nature, 10.1038/s41586-021-03819-2); fpocket (Le Guilloux 2009);
  OpenMM; PLUMED (Tribello 2014; PLUMED consortium, Nat Methods 2019).
- EMC clinical context + the fusion-addiction/ASO/surrogate evidence: see the EMC-program roadmap and its
  source memos.

*Medical-integrity note: every citation flagged "to confirm" must be verified against the primary source
before submission; no claim should outrun its cited evidence.*
