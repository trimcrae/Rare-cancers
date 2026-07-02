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
- **Tissue co-expression (2026-07-02 Human Protein Atlas query).** NR4A1 ("low tissue specificity, detected
  in all") and NR4A3 ("low tissue specificity, detected in many") are **broadly co-expressed** — paralogue
  buffering is plausible across most tissues — whereas NR4A2 is **"tissue enhanced"** (its known CNS/
  dopaminergic bias), i.e. the tissue where paralogue compensation is **least** available. This is the
  structural reason the CNS is the safety watch-zone for any NR4A degrader that is not cleanly NR4A2-sparing.
- **Demonstrated redundancy is myeloid-specific — and it IS the AML anti-target.** Mullican et al., *Nat Med*
  2007 (**PMID 17515897**): combined *Nr4a1⁻/⁻;Nr4a3⁻/⁻* mice die of AML in 3–4 weeks while **single nulls do
  not** — operational proof that single-gene NR4A3 loss is compensated by NR4A1 *in myeloid cells*. Blood 2018
  (**PMID 29343483**): NR4A1/NR4A3 "functionally redundant suppressors of AML"; a conditional double-KO is
  required to unmask HSC-homeostasis defects. **So this redundancy is exactly why NR4A1-sparing is mandatory
  (design away from the NR4A1+NR4A3 combination) — it is not a general safety guarantee.**
- **Shared DNA-binding grammar (mechanistic plausibility only).** The NR4A family binds NBRE (monomer) /
  NurRE (dimer) elements; NR4A2-DBD crystal structures on inverted/everted repeats at 2.6–2.8 Å
  (**PMC6926456**, PDB 6L6Q/6L6L). *Caveat: NR4A3 homodimerization on NurRE is weaker than NR4A1/2.*

**★ What did NOT survive verification / still open (do NOT state as fact in the paper):**
- **IMPC single-KO phenotypes returned NO record** for Nr4a1/Nr4a2/Nr4a3 (2026-07-02 query) — these KO lines
  are not phenotyped in IMPC (or the marker query did not resolve). So the individual **mouse single-KO
  viability** question is **still unresolved by a standardized source**; in particular the assumption that
  **Nr4a2/Nurr1 single-KO is neonatal-lethal (dopaminergic-neuron loss) remains UNCONFIRMED here** — it rests
  on primary literature not re-verified in this pass. gnomAD's strong NR4A2 constraint (pLI 1.0) is *consistent
  with* an essential Nurr1 role but is not the mouse phenotype itself. (MGI is the remaining follow-up.)
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
valid inference; and the **CNS/NR4A2 exception is real** (NR4A2 is the most-constrained, most tissue-enhanced
paralogue), making **NR4A2-sparing selectivity a safety requirement, not just an efficacy nicety**. Pan-tissue
adult-knockdown tolerability remains an **assumption**, and the single-KO mouse phenotypes are **still
unverified** (IMPC empty; MGI pending). Net: the safety argument is **materially stronger and more honest** than
the pre-2026-07-02 hand-wave, and its residual risk is now **specifically located** (developmental / CNS), not vague.

## Open follow-ups (would upgrade both hypotheses; all are database queries, no wet lab)
1. ✅ **DONE (2026-07-02).** Direct DepMap query for NR4A1/2/3 gene-effect (NR4A3 +0.023 0/1178; NR4A1 −0.115;
   NR4A2 −0.05) + gnomAD LoF constraint (NR4A3 pLI 0.9999; NR4A2 1.0; NR4A1 tolerant) + HPA co-expression.
   `depmap_sarcoma_dependency.py` (`nr4a_paralogue_comparison`) + `nr4a_safety_genetics.py`.
2. **MGI single-KO phenotypes** for Nr4a1/Nr4a2/Nr4a3 (**IMPC returned no phenotyped KO** for any of the three
   on 2026-07-02 — MGI is the remaining source to bound CNS tolerability / resolve the Nurr1 question).
3. **GTEx/HPA co-expression** of NR4A1/2/3 (map where compensation is / isn't available).
4. The one that needs a lab: **acute NR4A3/fusion degradation (dTAG) in an EMC model** — the decisive
   efficacy experiment, and the reason the program is written to be *picked up* by a wet-lab collaborator.
