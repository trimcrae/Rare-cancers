---
id: DOC-RECRUITING-TREATMENT-READER-PROTOCOL-20260906
title: Independent therapeutic EMC source reading protocol
kind: prereg
status: immutable
purpose: Apply one evidence-backed therapeutic disease-scope rule to every supplied complete source record.
scope: Eight supplied archived registry records and explicit disease anchors only.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-09-06
last_verified: 2026-09-06
---

Read all eight full record JSONs in manifest order, including all eligibility, brief/detailed
descriptions, conditions, design, interventions and arm/cohort text; no truncated excerpts as a
substitute. Use only this protocol, disease-anchors.md, manifest.json and records. Do not inspect
other repository files, retrieval strategies, rankings, group maps, other readers or prior labels.
No registry refresh or external protocol retrieval is commissioned. Cite supplied source pointers.

Question: Does the complete archived record support at least one therapeutic cohort whose disease
and required molecular scope is compatible with extraskeletal myxoid chondrosarcoma (EMC)? This
is a disease-level lead conditional on ordinary remaining patient requirements, not an eligibility
verdict for an invented patient. A therapeutic route and EMC compatibility must refer to the same
cohort: an observational EMC cohort cannot borrow another cohort's treatment. Record-wide TREATMENT
alone does not establish this connection.

Use positive [1,1], negative [0,0], or unresolved [0,1]:

- Positive: a specifically linked therapeutic cohort admits explicit EMC, an anchored defining
  fusion, a supported fusion class, or a clearly encompassing broad soft-tissue sarcoma/solid-tumor
  population. Open-ended examples are not closed histology lists. No unresolved extra molecular
  requirement or scope-changing contradiction may remain. Explicit diagnosis takes precedence
  over defining fusion, fusion class and broad tumor as the descriptive route category.
- Negative: every plausible therapeutic route demonstrably excludes EMC or its supported molecular
  route, uses a closed positive disease list that excludes EMC, or the source demonstrates that no
  EMC-compatible therapeutic cohort exists. An exclusively observational EMC route is not positive.
  Quote affirmative evidence for absence; missing EMC wording alone never proves exclusion.
- Unresolved: disease or therapeutic cohort linkage is unclear, source text contradicts itself,
  mutation versus fusion acceptance is ambiguous, a required extra biomarker is not established
  for EMC by the anchors, or missing external criteria could change scope. Do not assume a broad
  gene mention implies an eligible alteration. Check all other cohorts before record aggregation.

Preserve ordinary age, stage, prior treatment, performance, organ function and geography restrictions
as requirements, without assuming anyone meets them. Additional tumor biomarker requirements remain
unestablished unless the supplied disease anchor actually supports the requirement. A disease-defining
fusion route can describe a molecular subtype of EMC; do not generalize that subtype to all EMC.

Cohort availability is a mandatory component. If the only EMC-compatible therapeutic cohorts
are explicitly unconditionally closed or held, the primary label is negative [0,0]; separately
preserve secondary_disease_scope_compatible=true and exact closure evidence. Conditional hold
language remains conditional: if its applicability to the EMC-compatible cohort is ambiguous
or contradictory, label unresolved [0,1]. A different compatible therapeutic cohort may support
a positive only after its own restrictions are checked. Unknown cohort/site availability alone
does not defeat a source-supported compatible lead; explicitly label availability unknown and
never imply open places. Record-level RECRUITING never overrides cohort closure or hold.

For each case save: case_id, nct_id, source_raw_sha256, label, bounds, route_category (explicit_EMC /
defining_fusion / fusion_class / broad_tumor / no_compatible_therapeutic_route / unresolved),
cohorts_checked (each cohort identifier plus therapeutic purpose, disease/molecular compatibility,
extra biomarkers, exclusions and availability), same_cohort_rationale, ordinary_requirements,
external_criteria_gap, contradictions, cohort_availability, secondary_disease_scope_compatible, rationale and evidence. Every evidence
item must include file, RFC6901 JSON pointer, exact verbatim excerpt and what it supports; cite
anchor ID when using a disease assertion. Evidence must support both therapy and disease in the
same cohort for positives, all plausible route exclusions for negatives, or the exact uncertainty.

First write complete independent-labels.json and source-evidence.json for all eight cases. Freeze
with timestamp, reader/model/effort as actually known, input hashes and output SHA256 hashes before
comparison with any other judgments. Missing source content or unreadable files stop that reading
and must be reported, never silently labeled negative or unresolved. No minimum positive or negative
count is required. No computational judgment establishes clinical efficacy, safety or eligibility.
