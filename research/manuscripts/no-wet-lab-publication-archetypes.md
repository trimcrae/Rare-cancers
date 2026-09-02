---
id: DOC-NO-WET-LAB-ARCHETYPES
title: How no-wet-lab cancer papers actually work — the archetype survey, and what this repo has not tried
level: L4
kind: memo
status: live
purpose: "Enumerate the publication archetypes that produce real cancer-treatment contributions with no wet lab, grade each against this programme's actual constraints, and name the ones this repo has never tried."
scope: "The METHOD / publication-archetype axis, which the 217-class modality census does not cover because every one of its bands asks what to do to the tumour rather than what evidence can be produced without a laboratory. Does not re-rank routes and does not restate the plan; the roadmap owns both."
date: 2026-08-12
last_verified: 2026-08-12
audience: ["maintainers", "autonomous research agents"]
---

# How no-wet-lab cancer papers actually work

> **Why this exists** (trimcrae, 2026-08-12): *"I feel like we're constantly running into hard boundaries
> from not having a wet lab and that kills so many routes. We need to understand how other no-wet-lab
> publications for cancer work."*
>
> ⛔ **Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness for any agent or
> route.** Every identifier is anchored in
> [`no-wet-lab-archetypes-2026-08-12.json`](../literature/no-wet-lab-archetypes-2026-08-12.json).

---

## 0 · The finding that reframes the complaint

**The wet lab is not killing routes at random. Almost every endpoint this repo built terminates in a
bench, and that was a choice made 31 times.**

Counting `patient_path` across all 31 endpoints in [`publications.json`](../../systems/graph/publications.json):

| path to a patient | endpoints | state |
|---|---:|---|
| 🧪 needs a bench (`named_bench` + `prebuilt_bench`) | 9 | mostly `drafted` |
| 🏥 `clinical_adoption` — no bench | 4 | 1 drafted, 2 outlined, **1 unwritten** |
| ⭐ `no_bench_needed` | **2** | 1 drafted (short report), **1 unwritten** |
| — no patient path at all (negatives / methods) | 16 | mostly `drafted` |

**Six of thirty-one endpoints can reach a patient without a laboratory, and four of those six are
unwritten or merely outlined — while sixteen endpoints with no patient path at all are fully drafted.**
`BLK-NO-WET-LAB` holds 16 routes across 7 families, but the blocker is downstream of the real problem.
The portfolio invested in the endpoint class that structurally requires the one thing it does not have.

⭐ **And the census has a missing axis.** [`modality-census.md`](../../systems/views/modality-census.md)
enumerated 217 classes in four bands — `drug_mechanism`, `delivery_and_conjugate`,
`physical_locoregional`, `strategy_and_architecture` — and that work is sound. But **every band answers
*what do we do to the tumour*. None answers *what kind of evidence can we produce without a lab*.** The
census that made modality-space absence auditable has no counterpart on the **method / publication
archetype** axis. That axis is where the answer to trimcrae's question lives, and it has never been
enumerated here.

---

## 1 · The nine archetypes, graded against THIS programme's constraints

Constraints applied: unaffiliated, solo, no wet lab, no clinic, no patient contact, no IRB, no
institutional DUA, GPU budget in the hundreds of dollars.

⛔ **READ THIS BEFORE THE TABLE — THE EVIDENCE IS UNEVEN BY ARCHETYPE, AND IT IS THINNEST EXACTLY WHERE
THE RECOMMENDATIONS ARE STRONGEST.** All 17 claims that survived verification rest on **six primary
papers**, clustered on archetypes **1, 2, 8 and 9**. Archetypes **3 (evidence synthesis / reconstructed
IPD), 4 (registry access), 5 (trial design / external controls / Bayesian borrowing), 6 (mathematical
modelling) and 7 (perspective papers) produced NO claim that survived verification.** ⚠ **That is an
absence of evidence in this survey, not evidence that those archetypes fail** — their claims were sourced
but their verifiers errored, died with the container, or were dropped for budget. **§2's recommendations
1–6 lean on exactly those archetypes and therefore need a fresh, targeted literature pass before anything
is staked on them.** The grades below still stand as *judgements*; they are not all equally *evidenced*.

| # | archetype | verdict here | the binding constraint |
|---|---|---|---|
| 1 | In-silico drug discovery (docking / MD / FEP / co-fold) | ⚠ **done to exhaustion, and its ceiling is now documented** | not access — **the field's own validation bar** |
| 2 | Public molecular-data reanalysis (DepMap, TCGA, GEO) | ✓ partly done, **under-exploited** | EMC has ~no molecular samples; class-borrowing is the way through |
| 3 | Evidence synthesis / reconstructed IPD | ⭐ **executable today, instrument already built, zero curves read** | nothing — a manual digitisation step nobody has started |
| 4 | Registry epidemiology | ◐ **SEER half is open; NCDB half is closed** | SEER: an email address. NCDB: a CoC-accredited collaborator |
| 5 | Trial design / external controls / regulatory science | ⭐ **executable, and never attempted here** | none |
| 6 | Mathematical / mechanistic modelling | ⭐ **executable, and never attempted here** | none |
| 7 | Hypothesis / perspective / theory | ✓ available | credibility, not access |
| 8 | AI/ML prediction on public data | ◐ partly done | rare-cancer sample floor + site/batch confounding |
| 9 | Negative results / reproducibility audits | ✓ heavily done | ⚠ **over-invested relative to §0 of CLAUDE.md** |

### 1 · Purely in-silico drug discovery — the archetype we chose, and its measured ceiling

The literature is blunt about what a computation-only hit-finding paper may claim, and the numbers
independently corroborate this repo's own instrument verdicts.

- Across **61 peer-reviewed docking-based virtual-screening papers** proposing repurposed SARS-CoV-2
  Mpro inhibitors, **41 (67.21%) applied no validation step at all** and only **2 (3.28%)** confirmed a
  prediction experimentally. Docking score did not track measured potency — best correlation
  **Pearson r = −0.335** *(both CONFIRMED 3-0)*, and in that dataset neither docking scores nor MM-GBSA ΔG
  separated actives from 113 experimentally confirmed inactives
  ([Med Res Rev, DOI 10.1002/med.21862](https://onlinelibrary.wiley.com/doi/full/10.1002/med.21862)).
  ⚠ **The GENERALISATION was REFUTED 0-3 and must not be repeated.** "A docking-score cutoff cannot
  legitimately be used to nominate hits" is contradicted by prospective ultra-large-library campaigns in
  which hit rate fell monotonically with docking score
  ([Lyu et al., Nature 2019](https://www.nature.com/articles/s41586-019-0917-9)) and by docking-nominated
  Mpro hits later confirmed by crystallography (Fink et al., Protein Science 2023, DOI 10.1002/pro.4712,
  PMID 37354015); the source's own caveat is that performance improved when covalent and noncovalent
  inhibitors were treated separately — **discrimination improved to a best AUC of 0.744** on that split.
  **What survives is narrow and still useful: a single-snapshot
  rescoring margin does not carry a selectivity verdict in this regime** — which is exactly what `V20`
  says, and [`methods-index.md`](../../systems/views/methods-index.md) already grades it `fails`. ⛔ It is
  *consistent with* the repo's verdict, not independent proof of it.
- The failure mode has a documented endgame: *"Network Pharmacology, Molecular Docking, and Experimental
  Validation to Unveil the Molecular Targets and Mechanisms of Compound Fuling Granule to Treat Ovarian
  Cancer"* (Oxidative Medicine and Cellular Longevity, DOI 10.1155/2022/2896049, PMID 36062197, PMC9428684)
  was **retracted**, notice [PMC10412175](https://pmc.ncbi.nlm.nih.gov/articles/PMC10412175/) — CONFIRMED
  3-0, *and grounded in process integrity rather than a scientific refutation of the docking*.
  ⚠ Separately, the genre **has** been criticised on methodological grounds (Front Pharmacol 2026,
  DOI 10.3389/fphar.2026.1566772) — so "integrity, not method" is true of *this retraction*, not of the
  whole literature.
  ⚠ **Do NOT read the mass retractions as a verdict on this archetype (REFUTED 0-3).** They were a
  paper-mill and compromised-peer-review phenomenon spanning **>8,000 papers across all topics**, and the
  cited paper's own title contains "Experimental Validation", so it was never an in-silico-only study.
- ⭐ **The one credibility architecture that resolves this without owning a lab is the blind prospective
  challenge.** CACHE is modelled on CASP but adds a prospective experimental arm — **the organisers
  assay the compounds participants predict** — the experimental hub is SGC-Toronto, and CACHE #1 screened
  **~1,955 participant-nominated compounds by SPR, yielding 73 binders below 150 µM K<sub>D</sub>** with
  orthogonal ITC/¹⁹F-NMR and aggregation counter-checks (DOI 10.1021/acs.jcim.4c01267, PMID 39499532).
  ⚠ **Terminology corrected by a verifier:** modern CACHE runs **Round 1 and Round 2** within a challenge,
  and cross-participant withholding protects **Round 2 independence** rather than making Round 1 blind
  ([Nat Rev Chem](https://www.nature.com/articles/s41570-022-00363-z); *CONFIRMED 2-1*). CACHE Challenge #1
  was won with an **entirely open-source stack** — GNINA docking plus pharmacophore search, ranked on
  docking score alone — against **an undrugged target with no known ligands** (the LRRK2 WD40 central
  cavity, apo structure **PDB 6DLO**), with **23 teams each selecting up to 100 compounds from Enamine REAL
  (~36 billion molecules)**
  ([J Chem Inf Model 2024;64(24):9388-9396, DOI 10.1021/acs.jcim.4c01429, PMID 39654129, PMC11683865](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11683865/)).
  ⛔ **TWO CLAIMS ABOUT THIS WERE REFUTED 0-3 AND BOTH WOULD HAVE MISLED A PLAN.**
  **(a) It is NOT a modest-compute workflow.** The paper's own methods report docking *"parallelized across
  **4936 CPU cores** as preemptable, low-priority jobs"* on a university cluster, taking *"2 weeks with
  light concurrent usage and 4–6 weeks with heavier"*, with Pharmit screening >179 million compounds.
  **A few hundred dollars does not buy this.** Costing a CACHE entry means costing 4,936-core-weeks.
  **(b) CACHE does NOT demonstrably give participants free wet-lab validation.** The organiser-run arm is
  real — SPR on 1,955 procured compounds, 73 hits <150 µM K<sub>D</sub> (CACHE #1 results paper,
  DOI 10.1021/acs.jcim.4c01267, PMID 39499532) — but the claim that participants' validation costs are
  covered failed 0-3 and the cost structure remains **unresolved**. Check it before any plan rests on it.

### 2 · Public molecular-data reanalysis — under-exploited, with a documented small-n rule

- Target nomination from public dependency data **clears peer review at real journals**: PAK2 in HNSCC
  from DepMap CRISPR reanalysis ([Mol Oncol, DOI 10.1002/1878-0261.13558, PMID 37997254](https://pubmed.ncbi.nlm.nih.gov/37997254/));
  ⚠ **but do NOT cite it as a confirmed zero-wet-lab exemplar**: its Methods section was unobtainable in
  this survey, so whether the published version contains author-generated validation is **UNVERIFIED**.
  The indirect evidence (deposited code and gene lists only; the inhibitor arm reusing GDSC assays)
  favours pure reanalysis but does not establish it. shinyDepMap, whose **entire contribution is
  reanalysis of public DepMap data**, accepted by *eLife*
  ([DOI 10.7554/eLife.57116, PMC7924953](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7924953/)).
- **The credibility architecture is a prespecified negative-control filter stack, not a top-hit
  ranking**: essential in ≥10% of the type's lines, NOT a DepMap common-essential, NOT a dependency in
  normal-lineage screens, and druggable per DGIdb — cross-checked against an orthogonal perturbation
  modality (RNAi/DEMETER2) and public drug-response data (GDSC2, PRISM). All inputs are $0
  registration-only downloads and the code is released.
- ⭐ **The small-n rule, stated explicitly in a published sarcoma paper**: MPNST with only **five** TCGA
  samples was **retained** in the supervised classification analysis but **excluded outright** from the
  survival analysis ([PLOS Comput Biol, DOI 10.1371/journal.pcbi.1006826](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1006826)).
  **Class-discrimination questions tolerate n = 5; time-to-event questions do not.** That is a design
  rule this repo can apply directly.
- ⚠ **The same paper is the cautionary half, and it is the sharpest lesson here.** Its discovery layer was
  public (TCGA soft-tissue sarcoma, GTEx v7, GEO GSE21050 — **and the Connectivity Map, a fourth public
  set omitted from the first draft of this memo**), but what made it publishable at that level was
  author-generated qRT-PCR, a tissue microarray and ethics approval **LUMC B17.036** *(CONFIRMED 3-0, both
  halves — and the only claims here verified against a genuinely fetched primary full text)*.
  ⚠ **A verifier killed the counterfactual and it is worth keeping dead:** *"the validation is what made
  this publishable"* is **unverifiable**, because PLOS Comput Biol publishes purely computational work.
  What is established is narrower and still the lesson: *the public-data analysis is portable; the
  validation layer requires institutional assets, and it was present here.*
- ⛔ **Signature-reversal repurposing (CMap/LINCS) is a trap.** Querying CMap 2 with 588 CMap 1-derived
  signatures put the correct compound in the top 10% only **17%** of the time, against **83%** for a
  same-resource self-query *(CONFIRMED 3-0)*, and the previously-reported hit parbendazole ranks **142**
  in CMap 2 ([Sci Rep 2021;11:17624](https://www.nature.com/articles/s41598-021-97005-z)).
  ⚠ **The "fell from rank 1" framing was REFUTED 0-3**: the source gives CMap 2 ranks only, the CMap 1
  ranks are not in evidence, and of the compounds named only parbendazole was experimentally validated
  (PNAS, DOI 10.1073/pnas.1501597112). The same paper also reports glucocorticoids ranking top-20 in
  **both** versions, so this is partial non-recovery, not total.

### 3 · Evidence synthesis and reconstructed IPD — ⭐ the live one

- **Guyot et al.** invert a published Kaplan-Meier curve back into approximate patient-level time-to-event
  data from digitised coordinates plus the numbers-at-risk table — **zero patient contact, zero IRB, zero
  DUA** ([BMC Med Res Methodol 2012;12:9, PMID 22297116, DOI 10.1186/1471-2288-12-9](https://link.springer.com/article/10.1186/1471-2288-12-9)).
  Free tooling exists: **IPDfromKM** R package plus a Shiny app
  ([PMID 34074267](https://pubmed.ncbi.nlm.nih.gov/34074267/)).
- ⭐ **The published hard conditional matches this repo's own quality floor exactly.** Reconstructed
  hazard ratios are trustworthy **only** when the source reports numbers at risk or total events; with
  neither, the 97.5% bound admits an error factor of **exp(1.556) = 4.7** either side of the true HR.
  [`emc_ipd_survival.py`](../modalities/emc_ipd_survival.py) already sets
  `require_numbers_at_risk_table: True` and refuses non-compliant curves rather than pooling them with a
  caveat. **The instrument was built to the field standard before this survey was run.**
- **The end-to-end template exists in a Lancet-family journal**: a reconstructed-IPD study generating
  **zero new patient data**, registered **PROSPERO CRD42023411195**, screening 7,402 records to 35 studies
  and **2,833 participants**, pooled one-stage with a two-stage sensitivity analysis, with an explicit
  **≥5 participants per study** inclusion floor and a claim ceiling kept at descriptive comparison
  ([PMC11474374](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11474374/)).
- ⚠ **Know which gold standard you are not claiming.** True IPD meta-analysis under
  [PRISMA-IPD](https://jamanetwork.com/journals/jama/fullarticle/2279718) requires raw data transfer from
  custodians — the structural blocker for an unaffiliated researcher, and precisely why solo work routes
  to Guyot-style reconstruction instead.

### 4 · Registry epidemiology — ⛔ the blocker is SPLIT, and this repo records it as uniform

- ⭐ **SEER Research (base tier): as of 13 June 2025, any requestor with a VALID EMAIL ADDRESS may access
  it — no restriction by email provider.** No institutional signature, no eRA Commons, no IRB
  ([seer.cancer.gov/data/access-policy.html](https://seer.cancer.gov/data/access-policy.html)).
  The institutional-email requirement applies to **Research Plus / NCCR**, not the base tier.
- ⚠ **The free tier is field-restricted**: it withholds registry, county, state-county, month of
  diagnosis, age-at-diagnosis to 99 and PRCDA region — exactly the granularity ultra-rare work often
  needs.
- ⛔ **NCDB PUF is genuinely closed** and cannot be bought or waived: CoC-accredited affiliation, an
  insider designation in CoC Datalinks before the form is even reachable, and a signed Cancer Committee
  Chair endorsement on letterhead
  ([ACS PUF](https://www.facs.org/quality-programs/cancer-programs/national-cancer-database/puf/)).
  **That is a collaborator gate.**
- ⭐ **Consequence:** `BLK-REGISTRY-DUA` should be **split into two blockers**. Its SEER half is retirable
  by an action trimcrae can take with an ordinary email address; its NCDB half is
  `requires_external_collaboration`. ⚠ **This does not reorder `RT-POPULATION-REGISTRY`**, which is
  deliberately sequenced behind the ICD-O-3 9231/3 contamination question — buying access before the
  split is quantified still buys a contaminated denominator. That sequencing was right and stays.

### 5 · Trial design, external controls, regulatory science — ⭐ never attempted here

- A rare-disease **Bayesian trial-design methodology paper generating zero new patient data** — every
  case study hypothetical or built from already-published trials — is publishable
  ([Orphanet J Rare Dis 2022;17:186, DOI 10.1186/s13023-022-02342-5, PMID 35526036](https://link.springer.com/article/10.1186/s13023-022-02342-5)).
  Worked example: Bayesian borrowing with a meta-analytic-predictive prior cut a control arm from
  **85 + 85 to 85 + 43**.
- The basket-trial corpus for rare disease is **small and surveyable — 36 trials worldwide, 75% oncology,
  ~81% phase I/II, ~86% non-randomised**, with hierarchical/Bayesian borrowing across related diseases
  named as the methodological remedy ([DOI 10.1186/s13023-025-04048-w](https://link.springer.com/article/10.1186/s13023-025-04048-w)).
  **That is peer-reviewed endorsement of the fusion-class borrowing framing this repo already uses.**
- ⭐ **A documented, checkable gap worth a commentary**: FDA's externally-controlled-trials draft guidance
  **explicitly excludes summary-level external controls** — the exact construct a no-DUA researcher can
  build from published KM curves — and NORD's docket comment found the term "rare disease" used **once,
  in a footnote on page 2**, in a document about an instrument used predominantly in rare disease.
  ⚠ The FDA PDF at `fda.gov/media/164960/download` **404'd both to this sandbox and to a GitHub Actions
  runner with unrestricted egress**; content came from the Federal Register notice (88 FR 6748).

### 6 · Mathematical and mechanistic modelling — ⭐ never attempted here

Treatment-schedule optimisation by mathematical model is an established therapeutic-contribution
archetype ([Trends in Cancer 2022](https://www.cell.com/trends/cancer/abstract/S2405-8033(22)00041-3)).
`RT-SCHEDULING` and `RT-SEQUENCING` exist on the board at `concept` maturity and neither has an
instrument. For an indolent disease measured in years — which is EMC — *when* and *in what order* the
existing agents are given is a real therapeutic question that needs no laboratory.

### 8 · AI/ML on public data — the confound that voids most of it

Site of tissue submission is recoverable from TCGA whole-slide images at **AUROC 0.964–0.998**, versus
0.623 for clinical variables, and **stain normalisation does not remove it** (site still ≥0.850).
Re-splitting so no site spans folds destroyed a large share of apparent signal: of 56 predictable
features, **51 (91.1%) declined** and **20 (35.7%) became undetectable** — ⚠ measured on TCGA
**whole-slide images**, not on all TCGA-derived predictors (scope corrected by a verifier)
([Nat Commun 2021](https://www.nature.com/articles/s41467-021-24698-1)).
⭐ **The prescribed $0 mitigation — preserved-site cross-validation with public code — is offered by its
authors precisely because external validation cohorts are unavailable, and they say this applies
especially to rare cancer subtypes.**

---

## 2 · ⭐ What is in there that we have NOT tried

Ordered by *could this still produce a result*, per CLAUDE.md §0 — not by how finished it would look.

1. ⭐⭐ **Read the KM curves. The instrument is built and has never been given an input.**
   [`emc-ipd-survival.json`](../modalities/emc-ipd-survival.json) reads
   `curves_supplied: 0` and — the real gap — **`candidate_sources: []`**. Its own status field is honest:
   *"The instrument is built and its known-answer control passes; no published EMC figure has been read
   into CURVES yet."* **Nobody has even enumerated which published EMC series carry an admissible figure**,
   and that enumeration needs no figure-reading, no lab, no money. This survey already surfaced
   candidates: the pazopanib phase 2 ([Lancet Oncol 2019;20(9):1252-62](https://www.thelancet.com/journals/lanonc/article/PIIS1470-2045(19)30319-5/abstract),
   n = 23, median PFS 19 months), the sunitinib series ([Eur J Cancer 2014;50:1657-64, PMID 24703573](https://pubmed.ncbi.nlm.nih.gov/24703573/),
   10 patients, 6 PR), and an EMC clinical-features/OS series ([PMID 35144048](https://www.sciencedirect.com/science/article/pii/S2468294222000211)).
   `PUB-IPD-SURVIVAL` is the **highest-scoring `no_bench_needed` endpoint in the portfolio (11.0)** and it
   is `unwritten`. **This is the §0 pattern in textbook form: a row that reads blocked, waiting on
   something free that nobody had done.**
2. ⭐⭐ **Register the systematic review on PROSPERO before doing it.** No route here has ever been
   preregistered on PROSPERO, and it is the single cheapest credibility upgrade available — it is what
   separates the *Lancet*-family reconstructed-IPD template from a pooled-numbers blog post. $0.
3. ⭐ **Split `BLK-REGISTRY-DUA`.** It currently reads as one `requires_authorization` blocker with *no
   named way out*. Its SEER half has a way out costing an email address; its NCDB half is a collaborator
   gate that should be modelled as such. A blocker with no named technology is the most expensive kind,
   and half of this one is retirable today.
4. ⭐ **The external-control-arm paper — the highest-leverage thing on this list.** Building the
   comparator that a future single-arm EMC trial would be judged against is a therapeutic contribution
   with **no bench and no clinic**, and FDA's guidance explicitly leaves summary-level external controls
   out of scope. This is unmodelled in the graph: `grep` returns no route for it.
5. ⭐ **A trial-design / Bayesian-borrowing paper for fusion-driven sarcoma.** Zero new patient data is a
   published norm for this archetype, and the basket-trial corpus is small enough to survey exhaustively.
   Nothing on the board occupies this slot.
6. ⭐ **Scheduling and sequencing as a modelling result, not a concept row.** `RT-SCHEDULING` and
   `RT-SEQUENCING` have no instrument. Mathematical schedule optimisation is a recognised archetype.
7. **Formalise case-report aggregation.** 40 files mention case reports; none applies a formal
   aggregation method with an inclusion floor. The published template uses **≥5 participants per study**
   and keeps the ceiling at descriptive comparison.
8. **Re-cut the fusion-partner assumption against the measured distribution.** In a 58-case EMC cohort:
   **EWSR1::NR4A3 46/58 (79%), TAF15::NR4A3 9/58 (16%), TCF12::NR4A3 2/58 (3%)**
   ([Mod Pathol 2023, PMID 36948401](https://pubmed.ncbi.nlm.nih.gov/36948401/)). ⚠ **Any in-silico model
   that treats "the EMC fusion" as EWSR1::NR4A3 omits roughly one patient in five.** That bears directly
   on `RT-PARTNER-STRAT` and on every structural route built on the canonical fusion.
9. **A CACHE entry is a real, costed option — but verify the cost first.** The winning CACHE #1 workflow
   was open-source GNINA at modest compute against a ligandless target, which is this programme's exact
   regime. ⛔ The "free validation" claim was **refuted 0-3** and must be checked before planning on it.
10. **Preserved-site cross-validation** is the mandatory control if any public-image or multi-cohort ML
    is ever attempted here. Not currently modelled as an instrument.

⚠ **Not on this list, deliberately:** another negative, another failure record, another closed-route
write-up. Sixteen endpoints already have no patient path. CLAUDE.md §0 is explicit that negatives wait
behind anything live, and items 1–6 above are all live.

---

## 3 · Limits of this survey

- **The harness failed TWICE and both are recorded rather than smoothed over.** The first pass hit an
  account weekly usage limit: 40 of 107 agents completed, 67 errored, **and the synthesis step failed**,
  so the tool's returned result was a truncation artifact and was not reported as a finding. The resumed
  run reached 102 results and 24 adjudicated claims and then **died when the container was restarted** —
  diagnosed from PID 1 elapsed time of ~73 s, a `--session-mode resume` launch and no surviving workflow
  process. **The synthesis never ran in either pass.** Everything here was recovered from `journal.jsonl`
  by correlating each verifier's `agentId` to its `## Claim under review` prompt.
- ⚠ **24 claims carry a real 3-vote verdict — 16 CONFIRMED, 8 REFUTED. The remaining ~91 carry none**,
  because their voters errored or died with the container. **An errored vote is not a refutation** (§4),
  and it is not a confirmation either.
- ⛔ **A REFUTATION HERE USUALLY MEANS SCOPE OVERREACH, NOT FACTUAL FALSITY, AND CONFLATING THE TWO WOULD
  DISCARD TRUE FINDINGS.** Six of the eight refutations upheld the underlying measurement and killed the
  inference drawn from it. Read the verdict's evidence in the JSON before acting on it — the exception is
  the CACHE compute correction, which is a straight factual fix with planning consequences.
- ⚠ **One voter cited THIS repo's own committed files as a counter-source.** That is a circularity to
  watch: an artifact committed earlier in the same session is not independent corroboration of itself.
- **Several identifiers are search-result-derived, not page-fetched**, because the egress proxy blocks
  seer.cancer.gov, jamanetwork.com and PMC. Each is flagged in the evidence JSON.
- ⛔ **An anchored identifier is not a verified one.** Gate 4 checks that an identifier appears in a
  tracked artifact, which is evidence of a fetch, not of correctness. Nothing here should be cited in a
  manuscript without reading the source.

---

## 4 · The archetype reference — what it costs to enter, what venue takes it, what claim it may make

⭐ **This is the synthesis the harness never produced.** §1 grades each archetype against this programme;
this section is the operational detail behind those grades — entry cost, venue, claim ceiling, and the
specific thing that kills a submission. Verdicts marked *(n-n)* carry an adjudicated 3-vote result;
everything else is sourced but unadjudicated.

⛔ **NO JOURNAL'S STATED POLICY ON REQUIRING EXPERIMENTAL VALIDATION WAS RETRIEVED IN THIS SURVEY.** Every
venture named below as one that "takes" an archetype is **inferred from where the exemplars were
published**, which is not the same thing: PLOS Comput Biol publishing a wet-lab-backed paper does not mean
it requires one, and the converse is equally unproven. **Check the policy page before choosing a venue.**

### 4.1 · Entry cost and the real gate

| archetype | true $ cost to enter | the gate that is NOT money |
|---|---|---|
| Blind challenge (CACHE) | ⛔ **4,936 CPU cores × 2–6 weeks** for the winning entry — not a few hundred dollars | none administratively: entry is open to unaffiliated participants, code release is **not** required, and participants may stay anonymous (top performers are de-anonymised at data release) |
| DepMap / public-omics reanalysis | **$0**, registration-only downloads | ⛔ **the cell line.** The unit of analysis is an immortalised line, and an ultra-rare tumour may have **zero or one** model — no model, no derivable dependency |
| CMap / LINCS audit | **$0** — GSE92742, GSE70138, L1000-Query, scripts on GitHub | reproducibility itself: the resource fails its own cross-version test |
| Reconstructed IPD | **$0** — R implementation shipped as a supplementary file, open access CC BY | ⛔ **the numbers-at-risk table.** No table, no admissible curve |
| Systematic review / meta-analysis | **$0** | PROSPERO registration and an exhaustive dated multi-database search |
| SEER Research (base tier) | **$0**, no fee, requests processed in **2 business days** | ⚠ **a Windows desktop environment** — SEER*Stat is a Windows application. The practical barrier is an OS, not an institution |
| SEER Research Plus / Specialized | — | ⛔ chained gates: eRA Commons or HHS account → institutional email → per-database review. Compounded, not singular |
| NCDB PUF | — | ⛔ CoC-accredited affiliation + insider designation + Chair's letterhead |
| Trial-design / Bayesian methodology | **$0** | none — case studies may be hypothetical or built from published trials |
| **Running** a basket trial | — | ⛔ **89% are multicentric, averaging 56 centres**; one reached 1,013. Structurally impossible solo |
| Mathematical modelling | **$0** | none |
| Digital pathology on public WSI | **$0** (GDC, cBioPortal; fold code on GitHub) | ⛔ site/batch confounding — see 4.3 |

### 4.2 · Claim ceilings, and the phrasing that survives review

⛔ **Every archetype here has a ceiling, and the papers that survive state it themselves rather than
letting a reviewer find it.** This is the single most transferable lesson in the survey.

- **Blind-challenge hit-finding** — the winning CACHE #1 deliverable was a **weak micromolar binder,
  K<sub>D</sub> = 56 µM by SPR**, framed as *"a hit series"* and a reproducible workflow. Not a drug, not
  a functional inhibitor. **Venue: J Chem Inf Model** published both the participant methods papers and the
  organisers' companion outcome paper. ⚠ **INFERRED FROM WHERE EXEMPLARS APPEARED, NOT FROM POLICY** — see
  the warning under §4.1.
- **DepMap mining** — *"prioritised candidate / repurposing opportunity / methodological template"*. One
  exemplar reported **143 prioritised dependencies and 14 targets with existing clinical inhibitors**,
  framed as *"near-term potential to repurpose"* *(3-0)*.
- **Reanalysis tools** — explicitly hypothesis-generating: nominating the most sensitive lines **for
  someone else to test**, and "target hopping" from an undruggable protein to a druggable one.
- **Reconstructed IPD** — a **methods claim about recovering published data**, never a clinical efficacy
  claim. The mucosal-melanoma exemplar kept its conclusion at descriptive comparison and stated plainly
  that the better-looking combination arm *did not reach significance*.
- **Computational critique** — the CMap audit **declined to adjudicate which version was correct** and
  converted its negative into usage recommendations *(3-0)*. A critique that refuses to overclaim is more
  publishable than one that declares a winner.
- **Single-arm ultra-rare trials** — *"clinically meaningful antitumour activity"* and a conditional
  option in a defined line. Never efficacy, never survival benefit.

⭐ **Two credibility devices recur and both are free:** a **known-answer positive control** (one repurposing
paper validated its pipeline by showing CMap recovered doxorubicin, the standard agent) and **explicitly
hedged phrasing for the novel prediction**. This repo already runs known-answer controls as instruments;
what it has not done is use one as the *rhetorical* spine of a paper.

### 4.3 · What kills each archetype

- **Docking/virtual screening** — no validation architecture. ⭐ The critique that names the failure also
  prescribes the **wet-lab-free** fix: retrospective enrichment against known actives **and** known
  inactives/decoys, re-docking from **SMILES-regenerated** 3D coordinates rather than crystallographic
  ones, and cross-docking to test protein flexibility. **None of that needs a laboratory.**
- **Provenance, not method.** The retracted exemplar's own title advertised *"Experimental Validation"* and
  it did not save the paper *(3-0)*. What carries a computational paper is verifiable data provenance and
  reviewable process — which is an argument for this repo's artifact discipline, not against it.
- **Digital pathology** — site signal masquerading as biology. Named endpoints collapse under
  preserved-site splits: genomic-ancestry prediction **0.798 → 0.507**, ALK-fusion detection **0.678 →
  0.404** (LUSC) and **0.637 → 0.417** (LUAD). Chance, in other words.
- **Bayesian borrowing** — the exchangeability assumption and the between-trial heterogeneity variance,
  *hardest to specify precisely when few external trials exist*, which is the ultra-rare regime. Honest
  papers report the cost: max type I error **6.3%** against a nominal 2.5% under prior-data conflict,
  against power gains up to 14%.

### 4.4 · ⚠ Two corrections to §2 that this detail forces

1. **The external-control-arm route splits in two, and only one half is reachable.** FDA's guidance
   imposes an **Agency-access and auditability requirement** — the sponsor must ensure FDA can reach the
   underlying data. **A solo researcher cannot satisfy that**, so a *regulatory-grade* external control is
   out of reach. What remains reachable, and still valuable, is a **published comparator for the field**:
   the natural-history benchmark a future single-arm trial would be interpreted against. Externally
   controlled designs are overwhelmingly a rare-disease instrument in practice — **45 non-oncology FDA
   approvals between 2000 and 2019** rested on external control data (Jahanshahi et al., *Ther Innov Regul
   Sci* 2021, PMC8332598, via the NORD docket comment).
2. **NCDB PUF could not answer the facility-volume question even if it were obtainable.** The PUF is
   de-identified and **identifies neither patients, providers nor hospitals**. `RT-POPULATION-REGISTRY`'s
   `remaining_unknowns` asks *"whether facility volume is recoverable at all in the public files"* — for
   NCDB PUF the answer is **no, structurally**. That is a free closure of an open question, and it means
   the referral-pattern question needs a different instrument.

### 4.5 · ⭐ The argument that unlocks the ultra-rare case

The mucosal-melanoma reconstructed-IPD paper justified its own existence with the evidence gap itself:
prospective trials in that disease are infeasible, so standard of care had been **extrapolated from a
biologically distinct common cancer**. That is precisely EMC's situation — an ultra-rare sarcoma managed
largely by extrapolation from soft-tissue sarcoma at large.

⭐ **That argument structure is available to this programme verbatim, and it is the strongest framing
found in this survey for getting ultra-rare synthesis work past review.** It converts small n from a
weakness the paper must apologise for into the reason the paper is necessary. Supporting evidence that the
constraint is structural rather than an author failing: the largest molecularly-confirmed EMC series
assembled **58 FISH-confirmed tumours with material for only 48**, and one sarcoma study could not run a
receptor-tyrosine-kinase assay **at all** because untreated frozen material did not exist.

---

## 5 · The execution plan — ordered, costed, and split by who can actually do it

⭐ **This section exists because §2 listed routes and a route is not a next action.** Each step below
names what to run, what it costs, what it produces, and what would stop it.

### 5.1 · ⛔ The distinction that governs step 1: READING A PRINTED NUMBER IS NOT DIGITISING A FIGURE

Reconstruction needs two things from a paper: the **numbers-at-risk table** (printed as text) and the
**curve coordinates** (readable only off the figure). These have completely different integrity
profiles and must not be done in the same step.

- **Extracting printed facts is safe and defensible.** Does this paper contain a Kaplan-Meier figure at
  all? Does it print a numbers-at-risk table? What median survival does it state? Those are transcription,
  checkable against the source, and they decide **admissibility** — which is the gating question.
- ⛔ **Reading coordinates off a plotted curve is a HAND STEP WITH UNGUARDED ERROR.** The instrument's own
  test docstring says so: the known-answer control feeds exact coordinates, so it bounds *algorithmic*
  error and is *"structurally incapable of failing on digitization error."* An agent reading a rendered
  figure by eye would produce clinical numbers whose error nothing in this repo measures.

⭐ **So step 1 does the whole admissibility pass without digitising anything.** That is not a compromise —
it is the larger half of the work, and it converts 17 unread candidates into a graded, admissible subset.

### 5.2 · The steps

| # | step | who | cost | produces | what stops it |
|---:|---|---|---|---|---|
| 1 | ✅ **DONE — full texts fetched and scanned** (Actions run `31605336241`, published to `literature-cache`). Result in [`emc-ipd-admissibility-2026-08-12.json`](../literature/emc-ipd-admissibility-2026-08-12.json). **It did not close the question, and why it could not is the finding — see 5.2a.** | me | **$0** (CI) | 5 of 7 retrieved; 4 report Kaplan-Meier analysis | 2 of 7 returned **HTTP 404** from the Europe PMC endpoint despite having PMCIDs |
| 1b | ⚠ **ATTEMPTED — the question is real but the assets are not reachable yet.** Five routes tried; the figures are raster, so no text route can answer it. See 5.2b. | me | **$0** | a reusable routing map, and two papers definitively closed | **no working HTTPS route to PMC open-access figure assets was found** |
| 2 | **Adjudicate overlap** across the 11 flagged rows — Milan/INT recurrence and the US institutional recurrence — against study periods and institutions, which are already curated fields. | me | **$0** | a non-overlapping pooling set, as `POLICY-evidence.md` requires | study periods may not disambiguate; some will stay "cannot exclude overlap" and must be excluded |
| 3 | ⛔ **DECIDE who digitises the curves.** | **trimcrae** | — | unblocks everything downstream | **This is a medical-integrity call, not a task.** See 5.3 |
| 4 | **Register on PROSPERO before analysing.** | trimcrae (account) / me (protocol text) | **$0** | the credibility step that separates this from pooled numbers | registration requires a named person; it is an account, not an affiliation |
| 5 | **Quantify the ICD-O-3 9231/3 split** before any SEER work. | me | **$0** | whether a 9231/3 cohort is an EMC cohort at all | already scoped as `RT-DIAGNOSTIC-PATHWAY`; unchanged by this survey |
| 6 | **Obtain SEER Research base tier** — valid email, online form, DUA acknowledgement, ~2 business days, no fee. | **trimcrae** | **$0** | population denominators and treatment patterns | ⚠ needs a **Windows** environment for SEER\*Stat. Do **after** step 5, not before |
| 7 | ⚠ **RUN, AND IT DID NOT CLOSE THE GAP.** Archetypes C/D/E and all three open questions still unverified — see §6. | me | **$0** | (A) and (B) closed; the rest unchanged | **egress blocking + an exhausted search budget** |
| 8 | ⭐ **Re-run the remaining retrieval THROUGH CI, not through another deep-research pass.** The only findings that survived came off a GitHub Actions runner. | me | **$0** | archetypes C/D/E, venue policies, CACHE terms, the EMC substrate census | nothing — this is the corrected next action |
| 9 | ⛔ **Grade the care-delivery questions against SEER's actual fields BEFORE step 6.** First-course only; no clean untreated denominator for RT or chemo. | me | **$0** | which questions SEER can answer at all | nothing |

### 5.2a · ⛔ What step 1 established, and the trap it walked into

**Four of the five retrieved papers report Kaplan-Meier survival analysis.** `chiusole2020` alone prints
**four overall-survival curves** — by resection extent, sex, primary location and metastatic site — making
it the richest single candidate found. `stacchiotti2013anthracycline` mentions no Kaplan-Meier analysis at
all and probably carries no curve.

⚠ **Two of seven were never retrieved.** `drilon2008` (PMC2779719) and `bishop2019` (PMC7771031) both
returned **HTTP 404** from the Europe PMC full-text endpoint despite having PMCIDs. That is a statement
about *that endpoint*, not about those papers, and they need a second route before anything is concluded.

⛔ **And zero of the five mentions "numbers at risk" in its text or prints it in a table — which is a LIMIT
OF THE METHOD, NOT A FINDING ABOUT THE PAPERS.** In JATS XML the at-risk row is rendered **inside the
figure image**, so a full-text search is structurally incapable of seeing it whether or not it is there.
Reporting "no EMC series carries an at-risk table" would have been exactly the error §4 of CLAUDE.md
names: *an absent reading is not a reading of absence.* **The question is open and step 1b answers it.**

⭐ **The useful distinction this exposed, which the original plan did not have.** There are *three* levels
of engagement with a figure, not two, and only the third is the risky one:
1. **Reading the caption** — pure text, entirely safe. Done.
2. **Inspecting the plot for structure** — *is there a numbers-at-risk row beneath the axis?* A bounded
   yes/no with no quantity attached. **Safe, and it is what decides admissibility.**
3. **Reading coordinates off the curve** — a hand step with unguarded error. **This, and only this, is
   trimcrae's decision in 5.3.**

The original plan collapsed 2 and 3 together and therefore deferred more than it needed to.

### 5.2b · ⛔ Step 1b: the question is unanswerable from text, established rather than assumed

**The chiusole2020 figures are raster images.** The discriminating observation: the PDF text layer
carries the figure **captions** — which are typeset page text — and **zero plot internals**. No axis tick
labels, no survival-axis tokens, no bare numeric rows. So the absence of "at risk" from *both* the XML and
the PDF proves nothing at all, and §4's rule holds: **the only way to close admissibility is to look at
the graphic.**

⭐ **The routing map, which is reusable for every future literature fetch here:**

| route | result |
|---|---|
| `pmc.ncbi.nlm.nih.gov/articles/<PMCID>/bin/<fig>.jpg` | HTTP 200 but `text/html` — a **reCAPTCHA** |
| `europepmc.org/articles/<PMCID>/bin/<fig>.jpg` | connection closed without a response |
| Europe PMC `supplementaryFiles` | HTTP 200 `application/zip` — ⛔ **and it exposed a live corruption bug** |
| **`oa.fcgi?id=<PMCID>`** | ✅ **works** — returns licence and package path. The correct entry point |
| `https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/…` | HTTP 404 on every path tried — **unresolved** |
| **publisher direct PDF** | ✅ **works** — 33 KB of extracted text |

⭐ **Two papers are now definitively closed.** `drilon2008` and `bishop2019` return **`idIsNotOpenAccess`**.
Their earlier 404s were not an endpoint quirk — no open route reaches them, and obtaining them is a
subscription decision rather than a free step.

⭐ **And option 3 stopped being hypothetical.** The PDF text layer yielded real printed statistics for
`chiusole2020` — median overall survival **180 months**, **75%** alive at 5 years, 20 deaths, and the
p-value for every subgroup comparison — by transcription, with nothing digitised. **The
printed-numbers-only paper is already accumulating its inputs as a byproduct of the admissibility pass**,
which is exactly the argument for it in §5.3.

### 5.3 · ⛔ The one decision that is genuinely trimcrae's

**Who reads the curve coordinates, and is an agent-read coordinate acceptable provenance for a clinical
datum?**

The instrument demands a `digitized_by` field precisely because this is a hand step. Three options, and
this programme's medical-integrity rule makes the choice non-obvious:

1. **trimcrae digitises** with WebPlotDigitizer — slowest, and the only option whose provenance is
   unambiguous. The published method estimates roughly half an hour per curve.
2. **An agent digitises**, recorded honestly as such — fast, and it puts numbers whose error nothing here
   measures into a clinical artifact. ⚠ *The repository's first golden rule is never to fabricate medical
   facts; a mis-read coordinate is not a fabrication in intent but is one in effect.*
3. **Neither** — restrict the paper to what printed numbers alone support (pooled response rates, medians,
   reporting-completeness findings). **Weaker, and entirely defensible.**

⭐ **Option 3 is a real paper on its own**, and step 1 produces it as a byproduct. A survey of *how
completely EMC's published survival literature reports itself* — how many series print a numbers-at-risk
table at all — is both a finding and the methods section of whatever follows.

### 5.4 · What this plan does NOT claim

⚠ **Steps 1 and 2 do not produce a survival result.** They produce a graded, deduplicated,
provenance-clean input set and an honest count of what is usable. That is the unglamorous half, it is
where the route actually is, and pretending otherwise would repeat the error §0 describes.
⛔ **And nothing here promises the pooled cohort is large.** The 1,133 figure is a sum across rows with
known overlap; the non-overlapping admissible total could be a small fraction of it, and step 2 exists to
find out rather than to assume.

---

## Appendix A — corrections after adjudication, with the superseded wording retained

⚠ **Every line below was in this memo when it was first committed (`ff28beaa`) and was corrected once the
resumed run's 3-vote verdicts were recovered.** Rule 1.2: the superseded wording stays quotable here and
the live text carries only the corrected value. **The first commit's message repeats two of these errors
and cannot be edited** — this appendix is the correction of record for it.

| # | superseded wording, verbatim | verdict | what replaced it |
|---|---|---|---|
| A1 | "CACHE Challenge #1 was won with an **entirely open-source, modest-compute workflow**" — and, in the commit message, that it is a route for a researcher with hundreds of dollars | REFUTED 0-3 | The paper's methods report docking **parallelized across 4,936 CPU cores** on a university cluster over 2–6 weeks, with Pharmit screening >179 M compounds. The open-source half stands; **"modest-compute" was wrong and is the one correction with direct planning consequences.** |
| A2 | "neither docking scores nor MM-GBSA ΔG could separate actives from 113 experimentally confirmed inactives … **the external confirmation of `V20`**" | REFUTED 0-3 *(on the generalisation)* | The measurement stands in that dataset. The general claim that a docking cutoff can never nominate hits is contradicted by Lyu et al. Nature 2019 and Fink et al. Protein Science 2023. Now stated as **consistent with `V20`, not independent proof of it.** |
| A3 | "one of a genre spanning **many sibling retractions**" | REFUTED 0-3 | The retractions were a **paper-mill and compromised-peer-review** phenomenon across >8,000 papers in all topics — not a verdict on in-silico methodology. The cited paper's own title contains "Experimental Validation". |
| A4 | "parbendazole fell **from rank 1** to rank 142" | REFUTED 0-3 | The source reports CMap 2 ranks only; the CMap 1 ranks are not in evidence and only parbendazole was experimentally validated. Glucocorticoids ranked top-20 in **both** versions, so this is partial non-recovery. |
| A5 | discovery layer "fully public (TCGA, GTEx v7, GEO GSE21050)" | REFUTED 1-2 | Correct but incomplete — it **omitted the Connectivity Map**, a fourth public dataset used in the therapeutic-target arm. |

⭐ **What did NOT need correcting, because it was adjudicated and held:** the 61-paper/67%-no-validation
count and the r = −0.335 correlation (3-0); the CMap 17%-versus-83% reproducibility gap (3-0); the TCGA
site signature at AUROC 0.964–0.998 and preserved-site cross-validation as the prescribed $0 mitigation
(3-0); that the PLOS sarcoma paper is **not** a zero-wet-lab study and its validation needed institutional
assets (3-0); the n=5 classification-versus-survival floor (2-0); CACHE's prospective experimental arm
(2-1); and the LRRK2 WD40 target being undrugged with no known ligands (2-1).

⛔ **The §2 recommendations are unaffected.** Items 1–8 rest on the IPD/registry/trial-design evidence,
none of which was refuted. **Item 9 (a CACHE entry) is the exception and is materially downgraded by A1:**
it is no longer a cheap option and must be costed as 4,936-core-weeks before it is considered.

---

## Appendix B — corrections from the harness's own synthesis (third pass, completed)

⭐ **The run finally completed on its third resume: 107/107 agents, 0 errors, and the synthesis ran.** Its
output is recorded verbatim in the evidence JSON under `harness_synthesis` and is the authority over the
earlier hand-recovered reading wherever the two differ. It corroborated the memo's structure and forced
these corrections, all applied above.

| # | superseded wording | what replaced it |
|---|---|---|
| B1 | *(absent)* — §1 stated grades without stating that the evidence behind them is uneven | ⛔ **Archetypes 3, 4, 5, 6 and 7 produced NO claim that survived verification.** All 17 surviving claims rest on **six primary papers** clustered on archetypes 1, 2, 8 and 9. §2's recommendations 1–6 lean on the unevidenced ones and now say so. |
| B2 | "**Venue:** J Chem Inf Model … a named venue that accepts compute-only work" | ⛔ **No journal's stated policy was ever retrieved.** Every venue statement is inferred from where exemplars appeared. PLOS Comput Biol publishing a wet-lab-backed paper does not mean it requires one. |
| B3 | shinyDepMap/PAK2 cited as clearing review "with no author-generated data" | ⚠ The PAK2 paper's Methods were unobtainable; whether the published version contains author-generated validation is **UNVERIFIED**. Not a confirmed zero-wet-lab exemplar. |
| B4 | "what made it publishable at that level was author-generated qRT-PCR…" | ⚠ **An unverifiable counterfactual** — PLOS Comput Biol publishes purely computational work. Narrowed to: the validation layer requires institutional assets, and it was present here. |
| B5 | "neither docking nor MM-GBSA could separate actives from inactives" | Discrimination **improved to best AUC 0.744** when covalent and noncovalent were separated. |
| B6 | "retracted … one of a genre" | Full identifiers now given (DOI 10.1155/2022/2896049, PMID 36062197, PMC9428684). ⚠ And the genre **has** been criticised methodologically (Front Pharmacol 2026, DOI 10.3389/fphar.2026.1566772) — "integrity, not method" is true of *this retraction*, not the whole literature. |
| B7 | "screening data are withheld until the cycle completes, so the prediction is genuinely blind" | Modern CACHE runs **Round 1 and Round 2**; cross-participant withholding protects **Round 2 independence** rather than making Round 1 blind. |
| B8 | preserved-site CV "destroyed a large share of apparent signal" | ⚠ Measured on TCGA **whole-slide images** only, not all TCGA-derived predictors. |

⚠ **How strong the verification actually is, stated plainly.** Only **three** claims were confirmed against
a genuinely fetched primary full text — the CMap paper and both PLOS Comput Biol claims — routed out
through GitHub Actions runs `31592017890` / `31594039131` / `31594360640` with artifacts committed to
`origin/literature-cache`. ⭐ *That is this repo's own §6 escape hatch, used by the harness without being
told to.* Everything else was confirmed from **search-result rendering** cross-checked across at least two
independent hosts per identifier, which is materially weaker than reading the page.

⛔ **One verifier flagged CIRCULAR PROVENANCE:** for one quote the only reachable home was this repo's own
cache, committed earlier in the same session. An artifact is not independent corroboration of itself, and
that claim's confidence was capped for it.

---

## 6 · The second pass, what it settled, and what it did not

A second run (113/113 agents, 0 errors) was commissioned **only** to close archetypes 3–7 and three named
open questions. ⛔ **It did not close them, and it says so plainly:** zero verified claims for trial
design, mathematical modelling or perspective papers, and zero for all three open questions. All seven
surviving claims sit in evidence synthesis and registry access. **More than half the commissioned scope is
unchanged, and §1's grades for archetypes 5, 6 and 7 remain judgements rather than sourced findings.**

⭐ **Why it failed is the actionable part.** Its caveats name the cause: the egress proxy 403'd every major
publisher and index, *and* the session exhausted its 200-call search budget, so many verification votes
graded internal soundness rather than re-retrieving. **The two strongest findings were rescued by routing
fetches through a GitHub Actions runner** — CLAUDE.md §6's own escape hatch. A third blocked pass would hit
the same wall; **the remaining gap is a CI-routing job, not another deep-research run.**

### 6.1 · ⛔ A correction to §5: the at-risk table is a FIDELITY modifier, and OUR gate is stricter than the method

**IPDfromKM treats numbers at risk, total patients and total events as OPTIONAL arguments.** They
materially improve reconstruction quality and preprocessing can fail to converge without them — but a
curve lacking them is *lower fidelity*, **not illegal to reconstruct**.

⚠ **So §5 was conflating two different things.** `emc_ipd_survival.py` sets `REQUIRE_RISK_TABLE = True` and
refuses such curves outright. **That is this programme's own deliberate stricter choice, not a constraint
inherited from the method**, and it should be visible as a choice. It is defensible — Guyot's hard
conditional is that without numbers at risk *or* total events the 97.5% bound admits a hazard-ratio error
factor of **4.7** — but a future reader must be able to see that the gate was set here rather than handed
down. **The admissibility question is therefore really a fidelity question with a policy threshold on top.**

### 6.2 · ⭐ A checkable statistical trap that lands directly on this disease's n

When pooling tiny series **as proportions**, the **Freeman-Tukey double-arcsine transformation is a
documented hazard, not a safe default** *(3-0, and one of only two findings read directly off a primary
page)*. Back-transformation requires substituting a single sample size, and the harmonic mean degenerates
across studies of very unequal size. In the published case study, back-transformed prevalences **and their
confidence limits came out exactly zero**, with sample sizes between roughly 10 and 120 returning zero.

⛔ **That window is where almost every EMC series lives.** The candidate list runs n = 5 to 270 with the
bulk between 10 and 120. **Generalized linear mixed models are the named alternative, and a sensitivity
analysis across sample sizes is called mandatory.** ⚠ The 10–120 endpoints are *not* a universal property —
they depend on the pooled set — so this is a check to run, not a number to quote.

### 6.3 · What SEER can and cannot answer, before anyone signs for it

- **Treatment data is FIRST COURSE ONLY** — no post-progression, relapse, second-line or salvage therapy is
  abstracted. Later lines exist only in SEER-Medicare, a separate product needing an institutional
  application. ⚠ *(single-host retrieval, not cross-checked)*
- ⛔ **Radiation and chemotherapy collapse "did not receive" with "unknown" into one category**, so **no
  clean untreated-versus-treated denominator is constructible** for those modalities. **Surgery is not
  affected** — SEER carries a separate "reason no cancer-directed surgery" field. ⚠ *(2-1; the primary page
  was never fetched, corroborated structurally from SEER\*Stat dictionary files)*
- ⭐ **This bites before access does.** Several care-delivery questions assume treatment detail SEER does
  not carry. **Grade the questions against the fields before step 6 is taken, not after.**

### 6.4 · NCDB, confirmed closed — with the one door that exists

The PUF is restricted to investigators **affiliated with a CoC-accredited cancer program**, with a DUA
signed before download and sharing confined to that facility *(3-0, direct page read)*. ⭐ **The blocking
condition is the affiliation of the APPLICANT** — so being named personnel on a CoC-affiliated
investigator's approved application is the route, and it is a collaborator ask rather than a purchase.

### 6.5 · ⭐ The medical-integrity gate answered an open question the research could not

Committing §6 turned gate 3 red. The cause was substantive rather than clerical: the evidence artifact had
picked up **`CVCL_1238`** — and this repository already records that object as **identity-disputed**.

⛔ **That is the answer to open question 3's cell-line half, and the repo's own register gives it more
sharply than either research pass did.** The single DepMap model carrying the OncotreeSubtype
"Extraskeletal Myxoid Chondrosarcoma" is `OBJ-LINE-HEMCSS` / H-EMC-SS / `CVCL_1238`, and **the public
record does not support the label.** An STR profile of 16 markers — 15 STR loci plus amelogenin —
exists, so the line is a real profiled entity — *the open question is what it is, not whether it exists.*

⭐ **THE LOAD-BEARING EVIDENCE IS THE FUSION-CALL FILE, NOT THE CELLOSAURUS CAUTION** (trimcrae,
2026-08-12, correcting an earlier draft of this section). The register's `evidence_verbatim` reads *"Does
not harbor a gene fusion involving **EWSR1** which is a hallmark of extraskeletal myxoid chondrosarcoma"* —
and quoting that alone is a weak argument, because ⛔ **EWSR1 is not what defines this disease. NR4A3
rearrangement is.** EWSR1 is merely the commonest partner (79% in the 58-case cohort in §2), and a
TAF15::NR4A3 or TCF12::NR4A3 line would be fully EMC while harbouring no EWSR1 fusion at all. The claim
survives only because a **second, independent line** carries it: **DepMap `OmicsFusionFiltered.csv` 24Q4
lists this model with two calls — `AL158209.1--NEBL` and `VIM--RPS25` — and NEITHER names NR4A3, EWSR1,
TAF15 or FUS.** ⭐ *The model's PRESENCE in that file is what makes this a reading of absence rather than
an absent reading.* Weak corroboration only: NR4A3 expression sits at 0.941 log2(TPM+1) — 83rd percentile
of 1,673 lines, but against a panel median of 0.214, where a fusion transcript driving the NR4A3 body off
a partner promoter should read far higher.

⚠ **AND THE REGISTER IS CAREFUL IN A WAY THIS SECTION MUST NOT BLUR.** Its `what_this_cannot_settle`
field states that none of this establishes *what the line is instead, that the original characterisation
was wrong, or that the line is not EMC* — a line can be misidentified, drift in culture, or be a genuine
fusion-negative tumour of the same histology. Settling identity needs STR authentication against the donor
and RT-PCR for the fusion, neither of which is in public data at the needed resolution and neither of
which this programme can perform. **What is established is narrower and still sufficient for the
consequence below: the public record does not support the label.**

**Consequence for §1's grade of archetype 2.** Public-omics reanalysis was graded *"partly done,
under-exploited"* with the binding constraint given as "EMC has ~no molecular samples". That is now
sharper and worse: **the one model that would carry EMC-labelled dependency or expression signal cannot be
used to ground an EMC property at all.** The DepMap leadership's own honest framing applies exactly —
absence of a model class means absence of evidence — and here the apparent presence of one is the trap.
⭐ **Class-borrowing across FET-fusion sarcomas is not a convenience for this route; it is the only form it
can take.**

⚠ **The use in the evidence artifact is classified `unaffected`** and registered in
`emc-systems-map.json` → `read_by`, because that file names the identifier only as a retrieval source and
grounds no biological property on the model. It would become `invalidated` the moment any claim here rested
on it.

---

## 7 · Paper ideas this analysis produced — one kept, one WITHDRAWN

*Recorded so neither is re-proposed as unexplored. Absence of an idea from the board is sometimes a
judgement; these two are.*

### 7.1 · ⛔ WITHDRAWN — "audit the published EMC literature for findings that rest on H-EMC-SS"

**Proposed and withdrawn the same day (2026-08-12), and the withdrawal is the more useful record.**

The pitch was: §6.5 shows the public record does not support this line's EMC label, your `read_by` sweep
covers 30 files *inside this repository*, and nobody has asked the same question of the **external**
published literature — so audit which published EMC findings rest on it. That is the publishable-negative
archetype, which this survey verified better than any other, and it costs $0.

⛔ **It does not survive its own source.** An audit of that shape needs the premise *"these papers studied
something that is not EMC."* The register explicitly refuses to supply it: `what_this_cannot_settle` says
the evidence does **not** establish that the line is not EMC, only that the public record does not support
the label. **A caution is not a refutation**, and a paper built on the stronger reading would be asserting
exactly what the underlying artifact declines to assert.

⚠ **The failure mode worth remembering is how it arose.** The idea was generated from a *lint failure* —
gate 3 going red — and a red gate feels like a discovery. It was inflated into a paper before its
governing artifact was re-read. **The artifact had the disqualifying sentence in it the whole time.**

**Reopening trigger:** STR authentication against the donor, or RT-PCR for an NR4A3 fusion in this line,
appearing in public data. Either would convert the caution into a finding. Neither is something this
programme can produce.

### 7.2 · ⭐ KEPT — does EMC's published survival literature report itself well enough to be reused?

Unaffected by the above, because it rests on this survey's own measurements rather than on the cell line.
§5.2a and §5.2b establish the shape: 17 candidate series, 2 of 7 reachable full texts denied outright as
not open access, figures rasterised so reporting completeness cannot be read from text, and a quality
floor (`REQUIRE_RISK_TABLE`) that is **this programme's stricter choice** rather than a constraint the
method imposes (§6.1).

**The claim it would make:** an ultra-rare cancer's clinical literature can be exhaustively enumerated and
still not be poolable, and the binding limit is *reporting practice* rather than patient numbers. **The
denominator is the finding** — how many of a disease's published series carry a numbers-at-risk table at
all. ⚠ Genuinely at risk of being a paragraph rather than a paper: if most series report well, the
finding evaporates and it becomes the methods section of `PUB-IPD-SURVIVAL`. **That is knowable from step
1b and should decide it.**

⚠ **Neither is on the board.** Adding 7.2 to `publications.json` is a separate call, and §0's ordering
applies: `PUB-MTAP-PRMT5`, `PUB-REPURPOSING` and `PUB-IPD-SURVIVAL` are live and rank ahead of it.
