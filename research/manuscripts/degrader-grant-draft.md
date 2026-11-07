# Grant #1 — draft (non-dilutive, method-rigor / rare-sarcoma)

> Rung C of [degrader-startup-plan-exo.md](./degrader-startup-plan-exo.md) §6.2. This is a **DRAFT**
> for adaptation to a specific funder; the outward **submit** is a human-gated, sign-off act (GOVERN
> eval Layer 2). Milestones map 1:1 onto the STRATEGY.md spend-gated rungs so each GO/NO-GO is a
> reportable deliverable. Language follows the program's discipline: nothing here asserts efficacy,
> safety, or clinical readiness; the deliverable is a **benchmarked computational prioritization
> capability** and **predicted paralogue-selective candidates**.
>
> `[VERIFY]` = fill/confirm from a cited primary source before submission. `[FUNDER-SPECIFIC]` = tailor
> to the chosen funder's format/limits. Do not submit with any placeholder unresolved.

---

## Cover / identifiers `[FUNDER-SPECIFIC]`

- **Title:** A benchmarked, reproducible in-silico pipeline for predicting NR4A-paralogue-selective
  degrader candidates for extraskeletal myxoid chondrosarcoma (EMC) and NR4A-driven cancers.
- **PI / organization:** `[FUNDER-SPECIFIC — solo investigator; independent research]`
- **Funder / program:** `[FUNDER-SPECIFIC — e.g. a rare-sarcoma foundation research grant, a
  methods-rigor grant, or an SBIR/STTR-eligible track; confirm solo/micro-entity eligibility]`
- **Amount requested:** `[FUNDER-SPECIFIC]` — see Budget; the compute ask is small (low-hundreds to
  ~$1.5k GPU spot for the full gated ladder) and the labor is founder-provided.

## 1. Summary / abstract

Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare sarcoma `[VERIFY incidence, cited]` driven in
most cases by an *EWSR1::NR4A3* fusion. NR4A3 is an orphan nuclear receptor long considered
difficult to drug. This project delivers a **rigorous, honest, reproducible in-silico pipeline** that
predicts whether **NR4A-paralogue-selective degrader candidates** are computationally credible — using
relative free-energy calculations, a ternary-cooperativity cycle benchmarked against public known-answer
systems, and a family-selectivity retrospective control — with every quantitative claim validated or
explicitly labelled conditional. The output is a **computationally prioritized, structure-defined
candidate matrix** and an open, benchmarked method, handed off to wet-lab collaborators for
experimental validation. No efficacy, safety, or clinical claim is made; degradation is reported as
directional concordance with known outcomes, not as demonstrated.

## 2. Significance `[VERIFY all clinical facts against cited primary sources]`

- EMC is ultra-rare with limited systemic options `[VERIFY, cited]`; a target-directed rationale is
  scientifically attractive but under-resourced precisely because the disease is small.
- The *EWSR1::NR4A3* fusion retains the NR4A3 ligand-binding domain, motivating a degradation strategy;
  degradation is **target-generic** (removes NR4A3 whether wild-type or fusion), which is why the program
  is framed around NR4A3, with fusion-exclusive routes tracked separately (see the program's route
  portfolio). Full biological rationale and citations: `[ref: nr4a3-degrader-paper.md + EMC biology
  evidence in the repo]`.
- Family selectivity across NR4A1/2/3 is the central hard problem. The existence of a reported
  family-selective NR4A1 degrader (NR-V04; degraded NR4A1, spared NR4A2/3) is event-level evidence that
  family-selective NR4A degradation is achievable `[VERIFY: Wang 2024, cited]` — it does **not** establish
  a transferable structural mechanism, which this project treats as an open question.

## 3. Innovation

- A **honestly-benchmarked** ternary-cooperativity selectivity pipeline: the general approach is
  cite-able prior art (all-atom alchemical cooperativity FEP), and the contribution is an open-source,
  OpenFE-based implementation with the accuracy of **our specific pipeline** validated against public
  known-answer systems — the distinction the field usually blurs.
- A **conditional-honesty** stance on cryptic-pocket affinities (reported as ΔG_bind|open, with the
  per-paralogue opening penalty treated explicitly) rather than an unconditional-affinity over-claim.
- A **spend-gated, preregistered** design: the cheapest experiment that could falsify the thesis runs
  first; expensive stages unlock only on a GO. The whole program can be falsified for ~$25.

## 4. Approach & milestones (mapped 1:1 to the spend-gated ladder)

Each milestone is a reportable deliverable with an explicit GO/NO-GO. Full detail: STRATEGY.md.

| # | Milestone (rung) | Deliverable | GO/NO-GO | Status |
|---|---|---|---|---|
| M0 | Infra shakeout + charge-model fix (step0) | Validated spot-safe RBFE pipeline on am1bcc | one edge finishes clean | **Done (GO)** |
| M1 | Reference-reproduction smoke (valA_mini) | Container reproduces a known public ΔΔG | within ~2 kcal/mol | **Done (GO; abs err 0.61)** |
| M2 | cmpd19 conditional RBFE pilot (step1_pilot) | Converged conditional relative FE on the real cryptic pocket | reproducible, receptor-sensitive, pocket stable | **Pilot crux cleared** |
| M3 | Known-answer ternary benchmark (valB_mini→full) | Pipeline recovers a measured ternary cooperativity | recovers known sign/magnitude | Ready to run on go |
| M4 | NR-V04 family-selectivity retrospective | Directional concordance with the known NR4A1-degraded / NR4A2·3-spared outcome | at least directionally concordant | Gated on M3 |
| M5 | Prospective candidate matrix | A computationally prioritized, structure-defined candidate matrix (24–36 primary → preregistered downselect) | staged gates + Pareto front | Gated on M3–M4 |
| M6 | Open method + reproducibility bundle + preprint | Public benchmarked pipeline + manuscript | red-team clean + sign-off | Write & ship |

**Honesty gates (binding):** the prospective matrix (M5) never runs unless the ternary benchmark (M3)
passes; degradation is reported as **surrogate-score concordance**, never demonstrated; the parent-warhead
pharmacology (including reported MYC induction) is disclosed as a liability, not benefit.

## 5. Deliverables

1. An **open, benchmarked** NR4A-selectivity in-silico pipeline (method + public benchmarks + reproduce path).
2. A **computationally prioritized, structure-defined and retrosynthetically annotated candidate matrix**
   of predicted NR4A-paralogue-selective degrader candidates (degradation experimentally unvalidated).
3. A **preprint + reproducibility bundle**, and a wet-lab-collaborator handoff package.
4. A public **decision-trace / benchmark record** (reproducibility + cost transparency).

## 6. Feasibility / investigator

- Solo investigator directing an **AI-agent + spot-GPU research pipeline** (checkpoint/resume,
  preregistered GO/NO-GO gates), with the program already through M0–M2 at **~$36 total realized GPU
  spend** `[VERIFY from the decision-trace log]`. Existence proof for solo agent-leveraged delivery is
  well established `[ref: plan §8]`.
- **No wet lab** is required for the computational deliverables; experimental validation is an explicit,
  honestly-stated handoff to a collaborator/foundation — not claimed within scope.

## 7. Budget (compute-as-COGS)

- GPU spot compute for the full gated ladder: **~$0.8–1.5k** *only if every gate says GO* (per-rung
  anchors in STRATEGY.md; realized to date ~$36). `[FUNDER-SPECIFIC: add any allowed stipend/publication
  costs.]`
- Labor: founder-provided (flat-rate agent tooling ≈ $0 marginal). This is an unusually capital-efficient
  ask for a target-directed program.

## 8. Rigor, reproducibility, data & integrity

- Every quantitative result is either **benchmarked** against a public known-answer or **explicitly
  labelled conditional**; precision diagnostics are not presented as accuracy.
- All code, containers, gates, and the public decision-trace record are shared for reproduction.
- Medical-integrity: every clinical fact and citation is real and cited; no synthetic data is presented
  as real. No efficacy, safety, therapeutic-window, or clinical-readiness claim is made.

## 9. Broader impact

A reusable, honestly-benchmarked family-selectivity pipeline transfers beyond EMC to other NR4A-driven
and paralogue-selectivity degrader problems, lowering the cost of an honest computational go/no-go for
neglected targets — the mission of the program (MTP: *make rigorous, honest in-silico drug-target
evaluation abundant for neglected diseases*).

---

*Pre-submission gate: run `node scripts/govern-overclaim-lint.mjs research/manuscripts/degrader-grant-draft.md`
(0 ERROR) and complete the GOVERN eval Layer-2 checklist before submitting. Resolve every `[VERIFY]` /
`[FUNDER-SPECIFIC]` placeholder first.*
