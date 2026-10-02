---
id: DOC-CHRNA6-SPECIMEN-CROSSWALK-HANDOFF-20261002
title: CHRNA6 discovery and validation overlap evidence handoff
kind: memo
status: live
date: 2026-10-02
last_verified: 2026-10-02
purpose: Preserve the exact public-source availability result and unresolved specimen crosswalk.
scope: Source methods/availability audit; no expression or tissue-assay reanalysis.
audience: [maintainers, autonomous research agents]
---

The required discovery/validation specimen crosswalk was not obtained in this bounded public-source
cycle. Specimen overlap, patient overlap and independence remain unknown. This is a missing-input
result, not evidence that the study lacked independent validation or never published a crosswalk.

Europe PMC and Crossref identify the intended study, “CHRNA6 RNA In Situ Hybridization Is a Useful
Tool for the Diagnosis of Extraskeletal Myxoid Chondrosarcoma,” PMID 38447752, DOI
10.1016/j.modpat.2024.100464. The indexed primary abstract says the authors “we analyzed genome-wide gene expression microarray data to identify candidate biomarkers based on differential expression in EMC in comparison with other mesenchymal neoplasms.”
That span establishes a described microarray discovery step. It names no dataset or specimen
mapping; it cannot determine whether the recovered GEO cases contributed to that discovery.

The observed Europe PMC record has no PMCID and marks the DOI full-text locator “Subscription
required.” Its inPMC/open-access/data/supplement flags are index metadata, not proof that article
methods, supplements or rosters do not exist elsewhere. Crossref supplies the publisher's
PII S0893395224000449 and text-mining URLs. Those API URLs were not used.

The returned publisher landing page is an HTTP 200 response, but its title is “Redirecting” and
its body contains JavaScript/meta redirect instructions and a text/data mining reservation.
It supplies no acquired article methods or specimen roster. No script was executed, no redirect
preferences were followed and no subscription/TDM access was bypassed. Treating that successful
HTTP transport as full-text evidence would overstate what was recovered.

[evidence.json](evidence.json) retains the complete raw UTF-8 response bodies, HTTP/robots
receipts, dates, byte counts, SHA256 hashes and raw-bound metadata projections.
[source-findings.json](source-findings.json) binds the quoted span and access interpretation to
exact source hashes and JSON pointers. Both are public-source provenance records; neither is a
new patient dataset. The exact missing inputs are the discovery sample roster, a mapping to
the CISH validation cases and the existing cohorts, and accessible primary methods/supplement
bytes that can support or bound reuse.

One source cycle acquired three text records on 2026-10-02 from 01:35:58 to 01:36:00 UTC:
Europe PMC 8,256 bytes (SHA256 fc5da76000aff1c0b5d92a6a3224e3b8748849036d441d6b0950eb6b045defd0); Crossref 14,975 bytes
(f558c48c50182f9c9140ffb992c15f3ae73ef6192b9ef1fc8e062986b03dc072); and publisher redirect HTML 2,645 bytes
(9f51b8e66e56c34426368f5a2e935b5e2aa5795ef7fec0b457bbf4c966de3496). Robots were checked; Crossref's robots endpoint returned 404,
and the other two allowed the requested paths. No source was retried. The original cycle completed in about 2.2 seconds under the original
soft 180-second alarm and four-minute workflow hard stop. The original alarm raised an ordinary
TimeoutError that an error handler could catch; it was not a hard process deadline. Independent
review identified this distinction and a robots-decision replay omission. The repaired tooling
uses a BaseException deadline that propagates through both error handlers, binds each robots
receipt to its requested source origin, and replays the acquired 200 policy. These changes are
validated offline; they do not retroactively describe the original acquisition's enforcement.
The committed evidence
prevents future reacquisition by this workflow. Its output has 41,711 UTF-8 bytes, SHA256
bda7d71678705ba84f82381dba49a3d47eacbfa4fb9cea4552def0e837919ffb.

Original [run 36951680169](https://github.com/trimcrae/Rare-cancers/actions/runs/36951680169),
job 110665777636, completed SUCCESS at source 98051296780d146e862810a2f3daf75e055f266b.
Actual Python 3.11.16 execution passed 26 synthetic provenance/unsupported-inference cases,
the finite source acquisition, its immediate offline check, normal
`PREFLIGHT OK (fast gates only (doc + artifact linters))`, and clean tracked diff.
The complete original log is preserved in [acquisition-original.log](acquisition-original.log).
This validates source integrity and repository fast gates, not full scientific or publication suites.
Settled [run 36952479957](https://github.com/trimcrae/Rare-cancers/actions/runs/36952479957),
job 110668444392, completed SUCCESS at 9bfd7112bf76f184d632e4d72fea3fa95f5e9d34.
Actual execution passed 32 Python cases, committed-evidence offline validation, normal FAST
preflight and clean tracked diff. The acquisition and artifact-upload steps were actually
skipped. The final tests exercise robots policy/origin refusal, missing-policy handling and
hard deadline propagation through both error handlers. Its full original log is preserved in
[settled-original.log](settled-original.log); [validation-receipt.json](validation-receipt.json)
records exact commits, source/code/log Git blobs, run/job receipts and scope limitations.

The coordinator independently extracted the original output and checked its 41,711 UTF-8
bytes and SHA256, all three raw source sizes/hashes, exact study identity and all four
source-findings observations against raw JSON pointers or substrings. The committed evidence
was byte-identical to that original output. Root cleared source methods and prose at
9bfd7112, including handoff blob 939d1ac46c00e006a4ab7018bc4c396e5aa7b649 and derived findings
blob 77f9fe60b78adafa5e072c883f0fa69c1e862e81. Root also reviewed the named robots/deadline
repair and final handler fixture. This is independent LLM review, not human scientific
validation or a new whole-paper review seat. Only operational completion/receipt wording
and the findings' authorship-review status change afterward; source observations and bytes
are unchanged. This bounded task is complete, no task job remains running, and ownership
has returned to the coordinator.

The existing abstract-only marker evidence and completed 42-value GEO source projection were reused.
The historical readiness packet, seven excluded records, frozen analyses, immutable preregistrations,
manuscripts, paid fleet, no-GPU/publication guards and shared ownership records are untouched.
Fresh base main is 7f0971a331272695dcfe4b2a7fac554185b398d9; its full ledger contains 415 entries and
zero non-null owners, and the legacy driver remains disabled. This is an isolated reviewable branch,
not a remote legacy claim or scheduler cutover. No PR, main merge, publication, model inference,
paid API job, GPU dispatch or separately billed compute was performed.

Stop here on the unchanged source fingerprints. Reopen this overlap question only when a distinct
authorized accessible primary methods/supplement or crosswalk becomes available. Otherwise choose
a different bounded evidence route; an unresolved crosswalk cannot support an independent-validation
label, and different identifiers alone cannot resolve it. The next candidate route is authoritative
CHRNA6 coverage and reference-pool compatibility for the remaining legacy two-colour GPL3290 panel,
only after inspecting its current completed outputs and ownership; do not rerun existing expression
kernels or combine incompatible measurements.

AI authorship: Codex AI assistant. Model/effort IDs and subscription usage are not exposed.
No local shell/managed environment was available. Execution used hosted CPU source retrieval and
Python checks, with no clinical, classifier, efficacy, safety or therapeutic-window conclusion.
