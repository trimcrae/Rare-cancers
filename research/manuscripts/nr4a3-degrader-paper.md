# In silico design of a paralogue-favoured ligand for a cryptic NR4A3 pocket

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
screen (§2.5b), superfamily screen (§2.8 back half), indication/CAR-T/pan pole (§3), safety genetics (§4),
degradation-window model, and lo_m0_NCCO were moved to the Supporting Information (nr4a3-degrader-paper-SI.md, sections S1-S6). See nr4a3-degrader-paper-review-response.md.
Adversarial self-review: nr4a3-degrader-paper-redteam.md. Display-items plan: nr4a3-degrader-figures.md. -->
<!-- P0 REVISION TASKS (both DONE): (1) AF2 model/pocket/handles benchmarked against the experimental 8XTT
NMR ensemble — now the lead Results section §2.1 (8XTT-first per round-5 c43); (2) ABFE protocol audit given
the +7.1 T4L miss — per-replicate ΔG / λ-overlap / ESS / convergence published in SI §S7, result in §2.8. -->
<!-- SUPERSEDED editorial: the earlier degrader-title alternates are retired (see title change above). -->

## Abstract
The NR4A nuclear receptors are orphan transcription factors long considered "undruggable" — their orthosteric
pocket is occluded in crystal structures — and NR4A3, a gain-of-function driver of extraskeletal myxoid
chondrosarcoma, has an experimental ligand-binding-domain structure only as a recently released apo
solution-NMR ensemble (PDB 8XTT, 2025). fpocket analysis of the 20 deposited low-energy conformers shows
**substantial geometric heterogeneity at the mapped orthosteric site** — most strongly occluded, a few
exceeding an empirical drug-bound reference boundary (these are low-energy structural models, **not**
equilibrium-population samples) — and a three-independent-seed metadynamics workflow on an AlphaFold2 working
model explores cavity-bearing "open-like" geometries; short bias-free continuations from a selected geometry
show **geometric persistence in 3/3 replicas** (final pocket-druggability fractions await harmonized site
tracking), while the replicas do **not** yet agree on a **common quantitative free-energy profile**. A falsification-heavy, pocket-conditioned generative campaign (chemical triage, an empirical decoy
null, multi-snapshot rescoring, independent-seed replication, and molecular-species resolution) leaves a
single candidate, **denovo_401**, whose NR4A3-favoured preference is probed by **initial three-replicate
absolute-binding free-energy calculations conditional on selected opened conformers** (favouring NR4A3 over
both paralogues; a receptor-specific λ-overlap repair and an experimental-structure-anchored NR4A3
recalculation are in progress before final interpretation, and the engine's *absolute* scale is not
validated). This is a **computation-only** design and feasibility study — **no molecule was synthesized and no
wet-lab validation was performed** — whose principal unresolved limitations are the consistency of pocket
identification across structural models, cross-replica free-energy convergence, and the atomic binding pose
and ensemble-weighted selectivity.

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
demonstrates). *This work's structural foundation is the AF2 model, which predates 8XTT; we benchmark the AF2 pocket
against the experimental 8XTT ensemble in §2.1 (site heterogeneity corroborated; AF2 opened geometry
diverges ~3.5 Å), and a full 8XTT-anchored rebase of the dynamics, generation, and ABFE remains the primary
revision task (§4).* Full reconciliation of the "undruggable" reputation with our
findings, with references and the NR4A-family precedent, is in
[`../modalities/nr4a3-druggability-reconciliation.md`](../modalities/nr4a3-druggability-reconciliation.md).

Targeted **degradation** is one attractive downstream application: productive target *engagement* need not
itself encode the sustained occupancy pharmacology that a classical agonist/antagonist requires (the
demonstrated NR4A ligandability above is real but chemotype-specific and mostly low-affinity), so a
degrader that transiently engages the LBD to recruit an E3 and remove the protein is a rational route —
though the same cryptic-pocket dynamics (§2.3) remain a challenge for *warhead binding* either way.
Degradation recruits the retained, ordered NR4A3 LBD to an E3 ligase and removes the protein. This is target-generic
(it degrades NR4A3 whether wild-type or in the EMC fusion), which is why the program is framed around
NR4A3 rather than EMC specifically.

The same cryptic-pocket framework can be formulated with distinct **NR4A3-favoured and pan-NR4A design objectives**: re-ranked on the conserved core it targets a *pan-NR4A* binder for **ex-vivo CAR-T de-exhaustion** rather than an NR4A3-selective one. The full indication landscape (EMC, acinic cell carcinoma, the pan-NR4A/CAR-T pole, and the NR4A1+NR4A3 anti-target the method must design *away* from) is in **SI §S4**.

## 2. Results

### 2.1 The experimental apo NR4A3 ensemble (PDB 8XTT) is structurally heterogeneous at the mapped site
We begin from the only **experimental** NR4A3 structural data — the apo NR4A3/NOR-1 LBD solution-NMR ensemble (PDB **8XTT**, released 2025-01-15;
248-residue construct; **20 deposited low-energy conformers**, selected from 100 calculated as the
lowest-energy models — *not* population-weighted equilibrium samples) became available after this work's
AF2-based analysis. It lets us evaluate **independent experimental conformers at the AF2-derived mapped site**
— an experimental-structure *transfer test* of the pre-existing site hypothesis (the conformers are
independent experimental data, but the site residue set was originally identified on the AF2 model, so this is
not an AF2-independent site *discovery*). Mapping our pocket-5 residues onto 8XTT (sequence identity 1.000,
248 residues mapped) and running the **corresponding fpocket analysis workflow** per conformer (build pinning
across all structures is part of the harmonized rerun, so we do not yet claim a byte-identical pipeline)
([`../modalities/nr4a3-8xtt-benchmark-findings.md`](../modalities/nr4a3-8xtt-benchmark-findings.md);
`nr4a3_8xtt_benchmark.py`) shows **substantial conformational heterogeneity at the same mapped site**: most
conformers are strongly occluded (median druggability 0.012), while **4 of the 20 deposited conformers were
assigned orthosteric-site fpocket scores above the empirical reference boundary D\*=0.53**. An orthosteric-site
score was obtained for **all 20** conformers under the original implementation (range 0.000–0.925), so this is
**4/20 on both the detected-pocket and total-deposited denominators**; the harmonized rerun (pinned fpocket +
score-independent matcher) will report both denominators explicitly. Because these are
low-energy structural models rather than equilibrium samples, **4/20 is a structural-heterogeneity
observation, not an estimate of a 20 % open-state population** (and both the experimental median and the static
AF2 0.495 fall below D\*, though the experimental conformers are typically *substantially more occluded* than
the AF2 model — AF2 may over-open the site relative to the typical 8XTT conformer). The point is qualitative
and strong: an experimental ligand-free ensemble contains both occluded and cavity-bearing geometries at the
mapped site, **independent of the AF2/MD machinery**. **What 8XTT does *not* settle:** the AF2 model's *atomic*
pocket geometry diverges from the experimental ensemble — pocket-local Cα-RMSD median 3.56 Å, handle
Cα-RMSD 3.44 Å (global 7.63 Å). **The AF2↔NMR-vs-NMR↔NMR RMSD decomposition (`nr4a3_af2_nmr_rmsd.py`; NMR
numbering registered onto the AF2/UniProt frame by an exact +378 amino-acid offset) now attributes most of
this global divergence to genuine apo flexibility rather than model error: over all shared Cα, the AF2 model's
mean RMSD to the 20 NMR conformers (7.6 Å) is *within* the ensemble's own model-to-model spread (mean 8.3 Å,
range 1.8–14.4 Å) — i.e. AF2 is no further from the experimental conformers than they are from each other, a
legitimate ensemble member rather than an outlier. On the pocket-lining Cα alone (locally superposed) the model
is closer still — AF2↔NMR 0.84 Å mean (0.54–1.16) vs NMR↔NMR 0.59 Å (0.22–1.08) — so the local pocket geometry
is conserved to sub-Ångström in both, with AF2 at the high end of but inside the ensemble's internal range.** **Two post hoc robustness *transfers* to
8XTT-derived conformers (not a full workflow rebase — the metadynamics, generation, and ABFE still run on
AF2-derived structures) hold:** (i) **PocketMiner scored on the 8XTT conformers still enriches** the Pocket-5
residues (median 1.40× vs 1.36× on AF2 — the propensity call **transfers to the experimental conformers**, though, evaluated at the preselected AF2-defined region, it does not by itself establish an AF2-independent site *discovery*); and
(ii) a **multi-snapshot MM-GBSA re-dock of `denovo_401` into the four cavity-bearing 8XTT conformers keeps its
NR4A3 preference in all four** (min-margin median 9.4 kcal/mol; NR4A3 favoured over both paralogue reference
states in every conformer). These are **binding-competent-state robustness tests, not an unbiased ensemble
test** — the four conformers were prespecified by the fpocket criterion, a matched 8XTT-frame decoy null is
pending (§4), and the paralogue reference states were re-computed opened models, so the comparison is
structurally asymmetric. So the 8XTT analyses **reduce, but do not eliminate**, the structural uncertainty:
the site's existence as a heterogeneous experimental feature and the transfer of the two prediction
*directions* are supported, while the atomic pose and the ensemble-weighted (ABFE-grade) selectivity remain
unresolved. The automated apo-benchmark verdict is reported as **"partial"**.

### 2.2 AlphaFold2 gives an imperfect working model: a borderline static pocket, contextualized against a reference panel
fpocket assigns the NR4A3 orthosteric pocket (Pocket 5, residues 406–534, carrying all 7 selectivity
handles) a druggability of **0.495**. To make that interpretable we ran the same pipeline on a
nuclear-receptor calibration panel ([`../modalities/nr4a3_calibration.py`](../modalities/nr4a3_calibration.py)):
- experimentally **drug-bound** NR pockets score **0.53–0.68** (PPARγ/rosiglitazone 0.599, ERα/estradiol
  0.586, Nurr1-holo 0.677, Nur77-holo 0.529) → **empirical reference boundary D\* = 0.53** (the lower edge
  of this small, selected drug-bound panel — a descriptive reference, not a statistically calibrated
  threshold with a negative distribution);
- fpocket **`max` is non-discriminating** (even the occluded 1OVL crystal scores 0.864 at a
  *non-orthosteric* cavity) — so the widely-quoted "Nurr1 ~0.8" is **not** the orthosteric pocket, and is
  present in both model (0.801) and crystal (0.864), i.e. **not an AlphaFold artifact**;
- the AF2 static orthosteric score (0.495) lies **below the empirical drug-bound reference boundary
  (D\* = 0.53)** but **above the median score across the deposited 8XTT conformers** (0.012; §2.1 above); the AF2 model may therefore already represent a **relatively open member of the experimentally
  observed structural range**, not a conservative lower bound.
Thus the static orthosteric pocket sits *just below* the empirical drug-bound reference range — concordant with
"undruggable", and the right starting point for the cryptic-pocket question.

**Figure 1.** Contextualized druggability of the NR4A3 orthosteric pocket: the empirical drug-bound
nuclear-receptor reference range (PPARγ 0.599, ERα 0.586, Nurr1-holo 0.677, Nur77-holo 0.529; D\* = 0.53) against the
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
true weight, with two honest caveats: (i) PocketMiner is a *propensity predictor* — it supports **elevated
cryptic-pocket-forming propensity** at the mapped region from an orthogonal method, but supplies neither the
opened geometry nor a druggability value, which remain the job of the metadynamics + fpocket analysis below; and (ii) the
network's single highest-scoring residues (375–398) fall at the **N-terminal truncation edge** of the
domain fragment — a chain-terminus flexibility artifact of scoring an isolated LBD, not the functional
cavity — so we rest on the *Pocket-5 enrichment*, not a rank-1 claim. **That enrichment is statistically
significant and persists under a null that excludes the high-scoring truncation-edge region**
(`nr4a3_pocketminer_null.py`, empirical permutation null over the full 254-residue score array): the
Pocket-5 mean (0.64) beats random same-size residue sets at **p = 0.009**, and against a null pool with the
N-terminal edge (373–398) **excluded** the enrichment remains (**p = 0.0001**). We read this as *persistence*
of the enrichment when the edge is removed — not as proof the terminus is irrelevant, since excluding a
high-scoring region can itself shift the null downward. It also clears a
**sequence-contiguous-window** null at p = 0.036. A stricter **selection-aware (maximum-statistic)
permutation** — which corrects for having *selected* the Pocket-5 patch by requiring it to beat the *best*
same-size contiguous window under each permutation, not merely a random one — is decisive about the terminus:
with the truncation edge included the enrichment does **not** survive the familywise correction (p = 0.74,
because that edge itself supplies the winning patches), but with the flagged region masked it **does**
(p = 0.014). This is consistent with the reading above — the Pocket-5 signal is robust to a conservative
selection-aware null *provided* the known N-terminal artifact is excluded. (A true residue-contact-graph
spatial-patch max-statistic null and the all-20-conformer PocketMiner stratification remain follow-ups, §4.)
Permutation mechanics: 20,000
one-sided draws, fixed seed, add-one correction, pocket prespecified before scoring. Data:
[`../modalities/nr4a3-pocketminer-result.json`](../modalities/nr4a3-pocketminer-result.json),
[`../modalities/nr4a3-pocketminer-null.json`](../modalities/nr4a3-pocketminer-null.json).



**Reconciliation with recent NR4A structural and chemical-biology work (2023–2025).** Three independent
lines of evidence bracket this borderline score and sharpen (rather than soften) our claim. *(i) The
occluded-pocket challenge.* A 2025 structure-guided Nurr1 study (vidofludimus; López-García et al. 2025) reaffirms
that the *canonical* NR4A pocket is "filled with bulky hydrophobic residues" and modulates the receptor
instead through an **allosteric surface pocket** — a direct challenge to any canonical-cavity strategy. It is
exactly why our claim is explicitly **not** that the static canonical pocket is druggable but that it
*breathes* into a transiently druggable cavity (§2.3); their surface pocket is also an alternative site we do
not pursue here. *(ii) Ligandability is real but chemotype-specific.* Protein-NMR footprinting (Munoz-Tello
2020) confirms amodiaquine, chloroquine and cytosporone B directly bind the NR4A LBD while **celastrol,
C-DIM12 and TMPA do not** — so among the repurposed actives in our selectivity matrix (§2.5), cytosporone B
carries independent direct-binding support whereas celastrol does not, which we now weight accordingly; and a
family-wide chemical-probe audit (Willems/Merk 2025) validates a small vetted NR4A tool set while showing many
putative NR4A ligands lack on-target engagement — a caution we apply to every repurposed chemotype.
Fragment-to-lead campaigns reaching sub-µM NR4A ligands with NOR-1/NR4A3 tested (Stiller & Merk 2023; Zaienne
2022) keep the *ligandable-not-undruggable* premise on experimental footing. *(iii) Paralog-selective NR4A
degradation is achievable.* The NR-V04 PROTAC (Wang 2024) selectively degrades NR4A1 while **sparing
NR4A2/NR4A3** — proof-of-concept that intra-family degradation selectivity is attainable (the exact inverse of
our NR4A3-selective goal), though its sparing mechanism is unresolved and its celastrol warhead is a
promiscuous covalent binder, not a selective one.

### 2.3 Metadynamics drives the orthosteric pocket to breathe into a druggable state (30 ns production)
Well-tempered metadynamics on the radius of gyration of the Pocket-5 lining Cα atoms (method:
[`../modalities/metad-methods-appendix.md`](../modalities/metad-methods-appendix.md)) drives the pocket
open (CV Rg ~0.5 → ~1.05 nm). On the 30 ns run (600 frames), per-frame fpocket on the **orthosteric
Pocket-5 cavity** (the *same* metric as the static 0.495 and D\*, not the non-discriminating "max-anywhere"
cavity of §2.2) reaches druggability **0.931** (max over frames; `crosses_0.5 = True`); SASA of the lining
residues rises (+6.1 nm², 86.8 % of frames more open than baseline). (A 5 ns validation gave a consistent
0.751.) This pocket-dynamics analysis of NR4A3 parallels the *dynamic, breathing*
Nurr1 pocket (de Vera 2019).

**Read this number for what it is.** The fpocket druggability score is an established computational
pocket-druggability proxy (a logistic model of hydrophobic enclosure and polarity — *not* raw cavity volume), and §2.2 already anchors
it on a nuclear-receptor panel that includes the occluded 1OVL crystal as a de-facto negative; it is a
geometry-based druggability *proxy* (a prediction, not a measurement). Two honest qualifications apply to
the **0.931** specifically. First, it is the
**maximum over the 600 opened frames** — an extreme-value statistic that overstates the *typical* opened
conformation; the more faithful summary is the *distribution*, i.e. the fraction of opened frames clearing
D\*=0.53 (the pre-registered ≥5 %-of-frames test, comfortably met — the handle-facing sub-sample found
roughly one third of frames druggable), with 0.931 as the peak. Second, it is computed on **biased-MD
conformations**, so its magnitude is not on the same footing as the *static* drug-bound crystal sites
(0.53–0.68) and we do **not** claim "0.931 > the drug-bound band" as a like-for-like result. Note the rise
is more consistent with a genuine enclosed cavity than with mere solvent exposure: because the fpocket score
weights hydrophobic *enclosure*, a pocket that merely splayed open / became solvent-exposed would tend to
score *lower*, not higher. The score is a multi-feature composite, so we do not attribute the rise to any
single feature; but the independent lining-residue / handle-facing check (§2.3 below) supports an enclosed,
hydrophobic breathing cavity. fpocket cannot establish whether such geometries occur with appreciable
**equilibrium probability**; the open-seeded **release** simulations (below) address only the narrower
question of prompt relaxation after the bias is removed, not the equilibrium population. The honest claim:
the pocket *geometrically admits* a druggable cavity when it breathes open, with that cavity
hydrophobic/enclosed; its equilibrium weight is not estimated here.

**Gate scoring** ([`../modalities/nr4a3-druggability-prereg.md`](../modalities/nr4a3-druggability-prereg.md)):
**Gate 2 (opened state druggable) initially passed under the original implementation** on both clauses
(druggable frames + handles pocket-facing, below); **its final classification is provisional pending the
harmonized pocket-tracking re-analysis** (the set of druggable frames itself depends on the tracker). **Gate 1 (a genuine two-state cryptic *opening*) FAILED as pre-registered.** Gate 1
asked for an accessible *minimum or shoulder* at an opened Rg "not just biased excursions," but F(Rg) is
**monotonic — a single resolved minimum and a rising wall, with no separate opened minimum**. By the
pre-registered criterion this is a fail: there is no distinct opened state. **This negative result
motivated an alternative hypothesis** — that the druggable conformations are reached by **basin-internal
breathing** rather than a two-state opening — which the release run (below) then tested. So we report
Gate 1 as **failed, and reformulated**, not as a "weak pass": there is one basin whose thermal
fluctuations transiently expose a druggable cavity (consistent with de Vera's breathing Nurr1 pocket), and
"opened *state*" would overstate it. **Gate 3 splits into two distinct subclaims that one run cannot
jointly settle** (a kinetic/thermodynamic distinction): **3A — persistence after bias removal** (does a
seeded open-like geometry promptly collapse?) and **3B — equilibrium energetic accessibility from the closed
ensemble** (is that geometry reachable with appreciable probability at equilibrium?). **3B is addressed only
provisionally, by the biased F(Rg)** (this paragraph); **3A is addressed by the release run** (next
paragraph). Neither establishes the other: a conformation can be equilibrium-rare yet persist for a few ns
once seeded there. On **3B**, the bottom line first: **an initial single-profile analysis suggested a low
apparent cost near the selected reference Rg, but three independent replicas failed to reproduce a common
profile (below), so we withdraw that quantitative accessibility interpretation and leave 3B unresolved.** The
superseded single-profile reasoning, for completeness: the naive closed→fully-open cost is ~38 kcal/mol, but that is the cost to the
*most-open* edge (Rg 1.06) at the **under-converged sampling frontier**, not a *druggable* state:
correlating per-frame druggability with F(Rg) shows the pocket is already druggable (fpocket 0.80) at
Rg ≈ 0.72 — in the well-sampled basin region — at only ~0.76 kcal/mol. The caveat:
both numbers are read off the *same* incompletely-converged biased F(Rg), so the 0.76 rests on the
basin region being better sampled than the frontier (it is, but it is a single biased profile). **The metad
has since been extended to 60 ns cumulative** on the original continued trajectory (two 30 ns segments;
`report_metad.py` on `metad-fes-60ns.dat`): still a **single resolved minimum** with **no separate opened
minimum** (Gate 1 stays failed-as-registered / basin-breathing). On that single profile the druggable
release-frame region (Rg ≈ 0.73) sat ~0.6 kcal/mol above the basin and the most-open frontier (Rg ≈ 1.06)
~35 kcal/mol — **but those are single-profile numbers that the three independent replicas below do NOT
reproduce.** We then ran **three independent-seed well-tempered metadynamics replicas** (seeds 1/2/3, 30 ns
each; `nr4a3_metad.py`, prefixes `nr4a3-metad-r{1,2,3}`; analysis `nr4a3_metad_analysis.py` +
`nr4a3_metad_crossreplica.py`), interpreted **not** as a convergence claim:
**(i) The profiles are not converged.** Within-run block-to-block drift *decreases* with time (max|ΔF(Rg)| for
the 10→20 then 20→30 ns blocks = 29→14 (r1), 31→15 (r2), 16→18 (r3) kJ/mol) but the 20→30 ns block still
drifts **~14–18 kJ/mol (≈3.3–4.2 kcal/mol)**, and r3's does not decrease — so each replica shows only a
*late-time reduction* in drift, not convergence. (The near-zero 30.0→30.2 ns increment is the trivial 0.2 ns
extension, not a convergence metric.) *(Drift-comparison protocol: each block's F(Rg) is reconstructed by
well-tempered `sum_hills` on a **common uniform Rg grid**, **re-zeroed at its own minimum**, and differenced
only over the **interpretable region** with sparsely-sampled edge bins excluded; we quote the pointwise
**max**|ΔF|, and the **mean and RMSD** of |ΔF| over the same region — also computed by
`nr4a3_metad_analysis.py` — give the same not-converged verdict, so the max is not an isolated edge-bin
artifact.)* **(ii) The independent replicas do not reconstruct a common F(Rg).** Each replica's F(Rg) has a single
minimum, but at a different Rg, and each assigns a different free energy to the **reference Rg region
(Rg ≈ 0.72 nm)** — the geometry of the old single-profile ~0.6 kcal/mol estimate (one row per replica, so the
pairing is unambiguous):

| replica | basin Rg (nm) | ΔF at reference Rg ≈ 0.72 (kcal/mol) |
|---|---|---|
| r1 | 0.87 | **16.03** |
| r2 | 0.73 | 0.06 |
| r3 | 0.74 | 0.83 |

(`nr4a3-metad-crossreplica.json`; spread ~16 kcal/mol across seeds.) So **r2 and r3 place Rg ≈ 0.72 near their
own minimum** (a cost close to the old ~0.6 estimate), whereas **r1's minimum is substantially more expanded
(0.87 nm)**, putting the same reference geometry ≈ 16 kcal/mol uphill. Two cautions bound this comparison, both flagged for the harmonized rerun: a fixed Rg
is **not** established to correspond to the same physical pocket — or to any druggable cavity — in each
independent replica (the per-replica harmonized pocket scoring that would define an equivalent druggable region
is pending, §3), and a single F(Rg) minimum is not, on its own, a structural classification of a "closed"
state. **So the ~0.6 kcal/mol opening cost is a single-profile estimate not reproduced across seeds; the robust
conclusion is the narrower one — the reconstructed 1-D F(Rg) profiles differ substantially across independent
replicas** — and cross-replica free-energy agreement — hence **Gate 3B (equilibrium accessibility) — remains
unresolved.**
**(iii)** A separately-defined **gate descriptor** (pocket-mouth distance) tracks the same expansion
(corr(Rg, gate) = 0.94 / 0.96 / 0.94), confirming the Rg excursion is **coherent gate motion** rather than an
Rg-only numerical artifact — but at ~0.95 correlation it is **nearly collinear with Rg and does not test
whether Rg captures all slow degrees of freedom**. A data-driven test now shows it does **not**: **TICA
(time-lagged independent component analysis; `nr4a3_slow_cv.py`) on the pooled replicas — featurised by
pocket-lining Cα distances, gate-residue χ1, lining SASA and Rg — returns a slowest independent component only
partially aligned with Rg (corr(IC1, Rg) = 0.68; slowest implied timescale ≈ 17 ns), i.e. a slow coordinate
that Rg does not capture exists.** Biasing 1-D Rg therefore projects a ≥2-D opening process onto one lagging
coordinate — a parsimonious explanation for the cross-replica F(Rg) divergence — and motivates biasing the
**data-derived coordinate directly** rather than adding sampling to the 1-D Rg profile (in progress; §4). **(iv) Recrossing is heterogeneous** (a "crossing" is a **low-Rg↔high-Rg
threshold crossing** of the Rg CV — closed/open boundary at **Rg = 0.9 nm with a 5σ hysteresis deadband**,
reference/"druggable" window **Rg ∈ [0.7, 1.1] nm** — *not* a structurally classified closed↔open transition;
a distinct entry into the window counts as one "visit" (so a long residence is one visit, not many, but no
minimum-dwell filter is applied and no structural state is defined — refinements flagged for the harmonized
re-analysis): r1 shows **3 low-Rg↔high-Rg crossings** with 41 window-visits (partial recrossing); r3 makes
**360 window-visits** but does not fully recross within 30 ns; **r2's crossing count is not reported** (its
reduced COLVAR retained a single usable sample; see provenance below). What the
replicas *do* agree on is narrower: each 1-D F(Rg) profile contains **a single resolved minimum and no
reproducibly resolved second minimum**, while the quantitative profiles and minimum locations differ
substantially — **not** a common opening free energy or a demonstrated common druggable geometry.

**Per-replica analysis-product provenance (round-5 comment 5).** The F(Rg) profiles and the Rg↔gate
correlation above use the full **HILLS / raw COLVAR** and are valid for all three replicas; the
recrossing/event analysis reads a separately **decimated ("reduced") COLVAR**, whose r2 product retained a
single usable sample — an **analysis-pipeline artifact flagged for repair** (re-decimate r2 from the raw
COLVAR), *not* a property of the r2 trajectory (whose FES and correlation are valid). We therefore report r2's
FES and correlation but withhold its crossing count:

| replica | HILLS → FES (basin, drift) | raw-COLVAR corr(Rg,gate) | reduced-COLVAR event/recrossing |
|---|---|---|---|
| r1 | ✓ | ✓ (0.94) | ✓ — 3 low-Rg↔high-Rg crossings |
| r2 | ✓ | ✓ (0.96) | ✗ — reduction retained 1 usable sample (**repair item**) |
| r3 | ✓ | ✓ (0.94) | ✓ — revisits reference Rg window, no full recross in 30 ns |
 The 60 ns single-trajectory profile is **Figure 2**
([`../modalities/nr4a3-fig2.png`](../modalities/nr4a3-fig2.png); generated by `nr4a3_journal_figures.py`
from the committed `metad-fes-60ns.dat`). (Edge caveat retained: sum_hills references the sampled edges to
~0 at the metad walls, so only the basin and the profile *shape* are interpretable, not the edge values. The
fpocket druggability figures above are from the 30 ns trajectory; extending per-frame fpocket to the 60 ns
frames is a cheap, still-open follow-up.) The **release run**
(`nr4a3_md_release.py`) addresses the separate subclaim **3A** — whether the seeded open-like geometry
persists or promptly collapses once the bias is removed — and is described next; it does **not** estimate
equilibrium population (3B).
Net: enhanced sampling generated cavity-bearing geometries not represented by the static AF2 snapshot (0.495); the
biased metadynamics profile breathes to a geometrically druggable cavity at low apparent cost on that
(convergence-limited) profile, and a bias-free continuation seeded from a metadynamics-derived conformation
shows that cavity **persists over the 5 ns propagated** (not that it is a
thermally-populated equilibrium state) — a feasibility result, stated at that weight.

**The release run supports Gate 3A (persistence after bias removal); Gate 3B (equilibrium accessibility)
remains unresolved.** Seeding a bias-free continuation from a *strained* metad frame requires care: a first
run seeded the max-Rg frontier frame (0.984 nm, the ~38 kcal/mol opening edge) and it collapsed
(frac-near-open 0.00) — the *worst-case* frame, near-guaranteed to collapse, and not the realistic target.
Re-seeded from the **selected reference frame at CV Rg 0.717 nm** (assigned a low apparent free energy in the
original single-profile analysis and exceeding the fpocket criterion under the original tracking
implementation), the breathing-open geometry **persists: 3/3
bias-free replicas held the full 5 ns** (frac-near-seed 1.00, mean |drift| 0.025 nm, no collapse in any
replica). Running fpocket on the bias-free release trajectory, the orthosteric Pocket-5 is **druggable in
~24 % of frames** (max 0.842, mean 0.262, fraction ≥ 0.5 = 0.24, fraction ≥ D\*=0.53 = 0.20; static 0.495)
at CV Rg ≈ 0.737 — clearing the pre-registered "≥5 % of frames ≥ D\*" bar (20 % here). Because the
propagation carried no bias, **the geometry is maintained without ongoing metadynamics bias** (its *initial*
conformation was, however, selected from biased sampling, so this is not an equilibrium-provenance statement).
*(Two scope notes so the two numbers are not over-read as one. (i) The **3/3 persistence** is an
**Rg-persistence** result across the triplicate; the druggability frame-fraction was originally quoted on the
single `release_rep0` trajectory but has now been **scored on all three release replicas** (per-frame fpocket,
`nr4a3_mdpocket.py`): fraction of frames ≥ D\*(0.53) = **0.20 / 0.16 / 0.28** (rep0/rep1/rep2; fraction ≥ 0.5 =
0.24 / 0.16 / 0.28; per-replica max 0.84 / 0.89 / 0.88; mean 0.26 / 0.22 / 0.22), so **all three independent
bias-free trajectories cross into the druggable band** and the ~0.2 druggable fraction is **replicated, not
`rep0`-specific** (mean ≈ 0.21, range 0.16–0.28). These remain **descriptive frame fractions on correlated,
non-equilibrium frames**, not equilibrium populations; an autocorrelation-aware descriptive interval
(integrated autocorrelation time → effective sample size → block bootstrap) and the important reproducibility
caveat that the denominator is *frames with a detected overlapping pocket* (undetected frames are excluded,
not scored zero) are given in the SI. (ii) **5 ns is a short persistence window**: no prompt sub-nanosecond collapse of the seeded conformation was observed in these three trajectories,
but a geometry can hold on 5 ns and still relax on tens–hundreds of ns, so "persists" here means "does not
promptly collapse," not "a verified long-lived sub-state.")* This is **not** an
always-open pocket (mean 0.262 < 0.5) but a **dynamic cavity** whose seeded open-like geometry does not
promptly collapse once the bias is removed and is fpocket-druggable in a fraction of frames **across all three
release replicas** (≥ D\* in 0.20 / 0.16 / 0.28 of frames; below). **These are correlated, open-seeded,
non-equilibrium frame fractions — NOT equilibrium population estimates**, and (per the pocket-tracking Methods)
they use a **detected-matched-pocket denominator**; the harmonized re-analysis with an all-frame denominator
and a stricter site-match is a submission gate (§3 / §4). 5 ns cannot establish the equilibrium probability of
the conformation or a spontaneous opening rate. So
**Gate 3A is supported** (the seeded druggable geometry does not promptly relax once the bias is removed)
while **Gate 3B — equilibrium energetic accessibility from the closed ensemble — remains unresolved** (the
only estimate is the convergence-limited biased F(Rg)); a warhead would need to select-and-stabilise these
transiently-druggable conformations rather than occupy a static pocket. Establishing an actual populated
fraction would require reweighted enhanced sampling or many independent unbiased trajectories with
equilibrium weighting (a revision task, §4). All downstream design (below) is therefore anchored to a
**druggable release-derived frame** (Rg ≈ 0.737, fpocket ≥ 0.5; `nr4a3_release_druggable.py`), not the
biased-metad frame. *(Registered Gate-2 sub-check — computed under the original implementation; not treated as confirmed while the set of druggable frames it is computed over depends on the provisional tracker. The handle-facing analysis
(`../modalities/nr4a3_handle_facing.py`, run 2026-06-26 on the 30 ns trajectory) shows the opened,
druggable frames keep the selectivity handles pocket-facing: across the druggable frames (fpocket ≥
D\*=0.53) a mean of **5.0/7** handles point into the cavity and **87.5 %** keep ≥4 facing. Five are
reliably pocket-facing — **L406, T410, I484, I531, L534** (≥0.875 of druggable frames) — while **T407
and R412 mostly splay outward** (facing in 0.0 and 0.25 of druggable frames), so the demonstrated
candidate pocket-facing handle set is those five, not all seven (geometric orientation, not a ligand-engagement result). This is also the precondition for the warhead
screen's handle-contact scoring (§2.5). The open-seeded "release" run is the orthogonal Gate-3A test (does
the seeded open-like geometry persist, or promptly collapse once the bias is removed?); the seeded geometry
persists across 3/3 short replicas and is fpocket-druggable in a fraction of frames of **each of the three
release replicas** (≥ D\* in 0.20/0.16/0.28; detected-pocket denominator), so the **short-timescale
persistence question (3A) is answered** (it does not promptly collapse), while equilibrium accessibility (3B)
is not. The calculations do **not**
distinguish conformational selection from ligand-induced stabilization; we use the neutral term
*short-timescale persistent open-like geometry* (see the release-run paragraph above).)*

**The opened frame is an intact fold, not a metad-melted one (structural-sanity control).** Because every
downstream step (docking, MM-GBSA, the ternary, and the FEP below) is anchored to the opened NR4A3 frame, we
verified that opening the pocket did not *unfold* the LBD. The opened frame is elongated (~99 Å long axis vs
~45 Å for a compact LBD), which a reviewer could read as an over-driven metadynamics artifact — so we measured
it directly (`nr4a3_frame_sanity.py`): against the pre-metad AF2 LBD, the opened frame **retains 100 % of the
helical content** (DSSP helix fraction 0.602 vs 0.594; retention 1.01) and its folded **core superimposes to
1.76 Å Cα-RMSD** (1.78 Å including the pocket mouth). So the fold is intact and the elongation is a **floppy,
disordered N-terminal hinge** (the ~22 residues before the LBD core) swinging out — not a melt. This
supports **preservation of the folded core** in the frame used throughout (it does *not* by itself validate
the pocket-opening pathway, the elongation, the local side-chain geometry, or any binding pose) and licenses
trimming that disordered hinge for the explicit-solvent FEP (§3), which is standard practice (ABFE is run on
the folded domain, not a disordered tail).

### 2.4 Selectivity handles for an NR4A3-selective (NR4A1/2-sparing) warhead
Aligning the NR4A3 pocket to NR4A1/NR4A2 ([`../modalities/nr4a-selectivity.json`](../modalities/nr4a-selectivity.json))
identifies, among the **10 Pocket-5 lining residues**, **7 divergent** ones — L406, T407, T410, R412,
I484, I531, L534 — as selectivity handles. All 7 are within the metadynamics CV; of these the opened,
druggable ensemble keeps **5 pocket-facing** (L406, T410, I484, I531, L534 — §2.3), so those five are the
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
*same* opened pocket be tuned **NR4A3-selective** (engaging the divergent handles; an NR4A3-selective agent
removes NR4A3 but **spares NR4A1**, thereby avoiding the combined NR4A1+NR4A3 loss state associated with
myeloid-leukaemia risk) or deliberately **pan-NR4A** (engaging the
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
conservation observation only. A computational alanine scan of the handle residues (per-residue MM-GBSA ΔΔG
of `denovo_401`; `nr4a3_resistance_ddg.py`) could estimate the **ligand-binding sensitivity** to mutation,
**not** the receptor's functional constraint — it does not tell us whether mutating a residue impairs
receptor folding, transcriptional activity, or oncogenic function; that would require separate
stability/function calculations or experimental mutational data. Human-variation / deep-mutational data would
be needed to speak to escape resistance.

**The warhead pocket is enriched for residues divergent from both paralogues — a candidate selectivity
hotspot.** Comparing
NR4A1/2/3 divergence in the orthosteric cryptic pocket (the warhead's contact residues) against the LBD-wide
pocket-residue census (same `nr4a-selectivity.json` alignment):

| residue set | n | divergent vs ≥1 paralogue | divergent vs **both** paralogues |
|---|---|---|---|
| **orthosteric cryptic pocket (warhead contacts)** | 10 | **70 %** | **60 %** |
| **predicted NR4A3–CRBN ternary interface (§2.5)** | 33 | **24 % (8)** | **18 % (6)** |
| LBD-wide pocket census | 148 | 45 % | 28 % |
| non-orthosteric remainder (surface/PPI proxy) | 138 | 43 % | — |

**Supplementary Figure S2** ([`../modalities/nr4a3-figS2.png`](../modalities/nr4a3-figS2.png); generated by
`nr4a3_journal_figures.py` from the table above, alignment source `nr4a-selectivity.json`). Paralogue
divergence by LBD residue set: the orthosteric cryptic pocket (warhead contacts) is **enriched for
paralogue-divergent residues** — 70 % of its residues differ from ≥1 paralogue (60 % from both), ~1.6× the
LBD-wide average — while the predicted NR4A3–CRBN ternary interface is separately divergent on a *different*
surface. Sequence divergence is handle *availability* (a specification), not a demonstrated binding margin.

The warhead pocket is **~1.6× more paralogue-divergent than the LBD-wide average** — a candidate selectivity
hotspot, not a conserved wall. **This enrichment is statistically tested** (`nr4a3_divergence_enrichment.py`,
one-sided Fisher exact of Pocket-5 vs the pooled background of all other LBD pocket-lining residues): the
**divergence vs *both* paralogues** is **6/10 = 60 % vs 25 % background, p = 0.028**, while divergence vs ≥1
paralogue is a **non-significant trend** (7/10 = 70 % vs 43 %, p = 0.090). Three caveats keep this from being
over-read as a firm "most-divergent-zone" claim. **(a) Multiplicity:** two related endpoints were evaluated;
a two-test Bonferroni correction moves p = 0.028 to 0.056, i.e. borderline — and "divergent vs both" was the
decision-relevant metric but was **not** pre-registered as the sole endpoint. **(b) Spatial correlation:** the
ten pocket residues are contiguous in space and are not an independent random sample, which the residue-wise
Fisher test does not model. **(c) Selection:** the pocket itself was identified before this test, so a
maximum-statistic correction across candidate pockets would be needed to claim it is *the* most divergent
region. A spatial-block / contact-graph permutation with selection-aware (maximum-statistic) correction is a
revision item (§4); until then we report an **enrichment on the decision-relevant metric, borderline after
multiplicity**, not a calibrated "most divergent zone." The comparison table above contrasts the pocket
against the LBD-wide census, the ternary interface, and the pooled remainder — it does **not** test every
individual LBD sub-region, so "most divergent" is not established. So the
in this mapping, handle availability does not appear to be the primary limitation; the binding problem is **pocket druggability + affinity-margin robustness** (the cryptic, least-druggable-of-three
pocket, and the MM-GBSA noise floor of §2.6). The full selectivity-architecture analysis — the
multiplicative binder × ternary × kinetics budget, the paralogue-divergent CRBN-ternary interface, and a
superfamily-wide pocket-liability screen across all 47 human NRs (with MR/AR as the sole non-paralogue
sequence-level follow-ups) — is in **SI §S3**.

### 2.5 Warhead screen and the family-wide selectivity matrix
Having identified cavity-bearing model geometries and short-timescale persistence after bias removal (§2.3;
Gate 3A supported, 3B unresolved), we screen for an **NR4A3-favoured warhead profile** against the
*opened* conformer (`nr4a3_warhead.py` + `gpu-warhead-aws.yml`): it extracts the most-druggable opened
conformer, docks a real ChEMBL NR4A library into NR4A3-opened **and** the
aligned NR4A1/NR4A2 pockets, and ranks by a selectivity margin + engagement of the **5 pocket-facing**
handles (§2.4). A first screen returns NR4A3-favoured chemotypes (e.g. an NR4A3-active scaffold,
ΔdG ≈ +1.7 kcal/mol vs the paralogues); these docking margins are **triage priors, not affinities**.

**The selectivity matrix.** A central methodological point: docking the *opened* NR4A3 pocket against
*static* NR4A1/2 models biases toward apparent selectivity, because — by our own argument (de Vera 2019;
the Nur77 cryptic pocket) — the paralogue pockets are likely cryptic too. We therefore ran the **same
metadynamics on NR4A1 and NR4A2** (one pipeline; paralogue CV/LBD mapped to NR4A3 by BLOSUM62 alignment)
to obtain **criterion-matched opened-pocket ensembles** for all three (here and throughout, "criterion-matched"
means *analogously selected* high-druggability metadynamics-opened conformers — matched on the selection
criterion, **not** on state definition or equilibrium population), and docked one library into each
(`nr4a3_matrix.py`; criterion-matched opened conformers NR4A3 frame 300 (druggability 0.931) / NR4A1 frame 524
(0.981) / NR4A2 frame 125 (0.938)). Each candidate carries a **selectivity fingerprint** across the family, partitioning
the library into NR4A3-selective (EMC/AciCC), pan-NR4A (ex-vivo immuno), and the AML-associated NR4A1+NR4A3
**anti-target** cells (SI §S4). The **anti-target cell is empty** (no candidate engages NR4A1+NR4A3 while
sparing NR4A2 — nothing to design away from in this library), and the NR4A3-leaning leads are repurposed NR4A
actives (e.g. cytosporone B, amodiaquine). This *suggests* a tunable design axis — but the docking dG are
within noise, so they nominate chemotypes, not a lead, and the stronger programmability claim rests on the
complete de-novo campaigns (§2.6), not this docking matrix.

**Figure 4.** The family-wide, criterion-matched selectivity matrix: one candidate library docked into the
metadynamics-opened NR4A3, NR4A1 and NR4A2 pockets, giving each candidate a per-paralogue selectivity
fingerprint (NR4A3-selective / pan-NR4A / NR4A1+NR4A3 anti-target cells). Full figure: [`../modalities/nr4a3-fig4.png`](../modalities/nr4a3-fig4.png) (rendered by `nr4a3_journal_figures.py`).

**Docking nominates; endpoint rescoring challenges the nominations but itself requires specificity controls.**
We re-scored the matrix's own docked poses with single-snapshot **MM-GBSA** (enthalpy + GBn2 implicit solvent,
no entropy/ensemble average; OpenCL on the A10G; `nr4a3_mmgbsa.py`). The docking-level NR4A3-selectivity
**mostly does not survive**: the apparent docking lead **cytosporone B reverses**, and across the 13
deduplicated candidates the pipeline verdict census is *confirmed_selective* 3
(amodiaquine, celastrol, + a duplicate), *reversed* 3, *weakened* 2, *rescued* 3, *confirmed_nonselective*
2. MM-GBSA magnitudes here are inflated by the single-snapshot/no-entropy approximation, so we read the
**verdict/direction, not the kcal/mol** — but the direction is clear: **the exploratory repurposing screen
did not yield a candidate that advanced under the later specificity controls** (the single-snapshot tier is
itself shown non-specific by the decoy null, §2.6), which is exactly why a *de-novo* design is needed (§2.6).
(Selectivity FEP on a survivor is the defensible affinity tier, gated behind a bona-fide selective
candidate.) For a representative `denovo_401`-PROTAC, the model **predicts a ternary-like CRBN complex of comparable
confidence for all three paralogues** (`nr4a3_ternary.py`, Boltz-2; per-paralogue iptm 0.72/0.83/0.82, each
LBD presenting a solvent-exposed lysine near the modeled CRBN-facing interface (closest Lys-Nζ to the nearest
CRBN heavy atom — NR4A3 K195 3.1 Å, NR4A1 K53 2.3 Å, NR4A2 K175 4.0 Å — a **CRBN-proximity proxy, not modeled
ubiquitin-transfer geometry**, since no CRL4^CRBN assembly or E2~Ub is included). We read this only as *geometric feasibility*, not as
demonstrated cooperativity, ubiquitination competence, or degradation (a single Boltz pose, no
CRL4^CRBN–E2~Ub assembly, one arbitrary linker; the CRBN/IMiD recovery is a memorization-consistent sanity
check, not out-of-distribution validation). At that weight, the model **did not provide evidence for
NR4A3-selective ternary geometry** (comparable confidence for all three paralogues from one linker is not
proof of nonselectivity), so **this representative modeled linker did not provide evidence that ternary
geometry adds NR4A3 selectivity** — degradation selectivity, if any, rests on the **binder** margin, with
linker/exit-vector design the (untested) lever that might introduce it. The full ternary detail, the
CRBN/IMiD positive control, and the standard three-body cooperative-equilibrium **degradation-window** model
(DC50/Dmax/hook) are in **SI §S2**, framed as a **sensitivity-analysis framework that could accept
experimentally measured or validated ensemble-weighted binary affinities in future work** — we do **not**
derive Kd values from the current raw ABFE absolutes (whose scale is not validated, §3).

**At marketed-library scale, no repurposing candidate survives the counter-screen** (the same funnel over the ~6,000-compound Broad Drug Repurposing Hub plus a 9-target anti-target panel: every paralogue-margin survivor receives a more favourable docking score at ≥1 counter-screen target than at NR4A3, whereas `denovo_401` does not). This is a screen-level result — it does *not* prove no NR4A3-selective repurposed drug exists — that **motivates** the de-novo route (§2.6). **Full screen and target panel: SI §S1.**

### 2.6 Generative design produces apparent hits but fails a single-snapshot specificity control
Because the repurposed library produced no candidate that survives MM-GBSA as NR4A3-selective (§2.5), we
ran a **pocket-conditioned de-novo generative campaign** and put its output through the *same* selectivity
funnel. (1) **Receptor.** We anchored generation and docking to a **release-derived frame from a bias-free
continuation** (seeded from a metadynamics-derived conformation, then propagated without bias;
`nr4a3_release_druggable.py`: Rg ≈ 0.737, confirmed fpocket druggability 0.667, in the empirical drug-bound
reference range) — the release-derived frame from §2.3, not the biased-metad frame — keeping a small
druggable sub-ensemble since the pocket is dynamic. (2) **Generation.** DiffSBDD (pocket-conditioned
diffusion, pretrained CrossDocked weights; `nr4a3_denovo.py`) generated molecules into that pocket,
conditioned on the lining residues incl. the engageable divergent handles; a lead-size constraint
(`--num_nodes_lig`) plus a molecular-weight floor in scoring removed a fragment bias seen in an
unconstrained pilot (whose top hits were trivially small benzoic/toluic-acid-class fragments). The
size-constrained production generation showed **high validity and uniqueness**: of 195 generations, **191
valid and unique, 96 % PAINS-free, 92 % contacting ≥4 of the 5 engageable handles** in the generated pose
(developability filtering below reduces this to 11 advanceable molecules). (3) **Funnel.** We docked the top-20 generations into the
NR4A3-release / NR4A1 / NR4A2 pockets for a selectivity fingerprint (`denovo_15` the
docking-level NR4A3-selective lead **by margin** — NR4A3 favoured over both paralogues by ≥1 kcal/mol),
then **MM-GBSA-rescored all 20**. *(Receptor-state caveat: unlike the §2.5 repurposed matrix, which was
fully criterion-matched — all three paralogues at their metad-opened frames — this de-novo funnel docks NR4A3 in
its **release-derived** frame (fpocket 0.667) against the **biased-metad** NR4A1 frame 524
(0.981) / NR4A2 frame 125 (0.938), because the release run (§2.3) made that frame the defensible
NR4A3 receptor. The states are therefore **not** matched the way §2.5's are. We had argued this asymmetry
plausibly runs *against* NR4A3-selectivity (the paralogue pockets are scored in their more-druggable opened
state), but a higher fpocket score does not guarantee a more favourable docking score for *every* chemotype,
so we treat the direction of this asymmetry as **a limitation of uncertain direction across the library**,
demonstrated only for the candidate: a fully criterion-matched re-dock (NR4A3 metad-opened) **has since been run for
`denovo_401`** (§2.7) and it **retains a positive NR4A3-favoured endpoint margin** there too (+7.44 ± 4.18), so the positive *sign* is not unique to the design frame — though, as §2.7 shows, the candidate does **not** clear the frame-matched decoy null in that metad frame, i.e. specificity-control success is itself frame-dependent.)* The result is qualitatively different
from the repurposed library: the funnel returns **de-novo matter that survives single-snapshot MM-GBSA without
reversing** (census: confirmed_selective 3 · rescued 7 · weakened 1 · confirmed_nonselective 9 · **reversed 0**),
where the repurposed matter reversed. But a medicinal-chemistry triage of the three `confirmed_selective` hits
(`denovo_15/94/57`) shows **none is simultaneously chemically viable and a strong selective binder**: the two
strong-margin hits carry generative-model liabilities (a carbamic acid / reactive diene; a peroxide / acetals)
and the one clean, synthesizable hit gives the weakest signal — the expected behaviour of a pretrained
pocket-conditioned diffusion model (DiffSBDD) with no stability term in its objective. **No single-snapshot
nomination was accepted**, and the per-molecule forensic record (SMILES, liabilities, and the drug-likeness top
hit `denovo_189` that came back non-selective) is archived in **SI §S8** as the falsification record, not
carried here. The load-bearing claim is the **funnel and the selectivity direction it produces**, not any single
molecule — and, as the next paragraph shows, **even that direction fails a decoy specificity control at the
single-snapshot tier.**

**Specificity control: the single-snapshot MM-GBSA selectivity verdict fails a decoy test, so
selectivity is NOT established by this tier.** We ran a **specificity control** — 38 diverse **non-NR4A
marketed drugs** (`decoy_library.py`) through the *identical* dock→MM-GBSA funnel — and a **developability-gated
re-screen** of the generations (the structural-alert gate of §2.5 added after the artifact finding;
`structural_alerts.py`). Two results force a retraction of the "MM-GBSA-confirmed selective" claim. (i) The
decoy null is **`confirmed_selective` in 39 % of cases (15/38; ~58 % have a positive NR4A3 margin)** —
including **caffeine, ibuprofen, lidocaine, phenytoin** — while the developable de-novo set is
`confirmed_selective` in only **2/11 (18 %)**, i.e. **below the decoy baseline and not enriched.** The
single-snapshot, single-pose MM-GBSA pipeline **yields positive NR4A3 margins for a large fraction of
unrelated compounds** (~40–58 %), so it has **no demonstrated specificity** — which also explains why the
artifact `denovo_15` was pipeline-classified `confirmed_selective`. The asymmetric receptor setup (NR4A3
scored in its release frame vs the paralogue frames) is one *plausible contributor* to this bias, not a
demonstrated mechanism (the decoy experiment establishes the high false-positive rate, not its cause). (ii) Of the generations, only **11/191 survive the
developability gate**, and **none of the clean ones is robustly NR4A3-selective** once the decoy baseline is
accounted for. **We use the decoy run as an empirical null, and one candidate clears it.** Rather than the
non-discriminating "margin > 0", we rank against the **decoy empirical 95th percentile (+13.1 kcal/mol;
`selectivity_calibration.py`)** — an empirical rank, not a precisely calibrated universal cutoff (with n = 38
the upper tail is estimated from one or two order statistics, so we also report the raw rank and, in SI, the
full ECDF and a bootstrap interval on the percentile). Against that bar, **`denovo_111`** (a clean
fluoro-phenyl-pyrrolidine, QED 0.87 / SA 2.9, NR4A3-margin **+15.7**, favoured in *both* receptor states,
**ranked above 37 of 38 decoys**) is the **first de-novo hit above the empirical decoy-null percentile** in
that harvest — every other de-novo and decoy molecule *in that harvest* falls in the null. *(A later generation batch produced `denovo_401`, whose single-snapshot margin
+13.92 also exceeds this +13.1 bar and which additionally survives multi-snapshot de-noising (§2.7); it — not
`denovo_111` — is the carried candidate. (`denovo_111`, the earlier single-snapshot foothold, de-noised well as the
*neutral* form but was later **withdrawn** when the species-resolution sweep showed its *cation*
reverses selectivity — §2.7; so `denovo_401` is the sole candidate advanced through the computational funnel.))* So the
read is therefore **not** "no selectivity"; it is "**raw single-snapshot MM-GBSA is
non-specific; decoy-calibration flagged one above-null candidate, `denovo_111`, which was *subsequently
rejected* after protonation-state resolution reversed its predicted selectivity (§2.7) — a microstate
artifact, not a genuine lead**." The de-novo program
continues as a **candidate-optimization campaign around `denovo_401`** (its then-foothold `denovo_111` was later
withdrawn as protonation-fragile, §2.7) — scaffold-seeded generation conditioned on
the four paralogue-divergent handles (L406/T410/I484/L534), heavily oversampled + developability-gated, and
ranked against the decoy null — with **decoy-calibrated multi-snapshot MM-GBSA** to confirm the survivors and
selectivity FEP reserved for an above-null lead. The decoy control is retained as a **standing specificity
gate** every candidate must clear.

### 2.7 Multi-frame rescoring retains one candidate for higher-tier evaluation (`denovo_401`)
The decoy control (§2.6) showed the *raw* single-snapshot MM-GBSA margin is non-specific. We built the
follow-up tier the §2.6 plan named — **multi-snapshot endpoint MM-GBSA** (`endpoint_dG_multisnapshot`:
minimize → short GB Langevin MD → ΔG averaged over 10 frames + SD) — and ran it on the lead set. It
**independently confirms the noise diagnosis and then isolates a survivor**:

| candidate | single-snapshot margin | **multi-snapshot mean ± SD** | margin − SD | verdict |
|-----------|------------------------|------------------------------|-------------|---------|
| `denovo_393` (was the single-snapshot best, above decoy *max*) | +18.34 | **−2.95 ± 3.65** | — | **collapses** (selectivity gone) |
| `denovo_780` | +14.66 | +2.07 ± 6.36 | <0 | within noise of 0 |
| `denovo_924` (negative control) | −19.41 | −25.20 ± 4.55 | — | stays non-selective ✓ (behaved as expected) |
| **`denovo_401`** | +13.92 | **+12.83 ± 2.98** | **+9.85** | **holds** (margin − SD > 0) |
| **`denovo_111`** (neutral form; later **withdrawn** — cation reverses, see species resolution) | +15.70 | **+14.60 ± 4.10** | **+10.50** | holds *as neutral* (but protonation-fragile) |

**Figure 5** ([`../modalities/nr4a3-fig5.png`](../modalities/nr4a3-fig5.png); rendered by `nr4a3_journal_figures.py`). The de-novo candidate `denovo_401`, across four panels. **(a)** Multi-snapshot de-noising: each candidate's
single-snapshot margin (open circle) vs its multi-snapshot mean ± SD (filled) — the single-snapshot best
`denovo_393` (+18.34) collapses to ~0, and the negative control `denovo_924` stays non-selective (behaving as
expected — a single negative control, not a demonstration that the method discriminates in general). Two
candidates hold at this stage (`denovo_401` and neutral `denovo_111`, both margin − SD > 0); **after
subsequent protonation-state resolution (§2.7) only `denovo_401` remains** (`denovo_111`'s physiological
cation reverses). `denovo_401`'s margin − SD = +9.85 is clear of the multi-snapshot decoy-null 95th
percentile (+6.69); here **margin − SD is a prespecified advancement heuristic using the frame-to-frame SD,
not a confidence interval**. **(b)** The decoy null is receptor-frame-dependent: `denovo_401` clears the whole same-tier
null in its unbiased *release/design* frame but not in the biased *metad-opened* frame (§2.7). **(c)** 2D
structure of `denovo_401` (MW 304, QED 0.80, SA 3.87, no structural alerts). **(d)** The predicted docked pose
of `denovo_401` (orange) in the metadynamics-opened NR4A3 LBD (teal cartoon; pocket-lining side chains grey)
— a screening-grade *docked* pose in an AF2-derived LBD *model*, an illustration of the predicted binding
geometry, **not** an experimental complex or a validated pose. Single-trajectory GB-implicit MD, not FEP —
direction and robustness, not affinity.

**Supplementary Figure S1** ([`../modalities/nr4a3-figS1.png`](../modalities/nr4a3-figS1.png); generated by
`nr4a3_journal_figures.py` from the §2.7 per-receptor ΔG values). Per-receptor multi-snapshot MM-GBSA
binding ΔG of `denovo_401` against NR4A3 vs NR4A1/NR4A2, in the unbiased *release* (design) frame and the
biased *metad-opened* frame. NR4A3 is the most-favoured receptor in **both** frames (the margin **retains the
same sign in the two selected receptor frames** — not a general frame-robustness claim), but the
NR4A3-vs-NR4A1 margin shrinks from +14.75 (release) to +7.44 (metad-opened) — *magnitude* is frame-dependent
(as discussed below). These are **short-trajectory multi-frame endpoint MM-GBSA without entropy estimation or
a fully equilibrated receptor ensemble**, so read the ΔΔG direction, not Kd.

Two things follow. (i) The subsequent multi-frame analysis revealed **frame-to-frame SDs of ~4–6 kcal/mol —
comparable to or larger than several single-snapshot margins** — so the single-snapshot "above-null" harvest is noise-dominated; `denovo_393`'s +18.34 was an
extreme-value artifact (de-noised, it is ~0/slightly paralogue-favouring): the apparent lead lost its
positive margin under the multi-frame analysis while the prespecified negative control stayed non-selective,
which corroborates the decoy finding from an orthogonal direction. (ii) **`denovo_401` is the exception that
survives**: its multi-snapshot margin (+12.83) is barely below its single-snapshot value, the SD (2.98) is
small, and **margin − SD = +9.85 ≫ 0** — a substantially more favourable NR4A3 endpoint *score* (mean
−38.18 kcal/mol, an inflated non-affinity endpoint value, read for direction only) than either paralogue
(~13–15 kcal/mol weaker). So the de-noising tier **reduces the single-snapshot false-positive behaviour and
retains one candidate above the selected design-frame decoy reference**: it killed a noise artifact and
identified a reproducible survivor for advancement. `denovo_401`
(`COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1`; MW 304, QED 0.80, SA 3.87, no structural alerts)
is the program's **first candidate retaining an NR4A3-favoured endpoint-score margin through the
multi-snapshot screening tier**, subsequently taken through selectivity ABFE (§3). A formal in-silico developability profile (`nr4a3_developability.py`, RDKit) confirms the
binder **passes the selected in-silico property and structural-alert filters**: 0 Lipinski violations,
**Veber-compliant** (TPSA 29.5, 7 rotatable bonds), **clean on both the PAINS and BRENK structural-alert
catalogs**, with **moderate predicted synthetic accessibility** (SA 3.87, a heuristic score). The one
honest watch-item is **lipophilicity (cLogP 4.63)**, to be tracked as the binder is elaborated. As a *binder*,
this is Rule-of-5-compliant; assembled into a CRBN degrader (binder + E3 ligand + linker) the molecule is
projected into normal **beyond-Rule-of-5** PROTAC space (projected MW ~657) — expected for the modality, and
the linker exit-vector build is tracked as an explicit next step (completeness ledger E4). The single-snapshot foothold `denovo_111` also de-noised well **as the neutral form**
(+14.60 ± 4.10) — but a **pre-FEP species-resolution sweep subsequently demoted it**: `denovo_111`
carries a **basic pyrrolidine**, and in its **cationic** protonation state its selectivity **reverses**
(multi-snapshot margin **−15.01 ± 5.14**, binding NR4A1 *more* tightly than NR4A3, −36.81 vs −21.80).
*(Protonation-state assignment method: a rule-based RDKit SMARTS assignment (`fep_species.protonation_variants`)
— an aliphatic secondary/tertiary amine that is not an amide, imine, or aromatic N
(`[NX3;!$(N=*);!$(N-C=[O,N,S]);!$(n)]`) is emitted in a +1 form as well as neutral; non-basic groups stay
neutral. This is a **rule-based state assignment, not a pKa calculation**: we do not compute a predicted pKa,
protomer populations, or tautomers, so this result demonstrates **protonation-state *sensitivity*, not the
dominant physiological microstate**. Both the neutral and cationic forms of `denovo_111` were scored; because
the cationic form reverses the endpoint-score preference and the present procedure cannot establish which
microstate dominates at pH 7.4, `denovo_111` was **conservatively not advanced**. `denovo_401` contains
**no basic nitrogen** in the specified structure — an ether / aryl / tertiary-alcohol scaffold — so this
SMARTS emits only its neutral form.)* Its earlier margin was therefore a **neutral-form artifact for
`denovo_111`**, which is **withdrawn as an FEP candidate**, leaving **`denovo_401` the sole candidate advanced
through the computational funnel** (see the species-resolution paragraph below).

**Honest weight.** `denovo_401` clears the **FEP-worthiness bar this
program pre-committed to** (multi-snapshot margin − SD > 0, favourable NR4A3 endpoint score, persistence of the modeled pose over the short screening trajectory) — which is
a real upgrade over a single-snapshot point estimate — but it is **single-trajectory GB-implicit MD, not
FEP**, **unsynthesized**, and **un-validated**. It is also the **best-of-~10** candidates multi-snapshot-tested
(and best-of-~200 generated), so its +12.83 point estimate carries a **selection (winner's-curse) bias on top
of the reported ±2.98 SD** — the same extreme-value logic that demotes `denovo_393`'s single-snapshot +18.34
applies to picking `denovo_401` as the survivor. An independent re-run **estimates the within-candidate seed
sensitivity after selection** — it does **not** de-bias the best-of-N selection (no single rerun can).
**We ran that independent re-run** (fresh Langevin seed): `denovo_401` reproduces at
**+14.75 ± 4.82** (vs the original +12.83 ± 2.98; ΔG NR4A3 −37.50 / NR4A1 −22.75 / NR4A2 −20.43) — the margin
does **not** regress toward the null under an independent trajectory (it lands slightly higher), so the margin is
**not specific to one Langevin seed**. This bounds the *within-candidate/seed* variance; the *between-candidate*
best-of-N selection remains a design-stage selection caveat — higher-tier calculations (ABFE) test the
selected molecule but do **not** erase the selection process (only re-selection from scratch would).
The decoy null (§2.6) was originally computed at
*single-snapshot*, so the matching question was whether "+12.83 survives de-noising" is the same as "+12.83
is above a *multi-snapshot* null." **That control has now been run: re-scoring
all 38 decoys through the identical multi-snapshot tier gives a far tighter null — mean −3.47, 95th
percentile **+6.69**, max decoy **+7.10**, `confirmed_selective` 11/38 (29 %) — vs the single-snapshot
+13.1 / +16.46 / 39 %.** Against that re-calibrated bar **`denovo_401`'s +12.83 ± 2.98 clears the
multi-snapshot 95th percentile and exceeds the single highest decoy even after subtracting its SD
(margin − SD = +9.85 > +7.10)** — so the margin is not merely de-noised but **above a decoy null recomputed at
the same tier.** *(That null controls the **docking/MM-GBSA scoring** step
(marketed drugs pushed through the identical dock→multi-snapshot funnel), but it does **not** control the
**generative** step: `denovo_401` is a DiffSBDD molecule pocket-conditioned on the NR4A3 **release** frame,
whereas the decoys were fit to no pocket — so in the release frame `denovo_401` carries a design-match
advantage the decoys lack, which inflates its NR4A3 leg (hence its margin) relative to the null. Consistent
with this, in the **metad-opened** frame — which `denovo_401` was *not* conditioned on, so neither it nor the
decoys have a generation advantage — it does **not** clear the null (below; the paper elsewhere reads that as
the metad frame being non-discriminating, but it is also the less-confounded specificity test). A fully clean
specificity test would require a generation-matched decoy null (in flight, §4). On the confound's magnitude:
all ~191 **valid unique generated molecules** were pocket-conditioned on the *same* release frame, yet the set
is **not enriched** over the marketed-drug decoys and only **two of ~11** multi-snapshot-tested candidates
survive (§2.7). **The absence of broad enrichment argues against a *uniform* frame-conditioning effect, but
does not quantify the candidate-specific design-match confound** — a generation-match advantage can be
heterogeneous, concentrated in top-ranked candidates, and amplified by best-of-N selection, and only a subset
reached the expensive multi-snapshot tier. So against the null we have, "above-null" is a **de-noised
foothold, not yet a fully-controlled specificity result**; the higher-tier ABFE result (§3) provides an
**additional, methodologically distinct energetic check** (it does not, by itself, resolve best-of-N
selection or the generation-match confound).)* **A receptor-robustness check (a
fully criterion-matched re-dock — NR4A3 in its *metad-opened* frame rather than the release frame — then the same
multi-snapshot rescore) keeps `denovo_401` NR4A3-favoured but weaker:
+7.44 ± 4.18 (ΔG NR4A3 −32.37 vs NR4A1 −24.93 / NR4A2 −22.80)** — so the selectivity *direction* is robust
across receptor frames (not a release-frame artifact), but the *magnitude* is frame-dependent. **The matching
metad-frame decoy null has since been run, and it forces an honest narrowing: `denovo_401`
does *not* clear it.** In the metad-opened frame the decoy null *balloons* — mean +1.59, 95th percentile
**+17.70**, max decoy **+24.74** (vs the release frame's +6.69 / +7.10) — because the biased wide-open pocket
scores *most* drug-like matter as strongly NR4A3-favoured (diphenhydramine +24.74, lidocaine +22.08); against
that inflated null `denovo_401`'s +7.44 sits at only ~the **84th percentile** (6/38 decoys score higher). So the
metad-opened frame is a **poor, promiscuous discriminator**, and `denovo_401`'s specificity-controlled result is
**release-frame-specific**: present in its *design* (bias-free-continuation) frame, but it does **not** generalise to the
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
`denovo_401` as the sole candidate advanced through the computational funnel.** A low hit-rate either way (the funnel does **not** *abundantly* yield
de-noising survivors), with the negative control staying non-selective throughout —
consistent with the selectivity-architecture analysis (SI §S3): a cryptic pocket that is a *fragile but not empty* place to source a margin.

**Pre-FEP species resolution — resolve the exact 3D molecule before spending on FEP.** Because
FEP presupposes a correct, well-defined species, we docked + MM-GBSA-scored **denovo_401's 16 stereoisomers**
(its 4 stereocenters are DiffSBDD-assigned, i.e. arbitrary) and **denovo_111's neutral/cationic forms**.
Two results. (i) **the selected isomer was not uniquely favoured in the endpoint analysis; several
diastereomers retained positive margins:** nearly all 16 diastereomers were pipeline-classified
`confirmed_selective` (an endpoint tier itself shown non-specific, §2.6), and de-noising the top four gives
**iso08 (the C13-epimer) +11.36 ± 5.25** and the **as-generated isomer +9.54 ± 4.26** as co-best (overlapping
within SD), with iso00/iso14 behind — so the as-generated isomer was **among the subset advanced for
multi-frame evaluation**, not established as uniquely optimal (isomer selection is itself another
winner-selection step). **The completed
three-replicate ABFE (§3) was run on the as-generated diastereomer** (the fully-specified SMILES
`COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1`, 4 defined stereocenters; input coordinates in the
reproducibility archive), with the **iso08 C13-epimer** its one co-best MM-GBSA alternative and the single
open FEP comparison remaining on the stereochemistry axis. (ii) **denovo_111 is withdrawn:** selective as
the neutral form but its **cationic form reverses** (multi-snapshot **−15.01 ± 5.14**, NR4A1 −36.81 <
NR4A3 −21.80), so its earlier de-noised margin was a neutral-form artifact. Net: **`denovo_401` is the sole
candidate advanced to ABFE, on a resolved diastereomer.**

### 2.8 Conditional ABFE tests the NR4A3-favoured receptor contrast

The endpoint MM-GBSA tiers rank and de-noise but are not affinity-grade. As a **higher-tier explicit-solvent
free-energy test** of the one candidate that survives them, we ran **absolute binding free-energy perturbation
(ABFE)** — explicit-solvent
double-decoupling with a Boresch orientational restraint and MBAR reduction, on an independent-λ-window engine
(`nr4a3_abfe.py`; protocol and benchmarks in §3) — for `denovo_401` (the resolved DiffSBDD-generated
diastereomer, SMILES `COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1`) against each of NR4A3, NR4A1 and
NR4A2 in its selected opened conformer.

**Result (three independent-seed replicates; error = between-replicate SD, n = 3).** Raw-engine per-receptor
ΔG_bind = **+3.5 ± 1.4 (NR4A3) / +8.3 ± 1.1 (NR4A1) / +8.5 ± 0.7 (NR4A2)** kcal/mol, giving
**ΔΔG(NR4A3 − NR4A1) = −4.76 ± 2.03** and **ΔΔG(NR4A3 − NR4A2) = −4.98 ± 0.68** kcal/mol — both favour NR4A3,
with the **direction unanimous across all three replicates**. Read at its correct weight this is a *relative,
conditional* preference for the selected opened NR4A3 conformer over the selected opened paralogue conformers —
**not** an "NR4A3 engages, paralogues do not" claim. (The NR4A1 contrast SD is wider, ± 2.03, driven by one
replicate whose NR4A3 leg sampled ~2.5 kcal/mol weaker; excluding it, r1/r3 agree at −6.9/−4.5.)

**Three limits bound the reading, and two repairs are in flight.** *(i) The absolute scale is not validated.*
The same engine on a textbook benchmark (T4-lysozyme L99A + benzene, experimental ΔG_bind = −5.2 kcal/mol)
returns **+1.90 ± 0.09**, under-binding by **≈ +7.1 kcal/mol** — a failed/strongly-biased absolute benchmark —
so we interpret **the receptor contrasts rather than the raw absolute values**, never calibrated absolute
affinities, and do not treat +7.1 as a subtractable constant (a single system cannot establish a
target-independent offset). The contrast cancels the literally shared solvent leg and any *truly common*
additive bias, but **remains vulnerable to receptor-specific complex-leg errors** (e.g. the NR4A2 overlap
defect below) — it is not invariant to all engine error. *(ii) The NR4A2
contrast is provisional.* One complex-NR4A2 λ-window pair is under-overlapped (min adjacent overlap 0.003);
because that error propagates **directly** into ΔΔG(3−2) (it is receptor-specific and does not cancel via the
shared solvent leg), the **−4.98 ± 0.68 NR4A2 contrast is an initial estimate held provisional** until the
λ-repair — **in progress** — lands (SI §S7). *(iii) The ΔΔG is conditional on the opened state.* It compares
binding to *selected opened* conformers and omits the receptor-specific free-energy cost of populating that
cryptic-opened state, which is potentially decisive and may differ across paralogues (§4). A second run in
flight rebuilds the NR4A3 leg from an **8XTT-anchored** physical model as a **receptor-model sensitivity test**
(interpreted as sensitivity, **not** an experimental-structure-anchored selectivity calculation, since only the
NR4A3 leg is re-based while the paralogue references are unchanged). Per-replicate paired ΔΔG, λ-overlap
matrices, effective sample sizes, forward/reverse convergence traces, and the per-receptor component
decomposition are in **SI §S7**; the lead-optimization ABFE cross-check (`lo_m0_NCCO`, an FEP tie not an
advance) is in **SI §S5**.

## 3. Methods (reproducible, no wet lab)
Scripted in `research/modalities/`, run as managed AWS SageMaker GPU/CPU jobs (GitHub Actions
`gpu-*-aws.yml`). Structure: AlphaFold2 (AFDB) + fpocket (file→pocket mapping derived from data,
`fpocket_lib.py`). Cryptic pocket: OpenMM + PLUMED well-tempered metadynamics with checkpoint/restart and
fail-loud pre-flight guards ([`../modalities/metad-methods-appendix.md`](../modalities/metad-methods-appendix.md)).
**Gate 3A (persistence after bias removal):** unbiased "release" MD (`nr4a3_md_release.py`, OpenMM, no PLUMED) seeded at the
selected reference frame at Rg 0.717 nm (triplicate replicas), with per-frame fpocket on all three release trajectories; the
druggable receptor for all downstream design is extracted from the release trajectory
(`nr4a3_release_druggable.py`).

**Pocket detection and pocket tracking.** All cavity detection used fpocket with default parameters
(`fpocket -f <model.pdb>`); within a single run, info.txt pocket numbers were bijectively matched to their
residue/vertex files by alpha-sphere fingerprint, failing loudly on ambiguity (`fpocket_lib.py`). The
reference "orthosteric Pocket 5" was defined **once**, on the static AF2 model, as the highest-druggability
pocket carrying ≥1 residue in the LBD window 373–626 (`nr4a3_fpocket_enumerate.py`), giving druggability 0.495
with lining residues spanning 406–534. Because fpocket's per-run numbering is **not** a persistent physical
identifier, the same site was re-identified in every other structure — MD/metadynamics/release frames and each
8XTT NMR conformer — **not by pocket number but by maximal residue-set overlap** (the detected pocket sharing
the most lining residues with the reference set; argmax of the intersection, requiring ≥1 shared residue). This
per-frame tracking was **blind to the druggability score** (the overlap-maximizing pocket was selected first
and its score read out afterward), although the original reference pocket was itself druggability-selected on
the static model. **Three honest limits of this scheme, which the manuscript does not overstate:** (i) the
match threshold is only "≥1 shared residue," with **no** minimum-overlap fraction, centroid-distance, or
volume-overlap gate, so in a poorly-formed frame a spurious low-overlap cavity could be selected; (ii) the
reference set differs between analyses (MD/release match the full 406–534 span; 8XTT matches the ten named
lining residues after a BLOSUM62 alignment with a ≥0.80-identity guard), so "the same rule" is only
approximately uniform across sections; and (iii) **split/merge is not explicitly handled** and frames with
**no** overlapping pocket are recorded as missing (`None`) and **excluded** — not scored zero — so every
reported "fraction of frames/conformers druggable" has a denominator of *frames with a detected overlapping
pocket*, which can inflate the fraction where the site is frequently undetected. The fpocket build was
resolved per job from conda-forge and **not pinned**; the resolved version is a reproducibility gap we flag
(the 8XTT re-extraction and release scans may use different fpocket builds).
**Required change (in progress as the harmonized rerun).** Because the reference site was chosen as the
highest-*druggability* pocket in a residue window that is essentially the whole LBD, the foundational site
identity is **partly outcome-selected**. The submission-gate fix is to define the orthosteric site **without
using the fpocket score** — from a fixed, prespecified set of canonical NR ligand-pocket residues (mapped by
structural alignment to homologous NR orthosteric sites) — then detect cavities, match to that region under a
composite Jaccard + fraction-recovered + centroid gate (replacing the ≥1-residue rule), and read druggability
only afterward, under one pinned fpocket build across the reference panel, AF2, all 20 8XTT conformers, the
three metad replicas, and the three release replicas. **Dependency audit.** Because the generative campaign
was conditioned on a receptor frame selected by this provisional classifier, the rerun must confirm that the
**exact release-derived frame used to generate `denovo_401` still qualifies as the same mapped orthosteric
site and still exceeds D\***; if it does not, the generation receptor — not merely a reported frame-fraction —
is affected. This audit is the primary submission gate (§4).
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
fail-loud guards + an audit log — to produce criterion-matched opened-pocket ensembles for the selectivity
matrix (§2.5). **Warhead / matrix:** smina docking of a real ChEMBL NR4A library into each paralogue's
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
its standard-state correction, so ΔG_bind = ΔG_dec,solv − ΔG_dec,cplx − SSC. The engine (`nr4a3_abfe.py`) is an
**independent-λ-window** design rather than a monolithic Hamiltonian-replica-exchange stack: each window
is an independent OpenMM simulation that, every iteration, evaluates the reduced potential at *all* λ and writes
a small per-window checkpoint; MBAR then reduces the per-window samples to each leg's ΔG with a per-iteration
convergence trace. We adopted this specifically for **spot-interruption robustness** — small per-window
checkpoints resume losing ≤1 iteration, whereas the earlier monolithic-`.nc` replica-exchange stack (Yank) lost
long spot runs to all-or-nothing checkpointing — and the engine was **evaluated on two benchmark systems**, with
**opposite outcomes** ([`../modalities/nr4a3-abfe-calibration.json`](../modalities/nr4a3-abfe-calibration.json)):
a **hydration-free-energy** benchmark (methane ΔG_hyd = **+1.60 ± 0.04** kcal/mol vs experimental +2.0, FreeSolv — a **−0.40**
kcal/mol offset; **approximately reproduced**, which supports the basic solvent-decoupling implementation on a
simple neutral test system — it does *not* validate charge assignment, conformational sampling, or drug-like
solvation for `denovo_401`) and a **protein–ligand binding** benchmark (T4-lysozyme L99A + benzene; below) that **fails by ≈ +7.1
kcal/mol**. Because one benchmark passes and the other fails, this is a **benchmark evaluation, not a successful calibration**:
it measures the engine's systematic offset on an *absolute* ΔG_bind and shows the absolute scale is **not** validated. The
NR4A3-vs-paralogue **ΔΔG** is the selectivity read-out (CUDA on the A10G; SageMaker managed-spot *Training* with
continuous per-window S3 checkpointing). **Protocol: 2 ns/window, n_iter = 2000, three independent-seed replicates** (r1/r2/r3; error bars =
between-replicate SD, n = 3), reduced 2026-07-08 with a per-window dedup-by-iteration safeguard on the MBAR
input so the crash/resume history of the nr4a2 legs does not double-count samples or shrink the SE. **The
three-replicate ΔΔG result and its conditional/opened-state reading are reported in Results §2.8** (raw
per-receptor ΔG_bind, the two ΔΔG contrasts, the unanimous direction, and the provisional-NR4A2 caveat). **Full FEP diagnostics are in SI §S7** (per-replicate paired ΔΔG table, λ-overlap matrices, effective sample sizes, forward/reverse convergence traces; data in `results/nr4a3-abfe/diagnostics/`): they recompute these ΔG_bind from the raw reduced potentials to within ≤0.03 kcal/mol (a reproducibility check), and show healthy MBAR overlap across most windows (adjacent ≈0.2) with one **honest exception — a locally under-overlapped window pair (min adjacent overlap 0.003) in the complex-NR4A2 leg.** (The direct propagation of this defect into ΔΔG(3−2), the resulting **provisional** −4.98 ± 0.68 NR4A2 contrast, and the λ-repair are interpreted in §2.8 and detailed in SI §S7; we do not report calibrated absolute ΔG_bind.) The engine mis-predicts a rigid textbook benchmark
(T4-lysozyme L99A + benzene) by ≈ +7.1 kcal/mol (below), which we read as a *failed/strongly-biased
absolute benchmark* — evidence the protocol is not yet validated for absolute affinity — **not** as a
universal additive engine constant to subtract from NR4A3. The raw-engine NR4A3 absolute (+3.5) is
therefore not quantitatively interpretable on its own; the selectivity conclusion rests entirely on the
**ΔΔG**, which is unaffected by any common per-engine bias.
To gauge whether the engine reports meaningful *absolute* affinities, we ran it on a
**known protein-ligand binding free energy — T4-lysozyme L99A + benzene** (rigid textbook cavity, experimental ΔG_bind =
−5.2 kcal/mol; Morton & Matthews 1995; PDB 181L), through the identical double-decoupling + Boresch-restraint + MBAR path
(12 windows, 1000 iterations, same baked engine). It returns **ΔG_bind = +1.90 ± 0.09 kcal/mol** — i.e. the engine
**under-binds this benchmark by ≈ +7.1 kcal/mol** (published converged ABFE on this system is −5 to −6.5 kcal/mol).
We treat this as what it is: a **failed / strongly-biased absolute benchmark**, indicating the automated,
single-replicate, 1-ns/window protocol is **not yet validated for absolute affinity**. Potential contributors
include incomplete cavity-water and ligand-orientation sampling, restraint/standard-state handling, the λ
schedule, and force-field limitations, **although the present benchmark does not isolate the source of the
bias**. We explicitly **do not** treat +7.1 kcal/mol as a universal additive engine offset:
a single system cannot establish a target-independent constant, because absolute-ΔG error (force field, water
sampling, receptor reorganization, restraint/standard-state handling, finite sampling) is system-dependent.
Accordingly we **make no offset-corrected absolute claim** and rest the selectivity conclusion on the **ΔΔG**.
Two consequences follow. **(i) The receptor contrast may benefit from partial common-mode cancellation.**
Because the ligand-in-water (solvent-decoupling) leg is **literally shared** and the restraint scheme is
identical, the contrast is, algebraically, ΔΔG(3−1) = −ΔG_cplx,3 + ΔG_cplx,1 − SSC₃ + SSC₁ (the shared
ΔG_solv drops out), so a per-engine bias cancels **only to the extent it is common across the receptors'
complex legs and standard-state corrections** — which system-dependent complex-leg error is not guaranteed to
be. The **smaller observed NR4A2 contrast SD (0.68 < either absolute leg's SD)** is *consistent with, but does
not prove,* cancellation of shared errors; the NR4A1 contrast SD is wider (± 2.03), where one anti-correlated
replicate defeats any cancellation in an n = 3 sample. We therefore claim only lower *observed* run-to-run
variation in the NR4A2 contrast, **not** demonstrated cancellation of systematic complex-leg error. The
explicit per-receptor component decomposition (ΔG_cplx and SSC per receptor, with the Boresch restraint
anchors) is tabulated in **SI §S7**. **(ii) The ΔΔG is a *conditional* binding selectivity, not the full thermodynamic selectivity.**
The calculation compares `denovo_401` binding to *selected opened* NR4A3/NR4A1/NR4A2 conformers, so it estimates
ΔG_bind **conditional on the receptor already being in its opened state** — it **omits the receptor-specific
free-energy cost of populating that cryptic-opened conformation**. For a paper whose premise is a cryptic pocket,
this term is potentially decisive and may differ across the three paralogues (their opening penalties are not
shown equal): a ligand can bind a rarely-populated pre-opened conformer strongly yet bind the equilibrium apo
ensemble weakly, and paralogue-specific opening penalties could narrow or even reverse the conditional margin.
The ensemble/state-weighted ABFE that would close this — per-paralogue opening free energies folded into a
state-weighted ΔG_bind — is **not done here** and is a primary revision task (§4); the reported ΔΔG must be read
as **conditional-on-opened-conformer** selectivity. Full calibration record:
[`../modalities/nr4a3-abfe-calibration.json`](../modalities/nr4a3-abfe-calibration.json).

**Lead-optimization cross-check.** A single scaffold-decorated variant (`lo_m0_NCCO` = `denovo_401` + ortho-acetamido) was put through the identical ABFE engine as an affinity-grade check of an MM-GBSA-predicted tightening and lands **within statistical noise of `denovo_401`** — no resolved improvement under this protocol (free energy does not reproduce the MM-GBSA-predicted gain), so `denovo_401` remains the sole candidate advanced through the funnel; detail in **SI §S5**.

**Why absolute
(ABFE), not relative/mutation, FEP.** The selectivity question is *one* ligand (`denovo_401`) against *three
different* proteins, so there is no ligand pair to alchemically morph — standard relative binding FEP (RBFE),
which transforms ligand A→B within one pocket, does not apply. The relative alternative that *would* fit is
**alchemical protein-mutation FEP** (morph the divergent NR4A3→NR4A1/2 pocket residues, bound vs apo, for a
direct ΔΔG). We deliberately use per-receptor ABFE instead, for three reasons. (i) *Conformational.* Each
paralogue is engaged in its own **opened** conformation of a cryptic LBD pocket (§2.2–2.3); alchemical
mutation would require a sufficiently overlapping conformational ensemble and **may be challenging here because
the selected receptor structures differ in backbone and pocket state** — whereas ABFE
models each receptor independently in its own opened frame. (ii) *Precedent.* ABFE is an established route to
selectivity across related/paralogous pockets (e.g. bromodomain-selectivity ABFE — Aldeghi et al. 2017), which provides precedent for receptor-to-receptor selectivity estimates using ABFE across related proteins (our application additionally involves cryptic/opened conformers, a custom engine, unresolved state populations, and no validated absolute scale). (iii) *Absolute observable, in principle only.* ABFE
would additionally provide an **absolute** ΔG_bind for each receptor; **in this study, however, the failed
T4L benchmark prevents quantitative interpretation of that absolute observable**, so we use **only
receptor-to-receptor contrasts** and make no claim about whether `denovo_401` engages any receptor in
absolute terms. The one cost of ABFE (larger per-leg error than a relative calculation) is
partly recovered here: because the ligand is identical across all three experiments, the solvent-decoupling
leg is literally the same calculation for each receptor and cancels in the ΔΔG, along with common-mode
ligand-charge/protonation error, so the *selectivity* ΔΔG **eliminates the shared solvent leg and may reduce
truly common errors** (a general numerical claim of "better-behaved" would need a relevant selectivity benchmark).
A confirmatory alchemical-mutation cross-check is left as future work, gated on the pocket-homology assessment
noted in [`../method-watch.md`](../method-watch.md). **Receptor prep for
FEP:** the docked opened frame is cleaned with `pdb4amber` (LEaP-compatible, drops MD hydrogens/waters) and its
**disordered N-terminal hinge is trimmed to the folded LBD core** (`_trim_floppy_termini`, adaptive, pocket
never trimmed) — motivated by the structural-sanity control (§2.3: fold intact, core RMSD 1.76 Å) and standard
for ABFE (run on the folded domain, not the disordered tail), though **sensitivity to this truncation was not
separately evaluated**; this also keeps the explicit-solvent box within a
single commodity GPU. **De-novo design:** a selectivity blueprint (`denovo_blueprint.py` → `nr4a3-denovo-blueprint.json`)
classifies the Pocket-5 lining residues into the five engageable selective handles (four discriminating
both paralogues — L406/T410/I484/L534 — and the NR4A1-only lever I531) vs the conserved core
(P411/R481/R485), weighting the both-paralogue handles in the selective campaign; DiffSBDD pocket-conditioned
diffusion (pretrained CrossDocked weights; `nr4a3_denovo.py` + `entry_denovo.py`) conditioned on the
druggable release-frame pocket / divergent handles, with a lead-size constraint and an RDKit cheminformatics
+ pose-handle-contact triage (`denovo_funnel.py`); generated candidates are funneled through the same matrix dock + MM-GBSA pipeline
(`nr4a3_matrix.py` candidate mode). Docking scores are used only as triage priors. All
parsing/mapping/classification/scoring logic is in pure, unit-tested modules (TESTING.md).

## 4. Limitations
In-silico throughout; no molecule synthesized; broader indications (SI §S4) are **motivation, not
demonstrated efficacy**. Therapeutic application to EMC (and AciCC) additionally **assumes NR4A3 dependence, which is not tested here**: the supporting prior (a transfer prior from fusion-addicted EWSR1/FET sarcomas; EMC-native evidence the fusion is a functional driver; a near-invariant clonal fusion in a quiet genome) and the **one decisive gap** (no loss-of-function experiment in any EMC model — the make-or-break dTAG test is delegated to the EMC-program paper), together with the systemic-lead safety/tolerability rationale and the pan-NR4A/CAR-T pole, are in **SI §S9** (safety in **SI §S6**, indications in **SI §S4**). This paper's claimed contribution is the target's **computational druggability/selectivity, not EMC efficacy**.
The structure is an AF2 model
(NR4A3 has no ligand-bound experimental structure; its apo LBD was released as a solution-NMR ensemble,
PDB 8XTT, only in 2025) — the MD addresses exactly the single-snapshot limitation. **The 8XTT benchmark
is done (§2.1) and is two-sided:** the experimental apo ensemble is structurally *heterogeneous* at the
mapped site (most conformers occluded, 4/20 above D\* — structural corroboration, not a population estimate),
**but** the AF2 atomic pocket geometry *diverges* from it (pocket-local Cα-RMSD 3.56 Å, handle 3.44 Å). Two
prediction *directions* transfer to 8XTT conformers (PocketMiner enrichment, denovo_401 MM-GBSA preference),
so the site's existence and those directions are corroborated while the AF2 *opened geometry* is not.
**A full workflow rebase and the review-warranted controls remain to do** (not yet done here): (i) an
8XTT-*started* metadynamics/MD, generation, and — most importantly — an **8XTT-anchored ABFE** (the current
ABFE is AF2/opened-conformer-conditional); (ii) a **matched 8XTT-frame decoy null** (denovo_401 + the 38
decoys through the same 4 conformers, since we have shown MM-GBSA margins are frame-dependent); (iii)
PocketMiner + docking over **all 20** conformers (not only the 4 cavity-bearing ones), with an AF2↔NMR
vs NMR↔NMR RMSD decomposition and a true residue-contact-graph spatial-patch null; (iv) **repair of the one
under-overlapped ABFE window** (add λ-windows in the complex-NR4A2 decoupling-endpoint region and re-reduce).
Only a **ligand-bound** experimental structure could validate the warhead-engaged pose. We state the central result at its true
weight, with the following caveats made explicit rather than buried:

1. **The 0.931 is a biased-ensemble peak, not a like-for-like beat of the static band.** fpocket
   druggability is a standard, model-derived geometric proxy (a logistic model of hydrophobic enclosure +
   polarity, not raw volume; §2.2 anchors it on an NR panel incl. the occluded 1OVL negative) — a
   druggability *prediction*, not a ground-truth measurement.
   But (a) 0.931 is the **maximum over 600 frames** — report it as a distribution (fraction of frames
   ≥ D\*=0.53, met) with 0.931 as the peak; and (b) it is computed on **biased-MD** conformations, so its
   magnitude is not directly comparable to the *static* drug-bound crystal sites (0.53–0.68) — we do not
   claim it beats that band. fpocket druggability is in any case a geometric screen, not affinity. The release
   simulations test only **short-timescale relaxation** after the bias is removed (persistence, Gate 3A);
   they do **not** establish equilibrium population or accessibility from the closed ensemble (Gate 3B,
   unresolved).
2. **No separate opened free-energy basin.** The original production profile is monotonic (a single resolved minimum, rising wall) and independent replicas likewise **do not resolve a reproducible second minimum**, but their 1-D profiles and minimum locations **differ substantially** (the minimum is not structurally classified as "closed"); the
   druggable conformations are reached by *basin-internal breathing*, not a two-state cryptic opening, so
   the pre-registered Gate 1 ("minimum or shoulder, not just biased excursions") **failed as registered**
   and was **reformulated** as basin-breathing. "Opened state" is shorthand for these breathing sub-states,
   not a distinct metastable conformation.
3. **Gate 3A (persistence) supported; Gate 3B (equilibrium accessibility) unresolved.** These are distinct:
   a geometry can be equilibrium-rare yet persist once seeded. On **3B**, the original single-profile
   ~0.6–0.76 kcal/mol interpretation is **not supported by the independent profiles**: at the fixed reference
   Rg the three replicas assign widely differing free energies (16.0 / 0.06 / 0.83 kcal/mol in r1/r2/r3 order;
   §2.3), read off still-drifting biased F(Rg), and **that fixed coordinate is not yet an equivalent-state (or
   demonstrated-druggable) comparison** across replicas — so 3B is unresolved. On **3A**, the open-seeded release run
   shows the seeded open-like geometry **persists across 3/3 short replicas and is fpocket-druggable in a
   fraction of frames of all three replicas** (≥ D\* in 0.20/0.16/0.28; detected-pocket denominator) — correlated,
   open-seeded, non-equilibrium frame fractions (**not** an equilibrium population), and explicitly **not** a
   static always-open pocket (mean 0.262). The calculations do not
   distinguish conformational selection from ligand-induced stabilization. The design consequence: a warhead
   would need to select-and-stabilise a transiently-druggable open-like geometry rather than occupy a
   permanent pocket — a harder ask, and one whose *equilibrium* likelihood would need reweighted enhanced
   sampling or many independent unbiased trajectories to quantify (§4).
4. **Selectivity handles are a specification with an asymmetric window.** The registered handle-facing
   check confirms the handles stay pocket-facing in the druggable frames (mean 5.0/7; T407/R412 splay out,
   so five engageable). But the engageable *divergent* set is **5 vs NR4A1 and only 4 vs NR4A2** (I531 is
   conserved with NR4A2), so NR4A2 selectivity is the harder, narrower case — and these are a specification,
   not a demonstrated binding margin.
5. **Binding selectivity ≠ degradation selectivity — and that reallocates the whole selectivity problem
   (SI §S3).** The §2.5 matrix is a necessary-not-sufficient filter; degradation selectivity is set by the
   per-paralogue ternary complex (now computed, §2.5 / SI §S2 — no evidence for NR4A3-selective ternary geometry with the representative linker). The selectivity-architecture analysis sharpens
   this from a caveat into a design: selectivity is a **multiplicative budget** (binding × ternary ×
   kinetics) whose factors **compound**, so the binder need not carry it *alone* — but a selective binder is
   still strictly valuable and is the primary goal (`denovo_401` is a decoy-null-screened foothold, not fully
   control-validated (the decoy null does not control the generative step); the second candidate denovo_111 was withdrawn as protonation-fragile — §2.7). The
   computed result that the orthosteric pocket is **enriched for paralogue-divergent residues**
   (70 % vs 43 % across the rest of the LBD) means binder selectivity is handle-rich but
   druggability/noise-limited — so the rational plan keeps the binder selective **and** optimizes it for
   affinity + a productive exit vector. The hoped-for *additional* lever — sourcing paralogue selectivity from
   the **ternary** — **has now been tested (§2.5) and, for a representative PROTAC, does not materialize**:
   the NR4A3/NR4A1/NR4A2 ternaries have **comparable predicted geometry with no evidence for an
   NR4A3-selective ternary**, so the ternary does **not** compound the binder's NR4A1 margin as hoped. Degradation selectivity therefore rests, on current evidence, on the **binder** (plus
   **pharmacokinetics** for NR4A2: CNS exposure is an additional design concern given NR4A2's established
   dopaminergic biology, **but the distribution of toxicity from NR4A2 loss is not established here**
   (§4/SI §S6)), with **linker/exit-vector
   engineering** the only remaining (untested) route to ternary selectivity; and **fusion-vs-wild-type**
   selectivity remains **unobtainable from the degrader** (route to the ASO). Net: running the ternary
   *narrowed* the budget rather than widening it — the binder carries more of the load than the architecture
   originally hoped.
6. **The carried candidate is a chemotype/pose hypothesis, not a synthesized or affinity-validated molecule.**
   `denovo_401` passes the in-silico property/alert filters (§2.7), but remains a docking/endpoint/ABFE-tier
   prediction on an AF2-derived pocket, unsynthesized and un-validated. The durable claim is the
   **falsification-controlled funnel** and the surviving selectivity *direction*, not a developable molecule.
   (Detailed forensic records of the retracted single-snapshot candidates — denovo_15/94/57 and the
   protonation-sensitive denovo_111 — are in **SI §S8**; the main text retains only the falsification sequence
   needed to explain candidate advancement.)
7. **Single-snapshot MM-GBSA is non-specific; multi-snapshot de-noising AND its matching decoy
   re-scoring are now run, and `denovo_401` clears them — leaving ABFE as the last tier: initial
   three-replicate ABFE complete, with the NR4A2 λ-overlap repair pending before final interpretation (§3).** The de-novo
   funnel originally docked an *unbiased-release* NR4A3 receptor against *biased-metad* paralogue receptors
   (a receptor-model asymmetry whose *direction* on selectivity is uncertain — §2.6), and the single-snapshot, single-pose MM-GBSA carries
   no replicate/ensemble average and **fails the decoy control** (§2.6). Two follow-up controls
   resolve this (§2.7): (a) the **multi-snapshot decoy null** (all 38 decoys re-scored
   multi-snapshot: 95th pct +6.69, max +7.10) — `denovo_401` (+12.83 ± 2.98, margin − SD +9.85) **clears it**,
   so the margin is above a decoy null recomputed at the same tier, not merely de-noised — **but that null
   controls the docking/MM-GBSA scoring step only, not the generative step or the best-of-N selection:
   `denovo_401` was DiffSBDD-fit to the release frame it clears the null in, while the decoys were fit to no
   pocket, and it is the best of ~200 generations / ~10 de-noised candidates. So this is a de-noised
   *foothold*, not a demonstrated specificity result** (consistent with its metad-frame failure below, the
   frame it was *not* designed for); and (b) a **fully
   criterion-matched re-dock** (NR4A3 metad-opened) — `denovo_401` stays NR4A3-favoured (+7.44 ± 4.18), confirming
   the *direction* is not a release-frame artifact, though the magnitude is frame-dependent. **The matching
   metad-frame decoy null was then run (§2.7) and, honestly, `denovo_401` does *not* clear it**: in the biased
   metad-opened frame the decoy null balloons (95th +17.70, max +24.74, driven by drugs like diphenhydramine
   +24.74) and +7.44 sits at only ~the 84th percentile — so the metad-opened frame is a poor discriminator, but
   it is also the frame `denovo_401` was *not* generatively fit to, so the above-null result is
   **release-frame-specific (= design-frame-specific)**, not universal. What remains is
   **single-trajectory GB-implicit MD, not ABFE**, so **selectivity ABFE is the quantitative gate — initial
   three-replicate ABFE complete (three-replicate ΔΔG NR4A3-selective), with the NR4A2 λ-overlap repair
   pending before final interpretation (§3)**;
   the receptor-frame dependence is best resolved by ensemble scoring over the druggable release sub-ensemble.

**Selectivity methodology:** docking margins are **triage priors, not affinities**; a quantitative
selectivity claim needs endpoint free energy. The criterion-matched NR4A1/NR4A2 metadynamics runs are
**complete**, so the matrix (§2.5) is genuinely criterion-matched (not opened-target-vs-static-off-target), and
the quantitative tier is now **MM-GBSA-run** rather than planned — but single-snapshot MM-GBSA has **no
entropy and no ensemble average**, so its magnitudes are inflated and only the **verdict/direction** is
trusted; **selectivity FEP** (the defensible affinity tier) is **now run** (independent-window ABFE;
three-replicate NR4A3-selective ΔΔG, §3), and even converged FEP on a
cryptic/induced-fit pocket is sampling-limited. **An independent structural cross-check (AF3-class
co-folding) does not corroborate the pose/pocket, and honestly cannot here.** To test the docked binder
pose by a physically different method than docking/MD, we co-folded `denovo_401` into each NR4A{3,1,2} LBD
with **Boltz-2** (an open AF3-class protein–ligand structure predictor), control-validated on CRBN +
lenalidomide (the known imide pose recovered: ligand-interface iptm 0.99, protein↔ligand pair-iptm 0.78).
For all three NR4A paralogues the protein **fold** is confident (chain pTM 0.91–0.96) but the **ligand
placement** is not (protein↔ligand pair-iptm 0.23–0.32; ligand_iptm 0.77–0.87), and the cross-paralogue
ordering does **not** favour NR4A3 (if anything NR4A3 is lowest, though the three are within noise of each
other). Under the present inputs, **ligand-placement confidence was low for all three paralogues**, so these
calculations do not independently corroborate the modeled pose or receptor ordering; the low confidence
is neither surprising nor evidence against binding; but it means an orthogonal method **cannot independently
corroborate** the docked pose or the ABFE selectivity. The structural-model assumption (the AF2-derived,
metadynamics-opened pocket) therefore remains the **load-bearing uncertainty**, and this class of tool
cannot currently discharge it. The newly released apo 8XTT ensemble can now benchmark the apo pocket
geometry and handle map (the primary revision task, §4), but only a **ligand-bound** experimental
structure can validate the opened, warhead-engaged pose
([`../modalities/nr4a3-binary-cofold-result.json`](../modalities/nr4a3-binary-cofold-result.json)).
The **single-snapshot MM-GBSA "confirmed_selective"
verdict that originally nominated `denovo_15` failed a decoy control** (§2.6): it labels 39 % of non-NR4A
marketed drugs "NR4A3-selective," so a raw two-tier (docking + single-snapshot MM-GBSA) survival is **not**
selectivity evidence, and the earlier "MM-GBSA-confirmed selective" headline (and `denovo_15` as the lead) is
**retracted**. What survives is a single de-noised foothold: **`denovo_401`**, the one candidate whose margin
**survives multi-snapshot de-noising** (+12.83 ± 2.98, margin − SD = +9.85; §2.7) and **clears a same-tier
multi-snapshot decoy null in its design frame** (§2.7), and which is the subject of the completed three-replicate
selectivity FEP (§3). (The earlier decoy-calibrated single-snapshot foothold `denovo_111` — +15.7 vs the +13.1
95th-percentile bar; §2.6 — was subsequently **withdrawn**: its cationic form reverses selectivity, §2.7.)
It remains a **screening-grade, single-trajectory GB-implicit, unsynthesized, no-wet-lab** candidate —
supported by **initial conditional ABFE receptor contrasts** (NR4A2 λ-repair and the NR4A3 structural-model
sensitivity test still pending) but not experimentally validated. With no wet lab, the strongest honest claim is
**"computationally designed for an NR4A3-favoured profile and supported by initial ABFE receptor contrasts
conditional on selected opened conformers,"** not "selective." Matrix cells are gated by degradation *direction* and bounded by the AML
anti-target (SI §S4); and binding selectivity is still necessary-not-sufficient for *degradation* selectivity
(caveat 5).

## 5. Falsification (pre-registered)
Every gate has a fixed pass/fail set *before* the production numbers
([`../modalities/nr4a3-druggability-prereg.md`](../modalities/nr4a3-druggability-prereg.md)). Three
gate outcomes deviate from the literal pre-registration and are **disclosed, not silently swapped**, in
that file's deviation log: (i) the **Gate 0** metric (max → orthosteric/ligand-site, D\*=0.53 — a *real*
drug-bound bar, not a laxer one); and (ii) **Gate 1**, which asked for a free-energy *minimum or shoulder*
at an opened Rg "not just biased excursions" — F(Rg) is instead monotonic, so Gate 1 is reported as
**failed as pre-registered** (no separate opened basin) and **reformulated** into the *basin-breathing*
hypothesis the release run then tested; and (iii) **Gate 3 is split** into two subclaims that no single run
can jointly settle (a kinetic/thermodynamic distinction), reported separately below rather than as one
"Gate 3 passed." The pre-registered gates and outcomes:

| Gate | Pre-registered criterion | Outcome | Deviation | Current interpretation |
|---|---|---|---|---|
| 0 | druggability metric / bar | pass | metric → orthosteric/ligand-site, D\*=0.53 (a real drug-bound bar) | applies the stricter, ligand-site metric |
| 1 | a free-energy minimum/shoulder at an opened Rg | **fail** | reformulated to *basin-breathing* | no separate opened basin; F(Rg) monotonic |
| 2 | opened state geometrically druggable | **provisional** — initial pass under the original implementation | — | **final outcome pending the harmonized pocket-tracking re-analysis** (§3/§4): current fractions use a detected-pocket denominator + a permissive site match, so the pass is not treated as settled |
| 3A | persistence after bias removal | **supported** | *post hoc* split from Gate 3 | seeded open-like geometry holds 5 ns in 3/3 replicas |
| 3B | equilibrium energetic accessibility from the closed ensemble | **unresolved** | *post hoc* split from Gate 3 | independent F(Rg) profiles disagree substantially; the fixed-reference-Rg comparison spans ~16 kcal/mol but is **not** an equivalent-state free energy; enhanced-sampling convergence pending |
| 4 | a selective drug-like ligand meets the computational criteria | met **in silico**, not physical | absolute engagement not shown | provisional single candidate (below) |

We explicitly do **not** claim "Gates pass" as unqualified: Gate 1 **failed** as pre-registered, Gate 2 is
**provisional pending the tracking re-analysis**, Gate 3A is supported only in the narrow persistence sense
while **Gate 3B is unresolved**, and Gate 4 is an in-silico criterion, not physical binding. The 3A/3B split
and the three-replica / gate-descriptor diagnostics are **post-hoc analyses**, logged as such in the deviation
file and **not** folded silently into the original single-Rg gate definition. The route is
abandoned (weight shifting to ASO/immuno backups in the roadmap) if the opened conformations are not
geometrically druggable under the harmonized analysis, or no selective drug-like binder can be designed.

**Gate 4 (a selective, drug-like ligand can engage the opened pocket) — met in silico by a single de-noised,
initial-ABFE-supported foothold, not an unqualified pass.** `denovo_401` docks into the druggable release
pocket (4/5 handles), stays NR4A3-favoured through multi-snapshot MM-GBSA where the single-snapshot harvest
collapses, clears a same-tier decoy null in its design frame, is **supported by initial conditional
three-replicate ABFE** (§2.8), and passes the in-silico developability filters. Three honest limits keep
it short of an unqualified pass: the decoy null controls the *scoring* step only (not the generative step or
the best-of-~200 selection); the **positive margin persists in the metad-opened frame but the candidate does
not clear the corresponding metad-frame decoy null** (itself a poor discriminator); and the ABFE is a
*conditional receptor contrast*, not absolute engagement (the T4L
benchmark fails, §2.8). The gate verdict: **a predicted NR4A3-favoured profile in the
computational opened-state models — met under the preregistered criteria, but not a demonstration of physical
binding**, and not experimentally validated. (The earlier nominal pass on `denovo_15` is retracted and the
interim foothold `denovo_111` withdrawn on protonation grounds; both disclosed in the prereg deviation log.)

## References

Square-bracket tags record only methodologically load-bearing scope (primary vs review/secondary source;
the paralogue actually studied; associated PDB IDs) — not editorial commentary. Author lists, titles, and
volume/page fields are reproduced as verified against the primary record; where a source was originally
cited without a formal article title (conference/early-access or database entries), none is asserted here.

1. RCSB Protein Data Bank. *PDB 8XTT — NR4A3 (Nor1) ligand-binding domain, apo, solution NMR (20 of 100
   low-energy conformers deposited; 248-residue human construct).* Deposited 2024-01-11; released 2025-01-15.
   doi 10.2210/pdb8XTT/pdb. [Experimental structural entry; primary literature citation not yet published.]
2. Wang Z, et al. *Structure and function of Nurr1 identifies a class of ligand-independent nuclear
   receptors.* Nature 423:555–560 (2003). PubMed 12774125. [Nurr1/NR4A2; PDB 1OVL.]
3. de Vera IMS, et al. *Defining a Canonical Ligand-Binding Pocket in the Orphan Nuclear Receptor Nurr1.*
   Structure 27(1):66–77.e5 (2019). PubMed 30416039; doi 10.1016/j.str.2018.10.002. [Nurr1/NR4A2.]
4. Lanig H, et al. *In Silico Adoption of an Orphan Nuclear Receptor NR4A1.* PLoS ONE 10:e0135246 (2015).
   PMC4535767; doi 10.1371/journal.pone.0135246. [NR4A1/Nur77.]
5. Zaienne D, et al. *Druggability Evaluation of the Neuron Derived Orphan Receptor (NOR-1) Reveals Inverse
   NOR-1 Agonists.* ChemMedChem 17(16):e202200259 (2022). PMC9542104; doi 10.1002/cmdc.202200259.
   [Primary; experimental NR4A3/NOR-1 ligandability.]
6. Safe S, Oany AR, Tsui WN, Lee M, Srivastava V, Upadhyay S, et al. *Orphan nuclear receptor transcription
   factors as drug targets.* Transcription 16:224–260 (2025). PMID 40646688; PMC12263127;
   doi 10.1080/21541264.2025.2521766. [Review/secondary.]
7. Willems S, Morozov V, Marschner JA, Merk D. *Comparative Profiling and Chemogenomics Application of Chemical
   Tools for NR4A Nuclear Receptors.* J Med Chem 68:19955–19970 (2025). doi 10.1021/acs.jmedchem.5c00459.
8. Muñoz-Tello P, Lin H, Khan P, de Vera IMS, Kamenecka TM, Kojetin DJ. *Assessment of NR4A Ligands That
   Directly Bind and Modulate the Orphan Nuclear Receptor Nurr1.* J Med Chem 63(24):15639–15654 (2020).
   PMID 33289551; PMC8006468; doi 10.1021/acs.jmedchem.0c00894. [Nurr1/NR4A2.]
9. Stiller T, Merk D. *Exploring Fatty Acid Mimetics as NR4A Ligands.* J Med Chem 66(22):15362–15369 (2023).
   PMC10683012; doi 10.1021/acs.jmedchem.3c01467.
10. Rajan S, et al. *Prostaglandin A2 Interacts with Nurr1 and Ameliorates Behavioral Deficits in a
    Parkinson's Disease Fly Model.* NeuroMolecular Med (2022). PMID 35482177. [Nurr1; PDB 5YD6.]
11. López-García Ú, Vietor J, Marschner JA, Heering J, Morozov V, Wein T, Merk D. *Structural and mechanistic
    profiling of Nurr1 modulation by vidofludimus enables structure-guided ligand design.* Commun Chem 8:159
    (2025). PMC12095788; doi 10.1038/s42004-025-01553-8. [Nurr1.]
12. Wang L, Xiao Y, Luo Y, et al. *PROTAC-mediated NR4A1 degradation as a novel strategy for cancer
    immunotherapy.* J Exp Med 221(3):e20231519 (2024). PMID 38334978; PMC10857906;
    doi 10.1084/jem.20231519. [NR-V04; NR4A1-selective degrader precedent.]
13. Haller F, et al. *Enhancer hijacking activates oncogenic transcription factor NR4A3 in acinic cell
    carcinomas of the salivary glands.* Nat Commun 10:368 (2019). PMC6341107; doi 10.1038/s41467-018-08069-x.
14. Lee DY, et al. *Oncogenic Orphan Nuclear Receptor NR4A3 Interacts and Cooperates with MYB in Acinic Cell
    Carcinoma.* Cancers 12(9):2433 (2020). PMC7565926; doi 10.3390/cancers12092433.
15. Khan J, Ullah A, Goodbee M, Lee KT, Yasinzai AQK, Lewis JS Jr, Mesa H. *Acinic Cell Carcinoma in the 21st
    Century: A Population-Based Study from the SEER Database and Review of Recent Molecular Genetic Advances.*
    Cancers 15(13):3373 (2023). PMID 37444483; PMC10340722; doi 10.3390/cancers15133373.
16. Stacchiotti S, Baldi GG, Morosi C, Gronchi A, Maestro R. *Extraskeletal Myxoid Chondrosarcoma: State of
    the Art and Current Research on Biology and Clinical Management.* Cancers 12(9):2703 (2020). PMC7563993;
    doi 10.3390/cancers12092703.
17. Huang S-C, et al. *Extraskeletal Myxoid Chondrosarcomas: The Uncommon Clinicopathologic Manifestations
    and Significance of TAF15::NR4A3 Fusion.* Mod Pathol 36(7):100161 (2023). PMID 36948401.
18. Agaram NP, et al. *Extraskeletal Myxoid Chondrosarcoma with Non-EWSR1-NR4A3 Variant Fusions Correlate
    with Rhabdoid Phenotype and High-Grade Morphology.* Hum Pathol 45(5):1084–1091 (2014). PMID 24746215;
    PMC4015728. [EMC variant-fusion series; NR4A3 as the shared 3′ driver.]
19. Wei S, et al. *SMARCA2-NR4A3 is a novel fusion gene of extraskeletal myxoid chondrosarcoma identified by
    RNA next-generation sequencing.* Genes Chromosomes Cancer 60(10):709–712 (2021). PMID 34124809;
    doi 10.1002/gcc.22976.
20. Warmke LM, et al. *TAF15::NR4A3 gene fusion identifies a morphologically distinct subset of extraskeletal
    myxoid chondrosarcoma mimicking myoepithelial tumors.* Genes Chromosomes Cancer 62(10):581–588 (2023).
    doi 10.1002/gcc.23144. [Clusters with EMC by DNA-methylation profiling.]
21. Wilbur HC, et al. *Identification of Novel PGR-NR4A3 Fusion in Extraskeletal Myxoid Chondrosarcoma and
    Resultant Patient Benefit From Tamoxifen Therapy.* JCO Precis Oncol (2022). PMID 36103645; PMC9489176;
    doi 10.1200/PO.22.00039. [Patient benefit was via a partner-specific tamoxifen mechanism.]
22. Brenca M, et al. *NR4A3 fusion proteins trigger an axon guidance switch that marks the difference between
    EWSR1 and TAF15 translocated extraskeletal myxoid chondrosarcomas.* J Pathol 248:239–251 (2019).
    PMID 31020999; PMC6766969; doi 10.1002/path.5284.
23. Filion C, Motoi T, Olshen AB, Laé M, Emnett RJ, Gutmann DH, Perry A, Ladanyi M, Labelle Y. *The
    EWSR1/NR4A3 fusion protein of extraskeletal myxoid chondrosarcoma activates the PPARG nuclear receptor
    gene.* J Pathol 217(1):83–93 (2009). PMC4429309. [Validated direct fusion target.]
24. Chen J, et al. *NR4A transcription factors limit CAR T cell function in solid tumours.* Nature
    567:530–534 (2019). doi 10.1038/s41586-019-0985-x.
25. Mullican SE, et al. *Abrogation of nuclear receptors Nr4a3 and Nr4a1 leads to development of acute
    myeloid leukemia.* Nat Med 13:730–735 (2007). PubMed 17515897; doi 10.1038/nm1579.
26. Freire PR, Conneely OM. *NR4A1 and NR4A3 restrict HSC proliferation via reciprocal regulation of C/EBPα
    and inflammatory signaling.* Blood 131(10):1081–1093 (2018). PMID 29343483; PMC5863701.
    [Myeloid NR4A1/NR4A3 redundancy.]
27. Safe S, Karki K. *The Paradoxical Roles of Orphan Nuclear Receptor 4A (NR4A) in Cancer.* Mol Cancer Res
    19(2):180–191 (2021). PMC7864866; doi 10.1158/1541-7786.mcr-20-0707. [Review/secondary.]
28. Aldeghi M, Heifetz A, Bodkin MJ, Knapp S, Biggin PC. *Predictions of Ligand Selectivity from Absolute
    Binding Free Energy Calculations.* J Am Chem Soc 139(2):946–957 (2017). PMID 28009512; PMC5253712;
    doi 10.1021/jacs.6b11467. [ABFE across related bromodomains; precedent for the §3 per-receptor approach.]
29. Jumper J, Evans R, Pritzel A, et al. *Highly accurate protein structure prediction with AlphaFold.*
    Nature 596:583–589 (2021). doi 10.1038/s41586-021-03819-2.
30. Le Guilloux V, Schmidtke P, Tuffery P. *Fpocket: an open source platform for ligand pocket detection.*
    BMC Bioinformatics 10:168 (2009). doi 10.1186/1471-2105-10-168.
31. Eastman P, Swails J, Chodera JD, et al. *OpenMM 7: Rapid development of high-performance algorithms for
    molecular dynamics.* PLoS Comput Biol 13(7):e1005659 (2017). doi 10.1371/journal.pcbi.1005659.
32. Tribello GA, Bonomi M, Branduardi D, Camilloni C, Bussi G. *PLUMED 2: New feathers for an old bird.*
    Comput Phys Commun 185:604–613 (2014). doi 10.1016/j.cpc.2013.09.018. See also The PLUMED consortium,
    *Promoting transparency and reproducibility in enhanced molecular simulations.* Nat Methods 16:670–673
    (2019). doi 10.1038/s41592-019-0506-8.

Additional EMC-biology sources cited in §4 (data-derived numbers such as the DepMap Chronos gene-effect scores
are in the reproducibility archive, not the literature list):

33. *Structural basis of binding of homodimers of the nuclear receptor NR4A2 to selective Nur-responsive DNA
    elements.* J Biol Chem (2020). PMC6926456. [NR4A DNA-binding grammar; PDB 6L6Q/6L6L.]
34. *ETV6 dependency in Ewing sarcoma by antagonism of EWS-FLI1-mediated enhancer activation.* Nat Cell Biol
    25:298–308 (2023). PMID 36658219; PMC10101761; doi 10.1038/s41556-022-01060-1. [FET-fusion
    enhancer-reprogramming transfer prior.]
35. Zou T, Sethi R, Wang J, et al. *Whole genome sequencing for metastatic mutational burden in extraskeletal
    myxoid chondrosarcoma.* Front Mol Med (2023). PMC11285543; doi 10.3389/fmmed.2023.1152550. [EMC
    quiet-genome / clonal WGS.]
36. Tumor Biol 33:1599–1607 (2012). doi 10.1007/s13277-012-0415-2. [Further EMC-over-expressed fusion targets,
    e.g. NDRG2. Title to be completed at submission.]

**Structural controls (PDB).** PPARγ LBD + rosiglitazone (2PRG; Nolte et al., Nature 395:137, 1998);
ERα LBD + estradiol (1ERE; Brzozowski et al., Nature 389:753, 1997); NR4A holo references Nur77 4JGV
(THPN) and 6KZ5 (cytosporone B), Nurr1 5Y41 (PGA1).

**Methods, software, and benchmark references.**
37. Meller A, Ward M, Borowsky J, et al. *Predicting locations of cryptic pockets from single protein
    structures using the PocketMiner graph neural network.* Nat Commun 14:1177 (2023).
    doi 10.1038/s41467-023-36699-3.
38. Schneuing A, Harris C, Du Y, et al. *Structure-based drug design with equivariant diffusion models.*
    Nat Comput Sci (2024). PMC11659159; doi 10.1038/s43588-024-00737-x (arXiv 2210.13695).
39. Passaro S, Corso G, Wohlwend J, et al. *Boltz-2: Towards Accurate and Efficient Binding Affinity
    Prediction.* bioRxiv 2025.06.14.659707 (2025). PMC12262699; doi 10.1101/2025.06.14.659707. (Structure/
    affinity co-folding.)
40. Koes DR, Baumgartner MP, Camacho CJ. *Lessons learned in empirical scoring with smina from the CSAR 2011
    benchmarking exercise.* J Chem Inf Model 53(8):1893–1904 (2013). doi 10.1021/ci300604z. (Docking.)
41. Shirts MR, Chodera JD. *Statistically optimal analysis of samples from multiple equilibrium states.*
    J Chem Phys 129:124105 (2008). doi 10.1063/1.2978177. (MBAR.)
42. Boresch S, Tettinger F, Leitgeb M, Karplus M. *Absolute binding free energies: a quantitative approach for
    their calculation.* J Phys Chem B 107:9535–9551 (2003). doi 10.1021/jp0217839. (Boresch restraint + SSC.)
43. Jakalian A, Jack DB, Bayly CI. *Fast, efficient generation of high-quality atomic charges. AM1-BCC model:
    II. Parameterization and validation.* J Comput Chem 23(16):1623–1641 (2002). doi 10.1002/jcc.10128.
44. Wang J, Wolf RM, Caldwell JW, Kollman PA, Case DA. *Development and testing of a general amber force
    field.* J Comput Chem 25(9):1157–1174 (2004). doi 10.1002/jcc.20035. (GAFF/GAFF2.)
45. Jorgensen WL, Chandrasekhar J, Madura JD, Impey RW, Klein ML. *Comparison of simple potential functions
    for simulating liquid water.* J Chem Phys 79:926–935 (1983). doi 10.1063/1.445869. (TIP3P.)
46. Mobley DL, Guthrie JP. *FreeSolv: a database of experimental and calculated hydration free energies, with
    input files.* J Comput Aided Mol Des 28:711–720 (2014). doi 10.1007/s10822-014-9747-x.
47. Morton A, Matthews BW. *Specificity of ligand binding in a buried nonpolar cavity of T4 lysozyme: linkage
    of dynamics and structural plasticity.* Biochemistry 34(27):8576–8588 (1995). doi 10.1021/bi00027a007.
    (T4-lysozyme L99A + benzene benchmark; PDB 181L. Converged literature ABFE on this system, ≈ −5 to −6.5
    kcal/mol, from Deng Y, Roux B, *Calculation of standard binding free energies: aromatic molecules in the
    T4 lysozyme L99A mutant*, J Chem Theory Comput 2(5):1255–1273 (2006), doi 10.1021/ct060037v.)
48. Corsello SM, Bittker JA, Liu Z, et al. *The Drug Repurposing Hub: a next-generation drug library and
    information resource.* Nat Med 23:405–408 (2017). doi 10.1038/nm.4306. (Broad Drug Repurposing Hub.)
49. Mendez D, Gaulton A, Bento AP, et al. *ChEMBL: towards direct deposition of bioassay data.* Nucleic Acids
    Res 47(D1):D930–D940 (2019). doi 10.1093/nar/gky1075.
50. The UniProt Consortium. *UniProt: the universal protein knowledgebase in 2023.* Nucleic Acids Res
    51(D1):D523–D531 (2023). doi 10.1093/nar/gkac1052.
51. Cock PJA, Antao T, Chang JT, et al. *Biopython: freely available Python tools for computational molecular
    biology and bioinformatics.* Bioinformatics 25(11):1422–1423 (2009). doi 10.1093/bioinformatics/btp163.
    (BLOSUM62 alignment: Henikoff & Henikoff, PNAS 89:10915, 1992.)
52. RDKit: Open-source cheminformatics. https://www.rdkit.org (software; version recorded in the
    reproducibility archive).

## Data and software availability
All analysis code, input structures, generated molecules, docking/MM-GBSA/ABFE inputs and outputs, and the
pre-registration/gate files are in the project repository under `research/modalities/` and `results/`;
each computational result carries its generating script and, where applicable, its run identifier
(provenance ledger: `results/PROVENANCE.md`). Large trajectory artifacts are deposited to a permanent
archive (Zenodo DOI to be minted at submission). References were verified against the primary record
(Crossref, PubMed, Europe PMC): journal, year, volume/pages, and DOI/PMID/PMCID.

## AI-assisted research disclosure
This study was executed with substantial assistance from Anthropic **Claude** large-language-model coding
agents (Opus- and Sonnet-class Claude models, access period **~2026-05 to 2026-07**; the exact per-run model
identifiers, agent/tool environment, and access dates are recorded in the reproducibility archive alongside
each run). By task: **code authoring and refactoring** (analysis/simulation
pipelines), **orchestration** of the managed-cloud GPU/CPU jobs, **literature retrieval and cross-checking**,
and **manuscript drafting/revision**; the models also proposed analyses and interpretations, which were
adopted only after human review. **Validation evidence** (concrete, per ACS's note that extensive AI use may
be scrutinized): all quantitative results were produced by *executing* code on real inputs — never generated
by the language model; scientific-logic modules were covered by **unit and known-answer tests where feasible**
(e.g., the ABFE diagnostics **independently re-reduce the reported ΔG_bind from the raw reduced potentials**,
SI §S7; the statistical nulls carry known-answer tests) and model-generated code was reviewed before
execution; every citation was verified by a human against the primary record; and the scientific claims, their
weighting, and all go/no-go decisions remained human-controlled. Unit tests establish *software behaviour
against specified expectations*, not scientific validity; no numeric result, structure, or citation was
accepted from a language model without independent computation or source verification. (The exact test counts,
CI status, commit hash, and independent-recomputation scripts for load-bearing results are in the archive.)

**Figures.** All scientific figures were produced **programmatically** (matplotlib via
`nr4a3_journal_figures.py` and companion scripts) from the computed data — **no generative-AI image tools were
used** to create or edit any figure.

## Acknowledgments
The author used Anthropic **Claude** large-language-model coding agents (Opus- and Sonnet-class; access period
~2026-05 to 2026-07) for code authoring/refactoring, managed-cloud job orchestration, literature
retrieval/cross-checking, and manuscript drafting and revision, under human direction. The substantial-use
details and human-verification evidence are in the *AI-assisted research disclosure* above. No other assistance
and no external funding were received.
