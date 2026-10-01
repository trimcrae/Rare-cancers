# Retained independent review: DATA-IMMUNOSARC-2026-09-30

This is a coordinator transcription of the completed independent review messages, preserving their judgment and execution scope. It is not a verbatim copy of the reviewer's longer original report. Draft review does not establish publication eligibility or repository-gate approval.

Reviewer: /root/review_immunosarc. Writers: /root/write_immunosarc, /root. Exact served model was not observable. Review timestamp: 2026-10-01T01:03:26Z. Checkpoint: 9224028c3f883a4a88b4c4fa6ac46c9a790e71ac.

## Artifact bindings

- research/autonomy/data-opportunities-2026-09-30/drafts/immunosarc-availability-correspondence.md: Git blob 637c917c6163e803742c700025f3914ae0cd4683; SHA256 428a6fe5e192ddb4310db1872dbd2f3cd0c62b12c69b5aae1f00b572298f2679.
- research/autonomy/data-opportunities-2026-09-30/analysis/immunosarc_availability.mjs: Git blob 822909ebcafbad34c8360a19530f66b4e2d13b98; SHA256 343ee1a487b8d8f3fcb52eb47de9201b763c6ff4165bf4b3a1b12b7f11c7de25.
- research/autonomy/data-opportunities-2026-09-30/results/immunosarc-availability.json: Git blob 20b6fe121dfa6f6decf1ae64dc5ffeef274328d5; SHA256 6ca8d7b827ec94c83f8db8e51b991d15ada3daf5bcfa9cbac7fc164a3ee3acee.

## Reader explanation and checked evidence

Question: Which patients have published analyzable values before and during therapy, and what can the released serial-biopsy data support?

Approach and execution: Patient-linked audit of 77 clinical subjects and 133 source sample rows, with assay-specific availability and an exploratory timing check. The reviewer independently reproduced the complete analysis result and checked pinned source/code bindings.

Main finding: RNA scores have 38 on-treatment records and 31 paired patients; numeric CD8 has 32 and 23. UPS has no published on-treatment numeric CD8 values despite some clinical IHC flags. These are availability counts, not proof an assay was never performed.

Main limitations: The source table covers 77 of 84 enrolled patients, no EMC cohort is identified, and individual biopsy dates are absent. A common time-origin shift preserves the illustrated risk sets; no corrected hazard ratio or causal bias estimate is produced.

Next step: Clarify patient/timepoint/assay denominators and make individual biopsy times available before timing-sensitive biomarker analyses.

## Actual prose review

The reviewer read the complete correspondence and found the question, approach, numerical findings and limitations understandable and followable. Scientific meaning and limitations were preserved. Optional expansion of specialist terms was suggested; no mandatory repair.

Decision: pass for continued draft/author review. No unresolved material draft blockers. No full preflight, registered outgoing-prose inventory, rendered-packet inspection, exhaustive novelty determination, venue approval or submission is claimed.
