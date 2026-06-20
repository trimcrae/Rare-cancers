# Mechanism-based drug-repurposing hypotheses for extraskeletal myxoid chondrosarcoma

**Status: DRAFT v0.2 — full prose, pre-clinician-review, not for submission.**
This is a *hypothesis-generating* paper (the genre of e.g. a "hypothesis" or
"perspective" article). It proposes existing drugs whose mechanisms fit EMC biology
but that have not been tested in EMC. **It asserts no efficacy.** Authors: TBD (must
include a sarcoma clinician/researcher). Source of candidates:
`research/hypotheses/candidates.json`; method: `research/hypotheses/METHODOLOGY.md`.

## Abstract
Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare, *NR4A3* fusion-driven soft-tissue
sarcoma with an indolent-but-relentlessly-metastasising course and no established effective
systemic therapy; anti-angiogenic tyrosine-kinase inhibitors (TKIs) are its most consistently
active class, yet responses are partial and temporary. Because the disease is too rare for
large de-novo trials and its genome is recurrently "quiet" (no recurrent actionable mutations
on clinical sequencing), drug *repurposing* — deploying agents that already exist and carry
human safety data — is a rational strategy. We systematically map EMC's molecular and
microenvironmental vulnerabilities to existing drugs **not yet reported in EMC** using three
independent methods: (i) expert, literature-driven mechanism curation; (ii) a reproducible
target→drug enumeration against a public interaction database (DGIdb); and (iii) zero-shot
prediction from a graph foundation model (TxGNN). Each hypothesis is graded by an explicit
evidence tier (T0–T3) and a transparent six-criterion priority score, and is held behind a
strict firewall from patient-facing material. Curation and enumeration converge on a
prioritised menu of **14 candidates** spanning the angiogenic, *NR4A3*-transcriptional,
PPARγ/lineage, cell-cycle, epigenetic, apoptotic and immune axes — led by imatinib for the
small *KIT*-mutant subset (the one candidate with direct EMC clinical evidence) and an
extension of the validated VEGFR-TKI class. The graph foundation model, by contrast, diverged
sharply, illustrating a concrete limitation of knowledge-graph models on data-sparse rare
cancers. We present this as a feasibility-ranked set of testable hypotheses to focus
preclinical and n-of-1 investigation — explicitly **not** as evidence of efficacy.

## 1. Introduction

**The disease.** EMC is a rare soft-tissue sarcoma defined molecularly by rearrangement of
*NR4A3* (also called *NOR1*/*CHN*/*TEC*), most often as the *EWSR1::NR4A3* fusion and less
commonly *TAF15::NR4A3* and other variants. The fusion produces a chimeric transcription
factor that drives the tumour's transcriptional programme — including activation of target
genes via chromatin modification (Yoshimura et al. 2016) — making EMC a prototypical
fusion-addicted, "transcription-factor" cancer. Clinically it is paradoxical: typically
slow-growing and associated with prolonged survival, yet with a high cumulative rate of
local recurrence and distant (especially pulmonary) metastasis over years to decades
(Remiszewski et al. 2025). Even once metastatic the course can be protracted, and outcomes
vary widely by era and by completeness of surgery (Masunaga et al. 2025).

**The unmet need.** Surgery (± radiotherapy) controls localised disease, but there is **no
established effective systemic therapy** for advanced EMC. The most consistently active class
is the anti-angiogenic multikinase TKIs — pazopanib and sunitinib in particular — but
responses are usually partial and finite, and conventional cytotoxic chemotherapy has limited
activity (Remiszewski et al. 2025). Compounding this, clinical next-generation sequencing of
advanced EMC characteristically reveals **no recurrent, directly actionable driver mutations**
beyond the defining fusion; an imatinib-sensitive *KIT* mutation occurs in only a small minority
(Jennings et al. 2021; Warmke et al. 2023). EMC therefore sits in a difficult space: too rare
for adequately-powered de-novo trials, and without an obvious single druggable mutation to
anchor a targeted-therapy programme.

**The case for repurposing.** Re-deploying drugs that are already approved (or have human
safety data) is especially suited to this setting: it removes the largest cost and time
barriers of de-novo development, lets a candidate move quickly to a biomarker-matched n-of-1
or basket study, and is well-aligned with the economics of neglected diseases, where off-patent
agents lack a commercial sponsor to fund confirmatory trials. The challenge is to choose
*which* existing drugs to test, rationally and transparently, without overstating the
evidence. Here we address that choice for EMC by mapping its documented vulnerabilities to
existing drugs through three independent and complementary methods, grading every resulting
hypothesis by how speculative it is, and reporting where the methods agree and where they
do not.

## 2. Methods
Vulnerability axes, candidate inclusion/exclusion, the T0–T3 evidence-tier rubric,
and citation rules — per `hypotheses/METHODOLOGY.md`. State explicitly that any
claim tagged `needs-verification` in the catalog must be resolved to a primary
source before publication.

Candidate generation combined expert, literature-driven curation with a **systematic
target→drug enumeration** (`hypotheses/enumerate-drugs.mjs`): the EMC drug targets in
`targets.json` were queried against the DGIdb interaction database, approved drugs with
an inhibitor interaction were retained, and a gap analysis against the catalog and the
known-active EMC agents isolated genuinely unconsidered drugs (`target-drug-matrix.json`).
This independently reproduced the anti-angiogenic-TKI cluster and broadened it (e.g.
nintedanib, axitinib, vandetanib, tivozanib), mitigating single-rater coverage bias;
implausible hits (e.g. a PPI, a thrombopoietin agonist) were triaged out on mechanism.

As a third, independent line we ran the pretrained **TxGNN** graph foundation model
(Huang et al., Nat Med 2024) zero-shot on the EMC knowledge-graph node and ranked all
7,957 drugs (`hypotheses/txgnn-emc-findings.md`). Unlike curation and enumeration —
which converge on oncology leads — TxGNN diverged: its top predictions were
metabolic/lysosomal-storage-disease drugs, and EMC's most clinically-active agents
(pazopanib, sunitinib) and our biomarker-supported lead (imatinib) ranked in the bottom
quartile, a consequence of EMC's sparse graph neighbourhood driving zero-shot
similarity-transfer toward unrelated diseases. We report this divergence as a limitation
of knowledge-graph foundation models on ultra-rare cancers rather than acting on it; no
TxGNN prediction was promoted to a candidate.

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

*Citation status: all previously-unverified claims are now resolved — the mRNA-immunology
claims to primary references (LNP-immunogenicity review, Exp Mol Med 2023; KEYNOTE-942,
Weber et al. Lancet 2024), and the transcriptional rationale re-grounded in EMC-native
evidence (Yoshimura et al. 2016); the Ewing BET/CDK comparison is retained only as a
labelled analogy in the candidate's rationale, not as an evidence claim. `validate-research.mjs`
reports zero `needs-verification` claims.*

## 4. Prioritization & a path to testing

We prioritise by **evidence tier × feasibility**, where feasibility combines drug
availability (approved > investigational-with-safety-data), tolerability, and whether a
**selection biomarker** exists. This yields three practical tranches:

**Tranche 1 — biomarker-matched, near-term n-of-1.** *Imatinib* in the *KIT*-mutant subset
is the only candidate at T3 (direct EMC clinical evidence: a *KIT* exon-11–mutant patient with
3 years of disease stabilisation; Jennings et al. 2021). It is approved, well-characterised,
and biomarker-defined. The realistic route is **molecular pre-screening** (NGS for *KIT*
mutations) followed by an **expanded-access / n-of-1** trial in the ~5% who qualify — not
general use. This is the single most actionable lead and is flagged as eligible for the
patient-facing page pending clinician review.

**Tranche 2 — shelf-ready class extension.** The VEGFR-TKI extension (regorafenib,
cabozantinib, lenvatinib, and the enumeration-surfaced nintedanib, sorafenib, axitinib,
vandetanib, tivozanib) builds on EMC's *most validated* active class and needs no new
biomarker. These are candidates for **histology-inclusive basket trials** of anti-angiogenic
agents in sarcoma, or for prospective registry-embedded cohorts, with the caveat that they
likely share pazopanib's eventual resistance.

**Tranche 3 — preclinical-validation-first.** The PPARγ/lineage (zaltoprofen, pioglitazone),
cell-cycle (CDK4/6), epigenetic (HDAC, BET/CDK7-9), and apoptotic/proteostatic (venetoclax,
carfilzomib) candidates rest on *in-vivo* or patient-derived-model screen signals rather than
clinical data. Their natural next step is **confirmatory testing in the existing
patient-derived EMC models** (the two independent EMC model drug screens that anchor much of
this evidence), prioritising hits that recur across models and that pair logically with the
current anthracycline backbone, before any clinical consideration.

Across all tranches, the disease's rarity argues for **shared infrastructure**: centralised
molecular profiling, multi-institution basket/registry designs, and contributing real-world
off-label experiences to public registries such as **CURE ID** (FDA/NCATS) so that isolated
n-of-1 outcomes become collective evidence.

## 5. Limitations & ethics

These are **hypotheses, not recommendations, and no efficacy is claimed.** Several specific
limitations bound their strength. First, most candidates are supported by preclinical,
in-vitro, or model-screen data rather than EMC clinical evidence (only imatinib reaches T3),
and the dominant rationale is *lineage/fusion* biology because EMC's genome is recurrently
quiet — so target-level plausibility does not guarantee clinical activity. Second, candidate
*generation* began as single-rater curation; we mitigated the resulting coverage bias with a
reproducible target→drug enumeration, but the priority score remains an expert-elicited,
equally-weighted heuristic, not a calibrated probability. Third, the graph foundation model
(TxGNN) we used as an independent check **diverged** from the mechanism- and
enumeration-derived leads, ranking EMC's most clinically-active agents in the bottom quartile;
we interpret this as a limitation of knowledge-graph models on data-sparse rare cancers rather
than as evidence against those agents, but it is a reminder that no single method is
authoritative here. Fourth, biomarker-restricted candidates (notably imatinib) apply only to a
molecularly-defined minority and must not be generalised.

Ethically, the chief risk is **false hope**: a plausible-sounding mechanism can be mistaken by
a frightened patient for an available treatment. We address this structurally — a strict
firewall keeps T0–T2 hypotheses out of all patient-facing material, and only a candidate that
reaches real EMC clinical evidence (T3) may migrate, and then only after clinician review. Any
clinical step (expanded access, n-of-1, trial) requires sarcoma-specialist judgement and,
where applicable, formal ethics oversight and informed consent. Every clinical and biological
claim in the underlying catalogue is cited to a primary source; remaining textbook/analogy
claims were resolved to primary references prior to drafting.

## 6. Conclusion

For a cancer too rare to support large de-novo trials, a transparent, honestly-graded menu of
*existing-drug* hypotheses is a pragmatic way to focus scarce investigative effort. Triangulating
three independent methods, mechanism curation and reproducible target enumeration converge on a
prioritised set led by a biomarker-matched, clinically-supported lead (imatinib in *KIT*-mutant
disease) and an extension of EMC's validated anti-angiogenic class — while a graph foundation
model's divergence marks the current limits of automated repurposing for ultra-rare cancers.
We offer this catalogue not as a claim of efficacy but as an invitation: a feasibility-ranked
starting point for the preclinical validation, biomarker-matched n-of-1 studies, and shared
registry infrastructure that could realistically move EMC care forward.
