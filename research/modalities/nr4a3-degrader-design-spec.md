# NR4A3 degrader — in-silico design spec (runnable when compute is available)

> **✓ Numbers verified (2026-06-25).** The pocket↔residue attribution below (**fpocket Pocket 5,
> druggability 0.495, residues 406–534**, holding all 7 selectivity handles) was regenerated from the
> count-fixed, data-derived pipeline and reproduces the original values exactly. (A same-day claim that
> these were corrupted by an "off-by-one" and that the orthosteric pocket was really ~0.026 was itself a
> bug in an interim enumeration script — retracted; see `ASSUMPTIONS.md`.) The orthosteric pocket is
> **borderline-druggable at 0.495** — just under the conventional 0.5 cutoff — which is exactly why the
> cryptic-pocket MD below matters: it tests whether breathing pushes it ≥0.5.

**Purpose.** The NR4A3 (NOR-1) degrader is the only route that attacks EMC's actual driver, and its
one missing piece — a selective NR4A3 warhead — is a **pure in-silico design problem**. This is the
spec for that design campaign: precise inputs, the pipeline, what runs on CPU now vs. needs a GPU,
and what output is publishable. It is the "de-novo binder design" arm of the in-silico work program
(`emc-treatment-strategy.md`). Nothing here is run yet — it is *prepared* so it can be executed the
moment compute/tooling is in hand.

## Selectivity & safety rationale (why selectivity is non-negotiable)
A LBD-binding degrader removes any NR4A protein whose LBD it engages, so two distinct selectivity
questions arise — only one is solvable by a small molecule.

**(a) NR4A3 vs NR4A1/NR4A2 — SOLVABLE and mandatory.** The paralogues have important normal roles, so
off-target degradation has real, *characterized* toxicity (known from NR4A biology independent of
EMC — knockout mice and family genetics, not from the rare tumour):
  - **NR4A2/Nurr1** is essential for midbrain **dopamine neurons** (Parkinson's gene) → hitting it
    risks neurotoxicity.
  - **NR4A1 + NR4A3 lost together** → **acute myeloid leukaemia** in mice (Mullican et al., Nat Med
    2007; redundant myeloid tumour suppressors) → a degrader must **spare NR4A1** to keep that safety
    net intact.
  → Design target: **NR4A3-selective, NR4A1/2-sparing**, using the 7 divergent pocket handles
  (L406/R412/I484 + T407/T410/I531/L534; `nr4a-selectivity.json`). This matters *more* because
  NR4A3's pocket is the *least* druggable of the three (0.495 vs 0.657/0.801) — a naive binder would
  drift to the off-targets.

**(b) Fusion vs wild-type NR4A3 — NOT solvable by this modality.** The fusion's only tumour-unique
feature is the EWSR1::NR4A3 junction, which lies in a **disordered** region, not a structured pocket;
the druggable LBD is **identical** in fusion and wild-type, so a LBD warhead degrades both. On-target
wild-type-NR4A3 loss (vascular/metabolic/vestibular/bone roles) is the accepted cost — likely
**tolerable** (paralogue redundancy; NR4A3 single-knockout animals are viable; catalytic, dose-able
PROTAC), but it must be assessed, and it is *known* from NR4A3 physiology despite EMC's rarity.
  → If sparing wild-type NR4A3 is required, that is the **ASO route's** advantage, not the degrader's:
  the fusion *mRNA* junction is tumour-unique, so a junction ASO/siRNA (`junction_aso.py`) silences
  only the fusion transcript. Degrader = more potent/druggable but not fusion-specific; ASO =
  fusion-specific but delivery-limited. They are complementary. (Speculative frontier: FET-fusion
  condensate biology may offer a fusion-specific state to exploit — unproven.)

## Why a degrader, and why design is the bottleneck (recap, sourced)
- NOR-1's oncogenic activity scales with **expression level** → removing the protein removes the
  activity; degradation is mechanistically ideal (Munck 2022, NOR-1 druggability).
- The NR4A family is degradable in principle: an **NR4A1 PROTAC** works in cells — but does **not**
  cross-degrade NR4A3 → NR4A3 needs its **own** warhead.
- Real NR4A3-specific chemical matter exists to start from: fragment-derived **inverse NOR-1
  agonists** (low-µM) and fatty-acid-mimetic NR4A ligands — despite the canonical orthosteric pocket
  being collapsed (consistent with our fpocket druggability 0.495).
- The fusion **retains the entire ordered NR4A3 LBD** (the warhead-binding region), so a LBD binder
  hits the oncoprotein.
- **Degrader modality delivers in a sibling FET-fusion sarcoma (precedent, contextual).** A 2026
  report describes **YSA64, an RBM39 degrader with in vivo efficacy and potent cellular activity in
  pediatric Ewing sarcoma (A673)** (Europe PMC `MED/42085934`; *title-level — full text to verify via
  `fetch-literature.yml` before final citation*). This is a useful *modality* precedent — a
  CRBN-recruiting degrader achieving in vivo activity in an EWSR1-fusion sarcoma — **but note it
  degrades the RBM39 splicing dependency, not the fusion oncoprotein itself**, so it supports
  "degraders are tractable and efficacious in FET-fusion sarcoma," not "the fusion was degraded." It
  does not lower our specific bottleneck (a selective NR4A3 warhead) but does de-risk the modality
  bet for the route.

## Target definition (exact inputs)
- **Protein:** NR4A3 / NOR-1, UniProt **Q92570**. Warhead-binding region = the **ligand-binding
  domain, residues 373–626** (ordered, AF2 pLDDT ≈ 85). Retained intact in EWSR1::NR4A3.
- **Pocket:** fpocket **Pocket 5** (druggability 0.495), residues **406–534**, dominant domain = LBD
  (from `nr4a3-structure-assessment.json`). *First prep step: re-run fpocket on the AF2 model with
  per-pocket residue output to enumerate the exact lining residues (the current JSON stores only
  min/max + count).*
- **Structure:** AF2 model from AFDB (Q92570). Consider an **AF3** holo/ligand-bound model and an
  MD-relaxed ensemble (the orthosteric pocket is collapsed/dynamic, so an ensemble matters).
- **Off-targets for selectivity:** NR4A1 (P22736) and NR4A2/Nurr1 (P43354) LBDs — the warhead must
  be NR4A3-selective (the NR4A1 PROTAC's failure to hit NR4A3 shows the family is distinguishable).
  **Pre-computed (result):** `nr4a_selectivity.py` → `nr4a-selectivity.json`. Of 10 NR4A3 top-pocket
  lining residues, **7 diverge** from both paralogues — the selectivity handles:
  **L406** (NR4A3) vs H/H (NR4A1/2), **R412** vs A/T (a charge unique to NR4A3), **I484** vs Y/Y
  (smaller → more room), T407, T410, I531, L534. Constrain generation/scoring to make specific
  contacts at these (esp. L406, R412, I484).
  **Important caveat:** NR4A3's pocket is the *least* druggable of the three (fpocket 0.495 vs NR4A1
  0.657, NR4A2 0.801) — so a naive NR4A binder could *prefer* the off-targets; selectivity must be
  *designed* at the divergent positions, not assumed (consistent with the NR4A1-PROTAC-not-hitting-
  NR4A3 precedent). These handles are a v1 from the static AF2 pocket; refine against the
  MD-revealed conformer.

## Pipeline
1. **Site characterisation (CPU — do first).** Dock the known **inverse NOR-1 agonists** and
   fatty-acid-mimetic NR4A ligands (SMILES from Munck 2022 / J Med Chem 2023) into the LBD with
   smina/AutoDock Vina (or Gnina) against the AF2 model + MD ensemble. Goal: a validated binding
   site + baseline poses/affinities to seed design. **This is the immediate next executable step and
   needs no GPU.**
2. **Warhead optimisation.** Structure-based generative design (e.g. diffusion small-molecule models
   / REINVENT) + re-docking to improve affinity, scored simultaneously against NR4A1/NR4A2 for a
   **selectivity margin**. RDKit for property/ADMET filters.
3. **PROTAC assembly.** Attach the optimised warhead to a **CRBN (lenalidomide-class)** or **VHL
   (VH032)** ligand via a linker library; model the **ternary complex** NR4A3–PROTAC–E3 (AF3 or
   ternary docking / PRosettaC) and score predicted cooperativity & a degradable lysine geometry.
4. **(Alt biologic handle)** RFdiffusion + ProteinMPNN + AF2 filtering for a mini-binder/nanobody to
   the LBD surface — a backup "degrader-by-binder" handle if small-molecule selectivity stalls.
5. **Triage to a publishable candidate set.** Ranked candidates with poses, predicted affinity,
   NR4A1/2 selectivity margin, ternary-complex plausibility, and synthesizability — a computational
   design paper inviting a chemistry group to synthesise and a sarcoma lab to test.

## Compute map (what runs where)
- **CPU / CI now:** fpocket residue enumeration; RDKit; smina/Vina docking of known ligands
  (step 1); off-target structure fetch. → a real first-pass deliverable without a GPU.
- **GPU needed:** RFdiffusion/ProteinMPNN/AF2/AF3, MD, generative small-molecule models.

## GPU experiment plan (HIGH BENEFIT — run these if GPU is provisioned)

> **STATUS 2026-06-26: Experiment 1 (cryptic pocket) COMPLETE — all gates pass.** 30 ns well-tempered
> metadynamics shows the orthosteric pocket opens to fpocket druggability **0.931** (Gate 2 PASS), and a
> druggable conformation (0.80) is thermally accessible at only **0.76 kcal/mol** (Gate 3 PASS; the naive
> ~38 kcal/mol was the cost to the most-OPEN edge, not a druggable state). Calibrated against an NR panel
> (D\*=0.53; the static 0.495 is conservative, not inflated). **The next computational step is
> Experiment 2 — the selective warhead** (`gpu-warhead-aws.yml`, BUILT and idle), then the ternary model.
> Full program state + exact run instructions for a fresh session:
> **[`nr4a3-degrader-next-steps.md`](./nr4a3-degrader-next-steps.md)**. Manuscript:
> [`../manuscripts/nr4a3-degrader-paper.md`](../manuscripts/nr4a3-degrader-paper.md).

Two experiments would materially change the degrader paper, both attacking the route's core
weaknesses. Ranked by impact-per-effort:

1. **MD cryptic-pocket detection (do first — rebuts the central objection).** The whole
   "undruggable" verdict rests on the NR4A3 orthosteric pocket being *collapsed* in a single static
   AF2 model. **GPU-accelerated MD (OpenMM) of the LBD** — solvated, µs-scale or enhanced-sampling
   (metadynamics / `PocketMiner`-style transient-pocket detection) — directly tests whether a
   **transient/cryptic druggable pocket opens**. A positive result *overturns the undruggability
   prior* and is the single strongest possible figure for the paper. Inputs ready: AF2 NR4A3 LBD
   (AF-Q92570, 373–626). Output: pocket-opening frequency/volume time series + representative holo
   conformer to dock into. ~1–2 GPU-days.
2. **De-novo selective warhead/binder design (the route's missing piece).** Turns the paper from
   "a degrader *could* work" into "here is a *designed candidate*." Two parallel tracks:
   - *Small molecule:* structure-based generative design conditioned on the (MD-revealed) pocket —
     DiffSBDD / Pocket2Mol / TargetDiff — then dock-rescore and score **selectivity vs NR4A1/NR4A2
     LBDs**. Output: novel candidate warhead scaffolds with predicted selectivity margins.
   - *Protein binder (alt handle):* **RFdiffusion → ProteinMPNN → AF2 filtering** for a mini-binder
     to the LBD surface (a biologic degrader handle if small-molecule selectivity stalls).
   ~2–5 GPU-days for a first candidate set.

3. **Ternary-complex (degradability geometry) — newly tractable, pipeline PRIMED.** Previously parked
   as "lower priority" because open AF3-class ligand+multimer prediction wasn't available. As of
   2026-06 it **is**: AlphaFold3 (v3.0.x), **Boltz-2**, and Protenix are released (method-watch hit).
   This unblocks modelling the **NR4A3–PROTAC–E3 (CRBN/VHL) ternary complex** to score whether a
   recruited PROTAC presents a **degradable-lysine geometry** — the degrader route's "is it
   geometrically degradable" question, now answerable in-silico. **Pipeline prepared:**
   `nr4a3_ternary.py` (Boltz-2; Protenix/AF3 are documented swap-ins per the "keep pipelines modular"
   principle) + `nr4a3_ternary_sagemaker.py` + `gpu-ternary-aws.yml`, mirroring the MD pipeline.
   Because no NR4A3 warhead/PROTAC exists yet, the script (a) runs a **CPU/CI input-prep + a
   checkable positive control** now (CRBN + its known ligand lenalidomide — does Boltz seat the E3
   ligand in CRBN's tri-Trp pocket?), and (b) emits the **NR4A3-LBD + CRBN + PROTAC** input
   *template* that completes the moment a warhead SMILES is in hand (from experiment 2). Needs GPU
   only to *run* (graceful CI skip, like the MD). *(Also primed for later: AF3 of the
   fusion↔coactivator interface for the transcriptional route.)*

**What I'll prep now (CPU) so GPU time is spent immediately:** the OpenMM MD setup script (system
build/solvation/run config for the AF2 LBD) and the selectivity-scoring harness (NR4A1/2 off-target
structures + docking rescore), so a GPU box only has to *run*, not be configured. The MD result then
feeds the generative design (dock into the cryptic conformer).

## The gate that governs whether any of this matters
Pair every step with the **fusion-addiction evidence** (`depmap-sarcoma-dependency.json` →
`fusion_addiction_proxy`; and the make-or-break dTAG argument). If EMC is not addicted to
EWSR1::NR4A3, a perfect degrader is useless — so the addiction case must be built *alongside* the
warhead, and both belong in the same publication.

## Immediate next action
The CPU docking (`nr4a3_dock.py` — dock real ChEMBL NR4A ligands into the AF2 LBD Pocket-5) is
**built and committed** but **deferred**: three CI runs failed to publish (opaque, and it is a
non-load-bearing *seed*). It is set to manual-dispatch and will be **run on the GPU box alongside
the MD** (smina/openbabel are already in that environment). The load-bearing GPU experiments are the
MD cryptic-pocket scan (`nr4a3_md.py` / `nr4a3_md_modal.py`) and de-novo warhead design — those are
where in-silico effort should go next.

## Molecule-design execution update (2026-06-26) — "making the molecule" in-silico
The warhead design is no longer all-prospective. Status + the staged plan, with the CPU/GPU split and the
gate that governs it:

**Done.** The **warhead screen ran** (smina docking of the real ChEMBL NR4A library into the opened pocket):
NR4A3-favoured chemotypes (top **CHEMBL1873475**, ΔdG ≈ −8.34, margin +1.7, 4/5 handles; **amodiaquine**
−7.63, +1.53). These margins are **confounded triage** (opened NR4A3 vs *static* paralogues) — a binding
prior, not affinity.

**Now (CPU, no GPU, pocket-independent) — the developability tier.** `warhead_chem_profile.py`
(+ `.github/workflows/warhead-chem-profile.yml`) profiles the same docked hits with RDKit: drug-likeness
(QED, Lipinski/Veber, beyond-Ro5 — relevant since PROTACs are bRo5), **synthesizability (SAscore =
"can we make it")**, **PAINS/BRENK liability alerts**, and **PROTAC attachment handles** (amine/phenol/
carboxylic-acid counts = candidate linker-conjugation chemistry). Output `warhead-chem-profile.json` ranks
which docked chemotypes are worth carrying into a PROTAC — the in-silico "can we make this molecule" answer,
needing no GPU and no firmed pocket.
- **Result (run 2026-06-26).** All 7 hits are **readily synthesizable** (SAscore 2.1–3.0; only celastrol
  hard at 4.9). Developability ranks **chloroquine (QED 0.76) > resveratrol (0.69, 3 handles) > amodiaquine
  (0.60, but a PAINS Mannich alert) > piperlongumine (0.78 but **0 conjugation handles**)**; the docking
  top hit **CHEMBL1873475 is only mid-pack (QED 0.47)**, and cytosporone B / celastrol score poorly
  (low QED; celastrol cLogP 6.7). **Key insight: the best *binder* (docking) is not the best *developable*
  scaffold — the two priors are orthogonal**, which is exactly why both tiers are run. Caveats: these are
  known NR4A tool/screening compounds = **starting scaffolds, not selective warheads** (the true warhead is
  the de-novo step); alert catalogs are not exhaustive (e.g. celastrol's known covalent/promiscuous
  character is not flagged); `warhead_promise` is a transparent triage heuristic, not affinity or selectivity.

**PROTAC assembly (design, CPU + one GPU step).** Once a warhead is chosen: attach a known **E3 ligand** —
CRBN (glutarimide, pomalidomide/lenalidomide-derived) or VHL (VH032-derived) — via a **linker** (PEG₂–PEG₆,
alkyl C₂–C₁₂, or rigid piperazine/triazole), conjugated at a **solvent-exposed exit vector** of the docked
warhead pose (away from the handle-contacting pharmacophore; the profile's handle counts seed the
attachment chemistry). Then the **ternary-complex model** (`nr4a3_ternary.py`) scores degradable-lysine
geometry per paralogue — degradation selectivity ≠ binding selectivity. *(E3/linker specifics are standard
PROTAC chemistry; finalise the exact ligand/linker set against the current literature before submission.)*
- **Result (`protac_feasibility.py`, run 2026-06-26).** All four candidate warheads carry a conjugation
  handle (resveratrol 3 phenols; chloroquine/CHEMBL1873475 an amine; amodiaquine amine+phenol) and **all
  assemble into property-space-viable PROTACs**: the best warhead × E3 × linker combos (e.g. amodiaquine +
  VH032 + PEG2 ≈ MW 899; CHEMBL1873475 + pomalidomide + PEG4 ≈ 872; chloroquine + VH032 + PEG2 ≈ 863) land
  **5/5** in the typical PROTAC window (MW ~860–900, RotB 17–25, HBA 10–16); all 4 E3 ligands resolved
  (CRBN: pomalidomide/lenalidomide/thalidomide; VHL: VH032). So assembling a viable degrader is
  in-silico-feasible for every scaffold. *Honest bounds:* additive property estimate (not a bonded SMILES);
  exit vector is a chemical handle (the TRUE attachment vector needs the docked pose, a GPU step); these are
  scaffolds, not selective warheads — the selective binder is still the de-novo (GPU) step.

**De-novo generation + quantitative selectivity (GPU, APPROVAL-GATED) — PIPELINE BUILT (2026-06-29).**
`generate_denovo()` is now **wired to DiffSBDD** (the SOTA pocket-conditioned diffusion model), split into a
minimal-compute funnel: **two GPU runs only** (generation + MM-GBSA), with the whole screen FREE on a GitHub
CPU runner. `nr4a3_denovo.py MODE=generate` (`gpu-denovo-aws.yml`) samples two campaigns
(divergent-handle-conditioned = NR4A3-selective; conserved-conditioned = pan) against the opened pocket;
`MODE=screen` (`denovo-screen.yml`, free CPU) runs novelty → developability → 3-pocket docking →
`selectivity_fingerprint` → PROTAC-handle, and emits the shortlist-only MM-GBSA handoff so the EXISTING
`mmgbsa-aws.yml` confirms the shortlist unchanged (`input_prefix=nr4a3-denovo`). A molecule returning
`confirmed_selective` is the designed candidate. Both GPU runs are gated behind the unbiased release run
(designing/quantifying against a confirmed pocket, not an artifact). FEP stays deferred to the one confirmed
lead. Full spec + how-to: [`nr4a3-denovo-result.md`](./nr4a3-denovo-result.md). Pure gates/ranking are
unit-tested in `denovo_select.py`.

**The gate (honest, ties to the red-team).** All the *GPU* molecule design is **designing against a cryptic,
biased-MD, provisional pocket** (Gate 1 basin-breathing only; Gate 3 provisional; 0.931 is a biased-MD peak).
A warhead must *select/stabilise* the opened state, which docking/generative tools handle poorly. So the
GPU campaign should be **gated on the unbiased release run** (does the opened pocket persist, or is it
bias-induced strain?) — designing against an artifact would waste the effort. The **CPU developability tier
above is not so gated** and runs now. The program's output is an **in-silico design package** (a named
candidate + predicted binding mode, selectivity, ternary geometry, and developability/synthesizability) — a
**design hypothesis, not a validated warhead**; the terminal blockers (synthesise it, prove it binds/
degrades, prove EMC fusion-addiction via dTAG) remain the wet-lab hand-off.

## Remaining in-silico roadmap → wet-lab handoff
The first **designed candidate** (de-novo generation → CPU screen → MM-GBSA confirmation, above) is the
near-term deliverable. This is the *complete* in-silico arc that lies downstream of it — every tier is a
**design hypothesis / prediction, not validation**, and all are **deferred behind the first candidate**.
The point is to be explicit about how far computation can carry this and exactly where it stops.

**Already in the pipeline (built / specified — cross-linked, not re-derived here):**
- **Ternary degradable-lysine geometry** — `nr4a3_ternary.py` / `gpu-ternary-aws.yml` (NR4A3–PROTAC–CRBN/VHL;
  binding selectivity ≠ degradation selectivity, so this is the gating geometry step once a warhead SMILES
  exists; positive control = CRBN + lenalidomide).
- **Selectivity FEP** — the affinity tier (ABFE/relative across the three opened pockets); the program's
  dominant GPU cost, deferred to the one confirmed lead (see `nr4a3-matrix-result.md` go/no-go).
- **Developability + PROTAC assembly** — `warhead_chem_profile.py` (QED, SAscore, PAINS/BRENK, bRo5,
  conjugation handles) + `protac_feasibility.py` (E3 × linker property-window check). Light ADMET only.

**Missing — additional in-silico tiers to add as the candidate matures (in priority order):**
1. **Ternary cooperativity (α) + short MD stability.** Beyond static degradable-lysine geometry: predict
   positive/negative cooperativity and run short MD on the predicted ternary to confirm it is *stable*
   (productive sandwich), not just formable.
2. **Linker-optimisation loop.** Score linker length/rigidity/exit-vector *against the ternary model*
   (replacing `protac_feasibility.py`'s one-shot property-window check) to maximise the degradable-lysine
   presentation — a small design loop, not a single pass.
3. **Fuller ADMET / developability.** Predicted aqueous solubility, permeability, metabolic stability,
   hERG / CYP liabilities — the "survives in a body" questions beyond drug-likeness heuristics.
4. **Retrosynthesis / synthetic route.** A concrete proposed route (e.g. an AiZynthFinder-class search)
   so a chemistry group can make it — beyond the SAscore heuristic.
5. **Broad off-target / polypharmacology panel.** Dock/screen the final candidate against a wider
   nuclear-receptor / proteome panel to flag off-target liabilities beyond the three NR4A paralogues.
6. *(optional)* **Resistance-mutation scan** of the NR4A3 LBD — which pocket mutations could blunt the
   warhead.

**The hard wall — inherently wet-lab, NOT closable in silico (no matter how many tiers are stacked):**
synthesise the molecule; prove it **binds** NR4A3 (and is selective) in a real assay; prove it **degrades**
NR4A3 in cells; and the make-or-break — prove **EMC is fusion-addicted** (that killing EWSR1::NR4A3 kills
the tumour) via the **dTAG** experiment, today supported only by transfer-analogy (DepMap/Ewing-FLI1). The
in-silico program's terminal output is a fully-specified **design package** that hands off to a chemistry
lab and a sarcoma lab — a hypothesis, not a validated therapeutic.

## References (verified)
- Munck JM et al. *Druggability Evaluation of NOR-1 Reveals Inverse NOR-1 Agonists* (2022).
  https://pmc.ncbi.nlm.nih.gov/articles/PMC9542104/
- *Exploring Fatty Acid Mimetics as NR4A Ligands.* J Med Chem 2023. https://pubs.acs.org/doi/10.1021/acs.jmedchem.3c01467
- NR4A1 PROTAC degrades NR4A1 but not NR4A2/NR4A3 (melanoma) — family degradable, NR4A3 needs own
  warhead. (See `degrader-vs-synthetic-lethal.md` refs.)
- Structure/pocket: `research/modalities/nr4a3-structure-assessment.json` (AF2 AFDB + fpocket).
