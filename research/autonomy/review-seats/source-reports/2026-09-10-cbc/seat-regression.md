# ASO CBC independent regression seat

Verdict: **PASS WITH SCOPE LIMITATIONS**. No blockers or P1 findings established.

Central claim verdict: **supported**, within the executed scope and limitations below.

Root subsequently reports actual spawn configuration: gpt-6-astra / medium. This is root-provided metadata, not deployment introspection by this seat.

Computational NR4A3 junction-gapmer designs frequently permit mature-parent pairing through their complete DNA gap, while threshold-sensitive selection and exon-terminus controls leave biological selectivity and disease-specific excess unresolved.

Commit: 1f717f120724ad0d0442f0cf24d565871b52afb6

Document: research/manuscripts/aso/cbc-20260910/manuscript.md

Document SHA256: 9154a93be06ad7e34990f26e202b0c70e69c1d9b9b14b539a8da850c752e9d04

Formal digest: 5b474a4a3ba97f7e9e4fed02114009f992a1629f82f22aa6a492353d2af21f9d

Fileset: 73e8ae47e0b253ae4fdd0cae5529e62ab6c7d4f8da638d94d328c92e1c9c357e

Model: GPT-6 family per system identity; exact deployment identifier not independently exposed in this seat context. Effort: Inherited from parent; exact configured effort not exposed, so no ultra claim is made.

Blind context: No prior/current review report or visual-QA findings were read; filenames of review records appeared in inventory only. Historical annotations describing earlier reviews and corrections were encountered in scientific source aso_parent_gap_pairing.py and aso-control-oligos.json, and withdrawal/correction history in the manuscript and SI. This is an independent review with that disclosed exposure, not history-free context. No cross-talk with other reviewers. Parent supplied pin, expected identity hashes, and scope, but no expected scientific outcome.

## Hash verification

- Independently hashed all 29 frozen-candidate.json files and checked their byte lengths; zero mismatches. QA/report-like files in that set were hashed as opaque bytes only, not read for findings.
- Recomputed fileset digest using stored files-array order, path + NUL + SHA256 + newline; matches declared digest.
- Recomputed formal MD/DOCX/PDF digest with repository-relative lexically sorted paths, path + NUL + SHA256 + newline; matches supplied digest.
- Verified original/bound DOCX, PDF and PNG bytes and all three endpoint-binding hashes. Verified registered MD SHA256 and exact equivalence to original MD after removing only three bold label markups.
- Read actual baseline submitted DOCX from git object at 3dc59c67654a4dfc5a6d0b842f12a732e6aeda89 and independently matched SHA256 7fe0033347e3825678394082157b8b60e5cc4edcdd122061d02d8d5a28d060c7.

## Executed review

- Read complete main manuscript including 24 references, two tables and figure legend; complete Supplementary File 2 PDF text; packaging builder, source-evidence-map, endpoint-binding and September 4 build_data.py/data-build-stamp.
- Compared baseline and candidate DOCX paragraphs and all table cell text. Scientific body paragraphs and table cells are retained. Differences are declared title, abstract, running title, section names/order, authorship wording and AI section heading.
- Extracted all 20 PDF pages and compared every nonempty DOCX paragraph after whitespace normalization and removal of standalone page numbers: zero missing paragraphs. Tables 1/2 and figure legend text checked in PDF. DOCX contains one embedded 212301-byte PNG; separate figure formats exist and hashes pass. This is textual/structural checking, not visual layout certification.
- Compared all non-comment sequence CSV lines against canonical repository source: exact equality, 782 rows. Named reagent sequences, margins, TFG duplexes 8/9, and model differences 51.3-24.7=26.6 and 60.7-24.7=36.0 agree with Table 1.
- Read mature-parent matching algorithm and per-design evidence via git show. Independently reimplemented contiguous whole-gap search in memory, reconstructing mature parents from committed exon spans. All 190 longest duplex lengths agree with committed evidence. Independently recounts 87 >=10 bp, including 61 whose longest-parent label is NR4A3.
- Independently recomputed both controls: longest duplex lengths 6 and 7; length, terminal bases and dinucleotide counts preserved. Table 2 matches control records.
- Confirmed main text and SI consistently label ten-bp threshold and proposed selectivity/power conventions, no laboratory work, unresolved cell junctions, and chemistry limitations.
- Attempted DOI retrieval through web tool; safe-open error prevented live public archive verification. No conclusion that DOI is broken is drawn.

## Limits

- No full CI, broad regeneration, external alignment/genome reruns, or new checkout. Reproduction is scoped to parent duplex computation, controls and unchanged numerical records; not a fresh replay of every screen.
- No visual PDF rendering or typography certification performed by this seat. No journal submission or external archive availability certification.
- Null ensembles, near-match/genomic loads, coverage and proposed power numbers were read in the complete manuscript but not independently recomputed in this finite regression seat.
- MD and PDF consistency is backed by readback identity and DOCX-to-PDF text checks; markdown syntax itself is not a byte-equivalent representation of DOCX.

## Optional recommendation

For public-reader convenience, provide a durable direct locator for the preserved September 4 build_data.py and data-build-stamp.json alongside the historical DOI. Their local existence and derivation were verified; live public accessibility was not.

Only these reports were written; scientific payloads were unchanged.
