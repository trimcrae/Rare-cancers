---
id: DOC-IPD-PARTIAL-ORDER-PRIOR-ART-20260906
title: Existing imprecise-rank bounds narrow the survival-summary contribution
kind: memo
status: live
purpose: Reassess novelty before further survival-summary solver investment.
scope: Bounded primary literature and actual source-code inquiry; no experiment or novelty proof.
audience: [maintainers, autonomous research agents]
date: 2026-09-06
last_verified: 2026-09-06
---

**Withdraw generic novelty for logrank bounds under imprecise timing, three-way decision certification, and selecting observations to determine a decision.** Those ideas have substantive prior art. The surviving prospect is a practically useful, rigorously covering inverse solver for released rounded KM/risk information with unknown within-arm histories and true ties. This checkpoint does not establish that prospect as novel enough, scalable enough, or useful enough for a standalone paper.

## Closest collision

[Coolen-Maturi and Coolen](https://tahanimaturi.com/pdfs/Logrank-ComStats-rev-20210507-Final.pdf), published in 2023 (DOI 10.1080/03610926.2021.1952270; preprint 2020), directly studies standardized logrank bounds for imprecise recorded event and censoring times. At rho=0, equations (1)-(4), PDF p3, match our signed score Z=U/sqrt(V). Their Theorem 3.1, p4, asserts monotonicity under adjacent cross-arm switches. The setting fixes within-arm ordering and failure/censor status (pp2-4), and expressly says, “we assume throughout this paper that there are no ties” (p3). Example 2, pp12-14, applies timing intervals and compares extrema with test thresholds. Calling our target the original finite-sample statistic does not distinguish it from this overlap.

The original author PDF is archived in the worker cache, SHA256 `c5245823c92992cbfce2cb67ee965891ee2aaae307a4b66db9100e3965c53ad6`. The publisher PDF returned HTTP 403; publisher indexed text corroborates the restriction. Appendix p16 rewrites the desired inequality through four differences; this checkpoint has not independently validated its proof. Reuse requires an independently justified statement, not simply a citation.

## What the theorem does and does not replace

These are deductions from the target models, not claims that the cited authors implemented our solver:

1. Conditional on a fixed no-tie within-arm event/censor sequence, a sound monotonicity result can potentially shortcut cross-arm interleaving optimization. It does not enumerate the sequences that rounded KM data permit. Published summary constraints concern products of event/risk ratios, total events and exact risk counts; extremizing switches can violate them.
2. An easier interval/order problem containing the full compatible set could supply conservative bounds. Its containment must be proved, including all event/censor assignments. Dropping constraints is safe for outer bounds; dropping feasible tied histories is not. Neither cited no-tie method licenses replacing actual ties by strict orders.
3. If attained signed-Z extrema are a and b, the maximum Q is max(a^2,b^2). If their interval crosses zero, a hull-derived Q lower bound of zero is conservative but need not be attained. Exact minimum Q requires the attainable Z closest to zero. Endpoint order construction alone therefore does not always deliver exact two-sided p extrema.
4. No inspected algorithm directly replaces the proposed per-arm suffix-reachability DP. That DP addresses inverse compatibility and dead-prefix pruning, while the switch theorem addresses a conditional objective ordering. This input mismatch is a reason to investigate a specific solver, not evidence that it will work or warrant a paper.

## Other substantive overlap

[Denoeux, Masson and Hebert (2005)](https://www.hds.utc.fr/~tdenoeux/dokuwiki/_media/en/publi/fss2642v4.pdf) already map interval observations to compatible linear extensions, statistic/p bounds and rejection/nonrejection/indeterminacy (section 3, PDF pp5-8). Section 3.3 acknowledges that sampled extrema approximate inward; such sampling can find witnesses but cannot certify full coverage. Section 6, p19, explicitly leaves weak orders with ties for future study. General partial-order reduction and three-way reporting must be credited as established ideas.

[Fay and Shaw's interval package](https://stat.ethz.ch/CRAN/web/packages/interval/vignettes/intervalCensoring.pdf) answers a different question. Its actual `ictest.R` calls the pooled NPMLE at line 104, then score/imputation/permutation procedures at lines 165-206. Its `ictest.Rd`, lines 149-158 and 240-248, explains the variance and p-value differences from ordinary right-censored logrank. “Exact” there concerns permutation inference, not a complete range of the original statistic over release-compatible records. It is not a drop-in certification method. [Coolen et al. (2021)](https://link.springer.com/article/10.1007/s00184-021-00807-4) additionally demonstrate an imprecise logrank application in accelerated life testing.

[Golovin, Krause and Ray (2010)](https://www.cs.cmu.edu/~dgolovin/papers/nips10.pdf), section 3, PDF p4, define equivalence-class determination: acquire tests until all remaining hypotheses have one decision label. Our compatible histories are hypotheses, p<.05 supplies two labels, and an exact arm/time risk count is a deterministic test. Thus the basic query idea is a direct application of established decision-focused active learning. Their expected-cost, prior-based EC2 guarantee does not transfer to our prior-free one-step minimax rule. Greedy splits are not a proof of the smallest total number of counts. Query-family restrictions and efficient implicit-state computations could matter, but must demonstrate useful information savings.

## Decision and next action

Retain only this conditional development question: can an auditable solver certify the ordinary observed-IPD logrank decision from realistically compressed KM/risk releases, preserving true ties, at useful cost and with better information requests than simple alternatives? Establishing a complete tiny oracle is useful groundwork; generic enumeration and a greedy query rule are insufficient novelty by themselves. Current frontier stress failures still leave usefulness unproven.

First reconcile the paper-level rationale with these collisions and independently assess any candidate monotonicity shortcut. If further implementation is selected, frame it as aggregate-summary inversion and demonstrate the extra value of its constraints and tied-history coverage; benchmark it against a sound relaxed bound when available. Do not relabel uncertainty about novelty as proof of absence, or the remaining application as automatically valuable.

## Evidence and execution scope

[evidence.json](evidence.json) provides source-level decisions and locators; [web retrieval log](sources/web-retrieval-log.json) preserves exact queries and inspected responses; [download receipts](sources/download-receipts.json) record original-body URLs, access outcomes and hashes. Original bodies live in this worktree's `.cache/ipd-partial-order-prior-art-2026-09-06/`; these cached files must accompany any archival handoff. Python TLS trust failed for Denoeux; PowerShell's normal system trust succeeded, with no certificate verification disabled. No inaccessible source or generic search miss was counted as an absence result.

Base: `920fed4fff362b9cef8e97fb7b3356209c77c7af`. Model/effort were inherited and not independently exposed; usage was unavailable. Work remained within the owned packet and cache. No held-out data, experiments, manuscript/shared state, commits, publication, outreach, paid compute or settings changes occurred. No normal preflight or ultra review is claimed. This bounded checkpoint is finished; no process remains running.
