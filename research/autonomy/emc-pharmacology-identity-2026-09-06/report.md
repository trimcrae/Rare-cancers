---
id: DOC-EMC-PHARMACOLOGY-IDENTITY-REPORT-20260906
title: NCC pharmacology identity-aware descriptive result
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Report corrected source identity and bounded two-family consistency.
scope: Retrospective NCC screen chemical identity and descriptive consistency.
audience: [maintainers, autonomous research agents]
---

The source-resolved, proteasome-directed candidate set comprises five preparations among all 221 NCC screen entries. Their low-viability pattern survives active-moiety grouping and removal of either broad chemical family. Current catalogue identity is now resolved for the fifth preparation, S2181; its active-moiety equivalence and analogue-specific mechanism remain unestablished. The original descriptive stop rule passes under the source-annotated membership interpretation; validated mechanistic completeness remains unsupported.

This is a retrospective result from one patient-derived EMC model. Selected values were already inspected before the protocol. It is not a blinded prediction, independent biological replication or new target discovery.

| Exact MOESM5 source name | CAS | MOESM4 catalogue / row | Mean rank /221 | Mean+SD rank /221 |
|---|---|---|---:|---:|
| Bortezomib (PS-341) | 179324-69-7 | S1013 /31 | 15 | 19 |
| Carfilzomib (PR-171) | 868540-17-4 | S2853 /41 | 24 | 17 |
| Ixazomib (MLN2238) | 1072833-77-2 | S2180 /111 | 14 | 10 |
| Ixazomib citrate | 1239908-20-3 | S4432 /112 | 17 | 12 |
| Ixazomib Citrate (MLN9708) | 1201902-80-8 | S2181 /113 | 22 | 20 |

All five MOESM4 rows state Proteasome, Proteases and provider Selleck  Chemicals. Exact source names and supplier fields are preserved separately in the amended roster and screen. The current [S2181 supplier label](https://www.selleckchem.com/products/MLN9708.html) identifies an ixazomib-citrate analogue, with different boronate connectivity from regulatory S4432 citrate. S2180 is active ixazomib. Catalogue identity is no longer a missing input. Supplier prose describing MLN2238 biochemical potency cannot establish S2181-specific activity or hydrolysis to the same active moiety.

Four preparations map through established drug/prodrug relationships to three documented active moieties: bortezomib, carfilzomib and ixazomib. Grouping regulatory citrate with active ixazomib is an explicit sensitivity, not equivalent exposure. Their worst preparation ranks are 15, 24 and 17, all within the retrospective lowest-quartile threshold of 55.25. S2181 remains a separately annotated analogue, not an additional validated active moiety.

The two broad families are boronic-acid/ester lineage and epoxyketone. Including source-annotated S2181, the former's worst rank is 22, the latter's 24. Removing the boronic lineage leaves carfilzomib; removing epoxyketone leaves four preparations, including the analogue, representing two documented active moieties plus one unresolved active-moiety analogue. Only one family remains in either sensitivity. The low-rank observations remain if S2181 is omitted or hypothetically grouped with ixazomib; neither handling establishes conversion. These are descriptive robustness checks, not replicated target engagement.

The source amendment corrects the original false result's exact-current-identity blocker. It does not claim complete experimental mechanism: historical material, in-well chemistry and target engagement remain unmeasured. The original protocol explicitly keeps mechanistic attribution blocked regardless of the descriptive result. Both old and updated dispositions are retained in `amended-result.json`, and the original false `result.json` remains unchanged.

All 221 measurements, 51 viability values outside 0–100%, 24 selected IC50 entries and original ranks remain unchanged. MOESM6 row18 associates 1982 nM and the name Ixazomib with S2181 CAS1201902-80-8; it is not a measurement for active S2180 CAS1072833-77-2. Carfilzomib and active ixazomib CAS entries are absent from that selected follow-up. The follow-up is not independent validation.

Mean+SD is a deterministic stress calculation, not a confidence interval. The original binary64 implementation merges two near-ties: exact decimal arithmetic shifts four unrelated ranks by 0.5, with no effect on candidate ranks or quartile status. Details and exact values are in `amended-result.json` and the copied independent arithmetic report.

Unknown concentration, duration, replicate definition and dose-response fitting prevent uncertainty intervals and comparative potency inference. No target engagement, EMC selectivity, therapeutic window, clinical efficacy or quantitative NCC–Zurich concordance is established. No Zurich bands or clinical recommendations are used.

For the current checkpoint use `amended-result.json`, `amended-identity-roster.json`, `amended-ranked-screen.csv` and `source-amendment-2026-09-06.md`. Run bundled Python with `-B -X utf8 apply-source-amendment.py` to replay the affected annotation/disposition outputs from the immutable archive and cached source catalogue; original extraction/ranks are reused. Original `analyze.py` and its freeze describe the archived first version and are not the amended runner. Archive hashes verify all 26 original files. The amendment checks verify all 221 unchanged source values/ranks, all 221 catalogue joins, exact five source target annotations, unchanged active-moiety count and distinct analogue identity.

This completes the bounded repair for focused independent verification. No commits, preflight, publication, correspondence or background processes were launched.
