> **Role:** framing/strategy memo — feeds the positioning decision record
> ([`nr4a3-degrader-paper-positioning.md`](./nr4a3-degrader-paper-positioning.md)) and the lead manuscript
> ([`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md)). Proposes elevating the pan-NR4A / ex-vivo
> CAR-T application from "contingency" to a deliberate second pillar, and re-framing the whole paper
> around **NR4A-family druggability** to target a higher-tier journal (Nature Computational Science /
> ACS Central Science). Not separately submitted. Written 2026-07-08.

# Leveraging the *non-selective* degrader for ex-vivo CAR-T — and re-framing the paper around NR4A-family druggability

## TL;DR
- **Yes — the "non-selective" degrader is not a failure mode, it is a second product.** A **pan-NR4A**
  degrader applied **ex vivo** during CAR-T manufacturing is a chemical route to the landmark **NR4A
  triple-knockout that reverses T-cell exhaustion** (Chen et al., *Nature* 2019). The exact property that
  is a *liability* for the in-vivo cancer drug (hitting NR4A1/2/3 together) is the *desired* property here.
- **Ex-vivo use dissolves the toxicity constraint that motivated the entire selectivity program.** The
  reasons we must be NR4A3-selective in vivo — NR4A1/NR4A3 loss → AML (Mullican 2007), NR4A2/Nurr1 loss →
  dopaminergic toxicity — are **systemic, chronic-exposure** arguments. Ex vivo you dose the T-cell product
  transiently in a dish, wash it out, and infuse cells; there is no chronic systemic NR4A blockade in the
  patient. So the *hardest* thing this paper does (achieve intra-family selectivity) is **not even required**
  for the CAR-T application — a strictly easier design target.
- **Cost to add it: near zero new compute.** The family-wide **state-matched selectivity matrix already
  exists** (§2.4 of the paper). "Pan-NR4A" is simply the *conserved-pocket-engaging* readout of the same
  matrix — the opposite cell from the NR4A3-selective one. A pan-NR4A candidate is a **cheap matrix/generation
  readout**, not a new GPU program. This is squarely the "add a new axis of evidence for near-zero cost"
  breadth-first move the North Star rewards.
- **Yes — it raises the achievable journal tier, but only *with* the reframe.** The CAR-T application alone
  doesn't lift a rare-cancer degrader paper into a top journal. What lifts it is the **general claim it
  licenses**: *the NR4A family — canonically "undruggable" orphan nuclear receptors — harbours a dynamically
  druggable cryptic pocket, and one computational framework tunes a degrader across the family: paralogue-
  selective for NR4A3-driven cancers at one pole, pan-family for CAR-T de-exhaustion at the other.* That is a
  **methods + broad-impact** story that fits **Nature Computational Science** and **ACS Central Science**;
  "an NR4A3 degrader for a rare sarcoma" is not.

---

## 1. Why the ex-vivo CAR-T angle is real, not a stretch

### 1.1 The biology is a landmark result, and it points the *opposite* way from our cancer drug
NR4A1/2/3 are the transcription factors that **enforce CD8⁺ T-cell exhaustion** downstream of chronic
TCR/NFAT signalling. The defining experiment: CAR-T cells with **all three NR4A genes knocked out** show
markedly **restored effector function, reduced exhaustion-marker expression, and tumour regression** in a
solid-tumour model where wild-type CAR-T fails (**Chen, López-Moyado, … Rao, *Nature* 2019**, "NR4A
transcription factors limit CAR T cell function in solid tumours"). The effect is a **redundant-family**
effect — single or double knockouts are substantially weaker than the triple — which is exactly why a
**pan-NR4A** agent, not an NR4A3-selective one, is what this application needs. (Companion exhaustion-axis
work — TOX, NFAT-without-AP-1 — puts NR4A in a validated, much-studied network, so this is not a lone paper.)

For the paper this is a striking narrative pivot: **the selectivity we spend the whole paper engineering is
precisely what you throw away for the immunotherapy use.** Same pocket, same framework, opposite tuning. That
symmetry ("one method, both poles of the selectivity axis") is the kind of conceptual payload high-tier
editors reward, and we already have the machinery to demonstrate both poles.

### 1.2 Ex vivo removes the constraint that justified the hard part of the paper
The paper's selectivity effort exists to avoid **systemic** harms of chronic pan-NR4A blockade:
- NR4A1 + NR4A3 are **myeloid tumour suppressors** → combined loss drives **AML** (Mullican 2007);
- NR4A2/Nurr1 loss carries **dopaminergic/CNS** liability.

Both are **chronic, systemic-exposure** arguments. The ex-vivo CAR-T workflow is the opposite regime:
1. transduce/expand patient (or allogeneic) T cells;
2. **transiently** expose them to the pan-NR4A degrader *in the culture dish* during manufacturing;
3. **wash out** the compound; infuse the cells.

There is no persistent pan-NR4A degrader in the patient's marrow or brain — the toxicity that mandates
selectivity **never occurs**. A degrader is in fact well-suited to this: degradation is catalytic and its
effect **persists after washout** (the protein stays low until resynthesised), giving a durable
"reprogramming" pulse without a genetic edit. This is the honest, defensible version of the claim — it is a
**manufacturing additive**, adjacent to transient-mRNA / small-molecule conditioning approaches already used
in cell-therapy process development, not a systemic drug.

**Honest bounds (state them in the paper, don't hide them):**
- The in-silico work we have characterises **pocket druggability + binder/degradation-geometry feasibility**,
  not cellular exhaustion-reversal — that endpoint is a **wet-lab claim we cannot and do not make**. The
  paper contributes the **chemical-feasibility** half (a pan-NR4A degrader is *designable* from the same
  pocket); the functional half is explicitly future wet-lab work.
- "Transient / washes out" is the intended use, but **degradation persistence cuts both ways** — the
  reprogramming pulse is a feature, but residual pan-NR4A suppression in the infused product is a real
  parameter to characterise (dose/exposure/washout window). Flag it as a design variable, not a solved point.
- We are not claiming novelty of the *biology* (Chen 2019 owns that). We claim the **chemical enablement**:
  the field has used **genetic** triple-KO; a washable **pan-NR4A degrader** is a drug-like, off-the-shelf,
  dose-tunable alternative that the same druggable-pocket finding makes conceivable.

### 1.3 What it costs us to add (and why it's a breadth-first "default yes")
- **Framework:** already built. The **state-matched opened-pocket ensembles for NR4A1/2/3** and the
  **family selectivity matrix** (paper §2.4) are the entire apparatus. Pan-NR4A = the **conserved-pocket-
  engaging** cell (engage the ~30% of pocket residues that are *invariant* across paralogues, avoid the
  divergent handles) — the mirror image of the NR4A3-selective cell we already read out.
- **New compute:** at most a **cheap** readout — re-rank the existing matrix/de-novo poses for pan-NR4A
  engagement, or one small pocket-conditioned generation run *conditioned on the conserved residues instead
  of the divergent handles*. This is inside the **autonomy threshold** ("proceed on cheap in-silico steps
  without asking") and is a **new axis of evidence** (breadth-first "default yes"). It is **strictly easier**
  than the selective design (no selectivity budget to satisfy), so a positive readout is the expected case.
- **Deliverable to bank before claiming it:** a demonstrated **pan-NR4A candidate** from the matrix/generator
  that engages the conserved pocket residues across all three opened ensembles — the concrete artefact that
  turns "the framework *supports* a second mode" into "the framework *produces* both modes."
  **DONE (2026-07-08, zero new compute):** re-read the existing state-matched matrix + de-novo funnel S3
  results ([`../modalities/nr4a3-pan-readout.json`](../modalities/nr4a3-pan-readout.json); report jobs
  28935050401 / 28935054929). The pan-NR4A cell is populated at **both** tiers: (i) the repurposed library
  has an essentially **equipotent** tri-paralogue engager (dG −8.40/−8.41/−8.80), and (ii) the de-novo
  funnel's own `confirmed_nonselective` rejects contain **two developable pan-NR4A binders** — `denovo_106`
  (QED 0.78 / SA 3.8 / 5 handle contacts, the lead) and `denovo_86`. So one generative campaign yields both
  poles of the axis: NR4A3-selective warheads *and*, in its non-selective by-catch, developable pan-NR4A
  binders. Folded into paper §3. Docking-tier screening priors (same weight as the selective docking leads),
  no molecule synthesized. **Now upgraded to a *designed* result (§3.5):** a conserved-core-ranked campaign
  makes pan the dominant docking outcome (4/7 pan, 0 selective) with a clean lead `denovo_9` — so the pan pole
  no longer rests only on the by-catch.

---

## 2. Does it raise the journal tier? Yes — but the *reframe* is what does the lifting

The CAR-T application is the **hook**, not the mechanism. On its own, "we also note a pan-NR4A degrader could
help CAR-T" is a paragraph, not a tier change. The tier change comes from the **general claim the two poles
jointly license**, which is what NR4A-family druggability lets us assert:

> **A textbook-"undruggable" orphan nuclear-receptor family is dynamically druggable, and one cryptic-pocket
> framework designs degraders across its entire selectivity axis — from a paralogue-selective agent for
> NR4A3-driven cancers to a pan-family agent for reversing CAR-T exhaustion.**

That sentence is a **methods + impact** contribution with **two disease areas** (rare oncology *and*
immuno-oncology) served by **one computational result**. That is the profile these journals select for:

- **Nature Computational Science** — rewards a *computational method/finding* with demonstrable reach across
  problems. Our load-bearing novelty is computational (first NR4A3 pocket-dynamics + druggability calibration;
  the family-wide **state-matched** selectivity matrix that removes the opened-vs-static confound; the
  decoy-calibrated selectivity null). The two application poles show the method **generalises**. Good fit.
- **ACS Central Science** — rewards chemistry of *central* significance across sub-fields. "Making an
  undruggable receptor family druggable, and steering selectivity by design" is a central-chemistry thesis
  with an immunotherapy payoff. Good fit.

**Reality check (so we don't over-promise the tier):** these are still selective journals and our result is
**in-silico, no molecule synthesised**. The honest positioning is *"a rigorous, calibrated computational
druggability + design framework"* — which is publishable at this tier **as a computational paper**, provided
we (a) keep every claim at its true weight (the paper already does this well), and (b) don't let the CAR-T
hook drift into an unearned functional claim. The reframe **maximises the achievable tier**; it does not
guarantee acceptance. Fallback ladder if it doesn't land: *JACS Au / Chemical Science → J. Med. Chem. /
J. Chem. Inf. Model. → ChemRxiv preprint* (the preprint goes up regardless, per the operating regime).

---

## 3. The reframe: "the NR4A family is more druggable than we thought"

This is the strongest available framing and — importantly — **it is already latent in the paper's own
results.** We are re-weighting emphasis, not inventing a claim. Everything below is supported by material
already in [`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md):

| Ingredient the reframe needs | Where the paper already has it |
|---|---|
| The family is *canonically* undruggable | Abstract + §1: occluded Nurr1 crystal, no NR4A3 structure, "ligand-independent" reputation |
| …but experimentally ligandable | §1: Zaienne 2022 low-µM inverse agonist; Safe 2025 selective analogues |
| A *dynamically* druggable cryptic pocket exists | §2.2: metad breathing → unbiased **release run** metastable + druggable ~24% of frames |
| Orthogonal, independent corroboration | §2.1: **PocketMiner** flags the same site from the apo structure |
| The finding generalises across the family | §2.4: **same metadynamics run on NR4A1 and NR4A2** → state-matched opened pockets for all three |
| Selectivity is *programmable*, not fixed | §2.3/§2.7: pocket is the **most paralogue-divergent zone** of the LBD → tunable |
| Two opposite application poles | Selective (EMC/AciCC/NR4A-sarcomas) **and** pan-NR4A (CAR-T) |

So the reframe is a **promotion of emphasis**, executed as:

### 3.1 Proposed retitle (family-first, method-first)
Current: *"Computational design of a selective NR4A3 degrader: opening a cryptic pocket in a
'ligand-independent' nuclear receptor."*

Reframed options (family-level, dual-pole):
- **"The NR4A nuclear-receptor family is druggable: a cryptic-pocket framework for tunable degraders, from
  paralogue-selective oncology to pan-family CAR-T de-exhaustion."**
- **"Programmable druggability of an 'undruggable' nuclear-receptor family: one cryptic pocket, from a
  selective NR4A3 degrader to a pan-NR4A CAR-T enhancer."**

The NR4A3-selective degrader remains the **deepest-validated result** (it carries the FEP, the ternary, the
decoy-null lead `denovo_401`); the family framing is the **container** that gives it reach.

### 3.2 Abstract restructure (opening move)
Lead with the **family-level druggability reversal**, then descend to the two design modes:
1. *Claim:* NR4A (NR4A1/2/3) — textbook undruggable orphan NRs — are dynamically druggable; we show a
   cryptic orthosteric pocket that breathes open (metad + **unbiased** release run), corroborated by an
   independent predictor (PocketMiner), calibrated against an NR panel.
2. *Generalisation:* the **same** cryptic-pocket dynamics on all three paralogues yields state-matched
   opened pockets and a **programmable selectivity axis** (the pocket is the family's most divergent zone).
3. *Pole 1 (selective):* a decoy-null-calibrated, FEP-supported **NR4A3-selective** degrader design for
   NR4A3-driven cancers (EMC, AciCC, NR4A-rearranged sarcomas).
4. *Pole 2 (pan-family):* the mirror design mode — a **pan-NR4A** degrader — as a chemical, washable,
   ex-vivo route to the exhaustion-reversing NR4A triple-KO for **CAR-T** (Chen 2019), where selectivity is
   unnecessary and ex-vivo use removes the systemic-toxicity constraint.
5. *Weight:* in-silico design + feasibility; no molecule synthesised; functional CAR-T reversal is future
   wet-lab work.

### 3.3 New/expanded section to add
- Promote the pan-NR4A mode from the current one-line "second design mode" (§3, and the abstract's clause)
  into a **short dedicated subsection** ("§3.x A pan-NR4A design mode for ex-vivo CAR-T de-exhaustion"),
  containing: the Chen-2019 rationale, the **ex-vivo-obviates-selectivity** argument (§1.2 above), the
  conserved-pocket readout of the matrix, and the honest bounds (§1.2). Anchor it to a **pan-NR4A candidate
  readout** (§1.3) once run.
- Keep the AML **anti-target** (NR4A1+NR4A3) analysis exactly where it is — it now does double duty: it is
  the safety bound for the selective drug *and* the reason the CAR-T agent must be **pan**-NR4A (all three),
  not the AML-like NR4A1+NR4A3 pair. The matrix already designs *away* from that cell.

### 3.4 What NOT to do (integrity guardrails)
- **Do not** claim demonstrated exhaustion reversal, T-cell functional data, or a synthesised pan-NR4A
  molecule. The contribution is **chemical feasibility + framework generality**.
- **Do not** let the family framing dilute the honest, hard-won caveats on the NR4A3-selective result
  (release-frame-specific decoy-null clearance; single-trajectory GB-implicit MD; ternary adds no selectivity;
  the FEP replicate error bars in progress). The reframe **adds a container**; it does not soften any weight.
- **Do not** headline the CAR-T pole over the NR4A3-selective pole in the *results* — the selective design is
  the validated core; CAR-T is the reach-extending second mode. Family-first in the *title/abstract*,
  selective-first in the *depth of evidence*.

---

### 3.5 Status of the "make pan a design objective" step — DONE 2026-07-08 (trimcrae go-ahead)
Originally `campaign=pan` was **label-only** (`nr4a3_denovo.py` conditioned DiffSBDD on the full pocket
identically for both campaigns). We made the code change — pan now scores `denovo_promise` by **conserved-core
contact** (residues 411/481/485) so generation ranks conserved-core engagers to the top and into the dock —
then ran the full **generate → dock → report** cycle (runs 28936737785 / 28937575876 / 28938420060; aggregate
~$3–6, under the gate). **Result: the pan pole is now a *designed* result, and a stronger one.** Designing for
the conserved core **flips the docking census to pan-NR4A-dominant (4/7 docked, 0 NR4A3-selective)** — the
mirror image of the selective campaign — and yields a **clean** lead where the by-catch had none: **`denovo_9`**
(docking dG NR4A3/NR4A1/NR4A2 = −7.69/−7.31/−7.40; 3/3 conserved-core residues; PAINS/BRENK/NIH-
and reactive-liability-clean; MW 335 / logP 1.74 / QED 0.64). **Endpoint multi-snapshot MM-GBSA
(run 28938839827, ~$0.5) then confirmed tri-paralogue engagement one tier above docking** — ΔG
−28.3/−23.9/−20.7 kcal/mol for NR4A3/1/2, all favorable; the +4.44 NR4A3 lean is within noise (SD 5.47,
margin − SD < 0, far below the §2.5 decoy null), so **no de-noising-robust selectivity — a confirmed pan
binder** (not equipotent, but engages all three). Data:
[`../modalities/nr4a3-pan-readout.json`](../modalities/nr4a3-pan-readout.json) → `pan_designed_campaign`.
Folded into paper §3 + the abstract. No molecule synthesized; the honest-weight bounds of
§1.2 (function not shown; ex-vivo persistence a parameter) are unchanged.

## 4. Recommended next actions
1. **Cheap, default-yes now:** run the **pan-NR4A readout** — re-rank the existing family matrix / a small
   conserved-residue-conditioned generation for a candidate that engages the invariant pocket residues across
   all three opened ensembles. Banks the artefact the reframe leans on. (Within the autonomy threshold.)
2. **Framing:** fold §3 of this memo into [`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md) (retitle,
   abstract restructure, new pan-NR4A/CAR-T subsection) and record the tier target in
   [`nr4a3-degrader-paper-positioning.md`](./nr4a3-degrader-paper-positioning.md) (promote pan-NR4A from
   "contingency" to "second design pillar"; set journal target Nat Comput Sci / ACS Cent Sci with the
   fallback ladder).
3. **Outreach:** the CAR-T pole widens the outreach list — add **NR4A/exhaustion immunology labs** (the Rao
   group's network) and **cell-therapy process-development** contacts to
   [`nr4a3-degrader-outreach-emails.md`](./nr4a3-degrader-outreach-emails.md).
4. **Hold the line on weight:** everything above is emphasis + one cheap readout; no claim exceeds what the
   in-silico work supports.

## References (already in the lead paper unless noted)
- Chen J, López-Moyado IF, … Rao A. **NR4A transcription factors limit CAR T cell function in solid tumours.**
  *Nature* 2019;567:530–534. (The pan-NR4A / exhaustion landmark.)
- Mullican SE, et al. NR4A (Nur77/Nurr1/NOR-1) as myeloid tumour suppressors (loss → AML). 2007. (AML
  anti-target bound.)
- Zaienne 2022 (NOR-1/NR4A3 druggability evaluation); Safe 2025 (NR4A3-selective analogues); de Vera 2019
  (Nurr1 breathing pocket); PocketMiner (Meller et al., *Nat Commun* 2023). — as cited in the lead paper.
