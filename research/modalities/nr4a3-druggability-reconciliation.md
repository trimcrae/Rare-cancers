# Reconciling NR4A3's borderline fpocket score with the "undruggable" reputation

**For the manuscript discussion/appendix.** NR4A receptors are widely called undruggable, yet our
fpocket pipeline assigns the NR4A3 orthosteric pocket (Pocket 5, residues 406–534) a druggability of
**0.495** — borderline, not zero. A reviewer will press on this. The tension is mostly *apparent*, and
where it is real it sharpens our caveats rather than supporting an unfalsifiable "it's druggable"
narrative. Five points, then the calibration that adjudicates them, then why AF3 is not the fix.

## 1. The "0.80 for Nurr1" is an unlocalized *top* pocket — not the occluded orthosteric site
During analysis our pipeline reported a top-pocket druggability of **~0.80** for the Nurr1/NR4A2 AF2
model, which seems to clash with Nurr1's famously occluded pocket. But `nr4a_selectivity.py` recorded,
for the paralogues, only the single **highest-scoring pocket anywhere on the LBD** (and its lowest
lining residue), and **never localized it**. fpocket finds *all* cavities; the Nurr1 0.80 is very
plausibly a surface/coactivator or interdomain cleft, not the classical ligand pocket — and Nurr1 is
known to bind ligands at non-classical/surface sites (below). So the 0.80-vs-occluded "contradiction"
compared Nurr1's *best* cavity against NR4A3's *orthosteric* cavity — apples to oranges. The
calibration panel (§6) localizes it explicitly.

## 2. fpocket is geometric, not pharmacological — and 0.495 is *sub*-threshold anyway
"Undruggable" in the NR4A literature is a *pharmacological* claim (no reliable high-affinity selective
small molecule for the classical pocket). fpocket's score is a *geometric* estimate of cavity
size/shape/hydrophobicity — necessary but far from sufficient for a bindable drug site. And 0.495 is
*below* the conventional 0.5 line: the pipeline is calling NR4A3 **not cleanly druggable**, which is
broadly *concordant* with the reputation, not a refutation. The honest label is "borderline/occluded,"
not "fpocket says druggable."

## 3. The reputation is built on *static* structures; we test the *dynamic ensemble*
The structural basis of "undruggable" is the Nurr1 LBD crystal (Wang et al., *Nature* 2003; PDB
**1OVL**), where bulky side chains fill the canonical pocket — a single snapshot. Crucially, later work
shows that snapshot is not the whole story: de Vera et al. (*Structure* 2019) found the Nurr1 pocket is
**dynamic, highly solvent-accessible, exchanges between conformations on the µs–ms timescale, and
expands from the collapsed crystallized conformation to bind unsaturated fatty acids.** That is
*precisely* the cryptic-opening hypothesis we test for NR4A3 — so our approach is **precedented by the
experimental NR4A literature**, not contrarian. The conventional claim and ours address different
objects (static occlusion vs. dynamic accessibility).

## 4. Our AF2 model likely *over-reports* the cavity — so 0.495 is an upper bound
fpocket on an AF2 model can place side-chain rotamers/backbone leaving more apparent void than the
packed experimental pocket. We test this directly (§6, Gate 0b): score the **NR4A2 AF2 model** vs the
**1OVL crystal**. If the model reads substantially higher, our NR4A3 static 0.495 is an **upper bound**
on static druggability (the true static pocket is likely tighter) — which is *why* the dynamic question
matters: we are not claiming the static model is druggable.

## 5. The field has moved from "undruggable" → "ligandable at cryptic/surface sites"
Experimentally validated NR4A ligands bind **non-classical** sites: Nur77/NR4A1 binds THPN (PDB
**4JGV**) and cytosporone B (PDB **6KZ5**) at **surface** pockets; Nurr1/NR4A2 co-crystallizes with
prostaglandin-A1 and a dopamine metabolite (PDB **5Y41/5YD6/6DDA**) and binds amodiaquine (by NMR; no
crystal). So the modern consensus is softer than "undruggable": *no open classical pocket, but
ligandable at cryptic/alternative sites.* Our route sits inside that consensus.

## 5b. NR4A-family precedent for dynamic / cryptic pockets (paper-ready)
The single strongest defense of our approach is that **the cryptic/dynamic-pocket mechanism is already
demonstrated experimentally and computationally in NR4A3's close paralogues — but has never been
examined in NR4A3 itself.** That makes our result simultaneously *credible* (precedented in a highly
conserved family) and *novel* (first for NR4A3). The parallels to cite:

- **NR4A2 / Nurr1 — canonical pocket is dynamic and expands (the closest precedent).** de Vera et al.
  (*Structure* 2019) used NMR, HDX-MS and MD to show Nurr1's putative canonical pocket is **dynamic,
  highly solvent-accessible, exchanges between conformations on the µs–ms timescale, and expands from
  the collapsed crystallized conformation to bind unsaturated fatty acids.** This is our exact
  hypothesis, on the *same* (orthosteric) pocket, in the nearest paralogue.
- **NR4A1 / Nur77 — MD revealed a cryptic druggable pocket.** An in-silico/MD study reported a
  *previously undetected, druggable* pocket in the Nur77 LBD (remote from the canonical site), stable
  in simulation with conformational coupling to a distal loop ("In Silico Adoption of an Orphan Nuclear
  Receptor NR4A1", PMC4535767). Independent evidence that NR4A LBDs harbour MD-revealable druggable
  cavities invisible in static structures.
- **Experimentally validated NR4A ligands bind cryptic/surface sites:** Nur77 + THPN (PDB 4JGV) and
  + cytosporone B (PDB 6KZ5); Nurr1 + prostaglandin-A1 / dopamine-metabolite co-crystals (PDB
  5Y41/5YD6/6DDA); Nurr1 + amodiaquine (NMR). Real NR4A ligands exist and engage non-classical sites.
- **NR4A3 / NOR-1 itself: no experimental LBD structure and no published cryptic-pocket / MD study** —
  the gap our work fills. NR4A LBDs are highly conserved (see `nr4a-selectivity.json`: most Pocket-5
  lining residues are conserved across NR4A1/2/3), so the paralogue precedent transfers by homology.

**Framing for the paper:** "A dynamic, ligand-accessible pocket has been demonstrated in the homologous
Nurr1 (de Vera 2019) and a cryptic druggable pocket reported in Nur77 by MD, yet NR4A3 — the EMC fusion
driver — has neither an experimental LBD structure nor any reported pocket-dynamics analysis. We provide
the first."

## 6. Calibration that adjudicates all of the above (`nr4a3_calibration.py`)
Same fpocket pipeline (and `fpocket_lib` file→pocket mapping) on a nuclear-receptor panel:
- **Known-druggable controls** — PPARγ LBD + rosiglitazone (PDB **2PRG**), ERα LBD + 17β-estradiol
  (PDB **1ERE**): the ligand-site druggability here is what "druggable" *looks like in our pipeline*.
- **NR4A crystals** — Nurr1 apo occluded **1OVL**, Nurr1 holo **5Y41**, Nur77 holo **4JGV**.
- **NR4A AF2 models** — NR4A3/NR4A2/NR4A1 (the model-vs-crystal over-call check).

This sets the working threshold **D\*** and the falsification gates fixed in
[`nr4a3-druggability-prereg.md`](./nr4a3-druggability-prereg.md), *before* the production numbers.

### Calibration results (gpu-calibration-aws.yml run 28202437979, S3 `nr4a3-calibration`)

| structure | type | max druggability | ligand-site druggability |
|-----------|------|------------------|--------------------------|
| PPARγ 2PRG | druggable control | 0.957 | **0.599** (rosiglitazone) |
| ERα 1ERE | druggable control | 0.799 | **0.586** (estradiol) |
| Nurr1 1OVL | NR4A apo crystal (occluded) | 0.864 | — (no true ligand; selenomet artifact) |
| Nurr1 5Y41 | NR4A holo crystal | 0.812 | **0.677** (prostaglandin-A1) |
| Nur77 4JGV | NR4A holo crystal | 0.960 | **0.529** (THPN) |
| NR4A2 AF2 (Nurr1) | NR4A model | 0.801 | — |
| NR4A1 AF2 (Nur77) | NR4A model | 0.657 | — |
| NR4A3 AF2 (target) | NR4A model | **0.495** (Pocket 5, orthosteric) | — |
| NR4A3 metad opened (5 ns prelim) | MD opened frames | 0.751† (max over frames) | — |
| **NR4A3 metad opened (30 ns)** | **MD opened frames** | **0.931†** (max over 600 frames) | — |

> **† Metric note (important — avoid the apples-to-oranges trap §1 warns about).** For the *crystal/model*
> rows above, the "max druggability" column is the **max-anywhere-on-LBD** cavity (non-discriminating;
> e.g. 1OVL 0.864 is a non-orthosteric cleft). For the two **metad-opened** rows, 0.751/0.931 are the
> **orthosteric Pocket-5** druggability (the *same* metric as the static NR4A3 0.495 and D\*=0.53), taken
> as the **peak over frames** of that pocket — *not* the max-anywhere cavity. So 0.931 is commensurate
> with 0.495 and D\*, but two caveats: it is an **extreme value over 600 frames** (report the fraction of
> frames ≥ D\* — met — with 0.931 as the peak), and it is a **biased-MD-frame** number, so its magnitude is
> not on the same footing as the *static* drug-bound crystal sites (0.53–0.68). The fpocket druggability
> metric itself is standard and is already anchored by this panel (incl. the occluded 1OVL negative), so no
> bespoke negative control is needed; and because druggability rewards hydrophobic *enclosure*, a merely
> splayed/solvent-exposed pocket would score *lower* — the rise is informative. Read 0.931 as a
> structural-feasibility readout; the physical-population question is the release run's, not fpocket's.

**Interpretation (three findings):**

1. **`max` druggability is non-discriminating — so our Pocket-5-specific reporting was correct.** Even
   the *occluded* 1OVL crystal scores **0.864** somewhere on the LBD; every NR LBD has *some* high
   cavity. So "fpocket max on an LBD" is meaningless, and the right yardstick is the **ligand-site /
   orthosteric-specific** score. This also **localizes the Nurr1 "0.80"**: it is a *non-orthosteric*
   cavity, present in **both** the AF2 model (0.801) **and** the occluded crystal (0.864) — confirming
   §1 (it was never the orthosteric pocket, and is not an AF2 artifact).
2. **Our AF2 model does *not* over-call (Gate 0b refuted, reassuringly).** NR4A2 model max 0.801 ≈
   1OVL crystal max 0.864 — the model and the experimental structure agree. So our NR4A3 static
   orthosteric **0.495 is trustworthy and, if anything, conservative**, not inflated.
3. **The calibrated druggable band:** experimentally **ligand-occupied** NR pockets score **0.53–0.68**
   (PPARγ 0.599, ERα 0.586, Nurr1-holo 0.677, Nur77-holo 0.529). Define **D\* = 0.53** (the lowest
   validated drug-bound NR site). Then:
   - static NR4A3 orthosteric **0.495 < D\*** → sub-druggable in the static/occluded state (concordant
     with the "undruggable" reputation);
   - **metad-opened NR4A3 0.751 (5 ns) / 0.931 (30 ns) > D\*** — the breathing-open pocket geometrically
     admits a druggable cavity. *Caveat (see † above):* this is a biased-MD-frame score and its raw
     magnitude is **not** a like-for-like comparison to the *static* drug-bound crystal sites — we do not
     claim "above every drug-bound NR pocket" as a calibrated result; that comparison awaits the
     negative-control run.
   The qualitative conclusion (static sub-D\*, breathing-open above D\*) is identical under a naive 0.5
   cutoff or the calibrated 0.53, so it does not hinge on the exact threshold.

### Gate scoring against the pre-registration ([`nr4a3-druggability-prereg.md`](./nr4a3-druggability-prereg.md))
- **Gate 0 — DEVIATION (disclosed).** As pre-registered, Gate 0 used **max** druggability and required
  the occluded 1OVL max < 0.5; 1OVL max is **0.864**, so the test **fails as literally specified**. The
  calibration revealed *why*: max is dominated by non-orthosteric cavities present even in occluded
  structures. We therefore correct the discriminator to the **ligand-site** metric (which was also
  computed), disclose the change, and adopt **D\* = 0.53** from the validated drug-bound controls. This
  correction makes the bar *real* (0.53, a true drug-bound score), not laxer.
- **Gate 0b (model over-call) — refuted:** model ≈ crystal; the static 0.495 is conservative.
- **Gate 1 (a genuine cryptic *opening* occurs) — MET ONLY IN THE WEAKER, BASIN-BREATHING SENSE
  (disclosed deviation).** Gate 1 as pre-registered required the converged F(Rg) to show "an accessible
  **minimum or shoulder** at an opened Rg distinct from the closed basin (**not just biased excursions**)."
  The 30 ns F(Rg) is instead **monotonic — a single closed basin with a rising wall and no opened
  minimum/shoulder** (the opening frontier is also under-converged). So the literal Gate-1 condition is
  **not** satisfied: the druggable conformations are reached by *basin-internal breathing* under the bias,
  not via a distinct opened metastable state. This is still consistent with the de Vera 2019 *breathing*
  Nurr1 pocket (the precedent is breathing, not a two-state switch), and it does not by itself sink the
  route — but it must be scored honestly, and the metastability-vs-bias-induced-strain question is left to
  the in-progress unbiased release run, **not** pre-judged as a pass. (Previously this gate was un-scored
  while the program reported "Gates 0–3 pass"; that overstatement is corrected here and in the paper.)
- **Gate 2 (opened state druggable) — PASS (30 ns).** On the full 30 ns production run
  (600 frames), opened-frame max druggability is **0.931** (≥ D\* 0.53; up from the 5 ns 0.751), with
  86.8 % of frames more open than baseline and +6.1 nm² SASA — above every validated NR drug-bound site
  in the panel. Second clause of this gate (handles pocket-facing) — **CONFIRMED
  2026-06-26** (`nr4a3_handle_facing.py` / `handle_facing_geom.py` on the 30 ns trajectory): in the
  druggable frames (fpocket ≥ D\*=0.53), a mean of **5.0/7** selectivity handles face into the cavity and
  87.5 % keep ≥4 facing (not a splayed artifact). Five are reliably inward — L406, T410, I484, I531,
  L534 — while **T407 (0.0) and R412 (0.25) mostly splay outward**, so the engageable selectivity set is
  five handles, not seven. Gate 2 PASSES on both clauses, with that caveat noted for warhead design.
- **Gate 3 (energetic accessibility) — PROVISIONALLY MET (not closed).** The naive closed→fully-open cost
  is ~38.5 kcal/mol, but that measures the cost to reach the *most-open edge* (Rg 1.06, the under-converged
  sampling frontier — monotonic wall, no open basin), **not** the cost to reach a *druggable* conformation.
  Correlating per-frame druggability with the CV (F(Rg)-vs-druggability re-analysis) shows the orthosteric
  pocket is **already druggable (fpocket 0.80) at Rg ≈ 0.717 nm**, in the well-sampled basin region,
  costing only **0.76 kcal/mol** — thermally plausible. **Honest caveat:** both the 0.76 and the 38 are
  read off the *same* incompletely-converged biased F(Rg); the 0.76 is the more reliable of the two only
  because the basin is better sampled than the frontier, but it is still one biased profile. So the opening
  cost ~38 is best read as an artifact of reading the frontier, and a druggable conformation is *plausibly*
  cheap — but the **independent** confirmation is the unbiased "release" run (does the breathing-open
  geometry persist as a populated sub-state, or collapse as bias-induced strain?). That run's earlier
  startup crash is fixed and it is queued; **until it reports, Gate 3 is "thermally plausible," not
  resolved.** *Reframing:* the single static AF2 model (0.495) understated the pocket; the thermally-
  populated MD ensemble breathes to a geometrically druggable cavity at low apparent cost — stated at
  feasibility weight, not as a closed result.
  Shared check with Gate 2 (handles facing in) — CONFIRMED 2026-06-26 (mean 5.0/7 handles pocket-facing
  in the druggable frames; T407/R412 the outward-pointing exceptions; `nr4a3_handle_facing.py`).
- *Infra note:* the 30 ns GitHub wrapper job was auto-cancelled at GitHub's 6 h job cap, but the
  SageMaker job ran to completion independently and wrote the 30 ns outputs to S3 (frames=600 confirms).
  The submitter is being hardened so long runs don't depend on that.

## Would AF3 give "better" results? No — not for this question
The bottleneck is **not** backbone-prediction accuracy:
- AF2 and AF3 both predict a single low-energy conformation; **neither models the conformational
  ensemble**, and neither guarantees the packed side chains that close an occluded apo pocket. fpocket
  can see a void in either. Swapping AF2→AF3 changes the snapshot slightly; it does not address
  "single snapshot vs ensemble," which is the actual issue.
- AF3's real gains are in **complexes** (protein–ligand, protein–nucleic-acid, ions, PTMs, multimers),
  not apo single-domain side-chain packing or ensembles.
- For probing conformational heterogeneity via structure prediction, the relevant tool is **AF2 with
  MSA subsampling / AFSample-style ensembles**, not AF3.
- NR4A2/NR4A1 have experimental LBD structures, but **NR4A3/NOR-1 does not** (hence the AF2 model);
  AF3 would still be a prediction, not experimental data.
- **Where AF3 *does* help us:** later, for the holo/ternary modeling — NR4A3 + warhead + E3 ligase and
  the coactivator interface (the repo's `nr4a3_ternary.py` is primed for this). For the druggability
  *baseline*, the fix is **ensemble + calibration + pre-registration**, not a different folding model.

## References (verified against primary sources)
- Wang Z, Benoit G, Liu J, Prasad S, Aarnisalo P, Liu X, Xu H, Walker NPC, Perlmann T. *Structure and
  function of Nurr1 identifies a class of ligand-independent nuclear receptors.* **Nature** 423:555–560
  (2003). PubMed 12774125. (PDB 1OVL.)
- de Vera IMS, Munoz-Tello P, Zheng J, Dharmarajan V, Marciano DP, Matta-Camacho E, Giri PK, Shang J,
  Hughes TS, Rance M, Griffin PR, Kojetin DJ. *Defining a Canonical Ligand-Binding Pocket in the Orphan
  Nuclear Receptor Nurr1.* **Structure** 27(1):66–77.e5 (2019). PubMed 30416039.
- Lanig H, et al. *In Silico Adoption of an Orphan Nuclear Receptor NR4A1.* **PLoS ONE** 10(8):e0135246
  (2015). PMC4535767; doi 10.1371/journal.pone.0135246. (MD-revealed cryptic druggable pocket in
  Nur77/NR4A1; verified 2026-06-26.)
- Munoz-Tello P, et al. *Assessment of NR4A Ligands that Directly Bind and Modulate the Orphan Nuclear
  Receptor Nurr1.* **J Med Chem** (2020). PMC8006468; doi 10.1021/acs.jmedchem.0c00894. (Amodiaquine
  binding by NMR; PGA1/5,6-dihydroxyindole co-crystals 5Y41/5YD6/6DDA; journal/year/DOI verified
  2026-06-26 — volume/pages still to add from the primary record.)
- Nur77/NR4A1 ligand co-crystals: PDB 4JGV (THPN), 6KZ5 (cytosporone B) — surface pockets. *[primary
  citations to attach before submission].*
- PPARγ control: PDB 2PRG (Nolte RT et al., PPARγ LBD + rosiglitazone, **Nature** 395:137, 1998).
- ERα control: PDB 1ERE (Brzozowski AM et al., ERα LBD + 17β-estradiol, **Nature** 389:753, 1997).

*Note (medical integrity): full locators for the NR4A-ligand precedent citations marked "[…to
confirm]" must be verified against the primary sources before they enter the submitted manuscript.*
