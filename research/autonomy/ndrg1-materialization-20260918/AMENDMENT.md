---
id: DOC-NDRG1-MATERIALIZATION-20260918
title: NDRG1 full-membership background materialization amendment
kind: memo
status: live
date: 2026-09-18
last_verified: 2026-09-18
audience: [maintainers, autonomous research agents]
purpose: Make the current artifact reflect the already-adjudicated S53 result and preserve its controls.
scope: AUT-PD-170 generator pin, machine-readable artifact and result-specific tests; no new source retrieval or publication.
---

The generator now explicitly selects `full_membership_background_null`, using the existing
input blocks. This implements the result already measured in
[S53](../sprint-2026-09-01/S53-HYPOXIA-BACKGROUND-READ.md), rather than selecting a read that retains
the former curated-only finding. The old generator and artifact remain recoverable at base commit
`97929c00ccbd3c7b10e1d41e0da28a598cd1f65d`; the original S53 and original protocol remain unchanged.

The regenerated artifact matches all 24 retained panel rows at S53's displayed precision:
[comparison receipt](S53-COMPARISON.json). GSE24369 has 2/6 hypoxia and 3/6 PPARγ panels above
their own nulls; GSE4303 has 5/6 and 0/6. Neither series meets the original joint criterion.
The smaller series' remaining hypoxia-leaning pattern must not be described as no signal.
These small, mixed-histology observational series and uncorrected panel comparisons establish
neither mechanism nor therapeutic suitability. S53's prose says three large-series hypoxia
failures, but its table and 2/6 count imply four; its original text is preserved, not silently fixed.
No full-precision historical probe JSON was retained, so this is not a byte-identity assertion.

Seed 20260829, 2000 null draws, size-matching, thresholds, subject exclusion and the original
joint criterion are unchanged. Historical curated self-inclusion and selection-diagnostic
mutations remain explicit tests of that historical configuration. Current artifact checks bind
scores and sample counts to independently enumerated subject-excluded full membership. Full
panels retain null subset-percentiles. The raw-rho test now checks the supported panel-level
inversion, not the unsupported assertion that no threshold could reproduce two series booleans.
No guard was changed to reinstate separation. Deterministic LF serialization avoids a Windows
newline-only diff; parsed scientific content is unchanged by that normalization.

Validation is pending in this draft commit. A local attempt could not start because the bundled
Python lacks pytest. The task-scoped remote workflow runs the four relevant control files and
then normal preflight against its exact commit, with actual exit codes and durable logs. A green
normal run is not FULL publication evidence. No old fetch is retried, no journal or preprint is
changed, and AUT-PD-170 is not marked complete before actual validation.
