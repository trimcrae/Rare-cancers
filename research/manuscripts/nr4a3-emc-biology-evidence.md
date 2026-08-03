# EMC / NR4A3 biological-rationale evidence base (efficacy + safety)

> **Purpose.** Replace the two hand-wavy biological assumptions of the degrader program with a *quantified,
> primary-source-cited* evidence base, and — per medical-integrity rules — state honestly what did and did
> **not** survive verification. Built 2026-07-02 from an adversarially-verified deep-research pass (95 agents,
> 3-vote refutation) + the repo's cached DepMap analysis (`depmap-insilico-findings.md`). Every numeric claim
> carries a PMID/PMCID/DOI or the named database; unverified items are flagged as such and must **not** be
> stated in the manuscript as established fact.

## Hypothesis 2 — "Degrading NR4A3 hurts EMC" (efficacy). VERDICT: strong multi-pillar *prior*, one decisive gap.
The single-analogy framing is replaced by four independent pillars:

1. **The NR4A3 rearrangement is near-pathognomonic for EMC (~90–98% of cases).** EWSR1::NR4A3 is the dominant
   fusion (~62–79%; ~75% typical), with TAF15::NR4A3 (~16–27%) and TCF12/FUS/TFG::NR4A3 making up most of the
   rest — so **NR4A3 is the invariant 3′ partner regardless of the 5′ gene.** Cohorts: Modern Pathology 2023
   (**PMID 36948401**, 58 EMC: EWSR1 46/79 %, TAF15 9/16 %, TCF12 2/3 %, 1 unpartnered → **58/58 NR4A3-
   rearranged**); Agaram, *Hum Pathol* 2014 (**PMC4015728**, 26 cases: 16/7/1). *Confidence: high (3-0).*
2. **The fusion is a transcriptionally active oncoprotein (gain-of-function).** Filion et al., *J Pathol* 2009
   (**PMC4429309**): EWSR1/NR4A3 binds a response element in the **PPARG** promoter and transactivates it
   (band-shift + transfection); EMC tumours over-express PPARG + NDRG2 vs other sarcomas. Filion & Labelle,
   *Exp Cell Res* 2004: stable EWS/NOR-1 **transforms CFK2 chondrogenic cells** (soft-agar). *Confidence: high.*
   *Caveat: heterologous reporter + rat CFK2, not endogenous human EMC; gain-of-function, not addiction proof.*
3. **Quiet genome, clonal founding lesion.** Matched-trio WGS (**PMC11285543**): the EWSR1::NR4A3 t(9;22) is
   present in primary + both metastases (shared founding lesion); SV burden low/stable in primary (53) and lung
   met (46) but rises to 163 in the late pelvic met — "different drivers appear in advanced disease." EMC is
   **<3 % of soft-tissue sarcomas.** *Confidence: medium (N=1 trio; SVs counted, not functionally validated).*
4. **EMC sits in the FET-fusion-sarcoma addiction class.** A FET low-complexity domain (EWSR1/FUS/TAF15) fused
   to a TF is the defining, transcription-initiating driver across Ewing (EWS-FLI1), myxoid liposarcoma
   (FUS-DDIT3), clear-cell sarcoma (EWSR1-ATF1), DSRCT (EWSR1-WT1), EMC (EWSR1-NR4A3). Canonical member
   EWS-FLI1 is an enhancer-reprogramming pioneer factor at GGAA microsatellites (*Nat Cell Biol* 2022,
   s41556-022-01060-1). **DepMap (repo cache): FLI1 gene effect −0.93, 74 % of Ewing lines dependent (n=27)** —
   a strong selective fusion-dependency in the exemplar. *Confidence: high for the class/mechanism.*

**★ The decisive gap (honest floor).** **No direct loss-of-function experiment in any EMC cell line was found** —
every confirmed EMC functional result is *gain-of-function*. No RNAi/CRISPR/ASO knockdown of NR4A3 or the fusion
in a human EMC line (e.g. H-EMC-SS) with a growth/survival readout exists in the literature. So EMC's dependence
on the fusion is a **strong, multi-pillar prior, not a demonstrated dependency.** The **acute-degradation (dTAG)
experiment remains the make-or-break** (delegated to the EMC-program roadmap). Also un-reconfirmed by this pass:
the exact EWS-FLI1 DepMap number was taken from the repo cache, not independently re-verified here, and a Ewing
peptide-squelching "functional dependency" claim was **refuted (0-3)**.

## Hypothesis 1 — "NR4A3-selective degradation is tolerable via NR4A1/2 redundancy" (safety). VERDICT: partially supported, must NOT be overstated.
The broad "the paralogues do the same jobs so losing NR4A3 is fine" is **under-evidenced**. What survives:

- **The whole NR4A family is non-essential in dividing cells — now quantified for all three (2026-07-02
  direct DepMap query, `depmap_sarcoma_dependency.py`, n=1178 CRISPR lines).** NR4A3 mean gene effect
  **+0.023, 0/1178 lines dependent** (completely dispensable); NR4A1 **−0.115, 0.5 %** (6 lines); NR4A2
  **−0.05, 0.3 %** (4 lines). So proliferating cancer cells — tumour included — tolerate loss of any single
  NR4A, supporting a **proliferative-compartment therapeutic window**. *Caveat: no DepMap line is EMC; this is
  generic dispensability in dividing cells, not EMC-specific and not post-mitotic tissue.*
- **★ HONEST TENSION — human germline genetics says NR4A3 loss is *constrained*, not free (2026-07-02
  gnomAD LoF-constraint query).** NR4A3 is **LoF-intolerant** (pLI **0.9999**, LOEUF **0.37**; only **13**
  loss-of-function variants observed vs **55.6** expected), and NR4A2 is even more constrained (pLI **1.0**,
  LOEUF **0.094**); **only NR4A1 is LoF-tolerant** (pLI 0.002, LOEUF 0.71). This does **not** contradict the
  DepMap result — it means NR4A3's essentiality is **developmental / tissue-specific, not proliferative**. The
  correct reading: the glib "NR4A3 is dispensable, therefore degrading it is safe" is **not supported**;
  population constraint reflects germline/developmental fitness (many well-tolerated drug targets are
  LoF-constrained), so it neither proves nor refutes *adult transient-knockdown* tolerability — but it **flags
  a tissue/developmental context that needs NR4A3** as the on-target-toxicity risk to watch, and it makes
  **NR4A2-sparing doubly important** (most-constrained paralogue *and* CNS-enhanced; see HPA below).
- **★ Tissue co-expression is now MEASURED per tissue, not read off HPA's specificity LABEL
  (2026-08-03, roadmap row 26).** The per-tissue nTPM field this file previously had no access to
  (`rna_tissue_specific_nTPM: null` for all three genes) is filled from the HPA consensus table, and every
  count has one home in [`nr4a2-sparing-bound.json`](../modalities/nr4a2-sparing-bound.json) →
  `hpa.overlap.counts` — **not restated here.** Two things the numbers settle:
  1. **NR4A2 and NR4A3 co-express across almost every tissue measured**, so tissue distribution cannot
     separate target from anti-target: **the selectivity has to be molecular.** That is the operative fact
     for the degrader brief.
  2. ⛔ **There is no tissue in which NR4A2 is present while both paralogues are absent, and NR4A2 is
     nowhere the dominant family member.** So *"NR4A2 marks the tissue where paralogue compensation is
     least available"* is **not supported by this table**. ⚠ It is **not refuted** either, and the reason
     matters more than the count: a bulk tissue average dilutes the substantia nigra pars compacta to
     invisibility, so this measures **exposure breadth** and not the dopaminergic requirement
     (`hpa.overlap._the_specific_misreading_to_avoid`). HPA's *"Tissue enhanced"* label describes relative
     **enrichment, not restriction** — reading it as "NR4A2 is the CNS-confined paralogue" is a category
     error the per-tissue numbers settle directly.
  *(Superseded, retained: the label-based reading — see the appendix.)*
- **Demonstrated redundancy is myeloid-specific — and it IS the AML anti-target.** Mullican et al., *Nat Med*
  2007 (**PMID 17515897**): combined *Nr4a1⁻/⁻;Nr4a3⁻/⁻* mice die of AML in 3–4 weeks while **single nulls do
  not** — operational proof that single-gene NR4A3 loss is compensated by NR4A1 *in myeloid cells*. Blood 2018
  (**PMID 29343483**): NR4A1/NR4A3 "functionally redundant suppressors of AML"; a conditional double-KO is
  required to unmask HSC-homeostasis defects. **So this redundancy is exactly why NR4A1-sparing is mandatory
  (design away from the NR4A1+NR4A3 combination) — it is not a general safety guarantee.**
- **Shared DNA-binding grammar (mechanistic plausibility only).** The NR4A family binds NBRE (monomer) /
  NurRE (dimer) elements; NR4A2-DBD crystal structures on inverted/everted repeats at 2.6–2.8 Å
  (**PMC6926456**, PDB 6L6Q/6L6L). *Caveat: NR4A3 homodimerization on NurRE is weaker than NR4A1/2.*

- **★ RESOLVED 2026-08-03 — the mouse single-KO phenotypes exist, in MGI, with citations (roadmap row 26).**
  IMPC held no record for any of the three, and MGI was named here as the remaining source. It was read: the
  whole `MGI_PhenoGenoMP.rpt` corpus, with a genotype admitted as *single-gene* only when the free-text
  allelic-composition parse and the curated marker-accession column agree. Counts, terms, PubMed IDs and the
  verdict have one home in [`nr4a2-sparing-bound.json`](../modalities/nr4a2-sparing-bound.json) →
  `mgi.single_gene` / `headline_findings`; what changes **here** is which claims may now be stated:
  - ✅ **`Nr4a2` single-KO neonatal lethality is CONFIRMED and citable** — the MP term and its PubMed IDs are
    in the artifact. The **UNCONFIRMED flag this file carried is retired.** The supporting dopaminergic
    phenotype set (substantia nigra morphology, dopaminergic neuron number, dopamine level) is cited there too.
  - ⚠ **`Nr4a3`'s OWN single knockout carries lethality terms as well** — a fact about the **target**, not an
    anti-target, and one this program had no standardized in-vivo source for. It is **concordant with** the
    gnomAD reading directly above (NR4A3 LoF-constrained, pLI 0.9999) and gives the *"developmental /
    tissue-specific rather than proliferative"* interpretation a mouse phenotype instead of an inference.
  - ✅ **`Nr4a1` single-KO carries NO survival/viability term**, which is exactly what *"single nulls do not
    do it"* predicts, and the **`Nr4a1`+`Nr4a3` double-KO lethality is independently recoverable from MGI**
    with the same PMID this file already cites — so the hard half of the selectivity requirement now rests on
    two standardized sources rather than one pair of papers.
  - ⛔ **NONE of this is a safety result, and the limit is structural rather than a hedge.** A germline
    knockout bounds **developmental, complete, lifelong** loss of a gene; a degrader is **adult, transient
    and incomplete** loss of a protein, and no source read here measures that. What would close it is an
    adult conditional or inducible deletion with a survival readout, plus a CNS-exposure measurement for a
    real candidate molecule — the first is a wet-lab experiment and the second is a property of a molecule
    this program has not built. *(Sentence with one home:
    `verdict.caveat_that_must_travel_with_any_result`.)*

**★ What did NOT survive verification / still open (do NOT state as fact in the paper):**
- No numeric DBD %-identity (only the shared-element mechanism).
- No T-cell "all three NR4As needed" redundancy in this set.
- **Refuted (0-3):** "dual NR4A1/3 loss is not catastrophic to HSCs" — the double-KO **does** damage HSCs
  (loss of quiescence, oxidative stress, DNA damage). So even dual loss is not innocuous.

**Honest safety conclusion (updated 2026-07-02).** The tolerability case now rests on a *quantified* base:
(a) the whole NR4A family is **non-essential in dividing cells** (DepMap: NR4A3 0/1178 dependent), supporting a
proliferative-compartment window; (b) *myeloid-compartment* NR4A1↔NR4A3 compensation (which doubles as the
NR4A1-sparing rationale); (c) broad NR4A1/NR4A3 tissue co-expression (HPA) making paralogue buffering plausible
outside the CNS. **But two honest brakes must be stated:** NR4A3 is **germline LoF-constrained** in humans
(gnomAD pLI ~1) — so complete developmental loss is selected against and "dispensable ⇒ safe" is **not** a
valid inference; and **NR4A2-sparing selectivity is a safety requirement, not just an efficacy nicety.**
Pan-tissue **adult**-knockdown tolerability remains an **assumption**, and nothing read to date measures it.

★ **Updated 2026-08-03 (row 26), and the update cuts both ways.** The single-KO mouse phenotypes are **no
longer unverified**: MGI carries them for all three genes, with citations, and the Nurr1 neonatal-lethality
claim is confirmed — see the resolved bullet above. Two consequences for this paragraph, neither of them
comfortable: **(a)** the *germline* brake now applies to **NR4A3 itself** and not only to human constraint
data, because its own single knockout carries lethality terms; and **(b)** the *"CNS exception"* clause that
used to sit here was a reading of an HPA **label**, and the per-tissue numbers do not support it — the
measured exception is that NR4A2 and NR4A3 co-express nearly everywhere, so the residual risk is **not**
specifically located in the CNS by this evidence. It is located in **development**, and in the fact that a
degrader's adult, transient, incomplete loss is a regime **no source read here measures**.
*(Superseded, retained: "the CNS/NR4A2 exception is real … residual risk is now specifically located
(developmental / CNS)" and "the single-KO mouse phenotypes are still unverified (IMPC empty; MGI pending)" —
appendix below.)*

## Open follow-ups (would upgrade both hypotheses; all are database queries, no wet lab)
1. ✅ **DONE (2026-07-02).** Direct DepMap query for NR4A1/2/3 gene-effect (NR4A3 +0.023 0/1178; NR4A1 −0.115;
   NR4A2 −0.05) + gnomAD LoF constraint (NR4A3 pLI 0.9999; NR4A2 1.0; NR4A1 tolerant) + HPA co-expression.
   `depmap_sarcoma_dependency.py` (`nr4a_paralogue_comparison`) + `nr4a_safety_genetics.py`.
2. ✅ **DONE (2026-08-03, roadmap row 26).** MGI single-KO phenotypes for Nr4a1/Nr4a2/Nr4a3, plus the
   double-KO genotypes, read out of the public reports with a PubMed ID on every annotation.
   `nr4a2_sparing_bound.py` → [`nr4a2-sparing-bound.json`](../modalities/nr4a2-sparing-bound.json).
   The Nurr1 question is **resolved**; see the resolved bullet in H1 above.
3. ✅ **DONE (2026-08-03, same run).** HPA **per-tissue nTPM** for all three, so co-expression is arithmetic
   rather than a specificity label → `hpa.overlap` in the same artifact.
4. The one that needs a lab: **acute NR4A3/fusion degradation (dTAG) in an EMC model** — the decisive
   efficacy experiment, and the reason the program is written to be *picked up* by a wet-lab collaborator.
5. ⭑ **The one row 26 identified and could NOT close at $0:** an **adult conditional or inducible** *Nr4a2*
   deletion with a survival/behaviour readout. Every mouse phenotype above is germline, and the gap between
   germline loss and adult degradation is the whole distance between this evidence base and a tolerability
   claim. Also needed and equally absent: a CNS-exposure datum for a real candidate molecule — this repo
   holds no measured or predicted CNS-penetration value for any NR4A candidate.

---

## Appendix — superseded readings (retained, because the old wording stays quotable)

Per CLAUDE.md rule 1: a corrected statement is never silently dropped, and the narrative never stays inline.

| date | superseded reading | what replaced it |
|---|---|---|
| 2026-08-03 | *"the assumption that **Nr4a2/Nurr1 single-KO is neonatal-lethal** … remains **UNCONFIRMED** here"* and *"the single-KO mouse phenotypes are **still unverified** (IMPC empty; MGI pending)"* | MGI carries the phenotypes for all three genes with PubMed IDs; the Nurr1 neonatal-lethality claim is confirmed. One home: [`nr4a2-sparing-bound.json`](../modalities/nr4a2-sparing-bound.json) → `mgi.single_gene` |
| 2026-08-03 | *"NR4A2 is **'tissue enhanced'** … i.e. the tissue where paralogue compensation is **least** available. This is the structural reason the CNS is the safety watch-zone"* | a **label** is not a distribution. Per-tissue nTPM shows NR4A2 above the detection cut in every tissue measured, unbuffered in none, and dominant in none. The CNS localisation of the residual risk is **not** supported by this table — and is not refuted by it either, because a bulk average dilutes the substantia nigra. `hpa.overlap` |
| 2026-08-03 | *"its residual risk is now **specifically located** (developmental / CNS)"* | developmental, yes; CNS, not by this evidence |
