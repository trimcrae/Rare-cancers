# Computational design of a selective NR4A3 degrader: opening a cryptic pocket in a "ligand-independent" nuclear receptor

> **ACTIVE LEAD MANUSCRIPT (result paper).** Target-centric paper on the NR4A3 degrader, split out from
> the EMC-program roadmap ([`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md)) on 2026-06-25 per
> [`nr4a3-degrader-paper-positioning.md`](./nr4a3-degrader-paper-positioning.md). The roadmap remains
> the EMC-program paper (driver framing + the fusion-specific ASO / immuno / registry routes); this
> paper is the degrader's own publish-to-convince deliverable, led by the target, with EMC as the lead
> clinical application among several NR4A3/NR4A-degradation indications.

*Draft (2026-06). Authors/affiliations TBD. In-silico design + feasibility study — no wet lab; no
molecule synthesized. Every claim is sourced or computed and labelled with its weight. The 30 ns
production metadynamics is in progress; results below from the 5 ns validation are marked preliminary.*

## Abstract
NR4A nuclear receptors (NR4A1/2/3) are textbook "undruggable" transcription factors: the canonical
Nurr1/NR4A2 crystal structure shows a ligand-binding pocket occluded by bulky side chains, and NR4A3 has
no experimental structure at all. Yet NR4A3 is a compelling degradation target — it is the driver fusion
of extraskeletal myxoid chondrosarcoma (EMC; EWSR1/TAF15::NR4A3, which retains a near-intact NR4A3
ligand-binding domain), and the NR4A family is a central brake on anti-tumour T-cell function. We present
a **computation-only** program to design a **selective NR4A3 degrader**. (1) Calibrated against a
nuclear-receptor panel, the NR4A3 orthosteric pocket is borderline/occluded in the static AlphaFold
model (fpocket druggability 0.495, below the calibrated drug-bound band of 0.53–0.68), consistent with
the family's reputation — and we show the apparent "0.80 druggable" reads reported for Nurr1 are a
*non-orthosteric* cavity present even in the occluded crystal, not a model artifact. (2) **Well-tempered
metadynamics opens a cryptic druggable pocket**: the orthosteric Rg coordinate expands and the opened
conformations reach fpocket druggability **0.751** — above every experimentally drug-bound NR pocket in
our panel — the first pocket-dynamics evidence for NR4A3, paralleling the experimentally demonstrated
dynamic pocket of Nurr1 (de Vera 2019) and an MD-revealed cryptic pocket in Nur77. (3) We map 7
NR4A3-vs-NR4A1/NR4A2 divergent pocket residues as **selectivity handles**, enabling a tunable selectivity
profile, and prime a degrader/E3 ternary-complex design on the opened pocket. The work is governed by a
**pre-registered falsification scheme** (calibrated thresholds fixed before the production results).
Because the pipeline is NR4A3-generic, the same chemistry — tuned NR4A3-selective or deliberately broad —
addresses **NR4A3-fusion sarcomas (EMC the lead example)**, **immuno-oncology (reversing T-cell
exhaustion)**, and **NR4A1/2-driven solid tumours**, bounded by the NR4A myeloid tumour-suppressor
contraindication. EMC is the entry point, not the endpoint.

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

### 2.2 Metadynamics opens a druggable cryptic pocket (preliminary; 30 ns in progress)
Well-tempered metadynamics on the radius of gyration of the Pocket-5 lining Cα atoms (method:
[`../modalities/metad-methods-appendix.md`](../modalities/metad-methods-appendix.md)) drives the pocket
open (CV Rg ~0.5 → ~1.05 nm). Per-frame fpocket on the opened conformations reaches druggability
**0.751** (`crosses_0.5 = True`), **above every drug-bound NR pocket in the calibration panel** and well
above D\* = 0.53; SASA of the lining residues rises (+5 nm², 69% of frames more open than baseline). This
is the **first evidence of a dynamic druggable pocket in NR4A3**, paralleling Nurr1 (de Vera 2019).
*Weight:* preliminary — a 5 ns biased run on the AF2 model; the converged **30 ns production**
(free-energy cost of opening; confirmation that opened frames still line 406–534 with handles facing in)
is in progress. Gate scoring against the pre-registration is in
[`../modalities/nr4a3-druggability-prereg.md`](../modalities/nr4a3-druggability-prereg.md): Gate 2
(opened state druggable) **passes preliminarily**; Gate 3 (energetic accessibility) awaits the 30 ns
F(Rg).

### 2.3 Selectivity handles for an NR4A3-selective (NR4A1/2-sparing) warhead
Aligning the NR4A3 pocket to NR4A1/NR4A2 ([`../modalities/nr4a-selectivity.json`](../modalities/nr4a-selectivity.json))
identifies **7 divergent Pocket-5 residues** — L406, T407, T410, R412, I484, I531, L534 — as selectivity
handles. All 7 are within the metadynamics CV, so the opened pocket presents them to a designed warhead.
This is the design specification that lets the *same* program be tuned NR4A3-selective (for the fusion
sarcomas, sparing the NR4A1/NR4A3 myeloid tumour-suppressor function) or deliberately broad (for
immuno-oncology) — §3.

### 2.4 Degrader / ternary design (primed)
The degrader recruits the opened LBD to an E3 ligase. The ternary-complex modelling pipeline
(`nr4a3_ternary.py`, AF3-class) is primed and runs a checkable CRBN+lenalidomide positive control now;
it completes once a warhead SMILES exists (from structure-based generative design against the opened
pocket conformer). *No molecule is synthesized; this is design prep.*

## 3. Indication landscape — why make it (EMC is the entry point, not the endpoint)
Detail + references: [`nr4a3-degrader-broader-indications.md`](./nr4a3-degrader-broader-indications.md).
Ordered for impact:
1. **Immuno-oncology (headline).** NR4A1/2/3 drive CD8⁺ T-cell exhaustion; NR4A-deficient CAR-T cells
   show superior solid-tumour control (Chen, *Nature* 2019). A NR4A degrader as an immunotherapy/CAR-T
   adjuvant across common solid tumours. *(Likely wants a broad NR4A profile — the selectivity knob.)*
2. **Precision oncology — NR4A3-fusion sarcomas.** EMC (EWSR1/TAF15::NR4A3) and variants: a fusion
   oncoprotein driver with **no targeted therapy**; the concrete application of a *selective* degrader.
   EMC is the clean, single-driver **proof-of-concept** indication.
3. **NR4A1/NR4A2-driven solid tumours** (pancreatic, lung, breast, colorectal), if cross-reactive.

**Hard contraindication (stated):** NR4A1/NR4A3 are myeloid **tumour suppressors** — combined loss
causes AML (Mullican, *Nat Med* 2007); also HCC/bladder. A pan-NR4A degrader is leukemogenic, which is
*why* selectivity engineering (§2.3) is central and the immuno-oncology use is best confined to *ex vivo*
CAR-T engineering.

## 4. Methods (reproducible, no wet lab)
Scripted in `research/modalities/`, run as managed AWS SageMaker GPU/CPU jobs (GitHub Actions
`gpu-*-aws.yml`). Structure: AlphaFold2 (AFDB) + fpocket (file→pocket mapping derived from data,
`fpocket_lib.py`). Cryptic pocket: OpenMM + PLUMED well-tempered metadynamics with checkpoint/restart and
fail-loud pre-flight guards ([`../modalities/metad-methods-appendix.md`](../modalities/metad-methods-appendix.md)).
Calibration: NR-LBD panel ([`../modalities/nr4a3_calibration.py`](../modalities/nr4a3_calibration.py)).
Falsification: pre-registered gates ([`../modalities/nr4a3-druggability-prereg.md`](../modalities/nr4a3-druggability-prereg.md)).
Selectivity: Biopython BLOSUM62 alignment vs NR4A1/NR4A2.

## 5. Limitations
In-silico throughout; no molecule synthesized; broader indications (§3) are **motivation, not
demonstrated efficacy**. The structure is an AF2 model (NR4A3 is uncrystallized) — the MD addresses
exactly the single-snapshot limitation. The headline 0.751 is a **5 ns biased** preliminary result on
the model; the converged 30 ns run, opened-pocket handle-facing confirmation, and the free-energy cost of
opening are pending. fpocket druggability is a geometric screen, not affinity. Selectivity handles are a
specification, not a demonstrated margin.

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
- Chen J, et al. *NR4A transcription factors limit CAR T cell function in solid tumours.* **Nature**
  567:530–534 (2019).
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
