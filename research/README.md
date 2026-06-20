# EMC research program

The mission of this project is not a web page — it is to **improve outcomes for
people with extraskeletal myxoid chondrosarcoma (EMC)**. That runs on three rails:

1. **Patient education** — the public hub (`/cancers/emc/`), already live.
2. **Hypothesis generation** — find *existing* drugs whose mechanisms plausibly fit
   EMC's biology but have **not been tried** in EMC, as testable, cited hypotheses.
3. **Dissemination** — two manuscripts toward a preprint / journal submission:
   - a **systematic review & meta-analysis** of EMC outcomes (built on the pooled,
     cited registry), and
   - a **drug-repurposing hypothesis** paper.

```
research/
  README.md                         this file
  PROTOCOL.md                       systematic-review / meta-analysis protocol (PRISMA-style)
  hypotheses/
    METHODOLOGY.md                  how candidates are generated, graded, and cited
    candidates.json                 structured repurposing-candidate catalog (data)
  manuscripts/
    meta-analysis.md                manuscript skeleton (outcomes meta-analysis)
    repurposing-hypotheses.md       manuscript skeleton (repurposing hypotheses)
```

## Non-negotiable rules

- **Firewall.** Nothing in `research/` is served on the patient site, and no
  hypothesis (Tier T0–T2, see hypotheses/METHODOLOGY.md) may appear on the
  patient-facing page. Only a candidate that reaches **real EMC clinical evidence
  (T3)** can migrate to `emergingTreatments`, and only after clinician review.
- **Hypotheses are hypotheses.** Every mechanistic claim is cited or explicitly
  flagged `needs-verification`. Nothing here is medical advice, a recommendation,
  or a statement that any drug works in EMC. It does not.
- **Human-in-the-loop publishing.** Claude drafts, structures, and cites. A named
  human author (ideally with a sarcoma clinician/researcher) reviews and is the one
  who submits. No automated posting to a preprint server or journal.
- **No fabrication** (inherits the repo's medical-integrity rule and
  `METHODOLOGY.md`): no invented citations, mechanisms, or results.

## Status

- Meta-analysis: pooled dataset built; protocol drafted; **random-effects engine
  implemented** (`research/meta/meta-analysis.mjs` → DL pooling + I²/τ², forest
  plots, PRISMA flow, leave-one-out / era / registry-vs-all sensitivity); manuscript
  results populated. **Still needs** formal risk-of-bias scoring, a GLMM/Freeman–Tukey
  cross-check, and clinician review before submission.
- Repurposing: methodology + grading rubric drafted; catalog seeded with 3 graded
  candidates. **Needs** targeted literature verification of `needs-verification`
  claims and clinician review.
