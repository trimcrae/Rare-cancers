# Disrupting the fusion's condensate: an EWS-low-complexity-domain phase-separation strategy as a fusion-selective route in EWSR1::NR4A3 extraskeletal myxoid chondrosarcoma

> **IN-SILICO / CONCEPT PAPER — earliest-stage of the three protein-level fusion-unique routes.**
> No wet lab. **No new GPU/AWS compute run was performed for this manuscript.** The first-party data
> here are previously-committed AlphaFold disorder numbers
> (`../modalities/nr4a3-structure-assessment.json`) plus a new **CPU-only sequence-feature analysis**
> run on a GitHub runner (`../modalities/fusion-idr-features.json`, §3.2); everything else is cited
> literature. The sequence-feature descriptors are phase-separation **proxies**, not a condensate
> measurement. The rationale is **fusion-exclusive**: the aberrant
> condensate/phase-separation behaviour is an *emergent* property of the EWS::NR4A3 chimera that
> **wild-type NR4A3 does not have**, so a condensate-directed agent is functionally fusion-selective
> in a way the repo's NR4A3 PROTAC (which binds the **shared** NR4A3 LBD) is not. **Read this caveat
> first: drugging biomolecular condensates is an EMERGING, largely unproven field.** Predicted
> phase-separation propensity is not a druggable condensate; "dissolving" a condensate in a dish is
> not a therapy. Nothing here is a drug candidate, and nothing here is clinical evidence. Companion
> papers: the LBD-shared degrader [`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md), the
> EMC-program roadmap [`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md), and the modality
> survey [`novel-modalities.md`](./novel-modalities.md) (§1, §2.1, §3.5). Strategy board:
> [`../IDEAS.md`](../IDEAS.md).

---

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is defined in ~90% of cases by an in-frame fusion of the
*EWSR1* (or, less often, *TAF15*) low-complexity (LC) / prion-like domain to the orphan nuclear
receptor *NR4A3*, on an otherwise quiet genome. The fusion is the disease's single near-clonal
driver, but it joins two hard-to-drug protein classes — an intrinsically disordered transactivation
domain and an orphan-receptor ligand-binding domain (LBD). The repo's lead protein-level agent, a
selective NR4A3 degrader, binds the NR4A3 LBD — a domain **shared** between the fusion and wild-type
NR4A3 — and is therefore NR4A3-selective, **not fusion-selective**. Here we develop a route that is
fusion-selective by construction: target the **aberrant biomolecular condensate / phase-separation
behaviour** the fusion drives through the EWS prion-like LC domain. For FET-family fusion oncoproteins
the LC domain self-associates and undergoes liquid-liquid phase separation (LLPS), nucleating
condensates that retarget chromatin-remodelling machinery (BAF) and drive aberrant transcription
(Boulay et al., *Cell* 2017; with the general disordered-protein phase-transition precedent of Nott
et al., *Mol Cell* 2015). Wild-type NR4A3 — a folded LBD plus a short disordered AF1 — **lacks the
EWS LC domain entirely**, so this condensate behaviour is **fusion-emergent**: an agent that partitions
into, modulates, or prevents the fusion's condensates is, in mechanism, fusion-selective and spares
wild-type NR4A3 and its tumour-suppressor functions. We ground the disorder premise on real committed
data (EWSR1 1–264: mean pLDDT 38.8, 98.1% of residues < 50; NR4A3 has no comparable LC domain) and
now add **first-party sequence-feature support**: a CPU-only, pure-stdlib descriptor analysis (run on a
GitHub runner with a UniProt fetch; `../modalities/fusion-idr-features.json`) shows the EWS/TAF15 LC
domains carry the LLPS/prion compositional signature (high SYGQ and aromatic content, low charge, low
Shannon entropy) while folded controls do not — and, **crucially, the non-prion NR4A3_AF1 control
(NR4A3's own disordered N-terminus) lacks the signature**, providing real first-party evidence that the
condensate-driving composition is EWS/TAF15-emergent and not a generic property of NR4A3's own disorder.
These remain sequence-derived **proxies** for phase-separation propensity, not a condensate measurement. We outline three condensate-directed
modality classes, the decisive condensate assays others would run, and an honest selectivity/safety
analysis whose real risk is **not** wild-type NR4A3 but cross-reactivity with the cell's many normal
condensates. This is the **earliest-stage and least-proven** of the three protein-level fusion-unique
routes; we say so throughout.

---

## 1. Background: the fusion drives transcription through condensate behaviour wild-type NR4A3 does not have

EMC's defining lesion fuses the N-terminal low-complexity / transactivation domain of EWSR1 (a
FET-family RNA-binding protein) to most of NR4A3 (NOR-1), an orphan member of the NR4A nuclear-receptor
subfamily [Sjögren et al.; Panagopoulos et al.]. EWSR1::NR4A3 accounts for the majority of cases and
TAF15::NR4A3 for a substantial minority, with rarer partners; the disease otherwise carries few
recurrent secondary mutations, making the fusion, to a first approximation, *the* disease (see
[`novel-modalities.md`](./novel-modalities.md) §1 and the roadmap for the cited breakdown).

**The fusion is an aberrant transcriptional activator, and its activation mechanism runs through
phase-separation/condensate behaviour.** FET-fusion oncoproteins do not work by occupying a folded
active site; they work because their prion-like LC domain **self-associates and phase-separates**,
forming biomolecular condensates that concentrate and **retarget chromatin-remodelling and
transcriptional machinery** to ectopic genomic sites. The paradigm result is Boulay et al.
(*Cell* 2017): the EWS prion-like domain of an FET fusion **retargets BAF (SWI/SNF) complexes** to
tumour-specific enhancers, converting a normally-restrained transcription factor into a potent,
mistargeted activator (doi:10.1016/j.cell.2017.07.036). The general biophysics — that a single
intrinsically disordered protein can undergo a phase transition into a dynamic, membraneless,
environmentally-responsive compartment — is established by Nott et al. (*Mol Cell* 2015;
doi:10.1016/j.molcel.2015.01.013). Earlier work on the FUS/EWS-family LC domains as self-associating,
hydrogel/amyloid-forming modules underpins this picture [Kwon et al. 2013, locator to verify]. We do
**not** here assert an EMC-specific, EWSR1::NR4A3-resolved condensate measurement — that is exactly
the assay §4 hands to others; the cited evidence is for the EWS LC domain / FET-fusion class.

**The EWS LC domain is intrinsically disordered — quantified on the patient-relevant sequence.** The
repo's committed AlphaFold assessment (`../modalities/nr4a3-structure-assessment.json`) gives the
EWSR1 SYGQ-rich N-terminal transactivation / prion-like region (residues 1–264) a **mean pLDDT of
38.8**, with **98.1% of residues below 50** — i.e. AlphaFold predicts it as essentially fully
disordered (pLDDT < 50 is a validated proxy for predicted intrinsic disorder; Varadi et al.,
*NAR* 2022, doi:10.1093/nar/gkab1061). Disorder of this kind is the structural substrate of LC-domain
phase separation: no folded pocket, a multivalent SYGQ-rich sequence, weak distributed interactions —
the very features that drive LLPS rather than lock-and-key binding.

**Wild-type NR4A3 lacks this domain — so condensate behaviour is fusion-emergent.** NR4A3 (UniProt
Q92570, 626 aa) is, by the same committed data, a folded LBD (residues 373–626, mean pLDDT **85.0**)
and DNA-binding zinc fingers (261–337, mean pLDDT **76.1**) preceded by a **short** disordered AF1
region (1–260, mean pLDDT 37.7). Critically, **wild-type NR4A3 has no EWS-type SYGQ-rich prion-like LC
domain at all** — that module is contributed entirely by the EWSR1 (or TAF15) fusion partner. The
fusion therefore acquires a phase-separation/condensate-nucleating capacity that the wild-type
monomer does not possess. This is the crux of fusion-selectivity for this route: **the condensate
behaviour is a property of the chimera, not of either parent.** (We are careful not to overstate the
wild-type side: a short disordered AF1 is not "no disorder," and NR4A3 biology can involve coactivator
interactions; the claim is specifically that wild-type NR4A3 lacks the *EWS prion-like LC domain* that
drives FET-fusion LLPS, and does not phase-separate in the same domain-encoded way.)

The practical contrast with the repo's existing protein-level agent is the entire motivation for this
paper. The lead NR4A3 degrader (see [`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md)) engages the
**NR4A3 LBD, which is shared by the fusion and by wild-type NR4A3** — an excellent *NR4A3*-selective,
NR4A1/2-sparing design, but **not fusion-selective**: it cannot, by binding site alone, distinguish the
oncoprotein from the wild-type protein. A condensate-directed agent flips that axis: it targets the one
functional property only the fusion has.

---

## 2. The approach: three condensate-directed modality classes

We group the candidate mechanisms by what they act on. None is a molecule; each is a target hypothesis
with an honest maturity tag, and all sit downstream of the emerging-field caveat in the banner.

### 2.1 (a) Small molecules that partition into / dissolve the fusion's condensates
- **Rationale.** Some small molecules preferentially **partition into** specific biomolecular
  condensates and change their material properties (composition, viscosity, or whether they form at
  all). The therapeutic hypothesis is a molecule that enriches in the EWS::NR4A3 condensate and
  **dissolves or detunes** it, collapsing the aberrant transcriptional output without binding any
  folded pocket — exactly the modality an LC-domain-driven target invites.
- **Honesty.** This is the most speculative class. Predictable, selective condensate-partitioning
  pharmacology is an **emerging** capability, not an established one; "drugging the condensate" is a
  research frontier and there is no validated EMC-condensate-dissolving small molecule. We name the
  mechanism, not a compound — naming a compound would be fabrication.

### 2.2 (b) Block EWS-LC self-association or its BAF/coactivator recruitment
- **Rationale.** Rather than dissolve a formed condensate, prevent its formation or its function:
  (i) interfere with **EWS-LC self-association** (the multivalent, distributed interactions that
  nucleate LLPS), or (ii) block the **downstream recruitment** the condensate enables — most
  concretely the EWS-prion-domain → **BAF/SWI-SNF retargeting** that Boulay et al. (2017) showed is
  the cancer-specific event. Blocking the recruitment interface is mechanistically tied to the
  fusion's oncogenic action and is, in principle, a more conventional protein-interaction target than
  the bulk material properties of a droplet.
- **Honesty.** Disordered self-association surfaces are notoriously hard to target with selective
  binders (no pocket; transient, distributed contacts). The BAF-recruitment interface is better
  defined biologically but its molecular surface in the EMC fusion is not characterised here. This is
  a hypothesis class, not a designed inhibitor.

### 2.3 (c) Tool-compound proof-of-concept — a TOOL, not a drug
- **Rationale.** Aliphatic alcohols, classically **1,6-hexanediol**, dissolve many LLPS-driven
  condensates by disrupting the weak hydrophobic interactions that hold them together. Such reagents
  are the standard **first-line probe** to ask whether a given nuclear body is condensate-like and
  whether the fusion's transcriptional activity depends on that state.
- **Honesty — flagged loudly.** 1,6-hexanediol and related aliphatic alcohols are **research tools,
  not therapeutics**: they are non-selective, cytotoxic, perturb condensates globally, and have known
  confounding effects on chromatin and the kinome. We invoke them **only** as a mechanistic
  proof-of-concept probe in §4 (does dissolving the condensate abolish fusion-driven transcription?),
  **never** as a candidate drug. Any "1,6-hexanediol works" readout would be a statement about
  *mechanism*, not about a treatment.

---

## 3. Computational groundwork — what is real now (committed pLDDT + first-party sequence features)

We separate, strictly, the first-party data that exist from the wet-lab measurements that computation
cannot replace (§4).

### 3.1 What is real now (committed, first-party)
The only first-party numbers in this paper are the previously-committed AlphaFold disorder values
(`../modalities/nr4a3-structure-assessment.json`; method and calibration described in
[`novel-modalities.md`](./novel-modalities.md) §2):
- **EWSR1 LC domain (res 1–264): mean pLDDT 38.8, 98.1% of residues below 50** — predicted essentially
  fully disordered, the structural premise for LC-domain phase separation.
- For contrast on the same model, EWSR1's folded RRM (res 361–442) is ordered (mean pLDDT 85.1, 0%
  disordered), confirming the method resolves order from disorder rather than calling everything
  low-confidence.
- **NR4A3** is a folded LBD (373–626, mean pLDDT 85.0) and zinc-finger DBD (261–337, mean pLDDT 76.1)
  with only a short disordered AF1 (1–260) — and **no EWS-type prion-like LC domain**, the fusion-vs-
  wild-type asymmetry this route exploits.

These establish the *premise* (the fusion contributes a disordered, LLPS-competent module that
wild-type NR4A3 lacks). They do **not**, by themselves, demonstrate condensate formation — disorder is
necessary, not sufficient, for LLPS, and AlphaFold pLDDT is a disorder proxy, not a phase-separation
measurement.

### 3.2 First-party sequence-feature descriptors (now RUN — CPU-only, real)
The natural first-party computational step that *strengthens* the premise — a **sequence-based
low-complexity / LLPS-propensity analysis of the EWS LC domain** — has now been **run**. In an earlier
draft it was deferred because the residue-level FASTA was not available offline; that blocker is gone.
The committed JSON stores summarised pLDDT statistics over windows, not the sequence, so the analysis
was executed on a **GitHub runner**: a one-shot job (`fusion_idr_features.py`) **fetched the EWSR1 /
TAF15 / NR4A3 sequences from UniProt** and computed, with **pure Python stdlib** (no GPU, no external
deps), a set of established composition/charge-patterning/complexity descriptors for each domain window.
The result is committed first-party data at **`../modalities/fusion-idr-features.json`**.

The descriptors are: **frac_SYGQ** (fraction of Ser/Tyr/Gly/Gln, the hallmark FET LC-domain bias),
**frac_aromatic(FYW)** (aromatic content, a known LLPS-driving "sticker" feature), **FCR** (fraction of
charged residues; low charge favours LC-domain LLPS over charge-driven complex coacervation),
**disorder-promoting** (fraction of disorder-promoting residues), **Shannon entropy** (sequence
compositional complexity in bits; *lower* = lower-complexity), and **SCD** (sequence charge
decoration, a charge-patterning statistic). Per window:

| window | frac_SYGQ | frac_aromatic (FYW) | FCR | disorder-promoting | Shannon entropy (bits) | SCD |
| --- | --- | --- | --- | --- | --- | --- |
| **EWSR1_LC** (prion-like TAD, 1–264) | **0.561** | **0.140** | **0.030** | 0.648 | **3.154** | 0.218 |
| **TAF15_LC** (alt partner, 1–205) | **0.683** | **0.132** | 0.166 | 0.668 | **3.239** | 1.940 |
| NR4A3_AF1 (disordered, **NON-prion**, 1–260) | 0.258 | 0.077 | 0.108 | 0.589 | 3.875 | 0.028 |
| EWSR1_RRM (folded control, 361–442) | 0.220 | 0.098 | 0.281 | 0.476 | 4.040 | −0.546 |
| NR4A3_LBD (folded control, 373–626) | 0.197 | 0.067 | 0.236 | 0.484 | 4.035 | −0.340 |
| NR4A3_DBD (folded control, 261–337) | 0.286 | 0.052 | 0.169 | 0.571 | 3.871 | −0.420 |

**What the numbers say.** The two FET LC domains carry the LLPS/prion compositional signature and the
folded controls are its mirror image:
- **EWS_LC and TAF15_LC** have **very high SYGQ** (0.561 / 0.683) and **high aromatic** content
  (0.140 / 0.132), **low charge** (FCR 0.030 / 0.166), and **low Shannon entropy** (3.154 / 3.239 bits)
  — the classic low-complexity, sticker-rich, charge-poor profile that drives LC-domain phase
  separation.
- The **folded controls** (EWSR1_RRM, NR4A3_LBD, NR4A3_DBD) are the opposite: **high entropy** (~4.0
  bits), **low SYGQ** (~0.20–0.29), and **higher charge** (FCR 0.169–0.281) — confirming the descriptors
  separate low-complexity LC domains from ordinary folded sequence rather than calling everything
  "disordered-looking."
- **The decisive control is NR4A3_AF1** — NR4A3's own N-terminal region, which **is** disordered (high
  disorder-promoting fraction, 0.589) but is **not** a prion-like LC domain. It **lacks the signature**:
  SYGQ 0.258, aromatic 0.077, Shannon entropy 3.875 — far from the EWS/TAF15 LC values and close to the
  folded controls on every composition axis. This is the key result: **the LLPS-driving compositional
  signature is specific to the EWS/TAF15 LC domain and is not a generic consequence of NR4A3 having a
  disordered region of its own.** It is real first-party quantitative support that the condensate
  capacity is **EWS/TAF15-emergent** and absent from wild-type NR4A3.

**Honest scope of this result.** These are **sequence-derived proxies** for phase-separation propensity
(composition, charge patterning, low-complexity entropy), **not** a phase diagram and **not** a
condensate measurement. They strengthen the premise — and sharpen the fusion-vs-wild-type
asymmetry with NR4A3's own disorder as an internal negative control — but they **do not demonstrate
condensate formation**. Demonstrating that the fusion phase-separates and that its transcription
*depends* on the condensed state is still the wet-lab step in §4. No GPU/AWS run was involved; the job
is CPU- and sequence-only, with real tools and real numbers reported as committed.

---

## 4. The decisive experiment others would run (computation cannot replace this)

Condensate behaviour must be **measured**, not predicted. The make-or-break experiments — for a
sarcoma/biophysics lab, not for this in-silico work — are:

1. **Demonstrate the condensate in EMC cells.** Express tagged EWSR1::NR4A3 in patient-derived EMC
   lines (e.g. USZ-EMC, NCC-EMC1/2 [Bangerter et al. 2023; Iwata et al.]) and image nuclear puncta;
   test their **liquid-like dynamics by FRAP** (recovery kinetics) and their **dependence on the LC
   domain** with LC-domain deletion/mutation controls. Wild-type NR4A3, lacking the LC domain, is the
   built-in negative control — the prediction is that it does **not** form the same puncta.
2. **Establish condensate-dependence of fusion transcription.** Use an **optoDroplet / optogenetic**
   construct to force or relieve condensation on demand and read out fusion target-gene transcription,
   and test **1,6-hexanediol sensitivity** of both the puncta and the transcriptional output (with all
   the tool-compound caveats of §2.3). The decisive question: does fusion-driven transcription require
   the condensed state?
3. **Screen condensate modulators for fusion-transcription loss.** With a condensate/transcription
   readout in hand, screen candidate condensate-modulating chemical matter and partition-probes for
   **selective loss of fusion transcriptional output** versus a wild-type-NR4A3 / generic-condensate
   counter-screen. A hit is interesting only if it spares normal condensates (see §5).

If experiment 1 fails — if EWSR1::NR4A3 does not form LC-domain-dependent, liquid-like condensates in
EMC cells, or if its transcription does not depend on that state — this entire route is falsified, and
weight should move back to the LBD-shared degrader and the fusion-junction ASO/immuno routes in the
roadmap. We state that falsifier plainly.

---

## 5. Selectivity & safety: the right risk is *other* condensates, not wild-type NR4A3

**The fusion-selectivity argument is genuinely strong on the wild-type-NR4A3 axis.** Because the
condensate behaviour is encoded by the EWS LC domain that wild-type NR4A3 does not carry, a
condensate-directed agent acts on a property the wild-type protein lacks. This now has **first-party
sequence-feature support** (§3.2): the EWS/TAF15 LC domains carry the LLPS/prion compositional signature
and the **non-prion NR4A3_AF1 control** — NR4A3's own disordered N-terminus — does **not**, evidence
that the condensate-driving composition is fusion-emergent rather than a generic property of NR4A3's
disorder. (These are sequence proxies, not a condensate measurement; see the §3.2 and §6 caveats.) This is precisely the
selectivity gap the LBD-shared degrader cannot close: that agent removes NR4A3 protein (fusion and
wild-type alike) and must rely on the tumour's *dependence* on NR4A3 for its therapeutic window,
whereas a condensate-directed agent is, in mechanism, blind to wild-type NR4A3 monomer. Sparing
wild-type NR4A3 matters: NR4A3 (with NR4A1) is a myeloid **tumour suppressor** whose combined loss is
leukaemogenic (Mullican et al., *Nat Med* 2007) and is tumour-suppressive in other tissues (Safe &
Karki, *Mol Cancer Res* 2021), so a fusion-only mechanism avoids the on-pathway liability the systemic
degrader must engineer around.

**But the honest, dominant selectivity risk is different: the cell is full of normal condensates.**
Nucleoli, stress granules, P-bodies, Cajal bodies, transcriptional and splicing condensates, and the
phase behaviour of wild-type FET proteins (FUS, EWSR1, TAF15) are all LLPS-driven and physiologically
essential. A small molecule that "dissolves condensates" or a tool like 1,6-hexanediol acts on this
whole class. **The hard problem for this route is not distinguishing the fusion from wild-type NR4A3
— it is distinguishing the fusion's condensate from every other condensate in the cell.** Whether
selective condensate pharmacology — partitioning into one specific condensate by composition/sequence
identity — is achievable is an **open, emerging question**, and it is the single biggest reason this
route is rated immature. We do not assert it is solvable; we flag it as the central risk any program
here must confront, and as a key counter-screen design requirement in §4.

---

## 6. Limitations (read this — this is the earliest-stage of the three protein routes)

- **Condensate pharmacology is early and largely unproven.** Selectively and therapeutically
  modulating a specific biomolecular condensate in vivo is a research frontier, not an established
  modality. There is no validated EMC-condensate-directed agent, and the general feasibility of
  selective condensate drugging is unsettled. This route is the **least mature** of the three
  protein-level fusion-unique routes in the portfolio, and should be weighted accordingly.
- **Predicted disorder ≠ demonstrated LLPS ≠ druggable condensate.** Three separate gaps: (1) pLDDT
  disorder is a sequence/structure proxy, not a phase-separation measurement; (2) LLPS in vitro or in a
  reporter does not establish that fusion transcription *depends* on the condensed state in EMC; (3)
  even a demonstrated, dependence-validated condensate may not be **druggable** — there may be no
  selective chemical handle. Each gap is a place this route can fail.
- **Mechanism-to-drug gap.** We name mechanisms (partition/dissolve; block self-association/recruitment;
  tool-compound probe), not molecules. Disordered, multivalent self-association surfaces are among the
  hardest targets in chemistry, and bulk material properties of a droplet are not a classical binding
  site. The path from "this mechanism is fusion-selective" to "this molecule does it selectively" is
  long and not crossed here.
- **No EMC-specific condensate data exist in this work.** All condensate evidence cited is for the EWS
  LC domain / FET-fusion class (Boulay 2017; Nott 2015; Kwon 2013), not an EWSR1::NR4A3-resolved
  measurement. The decisive EMC experiments (§4) have not been done.
- **The new computation is sequence proxies, not a condensate measurement.** The first-party numbers
  are now the pre-existing pLDDT values **plus** the §3.2 sequence-feature descriptors
  (`../modalities/fusion-idr-features.json`, run CPU-only on a GitHub runner). The latter are
  composition/charge-patterning/entropy **proxies** for phase-separation propensity — they strengthen
  the premise and supply the non-prion NR4A3_AF1 control, but they do **not** demonstrate that the
  fusion forms condensates or that its transcription depends on them; that remains the §4 wet-lab step.
- **Wild-type side stated carefully.** The selectivity claim is specifically that wild-type NR4A3
  lacks the EWS prion-like LC domain that drives FET-fusion LLPS — not a claim that wild-type NR4A3 is
  wholly devoid of disorder or coactivator interactions.
- **Not clinical evidence.** Nothing here has been tested in a patient, a cell, or a tube by this work.

---

## 7. Broader indications: this generalises to other condensate-driven oncogenic fusions

The mechanism is not EMC-specific, which both motivates the route and shares its risk across a family:
- **FET-fusion sarcomas.** The EWS/FUS/TAF15 prion-like LC domain drives the same condensate biology in
  **Ewing sarcoma (EWSR1::FLI1)** and other FET-fusion sarcomas; Boulay et al. (2017) demonstrated the
  BAF-retargeting condensate mechanism in this broader FET-fusion context. A genuinely fusion-selective
  condensate-directed strategy validated in one FET fusion could, in principle, generalise across the
  class — while inheriting the same "which condensate?" selectivity problem in each.
- **Other condensate-driven fusions.** Beyond FET fusions, other oncogenic transcription-factor fusions
  drive transcription through aberrant LLPS/condensate behaviour [broader-class citations to verify].
  The same logic — target the emergent condensate property the fusion has and neither parent does —
  applies, and the same emerging-field caveats apply with it.

EMC remains the clean entry point: a single near-clonal driver, a quiet genome, and a sharp
fusion-vs-wild-type structural asymmetry (the EWS LC domain present only in the fusion) that makes the
fusion-selectivity argument unusually crisp. It is the entry point, not the endpoint — but it is the
earliest-stage route, and this paper's job is to state the hypothesis honestly, not to oversell it.

---

## References

**Verified pool (cite faithfully):**
- Boulay G, et al. *Cancer-specific retargeting of BAF complexes by a prion-like domain.* **Cell**
  171(1):163–178.e19 (2017). doi:10.1016/j.cell.2017.07.036. *(EWS prion-like LC domain retargets BAF;
  the FET-fusion condensate-mechanism paradigm.)*
- Nott TJ, et al. *Phase transition of a disordered nuage protein generates environmentally responsive
  membraneless organelles.* **Mol Cell** 57(5):936–947 (2015). doi:10.1016/j.molcel.2015.01.013.
  *(General disordered-protein LLPS precedent.)*
- Kwon I, et al. (2013). *[low-complexity / prion-like FET-domain self-association — locator (journal/
  volume/DOI/PMID) to verify before submission].*
- Varadi M, et al. *AlphaFold Protein Structure Database…* **Nucleic Acids Res** 50:D439–D444 (2022).
  doi:10.1093/nar/gkab1061. *(pLDDT as order/disorder proxy.)*
- Wang Z, et al. *Structure and function of Nurr1 identifies a class of ligand-independent nuclear
  receptors.* **Nature** 423:555–560 (2003). doi:10.1038/nature01645. *(NR4A orphan-receptor / Nurr1
  pocket context.)*
- Mullican SE, et al. *Abrogation of nuclear receptors Nr4a3 and Nr4a1 leads to development of acute
  myeloid leukemia.* **Nat Med** 13:730–735 (2007). doi:10.1038/nm1579. *(NR4A1/3 myeloid
  tumour-suppressor liability spared by a fusion-only mechanism.)*
- Safe S, Karki K. *The Paradoxical Roles of Orphan Nuclear Receptor 4A (NR4A) in Cancer.* **Mol Cancer
  Res** 19(2):180–191 (2021). doi:10.1158/1541-7786.mcr-20-0707.
- Sjögren H, et al. *EWSR1/NR4A3 fusion in extraskeletal myxoid chondrosarcoma.* *(EMC fusion biology;
  shared with companion papers — see their fact-check log.)*
- Panagopoulos I, et al. *Fusion variants/partners in EMC (incl. TAF15, TCF12, TFG, FUS).* *(Shared
  with companion papers — see their fact-check log.)*
- Bangerter, et al. (2023). *USZ-EMC patient-derived EMC model.* *(EMC cell model for the §4 assays;
  see roadmap fact-check log.)*
- Iwata S, et al. *NCC-EMC patient-derived EMC cell lines.* *(EMC cell models; see roadmap fact-check
  log.)*

**To verify (do not treat as grounded):** the Kwon et al. 2013 locator above; the broader-class non-FET
condensate-fusion citations in §7. (The §3.2 sequence-feature analysis uses first-party pure-stdlib
descriptors, not a third-party predictor, so it carries no external-tool citation to verify; the
descriptor families it implements — SYGQ/aromatic composition, FCR, SCD, Shannon entropy — are
standard.) None of these should be cited as fact until grounded against the primary record.

---

*Author contributions, competing interests, funding: independent, unfunded, single non-clinician author
with AI assistance (Claude) for drafting and structuring; all biological claims are cited and require
sarcoma-specialist and biophysics review before any submission. No competing interests. No funding. A
wet-lab/biophysics collaborator is explicitly sought to run the condensate assays of §4. Medical-
integrity note: no medical facts, statistics, citations, DOIs, PMIDs, authors, or data were fabricated;
the first-party numbers are the committed pLDDT values in `../modalities/nr4a3-structure-assessment.json`
(EWSR1 1–264 pLDDT 38.8 / 98.1% < 50; NR4A3 LBD 85.0) and the §3.2 sequence-feature descriptors in
`../modalities/fusion-idr-features.json` (run CPU-only on a GitHub runner; quoted faithfully and flagged
as phase-separation proxies, not a condensate measurement); unverifiable citations are flagged
"to verify"; condensate pharmacology is flagged throughout as an emerging, unproven field.*
