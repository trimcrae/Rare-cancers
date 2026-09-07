---
id: DOC-IPD-BOUNDS-DEVELOPMENT-20260906
title: Discrete-time rounded-release compatibility development protocol
kind: memo
status: live
purpose: Define an executable exact compatibility model before development-case outcomes.
scope: Synthetic development only; no held-out evaluation or publication-ready claim.
audience: [maintainers, autonomous research agents]
date: 2026-09-06
last_verified: 2026-09-06
---

This protocol is written before generating the development cases. The concrete question is
whether complete finite enumeration can establish ordinary logrank decision bounds with both-arm
censoring, tied events, and rounded survival probabilities on a declared discrete time grid.
This checkpoint tests implementation and feasibility, not superiority or benchmark performance.
No held-out records will be generated or opened here.

## Released information and target

The JSON release has `schema: discrete-km-release-v1`, `synthetic: true`, integer `grid` values
1 through K, `probability_digits` (0 to 6), and arms `a` and `b`. Each arm has exact `n`,
exact `total_events`, `survival_rounded` (K fixed-decimal strings), and `risk_counts`, a dictionary
from selected grid indices to exact pre-event risk counts. The count immediately before time 1
equals n. Every subject exits by time K; terminal survivors are administratively censored at K.
No censor marks, original p-value, or hidden event/censor counts are released.

Each subject has one observed pair (integer time 1,...,K; event indicator 0 or 1), with no
left truncation or weights. All events at t occur before all censorings at t. If y_t is the
pre-event risk count, d_t the event count and c_t the censor count, then
`y_(t+1) = y_t - d_t - c_t` and `S_t = S_(t-1) * (y_t-d_t)/y_t` when y_t>0.
After y_t=0, survival carries forward. Round S_t to `probability_digits` decimal places,
nearest with exact half ties upward. Thus a published value r with increment h means
`max(0,r-h/2) <= S_t < min(1,r+h/2)`, except that S_t=1 is included when the upper
endpoint would exceed 1. The implementation tests the exact integer rounding map, avoiding
ambiguous endpoint clipping. All post-grid values, including plateaus, are released.

The target is the finite-sample ordinary two-sided logrank result from these discrete observed
records. At each pooled event time, `U += d_a - d*y_a/y` and
`V += y_a*y_b*d*(y-d)/(y^2*(y-1))` for y>1. Q=U^2/V and p=erfc(sqrt(Q/2)).
When V=0 and U=0 define Q=0,p=1; a nonzero U with V=0 is an error.
The reporting threshold is p<0.05, not evidence of clinical benefit. This uses the ordinary
asymptotic reference distribution; it is not an exact randomization test or population coverage.

Time indices are exact within this model. This is not a compatibility model for continuous
event times coarsened into bins: within-bin orders and digitization uncertainty could change the
original continuous-time logrank statistic. Future rendered/continuous-release work must add that
uncertainty before claiming original-IPD containment. Likewise the complete grid supplies more
curve information than a sparsely sampled graph. No guarantee transfers silently to those cases.

## Calculation, certificates, and limits

Enumerate all nonnegative integer (d_t,c_t) paths for each arm that satisfy the released rounded
curve, risk counts, exact event total, and terminal exhaustion. Every individual-level data set
maps to exactly one aggregate path; every accepted path expands to a compatible individual-level
data set. Survival and logrank depend only on the aggregate paths. Cartesian traversal therefore
gives exact rational extrema of Q when both arm enumerations and the pair traversal complete.
Pruning may use only necessary constraints: nonnegative remaining subjects/events, future risk
counts, the rounded curve at the current time, and final exhaustion.

Certificate decisions compare rational Q extrema against a conservative rational enclosure of
the chi-square-1 0.95 quantile, independently verified using rational alternating-series bounds.
Floating p-values are descriptive approximations, never the basis of a stability certificate.
If any path/pair/time budget is exhausted, return unresolved with the conservative bound Q in
[0,infinity] (p in [0,1]); sampled extrema may be labelled observed, never certified extrema.
Infeasible releases are reported separately, never vacuously certified.

For completed sets, consider exact risk-count queries at unreleased arm/grid coordinates.
Choose without original-IPD access by minimizing the worst number of compatible pair classes
whose decisions remain unresolved, then worst remaining class count, then arm and time.
This is minimax over classes, not a probability model over patients. Report all possible answers.
This checkpoint does not estimate query superiority over equally spaced queries.

## Development validation and stopping

Independently brute-force all labeled-free subject category multisets for tiny n and K, filter
the release by recomputing KM/risk summaries, and compare complete accepted path sets and Q
extrema. Use a separate subject-level logrank implementation and SciPy when locally available.
Include tied events, event/censor ties, both-arm censoring, empty-event/zero-variance cases,
half-up endpoints, incompatible releases, and forced incomplete enumeration. Moderate development
cases use n=20,40,80 per arm, discrete hazards and independent censoring, with explicit seeds,
different effect sizes and risk-table densities. Retain every generated case and failure;
no threshold-crossing selection and no held-out generation. If exhaustive enumeration becomes
intractable, document the rate/cause and retain exact small-case results plus unresolved outputs.
Stop this checkpoint with executable artifacts, actual timings, verification evidence, and a
precise next improvement; do not manufacture a manuscript from a working toy.
