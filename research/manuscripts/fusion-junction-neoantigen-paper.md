# Targeting the EWSR1::NR4A3 fusion-junction neoantigen in extraskeletal myxoid chondrosarcoma: a fusion-exclusive immunotherapy rationale from breakpoint-resolved epitope prediction and HLA population coverage

> **IN-SILICO, PUBLISH-TO-CONVINCE — no wet lab, no new computation for this draft.** Every number
> below is quoted from an already-committed pipeline output (`fusion-breakpoint-neoantigens.json`,
> `hla-coverage.json`, and the §3.3 results table in [`novel-modalities.md`](./novel-modalities.md));
> nothing was re-run to write it. **Fusion-exclusive rationale, in one line:** the peptide spanning the
> EWSR1→NR4A3 seam exists in *no* normal protein, so an immune response against it is both tumour-exclusive
> *and* fusion-exclusive — the cleanest selectivity layer available, complementary to (not a replacement
> for) the repo's NR4A3-LBD degrader, which is NR4A3-selective but **not** fusion-selective.

*Draft (2026-06). Authors/affiliations TBD. Companion to the NR4A3-degrader result paper
([`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md)) and the EMC-program roadmap
([`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md)); it carries forward, in standalone form, the
neoantigen groundwork in [`novel-modalities.md`](./novel-modalities.md) §3.3, the parked coverage
analysis [`hla-coverage-emc.md`](./hla-coverage-emc.md), and the clinician brief
[`clinical-brief-emc-neoantigen.md`](./clinical-brief-emc-neoantigen.md). Predicted MHC binding is a
screen, not proof of immunogenicity; no claim here is medical advice or evidence that any product works
in EMC.*

---

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is defined in ~90% of cases by an in-frame fusion of *EWSR1*
(or, in ~16%, *TAF15*) to the orphan nuclear receptor *NR4A3*, on an otherwise quiet genome. The repo's
small-molecule track pursues an NR4A3-degrader that engages the **NR4A3 ligand-binding domain (LBD)** —
selective for NR4A3 over its NR4A1/2 paralogues, but **not** selective for the fusion, because that LBD is
shared with wild-type NR4A3. This paper pursues the orthogonal, immune-level **fusion-exclusive** axis: the
handful of residues spanning the EWSR1→NR4A3 junction form a peptide present in no normal protein, so a
T-cell response against it spares wild-type NR4A3 entirely and cannot, in principle, harm any normal cell.
We summarise the already-committed, reproducible evidence base for this approach and frame the clinical
modalities it enables — personalised neoantigen vaccine, TCR-T, and soluble-TCR (ImmTAC)-style products —
without performing or asserting any new computation. Breakpoint-resolved prediction (junctions derived from
real Ensembl exon structure, MHCflurry-2.0) finds **7 in-frame junctions** (EWSR1 exons 7/9/10/11/12/13 →
predominantly NR4A3 exon 3) yielding **26 distinct predicted binders**, with **no single pan-EMC epitope**:
the most-shared candidate appears in only 2 of 7 junctions and is a weak binder, so strong binders are
breakpoint-specific. HLA class-I population coverage (AFND frequencies, IEDB formula) is **~30%** for the
commonly reported EWSR1 e7::NR4A3 e3 public junction (A\*11:01 + B\*08:01; 29.7%, 95% CI 29.0–30.3%),
**~58%** for all strong-binder alleles pooled (58.0%, 95% CI 57.1–59.0%), with **large regional variation**
(36% Sub-Saharan Africa to 79% Northern Europe), and a **~16% "both-arms" floor** when a class-II (CD4
helper) allele is also required (16.5%; the class-II figure is itself a floor over a 3-allele DR panel).
The honest conclusion is that a fusion-exclusive EMC immunotherapy is **personalised by necessity** (no
off-the-shelf pan-EMC epitope) and **acceptable** (the platforms already exist in humans, and many patients
carry a presenting allele). The decisive experiment is wet-lab and stated as such. All figures are
hypothesis-generating and require sarcoma-immunology review.

---

## 1. Background and the fusion-selectivity rationale

EMC's defining lesion is a gene fusion creating a chimeric transcription factor: the N-terminal
low-complexity/transactivation domain of EWSR1 (a FET-family protein) fused to most of NR4A3 (NOR-1), an
orphan member of the NR4A nuclear-receptor subfamily [Sjögren et al.; Panagopoulos et al.]. EWSR1::NR4A3
accounts for most cases, TAF15::NR4A3 for ~16%, with rarer partners; the genome is otherwise quiet, so the
fusion is, to a first approximation, *the* disease.

**Three nested layers of selectivity.** A therapy against EMC can be selective at three increasingly tight
levels:

1. **Tumour-vs-normal by lineage/over-expression** — the weakest layer; many normal tissues express the
   parent genes.
2. **NR4A3-selective** — the layer the repo's degrader achieves. It binds the NR4A3 LBD and spares the
   NR4A1/NR4A2 paralogues (whose loss is toxic — notably leukaemogenic), engaging divergent pocket residues
   as selectivity handles ([`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md) §2.3). But the NR4A3 LBD
   is **identical in the fusion and in wild-type NR4A3**, so a degrader cannot distinguish the oncoprotein
   from the normal receptor — it is NR4A3-selective, *not fusion-selective*.
3. **Fusion-exclusive** — the layer this paper targets. The few residues that span the EWSR1→NR4A3 seam
   form a sequence that exists in **no normal protein**: neither in wild-type EWSR1 (which ends before the
   seam) nor in wild-type NR4A3 (which begins after it). A peptide drawn across that seam is therefore both
   **tumour-exclusive** (only fusion-positive cells make it) and **fusion-exclusive** (it is absent from the
   wild-type receptor the degrader cannot avoid). If such a peptide is presented on MHC, a T-cell response
   against it is the **cleanest possible selectivity** for EMC: it spares wild-type NR4A3, EWSR1, and every
   normal cell, and — because the fusion is the truncal, clonal driver present in every tumour cell and
   never subclonally lost — it cannot be escaped by antigen loss the way a passenger-mutation response can.

This is the rationale for an *immune-level* fusion-unique approach as a complement to the small-molecule
degrader. The degrader removes NR4A3 (fusion or wild-type) wherever it is; the junction neoantigen marks
*only* fusion-expressing cells for immune attack. They attack the same disease from non-overlapping
selectivity premises, and neither needs a druggable pocket on the disordered EWSR1 transactivation domain.

**Why this is not already a therapy.** Not because the biology is unknown, but because the steps past
"know the variant" are hard, and they are exactly the honest caveats of §6: the breakpoint varies between
patients (no single off-the-shelf product), the junction is *mostly self-sequence* (only the seam is
foreign, so central tolerance may have pruned reactive T cells), sarcomas are low-mutational-burden "cold"
tumours, and a bespoke per-patient product for an ultra-rare cancer has weak commercial pull. The value of
an in-silico analysis is to quantify what *is* tractable — which junctions exist, which peptides are
predicted presented, and on how many patients — so a clinical collaborator can judge feasibility.

---

## 2. The junction neoantigen — derived from real in-frame breakpoints

The epitope set is **not** an assumed junction. An earlier first pass (`fusion_neoantigen.py`) modelled a
*single guessed* breakpoint (EWSR1 kept to residue 264 :: NR4A3 from residue 2) and reported a strong
HLA-B\*15:01 epitope `GQQPCVQAQY`. That result was not trusted: the breakpoint was a guess, so the epitope
could be an artifact of the guess. A second, breakpoint-resolved analysis (`fusion_breakpoints.py`) removed
the assumption — it derives the real in-frame junctions from Ensembl exon structure (self-checked:
translate(CDS) == Ensembl protein; only fusions retaining an intact NR4A3 C-terminus are kept) and runs
MHCflurry-2.0 across them. **The result overturned the first:** `GQQPCVQAQY` arises from no real in-frame
junction. This self-correction is the reason the headline epitopes below come from sourced junctions, not a
convenient assumption.

The **7 in-frame junctions** (EWSR1 exons 7/9/10/11/12/13 → predominantly **NR4A3 exon 3**, whose retained
sequence reads `…VVRTDS…`) yield **26 distinct predicted binders**. The strong binders, one or two per
junction, are listed below (all values quoted from `fusion-breakpoint-neoantigens.json`):

| predicted epitope | HLA | affinity (nM) | pres. %ile | call | junction (EWSR1 exon → NR4A3 exon) |
|---|---|---|---|---|---|
| QQIVRTDSL | B\*08:01 | 96.8 | 0.037 | strong | e7 → e3 |
| SSYGQQIVR | A\*11:01 | 61.2 | 0.082 | strong | e7 → e3 |
| KPGVVRTDSL | B\*07:02 | 54.4 | 0.186 | strong | e9 → e3 |
| DLVVRTDSL | B\*08:01 | 58.1 | 0.033 | strong | e10 → e3 |
| GVVKRTVQK | A\*11:01 | 32.2 | 0.235 | strong | e11 → e2 |
| KQCGVVKY | B\*15:01 | 111.0 | 0.124 | strong | e11 → e4 |
| FDVVRTDSL | B\*08:01 | 185.1 | 0.093 | strong | e12 → e3 |
| AAVEWFDVV | A\*02:01 | 111.0 | 0.164 | strong | e12 → e3 |
| GMPPPLRGV | A\*02:01 | 44.6 | 0.142 | strong | e13 → e3 |
| RGVVRTDSL | B\*08:01 | 164.5 | 0.391 | strong | e13 → e3 |
| MPPPLRGVV | B\*07:02 | 42.5 | 0.400 | strong | e13 → e3 |
| MPPPLRGV  | B\*07:02 | 212.8 | 0.435 | strong | e13 → e3 |

**The central, honest finding is about robustness, not a single hero epitope.** No epitope is pan-EMC: the
most-shared candidate, `GVVRTDSLK` (A\*11:01), appears in only **2 of 7** junctions and is merely a *weak*
binder (presentation %ile 0.574); every strong binder is breakpoint-specific. Two consequences follow, both
faithful to the data:

1. A fusion-exclusive EMC immunotherapy is most realistically **personalised** — sequence the patient's
   breakpoint, generate the junction peptides, match to the patient's HLA — not a single off-the-shelf
   vaccine.
2. *If* one breakpoint is recurrent enough to be a "public" target, the commonly reported **EWSR1 exon 7 ::
   NR4A3 exon 3** junction is the leading candidate; its strong epitopes `QQIVRTDSL`/B\*08:01 and
   `SSYGQQIVR`/A\*11:01 then become shared targets. Whether e7::e3 is recurrent enough to act as a public
   epitope is an empirical cohort question (§5), not something prediction can settle.

**Both partners are covered.** The pipeline addresses both fusion partners. The committed worked example for
the **TAF15::NR4A3** variant (~16% of EMC; TAF15 exon 4 :: NR4A3 e3) yields its *own* strong candidates,
distinct from the EWSR1 set — e.g. `SVVRTDSLK`/A\*11:01 (37 nM) and `QSVVRTDSL`/B\*08:01 (124 nM)
([`clinical-brief-emc-neoantigen.md`](./clinical-brief-emc-neoantigen.md)) — reinforcing that the target is
patient-specific and that a TAF15-fusion patient is not served by an EWSR1 construct. A useful tie-breaker
the per-patient tool surfaces: among the e7::e3 strong CD8 epitopes, `SSYGQQIVR` straddles the seam more
evenly (6 residues from EWSR1 + 3 from NR4A3) and so is *more foreign* than the otherwise-strong
`QQIVRTDSL` (2 + 7, mostly NR4A3-self) — relevant when picking the least-tolerised target (§6).

---

## 3. HLA population coverage — quoted honestly

A predicted binder is only useful in a patient whose HLA presents it, so the clinically decisive number is
population coverage. All figures here are the committed output of `hla_coverage.py`
(`hla-coverage.json`): allele frequencies are denominator(2N)-weighted means pooled over Allele Frequency
Net Database (AFND) populations [Gonzalez-Galarza et al. 2020] with Wilson 95% CIs, and coverage =
1 − ∏(1 − af)² (the fraction carrying ≥1 presenting allele; the IEDB population-coverage formula). We quote
them without re-running anything.

**Global class-I (CD8) coverage.**

- The commonly reported **EWSR1 e7::NR4A3 e3 public junction** (presented on **A\*11:01** and **B\*08:01**)
  covers **≈30% of patients** — 29.7% (95% CI 29.0–30.3%).
- Pooling **all strong-binder alleles** across the resolved breakpoints (A\*02:01, A\*11:01, B\*07:02,
  B\*08:01, B\*15:01) reaches **≈58%** — 58.0% (95% CI 57.1–59.0%).

So a single public junction reaches under a third of patients, and even the full multi-allele panel leaves
~40% with no predicted strong-binding class-I allele.

**Large regional variation — a single global number must not be quoted alone.** These global means hide
wide between-population spread (`hla-coverage.json` → `regions`). Pooled per UN M49 sub-region, any-strong
coverage ranges from **36% (Sub-Saharan Africa)** to **79% (Northern Europe)**; the e7::e3 public junction
ranges from **~10%** (Sub-Saharan Africa, Latin America) to **~53% (Melanesia)** / **~42% (Eastern Asia)**,
tracking the high frequency of A\*11:01 in East Asian and Oceanian populations. A global figure therefore
overstates benefit for some patients and understates it for others; coverage must be confirmed for the
target population.

**CD4 help is the limiting arm, and it anti-correlates with CD8 coverage.** The DRB1 helper alleles
presenting a strong class-II junction binder (DRB1\*03:01, DRB1\*07:01) cover only **28.4% globally** (95%
CI 27.9–28.9%), and — critically — this is *anti-correlated by region* with CD8 coverage (high in Africa,
Southern Asia, Europe; near-zero in Melanesia/Polynesia and low in East Asia, the very populations where the
public CD8 junction does best). Requiring **both** a class-I *and* a class-II allele — what a durable
vaccine needs — therefore covers just **≈16%** of patients globally (16.5%). This both-arms figure is a
**floor**, because the class-II screen tested only a 3-allele DR panel (DRB1\*15:01/03:01/07:01): untested DR
(or DQ/DP) alleles that also present the helpers would only raise it.

**Read-out.** Coverage is *partial by construction* and *inequitable if framed by one global number*. This
is the quantitative case for a personalised-first design, with public junctions reserved for the specific
allele groups where coverage is genuinely high — not an argument that the approach fails, but a boundary on
how to deploy it.

---

## 4. The clinical modalities

The fusion-exclusive junction neoantigen, once validated in a patient, can be acted on by three modalities
already in human trials in other cancers — so for EMC nothing chemically novel is required, only the
EMC-specific epitopes the pipeline generates.

**(a) Personalised neoantigen vaccine (peptide or mRNA).** This is the lead, because the *platform already
exists in the clinic*: individualised mRNA neoantigen vaccines plus checkpoint blockade (mRNA-4157/V940 in
resected melanoma, KEYNOTE-942 [Weber et al., *Lancet* 2024]) and autogene cevumeran in pancreatic cancer
[Rojas et al., *Nature* 2023] are in human trials and have shown activity. A vaccine encoding the patient's
junction-spanning long peptide(s), paired with the predicted CD4 helper epitopes for durable responses,
rides this platform with EMC-specific content. **Personalised is necessary and acceptable:** §2 shows there
is no off-the-shelf pan-EMC epitope (necessity), while §3 shows the presenting alleles are among the most
common worldwide, so many patients carry ≥1 (acceptability).

**(b) TCR-T (engineered T cells).** A T-cell receptor isolated against a validated junction epitope, then
transduced into the patient's T cells, delivers the same fusion-exclusive specificity as a cell therapy
rather than a vaccine — useful where an endogenous response is weak (the cold-tumour problem, §6).
Fusion-directed TCR approaches are being explored in other sarcomas. For a recurrent public junction
(e7::e3), a single TCR against `QQIVRTDSL`/B\*08:01 or `SSYGQQIVR`/A\*11:01 could in principle serve the
allele-matched subset that §3 sizes (~30% on the public junction).

**(c) Soluble-TCR / ImmTAC-style bispecific.** A soluble affinity-enhanced TCR fused to an anti-CD3 effector
(the brenetafusp/IMCgp100-class format) redirects polyclonal T cells onto cells displaying the junction
peptide–MHC, without engineering the patient's cells. This is an off-the-shelf *format* but still requires a
public, allele-defined target (e.g. e7::e3 on a specific HLA), so its addressable fraction is bounded by the
same coverage arithmetic in §3, and a TAF15-fusion or alternate-breakpoint patient would need a different
reagent.

Across all three, the fusion-exclusivity is the shared selling point: the target peptide is absent from the
normal proteome, so on-target/off-tumour toxicity against wild-type NR4A3- or EWSR1-expressing tissue is, in
principle, not possible — the failure mode that haunts shared-antigen TCR therapies. The honest counterpart
(§6) is that "mostly self-sequence" cuts the other way for immunogenicity.

---

## 5. Decisive experiment (wet-lab; computation hands off here)

Computation narrows the search; it cannot confirm a neoantigen. The decisive program, for a consenting
patient and within an appropriate trial/IRB framework, is:

1. **Sequence the patient's breakpoint** by RNA-seq / a targeted fusion panel (often already done at
   diagnosis) to fix the exact EWSR1::NR4A3 (or TAF15::NR4A3) junction, and HLA-type the patient (class I
   and II). Run the committed `patient_neoepitopes.py` / `patient_cd4_epitopes.py` tools to generate the
   per-patient CD8 and CD4 shortlist.
2. **Confirm presentation by immunopeptidomics** — show the predicted junction peptide is actually
   processed and displayed on the patient's MHC on tumour material.
3. **Confirm T-cell reactivity ex vivo** — demonstrate that autologous T cells can recognise and respond to
   the junction peptide–MHC complex (the test of immunogenicity that binding prediction cannot provide).
4. **For a public-epitope strategy, establish recurrence** — determine how often the **EWSR1 e7::NR4A3 e3**
   junction actually recurs across an EMC cohort, since the entire off-the-shelf case (TCR-T / soluble-TCR
   on a shared target) rests on that breakpoint being common enough to be "public."

Only after steps 2–3 (and step 4 for a shared product) does any of this become a candidate for a clinical
construct. This paper stops precisely at that door.

---

## 6. Limitations

1. **The junction peptide is mostly self-sequence → central-tolerance risk.** A neoepitope spanning the
   seam is typically one or two "foreign" junction residues on an otherwise self peptide (EWSR1 and NR4A3
   are both self proteins); central T-cell tolerance may have pruned the reactive repertoire, blunting
   responses. This is a real immunological risk for *any* fusion-neoantigen approach and is the key reason
   the seam-straddling, more-foreign epitopes (e.g. `SSYGQQIVR`, 6+3) are preferable tie-breakers. It must
   be tested (steps 2–3), not assumed away.
2. **Predicted MHC binding ≠ immunogenicity.** A predicted strong binder may not be processed, presented, or
   T-cell-visible in vivo. MHCflurry-2.0 [O'Donnell et al., *Cell Systems* 2020] is a screen; processing,
   transport, TCR repertoire and tolerance are not modelled.
3. **Cold tumour.** Sarcomas are low-mutational-burden, often immunologically "cold"; even a valid
   neoantigen may not elicit a clinically meaningful response without an adjuvant/checkpoint or a cell-/
   bispecific-therapy format that does not rely on a pre-existing endogenous response.
4. **Personalised logistics.** No off-the-shelf pan-EMC epitope exists (§2), so the product is bespoke per
   patient — a manufacturing and trial-design burden for an ultra-rare cancer, mitigated only by the
   existence of platforms already running this workflow in other tumours (§4).
5. **Coverage floor and inequity.** Population coverage is partial (~30% public junction, ~58% all strong
   alleles, ~16% both-arms floor) and varies ~36–79% by region; a fixed allele panel tuned on one population
   under-serves others. The class-II / both-arms figures are floors over a 3-allele DR test panel, and the
   coverage formula assumes cross-locus independence (it ignores linkage disequilibrium — e.g. the
   A1-B8-DR3 ancestral haplotype links B\*08:01 and DRB1\*03:01).
6. **Predictions inherit upstream assumptions.** The epitope set inherits every limitation of the
   breakpoint-neoantigen predictions, and the breakpoint windows scanned (EWSR1 exons ~6–14, NR4A3 exons
   2–4) are literature-bounded; a real patient's junction must be re-derived from their sequenced breakpoint.

None of these is fatal; together they define what an honest in-silico analysis can and cannot claim, and
they map directly onto the wet-lab steps in §5.

---

## 7. Broader indications — the fusion-neoantigen pipeline generalises

The contribution that survives EMC's rarity is the **pipeline**, not a single epitope. The machinery here —
derive real in-frame junctions from exon structure, enumerate junction-spanning peptides absent from both
parents, predict MHC-I (and MHC-II helper) presentation, and compute HLA population coverage — is
gene-agnostic. It applies directly to the **other recurrent-fusion sarcomas** that share EMC's defining
features: a clonal, truncal fusion on a quiet genome, where the junction is the most reliable public
neoantigen and the same "personalised-by-necessity, platform-already-in-humans" logic holds. The same
honest caveats travel with it (mostly-self junctions, binding ≠ immunogenicity, partial and population-
dependent coverage), so generalisation is a reason to build the engine once and reuse it across the
fusion-driven sarcoma family — with EMC as the worked, fusion-exclusive entry point, not the endpoint. This
fusion-exclusive immune axis and the NR4A3-selective degrader axis are complementary routes to the same
disease; pursuing both, on non-overlapping selectivity premises, is the portfolio rationale.

---

## 8. Author contributions, competing interests, funding

Independent, unfunded work by a single non-clinician author, with AI assistance (Claude) for drafting,
code, and structuring; all clinical and biological claims are cited and require sarcoma-immunology /
immunogenetics review before any submission. No competing interests. No funding. **A sarcoma immuno-
oncology collaborator and a route to validation (immunopeptidomics + T-cell assays) are explicitly
sought** — this program is designed to be handed to one.

---

## 9. References

Verified pool (used above):

- Sjögren H, et al. EWSR1/NR4A3 fusion in extraskeletal myxoid chondrosarcoma. *(EMC-biology; shared with
  companion papers — see their fact-check log.)*
- Panagopoulos I, et al. Fusion variants/partners in EMC (incl. TAF15). *(EMC-biology; shared with
  companion papers.)*
- O'Donnell TJ, Rubinsteyn A, Laserson U. MHCflurry 2.0: improved pan-allele prediction of MHC class
  I-presented peptides. *Cell Systems* 2020. doi:10.1016/j.cels.2020.09.001.
- Weber JS, et al. Individualised neoantigen therapy mRNA-4157 (V940) plus pembrolizumab versus
  pembrolizumab in resected melanoma (KEYNOTE-942). *The Lancet* 2024.
  doi:10.1016/S0140-6736(23)02268-7.
- Rojas LA, et al. Personalized RNA neoantigen vaccines stimulate T cells in pancreatic cancer (autogene
  cevumeran). *Nature* 2023. doi:10.1038/s41586-023-06063-y.
- Gonzalez-Galarza FF, et al. Allele Frequency Net Database (AFND) 2020 update. *Nucleic Acids Res.* 2020.
  *(via the MIT-licensed `slowkow/allelefrequencies` mirror; region mapping ISO 3166 / UN M49.)*
- Bangerter, et al. USZ-EMC patient-derived EMC model. *(EMC model; shared with companion papers.)*
- Iwata S, et al. NCC-EMC patient-derived EMC cell lines. *(EMC model; shared with companion papers.)*

Not in the verified pool and **[citation to verify]** before submission:

- The IEDB population-coverage method (Bui et al., 2006) and the Wilson 95%-CI method (Wilson, 1927) as
  applied in `hla-coverage-emc.md` — **[citation to verify]** against that file's reference list.
- The brenetafusp / soluble-TCR (ImmTAC) class as a clinical format — **[citation to verify]**; no specific
  trial or compound result is claimed here beyond naming the modality.
- Fusion-directed TCR-T being "explored in other sarcomas" — **[citation to verify]**; stated as
  background, not as an EMC result.

*Medical-integrity note: every number in this draft is quoted from an already-committed pipeline output
(`fusion-breakpoint-neoantigens.json`, `hla-coverage.json`, `novel-modalities.md` §3.3,
`clinical-brief-emc-neoantigen.md`); no new computation was run for it. No clinical claim is made; predicted
binding is a screen, not proof of immunogenicity. Reproducibility: the analyses are scripted in
`research/modalities/` (`fusion_breakpoints.py`, `patient_neoepitopes.py`, `patient_cd4_epitopes.py`,
`hla_coverage.py`) and run in CI.*
