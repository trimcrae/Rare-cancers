---
id: DOC-ASO-FRAME-CENSUS-SPRINT-2026-10-01
title: ASO frame candidate census handoff
kind: memo
status: live
date: 2026-10-01
last_verified: 2026-10-01
purpose: Preserve one bounded candidate-vetting result and its demonstrated integrity repair.
scope: Computational reference-transcript frame census and verifier integrity; no publication or clinical claim.
audience: [maintainers, autonomous research agents]
---

# ASO frame candidate census

The question was whether register-correct premature termination excludes any additional candidate
under the current native gate ladder. It does not: 38 declared pairs pass the coding/resume/register
gates and all 38 pass the translation criterion. All eight register-correct fixed-offset
terminations already fail the resume gate: they start NR4A3 at residue 318, outside the declared
range [1, 1], and their current grade is `SEAM_NOT_PRODUCED`.

Six stop witnesses are retained donor terminators. The TCF12 exon-1 and TFG exon-1 cuts omit the
native donor start codon; their fixed-offset translations are computational diagnostics, not
evidence of initiated biological fusion proteins. The census adds no candidate exclusion and no
patient, binding, efficacy, safety, delivery or therapeutic-window evidence.

The new JSON records all eight stop triplets/coordinates and native-start-retention flags,
donor-stratified declared grade counts, the unrestricted census and SHA256s of its inputs and
instruments. It reuses the existing independent instrument; it is not a third independent
implementation. The coordinator separately recomputed all 231 declared rows and the 616-row
unrestricted census without importing this Python implementation, with matching counts and
stop witnesses.

One explanatory sentence in the preserved `aso-independent-verification.json` calls these eight
rows `OUT_OF_FRAME`. That explanation is obsolete for the current resume scope; the actual
row grades are `SEAM_NOT_PRODUCED`. This branch preserves that artifact, the atlas, manuscript,
preregistrations and all frozen/deposited assets. The new census documents the qualification.

# Demonstrated integrity repair

Baseline job [110634415792](https://github.com/trimcrae/Rare-cancers/actions/runs/36941687725)
at `00935ad95ebec3575eec4cef5b9082a977ec8dfe` returned `AGREES` with no problems for both
a duplicate graded row (232 rows) and a false EMITTABLE total (39 instead of 38). The verifier now
retains multiplicity before indexing and compares reported grade counts to both raw rows and
independent grades. Behavioral checks cover duplicates (including shadowed corruption),
missing/extra rows, wrong/missing/unused/fractional totals and valid row reordering.

# Source and generated provenance

- Branch: `codex/usage-sprint-2026-10-01-frame-census`; base: `c93daca9947c3f16e41e309a302d6279a7b47fa5`.
- Source checkpoint: `33ceb4739c9eef5842a1863d2fe28ef192487f0f`.
- [Successful CPU preview](https://github.com/trimcrae/Rare-cancers/actions/runs/36942117282):
  actual census generation/check, strict archive generation/check, drift generation/check and
  clean restoration passed. Census SHA256: `8a3cf0e5d98e2524e015a788e096092270836fa8a63fe4dd08c843838d0320e2`.
- Live archive inventory retains 521 paths, unchanged promises/gaps and every scientific/frozen
  file hash. Only verifier and existing integrity-test entries changed. Its clean-source flag is
  true and revision anchors the source checkpoint above.
- Deposit-drift generation reproduced the checklist byte-for-byte; it is not edited.
- Model/effort identifiers and subscription usage are not exposed in this connector session;
  remaining capacity is unknown. CPU-only branch jobs have finite timeouts; no dispatch of GPU,
  paid API, publication, PR, merge, owner/fleet or shared-queue changes.

The first metadata preview correctly refused clean-source provenance after an untracked census
was generated before the archive. The next preview passed generation but rejected an assertion
that assumed the unchanged drift block must differ. Both restored tracked inputs. The corrected
capture generates the archive first and permits an unchanged checklist; no acceptance gate changed.

# Actual settled validation and endpoint

[Run 36942362454](https://github.com/trimcrae/Rare-cancers/actions/runs/36942362454), job
`110636583482`, completed successfully against `c9aa07680cff61d0f7561934258d410f9082c0e4`:
46 verifier tests passed in 8.84 seconds; two drift guards passed in 1.76 seconds; unchanged
scientific-artifact, new census, live archive-content and operational-drift checks passed.
Normal preflight exited 0 with `PREFLIGHT OK (fast gates only (doc + artifact linters))`.
Tracked status/diff stayed clean. The CPU job lasted 165 seconds, including 114 seconds for
normal preflight. Broad scientific pytest suites and full publication preflight were not run.

The coordinator independently matched every census quantity/stop witness and reviewed the
question, method, finding, limitations and next step at census blob
`09e0b87bf2f5f97a1310c6e808192d0ea07ff2c5` and original prose blob
`6c70af61a28689813448bcc770e8bc43d8ac9b50`; no scoped blocker or misleading biological claim was found.
Only this operational receipt footer changed after that prose review. Exact output hashes,
job timings, review scope and full original logs are preserved in
[validation-receipt.json](validation-receipt.json).

This bounded task is finished; no job remains running. The coordinator owns integration.
Frozen submission or deposited-package replacement requires its separate existing release
procedure. The next science priority follows the current CHRNA6 readiness outcome: obtain
authoritative GPL6244 probe annotation plus matching per-probe measurements/preprocessing
metadata for the 42 recorded GSMs, preserving all seven exclusions and unresolved discovery-study
overlap. Stop with a precise missing-evidence result before statistics or independence claims.

