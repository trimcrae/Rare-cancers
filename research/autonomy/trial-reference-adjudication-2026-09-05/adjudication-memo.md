---
id: DOC-TRIAL-REFERENCE-ADJUDICATION-2026-09-05
title: Independent adjudication of the frozen trial reference
kind: memo
audience: [maintainers, autonomous research agents]
date: 2026-09-05
status: live
purpose: Record independent source judgments and the resulting adjudication.
scope: Frozen 49-pair registry reference; no patient eligibility or publication clearance.
last_verified: 2026-09-05
---

The fresh-session review completed all 49 diagnosis-trial pairs across 37 trials. The final reference preserves 33 metadata-sample memberships, 18 purposive challenge memberships and two overlaps. No additional pairs were silently labeled. All work was offline, inside this directory, using the committed saved registry records.

`independent-labels.json` was frozen at 2026-09-05T19:15:53.641842+00:00 with source evidence and protocol hashes before `reference.json` was opened. `independent-freeze-receipt.json` records that boundary. The session knew the diagnoses, defining molecular scope and challenge anchors. This is an independent model source judgment, not human clinical review or a claim of perfect blinding. An initial oversized allowed-packet read was truncated before the worker's own reading protocol; the protocol discloses this and all required record sections were subsequently read systematically. Truncated systematic output sections were reread.

Two primary labels differ from the first reader, both for NCT05918640:

- DSRCT: retain explicit diagnosis-compatible phase-1 scope and represent the safety lead-in as a **conditional hold whose release is unknown**. The source does not establish an unconditional exclusion or that enrollment is currently available. Phase 2 remains Ewing-only.
- Synovial sarcoma: retain broad solid-tumor histologic scope, with the additional FET fusion requirement **unestablished**. SS18::SSX does not satisfy that gate. The first reader's uncertainty is preserved as molecular compatibility unknown, and the case is excluded from uncomplicated positive/negative scoring. This is a taxonomy resolution, not new evidence that SS qualifies.

Every pair retains the complete first-reader and frozen independent judgments, original set membership/fractions, final disposition, exact source references, phase, study purpose, snapshot status and uncertainty. The other 47 primary labels agree. No reader is treated as authoritative merely because they labeled first. `discrepancy/adjudication.json` records all 49 comparisons, including concordant cases.

The source review reconciles the broad phase-I versus Ewing-only phase-II pathways, the alternative DDR cohort, TAS cohort 3, the restricted PerVision screening list and all named comparator/expansion groups. It preserves the missing CaboMain external exclusions, unclear Ewing-like boundaries, KRAS part-specific requirements, SS18 mutation-versus-fusion interpretation, PRAME/HLA details, B7-H3 acceptance and registry internal discrepancies. Clinical criteria remain sponsor-provided requirements, not medical facts newly established by this review.

Validation passed 1,384 assertions, including deterministic selection reproduction, exact original memberships, frozen-file integrity, 1,139 source-pointer resolutions and 155 exact excerpt checks over 23 raw source files. Counts include repeated resolutions across pairs, not 1,139 distinct pointers. The 282 independent evidence objects retain full reviewed module values and decisive excerpts. Adjudicated content reproduces exactly from the frozen independent judgments and explicit adjudication script. These are data and provenance checks, not clinical validation. Integration preflight was not run, as assigned to the coordinator.

Run the read-only validation from the repository root:

```powershell
& 'C:/Users/mcrae/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -X utf8 research/autonomy/trial-reference-adjudication-2026-09-05/validate.py
```

The authoring scripts intentionally refuse to overwrite frozen output files. `validate.py` rebuilds the adjudicated content in memory and compares it without changing artifacts. Do not delete caches to run these checks; Python `-B` prevents new bytecode output.

This reference can support audit and multicategory evaluation of **saved registry disease/cohort scope** on the frozen selected pairs. Keep sample and challenge summaries separate, retain overlaps and apply explicit purpose/snapshot/uncertainty rules. It cannot establish individual eligibility, site availability, safety, efficacy, therapeutic window, treatment benefit, prognosis, population prevalence or global retrieval recall. No rankings, fitted models or performance-derived label tuning were produced.

Expansion to the 149 current ordinary/molecular frame pairs is the next distinct task, with existing reviewed overlaps reused. Unreviewed records remain unjudged. The reference is complete as this worker's bounded adjudication checkpoint and awaits the coordinator's independent scientific verification and normal integration preflight. No subprocesses, runners, nested workers or background jobs remain running; no commits, PRs, outreach or publication occurred.
