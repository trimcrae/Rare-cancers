---
id: DOC-EMC-LITERATURE-CENSUS-20260912
title: EMC literature census and initial research connections
kind: memo
status: live
purpose: Record reproducible literature discovery counts and preliminary cross-study questions without claiming exhaustive coverage or reading.
scope: September 2026 bibliographic snapshot, initial source readings, limitations and remaining review work.
audience: [maintainers, collaborators]
date: 2026-09-12
last_verified: 2026-09-12
---

# EMC literature census and initial research connections

There is not yet a defensible worldwide total of distinct published EMC research outputs. The current searches establish a manageable discovery corpus, not an exhaustive or adjudicated evidence base. The first catalogue contains 1,603 records after DOI/identifier deduplication, including 648 disease/fusion matches in titles or abstracts and 955 broader matches. Many broader matches will be incidental; some focused matches concern diagnostic mimics. Reviews, preprints, meeting abstracts and repeat reports of a cohort cannot be counted as independent studies.

The exhaustive reading and synthesis requested for this project is **not complete**. Ninety-four article bodies were recovered from 131 focused PMC-identified records. Recovery is not reading. Thirty-seven XML requests remain unresolved; a failed XML endpoint does not mean that the paper is inaccessible. Figures, supplementary files, older non-OA literature, conference archives and mixed-cohort result tables need further work. No new treatment has been validated, and no claim of a previously overlooked discovery is warranted at this checkpoint.

## What the numbers measure

Searches were performed on 12 September 2026. Original Europe PMC and Crossref API responses are retained in compressed snapshots. Europe PMC response hashes and exact paginated queries are recorded in `manifest.json`; the direct PubMed response is in `pubmed-count.json`.

| Search or processing step | Count | Interpretation |
|---|---:|---|
| Direct PubMed exact disease phrase | 447 | Indexed bibliographic records, not distinct studies |
| Europe PMC exact disease phrase, default search | 1,240 | Includes full-text/index matches and sources beyond PubMed |
| Europe PMC MED source, disease spelling variants in title/abstract | 455 | Focused database records; different query from direct PubMed |
| Europe PMC MED source, spelling variants in title | 285 | A narrow retrieval anchor, not a lower bound on original studies |
| Europe PMC expanded disease/fusion query | 1,471 | All returned records retrieved across 15 pages |
| Crossref first 1,000 title-search results | 389 title matches | Fuzzy search is truncated; its 9,415 total hits are not EMC works |
| Crossref records added after DOI matching | 132 | Includes conference supplements and other non-MED outputs |
| Combined discovery catalogue | 1,603 | DOI/identifier-deduplicated records, not study-deduplicated |
| Combined title or abstract matches | 648 | Automated priority screen; 441 title and 207 abstract matches |
| Focused records with an indexed free-text link | 178 | Includes free conference abstracts; not all links downloaded |
| Focused access unresolved | 470 | No claim that a public copy does not exist |
| Focused records with a PMC identifier | 131 | XML retrieval attempted |
| Article bodies recovered / XML unresolved | 94 / 37 | Figures and supplements not verified |

The total is tractable for a systematic bibliography and staged reading. It is not tractable as a single undifferentiated claim to have read everything: access, entity identification, report linkage and supplementary material are substantive parts of the work. A sensible planning scale is hundreds of focused records plus roughly a thousand candidates to screen for incidental mentions or buried EMC data. That is a workload estimate, not a confidence interval for the world's literature.

## Inclusion and counting rules

An eligible research output should contain identifiable results on confirmed EMC: clinical observations, case reports, tumour or model experiments, genomic/transcriptomic data, or extractable EMC subgroups from larger studies. Posters and conference abstracts count as reports when actual results can be located. A programme listing alone establishes a presentation's existence, not its results. Reviews belong in the bibliography but are a separate evidence class. Trial registrations without posted results are discovery leads, not completed studies.

Maintain three distinct identifiers: a bibliographic report, its underlying study, and its patient/model cohort. One study can generate an abstract, poster, preprint, journal paper and update. Two studies may reuse patients. Identical titles are insufficient to merge studies; a shared trial identifier or demonstrably matching cohort provenance is stronger evidence. Report counts and patient denominators must therefore remain separate.

For historical reports, record how EMC was diagnosed and whether molecular confirmation exists. Do not silently equate skeletal myxoid chondrosarcoma, mesenchymal chondrosarcoma, myoepithelial tumours or morphologic mimics with modern NR4A3-rearranged EMC. Preserve uncertain older reports for expert adjudication instead of inventing molecular confirmation.

The catalogue currently deduplicates exact DOI/record identifiers only. It has not completed study-level linkage, language screening, reference chasing, forward citation searching, full society-archive searching, public dataset mining, or per-record adjudication. These limitations preclude an “all published EMC research” label.

## Initial connections worth testing

### 1. Fusion identity and additional alterations should be evaluated jointly

The 2025 Suemitsu study describes 18 patients represented by 20 samples. Its abstract associates additional alterations with poorer survival and reports variation beyond the defining fusion. The 2026 Caris poster summary also discusses secondary changes and fusion partners, but its complete cohort tables have not been recovered. These are potentially complementary sources; the summary alone cannot establish independent replication or justify pooling. [Suemitsu et al.](https://pubmed.ncbi.nlm.nih.gov/40828003/), [Caris poster summary](https://www.carislifesciences.com/research/publications/secondary-genetic-alterations-in-extraskeletal-myxoid-chondrosarcoma-beyond-nr4a3/)

The useful research question is whether a putative association between fusion partner and treatment response remains after accounting for additional alterations, disease stage and treatment line. This could distinguish a predictive biomarker from a marker of intrinsically aggressive disease. A patient-level table linking these variables would be more informative than pooling response percentages by fusion partner across unrelated reports.

The next evidence requirement is recovery of the full genomic tables and cohort identifiers, followed by an overlap audit. With rare events and small subgroups, elaborate multivariable models may be unstable; prespecified descriptive strata and uncertainty may be the only defensible analysis. Additional alterations are not automatically actionable drug targets, and a prognostic association does not demonstrate benefit from a matching therapy.

### 2. Anti-angiogenic response and semaphorin biology are an existing hypothesis

The 2019 primary study profiled seven EWSR1- and five TAF15-rearranged tumours and used engineered cell models. It explicitly connected fusion-dependent axon-guidance programs with possible differences in anti-angiogenic response, including a discussion of semaphorin-directed treatment. Rediscovering that connection is not novel. Its models also showed differences between fusion-protein abundance and RNA abundance, making transcript-only stratification an imperfect substitute for protein measurements. [Brenca et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC6766969/)

A more discriminating follow-up would ask whether the relevant pathway state predicts response within a fusion class, rather than assuming that the fusion label completely captures pathway activity. That requires linked pretreatment tumour measurements and actual treatment outcomes. Endothelial and immune compartments need explicit representation; isolated tumour-cell viability cannot establish an anti-angiogenic mechanism.

The 2025 IMMUNOSARC II meeting report provides a combination-treatment dataset, but its single-arm design cannot isolate nivolumab's contribution. The abstract reports 77% six-month PFS alongside 16/23 patients progression-free at six months; the simple fraction is approximately 69.6%. A survival estimator may explain this difference, but the abstract does not provide enough detail to reconcile it. Do not substitute one quantity for the other or label the difference a proven error. [Hindi et al., ASCO 2025](https://ascopubs.org/doi/10.1200/JCO.2025.43.16_suppl.11513)

The endpoint clarification and patient-level biomarker linkage are higher priorities than proposing another empiric combination from literature co-occurrence. No evidence reviewed here establishes that adding an immune agent is superior to the anti-angiogenic component alone.

### 3. Proteasome combinations need model-specific validation, not a uniform synergy claim

The two patient-derived EMC models in Bangerter et al. support a preclinical combination-testing lead. The results distinguish synergy in one model from additivity in the other, and venetoclax monotherapy did not retain its initial screening signal in validation. The study is already represented in this repository's research, so it is not a newly discovered treatment lead. Its results and discussion also describe partner combinations inconsistently; the figures and original response matrices are needed before assigning a precise combination effect. [Bangerter et al.](https://doi.org/10.1007/s13577-022-00818-x)

The useful next comparison is whether this sensitivity is reproducible across independent molecularly confirmed EMC models, whether it is related to fusion-protein handling or a broader stress response, and whether it exceeds toxicity in relevant nonmalignant cells at achievable exposure. Fusion knockdown or rescue controls would help distinguish a fusion-dependent vulnerability from generic cytotoxicity. A small number of models cannot establish a therapeutic window, and one model per fusion partner confounds patient background with fusion type.

The existing `carfilzomib-class-clinical-2026-08-28.json` memo must be carried forward as prior work, including the limitations of broader sarcoma class evidence. It should not be summarized as fresh clinical confirmation of the EMC cell experiments.

### 4. Exceptional molecular cases justify better ascertainment of rare subgroups

The PGR–NR4A3/tamoxifen report and the somatic KIT-mutant/imatinib report are examples of biologically selected single-patient observations. The former describes an unusual fusion and hormone-related expression pattern; the latter documents sustained stable disease with a KIT alteration. They do not support giving those drugs to unselected EMC patients or treating an immunostain as equivalent to a functional mutation. [Wilbur et al.](https://doi.org/10.1200/PO.22.00039), [Jennings et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC8395296/)

The connection is methodological: narrow assays and broad histology labels can hide potentially relevant exceptional subgroups. A harmonized catalogue should therefore capture assay coverage, fusion architecture, secondary alterations, the reason a therapy was selected and the pretreatment growth trajectory. This can reveal missed opportunities to investigate a subgroup without turning anecdotal benefit into general efficacy.

The next step is a denominator search: how many comparable patients were sequenced with an assay able to detect the alteration, how many were negative, and how many received the proposed therapy? Positive case publication alone cannot answer prevalence or response probability.

### 5. Comparative studies can prevent false treatment transfers

The 2019 ESMO abstract comparing 12 EMC with seven myoepithelial tumours assigns the stronger Hedgehog/WNT signature to the myoepithelial group. An automated search that collects the disease name, pathway and drug target from the same abstract could incorrectly assign that finding to EMC. Its EMC fusion-group composition also matches the seven/five split in the 2019 axon-guidance paper; this is a reason to investigate cohort reuse, not proof of identical patients. [Racanelli et al., abstract 1721P](https://www.sciencedirect.com/science/article/pii/S0923753419603431)

Every cross-tab extraction should preserve row labels, diagnosis, comparator, numerator, denominator, assay and specimen provenance. A negative or comparator-specific finding can be as useful as a new positive hypothesis because it stops an unsupported route from consuming experimental effort.

### 6. Separate a metabolic enzyme's transcriptional role from glycolysis

A 2007 study found that GAPDH could enhance hTAFII68–TEC fusion-dependent reporter activity through an interaction-associated mechanism. The assays used engineered non-EMC cellular systems, and the authors left the precise mechanism unresolved. The old fusion terminology makes this paper easy to miss in searches confined to modern NR4A3 names. [Kim et al.](https://pubmed.ncbi.nlm.nih.gov/17302560/)

The availability of newer patient-derived EMC models creates a way to revisit that biochemical observation in a disease-relevant setting. A discriminating experiment would compare a perturbation of the proposed cofactor interaction with inhibition of glycolytic activity, using controls that separate transcriptional effects from general cell toxicity. This is an experimental-design hypothesis, not evidence that a GAPDH inhibitor treats EMC. The original interaction is established prior art; whether this particular follow-up has already been performed remains unverified. The primary abstract and substantial publisher-indexed text were read; complete figure-level verification remains outstanding.

## Reading and evidence status

| Source | Reading completed at this checkpoint | Still needed |
|---|---|---|
| Bangerter 2023 models | Body, references, all six figures and both supplementary tables | Original response matrices; independent check of discrepancies |
| Brenca 2019 axon-guidance study | Substantial article text, including methods and discussion | Complete untruncated reading, figures, supplements, cohort matching |
| Wilbur 2022 PGR case | Partial cached body text | Complete text/tables/figures |
| Jennings 2021 KIT case | Cached body text | Figure inspection and source-level verification |
| Stacchiotti 2012 sunitinib cases | Cached body text | Figures and linkage to subsequent series |
| Suemitsu 2025 | Primary PubMed abstract | Full paper and patient/sample tables |
| Hindi 2025 IMMUNOSARC II | Publisher meeting abstract | Full report/poster, endpoint clarification, cohort linkage |
| Racanelli 2019 comparative study | Publisher meeting abstract | Underlying data and potential journal counterpart |
| Caris 2026 | Laboratory's public summary | Actual poster, denominators and overlap |
| Kim 2007 GAPDH/fusion study | Primary abstract and substantial indexed article text | Complete article/figures and verification in EMC models |

The cached texts reused above come from literature-cache commit `216bd1b5fb25a56b90ef3cc2373e1fe68322708f`; newly retrieved body hashes are in `retrieval-ledger.json`. A keyword screen, an API download and an abstract reading never count as a complete literature reading. There is no evidence here that nobody previously read or integrated these works.

## Completion criteria for the remaining synthesis

1. Adjudicate the 654 focused records, maintaining exclusions with reasons and separate review/case/clinical/preclinical/conference classes.
2. Screen the 975 broader records for genuine EMC subgroup results. Search older names and society archives; record coverage by source and year, including unsuccessful searches.
3. Recover lawful public versions for unresolved records, checking repository copies and author manuscripts. Label unresolved access honestly; do not purchase articles or contact authors without applicable authorization.
4. Link reports to studies and cohorts. Treat suspected overlap conservatively until source evidence resolves it.
5. Read accessible bodies, tables, figure legends, figures, supplements and corrections with an item-level ledger. Extract contradictory results and failed validation, not only supporting statements.
6. Produce a cross-study evidence matrix with exact source locations, model/patient denominators, effect definitions, uncertainty, confounders and competing explanations. Rank only hypotheses with a specific discriminating experiment or reproducible public-data test.

The current output is a reproducible census checkpoint, a usable discovery catalogue and an initial research-priority memo. It is not the completed exhaustive review or a submission-ready scientific synthesis.


## Continued source review, 12 September

The Bangerter model paper has now been read through its body, references, all six figures and both supplementary tables. Figure 6 supports carfilzomib paired with venetoclax or doxorubicin; the discussion's different pairing should not be propagated. Figure 3 prints 5.01 days for USZ20-EMC1 while its caption/text says 5.09. The displayed USZ22 growth curve and stated doubling time also need reconciliation against raw data. These discrepancies do not establish that the drug findings are wrong, but prevent treating every printed number as independently verified.

The Iwata 2025 paper, DOI [10.1007/s13577-025-01250-7](https://link.springer.com/article/10.1007/s13577-025-01250-7), has a subscription preview but publicly downloadable supplements. All 221 rows of supplementary Table 3 and all 24 rows of Table 4 were read and extracted with source-row provenance in `iwata-2025-screen-extraction.json`. The headline candidates brigatinib, panobinostat and romidepsin have reported IC50 values of 1.73, 3.37 and 8.04 nM. Bortezomib is 135 nM. Carfilzomib appears in the screen but not the IC50 table. Main methods remain unavailable in this review; concentration, duration, normalization and replicate count must be recovered before quantitative comparison. Salt forms, negative normalized values and large standard deviations are preserved. The supplementary figure caption mentions 21 agents while the IC50 table lists 24.

### Questions supported by the comparison

1. **Proteasome sensitivity across independently derived models.** The newer screening result gives a reason to test whether the earlier carfilzomib finding generalizes under matched conditions. It does not establish cross-study replication of potency or clinical benefit. Venetoclax monotherapy's weak activity in both reports is useful negative context; combination benefit still needs its own evidence.
2. **Drug response versus target identity.** Brigatinib sensitivity alone cannot identify ALK as the dependency. A useful next analysis is a panel of structurally distinct inhibitors combined with verified tumour/model kinase alterations and target-engagement evidence. Drug labels in a library are not mechanistic validation.
3. **Model identity before merging old experiments.** [Cellosaurus H-EMC-SS](https://www.cellosaurus.org/CVCL_1238) cautions that this line lacks an EWSR1 fusion, citing the Gartrell study. Absence of EWSR1 alone does not exclude every alternative NR4A3 fusion. The primary molecular characterization must be checked before older H-EMC-SS findings are pooled with the molecularly confirmed modern models.

These are review questions, not newly established therapies or verified novel hypotheses. Existing repository work and primary-paper discussion must be checked before any novelty claim. Raw model-screen files remain local; the public catalogue links readers directly to the publisher's supplementary results.


The follow-up historical-model/fusion query retrieved all 56 results and added 26 identifiers, bringing the discovery pool to **1,629 records**, including **654 title/abstract matches**. These remain candidate records, not 1,629 EMC studies. All 447 PubMed exact-phrase identifiers were checked against the catalogue and were already present. The query newly surfaced mixed-sarcoma drug screens and H-EMC-SS experiments, along with incidental references that require exclusion.


### Mixed-screen subgroup: useful negative context

The [Beird 2026 sarcoma screen](https://doi.org/10.1158/2767-9764.CRC-26-0142) provides a public [author dataset](https://zenodo.org/records/19098295). Its HEMCSS column contains 1,387 compound measurements, now extracted reproducibly by `scripts/emc_beird_subgroup.py`. This is computational extraction, not a claim that every row or the complete paper has been manually reviewed. The model catalogue maps this column to CVCL_1238; its disputed identity prevents interpreting these as confirmed EMC-specific findings.

For carfilzomib, the published fraction-affected AUC is 0.4653 versus a mean of 0.7218 in 16 other cancer models with measurements; 13 have higher AUC. Panobinostat is 0.4693 versus 0.7301 in 19 comparison models, 18 of which have higher AUC. These within-assay comparisons weaken a claim of unusual sensitivity in this historical model. They do not contradict a matched experiment in the newer, molecularly confirmed EMC models, and the cancer comparators establish no normal-tissue safety margin. The source matrix, exact drug aliases and source-row numbers are retained in `beird-2026-hemcss-extraction.json`. Full plate QC and figure review remain pending.

### Regression cases: hypothesis and alternative explanation

[Carroll 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12660641/) has now been read through its body, all references and four figures. It reports regression of pulmonary nodules following debulking after earlier progression on sunitinib, atezolizumab and trabectedin. The primary tumour was NR4A3-rearranged; biopsy confirmation of the lung nodules is not reported in the text. The selected before/after CT panels illustrate the authors' observation, but cannot independently establish the identity of every nodule or a causal mechanism.

The authors already propose surgery-associated immune effects and earlier immunotherapy priming. That is their hypothesis, not a new discovery from this review. The abstract of [Kinoshita 2015](https://pubmed.ncbi.nlm.nih.gov/26434451/) describes regression after biopsy without preceding treatment, providing a reason not to assume checkpoint exposure is necessary. Its full text remains unresolved. Neither case establishes a treatment strategy. A useful discriminating research question is whether paired tissue and immune measurements can separate tumour-specific immunity from other causes of radiographic change; those measurements are not supplied by these reports.


### Conference archive expansion and repeat-report linkage

Six society/institutional records are now explicitly sourced in `manual-records.json`: three complete public abstracts and three program listings. The discovery pool is **1,635 records**, with **660 title/abstract or manually assessed focused matches**. A program listing proves that a presentation was listed; it does not supply the results. The CTOS 2023 and 2025 mixed-subtype abstracts have unresolved classification/denominator issues documented beside their catalogue entries.

The Japanese trabectedin family is linked in `study-families.json`. [Morioka 2016](https://doi.org/10.1186/s12885-016-2511-y), [Takahashi 2017](https://doi.org/10.1634/theoncologist.2016-0064) and [Endo 2020](https://doi.org/10.1002/cam4.2991) reuse the two EMC patients from JapicCTI-121850; the crossover trial adds none. The two EMC outcomes were stable disease with PFS of 13.0 and 7.4 months. The subanalysis's partial response was mesenchymal chondrosarcoma, and its supportive-care arm contained no EMC patient. The figures and supplements have now been read. This family cannot provide a randomized EMC-only treatment-effect estimate.

### Clinical context for the model-screen lead

The complete main [Boklan 2025 carfilzomib combination report](https://doi.org/10.3390/cancers17172924), including seven tables, references and two figures, was read. Its Table 2 has one unqualified “sarcoma” entry, also labelled only “Sarcoma” in Figure 2 (C041); EMC inclusion cannot be determined. The manuscript does not demonstrate EMC benefit or isolate carfilzomib's contribution from cyclophosphamide/etoposide. Banked proteasome-inhibition samples had not yet been analyzed. Full supplementary protocol review remains pending. The study is retained as clinical context rather than added to the count of confirmed EMC reports.
