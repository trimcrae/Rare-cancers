# CSPG4 expanded sarcoma comparison data and code

This package contains the September 19 expanded comparative analysis. It is distinct from the original Research Square version 1 archive. Main supplementary Tables S2/S3 correspond to primary/pooled-panel-tests.csv and primary/CSPG4-by-type.csv; Tables S4/S5 are external/analysis-final/external-type-summaries.csv and external-within-source-pairs.csv.

## Verification and replay

Use Python 3.12 with numpy and openpyxl. `python replay.py` verifies every packaged input and retained output hash without rerunning accepted analyses. To reproduce the primary exact tests and all external tables, run `python replay.py --output PATH_TO_NEW_DIRECTORY`. The directory must not exist. The primary script recomputes all 11 exact tests and checks their numerical records; the external script checks all five CSVs byte for byte. Existing package inputs remain untouched. Timestamps in newly generated JSON naturally differ. No network access or full-matrix download is needed for this replay.

The original historical conditional analysis is preserved rather than repeated by this replay. Original complete data/code remain at https://assets-eu.researchsquare.com/files/rs-10959636/v1/b95606f3a3799c60c8ac4434.zip (SHA256 56e089a6b39b9d5d5140a4185987778803359ab1154d26beb882d6e6197f3ea6). The archived primary/analyze.py and prepare.py contain the historical local full-source path; replay.py invokes only their imported rank/effect functions and the exact test using the included fixed reported-value slice. Full-source reacquisition requires the source metadata and Zenodo link below, not that local path.

## Inputs and scope

Hofvander: https://doi.org/10.5281/zenodo.17866629. All 644 eligible specimens and 11 reported genes are preserved, with the original 9 EMC and 393 defined references. Eligibility and original source digests are in primary/FROZEN-DESIGN.json. No new inferential population or year effect is assumed.

Original arrays: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE24369 and GPL6244. Retained historical-analysis files include the full original gene/comparator/deletion tables and metadata; the old public archive contains the original source replay.

Treehouse: https://xena.treehouse.gi.ucsc.edu/; exact version25.01 dataset names, query policy and original URLs appear in external/EXTERNAL-DESIGN.json and RETRIEVALS.jsonl. TREEHOUSE-VALUES.json preserves original query values, including profiles subsequently excluded by documented identity corrections. TREEHOUSE-SELECTION-CORRECTED.json controls final selection.

Boudin: https://doi.org/10.1186/s12967-022-03679-y. Supplementary Table S8 is retained with its original column/row positions and file digest. BOUDIN-SELECTION.json preserves source diagnosis text and mapped records; the acceptance record resolves the 986 selected rows.

Modern cohorts: GEO GSE213065 and GSE234092. Extract JSON files preserve source URL, compressed-matrix hash, headers, selected values, diagnosis crosswalks and (for raw counts) complete column denominators. The MSB40 prefix-match qualification is in METADATA-CORRECTIONS.json. CPM is not TPM.

OpenPedCan: https://s3.amazonaws.com/d3b-openaccess-us-east-1-prd-pbta/open-targets/v15/. The frozen design, metadata slice, exact29-column extraction and remote receipt are retained. Clinical summaries contain28 profiles; the unresolved parental-tumor profile stays visible in the ledger. Large RDS MD5:5e17af159401140c5946dd0517d03015. Only the gene slice is included. The source read is supported by its committed code, checksum, schema and actual runner receipt; it was not independently extracted twice.

Resource-profile counts are not an additive globally unique patient count. External measurements remain on their designated source scales, and there is no external pooled EMC P value or additional explicitly labeled EMC group. All 304 summaries and 1,480 pairs are preserved, including small groups and adverse results.

## Figure sources and rights

`figures/make_figures.py` uses ReportLab with the three retained CSV inputs to produce vector figures. It is presentation code, not a new inferential analysis. Figure commit receipts accompany the manuscript revision. Original source attribution and reuse terms apply; this package does not relicense third-party datasets. The manuscript cites every source collection. Public individual-level identifiers are source research identifiers, not author disclosure forms. No private journal form is included.
