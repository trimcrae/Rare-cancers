---
id: DOC-IPD-FRONTIER-PROTOCOL-20260906
title: Conservative joint-state frontier bounds development protocol
kind: memo
status: live
purpose: Freeze the coverage argument before timing the existing development and stress releases.
scope: Existing discrete-time release model only; no new data generation or held-out evaluation.
audience: [maintainers, autonomous research agents]
date: 2026-09-06
last_verified: 2026-09-06
---

This checkpoint receives exactly the 18 committed development and four stress releases. The
original oracle remains unchanged. The target remains its ordinary logrank statistic Q=U^2/V
and two-sided p<.05, using the existing proved rational critical-value enclosure. No clinically
validated claim or continuous-time guarantee is introduced.

At the beginning of grid time t the structural state is `(t,yA,yB,eA,eB,sA,sB)`, with exact
rational current KM values sA,sB and remaining event counts eA,eB. A state stores a rational
rectangle enclosing every reachable accumulated (U,V), plus one actual prefix path. Feasible
integer event/censor transitions obey the unchanged released rounded curves, risk counts,
event totals and terminal exhaustion. Future transitions depend only on the structural key.
When histories share that key, coordinatewise min/max merges retain all attainable (U,V)
pairs, though lost U/V dependence can make Q bounds wider. The actual prefix retained at a
merge remains feasible and can follow any future transition from that structural key.

Layered joint traversal expands each state into the next time layer. U,V increments are exact
rationals under the pooled tied-event formula. We do not materialize all complete arm paths
or their Cartesian product. A separate bounded, memoized release-only feasibility search may
find one full compatible path per arm, establishing nonemptiness before joint traversal ends.
Failure to find such a witness under budget does not establish infeasibility.

For any unresolved state, remaining eA/eB events give delta-U in [-eB,eA]: each contribution
`dA-(dA+dB)*yA/(yA+yB)` is between -dB and dA. Variance increments are nonnegative and
at most d/4, since the finite-population factor `(y-d)/(y-1)` is at most one when d>=1,
and `yA*yB/y^2 <= 1/4`. Thus total delta-V lies in [0,(eA+eB)/4]. Add these intervals
to the accumulated rectangle. Future feasibility constraints may make the true set smaller;
ignoring them cannot exclude a compatible suffix.

For a resulting rectangle U in [l,h], V in [a,b], V>=0, let m be squared distance of [l,h]
from zero and M=max(l^2,h^2). If b>0, a lower Q bound is m/b. If a>0, an upper Q bound
is M/a; otherwise use infinity, except an identically zero U interval implies Q=0. When
b=0, every feasible actual score has U=0 and uses the defined Q=0 convention; an inconsistent
nonzero-U zero-V rectangle is not treated as a valid certificate. Every feasible V=0 history
has U=0, so the lower bound includes zero whenever that history could occur.

The global outer bound unions all terminal and frontier rectangles. Its threshold classification
can certify only with an actual compatible full witness. A crossing outer interval means
unresolved; opposing decisions are reported only if actual compatible full witnesses establish
them. No interpretation as confidence limits, probabilities over boxes, or expected patient
counts is allowed.

If a budget fires mid-expansion, retain the entire active parent rectangle in addition to
already-generated children and the unexpanded current layer. This deliberate overlap preserves
every unprocessed sibling. Only after every child has been processed may the active parent be
removed. A failure while generating transitions follows the same rule. Budgets constrain
transitions, states and wall time; observed memory is measured with tracemalloc. Forced-stop
tests will verify both mid-expansion parent retention and complete exhaustion behavior.

Validation compares every completed oracle interval against these outer bounds for all 18
fixed releases; tiny existing oracle cases and explicit forced-budget cases test merging,
zero variance, infeasibility and witness requirements. Existing four stress cases measure
tractability and bound width under fixed limits, with no new case search. Development timings
are descriptive and include instrumentation. A useful checkpoint need not improve certificate
count; it must preserve coverage and expose actual usefulness or weakness.
