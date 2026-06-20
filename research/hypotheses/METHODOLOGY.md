# Drug-repurposing hypothesis methodology

How candidate drugs are generated, graded, cited, and (rarely) graduated. The goal
is **testable, honestly-graded hypotheses** for EMC — existing drugs whose
mechanisms fit EMC biology but that have not been tried in EMC — not claims of
efficacy. Read with `research/README.md` (firewall + integrity rules).

## 1. Candidate generation — EMC vulnerability axes

Candidates must map to a documented feature of EMC biology, e.g.:

- **Fusion-driven transcription.** EMC is defined by NR4A3 rearrangements (commonly
  EWSR1::NR4A3), producing a chimeric transcription factor with aberrant activity —
  a potential transcriptional "addiction" shared with other EWSR1-fusion sarcomas.
- **Angiogenesis dependence.** The most consistently active systemic class in EMC is
  anti-angiogenic TKIs (pazopanib, sunitinib, anlotinib); pazopanib sensitivity has
  been linked to upregulated VEGF/Notch signalling.
- **Cold immune microenvironment.** EMC is immunologically quiet; checkpoint
  inhibitors have not shown systematic activity.
- **Other leads.** Upregulated targets reported in EMC (e.g. CHI3L1/YKL-40,
  neuroendocrine markers) as exploratory axes.

Each axis claim must be cited (or flagged `needs-verification`).

## 2. Inclusion / exclusion

- **Include:** drugs that already exist (approved anywhere, or investigational with
  human safety data) whose mechanism plausibly engages an EMC vulnerability **and
  that have not been reported in EMC** (`notTriedInEmc: true`).
- **Exclude:** current EMC standard/known-active agents (they belong in the patient
  page's `treatments`/`emergingTreatments`, not here); pure de-novo molecules with
  no existing drug; anything requiring fabricated mechanism.

## 3. Evidence tiers (how speculative)

| Tier | Meaning |
|------|---------|
| **T0-mechanistic** | Mechanistic rationale only; no EMC or close-analog data. |
| **T1-preclinical-or-analog** | Preclinical/in-vitro signal, or strong analogy in a related fusion-driven sarcoma. |
| **T2-emc-case-signal** | Case report(s) / small signal in EMC or very close relatives. |
| **T3-emc-clinical-evidence** | Prospective or substantial clinical evidence in EMC. |

Also record `speculationLevel` (low / moderate / high) as a plain-language summary.

### Breadth before narrowing

Candidate generation must be **systematic and wide** — survey every documented EMC
vulnerability and the full field of existing drugs/mechanisms that engage them
(across angiogenesis, the NR4A3 fusion/transcription, nuclear-receptor/PPARγ,
epigenetic, kinase, and immune axes), *including* unbiased EMC drug-screen hits —
before shortlisting. Do not jump to a favoured few.

### Prioritization scoring

Each candidate is scored **0–3** on six criteria; the composite `priorityScore`
is their sum (max 18). It is a transparent prioritization **heuristic, not a
probability of success**, and is recomputed by `build-candidates.mjs`.

| Criterion | 0 → 3 |
|---|---|
| `emcEvidence` | mechanism-only → EMC clinical evidence |
| `mechanisticFit` | indirect → engages a validated EMC driver |
| `availability` | preclinical-only → investigational (human safety) → approved |
| `safety` | narrow window → well-tolerated |
| `biomarker` | none → a selection biomarker exists |
| `novelty` | already tried → fully untried in EMC |

Flag `subsetRestricted` (applies only to a biomarker-defined minority) and
`weakRationale` (kept for completeness despite a thin mechanistic basis) so the
score is read in context.

## 4. Citation rules

Inherits `METHODOLOGY.md` §1. Every `claim` carries either a `sourceId` resolving
to the local `citations` map (≥1 resolvable id) or `sourceStatus: "needs-verification"`
if it is general/textbook knowledge not yet pinned to a fetched source. A candidate
may be **catalogued** with unverified claims, but they are tracked and must be
resolved (or removed) before that candidate appears in any manuscript.

## 5. The graduation rule (firewall to the patient page)

A candidate may move to the patient-facing `emergingTreatments` **only** when it
reaches **T3 (real EMC clinical evidence)** *and* is reviewed by a clinician.
T0–T2 candidates stay in `research/` and never appear as patient-facing options.
This is the bright line that keeps hypotheses from being mistaken for treatments.

## 6. What a good candidate entry contains

`drug`, `drugClass`, `regulatoryStatus`, `mechanism`, `emcVulnerability` (cited),
`supportingEvidence[]` (each cited or flagged, tagged EMC vs analog vs general),
`rationale`, `evidenceTier`, `speculationLevel`, `keyRisks`, `openQuestions`,
`notTriedInEmc`. Validated by `scripts/validate-research.mjs`.
