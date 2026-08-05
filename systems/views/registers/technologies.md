---
id: DOC-VIEW-TECHNOLOGIES
title: Technology-dependency register and forecasts
level: cross-cutting
kind: generated
status: generated
generator: systems/systems_check.py
purpose: What would unblock the work, how much comes back if it lands, and when it is expected.
scope: "All technology dependencies and their forecasts. Vocabulary: systems/taxonomy/technology.md"
audience: ["maintainers", "autonomous research agents", "external reviewers"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# Technology-dependency register

> **A coming capability justifies waiting and re-running. It never licences claiming the result
> before the method can support it.**

Every forecast declares its `basis` — `evidence_based`, `extrapolated` or `speculative`. An
unlabelled forecast is indistinguishable from a measurement.

## Ordered by fan-out

| fan-out | technology | category | state | conservative | expected | optimistic | basis | impact | scanned |
|---:|---|---|---|---|---|---|---|---|---|
| 14 | **TECH-EMC-MODEL-ACCESS** | `experimental_access` | `absent` | beyond-2031 | **2029** | 2027H2 | `speculative` | `transformative` | yes |
| 11 | **TECH-FE-CRYPTIC-POCKET** | `free_energy_method` | `absent` | 2030 | **2028** | 2027H1 | `extrapolated` | `transformative` | yes |
| 10 | **TECH-EMC-EXPRESSION-DATA** | `biological_dataset` | `early_signals` | beyond-2031 | **2029** | 2027 | `speculative` | `transformative` | yes |
| 9 | **TECH-COFOLD-ASSEMBLY** | `structure_prediction` | `partially_landed` | 2028 | **2027** | 2026H2 | `evidence_based` | `transformative` | yes |
| 7 | **TECH-CHEAP-ENSEMBLE** | `conformational_ensemble` | `partially_landed` | 2028 | **2027** | 2026H2 | `evidence_based` | `large` | yes |
| 7 | **TECH-POSE-CONVERGENCE** | `structure_prediction` | `absent` | 2030 | **2028** | 2027 | `extrapolated` | `large` | yes |
| 6 | **TECH-EXPOSURE-CRITERION** | `free_energy_method` | `absent` | 2029 | **2027H2** | 2026H2 | `extrapolated` | `moderate` | yes |
| 6 | **TECH-VIRTUAL-CELL** | `foundation_model_biology` | `early_signals` | 2030 | **2028** | 2027H1 | `extrapolated` | `transformative` | yes |
| 6 | **TECH-CLOUD-WET-LAB** | `lab_automation` | `early_signals` | beyond-2031 | **2029** | 2027H2 | `extrapolated` | `transformative` | yes |
| 5 | **TECH-CHARGE-CHANGE-FEP** | `free_energy_method` | `absent` | 2028 | **2027** | 2026H2 | `extrapolated` | `moderate` | yes |
| 5 | **TECH-OBSERVED-CRL** | `structure_prediction` | `absent` | beyond-2031 | **2028** | 2027 | `speculative` | `moderate` | yes |
| 4 | **TECH-VECTOR-DELIVERY** | `lab_automation` | `absent` | beyond-2031 | **2030** | 2028 | `speculative` | `large` | yes |
| 4 | **TECH-GLUE-DESIGN** | `generative_design` | `early_signals` | 2029 | **2027H2** | 2026H2 | `extrapolated` | `large` | yes |
| 4 | **TECH-TERNARY-ALCHEMY** | `free_energy_method` | `absent` | 2030 | **2028** | 2027H1 | `extrapolated` | `large` | yes |
| 4 | **TECH-E1-POWERED** | `free_energy_method` | `absent` | beyond-2031 | **2029** | 2027H2 | `speculative` | `moderate` | yes |
| 4 | **TECH-E3-RECRUITER-STRUCTURE** | `structure_prediction` | `absent` | 2030 | **2028** | 2027 | `speculative` | `moderate` | yes |
| 4 | **TECH-NONCOVALENT-PARALOGUE-CONTROL** | `published_measurement` | `absent` | beyond-2031 | **2028** | 2027 | `speculative` | `large` | yes |
| 4 | **TECH-JUNCTION-PMHC** | `foundation_model_biology` | `absent` | 2032 | **2029** | 2027H2 | `extrapolated` | `large` | yes |
| 3 | **TECH-OLIGO-DELIVERY** | `lab_automation` | `early_signals` | beyond-2031 | **2029** | 2027H2 | `extrapolated` | `transformative` | yes |
| 3 | **TECH-ANTITARGET-PROTOCOL** | `structure_prediction` | `absent` | 2028 | **2027** | 2026H2 | `extrapolated` | `moderate` | yes |
| 3 | **TECH-ATOM-MAPPER** | `free_energy_method` | `absent` | 2028 | **2027** | 2026H2 | `extrapolated` | `marginal` | yes |
| 3 | **TECH-AUTONOMOUS-AGENT** | `autonomous_research_agent` | `partially_landed` | 2029 | **2027** | 2026H2 | `evidence_based` | `large` | yes |
| 3 | **TECH-COMPUTE-COST** | `compute_economics` | `early_signals` | 2029 | **2027H2** | 2026H2 | `evidence_based` | `moderate` | n/a — watched another way |
| 1 | **TECH-RXR-HETERODIMER-REPORT** | `published_measurement` | `absent` | never | **beyond-2031** | 2029 | `speculative` | `marginal` | yes |
| 1 | **TECH-ASO-SPECIFICITY-MODEL** | `foundation_model_biology` | `absent` | 2029 | **2028** | 2027 | `extrapolated` | `moderate` | yes |

**1 dependency(ies) cannot be seen by a literature search and are watched
another way** — each says how, under `not_scannable_because` in its Detail entry: `TECH-COMPUTE-COST`. ⛔ This is a recorded decision, not a gap; the
alternative was a fabricated query that reports nothing forever while being credited
as coverage.

## Detail

### TECH-EMC-MODEL-ACCESS — fan-out 14

**Access to a patient-derived EMC model through a collaborator, or through a solo-affordable cloud or robotic wet-lab service with EMC-runnable assay scope**

*Category:* `experimental_access` · *state:* `absent` · *confidence in that state:* `high`

**Why it matters.** The cell-line repositories exclude unaffiliated individuals by published policy rather than by price, so no budget reaches this and every confirm-gated row is gated on a person. It is the highest fan-out non-method dependency in the portfolio, and it is about ACCESS rather than capability.

**What the state assessment rests on:**
- Repository policies exclude individuals; no collaborator has been secured.

**Unblocks.** blockers: BLK-NO-WET-LAB, BLK-R4-BINDS, BLK-FUNCTIONAL-ACTIONABILITY · routes: RT-ATR-PANEL, RT-ASO-ASK, RT-TRABECTEDIN-PPARG, RT-SSTR2, RT-COVALENT-PROBE, RT-SYNLETH-DEP, RT-B7H3, RT-CART-SURFACE, RT-PPARG-DOWNSTREAM, RT-CARFILZOMIB · requirements: R4

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `beyond-2031` | high | Repository policy excludes unaffiliated individuals, and policy of that kind does not change on a research timescale. Without an affiliation or a collaborator this stays shut regardless of budget. |
| expected | `2029` | low | The realistic route is not a policy change but a substitution: a cloud or robotic lab reaching a scope that covers this work, which would supply execution — though not the cell line itself. |
| optimistic | `2027H2` | moderate | A single self-interested collaborator with existing access would satisfy this in a week. This is the scenario a convincing preprint is actually aimed at. |

*Basis:* `speculative` · *impact here:* `transformative` · *last reviewed:* 2026-08-05

**What would move this.** A responding collaborator, or a cloud-lab service adding both the assay scope and a material-sourcing path. ⚠ The two are not interchangeable: a cloud lab supplies robots and generic reagents, never the EMC line.

*Scanned by:* `TRG-EMC-FUNCTIONAL-MODEL`

### TECH-FE-CRYPTIC-POCKET — fan-out 11

**A binding free-energy method — alchemical or ML — with a published known-answer validation on cryptic or induced-fit pockets, reproducing a benchmark to within about 1 kcal/mol on a site absent from the apo structure**

*Category:* `free_energy_method` · *state:* `absent` · *confidence in that state:* `high`

**Why it matters.** This program's central quantitative claim is a free-energy difference between two closely related pockets, and the engine used to compute it misses a known absolute answer by more than the entire margin it is asked to resolve. Every absolute number on the binder path is therefore uninterpretable. This is the single highest fan-out dependency in the portfolio.

**What the state assessment rests on:**
- No public benchmark validates an absolute free-energy engine on a cryptic or induced-fit pocket to the accuracy this margin requires.

**Unblocks.** blockers: BLK-PARALOGUE-DDG · routes: RT-DEGRADER, RT-MONOVALENT, RT-GLUE, RT-ANDGATE, RT-RIPTAC, RT-TCIP · requirements: R7 · instruments: V4, V7, V9

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2030` | moderate | Absolute free-energy accuracy on induced-fit sites has resisted improvement for a decade; force-field and sampling gains have historically arrived at a pace that would put a validated cryptic-pocket benchmark late in the decade. |
| expected | `2028` | low | Machine-learned potentials are closing the force-field half of the error while the sampling half is being attacked separately by generative ensembles. Both improving at once is what would produce a validated benchmark, and both are currently improving. |
| optimistic | `2027H1` | low | A single well-resourced group publishing a cryptic-pocket benchmark set with an ML-potential engine would satisfy this in one paper. The ingredients exist; nobody has assembled them into a benchmark. |

*Basis:* `extrapolated` · *impact here:* `transformative` · *last reviewed:* 2026-08-05

**What would move this.** A public benchmark set of cryptic or induced-fit binding sites with reference affinities — the benchmark landing before the method would compress every band, because the method cannot be shown to work without one.

**⚠ Adoption note.** The date refers to a method validated ON THIS REGIME, not to one existing in a paper. A cryptic-pocket free-energy result published without a known-answer control does not move this forecast.

*Scanned by:* `TRG-FEP-CRYPTIC-POCKET`

### TECH-EMC-EXPRESSION-DATA — fan-out 10

**A fetchable public EMC RNA-seq or proteomics deposit beyond the single existing model, enabling a target-regulon readout and per-antigen expression confirmation on real EMC tissue**

*Category:* `biological_dataset` · *state:* `early_signals` · *confidence in that state:* `moderate`

**Why it matters.** EMC is nearly absent from public functional genomics: one line, no CRISPR data. This is the repository-wide rate-limiter and it is a DATA dependency, not a method one — it fans out across every route whose in-silico half is bounded by a sample size of one.

**What the state assessment rests on:**
- The weekly scan fired on this trigger with new hits in its most recent run; none has yet been graded as a usable deposit.

**Unblocks.** blockers: BLK-NO-EMC-DATA · routes: RT-SYNLETH-DEP, RT-PPARG-DOWNSTREAM, RT-TRABECTEDIN-PPARG, RT-B7H3, RT-SSTR2, RT-PRAME-IMMTAC, RT-CART-SURFACE, RT-FAP-RLT, RT-CARFILZOMIB

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `beyond-2031` | moderate | EMC is an ultra-rare sarcoma. Public deposition depends on a group both collecting a series and choosing to deposit it, and neither is on anyone's published roadmap. |
| expected | `2029` | low | Sarcoma consortia deposit periodically and sequencing cost continues to fall, so a series including EMC cases arriving inside five years is more likely than not — but the timing is essentially a draw from an unknown distribution. |
| optimistic | `2027` | low | A single already-collected series being deposited would satisfy this immediately. The weekly scan has produced hits on this query, none yet graded as usable. |

*Basis:* `speculative` · *impact here:* `transformative` · *last reviewed:* 2026-08-05

**What would move this.** Any deposited EMC series, or a pan-sarcoma atlas whose inclusion criteria reach this histology. A single usable deposit collapses the whole forecast.

*Scanned by:* `TRG-EMC-EXPRESSION-DATASET`, `TRG-SARCOMA-ATRI-RESPONSE-PANEL`

### TECH-COFOLD-ASSEMBLY — fan-out 9

**A sequence-only co-folder evaluated on ternary ASSEMBLY — inter-chain accuracy on post-training-horizon induced complexes — rather than on per-chain pocket accuracy**

*Category:* `structure_prediction` · *state:* `partially_landed` · *confidence in that state:* `high`

**Why it matters.** One co-folder failing is not the class failing: the same harness already recognises a correct ternary when both binding sites are supplied, so the plumbing is not what missed. What is missing is a model benchmarked on the assembly problem itself, and a benchmark discipline that reports inter-chain rather than per-chain accuracy.

**What the state assessment rests on:**
- Open tools now exist for induced-complex prediction and one reaches high inter-chain accuracy WHEN BOTH SITES ARE GIVEN.
- The arm that has NOT landed is assembly from sequence and ligand alone, which is the problem this program actually has.

**Unblocks.** blockers: BLK-TERNARY-GEOMETRY, BLK-INDUCED-COMPLEX · routes: RT-AF3-INTERFACE, RT-ANDGATE, RT-DEGRADER, RT-RIPTAC, RT-TCIP · requirements: R10 · instruments: V12

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2028` | moderate | Assembly from sequence and ligand alone is a materially harder problem than assembly with both sites given, and training data for induced complexes is scarce because few are deposited. |
| expected | `2027` | moderate | Structure-prediction models are iterating fast and induced-complex prediction is an explicit target for several. The benchmark discipline — reporting inter-chain rather than per-chain accuracy — is the part most likely to lag. |
| optimistic | `2026H2` | moderate | An existing model re-evaluated on post-horizon induced complexes with inter-chain metrics would satisfy this with no new architecture. |

*Basis:* `evidence_based` · *impact here:* `transformative` · *last reviewed:* 2026-08-05

**What would move this.** Any induced-complex benchmark reporting inter-chain accuracy on structures deposited after the model's training horizon. In-horizon results are memorisation-permitting by construction and move nothing.

**⚠ Adoption note.** One arm has landed — high inter-chain accuracy WHEN BOTH SITES ARE GIVEN. The forecast dates assembly from sequence and ligand alone, which is the problem this program actually has.

*Scanned by:* `TRG-COFOLD-TERNARY-ASSEMBLY`, `TRG-TERNARY-GEN-NO-SITES`

### TECH-CHEAP-ENSEMBLE — fan-out 7

**Generative equilibrium-ensemble models validated against known cryptic pockets — recovering benchmark sites without GPU-days of biased sampling, and calibrated on rare-open populations**

*Category:* `conformational_ensemble` · *state:* `partially_landed` · *confidence in that state:* `high`

**Why it matters.** It collapses the per-target cost of opening a cryptic pocket from GPU-days to pennies, which decides whether a cryptic-pocket druggability survey is a focused target class or proteome-scale. For this program it is an orthogonal, unbiased cross-check on a biased sampling result.

**What the state assessment rests on:**
- The detection arm landed: a sequence-only generative ensemble model detects the site and opens it to a druggable state in a minority of frames, concordant in direction with an experimental NMR ensemble.
- The CALIBRATION arm has not landed: the model is uncalibrated on rare-open populations and apo is its weakest regime, so the result is a qualitative cross-check and not a population estimate.

**Unblocks.** routes: RT-DEGRADER, RT-MONOVALENT · requirements: R1, R2, R6 · instruments: V13, V14

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2028` | moderate | Calibrating a generative ensemble on RARE-open populations is harder than detecting a site, and rare-state calibration has no established benchmark. |
| expected | `2027` | moderate | The detection arm has already landed and is in use here. Calibration is the active research frontier for exactly these models, with several groups working on it. |
| optimistic | `2026H2` | moderate | A benchmark paper evaluating existing ensemble models against known cryptic-pocket populations would satisfy this without any new model at all. |

*Basis:* `evidence_based` · *impact here:* `large` · *last reviewed:* 2026-08-05

**What would move this.** A published evaluation of generative ensemble models against known cryptic-site occupancies. The models exist; what is missing is the calibration study.

**⚠ Adoption note.** Half of this has already landed. The forecast dates the CALIBRATION arm only — the detection arm is in production use here and is what makes the remaining gap precisely stateable.

*Scanned by:* `TRG-GENERATIVE-ENSEMBLE`, `TRG-CRYPTIC-POCKET-PREDICTION`

### TECH-POSE-CONVERGENCE — fan-out 7

**A pose-prediction protocol whose site transfer places the crystallographic ligand inside its own search box in regime, and on which two scoring-independent methods converge in ORIENTATION as well as location on the same receptors**

*Category:* `structure_prediction` · *state:* `absent` · *confidence in that state:* `moderate`

**Why it matters.** Two independent site-transfer routes both place the site at zero in regime, and two disjoint scoring functions disagree in orientation at a median far above their centroid separation. So the non-convergence belongs to the system, not to one scoring function — and a single better docking program is therefore not the trigger. Every pose-conditional claim in the program depends on this.

**What the state assessment rests on:**
- Nothing is currently scanning for this — it was registered as a revival trigger with no corresponding literature query.

**Unblocks.** routes: RT-DEGRADER, RT-MONOVALENT, RT-COVALENT-PROBE · requirements: R5, R8 · instruments: V3, V22

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2030` | moderate | Two disjoint scoring functions disagreeing in orientation on the same receptors points at the receptor conformer rather than at either function, and conformer-aware pose prediction is not close to solved. |
| expected | `2028` | low | Co-folding methods that place a ligand and its receptor conformation jointly are improving quickly and sidestep the site-transfer step that is failing here entirely. |
| optimistic | `2027` | low | A joint ligand-and-conformer predictor benchmarked on apo-to-holo transfer would satisfy this, and that benchmark is a natural next paper for several existing methods. |

*Basis:* `extrapolated` · *impact here:* `large` · *last reviewed:* 2026-08-05

**What would move this.** Any pose method reporting apo-to-holo site transfer in regime rather than holo self-docking. ⚠ A better docking program alone does NOT move this — the non-convergence is the system's, not one function's.

*Scanned by:* `TRG-POSE-ORIENTATION-CONVERGENCE`

### TECH-EXPOSURE-CRITERION — fan-out 6

**A solvent-exposure or thiol-reactivity criterion that recovers the one NR4A-family covalent site with literature support as engageable on a state-matched opened model**

*Category:* `free_energy_method` · *state:* `absent` · *confidence in that state:* `moderate`

**Why it matters.** The standing exposure cutoff fails that positive control, so anything it adjudicates inherits a demonstrated false negative and only a threshold-free rank survives. A criterion that passes the control makes the whole covalent screen readable again rather than rank-only.

**What the state assessment rests on:**
- Nothing is currently scanning for this.

**Unblocks.** blockers: BLK-REACH-CATEGORICAL · routes: RT-COVALENT-PROBE, RT-MONOVALENT · requirements: R8, R15 · instruments: V17

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2029` | moderate | Covalent-site accessibility criteria are a niche methodological corner with few groups working on them and no benchmark that would force the issue. |
| expected | `2027H2` | low | Covalent drug discovery is active enough that a reactivity-aware accessibility criterion is a natural methods contribution, and chemoproteomics datasets to calibrate one exist. |
| optimistic | `2026H2` | moderate | This is small enough that it could be BUILT here rather than waited for — a reactivity-weighted criterion calibrated against the existing positive control is a bounded piece of work. |

*Basis:* `extrapolated` · *impact here:* `moderate` · *last reviewed:* 2026-08-05

**What would move this.** A chemoproteomics-calibrated ligandability criterion, or a decision to build one here. ⭐ This is a dependency where waiting may be the wrong call — see the optimistic scenario.

*Scanned by:* `TRG-COVALENT-EXPOSURE-CRITERION`

### TECH-VIRTUAL-CELL — fan-out 6

**A virtual-cell or perturbation model that predicts held-out knockdown phenotype in a cell type it was not trained on**

*Category:* `foundation_model_biology` · *state:* `early_signals` · *confidence in that state:* `moderate`

**Why it matters.** It would let the fusion-dependence question — the make-or-break premise beneath the degrader and the oligonucleotide routes alike — be asked without an EMC cell line. That is the one question this program currently delegates entirely.

**What the state assessment rests on:**
- Perturbation-prediction models exist and are improving; held-out phenotype prediction in an untrained rare cell type is not demonstrated.

**Unblocks.** blockers: BLK-NO-EMC-DATA, BLK-CLASS-INHERITANCE · routes: RT-DEGRADER, RT-ASO, RT-SYNLETH-DEP · requirements: R16

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2030` | moderate | Held-out phenotype prediction in a cell type absent from training is the hard version of the problem, and rare tumour types are exactly where training data is thinnest. |
| expected | `2028` | low | Perturbation and virtual-cell models are a major, well-funded research direction with rapid iteration. Generalisation to unseen cell types is the explicit target, not a side effect. |
| optimistic | `2027H1` | low | A foundation model demonstrating cross-cell-type knockdown prediction on a held-out benchmark would satisfy this, and that benchmark is the field's stated goal. |

*Basis:* `extrapolated` · *impact here:* `transformative` · *last reviewed:* 2026-08-05

**What would move this.** A held-out knockdown-phenotype benchmark in an untrained cell type. ⚠ Within-training-distribution accuracy moves nothing — the whole value here is that EMC is out of distribution for everything.

**⚠ Adoption note.** This is the dependency where the brief's caution against defaulting to conservative assumptions bites hardest. Foundation-model progress in adjacent domains has repeatedly outrun conservative forecasts; the expected band reflects that, and is deliberately not the safe answer.

*Scanned by:* `TRG-VIRTUAL-CELL-NO-LINE`

### TECH-CLOUD-WET-LAB — fan-out 6

**A remote robotic or cloud wet lab, rentable per experiment by an unaffiliated researcher, at a price and assay scope that covers EMC cell work**

*Category:* `lab_automation` · *state:* `early_signals` · *confidence in that state:* `moderate`

**Why it matters.** This is the only watched capability that could flip the program's FOUNDING CONSTRAINT — that no wet lab is available, so every step must be in-silico or publish-to-convince. It would make the wet-lab-gated experiments runnable by this program rather than by a hypothetical collaborator.

**What the state assessment rests on:**
- Cloud-lab services exist commercially.
- ⚠ A cloud lab unlocks robotic EXECUTION, not the reagents or the biology. The EMC cell line remains a separate dependency, so this flips the execution gate and not automatically the material gate.

**Unblocks.** blockers: BLK-NO-WET-LAB, BLK-FUNCTIONAL-ACTIONABILITY · routes: RT-ASO-ASK, RT-ATR-PANEL, RT-COVALENT-PROBE · requirements: R4

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `beyond-2031` | moderate | Existing cloud labs are enterprise-contracted and chemistry-weighted. Solo-affordable per-experiment pricing WITH cell-based assay scope is a business-model change, not a technical one, and those are slow. |
| expected | `2029` | low | Self-driving-lab research is expanding and autonomous agents create demand for per-experiment API access. Both push toward a solo-usable offering, but the material-sourcing gate remains separate. |
| optimistic | `2027H2` | low | A single provider opening cell-based assays at per-run pricing would satisfy the EXECUTION half immediately. Agent-driven demand is a plausible forcing function. |

*Basis:* `extrapolated` · *impact here:* `transformative` · *last reviewed:* 2026-08-05

**What would move this.** A cloud-lab service publishing per-experiment pricing for cell-based assays with no institutional requirement.

**⚠ Adoption note.** ⚠ This flips the EXECUTION gate, not automatically the MATERIAL gate. A cloud lab supplies robots and generic reagents, never the EMC cell line — which stays coupled to the model-access dependency. Reporting this as 'the wet-lab problem solved' would be wrong in exactly the way that matters.

*Scanned by:* `TRG-CLOUD-WET-LAB`

### TECH-CHARGE-CHANGE-FEP — fan-out 5

**A validated charge-change correction for alchemical free-energy edges — a co-alchemical-ion or finite-size treatment demonstrated to reproduce a known-answer set of charge-changing transformations**

*Category:* `free_energy_method` · *state:* `absent` · *confidence in that state:* `moderate`

**Why it matters.** Charge-changing edges block legs of the relative free-energy map and killed a high-contrast calibrator route. The correction reopens the EDGES; it does not rescue the calibrator design, which was a poor calibrator on perturbation size alone.

**What the state assessment rests on:**
- Nothing is currently scanning for this.

**Unblocks.** routes: RT-DEGRADER · requirements: R7, R11 · instruments: V5, V6

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2028` | moderate | Finite-size corrections for charge-changing alchemical edges are well studied in theory but validated implementations in production software lag the literature by years. |
| expected | `2027` | moderate | The theory is settled and the remaining work is implementation and a known-answer set. Both are within reach of the maintained free-energy packages. |
| optimistic | `2026H2` | low | A co-alchemical-ion implementation already exists in at least one package; what is missing is a published validation set, which is a bounded piece of work. |

*Basis:* `extrapolated` · *impact here:* `moderate` · *last reviewed:* 2026-08-05

**What would move this.** A validation set of charge-changing transformations with reference values, run through a production package.

**⚠ Adoption note.** ⚠ This reopens the blocked EDGES only. It does not rescue the calibrator design those edges sat inside, which was a poor calibrator on perturbation size alone — a distinction that must travel with any revival.

*Scanned by:* `TRG-CHARGE-CHANGE-FEP`

### TECH-OBSERVED-CRL — fan-out 5

**An OBSERVED rather than COMPOSED ubiquitin-ligase RING and E2-ubiquitin geometry — a deposited full-assembly structure replacing a composed model carrying tens of angstroms of positional uncertainty**

*Category:* `structure_prediction` · *state:* `absent` · *confidence in that state:* `moderate`

**Why it matters.** No degradation-geometry claim may rest on a composed rather than observed assembly, and the ligase-choice selectivity readout is not stable under restaging. Both are statements about the geometry's PROVENANCE, which only an observed assembly changes — no amount of modelling does.

**What the state assessment rests on:**
- Nothing is currently scanning for this.

**Unblocks.** blockers: BLK-TERNARY-GEOMETRY · routes: RT-UBIQ-SELECTIVE, RT-DEGRADER · requirements: R12 · instruments: V18

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `beyond-2031` | moderate | Full ligase assemblies with the transfer geometry resolved are hard structures and are deposited rarely. Whether one appears is not under anyone's control here. |
| expected | `2028` | low | Cryo-electron microscopy of large flexible assemblies continues to improve, and ligase machinery is heavily studied. A deposition inside a few years is plausible without being predictable. |
| optimistic | `2027` | low | A single deposition satisfies this. Depositions are Poisson-like events and the optimistic band simply reflects that one could land at any time. |

*Basis:* `speculative` · *impact here:* `moderate` · *last reviewed:* 2026-08-05

**What would move this.** Any deposited full-assembly ligase structure with the transfer geometry resolved rather than composed.

*Scanned by:* `TRG-OBSERVED-CRL-E2UB-GEOMETRY`

### TECH-VECTOR-DELIVERY — fan-out 4

**A gene-therapy vector that reaches a solid tumour at therapeutic coverage**

*Category:* `lab_automation` · *state:* `absent` · *confidence in that state:* `moderate`

**Why it matters.** Three genetic routes are gated on it. It is kept strictly separate from oligonucleotide delivery: they are different engineering problems with different candidate solutions, and merging them would let one arriving imply the other had.

**What the state assessment rests on:**
- No solid-tumour vector delivery platform is established at the coverage these routes assume.

**Unblocks.** blockers: BLK-VECTOR-DELIVERY · routes: RT-CRISPR-CAS13, RT-RIBOZYME, RT-SYNPROMOTER

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `beyond-2031` | high | Solid-tumour vector coverage at therapeutic levels is a longstanding unsolved problem, and the routes depending on it need near-complete coverage rather than partial transduction. |
| expected | `2030` | low | Capsid engineering and intratumoural administration are both improving, but the coverage requirement for a suicide-gene strategy is unusually demanding. |
| optimistic | `2028` | low | A locally administered vector in a well-circumscribed soft-tissue mass is a more favourable geometry than most solid tumours, so a sarcoma-specific result could arrive earlier than the general problem is solved. |

*Basis:* `speculative` · *impact here:* `large` · *last reviewed:* 2026-08-05

**What would move this.** Any solid-tumour gene-therapy result reporting transduction coverage rather than expression alone.

*Scanned by:* `TRG-VECTOR-DELIVERY-SOLID-TUMOUR`

### TECH-GLUE-DESIGN — fan-out 4

**A validated prospective molecular-glue design method or glue-interface selectivity predictor, demonstrated on a neosubstrate interface that was not in its training set**

*Category:* `generative_design` · *state:* `early_signals` · *confidence in that state:* `moderate`

**Why it matters.** A glue has no linker, so it has no covalent axis and no designed exit vector — it removes several of this program's hardest sub-problems at once. It is also the modality most likely to arrive from someone else's screen rather than from this program's design, which is why it is watched rather than built.

**What the state assessment rests on:**
- Generative interface-design methods are advancing; none is demonstrated prospectively on an out-of-training neosubstrate interface.

**Unblocks.** routes: RT-GLUE · requirements: R7, R9, R10

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2029` | moderate | Prospective glue design requires predicting an interface that does not exist until the molecule is present, which is a harder generative problem than binder design and has far less training data. |
| expected | `2027H2` | low | Generative interface design is advancing quickly and glue discovery is heavily funded. The gating requirement is a PROSPECTIVE demonstration on an out-of-training interface, which is a benchmark discipline problem as much as a capability one. |
| optimistic | `2026H2` | low | A single prospective success published from an industrial programme would satisfy this. Several are plausibly in progress and unpublished. |

*Basis:* `extrapolated` · *impact here:* `large` · *last reviewed:* 2026-08-05

**What would move this.** A prospectively designed glue validated on an interface absent from the design method's training set. Retrospective recovery of known glues moves nothing.

*Scanned by:* `TRG-GLUE-PROSPECTIVE-DESIGN`

### TECH-TERNARY-ALCHEMY — fan-out 4

**A ternary alchemical free-energy method that PASSES the known-answer cooperativity control — recovering the reference value with the correct sign, not merely with more sampling of the present protocol**

*Category:* `free_energy_method` · *state:* `absent` · *confidence in that state:* `moderate`

**Why it matters.** The present method returns the wrong sign in every replicate at many times the statistical uncertainty, and the closure analysis localises the miss to an endpoint-state error. That is a property of the model or the reference data, so more sampling of the same endpoints cannot fix it.

**What the state assessment rests on:**
- Nothing is currently scanning for this beyond the general ternary-alchemy query.

**Unblocks.** routes: RT-DEGRADER, RT-ANDGATE · requirements: R11 · instruments: V5

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2030` | moderate | The present miss is localised to an endpoint-state error, which is a model or reference-data problem. Those are slow to fix because they are not visible as convergence failures. |
| expected | `2028` | low | Ternary cooperativity is a recognised methodological target with a small number of published reference values, and the field is aware the endpoints are the hard part. |
| optimistic | `2027H1` | low | A method paper reporting correct-sign recovery on a known cooperativity would satisfy this, and the reference values already exist. |

*Basis:* `extrapolated` · *impact here:* `large` · *last reviewed:* 2026-08-05

**What would move this.** Correct-SIGN recovery of a known cooperativity by any ternary alchemical method. ⚠ More sampling of the present protocol does not qualify — the closure analysis localises the miss to the endpoints, which sampling cannot reach.

*Scanned by:* `TRG-TERNARY-ALCHEMICAL-VALIDATED`

### TECH-E1-POWERED — fan-out 4

**An interface-stability readout with power at achievable sampling, OR a different test system whose interface effect is large enough for an endpoint readout to resolve**

*Category:* `free_energy_method` · *state:* `absent` · *confidence in that state:* `moderate`

**Why it matters.** Two independent attempts returned no pass, the second on an adequately powered design — so the block is the readout's resolution against this system's effect size, not the sample size. Two failures is strong evidence, not proof of impossibility.

**What the state assessment rests on:**
- Nothing is currently scanning for this.

**Unblocks.** blockers: BLK-ENDPOINT-MD · routes: RT-DEGRADER · requirements: R11 · instruments: V11

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `beyond-2031` | moderate | Two independent attempts returned no pass, the second adequately powered. That is evidence about the readout's resolution against this effect size, and no obvious methodological development targets it. |
| expected | `2029` | low | The more likely resolution is a different TEST SYSTEM with a larger interface effect rather than a better readout — which is a sourcing question, and sourcing questions resolve unpredictably. |
| optimistic | `2027H2` | moderate | Identifying a system whose interface effect is large enough is free and could be done at any time. ⭐ The optimistic band is short because the work is a literature search, not a capability. |

*Basis:* `speculative` · *impact here:* `moderate` · *last reviewed:* 2026-08-05

**What would move this.** A published interface-stability result resolving a small effect at achievable sampling, or the identification of a suitable alternative test system. ⭐ The second is $0 and startable now.

*Scanned by:* `TRG-ENDPOINT-SELECTIVITY-READOUT`

### TECH-E3-RECRUITER-STRUCTURE — fan-out 4

**A deposited partner-free liganded structure for one of the blocked ubiquitin-ligase recruiters — a handle pocket rather than a glue interface**

*Category:* `structure_prediction` · *state:* `absent` · *confidence in that state:* `high`

**Why it matters.** Availability was the wrong constraint; structural stageability binds. One candidate recruiter has no deposited structure at all and another's ligand is largely buried once its partner is removed, so the recruiter set this program can actually stage is far smaller than the set that exists.

**What the state assessment rests on:**
- No partner-free liganded structure has been deposited for the blocked recruiters.

**Unblocks.** blockers: BLK-TERNARY-GEOMETRY · routes: RT-DEGRADER · requirements: R9, R12

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2030` | moderate | One candidate recruiter has no deposited structure at all. Structures of proteins nobody has solved appear on nobody's schedule. |
| expected | `2028` | low | Degrader chemistry is heavily invested and new recruiter structures appear regularly; the specific requirement is a PARTNER-FREE liganded form, which is less commonly deposited than the complex. |
| optimistic | `2027` | low | A single deposition satisfies this, and recruiter structural biology is active enough that one could land at any time. |

*Basis:* `speculative` · *impact here:* `moderate` · *last reviewed:* 2026-08-05

**What would move this.** Any partner-free liganded deposition for a blocked recruiter. ⚠ A structure of the recruiter in complex with its partner does not qualify — the ligand must remain engageable once the partner is removed, which is precisely what fails now.

*Scanned by:* `TRG-E3-RECRUITER-STRUCTURE`, `TRG-FEM1B-LINKER-BEARING-STRUCTURE`

### TECH-NONCOVALENT-PARALOGUE-CONTROL — fan-out 4

**A paralogue-selectivity positive control whose selectivity is reproduced by a NON-covalent readout — a different test compound or a different system, not more sampling of the current one**

*Category:* `published_measurement` · *state:* `absent` · *confidence in that state:* `moderate`

**Why it matters.** The available control's geometry readout passes for a confounded reason: its selectivity is attributable to a covalent bond at a residue the off-target paralogues lack. No sample size and no better method fixes a confound in the system — only a different control does.

**What the state assessment rests on:**
- Nothing is currently scanning for this.

**Unblocks.** blockers: BLK-PARALOGUE-CONTROL · routes: RT-DEGRADER · requirements: R7, R11

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `beyond-2031` | moderate | Paralogue-selective chemical probes with clean non-covalent selectivity are rare, and one for a closely related receptor family is rarer still. |
| expected | `2028` | low | Chemical-probe consortia continue to produce selective tool compounds across receptor families, so a usable control appearing in some family within a few years is reasonable — it need not be this receptor family. |
| optimistic | `2027` | moderate | An existing probe may already satisfy this and simply not have been searched for. ⭐ Identifying one is a literature question, not a capability. |

*Basis:* `speculative` · *impact here:* `large` · *last reviewed:* 2026-08-05

**What would move this.** A published paralogue-selective probe whose selectivity is NOT attributable to a covalent bond at a residue the off-targets lack. ⭐ Searching for one is $0 and has not been done.

*Scanned by:* `TRG-PARALOGUE-POSITIVE-CONTROL`

### TECH-JUNCTION-PMHC — fan-out 4

**A fusion-junction presentation or immunogenicity predictor validated ON FUSION JUNCTIONS, or a TCR/ImmTAC discovery platform demonstrated against a low-abundance peptide-HLA**

*Category:* `foundation_model_biology` · *state:* `absent` · *confidence in that state:* `moderate`

**Why it matters.** Three antigen-directed routes are parked on one shared finding: the EWSR1::NR4A3 junction is a WEAK peptide-HLA, and general presentation predictors are not validated on fusion junctions, so the repo's own coverage instrument is disclosed as failing rather than supporting. Until something can either predict junction presentation credibly or reach a low-abundance pHLA in practice, all three routes rest on the same unmeasured premise and re-grading any one of them alone would be arbitrary. ⚠ IT DOES NOT RETIRE BLK-ANTIGEN-COLD. That blocker is a fundamental_biological_limit -- a fact about what the junction IS -- and no method changes it. What lands here changes whether that fact remains DECISIVE for these three routes, which is why `unblocks` names the routes and not the blocker. The blocker taxonomy draws exactly this line and [B1] enforces it.

**What the state assessment rests on:**
- The repo's own HLA-coverage instrument is recorded as disclosed_failing on all three routes, not as support.
- No public benchmark validates a presentation or immunogenicity predictor specifically on fusion-junction neopeptides; the training sets are dominated by point-mutation neoantigens.

**Unblocks.** routes: RT-TCR-IMMTAC, RT-JUNCTION-NEOANTIGEN, RT-VACCINE · instruments: INS-HLA-COVERAGE

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2032` | moderate | Fusion junctions are a small, hard slice of an already data-poor problem: presentation training sets are dominated by point-mutation neoantigens, and the immunopeptidomics that would supply junction-specific ground truth is generated one tumour type at a time. On the platform side, reaching a genuinely low-abundance pHLA has been the field's stated obstacle for a decade. If neither half moves, this sits out the decade. |
| expected | `2029` | low | Two independent trends point at it: immunopeptidomics datasets are growing and are increasingly released with the mass-spec evidence rather than as predictions, and soluble-TCR platforms now have an approved product, which pulls discovery effort toward harder pHLA targets. Either half alone would be partial evidence; the expected band assumes one of the two lands convincingly and the other does not. |
| optimistic | `2027H2` | low | A single sarcoma or fusion-driven-tumour immunopeptidomics study that measured junction peptides directly would satisfy the predictor half in one paper — the technique exists and the cohort is the missing part. ⚠ This is the band most likely to be wrong in the optimistic direction, because a study on a DIFFERENT fusion would read as a hit and would not be one. |

*Basis:* `extrapolated` · *impact here:* `large` · *last reviewed:* 2026-08-05

**What would move this.** Direct mass-spec evidence that a fusion-junction peptide is presented at measurable abundance on a common allele — in ANY fusion-driven tumour, which would make the question empirical rather than predictive. Failing that, a soluble-TCR or TCR-T programme reporting activity against a pHLA at an abundance in the range this junction is expected to occupy.

**⚠ Adoption note.** ⛔ A hit on a DIFFERENT fusion is not this capability. The trigger's on_fire text is explicit: state whether the evidence is about presentation, about abundance, or only about another fusion. EMC's junction is a specific sequence on specific alleles, and a general advance in neoantigen prediction has repeatedly not transferred to it — which is why the repo's own coverage instrument is disclosed as failing rather than quietly dropped.

*Scanned by:* `TRG-JUNCTION-PHLA`

### TECH-OLIGO-DELIVERY — fan-out 3

**An oligonucleotide tumour-delivery technology reaching non-hepatic solid tumours — a conjugate, tumour-penetrating peptide or ligand-targeted lipid nanoparticle — OR a characterised EMC-enriched surface antigen to serve as its targeting arm**

*Category:* `lab_automation` · *state:* `early_signals` · *confidence in that state:* `moderate`

**Why it matters.** Delivery is the single remaining gate on the most structurally sound route in the portfolio, and it is engineering rather than biology. The honest bottleneck is not that delivery cannot be simulated — it is that no validated way to deliver an oligonucleotide to an EMC tumour exists. A single characterised EMC surface antigen or a working soft-tissue-sarcoma conjugate would change this route's standing more than any predictor could.

**What the state assessment rests on:**
- Conjugate and targeted-nanoparticle platforms are advancing generally; none is demonstrated in a non-hepatic solid tumour at the required scope.

**Unblocks.** blockers: BLK-DELIVERY · routes: RT-ASO, RT-ASO-ASK

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `beyond-2031` | high | Delivering an oligonucleotide to a non-hepatic solid tumour has defeated the field for two decades. Liver tropism is a physical property of the delivery vehicles that work. |
| expected | `2029` | low | Antibody-oligonucleotide conjugates have reached the clinic for muscle, which is the first real evidence that the liver constraint is escapable with a targeting arm. Extending that to a stromal-rich sarcoma is a further step and not a small one. |
| optimistic | `2027H2` | low | A characterised EMC-enriched surface antigen would matter more than a delivery platform: with a targeting arm, existing conjugate chemistry may suffice. That is a discovery event, not an engineering one, and could happen at any time. |

*Basis:* `extrapolated` · *impact here:* `transformative` · *last reviewed:* 2026-08-05

**What would move this.** A conjugate demonstrating tumour delivery in ANY solid tumour outside the liver, or a characterised EMC-enriched surface antigen. The second is the higher-value observation and the cheaper one to notice.

*Scanned by:* `TRG-OLIGO-DELIVERY-TECH`, `TRG-OLIGO-DELIVERY-PREDICTOR`

### TECH-ANTITARGET-PROTOCOL — fan-out 3

**An anti-target docking protocol in which every panel receptor recovers its own cognate crystallographic ligand inside the pre-registered criterion, with no receptor dropped, no search box re-centred and no band lowered**

*Category:* `structure_prediction` · *state:* `absent` · *confidence in that state:* `moderate`

**Why it matters.** Several panel receptors miss their own cognate ligand, so the panel is unreadable — and because the published scope clauses are maximum-over-the-panel statements, one unreadable receptor makes all of them unreadable. A failing target may not be dropped, which is what makes this a protocol problem rather than a curation one.

**What the state assessment rests on:**
- Nothing is currently scanning for this.

**Unblocks.** routes: RT-DEGRADER · requirements: R14 · instruments: V21

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2028` | moderate | Several of the failing receptors are genuinely hard docking targets with large flexible sites; a protocol that recovers all of them is not a parameter tweak. |
| expected | `2027` | low | Ensemble or co-folding-assisted receptor preparation is the likely route, and both are improving. The requirement that no receptor be dropped is what makes this slower than it looks. |
| optimistic | `2026H2` | moderate | This is substantially a PREPARATION problem and could plausibly be fixed here rather than waited for — a bounded piece of work on receptor preparation, not a new capability. |

*Basis:* `extrapolated` · *impact here:* `moderate` · *last reviewed:* 2026-08-05

**What would move this.** Either an improved receptor-preparation protocol built here, or a docking method reporting cognate-ligand recovery across a diverse receptor panel. ⭐ The first is startable now.

*Scanned by:* `TRG-ANTITARGET-PANEL-PROTOCOL`

### TECH-ATOM-MAPPER — fan-out 3

**An atom mapper that reaches the provable floor on the remaining congeneric edge WITHOUT a degenerate correspondence — without mapping a carbon onto a hydrogen**

*Category:* `free_energy_method` · *state:* `absent` · *confidence in that state:* `high`

**Why it matters.** The best available map falls one atom short and the search budget is provably not binding, so more search time buys nothing; the one map that does reach the floor gets there by a chemically impossible correspondence. This is a small, sharp dependency and it blocks a specific edge.

**What the state assessment rests on:**
- Nothing is currently scanning for this.

**Unblocks.** routes: RT-DEGRADER · requirements: R7 · instruments: V6

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2028` | moderate | Atom mapping is mature tooling and receives incremental attention; a mapper improving on the current floor without degenerate correspondences is not anyone's priority. |
| expected | `2027` | low | Free-energy map construction is actively maintained and mapping quality is a known pain point, so incremental improvement is likely even if not targeted at this case. |
| optimistic | `2026H2` | low | A single release of an existing mapper could close a one-atom gap. |

*Basis:* `extrapolated` · *impact here:* `marginal` · *last reviewed:* 2026-08-05

**What would move this.** A release note from any maintained atom mapper reporting improved correspondence quality. The search budget is provably not binding here, so more compute is not the answer.

*Scanned by:* `TRG-ATOM-MAPPER-FLOOR`

### TECH-AUTONOMOUS-AGENT — fan-out 3

**Autonomous research agents able to carry a multi-month scientific thread — planning, running, checking and revising — with provenance a reviewer would accept**

*Category:* `autonomous_research_agent` · *state:* `partially_landed` · *confidence in that state:* `moderate`

**Why it matters.** This program is one person with no bench, and its binding constraint after money is attention. An agent that can hold a long thread would change what a solo program can attempt rather than merely how fast it goes. It is also the dependency this repository is best placed to notice arriving, because it is already operated this way.

**What the state assessment rests on:**
- Agents already execute this repository's compute lanes, monitoring and document generation.
- The arm that has NOT landed is unsupervised multi-month scientific judgement: the repository's own automation record shows a scheduled agent task credited in two documents that has never produced an entry.

**Unblocks.** routes: RT-METHODS-PAPER, RT-DEGRADER, RT-ASO

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2029` | moderate | Reliability over months, not hours, is the gap. This repository's own record shows a scheduled agent task credited in two documents that has never produced an entry — long-horizon reliability is genuinely not solved. |
| expected | `2027` | moderate | Agent capability on multi-step technical work has improved rapidly and continuously. The remaining gap is durability and provenance rather than raw capability, and both are being worked on directly. |
| optimistic | `2026H2` | moderate | Much of this has already landed here: agents run the compute lanes, the monitoring and the document generation. The missing piece is unsupervised scientific judgement over long horizons. |

*Basis:* `evidence_based` · *impact here:* `large` · *last reviewed:* 2026-08-05

**What would move this.** Demonstrated multi-month autonomous research threads with provenance a reviewer would accept. ⭐ This repository is unusually well placed to observe this directly, because it is already operated this way and its failures are recorded.

*Scanned by:* `TRG-AUTONOMOUS-RESEARCH-AGENT`

### TECH-COMPUTE-COST — fan-out 3

**A sustained fall in the price of the simulation this program actually buys — cost per nanosecond of molecular dynamics at usable accuracy**

*Category:* `compute_economics` · *state:* `early_signals` · *confidence in that state:* `moderate`

**Why it matters.** Several parked items are parked on price rather than on method. A sustained fall converts them from unaffordable to routine without any scientific advance at all — and this repository already measures the relevant price series, so it is one of the few dependencies it can observe directly rather than infer.

**What the state assessment rests on:**
- The repository samples the GPU market on a schedule and holds a price time series; the trend has not been graded as a sustained fall.

**Unblocks.** routes: RT-DEGRADER, RT-MONOVALENT · requirements: R6

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2029` | moderate | Rental prices for the cards this work uses are set by a market with demand from elsewhere. A sustained fall is not guaranteed and the market has thinned as well as cheapened within single days. |
| expected | `2027H2` | moderate | New accelerator generations and broadening supply have historically produced step changes in cost per unit of simulation, and the measured throughput table here already records card-to-card ratios large enough to matter. |
| optimistic | `2026H2` | moderate | A single generation of hardware entering the rental market at scale would move the rate immediately, and this program measures that rate continuously. |

*Basis:* `evidence_based` · *impact here:* `moderate` · *last reviewed:* 2026-08-05

**What would move this.** The repository's own price series showing a sustained fall in cost per nanosecond rather than a fall in hourly rate. ⚠ Those are different: a cheap slow card and an expensive fast one look identical on hourly price.

**⚠ Adoption note.** The measurement home is the repository's own cost model and price sampling. This is one of very few dependencies observable directly rather than inferred from the literature.

*Not scannable — watched another way.* A literature search cannot see a GPU price. This is measured directly from a live market board -- relaunch_market_gate.price_offers takes the snapshot and vast_cost_model.py converts it to the $/ns basis every in-flight row is graded against -- so the watch here is a PRICE observation on every fleet launch, not a weekly scan. Inventing an arXiv query to clear [T3] would manufacture the credited-but-silent scanner MAINTENANCE.md section 4 exists to warn about.

### TECH-RXR-HETERODIMER-REPORT — fan-out 1

**A primary report of NR4A3 forming a permissive or ligand-modulable heterodimer with RXR in cells, contradicting the published negative**

*Category:* `published_measurement` · *state:* `absent` · *confidence in that state:* `high`

**Why it matters.** One closed route turns entirely on a single measured biological fact about this receptor, so only a contradicting primary measurement of that same fact reopens it. No method advance does — which is exactly why it is registered as a measurement dependency and not a capability one.

**What the state assessment rests on:**
- The published negative stands unchallenged.

**Unblocks.** routes: RT-RXR

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `never` | high | The closure rests on a direct published measurement of this receptor's behaviour. The conservative reading is simply that the measurement is correct, in which case no contradicting report will ever appear. |
| expected | `beyond-2031` | moderate | Nobody is re-examining this question, and there is no incentive to: the receptor is not a commercial target and the negative result is not contested. |
| optimistic | `2029` | low | A systematic nuclear-receptor dimerisation survey could re-open it incidentally, without anyone intending to. |

*Basis:* `speculative` · *impact here:* `marginal` · *last reviewed:* 2026-08-05

**What would move this.** A primary measurement of this receptor's heterodimerisation contradicting the published negative. ⚠ No method advance moves this — the closure turns on one biological fact, so only a measurement of that same fact counts.

*Scanned by:* `TRG-NR4A3-DIRECT-MATTER`

### TECH-ASO-SPECIFICITY-MODEL — fan-out 1

**A calibrated oligonucleotide off-target and cleavage-activity predictor, and an accessibility-aware efficacy model**

*Category:* `foundation_model_biology` · *state:* `absent` · *confidence in that state:* `moderate`

**Why it matters.** The junction oligonucleotide's predicted specificity currently rests on a deliberately conservative heuristic, and its potency ranking on a local-fold proxy. A calibrated model would let both be re-graded on evidence rather than on caution — which could move the route in either direction, and that is the point.

**What the state assessment rests on:**
- No calibrated cleavage-activity predictor is established for this design class.

**Unblocks.** routes: RT-ASO

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2029` | moderate | Calibrated cleavage-activity prediction needs training data that is largely proprietary to the companies running these programmes. |
| expected | `2028` | low | Oligonucleotide therapeutics are commercially active and off-target prediction is a regulatory pressure point, so a published calibrated model is plausible within a few years. |
| optimistic | `2027` | low | A public dataset release from any active programme would enable a calibrated model quickly; the modelling is not the hard part. |

*Basis:* `extrapolated` · *impact here:* `moderate` · *last reviewed:* 2026-08-05

**What would move this.** A published cleavage-activity dataset with mismatch coverage, or a calibrated predictor built on one.

**⚠ Adoption note.** ⚠ This could move the route in EITHER direction. The current heuristic is deliberately conservative, so a calibrated model might reveal more off-targets rather than fewer — and that is a reason to want it, not a reason to avoid it.

*Scanned by:* `TRG-ASO-OFFTARGET-PREDICTOR`, `TRG-ASO-EFFICACY-ACCESSIBILITY`

[← L0](../L0-ecosystem.md)
