# Independent bounded Lee checkpoint verification

Verdict: SUPPORTED scientific conclusions, with one minor narrative coordinate correction before integration. No substantive sequence, assay or outcome defect found.

Frozen writer: C:/Users/mcrae/.codex/worktrees/lee-sequence-assay-20260906/EMC-Research; base ac789abf1029d995c364d93a459f286595707568. Reviewed packet research/autonomy/lee-sequence-assay-2026-09-06. Its output-manifest.json SHA256 is cdc2ff2b9759d7bf1bcdd1a508db61fa25576f27016873c4a9bded22b3da3486. Requested routine medium review; precise runtime model/effort not independently exposed. This is not a whole-paper ultra pass or submission authorization.

## Smallest correction

In result.md, first paragraph under Verified sequence result, change NUTM1 right-flank positions483–509 to positions483–510. The displayed right flank CATCTGCATTGCCGGGACCGGATATGAG contains28nt and uniquely starts483. The reconstruction code already uses the correct entire sequence; the junction coordinate483, exon3 annotation, full fusion, all guide and PCR results are unaffected. Update the output manifest after this prose-only repair. This is a narrative coordinate typo, not a reason for another scientific review cycle.

## Actual independent checks

Read specification, result, manifest, provenance/retrieval records and all four worker scripts. Executed my own independent_check.py; did not execute analyze.py or verify.py. The separate script parsed GenBank ORIGIN records, enumerated annotated exon features, reconstructed the fusion, and used overlapping regular-expression matches for all guide and primer sites. All245 assertions passed; final calculation took0.491seconds and completed2026-09-06T22:43:18.602034+00:00. Total review approximately6minutes; initial wall-clock time was not instrumented.

Visually inspected primary main Fig2 and retained rendered S3 and S6 pages. Independently transcribed their colored junctions and primer pairs, and checked primers against fresh extraction from retained S3 PDF. GenBank exon enumeration places BRD4 exon11 at2270..2380 and NUTM1 exon3 at483..1191. Fig2 flanks uniquely start2355 and483. Reconstructed NM_058243.2:1..2380 plus NM_001284292.2:483..4109 exactly equals supplied FASTA.

All15 B4N19nt cores uniquely cross the full reconstructed junction, from3/16 to17/2; all antisense cores are reverse complements. Neither orientation string has a full match in any of the four specified parental records. B4N#15 starts2364 and ends2382. All16 SS cores uniquely cross the displayed S6 junction, from2/17 to17/2. Full SS mappings and both SS primer verdicts remain null/unverified. The retained article/supplement searchable material contains only the four BRD4/NUTM1 accessions, no versioned SS18/SSX1 accession. No replacement SS reference was inferred.

Independent inward-facing exact PCR calculation agrees for every supplied template/pair: wild BRD4 predicts114bp4910..5023 on both .2 and .3, with neither exact primer binding site present on reconstructed fusion; wild NUTM1 predicts145bp429..573 on both .1 and .2, no fusion amplicon; fusion assay predicts65bp2359..2423 and no parental amplicons. S3 primer target labels, forward/reverse orientation, and accession discrepancy versus article are preserved.

Checked byte sizes and SHA256 for all20 manifest entries, five successful new retrievals and nine inherited source/member files. Compared frozen designs, outcomes, source manifest and XML against git base content (allowing checkout newline translation); all agree. All93 joined outcome dictionaries equal the immutable CSV rows as an exact multiset and are assigned to the correct design. All31 second-parent placeholders remain unmeasured, with no invented values. B4N#15 parent0.3473684211 (reading0.3263157895..0.3684210526), fusion0.0736842105 (reading0.0526315789..0.0947368421), and absent second parent are unchanged.

The narrow B4N#15 interpretation follows: apparent measured-parent loss persists after excluding an exact-sequence fusion amplicon for the named BRD4 pair. It does not establish empirical PCR specificity or causal/direct parent targeting. The report explicitly retains unknown Ct transformation, reading uncertainty distinct from source SD, unresolved replicate identity, censored SS#4, and absent second-parent outcomes. Zero exact matches are scoped to four records, not genome-wide or biological selectivity. No clinical/ASO/EMC efficacy claim follows.

Two verifier-development assumptions were corrected locally: Windows default text decoding made an XML decoded-text comparison fail despite identical source bytes, and GenBank exon records lack explicit /number qualifiers so numbering was derived from ordered exon features. The right-flank off-by-one prose error was then identified and recorded above. No scientific packet or tracked file was edited; no commit, contact, retrieval or whole-repository test was performed. No computation remains running.

Outputs: independent_check.py, independent-results.json, and this review.md, all in the assigned external verification directory. Stop condition reached. Coordinator may apply the one-character coordinate correction and regenerate the manifest during integration.
