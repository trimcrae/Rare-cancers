---
id: DOC-FP-RESIDUAL-R8-PATCH-NOTE
title: "Unapplied patch — PUB-FUSION-PARTNER current-claim replacement (R8)"
level: L4
kind: patch-note
status: prepared-not-applied
date: 2026-09-08
last_verified: 2026-09-08
---

# Unapplied patch — `PUB-FUSION-PARTNER` current claim

⛔ **THIS PATCH IS NOT APPLIED.** `systems/graph/publications.json` is a parent-owned shared file. It was read
and diffed against, and it is **byte-unchanged** by this author (`IDENTITIES.md`). Applying it, checking
concurrent ownership, and regenerating `systems/views/` (which is generated from this file) are the owner's
acts, not this author's.

**Patch:** `PUB-FUSION-PARTNER-current-claim-replacement.patch`
**Target:** `systems/graph/publications.json`, entry `"id": "PUB-FUSION-PARTNER"` (around line 231; the
changed lines are in the hunk at `@@ -236,9 +236,9 @@`).
**Baseline it was cut against:** `systems/graph/publications.json`, 63,825 bytes, sha256
`11b8a785ac95809d844f46f6427601c67f73f9137a063f6d91b4b93ba0d5bf53`. ⚠ That live file **differs from the
63,611-byte copy pinned in the focused-verification capsule**, because other lanes write this file; the patch
was deliberately cut against the live bytes. Re-check before applying.
**Verified:** `git apply --check -p1` returned exit **0** — `checks/05-r8-patch-apply-check/`.
**Scope:** exactly two fields of exactly one entry — `what_it_would_claim` and `outcome_potential_why`. No
other publication entry is touched and **no repository-wide graph audit was performed**.

## What it does, and why this narrowing requires it

The current `what_it_would_claim` is a **live** publication claim field, not superseded history. It still
asserts each of the following, all of which this batch withdrew from the manuscript, the artifact and the
producer:

| still asserted in the graph | status after this batch |
|---|---|
| the two-cohort 73-patient pool, disease-specific death 7/15 = 46.7 % vs 6/58 = 10.3 % | **withdrawn** (R1 / register A43) — the Huang 2023 Table 1 inputs are verified by no retained original and are quarantined. Scoped absence, not a finding that the published counts are wrong |
| "a zero-event arm yields no magnitude at any denominator" | **withdrawn as mathematically false** (register A44); replaced by the observed-versus-population-magnitude distinction (R2) |
| "the partner may be a marker for a big tumour rather than for a biology", 78 % of TAF15 tumours over 10 cm read as the explanation | **withdrawn** (R3) — the size-causation reading; no coefficient, interval, event count or specification is available, and size may lie on the causal path |
| "the entire published TAF15::NR4A3 antiangiogenic-TKI experience" | **withdrawn** (R8/R9) — no systematic search was run, so nothing here is a census |
| "The review literature's metastasis claim is supported by neither count-bearing cohort in either direction" | **withdrawn** (register A51, carried here) — a different endpoint, and a non-significant crude tally cannot refute a cautious DMFS trend |
| response evidence given as a bare 3-to-5-patient direction | **relabelled CONDITIONAL** at every live site (R2) |

The replacement states the **selected conditional descriptive synthesis** and its source limits instead: the
conditional response reconstructions with their assumptions named; one series carrying the main event
analysis with a second separately source-verified series reported beside it; prevalence as a conditional
share among named-partner-assigned cases, with the confirmation stage (26/58/12/67) distinguished from the
named-partner stage (24/57/11/62); an explicit **WITHDRAWN** list; and an explicit source-limits list. It
keeps the existing "no efficacy, safety, selectivity, therapeutic window or clinical readiness" language and
adds that no wet-lab work was performed.

`outcome_potential` (`live_positive`), `patient_path`, `state`, `target_venue`, `level`, `kind` and `document`
are **unchanged**. `outcome_potential_why` is narrowed so it no longer implies the paper supports changing
which patients receive an active class.

## What must happen if it lands

1. The owner checks concurrent ownership of `systems/graph/publications.json` before applying.
2. `systems/views/` is **generated** from this file; regenerating it is the owner's act, not this author's.
3. The correction register's preamble records that the shared entry disagrees with the paper **until** this
   patch lands; that sentence should be updated by whoever applies it, with the date and the resulting
   binding.
