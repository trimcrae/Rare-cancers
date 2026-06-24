# Attacking an "undruggable" fusion oncoprotein by computation alone: a driver-directed treatment program for EWSR1::NR4A3 extraskeletal myxoid chondrosarcoma

> **ACTIVE MANUSCRIPT — the repo's one paper currently being developed.** This is the single
> publish-to-convince deliverable; everything else in this folder feeds it, records QA for it, or is
> parked/separate-track. Strategy/source-of-truth: [`emc-treatment-strategy.md`](./emc-treatment-strategy.md).
> Folder map: [`README.md`](./README.md).

*Draft manuscript (2026-06). Authors/affiliations TBD. Built entirely from the tracker
(`emc-treatment-strategy.md`) and the in-silico results in `research/modalities/`. Every claim is
sourced or computed; nothing is wet-lab validated, and the paper says so throughout.*

> **Scope (read first).** This paper's **contribution is a method and a driver-directed program**, not
> a ranking of known drugs. Concretely it offers: (1) a reproducible, computation-only framework for
> triaging treatment routes for an orphan fusion cancer that has no models and no market; (2) the
> first systematic computational attack on the EWSR1::NR4A3 **driver itself** — a structural
> "undruggability" call, a reframing of the driver as a *degradation/knockdown* problem, and two
> driver-directed modalities (a NR4A3 degrader and a fusion-junction ASO/siRNA) each with first
> in-silico evidence and an explicit make-or-break experiment; and (3) a falsifiable kill-criterion
> for every route. The near-term **repurposing landscape** (anti-angiogenic-TKI + checkpoint
> inhibitor, trabectedin, carfilzomib + anthracycline) is included as the honest answer to "what could
> help a patient now," but it is **prior, published knowledge**: we present it as the *triage output /
> context* that motivates the driver-directed work, not as this paper's discovery. The structural
> insight the paper is organised around is that the "ready" and "driver-directed" quadrants do not
> overlap — *nothing that attacks the EMC driver is near-term, and nothing near-term attacks the
> driver* — and closing that gap is the program defined here.

> **Status of the experiments (this is a work in progress — stated so reviewers read it correctly).**
> Done and reported here: AlphaFold2/fpocket structural druggability; DepMap surrogate target-expression
> mining; the FET-fusion-addiction class prior (FLI1/Ewing); the ASO transcriptome-wide off-target +
> accessibility screen (first pass, reported as a *negative-leaning result*); HLA population coverage.
> **In progress (pipelines built, results pending):** molecular dynamics of the NR4A3 LBD for cryptic
> pockets; de-novo selective-warhead/binder design; the degrader ternary-complex model. **Deliberately
> left to others (the asks of this paper):** the wet decisive experiments (dTAG fusion-addiction test,
> EMC-tissue IHC/FAP-PET, junction-knockdown viability). We do not claim the in-progress results; we
> claim the framework, the structural call, the class prior, and the ASO screen — and we name exactly
> what is pending and what would prove or kill each route.

> **Living document.** The volatile part of this work — the route *ranking* — is maintained
> continuously in git and in tagged Zenodo releases, deliberately faster than the peer-review cycle
> (rationale + dissemination tiers: `emc-treatment-strategy.md` → Q4). **The journal version's claim
> is the stable core that does not decay: the method, the structural/driver-directed analysis, and the
> falsifiable-kill-criterion framework.** The current route prioritization (§3) is explicitly delegated
> to the living layer so that the paper's contribution never goes stale on a ranking it already
> disclaims. Material changes are logged below; the `method-watch` digest is the automated input.
>
> **Changelog**
> - *2026-06-24* — **Rescope:** contribution reframed from "prioritized portfolio roadmap" to
>   "computation-only **driver-directed** program"; the repurposing portfolio demoted to motivating
>   landscape/triage output (it is prior knowledge, now labelled as such). Title changed. Surrogate
>   language corrected throughout (DepMap "myxoid" = myxoid *liposarcoma*, a tumour EMC is
>   distinguished *from* — so expression reads are pan-sarcoma priors, not EMC-nearest-neighbour
>   claims). FLI1/Ewing relabelled as a **class-level** prior, not NR4A3-fusion-specific support.
>   Added an explicit experiment-status block. Added the junction **ASO/siRNA** route (driver-directed,
>   to-build) + its in-silico evaluation arm and first result (0/5 gapmers transcriptome-clean →
>   specificity bar to clear); added the **delivery** proposal (B7-H3 AOC/siRNA, flagged as contingent
>   on the B7-H3 surrogate). Degrader **ternary-complex** modelling re-primed (open AF3-class tools
>   shipped) and pipeline built.
> - *2026-06* — Initial ranked portfolio (repurposing / degrader / surface-antigen / down-weighted).

## Abstract
Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare sarcoma defined by an EWSR1::NR4A3 (or
TAF15::NR4A3) fusion that produces an aberrant orphan-nuclear-receptor transcription factor. It has no
approved targeted therapy, almost no laboratory models, and no commercial pull. For such a disease the
rate-limiter is not the supply of plausible drugs — those are already in the literature — but a
disciplined attack on the **driver itself**, which is widely treated as undruggable. We present a
**computation-only** program (no wet lab) that does three things. (1) We give a reproducible framework
that places every plausible route on two explicit axes — near-term readiness and driver-directedness —
and show its central structural result: the "ready" and "driver-directed" quadrants are disjoint, so
the field's real gap is a driver-directed route, which is the program's target. (2) We make the first
systematic computational case against the EWSR1::NR4A3 driver: AlphaFold2 + fpocket find the
transactivation domain disordered and the best NR4A3 ligand-binding-domain cavity only borderline
druggable (fpocket druggability 0.495, sub-threshold) — which is *why* we reframe the driver as a
degradation/knockdown problem and define two driver-directed modalities: a **NR4A3 degrader** (removes
the oncoprotein without occupying the collapsed pocket) and a uniquely tumour-specific **fusion-junction
ASO/siRNA** (silences only the fusion transcript). For each we generate first in-silico evidence and
name the decisive wet experiment. (3) We attach a falsifiable kill-criterion to every route. New
computed evidence reported here is honest about its weight: the degrader's make-or-break premise —
that EMC is *addicted* to its fusion — is supported only at the level of a **class prior** (FET-fusion
sarcomas are fusion-addicted; FLI1 in Ewing has gene effect −0.93 with 74% of lines dependent), an
analogy that does **not** establish NR4A3-fusion-specific dependence (the partners differ) and that the
dTAG experiment we hand to others would settle; the ASO's first transcriptome-wide screen returns a
deliberately uncomfortable result (0 of 5 designed gapmers are transcriptome-clean), converting a
"fusion-specific in principle" claim into a measured specificity bar; and DepMap surrogate mining
(sarcoma lines stand in for the absent EMC line) nominates **B7-H3** and **PRAME** as the strongest
surface/antigen targets while down-weighting NY-ESO-1/MAGE-A4 cell therapy and a fusion-junction
vaccine. The near-term repurposing options (TKI+ICI, trabectedin, carfilzomib+anthracycline) are
summarised as prior-art context, not as our contribution. The deliverable is a method plus a
driver-directed work program that hands testable, de-risked hypotheses — and explicit kill-criteria —
to groups with EMC models or patients.

## 1. Background
EMC is defined by rearrangement of *NR4A3*, most often fused to *EWSR1*. The chimeric protein is an
orphan-nuclear-receptor transcription factor: an intrinsically disordered FET-derived transactivation
domain welded to the ordered NR4A3 DNA-binding and ligand-binding domains. Conventional occupancy
pharmacology is precluded — AlphaFold2 (AlphaFold DB) + fpocket find the transactivation domains
disordered and the single best cavity (in the NR4A3 ligand-binding domain) only borderline druggable
(fpocket druggability 0.495, sub-threshold; `nr4a3-structure-assessment.json`). EMC is also a
low-mutational-burden "cold" tumour, ultra-rare (a few hundred cases/year globally), and essentially
absent from public functional-genomics resources (the only models are newly derived patient lines,
e.g. NCC-EMC1-C1, USZ-EMC). It has, in effect, no champion: personalized and fusion-directed therapies
advance in other sarcomas, but EMC must free-ride on that infrastructure rather than fund its own.

Because the driver is widely considered undruggable, the literature on "what to give an EMC patient"
has settled on borrowed, generic agents (anti-angiogenics, trabectedin, an ex-vivo proteasome-inhibitor
hit). Those are real and we summarise them — but they are *prior knowledge*, and none of them attacks
EWSR1::NR4A3. The contribution we set out to make is the missing one: a disciplined, reproducible
computational program that (a) states *where* to push and *what evidence already exists*, and (b)
generates the first in-silico evidence aimed squarely at the driver, together with the falsifiable
experiments that would confirm or kill each idea.

## 2. Methods (reproducible, no wet lab)
All analyses are scripted (`research/modalities/`) and run on public data:
- **Structure/druggability:** AlphaFold2 models (AFDB) + per-residue pLDDT (disorder) + fpocket.
- **Immunogenicity/coverage:** MHCflurry/MHCnuggets junction-neoantigen prediction; Allele Frequency
  Net Database for HLA population coverage (denominator-weighted pooling + Wilson 95% CIs).
- **DepMap surrogate mining (EMC has no line):** CRISPR (Chronos) gene effect for selective
  essentiality and a **fusion-addiction class proxy** (dependency of a *homologous* FET fusion in its
  own driver context); OmicsExpression for candidate-target expression — across sarcoma lineages vs.
  all others, with per-subtype breakdowns. Pipelines self-validate on known dependencies / housekeeping
  genes (ACTB/GAPDH ~11–12 log2(TPM+1) in ~100% of lines).
- **ASO/siRNA sequence screen (CPU-only):** transcriptome-wide off-target scan against human RefSeq
  RNA (GRCh38, 186,185 transcripts; exact + ≤1-mismatch seed-and-extend), ViennaRNA target-site
  accessibility, and sequence-liability filters (`aso_insilico.py`).
- **Literature triage** for clinical signal, with sources tracked.

**On the surrogate, stated up front because it bounds several results.** No EMC cell line exists in
DepMap, so sarcoma lines stand in. Critically, the DepMap **"myxoid" subtype label denotes myxoid
*liposarcoma*, a different tumour** — one that EMC is routinely *distinguished from* (e.g. by NY-ESO-1
positivity in myxoid liposarcoma). We therefore treat all DepMap expression reads as **pan-sarcoma
priors**, not as "EMC-nearest-neighbour" claims, and we do **not** lean on the myxoid-liposarcoma
subtype as a stand-in for EMC. Per-route limitations are restated in §6; the headline caveat is that
nothing here is experimentally validated in EMC.

**How the two-axis bins are assigned (so the rubric is reproducible).** Each route is placed by fixed
rules, not impression. *Axis A (readiness)* — **available now**: an approved agent *and* a published
EMC response/ex-vivo signal; **confirm-gated**: an approved/clinical agent that needs exactly one EMC
target test (one IHC/PET) before use; **to build**: the agent/warhead/construct does not yet exist or
is not deliverable; **down-weighted**: a specific datum argues against it. *Axis B (driver-directedness)*
is a categorical property of the mechanism — **driver-directed** (acts on the fusion product/transcript),
**targeted-indirect** (engages fusion-driven biology at another point), **generic** (disease-agnostic).
We use categorical directedness rather than a numeric "impact" score because the benefit of an untested
agent is not measurable and a granular scale would be false precision.

## 3. The triage landscape (context, not the contribution) — and the gap it exposes

This section is the *output* of the framework applied to the full route list. We foreground it not as a
discovery — the near-term entries are prior, published knowledge — but because its **structure is the
paper's motivating result**: the routes that are *ready* are all *generic*, and the only
*driver-directed* routes are *not ready*. The driver-directed program in §4 exists to close that gap.

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

![EMC treatment routes on two categorical axes: near-term readiness (x) against driver-directedness (y). Repurposed approved drugs are ready but generic; the NR4A3 degrader and junction ASO are the only driver-directed routes but not near-term; targeted-indirect routes (surface antigen, stroma, dependencies) sit between. The top-right — ready and driver-directed — is empty.](figures/portfolio-quadrant.png)

**Figure 2. The triage landscape on both axes.** Graphical form of the table above (regenerate via
`figures/portfolio_quadrant.py`). **That no route occupies the top-right — ready *and* driver-directed —
is the structural problem this paper is organised around;** §4 is the attempt to build a route into
that empty quadrant.

**The near-term landscape (prior knowledge, summarised for the clinician — not our finding).** These
are approved drugs already discussed in the EMC literature; we include them so the paper is not wrong by
omission and so the "what now?" reader is served, but we claim no novelty for them.
- **Anti-angiogenic TKI + checkpoint inhibitor.** The ImmunoSarc trial (sunitinib + nivolumab) reported
  a partial response in an EMC patient (single case within the trial); EMC is unusually TKI-sensitive
  and TKIs remodel the cold tumour microenvironment — a plausible mechanistic synergy. *Evidence weight:
  one trial-embedded responder + a drug-class signal; anecdotal.*
- **Trabectedin.** Approved for soft-tissue sarcoma; its mechanism is displacing fusion transcription
  factors from target promoters (validated in myxoid liposarcoma), mechanistically apt for EMC's
  fusion-TF biology; an EMC responder is reported (trabectedin + radiotherapy, metastatic EMC — *case
  report; full citation to be completed, see §References*). *Evidence weight: single case report.*
- **Carfilzomib + anthracycline (± venetoclax).** The only drug active across two patient-derived EMC
  models in an unbiased ex-vivo screen (Bangerter 2023) — the best *experimental* EMC evidence in the
  whole landscape, though it is ex-vivo and carries no fusion rationale; play it on the existing
  anthracycline backbone. *Evidence weight: ex-vivo, two models.*

## 4. The contribution — a driver-directed program against EWSR1::NR4A3

This is the part of the paper that is new. The structural premise (§1) is that the driver cannot be
drugged by occupancy: the transactivation domain is disordered, and the one ordered cavity (NR4A3 LBD)
scores below the fpocket druggability threshold. That premise is not a dead end — **it dictates the
modality.** If you cannot *occupy* the driver, you can still *remove* it (degrade the protein) or
*silence* it (knock down the transcript). The two driver-directed routes follow directly.

### 4.1 The NR4A3 degrader (flagship)
The fusion retains the ordered NR4A3 ligand-binding domain, so a degrader can recruit it to an E3
ligase and remove the oncoprotein **without needing the collapsed functional pocket** — turning the
borderline-druggability finding from an obstacle into the rationale. Degradation is mechanistically
apt: NOR-1 is constitutively active and its output scales with **expression level** (Munck 2022), so
lowering protein lowers oncogenic activity. The modality has precedent — an NR4A1 PROTAC works (though
it does **not** cross-degrade NR4A3, so NR4A3 needs its own warhead), NR4A3-selective ligand starting
points exist (inverse NOR-1 agonists), and the first FDA-approved PROTAC (vepdegestrant, 2025; *to
verify against the primary approval record before submission*) degrades a nuclear receptor.

**What we add, and its honest weight.** The route's make-or-break premise is that EMC is *addicted* to
its fusion (degrading it kills the cell). We cannot test EMC, so we report a **class-level prior**, and
we are explicit that it is only that: in Ewing sarcoma, where the homologous EWS-FLI1 is the driver,
**FLI1 has gene effect −0.93 and 74% of lines are dependent** (DepMap; `depmap-sarcoma-dependency.json`,
n=27 Ewing lines). This supports *FET-fusion sarcomas being fusion-addicted as a class*. It does **not**
establish NR4A3-fusion-specific dependence: EWS-FLI1 and EWSR1::NR4A3 share only the EWSR1 moiety, and
their DNA-binding partners differ (an ETS factor whose neomorphic GGAA-microsatellite binding drives
much of Ewing's addiction, vs. a nuclear receptor), so the analogy raises the prior without proving the
case. **The decisive experiment we hand to others is the dTAG acute-degradation viability test in EMC
lines; if degrading the fusion does not kill EMC cells, the route dies.**

*Selectivity/safety (design constraint, not a result):* a LBD warhead also degrades wild-type NR4A3
and could hit the paralogues NR4A1/NR4A2 — whose loss carries known liabilities (Nurr1/dopamine-neuron
toxicity; NR4A1+NR4A3 double-loss → leukaemia in mice) — so the design target is **NR4A3-selective,
NR4A1/2-sparing** (7 divergent pocket residues identified as selectivity handles; `nr4a-selectivity.json`).
This is a specification for the warhead, not a demonstrated property.

*What we are running (WIP, pipelines built, results pending — not claimed here):* (i) molecular
dynamics of the NR4A3 LBD to test whether a transient/cryptic druggable pocket opens that the static
AlphaFold model misses — a positive result would directly challenge the "undruggable" prior of §1;
(ii) de-novo selective-warhead/binder design scored against NR4A1/2; (iii) an AF3-class ternary-complex
model of NR4A3–PROTAC–E3 geometry (re-primed now that open AF3-class tools shipped). These are the
substance of the planned **follow-on result paper**; this paper claims the program and the structural
rationale, not their outputs.

### 4.2 The fusion-junction ASO/siRNA (the uniquely tumour-specific route)
The fusion *mRNA* junction exists in no normal transcript, so an antisense oligonucleotide (or siRNA)
spanning it silences **only** the fusion — sparing wild-type NR4A3 *and* EWSR1. This is the one truly
tumour-specific route (the protein degrader cannot be, since the druggable LBD is shared); 5
fusion-specific gapmers are designed (`junction_aso.py`). It is lower on near-term feasibility, not in
principle: the EMC junction is **GC-rich (~75–81%)**, outside the usual comfort zone, and **tumour
delivery is the unsolved problem** for oligonucleotides generally. Degrader and ASO are
**complementary** — potent-but-not-fusion-specific vs. fusion-specific-but-delivery-limited.

**In-silico evaluation arm (runs without a wet lab; its questions are sequence/RNA, not structure;
`aso_insilico.py`):** (i) a **transcriptome-wide off-target screen** — every candidate's target window
is scanned against the whole human RefSeq transcriptome (GRCh38) for exact and ≤1-mismatch matches
(seed-and-extend), because hybridization-dependent off-target RNase-H cleavage is the dominant
gapmer-toxicity mode and "not a perfect complement of the two parents" is too weak a specificity bar;
(ii) **target-site accessibility**, folding the fusion mRNA (ViennaRNA partition function) to rank
candidates by the single-stranded probability of their RNase-H site (potency); (iii) **sequence-liability
filters** (CpG/TLR9 immunostimulation, G-quadruplex, homopolymer runs); and (iv) an **siRNA seed-region
off-target** module, reporting each candidate's seed 7-mer, whether the seed *straddles the junction*
(a fusion-unique seed, the design goal), and its transcriptome occurrence count. The output is a ranked,
off-target-screened shortlist across **both** chemistries — it advances *specificity and potency-site
selection only*; it does **not** address delivery.

*Result (first pass, reported as a negative-leaning result — this is the screen working, not a flaw).*
Screening the 5 fusion-specific gapmers against the full human RefSeq transcriptome (186,185 transcripts)
returns: **none is transcriptome-clean** — every candidate has at least one near-complementary off-target
at ≤1 mismatch (best candidate: 0 exact but 8 one-mismatch hits); the junction sites are **poorly
accessible** (best ≈0.35 unpaired probability); they are **GC-rich (~75%)**; and only **2 of 5** place
the RISC seed across the junction. The "not a perfect complement of the two parents" heuristic passes all
5; the stricter transcriptome-wide bar fails all 5. The actionable read is that a viable oligo here needs
**wider design latitude than the canonical 16-mer at the canonical breakpoint** — longer/shifted gapmers
or a junction-in-seed siRNA — pushed until the ≤1-mismatch off-target count reaches zero on an
accessible, lower-GC site. We report this as a *result* because it converts an untested "fusion-specific
in principle" claim into a measured specificity bar the eventual construct must clear.

**Delivery (the route's real gate — a proposal, explicitly contingent).** No oligonucleotide is yet
approved for *targeted systemic delivery to a solid tumour*: the solved cases are liver (GalNAc→ASGPR;
inclisiran-class), local CNS (intrathecal; nusinersen), and local eye. EMC is none of these, so delivery
— not sequence design — gates this route. EMC does have an unusually clean handle that falls out of our
own surface-target analysis: **B7-H3 (CD276)** is near-universally expressed across sarcoma lines and
internalises (§5), making an **anti-B7-H3 antibody–oligonucleotide conjugate (AOC)** — or a
B7-H3-decorated lipid nanoparticle — a logical EMC delivery vector. **We flag this proposal as
contingent:** it inherits the B7-H3 *surrogate* caveat (§5/§6) and is unproven for EMC; it is offered so
a delivery lab gets a specific starting design rather than "good luck," not as a solved problem.
Corollaries: prefer an **siRNA chassis** (RISC has the mature conjugate/LNP toolbox and approved
precedents); expect EMC's **myxoid extracellular matrix** to be a penetration barrier (a
stroma-normalising adjunct is a reasonable co-design). **The decisive biology gate comes first and is
delivery-independent:** lipofected junction-knockdown must kill EMC cells before any delivery campaign is
justified — the ASO's analogue of the degrader's dTAG gate, and another wet experiment we hand to others.

## 5. Targeted-indirect routes that the framework promotes or kills (surrogate-graded)
These are not driver-directed, but the framework's job is to grade them honestly on data we can compute.
All expression reads are **pan-sarcoma surrogate priors** (no EMC line; see §2/§6), not EMC facts.
- **B7-H3 (CD276) — promoted (confirm-gated).** Expressed in **99% of sarcoma lines** (DepMap mean 5.73
  log2(TPM+1)); on top of 97% pan-STS by IHC. Expression is present across subtypes but **not uniformly
  "high"** — the myxoid-liposarcoma subtype reads 4.4, *below* the panel mean and the lowest of the
  subtypes measured — so we state it as *near-universal positivity*, not *uniformly high*. This supports
  the antibody-drug conjugate ifinatamab deruxtecan, a B7H3×CD3 bispecific, or B7-H3 CAR-T, and supplies
  the internalising handle the §4.2 delivery proposal borrows. *Gate: EMC-tissue B7-H3 IHC.*
- **PRAME — promoted as best-of-the-CTAs (confirm-gated), with a stated caveat.** Expressed in **53% of
  sarcoma lines** overall. Its highest subtype reads are in synovial (7.2) and myxoid *liposarcoma*
  (7.6) — but because myxoid liposarcoma is **not** EMC (§2), we do **not** treat that 7.6 as an
  EMC-proximal value; the defensible claim is the *relative* one: PRAME ≫ MAGE-A4/NY-ESO-1. Cell lines
  also epigenetically silence cancer-testis antigens, so these are **lower bounds**. → the PRAME ImmTAC
  brenetafusp (tumour-agnostic basket) or PRAME-directed cell therapy. *Gate: EMC-tissue PRAME IHC.*
- **FAP-targeted radioligand therapy — plausible (confirm-gated).** EMC's myxoid stroma is a candidate;
  cell lines under-represent stromal FAP (no CAF compartment), so the modest cell-line FAP does not
  weaken the case; the tracer is also diagnostic. *Gate: EMC FAP-PET avidity.*
- **CD56/NCAM — left plausible-but-unsupported.** EMC's neuroendocrine phenotype (synaptophysin/INSM1⁺)
  suggests CD56, but the surrogate disagrees (myxoid-liposarcoma subtype CD56 ≈ 0); we carry it as
  unconfirmed rather than promote it, and flag the surrogate–phenotype mismatch openly.

**Down-weighted with data/logic.**
- **TCR-T / ImmTAC against NY-ESO-1 or MAGE-A4:** EMC is CTA-low (NY-ESO-1 5%, MAGE-A4 7% of sarcoma
  lines; NY-ESO-1 is used to distinguish myxoid liposarcoma *from* EMC) → the afami-cel/letetresgene
  port is weak; only a PRAME⁺ subset is attractive.
- **Synthetic-lethal / BRD9–ncBAF:** a transfer prior from EWS-FLI1's prion-domain BAF retargeting, but
  DepMap shows BRD9/ncBAF is **not** selectively essential in sarcoma — not even in Ewing — and BET/CDK
  targets show no selectivity window. No shortcut; a de-novo EMC CRISPR screen would be required.
- **Fusion-junction vaccine:** the junction is largely self-sequence in a cold tumour (weak immunogen),
  and the economics favour a tumour-agnostic platform; the HLA-coverage analysis is retained only as
  input to TCR-T/ADC eligibility.

## 6. What would prove or kill each candidate (the falsifiable core)
The value of this paper to a reader is the decisive next experiment and the kill-criterion per route —
including for our own driver-directed flagship.

| Candidate | Decisive experiment | Kill-criterion |
|---|---|---|
| NR4A3 degrader (flagship) | dTAG acute-degradation viability in EMC lines | degrading the fusion doesn't kill EMC cells (EMC not fusion-addicted) |
| Junction ASO/siRNA (flagship) | in-silico pre-screen (`aso_insilico.py`: zero ≤1mm transcriptome off-targets + accessible site) → lipofected junction-knockdown vs scrambled in EMC lines | no fusion knockdown / no kill, irreducible off-targets, or undeliverable to tumour |
| TKI + ICI; trabectedin; carfilzomib+anthracycline | prospective EMC cohort / case series | fails to reproduce in EMC patients |
| B7-H3 ADC / CAR-T; FAP-RLT | EMC tissue IHC / FAP-PET, then the agent | EMC is target-negative |
| PRAME ImmTAC/CAR | EMC PRAME IHC; brenetafusp basket enrolment | primary EMC PRAME-negative |
| Synthetic-lethal/BRD9 | genome-wide CRISPR screen in EMC lines | (already down-weighted by DepMap) |

## 7. The in-silico work program (what we are running, and what others can extend)
Because we attack the actual driver only computationally, we define a runnable program and state its
status honestly (done / running / planned), so the contribution is the program plus the completed
pieces, not unfinished results:
- **Done:** structural druggability call (§1); FET-fusion-addiction class prior (§4.1); ASO
  transcriptome off-target + accessibility screen (§4.2); surrogate target-expression mining (§5); HLA
  coverage.
- **Running (pipelines built; the substance of the planned result paper):** (i) **molecular dynamics of
  the NR4A3 LBD** to test for a transient/cryptic druggable pocket the static model misses — a positive
  result would overturn the "undruggable" prior; (ii) **de-novo selective warhead/binder design**
  (structure-based generative small-molecule design; or RFdiffusion→ProteinMPNN→AF2 for a binder),
  scored for selectivity against NR4A1/NR4A2; (iii) the **AF3-class ternary-complex** model.
- **Watching (method-watch trigger table, `method-watch.md`):** a usable in-silico tumour-delivery
  predictor (would let us score the B7-H3-targeted junction-siRNA and re-grade the ASO gate); a
  virtual-cell/perturbation model that predicts a held-out knockdown phenotype (would substitute in
  silico for the dTAG fusion-addiction experiment that gates the degrader).
Scripts and a cloud-GPU pipeline are provided. The MD is the highest-value single GPU experiment; the
ASO off-target/accessibility screen is the highest-value experiment that needs no GPU at all and is
already done.

## 8. Limitations
Nothing here is experimentally validated in EMC. DepMap analyses use **sarcoma lines as a surrogate**
(no EMC line exists), and the DepMap "myxoid" label is myxoid *liposarcoma* — a tumour EMC is
distinguished *from* — so expression reads are pan-sarcoma priors, not EMC-proximal values, and we do
not lean on the myxoid subtype as an EMC stand-in. Cell lines silence cancer-testis antigens (CTA reads
are lower bounds) and under-represent stromal FAP; AlphaFold yields a single static model (cryptic
pockets unseen — the MD experiment in §7 is the test of exactly this); predicted MHC binding and docking
scores are screens, not proof. The fusion-addiction result is a **class-level analogy** (FLI1/Ewing),
not EMC data, and an imperfect one — EWS-FLI1 and EWSR1::NR4A3 share only the EWSR1 moiety while their
DNA-binding partners differ — so it supports FET-fusion addiction as a *class* property rather than
proving NR4A3-fusion dependence; the dTAG experiment (§6) is what would settle it. The ASO first-pass
result is negative-leaning by design (it sets a specificity bar, it does not deliver a construct), and
the B7-H3 delivery proposal is contingent on the unvalidated B7-H3 surrogate. HLA/expression statistics
are population/line priors, not the individual patient. These are stated so the work is read as method +
driver-directed program + evidence-synthesis with explicit kill-criteria — not as demonstrated efficacy.

## 9. Why pursue an ultra-rare cancer — and how to make a candidate worth developing
The hardest objection to any EMC drug program is economic: EMC is too rare to generate commercial or
translational pull on its own, so even a well-evidenced candidate risks never being made. We note two
mitigations to be *built into* how a lead is advanced — and we flag them as directions, not as analyses
completed in this paper. First, **EMC's clean, single-driver biology makes it an unusually good
proof-of-concept indication** for a mechanism hard to validate in messier, multi-driver common tumours:
the fusion is truncal and near-universal, so an effect is causally interpretable. Second, **each lead
here has a plausible path to common cancers** that should be assessed alongside the EMC case to widen
the addressable population and the incentive to develop it — the NR4A receptor family (NR4A1/2/3) is
implicated across leukaemia, melanoma, prostate, breast and colorectal cancer (and the "degrade an
undruggable nuclear-receptor TF via its retained LBD" *platform* is itself transferable); B7-H3, PRAME
and FAP are already pan-cancer targets; and the repurposed agents carry other-cancer evidence. **These
broader-indication claims are stated as hypotheses to be substantiated with the same public-data
pipelines used here (which already cover all lineages); they are not computed in this draft.** The
recommendation is that any candidate which firms up be accompanied by a **broader-indication analysis** —
positioning EMC as the entry point, not the endpoint — and we mark that analysis as future work rather
than asserting its result.

## 10. Conclusion
For an orphan cancer with no models and no market, a computation-only program can do the thing the field
most lacks: take the driver seriously. We give a reproducible framework whose central result is that no
*ready* route attacks the EWSR1::NR4A3 driver, and we define the driver-directed program that aims to
fill that gap — a NR4A3 degrader (rationalised by the very structural finding that rules out occupancy,
its make-or-break fusion-addiction premise supported only as a class prior and explicitly gated on a
dTAG test) and a uniquely tumour-specific fusion-junction ASO/siRNA (whose first transcriptome-wide
screen sets a concrete specificity bar and whose delivery we propose but do not solve). Alongside, the
framework grades the borrowed near-term options (TKI+ICI, trabectedin, carfilzomib+anthracycline) as the
honest stopgap they are, and promotes B7-H3 and PRAME as the strongest surface/antigen targets on
surrogate data. Every route, including our own flagship, carries an explicit decisive experiment and
kill-criterion. We invite groups with EMC models or patients to run them.

## References (verified in the underlying analyses; collate to journal format; run verify-refs before submission)
NR4A3/EMC biology and EWSR1::NR4A3 → PPARG (PMC4429309); EMC neuroendocrine phenotype / INSM1
(Mod Pathol 2017; PMID 36563884); patient-derived EMC line NCC-EMC1-C1 (Human Cell 2025).
Structure: AlphaFold2 (Jumper 2021, *Nature*, 10.1038/s41586-021-03819-2) / AFDB; fpocket
(Le Guilloux 2009). Degrader: NOR-1 druggability & inverse agonists (Munck 2022, PMC9542104);
NR4A ligands (PMC11267491); vepdegestrant first approved PROTAC (Arvinas 2025 — **primary approval
record to be cited/verified before submission**). Synthetic-lethal: Boulay *Cell* 2017
(10.1016/j.cell.2017.07.036; EWSR1 prion-domain BAF retargeting); Brien *eLife* 2018 (BRD9 degrader).
Immunotherapy: afami-cel (Tecelra) approval 2024; NY-ESO-1 in sarcoma (PMC3518519); ImmunoSarc /
sarcoma IO (ASCO EDBK 2024); brenetafusp PRAME ImmTAC (Immunocore 2024). EMC-specific clinical signal:
sunitinib response in EMC (PMC3534218); trabectedin + radiotherapy long-term response in metastatic EMC
(**case report — full bibliographic identifier (PMID/DOI) outstanding; OPEN reference item, must be
completed before submission**). Surface targets: B7-H3 in soft-tissue sarcoma (PMC11523878); FAPI
radioligand therapy in sarcoma (Clin Cancer Res 2022). Repurposing/ex-vivo: carfilzomib (top ex-vivo
hit) ± anthracycline/venetoclax in two patient-derived EMC models (Bangerter et al., *Human Cell* 2023;
PMID 36316541; full text CI-verified, `fact-check-log.md`). Fusion-junction ASO (5 fusion-specific
gapmers; RNase-H mechanism): `junction_aso.py` / `novel-modalities.md` §3.2; ASO in-silico evaluation
(transcriptome off-target screen, ViennaRNA target-site accessibility, sequence-liability filters):
`aso_insilico.py`. Data: DepMap 24Q4 (CRISPR + OmicsExpression); AFND (HLA); human RefSeq RNA
GRCh38.p14 (ASO off-target screen).
*(Full citations live in the per-route memos; verify-refs before submission. Outstanding reference items
are flagged inline above so they are not lost.)*
</content>
</invoke>
