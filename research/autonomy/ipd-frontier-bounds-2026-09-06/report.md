---
id: DOC-IPD-FRONTIER-RESULTS-20260906
title: Conservative frontier coverage is verified but decision utility remains weak
kind: memo
status: live
purpose: Report the implemented frontier method and its observed development limitations.
scope: The 18 existing grouped-time development releases and four fixed stress releases only.
audience: [maintainers, autonomous research agents]
date: 2026-09-06
last_verified: 2026-09-06
---

**The new frontier calculation preserves rigorous coverage when interrupted, but it does not
improve certification on the fixed development cases.** It certifies 16 of the initial 18
releases, versus 17 for the existing exact oracle, and none of the four stress releases.
Two stress outputs have finite Q upper bounds; those bounds are far too wide to resolve the
reporting decision. This is a verified mathematical implementation checkpoint, not evidence
of superiority or a paper-ready method.

## Implemented method and guarantee

The unchanged pre-timing [protocol](protocol.md) has SHA256
`bb4a4698d6e69c523c52c6b3984f2a50b9f79a2484f359536608dcbaa022757a`.
[frontier.py](frontier.py) carries the exact structural key
`(time,riskA,riskB,remainingEventsA,remainingEventsB,exactKMA,exactKMB)` through a layered
joint traversal. Histories with the same key merge by the coordinatewise union of rational
score U and variance V intervals. Each retained representative prefix is an actual history;
merging does not average it or claim its score represents the entire box.

The ordinary logrank increments depend only on the key and the proposed event counts.
Every feasible event/censor count transition obeys the original rounded-curve, exact risk,
event-total and terminal-exhaustion constraints. Thus merging exact structural states retains
all feasible histories, with potentially loose U/V dependence. It avoids storing all complete
arm paths and their Cartesian products; it can still create many joint prefix states.

For every unexpanded state, suffix score lies in [-eB,eA] and suffix variance in
[0,(eA+eB)/4]. These rational enclosures are added to its prefix rectangle. Q bounds follow
the squared distance of the U interval from zero divided by maximum variance, and maximum
squared U divided by positive minimum variance. Zero lower variance permits an infinite
upper bound. The ordinary-logrank U=V=0 convention is handled explicitly; a zero-variance
rectangle excluding U=0 cannot produce a certificate.

On a partial expansion, the whole active parent is retained alongside its already-generated
children, all unexpanded current states, and terminal states. The overlap deliberately covers
unprocessed siblings. Only fully processed parents are removed. The union of all these
regions encloses every compatible full history even if some retained prefixes have no feasible
completion. The protocol gives the contribution and coverage arguments in detail.

The solver establishes nonemptiness using actual paths found by a bounded release-only
memoized feasibility search, or a full representative path reached by joint traversal. A
stable outer interval cannot certify without such a witness. A crossing outer interval is
only unresolved; `opposing_witnesses_found` requires actual witnesses of both decisions.
Failure to find an opposing witness is not proof that none exists. No probability distribution
over boxes or patient histories is assumed.

The exact grouped-time target is unchanged. Continuous event-time uncertainty, sparse graph
observations and raster digitization remain outside this model. The original exact oracle
source and fixtures are unchanged and imported read-only for the declared schema, rounding
map, critical-value proof and witness scoring; expected verification values come from an
independent subject-record implementation.

## Fixed-case results

[run_existing.py](run_existing.py) reads only committed released-summary files. It never opens
the hidden original rows. Limits are 100,000 joint transitions, 20,000 stored states, and
eight seconds for the joint search; each arm's feasibility search has 50,000 nodes and two
seconds. An active parent retained at interruption can make the recorded covered-state union
20,001, deliberately preserving coverage beyond the stored-state cap.

All 22 fixed releases finished with an output in 41.911 seconds total on this host. Sixteen
initial releases completed traversal: seven stable reject and nine stable nonreject. All
16 decisions have actual compatible witnesses and agree with the original exact oracle's
classification. Coordinatewise boxes sometimes widen exact extrema even after complete
traversal; `complete_traversal` does not mean the reported interval is the exact attained range.

Two sparse n=80 initial releases stopped early. The equal-hazard case reached the state cap;
the .32-hazard case reached the time limit. Their Q outer intervals were [0,382925/893] and
[0,5080230808387/118327179511], respectively. Both are unresolved, though the latter was
certified by the original enumerator. Many initial prefix states have not yet been ruled out
by later curve/risk constraints; the current joint traversal pays for these states before
discovering their infeasibility.

| Fixed stress release | Q outer interval | Decision | Elapsed seconds | Peak traced Python bytes |
|---|---|---|---:|---:|
| n80, K12, 2 decimals | [0,8957/12] | Unresolved | 6.961 | 22,864,905 |
| n200, K12, 2 decimals | [0,infinity] | Unresolved | 3.492 | 20,836,629 |
| n80, K6, 1 decimal | [0,infinity] | Unresolved | 3.071 | 19,381,066 |
| n200, K20, 2 decimals | [0,105393/52] | Unresolved; no full witness found under budget | 8.083 | 22,531,132 |

All four stress joint searches reached the state cap. The first three have actual compatible
full witnesses. Both feasibility searches for the last case reached their two-second limits;
this is not evidence of incompatibility. Its outer Q interval is valid conditionally for all
compatible histories, but no certificate is issued without nonemptiness evidence from the solver.

The finite stress upper bounds, approximately 746.4 and 2026.8, still correspond to p ranges
extending essentially from zero to one. They do not deliver useful decision certification.
The second displayed lower p bound underflows to zero in floating arithmetic; all certification
uses rational Q bounds, not displayed p values.

Timings include tracemalloc instrumentation and witness search, and the original oracle used
different limits and instrumentation. These host timings are not a fair speed benchmark.
Memory measurements are peak traced Python allocations, not operating-system RSS. Original
per-case limits, timings, merge counts, covered regions, witnesses and exact intervals are
preserved in [results.json](results.json) and the [original run log](run.log).

## Actual verification

[verify.py](verify.py) reuses the original checker's 56 tiny subject-category multisets and
independent subject-level summary/score functions. Under the previously used coarse release
design these form ten release groups. Fifty complete or forced-limit runs exercise 2,330
individual-history coverage checks: every compatible history has at least one retained region
with the identical exact structural key and a prefix U,V inside its rectangle. This is stronger
than checking a loose final scalar interval. All 40 interrupted runs retain the active parent;
745 merge operations are exercised.

The worker checks also verify half-empty search handling, time/state stops, incompatible
releases, zero-variance and impossible-coordinate boxes, and the nonemptiness gate. A zero-event
partial interval Q=[0,0] cannot certify when witness search is disabled, but can certify with
an independently valid full witness. All 18 original exact oracle extrema fall within the
new intervals. Every full witness returned across the 22 fixed releases independently
reproduces its released summaries and score. The checks passed in 0.219 seconds; see
[verification.json](verification.json) and [the original verification log](verification-run.log).

These are separate worker implementations, not an ultra review. The coordinator additionally
reported independently checking 864 unequal-arm release/budget combinations and 2,016
subject-history coverage cases, including 531 interrupted and 108 no-witness runs, against
the same unchanged source digest. Its original script/result belong to the integration
receipt; this packet does not substitute a worker claim for that independent evidence.

## Reproduction and next action

Run from any directory with Python; outputs resolve beside the scripts:

```text
python -B run_existing.py
python -B verify.py
```

The first command overwrites timing/results files. To preserve original execution evidence,
copy this directory and its sibling oracle directory before rerunning. A single release can
also be passed to `python -B frontier.py release.json --output result.json`.
Standard-library modules suffice. [manifest.json](manifest.json) identifies every file,
source/fixture dependency and the known base revision.

The specific next algorithmic improvement is exact per-arm suffix reachability pruning before
forming joint transitions. The current bounded feasibility search finds one witness but does
not share a complete table of feasible suffix states with the joint traversal. Such a table
could eliminate dead prefixes earlier while retaining exact KM keys; interrupted feasibility
proofs must remain unknown, never be marked infeasible. U/V box dependence may still dominate
after that pruning, so tighter correlated regions or subdivision may subsequently be needed.
Raising caps or adding new cases is not a demonstrated repair. This checkpoint stops here.

No new scientific fixtures, held-out or empirical benchmark data were generated/opened. No
manuscript, shared queue, main checkout, commit or publication state changed. No normal/full
preflight or ultra review is claimed. All worker processes are finished. The worktree base is
`920fed4fff362b9cef8e97fb7b3356209c77c7af`; actual model/effort were inherited and are not
independently exposed in this worker's tool outputs.
