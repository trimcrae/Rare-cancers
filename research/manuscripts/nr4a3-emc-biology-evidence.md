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

- **NR4A3 is broadly non-essential in cancer cell lines.** DepMap (repo cache): NR4A3 gene effect **0.02**
  (non-dependent). *Caveat: no DepMap line is EMC, so this speaks to generic dispensability, not EMC.* (NR4A1
  and NR4A2 essentiality were **not** in the cache and were **not** web-verifiable — a direct DepMap query is
  the follow-up to complete the paralogue comparison.)
- **Demonstrated redundancy is myeloid-specific — and it IS the AML anti-target.** Mullican et al., *Nat Med*
  2007 (**PMID 17515897**): combined *Nr4a1⁻/⁻;Nr4a3⁻/⁻* mice die of AML in 3–4 weeks while **single nulls do
  not** — operational proof that single-gene NR4A3 loss is compensated by NR4A1 *in myeloid cells*. Blood 2018
  (**PMID 29343483**): NR4A1/NR4A3 "functionally redundant suppressors of AML"; a conditional double-KO is
  required to unmask HSC-homeostasis defects. **So this redundancy is exactly why NR4A1-sparing is mandatory
  (design away from the NR4A1+NR4A3 combination) — it is not a general safety guarantee.**
- **Shared DNA-binding grammar (mechanistic plausibility only).** The NR4A family binds NBRE (monomer) /
  NurRE (dimer) elements; NR4A2-DBD crystal structures on inverted/everted repeats at 2.6–2.8 Å
  (**PMC6926456**, PDB 6L6Q/6L6L). *Caveat: NR4A3 homodimerization on NurRE is weaker than NR4A1/2.*

**★ What did NOT survive verification (do NOT state as fact in the paper):**
- No DepMap/Achilles gene-effect comparison for NR4A1 vs NR4A2 vs NR4A3 (only NR4A3=0.02 from the repo cache).
- No verified individual **mouse single-KO phenotypes** for Nr4a1/Nr4a2/Nr4a3 — in particular the assumption
  that **Nr4a2/Nurr1 single-KO is neonatal-lethal via dopaminergic-neuron loss was NOT confirmed** here, so
  **CNS tolerability of selective NR4A3 loss is UNRESOLVED**, not "handled."
- No GTEx/HPA tissue co-expression map (the "where can paralogues compensate" question).
- No numeric DBD %-identity (only the shared-element mechanism).
- No T-cell "all three NR4As needed" redundancy in this set.
- **Refuted (0-3):** "dual NR4A1/3 loss is not catastrophic to HSCs" — the double-KO **does** damage HSCs
  (loss of quiescence, oxidative stress, DNA damage). So even dual loss is not innocuous.

**Honest safety conclusion.** The tolerability case rests on (a) NR4A3's broad dispensability in cancer lines,
(b) *myeloid-compartment* NR4A1↔NR4A3 compensation (which doubles as the NR4A1-sparing rationale), and (c)
shared-grammar plausibility — **not** on a quantified pan-tissue tolerability. Broad tolerability and the
CNS/NR4A2 exception are **assumptions**, not established facts, and must be stated as such. The rigorous
completion is a **targeted database follow-up** (DepMap NR4A1/2 essentiality; MGI/IMPC single-KO phenotypes;
GTEx/HPA co-expression) — web search could not verify these; they need direct DB access, not literature mining.

## Open follow-ups (would upgrade both hypotheses; all are database queries, no wet lab)
1. **Direct DepMap query** for NR4A1 + NR4A2 gene-effect (complete the paralogue-essentiality comparison; the
   repo `depmap_sarcoma_dependency.py` already pulls Chronos — extend it to NR4A1/2).
2. **MGI/IMPC single-KO phenotypes** for Nr4a1/Nr4a2/Nr4a3 (bound CNS tolerability; resolve the Nurr1 question).
3. **GTEx/HPA co-expression** of NR4A1/2/3 (map where compensation is / isn't available).
4. The one that needs a lab: **acute NR4A3/fusion degradation (dTAG) in an EMC model** — the decisive
   efficacy experiment, and the reason the program is written to be *picked up* by a wet-lab collaborator.
