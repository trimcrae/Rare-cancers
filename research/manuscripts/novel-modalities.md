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
ligand-binding domain (LBD). We find both transactivation domains are predicted
intrinsically disordered (EWSR1 1–264: mean pLDDT 38.8, 98% of residues < 50), while
the NR4A3 LBD is confidently folded (mean pLDDT 85.0) — yet across all 33 fpocket
cavities on the model the most druggable pocket scores only 0.495 (below the 0.5
"druggable" threshold) and localises within the LBD, recapitulating the pocket-less
Nurr1/Nur77 precedent. The fusion is therefore either disordered or folded-but-pocketless:
a strong argument for modalities that do **not** occupy a pocket. We specify five such
modalities — targeted protein degradation, fusion-junction antisense, fusion-directed
immunotherapy, synthetic-lethal dependency mapping, and transcriptional/coactivator
disruption — and take each as far as present-day computation allows. As worked examples
we (i) design fusion-specific gapmer antisense oligonucleotides against the junction
transcript, and (ii) predict, with MHCflurry-2.0, that the junction peptide GQQPCVQAQY
is a strong HLA-B\*15:01-presented neoantigen (44.6 nM; presentation percentile 0.07) —
a concrete but HLA-restricted lead for a fusion-directed vaccine or TCR-T. We close with
a prioritised, falsifiable experimental program and an explicit statement of where
computation ends. All analyses are reproducible (`research/modalities/`), run in CI, and
use only public data.

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

**Method.** `research/modalities/nr4a3_structure.py` downloads the AlphaFold2 (AFDB)
models for NR4A3 (UniProt Q92570) and EWSR1 (Q01844), reads per-residue pLDDT
(AlphaFold's confidence, a validated proxy for order/disorder: pLDDT < 50 marks
predicted intrinsic disorder [Ref: Varadi 2022/AlphaFold-DB]), and runs fpocket
[Ref: Le Guilloux 2009] to detect and score cavities on the NR4A3 model. We summarise
pLDDT over annotated domain windows and report every fpocket cavity with its
druggability score (0–1; >0.5 conventionally "druggable"). Numbers below are the live
CI output (`nr4a3-structure-assessment.json`, `modalities-cache` branch).

### 2.1 Both transactivation domains are predicted intrinsically disordered

The EWSR1-derived **SYGQ-rich N-terminal region** that forms the fusion's
transactivation module (res 1–264) has **mean pLDDT 38.8**, with **98.1%** of residues
below 50 — i.e. AlphaFold predicts it as essentially fully disordered. NR4A3's own
N-terminal AF1 region (res 1–260) is likewise disordered (mean pLDDT **37.7**, **96.5%**
below 50). EWSR1's folded modules behave as expected by contrast (RRM res 361–442: mean
pLDDT **85.1**, 0% disordered), confirming the method resolves order from disorder on
these exact sequences rather than calling everything low-confidence.

This quantifies, on the patient-relevant sequence, the long-held qualitative claim
that the EWSR1 portion is an IDR. A disordered domain has no pocket to occupy — it
is essentially un-druggable by direct small-molecule inhibition, which is the single
most important constraint on EMC drug design and the reason §3 leads with degradation
and transcript/immune modalities rather than inhibitors.

### 2.2 The NR4A3 ligand-binding domain is well-folded — yet has no druggable pocket

Unlike the transactivation domains, the NR4A3 **ligand-binding domain (res 373–626) is
confidently folded** (mean pLDDT **85.0**; only 9.1% of residues below 50), as is the
DNA-binding domain (zinc fingers, res 261–337; mean pLDDT **76.1**). So the LBD is not
disordered — AlphaFold returns a definite structure. The question is whether that
structure presents a cavity a small molecule could occupy. It does not: across **all 33
fpocket cavities on the entire NR4A3 model, the single most druggable pocket scores only
0.495** — i.e. below the conventional 0.5 "druggable" threshold, and every other cavity
scores ≤ 0.20. That best cavity does sit **within the LBD** (lining residues span 406–534,
all assigned to the ligand-binding domain) — so this is not a case of "the tool looked in
the wrong place": the most tractable pocket the LBD offers is still only borderline.

This is precisely the **Nurr1/Nur77 precedent** [Ref: Wang 2003], now quantified for
NR4A3: a structured orphan-receptor LBD whose canonical ligand pocket is effectively
absent/occluded. The headline of the structural assessment is therefore stark — the
fusion is *either* disordered (transactivation domains, no pocket) *or* folded-but-
pocketless (LBD) — and it is the strongest possible argument for the non-occupancy
modalities of §3.

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
- **Computational groundwork (done here).** `research/modalities/junction_aso.py`
  fetches the RefSeq CDS of *EWSR1* (NM_005243) and *NR4A3* (NM_006981), builds the
  modelled fusion transcript, and tiles 16-mer gapmers (5-6-5 LNA/DNA/LNA) whose
  central DNA gap spans the junction, keeping only oligos that draw bases from **both**
  sides of the seam and are absent as a perfect complement from either parent CDS. It
  returns **5 fusion-specific candidate gapmers**. A real, honest design caveat surfaces
  immediately: the junction here is **GC-rich** (top candidates ~75–81% GC), which is
  outside the usual 40–60% comfort zone and would need chemistry tuning — exactly the
  kind of constraint a design tool should expose up front rather than hide.
- **Decisive experiment.** Junction-ASO knockdown vs. scrambled control in EMC lines;
  rescue specificity by sparing parental transcripts.
- **Maturity:** design computable and done; sequence is breakpoint-conditional, GC is
  high, and delivery to tumour remains the hard, unsolved part.

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

  Of **34** novel junction-spanning peptides, **5** are predicted MHC-I binders
  (presentation %ile ≤ 2) and **2** are strong (≤ 0.5); **3** also pass the raw-affinity
  cutoff (≤ 500 nM). The result is dominated by one peptide on one allele:

  | peptide | HLA | affinity (nM) | presentation %ile | pres. score | call |
  |---|---|---|---|---|---|
  | **GQQPCVQAQY** | **B\*15:01** | **44.6** | **0.07** | 0.94 | strong |
  | QQPCVQAQY | B\*15:01 | 58.1 | 0.24 | 0.83 | strong |
  | GQQPCVQAQY | A\*01:01 | 705 | 0.83 | 0.49 | weak |
  | GQQPCVQAQY | B\*44:02 | 847 | 0.93 | 0.45 | weak |
  | QPCVQAQY | B\*35:01 | 234 | 1.16 | 0.36 | weak |

  The lead epitope **GQQPCVQAQY** (EWSR1 `GQQ` ⊕ NR4A3 `PCVQAQY`) is predicted to be
  **strongly presented on HLA-B\*15:01** and weakly on HLA-A\*01:01/B\*44:02. So the
  honest read is **conditionally positive and HLA-restricted**: fusion-directed
  immunotherapy is a credible lead *for B\*15:01-positive patients* with this junction,
  not a pan-population one. (Methodological note: an early version of this analysis read
  the wrong MHCflurry output column and spuriously reported zero binders; the pipeline
  now records `_rank_column_used` and cross-checks raw affinity so the result is
  verifiable — see `fusion-neoantigen-predictions.json`.)

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
  neoantigen prediction (records `_rank_column_used` for verifiability).
- `research/modalities/junction_aso.py` — RefSeq CDS + fusion-junction gapmer ASO design.
- `.github/workflows/modalities-run.yml` — runs all three in CI (internet + fpocket/
  MHCflurry), publishes results to the `modalities-cache` branch (analyses are
  `continue-on-error` and publishing is `if: always()`, so partial/failed runs stay
  observable rather than silently dropping output).

Result snapshots (`nr4a3-structure-assessment.json`,
`fusion-neoantigen-predictions.json`, `junction-aso-designs.json`) are produced on the
`modalities-cache` branch and can be snapshotted alongside this manuscript.

---

## 7. Author contributions, competing interests, funding

As for the companion papers: independent, unfunded work by a single non-clinician
author, with AI assistance (Claude) for drafting, code, and structuring; all clinical
and biological claims are cited and require sarcoma-specialist review before any
submission. No competing interests. No funding. **A wet-lab/sarcoma collaborator is
explicitly sought** — this program is designed to be handed to one.

---

## 8. References

All 10 methods/tools DOIs below are ✓ CI-confirmed via Crossref (`verify-refs.yml`,
sections 4–5; Boulay and Jumper were disambiguated from near-title decoys by adding
author + journal + year constraints). EMC-biology refs (1–2, 12–13) are shared with the
companion papers and cross-referenced to their fact-check log; ⚠ marks those still to be
finalised there.

**Methods / tools (CI-verified DOIs):**

3. Wang Z, et al. Structure and function of Nurr1 identifies a class of
   ligand-independent nuclear receptors. *Nature* 2003. ✓ doi:10.1038/nature01645
4. Nott TJ, et al. Phase transition of a disordered nuage protein generates
   environmentally responsive membraneless organelles. *Mol Cell* 2015.
   ✓ doi:10.1016/j.molcel.2015.01.013  *(general phase-separation reference; replaces a
   mis-titled earlier entry caught in fact-checking)*
7. Varadi M, et al. AlphaFold Protein Structure Database: massively expanding the
   structural coverage of protein-sequence space. *Nucleic Acids Res* 2022.
   ✓ doi:10.1093/nar/gkab1061
8. Le Guilloux V, Schmidtke P, Tufféry P. Fpocket: an open source platform for ligand
   pocket detection. *BMC Bioinformatics* 2009. ✓ doi:10.1186/1471-2105-10-168
9. O'Donnell TJ, Rubinsteyn A, Laserson U. MHCflurry 2.0: improved pan-allele
   prediction of MHC class I-presented peptides. *Cell Systems* 2020.
   ✓ doi:10.1016/j.cels.2020.09.001
10. Békés M, Langley DR, Crews CM. PROTAC targeted protein degraders: the past is
    prologue. *Nat Rev Drug Discov* 2022. ✓ doi:10.1038/s41573-021-00371-6
11. Nabet B, et al. The dTAG system for immediate and target-specific protein
    degradation. *Nat Chem Biol* 2018. ✓ doi:10.1038/s41589-018-0021-8
14. Crooke ST, et al. Antisense technology: an overview and prospectus. *Nat Rev Drug
    Discov* 2021. ✓ doi:10.1038/s41573-021-00162-z
5. Boulay G, et al. Cancer-specific retargeting of BAF complexes by a prion-like
   domain. *Cell* 2017. ✓ doi:10.1016/j.cell.2017.07.036  *(CI confirmed the Cell
   article over a near-title AACR abstract by constraining author + journal + year.)*
6. Jumper J, et al. Highly accurate protein structure prediction with AlphaFold.
   *Nature* 2021. ✓ doi:10.1038/s41586-021-03819-2

**EMC biology (shared with companion papers; see their fact-check log):**

1. Sjögren H, et al. EWSR1/NR4A3 fusion in extraskeletal myxoid chondrosarcoma. ⚠
2. Panagopoulos I, et al. Fusion variants/partners in EMC (incl. TAF15, TCF12, TFG,
   FUS; and the PGR-NR4A3 variant, PMID 36103645). ⚠
12. Bangerter, et al. USZ-EMC patient-derived EMC model (full text confirms carfilzomib,
    doxorubicin, venetoclax validated in both cell models — see fact-check-log). ⚠
13. Iwata S, et al. NCC-EMC patient-derived EMC cell lines. ⚠
