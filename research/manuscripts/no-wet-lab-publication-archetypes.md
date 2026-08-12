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
  inhibitors were treated separately. **What survives is narrow and still useful: a single-snapshot
  rescoring margin does not carry a selectivity verdict in this regime** — which is exactly what `V20`
  says, and [`methods-index.md`](../../systems/views/methods-index.md) already grades it `fails`. ⛔ It is
  *consistent with* the repo's verdict, not independent proof of it.
- The failure mode has a documented endgame: a network-pharmacology-plus-docking cancer-mechanism paper
  **retracted** by its publisher on publication-integrity grounds
  ([PMC10412175](https://pmc.ncbi.nlm.nih.gov/articles/PMC10412175/)) — the retraction itself CONFIRMED
  3-0, *and grounded in process integrity rather than a scientific refutation of the docking*.
  ⚠ **Do NOT read the mass retractions as a verdict on this archetype (REFUTED 0-3).** They were a
  paper-mill and compromised-peer-review phenomenon spanning **>8,000 papers across all topics**, and the
  cited paper's own title contains "Experimental Validation", so it was never an in-silico-only study.
- ⭐ **The one credibility architecture that resolves this without owning a lab is the blind prospective
  challenge.** CACHE is modelled on CASP but adds a prospective experimental arm — **the organisers
  assay the compounds participants predict**, and screening data are withheld until the cycle completes,
  so the prediction is genuinely blind
  ([Nat Rev Chem](https://www.nature.com/articles/s41570-022-00363-z); *CONFIRMED 2-1*). CACHE Challenge #1
  was won with an **entirely open-source stack** — GNINA docking plus pharmacophore search, ranked on
  docking score alone — against **an undrugged target with no known ligands** (the LRRK2 WD40 central
  cavity), with 23 groups competing
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
  shinyDepMap, whose **entire contribution is reanalysis of public DepMap data**, accepted by *eLife*
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
  halves)*. *The public-data analysis is portable; the validation that carried it is not.*
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
features, **51 (91.1%) declined** and **20 (35.7%) became undetectable**
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
