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
| 10 | **TECH-RECONSTRUCTED-IPD** | `biological_dataset` | `partially_landed` | 2027 | **2026H2** | 2026H2 | `evidence_based` | `large` | n/a — watched another way |
| 9 | **TECH-COFOLD-ASSEMBLY** | `structure_prediction` | `partially_landed` | 2028 | **2027** | 2026H2 | `evidence_based` | `transformative` | yes |
| 7 | **TECH-CHEAP-ENSEMBLE** | `conformational_ensemble` | `partially_landed` | 2028 | **2027** | 2026H2 | `evidence_based` | `large` | yes |
| 7 | **TECH-POSE-CONVERGENCE** | `structure_prediction` | `absent` | 2030 | **2028** | 2027 | `extrapolated` | `large` | yes |
| 7 | **TECH-CLOUD-WET-LAB** | `lab_automation` | `early_signals` | beyond-2031 | **2029** | 2027H2 | `extrapolated` | `transformative` | yes |
| 6 | **TECH-EXPOSURE-CRITERION** | `free_energy_method` | `absent` | 2029 | **2027H2** | 2026H2 | `extrapolated` | `moderate` | yes |
| 6 | **TECH-VIRTUAL-CELL** | `foundation_model_biology` | `early_signals` | 2030 | **2028** | 2027H1 | `extrapolated` | `transformative` | yes |
| 5 | **TECH-CHARGE-CHANGE-FEP** | `free_energy_method` | `absent` | 2028 | **2027** | 2026H2 | `extrapolated` | `moderate` | yes |
| 5 | **TECH-OBSERVED-CRL** | `structure_prediction` | `absent` | beyond-2031 | **2028** | 2027 | `speculative` | `moderate` | yes |
| 4 | **TECH-VECTOR-DELIVERY** | `lab_automation` | `absent` | beyond-2031 | **2030** | 2028 | `speculative` | `large` | yes |
| 4 | **TECH-GLUE-DESIGN** | `generative_design` | `early_signals` | 2029 | **2027H2** | 2026H2 | `extrapolated` | `large` | yes |
| 4 | **TECH-TERNARY-ALCHEMY** | `free_energy_method` | `absent` | 2030 | **2028** | 2027H1 | `extrapolated` | `large` | yes |
| 4 | **TECH-E1-POWERED** | `free_energy_method` | `absent` | beyond-2031 | **2029** | 2027H2 | `speculative` | `moderate` | yes |
| 4 | **TECH-E3-RECRUITER-STRUCTURE** | `structure_prediction` | `absent` | 2030 | **2028** | 2027 | `speculative` | `moderate` | yes |
| 4 | **TECH-NONCOVALENT-PARALOGUE-CONTROL** | `published_measurement` | `absent` | beyond-2031 | **2028** | 2027 | `speculative` | `large` | yes |
| 4 | **TECH-JUNCTION-PMHC** | `foundation_model_biology` | `absent` | 2032 | **2029** | 2027H2 | `extrapolated` | `large` | yes |
| 4 | **TECH-JUNCTION-CLINICAL-PRECEDENT** | `published_measurement` | `partially_landed` | beyond-2032 | **2029** | 2027H1 | `extrapolated` | `moderate` | yes |
| 3 | **TECH-OLIGO-DELIVERY** | `lab_automation` | `early_signals` | beyond-2031 | **2029** | 2027H2 | `extrapolated` | `transformative` | yes |
| 3 | **TECH-ANTITARGET-PROTOCOL** | `structure_prediction` | `absent` | 2028 | **2027** | 2026H2 | `extrapolated` | `moderate` | yes |
| 3 | **TECH-ATOM-MAPPER** | `free_energy_method` | `absent` | 2028 | **2027** | 2026H2 | `extrapolated` | `marginal` | yes |
| 3 | **TECH-AUTONOMOUS-AGENT** | `autonomous_research_agent` | `partially_landed` | 2029 | **2027** | 2026H2 | `evidence_based` | `large` | yes |
| 3 | **TECH-COMPUTE-COST** | `compute_economics` | `early_signals` | 2029 | **2027H2** | 2026H2 | `evidence_based` | `moderate` | n/a — watched another way |
| 1 | **TECH-RXR-HETERODIMER-REPORT** | `published_measurement` | `absent` | never | **beyond-2031** | 2029 | `speculative` | `marginal` | yes |
| 1 | **TECH-ASO-SPECIFICITY-MODEL** | `foundation_model_biology` | `absent` | 2029 | **2028** | 2027 | `extrapolated` | `moderate` | yes |
| 1 | **TECH-CONDENSATE-RESOLUTION** | `conformational_ensemble` | `early_signals` | beyond-2029 | **2028** | 2027H1 | `speculative` | `marginal` | yes |

**2 dependency(ies) cannot be seen by a literature search and are watched
another way** — each says how, under `not_scannable_because` in its Detail entry: `TECH-COMPUTE-COST`, `TECH-RECONSTRUCTED-IPD`. ⛔ This is a recorded decision, not a gap; the
alternative was a fabricated query that reports nothing forever while being credited
as coverage.

## Detail

### TECH-EMC-MODEL-ACCESS — fan-out 14

**Access to a patient-derived EMC model through a collaborator, or through a solo-affordable cloud or robotic wet-lab service with EMC-runnable assay scope**

*Category:* `experimental_access` · *state:* `absent` · *confidence in that state:* `high`

**Why it matters.** The cell-line repositories exclude unaffiliated individuals by published policy rather than by price, so no budget reaches this and every confirm-gated row is gated on a person. It is the highest fan-out non-method dependency in the portfolio, and it is about ACCESS rather than capability.

> ⏳ **1 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-EMC-FUNCTIONAL-MODEL` · *Model-dependent GD2 upregulation in Ewing sarcoma with the EZH2 inhibitor tazemetostat: Prerequisites for combination with GD2-specific CAR T cells* (PPR, 2026-07-24) — seen 2026-08-08

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

> ⏳ **2 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-SARCOMA-ATRI-RESPONSE-PANEL` · *Elimusertib enhances cytotoxic effects of conventional chemotherapy and sensitizes to radiation in preclinical Ewing sarcoma models* (Sci Rep, 2026-03-27) — seen 2026-08-08
> - `TRG-EMC-EXPRESSION-DATASET` · *Ki-67 labeling index and HIF-1α expression delineate prognostic heterogeneity within FNCLCC grade 2 soft-tissue sarcoma: a multicenter cohort study* (PPR, 2026-08-31) — seen 2026-09-04

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

### TECH-RECONSTRUCTED-IPD — fan-out 10

**Patient-level survival data recovered from published Kaplan-Meier curves, at a quality this disease's series can actually support**

*Category:* `biological_dataset` · *state:* `partially_landed` · *confidence in that state:* `moderate`

**Why it matters.** ⭐ THIS IS THE CAPABILITY TWO PARKED ROUTES WERE WAITING ON WITHOUT NAMING IT. RT-SEQUENCING is parked with the rationale 'Only individual-patient data could change this, and it is not obtainable here', and RT-SCHEDULING is closed `definitional` because POLICY-evidence.md s2.4 forbids merging time-anchored endpoints so no pooled progression-free-survival figure may be built. Reconstruction obtains the first and legalises the second: Guyot et al. 2012 inverts a published curve plus its numbers-at-risk table back into the data that generated it, and a patient-level dataset may be pooled where a median may not. ⚠ It adds censoring structure, never patients — every selection and publication bias of the source series survives intact.

**What the state assessment rests on:**
- The instrument is built and validated: research/modalities/emc_ipd_survival.py implements Guyot et al. 2012 and its known-answer control recovers a held-out cohort EXACTLY (26 patients, 11 events, 15 censored), with survival agreeing within 0.004 except at the tail, and the control is demonstrably capable of failing.
- ⛔ THE ARM THAT HAS NOT LANDED IS THE DATA. No published EMC figure has been digitized into it, so the artifact computes over an empty CURVES table and says so. Whether the capability arrives in this disease depends on how many EMC series print a numbers-at-risk table, which nobody has counted.
- The control feeds exact coordinates, so it bounds ALGORITHMIC error only and is structurally unable to fail on a mis-read pixel.

**Unblocks.** blockers: BLK-NO-CURATED-CLINICAL-DATA · routes: RT-IPD-SURVIVAL, RT-RISK-MODEL, RT-SURVEILLANCE, RT-SEQUENCING, RT-SURGICAL-QUALITY, RT-METASTASECTOMY, RT-LIMB-PERFUSION, RT-LUNG-DIRECTED, RT-RT-INTENSIFY

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2027` | moderate | If most EMC series print no numbers-at-risk table, the quality floor refuses them and the capability never arrives in this disease however good the algorithm is. That is the live failure mode and nobody has counted the tables. |
| expected | `2026H2` | moderate | The instrument is built and its known-answer control passes; what remains is digitizing figures from open-access papers already retrieved. That is manual work measured in hours, not a capability anyone is waiting on. |
| optimistic | `2026H2` | moderate | ⛔ THERE IS NO OPTIMISTIC CASE DISTINCT FROM THE EXPECTED ONE, and saying so is the honest entry. Nothing external accelerates this — no paper, no model and no collaborator. It is bounded entirely by whether someone reads the figures. |

*Basis:* `evidence_based` · *impact here:* `large` · *last reviewed:* 2026-08-09

**What would move this.** A count of how many published EMC series print a numbers-at-risk table beside their Kaplan-Meier curve. That single census decides whether the capability is reachable at all, and it is free.

**⚠ Adoption note.** ⚠ The date refers to a DATASET existing, not to any clinical question being answered by it. Reconstruction adds censoring structure and no patients, so a landed forecast here licenses time-to-event ANALYSIS and licenses nothing about the strength of the underlying series.

*Not scannable — watched another way.* ⛔ NOTHING EXTERNAL WILL ANNOUNCE THIS ONE, AND THAT IS WHY IT NEEDS SAYING RATHER THAN A TRIGGER. Every other capability here waits on someone else's paper, so a literature scan is the right watcher. This one waits on a method published in 2012 being applied to figures already retrieved — the algorithm landed fourteen years ago and the instrument is built and validated in this repository. A scan would return reconstruction papers in other diseases forever and none of them would move it.

WHAT WATCHES IT INSTEAD: `curves_supplied` in research/modalities/emc-ipd-survival.json, which is 0 today and is the only number that can change this capability's state, plus research/modalities/tests/test_emc_ipd_survival.py, which fails the build if a curve is added without digitization provenance. ⚠ The genuinely uncertain input is not a method but a COUNT — how many published EMC series print a numbers-at-risk table beside their curve — and nobody has taken it.

### TECH-COFOLD-ASSEMBLY — fan-out 9

**A sequence-only co-folder evaluated on ternary ASSEMBLY — inter-chain accuracy on post-training-horizon induced complexes — rather than on per-chain pocket accuracy**

*Category:* `structure_prediction` · *state:* `partially_landed` · *confidence in that state:* `high`

**Why it matters.** One co-folder failing is not the class failing: the same harness already recognises a correct ternary when both binding sites are supplied, so the plumbing is not what missed. What is missing is a model benchmarked on the assembly problem itself, and a benchmark discipline that reports inter-chain rather than per-chain accuracy.

> ⏳ **3 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-COFOLD-TERNARY-ASSEMBLY` · *Boltz-Perturb: Improving Diversity and Accuracy in Protein-Ligand Co-Folding through Training-Free Conditioning Perturbation* (PPR, 2026-08-05) — seen 2026-08-08
> - `TRG-COFOLD-TERNARY-ASSEMBLY` · *MG2Act: A Mechanism-Inspired Sequential Attention Framework for Molecular Glue Degradation Prediction* (PPR, 2026-08-13) — seen 2026-08-21
> - `TRG-COFOLD-TERNARY-ASSEMBLY` · *Beyond random splits: A hierarchical benchmark of transferability and reliability in PROTAC activity prediction* (Comput Biol Chem, 2026-08-27) — seen 2026-09-04

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

> ⏳ **7 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-GENERATIVE-ENSEMBLE` · *Mavchen 1: A Conformational Ensemble Platform for Protein Ligand Pose Prediction That Substantially Outperforms Static Structure Prediction in a Category-Stratified Benchmark* (PPR, 2026-07-29) — seen 2026-08-08
> - `TRG-GENERATIVE-ENSEMBLE` · *UniFlow: Unifying protein conformational ensemble generation and machine-learned force fields with a scalable normalizing Flow* (PPR, 2026-07-20) — seen 2026-08-08
> - `TRG-GENERATIVE-ENSEMBLE` · *ConformFlow: scalable normalizing flow for protein conformational ensemble generation* (PPR, 2026-06-16) — seen 2026-08-08
> - `TRG-CRYPTIC-POCKET-PREDICTION` · *Highly selective small molecule Kv1.3 inhibitors bind to a cryptic pocket and stabilize the channel in a C-type inactive conformation* (PPR, 2026-06-04) — seen 2026-08-08
> - `TRG-CRYPTIC-POCKET-PREDICTION` · *AE-PocketMiner Uses Attention to Simultaneously Predict Cryptic Pockets and Their Allosteric Coupling* (PPR, 2026-05-23) — seen 2026-08-08
> - `TRG-CRYPTIC-POCKET-PREDICTION` · *UniPocket: Unified Ligand and Cryptic Pocket Prediction from Protein Language Model Embeddings* (ACM BCB, 2026-07-28) — seen 2026-08-21
> - `TRG-GENERATIVE-ENSEMBLE` · *PHASE: encoding global protein ensembles with local Hamiltonians and all-atom backmapping* (arXiv, 2026-08-24) — seen 2026-08-28

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

> ⏳ **46 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-POSE-ORIENTATION-CONVERGENCE` · *Exploring the neuroprotective mechanism of lumbrokinase against ischemic stroke based on network pharmacology, molecular docking and experimental validation* (J Ethnopharmacol, 2026-06-19) — seen 2026-08-08
> - `TRG-POSE-ORIENTATION-CONVERGENCE` · *Neuroprotective effects of aqueous extract of Pterocarpus mildbraedii Harms. on some biochemical markers in Alzheimer's disease using an AlCl&lt;sub&gt;3&lt;/sub&gt;-induced rat model: Integrated ADMET, network pharmacology, molecular docking, and in vivo experimental validation* (J Ethnopharmacol, 2026-06-09) — seen 2026-08-08
> - `TRG-POSE-ORIENTATION-CONVERGENCE` · *Revealing the mechanism of heptamethoxyflavone against diabetic kidney disease: an integrated study combining network pharmacology, molecular docking and experimental validation* (Biochem Biophys Res Commun, 2026-07-08) — seen 2026-08-08
> - `TRG-POSE-ORIENTATION-CONVERGENCE` · *Integrating network toxicology, molecular docking and experimental validation reveals potential mechanisms of DEHP in osteoarthritis* (Exp Gerontol, 2026-06-11) — seen 2026-08-08
> - `TRG-POSE-ORIENTATION-CONVERGENCE` · *Integrated network pharmacology, molecular docking, and experimental validation reveal synergistic inhibition of EGFR and PI3K-Akt/JAK2-STAT3 pathways by Esculin and Esculetin to exert anti-colorectal cancer effects* (Toxicol Appl Pharmacol, 2026-08-04) — seen 2026-08-08
> - `TRG-POSE-ORIENTATION-CONVERGENCE` · *Integrative screening of plant volatiles through transient receptor potential channel docking, olfactometry, and field validation in Bemisia tabaci* (Pest Manag Sci, 2026-04-16) — seen 2026-08-08
> - `TRG-POSE-ORIENTATION-CONVERGENCE` · *Mechanisms of Qing-Shen-Du formula in treating diabetic kidney disease: Integrating network pharmacology, molecular docking, molecular dynamics, transcriptomics, and experimental validation* (J Chromatogr B Analyt Technol Biomed Life Sci, 2026-07-27) — seen 2026-08-08
> - `TRG-POSE-ORIENTATION-CONVERGENCE` · *[(Bromomethyl)phenyl]methyl-Conjugated Chalcone Derivatives as Potential Lung Cancer Inhibitors: Structure Modification, Molecular Docking, Molecular Dynamics and In Vitro Validation* (Int J Mol Sci, 2026-07-08) — seen 2026-08-08
> - …and 38 more

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

### TECH-CLOUD-WET-LAB — fan-out 7

**A remote robotic or cloud wet lab, rentable per experiment by an unaffiliated researcher, at a price and assay scope that covers EMC cell work**

*Category:* `lab_automation` · *state:* `early_signals` · *confidence in that state:* `moderate`

**Why it matters.** This is the only watched capability that could flip the program's FOUNDING CONSTRAINT — that no wet lab is available, so every step must be in-silico or publish-to-convince. It would make the wet-lab-gated experiments runnable by this program rather than by a hypothetical collaborator.

> ⏳ **1 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-CLOUD-WET-LAB` · *When Brownian Motion Meets Clinical Laboratory Automation: A DLS-Inspired Autocorrelation Function for Characterizing Workflow Performance in Sample Processing* (Diagnostics (Basel), 2026-07-07) — seen 2026-09-04

**What the state assessment rests on:**
- Cloud-lab services exist commercially.
- ⚠ A cloud lab unlocks robotic EXECUTION, not the reagents or the biology. The EMC cell line remains a separate dependency, so this flips the execution gate and not automatically the material gate.

**Unblocks.** blockers: BLK-NO-WET-LAB, BLK-FUNCTIONAL-ACTIONABILITY · routes: RT-ASO-ASK, RT-ATR-PANEL, RT-COVALENT-PROBE, RT-PANNR4A-EXVIVO · requirements: R4

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

### TECH-EXPOSURE-CRITERION — fan-out 6

**A solvent-exposure or thiol-reactivity criterion that recovers the one NR4A-family covalent site with literature support as engageable on a state-matched opened model**

*Category:* `free_energy_method` · *state:* `absent` · *confidence in that state:* `moderate`

**Why it matters.** The standing exposure cutoff fails that positive control, so anything it adjudicates inherits a demonstrated false negative and only a threshold-free rank survives. A criterion that passes the control makes the whole covalent screen readable again rather than rank-only.

> ⏳ **22 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-COVALENT-EXPOSURE-CRITERION` · *Substituted cysteine accessibility method (SCAM) in membrane transporters studies: Learn from lactose permease* (Biochimie, 2026-05-30) — seen 2026-08-08
> - `TRG-COVALENT-EXPOSURE-CRITERION` · *Fine-tuning thiosemicarbazones with heterocyclic substituents: identification of styryl-dependent cysteine reactivity and potent anti-cancer activity* (Chem Sci, 2026-07-15) — seen 2026-08-08
> - `TRG-COVALENT-EXPOSURE-CRITERION` · *A FRET-Based Assay for Assessing Covalent Warhead Reactivity* (ACS Omega, 2026-06-24) — seen 2026-08-08
> - `TRG-COVALENT-EXPOSURE-CRITERION` · *Covalent character of Cellobiose-Water hydrogen bonds revealed by ELF and QTAIM for enhanced dewatering and reactivity* (J Mol Graph Model, 2026-07-02) — seen 2026-08-08
> - `TRG-COVALENT-EXPOSURE-CRITERION` · *Photoinitiated thiol-ene reactions of glycals: Effect of C2-substitution on reactivity and regio- and stereoselectivity* (Carbohydr Res, 2026-04-17) — seen 2026-08-08
> - `TRG-COVALENT-EXPOSURE-CRITERION` · *Cysteine-mapping efforts offer new tools for drug development and discovery: Research groups are characterizing cysteine binding and reactivity traits to provide important new starting points for drug design* (Cancer Cytopathol, 2026-06-01) — seen 2026-08-08
> - `TRG-COVALENT-EXPOSURE-CRITERION` · *Correction: Assessment of solvent exposure of native cysteines in human Hsp90 using thiol-reactive functional tags* (Org Biomol Chem, 2026-06-10) — seen 2026-08-08
> - `TRG-COVALENT-EXPOSURE-CRITERION` · *A Global Ligandability Map of Tryptoline Butynamide Stereoprobes Identifies Covalent Inhibitors of the Actin Maturation Protease* (J Am Chem Soc, 2026-05-20) — seen 2026-08-08
> - …and 14 more

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

> ⏳ **12 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-VIRTUAL-CELL-NO-LINE` · *SLIM: A small linear model with STRING embeddings for single-cell genetic perturbation prediction* (PPR, 2026-08-07) — seen 2026-08-08
> - `TRG-VIRTUAL-CELL-NO-LINE` · *Multimodal physical evidence uncovers interpretable gene regulatory networks for perturbation prediction* (PPR, 2026-06-07) — seen 2026-08-08
> - `TRG-VIRTUAL-CELL-NO-LINE` · *Signal, Bounds, and Baselines: Principles for Evaluating Virtual Cell Perturbation Models* (PPR, 2026-04-22) — seen 2026-08-08
> - `TRG-VIRTUAL-CELL-NO-LINE` · *Spurious correlation inflates performance in single-cell perturbation prediction* (PPR, 2026-05-12) — seen 2026-08-08
> - `TRG-VIRTUAL-CELL-NO-LINE` · *Deep learning models for chemical perturbation prediction do not yet utilise drug molecular features* (PPR, 2026-05-15) — seen 2026-08-08
> - `TRG-VIRTUAL-CELL-NO-LINE` · *LLM-Guided Retrieval for Prediction of Molecular Perturbation Responses* (arXiv, 2026-08-03) — seen 2026-08-08
> - `TRG-VIRTUAL-CELL-NO-LINE` · *Response Magnitude as a Dominant Signal for Held-Out CRISPRi Perturbation Effect Prediction* (arXiv, 2026-07-31) — seen 2026-08-08
> - `TRG-VIRTUAL-CELL-NO-LINE` · *Control-Anchored Residual Flow Matching Conditioned on Gene Geometry for Virtual Cell Perturbation Modeling* (arXiv, 2026-08-07) — seen 2026-08-14
> - …and 4 more

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

### TECH-CHARGE-CHANGE-FEP — fan-out 5

**A validated charge-change correction for alchemical free-energy edges — a co-alchemical-ion or finite-size treatment demonstrated to reproduce a known-answer set of charge-changing transformations**

*Category:* `free_energy_method` · *state:* `absent` · *confidence in that state:* `moderate`

**Why it matters.** Charge-changing edges block legs of the relative free-energy map and killed a high-contrast calibrator route. The correction reopens the EDGES; it does not rescue the calibrator design, which was a poor calibrator on perturbation size alone.

> ⏳ **1 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-CHARGE-CHANGE-FEP` · *Toward Relative Redox Potential Predictions in Flavoproteins: Treatment of a Charge-Changing Mutation in Alchemical Free Energy Simulations* (J Chem Theory Comput, 2026-08-01) — seen 2026-09-04

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

> ⏳ **5 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-GLUE-PROSPECTIVE-DESIGN` · *Discovery of molecular glue degrader for treatment of IMiDs-resistant multiple myeloma based on GLUT-mediated tumor targeting strategy* (Bioorg Chem, 2026-07-28) — seen 2026-08-08
> - `TRG-GLUE-PROSPECTIVE-DESIGN` · *Discovery of CDK4-selective molecular glue degraders by high-throughput proteomics* (PPR, 2026-06-22) — seen 2026-08-08
> - `TRG-GLUE-PROSPECTIVE-DESIGN` · *Integrated proteomic screening reveals design principles of CRBN molecular glue degraders* (PPR, 2026-03-10) — seen 2026-08-08
> - `TRG-GLUE-PROSPECTIVE-DESIGN` · *Leveraging High-Throughput Proteomics and AI-Based Protein Folding to Accelerate VAV1 Molecular Glue Discovery* (PPR, 2026-03-10) — seen 2026-08-08
> - `TRG-GLUE-PROSPECTIVE-DESIGN` · *MG2Act: A Mechanism-Inspired Sequential Attention Framework for Molecular Glue Degradation Prediction* (PPR, 2026-08-13) — seen 2026-08-21

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

> ⏳ **15 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-JUNCTION-PHLA` · *TCR-FramePose: a local-frame representation for decomposing global docking and CDR3 loop geometry in TCR-pMHC recognition* (PPR, 2026-07-04) — seen 2026-08-08
> - `TRG-JUNCTION-PHLA` · *CD8-mediated organization of the TCR–pMHC interface shapes its force response and dissociation pathways* (PPR, 2026-06-20) — seen 2026-08-08
> - `TRG-JUNCTION-PHLA` · *FairTCR: Equity-Aware TCR–pMHC Binding Prediction Across HLA Alleles and Cohort Strata* (PPR, 2026-04-17) — seen 2026-08-08
> - `TRG-JUNCTION-PHLA` · *Active Learning for Budget-Constrained TCR–pMHC Wet-Lab Validation* (PPR, 2026-04-17) — seen 2026-08-08
> - `TRG-JUNCTION-PHLA` · *AI-enabled virtual immunopeptidomics links quantitative neoantigen presentation to immunogenicity* (PPR, 2026-05-10) — seen 2026-08-08
> - `TRG-JUNCTION-PHLA` · *PepBridge for peptide-bridged, unified and structure-aware modeling of pMHC-TCR recognition* (PPR, 2026-04-28) — seen 2026-08-08
> - `TRG-JUNCTION-PHLA` · *Structure-based TCR-pMHC binding prediction and generalization to unseen peptides* (NPJ Drug Discov, 2026-08-14) — seen 2026-08-21
> - `TRG-JUNCTION-PHLA` · *Predicting specificity of TCR-pMHC interactions using machine-learning and biophysical models* (Cell Syst, 2026-08-13) — seen 2026-08-21
> - …and 7 more

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

### TECH-JUNCTION-CLINICAL-PRECEDENT — fan-out 4

**A human clinical readout for a therapy directed at a fusion breakpoint — any fusion, any modality that targets the junction sequence itself**

*Category:* `published_measurement` · *state:* `partially_landed` · *confidence in that state:* `high`

**Why it matters.** The three antigen routes are parked on TECH-JUNCTION-PMHC, which is a TOOL: a predictor or a discovery platform. This row is the other half of the same bet and it is not the same question. A tool would let this program COMPUTE something it currently cannot; a human readout moves the PRIOR on whether immunising against a fusion junction does anything in a person, and moves it supplying no method at all. Keeping them in one row would mean a clinical result could be read as progress on a predictor, or a predictor as evidence that the class works — the two substitutions this register exists to prevent.

> ⏳ **48 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-FUSION-JUNCTION-CLINICAL` · *Development of an oral Lactobacillus casei-based recombinant vaccine expressing GCRV-II multi-epitope fusion protein and its protective efficacy against grass carp hemorrhagic disease* (Fish Shellfish Immunol, 2026-08-04) — seen 2026-09-04
> - `TRG-FUSION-JUNCTION-CLINICAL` · *Publisher Correction: Adjuvant personalized multivalent neoantigen DNA vaccination for MGMT unmethylated glioblastoma: a phase 1 trial* (Nat Cancer, 2026-09-01) — seen 2026-09-04
> - `TRG-FUSION-JUNCTION-CLINICAL` · *Co-administration of a chicken interleukin-2-interferon-α fusion protein enhances immune responses and protective efficacy of an inactivated fowl adenovirus serotype 4 vaccine* (Int J Biol Macromol, 2026-09-01) — seen 2026-09-04
> - `TRG-FUSION-JUNCTION-CLINICAL` · *Generative AI-enabled neoantigen vaccine engineering: From tumor antigen discovery to personalized construct design and translational validation* (Biotechnol Adv, 2026-09-01) — seen 2026-09-04
> - `TRG-FUSION-JUNCTION-CLINICAL` · *A Cell-Penetrating Peptide and Signal Sequence Fusion DNA Vaccine Enhances CD8+ T Cell-Mediated Anti-Tumor Immunity Targeting HPV-16 Cervical Cancer Antigens* (Obstet Gynecol Res, 2026-07-17) — seen 2026-09-04
> - `TRG-FUSION-JUNCTION-CLINICAL` · *A novel bivalent neoantigen vaccine based on mRNA-loaded lipid nanoparticles eradicates hepatocellular carcinoma in mice* (J Control Release, 2026-07-13) — seen 2026-09-04
> - `TRG-FUSION-JUNCTION-CLINICAL` · *Targeting vaccine fusion proteins to APCs increases immunogenicity of adenoviral and mRNA-LNP vaccines* (Mol Ther, 2026-06-26) — seen 2026-09-04
> - `TRG-FUSION-JUNCTION-CLINICAL` · *Neoantigen-based multi-epitope vaccine designing against glioblastoma using reverse vaccinology and immunoinformatic approaches* (Int Immunopharmacol, 2026-06-12) — seen 2026-09-04
> - …and 40 more

**What the state assessment rests on:**
- WHICH HALF LANDED: that a shared, off-the-shelf multi-peptide vaccine spanning a fusion breakpoint can be built, given, and raise durable junction-specific T-cell responses in a human. PMID 42570981 — type 1 EWSR1-FLI1, de novo polyfunctional CD4+ responses against all four fusion-derived peptides, first detectable by month 7 and persisting beyond two years.
- WHICH HALF DID NOT: anything powered. That report is n = 1 and uncontrolled. The only larger human experience of the modality is two SYT-SSX junction-peptide trials from 2005 and 2012 (PMID 15647119, n = 6; PMID 22726592, n = 21), and the published evaluation of the larger one (PMID 23252384) reports that no robust immune response to the target epitope was demonstrated.
- AND NEITHER HALF IS EMC. Every record is a different fusion. Nothing here bears on EWSR1::NR4A3 except by class inheritance, and nothing here measures how much junction peptide-HLA an EMC cell displays — which is BLK-ANTIGEN-COLD, a permanent blocker this row does not touch.

**Unblocks.** routes: RT-VACCINE, RT-JUNCTION-NEOANTIGEN, RT-TCR-IMMTAC, RT-VACCINE-COMBINATION

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `beyond-2032` | moderate | The powered half may simply not arrive. Fusion-driven sarcomas are rare enough that a breakpoint-specific vaccine trial has to be run per fusion, and the two SYT-SSX trials — the only ones ever run — are 14 and 21 years old with no successor. A single-patient report does not start a programme, and a shared off-the-shelf peptide vaccine failing its Phase 2 in a commoner indication is the kind of result that removes commercial appetite for the whole class. |
| expected | `2029` | low | Two things that were not true for the SYT-SSX trials are true now: individualised neoantigen vaccines have a positive Phase 3 behind them, which pulls money and regulatory familiarity toward cancer vaccines generally, and fusion breakpoints are being enumerated routinely in clinical genomics (PMID 36900411) so a fixed off-the-shelf panel is orderable rather than bespoke. The expected band assumes a small investigator-initiated basket in fusion-positive sarcoma reads out, not a registrational trial. |
| optimistic | `2027H1` | low | The Tübingen group behind PMID 42570981 already has the construct, the adjuvant combination and one long-followed patient. A case series from the same centre is the cheapest possible next step and needs nobody's permission but an ethics committee's. |

*Basis:* `extrapolated` · *impact here:* `moderate` · *last reviewed:* 2026-08-28

**What would move this.** A registered trial of a fusion-breakpoint-directed vaccine or TCR-T opening in any fusion-driven sarcoma — free to detect, since method-watch.yml already queries ClinicalTrials.gov v2. ⛔ AND A NEGATIVE READOUT MOVES IT JUST AS FAR: a powered trial of this modality reporting no immunologic or clinical signal would push the conservative band toward `never`, and is the direction a watch list maintained by people who want the route to work will under-report.

**⚠ Adoption note.** ⚠ THE DATE IS FOR A READOUT EXISTING, NOT FOR EMC BENEFITING FROM ONE. Every plausible readout is in a different fusion, so what lands is a stronger class-inheritance argument — which is BLK-CLASS-INHERITANCE, still standing — and never an EMC measurement. A landed forecast here licenses raising the prior on the three antigen routes and licenses nothing about EWSR1::NR4A3 junction abundance.

*Scanned by:* `TRG-FUSION-JUNCTION-CLINICAL`

### TECH-OLIGO-DELIVERY — fan-out 3

**An oligonucleotide tumour-delivery technology reaching non-hepatic solid tumours — a conjugate, tumour-penetrating peptide or ligand-targeted lipid nanoparticle — OR a characterised EMC-enriched surface antigen to serve as its targeting arm**

*Category:* `lab_automation` · *state:* `early_signals` · *confidence in that state:* `moderate`

**Why it matters.** Delivery is the single remaining gate on the most structurally sound route in the portfolio, and it is engineering rather than biology. The honest bottleneck is not that delivery cannot be simulated — it is that no validated way to deliver an oligonucleotide to an EMC tumour exists. A single characterised EMC surface antigen or a working soft-tissue-sarcoma conjugate would change this route's standing more than any predictor could.

> ⏳ **10 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-OLIGO-DELIVERY-PREDICTOR` · *The biodistribution and effect of post-exposure neutralising monoclonal antibody treatment in a mouse model of SARS-CoV-2 infection with viral spread to the brain* (PPR, 2026-05-29) — seen 2026-08-08
> - `TRG-OLIGO-DELIVERY-PREDICTOR` · *A Mechanistic PBPK-PD Framework to Predict Clinical Success of Tuberculosis Treatments Across Populations: A Proof- of-Concept Study* (PPR, 2026-05-25) — seen 2026-08-08
> - `TRG-OLIGO-DELIVERY-PREDICTOR` · *Development of a Dissolution-Informed PBPK-Assisted In Vitro–In Silico Correlation Framework for Predicting Food Effects of Lurasidone Hydrochloride* (PPR, 2026-08-12) — seen 2026-08-14
> - `TRG-OLIGO-DELIVERY-PREDICTOR` · *Advances in Machine Learning-Enhanced PBPK Models for Brain-Targeted Drug Delivery via Nanocarriers: A Comprehensive Review* (J Funct Biomater, 2026-08-03) — seen 2026-08-28
> - `TRG-OLIGO-DELIVERY-PREDICTOR` · *Biodistribution and transport of intratympanically administered drugs in the inner ear using a porcine ex-vivo chamber model* (Mater Des, 2026-07-02) — seen 2026-08-28
> - `TRG-OLIGO-DELIVERY-PREDICTOR` · *PBPK model of carbamazepine and its metabolite for bioequivalence assessment: prioritizing early exposure and single-dose study designs* (Eur J Pharm Biopharm, 2026-09-02) — seen 2026-09-04
> - `TRG-OLIGO-DELIVERY-PREDICTOR` · *PBPK-Based Prediction of Oliceridine Exposure in Breast Milk and Relative Infant Dose During the First 24 h After Cesarean Delivery* (J Clin Pharmacol, 2026-09-01) — seen 2026-09-04
> - `TRG-OLIGO-DELIVERY-PREDICTOR` · *Moxifloxacin-Mediated Downregulation of Intestinal P-Glycoprotein Alters the Pharmacokinetics of Dabigatran Etexilate: Mechanistic Insights in Rats and PBPK Model-Informed Dose Optimization* (Pharmaceutics, 2026-08-20) — seen 2026-09-04
> - …and 2 more

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

> ⏳ **14 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-ANTITARGET-PANEL-PROTOCOL` · *Cytotoxic and genotoxic effects of oxime β-lapachone in human cancer cells: selectivity toward NCI-H460 and insights from molecular docking* (Hum Cell, 2026-07-27) — seen 2026-08-08
> - `TRG-ANTITARGET-PANEL-PROTOCOL` · *Conformation-dependent donor selectivity in the xanthan gum glycosyltransferase GumK revealed by AI-based docking* (Sci Rep, 2026-07-07) — seen 2026-08-08
> - `TRG-ANTITARGET-PANEL-PROTOCOL` · *DeepKinomeWeb: a quantitative, panel-level platform for kinase inhibitor screening and selectivity profiling* (Nucleic Acids Res, 2026-07-01) — seen 2026-08-08
> - `TRG-ANTITARGET-PANEL-PROTOCOL` · *Limitations of Molecular Docking in Predicting the Selectivity of Selective Androgen Receptor Modulators (SARMs): A Comparative Study of YK11 and Ostarine Across Five Nuclear Receptors* (Int J Mol Sci, 2026-06-26) — seen 2026-08-08
> - `TRG-ANTITARGET-PANEL-PROTOCOL` · *AI-assisted molecular docking and molecular dynamics simulations for predicting off-target effects of AKT1 ATP-competitive inhibitors* (J Biomol Struct Dyn, 2026-06-27) — seen 2026-08-08
> - `TRG-ANTITARGET-PANEL-PROTOCOL` · *Integrated Experimental and Computational Profiling of Curcumin-Derived Diarylpentanoids Reveals Mechanistic Determinants of COX1/COX2 Inhibition and Selectivity* (ACS Omega, 2026-06-03) — seen 2026-08-08
> - `TRG-ANTITARGET-PANEL-PROTOCOL` · *The Selectivity Implications of Docking Libraries with Greater and Lesser Similarities to Bio-like Molecules* (J Med Chem, 2026-05-08) — seen 2026-08-08
> - `TRG-ANTITARGET-PANEL-PROTOCOL` · *Evidence of off-target probe binding affecting 10x Genomics Xenium gene panels compromise accuracy of spatial transcriptomic profiling* (Elife, 2026-05-01) — seen 2026-08-08
> - …and 6 more

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

*Category:* `autonomous_research_agent` · *state:* `partially_landed` · *confidence in that state:* `high`

**Why it matters.** This program is one person with no bench, and its binding constraint after money is attention. An agent that can hold a long thread would change what a solo program can attempt rather than merely how fast it goes. It is also the dependency this repository is best placed to notice arriving, because it is already operated this way.

> ⏳ **54 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-AUTONOMOUS-RESEARCH-AGENT` · *Autonomous biomedical research with an artificial intelligence agent* (Science, 2026-07-09) — seen 2026-08-08
> - `TRG-AUTONOMOUS-RESEARCH-AGENT` · *A Modular and Affordable Self-Driving Laboratory for Vision-Guided Optimization of Metal Electrodeposition* (ACS Appl Mater Interfaces, 2026-06-30) — seen 2026-08-08
> - `TRG-AUTONOMOUS-RESEARCH-AGENT` · *Transforming Molecular Science With Large Language Models: From Molecule Understanding to Autonomous Scientific Discovery* (Chem Asian J, 2026-06-01) — seen 2026-08-08
> - `TRG-AUTONOMOUS-RESEARCH-AGENT` · *Autonomous pathology research using agentic AI shows potential in oncology* (Nat Med, 2026-06-01) — seen 2026-08-08
> - `TRG-AUTONOMOUS-RESEARCH-AGENT` · *An agentic framework for autonomous scientific discovery in cancer pathology* (Nat Med, 2026-04-29) — seen 2026-08-08
> - `TRG-AUTONOMOUS-RESEARCH-AGENT` · *Research on Reinforcement Learning-Based Autonomous Navigation and Obstacle Avoidance Methods for AGVs in Unknown Hospital Environments* (Sensors (Basel), 2026-05-29) — seen 2026-08-08
> - `TRG-AUTONOMOUS-RESEARCH-AGENT` · *From Experimental Planning to Autonomous Discovery: The Changing Role of Design of Experiments in Nanotechnology* (Chimia (Aarau), 2026-05-27) — seen 2026-08-08
> - `TRG-AUTONOMOUS-RESEARCH-AGENT` · *Toward Intelligent Sensing Systems: Non-Equilibrium Materials as Platforms for AI-Enabled Autonomous Discovery* (Sensors (Basel), 2026-05-12) — seen 2026-08-08
> - …and 46 more

**What the state assessment rests on:**
- Agents already execute this repository's compute lanes, monitoring and document generation.
- The arm that has NOT landed is unsupervised multi-month scientific judgement: the repository's own automation record shows a scheduled agent task credited in two documents that has never produced an entry.
- ⭐ EXTERNALLY CALIBRATED 2026-08-27, and it dates the LANDED half precisely. BixBench3 (arXiv:2608.25286v1, 26 Aug 2026, Edison Scientific) graded 13 frontier models on 20 research-study-scale computational-biology tasks, 138 artifacts, 1,794 artifact evaluations: top score 0.48 (GPT 5.6 Sol), Claude Opus 5 — the model this repository runs — 0.406, rising to 0.455 when the three tasks it lost on OUTPUT-FORMAT contract violations are excluded from every model. Its authors state the split this row records: agents 'can begin to execute a specified analysis pipeline – not that they can decide which questions or analyses are worth pursuing.' Reading: research/method-watch-bixbench3-calibration.md

**Unblocks.** routes: RT-METHODS-PAPER, RT-DEGRADER, RT-ASO

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `2029` | moderate | Reliability over months, not hours, is the gap. This repository's own record shows a scheduled agent task credited in two documents that has never produced an entry — long-horizon reliability is genuinely not solved. |
| expected | `2027` | moderate | Agent capability on multi-step technical work has improved rapidly and continuously. The remaining gap is durability and provenance rather than raw capability, and both are being worked on directly. ⚠ SHARPENED 2026-08-27 against BixBench3 (arXiv:2608.25286v1): the gap is NOT only durability and provenance. Artifact pass rate falls to 0.24 at dependency depth 3+ (against 0.44 at depth 2) and to 0.10 on tasks with >100 GB of raw input, so multi-step reliability is a measured raw-capability gap too. The band is unchanged because the paper also shows the top models chaining analyses that defeated the previous generation one year earlier. |
| optimistic | `2026H2` | moderate | Much of this has already landed here: agents run the compute lanes, the monitoring and the document generation. The missing piece is unsupervised scientific judgement over long horizons. ⚠ 2026-08-27: BixBench3's authors draw exactly this line — success on a task carrying an explicit methodological plan means an agent 'can begin to execute a specified analysis pipeline – not that they can decide which questions or analyses are worth pursuing.' |

*Basis:* `evidence_based` · *impact here:* `large` · *last reviewed:* 2026-08-27

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

> ⏳ **5 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-NR4A3-DIRECT-MATTER` · *NR4A3 knockdown ameliorates metabolic dysfunction-associated steatotic liver disease through ATF3 transcriptional repression* (PPR, 2026-06-30) — seen 2026-08-08
> - `TRG-NR4A3-DIRECT-MATTER` · *Nr4a3 Deficiency Disrupts MEK1-ERK1/2-Drp1 Signaling, Driving Adiposity and Glucose Intolerance in Male Mice* (Am J Physiol Endocrinol Metab, 2026-08-09) — seen 2026-08-14
> - `TRG-NR4A3-DIRECT-MATTER` · *Delayed Diagnosis and Multimodality Management of a Primary Myxoid Chondrosarcoma of the Skull Base: A Case Report* (Cureus, 2026-07-20) — seen 2026-08-28
> - `TRG-NR4A3-DIRECT-MATTER` · *NR4A3 mediates Coal Dust Nanoparticle-induced Immunopathogenesis in Rheumatoid Arthritis* (PPR, 2026-08-18) — seen 2026-08-28
> - `TRG-NR4A3-DIRECT-MATTER` · *NR4A3 Fusion-Junction Antisense Gapmers for Extraskeletal Myxoid Chondrosarcoma: Reagents, Test Articles and a Pre-Registrable Knockdown Experiment* (PPR, 2026-08-27) — seen 2026-09-04

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

> ⏳ **21 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-ASO-EFFICACY-ACCESSIBILITY` · *Sequence determinants of efficient exon 44 skipping in Duchenne muscular dystrophy define design principles for steric-blocking antisense oligonucleotides* (PPR, 2026-07-01) — seen 2026-08-08
> - `TRG-ASO-EFFICACY-ACCESSIBILITY` · *FENNEC: Fine-Tuned Ensemble Neural Networks Accelerate Chemically Modified siRNA Design and Screening* (PPR, 2026-06-14) — seen 2026-08-08
> - `TRG-ASO-EFFICACY-ACCESSIBILITY` · *RNAiSpline: A Deep learning model for siRNA efficacy prediction* (PPR, 2026-02-17) — seen 2026-08-08
> - `TRG-ASO-EFFICACY-ACCESSIBILITY` · *Benchmarking Large Language Models for Predicting Therapeutic Antisense Oligonucleotide Efficacy* (PPR, 2026-02-19) — seen 2026-08-08
> - `TRG-ASO-EFFICACY-ACCESSIBILITY` · *OligoGraph: A novel geometric graph-based approach for siRNA efficacy prediction* (PPR, 2026-02-24) — seen 2026-08-08
> - `TRG-ASO-EFFICACY-ACCESSIBILITY` · *Systemic delivery of cationic liposome-mediated siRNA EGFR enhances therapeutic efficacy in a human colorectal cancer model* (PPR, 2026-03-31) — seen 2026-08-08
> - `TRG-ASO-EFFICACY-ACCESSIBILITY` · *A generative-AI framework for target-Specific MicroRNAs towards RNAi-based drug design* (PPR, 2026-05-11) — seen 2026-08-08
> - `TRG-ASO-OFFTARGET-PREDICTOR` · *ASOCompass: Context- and Chemistry-Aware Activity Prediction for Transferable Antisense Oligonucleotide Screening* (PPR, 2026-08-07) — seen 2026-08-14
> - …and 13 more

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

### TECH-CONDENSATE-RESOLUTION — fan-out 1

**A residue-resolution phase-behaviour model — a second independent force field such as Mpipi, or a CALVADOS successor — demonstrated to resolve differences between closely related disordered sequences finer than the Flory-exponent floor the CALVADOS 2 single-chain arm measured; OR a published EMC condensate measurement (droplet formation, FRAP recovery, saturation concentration) reported stratified by 5' fusion partner rather than pooled**

*Category:* `conformational_ensemble` · *state:* `early_signals` · *confidence in that state:* `low`

**Why it matters.** It is the one thing that reopens the shelved CALVADOS single-chain arm, and that arm was closed by RESOLUTION rather than by failure -- it ran to its prespecified standard, both controls passed, and it returned a bounded null that excludes only partner differences larger than its own separation threshold. ⛔ Re-running the same arm with more sampling is NOT this capability and is forbidden by that arm's own prespecification: the reason to reopen is resolution, never repetition. ⚠ Fan-out one is the honest size -- nothing else in the portfolio waits on it, and the route it serves was parked on expected value.

> ⏳ **34 UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly scan matched them on this dependency's own queries. ⚠ **They are unvalidated leads, machine-matched on a title and not read** — the scan deliberately cannot change `current_state`, so nothing below reflects them yet.
>
> - `TRG-CONDENSATE-PARTNER-RESOLUTION` · *Engineering short-sequence elements for condensate-like assemblies by de novo design* (Synth Syst Biotechnol, 2026-07-18) — seen 2026-09-04
> - `TRG-CONDENSATE-PARTNER-RESOLUTION` · *Hydrodynamic simulation of viscoelastic phase separation via coupled Model-H and Oldroyd-B equations* (J Chem Phys, 2026-09-01) — seen 2026-09-04
> - `TRG-CONDENSATE-PARTNER-RESOLUTION` · *Modulation Mechanisms of Transmembrane Domain Flexibility in Amyloid Precursor Protein and Notch: A Coarse-Grained Simulation Study on the Impact of Upper and Lower Leaflet Composition in Liquid-Ordered and Liquid-Disordered Ternary Bilayer Membranes* (Langmuir, 2026-08-01) — seen 2026-09-04
> - `TRG-CONDENSATE-PARTNER-RESOLUTION` · *Liquid-liquid phase separation in a minimal explicit-solvent lattice model mimicking protein solutions* (J Chem Phys, 2026-08-01) — seen 2026-09-04
> - `TRG-CONDENSATE-PARTNER-RESOLUTION` · *Coarse-grained simulation studies of gasdermin self-assembly and pore formation* (Biophys J, 2026-08-04) — seen 2026-09-04
> - `TRG-CONDENSATE-PARTNER-RESOLUTION` · *A Thermodynamic Model on Liquid-Liquid Interfacial Adsorption* (Langmuir, 2026-08-01) — seen 2026-09-04
> - `TRG-CONDENSATE-PARTNER-RESOLUTION` · *Programmable Multiphasic Condensates Formed via Evaporation-Induced Phase Separation of Minimal Peptide Model* (Adv Mater, 2026-07-14) — seen 2026-09-04
> - `TRG-CONDENSATE-PARTNER-RESOLUTION` · *Structural and Thermodynamic Properties of CnEOm Micelles and Monolayers Reproduced by a Coarse-Grained Force Field Based on a Polarizable Water Model* (J Chem Inf Model, 2026-08-01) — seen 2026-09-04
> - …and 26 more

**What the state assessment rests on:**
- The CLASS of model exists and works here: CALVADOS 2 is installed and validated two-sidedly -- the package's own shipped single-IDR example reproduces end to end, and the directional control moves nu by more than the arm's separation threshold. A residue-resolution phase-behaviour force field is a usable instrument today (INS-CALVADOS-SINGLE-CHAIN).
- What has NOT landed is resolution below that instrument's floor: run to the package's shipped protocol with five replicates, CALVADOS 2 single-chain nu separates none of EMC's 5' partner windows from each other, nor any of them from wild-type NR4A3's own disordered region. The floor, the pooled replicate spread and the threshold have one home: research/modalities/emc-condensate-calvados-findings.md.
- UNKNOWN and deliberately not guessed: whether any other residue-resolution force field already resolves finer than that floor between closely related disordered sequences. Nobody here has measured it or searched for it -- TRG-CONDENSATE-PARTNER-RESOLUTION is the query that would find it, and this row is what a hit lands on.
- No published EMC condensate measurement stratified by 5' fusion partner is recorded anywhere in this repository. That is the second disjunct's reason for existing: a pooled measurement cannot answer the partner question however good it is.

**Unblocks.** instruments: INS-CALVADOS-SINGLE-CHAIN

**Forecast.**

| scenario | band | confidence | rationale |
|---|---|---|---|
| conservative | `beyond-2029` | moderate | Neither disjunct is anybody's stated target. The wet-lab half needs somebody to run a partner-stratified condensate measurement in a tumour type this rare; the modelling half needs a force-field generation benchmarked on DISCRIMINATION between similar sequences rather than on agreement with experiment across dissimilar ones. |
| expected | `2028` | low | Coarse-grained IDR force fields are a live and iterating field -- the line this repository uses is already at version 2 -- so a successor arriving is likely. What is uncertain is whether any of them reports the discrimination this needs, which is not the axis such papers usually publish. |
| optimistic | `2027H1` | low | One published benchmark reporting nu discrimination between closely related disordered sequences below this floor satisfies the modelling half immediately, and a single EMC condensate paper that splits its readouts by 5' partner instead of pooling them satisfies the other. |

*Basis:* `speculative` · *impact here:* `marginal` · *last reviewed:* 2026-08-24

**What would move this.** A published benchmark that reports resolution between closely related disordered sequences on this axis at all -- today's papers report agreement with experiment on sequences that are not close, which does not bound the discrimination. ⛔ A re-run of this repository's own arm with more sampling moves nothing.

**⚠ Adoption note.** The modelling half arrives as usable software long before it arrives VALIDATED at this discrimination, and only the second date reopens anything here: the arm was closed by a resolution floor, so a successor force field shipping without a discrimination benchmark leaves the same question open at a new version number.

*Scanned by:* `TRG-CONDENSATE-PARTNER-RESOLUTION`

[← L0](../L0-ecosystem.md)
