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

## 7. Benchmarking against public repurposing methods

This section exists so we are honest about *what kind of method this is* and where
it sits relative to the public state of the art. (Prompted by the Freakonomics Radio
episode on drug repurposing featuring David Fajgenbaum / Every Cure, Chris Snyder,
the FDA's CURE ID, and the Market Shaping Accelerator. We could not access the audio
in this environment; this is written from the published record on those initiatives.)

### 7.1 What our method is

A **single-rater, mechanism-first, literature-curated** pipeline: a human surveys EMC
biology, hand-matches drugs to vulnerabilities, and grades each with a transparent
additive rubric behind a citation/evidence-tier firewall. Its real strengths are
**transparency, auditability, citation integrity, biomarker-awareness, and explicit
speculation grading** — properties that large automated platforms often *lack*. We
keep these.

### 7.2 Honest limitations

- **Coverage bias (the big one).** It only surfaces drugs the curator thought to look
  for. There is no guarantee the full ~3,000 approved drugs have been screened against
  EMC's biology. This is a *discovery* gap, not a *curation* gap.
- **Expert-elicited scoring, not validated.** The six 0–3 axes are equally weighted,
  additive, uncalibrated, and carry no uncertainty. The composite looks more rigorous
  than it is; §3 already labels it a heuristic, not a probability.
- **Single rater.** No inter-rater reliability; bounded by one person's knowledge and
  recall, and by a fixed knowledge cutoff.
- **No computational substrate.** No knowledge graph, no transcriptomic
  signature-matching, no ML ranking — the things that make modern repurposing *systematic*.

### 7.3 Public state of the art we benchmark against (and could leverage)

The unifying idea we lack is **"score every drug against every disease"** rather than
"score the drugs I suspected."

| Approach | What it adds over us | How we'd use it under a zero-build, egress-limited constraint |
|---|---|---|
| **Every Cure / "MATRIX"** (Fajgenbaum et al.; ARPA-H–backed) | Systematic drug×disease scoring via a biomedical knowledge graph + ML link-prediction | Adopt the *philosophy* (score everything); link out so patients/clinicians can act |
| **TxGNN** (Huang, Zitnik et al., *Nat Med* 2024) | Graph **foundation model built for rare diseases with little data**; zero-shot, **explainable** | Best fit for EMC. Run "TxGNN Explorer" offline; import ranked, explained hits as cited data |
| **Hetionet / Rephetio** (Himmelstein et al., *eLife* 2017) | Open, reproducible knowledge-graph repurposing scores | Cross-check our shortlist against an independent graph method |
| **Connectivity Map / LINCS L1000** (Subramanian et al., *Cell* 2017) | "Signature reversal" — drugs that reverse EMC's NR4A3 expression signature | Offline CMap query against an EMC/NR4A3 signature; import results |
| **Open Targets, DGIdb, DrugBank/ChEMBL** | Systematic, reproducible drug↔target enumeration | A CI step (like our literature fetch) to enumerate *all* approved drugs hitting EMC targets |
| **CURE ID** (FDA/NCATS) | Crowd-sourced **real-world** off-label case reports | Mine it for EMC cases *and* contribute ours (e.g. the imatinib/KIT-mutant case) |

### 7.4 Why this is under-resourced (the economics, and what it means for us)

The episode's economics thread (Snyder; Kremer & Glennerster, *Strong Medicine*; the
Market Shaping Accelerator) explains *why* repurposing is neglected: a repurposed,
off-patent drug has **no profit incentive** to fund the confirmatory trials, so good
hypotheses die unfunded. We cannot fix incentives. But this is the clearest argument
for the *value* of a **free, transparent, public** evidence hub like this one: it
**lowers the information cost** of finding and vetting candidates, which is exactly the
market failure. It also argues for plugging into the public ecosystem (CURE ID, Every
Cure) rather than being a silo.

### 7.5 What we keep vs adopt

- **Keep:** the citation firewall, evidence tiers, the graduation rule, and honest
  speculation grading. These are our comparative advantage and are not what the big
  platforms optimise for.
- **Adopt (roadmap, in priority order):** (1) **systematic target→drug enumeration**
  via public APIs in CI to kill coverage bias — **implemented**: `targets.json`
  (EMC targets) → `enumerate-drugs.mjs` (DGIdb query + gap analysis vs the catalog)
  → `.github/workflows/enumerate-drugs.yml` → `target-drug-matrix.json`; its
  `gapAnalysis.newlySurfaced` lists approved drugs hitting EMC targets that we have
  *not* yet catalogued, to triage under §1–§4; (2) CURE ID integration — **partly
  done**: an outbound action path to the FDA/NCATS CURE ID registry is now on the
  patient page (`clinicalTrials.finders`) so clinicians/patients can *browse and
  report* real-world off-label drug use; programmatic *mining* is deferred (CURE ID
  exposes no documented public API). Our imatinib/KIT-mutant case is exactly the kind
  of real-world signal worth contributing there; (3) a graph-ML screen with **TxGNN**
  (Huang et al., Nat Med 2024) — **done**: we ran the *real* pretrained model zero-shot
  on the EMC node and ranked all 7,957 drugs (`txgnn_predict.py` + `txgnn-run.yml`;
  output `txgnn-emc-predictions.json`; write-up `txgnn-emc-findings.md`). Result: TxGNN
  **diverges from** mechanism curation and enumeration for EMC — its top picks are
  metabolic/lysosomal-disease drugs, while EMC's most clinically-active agents
  (pazopanib #6422, sunitinib #6382 of 7,957) and our T3 lead (imatinib #5951) rank in
  the bottom quartile. EMC's sparse KG neighbourhood makes zero-shot similarity-transfer
  pull toward unrelated diseases. A genuine, citable limitation finding for the
  Methods/Limitations, not promoted to any candidate (firewall §5); (4) iterate
  the scoring rubric (document provenance; consider weighting/uncertainty) once there
  is a systematic candidate set to calibrate against.

> A target→drug link is a **triage starting point, not an efficacy claim**. A
> newly-surfaced drug still must pass §1–§4 (mapped EMC vulnerability, cited
> evidence, evidence tier, score) and the §5 firewall before it means anything.

### Further reading (external — not part of the local cited corpus)

- Fajgenbaum DC. *Chasing My Cure* (2019); Every Cure (everycure.org); ARPA-H "MATRIX".
- Huang K, et al. *A foundation model for clinician-centered drug repurposing.* Nat Med 2024 (TxGNN).
- Himmelstein DS, et al. *Systematic integration of biomedical knowledge prioritizes drugs for repurposing.* eLife 2017 (Hetionet/Rephetio).
- Subramanian A, et al. *A Next Generation Connectivity Map: L1000 Platform.* Cell 2017 (CMap/LINCS).
- Open Targets Platform; DGIdb; DrugBank; ChEMBL.
- Kremer M, Glennerster R. *Strong Medicine* (2004); Market Shaping Accelerator (Univ. of Chicago).
- CURE ID — FDA / NCATS public registry of real-world off-label use.
