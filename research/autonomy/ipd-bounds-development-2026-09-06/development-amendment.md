---
id: DOC-IPD-BOUNDS-STRESS-AMENDMENT-20260906
title: Additional development stress cases after the initial grouped-time results
kind: memo
status: live
purpose: Measure enumeration limits without presenting an easy development model as a completed method.
scope: Dated development-only addition; original protocol bytes and initial fixtures remain unchanged.
audience: [maintainers, autonomous research agents]
date: 2026-09-06
last_verified: 2026-09-06
---

The original protocol has SHA256 `f15bb9e77ffdc127a9ee5ec3cf1bd3b99fa98a3532d2549ff08c73e00611762f`.
The initial 18 releases all completed. All nine dense designs uniquely identified aggregate
counts; one sparse n=80 equal-hazard case was decision-ambiguous. Thus these six-grid-point
designs show correctness but are too easy to assess broad tractability.

Before generating any additional records, this development addition specifies four stress
cases with seed 2026090601: (n=80,K=12,digits=2), (n=200,K=12,digits=2),
(n=80,K=6,digits=1), and (n=200,K=20,digits=2). Per-step event hazards are .08 and .12
in arms A and B, respectively; conditional censor hazard .04 in both. Release risk counts
only at time 1 and `1+floor(K/2)`. Retain every generated case, with no search or selection.
Limits are 300,000 nodes and 10,000 paths per arm, 25,000 pairs, eight seconds per phase.
Incomplete runs must remain unresolved with universal outer bounds, even if partial samples
agree. No held-out cases are generated or accessed. This records additional development,
not a change to a preregistered evaluation or success criterion.
