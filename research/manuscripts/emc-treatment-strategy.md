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

## In-silico results we have actually generated (DepMap, no wet lab) — `depmap-insilico-findings.md`
Mining DepMap 24Q4 with sarcoma lines as the EMC surrogate (pipeline validated on housekeeping):
- **Degrader premise supported by analogy:** FET-fusion sarcomas are fusion-addicted — **FLI1 in
  Ewing = −0.93 gene effect, 74% dependent** — raising the prior that EMC depends on EWSR1::NR4A3,
  i.e. that degrading it could be lethal. (No EMC line exists, so this is an analogy, not proof.)
- **B7-H3/CD276 promoted:** expressed in **99% of sarcoma lines, high across every subtype incl.
  myxoid** → surrogate support for the ADC/CAR-T/bispecific route (was gated on unrun IHC).
- **PRAME is the best antigen-directed bet:** **53% of sarcoma lines, high in myxoid (7.6)/synovial
  (7.2)**; MAGE-A4 (7%) and NY-ESO-1 (5%) confirmed low → favour **brenetafusp (PRAME ImmTAC)** over
  afami-cel. (Cell lines silence CTAs, so these are lower bounds.)

## Recommended program (no wet lab)
- **Publish-to-convince, now:** an EMC treatment-landscape / hypothesis paper built on this tracker —
  it makes the case for the clinical leads (TKI+ICI, trabectedin, carfilzomib) *and* the novel
  mechanism (NR4A3 degrader), with explicit decisive experiments for others to run. This is the
  #1 deliverable and the repo's reason to exist.
- **Generate new in-silico evidence:** the NR4A3-degrader warhead design + the public-data expression
  calls + the surfaceome screen — the parts where *we* can move the needle, not just argue.
- **Stop spending on:** the fusion-junction vaccine and the BRD9 transfer bet (assessed, down-
  weighted); keep TCR-T/ImmTAC only as a basket-trial note for the rare antigen⁺ subset.

## Publishing & in-silico strategy (open strategic questions — current thinking, 2026-06)

Standing program decisions. Revisit as results and tools land.

### Q1 — Scope of the FIRST paper
**Decision: paper 1 is the prioritized-portfolio roadmap (`emc-treatment-roadmap.md`) — not the
MD→de-novo degrader, and not a broadened rare-cancer framework.**
- The **degrader/MD→design paper is premature as paper 1** (no result yet: MD unrun, no designed
  candidate). It is the natural **paper 2** — a focused, higher-impact *result* paper once the
  cryptic-pocket MD + a designed selective warhead exist; it will cite paper 1.
- The **roadmap is publishable now** and is the right trunk: it carries *new computed evidence*
  (DepMap fusion-addiction proxy, target expression, structure) + falsifiable decisive experiments,
  so it is more than a review; it establishes the program, claims priority, and — the point for an
  orphan disease — **hands testable hypotheses to groups with models/patients** (mobilize-others).
  Low novelty bar, fast to preprint.
- **Don't over-broaden.** A general "computational triage for rare cancers" framing dilutes
  actionability and credibility. Keep paper 1 EMC-specific and concrete; put generalizability + the
  broader-indication idea (roadmap §7) in the Discussion as future work. Breadth becomes a later
  *perspective* paper once there's a track record.
- **Sequence:** P1 roadmap (now) → P2 degrader (MD + warhead, when results land) → result/update
  papers → an eventual generalization/perspective.

### Q2 — How in-silico testing improves over ~1 year → timing & cadence
Methods are improving fast, but **that argues for shipping paper 1 SOON, not waiting** — the roadmap
doesn't depend on better tools, and delay forfeits priority and collaborators. Better tools matter
for the *result* papers. Capability curves to watch:
- **Perturbation-prediction / "virtual-cell" models** (scGPT/Geneformer/State-class; Arc Virtual
  Cell): the **highest-leverage** near-future capability for us — one that predicts a knockdown/
  degradation phenotype in a held-out context could **predict EMC fusion-dependence in-silico,
  substituting for the dTAG wet-lab experiment that gates the whole degrader route.** When usable,
  top-priority re-run and likely its own paper.
- **Structure/complex + binder/molecule design** (AF3-class: Boltz/Chai; RFdiffusion2; SBDD
  diffusion): improve warhead design + PROTAC ternary modelling → refresh the design as they mature.
- **Cheaper/better MD + ML force fields**: better cryptic-pocket sampling.
- **Cadence:** publish P1 now; follow up roughly every **~6 months**, triggered by (a) a compute
  result landing or (b) a watched capability crossing a usefulness threshold. Treat the roadmap as a
  **living, versioned reference**, not a one-shot. Robust stance under tool-progress uncertainty:
  ship what's publishable now; re-run/upgrade only when a *specific* gating capability actually
  arrives — don't bet the schedule on tools that may slip.

### Q3 — Automating the tracking of in-silico advances (use new tech as soon as it's ready)
**BUILT** — `scripts/method-watch.mjs` + `.github/workflows/method-watch.yml` (monthly cron),
publishing a dated digest to the `method-watch-cache` branch; watch config + trigger table tracked
at `research/method-watch.md`. Reuses the repo's scheduled-probe pattern (`fetch-literature.yml`):
- A **cron CI job** (monthly) running targeted searches (Europe PMC + GitHub releases) for our gaps
  — *virtual cell / perturbation prediction, AlphaFold3 / Boltz / Chai, RFdiffusion, de-novo binder
  design, cryptic pocket, in-silico oligo/nanoparticle tumour-DELIVERY prediction, NR4A3* — emitting
  a **digest** for the next agent/human to triage.
- A **capability → action trigger table** (canonical copy in `research/method-watch.md`):

  | When this capability becomes usable | …re-run this |
  |---|---|
  | virtual-cell predicts held-out knockdown phenotype | EMC fusion-dependence (the degrader make-or-break) |
  | open AF3-class ternary-complex prediction | NR4A3–PROTAC–E3 degradability geometry |
  | reliable structure-based generative + selectivity scoring | NR4A3 warhead design (using `nr4a-selectivity.json` handles) |
  | in-silico oligo/nanoparticle tumour-delivery predictor | score the B7-H3-targeted junction-siRNA/AOC delivery → re-grade the ASO route (its gate) |
  | improved perturbation/DepMap-transfer models | re-test synth-lethal / nominate new dependencies |

- **Keep pipelines modular** so a new model swaps in cheaply (structure step AF2→AF3/Boltz; design
  step already separated from scoring). Pin versions, document the upgrade path.
- *Trap to avoid:* over-engineering a "capability detector." A periodic search digest + this trigger
  table is enough.

### Q4 — Low-latency dissemination (keep the roadmap fresher than the journal cycle)
**Problem.** Peer review is months-slow; the method/treatment landscape moves in weeks (this repo
already re-graded routes mid-cycle: degrader downgraded then re-primed once Boltz shipped; ASO added;
delivery vector identified). A single journal paper is **stale on arrival** for the volatile parts.
**Principle: put volatility in the low-latency layer and stability in the slow one.** Three tiers,
each matched to how fast its content changes:

- **Tier A — the git repo *is* the living roadmap (latency: instant, fully in our control).**
  `emc-treatment-roadmap.md` + `IDEAS.md` are already version-controlled and updated the moment a
  finding lands. Make this official: maintain a dated **changelog** at the top of the roadmap (what
  changed, why, which method-watch hit drove it) so a reader sees the live state and its provenance.
  The method-watch digest (Q3) is the automated *input* to this layer.
- **Tier B — citable, versioned snapshots (latency: minutes–days).** Wire **GitHub releases →
  Zenodo** so every tagged release mints a **versioned DOI** archiving that state of the roadmap;
  and post the roadmap as a **bioRxiv preprint we bump (v2, v3…)** as Tier-1/2 routes change —
  i.e., treat it as a *living preprint / living review*, an accepted genre. Cadence: cut a
  release/DOI on any **Tier-1/2 route change** (or monthly if anything changed); bump the preprint on
  any change a reader would act on differently.
- **Tier C — peer-reviewed journal (latency: months, occasional).** Reserve this for the **stable
  core** that *doesn't* decay: the falsifiable kill-criteria framework, the methodology (pooling,
  citation map), and the "why pursue an ultra-rare cancer / broaden-to-common" argument. The journal
  paper should **explicitly delegate the live portfolio** to the low-latency layer — e.g. *"the
  current route prioritization is maintained at <repo + latest Zenodo DOI>"* — so its slowness never
  makes it wrong, only less current on rankings it already disclaims.

**Net:** the paper earns credibility once; the roadmap stays current continuously; the DOI/preprint
layer makes the current state citable in between. Build order: changelog (now, free) → Zenodo release
hook → preprint with a "living" banner pointing at the repo.

## Source memos
`immunotherapy-options-emc.md` · `emerging-modalities-scan-emc.md` · `car-t-strategies-emc.md` ·
`degrader-vs-synthetic-lethal.md` (+ `depmap-sarcoma-dependency.json`) · `hla-coverage-emc.md`
(parked) · `novel-modalities.md` (program overview). Live board: `research/IDEAS.md`.
