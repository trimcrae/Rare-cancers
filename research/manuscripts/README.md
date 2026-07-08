# research/manuscripts/ — what's here, and what's active

This folder holds the treatment-track writing plus a few supporting and separate-track
documents. To avoid the "which of these is *the paper*?" confusion, the rule is:

> **TWO PRIORITY papers to publish first (trimcrae decision 2026-06-26):**
> 1. **[`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md)** — **lead result paper**; **reframed
>    2026-07-08 around NR4A-*family* druggability with two design poles** (cryptic-pocket druggability +
>    selectivity handles + degrader design, tuned from **NR4A3-selective** for NR4A3-driven cancers to
>    **pan-NR4A** for ex-vivo CAR-T de-exhaustion). EMC is the lead clinical application of the selective
>    pole. Realistic journal target: **JCIM** + ChemRxiv immediately (an early "Nature Computational Science /
>    ACS Central Science" aim was walked back 2026-07-08 as over-optimistic for a no-wet-lab study). Framing decision:
>    [`nr4a3-degrader-carT-and-family-druggability-framing.md`](./nr4a3-degrader-carT-and-family-druggability-framing.md).
>    *Selective pole is NR4A3-selective but NOT fusion-selective (the LBD is shared with wild-type NR4A3).*
> 2. **[`fusion-junction-aso-paper.md`](./fusion-junction-aso-paper.md)** — **fusion-exclusive result
>    paper**: an RNase-H gapmer / siRNA against the EWSR1::NR4A3 breakpoint junction that silences the
>    chimera while **sparing wild-type NR4A3** — the most-likely-to-work fusion-unique route, with a
>    complete in-silico arc (design → off-target → breakpoint-favorability scan → gap-mismatch-resolved
>    predicted-clean gapmers; delivery is the one remaining gate). The standout of the fusion-exclusive set.
>
> **Next tier (not the first two):** **[`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md)** (the
> EMC-program paper: driver-directed framework, categorical-gap landscape, fusion-specific routes) and the
> **fusion-exclusivity framework** ([`fusion-selective-approaches-overview.md`](./fusion-selective-approaches-overview.md))
> spanning all five fusion-unique routes (ASO, neoantigen, AND-gate degrader, condensate, PPI) — the
> framework houses the four non-ASO routes as a comparative design space.
>
> All still serve the repo's EMC goal (the degrader paper is *how* we advance it — see
> [`nr4a3-degrader-paper-positioning.md`](./nr4a3-degrader-paper-positioning.md)). Everything else in this
> folder **feeds** one of them, **records QA**, or is **parked / separate-track**; each file carries a
> one-line role banner.

---

## ▶ Priority manuscripts (publish first — 2026-06-26 decision)

- **[`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md)** and
  **[`fusion-junction-aso-paper.md`](./fusion-junction-aso-paper.md)** — the two papers to develop to
  preprint/submission first (see the priority block at the top of this file and `emc-treatment-strategy.md`
  Q1). The degrader is the target-selective result; the ASO is the fusion-exclusive result that spares
  wild-type NR4A3.

- **[`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md)** — *"Attacking an 'undruggable' fusion
  oncoprotein by computation alone: a driver-directed treatment program for EWSR1::NR4A3 EMC."* The
  **EMC-program paper** — now **next-tier**, not the first to ship. **Its contribution is the novel
  in-silico work** (done + planned) and the **driver-directed designs** it feeds (degrader + junction-ASO
  against the fusion itself); the repurposing/standard-of-care material is *not* a contribution — it
  appears only as one-paragraph context establishing the categorical gap (no targeted drug exists for
  EMC). Grading known drugs was cut in the 2026-06-24 rescope (see `emc-treatment-strategy.md` Q1). It is
  a **living document** (changelog at its top).

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
- [`car-t-strategies-emc.md`](./car-t-strategies-emc.md) — CAR-T *surface-target* strategies for treating EMC directly (Phase 3). NB: distinct from the degrader's pan-NR4A CAR-T-*enhancement* angle below.
- [`nr4a3-degrader-carT-and-family-druggability-framing.md`](./nr4a3-degrader-carT-and-family-druggability-framing.md) — framing decision (2026-07-08): the pan-NR4A ex-vivo CAR-T-enhancement pole + the NR4A-family-druggability reframe (JCIM target; NCS walked back). Feeds the degrader paper + positioning doc.
- [`nr4a3-degrader-ncs-presubmission-inquiry.md`](./nr4a3-degrader-ncs-presubmission-inquiry.md) — drafted free presubmission enquiry to Nature Computational Science (the long shot); if declined → JCIM + ChemRxiv.
- [`degrader-vs-synthetic-lethal.md`](./degrader-vs-synthetic-lethal.md) — degrader vs. BRD9 head-to-head
- [`nr4a3-degrader-broader-indications.md`](./nr4a3-degrader-broader-indications.md) — beyond-EMC motivation for the degrader (NR4A3-fusion sarcomas; NR4A in T-cell exhaustion / immuno-oncology; the AML tumour-suppressor contraindication)

## Surface-antigen preprint (red-teamed; hypothesis-generating, seeks validation data)

- [`emc-surface-target-landscape.md`](./emc-surface-target-landscape.md) — **full preprint** (trimcrae
  2026-07-03): a *target-class* paper on EMC **surface antigens** for delivery + immunotherapy (ADC / TCE /
  CAR / radioligand) — a different thesis/modality axis from the fusion-junction ASO. Deliberately
  self-critical after two red-team passes ([`emc-surface-target-redteam.md`](./emc-surface-target-redteam.md)):
  rigorous selectivity + a hard normal-tissue window show **B7-H3 is not selective** and the selective
  candidates carry window liabilities, so the honest result refines priorities and nominates a neuroendocrine
  **SSTR2/GD2** route rather than declaring winners. Uses the one real EMC line in DepMap (**H-EMC-SS /
  ACH-001519**, n=1). Ready-to-send author outreach: [`emc-surface-target-outreach.md`](./emc-surface-target-outreach.md).
  Makes **no** EMC-validated surface claim; the decisive protein-level validation needs the patient-derived
  EMC lines.

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
