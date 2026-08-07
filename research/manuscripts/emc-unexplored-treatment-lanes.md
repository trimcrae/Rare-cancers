---
id: DOC-EMC-UNEXPLORED-LANES
title: Treatment lanes the portfolio does not contain — a ten-sweep deep search
level: L3
kind: memo
status: live
canonical_for: ["the 2026-08-07 unexplored-lane search and its grades"]
purpose: >
  Answer one question asked on 2026-08-07: what treatment paths exist that this repository's forty
  routes do not already contain? Ten parallel literature sweeps, screened against the full route
  registry rather than against any single manuscript, graded honestly, with the negatives kept.
scope: >
  L3. This memo REGISTERS candidate lanes and grades them; it does not re-grade any existing route
  except where a sweep produced a dated primary source that supersedes one, and those are collected
  in section 5 so they are not buried. Porting the surviving lanes into systems/graph/routes.json is
  the follow-on, exactly as emc-post-degrader-options.md was ported.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-08-07
last_verified: 2026-08-07
---

# Treatment lanes the portfolio does not contain — a ten-sweep deep search

> ⛔ **NOTHING HERE ASSERTS EFFICACY, SAFETY, A THERAPEUTIC WINDOW OR CLINICAL READINESS FOR EMC.**
> Every lane below is a *candidate*, most rest on evidence from another disease, and the ones with
> EMC-specific data are almost all n = 1 to n = 26. Where a sweep found nothing, this memo says so
> rather than leaving the question open.

## 0 · What this is, and what "new" was screened against

Ten parallel sweeps ran on 2026-08-07, each scoped to a lane the repository had never searched. The
novelty screen was deliberately the **strict superset**: every candidate was checked against all
**40 routes** in [`systems/graph/routes.json`](../../systems/graph/routes.json) *and* against the
technique-class table in
[`emc-post-degrader-options.md` §3b](./emc-post-degrader-options.md#3b--the-technique-classes-searched-and-where-each-landed),
which records what a previous search already considered and rejected. So anything surviving here is
new against any single manuscript, including [`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md) §3.

**Why the previous searches missed these.** Not oversight — **instrument shape**. The portfolio's
searches have been *molecular-modality-centric*: degrader architectures, oligonucleotides, antibodies,
cell therapy, small molecules. Four whole categories were therefore structurally invisible:

1. **Physical, device and locoregional modalities** — nothing in the portfolio is a machine, a beam or
   a procedure.
2. **The matrix as a target rather than a barrier** — the myxoid ECM appears in the portfolio's prose
   only as an obstacle to delivery.
3. **Non-cancer diseases sharing EMC's phenotype or its receptor family.**
4. **Treatment *strategy*** — scheduling, sequencing and trial architecture, as opposed to new agents.

And two instrument limits are worth naming because they produced *false negatives that read as
measured negatives*:

- ⚠ **[`emc_surfaceome_scan.py`](../modalities/emc_surfaceome_scan.py) cannot see glycans or stroma.**
  It ranks DepMap **tumour-cell monoculture mRNA**. A sulfation pattern has no gene to rank, and there
  is no CAF or ECM compartment in the data. Its own numbers prove the second point: `LRRC15` reads
  `frac_expressed 0.00` at the floor, yet LRRC15 is a real sarcoma stromal ADC target. The scan's
  conclusion that the selective ∩ normal-tissue-restricted intersection is empty is therefore a
  statement about **classic protein antigens**, which is narrower than how it currently reads.
- ⚠ **`CSPG4` is absent from that scan's `SEED_SURFACE` and from all four of its output artifacts.**
  Confirmed independently by two sweeps. It was never rejected; it was never seen.

**Provenance discipline used throughout.** The sandbox egress proxy 403s Europe PMC, PubMed, PMC,
ClinicalTrials.gov, EBI, Crossref and most publishers on CONNECT, and the session's shared WebSearch
budget (200 calls) was exhausted partway. Retrieval was therefore routed through GitHub Actions per
[CLAUDE.md §6](../../CLAUDE.md). Citations below carry their verification level:
**[FT]** full text read · **[API]** structured record read from Europe PMC / ClinicalTrials.gov /
UniProt / Cellosaurus · **[snippet]** search-result text only · **[unverified]** could not confirm.
⛔ **A `[snippet]` claim must not be quoted in a manuscript without upgrading it first.**

---

## 1 · The organising finding

**The portfolio is organised around one question — *how do we act on the fusion?* — and that question
has a paralogue-selectivity problem, a ternary-geometry problem and a no-binder problem attached to
it.** Every one of the ten sweeps independently produced its strongest candidate by **declining to
answer that question**:

| sweep | what it targeted instead of the fusion |
|---|---|
| physical / locoregional | dose and fractionation |
| matrix | the chondroitin-sulfate gel |
| non-cancer lookalikes | the **5′ partner's promoter** |
| fusion-cancer transfer | a kinase the fusion installs (SGK1) and one it activates (RET) |
| proximity chemistry | the protein's own degradation brake (DNA-PK) |
| nucleic acid | the **hybrid intron**, not the exon junction |
| immune | a glycan (oncofetal CS) and a peptide-HLA |
| metabolic / strategy | the schedule, and dormancy |
| frontier | the stroma (FAP) |
| clinical evidence | the **fusion variant as a biomarker**, not as a target |

That convergence is the memo's actual result. It is not an argument against the driver-directed
routes — it is the observation that **the portfolio's blockers are properties of one attack surface**,
and that ten independent searches all walked around it.

---

## 2 · Ranked shortlist

Ranked on *(strength of existing human or EMC-specific evidence)* × *(what a no-wet-lab program can
add)* × *(absence from the current portfolio)*.

| # | Lane | Why here | §
|---|---|---|---|
| **1** | **RET as EMC's activated, druggable effector** | Two independent groups; the only kinase measured as *expressed **and activated*** in EMC; two approved selective inhibitors; **no RET route among the 40**; twelve years with no follow-up | [3.1](#31--ret) |
| **2** | **Fusion-variant stratification (EWSR1 vs TAF15)** | Four independent lines converge, including a perfect response split in a 10-patient series; every clinician review says it needs validation; nobody has pooled it; the repo already owns the pooling method | [3.2](#32--fusion-variant-stratification) |
| **3** | **Lurbinectedin / LIFFT — an open trial EMC is eligible for and cannot find** | `NCT05918640` phase 1 eligibility is *"a known FET fusion (EWSR1, FUS, or TAF15)"*; all three of EMC's main partners are FET; the listed conditions do not include EMC, so no histology search surfaces it | [3.3](#33--fet-fusion-trial-eligibility) |
| **4** | **FAP-targeted ²²⁵Ac radioligand therapy** | `NCT07156565` recruiting in relapsed/refractory sarcoma, with a companion diagnostic and a paired FAP-PET trial; needs no fusion-selective binder; turns EMC's stroma into the selection criterion | [3.4](#34--fap-radioligand--the-2026-increment) |
| **5** | **The hybrid intron as a fusion-exclusive ASO target** | Kilobases of sequence existing in no other transcript, versus the ~20 nt the gapmer route works with; directly attacks the known GC-rich-junction weakness; feasibility fully computable now | [3.5](#35--the-hybrid-intron) |
| **6** | **Oncofetal chondroitin sulfate (VAR2CSA / Vartumab)** | EMC's defining matrix becomes the address; clinical-stage platform whose live PET trial already enrols chondrosarcoma; an antigen class the surfaceome screen structurally could not find | [3.6](#36--oncofetal-chondroitin-sulfate) |
| **7** | **The radioresistance reappraisal** | A live contradiction in EMC's own record — two registries say RT does nothing, the largest series says 100% vs 63% 10-year local control — resolvable with a BED regression and a bias analysis, no compute | [3.7](#37--the-radioresistance-reappraisal) |
| **8** | **Adaptive scheduling of pazopanib** | EMC is close to an ideal adaptive-therapy indication on five independent grounds; $0; and its falsifier is itself a publishable question | [3.8](#38--adaptive-scheduling) |
| **9** | **DNA-PK inhibition as an indirect fusion-destabiliser** | Curated experimental evidence *on NR4A3 itself*; removes the no-binder and ternary-geometry blockers by not needing either; folds into the existing DDR lane | [3.9](#39--dna-pk) |
| **10** | **SGK1** | 10/10 EMC tumours by IHC with an internal negative control; druggable AGC kinase; published 2006 and never followed up | [3.10](#310--sgk1) |
| **11** | **NR2F1 dormancy agonism** | Targets EMC's actual clinical problem; repoints the repo's orphan-NR-LBD stack onto a receptor that has a published tool compound — the known-answer control NR4A3 never had | [3.11](#311--nr2f1-dormancy) |
| **12** | **The hormone-responsive-partner subset** | A 5′ partner can import a druggable input: PGR::NR4A3 + tamoxifen produced >5 years of ongoing benefit; **no hormonal route among the 40** | [3.12](#312--hormone-responsive-partners) |

---

## 3 · The lanes

### 3.1 · RET

**The evidence.** In the sunitinib series (n = 10; 6 PR, 2 SD, 2 PD), verbatim: *"Among putative
sunitinib targets, only **RET** was expressed and activated in analysed samples"* — Stacchiotti et al.,
*Eur J Cancer* 2014;50:1657–64, **PMID 24703573** **[FT]**. Independently, RET expression is
significantly higher in EMC than in other sarcomas except liposarcoma — *Oncotarget* 2017;8:21770–7,
**PMID 28423517** **[FT]**.

**Why it matters and why it is not obvious.** Sunitinib and pazopanib each hit ~10 kinases, so EMC's
TKI activity is conventionally attributed to VEGFR. **Selpercatinib and pralsetinib are approved,
selective, and have never been given to an EMC patient.** The methodological guard comes free from the
adjacent failure: clear cell sarcoma's EWSR1::ATF1 transactivates MET, which motivated crizotinib
trials that produced only sporadic responses — and the exploratory analysis attributed that to
infrequent actual MET *activation*. Expression is not a target; measured activation is. **RET in EMC
passes the test MET in CCS failed.**

**Free next step.** Test whether *RET* is a fusion target gene: an NBRE-motif scan of its regulatory
region, the same bioinformatic approach that established *PPARG* and *ENO3* as direct targets, plus a
read across the public EMC expression series. **What would kill it:** no NBRE at *RET*, plus evidence
that RET phosphorylation tracks stromal rather than tumour content.

### 3.2 · Fusion-variant stratification

Four independent lines, none of which has been pooled:

- **Sunitinib**, verbatim: *"all responsive cases turned out to express the typical EWSR1-NR4A3 fusion,
  while refractory cases carried the alternative TAF15-NR4A3 fusion"* (**PMID 24703573** **[FT]**).
- **Pazopanib** phase 2, `NCT02066285`, n = 26 enrolled / 22 evaluable, 4 objective responses: all four
  responders carried EWSR1::NR4A3 (*Lancet Oncol* 2019, **PMID 31331701**; figures read from the 2025
  review's full text, PMC12504171 **[FT]**).
- **Outcome**: 1/16 EWSR1 died of disease vs 3/7 TAF15; 80% of non-EWSR1 tumours high-grade
  (**PMID 24746215** **[FT]**).
- **Mechanism**: the axon-guidance pathway is the major transcriptional discriminator between the
  variants — class 4–6 semaphorins higher in TAF15, growth-inhibitory class 3 higher in EWSR1,
  recapitulated in engineered cells (*J Pathol* 2019, **PMID 31020999**, PMC6766969 **[FT]**).
- And the two USZ patient-derived lines are a **matched pair** — `USZ20-EMC1` is EWSR1, `USZ22-EMC2`
  is TAF15 (**PMID 36316541** **[FT]**) — in which even the carfilzomib synergy splits by partner.

⚠ **The primary authors hedge, and the hedge belongs in the paper:** the sunitinib source itself says
*"Even in EMCS the fusion-protein is unlikely to be related to sunitinib sensitivity"* — i.e. they read
the correlation as a surrogate for something downstream. Every series is small and the TAF15 arms are
2–7 patients.

**Free next step.** A partner-stratified pooled synthesis using the repo's existing method
([`POLICY-evidence.md`](../../systems/POLICY-evidence.md): denominator-weighted proportions + Wilson
95% CIs, non-overlapping cohorts only) over every published EMC systemic-therapy report. This is the
cheapest paper on the board and it answers the complaint clinicians actually make (§5).

### 3.3 · FET-fusion trial eligibility

**`NCT05918640` (LIFFT, CHOP), phase 1/2, RECRUITING** **[API]**. Phase 1 eligibility is
**fusion-defined, not histology-defined**: age ≥10, recurrent/relapsed solid tumour with *"a known FET
fusion (fusion that contains EWSR1, FUS, or TAF15)"*. EMC's three principal 5′ partners are all FET
proteins, and ≈89–95% of EMC carries one. **The trial's listed conditions are Ewing / DSRCT /
undifferentiated sarcoma, so no histology-based search will ever surface it for an EMC patient.**

This is a search-index problem with a direct patient consequence, and the fix is a paragraph, not a
grant. Also verified open and EMC-eligible: `NCT06239272` (NRSTS2021, St. Jude — EMC is an explicitly
listed condition, ages 1–30), `NCT05722886` (DETERMINE, UK platform), `NCT03767075`, `NCT04040205`,
`NCT01659203` **[all API]**.

⚠ **Verified as NOT currently enrollable, against a 2025 review that lists two of them as open:**
`NCT05836571` is ACTIVE_NOT_RECRUITING; `NCT03600649` (seclidemstat, EMC explicitly listed) is status
UNKNOWN. And `NCT04305548` looks like an EMC trabectedin trial in search results but its condition list
is **Mesenchymal Chondrosarcoma only** — a different disease.

### 3.4 · FAP radioligand — the 2026 increment

`RT-FAP-RLT` is graded `concept` off 2022 ⁹⁰Y-FAPI data. Four things landed since **[all API]**:

- **`NCT07156565`** — [Ac225]-RTX-2358 in **relapsed/refractory sarcoma**, phase 1/2, **RECRUITING**,
  actual start 2025-11-12, with paired diagnostic [Cu64]LNTH-1363S.
- **`NCT06298916`** (PHANTOM) — ⁶⁴Cu-FAPI PET/CT in sarcoma against FAP IHC, recruiting.
- **First human FAP-RLT sarcoma therapy readout** — ¹⁷⁷Lu-FAPI-2286, n = 6, **PMID 42080808**;
  tolerated, and **3 of 6 died of progression before follow-up imaging**.
- **FAP IHC ↔ PET SUVmax r = 0.88** in 22 STS patients, **PMID 42128000**.

**Why it fits EMC:** it needs no fusion-selective binder and no antigen on the tumour cell — it targets
CAF stroma, which is what EMC has most of. ⚠ **The counterweight is real:** EMC is hypovascular, and
the same physics that starves it of chemotherapy limits any radioligand's delivery. And the repo's own
screen puts FAP at `enrichment 0.02, selectivity_q = 0.1555` — not significant — though that screen is
tumour-cell monoculture and structurally cannot see a CAF antigen (§0).

### 3.5 · The hybrid intron

**The idea.** The mature fusion mRNA's only unique feature is the exon 7 | exon 3 junction — ~20 nt,
GC-rich and specificity-poor, which is the gapmer route's known weakness. But the fusion **pre-mRNA**
has a second unique feature that is far larger: the **hybrid intron**, EWSR1 intron 7's 5′ portion
joined to NR4A3 intron 2's 3′ portion. That sequence exists in no other transcript in the body.
Anything inside it — a cryptic pseudoexon, the branch point, the polypyrimidine tract — is a
fusion-exclusive steric-block ASO target, and there are **kilobases** of it.

**Precedent for the mechanism, not for this application:** poison-exon inclusion is clinical (the
SCN1A exon-20N Dravet ASO; branaplam's HTT-lowering pseudoexon, *Nat Commun* 2022 **[snippet]**), and
ASO-mediated TRA2β poison-exon inclusion has an anti-tumour readout (*Nat Commun* 2025 **[snippet]**).
Applied to a fusion's hybrid intron: **concept-only, no example in any fusion-driven cancer.**

⛔ **A small molecule cannot do this.** Risdiplam/branaplam-class compounds read a degenerate motif,
not a fusion; branaplam also hit PMS1 and its Huntington's trial stopped for peripheral neurotoxicity.
Only an ASO can be fusion-exclusive here. And it does **not** solve delivery — same molecule class,
same `BLK-DELIVERY`, plus it acts on nuclear pre-mRNA.

**Free next step.** Reconstruct the hybrid intron per modelled breakpoint and run SpliceAI / Pangolin /
MaxEntScan: does it splice efficiently at all; is there an inducible pseudoexon; does that pseudoexon
carry a premature stop in the fusion's frame; where would an SSO tile. Output is a designed panel and
a *second, mechanistically independent* fusion-exclusive oligonucleotide route.

### 3.6 · Oncofetal chondroitin sulfate

**What EMC's matrix actually is, and why it re-ranks the field.** *"Since chondroitin sulfate is much
more abundant in the ECM of extraskeletal myxoid chondrosarcoma compared to intramuscular myxoma and
myxofibrosarcoma, it might, therefore, play a role in the more malignant behavior of this tumor"* —
Willems et al., *Virchows Arch* 2010;456:181–92, PMC2828560 **[FT]**. **Hyaluronan is the component
EMC shares with every myxoid tumour; chondroitin sulfate is the one that distinguishes it.**

**The platform.** VAR2CSA, a *P. falciparum* protein, binds a placental-type 4-O-sulfated chondroitin
sulfate re-expressed on most solid tumours, including tissue *"of both epithelial and mesenchymal
origin"* — *Cancer Cell* 2015, **PMID 26461094** **[API]**. **`NCT06645808`** (VAR2 Pharmaceuticals,
Vartumab PET imaging) is **RECRUITING** and its registered conditions include **chondrosarcoma and
osteosarcoma** **[API]**. ⚠ rVAR2 itself has been discontinued as a therapeutic in favour of the
Vartumab antibodies — do not write rVAR2 as the clinical vehicle **[snippet]**.

**Why the surfaceome screen could not have found it:** ofCS is a *sulfation pattern*. There is no gene
to rank. Its absence from the screen is an instrument limit, not a negative.

**Free next step.** Read the ofCS biosynthetic module — `CHST11/12/13/14/15`, `CHSY1/3`,
`CSGALNACT1/2`, `UST`, `DSE`, plus `CSPG4`, `CD44`, `VCAN`, `ACAN` — in the two readable EMC series.
Does EMC carry the 4-O-sulfotransferase signature VAR2CSA requires? That is a *sulfation-code*
argument and the honest in-silico proxy for a stain nobody will run.

**Its protein-backbone sibling: CSPG4/MCSP.** 71% medium-to-high in conventional chondrosarcoma
(PMC9468862 **[snippet]**); in STS, CSPG4-high vs low 5-year DFS **49% (95% CI 42–57) vs 61% (56–68)**
(**PMID 36221119** **[snippet]**); two live CAR trials (`NCT06096038` CAR-T; `NCT07627698` allogeneic
dual-target CSPG4/GD2 CAR-NK) **[API]**. Adding CSPG4 and the proteoglycan module to `SEED_SURFACE` is
a one-line change to an existing script and repairs a hole in a live manuscript.

### 3.7 · The radioresistance reappraisal

**The contradiction, stated as it stands:**

| direction | evidence |
|---|---|
| RT does nothing | Japanese registry n = 171: *"No association was found between (neo)adjuvant radiotherapy and local recurrence rates"* (**PMID 40885991** **[FT]**). SEER 1973–2016: RT associated with inferior OS on univariate analysis (**PMID 32856598** **[API]**) |
| RT does a great deal | MD Anderson, 41 consecutive localised EMC, median follow-up 94 months: 10-year local control **63% surgery alone vs 100% combined modality, P = 0.004** (**PMID 31436747** **[API]**) |

**The shape of the resolution.** The registries cannot see dose, and both are open to confounding by
indication — RT goes to the big, deep, close-margin tumours. Meanwhile the durable case responses
cluster far above the standard prescription in biologically effective dose: HDR interstitial
brachytherapy at 30 Gy in 2 fractions controlled **three separate metastatic sites for 36–41 months**
in one patient (**PMID 35494187** **[API]**), against 50 Gy/25 fx as the conventional STS prescription.
⚠ All BED arithmetic here is *ours*, α/β = 10 assumed, and no author quoted it.

**Free next step.** A BED meta-regression over every published EMC radiotherapy exposure with an
extractable dose, fraction size and local outcome — case reports included, because at this incidence
they *are* the dataset — fitting local control against BED with α/β free, plus a propensity/E-value
bias analysis of the registry result. **Nobody has an α/β estimate for EMC.**

⛔ **And a correction to the strongest preclinical support for this lane.** The dose-dependent
radiosensitivity plus hypoxia-prodrug potentiation result (**PMID 32948981**) was run in an
**H-EMC-SS** xenograft — the line this repository determined is
`NOT_FUSION_POSITIVE_PER_CURATED_RECORD` (2026-08-05). Cellosaurus `CVCL_1238` records, citing a
primary source, that it *"does not harbor a gene fusion involving EWSR1 which is a hallmark of
extraskeletal myxoid chondrosarcoma"*, and Cell Model Passports gives it **30.82 mutations/Mb**
against real EMC's measured TMB of 0–2. **The identity of this model is disputed** — the canonical
correction is
[`emc-surface-target-landscape.md` → Amendment 1](./emc-surface-target-landscape.md), and this memo
does not restate it. A real, profiled cell line was irradiated and responded; **"EMC xenograft" is
doing work the evidence cannot carry**, so this lane's grade rests on the clinical series and the
case-level dose evidence instead. The same caveat applies to the zaltoprofen/PPARγ result
(**PMID 36636023**) cited in §5. Both uses are classified in
[`emc-systems-map.json`](./emc-systems-map.json) → `OBJ-LINE-HEMCSS.read_by` as `invalidated`.

### 3.8 · Adaptive scheduling

**The idea.** Modulate dose or interrupt therapy to preserve a drug-sensitive population that
competitively suppresses resistant cells, instead of dosing to maximum tolerated and to progression.
Clinical anchor: adaptive abiraterone in metastatic castration-resistant prostate cancer, 10 of 11
patients holding stable oscillations at **47% of standard cumulative dose** (*Nat Commun* 2017,
**PMID 29180633** **[API]**; updated *eLife* 2022, **PMID 35762577**).

**Five EMC-specific reasons, none generic.** (i) There is **one active systemic class**, so preserving
it beats deepening it. (ii) Pazopanib's profile — ORR ~18% with median PFS ~19 months — is *control
without shrinkage*, the signature of competitive suppression and exactly where RECIST-driven dosing
buys nothing. (iii) The natural history is long enough for oscillation to run. (iv) Burden is
**countable**: lung nodules on volumetric CT are arguably a better control signal than a serum marker.
(v) Patients are on therapy for years, so halving cumulative dose is a claim on its own.

**What would kill it, and it must be the paper's centrepiece rather than a limitations line:**
anti-angiogenic resistance may not be fitness-costed, because **the drug's target is host endothelium,
not the tumour cell** — so resistance could be microenvironmental, and competitive suppression would
have nothing to work with.

**The deliverable is not "adaptive therapy works in EMC."** It is: here is the parameter region in
which it would, and here is exactly what you would have to measure to know which region EMC is in.
Two-population Lotka–Volterra, parameters as intervals, full sensitivity analysis over what published
data cannot identify. Cost: $0.

### 3.9 · DNA-PK

**Curated experimental evidence, on NR4A3 itself.** UniProt Q92570 **[API]**:
`Interacts with the constituents of DNA-PK heterotrimer PRKDC, XRCC6 and XRCC5; phosphorylates and
prevents NR4A3 ubiquitinylation and degradation (PubMed:25852083)`, with
`PTM: Phosphorylated by PRKDC {ECO:0000269|PubMed:25852083}`. Primary source: Medunjanin et al.,
*Cardiovasc Res* 2015;106:488–97, **PMID 25852083**.

**Why it is the highest evidence-to-cost item here.** If DNA-PK phosphorylation blocks NOR-1
ubiquitination, then **DNA-PK inhibition should lower NR4A3 protein with no ligand for NR4A3 of any
kind** — removing the no-selective-binder blocker and the ternary-geometry blocker by not needing
either. DNA-PK inhibitors are clinical-stage. And it lands inside the DDR lane the repo already built
rather than opening a new front. ⚠ It removes neither the paralogue nor the fusion-vs-wild-type
blocker: it would lower wild-type NR4A3 too, and whether NR4A1/NR4A2 are similarly regulated is
untested. **Mechanism established in vascular smooth muscle, not in any sarcoma.**

**Free next steps.** Read PMID 25852083 at primary level and confirm the site; check the site's
retention (see below); DepMap *PRKDC* dependency across sarcoma lines.

⭐ **A retention question that is already answered.** Both papers' post-translational sites map into
NR4A3's N-terminal region, and `OBJ-FUS-T1` is `EWSR1(1–431) :: NR4A3(1–626)` — **`NR4A3(1–626)` is the
full coding region, so nothing is deleted and EWSR1-LC is additive**
([`systems/AUDIT-2026-08-06-routes.md`](../../systems/AUDIT-2026-08-06-routes.md) X9). The SUMO sites
(ψKxE at K85; the ψKxSP pSuM site at K136/S138) are **INVARIANT across all 9 DBD-retaining
breakpoints**. ⚠ But the two source papers number them Lys-89 and Lys-137 with **inconsistent offsets
(4 and 1)**, so pin the residue by alignment before any manuscript quotes a number. ⛔ And neither site
is NR4A3-unique, so this axis does **not** deliver paralogue selectivity.

### 3.10 · SGK1

Tet-regulated EWS/NOR1 in chondrogenic cells induces SGK1, and **10/10 EWS/NOR1-positive EMC tumours
overexpressed SGK1 protein by IHC**, against non-neoplastic cells *in the same biopsies* and against
other sarcoma types — **PMID 16756948** **[API]**. SGK1 is a structurally characterised, druggable AGC
kinase. Published 2006; no knockdown, no inhibitor experiment, no confirmation that it is a
*dependency* rather than a marker, and the fusion→SGK1 link is from a rat line.

The generalised principle, taken from the menin/KMT2A logic: when the fusion TF is undruggable, the
highest-value node is **a druggable enzyme whose expression the fusion directly installs and which is
absent from the normal counterpart tissue** — that gives a therapeutic index for free. 10/10 with an
internal negative control is unusually clean for this disease.

### 3.11 · NR2F1 dormancy

**The disease fit.** EMC's natural history *is* the dormancy problem: distant metastasis in a large
minority, overwhelmingly lung, over many years, with long survival and reported near-complete 5-year
survival after complete metastasectomy — the problem is the next crop of nodules. **A therapy that
holds cells asleep and never shrinks a tumour is worthless in most cancers and unusually well-matched
here.** NR2F1/COUP-TF1 is the master regulator of disseminated-tumour-cell dormancy (*Nat Commun* 2015,
**PMID 25636082** **[API]**); a specific agonist (C26) induced a dormant state and suppressed lung
metastasis in head-and-neck models **with the effect persisting after treatment stopped** (*J Exp Med*
2022 **[snippet]**).

⭐ **The capability transfer is exact.** NR2F1 is an **orphan nuclear receptor with a ligand-binding
domain**, and this program has spent months building an orphan-NR-LBD pipeline — cryptic-pocket
metadynamics, fpocket grading, docking, MM-GBSA/FEP, de-novo design, paralogue matrices. Repointing it
costs almost no new engineering, and NR2F1 has something NR4A3 never had: **a published agonist to
calibrate against**, i.e. the known-answer control the flagship lacked.

⚠ **It also inherits the risk that sank the flagship** — paralogue selectivity in a nuclear-receptor
LBD (here NR2F2/NR2F6). That must be stated in the first paragraph, not the limitations.

### 3.12 · Hormone-responsive partners

**The finding, primary-verified.** Wilbur et al., *JCO Precis Oncol* 2022;6:e2200039,
**PMID 36103645**, PMC9489176 **[FT]**. A cellular-variant EMC, EWSR1-FISH-negative, rapidly recurrent
and lung-metastatic; RNA-seq found **PGR (exon 2) fused to the 5′UTR of NR4A3 (exon 2)** with outlier
*ESR1*, *PGR* and *GREB1* expression. On tamoxifen, verbatim: *"Since initiation of tamoxifen is over
5 years ago, she has had ongoing decrease in size of her pulmonary nodules and no evidence of disease
progression despite intraoperative rupture and previously rapid, aggressive recurrences."* The authors
also note the fusion **would not have been detected by panel-based commercial assays**, which cover
neither *PGR* nor *NR4A3*.

**The generalisable principle — and it is the strongest structural idea in the memo.** NR4A3 breaks
near its start, so **the 5′ partner supplies the promoter**. The pharmacologically reachable handle on
fusion *expression* is therefore the **partner's promoter**, not NR4A3's. Here the partner was PGR,
PGR transcription is oestrogen-driven, and a SERM turned it down.

⛔ **The corollary is a clean negative that closes a whole family of intuitions.** NR4A3 is a
MAPK-induced immediate-early gene, so "use a MEK inhibitor to lower fusion expression" is the obvious
idea — and it is **architecturally impossible**, because the fusion allele does not use NR4A3's IEG
promoter. The same argument closes β-adrenergic, angiotensin-II and serum-response modulation. Worth
stating explicitly in the paper, because a reader will otherwise propose it.

**Free next step.** A **partner-by-partner druggability map** of every reported NR4A3 5′ partner —
EWSR1, TAF15, TCF12, TFG, FUS, HSPA8, **PGR**, SMARCA2, LSM14A, ACTB, CARMN, SLCO5A1 — asking for each:
what promoter does this import, and is it druggable? PGR answers *yes, tamoxifen*. EWSR1 is the hard
case and the honest answer there may be *no*, which is itself publishable. Pure sequence and promoter
annotation. **The repo has no hormonal route among its 40.**

---

## 4 · Free to run now

Six lanes resolve on a **single** `emc-expression-datasets.yml` dispatch against the two readable EMC
series (`GSE24369`/GPL6244, 6 EMC vs 29 comparators, 93.2% probe mapping; `GSE4303`/GPL3290, 10 EMC,
58.2% after UniGene rescue) — both already characterised in
[`emc-atr-vulnerability.json`](../modalities/emc-atr-vulnerability.json):

| read | settles |
|---|---|
| `ASS1` | arginine auxotrophy / ADI-PEG20 — one binary answer |
| CS/GAG biosynthesis + PAPS module | ofCS (§3.6), CSPG4, substrate reduction, chondroitinase |
| PPARγ **target-gene** signature (not `PPARG` abundance) | the agonist-vs-redundancy direction question, open since 2009 |
| `DLL3`, `ASCL1`, `NEUROD1`, `INSM1`, `HES1` | whether EMC occupies an SCLC-style NE-high state |
| Buffa/Winter hypoxia signature | disciplines §3.7 and the whole hypoxia framing |
| `NR2F1` | §3.11's precondition |

Plus, each independent and $0:

- ⭐ **`GSE11185` — "Differences between NOR1 and EWS/NOR1"** is the direct wild-type-versus-fusion
  experiment, it is in this repo's own GEO census, and **it has never been read.**
- **PDB 7WNH (Nurr1 bound to NBRE, 3.1 Å) is already in the repo** — the anchor for testing whether a
  response-element-based degrader is geometrically buildable, on the linker-reach enumeration the repo
  already owns.
- Compare the published **H1/H5/H7/H8 allosteric pocket** on Nurr1 against Pocket-5 on 8XTT. A match
  hands the FEP lane a clinical-stage scaffold with published SAR; a mismatch is a documented negative.
- The **BED regression** (§3.7) and the **partner-stratified pooling** (§3.2) — literature only.

---

## 5 · Corrections and re-grades that fell out

Collected here rather than buried, because several touch live route grades.

1. ✅ **CLOSED 2026-08-07 — `RT-ICI-TKI`'s evidence is out of date, and the missing effect size has now
   been RETRIEVED.** IMMUNOSARC II's dedicated EMC phase 2 cohort (*J Clin Oncol* 2025;43(16_suppl):11513,
   NCT03277924): **24 accrued May 2020–July 2024 at 9 centres in Spain, Italy and the UK; 23 evaluable;
   16/23 progression-free at 6 months (reported as 77%); median PFS 13.2 mo (95% CI 5.7–20.7); 12-month
   OS 90% (95% CI 77–100); best response 2 PR, 18 SD, 2 PD.** Prior antiangiogenic exposure (6/23) was
   associated with shorter median PFS (7 vs 13 mo, p = 0.11) and significantly shorter OS (28 mo vs not
   reached, p = 0.038).
   ⚠ *Superseded, retained: "**The effect size could not be retrieved** (ascopubs 403s; not indexed in
   Europe PMC) and is `[unverified]`."* **Both halves of that were true and the conclusion did not
   follow.** ascopubs returns 403 on `/doi/`, `/doi/full/` and `/doi/abs/`, `doi.org` inherits the 403 by
   redirect, and Europe PMC returns `hitCount: 0` for the DOI — but **Crossref, Semantic Scholar and
   OpenAlex each serve the publisher-deposited abstract in full**, and the first two agree token-for-token
   apart from one HTML entity. The search had stopped at the two obvious doors. Every route and its HTTP
   code is recorded as a measurement in
   [`emc-systemic-therapy-pooling.json`](./emc-systemic-therapy-pooling.json) → `retrieval_provenance`.
   ⚠ **It remains a CONFERENCE ABSTRACT and it carries two unreconciled arithmetic inconsistencies:** the
   primary endpoint is stated as both 77% and 16/23 (= 69.6%), and the best-response counts sum to 22
   rather than the 23 evaluable patients (the printed percentages 9/82/9% are consistent only with a
   denominator of 22). No full paper is indexed — the same master trial's bone-sarcoma (**PMID 39540661**)
   and clear-cell-sarcoma (**PMID 41836677**) cohorts have them — and ClinicalTrials.gov has no posted
   results for NCT03277924 (`hasResults: false`). Separately, IMMUNOSARC I enrolled **4 EMC patients
   (4/52)** and selected EMC deliberately for antiangiogenic sensitivity (**PMID 33203665** **[FT]**);
   ⚠ **IMMUNOSARC I and II are stage 1 and stage 2 of the same registration**, so its mixed-histology
   48% 6-month PFS must never be pooled with the EMC cohort's.
2. ✅ **CLOSED 2026-08-07, AND THE CORRECTION IS LARGER THAN IT LOOKED.** ⚠ *Superseded, retained: "the
   trabectedin row **overstates its own denominator** … 5 subjects with EMCS *or* MCS … not 5 EMC
   patients" — right in direction, and it stopped one step short, because it read only the abstract.*
   **The full text states the split in its Methods — "we adopted TWO EMCS subjects and three MCS
   subjects" — and Table 2 labels every subject individually.** So the EMC denominator is **2**, not "5"
   and not "unstated": both EMC subjects had **stable disease**, with PFS **13.0** and **7.4** months and
   OS **26.4** and **10.4** months. ⭐ **And the arm's headline number lands on an MCS patient:**
   the published **12.5 months (95% CI 7.4–NR)** is the arm's Kaplan–Meier median over all five subjects,
   and Table 2's five individual values are 13.0, 7.4, 22.2, 7.5, 12.5 — so it coincides with subject 5's
   own PFS, also mesenchymal chondrosarcoma. Either way it is a property of the mixed arm and not of its
   EMC patients, and the arm's single objective response was also an MCS patient (**PMID 27418251** **[FT]**). Attached to the
   registry row 2026-08-07, with the superseded values registered in
   `treatments.systemicEvidenceCorrections`.
3. ⚠ **`RT-FAP-RLT` is graded `concept` on 2022 data.** Four 2025–26 items supersede that (§3.4).
4. ⚠ **`CD248`/endosialin reads `enrichment +2.29, selectivity_q = 0.0, selectivity_significant: true`
   in the repo's own surfaceome scan and appears in no prose.** One of the few significant hits in that
   artifact, with a prior sarcoma antibody program. Whoever owns the surface-antigen lane should pick
   it up.
5. ⚠ **The ATR assessment's "unrelated controls" were the largest-moving concepts measured.** OXPHOS
   and adipogenesis were used to discount a DDR signal — correctly, and that conclusion is untouched.
   But nobody read the control's own value, and in both EMC series it moves more than anything else.
   **A control's value is a measurement.** Worth an audit pass beyond this lane.
6. ⭐ **The fusion's demonstrated direct target is a glycolytic enzyme.** An NR4A3 fusion transactivates
   **ENO3** through chromatin modification of its promoter (**PMID 26310886**) — cited in this repo
   only as evidence for the chromatin mechanism, never for what it turns on. A $0 re-read of the
   committed EMC series gives ENO3 **+0.813** (t 3.66) and **+3.811** (t 13.22) in the two cohorts, with
   `MKI67` flat in the first. The muscle-admixture confound (ENO3 is muscle-specific β-enolase; EMC
   arises in thigh) was tested and fails at set level: the whole myogenesis set is flat and the
   muscle-restricted markers *fall*. ⚠ n = 6 and n = 10, cached gene-set subset, no multiple-testing
   correction.
7. ⚠ **NR4A2 can substitute for NR4A3 as the driver.** An EMC with no canonical NR4A3 fusion carried
   **HSPA8::NR4A2**, full neuroendocrine phenotype, **methylation class EMC at 0.99** (*Virchows Arch*
   2025, **PMID 41315062** **[API]**); **FUS::NR4A2** is separately reported. `RT-ASYMMETRIC` holds
   NR4A2-sparing as best-effort — for that subset a strictly NR4A2-sparing agent misses by
   construction. This bounds the addressable population; it does not contradict the selectivity rule.
8. ⚠ **NR4A3 has exactly one PDB entry** — 8XTT, apo NMR, LBD 379–626, no ligand. NR4A2 has 8; NR4A1
   has 21, including recent crystals at 2.0–2.7 Å **[API, UniProt cross-references]**. **The anti-target
   is better resolved than the target**, and every reported paralogue ΔΔG inherits that asymmetry. It
   belongs in the manuscript's limitations explicitly.
9. ⚠ **A published chemogenomics audit found that several putative NR4A ligands lack on-target
   binding** (*J Med Chem* 2025, **PMID 40968635** **[API]**). Direct warning about any NR4A literature
   compound treated here as a validated binder.
10. ⚠ **`TECH-EMC-MODEL-ACCESS` reads `current_state: absent` with 10 routes gated on it, but
    NCC-EMC1-C1 exists** (**PMID 40580361**) and the two USZ lines are Cellosaurus-registered
    (`CVCL_C6MX` EWSR1, `CVCL_C6MY` TAF15). The honest state is *"models exist; access is
    institutional"* — a different sentence and a different forecast.
11. ⚠ **The menin play does not transfer, and that is measured rather than unexplored.** The mapped
    EWSR1::NR4A3 interactome has no obligate druggable coactivator: Six3 *represses* the fusion, PARP-1
    binds wild-type NOR1 but not the fusion, SRC/NCOA works through AF-1. The source's own conclusion
    is that the fusion and wild-type NOR1 associate with *mostly the same* proteins — it diverges by
    **escaping** modulators, not by acquiring a dependency. ⚠ But **no modern IP-MS/BioID interactome
    of the fusion exists**, so the honest statement is "not found by the methods applied", which makes
    it a precisely-specified collaborator ask rather than a closed question.
12. ⭐ **The AF-2 helix is functionally required and is uncited here.** Deleting the last 15 residues of
    the 949-aa fusion destroys **>70%** of transcriptional activity; I939, D940 and F943 each cripple it
    (**PMID 12049818** **[API]**). It cuts both ways: it says the C-terminal LBD surface is on a
    validated mechanism, while a separate report describes NOR-1's canonical cleft as replaced by a
    hydrophilic surface. Two labs, two assays, in tension — both belong in the paper.
13. ⚠ **A live contradiction in the 2025 EMC review.** It states EMC is *"consistently negative for KIT
    (CD117)"* and uses that to exclude GIST; three independent series report CD117 positivity at 52.6%,
    84%, and "variable in all cases" **[API]**. That is the difference between a diagnostic exclusion
    and a therapeutic candidate, and nobody has reconciled it.
14. ✅ **Fixed this session:** the `Sturm/Willems` attribution on the vidofludimus/Nurr1 paper in
    [`nr4a3-druggability-reconciliation.md`](../modalities/nr4a3-druggability-reconciliation.md)
    (correct authors were two files away, matching on PMC ID and DOI); a mislabelled literature-cache
    record where PMID 35952317 — a breast-cancer letter — sat under an EMC tamoxifen filename; and four
    unclassified H-EMC-SS uses that had turned gate 3 red.

---

## 6 · Considered and rejected

Absence from sections 2–3 is a judgement, not an oversight.

| lane | why not |
|---|---|
| **TTFields** | Efficacy is explicitly division-rate-dependent — the worst possible match for an indolent tumour. A dedicated search returned **no sarcoma clinical trial**, and no transducer configuration exists for a deep proximal limb. |
| **NIR-photoimmunotherapy** | The only approved agent is EGFR-targeted, and this repo measured **EGFR at −2.21 log2, p = 1.0** in EMC. Light penetration is millimetres; EMC is deep. |
| **Electrochemotherapy** | The sarcoma trial's own inclusion criterion was **maximum 3 cm deep**. |
| **FLASH radiotherapy** | **No sarcoma clinical data at all.** Method-watch trigger, not a route. |
| **BNCT** | Dose scales with boron atoms per unit volume, and the field already measured this failure in the nearest histology: myxofibrosarcoma BNCT attributed low BPA accumulation to *"the low density of cells per unit volume of mucus produced by the tumor"*. EMC is **more** matrix-dominated. ⭐ The negative generalises — the same cells-per-volume correction applies to the repo's SSTR2 and FAP radioligand routes, which are dosed per volume but delivered per cell. |
| **PEGPH20 / hyaluronidase matrix depletion** | Wrong enzyme — EMC's matrix is chondroitin-sulfate-rich and **partially hyaluronidase-resistant**. And the strategy failed at phase 3 in the tumour it was built for (HALO-301, OS 11.2 vs 11.5 months, **PMID 32706635**). |
| **Losartan / LOXL2 / FAK stromal normalisation** | All from **collagen-stiff desmoplastic** stroma. EMC is a soft hyaluronan/CS gel. Simtuzumab failed phase 2 across five indications. Revisit only if the matrisome census returns high `COL1A1`/`LOX`/`ACTA2`. |
| **CD44 / RHAMM** | Killed by the repo's own data: `enrichment −3.89, q = 1.0` — *depleted* in the translocation-sarcoma class. |
| **ADAR/AIMer editing to install a stop codon** | **Chemically impossible** — A→I cannot create UAA/UAG/UGA. The splice-acceptor workaround fails discrimination because the acceptor is NR4A3-derived and identical in wild-type. |
| **n-Lorem bespoke ASO** | Structurally ineligible on the published inclusion criterion: EWSR1::NR4A3 is shared by every EMC patient, not a 1–30-patient private mutation, and their IND record contains no oncology division. ⚠ Explicit exclusion language not retrieved. |
| **AOC for EMC** | **No targeting arm exists.** The blocking step is an antigen, not conjugate chemistry. Every clinical AOC is muscle-directed. |
| **In vivo CAR-T as a modality** | Registry query returned 8 trials, **all autoimmune or haematological, zero solid-tumour**. Keep the *economics* argument (§below); drop the modality claim. |
| **CAR-M as a standalone route** | Contradicted in the direction that matters: translocation-associated sarcomas carry **significantly lower** macrophage counts than non-translocation sarcomas (**PMID 32313727**), weakening the trafficking premise in exactly EMC's class. |
| **Engineered bacteria** | Taken seriously and graded honestly — perfect niche fit for a hypoxic matrix-rich tumour, but **ACTM-838's trial is TERMINATED** and *C. novyi*-NT has four phase 1 trials over twenty years and no phase 2. Decisive for *this* program: there is **no in-silico instrument** to bring to it. |
| **ASPS as a precedent for ICI in EMC** | Rejected on mechanism, and the rejection is worth publishing. ASPS's response is attributed to an immune-hot, CD8-infiltrated, **hypervascular** microenvironment; EMC is cold, excluded, hypovascular. Shared classification, opposite biology. |
| **TEAD/YAP inhibitors** | No YAP/TAZ/TEAD dependency reported in EMC anywhere in a 1,369-record corpus, and mechanistically a different object. Close as a publishable negative. |
| **PARP inhibitors** | Inverted here — PARP-1 represses wild-type NOR1 and the fusion *escapes* it. |
| **Ivosidenib / IDH** | **Nominal name-match only.** EMC has no IDH mutation and no true cartilage differentiation. Worth one paragraph precisely because the *name* misleads clinicians into conventional-chondrosarcoma reasoning. |
| **Scleromyxedema pharmacology (IVIG, IMiDs, bortezomib)** | Driver is a plasma-cell paraprotein; mucin is the only shared feature. IMiD neosubstrate degrons are C2H2 zinc fingers; NR4A3's DBD is a C4 nuclear-receptor finger. |
| **Teprotumumab / IGF-1R** | Ewing's ganitumab phase 3 was negative and an explicit *"no preclinical rationale"* exists for chondrosarcoma of bone. Keep as a cheap closed line. |
| **Nirogacestat / Notch** | No Notch pathway data in EMC at all. Retained only as a **trial-design precedent** (§below). |
| **Retinoid differentiation** | APL works because PML-RARα *is* a retinoid receptor the drug re-activates. NR4A3 is ligand-independent with an atypical pocket — structurally disanalogous. |
| **Senolytics / pro-senescence** | Low proliferative index and no senescence-inducing therapy to follow. The one-two punch needs a first punch EMC never receives. |
| **Glutamine, serine/one-carbon, FASN** | All proliferation-coupled; EMC is slow-cycling, and its lipid signal reads oxidative rather than lipogenic. |
| **Autophagy degraders (AUTAC/ATTEC/AUTOTAC)** | Nuclear target, cytosolic mechanism; no TF or nuclear-receptor precedent. |
| **HERV / cryptic "dark" antigens** | No sarcoma immunopeptidome work found, and repeats are unmeasurable on the array platforms that constitute EMC's available data — **unfalsifiable from the desk**, which is a reason to down-rank. |

**Two things retained as arguments rather than routes.** ⭐ **The ultra-rare economics argument:** a
bespoke autologous cell product will never be built for a few hundred patients a year, so the unit that
makes any cell therapy coherent is a **FET-fusion sarcoma basket** (EMC + Ewing + DSRCT + clear cell
sarcoma — all FET-rearranged, all ultra-rare, all antigen-poor). ⭐ **The minimum-evidence-path
argument:** atezolizumab's ASPS approval rested on a **single-arm, n = 49, ORR 24%** study
(**PMID 37672694** **[API]**) in EMC's exact disease class, and desmoid (nirogacestat, DeFi), TGCT
(vimseltinib, MOTION) and NF1-PN provide three more indolent-mesenchymal-rare-disease registration
precedents between 2020 and 2025. That makes *"what is the minimum credible evidence path for EMC"* a
simulable question with a Bayesian operating-characteristics answer, on the registry already curated
here.

---

## 7 · Limits of this memo

- **Ten sweeps, one day.** Breadth was the objective; each lane is scoped, not settled.
- **Verification is uneven and labelled.** The shared WebSearch budget ran out partway and every
  literature host is proxy-blocked, so a substantial fraction of citations are `[snippet]` or `[API]`
  rather than `[FT]`. **The labels are the deliverable's honesty, not decoration.**
- **This memo grades nothing that already has a grade owner.** Section 5 reports where a dated primary
  source has overtaken an existing grade; applying those re-grades belongs to each route's owner.
- **No lane here is validated.** The strongest EMC-specific evidence in the entire sweep is a
  22-patient single-arm phase 2 and a 10-patient retrospective series. Several load-bearing items are
  n = 1.
- ⛔ **Two data gaps could not be closed:** NCBI SRA/BioProject rate-limited (HTTP 429) and PDCM Finder
  returned HTTP 500, so *"does any EMC PDX exist?"* is unanswered. Both are one re-dispatch away.
