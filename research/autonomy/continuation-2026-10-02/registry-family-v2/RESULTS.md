---
id: DOC-CHECKPOINT06-REGISTRY-V2-RESULTS
title: "Response-family parser repair and preservation of reported measurements"
kind: memo
status: live
date: "2026-10-02"
last_verified: "2026-10-02"
purpose: "Record changed-code regression results and direct verification of exported source payloads."
scope: "Frozen registry snapshots and finite syntax repair; no clinical accuracy or generalization claim."
audience: [maintainers, external reviewers]
---

The parser repair addresses the seven abstentions observed in the previous independent evaluation: ordinary “who” was confused with WHO criteria, and explicit RECIST or iwCLL names and intervening version syntax were missed. The repaired implementation is separate from the original. Independent review then found a repair-induced defect: “previously treated patients” incorrectly marked a current assessment as historical. One bounded correction and its original failing tests are retained.

[Cloud run 37050069878](https://github.com/trimcrae/Rare-cancers/actions/runs/37050069878) passed at `6f7cb786511853dcb77b8acc90704ace3469a165`. In the same frozen 68-outcome, ten-trial snapshot, the nine eligible outcomes now have nine exact joint status/family/version/modifier agreements: eight assigned families and one unknown. Seven predictions changed. This is **seen-case regression after a repair informed by the previous failures**. The original independent result remains 2/9; the 9/9 result does not estimate generalization or clinical accuracy. The original oracle and two mechanical amendments remain unchanged.

The new direct payload audit closes an earlier verification gap. Across both original and repaired exports it verified all 68 full outcome objects, 460 literal rows, 421 measurement records, 663 literal denominator records including repeated scopes, and 45 accepted companion rows against the frozen source. Empty group coverage and all accepted literal payloads are preserved. This verifies source fidelity, not the clinical validity of the reported endpoint or denominator.

Five payload-audit tests, including four negative controls, and 16 independently frozen synthetic syntax cases passed in the cloud. The implementation worker's 22 synthetic tests and the focused independent nine-probe repair check are also retained; unchanged tests were not run again merely for this receipt. The original manual freeze timestamp was corrected by a dated amendment to the actual Git commit time, without changing the frozen cases.

The distinct changed-code replay of the known 575-unit corpus produced 424 assigned, 116 unknown and 35 ambiguous family contexts. All 27 previously reviewed units retained their family, category values and denominators. The accepted 510 unqualified four-cell units remain unchanged; 387 units now have four cells within the explicitly assigned family. These are known-corpus counts, not a held-out validation. Family annotation does not authorize pooling.

The finite grammar still does not cover every response-criteria phrase, including the independently identified “WHO tumor response criteria” construction. Category/class-role mapping was not changed; confirmation, reader and aggregate roles are not automatically adjudicated. A new claim about transfer requires a fresh predeclared source slice and independently labelled oracle. No further threshold tuning or repeat of this unchanged slice is justified.

Exact execution metadata, the complete compressed artifact, source and code digests, original and repaired code, failed tests, independent reviews and source-preservation outputs are retained here. No accepted clinical registry or publication package was modified.
