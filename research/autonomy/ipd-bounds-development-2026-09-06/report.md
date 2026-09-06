---
id: DOC-IPD-BOUNDS-DEVELOPMENT-RESULTS-20260906
title: Exact grouped-time bounds work on small releases and expose larger search limits
kind: memo
status: live
purpose: Report actual compatibility computation and its tractability limits for the next research decision.
scope: Synthetic development with exact integer times; not held-out validation, clinical evidence, or a finished preprint.
audience: [maintainers, autonomous research agents]
date: 2026-09-06
last_verified: 2026-09-06
---

**A rigorously scoped extension is executable: both arms can censor, events can tie, and
survival probabilities can be rounded. The current exhaustive method does not scale to the
four planned stress releases under the bounded run limits.** That is an implementation
development result, not a scientific no-go or evidence of useful performance beyond published
point reconstruction and margin abstention. Those comparisons remain outstanding.

## Scope and exactness

The unchanged pre-outcome [protocol](protocol.md) defines genuinely integer-valued observed
times, event-before-censor ties, ordinary pooled logrank variance, exact initial/event counts,
selected pre-event risk counts, and rounded post-step KM values at every grid time. No records
remain after the terminal grid time. The solver receives only the released JSON. Hidden
synthetic records are used after solving to verify containment, never to choose compatible
paths or the query.

For each arm, every labeled individual-level dataset induces nonnegative aggregate counts
`(d_t,c_t)` summing to n. Conversely, any such count path expands to records at the grid times.
The published summaries and logrank statistic are invariant to subject labels within that
path. The recursion in [bounds.py](bounds.py) considers all d from zero to the lesser of the
current risk and remaining event total, then every possible c; at the final time c exhausts
the remaining subjects. Pruning only rejects a current rounded KM mismatch, a specified risk
count mismatch, too many/few remaining possible events, or a future risk count larger than
the current remaining count. Each condition is necessary, so no compatible completion is
removed. Thus completed arm traversals recover all compatible paths; their completed
Cartesian product yields the exact rational extrema of `Q=U^2/V`.

Floating p-values are descriptive. Stability decisions use exact Q extrema and a rational
enclosure of the chi-square-one 0.95 quantile:
`3.84145882069412 < q_critical < 3.84145882069413`.
The executable proof bounds pi via the Machin arctangent identity and alternating series,
bounds the error-function series by its next term, and bounds square roots using integer
arithmetic. It verifies p at the lower Q endpoint is strictly above .05 and p at the upper
endpoint is strictly below .05. A Q within this tiny enclosure remains unresolved rather
than relying on floating rounding. The zero-score/zero-variance convention is p=1.

If either arm or the product traversal is incomplete, the result is unresolved with universal
outer bounds Q in [0,infinity], p in [0,1]. Partial extrema, if present, are explicitly not
certified bounds. An empty complete feasible set is an incompatible release, not a stable
decision. The implementation is a reference enumerator; it does not claim useful partial-search
bounds beyond the universal interval.

These guarantees apply to the declared discrete observed records. Binning a continuous-time
curve can create ties and discard ordering information, changing the original logrank target.
This implementation does not bound those continuous-time possibilities or pixel-coordinate
uncertainty. Releasing every grid value also supplies more information than a sparse plotted
curve. A later realistic release model and validation must address these gaps explicitly.

## Actual development results

[develop.py](develop.py) generated nine retained datasets at seed 20260906 with n=20,40,80
per arm, six grid times, arm-A event hazard .18, arm-B hazard .18,.32,.65, and conditional
censor hazard .08. Each supplies both a sparse risk table (times 1,4) and a dense table
(all six times). All KM probabilities have two decimals. They are development cases, not
independent held-out datasets; the two release designs share each original dataset.

All 18 releases enumerated completely. Eight were stable reject, nine stable nonreject,
and one unresolved; all true observed statistics were contained. These are descriptive
counts from a small selected development design, not an estimated certification rate.
All nine dense releases identified a single aggregate path per arm, making them easy cases.
The complete initial generation/solve run took 2.044 seconds on this host, recorded in
[development-results.json](development-results.json) and [the original log](development-run.log).

The n=80 equal-hazard sparse release had 90 compatible A paths and 118 B paths, giving
10,620 pair classes. Its approximate p extrema were 0.04879248 and 0.10825663; original
observed p was 0.07603997. Thus opposite reporting decisions genuinely occur within this
rounded-release model. This case arose among the fixed nine datasets; there was no search
until a threshold-crossing case appeared.

The release-only minimax rule selected B's risk count at time 2. Across its nine possible
answers, eight give stable nonrejection and one (risk 56) remains unresolved. The actual
answer, inspected only after selection, was 63; this leaves 1,530 pairs with approximate p
extrema 0.05326903 to 0.09746466. A full re-solve with that added count matches the predicted
subset exactly. This illustrates conditional information recovery; it does not show that one
query always resolves ambiguity, estimate average query savings, or compare with equally
spaced counts. [Query verification](query-verification.json) records all possible answers.

Because the six-time cases were easy, a [dated development amendment](development-amendment.md)
specified four further cases before their generation, at seed 2026090601. No original
protocol, fixture, or outcome was rewritten. All four have sparse risk times, hazards .08/.12
and conditional censor hazard .04. Limits were 300,000 visited nodes and 10,000 accepted
paths per arm, 25,000 pairs, eight seconds per phase (time checked periodically).

| n per arm | Grid times | Probability decimals | Observed result |
|---:|---:|---:|---|
| 80 | 12 | 2 | A reached node limit after 531 paths; B completed with 4,163 paths. |
| 200 | 12 | 2 | Both arms reached 10,000-path limits. |
| 80 | 6 | 1 | Both arms reached 10,000-path limits. |
| 200 | 20 | 2 | Both arms reached node limits before accepting a path. |

All four correctly return unresolved universal bounds; zero accepted partial paths in the
last case is not evidence of infeasibility. Their originals independently reproduce their
released summaries. No Cartesian calculation was attempted once an arm was incomplete.
The four solve times were 10.761, 0.735, 0.919 and 4.540 seconds, respectively; the first
is a sum of two arm phases. See [stress-results.json](stress-results.json) and
[the original stress log](stress-run.log). Increasing caps alone has not been tested and is
not a demonstrated solution to the combinatorial growth.

## Actual verification and reproducibility

[verify.py](verify.py) independently filters subject-category multisets, recomputes summaries,
and evaluates subject-level logrank arithmetic; production curve/rounding/score functions do
not supply expected results. It checks all 56 multisets for n=3,K=3 under four risk/rounding
designs: 107 distinct arm-release groups, 3,357 release-pair comparisons and 12,544
subject-pair evaluations. Complete accepted path sets and exact Q extrema agree. This
exercises both-arm censoring and tied events. Explicit tests cover half-up boundaries,
both-arm all-censored V=0, incompatible summaries, and forced node/path/time/pair exhaustion.

All 18 moderate releases, their true scores, and both endpoint witnesses are independently
recomputed from subject records. SciPy 1.18.1 ordinary logrank p-values agree within
3.89e-16 across the 18 comparisons. The main verification took 58.515 seconds; the separate
10,620-pair query partition/selection check took 3.839 seconds. These are distinct worker
implementations, not a claim of independent external scientific review. The coordinator is
performing a separately owned check; its receipt belongs to integration.

Run with standard-library Python (SciPy is an optional extra comparison in verify.py):

```text
python -B develop.py
python -B verify.py
python -B verify_query.py
python -B stress.py
```

Each script resolves outputs beside itself. These commands overwrite the development outputs;
copy the directory elsewhere first when preserving original execution logs and timings.
To solve one released-summary JSON without the hidden records:

```text
python -B bounds.py release.json --output bounds.json --seconds 15 --max-pairs 100000
```

Source/fixture hashes and actual outputs are preserved in [manifest.json](manifest.json).
No held-out records were generated or opened, no baseline code was edited, no manuscript,
shared queue, publication state, commit, or main checkout was changed. No normal/full
repository preflight or ultra review is claimed by this worker. All worker processes are
finished at this checkpoint. The known starting revision is
`863a1917f98b55772243807d32c8abd5ee82d511`; model/effort were inherited from the parent and
are not independently exposed in this worker's tool outputs.

## Next scientific decision

Keep this exact enumerator as a small-model oracle. The four stress failures identify the
next mathematical development need: avoid materializing every compatible path, for example
with a reachable-state graph and rigorously conservative bounds on the jointly attainable
logrank score and variance. Merging states solely because their KM/risk summaries match is
unsafe when their accumulated U and V differ. Any accelerated bounds must enclose the exact
small-model extrema and return unresolved when the proof is incomplete.

Actual IPDfromKM/CIFresolve comparison, development-calibrated margin abstention, added-count
budget comparisons, a model admitting realistic figure/time uncertainty, and a frozen held-out
evaluation remain necessary before deciding whether the method merits a paper. This checkpoint
advances those questions by providing a correct oracle and observed failure cases; it does not
replace them with an easier completion criterion.
