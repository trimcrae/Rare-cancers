# A prioritized, falsifiable roadmap to a treatment for EWSR1::NR4A3 extraskeletal myxoid chondrosarcoma — a computation-only triage

> **ACTIVE MANUSCRIPT — the repo's one paper currently being developed.** This is the single
> publish-to-convince deliverable; everything else in this folder feeds it, records QA for it, or is
> parked/separate-track. Strategy/source-of-truth: [`emc-treatment-strategy.md`](./emc-treatment-strategy.md).
> Folder map: [`README.md`](./README.md).

*Draft manuscript (2026-06). Authors/affiliations TBD. This is the repo's #1 deliverable — the
publish-to-convince artifact. Built entirely from the tracker (`emc-treatment-strategy.md`) and the
in-silico results in `research/modalities/`. Every claim is sourced or computed; nothing is wet-lab
validated, and the paper says so throughout.*

> **Living document.** This roadmap is maintained continuously in git and is intended to move faster
> than the peer-review cycle (rationale + dissemination tiers: `emc-treatment-strategy.md` → Q4). The
> peer-reviewed version covers the stable core (kill-criteria framework, methodology); the **current
> route prioritization lives here and in the latest tagged release/DOI.** Material changes are logged
> below; the `method-watch` digest is the automated input that drives them.
>
> **Changelog**
> - *2026-06-24* — Added the junction **ASO/siRNA** route (driver-directed, to-build) + its in-silico evaluation arm and
>   first result (0/5 gapmers transcriptome-clean → specificity bar to clear); added the **delivery
>   strategy** (B7-H3 AOC/siRNA). Degrader **ternary-complex** modelling re-primed (open AF3-class
>   tools shipped) and pipeline built. Recorded a degrader-modality precedent in Ewing sarcoma
>   (YSA64, RBM39 — *to verify*).
> - *2026-06* — Initial ranked portfolio (repurposing / degrader / surface-antigen / down-weighted).

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

**Two axes, not one tier number.** A single ranked "tier" is misleading here, because a tier number
blends two independent questions that do not move together: **(A) near-term readiness** — how close a
route is to helping a real EMC patient (approved and available, with EMC evidence, vs. still to be
discovered, built, or validated) — and **(B) impact ceiling & driver-directedness** — how high the
potential benefit is and how directly it attacks the actual EWSR1::NR4A3 driver (EMC-specific vs. a
generic borrowed drug). They pull apart: the repurposed approved drugs are the most *ready* but
generic and modest-ceiling; the NR4A3 degrader is the highest-ceiling, EMC-specific bet but the
furthest from a patient. We therefore score every route on **both** axes rather than forcing one rank —
a clinician seeking the next option weights Axis A; a developer or scientist choosing where the field
should invest weights Axis B.

| Route | **Axis A — near-term readiness** | **Axis B — impact ceiling & driver-directedness** |
|---|---|---|
| Anti-angiogenic TKI + checkpoint inhibitor | **Now** — approved; real EMC responder | Moderate — generic IO + anti-angiogenic; partial responses, not driver-directed |
| Trabectedin (± RT / combo) | **Now** — approved; reported EMC responder | Moderate–high — its MoA *is* fusion-TF displacement (mechanism-fit), but empirical in EMC |
| Carfilzomib + anthracycline (± venetoclax) | **Now** — approved; best *ex-vivo* EMC evidence | Moderate — empirical screen hit, not driver-directed |
| B7-H3 (CD276) ADC / bispecific | **Confirm-gated** — needs EMC B7-H3 IHC | High — EMC-directed surface target; ADC is the fastest high-ceiling route |
| PRAME ImmTAC / cell therapy | **Confirm-gated** — needs EMC PRAME IHC | High — antigen-directed; basket access via brenetafusp |
| FAP radioligand therapy | **Confirm-gated** — needs EMC FAP-PET | High — stroma-directed; theranostic (tracer = diagnostic) |
| **NR4A3 degrader (PROTAC)** | **To build** — no selective warhead yet; no EMC validation | **Highest — directly removes the EWSR1::NR4A3 driver; EMC-specific. The program's flagship bet.** |
| **Fusion-junction ASO / siRNA** | **To build** — tumour delivery unsolved | **Highest — the only *truly fusion-specific* route (silences the fusion alone)** |
| B7-H3 / CD56 CAR-T | **To build** — harder than the ADC | High — EMC-directed, higher ceiling than the ADC; ADC/RLT reach a patient first |
| PPARG modulation (TZDs) | **To build** — agonist-vs-antagonist direction unresolved | Low–moderate — druggable *downstream* node, not the driver |
| TCR-T / ImmTAC (cancer-testis antigen) | **Down-weighted** — EMC is CTA-low | Low for EMC — antigen mostly absent; only a small PRAME⁺/A\*02⁺ subset |
| Synthetic-lethal / BRD9 | **Down-weighted** — DepMap transfer prior negative | Low — no selectivity window |
| Fusion-junction vaccine / HLA-coverage | **Parked** | Low — weak immunogen in a cold tumour |

![EMC treatment routes plotted on two axes: near-term readiness (x) against impact ceiling and driver-directedness (y). Repurposed approved drugs are ready but modest-ceiling; the NR4A3 degrader and junction ASO are the highest-ceiling, EMC-specific flagship but not near-term; surface/antigen routes sit between. The top-right — ready and high-ceiling — is empty.](figures/portfolio-quadrant.png)

**Figure 2. The prioritized portfolio on both axes.** Graphical form of the table above — keep the two
in sync; regenerate via `figures/portfolio_quadrant.py` (matplotlib). That no route occupies the
top-right (ready *and* highest-ceiling) is the structural problem this roadmap navigates.

*The routes below are presented narrative-first — near-term repurposing, then the flagship
driver-directed bet, then surface/antigen, then down-weighted — for readability. **That order is not
a combined rank;** read both axes off the table above.*

**Ready now — approved drugs with EMC evidence** *(Axis A: available now · Axis B: moderate, generic).*
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

**Highest-ceiling, driver-directed — the NR4A3 degrader (the flagship)** *(Axis A: to build · Axis B: highest, EMC-specific).*
The fusion retains the ordered NR4A3 ligand-binding domain, so a degrader can remove the oncoprotein
without needing the collapsed functional pocket. Degradation is mechanistically ideal: NOR-1 is
constitutively active and its output scales with **expression level** (Munck 2022), so lowering
protein lowers oncogenic activity. The family is degradable (an NR4A1 PROTAC works, though it does
not cross-degrade NR4A3 — so NR4A3 needs its own warhead), NR4A3-selective ligand starting points
exist (inverse NOR-1 agonists), and the first FDA-approved PROTAC (vepdegestrant, 2025) degrades a
nuclear receptor. **New evidence:** the route's make-or-break premise — that EMC is *addicted* to its
fusion — is supported by analogy in DepMap: in Ewing sarcoma, where the homologous EWS-FLI1 is the
driver, **FLI1 has gene effect −0.93 and 74% of lines are dependent**. *Selectivity/safety:* a
LBD warhead also degrades wild-type NR4A3 and could hit the paralogues NR4A1/NR4A2 — whose loss
carries known liabilities (Nurr1/dopamine-neuron toxicity; NR4A1+NR4A3 double-loss → leukaemia in
mice) — so the design target is **NR4A3-selective, NR4A1/2-sparing** (7 divergent pocket residues
identified; `nr4a-selectivity.json`).

**Also driver-directed, but transcript-level and uniquely fusion-specific: a junction ASO.** The
fusion *mRNA* junction exists in no normal transcript, so an antisense oligonucleotide (or siRNA)
spanning it silences **only** the fusion — sparing wild-type NR4A3 *and* EWSR1. This is the one
truly tumour-specific route (the protein degrader cannot be, since the druggable LBD is shared);
5 fusion-specific gapmers are designed (`junction_aso.py`). It is lower on near-term feasibility,
not lower in principle: the EMC junction is **GC-rich (~75–81%)**, outside the usual comfort zone,
and **tumour delivery is the unsolved problem** for oligonucleotides generally. Degrader and ASO are
**complementary** — potent-but-not-fusion-specific vs. fusion-specific-but-delivery-limited.

The ASO route also has its own **in-silico evaluation arm** that advances it without a wet lab
(`aso_insilico.py`), since its open questions are sequence/RNA problems, not structure problems:
(i) a **transcriptome-wide off-target screen** — every candidate's target window is scanned against
the whole human RefSeq transcriptome (GRCh38) for exact and ≤1-mismatch matches (seed-and-extend),
because hybridization-dependent off-target RNase-H cleavage is the dominant gapmer-toxicity mode and
"not a perfect complement of the two parents" is too weak a specificity bar; (ii) **target-site
accessibility**, folding the fusion mRNA (ViennaRNA partition function) to rank candidates by the
single-stranded probability of their RNase-H site (potency); (iii) **sequence-liability filters**
(CpG/TLR9 immunostimulation, G-quadruplex, homopolymer runs); and (iv) an **siRNA seed-region
off-target** module — because the same junction is targetable by RISC, and RNAi off-targeting is
driven by guide **seed** (g2–g8) complementarity, we report each candidate's seed 7-mer, whether the
seed *straddles the junction* (a fusion-unique seed, the design goal), and its transcriptome
occurrence count. The result is a ranked, off-target-screened shortlist across **both** chemistries
(gapmer and siRNA) rather than an untriaged design list. This advances *specificity and potency-site
selection only* — it does **not** address delivery, which remains the route's gating problem.

*Result (first pass).* Screening the 5 fusion-specific gapmers against the full human RefSeq
transcriptome (186,185 transcripts) returns a deliberately uncomfortable finding: **none is
transcriptome-clean** — every candidate has at least one near-complementary off-target at ≤1
mismatch (best candidate: 0 exact but 8 one-mismatch hits), the junction sites are **poorly
accessible** (best ≈0.35 unpaired probability), they are **GC-rich (~75%)**, and only **2 of 5**
place the RISC seed across the junction. This is the screen doing its job: "not a perfect complement
of the two parents" passes all 5, but the stricter transcriptome-wide bar fails all 5. The actionable
read is that a viable oligo here will need **wider design latitude than the canonical 16-mer at the
canonical breakpoint** — longer/shifted gapmers or a junction-in-seed siRNA — pushed until the
≤1-mismatch off-target count reaches zero on an accessible, lower-GC site. We report this as a
negative-leaning *result*, not a flaw, because it converts an untested "fusion-specific in principle"
claim into a measured specificity bar the eventual construct must clear.

**Delivery strategy (the route's real gate, and a concrete proposal).** No oligonucleotide is yet
approved for *targeted systemic delivery to a solid tumour*: the solved cases are liver (GalNAc→ASGPR;
inclisiran-class), local CNS (intrathecal; nusinersen), and local eye. EMC is none of these, so
delivery — not sequence design — is what gates this route, and we say so plainly. But EMC has an
unusually clean handle, and it falls out of our **own** surface-target analysis: **B7-H3 (CD276) is
expressed in 99% of sarcoma lines, high across every subtype, and internalises** (it already powers
the surface-antigen B7-H3 ADC arm). That makes an **anti-B7-H3 antibody–oligonucleotide conjugate (AOC)** — or a
B7-H3-decorated lipid nanoparticle — the logical EMC delivery vector: the same near-universal,
internalising antigen that addresses an ADC payload can address the fusion-junction oligo, and an
intracellular driver is something surface-targeting *alone* cannot reach. Corollaries: (a) prefer an
**siRNA chassis** for the delivery campaign — RISC has the mature conjugate/LNP toolbox and approved
precedents (GalNAc, LNP, the clinical TfR1-AOC), and the junction is equally RISC-targetable; (b)
expect EMC's **myxoid extracellular matrix** (hyaluronan-rich, high interstitial pressure) to be a
penetration barrier, so a stroma-normalising adjunct (hyaluronidase-class) is a reasonable co-design.
The decisive *biology* gate comes first and is delivery-independent — lipofected junction-knockdown
must kill EMC cells before any delivery campaign is justified (the ASO's analogue of the degrader's
dTAG gate). In-silico we cannot solve delivery (it is chemistry/formulation/biology); what we *can*
do is (1) hand a delivery lab this specific B7-H3-AOC/siRNA starting design instead of "good luck",
and (2) **watch for a usable in-silico delivery-prediction capability** in the method-watch
(`method-watch.md`) so the moment one matures, the B7-H3-targeted junction-siRNA can be scored
computationally and the route's feasibility re-graded.

**Surface/antigen targets — gated by one cheap confirm** *(Axis A: confirm-gated · Axis B: high).*
- **B7-H3 (CD276):** expressed in **99% of sarcoma lines, high across every subtype including
  myxoid** (DepMap; on top of 97% pan-STS by IHC) → the antibody-drug conjugate ifinatamab
  deruxtecan, a B7H3×CD3 bispecific, or B7-H3 CAR-T.
- **PRAME:** the best cancer-testis antigen — **53% of sarcoma lines, high in myxoid (7.6) and
  synovial (7.2)** → the PRAME ImmTAC brenetafusp (tumour-agnostic basket) or PRAME-directed
  cell therapy.
- **FAP-targeted radioligand therapy:** EMC's myxoid stroma is a strong candidate; the tracer is
  also diagnostic.

**Down-weighted with data/logic** *(Axis A & B: low).*
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
| Junction ASO/siRNA | in-silico pre-screen (`aso_insilico.py`: zero transcriptome off-targets + accessible site), then junction-knockdown vs scrambled in EMC lines (spare parental transcripts) | candidate has off-target ≤1mm transcriptome hits, no fusion knockdown, or undeliverable to tumour |
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
IHC. For the **ASO** route — whose questions are sequence/RNA rather than structure — we run a
CPU-only arm now (`aso_insilico.py`): a transcriptome-wide off-target screen against human RefSeq
RNA, ViennaRNA target-site accessibility, and sequence-liability filters, yielding a ranked,
off-target-screened gapmer shortlist. Scripts and a cloud-GPU pipeline are provided; the MD is the
highest-value single GPU experiment, and the ASO off-target/accessibility screen is the
highest-value experiment that needs no GPU at all.

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
`repurposing-hypotheses.md`). Fusion-junction ASO (5 fusion-specific gapmers; RNase-H mechanism): `junction_aso.py` /
`novel-modalities.md` §3.2; ASO in-silico evaluation (transcriptome off-target screen, ViennaRNA
target-site accessibility, sequence-liability filters): `aso_insilico.py`. Data: DepMap 24Q4
(CRISPR + OmicsExpression); AFND (HLA); human RefSeq RNA GRCh38.p14 (ASO off-target screen).
*(Full citations live in the per-route memos; verify-refs before submission.)*
