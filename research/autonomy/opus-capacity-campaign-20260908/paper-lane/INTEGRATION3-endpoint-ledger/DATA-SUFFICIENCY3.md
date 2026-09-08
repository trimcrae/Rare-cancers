---
id: DOC-OPUS-CAMPAIGN-INTEGRATION3-DATA-SUFFICIENCY
title: "Data sufficiency after the C2 v3 propagation"
level: L4
kind: assessment
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Data sufficiency after the C2 v3 propagation

This supersedes nothing in `INTEGRATION2-endpoint-ledger/DATA-SUFFICIENCY2.md` except where it says
so. That document remains readable and unmodified; read it for the parts unchanged here.

## The bottom line, first

**The integrated ledger is complete, and the endpoint analysis is not supportable. The endpoint
paper stays PARKED.** The propagation moved the ledger **away** from supportability, not toward it.

## What changed

1. **A fourth unresolved condition is now explicit.** v2 named three: (a) job 2 and job 3
   unconfirmed, (b) no cohort-disjointness evidence in this cache, (c) semantic correspondence
   among competing records not established with no pre-registered selection rule. C2 v3 adds
   **(d) the registry join itself is not established** —
   `NOT_ESTABLISHED_REGISTRY_JOIN_FIELDS_ABSENT_FROM_THIS_CACHE` on **all 552 rows** — so no row
   has a source-verified binding between a results group and a registered arm.

2. **The arm-attribution axis has no unblocked complement.** v2 reported 494 blocked on that axis
   and 58 not. Under v3 the axis blocks all 552, and `integration_state` is BLOCKED on 552 of 552.
   v2's two rows with no component-specific block are now blocked. Nothing was ever eligible on
   that basis, and nothing is now.

3. **Zero established contradictions.** The 83 sole-arm cardinality flags and the 8 contested-flag
   promotions are demoted to unresolved mapping and evidence tensions
   (`UNRESOLVED-TENSIONS3.tsv`). This is **not** a finding that the records agree. It is a
   statement that the evidence available in this cache does not establish incompatibility: the
   cardinality mismatch is incompatible only under a mapping v3 marks unproved, and a contested
   flag opposes an inference to a source field rather than one source assertion to another. Every
   flag is retained. **Fewer established contradictions here means less established, not more
   agreement.**

## What is still insufficient, and therefore withheld

Unchanged from v2, and now with (d) added: no response rate, no proportion, no unique-patient
total, no cross-disease capacity bound, no control comparison, no agent-independent effect, no
eligibility subset. `proportion_authorisation` reads `NO_PROPORTION_AUTHORISED_IN_THIS_INTEGRATION`
on all 552 rows and the five sentinel columns read `NOT_DERIVED` on all 552 (`J7`, `J13b`, `J18`).

Correcting a component's vocabulary and register discipline is not a licence to compute, and a
complete curation ledger is not automatic scientific eligibility.

## What would change this

For (d): a source statement binding results groups to registered arms for these records — the
registry join fields absent from this cache. For the demoted tensions, the same, plus verbatim
source text able to be set against a registry-side statement of the same fact. Neither is
obtainable within this lane's fences, and no acquisition is attempted here.

**Findings F1–F10 of `HOLD-endpoint-extraction-validity.md` are untouched and unsatisfied by this
ledger.**
