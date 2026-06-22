# EMC treatment strategy — prioritized portfolio (capstone)

**What this is.** The synthesis of the autonomous treatment-route investigation (2026-06-21/22),
ranking every route by **likelihood of helping a real EMC patient × near-term feasibility**, with
the cheapest experiments that unblock the most. Detail lives in the per-route memos; the live
one-screen board is `research/IDEAS.md`. Goal throughout: a *real treatment*, not a paper.

## The ranking

### Tier 1 — Actionable now (approved drugs, EMC evidence) — **the realistic near-term wins**
1. **Anti-angiogenic TKI + checkpoint inhibitor.** Real EMC partial responder (ImmunoSarc
   sunitinib+nivolumab); EMC is TKI-sensitive and the TKI remodels the cold TME (cold→hot) — a
   mechanistic synergy, not coincidence. All drugs approved. *(immunotherapy-options-emc.md §2)*
2. **Trabectedin (± RT, ± TKI/IO).** Approved for STS; its mechanism *is* displacing fusion
   transcription factors from promoters (proven in myxoid liposarcoma), and EMC has a reported
   impressive responder. *(emerging-modalities-scan-emc.md §1)*
3. **Carfilzomib ± anthracycline (± venetoclax)** — *best ex-vivo EMC evidence of anything here.*
   The only 1 of 17 drugs with high sensitivity across **two patient-derived EMC models**, with
   carfilzomib+doxorubicin / +venetoclax synergy (Bangerter et al. 2023). Approved drugs; the play
   is a combination arm on EMC's existing **anthracycline (doxorubicin)** backbone. Already in the
   repurposing track — see `repurposing-hypotheses.md` (the unbiased-screen tier). *Carried here so
   the portfolio isn't wrong by omission.*

> **Headline:** the best near-term options are **repurposing approved drugs** — TKI+ICI and
> trabectedin (mechanism-fit) and the **carfilzomib+anthracycline ex-vivo hit** — not novel
> modalities. That is the honest answer to "what could help a patient now."

> **Relationship to the existing repurposing work.** This capstone sits *on top of* the repo's
> repurposing track (`repurposing-hypotheses.md`, `hypotheses/candidates.json`, TxGNN predictions),
> which already covers doxorubicin (standard), the carfilzomib ex-vivo hit, and a *mechanistic* tier
> (pioglitazone/PPARγ, BET/CDK7–9, NR4A3/NOR1, mRNA-vaccine+checkpoint). What the night's work
> **adds**: trabectedin (fusion-TF mechanism + EMC responder), the **TKI+ICI ImmunoSarc EMC
> responder**, FAP-RLT, B7-H3 surface modalities, the NR4A3-degrader specifics, and **data** that
> *updates* two existing mechanistic hypotheses — the DepMap result down-weights BET/CDK
> (no sarcoma selectivity), and §4 below is the same PPARG axis as the existing pioglitazone idea.

### Tier 2 — Emerging, plausible, gated by ONE cheap confirm
3. **FAP-targeted radioligand therapy (FAPI-RLT).** ~50% disease control in advanced sarcoma; EMC's
   myxoid stroma is likely FAP⁺; the tracer is also the diagnostic. *Gate: EMC FAP-PET avidity.*
4. **B7-H3 ADC (ifinatamab deruxtecan).** B7-H3 in 97% of STS; fastest surface-target route. *Gate:
   EMC-specific B7-H3 IHC — **not yet published** (ultra-rare tumour), favorable prior only.*

### Tier 3 — High-ceiling, longer-horizon, real groundwork
5. **Degrader — NR4A3 PROTAC** (the best "attack the actual driver" bet). Mechanistically ideal
   (NOR-1 activity scales with expression level), the family is degradable (NR4A1 PROTAC works),
   NR4A3-specific warhead starting points exist (inverse NOR-1 agonists). *Needs: a selective
   warhead (med-chem or **AI de-novo binder design**) + the dTAG fusion-addiction test.*
6. **CAR-T** (B7-H3 / CD56 ± TKI; armored / SynNotch-logic-gated / allogeneic). Same surface-target
   gate as the ADC but harder; higher ceiling. Among surface modalities, **ADC/RLT beat CAR-T to a
   patient.** *(car-t-strategies-emc.md)*

### Tier 4 — Speculative / downstream / parked
7. **PPARG modulation (TZDs)** — the fusion transactivates PPARG; druggable downstream node, but
   agonist-vs-antagonist direction unresolved. *This is the same axis as the existing
   **pioglitazone** mechanistic hypothesis in `repurposing-hypotheses.md`* — Phase-2 added the
   fusion→PPARG transactivation mechanism behind it. Cheap to explore.
8. **TCR-T / ImmTAC** — weak: EMC is cancer-testis-antigen-low. Only a PRAME⁺/HLA-A\*02⁺ subset, via
   the brenetafusp basket. *(immunotherapy-options-emc.md §1, §2b)*
9. **Synthetic-lethal / BRD9** — **downgraded** by a computed DepMap transfer prior (BRD9/ncBAF not
   sarcoma-selective, not even in Ewing). No shortcut; needs a de-novo CRISPR screen in EMC models.
10. **Fusion-junction vaccine / HLA-coverage** — parked (self-adjacent junction in a cold tumour;
    economics favour a platform we don't control). Reusable: its HLA work feeds TCR-T/ADC eligibility.

## The cross-cutting bottleneck (and the highest-leverage investment)

**Almost every route is gated by the same thing: EMC tissue/model scarcity.** One small set of
assets unblocks the most:
- **A patient-derived EMC tissue microarray / cohort for IHC** → resolves B7-H3, CD56, FAP (gates
  Tiers 2 *and* 6 — ADC, bispecific, RLT, CAR-T) in a single cheap experiment nobody has run.
- **Patient-derived EMC cell lines** (NCC-EMC1-C1 2025; USZ-EMC) → the dTAG fusion-addiction test
  (degrader make-or-break) and any CRISPR screen (synth-lethal).
- **FAP-PET on EMC patients** → doubles as diagnostic + RLT eligibility.

If the program could fund one wet-lab thing, it's the **EMC IHC/FAP-PET expression panel** — it
de-risks four modalities at once and is cheap.

## AI-era accelerators worth pursuing computationally
- **De-novo binder design** (RFdiffusion / AlphaFold-based) to mature the inverse-NOR-1-agonist hit
  into a selective NR4A3 PROTAC warhead — the degrader route's missing piece.
- **Surfaceome screen** of the fusion's transcriptional output to discover an EMC-enriched CAR/ADC
  target instead of a pan-sarcoma compromise (data-limited; uses published fusion-target gene sets).
- **AF3** for a fusion↔coactivator / fusion↔E3 interface, *only* once a specific interface is chosen.

## Recommended portfolio (if forced to choose)
- **Pursue now (clinical, existing drugs):** TKI+ICI and trabectedin — and the rational combination
  of them — through sarcoma/basket trials. This is where a patient benefits soonest.
- **Fund one experiment:** the EMC IHC/FAP-PET expression panel (unblocks ADC/RLT/CAR-T).
- **Invest computationally (high ceiling):** the NR4A3-degrader warhead (AI binder design) + dTAG
  validation — the only route that attacks the actual driver.
- **Stop spending on:** the fusion-junction vaccine and the BRD9 transfer bet (both assessed and
  down-weighted); keep TCR-T/ImmTAC only as a basket-trial option for the rare antigen⁺ subset.

## Source memos
`immunotherapy-options-emc.md` · `emerging-modalities-scan-emc.md` · `car-t-strategies-emc.md` ·
`degrader-vs-synthetic-lethal.md` (+ `depmap-sarcoma-dependency.json`) · `hla-coverage-emc.md`
(parked) · `novel-modalities.md` (program overview). Live board: `research/IDEAS.md`.
