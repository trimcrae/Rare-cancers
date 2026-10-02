# Revised correspondence: focused claim/source pairs

Draft only. No submission, sent maintainer report, upstream correction, or
cloud-CI success is asserted. Main numerical comparison remains frozen.

| Claim | Evidence and exact scope |
|---|---|
| 3770/3771 rearrangement IDs discordant; ordinal+3 relationship | Frozen Foundation-complete-ID-proof-and-current-source.json at da49c4e836533253825587f83656675dac4c913b. Existing complete proof reused, not rerun against workbook. |
| 3756 agreeing gene pairs; 15 symbol differences | Existing proof plus prototype inspection: mapping uses empty strings for export N/A. Revised text explicitly discloses the missing-value convention rather than calling all raw tokens literal matches. Biological symbol equivalence remains unassumed. |
| 564 N/A tokens retained unchanged | Actual in-memory correction-core run against exact export and mapping hashes; foundation_recovery_check.json. |
| 75 EMC profiles,76 events,63 EWSR1/12 TAF15 profiles;43 short-variant control rows | Existing frozen proof. Profiling-series counts, not population prevalence or independent validation of diagnoses/expressed fusions. |
| 28 selected events from outside EMC;0 true EMC-origin events;47 IDs outside range | New in-memory complete-mapping join. Selector is original EMC IDs prefixed sarcoma_msk_2022-. Not a live portal clinical query. |
| Defect present by February2024; unchanged IDs across May/current objects | Verified historical pointers/payloads recorded in history-addendum.md and foundation_recovery_check.json. Earliest inspected file commit6ad0f9e; equivalent PR-head payload00d055...; May payloadc1226...; currentd9fc3.... |
| June2024 release PR merge; December symbol migration | Official PR2027 and commit45dcc57. Commit/merge dates do not establish actual portal deployment date. |
| Current snapshot still affected on2October2026 | HEADdca75cb... still referencesd9fc3...; payloadhash independently checked. No claim about downstream installations. |
| Recovery preserves3771 events and original multiplicities; refuses altered inputs | In-memory standard-library core passed; outputSHA2562c910856e5e483c3774af5d0192b6118536f368aade8f05960bb123014a20184. CLI writing/importing not tested by this seat. |
| No first-detection novelty claim | Focused primary-source prior art: Yoo2021 doi10.1016/j.patter.2021.100245; Abeysooriya2021 doi10.1371/journal.pcbi.1008984. Search is bounded, not exhaustive. |

Frozen evidence folder:
https://github.com/trimcrae/Rare-cancers/tree/da49c4e836533253825587f83656675dac4c913b/research/autonomy/data-opportunities-2026-09-30/deep-analysis/results

No new biological inference is added. Practical next action is maintainer
reconciliation; journal fit remains uncertain because the demonstrated defect
is in a derivative export rather than the original published scientific claim.
