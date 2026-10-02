---
id: DOC-CHECKPOINT05-HLA-COMPLETED-RESULT
title: "Historical canonical HLA search-space result"
kind: memo
status: live
date: "2026-10-02"
last_verified: "2026-10-02"
purpose: "Record the bounded checkpoint result and its evidence."
audience: [maintainers, autonomous research agents]
scope: "Named public sources and exact computations; no publication clearance."
---

The complete deposited `sp_21_04_2020_decoy.fasta` contains 20,365 SwissProt targets and 20,365 decoys. None contains any of the four frozen provisional sequences NMPCVQAQY, QQNMPCVQAQY, SYGQQNMPCVQAQYS or DMPCVQAQY as an exact within-record substring. [Cloud execution](https://github.com/trimcrae/Rare-cancers/actions/runs/37041943617) passed at 9918aa902d96128adcc86009174645d0300f59f4 in 17.46 seconds. Six synthetic tests, including an exhaustive short-pattern oracle, passed before dispatch. The 27,229,450-byte FASTA has SHA256 d351fdc0add26d0a1eb6c2214ee9bf597096387c866f2d6e6ed4507a7a090dcd; its computed SHA1 agrees with the PRIDE checksum, whose algorithm was not explicitly named in metadata.

All 483 deposited RESULT records refer to this FASTA through the README. That association does not prove every run's settings. The paper's 20,365-protein/Percolator 3.4 description differs from project metadata reporting 20,416 proteins plus contaminants/Percolator 3.1.1. The observed target count agrees with the paper, but does not resolve per-run provenance or the separate cryptic search database.

The exact queries are absent from this deposited canonical search space. Their absence in the processed peptide list consequently cannot establish a measured negative from that search. This is a search-space and donor-coverage methods result, not demonstrated absence of presentation or clinical safety. Fusion-query biological authenticity remains unverified. Length flags apply only to the paper's length bounds, not mass, charge or detectability.

[Working draft](manuscript-draft.md) integrates this new question while preserving all baseline donor calculations and the original manuscript. [Review](review/review.json) and [prose review](review/integration-prose-review.json) passed within their stated scope. The optional test-description correction was applied exactly. The earlier findings.md remains a dated pre-execution intake memo. Source ZIPs preserve primary XML, PRIDE metadata and README with member digests; extract as their adjacent manifests specify. No full scientific rerun or submission gate was performed.
