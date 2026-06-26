# A fusion-selective antisense oligonucleotide against the EWSR1::NR4A3 breakpoint junction: RNA-level fusion-exclusivity that the NR4A3 degrader cannot reach

> **In-silico design / feasibility draft (2026-06).** No wet lab; no molecule synthesized; **NO new
> GPU/compute run was performed for this draft** — the only real result cited here is the already-committed
> CPU design output [`../modalities/junction-aso-designs.json`](../modalities/junction-aso-designs.json)
> (5 fusion-specific gapmers). **The fusion-selectivity rationale in one line:** the breakpoint mRNA seam is
> present *only* in the chimera, so an RNase-H gapmer (or siRNA) targeting the junction silences
> EWSR1::NR4A3 while sparing wild-type *EWSR1* and wild-type *NR4A3* — true fusion-exclusivity, which an
> LBD-binding degrader (identical domain in fusion and wild-type) cannot achieve. Every clinical/quantitative
> claim is cited, computed from committed repo output, or flagged as a design hypothesis. Nothing here is a
> validated drug or clinical evidence.

---

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is defined in the large majority of cases by an in-frame fusion
of *EWSR1* (less often *TAF15*, and rarely TCF12/TFG/FUS) to the orphan nuclear receptor *NR4A3*, on an
otherwise "quiet" genome with few recurrent secondary mutations [Sjögren; Panagopoulos]. The companion
NR4A3-degrader program in this repo targets the **NR4A3 ligand-binding domain (LBD)** — a domain whose
sequence is *identical* in the fusion and in wild-type NR4A3 — so that agent is NR4A3-selective but **not
fusion-selective**, and it carries the residual liability of also removing tumour-suppressive wild-type
NR4A3 [Mullican; Safe & Karki]. This manuscript pursues the one feature the degrader cannot offer: **true
fusion-exclusivity at the RNA level.** The chimeric mRNA contains a breakpoint *junction sequence* that
exists in no normal transcript; an antisense gapmer whose central DNA window straddles that seam directs
RNase-H1 cleavage of the fusion transcript while sparing both parent mRNAs by sequence, and a
junction-spanning siRNA offers a parallel route. We report the one real, committed computational result —
**5 fusion-specific candidate gapmers** designed against the modelled EWSR1::NR4A3 junction
([`junction-aso-designs.json`](../modalities/junction-aso-designs.json)), each drawing bases from both
sides of the seam and absent as a perfect complement from either parent CDS — together with the honest
caveat that surfaces immediately: this junction is **GC-rich (~75–81% GC)**, outside the usual comfort
zone, and would need chemistry tuning. We then specify what is computable *now* without any GPU (extended
tiling, a CPU genome-wide off-target complementarity screen, an siRNA alternative, and a breakpoint-keyed
per-patient panel), and we are explicit that the genuinely unsolved problem is **tumour delivery**, which
we discuss only at the hypothesis level (e.g. a B7-H3-targeted antibody–oligonucleotide conjugate or a
receptor-targeted nanoparticle). We ask others to run one decisive experiment: junction-ASO versus
scrambled-control knockdown in patient-derived EMC lines (USZ-EMC [Bangerter]; NCC-EMC [Iwata]), with
specificity confirmed by sparing of the parental transcripts. The platform generalises to any
recurrent-fusion cancer with a defined breakpoint; EMC is the proof-of-concept entry indication.

---

## 1. Background and the fusion-selectivity rationale

EMC's defining lesion creates a chimeric transcription factor: the N-terminal low-complexity /
transactivation region of EWSR1 (a FET-family protein) fused to most of NR4A3 (NOR-1), an orphan member of
the NR4A nuclear-receptor subfamily [Sjögren; Panagopoulos]. *EWSR1::NR4A3* is the dominant variant;
*TAF15::NR4A3* accounts for a substantial minority, with rarer partners (TCF12, TFG, FUS) [Panagopoulos].
Critically, EMC otherwise carries **few recurrent secondary mutations** — a "quiet genome" — so the fusion
is, to a first approximation, the single clonal driver of the disease [Panagopoulos; and see the
EMC-program roadmap]. A therapy that neutralises the fusion transcript should therefore reach essentially
every tumour cell, with no large mutational landscape offering obvious escape.

**The central differentiator — why this paper exists alongside the degrader.** The repo's lead modality is
a PROTAC/molecular-glue degrader that engages the **NR4A3 ligand-binding domain** and recruits an E3 ligase
to remove the protein (see [`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md)). That LBD is retained
near-intact in the fusion, and its amino-acid sequence is **identical** to that of wild-type NR4A3. A
ligand that binds the fusion's LBD therefore cannot, in principle, distinguish the fusion from wild-type
NR4A3: the degrader is **NR4A3-selective but not fusion-selective**. The degrader paper handles this
honestly — its selectivity work is *paralogue* selectivity (NR4A3 vs NR4A1/NR4A2), not *fusion-vs-wildtype*
selectivity — and it is bounded by NR4A3's own tumour-suppressor roles (combined NR4A1/NR4A3 loss causes
AML [Mullican]; NR4A3 is tumour-suppressive in HCC/breast/lymphoma [Safe & Karki]). Removing wild-type
NR4A3 systemically is thus a real liability the degrader must manage.

The fusion **mRNA junction** dissolves this problem at the sequence level. The breakpoint seam — the few
nucleotides where the retained EWSR1 exon is spliced to the retained NR4A3 exon — is a contiguous sequence
that appears in **neither** parent transcript. An antisense oligonucleotide complementary to that seam, or
an siRNA spanning it, can engage the chimera while each wild-type mRNA matches only one half of the oligo.
This is the RNA-level expression of "fusion-unique": fusion-exclusivity **by sequence**, achieving exactly
the discrimination the LBD degrader cannot. The two modalities are complementary, not redundant — the
degrader removes the oncoprotein (and, accepting the liability, wild-type NR4A3 too); the junction ASO
removes only the chimeric transcript.

---

## 2. The approach: junction-spanning gapmer or siRNA

Two transcript-level mechanisms can exploit the junction; both require the active sequence to **straddle**
the breakpoint so that fusion-exclusivity is enforced by base-pairing.

**(a) RNase-H1 gapmer (lead).** A gapmer is a short oligo with a central DNA "gap" flanked by modified
"wings" (LNA — locked nucleic acid — or cEt — constrained ethyl). The wings raise affinity and nuclease
resistance; the DNA gap, once hybridised to the target, recruits endogenous RNase-H1 to cleave the RNA
strand [Crooke et al. 2021]. For fusion-exclusivity the central DNA gap must span the junction, because
RNase-H1 cleaves within the DNA:RNA duplex of the gap — so the cleaved bond sits across the tumour-specific
seam, and a parent transcript (matching only one wing-plus-partial-gap) does not form the contiguous duplex
needed for catalysis. The committed designs (§3) use a 16-mer **5-6-5** LNA/DNA/LNA architecture; the
design script's docstring also references the common **5-10-5** gapmer layout as the standard template
[`junction_aso.py`].

**(b) Junction-spanning siRNA (parallel route).** An siRNA / shRNA whose guide strand is centred on the
junction loads into RISC and directs Ago2 cleavage of the chimeric mRNA. siRNA chemistry (2′-OMe / 2′-F,
phosphorothioate, and conjugation handles) is mature, and RISC tolerates the GC-rich seam differently from
RNase-H, so the siRNA route is a genuine fallback if gapmer chemistry proves intractable at this GC content
(§6). The selectivity logic is the same: the guide must cover the seam, and a single-nucleotide-resolved
seed mismatch against either parent transcript is what buys fusion-exclusivity. siRNA off-target
(seed-mediated) behaviour differs from ASO off-target behaviour, so the two routes need separate
specificity screens.

**Chemistry options (both routes).** Backbone phosphorothioate for stability/protein binding; sugar
modifications (LNA/cEt for gapmers; 2′-OMe/2′-F for siRNA); and — central to the unsolved delivery problem
(§3c) — conjugation handles (GalNAc is hepatocyte-directed and therefore *not* useful for a soft-tissue
sarcoma; a tumour-receptor-directed conjugate is what EMC would need).

---

## 3. Computational groundwork

### 3a. What already exists (real, committed output)

[`research/modalities/junction_aso.py`](../modalities/junction_aso.py) fetches the RefSeq CDS of *EWSR1*
(NM_005243) and *NR4A3* (NM_006981) from NCBI, builds the **modelled** fusion CDS at the canonical
protein-level breakpoint (EWSR1 kept to codon 264; NR4A3 retained from codon 2 — flagged in the output as
an assumption), and tiles 16-mer 5-6-5 gapmers whose central DNA gap spans the junction. It keeps only
oligos that (i) draw bases from **both** sides of the seam and (ii) are **not** a perfect complement of
either parent CDS. The committed result
([`junction-aso-designs.json`](../modalities/junction-aso-designs.json)) reports **5 fusion-specific
candidate gapmers** (`n_candidates = 5`, `n_fusion_specific = 5`), e.g. the top design antisense
`5′-ACGCAGGGCTGCTGCC-3′` (target mRNA `GGCAGCAGCCCTGCGT`, 8 bases from each side of the seam,
specificity margin 8). The modelled junction context is `…TACGGGCAGCAG|CCCTGCGTCCAA…`.

**The honest design caveat surfaces immediately and is reported as a real finding:** this junction is
**GC-rich**, with the top candidates at **75–81% GC** (75.0% and 81.2% across the five), well outside the
usual 40–60% gapmer comfort zone. None carry a G-quadruplex (≥4 consecutive G) motif (`has_G4_motif:
false` for all five), but the high GC alone implies elevated melting temperature, self-structure and
potential aggregation/tox risk that would require chemistry tuning (wing chemistry, length, or the siRNA
route). This is exactly the kind of constraint a design tool should expose up front; it is recorded here as
a real, committed result, not hidden.

> **Integrity flag (breakpoint is modelled).** The committed designs use an *assumed* canonical breakpoint
> (the JSON marks `_breakpoint_model.assumption = true`). They are correct as a worked example of the
> method, but for any clinical design the script must be re-run on a patient's **sequenced** fusion
> transcript (§3b). The five sequences are design hypotheses, not a drug.

### 3b. What is specifiable now, without any GPU

All of the following are CPU-only and need no new GPU/compute run; they are specified, not executed, in
this draft:

1. **Expanded tiling.** Re-run the existing tiler over a wider window and multiple oligo lengths (e.g.
   14–20-mers) and both 5-6-5 and 5-10-5 architectures, to enumerate the full junction-spanning design
   space rather than the top-5 snapshot, and to find any lower-GC register that still straddles the seam.
2. **Genome-wide off-target complementarity screen (CPU).** The current specificity check only confirms an
   oligo is not a *perfect* complement of the two parent CDSs. A real specificity claim requires a
   transcriptome-wide near-match search (allowing mismatches/gaps, with gap-region weighting since RNase-H
   tolerates wing mismatches more than gap mismatches) — a standard CPU alignment/seed-scan job (e.g.
   against RefSeq/GENCODE). This is the single most important *computable* upgrade and is flagged as not
   yet done.
3. **siRNA alternative (computable).** Generate junction-spanning siRNA guides with standard design rules
   (asymmetry/thermodynamic end stability, seed off-target counting against the transcriptome) as a
   GC-tolerant parallel set — same junction, different mechanism (§2b).
4. **Breakpoint heterogeneity → a per-patient panel.** Because EMC breakpoints vary by exon usage (the
   companion neoantigen work resolved *7 distinct in-frame junctions* across EWSR1 exons 7/9/10/11/12/13 →
   predominantly NR4A3 exon 3; see [`novel-modalities.md`](./novel-modalities.md) §3.3), the ASO sequence
   is **breakpoint-conditional**. The deployable artifact is therefore not one oligo but a *panel*:
   key each patient's design to their sequenced breakpoint, exactly as the script already supports by
   re-running on the patient transcript. This is a feature of the modality, not a bug — it mirrors the
   personalised logic the immunotherapy route reached independently.

### 3c. The honest hard part — tumour delivery (unsolved)

Oligonucleotide *design* is tractable; **delivery to an EMC tumour is not**, and this is stated plainly as
the limiting problem. Systemically administered naked gapmers distribute to liver/kidney; GalNAc
conjugation (the one solved targeting handle) is hepatocyte-directed and useless for a soft-tissue sarcoma.
Options below are **hypotheses, explicitly flagged**, not validated approaches:

- **Receptor-targeted antibody–oligonucleotide conjugate (AOC).** Couple the gapmer/siRNA to an antibody
  against a surface antigen enriched on EMC cells. **B7-H3 (CD276)** is one candidate worth evaluating as
  an EMC surface marker — *flagged as a hypothesis to verify; B7-H3 expression in EMC specifically is
  [citation to verify].* AOC platforms exist in other indications but none is established for EMC.
- **Receptor-/ligand-targeted nanoparticle (LNP or polymer).** Encapsulate the oligo and decorate with a
  ligand for an EMC-enriched receptor. Again, the specific EMC-enriched receptor is the unsolved input
  [citation to verify].
- **Local/intratumoural administration** for accessible lesions, sidestepping systemic targeting — a
  narrower but more tractable first-in-human setting (hypothesis).

No delivery claim is made; this section exists to mark delivery as the dominant risk, not to assert a
solution.

---

## 4. The decisive experiment we ask others to run

Computation cannot establish that junction silencing kills EMC cells, nor confirm parental sparing in a
living transcriptome. The single decisive, wet-lab-doable experiment is:

**Junction-ASO vs. scrambled-control knockdown in patient-derived EMC lines.** Transfect (or free-uptake /
gymnose) the committed candidate gapmers — and a junction-spanning siRNA — into **USZ-EMC** [Bangerter] and
**NCC-EMC** [Iwata], against a scrambled/mismatch control matched for length and GC. Read out:

1. **On-target knockdown** of the fusion transcript (junction-spanning qPCR / RNA-seq across the breakpoint)
   and of fusion protein.
2. **Specificity — the crux:** wild-type *EWSR1* and wild-type *NR4A3* transcripts must be **spared**
   (allele/exon-resolved or junction-discriminating assays), confirming the oligo silences only the chimera.
3. **Phenotype:** viability/proliferation/apoptosis, to test whether the cells are addicted to the fusion
   transcript.

This is the experiment that converts five sequences and a mechanism into evidence. It needs no new molecule
beyond synthesising the listed oligos and no new biology beyond the published EMC models.

---

## 5. Selectivity and safety

- **Fusion-exclusive by sequence.** The active oligo spans the breakpoint; neither parent mRNA presents the
  contiguous junction duplex required for RNase-H (gapmer) or RISC (siRNA) cleavage. Selectivity is
  enforced by base-pairing, not by protein conformation.
- **Spares wild-type NR4A3 — and therefore avoids the tumour-suppressor liability the degrader carries.**
  This is the key safety advantage over the LBD degrader. Because the junction is absent from wild-type
  *NR4A3*, the oligo does not touch the wild-type transcript, side-stepping the AML risk of combined
  NR4A1/NR4A3 loss [Mullican] and the HCC/breast/lymphoma tumour-suppressor roles of NR4A3 [Safe & Karki].
- **Spares wild-type EWSR1.** EWSR1 is a broadly expressed FET-family gene with essential functions; a
  junction oligo leaves the wild-type *EWSR1* transcript intact, matching only one wing.
- **Residual risks remain and must be tested, not assumed away:** sequence-based off-target hybridisation
  elsewhere in the transcriptome (the §3b CPU screen is the in-silico filter; only the wet-lab experiment
  is proof), and chemistry-class / phosphorothioate effects (hepatotoxicity, complement, platelet effects)
  that are generic to oligonucleotide drugs [Crooke et al. 2021]. Predicted specificity is a screen, not a
  guarantee (§6).

---

## 6. Limitations

- **GC-rich chemistry.** The modelled junction yields 75–81% GC gapmers — outside the comfort zone; high Tm
  and self-structure risk would need chemistry tuning, an alternative register, or the siRNA route (§2b).
  This is a real, committed finding, not a hypothetical.
- **Breakpoint-conditional (personalised).** The active sequence depends on the patient's exact exon-level
  breakpoint; the deliverable is a breakpoint-keyed panel, and every clinical design must be re-derived from
  a sequenced fusion transcript (the committed designs use a *modelled* breakpoint).
- **Delivery unsolved.** No validated tumour-delivery route for EMC exists; §3c lists hypotheses only. This
  is the dominant risk for the whole modality.
- **Knockdown, not knockout.** ASO/siRNA reduce transcript; they do not eliminate the gene or guarantee
  durable, complete loss of fusion protein. Depth and duration of knockdown are empirical.
- **Predicted specificity ≠ validated specificity.** The committed output only excludes perfect parental
  complementarity; the transcriptome-wide near-match screen (§3b) is specified but not yet run, and even it
  is in-silico. Only the §4 experiment can confirm parental sparing in cells.
- **No molecule, no clinical claim.** This is a computation-only, publish-to-convince draft. Nothing here
  has been tested in a patient.

---

## 7. Broader indications

The junction-ASO concept is a **platform**, not an EMC-only tactic: it applies to **any recurrent-fusion
cancer with a defined, sequenced breakpoint**, because the only requirement is a tumour-specific mRNA seam
absent from both parent transcripts. Natural extensions include other **FET-family / EWSR1-fusion
sarcomas** (the EWSR1-rearranged sarcoma spectrum more broadly), where the same design-and-screen pipeline
([`junction_aso.py`](../modalities/junction_aso.py) plus the §3b CPU off-target screen) applies with only
the breakpoint sequence changed. EMC is the proof-of-concept entry indication precisely because it is the
cleanest case — a quiet genome with a single near-clonal fusion driver — so a positive parental-sparing
knockdown result here is the strongest possible demonstration that the platform discriminates fusion from
wild-type at the RNA level. *(Specific partner cancers beyond the EWSR1/FET family are not enumerated here
to avoid over-claiming; each would need its own breakpoint sourcing — [citation to verify] per indication.)*

---

## References

Verified reference pool (appear verified in the repo):

- **Sjögren H, et al.** *EWSR1/NR4A3 fusion in extraskeletal myxoid chondrosarcoma.* (EMC defining fusion.)
- **Panagopoulos I, et al.** *Fusion variants and partners in EMC* (incl. TAF15, TCF12, TFG, FUS).
- **Crooke ST, et al.** *Antisense technology: an overview and prospectus.* **Nat Rev Drug Discov** 2021.
  doi:10.1038/s41573-021-00162-z. (Antisense / gapmer / RNase-H1 mechanism overview.)
- **Bangerter, et al.** USZ-EMC patient-derived EMC model (2023).
- **Iwata S, et al.** NCC-EMC patient-derived EMC cell lines.
- **Mullican SE, et al.** *Abrogation of Nr4a3 and Nr4a1 leads to acute myeloid leukemia.* **Nat Med** 2007.
  (Wild-type NR4A1/NR4A3 loss → AML — the tumour-suppressor liability the junction ASO avoids.)
- **Safe S, Karki K.** *The paradoxical roles of orphan nuclear receptor 4A (NR4A) in cancer.* **Mol Cancer
  Res** 2021. (NR4A3 tumour-suppressor roles in HCC/breast/lymphoma.)
- **Le Guilloux V, Schmidtke P, Tufféry P.** *Fpocket.* **BMC Bioinformatics** 2009. (Referenced for the
  companion structural/degrader work; not used in this RNA-level analysis.)
- **Varadi M, et al.** *AlphaFold Protein Structure Database.* **Nucleic Acids Res** 2022.
  doi:10.1093/nar/gkab1061. (Referenced for the companion structural work; not used here.)

To verify (do **not** treat as established until sourced):

- B7-H3 (CD276) surface expression in EMC specifically — **[citation to verify]**.
- EMC-enriched surface receptor(s) suitable for AOC / targeted-nanoparticle delivery — **[citation to verify]**.
- Specific non-EWSR1/FET recurrent-fusion cancers as platform extensions — **[citation to verify]** per indication.

**Reproducibility.** The only real result cited here is the committed CPU design output
[`junction-aso-designs.json`](../modalities/junction-aso-designs.json), produced by
[`junction_aso.py`](../modalities/junction_aso.py). No new computation was performed for this draft.
