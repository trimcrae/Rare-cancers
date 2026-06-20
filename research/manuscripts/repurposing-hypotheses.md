# Mechanism-based drug-repurposing hypotheses for extraskeletal myxoid chondrosarcoma

**Status: DRAFT skeleton v0.1 — pre-clinician-review, not for submission.**
This is a *hypothesis-generating* paper (the genre of e.g. a "hypothesis" or
"perspective" article). It proposes existing drugs whose mechanisms fit EMC biology
but that have not been tested in EMC. **It asserts no efficacy.** Authors: TBD (must
include a sarcoma clinician/researcher). Source of candidates:
`research/hypotheses/candidates.json`; method: `research/hypotheses/METHODOLOGY.md`.

## Abstract — *to finalize*
EMC is an ultra-rare, NR4A3 fusion-driven sarcoma with few active systemic options
(anti-angiogenic TKIs being the most consistent). We systematically map EMC's
molecular and microenvironmental vulnerabilities to **already-existing drugs not yet
tried in EMC**, grading each hypothesis by evidence tier, to prioritize feasible
investigation in a disease too rare for large de-novo trials.

## 1. Introduction — *to write*
EMC biology (EWSR1/TAF15::NR4A3 chimeric transcription factor; angiogenesis
dependence; cold immune microenvironment); the unmet need; the case for repurposing
in ultra-rare cancers (existing safety data, faster path).

## 2. Methods
Vulnerability axes, candidate inclusion/exclusion, the T0–T3 evidence-tier rubric,
and citation rules — per `hypotheses/METHODOLOGY.md`. State explicitly that any
claim tagged `needs-verification` in the catalog must be resolved to a primary
source before publication.

## 3. Candidates (from the scored catalog)
We surveyed EMC's documented vulnerabilities across seven axes (angiogenesis; the
NR4A3 fusion / transcription; PPARγ / nuclear-receptor; epigenetic; cell-cycle;
apoptosis/proteostasis; immune) and scored **14 existing-drug candidates** 0–3 on
six criteria (EMC evidence, mechanistic fit, availability, safety, biomarker,
novelty; composite max 18). Two independent **patient-derived EMC model drug
screens** anchor much of the preclinical evidence. Full per-criterion data:
`research/hypotheses/candidates.json`. Ranked:

| # | Candidate | Tier | Score | Basis |
|---|---|---|---|---|
| 1 | Imatinib (KIT-mutant subset) | **T3** | 15* | KIT-mutant EMC patient: 3-year stable disease on imatinib |
| 2 | Zaltoprofen (PPARγ-inducing NSAID) | T1 | 14 | Inhibits EMC growth *in vivo* via PPARγ |
| 2 | VEGFR-TKI extension (rego/cabo/lenva) | T1 | 14 | Extends EMC's most active class |
| 4 | Pioglitazone (PPARγ agonist) | T1 | 13 | Direct PPARγ agonism |
| 4 | CDK4/6 inhibitors (palbociclib) | T1 | 13 | CDK4 100% IHC + CDKN2A/2B loss |
| 6 | HDAC inhibitors (romidepsin/panobinostat) | T1 | 11 | Cell-line drug-screen hits |
| 6 | NTRK inhibitors | T0 | 11† | Expression, not fusion (weak) |
| 6 | Venetoclax (BCL-2) | T1 | 11 | Validated in 2 EMC ex vivo models |
| 9 | Brigatinib | T1 | 10 | Cell-line screen hit; mechanism unknown |
| 9 | Carfilzomib (proteasome) | T1 | 10 | Validated in 2 EMC ex vivo models |
| 9 | Anthracycline + venetoclax/carfilzomib | T1 | 10 | Screen-validated synergy on a current backbone |
| 12 | NR4A3/NOR1 direct modulation | T1 | 9 | Drug the fusion's receptor (PGA2 binds NOR1 LBD) |
| 12 | BET / CDK7-9 inhibitors | T1 | 9 | Fusion transcriptional addiction (Ewing analogy) |
| 14 | mRNA vaccine + checkpoint inhibitor | T0 | 8 | Inflame the cold microenvironment |

\*subset-restricted (biomarker-defined minority). †weak mechanistic rationale,
retained for completeness.

**Framing — the quiet genome.** Clinical NGS of metastatic EMC found *no recurrent
actionable mutations* (the KIT case is a ~5% exception), so the strategy is to
target the fusion / lineage biology and to mine unbiased patient-derived-model
screens — which is why approved drugs hitting PPARγ, cell-cycle, epigenetic and
apoptotic nodes, plus the validated VEGFR-TKI class, dominate the top of the list.

*Remaining `needs-verification` claims (mRNA immunology; Ewing BET/CDK analogy) to be
resolved before submission.*

## 4. Prioritization & a path to testing — *to write*
Rank by tier × feasibility (drug availability, known safety, biomarker). Discuss
realistic routes for an ultra-rare cancer: n-of-1 / expanded access, basket trials,
preclinical EMC models, registry-embedded studies.

## 5. Limitations & ethics — *to write*
Hypotheses only; no efficacy claimed; risk of false hope; the firewall from the
patient page; the requirement for clinician and (where relevant) ethics oversight
before any clinical step.

## 6. Conclusion — *to write*
A prioritized, honestly-graded menu of repurposing hypotheses to accelerate
investigation in EMC.
