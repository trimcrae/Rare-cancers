---
id: DOC-RECRUITING-TREATMENT-PROTOCOL-20260906
title: Frozen recruiting treatment retrieval difference protocol
kind: prereg
status: immutable
purpose: Prespecify a finite source adjudication of therapeutic EMC-compatible retrieval leads before new relevance judgments.
scope: Eight-record census in the frozen recruiting treatment structural population; no clinical eligibility or efficacy inference.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-09-06
last_verified: 2026-09-06
---

# Prospective endpoint and fixed selection

This standalone post-ranking protocol freezes a new experiment before new relevance judgments.
It does not change or pass earlier protocols. Archive SHA256 is
85c2083921ad6050c48da1f54fbe7849104ed7d1f90da6ecf85d477e7140ba5b;
archive-manifest SHA256 is 40145d75f2b5f6060525df0c5d4687bc8be018b4273bc52176d0edac30d5965c.
The code, inputs, selected versions, and complete source records are hashed in the coordinator
manifest. Base revision is 0430a9b689d373c6b0c515c0aa0aac789b76ce5c.

The population is the frozen 6,182-record query union. Select the archived version by greatest
lastUpdatePostDateStruct.date, then greatest retrieved_at_utc; break remaining ties by smallest
source page path then canonical study SHA256, exactly as archived baseline.py. Reconcile all
6,182 versions against version-audit.json before selection. Apply both full-path conditions:
protocolSection.statusModule.overallStatus == RECRUITING and
protocolSection.designModule.designInfo.primaryPurpose == TREATMENT.
Missing or other values are outside this population, never negative disease judgments.
The reproduced population has 737 records, all INTERVENTIONAL.

Use frozen scores without recomputation, query changes, refresh, or tuning. In archived baseline.py,
O is the maximum expression score across frozen EMC synonyms; H = O + 0.25*BM25(sarcoma);
A = H + 0.5*maximum molecular expression score. Fields include brief/official titles,
conditions/keywords, brief/detailed descriptions, eligibilityCriteria, and intervention
name/otherNames/description. NFKC lowercase alphanumeric tokenization is used. Expression score
is mean BM25 over distinct expression tokens plus one for exact phrase matching. Ordinary
single-part expressions may score lexically without full phrase matching; molecular expressions
require every AND-separated phrase within a source field. BM25 uses the whole frozen corpus,
k1=1.2 and b=0.75. Therefore O is a diagnosis-synonym retrieval score, not literal exact matching.
The coordinator manifest preserves the exact frozen synonyms and molecular terms. Broad molecular
terms are candidate generators, never eligibility evidence.

Within the structural population sort by descending stored score then ascending NCT ID. Select
up to 100 strictly positive scores per method. O has 77 positives: no zero padding. H and A
have 100 selected each; all 77 O records are common, plus 19 other common records. H-only and
A-only each have four records. Neither H/A cutoff crosses a score tie; preserve cutoff score,
tie extent, successor and positive population in the manifest. Reproduce original whole-corpus
rank/tie metadata independently of this new filtered order. No original rank is a filtered rank.

The primary comparator is ordinary-plus-parent-histology H, not the best achievable clinician
search. Commission the full eight-record H/A symmetric difference only. The 27-record union
beyond O is uncommissioned and cannot be used to claim O comparison yield.

# Judgment, masking and uncertainty

Provide each of two fresh independent readers only reader/protocol.md, reader/disease-anchors.md,
reader/manifest.json and the eight complete reader/records JSON files. The reader protocol below
is the sole operational labeling rubric. Readers must not receive this coordinator selection
protocol, scores, groups, query provenance, other judgments or historical task instructions.
Shuffle by SHA256 of the fixed seed plus newline plus NCT ID; the coordinator manifest records
seed and membership. This is model-session masking, not a claim of human review or perfect blinding.
The preparer verifies metadata and source identities only and does not judge eligibility.

The same strategy-independent label applies to a source version regardless of retrieval method.
Positive [1,1] means source-supported therapeutic EMC-compatible disease scope in at least one
and the same cohort, with no unresolved scope-changing disease/molecular restriction. Negative
[0,0] requires demonstrated absence of such a route after all plausible cohorts are checked.
Unresolved [0,1] preserves contradictory text, missing scope-changing external criteria, uncertain
molecular acceptance or an additional required biomarker unestablished by the supplied anchors.
Explicit closure or unconditional hold of all otherwise compatible therapeutic cohorts makes the
primary label negative, retaining secondary disease-scope compatibility. Ambiguous closure
applicability is unresolved; unknown availability alone is preserved without assuming open places.
Missing or incomplete readings stop the analysis; they are not automatically unresolved labels.

Each reader freezes all eight evidence-backed judgments, source pointers/excerpts and packet
hashes before comparison. Coordinator verifies exact excerpts and completeness, then reconciles
disagreements while preserving both original readers. Unresolved source uncertainty is retained;
agreement does not manufacture evidence. Amendments are dated append-only and must precede any
changed-rule reading. Readers are not launched during this preparation checkpoint.

# Signed finite result and stop rule

Let E=A\H and D=H\A. Delta = sum(y_i for E) - sum(y_i for D), measured in additional
source-supported therapeutic disease-scope leads at review capacity 100. The 96 common record
contributions cancel; absolute top-100 yields, precision, recall, or availability cannot be estimated
from these eight records. For intervals [l_i,u_i], lower = sum_E(l)-sum_D(u), upper =
sum_E(u)-sum_D(l). Initially [-4,+4]. If unresolved labels remain, report the interval and both
reader estimates; never impute their midpoint as a result. These are deterministic uncertainty
bounds for a finite census, not sampling confidence intervals or inferential significance tests.

Report negative, zero and inconclusive results equally. Useful positive increment is established
only when the final conservative lower bound exceeds zero; then consider separately authorized
validation. If lower <= 0, stop this augmentation experiment without changing weights, capacity,
filters, labels or expanding the sample to rescue the result. A positive increment does not clear
submission. No manuscript, 27-record extension, outreach, paid access or publication is authorized.
Snapshot recruiting is not proof of current cohort/site availability, patient eligibility,
therapeutic window, safety, efficacy, or clinician time saved. No patient is invented.
