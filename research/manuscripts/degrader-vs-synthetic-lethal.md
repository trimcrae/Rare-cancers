# Degrader vs. synthetic-lethal for EWSR1::NR4A3 EMC — a feasibility comparison

**Scope.** A deeper head-to-head than `novel-modalities.md` §3.1 (degradation) and §3.4–3.5
(synthetic-lethal / transcriptional), written to decide **which route to invest in first**.
This is a *decision memo*, not a results paper: no EMC wet-lab data exists, so everything below
is feasibility reasoning from public structure (`research/modalities/nr4a3-structure-assessment.json`)
and the cited literature. Claims are tagged **[established]**, **[precedent]**, or
**[hypothesis]**. Nothing here proposes a specific unproven compound as if it worked.

---

## 0. The shared starting point — two handles on one molecule

From the project's AlphaFold2 (AFDB) + fpocket assessment, the fusion is two very different
halves:

- **EWSR1 SYGQ-rich prion-like IDR (res 1–264)** — intrinsically disordered (mean pLDDT 38.8,
  98% of residues < 50). A *functional* handle.
- **NR4A3 DNA-binding domain (261–337) + hinge + ordered ligand-binding domain (373–626,
  mean pLDDT 85)** — well-folded, and carrying the **single best pocket in the whole protein**
  (fpocket Pocket 5, druggability **0.495**, lining residues 406–534, entirely within the LBD).
  A *structural* handle. The fusion **retains the entire ordered LBD**. [established — repo]

So the two routes are **not competitors at the same node**: the degrader attacks the *NR4A3-LBD
end*, synthetic-lethality attacks the dependency created by the *EWSR1-prion end*. That reframing
drives the recommendation in §3.

---

## 1. Route D — Degrader (target the NR4A3-LBD end)

**Why it's attractive.**
- **Nuclear receptors are now a *proven* degradable class.** **Vepdegestrant (ARV-471), an
  estrogen-receptor PROTAC, became the first FDA-approved PROTAC in 2025** (VEPPANU; phase-3
  VERITAC-2). The first-ever approved degrader targets a nuclear receptor — the same superfamily
  as NR4A3. [precedent]
- **A ligandable handle exists in principle.** NR4A LBDs have a **collapsed orthosteric pocket**
  filled with bulky hydrophobic side chains (why they're "orphan"), consistent with our
  borderline 0.495 score — *yet* real small molecules bind the LBD: cytosporone B, celastrol,
  CDIM (bis-indole) compounds, and antimalarials (amodiaquine, chloroquine; confirmed by NMR
  footprinting on the Nurr1 LBD). A degrader needs only a *binder*, not a functional-pocket
  occupant. [established]
- Degradation removes the protein rather than blocking a site, so it sidesteps the "no druggable
  functional pocket" verdict that kills classical inhibition (`novel-modalities.md` §2).

**Practical limitations (honest).**
1. **No usable warhead today.** Known NR4A binders are low-affinity (µM), non-selective, and
   characterized mostly for **Nurr1/Nur77, not NR4A3/NOR-1**. A real degrader needs a med-chem
   campaign to a selective NR4A3-LBD binder — a multi-year effort.
2. **Selectivity vs. wild-type NR4A3.** A LBD-binding degrader hits WT NR4A3 too (the LBD is
   shared). Probably tolerable (NR4A3 is not a broad essential and the fusion is the pathogenic
   species), but unproven. [hypothesis]
3. **E3 availability** (CRBN/VHL) in EMC is unverified.
4. **The make-or-break question is upstream of any molecule:** *is EMC addicted to the fusion?*
   The dTAG acute-degradation test (`novel-modalities.md` §3.1) must come first — if degrading
   the fusion doesn't kill EMC cells, the entire route is moot.

**Cheap computational next steps (no wet lab).**
- Map the published NR4A-ligand contact residues onto our fpocket Pocket-5 lining (406–534) to
  score warhead tractability and confirm the contacts are retained in the fusion.
- Check E3-ligase (CRBN/VHL) expression in EMC / sarcoma from public expression data.

---

## 2. Route S — Synthetic-lethal (target the EWSR1-prion end)

**Why it's attractive.**
- The EWSR1 prion-like domain in the fusion is the **same domain that, in EWS-FLI1, retargets
  BAF/SWI-SNF chromatin-remodeling complexes to tumour-specific enhancers** via tyrosine-dependent
  phase transitions (Boulay et al., *Cell* 2017). This is a **generic FET-fusion property**, so
  EWSR1::NR4A3 plausibly creates the same **chromatin-remodeling dependency**. [hypothesis, strong
  mechanistic basis]
- **The sharpest druggable node is ncBAF / BRD9.** Synovial sarcoma and malignant rhabdoid tumour
  are selectively ncBAF/BRD9-dependent, and **BRD9 degraders** (clinical-stage, e.g. CFT8634,
  FHD-609) — the *degrader*, not the parent bromodomain binder — selectively kill them. If EMC
  shares BAF-retargeting, **an existing BRD9 degrader is an off-the-shelf test article** — no new
  chemistry required. [established for SS/MRT; transfer to EMC is hypothesis]
- Backstop targets already drugged in fusion-sarcomas: BET, CDK7/9, p300/CBP (the EWSR1-IDR
  transactivation machinery; `novel-modalities.md` §3.5).

**Practical limitations (honest).**
1. **No EMC models to screen.** EMC is essentially absent from DepMap; the only models are
   **brand-new patient-derived lines** (e.g. NCC-EMC1-C1, 2025; USZ-EMC). A genome-wide CRISPR
   screen must be *run* in these scarce lines, not mined. **This is the binding limitation.**
2. **The BAF/BRD9 dependency is transferred, not demonstrated.** ncBAF dependence is best
   established in SMARCB1-altered / SS18-SSX contexts, **not** FET–nuclear-receptor fusions.
3. **Generic transcriptional targets (BET/CDK9) are pan-essential/toxic** — the therapeutic
   window, not target validity, is the problem.

**Cheap computational next steps (no wet lab).**
- **DepMap pan-sarcoma transfer prior:** is BRD9 / BRD4 / CDK9 / EP300 / SMARCA4 *selectively*
  essential across sarcoma lineages (especially fusion-driven) versus other cancers? A positive
  prior would justify spending a scarce EMC-model slot on the BRD9 test.
- EMC tumour expression of ncBAF subunits (BRD9, GLTSCR1) as a dependency prior.

---

## 2b. RESULT — DepMap transfer prior (computed this session)

`depmap_sarcoma_dependency.py` was run against **DepMap 24Q4** (2105 models, 176 sarcoma;
`depmap-sarcoma-dependency.json` + `.png`). The result is a **negative for the cheap BRD9 bet**:

- **ncBAF is not a sarcoma dependency.** BRD9 mean gene effect in sarcoma is **+0.11**
  (non-essential), BICRA/BICRAL likewise; selectivity ≈ 0. The primary hypothesis is **not
  supported** at the pan-sarcoma level.
- **Not supported even in the closest FET-fusion analog.** In **Ewing sarcoma (n=27)** — where
  the EWSR1-prion→BAF mechanism is *proven* — BRD9 is **+0.13, 0% dependent**. The one place the
  transfer logic should hold, it doesn't.
- **BET/CDK targets give no selectivity window.** BRD4 (−0.95), CDK7 (−1.85), CDK9 (−1.46) are
  strongly essential but *equally* outside sarcoma — pan-essential, not a therapeutic margin.
- **Pipeline mechanics validated** by correct recovery of the pan-essential controls
  (CDK7/BRD4/CDK9, ~100% dependent everywhere). Two *selective*-dependency self-checks were weak:
  BRD9-in-synovial is an inherently modest DepMap signal (n=5, −0.13), and **SMARCB1-in-rhabdoid
  was mis-specified** (rhabdoid tumours have *lost* SMARCB1, so non-dependence is correct biology,
  not a pipeline failure). So distrust the controls, not the headline — which the working
  pan-essential recovery supports.

**Interpretation.** The cheap transfer prior does **not** support BRD9/ncBAF (or selective
BET/CDK) as an EMC vulnerability. The synthetic-lethal route therefore has **no shortcut**: to
pursue it honestly requires a *de novo* genome-wide CRISPR screen in the scarce patient-derived
EMC lines — the expensive path, gated by model availability. This re-weights the decision in §3
**toward the degrader route**, whose retained-LBD handle and class precedent now look comparatively
stronger. (Caveat: "all sarcoma" is coarse and EMC is unrepresented; a negative transfer lowers,
but does not eliminate, the prior — only a real EMC screen settles it.)

## 3. Convergence and recommendation

**They meet at degraders.** Route D ends in an NR4A3 PROTAC; Route S's best node (BRD9) is
*already* attacked by clinical-stage degraders. The cheapest **decisive** first experiment sits at
the intersection:

> **Test an existing clinical-stage BRD9 degrader (± BET / CDK9 comparators) in the new
> patient-derived EMC lines.** It needs no new chemistry, directly tests the shared-prion-domain
> BAF hypothesis, and — if positive — hands back an *already-drugged* target.

The **direct NR4A3 PROTAC** is the higher-ceiling, longer-horizon bet: it degrades the actual
driver and rides the strongest possible class precedent (first approved PROTAC = a nuclear-receptor
degrader), but is gated by a multi-year warhead campaign.

**The real rate-limiter for *both* routes is EMC model availability, not ideas.** Every decisive
experiment — the dTAG fusion-addiction test (Route D), the CRISPR screen and the BRD9 test
(Route S) — needs the scarce patient-derived lines. Securing/using those models is the enabling
step neither route escapes.

**Verdict (updated 2026-06-21 after the §2b DepMap result).**
- The DepMap transfer prior **came back negative**, so the "test an existing BRD9 degrader first"
  shortcut is **no longer justified by transfer logic** — BRD9/ncBAF isn't a sarcoma dependency,
  not even in Ewing. The synthetic-lethal route now requires the expensive de-novo CRISPR screen
  in EMC models; do **not** spend a scarce wet-lab slot on a transfer-justified BRD9 test.
- **The degrader route (NR4A3 LBD) is now the better-supported bet.** Next *computational* steps
  (cheap, no wet lab): (i) map published NR4A-ligand contact residues onto fpocket Pocket-5
  (406–534) to score warhead tractability and confirm the contacts are retained in the fusion;
  (ii) check CRBN/VHL expression in EMC/sarcoma. The make-or-break wet-lab step for *either* route
  remains the **dTAG fusion-addiction test** in EMC lines (`novel-modalities.md` §3.1).
- Model scarcity is still the shared rate-limiter; nothing here escapes needing the patient-derived
  EMC lines for its decisive experiment.

---

## References (verified this session)

- Boulay G, et al. *Cancer-Specific Retargeting of BAF Complexes by a Prion-like Domain.* Cell
  2017. (EWSR1 prion-like domain retargets BAF.)
  https://www.cell.com/cell/pdf/S0092-8674(17)30872-3.pdf
- Brien GL, et al. *Targeted degradation of BRD9 reverses oncogenic gene expression in synovial
  sarcoma.* eLife 2018. (BRD9 degrader, not binder, kills ncBAF-dependent sarcoma.)
- Munoz-Tello P, Kojetin DJ, et al. *Assessment of NR4A Ligands that Directly Bind and Modulate the
  Orphan Nuclear Receptor Nurr1.* 2020. https://pmc.ncbi.nlm.nih.gov/articles/PMC8006468/
- *Natural products and synthetic analogs as selective NR4A modulators.* 2024.
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11267491/
- Arvinas/Pfizer. *FDA approval of VEPPANU (vepdegestrant), first approved PROTAC*, 2025;
  VERITAC-2 phase 3. https://ir.arvinas.com/ ; *J Med Chem* 2025 (NDA/era commentary)
  https://pubs.acs.org/doi/10.1021/acs.jmedchem.5c01818
- *Establishment and characterization of NCC-EMC1-C1, a novel patient-derived EMC cell line.*
  Human Cell 2025. https://link.springer.com/article/10.1007/s13577-025-01250-7

*Fact-check note:* the BAF-dependency and NR4A3-warhead points are **hypotheses transferred** from
related fusions/receptors, not demonstrated in EMC — flagged as such above. Before any of these is
quoted as established for EMC, it should pass the project's `verify-refs` check and be confirmed in
an EMC model.
