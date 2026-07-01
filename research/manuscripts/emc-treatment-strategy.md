# EMC treatment strategy — prioritized portfolio (capstone)

> **STRATEGY / SOURCE OF TRUTH (not a manuscript).** This capstone ranks every treatment route; the
> active manuscript [`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md) is its publishable form.
> Read this before resuming treatment-research work. Folder map: [`README.md`](./README.md).

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

## The ranking — two axes, not one tier number

A single ranked "tier" misleads here, because a tier number silently blends **two independent
questions that do not move together**:

- **Axis A — near-term readiness:** how close is this to helping a real EMC patient *now*? (Drug
  approved and available? Real EMC evidence? Or must it still be discovered, built, or validated?)
- **Axis B — driver-directedness:** how directly does it target the EWSR1::NR4A3 driver itself? Three
  *defined* levels — **driver-directed** (the fusion itself) → **targeted, indirect** (an EMC target
  that isn't the fusion) → **generic** (disease-agnostic). This is a categorical property of the
  mechanism, used deliberately *instead of* a numeric "impact" score we cannot measure for untested agents.

These pull in opposite directions. The **repurposed approved drugs are the most *ready*** (Axis A)
but **generic** (Axis B); the **NR4A3 degrader and junction ASO are the only *driver-directed*
routes** (Axis B) but the **furthest from a patient** (Axis A). Collapsing both onto one number is what
made the old "Tier 1/2/3" labels inconsistent across documents. So we score every route on **both
axes** and let the reader weight whichever they care about — a clinician seeking the next option
leans on Axis A; a scientist or developer choosing where the field should invest leans on Axis B.
*(This table mirrors the one in the active manuscript, `emc-treatment-roadmap.md` §3.)*

| Route | **Axis A — near-term readiness** | **Axis B — driver-directedness** |
|---|---|---|
| Anti-angiogenic TKI + checkpoint inhibitor | **Now** — approved; real EMC responder | **Generic** — anti-angiogenic + checkpoint; disease-agnostic |
| Trabectedin (± RT / combo) | **Now** — approved; reported EMC responder | **Targeted (indirect)** — displaces the fusion TF from promoters (mechanism-fit), not fusion-selective |
| Carfilzomib + anthracycline (± venetoclax) | **Now** — approved; best *ex-vivo* EMC evidence | **Generic** — proteasome inhibitor; empirical ex-vivo hit, no fusion rationale |
| B7-H3 (CD276) ADC / bispecific | **Confirm-gated** — needs EMC B7-H3 IHC | **Targeted (indirect)** — surface antigen (not the fusion); fastest such route |
| PRAME ImmTAC / cell therapy | **Confirm-gated** — needs EMC PRAME IHC | **Targeted (indirect)** — cancer-testis antigen; basket access via brenetafusp |
| FAP radioligand therapy | **Confirm-gated** — needs EMC FAP-PET | **Targeted (indirect)** — stromal target; theranostic (tracer = diagnostic) |
| **NR4A3 degrader (PROTAC)** | **To build** — no selective warhead yet; no EMC validation | **Driver-directed** — degrades the EWSR1::NR4A3 fusion oncoprotein. *Flagship.* |
| **Fusion-junction ASO / siRNA** | **To build** — tumour delivery unsolved | **Driver-directed** — silences the fusion transcript, junction-specific. *Flagship.* |
| B7-H3 / CD56 CAR-T | **To build** — harder than the ADC | **Targeted (indirect)** — surface antigen; higher bar than the ADC |
| PPARG modulation (TZDs) | **To build** — agonist-vs-antagonist direction unresolved | **Targeted (indirect)** — a node the fusion transactivates (downstream, not the driver) |
| TCR-T / ImmTAC (cancer-testis antigen) | **Down-weighted** — EMC is CTA-low | **Targeted (indirect)** — antigen-directed in principle; gated on Axis A (EMC antigen-low) |
| Synthetic-lethal / BRD9 | **Down-weighted** — DepMap transfer prior negative | **Targeted (indirect)** — a candidate dependency; not sarcoma-selective |
| Fusion-junction vaccine / HLA-coverage | **Parked** | **Targeted (indirect)** — fusion neoantigen; weak immunogen in a cold tumour |

> **Axis B levels (defined, not scored):** **Driver-directed** = acts on the EWSR1::NR4A3 fusion
> product/transcript itself · **Targeted (indirect)** = engages EMC's fusion-driven biology at a point
> *other* than the fusion (surface antigen, stroma, a transactivated node, a dependency, or fusion-TF
> displacement) · **Generic** = a disease-agnostic mechanism. This categorical *directedness* is an
> objective property of the mechanism; we use it rather than a numeric "impact" score we cannot measure
> for untested agents. **Axis A** is likewise four defined states (available now / confirm-gated /
> to build / down-weighted). Read a route from **both** cells — an antigen route is "targeted" on B yet
> "down-weighted" on A when EMC doesn't express the antigen.

The detail below is grouped by **Axis A (readiness)** for readability, with the flagship (Axis B)
called out explicitly — *grouping is not a combined rank; read both axes off the table.*

### Ready now — approved drugs with EMC evidence  *(Axis A: now · Axis B: generic)*
- **Anti-angiogenic TKI + checkpoint inhibitor.** Real EMC partial responder (ImmunoSarc
   sunitinib+nivolumab); EMC is TKI-sensitive and the TKI remodels the cold TME (cold→hot) — a
   mechanistic synergy, not coincidence. All drugs approved. *(immunotherapy-options-emc.md §2)*
- **Trabectedin (± RT, ± TKI/IO).** Approved for STS; its mechanism *is* displacing fusion
   transcription factors from promoters (proven in myxoid liposarcoma), and EMC has a reported
   impressive responder. *(emerging-modalities-scan-emc.md §1)*
- **Carfilzomib ± anthracycline (± venetoclax)** — *best ex-vivo EMC evidence of anything here.*
   The only 1 of 17 drugs with high sensitivity across **two patient-derived EMC models**, with
   carfilzomib+doxorubicin / +venetoclax synergy (Bangerter et al. 2023). Approved drugs; the play
   is a combination arm on EMC's existing **anthracycline (doxorubicin)** backbone. Already in the
   repurposing track — see `repurposing-hypotheses.md` (the unbiased-screen tier). *Carried here so
   the portfolio isn't wrong by omission.*

> **Headline (Axis A — readiness):** the most *ready* options are **repurposing approved drugs** —
> TKI+ICI and trabectedin (mechanism-fit) and the **carfilzomib+anthracycline ex-vivo hit** — not
> novel modalities. That is the honest answer to "what could help a patient now." On Axis B they are
> **generic** — for the only **driver-directed** bet see the **NR4A3 degrader**.

> **Relationship to the existing repurposing work.** This capstone sits *on top of* the repo's
> repurposing track (`repurposing-hypotheses.md`, `hypotheses/candidates.json`, TxGNN predictions),
> which already covers doxorubicin (standard), the carfilzomib ex-vivo hit, and a *mechanistic* tier
> (pioglitazone/PPARγ, BET/CDK7–9, NR4A3/NOR1, mRNA-vaccine+checkpoint). What the night's work
> **adds**: trabectedin (fusion-TF mechanism + EMC responder), the **TKI+ICI ImmunoSarc EMC
> responder**, FAP-RLT, B7-H3 surface modalities, the NR4A3-degrader specifics, and **data** that
> *updates* two existing mechanistic hypotheses — the DepMap result down-weights BET/CDK
> (no sarcoma selectivity), and §4 below is the same PPARG axis as the existing pioglitazone idea.

### Gated by one cheap confirm — surface/antigen targets  *(Axis A: confirm-gated · Axis B: targeted, indirect)*
- **FAP-targeted radioligand therapy (FAPI-RLT).** ~50% disease control in advanced sarcoma; EMC's
   myxoid stroma is likely FAP⁺; the tracer is also the diagnostic. *Gate: EMC FAP-PET avidity.*
- **B7-H3 ADC (ifinatamab deruxtecan).** B7-H3 in 97% of STS; fastest surface-target route. *Gate:
   EMC-specific B7-H3 IHC — **not yet published** (ultra-rare tumour), favorable prior only.*

### To build — driver-directed & targeted, longer-horizon  *(Axis A: to build · Axis B: driver-directed / targeted)*
- **Degrader — NR4A3 PROTAC** — **the flagship, driver-directed bet** ("attack the actual driver"). Mechanistically ideal
   (NOR-1 activity scales with expression level), the family is degradable (NR4A1 PROTAC works),
   NR4A3-specific warhead starting points exist (inverse NOR-1 agonists). *Needs: a selective
   warhead (med-chem or **AI de-novo binder design**) + the dTAG fusion-addiction test.*

> **Feasibility check (2026-06-25, updated) — orthosteric druggability reconfirmed at 0.495.**
> A 2026-06-25 "reassessment" briefly claimed the orthosteric pocket was ~0.026 (undruggable). **That
> was retracted the same day: it was a self-inflicted bug** in an interim pocket-enumeration script
> (a wrong alpha-sphere count + a filename→pocket index assumption), *not* a real druggability number.
> Regenerating the JSONs from the count-fixed, data-derived pipeline (see
> `research/modalities/ASSUMPTIONS.md`) reproduces the **original** values exactly: the orthosteric LBD
> **Pocket 5 = druggability 0.495**, lining residues **406–534**, carrying **all 7 selectivity
> handles** (L406, T407, T410, R412, I484, I531, L534). So the warhead plan is **unchanged** from the
> original: a borderline-druggable orthosteric pocket (0.495, just under the conventional 0.5 cutoff)
> that *also* holds the selectivity — druggability and selectivity coincide here, the favourable case.
> - The **make-or-break in-silico test stands:** per-frame fpocket druggability over the cryptic-pocket
>   MD/metadynamics — does breathing push the borderline 0.495 pocket **≥0.5** (cryptic opening, route
>   live) or collapse it (route weakened)? This is wired into `nr4a3_mdpocket.py` and is what the
>   metadynamics run reads out.
> - The small-molecule orthosteric warhead **remains the lead**; the de-novo protein binder and
>   junction ASO stay as the pocket-independent backups they always were (not promoted to co-lead).
- **CAR-T** (B7-H3 / CD56 ± TKI; armored / SynNotch-logic-gated / allogeneic). Same surface-target
   gate as the ADC but harder; higher bar. Among surface modalities, **ADC/RLT beat CAR-T to a
   patient.** *(car-t-strategies-emc.md)*

### Down-weighted / speculative / parked  *(Axis A: down-weighted)*
- **PPARG modulation (TZDs)** — the fusion transactivates PPARG; druggable downstream node, but
   agonist-vs-antagonist direction unresolved. *This is the same axis as the existing
   **pioglitazone** mechanistic hypothesis in `repurposing-hypotheses.md`* — Phase-2 added the
   fusion→PPARG transactivation mechanism behind it. Cheap to explore.
- **TCR-T / ImmTAC** — weak: EMC is cancer-testis-antigen-low. Only a PRAME⁺/HLA-A\*02⁺ subset, via
   the brenetafusp basket. *(immunotherapy-options-emc.md §1, §2b)*
- **Synthetic-lethal / BRD9** — **downgraded** by a computed DepMap transfer prior (BRD9/ncBAF not
   sarcoma-selective, not even in Ewing). No shortcut; needs a de-novo CRISPR screen in EMC models.
- **Fusion-junction vaccine / HLA-coverage** — parked (self-adjacent junction in a cold tumour;
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
**Decision (2026-06-26, trimcrae) — the two papers to publish FIRST are the NR4A3-degrader paper and the
fusion-junction ASO paper.** This supersedes the earlier "paper 1 = roadmap" sequencing *for what ships
first*. The two priorities:
1. **NR4A3-degrader result paper** ([`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md)) — the
   target-centric cryptic-pocket/selectivity/degrader-design result. NR4A3-selective but **not**
   fusion-selective (shared LBD).
2. **Fusion-junction ASO paper** ([`fusion-junction-aso-paper.md`](./fusion-junction-aso-paper.md)) — the
   **fusion-exclusive** RNA-level route that spares wild-type NR4A3, and the **most-likely-to-work** of the
   fusion-unique modalities (proven knockdown class + strong fusion-addiction prior). It now carries a
   complete in-silico arc — gapmer/siRNA design → transcriptome-wide off-target screen → a per-breakpoint
   favorability scan (the canonical junction is GC-rich/specificity-poor, but **62% of modelled breakpoints
   are favorable**) → a **gap-mismatch-resolved** off-target screen that finds **predicted-clean gapmers
   (2/5) at a favorable breakpoint** — plus a reusable specificity workflow that generalizes to any
   recurrent-fusion ASO. **Delivery is its one remaining gate.** Rationale for elevating it over the
   roadmap/program paper: it is a self-contained *result + method*, it is the highest-likelihood-of-working
   fusion-exclusive route, and it pairs naturally with the degrader (the degrader spares the paralogues; the
   ASO spares wild-type NR4A3 — the next selectivity tier). **Next tier (not first):** the
   `emc-treatment-roadmap.md` program paper and the **fusion-exclusivity framework**
   ([`fusion-selective-approaches-overview.md`](./fusion-selective-approaches-overview.md), which houses the
   four non-ASO fusion-unique routes as a comparative design space). The prior 2026-06-24 framing is
   retained below for the record.

**Note (2026-06-30, honest-assessment pass — two corrections to hold; don't re-litigate).**
1. **Publishability rests on novel *findings*, not novel *methods* — do not conflate them.** A passing
   framing in discussion drifted to "the methods aren't novel, so there's nothing to publish." That is a
   category error. Both flagship papers use *standard* tools (metadynamics, docking, MM-GBSA, DiffSBDD,
   transcriptome off-target BLAST) — but their **findings are first-in-target**: the first
   druggability/cryptic-pocket characterization of NR4A3 (no prior structure or pocket analysis), the first
   family-wide *state-matched* NR4A1/2/3 selectivity map, and a designed NR4A3-selective candidate
   (`denovo_401`) that survives an unusually complete control battery (docking → single- **and
   multi-snapshot** MM-GBSA → **single- and multi-snapshot decoy nulls** → state-matched re-dock →
   clean/synthesizable, no structural alerts). That is a legitimate, publishable contribution at
   **specialized-journal tier** (JCIM / IJMS / PLoS Comp. Biol. / Front. Pharmacol. / Sci. Rep.) — *not*
   methods-novel, *not* high-impact, and the candidate must be framed as **designed/predicted, not
   validated** (no wet lab). Sell the **target knowledge + the controlled candidate**, never the methods.
   The same logic applies to the ASO paper (first junction-specificity map + clean designed gapmers);
   its weaker spots are the delivery caveat and a thinner candidate battery, not "nothing to publish."
2. **WT-NR4A3 — resolve the bet-vs-hedge contradiction before submission.** The repo asserts *both* (a) the
   degrader's "WT NR4A3 loss is **tolerable** (paralogue redundancy; viable single-KO animals)" and (b) the
   ASO's "**sparing** WT NR4A3 is a headline advantage / avoids the tumour-suppressor liability the degrader
   carries." As two confident *independent* claims they contradict. Reconcile as **one bet and its hedge**:
   WT-NR4A3-loss tolerability is *uncertain* — paralogue redundancy plausibly covers the *physiological*
   roles, but the *tumour-suppressor* axis (HCC/breast/lymphoma) under chronic systemic loss is far less
   certain; the **degrader bets it is tolerable**, the **ASO hedges** against that bet being wrong. Frame the
   ASO's WT-sparing as *insurance + automatic paralogue/tumour-exclusivity*, **not** as an independent win the
   degrader's own thesis declares moot. Align both manuscripts' WT-NR4A3 language to this.
   *(A third, related inconsistency — §2.7's "source paralogue selectivity from the ternary, not the binder"
   read as contradicting the whole binder campaign — was **fixed 2026-07-01** (trimcrae): reframed to
   "binder **+** ternary" (factors compound; a selective binder is the primary goal and `denovo_401` is one,
   control-validated; the ternary is an *additional* robustness lever, not a substitute). Corrected in the
   paper §2.7/§5/abstract and `nr4a3-degrader-selectivity-architecture.md` thesis + §7.)*

**Decision (REVISED 2026-06-24): paper 1 is the computation-only `emc-treatment-roadmap.md`, but its
*contribution* is reframed from "the prioritized portfolio" to "a method + a driver-directed program."**
The earlier framing (below) made the *ranking of mostly-known repurposed drugs* the headline, which
reads as review-grade and invites a "what's new?" rejection. Revised framing: the contribution is (1)
the reproducible two-axis triage **method**, (2) the **driver-directed program** against EWSR1::NR4A3
itself (structural undruggability call → degrader + junction-ASO, each with first in-silico evidence and
a make-or-break experiment), and (3) the **falsifiable kill-criterion** per route. The repurposing
portfolio is demoted to *motivating landscape / triage output* (prior knowledge, labelled as such); its
volatile ranking is delegated to the living layer (Q4), so the journal paper's claim is the stable
core. **This does NOT promote the degrader *result* paper to paper 1** — the MD/warhead-design *results*
remain the focused follow-on (paper 2, §below); paper 1 claims the program and the completed in-silico
pieces, not the pending results. Original decision retained for the record:

> **(Superseded framing) paper 1 is the prioritized-portfolio roadmap (`emc-treatment-roadmap.md`) — not
> the MD→de-novo degrader, and not a broadened rare-cancer framework.**
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
- **Tier B — citable, versioned snapshots (latency: minutes–days). MACHINERY BUILT.** **GitHub
  releases → Zenodo** versioned DOIs are wired: `CITATION.cff` + `.zenodo.json` (author Tristan D.
  McRae; Apache-2.0) supply the metadata, and `release.yml` (dispatch-only) cuts a tag + Release whose
  notes are the roadmap changelog. *Remaining one-time manual steps* (need your accounts — see
  `deploy/release-doi.md`): flip the Zenodo↔GitHub toggle ON and add your ORCID. Then post the roadmap
  as a **bioRxiv preprint we bump (v2, v3…)** as routes change — a *living preprint / living review*.
  Cadence: cut a release/DOI on any **ready-now-or-flagship route change** (or monthly if anything
  changed); bump the preprint on any change a reader would act on differently.
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
