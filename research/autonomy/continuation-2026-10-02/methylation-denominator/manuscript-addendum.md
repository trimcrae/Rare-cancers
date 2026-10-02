---
id: DOC-CHECKPOINT06-METHYLATION-ADDENDUM
title: "Recovered cohort exclusions and diagnostic review"
kind: memo
status: live
date: "2026-10-02"
last_verified: "2026-10-02"
purpose: "Integrate newly recovered denominator and adjudication evidence into the working methylation paper."
scope: "Working addendum; no new classifier performance or publication clearance."
audience: [maintainers, external reviewers]
---

The separately deposited E-MTAB-9875 cohort contains 986 profiles, of which three are marked FAILED in the primary case table. We recovered their exact case and array identifiers: cases 847, 848 and 982. The same table directly labels 820 retained cases as diagnoses represented in classifier version 12 and 163 as unrepresented, yielding 983 retained profiles. These are the source authors' eligibility labels, not a mapping into the separate 12-class score-transport experiment.

The table records six diagnosis revisions and provides initial and final diagnoses for those cases. The source describes reviewing discrepant classifications with pathological and other available evidence. These final diagnoses therefore cannot be assumed to have been assigned independently of the classifier. Blank initial-diagnosis fields were not filled from final diagnoses. A nonblank initial field alone also does not establish a revision: case 1015 contains “Central” in that field while its revision flag is No.

The recovered identifiers resolve the deposited-versus-analyzed profile count, but not every source inconsistency. The core-case count is 820 in the case table and main text, whereas two summary-table cells contain 821. We preserve that discrepancy without adding a case or selecting a score threshold. The inspected sources do not specify each failed profile's QC metric or technical reason. This audit supplies a source-native denominator and adjudication record; it does not calculate external classifier performance, harmonize diagnostic taxonomies, or establish cross-study patient independence.

