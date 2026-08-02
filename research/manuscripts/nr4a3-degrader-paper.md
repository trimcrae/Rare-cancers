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
show **geometric persistence in 3/3 replicas** (harmonized pocket-tracking: the orthosteric pocket is detected
in every propagated frame of all three replicas and is druggable at ≥ D\*=0.53 in **56 %/40 %/80 %** of frames
per replica — **44/75 = 59 % pooled**), while the replicas do **not** yet agree on a **common quantitative
free-energy profile**. A falsification-heavy, pocket-conditioned generative campaign (chemical triage, an empirical decoy
null, multi-snapshot rescoring, independent-seed replication, and molecular-species resolution) leaves a
single candidate, **denovo_401**, whose NR4A3-favoured preference is probed by **initial three-replicate
absolute-binding free-energy calculations conditional on selected opened conformers** (favouring NR4A3 over
both paralogues in the AF2-opened states; a receptor-specific λ-overlap defect leaves the whole block
provisional, its repair is scoped but held, and the engine's *absolute* scale is not validated). A completed
**experiment-anchored (8XTT)
recalculation of the NR4A3 leg** shows the absolute ΔG_bind is **strongly conformer-dependent** (+8.17 ± 0.98
vs +3.5 kcal/mol on the AF2-opened conformer, a ≈ 4.7 kcal/mol shift larger than the selectivity margin), so
the selectivity is reported as **conditional on the chosen opened conformers**; a matched experiment-anchored
paralogue comparison is the flagged decisive follow-up. Separately, because a useful degradation window would
require an induced-interface margin larger than these methods can resolve, we report a **mechanism-first
prospective design stage** that searches instead for **categorical** paralogue differences — positions at
which NR4A1/NR4A2 are structurally incapable rather than merely disfavoured. It identifies an exposed
NR4A3-unique cysteine and three NR4A3-unique lysines whose paralogue side is a *sequence* fact independent of
any receptor model; finds that the chemistry axis is **one residue deep, with no geometric fallback**; returns
a **negative on E3-recruiter breadth** (structural stageability, not target availability, is the binding
constraint, and widening the panel confirmed the incumbent recruiters rather than displacing them); nominates
orientation basins that exploit the categorical terms in only a **small minority** of placements; and
enumerates a **reversible-covalent-preferring virtual linker library** whose covalent handle is reported as an
unresolved liability alongside the parent warhead's own pharmacology. Two ubiquitination-geometry parameters
are corrected against solved intact assemblies rather than assumed. **A preregistered known-answer test of the
ternary machinery itself — measured SPR cooperativity for a linker pyridine→benzene edge on SMARCA2/VHL —
returns the wrong sign in all three preregistered replicates (ΔΔG_coop = −0.599 kcal/mol at n = 3 vs a target
of +0.944), and does so with converged, structurally stable, forward/reverse-antisymmetric sampling and a
closed cycle, making the miss ~34× the statistical uncertainty and therefore systematic rather than a sampling
deficit that replicates could remove.** No cooperativity or
ternary-complex quantity in this work is therefore calibrated, and the degrader stage is reported as a
prioritized candidate matrix rather than a quantitative prediction. **A second preregistered known-answer test
— a sensitivity control asking whether the endpoint readout can detect paralogue selectivity that a primary
source reports, run on SMARCA2 vs SMARCA4 with the PRT3789 chemotype, a pair with solved structures on both
arms — returns a NULL on an adequately-powered design** (exact one-sided *p* = 0.7468; reference set of 462
arrangements with a floor of 0.00216 against α = 0.05; no technical failures; the observed separation runs
opposite to the predicted direction but is not significant in either, mirrored *p* = 0.2554). **Every
paralogue-selectivity statement in this work is therefore an unvalidated prediction**: all three attempts to
establish a positive control for selectivity detection — the cooperativity calibrator above, a preregistered
retrospective holdout that returned a non-resolution and is in any case covalency-confounded, and this
control — have now been run and none succeeded. ⛔ A null of this kind **does not distinguish an insensitive
readout from a genuinely narrow structural signal** and is not reported as though it did. The **causal test of whether any designed
element creates discrimination has not been run**, and its reading is pre-registered. This is a
**computation-only** design and feasibility
study — **no molecule was synthesized and no wet-lab validation was performed** — whose principal unresolved
limitations are the consistency of pocket identification across structural models, the **structural-provenance
dependence of the free-energy selectivity**, cross-replica convergence, the atomic binding pose and
ensemble-weighted selectivity, and — for the prospective stage — a double conditionality on a hypothesized
warhead pose and a chosen receptor frame.

## 1. Background and rationale
NR4A receptors are constitutively active orphan nuclear receptors whose canonical ligand pocket is
collapsed/occluded in crystal structures (Nurr1, PDB 1OVL; Wang 2003), the structural basis of their
"undruggable" reputation. That reputation is a statement about *static* structures: Nurr1's pocket is in
fact **dynamic and expands** from the collapsed crystal conformation to bind fatty acids (de Vera 2019),
an MD study reported a cryptic druggable pocket in Nur77 (Lanig 2015), and validated NR4A ligands engage
cryptic/surface sites. **NR4A3 itself is experimentally ligandable — pharmacologically, though not yet
structurally.** A fragment screen against NOR-1/NR4A3 (hit rate <1 %) returned three ligand chemotypes, one
elaborated to a **low-micromolar inverse agonist** (compound 19) that shifted NOR-1-regulated gene expression
in cells, de-repressing the NR4A3 target gene *MYC* (IC₅₀ ≈ 8–47 µM; Zaienne 2022, a paper titled, aptly, a
*"Druggability Evaluation of NOR-1"*; the same compounds are recapitulated in the Safe 2025 review). We note
explicitly that these compounds were characterized **on NR4A3/NOR-1 only** — no NR4A1/NR4A2 counter-screen was
reported — so they establish NR4A3 *engagement*, **not** paralogue selectivity. These experimental results
establish that NR4A3 *can* be engaged by small molecules, but
leave the binding site structurally undefined: NR4A3's LBD has an experimental structure only as a
recently released **apo solution-NMR ensemble (PDB 8XTT, 2025)** — **no ligand-bound structure and no
published pocket-dynamics analysis** exist — the structural gap this paper addresses (our in-silico
druggable pocket supplies a candidate *mechanism* for the ligandability their pharmacology already
demonstrates). Crucially, 8XTT also **corroborates** that premise rather than pre-empting our work: an
experimental, ligand-free NR4A3 ensemble already contains cavity-bearing conformers at the mapped orthosteric
site (§2.1), so the druggable pocket we design into is supported by experiment *independent of our AF2/MD
machinery* — the deposited structure **de-risks the feasibility premise**. It does not, however, supply the
opened pose, the equilibrium population, or the paralogue-selectivity energetics, which are this paper's
actual contribution; pocket *existence* is the shared premise (family-wide: Nurr1 de Vera 2019, Nur77 Lanig
2015; and now NR4A3), not a claim we originate. *This work's structural foundation is the AF2 model, which predates 8XTT; we benchmark the AF2 pocket
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

**Clinical precedent for the degrader modality.** Targeted protein degradation is no longer speculative in
oncology — it is both an approved therapeutic strategy and, as of 2026, an approved *PROTAC* strategy, so a
degrader rationale rests on precedent rather than on hope. Two strands apply. First, *molecular-glue* degraders
that redirect the CRL4^CRBN E3 ligase — the immunomodulatory imide drugs (IMiDs) thalidomide, lenalidomide and
pomalidomide, whose mechanism is CRBN-dependent degradation of the IKZF1/IKZF3 transcription factors and, in
del(5q) myelodysplastic syndrome, of CK1α (Krönke 2014, 2015; Lu 2014; Gandhi 2014) — have been standard-of-care
for multiple myeloma, del(5q) MDS and mantle-cell lymphoma since 2005–2006. Molecular glues are monovalent and
mechanistically distinct from the bivalent PROTAC architecture invoked here, but they establish that eliminating
an oncoprotein through the ubiquitin–proteasome system is a safe, durable and approvable strategy. Second, and
more directly, the heterobifunctional PROTAC class reached its first regulatory approval in May 2026:
vepdegestrant (ARV-471), an oral cereblon-recruiting **estrogen-receptor** degrader, was approved by the FDA for
ESR1-mutated ER+/HER2− advanced breast cancer (FDA 2026), on the strength of the phase-3 VERITAC-2 trial in which
— in the ESR1-mutant population — median progression-free survival was 5.0 vs 2.1 months versus fulvestrant
(HR 0.57; objective response 19% vs 4%; Hurvitz 2025). The benefit was confined to the ESR1-mutant subgroup and
was not significant in the intention-to-treat population, with the label restricted accordingly — a reminder that
degrader efficacy, like any modality's, is context-dependent and not guaranteed by target removal alone. Several
other oncology PROTACs show substantial single-agent activity short of approval: the BTK degraders BGB-16673 and
bexobrutideg (NX-5948) reached objective response rates of ~78–94% and ~80% in relapsed/refractory CLL/SLL
(ASH 2024–2025), and the androgen-receptor degraders bavdegalutamide (ARV-110) and luxdegalutamide (ARV-766)
produced PSA50 responses of ~46–50% in biomarker-selected metastatic castration-resistant prostate cancer.

This precedent is unusually close to the present target. The two most clinically advanced PROTACs both degrade
**nuclear receptors** — the estrogen and androgen receptors, the same superfamily as NR4A3 — and nuclear
receptors have proven a favourable degrader class precisely because their ligand-binding domain offers a defined
pocket with decades of prior medicinal chemistry, and because removing the receptor circumvents resistance that
defeats competitive antagonists (ESR1 activating mutations; AR amplification, LBD mutations and splice variants).
An NR4A3 degrader therefore sits within the validated PROTAC target class and shares the receptor superfamily of
the first-approved and most-advanced agents. What has **not** been attempted is any degrader against NR4A3 or
against EMC: the only reported NR4A-family degrader remains the preclinical NR4A1-selective PROTAC NR-V04
(Wang 2024), and degrader campaigns in fusion-driven sarcomas (e.g. BRD9 degraders in synovial sarcoma) have
reached only early-phase trials and target partner proteins rather than the fusion driver itself. We accordingly
frame this work as a first-in-concept computational design resting on strong *class* precedent rather than direct
precedent — a distinction maintained throughout, and one that NR4A3's atypical, largely collapsed orphan-receptor
pocket (§2.1, §2.3) makes especially important not to overstate: strong precedent for the *modality* is not
precedent for the *pocket*.

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
conformers are strongly occluded (median druggability 0.012), while a few conformers were assigned
orthosteric-site fpocket scores above the empirical reference boundary D\*=0.53. The original implementation
obtained an orthosteric-site score for **all 20** conformers (range 0.000–0.925) and placed **4/20** above
D\*. The **harmonized rerun** (pinned fpocket build + score-independent matcher;
[`../modalities/nr4a3-pocket-reharmonize-summary.json`](../modalities/nr4a3-pocket-reharmonize-summary.json))
now reports both denominators explicitly: the orthosteric pocket is **matched in 19/20** conformers, of which
**3** score ≥ D\* — i.e. **3/19 (16 %) among detected pockets and 3/20 (15 %) across all deposited
conformers** (one fewer than the original 4/20, as expected from the pinned build and the stricter
score-independent matcher). Because these are
low-energy structural models rather than equilibrium samples, **3/20 is a structural-heterogeneity
observation, not an estimate of a 15 % open-state population** (and both the experimental median and the static
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
is conserved to sub-Ångström in both, with AF2 at the high end of but inside the ensemble's internal range.**
**AF-vs-experiment fold fidelity, matched across all three paralogues (closes the "benchmarked for NR4A3
only" gap).** NR4A1 and NR4A2 also have experimental LBD structures, so we ran the identical AF↔experiment
Cα-RMSD (`nr4a_af_crystal_rmsd.py`; BLOSUM62 residue maps): the AlphaFold models reproduce the experimental
folds tightly — **NR4A1 AF vs Nur77 crystal 3V3E global 1.20 Å / Pocket-5-local 0.44 Å; NR4A2 AF vs Nurr1
crystal 1OVL global 1.40 Å / 0.82 Å** (all-atom alignment identity 1.0 to the same-protein crystal, 0.54/0.64
across paralogues). *This is an AF-vs-**collapsed apo crystal** fold check, not a pocket-state validation:* the
small global RMSD confirms AF is a faithful backbone model for each paralogue (so the AF-based design and the
paralogue selectivity references rest on a sound fold), while the sub-Ångström pocket-local number reflects
that the crystal orthosteric site is occluded, not that AF captures an open state. Notably NR4A3 is the outlier
— its AF↔experiment divergence (global 7.63 Å, pocket 3.56 Å vs a *flexible NMR ensemble*) is far larger than
the paralogues' (vs *single collapsed crystals*), consistent with 8XTT sampling a genuinely dynamic,
cavity-bearing ensemble rather than one static conformer. **Two post hoc robustness *transfers* to
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

**An orthogonal, learned generative ensemble (BioEmu) independently recovers the cryptic site and gives an
unbiased minority-open population.** Because the metadynamics is a *biased* enhanced-sampling readout and the
8XTT transfers use *prespecified* conformers, we added the one thing missing above — an **unbiased ensemble
test** from a method orthogonal to our MD. BioEmu (Lewis et al., *Science* 2025; v1.4.1), a diffusion emulator
of protein equilibrium ensembles, generated an ensemble of the apo LBD **from sequence alone** (no MD, no
metadynamics, no opened input structure), which we scored through the **identical** harmonized Pocket-5 detector
(fpocket 4.0, score-independent lining-set match, D\*=0.53; [`../modalities/nr4a3-bioemu-crosscheck-findings.md`](../modalities/nr4a3-bioemu-crosscheck-findings.md)).
Over 56 frames it **detects Pocket-5 in 68 %** and opens it to a druggable state (≥ D\*) in **12.5 % (7/56)** —
**far below the biased metadynamics (0.68) and unbiased-release (0.587) fractions, but closely matching the
experimental 8XTT NMR ensemble (0.15)**. Two readings follow, both stated straight: (i) an independent,
learned method that never saw NR4A3 MD **re-finds and opens the same cryptic site**, corroborating its existence
and openability on a *new* evidence axis; and (ii) the concordance of **two unbiased sources (BioEmu 0.125, NMR
0.15)** on a *minority*-open population, against the biased metadynamics majority (0.68), indicates the
enhanced-sampling fractions likely **over-represent** the open state — the honest open-state population is more
plausibly a low-teens-percent minority. *Integrity limits:* apo cryptic-pocket recovery is BioEmu's weakest
regime (~50 % in `bioemu-benchmarks`) and it is not calibrated on the absolute probability of rare pocket
opening (JCTC 2026, 10.1021/acs.jctc.6c00135), so this is a **qualitative cross-check, not a population
estimate**, and a druggability *claim* still rests on the fpocket/energetics gate — BioEmu does not, alone, show
the pocket binds anything.

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
2020) confirms amodiaquine, chloroquine and cytosporone B directly bind the **Nurr1/NR4A2** LBD while
**celastrol, C-DIM12 and TMPA do not**. ⚠ **Corrected 2026-07-25 — an earlier version of this sentence read
"the NR4A LBD", which over-generalises a single-paralogue result and inverted its meaning for celastrol.**
That study assayed **NR4A2 only** (its title names Nurr1; our own bibliography annotates it *[Nurr1/NR4A2]*).
Celastrol's proposed mechanism is **covalent engagement at NR4A1 Cys551** (Zhang et al. 2018 [64]) — and, on
the primary record, that bond is **reversible**: the source's title is *"Celastrol binds to its target protein
via specific noncovalent interactions and reversible covalent bonds."* ⚠ **Corrected 2026-07-25: an earlier
version of this sentence read "covalent capture", and this paper elsewhere refers to celastrol simply as
"covalent".** Neither is wrong about the bond forming, but both understate the mechanism, and the distinction
is load-bearing rather than pedantic — a reversible-covalent binder has a residence time and retains catalytic
turnover in a degrader architecture, which is precisely the property §2.10's linker library selects for on
independent design grounds. Read "covalent" throughout this paper as *reversible*-covalent wherever it refers
to celastrol. **NR4A2 carries Tyr at
the aligned position** — established independently here in the covalent panel's Leg 0, which also puts Thr579
in NR4A3. **A celastrol negative on NR4A2 is therefore exactly what the Cys551 mechanism predicts: the two
studies corroborate rather than conflict, and together they STRENGTHEN the covalent confound** rather than
weakening celastrol's direct-binding evidence. So cytosporone B carries independent direct-binding support on
NR4A2, and celastrol's NR4A1 engagement is **neither supported nor refuted** by Muñoz-Tello — it was not
tested there. We no longer down-weight celastrol on this basis. And a
family-wide chemical-probe audit (Willems/Merk 2025) validates a small vetted NR4A tool set while showing many
putative NR4A ligands lack on-target engagement — a caution we apply to every repurposed chemotype.
Fragment-to-lead campaigns reaching sub-µM NR4A ligands with NOR-1/NR4A3 tested (Stiller & Merk 2023; Zaienne
2022) keep the *ligandable-not-undruggable* premise on experimental footing. *(iii) Paralog-selective NR4A
degradation is achievable.* The NR-V04 PROTAC (Wang 2024) selectively degrades NR4A1 while **sparing
NR4A2/NR4A3** — proof-of-concept that intra-family degradation selectivity is attainable (the exact inverse of
our NR4A3-selective goal), though its sparing mechanism is unresolved and its celastrol warhead is a
promiscuous covalent binder, not a selective one.

### 2.3 Metadynamics drives the orthosteric pocket to breathe into a druggable state (60 ns cumulative production)
Well-tempered metadynamics on the radius of gyration of the Pocket-5 lining Cα atoms (method:
[`../modalities/metad-methods-appendix.md`](../modalities/metad-methods-appendix.md)) drives the pocket
open (CV Rg ~0.5 → ~1.05 nm). On the committed 60 ns cumulative trajectory (1200 frames at 0.05 ns/frame;
artifact `results/nr4a3-pocket-reharmonize/metad/pocket_analysis_summary.json`, pinned fpocket 4.0),
per-frame fpocket on the **orthosteric Pocket-5 cavity** (the *same* metric as the static 0.495 and D\*, not
the non-discriminating "max-anywhere" cavity of §2.2) reaches druggability **0.931** (max over the 25
fpocket-sampled frames; mean 0.582; `crosses_0.5 = True`; ≥ D\*=0.53 in 0.68 of sampled frames); SASA of the
lining residues rises by up to **+6.1 nm²**, with **70.8 % of the 1200 frames more open than the equilibrated
production-frame-0 baseline**. (A 5 ns validation gave a consistent 0.751.)
*Correction of record: earlier drafts quoted "86.8 % of frames more open" and attributed the fpocket numbers
to a 30 ns / 600-frame run. **No committed artifact anywhere in this repository reports 86.8 %**; every
committed version of the metadynamics pocket summary (git `80e9cec0`, `08deeac5`, `800cf76d`) is the
1200-frame/60 ns analysis reporting 0.708. The 86.8 % figure is therefore
**unsupported by any committed artifact** and has been replaced by the committed 70.8 %; the 0.931 and
+6.1 nm² values are unchanged because they come from that same committed 60 ns artifact.*
This pocket-dynamics analysis of NR4A3 parallels the *dynamic, breathing*
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
(druggable frames + handles pocket-facing, below); **the harmonized pocket-tracking re-analysis has since been
run and committed** and the frame-fraction clause passes more strongly under it (0.56/0.40/0.80 vs the earlier
0.20/0.16/0.28), while the **handles-pocket-facing clause was not re-run under the harmonized tracker** and is
therefore still reported at its pre-harmonized weight. **Gate 1 (a genuine two-state cryptic *opening*) FAILED as pre-registered.** Gate 1
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
fpocket druggability figures in §2.3 are already computed on the 60 ns frame set, so no extension is
outstanding; what remains sampled rather than exhaustive is the fpocket *frame subsample* — 25 of the 1200
frames — which is a resolution limit on the frame-fraction, not a trajectory-length gap.) The **release run**
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
replica; *provenance note:* these two persistence numbers are recorded in the committed run ledger
[`../modalities/nr4a3-degrader-next-steps.md`](../modalities/nr4a3-degrader-next-steps.md) for triplicate run
28343901058, but the underlying per-replica Rg summary is an **S3-only object, not committed to this
repository** — they are reproducible from the deposited trajectories, not checkable against a repo artifact).
Running fpocket on the bias-free release trajectories under the **harmonized, score-independent Pocket-5
tracker** (fixed lining set, composite Jaccard/recovery + centroid gate, pinned fpocket 4.0; committed
artifact [`../modalities/nr4a3-pocket-reharmonize-summary.json`](../modalities/nr4a3-pocket-reharmonize-summary.json)),
the orthosteric Pocket-5 is **detected in 75/75 propagated frames (detection fraction 1.00 in every replica)**
and is druggable at ≥ D\*=0.53 in **56 % / 40 % / 80 %** of frames (rep0/rep1/rep2) — **44/75 = 59 % pooled**
— at CV Rg ≈ 0.737, clearing the pre-registered "≥5 % of frames ≥ D\*" bar. Because the
propagation carried no bias, **the geometry is maintained without ongoing metadynamics bias** (its *initial*
conformation was, however, selected from biased sampling, so this is not an equilibrium-provenance statement).
*(Two scope notes so the two numbers are not over-read as one. (i) The **3/3 persistence** is an
**Rg-persistence** result across the triplicate; the druggability frame-fraction was originally quoted on the
single `release_rep0` trajectory but has now been **scored on all three release replicas**: under the
harmonized tracker the fraction of frames ≥ D\*(0.53) is **0.56 / 0.40 / 0.80** (rep0/rep1/rep2; 14/25, 10/25,
20/25), pooled **44/75 = 0.59**, so **all three independent bias-free trajectories cross into the druggable
band**. *Superseded numbers, stated so the change is auditable:* earlier drafts reported **0.20 / 0.16 / 0.28**
from the pre-harmonized tracker (`nr4a3_mdpocket.py`, per-replica max 0.84 / 0.89 / 0.88; mean 0.26 / 0.22 /
0.22, artifacts `results/nr4a3-release-pocket-rep1|rep2/pocket_analysis_summary.json`). **The difference is
*not* a denominator difference** — we checked: under *both* trackers the pocket is detected in 25/25 frames of
every replica, so the detected-frame and all-frame denominators are identical (1.00) either way. The change is
entirely one of **site assignment**: the old tracker scored the highest-druggability cavity that overlapped the
target residues at all (an outcome-selected, permissive match), whereas the harmonized tracker matches the
**fixed Pocket-5 lining set** score-independently, and that reassignment — not any change of denominator —
moves the fractions. These remain **descriptive frame fractions on correlated,
non-equilibrium frames**, not equilibrium populations; an autocorrelation-aware descriptive interval
(integrated autocorrelation time → effective sample size → block bootstrap) is given in the SI.
(ii) **5 ns is a short persistence window**: no prompt sub-nanosecond collapse of the seeded conformation was observed in these three trajectories,
but a geometry can hold on 5 ns and still relax on tens–hundreds of ns, so "persists" here means "does not
promptly collapse," not "a verified long-lived sub-state.")* This is **not** a
demonstrated always-open pocket but a **dynamic cavity** whose seeded open-like geometry does not
promptly collapse once the bias is removed and is fpocket-druggable in a fraction of frames **across all three
release replicas** (≥ D\* in 0.56 / 0.40 / 0.80 of frames; below). **These are correlated, open-seeded,
non-equilibrium frame fractions — NOT equilibrium population estimates.** Because the pocket is detected in
every propagated frame, the detected-frame and all-frame denominators coincide (1.00), so the fractions are
not denominator-inflated; the **harmonized re-analysis is done and is what is quoted here**
(`nr4a3-pocket-reharmonize-summary.json`), and the residual limitation is the non-equilibrium provenance of
the frames, not the pocket-matching rule. 5 ns cannot establish the equilibrium probability of
the conformation or a spontaneous opening rate. So
**Gate 3A is supported** (the seeded druggable geometry does not promptly relax once the bias is removed)
while **Gate 3B — equilibrium energetic accessibility from the closed ensemble — remains unresolved** (the
only estimate is the convergence-limited biased F(Rg)); a warhead would need to select-and-stabilise these
transiently-druggable conformations rather than occupy a static pocket. Establishing an actual populated
fraction would require reweighted enhanced sampling or many independent unbiased trajectories with
equilibrium weighting (a revision task, §4). All downstream design (below) is therefore anchored to a
**druggable release-derived frame** (Rg ≈ 0.737, fpocket ≥ 0.5; `nr4a3_release_druggable.py`), not the
biased-metad frame. *(Registered Gate-2 sub-check — computed under the **pre-harmonized** tracker and **not** re-run under the
harmonized one, so it is reported but not treated as confirmed, since the set of druggable frames it is
computed over is the superseded one. The handle-facing analysis
(`../modalities/nr4a3_handle_facing.py`, run 2026-06-26 on the metadynamics trajectory) shows the opened,
druggable frames keep the selectivity handles pocket-facing: across the druggable frames (fpocket ≥
D\*=0.53) a mean of **5.0/7** handles point into the cavity and **87.5 %** keep ≥4 facing. Five are
reliably pocket-facing — **L406, T410, I484, I531, L534** (≥0.875 of druggable frames) — while **T407
and R412 mostly splay outward** (facing in 0.0 and 0.25 of druggable frames), so the demonstrated
candidate pocket-facing handle set is those five, not all seven (geometric orientation, not a ligand-engagement result).
**Artifact status:** these fractions are recorded in the committed run ledger
[`../modalities/nr4a3-degrader-next-steps.md`](../modalities/nr4a3-degrader-next-steps.md) ("STEP 0", run
28249776934), but the primary output `handle_facing_summary.json` is an **S3-only object that is not committed
to this repository**, so the numbers are traceable to a run record rather than to a checked-in artifact; they
are quoted here at that weight. This is also the precondition for the warhead
screen's handle-contact scoring (§2.5). The open-seeded "release" run is the orthogonal Gate-3A test (does
the seeded open-like geometry persist, or promptly collapse once the bias is removed?); the seeded geometry
persists across 3/3 short replicas and is fpocket-druggable in a fraction of frames of **each of the three
release replicas** (≥ D\* in 0.56/0.40/0.80, harmonized tracker), so the **short-timescale
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
1.76 Å Cα-RMSD**. (*Artifact status:* the helix-retention and 1.76 Å core-RMSD values are recorded in the
committed run ledger [`../modalities/FEP-STATUS.md`](../modalities/FEP-STATUS.md) for run 28655050752; the
script's JSON verdict is **not committed to this repository**, so they are traceable to a run record rather
than a checked-in artifact. A companion "1.78 Å including the pocket mouth" figure appeared in earlier drafts
and has **no committed source anywhere in this repository** — it is removed here rather than restated, and the
pocket-mouth-inclusive RMSD should be recomputed and deposited before submission.)
So the fold is intact and the elongation is a **floppy,
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

**Prior art and honest novelty positioning.** All-atom alchemical *ternary-cooperativity* free-energy
calculation — the same ΔΔG_coop = ternary − binary thermodynamic cycle, including VHL–BRD4/MZ1 applications
and paralogue-selectivity applications — is an **active, already-published area** [60–63]. Nothing in the
ternary work reported here is a landmark methodological first: what is offered is an **open-source
OpenFE-based implementation applied honestly to the NR4A family**, i.e. an *incremental* methods contribution
plus a new biological application, and any future ternary-cooperativity result from this program must be
**benchmarked against that prior art** rather than presented as a new capability. We state this explicitly
because the alternative framing — presenting an established cycle as novel — would be an overclaim.

**A family-matched retrospective case study gives thin concordance but fails an affinity-sensitive control.**
We applied the co-folding workflow to an **NR-V04-inspired representative reconstruction** (an
NR-V04-inspired 79-heavy-atom celastrol–PEG–VHL construct; the exact recruiter connectivity/regiochemistry,
stereochemistry, attachment points, and linker atom count from the primary source are **not yet independently
verified**, so this is not an exact retrospective benchmark against the reported NR-V04 phenotype). NR-V04 is
reported to degrade NR4A1 while sparing NR4A2/NR4A3. In a **historical (now retired) analysis**, a gross
dual-contact classifier whose ligand halves were assigned by a conformation-dependent **sulfur-anchor
partition** was concordant with the reported phenotype across three seeds — satisfied for NR4A1 in **2/3
seeds** but 0/3 for NR4A2/NR4A3, with mean ligand-iPTM *not* reproducing the ordering (higher for spared
NR4A2). That sulfur-anchor assignment has since been **replaced**: the pending corrected rerun assigns the
warhead/recruiter/linker by an **atom-mapped SMILES↔structure moiety mapping** (fail-closed when the mapping
cannot be established), and reports **correct-half dual-surface proximity** (a half touches the *right*
protein) **separately** from **canonical VHL hydroxyproline-pocket occupancy** (the recruiter half within the
Ser111/His115 sub-pocket, not any VHL surface). The rerun's descriptive result on the corrected classifier is
pending. **However, an
expected VHL-inactive stereoisomer (the 4-hydroxyproline epimer construct) achieved the same aggregate bridge
fraction as the active construct (0.75 vs 0.75 over the seed×pose pool), showing that this structure-only
classifier has no demonstrated affinity sensitivity.** A structure generator can place an inactive
stereoisomer in a plausible pocket geometry while not modelling its unfavourable binding thermodynamics; this
structure-only invocation and contact classifier did not assess affinity (Boltz-2's optional affinity head was
not used and is not recommended for ligands substantially larger than 56 atoms, whereas this construct has 79
heavy atoms). The classifier **may therefore support architecture-feasibility screening, but not binding,
ternary-stability, degradation-selectivity, or linker-ranking claims** — this failed affinity control is
decisive for the frozen go/no-go gate (`negative_controls_pass = false`), which prohibits geometry-only
affinity or linker ranking. Further limitations: only three seeds × one top model were analyzed here (thin;
poses within a seed are nested, so pooled counts overstate independence); the free-celastrol control detects
one gross architectural failure (no recruiter) but one control does not establish specificity; celastrol's
covalent engagement of NR4A1 Cys551 was **not evaluated here** — the residue-offset lookup has since been
confirmed against output structures, and confirming it is what revealed that the co-folding never seats
celastrol anywhere near Cys551 (banner below), so the covalent arm of this comparison was never instantiated
rather than merely unmeasured; the Cullin–RING/E2~Ub machinery was absent; and the phenotype does not establish that
selectivity is *caused* by ternary geometry. Under the same gross classifier the representative
`denovo_401`–CRBN linker contacted both proteins for all three paralogues, showing **no modelled paralogue
discrimination**. This is a **structure-only gross architecture classifier that showed thin retrospective
concordance and failed an affinity-sensitive stereochemical control; it is unsuitable for prospective affinity
or degradation-selectivity ranking.** Full spec, controls, and the seed-level analysis:
`nrv04-ternary-benchmark.json` / `report_nrv04.py`; **SI §S2**. *(Reflects three external methods reviews,
2026-07-11: the metric is "correct-half dual-surface proximity" (not "productive geometry"); the analyzer fixes
— atom-mapped moiety occupancy, intended-site checks, verified/annotated Cys551 mapping, seed-level (not
pose-pooled) statistics with strict-majority seed calls, separated architecture-vs-affinity controls, and a
paired active-vs-epimer comparison — are **committed**; the corrected descriptive rerun is authorized as a
seed-level architecture characterization only, pending a real-CIF forced-restart smoke, and confers **no**
prospective affinity or degradation-selectivity ranking authority.)*

> ## ⚠ THE FOLLOWING SUBSECTION IS UNDER CORRECTION — DO NOT CITE ITS NUMBERS (2026-07-24)
>
> Every quantitative claim in the covalent-panel paragraph below was computed against the **wrong protein
> interface** and must not be quoted, reproduced in a figure, or relied on, pending a corrected re-run.
>
> **What happened.** The endpoint-MD driver split "E3" from "degradation target" *positionally* — it took the
> last protein chain in sorted order as the target — while the co-fold builder writes the target **first**
> (`proteins = [("A", NR4A-LBD)] + e3`). With chains A = 254 aa (NR4A LBD), E = 213 (VHL), F = 118 (Elongin B),
> G = 112 (Elongin C), the rule selected **Elongin C** as the degradation target. So the interface-RMSD
> stability endpoint (R1) and the contact endpoint (R2) describe the **Elongin C↔rest** interface rather than
> the VHL↔NR4A1 one, and the Lys-presentation endpoint (R3) counted **Elongin C's** lysines instead of the
> target's.
>
> **How we know.** The same driver resolves the celastrol-reactive cysteine independently, *by geometry*, and
> records its chain in every leg. That cysteine is on the NR4A1 LBD, and it is recorded on chain **A** in 12 of
> the 14 landed legs — while the positional rule was pointing at chain **G**, in the same runs. The reported
> arithmetic reproduces exactly from the landed plateaus; it is the interface being measured that is wrong.
>
> **Consequently:** the active-vs-epimer separation, the covalent-vs-non-covalent comparison, the C551A
> contrast, and this subsection's contribution to any GO decision are all **withdrawn pending re-run**. The
> specific per-arm figures are **retracted and must not be quoted**: recruiter_active stable in 3/3 seeds vs
> recruiter_epimer 1/3; cov_nr4a1 2/3 equal to noncov_nr4a1 2/3; cov_c551a 1/3. They are listed here only so
> that a reader who has seen them elsewhere can identify them as withdrawn.
>
> **What is unaffected**, and is all the paragraph below now claims: the panel's *design and execution* (arms,
> protocol, 17/18 legs landed, no blow-ups), the *infrastructure and cost* record, and — in direction only — the
> observation that **contact-based recruitment is a weak discriminator**, since every arm scored as "recruited"
> regardless of which chain pair was measured. Even that should be re-derived from the corrected run rather than
> cited from here.
>
> The chain split is now identified and validated rather than inferred from ordering, and every leg records the
> split it used. Evidence and fixes:
> [`../modalities/nrv04-cofold-chain-forensics-2026-07-24.md`](../modalities/nrv04-cofold-chain-forensics-2026-07-24.md).
>
> ## ⚠⚠ UPDATED 2026-07-25 — THE SITUATION IS WORSE THAN "UNDER CORRECTION", AND THE RE-RUN IS **HELD**
>
> A $0 attempt to recompute the correct interface from the committed output established four further things.
> The banner above stands; these change what the subsection can ever claim.
>
> 1. **The result is not recoverable, at any price short of re-running the MD.** A read-only object census of
>    the panel's output found **72 objects, 19 units, and zero trajectory files**. Everything persisted is
>    either a *single* frame (the solvated topology carries pre-minimisation coordinates), forces/parameters
>    with no coordinates over time, or scalars **already reduced against the wrong split**. The driver reduces
>    each frame in-loop and discards positions, and it deletes its one checkpoint frame on clean completion.
> 2. **The GO was never produced by the frozen scoring rule.** Running the preregistration's own frozen verdict
>    function on the panel's own committed legs returns **NO-GO** — *both* negative controls scored positive.
>    The chain split changed which interface the numbers described; it did **not** manufacture a GO that the
>    frozen rule would otherwise have granted.
> 3. **The panel's inputs were contaminated as well** — an independent, third data-invalidating defect. The
>    simulated assemblies contain **14-3-3 epsilon where Elongin B belongs**, identified by CA-geometry
>    superposition to a specific superseded co-fold set at **RMSD 0.000 Å** (the clean set is 5.9 Å away). An
>    earlier audit that cleared the panel on this point is **retracted**: it checked the input prefix the code
>    *names*, not the artifact that *ran*.
> 4. **The lysine-presentation endpoint (R3) was reported in nanometres under an Ångström label.** Simulation
>    positions are in nm; the interface endpoint converted, R3 did not. Every committed R3 is therefore **~10×
>    too small** — reading as ubiquitination-compatible at 2–4 Å when the true separations are **~30–49 Å**.
>    Cross-checked independently against a t = 0 distance of 25.2 Å on a leg reporting 2.34 Å.
>
> **A claim in the paragraph below is now in question.** It states that we "built the covalent celastrol–Cys
> adduct explicitly." A staging check finds the electrophilic carbon far outside bonding distance of the
> preregistered cysteine in *every* available input, against a ~1.8 Å C–S bond — the co-folding does not seat
> celastrol against an NR4A1 cysteine at all. Whether the adduct was formed, or formed under severe strain, is
> not established by anything we retained. Notably, the withdrawn covalent-vs-non-covalent *null* is exactly
> what one would predict if the covalent leg never carried a bond — a **hypothesis a corrected run could
> test**, offered here as such and not as a finding.
>
> ⚠ **Superseded within a day, and the correction runs against us — do not cite 8.99–16.39 Å.** That first
> staging check resolved the *nearest* of the construct's six cysteines, which is **C566**, not the
> preregistered site **C551** (residue offset 344; the panel's legs record the C566 index throughout). At the
> preregistered C551 the distances are **28.42–39.11 Å across every clean co-fold model in the bucket**. The
> superseded figures made the input look *nearly* admissible — at ~9 Å a co-fold would have come close to
> passing an 8 Å limit while the real site sat ~28 Å away — so the correction makes the admissibility
> criterion **more** binding, not less. Two further defects shared the same root cause and are fixed: the
> covalent restraint would have been built onto C566, and the control named for removing C551 engagement
> (`cov_c551a`) was mutating C566 — i.e. it was not touching C551 at all.
>
> **The preregistration has accordingly been amended (dated, with the frozen text left unedited).** The
> recruitment endpoint (R2) is **retired as a gating criterion** — it returned one distinct value, 1.0, across
> all 18 legs including both negative controls, so it had **zero discriminating power**, and the control
> criterion that depended on it was therefore *unsatisfiable*, making the gate return NO-GO regardless of the
> science. It is replaced by an **input-admissibility criterion that can fail, and does**: a leg declared
> covalent must stage its electrophile within bonding distance of the target-chain Sγ. **The re-run is HELD,
> not merely unlaunched** — unblocking it requires re-folding the covalent systems, not compute.
>
> ## ⚠⚠ RESOLVED 2026-07-25 — THE COVALENT LEGS ARE RETIRED AND THE PANEL IS RE-SCOPED TO NON-COVALENT
>
> The re-folding route named above was **run and refuted**, not argued away, and the covalent arms are
> therefore dropped rather than left indefinitely held. Three results, in the order they close the question.
> **(1) Removing the E3 makes the seating worse, not better** — a binary re-fold without the VHL module puts
> celastrol 33.6–44.7 Å from C551 against ~28 Å in the ternary arrangement, so the ternary geometry is not what
> prevents the contact. **(2) Steering the predictor directly at C551** with an explicit 6 Å pocket restraint
> to that residue **demonstrably acts and still fails**: the distance closes from ~37 Å to **14.8 / 15.6 /
> 15.9 Å** and warhead–target contacts rise, on three independent seeds, and the 6 Å bound is satisfied on
> none of them — the ligand parks instead near the buried C505. **(3) The miss is systematic rather than seed
> noise**: seven clean models over four diffusion seeds, three prefixes and two compute providers span
> 28.4–39.1 Å at C551 with no trend toward it. The only remaining route to a covalent input is a **hand-placed
> pose**, which would fix the *comparison* without supplying the *evidence*.
>
> **This is a statement about the structure predictor, not about the chemistry.** Celastrol's covalent
> engagement of NR4A1 Cys551 is literature-anchored (Zhang et al. 2018 [64]); no deposited celastrol–NR4A1
> complex exists to constrain an MSA-based predictor, and a predictor's inability to reproduce a site is
> evidence about the predictor. It also over-reaches to say "no predictor" — every model here is **Boltz-2**,
> and the four seeds, three prefixes and two providers vary the *sampling and the compute host, not the
> method*. Retiring the covalent arms costs little: the panel's Leg 0 already established for \$0 the covalent
> confound's actual content — the reactive cysteine is **unique to NR4A1** (NR4A2 Tyr, NR4A3 Thr579) — and
> NR-V04 is in any case a **biological holdout for the family-selectivity question, not the method
> calibrator**, so modelling its covalency was never load-bearing for the machinery used elsewhere in this
> paper.

**A covalent-adduct endpoint-MD feasibility panel was built and executed; its interface readouts are withdrawn,
and what stands is the panel's execution and cost.** The co-fold retrospective above left celastrol's covalent
Cys551 engagement unevaluated and its epimer control was affinity-blind (active and 4-hydroxyproline-epimer
constructs gave the identical 0.75 bridge fraction). To probe both, we built the covalent celastrol–Cys
adduct explicitly and ran an **18-leg endpoint-MD panel** — six arms × three velocity seeds — on the
NR-V04-inspired VHL-recruiting assembly: **cov_nr4a1** (covalent adduct + active recruiter), **noncov_nr4a1**
(non-covalent), **cov_c551a** (reactive Cys→Ala, covalent auto-disabled), **warhead_only** (covalent, no
recruiter arm), **recruiter_active** (active recruiter), and **recruiter_epimer** (the VHL-inactive
4-hydroxyproline epimer). Each leg is 1 ns equilibration + 5 ns production (500 frames) in explicit solvent
(amber14 / GAFF-2.11 / TIP3P, OpenMM 4 fs hydrogen-mass-repartitioned LangevinMiddle), scored by an
E3-CA-superposed **Kabsch-aligned interface-RMSD plateau** (R1), an E3–target contact fraction (R2,
recruitment), and target-Lys presentation (R3). **17 of 18 legs completed** (warhead_only-s0 never cleared its
host's container pull across repeated relaunches); **no leg blew up.**

**All three readouts were computed against the wrong protein interface** (banner above): R1 and R2 describe the
Elongin C↔rest interface and R3 counted Elongin C's lysines, because the driver identified the degradation
target by chain *order*. The per-arm interface-stability figures are therefore **withdrawn**, and with them this
subsection's contribution to any GO decision. One observation survives in direction only, and even it is to be
re-derived rather than cited: **recruitment is uninformative here** — every completed leg scored "recruited"
with frac-frames-in-contact = 1.0, in *all* arms including warhead_only (no recruiter) and the epimer, which
holds regardless of which chain pair was measured. **This is now formalised: the recruitment endpoint has been
retired as a gating criterion, on the evidence that it took a single distinct value across all 18 legs
including both negative controls** — a statistic with no variance across the contrast it exists to score. The
corrected re-run, with the chain split resolved and recorded per leg, is **HELD** rather than pending: it
cannot reach the frozen criteria on any currently available co-fold (see the banner above).

What the panel does establish, independent of the chain bug, is **executional**: a six-arm covalent/non-covalent
endpoint-MD control panel with an explicitly built covalent adduct is constructible and runs to completion at
this scale. It ran end-to-end on **Vast.ai community RTX 3090s** (interruptible bid tier) with portable
per-frame checkpoint/resume across preempting hosts, at **~\$0.43 per leg (~\$8 for the full 18-leg panel)**
over a 15-leg price ledger — far below the going-in estimate, and unaffected by the interface error, which
changed which atoms were scored and not what was simulated or billed. Even once corrected, this class of result
would be geometric feasibility only, **not a selectivity, cooperativity, or degradation claim:** 5 ns endpoint
MD samples local interface stability, not binding thermodynamics, ternary cooperativity, or a DC50/Dmax window;
only three seeds per arm; the Cullin–RING/E2~Ub machinery is absent; and the NR-V04 reconstruction's exact
recruiter connectivity remains primary-source-unverified. **One further limit, learned the expensive way and
now adopted as a standing requirement for every MD driver in this program: the panel persisted no trajectory,
so three separate analysis defects — the chain split, a chain-blind reactive-cysteine search, and a
nanometre/Ångström unit error — were each correctable in principle and none correctable in practice.** A
strided heavy-atom trajectory costs tens of MB against the ~112 MB system file these runs already uploaded. It makes **no efficacy, potency, or therapeutic
claim.** Full per-leg readouts, the frozen scoring/prereg, and the driver: `nrv04_covalent_md.py` /
`nrv04_covalent_panel.py`.

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

**External corroboration on *known* NR4A chemistry — neither cheap tier reproduces paralogue preference.**
The decoy null shows the cheap tiers are non-specific on *unrelated* drugs; we additionally tested them on
*experimentally anchored* NR4A ligands, which is a stronger check — a model that cannot recover *known*
NR4A1-vs-NR4A2 preferences cannot be trusted to *discover* NR4A3 selectivity. We assembled a versioned
registry of published NR4A chemistry with cross-checked structures (the Zaienne NOR-1 inverse-agonist lead
compound 19, the NR4A1/Nur77 and NR4A2/Nurr1 direct binders, NR-V04; SI §S10) and docked the reversible
discriminators into the state-matched opened NR4A3/NR4A1/NR4A2 pockets. **The pocket model *accommodates*
every published active (docking ΔG −5 to −9 kcal/mol) but does not *discriminate* paralogues:** only THPN's
known NR4A1 preference is cleanly recovered, the rest fall within docking noise, and multi-snapshot MM-GBSA
does not rescue it — it labels *both* neutral NR4A1 ligands (THPN, TMPA) as **false NR4A3-selective** (the
opened NR4A3 frame is intrinsically more accommodating) and the charged 4-aminoquinolines show
protonation-fragile electrostatic artifacts. This is an independent, external confirmation of the same limit
the decoy null and the protonation-fragility of `denovo_111` establish internally: **paralogue selectivity
cannot rest on docking or single-frame MM-GBSA; it requires FEP with resolved microstates and ensemble
controls, or must be hedged accordingly** (SI §S10).

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
specificity test would require a generation-matched decoy null; **one arm of that control has since been run,
and it does not settle the question — see the dedicated paragraph below.** On the confound's magnitude:
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

**The generation-matched null: one arm has run, it points the right way, and it is underpowered to exclude the
confound it was built for.** The decoy null above controls the *scoring* step but not the *generative* one, so
the designed control runs the **identical** generate → developability-filter → dock → multi-snapshot MM-GBSA →
best-of-N funnel on **control objectives** and asks how often the whole procedure *manufactures* a
confirmed-selective, above-null survivor. Of its three planned arms the **scrambled-objective** arm has run:
`denovo_promise` is permuted so the best-of-N advanced to docking is decoupled from the divergent-handle
objective, on the same real NR4A3 release frame and the same 191 generated molecules — which isolates the
**winner's-curse in the selection step**. It manufactured **no survivor** (0 of 191, against 2 of 20 rescored
reaching `confirmed_selective` and none clearing the null bar), where the real campaign produced **one** (1 of
191, 3 of 13 rescored `confirmed_selective`). **The direction is the favourable one and the honest reading is
that it does not establish anything:** a control campaign that manufactures zero survivors in 191 generations
bounds the manufactured per-molecule rate at **≤ 0.0157 (one-sided 95 %, rule of three)** — three times the
real campaign's own **0.0052** — so a funnel quietly manufacturing at up to that rate is not excluded, and the
one-sided Fisher exact test for 1/191 against 0/191 gives **p = 0.5**. *(The committed artifact previously
recorded this as p = 0.0 with infinite enrichment; those follow from treating a zero point estimate as a
measured zero, and both are retired in place in the artifact's `_superseded` block. No count changed.)* What
would settle it is more control campaigns, not a different statistic. **The arm that speaks most directly to
the generative confound — a fresh generation into a *paralogue* pocket, where any NR4A3-selective survivor is a
manufactured false positive — has not been run**, so §2.7's claim remains the narrow one: `denovo_401` clears a
same-tier decoy null in its design frame, with the design-match advantage bounded but not eliminated. Record:
[`../../results/nr4a3-generation-matched-null/nr4a3-generation-matched-null.json`](../../results/nr4a3-generation-matched-null/nr4a3-generation-matched-null.json).

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

**Result (three independent-seed replicates; small-n statistics, n = 3, 2 dof).** Raw-engine per-receptor
ΔG_bind = **+3.5 ± 1.4 (NR4A3) / +8.3 ± 1.1 (NR4A1) / +8.5 ± 0.7 (NR4A2)** kcal/mol (means ± between-replicate
SD). We report each selectivity contrast as its raw replicates, mean, SD, and the small-sample 95% *t*-interval
(not a Gaussian σ, which n = 3 does not support):
- **ΔΔG(NR4A3 − NR4A1):** replicates **−6.90, −2.85, −4.53**; mean **−4.76 ± 2.03** (SD); 95% *t*-interval
  **[−9.80, +0.28]** kcal/mol — the direction is **unanimous across all three replicates but the contrast is
  *not* resolved from zero** at 95%.
- **ΔΔG(NR4A3 − NR4A2):** replicates **−5.48, −4.20, −5.26**; mean **−4.98 ± 0.68** (SD); 95% *t*-interval
  **[−6.67, −3.29]** kcal/mol — **resolved below zero** (statistically; still held provisional for the separate
  λ-overlap reason in (ii) below).

Both favour NR4A3. Read at its correct weight this is a *relative, conditional* preference for the selected
opened NR4A3 conformer over the selected opened paralogue conformers — **not** an "NR4A3 engages, paralogues do
not" claim. Because the NR4A1 interval still spans zero while the NR4A2 interval does not, `denovo_401` is
described only as **NR4A2-sparing (computational); NR4A1 selectivity provisional** — NR4A2, the harder
(tighter-contrast) paralogue, is the primary gate and is the one cleared, whereas the NR4A1 contrast is
directionally supportive but **not statistically resolved** and is not claimed as established. (The wider NR4A1
SD, ± 2.03, is driven by one replicate whose NR4A3 leg sampled ~2.5 kcal/mol weaker; excluding it, r1/r3 agree
at −6.9/−4.5.)

**Three limits bound the reading, and the repair that would lift the second is scoped but deliberately held.**
*(i) The absolute scale is not validated.*
The same engine on a textbook benchmark (T4-lysozyme L99A + benzene, experimental ΔG_bind = −5.2 kcal/mol)
returns **+1.90 ± 0.09**, under-binding by **≈ +7.1 kcal/mol** — a failed/strongly-biased absolute benchmark —
so we interpret **the receptor contrasts rather than the raw absolute values**, never calibrated absolute
affinities, and do not treat +7.1 as a subtractable constant (a single system cannot establish a
target-independent offset). The contrast eliminates the literally shared solvent leg and is a **protocol-matched relative comparison
expected to reduce some common-mode errors**, but the engine's absolute offset is **not guaranteed to cancel
across paralogues** — target-specific restraint terms, receptor-/bound-state definitions, protonation, and
pose errors can remain, and ABFE is especially sensitive to bound-state/restraint/symmetry/standard-state
treatment; it **remains vulnerable to receptor-specific complex-leg errors** (e.g. the NR4A2 overlap
defect below) and is not invariant to all engine error. *(ii) The λ-overlap defect is systematic across the
decoupling tail, not NR4A2-specific — so **all** the absolutes and **both** contrasts are provisional.* Reading
the diagnostics JSON **as committed at git `b4b8e217`** (the version matching these three AF2 replicates; the
working-tree file at that path has since been overwritten by a later, unrelated λ-repair pilot — see §3 Methods),
median adjacent overlap per leg is a healthy ≈0.13–0.22, but **every leg — the shared solvent leg and all three
complex legs — has at least one soft-core-tail window pair below 0.03**, per-leg minima spanning **0.003–0.027**
(worst: complex-NR4A2 in r3, 0.0034). The NR4A2 minimum is the most severe and, being receptor-specific, does
not cancel via the shared solvent leg, so ΔΔG(3−2) carries the largest such error; but a **solvent-leg**
under-overlap propagates into every absolute, and the NR4A1 and NR4A3 complex legs have their own sub-0.03
pairs. We therefore hold the **whole ABFE block — the three absolutes and both ΔΔG values — provisional pending
a dense-schedule λ-repair** (SI §S7), rather than presenting NR4A2 as a single localized exception. *Status of
that repair (stated honestly):* a dense-schedule repair pilot scoped to the NR4A2 leg (tags
`nr4a3-abfe-nr4a2rep-r1|r2|r3`) has been run but **did not complete** — its output, the file now occupying
`results/nr4a3-abfe/diagnostics/nr4a3-abfe-diagnostics.json`, contains partial complex-NR4A2 legs only, **no
solvent legs, and therefore no ΔG_bind** (the run log records `no ΔG_bind computed (no complete
complex+solvent legs found)`, `research/modalities/_reports_abfe_diag.txt`). **No repaired ΔG or ΔΔG exists
yet**, and the repair as piloted covers only one of the four legs that need it. **It is not currently running:
the whole ABFE block is deliberately held** — completing the repair would sharpen error bars on a quantity that
is conditional on the opened state and reported without any absolute calibration anyway, so it is not the next
thing worth computing. Read the ABFE block as provisional and unresolved, not as pending. *(iii) The ΔΔG is
conditional on
the opened state.* It compares
binding to *selected opened* conformers and omits the receptor-specific free-energy cost of populating that
cryptic-opened state, which is potentially decisive and may differ across paralogues (§4).

**8XTT-anchored recalculation — the NR4A3 leg only, three replicates — structural provenance dominates the
absolute.** To be precise about what is and is not done: the **NR4A3** leg has been rebuilt and run in
triplicate from an 8XTT-anchored conformer; the **matched NR4A1/NR4A2 legs have not been run at all** and remain
the decisive follow-up (§4). Rebuilding the NR4A3 leg from an **experiment-anchored** opened conformer (a
druggable frame from 8XTT-seeded release MD, `denovo_401` docked identically, the shared solvent leg reused)
gives ΔG_bind(NR4A3) = **+8.17 ± 0.98** kcal/mol (r1 7.95 / r2 9.24 / r3 7.32; diagnostics JSON as committed at
git `632010e6`) — **≈ +4.7 kcal/mol weaker** than the AF2-opened
conformer (+3.5). Two readings, both stated at their true weight: **(a)** the choice of opened conformer moves
the NR4A3 absolute by **more than the entire AF2-conditioned selectivity margin**, so the ΔΔG magnitude is
strongly conformer-dependent and must be read as conditional on the *AF2-opened* states, not as a
structure-independent selectivity; **(b)** this remains a **receptor-model sensitivity test, not a selectivity
calculation** — it pairs an experiment-anchored NR4A3 leg against *AF2-opened* paralogue references, a
deliberately mismatched provenance, so the apparent collapse of the margin (8.17 vs 8.3/8.5) is **not** a
selectivity refutation. A *matched* experiment-anchored contrast would require **crystal-seeded paralogue ABFE**
(Nurr1 1OVL / Nur77 3V3E are collapsed apo crystals, so it additionally needs a pocket-opening MD step), flagged
as the decisive follow-up (§4). Caveat carried forward: the 8XTT complex legs share the same low soft-core-tail
λ-overlap (min adjacent 0.017–0.026) as the paralogue legs, so **+8.17 is itself provisional** pending the same
dense-schedule λ-repair before it is read as a converged absolute. Per-replicate paired ΔΔG, λ-overlap
matrices, effective sample sizes, forward/reverse convergence traces, and the per-receptor component
decomposition are in **SI §S7**; the lead-optimization ABFE cross-check (`lo_m0_NCCO`, an FEP tie not an
advance) is in **SI §S5**.

### 2.9 A congeneric relative-FE pilot on the Zaienne cmpd19 anchor converges end-to-end

The ABFE above is an *absolute* test on a de-novo species. The complementary quantitative tool for a real,
literature-anchored ligand is **relative binding free-energy perturbation (RBFE)** on a congeneric pair — the
lower-variance, field-standard mode, and the engine that underpins the forthcoming ternary/degrader work. As a
first end-to-end pilot we ran one congeneric edge on the **Zaienne cmpd19** anchor (methyl 5-bromoindole-3-
carboxylate, a *functional* NR4A3 ligand; IC₅₀ ≈ 8–47 µM, no solved co-crystal pose) → its **5-NH₂** analogue,
docked into the same metadynamics-derived **opened** NR4A3 conformer used throughout §2, with OpenFE's
`RelativeHybridTopologyProtocol` (12 λ-window Hamiltonian replica exchange, MBAR reduction; `nr4a3_rbfe.py`,
protocol in §3), on a Modal L4 GPU with per-iteration GCS checkpoint/resume.

**Result (single edge, single replicate, single conformer).** Both alchemical legs MBAR-converged with tight
within-run standard error: complex-leg ΔG_morph = **−29.68 ± 0.24**, solvent-leg = **−31.52 ± 0.26** kcal/mol,
giving **ΔΔG_bind = +1.84 kcal/mol** (± 0.36, leg SEs in quadrature) — the 5-NH₂ analogue is predicted
**≈ 1.8 kcal/mol (≈ 20×) weaker** than cmpd19 in the modeled pocket.

**Honest weight.** This is a **pipeline-validation and convergence** result, not an affinity claim. (i) It is a
**conditional** relative free energy for a **hypothesized** cmpd19 binding mode in a preselected open conformer —
cmpd19 has **no solved pose and no measured affinity for this pair**, so read the sign and the convergence, not a
Kd. (ii) "Converged" here means **statistical** convergence and self-consistency (both legs, tight MBAR SE),
**not** experimental accuracy; accuracy is established separately against a **public measured-ΔΔG benchmark**
(the valA track), which this is not. (iii) It is a **single edge / single replicate / single conformer**; the
reproducibility (independent replicas) and receptor-sensitivity (pose/state sweep) needed to clear the pilot's
pre-registered GO/NO-GO are still outstanding. What it does establish is that the congeneric-RBFE machinery runs
end-to-end and converges on the real NR4A3 system — the quantitative-method foundation on which the paralogue-
selectivity and ternary-cooperativity calculations are built.

**A general limit on what a thermodynamic-cycle self-check can ever certify, stated here because it bounds
every free-energy claim in this paper.** Cycle closure — running a closed loop of alchemical edges and asking
whether the computed values sum to zero — is a routine and valuable internal check, and it is often reported as
if it spoke to accuracy. It does not, and the reason is an identity rather than a matter of degree. Writing
each computed edge as `ΔΔG_calc(A→B) = ΔΔG_true(A→B) + e(A→B)`, the true terms telescope around any closed
cycle, so the residual is `R = Σ e`. If the error is a **per-endpoint state function** — `e(A→B) = ε(B) − ε(A)`
for any ε assigned to states rather than to paths — then that sum telescopes to zero as well. **A closed cycle
is therefore identically blind to every error class that attaches to an endpoint**: the force field, a homology
substitution in the receptor model, the partial-charge method, and protonation/tautomer assignment. (Error in
the *reference* data is invisible for a different and simpler reason — it is not in the calculation at all.)
What closure does see is the non-conservative part: λ-sampling and hysteresis, poor overlap, endpoint states
built inconsistently between edges, and mutually inconsistent atom maps — the last two being classes a
forward/reverse pair structurally cannot reach. We verified the identity numerically (2,000 random
state-function draws give a maximum |R| of 3.6 × 10⁻¹⁵, i.e. machine precision, while adding a per-edge path
error makes R non-zero immediately) and in independent unit tests that construct a fresh per-endpoint bias
rather than re-running the generator's own loop. The practical consequence is a reporting rule this paper
adopts: **a closed cycle, a small forward/reverse gap, and good MBAR overlap are precision diagnostics and may
never be presented as accuracy evidence**, and a known-answer benchmark against measured data is not
substitutable by any number of internally consistent cycles.

**The congeneric map is COMPLETE at 18 computed edges of the 18 that are computable, in a 19-edge map.** The
three numbers are different and all three are needed: 19 is the designed map, **18** is what the lane can ever
deliver (one edge is excluded for a measured reason given below), and 18 is what landed. The lane closed
itself — `pending=0`, `live=0`, every unit carrying a `ddg.json` or on the blocked list — so the counts are
final rather than a snapshot of work in progress. They remain readable as `n_units` / `n_computable` /
`n_complete` in [`../modalities/step1-fanout-map.json`](../modalities/step1-fanout-map.json) — **that artifact
governs and this paragraph does not.** A 19-edge perturbation map around the cmpd19 anchor is frozen
(`congeneric-rbfe-map.json`), its common-mode input poses are built (every analogue inheriting the anchor's
core coordinates atom-for-atom, so the edges are mutually comparable), and the fan-out returned ΔΔG_bind for
all 18 (single replicate each, 12 λ-windows, **$73.79** of realised GPU spend against a derived authorisation
ceiling of $74.91).

Of the 18, **15 are rooted at the cmpd19 anchor** and are the ones that can be read as "tighter or weaker than
cmpd19"; the remaining **3 join two non-anchor nodes** and are listed separately below, because a ΔΔG measured
between two analogues is not a statement about the anchor at all. More negative = predicted tighter than the
cmpd19 anchor in the modeled pocket:

| analogue (5-position unless noted) | ΔΔG_bind (kcal/mol) | mapped atoms |
|---|---|---|
| `cw_ev_5opropargyl` | **−1.698 ± 0.380** | 21 |
| `cw_bio_tetrazole` | −1.215 ± 0.317 | 15 |
| `cw_ev_5pegamine` | −0.646 ± 1.071 | 21 |
| `cw_ev_5alkyne` | −0.363 ± 0.047 | 21 |
| `cw_bio_acylsulfonamide` | +0.127 ± 0.688 | 17 |
| `cw_ms_free_acid` | +0.136 ± 0.457 | 18 |
| `cw_bio_hydroxamic` | +0.392 ± 0.285 | 17 |
| `cw_ms_5acetamido_ester` | +0.445 ± 0.572 | 21 |
| `cw_ev_5oh` | +0.474 ± 0.195 | 21 |
| `cw_ms_carbinol` | +0.582 ± 0.602 | 17 |
| `cw_ev_5cooh` | +0.688 ± 0.197 | 21 |
| `cw_bio_primary_amide` | +0.935 ± 0.500 | 17 |
| `cw_ev_5nh2` | +1.064 ± 0.118 | 21 |
| `cw_ev_5ch2nh2` | +1.248 ± 0.139 | 21 |
| `cw_ev_5piperazine` | +3.403 ± 0.649 | 21 |

The three non-anchor-rooted edges, which close cycles in the map rather than rank analogues against cmpd19:

| edge | ΔΔG_bind (kcal/mol) | mapped atoms |
|---|---|---|
| `cw_ev_5oh → cw_ev_5opropargyl` | −2.928 ± 0.589 | 22 |
| `cw_ev_5nh2 → cw_ms_5acetamido_ester` | −1.345 ± 0.810 | 23 |
| `cw_ms_free_acid → cw_bio_primary_amide` | +2.106 ± 0.132 | 17 |

**Every uncertainty in that table is a within-run MBAR standard error propagated in quadrature — NOT a
replicate SD.** One replicate per edge cannot report reproducibility, so these speak to precision only, and the
ranking must be read as provisional. Live record:
[`../modalities/step1-fanout-map.json`](../modalities/step1-fanout-map.json), whose `_claim_ceiling` field
governs and states the binding limit: *conditional* relative free energies given a **hypothesized** cmpd19 pose
(no solved NR4A3 co-crystal) in **one** modeled opened conformer.

**Those three edges exist to close cycles, so the closures are reported — and one of the three does not
close.** Per the identity argued above, closure is a precision diagnostic and can never certify accuracy; but
the converse direction does carry information, because a cycle that fails to close means at least one of its
edges is unconverged or mis-mapped. Two of the three cycles close comfortably: `cycle_exitvector_aniline`
(cmpd19 → 5-NH₂ → 5-NHAc → cmpd19) at **R = −0.726** and `cycle_exitvector_ether` (cmpd19 → 5-OH →
5-O-propargyl → cmpd19) at **R = −0.756**, both inside the preregistered ±1.0 kcal/mol tolerance.
`cycle_3carbonyl` — cmpd19 → free acid → primary amide → cmpd19, i.e. `+0.136` and `+2.106` against the direct
`+0.935` — sums to **R = +1.307 and is a VIOLATION** of that tolerance. Because the residual is a property of
the loop rather than of any one edge, this does **not** identify which of the three is at fault; what it does
establish is that **at least one of them is not converged or not consistently mapped, and all three are
therefore quoted here under that reservation.** They remain in the tables because deleting an edge on a
closure failure would silently truncate the map, which is exactly the failure mode the previous paragraph
distinguishes from a named exclusion — but no ranking statement in this section should be rested on the
3-carbonyl arm. The natural resolution is the one the section already flags as outstanding everywhere else:
replicates. With one replicate per edge, a 1.307 residual against per-edge MBAR errors of 0.13–0.50 cannot be
separated into "a mis-mapped edge" and "three single draws that happened to land this way", and the
between-replicate SD measured on the *ternary* calibrator (§2.11, 0.375 kcal/mol, ≈3× its own within-run
errors) is the closest available indication of how large that second possibility is. Machine record:
`cycle_closure` in the same artifact.

**⚠ An independent recomputation of the same edge disagrees with the §2.9 pilot by more than either stated
uncertainty, and we report it rather than choosing between them.** The pilot above gives cmpd19 → 5-NH₂ =
**+1.84 ± 0.36** kcal/mol; the fan-out's `cw_ev_5nh2` is the same nominal perturbation and gives **+1.064 ±
0.118**. The gap is **≈0.78 kcal/mol**, against quadrature errors of 0.36 and 0.12. The two were computed on
different execution lanes with different protocol settings, so this is **not** a like-for-like replicate and
does not license a reproducibility statistic in either direction — but it is a direct, concrete illustration of
the point this section already makes: a tight within-run MBAR error is **not** a reproducibility claim, and
here two independent runs of one perturbation differ by several times their own error bars. Reconciling them
(identical protocol, matched conformer, true replicates) is outstanding work, not a resolved question.

**One edge is excluded for a principled, measured reason rather than a budget one, and it is worth reporting.**
The edge to `cw_bio_nmethyl_amide` is **not** unrun — it is unrunnable by the mappers available: its complex leg
aborts on a provably degenerate atom map. A complete 22-atom map exists as a graph fact, giving a provable floor
of **20** mapped atoms, and the production mappers reach **17** (LOMAP, `element_change=False`), **19** (LOMAP,
`element_change=True`) and **18** (Kartograf). Both LOMAP budgets return in 0.01 s, which measures the MCS
timeout *not* to be the mechanism, so a relaunch aborts identically and buys nothing. Recording this as a
mapper-capability limit rather than a missing datum is the honest reading: an incomplete perturbation map with a
named, reproducible reason for each hole is a different object from one silently truncated on cost.

Re-measured on the production staged components on 2026-07-29, that reading holds, and one further detail
sharpens it. A count two short of a floor is equally consistent with a search that nearly succeeded and one that
failed and returned nonsense, so we recorded *which* atoms each mapper leaves unmapped and which element
substitutions the returned map itself makes. The 19-atom LOMAP map reaches 19 only by mapping the ester's methyl
**carbon** onto an amide **hydrogen** — a heavy atom onto a hydrogen. It is therefore not a near-complete map two
atoms short but exactly the degenerate correspondence the floor exists to reject, and the two mappers that remain
chemically sane (strict-element LOMAP, Kartograf) top out at 17 and 18. The limit is thus a property of the
available *mappers* and not of the chemistry — the two heavy-atom graphs are isomorphic up to the single O→N
substitution, so a complete map exists to be found — which also makes the exclusion revisitable rather than
final: should any mapper reach the floor for this edge, it runs like the others.

**A second hole has a different and non-scientific cause, and it is reported separately because conflating the
two would overstate the map's limits.** The edge to `cw_bio_primary_amide` failed repeatedly, and the cause is
not chemistry, not the atom map (17 mapped against a provable floor of 12) and not the rented hardware: the
solvated hybrid system as built contains two atoms at *exactly* coincident coordinates, and they carry a gradient
of **4.996 × 10¹⁷ kJ mol⁻¹ nm⁻¹** against **6.46 × 10⁵** on the largest non-degenerate atom of the same
112,955-atom build — a factor of 7.7 × 10¹¹. That value is finite, so the potential energy of every force term is finite and a
double-precision CPU minimiser descends it to completion; the GPU minimiser does not, and this edge died at the
identical `LocalEnergyMinimizer` call on **25 archived attempts across 7 distinct card/driver combinations**
before the per-attempt archive was examined. The remedy is the starting geometry — one member of each coincident
pair is displaced by 0.01 Å, two orders of magnitude below a bond length, into a minimiser that is about to move
it in any case — and it touches no force-field parameter, no λ schedule and no estimator. Its effect was measured
as a before/after on the same build rather than argued: the system's largest gradient falls from 4.996 × 10¹⁷ to
6.46013 × 10⁵ kJ mol⁻¹ nm⁻¹, which is the value an unrelated atom already carried (6.46013 × 10⁵) before the
displacement — the singular force is removed and every other force in the box is unchanged to six significant
figures. **This edge is
therefore a defect that was fixed, not a scientific exclusion, and it is not counted against what the method can
do.** The de-degenerated geometry reached the execution hosts and **the edge computed**: it is the
`cw_bio_primary_amide` row of the ranked table above (**+0.935 ± 0.500**, 17 mapped atoms), and `blocked_units`
in the live artifact now names only the mapper-limited edge. What the episode cost is worth recording next to
the fix, because it is the reason the archive was eventually read at all: the edge burned **25 rentals across 7
cards** before anyone counted the attempts, each one failing at the same call for the same reason.

Two scope limits apply to every edge in this map, computed or not: it covers only the **charge-conserving**
microstate of each edge (the charge-changing species need a co-alchemical or analytical charge correction that is
not implemented), and only the **primary** receptor conformer — so it is a single-conformer *conditional* map,
not a paralogue-selectivity readout and not a sensitivity range.

### 2.10 A mechanism-first prospective degrader-design stage: categorical paralogue handles, a negative on E3 breadth, and a virtual linker library (all CPU, no GPU)

*Novelty positioning, carried forward from §2.5 rather than restated: nothing in this section is a
methodological first.* All-atom alchemical ternary-cooperativity free-energy calculation is an active
published area [60–63], orientation/pose sampling around a tethered ternary is standard practice, and the
geometric kernels used here are textbook. What is offered is an **open-source implementation applied honestly
to the NR4A family with its negatives reported**, plus the two structure-derived corrections below — an
incremental methods contribution, and any future quantitative result from this line must be benchmarked
against that prior art rather than presented as a new capability.

Sections 2.4–2.9 pursue paralogue discrimination as a **thermodynamic margin** — a divergent pocket, a
docking/endpoint/FEP ranking, a ternary that might compound it. This section reports a re-ordered prospective
stage that puts a different question first, and reports what it returned, including where it returned a
negative. **Every result below was computed on CPU; no GPU was used and none is claimed.** Nothing here is a
molecule that was made, a binding measurement, or a degradation result: the output is a set of **predicted
selective candidates** and the geometric hypotheses behind them.

**Why the search was re-ordered: the induced-interface axis is uncalibrated, and at the time it was also
believed to be unresolvable.** A useful degradation window needs on the order of **2.0 kcal/mol** of true
induced-interface margin (median over 27 potency scenarios, range 1.75–2.25; `selectivity_margin_model.py`).
When the search was re-ordered, that was set against a best-case **resolvable** difference of 1.12 kcal/mol —
a figure computed at a replicate scatter the program had **assumed** rather than measured, and a
field-standard relative-FE accuracy near 1.7 kcal/mol RMSE taken from the literature. **Both inputs have since
been measured on this pipeline, and they move in opposite directions.** The replicate scatter is
**0.375 kcal/mol** (§2.11, the between-replicate SD of the ternary calibrator at n = 3), which puts the
best-case resolvable difference at **0.60 kcal/mol**, not 1.12 — so the required margin is ~3.3× the noise
floor rather than ~1.8×. The accuracy, meanwhile, is no longer a literature number: the one known-answer test
of this exact quantity class **misses by 1.543 kcal/mol with the wrong sign** (§2.11), and a redundant-cycle
diagnostic localises that miss to a **per-endpoint state function**, which replicates cannot remove.

Two caveats travel with the measured scatter and we state them rather than absorbing them: it was measured on
the **SMARCA2/VHL** calibrator and is transferred to NR4A, and it is an **upper** bound on sampling-only
scatter because the replicates also differ in their relaxed homology model and in independent solvation. The
net reading is therefore not that the induced-interface axis is *blunt* but that it is **uncalibrated** — a
different deficiency with a different remedy, since more sampling addresses precision and only a known-answer
benchmark addresses accuracy. We accordingly treat the induced-interface (**marginal**) axis as a confirmation
tool whose accuracy is unestablished rather than as a discovery tool, and searched first on **categorical**
differences — positions at which NR4A1/NR4A2 are structurally *incapable* rather than merely disfavoured,
which require no thermodynamic margin at all and so do not depend on either figure above.

**Full-length paralogue alignment gives two categorical handles, and their paralogue side is a sequence fact
rather than a model output.** Aligning full-length UniProt NR4A3/NR4A1/NR4A2 with two independent aligners and
requiring agreement (`nr4a_paralogue_unique_residues.py`) identifies **four NR4A3-unique cysteines**, of which
**Cys397** — NR4A1 Asn363, NR4A2 Ser363 — is exposed and sits **10.9 Å** from the cryptic pocket along the
exit vector, and **four NR4A3-unique lysines**, of which **K572, K518 and K592** are exposed in the LBD in the
same 11–16 Å band as the conserved ones. Neither handle needs a receptor model on the paralogue side: a
thiol–Michael adduct cannot form where the aligned position carries no thiol, and a lysine that is not present
cannot be ubiquitinated. That is the sense in which these are *categorical*, and it is why they are worth
searching on ahead of an energy difference the method cannot resolve.

**The categorical claim's one untested assumption has now been tested against paralogue dynamics, and it holds.** Uniqueness at the *aligned* position is a sequence fact, but a degrader does not care which cysteine it labels: the assumption that actually carries the claim is that no paralogue presents some **other** nucleophile that the same linker path reaches. That had been checked only on one static conformer per paralogue. Repeating it over **300 matched conformers** — NR4A3/NR4A1/NR4A2, 100 each (25 well-tempered metadynamics on the homologous cryptic-pocket CV + 3 × 25 ns unbiased release, identical protocol per species) — against **73,867 matched E3 placements** at the 12-atom gate gives **P(no paralogue cysteine reachable | the construct reaches an NR4A3-unique cysteine) = 1.000 for solvent-exposed cysteines in every scope** (static, unbiased-release and biased), with the mean per-placement probability of reaching *any* exposed NR4A1 or NR4A2 cysteine identically **0.0**. On the all-cysteine measure a small residue appears (0.12 % unbiased, 0.29 % biased) and it is entirely on **buried** paralogue cysteines — reachability without labelability. *Reported as the rare-event statistic it is:* the conditioning event fires in ~0.04 % of placements (**122 hits in 73,867**), so the defensible statement is the exposed column — **zero co-labelling events observed** — not a probability quoted to five figures. This removes a specific structural failure mode; it says nothing about thiol pKa, nucleophilicity, adduct stability or promiscuity, which remain the untested and chemical limits on this axis. The same analysis reproduces, from the
opposite direction, the residue that most parsimoniously explains the one demonstrated case of NR4A-family
degradation selectivity: **NR4A1 Cys551 is unique to NR4A1** (NR4A3 Thr579, NR4A2 Tyr), which is both the
covalent confound in reading NR-V04 (§2.5) and the reciprocal of the handle used here. *Checked and reported
weak rather than quietly dropped:* the EWSR1 moiety of the fusion contributes only **1–2 lysines** (the
low-complexity domain is Lys-poor), so a fusion-lysine-directed axis is thin and is **not** used as a design
variable.

**The chemistry axis is robust in the receptor ensemble but is one residue deep, with no geometric fallback.**
Scoring the three unique cysteines across the **100 committed NR4A3 conformers** of §2.3 — 25 metadynamics
frames and 75 bias-free release frames, identical Shrake–Rupley and identical reach calculation per frame
(`nr4a3_handle_ensemble.py`) — shows C397's exposure is a property of the fold and not a lucky frame.
*Every statistic in this paragraph is computed on the **75 unbiased release frames only**; the 25
metadynamics frames are deliberately excluded because they are biased along the pocket-opening collective
variable and their histogram is therefore not a population estimate.* Over those 75, C397's RSA median is
**0.416** (mean 0.405 ± 0.096, p10–p90 0.298–0.510), with the single committed frame's 0.395 sitting at the
median, and C397 comes within a practical **12-backbone-atom** linker of the pocket exit vector in
**72/75 = 96 %** of them. **C420 and C559 reach that gate in 0 of 75** (across all 100 conformers the only
exceptions are **two biased metadynamics frames for C420** and none at all for C559 — frames driven along the
opening CV, not a population a design can count on). They are recoverable only by paying contour
length (16 and 20 backbone atoms respectively), and that length is paid out of the *same* budget that must also
span to the E3, so buying it degrades the term it would rescue while simultaneously bringing **conserved**
cysteines into reach. So the honest statement is not "NR4A3 carries paralogue-unique cysteines" (plural, true
by sequence) but **"one of them is a usable handle."** This is **concentration risk rather than fragility**:
a live way the axis could have failed does not fire. The electrophile-reach criterion needs **one** conformer
to do two things at once
— present the cryptic pocket the warhead occupies *and* put C397 within a linker's reach — and marginal
fractions say nothing about whether those are the same frames; had they been anti-correlated the axis would
have been conditional on a state that excludes warhead binding, with no marginal statistic showing it. Joining
the two per-frame (the harmonized pocket analysis carries an `orthosteric_druggability` for exactly these
conformers at the pinned D\* = 0.53) gives **P(both) = 0.560** against an independence product of **0.563**,
and P(reach | druggable) = **0.955** versus 0.960 unconditional. At n = 75 this establishes **the absence of an
anti-correlation, not independence as a precise property** — read the direction and the magnitude, not the
probability. What the axis does carry is a single point of failure whose
untested modes are **chemical, not geometric** — thiol pKa, intrinsic nucleophilicity, adduct stability and
electrophile promiscuity, none of which any in-silico step in this program tests and the last of which needs
chemoproteomics. The program's only insurance against a C397-specific chemical failure is the **unique-lysine**
term, not a second cysteine.

**Widening the E3 recruiter panel returned a negative, and the negative is the result.** The design argument
for widening beyond VHL/CRBN is that recruiter choice is free at CPU and multiplies the chance that *some* E3
surface complements NR4A3's differential surface. Ten recruiters (VHL, CRBN, BIRC2, DCAF1, DCAF15, DCAF16,
KEAP1, FEM1B, RNF114, MDM2) were assessed from live UniProt/RCSB fetches under a **rule whose decision content
was committed before the fetch** — three eligibility gates (a public ligand-bound structure at ≤3.0 Å or by
NMR; ligand buried fraction ≥0.50; exit clearance ≥8 Å with 30° cone openness ≥0.30), then a nondominated
Pareto front over linker-analogue tier / exit quality / open solid angle, then a fixed lexicographic tiebreak
to a hard cap of two, with **no tunable scalar** (`e3_recruiter_staging.py`; the gates, axes, tiebreak and cap
are byte-identical between the preregistering commit and the final artifact). *Stated precisely because the
distinction matters:* the **decision rule** was fixed before any data; the **geometry engine** was
defect-repaired after the first data were seen — biological-assembly frames, the exit-vector ray origin,
coordinate-level verification of bridging — with each repair and its triggering observation logged. **CRBN
(9CUO [67]) and VHL (9GIO [68]) advance**, CRBN as the sole Pareto-front member and **VHL explicitly as a backfill and
E3-choice sensitivity control, not a co-winner**; the CRBN−VHL margin is **0.033** in open solid angle on one
deposited conformer each with no error model, and is reported as a **tie, not a finding**.

The informative part is *why* the widening did not deliver breadth. **Availability was the wrong constraint:**
all eight widened arms are broadly expressed and record-complete on the Human Protein Atlas, and no recruiter
was dropped for expression (enforced by a test that fails the build if a drop reason mentions it). The binding
constraint is **structural stageability**. **RNF114 has no deposited structure of the protein at all** — not
"unliganded", structurally unknown — so nothing could be staged for it. **DCAF16**'s ligand is only **34.4 %**
buried once its partners are removed from the occluder set, against the 0.50 gate, and makes far more contacts
to the partner than to DCAF16 itself: that is what a **molecular-glue interface looks like when the partner is
taken away — not a handle pocket to hang a linker on** — and it holds despite DCAF16 carrying the panel's
*highest* open solid angle (0.736), i.e. openness without a pocket. **DCAF15** has no partner-free liganded
structure at all. **So the widening confirmed the incumbents rather than displacing them**, and that is a real
negative for the E3-breadth argument rather than a null to absorb quietly. Three honest riders travel with it:
the confirmation holds only *after* the biological-assembly frame fix (before it, the advanced pair was
BIRC2 + MDM2, because VHL and CRBN were being measured inside ternary complexes whose bound partner occupied
the very orientation space being scored — those numbers are retracted, not merely superseded); **BIRC2 lost by
0.039** in open solid angle at identical tier and exit quality, so it is a near-tie and the first recruiter to
bring back at $0; and **the rule is blind to recruiter-intrinsic pharmacology** — MDM2 and KEAP1 rank well on
geometry while their handles are developed inhibitors of the E3's *own* function. That blindness is a required
input to the next gate, not a footnote: no recruiter may be committed to on geometry alone.

**An orientation-basin search over the two advanced recruiters nominates on the categorical terms — and
"weakly" is part of the verdict.** Sampling 10⁶ rigid-body placements of each recruiter arm around the
warhead-bound target, over an ensemble of **12** warhead exit-vector poses, and evaluating every placement
against NR4A3 and both paralogues superposed into **one** frame (so a paralogue difference cannot be an
artifact of three independent searches; `nr4a3_basin_search.py`), then clustering on the interface fingerprint
the scored terms actually depend on, gives **58 pose-marginalised meta-basins over 192 basins**. Of these,
**3** place an electrophile within the practical 12-atom gate of a unique cysteine, **40** put the modelled
E2~Ub transfer zone over a unique lysine at a rate exceeding its own background null, and **28** discriminate
NR4A3 nominally. The three that clear the electrophile gate are **`vhl|M2`** (C397 at **10** backbone atoms,
gate-level reach fraction 0.057), **`vhl|M3`** (11 atoms, 0.021) and **`crbn|M17`** (12 atoms, 0.045, clearing
the lysine background by 3.87×).

**The basin that is strongest overall is not one of them, and saying so is the point of separating the two
terms.** **`crbn|M0`** survives **11 of 12** poses and clears the *lysine* term's background by **7.5×** — the
best nomination in the run on both counts — but under the exact reach kernel its shortest C397 requirement is
**13** backbone atoms, so it **misses the 12-atom electrophile gate by one atom** and its gate-level reach
fraction is **0.000**. A basin can therefore carry the transfer-zone term convincingly and the electrophile
term not at all; the gate passes on the categorical basis because three *other* basins clear it, not because
the leading basin does. Four quoting rules constrain how any of this may be read, and each was produced by a
measurement rather than by caution:

1. **The categorical terms fire in a small minority of placements.** Gate-level electrophile-reach fractions
   across the three basins are **0.021–0.057** — an electrophile reaches C397 in only **2–6 %** of a basin's
   placements — and each is itself a *maximum* over the meta-basin's member basins, i.e. the optimistic end.
   Reach is nonetheless **selective** rather than generic: the **conserved** cysteines are scored by the
   identical rule as a control, and that control is **exactly zero in 184 of 192 basins** (0.4–3.9 % where it
   is nonzero). The lysine term is held to its own separate null — a basin must exceed the background rate at
   which *any* linker-feasible, clash-free placement covers a unique lysine (**1.0–7.5 %** across the 24
   arm × pose nulls), which is why the enrichment quoted for `crbn|M0` above is on the *lysine* term and must
   not be read as an electrophile-reach enrichment. So these are **enrichments, not saturation**: a basin is a region
   that *admits* the mechanism, not one that enforces it, and the gate therefore **nominates** rather than
   decides.
2. **All three electrophile-reach basins reach C397, and only C397**, consistent with the ensemble result
   above and with the same consequence — the chemistry axis has no geometric fallback. Across the whole run
   the shortest requirement per residue is **C397 10 · C420 16 · C559 27** backbone atoms, so at a 12-atom
   gate the other two are not near-misses but out of range by 4 and 15 atoms.
3. **The reach figures are exact, and they were not always: an earlier criterion made every one of them a
   lower bound by up to about 5 backbone atoms.** That criterion credited a pendant arm with shortening the
   *span* between the two anchors, which no pendant can do — a linker must physically connect the two exit
   vectors whatever its branch carries. All 576 (basin × unique cysteine) records were audited under it and
   **none was internally impossible**, so it was a bound rather than an error; it has since been replaced
   throughout by the exact three-ball kernel and every figure recomputed on a matched 10⁶-placement run.
   **The correction is the reason the electrophile count in this section is 3: it moved that term from 7 to 3,
   while leaving the transfer-zone term at 40 and the nominal limb at 28 bit-identical** — which is itself the
   evidence that the two terms are independent, since only the term the rule touches moved. The superseded
   values are recorded in Appendix A, and no figure in this section is a bound.
4. **The shortest-linker figure is a best-of-N over a basin's members, and the achieving member is not the
   published representative.** Both are now emitted — the achieving placement (optimistic) and the
   representative (typical) — and neither may be quoted without saying which. The gap is large enough to
   matter: at `crbn|M0`, and at one fixed pendant convention throughout, the exact C397 requirement is
   **25** backbone atoms at the representative and **11** at the achieving placement (under the search's own
   shorter 3.0 Å pendant convention the representative figure is 33; a length quoted without its pendant
   convention is not interpretable). A first pass that compared a best-of-N length against a typical
   placement concluded that linker tractability *inverts* the basin ranking, `crbn|M0` looking the least
   buildable of the set; emitting the achieving placement explicitly removed that apparent inversion, leaving
   `crbn|M0` comparable to the others rather than an outlier (13 backbone atoms at the achieving placement
   against 10 and 11 for `vhl|M2` and `vhl|M3`, all at the 3.0 Å convention). It does not make it the *most*
   tractable, and the earlier draft of this section said so; that overstatement is withdrawn in Appendix A.
   The representative/achieving split was purely additive to the counts — the electrophile term moved later
   and for the separate reason given in rule 3, not in this re-run.

**Two ubiquitination-geometry parameters were measured rather than assumed, and both corrected defaults this
program was using.** *(i)* The distance an E2~Ub must span to a substrate lysine was assumed at **10 Å**; in a
solved CRL4–DDB1–CRBN–IKZF3–E2~Ub ubiquitylation assembly (9UUM [70]) the nearest of 11 substrate lysines sits
**17.09 Å** from the E2 catalytic cysteine, with the rest at 17.3–45.8 Å. The assumed value was therefore
~7 Å too strict, and the reported run uses the measured one. *Stated carefully, because the obvious stronger
claim is not supported:* the committed per-basin sensitivity sweep shows the categorical rank is **not**
abolished at 10 Å — 84 of 192 basins still reach rank ≥ 3 somewhere in the sweep at 10 Å against 75 at 17 Å,
because a wider zone also picks up **paralogue** lysines and demotes the rank — so the correct statement is
that a parameter chosen by assumption was quietly setting the scale of a gate, **not** that it would have
suppressed the term. The category is genuinely sensitive to the choice, and is reported per basin as such;
that sensitivity is the term's single biggest soft spot. (A deposited assembly is a snapshot poised for
transfer, not a transition state, so the measured value is an empirically anchored **permissive** radius, not
a proof of the productive one; and it is one distance in one CRBN assembly.) *(ii)* A **composed** CRL RING —
one built by superposing a ligand-bound receptor entry onto a separate cullin-scaffold entry — carries
**~30–50 Å of positional uncertainty** (VHL 30.18 Å, CRBN 50.14 Å against the RING of each arm's own intact
assembly; two arms, so a two-point range rather than a distribution). This is **conformational rather than
error**: the joins are good (VHL 0.98/1.17 Å, CRBN 1.17/1.92 Å) and CRLs are genuinely mobile scaffolds, so a
well-fitted composition is still not a position. The consequence
generalises past this section — **no degradation-geometry claim in this program may rest on a RING or an E2
that was composed rather than observed** — and it is **not in force in the run reported here**, which anchors
both arms on the **E2 catalytic cysteine observed in a solved assembly** (8R5H [69] for VHL, 9UUM [70] for
CRBN). It
binds any future recruiter for which no intact assembly exists. Relatedly, the E2 catalytic cysteine had itself
been assigned by a heuristic; identifying it instead as the thiol bearing ubiquitin's C-terminal glycine
**overturns the heuristic's answer** and is unambiguous (3.4 Å versus 16.4 Å for the next-nearest candidate).

**A conflict in where the transfer zone sits was resolved against a solved intact assembly, not adjudicated.**
Staging VHL from two separately verified receptor entries put the observed transfer anchor **30.9 Å** and
**69.9 Å** from the recruiter's ligand exit vector — a ~39 Å disagreement that, had it been conformational,
would have weakened the lysine term across the board. **8R5H [69] settles it with no model at all**: it holds
VHL·Elongin B·Elongin C, the MZ1 degrader bound in the VHL site, **and** a trapped UBE2R2~ubiquitin in one
frame, so the disputed distance is directly measurable — **30.76 Å**. The staging the reported run consumed
reproduces it to **0.09 Å** (like-for-like, because that staging's source entry carries the *same* ligand and
the rule selects a neighbouring atom of it — which is also the resolution this convention can be expected to
have between a 2.7 Å crystal and a 3.44 Å cryo-EM map, so 0.09 Å should be read as agreement at the
convention's own resolution, not as a precision claim); the alternative misses by **39.15 Å**. Decomposing
both into a common frame puts
**0.02 Å** of the disagreement in the mapped E2 position and **50.67 Å** in the exit vector, which localises
the fault and refutes the conformational explanation. The root cause, read off the structure rather than
inferred: the rejected staging's chosen "recruiter ligand" has a 4.5 Å lining of **eight Elongin C residues and
zero VHL residues**, because the ligand-selection step tested contact against the receptor *body* (recruiter
plus obligate partners) and never against the recruiter itself. Fixed, unit-tested on that case, and verified
to leave every consumed number bit-identical.

**A virtual linker library turns the surviving basins into enumerated structures, and prefers reversible
covalency for a reason that is argued, not measured.** Enumerating linker architectures against each confirmed
basin's exact geometric requirement — anchor-to-anchor span, both exit-vector angles, the connecting dihedral,
worm-like-chain strain, and the integer branch positions from which a pendant of a given reach can touch
Cys397's Sγ — gives **36 retained constructs from 3,544 enumerated** at the achieving (exemplar) placement and
a further **18 from 1,791** at the representative placement, **54 in total**, under a filter **fixed before
enumeration** (span the anchor-to-anchor floor; comfortably hold ≥25 % of the basin's members; ≤3 kT of chain
strain at the designed placement; ≤24 backbone atoms; a per-basin cap; one construct retained per confirmed
basin even on failure, with its failing thresholds attached, so the library cannot look clean by silently
dropping the best basin). *Both placements are enumerated for the reason given in rule 4 above — a construct
drawn against a best-of-N geometry and one drawn against a typical member of the same basin are different
molecules, and quoting either alone would misstate what is buildable.* In the event no basin needed the
failure clause: all 54 were kept on merit (`n_kept_despite_failing` is 0 for every basin), which is a
measurement the clause exists to make possible rather than a foregone result. Every retained construct is
emitted as an explicit SMILES from staged warhead chemistry (the cmpd19
methyl 5-X-indole-3-carboxylate anchor with exit vectors already in the congeneric series), a published E3
handle (VH032 on the *tert*-leucine nitrogen, or pomalidomide on the 4-amino nitrogen), and an L-amino-acid
branch residue that makes the pendant's stereocentre a defined **(S)** centre inherited from a catalogue
building block rather than an unspecified one. **All 54 were verified with RDKit against the parsed molecule
rather than against the geometry that proposed them** — backbone length and branch position re-derived by
topological shortest path between the two anchors, required cores and declared pendants matched as exact
substructures, and any unassigned stereocentre refused. That verification is a **refusal, not a report**, and
it caught defects invisible to inspection, including a junction that emitted an α-ketoamide, a hydrolytically
labile N,O-acetal, an off-by-one that placed every electrophile one atom too close to the warhead, and a
stereocentre created by the saturated non-electrophilic control. The default electrophile is a
**reversible-covalent β-methyl α-cyanoacrylamide**, with an irreversible acrylamide and a saturated
non-electrophilic analogue carried as comparators. **The preference is a stated design rationale with its
comparator enumerated, not a computed result:** an irreversible adduct makes the degrader **stoichiometric**
and forfeits catalytic turnover, the property that makes the modality attractive — nothing energetic has been
run comparing the two. *Noted because it is a convergence and not a design input:* the field's one demonstrated
NR4A-family-selective degrader recruits a warhead whose own reported mechanism is **reversible**-covalent
engagement of a paralogue-unique cysteine [64]. This library arrived at the same chemistry class from
turnover arguments, and at the reciprocal residue from sequence — so the precedent is corroborating, **not**
evidence that this construct will behave as that one did.

**The covalent handle is an unresolved liability, not an upgrade, and the parent warhead's pharmacology
compounds it.** Electrophile promiscuity cannot be assessed without chemoproteomics, which this program does
not have; and lengthening the pendant, which relaxes reach on the *unique* cysteine, relaxes it on the
**conserved** cysteines at the same time, so intra-NR4A3 chemoselectivity degrades with the same knob that buys
reach (the paralogue argument is untouched, being a sequence fact). These sit alongside the parent chemotype's
own reported pharmacology: cmpd19 **de-represses MYC** by blocking the NOR-1–corepressor interaction (§1), so
parent-warhead pharmacology is a **potential liability, not evidence of benefit**, and must be reported with
any covalent design rather than separated from it. The library's only honest hedge is that it is not
all-covalent: constructs carrying **no electrophile at all** are retained and are designed against the
**unique-lysine** term instead, which is independent of Cys397 entirely.

**What this stage does not establish.** It is a **nomination**, not a result. Every construct and every basin
is conditional on the **hypothesized cmpd19 binary pose × the chosen receptor frame** — a *double*
conditionality, and this work holds no cmpd19 pose in the matched-model frame (cmpd19 has functional
target-engagement evidence and no solved NR4A3 co-crystal, §2.9), which is why the warhead exit vector is
marginalised over a pose ensemble rather than asserted. The placements are **rigid-body with rigid side
chains, no solvation and no induced fit**, so a basin is a region of orientation space that admits a
mechanism, not a modelled complex; the strain estimate is an ideal semi-flexible-chain quantity, not a
force-field energy; whether the linker's conformer population actually visits the branch position that
presents the electrophile is unmeasured. The lysine term **raises the odds; it does not guarantee the
paralogue is spared**, because real degraders often ubiquitinate several lysines and lysine-less substrates
can still be degraded through N-terminal, Ser, Thr or Cys ubiquitination. The models are LBD-only, so hinge,
DBD and fusion-partner lysines are absent. The synthetic annotations are **routes, not validated syntheses** —
building-block availability was not checked against a live commercial catalogue and no step was attempted.
And the **causal test has now been run, and returned its preregistered null**: the matched-pair experiment
asking whether a designed element *creates* discrimination gives **S = −0.1297 ± 0.3264 kcal/mol** (§2.10e),
i.e. indistinguishable from zero — the outcome §5(b) fixed in advance as the *likely* one. It does not add a
selectivity claim and it does not remove one. Under the language this paper holds itself to, the deliverable
of this stage is *a
computationally prioritized, structure-defined, retrosynthetically annotated candidate matrix for synthesis
and experimental testing* — not a hit, not a selective degrader, and no statement about efficacy, safety, a
therapeutic window, or clinical readiness.

### 2.10e The causal matched-pair test returns its preregistered null: a one-atom designed wedge creates no resolvable paralogue discrimination

**What was asked, and why this one experiment.** Everything in §2.10 is a *prediction* that designed elements
should discriminate. The matched-pair double difference is the only test in this program that asks whether a
designed element **causes** discrimination rather than being nominated by a model that already assumes it.
The pair `d0 → d` differs by **one atom** — an aromatic C–H becomes N (phenyl → 3-pyridyl) — on a wedge aimed
at **T407**, which is Leu in NR4A1 and Val in NR4A2, so the hydrogen-bond donor NR4A3 presents is absent in
*both* paralogues. The statistic is
`S = ΔG_tern(NR4A3) − ΔG_tern(NR4A1)`, in which the binary and solvent legs cancel algebraically; its sign
convention and all three readings were fixed in advance in §5(b).

**Result:** **S = −0.1297 ± 0.3264 kcal/mol** (replicate SD over n = 2 independent seeds per arm; NR4A3 mean
−10.9439 ± 0.2354, NR4A1 mean −10.8142 ± 0.2261; the one home of every figure is
[`../modalities/nr4a3-5aks-reduction.json`](../modalities/nr4a3-5aks-reduction.json)). The magnitude is
**2.5× smaller than its own uncertainty**, so *S* is indistinguishable from zero. Per the preregistered
reading this is **"the marginal wedge is absent"** — registered explicitly as the **likely** outcome and as
**not a stop**, because the design's paralogue claim rests on the *categorical* axis (§2.10a–c) rather than
on this marginal one.

⚠ **The honest positive content of the null is a BOUND, not a zero.** At this error the design could only
have resolved a wedge contribution of roughly **|S| ≳ 0.65 kcal/mol** (2σ); it did not, so the measurement
bounds the designed wedge's contribution below about that, and says nothing about smaller effects. The error
quoted is the **replicate SD**, not the MBAR standard error — the latter is ~0.08 kcal/mol per arm, roughly
three-fold smaller, and quoting it would understate the uncertainty by exactly the factor this program's
error-bar standard exists to prevent.

**Staging was verified rather than assumed, because a specific defect would counterfeit this result.** A
one-chain "ternary" leg is a binary leg nobody labelled, and it would also return *S* ≈ 0 — indistinguishable
from the preregistered null. Both arms were therefore checked against their committed staging manifests and
are **identically composed**: chains `A` (254 residues, the NR4A paralogue LBD) and `B` (442 residues, the
CRBN E3 machinery) plus the PROTAC in chain `L`, with `protocol_hash`, `charge_method`, `setup_cache_version`
and `n_windows` all agreeing across the four legs.

**Three limits, each of which could hide a real effect.** *(i)* The reducer flags `n_particles` as disagreeing
across the arms — NR4A1 ≈ 210k against NR4A3 ≈ 148k. Composition is identical, so this is the **solvated box**,
not the molecular system; but it means any size-dependent systematic does **not** cancel between the arms,
which is the one thing a double difference is otherwise supposed to buy. *(ii)* The starting geometry is a
**Boltz-2 prediction** of each ternary complex, not a crystal structure, so *S* is conditional on those poses.
*(iii)* ⛔ **The instrument that produced this number has a failed calibrator.** §2.11's known-answer ternary
cooperativity benchmark misses with the **wrong sign**, systematically. An uncalibrated instrument returning
zero cannot distinguish *"there is no wedge effect"* from *"this method cannot resolve the wedge effect"*, and
this result is not reported as though it could. It is a null from a method whose ability to see the thing it
looked for is unestablished — which is a weaker statement than a null, and is the one supported.

### 2.11 The preregistered known-answer ternary-cooperativity benchmark misses, with the wrong sign, and the miss is systematic rather than statistical

Every degrader claim in §2.10 rests on an alchemical machine that has never been shown to reproduce a *measured*
ternary cooperativity. §2.9 established that internal self-checks — cycle closure, forward/reverse agreement,
MBAR overlap — are precision diagnostics and can never substitute for a known-answer test. This section reports
that test. **It does not pass**, and we report it in full because a benchmark disclosed only when it succeeds is
not a benchmark.

**Design, frozen before execution.** The calibrator (`valB_mini`) is the **Wurz compound 1 → compound 4** edge on
the **SMARCA2/VHL** ternary complex: a single linker **pyridine N → CH** substitution, i.e. a genuine
constitutional element change rather than a stereochemical null-map (checked at freeze time and recorded in the
artifact: `delta_N = −1`, `delta_C = +1`, 59 heavy atoms on both sides). Both compounds have **same-paper SPR** cooperativities (α₁ = 12.8, α₄ = 2.6), so the
target is fixed a priori by `ΔΔG_coop = −RT ln(α₄/α₁)` at 298.15 K = **+0.944 kcal/mol**, positive for the
hi→lo direction. The quantity computed is the thermodynamic cycle `ΔΔG_coop = ΔΔG_alch,ternary − ΔΔG_alch,binary`.
The pass rule was preregistered and requires *all* of: converged diagnostics, **correct positive sign**,
`|mean − target| ≤ 1.0`, between-replicate cycle SD ≤ 0.75, mean > target/2, and a t-based 95 % CI excluding
zero. Frozen record: [`../modalities/wurz-calib-frozen.json`](../modalities/wurz-calib-frozen.json).

**Result, now at the preregistered n = 3.** All three replicates landed on 2026-07-30 and the reduction gives
**ΔΔG_coop = −0.599 kcal/mol against a target of +0.944** — the **wrong sign**, an absolute error of
**1.543 kcal/mol**, and a failure of the preregistered rule on sign alone, before the cycle-SD criterion is
ever reached. The per-replicate values are **−0.5125, −1.0097 and −0.2749 kcal/mol**; every one of the three is
negative, so the sign failure is not an artifact of averaging. The t-based 95 % CI is **[−1.103, −0.095]**,
which excludes zero *on the wrong side of it*: the method resolves a cooperativity change confidently, and
resolves it with the opposite sign to the measured one. Machine record: `valB_calibration_gate` and
`valB_calibration_decision` in the reduction artifact (decision **NO-GO**).

**The between-replicate cycle SD is 0.375 kcal/mol, and it is the durable product of this experiment.** Against
per-leg MBAR standard errors of **0.097–0.132 kcal/mol**, the replicate spread is roughly **three times** the
within-run uncertainty on the same legs. That is a direct, same-system measurement of the gap this paper's
reporting rule asserts — that a within-run MBAR SE speaks to precision and never to reproducibility — and it is
why every ΔΔG in §2.9 is reported with its uncertainty explicitly labelled as an MBAR SE rather than a
replicate SD. The SD itself passes its own preregistered threshold (≤ 0.75); the calibrator fails on sign, not
on scatter.

**A control that could have explained the miss was run, and it does not.** In the original edge the binary
arm's ligand left its pocket in 8 of 12 replicas, so that ΔG was not a free energy of the intended bound state
and the cycle built on it was not strictly a cooperativity. That arm was therefore **re-run from scratch** with
a flat-bottom, λ-independent pocket restraint — λ-independent so it cancels exactly from ΔG(A→B), which is why
no standard-state correction arises (this is RBFE; the ligand is never decoupled) — writing to its own commit
prefix so it could neither resume nor overwrite the contaminated trajectory. The re-run landed, and the
reduction moved from **−0.534 to −0.522 kcal/mol: a shift of 0.012 against a miss of ~1.47.** Removing the
pocket-escape contamination changed the answer by **under 1 %** of the discrepancy. This is the single most
useful thing the calibrator has produced so far, because it eliminates the most plausible benign explanation
for the wrong sign by measurement rather than by argument.

**The miss is not a sampling failure, and the evidence for that is a full diagnostic battery that passes.** The
ternary leg reached **2000/2000** production iterations with MBAR **ΔG_morph = 47.511 ± 0.045 kcal/mol**;
λ-overlap is connected with minimum adjacent overlap **0.109** (floor 0.03); **N_eff = 676**; all 12 replicas
visit both end states; the ΔG(t) plateau is flat (full-vs-final-half **0.0023**). Replica mixing is **0.8915**
against a 0.90 ceiling — passing, but recorded as marginal. An apparent 78.9 Å → 14.97 Å solute RMSD excursion
is **periodic wrapping**, not a rearrangement (p50 2.50 Å, p90 5.91 Å, ~2 % of atoms displaced by ~one 126.3 Å
box edge; √(0.02·100² + 0.98·3²) ≈ 14.4 reproduces the observed value), so the ternary assembly is
structurally stable. A separately derived **ligand-only** pose RMSD — the ligand identified fail-closed from
bonded connectivity inside the trajectory, a single candidate among 141,968 partitioned particles, and
independently corroborated by an RDKit heavy-atom count from freeze time — gives **max 2.765 Å, median 1.644 Å**
against a 4.0 Å threshold, so the ligand did not drift out of the interface either.

**The forward/reverse antisymmetry check now returns a value, and it passes.** The reverse leg was for a period
structurally unreachable (four independent callers pinned the direction to forward); with that fixed, the
measured hysteresis is **|ΔG_fwd + ΔG_rev| = 0.325 kcal/mol against a preregistered ≤ 1.000 threshold — PASS**.
This was the **first of the three preregistered systematic-error detectors to return any value** (cycle closure has since returned one too, below), and its
reading is deliberately narrow: forward and reverse alchemical paths agree, so the miss is **not** a path or
hysteresis artifact. Per the identity argued in §2.9, a passing antisymmetry check is a *precision* diagnostic;
it is fully consistent with a large endpoint-state error and is **not** evidence that the cooperativity is right.

**The third detector — cycle closure — has now also returned a value, and it points the same way.** A
synthetic third vertex (cmpd4″) closes the triangle cmpd1 → cmpd4 → cmpd4″ → cmpd1, and the residual
`R = ΔΔG_coop(T1) + ΔΔG_coop(T2) − ΔΔG_coop(T3)` is **0.2128 kcal/mol**, inside the tightest plausible noise
floor (0.216 at σ_leg = 0.045) — decision `R_CONSISTENT_WITH_ZERO`
([`../modalities/valb-triangle-reduction.json`](../modalities/valb-triangle-reduction.json)). The reading is
that this workflow's ΔΔG_coop cycle is internally self-consistent to within |R| of **path** error, so the miss
is **not** explained by path error and more sampling will not fix it — the same conclusion the antisymmetry
check reaches, by an independent route. The two component closures are reported separately, never as `R` alone,
because a small residual can be two large closures cancelling: **R_ternary = −0.0312** essentially closes,
while **R_binary = −0.2440** is resolved against its 0.1528 threshold, upholding the prediction registered on
2026-07-26 (`BINARY_PATH_DEPENDENT`) that the binary arm — the one whose ligand left its pocket — would carry
the path dependence. Three limits travel with this number and none is incidental: it is **n = 1 by design**,
since one seed per edge is what makes a closure a closure and a mixed-seed triangle is a different quantity, so
**no error bar is quoted and none is constructed** from the per-leg MBAR SEs; at the σ_leg upper bound measured
from the n = 3 replicates the verdict is unchanged, but at the older assumed bound the same design reads
`UNDERPOWERED`, and that divergence is recorded rather than resolved; and closure bounds **internal
consistency, not accuracy** — it is structurally blind to exactly the endpoint-state classes named below.

**Taken together these give the load-bearing conclusion: the error is systematic, not statistical.** The
within-run statistical uncertainty (0.045 kcal/mol) is roughly **34× smaller than the miss** (1.543 kcal/mol at
n = 3).
Because replicates shrink variance and not bias, **more replicates cannot rescue this result** — a point worth
stating plainly, since the reflex response to a failed free-energy benchmark is to add sampling. The residual
error classes that a converged, structurally stable, antisymmetric calculation can still carry are precisely the
endpoint-state ones §2.9 showed a closed cycle to be blind to: the force field, the partial-charge method,
protonation/tautomer assignment, **the homology substitution in the receptor model**, and error in the reference
data itself. The partial-charge term enters as the *absolute* accuracy of one shared model and not as a
mismatch between the two arms: both arms' hybrid systems were read out of storage and carry the **same**
alchemical charges to the last serialised digit, so the model cancels from the cycle as intended (SI §S11).
Two of the classes are concretely elevated here: the SMARCA2 bromodomain is a **sequence substitution
into a 3.73 Å SMARCA4 parent structure** followed by relaxation (SMARCA2 crystallization having failed for the
original investigators too), and the target is derived from an SPR α-ratio whose own uncertainty is not
propagated into the ±1.0 kcal/mol margin.

**Those two elevated classes are not independent — they are one design choice, and a survey of the deposited
record measures what it cost.** Searching the PDB for ternary complexes on both arms of the SMARCA2/SMARCA4
pair returns the calibrator's own template, **8G1Q**, on the **SMARCA4** arm, and four SMARCA2 ternaries at
**2.24, 2.35, 2.70 and 2.84 Å** — every one of them better resolved than the 3.73 Å structure the calibrator
is built on. The substitution was nonetheless **not avoidable for this edge**: 8G1Q's deposition is
*"Compound 1 … bromodomain of human SMARCA4 and pVHL:ElonginC:ElonginB"*, so Wurz compound 1 — the calibrator's
`calib_hi`, and the compound whose SPR α values **are** the reference data — was co-crystallised only with
SMARCA4, while each deposited SMARCA2 ternary carries a **different** ligand (Compound 11, PROTAC 1, PROTAC 2,
P3). **Ligand identity and protein identity are coupled for this system**, and keeping the ligand whose
measurement defines the target forced taking the protein at the wrong paralogue and the worst resolution
available. Stated as a limitation rather than a fault: the choice was the defensible one, and the consequence
is that the calibrator's two most elevated error classes — the receptor model and the reference data — trace
to the *same* decision, which is why a closure residual that localises the miss to those classes cannot
separate them. It also fixes a requirement on any future calibrator: **choose a system whose reference
measurement and whose structure sit on the same protein.** *(Not established and not claimed: that a different
template would change this calibrator's answer. Nothing here tests the swap, and a shared deposition series
does not make two entries interchangeable.)* Record:
[`../modalities/s-calibrator-survey.json`](../modalities/s-calibrator-survey.json), in which every accession is
returned by the RCSB search API rather than typed.

**Status, stated without rounding up.** The calibrator's formal verdict is **FAIL**, and the decision is
**NO-GO**. It is no longer INDETERMINATE: that earlier status existed only because the preregistered rule needs
a between-replicate cycle SD that a single replicate cannot supply, and the replicates have now been run. The
change is in the completeness of the evidence, not in its direction — the sign was already wrong at n = 1 and
it is wrong in all three replicates. **All three systematic-error detectors have now returned a value.**
Antisymmetry passed; the replicate SD returned 0.375 kcal/mol, itself within its threshold; and cycle closure
completed on 2026-07-30 when the fourth and last leg landed, giving **R = 0.2128 kcal/mol**,
`R_CONSISTENT_WITH_ZERO`. The reducer had refused every partial cycle until then by construction, on the
grounds that an R from an incomplete cycle is a different quantity rather than a noisier one — so the value
exists only because all four legs exist. None of the three detectors indicates a sampling or path origin for
the miss.

**One caveat on the SD, carried rather than resolved.** The same reduction reports system identity as
INCONSISTENT because the ternary arm disagrees with *itself* across seeds: **144,447 particles at r1 against
141,740 at r2**, and 90,324 against 90,720 on the binary arm. The legs share a protocol hash, a charge method
(`nagl`) and a setup-cache version (`v1pe`), so this is independent solvation of the same protocol rather than
a different pipeline — but a replicate SD computed across systems that differ in water count is measuring
solvation variability alongside sampling variability, and we do not currently separate the two. The figure is
therefore reported as an upper bound on the sampling-only SD. A second caveat was registered in advance of the
replicates and now applies in fact rather than in prospect: the ternary starting-model index is
`seed mod n_models` at `n_models = 2`, so the third replicate returned to the first model's pose, and the
between-replicate SD across the three therefore **understates** homology-model variance.

**What this costs the rest of the paper, applied rather than noted.** §5's Tier-3 reading states that a positive
degrader-design result "stays exploratory until the known-answer ternary control passes." That control has now
been run and has **not** passed. The consequence is therefore in force, not hypothetical: **no cooperativity or
ternary-complex claim in this paper is calibrated**, the §2.10 degrader stage remains a prioritized candidate
matrix rather than a quantitative prediction, and the ternary machinery's demonstrated status is *converges and
is internally self-consistent on a real ternary system* — not *predicts measured cooperativity*. We regard
reporting this negative at full weight as more informative than the pilot it was meant to license.

### 2.12 The NR-V04 retrospective holdout returns DISCORDANT on the registered primary, and its three preregistered secondary endpoints are reported alongside it

§2.11 tested whether the alchemical machinery reproduces a measured *cooperativity*. This section reports the
other half of the same question — whether the **ensemble ternary workflow discriminates paralogues at all**
— on the one system where the answer is already known. NR-V04 (Wang 2024) degrades NR4A1 while sparing NR4A2
and NR4A3, so it is a biological holdout for exactly the discrimination every selectivity statement in this
paper depends on. The panel was preregistered in full — endpoints, direction, α, the unit of independence
and the tier definitions — before any leg ran
([`../modalities/nr4a3-nrv04-retrospective-prereg.md`](../modalities/nr4a3-nrv04-retrospective-prereg.md),
scored by the frozen `nrv04_retro_gate.py`).

**Design, and the confound it deliberately holds off.** NR4A1's Cys551 is **not conserved** in NR4A2 or NR4A3
(Tyr and Thr respectively, no cysteine within ±5 residues), so celastrol cannot form its covalent adduct on the
paralogues at all and a "three paralogues, same treatment" comparison would measure warhead chemistry rather
than ternary assembly. The authorized panel is therefore the **non-covalent** arms only, one per paralogue,
protocol-matched down to a single co-fold prefix and one code path — the contrast a prospective non-covalent
campaign would actually depend on. The covalent arm was retired on measured evidence (the C6→Cys551 adduct
measures **34.42 / 29.87 / 39.11 Å** on the three pinned NR4A1 co-fold models against an **8.0 Å**
admissibility limit — 0 of 3 pass, so it is unbuildable on every available input), and no covalent
NR4A2/NR4A3 leg exists or may be added — there is no cysteine to bond to, and modelling one would be
fabricating chemistry.

**Result on the registered primary: DISCORDANT.** The primary endpoint **E1** is the interface-RMSD plateau
(Å) — the mean RMSD of the E3∩target interface heavy atoms over the final 50 % of production frames, against
the starting interface, lower being more stable. Sixteen legs landed across 8 co-fold models
(n = 3 / 3 / 2 after a preregistered amendment excluded one NR4A3 co-fold on a **measured input fault**: two
heavy atoms placed 0.181 Å apart, a potential energy ten decades above control, both replicas dead at frame 0).
Arm means are **NR4A1 4.0977 Å, NR4A2 4.8435 Å, NR4A3 3.6852 Å** — NR4A1 is *not* the most stable arm, which
is the tier's stated criterion. The pooled one-sided exact permutation statistic is **−0.2825 Å at
p = 0.3929** over the **C(8,3) = 56**-arrangement reference set (α = 0.05, minimum attainable p 0.0179). The
emitted verdict, with its leave-one-model-out refits, its reverse-direction check and its registered
minimum-detectable-effect bound, is the one home for these numbers:
[`../modalities/nrv04-retro-verdict.json`](../modalities/nrv04-retro-verdict.json).

**What that does and does not license** is fixed by the prereg and we do not widen it. Discordance does **not**
falsify a ternary-first thesis: NR-V04's selectivity may arise from the covalent warhead chemistry alone —
which the sequence result is sufficient to explain — or downstream at ubiquitination rather than at ternary
formation. Nor is the null a finding of no difference: the design's registered 80 % power band is a
**1.5–2.0 Å** separation in interface-RMSD plateau, so what it licenses is *the workflow did not resolve a
paralogue difference of the magnitude this design can detect*, and nothing stronger. That band is itself an
**upper bound on the delivered power**: it was computed for the registered 3-models-per-arm design, and the
amendment that took NR4A3 to n = 2 deliberately registered no replacement, so the panel as run is blunter
still. No ΔΔG, α, cooperativity, affinity or degradation claim follows; this arm computes no free energy.

**The three preregistered SECONDARY endpoints, now reported.** Prereg §3 registered three secondaries and
promised they would be "reported alongside [E1] in every result, including when they disagree with E1". They
were not: the frozen scorer never reads them, and the criteria audit recorded the omission in as many words.
They are reported here, computed from the same 16 landed legs by the same frozen kernels, and read back from
the stored leg records rather than from a collector's summary
([`../modalities/nrv04-retro-secondaries.json`](../modalities/nrv04-retro-secondaries.json); per-leg tables and
the provenance census in **SI §S12**).

| id | preregistered definition | NR4A1 | NR4A2 | NR4A3 | reading |
|---|---|---|---|---|---|
| **E2** *(secondary)* | **stable fraction** — fraction of an arm's **legs** with plateau **< 4.0 Å** (threshold frozen before the feasibility panel ran) | **0.6667** (4/6) | **0.3333** (2/6) | **0.75** (3/4) | orders the arms **NR4A3 > NR4A1 > NR4A2** — the same ordering as E1, and likewise not the registered prediction. E2 **agrees with the primary's discordance**; it does not soften it |
| **E3** *(secondary)* | mean interface **contact count** over production (heavy-atom pairs within 4.5 Å) | **1571.62** | **2210.43** | **2125.25** | the degraded paralogue is the **least** contacted arm, not the most. Registered in advance as a **known weak discriminator** — the feasibility panel showed co-fold seeds contact in all arms — so it is reported and never gating |
| **E4** *(descriptive)* | Lys-Nζ **presentation distance distribution**: per frame, the minimum target-Lys-Nζ → catalytic-proxy distance | mean-of-min **34.52 Å**, mean-of-median **38.51 Å** | mean-of-min **24.84 Å**, mean-of-median **28.91 Å** | mean-of-min **31.13 Å**, mean-of-median **34.11 Å** | every arm sits **tens of Ångström** from the catalytic proxy, with no arm distinguished. **Descriptive only, never a gate** — no distance cutoff quantitatively predicts degradation, so no threshold is applied to E4 anywhere |

**⛔ None of the three was promoted, and that is a decision rather than an omission.** E1 is the registered
primary and, in the prereg's own words, *"the only one the verdict of §5 turns on"*. No secondary is allowed to
become a verdict, a tier condition or a substitute primary; none carries a p-value or a significance test in
the artifact or here; and the emitted tier is unchanged. E2 in particular is **not** leaned on: its motivating
observation ("recruiter_active 3/3 vs epimer 1/3") was **withdrawn** in 2026-07-24 forensics that found the
panel behind it had scored the Elongin C interface rather than VHL↔NR4A1 — the endpoint and its 4.0 Å
threshold are unchanged and were frozen before the panel ran, but E2 no longer has a demonstrated
discrimination behind it. We state the restraint explicitly so it cannot later be mistaken for oversight:
**gating on the friendliest endpoint is precisely the kind of retune this program forbids**, and reporting
these three was owed regardless of how they came out.

**Two limits of the secondary tests are structural, and both are stronger than "did not reach significance".**
First, the **NR4A1-vs-NR4A3 pairwise comparison is a non-measurement rather than a null.** At 3 versus 2
co-fold models the exact reference set holds **10** arrangements, so the smallest attainable one-sided p is
**0.10** — above α. The rejection region is empty: the test's exact size is **0.0** and its power against a
true separation δ of **any** magnitude is **exactly 0.0**. Its observed p of 0.70 could not have been small,
and it is reported as a comparison that could not have detected a difference of any size. Second,
**replicates could not have rescued either test.** Feeding the frozen scorer the landed panel at 2, 8, 20 and
100 legs per co-fold model — 16 legs through 800 — returns an **identical** reference set, statistic and
p-value at every count, because the scorer collapses a model's legs to their mean *before* the enumeration:
the unit of independence is the co-fold model, so the reference set is sized by models and replicates cannot
move it. What replicates *can* buy is bounded and small — the model-level σ the test competes against is
**1.0278 Å** and its irreducible between-model floor is 0.8312 Å, a ceiling of ~19 % on the noise infinitely
many replicates could remove. That σ has one home and the distinction matters: it is **not** the registered
leg-to-leg 0.855 Å nor the criteria audit's 1.1497 Å, and quoting either overstates the design's power
([`../modalities/selectivity-resolution-options.md`](../modalities/selectivity-resolution-options.md) §1a,
`which_sigma`).

**What this costs the rest of the paper, applied rather than noted.** The retrospective **was** the positive
control for selectivity detection — the one experiment meant to show that this workflow can discriminate
paralogues where the answer is already known — and it did not resolve. Together with §2.11's failed
cooperativity calibrator, the program therefore has **no demonstrated positive control** for either half of
the selectivity question, and every paralogue-selectivity statement in this paper is correspondingly
predictive rather than validated. A method calibrator on a structure-matched paralogue pair is the named gap,
and **it has now been run**: an endpoint-MD sensitivity control on **SMARCA2 vs SMARCA4** with the PRT3789
chemotype — a pair whose selectivity is measured in the primary literature and which has solved structures on
*both* arms, the property the retrospective's system lacks. Its criterion was frozen before the first GPU leg
([`../modalities/selectivity-sensitivity-control-prereg.md`](../modalities/selectivity-sensitivity-control-prereg.md);
`selcal_panel.PASS_CRITERION`).

### 2.12a The sensitivity control returns NULL on an adequately-powered design — the readout did not discriminate a paralogue pair whose selectivity is measured

**It did not detect the difference.** Scored against the frozen criterion on the complete panel
([`../modalities/selcal-verdict.json`](../modalities/selcal-verdict.json), which is the one home of every
figure here), the model-level interface-RMSD plateaus are **4.9684 Å (SMARCA2)** against **4.5311 Å
(SMARCA4)**, a statistic of **+0.4373 Å**. The primary source predicts SMARCA2 to be the *more* stable arm,
i.e. a **negative** statistic; the observed value has the **opposite sign**, and every one of the **11
leave-one-model-out refits keeps that sign**. It is nonetheless **not significant in either direction** —
exact one-sided *p* = **0.7468** in the predicted direction and **0.2554** on the mirrored test — so the tier
is **NULL**, not WRONG_SIGN.

⚠ **This is a real negative, not an underpowered one, and that distinction is the whole point.** The design's
own frozen adequacy clauses are all satisfied on the landed data: **zero technical failures in either arm**,
**22 admitted legs**, and an exact reference set of **462** label arrangements whose minimum attainable *p* is
**0.00216** — more than an order of magnitude below α = 0.05. The test *could* have returned a significant
result and did not. That is a stronger and less comfortable outcome than §2.12's DISCORDANT, which was a
non-resolution; here the instrument was given a difference the literature says is there, on solved structures,
at its own preregistered rigour, and returned nothing.

**Two legs of the designed 24 were excluded before scoring, on a measured input fault and not on an outcome.**
The SMARCA4 seed-3 co-fold places `A:LYS71:O` and `E:SER38:O` **0.693 Å** apart against a 1.00 Å floor, so the
pre-MD input audit refused it on every attempt — reproducibly, on five separate machines, before any dynamics
were integrated and therefore before any endpoint value for it existed. Both of its replicas died; both
replicas of every other model ran. The admissible panel is therefore **22 legs / 6 vs 5 models**, still above
the criterion's own per-arm floor of 4, which was written to survive exactly this
([prereg AMENDMENT 1](../modalities/selectivity-sensitivity-control-prereg.md#amendment-1--2026-08-02-measured-input-fault-smarca4-model-3)).
The one other unfinished unit at that moment audited **clean at 1.2994 Å** and was **re-run rather than
excluded**, which is what distinguishes an input-fault exclusion from trimming a panel to taste. The unbalanced
arms cost **power, not validity** — the exact test enumerates the arrangements that exist — and that direction
is adverse and was recorded before the result was known.

**What it licenses, in the words written in advance.** The failure sentence was fixed before the run
([`../modalities/selectivity-resolution-options.md`](../modalities/selectivity-resolution-options.md) §4) so
that it could not be re-narrated afterwards: *the workflow's paralogue-discrimination authority rests on
nothing this program has measured, and every NR4A3 selectivity statement in this paper is reported as an
**unvalidated prediction**.* ⛔ It licenses nothing further. In particular a fail **does not distinguish "the
readout is blunt" from "this pair is hard"**, and must not be reported as though it did — SMARCA2/SMARCA4
bromodomains are ~80 % identical and the published selectivity is driven by a single Gln1469 hydrogen bond,
so a null here is consistent with both an insensitive endpoint and a genuinely narrow structural signal. It
re-scores no leg reported above, and it changes no ΔΔG.

⚠ **A THIRD READING, MEASURED AFTER THE FACT, AND IT WEAKENS THIS RESULT RATHER THAN RESCUING IT.** The two
readings above were the only ones registered, and they share an assumption nobody had checked: that the
simulated complexes were the complexes whose selectivity was measured. They were not. Scored against the
deposited ternaries the panel was designed around — 9DTY and 9DTX, chosen precisely so that *"each arm's
co-fold can be validated against a real structure of the very complex it models"*, a comparison that was
**never** run at the time — all twelve starting
structures reproduce the **internal VHL/Elongin B/Elongin C machinery at DockQ 0.89–0.97** and the
**degradation-target↔VHL interface at DockQ 0.023–0.046 with fnat 0.000**, i.e. not one native interface
contact recovered on either arm. Two independent implementations agree, one of them the canonical DockQ
([`../modalities/selcal-cofold-vs-crystal.json`](../modalities/selcal-cofold-vs-crystal.json),
[`../modalities/selcal-cofold-dockq.json`](../modalities/selcal-cofold-dockq.json)).
⛔ **This does not convert the null into a positive result and must never be read that way.** It says the
endpoint was never exercised on the complexes in question, so the null bounds the *workflow as run* and not
the readout in isolation — the instrument claim is weaker than the two registered readings imply, not
stronger. The consequence for this paper's language is unchanged: every paralogue-selectivity statement
remains an unvalidated prediction. What it does change is where the failure sits — at ternary **generation**
rather than at ranking — which is a statement about this co-folding pipeline on a VHL neosubstrate interface
and about nothing else.

**Both halves of the control that a near-zero score requires, so it is a measurement and not an artefact of
the scorer.** A DockQ of 0.03 invites two objections, and each was answered by running it rather than by
argument.
*Does anything score high through this harness?* DeepTernary, a dedicated SE(3)-equivariant ternary
generator, run on `6HAX_B_A_FWZ` — a VHL/SMARCA2 PROTAC ternary supplied as complete unbound inputs in its
own released benchmark — reaches **DockQ 0.618 (CAPRI "Medium"), median 0.438 over 16 scored poses, best
interface-RMSD 1.21 Å**, from the same DockQ 2.1.3 build that returns 0.023–0.046 above
([`../modalities/selcal-deepternary-poscontrol.json`](../modalities/selcal-deepternary-poscontrol.json)).
⛔ That case was deposited in 2018, inside the model's 2023-10-14 data horizon, so it is memorisation-
permitting by construction: it is a **positive control on the harness and the instruments**, and is not
evidence of generalisation, of anything about NR4A3, or of anything about degradation or selectivity.
*And how wrong is 0.03?* Holding VHL fixed and displacing the **true** target chain of 9DTY by a rigid motion
of known magnitude — every side chain, every contact, the right protein, the right copy, placement the only
variable — gives DockQ **1.000 → 0.948 (0.5 Å) → 0.845 (1 Å) → 0.717 (2 Å) → 0.401 (4 Å) → 0.240 (8 Å) →
0.085 (16 Å) → 0.026 (32 Å)**
([`../modalities/selcal-dockq-decoy-scale.json`](../modalities/selcal-dockq-decoy-scale.json)). The co-folds'
0.023–0.046 sits at the bottom of that ladder: **they score like the correct structure displaced ~32 Å**,
which is consistent with the 17.8–21.2 Å interface-RMSD measured independently. So the co-folds are not a
near-miss on placement, and the failure at generation is not a matter of degree.

★ **AND THE COMPLEX ITSELF IS RECOVERABLE IN SILICO, WHICH LOCATES THE FAILURE PRECISELY.** Run on **9DTY** —
the SMARCA2 arm's own deposited ternary, absent from DeepTernary's disclosed 4,471-entry exclusion set and
deposited well after its 2023-10-14 data horizon — the same generator reaches **DockQ 0.839 (CAPRI "High"),
interface-RMSD 0.67 Å, fnat 0.83**, best of 16 seeds, median 0.442, against our co-folds' best of 0.038 on
the same interface and the same reference
([`../modalities/selcal-deepternary-headtohead.json`](../modalities/selcal-deepternary-headtohead.json)).
⛔ **It is not the same question our co-folds were asked, and the two numbers are not interchangeable.**
DeepTernary's published *unbound* protocol superposes the two unbound binary structures into the native
ternary frame and supplies the native degrader pose, so the model is given **which pocket on each protein
each end of the degrader occupies**; what it predicts is the two proteins' **relative placement**, which is
randomised out of its input (protein 2 and the ligand are each independently rotated and translated before
the forward pass). Our co-folds were given sequence and ligand and nothing else. ⚠ Reported as best-of-16 and
as **one arm**: the SMARCA4 arm was refused before any prediction, its best available warhead fragment
sharing 0.42 of its heavy atoms with the degrader against a 0.55 bar, and no SMARCA4 number exists.
What this does establish, and it is the reason the paragraph above is a diagnosis rather than a shrug: this
ternary is **not beyond in-silico reach** — with the two binding sites supplied, a dedicated ternary
generator places it to within 0.67 Å at the interface. The 0.023–0.046 is therefore a property of the
sequence-only co-folding route used here, not of the problem.

★ **AND THE FAILURE IS LOCALISED: THE TWO HALVES ARE APPROXIMATELY RIGHT, THE ASSEMBLY IS NOT.** Superposing
each co-fold on one protein at a time and measuring the degrader's deviation over the native atoms contacting
*that* protein — correspondence through the reference molecule's own atom graph, never by proximity — all
twelve place the degrader within **3.2 Å** of its crystal position in each protein's own frame (target-side
median **1.83 Å**, E3-side median **1.96 Å**), while the assembled interface scores what the true complex
scores when displaced **32 Å**: a factor of **10**
([`../modalities/selcal-cofold-decompose.json`](../modalities/selcal-cofold-decompose.json)). So each
protein's ligand pocket is occupied roughly as the crystal has it, and what fails is the **relative placement
of the two proteins** — which is precisely the information a ternary generator is handed when it is given
each end's site, and the configuration that reached 0.839 above. ⚠ The locus is decided against that measured
displacement scale rather than a threshold chosen here; where the scale cannot be read, the artifact reports
the locus as undetermined rather than guessing it.

★★ **AND A PARALOGUE-SELECTIVITY READOUT THAT PASSES A KNOWN-ANSWER TEST — the first this program has.**
The published mechanism for this pair is not a dynamical quantity: Kofink et al. 2022 (PMC9551036) report
*"the selectivity-inducing hydrogen bonding between Gln1469 of SMARCA2BD and VCB"*. A bond between two named
partners is visible in a deposited structure, so the question can be put to a static interface descriptor on
the two crystals, at no cost, against an answer published before this program existed. Scoring the
target↔VCB contact map of 9DTY and 9DTX and aligning the two bromodomains **by sequence** (they are numbered
in their own full-length proteins, so equal numbers are different residues; interface-alignment identity
0.890), the descriptor finds exactly one position where a glutamine on the SMARCA2 arm makes a **side-chain**
polar contact to VCB that the aligned SMARCA4 residue does not: **Gln98 Oε1 → VHL Arg12 Nη2 at 2.88 Å**
(34 interface contacts), against **Leu1545** on SMARCA4 (10 contacts), which cannot make that bond at all
([`../modalities/selcal-interface-signature.json`](../modalities/selcal-interface-signature.json)).
⚠ **Side-chain, not any polar contact** — SMARCA4's leucine does touch the E3 through its *backbone* amide
(2.93 Å), and counting that hides the substitution behind an interaction of a different kind. ⚠ No hydrogens
are placed at these resolutions, so "polar contact" is the standard heavy-atom donor–acceptor proxy and is
labelled as one throughout. ⛔ **What this licenses is narrow and is stated here rather than left to be
inferred:** a *structural* paralogue-discriminating contact is detectable from a ternary structure, and this
descriptor detects the one that was published. It validates **one contact in one pair**. It does **not**
validate E1 — a different quantity, still untested on correct inputs — and it makes **no NR4A3 prediction
correct**; applying it to an NR4A3 ternary additionally requires that ternary to be credible, which the
paragraph above shows is not yet the case for this route.

**Applied, not noted:** with §2.11's cooperativity calibrator failed on sign, §2.12's retrospective
non-resolved, and this control null on an adequately-powered design, **all three** attempts to establish a
positive control **for this program's selectivity claims** have now been run and none succeeded — a
statement about the *selectivity* endpoint that the harness control above does not touch and must not be
read as softening. The consequence
is stated in **three** places, not one — the **Abstract**, this section, and **§4 Limitations** — so that a
reader who never reaches the limitations still meets it. It is a scope statement about the whole workflow, so
it is carried at those three levels rather than appended to each individual ΔΔG, which would say the same
thing twenty times and dilute it.

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
**Required change (the harmonized rerun — now run and committed).** Because the reference site was chosen as the
highest-*druggability* pocket in a residue window that is essentially the whole LBD, the foundational site
identity is **partly outcome-selected**. The submission-gate fix is to define the orthosteric site **without
using the fpocket score** — from a fixed, prespecified set of canonical NR ligand-pocket residues (mapped by
structural alignment to homologous NR orthosteric sites) — then detect cavities, match to that region under a
composite Jaccard + fraction-recovered + centroid gate (replacing the ≥1-residue rule), and read druggability
only afterward, under one pinned fpocket build across the reference panel, AF2, all 20 8XTT conformers, the
three metad replicas, and the three release replicas. **That rerun has been executed and is committed**
([`../modalities/nr4a3-pocket-reharmonize-summary.json`](../modalities/nr4a3-pocket-reharmonize-summary.json);
fpocket pinned to 4.0, match gate jaccard ≥ 0.25 / fraction-recovered ≥ 0.3 / centroid ≤ 8.0 Å, both
denominators reported): AF2 static 0/1 ≥ D\*, the 8XTT ensemble 3/19 detected frames (3/20 propagated), the
metadynamics frames 17/25, and the three release replicas 14/25, 10/25, 20/25 (44/75 pooled). **Dependency
audit — still open.** Because the generative campaign was conditioned on a receptor frame selected by the
*provisional* classifier, the rerun must additionally confirm that the **exact release-derived frame used to
generate `denovo_401` still qualifies as the same mapped orthosteric site and still exceeds D\***. The
committed harmonized artifact reports **ensemble-level** fractions only and does **not** identify which
individual frames cleared D\*, so this frame-level dependency check is **not** discharged by it and remains a
submission gate (§4); if the generation frame does not qualify, the generation receptor — not merely a
reported frame-fraction — is affected.
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
per-receptor ΔG_bind, the two ΔΔG contrasts, the unanimous direction, and the provisional-NR4A2 caveat). **Full FEP diagnostics are in SI §S7** (per-replicate paired ΔΔG table, λ-overlap matrices, effective sample sizes, forward/reverse convergence traces). **Artifact pointer (read this carefully — the path is version-pinned).** The diagnostics JSON for the three-replicate AF2-conditioned run is `results/nr4a3-abfe/diagnostics/nr4a3-abfe-diagnostics.json` **as committed at git `b4b8e217`** (tags `nr4a3-abfe`, `-r2`, `-r3`; 12 λ-windows × 2000 samples per leg); the file **at that same path in the current working tree has since been overwritten** by a later, unrelated λ-repair pilot scoped to the `nr4a3-abfe-nr4a2rep-*` tags, which contains only partial complex legs, no solvent legs and no ΔG_bind, and therefore does **not** support any number in this paper. The overlap/ESS/convergence PNGs for the three original replicates (`*_nr4a3-abfe.png`, `*-r2.png`, `*-r3.png`) were not overwritten and remain in the tree. Against the `b4b8e217` JSON the reduction is reproducible: it recomputes these ΔG_bind from the raw reduced potentials with a maximum absolute deviation of **0.022 kcal/mol** across all ten checked means and SDs (its own `manuscript_consistency` block records `consistent: true`), which is the basis for the ≤0.03 kcal/mol statement. On overlap, the honest picture is **not** a single localized exception: median adjacent overlap per leg is ≈0.13–0.22, but **every leg — including the shared solvent leg and all three NR4A3 complex legs — has at least one soft-core-tail window pair below 0.03**, with per-leg minima spanning **0.003–0.027** (worst: complex-NR4A2 in r3, 0.0034). The defect is therefore **systematic across the λ-schedule's decoupling tail, not NR4A2-specific**, so the same λ-repair caveat applies to *all* absolutes and to *both* ΔΔG contrasts; NR4A2 is singled out in §2.8 only because it is the worst case and because a receptor-specific complex-leg error does not cancel in ΔΔG(3−2). We do not report calibrated absolute ΔG_bind. The engine mis-predicts a rigid textbook benchmark
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

**Relative-FEP pipeline — independent known-answer validation (2026-07-17).** Separately from the absolute
(ABFE) scale above, the same OpenMM/OpenFE infrastructure's **relative binding FEP** path —
`RelativeHybridTopologyProtocol` (Hamiltonian replica exchange), the standard engine for congeneric ΔΔG and the
tool any relative warhead campaign would rely on — was validated end-to-end against a **public known-answer
edge**: the TYK2 congeneric pair `ejm_31→ejm_42` from the OpenFE protein–ligand benchmark, at full sampling
(5 ns/window × 12 λ-windows, am1bcc charges, CUDA) on the GCP-Spot L4 pipeline (`gpu-rbfe-gcp.yml`). It
reproduced the experimental relative binding free energy — **ΔΔG_bind = +0.37 vs experimental −0.24 kcal/mol,
absolute error 0.61 kcal/mol** — inside the ~1 kcal/mol chemical-accuracy band and consistent with OpenFE's
published accuracy for this protocol. This is a **build-consistency check on the relative-FEP path** (it does not
touch NR4A and makes no NR4A3 claim), but it establishes two operationally relied-upon facts: our container
reproduces a known ΔΔG — i.e. the *relative*-FEP tooling is sound, in explicit contrast to the un-calibrated
*absolute* scale above — and the **spot-safe GCS checkpoint/resume infrastructure** carries a multi-hour FEP
through repeated real spot preemptions with zero lost work (relevant to any future large FEP fan-out).

**Measured throughput on the NR4A3 system itself (2026-07-24).** The TYK2 validation above is a *build*
check, and its timings do not transfer: on the real cmpd19/NR4A3 congeneric complex, three independent RTX-4090
hosts sampled at **12.76 / 13.70 / 14.42 s per Hamiltonian-replica-exchange iteration** (16 samples each;
12 λ-windows, 2.5 ps/iteration), i.e. **≈190 ns/day aggregate versus ≈498 ns/day for the public TYK2 edge on the
same card class** — the NR4A3 hybrid is ~2.6× more expensive per unit of sampling. Effective protocol settings,
read off the built system rather than assumed, are OpenFE's defaults `constraints=hbonds` with
`hydrogen_mass = 3.0`, under which every X–H is constrained and the integrator runs at 4 fs. These figures are
reported so that anyone costing a comparable campaign prices it on the *target* system: a per-iteration rate
measured on a benchmark system underestimated this one ~4-fold.
**Artifact status:** the run is GitHub Actions run **29566859637** (2026-07-17) and its outcome is recorded in the
committed run ledger `../manuscripts/degrader-paper-schedule.json` (record `valA_mini`: `ddg_bind=+0.366`,
`ddg_exp=-0.24`, `abs_err=0.606`, solvent-leg ΔΔG 13.703 ± 0.079). The raw result object lives in a **private
GCS checkpoint bucket** (`gs://<gcp-project>-rbfe-ckpt/valA-tyk2/results/ddg_nr4a3.json`; note the filename is a
harness artifact — the calculation is TYK2, not NR4A3) and is **not committed to this repository**; it must be
exported into the deposited archive before submission.

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
A confirmatory alchemical-mutation cross-check is **no longer blocked on tooling**: an alchemical
protein-mutation FEP engine (pmx + GROMACS; equilibrium λ windows reduced with BAR) was implemented and, on
2026-07-25, **passed a known-answer benchmark** on the barnase–barstar interface at 3 × 3 replication —
**Y29A +4.42 ± 1.08** against a SKEMPI-verified +3.40 (abs err 1.02) and the near-null control **Y29F
−0.37 ± 0.18** against −0.13 (abs err 0.24), both inside a ±1.5 kcal/mol tolerance and correctly ordered.
Two properties of that benchmark bear directly on whether such a cross-check would be interpretable here, and
both are reported because they cut in opposite directions. (a) **Between-setup scatter is effect-size
dependent by ~6×** — ±1.08 on the +4.4 kcal/mol hot-spot knockout versus ±0.18 on the near-null — while
*within*-leg MBAR standard errors are 0.05–0.13 kcal/mol in both, i.e. an order of magnitude smaller. The
variance is therefore in setup/equilibration, not sampling length, so single-replicate mutation ΔΔG values are
not interpretable and replicates are mandatory. (b) **No benchmark yet probes the regime this cross-check would
occupy** — resolving ~1 kcal/mol between two closely related receptor states — so the engine is validated for
seeing a large effect and for not inventing one where none exists, but *not* demonstrated to resolve a small
paralogue-scale difference. The cross-check accordingly remains future work, now gated on that missing
wedge-scale benchmark **and** on the pocket-homology assessment noted in
[`../method-watch.md`](../method-watch.md), rather than on engine availability. **Receptor prep for
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

**Mechanism-first prospective stage (§2.10).** All CPU, no GPU; the network-touching steps run on free CI
runners because the development environment's egress proxy blocks the structural and sequence databases.
*Paralogue-unique residues* (`nr4a_paralogue_unique_residues.py`): full-length UniProt sequences for NR4A3,
NR4A1, NR4A2 and the EWSR1 fusion partner [50], aligned by two independent aligners with **agreement
required** — a position on which the aligners disagree is excluded rather than adjudicated — then intersected
with matched-model solvent exposure. *Handle ensemble* (`nr4a3_handle_ensemble.py`): the identical
Shrake–Rupley routine [71] and the identical reach calculation applied per-frame to the 100 committed NR4A3
conformers of §2.3, with the 25 biased metadynamics frames reported separately and **never pooled** with the
75 bias-free frames. *E3 recruiter staging* (`e3_recruiter_staging.py`): RCSB search by UniProt accession with
a fail-closed exact-match guard that refuses rather than substituting a plausible accession; coordinates read
from **biological assembly 1**, not the asymmetric unit; occluders restricted to the recruiter plus its own
CRL arm with every removed chain recorded; burial by [71], cavity volume by a LIGSITE protein–solvent–protein
scan [72], and an exit vector taken as the **solid-angle centroid of the near-maximal rays** from the
most-exposed ligand heavy atom rather than the single maximal ray, since a wide mouth ties dozens of rays and
an argmax would return an iteration-order artifact. *Basin search* (`nr4a3_basin_search.py` + `basin_geom.py`,
pure standard library, 35 unit tests each against a closed-form or hand-constructed answer): NR4A1/NR4A2 are
placed into the NR4A3 frame by quaternion superposition [73] with iterative outlier rejection, so a single
sampled set of E3 placements is scored against all three paralogues and a paralogue difference cannot be an
artifact of three separate searches; every paralogue lysine carries its own post-fit deviation and a
reliability flag, and a covered-but-unreliably-placed lysine is reported separately rather than counted.
Linker reach uses the exact prolate-spheroid criterion — a chain of contour length *L* tethered at exit
vectors **a** and **b** can route through **p** only if |p−a| + |p−b| ≤ *L* — which is what makes reaching a
cysteine and spanning to the E3 compete for the *same* budget; accessibility uses a worm-like-chain
end-to-end density rather than a Gaussian chain, because real degrader linkers are 3–16 backbone atoms and a
Gaussian assigns non-zero probability *beyond* the contour length, i.e. exactly where the answer matters
(primary reference for this distribution to be established, see References). Clustering is on the **interface
fingerprint** the scored terms depend on, rather than on the RMSD between placements' reference points: at an
~18 Å recruiter radius an 8 Å reference-point RMSD corresponds to only a ~25° rotation, and just 0.09 % of
accepted placement pairs fall inside it, so RMSD clustering returned zero basins and would have needed
~10⁷–10⁸ placements per arm. The lysine-identity term is scored
against a background null computed over the **unclustered** accepted set — the same population the basins
were drawn from, with only the enriching step removed — and a basin must exceed it; the electrophile term
carries the analogous control of scoring the **conserved** cysteines by the identical rule. Both terms are
read at a practical 12-backbone-atom linker rather than at the 20-atom sampling ceiling, where the focal-sum
criterion admits almost any nearby cysteine and the gate could not fail. *Linker design*
(`linker_design.py` + `nr4a3_linker_design.py`, 52 tests; `linker_chem_check.py` for verification) computes
the exact three-ball branch-position window at integer backbone positions and emits SMILES by assembly, then
**re-derives** length and branch position from the parsed molecule by topological shortest path between the
two anchor atoms; a mismatch, a forbidden junction motif, or an unassigned stereocentre **fails the build**.

## 4. Limitations
**⛔ THE LIMITATION THAT CONDITIONS EVERY SELECTIVITY NUMBER IN THIS PAPER: there is no working positive
control for paralogue-selectivity detection, and this is now a measured finding rather than an untested
assumption.** Three attempts have been run and none succeeded — the ternary cooperativity calibrator returned
the **wrong sign** systematically (§2.11), the preregistered NR-V04 retrospective returned a **non-resolution**
and is covalency-confounded so it could never have served at any *n* (§2.12), and the sensitivity control
purpose-built to be free of both defects — a paralogue pair with measured selectivity and solved structures on
*both* arms — returned **NULL on an adequately-powered design** (§2.12a; *p* = 0.7468, reference-set floor
0.00216 against α = 0.05, zero technical failures). **Every paralogue-selectivity statement in this work is
therefore an unvalidated prediction.** Two things this does *not* license, both stated because the opposite
reading is the tempting one: it does **not** distinguish an insensitive readout from a genuinely narrow
structural signal, and it does **not** retroactively invalidate any individual ΔΔG — it removes the evidence
that the workflow producing them can resolve a paralogue difference at all, which is a different and broader
claim. ⚠ **And a third limitation, measured after the fact, sits upstream of all of it:** the sensitivity
control's starting structures were subsequently scored against the deposited ternaries the design was built
around and reproduce the **target↔VHL interface at DockQ 0.023–0.046, fnat 0.000**, while reproducing the
internal E3 machinery at 0.89–0.97 (§2.12a). The endpoint was therefore never exercised on the complexes
whose selectivity was measured, which makes that null a bound on the **workflow as run** rather than on the
readout in isolation — weaker evidence about the instrument than the registered readings imply, not stronger,
and no basis whatever for re-opening any selectivity claim. Both halves of the control that number needs have
since been run (§2.12a): the same DockQ build returns **0.618, CAPRI "Medium"** for a dedicated ternary
generator on a known complex, so the near-zero score is not an artefact of the scorer; and displacing the
**true** target chain of 9DTY by a known rigid magnitude puts 0.023–0.046 at the **~32 Å** rung of the ladder,
so the co-folds are not a near-miss. And on 9DTY itself — post-horizon for that generator — the same run
reaches **DockQ 0.839, CAPRI "High", interface-RMSD 0.67 Å** when the two binding sites are supplied, so the
complex is **not beyond in-silico reach** and the near-zero score is a property of the sequence-only route
used here rather than of the problem. ⛔ None of that is a positive control for paralogue-selectivity
*detection* — that endpoint still has none, the recovery answers a **different and easier question** than
our co-folds were asked (it is given each end's pocket; they were given sequence alone), and none of it may
be read as softening the paragraph above.

In-silico throughout; no molecule synthesized; broader indications (SI §S4) are **motivation, not
demonstrated efficacy**. Therapeutic application to EMC (and AciCC) additionally **assumes NR4A3 dependence, which is not tested here**: the supporting prior (a transfer prior from fusion-addicted EWSR1/FET sarcomas; EMC-native evidence the fusion is a functional driver; a near-invariant clonal fusion in a quiet genome) and the **one decisive gap** (no loss-of-function experiment in any EMC model — the make-or-break dTAG test is delegated to the EMC-program paper), together with the systemic-lead safety/tolerability rationale and the pan-NR4A/CAR-T pole, are in **SI §S9** (safety in **SI §S6**, indications in **SI §S4**). This paper's claimed contribution is the target's **computational druggability/selectivity, not EMC efficacy**.
The structure is an AF2 model
(NR4A3 has no ligand-bound experimental structure; its apo LBD was released as a solution-NMR ensemble,
PDB 8XTT, only in 2025) — the MD addresses exactly the single-snapshot limitation. **The 8XTT benchmark
is done (§2.1) and is two-sided:** the experimental apo ensemble is structurally *heterogeneous* at the
mapped site (most conformers occluded; under the harmonized tracker the site is matched in 19/20 conformers, of
which **3 exceed D\*** — 3/19 among detected, 3/20 across all deposited; structural corroboration, not a
population estimate),
**but** the AF2 atomic pocket geometry *diverges* from it (pocket-local Cα-RMSD 3.56 Å, handle 3.44 Å). Two
prediction *directions* transfer to 8XTT conformers (PocketMiner enrichment, denovo_401 MM-GBSA preference),
so the site's existence and those directions are corroborated while the AF2 *opened geometry* is not.
**A full workflow rebase and the review-warranted controls remain to do**: (i) an 8XTT-*started*
metadynamics/MD and generation (not yet done here), and an **8XTT-anchored ABFE** — of which the **NR4A3 leg
is done** in triplicate (+8.17 ± 0.98, §2.8) but the **matched NR4A1 and NR4A2 legs are not**, so the
8XTT-anchored *selectivity* contrast does not yet exist and the reported ΔΔG values remain
AF2/opened-conformer-conditional; (ii) a **matched 8XTT-frame decoy null** (denovo_401 + the 38
decoys through the same 4 conformers, since we have shown MM-GBSA margins are frame-dependent); (iii)
PocketMiner + docking over **all 20** conformers (not only the 4 cavity-bearing ones), with an AF2↔NMR
vs NMR↔NMR RMSD decomposition and a true residue-contact-graph spatial-patch null; (iv) **repair of the
under-overlapped ABFE windows** — note this is *not* a single window: every leg (solvent and all three
complex legs) has at least one soft-core-tail pair below 0.03 (§2.8), so the dense-schedule repair must cover
all four legs, and the one repair pilot attempted so far (NR4A2 leg, tags `nr4a3-abfe-nr4a2rep-*`) **did not
complete and produced no ΔG**. This item is **held, not queued** — repairing the error bars would not lift the
two limits that actually bound the ABFE block (no validated absolute scale; conditional on the chosen opened
state), so it is not the next computation this program should buy.
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
   fraction of frames of all three replicas** (≥ D\* in 0.56/0.40/0.80, harmonized tracker; pocket detected in
   75/75 frames, so detected-frame and all-frame denominators coincide) — correlated,
   open-seeded, non-equilibrium frame fractions (**not** an equilibrium population), and explicitly **not** a
   demonstrated static always-open pocket. The calculations do not
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
   affinity + a productive exit vector.
   ⚠ **A conclusion previously drawn here is withdrawn as an overclaim in the negative direction.** This
   caveat used to state that sourcing paralogue selectivity from the ternary "**has now been tested and does
   not materialize**", on the basis of the representative-PROTAC co-fold in §2.5. That inference is not
   available from that experiment: §2.5 establishes, from its own failed stereochemical control, that the
   co-folding classifier is **unsuitable for binding, ternary-stability, degradation-selectivity or
   linker-ranking claims**, and a method that may not rank ternary selectivity may not conclude ternary
   selectivity is absent either. What §2.5 supports is the weaker and correct statement it already makes:
   **one representative, arbitrarily-linkered construct did not *provide evidence for* an NR4A3-selective
   ternary geometry** — an absence of evidence at a tier that cannot produce the evidence, not a negative
   result. Accordingly the ternary is **not** written off as a selectivity lever here, and §2.10 reports the
   stage that actually interrogates it: paralogue discrimination is searched first on **categorical** handles
   (a nucleophile and lysines the paralogues do not possess), because the induced-interface margin the co-fold
   was being asked about needs ~2.0 kcal/mol and is not decidable by any tier this paper runs, let alone by a
   structure-only classifier. *(That re-ordering was originally argued against a best-case resolvable ~1.12
   kcal/mol; **that figure is superseded** — §2.10 carries the measured replacement and the reason the
   conclusion here is unchanged, which is that the binding limit is accuracy rather than resolution.)* That
   search **nominates**; it does not settle the question, and the causal test remains unrun.
   Degradation selectivity therefore rests, on current evidence, on the **binder** margin plus those
   nominated categorical handles (plus
   **pharmacokinetics** for NR4A2: CNS exposure is an additional design concern given NR4A2's established
   dopaminergic biology, **but the distribution of toxicity from NR4A2 loss is not established here**
   (§4/SI §S6)); and **fusion-vs-wild-type**
   selectivity remains **unobtainable from the degrader** (route to the ASO).
6. **The carried candidate is a chemotype/pose hypothesis, not a synthesized or affinity-validated molecule.**
   `denovo_401` passes the in-silico property/alert filters (§2.7), but remains a docking/endpoint/ABFE-tier
   prediction on an AF2-derived pocket, unsynthesized and un-validated. The durable claim is the
   **falsification-controlled funnel** and the surviving selectivity *direction*, not a developable molecule.
   (Detailed forensic records of the retracted single-snapshot candidates — denovo_15/94/57 and the
   protonation-sensitive denovo_111 — are in **SI §S8**; the main text retains only the falsification sequence
   needed to explain candidate advancement.)
7. **Single-snapshot MM-GBSA is non-specific; multi-snapshot de-noising AND its matching decoy
   re-scoring are now run, and `denovo_401` clears them — leaving ABFE as the last tier: initial
   three-replicate ABFE complete, and the λ-overlap repair **held, not pending** (§2.8).** The de-novo
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
   frame it was *not* designed for). The purpose-built control for that gap — the **generation-matched null**
   — has run one of its three arms (scrambled objective, isolating the best-of-N selection step): it
   manufactured no survivor, but a zero out of 191 generations only bounds the manufactured rate at ≤ 0.0157
   against the real campaign's own 0.0052, so it **narrows the confound without excluding it**, and the
   paralogue-pocket generation arm that would speak to the generative step directly is **not run** (§2.7);
   and (b) a **fully
   criterion-matched re-dock** (NR4A3 metad-opened) — `denovo_401` stays NR4A3-favoured (+7.44 ± 4.18), confirming
   the *direction* is not a release-frame artifact, though the magnitude is frame-dependent. **The matching
   metad-frame decoy null was then run (§2.7) and, honestly, `denovo_401` does *not* clear it**: in the biased
   metad-opened frame the decoy null balloons (95th +17.70, max +24.74, driven by drugs like diphenhydramine
   +24.74) and +7.44 sits at only ~the 84th percentile — so the metad-opened frame is a poor discriminator, but
   it is also the frame `denovo_401` was *not* generatively fit to, so the above-null result is
   **release-frame-specific (= design-frame-specific)**, not universal. What remains is
   **single-trajectory GB-implicit MD, not ABFE**, so **selectivity ABFE is the quantitative gate — initial
   three-replicate ABFE complete (three-replicate ΔΔG NR4A3-favoured; NR4A2-sparing resolved below zero,
   NR4A1 unanimous in direction but not resolved from zero), with the dense-schedule λ-overlap repair
   **deliberately held rather than queued** — it is parked, not in flight, and repairing error bars would not
   lift the two limits that actually bound the block (no validated absolute scale; conditional on the chosen
   opened state) (§2.8)**;
   the receptor-frame dependence is best resolved by ensemble scoring over the druggable release sub-ensemble.

8. **The mechanism-first prospective stage (§2.10) is a nomination with four limits that bound it, and one
   of them is a single point of failure.** *(a) The categorical chemistry axis is one residue deep.* C397 is
   robust in the receptor ensemble, but C420 and C559 are unreachable at the practical gate in every unbiased
   conformer, so there is **no geometric fallback** — and the untested failure modes for C397 are **chemical,
   not geometric** (thiol pKa, nucleophilicity, adduct stability, and electrophile promiscuity), none of which
   this or any other in-silico step here tests and the last of which requires chemoproteomics. The only hedge
   is the independent unique-**lysine** axis, which raises the odds without guaranteeing a paralogue is
   spared: real degraders often ubiquitinate several lysines, and lysine-less substrates can still be degraded
   through N-terminal, Ser, Thr or Cys ubiquitination. A covalent handle is therefore an **unresolved
   liability, not an upgrade**, and must be reported together with the parent cmpd19 chemotype's own
   **MYC de-repression** — parent-warhead pharmacology is a potential liability, not evidence of benefit.
   *(b) The nominations are rigid-body.* Rigid side chains, no solvation, no induced fit, LBD-only models
   (hinge, DBD and fusion-partner lysines absent), one static opened conformer per paralogue **for the
   interface — no longer for the categorical reach test, which now runs over 100 matched conformers per
   species (§2.10)** — and an ideal semi-flexible-chain strain estimate that is not a force-field energy. A basin is a
   region of orientation space that *admits* a mechanism, not a modelled complex; whether a linker's conformer
   population actually visits the branch position that presents the electrophile is **unmeasured**. *(c) The
   double conditionality is the binding one.* Everything rests on the hypothesized cmpd19 binary pose × the
   chosen receptor frame, and no cmpd19 pose exists in the matched-model frame — which is why the warhead exit
   vector is marginalised over a pose ensemble rather than asserted, and why the pose-surviving fraction is
   reported per basin. Sequence-level uniqueness of C397 and the lysines is pose-independent; the *reach*
   estimates are not. *(d) The causal test has been run and is NULL.* No result in §2.10 shows that any
   designed element **creates** discrimination, and the matched-pair experiment that asks directly now
   returns **S = −0.1297 ± 0.3264 kcal/mol** — indistinguishable from zero (§2.10e). This retires the earlier
   form of this limitation ("the causal test has not been run") without weakening it: the claim that a
   designed element creates discrimination remains unsupported, and is now unsupported *by measurement*
   rather than by absence. Everything in §2.10 is accordingly a set of
   **predicted selective candidates** — *a computationally prioritized, structure-defined, retrosynthetically
   annotated candidate matrix for synthesis and experimental testing* — with the synthetic annotations being
   **routes, not validated syntheses** (no building-block availability was checked against a live commercial
   catalogue and no step was attempted).
9. **A cycle-closure check, a small forward/reverse gap, and good MBAR overlap are precision diagnostics and
   are never accuracy evidence** — not as a matter of degree but by an identity: a closed cycle is
   **identically blind** to any error that attaches to an endpoint rather than to a path, which is to say to
   the force field, the receptor model, the charge method and protonation assignment (§2.9). Every free-energy
   result in this paper is therefore bounded above by its known-answer benchmarking, not by its internal
   self-consistency, and no amount of internally consistent cycling substitutes for a measured reference.

**Selectivity methodology:** docking margins are **triage priors, not affinities**; a quantitative
selectivity claim needs endpoint free energy. The criterion-matched NR4A1/NR4A2 metadynamics runs are
**complete**, so the matrix (§2.5) is genuinely criterion-matched (not opened-target-vs-static-off-target), and
the quantitative tier is now **MM-GBSA-run** rather than planned — but single-snapshot MM-GBSA has **no
entropy and no ensemble average**, so its magnitudes are inflated and only the **verdict/direction** is
trusted; **selectivity FEP** (the defensible affinity tier) is **now run** (independent-window ABFE;
three-replicate NR4A3-favoured ΔΔG, §3), and even converged FEP on a
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
supported by **initial conditional ABFE receptor contrasts** but not experimentally validated. Two riders on
those contrasts, at their current status: the NR4A3 structural-model sensitivity test **has been run** (the
8XTT-anchored NR4A3 leg, in triplicate, §2.8) and it moved the absolute by more than the entire selectivity
margin, while the **matched** experiment-anchored paralogue legs have not been run and remain the decisive
follow-up; and the dense-schedule λ-repair that would firm up the error bars is **held**, so every ABFE number
here stays provisional. With no wet lab, the strongest honest claim is
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
| 2 | opened state geometrically druggable | **pass under the harmonized tracker** (release replicas ≥ D\* in 0.56/0.40/0.80; 44/75 = 0.59 pooled) | initial pass was under the permissive pre-harmonized tracker (0.20/0.16/0.28) | the harmonized re-analysis is **done** (`nr4a3-pocket-reharmonize-summary.json`) and the pocket is detected in 75/75 frames, so the pass no longer depends on a permissive site match or a restricted denominator; what it is **not** is an equilibrium population (the frames are open-seeded and correlated) |
| 3A | persistence after bias removal | **supported** | *post hoc* split from Gate 3 | seeded open-like geometry holds 5 ns in 3/3 replicas |
| 3B | equilibrium energetic accessibility from the closed ensemble | **unresolved** | *post hoc* split from Gate 3 | independent F(Rg) profiles disagree substantially; the fixed-reference-Rg comparison spans ~16 kcal/mol but is **not** an equivalent-state free energy; enhanced-sampling convergence pending |
| 4 | a selective drug-like ligand meets the computational criteria | met **in silico**, not physical | absolute engagement not shown | provisional single candidate (below) |

We explicitly do **not** claim "Gates pass" as unqualified: Gate 1 **failed** as pre-registered, Gate 2's
frame-fraction clause **passes under the committed harmonized re-analysis** while its handles clause is still
only at pre-harmonized weight and the frame-level generation-receptor dependency audit is **still open** (§3),
Gate 3A is supported only in the narrow persistence sense
while **Gate 3B is unresolved**, and Gate 4 is an in-silico criterion, not physical binding. The 3A/3B split
and the three-replica / gate-descriptor diagnostics are **post-hoc analyses**, logged as such in the deviation
file and **not** folded silently into the original single-Rg gate definition. The route is
abandoned (weight shifting to ASO/immuno backups in the roadmap) if the opened conformations are not
geometrically druggable under the harmonized analysis, or no selective drug-like binder can be designed.

**The prospective design stage of §2.10 carries its own preregistered gate ladder, ordered
cheapest-decisive-first, and two of its rules were fixed specifically so that a predictable outcome could not
be reinterpreted after the fact.** The ladder is a hard kill-switch: if no paralogue-discriminating,
ubiquitination-compatible mechanism survives, the honest negative is the publication, and the tiers are
ordered so that the free ones can end it before any GPU spend.

| Tier | Pre-registered criterion | Cost | Outcome |
|---|---|---|---|
| 0 | **Categorical-axis screen.** If no paralogue-unique nucleophile lies within tether range *and* no paralogue-unique exposed lysine exists, selectivity must come from the marginal axis alone — which sits at the method's resolution limit — so say so and expect a negative | $0 CPU | **pass on both axes** — an exposed paralogue-unique cysteine within exit-vector reach, and three exposed paralogue-unique lysines (figures in §2.10) |
| 1 | **Differential surface atlas.** No E3-reachable divergent surface ⇒ stop for free | $0 CPU | **pass** (46 differential-surface handles, §2.4) |
| 2 | **Basin nomination.** If no basin exploits a categorical handle *and* none even nominally discriminates NR4A3 ⇒ stop cheaply | $0 realized | **GO, on the CATEGORICAL basis and weakly** — basins exploit both categorical terms above their nulls, but the terms fire in only a small minority of each basin's placements; counts and fractions in §2.10, which is their only home |
| 3 | **One causal matched-pair test:** a ligand-side double difference asking whether a designed element *creates* discrimination, on one matched pair differing in that element alone | priced, **not run** | pending |

Two of these deserve to be stated as *rules written before the result*, because both concern how a likely
negative is read. **(a) The Tier-2 gate nominates; it does not decide.** Its asymmetry is deliberate: cheap
scoring has poor signal-to-noise for a ~1 kcal/mol *energy* difference, but "does this basin place an
electrophile within reach of C397, and does its transfer zone cover a unique lysine?" is a **geometric
set-membership** question that cheap scoring answers reliably. A gross absence of signal would therefore have
been an informative NO-GO; the presence of a weak signal is *not* trusted to establish a real wedge.
**(b) A null at Tier 3 does not falsify the program, and the reason is structural rather than charitable.**
The Tier-2 GO was taken on the **categorical** basis — the paralogues have no nucleophile at the aligned
position, so the bond cannot form on them at all. The Tier-3 double difference is an ordinary **non-covalent**
alchemical quantity: it models no bond in either leg and can only ever see the pre-covalent complex, so it is
**structurally incapable of testing the categorical mechanism**. What it tests is the **marginal**
induced-interface wedge. Its expected effect for the designed pair is bounded by roughly one partly-buried
hydrogen bond (~0.5–1.5 kcal/mol), so **a null is a likely outcome**,
and the reading is fixed in advance: *a null means the marginal wedge is absent and the claim rests on the
categorical axis alone; the program stops only if the categorical axis has also failed.* *(This rule was
registered against a best-case resolvable ~1.12 kcal/mol — a figure since **superseded** by the measured
replicate scatter of §2.10, at which the expected effect straddles the resolution rather than sitting under it.
**The rule is unchanged**, and the correction runs in the direction that makes it stronger: at an adequate
replicate count a null now **bounds** the marginal wedge instead of merely failing to find it. We note in the
same breath that the test as currently configured — one seed per arm — would **not** deliver that bound, which
is a design condition on running it, not a licence to read a single-seed null as one.)* Writing that down
before the run is the point — without it, a predictable null becomes a verdict on the whole program through a
category error. The corresponding **honest expectation recorded in advance** is that the designed pair offers
NR4A3 a *gain* rather than imposing a paralogue *penalty* (the aligned paralogue residues are hydrocarbon and
simply cannot donate), and that a NO-GO may be acted on at this evidence grade because stopping is the
conservative action, whereas a **positive** result stays **exploratory** until the known-answer ternary
control passes. **⚠ That control has since been run and did NOT pass** (§2.11: wrong sign in all three
replicates, ΔΔG_coop = −0.599 at n = 3 against a preregistered +0.944, with the miss ~34× the statistical
uncertainty and therefore systematic). This
clause is consequently **in force, not pending**: any positive Tier-3 result is exploratory, and the condition
cannot be discharged by adding replicates, because replicates shrink variance and not bias.

> **OUTCOME (2026-08-02) — the Tier-3 test has now been run, and this clause is what it is read against.**
> **S = −0.1297 ± 0.3264 kcal/mol** (§2.10e). It is the **null this clause registered as likely**, and the
> program does **not** stop, exactly as written: the categorical axis has not failed.
> ⓘ **The design condition stated above was MET, and that is why the null is a bound rather than a shrug.**
> The clause warned that at *one seed per arm* the test "would **not** deliver that bound"; it was
> re-specified to **two seeds per arm** before it ran, so the bound exists. At the measured replicate scatter
> it excludes a marginal wedge of **≳ 0.65 kcal/mol (2σ)** — which sits at the **bottom edge** of this
> clause's own predicted ~0.5–1.5 kcal/mol range for one partly-buried hydrogen bond. So the result excludes
> **most** of the effect it was designed to look for while leaving the smallest predicted effect
> (~0.5–0.65 kcal/mol) unexcluded, and it is reported as that rather than as "no wedge".
> ⛔ And the exploratory condition above still binds in the other direction: because §2.11's control did not
> pass, a *positive* S here would have been exploratory — so this null cannot be upgraded into evidence that
> the method works, either.

**Gate 4 (a selective, drug-like ligand can engage the opened pocket) — met in silico by a single de-noised,
initial-ABFE-supported foothold, not an unqualified pass.** `denovo_401` docks into the druggable release
pocket (4/5 handles), stays NR4A3-favoured through multi-snapshot MM-GBSA where the single-snapshot harvest
collapses, clears a same-tier decoy null in its design frame, is **supported by initial conditional
three-replicate ABFE** (§2.8), and passes the in-silico developability filters. Three honest limits keep
it short of an unqualified pass: the decoy null controls the *scoring* step only, and the generation-matched
control that addresses the rest has run one arm — favourable in direction, underpowered to exclude the
confound, and missing the paralogue-pocket arm entirely (§2.7); the **positive margin persists in the metad-opened frame but the candidate does
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
    e.g. NDRG2. **Identifier-only entry — deliberately not completed:** the author list and title were not
    retrievable from a primary source in this environment, and are left blank rather than reconstructed, since
    a plausible-looking but unverified citation is a fabrication. Entries 33 and 34 above carry titles but no
    author list, for the same reason. All three must be completed from the publisher record before
    submission.]

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

**Clinical precedent for targeted protein degradation (§1).**
53. Krönke J, Udeshi ND, Narla A, et al. *Lenalidomide causes selective degradation of IKZF1 and IKZF3 in
    multiple myeloma cells.* Science 343(6168):301–305 (2014). PMID 24292625; doi 10.1126/science.1244851.
    [Molecular-glue mechanism of the IMiDs; primary.]
54. Lu G, Middleton RE, Sun H, et al. *The myeloma drug lenalidomide promotes the cereblon-dependent
    destruction of Ikaros proteins.* Science 343(6168):305–309 (2014). PMID 24292623; doi 10.1126/science.1244917.
55. Krönke J, Fink EC, Hollenbach PW, et al. *Lenalidomide induces ubiquitination and degradation of CK1α in
    del(5q) MDS.* Nature 523(7559):183–188 (2015). PMID 26131937; doi 10.1038/nature14610.
    [Neosubstrate basis of the del(5q) therapeutic window.]
56. Gandhi AK, Kang J, Havens CG, et al. *Immunomodulatory agents lenalidomide and pomalidomide co-stimulate
    T cells by inducing degradation of T cell repressors Ikaros and Aiolos (IKZF1 and IKZF3) via modulation of
    the E3 ubiquitin ligase complex CRL4^CRBN.* Br J Haematol 164(6):811–821 (2014). PMID 24328678;
    doi 10.1111/bjh.12708.
57. Hurvitz SA, et al. *Vepdegestrant, a PROTAC Estrogen Receptor Degrader, in Advanced Breast Cancer.*
    N Engl J Med (2025). PMID 40454645; doi 10.1056/NEJMoa2505725. [VERITAC-2 phase 3; PFS benefit confined to
    the ESR1-mutant subgroup, not significant in ITT.]
58. U.S. Food and Drug Administration. *FDA approves vepdegestrant for ER-positive, HER2-negative, ESR1-mutated
    advanced or metastatic breast cancer.* 2026-05-01. https://www.fda.gov/drugs/resources-information-approved-drugs/fda-approves-vepdegestrant-er-positive-her2-negative-esr1-mutated-advanced-or-metastatic-breast
    [First FDA-approved heterobifunctional PROTAC.]
59. Investigational oncology PROTACs (activity short of approval): BTK degrader **BGB-16673** (CaDAnCe-101),
    Blood 144(Suppl 1):885 (2024) and Blood 146(Suppl 1):85 (2025), ASH; BTK degrader **bexobrutideg (NX-5948)**,
    Blood 146(Suppl 1):86 (2025), ASH; AR degrader **luxdegalutamide (ARV-766)**, J Clin Oncol 42(16 suppl):5011
    (2024), ASCO; AR degrader **bavdegalutamide (ARV-110)**, ASCO GU 2022 (ARDENT). [Conference/early-access
    sources; response figures as reported at the cited data cut-offs.]

**Prior art in alchemical ternary-cooperativity free-energy calculation** (cited in §2 to position this work's
novelty as incremental; these are the benchmarks any ternary-cooperativity result from this program must be
compared against). *Entries 60–63 are identifier-anchored: DOI/year/journal as recorded in the project's
`STRATEGY.md`; author-title strings for 61–63 were not retrievable from a primary source in this environment
and are deliberately left blank rather than reconstructed. They must be completed from the publisher record
before submission.*

60. Chen et al. (2023). [Alchemical ternary-complex cooperativity free-energy calculations for PROTAC systems,
    incl. VHL–BRD4/MZ1. Full citation to be completed from the publisher record; the DOI was not recorded in
    `STRATEGY.md`.]
61. *J Chem Theory Comput* (2025). doi 10.1021/acs.jctc.5c00064. [Alchemical PROTAC ternary-cooperativity
    ΔΔG_coop cycle. Authors/title to be completed at submission.]
62. *J Chem Theory Comput* (2025). doi 10.1021/acs.jctc.5c00736. [Alchemical PROTAC ternary-cooperativity
    ΔΔG_coop cycle. Authors/title to be completed at submission.]
63. *J Chem Inf Model* (2024). doi 10.1021/acs.jcim.4c01227. [PROTAC ternary cooperativity / paralogue
    selectivity by free-energy calculation. Authors/title to be completed at submission.]

**Sources added for the mechanism-first prospective stage (§2.10) and the celastrol mechanism (§2.2, §2.5).**
*Entries 64–73 were verified against the primary record on 2026-07-25 by machine query (Crossref for journal
articles, the RCSB data API for structural entries; the verification job's log is in the reproducibility
archive). Where a field is marked "not retrieved" it was not returned by that query and is deliberately left
blank rather than reconstructed — an unverified author list is a fabrication. Structural entries 68–70 printed
title, method, resolution, first author, journal and year but **no DOI or PMID**, so those two fields are
absent by verification status rather than by oversight; entry 70 has no publication at all.*

64. Zhang D, Chen Z, Hu C, Yan S, Li Z, Lian B, Xu Y, Ding R, Zeng Z, Zhang X-k, Su Y. *Celastrol binds to its
    target protein via specific noncovalent interactions and **reversible** covalent bonds.* Chem Commun
    54:12871–12874 (2018). doi 10.1039/C8CC06140H. [The celastrol covalent-engagement anchor cited in §2.2 and
    §2.5. **Note the mechanism this title states: the bond is *reversible*.** The paper's earlier shorthand
    "covalent capture" is therefore imprecise and is corrected in §2.2 — which matters twice over, because the
    one demonstrated NR4A-family-selective degrader's warhead is itself a reversible-covalent binder, and
    reversible covalency is also the chemistry §2.10's library selects on independent grounds.]
65. Gadd MS, et al. *Structural basis of PROTAC cooperative recognition for selective protein degradation.*
    Nat Chem Biol 13:514–521 (2017). doi 10.1038/nchembio.2329. [PDB **5T35** — VHL·EloB·EloC + BRD4-BD2 + MZ1,
    X-ray 2.7 Å; the VHL recruiter frame the §2.10 basin search consumed. Full author list not retrieved.]
66. Nowak RP, et al. *Plasticity in binding confers selectivity in ligand-induced protein degradation.*
    Nat Chem Biol 14:706–714 (2018). doi 10.1038/s41589-018-0055-y. [PDB **6BOY** — DDB1–CRBN–BRD4(BD1) + dBET6,
    X-ray 3.33 Å; the CRBN recruiter frame. Full author list not retrieved.]
67. Zheng X, Ji N, Campbell V, Slavin A, Zhu X, Chen D, Rong H, Enerson B, Mayo M, Sharma K, Browne CM,
    Klaus CR, Li H, Massa G, McDonald AA, Shi Y, Sintchak M, Skouras S, Walther DM, Yuan K, Zhang Y,
    Kelleher J, Liu G, Luo X, Mainolfi N, Weiss MM. *Discovery of KT-474 — a Potent, Selective, and Orally
    Bioavailable IRAK4 Degrader for the Treatment of Autoimmune Diseases.* J Med Chem 67:18022–18037 (2024).
    doi 10.1021/acs.jmedchem.4c01305. [Primary citation of PDB **9CUO** ("Crystal structure of CRBN with
    compound 3", X-ray 1.60 Å) — the CRBN entry advanced by the §2.10 E3 downselect.]
68. Lucas SCC, Xu Y, Hewitt S, Collie GW, Fusani L, Kadamur G, Hadfield TE, Su N, Truman C, Demanze S, Hao H,
    Phillips C. *Discovery of a Series of Covalent Ligands That Bind to Cys77 of the Von Hippel–Lindau Tumor
    Suppressor Protein (VHL).* ACS Med Chem Lett 16:693–699 (2025). doi 10.1021/acsmedchemlett.4c00582.
    [Primary citation of PDB **9GIO** ("Crystal structure of the VHL–EloC–EloB complex with a covalent compound
    bound to C77 of VHL", X-ray 1.486 Å) — the VHL entry advanced by the §2.10 E3 downselect. **Flagged, not
    resolved:** the deposited compound is described by the structural record as a **covalent Cys77 ligand**,
    which is not the same characterization as the hydroxyproline-pocket handle chemistry every published VHL
    PROTAC uses; whether that changes the downselect's ligandability scoring is a $0 re-check, and it does not
    touch the reported basin result, which consumed **5T35/8R5H** and not 9GIO.]
69. Li J, et al. *Cullin-RING ligases employ geometrically optimized catalytic partners for substrate
    targeting.* Mol Cell (2024). [Primary citation of PDB **8R5H** — "NEDD8-CUL2-RBX1-ELOB/C-VHL-MZ1 with
    trapped UBE2R2~donor Ub-BRD4 BD2", cryo-EM 3.44 Å; the intact assembly against which §2.10's transfer
    anchor is measured with no composition. Volume/pages/DOI/PMID and the full author list not retrieved.]
70. RCSB Protein Data Bank. *PDB **9UUM** — "Cryo-EM structure of mezigdomide-organized
    CRL4-DDB1-CRBN-IKZF3(ZF2-ZF3)-UbcH5a-Ub ubiquitylation assembly", cryo-EM 3.41 Å.* [The CRBN-arm intact
    assembly supplying §2.10's observed E2 catalytic cysteine and its measured substrate-lysine transfer distance.
    **Deposition status "to be published" — there is no associated publication and no year**, so it is cited
    as a structural entry only.]
71. Shrake, Rupley. *Environment and exposure to solvent of protein atoms. Lysozyme and insulin.* J Mol Biol
    79:351–371 (1973). doi 10.1016/0022-2836(73)90011-9. [Solvent-accessible-surface algorithm used for every
    RSA and burial figure in §2.10. Author initials not retrieved.]
72. Hendlich, et al. *LIGSITE: automatic and efficient detection of potential small molecule-binding sites in
    proteins.* J Mol Graph Model 15:359–363 (1997). doi 10.1016/S1093-3263(98)00002-3. [Cavity-volume scan in
    the E3 ligandability assessment. Full author list not retrieved.]
73. Horn. *Closed-form solution of absolute orientation using unit quaternions.* J Opt Soc Am A 4:629 (1987).
    doi 10.1364/JOSAA.4.000629. [The superposition used to place NR4A1/NR4A2 into the NR4A3 frame so that one
    sampled set of placements is evaluated against all three paralogues. Author initials not retrieved.]

*Deliberately NOT cited:* the worm-like-chain end-to-end distribution used for the linker-accessibility term in
§2.10 is a standard polymer-physics result, but the machine query for its primary source returned **no matching
record** (all candidates were unrelated). Rather than attach a remembered citation to it, the model is described
in Methods and the reference is left to be established from the primary literature before submission.

## Appendix A — corrections to earlier drafts

Superseded values are recorded here rather than left inline, so the live text carries only the current figure
while nothing that was previously stated silently disappears.

- **§2.9, `cw_ms_5acetamido_ester`: the tabulated ΔΔG_bind was −1.345 ± 0.810 kcal/mol (23 mapped atoms); it
  is now +0.445 ± 0.572 (21 mapped atoms).** The superseded value is a real measurement, but of the wrong
  edge: it is `cw_ev_5nh2 → cw_ms_5acetamido_ester`, which joins two analogues, and it had been placed in a
  table whose caption reads *"more negative = predicted tighter than the cmpd19 anchor."* The anchor-rooted
  edge `zaienne_cmpd19 → cw_ms_5acetamido_ester` is the one that belongs there. The consequence is a sign
  change: the analogue moves from apparently the second-tightest of the series to modestly weaker than the
  anchor. The non-anchor-rooted value is retained, correctly labelled, in the second table of §2.9. Caught by
  regenerating the table from `step1-fanout-map.json`'s own `ranking` field, whose `ranking_note` states the
  anchor-rooted restriction explicitly — the artifact was right and the transcription was not.
- **§2.11 calibrator: the headline was a single replicate, ΔΔG_coop = −0.522 kcal/mol with an absolute error
  of 1.466, and the formal verdict was INDETERMINATE.** All three preregistered replicates landed on
  2026-07-30, so the headline is now the n = 3 mean **−0.599** (abs error **1.543**) and the verdict is
  **FAIL / NO-GO**. The superseded single-replicate value is not withdrawn as wrong — it is r0, and it appears
  in the live text as one of the three per-replicate figures (as **−0.5125**, the 4 fs reduction of the same
  seed; **−0.522** was its earlier reduction and **−0.534** the 2 fs cycle that preceded the restrained
  binary-arm re-run). What changed is that a mean of one is no longer being reported as the result. INDETERMINATE
  must not be quoted going forward: it described the absence of replicates, and the replicates exist.
  **This entry was written before the correction reached the rest of the manuscript, and for a period the paper
  disagreed with itself about its own headline:** the abstract still gave −0.522, §2.11 and §5 derived
  "~33× the statistical uncertainty" from the superseded 1.466, and the SI's §S11 discussion used **1.478** —
  the reading from *before* the restrained binary re-run, superseded twice over, four rows below a table that
  already carried 1.543. All are now the n = 3 values and the ratio is **~34×**. The conclusion is untouched at
  every one of the three magnitudes, since the sign is wrong in all of them; recorded because a superseded
  number surviving in an abstract is exactly the copy that gets quoted onward.

- **§2.9 edge count: the table was cut at 14 computed edges of 18 computable, against ~$69 of GPU spend
  across 197 rentals.** The fan-out has since closed at **18 of 18** and **$73.79**, so those figures describe
  a run in progress and are not the final map.

- **§2.10 Tier-2 electrophile term: the count was 7 basins, `crbn|M0` was reported as reaching C397 at 11
  backbone atoms and as therefore clearing the 12-atom gate, gate-level reach fractions were quoted as
  0.019–0.057 across seven basins, the conserved-cysteine control as zero in 168 of 192 basins (0–6.6 %), and
  every reach length was carried as a lower bound.** All of these came from a reach criterion that credited a
  pendant arm with shortening the anchor-to-anchor span, which no pendant can do. Replacing it with the exact
  three-ball kernel and recomputing on a matched 10⁶-placement, 12-pose run gives **3** basins (`vhl|M2` 10
  atoms, `vhl|M3` 11, `crbn|M17` 12), `crbn|M0` at **13** atoms and therefore **missing** the gate with a
  gate-level reach fraction of 0.000, fractions **0.021–0.057**, and the control zero in **184 of 192**
  (0.4–3.9 %). **The transfer-zone term (40) and the nominal limb (28) are bit-identical across the
  correction**, and the Tier-2 verdict is unchanged — it passes on the categorical basis either way, because
  the three surviving basins still clear the gate. What changes is which basin clears it: the correction
  separates the strongest *nomination* (`crbn|M0`, on the lysine term) from the basins that carry the
  *electrophile* term, and an earlier draft's claim that the achieving-placement re-run left "the strongest
  basin among the most tractable" is withdrawn — at the achieving placement `crbn|M0` needs 13 atoms against
  10 and 11 for `vhl|M2`/`vhl|M3`, i.e. comparable, not leading. Live record:
  [`../modalities/nr4a3-orientation-basins.json`](../modalities/nr4a3-orientation-basins.json) →
  `tier2_gate`, whose `n_exploiting_term_a_electrophile_reach` governs; the superseded per-record values are
  retained in that artifact as `*_relaxed_superseded`.

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
