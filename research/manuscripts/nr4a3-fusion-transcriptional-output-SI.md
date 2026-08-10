---
id: DOC-NR4A3-FUSION-TRANSCRIPTIONAL-OUTPUT-SI
title: "Supplementary Information, the direct-target catalogue of EWSR1::NR4A3 across three EMC cohorts"
level: L3
kind: manuscript
status: live
canonical_for: ["the full 22-row evidence-typed NR4A3 target catalogue with verbatim sentences", "the complete set-score, robustness, stratified-comparator and covariate-adjustment tables for the EMC transcriptional-output reading", "the PPARγ receptor-activity reading and its adipogenic ceiling", "the sensitivity analyses of the size-matched empirical null used by the EMC transcriptional-output manuscript"]
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
date: 2026-08-10
last_verified: 2026-08-10
---

# Supplementary Information

**For:** *The published direct-target catalogue of the EWSR1::NR4A3 fusion is three genes wide, and
none is separable from disease association in the available EMC expression record.*

Every table here is generated from a committed artifact and is not re-typed from prose; the producers
are listed in the main text's Data and code availability section. Section numbers below are
referenced from the main text as §S1–§S11.

---

## S1 · Method detail

### S1.1 · Probe mapping and floors

Probes were mapped to gene symbols per platform. GPL6244: 20,230 of 28,459 probes carry a symbol,
giving 18,694 distinct symbols. GPL3290: 27,203 of 43,008 spots resolve through an EST-accession
bridge to 14,932 distinct symbols, so a gene unreadable on GPL3290 may be absent from the bridge
rather than from the array, and is recorded as unread rather than as absent.

Each sample's values are z-scored against that array's own probe distribution, so a per-sample score
is a within-array quantity. A gene score for a sample is its mean z over the probes mapping to it; a
set score is the mean over the set's readable members. Floors: **three samples per group** for any
contrast, and four genes and 0.4 coverage for any set score. A set below the floor emits no
number and says so, which is why class A, at three genes, is never scored as a set.

### S1.2 · The circularity grade

Whether GSE4303 is the Subramanian (2005) cohort was graded from the fetched GEO series record,
never from sample counts: the record's title, summary, contributors and linked PubMed identifier
were read verbatim. If the record names PMID 15920699 or Subramanian, the verdict is circular; if
it does not, the verdict is *not-clean* rather than clean, the absence of a name is not evidence of
independence; if the record could not be read at all, the verdict is *unanswered*. The record does
name both, so the verdict is circular, which is what makes both the set-E score and the *PPARG* gene
row on that platform non-independent (main text §3.8).

### S1.3 · The pre-registered decision rule, and how it landed

A six-branch decision rule was written and committed while the measurement run was still executing,
so the verdict could not be fitted to whatever came back. Each branch carried its sentence, its
ceiling and its next step in advance.

| # | outcome | what it licenses |
|---|---|---|
| A | *ENO3* reproduces and class A (or A+B) clears its null on both platforms and *PLAGL1* reads down | A positive, EMC-specific result, with the ceiling attached in the same paragraph. |
| B | *ENO3* reproduces, class A clears its null on one platform only | A single-platform observation, reported as one. |
| C | *ENO3* reproduces, nothing clears its null | Still a result: the published target set is not distinguishable from a size-matched random gene set. |
| D | *ENO3* does not reproduce | Report the instrument and stop. No biological sentence may be written. |
| E | *ENO3* reproduces but *PLAGL1* reads up | Every up row loses its strongest defence against the offset explanation. |
| F | Filion Table 1 clears its null but class A does not | The instrument reads EMC and the fusion-target set is the thing that is flat. |

**Outcome F came true**, with a per-gene positive inside it that the rule did not anticipate. Two
limits of the pre-registration are recorded rather than quietly rewritten. First, the branches were
written over *set* scores and the measurement landed at the *gene* level, so a future version of this
rule needs an explicit gene-level branch. Second, the rule did not anticipate that the per-gene
result would itself be split by a later confound audit; *ENO3* surviving every stratification while
*SEMA3C* reverses sign, so it had no branch for "the genes disagree with each other", which is what
happened.

---

## S2 · The complete evidence-typed catalogue, and the citation-share probe

Class assignments are from the main text Table 1. The verbatim sentence each classification rests
on is held in the machine-readable catalogue (`nr4a3_fusion_targets.py` `LITERATURE_TARGETS`,
emitted to `nr4a3-fusion-targets.json` `evidence_table.rows[].verbatim`) and is not reproduced here
only for length; every row below carries its citation and the assay the classification rests on.

### S2.1 · The citation-share probe

Main-text §1.2 reports how often the three class-A genes and their sources are named. The committed
probe (Europe PMC, 2026-08-08) gives, per source: the number of citing records overall, the number
that are EMC records, and the number that are EMC reviews.

| source | gene | citing records | citing EMC records | share | citing EMC reviews |
|---|---|---:|---:|---:|---:|
| Filion *et al.* 2009 (PMID 18855877) | *PPARG* | 52 | 22 | 42% | 4 |
| Subramanian *et al.* 2005 (PMID 15920699) | cohort | 50 | 27 | 54% | 6 |
| Kim *et al.* 2016 (PMID 26310886) | *ENO3* | 12 | 4 | 33% | 0 |
| Brenca *et al.* 2019 (PMID 31020999) | *SEMA3C* | query returned no count | 19 | not computable | 5 |

Brenca's total-citation query executed and returned no count, so no share can be computed for it
and no upper bound of the range may be quoted. Kim *et al.*, the source of the one gene that survives
every test in the main text, is the source with the thinnest profile: 12 citing records and no citing
EMC review.

A published negative control accompanies the catalogue: ***CALD1***, whose promoter was searched for
NOR-1 response elements in the same experiment that found the *SMPX* site, and none were found
(PMID 27181368). It controls the inference "this gene moved, therefore NR4A3 bound it", not EMC
biology.

**Table S1. The complete evidence-typed catalogue**

| gene | class | factor actually tested | assays | cell system | species | expected in EMC | citation |
|---|---|---|---|---|---|---|---|
| ENO3 | A | TFG::NR4A3 (TFG-TEC) | EMSA, ChIP (endogenous promoter), luciferase reporter, two NGFI-B response element motifs upstream of the putative TSS, ChIP for histone H3 acetylation at the endogenous promoter | cultured cell lines over-expressing TFG-TEC (the t(3;9) EMC fusion variant) | human (human beta-enolase promoter) | UP | Kim AY, Lim B, Choi J, Kim J. The TFG-TEC oncoprotein induces transcriptional activation of the human beta-enolase gene via chromatin modification of the promoter region. Mol Carcinog 2016. PMID 26310886, doi 10.1002/mc.22384 |
| PPARG | A | EWSR1::NR4A3, NR4A3 (native), NR4A3-deltaC (native truncated) | predicted perfect NBRE at -675 bp (5' AAAGGTCA 3'), band-shift (EMSA) with the fusion protein, 2.8 kb human PPARG isoform-1 promoter luciferase reporter, single-nucleotide NBRE mutant of that reporter | CFK2 fetal RAT chondrogenic cells, stable EWSR1/NR4A3 lines (et2, et16, et19) and transient transfection of wild-type CFK2; HUMAN PPARG promoter construct | rat (the promoter construct is human) | UP | Filion C, Motoi T, Olshen AB, et al. The EWSR1/NR4A3 fusion protein of extraskeletal myxoid chondrosarcoma activates the PPARG nuclear receptor gene. J Pathol 2009;217(1):83-93. PMID 18855877, PMCID PMC4429309, doi 10.1002/path.2445 |
| SEMA3C | A | EWSR1::NR4A3, TAF15::NR4A3, NR4A3 (native) | in-silico NBRE-like site (MatInspector, GRCh38 chr7), chromatin affinity purification + target qPCR (ChAP-qPCR), Strep-tagged | tBJ/ER transformed HUMAN fibroblasts engineered to express Strep-tagged NR4A3, EWSR1-NR4A3 (E-N) or TAF15-NR4A3 (T-N) | human | UP | Brenca M, Stacchiotti S, Fassetta K, et al. NR4A3 fusion proteins trigger an axon guidance switch that marks the difference between EWSR1 and TAF15 translocated extraskeletal myxoid chondrosarcomas. J Pathol 2019;249(1):90-101. PMID 31020999, PMCID PMC6766969, doi 10.1002/path.5284 |
| BIRC3 | B2 | NR4A3 (native) | NBRE binding site | vascular smooth muscle cells / hypoxic endothelium | human/rodent vascular | UP | Reviewed in PMCID PMC6912296 and PMC8583700 |
| CCND1 | B2 | NR4A3 (native) | ChIP at the Cyclin D1 promoter, NBRE site | hepatocytes; vascular smooth muscle cells; guidewire arterial-injury model in NOR-1-deficient mice | mouse / rat vascular and hepatic cells | UP | Reviewed in Herring JA, Elison WS, Tessem JS. Function of Nr4a Orphan Nuclear Receptors in Proliferation, Apoptosis and Fuel Utilization Across Tissues. Cells 2019;8:1373. PMID 31683815, PMCID PMC6912296; and in Haller F, et al. Nat Commun 2019;10:368. PMID 30664630, PMCID PMC6341107 |
| CDKN2AIP | B1 | NR4A3 (native) | ChIP at predicted sites in the CDKN2AIP promoter, luciferase reporter reversed by promoter mutant | MHCC-LM3 human hepatocellular carcinoma cells | human | UP | Zhao X, Min X, Wang Z, et al. NR4A3 inhibits the tumor progression of hepatocellular carcinoma by inducing cell cycle G0/G1 phase arrest and upregulation of CDKN2AIP expression. Int J Biol Sci 2024. PMID 39664575, PMCID PMC11628324, doi 10.7150/ijbs.95174 |
| COX5A | B1 | NR4A3 (native) | Cut&Tag over the promoter, dual-luciferase reporter | neonatal mouse cardiomyocytes; HEK293T reporter | mouse; human reporter construct | UP | Peng H, et al. eBioMedicine 2024;106:105268. PMID 39098108, PMCID PMC11334830 |
| GLS2 | B1 | NR4A3 (native) | ChIP-seq + mRNA-seq, dual-luciferase reporter, abolished by mutation of the predicted NR4A3 motif | Schwann cells (diabetic peripheral neuropathy model) | rat/mouse Schwann cells | UP | Pang B, Chen S, Bai Y, Zhang Y, Wang Z. NR4A3 alleviates diabetic neuropathy via GLS2-mediated mitochondrial repair and Schwann cell differentiation. iScience 2026. PMID 42028030, PMCID PMC13099357, doi 10.1016/j.isci.2026.115515 |
| ICAM1 | B2 | NR4A3 (native) | binding to the NBRE consensus site | TNF-stimulated endothelial cells / monocyte adhesion | human endothelial | UP | Reviewed in PMCID PMC8583700 / PMC10088923 / PMC9100886 |
| LOXL2 | B2 | NR4A3 (native) | named a direct NOR-1 target gene in the source review | cardiac fibroblast-to-myofibroblast switch, NOR-1 transgenic mice | mouse | UP | Reviewed in Martinez-Gonzalez J, et al. Int J Mol Sci 2021;22:11371, PMCID PMC8583700 |
| MYH7 | B2 | NR4A3 (native) | named a direct NOR-1 target gene in the source review | cardiac hypertrophy, NOR-1 transgenic mice | mouse | UP | Reviewed in PMCID PMC8583700 |
| NOX1 | B2 | NR4A3 (native) | gene silencing, luciferase reporter, site-directed mutagenesis, EMSA | vascular smooth muscle cells; co-localisation in human atheroma | human | UP | Reviewed in Martinez-Gonzalez J, et al. Int J Mol Sci 2021;22:11371, PMCID PMC8583700 |
| PDP1 | B1 | NR4A3 (native) | Cut&Tag over the promoter | neonatal mouse cardiomyocytes | mouse | UP | Peng H, et al. eBioMedicine 2024;106:105268. PMID 39098108, PMCID PMC11334830 |
| SDHA | B1 | NR4A3 (native) | Cut&Tag, truncated-promoter dual-luciferase mapping to region R3 (predicted element AAAGTCAC) | neonatal mouse cardiomyocytes; HEK293T for the HUMAN SDHA promoter reporter | mouse cardiomyocytes; human HEK293T for the reporter | UP | Peng H, Yuan J, Wang Z, et al. NR4A3 prevents diabetes induced atrial cardiomyopathy by maintaining mitochondrial energy metabolism and reducing oxidative stress. eBioMedicine 2024;106:105268. PMID 39098108, PMCID PMC11334830, doi 10.1016/j.ebiom.2024.105268 |
| SKP2 | B2 | NR4A3 (native) | EMSA, ChIP, NBRE site in the SKP2 promoter | vascular smooth muscle cells | human/rodent VSMC (the review does not disambiguate) | UP | Reviewed in Martinez-Gonzalez J, et al. NR4A3: A Key Nuclear Receptor in Vascular Biology, Cardiovascular Remodeling, and Beyond. Int J Mol Sci 2021;22:11371. PMID 34768801, PMCID PMC8583700 |
| SMPX | B1 | NR4A3 (native) | promoter deletion, site-directed mutagenesis of a non-consensus NBRE (-167/-160), EMSA, ChIP in differentiating human skeletal myoblasts | human vascular smooth muscle cells and HSMM myoblasts | human | UP | Ferran B, Marti-Pamies I, Alonso J, et al. The nuclear receptor NOR-1 regulates the small muscle protein, X-linked (SMPX) and myotube differentiation. Sci Rep 2016;6:25944. PMID 27181368, PMCID PMC4867575 |
| TH | B2 | NR4A3 (native) | transient transfection through an NBRE site in the TH promoter | vascular smooth muscle cells; NOR-1 transgenic mouse aorta | mouse / VSMC | UP | Reviewed in Martinez-Gonzalez J, et al. Int J Mol Sci 2021;22:11371, PMCID PMC8583700 |
| VCAM1 | B2 | NR4A3 (native) | binding to the NBRE consensus site | TNF-stimulated endothelial cells / monocyte adhesion | human endothelial | UP | Reviewed in Martinez-Gonzalez J, et al. Int J Mol Sci 2021;22:11371, PMCID PMC8583700; and PMCID PMC10088923 |
| VTN | B2 | NR4A3 (native) | listed by an independent review as a functionally validated direct target, over-expression + blocking-antibody / silencing rescue of migration, co-localisation in human atherosclerotic lesions | vascular smooth muscle cells; independently raised >2-fold by NR4A3 over-expression in the human MHCC-LM3 hepatocellular line | human | UP | Haller F, et al. Nat Commun 2019;10:368. PMID 30664630, PMCID PMC6341107 (target list); Martinez-Gonzalez J, et al. Int J Mol Sci 2021;22:11371, PMCID PMC8583700 (VSMC); Zhao X, et al. Int J Biol Sci 2024, PMCID PMC11628324 (MHCC-LM3) |
| PLAGL1 | C | EWSR1::NR4A3 | differential display in a fusion-expressing line, RT-PCR in six EMC tumours | CFK2 chondrogenic cells over-expressing EWS/NOR1; human EMC tumours vs immortalised and primary human chondrocytes | rat cells; human tumours | DOWN | Filion C, et al. The PLAGL1 gene is down-regulated in human extraskeletal myxoid chondrosarcoma tumors. Cancer Lett 2005. PMID 16112421, doi 10.1016/j.canlet.2004.12.007 |
| SGK1 | C | EWSR1::NR4A3 | differential display in a tetracycline-regulated fusion line, co-immunocytochemistry, immunohistochemistry in 10 fusion-positive EMC | CFK2 fetal RAT chondrogenic cells with tetracycline-controlled EWS/NOR1 | rat | FLAT_OR_DOWN_AT_TRANSCRIPT_LEVEL | Labelle Y, et al. Serum- and glucocorticoid-regulated kinase 1 (SGK1) induction by the EWS/NOR1(NR4A3) fusion protein. Biochem Biophys Res Commun 2006. PMID 16756948, doi 10.1016/j.bbrc.2006.05.134 |
| NDRG2 | D | [] | Affymetrix U133A microarray, 3 fusion-positive EMC vs 137 other sarcomas, Western blot, immunohistochemistry in 9/9 EWSR1/NR4A3-positive EMC | human EMC tumour tissue | human | UP | Filion C, et al. J Pathol 2009;217(1):83-93. PMID 18855877, PMCID PMC4429309 |

---

## S3 · Scored gene sets and sensitivity analyses of the null

The threshold column is the value the observed delta had to exceed to fall outside the 95% band
of its own size-matched null; **reached** expresses the observed delta as a fraction of it (below 1)
or a multiple of it (at or above 1). The inflated column applies the inter-gene correlation
correction of main-text §2.3.2: ρ̄ is the mean pairwise correlation between member genes' per-sample
z after centring each gene within each arm, the variance inflation factor is 1 + (n−1)ρ̄, and the
inflated threshold is the uninflated one times its square root.

Two rows deserve caution because they clear the uninflated threshold only barely: the PPARγ KO_UP
falsifier on GPL6244 (1.02×) and the TRRUST human-curated arm on GPL6244 (1.02×). Neither clears its
inflated threshold, and the main text does not lean on either. Set E is circular on GPL3290 (§S1.2)
and is reported for completeness only.

**Table S2. Every scored gene set, with its detectability threshold and its inflated counterpart**

| set | platform | n requested / readable | Δ | null 95% band | reached | inter-gene correlation | verdict |
|---|---|---:|---:|---|---:|---|---|
| A fusion dna binding targets | GPL6244 | 3 / 3 |, |, |, |, | no score (below floor) |
| A fusion dna binding targets | GPL3290 | 3 / 3 |, |, |, |, | no score (below floor) |
| A plus B all dna binding | GPL6244 | 19 / 19 | +0.0403 | [-0.1418, +0.1047] | 39% | ρ̄ +0.1044, VIF 2.88, 23% | not distinguishable |
| A plus B all dna binding | GPL3290 | 19 / 17 | +0.3301 | [-0.2972, +0.3765] | 88% | ρ̄ +0.0372, VIF 1.596, 69% | not distinguishable |
| B native nr4a3 dna binding targets | GPL6244 | 16 / 16 | -0.0675 | [-0.1568, +0.1142] | 43% | ρ̄ +0.1334, VIF 3.002, 25% | not distinguishable |
| B native nr4a3 dna binding targets | GPL3290 | 16 / 14 | -0.1453 | [-0.3357, +0.3971] | 43% | ρ̄ +0.0186, VIF 1.242, 39% | not distinguishable |
| C fusion expression only | GPL6244 | 2 / 2 |, |, |, |, | no score (below floor) |
| C fusion expression only | GPL3290 | 2 / 2 |, |, |, |, | no score (below floor) |
| D filion table1 emc vs 137 sarcomas | GPL6244 | 21 / 21 | +1.1311 | [-0.1374, +0.0947] | 11.94× | ρ̄ +0.1286, VIF 3.572, 6.32× | SET-SPECIFIC |
| D filion table1 emc vs 137 sarcomas | GPL3290 | 21 / 18 | +1.4783 | [-0.2853, +0.3481] | 4.25× | ρ̄ +0.1335, VIF 3.27, 2.35× | SET-SPECIFIC |
| E filion table2 overlap with subramanian | GPL6244 | 20 / 20 | +0.8932 | [-0.1399, +0.0978] | 9.13× | ρ̄ +0.2770, VIF 6.263, 3.65× | SET-SPECIFIC |
| E filion table2 overlap with subramanian | GPL3290 | 20 / 18 | +1.9850 | [-0.2853, +0.3481] | 5.70× | ρ̄ +0.1388, VIF 3.36, 3.11× | SET-SPECIFIC |
| F brenca EWSR1 high axon guidance | GPL6244 | 3 / 3 |, |, |, |, | no score (below floor) |
| F brenca EWSR1 high axon guidance | GPL3290 | 3 / 3 |, |, |, |, | no score (below floor) |
| G brenca TAF15 high axon guidance | GPL6244 | 10 / 10 | -0.4975 | [-0.1957, +0.1460] | 2.54× | ρ̄ +0.0154, VIF 1.139, 2.38× | SET-SPECIFIC |
| G brenca TAF15 high axon guidance | GPL3290 | 10 / 10 | +0.1214 | [-0.4059, +0.4600] | 26% | ρ̄ +0.1343, VIF 2.209, 18% | not distinguishable |
| PPARG adipogenesis process proxy | GPL6244 | 200 / 189 | +0.0473 | [-0.0553, +0.0174] | 2.73× | ρ̄ +0.4948, VIF 94.015, 28% | SET-SPECIFIC |
| PPARG adipogenesis process proxy | GPL3290 | 200 / 176 | +0.2183 | [-0.0665, +0.1325] | 1.65× | ρ̄ +0.0578, VIF 11.107, 49% | SET-SPECIFIC |
| PPARG pparg KO DOWN | GPL6244 | 206 / 188 | +0.0003 | [-0.0548, +0.0173] | 2% | ρ̄ +0.0381, VIF 8.132, 1% | not distinguishable |
| PPARG pparg KO DOWN | GPL3290 | 206 / 157 | +0.2219 | [-0.0715, +0.1383] | 1.60× | ρ̄ +0.0330, VIF 6.148, 65% | SET-SPECIFIC |
| PPARG pparg KO UP FALSIFIER | GPL6244 | 246 / 231 | -0.0536 | [-0.0527, +0.0143] | 1.02× | ρ̄ +0.0645, VIF 15.844, 26% | SET-SPECIFIC |
| PPARG pparg KO UP FALSIFIER | GPL3290 | 246 / 196 | -0.1118 | [-0.0612, +0.1309] | 1.83× | ρ̄ +0.0605, VIF 12.804, 51% | SET-SPECIFIC |
| PPARG pparg OE UP | GPL6244 | 269 / 250 | -0.0238 | [-0.0507, +0.0122] | 47% | ρ̄ +0.0999, VIF 25.885, 9% | not distinguishable |
| PPARG pparg OE UP | GPL3290 | 269 / 230 | -0.0020 | [-0.0505, +0.1206] | 4% | ρ̄ +0.0236, VIF 6.408, 2% | not distinguishable |
| PPARG pparg chip chea | GPL6244 | 191 / 188 | +0.0800 | [-0.0548, +0.0173] | 4.62× | ρ̄ +0.3126, VIF 59.449, 60% | SET-SPECIFIC |
| PPARG pparg chip chea | GPL3290 | 191 / 169 | +0.2938 | [-0.0636, +0.1336] | 2.20× | ρ̄ +0.0646, VIF 11.848, 64% | SET-SPECIFIC |
| PPARG pparg curated trrust human | GPL6244 | 66 / 63 | +0.0454 | [-0.0870, +0.0445] | 1.02× | ρ̄ +0.1028, VIF 7.372, 38% | SET-SPECIFIC |
| PPARG pparg curated trrust human | GPL3290 | 66 / 57 | +0.1647 | [-0.1374, +0.2115] | 78% | ρ̄ +0.0146, VIF 1.82, 58% | not distinguishable |

The inflation is a coarse correction, and it is coarsest where the sets are largest: at n ≈ 190 a
ρ̄ of 0.05 already gives a variance inflation factor near 10, so the inflated thresholds for the
PPARγ arms are conservative bounds rather than calibrated values. The three sets the main text's
argument rests on are 14 to 21 genes, where the factor is between 1.2 and 3.6.

### S3.1 · The independence property of the null, measured

`null_sd × sqrt(n)` is constant across set size on both platforms, which is what a null with no
inter-gene correlation term produces:

| platform | set sizes checked | `null_sd × sqrt(n)` | spread | σ used in the closed form | global offset |
|---|---|---|---:|---:|---:|
| GPL6244 | 10, 16, 19, 20, 21, 63, 188, 189, 231, 250 | 0.25282 – 0.26832 | 5.9% | 0.261 | -0.0084 |
| GPL3290 | 10, 14, 17, 18, 57, 157, 169, 176, 196, 230 | 0.66235 – 0.69693 | 5.1% | 0.6776 | 0.0258 |

The closed form `offset ± 1.96 σ_platform / sqrt(n_readable)` reproduces the resampled band edges to
within 3–13% on GPL3290 and 14–36% on GPL6244, the larger error on GPL6244 arising because that
platform's null delta distribution is left-skewed and its empirical quantiles are not those of a
normal. The residual 3–5% decline of `null_sd × sqrt(n)` at the largest set sizes is the
finite-population correction for drawing without replacement from a 4,000-symbol pool.

### S3.2 · Seed sensitivity

Redrawing the 4,000 random sets under 20 further seeds, at a fixed pool:

| set | platform | committed 97.5th percentile | mean over 20 seeds | SD | range | relative SD |
|---|---|---:|---:|---:|---|---:|
| A plus B all dna binding | GPL3290 | 0.37648 | 0.36018 | 0.00562 | [0.35279, 0.3727] | 1.6% |
| D filion table1 emc vs 137 sarcomas | GPL3290 | 0.34814 | 0.35201 | 0.0068 | [0.33775, 0.36175] | 1.9% |
| A plus B all dna binding | GPL6244 | 0.10465 | 0.10009 | 0.00255 | [0.09507, 0.10476] | 2.5% |
| D filion table1 emc vs 137 sarcomas | GPL6244 | 0.09472 | 0.09369 | 0.00292 | [0.08893, 0.1001] | 3.1% |

This bounds Monte-Carlo error only. The committed artifact carries the 4,000 symbols that were
drawn and not the platform universe they were drawn from, so a second pool cannot be drawn here and
pool-composition error is not bounded.

### S3.3 · Composition-matched nulls

Size matching ignores expression level and detection rate, while a published target list is biased
toward well-measured genes. Two further nulls match each draw's decile composition to the real set's,
on the pool symbol's mean value across samples and on its detection rate (the fraction of samples
with a value):

| set | platform | matched on | matched band | reached | uniform-draw reached |
|---|---|---|---|---:|---:|
| A plus B all dna binding | GPL3290 | detection rate decile | [-0.28428, 0.38096] | 87% | 88% |
| D filion table1 emc vs 137 sarcomas | GPL3290 | detection rate decile | [-0.32819, 0.36627] | 4.04× | 4.25× |
| A plus B all dna binding | GPL3290 | expression decile | [-0.32017, 0.3125] | 1.06× | 88% |
| D filion table1 emc vs 137 sarcomas | GPL3290 | expression decile | [-0.21236, 0.59437] | 2.49× | 4.25× |
| A plus B all dna binding | GPL6244 | detection rate decile | [-0.10646, 0.11196] | 36% | 38% |
| D filion table1 emc vs 137 sarcomas | GPL6244 | detection rate decile | [-0.10081, 0.107] | 10.57× | 11.94× |
| A plus B all dna binding | GPL6244 | expression decile | [-0.1514, 0.09665] | 42% | 38% |
| D filion table1 emc vs 137 sarcomas | GPL6244 | expression decile | [-0.12774, 0.09874] | 11.46× | 11.94× |

On GPL6244 the mean value is a log2 intensity and the decile match is an expression-level match; on
GPL3290 it is a mean log-ratio against a reference pool, so detection rate is the closer analogue of
an annotation-quality match there. Both are reported and neither is preferred. The aggregate negative
holds under three of the four and is marginal under the fourth.

### S3.4 · The size-1 null under each gene's own missingness

| gene | platform | n EMC / n comparator | Δ | platform-wide band | band under this gene's own design | width ratio | outside its own band |
|---|---|---|---:|---|---|---:|---|
| *ENO3* | GPL3290 | 10 / 6 | +3.8113 | [-1.31352, 1.40969] | [-1.4092, 1.40647] | 1.034 | yes |
| *NR4A3* | GPL3290 | 9 / 2 |, |, |, |, | not measurable |
| *PLAGL1* | GPL3290 | 8 / 6 | -2.1340 | [-1.31352, 1.40969] | [-1.37486, 1.41577] | 1.025 | yes |
| *PPARG* | GPL3290 | 10 / 5 | +2.4809 | [-1.31352, 1.40969] | [-1.40842, 1.35956] | 1.016 | yes |
| *SEMA3C* | GPL3290 | 10 / 6 | +0.6228 | [-1.31352, 1.40969] | [-1.4092, 1.40647] | 1.034 | no |
| *SGK1* | GPL3290 | 10 / 6 | +0.6156 | [-1.31352, 1.40969] | [-1.4092, 1.40647] | 1.034 | no |
| *ENO3* | GPL6244 | 6 / 29 | +0.8075 | [-0.60637, 0.52874] | [-0.66089, 0.50545] | 1.028 | yes |
| *NR4A3* | GPL6244 | 6 / 29 | +0.7415 | [-0.60637, 0.52874] | [-0.66089, 0.50545] | 1.028 | yes |
| *PLAGL1* | GPL6244 | 6 / 29 | -0.4234 | [-0.60637, 0.52874] | [-0.66089, 0.50545] | 1.028 | no |
| *PPARG* | GPL6244 | 6 / 29 | +0.3071 | [-0.60637, 0.52874] | [-0.66089, 0.50545] | 1.028 | no |
| *SEMA3C* | GPL6244 | 6 / 29 | +0.7298 | [-0.60637, 0.52874] | [-0.66089, 0.50545] | 1.028 | yes |
| *SGK1* | GPL6244 | 6 / 29 | -0.1807 | [-0.60637, 0.52874] | [-0.66089, 0.50545] | 1.028 | no |

### S3.5 · The *t*-scale null, and detectability

Recomputing the Welch *t* for each of the 4,000 draws at the aggregate's readable size gives a 95%
null band for *t* of [−3.31, +4.35] on GPL3290 and [−6.72, +4.37] on GPL6244. The aggregate's own
*t* is 3.16 on GPL3290, and 9.9% of random 17-gene sets print a larger absolute *t*; on GPL6244 its
*t* is 0.76 and 76.9% of random sets print a larger absolute *t*.

| set | platform | Δ | permutation 95% CI | method | smallest shift outside the band with 80% probability |
|---|---|---:|---|---|---:|
| A plus B all dna binding | GPL3290 | +0.3301 | [+0.0921, +0.5650] | exact | 0.4644 |
| B native nr4a3 dna binding targets | GPL3290 | -0.1453 | [-0.4116, +0.1101] | exact | 0.423 |
| D filion table1 emc vs 137 sarcomas | GPL3290 | +1.4783 | [+0.8371, +2.1032] | exact | 0.5722 |
| A plus B all dna binding | GPL6244 | +0.0403 | [-0.0816, +0.1628] | sampled, 20,000 assignments | 0.1495 |
| B native nr4a3 dna binding targets | GPL6244 | -0.0675 | [-0.1777, +0.0433] | sampled, 20,000 assignments | 0.2141 |
| D filion table1 emc vs 137 sarcomas | GPL6244 | +1.1311 | [+0.8946, +1.3725] | sampled, 20,000 assignments | 0.2551 |

### S3.6 · Class B split into B1 and B2

B1 is a catalogue row whose primary assay paper was retrieved and read; B2 rests on a review's
assertion. The partition rule is that the row's citation begins "Reviewed in", with *VTN* assigned to
B2 by hand because its cited primary is a target list rather than the assay the row describes.

| set | platform | n readable | Δ | reached | p_emp | ρ̄ | reached, inflated |
|---|---|---:|---:|---:|---:|---:|---:|
| A plus B1 | GPL3290 | 9 | +0.9189 | 1.91× | 0.0015 | -0.0161 | 1.91× |
| A plus B all dna binding | GPL3290 | 17 | +0.3301 | 91% | 0.07448 | +0.0372 | 72% |
| B1 only | GPL3290 | 6 | +0.1220 | 20% | 0.73207 | -0.0508 | 20% |
| B2 only | GPL3290 | 8 | -0.3537 | 82% | 0.10672 | +0.0994 | 63% |
| A plus B1 | GPL6244 | 9 | +0.1699 | 1.10× | 0.03874 | +0.1586 | 73% |
| A plus B all dna binding | GPL6244 | 19 | +0.0403 | 39% | 0.33017 | +0.1044 | 23% |
| B1 only | GPL6244 | 6 | -0.0525 | 22% | 0.68083 | +0.2929 | 14% |
| B2 only | GPL6244 | 10 | -0.0764 | 41% | 0.44239 | +0.0514 | 34% |

B1 alone clears nothing on either platform, so the A+B1 clearance is carried by the three class-A
members rather than by the retrieved-primary native targets. A+B1 is reported as a sensitivity; A+B
remains the primary aggregate, because re-designating the primary set after seeing which subset
clears is the manoeuvre the calibration exists to prevent.

### S3.7 · Set D without the genes it shares with set E

Set D shares *DKK1*, *MAN1A1* and *NMB* with set E, which is defined as the overlap between Filion's
EMC profile and the top 50 of the GPL3290 cohort itself, so 3 of set D's 18 GPL3290-readable members
are documented members of a list derived from that platform. Scored in one resampler:

| platform | n | Δ with the shared genes | reached | n | Δ without them | reached | p_emp |
|---|---:|---:|---:|---:|---:|---:|---:|
| GPL3290 | 18 | +1.4783 | 4.14× | 15 | +1.0343 | 2.72× | 0.00025 |
| GPL6244 | 21 | +1.1311 | 11.47× | 18 | +1.0756 | 10.56× | 0.00025 |

---

## S4 · The PPARγ receptor-activity reading and its adipogenic ceiling

*PPARG* abundance in EMC is settled elsewhere and is not this work's subject. What no study retrieved
in the corpora searched here reports is receptor *activity*, transcriptional output, as distinct from
receptor abundance. This is a bounded statement about a search, not a claim that no such measurement
exists anywhere. Six gene sets were scored, each pinned to a verbatim Enrichr term with its species
read off the term rather than assumed, each null-calibrated on its own platform.

| arm | library / term | species | GPL6244 | GPL3290 |
|---|---|---|---|---|
| ChEA ChIP-PET targets (191) | `ChEA_2022` · PPARG 19300518 ChIP-PET 3T3-L1 Mouse | mouse | +0.080, p_emp ≤ 0.0005 SET-SPECIFIC UP | +0.294, p_emp ≤ 0.0005 SET-SPECIFIC UP |
| KO_UP falsifier (246) | `TF_Perturbations…` · PPARG DEFICIENCY MOUSE GSE23421 … UP | mouse | −0.054, p_emp 0.041 SET-SPECIFIC DOWN | −0.112, p_emp 0.0035 SET-SPECIFIC DOWN |
| KO_DOWN (206) | …PPARG DEFICIENCY MOUSE GSE23421 … DOWN | mouse | +0.0003 not distinguishable | +0.222, p_emp ≤ 0.0005 SET-SPECIFIC UP |
| OE_UP (269) | …PPARG OE MOUSE GSE10192 … UP | mouse | −0.024 not distinguishable | −0.002 not distinguishable |
| TRRUST, human-curated (66) | `TRRUST…2019` · PPARG human | human | +0.0454, p_emp 0.048 SET-SPECIFIC UP | +0.1647 not distinguishable |
| adipogenesis process proxy (200) | `MSigDB_Hallmark_2020` · Adipogenesis | unstated in the term | +0.047, p_emp ≤ 0.0005 SET-SPECIFIC UP | +0.218, p_emp ≤ 0.0005 SET-SPECIFIC UP |

**Why KO_DOWN and OE_UP cannot be expected to agree, measured rather than argued.** The two arms were
once read as disagreeing about biology, but they share 16 genes out of 206 and 269 (Jaccard 0.035) and
come from different experiments in different tissues. They are, for practical purposes, different gene
sets, and asking them to agree was asking two nearly disjoint lists of mouse genes to score alike in
human tumour tissue. Arithmetic control: KO_DOWN ∩ KO_UP = 0, exactly as the two arms of one knockout
experiment must be.

**What replicates, and how strongly.** The occupancy-derived target set is set-specific up on both
platforms and remains strongly significant under exact label permutation (p = 0.00033 and 0.00075).
The KO_UP falsifier is set-specific down on both platforms under the competitive null, but **it does
not reach significance under the permutation test on either** (p = 0.362 and 0.296), and it clears its
competitive threshold by only 1.02× on GPL6244. The falsifier half of the "two arms separating in
opposite directions" pattern therefore rests on the competitive null alone, and is reported at that
weight. Three of the six arms (KO_DOWN, OE_UP, TRRUST) were never permutation-tested at all, so their
verdicts rest on the competitive null only.

**Under the correlation-inflated threshold none of the six arms clears.** Applying the variance
inflation of main-text §2.3.2 to each arm's own measured ρ̄, the six arms reach 28%, 1%, 26%, 9%, 60%
and 38% of the inflated threshold on GPL6244 and 49%, 65%, 51%, 2%, 64% and 58% on GPL3290
(Table S2). These sets are large, 57 to 250 readable genes, and 1 + (n−1)ρ̄ grows quickly with n,
so the inflated threshold at these sizes is a conservative bound rather than a calibrated one; but the
direction is not in doubt, and no PPARγ arm may be reported as set-specific without that
qualification. The permutation results below are the self-contained evidence that is unaffected by it.

**The ceiling is not small.** The adipogenesis process proxy is also set-specific up on both platforms
and shares 44 genes with the ChEA arm (23% of the smaller set), the largest overlap in the table, and
it is itself significant under permutation on both platforms. PPARγ target output therefore cannot be
separated from an adipogenic differentiation component in these data, and five of the six arms are
mouse-derived. Stated at full honesty: PPARγ target genes are coordinately higher in EMC tumour tissue
than in comparator sarcomas, beyond a size-matched random set, on two platforms, and the same data
cannot distinguish that from an adipogenic differentiation programme. **This says nothing about the
direction of any pharmacological intervention on this axis.**

---

## S5 · Robustness, stratification and covariate sensitivity

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

**The adjustment is a sensitivity analysis, not a correction.** If a panel gene is itself driven by
the fusion, the adjustment removes real signal. The provenance filter (main text §2.6) makes that
unlikely but does not exclude it, and no adjusted number in this document is "the real effect".

**Table S4. Robustness panel (exact permutation, BH, jackknife, rank re-read)**

| row | kind | platform | Δ | exact p | BH q | jackknife: sign holds in every fit | rank re-read: same sign (p) |
|---|---|---|---:|---:|---:|---|---|
| ENO3 | gene | GPL6244 | +0.8074 | 7.3e-05 | 0.000438 | yes | yes (4.9e-05) |
| PPARG | gene | GPL6244 | +0.3071 | 0.0485 | 0.097 | yes | yes (0.059668) |
| SEMA3C | gene | GPL6244 | +0.7298 | 0.194266 | 0.233119 | yes | yes (0.067107) |
| NR4A3 | gene | GPL6244 | +0.7415 | 0.000184 | 0.000552 | yes | yes (0.000146) |
| PLAGL1 | gene | GPL6244 | -0.4234 | 0.082605 | 0.123908 | yes | yes (0.015936) |
| SGK1 | gene | GPL6244 | -0.1807 | 0.369002 | 0.369002 | yes | yes (0.445976) |
| A_plus_B_all_dna_binding | set | GPL6244 | +0.0403 | 0.517577 |, | yes | yes (0.36406) |
| B_native_nr4a3_dna_binding_targets | set | GPL6244 | -0.0675 | 0.225747 |, | yes | yes (0.137337) |
| D_filion_table1_emc_vs_137_sarcomas | set | GPL6244 | +1.1311 | 1e-06 |, | yes | yes (1e-06) |
| PPARG_pparg_chip_chea | set | GPL6244 | +0.0800 | 0.000327 |, | yes | yes (0.001238) |
| PPARG_pparg_KO_UP_FALSIFIER | set | GPL6244 | -0.0536 | 0.361899 |, | yes | yes (0.222558) |
| PPARG_adipogenesis_process_proxy | set | GPL6244 | +0.0473 | 0.034511 |, | yes | yes (0.037594) |
| ENO3 | gene | GPL3290 | +3.8113 | 0.000125 | 0.000625 | yes | yes (0.000125) |
| PPARG | gene | GPL3290 | +2.4809 | 0.000333 | 0.000833 | yes | yes (0.000333) |
| SEMA3C | gene | GPL3290 | +0.6228 | 0.16521 | 0.16521 | yes | yes (0.097777) |
| PLAGL1 | gene | GPL3290 | -2.1340 | 0.002331 | 0.003885 | yes | yes (0.008658) |
| SGK1 | gene | GPL3290 | +0.6156 | 0.155844 | 0.16521 | yes | yes (0.257867) |
| A_plus_B_all_dna_binding | set | GPL3290 | +0.3301 | 0.011114 |, | yes | yes (0.001499) |
| B_native_nr4a3_dna_binding_targets | set | GPL3290 | -0.1453 | 0.257493 |, | yes | yes (0.334915) |
| D_filion_table1_emc_vs_137_sarcomas | set | GPL3290 | +1.4783 | 0.0005 |, | yes | yes (0.000375) |
| PPARG_pparg_chip_chea | set | GPL3290 | +0.2938 | 0.000749 |, | yes | yes (0.000375) |
| PPARG_pparg_KO_UP_FALSIFIER | set | GPL3290 | -0.1118 | 0.296454 |, | yes | yes (0.084416) |
| PPARG_adipogenesis_process_proxy | set | GPL3290 | +0.2183 | 0.001499 |, | yes | yes (0.00025) |

**Table S5. Every stratified comparator contrast, with its own exact permutation p**


**GPL6244**, comparator sub-arms: class_LGFMS_only (n=17), class_desmoid_fibromatosis_only (n=6; identical to non_myxoid_comparators_only, which is the same six samples), class_myxofibrosarcoma_only (n=6; the producing artifact still carries the internal label `fibrosarcoma`), myxoid_comparators_only (n=23), non_myxoid_comparators_only (n=6)

| gene | class LGFMS only | class desmoid fibromatosis only | class myxofibrosarcoma only | myxoid comparators only | non myxoid comparators only |
|---|---|---|---|---|---|
| *ENO3* | +0.805 (p 0.000168) | +0.807 (p 0.02165) | +0.816 (p 0.01082) | +0.808 (p 8e-05) | +0.807 (p 0.02165) |
| *PPARG* | +0.197 (p 0.2204) | +0.473 (p 0.04329) | +0.454 (p 0.06926) | +0.264 (p 0.1003) | +0.473 (p 0.04329) |
| *SEMA3C* | +1.657 (p 0.000119) | -0.645 (p 0.01515) | -0.523 (p 0.1364) | +1.089 (p 0.04609) | -0.645 (p 0.01515) |
| *NR4A3* | +0.839 (p 0.000158) | +0.837 (p 0.002165) | +0.370 (p 0.1255) | +0.717 (p 0.000568) | +0.837 (p 0.002165) |
| *PLAGL1* | -0.169 (p 0.4306) | -0.733 (p 0.04329) | -0.835 (p 0.06277) | -0.343 (p 0.1831) | -0.733 (p 0.04329) |
| *SGK1* | -0.032 (p 0.8796) | -0.167 (p 0.5173) | -0.617 (p 0.04762) | -0.184 (p 0.4055) | -0.167 (p 0.5173) |

**GPL3290**, comparator sub-arms: class_DFSP_only (n=3; identical to reference_pool_matched_only), class_GIST_only (n=3), non_myxoid_comparators_only (n=6), reference_pool_matched_only (n=3)

| gene | class DFSP only | class GIST only | non myxoid comparators only | reference pool matched only |
|---|---|---|---|---|
| *ENO3* | +3.515 (p 0.003497) | +4.107 (p 0.003497) | +3.811 (p 0.000125) | +3.515 (p 0.003497) |
| *PPARG* | +2.679 (p 0.003497) |, | +2.481 (p 0.000333) | +2.679 (p 0.003497) |
| *SEMA3C* | +0.113 (p 0.8427) | +1.133 (p 0.05944) | +0.623 (p 0.1652) | +0.113 (p 0.8427) |
| *NR4A3* |, |, |, |, |
| *PLAGL1* | -1.659 (p 0.04242) | -2.609 (p 0.006061) | -2.134 (p 0.002331) | -1.659 (p 0.04242) |
| *SGK1* | -0.198 (p 0.5804) | +1.429 (p 0.01399) | +0.616 (p 0.1558) | -0.198 (p 0.5804) |

**Table S6. Covariate-adjusted sensitivity**

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

**Table S7. The skeletal-muscle admixture control (GPL6244), with each marker put through the size-1 null**

| gene | muscle-marker? | mean percentile in the 2 pooled muscle samples | EMC | comparators | EMC − comparator |
|---|---|---:|---:|---:|---:|
| *ACTA1* | yes | 1.000 | 0.721 | 0.778 | -0.057 |
| *MYH7* | yes | 1.000 | 0.479 | 0.522 | -0.043 |
| *PYGM* | yes | 0.999 | 0.604 | 0.462 | +0.142 |
| *MYL1* | yes | 0.998 | 0.133 | 0.283 | -0.150 |
| *ENO3* | no (class-A target) | 0.996 | 0.663 | 0.348 | +0.315 |
| *SEMA3C* | no (class-A target) | 0.924 | 0.945 | 0.685 | +0.260 |
| *PPARG* | no (class-A target) | 0.381 | 0.707 | 0.591 | +0.116 |

The percentile differences above carry no null. Put through the same size-1 empirical null the
class-A genes face, on the within-array *z* scale and on GPL6244:

| gene | Δ mean z | size-1 null band | p_emp | outside the band |
|---|---:|---|---:|---|
| *ACTA1* | −0.2800 | [−0.66089, +0.50545] | 0.161 | no |
| *MYH7* | −0.1658 | [−0.66089, +0.50545] | 0.294 | no |
| *MYL1* | −0.5133 | [−0.66089, +0.50545] | 0.064 | no |
| *PYGM* | +0.3438 | [−0.66089, +0.50545] | 0.105 | no |
| *ENO3* | +0.8074 | [−0.66089, +0.50545] | 0.023 | yes |

*MYH7* is a class-B row of the paper's own catalogue (Table S1), so under the native-to-fusion
transfer assumption it would be expected to move; its flatness therefore cannot be read purely as
evidence about admixture. It is retained in the panel with the conflict stated rather than dropped,
because removing a marker after seeing its value is the choice a reader cannot check. On GPL3290 only
*ACTA1* and *MYL1* are readable of the four, at 8 versus 4 and 10 versus 6 samples; both fall inside
their bands, and *PYGM* reads −2.577 there, outside its band in the direction opposite to *ENO3*.

**Table S3. The four instrument controls, graded before any biological read**

| control | platform | n EMC / n comparator | Δ | size-1 null band | p_emp | state |
|---|---|---|---:|---|---:|---|
| *ENO3* (positive) | GPL6244 | 6 / 29 | +0.8075 | [−0.606, +0.529] | 0.0195 | outside, AGREES |
| *ENO3* | GPL3290 | 10 / 6 | +3.8113 | [−1.314, +1.410] | 0.00054 | outside, AGREES |
| *NR4A3* (tumour identity) | GPL6244 | 6 / 29 | +0.7415 | [−0.606, +0.529] | 0.0240 | outside, AGREES |
| *NR4A3* | GPL3290 | 9 / 2 |, |, |, | not measurable (floor is 3 per arm) |
| *PLAGL1* (directional falsifier) | GPL6244 | 6 / 29 | −0.4235 | [−0.606, +0.529] | 0.0885 | inside, not a reading at this power |
| *PLAGL1* | GPL3290 | 8 / 6 | −2.1340 | [−1.314, +1.410] | 0.0130 | outside, AGREES |
| *SGK1* (transcript/protein discordance) | GPL6244 | 6 / 29 | −0.1807 | [−0.606, +0.529] | 0.2694 | inside, AGREES (flat) |
| *SGK1* | GPL3290 | 10 / 6 | +0.6156 | [−1.314, +1.410] | 0.2934 | inside, AGREES (flat) |

Eight cells; seven carry a computable contrast, six are gradeable and all six agree with the
published direction. Four of the six agreements are outside-band readings that could have refused
their prediction; the two *SGK1* cells could not, because an inside-band reading satisfies "flat or
down". Only 42 of the 78 readable genes have the full 10 versus 6 design on GPL3290; the size-1 null
redrawn under each gene's own observed samples is Table S3's companion in §S3.4.

**Table S8. The 3SEQ cohort, calibrated against its own deposit**

| gene | peaks | EMC/normal | percentile of 13,708 | EMC/sarcoma | percentile of 13,247 |
|---|---:|---:|---:|---:|---:|
| ENO3 | 2 | 2.53× | 98.0th | 2.02× | 95.9th |
| SEMA3C | 3 | 1.82× | 94.2nd | 1.66× | 92.6th |
| PPARG | 5 | 1.42× | 84.0th | 2.12× | 96.4th |
| *NR4A3 (control)* | 3 | 1.96× | 95.6th |, (sarcoma median 0.000) |, |

The median gene in this deposit has an EMC/normal ratio of 1.05 and an EMC/sarcoma ratio of 1.05; the
95th percentiles are 1.89 and 1.89. The denominators are the genes with a computable ratio on each
axis, not the deposit's 14,120 genes: a gene whose comparator median is zero has no ratio and is
excluded rather than ranked at the top. A percentile is a rank and this axis carries no test.

**Table S9. NR4A occupancy at the class-A genes, calibrated against a 198-gene background panel**

Peak counts are promoter-window peaks; *p* is empirical against the panel.

| experiment | antigen | peaks | panel genes with a peak | *ENO3* | *PPARG* | *SEMA3C* |
|---|---|---:|---:|---|---|---|
| ReMap2022 (merged) | NR4A1 | 83,773 | 82.8% | 6, p 0.14 | 1, p 0.83 | 1, p 0.83 |
| SRX1653204 | NR4A1 | 26,660 | 45.5% | 2, p 0.12 | 0, p 1.00 | 1, p 0.46 |
| SRX1653203 | NR4A1 | 22,717 | 31.3% | 2, p 0.050 | 0, p 1.00 | 1, p 0.32 |
| AciCC-1 (Haller) | NR4A3 | 18,666 | 67.5% | 4, p 0.070 | 0, p 1.00 | 1, p 0.68 |
| AciCC-2 (Haller) | NR4A3 | 9,810 | 56.0% | 3, p 0.094 | 0, p 1.00 | 0, p 1.00 |
| AciCC-3 (Haller) | NR4A3 | 9,263 | 49.0% | 2, p 0.16 | 0, p 1.00 | 0, p 1.00 |
| Normal parotid gland (Haller) | NR4A3 | 8,501 | 50.5% | 4, p 0.035 | 0, p 1.00 | 0, p 1.00 |
| 5 further NR4A1 experiments | NR4A1 | 305–16,023 | 2.5–27.3% | 0–1, p ≥ 0.26 | 0, p 1.00 | 0, p 1.00 |
| 12 ChIP-Atlas NR4A3 peak sets | NR4A3 | 53–154 | 0.0% | uninformative | uninformative | uninformative |

Both of the two nominal hits at p < 0.05 across the 36 gene-by-experiment tests are *ENO3*'s
(p = 0.0348 in the normal parotid gland and p = 0.0498 in `SRX1653203`); *PPARG* and *SEMA3C* have
none. No multiplicity statistic is computed on the 36 tests, for the reason given in main-text §3.8:
the empirical p-values are ranks within a panel of small integer peak counts, heavily tied and not
independent across experiments. Replacing the withdrawn binomial with a permutation over panel genes
at fixed peak-set depth would require the panel's per-gene peak counts, which the deposited artifact
does not carry; it records `n_panel_genes_at_or_above` per focus gene and the panel's overall hit
rate only.

---

## S6 · The NBRE motif scan, full parameters

**Window.** −10 kb/+15 kb around each gene's Ensembl-canonical TSS. The window is asymmetric, was
fixed in advance on published regulatory architecture, and was frozen **before any sequence was
read** rather than chosen around a result. A distal element outside it is untested by construction.

**Motifs.** The exact NBRE, 5′-AAAGGTCA-3′ (PMID 1902986), and the NurRE (PMID 9315667), scanned on
both strands with hits de-duplicated by genomic position so a palindromic match cannot be counted
twice. **No NurRE occurs in any focus window.**

**Two independent nulls, because an 8-mer occurs in 25 kb by chance.** (i) A
**dinucleotide-preserving shuffle** of the same window, 2,000 shuffles, seeded, which holds base
and dinucleotide composition, and therefore GC and CpG content, exactly. (ii) A background panel
of 198 other genes' windows, read raw and additionally restricted to a GC-matched subset (±0.05). The
panel is a gene list this project had already assembled for an unrelated question, so it cannot have
been chosen to flatter or damage any gene here. It averages 1.15 exact NBREs per 25 kb window, so
a single hit is what an arbitrary window contains anyway. Sequences are cached, so the scan
re-derives offline.

| gene | exact NBRE | shuffle-null p | background-panel p | GC-matched p |
|---|---:|---:|---:|---:|
| *ENO3* | 4 | 0.034 | 0.025 | 0.018 |
| *PPARG* | 3 | 0.227 | 0.131 | 0.209 |
| *SEMA3C* | 0 | 1.00 | 1.00 | 1.00 |
| *NR4A3* | 0 | 1.00 | 1.00 | 1.00 |
| *NR4A1* | 0 | 1.00 | 1.00 | 1.00 |

**The one-mismatch (NBRE-like) class.** Brenca *et al.* report a predicted NBRE-*like* site at
*SEMA3C*, which by construction is not an exact NBRE, so the exact scan is not a test of their claim.
Octamers matching the NBRE with at most one substitution were therefore scanned with their own
null, taken from the *same* shuffled sequences so every exact figure is unchanged. *SEMA3C*'s window
carries 39 one-mismatch sites, the most of any gene scanned, and that is **what its own
composition predicts**: null mean 33.7, p = 0.203 against the dinucleotide-preserving shuffle, and
p = 0.118 GC-matched. Only the composition-naive raw panel rank suggests enrichment (p = 0.040), and
*SEMA3C*'s window is the most AT-rich of the set (GC 0.371) while the NBRE itself is AT-leaning, which is exactly the artefact GC-matching exists to remove. The converse holds for *ENO3*: its
one-mismatch count is *not* enriched (28 against a null mean of 25.6, p = 0.336), so its signal sits
in exact NBREs rather than in degenerate ones.

**A one-mismatch match is a weaker claim than an exact NBRE, not a stronger one**: it admits many
sequences per position, most of which no NR4A protein has been shown to bind. The calibration bounds
a count; it does not license calling any hit a site.

**The hit positions do not reproduce the published coordinates.** Kim *et al.* report two NBREs
upstream of the *ENO3* TSS; this scan finds one upstream (−8.7 kb) and three downstream. Filion
*et al.* report a perfect NBRE at −675 bp of *PPARG*; the nearest hit here is −186. Both papers
numbered from their own promoter constructs, and *PPARG* has multiple promoters, so the offsets are
not directly comparable. **This scan neither confirms nor refutes the published site positions**, and
a motif scan cannot refute a measured binding event at a named locus in any case.

---

## S7 · The archive search for a fusion cistrome

Main-text §3.8 reports that no experiment has measured where an NR4A3 fusion binds, or what chromatin
does, in EMC material. That statement is the result of two searches with different reach, and both
are recorded because they disagree in an instructive way.

The first was a screen of retrieved full text: five corpora totalling 2,276 full-text documents
(3,669 catalogued Europe PMC records), of which 153 name both a genome-wide chromatin method
(ChIP-seq, CUT&RUN, CUT&Tag, ChIP-exo, ChIP-PET, ATAC-seq, ChAP) and NR4A3/NOR-1/TEC. None of the 153
applies one to an NR4A3 chimera, and the only chromatin experiment performed with a fusion anywhere
in that corpus is Brenca *et al.*'s ChAP-qPCR, which is target-specific amplification at one locus.
That count is a fact about a literature screen and an absence does not follow from it.

The second searched the primary sequence archives on 2026-08-08: 179 API endpoints across six rounds
with every query string committed, over GEO, SRA, BioProject, BioSample, ArrayExpress/BioStudies, ENA
and ChIP-Atlas. It retrieved GEO GSE243553, which the literature screen could not reach, for two
recorded reasons: in a pooled screen the perturbation identity is data rather than metadata, so
`NR4A3` appears zero times in that paper's abstract and zero times across all 24 of the series' GEO
sample records, and this project's prior chromatin census was antigen-centric with a ChIP-seq-only
method vocabulary that no ATAC deposit can satisfy. Within the second search, an EMC disease term
returns zero deposits carrying any chromatin library strategy; the 46 SRA runs an EMC term does
return are every one RNA-Seq, WXS, WGS, Targeted-Capture or CAGE; and ChIP-Atlas's complete antigen
index carries NR4A3 in one cell type only (CD1c⁺ dendritic cells) and EWSR1 in seven, none of them
EMC. By contrast the same archives hold ChIP-seq for EWSR1::WT1 and EWSR1::ATF1, ATAC-seq for
EWSR1::FLI1 and FUS::DDIT3 (GSE235218), and ChIP-seq twice for HEY1::NCOA2 mesenchymal chondrosarcoma
(GSE163585, GSE196000).

The bound on this negative is reach rather than existence: it is a statement about what has been
deposited under a label an archive indexes, and GSE243553 is the standing demonstration that a
deposit can be invisible to every gene-keyed query and be reached only through a paper's full text.

---

## S8 · The GEO cohort search

Main-text §2.2 gives the method in one paragraph and Limitation 1 the result. This section carries the queries
verbatim, because a search reported only by its conclusion cannot be checked or repeated.

**Table S11. The cohort search, grouped by why each deposit is not a fourth cohort.**

| group | deposits | EMC samples | disposition |
|---|---|---|---|
| The three cohorts analysed here | GSE24369 (42 samples), GSE4303 (36), GSE28866 (99) | 6, 10, 4 | already used, and the search's positive control |
| The same EWS/NOR1 construct experiment | GSE11185 (4), GDS3481 (its curated view) | 2 sample labels | HEK293 cells carrying a tet-inducible construct, not a tumour cohort |
| Other sarcoma and chondrosarcoma series | 17 deposits, 4–51 samples each: GSE12475, GSE12592, GSE14469, GSE29085, GSE43045, GSE43632, GSE44934, GSE52677, GSE52679, GSE62747, GSE80126, GSE150474, GSE168560, GSE196000, GSE196002, GSE289237, GSE315379 | 0 in every one | read at sample level; no EMC sample in any |

The first row is the result rather than the preamble: it is the positive control, since the same
queries recovered all three cohorts already in use and recovered their EMC arm sizes, 6, 10 and 4,
from GEO sample titles alone, which is an independent path to the three numbers main-text Table 1
takes from the series matrices. A search that had failed to find them would have made the negative
meaningless. The seventeen zeros are what makes it a negative rather than an absence: they span
chondrosarcoma profiling, myxoid liposarcoma, myxoinflammatory fibroblastic sarcoma,
synovial-sarcoma-like tumours, clear cell sarcoma, Ewing sarcoma, rhabdomyosarcoma,
translocation-sarcoma panels and two fusion-detection method series, which is the adjacent territory
in which an EMC sample could plausibly sit under a title that never names the disease. Two of them
(GSE43632, *Large scale screening for fusion genes in sarcoma patient samples*; GSE80126) name no EMC
token in title or summary yet were returned by the full-disease-name query, so GEO's `[All Fields]`
index reaches text beyond the series prose. Read at sample level, none of the seventeen carries an
EMC sample.

The bound is reach rather than existence: a deposit that names the disease nowhere in its GEO record
is invisible to any term search, and a term search is not a systematic review. Within that reach, no
fourth EMC expression cohort exists on GEO. Main-text Limitation 1 records the one deposit outside
that reach, `PRJNA1357027` / `SRP640302`, which is public in the Sequence Read Archive with no GEO
mirror and is not a drop-in fourth arm.

**Table S12. The six queries, with the reason each was included.**

| # | query (NCBI E-utilities, `db=gds`) | why | as written | repaired |
|---|---|---|---|---|
| 1 | `"extraskeletal myxoid chondrosarcoma"[All Fields]` | the disease name in full, highest precision | 17 |, |
| 2 | `"myxoid chondrosarcoma"[All Fields] AND "expression profiling"[Filter]` | the shortened name, restricted to expression series | 0 | 2 |
| 3 | `(EWSR1 AND NR4A3) OR "EWS-NOR1" OR "EWSR1-NR4A3" OR "TAF15-NR4A3"` | the fusion rather than the disease, catches a deposit indexed by its driver | 5 |, |
| 4 | `NR4A3[All Fields] AND sarcoma[All Fields] AND "expression profiling"[Filter]` | the 3′ partner plus lineage, for a deposit naming *NR4A3* but not EMC | 0 | 0, a confirmed zero |
| 5 | `"chondrosarcoma"[All Fields] AND "expression profiling"[Filter] AND "Homo sapiens"[Organism]` | intentionally over-broad: EMC samples inside a general chondrosarcoma series | 0 | 4 |
| 6 | `sarcoma[All Fields] AND "translocation"[All Fields] AND "expression profiling"[Filter]` | translocation-sarcoma panels, the kind of deposit EMC hides inside | 0 | 32 |

All six executed and none returned an error. Counts are the distinct records each query contributed
that no earlier query had already returned, so the same deposit is never counted twice.

**Four queries first returned exactly zero, and that was a reading about the queries before it was
a reading about GEO.** All four carry an `"expression profiling"[Filter]` clause; the two that
returned records do not. Query 5 asks GEO for human chondrosarcoma expression series, a question it
cannot honestly answer with nothing. **A zero and a malformed query are the same length**, and
reported as "six queries, no fourth cohort" this would have made the negative sound materially
stronger than the evidence supported.

**The repair, and what it changed.** A zero-returning query carrying a field restriction is re-asked
with the restriction lifted and the search terms unchanged; records from the repaired form are used
and the query is recorded as `read_after_syntax_repair`. Three of the four then returned records; **2, 4 and 32**, taking the search from 7 series to 22 and from 22 records to 56. Query 6,
the translocation-sarcoma panel query written precisely because it is the kind of deposit EMC hides
inside, accounted for 32 of them on its own. **Query 4 returned zero again under the unrestricted
re-ask and is the only zero in this table read as an absence.** Both forms and both counts are in
`emc-cohort-search-inputs.json`.

**The negative reported in Table S11 is the repaired search.** The unrepaired one would have rested
on two queries while presenting itself as six, and the seventeen sample-level zeros that give the
negative its weight would not have existed, fifteen of those deposits arrived through the repaired
queries.

**What the search declines to conclude, and one way it reaches further than expected.** GEO's
`esearch` matches the text of a record, so a deposit that names the disease nowhere in its GEO
metadata is invisible to every query above however many EMC samples it holds. That bound is real and
is the reason this is a statement about reach rather than existence.

**But the index reaches past the series title and summary, which the returned records demonstrate
directly.** Neither GSE43632 (*Large scale screening for fusion genes in sarcoma patient samples*) nor
GSE80126 carries an EMC token in its title or its summary, and query 1, the full disease name under
`[All Fields]`, returned both. `[All Fields]` therefore indexes text this module never captured, which
is exactly the "EMC hiding inside a generically titled pan-sarcoma deposit" case that queries 4–6 were
written to cover and, being malformed, did not. Both were then read at sample level and carry no EMC
sample. The coverage the broken queries were meant to provide was, in this instance, supplied by query
1, which is a fortunate accident and not a design, and is recorded as such.

**Records excluded for not being deposits.** `db=gds` returns sample and platform records alongside
series, and most of what came back was neither. Of the 56 records: **21 series**, 1 curated dataset
(GDS3481), 30 individual sample records and 4 platform records. Ten of the 30 samples are
samples of the three cohorts already analysed here, six EMC samples of GSE24369 and the four of the
Brunner deposit, returned in their own right by the disease-name query, and two are the
doxycycline-treated and untreated HEK293 samples of GSE11185. A single sample is not a cohort and a
platform is not a deposit; grading them as though they might be would bury the records that need a
decision under records that never could.

**Reproduction.** `research/modalities/emc_cohort_search.py` `emc-cohort-search.json`, with the raw
query record in `emc-cohort-search-inputs.json`. The derive half runs offline from the cached queries
and `--check` re-derives the verdict and diffs it against the committed artifact.

---

## S9 · Genome-build inference for the Haller NR4A3 cistrome

Main-text §3.8 and Table S9 report four deep NR4A3 peak sets from Haller *et al.* (Zenodo
10.5281/zenodo.1483691). This section records how they became usable, because the step is not
routine and a reader should be able to reject it.

**The problem.** A BED file carries no genome build. The deposit names none in its title, its
description or its filenames, and the two candidate human builds differ by a large, position-dependent
offset, on chr10, roughly 300 kb near *RET*. An intersection performed on the wrong build does not
fail: it returns a plausible number for a different locus. This analysis therefore refuses to intersect
any peak set whose build is unknown, and these four arrived in exactly that state.

**The test.** H3K4me3 marks active promoters. The deposit includes an H3K4me3 peak set for each of the
four samples, so on the correct build those peaks must recover most of a promoter panel, and on the
wrong build they must not. The panel used is the same 198-gene background panel every count in Table S9
is calibrated against, assembled for an unrelated question and never chosen with reference to these
data.

**Table S13. Promoter recovery of each H3K4me3 peak set, by candidate build.**

| sample | peaks | panel promoters recovered, hg19 | hg38 |
|---|---:|---:|---:|
| AciCC-1 | 30,660 | 90.6% | 33.6% |
| AciCC-2 | 30,532 | 92.5% | 32.2% |
| AciCC-3 | 29,494 | 92.5% | 33.2% |
| Normal parotid gland | 28,407 | 93.9% | 32.7% |

The deposit is read as hg19, on a worst-case recovery of 0.906 against 0.322, a ratio of 2.81.

**Why two thresholds and not one.** A build is assigned only if the worst sample clears an absolute
floor (0.80) *and* beats the runner-up by a ratio (2.0). The ratio alone would accept two equally wrong
builds; the absolute alone would accept a build on which peaks happen to be broadly distributed.
**The 33% on hg38 is not noise**, the two builds are identical over much of the genome, so a
substantial wrong-build recovery is expected, and a test that treated "it found some" as agreement
would pass on either.

**What the reader can check, and what would overturn it.** Four biological samples agree independently,
which a coordinate error affecting one file would not produce; the mark used is the one with the
strongest prior expectation of promoter localisation, and no transcription factor was used, because a
factor that genuinely avoided promoters would mimic the wrong build; and the panel is the same one the
occupancy calibration uses, so an error in it degrades the build call and the occupancy nulls together
rather than silently favouring one build. **If the deposit is in fact hg38, every Table S9 row from it is
void**, the class-A counts would refer to other loci, while the ChIP-Atlas and ReMap rows, whose
builds come from their catalogues, are unaffected. Nothing else in the manuscript depends on it.

**Reproduction.** `python3 research/modalities/emc_ret_cistrome.py --infer-builds`, offline, from the
committed peak cache; the full per-build table is written to `emc-ret-cistrome-inputs.json` under
`build_inference`.

---

## S10 · Falsifying observations

**Table S10. Observations that would overturn a stated conclusion.**

| observation | what it would overturn |
|---|---|
| An EWSR1::NR4A3 cistrome showing no peak near *ENO3* | The only remaining reading under which *ENO3* is a direct fusion target; it would move *ENO3* to "up in EMC, not fusion-bound". |
| An EWSR1::NR4A3 cistrome showing a peak near *SEMA3C* | Would restore *SEMA3C* as a direct target despite its failure on every correlative axis here, and would show that comparator-driven expression contrasts can mask a real target. |
| A fusion-positive EMC model with fusion knockdown and RNA-seq | Would replace every association in this paper with a directional test, and could overturn all three orderings at once. |
| An EMC expression series recording fusion type per sample | Would test whether *SEMA3C*'s comparator-dependence is EWSR1-versus-TAF15 heterogeneity inside the EMC arm. |
| A soft-tissue normal comparator arm | Would remove confound (a), the one this paper cannot narrow. |
| A per-arm reanalysis of GSE243553's barcode-to-variant files placing the four NR4A3-fusion arms' accessibility calls against a background panel | Would convert §3.8's quoted figures into measured ones and give the first calibrated chromatin read of an NR4A3 fusion, in HEK293T, so it would still not make any gene here fusion-driven in EMC. |
| Any chromatin experiment deposited on EMC material under a label an archive indexes | Would remove the bound §3.8 places on its own negative, which is reach and not existence. |

---

## S11 · Figures moved from the main text

![Figure S1](figures/fig2-evidence-classes.png)

> **Figure S1. The published direct-target catalogue of an NR4A3 chimera is three genes.** Counted
> across 2,276 retrieved full-text documents in five corpora. This is a count of what has been
> published and retrieved, not of what exists. Class B requires the transfer assumption that
> main-text §3.2 shows failing in both directions, and is split in Table S1 into B1 (primary assay
> retrieved) and B2 (review assertion only); the figure shows the undivided class-B total of 16.

![Figure S2](figures/fig5-muscle-admixture-control.png)

> **Figure S2. The *ENO3* muscle-admixture control.** Horizontal axis: how muscle-restricted a gene
> is, as its mean within-array percentile in the two pooled skeletal-muscle RNA samples GSE24369
> contains. Vertical axis: the EMC minus comparator difference in within-array percentile points. The
> two muscle samples are in neither arm and no contrast in this paper uses them; they fix the scale
> only. Three of the four markers more muscle-restricted than *ENO3* sit at or below zero and the
> fourth, *PYGM*, moves +0.142; all four fall inside their size-1 null while *ENO3* falls outside it
> (Table S7). *MYH7* is also a class-B row of the paper's own catalogue. This bounds admixture of
> differentiated skeletal muscle; it does not exclude a myogenic differentiation programme in the
> tumour itself.
