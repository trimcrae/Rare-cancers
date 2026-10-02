# Independent scientific review of the frozen ASO transcriptome extension

Review completed: 2026-10-02 13:34 UTC. Reviewer: independent Codex worker /root/aso_ultra_review.
Scope: one bounded scientific review of the new extension, not a repeated review of the entire historical ASO manuscript.

## Frozen identity and execution record

- Repository: trimcrae/Rare-cancers.
- Reviewed revision: 0f6d9e896fe90352a1d39f03d96c8567fff30a4d.
- Directory: research/autonomy/continuation-2026-10-02/.
- Primary report: aso-transcriptome-report.md, Git blob 6cb9564bd67c890ef5ef1f95cfb38c5d073754d3; SHA256 e9e140db1eacc9ccd09cd712842c9320d995362343bf865406b7c676ba423157.
- Result: results/aso-transcriptome.json, Git blob 54450defc4fac3fb1b9f159e3157a8f713f47f53; SHA256 ffec759ac33c734d8aa28aa2f71f9f2b5e8296c8ece0e21f8a744606ba1d37ec.
- Baseline: a916dab2979e27f930b417243f021b6c2b2ca371; all-designs.tsv blob ee3b2300ab06851780789f0ea2f990231fb61270, SHA256 f231499b036e4c6b79f729cee0a44a4c482ab6215167e61c2fc0c4a3ceed7799.
- reasoning_effort_requested: ultra. The parent explicitly commissioned the independent ultra pass.
- reasoning_effort_actual: not exposed to this worker; not independently verified.
- model_actual: exact runtime model identifier not exposed. The supplied agent description says GPT-6-based; this is not an execution model receipt.
- Token usage and precise elapsed time: unavailable.
- This review must NOT be relabeled as a verified ultra execution solely from the request or its filename. The coordinator should attach the actual scheduler/session model and effort record, if available, before counting the operating-protocol requirement as satisfied. This is an evidence-record limitation, not an additional scientific finding or a request for another whole-paper review.

The reviewed hashes were recomputed in memory from connector-returned UTF-8 content using SHA256 checked against the standard empty-string and abc test vectors. The result hash exactly matches original_result_sha256 in the independent confirmation receipt.

## Assessment

No scientific submission blocker was identified in the frozen extension. The central claims are supported at their stated strength. This is useful, coherent evidence for inclusion in the existing ASO manuscript as a reference-corpus sensitivity analysis. It does not justify a new therapeutic claim, a new empirically validated ranking system, or a claim of methodological novelty.

The valuable contribution is specific: retaining a fixed design catalogue and ranking rule while broadening the annotated reference corpus changes its descriptive rankings, identifies 19 exact complementary reference matches, and identifies one deposited-sequence design that was an archived final choice. Merely observing monotonic extrema under set expansion is mathematically expected; the catalogue-specific magnitude and identities supply the information. Consolidation with the ASO catalogue is preferable to treating this as a separate discovery paper.

No further narrowing of the report's current scientific conclusion is necessary. Its distinction between sequence annotation and tissue expression/activity, between hypothetical and deposited-sequence evidence, and between changed and disjoint choice sets should survive any manuscript integration. I do not declare submission clearance, waive publication gates, or assess venue permission, cost, exclusivity or the pending full manuscript package.

## Evidence and independent checks

Read the operating protocol first. Reviewed the frozen report, analysis plan, saved complete result, original C++ scanner, Python runner, synthetic scanner oracle, interval arithmetic and tests, both independent verifier implementations, confirmation/execution receipts, annotation evidence, prior result audit, and the accepted baseline design table and catalogue context.

1. Independently parsed all 220 result records and compared nine carried-forward fields against all 220 baseline TSV records: target, antisense, evidence class, control flag, archived gap/Hamming metrics, and archived primary/final flags. No disagreements. Checked all 220 target/antisense reverse complements.
2. Independently derived every union maximum and resolved minimum from the saved strata and archive; every lower/upper bound agrees. Recomputed all 44 ranking groups, including the separate control junction, by minimizing union_gap then maximizing union_hamming among primary ties. No disagreements.
3. Target-only arithmetic is 215 designs, 43 junctions, 212 increased gap maxima, 213 smaller Hamming minima, 19 exact matches, and Hamming histogram 0:19, 1:165, 2:31. No change violates set-expansion monotonicity.
4. Evidence classes are 180 hypothetical designs/36 junctions, 25 deposited-sequence designs/5 junctions, 5 coordinate reconstructions/1 junction and 5 construct-description reconstructions/1 junction. Exact positives are 17 hypothetical plus 2 deposited. Controls are excluded from those totals.
5. Independently computed 42 changed primary sets and 41 changed final sets, but only 15 and 23 disjoint sets. The report does not equate changed membership with universal displacement.
6. The two highlighted target sequences, reverse complements, 22/1 occurrence counts, and archived-selection statuses agree with the result. TCF12 d9 was selected; EWSR1 d6 was not. The reported before/after junction choice sets agree.
7. There are 201 distinct target 16-mers among 215 target design records. All 19 exact-positive targets are distinct. The report consistently counts designs except for the true statement that 19 target sequences match.
8. Static algorithm review supports exhaustive discovery under the stated definition: the rolling 32-bit value represents the last 16 bases; the seed extracts exactly target positions 5 through 10; flank extension occurs only after complete-core equality; the Hamming neighborhood recursion enumerates distinct substitutions through radius three without revisiting position combinations. Invalid windows and record boundaries reset correctly. The independent verifier instead uses an Aho-Corasick automaton. No concrete scientific algorithm defect was found.
9. The original oracle fixtures cover individual mismatch placements, boundaries, ambiguity, sequence aliases, orientation, partitioning and input-length refusal. The 11 interval tests appropriately distinguish unresolved intervals from exact distances. I inspected their implementation and executed receipts; I did not rerun builds or corpus scans.
10. Candidate discovery scanner, runner, interval code and test blob identities match the executed discovery revision b066a7e7bcffe4892c78f2d9462cc70b4d14945b. Candidate independent verifier blobs match revision 5e289f506e5eb5e934192b8c68d69870e67e4b50. Runner SHA256 e611c035efc86aff077473741ff2224f3fb93bf0074673ceb856a288caaa92f8 and verifier script SHA256 593c4efa4e2526fbc404ae7657348aeedf4ed07bdb24dde33f1410ff65a41731 match the frozen receipts.
11. GitHub confirms discovery run 37009409052 succeeded. Independent ASO job 110850663697 in run 37011070408 succeeded. That parent run is globally failed because its separate foundation job failed; this does not invalidate the ASO job. No global workflow-success claim should be inferred.
12. Independently retrieved current Ensembl lookup and cDNA API responses, without UI or bulk files. ENST00000795030 returned version 1, lncRNA, parent ENSG00000266850, length 1336; bases 346–361 are ATCTGATGGATATGCC. ENST00000378334 returned version 3, processed_pseudogene, parent ENSG00000234429, length 6848; bases 3420–3435 are AGCAGAAGCCCACTGC. These independently support the representative annotation/sequence claims. They do not independently prove release equivalence, 22/1 total occurrence counts or therapeutic exposure.
13. Current GENCODE documentation confirms that its ALL transcript FASTA includes reference chromosomes, scaffolds, patches and alternate loci. Main-chromosome GTF statistics report 644292 transcripts; those statistics have a different scope from 670670 ALL FASTA records and do not contradict the census. GENCODE TAGENE documentation supports the narrow description in annotation-evidence.md.

## Findings

### E1 — Editorial suggestion: make the exact core/window definition self-contained

Artifact/evidence: aso-transcriptome-report.md lines 39–47 states the six-base-core metric but leaves the proposed architecture, core indices and complete-window eligibility to the supporting plan. aso-analysis-plan.json lines 23–26 and 35 specify target orientation, proposed 5LNA-6DNA-5LNA, zero-based positions 5:11, complete unambiguous 16-base windows and ambiguity exclusion.

Consequence: a reader of the report alone cannot reconstruct whether a shorter terminal transcript tract, an ambiguous flank, or an arbitrary six-base tract is eligible. The linked evidence and code resolve this, so this is not missing computational reproducibility and not a submission blocker for the reviewed package.

Smallest correction: one methods sentence giving proposed 5-LNA/6-DNA/5-LNA architecture and defining the descriptor over complete unambiguous 16-base transcript-oriented windows, with the core at target positions 6–11 one-based. Keep the architecture explicitly proposed. No new computation or review cycle is needed.

Disposition: optional; coordinator may accept on manuscript integration.

### E2 — Editorial suggestion: state that design counts include repeated sequences

Artifact/evidence: aso-transcriptome-report.md lines 22–28 describes 215 designs; results/aso-transcriptome.json $.designs, filtered by control=false, contains 201 distinct target values. For example, EWSR1_e12__NR4A3_e3:d8, TAF15_e11__NR4A3_e3:d8 and FUS_e10__NR4A3_e3:d8 are the same target sequence, with distinct catalogue identities.

Consequence: readers might mistake the design denominator for 215 independent or chemically distinct ASOs. No inferential independence assumption is used, and the report does not explicitly claim 215 unique sequences. The 19 exact-positive sequences are distinct, so no reported headline count is wrong.

Smallest correction: add “The 215 design records comprise 201 distinct target sequences” beside the denominator, if useful for the manuscript. Do not change the predeclared design-level endpoints or deduplicate retrospectively.

Disposition: optional denominator clarification, not a blocker.

## Negative or dismissed concerns

- No second exhaustive census of nonzero Hamming minima or global gap maxima exists. The report explicitly states this at lines 16–18, 54–58 and 117–119. The implementation, synthetic oracle, baseline reproduction and direct witness verification support the discovery results, while witness checks alone do not prove global optimality. Requiring an additional full census merely to make review “independent” would exceed the bounded review without a demonstrated defect.
- The independent count census verifies exact counts for 220 designs x 2 GENCODE strata, not 440 biological samples. The text calls these design-stratum counts; no sample-size inflation claim was found.
- Transcript aliases, repeated windows, isoforms and alternate loci can multiply occurrences. The report accurately treats 22 RBBP8-AS1 hits as record-window occurrences and does not infer 22 genes.
- Noncoding/pseudogene annotation neither proves a harmful substrate nor warrants dismissing a match. Current wording preserves this uncertainty.
- Mature-transcript coverage is incomplete for intronic pre-mRNA, individual variation and actual exposure. This is already stated. Hamming distance excludes bulges and mismatch-position energetics; the result is explicitly a fixed simplified descriptor, not a biological risk score.
- More references necessarily make maxima nondecreasing and minima nonincreasing. The report presents this as a consistency check, not a surprising biological effect.
- No random-control cohort, significance test, confidence interval or wet-lab experiment is required to establish this deterministic fixed-catalogue comparison. Such additions would answer different questions.
- The original parent-only calculations are not refuted for their stated reference set. The report correctly frames coverage dependence.
- An exact match among hypothetical joins does not establish a patient fusion. Evidence classes are retained and the report avoids that claim.
- Prior broad recommendations to confirm extrema do not turn the now narrower, accurately described independent exact-count verification into full independent validation. No such stronger claim is present.

## Sources and scope of citation review

- Frozen report and result: https://github.com/trimcrae/Rare-cancers/tree/0f6d9e896fe90352a1d39f03d96c8567fff30a4d/research/autonomy/continuation-2026-10-02
- Baseline catalogue: https://github.com/trimcrae/Rare-cancers/blob/a916dab2979e27f930b417243f021b6c2b2ca371/research/release-candidates/PUB-ASO/2026-09-30-full-catalogue/CATALOGUE.md
- GENCODE resource definition: https://www.gencodegenes.org/human/
- GENCODE main-chromosome statistics: https://www.gencodegenes.org/human/stats.html
- GENCODE TAGENE definition: https://www.gencodegenes.org/pages/tags.html
- Ensembl lookup and sequence endpoints for ENST00000795030 and ENST00000378334, using expand=1 and type=cdna respectively: https://rest.ensembl.org/documentation/info/lookup and https://rest.ensembl.org/documentation/info/sequence_id
- Primary experimental context: Hagedorn et al., Nucleic Acids Research 2018, doi:10.1093/nar/gky397, https://pubmed.ncbi.nlm.nih.gov/29790953/ . This supports the need to distinguish candidate sequence complementarity from experimentally measured activity and to consider factors beyond mismatch counts; it does not validate these EMC designs.
- Prior public catalogue abstract: https://aixiv.science/abs/aixiv.260918.000004 (190 designs/38 junctions, normal-parent comparison). The new analysis is an extension of the same program. This read does not establish publication permissions or perform a comprehensive novelty search.

GENCODE and both representative Ensembl records were independently checked during this review. HGNC/NCBI identities were supported by the frozen annotation evidence; web attempts encountered an inaccessible HGNC API and NCBI anti-bot page, so I do not claim a fresh independent HGNC/NCBI confirmation. Ensembl directly confirms the stated parent IDs and transcript biotypes. Citation/claim relationships are adequate for this bounded extension; biological-method context can be integrated from the existing manuscript, without claiming that the general need for transcriptome screening is new.

## Remaining gates and operational limits

The reviewed frozen candidate does not include completion of normal preflight, generated-figure visual verification, the actual full publication gates or a complete outgoing manuscript review. Those pending gates are not silently passed by this review. Actual model/effort execution evidence must be supplied before the coordinator makes the protocol-specific ultra-review readiness claim.

No corpus download, build, rendering, UI, screenshot, headless browser or research artifact edit was performed. Quiet in-memory arithmetic and small API requests were used during the standing 06:00–10:00 America/New_York restricted period; the September 12 exception was not applied. An initial local git ls-tree -r -l on a partial clone unexpectedly initiated Git lazy-fetch/auto-pack behavior; the owned command was stopped and the coordinator was notified. Exact fetched objects are unknown; no repository cleanup or unrelated process interruption was attempted. Thereafter all remote repository reads used the GitHub connector. C: free space was measured at 9803907072 bytes; only this small private review file is deliberately written.
