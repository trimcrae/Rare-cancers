---
id: DOC-IPD-SUFFIX-CHECKPOINT-20260906
title: Prune only suffixes proved infeasible before joint expansion
kind: memo
status: live
purpose: Test the specific explanation for excessive joint prefix states without changing the statistical target.
scope: Next bounded algorithmic checkpoint on the same 18 development and four stress releases.
audience: [maintainers, autonomous research agents]
date: 2026-09-06
last_verified: 2026-09-06
---

The first frontier solver preserves interrupted-search coverage but has weak utility: 16 initial certificates versus the exact oracle's 17, and no stress certificates. Many joint prefixes are generated before later marginal curve/risk constraints establish that they cannot complete. Test exact per-arm suffix reachability before forming their joint transitions. This is an implementation hypothesis, not a promised speedup or a paper contribution by itself.

For each exact arm key (time, risk count, remaining events, rational KM value), memoize whether any completion satisfies all future released marginal constraints. A found completion proves true. False requires exhausting every admissible successor and proving each cannot complete. A timeout, node cap, interrupted successor loop or unproved descendant returns unknown; unknown must not become false or be pruned. The marginal feasibility search receives only the released summaries. A true cache entry must have reconstructible continuation evidence if it is used to supply the global nonemptiness witness.

Reject joint transitions only when one marginal suffix is proved false. Preserve unknown transitions, or halt with their parent/frontier region still covering them. Exact structural keys and outward U/V rectangles remain unchanged. Charge suffix-search work and memory to the reported run budget; caching is not free preprocessing. State any different limits or instrumentation before comparing cost. Retain the first solver and all original outputs unchanged.

Freeze the short algorithm and budget contract before execution. Use only the existing 22 releases. Independently check retained-history coverage against exhaustive tiny subject histories and original oracle extrema, including forced termination inside a suffix recursion and after partially exploring successors. Check that unknown/false are distinct in cache state, and that no actual compatible suffix is pruned. Report per-arm cache counts, proved infeasible states, unknown results, joint states/transitions, total runtime, memory, Q widths and certificates. No new success-case search, held-out generation, or empirical benchmark access.

The interval-order oracle is now a separately checked tiny representation of continuous-time uncertainty. It does not solve scalability and must not be silently replaced by this grouped-time model. A useful final method still needs realistic uncertainty, competent published comparators, calibrated abstention and fair additional-count comparisons. A targeted primary prior-art check of bounds under partial orders/coarsened survival information should accompany development before committing to a manuscript; this is a focused novelty question, not another paper inventory.
