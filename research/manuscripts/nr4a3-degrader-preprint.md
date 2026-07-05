# Computational design of a selective NR4A3 degrader: opening a cryptic pocket in a "ligand-independent" nuclear receptor

> **Working title — NOT finalized.** The title is deliberately deferred to post-time and will be chosen once
> the selectivity FEP result is in hand (a confirming result licenses a bolder title; a refuting one a more
> retreating one; the frontrunner default is a result-led framing with "predicted-selective … warhead
> candidate"). See the title options + rationale in `nr4a3-degrader-preprint-plan.md`.

**Tristan D. McRae**

*Independent researcher. Correspondence: trimcrae@gmail.com*

*Preprint. In-silico design and feasibility study — no wet-lab validation; no molecule synthesized. Every
result is computed and reported with its evidentiary weight. Supporting analyses (pre-registration,
adversarial review, full selectivity-architecture treatment, method details) are cited as Supplementary
Information.*

---

## Abstract
NR4A nuclear receptors (NR4A1/2/3) are regarded as "undruggable" transcription factors: the canonical
Nurr1/NR4A2 crystal structure shows a ligand-binding pocket occluded by bulky side chains, and NR4A3 has no
experimental structure. Yet NR4A3 is a compelling *selective* degradation target, driving extraskeletal
myxoid chondrosarcoma (EMC; EWSR1/TAF15::NR4A3 fusion) and acinic cell carcinoma (AciCC; NR4A3
over-expression) by gain of NR4A3, where the therapeutic goal is to remove NR4A3 while sparing NR4A1/2
(whose combined loss is leukaemogenic). We present a computation-only program to assess NR4A3's
druggability and design a selective degrader warhead. (1) Calibrated against a nuclear-receptor panel, the
NR4A3 orthosteric pocket is borderline in the static AlphaFold2 model (fpocket druggability 0.495, below the
calibrated drug-bound band of 0.53–0.68). (2) Well-tempered metadynamics drives the orthosteric pocket to
breathe into transiently druggable conformations, and an unbiased "release" simulation seeded at a
low-energy druggable frame finds this geometry **metastable (3/3 replicas) and druggable in ~24 % of
unbiased frames** — a thermally-real induced-fit cavity, not a static pocket and not a bias artifact,
paralleling the experimentally demonstrated breathing pocket of Nurr1. (3) Seven of ten pocket-lining
residues diverge from NR4A1/2 as selectivity handles (five pocket-facing in the druggable ensemble; the
engageable divergent set is asymmetric — five versus NR4A1, four versus NR4A2). (4) Running the same
metadynamics on NR4A1 and NR4A2 yields **state-matched** opened-pocket ensembles for all three paralogues,
enabling a per-candidate family-wide selectivity fingerprint; repurposed NR4A actives largely fail to hold
up as NR4A3-selective under endpoint MM-GBSA. (5) A pocket-conditioned de-novo generative campaign, funnelled
through docking and endpoint MM-GBSA against a decoy null of non-NR4A drugs, yields **`denovo_401`**, whose
NR4A3-selectivity survives multi-snapshot ensemble de-noising and exceeds a same-tier multi-snapshot decoy null
**in its unbiased design-frame receptor** (while failing that null in the biased metad-opened frame). Because
the decoy null controls the scoring step but not the generative step (the candidate, unlike the decoys, was fit
to that receptor) or the best-of-N selection — and because the generated set is *not* enriched over the decoys —
we report it as a **receptor-frame-dependent de-noised foothold**, not a demonstrated-specificity hit. (A second
candidate, `denovo_111`, de-noised well as the neutral form but was withdrawn by a pre-FEP species sweep — its
physiological cation reverses selectivity — and a pre-FEP stereoisomer sweep shows denovo_401's selectivity is
stereochemistry-robust with the generated diastereomer near-optimal, so `denovo_401` is the sole robust lead.) (6) We then **predict the NR4A3/NR4A1/NR4A2–CRBN–
PROTAC ternaries** (a representative denovo_401-PROTAC; pipeline validated on the CRBN + lenalidomide control,
which it correctly seats in the tri-tryptophan pocket): **all three paralogues form an equally productive
ternary** (bridged, each presenting an exposed lysine within ubiquitin reach), so the degrader mechanism is
geometrically viable but the ternary is **not a paralogue-selectivity lever for this linker** — selectivity
rests on the binder (+ pharmacokinetics). We conclude that NR4A3's "undruggable" orthosteric pocket is
computationally tractable as a dynamic, induced-fit site; that selectivity is a multiplicative budget which,
on current evidence, is **carried by the binder** (the ternary being productive-but-not-selective); and that
the affinity-grade selectivity FEP is the one remaining tier. All claims are in-silico predictions requiring
experimental validation.

---

## 1. Introduction
NR4A receptors are constitutively active orphan nuclear receptors whose canonical ligand pocket is
collapsed or occluded in crystal structures (Nurr1, PDB 1OVL), the structural basis of their "undruggable"
reputation. That reputation, however, is a statement about *static* structures: Nurr1's pocket is in fact
dynamic and expands from its collapsed crystal conformation to bind fatty acids [de Vera 2019], an MD study
reported a cryptic druggable pocket in Nur77/NR4A1 [Lanig 2015], and validated NR4A ligands engage
cryptic/surface sites. NR4A3 itself is experimentally ligandable — a fragment screen against NOR-1/NR4A3
(<1 % hit rate) yielded a low-micromolar inverse agonist that shifts NOR-1-regulated gene expression in cells
[Zaienne 2022], and NR4A3-selective indole-3-carbinol analogues (IC₅₀ ≈ 8–47 µM) de-repress the NR4A3 target
gene MYC [Safe 2025] — but its binding site is structurally undefined: NR4A3 has no experimental structure and
no published pocket-dynamics analysis, the structural gap this work addresses.

NR4A3 is an attractive *selective* target because two cancers are driven by its gain: EMC, via the
EWSR1/TAF15::NR4A3 fusion that retains a near-intact NR4A3 ligand-binding domain (LBD); and AciCC, the third
most common malignant salivary-gland tumour, via NR4A3 over-expression through enhancer hijacking [Haller
2019; Khan 2023]. In both, the therapeutic objective is to remove NR4A3 while sparing NR4A1 and NR4A2:
combined loss of NR4A1 and NR4A3 is leukaemogenic in mice [Mullican 2007]. Because occupancy pharmacology is
precluded by the collapsed pocket, the apt modality is targeted **degradation** — recruiting the retained,
ordered NR4A3 LBD to an E3 ligase — which is target-generic (it removes NR4A3 whether wild-type or fused).

This program is governed by a pre-registered falsification scheme with thresholds fixed before the
production results (SI §1). We report each result at its evidentiary weight and state the
central limitation up front: this is an in-silico study with no wet-lab validation, so every candidate is a
*prediction*, not a validated molecule.

## 2. Results

### 2.1 The static orthosteric pocket is borderline — calibrated, not asserted
fpocket assigns the NR4A3 orthosteric pocket (Pocket 5, residues 406–534, carrying all seven selectivity
handles below) a druggability of **0.495**. To interpret this we ran the same pipeline on a nuclear-receptor
calibration panel. Experimentally drug-bound NR pockets score **0.53–0.68** (PPARγ/rosiglitazone 0.599,
ERα/estradiol 0.586, Nurr1-holo 0.677, Nur77-holo 0.529), defining a calibrated druggable threshold
**D\* = 0.53**. The fpocket *maximum-anywhere* score is non-discriminating — even the occluded 1OVL crystal
scores 0.864 at a *non-orthosteric* cavity — so the widely-quoted "Nurr1 ~0.8" reflects a non-orthosteric
site, present in both model (NR4A2 model 0.801) and crystal (0.864), i.e. not an AlphaFold artifact. Because
our AF2 model does not over-call relative to the 1OVL crystal, NR4A3's static 0.495 is a conservative upper
bound. The static orthosteric pocket therefore sits just below the validated druggable band — concordant
with "undruggable," and the right starting point for the cryptic-pocket question. Recent NR4A work brackets
this: a 2025 vidofludimus/Nurr1 study reaffirms the *canonical* pocket is occluded and acts via an allosteric
surface site [López-García 2025] — which is exactly why we claim not that the static pocket is druggable but
that it *breathes* open (§2.2); NMR shows the NR4A LBD is genuinely ligandable by some chemotypes (cytosporone
B) but not others (celastrol) [Munoz-Tello 2020]; and a paralog-selective NR4A1 PROTAC that spares NR4A2/NR4A3
[Wang 2024] establishes that intra-family degradation selectivity is achievable.

### 2.2 Metadynamics opens a druggable cryptic pocket; an unbiased run confirms it is metastable
Well-tempered metadynamics on the radius of gyration (Rg) of the Pocket-5 lining Cα atoms drives the pocket
open (Rg ~0.5 → ~1.05 nm). Per-frame fpocket on the orthosteric Pocket-5 cavity — the same metric as the
static 0.495 — reaches a peak druggability of **0.931**; reported as a distribution, a non-negligible
fraction of opened frames clear D\* (meeting the pre-registered ≥5 %-of-frames criterion), with SASA of the
lining residues rising. Because fpocket druggability rewards hydrophobic *enclosure*, a merely
solvent-exposed splaying would score lower, so the rise reflects a genuine enclosed cavity. This is the
first pocket-dynamics evidence for NR4A3, paralleling the breathing Nurr1 pocket [de Vera 2019].

Two honest qualifications frame the energetics. First, the free-energy profile F(Rg) is **monotonic** — a
single closed basin with a rising wall, no separate opened minimum — so the druggable conformations arise by
**basin-internal breathing**, not a two-state cryptic switch (the pre-registered "distinct opened basin"
condition is met only in this weaker sense; SI §1). Second, the decisive test of
whether the breathing-open geometry is physically populated or bias-induced strain is an **unbiased "release"
simulation** seeded at the low-energy druggable frame (Rg ≈ 0.717). This run is positive: the geometry is
**metastable — 3/3 unbiased replicas held 5 ns** with mean drift 0.025 nm and no collapse — and, on the
unbiased trajectory, the orthosteric pocket is **druggable in ~24 % of frames** (max 0.842, mean 0.262,
fraction ≥ D\* = 0.20) at Rg ≈ 0.737. This is a thermally-real, spontaneously sampled cavity — not a static
always-open pocket (unbiased mean 0.262 < 0.5) and not a bias artifact — i.e. an **induced-fit /
conformational-selection** site, the expected behaviour for a nuclear-receptor cryptic pocket. All downstream
design is anchored to a druggable unbiased-release frame (confirmed fpocket 0.667, within the drug-bound
band), not the biased-metad frame. *(Scope: the 3/3 metastability is an Rg-persistence result across the
triplicate; the ~24 % druggability fraction is measured on one release replica; 5 ns rules out prompt
collapse, not tens-to-hundreds-of-ns relaxation.)*

A registered check confirms the selectivity handles remain engageable in the druggable frames: a mean of
**5.0/7** handles point into the cavity, with **L406, T410, I484, I531, L534** reliably pocket-facing and
T407/R412 splaying outward. The realistic selectivity-handle set is therefore five, not seven.

### 2.3 Selectivity handles for an NR4A1/2-sparing warhead
Aligning the NR4A3 pocket to NR4A1/NR4A2 identifies, among the ten Pocket-5 lining residues, **seven
divergent** ones (L406, T407, T410, R412, I484, I531, L534). Of the five that stay pocket-facing in the
druggable ensemble, the engageable set is **asymmetric across paralogues**: all five distinguish NR4A3 from
NR4A1, but only four distinguish it from NR4A2, because **I531 is identical (Ile) in NR4A3 and NR4A2**. NR4A2
selectivity therefore rests on a narrower engageable handle set than NR4A1 selectivity — relevant because
NR4A2/Nurr1 carries the dopaminergic-loss liability one most wants to spare. This is a design specification
with a quantified, paralogue-resolved window, not a demonstrated binding margin.

### 2.4 A family-wide, state-matched selectivity matrix
Docking an opened NR4A3 pocket against *static* paralogue models would bias toward apparent selectivity,
since — by the same argument [de Vera 2019; Lanig 2015] — the paralogue pockets are likely cryptic too. We
therefore ran the **same metadynamics on NR4A1 and NR4A2** to obtain state-matched opened-pocket ensembles
for all three paralogues, and docked one library into each at matched opened conformers. Each candidate
carries a selectivity fingerprint across the family, partitioning the library into NR4A3-selective, pan-NR4A,
and the AML-associated NR4A1+NR4A3 anti-target cells. The **anti-target cell is empty** (no candidate engages
NR4A1+NR4A3 while sparing NR4A2), and the NR4A3-leaning leads are repurposed NR4A actives — but the docking
free energies fall within noise, so they nominate chemotypes, not a lead.

Re-scoring the matrix's own docked poses with single-snapshot endpoint **MM-GBSA** disqualifies the
repurposed actives: the docking-level NR4A3-selectivity mostly does not survive, and the apparent docking
lead cytosporone B *reverses* (consistent with its known NR4A1 agonism). MM-GBSA magnitudes here are inflated
by the single-snapshot/no-entropy approximation, so we read verdict/direction, not kcal/mol — but the
direction is clear: repurposed NR4A chemical matter is method-validation, not a selective lead, motivating
de-novo design. A degrader's *degradation*-selectivity is ultimately set by the ternary complex, so the
binding matrix is a necessary-but-not-sufficient filter (§2.7).

### 2.5 De-novo design, and a decoy control that disciplines it
Because the repurposed library produced no MM-GBSA-selective candidate, we ran a **pocket-conditioned de-novo
generative campaign** (DiffSBDD, pretrained CrossDocked weights) against the druggable unbiased-release
conformation, conditioned on the engageable divergent handles, with a lead-size constraint. Generation was
clean (191/195 valid and unique; 96 % PAINS-free; 92 % contacting ≥4 of the five engageable handles). The
top-ranked generations were funnelled through the same dock + MM-GBSA selectivity pipeline.

A specificity control is essential and, run honestly, is sobering. Passing **38 diverse non-NR4A marketed
drugs** through the identical dock → single-snapshot-MM-GBSA funnel, the single-snapshot "NR4A3-selective"
verdict proves **non-specific**: it labels **39 % (15/38)** of decoys — including caffeine, ibuprofen,
lidocaine, phenytoin — "confirmed_selective," and the developability-gated de-novo set is *not* enriched over
that null. The single-snapshot MM-GBSA selectivity verdict therefore cannot, on its own, support a
selectivity claim; a raw margin is not evidence. We accordingly treat the decoy run as a **calibrated null**
and require candidates to beat it. (An early single-snapshot "lead," `denovo_15`, is retracted on this basis:
beyond the non-specific score, medicinal-chemistry triage flags generative-model liabilities — a carbamic
acid, a 1,3-cyclopentadiene, an imine — and a synthesizability score above the campaign cut.)

### 2.6 One robust lead survives multi-snapshot de-noising (denovo_401), after species resolution
Single-snapshot MM-GBSA margins carried standard deviations (4–6 kcal/mol) larger than the margins
themselves, so we built a **multi-snapshot endpoint MM-GBSA** tier (short GB Langevin MD; ΔG averaged over
frames, with error bars) and applied it to the harvest. It is discriminating rather than merely destructive:
a negative control stayed non-selective and the single-snapshot "best" collapsed (+18.34 → −2.95 ± 3.65),
while two candidates initially held — **`denovo_401`** (multi-snapshot margin **+12.83 ± 2.98**, margin − SD
**+9.85**; NR4A3 ΔG −38.18, both paralogues 13–15 kcal/mol weaker; reproduced under an independent-seed
replicate at **+14.75 ± 4.82**, so not a single-draw artifact) and the neutral form of `denovo_111`
(+14.60 ± 4.10) — out of ~11 multi-snapshot-tested (a low but non-zero hit-rate). A **pre-FEP species-resolution
sweep** (dock + MM-GBSA of denovo_401's 16 stereoisomers and denovo_111's protonation forms) then sharpened
this to a single robust lead: **denovo_111 is withdrawn** — it carries a basic pyrrolidine, and its
physiological **cation reverses** selectivity (multi-snapshot **−15.01 ± 5.14**, binding NR4A1 *more* tightly
than NR4A3), so its neutral-form margin was an artifact; while **denovo_401's selectivity is
stereochemistry-robust** — nearly all 16 diastereomers scored selective, and the DiffSBDD-generated isomer is
near-optimal (de-noised +9.54 ± 4.26), co-best with its C13-epimer iso08 (+11.36 ± 5.25, within SD), so the FEP
subject is that resolved epimer pair. **`denovo_401` is thus the sole robust lead** (chemically clean:
`COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1`, MW 304, QED 0.80, SA 3.87, no PAINS/BRENK alerts,
0 Lipinski violations, Veber-compliant; one watch-item — cLogP 4.63, lipophilic-leaning),
characterized across receptor frames (below). Assembled into a CRBN degrader the molecule is projected into
normal beyond-Rule-of-5 space (projected MW ~657), as expected for the modality.

Judged against a **same-tier multi-snapshot decoy null**, the result is **receptor-frame-dependent** (and, as
we note below, confounded by the null not controlling the generative step); we report both directions honestly:

| receptor frame | multi-snapshot decoy null (95th pct / max) | `denovo_401` margin | clears the null? |
|---|---|---|---|
| unbiased **release** (design frame) | +6.69 / +7.10 | **+12.83 ± 2.98** | **yes** — above the whole null |
| biased **metad-opened** | +17.70 / +24.74 | +7.44 ± 4.18 | **no** — ~84th percentile |

In the biased metad-opened frame the decoy null *balloons* — random drugs such as diphenhydramine (+24.74)
and lidocaine (+22.08) score as strongly "NR4A3-selective" — so that frame is a poor, promiscuous
discriminator, and `denovo_401`'s margin does not stand out in it. One caveat sharpens this: the decoy null
controls the **docking/MM-GBSA scoring** step (the decoys are marketed drugs pushed through the identical
funnel) but **not** the **generative** step — `denovo_401` was DiffSBDD-fit to the release pocket, whereas the
decoys were fit to no pocket, so in the release *design* frame `denovo_401` carries a receptor-match advantage
the decoys lack, and it is additionally the best of ~200 generations / ~10 de-noised candidates. Tellingly,
the frame it clears the null in is the one it was designed for; the metad frame it *fails* is the one it was
not (and the less design-confounded of the two). The defensible claim is therefore narrow: *`denovo_401` is the
one candidate of the harvest whose NR4A3-selectivity survives ensemble de-noising and exceeds a same-tier decoy
null in its unbiased design frame — a de-noised **foothold**, not a demonstrated specificity result, since the
null does not control the generative step or the best-of-N selection*, consistent with the finding (§2.7) that
this cryptic pocket is a fragile place to source a robust margin. The natural resolutions — a generation-matched
decoy null, ensemble scoring over the druggable release sub-ensemble, and, as the affinity-grade tier, relative
selectivity free-energy perturbation — are none of them run here.

### 2.7 Selectivity architecture: a binder × ternary budget
Comparing NR4A1/2/3 divergence in the orthosteric cryptic pocket (the warhead's contact residues) against
the LBD-wide pocket-residue census, the warhead pocket is the **most paralogue-divergent zone of the LBD**
(70 % of contacts divergent versus 43 % across the rest of the LBD; SI §3). The
binder's selectivity problem was therefore never handle scarcity — it is pocket druggability and
affinity-margin robustness in a cryptic, least-druggable-of-three pocket. Three design conclusions follow.
First, selectivity is a **multiplicative** budget across binding × ternary × kinetics whose factors compound:
a selective binder is strictly valuable and remains the primary goal (`denovo_401` provides a
decoy-null-screened, if fragile, foothold — not a fully controlled specificity result, since the null does not
control the generative step; species resolution withdrew the second candidate denovo_111 as protonation-fragile). We had hoped the **ternary** could *multiply* that margin; **we tested it and it
does not** (for a representative PROTAC). We validated the ternary pipeline (Boltz-2) on the CRBN + lenalidomide
control (glutarimide seated in the tri-Trp pocket, 2.85 Å to W380, ligand-iPTM 0.99 — a necessary sanity check
on an in-distribution complex, not a generalization proof), then ran the actual **NR4A3/NR4A1/NR4A2-LBD + CRBN
+ denovo_401-PROTAC** ternaries. **All three form an equally productive-geometry complex** — the PROTAC bridges
LBD and CRBN and each LBD presents an exposed lysine within ubiquitin reach of CRBN (NR4A3 K195 3.1 Å, NR4A1 K53
2.3 Å, NR4A2 K175 4.0 Å), with comparable within-noise confidence (iptm 0.72/0.83/0.82). So the ternary is
**productive (the degrader mechanism is viable) but not paralogue-selective** for this linker: it does not add
NR4A3 selectivity on top of the binder. This is mechanistically unsurprising — the PROTAC engages the conserved
LBD fold — and it *narrows* the selectivity budget onto the **binder** (+ pharmacokinetics/CNS-exclusion for
NR4A2, whose tox is CNS-localized and EMC is a peripheral sarcoma). **But the ternary is not a spent lever:**
mapping paralogue divergence at the predicted NR4A3–CRBN interface shows **8 of 33 interface residues differ
from each paralogue (6 from both: E545/T563/Q570/S571/L576/E580/V588…), on a surface *distinct* from the pocket
handles** — so ternary selectivity is **structurally available** (a divergent patch a linker could be designed
toward), just not realized by this representative linker, and the binder and ternary would then draw on
*independent* residue sets (a genuine multiplicative gain). Caveats: one representative linker/exit vector (the
interface — and its divergent-patch set — will shift with the linker); Boltz gives a single ternary pose, not
the cooperativity (α)/productive-ensemble that sets real degradation selectivity, so single-pose docking can
*flag availability* but cannot *optimize or validate* ternary selectivity (a ternary-ensemble method is the
right tool — a method-watch item); the Lys-proximity is a CRBN-only proxy (no full CRL4^CRBN + E2~Ub). Third,
**fusion-versus-wild-type selectivity is
unobtainable from the degrader** at any stage — the warhead binds an LBD identical in fusion and wild-type —
so tumour-exclusivity is the complementary antisense route's job, and the degrader's honest scope is
paralogue selectivity plus accepted wild-type-NR4A3 loss.

## 3. Indication landscape
The family-wide ensembles make the degrader a *programmable* design axis. The primary **NR4A3-selective**
path addresses EMC (clean single-driver proof-of-concept), AciCC (the more common, NR4A3-over-expression
indication), and other NR4A3-rearranged sarcomas. A deliberately **pan-NR4A** profile (engaging the conserved
pocket residues) is a distinct second design mode for *ex-vivo* immuno-oncology, where reversing CD8⁺ T-cell
exhaustion requires degrading all three NR4As [Chen 2019]; it is scoped to transient ex-vivo use, not
systemic therapy. The **NR4A1+NR4A3** combination is an explicit anti-target (combined loss causes AML
[Mullican 2007]); showing the method can design *into* NR4A3-only and *away from* NR4A1+NR4A3 is itself a
safety-design result. EMC is the entry point, not the endpoint.

## 4. Methods (summary)
Structure: AlphaFold2 (AFDB) + fpocket. Cryptic pocket: OpenMM + PLUMED well-tempered metadynamics on the
Pocket-5 Rg coordinate, with an unbiased release simulation (OpenMM, no bias) seeded at the low-energy
druggable frame for the metastability/druggability test. Calibration: a nuclear-receptor LBD panel.
Selectivity: BLOSUM62 alignment versus NR4A1 (P22736) and NR4A2 (P43354); the same metadynamics pipeline run
on all three paralogues for state-matched ensembles. Docking: smina of a ChEMBL NR4A library into each
paralogue's opened conformer. Endpoint free energy: single-snapshot and multi-snapshot one-trajectory MM-GBSA
(OpenFF/GAFF-2.11, GBn2 implicit solvent, AM1-BCC charges), read as verdict/direction. De-novo design:
DiffSBDD pocket-conditioned diffusion on the druggable release frame, with RDKit cheminformatics,
structural-alert, and pose-handle-contact triage. Specificity control: 38 non-NR4A marketed drugs through the
identical funnel, used as a calibrated null (single- and multi-snapshot). Full parameters and the pre-
registered gates are in SI §1–§2. Jobs were run as managed cloud GPU/CPU tasks; all analysis code is public
(Data & Code Availability).

## 5. Limitations
This work is in-silico throughout; no molecule was synthesized and there is no wet-lab validation, so all
candidates are predictions. The receptor is an AF2 model (NR4A3 is uncrystallized); the metadynamics
addresses the single-snapshot limitation but the opening free-energy frontier is not fully converged, and
the druggability case is a **feasibility** result — an induced-fit cavity druggable ~a quarter of the time,
not an always-open pocket. The lead `denovo_401` is a **receptor-frame-dependent** predicted-selective
chemotype: it exceeds a same-tier decoy null in its design frame but not in the biased metad-opened frame, and
that null controls the scoring step only — not the generative step (the candidate, unlike the decoys, was fit
to the receptor) or the best-of-N selection — so it is a **de-noised foothold, not a controlled specificity
result** (the generated set is not enriched over the decoys, bounding the confound). A pre-FEP species sweep
resolved denovo_401's stereochemistry (selectivity is stereochemistry-robust; the generated diastereomer is
near-optimal) and **withdrew the second candidate denovo_111** (its physiological cation reverses selectivity).
denovo_401's endpoint MM-GBSA is single-trajectory and not affinity-grade, and selectivity free-energy
perturbation remains un-run (the one remaining affinity tier). The degradation-selectivity (ternary) pipeline
is validated on the CRBN/IMiD control (in-distribution, a sanity check not a generalization test); the actual
NR4A3/NR4A1/NR4A2 ternaries were then predicted for a **representative** denovo_401-PROTAC and all three form an
equally productive complex — so the ternary is a single-pose, single-linker prediction that shows the mechanism
is geometrically viable but **not** a paralogue-selectivity lever (Boltz gives one pose, not the cooperativity/
productive-ensemble that sets real degradation selectivity; a different linker could differ). Binding
selectivity is necessary but not sufficient for *degradation* selectivity. The therapeutic rationale assumes EMC remains dependent on NR4A3 for
survival — supported by a transfer prior from reliably fusion-addicted EWSR1/FET-fusion sarcomas and by
EMC-native evidence that the fusion is a functional transcriptional driver [Filion 2009], but **not yet
demonstrated in EMC**; the decisive acute-degradation (dTAG) experiment is delegated to wet-lab collaborators.
The strongest honest claim is that NR4A3's orthosteric pocket is *computationally tractable as a dynamic,
induced-fit site*, and that a selective warhead can be *designed for, and predicted to have*, the intended
profile — not that a selective degrader has been achieved.

## Data & Code Availability
All analysis code, input models, and result summaries are in the public project repository
(`github.com/trimcrae/Rare-cancers`, `research/`); large simulation trajectories and endpoint-energy outputs
are available on request. The pre-registration and deviation log (SI §1), pre-registered gate outcomes (SI §2), full
selectivity-architecture analysis (SI §3), and adversarial self-review (SI §4) are provided as
Supplementary Information.

## Competing interests / Funding
No funding was received for this work. The author declares no competing interests.

## AI-assistance statement
Computational pipelines, analysis, and manuscript drafting were carried out with substantial assistance from
an AI coding assistant (Anthropic Claude), under human direction; all results derive from the described,
reproducible computational methods.

## References
*(Collate to journal format before submission; DOIs/PMIDs verified against Crossref + Europe PMC.)*
- Wang Z, et al. *Nature* 423:555–560 (2003). PMID 12774125. (Nurr1; PDB 1OVL.)
- de Vera IMS, et al. *Structure* 27(1):66–77.e5 (2019). doi 10.1016/j.str.2018.10.002. (Nurr1 breathing pocket.)
- Lanig H, et al. *PLoS ONE* 10:e0135246 (2015). doi 10.1371/journal.pone.0135246. (MD cryptic pocket in Nur77/NR4A1.)
- Zaienne D, et al. *ChemMedChem* 17(16):e202200259 (2022). doi 10.1002/cmdc.202200259. (Merk group; experimental druggability of NOR-1/NR4A3 — fragment-derived low-µM inverse agonist.)
- Safe S, Oany AR, Tsui WN, et al. *Transcription* 16:224–260 (2025). doi 10.1080/21541264.2025.2521766. (Review; NR4A3-selective indole-3-carbinol analogues de-repress MYC.)
- Willems S, Morozov V, Marschner JA, Merk D. *J Med Chem* 68:19955–19970 (2025). doi 10.1021/acs.jmedchem.5c00459. (NR4A1/2/3 chemical-probe audit; vetted tool set; many putative NR4A ligands don't bind.)
- Munoz-Tello P, Kojetin DJ, et al. *J Med Chem* (2020). PMID 33289551; doi 10.1021/acs.jmedchem.0c00894. (NMR: amodiaquine/cytosporone B bind NR4A2 LBD; celastrol/C-DIM12 don't — disciplines the repurposed matrix.)
- Stiller T, Merk D. *J Med Chem* 66(22):15362–15369 (2023). doi 10.1021/acs.jmedchem.3c01467. (Fatty-acid-mimetic NR4A ligands, sub-µM, NOR-1/NR4A3 tested.)
- Rajan S, et al. *NeuroMolecular Med* (2022). PMID 35482177; PDB 5YD6. (PGA2 covalent Cys566 adduct in Nurr1 LBD — covalent-warhead precedent.)
- López-García Ú, Vietor J, Marschner JA, Heering J, Morozov V, Wein T, Merk D. *Commun Chem* 8:159 (2025). doi 10.1038/s42004-025-01553-8. (Vidofludimus/Nurr1; allosteric surface pocket; canonical pocket occluded — the challenge §2.1 engages.)
- Wang L, Xiao Y, et al. *J Exp Med* 221(3):e20231519 (2024). PMID 38334978; doi 10.1084/jem.20231519. (NR-V04: NR4A1 PROTAC sparing NR4A2/NR4A3 — paralog-selective degradation precedent.)
- Haller F, et al. *Nat Commun* 10:368 (2019). doi 10.1038/s41467-018-08069-x. (AciCC = NR4A3 over-expression.)
- Khan J, et al. *Cancers* 15(13):3373 (2023). doi 10.3390/cancers15133373. (AciCC epidemiology.)
- Chen J, et al. *Nature* 567:530–534 (2019). doi 10.1038/s41586-019-0985-x. (NR4A T-cell exhaustion.)
- Mullican SE, et al. *Nat Med* 13:730–735 (2007). doi 10.1038/nm1579. (Nr4a1/Nr4a3 co-loss → AML.)
- Safe S, Karki K. *Mol Cancer Res* 19(2):180–191 (2021). doi 10.1158/1541-7786.mcr-20-0707. (NR4A paradoxical roles.)
- Filion C, et al. *J Pathol* 217(1):83–93 (2009). PMC4429309. (EWSR1/NR4A3 transactivates PPARG in EMC.)
- Brenca M, et al. *J Pathol* 248:239–251 (2019). PMID 31020999; doi 10.1002/path.5284. (Ectopic fusion expression recapitulates EMC phenotype; 5′ partner shapes the transcriptome.)
- EMC variant-fusion series (NR4A3 = shared >90 % driver, ≥6 partners): Agaram *Hum Pathol* 45:1084 (2014); Wei *Genes Chromosomes Cancer* (2021, PMID 34124809, SMARCA2); Warmke *GCC* (2023, doi 10.1002/gcc.23144, TAF15 methylation); Wilbur HC *JCO PO* (2022, PMID 36103645, doi 10.1200/PO.22.00039, PGR).
- Stacchiotti S, et al. *Cancers* 12(9):2703 (2020). doi 10.3390/cancers12092703. (EMC state of the art.)
- Methods: AlphaFold2 (Jumper 2021); fpocket (Le Guilloux 2009); OpenMM; PLUMED (Tribello 2014); DiffSBDD;
  smina; OpenFF/GAFF-2.11. Controls: PPARγ 2PRG, ERα 1ERE; NR4A holo 4JGV/6KZ5/5Y41.
