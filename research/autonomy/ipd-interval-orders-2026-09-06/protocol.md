---
id: DOC-IPD-INTERVAL-ORDER-PROTOCOL-20260906
title: Tiny continuous-time interval-observation order-class oracle
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Check finite order-class coverage without changing the observed-IPD logrank target.
scope: Pre-outcome protocol for a tiny continuous-time development oracle only.
audience: [maintainers, autonomous research agents]
---

## Frozen release model

Schema `interval-km-release-v1` describes two right-censored arms on a finite rational time horizon T>0. Every observation exits at some real time in (0,T]; no truncation, entry, or censoring after T is admissible. Each arm has integer n>=1; `total_events` is either an integer in [0,n] or null (unknown); `risk_counts` maps exact rational time strings in [0,T] to integer pre-event risk counts; `observations` is an ordered list of boxes `{time_lo,time_hi,survival_lo,survival_hi}`. All bounds are exact rational strings; both ends of each box are closed. A box asserts existence of a real timestamp x in its horizontal interval at which the right-continuous KM estimate S(x) lies in its vertical interval. The timestamps for an arm's listed observations must be nondecreasing, including possible equality. Observation timestamps may differ across arms. Boxes constrain coordinates, not whole connecting segments, slopes, censor tick locations or an entire raster image. No probability distribution over boxes or feasible patient records is assumed.

At a shared event/censor time, all events see the pre-time risk set; censor removals occur after the events. True event ties within and between arms are allowed. S(0)=1 and, after exhaustion, S carries forward. Exact risk count at t means number of recorded exit times >=t. The target is the ordinary two-sided observed-IPD logrank statistic, with the pooled hypergeometric variance accounting for true event ties. U=V=0 is reported as p=1; no clinical-effect interpretation is made.

## Finite representation and completeness argument

Partition [0,T] at 0,T, every horizontal box endpoint and every supplied exact risk-count time. A prespecified exact query time, if later used, must likewise be a boundary before enumeration. Boundaries are singleton time locations; adjacent boundaries define open cells. There are N=nA+nB exit records. In every open cell, represent k nonempty pooled exit weak-order groups (k<=N) at the exact rational slots `left+(right-left)*j/(N+1)`, j=1,...,k. Every group records nonnegative counts of A events, A censors, B events and B censors, with positive total. Groups at fixed boundaries are allowed (except time0); groups in an open cell are an uninterrupted prefix of these slots. Enumerate all group-count compositions consistent with arm sizes and any available event totals. This is not an arbitrary fine time grid: the slots encode all weak orders, not unknown times rounded to a physical grid.

For any admissible real dataset, sort the distinct exit-time groups inside each cell and map the jth group to the jth slot; keep all boundary groups fixed. At most N slots suffice because there are at most N records. This preserves every cross-arm event/censor weak order, every actual event tie, every risk set at events, and every exact risk count at a fixed boundary. Consequently it preserves U,V and ordinary logrank p exactly.

It also preserves box feasibility. Refine the partition further at the chosen exit-group times. On each resulting open segment, both KM estimates are constant and all horizontal-box membership predicates are constant; singleton endpoints retain right-continuous values. Any observation timestamp on a fixed point stays there, and any timestamp in an open segment can be mapped to a representative midpoint of its corresponding transformed segment. The resulting map is nondecreasing, preserves every arm's ordered-observation constraint, and preserves vertical and horizontal membership. Conversely any canonical dataset and chosen observation timestamps are admissible real timestamps under the original model. Thus canonical enumeration is neither a snapped-time approximation nor an outer relaxation: its attainable U,V set equals that of the model.

For a fixed canonical exit dataset, check observation feasibility by considering every fixed boundary and exit time plus every intervening open-segment midpoint. Greedily select the earliest feasible candidate at or after the previous observation candidate. This succeeds exactly when a nondecreasing feasible observation sequence exists: every allowed real sequence maps to this finite list, and replacing any chosen point by an earlier admissible one cannot obstruct the remaining nondecreasing observations. Equal timestamps remain allowed.

## Execution bounds and verification

The implementation enumerates tiny cases only. Apply explicit node limits; stop early with `complete=false` and universal p bounds [0,1], while retaining any actual witnesses found. Sampled extrema are not certificates. An empty exhaustive feasible set is incompatible input; an empty incomplete search is unresolved nonemptiness. Exact Fraction arithmetic is used for KM, U,V and Q=U^2/V; floating p values are display values derived from Q. No threshold certificate based solely on rounded floating p is required at this checkpoint.

After coordinator review of this protocol, use predetermined tiny fixtures (n2 or n3 per arm), both-arm censoring, closed horizontal/vertical uncertainty boxes, exact risk counts and both known/unknown event-total cases. Include true ties, boundary exits, ordered observations, invalid boxes/release inconsistency and forced exhaustion. Verify known original records' U,V belong to the exhaustive attainable set. Independently enumerate labelled exit assignments to finite canonical slots on at least one n2-per-arm fixture and compare the full attainable U,V set, using a separate KM/observation/logrank implementation. Demonstrate that admissible within-window order changes can change logrank; no search for significance crossings or favorable performance. This is an oracle-development checkpoint, not a moderate or realistic benchmark or a readiness claim.
