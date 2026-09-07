---
id: DOC-EMC-PHARMACOLOGY-IDENTITY-PROTOCOL-20260906
title: Original NCC pharmacology protocol display
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Display the unchanged frozen rules with supported repository metadata.
scope: Retrospective NCC screen chemical identity and descriptive consistency.
audience: [maintainers, autonomous research agents]
---

Display wrapper only: the original unwrapped bytes and freeze are in `original-2026-09-06/frozen-packet.zip`. The dated source amendment is separate; it does not change these rules.

# Retrospective NCC chemical-identity analysis: frozen rules

2026-09-06. This is retrospective: the reader has already inspected selected screen values including proteasome inhibitors, venetoclax and several duplicate-looking entries. It is not a preregistered blinded prediction or a novel clinical study.

Question: does the complete reported NCC-EMC1-C1 screen contain consistent low-viability observations for distinct proteasome-directed compounds and chemical families, or is apparent replication an artifact of multiple preparations of the same active moiety?

Inputs: retain all 221 CAS-level screen rows and all 24 reported IC50 entries without modifying measurements; source workbooks/extraction in sibling ncc-screen-source-2026-09-06. Unknown NCC assay concentration/duration/replicate definition and IC50 fitting prevent potency comparisons, uncertainty intervals and numerical cross-study comparison. Zurich bands are not used in this checkpoint.

Before calculation: semantically inspect every screen name and authoritative primary/regulatory pharmacology sources for proteasome membership; inspect ambiguous candidates, not just known hits. Annotate the complete roster as confirmed direct proteasome inhibitor, unresolved candidate, or not identified as proteasome-directed in this bounded review. The last label is not an exhaustive target taxonomy. Establish active moiety, chemical family and formulation/prodrug distinctions for proteasome entries and obvious repeated-name groups; leave unsupported relationships unresolved. CAS alone is not biological independence.

Descriptive rules: lower reported viability receives better rank; ties use midranks. The screen's lowest quartile (rank <= 221/4) is a retrospective descriptive threshold, not a biological activity cutoff. Primary denominator always remains 221 preparations. Do not replace the entire panel with a supposedly deduplicated denominator when unrelated identity groups have not been fully curated. For each confirmed proteasome active-moiety group report all preparation ranks and their worst (least favorable) rank. Report families separately. No averaging to hide discordance. Preserve separate prodrug preparations; optionally grouping them with a documented active metabolite is explicitly a sensitivity, not an assertion of equivalent assay exposure.

Stop rule: the bounded claim of chemical-family consistency is unsupported if any confirmed active-moiety group's worst preparation rank is outside the lowest quartile, if fewer than two source-supported distinct chemical families are represented, if unresolved proteasome-candidate membership could change completeness, or if removing either represented chemical family eliminates all remaining lowest-quartile support. Passing supports only observed within-screen consistency across the represented chemical families; it does not identify a causal target or EMC selectivity. With only one surviving family after removal, state that explicitly; do not call it independently replicated biology. Unknown exposure and target engagement continue to block mechanistic attribution regardless of this descriptive result.

Sensitivity: recompute preparation positions using mean+reported SD for all 221 entries; this is a deterministic stress test, not a confidence bound. Keep all values outside 0-100. Report the 24 IC50 values only as source-reported selected follow-up data, not independent validation or an unbiased second screen. List any members absent from that follow-up.

One reproducible local script and exact data/source locators will support independent arithmetic. No expression reanalysis, new compound recommendation, p-value enrichment test, author-dependent concordance, paid execution, commit or publication. Stop after this complete bounded checkpoint and report remaining scientific limits.
