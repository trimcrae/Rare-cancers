---
id: DOC-ASO-EXTREMA-CERTIFICATE-FOCUSED-REVIEW-20261002
title: Focused static review of the ASO union extrema certificate
kind: memo
status: live
level: cross-cutting
purpose: Assess whether the independent certificate implementation establishes the declared global union extrema and rejects false extrema claims.
scope: >
  Static inspection of four pinned source files and their synthetic test definitions.
  No local compilation, execution, corpus scan or cloud-result verification was
  performed for this review. This is not a manuscript or submission review.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

# Assessment

No concrete correctness defect was identified in the inspected global union certificate logic. This conclusion is based on source inspection, not a claim that the currently executing cloud job passed. The reviewed revision is `e4e41e8cc93e66c2a576ec8a6f6f4acba5c5d496`; runtime results from [run 37017553101](https://github.com/trimcrae/Rare-cancers/actions/runs/37017553101) require a separate execution receipt.

**Eligible windows and orientation.** The engine derives an aligned full-window start as `match_end + 1 - pattern_length - target_interval_left`. It rejects negative starts, windows extending past a record, and any ambiguity anywhere in all 16 aligned bases. Record processing resets automaton state; U is normalized to T. Thus a short core occurrence at an end, or a core flanked by an ambiguous base, does not count. The runner binds targets to the pinned catalogue and checks reverse-complement correspondence to the antisense string. The six-base core uses zero-based `[5,11)`, consistently with the accepted endpoint definition.

**Gap extremum proof.** Generated intervals enumerate every possible left endpoint 0–5 at the challenged length, requiring the right endpoint to cover position 10 and remain within position 15. Attainment at g and absence at g+1 suffice: every longer contiguous matching interval containing the six-base core contains a subinterval of length g+1 that also contains that core. At g=0 the exclusion challenge is length 6 and no attainment is needed; at g=16 a longer interval is structurally impossible. Joining both corpora requires no counterexample in either and attainment in at least one.

**Hamming extremum proof.** Literal recursion enumerates each subset of mutated positions in strictly increasing order and each alternative base, including the unchanged target, through the claimed radius. Resetting the current position after recursion preserves earlier selected substitutions. For the supported pinned claims h=0–2, the minimum observed distance among these patterns must equal h; the no-hit sentinel 3 cannot be mistaken for attainment. Every smaller distance is included, so both understated and overstated claims are rejected. Duplicate target sequences retain separate query-ID hits; duplicate query IDs are rejected.

**Binding and execution contract.** The runner verifies the result Git blob and catalogue/archive/GENCODE byte counts and SHA256 digests, binds the same 220 IDs and target strings, requires exact Hamming bounds, builds the engine, runs its tests, and invokes it independently on both corpora. It compares complete corpus census metadata and exact certificate-ID coverage before writing a passing receipt. The outer runner enforces download identity, disk reserve, a whole-lane deadline, and child-process-group termination on a guard failure. Certificate TSV files are generated and read in a new output directory. They are not externally authenticated cryptographic proofs against an adversary modifying local files.

**Actual test definitions.** Fourteen unittest methods cover first/last complete windows; no record bridge; N in selected core/flank positions; incomplete-window end exclusion; all 16 single-mismatch positions; a distance-two fixture; lower/higher claimed gaps; lower/higher claimed Hamming distances; radius-two nonattainment; zero gap; U/lowercase/whitespace normalization; gzip and GENCODE headers; duplicate target sequences; missing/duplicate certificate coverage; and invalid challenge ranges. The seeded randomized test compares 360 threshold challenges (15 targets × 3 radii × 8 gap values) against direct literal window enumeration. Mutated claims are submitted through the engine and rejected by the combiner; this is not exhaustive mutation testing of every serialized certificate field.

**Limits.** This new test file does not explicitly exercise a gzip read error, duplicate FASTA identifiers, declared-header-length mismatch, a line spanning the 65,536-byte read buffer, every malformed TSV value, or an actual source-pin mismatch. These are coverage limits, not observed wrong results. Tests are synthetic and finite. The certificate independently checks only global union Hamming minima and complete-core gap maxima; it does not independently establish every stratum's nonzero extrema, occurrence counts, rank calculation or biological consequence. Its literal representation and automaton differ from the original two-bit lookup, while both rely on Hamming-neighborhood enumeration. No local tests or cloud results were claimed by this review.

# Exact reviewed code

All paths are relative to `research/autonomy/continuation-2026-10-02/` at the pinned revision above. Digests were computed from raw GitHub response bytes without saving another source checkout.

| Path | Bytes | SHA256 |
| --- | ---: | --- |
| `extrema-confirmation/extrema_certificate.cpp` | 6677 | `ab1cc02ad39857df724bded032f9c2eacf63f4914d554c01b8bff42cd665cd32` |
| `extrema-confirmation/run_extrema_confirmation.py` | 6880 | `3393f3e81ef78886e8e2a6ea65109e55ca582aa6994e4e5570eca6c2b2f0cc4d` |
| `extrema-confirmation/test_extrema_certificate.py` | 6688 | `725f36a1c1e237aa15804f292fd4e383e3c8816587974d333c5ef5d8e18c6248` |
| `run_followups.py` | 3652 | `8b2ca562620b60abef631b923997ef3fbccabcee66f525a385ddd8b6ca4fb910` |
