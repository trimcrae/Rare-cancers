---
id: DOC-SHARED-VS-INDIVIDUALIZED-NEOANTIGEN
title: "Shared versus individualized neoantigen vaccines: what the 2026 readouts actually support, and what they mean for the EWSR1::NR4A3 junction route"
level: L4
kind: memo
status: live
canonical_for: [shared-vs-individualized-neoantigen-grading]
purpose: >
  Grade the shared/off-the-shelf versus individualized neoantigen-vaccine question against
  primary sources, separate what the two 2026 readouts establish from what they are confounded
  by, and state the consequence for this repository's EWSR1::NR4A3 junction-vaccine route.
  Produces a re-grade PROMPT, not a re-grade.
scope: >
  Evidence synthesis only. No wet-laboratory work, no new computation, no new prediction. No
  efficacy, safety, tolerability, therapeutic-window or clinical-readiness claim is made or
  implied for any agent or combination this repository proposes.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-08-24
last_verified: 2026-08-24
---
# Shared versus individualized neoantigen vaccines: what the 2026 readouts actually support

**Written 2026-08-24 in response to two 2026 datapoints that had been sitting in this repository at
press level and had never been graded against the junction-vaccine route:** the Merck/Moderna
INTerpath-001 announcement (2026-08-19, an *individualized* therapy reported positive) and the Elicio
AMPLIFY-7P announcement (2026-06-15, a *shared* peptide vaccine reported to have missed). Both were
carried as `[PRESS]` rows in
[`method-watch-backfill-2026-08.md`](../../method-watch-backfill-2026-08.md) §3, where the second is
annotated as "the comparison this route most needs to take seriously". This memo is that comparison.

---

## 0 · Evidence grades used below

Every claim in this memo carries one of four grades. **A press report is a LEAD, NOT EVIDENCE, and is
never citable as a medical fact** (CLAUDE.md §7).

| grade | meaning |
|---|---|
| **`[PRIMARY]`** | Traced to a peer-reviewed publication with an identifier retrieved by the CI literature fetch, not written from recollection. |
| **`[REGISTRY]`** | Traced to the ClinicalTrials.gov API v2 record, retrieved by the CI fetch on 2026-08-24 (`literature/neoantigen-press-primary-sources/` on `literature-cache`). A registry record establishes *design*, not *result*. |
| **`[PRESS]`** | A company announcement. Establishes that the announcement was made, on that date, in those words. Establishes nothing about the result. |
| **`[REPO]`** | This repository's own committed artifact or computation. Predicted, not measured. |

`[PRIMARY]` and `[REGISTRY]` correspond to the backfill memo's `[VERIFIED]`; `[PRESS]` is the same
grade it uses.

---

## 1 · Bottom line

1. **"Shared versus individualized" is not the axis on which the two 2026 cases differ.** They differ
   on at least seven axes at once — disease, backbone, comparator, platform, antigen biology, phase and
   size — and the registry records make the backbone difference explicit: INTerpath-001's control arm is
   **placebo plus pembrolizumab**, AMPLIFY-7P's Phase 2 comparator is **observation** `[REGISTRY]`. One
   trial asked whether a vaccine adds to a checkpoint inhibitor, in 1,089 or more patients, in the most
   checkpoint-responsive solid tumour; the other asked whether a vaccine alone beats nothing, in 144
   patients, in one of the least. Two trials cannot separate seven axes, and nothing in this memo should
   be read as a trend.
2. **Neither 2026 result is evidence yet.** Both are company announcements, and **neither has a
   peer-reviewed publication among the records retrieved for this memo** `[PRESS]`. INTerpath-001
   disclosed no effect size at all, and its release says data will be presented at a future medical
   meeting. AMPLIFY-7P disclosed
   no intent-to-treat effect size either — every efficacy number in its release is post-hoc, landmark or a
   responder split, and it also reports a baseline prognostic imbalance against its own treated arm. What
   each announcement *is* evidence of is that the announcement was made.
3. **The published randomized evidence for individualized neoantigen therapy is thinner than the
   headline.** The only randomized publication of this agent among the records retrieved here,
   KEYNOTE-942, reported a recurrence-free-survival hazard ratio of 0.561 (95% CI 0.309–1.017) at a
   two-sided p of 0.053 — its own primary endpoint did not reach the conventional cut `[PRIMARY]`. The
   5-year update is explicitly descriptive `[PRIMARY]`.
4. **Shared neoantigen vaccines are not failing for want of immunogenicity.** The shared mKRAS
   amphiphile vaccine raised direct *ex vivo* mKRAS-specific T-cell responses in 21 of 25 patients in its
   phase 1 `[PRIMARY]`. Where a shared multi-epitope vaccine did fail cleanly, in advanced solid tumours,
   the published mechanism was **immunodominance** — T-cell responses biased toward TP53 neoantigens
   encoded in the vaccine and away from the KRAS neoantigens the patients' tumours actually expressed —
   not sharedness as such `[PRIMARY]`.
5. **The relevant comparator class for an EWSR1::NR4A3 junction vaccine is neither of the 2026 trials.**
   It is the shared *fusion-breakpoint* peptide vaccine: two synovial-sarcoma SYT-SSX junction trials
   from 2005 and 2012, and one 2026 EWSR1::FLI1 Ewing sarcoma case `[PRIMARY]`. That literature is small,
   immunogenic in a minority, adjuvant-dependent, and has never demonstrated efficacy.
6. **This does not change the route's grade, and §6 says why.** RT-VACCINE is parked on
   `BLK-ANTIGEN-COLD` — immunogenicity of a self-adjacent junction in a cold tumour — and neither 2026
   datapoint bears on that blocker. What the two cases *do* bear on is the premise of
   `RT-VACCINE-COMBINATION`, which is the open route in this family, and §6 raises that as a re-grade
   prompt for trimcrae rather than acting on it.

---

## 2 · The evidence ledger

### 2.1 Individualized

| claim | grade | source |
|---|---|---|
| INTerpath-001 is a Phase 3, randomized, double-blind, placebo- and active-comparator-controlled study of adjuvant V940 (mRNA-4157) plus pembrolizumab **versus placebo plus pembrolizumab** in high-risk stage II–IV melanoma; lead sponsor Merck Sharp & Dohme; status ACTIVE_NOT_RECRUITING; primary outcome recurrence-free survival; registry enrollment count 1,089. | `[REGISTRY]` | NCT05933577 |
| Merck and Moderna announced on 19 August 2026 that INTerpath-001 met its primary endpoint of RFS and a key secondary endpoint of DMFS at a pre-specified interim analysis, that the study continues for overall survival, that the enrolled population was 1,137 patients randomized 2:1, and that data will be presented at a future medical meeting. | `[PRESS]` | Merck release, 19 Aug 2026, retrieved to `literature/interpath-001-announcement-2026-08-22/` and `literature/neoantigen-press-primary-sources/` |
| **No effect size, hazard ratio, confidence interval, event count or absolute RFS difference was disclosed for INTerpath-001.** | `[PRESS]` — absence in the retrieved release text | as above |
| Intismeran autogene is an mRNA-based individualized therapy encoding **up to 34 patient-specific neoantigens**, designed from each patient's own tumour sequencing. | `[PRIMARY]` for the platform description | PMID 39115419, *Cancer Discov* 2024;14(11):2209–2223, doi:10.1158/2159-8290.CD-24-0158 |
| KEYNOTE-942 (phase 2b, open-label, n=157, 2:1): RFS hazard ratio 0.561 (95% CI 0.309–1.017), two-sided **p=0.053**; recurrence or death in 24/107 versus 20/50; 18-month RFS 79% versus 62%; grade ≥3 treatment-related adverse events 25% versus 18%. | `[PRIMARY]` | PMID 38246194, *Lancet* 2024;403(10427):632–644, doi:10.1016/S0140-6736(23)02268-7; NCT03897881 |
| KEYNOTE-942 5-year update, **explicitly descriptive analyses**, median planned follow-up 60.3 months: RFS HR 0.510 (95% CI 0.294–0.887), DMFS HR 0.411 (0.200–0.843), OS HR 0.471 (0.165–1.345). | `[PRIMARY]` | PMID 42223134, *J Clin Oncol* 2026, doi:10.1200/JCO-26-00835 |
| A second individualized platform, autogene cevumeran (up to 20 neoantigens), elicited neoantigen-specific responses in 71% of patients in a phase 1 in pretreated patients with advanced solid tumours (n=30 monotherapy, n=183 in combination with atezolizumab); clinical activity reported was one objective response in monotherapy dose escalation plus two responders in combination. | `[PRIMARY]` | PMID 39762422, *Nat Med* 2025;31(1):152–164, doi:10.1038/s41591-024-03334-7; NCT03289962 |
| INTerpath-007, the same individualized platform in resectable locally advanced cutaneous squamous cell carcinoma, is **TERMINATED** at an enrollment count of 46. | `[REGISTRY]` | NCT06295809 |

### 2.2 Shared / off-the-shelf

| claim | grade | source |
|---|---|---|
| AMPLIFY-7P is registered as a **Phase 1/2** first-in-human trial of ELI-002 7P in KRAS/NRAS-mutated PDAC and other solid tumours; lead sponsor Elicio Therapeutics; status ACTIVE_NOT_RECRUITING; registry enrollment count 158; the Phase 2 primary outcome is "Compare ELI-002 7P versus standard of care (SOC; **observation**) in DFS". | `[REGISTRY]` | NCT05726864 |
| Elicio announced on 15 June 2026 that **AMPLIFY-7P did not meet the pre-specified primary endpoint of disease-free survival in the intent-to-treat population**, and outlined a refined Phase 3 strategy in a defined R0-resected population with extended dosing. | `[PRESS]` | Elicio release, 15 June 2026, retrieved verbatim to `literature/amplify7p-topline-2026-06-15/elicio_release_site.txt` |
| The randomized Phase 2 part enrolled **144 patients across 24 U.S. sites**, ELI-002 7P versus observation, in resected Stage I–III mKRAS-driven PDAC, radiographically free of disease at enrollment, after surgery and standard locoregional therapy. | `[PRESS]` | as above |
| Randomization was stratified by nodal status, and the release reports a **baseline imbalance in R1 resection status against the treated arm** (ELI-002 7P 19% versus observation 10%), which it names a known adverse prognostic factor; its own multivariable analysis put R1 resection at HR 1.56, p=0.181. | `[PRESS]` | as above |
| **Post-hoc** analyses reported by the company: R0-resected subgroup DFS HR 0.65, p=0.048, n=121, median DFS 23.8 versus 12.8 months, with 18-month absolute recurrence 9.5% lower; post-hoc landmark DFS rates 90.3% versus 76.6% at 3 months (p=0.022) and 75.7% versus 61.7% at 6 months (p=0.056); R0 patients about 84% of those enrolled. Overall survival data described as immature. | `[PRESS]`, and **post-hoc after an intent-to-treat miss** | as above |
| The company also reports that mKRAS-specific T-cell responses correlated with DFS, comparing patients above and below a 9.17-fold change from baseline (HR 0.22, p<0.0001, n=90 evaluable). **This is a responder analysis, not a randomized comparison** — the same design as the AMPLIFY-201 threshold split below, and patients who mount immune responses can differ from those who do not for reasons the split does not control. | `[PRESS]` | as above |
| No treatment-related discontinuations or treatment-related deaths were reported. | `[PRESS]` | as above |
| ELI-002 2P (phase 1 AMPLIFY-201, n=25, 20 PDAC and 5 CRC, MRD-positive after locoregional therapy): direct *ex vivo* mKRAS-specific T-cell responses in **21 of 25 (84%)**, 59% both CD4⁺ and CD8⁺; tumour biomarker responses 21/25; biomarker clearance 6/25; median RFS 16.33 months; no dose-limiting toxicities. | `[PRIMARY]` | PMID 38195752, *Nat Med* 2024, doi:10.1038/s41591-023-02760-3; NCT04853017 |
| AMPLIFY-201 final results at median follow-up 19.7 months: 71% of evaluable patients induced both CD4⁺ and CD8⁺ subsets; antigen spreading in 67%. Efficacy comparisons are **between patients above and below a 9.17-fold T-cell-response threshold**, not between randomized arms. | `[PRIMARY]` | PMID 40790272, *Nat Med* 2025, doi:10.1038/s41591-025-03876-4 |
| A shared 20-neoantigen ChAd68/samRNA vaccine with ipilimumab and nivolumab in advanced/metastatic solid tumours (18/19 patients KRAS-mutant) gave an **overall response rate of 0%**, median PFS 1.9 months, median OS 7.9 months; T-cell responses were **biased toward HLA-matched TP53 neoantigens encoded in the vaccine relative to the KRAS neoantigens the tumours expressed**, which the authors describe as a previously unknown hierarchy of neoantigen immunodominance. | `[PRIMARY]` | PMID 38538867, *Nat Med* 2024, doi:10.1038/s41591-024-02851-9; NCT03953235 |

### 2.3 Shared **fusion-breakpoint** vaccines — the actual comparator class

| claim | grade | source |
|---|---|---|
| A 9-mer SYT-SSX junction peptide, HLA-A\*24:02-restricted, was given to six patients with disseminated synovial sarcoma: no serious adverse effects, peptide-specific CTLs induced from four patients, tumour progression suppressed in one. | `[PRIMARY]` | PMID 15647119, *J Transl Med* 2005, doi:10.1186/1479-5876-3-1 |
| In 21 patients across four protocols, peptide alone gave progression in all but one of nine; peptide with incomplete Freund's adjuvant plus interferon-α gave stable disease during vaccination in half of twelve; nine of 21 showed a greater-than-twofold rise in tetramer-positive CTLs; delayed-type hypersensitivity was negative in all. | `[PRIMARY]` | PMID 22726592, *Cancer Sci* 2012, doi:10.1111/j.1349-7006.2012.02370.x |
| An **off-the-shelf** multi-peptide vaccine spanning the type 1 EWSR1-FLI1 breakpoint, with GM-CSF and topical imiquimod, produced de novo polyfunctional **CD4⁺** T-cell responses against all four fusion-derived peptides, first detectable by month 7 and persisting beyond two years, with grade 1 local reactions and disease stability beyond 26 months. **n = 1.** | `[PRIMARY]` | PMID 42570981, *npj Precis Oncol* 2026;10(1):305, doi:10.1038/s41698-026-01642-4 |
| Gene fusions are a source of immunogenic neoantigens that elicit cytotoxic T-cell responses in tumours with **low mutational load and minimal immune infiltration**; the same work reports evidence of negative selective pressure against fusion-derived neoantigens in fusion-positive cancers. | `[PRIMARY]` | PMID 31011208, *Nat Med* 2019, doi:10.1038/s41591-019-0434-2 |

⚠ **The last row cuts both ways and must not be quoted only in the favourable direction.** Immune
surveillance against fusion neoantigens is a reason to expect presentation *and* a reason to expect
selection against the tumours that present them best.

---

## 3 · Is "shared versus individualized" the right axis?

**No — not from these two trials.** The table below is the discriminating observation. Every row is a
difference between the two cases; the sharedness of the antigen is one row of eight.

| axis | INTerpath-001 (reported positive) | AMPLIFY-7P (reported missed) | grade |
|---|---|---|---|
| antigen selection | individualized, up to 34 per patient | shared fixed mKRAS/NRAS peptide set | `[PRIMARY]` / `[REGISTRY]` |
| antigen biology | largely passenger mutations; sequences unrelated to any self protein | truncal driver, but a **single-residue substitution of a self protein** | `[PRIMARY]` |
| **backbone / comparator** | **added to pembrolizumab; control = placebo + pembrolizumab** | **compared against observation; no checkpoint backbone** | `[REGISTRY]` |
| disease | cutaneous melanoma | pancreatic ductal adenocarcinoma | `[REGISTRY]` |
| delivery platform | mRNA–lipid nanoparticle | amphiphile synthetic peptide with amphiphile CpG-7909, lymph-node-targeted | `[PRIMARY]` |
| phase and size | Phase 3; registry enrollment 1,089, release says 1,137 randomized 2:1 | Phase 2 part of a Phase 1/2; release says 144 enrolled across 24 sites (registry enrollment 158 covers the whole study) | `[REGISTRY]` / `[PRESS]` |
| endpoint | recurrence-free survival | disease-free survival | `[REGISTRY]` |
| baseline balance | not disclosed | company reports an R1-resection imbalance against the treated arm, 19% versus 10% | `[PRESS]` |
| setting | resected, adjuvant | resected, adjuvant, MRD-selected | `[REGISTRY]` / `[PRESS]` |

Only the last row is matched. **The two axes that a reader would most want held constant — the disease
and the presence of a checkpoint backbone — are the two that differ most.** Melanoma is the tumour type
in which checkpoint blockade works best; PDAC is one in which it does not. And a vaccine tested *on top
of* an active immunotherapy is being asked a different question from a vaccine tested *instead of
nothing*.

**Three further observations refuse the simple story:**

- The shared platform is **highly immunogenic**: 21 of 25 patients raised direct *ex vivo*
  mKRAS-specific T cells `[PRIMARY]`. Whatever went wrong in AMPLIFY-7P, "shared antigens do not raise
  T cells" is not supported.
- The individualized platform's **only randomized publication retrieved here missed the conventional
  cut** on its primary endpoint (p=0.053) `[PRIMARY]`, and its most recent update is descriptive
  `[PRIMARY]`. The Phase 3 that would settle it is unpublished `[PRESS]`.
- The individualized platform has a **terminated** study in another resected solid tumour `[REGISTRY]`.
  Platform-level success is not uniform across diseases, which is the same conclusion the confounding
  table forces.

**What the two cases would need in order to speak to sharedness:** the same antigen class, in the same
disease, on the same backbone, with the same endpoint, differing only in whether the antigen set is
patient-specific. **No such comparison was identified in the searches run for this memo.**

---

## 4 · Where an EWSR1::NR4A3 junction vaccine actually sits

It is not on either side of the binary. It is a **third category: a shared antigen that is also a
truncal, fully tumour-specific driver sequence.**

**What it has that a shared KRAS peptide does not.** A fusion junction encodes residues present in
neither parent protein — the corrected transcript-level junction set gives 5 in-frame exon pairs of 27
declared, each carrying junction-spanning peptides absent from both parents `[REPO]`
([`fusion-neoantigen-retraction.json`](../../modalities/fusion-neoantigen-retraction.json)). A KRAS
G12D peptide differs from self at one residue; a junction peptide is a novel sequence at the seam. It
also cannot be lost without loss of the driver, which is the property the sponsors of individualized
therapies are *paying* to approximate by sequencing each tumour.

**What it has that an individualized vaccine does not.** Design-space enumerability. The antigen is
determined by which exon pair the patient carries, not discovered per patient, so a small fixed panel
allocated by a diagnostic assay replaces per-patient manufacture — which matters because at EMC's
incidence per-patient manufacture is the limit, not the antigen (§B9 of
[`emc-vaccine-development-path.md`](./emc-vaccine-development-path.md)). **The INTerpath-001 result
therefore does not transfer to EMC even if it is everything the announcement says**: what it
demonstrates is that individualized manufacture is a clinical reality, and individualized manufacture is
the one option this disease cannot buy.

**What bounds it, and none of these is sharedness** `[REPO]`, all from
[`hla-coverage.json`](../../modalities/hla-coverage.json) and the vaccine paper's §2.3 and §B1–B10:

- **Epitope breadth.** The screen returns 11 distinct predicted binders, 4 strong, across all in-frame
  junctions. The class II arm yields **one strong epitope, on DRB1\*14:01, of 23 alleles tested**.
- **HLA restriction.** The commonly reported *EWSR1* exon 7 :: *NR4A3* exon 3 junction covers 8.5% on
  the ten-allele screen and 12.3% on the 34-allele screen; pooling every in-frame junction gives 27.4%
  and 30.4% on those two panels. None of these is a ceiling, and all of them move with the panel, the
  acceptance threshold and the predictor by more than the distance between them. **Quote them from the
  paper's §2.3 and Appendix B, never bare.**
- **Self-adjacency.** The lead peptide sits one residue from a sequence in a normal *NR4A3* isoform and
  two from a paralogue peptide, with neither difference at an anchor position under the general class I
  convention of position 2 and the C-terminus.
- **The tumour.** A cold microenvironment and a myxoid matrix proposed to exclude lymphocytes — the
  properties `BLK-ANTIGEN-COLD` names, and the ones a vaccine cannot address by itself.
- **Trial arithmetic.** Applying the fusion-partner fraction and the HLA fraction to the accrual rate of
  the one EMC histology-specific cohort that has actually run leaves roughly 0.3 to 1.4 eligible
  patients a year.

**Predicted binding is a screen. It is not presentation, not immunogenicity and not benefit.** Nothing
in this memo supports the use of any agent outside a clinical trial.

**Read against the fusion-breakpoint literature in §2.3, the honest position is:** the closest human
data to this route are a single Ewing patient and two decade-old synovial-sarcoma trials, one of which
found that peptide *alone* produced progression in eight of nine patients while peptide with adjuvant
and interferon produced stable disease in half of twelve `[PRIMARY]`. The reading that survives is about
**adjuvant and backbone, not about sharedness** — which is the same reading §3 forces from the 2026 pair.

---

## 5 · What is UNKNOWN

An honest unknown beats a confident guess. Each of these is a question this memo could not answer, not a
finding of absence.

### 5.1 INTerpath-001

- Hazard ratio, confidence interval, p-value, event counts, absolute RFS or DMFS difference, median
  follow-up, and every subgroup result: **not disclosed**. No peer-reviewed publication of this trial
  appears among the Europe PMC records retrieved on 2026-08-24, and the release itself says the data
  will be presented at a future medical meeting. **That is a statement about what these searches
  returned, not proof that nothing exists.**
- The release states 1,137 patients enrolled; the registry record's enrollment count is 1,089. **This
  memo cannot reconcile the two and does not assert either as the analysis population.**
- Whether the RFS benefit is attributable to the neoantigen content, to the mRNA-LNP platform's own
  innate immunostimulation, or to both: **undetermined by the available record.**

### 5.2 AMPLIFY-7P

The company release was retrieved verbatim on the third CI attempt; two earlier attempts against the
GlobeNewswire mirror timed out and are recorded as timeouts, not as empty results, in the manifests of
`literature/neoantigen-press-primary-sources/` and `literature/amplify7p-topline-2026-06-15/`. What
remains unknown after reading it:

- **The intent-to-treat result itself.** The release states the primary DFS endpoint was not met and
  reports no ITT hazard ratio, no ITT confidence interval, no ITT p-value and no event counts. Every
  number it does give for efficacy is post-hoc, landmark or a responder split.
- Whether any of the post-hoc or landmark analyses were prespecified, what the multiplicity handling was,
  and what the study was powered to detect: **not stated.** A post-hoc subgroup at p=0.048 following an
  ITT miss is hypothesis-generating; the release itself frames it as informing a future trial rather than
  as a result.
- The magnitude of the R1 imbalance's effect. The company asserts the imbalance "meaningfully and
  negatively impacted the ELI-002 arm" while its own multivariable estimate for R1 resection is HR 1.56 at
  p=0.181 — an unstable estimate that does not settle the question either way. **This memo takes no
  position on it.**
- Whether the miss is attributable to antigen sharedness, to the absence of a checkpoint backbone, to
  PDAC biology, to the baseline imbalance, or to power: **undetermined.** The registry establishes that
  the comparator was observation, and the release establishes that 144 patients were enrolled, which
  makes the backbone and power explanations available; neither establishes that either is the right one.

### 5.3 The EMC route itself

- Whether **any** junction peptide is presented on EMC tissue: never measured, in this repository or
  anywhere identified.
- Whether the anchor convention decides it: the near-self search has been run `[REPO]` and places the
  seam differences away from the anchors under the general class I convention, but position 1's anchor
  status for the five restricting alleles is unresolved here and flips six of the 11 binders.
- Whether EMC retains HLA class I at the **protein** level, per tumour rather than per cohort.
- Whether a wider allele panel or a better predictor raises coverage enough to change the trial
  arithmetic.
- Whether the Ewing n=1 replicates in a series.
- **No head-to-head shared-versus-individualized trial was identified** in the Europe PMC and registry
  searches run for this memo. That is a statement about what these searches returned, not a claim that
  none exists.

---

## 6 · Consequence for the junction-vaccine route

### 6.1 This does not change the grade, and here is why

`RT-VACCINE` is graded **PARKED** on `BLK-ANTIGEN-COLD` — "a self-adjacent junction in a cold tumour is
a weak immunogen" — with its coverage output reusable and still feeding TCR-T eligibility
([`systems/graph/routes.json`](../../../systems/graph/routes.json)). **Neither 2026 datapoint touches
that blocker.**

- AMPLIFY-7P tested a shared vaccine **against observation, with no checkpoint backbone, in a tumour
  type as cold as EMC, in 144 patients, with a baseline prognostic imbalance against the treated arm**
  `[REGISTRY]` / `[PRESS]`. If anything it is weak, confounded, press-level support for the blocker this
  route is *already* parked on — it is not a new finding about shared antigens, and a route cannot be
  downgraded twice for the same reason.
- INTerpath-001 tested an **individualized** therapy **on a checkpoint backbone in the most
  checkpoint-responsive solid tumour** `[PRESS]`, using a manufacturing model that EMC's incidence
  forecloses. It is not transferable in either direction.
- The measured facts that actually bound this route — epitope breadth, HLA restriction, self-adjacency,
  the cold microenvironment, the accrual arithmetic — are unchanged by both, because all of them are
  properties of this junction and this disease `[REPO]`.

**So: no re-grade of `RT-VACCINE` is warranted, and none is made here.** Its grade line and its owner
file are untouched by this memo.

### 6.2 The re-grade PROMPT this memo does raise — for trimcrae, not a decision taken here

The one axis on which the two 2026 cases differ **cleanly and verifiably** is the backbone: a vaccine
added to a checkpoint inhibitor versus a vaccine against observation `[REGISTRY]`. That is precisely the
premise of `RT-VACCINE-COMBINATION`, registered 2026-08-19 as an **ungraded unit** on the observation
that "each verdict assumed the other component absent". The synovial-sarcoma finding in §2.3 — peptide
alone giving progression in eight of nine, peptide with adjuvant and interferon giving stable disease in
half of twelve `[PRIMARY]` — points the same way, in the same modality, in a sarcoma.

**The prompt:** does the combination route's `supporting_evidence` warrant a row for the
backbone-versus-no-backbone contrast, given that it is now traceable to two registry records and one
peer-reviewed sarcoma trial rather than to a press comparison? **This memo does not answer that and does
not edit the graph.** Nothing here promotes any route, and no family holds `portfolio_role: lead`.

### 6.3 What would have to be true for the route to be in trouble

Stated as falsifiers, so that a future session can check them rather than re-argue them.

1. **A shared, truncal, fully tumour-specific fusion-junction vaccine fails on a checkpoint backbone, in
   a checkpoint-responsive fusion-driven tumour, with adequate power.** That would attack the antigen
   class itself rather than the setting, and it is the single result that would most damage this route.
   **No result of that shape appears among the records retrieved for this memo** — which is a statement
   about these searches, not proof that none exists.
2. **Immunopeptidomics on EMC tissue or a patient-derived line finds no junction peptide presented.**
   This bounds the whole route and is already listed as a required validation, blocked on
   `BLK-NO-EMC-DATA`.
3. **The seam residues fall only at anchor positions rather than at T-cell-receptor contact
   positions**, so that the neoepitope and its near-self *NR4A3*-isoform neighbour present the same
   surface to a receptor and central tolerance to the neighbour has deleted the repertoire.
   ⚠ **Corrected 2026-09-01: this falsifier previously named the opposite configuration** — contact
   positions rather than anchors — which inverts it, because a difference the receptor can read is
   what leaves a repertoire possible. It was written from a clause in the vaccine paper's §B3 that
   stated the same ordering the wrong way round; that clause is now withdrawn there, in its Appendix
   C, and §B3's own next sentence had always named the anchor-only case as the worst one.
   The near-self search has been run `[REPO]`
   ([`junction-selfsimilarity.json`](../../modalities/junction-selfsimilarity.json)): under the
   general class I convention of position 2 and the C-terminus, no binder is in this configuration.
   ⛔ **And it is not the fully computable item this row used to claim.** The convention is not
   allele-specific; counting position 1 as an anchor puts six of the 11 binders in the failing
   configuration, all six against the same *NR4A3* isoform, and this repository holds no
   allele-specific binding motif for HLA-A\*01:01, B\*07:02, B\*15:01, B\*35:01 or B\*44:02. What is
   computable has been computed; what remains needs a motif source that has to be fetched.
4. **HLA class I is lost at the protein level in individual EMC tumours**, as opposed to the cohort-level
   transcript reads that currently show it flat rather than lost.
5. **Wider allele panels and better predictors fail to raise coverage**, leaving the eligible-patient
   arithmetic where it is. Coverage that does not move is the difference between a route with a
   stratified product and a route with no reachable cohort.
6. **The EWSR1-FLI1 n=1 fails to replicate**, or its durable CD4 responses prove on re-analysis not to
   be junction-specific. That single case is currently the strongest human evidence the whole design
   class has.

Conversely, **none of the following would rescue the route**, and a future session should not treat them
as if they did: another positive individualized-therapy readout in a common tumour; another shared-vaccine
failure in a disease with no checkpoint backbone; or any announcement without a disclosed effect size.

---

## 7 · Provenance

Retrieval records for everything cited above, all fetched 2026-08-24 by
`.github/workflows/fetch-literature.yml` and published to the `literature-cache` branch:

- `literature/neoantigen-press-primary-sources/` — the ClinicalTrials.gov API v2 records for
  NCT05933577, NCT06295809, NCT05726864, NCT04853017, plus the Merck and Moderna INTerpath-001 releases
  and the manifest recording the first GlobeNewswire timeout.
- `literature/amplify7p-topline-2026-06-15/elicio_release_site.txt` — the Elicio AMPLIFY-7P release of
  15 June 2026, retrieved verbatim, plus `ctgov_nct05726864.txt` and a manifest recording the second
  GlobeNewswire timeout.
- `literature/individualized-neoantigen-mrna4157/_index.json` — Europe PMC records including
  PMID 38246194, 42223134, 39115419, 39762422.
- `literature/shared-neoantigen-kras-vaccine/_index.json` — Europe PMC records including PMID 38195752,
  40790272, 38538867.
- `literature/ewsr1-fli1-peptide-vaccine/_index.json` — Europe PMC records including PMID 42570981,
  15647119, 22726592, 31011208.

Those retrievals are consolidated into one tracked artifact,
[`shared-vs-individualized-neoantigen-sources-2026-08-24.json`](../../literature/shared-vs-individualized-neoantigen-sources-2026-08-24.json),
which carries the eleven bibliographic records, the four registry records and the verbatim announcement
sentences quoted above — including the recorded GlobeNewswire timeouts.

**No identifier in this memo was written from recollection.** Every PMID, DOI and NCT number was
transcribed from one of the retrieval records above.

**Related documents.** The route's standing-state report is
[`emc-vaccine-development-path.md`](./emc-vaccine-development-path.md), which owns the coverage figures,
the ten limits and the combination framing; this memo adds only the shared-versus-individualized grading
and does not restate them. The two datapoints' original rows are in
[`method-watch-backfill-2026-08.md`](../../method-watch-backfill-2026-08.md) §3. The route records are in
[`systems/graph/routes.json`](../../../systems/graph/routes.json).
