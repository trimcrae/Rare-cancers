---
id: DOC-EMC-TXN-PROTEOSTATIC
title: Two unpaired evidence streams for a fusion transcription factor — transcript-score contrasts in archival EMC tumours and knockout dependency in non-EMC cancer lines
level: L3
kind: manuscript
status: live
canonical_for: ["the 2026-08-09 EMC transcriptional-CDK and chaperone dependency readings"]
purpose: >
  Describe, transparently and separately, two evidence streams assembled for extraskeletal myxoid
  chondrosarcoma: relative transcript-score contrasts for seven curated gene lists in archival
  EMC-labelled tumours against selected other soft-tissue tumours, and single-gene CRISPR knockout
  effects for five of the same genes in non-EMC cancer cell lines. The two streams are unpaired —
  different material, different populations, different scales — so no relationship between them is
  estimated here, and none is claimed. The paper reports what each stream describes, what neither
  can decide, and what would have to be measured instead.
scope: >
  L3. Two public archival expression series, 16 EMC-labelled specimen records, transcript level only,
  plus a public cancer cell-line CRISPR dependency release containing no EMC line. Reports no new
  experiment, no drug exposure, and no new patient contact; the archival records analysed are
  patient-derived and were deposited publicly by others.
audience: [maintainers, external reviewers, autonomous research agents, collaborators]
date: 2026-08-09
last_verified: 2026-09-08
related: [DOC-MODALITY-CENSUS, DOC-EMC-BIOMARKER-SELECTED]
---

# Two unpaired evidence streams for a fusion transcription factor

**Tristan D. McRae**

Independent researcher, unaffiliated. Correspondence: trimcrae@gmail.com.
ORCID 0000-0002-1823-1451.

*Study type: a computational study of public archival tumour-expression series and a public
cancer-cell-line CRISPR dependency release. No experiment was performed for it, no cell was cultured,
and no new recruitment, sampling or clinical intervention was undertaken. The records analysed are
patient-derived archival material deposited publicly by others.*

> ⛔ **Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness for any agent
> in any disease.** This paper reads relative transcript scores from 16 archival EMC-labelled specimen
> records and a public dependency release containing no cell line from this disease.

---

## Summary

Extraskeletal myxoid chondrosarcoma (EMC) is driven by an *NR4A3* gene fusion, most often
**EWSR1::NR4A3**. Two hypotheses motivated the reads reported here, and both remain hypotheses.

**The driver's described mechanism is transactivation.** A cancer whose driver is a transcription
factor *may* depend disproportionately on the general transcriptional machinery — the *transcriptional
addiction* argument (Bradner *et al.*, 2017), made pharmacologically approachable by covalent CDK7
inhibitors (Kwiatkowski *et al.*, 2014) and reported for one defined tumour type (Wang *et al.*, 2015).
⚠ That a driver is a transcription factor does not by itself establish a disproportionate dependency;
it motivates looking.

**The driver is a chimera of two domains that did not evolve together**, which suggests a folding
problem before a signalling one. ⚠ The step from there to *chimeric proteins are disproportionately
chaperone-dependent* is this programme's working hypothesis and is stated as one throughout. No source
retrieved here establishes it as a general property of fusion proteins, and nothing below rests on it.

**What this paper contains is two descriptive evidence streams that were not measured together.**

- **Stream A — relative transcript scores.** Seven curated gene lists, scored as the mean
  within-array standardized value over the readable members of each list, compared between EMC-labelled
  specimens and selected other soft-tissue tumour specimens on two archival platforms. The
  transcriptional-CDK initiation module and the transcriptional-output context list read higher in the
  EMC-labelled group at nominal uncorrected significance on the array platform whose reference design
  is interpretable (GPL6244); so does the four-gene HSP90 machine list. The HSP70-and-stress list
  gives negative point estimates that are **not** statistically distinguishable from zero, and whose
  approximate intervals include positive differences.
- **Stream B — single-gene knockout effects.** In DepMap 24Q4 Chronos gene effects, CDK7 and CDK9 are
  scored dependencies in 91 of 91 screened sarcoma-lineage lines; HSP90AA1 and HSP90AB1 in 5 and 17 of
  91; the co-chaperone CDC37 in 89 of 91. The cancer-line mean differences between sarcoma-lineage and
  other cancer lines are small (|difference| ≤ 0.085 gene-effect units) and are reported without a
  precision estimate.

⛔ **These two streams are not paired and no relationship between them is estimated here.** Stream A
is measured in archival patient tumour specimens on decade-old arrays; Stream B is a knockout
phenotype in cultured cancer cell lines, none of which is EMC. The material, the populations, the
genes summarized and the scales all differ. This paper therefore makes **no claim that abundance and
dependency disagree**, in opposite directions or at all, and it makes no claim that a reader relying
on one stream alone would have been misled. Testing such a claim requires a design that observes a
specified relation between expression and dependency in comparable units. That design was not run.

⛔ **No dependency was observed in EMC.** The single DepMap model carrying the EMC label contributes
no CRISPR gene-effect data at all. Nothing here decides, closes or reopens an EMC-specific
vulnerability in either class, and any statement about what Stream B implies for EMC is an
**uncalibrated assumption**, not a validated transfer: shared "sarcoma" lineage membership does not
establish that a dependency structure carries to this disease.

---

## 1 · What was measured, and how

### 1.1 Stream A — the expression construct

**Series and cohorts.** Two public series were read.

| platform record | GEO platform | specimens | EMC-labelled | comparator arm as annotated | excluded from both arms |
|---|---|---|---|---|---|
| `GSE24369_series_matrix.txt.gz` | GPL6244, single-channel intensity | 42 | 6 | 17 low-grade fibromyxoid sarcoma, 6 desmoid fibromatosis, 6 myxofibrosarcoma (binned by the classifier under `fibrosarcoma`) | 5 solitary fibrous tumour, 2 pooled skeletal-muscle RNA |
| `GSE4303-GPL3290_series_matrix.txt.gz` | GPL3290, two-colour log-ratio against a reference pool | 16 | 10 | 3 dermatofibrosarcoma protuberans, 3 gastrointestinal stromal tumour | none |

⚠ **Cohort assembly was operational, not prospective.** Specimens were assigned to arms by
string-matching their deposited annotation text; "other sarcoma" is therefore a biologically mixed,
operationally selected comparator, and the 5 solitary fibrous tumour and 2 pooled skeletal-muscle
records fall outside it because the classifier does not name them, not because a scientific exclusion
rule was applied to them. The counts above are **specimens/arrays under deposited labels**. They do
not establish patient uniqueness, independence across studies, or molecular confirmation of the fusion
in any specimen; the deposited metadata read here carries none of that information.

**Scoring.** For each gene, each array's value is standardized within that array against the array's
own distribution over all probes: (value − array mean over all probes) ÷ (array SD over all probes).
A group score for a specimen is the **unweighted** mean of those standardized values over the
**readable** members of the list — every readable member counts equally; there are no weights. Group
scores are then compared between arms by Welch's *t*, and the reported difference is
EMC-mean minus comparator-mean in units of the array's own probe-distribution SD.

⛔ **What this construct is not.** It is not absolute mRNA concentration, not a transcription rate,
not protein abundance, and not a conventional pooled between-patient standardized effect size. A
GPL6244 intensity and a GPL3290 log-ratio do not share a biological effect scale, so the two
platforms' numbers must not be read against each other as though they did. A gene counted
*not readable* has no probe mapping to its symbol on that platform; that is a mapping and platform
limit, **not** evidence that the gene is unexpressed.

**⚠ Interpretation hold on GPL3290.** The deposited annotations on this platform name **three
different reference labels**: the ten EMC-labelled specimens carry `CRH-mRNA`, the three DFSP
specimens carry `CRH`, and the three GIST specimens carry `UHR`. For a two-colour log-ratio, a
between-group difference can absorb a gene-specific difference between reference pools, and
subtracting each array's global mean and dividing by its global SD does not generally remove such a
difference. Whether the deposited values were harmonized upstream across those labels is **not
established** by anything read here — and incorrect original preprocessing is **not** established
either. **Accordingly, GPL3290 is withdrawn as independent biological corroboration.** Its values are
displayed below for completeness and historical continuity, under this hold; no biological conclusion
in this paper rests on them, and no re-analysis, reference substitution or comparator change was
performed. Reopening the GPL3290 interpretation requires authentic deposited processing and reference
documentation showing comparability across `CRH`, `CRH-mRNA` and `UHR`, or a separately designed
compatible-reference contrast with its own changed estimand.

**Gene lists.** All seven are ⚠ **repository-curated pathway-membership lists, not published gene sets
or signatures** — each panel's own `provenance` field says so in terms. A differently drawn list could
move any group statistic below.

| panel | group | requested members | readable on GPL6244 | readable on GPL3290 |
|---|---|---|---|---|
| transcriptional CDK | `cdk7_initiation_module` | CCNH, CDK7, MNAT1 | 3/3 | 3/3 |
| transcriptional CDK | `cdk9_elongation_module` | AFF4, CCNT1, CCNT2, CDK9 | 4/4 | 4/4 |
| transcriptional CDK | `cdk12_13_processivity` | CCNK, CDK12, CDK13 | 3/3 | 3/3 |
| transcriptional CDK | `transcriptional_output_context` | GTF2B, MYC, POLR2A, TAF1 | 4/4 | 4/4 |
| chaperone | `hsp90_machine` | HSP90AA1, HSP90AB1, HSP90B1, TRAP1 | 4/4 | 3/4 — *HSP90AA1* unreadable |
| chaperone | `co_chaperones` | AHSA1, CDC37, PPID, PTGES3, STIP1 | 5/5 | 5/5 |
| chaperone | `hsp70_arm_and_stress_response` | DNAJB1, HSF1, HSPA4, HSPA8, HSPH1 | 4/5 — *HSPA8* unreadable | 4/5 — *HSF1* unreadable |

⚠ **The two platforms do not read the same HSP70 list**: *HSPA8* is missing on GPL6244 and *HSF1* on
GPL3290, so the heat-shock transcription factor itself is absent from one of the two reads. A missing
member of either list could move the group score in either direction.

### 1.2 Stream B — the dependency construct

Source: **DepMap public release 24Q4** (`CRISPRGeneEffect.csv` and `Model.csv`), Chronos gene effect,
in which a more negative value means a larger fitness cost on knockout.

- **Dependent** is defined by a single fixed threshold: **gene effect < −0.5**. It is a binary cut on
  a continuous score, not a graded response, not a drug sensitivity, and not a therapeutic margin.
- **Cohort rule.** A model is counted "sarcoma" if its `OncotreeLineage` is **Soft Tissue or Bone**.
  This is an operational lineage rule applied to release metadata, not a curated histological review.
- ⚠ **Two different counts describe that cohort and both are needed.** The release catalogues
  **176** Soft Tissue/Bone models, but every gene summarized here has non-missing gene-effect values
  for **91** of them. **91 is the denominator of every percentage below**; 176 is a catalogue size.
- **Mean difference.** The quantity the artifact labels `selectivity` is **(mean gene effect in
  non-sarcoma cancer lines) − (mean gene effect in sarcoma-lineage lines)**. It is a difference of two
  cancer-line means. ⛔ It is not a within-sarcoma discrimination statistic, not a tumour-versus-normal
  comparison, and not a validated therapeutic-selectivity scale. It is reported here **without** a
  variability estimate, without the non-sarcoma non-missing sample size, and without an equivalence
  margin, because the retained artifact supplies none of those.

⛔ **No line in this release supplies a CRISPR observation for this disease.** The single model
carrying the EMC label has no CRISPR gene-effect data at all (`fet-ddr-axis-scan.json`,
`emc_line.has_crispr_gene_effect = false`), which settles the point on its own. The further curated
record that this line does not harbour the fusion is *suggestive and consistent, not definitive* in
the repository's own words; this paper does not rest on it and does not treat that line's disease
identity as resolved.

⚠ **The release's own `self_validation` block cannot be credited as passed.** Its stated criterion is
that each control subtype show a clearly more-negative mean gene effect and a high dependent fraction
relative to the gene's rest-of-panel value. BRD9 in 5 synovial models gives mean −0.13 with 20 %
dependent. SMARCB1 in 13 rhabdoid models gives mean **−0.025** with **7.7 %** dependent, against a
rest-of-panel mean of **−0.832** and **83.9 %** dependent — that is the **opposite** of the stated
expected-positive direction, so this control **fails its own criterion**. ⛔ It is not relabelled here
as a passed negative control, and its failure does **not** show that the CDK or chaperone numbers
below are wrong: it means this release's sensitivity to selective dependencies is **not calibrated**
by the check it carries. Whether the control is even suitable depends on each target's actual
functional and genotypic status in those models, which a label-based match does not establish.

## 2 · Stream A results

All values are read from the frozen artifact. **Δ** is EMC-minus-comparator in within-array
standardized units on that platform; *t* and df are Welch's as the artifact prints them.
**Approximate two-sided *p* and 95 % intervals are conditional arithmetic on the rounded published
Δ/*t*/df** — the interval uses Δ ÷ *t* as the standard error together with the printed rounded df, so both
inherit the artifact's rounding. They are not newly measured quantities and not a re-analysis.
⚠ **All readings are exploratory and uncorrected for multiple testing.**

**GPL6244 (GSE24369; 6 EMC-labelled vs 29 comparator specimens).**

| group | coverage | Δ | *t* | df | approx. *p* | approx. 95 % interval |
|---|---|---|---|---|---|---|
| `cdk7_initiation_module` | 3/3 | +0.2102 | 3.688 | 6.6 | 0.0086 | +0.074 to +0.347 |
| `cdk9_elongation_module` | 4/4 | +0.0450 | 1.189 | 5.7 | 0.282 | −0.049 to +0.139 |
| `cdk12_13_processivity` | 3/3 | −0.0418 | −0.880 | 6.8 | 0.409 | −0.155 to +0.071 |
| `transcriptional_output_context` | 4/4 | +0.1983 | 3.782 | 7.5 | 0.0061 | +0.076 to +0.321 |
| `hsp90_machine` | 4/4 | +0.0899 | 3.857 | 15.0 | 0.0016 | +0.040 to +0.140 |
| `co_chaperones` | 5/5 | +0.0809 | 1.636 | 7.6 | 0.142 | −0.034 to +0.196 |
| `hsp70_arm_and_stress_response` | 4/5 | −0.0853 | −1.056 | 7.5 | 0.324 | −0.274 to +0.103 |

**GPL3290 (GSE4303; 10 EMC-labelled vs 6 comparator specimens) — ⚠ displayed under the §1.1
interpretation hold; not used as corroboration.**

| group | coverage | Δ | *t* | df | approx. *p* | approx. 95 % interval |
|---|---|---|---|---|---|---|
| `cdk7_initiation_module` | 3/3 | +0.4966 | 4.113 | 9.6 | 0.0023 | +0.226 to +0.767 |
| `cdk9_elongation_module` | 4/4 | +0.1737 | 2.258 | 13.1 | 0.0416 | +0.008 to +0.340 |
| `cdk12_13_processivity` | 3/3 | −0.0751 | −0.690 | 13.5 | 0.502 | −0.309 to +0.159 |
| `transcriptional_output_context` | 4/4 | +0.4709 | 4.811 | 9.8 | 0.00075 | +0.252 to +0.690 |
| `hsp90_machine` | 3/4 | +0.6075 | 3.465 | 11.0 | 0.0053 | +0.222 to +0.993 |
| `co_chaperones` | 5/5 | +0.2511 | 2.011 | 12.0 | 0.0673 | −0.021 to +0.523 |
| `hsp70_arm_and_stress_response` | 4/5 | −0.1639 | −0.959 | 5.9 | 0.375 | −0.584 to +0.256 |

**Multiplicity.** Fourteen group-by-platform readings are printed, drawn from a wider curated census;
declaring lists curated does not remove multiplicity, and the specification of these lists relative to
seeing the data is not documented here. ⚠ For illustration only, a Bonferroni threshold across these
fourteen readings (α = 0.05/14 ≈ 0.0036) is cleared by three of them — `cdk7_initiation_module` and
`transcriptional_output_context` on GPL3290, `hsp90_machine` on GPL6244 — and **no group clears it on
both platforms**. ⛔ Fourteen is not established here as the correct testing family; the illustration
reinforces the exploratory status of these estimates rather than confirming or refuting any of them.

**What the lists do and do not show internally.** The `transcriptional_output_context` label must not
be read as a uniform rise of the general polymerase machinery. *MYC*'s own difference is **+1.0625**
on GPL6244 and **+1.863** on GPL3290, against four-gene group means of +0.1983 and +0.4709. Simple
algebra on those published summaries leaves a mean difference for the other three members of
approximately **−0.090** and **+0.007** respectively. ⚠ That algebra is descriptive bookkeeping on
rounded summaries, **not** a new gene-set test of a three-gene panel. Similarly, *HSP90AA1*'s own
difference is negative on GPL6244 and unreadable on GPL3290, so the `hsp90_machine` group result
cannot be attributed to that gene.

**The HSP70 reading.** The two negative point estimates are **not** statistically distinguishable
from zero, and their approximate intervals (−0.274 to +0.103; −0.584 to +0.256) **include positive
differences**. ⛔ They therefore do not establish absence of elevation, they are not an equivalence
result, and they are not evidence of contradictory biology. Nor is a relative contrast against other
tumour types a test of whether EMC cells mount a stress response at all: both arms could be elevated
against an appropriate baseline that this design does not contain. The list mixes heterogeneous
members with platform-specific omissions and is not a validated measurement of the classical
heat-shock programme or of HSF1 activity; the malignancy-associated HSF1 programme is in any case
described as distinct from classical heat shock (Mendillo *et al.*, 2012; PMID 22863008). ⛔ Nothing in this reading
refutes, or supports, a standing proteostatic load.

**Proliferation and other covariates.** ⛔ This paper makes **no claim** that either reading is
independent of proliferation. The retained eleven-gene proliferation-control list gives *t* = 0.441
and 2.905 at df 6.7 and 14.0 with Δ = 0.0896 and 0.4459; the single-gene *MKI67* group is marked
unscored by the panel-size rule. A separate gene read is not proliferation matching, and those
controls do not establish independence. Tumour cellularity, lineage composition, tissue handling,
batch and reference composition are likewise unresolved, and any of them could contribute to the
contrasts above.

## 3 · Stream B results

DepMap 24Q4 Chronos gene effects. **n = 91** screened sarcoma-lineage lines per gene; "dependent" is
gene effect < −0.5; "difference" is non-sarcoma-cancer-line mean minus sarcoma-lineage mean. The
integer counts are the unique integers compatible with the stored rounded fractions, not separately
observed raw counts.

| gene | sarcoma mean | rest-of-panel mean | difference (rest − sarcoma) | dependent, sarcoma | dependent, rest |
|---|---|---|---|---|---|
| CDK7 | −1.847 | −1.762 | +0.085 | 91/91 (100 %) | 99.9 % |
| CDK9 | −1.464 | −1.447 | +0.017 | 91/91 (100 %) | 99.4 % |
| HSP90AA1 | −0.230 | −0.256 | −0.026 | 5/91 (5.5 %) | 5.2 % |
| HSP90AB1 | −0.348 | −0.275 | +0.073 | 17/91 (18.7 %) | 11.9 % |
| CDC37 | −1.093 | −1.160 | −0.067 | 89/91 (97.8 %) | 98.7 % |

**What these numbers support.** CDK7 and CDK9 cross the −0.5 threshold in every screened
sarcoma-lineage line, with large mean effects; CDC37 crosses it in nearly all of them; the two HSP90
paralogues cross it in a small minority. The cancer-line mean differences are small and descriptive.

⛔ **What they do not support.** All lines crossing a single binary threshold does **not** imply equal
continuous effects, absence of subgroup heterogeneity, absence of a graded response to partial
inhibition, or absence of a selectable phenotype. The mean differences are point estimates without
variability, without comparator sample sizes and without an equivalence margin, so they cannot
establish "no selectivity". Pooled lineage means cannot rule out within-lineage subgroups — HSP90AB1,
for instance, is 18.7 % dependent in sarcoma-lineage lines against 11.9 % elsewhere, which this
summary can neither dismiss nor confirm as important. And a cancer-versus-cancer comparison cannot
establish a tumour-versus-normal window, which is the question a therapeutic argument would need.
⚠ The uncalibrated `self_validation` control (§1.2) further limits what an absence of a detected
difference in this release would mean.

⚠ **The published class literature points the same way on scope.** The covalent CDK7 inhibitor report
describes exceptional sensitivity in a *subset* of cancer lines (Kwiatkowski *et al.*, 2014), and the
triple-negative breast cancer work contrasts CDK7 dependence between tumour subsets using both
inhibitor and CRISPR/Cas9 approaches (Wang *et al.*, 2015). Those are model-specific differential CDK
dependencies in other diseases and assays. They are relevant context: a binary threshold in one
release is not a general disqualification of a target class. ⛔ They are also not evidence of an EMC
window and not a re-analysis of 24Q4.

**HSP90 paralogues and the co-chaperone.** ⛔ The low dependent fractions must not be read as
"HSP90 is dispensable", and equally must not be read as demonstrated paralogue compensation. Single
knockouts of *HSP90AA1* and *HSP90AB1* were measurable and produced recorded classifications in 5.5 %
and 18.7 % of lines; the paralogues are **not** "untestable singly". Mutual redundancy is a plausible
explanation for low single-knockout effects and is **not the only one**, and no dual perturbation or
rescue experiment appears in this release or anywhere read here. **CDC37's 97.8 % is the measured
observation**: a broad requirement for that kinase-specific co-chaperone under these screen
conditions. It is not a measurement of every HSP90-family component, not a cytosolic double knockout,
not evidence about any fusion protein, and not a therapeutic window. Note also that the expression
list `hsp90_machine` contains four genes while the dependency rows cover two of them plus a different
co-chaperone; the two streams do not describe the same set of genes.

## 4 · Bounded literature assessment of chaperone clientship

The cheaper precursor to any client experiment was a literature question: **is any FET-family fusion
protein a documented chaperone client?** A dated PubMed assessment of **fifteen queries run on
2026-08-27** was performed, with each query string and its hit count recorded in the cited artifact.

**Finding, stated to its actual scope.** ⛔ *We did not identify a qualifying direct binding result —
co-immunoprecipitation, pull-down or affinity capture — for any FUS, EWSR1 or TAF15 fusion protein
among the items inspected in that dated search.* ⚠ That is a bounded search finding, not a
demonstration that no such result exists and not a statement that the experiment has never been
attempted, published or unpublished. Its explicit limits:

- Query **Q15 returned 25 hits that were not individually screened**. No inference is drawn here from
  what they might contain.
- Query **Q13** located the one systematic human chaperone client screen (PMID 25036637),
  whose full text names no FET protein; **whether the FET proteins appear in its deposited
  supplementary panel is unknown** and was not retrieved.
- Several records were **abstract-only or full-text inaccessible**, and **preprint servers and
  non-PubMed-indexed sources were not searched**. A title-only interactome query cannot establish that
  no physical interactome exists.

**What the inspected records do contain, with the distinctions kept.** *EWS::FLI1* protein levels fall
when the HSP90 machine is perturbed pharmacologically (PMID 24388362; PMID 36495678) and when the
HSP90 co-chaperone SGT1/SUGT1 is depleted genetically (PMID 25985210). ⚠ **That is depletion, not
binding.** None of those reports includes a cycloheximide chase, a proteasome-block rescue or a
parallel mRNA measurement, so a route through the fusion's own autoregulated transcription is not
excluded. Separately, engineered protein disaggregases acting on FET fusion proteins were reported
**in yeast** (PMID 31171724); that is a different chaperone, organism and assay category from a human
HSP90 clientship question, and it is not evidence for it. For *NR4A3* fusions specifically, the only
chaperone-adjacent record retrieved is *HSPA8* appearing as a fusion **partner** in one EMC case
(PMID 28383167) — a chaperone gene donating sequence to the chimera, which says nothing about whether
the chimera is a chaperone substrate. The comparator that shows the assay is feasible is AML1-ETO,
reported to bind the chaperonin TRiC/CCT directly through its DNA-binding domain (PMID 26706127).

**Definitional consistency.** ⚠ Binding, folding or stability dependence, fusion-specific dependence,
and a tumour-selective vulnerability are **four different claims**, and evidence for one is not
evidence for another. This paper uses *client* only for a specific physical-association or
affinity-capture observation naming the chaperone, the protein and the assay; loss of a protein
following chaperone inhibition or co-chaperone depletion is reported here as **dependence**, never as
clientship. ⛔ No single measurement settles the chaperone route: a co-immunoprecipitation supports
physical association, which may be indirect within a complex, and depletion after inhibition can
follow from altered transcription, generalized stress or cell loss. Conversely, a useful chaperone
vulnerability would not *require* direct clientship of the fusion; a downstream dependency could
matter instead.

## 5 · What these two streams do and do not support

| | Stream A says (16 EMC-labelled archival specimens) | Stream B says (91 non-EMC cancer lines) | what follows |
|---|---|---|---|
| transcriptional CDK | initiation and output-context lists read higher at nominal uncorrected significance on GPL6244; elongation and processivity lists do not; GPL3290 under interpretation hold | CDK7/CDK9 cross the dependency threshold in every screened line; small descriptive lineage-mean differences without precision | two unpaired descriptions. Neither measures an EMC dependency, and no relation between them is estimated |
| chaperone | `hsp90_machine` reads higher on GPL6244; co-chaperones directionally higher but not distinguishable from zero; HSP70 arm not distinguishable from zero in either direction | HSP90AA1/AB1 cross the threshold in a minority of lines; CDC37 in 97.8 % | two unpaired descriptions. Compensation is not identified; clientship is untested |

**The contribution of this paper is the disease-specific accounting**: which archival records exist for
EMC, what they were made to say under an explicit and reproducible scoring rule, what a public
dependency release does and does not contain for the same genes, and where the boundary of each
statement lies. The general methodological point that transcript abundance is not dependency is
background, not a result established here.

**What would be needed to say more.** A claim that abundance and dependency stand in any particular
relation needs a design that observes both in comparable units with a stated prediction and its
uncertainty. A claim of absent selectivity needs distributions, precision, an explicit estimand and an
equivalence margin, plus relevant non-cancer controls. A claim about EMC dependency needs a CRISPR or
equivalent perturbation observation in a fusion-positive EMC model. A claim of clientship needs a
binding assay in a relevant model. ⛔ None of those is performed, commissioned or simulated here.

## 6 · Update conditions

⚠ These are observations that would **update the specified hypothesis**. They are not universal
falsifiers, and none of them would retroactively invalidate a correctly reported description of the
specimens or lines actually analysed.

| # | statement, at its actual scope | what would update it, and how |
|---|---|---|
| U1 | the `cdk7_initiation_module` score is higher in the EMC-labelled arm of GSE24369 | a comparably designed independent series with adequate precision showing a null or reversed contrast would lower confidence in **generalization** and may expose heterogeneity; it would not erase this recorded contrast, and non-significance in it would not establish a null population effect |
| U2 | CDK7 and CDK9 cross the −0.5 threshold in all 91 screened lines of 24Q4, with small lineage-mean differences | a larger or better-powered panel updates **generalization** and could reveal subgroup selectivity; it cannot falsify a fixed historical description of these 91 lines, which already claims no proven absence of selectivity |
| U3 | the `hsp90_machine` score is higher in the EMC-labelled arm of GSE24369 | a comparably designed independent series reversing it would lower confidence in generalization |
| U4 | the HSP70-and-stress list gives negative estimates not distinguishable from zero | a positive contrast in a third series would revise this exploratory estimate. ⛔ It would **not** identify a standing proteostatic load or restore a causal interpretation, because this comparison never identified one in either direction |
| U5 | no qualifying binding result for a FET fusion was identified among the items inspected in the 2026-08-27 search | a published binding assay for a FET-family fusion would close the **search** question. ⛔ A finding in any FET fusion would not establish EWSR1/TAF15::NR4A3 clientship in EMC, which is a separate molecular hypothesis; the search claim and that hypothesis must be updated separately |
| U6 | HSP90 paralogue single-knockout effects are low in these lines | an adequately controlled combined perturbation could challenge a proposed combined requirement under those conditions. ⛔ Redundancy is not currently demonstrated, so there is no redundancy result to falsify |
| U7 | proliferation and other covariates are unresolved for both contrasts | a proliferation-matched or adjusted analysis would inform this. ⛔ Independence from proliferation is **not claimed** here, so a disappearing contrast would refine, not refute; changed precision and a changed sample population would need attention |
| U8 | Stream B is an uncalibrated assumption if applied to EMC | a CRISPR screen in a fusion-positive EMC model departing from the screened panel would update the transfer hypothesis for the genes, direction and controls it actually tests; it would neither generally disprove the hypothesis's usefulness as an uncertain prior nor establish disease-wide dependency |

## 7 · Limits

- **Sixteen EMC-labelled specimen records, two decade-old array platforms, uncorrected for multiple
  testing**, with different comparator arms on each, and with GPL3290 additionally under an
  interpretation hold for its reference design (§1.1).
- **A transcript score is not a protein, an activity or a dependency**, and the two streams here are
  measured in different material.
- **No EMC cell line carrying the fusion appears in the dependency release read here**, so every
  dependency figure describes other cancer lines and cannot be transferred to EMC without an
  assumption this paper does not test.
- **No claim here decides a dependency in this disease.** An unmeasured EMC dependency is unknown,
  not absent.
- **The comparator arms are other soft-tissue tumours**, so every Stream A statement is relative to
  that operationally selected comparator, not to normal tissue.
- **Ascertainment is operational.** Specimen counts are arrays under deposited labels; patient
  uniqueness and fusion confirmation are not established by them.
- **Scope of the "no exposure" statement.** No new intervention, recruitment, sampling or patient
  contact was undertaken **for this study**, and the analysis is of archival patient-derived material.
  ⛔ This is not a claim that no agent in either class has ever been given to a patient with this
  disease; no exhaustive clinical-exposure census was performed.

## 8 · Methods, data, code and reproduction limits

**Fixed versions.** Stream A values are read from `research/modalities/emc-expression-panels.json`,
produced by `research/modalities/emc_expression_panels.py`; the per-route grading is
`research/modalities/census-route-expression-grading.json`, produced by
`research/modalities/census_route_expression_grading.py`. Stream B values are read from
`research/modalities/depmap-sarcoma-dependency.json`, produced by
`research/modalities/depmap_sarcoma_dependency.py` against **DepMap public release 24Q4**
(`CRISPRGeneEffect.csv`, `Model.csv`). The EMC-line CRISPR-availability record is
`research/modalities/fet-ddr-axis-scan.json`. Class definitions and their citations are
`research/literature/txn-dependency-class-definitions-2026-08-09.json`; the chaperone-clientship
search is `research/literature/fet-fusion-chaperone-clientship-2026-08-27.json`.

⚠ **The producers were not re-run to write this paper, and that fact is not the method.** The numbers
reported here originate from those producers under the inputs named above; this manuscript is a
reading of their committed outputs. A producer that discovers "the newest available DepMap release"
at run time is **not** a specification of the 24Q4 analysis; the release label, the two input files
and the cohort rule given in §1.2 are.

**What can and cannot be reproduced from what is retained.**

| available in this repository | **not** available here |
|---|---|
| the seven curated memberships, per-platform readability, group means, Δ, Welch *t* and df | the original GEO series matrices and the probe-to-symbol mapping tables |
| deposited per-specimen annotation strings and the derived class assignments | the raw per-probe intensities and log-ratios behind each standardized value |
| the five dependency rows: means, dependent fractions, difference, `n_sarcoma`, the threshold and the lineage rule | the per-line Chronos gene-effect distributions, the non-sarcoma non-missing counts, and the DepMap input files themselves |
| the fifteen dated query strings, hit counts and curated per-record assay classifications | full texts and supplements for several cited records, and the 25 unscreened Q15 hits |

Given the retained derived summaries, the group statistics, the dependency table, and the conditional
arithmetic in §2 are reproducible exactly. ⛔ The underlying standardized scores, the classifier's
behaviour on the raw annotation text, and the DepMap per-line distributions are **not** reproducible
without the original inputs, which are not held here.

**Display items.** No figure has been rendered for this paper; its display items are the tables in the
running text.

**Artifact map.**

| what it supplies | artifact |
|---|---|
| scored expression panels per platform: memberships, per-gene readability, group means, *t*, Welch df | [`emc-expression-panels.json`](../../modalities/emc-expression-panels.json) |
| the per-route grading of the same panels | [`census-route-expression-grading.json`](../../modalities/census-route-expression-grading.json) |
| the DepMap 24Q4 rows: mean gene effects, dependent fractions, difference, `n_sarcoma`, catalogued model count, threshold and the release's own control block | [`depmap-sarcoma-dependency.json`](../../modalities/depmap-sarcoma-dependency.json) |
| the record that the one EMC-labelled DepMap model carries no CRISPR gene-effect data | [`fet-ddr-axis-scan.json`](../../modalities/fet-ddr-axis-scan.json) |
| class definitions and the background citations in the summary and §3 | [`txn-dependency-class-definitions-2026-08-09.json`](../../literature/txn-dependency-class-definitions-2026-08-09.json) |
| the chaperone-clientship search, its fifteen dated queries, their hit counts, and every record cited in §4 | [`fet-fusion-chaperone-clientship-2026-08-27.json`](../../literature/fet-fusion-chaperone-clientship-2026-08-27.json) |

## 9 · References

1. Bradner JE, Hnisz D, Young RA. Transcriptional addiction in cancer. *Cell*, 2017.
   doi:10.1016/j.cell.2016.12.013 · PMID 28187285 · <https://pubmed.ncbi.nlm.nih.gov/28187285/>
2. Kwiatkowski N, Zhang T, Rahl PB, *et al.* Targeting transcription regulation in cancer with a
   covalent CDK7 inhibitor. *Nature*, 2014. doi:10.1038/nature13393 · PMID 25043025 ·
   <https://pubmed.ncbi.nlm.nih.gov/25043025/>
3. Wang Y, Zhang T, Kwiatkowski N, *et al.* CDK7-dependent transcriptional addiction in
   triple-negative breast cancer. *Cell*, 2015. doi:10.1016/j.cell.2015.08.063 · PMID 26406377 ·
   <https://pubmed.ncbi.nlm.nih.gov/26406377/>
4. Peterlin BM, Price DH. Controlling the elongation phase of transcription with P-TEFb.
   *Molecular Cell*, 2006. doi:10.1016/j.molcel.2006.06.014 · PMID 16885020 ·
   <https://pubmed.ncbi.nlm.nih.gov/16885020/>
5. Mendillo ML, Santagata S, Koeva M, *et al.* HSF1 drives a transcriptional program distinct from
   heat shock to support highly malignant human cancers. *Cell*, 2012.
   doi:10.1016/j.cell.2012.06.031 · PMID 22863008 · <https://pubmed.ncbi.nlm.nih.gov/22863008/>
6. Schopf FH, Biebl MM, Buchner J. The HSP90 chaperone machinery. *Nature Reviews Molecular Cell
   Biology*, 2017. doi:10.1038/nrm.2017.20 · PMID 28429788 ·
   <https://pubmed.ncbi.nlm.nih.gov/28429788/>
7. Stebbins CE, Russo AA, Schneider C, *et al.* Crystal structure of an Hsp90–geldanamycin complex:
   targeting of a protein chaperone by an antitumor agent. *Cell*, 1997.
   doi:10.1016/s0092-8674(00)80203-2 · PMID 9108479 · <https://pubmed.ncbi.nlm.nih.gov/9108479/>
8. The oncogenic role of the cochaperone Sgt1. *Oncogenesis*, 2015. doi:10.1038/oncsis.2015.12 ·
   PMID 25985210 · <https://pubmed.ncbi.nlm.nih.gov/25985210/>
9. Pre-clinical efficacy of PU-H71, a novel HSP90 inhibitor, alone and in combination with bortezomib
   in Ewing sarcoma. *Molecular Oncology*, 2013. doi:10.1016/j.molonc.2013.12.005 · PMID 24388362 ·
   <https://pubmed.ncbi.nlm.nih.gov/24388362/>
10. Optimisation of pyrazolo[1,5-a]pyrimidin-7(4H)-one derivatives as novel Hsp90 C-terminal domain
    inhibitors against Ewing sarcoma. *Bioorganic Chemistry*, 2022. doi:10.1016/j.bioorg.2022.106311 ·
    PMID 36495678 · <https://pubmed.ncbi.nlm.nih.gov/36495678/>
11. Engineered protein disaggregases mitigate toxicity of aberrant prion-like fusion proteins
    underlying sarcoma. *Journal of Biological Chemistry*, 2019. doi:10.1074/jbc.RA119.009494 ·
    PMID 31171724 · <https://pubmed.ncbi.nlm.nih.gov/31171724/>
12. HSPA8 as a novel fusion partner of NR4A3 in extraskeletal myxoid chondrosarcoma. *Genes,
    Chromosomes & Cancer*, 2017. doi:10.1002/gcc.22462 · PMID 28383167 ·
    <https://pubmed.ncbi.nlm.nih.gov/28383167/>
13. Chaperonin TRiC/CCT modulates the folding and activity of leukemogenic fusion oncoprotein
    AML1-ETO. *Journal of Biological Chemistry*, 2015. doi:10.1074/jbc.M115.684878 · PMID 26706127 ·
    <https://pubmed.ncbi.nlm.nih.gov/26706127/>
14. A quantitative chaperone interaction network reveals the architecture of cellular protein
    homeostasis pathways. *Cell*, 2014. doi:10.1016/j.cell.2014.05.039 · PMID 25036637 ·
    <https://pubmed.ncbi.nlm.nih.gov/25036637/>
15. A pivotal role for heat shock protein 90 in Ewing sarcoma resistance to anti-insulin-like growth
    factor 1 receptor treatment. *Cancer Research*, 2008. doi:10.1158/0008-5472.CAN-07-3074 ·
    PMID 18676850 · <https://pubmed.ncbi.nlm.nih.gov/18676850/>

⚠ Author lists are abbreviated for records 1–7 and omitted for records 8–15, whose retained curated
records carry title, journal, year, DOI and PMID but no author string; the verbatim author strings for
records 1–7, and DOIs and retrieval dates for all of them, are in the two cited literature artifacts. Records 8–15 were read as curated extraction
records and, for records 1–3 and 5–7, as retained Europe PMC **abstracts** — not as full articles.
Data sources: GEO series **GSE24369** (GPL6244) and **GSE4303** (GPL3290); **DepMap public release
24Q4**, `CRISPRGeneEffect.csv` and `Model.csv`.

## 10 · Declarations

**Author contribution.** T.D.M. is the sole author and is responsible for the design, the analysis,
the interpretation and the manuscript.

**AI assistance.** Analysis and drafting were carried out with Claude (Anthropic) and OpenAI models
under the author's direction, and the author is responsible for the content. No AI tool is an author.
This manuscript has not been peer reviewed by a human reviewer.

**Declarations.** Funding: none. Competing interests: none. Ethics: no ethics approval was sought and
none was obtained for this analysis, and no institution or committee has determined whether any is
required. The analysis reads public archival tumour-expression series and a public cancer-cell-line
dependency release deposited by others; it involved no new recruitment, no new sampling, no clinical
intervention and no patient contact.
