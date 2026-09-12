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

## Reading and evidence status

| Source | Reading completed at this checkpoint | Still needed |
|---|---|---|
| Bangerter 2023 models | Cached article body text | Figures, supplements, original response matrices, independent check |
| Brenca 2019 axon-guidance study | Substantial article text, including methods and discussion | Complete untruncated reading, figures, supplements, cohort matching |
| Wilbur 2022 PGR case | Partial cached body text | Complete text/tables/figures |
| Jennings 2021 KIT case | Cached body text | Figure inspection and source-level verification |
| Stacchiotti 2012 sunitinib cases | Cached body text | Figures and linkage to subsequent series |
| Suemitsu 2025 | Primary PubMed abstract | Full paper and patient/sample tables |
| Hindi 2025 IMMUNOSARC II | Publisher meeting abstract | Full report/poster, endpoint clarification, cohort linkage |
| Racanelli 2019 comparative study | Publisher meeting abstract | Underlying data and potential journal counterpart |
| Caris 2026 | Laboratory's public summary | Actual poster, denominators and overlap |

The cached texts reused above come from literature-cache commit `216bd1b5fb25a56b90ef3cc2373e1fe68322708f`; newly retrieved body hashes are in `retrieval-ledger.json`. A keyword screen, an API download and an abstract reading never count as a complete literature reading. There is no evidence here that nobody previously read or integrated these works.

## Completion criteria for the remaining synthesis

1. Adjudicate the 648 focused records, maintaining exclusions with reasons and separate review/case/clinical/preclinical/conference classes.
2. Screen the 955 broader records for genuine EMC subgroup results. Search older names and society archives; record coverage by source and year, including unsuccessful searches.
3. Recover lawful public versions for unresolved records, checking repository copies and author manuscripts. Label unresolved access honestly; do not purchase articles or contact authors without applicable authorization.
4. Link reports to studies and cohorts. Treat suspected overlap conservatively until source evidence resolves it.
5. Read accessible bodies, tables, figure legends, figures, supplements and corrections with an item-level ledger. Extract contradictory results and failed validation, not only supporting statements.
6. Produce a cross-study evidence matrix with exact source locations, model/patient denominators, effect definitions, uncertainty, confounders and competing explanations. Rank only hypotheses with a specific discriminating experiment or reproducible public-data test.

The current output is a reproducible census checkpoint, a usable discovery catalogue and an initial research-priority memo. It is not the completed exhaustive review or a submission-ready scientific synthesis.
