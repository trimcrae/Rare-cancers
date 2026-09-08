---
id: DOC-DEGRADER-VS-SYNTHETIC-LETHAL
title: Degrader vs. synthetic-lethal for EWSR1::NR4A3 EMC — an internal route-comparison memo
level: L3
kind: memo
status: live
canonical_for: ["the internal degrader-versus-synthetic-lethal route comparison for EWSR1::NR4A3 EMC"]
purpose: >
  Compare the two routes this program could invest in first, degrading the NR4A3-LBD end of the
  fusion or attacking a dependency created by the EWSR1-prion end, and record what the retained
  computational evidence does and does not support about that choice.
scope: >
  Internal decision memo, not a submission text. Public AlphaFold2/fpocket predictions on wild-type
  monomers, one public CRISPR dependency panel that contains no EMC line, and cited literature.
  No wet-lab work, no experiment in an EMC model, no patient data, and no efficacy, potency,
  selectivity, safety, therapeutic-window or clinical-readiness claim for either route.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: 2026-09-08
---
# Degrader vs. synthetic-lethal for EWSR1::NR4A3 EMC — an internal route-comparison memo

> **SOURCE MEMO (internal) — feeds the active manuscript** [`emc-treatment-roadmap.md`](../program/emc-treatment-roadmap.md)
> via the strategy capstone [`emc-treatment-strategy.md`](../program/emc-treatment-strategy.md).
> Not separately submitted, and not a preprint candidate; the reasons are in §4, which is a
> finding of this review rather than a deferral. Its record `PUB-SYNLETH` carries
> `target_venue: internal_note`, and this document is written to that.
> Folder map: [`README.md`](../README.md).

**Scope.** A deeper head-to-head than [`novel-modalities.md`](../modality-census/novel-modalities.md)
§3.1 (degradation) and §3.4–3.5 (synthetic-lethal / transcriptional), written to decide
**which route to invest in first**.
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
  (fpocket Pocket 5, druggability **0.495**, 10 lining residues spanning 406–534, all 10 within the LBD).
  A *structural* handle. ⚠ Both readings are AlphaFold2 predictions on the wild-type monomers
  (UniProt Q92570 and Q01844); `nr4a3-structure-assessment.json` contains no model of the fusion
  protein, so that the fusion retains the entire ordered LBD is asserted from the breakpoint
  architecture and is not measured by the cited artifact. [prediction — repo, wild-type monomers]

So the two routes are **not competitors at the same node**: the degrader attacks the *NR4A3-LBD
end*, synthetic-lethality attacks the dependency created by the *EWSR1-prion end*. That reframing
drives the recommendation in §3.

---

## 1. Route D — Degrader (target the NR4A3-LBD end)

**Why it's attractive.**
- **Nuclear receptors are now a *proven* degradable class.** **Vepdegestrant (ARV-471), an
  estrogen-receptor PROTAC, became the first FDA-approved PROTAC** (VEPPANU; phase-3
  VERITAC-2). That first FDA-approved PROTAC targets a nuclear receptor — the same superfamily
  as NR4A3. [precedent]
  ⚠ This repository's two records disagree on the year: this memo says 2025, which is the year of
  the phase-3 VERITAC-2 publication, while [`nr4a3-degrader-paper.md`](../degrader/nr4a3-degrader-paper.md)
  records the FDA approval as 2026-05-01 in its reference list; not adjudicated here.
  (A line number printed here previously, `:156`, no longer located that reference and has been
  replaced by the file and the quoted date.)
- **A ligandable handle exists in principle.** NR4A LBDs have a **collapsed orthosteric pocket**
  filled with bulky hydrophobic side chains (why they're "orphan"), consistent with our
  borderline 0.495 score — *yet* real small molecules bind the LBD: cytosporone B, celastrol,
  CDIM (bis-indole) compounds, and antimalarials (amodiaquine, chloroquine; confirmed by NMR
  footprinting on the Nurr1 LBD). A degrader needs only a *binder*, not a functional-pocket
  occupant. [established]
- Degradation removes the protein rather than blocking a site, so it sidesteps the "no druggable
  functional pocket" verdict that kills classical inhibition (`novel-modalities.md` §2).
- **Degradation is mechanistically ideal *here specifically*.** NOR-1/NR4A3 is constitutively
  active and its transcriptional output scales with **expression level** [Zaienne 2022, **PMID
  35704774**, NOR-1 druggability — ⛔ *superseded attribution, retained: "Munck 2022", which names no
  paper;* [`nr4a3-druggability-reconciliation.md` §5b](../../modalities/nr4a3-druggability-reconciliation.md)] — so lowering protein dose directly lowers oncogenic output, which is exactly what
  a degrader does (an inhibitor would have to block a function NOR-1 may not even gate on a pocket).
  And the family is degradable: an **NR4A1 PROTAC** degrades NR4A1 in cells — though notably it
  does **not** cross-degrade NR4A3, so NR4A3 needs its own warhead. [established]

**Practical limitations (honest).**
1. **Warhead is early but real (revised up).** NR4A3-*specific* starting points now exist —
   fragment-derived **inverse NOR-1 agonists** (low-µM) that alter NOR-1-regulated gene expression
   in cells [Zaienne 2022, **PMID 35704774**], plus fatty-acid-mimetic NR4A ligands [J Med Chem 2023] — not just the
   non-selective Nurr1/Nur77 compounds. Still low-affinity and pre-degrader, so a med-chem campaign
   to a selective, potent NR4A3 warhead remains multi-year — but it starts from real chemical
   matter, not zero. This is where **AI de-novo binder design** (RFdiffusion/AF-based) could
   compress the timeline.
2. **Selectivity vs. wild-type NR4A3.** A LBD-binding degrader hits WT NR4A3 too (the LBD is
   shared). Probably tolerable (NR4A3 is not a broad essential and the fusion is the pathogenic
   species), but unproven. [hypothesis]
3. **E3 availability** (CRBN/VHL) in EMC is unverified — and unlike Route S's transfer prior in §2b,
   the cheap step that would test it has not been run: the sibling sarcoma-expression surrogate
   `depmap-target-expression.json` contains no CRBN and no VHL row. This is an unrun check, not a
   negative result, and the asymmetry matters when the two routes are weighed below.
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

## 2b. RESULT — DepMap transfer prior (2026-06-21; artifact re-check 2026-09-08)

`depmap_sarcoma_dependency.py` was run against **DepMap 24Q4** (2105 models; 176 sarcoma models catalogued in
the release, but every gene record carries `n_sarcoma = 91`, so 91 is the screened denominator of
every number below —
`depmap_sarcoma_dependency.py:79`;
`depmap-sarcoma-dependency.json` + `.png`). The result is a **negative for the cheap BRD9 bet**:

- **ncBAF is not a sarcoma dependency.** BRD9 mean gene effect in sarcoma is **+0.105**
  (non-essential; 2.2% of the 91 screened lines dependent), and BICRA (+0.093) and BICRAL (−0.142)
  likewise; BRD9 selectivity is −0.016, i.e. none. The primary hypothesis is **not
  supported** at the pan-sarcoma level.
- **Not supported even in the closest FET-fusion analog.** In **Ewing sarcoma (n=27)** — where
  the EWSR1-prion→BAF mechanism is *proven* — BRD9 is **+0.134, 0% dependent**. The one place the
  transfer logic should hold, it doesn't.
- **BET/CDK targets give no selectivity window.** BRD4 (−0.954), CDK7 (−1.847), CDK9 (−1.464) are
  strongly essential in sarcoma but *equally* so outside it (rest means −0.972, −1.762, −1.447;
  selectivities −0.018, +0.085, +0.017) — pan-essential, not a therapeutic margin.
- ⚠ **The same run read Route D's own target, and this memo prints it nowhere.** In
  `depmap-sarcoma-dependency.json`, NR4A3 is +0.021 in sarcoma with 0% of the 91 screened lines
  dependent, and its selectivity is +0.002 (`context_genes`). No line in the panel supplies a
  CRISPR observation for EMC: the single EMC-labelled line has no CRISPR gene-effect data at all, and the further curated record
  that it does not harbour the fusion is suggestive and consistent, not definitive. That caveat
  qualifies this NR4A3 null exactly as it qualifies the BRD9 null above, so the two routes must be
  read at equal strength: neither is a measurement in EMC.
- **Pipeline mechanics validated** by correct recovery of the pan-essential controls
  (CDK7/BRD4/CDK9, ~100% dependent everywhere). Two *selective*-dependency self-checks were weak:
  BRD9-in-synovial is an inherently modest DepMap signal (n=5, −0.130), and **SMARCB1-in-rhabdoid
  was mis-specified** (n=13, −0.025, 7.7% dependent: rhabdoid tumours have *lost* SMARCB1, so
  non-dependence is correct biology, not a pipeline failure). But the pan-essential recovery
  validates essentiality detection, and the headline is a claim about selectivity. The one control that could have validated
  selectivity detection — BRD9 in synovial sarcoma, the context where ncBAF dependence *is*
  established — did not recover it (n=5, −0.130, 20% dependent, i.e. 1 line of 5). So the headline
  negative rests on a limb whose only positive control came back weak, and it should be read as a
  weak prior against BRD9 rather than as a settled negative.

**Interpretation.** The cheap transfer prior does **not** support BRD9/ncBAF (or selective
BET/CDK) as an EMC vulnerability. The synthetic-lethal route therefore has **no shortcut**: to
pursue it honestly requires a *de novo* genome-wide CRISPR screen in the scarce patient-derived
EMC lines — the expensive path, gated by model availability. This re-weights the decision in §3
**toward the degrader route**, whose retained-LBD handle and class precedent now look comparatively
stronger. (Caveat: "all sarcoma" is coarse and EMC is unrepresented; a negative transfer lowers,
but does not eliminate, the prior — only a real EMC screen settles it.)

---

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
- The DepMap transfer prior **came back negative** — a weak prior against BRD9 rather than a
  settled negative, because §2b's only selectivity control came back weak. The "test an existing
  BRD9 degrader first" shortcut is therefore **no longer justified by transfer logic** — BRD9/ncBAF
  isn't a sarcoma dependency, not even in Ewing. The synthetic-lethal route now requires the
  expensive de-novo CRISPR screen in EMC models; do **not** spend a scarce wet-lab slot on a
  transfer-justified BRD9 test.
- **The degrader route (NR4A3 LBD) is now the comparatively better-placed bet — because the
  comparator lost support, not because the degrader gained any.** No result in §2b is evidence for
  Route D; the same run returned a null on NR4A3 itself. Next *computational* steps
  (cheap, no wet lab): (i) map published NR4A-ligand contact residues onto fpocket Pocket-5
  (406–534) to score warhead tractability and confirm the contacts are retained in the fusion;
  (ii) check CRBN/VHL expression in EMC/sarcoma. The make-or-break wet-lab step for *either* route
  remains the **dTAG fusion-addiction test** in EMC lines (`novel-modalities.md` §3.1).
- Model scarcity is still the shared rate-limiter; nothing here escapes needing the patient-derived
  EMC lines for its decisive experiment.

---

## 4. Note status and the preprint decision

This section is a finding of the 2026-09-08 review, not a deferral. The document was examined
against the artifacts it names to decide whether its content is paper-shaped, and it is not.

1. **Its purpose is internal ordering, not a reportable result.** The document exists to decide
   which route this program funds first. That question is about this program's budget and model
   access, and its answer is consumed by
   [`emc-treatment-roadmap.md`](../program/emc-treatment-roadmap.md) and
   [`emc-treatment-strategy.md`](../program/emc-treatment-strategy.md), not by an outside reader.
2. **The one original computation here is bounded, and §2b already says so.** §2b is a read of a
   public DepMap release. Its headline is a claim about *selectivity*, and the one self-check that
   could have shown selectivity detection works, BRD9 in synovial sarcoma (where ncBAF dependence
   is established), came back weak (n=5, −0.130, 20% dependent). §2b therefore reports a weak prior
   against BRD9, and a weak prior is not a finding a preprint can carry as its subject.
3. **Nothing in it is measured in EMC.** The panel supplies no CRISPR observation for any EMC line.
   The structure readings are AlphaFold2 predictions on wild-type monomers (Q92570, Q01844) and the
   cited artifact models no fusion protein. The BAF/BRD9 dependency and the NR4A3 warhead case are
   transferred from other fusions and other receptors.
4. **The comparison itself cannot be published as a comparison.** No retained evidence compares
   Route D and Route S on efficacy, potency, selectivity, safety, therapeutic window or clinical
   readiness, and this memo makes no such claim for either route. §3's verdict is a statement about
   which *prior* lost support (the comparator's, on one public panel), and it says explicitly that
   no result in §2b is evidence for the degrader. That is a defensible internal ranking and an
   indefensible external claim about two therapeutic strategies.
5. **House register is correct here.** `lint_style.py`'s target list is submission texts only and
   says in its own comment that a memo must not be added to it. The warning glyphs and emphasis in
   this file are carrying caveats to a maintainer, which is what the house style is for.

**What would reopen this.** A CRISPR or drug-response observation in a fusion-positive EMC model,
or a selectivity self-check that actually recovers a known-positive context, would give §2b a
subject of its own. At that point the negative belongs in a paper that reports it as its own
result with its own methods, and this memo goes back to being the decision record it is.

---

## References

These are as recorded at writing. The 2026-09-08 pass did no external retrieval,
so none of them was re-fetched.

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

---

## Appendix A. Quantity verification, 2026-09-08

Every quantity printed above was re-read from the artifact named beside it. No producer was re-run
and no figure was regenerated; these are reads of the committed files.

| printed here | artifact and field | value read |
|---|---|---|
| 2105 models; 176 sarcoma models; 91 screened denominator | `research/modalities/depmap-sarcoma-dependency.json` → `n_models_total`, `n_sarcoma_models`, every `n_sarcoma` | 2105, 176, 91 |
| the 91-line denominator is the script's own reading | `research/modalities/depmap_sarcoma_dependency.py:79` | "91 SCREENED sarcoma lines (of 176 sarcoma models in the release)" |
| BRD9 +0.105, selectivity −0.016, 2.2% dependent | same JSON → `genes_by_group` → ncBAF | 0.105, −0.016, 0.022 |
| BICRA +0.093, BICRAL −0.142 | same JSON → ncBAF | 0.093, −0.142 |
| BRD4 −0.954, CDK7 −1.847, CDK9 −1.464 | same JSON → BET / transcriptional | −0.954, −1.847, −1.464 |
| NR4A3 +0.021, 0% dependent, selectivity +0.002 | same JSON → `context_genes` | 0.021, 0.0, 0.002 |
| Ewing BRD9 +0.134, n=27, 0% dependent | same JSON → `BRD9_by_fusion_sarcoma_subtype.Ewing` | 0.134, 27, 0.0 |
| synovial BRD9 −0.130, n=5, 20% dependent | same JSON → `self_validation.BRD9_in_synovial` | −0.13, 5, 0.2 |
| SMARCB1-in-rhabdoid −0.025, n=13, 7.7% | same JSON → `self_validation.SMARCB1_in_rhabdoid` | −0.025, 13, 0.077 |
| EWSR1 IDR 1–264, mean pLDDT 38.8, 98% < 50 | `research/modalities/nr4a3-structure-assessment.json` → `EWSR1.regions` | 1-264, 38.8, 0.981 |
| NR4A3 DBD 261–337; LBD 373–626, mean pLDDT 85 | same JSON → `NR4A3.regions` | 261-337; 373-626, 85.0 |
| Pocket 5, druggability 0.495, 10 lining residues, 406–534, all in the LBD | same JSON → `NR4A3.fpocket.top_pocket_locale` | 0.495, 10, 406, 534, `{"ligand-binding domain": 10}` |
| Pocket 5 is the best pocket in the protein | same JSON → `NR4A3.fpocket.pockets` (33 pockets, next best 0.196) | 0.495 is the maximum |
| no CRBN and no VHL row in the sibling expression surrogate | `research/modalities/depmap-target-expression.json` | neither symbol occurs in the file |
| the EMC-labelled DepMap line is not fusion-positive on the curated record | `research/modalities/emc-atr-vulnerability.json` → `part_a_hemcss_identity.verdict` | `NOT_FUSION_POSITIVE_PER_CURATED_RECORD` |
| that line carries no CRISPR gene-effect data | `research/modalities/emc-blk-no-emc-data-route-retest.json` → blocker name, verbatim | "one DepMap line, n = 1, no CRISPR data" |

**One repair the review made to a printed pointer.** §1 previously cited
`nr4a3-degrader-paper.md:156` for the 2026-05-01 FDA-approval date. That line no longer holds the
reference (it is at line 3178 as of this pass), so the citation now names the file and quotes the
date instead of a line number that drifts.

**Not re-verified.** The literature citations in the reference list were not re-retrieved: this pass
did no external retrieval. They stand as recorded when the memo was written.
