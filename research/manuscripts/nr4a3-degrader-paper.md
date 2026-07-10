# Opening a cryptic pocket in the "undruggable" NR4A3: computational design of a paralogue-selective binder

**Tristan D. McRae**

*Independent researcher.* Correspondence: trimcrae@gmail.com

*An in-silico design and feasibility study: no molecule was synthesized and no wet-lab experiment
was performed. Every claim below is sourced or computed and labelled at its computational weight.
Computational analyses were carried out with AI assistance (see Methods).*

<!-- EDITORIAL, NOT FOR SUBMISSION: result paper split from emc-treatment-roadmap.md (2026-06-25),
reframed around NR4A-family druggability with two design poles (2026-07-08). Target: JCIM primary +
ChemRxiv preprint posted immediately; Nature Computational Science = free presubmission inquiry only
(a long shot, not the plan). **Title (2026-07-10, trimcrae): retitled "degrader" -> "binder"** — the review
correctly flagged "degrader" as an overclaim (we have a selective binder/warhead + an arbitrary-linker
PROTAC + a ternary that is NOT paralogue-selective). Degradation stays as the honest future application.
**RESTRUCTURE DONE (2026-07-10, trimcrae "cut hard to the spine"):** main text = 8XTT pocket -> dynamics
-> divergent handles -> falsification-controlled de-novo -> conditional ABFE; demote the 6k repurposing
screen (§2.4b), superfamily screen (§2.7 back half), indication/CAR-T/pan pole (§3), safety genetics (§5),
degradation-window model, and lo_m0_NCCO were moved to the Supporting Information (nr4a3-degrader-paper-SI.md, sections S1-S6). See nr4a3-degrader-paper-review-response.md.
Adversarial self-review: nr4a3-degrader-paper-redteam.md. Display-items plan: nr4a3-degrader-figures.md. -->
<!-- P0 REVISION TASKS not yet done: (1) benchmark AF2 model + pocket + handles against the experimental
8XTT NMR ensemble; (2) ABFE protocol audit given the +7.1 T4L miss (publish per-replicate ΔG, λ-overlap,
ESS, convergence as SI). -->
<!-- SUPERSEDED editorial: the earlier degrader-title alternates are retired (see title change above). -->

## Abstract
The NR4A nuclear receptors (NR4A1/2/3) are orphan, constitutively active transcription factors
long considered "undruggable": their orthosteric ligand pocket is occluded in crystal structures,
and NR4A3 — which drives extraskeletal myxoid chondrosarcoma (EMC) and acinic cell carcinoma by
gain of function — has an experimental LBD structure only as a recently released apo solution-NMR
ensemble (PDB 8XTT, 2025), with no ligand-bound structure and no published pocket-dynamics analysis.
Using a computation-only workflow, we show this
family is instead dynamically druggable and that a *single* cryptic-pocket design framework is
programmable across the NR4A selectivity axis. Calibrated against a nuclear-receptor panel, the
static NR4A3 pocket is borderline (fpocket druggability 0.495 vs a drug-bound band of 0.53–0.68);
well-tempered metadynamics drives a druggable cryptic cavity, and an unbiased "release" simulation shows
that seeded geometry persists without bias (3/3 short replicas) and is fpocket-druggable in ~20–24 % of
frames of one release trajectory (a short-timescale persistence + single-trajectory frame fraction, not an
equilibrium population) — with the same residues independently flagged by a cryptic-pocket predictor
(PocketMiner). Seven paralogue-divergent lining residues
make the pocket a selectivity hotspot: ranking a pocket-conditioned generative campaign on these
divergent handles yields a de-noised, decoy-null-calibrated NR4A3-selective foothold (denovo_401),
whose predicted paralogue selectivity is corroborated by three-replicate absolute-binding FEP
(ΔΔG −4.8 ± 2.0 and −5.0 ± 0.7 kcal/mol vs NR4A1/NR4A2), while re-ranking the same framework on the
conserved core instead designs a pan-NR4A binder for ex-vivo CAR-T de-exhaustion. A CRBN
ternary-complex model forms comparably for all three paralogues, placing degradation selectivity on
the binder. This is an in-silico design and feasibility study — no molecule was synthesized and no
wet-lab validation was performed; every claim is labelled at its computational weight, and the
AF2-derived opened-pocket model — which now must be benchmarked against the experimental 8XTT ensemble —
remains the load-bearing uncertainty.

## 1. Background and rationale
NR4A receptors are constitutively active orphan nuclear receptors whose canonical ligand pocket is
collapsed/occluded in crystal structures (Nurr1, PDB 1OVL; Wang 2003), the structural basis of their
"undruggable" reputation. That reputation is a statement about *static* structures: Nurr1's pocket is in
fact **dynamic and expands** from the collapsed crystal conformation to bind fatty acids (de Vera 2019),
an MD study reported a cryptic druggable pocket in Nur77 (Lanig 2015), and validated NR4A ligands engage
cryptic/surface sites. **NR4A3 itself is experimentally ligandable — pharmacologically, though not yet
structurally.** A fragment screen against NOR-1/NR4A3 (hit rate <1 %) returned three ligand chemotypes, one
elaborated to a **low-micromolar inverse agonist** that shifted NOR-1-regulated gene expression in cells
(Zaienne 2022, a paper titled, aptly, a *"Druggability Evaluation of NOR-1"*), and NR4A3-selective
carboxymethyl-indole-3-carbinol analogues (IC₅₀ ≈ 8–47 µM) de-repress the NR4A3 target gene *MYC* (Safe
2025). These independent, experimental results establish that NR4A3 *can* be engaged by small molecules, but
leave the binding site structurally undefined: NR4A3's LBD has an experimental structure only as a
recently released **apo solution-NMR ensemble (PDB 8XTT, 2025)** — **no ligand-bound structure and no
published pocket-dynamics analysis** exist — the structural gap this paper addresses (our in-silico
druggable pocket supplies a candidate *mechanism* for the ligandability their pharmacology already
demonstrates). *This work's structural foundation is the AF2 model, which predates and does not yet
incorporate 8XTT; benchmarking the AF2 pocket, its dynamics, and the selectivity handles against the
experimental 8XTT ensemble is the primary revision task (§5).* Full reconciliation of the "undruggable" reputation with our
findings, with references and the NR4A-family precedent, is in
[`../modalities/nr4a3-druggability-reconciliation.md`](../modalities/nr4a3-druggability-reconciliation.md).

Because occupancy pharmacology is precluded by the collapsed pocket, the apt modality is **degradation**:
recruit the retained, ordered NR4A3 LBD to an E3 ligase and remove the protein. This is target-generic
(it degrades NR4A3 whether wild-type or in the EMC fusion), which is why the program is framed around
NR4A3 rather than EMC specifically.

The same cryptic-pocket framework is programmable across the NR4A selectivity axis: re-ranked on the conserved core it designs a *pan-NR4A* binder for **ex-vivo CAR-T de-exhaustion** rather than an NR4A3-selective one. The full indication landscape (EMC, acinic cell carcinoma, the pan-NR4A/CAR-T pole, and the NR4A1+NR4A3 anti-target the method must design *away* from) is in **SI §S4**.

## 2. Results

### 2.1 The static orthosteric pocket is borderline — calibrated, not just asserted
fpocket assigns the NR4A3 orthosteric pocket (Pocket 5, residues 406–534, carrying all 7 selectivity
handles) a druggability of **0.495**. To make that interpretable we ran the same pipeline on a
nuclear-receptor calibration panel ([`../modalities/nr4a3_calibration.py`](../modalities/nr4a3_calibration.py)):
- experimentally **drug-bound** NR pockets score **0.53–0.68** (PPARγ/rosiglitazone 0.599, ERα/estradiol
  0.586, Nurr1-holo 0.677, Nur77-holo 0.529) → calibrated druggable threshold **D\* = 0.53**;
- fpocket **`max` is non-discriminating** (even the occluded 1OVL crystal scores 0.864 at a
  *non-orthosteric* cavity) — so the widely-quoted "Nurr1 ~0.8" is **not** the orthosteric pocket, and is
  present in both model (0.801) and crystal (0.864), i.e. **not an AlphaFold artifact**;
- our AF2 model does **not** over-call (NR4A2 model 0.801 ≈ 1OVL crystal 0.864), so NR4A3's static
  **0.495 is conservative**.
Thus the static orthosteric pocket sits *just below* the validated druggable band — concordant with
"undruggable", and the right starting point for the cryptic-pocket question.

**Figure 1.** Calibrated druggability of the NR4A3 orthosteric pocket: the validated drug-bound
nuclear-receptor band (PPARγ 0.599, ERα 0.586, Nurr1-holo 0.677, Nur77-holo 0.529; D\* = 0.53) against the
static NR4A3 pocket (0.495, just below the band) and the metadynamics-opened peak (0.931, shown as a
biased-ensemble readout on a distinct scale — not a like-for-like beat of the static band). Full figure: [`../modalities/nr4a3-fig1.png`](../modalities/nr4a3-fig1.png) (rendered by `nr4a3_journal_figures.py`).

**Independent cross-check — a cryptic-pocket predictor, trained on separate data, flags this exact site.**
Before invoking our own dynamics, we asked whether a *method that shares no code or training data with ours*
independently expects a cryptic pocket here. PocketMiner (Meller et al., *Nat Commun* 2023) is a graph
neural network that predicts per-residue cryptic-pocket-forming propensity from a **single static
structure**, trained on an independent MD-derived cryptic-pocket dataset. Run on the **apo** AF2 NR4A3 LBD
(AF-Q92570, residues 373–626 — the *pre-metadynamics* structure, so the test is not circular; MIT tool, run
verbatim), it assigns the Pocket-5 lining residues a mean cryptic-pocket probability of **0.64 versus a
0.47 whole-LBD background (1.36× enrichment)**, with **8/10 Pocket-5 residues ≥ 0.5** and **4/10 ≥ 0.7**
(residues 406, 481, 484, 531 — three of which, 406/484/531, are among our seven selectivity handles); eight
of the ten sit in the **top ~14–29 %** of the LBD by score (percentile 0.71–0.89). We report this at its
true weight, with two honest caveats: (i) PocketMiner is a *propensity predictor* — it corroborates the
**site/existence** of a cryptic pocket from an orthogonal method, but supplies neither the opened geometry
nor a druggability value, which remain the job of the metadynamics + fpocket analysis below; and (ii) the
network's single highest-scoring residues (375–398) fall at the **N-terminal truncation edge** of the
domain fragment — a chain-terminus flexibility artifact of scoring an isolated LBD, not the functional
cavity — so we rest on the *Pocket-5 enrichment*, not a rank-1 claim. Data:
[`../modalities/nr4a3-pocketminer-result.json`](../modalities/nr4a3-pocketminer-result.json).

**Reconciliation with recent NR4A structural and chemical-biology work (2023–2025).** Three independent
lines of evidence bracket this borderline score and sharpen (rather than soften) our claim. *(i) The
occluded-pocket challenge.* A 2025 structure-guided Nurr1 study (vidofludimus; Sturm/Willems 2025) reaffirms
that the *canonical* NR4A pocket is "filled with bulky hydrophobic residues" and modulates the receptor
instead through an **allosteric surface pocket** — a direct challenge to any canonical-cavity strategy. It is
exactly why our claim is explicitly **not** that the static canonical pocket is druggable but that it
*breathes* into a transiently druggable cavity (§2.2); their surface pocket is also an alternative site we do
not pursue here. *(ii) Ligandability is real but chemotype-specific.* Protein-NMR footprinting (Munoz-Tello
2020) confirms amodiaquine, chloroquine and cytosporone B directly bind the NR4A LBD while **celastrol,
C-DIM12 and TMPA do not** — so among the repurposed actives in our selectivity matrix (§2.4), cytosporone B
carries independent direct-binding support whereas celastrol does not, which we now weight accordingly; and a
family-wide chemical-probe audit (Willems/Merk 2025) validates a small vetted NR4A tool set while showing many
putative NR4A ligands lack on-target engagement — a caution we apply to every repurposed chemotype.
Fragment-to-lead campaigns reaching sub-µM NR4A ligands with NOR-1/NR4A3 tested (Stiller & Merk 2023; Zaienne
2022) keep the *ligandable-not-undruggable* premise on experimental footing. *(iii) Paralog-selective NR4A
degradation is achievable.* The NR-V04 PROTAC (Wang 2024) selectively degrades NR4A1 while **sparing
NR4A2/NR4A3** — proof-of-concept that intra-family degradation selectivity is attainable (the exact inverse of
our NR4A3-selective goal), though its sparing mechanism is unresolved and its celastrol warhead is a
promiscuous covalent binder, not a selective one.

### 2.2 Metadynamics drives the orthosteric pocket to breathe into a druggable state (30 ns production)
Well-tempered metadynamics on the radius of gyration of the Pocket-5 lining Cα atoms (method:
[`../modalities/metad-methods-appendix.md`](../modalities/metad-methods-appendix.md)) drives the pocket
open (CV Rg ~0.5 → ~1.05 nm). On the 30 ns run (600 frames), per-frame fpocket on the **orthosteric
Pocket-5 cavity** (the *same* metric as the static 0.495 and D\*, not the non-discriminating "max-anywhere"
cavity of §2.1) reaches druggability **0.931** (max over frames; `crosses_0.5 = True`); SASA of the lining
residues rises (+6.1 nm², 86.8 % of frames more open than baseline). (A 5 ns validation gave a consistent
0.751.) This is the **first pocket-dynamics evidence for NR4A3**, paralleling the *dynamic, breathing*
Nurr1 pocket (de Vera 2019).

**Read this number for what it is.** The fpocket druggability score is a standard, validated metric (a
logistic model of hydrophobic enclosure and polarity — *not* raw cavity volume), and §2.1 already anchors
it on a nuclear-receptor panel that includes the occluded 1OVL crystal as a de-facto negative; it is a
geometry-based druggability *proxy* (a prediction, not a measurement). Two honest qualifications apply to
the **0.931** specifically. First, it is the
**maximum over the 600 opened frames** — an extreme-value statistic that overstates the *typical* opened
conformation; the more faithful summary is the *distribution*, i.e. the fraction of opened frames clearing
D\*=0.53 (the pre-registered ≥5 %-of-frames test, comfortably met — the handle-facing sub-sample found
roughly one third of frames druggable), with 0.931 as the peak. Second, it is computed on **biased-MD
conformations**, so its magnitude is not on the same footing as the *static* drug-bound crystal sites
(0.53–0.68) and we do **not** claim "0.931 > the drug-bound band" as a like-for-like result. Note the rise
is informative rather than an artifact of "opening": because druggability rewards hydrophobic *enclosure*,
a pocket that merely splayed open / became solvent-exposed would score *lower*, not higher — so reaching a
druggable score means the breathing cavity is hydrophobic and enclosed (corroborated by the lining-residue
/ handle-facing check, §2.2 below). The one thing fpocket cannot settle — whether the breathing-open
geometry is physically populated or bias-induced strain — is decided by the unbiased **release run**, not
by any fpocket control. The honest claim: the pocket *geometrically admits* a druggable cavity when it
breathes open, with that cavity hydrophobic/enclosed, and the population pending the release run.

**Gate scoring** ([`../modalities/nr4a3-druggability-prereg.md`](../modalities/nr4a3-druggability-prereg.md)):
**Gate 2 (opened state druggable) PASSES** on both clauses (druggable frames + handles pocket-facing,
below). **Gate 1 (a genuine two-state cryptic *opening*) FAILED as pre-registered.** Gate 1
asked for an accessible *minimum or shoulder* at an opened Rg "not just biased excursions," but F(Rg) is
**monotonic — a single closed basin and a rising wall, with no separate opened minimum**. By the
pre-registered criterion this is a fail: there is no distinct opened state. **This negative result
motivated an alternative hypothesis** — that the druggable conformations are reached by **basin-internal
breathing** rather than a two-state opening — which the release run (below) then tested. So we report
Gate 1 as **failed, and reformulated**, not as a "weak pass": there is one basin whose thermal
fluctuations transiently expose a druggable cavity (consistent with de Vera's breathing Nurr1 pocket), and
"opened *state*" would overstate it. **Gate 3 (energetic accessibility)
is provisionally met.** The naive closed→fully-open cost is ~38 kcal/mol, but that is the cost to the
*most-open* edge (Rg 1.06) at the **under-converged sampling frontier**, not a *druggable* state:
correlating per-frame druggability with F(Rg) shows the pocket is already druggable (fpocket 0.80) at
Rg ≈ 0.72 — in the well-sampled basin region — at only ~0.76 kcal/mol. The caveat (disclosed, not buried):
both numbers are read off the *same* incompletely-converged biased F(Rg), so the 0.76 rests on the
basin region being better sampled than the frontier (it is, but it is a single biased profile). **The metad
has since been extended to 60 ns cumulative** (two 30 ns segments; `report_metad.py` on the committed
`metad-fes-60ns.dat`), and the F(Rg) picture is **robust to the doubled sampling**: still a **single basin**
(minimum Rg ≈ 0.755 nm) with **no separate opened minimum** (Gate 1 stays failed-as-registered / basin-breathing), the
**druggable release-frame region (Rg ≈ 0.73) sits only ~0.6 kcal/mol above the basin** (confirming the ~0.76),
and the **most-open frontier (Rg ≈ 1.06) is ~35 kcal/mol** (confirming the ~38). So the provisional Gate-3
energetics are **confirmed, not revised, at 2× sampling** — the low-cost accessibility of the druggable basin
region does not rest on under-convergence. The converged landscape is **Figure 2**
([`../modalities/nr4a3-fig2.png`](../modalities/nr4a3-fig2.png); generated by `nr4a3_journal_figures.py`
from the committed `metad-fes-60ns.dat`). (Edge caveat retained: sum_hills references the sampled edges to
~0 at the metad walls, so only the basin and the profile *shape* are interpretable, not the edge values. The
fpocket druggability figures above are from the 30 ns trajectory; extending per-frame fpocket to the 60 ns
frames is a cheap, still-open follow-up.) The
**independent** test — whether the breathing-open geometry is a populated sub-state or bias-induced strain
— is the **unbiased release run** (`nr4a3_md_release.py`), **now complete and POSITIVE** (next paragraph).
Net: the single static structure (0.495) understated the pocket; the
thermally-populated ensemble breathes to a geometrically druggable cavity at low apparent cost, and an
unbiased run confirms that cavity is metastable and druggable without any bias — a feasibility result,
stated at that weight.

**The unbiased release run resolves Gate 3 — cautiously POSITIVE, as an induced-fit cavity.** Seeding
unbiased dynamics from a *strained* metad frame requires care: a first run seeded the max-Rg frontier frame
(0.984 nm, the ~38 kcal/mol opening edge) and it collapsed (frac-near-open 0.00) — the *worst-case* frame,
near-guaranteed to collapse, and not the realistic target. Re-seeded at the **low-energy druggable frame
(CV Rg 0.717)**, the breathing-open geometry is **metastable: 3/3 unbiased replicas held the full 5 ns**
(frac-near-seed 1.00, mean |drift| 0.025 nm, no collapse in any replica). Running fpocket on the *unbiased*
release trajectory, the orthosteric Pocket-5 is **druggable in ~24 % of frames** (max 0.842, mean 0.262,
fraction ≥ 0.5 = 0.24, fraction ≥ D\*=0.53 = 0.20; static 0.495) at CV Rg ≈ 0.737 — clearing the
pre-registered "≥5 % of frames ≥ D\*" bar (20 % here), and crucially **on unbiased dynamics, so not a bias
artifact**. *(Two scope notes so the two numbers are not over-read as one. (i) The **3/3 metastability** is an
**Rg-persistence** result across the triplicate; the **~24 % druggability fraction** is measured on the
**single** `release_rep0` trajectory — the other two replicas confirm the geometry persists, not
independently that it is druggable a quarter of the time. (ii) **5 ns is a short persistence window**: it
rules out fast (sub-ns) collapse of the seeded conformation, but a pocket can read as metastable on 5 ns and
still relax on tens–hundreds of ns, so "metastable" here means "does not promptly collapse," not "a verified
long-lived sub-state.")* The honest reading: this is **not** an always-open pocket (mean 0.262 < 0.5) but a **dynamic /
induced-fit cavity** whose seeded open-like geometry does not promptly collapse without bias and is
fpocket-druggable in ~20–24 % of frames of one release trajectory. **This is a short-timescale persistence
result plus a single-trajectory frame fraction — NOT an equilibrium population estimate:** the frames are
temporally correlated, the fraction is from one replica, and 5 ns cannot establish the equilibrium
probability of the conformation or a spontaneous opening rate. So **Gate 3 is cautiously passed in this
narrow sense** (the seeded druggable geometry is not bias-induced strain that instantly relaxes); a warhead
would need to select-and-stabilise these transiently-druggable conformations rather than occupy a static
pocket. Establishing an actual populated fraction would require reweighted enhanced sampling or many
independent unbiased trajectories with equilibrium weighting (a revision task, §5). All downstream design (below) is therefore anchored to a **druggable unbiased
release frame** (Rg ≈ 0.737, fpocket ≥ 0.5; `nr4a3_release_druggable.py`), not the biased-metad frame. *(Registered Gate-2 sub-check — now COMPLETE and CONFIRMED. The handle-facing analysis
(`../modalities/nr4a3_handle_facing.py`, run 2026-06-26 on the 30 ns trajectory) shows the opened,
druggable frames keep the selectivity handles pocket-facing: across the druggable frames (fpocket ≥
D\*=0.53) a mean of **5.0/7** handles point into the cavity and **87.5 %** keep ≥4 facing. Five are
reliably pocket-facing — **L406, T410, I484, I531, L534** (≥0.875 of druggable frames) — while **T407
and R412 mostly splay outward** (facing in 0.0 and 0.25 of druggable frames), so the demonstrated
selective-engagement set is those five, not all seven. This is also the precondition for the warhead
screen's handle-contact scoring (§2.4). The unbiased "release" run is the orthogonal metastability test
that upgrades Gate 3 from "thermally plausible" to confirmed (does the breathing-open geometry persist, or
collapse as bias-induced strain?); it has now **run and resolved POSITIVE** — metastable (3/3 replicas) and
druggable in ~24 % of unbiased frames when seeded at the low-energy druggable frame — so the metastability
question is **resolved**, as an induced-fit cavity (see the release-run paragraph above).)*

**The opened frame is an intact fold, not a metad-melted one (structural-sanity control).** Because every
downstream step (docking, MM-GBSA, the ternary, and the FEP below) is anchored to the opened NR4A3 frame, we
verified that opening the pocket did not *unfold* the LBD. The opened frame is elongated (~99 Å long axis vs
~45 Å for a compact LBD), which a reviewer could read as an over-driven metadynamics artifact — so we measured
it directly (`nr4a3_frame_sanity.py`): against the pre-metad AF2 LBD, the opened frame **retains 100 % of the
helical content** (DSSP helix fraction 0.602 vs 0.594; retention 1.01) and its folded **core superimposes to
1.76 Å Cα-RMSD** (1.78 Å including the pocket mouth). So the fold is intact and the elongation is a **floppy,
disordered N-terminal hinge** (the ~22 residues before the LBD core) swinging out — not a melt. This both
validates the frame used throughout and licenses trimming that disordered hinge for the explicit-solvent FEP
(§4), which is standard practice (ABFE is run on the folded domain, not a disordered tail).

### 2.3 Selectivity handles for an NR4A3-selective (NR4A1/2-sparing) warhead
Aligning the NR4A3 pocket to NR4A1/NR4A2 ([`../modalities/nr4a-selectivity.json`](../modalities/nr4a-selectivity.json))
identifies, among the **10 Pocket-5 lining residues**, **7 divergent** ones — L406, T407, T410, R412,
I484, I531, L534 — as selectivity handles. All 7 are within the metadynamics CV; of these the opened,
druggable ensemble keeps **5 pocket-facing** (L406, T410, I484, I531, L534 — §2.2), so those five are the
realistically *engageable* handles a warhead can exploit (T407 and R412 mostly splay outward).

**Figure 3.** The seven paralogue-divergent Pocket-5 lining residues mapped on the opened NR4A3 pocket, with
the five that stay pocket-facing in the druggable ensemble (L406, T410, I484, I531, L534; T407 and R412 splay
outward) highlighted as the engageable selectivity handles. Full figure: [`../modalities/nr4a3-fig3.png`](../modalities/nr4a3-fig3.png) (rendered by `nr4a3_journal_figures.py`).

**The selectivity window is asymmetric across the two paralogues — and narrower against NR4A2.** "Divergent"
in the alignment means *differs from NR4A1 or NR4A2*; selectivity must hold against **each** separately, and
the subsets are not equal. Against **NR4A1**, all 7 handles differ (and all 5 engageable ones). Against
**NR4A2**, only **6 of 7** differ — **I531 is identical (Ile in both NR4A3 and NR4A2)** — so of the 5
engageable handles, only **4** distinguish NR4A3 from NR4A2 (L406, T410, I484, L534; I531 drops out). NR4A2
selectivity therefore rests on a *narrower* engageable set than NR4A1 selectivity, which matters because
NR4A2/Nurr1 is the paralogue carrying the dopaminergic-loss liability one most wants to spare. This is a
specification with a quantified, paralogue-resolved window — not a demonstrated binding margin. This design
specification lets the
*same* opened pocket be tuned **NR4A3-selective** (engaging the divergent handles; for the fusion sarcomas,
sparing the NR4A1/NR4A3 myeloid tumour-suppressor function) or deliberately **pan-NR4A** (engaging the
conserved pocket residues; for ex-vivo immuno-oncology) — SI §S4.

**These same handles are ortholog-conserved — divergent across paralogues yet invariant across
NR4A3 orthologs.** A degrader against a fusion-driven cancer could face selective pressure for target-site
escape mutation, so we asked whether the warhead pocket is evolutionarily conserved (`nr4a3_resistance_map.py`).
All ten Pocket-5 lining residues — including all seven selectivity handles — are **fully conserved across
six species spanning ~300 My of amniote evolution** (human plus five orthologs: mouse, rat, cow, pig,
chicken; overall LBD identity 0.79–0.95, with more-divergent xenopus/zebrafish excluded by an
alignment-identity guard). So the
handles are **paralogue-divergent** (the source of NR4A3 selectivity) yet **ortholog-invariant** across
these six amniote species. Ortholog conservation is *suggestive* that these positions are functionally
constrained, but it is **not** evidence of escape resistance in human tumours: cross-species conservation
and acquired resistance under therapeutic selection are distinct questions, and we do not show that a
tumour cannot mutate these residues or that doing so would abolish oncogenic function. This is the
conservation observation only; an energetic test of the functional cost of mutation — a computational
alanine scan of the handle residues (per-residue MM-GBSA ΔΔG of `denovo_401`; `nr4a3_resistance_ddg.py`) —
is a computed follow-up, and human-variation / deep-mutational data would be needed to speak to resistance.

**The warhead pocket is the most paralogue-divergent zone of the LBD — a selectivity hotspot.** Comparing
NR4A1/2/3 divergence in the orthosteric cryptic pocket (the warhead's contact residues) against the LBD-wide
pocket-residue census (same `nr4a-selectivity.json` alignment):

| residue set | n | divergent vs ≥1 paralogue | divergent vs **both** paralogues |
|---|---|---|---|
| **orthosteric cryptic pocket (warhead contacts)** | 10 | **70 %** | **60 %** |
| **predicted NR4A3–CRBN ternary interface (§2.4)** | 33 | **24 % (8)** | **18 % (6)** |
| LBD-wide pocket census | 148 | 45 % | 28 % |
| non-orthosteric remainder (surface/PPI proxy) | 138 | 43 % | — |

**Supplementary Figure S2** ([`../modalities/nr4a3-figS2.png`](../modalities/nr4a3-figS2.png); generated by
`nr4a3_journal_figures.py` from the table above, alignment source `nr4a-selectivity.json`). Paralogue
divergence by LBD residue set: the orthosteric cryptic pocket (warhead contacts) is the *most*
paralogue-divergent zone — 70 % of its residues differ from ≥1 paralogue (60 % from both), ~1.6× the LBD-wide
average — while the predicted NR4A3–CRBN ternary interface is separately divergent on a *different* surface.
Sequence divergence is handle *availability* (a specification), not a demonstrated binding margin.

The warhead pocket is **~1.6× more paralogue-divergent than the rest of the LBD** — the *most* divergent
zone, a selectivity hotspot, not a conserved wall — so the binder's selectivity problem was **never handle
scarcity**; it is **pocket druggability + affinity-margin robustness** (the cryptic, least-druggable-of-three
pocket, and the MM-GBSA noise floor of §2.5–2.6). The full selectivity-architecture analysis — the
multiplicative binder × ternary × kinetics budget, the paralogue-divergent CRBN-ternary interface, and a
superfamily-wide pocket-liability screen across all 47 human NRs (with MR/AR as the sole non-paralogue
sequence-level follow-ups) — is in **SI §S3**.

### 2.4 Warhead screen and the family-wide selectivity matrix
With the pocket validated as druggable and accessible, we screen a **selective warhead** against the
*opened* conformer (`nr4a3_warhead.py` + `gpu-warhead-aws.yml`): it extracts the most-druggable opened
conformer, docks a real ChEMBL NR4A library into NR4A3-opened **and** the
aligned NR4A1/NR4A2 pockets, and ranks by a selectivity margin + engagement of the **5 pocket-facing**
handles (§2.3). A first screen returns NR4A3-favoured chemotypes (e.g. an NR4A3-active scaffold,
ΔdG ≈ +1.7 kcal/mol vs the paralogues); these docking margins are **triage priors, not affinities**.

**The selectivity matrix.** A central methodological point: docking the *opened* NR4A3 pocket against
*static* NR4A1/2 models biases toward apparent selectivity, because — by our own argument (de Vera 2019;
the Nur77 cryptic pocket) — the paralogue pockets are likely cryptic too. We therefore ran the **same
metadynamics on NR4A1 and NR4A2** (one pipeline; paralogue CV/LBD mapped to NR4A3 by BLOSUM62 alignment)
to obtain **state-matched opened-pocket ensembles** for all three, and docked one library into each
(`nr4a3_matrix.py`; state-matched opened conformers NR4A3 frame 300 (druggability 0.931) / NR4A1 frame 524
(0.981) / NR4A2 frame 125 (0.938)). Each candidate carries a **selectivity fingerprint** across the family, partitioning
the library into NR4A3-selective (EMC/AciCC), pan-NR4A (ex-vivo immuno), and the AML-associated NR4A1+NR4A3
**anti-target** cells (SI §S4). The **anti-target cell is empty** (no candidate engages NR4A1+NR4A3 while
sparing NR4A2 — nothing to design away from in this library), and the NR4A3-leaning leads are repurposed NR4A
actives (e.g. cytosporone B, amodiaquine). This makes the divergent-handle map a *demonstrated, tunable*
design axis rather than an assertion — but the docking dG are within noise, so they nominate chemotypes,
not a lead.

**Figure 4.** The family-wide, state-matched selectivity matrix: one candidate library docked into the
metadynamics-opened NR4A3, NR4A1 and NR4A2 pockets, giving each candidate a per-paralogue selectivity
fingerprint (NR4A3-selective / pan-NR4A / NR4A1+NR4A3 anti-target cells). Full figure: [`../modalities/nr4a3-fig4.png`](../modalities/nr4a3-fig4.png) (rendered by `nr4a3_journal_figures.py`).

**Docking nominates; endpoint free energy decides — and it disqualifies the repurposed actives.** We
re-scored the matrix's own docked poses with single-snapshot **MM-GBSA** (enthalpy + GBn2 implicit solvent,
no entropy/ensemble average; OpenCL on the A10G; `nr4a3_mmgbsa.py`). The docking-level NR4A3-selectivity
**mostly does not survive**: the apparent docking lead **cytosporone B reverses** (as its known NR4A1
agonism demands), and across the 13 deduplicated candidates the verdict census is *confirmed_selective* 3
(amodiaquine, celastrol, + a duplicate), *reversed* 3, *weakened* 2, *rescued* 3, *confirmed_nonselective*
2. MM-GBSA magnitudes here are inflated by the single-snapshot/no-entropy approximation, so we read the
**verdict/direction, not the kcal/mol** — but the direction is clear: **repurposed NR4A chemical matter is
method-validation, not a selective lead**, which is exactly why a *de-novo* design is needed (§2.5).
(Selectivity FEP on a survivor is the defensible affinity tier, gated behind a bona-fide selective
candidate.) A representative `denovo_401`-PROTAC CRBN ternary-complex model (`nr4a3_ternary.py`, Boltz-2; the pipeline validated by recovering the known CRBN + lenalidomide pose) forms a **productive-geometry ternary comparably for all three paralogues** (per-paralogue iptm 0.72/0.83/0.82; each LBD presenting an exposed lysine within ubiquitin reach), so for this representative linker **the ternary adds no NR4A3 degradation-selectivity** — degradation selectivity, if any, rests on the **binder** margin, with linker/exit-vector design the (untested) lever that might introduce it. The full ternary detail, the CRBN/IMiD positive control, and the standard three-body cooperative-equilibrium **degradation-window** model (DC50/Dmax/hook, the analysis layer the per-paralogue FEP Kd's feed) are in **SI §S2**.

**At marketed-library scale the negative result holds.** Running the *same* funnel over the entire ~6,000-compound Broad Drug Repurposing Hub — with a 9-target anti-target/promiscuity panel added as a selectivity axis — finds **no** repurposed compound that is both NR4A3-selective *and* clean against the counter-screen (every paralogue-margin survivor, e.g. SNX-5422 / AGI-5198, engages ≥1 off-target more tightly than NR4A3, whereas `denovo_401` does not), a 6k-scale promiscuity-controlled negative result that is precisely why a *de-novo* design (§2.5) is required; full screen in **SI §S1**.

### 2.5 De-novo design yields NR4A3-selective candidates: decoy-calibrated, then multi-snapshot-confirmed (§2.6)
Because the repurposed library produced no candidate that survives MM-GBSA as NR4A3-selective (§2.4), we
ran a **pocket-conditioned de-novo generative campaign** and put its output through the *same* selectivity
funnel. (1) **Receptor.** We anchored generation and docking to a **druggable unbiased *release* frame**
(`nr4a3_release_druggable.py`: Rg ≈ 0.737, confirmed fpocket druggability 0.667, in the calibrated drug-bound
band) — the release-derived induced-fit conformation from §2.2, not the biased-metad frame — keeping a small
druggable sub-ensemble since the pocket is dynamic. (2) **Generation.** DiffSBDD (pocket-conditioned
diffusion, pretrained CrossDocked weights; `nr4a3_denovo.py`) generated molecules into that pocket,
conditioned on the lining residues incl. the engageable divergent handles; a lead-size constraint
(`--num_nodes_lig`) plus a molecular-weight floor in scoring removed a fragment bias seen in an
unconstrained pilot (whose top hits were trivially small benzoic/toluic-acid-class fragments). The
size-constrained production generation was clean: of 195 generations, **191 valid and unique, 96 %
PAINS-free, 92 % contacting ≥4 of the 5 engageable handles** in the generated pose. (3) **Funnel.** We docked the top-20 generations into the
NR4A3-release / NR4A1 / NR4A2 pockets for a selectivity fingerprint (`denovo_15` the
docking-level NR4A3-selective lead **by margin** — NR4A3 favoured over both paralogues by ≥1 kcal/mol),
then **MM-GBSA-rescored all 20**. *(Receptor-state caveat: unlike the §2.4 repurposed matrix, which was
fully state-matched — all three paralogues at their metad-opened frames — this de-novo funnel docks NR4A3 in
its **unbiased release** frame (fpocket 0.667) against the **biased-metad** NR4A1 frame 524
(0.981) / NR4A2 frame 125 (0.938), because the release run (§2.2) made the unbiased frame the defensible
NR4A3 receptor. The states are therefore **not** matched the way §2.4's are — but the asymmetry runs
**against** NR4A3-selectivity (the paralogue pockets are scored in their more-druggable opened state, which
tends to dock ligands more favourably), so a positive NR4A3-selectivity call here is conservative rather
than flattered. A fully state-matched re-dock (NR4A3 metad-opened) **has since been run for the lead**
(`denovo_401`, §2.6): it stays NR4A3-selective there too (+7.44 ± 4.18), so the call is not a receptor-frame
artifact.)* The result is qualitatively different
from the repurposed library: **3 candidates are *confirmed_selective* (`denovo_15`, `denovo_94`,
`denovo_57`) and NONE reverse** (census: confirmed_selective 3 · rescued 7 · weakened 1 ·
confirmed_nonselective 9 · **reversed 0**). The lead **`denovo_15`** (SMILES
`C=C(CC1=CC=C(NC(=O)O)C1)[C@H]1C=C2C(=NC1)OC[C@H](C)[C@@H]2C`; QED 0.774, SAscore 5.08, contacts 4 of the 5
handles) is NR4A3-selective at *both* tiers — docking selectivity margin +1.0 (the dock-tier `nr4a3_selective`
lead; in absolute engagement NR4A2 is weakly co-engaged at the permissive −7 kcal/mol cutoff, so its matrix
*cell* is NR4A2+NR4A3, but NR4A3 is the favoured paralogue at both tiers) and **MM-GBSA margin +10.7
kcal/mol** (magnitude inflated by the single-snapshot approximation; the *direction* is the robust part).
The chemistry-promise top hit (`denovo_189`) instead landed in the docking anti-target cell and did not come
back selective, a useful reminder that drug-likeness ≠ selectivity. This is the program's **first *designed*
NR4A3-selective warhead candidate** — a screening-grade, pose-aware prediction across two energy tiers,
**not** a synthesized or affinity-validated molecule (selectivity FEP, then the ternary-complex /
degradation-selectivity step, remain the gates ahead).

**Read `denovo_15` as a chemotype/pose hypothesis, not a developable molecule.** A medicinal-chemistry pass
on the SMILES (RDKit) flags several **generative-model liabilities**: a **carbamic acid** (`NC(=O)O`, the
polar "handle" — hydrolytically unstable, decomposing to the amine + CO₂), a **1,3-cyclopentadiene** (a
reactive diene), an **imine** and an **exocyclic alkene**, and **no aromatic ring at all** — and its
**SAscore 5.08 sits above the campaign's own ≤4.5 synthesizability cut** (QED 0.774 is favourable but does
not screen for stability/reactivity). These are characteristic DiffSBDD artifacts: the molecule is optimised
to *fit and score* in the pocket, not to be stable or makeable. The honest contribution is therefore the
**funnel and the selectivity *direction* it produces** (de-novo matter that survives MM-GBSA without
reversing, where repurposed matter reversed), with `denovo_15` as a **selective chemotype/pose hypothesis to
be re-designed into a stable, synthesizable analogue** — not a warhead ready for synthesis.

**The other two `confirmed_selective` hits do not rescue this** (full RDKit triage, 2026-06-29): **`denovo_94`**
(MM-GBSA margin +5.02, 4 handles) carries a **peroxide (1,2-dioxane)** plus N,S- and O,S-acetals — equally
non-viable; **`denovo_57`** (`NC[C@@H]1CCN(Cc2ccccc2)C1`, a 3-(aminomethyl)-1-benzylpyrrolidine) is the **one
chemically clean, readily synthesizable** hit (SAscore 2.09, aromatic, basic amine, no flagged liabilities) —
but it is the **weakest** selectivity signal (margin +1.07), engages only **2** of the 5 handles, and falls in
the docking "none" cell. So the three confirmed-selective hits split into *strong-but-artifactual*
(denovo_15/94) and *clean-but-weak* (denovo_57); **none is simultaneously chemically viable and a strong
selective binder.** This is the expected behaviour of a pretrained pocket-conditioned diffusion model with no
stability/synthesizability term in its objective. The load-bearing, honest claim is therefore the **method**
(the funnel produces de-novo matter whose NR4A3-selectivity survives an endpoint energy model, unlike the
repurposed library), not a specific developable molecule. **Next de-novo steps:** add a stability/reactivity
filter to `denovo_funnel.score_molecule` (reject peroxides, carbamic acids, cyclopentadienes, acetals/aminals,
non-aromatic warheads, SA > 4.5) and **re-generate**, aiming for a hit that is clean *and* strongly selective.

**Decisive control: the single-snapshot MM-GBSA selectivity verdict fails a decoy test, so
selectivity is NOT established by this tier.** We ran a **specificity control** — 38 diverse **non-NR4A
marketed drugs** (`decoy_library.py`) through the *identical* dock→MM-GBSA funnel — and a **developability-gated
re-screen** of the generations (the structural-alert gate of §2.4 added after the artifact finding;
`structural_alerts.py`). Two results force a retraction of the "MM-GBSA-confirmed selective" claim. (i) The
decoy null is **`confirmed_selective` in 39 % of cases (15/38; ~58 % have a positive NR4A3 margin)** —
including **caffeine, ibuprofen, lidocaine, phenytoin** — while the developable de-novo set is
`confirmed_selective` in only **2/11 (18 %)**, i.e. **below the decoy baseline and not enriched.** The
single-snapshot, single-pose MM-GBSA plus the asymmetric receptor (NR4A3 scored in its druggable release
frame vs the paralogue frames) systematically favours NR4A3, so the verdict labels ~40–58 % of *any* drug-like
matter "NR4A3-selective" — it has **no demonstrated specificity**, which also explains why the artifact
`denovo_15` had scored "confirmed_selective." (ii) Of the generations, only **11/191 survive the
developability gate**, and **none of the clean ones is robustly NR4A3-selective** once the decoy baseline is
accounted for. **We use the decoy run as a calibrated null, and one candidate clears it.** Rather than the
non-discriminating "margin > 0", we set the selectivity bar at the **decoy 95th percentile (+13.1 kcal/mol;
`selectivity_calibration.py`)**. Against that bar, **`denovo_111`** (a clean fluoro-phenyl-pyrrolidine,
QED 0.87 / SA 2.9, NR4A3-margin **+15.7**, favoured in *both* receptor states, only 1 of 38 decoys above it)
is the **first calibrated above-null NR4A3-selective hit** — every other de-novo and decoy molecule *in that
harvest* falls in the null. *(A later generation batch produced `denovo_401`, whose single-snapshot margin
+13.92 also exceeds this +13.1 bar and which additionally survives multi-snapshot de-noising (§2.6); it — not
`denovo_111` — is the carried lead. (`denovo_111`, the earlier single-snapshot foothold, de-noised well as the
*neutral* form but was later **withdrawn** when the species-resolution sweep showed its physiological *cation*
reverses selectivity — §2.6; so `denovo_401` is the sole robust lead.))* So the
honest read is **not** "no selectivity"; it is "**raw single-snapshot MM-GBSA is
non-specific, but decoy-calibration isolates `denovo_111` as a genuine foothold**." The de-novo program
continues as a **lead-optimization campaign around `denovo_401`** (its then-foothold `denovo_111` was later
withdrawn as protonation-fragile, §2.6) — scaffold-seeded generation conditioned on
the four paralogue-divergent handles (L406/T410/I484/L534), heavily oversampled + developability-gated, and
ranked against the decoy null — with **decoy-calibrated multi-snapshot MM-GBSA** to confirm the survivors and
selectivity FEP reserved for an above-null lead. The decoy control is retained as a **standing specificity
gate** every candidate must clear.

### 2.6 Multi-snapshot de-noising refutes the single-snapshot harvest but confirms one lead (`denovo_401`)
The decoy control (§2.5) showed the *raw* single-snapshot MM-GBSA margin is non-specific. We built the
follow-up tier the §2.5 plan named — **multi-snapshot endpoint MM-GBSA** (`endpoint_dG_multisnapshot`:
minimize → short GB Langevin MD → ΔG averaged over 10 frames + SD) — and ran it on the lead set. It
**independently confirms the noise diagnosis and then isolates a survivor**:

| candidate | single-snapshot margin | **multi-snapshot mean ± SD** | margin − SD | verdict |
|-----------|------------------------|------------------------------|-------------|---------|
| `denovo_393` (was the single-snapshot best, above decoy *max*) | +18.34 | **−2.95 ± 3.65** | — | **collapses** (selectivity gone) |
| `denovo_780` | +14.66 | +2.07 ± 6.36 | <0 | within noise of 0 |
| `denovo_924` (negative control) | −19.41 | −25.20 ± 4.55 | — | stays non-selective ✓ (method discriminates) |
| **`denovo_401`** | +13.92 | **+12.83 ± 2.98** | **+9.85** | **holds** (confirmed_selective) |
| **`denovo_111`** (neutral form; later **withdrawn** — cation reverses, see species resolution) | +15.70 | **+14.60 ± 4.10** | **+10.50** | holds *as neutral* (but protonation-fragile) |

**Figure 5** ([`../modalities/nr4a3-fig5.png`](../modalities/nr4a3-fig5.png); rendered by `nr4a3_journal_figures.py`). The de-novo lead `denovo_401`, across four panels. **(a)** Multi-snapshot de-noising: each candidate's
single-snapshot margin (open circle) vs its multi-snapshot mean ± SD (filled) — the single-snapshot best
`denovo_393` (+18.34) collapses to ~0, the negative control `denovo_924` stays non-selective (the method
discriminates), and only `denovo_401` holds (margin − SD = +9.85, clear of the multi-snapshot decoy-null 95th
percentile +6.69). **(b)** The decoy null is receptor-frame-dependent: `denovo_401` clears the whole same-tier
null in its unbiased *release/design* frame but not in the biased *metad-opened* frame (§2.6). **(c)** 2D
structure of `denovo_401` (MW 304, QED 0.80, SA 3.87, no structural alerts). **(d)** The predicted docked pose
of `denovo_401` (orange) in the metadynamics-opened NR4A3 LBD (teal cartoon; pocket-lining side chains grey)
— a screening-grade *docked* pose in an AF2-derived LBD *model*, an illustration of the predicted binding
geometry, **not** an experimental complex or a validated pose. Single-trajectory GB-implicit MD, not FEP —
direction and robustness, not affinity.

**Supplementary Figure S1** ([`../modalities/nr4a3-figS1.png`](../modalities/nr4a3-figS1.png); generated by
`nr4a3_journal_figures.py` from the §2.6 per-receptor ΔG values). Per-receptor multi-snapshot MM-GBSA
binding ΔG of `denovo_401` against NR4A3 vs NR4A1/NR4A2, in the unbiased *release* (design) frame and the
biased *metad-opened* frame. NR4A3 is the most-favoured receptor in **both** frames (selectivity *direction*
is frame-robust), but the NR4A3-vs-NR4A1 margin shrinks from +14.75 (release) to +7.44 (metad-opened) —
*magnitude* is frame-dependent (as discussed below). Magnitudes are inflated (single-snapshot/no-entropy);
read the ΔΔG direction, not Kd.

Two things follow. (i) The single-snapshot margins carry **SD ~4–6 kcal/mol — larger than the margins
themselves** — so the single-snapshot "above-null" harvest is noise-dominated; `denovo_393`'s +18.34 was an
extreme-value artifact (de-noised, it is ~0/slightly paralogue-favouring). The negative control behaving
correctly (staying non-selective) makes this a **trustworthy refutation, not a method failure**, and it
corroborates the decoy finding from an orthogonal direction. (ii) **`denovo_401` is the exception that
survives**: its multi-snapshot margin (+12.83) is barely below its single-snapshot value, the SD (2.98) is
small, and **margin − SD = +9.85 ≫ 0** — strong, favourable NR4A3 binding (mean ΔG −38.18 kcal/mol) with
both paralogues ~13–15 kcal/mol weaker. So the de-noising tier is **discriminating, not merely destructive**:
it killed a noise artifact and confirmed a genuine lead. `denovo_401`
(`COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1`; MW 304, QED 0.80, SA 3.87, no structural alerts)
is the program's **first multi-snapshot-confirmed NR4A3-selective candidate and the lead queued for
selectivity FEP**. A formal in-silico developability profile (`nr4a3_developability.py`, RDKit) confirms the
binder is **drug-like and clean**: 0 Lipinski violations, **Veber-compliant** (TPSA 29.5, 7 rotatable bonds),
**clean on both the PAINS and BRENK structural-alert catalogs**, and readily synthesizable (SA 3.87). The one
honest watch-item is **lipophilicity (cLogP 4.63)**, to be tracked as the binder is elaborated. As a *binder*,
this is Rule-of-5-compliant; assembled into a CRBN degrader (binder + E3 ligand + linker) the molecule is
projected into normal **beyond-Rule-of-5** PROTAC space (projected MW ~657) — expected for the modality, and
the linker exit-vector build is tracked as an explicit next step (completeness ledger E4). The single-snapshot foothold `denovo_111` also de-noised well **as the neutral form**
(+14.60 ± 4.10) — but a **pre-FEP species-resolution sweep subsequently demoted it**: `denovo_111`
carries a basic pyrrolidine and is **cationic at physiological pH 7.4**, and in that protonation state its
selectivity **reverses** (multi-snapshot margin **−15.01 ± 5.14**, binding NR4A1 *more* tightly than NR4A3,
−36.81 vs −21.80). Its apparent selectivity was a **neutral-form artifact**, so `denovo_111` is **withdrawn as
an FEP candidate** and **`denovo_401` is the sole robust lead** (see the species-resolution paragraph below).

**Honest weight.** `denovo_401` clears the **FEP-worthiness bar this
program pre-committed to** (multi-snapshot margin − SD > 0, favourable NR4A3 binding, stable pose) — which is
a real upgrade over a single-snapshot point estimate — but it is **single-trajectory GB-implicit MD, not
FEP**, **unsynthesized**, and **un-validated**. It is also the **best-of-~10** candidates multi-snapshot-tested
(and best-of-~200 generated), so its +12.83 point estimate carries a **selection (winner's-curse) bias on top
of the reported ±2.98 SD** — the same extreme-value logic that demotes `denovo_393`'s single-snapshot +18.34
applies to picking `denovo_401` as the survivor; an independent re-run (or FEP) is what would de-bias it.
**We ran that independent re-run** (fresh Langevin seed): `denovo_401` reproduces at
**+14.75 ± 4.82** (vs the original +12.83 ± 2.98; ΔG NR4A3 −37.50 / NR4A1 −22.75 / NR4A2 −20.43) — the margin
does **not** regress toward the null under an independent trajectory (it lands slightly higher), so the lead is
**not a single-draw artifact**. This bounds the *within-candidate/seed* variance; the *between-candidate*
best-of-N selection remains a (now-bounded) caveat that only re-selection-from-scratch or FEP fully removes.
The decoy null (§2.5) was originally computed at
*single-snapshot*, so the matching question was whether "+12.83 survives de-noising" is the same as "+12.83
is above a *multi-snapshot* null." **That control has now been run: re-scoring
all 38 decoys through the identical multi-snapshot tier gives a far tighter null — mean −3.47, 95th
percentile **+6.69**, max decoy **+7.10**, `confirmed_selective` 11/38 (29 %) — vs the single-snapshot
+13.1 / +16.46 / 39 %.** Against that re-calibrated bar **`denovo_401`'s +12.83 ± 2.98 clears the
multi-snapshot 95th percentile and exceeds the single highest decoy even after subtracting its SD
(margin − SD = +9.85 > +7.10)** — so the margin is not merely de-noised but **above a decoy null recomputed at
the same tier.** *(Read this at its true weight. That null controls the **docking/MM-GBSA scoring** step
(marketed drugs pushed through the identical dock→multi-snapshot funnel), but it does **not** control the
**generative** step: `denovo_401` is a DiffSBDD molecule pocket-conditioned on the NR4A3 **release** frame,
whereas the decoys were fit to no pocket — so in the release frame `denovo_401` carries a design-match
advantage the decoys lack, which inflates its NR4A3 leg (hence its margin) relative to the null. Consistent
with this, in the **metad-opened** frame — which `denovo_401` was *not* conditioned on, so neither it nor the
decoys have a generation advantage — it does **not** clear the null (below; the paper elsewhere reads that as
the metad frame being non-discriminating, but it is also the less-confounded specificity test). A fully clean
specificity test would require a generation-matched decoy null. That said, the generative-step confound is
**empirically bounded small**: all ~191 developable generations were pocket-conditioned on the *same* release
frame, yet the set is **not enriched** over the marketed-drug decoys and only **two of ~11** multi-snapshot-
tested candidates survive (§2.6) — if being generated-for-NR4A3 uniformly inflated the NR4A3 margin, the whole
generated set would clear the null, and it does not. So against the null we have, "above-null" is a **de-noised
foothold, not yet a fully-controlled specificity result** — but the confound is a bounded caveat, not a
whole-cloth artifact (the decisive resolution is FEP — now complete: a three-replicate NR4A3-selective ΔΔG, §4).)* **A receptor-robustness check (a
fully state-matched re-dock — NR4A3 in its *metad-opened* frame rather than the release frame — then the same
multi-snapshot rescore) keeps `denovo_401` NR4A3-favoured but weaker:
+7.44 ± 4.18 (ΔG NR4A3 −32.37 vs NR4A1 −24.93 / NR4A2 −22.80)** — so the selectivity *direction* is robust
across receptor frames (not a release-frame artifact), but the *magnitude* is frame-dependent. **The matching
metad-frame decoy null has since been run, and it forces an honest narrowing: `denovo_401`
does *not* clear it.** In the metad-opened frame the decoy null *balloons* — mean +1.59, 95th percentile
**+17.70**, max decoy **+24.74** (vs the release frame's +6.69 / +7.10) — because the biased wide-open pocket
scores *most* drug-like matter as strongly NR4A3-favoured (diphenhydramine +24.74, lidocaine +22.08); against
that inflated null `denovo_401`'s +7.44 sits at only ~the **84th percentile** (6/38 decoys score higher). So the
metad-opened frame is a **poor, promiscuous discriminator**, and `denovo_401`'s specificity-controlled result is
**release-frame-specific**: real in its unbiased *design* receptor, but it does **not** generalise to the
biased-open frame. The honest, narrowed claim: *`denovo_401` is the one candidate whose NR4A3-selectivity
survives ensemble de-noising **and** clears a like-for-like multi-snapshot decoy null **in its release (design)
receptor** — a real but **receptor-frame-dependent** signal (it fails the null in the biased metad-opened frame,
which is itself non-discriminating), consistent with the selectivity-architecture analysis (SI §S3), that this cryptic pocket is a fragile place
to source a robust margin.* It stays the justified single candidate to advance to FEP, but as a **frame-dependent
hit, not an unqualified one** — and the right resolution is ensemble scoring over the druggable release
sub-ensemble rather than any single frame (method-watch: better induced-fit/ensemble affinity). **A further 6-candidate multi-snapshot
batch (`denovo_921/277/804/431/838` + the `denovo_924` negative control) returned *no additional survivor*:
the best two, `denovo_921` (+4.22 ± 5.23) and `denovo_277` (+2.23 ± 3.52), are positive-margin but **fail
the margin − SD > 0 bar**, while the negative control stayed non-selective.** So across ~11 candidates now
multi-snapshot-tested, two initially cleared the bar (`denovo_401` and neutral `denovo_111`) — **but the
species-resolution sweep (next paragraph) then withdrew `denovo_111` on protonation grounds, leaving
`denovo_401` as the sole robust lead.** A low hit-rate either way (the funnel does **not** *abundantly* yield
de-noising survivors), with the negative control failing throughout keeping the discrimination trustworthy —
consistent with the selectivity-architecture analysis (SI §S3): a cryptic pocket that is a *fragile but not empty* place to source a margin.

**Pre-FEP species resolution — resolve the exact 3D molecule before spending on FEP.** Because
FEP presupposes a correct, well-defined species, we docked + MM-GBSA-scored **denovo_401's 16 stereoisomers**
(its 4 stereocenters are DiffSBDD-assigned, i.e. arbitrary) and **denovo_111's neutral/cationic forms**.
Two results. (i) **denovo_401's selectivity is stereochemistry-robust and the generated isomer is near-optimal:**
nearly all 16 diastereomers scored `confirmed_selective`, and de-noising the top four gives **iso08 (the
C13-epimer) +11.36 ± 5.25** and the **as-generated isomer +9.54 ± 4.26** as co-best (overlapping within SD),
with iso00/iso14 behind — so all prior denovo_401 results stand on a near-optimal isomer, and the FEP subject
is the iso08/as-generated **epimer pair** (FEP resolves which). (ii) **denovo_111 is withdrawn:** selective as
the neutral form but its **physiological cation reverses** (multi-snapshot **−15.01 ± 5.14**, NR4A1 −36.81 <
NR4A3 −21.80), so its earlier de-noised margin was a neutral-form artifact. Net: **`denovo_401` is the sole
robust lead entering FEP, on a resolved diastereomer.**

## 4. Methods (reproducible, no wet lab)
Scripted in `research/modalities/`, run as managed AWS SageMaker GPU/CPU jobs (GitHub Actions
`gpu-*-aws.yml`). Structure: AlphaFold2 (AFDB) + fpocket (file→pocket mapping derived from data,
`fpocket_lib.py`). Cryptic pocket: OpenMM + PLUMED well-tempered metadynamics with checkpoint/restart and
fail-loud pre-flight guards ([`../modalities/metad-methods-appendix.md`](../modalities/metad-methods-appendix.md)).
**Metastability / Gate 3:** unbiased "release" MD (`nr4a3_md_release.py`, OpenMM, no PLUMED) seeded at the
low-energy druggable frame (triplicate replicas), with per-frame fpocket on the release trajectory; the
druggable receptor for all downstream design is extracted from the release trajectory
(`nr4a3_release_druggable.py`).
Calibration: NR-LBD panel ([`../modalities/nr4a3_calibration.py`](../modalities/nr4a3_calibration.py)).
Falsification: pre-registered gates ([`../modalities/nr4a3-druggability-prereg.md`](../modalities/nr4a3-druggability-prereg.md)).
Selectivity: Biopython BLOSUM62 alignment vs NR4A1/NR4A2. **Superfamily liability screen (SI §S3, A4/D4):**
`nr4a_superfamily_selectivity.py` queries UniProt for every reviewed human NR (family:"nuclear hormone
receptor family", organism 9606; no hardcoded accessions), globally aligns each to NR4A3/Q92570 with the same
BLOSUM62 aligner as `nr4a3_resistance_map.py`, maps the ten warhead-pocket residues, and scores pocket-residue
identity/similarity plus overall LBD identity as a mapping-confidence axis; NR4A1/2 are built-in positive
controls. Pure scoring core unit-tested (`test_superfamily_selectivity.py`). **Family-wide ensembles:** the *same*
metadynamics pipeline is run on NR4A1 (P22736) and NR4A2 (P43354) — one target-agnostic script whose
paralogue LBD trim + Pocket-5 CV residues are mapped to NR4A3 by the same BLOSUM62 alignment, with
fail-loud guards + an audit log — to produce state-matched opened-pocket ensembles for the selectivity
matrix (§2.4). **Warhead / matrix:** smina docking of a real ChEMBL NR4A library into each paralogue's
metad-opened conformer; per-candidate matrix cells assigned by `selectivity_fingerprint.py` (engage/margin
thresholds; unit-tested). **Quantitative tier (run):** single-snapshot 1-trajectory
MM-GBSA endpoint rescoring of the matrix's docked poses (OpenMM + OpenFF/GAFF-2.11 + GBn2 implicit solvent,
AM1-BCC charges; `nr4a3_mmgbsa.py`, OpenCL on the A10G), emitting a per-candidate verdict
(confirmed_selective / reversed / weakened / rescued) vs the docking margins; magnitudes are inflated
(no entropy/ensemble average) and read as direction, not affinity; selectivity FEP on the lead is the next
tier — now **run and complete at three replicates** (result below). **Selectivity FEP
(absolute binding free energy).** One absolute-binding-FEP experiment per receptor (NR4A3/NR4A1/NR4A2):
explicit-solvent (amber14SB + GAFF2 + AM1-BCC + TIP3P, PME) double-decoupling of `denovo_401` with a Boresch
orientational restraint held **identical across all complex-leg λ-windows** and removed **analytically** via
its standard-state correction, so ΔG_bind = ΔG_dec,solv − ΔG_dec,cplx − SSC. The engine (`nr4a3_abfe.py`) is a
**modern independent-λ-window** design rather than a monolithic Hamiltonian-replica-exchange stack: each window
is an independent OpenMM simulation that, every iteration, evaluates the reduced potential at *all* λ and writes
a small per-window checkpoint; MBAR then reduces the per-window samples to each leg's ΔG with a per-iteration
convergence trace. We adopted this specifically for **spot-interruption robustness** — small per-window
checkpoints resume losing ≤1 iteration, whereas the earlier monolithic-`.nc` replica-exchange stack (Yank) lost
long spot runs to all-or-nothing checkpointing — and the engine is **calibrated on two known systems** ([`../modalities/nr4a3-abfe-calibration.json`](../modalities/nr4a3-abfe-calibration.json)):
a **hydration-free-energy** gate (methane ΔG_hyd = **+1.60 ± 0.04** kcal/mol vs experimental +2.0, FreeSolv — a **−0.40**
kcal/mol solvation offset, well within GAFF/TIP3P norms, confirming the ligand-in-water decoupling machinery is sound) and,
newly, a **protein-ligand binding** gate (below) that measures the engine's systematic offset on an *absolute* ΔG_bind before
any absolute is over-read. The
NR4A3-vs-paralogue **ΔΔG** is the selectivity read-out (CUDA on the A10G; SageMaker managed-spot *Training* with
continuous per-window S3 checkpointing). **Completed three-replicate result (2 ns/window, n_iter = 2000; three independent-seed replicates r1/r2/r3, error bars = between-replicate SD, n = 3):** raw-engine per-replicate means are ΔG_bind(NR4A3) = **+3.5 ± 1.4**, ΔG_bind(NR4A1) = **+8.3 ± 1.1**, ΔG_bind(NR4A2) = **+8.5 ± 0.7** kcal/mol → **ΔΔG(NR4A3 − NR4A1) = −4.76 ± 2.03** and **ΔΔG(NR4A3 − NR4A2) = −4.98 ± 0.68** kcal/mol (both favour NR4A3). The selectivity **direction is unanimous — NR4A3 is the tightest-bound of the three in every one of the three replicates** — so `denovo_401` is predicted to engage the opened NR4A3 pocket and not the paralogues. These are now **replicate-based error bars (accuracy, not the earlier single-replicate MBAR ±0.2 precision)**, and they tell an honest story: the **NR4A2 margin is tight (± 0.68)** — smaller than either leg's absolute SD, the shared ligand-in-water decoupling and common-mode charge/protonation error cancelling in the difference as hoped — whereas the **NR4A1 margin is wider (± 2.03)**, driven by one replicate (r2) whose NR4A3 leg sampled ~2.5 kcal/mol weaker binding (raw +5.1 vs +2.6/+2.8 in r1/r3); that single soft draw both shrank r2's NR4A1 margin *and* inflated its NR4A3 absolute, so the NR4A1 ΔΔG does **not** tighten (excluding r2, r1/r3 agree closely at ΔΔG(NR4A3−NR4A1) = −6.9/−4.5). The honest read: **robust, tight NR4A2 selectivity and directionally-robust-but-noisier NR4A1 selectivity**, both clearing ~5 kcal/mol on the mean. This ~1–2 kcal/mol replicate scatter is exactly what the earlier single-replicate MBAR ±0.2 could not see; the three-replicate ensemble replaces that optimistic precision with realistic accuracy, and the ~5 kcal/mol selectivity survives it in both contrasts. **We do not report calibrated absolute ΔG_bind.** The engine mis-predicts a rigid textbook benchmark
(T4-lysozyme L99A + benzene) by ≈ +7.1 kcal/mol (below), which we read as a *failed/strongly-biased
absolute benchmark* — evidence the protocol is not yet validated for absolute affinity — **not** as a
universal additive engine constant to subtract from NR4A3. The raw-engine NR4A3 absolute (+3.5) is
therefore not quantitatively interpretable on its own; the selectivity conclusion rests entirely on the
**ΔΔG**, which is unaffected by any common per-engine bias. *(Reduced 2026-07-08 with a per-window dedup-by-iteration safeguard on the MBAR input, so the crash/resume/recovery history of the nr4a2 legs — see the run notes — does not double-count samples or shrink the SE.)* **The absolute benchmark, read honestly as a failed benchmark — not a calibration constant.**
To gauge whether the engine reports meaningful *absolute* affinities, we ran it on a
**known protein-ligand binding free energy — T4-lysozyme L99A + benzene** (rigid textbook cavity, experimental ΔG_bind =
−5.2 kcal/mol; Morton & Matthews 1995; PDB 181L), through the identical double-decoupling + Boresch-restraint + MBAR path
(12 windows, 1000 iterations, same baked engine). It returns **ΔG_bind = +1.90 ± 0.09 kcal/mol** — i.e. the engine
**under-binds this benchmark by ≈ +7.1 kcal/mol** (rigorous literature ABFE on this system is −5 to −6.5 kcal/mol).
We treat this as what it is: a **failed / strongly-biased absolute benchmark**, indicating the automated,
single-replicate, 1-ns/window protocol is **not yet validated for absolute affinity** (it under-samples cavity
water / ligand orientation). We explicitly **do not** treat +7.1 kcal/mol as a universal additive engine offset:
a single system cannot establish a target-independent constant, because absolute-ΔG error (force field, water
sampling, receptor reorganization, restraint/standard-state handling, finite sampling) is system-dependent.
Accordingly we **make no offset-corrected absolute claim** and rest the selectivity conclusion on the **ΔΔG**.
Two consequences follow. **(i) The ΔΔG is robust to common-mode error, argued empirically (not "cancels
exactly").** A per-engine bias cancels in a receptor-vs-receptor difference only to the extent it is *common*
across the three receptors; because the ligand, restraint scheme, and ligand-in-water leg are literally
identical, much common-mode error (charge/protonation, solvent decoupling) is expected to cancel — and this is
**borne out for NR4A2** (ΔΔG SD 0.68 < either leg's absolute SD) but **not fully for NR4A1**, where one
anti-correlated replicate defeats the cancellation in an n = 3 sample. So we claim *substantial*, not *exact*,
cancellation. **(ii) The ΔΔG is a *conditional* binding selectivity, not the full thermodynamic selectivity.**
The calculation compares `denovo_401` binding to *selected opened* NR4A3/NR4A1/NR4A2 conformers, so it estimates
ΔG_bind **conditional on the receptor already being in its opened state** — it **omits the receptor-specific
free-energy cost of populating that cryptic-opened conformation**. For a paper whose premise is a cryptic pocket,
this term is potentially decisive and may differ across the three paralogues (their opening penalties are not
shown equal): a ligand can bind a rarely-populated pre-opened conformer strongly yet bind the equilibrium apo
ensemble weakly, and paralogue-specific opening penalties could narrow or even reverse the conditional margin.
The ensemble/state-weighted ABFE that would close this — per-paralogue opening free energies folded into a
state-weighted ΔG_bind — is **not done here** and is a primary revision task (§5); the reported ΔΔG must be read
as **conditional-on-opened-conformer** selectivity. Full calibration record:
[`../modalities/nr4a3-abfe-calibration.json`](../modalities/nr4a3-abfe-calibration.json).

**Lead-optimization cross-check.** A single scaffold-decorated variant (`lo_m0_NCCO` = `denovo_401` + ortho-acetamido) was put through the identical ABFE engine as an affinity-grade check of an MM-GBSA-predicted tightening and lands **within statistical noise of `denovo_401`** — a validated *equal*, not an advance (free energy does not reproduce the MM-GBSA-predicted gain), so `denovo_401` remains the program's strongest candidate; detail in **SI §S5**.

**Why absolute
(ABFE), not relative/mutation, FEP.** The selectivity question is *one* ligand (`denovo_401`) against *three
different* proteins, so there is no ligand pair to alchemically morph — standard relative binding FEP (RBFE),
which transforms ligand A→B within one pocket, does not apply. The relative alternative that *would* fit is
**alchemical protein-mutation FEP** (morph the divergent NR4A3→NR4A1/2 pocket residues, bound vs apo, for a
direct ΔΔG). We deliberately use per-receptor ABFE instead, for three reasons. (i) *Conformational.* Each
paralogue is engaged in its own **induced/opened** conformation of a cryptic LBD pocket (§2.1–2.2); alchemical
mutation assumes the two proteins are related by point substitutions along a smooth path in a *shared*
conformation and is fragile to backbone/induced-state differences — precisely the regime here — whereas ABFE
models each receptor independently in its own opened frame. (ii) *Precedent.* ABFE is an established route to
selectivity across related/paralogous pockets (e.g. bromodomain-selectivity ABFE — Aldeghi et al. 2017), so this is a paved-road application, not a bespoke one. (iii) *Bonus observable.* ABFE
additionally yields each **absolute** ΔG_bind — i.e. whether `denovo_401` engages NR4A3 at all — which the
relative framing never produces. The one cost of ABFE (larger per-leg error than a relative calculation) is
partly recovered here: because the ligand is identical across all three experiments, the solvent-decoupling
leg is literally the same calculation for each receptor and cancels in the ΔΔG, along with common-mode
ligand-charge/protonation error, so the *selectivity* ΔΔG is better-behaved than either raw absolute number.
A confirmatory alchemical-mutation cross-check is left as future work, gated on the pocket-homology assessment
noted in [`../method-watch.md`](../method-watch.md). **Receptor prep for
FEP:** the docked opened frame is cleaned with `pdb4amber` (LEaP-compatible, drops MD hydrogens/waters) and its
**disordered N-terminal hinge is trimmed to the folded LBD core** (`_trim_floppy_termini`, adaptive, pocket
never trimmed) — justified by the structural-sanity control (§2.2: fold intact, core RMSD 1.76 Å) and standard
for ABFE (run on the folded domain, not the disordered tail); this also keeps the explicit-solvent box within a
single commodity GPU. **De-novo design:** a selectivity blueprint (`denovo_blueprint.py` → `nr4a3-denovo-blueprint.json`)
classifies the Pocket-5 lining residues into the five engageable selective handles (four discriminating
both paralogues — L406/T410/I484/L534 — and the NR4A1-only lever I531) vs the conserved core
(P411/R481/R485), weighting the both-paralogue handles in the selective campaign; DiffSBDD pocket-conditioned
diffusion (pretrained CrossDocked weights; `nr4a3_denovo.py` + `entry_denovo.py`) conditioned on the
druggable release-frame pocket / divergent handles, with a lead-size constraint and an RDKit cheminformatics
+ pose-handle-contact triage (`denovo_funnel.py`); generated candidates are funneled through the same matrix dock + MM-GBSA pipeline
(`nr4a3_matrix.py` candidate mode). Docking scores are used only as triage priors. All
parsing/mapping/classification/scoring logic is in pure, unit-tested modules (TESTING.md).

## 5. Limitations
In-silico throughout; no molecule synthesized; broader indications (SI §S4) are **motivation, not
demonstrated efficacy**. **In particular, the therapeutic rationale for degrading NR4A3 in EMC (and
AciCC) assumes the tumour remains *dependent on NR4A3 for survival*, which is not yet demonstrated in
EMC.** Two kinds of support raise this prior, each stated with its boundary so neither is mistaken for
proof:
- **A transfer prior — used to justify *testing* the target, not as EMC evidence.** Related EWSR1/FET-fusion
  sarcomas are reliably *fusion-addicted* (Ewing/EWS-FLI1: −0.93 DepMap gene effect, 74 % of lines
  dependent), and EMC shares the profile that makes addiction the class norm — a quiet genome with a single
  near-clonal fusion driver. Reasoning from a represented lineage to an un-profiled one this way is standard
  practice for prioritising a target; it raises the prior and warrants the experiment, but it **cannot
  establish EMC dependence**. Its transferable content is also bounded: what these fusions share is the
  **EWS low-complexity transactivation domain**, so the analogy supports "EMC is probably addicted to its
  fusion," **not** "the NR4A3 effector specifically is the essential part" (EWS-FLI1's ETS-domain mechanism
  at GGAA microsatellites differs from a nuclear receptor) — a caveat that matters because the degrader
  engages the NR4A3 end.
- **EMC-specific molecular evidence (non-transfer) that the fusion is a functional transcriptional driver.**
  The chimera directly transactivates real targets — most concretely **PPARG**, via a bioinformatically
  identified EWSR1/NR4A3 response element in the PPARG promoter confirmed by band-shift and transactivation
  assays [Filion 2009], with further EMC-over-expressed targets reported (e.g. NDRG2). This is EMC-native
  support that the fusion *does something* transcriptionally — but it shows the fusion is a functional
  driver, **not** that the cell cannot survive its loss; *functional driver ≠ addiction*.
- **The fusion is a near-invariant, clonal driver in a quiet genome (quantified; verified evidence base:
  [`nr4a3-emc-biology-evidence.md`](./nr4a3-emc-biology-evidence.md)).** An **NR4A3 rearrangement is
  near-pathognomonic for EMC (~90–98 % of cases)** — EWSR1::NR4A3 in ~62–79 % (58/58 NR4A3-rearranged in a
  58-case cohort, Modern Pathology 2023 [PMID 36948401]; 24/26 in Agaram *Hum Pathol* 2014 [PMC4015728]) —
  with NR4A3 the **invariant 3′ partner** regardless of the 5′ gene. It is the **shared founding/clonal lesion**
  across matched primary + metastases in a **genomically quiet** tumour (matched-trio WGS, [PMC11285543]; EMC is
  <3 % of soft-tissue sarcomas). A single invariant clonal driver in a quiet genome is the textbook
  oncogene-addiction *profile* — a materially stronger prior than a lone analogy, though still a prior.

**The one decisive gap, stated plainly: there is NO direct loss-of-function experiment in any EMC cell line —
every published EMC functional result is *gain-of-function* (transactivation, transformation of non-EMC cells);
no RNAi/CRISPR/ASO knockdown of NR4A3 or the fusion in a human EMC model (e.g. H-EMC-SS) with a survival readout
exists** (verified 2026-07-02, [`nr4a3-emc-biology-evidence.md`](./nr4a3-emc-biology-evidence.md)). So the
multi-pillar case above is a strong *prior*, not demonstrated dependence. The acute, specific degradation (dTAG)
test that would convert this prior into a demonstration is the make-or-break experiment, delegated to the
EMC-program paper ([`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md)); **this paper's claimed contribution
is the target's druggability/selectivity, not EMC efficacy.**

**Safety/tolerability, and the pan-NR4A/CAR-T pole — bounded in SI §S6 and §S4.** The systemic lead's tolerability case (the NR4A family's proliferative dispensability by DepMap; the *myeloid* NR4A1↔NR4A3 redundancy that makes NR4A1-sparing mandatory; broad NR4A1/NR4A3 co-expression; PK/CNS restriction) is quantified in **SI §S6**. Two load-bearing caveats carry back into main text: human germline genetics (gnomAD) **invalidates the glib "dispensable ⇒ safe" inference** and makes **NR4A2-sparing a safety requirement** — NR4A2 is the most LoF-constrained *and* CNS-enriched paralogue (LOEUF 0.094), NR4A3 borderline (LOEUF 0.37, pLI-intolerant) — and single-KO tolerability remains an *assumption* (no phenotyped IMPC KO for any of the three). The pan-NR4A / CAR-T pole is bounded separately and more tightly in **SI §S4** (chemical-feasibility only — the framework can *design* a pan-NR4A binder, not that it reverses T-cell exhaustion — plus an ex-vivo washout/exposure parameter).
The structure is an AF2 model
(NR4A3 has no ligand-bound experimental structure; its apo LBD was released as a solution-NMR ensemble,
PDB 8XTT, only in 2025) — the MD addresses exactly the single-snapshot limitation. **A load-bearing
revision task, not yet done here:** the AF2 pocket, its metadynamics-opened geometry, the PocketMiner
call, and the ten pocket-lining / seven divergent-handle positions must all be benchmarked against the
20-conformer 8XTT ensemble (global and pocket-local RMSD to each conformer; per-frame fpocket across the
ensemble; PocketMiner re-run on 8XTT; re-seeded unbiased MD from representative 8XTT conformers). If the
experimental ensemble supports the AF2 pocket and handles, this becomes the study's strongest validation;
if it does not, the downstream design is rebased on 8XTT. We state the central result at its true weight,
with five caveats made explicit rather than buried:

1. **The 0.931 is a biased-ensemble peak, not a like-for-like beat of the static band.** fpocket
   druggability is a standard, model-derived geometric proxy (a logistic model of hydrophobic enclosure +
   polarity, not raw volume; §2.1 anchors it on an NR panel incl. the occluded 1OVL negative) — a
   druggability *prediction*, not a ground-truth measurement.
   But (a) 0.931 is the **maximum over 600 frames** — report it as a distribution (fraction of frames
   ≥ D\*=0.53, met) with 0.931 as the peak; and (b) it is computed on **biased-MD** conformations, so its
   magnitude is not directly comparable to the *static* drug-bound crystal sites (0.53–0.68) — we do not
   claim it beats that band. fpocket druggability is in any case a geometric screen, not affinity. Whether
   the breathing-open geometry is physically populated vs bias-induced strain is settled by the release
   run, not by an fpocket control.
2. **No separate opened free-energy basin.** F(Rg) is monotonic (one closed basin, rising wall); the
   druggable conformations are reached by *basin-internal breathing*, not a two-state cryptic opening, so
   the pre-registered Gate 1 ("minimum or shoulder, not just biased excursions") **failed as registered**
   and was **reformulated** as basin-breathing. "Opened state" is shorthand for these breathing sub-states,
   not a distinct metastable conformation.
3. **Gate 3 accessibility — now release-confirmed as an induced-fit cavity, not always-open.** The
   ~0.76 kcal/mol cost to a druggable conformation and ~38 kcal/mol to the open edge are read off the *same*
   incompletely-converged biased F(Rg), so those numbers remain provisional; but the *independent*
   metastability test is no longer pending. The unbiased release run (seeded at the low-energy druggable
   frame) shows the breathing-open geometry is **metastable (3/3 replicas) and druggable in ~24 % of
   unbiased frames** — consistent with a release-derived, **induced-fit-like** cavity (not a
   bias artifact), but explicitly **not** a static always-open pocket (unbiased mean druggability 0.262).
   The design consequence is real: the warhead must select-and-stabilise the ~quarter of conformations that
   are druggable, which is a harder ask than occupying a permanent pocket.
4. **Selectivity handles are a specification with an asymmetric window.** The registered handle-facing
   check confirms the handles stay pocket-facing in the druggable frames (mean 5.0/7; T407/R412 splay out,
   so five engageable). But the engageable *divergent* set is **5 vs NR4A1 and only 4 vs NR4A2** (I531 is
   conserved with NR4A2), so NR4A2 selectivity is the harder, narrower case — and these are a specification,
   not a demonstrated binding margin.
5. **Binding selectivity ≠ degradation selectivity — and that reallocates the whole selectivity problem
   (SI §S3).** The §2.4 matrix is a necessary-not-sufficient filter; degradation selectivity is set by the
   per-paralogue ternary complex (the planned gating step). The selectivity-architecture analysis sharpens
   this from a caveat into a design: selectivity is a **multiplicative budget** (binding × ternary ×
   kinetics) whose factors **compound**, so the binder need not carry it *alone* — but a selective binder is
   still strictly valuable and is the primary goal (`denovo_401` is a decoy-null-screened foothold, not fully
   control-validated (the decoy null does not control the generative step); the second candidate denovo_111 was withdrawn as protonation-fragile — §2.6). The
   computed result that the orthosteric pocket is the *most* paralogue-divergent zone of the LBD
   (70 % vs 43 % across the rest of the LBD) means binder selectivity is handle-rich but
   druggability/noise-limited — so the rational plan keeps the binder selective **and** optimizes it for
   affinity + a productive exit vector. The hoped-for *additional* lever — sourcing paralogue selectivity from
   the **ternary** — **has now been tested (§2.4) and, for a representative PROTAC, does not materialize**:
   NR4A3/NR4A1/NR4A2 form equally productive ternaries, so the ternary does **not** compound the binder's NR4A1
   margin as hoped. Degradation selectivity therefore rests, on current evidence, on the **binder** (plus
   **pharmacokinetics / CNS-exclusion** for NR4A2, whose tox is CNS-localized), with **linker/exit-vector
   engineering** the only remaining (untested) route to ternary selectivity; and **fusion-vs-wild-type**
   selectivity remains **unobtainable from the degrader** (route to the ASO). Net: running the ternary
   *narrowed* the budget rather than widening it — the binder carries more of the load than the architecture
   originally hoped.
6. **The de-novo lead is a chemotype/pose hypothesis with flagged liabilities, not a developable molecule.**
   `denovo_15` carries DiffSBDD-typical instability/synthesizability liabilities (carbamic acid,
   1,3-cyclopentadiene, imine, exocyclic alkene; no aromatic ring; SAscore 5.08 > the campaign's ≤4.5 cut) —
   QED does not screen these. The durable claim is the *funnel and the selectivity direction*, not the
   specific molecule; a stability/reactivity filter + re-generation (and a check of the other two
   `confirmed_selective` hits, denovo_94/57) are the next de-novo steps.
7. **Single-snapshot MM-GBSA is non-specific; multi-snapshot de-noising AND its matching decoy
   re-calibration are now run, and `denovo_401` clears them — leaving FEP as the last tier, now run and complete (three replicates).** The de-novo
   funnel originally docked an *unbiased-release* NR4A3 receptor against *biased-metad* paralogue receptors
   (asymmetry conservative for NR4A3-selectivity — §2.5), and the single-snapshot, single-pose MM-GBSA carries
   no replicate/ensemble average and **fails the decoy control** (§2.5). Two follow-up controls
   resolve this (§2.6): (a) the **multi-snapshot decoy null** (all 38 decoys re-scored
   multi-snapshot: 95th pct +6.69, max +7.10) — `denovo_401` (+12.83 ± 2.98, margin − SD +9.85) **clears it**,
   so the margin is above a decoy null recomputed at the same tier, not merely de-noised — **but that null
   controls the docking/MM-GBSA scoring step only, not the generative step or the best-of-N selection:
   `denovo_401` was DiffSBDD-fit to the release frame it clears the null in, while the decoys were fit to no
   pocket, and it is the best of ~200 generations / ~10 de-noised candidates. So this is a de-noised
   *foothold*, not a demonstrated specificity result** (consistent with its metad-frame failure below, the
   frame it was *not* designed for); and (b) a **fully
   state-matched re-dock** (NR4A3 metad-opened) — `denovo_401` stays NR4A3-favoured (+7.44 ± 4.18), confirming
   the *direction* is not a release-frame artifact, though the magnitude is frame-dependent. **The matching
   metad-frame decoy null was then run (§2.6) and, honestly, `denovo_401` does *not* clear it**: in the biased
   metad-opened frame the decoy null balloons (95th +17.70, max +24.74, driven by drugs like diphenhydramine
   +24.74) and +7.44 sits at only ~the 84th percentile — so the metad-opened frame is a poor discriminator, but
   it is also the frame `denovo_401` was *not* generatively fit to, so the above-null result is
   **release-frame-specific (= design-frame-specific)**, not universal. What remains is
   **single-trajectory GB-implicit MD, not FEP**, so **selectivity FEP is the quantitative gate — now run and complete** (three-replicate ΔΔG NR4A3-selective);
   the receptor-frame dependence is best resolved by ensemble scoring over the druggable release sub-ensemble.

**Selectivity methodology:** docking margins are **triage priors, not affinities**; a quantitative
selectivity claim needs endpoint free energy. The state-matched NR4A1/NR4A2 metadynamics runs are
**complete**, so the matrix (§2.4) is genuinely state-matched (not opened-target-vs-static-off-target), and
the quantitative tier is now **MM-GBSA-run** rather than planned — but single-snapshot MM-GBSA has **no
entropy and no ensemble average**, so its magnitudes are inflated and only the **verdict/direction** is
trusted; **selectivity FEP** (the defensible affinity tier) is **now run** (modern independent-window ABFE;
three-replicate NR4A3-selective ΔΔG, §4), and even converged FEP on a
cryptic/induced-fit pocket is sampling-limited. **An independent structural cross-check (AF3-class
co-folding) does not corroborate the pose/pocket, and honestly cannot here.** To test the docked binder
pose by a physically different method than docking/MD, we co-folded `denovo_401` into each NR4A{3,1,2} LBD
with **Boltz-2** (an open AF3-class protein–ligand structure predictor), control-validated on CRBN +
lenalidomide (the known imide pose recovered: ligand-interface iptm 0.99, protein↔ligand pair-iptm 0.78).
For all three NR4A paralogues the protein **fold** is confident (chain pTM 0.91–0.96) but the **ligand
placement** is not (protein↔ligand pair-iptm 0.23–0.32; ligand_iptm 0.77–0.87), and the cross-paralogue
ordering does **not** favour NR4A3 (if anything NR4A3 is lowest, though the three are within noise of each
other). This is exactly the regime where co-folding is unreliable — a cryptic/induced-fit pocket in an
**orphan** receptor with no ligand-bound training structures, plus a de-novo warhead — so the low confidence
is neither surprising nor evidence against binding; but it means an orthogonal method **cannot independently
corroborate** the docked pose or the ABFE selectivity. The structural-model assumption (the AF2-derived,
metadynamics-opened pocket) therefore remains the **load-bearing uncertainty**, and this class of tool
cannot currently discharge it. The newly released apo 8XTT ensemble can now benchmark the apo pocket
geometry and handle map (the primary revision task, §5), but only a **ligand-bound** experimental
structure can validate the opened, warhead-engaged pose
([`../modalities/nr4a3-binary-cofold-result.json`](../modalities/nr4a3-binary-cofold-result.json)).
Crucially, the **single-snapshot MM-GBSA "confirmed_selective"
verdict that originally nominated `denovo_15` failed a decoy control** (§2.5): it labels 39 % of non-NR4A
marketed drugs "NR4A3-selective," so a raw two-tier (docking + single-snapshot MM-GBSA) survival is **not**
selectivity evidence, and the earlier "MM-GBSA-confirmed selective" headline (and `denovo_15` as the lead) is
**retracted**. What survives is a single de-noised foothold: **`denovo_401`**, the one candidate whose margin
**survives multi-snapshot de-noising** (+12.83 ± 2.98, margin − SD = +9.85; §2.6) and **clears a same-tier
multi-snapshot decoy null in its design frame** (§2.6), and which is the subject of the completed three-replicate
selectivity FEP (§4). (The earlier decoy-calibrated single-snapshot foothold `denovo_111` — +15.7 vs the +13.1
95th-percentile bar; §2.5 — was subsequently **withdrawn**: its physiological cation reverses selectivity, §2.6.)
It remains a **screening-grade, single-trajectory GB-implicit, unsynthesized, no-wet-lab** candidate —
corroborated by FEP but not experimentally validated. With no wet lab, the strongest honest claim is
**"computationally designed for, and predicted by absolute-binding FEP to retain, the intended NR4A3-selectivity
profile,"** not "selective." Matrix cells are gated by degradation *direction* and bounded by the AML
anti-target (SI §S4); and binding selectivity is still necessary-not-sufficient for *degradation* selectivity
(caveat 5).

## 6. Falsification (pre-registered)
Every gate has a fixed pass/fail set *before* the production numbers
([`../modalities/nr4a3-druggability-prereg.md`](../modalities/nr4a3-druggability-prereg.md)). Two
gate outcomes deviate from the literal pre-registration and are **disclosed, not silently swapped**, in
that file's deviation log: (i) the **Gate 0** metric (max → orthosteric/ligand-site, D\*=0.53 — a *real*
drug-bound bar, not a laxer one); and (ii) **Gate 1**, which asked for a free-energy *minimum or shoulder*
at an opened Rg "not just biased excursions" — F(Rg) is instead monotonic, so Gate 1 is reported as
**failed as pre-registered** (no separate opened basin) and **reformulated** into the *basin-breathing*
hypothesis the release run then tested. The metastability question that
deferral left open is now **answered by the completed unbiased release run** (§2.2): the breathing-open
geometry is metastable (3/3 replicas) and druggable in ~24 % of unbiased frames, i.e. an induced-fit cavity
rather than bias-induced strain — so **Gate 3 is cautiously passed** (as conformational selection), not
deferred. We explicitly do **not** claim "Gates 0–3 all pass" as *unqualified* passes — Gate 1 holds only
in the weaker basin-breathing sense and Gate 3 as an induced-fit (not always-open) cavity. The route is
abandoned (weight shifting to ASO/immuno backups in the roadmap) if the opened conformations are not
druggable, not energetically accessible (the release run would have collapsed them as bias-induced strain —
it did **not**), or no selective drug-like binder can be designed.

**Gate 4 (a selective, drug-like ligand can engage the opened pocket) — met in silico by a single
de-noised, FEP-corroborated foothold, not an unqualified pass.** The pre-registered Gate 4 asked for
drug-like matter that docks with a reasonable score, contacts a meaningful subset of the selectivity handles,
and shows a predicted selectivity margin vs NR4A1/NR4A2. The lead **`denovo_401`** meets this in silico across
four tiers: it docks into the druggable release pocket contacting 4 of the 5 engageable handles; it is
NR4A3-favoured at docking and, crucially, its selectivity **survives multi-snapshot endpoint MM-GBSA**
(margin +12.83 ± 2.98, margin − SD = +9.85) where the single-snapshot harvest collapses (`denovo_393`
+18.34 → −2.95 ± 3.65; §2.6); that de-noised margin **clears a same-tier multi-snapshot decoy null in its
design frame** (95th percentile +6.69, max decoy +7.10; §2.6); and it is **corroborated by three-replicate
absolute-binding FEP** (ΔΔG −4.76 ± 2.03 vs NR4A1, −4.98 ± 0.68 vs NR4A2; §4). Unlike the retracted
single-snapshot artifact `denovo_15`, `denovo_401` is developable (PAINS/BRENK-clean, SA 3.87, no structural
alerts). Three honest limits keep this short of an unqualified pass: the decoy null controls the *scoring*
step only, not the *generative* step (`denovo_401` was pocket-conditioned on the release frame the decoys
were never fit to) or the best-of-~200 selection; the margin does **not** survive into the non-design (biased
metad-opened) frame, which is itself a poor discriminator; and the ensemble tier is single-trajectory
GB-implicit MD, with no generation-matched null and no wet-lab validation. So Gate 4 is **met in silico by a
de-noised, FEP-corroborated lead** — the strongest the in-silico evidence supports — not a
specificity-controlled or experimentally validated pass. (The earlier nominal Gate-4 pass on the
single-snapshot `denovo_15` verdict is retracted — it failed the decoy control and carries generative-model
liabilities — and the interim decoy-calibrated foothold `denovo_111` was withdrawn on protonation grounds
(§2.5–2.6); both deviations are disclosed in the prereg deviation log.)

## References
- Wang Z, et al. *Structure and function of Nurr1 identifies a class of ligand-independent nuclear
  receptors.* **Nature** 423:555–560 (2003). PubMed 12774125. (PDB 1OVL.)
- de Vera IMS, et al. *Defining a Canonical Ligand-Binding Pocket in the Orphan Nuclear Receptor Nurr1.*
  **Structure** 27(1):66–77.e5 (2019). PubMed 30416039; doi 10.1016/j.str.2018.10.002.
- Lanig H, et al. *In Silico Adoption of an Orphan Nuclear Receptor NR4A1.* **PLoS ONE** 10:e0135246
  (2015). PMC4535767; doi 10.1371/journal.pone.0135246. (MD-revealed cryptic druggable pocket in Nur77/NR4A1.)
- Zaienne D, et al. *Druggability Evaluation of the Neuron Derived Orphan Receptor (NOR-1) Reveals Inverse
  NOR-1 Agonists.* **ChemMedChem** 17(16):e202200259 (2022). PMC9542104; doi 10.1002/cmdc.202200259. (Merk
  group. **Direct experimental ligandability of NR4A3/NOR-1:** fragment screen, <1 % hit rate → 3 chemotypes,
  one elaborated to a low-µM inverse agonist that alters NOR-1-regulated gene expression in cells — the
  experimental druggability our in-silico pocket supplies a structural mechanism for. Binding site not
  structurally defined by that work.)
- Safe S, Oany AR, Tsui WN, Lee M, Srivastava V, Upadhyay S, et al. *Orphan nuclear receptor transcription
  factors as drug targets.* **Transcription** 16:224–260 (2025). PMID 40646688; PMC12263127;
  doi 10.1080/21541264.2025.2521766. (Safe-group review; source for the **NR4A3-selective carboxymethyl-
  indole-3-carbinol analogues** (cpds 1 & 19, IC₅₀ ≈ 8–47 µM) that de-repress the NR4A3 target gene *MYC*.
  Secondary/review source for those compounds.)
- Willems S, Morozov V, Marschner JA, Merk D. *Comparative Profiling and Chemogenomics Application of Chemical
  Tools for NR4A Nuclear Receptors.* **J Med Chem** 68:19955–19970 (2025). doi 10.1021/acs.jmedchem.5c00459.
  (Family-wide NR4A1/2/3 profiling: validates a vetted probe set — 5 agonists + 3 inverse agonists — and shows
  several putative NR4A ligands lack on-target binding; disciplines repurposed-chemotype selectivity claims.
 )
- Muñoz-Tello P, Lin H, Khan P, de Vera IMS, Kamenecka TM, Kojetin DJ. *Assessment of NR4A Ligands That Directly
  Bind and Modulate the Orphan Nuclear Receptor Nurr1.* **J Med Chem** 63(24):15639–15654 (2020). PMID 33289551;
  PMC8006468; doi 10.1021/acs.jmedchem.0c00894. (NMR footprinting: amodiaquine/chloroquine/cytosporone B **bind**
  the NR4A2 LBD; celastrol/C-DIM12/TMPA **do not** — directly disciplines the §2.4 repurposed-matrix chemotypes.
  Nurr1/NR4A2, not NR4A3.)
- Stiller T, Merk D. *Exploring Fatty Acid Mimetics as NR4A Ligands.* **J Med Chem** 66(22):15362–15369 (2023).
  PMC10683012; doi 10.1021/acs.jmedchem.3c01467. (92-fragment screen → 11 scaffolds → sub-µM NR4A ligands, with
  NOR-1/NR4A3 tested in a Gal4 reporter — reinforces NR4A3 ligandability; caveat: cellular reporter, not direct
  NR4A3 binding.)
- Rajan S, et al. *Prostaglandin A2 Interacts with Nurr1 and Ameliorates Behavioral Deficits in a Parkinson's
  Disease Fly Model.* **NeuroMolecular Med** (2022). PMID 35482177; PDB 5YD6. (PGA2 forms a **covalent Michael
  adduct at Cys566** of the Nurr1 LBD — a covalent-warhead binding-mode precedent in the NR4A LBD.)
- Sturm/Willems, Marschner JA, Merk D, et al. *Structural and mechanistic profiling of Nurr1 modulation by
  vidofludimus enables structure-guided ligand design.* **Commun Chem** (2025). PMC12095788;
  doi 10.1038/s42004-025-01553-8. (Closest computational NR4A-selectivity precedent; MD/mutagenesis map an
  **allosteric surface pocket** and reaffirm the canonical pocket is occluded — the occluded-pocket challenge
  engaged in §2.1.)
- Wang L, Xiao Y, Luo Y, et al. *PROTAC-mediated NR4A1 degradation as a novel strategy for cancer immunotherapy.*
  **J Exp Med** 221(3):e20231519 (2024). PMID 37609171; doi 10.1084/jem.20231519. (**NR-V04** — the only NR4A
  targeted-degrader precedent; selectively degrades NR4A1 while sparing NR4A2/NR4A3, so paralog-selective
  degradation is achievable. Proof-of-concept only; sparing mechanism unresolved, celastrol warhead promiscuous.
 )
- Haller F, et al. *Enhancer hijacking activates oncogenic transcription factor NR4A3 in acinic cell
  carcinomas of the salivary glands.* **Nat Commun** 10:368 (2019). PMC6341107; doi 10.1038/s41467-018-08069-x.
  (AciCC = NR4A3-over-expression-driven; the second NR4A3-selective indication.)
- Lee DY, et al. *Oncogenic Orphan Nuclear Receptor NR4A3 Interacts and Cooperates with MYB in Acinic Cell
  Carcinoma.* **Cancers** 12(9):2433 (2020). PMC7565926; doi 10.3390/cancers12092433. (NR4A3–MYB
  cooperation in AciCC.)
- Khan J, Ullah A, Goodbee M, Lee KT, Yasinzai AQK, Lewis JS Jr, Mesa H. *Acinic Cell Carcinoma in the 21st
  Century: A Population-Based Study from the SEER Database and Review of Recent Molecular Genetic Advances.*
  **Cancers** 15(13):3373 (2023). PMID 37444483; PMC10340722; doi 10.3390/cancers15133373. (AciCC epidemiology — third most
  common salivary-gland malignancy; the SI §S4 relative-incidence anchor.)
- Stacchiotti S, Baldi GG, Morosi C, Gronchi A, Maestro R. *Extraskeletal Myxoid Chondrosarcoma: State of the
  Art and Current Research on Biology and Clinical Management.* **Cancers** 12(9):2703 (2020). PMC7563993;
  doi 10.3390/cancers12092703. (EMC ultra-rare, <1 per 1,000,000/year; the SI §S4 EMC-incidence anchor.)
- EMC biological-rationale evidence base (efficacy + safety; verified 2026-07-02, full citations +
  honest gaps in [`nr4a3-emc-biology-evidence.md`](./nr4a3-emc-biology-evidence.md)). Key primary sources
  newly cited in §5: EMC fusion-partner frequency — Huang et al., *Mod Pathol* 36(7):100161 (2023, PMID 36948401)
  and Agaram et al. *Hum Pathol* 45:1084–1091 (2014, PMC4015728; PMID 24746215); EMC
  quiet-genome / clonal WGS — *Front Mol Med* 2023 (PMC11285543); myeloid NR4A1/NR4A3 redundancy — Freire &
  Conneely, *Blood* 131:1081 (2018, PMID 29343483); NR4A DNA-binding grammar — NR4A2-DBD structures *J Biol
  Chem* (2020, PMC6926456, PDB 6L6Q/6L6L); FET-fusion (EWS-FLI1) enhancer-reprogramming — *Nat Cell Biol*
  2022 (10.1038/s41556-022-01060-1). DepMap gene-effect numbers (FLI1 −0.93/74 %; NR4A3 0.02) are from the
  repo's cached Chronos analysis (`depmap-insilico-findings.md`).
- Brenca M, et al. *NR4A3 fusion proteins trigger an axon guidance switch that marks the difference between
  EWSR1 and TAF15 translocated extraskeletal myxoid chondrosarcomas.* **J Pathol** 248:239–251 (2019).
  PMID 31020999; PMC6766969; doi 10.1002/path.5284. (Functional fusion-driver evidence: ectopic expression of
  either fusion recapitulates the malignant phenotype — but the 5′ partner shapes the NR4A3-driven
  transcriptome, tempering a strictly partner-agnostic story.)
- EMC variant-fusion series establishing NR4A3 as the shared **>90 % 3′ driver across ≥6 partners**: Agaram NP,
  et al. *Hum Pathol* 45:1084 (2014, PMC4015728; EWSR1 62 %/TAF15 27 %/TCF12, variant fusions → higher-grade/
  worse outcome); Wei S, et al. *Genes Chromosomes Cancer* (2021, PMID 34124809; novel SMARCA2-NR4A3, NR4A3
  rearranged in >90 %); Warmke LM, et al. *Genes Chromosomes Cancer* (2023, doi 10.1002/gcc.23144; TAF15::NR4A3
  clusters with EMC by DNA methylation); Ott G, et al. *JCO Precis Oncol* (2022, PMID 36103645,
  doi 10.1200/PO.22.00039; novel PGR-NR4A3). Underpin the partner-agnostic NR4A3-degrader rationale. (Note: Ott's
  patient benefit came via a *partner-specific* tamoxifen mechanism — cite for partner diversity, not as support
  for target-centric-over-junction.)
- Chen J, et al. *NR4A transcription factors limit CAR T cell function in solid tumours.* **Nature**
  567:530–534 (2019). doi 10.1038/s41586-019-0985-x. (T-cell exhaustion — needs *triple*-NR4A; the
  pan-NR4A second design mode, ex-vivo.)
- Mullican SE, et al. *Abrogation of nuclear receptors Nr4a3 and Nr4a1 leads to development of acute
  myeloid leukemia.* **Nat Med** 13:730–735 (2007). PubMed 17515897; doi 10.1038/nm1579.
- Safe S, Karki K. *The Paradoxical Roles of Orphan Nuclear Receptor 4A (NR4A) in Cancer.* **Mol Cancer
  Res** 19(2):180–191 (2021). PMC7864866; doi 10.1158/1541-7786.mcr-20-0707.
- Controls: PPARγ LBD + rosiglitazone (PDB 2PRG; Nolte 1998, Nature 395:137); ERα LBD + estradiol
  (PDB 1ERE; Brzozowski 1997, Nature 389:753). NR4A holo: Nur77 4JGV (THPN), 6KZ5 (cytosporone B);
  Nurr1 5Y41 (PGA1).
- Methods: AlphaFold2 (Jumper 2021, Nature, 10.1038/s41586-021-03819-2); fpocket (Le Guilloux 2009);
  OpenMM; PLUMED (Tribello 2014; PLUMED consortium, Nat Methods 2019).
- Aldeghi M, Heifetz A, Bodkin MJ, Knapp S, Biggin PC. *Predictions of Ligand Selectivity from Absolute Binding
  Free Energy Calculations.* **J Am Chem Soc** 139(2):946–957 (2017). PMID 28009512; PMC5253712;
  doi 10.1021/jacs.6b11467. (ABFE across related bromodomains — the precedent for the §4 per-receptor ABFE
  selectivity approach.)
- Filion C, Motoi T, Olshen AB, Laé M, Emnett RJ, Gutmann DH, Perry A, Ladanyi M, Labelle Y. *The
  EWSR1/NR4A3 fusion protein of extraskeletal myxoid chondrosarcoma activates the PPARG nuclear receptor
  gene.* **J Pathol** 217(1):83–93 (2009). PMC4429309. (EWSR1/NR4A3 response element in the PPARG promoter,
  confirmed by band-shift + transactivation — a validated *direct* fusion target; EMC-specific evidence the
  fusion is a functional transcriptional driver.) Further EMC-over-expressed fusion targets (e.g. NDRG2):
  *Tumor Biology* 33:1599–1607 (2012), doi 10.1007/s13277-012-0415-2.
- EMC clinical context + the fusion-addiction/ASO/surrogate evidence: see the EMC-program roadmap and its
  source memos.

*Medical-integrity note: every citation above was verified against the primary record (Crossref, PubMed and
Europe PMC), including journal, year, volume/pages and DOI/PMID/PMCID. No claim outruns its cited evidence.*
