# EMC treatment strategy — prioritized portfolio (capstone)

**What this is.** The synthesis of the autonomous treatment-route investigation (2026-06-21/22),
ranking every route by **likelihood of helping a real EMC patient × near-term feasibility**, with
the cheapest experiments that unblock the most. Detail lives in the per-route memos; the live
one-screen board is `research/IDEAS.md`. **This is the crux of the repo** — manuscripts and code
exist to advance entries here.

## What "success" means here — and the two paths we actually have

Nothing in this portfolio is *proven*, and for an untested ultra-rare disease that is **not the
bar**. The goal is to **push EMC treatment forward**: a promising, mechanistically-grounded idea
that *hasn't been tested* is itself publishable and can mobilise people who can test it. So each
candidate is judged on **how convincingly we can advance it**, not whether it's already de-risked.
We can be the ones who build the case that something *could* work.

**We have no wet lab.** That leaves exactly two ways to move a candidate — and every "next step" in
this repo must be one of them:

1. **Publish-to-convince** — assemble mechanism + evidence so rigorously that a group *with* models
   or patients runs the experiment we can't. What makes this land: a falsifiable prediction, a
   clearly specified decisive experiment, and honest kill-criteria.
2. **In-silico evaluation** — use computation to *discover / eliminate / promote* candidates
   ourselves, now or as near-future methods arrive (AI binder & structure design; perturbation-
   prediction "virtual-cell" models e.g. scGPT/Geneformer-class; public-data mining). This is where
   we generate *new evidence* instead of only arguing — and where we should deliberately prepare for
   tools landing in the next 1–3 years.

The strongest candidates are those where **both** apply. The ranking below therefore carries a
*"how WE advance it"* judgement, not a wet-lab to-do list.

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

## Kill-criteria — what would sink each lead (track the "unlikely-to-work" side honestly)

- **TKI+ICI / trabectedin / carfilzomib:** not novel, and EMC evidence is anecdotal/ex-vivo —
  could simply fail to reproduce in prospective EMC patients. Publishable only as *evidence
  synthesis*, not discovery.
- **FAP-RLT, B7-H3 ADC/CAR-T:** die if EMC doesn't express the target. This is checkable *without a
  wet lab* by mining public data (below); if EMC/nearest-surrogate is target-low, drop them.
- **NR4A3 degrader:** dies if EMC is **not addicted to the fusion** (degrading it doesn't kill the
  cell) or if no selective warhead is achievable. The addiction question is the make-or-break.
- **CAR-T:** dies on target expression *or* on failure to penetrate the cold myxoid stroma.
- **TCR-T/ImmTAC, BRD9 synth-lethal, vaccine:** already down-weighted (CTA-low; DepMap-negative;
  weak junction). Tracked as *unlikely* with the reason, so we don't re-litigate.

## The shared data gap — and how we close it WITHOUT a wet lab

Almost every route is gated by the same thing: **EMC-specific data we can't generate experimentally.**
The methodical response is to get as far as possible in-silico / from existing public data, and to
make the residual the explicit subject of a publish-to-convince paper:

- **Target expression (B7-H3, CD56, FAP, PPARG):** mine **public proteomics/transcriptomics** —
  Human Protein Atlas, ProteomicsDB, and public sarcoma/EMC RNA-seq (GEO/SRA), plus the nearest
  surrogate lineages — *instead of* new IHC. An in-silico expression call (even on a surrogate)
  is real evidence and is publishable. ★
- **Fusion addiction (degrader gate):** can't run dTAG, so build the **in-silico/argument case** —
  dependency on the analogous EWS-fusion in Ewing (DepMap), expression-level dependence of NOR-1,
  and *prepare for* perturbation-prediction models (virtual-cell) that could predict EMC fusion
  knockdown effects as they mature. ★
- **The warhead the degrader lacks:** a pure in-silico design problem (next section). ★

## What WE can actually build (the in-silico work program — this is our lane)
- **De-novo binder design** (RFdiffusion / AlphaFold-based) to mature the inverse-NOR-1-agonist
  starting point into a selective NR4A3 degrader warhead — the degrader route's missing piece, and
  a *self-contained computational deliverable we can publish* (a designed candidate + rationale).
- **Surfaceome screen** of the fusion's transcriptional output (published fusion-target gene sets ∩
  membrane-protein annotations) to nominate an EMC-enriched CAR/ADC target rather than a pan-sarcoma
  compromise.
- **Public-data expression mining** for the surface/effector targets above (closes the data gap
  without IHC).
- **AF3** of a fusion↔coactivator / fusion↔E3 interface — *only* once a specific interface is chosen.
- **Prepare for near-future tools:** structure the data/questions so virtual-cell / perturbation-
  prediction models can be applied to EMC the moment they're usable.

## Recommended program (no wet lab)
- **Publish-to-convince, now:** an EMC treatment-landscape / hypothesis paper built on this tracker —
  it makes the case for the clinical leads (TKI+ICI, trabectedin, carfilzomib) *and* the novel
  mechanism (NR4A3 degrader), with explicit decisive experiments for others to run. This is the
  #1 deliverable and the repo's reason to exist.
- **Generate new in-silico evidence:** the NR4A3-degrader warhead design + the public-data expression
  calls + the surfaceome screen — the parts where *we* can move the needle, not just argue.
- **Stop spending on:** the fusion-junction vaccine and the BRD9 transfer bet (assessed, down-
  weighted); keep TCR-T/ImmTAC only as a basket-trial note for the rare antigen⁺ subset.

## Source memos
`immunotherapy-options-emc.md` · `emerging-modalities-scan-emc.md` · `car-t-strategies-emc.md` ·
`degrader-vs-synthetic-lethal.md` (+ `depmap-sarcoma-dependency.json`) · `hla-coverage-emc.md`
(parked) · `novel-modalities.md` (program overview). Live board: `research/IDEAS.md`.
