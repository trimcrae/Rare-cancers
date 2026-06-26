# Blocking the fusion-emergent coactivator interactions of EWSR1::NR4A3: a fusion-selective protein-protein-interaction strategy for extraskeletal myxoid chondrosarcoma

> **CONCEPT / IN-SILICO POSITIONING PAPER — no wet lab, no new compute run, no molecule.**
> This is a hypothesis- and methods-framing paper for one of three *protein-level, fusion-unique*
> routes against EMC. It contains **no validated drug, no asserted efficacy, and no claim that any
> compound works.** The one-line fusion-exclusivity rationale: the coactivator/chromatin-remodeller
> contacts targeted here are made by the **appended EWSR1 transactivation domain**, which wild-type
> NR4A3 does not carry — so disrupting them is functionally **fusion-selective**, unlike an LBD-binding
> NR4A3 degrader (which engages the domain NR4A3 and the fusion *share*). Interactome partners beyond
> the literature-grounded BAF axis (Boulay 2017) are flagged `[to verify]`. The AlphaFold-multimer /
> AF3 interface model named in §3 is **DEFERRED** (needs GPU; not run here). Folder map:
> [`README.md`](./README.md); program board: [`../IDEAS.md`](../IDEAS.md).

---

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is defined in ~90% of cases by an in-frame fusion joining the
N-terminal low-complexity / transactivation domain of *EWSR1* (or, less often, *TAF15*) to most of the
orphan nuclear receptor *NR4A3*, on an otherwise quiet genome. The fusion's oncogenic output is
transcriptional: the appended EWSR1 prion-like transactivation domain (EWS-TAD) retargets chromatin
machinery — most directly the BAF (SWI/SNF) complex, shown for the homologous EWS-FLI1 fusion in Ewing
sarcoma (Boulay et al., *Cell* 2017) — and is presumed to recruit additional coactivators (p300/CBP,
Mediator) and to create dependence on general transcriptional kinases/readers (BET, CDK7/9). **Wild-type
NR4A3 has no EWS-TAD**, so each EWS-TAD-dependent protein-protein interaction (PPI) is a *fusion-emergent*
contact: a target that is, by construction, **fusion-selective**. This is a distinct selectivity logic
from the repo's lead NR4A3 degrader, which binds the NR4A3 ligand-binding domain (LBD) that the fusion and
wild-type NR4A3 **share** — that agent is NR4A3-selective but *not* fusion-selective. Here we frame the
opposite design: directly block the fusion↔coactivator interface with PPI inhibitors or molecular glues.
We are emphatic about one distinction that the repo's own work forces us to make honestly: this
**direct interface-blockade** idea is **not** the **synthetic-lethal BRD9/ncBAF** idea, which the repo
**downgraded** after a DepMap 24Q4 transfer-prior analysis found BRD9 is not a sarcoma dependency (not
even in Ewing) and BET/CDK are pan-essential with no selectivity window. Direct blockade remains hard for
its own reasons — disordered interface, pan-essential partners — and we flag the pan-essential-coactivator
selectivity risk as the dominant liability. We specify the literature-grounded interactome, defer the
AF-multimer/AF3 interface model (needs GPU), and list the decisive experiments others can run. No molecule
is proposed; nothing here is evidence that any agent works in EMC.

---

## 1. Background: the fusion is an aberrant transcriptional activator, and its coactivator contacts are fusion-emergent

EMC's driver is a chimeric transcription factor. The fusion appends the EWSR1 (a FET-family protein)
N-terminal **SYGQ-rich, low-complexity / prion-like transactivation domain (EWS-TAD)** to most of NR4A3
(NOR-1), an orphan NR4A-subfamily nuclear receptor [Refs: Sjögren; Panagopoulos]. EWSR1::NR4A3 accounts
for the majority of cases and TAF15::NR4A3 for a substantial minority, with rarer partners; EMC otherwise
carries few recurrent secondary mutations, so the fusion is, to a first approximation, *the* disease
[Refs: Sjögren; Panagopoulos].

The fusion's oncogenic mechanism is not enzymatic but **transcriptional/recruitment-based**. The EWS-TAD
is intrinsically disordered: on the patient-relevant sequence, the EWSR1 1–264 SYGQ region has a mean
AlphaFold pLDDT of **38.8** with **98.1%** of residues below 50 (`nr4a3-structure-assessment.json`), i.e.
predicted essentially fully disordered, consistent with phase-separation-like condensate behaviour rather
than a folded active site [Refs: Nott 2015; Varadi 2022 for the pLDDT-as-disorder convention]. That
disordered TAD is precisely the module that, in the homologous **EWS-FLI1** fusion of Ewing sarcoma, was
shown to **retarget BAF (SWI/SNF) complexes** to tumour-specific loci through its prion-like domain
(Boulay et al., *Cell* 2017). By close homology of the shared EWS-TAD, EWSR1::NR4A3 is expected to engage
the same class of chromatin machinery; the NR4A3 portion supplies DNA-binding/locus specificity while the
EWS-TAD supplies the aberrant activation surface.

The selectivity argument follows directly and is the reason this route exists:

- **Wild-type NR4A3 lacks the EWS-TAD entirely.** Its own N-terminal AF1 activation region is a different,
  unrelated disordered segment (NR4A3 1–260: mean pLDDT 37.7; `nr4a3-structure-assessment.json`). It does
  not present the SYGQ prion-like surface that recruits BAF.
- Therefore every PPI that **depends on the EWS-TAD** is **fusion-emergent**: it exists only because the
  fusion appended a domain that the normal protein does not have. Disrupting such a contact is
  **functionally fusion-selective** — it cannot, in principle, perturb the wild-type-NR4A3 interactome at
  the EWS-TAD-mediated contacts, because those contacts are absent from wild-type NR4A3.

This is the property the repo's lead **NR4A3 degrader does not have.** That program
([`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md)) recruits the **NR4A3 LBD** — the ordered domain
that the EMC fusion **retains and shares** with wild-type NR4A3 — to an E3 ligase. It is engineered to be
*NR4A3-selective* (sparing NR4A1/NR4A2), and that is valuable, but at the protein level it cannot
distinguish fusion NR4A3 from wild-type NR4A3: both carry the same LBD. The present route attacks a surface
that **only the fusion has**, and is the natural complement: where the degrader removes the protein
(LBD-shared), interface-blockade neutralises the fusion-unique activation contact (EWS-TAD-emergent).

This paper is one of **three protein-level, fusion-unique routes** the program distinguishes from the
LBD-shared degrader. The others (fusion-junction-directed modalities; the fusion-junction neoantigen) are
covered in [`novel-modalities.md`](./novel-modalities.md) §3.2–3.3 and the roadmap; this paper develops the
coactivator-PPI route (`novel-modalities.md` §3.5).

---

## 2. The approach: block the fusion↔coactivator interface — and why this is NOT the downgraded synthetic-lethal route

### 2.1 The idea

If the fusion's oncogenic output is the aberrant recruitment of chromatin machinery via the EWS-TAD, then
**directly blocking the fusion↔coactivator interface** should collapse that output while sparing the
normal cell's use of the same coactivators at non-fusion-recruited loci — *to the extent that the blockade
can be made interface-specific rather than coactivator-global* (the central caveat; §5). Candidate
interfaces, in descending order of literature support:

- **EWS-TAD ↔ BAF (SWI/SNF) complex** — the best-grounded contact, by homology to EWS-FLI1's
  prion-domain-mediated BAF retargeting (Boulay 2017). A PPI inhibitor or molecular glue that disrupts the
  EWS-TAD's engagement of a BAF subunit interface would be the most mechanism-anchored single target.
- **EWS-TAD ↔ p300/CBP** — a histone-acetyltransferase coactivator class generally recruited by potent
  transactivation domains. Engagement by the EMC fusion specifically is **`[to verify]`** (not grounded in
  the verified pool for EWSR1::NR4A3).
- **EWS-TAD ↔ Mediator** — Mediator is the canonical bridge from activation domains to RNA Pol II; a
  contact for the EMC fusion is **`[to verify]`**.
- **General transcriptional dependencies — BET bromodomain readers, CDK7, CDK9** — these are not
  fusion-emergent PPI *partners* of the EWS-TAD per se; they are the broader transcriptional apparatus the
  fusion's hyperactivated programme leans on. Drugging them is *mechanism-anchored* but **not
  fusion-selective** (they are pan-essential transcriptional machinery) — included here only as the
  transcriptional-dependency tier, with the selectivity caveat attached up front.

The modality could be a **PPI inhibitor** (an orthosteric or allosteric small molecule / peptidomimetic
blocking the interface) or a **molecular glue / degrader** that exploits the fusion-unique surface as a
neo-substrate handle [Ref: Békés/Crews 2022 for the event-driven degrader logic]. A glue is attractive in
principle because, like the degrader route, it needs only a transient shallow surface contact rather than a
deep pocket — but here the *handle* would be the fusion-emergent surface, preserving fusion selectivity.

### 2.2 Critical honesty: this is a DIRECT-PPI-blockade idea, distinct from the DOWNGRADED synthetic-lethal BRD9/ncBAF route

The repo previously evaluated, and **downgraded**, a *synthetic-lethal* idea built on the same upstream
biology (EWS-prion → BAF). It is essential not to let this PPI-blockade route inherit that downgrade by
association — and equally essential not to overstate this route by pretending the downgrade is irrelevant.
The two are mechanistically different:

- **The downgraded idea — synthetic-lethal BRD9 / ncBAF.** Hypothesis: because the EWS-prion domain
  retargets BAF, the tumour might *depend* on the non-canonical BAF (ncBAF) module — in particular **BRD9**
  — as a synthetic-lethal vulnerability, drugged with an existing BRD9 degrader/inhibitor. The repo
  assessed this with a **DepMap 24Q4 transfer-prior** analysis and found it **negative**: **BRD9 is not a
  sarcoma dependency, not even in Ewing**, and **BET/CDK are pan-essential with no selectivity window**
  (`emc-treatment-strategy.md`; `degrader-vs-synthetic-lethal.md`; `depmap-sarcoma-dependency.json`). The
  route's board status is **Down-weighted / DOWNGRADED**: "no cheap shortcut; needs a de-novo CRISPR screen
  in patient-derived EMC lines; don't spend a wet-lab slot on a transfer-justified BRD9 test"
  ([`../IDEAS.md`](../IDEAS.md)). We cite that as the repo's own honest finding.

- **This route — direct interface-blockade.** It does **not** posit that EMC is selectively *dependent* on
  a BAF subunit's general cellular function (the synthetic-lethal premise the DepMap transfer prior tested
  and rejected). It posits the narrower, different claim that the **fusion-specific physical contact**
  between the EWS-TAD and chromatin machinery can be **physically disrupted**, neutralising the fusion's
  aberrant recruitment *at fusion loci* without requiring the partner to be a global selective dependency.
  The DepMap transfer prior speaks to **gene-level dependency** (knock the gene out, does the cell die, and
  is that sarcoma-selective?). It does **not** speak to whether a **fusion-emergent interface** is
  blockable. A non-selective dependency (BRD9 essential everywhere → no window) and a fusion-selective
  interface (a contact only the fusion makes) are different objects; a route can fail the first test and
  still be coherent on the second.

We state the honest balance: **the DepMap result removes the "BRD9 is a free synthetic-lethal target"
shortcut and should temper enthusiasm for any BAF-centric EMC bet.** It does *not* falsify direct
EWS-TAD↔BAF interface-blockade, which is a separate, **still-hard** idea (§5–§6). The right reading is:
direct blockade is not downgraded by the DepMap finding, but it inherits no momentum from it either — it
must stand on its own decisive experiments (§4), and its single biggest risk is the pan-essential nature of
the very coactivators it would engage (§5).

---

## 3. Computational groundwork: map the interactome from literature; the interface model is DEFERRED

What is doable **now, in silico, with no new compute run**:

1. **Literature-grounded interactome map (assembled, with provenance flags).**
   - EWS-TAD ↔ **BAF/SWI-SNF**: grounded by homology to EWS-FLI1 (Boulay 2017). The most defensible single
     interface to model first.
   - EWS-TAD ↔ **p300/CBP**, ↔ **Mediator**: **`[to verify]`** for the EMC fusion specifically — included
     as hypotheses, not asserted partners.
   - **BET / CDK7 / CDK9**: transcriptional-dependency tier; mechanism-anchored, **not** fusion-selective,
     flagged as such.
   A scriptable next step (no GPU) is to formalise this as a provenance-tagged interaction table
   (partner, evidence class: *grounded* vs *`[to verify]`*, source), so downstream interface modelling
   targets only defensible contacts. This is the same "map the fusion binding partners" step flagged as the
   next scriptable action in `novel-modalities.md` §3.5.

2. **Domain-disorder context (already computed, reused here).** The EWS-TAD is predicted essentially fully
   disordered (mean pLDDT 38.8; 98.1% < 50; `nr4a3-structure-assessment.json`). This is *load-bearing for
   the modality choice*: a disordered activation domain has **no classical folded interface pocket**, so the
   tractable contact is more likely a short **linear motif / coupled-folding-on-binding** element engaging a
   structured groove on the partner (the BAF subunit / coactivator side), not a rigid lock-and-key
   interface. That shifts the design toward peptidomimetics, motif-mimics, or glues over conventional
   small-molecule interface inhibitors.

3. **DEFERRED — AlphaFold-multimer / AF3 interface model (NOT run here; needs GPU).** The decisive
   *computational* step would be to model the EWS-TAD↔BAF-subunit (and, if grounded, ↔p300/CBP) interface
   with **AF-multimer or AF3**, locate the contact residues, and assess whether a druggable groove exists on
   the structured partner. This requires GPU and **was not performed** in this concept paper. It is queued as
   a clearly-deferred step, consistent with the program's other deferred AF3/ternary modelling
   (`emc-treatment-strategy.md`: "AF3 on a druggable interface — deferred; only once the route picks a
   ternary/PPI interface"). Honest caveat in advance: AF-multimer/AF3 confidence on an interface where one
   partner is a **disordered low-complexity domain** is itself uncertain — disordered-region docking is a
   known weak spot — so even when run, the model is a hypothesis-generator, not proof of a druggable
   interface.

No GPU/AWS job was dispatched for this paper; no molecule was designed or scored.

---

## 4. The decisive experiments others can run (computation cannot replace these)

Because no wet lab is available here, the role of this paper is to specify the falsifying experiments
precisely enough to hand off:

1. **Map the real fusion interactome in EMC cells — proximity labelling / co-IP.** BioID or TurboID fused to
   EWSR1::NR4A3 (or endogenous-tagged), or co-IP / IP-MS of the fusion, in patient-derived EMC lines
   (USZ-EMC; NCC-EMC1/2 [Refs: Bangerter 2023; Iwata]). This is the experiment that **converts the
   `[to verify]` partners into grounded ones** (or refutes them) and tells us which coactivators the fusion
   actually engages — the single most important de-risking step, and the one the in-silico map only
   approximates.
2. **Fusion-tethered reporter + coactivator-inhibitor / PPI-disruptor panel.** A reporter driven by the
   fusion's recruitment activity, read out against a panel of coactivator-pathway perturbations (BAF, p300/
   CBP, BET, CDK7/9), to test which contact, when disrupted, actually collapses fusion-driven transcription
   — and whether any disruption is selective for the fusion programme vs. housekeeping transcription
   (the selectivity-window readout, §5).
3. **ChIP-seq / CUT&RUN for fusion-occupied enhancers, ± perturbation.** Define the fusion's genomic
   occupancy and coactivator co-occupancy, then test which interface-blockade collapses the fusion-specific
   (not the constitutive) chromatin signal. This directly probes whether blockade is fusion-locus-selective.

These mirror the decisive experiments listed in `novel-modalities.md` §3.5 and are the wet-lab hand-off for
a route that, with no lab here, can otherwise only be argued and modelled.

---

## 5. Selectivity & safety: the pan-essential-coactivator window is the dominant risk — stated prominently

**The good news (target-level fusion selectivity).** Every EWS-TAD-*dependent* contact is, by construction,
absent from wild-type NR4A3 (§1). A blockade that acts *strictly* at the EWS-TAD interface is therefore
fusion-selective at the level of *which protein surface it engages*. This is a genuine and attractive
property, and the reason the route is worth stating alongside the LBD-shared degrader.

**The dominant risk (effector-level pan-essentiality).** Fusion selectivity at the *fusion's* surface does
**not** guarantee fusion selectivity at the *partner's* surface — and that is where the danger is. The
coactivators in question are largely **pan-essential**:

- **p300/CBP, BET (BRD2/3/4), CDK7, CDK9** are general transcriptional machinery used genome-wide by normal
  cells. A molecule that blocks the EWS-TAD by **binding the coactivator** (rather than the fusion's unique
  surface) will, to the extent it occupies that coactivator's general-purpose interface, behave like a
  **pan-coactivator inhibitor with pan-transcriptional toxicity** — losing the fusion selectivity the route
  was chosen for. The repo's **own DepMap finding underlines this**: BET/CDK are pan-essential with **no
  selectivity window** (`depmap-sarcoma-dependency.json`) — the same property that sank the synthetic-lethal
  bet is a *safety* warning here.
- **BAF (SWI/SNF)** is likewise broadly essential; BAF subunits are core chromatin remodellers.

The selectivity window therefore depends entirely on **which side of the interface the molecule binds and
how fusion-specific that contact is**:
- Binding the **fusion-unique EWS-TAD surface / motif** (or gluing the fusion to a degradation machine via
  that surface) **preserves** fusion selectivity — this is the design to aim for.
- Binding the **coactivator's general interface** **forfeits** it — this is the failure mode, and it is the
  *easier* molecule to make, which is exactly why the risk is acute.

We flag this prominently: **the route's headline fusion-selectivity is real only for blockers anchored on
the fusion-emergent surface; any blocker anchored on the pan-essential coactivator inherits that
coactivator's toxicity and is not meaningfully fusion-selective.** This must govern target/modality choice
from the outset, and it is the reason the BET/CDK "transcriptional-dependency tier" (§2.1) is included only
with this warning, not as a selective option. No safety claim is made; no agent is asserted to be safe or
effective.

---

## 6. Limitations

- **PPIs are hard to drug.** Disrupting a protein-protein interface with a small molecule is a notoriously
  difficult medicinal-chemistry problem; flat, extended interfaces lack the deep pocket conventional drugs
  exploit. This is a general, well-known constraint, applied here without optimism.
- **The EWS-TAD is disordered — no classical interface pocket.** The fusion side of the contact is a
  predicted IDR (pLDDT 38.8; `nr4a3-structure-assessment.json`), so there may be no fixed pocket to target on
  the fusion; the tractable element is more likely a transient linear motif engaging a partner groove, which
  is a harder design problem and weakens the AF-multimer/AF3 modelling confidence (§3).
- **Pan-essential-coactivator toxicity** (§5) is the dominant liability and is restated here as a limitation,
  not just a design note: many candidate partners cannot be globally inhibited without systemic
  transcriptional toxicity.
- **The interactome is partly literature-inferred.** The BAF axis is grounded by homology to EWS-FLI1
  (Boulay 2017), but partners beyond it (p300/CBP, Mediator) are **`[to verify]`** for the EMC fusion
  specifically — the proximity-labelling experiment (§4) is required to ground them, and until then the map
  is a hypothesis.
- **No EMC interactome dataset and no AF-multimer model exist here.** The interface model is deferred (GPU);
  no proximity-labelling data has been generated. This route is at concept maturity: rationale + a deferred
  computational step + a specified hand-off experiment.
- **Not clinical evidence.** Nothing here has been tested in a cell or a patient. No molecule is proposed,
  and no claim is made that any agent works.

---

## 7. Broader indications: the EWS-LC ↔ BAF axis generalises across FET-fusion sarcomas

The fusion-emergent contact this route targets is supplied by the **EWS / FET low-complexity transactivation
domain**, which is **shared across the FET-fusion family** — EWS-FLI1 / EWS-ERG (Ewing sarcoma),
EWSR1::NR4A3 (EMC), and other EWSR1/FUS/TAF15 fusions. The BAF-retargeting mechanism was in fact first
demonstrated for **EWS-FLI1 in Ewing sarcoma** (Boulay 2017), not for EMC. A blocker of the **EWS-TAD↔BAF**
interface would, in principle, act on the *shared* fusion-emergent surface and therefore **generalise across
FET-fusion sarcomas** — with EMC as a clean single-driver entry point and Ewing as the better-characterised,
larger validation indication. This mirrors the degrader paper's "entry point, not endpoint" framing, but on a
**different axis**: the degrader generalises across NR4A3-driven cancers (EMC, AciCC) by the *NR4A3* portion;
this route generalises across FET-fusion sarcomas by the *EWS-TAD* portion. The two are orthogonal and
complementary. (Cross-indication efficacy is **motivation, not demonstrated** — no efficacy claim is made.)

---

## References

**Verified pool (cite directly):**

- Boulay G, et al. *Cancer-specific retargeting of BAF complexes by a prion-like domain.* **Cell** 2017.
  doi:10.1016/j.cell.2017.07.036. *(EWS prion-like domain retargets BAF/SWI-SNF — the grounding for the
  EWS-TAD↔BAF interface; demonstrated for EWS-FLI1, applied here by homology.)*
- Nott TJ, et al. *Phase transition of a disordered nuage protein generates environmentally responsive
  membraneless organelles.* **Mol Cell** 2015. doi:10.1016/j.molcel.2015.01.013. *(disorder / phase-
  separation context for the EWS-TAD.)*
- Varadi M, et al. *AlphaFold Protein Structure Database.* **Nucleic Acids Res** 2022.
  doi:10.1093/nar/gkab1061. *(pLDDT-as-disorder convention used for the EWS-TAD numbers.)*
- Wang Z, et al. *Structure and function of Nurr1 identifies a class of ligand-independent nuclear
  receptors.* **Nature** 2003. doi:10.1038/nature01645. *(NR4A LBD / orphan-receptor context.)*
- Békés M, Langley DR, Crews CM. *PROTAC targeted protein degraders: the past is prologue.* **Nat Rev Drug
  Discov** 2022. doi:10.1038/s41573-021-00371-6. *(event-driven degrader / molecular-glue logic, cited for
  the glue option.)*
- Mullican SE, et al. *Abrogation of nuclear receptors Nr4a3 and Nr4a1 leads to development of acute myeloid
  leukemia.* **Nat Med** 2007. doi:10.1038/nm1579. *(NR4A tumour-suppressor / safety context.)*
- Safe S, Karki K. *The Paradoxical Roles of Orphan Nuclear Receptor 4A (NR4A) in Cancer.* **Mol Cancer
  Res** 2021. doi:10.1158/1541-7786.mcr-20-0707. *(NR4A context.)*
- Sjögren H, et al. *EWSR1/NR4A3 fusion in extraskeletal myxoid chondrosarcoma.* *(EMC driver; shared with
  companion papers — see their fact-check log.)*
- Panagopoulos I, et al. *Fusion variants/partners in EMC (incl. TAF15, TCF12, TFG, FUS).* *(EMC fusion
  spectrum; shared with companion papers.)*
- Bangerter, et al. 2023. *USZ-EMC patient-derived EMC model.* *(EMC cell model for the decisive
  experiments.)*
- Iwata S, et al. *NCC-EMC patient-derived EMC cell lines.* *(EMC cell models.)*

**Repo's own findings (cited as such):**

- DepMap 24Q4 transfer-prior analysis downgrading the synthetic-lethal BRD9/ncBAF route (BRD9 not a sarcoma
  dependency, not even in Ewing; BET/CDK pan-essential, no selectivity window):
  [`emc-treatment-strategy.md`](./emc-treatment-strategy.md), [`../IDEAS.md`](../IDEAS.md),
  `degrader-vs-synthetic-lethal.md`, `depmap-sarcoma-dependency.json`.
- Domain-disorder numbers (EWS-TAD pLDDT 38.8 / 98.1% < 50; NR4A3 LBD ordered):
  [`../modalities/nr4a3-structure-assessment.json`](../modalities/nr4a3-structure-assessment.json).
- LBD-shared selectivity gap of the NR4A3 degrader (contrast partner for this paper):
  [`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md).

**Flagged as unverified / to ground (`[to verify]`):** any specific EMC-fusion interactome partner beyond
the BAF axis — notably **EWSR1::NR4A3 ↔ p300/CBP** and **↔ Mediator** engagement — must be grounded by the
proximity-labelling experiment (§4) before assertion. BET/CDK7/CDK9 are cited as pan-essential
transcriptional machinery, not as demonstrated fusion-selective partners. No DOIs/PMIDs/authors/years beyond
the verified pool above are invented; where a citation could not be grounded it is left flagged rather than
fabricated.

---

*Author contributions, competing interests, funding: independent, unfunded work by a single non-clinician
author, with AI assistance (Claude) for drafting and structuring; all clinical and biological claims are
cited or flagged and require sarcoma-specialist review before any submission. No competing interests. No
funding. A wet-lab/sarcoma collaborator is explicitly sought — the §4 experiments are the hand-off.*
