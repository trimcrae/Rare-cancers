# research/manuscripts/ — what's here, and what's active

This folder holds the treatment-track writing plus a few supporting and separate-track
documents. To avoid the "which of these is *the paper*?" confusion, the rule is:

> **There is exactly ONE active manuscript:
> [`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md).**
> Everything else in this folder **feeds it**, **records QA for it**, or is **parked /
> separate-track**. Every file carries a one-line role banner at its top saying which.

---

## ▶ Active manuscript (the repo's #1 deliverable)

- **[`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md)** — *"A prioritized, falsifiable
  roadmap to a treatment for EWSR1::NR4A3 EMC — a computation-only triage."* The single paper
  currently being developed for preprint/submission. It is a **living document** (changelog at
  its top). If you came here to work on "the manuscript," this is it.

## Strategy / source of truth (internal — not a manuscript)

- **[`emc-treatment-strategy.md`](./emc-treatment-strategy.md)** — the capstone that ranks every
  treatment route into the prioritized portfolio. This is the **decision record**; the active
  manuscript above is its publishable expression. Paired with the live route board in
  [`../IDEAS.md`](../IDEAS.md). `CLAUDE.md` points here as the repo's crux — **read it before
  resuming treatment-research work** so settled decisions aren't re-litigated.

## Source memos — internal route deep-dives that feed the roadmap

Per-route decision memos behind the portfolio. Cited by the strategy/roadmap; not separately
submitted.

- [`immunotherapy-options-emc.md`](./immunotherapy-options-emc.md) — TCR-T / ICI / ImmTAC (Phase 1)
- [`emerging-modalities-scan-emc.md`](./emerging-modalities-scan-emc.md) — trabectedin, FAP-RLT, PPARG (Phase 2)
- [`car-t-strategies-emc.md`](./car-t-strategies-emc.md) — CAR-T surface-target strategies (Phase 3)
- [`degrader-vs-synthetic-lethal.md`](./degrader-vs-synthetic-lethal.md) — degrader vs. BRD9 head-to-head

## Earlier treatment-track drafts — subsumed by the roadmap

Real, cited drafts from before the portfolio was unified. The roadmap **sits on top of** these
(it explicitly draws on the repurposing and novel-modalities work). Kept for reference and as
possible focused follow-on papers (e.g. a degrader result paper). **Not the active push** — don't
develop them as standalone submissions without a deliberate decision to do so.

- [`repurposing-hypotheses.md`](./repurposing-hypotheses.md) — mechanism-based repurposing catalog
- [`novel-modalities.md`](./novel-modalities.md) — structure-based target assessment + neoantigen pipeline
- [`clinical-brief-emc-neoantigen.md`](./clinical-brief-emc-neoantigen.md) — one-page clinician brief derived from novel-modalities

## Parked

- [`hla-coverage-emc.md`](./hla-coverage-emc.md) — fusion-neoantigen HLA-coverage analysis. **Parked**
  (self-adjacent junction in a cold tumour = weak immunogen; economics favour a platform we don't
  control). Reusable only as HLA input to TCR-T/ADC eligibility — see [`../IDEAS.md`](../IDEAS.md).

## Separate track (not treatment) — EMC outcomes

- [`meta-analysis.md`](./meta-analysis.md) — pooled **outcomes** systematic review / meta-analysis
  built on the patient registry. A distinct paper on a different question (prognosis, not
  treatment); drafted, needs risk-of-bias scoring + clinician review. Tracked here but **not part
  of the treatment-strategy track**.

## QA & checklists (not manuscripts)

Reviewer-grade verification trails and planning checklists; kept with the papers they support.

- [`fact-check-log.md`](./fact-check-log.md) — fact-check trail for `repurposing-hypotheses.md`
- [`repurposing-hypotheses-review.md`](./repurposing-hypotheses-review.md) — internal peer-review pass of the same
- [`novel-modalities-factcheck.md`](./novel-modalities-factcheck.md) — fact-check trail for `novel-modalities.md`
- [`emc-treatment-paper-outline.md`](./emc-treatment-paper-outline.md) — the retired planning scaffold for the
  active manuscript; retained only as a **figure + claims-audit checklist** (the prose draft now lives in
  `emc-treatment-roadmap.md`).

## Figures

- [`figures/`](./figures/) — generated figures for the active manuscript. Regenerate from the
  `*_figure.py` scripts; see [`../../AGENTS.md`](../../AGENTS.md) → "Making figures".
