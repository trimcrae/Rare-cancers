---
id: DOC-TRIAL-ADJUDICATION-SEMANTIC-CHECK-20260905
title: Focused coordinator verification
kind: memo
status: live
date: 2026-09-05
last_verified: 2026-09-05
purpose: Check the changed adjudication claims and describe verification coverage.
scope: Frozen trial reference; focused semantic verification rather than clinical validation.
audience: [maintainers, autonomous research agents]
---

# Focused coordinator verification

The coordinator assessed all 49 independent label rationales, the adjudication construction code and its two label differences, and reread the complete saved eligibility, study description and arm description for NCT05918640, the single trial underlying both differences. This is a focused check of changed claims, not a claim of a second full coordinator reading of all 37 records. The fresh model reader reports that full reading; the previous integration also checked all 49 first-reader rationales and five complete records.

The DSRCT change is supported when disease scope and enrollment availability remain separate. Phase 1 permits documented FET-fusion solid tumors, and the registry explicitly discusses DSRCT. Its exclusion lasts until at least three non-DSRCT participants have enrolled without dose-limiting toxicity. The saved text does not establish whether this condition has cleared. The final label retains compatible disease scope and an unknown hold-release field; it does not assert available enrollment. The initial label and its warning against binary negative scoring remain intact.

For synovial sarcoma, the phase-1 solid-tumor wording is broad but a documented EWSR1, FUS or TAF15 fusion is mandatory. Supplied SS18::SSX alone does not satisfy that gate. The final broad-histology label is interpretable only together with the unestablished molecular field and explicit exclusion from uncomplicated positive or negative scoring. No additional FET fusion or acceptance of such a case is demonstrated. A downstream evaluator must consume those fields, rather than treating every non-exclusion label as positive. Phase 2 remains Ewing-specific.

The coordinator's independently written verifier resolves all 222 copied registry modules and 60 exact excerpts against 23 original compressed pages, reconstructs all 49 pair memberships, and verifies that every first-reader and frozen independent-reader row is preserved byte-equivalently as parsed JSON. It checks the 49 decision records and reports both label differences. These checks establish source fidelity and data consistency; neither check count nor model agreement is clinical validation.

The worker's execution log shows the independent-label generation command at 19:15:49.223 UTC, its freeze receipt at 19:15:53.641842 UTC, and the first command opening the original `reference.json` at 19:16:04.315 UTC on 2026-09-05. Earlier visible commands read the allowed source packet and protocol, including systematic packet ranges and focused rereads. The coordinator inspected tool-call chronology, not private reasoning. Independence means a fresh model task with no prior label reading before the freeze; the files were not technically access-controlled. The phrase “inaccessible to this session” in the worker reference must be understood as the procedural reading restriction, not a demonstrated filesystem barrier. This is neither blinded human adjudication nor an inter-rater reliability study.

No source uncertainty is resolved merely by assigning a field. Missing external protocols, additional biomarkers, closed cohort lists, study purpose and snapshot status remain necessary inputs to the next benchmark design. The 149-pair expansion and any retrieval comparison are still outstanding. This verification supports reference development, not preprint readiness.
