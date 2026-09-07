---
id: DOC-IPD-INTERVAL-FIXTURES-20260906
title: Fixed tiny interval-oracle development fixtures
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Freeze all development fixture choices before generation or results.
scope: Deterministic tiny synthetic examples; no selected outcome search.
audience: [maintainers, autonomous research agents]
---

All fixtures are explicitly synthetic, with arbitrary time units. No random seed is used. Unless stated otherwise both arms have n=2, exactly one event, one censor, horizon3, risk(0)=2 and risk(3)=0. Each box below has closed horizontal and vertical endpoints. These definitions are fixed before generating their JSON or running the oracle.

1. `wide`: both arms have one box time[1,2], survival[49/100,51/100]. Original A records: event5/4,censor11/4; B:event7/4,censor5/2. No significance-crossing requirement; report the entire attainable score set. Alternate originals intentionally test ordering: A:event5/4,censor3/2; B:event7/4,censor5/2. An event/event tie original has both events3/2, A censor11/4,B censor5/2. An event/censor tie original has A:event5/4,censor7/4; B:event7/4,censor5/2. These choices precede results.
2. `exact_boundary`: both arms have risk(3/2)=2 and a zero-width time box[3/2,3/2], survival[1/2,1/2]. Original A:event3/2,censor3/2; B:event3/2,censor5/2. This tests true pooled event ties, simultaneous event/censor exits, pre-event exact risk and right-continuous observation at the same boundary.
3. `ordered_impossible`: both arms list first box time[2,2],survival[1/2,1/2], then time[1,1],survival[1,1]. Each box can be separately satisfied by original A and B:event3/2,censor5/2, but their required nondecreasing observation sequence cannot exist. The expected feasible set is empty for this reason, not because the box object is malformed.
4. `unknown_events`: identical to wide except both event totals are null. The original wide records are still admissible. This tests enumeration over available rather than silently inferred event totals.
5. `n3_boundary`: both arms n=3,total_events=1,horizon3,risk(0)=3,risk(1)=3,risk(2)=1,risk(3)=0 and a box time[1,1],survival[2/3,2/3]. Both original arms:event1,censor3/2,censor5/2. This tests a slightly larger count composition with exact boundary event constraints.

The labelled independent oracle will use `wide` and `exact_boundary`, each with a separate Cartesian enumeration of all labelled event/censor slot assignments. It will retain gaps in slots and compare sets of exact (U,V), not duplicate class counts. All case sizes stay tiny. Run each main oracle with node limit1,000,000. Force incomplete runs at limits1 and100 on wide; they must expose universal p bounds[0,1]. Reject a structurally invalid box with time_lo2,time_hi1 before enumeration. Verify every explicitly listed original with independent ordinary logrank arithmetic and direct box/risk checks, including an open-cell original and fixed-boundary originals. No additional fixture search is authorized here.
