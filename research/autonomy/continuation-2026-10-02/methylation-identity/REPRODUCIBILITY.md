---
id: DOC-METHYLATION-IDENTITY-REPLAY-20261002
title: Reproducing the primary methylation identity audit
kind: memo
status: live
level: cross-cutting
purpose: Locate preserved primary metadata and exact executed identity results.
scope: Bounded October 2 checkpoint; no publication clearance.
audience: [maintainers, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

The measured result and source audit are in findings.md. This is metadata-only work. No raw array values, classifier fitting or prediction-loss replay occurred.

metadata-inputs.zip contains the seven exact primary responses listed in retrieval-receipts.json: four publisher workbooks, two article XML responses and the E-MTAB-9875 SDRF. Archive bytes: 286330; SHA256: `959139b982d8a1616d01155d6a5005b122a27809d6cbfc873a999295bad4971d`. The worker's receipt records original individual input and output digests. Its initial-audit.json and workbook-rows.json were intermediate private summaries; all primary bytes needed for the joined result are retained here.

To reproduce in a separate scratch directory, copy this folder, verify the archive digest, extract metadata-inputs.zip into that same directory, and run `python compare_metadata.py` with Python and openpyxl. The script checks primary-input digests, channel pairing, unique identities and expected complete cohort counts before emitting the crosswalk and overlap files. Source retrieval may be replayed separately with audit_identity.py, but fresh responses must not silently replace these frozen bytes. Source drift should be reported.

The saved 2,491-row crosswalk establishes identifier-level array separation only. Accession-local individual labels are not common patient identifiers. The source authors' distinct-patient assertion is retained explicitly.

Independent source-field review found no missing cohort rows or malformed array identities. The SDRF parser retains distinct field names in its schema summary; repeated unused header positions (such as Protocol REF) collapse in DictReader. The identity columns used for the join are unique, so this does not affect the result. See independent-review.json for the exact scoped checks and their limits.
