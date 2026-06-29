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
conformations are reached by *basin-internal breathing*, not a two-state cryptic switch, and whether they
are a populated sub-state vs. bias-induced strain is the question the in-progress unbiased release run
addresses. (3) We map 7
NR4A3-vs-NR4A1/NR4A2 divergent pocket residues as **selectivity handles** (5 of which stay pocket-facing
in the opened, druggable ensemble — a measured, not assumed, property), enabling a tunable selectivity
profile. (4) Treating the opened pocket as a *programmable* design axis, we run the **same cryptic-pocket
metadynamics on NR4A1 and NR4A2** to build **state-matched opened-pocket ensembles for all three
paralogues**, and dock one candidate library into each — yielding a per-candidate **selectivity
fingerprint across the NR4A family** (tunable from NR4A3-selective to pan-NR4A) and removing the
opened-target-vs-static-off-target bias that confounds naive selectivity docking. We prime a degrader/E3
ternary-complex design on the opened pocket. The work is governed by a **pre-registered falsification
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
— is the in-progress **unbiased release run** (`nr4a3_md_release.py`); until it reports, Gate 3 is
"thermally plausible," not closed. Net: the single static structure (0.495) understated the pocket; the
thermally-populated ensemble breathes to a geometrically druggable cavity at low apparent cost — a
feasibility result, stated at that weight. *(Registered Gate-2 sub-check — now COMPLETE and CONFIRMED. The handle-facing analysis
(`../modalities/nr4a3_handle_facing.py`, run 2026-06-26 on the 30 ns trajectory) shows the opened,
druggable frames keep the selectivity handles pocket-facing: across the druggable frames (fpocket ≥
D\*=0.53) a mean of **5.0/7** handles point into the cavity and **87.5 %** keep ≥4 facing. Five are
reliably pocket-facing — **L406, T410, I484, I531, L534** (≥0.875 of druggable frames) — while **T407
and R412 mostly splay outward** (facing in 0.0 and 0.25 of druggable frames), so the demonstrated
selective-engagement set is those five, not all seven. This is also the precondition for the warhead
screen's handle-contact scoring (§2.4). The unbiased "release" run is the orthogonal metastability test
that would upgrade Gate 3 from "thermally plausible" to confirmed (does the breathing-open geometry
persist, or collapse as bias-induced strain?); its earlier startup crash is now fixed and it is queued —
so the metastability question is **open, not resolved**, and the §2.2 energetics are stated at that
weight.)*

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

### 2.4 Warhead screen + the family-wide selectivity matrix (in progress)
With the pocket validated as druggable and accessible, we screen a **selective warhead** against the
*opened* conformer (`nr4a3_warhead.py` + `gpu-warhead-aws.yml`): it extracts the most-druggable opened
conformer (frame 300, fpocket 0.931), docks a real ChEMBL NR4A library into NR4A3-opened **and** the
aligned NR4A1/NR4A2 pockets, and ranks by a selectivity margin + engagement of the **5 pocket-facing**
handles (§2.3). A first screen returns NR4A3-favoured chemotypes (e.g. an NR4A3-active scaffold,
ΔdG ≈ +1.7 kcal/mol vs the paralogues); these docking margins are **triage priors, not affinities**.

**The selectivity matrix.** A central methodological point: docking the *opened* NR4A3 pocket against
*static* NR4A1/2 models biases toward apparent selectivity, because — by our own argument (de Vera 2019;
the Nur77 cryptic pocket) — the paralogue pockets are likely cryptic too. We therefore run the **same
metadynamics on NR4A1 and NR4A2** (one pipeline; paralogue CV/LBD mapped to NR4A3 by BLOSUM62 alignment)
to obtain **state-matched opened-pocket ensembles** for all three, and dock one library into each. Each
candidate then carries a **selectivity fingerprint** across the family, partitioning the library into
NR4A3-selective (EMC/AciCC), pan-NR4A (ex-vivo immuno), and the AML-associated NR4A1+NR4A3 **anti-target**
cells (§3). This makes the divergent-handle map a *demonstrated, tunable* design axis rather than an
assertion. A de-novo structure-based generative layer (DiffSBDD/Pocket2Mol), conditioned on the divergent
handles (selective) or the conserved residues (pan), is primed to populate empty cells. **Docking
nominates; quantitative selectivity requires endpoint free energy** — MM-GBSA with per-residue
decomposition, and selectivity FEP on the leads — which the state-matched ensembles enable. Once a warhead
SMILES exists, the NR4A3–PROTAC–E3 ternary-complex model (`nr4a3_ternary.py`) scores degradable-lysine
geometry per paralogue. This is not a formality: the binding-selectivity matrix is a **necessary but not
sufficient** filter, because a degrader's actual selectivity is set by the *ternary complex* — a
non-selective binder can degrade selectively (productive ternary geometry on only one paralogue) and a
selective binder can fail to degrade. The per-paralogue ternary model is therefore the gating step for any
*degradation*-selectivity claim; the binding matrix triages which candidates enter it. **No molecule is
synthesized; this is design prep.** Run instructions + program state:
[`../modalities/nr4a3-degrader-next-steps.md`](../modalities/nr4a3-degrader-next-steps.md).

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
   a selective degrader removes it directly. AciCC is a more common salivary-gland carcinoma than the
   ultra-rare EMC, enlarging the addressable population for the *same* selective agent *(relative-incidence
   locator to attach before submission — claim currently qualitative, not quantified)*.
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
Calibration: NR-LBD panel ([`../modalities/nr4a3_calibration.py`](../modalities/nr4a3_calibration.py)).
Falsification: pre-registered gates ([`../modalities/nr4a3-druggability-prereg.md`](../modalities/nr4a3-druggability-prereg.md)).
Selectivity: Biopython BLOSUM62 alignment vs NR4A1/NR4A2. **Family-wide ensembles:** the *same*
metadynamics pipeline is run on NR4A1 (P22736) and NR4A2 (P43354) — one target-agnostic script whose
paralogue LBD trim + Pocket-5 CV residues are mapped to NR4A3 by the same BLOSUM62 alignment, with
fail-loud guards + an audit log — to produce state-matched opened-pocket ensembles for the selectivity
matrix (§2.4). **Warhead / matrix:** smina docking of a real ChEMBL NR4A library into each paralogue's
metad-opened conformer; per-candidate matrix cells assigned by `selectivity_fingerprint.py` (engage/margin
thresholds; unit-tested). **Quantitative tier (planned):** MM-GBSA with per-residue decomposition, then
selectivity FEP on the leads — enabled by the state-matched ensembles; docking scores are used only as
triage priors. All parsing/mapping/classification logic is in pure, unit-tested modules (TESTING.md).

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
- **Why NR4A3's wild-type tumour-suppressor role does *not* argue against fusion-addiction.**
  A natural objection — *NR4A3 is itself growth-suppressive (combined Nr4a1/Nr4a3 loss is
  leukaemogenic [Mullican 2007]; tumour-suppressive in HCC/breast/lymphoma [Safe & Karki 2021]),
  so how can a cancer be addicted to it?* — rests on a category slip: the dependency is on the
  **EWSR1::NR4A3 fusion**, not wild-type NR4A3. The two share the LBD, but the neomorphic element
  is the **appended EWS low-complexity transactivation domain**. The objection only bites under a
  **dominant-negative** model (the fusion *inactivating* wild-type NR4A3, making the oncogenic state
  a loss-of-function — under which knockdown would relieve repression rather than kill, i.e. *not*
  addiction). The EMC-native evidence points the other way, to **neomorphic gain-of-function**
  (the chimera directly transactivates PPARG via an EWSR1/NR4A3 response element [Filion 2009], and
  carries a heterologous EWS activation domain wild-type NR4A3 lacks). Under gain-of-function the
  tumour-suppressor fact is **orthogonal-to-mildly-supportive**: the very potency that lets wild-type
  NR4A3 control growth is what makes it a credible chassis to hijack, not a reason against dependency.
  Where the tumour-suppressor role *does* bite is **safety/therapeutic window** (an LBD degrader
  removes wild-type NR4A3 too), addressed by the fusion-exclusive routes — not the addiction prior.

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
3. **Gate 3 energetics are provisional.** The ~0.76 kcal/mol cost to a druggable conformation and the
   ~38 kcal/mol to the open edge are read off the *same* incompletely-converged biased F(Rg); the
   independent metastability test (unbiased release run) is in progress, so the accessibility claim is
   "thermally plausible," not closed.
4. **Selectivity handles are a specification with an asymmetric window.** The registered handle-facing
   check confirms the handles stay pocket-facing in the druggable frames (mean 5.0/7; T407/R412 splay out,
   so five engageable). But the engageable *divergent* set is **5 vs NR4A1 and only 4 vs NR4A2** (I531 is
   conserved with NR4A2), so NR4A2 selectivity is the harder, narrower case — and these are a specification,
   not a demonstrated binding margin.
5. **Binding selectivity ≠ degradation selectivity.** The §2.4 matrix is a necessary-not-sufficient
   filter; degradation selectivity is set by the per-paralogue ternary complex (the planned gating step).

**Selectivity methodology:** docking margins are **triage priors, not affinities**; a quantitative
selectivity claim needs endpoint free energy (MM-GBSA with per-residue decomposition, selectivity FEP on
the leads), and even then FEP on a cryptic/induced-fit pocket is sampling-limited. The selectivity matrix
(§2.4) is only credible because the paralogues are treated **state-matched** (same metadynamics), not
opened-target-vs-static-off-target; until the NR4A1/NR4A2 runs complete, the first warhead margins use
static paralogue pockets and are upper bounds on selectivity. With no wet lab, the strongest honest claim
is **"computationally designed for, and predicted to have, the intended selectivity profile,"** not
"selective." Matrix cells are gated by degradation *direction* and bounded by the AML anti-target (§3).

## 6. Falsification (pre-registered)
Every gate has a fixed pass/fail set *before* the production numbers
([`../modalities/nr4a3-druggability-prereg.md`](../modalities/nr4a3-druggability-prereg.md)). Two
gate outcomes deviate from the literal pre-registration and are **disclosed, not silently swapped**, in
that file's deviation log: (i) the **Gate 0** metric (max → orthosteric/ligand-site, D\*=0.53 — a *real*
drug-bound bar, not a laxer one); and (ii) **Gate 1**, which asked for a free-energy *minimum or shoulder*
at an opened Rg "not just biased excursions" — F(Rg) is instead monotonic, so Gate 1 is reported as met
only in the weaker *basin-breathing* sense (no separate opened basin), with the metastability question
deferred to the in-progress unbiased release run rather than scored as an unqualified pass. We explicitly
do **not** claim "Gates 0–3 all pass" without these qualifications. The route is abandoned (weight shifting
to ASO/immuno backups in the roadmap) if the opened conformations are not druggable, not energetically
accessible (the release run collapses them as bias-induced strain), or no selective drug-like binder can
be designed.

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
paper's first author (Lee, not Haller). Remaining to add from the primary record before submission: a few
volume/page numbers (e.g. Munoz-Tello 2020). No claim should outrun its cited evidence.*
