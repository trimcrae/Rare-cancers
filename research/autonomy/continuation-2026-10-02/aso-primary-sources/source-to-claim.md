---
id: DOC-ASO-PRIMARY-SOURCE-INTEGRATION-20261002
title: Targeted ASO primary-source integration and exact remaining limits
level: cross-cutting
kind: memo
status: live
purpose: Bind material biological and methodological claims in the current ASO draft to verified primary research.
scope: Seven selected publications and existing computational records; no comprehensive novelty review, new sequence analysis or outgoing-package rebuild.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

# Scope and outcome

The revised copy is manuscript-primary-integrated.md, based on manuscript-draft.md at remote revision 4818db097f97ff8f862cd02bb9a2ddcf6c76cb71 (Git blob e264ff94d88e2e3ad74954a4102fd5d5895d20dc). Only targeted source integration and independent-copy source links changed. Counts, sequences, ranking sets and accepted evidence classes remain inherited computational results; none was rerun. The latest exact-hit findings were read: 134 occurrences, 63 transcripts, 12 versioned gene IDs, six recovered occurrences in three transcripts, and 60-ID Ensembl comparison.

The user redirected program emphasis to measured-data reanalysis during this task. This deliverable closes already-started citation integration; it does not recommend further ASO rebuilding or another review cycle.

Current-package correction: the accepted author-proofreading package is candidate da7fab35440a74ea1c46c4ab197cead793333711, branch codex/aso-concise-20260927, at research/release-candidates/PUB-ASO/2026-09-30-letter-package. Local ROOT-ACCEPTANCE.json and FULL-TIER-ACCEPTANCE.json were read to confirm that binding. The 190-design journal source is only a historical comparator, not the current outgoing package. The copied draft now states this explicitly. No accepted brief or its tests was changed or revalidated. In claims-and-change-map.md, the opening “starting outgoing source” and material-status item1 should likewise say “historical journal-article comparator”; the current concise package already covers the 215-design catalogue.

All seven Europe PMC metadata requests returned one matching record. The JSON receipt retains actual response bytes/hash/UTC date and returned title, authors, journal, DOI/PMID and dates. Five full-text XML responses were retrieved successfully and selected relevant sections read. Full article XML is not retained. Long initial tool output was truncated; fulltext-receipts.json distinguishes extracted headings from the actual bounded reading scope, supplemented by direct PLOS full-text reading. The pre-existing PFRED Crossref record and receipt were inspected and reused as corroboration (Git blobs ce19704bbaf57e1e7293436f918868343d199356 and 29ab617b99623ba917d4f5d75a39f68cbe62b765).

## Source-to-claim table

| Draft claim/location | Primary source and verified identity | Text actually used and precise limit |
| --- | --- | --- |
| Introduction: EWSR1–NR4A3 fusion context | Labelle et al., 1995, Human Molecular Genetics 4(12), [DOI10.1093/hmg/4.12.2219](https://doi.org/10.1093/hmg/4.12.2219), [PMID8634690](https://pubmed.ncbi.nlm.nih.gov/8634690/) | Europe PMC abstract describes EWS/TEC fusion cloning and junction types. No prevalence percentage imported. Publisher DOI page was inaccessible via web tool; abstract-only support is stated. |
| Introduction: EWSR1/TAF15 models; test-article reconstruction | Brenca et al., 2019, Journal of Pathology 249(1), [DOI10.1002/path.5284](https://doi.org/10.1002/path.5284), [PMC6766969](https://pmc.ncbi.nlm.nih.gov/articles/PMC6766969/) | Full-text “Cells and constructs”: E-N, T-N and T-N* exon spans, PLPCX constructs and T-N cryptic-intron sequence; functional-model paragraph. These descriptions do not independently establish the literal sequence of the present test article. No supplement/construct sequence audit performed. |
| Test-article identity: USZ20/USZ22 reported fusions | Bangerter et al., Human Cell 36(1), 2023; online 2022-11-01, [DOI10.1007/s13577-022-00818-x](https://doi.org/10.1007/s13577-022-00818-x), [PMC9813045](https://pmc.ncbi.nlm.nih.gov/articles/PMC9813045/) | Molecular characterization methods/results and Figure4 textual legend. They explicitly report RNA-level fusion confirmation; draft must not suggest that no RNA assay occurred. Catalogue USZ20 reconstruction and unresolved USZ22 remain artifact-qualified statuses, not corrections to the reported existence of the fusions. |
| Introduction: junction-directed ASO precedent | Skórski et al., 1991, Folia Histochem Cytobiol 29(3):85–89, [PMID1794439](https://pubmed.ncbi.nlm.nih.gov/1794439/) | Abstract reports breakpoint-directed 18-mer BCR/ABL experiment. Used only for historical existence of junction-directed ASOs, not current efficacy, validated EMC gapmer chemistry, clinical selectivity or a first-in-literature claim. No DOI invented; full text not obtained. |
| Introduction/methodological precedent: reference-sequence off-target annotation | Sciabola et al., 2021, PLOS ONE 16(1):e0238753, [DOI10.1371/journal.pone.0238753](https://doi.org/10.1371/journal.pone.0238753), [PMC7822268](https://pmc.ncbi.nlm.nih.gov/articles/PMC7822268/) | PLOS Materials and methods describes cDNA/unspliced-gene searches, 0/1/2-mismatch annotations and explicitly separates the off-target search from predictive experimental models. It does not validate this manuscript's complete-core ordering or fixed chemistry. |
| Proposed chemistry and interpretation: empirical mismatch-dependent effects | Yoshida et al., 2019, Genes to Cells 24(12), [DOI10.1111/gtc.12730](https://doi.org/10.1111/gtc.12730), [PMC6915909](https://pmc.ncbi.nlm.nih.gov/articles/PMC6915909/) | Human-cell and Discussion paragraphs: 13-mer LNA-gapmer experiments; comprehensive expression analysis plus follow-up qPCR; authors distinguish sequence complementarity and actual expression effects. Their tested chemistry/length and mismatch observations are not thresholds for 16-mer 5-6-5 designs. No efficacy number transferred. |
| Interpretation: sequence pairing is insufficient for cleavage inference | Lima et al., 2014, PLOS ONE 9(7):e101752, [DOI10.1371/journal.pone.0101752](https://doi.org/10.1371/journal.pone.0101752), [PMC4114480](https://pmc.ncbi.nlm.nih.gov/articles/PMC4114480/) | Methods plus PLOS Results/Figures8–9/Discussion: SOD1 minigene, RNA structure/proteins and RNase H1 context affect off-target binding/activity. The study uses a different MOE/DNA configuration. It supplies no validated six-base-gap cutoff or safety margin for these designs. |

API full-text URLs and response SHA256s are in fulltext-receipts.json; metadata request URLs and hashes are in primary-metadata.json, all fetched 2026-10-02. GENCODE50's official [release description](https://www.gencodegenes.org/human/release_50.html), FASTA section, was also read and explicitly includes alternate loci/patches in the ALL transcript resource. Its release-specific description supports the existing corpus sentence; the generic README's older reference-chromosome wording does not override that release table.

## Exact edits and project-record separation

The opening now cites biological primary studies directly. It identifies historical BCR–ABL precedent and PFRED without a new novelty claim. Two brief qualifications distinguish experimentally studied gapmer configurations from the unvalidated 5-6-5 proposal. The model paragraph explicitly acknowledges RNA-level fusion confirmation while preserving catalogue reconstruction limits. The experimental paragraph cites actual cellular/mechanistic results without importing efficacy thresholds. References2 and10–15 are primary publications;1 and3–9 remain clearly identified historical/computational/resource records.

No older 190-design calculation, deposited-junction sequence, historical thermodynamic result, power assumption or manuscript-wide bibliography is represented as freshly audited. The cutoff5, the complete-core ranking, six-base gap, and proposed experiment remain project conventions/proposals. The primary references do not retroactively validate them.

Separate inherited source-map correction for root: item5 of claims-and-change-map.md currently says “self-funding, no external funding and no competing financial interests.” Replace that declaration sentence with: “The author has recorded: ‘This research received no funding’ and ‘The author declares no competing interests.’ These standing declarations are retained.” The revised manuscript copy already retains the correct no-funding/no-competing-interests declarations; no self-funding inference was added. This proposed source-map fix is not a shared-file edit.

## Exact unresolved list

1. Labelle1995 publisher full text was not obtained: DOI opening returned a web-tool inaccessible-page error, not a documented HTTP status. The draft uses only its verified abstract-level fusion claim, corroborated by Brenca's primary study.
2. Skórski1991 full text was not obtained. The PubMed abstract supports historical junction-ASO precedent only; detailed experimental evaluation remains outside this bounded task.
3. This task obtained no nucleotide-resolved USZ22 consensus and no new literal construct sequence. It retains the accepted USZ20 reference-reconstruction/USZ22-unresolved classification; RNA-level confirmation in the model paper is not relabeled as missing.
4. The proposed 5-6-5 chemistry, sequence ordering, ratio cutoff and biological efficacy remain experimentally unvalidated. This is an explicit interpretation limit, not something a citation can repair.

These are the complete unresolved source/interpretation limits identified by this bounded integration. Existing package preparation, AI-use disclosure and required independent ultra review remain as already stated in the draft; no new review or submission clearance is asserted.
