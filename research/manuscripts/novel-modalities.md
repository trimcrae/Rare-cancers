# A computational target-assessment and modality program for EWSR1::NR4A3 extraskeletal myxoid chondrosarcoma

**Status: DRAFT v0.1 — pre-clinician-review, pre-wet-lab.** This is a hypothesis-
and methods paper. It contains **no validated drug candidate and no clinical claim.**
Everything below is either (a) a reproducible computation on public data, run in CI
(scripts in `research/modalities/`), or (b) a cited, explicitly-flagged hypothesis.
Nothing here is medical advice or evidence that any agent works in EMC. It does not.

> **Why this paper exists.** Our companion repurposing paper reached an honest but
> deflating conclusion: of existing drugs, only imatinib has any real EMC clinical
> signal, and it is not novel; every genuinely novel lead is preclinical. That paper
> asks "what existing drug might we redeploy?" This paper asks the harder, more
> forward question: **given EMC's specific molecular lesion, what would a
> purpose-built therapeutic program look like, and how far can we de-risk it
> computationally before a wet lab is ever involved?** The answer is "quite far" —
> short of synthesising a molecule or dosing a patient, which is where computation
> must stop and biology must begin.

---

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is a translocation-driven sarcoma defined
in ~90% of cases by an in-frame fusion of *EWSR1* (or, less often, *TAF15*) to the
orphan nuclear receptor *NR4A3*, on an otherwise "quiet" genome with few recurrent
secondary mutations. This makes the EWSR1::NR4A3 oncoprotein the single, near-clonal
driver — an attractive target in principle, but one belonging to two notoriously
hard-to-drug protein classes: an intrinsically disordered transactivation domain and
an orphan-receptor ligand-binding domain. We assess this target objectively and
build the scaffolding for a rational therapeutic program. Using AlphaFold2 models and
open cavity-detection (fpocket), we quantify (i) the predicted disorder of the
EWSR1-derived transactivation domain and (ii) the ligandability of the NR4A3
ligand-binding domain (LBD), testing the hypothesis that, like its NR4A paralogues,
it lacks a classical druggable pocket. We then specify five orthogonal modalities
that do **not** depend on occupying that pocket — targeted protein degradation,
fusion-junction antisense, fusion-directed immunotherapy, synthetic-lethal dependency
mapping, and transcriptional/coactivator disruption — and take each as far as
present-day computation allows. As a worked example we predict, with MHCflurry-2.0,
which EWSR1::NR4A3 junction-spanning peptides are presentable on common HLA-I alleles,
yielding a concrete, tumour-specific neoantigen shortlist for a fusion-directed
vaccine or TCR-T. We close with a prioritised, falsifiable experimental program and
an explicit statement of where computation ends. All analyses are reproducible
(`research/modalities/`), run in CI, and use only public data.

---

## 1. Background: a clean target in a hard-to-drug class

EMC's defining lesion is a gene fusion that creates a chimeric transcription factor:
the N-terminal low-complexity/transactivation domain of EWSR1 (a FET-family protein)
fused to most of NR4A3 (NOR-1), an orphan member of the NR4A nuclear-receptor
subfamily [Refs: Sjögren; Panagopoulos]. EWSR1::NR4A3 accounts for ~62–79% of cases,
TAF15::NR4A3 for ~16%, with rarer partners (TCF12, TFG, FUS) [Ref]. Critically, EMC
otherwise carries **few recurrent secondary mutations** — a "quiet genome" — so the
fusion is not one driver among many; it is, to a first approximation, *the* disease
[Ref]. Two consequences follow:

1. **The good news (clonality).** A therapy that neutralises the fusion or the cells'
   dependence on it should, in principle, hit essentially every tumour cell. There is
   no large mutational landscape offering escape routes the way there is in
   carcinogen-driven carcinomas.

2. **The bad news (druggability).** The fusion joins two of the least
   tractable target classes in medicinal chemistry:
   - the **EWSR1 low-complexity domain**, an intrinsically disordered region (IDR)
     that drives aberrant transcription through phase-separation-like condensate
     behaviour rather than a folded active site [Refs: Boulay 2017; Kwon 2013]; and
   - the **NR4A3 ligand-binding domain**, an *orphan* receptor LBD. For the NR4A
     paralogues Nurr1 (NR4A2) and Nur77 (NR4A1), crystallography showed the canonical
     ligand pocket is **collapsed/autorepressed** — filled by bulky hydrophobic side
     chains, with no classical cavity for a small molecule [Ref: Wang 2003, Nurr1].

So EMC is the paradoxical case of a *clean* target that is *hard to drug by
conventional occupancy*. That framing — not a list of repurposed kinase inhibitors —
is the right starting point, and it points directly at modalities that do not need a
deep ligand pocket. The rest of this paper makes that quantitative.

---

## 2. Structure-based target assessment (reproducible)

**Method.** `research/modalities/nr4a3_structure.py` downloads the AlphaFold2 (AFDB
v4) models for NR4A3 (UniProt Q92570) and EWSR1 (Q01844), reads per-residue pLDDT
(AlphaFold's confidence, a validated proxy for order/disorder: pLDDT < 50 marks
predicted intrinsic disorder [Ref: Tunyasuvunakool/AlphaFold-DB; Akdel benchmark]),
and runs fpocket [Ref: Le Guilloux 2009] to detect and score cavities on the NR4A3
model. We summarise pLDDT over annotated domain windows and report every fpocket
cavity with its druggability score (0–1; >0.5 conventionally "druggable").

### 2.1 The EWSR1-derived transactivation domain is predicted disordered

> **[CI RESULT — fill from `nr4a3-structure-assessment.json`]**
> EWSR1 SYGQ-rich N-terminal region (res 1–264): mean pLDDT = **___**, fraction of
> residues with pLDDT < 50 = **___**. Interpretation: **___**.

This quantifies, on the patient-relevant sequence, the long-held qualitative claim
that the EWSR1 portion is an IDR. A disordered domain has no pocket to occupy — it
is essentially un-druggable by direct small-molecule inhibition, which is the single
most important constraint on EMC drug design and the reason §3 leads with degradation
and transcript/immune modalities rather than inhibitors.

### 2.2 The NR4A3 ligand-binding domain: is there a pocket?

> **[CI RESULT — fill from fpocket]**
> NR4A3 LBD (res ~373–626): mean pLDDT = **___** (fold confidence). fpocket top
> cavity druggability = **___**; number of cavities overlapping the LBD = **___**;
> best LBD-localised druggability = **___**. Interpretation vs. the Nurr1/Nur77
> "no-pocket" precedent: **___**.

The DNA-binding domain (zinc fingers, res ~261–337) is, by contrast, a well-ordered,
sequence-specific fold (**[pLDDT ___]**) — relevant to modalities that block the
fusion from engaging DNA, but historically even harder to drug than the LBD.

### 2.3 What the structure implies for strategy

If the LBD pocket is collapsed (as predicted for the paralogues), then **occupancy-
based agonism/antagonism is the wrong tool**. The rational implication is *event-
driven* pharmacology — degraders and molecular glues that need only a transient,
shallow surface contact to recruit an E3 ligase — and modalities that bypass the
protein's structure entirely (transcript-level, immune). This is the logic of §3.
(A second, testable corollary: any surface ligand reported for NR4A receptors is more
likely to act through an allosteric/surface site than the canonical pocket — a useful
filter for future virtual screens.)

---

## 3. A five-modality program (taken as far as computation allows)

Each modality below is presented with: the **rationale** from EMC biology; the
**computational groundwork** done here or specifiable now; the **decisive wet-lab
experiment** that computation cannot replace; and an honest **maturity** tag.

### 3.1 Targeted protein degradation of the fusion (PROTAC / molecular glue)

- **Rationale.** Degraders remove the protein rather than inhibit a site, so they do
  not need the collapsed LBD pocket; they need only a ligandable handle anywhere on
  the fusion plus a recruitable E3 ligase [Ref: Békés/Crews 2022]. NR4A3 is highly
  fusion-specific and near-clonal — an attractive degradation target.
- **Groundwork specifiable now.** (i) Surface-ligandability scan of the *ordered*
  NR4A3 DBD/LBD surfaces (fpocket output in §2 seeds this); (ii) E3-ligase
  co-expression check — confirm CRBN/VHL are expressed in EMC tumours/cell models
  before assuming a degrader can work (public expression data; a precise, falsifiable
  prerequisite); (iii) a **dTAG surrogate** (FKBP12^F36V knock-in at the fusion locus
  in EMC cells) to prove, before any bespoke degrader chemistry, that *acute*
  degradation of the fusion kills EMC cells — the make-or-break "is this addiction"
  experiment [Ref: Nabet 2018].
- **Decisive experiment.** dTAG knock-in + dTAG-13/V-1 washout viability in
  patient-derived EMC lines (USZ-EMC; NCC-EMC1/2 [Refs: Bangerter; Iwata]).
- **Maturity:** concept + prerequisites computable; no degrader molecule exists. We do
  **not** propose a specific compound — that would be fabrication.

### 3.2 Fusion-junction antisense oligonucleotide (transcript-level)

- **Rationale.** The fusion mRNA junction is a tumour-specific sequence absent from
  either parent transcript; a gapmer ASO complementary to the junction can trigger
  RNase-H cleavage of the chimeric transcript while sparing wild-type *EWSR1* and
  *NR4A3* [Ref: ASO/ Crooke]. The quiet genome means there is one dominant transcript
  to silence.
- **Groundwork specifiable now.** Enumerate junction-spanning antisense windows from
  the modelled fusion transcript; score for specificity (no perfect genomic
  off-target match) and standard gapmer design rules. This is a deterministic,
  scriptable design task (a natural next addition to `research/modalities/`).
- **Decisive experiment.** Junction-ASO knockdown vs. scrambled control in EMC lines;
  rescue specificity by sparing parental transcripts.
- **Maturity:** design computable; delivery to tumour remains the hard, unsolved part.

### 3.3 Fusion-directed immunotherapy: the junction neoantigen (worked example)

- **Rationale.** On a quiet genome, the fusion junction may be the tumour's most
  reliable *public* neoantigen: the handful of residues spanning the EWSR1→NR4A3 seam
  form a peptide present in no normal protein. If presentable on MHC-I, it is a
  rational target for a fusion-directed vaccine or TCR-T — a modality that needs no
  druggable pocket at all.
- **Computational groundwork (done here).**
  `research/modalities/fusion_neoantigen.py` fetches the real UniProt sequences,
  constructs junction-spanning 8–11mers for the modelled fusion, filters to true
  neo-sequences (absent from both parents), and predicts MHC-I binding with
  MHCflurry-2.0 [Ref: O'Donnell 2020] across ten high-frequency HLA-A/-B alleles.

  > **[CI RESULT — fill from `fusion-neoantigen-predictions.json`]**
  > Of **___** novel junction-spanning peptides, **___** are predicted binders
  > (%rank ≤ 2) and **___** strong binders (≤ 0.5). Top epitopes:
  > | peptide | HLA | affinity (nM) | %rank | class |
  > |---|---|---|---|---|
  > | ___ | ___ | ___ | ___ | ___ |

- **Decisive experiment.** Confirm the patient's *actual* breakpoint by RNA-seq (the
  exact junction peptide is breakpoint-specific — see Limitations), then validate
  presentation (immunopeptidomics) and T-cell reactivity ex vivo.
- **Maturity:** prediction pipeline real and reproducible; epitope list is conditional
  on the modelled breakpoint and is a hypothesis to be confirmed per patient.

### 3.4 Synthetic-lethal & dependency mapping (discovery engine)

- **Rationale.** If the fusion itself is hard to drug, find what the fusion makes the
  cell *depend on* — a druggable node downstream or in parallel (synthetic lethality).
  This is discovery, not a therapy in itself.
- **Groundwork specifiable now.** A precise genome-wide CRISPR-knockout screen design
  in the patient-derived EMC lines: library (e.g. Brunello), coverage, timepoints,
  and the key comparison — EMC lines vs. fusion-negative mesenchymal controls — to
  isolate fusion-context dependencies from generic essentials. DepMap contains no EMC
  line today (a gap worth stating), so this must be run in the EMC models, not mined.
- **Decisive experiment.** The screen itself; hits triaged against existing drugs via
  our enumeration pipeline (`research/hypotheses/enumerate-drugs.mjs`) to close the
  loop with the repurposing paper.
- **Maturity:** design ready; no screen has been run — results would be fabricated if
  asserted.

### 3.5 Transcriptional / coactivator disruption

- **Rationale.** EWSR1::NR4A3 acts as an aberrant transcriptional activator, recruiting
  coactivators (the fusion strongly transactivates via the EWSR1 IDR) [Ref]. Agents
  that disrupt the transcriptional machinery the fusion co-opts — BET bromodomain,
  CDK7/9, p300/CBP, mediator — are a mechanism-anchored class already drugged in other
  fusion-driven sarcomas.
- **Groundwork.** This overlaps the repurposing paper's mechanistic tier; the novel
  contribution here is to prioritise these by *fusion-coactivator* logic rather than
  generic anti-proliferation. A fusion-binding-partner literature/interaction map is
  the scriptable next step.
- **Decisive experiment.** Fusion-tethered reporter + coactivator-inhibitor panel in
  EMC lines; ChIP/CUT&RUN for fusion-occupied enhancers.
- **Maturity:** mechanistic hypothesis; some agents clinically available (links to
  repurposing tranches).

---

## 4. Prioritisation: a falsifiable decision tree

The modalities are not equally mature or equally decisive. We rank them by **(a) how
clonal/specific the target is**, **(b) whether the decisive experiment is doable in
existing EMC models now**, and **(c) independence from the undruggable-pocket problem**.

| Rank | Modality | Decisive next experiment | Needs new chemistry? | Doable in current EMC models? |
|---|---|---|---|---|
| 1 | **dTAG fusion-addiction test** (§3.1) | knock-in + acute degradation viability | No (degron is generic) | **Yes** |
| 2 | **CRISPR dependency screen** (§3.4) | genome-wide KO, EMC vs control | No | **Yes** |
| 3 | **Junction neoantigen** (§3.3) | breakpoint-specific immunopeptidomics + T-cell assay | No | Partly (needs patient material) |
| 4 | **Junction ASO** (§3.2) | gapmer knockdown specificity | No (design only) | **Yes** in vitro |
| 5 | **Degrader / coactivator drugs** (§3.1/§3.5) | medicinal chemistry / inhibitor panel | **Yes** (degrader) | Drugs: yes; degrader: no |

The unifying insight: **the first two experiments are the linchpin.** Before any
chemistry, a dTAG knock-in (rank 1) answers the existential question — *is EMC
addicted to acute fusion level?* — and the CRISPR screen (rank 2) supplies druggable
fallbacks if it is not. Both are feasible **today** in the published EMC cell models,
need no new molecule, and would convert this paper's hypotheses into data. That is the
recommended entry point for a collaborating wet lab.

---

## 5. Limitations & where computation ends (read this)

- **No molecule, by design.** We deliberately do not name a specific PROTAC, ASO
  sequence as "the drug", or claim a validated epitope. Proposing a specific validated
  novel compound from computation alone would be fabrication. The deliverable is a
  *de-risked, prioritised program*, not a candidate.
- **The breakpoint is modelled.** §3.3's epitopes are computed for a canonical,
  flagged EWSR1::NR4A3 junction. Real junctions vary by patient/transcript; the
  pipeline is built to re-run on a sequenced breakpoint, and the epitope list must be
  regenerated per patient.
- **Structure predictions are predictions.** AlphaFold pLDDT and fpocket are strong,
  validated tools, but a predicted absent pocket is not the same as an experimentally
  proven one; cryptic/allosteric pockets can exist. The §2 result is a hypothesis-
  grade prior, not proof of undruggability.
- **MHC binding ≠ immunogenicity.** A predicted MHC-I binder may not be processed,
  presented, or T-cell-visible in vivo. Prediction narrows the search; it does not
  confirm a neoantigen.
- **No EMC line in public dependency data.** §3.4 cannot be mined from DepMap today;
  it must be generated.
- **Not clinical evidence.** Nothing here has been tested in a patient. This paper
  stops precisely at the wet-lab door, by intent and by integrity.

---

## 6. Reproducibility

All computation is public-data, scripted, and CI-run:

- `research/modalities/nr4a3_structure.py` — AlphaFold pLDDT + fpocket druggability.
- `research/modalities/fusion_neoantigen.py` — UniProt sequences + MHCflurry junction
  neoantigen prediction.
- `.github/workflows/modalities-run.yml` — runs both in CI (internet + fpocket/
  MHCflurry), publishes results to the `modalities-cache` branch.

Result snapshots (`nr4a3-structure-assessment.json`,
`fusion-neoantigen-predictions.json`) are versioned alongside this manuscript.

---

## 7. Author contributions, competing interests, funding

As for the companion papers: independent, unfunded work by a single non-clinician
author, with AI assistance (Claude) for drafting, code, and structuring; all clinical
and biological claims are cited and require sarcoma-specialist review before any
submission. No competing interests. No funding. **A wet-lab/sarcoma collaborator is
explicitly sought** — this program is designed to be handed to one.

---

## 8. References

*(To be completed to journal style and DOI-verified in CI via `verify-refs.yml`;
entries marked ⚠ need verification.)*

1. Sjögren H, et al. EWSR1/NR4A3 fusion in extraskeletal myxoid chondrosarcoma. ⚠
2. Panagopoulos I, et al. Fusion variants and partners in EMC. ⚠
3. Wang Z, et al. Structure and function of Nurr1 identifies a class of
   ligand-independent nuclear receptors. *Nature* 2003. ⚠
4. Boulay G, et al. Cancer-specific retargeting of BAF by the EWS-FLI1 prion-like
   domain. *Cell* 2017. ⚠
5. Kwon I, et al. Phase transition of low-complexity domains. *Cell* 2013. ⚠
6. Jumper J, et al. Highly accurate protein structure prediction with AlphaFold.
   *Nature* 2021. ⚠
7. Varadi M, et al. AlphaFold Protein Structure Database. *Nucleic Acids Res* 2022. ⚠
8. Le Guilloux V, et al. Fpocket: an open source platform for ligand pocket detection.
   *BMC Bioinformatics* 2009. ⚠
9. O'Donnell TJ, et al. MHCflurry 2.0. *Cell Systems* 2020. ⚠
10. Békés M, Langley DR, Crews CM. PROTAC targeted protein degraders. *Nat Rev Drug
    Discov* 2022. ⚠
11. Nabet B, et al. The dTAG system for targeted protein degradation. *Nat Chem Biol*
    2018. ⚠
12. Bangerter ... USZ-EMC patient-derived EMC model (validated carfilzomib,
    doxorubicin, venetoclax). ⚠ [cross-ref repurposing paper / fact-check-log]
13. Iwata S, et al. NCC-EMC patient-derived EMC cell lines. ⚠
14. Crooke ST, et al. Antisense technology: an overview and prospectus. ⚠
