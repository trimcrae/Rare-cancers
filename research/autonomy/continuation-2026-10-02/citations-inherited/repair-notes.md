# Inherited citation provenance — 2026-10-02

All 14 requested identifiers have actual successful identity-matching metadata responses in `primary-metadata.json`: seven DOIs, five PMIDs, one PMCID and one GEO accession. The receipt stores UTC retrieval timestamps, original response byte lengths and SHA256 digests, exact request/final URLs, and selected returned metadata. Digests cover response bytes before parsing; complete responses are not retained. Bibliographic identity verification does not establish correctness of the scientific claims citing these sources.

Crossref registered metadata verified five journal/preprint DOIs directly. One Crossref request returned 429; this failure is preserved and is not evidence of identifier absence. A subsequent Europe PMC DOI query returned the matching Cancer Immunology, Immunotherapy record. Europe PMC supplied all five PMID and the PMCID records. The PRIDE archive API returned both PXD019643 and its matching project DOI. GEO's own SOFT endpoint returned the exact series accession, title and publication PMID. No unsupported or mismatched identifier remains among this requested set.

## Integration

Commit `primary-metadata.json` as the substantive fetched evidence. Root requested successful receipts rather than expanding the ledger, so no ledger status changes are proposed. The failed Crossref record may remain: its `url/status/attempts` shape is recognized by the linter's failed-fetch redaction. Successful records carry matching returned identifiers; PMID records also carry canonical PubMed URLs, since bare JSON `pmid` fields do not anchor in this gate. Do not commit a locations-only record as source evidence.

Reviewed actual `research/manuscripts/lint_citations.py` at candidate e65c28bd427623450e3d425d4ff55aa4caeebc83 (blob b5d8e2774589ce9b17e7119eea0e6c14800610c5), and existing ledger schema (blob efdf43553158afb8d45fc0e8b404f4cb736984c6). The gate scans tracked JSON/JSONL excluding the ledger and type/retraction caches. This work neither executes nor claims a passing repository gate; root must integrate and rerun normal preflight.

## Identity distinctions worth preserving

- Research Square `10.21203/rs.3.rs-10374394/v1` is itself the Crossref-returned registered DOI, type `posted-content`, published 2026-07-17. Retain `/v1`; do not apply the separate medRxiv canonicalization rule to this identifier. This is a preprint, not a verified peer-reviewed article.
- PMID33858848, PMC8054196 and DOI10.1136/jitc-2020-002071 all identify the HLA Ligand Atlas paper. The matching PRIDE project DOI is 10.6019/PXD019643. PRIDE reports publication 2021-04-16; that dataset date is distinct from article publication dates. Crossref online date is 2021-04-15; Europe PMC's coarse April date is preserved as returned.
- GSE285944 is the UPS/myxofibrosarcoma immunogenic-features dataset, linked by GEO to PMID40601026; Europe PMC supplies matching DOI10.1007/s00262-025-04123-y. GEO public date 2025-06-30 precedes the returned article date 2025-07-02.
- PMID35710741 identifies the bempegaldesleukin/nivolumab pilot, DOI10.1038/s41467-022-30874-8. I inspected the inherited ImmunoSarc correspondence: it correctly identifies NCT03282344 and explicitly distinguishes IMMUNOSARC1. No citation replacement is warranted.
- PMID35705558 is the Foundation sarcoma profiling paper; PMID35839778 is the 949-cell-line proteomic map; PMID41895280 is the 2026 Cancer Cell 50,000-tumor driver-alteration paper. The returned titles and dates are retained in the receipt.
- DOI10.1002/aisy.202500778 is Mepylome (online 2025-12-18, print March 2026); DOI10.1038/s41467-025-61272-5 is the SE(3)-equivariant ternary-complex prediction paper; DOI10.1371/journal.pone.0161879 is DockQ. No numerical research outputs changed.

The small collector and one-request completion helper are optional reproducibility code, not additional source evidence. The original collector completed all retrievals and saved the receipt, then hit a Windows console Unicode-print error; only its diagnostic print was repaired. The completion helper added the matching Europe PMC response for the rate-limited DOI and explicitly checked both PRIDE accession and DOI. No retrieval was rerun merely to fix console output.
