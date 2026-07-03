# An in-silico surface-antigen landscape for extraskeletal myxoid chondrosarcoma: prioritising delivery- and immunotherapy-directed targets, and a call for validation in patient-derived models

> **Preprint status (2026-07-03).** Computational, **hypothesis-generating** manuscript. Every antigen
> ranking here is derived from an **EMC-*surrogate*** analysis (sarcoma cell lines and normal-tissue atlases —
> EMC itself is absent from the public functional-genomics panels), and is labelled as such throughout. We
> make **no** EMC-specific surface-expression claim on surrogate data. The manuscript's purpose is twofold:
> (1) to publish a rigorous, honestly-bounded prioritisation of candidate surface antigens and the modalities
> they enable for EMC, and (2) to make an explicit, actionable request to the laboratories that hold
> patient-derived EMC models for the one dataset that converts these priors into an EMC-validated result
> (§6). Medical-integrity rule (repo-wide): no clinical fact, statistic, or antigen assignment is asserted as
> EMC-established without a citation; surrogate-derived items are flagged.

**Running head:** EMC surface-target landscape (in-silico)
**Keywords:** extraskeletal myxoid chondrosarcoma; EWSR1::NR4A3; surfaceome; antibody–drug conjugate; CAR-T; T-cell engager; radioligand therapy; tumour delivery.

---

## Abstract

**Background.** Extraskeletal myxoid chondrosarcoma (EMC) is a rare translocation sarcoma driven in most
cases by the *EWSR1::NR4A3* fusion, an aberrant nuclear-receptor transcription factor on an otherwise quiet
genome. Driver-directed strategies must reach an **intracellular** target: the leading routes — an NR4A3-LBD
degrader and a fusion-junction antisense oligonucleotide (ASO) — are gated respectively by pocket
druggability and by the classic problem of delivering a large charged oligonucleotide into the tumour-cell
cytosol/nucleus. **Cell-surface antigens** offer an orthogonal axis: they enable antibody–drug conjugates
(ADC), T-cell engagers (TCE), CAR-T/NK cells and radioligand therapy (RLT) — modalities whose delivery is
either a solved antibody-mediated paradigm or acts at the cell surface with no intracellular delivery at all,
at the cost of the fusion-level selectivity the ASO uniquely offers.

**Methods.** With no EMC line in public functional-genomics data, we built an EMC-surrogate pipeline: an
unbiased human surfaceome (UniProt plasma-membrane + transmembrane/GPI; 2,820 genes) ranked by expression
across the translocation-sarcoma DepMap class (n = 76 lines) and its myxoid subset; a normal-tissue
therapeutic-window analysis (Human Protein Atlas RNA tissue specificity/distribution + subcellular location);
and an attempted cross-check against the only public real-EMC transcriptome (GEO GSE4303). Each stage
self-validates on positive/negative controls.

**Results.** The surfaceome scan reprioritises the field's default antigen: **B7-H3 (CD276) is broadly
expressed but not selective** (98% of the surrogate class; enrichment vs other cancer lineages +0.14
log2TPM), while more selective candidates rank above it — **CDH11, FGFR1, GPC2, PTK7, MCAM/CD146, EPHB4**.
Layering the normal-tissue window is decisive: it identifies **GPC2, CDH11 and NCAM1/CD56 as both selective
and tumour-restricted** (the top priors), flags **FGFR1 as window-limited** (high tumour expression but broad
normal-tissue distribution), and shows **B7-H3 to be doubly penalised** — non-selective across cancers *and*
broad in normal tissue. We integrate expression, selectivity and window into a prioritised **antigen ×
modality** map. The single public real-EMC dataset (GSE4303) proved
technically unusable (two-colour cDNA-clone array, relative ratios, no gene-level annotation), which is
itself the motivation for the data request below.

**Conclusion.** In-silico analysis nominates a small, prioritised set of EMC surface-antigen candidates and
pairs each with a delivery/immunotherapy modality less gated by the intracellular-delivery problem that
limits the ASO. The decisive validation — EMC-specific surface expression — requires the immunophenotype and
transcriptome of the recently established patient-derived EMC lines (USZ-EMC; NCC-EMC1-C1). We set out exactly
what data would confirm or refute each prior and invite the groups holding those models to co-validate.

---

## 1. Introduction

EMC is a rare soft-tissue sarcoma (~3% of soft-tissue sarcomas) with a protracted but relentless course and
few effective systemic options [Stacchiotti; and see the EMC-program roadmap]. It is defined molecularly by a
recurrent translocation fusing the 5′ transactivation region of **EWSR1** (less often TAF15, and rarely
TCF12/TFG/FUS) to most of the orphan nuclear receptor **NR4A3 (NOR-1)**, yielding a constitutively active
chimeric transcription factor on a genome otherwise carrying few recurrent secondary mutations [Sjögren;
Panagopoulos]. The fusion is thus, to a first approximation, the single clonal driver.

**The intracellular-target bottleneck.** Because the driver is a nuclear transcription factor, driver-directed
therapies must act inside the cell. The two leading computational routes in this program both confront a
delivery- or druggability-limited intracellular step: (i) an **NR4A3 ligand-binding-domain degrader**, which
is NR4A3-selective but not fusion-selective and depends on a cryptic-pocket druggability case; and (ii) a
**fusion-junction ASO/siRNA**, which is uniquely *fusion-exclusive* (it silences the chimera while sparing
wild-type NR4A3) but whose dominant, unsolved gate is delivering a large polyanionic oligonucleotide into the
tumour-cell cytosol/nucleus and escaping the endosome. Both are compelling; both are held up at the cell
membrane.

**Why surface antigens are a distinct axis.** A cell-surface antigen changes the problem in two ways. First,
**delivery**: surface-directed modalities either use antibody-mediated targeting — a solved, approved
paradigm — or act at the surface with no intracellular delivery requirement, or (for cell therapies) traffic
themselves. Second, **selectivity model**: a surface antigen is not the fusion and is present on some normal
cells, so tumour-vs-normal selectivity comes from the antigen's expression *distribution*, not from fusion
sequence. Surface targeting therefore trades the ASO's exquisite fusion-exclusivity for a far more tractable
delivery problem — a genuine and complementary strategic option, not a replacement.

**The gap this paper fills.** EMC surface-antigen expression has, to our knowledge, never been systematically
mapped, and EMC is absent from the public cancer cell-line dependency/expression panels that make such maps
routine in common cancers. The field defaults to B7-H3 by extrapolation from other sarcomas, with no
EMC-specific evidence. We provide the first unbiased in-silico surface-antigen landscape for EMC — explicitly
surrogate-based — to prioritise which antigens and modalities merit the scarce, decisive wet-lab validation,
and to specify exactly what that validation is.

---

## 2. Methods

All analyses are computational, use only public data, and run reproducibly in continuous integration; every
output JSON is committed (Data & code availability). No wet-lab work was performed.

**2.1 Surfaceome definition.** We defined the human cell-surface proteome as UniProt-reviewed human proteins
annotated with a plasma-membrane subcellular location (SL-0039) together with a transmembrane (KW-0812) or
GPI-anchor (KW-0336) topology — i.e. proteins presenting an extracellular epitope engageable by an
antibody/ligand — unioned with a curated seed of clinically actionable surface antigens so that established
targets are always evaluated (2,820 genes total). [`emc_surfaceome_scan.py`]

**2.2 EMC-surrogate expression.** EMC has no line in DepMap. We used the DepMap OmicsExpression matrix
(log2(TPM+1)) and defined an **EMC-surrogate translocation-sarcoma class** by OncotreeSubtype
(Ewing/synovial/myxoid/alveolar/DSRCT/clear-cell; n = 76 lines), with the **myxoid** subset (closest to EMC)
resolved separately, and all non-sarcoma lineages retained as an off-target comparator. For each surface gene
we report class mean expression, fraction of class lines expressing it, myxoid-subset mean, and enrichment
versus the non-sarcoma comparator. Self-validation: housekeeping genes are excluded by the surfaceome filter;
a known broadly-expressed surface marker (CD276) recovers as broadly expressed. [`emc_surfaceome_scan.py`]

**2.3 Normal-tissue therapeutic window.** For the shortlist we queried the Human Protein Atlas for RNA tissue
specificity, tissue distribution, per-tissue nTPM, subcellular location and cancer specificity, and
classified each antigen into a therapeutic-window verdict — tumour-**RESTRICTED** (favourable window prior)
versus **BROAD** normal-tissue liability — flagging expression in high-consequence vital tissues. Positive
controls (DLL3, GPC3; textbook tumour-restricted antigens) must classify RESTRICTED and a housekeeping-broad
control (B2M) BROAD. [`emc_surface_normal_window.py`]

**2.4 Real-EMC cross-check (attempted).** We attempted to corroborate the surrogate ranking against the only
public real-EMC transcriptome, GEO GSE4303, with a platform-interpretability gate.
[`emc_gse4303_crosscheck.py`]

**2.5 Modality mapping.** Each prioritised antigen was paired with the surface modality its biology best
supports (internalising receptor → ADC/AOC; surface-accessible non-internalising → TCE/CAR/RLT), annotated
with clinical precedent where a targeting agent exists (flagged for verification).

---

## 3. Results

### 3.1 An unbiased surfaceome scan reprioritises B7-H3 and nominates more selective antigens

Across the 2,820-gene surfaceome, ranking by class expression and cross-lineage selectivity yields a
consistent picture (surrogate; [`emc-surfaceome-scan.json`]):

- **B7-H3 (CD276) is broad but non-selective.** It is expressed in **98%** of the surrogate class but its
  enrichment versus other cancer lineages is only **+0.14** log2TPM — i.e. it is expressed almost everywhere,
  which is favourable for tumour coverage but unfavourable for a therapeutic window. This tempers the field's
  default reliance on B7-H3 for EMC.
- **More selective candidates rank above it** (enrichment vs other cancer lineages, surrogate): **CDH11
  (+3.18)**, **FGFR1 (+1.99**, and the highest-expressed shortlist antigen in the single available myxoid
  line**)**, **GPC2 (+1.49)**, **PTK7 (+1.24)**, **MCAM/CD146 (+1.09)**, **EPHB4 (+1.0)**. Several have
  existing ADC/CAR/TCE programmes in other indications.

Self-validation passed: the surfaceome filter excluded housekeeping genes, and CD276 recovered as broadly
expressed.

### 3.2 A normal-tissue window separates tumour-restricted candidates from broad liabilities

Expression and cross-cancer selectivity are necessary but not sufficient: a surface target must be
**restricted in normal tissue**. The Human Protein Atlas window analysis
([`emc-surface-normal-window.json`]) classifies each shortlist antigen; controls behaved as required (DLL3,
GPC3 → RESTRICTED; B2M → BROAD), validating the classification.

**Table 2. Normal-tissue therapeutic-window verdict per antigen** (Human Protein Atlas RNA;
[`emc-surface-normal-window.json`]). Controls behaved as required.

| Antigen | HPA RNA tissue specificity | Therapeutic-window verdict |
|---|---|---|
| **GPC2** | Tissue enhanced | **RESTRICTED** |
| **CDH11** | Tissue enhanced | **RESTRICTED** |
| **NCAM1 / CD56** | Tissue enhanced | **RESTRICTED** |
| FAP | Tissue enhanced | RESTRICTED (stromal) |
| EGFR | Tissue enhanced | RESTRICTED |
| KIT | Tissue enhanced | RESTRICTED |
| **FGFR1** | Low tissue specificity | **BROAD liability** |
| PTK7 | Low tissue specificity | BROAD liability |
| MCAM / CD146 | Group enriched | BROAD liability |
| EPHB4 | Low tissue specificity | BROAD liability |
| **B7-H3 / CD276** | Low tissue specificity | **BROAD liability** |
| ERBB2 | Low tissue specificity | BROAD liability |
| *DLL3 (control, tumour-restricted)* | Tissue enriched | RESTRICTED ✓ |
| *GPC3 (control, tumour-restricted)* | Tissue enriched | RESTRICTED ✓ |
| *B2M (control, broad)* | Low tissue specificity | BROAD ✓ |

The decision-relevant reading is the **intersection of §3.1 (selective in the tumour class) and §3.2
(restricted in normal tissue)**, which sorts the shortlist cleanly:
- **Selective AND tumour-restricted — the top priors:** **GPC2** (surrogate +1.49; RESTRICTED; onco-fetal,
  internalising), **CDH11** (surrogate +3.18, the most selective; RESTRICTED; mesenchymal cadherin), and
  **NCAM1/CD56** (RESTRICTED; the EMC neuroendocrine-phenotype angle). These are the antigens to validate
  first.
- **Selective but broad window — window-limited:** **FGFR1** is the most striking tension — highest in the
  single myxoid line yet *Low tissue specificity* in normal tissue, so despite strong tumour expression its
  ADC/CAR window is questionable (a small-molecule FGFR adjunct may fit its biology better than a
  surface-cytotoxic). PTK7, MCAM and EPHB4 are similarly window-limited.
- **Broad AND non-selective — a double liability:** **B7-H3/CD276** is both non-selective across cancer
  lineages (§3.1, +0.14) *and* broadly expressed in normal tissue (Table 2). Two independent axes now argue
  against treating it as EMC's obvious first surface target; it remains viable chiefly through a **crossfire
  modality (RLT)** that tolerates broad, or an engineered therapeutic index.

*Caveat on surface confirmation.* HPA immunofluorescence subcellular annotation did not label every antigen
"plasma membrane" (e.g. GPI-anchored GPC2, cadherin CDH11), but all shortlist antigens are members of the
UniProt plasma-membrane + transmembrane/GPI surfaceome by construction (§2.1); we rely on that topology, not
on HPA IF, for surface accessibility.

### 3.3 An integrated antigen × modality prioritisation

Combining tumour-class expression, cross-cancer selectivity, normal-tissue window and receptor biology yields
a prioritised map (surrogate priors; clinical agents flagged for verification):

| Antigen | Surrogate class expr / selectivity | Normal-tissue window | Best-fit modality | Clinical precedent (other indications) |
|---|---|---|---|---|
| **GPC2** ★ | +1.49 | **RESTRICTED** | ADC / CAR (internalising, onco-fetal) | GPC2 CAR/ADC in neuroblastoma [citation to verify] |
| **CDH11** ★ | +3.18 (most selective) | **RESTRICTED** | TCE / CAR (mesenchymal cadherin) | CDH11 in sarcoma biology [citation to verify] |
| **NCAM1/CD56** ★ | (surrogate: see scan) | **RESTRICTED** | ADC / CAR (NE phenotype) | CD56 ADC/CAR [citation to verify] |
| **FGFR1** | +1.99, myxoid-high | BROAD (window-limited) | small-molecule FGFR adjunct > ADC | FGFR-directed agents [citation to verify] |
| **PTK7** | +1.24 | BROAD | ADC (if TI achievable) | PTK7 ADC [citation to verify] |
| **MCAM/CD146** | +1.09 | BROAD | ADC / CAR (TI-dependent) | CD146-directed programmes [citation to verify] |
| **EPHB4** | +1.0 | BROAD | ADC / ligand-directed | EphB4 agents [citation to verify] |
| **B7-H3/CD276** | broad, +0.14 (non-selective) | BROAD (double liability) | RLT (crossfire tolerates broad) / engineered-TI ADC | B7-H3 ADC (ifinatamab deruxtecan), CAR-T [citation to verify] |
| **FAP** | stromal | RESTRICTED (stromal) | RLT (FAPI) / anti-stroma | FAPI-RLT in sarcoma [citation to verify] |

★ = **top prior** (selective in the tumour class **and** tumour-restricted in normal tissue). The table is
sorted so the intersection winners lead; window-limited and broad antigens follow with the modality most able
to tolerate their liability (engineered therapeutic index, or crossfire RLT).

**Why the modality matters for the delivery argument.** The right column of modalities shares the property
that motivates this paper — each sheds the ASO's intracellular-delivery gate:

| Modality | Intracellular delivery needed? | Gate that replaces "delivery" |
|---|---|---|
| T-cell engager / bispecific (antigen × CD3) | **No** — kills at the surface via recruited T cells | Cold tumour microenvironment; antigen coverage |
| CAR-T / CAR-NK | **No** — living cells home and kill | Solid-tumour infiltration; cold TME; antigen escape |
| Radioligand therapy (¹⁷⁷Lu/²²⁵Ac) | **No** — payload is radiation; **crossfire** kills unbound neighbours | Antigen level; radiobiology; tumour-vs-normal window |
| ADC (antibody + cytotoxic) | Some — needs internalisation, but a **solved, approved** paradigm; diffusible payload | Antigen internalisation; tumour-vs-normal window |
| AOC (antibody–oligo conjugate) | Yes — but antibody-targeted, not naked oligo | Same antigen; serves the ASO's delivery arm |

**Radioligand therapy is the sharpest contrast to the ASO.** The ASO must functionally engage *every* tumour
cell's RNA — one escapee regrows the tumour — whereas an α/β emitter kills cells it never bound (crossfire
range ~mm), so **heterogeneous delivery is tolerable**. RLT converts "hit every cell" into "hit enough cells
near every cell", which is precisely the property the ASO lacks; it also uniquely tolerates a broad antigen
like B7-H3 through crossfire and dose fractionation.

### 3.4 The only public real-EMC transcriptome is unusable — which is the reason for the data request

We attempted to move from surrogate to real EMC data using the single public EMC expression dataset, GSE4303
([`emc-gse4303-crosscheck.json`]). It proved technically unusable for surface-antigen ranking: a seven-platform
**two-colour cDNA-clone microarray** series (three EMC samples per platform) whose values are log-ratios
versus a reference pool (not absolute expression) and whose probes are clone/spot identifiers without
gene-level annotation, so none of the shortlist genes resolved. The platform-interpretability gate correctly
flagged the data rather than forcing a meaningless ranking. This negative result is important: **there is no
usable public real-EMC surface-expression dataset**, which is exactly why the recently established
patient-derived EMC lines — and their holders — are the essential path to validation (§6).

---

## 4. Discussion

**A complementary third axis on the same driver.** EMC's driver can be attacked from three compartments:
protein (the NR4A3-LBD degrader; target-selective, not fusion-selective), RNA (the fusion-junction ASO;
fusion-exclusive, delivery-gated), and **surface** (this work; less delivery-gated, not fusion-exclusive).
These are complementary shots, not competitors. The surface axis is the antigen-discovery engine that also
supplies the ASO's antibody-oligonucleotide-conjugate delivery arm, so the map here de-risks more than one
route at once.

**Reprioritising B7-H3.** The most immediately actionable finding is that the field's default EMC surface
target is broad but not selective in the surrogate class. This does not disqualify it — broad expression aids
coverage, and a crossfire modality (RLT) or an engineered therapeutic index can exploit it — but it argues
against treating B7-H3 as the obvious first choice and for evaluating the intersection winners
(GPC2, CDH11, NCAM1/CD56 — selective *and* tumour-restricted) in parallel, while treating the
window-limited but highly-expressed FGFR1 as a candidate for a modality that tolerates broad expression or
for a small-molecule adjunct rather than a surface cytotoxic.

**Broader indications.** The nominated antigens are pan-sarcoma/pan-cancer targets with active ADC/CAR/TCE/RLT
programmes; EMC is a clean, single-driver *entry* indication for a surface-target strategy that generalises —
the market-widening logic that a rare-cancer result needs to attract development.

---

## 5. Limitations

- **Surrogate, not EMC.** The expression ranking uses translocation-sarcoma DepMap lines; EMC has no line.
  The **myxoid** subset closest to EMC is a **single** line, so the EMC-nearest signal is anecdotal and the
  n = 76 translocation class carries the weight. No antigen is claimed as EMC-expressed.
- **mRNA is a proxy for surface protein.** Both the DepMap ranking and the HPA window are transcript-level;
  surface-protein density, epitope accessibility and internalisation rate — the properties an ADC/CAR
  actually needs — require protein-level and functional data.
- **Cross-cancer, not tumour-vs-normal, in the scan.** The scan's "enrichment" is versus other cancer
  lineages; the normal-tissue safety axis comes separately from HPA (§3.2), which is bulk normal tissue and a
  window *prior*, not a safety guarantee.
- **The public real-EMC dataset is unusable** (§3.4); the surrogate cannot be corroborated against real EMC
  from public data.
- **Clinical-agent annotations are flagged for verification**; specific trial/agent claims must be sourced
  before use.
- **Delivery efficiency is not solved by naming an antigen.** Surface targeting removes the *oligo* delivery
  gate but introduces modality-specific gates (cold TME for immune modalities; internalisation for ADC;
  radiobiology for RLT).

---

## 6. The validation this needs — a request to the EMC-model community

This landscape is a set of *priors*. The single dataset that converts it into an EMC-validated result is the
**surface expression of patient-derived EMC cells** — and, uniquely, that reagent now exists. Two groups have
recently established and characterised patient-derived EMC models: **USZ-EMC** (USZ20-EMC1, USZ22-EMC2;
Bangerter et al., *Human Cell* 2022/2023) and **NCC-EMC1-C1** (Iwata et al., *Human Cell* 2025). These models
are not in the public expression panels, and their transcriptomes are held by the authors (available on
request or not yet public).

**What we request, in decreasing order of value and increasing order of effort for the holder:**
1. The lines' **existing RNA-seq / expression data** (if generated during characterisation) — this alone lets
   us re-run the entire pipeline on real EMC and validate or refute every antigen prior, at essentially no
   marginal cost to the holder.
2. A targeted **flow-cytometry or IHC panel** of the top candidates (GPC2, PTK7, CDH11, FGFR1, MCAM, B7-H3) on
   the lines and, where available, primary tumour — the direct surface-protein readout.
3. Collaboration on a short **surface-target validation study** pairing this in-silico map with their models.

We would welcome co-analysis and co-authorship. The computational landscape is ready; the models are the
missing half, and their holders are best placed to complete it.

---

## 7. Conclusion

An unbiased, honestly-bounded in-silico analysis nominates a small prioritised set of EMC surface-antigen
candidates — led by **GPC2, CDH11 and NCAM1/CD56** (selective *and* tumour-restricted) over the field-default
B7-H3 (broad and non-selective) — and pairs each with a delivery/immunotherapy modality less gated by the
intracellular-delivery problem that limits the fusion-junction ASO. Because EMC is absent from public functional-genomics data and the one public EMC
dataset is unusable, the decisive validation depends on the recently established patient-derived EMC lines. We
provide the map, specify the validating experiment, and invite the model-holding groups to complete it.

---

## Data & code availability

All analysis code and committed outputs are in the project repository (`research/modalities/`), refreshed by
GitHub Actions to the `modalities-cache` branch:
- **Surfaceome scan** — `emc_surfaceome_scan.py` → `emc-surfaceome-scan.json`
- **Normal-tissue window** — `emc_surface_normal_window.py` → `emc-surface-normal-window.json`
- **Real-EMC data probe** — `emc_line_data_probe.py` → `emc-line-data-probe.json`
- **GSE4303 cross-check** — `emc_gse4303_crosscheck.py` → `emc-gse4303-crosscheck.json`

Public data sources: UniProt (surfaceome), DepMap (OmicsExpression; surrogate expression), Human Protein
Atlas (normal-tissue/cancer expression, subcellular location), NCBI GEO (GSE4303).

## References

Verified in the repository's reference pool:
- **Sjögren H, et al.** EWSR1/NR4A3 fusion in EMC (defining fusion).
- **Panagopoulos I, et al.** Fusion variants/partners in EMC.
- **Bangerter, et al.** USZ-EMC patient-derived EMC models. *Human Cell* 2022/2023.
- **Iwata S, et al.** Establishment and characterization of NCC-EMC1-C1. *Human Cell* 2025.
- **Uhlén M, et al.** Tissue-based map of the human proteome (Human Protein Atlas). *Science* 2015.
- **Bausch-Fluck D, et al.** The in silico human surfaceome. *PNAS* 2018. (surfaceome definition basis.)

To verify (do not treat as established until sourced):
- EMC-specific surface expression of any nominated antigen — **[citation to verify]** (surrogate only here).
- Clinical-stage agents per antigen (GPC2, PTK7, FGFR1, CDH11, MCAM, EPHB4, B7-H3, FAP) — **[citation to
  verify]** per antigen/indication.
- Rank-order and magnitude of B7-H3 expression in EMC specifically — **[citation to verify]**.
- EMC incidence / proportion-of-STS figure — **[citation to verify]**.

---
*Provenance: consolidates the surfaceome scan, normal-tissue window, EMC-line data probe and GSE4303
cross-check (committed CPU outputs on `modalities-cache`) with the surface-modality memos
`emerging-modalities-scan-emc.md` and `car-t-strategies-emc.md`. Surrogate-based; no EMC-specific surface
claim is asserted.*
