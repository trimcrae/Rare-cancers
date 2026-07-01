# Computational design of a selective NR4A3 degrader: opening a cryptic pocket in a "ligand-independent" nuclear receptor

> **ACTIVE LEAD MANUSCRIPT (result paper).** Target-centric paper on the NR4A3 degrader, split out from
> the EMC-program roadmap ([`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md)) on 2026-06-25 per
> [`nr4a3-degrader-paper-positioning.md`](./nr4a3-degrader-paper-positioning.md). The roadmap remains
> the EMC-program paper (driver framing + the fusion-specific ASO / immuno / registry routes); this
> paper is the degrader's own publish-to-convince deliverable, led by the target, with EMC as the lead
> clinical application among several NR4A3/NR4A-degradation indications.

*Draft (2026-06). Authors/affiliations TBD. In-silico design + feasibility study — no wet lab; no
molecule synthesized. Every claim is sourced or computed and labelled with its weight. The 30 ns
production metadynamics is **complete and production-length; the closed basin is well-sampled, but the
opening frontier of F(Rg) is not fully converged** (so the free-energy numbers below are read in the
well-sampled basin region and treated accordingly — §2.2). The headline structural numbers are from the
30 ns run, and the 5 ns validation is retained only where explicitly labelled as the preliminary
cross-check. An adversarial self-review of this draft, with the deficiencies it surfaced and the fixes
applied, is in [`nr4a3-degrader-paper-redteam.md`](./nr4a3-degrader-paper-redteam.md). Display-items plan
(figures + tables): [`nr4a3-degrader-figures.md`](./nr4a3-degrader-figures.md).*

## Abstract
NR4A nuclear receptors (NR4A1/2/3) are textbook "undruggable" transcription factors: the canonical
Nurr1/NR4A2 crystal structure shows a ligand-binding pocket occluded by bulky side chains, and NR4A3 has
no experimental structure at all. Yet NR4A3 is a compelling **selective** degradation target — it drives
two cancers by *gain of NR4A3*: extraskeletal myxoid chondrosarcoma (EMC; EWSR1/TAF15::NR4A3 fusion,
which retains a near-intact NR4A3 ligand-binding domain) and acinic cell carcinoma of the salivary glands
(AciCC; NR4A3 over-expression via enhancer hijacking), and in both the goal is to remove NR4A3 while
**sparing NR4A1/2** (whose loss is toxic, notably leukaemogenic). We present a **computation-only**
program to design a **selective NR4A3 degrader**. (1) Calibrated against a
nuclear-receptor panel, the NR4A3 orthosteric pocket is borderline/occluded in the static AlphaFold
model (fpocket druggability 0.495, below the calibrated drug-bound band of 0.53–0.68), consistent with
the family's reputation — and we show the apparent "0.80 druggable" reads reported for Nurr1 are a
*non-orthosteric* cavity present even in the occluded crystal, not a model artifact. (2) **Well-tempered
metadynamics drives the orthosteric pocket to breathe into transiently druggable conformations**: under a
bias on the pocket's radius-of-gyration coordinate, the *same orthosteric Pocket-5* fpocket druggability
(the metric on which the static 0.495 and the calibrated threshold are defined — not the non-discriminating
"max-anywhere" cavity) reaches **0.931** (peak over the 600 opened frames; a non-negligible fraction clear
the calibrated threshold, the 5 ns validation gave 0.751). This is a **biased-ensemble structural-
feasibility readout** — fpocket druggability is a standard metric and the rise reflects a hydrophobic,
*enclosed* breathing cavity (a merely splayed pocket would score lower), but its magnitude on biased-MD
frames is not a like-for-like match to the *static* drug-bound crystal sites (0.53–0.68), so we do not
claim it "beats" that band (§2.2, §5) — yet it is the first
pocket-dynamics evidence for NR4A3, paralleling the experimentally demonstrated *dynamic, breathing* pocket
of Nurr1 (de Vera 2019) and an MD-revealed cryptic pocket in Nur77. We are careful that the free-energy
profile shows **no separate opened basin** (a single closed basin with a rising wall); the druggable
conformations are reached by *basin-internal breathing*, not a two-state cryptic switch. The decisive test
of whether these conformations are physically populated or bias-induced strain is an **unbiased "release"
run seeded at the low-energy druggable frame: it finds the breathing-open geometry *metastable* (3/3
unbiased replicas held 5 ns, mean drift 0.025 nm) and *druggable in ~24 % of unbiased frames* (fraction ≥
D\*=0.53 of 0.20, peak 0.842; static 0.495) — i.e. a thermally-real, induced-fit / conformational-selection
cavity druggable about a quarter of the time, not a static always-open pocket and not a bias artifact.**
(3) We map 7
NR4A3-vs-NR4A1/NR4A2 divergent pocket residues as **selectivity handles** (5 of which stay pocket-facing
in the opened, druggable ensemble — a measured, not assumed, property), enabling a tunable selectivity
profile. (4) Treating the opened pocket as a *programmable* design axis, we run the **same cryptic-pocket
metadynamics on NR4A1 and NR4A2** to build **state-matched opened-pocket ensembles for all three
paralogues**, and dock one candidate library into each — yielding a per-candidate **selectivity
fingerprint across the NR4A family** (tunable from NR4A3-selective to pan-NR4A) and removing the
opened-target-vs-static-off-target bias that confounds naive selectivity docking. (5) Re-scoring the matrix
poses with **endpoint MM-GBSA** shows the *repurposed* ChEMBL actives mostly do **not** hold up as
NR4A3-selective under a physics-based energy model (the apparent lead cytosporone B *reverses*, consistent
with its known NR4A1 agonism) — motivating **de-novo design**. (6) We therefore run a **pocket-conditioned
generative campaign** (DiffSBDD, conditioned on the divergent handles, against the thermally-real
druggable *release* conformation) and funnel the generated, lead-sized molecules through the same dock +
MM-GBSA selectivity pipeline: this yields candidates the single-snapshot MM-GBSA *labels* NR4A3-selective — **but a decoy
control (added 2026-06-30) shows that label is non-specific: 39 % of non-NR4A marketed drugs (caffeine,
ibuprofen, …) score "NR4A3-selective" by the same metric, and the de-novo set is *not enriched* over that
null — so a *raw* margin is not selectivity evidence.** We therefore use the decoy
run as a **calibrated null** (95th-percentile margin = +13.1 kcal/mol): against that bar, the developable
candidate **`denovo_111`** (a clean fluoro-phenyl-pyrrolidine, +15.7, favoured in both receptor states) is
the **one candidate that clears the decoy null** — the program's first calibrated above-null NR4A3-selective
hit and the lead for an ongoing optimization campaign (the earlier raw "three MM-GBSA-confirmed selective"
headline led by the artifact `denovo_15` is retracted in favour of this decoy-calibrated read; §2.5, §5) — the first
*designed* NR4A3-selective warhead candidate this program has produced (a screening-grade prediction, not a
synthesized or affinity-validated lead). (6b) Building the **multi-snapshot endpoint-MM-GBSA de-noising
tier** the §2.5 plan named, we find the single-snapshot harvest is noise-dominated (the single-snapshot best,
`denovo_393` +18.34, collapses to −2.95 ± 3.65) — but **one candidate survives de-noising: `denovo_401`
(+12.83 ± 2.98, margin − SD = +9.85; NR4A3 ΔG −38.18 kcal/mol, both paralogues ~13–15 weaker)**, the first
multi-snapshot-confirmed NR4A3-selective candidate and the lead justified to advance to FEP. The single-snapshot
foothold **`denovo_111` has since been de-noised too (+14.60 ± 4.10, margin − SD = +10.50)**, so the program
carries **two** de-noised, decoy-null-clearing footholds (two of ~11 multi-snapshot-tested), with `denovo_401`
the lead because it is additionally characterized across receptor frames. Both remain
single-trajectory GB-implicit MD, not FEP; and the decoy-null clearance is **receptor-frame-dependent** and
**does not control the generative step that produced it** (F16): the decoy null scores marketed drugs through
the same *docking*, but the leads were DiffSBDD-fit to the NR4A3 release pocket they clear the null in, and are
the best of ~200 generations — so "above-null" here is a de-noised foothold, not a fully-controlled specificity
result (though the confound is bounded: the generated set is *not* enriched over decoys, so being
generated-for-NR4A3 does not uniformly inflate the margin):
it clears the matching multi-snapshot decoy null **in its release/design frame** (95th-pct +6.69, max decoy
+7.10, so margin − SD +9.85 sits above the whole null), but in the biased **metad-opened** frame both its
margin and the decoy null inflate — the metad-frame decoy 95th-pct is +17.70 (max +24.74), and `denovo_401`'s
+7.44 there does **not** clear it (~84th pct) — so that frame is a poor, promiscuous discriminator and the
specificity-controlled result is release-frame-specific, not universal — §2.6). (6c) A **selectivity-architecture analysis** (§2.7) shows the orthosteric pocket is the *most*
paralogue-divergent zone of the LBD (70 % of warhead-contact residues divergent vs 43 % across the rest of the LBD) — so
binder selectivity is handle-rich but druggability/noise-limited — and concludes selectivity is a
**multiplicative budget** whose factors compound: keep the binder selective (`denovo_401`/`denovo_111` are
decoy-null-screened footholds — not fully control-validated, since the null does not control the generative
step, F16) **and** optimized for affinity. The hoped-for *additional* lever — **paralogue** selectivity from the
**ternary** — **has now been run (§2.4, F18) and does not materialize** for a representative `denovo_401`-PROTAC:
NR4A3/NR4A1/NR4A2 form equally productive ternaries (comparable within-noise confidence, each presenting an
exposed Lys within ubiquitin reach of CRBN), so the ternary does **not** compound the binder's NR4A1 margin;
degradation selectivity therefore rests on the **binder** (+ pharmacokinetics/CNS-exclusion for NR4A2), with
**linker/exit-vector engineering** the only remaining untested route to ternary selectivity, while
**fusion-vs-wild-type** selectivity is sourced not from the degrader at all (unobtainable here) but from the
complementary ASO. We read this honestly: `denovo_15` itself carries generative-model
**stability/synthesizability liabilities** (a carbamic acid, a 1,3-cyclopentadiene, an imine and an exocyclic
alkene; no aromatic ring; SAscore 5.08 — *above* the campaign's own ≤4.5 synthesizability cut), so it is a
selective **chemotype/pose hypothesis to be re-designed into a stable, synthesizable analogue**, not a
developable molecule; the durable result is that the de-novo funnel produces selectivity that survives a
physics-based energy model where repurposed matter did not. We also **ran the NR4A3/1/2–CRBN–PROTAC ternary**
(a representative `denovo_401`-PROTAC; Boltz-2, control-validated on CRBN/lenalidomide): all three paralogues
form a productive-geometry-proxy ternary, so the ternary is a *tested-negative* selectivity lever (§2.4/F18) —
selectivity, on current evidence, is a binder-carried budget. The affinity-grade **selectivity FEP** is the one
remaining SOTA tier (queued, pending a GPU-setup change). The work is governed by a **pre-registered falsification
scheme** (calibrated thresholds fixed before the production results). The NR4A3-selective agent — binding
the NR4A3 LBD shared by the EMC fusion and over-expressed wild-type NR4A3 — is the lead, addressing
**EMC, acinic cell carcinoma, and the broader NR4A3-rearranged sarcoma spectrum**; a deliberately
**pan-NR4A** agent is a distinct second design mode for *ex-vivo* immuno-oncology (reversing T-cell
exhaustion, which needs all three NR4As degraded; Chen 2019), while the AML-causing NR4A1+NR4A3
combination is an explicit **anti-target** the matrix is used to design *away* from. The set is bounded by NR4A3's
tumour-suppressor roles elsewhere (AML, HCC). EMC is the entry point, not the endpoint.

## 1. Background and rationale
NR4A receptors are constitutively active orphan nuclear receptors whose canonical ligand pocket is
collapsed/occluded in crystal structures (Nurr1, PDB 1OVL; Wang 2003), the structural basis of their
"undruggable" reputation. That reputation is a statement about *static* structures: Nurr1's pocket is in
fact **dynamic and expands** from the collapsed crystal conformation to bind fatty acids (de Vera 2019),
an MD study reported a cryptic druggable pocket in Nur77, and validated NR4A ligands engage
cryptic/surface sites. NR4A3 itself has **no experimental structure and no published pocket-dynamics
analysis** — the gap this paper fills. Full reconciliation of the "undruggable" reputation with our
findings, with references and the NR4A-family precedent, is in
[`../modalities/nr4a3-druggability-reconciliation.md`](../modalities/nr4a3-druggability-reconciliation.md).

Because occupancy pharmacology is precluded by the collapsed pocket, the apt modality is **degradation**:
recruit the retained, ordered NR4A3 LBD to an E3 ligase and remove the protein. This is target-generic
(it degrades NR4A3 whether wild-type or in the EMC fusion), which is why the program is framed around
NR4A3 rather than EMC specifically.

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
it on a nuclear-receptor panel that includes the occluded 1OVL crystal as a de-facto negative; the score
itself is not in question. Two honest qualifications apply to the **0.931** specifically. First, it is the
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
below). **Gate 1 (a genuine cryptic *opening*) is met only in a weaker form than pre-registered:** Gate 1
asked for an accessible *minimum or shoulder* at an opened Rg "not just biased excursions," but F(Rg) is
**monotonic — a single closed basin and a rising wall, with no separate opened minimum**. So the druggable
conformations are reached by **basin-internal breathing**, not a two-state cryptic opening; this is
consistent with de Vera's breathing Nurr1 pocket, but it means "opened *state*" overstates — there is one
basin whose thermal fluctuations transiently expose a druggable cavity. **Gate 3 (energetic accessibility)
is provisionally met.** The naive closed→fully-open cost is ~38 kcal/mol, but that is the cost to the
*most-open* edge (Rg 1.06) at the **under-converged sampling frontier**, not a *druggable* state:
correlating per-frame druggability with F(Rg) shows the pocket is already druggable (fpocket 0.80) at
Rg ≈ 0.72 — in the well-sampled basin region — at only ~0.76 kcal/mol. The caveat (disclosed, not buried):
both numbers are read off the *same* incompletely-converged biased F(Rg), so the 0.76 rests on the
basin region being better sampled than the frontier (it is, but it is a single biased profile). The
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
induced-fit cavity that is thermally, spontaneously druggable about a quarter of the time** — the expected
behaviour of a nuclear-receptor cryptic site (cf. de Vera 2019, Nurr1). So **Gate 3 is cautiously passed as
a conformational-selection target**: a warhead must select-and-stabilise the ~24 % druggable conformations,
not occupy a static pocket. All downstream design (below) is therefore anchored to a **druggable unbiased
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

### 2.3 Selectivity handles for an NR4A3-selective (NR4A1/2-sparing) warhead
Aligning the NR4A3 pocket to NR4A1/NR4A2 ([`../modalities/nr4a-selectivity.json`](../modalities/nr4a-selectivity.json))
identifies, among the **10 Pocket-5 lining residues**, **7 divergent** ones — L406, T407, T410, R412,
I484, I531, L534 — as selectivity handles. All 7 are within the metadynamics CV; of these the opened,
druggable ensemble keeps **5 pocket-facing** (L406, T410, I484, I531, L534 — §2.2), so those five are the
realistically *engageable* handles a warhead can exploit (T407 and R412 mostly splay outward).

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
conserved pocket residues; for ex-vivo immuno-oncology) — §3.

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
**anti-target** cells (§3). The **anti-target cell is empty** (no candidate engages NR4A1+NR4A3 while
sparing NR4A2 — nothing to design away from in this library), and the NR4A3-leaning leads are repurposed NR4A
actives (e.g. cytosporone B, amodiaquine). This makes the divergent-handle map a *demonstrated, tunable*
design axis rather than an assertion — but the docking dG are within noise, so they nominate chemotypes,
not a lead.

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
candidate.) Once a warhead SMILES exists, the NR4A3–PROTAC–E3 ternary-complex model (`nr4a3_ternary.py`,
Boltz-2) scores degradable-lysine geometry per paralogue. **This pipeline is validated on a positive
control:** predicting the CRBN + lenalidomide complex, Boltz-2 **seats the glutarimide in CRBN's
tri-tryptophan pocket** — closest heavy-atom approach 2.85 Å to W380 (3.4 Å to W386/W400), with high
confidence (ligand-iPTM 0.99) — recovering the experimentally known IMiD binding mode. This is a **necessary
sanity check, not a demonstration of generalization** (F18): CRBN/IMiD is one of the most-deposited ligase
complexes in the PDB and is almost certainly in Boltz-2's training data, so recovering it is
memorization-consistent and says little about performance on an **AF2-modeled cryptic NR4A3 LBD** with a
**de-novo** warhead and a possibly different E3. **We nonetheless ran that step (2026-07-01, F18 mitigation):**
we built a **representative `denovo_401`-PROTAC** (warhead–PEG2–succinyl–lenalidomide, RDKit-validated
C41H56N4O8, glutarimide intact) and predicted the **NR4A3/NR4A1/NR4A2-LBD + CRBN + PROTAC** ternaries. The
result is honest and instructive: **all three paralogues form a productive-geometry-proxy ternary** — the
PROTAC bridges the LBD and CRBN (2.5–3.1 Å each side) and each LBD presents an exposed lysine within
ubiquitin reach of CRBN (NR4A3 K195 3.12 Å, NR4A1 K53 2.34 Å, NR4A2 K175 3.96 Å) — with **comparable,
within-Boltz-noise confidence** (iptm 0.72/0.83/0.82). So for this representative linker the **ternary adds no
NR4A3 degradation-selectivity**: it does *not* "multiply" the binder's paralogue margin the way §2.7 hoped;
degradation selectivity, if any, rests on the **binder** margin (denovo_401/111), with **linker/exit-vector
design** the (untested) lever that might introduce ternary selectivity. Caveats: one arbitrary linker; Boltz
gives a single ternary pose (not the productive-ensemble/cooperativity α that sets real degradation
selectivity); Lys-proximity is a CRBN-only proxy (no full CRL4^CRBN + E2~Ub). This is not a formality: the
binding-selectivity matrix is a **necessary but not sufficient** filter, because a degrader's actual
selectivity is set by the *ternary complex* — a non-selective binder can degrade selectively and a selective
binder can fail to degrade; the ternary result above shows the *converse risk* here (a selective binder whose
ternary is non-selective). **No molecule is synthesized; this is design prep.** Run instructions + program state:
[`../modalities/nr4a3-degrader-next-steps.md`](../modalities/nr4a3-degrader-next-steps.md).

### 2.5 De-novo design yields NR4A3-selective candidates: decoy-calibrated, then multi-snapshot-confirmed (§2.6)
Because the repurposed library produced no candidate that survives MM-GBSA as NR4A3-selective (§2.4), we
ran a **pocket-conditioned de-novo generative campaign** and put its output through the *same* selectivity
funnel. (1) **Receptor.** We anchored generation and docking to a **druggable unbiased *release* frame**
(`nr4a3_release_druggable.py`: Rg ≈ 0.737, confirmed fpocket druggability 0.667, in the calibrated drug-bound
band) — the thermally-real induced-fit conformation from §2.2, not the biased-metad frame — keeping a small
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
its thermally-real **unbiased release** frame (fpocket 0.667) against the **biased-metad** NR4A1 frame 524
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

**Decisive control (2026-06-30): the single-snapshot MM-GBSA selectivity verdict fails a decoy test, so
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
`denovo_111` — is the carried lead; `denovo_111` is the earlier single-snapshot foothold, since **also
multi-snapshot-confirmed** (+14.60 ± 4.10, §2.6). So "the one candidate that clears the null" is batch-relative,
not a global claim, and the program now carries **two** de-noised footholds.)* So the
honest read is **not** "no selectivity"; it is "**raw single-snapshot MM-GBSA is
non-specific, but decoy-calibration isolates `denovo_111` as a genuine foothold**." The de-novo program
continues as a **lead-optimization campaign around `denovo_111`** — scaffold-seeded generation conditioned on
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
| **`denovo_111`** (the §2.5 single-snapshot foothold, now de-noised — run 28516596503) | +15.70 | **+14.60 ± 4.10** | **+10.50** | **holds** (confirmed_selective) |

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
selectivity FEP**. The single-snapshot foothold `denovo_111` **has since been de-noised too** (run 28516596503):
its multi-snapshot margin **+14.60 ± 4.10 (margin − SD = +10.50)** likewise holds and clears the release-frame
multi-snapshot decoy null — so there are now **two** de-noised, decoy-null-clearing footholds, not one.
`denovo_401` remains the *lead* because it is additionally characterized across receptor frames (the
state-matched metad re-dock, below); `denovo_111` has been de-noised only in the release/design frame and its
frame-dependence is not yet characterized (and its SD, 4.10, is larger).

**Honest weight (a fresh red-team should hold these).** `denovo_401` clears the **FEP-worthiness bar this
program pre-committed to** (multi-snapshot margin − SD > 0, favourable NR4A3 binding, stable pose) — which is
a real upgrade over a single-snapshot point estimate — but it is **single-trajectory GB-implicit MD, not
FEP**, **unsynthesized**, and **un-validated**. It is also the **best-of-~10** candidates multi-snapshot-tested
(and best-of-~200 generated), so its +12.83 point estimate carries a **selection (winner's-curse) bias on top
of the reported ±2.98 SD** — the same extreme-value logic that demotes `denovo_393`'s single-snapshot +18.34
applies to picking `denovo_401` as the survivor; an independent re-run (or FEP) is what would de-bias it. The decoy null (§2.5) was originally computed at
*single-snapshot*, so the matching question was whether "+12.83 survives de-noising" is the same as "+12.83
is above a *multi-snapshot* null." **That control has now been run (2026-06-30, run 28473680997): re-scoring
all 38 decoys through the identical multi-snapshot tier gives a far tighter null — mean −3.47, 95th
percentile **+6.69**, max decoy **+7.10**, `confirmed_selective` 11/38 (29 %) — vs the single-snapshot
+13.1 / +16.46 / 39 %.** Against that re-calibrated bar **`denovo_401`'s +12.83 ± 2.98 clears the
multi-snapshot 95th percentile and exceeds the single highest decoy even after subtracting its SD
(margin − SD = +9.85 > +7.10)** — so the margin is not merely de-noised but **above a decoy null recomputed at
the same tier.** *(Read this at its true weight — F16. That null controls the **docking/MM-GBSA scoring** step
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
whole-cloth artifact (the decisive resolution is FEP, the queued SOTA gate).)* **A receptor-robustness check (a
fully state-matched re-dock — NR4A3 in its *metad-opened* frame rather than the release frame — then the same
multi-snapshot rescore; runs 28473682532/28480041030) keeps `denovo_401` NR4A3-favoured but weaker:
+7.44 ± 4.18 (ΔG NR4A3 −32.37 vs NR4A1 −24.93 / NR4A2 −22.80)** — so the selectivity *direction* is robust
across receptor frames (not a release-frame artifact), but the *magnitude* is frame-dependent. **The matching
metad-frame decoy null has since been run (run 28483612927), and it forces an honest narrowing: `denovo_401`
does *not* clear it.** In the metad-opened frame the decoy null *balloons* — mean +1.59, 95th percentile
**+17.70**, max decoy **+24.74** (vs the release frame's +6.69 / +7.10) — because the biased wide-open pocket
scores *most* drug-like matter as strongly NR4A3-favoured (diphenhydramine +24.74, lidocaine +22.08); against
that inflated null `denovo_401`'s +7.44 sits at only ~the **84th percentile** (6/38 decoys score higher). So the
metad-opened frame is a **poor, promiscuous discriminator**, and `denovo_401`'s specificity-controlled result is
**release-frame-specific**: real in its unbiased *design* receptor, but it does **not** generalise to the
biased-open frame. The honest, narrowed claim: *`denovo_401` is the one candidate whose NR4A3-selectivity
survives ensemble de-noising **and** clears a like-for-like multi-snapshot decoy null **in its release (design)
receptor** — a real but **receptor-frame-dependent** signal (it fails the null in the biased metad-opened frame,
which is itself non-discriminating), consistent with §2.7's finding that this cryptic pocket is a fragile place
to source a robust margin.* It stays the justified single candidate to advance to FEP, but as a **frame-dependent
hit, not an unqualified one** — and the right resolution is ensemble scoring over the druggable release
sub-ensemble rather than any single frame (method-watch: better induced-fit/ensemble affinity). **A further 6-candidate multi-snapshot
batch (`denovo_921/277/804/431/838` + the `denovo_924` negative control) returned *no additional survivor*:
the best two, `denovo_921` (+4.22 ± 5.23) and `denovo_277` (+2.23 ± 3.52), are positive-margin but **fail
the margin − SD > 0 bar**, while the negative control stayed non-selective.** So across ~11 candidates now
multi-snapshot-tested, **two survive — `denovo_401` (+12.83 ± 2.98) and `denovo_111` (+14.60 ± 4.10)** — both
clearing the margin − SD > 0 bar and the release-frame multi-snapshot decoy null. Two of ~11 is still a low
hit-rate (the funnel does **not** *abundantly* yield de-noising survivors), but it is **not** the n=1 the earlier
draft reported, and the negative control failing throughout keeps the discrimination trustworthy — consistent
with §2.7's picture of a cryptic pocket that is a *fragile but not empty* place to source a selectivity margin.

### 2.7 Selectivity architecture: the pocket is a selectivity *hotspot*, and selectivity is a binder × ternary budget
Treating "where should selectivity come from" as its own optimization (full analysis:
[`nr4a3-degrader-selectivity-architecture.md`](./nr4a3-degrader-selectivity-architecture.md)) yields a
computed result (not asserted) that **contextualizes — not contradicts — the binder campaign**. Comparing NR4A1/2/3 divergence in the
orthosteric cryptic pocket (the warhead's contact residues) against the LBD-wide pocket-residue census
(same `nr4a-selectivity.json` alignment):

| residue set | n | divergent vs ≥1 paralogue | divergent vs **both** paralogues |
|---|---|---|---|
| **orthosteric cryptic pocket (warhead contacts)** | 10 | **70 %** | **60 %** |
| LBD-wide pocket census | 148 | 45 % | 28 % |
| non-orthosteric remainder (surface/PPI proxy) | 138 | 43 % | — |

The warhead pocket is **~1.6× more paralogue-divergent than the rest of the LBD** — it is the *most*
divergent zone, a selectivity hotspot, not a conserved wall. So the binder's selectivity problem was
**never handle scarcity**; it is **pocket druggability + affinity-margin robustness** (the cryptic, least-
druggable-of-three pocket, and the MM-GBSA noise floor of §2.5–2.6). This carries three design conclusions:

1. **Selectivity is a *multiplicative* budget** across binding × ternary × kinetics — the factors
   **compound** (binder *and* ternary *and* kinetics); none *replaces* another. A selective binder is
   therefore strictly valuable and **remains the program's primary goal** — `denovo_401`'s pocket
   selectivity is a **decoy-null-screened first factor** (it exceeds a same-tier multi-snapshot decoy null in
   its design frame, §2.6 — a foothold, not fully control-validated, since that null does not control the
   generative step, F16), not a discardable bonus. The architecture's contribution is the *complementary* point:
   because that binder selectivity is **fragile** in this cryptic, least-druggable-of-three pocket (two
   survivors out of ~11 multi-snapshot-tested; §2.6), a *robust* degrader would ideally **add** ternary
   selectivity *on top of* the binder's — **but the ternary experiment has now been run (§2.4, F18) and, for a
   representative `denovo_401`-PROTAC, does *not* add it** (all three paralogues form an equally productive
   ternary). So on current evidence the full budget rests **more heavily on the binder** than this architecture
   originally hoped: binder optimization must pursue **affinity, a productive linker exit vector, *and* the
   paralogue selectivity `denovo_401`/`denovo_111` already show**, and the ternary is *not* a reliable
   additional lever unless **linker design** can be shown to introduce ternary selectivity (untested). The
   "binding selectivity ≠ degradation selectivity" point (caveat 5) now cuts the *other* way here: a selective
   binder whose ternary is non-selective.
2. **Paralogue selectivity then compounds per-paralogue via matched levers — but the ternary is now a *tested,
   negative* lever, not a hoped-for one:** NR4A1 (the AML-safety-net, mandatory) — `denovo_401` discriminates it
   at the binder level (ΔG NR4A3 −38.18 vs NR4A1 −22.98, §2.6), but the **ternary does *not* multiply that
   margin** for the representative PROTAC (§2.4/F18: NR4A1 forms an equally productive ternary), so NR4A1
   selectivity currently rests on the **binder** (plus, speculatively, linker engineering); NR4A2 (the
   molecularly hardest case — I531 is NR4A3=NR4A2-identical, §2.3) is topped up from **pharmacokinetics /
   CNS-exclusion**, since its tox is CNS-localized and EMC is a peripheral sarcoma.
3. **Fusion-vs-wild-type selectivity is unobtainable from the degrader at any stage** (the warhead binds a
   LBD identical in fusion and wild-type, and the ternary forms at that LBD, nowhere near the N-terminal
   fusion partner). It is the **ASO's** job (RNA-level junction targeting); the degrader's honest scope is
   paralogue selectivity + accepted wild-type-NR4A3 loss, **not** tumour-exclusivity. Effort spent making
   the degrader fusion-selective is effort misallocated.

(Caveat: the "surface/PPI proxy" row uses pocket-lining residues across all cavities as a stand-in for the
true E3-facing interface, which is not yet mapped; the real interface conservation should be computed on the
predicted ternary before this comparison is load-bearing — flagged in the architecture doc §8.)

## 3. Indication landscape — a programmable selectivity matrix (EMC is the entry point, not the endpoint)
Detail + references: [`nr4a3-degrader-broader-indications.md`](./nr4a3-degrader-broader-indications.md).
The family-wide ensembles (§2.4) let a degrader be designed for a chosen NR4A *combination*. A cell of
that matrix is a real application only where the disease wants those paralogue(s) **degraded** (direction
matters: degrading neuroprotective Nurr1/NR4A2 in Parkinson's would be the *wrong* direction, so most
single-paralogue cells are not degrader indications) — and some combinations are actively harmful. So the
matrix has three kinds of cell:

**Lead — NR4A3-selective (the validated path):**
1. **EMC** — EWSR1/TAF15::NR4A3 fusion; clean single-driver proof-of-concept.
2. **Acinic cell carcinoma (AciCC) of the salivary glands** — driven by **NR4A3 over-expression via
   enhancer hijacking** (Haller, *Nat Commun* 2019; cooperates with MYB, Lee 2020). NR4A3 is the diagnostic driver;
   a selective degrader removes it directly. AciCC is the **third most common malignant salivary-gland
   tumour** (≈6–15 % of salivary-gland carcinomas; annual incidence on the order of ~0.1 per 100,000
   [Khan 2023]), whereas EMC is **ultra-rare** (<1 per 1,000,000 per year [Stacchiotti 2020]) — so the
   same selective agent addresses a materially larger population through AciCC. (Both are rare; the
   comparison is order-of-magnitude, not a precise ratio.)
3. **Other NR4A3-rearranged sarcomas** — the EMC fusion-variant spectrum.

**Second design mode — pan-NR4A (a distinct molecule, not a contingency):** reversing CD8⁺ T-cell
exhaustion (NR4A-deficient CAR-T cells control solid tumours better; Chen, *Nature* 2019) **requires
degrading all three NR4As**. This is the *opposite* selectivity profile, deliberately designed for from
the conserved pocket residues, and scoped to **ex-vivo / transient** use (CAR-T manufacturing) so the
systemic-toxicity bound below does not apply. The same matrix that yields the selective lead yields this.

**Anti-target — NR4A1+NR4A3 (design *away* from):** NR4A1/NR4A3 are myeloid **tumour suppressors** —
combined loss causes AML (Mullican, *Nat Med* 2007); NR4A3 is also tumour-suppressive in HCC/breast/
lymphoma (Safe & Karki 2021). This cell is a liability, not an indication; the matrix is explicitly used
to *avoid* it (and is *why* NR4A1-sparing selectivity (§2.3) is mandatory for the systemic lead). Showing
the method can design **into** NR4A3-only and **away from** NR4A1+NR4A3 is itself a safety-design result.

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
Selectivity: Biopython BLOSUM62 alignment vs NR4A1/NR4A2. **Family-wide ensembles:** the *same*
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
(unrun) tier. **De-novo design:** a selectivity blueprint (`denovo_blueprint.py` → `nr4a3-denovo-blueprint.json`)
classifies the Pocket-5 lining residues into the five engageable selective handles (four discriminating
both paralogues — L406/T410/I484/L534 — and the NR4A1-only lever I531) vs the conserved core
(P411/R481/R485), weighting the both-paralogue handles in the selective campaign; DiffSBDD pocket-conditioned
diffusion (pretrained CrossDocked weights; `nr4a3_denovo.py` + `entry_denovo.py`) conditioned on the
druggable release-frame pocket / divergent handles, with a lead-size constraint and an RDKit cheminformatics
+ pose-handle-contact triage (`denovo_funnel.py`); generated candidates are funneled through the same matrix dock + MM-GBSA pipeline
(`nr4a3_matrix.py` candidate mode). Docking scores are used only as triage priors. All
parsing/mapping/classification/scoring logic is in pure, unit-tested modules (TESTING.md).

## 5. Limitations
In-silico throughout; no molecule synthesized; broader indications (§3) are **motivation, not
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

The acute, specific degradation (dTAG) test that would convert this prior into a demonstration is the
make-or-break experiment, delegated to the EMC-program paper
([`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md)); **this paper's claimed contribution is the
target's druggability/selectivity, not EMC efficacy.** The structure is an AF2 model
(NR4A3 is uncrystallized) — the MD addresses exactly the single-snapshot limitation. We state the central result at its true weight, with five caveats
made explicit rather than buried (full adversarial review:
[`nr4a3-degrader-paper-redteam.md`](./nr4a3-degrader-paper-redteam.md)):

1. **The 0.931 is a biased-ensemble peak, not a like-for-like beat of the static band.** fpocket
   druggability is a standard, validated metric (hydrophobic enclosure + polarity, not raw volume; §2.1
   anchors it on an NR panel incl. the occluded 1OVL negative), so the score itself is not in question.
   But (a) 0.931 is the **maximum over 600 frames** — report it as a distribution (fraction of frames
   ≥ D\*=0.53, met) with 0.931 as the peak; and (b) it is computed on **biased-MD** conformations, so its
   magnitude is not directly comparable to the *static* drug-bound crystal sites (0.53–0.68) — we do not
   claim it beats that band. fpocket druggability is in any case a geometric screen, not affinity. Whether
   the breathing-open geometry is physically populated vs bias-induced strain is settled by the release
   run, not by an fpocket control.
2. **No separate opened free-energy basin.** F(Rg) is monotonic (one closed basin, rising wall); the
   druggable conformations are reached by *basin-internal breathing*, not a two-state cryptic opening, so
   the pre-registered Gate 1 ("minimum or shoulder, not just biased excursions") is met only in this
   weaker sense. "Opened state" is shorthand for these breathing sub-states, not a distinct metastable
   conformation.
3. **Gate 3 accessibility — now release-confirmed as an induced-fit cavity, not always-open.** The
   ~0.76 kcal/mol cost to a druggable conformation and ~38 kcal/mol to the open edge are read off the *same*
   incompletely-converged biased F(Rg), so those numbers remain provisional; but the *independent*
   metastability test is no longer pending. The unbiased release run (seeded at the low-energy druggable
   frame) shows the breathing-open geometry is **metastable (3/3 replicas) and druggable in ~24 % of
   unbiased frames** — confirming a thermally-real, **induced-fit / conformational-selection** cavity (not a
   bias artifact), but explicitly **not** a static always-open pocket (unbiased mean druggability 0.262).
   The design consequence is real: the warhead must select-and-stabilise the ~quarter of conformations that
   are druggable, which is a harder ask than occupying a permanent pocket.
4. **Selectivity handles are a specification with an asymmetric window.** The registered handle-facing
   check confirms the handles stay pocket-facing in the druggable frames (mean 5.0/7; T407/R412 splay out,
   so five engageable). But the engageable *divergent* set is **5 vs NR4A1 and only 4 vs NR4A2** (I531 is
   conserved with NR4A2), so NR4A2 selectivity is the harder, narrower case — and these are a specification,
   not a demonstrated binding margin.
5. **Binding selectivity ≠ degradation selectivity — and that reallocates the whole selectivity problem
   (§2.7).** The §2.4 matrix is a necessary-not-sufficient filter; degradation selectivity is set by the
   per-paralogue ternary complex (the planned gating step). The selectivity-architecture analysis sharpens
   this from a caveat into a design: selectivity is a **multiplicative budget** (binding × ternary ×
   kinetics) whose factors **compound**, so the binder need not carry it *alone* — but a selective binder is
   still strictly valuable and is the primary goal (`denovo_401` and `denovo_111` are both decoy-null-screened
   footholds, not fully control-validated — F16; §2.6). The
   computed result that the orthosteric pocket is the *most* paralogue-divergent zone of the LBD
   (70 % vs 43 % across the rest of the LBD) means binder selectivity is handle-rich but
   druggability/noise-limited — so the rational plan keeps the binder selective **and** optimizes it for
   affinity + a productive exit vector. The hoped-for *additional* lever — sourcing paralogue selectivity from
   the **ternary** — **has now been tested (§2.4/F18) and, for a representative PROTAC, does not materialize**:
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
   re-calibration are now run, and `denovo_401` clears them — leaving FEP as the remaining tier.** The de-novo
   funnel originally docked an *unbiased-release* NR4A3 receptor against *biased-metad* paralogue receptors
   (asymmetry conservative for NR4A3-selectivity — §2.5), and the single-snapshot, single-pose MM-GBSA carries
   no replicate/ensemble average and **fails the decoy control** (§2.5). Both follow-ups the prior draft listed
   as pending have since run (§2.6): (a) the **multi-snapshot decoy null** (all 38 decoys re-scored
   multi-snapshot: 95th pct +6.69, max +7.10) — `denovo_401` (+12.83 ± 2.98, margin − SD +9.85) **clears it**,
   so the margin is above a decoy null recomputed at the same tier, not merely de-noised — **but that null
   controls the docking/MM-GBSA scoring step only, not the generative step or the best-of-N selection (F16):
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
   **release-frame-specific (= design-frame-specific)**, not universal (F16). What remains is
   **single-trajectory GB-implicit MD, not FEP**, so **selectivity FEP is the one remaining quantitative gate**;
   the receptor-frame dependence is best resolved by ensemble scoring over the druggable release sub-ensemble.

**Selectivity methodology:** docking margins are **triage priors, not affinities**; a quantitative
selectivity claim needs endpoint free energy. The state-matched NR4A1/NR4A2 metadynamics runs are
**complete**, so the matrix (§2.4) is genuinely state-matched (not opened-target-vs-static-off-target), and
the quantitative tier is now **MM-GBSA-run** rather than planned — but single-snapshot MM-GBSA has **no
entropy and no ensemble average**, so its magnitudes are inflated and only the **verdict/direction** is
trusted; **selectivity FEP** (the defensible affinity tier) is **not yet run**, and even FEP on a
cryptic/induced-fit pocket is sampling-limited. Crucially, the **single-snapshot MM-GBSA "confirmed_selective"
verdict that originally nominated `denovo_15` failed a decoy control** (§2.5): it labels 39 % of non-NR4A
marketed drugs "NR4A3-selective," so a raw two-tier (docking + single-snapshot MM-GBSA) survival is **not**
selectivity evidence, and the earlier "MM-GBSA-confirmed selective" headline (and `denovo_15` as the lead) is
**retracted**. What survives are two differently-derived footholds: **`denovo_111`**, the single candidate above
the **decoy-calibrated null** (+15.7 vs the +13.1 95th-percentile bar; §2.5), and **`denovo_401`**, the single
candidate whose margin **survives multi-snapshot de-noising** (+12.83 ± 2.98, margin − SD = +9.85; §2.6) and is
therefore the lead justified to advance to FEP. Both remain **screening-grade, single-trajectory GB-implicit
(non-FEP), unsynthesized, no-wet-lab** candidates — not validated, and `denovo_401` is not yet re-tested against a
multi-snapshot decoy null. With no wet lab, the strongest honest claim is **"computationally designed for, and —
for `denovo_401` — predicted to retain the intended selectivity profile under ensemble de-noising,"** not
"selective." Matrix cells are gated by degradation *direction* and bounded by the AML
anti-target (§3); and binding selectivity is still necessary-not-sufficient for *degradation* selectivity
(caveat 5).

## 6. Falsification (pre-registered)
Every gate has a fixed pass/fail set *before* the production numbers
([`../modalities/nr4a3-druggability-prereg.md`](../modalities/nr4a3-druggability-prereg.md)). Two
gate outcomes deviate from the literal pre-registration and are **disclosed, not silently swapped**, in
that file's deviation log: (i) the **Gate 0** metric (max → orthosteric/ligand-site, D\*=0.53 — a *real*
drug-bound bar, not a laxer one); and (ii) **Gate 1**, which asked for a free-energy *minimum or shoulder*
at an opened Rg "not just biased excursions" — F(Rg) is instead monotonic, so Gate 1 is reported as met
only in the weaker *basin-breathing* sense (no separate opened basin). The metastability question that
deferral left open is now **answered by the completed unbiased release run** (§2.2): the breathing-open
geometry is metastable (3/3 replicas) and druggable in ~24 % of unbiased frames, i.e. an induced-fit cavity
rather than bias-induced strain — so **Gate 3 is cautiously passed** (as conformational selection), not
deferred. We explicitly do **not** claim "Gates 0–3 all pass" as *unqualified* passes — Gate 1 holds only
in the weaker basin-breathing sense and Gate 3 as an induced-fit (not always-open) cavity. The route is
abandoned (weight shifting to ASO/immuno backups in the roadmap) if the opened conformations are not
druggable, not energetically accessible (the release run would have collapsed them as bias-induced strain —
it did **not**), or no selective drug-like binder can be designed.

**Gate 4 (a selective, drug-like ligand can engage the opened pocket) — scored explicitly, cautiously met
*in silico*.** The pre-registered Gate 4 asked for drug-like matter that docks with a reasonable score,
contacts a meaningful subset of the selectivity handles, and shows a predicted selectivity margin vs
NR4A1/NR4A2. The de-novo campaign (§2.5) meets the *letter* of this — `denovo_15` docks into the druggable
release pocket, contacts 4 of the 5 engageable handles, and is NR4A3-favoured at both docking and MM-GBSA
with no reversal — but with two pre-registration-honest qualifications: (a) the energy tiers are screening
priors (docking) and a single-snapshot endpoint model (MM-GBSA), **not** the affinity-grade FEP, which is
unrun; and (b) "drug-like" is satisfied on QED but **not** on stability/synthesizability — `denovo_15`'s
generative-model liabilities (caveat 6, §5) mean Gate 4 is cleared by a *chemotype/pose hypothesis*, not a
developable warhead. So Gate 4 is recorded as **cautiously met in silico, pending a stable re-designed
analogue and FEP** — not as an unqualified pass. (Disclosed in the prereg deviation log.) **Update
(2026-06-30): Gate 4 is re-scored against a decoy null — partially met, one above-null hit.** A decoy
control (§2.5) showed the *raw* single-snapshot MM-GBSA verdict is non-specific (39 % of non-NR4A drugs score
"selective"), so a raw margin does not count. Re-scored against the **decoy-calibrated bar (95th pct =
+13.1 kcal/mol)**, **`denovo_111` is the one candidate that clears the null** (+15.7; clean; favoured in both
receptor states) — a *calibrated* above-null NR4A3-selective hit, while the rest fall in the null. Gate 4 is
therefore **provisionally supported by a single foothold**, pending (i) the lead-optimization campaign around
`denovo_111` producing a robust above-null series and (ii) decoy-calibrated multi-snapshot MM-GBSA / FEP
confirmation. Not an unqualified pass, but **not failed** — the small-molecule-warhead leg has a live lead.
**Update (2026-06-30, multi-snapshot tier): the de-noising step (ii) is now run and upgrades the foothold to
a single FEP-justified lead.** Multi-snapshot endpoint MM-GBSA (§2.6) shows the single-snapshot harvest is
noise-dominated (`denovo_393` +18.34 → −2.95 ± 3.65, collapses) but isolates **`denovo_401` (+12.83 ± 2.98,
margin − SD = +9.85)** as the one candidate whose selectivity survives ensemble de-noising — clearing the
pre-committed FEP-worthiness bar. Gate 4 is thus **supported by a de-noised lead justified to enter FEP**,
still pending the matching multi-snapshot decoy re-calibration and the FEP itself. Live, advancing, not an
unqualified pass. **Update (2026-06-30, matching controls now run): the multi-snapshot decoy re-calibration
named just above has been run, and `denovo_401` clears it.** Re-scoring all 38 decoys multi-snapshot tightens
the null to a 95th percentile of **+6.69** (max decoy +7.10); `denovo_401`'s +12.83 ± 2.98 (margin − SD
+9.85) sits **above the entire decoy null**, and a fully state-matched re-dock (NR4A3 metad-opened) keeps it
NR4A3-selective (+7.44 ± 4.18), confirming the direction is not a receptor-frame artifact. So Gate 4 is now
**met in silico by a single de-noised lead (`denovo_401`) whose margin exceeds a same-tier decoy null in its
design (release) frame** — the strongest the in-silico evidence supports — with two honest limits (F16): that
null controls the *scoring* step only, not the *generative* step (`denovo_401` was fit to the release frame;
the decoys were not) or the best-of-~200/~10 selection, and the signal does not survive into the
non-design (metad) frame — so this is a **de-noised foothold, not a demonstrated specificity result**.
**Selectivity FEP** remains the one quantitative gate (a stable, synthesizable status for `denovo_401`, which
unlike `denovo_15` carries no structural alerts, is already in hand). Still not an unqualified pass (no FEP, no
wet lab, generation-matched null not run): the small-molecule-warhead leg has a de-noised foothold, upgraded
from an above-noise one but short of a specificity-controlled lead.

## References (DOIs/journals verified via Crossref + Europe PMC 2026-06-26, `verify-refs.yml` §7; collate to journal format before submission)
- Wang Z, et al. *Structure and function of Nurr1 identifies a class of ligand-independent nuclear
  receptors.* **Nature** 423:555–560 (2003). PubMed 12774125. (PDB 1OVL.)
- de Vera IMS, et al. *Defining a Canonical Ligand-Binding Pocket in the Orphan Nuclear Receptor Nurr1.*
  **Structure** 27(1):66–77.e5 (2019). PubMed 30416039; doi 10.1016/j.str.2018.10.002.
- Lanig H, et al. *In Silico Adoption of an Orphan Nuclear Receptor NR4A1.* **PLoS ONE** 10:e0135246
  (2015). PMC4535767; doi 10.1371/journal.pone.0135246. (MD-revealed cryptic druggable pocket in Nur77/NR4A1.)
- Haller F, et al. *Enhancer hijacking activates oncogenic transcription factor NR4A3 in acinic cell
  carcinomas of the salivary glands.* **Nat Commun** 10:368 (2019). PMC6341107; doi 10.1038/s41467-018-08069-x.
  (AciCC = NR4A3-over-expression-driven; the second NR4A3-selective indication.)
- Lee DY, et al. *Oncogenic Orphan Nuclear Receptor NR4A3 Interacts and Cooperates with MYB in Acinic Cell
  Carcinoma.* **Cancers** 12(9):2433 (2020). PMC7565926; doi 10.3390/cancers12092433. (NR4A3–MYB
  cooperation in AciCC.)
- Khan J, Ullah A, Goodbee M, Lee KT, Yasinzai AQK, Lewis JS Jr, Mesa H. *Acinic Cell Carcinoma in the 21st
  Century: A Population-Based Study from the SEER Database and Review of Recent Molecular Genetic Advances.*
  **Cancers** 15(13):3373 (2023). PMC10340722; doi 10.3390/cancers15133373. (AciCC epidemiology — third most
  common salivary-gland malignancy; the §3 relative-incidence anchor.)
- Stacchiotti S, Baldi GG, Morosi C, Gronchi A, Maestro R. *Extraskeletal Myxoid Chondrosarcoma: State of the
  Art and Current Research on Biology and Clinical Management.* **Cancers** 12(9):2703 (2020). PMC7563993;
  doi 10.3390/cancers12092703. (EMC ultra-rare, <1 per 1,000,000/year; the §3 EMC-incidence anchor.)
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
- Filion C, Motoi T, Olshen AB, Laé M, Emnett RJ, Gutmann DH, Perry A, Ladanyi M, Labelle Y. *The
  EWSR1/NR4A3 fusion protein of extraskeletal myxoid chondrosarcoma activates the PPARG nuclear receptor
  gene.* **J Pathol** 217(1):83–93 (2009). PMC4429309. (EWSR1/NR4A3 response element in the PPARG promoter,
  confirmed by band-shift + transactivation — a validated *direct* fusion target; EMC-specific evidence the
  fusion is a functional transcriptional driver. DOI to confirm via `verify-refs.yml`.) Further
  EMC-over-expressed fusion targets (e.g. NDRG2): *Tumor Biology* 33:1599–1607 (2012),
  doi 10.1007/s13277-012-0415-2 — **[first author/details to verify]**.
- EMC clinical context + the fusion-addiction/ASO/surrogate evidence: see the EMC-program roadmap and its
  source memos.

*Medical-integrity note: the NR4A-degrader citations above had their journal/year/DOI verified against
Crossref + Europe PMC on 2026-06-26 (`verify-refs.yml` §7), which also corrected the NR4A3–MYB AciCC
paper's first author (Lee, not Haller). The two §3 incidence anchors (Khan 2023, Stacchiotti 2020) were
added 2026-06-30 from MDPI/PMC (DOIs + PMCIDs above) to replace the prior unsourced relative-incidence
claim and **should be run through `verify-refs.yml` with the rest before submission**. Remaining to add
from the primary record before submission: a few volume/page numbers (e.g. Munoz-Tello 2020). No claim
should outrun its cited evidence.*
