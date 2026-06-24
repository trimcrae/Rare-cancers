# A prioritized, falsifiable roadmap to a treatment for EWSR1::NR4A3 extraskeletal myxoid chondrosarcoma — a computation-only triage

*Draft manuscript (2026-06). Authors/affiliations TBD. This is the repo's #1 deliverable — the
publish-to-convince artifact. Built entirely from the tracker (`emc-treatment-strategy.md`) and the
in-silico results in `research/modalities/`. Every claim is sourced or computed; nothing is wet-lab
validated, and the paper says so throughout.*

## Abstract
Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare sarcoma defined by an EWSR1::NR4A3 (or
TAF15::NR4A3) fusion that produces an aberrant, undruggable transcription factor. It has no approved
targeted therapy, almost no laboratory models, and no commercial pull. We argue that for such a
disease the rate-limiter is not ideas but **prioritization and evidence**, and we provide both from
**computation alone** (no wet lab). We assess every plausible treatment route against likelihood of
patient benefit × near-term feasibility, generate new supporting evidence by mining public data
(AlphaFold/fpocket structure; DepMap dependency, fusion-addiction proxy, and target expression with
sarcoma lines as an EMC surrogate; HLA population coverage), and attach an explicit decisive
experiment and kill-criterion to each candidate. The result is a ranked portfolio: near-term
repurposing of approved drugs (anti-angiogenic-TKI + checkpoint inhibitor; trabectedin;
carfilzomib + anthracycline) carries the best near-term odds; a **NR4A3 degrader** is the most
compelling driver-directed bet, with its central "fusion-addiction" premise supported here by
analogy (FLI1 dependency in Ewing sarcoma, gene effect −0.93, 74% of lines dependent); **B7-H3** and
**PRAME** emerge as the strongest surface/antigen targets (expressed in 99% and 53% of sarcoma lines
respectively), while NY-ESO-1/MAGE-A4-directed cell therapy and a fusion-junction vaccine are
down-weighted with data. We frame each candidate as a testable hypothesis for groups with models or
patients, and define the in-silico experiments we can run ourselves to advance the degrader.

## 1. Background
EMC is defined by rearrangement of *NR4A3*, most often fused to *EWSR1*. The chimeric protein is an
orphan-nuclear-receptor transcription factor: structurally it is an intrinsically disordered
FET-derived transactivation domain welded to the ordered NR4A3 DNA-binding and ligand-binding
domains. Conventional occupancy pharmacology is precluded — AlphaFold2 (AlphaFold DB) + fpocket find
the transactivation domains disordered and the single best cavity (in the NR4A3 ligand-binding
domain) only borderline druggable (fpocket druggability 0.495, sub-threshold). EMC is also a
low-mutational-burden "cold" tumour, ultra-rare (a few hundred cases/year globally), and essentially
absent from public functional-genomics resources (the only models are newly derived patient lines,
e.g. NCC-EMC1-C1, USZ-EMC). It has, in effect, no champion. Personalized and fusion-directed
therapies are advancing in other sarcomas, but EMC must free-ride on that infrastructure rather than
fund its own. Our contribution is a disciplined, reproducible triage that says **where** to push and
**what evidence already exists**, and generates new computational evidence where it can.

## 2. Methods (reproducible, no wet lab)
All analyses are scripted (`research/modalities/`) and run on public data:
- **Structure/druggability:** AlphaFold2 models (AFDB) + per-residue pLDDT (disorder) + fpocket.
- **Immunogenicity/coverage:** MHCflurry/MHCnuggets junction-neoantigen prediction; Allele Frequency
  Net Database for HLA population coverage (Wilson CIs).
- **DepMap surrogate mining (EMC has no line):** CRISPR (Chronos) gene effect for selective
  essentiality and a **fusion-addiction proxy** (dependency of the fusion partner in its driver
  context); OmicsExpression for candidate-target expression — across sarcoma lineages vs. all others,
  with per-subtype breakdowns. Pipelines self-validate on known dependencies / housekeeping genes.
- **Literature triage** for clinical signal, with sources tracked.
Limitations of each method are stated in §6; the headline caveat is that nothing here is
experimentally validated in EMC.

## 3. Results — the prioritized portfolio
**Tier 1 — actionable now (approved drugs, EMC evidence).**
- **Anti-angiogenic TKI + checkpoint inhibitor.** The ImmunoSarc trial (sunitinib + nivolumab)
  reported a partial response in an EMC patient; EMC is unusually TKI-sensitive, and TKIs remodel the
  cold tumour microenvironment — a mechanistic synergy, not coincidence.
- **Trabectedin.** Approved for soft-tissue sarcoma; its mechanism is displacing fusion
  transcription factors from target promoters (validated in myxoid liposarcoma), mechanistically
  apt for EMC's fusion-TF biology; an impressive EMC responder is reported (trabectedin +
  radiotherapy, metastatic EMC).
- **Carfilzomib + anthracycline (± venetoclax).** The only drug active across two patient-derived
  EMC models in an unbiased ex-vivo screen (Bangerter 2023) — the best *experimental* EMC evidence
  here; play it on the existing anthracycline backbone.
*These are repurposing of approved drugs, not novel modalities — the honest near-term answer.*

**Tier 2 — driver-directed, high-ceiling: the NR4A3 degrader.**
The fusion retains the ordered NR4A3 ligand-binding domain, so a degrader can remove the oncoprotein
without needing the collapsed functional pocket. Degradation is mechanistically ideal: NOR-1 is
constitutively active and its output scales with **expression level** (Munck 2022), so lowering
protein lowers oncogenic activity. The family is degradable (an NR4A1 PROTAC works, though it does
not cross-degrade NR4A3 — so NR4A3 needs its own warhead), NR4A3-selective ligand starting points
exist (inverse NOR-1 agonists), and the first FDA-approved PROTAC (vepdegestrant, 2025) degrades a
nuclear receptor. **New evidence:** the route's make-or-break premise — that EMC is *addicted* to its
fusion — is supported by analogy in DepMap: in Ewing sarcoma, where the homologous EWS-FLI1 is the
driver, **FLI1 has gene effect −0.93 and 74% of lines are dependent**.

**Tier 3 — surface/antigen modalities (surrogate-supported).**
- **B7-H3 (CD276):** expressed in **99% of sarcoma lines, high across every subtype including
  myxoid** (DepMap; on top of 97% pan-STS by IHC) → the antibody-drug conjugate ifinatamab
  deruxtecan, a B7H3×CD3 bispecific, or B7-H3 CAR-T.
- **PRAME:** the best cancer-testis antigen — **53% of sarcoma lines, high in myxoid (7.6) and
  synovial (7.2)** → the PRAME ImmTAC brenetafusp (tumour-agnostic basket) or PRAME-directed
  cell therapy.
- **FAP-targeted radioligand therapy:** EMC's myxoid stroma is a strong candidate; the tracer is
  also diagnostic.

**Tier 4 — down-weighted with data/logic.**
- **TCR-T / ImmTAC against NY-ESO-1 or MAGE-A4:** EMC is CTA-low (NY-ESO-1 5%, MAGE-A4 7% of sarcoma
  lines; NY-ESO-1 is used to distinguish myxoid liposarcoma *from* EMC) → the afami-cel/letetresgene
  port is weak; only a PRAME⁺ subset (above) is attractive.
- **Synthetic-lethal / BRD9–ncBAF:** a transfer prior from EWS-FLI1's prion-domain BAF retargeting,
  but DepMap shows BRD9/ncBAF is **not** selectively essential in sarcoma — not even in Ewing — and
  BET/CDK targets show no selectivity window. No shortcut; a de-novo EMC CRISPR screen would be
  required.
- **Fusion-junction vaccine:** the junction is largely self-sequence in a cold tumour (weak
  immunogen), and the economics favour a tumour-agnostic platform; the HLA-coverage analysis is
  retained only as input to TCR-T/ADC eligibility.

## 4. What would prove or kill each candidate (the falsifiable core)
The value of this paper to a reader is the decisive next experiment and the kill-criterion per route.

| Candidate | Decisive experiment | Kill-criterion |
|---|---|---|
| TKI + ICI; trabectedin; carfilzomib+anthracycline | prospective EMC cohort / case series | fails to reproduce in EMC patients |
| NR4A3 degrader | dTAG acute-degradation viability in EMC lines | degrading the fusion doesn't kill EMC cells |
| B7-H3 ADC / CAR-T; FAP-RLT | EMC tissue IHC / FAP-PET, then the agent | EMC is target-negative |
| PRAME ImmTAC/CAR | EMC PRAME IHC; brenetafusp basket enrolment | primary EMC PRAME-negative |
| Synthetic-lethal/BRD9 | genome-wide CRISPR screen in EMC lines | (already down-weighted by DepMap) |

## 5. An in-silico program others can extend (and what we are running)
Because we attack the actual driver only computationally, we define a runnable program for the
degrader: (i) **molecular dynamics of the NR4A3 LBD** to test whether a transient/cryptic druggable
pocket opens that the static AlphaFold model misses — a positive result would overturn the
"undruggable" prior; (ii) **de-novo selective warhead/binder design** (structure-based generative
small-molecule design; or RFdiffusion→ProteinMPNN→AF2 for a binder), scored for selectivity against
the homologous NR4A1/NR4A2; (iii) public-data expression mining to substitute for unavailable EMC
IHC. Scripts and a cloud-GPU pipeline are provided; the MD is the highest-value single experiment.

## 6. Limitations
Nothing here is experimentally validated in EMC. DepMap analyses use sarcoma lines as a **surrogate**
(no EMC line exists); cell lines silence cancer-testis antigens (CTA reads are lower bounds) and
under-represent stromal FAP; AlphaFold yields a single static model (cryptic pockets unseen);
predicted MHC binding and docking scores are screens, not proof; the fusion-addiction result is an
**analogy** (FLI1/Ewing), not EMC data — and an imperfect one, since EWS-FLI1 and EWSR1::NR4A3 share
only the EWSR1 moiety while their DNA-binding partners (an ETS factor vs. a nuclear receptor) differ,
so it supports FET-fusion addiction as a *class* property rather than proving NR4A3-fusion
dependence; and HLA/expression statistics are population priors, not the individual patient. These are stated so the work is read as hypothesis-prioritization and
evidence-synthesis, not as demonstrated efficacy.

## 7. Why pursue an ultra-rare cancer — and how to make a candidate worth developing
The hardest objection to any EMC drug program is not scientific but economic: EMC is too rare to
generate commercial or translational pull on its own, so even a well-evidenced candidate risks
never being made. We propose two mitigations that should be built into how any lead is advanced.
First, **EMC's clean, single-driver biology makes it an unusually good proof-of-concept indication**
for a mechanism that is hard to validate in messier, multi-driver common tumours — the fusion is
truncal and near-universal, so an effect is causally interpretable. Second, and more importantly,
**every lead here has a plausible path to common cancers**, which should be assessed and presented
alongside the EMC case to widen the addressable population and the incentive to develop it:
- the **NR4A3 degrader** generalises along two axes — the NR4A receptor family (NR4A1/2/3) is
  implicated across leukaemia, melanoma, prostate, breast and colorectal cancer, and the underlying
  *platform* (degrading an "undruggable" nuclear-receptor transcription factor via its retained LBD)
  is itself transferable;
- **B7-H3, PRAME and FAP are already pan-cancer targets** (B7-H3 ADCs in lung/prostate; PRAME in
  melanoma/lung/ovarian/uterine; FAP across carcinomas), so EMC is best framed as one indication
  within a broader program rather than a standalone orphan bet;
- the **repurposed agents** (trabectedin, carfilzomib, TKI+ICI) already carry other-cancer evidence.

This is cheap to substantiate in silico with the same public-data pipelines used here (they cover
all lineages, not just sarcoma). The recommendation is therefore that any candidate which firms up
be accompanied by a **broader-indication analysis** — positioning EMC as the entry point, not the
endpoint.

## 8. Conclusion
A computation-only program can do for an orphan cancer what it most lacks: rank the routes, surface
the existing evidence, generate new supporting evidence, and hand testable, de-risked hypotheses to
those who can act. For EMC, the near-term path is smart repurposing (TKI+ICI, trabectedin,
carfilzomib+anthracycline); the most novel driver-directed bet is a NR4A3 degrader, whose central
premise we support by analogy and whose warhead is a tractable in-silico design problem; and B7-H3
and PRAME are the strongest surface/antigen targets. We invite groups with EMC models or patients to
run the decisive experiments named above.

## References (verified in the underlying analyses; collate to journal format)
NR4A3/EMC biology and EWSR1::NR4A3 → PPARG (PMC4429309); EMC neuroendocrine phenotype / INSM1
(Mod Pathol 2017; PMID 36563884); patient-derived EMC line NCC-EMC1-C1 (Human Cell 2025).
Structure: AlphaFold2 (Jumper 2021) / AFDB; fpocket. Degrader: NOR-1 druggability & inverse agonists
(Munck 2022, PMC9542104); NR4A ligands (PMC11267491); vepdegestrant first approved PROTAC (Arvinas
2025). Synthetic-lethal: Boulay *Cell* 2017 (EWSR1 prion-domain BAF retargeting); Brien *eLife* 2018
(BRD9 degrader). Immunotherapy: afami-cel (Tecelra) approval 2024; NY-ESO-1 in sarcoma (PMC3518519);
ImmunoSarc / sarcoma IO (ASCO EDBK 2024); brenetafusp PRAME ImmTAC (Immunocore 2024).
EMC-specific clinical signal: sunitinib response in EMC (PMC3534218); trabectedin + radiotherapy
long-term response in metastatic EMC (case report, *Impressive response and long-term survival…*). Surface targets:
B7-H3 in soft-tissue sarcoma (PMC11523878); FAPI radioligand therapy in sarcoma (Clin Cancer Res
2022). Repurposing/ex-vivo: carfilzomib (top ex-vivo hit) ± anthracycline/venetoclax in two
patient-derived EMC models (Bangerter et al., *Human Cell* 2023; PMID 36316541;
`repurposing-hypotheses.md`). Data: DepMap 24Q4 (CRISPR + OmicsExpression); AFND (HLA).
*(Full citations live in the per-route memos; verify-refs before submission.)*
