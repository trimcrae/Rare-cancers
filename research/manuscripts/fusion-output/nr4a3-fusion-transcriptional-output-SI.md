---
id: DOC-NR4A3-FUSION-TRANSCRIPTIONAL-OUTPUT-SI
title: "Supplementary Information — the direct-target catalogue of EWSR1::NR4A3 across three EMC cohorts"
level: L3
kind: manuscript
status: live
canonical_for: ["the full 22-row evidence-typed NR4A3 target catalogue with verbatim sentences", "the complete set-score, robustness, stratified-comparator and covariate-adjustment tables for the EMC transcriptional-output reading", "the PPARγ receptor-activity reading and its adipogenic ceiling"]
purpose: >
  Carry the material that supports the transcriptional-output manuscript but does not belong in a
  journal main text: the complete evidence-typed catalogue with the verbatim sentence behind every
  classification, the full set-score table with each set's detectability threshold, the complete
  robustness panel, every stratified comparator contrast with its own exact permutation p, the
  covariate-adjustment and muscle-admixture tables, the PPARγ activity reading, and the method
  detail and pre-registered decision rule referenced from the main text, the recorded GEO
  cohort search, and how the Haller NR4A3 deposit's genome build was determined.
scope: >
  Supplementary tables and method detail for one expression re-analysis. Asserts nothing about
  efficacy, selectivity, safety, a therapeutic window or clinical readiness for any agent, target or
  gene, and no such quantity is computed. Nothing here measures occupancy.
audience: [maintainers, external reviewers, autonomous research agents]
related: [DOC-NR4A3-FUSION-TRANSCRIPTIONAL-OUTPUT]
date: 2026-08-08
last_verified: 2026-08-08
---

# Supplementary Information

**For:** *Almost every gene set reads higher in the index arm: a size-matched empirical null for small rare-tumour expression series, and what it leaves of the EWSR1::NR4A3 direct-target catalogue.*

Every table here is generated from a committed artifact and is not re-typed from prose; the
producers are listed in the main text's Data and code availability section. Section numbers below
are referenced from the main text as §S1–§S8.

---

## S1 · Method detail

### S1.1 · Probe mapping and floors

Probes were mapped to gene symbols per platform. GPL6244: 20,230 of 28,459 probes carry a symbol,
giving 18,694 distinct symbols. GPL3290: 27,203 of 43,008 spots resolve through an EST-accession
bridge to 14,932 distinct symbols — so a gene unreadable on GPL3290 may be absent from the bridge
rather than from the array, and is recorded as unread rather than as absent.

Each sample's values are z-scored against that array's own probe distribution, so a per-sample score
is a within-array quantity. A gene score for a sample is its mean z over the probes mapping to it; a
set score is the mean over the set's readable members. Floors: **three samples per group** for any
contrast, and **four genes and 0.4 coverage** for any set score. A set below the floor emits no
number and says so — which is why class A, at three genes, is never scored as a set.

### S1.2 · The circularity grade

Whether GSE4303 is the Subramanian (2005) cohort was graded from the fetched GEO series record,
never from sample counts: the record's title, summary, contributors and linked PubMed identifier
were read verbatim. If the record names PMID 15920699 or Subramanian, the verdict is **circular**; if
it does not, the verdict is *not-clean* rather than clean — the absence of a name is not evidence of
independence; if the record could not be read at all, the verdict is *unanswered*. The record does
name both, so the verdict is circular, which is what makes both the set-E score and the *PPARG* gene
row on that platform non-independent (main text §3.8).

### S1.3 · The pre-registered decision rule, and how it landed

A six-branch decision rule was written and committed while the measurement run was still executing,
so the verdict could not be fitted to whatever came back. Each branch carried its sentence, its
ceiling and its next step in advance.

| # | outcome | what it licenses |
|---|---|---|
| **A** | *ENO3* reproduces **and** class A (or A+B) clears its null on **both** platforms **and** *PLAGL1* reads down | A positive, EMC-specific result, with the ceiling attached in the same paragraph. |
| **B** | *ENO3* reproduces, class A clears its null on **one** platform only | A single-platform observation, reported as one. |
| **C** | *ENO3* reproduces, **nothing** clears its null | Still a result: the published target set is not distinguishable from a size-matched random gene set. |
| **D** | *ENO3* does **not** reproduce | Report the instrument and stop. No biological sentence may be written. |
| **E** | *ENO3* reproduces but *PLAGL1* reads up | Every up row loses its strongest defence against the offset explanation. |
| **F** | Filion Table 1 clears its null but class A does not | The instrument reads EMC and the fusion-target set is the thing that is flat. |

**Outcome F came true**, with a per-gene positive inside it that the rule did not anticipate. Two
limits of the pre-registration are recorded rather than quietly rewritten. First, the branches were
written over *set* scores and the measurement landed at the *gene* level, so a future version of this
rule needs an explicit gene-level branch. Second, the rule did not anticipate that the per-gene
result would itself be split by a later confound audit — *ENO3* surviving every stratification while
*SEMA3C* reverses sign — so it had no branch for "the genes disagree with each other", which is what
happened.

---

## S2 · The complete evidence-typed catalogue

Class assignments are from the main text Table 1. The **verbatim sentence** each classification rests
on is held in the machine-readable catalogue (`nr4a3_fusion_targets.py` → `LITERATURE_TARGETS`,
emitted to `nr4a3-fusion-targets.json` → `evidence_table.rows[].verbatim`) and is not reproduced here
only for length; every row below carries its citation and the assay the classification rests on.

A published negative control accompanies the catalogue: ***CALD1***, whose promoter was searched for
NOR-1 response elements in the same experiment that found the *SMPX* site, and none were found
(PMID 27181368). It controls the inference "this gene moved, therefore NR4A3 bound it" — not EMC
biology.

### TABLE S1 — the complete evidence-typed catalogue

| gene | class | factor actually tested | assays | cell system | species | expected in EMC | citation |
|---|---|---|---|---|---|---|---|
| **ENO3** | A | TFG::NR4A3 (TFG-TEC) | EMSA, ChIP (endogenous promoter), luciferase reporter, two NGFI-B response element motifs upstream of the putative TSS, ChIP for histone H3 acetylation at the endogenous promoter | cultured cell lines over-expressing TFG-TEC (the t(3;9) EMC fusion variant) | human (human beta-enolase promoter) | UP | Kim AY, Lim B, Choi J, Kim J. The TFG-TEC oncoprotein induces transcriptional activation of the human beta-enolase gene via chromatin modification of the promoter region. Mol Carcinog 2016. PMID 26310886, doi 10.1002/mc.22384 |
| **PPARG** | A | EWSR1::NR4A3, NR4A3 (native), NR4A3-deltaC (native truncated) | predicted perfect NBRE at -675 bp (5' AAAGGTCA 3'), band-shift (EMSA) with the fusion protein, 2.8 kb human PPARG isoform-1 promoter luciferase reporter, single-nucleotide NBRE mutant of that reporter | CFK2 fetal RAT chondrogenic cells, stable EWSR1/NR4A3 lines (et2, et16, et19) and transient transfection of wild-type CFK2; HUMAN PPARG promoter construct | rat (the promoter construct is human) | UP | Filion C, Motoi T, Olshen AB, et al. The EWSR1/NR4A3 fusion protein of extraskeletal myxoid chondrosarcoma activates the PPARG nuclear receptor gene. J Pathol 2009;217(1):83-93. PMID 18855877, PMCID PMC4429309, doi 10.1002/path.2445 |
| **SEMA3C** | A | EWSR1::NR4A3, TAF15::NR4A3, NR4A3 (native) | in-silico NBRE-like site (MatInspector, GRCh38 chr7), chromatin affinity purification + target qPCR (ChAP-qPCR), Strep-tagged | tBJ/ER transformed HUMAN fibroblasts engineered to express Strep-tagged NR4A3, EWSR1-NR4A3 (E-N) or TAF15-NR4A3 (T-N) | human | UP | Brenca M, Stacchiotti S, Fassetta K, et al. NR4A3 fusion proteins trigger an axon guidance switch that marks the difference between EWSR1 and TAF15 translocated extraskeletal myxoid chondrosarcomas. J Pathol 2019;249(1):90-101. PMID 31020999, PMCID PMC6766969, doi 10.1002/path.5284 |
| **BIRC3** | B | NR4A3 (native) | NBRE binding site | vascular smooth muscle cells / hypoxic endothelium | human/rodent vascular | UP | Reviewed in PMCID PMC6912296 and PMC8583700 |
| **CCND1** | B | NR4A3 (native) | ChIP at the Cyclin D1 promoter, NBRE site | hepatocytes; vascular smooth muscle cells; guidewire arterial-injury model in NOR-1-deficient mice | mouse / rat vascular and hepatic cells | UP | Reviewed in Herring JA, Elison WS, Tessem JS. Function of Nr4a Orphan Nuclear Receptors in Proliferation, Apoptosis and Fuel Utilization Across Tissues. Cells 2019;8:1373. PMID 31683815, PMCID PMC6912296; and in Haller F, et al. Nat Commun 2019;10:368. PMID 30664630, PMCID PMC6341107 |
| **CDKN2AIP** | B | NR4A3 (native) | ChIP at predicted sites in the CDKN2AIP promoter, luciferase reporter reversed by promoter mutant | MHCC-LM3 human hepatocellular carcinoma cells | human | UP | Zhao X, Min X, Wang Z, et al. NR4A3 inhibits the tumor progression of hepatocellular carcinoma by inducing cell cycle G0/G1 phase arrest and upregulation of CDKN2AIP expression. Int J Biol Sci 2024. PMID 39664575, PMCID PMC11628324, doi 10.7150/ijbs.95174 |
| **COX5A** | B | NR4A3 (native) | Cut&Tag over the promoter, dual-luciferase reporter | neonatal mouse cardiomyocytes; HEK293T reporter | mouse; human reporter construct | UP | Peng H, et al. eBioMedicine 2024;106:105268. PMID 39098108, PMCID PMC11334830 |
| **GLS2** | B | NR4A3 (native) | ChIP-seq + mRNA-seq, dual-luciferase reporter, abolished by mutation of the predicted NR4A3 motif | Schwann cells (diabetic peripheral neuropathy model) | rat/mouse Schwann cells | UP | Pang B, Chen S, Bai Y, Zhang Y, Wang Z. NR4A3 alleviates diabetic neuropathy via GLS2-mediated mitochondrial repair and Schwann cell differentiation. iScience 2026. PMID 42028030, PMCID PMC13099357, doi 10.1016/j.isci.2026.115515 |
| **ICAM1** | B | NR4A3 (native) | binding to the NBRE consensus site | TNF-stimulated endothelial cells / monocyte adhesion | human endothelial | UP | Reviewed in PMCID PMC8583700 / PMC10088923 / PMC9100886 |
| **LOXL2** | B | NR4A3 (native) | named a direct NOR-1 target gene in the source review | cardiac fibroblast-to-myofibroblast switch, NOR-1 transgenic mice | mouse | UP | Reviewed in Martinez-Gonzalez J, et al. Int J Mol Sci 2021;22:11371, PMCID PMC8583700 |
| **MYH7** | B | NR4A3 (native) | named a direct NOR-1 target gene in the source review | cardiac hypertrophy, NOR-1 transgenic mice | mouse | UP | Reviewed in PMCID PMC8583700 |
| **NOX1** | B | NR4A3 (native) | gene silencing, luciferase reporter, site-directed mutagenesis, EMSA | vascular smooth muscle cells; co-localisation in human atheroma | human | UP | Reviewed in Martinez-Gonzalez J, et al. Int J Mol Sci 2021;22:11371, PMCID PMC8583700 |
| **PDP1** | B | NR4A3 (native) | Cut&Tag over the promoter | neonatal mouse cardiomyocytes | mouse | UP | Peng H, et al. eBioMedicine 2024;106:105268. PMID 39098108, PMCID PMC11334830 |
| **SDHA** | B | NR4A3 (native) | Cut&Tag, truncated-promoter dual-luciferase mapping to region R3 (predicted element AAAGTCAC) | neonatal mouse cardiomyocytes; HEK293T for the HUMAN SDHA promoter reporter | mouse cardiomyocytes; human HEK293T for the reporter | UP | Peng H, Yuan J, Wang Z, et al. NR4A3 prevents diabetes induced atrial cardiomyopathy by maintaining mitochondrial energy metabolism and reducing oxidative stress. eBioMedicine 2024;106:105268. PMID 39098108, PMCID PMC11334830, doi 10.1016/j.ebiom.2024.105268 |
| **SKP2** | B | NR4A3 (native) | EMSA, ChIP, NBRE site in the SKP2 promoter | vascular smooth muscle cells | human/rodent VSMC (the review does not disambiguate) | UP | Reviewed in Martinez-Gonzalez J, et al. NR4A3: A Key Nuclear Receptor in Vascular Biology, Cardiovascular Remodeling, and Beyond. Int J Mol Sci 2021;22:11371. PMID 34768801, PMCID PMC8583700 |
| **SMPX** | B | NR4A3 (native) | promoter deletion, site-directed mutagenesis of a non-consensus NBRE (-167/-160), EMSA, ChIP in differentiating human skeletal myoblasts | human vascular smooth muscle cells and HSMM myoblasts | human | UP | Ferran B, Marti-Pamies I, Alonso J, et al. The nuclear receptor NOR-1 regulates the small muscle protein, X-linked (SMPX) and myotube differentiation. Sci Rep 2016;6:25944. PMID 27181368, PMCID PMC4867575 |
| **TH** | B | NR4A3 (native) | transient transfection through an NBRE site in the TH promoter | vascular smooth muscle cells; NOR-1 transgenic mouse aorta | mouse / VSMC | UP | Reviewed in Martinez-Gonzalez J, et al. Int J Mol Sci 2021;22:11371, PMCID PMC8583700 |
| **VCAM1** | B | NR4A3 (native) | binding to the NBRE consensus site | TNF-stimulated endothelial cells / monocyte adhesion | human endothelial | UP | Reviewed in Martinez-Gonzalez J, et al. Int J Mol Sci 2021;22:11371, PMCID PMC8583700; and PMCID PMC10088923 |
| **VTN** | B | NR4A3 (native) | listed by an independent review as a functionally validated direct target, over-expression + blocking-antibody / silencing rescue of migration, co-localisation in human atherosclerotic lesions | vascular smooth muscle cells; independently raised >2-fold by NR4A3 over-expression in the human MHCC-LM3 hepatocellular line | human | UP | Haller F, et al. Nat Commun 2019;10:368. PMID 30664630, PMCID PMC6341107 (target list); Martinez-Gonzalez J, et al. Int J Mol Sci 2021;22:11371, PMCID PMC8583700 (VSMC); Zhao X, et al. Int J Biol Sci 2024, PMCID PMC11628324 (MHCC-LM3) |
| **PLAGL1** | C | EWSR1::NR4A3 | differential display in a fusion-expressing line, RT-PCR in six EMC tumours | CFK2 chondrogenic cells over-expressing EWS/NOR1; human EMC tumours vs immortalised and primary human chondrocytes | rat cells; human tumours | DOWN | Filion C, et al. The PLAGL1 gene is down-regulated in human extraskeletal myxoid chondrosarcoma tumors. Cancer Lett 2005. PMID 16112421, doi 10.1016/j.canlet.2004.12.007 |
| **SGK1** | C | EWSR1::NR4A3 | differential display in a tetracycline-regulated fusion line, co-immunocytochemistry, immunohistochemistry in 10 fusion-positive EMC | CFK2 fetal RAT chondrogenic cells with tetracycline-controlled EWS/NOR1 | rat | FLAT_OR_DOWN_AT_TRANSCRIPT_LEVEL | Labelle Y, et al. Serum- and glucocorticoid-regulated kinase 1 (SGK1) induction by the EWS/NOR1(NR4A3) fusion protein. Biochem Biophys Res Commun 2006. PMID 16756948, doi 10.1016/j.bbrc.2006.05.134 |
| **NDRG2** | D | [] | Affymetrix U133A microarray, 3 fusion-positive EMC vs 137 other sarcomas, Western blot, immunohistochemistry in 9/9 EWSR1/NR4A3-positive EMC | human EMC tumour tissue | human | UP | Filion C, et al. J Pathol 2009;217(1):83-93. PMID 18855877, PMCID PMC4429309 |

---

## S3 · Every scored gene set, with its detectability threshold

The **threshold** column is the value the observed delta had to exceed to fall outside the 95% band of
its own size-matched null; **reached** expresses the observed delta as a fraction of it (below 1) or a
multiple of it (at or above 1). Reporting this converts a flat set from an uninterpretable shrug into
a bounded negative: the A+B direct-target set reached 39% and 88% of what it needed, while the
published EMC phenotype overshot by 11.9× and 4.2×.

Two rows deserve a reader's caution because they clear their threshold only barely, and the main text
does not lean on either: the PPARγ KO_UP falsifier on GPL6244 (1.02×) and the TRRUST human-curated
arm on GPL6244 (1.02×). A set that clears by 2% is a different object from one that clears by 12-fold,
and the multiple is printed so the two are never read alike.

⛔ **Set E is circular on GPL3290** and is reported for completeness only (§S1.2).

---

### TABLE S2 — every scored gene set, with its detectability threshold

| set | platform | n genes | Δ | null 95% band | threshold | reached | verdict |
|---|---|---:|---:|---|---:|---:|---|
| A_fusion_dna_binding_targets | GPL6244 | 3 | — | — | — | — | no score (below floor) |
| A_fusion_dna_binding_targets | GPL3290 | 3 | — | — | — | — | no score (below floor) |
| A_plus_B_all_dna_binding | GPL6244 | 19 | +0.0403 | [-0.1418, +0.1047] | 0.10465 | 39% | not distinguishable |
| A_plus_B_all_dna_binding | GPL3290 | 17 | +0.3301 | [-0.2972, +0.3765] | 0.37648 | 88% | not distinguishable |
| B_native_nr4a3_dna_binding_targets | GPL6244 | 16 | -0.0675 | [-0.1568, +0.1142] | -0.15684 | 43% | not distinguishable |
| B_native_nr4a3_dna_binding_targets | GPL3290 | 14 | -0.1453 | [-0.3357, +0.3971] | -0.33573 | 43% | not distinguishable |
| C_fusion_expression_only | GPL6244 | 2 | — | — | — | — | no score (below floor) |
| C_fusion_expression_only | GPL3290 | 2 | — | — | — | — | no score (below floor) |
| D_filion_table1_emc_vs_137_sarcomas | GPL6244 | 21 | +1.1311 | [-0.1374, +0.0947] | 0.09472 | 11.94× | **SET-SPECIFIC** |
| D_filion_table1_emc_vs_137_sarcomas | GPL3290 | 18 | +1.4783 | [-0.2853, +0.3481] | 0.34814 | 4.25× | **SET-SPECIFIC** |
| E_filion_table2_overlap_with_subramanian | GPL6244 | 20 | +0.8932 | [-0.1399, +0.0978] | 0.0978 | 9.13× | **SET-SPECIFIC** |
| E_filion_table2_overlap_with_subramanian | GPL3290 | 18 | +1.9850 | [-0.2853, +0.3481] | 0.34814 | 5.70× | **SET-SPECIFIC** |
| F_brenca_EWSR1_high_axon_guidance | GPL6244 | 3 | — | — | — | — | no score (below floor) |
| F_brenca_EWSR1_high_axon_guidance | GPL3290 | 3 | — | — | — | — | no score (below floor) |
| G_brenca_TAF15_high_axon_guidance | GPL6244 | 10 | -0.4975 | [-0.1957, +0.1460] | -0.19574 | 2.54× | **SET-SPECIFIC** |
| G_brenca_TAF15_high_axon_guidance | GPL3290 | 10 | +0.1214 | [-0.4059, +0.4600] | 0.45998 | 26% | not distinguishable |
| PPARG_adipogenesis_process_proxy | GPL6244 | 189 | +0.0473 | [-0.0553, +0.0174] | 0.01735 | 2.73× | **SET-SPECIFIC** |
| PPARG_adipogenesis_process_proxy | GPL3290 | 176 | +0.2183 | [-0.0665, +0.1325] | 0.13251 | 1.65× | **SET-SPECIFIC** |
| PPARG_pparg_KO_DOWN | GPL6244 | 188 | +0.0003 | [-0.0548, +0.0173] | 0.0173 | 2% | not distinguishable |
| PPARG_pparg_KO_DOWN | GPL3290 | 157 | +0.2219 | [-0.0715, +0.1383] | 0.13828 | 1.60× | **SET-SPECIFIC** |
| PPARG_pparg_KO_UP_FALSIFIER | GPL6244 | 231 | -0.0536 | [-0.0527, +0.0143] | -0.05266 | 1.02× | **SET-SPECIFIC** |
| PPARG_pparg_KO_UP_FALSIFIER | GPL3290 | 196 | -0.1118 | [-0.0612, +0.1309] | -0.06123 | 1.83× | **SET-SPECIFIC** |
| PPARG_pparg_OE_UP | GPL6244 | 250 | -0.0238 | [-0.0507, +0.0122] | -0.05069 | 47% | not distinguishable |
| PPARG_pparg_OE_UP | GPL3290 | 230 | -0.0020 | [-0.0505, +0.1206] | -0.05054 | 4% | not distinguishable |
| PPARG_pparg_chip_chea | GPL6244 | 188 | +0.0800 | [-0.0548, +0.0173] | 0.0173 | 4.62× | **SET-SPECIFIC** |
| PPARG_pparg_chip_chea | GPL3290 | 169 | +0.2938 | [-0.0636, +0.1336] | 0.13357 | 2.20× | **SET-SPECIFIC** |
| PPARG_pparg_curated_trrust_human | GPL6244 | 63 | +0.0454 | [-0.0870, +0.0445] | 0.04448 | 1.02× | **SET-SPECIFIC** |
| PPARG_pparg_curated_trrust_human | GPL3290 | 57 | +0.1647 | [-0.1374, +0.2115] | 0.21148 | 78% | not distinguishable |

---

## S4 · The PPARγ receptor-activity reading, and its adipogenic ceiling

*PPARG* abundance in EMC is settled elsewhere and is not this work's subject. What no study retrieved
in the corpora searched here reports is receptor *activity* — transcriptional output, as distinct from
receptor abundance. This is a bounded statement about a search, not a claim that no such measurement
exists anywhere. Six gene sets were scored, each pinned to a verbatim Enrichr term with its species
read off the term rather than assumed, each null-calibrated on its own platform.

| arm | library / term | species | GPL6244 | GPL3290 |
|---|---|---|---|---|
| **ChEA ChIP-PET targets** (191) | `ChEA_2022` · PPARG 19300518 ChIP-PET 3T3-L1 Mouse | mouse | +0.080, p_emp ≤ 0.0005 → SET-SPECIFIC UP | +0.294, p_emp ≤ 0.0005 → SET-SPECIFIC UP |
| **KO_UP falsifier** (246) | `TF_Perturbations…` · PPARG DEFICIENCY MOUSE GSE23421 … UP | mouse | −0.054, p_emp 0.041 → SET-SPECIFIC DOWN | −0.112, p_emp 0.0035 → SET-SPECIFIC DOWN |
| **KO_DOWN** (206) | …PPARG DEFICIENCY MOUSE GSE23421 … DOWN | mouse | +0.0003 → not distinguishable | +0.222, p_emp ≤ 0.0005 → SET-SPECIFIC UP |
| **OE_UP** (269) | …PPARG OE MOUSE GSE10192 … UP | mouse | −0.024 → not distinguishable | −0.002 → not distinguishable |
| **TRRUST, human-curated** (66) | `TRRUST…2019` · PPARG human | human | +0.0454, p_emp 0.048 → SET-SPECIFIC UP | +0.1647 → not distinguishable |
| **adipogenesis process proxy** (200) | `MSigDB_Hallmark_2020` · Adipogenesis | unstated in the term | +0.047, p_emp ≤ 0.0005 → SET-SPECIFIC UP | +0.218, p_emp ≤ 0.0005 → SET-SPECIFIC UP |

**Why KO_DOWN and OE_UP cannot be expected to agree, measured rather than argued.** The two arms were
once read as disagreeing about biology, but they share 16 genes out of 206 and 269 (Jaccard 0.035) and
come from different experiments in different tissues. They are, for practical purposes, different gene
sets, and asking them to agree was asking two nearly disjoint lists of mouse genes to score alike in
human tumour tissue. Arithmetic control: KO_DOWN ∩ KO_UP = 0, exactly as the two arms of one knockout
experiment must be.

**What replicates, and how strongly.** The occupancy-derived target set is set-specific up on both
platforms and remains strongly significant under exact label permutation (p = 0.00033 and 0.00075).
The KO_UP falsifier is set-specific down on both platforms under the competitive null — but **it does
not reach significance under the permutation test on either** (p = 0.362 and 0.296), and it clears its
competitive threshold by only 1.02× on GPL6244. The falsifier half of the "two arms separating in
opposite directions" pattern therefore rests on the competitive null alone, and is reported at that
weight. Three of the six arms (KO_DOWN, OE_UP, TRRUST) were never permutation-tested at all, so their
verdicts rest on the competitive null only.

**The ceiling is not small.** The adipogenesis process proxy is also set-specific up on both platforms
and shares 44 genes with the ChEA arm (23% of the smaller set), the largest overlap in the table, and
it is itself significant under permutation on both platforms. PPARγ target output therefore cannot be
separated from an adipogenic differentiation component in these data, and five of the six arms are
mouse-derived. Stated at full honesty: PPARγ target genes are coordinately higher in EMC tumour tissue
than in comparator sarcomas, beyond a size-matched random set, on two platforms — and the same data
cannot distinguish that from an adipogenic differentiation programme. **This says nothing about the
direction of any pharmacological intervention on this axis.**

---

## S5 · Robustness, stratification and sensitivity

The stratified table below is the one that separates the three class-A genes. Read down each gene's
row: *ENO3* is within 0.011 SD of itself across five comparator sub-arms that share almost nothing,
and significant against every one; *SEMA3C* runs from +1.657 against low-grade fibromyxoid sarcoma to
−0.645 against desmoid fibromatosis, both significant, in opposite directions.

Note that the GPL3290 sub-arms have three comparators each, so **no p below 1/286 = 0.0035 is
reportable there however large the effect**; a value printed as 0.003497 is at that floor and is not a
smaller quantity than it appears.

The covariate-adjustment table carries its own internal control. The matrix panel separates the arms
on GPL6244 (Δ −0.518) and not on GPL3290 (Δ +0.006); a covariate that does not differ between arms
cannot move a contrast, and on GPL3290 none of the three genes moves by more than 3.5%. That is the
method behaving as it must, and it is the reason the GPL6244 movements can be read as adjustment
rather than as noise.

⛔ **The adjustment is a sensitivity analysis, not a correction.** If a panel gene is itself driven by
the fusion, the adjustment removes real signal. The provenance filter (main text §2.6) makes that
unlikely but does not exclude it, and no adjusted number in this document is "the real effect".

### TABLE S3 — robustness panel (exact permutation, BH, jackknife, rank re-read)

| row | kind | platform | Δ | exact p | BH q | jackknife: sign holds in every fit | rank re-read: same sign (p) |
|---|---|---|---:|---:|---:|---|---|
| ENO3 | gene | GPL6244 | +0.8074 | 7.3e-05 | 0.000438 | yes | yes (4.9e-05) |
| PPARG | gene | GPL6244 | +0.3071 | 0.0485 | 0.097 | yes | yes (0.059668) |
| SEMA3C | gene | GPL6244 | +0.7298 | 0.194266 | 0.233119 | yes | yes (0.067107) |
| NR4A3 | gene | GPL6244 | +0.7415 | 0.000184 | 0.000552 | yes | yes (0.000146) |
| PLAGL1 | gene | GPL6244 | -0.4234 | 0.082605 | 0.123908 | yes | yes (0.015936) |
| SGK1 | gene | GPL6244 | -0.1807 | 0.369002 | 0.369002 | yes | yes (0.445976) |
| A_plus_B_all_dna_binding | set | GPL6244 | +0.0403 | 0.517577 | — | yes | yes (0.36406) |
| B_native_nr4a3_dna_binding_targets | set | GPL6244 | -0.0675 | 0.225747 | — | yes | yes (0.137337) |
| D_filion_table1_emc_vs_137_sarcomas | set | GPL6244 | +1.1311 | 1e-06 | — | yes | yes (1e-06) |
| PPARG_pparg_chip_chea | set | GPL6244 | +0.0800 | 0.000327 | — | yes | yes (0.001238) |
| PPARG_pparg_KO_UP_FALSIFIER | set | GPL6244 | -0.0536 | 0.361899 | — | yes | yes (0.222558) |
| PPARG_adipogenesis_process_proxy | set | GPL6244 | +0.0473 | 0.034511 | — | yes | yes (0.037594) |
| ENO3 | gene | GPL3290 | +3.8113 | 0.000125 | 0.000625 | yes | yes (0.000125) |
| PPARG | gene | GPL3290 | +2.4809 | 0.000333 | 0.000833 | yes | yes (0.000333) |
| SEMA3C | gene | GPL3290 | +0.6228 | 0.16521 | 0.16521 | yes | yes (0.097777) |
| PLAGL1 | gene | GPL3290 | -2.1340 | 0.002331 | 0.003885 | yes | yes (0.008658) |
| SGK1 | gene | GPL3290 | +0.6156 | 0.155844 | 0.16521 | yes | yes (0.257867) |
| A_plus_B_all_dna_binding | set | GPL3290 | +0.3301 | 0.011114 | — | yes | yes (0.001499) |
| B_native_nr4a3_dna_binding_targets | set | GPL3290 | -0.1453 | 0.257493 | — | yes | yes (0.334915) |
| D_filion_table1_emc_vs_137_sarcomas | set | GPL3290 | +1.4783 | 0.0005 | — | yes | yes (0.000375) |
| PPARG_pparg_chip_chea | set | GPL3290 | +0.2938 | 0.000749 | — | yes | yes (0.000375) |
| PPARG_pparg_KO_UP_FALSIFIER | set | GPL3290 | -0.1118 | 0.296454 | — | yes | yes (0.084416) |
| PPARG_adipogenesis_process_proxy | set | GPL3290 | +0.2183 | 0.001499 | — | yes | yes (0.00025) |

### TABLE S4 — every stratified comparator contrast, with its own exact permutation p


**GPL6244** — comparator sub-arms: class_LGFMS_only (n=17), class_desmoid_fibromatosis_only (n=6), class_fibrosarcoma_only (n=6, whose GEO sample titles read *Myxofibrosarcoma*; the label is the
scoring module's bucket name and the samples are myxoid), myxoid_comparators_only (n=23), non_myxoid_comparators_only (n=6)

| gene | class LGFMS only | class desmoid fibromatosis only | class fibrosarcoma only | myxoid comparators only | non myxoid comparators only |
|---|---|---|---|---|---|
| *ENO3* | +0.805 (p 0.000168) | +0.807 (p 0.02165) | +0.816 (p 0.01082) | +0.808 (p 8e-05) | +0.807 (p 0.02165) |
| *PPARG* | +0.197 (p 0.2204) | +0.473 (p 0.04329) | +0.454 (p 0.06926) | +0.264 (p 0.1003) | +0.473 (p 0.04329) |
| *SEMA3C* | +1.657 (p 0.000119) | -0.645 (p 0.01515) | -0.523 (p 0.1364) | +1.089 (p 0.04609) | -0.645 (p 0.01515) |
| *NR4A3* | +0.839 (p 0.000158) | +0.837 (p 0.002165) | +0.370 (p 0.1255) | +0.717 (p 0.000568) | +0.837 (p 0.002165) |
| *PLAGL1* | -0.169 (p 0.4306) | -0.733 (p 0.04329) | -0.835 (p 0.06277) | -0.343 (p 0.1831) | -0.733 (p 0.04329) |
| *SGK1* | -0.032 (p 0.8796) | -0.167 (p 0.5173) | -0.617 (p 0.04762) | -0.184 (p 0.4055) | -0.167 (p 0.5173) |

**GPL3290** — comparator sub-arms: class_DFSP_only (n=3), class_GIST_only (n=3), non_myxoid_comparators_only (n=6), reference_pool_matched_only (n=3)

| gene | class DFSP only | class GIST only | non myxoid comparators only | reference pool matched only |
|---|---|---|---|---|
| *ENO3* | +3.515 (p 0.003497) | +4.107 (p 0.003497) | +3.811 (p 0.000125) | +3.515 (p 0.003497) |
| *PPARG* | +2.679 (p 0.003497) | — | +2.481 (p 0.000333) | +2.679 (p 0.003497) |
| *SEMA3C* | +0.113 (p 0.8427) | +1.133 (p 0.05944) | +0.623 (p 0.1652) | +0.113 (p 0.8427) |
| *NR4A3* | — | — | — | — |
| *PLAGL1* | -1.659 (p 0.04242) | -2.609 (p 0.006061) | -2.134 (p 0.002331) | -1.659 (p 0.04242) |
| *SGK1* | -0.198 (p 0.5804) | +1.429 (p 0.01399) | +0.616 (p 0.1558) | -0.198 (p 0.5804) |

### TABLE S5 — covariate-adjusted sensitivity

| platform | panel | arm separation Δ | gene | raw Δ | adjusted Δ | fraction retained | r(gene, proxy) |
|---|---|---:|---|---:|---:|---:|---:|
| GPL6244 | matrix (11) | -0.5184 | *ENO3* | +0.8074 | +0.6083 | 0.753 | -0.368 |
| GPL6244 | matrix (11) | -0.5184 | *PPARG* | +0.3071 | +0.0992 | 0.323 | -0.4798 |
| GPL6244 | matrix (11) | -0.5184 | *SEMA3C* | +0.7298 | +1.2458 | 1.707 | 0.3354 |
| GPL6244 | vascular (3) | -0.4057 | *ENO3* | +0.8074 | +0.6294 | 0.78 | -0.3236 |
| GPL6244 | vascular (3) | -0.4057 | *PPARG* | +0.3071 | +0.0917 | 0.299 | -0.489 |
| GPL6244 | vascular (3) | -0.4057 | *SEMA3C* | +0.7298 | +1.3789 | 1.889 | 0.4152 |
| GPL3290 | matrix (11) | +0.0064 | *ENO3* | +3.8113 | +3.8123 | 1.0 | -0.036 |
| GPL3290 | matrix (11) | +0.0064 | *PPARG* | +2.4809 | +2.3939 | 0.965 | -0.2575 |
| GPL3290 | matrix (11) | +0.0064 | *SEMA3C* | +0.6228 | +0.6148 | 0.987 | 0.6605 |
| GPL3290 | vascular (3) | -0.7962 | *ENO3* | +3.8113 | +2.2190 | 0.582 | -0.5888 |
| GPL3290 | vascular (3) | -0.7962 | *PPARG* | +2.4809 | +1.0323 | 0.416 | -0.7026 |
| GPL3290 | vascular (3) | -0.7962 | *SEMA3C* | +0.6228 | +0.5283 | 0.848 | -0.0809 |

### TABLE S6 — the skeletal-muscle admixture control (GPL6244)

| gene | muscle-marker? | mean percentile in the 2 pooled muscle samples | EMC | comparators | EMC − comparator |
|---|---|---:|---:|---:|---:|
| *ACTA1* | yes | 1.000 | 0.721 | 0.778 | -0.057 |
| *MYH7* | yes | 1.000 | 0.479 | 0.522 | -0.043 |
| *PYGM* | yes | 0.999 | 0.604 | 0.462 | +0.142 |
| *MYL1* | yes | 0.998 | 0.133 | 0.283 | -0.150 |
| *ENO3* | no (class-A target) | 0.996 | 0.663 | 0.348 | +0.315 |
| *SEMA3C* | no (class-A target) | 0.924 | 0.945 | 0.685 | +0.260 |
| *PPARG* | no (class-A target) | 0.381 | 0.707 | 0.591 | +0.116 |

---

## S6 · The NBRE motif scan — full parameters

**Window.** −10 kb/+15 kb around each gene's Ensembl-canonical TSS. The window is asymmetric, was
fixed in advance on published regulatory architecture, and was frozen **before any sequence was
read** rather than chosen around a result. A distal element outside it is untested by construction.

**Motifs.** The exact NBRE, 5′-AAAGGTCA-3′ (PMID 1902986), and the NurRE (PMID 9315667), scanned on
both strands with hits de-duplicated by genomic position so a palindromic match cannot be counted
twice. **No NurRE occurs in any focus window.**

**Two independent nulls, because an 8-mer occurs in 25 kb by chance.** (i) A
**dinucleotide-preserving shuffle** of the same window — 2,000 shuffles, seeded — which holds base
and dinucleotide composition, and therefore GC and CpG content, exactly. (ii) A **background panel**
of 198 other genes' windows, read raw and additionally restricted to a GC-matched subset (±0.05). The
panel is a gene list this project had already assembled for an unrelated question, so it cannot have
been chosen to flatter or damage any gene here. It averages **1.15 exact NBREs per 25 kb window**, so
a single hit is what an arbitrary window contains anyway. Sequences are cached, so the scan
re-derives offline.

| gene | exact NBRE | shuffle-null p | background-panel p | GC-matched p |
|---|---:|---:|---:|---:|
| ***ENO3*** | **4** | **0.034** | **0.025** | **0.018** |
| ***PPARG*** | 3 | 0.227 | 0.131 | 0.209 |
| ***SEMA3C*** | **0** | 1.00 | 1.00 | 1.00 |
| *NR4A3* | 0 | 1.00 | 1.00 | 1.00 |
| *NR4A1* | 0 | 1.00 | 1.00 | 1.00 |

**The one-mismatch (NBRE-like) class.** Brenca *et al.* report a predicted NBRE-*like* site at
*SEMA3C*, which by construction is not an exact NBRE, so the exact scan is not a test of their claim.
Octamers matching the NBRE with **at most one substitution** were therefore scanned with their own
null, taken from the *same* shuffled sequences so every exact figure is unchanged. *SEMA3C*'s window
carries **39** one-mismatch sites, the most of any gene scanned — and that is **what its own
composition predicts**: null mean 33.7, p = 0.203 against the dinucleotide-preserving shuffle, and
p = 0.118 GC-matched. Only the composition-naive raw panel rank suggests enrichment (p = 0.040), and
*SEMA3C*'s window is the most AT-rich of the set (GC 0.371) while the NBRE itself is AT-leaning —
which is exactly the artefact GC-matching exists to remove. The converse holds for *ENO3*: its
one-mismatch count is *not* enriched (28 against a null mean of 25.6, p = 0.336), so its signal sits
in exact NBREs rather than in degenerate ones.

⛔ **A one-mismatch match is a weaker claim than an exact NBRE, not a stronger one**: it admits many
sequences per position, most of which no NR4A protein has been shown to bind. The calibration bounds
a count; it does not license calling any hit a site.

⛔ **The hit positions do not reproduce the published coordinates.** Kim *et al.* report two NBREs
upstream of the *ENO3* TSS; this scan finds one upstream (−8.7 kb) and three downstream. Filion
*et al.* report a perfect NBRE at −675 bp of *PPARG*; the nearest hit here is −186. Both papers
numbered from their own promoter constructs, and *PPARG* has multiple promoters, so the offsets are
not directly comparable. **This scan neither confirms nor refutes the published site positions**, and
a motif scan cannot refute a measured binding event at a named locus in any case.

---

## S7 · The cohort search — every query, and every record it returned

Main-text §2.7 gives the method and §3.13 Table 10 the result. This section carries the queries
verbatim, because a search reported only by its conclusion cannot be checked or repeated.

**Table S7. The six queries, with the reason each was included.**

| # | query (NCBI E-utilities, `db=gds`) | why | as written | repaired |
|---|---|---|---|---|
| 1 | `"extraskeletal myxoid chondrosarcoma"[All Fields]` | the disease name in full — highest precision | **17** | — |
| 2 | `"myxoid chondrosarcoma"[All Fields] AND "expression profiling"[Filter]` | the shortened name, restricted to expression series | 0 ⚠ | **2** |
| 3 | `(EWSR1 AND NR4A3) OR "EWS-NOR1" OR "EWSR1-NR4A3" OR "TAF15-NR4A3"` | the fusion rather than the disease — catches a deposit indexed by its driver | **5** | — |
| 4 | `NR4A3[All Fields] AND sarcoma[All Fields] AND "expression profiling"[Filter]` | the 3′ partner plus lineage, for a deposit naming *NR4A3* but not EMC | 0 | **0** — a confirmed zero |
| 5 | `"chondrosarcoma"[All Fields] AND "expression profiling"[Filter] AND "Homo sapiens"[Organism]` | deliberately over-broad: EMC samples inside a general chondrosarcoma series | 0 ⚠ | **4** |
| 6 | `sarcoma[All Fields] AND "translocation"[All Fields] AND "expression profiling"[Filter]` | translocation-sarcoma panels, the kind of deposit EMC hides inside | 0 ⚠ | **32** |

All six executed and none returned an error. The counts are each query's own raw return and sum to
60; the 56 records in §3.13 are what remains after de-duplication across the six, so a deposit
returned by two queries is counted once there and twice here.

⚠ **Four queries first returned exactly zero, and that was a reading about the queries before it was
a reading about GEO.** All four carry an `"expression profiling"[Filter]` clause; the two that
returned records do not. Query 5 asks GEO for human chondrosarcoma expression series — a question it
cannot honestly answer with nothing. **A zero and a malformed query are the same length**, and
reported as "six queries, no fourth cohort" this would have made the negative sound materially
stronger than the evidence supported.

**The repair, and what it changed.** A zero-returning query carrying a field restriction is re-asked
with the restriction lifted and the search terms unchanged; records from the repaired form are used
and the query is recorded as `read_after_syntax_repair`. Three of the four then returned records —
**2, 4 and 32** — taking the search from 7 series to **22** and from 22 records to **56**. Query 6,
the translocation-sarcoma panel query written precisely because it is the kind of deposit EMC hides
inside, accounted for 32 of them on its own. **Query 4 returned zero again under the unrestricted
re-ask and is the only zero in this table read as an absence.** Both forms and both counts are in
`emc-cohort-search-inputs.json`.

⛔ **The negative reported in Table 10 is the repaired search.** The unrepaired one would have rested
on two queries while presenting itself as six, and the seventeen sample-level zeros that give the
negative its weight would not have existed — fifteen of those deposits arrived through the repaired
queries.

**What the search declines to conclude, and one way it reaches further than expected.** GEO's
`esearch` matches the text of a record, so a deposit that names the disease nowhere in its GEO
metadata is invisible to every query above however many EMC samples it holds. That bound is real and
is the reason this is a statement about reach rather than existence.

⭐ **But the index reaches past the series title and summary, which the returned records demonstrate
directly.** Neither GSE43632 (*Large scale screening for fusion genes in sarcoma patient samples*) nor
GSE80126 carries an EMC token in its title or its summary — and query 1, the full disease name under
`[All Fields]`, returned both. `[All Fields]` therefore indexes text this module never captured, which
is exactly the "EMC hiding inside a generically titled pan-sarcoma deposit" case that queries 4–6 were
written to cover and, being malformed, did not. Both were then read at sample level and carry no EMC
sample. The coverage the broken queries were meant to provide was, in this instance, supplied by query
1 — which is a fortunate accident and not a design, and is recorded as such.

**Records excluded for not being deposits.** `db=gds` returns sample and platform records alongside
series, and most of what came back was neither. Of the 56 records: **21 series**, 1 curated dataset
(GDS3481), **30 individual sample records** and **4 platform records**. Ten of the 30 samples are
samples of the three cohorts already analysed here — six EMC samples of GSE24369 and the four of the
Brunner deposit, returned in their own right by the disease-name query — and two are the
doxycycline-treated and untreated HEK293 samples of GSE11185. A single sample is not a cohort and a
platform is not a deposit; grading them as though they might be would bury the records that need a
decision under records that never could.

**Reproduction.** `research/modalities/emc_cohort_search.py` → `emc-cohort-search.json`, with the raw
query record in `emc-cohort-search-inputs.json`. The derive half runs offline from the cached queries
and `--check` re-derives the verdict and diffs it against the committed artifact.

---

## S8 · The Haller NR4A3 cistrome — how its genome build was determined

Main-text §3.11 and Table 9 report four deep NR4A3 peak sets from Haller *et al.* (Zenodo
10.5281/zenodo.1483691). This section records how they became usable, because the step is not
routine and a reader should be able to reject it.

**The problem.** A BED file carries no genome build. The deposit names none in its title, its
description or its filenames, and the two candidate human builds differ by a large, position-dependent
offset — on chr10, roughly 300 kb near *RET*. An intersection performed on the wrong build does not
fail: it returns a plausible number for a different locus. This analysis therefore refuses to intersect
any peak set whose build is unknown, and these four arrived in exactly that state.

**The test.** H3K4me3 marks active promoters. The deposit includes an H3K4me3 peak set for each of the
four samples, so on the correct build those peaks must recover most of a promoter panel — and on the
wrong build they must not. The panel used is the same 198-gene background panel every count in Table 9
is calibrated against, assembled for an unrelated question and never chosen with reference to these
data.

**Table S8. Promoter recovery of each H3K4me3 peak set, by candidate build.**

| sample | peaks | panel promoters recovered, hg19 | hg38 |
|---|---:|---:|---:|
| AciCC-1 | 30,660 | **90.6%** | 33.6% |
| AciCC-2 | 30,532 | **92.5%** | 32.2% |
| AciCC-3 | 29,494 | **92.5%** | 33.2% |
| Normal parotid gland | 28,407 | **93.9%** | 32.7% |

The deposit is read as **hg19**, on a worst-case recovery of 0.906 against 0.322, a ratio of 2.81.

**Why two thresholds and not one.** A build is assigned only if the worst sample clears an absolute
floor (0.80) *and* beats the runner-up by a ratio (2.0). The ratio alone would accept two equally wrong
builds; the absolute alone would accept a build on which peaks happen to be broadly distributed.
⚠ **The 33% on hg38 is not noise** — the two builds are identical over much of the genome, so a
substantial wrong-build recovery is expected, and a test that treated "it found some" as agreement
would pass on either.

**What the reader can check, and what would overturn it.** Four biological samples agree independently,
which a coordinate error affecting one file would not produce; the mark used is the one with the
strongest prior expectation of promoter localisation, and no transcription factor was used, because a
factor that genuinely avoided promoters would mimic the wrong build; and the panel is the same one the
occupancy calibration uses, so an error in it degrades the build call and the occupancy nulls together
rather than silently favouring one build. **If the deposit is in fact hg38, every Table 9 row from it is
void** — the class-A counts would refer to other loci — while the ChIP-Atlas and ReMap rows, whose
builds come from their catalogues, are unaffected. Nothing else in the manuscript depends on it.

**Reproduction.** `python3 research/modalities/emc_ret_cistrome.py --infer-builds`, offline, from the
committed peak cache; the full per-build table is written to `emc-ret-cistrome-inputs.json` under
`build_inference`.
