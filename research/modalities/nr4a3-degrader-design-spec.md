# NR4A3 degrader — in-silico design spec (runnable when compute is available)

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

> **STATUS 2026-06-25:** GPU is provisioned (AWS SageMaker). Experiment 1's pipeline is **validated
> end-to-end** — a 10 ns LBD MD completed on an A10G (stable energetics, `nr4a3-lbd-md.dcd` in S3);
> see `deploy/aws-sagemaker-setup.md` for the working config. **Next:** mdpocket/SASA analysis of the
> 10 ns trajectory (does the Pocket-5 site open?), then the 100–200 ns production run.

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

## References (verified)
- Munck JM et al. *Druggability Evaluation of NOR-1 Reveals Inverse NOR-1 Agonists* (2022).
  https://pmc.ncbi.nlm.nih.gov/articles/PMC9542104/
- *Exploring Fatty Acid Mimetics as NR4A Ligands.* J Med Chem 2023. https://pubs.acs.org/doi/10.1021/acs.jmedchem.3c01467
- NR4A1 PROTAC degrades NR4A1 but not NR4A2/NR4A3 (melanoma) — family degradable, NR4A3 needs own
  warhead. (See `degrader-vs-synthetic-lethal.md` refs.)
- Structure/pocket: `research/modalities/nr4a3-structure-assessment.json` (AF2 AFDB + fpocket).
