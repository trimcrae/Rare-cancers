---
id: DOC-IPD-INTERVAL-ORDER-REPORT-20260906
title: Continuous-time interval-observation oracle development result
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Report a checked finite representation preserving continuous-time observed-IPD logrank.
scope: Five predetermined tiny synthetic development fixtures; no held-out or realistic benchmark.
audience: [maintainers, autonomous research agents]
---

The tiny oracle exhaustively represents continuous-time exit orders consistent with uncertain KM coordinates, exact risk counts and available event totals. Its canonical slots encode pooled weak orders inside open cells; they do not round uncertain event times onto a common physical grid. Actual event ties and event/censor ties are preserved. This addresses the previously identified target-preservation gap at a tiny mathematical checkpoint. It does not establish scalability, practical certificate utility or paper readiness.

## Frozen model and evidence

The coordinator reviewed `protocol.md` before fixture generation (SHA256 `d593101e8cf4e7f538212cb8b085c528031cb3db20b92501ec3d27514d665e0f`). `fixtures-plan.md` then fixed the five deterministic cases and all seven original-record checks before JSON generation or results (SHA256 `3713e24a405ff738fa4e9b3772ce1e64c275de5c35fcd9ffbacb34029248486b`). Both exact files are unchanged. No random search, significance-crossing search or outcome-based fixture selection was performed.

The release mechanism is an ordered set of closed horizontal/vertical coordinate boxes. Each box asserts existence of a right-continuous KM observation inside it; within-arm observation timestamps must be nondecreasing, and equality is allowed. It does not model a complete raster plot or error in an entire connecting line. Exit times can be any real values in (0,T]. Exact risk counts are pre-event counts; all events at a tied time use that risk set before censor removals. Missing event totals are enumerated rather than implicitly supplied.

The completeness argument in the protocol uses at most N weak-order groups per open cell, where N is the total number of records. Fixed boundaries include all box endpoints and risk times. A monotone within-cell map preserves every event/censor order, event risk set, true tie and box feasibility. Conversely each canonical group arrangement is an admissible continuous-time dataset. Observation feasibility is checked on fixed points and segment midpoints; the independent checker uses explicit possible observation sequences rather than the main oracle's greedy selection.

## Actual results

| Fixed synthetic case | Nodes | Feasible canonical classes | Distinct exact (U,V) | Exact Q range | Display p range |
|---|---:|---:|---:|---|---|
| wide | 10,655 | 504 | 5 | [0,1] | [0.3173105,1] |
| exact_boundary | 1,048 | 6 | 1 | [0,0] | [1,1] |
| ordered_impossible | 10,655 | 0 | 0 | empty | empty |
| unknown_events | 47,655 | 1,410 | 15 | [0,49/17] | [0.0895551,1] |
| n3_boundary | 28,102 | 36 | 1 | [0,0] | [1,1] |

Q=U²/V is the ordinary logrank chi-square statistic. Its values and extrema use exact rational arithmetic. P values are floating display transformations, not outward-rounded numerical certificates. Class counts describe equivalence classes, not patient probabilities or prevalence. All five searches completed; the longest oracle call took approximately1.46 seconds on this host, which is not a moderate-scale performance claim.

In the fixed wide fixture, A:event5/4,censor11/4 and B:event7/4,censor5/2 give U=1/6,V=17/36,Q=1/17,p approximately0.8083652. Moving A's censor to3/2 remains compatible with the same released boxes/counts but gives U=1/2,V=1/4,Q=1,p approximately0.3173105. Tying the two events at3/2 gives Q=0,p=1. These were predetermined examples; they demonstrate the ordinary observed-IPD statistic changes with admissible order while no threshold-crossing claim is made. An A censor tied to B's event remains in its pre-event risk set, as independently checked.

The exact-boundary fixture observes survival1/2 at the same exact time at which risk is2. Its solutions include simultaneous events and censor exits, preserving right continuity and pre-event counts. The n3 fixture checks a larger within-arm count composition with exact boundary events. The ordered-impossible fixture's boxes are individually satisfiable, but require timestamp2 followed by timestamp1; its exhaustive empty set correctly reflects the joint ordering constraint.

## Independent validation

`verify_independent.py` does not import the oracle. It separately generates labelled event/censor assignments to every canonical slot, permitting slot gaps and retaining duplicate geometric representations. The wide fixture has50,625 unfiltered labelled assignments,9,025 feasible assignments and exactly the same five attainable (U,V) values as the grouped oracle. Exact_boundary has10,000 unfiltered labelled assignments,25 feasible assignments and the same single (U,V). Different representative counts are expected; full score sets, rather than counts, are compared.

The checker directly verifies all seven predefined original datasets, every returned witness (22 total) and every supplied witness observation timestamp. All original scores are contained. It independently recomputes risk sets and KM values, tests ordered observations by explicit products of candidate sequences, and verifies malformed boxes are rejected. Forced node limits1 and100 stop with `complete=false`, no proved nonemptiness and universal p bounds[0,1]. An incomplete search never turns its partial scores into a certificate.

A separate call to SciPy1.18.1 logrank reproduced all22 witness p values with maximum absolute discrepancy2.22e-16. `verification.json`, `scipy-verification.json` and original logs record the checks. The implementation also rejects duplicate exact rational risk-time keys, avoiding ambiguous aliases such as1/2 and0.5. No repository normal/full/ultra checks were run by this worker.

## Reproduction and limitations

Run `generate_fixtures.py`, `run_fixtures.py`, then `verify_independent.py` with Python3. The first three use the standard library only. `verify_scipy.py` additionally needs SciPy; this run used the existing repository cache via PYTHONPATH. Precise executed fixture commands, runtime and exit codes are in `runs.json`. The executable accepts a release JSON and output path, with an explicit positive node limit. It reads no original data; originals are confined to verification. `runtime.json` records the actual interpreter and frozen source hashes.

All exits must occur by the released horizon; unreported tail follow-up, delayed entry and competing risks are not included. Observation intervals and exact counts are assumed to be valid constraints. This protocol is a coordinate-observation model rather than an empirical digitization-error model. The search remains combinatorial. Larger inputs can return incomplete universal bounds; improved frontier bounds belong to the separately owned workstream. This packet does not implement query optimization or demonstrate benefit beyond margin abstention or published reconstruction methods. The previously executed baseline packages were not rerun. Zenodo contents and held-out material remain unopened.

The next integration step is an independent review of the coverage argument and code against this fixed observation mechanism, followed by deciding how to combine order uncertainty with tractable conservative bounds. All local processes have completed. No main/shared-state edits, commits, manuscript changes, publication, paid APIs or GPU work occurred.
