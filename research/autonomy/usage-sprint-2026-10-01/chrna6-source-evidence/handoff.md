---
id: DOC-CHRNA6-SOURCE-EVIDENCE-SPRINT-20261002
title: CHRNA6 source recoverability handoff
kind: memo
status: live
date: 2026-10-02
last_verified: 2026-10-02
purpose: Preserve authoritative CHRNA6 source excerpts without repeating expression analysis.
scope: One public GEO acquisition and exact source/cache correspondence; no expression statistics.
audience: [maintainers, autonomous research agents]
---

The recovered primary source agrees with the existing September 6 CHRNA6 cache. The original
GPL6244 table contains one CHRNA6 transcript-cluster/probe-set record, `8150550`, among 33,297
annotation rows. Its repeated transcript assignments all name CHRNA6. The row reports
`total_probes = 31`; the deposited measurements are one RMA log2 probe-set summary per GSM,
not 31 separately observed oligonucleotide values. All 42 summaries and 252 compared
metadata fields match the committed cache exactly.

The question was whether source annotation, sample IDs, measurements and preprocessing agreed.
The endpoint was one finite official-source acquisition and exact comparison. This result adds
source recoverability, not another biological experiment, expression statistic or patient cohort.
The JSON retains the complete matching annotation row and all 42 value lines, source line
numbers, titles, characteristics, source labels and preprocessing statements. It is a selected
source projection, not a complete portable source bundle.

The September 5 six-input readiness audit is historical. Current main already supplies the
September 6 manifest and 42 values, but its full Git tree lacks the seven source-bundle paths
named by the old offline replay input lock. The new source excerpt resolves this narrow
recoverability gap. It does not alter either historical packet or its analysis rules.

Historical arm membership is retained from the old readiness audit: 6 EMC, 29 comparators
and 7 excluded records. GSM600963–GSM600967 remain excluded solitary fibrous tumor records;
GSM600968–GSM600969 remain excluded pooled-muscle RNA records. Their deposited values are
preserved for completeness and do not make them controls. Discovery-study overlap, unique
patients and unique specimens remain unresolved. No CISH threshold, classifier, independence,
clinical validation, efficacy, safety or therapeutic-window claim follows.

One read-only GET of the official
[GSE24369 family SOFT](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE24nnn/GSE24369/soft/GSE24369_family.soft.gz)
completed on 2026-10-02 at 00:38:35 UTC. Its 20,240,336 bytes match the historical SHA256
`98c83c8ca23b7052cf0d4d0099a7bf1af6c3c972276038c3a633e2a5349b3c37`.
The streamed source contains 1,230,395 lines. Acquisition stops on a changed source hash,
unknown/duplicate sample, missing/ambiguous annotation, incomplete probe coverage, changed
units, mismatch or malformed/truncated source. Compressed and expanded size limits and
finite network/job timeouts are explicit. No second acquisition is permitted by the settled
workflow while committed evidence is present.

Original acquisition [run 36946984140](https://github.com/trimcrae/Rare-cancers/actions/runs/36946984140),
job `110651246654`, passed at `88920dd07bcce6f75d9c36917f5a6700a412726f`:
16 synthetic source-integrity tests, actual acquisition/comparison, immediate offline check,
normal `PREFLIGHT OK (fast gates only (doc + artifact linters))`, and clean tracked diff.
The source JSON has 105,819 bytes and SHA256
`469f272cabc709578f4c6a08bdd8574b0f7e60d721cc4d0624e2c67c96140825`.
Its original output bytes and full job log are preserved.

Independent methods review found a real omission: the offline checker bound raw and parsed
metadata but did not reassert GPL6244. A coherent raw/parsed platform change could pass.
The repair adds explicit top-level and sample-platform invariants plus malformed-projection
regressions. The same repair batch prevents repeated acquisition on later commits; handoff,
receipt and log changes do not trigger this workflow. Settled offline validation and both independent review scopes are now complete.

Settled [run 36947531796](https://github.com/trimcrae/Rare-cancers/actions/runs/36947531796),
job `110652916128`, passed against `e7ce6eac2eddd741a6b79f44cff46b7305bc2f72`:
19 actual Python unittest cases, committed-evidence offline integrity, default fast preflight
and clean tracked diff. Acquisition and source-artifact upload were actually skipped. Full
scientific suites and full publication preflight were not run. Exact original logs and hashes
are recorded in [validation-receipt.json](validation-receipt.json).

The coordinator independently parsed the original acquisition log's 105,819 output bytes and
the raw annotation/value/metadata text in JavaScript/V8. All 42 values, 294 metadata bindings
(six cached fields plus platform per sample), the entire historical arm map and the primary
source pin matched; zero differences were found. The final committed source JSON was also
byte-identical to that original output. A separate methods reviewer verified the platform
repair and actual settled CI. Both reviewed the qualified prose at blob
`ed6345b994ec573bb9984e9e3b0967b7dce8fb06`; only this operational receipt block changed afterward.
This bounded task is complete, no job remains running, and ownership has returned to the
coordinator.

Base main is `7f0971a331272695dcfe4b2a7fac554185b398d9`. Fresh ownership was checked from the
full research-ledger Git blob: 415 entries and zero live owners; the legacy driver remains
disabled. This isolated branch is not a remote legacy claim or scheduler cutover. Only new
task files and its branch-only read-only workflow change. Frozen research, manuscripts,
preregistrations, scientific results, fleet, GPU/publication guards and shared queue records
remain untouched. No PR, main merge, publication, GPU dispatch, paid API or separately billed
compute is performed. The coordinator owns integration.

The next bounded scientific question is whether an accessible authoritative source supplies
a discovery/validation specimen crosswalk for the CHRNA6 study, DOI
`10.1016/j.modpat.2024.100464`, PMID `38447752`. Establish the exact current evidence and source
availability first. Stop with a precise missing-input result if the required crosswalk remains
unavailable; do not infer independence from different accessions or fit a classifier.
Do not repeat this unchanged source acquisition or the completed expression kernels.

AI authorship is identified in the evidence JSON. Model/effort IDs and subscription usage are
not exposed by this connector session. Execution used GitHub-hosted Python 3.11.16 CPU checks;
no local shell or managed cloud environment was available.
