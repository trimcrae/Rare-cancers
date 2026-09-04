---
id: DOC-EMC-MORTALITY-MECHANISMS-PAPER
title: "What kills patients with extraskeletal myxoid chondrosarcoma, and the survival available to tumour-directed therapy: a cause-of-death and relative-survival analysis of the published record"
level: L3
kind: manuscript
status: live
canonical_for:
  - the proportion of deaths in the published extraskeletal myxoid chondrosarcoma record that carry a stated mechanism
  - the stratified upper bound on what antitumour therapy could add to survival in this disease
  - the convergence of relative survival and registry cause attribution as independent estimates of competing mortality
  - the absence of any published growth-rate measurement for pulmonary metastases in this disease
purpose: >-
  Establish what the published record of an ultra-rare, indolent sarcoma says about how its patients
  die; bound what preventing every disease death could add to survival, by stage at diagnosis; and
  test that bound with a method that requires no cause-of-death assignment.
scope: >-
  Published cohorts, case series and case reports of extraskeletal myxoid chondrosarcoma, together
  with a national life table. A study of the published record and of measurement. It contains no new
  patient, no patient-level re-analysis, and no claim that any treatment works.
audience: [external reviewers, collaborators, maintainers, autonomous research agents]
date: 2026-08-09
last_verified: 2026-08-09
related: [DOC-EMC-TREATMENT-STRATEGY, DOC-RESPONSE-ENDPOINT-REGIME, DOC-POLICY-EVIDENCE]
---

# What kills patients with extraskeletal myxoid chondrosarcoma, and the survival available to tumour-directed therapy: a cause-of-death and relative-survival analysis of the published record

**Tristan D. McRae**

*Independent researcher.* Correspondence: trimcrae@gmail.com

*A study of the published record. No patient was recruited, no patient-level record was re-analysed,
and no claim is made that any treatment works. Every figure below is computed from counts and
survival percentages already published, or from a public national life table. Analyses were carried
out with AI assistance (see Methods).*

<!-- EDITORIAL, NOT FOR SUBMISSION.
AUTHORSHIP: affiliation and correspondence match the block in response-endpoint-indolent-tumours.md
and nr4a3-degrader-paper.md. No ORCID is given because the repository carries none; an invented
identifier on a person is the failure lint_citations.py exists to prevent, applied to a human.
Supply one at deposit if wanted.
VENUE: medRxiv as preprint, then Cancer Epidemiology. That journal takes cause-of-death, competing-
risk and descriptive rare-cancer work as primary research, which is exactly what this is. Fallbacks:
Cancers (fast open access, active sarcoma special issues) and Frontiers in Oncology, Sarcoma section.
Not JNCI: the sibling manuscript on response endpoints already targets it.
STATUS: the two-compartment host-factor arithmetic and the supportive-care effect transfer are NOT
in this paper. The host-factor model has now run on retrieved effect sizes (2026-09-04,
research/manuscripts/emc-host-factor-model.json: three factors modelled in compartment B, every
sarcoma-specific estimate recorded at zero as association-only); the supportive-care transfer still
has none. Writing the host-factor band in is a queued item, not a done one. Section 4.3 states the
implication qualitatively and stops there, which is the honest boundary. -->

## Abstract

**Background.** Extraskeletal myxoid chondrosarcoma is an ultra-rare translocation sarcoma with a
protracted course: reported ten-year disease-specific survival is approximately 85 per cent, while
30 to 50 per cent of patients develop distant metastases, mostly pulmonary. Research effort in this
disease is directed almost entirely at preventing death from the tumour. How often patients die of
the tumour, and by what mechanism, has not been described.

**Methods.** Six hundred open-access publications matching the disease were enumerated through
Europe PMC and 328 full texts retrieved. Sentences containing a death cue were extracted mechanically
and classified by reading, with the patient rather than the sentence as the unit; papers not about
this disease were excluded, leaving 34. Cause-of-death splits reported on identical patients were
extracted from a national registry cohort. Relative survival was computed under the Ederer II
convention against a World Health Organization life table for the United States, matched to the
cohort median age and sex ratio. Every quoted figure is asserted against its source artifact
programmatically, and the analysis code and data are public.

**Results.** Of 52 deaths described in the disease's open-access literature, 15 (28.8 per cent)
carried any stated mechanism. Among those 15, death from a competing cause or a second malignancy was
the largest category (6 deaths, 40 per cent), exceeding respiratory failure (3 deaths), and one of the
three respiratory deaths followed tumour-embolic ischaemic stroke rather than pulmonary tumour
burden. In the national registry cohort, deaths not attributed to the sarcoma comprised 30.8 per cent
of deaths in localised disease (4 of 13) and 10.0 per cent in disease metastatic at diagnosis (1 of
10). The corresponding upper bound on what preventing every disease death could add was 6.7
percentage points of survival in localised disease and 31.0 points in metastatic disease at a median
follow-up of just over three years. Relative survival, which assigns no cause to any patient, gave a
median competing share of 23.0 per cent across eight series-horizons, against 21.7 per cent from the
cause split; the two methods share no input. Observed non-sarcoma deaths matched background mortality
for the cohort's age and sex (ratios 0.97 and 1.04, on four and one events). No publication reporting
the growth rate of pulmonary metastases in this disease was found.

**Conclusions.** The published record of this disease cannot say how most of its patients die. What it
does say is that a substantial minority of deaths are not caused by the sarcoma, that this fraction is
large in localised disease and small in metastatic disease, and that the survival available to
antitumour therapy is correspondingly concentrated in the metastatic stratum. Two independent methods
agree on the size of the competing fraction. These findings bound what tumour-directed research in
this disease can achieve and identify a second, unaddressed population of deaths.

## 1. Introduction

Extraskeletal myxoid chondrosarcoma is defined by rearrangement of *NR4A3*, most often as an
*EWSR1::NR4A3* fusion. It is ultra-rare, with an incidence well under one per million per year, and
its course is unusually protracted: patients recur and metastasise late, and survival with metastatic
disease is measured in years rather than months.

Almost all translational work in this disease is directed at the tumour. That is reasonable, and it
carries an assumption nobody has examined: that the event research is trying to prevent, death caused
by the sarcoma, is the event that actually occurs. For a disease whose reported ten-year
disease-specific survival is approximately 85 per cent, in patients most often diagnosed in their
fifties and sixties, the assumption is not self-evident. If a meaningful share of deaths after
diagnosis are not caused by the sarcoma, then the survival available to any antitumour therapy is
smaller than overall survival curves suggest, and a second population of deaths exists that no
tumour-directed approach addresses.

Answering this requires knowing what patients die of, which requires the literature to have recorded
it. This study asks three questions in order: how often the published record states a mechanism of
death; what fraction of deaths are attributed to the disease when a cohort reports both; and whether
a method that requires no cause-of-death assignment agrees.

## 2. Methods

### 2.1 Corpus

Publications were enumerated through the Europe PMC REST interface using a disease query spanning the
condition's alternative names, restricted to records with open-access or Europe PMC full text. Six
hundred records were enumerated and full text retrieved for 400, of which 328 returned parsable text.
Reference lists, tables and figures were removed before analysis, because bibliographies contain other
papers' titles carrying death terms.

Sentences containing a death cue were extracted by pattern. The pattern is
recall-oriented by design: it retains negative statements and methodological definitions, because a filter tuned
to exclude them would also exclude unusual terminal events, which are the observations of interest.
No cause was assigned by pattern at any point.

### 2.2 Inclusion and classification

Of 162 papers carrying at least one death sentence, 34 have the disease in their title. The remainder
match because the disease appears in a differential diagnosis or a citation, and their deaths belong
to other diseases' patients; all analyses are restricted to the 34.

Classification was performed by reading each sentence with its paper's context, and assigning one of:
respiratory failure, locoregional complication, visceral metastasis complication, treatment-related
death, competing non-cancer death, second malignancy, death from progressive disease without a stated
mechanism, mechanism unstated, or not a patient death.

The unit of analysis is a patient or a reported patient group, never a sentence. One paper describes
three deaths across seven sentences and another describes one death in four; counting sentences would
have inflated the total roughly threefold and weighted the most verbose reports most heavily.

### 2.3 Cause splits and the upper bound on antitumour benefit

Where a cohort reported both deaths attributed to the sarcoma and deaths attributed to other causes on
identical patients, the competing share was computed as a direct ratio of counts. This requires no
survival curve, no pairing across populations and no subtraction of summary percentages.

The upper bound on antitumour benefit, referred to below as the ceiling, is the disease-specific
mortality present in a cohort: the survival that preventing every death from the sarcoma would add.
It is an upper bound on all tumour-directed therapy taken together, not on any single agent.
Binomial proportions carry Wilson intervals.

### 2.4 Relative survival

Relative survival was computed as observed all-cause survival divided by the survival expected for a
general population of the same age and sex, under the Ederer II convention, using age-specific death
rates from the World Health Organization Global Health Observatory for the United States. Expected
survival was computed for a synthetic cohort at the median age at diagnosis and the reported sex
ratio, and survival across a rate band of width *w* at rate *m* was taken as exp(−*mw*).

This method attributes excess mortality to the disease without assigning a cause to any individual,
which is the point: it is independent of the cause-split described above and shares none of its
inputs. Series with relative survival at or above 0.99 were excluded from the pooled band, because the
competing share then divides a near-zero excess by a small all-cause mortality and becomes numerically
unstable; exclusions are reported individually.

### 2.5 Reproducibility and the use of AI assistance

All analysis code, input specifications and output artifacts are public. Every survival figure is
declared with the verbatim string it was read from and checked programmatically against its source, so
a corrected source figure fails the build rather than leaving a stale number. Every classified death
carries its verbatim sentence and identifier, checked against the retrieval artifact before any tally
is produced.

Analyses were carried out with AI assistance. Retrieval, arithmetic and consistency checking were
performed by software; the classification of each death, the inclusion decisions and the
interpretation are the author's. Two errors found during the work are recorded in Appendix A, because
both changed a headline figure.

## 3. Results

### 3.1 Statement of a mechanism in the published record

Fifty-two deaths were described across 16 of the 34 papers. Fifteen (28.8 per cent) carried a stated
mechanism. Twenty-eight were recorded with no mechanism beyond a vital status, and a further eight
were attributed to progressive disease without further specification.

**Table 1.** Deaths in the open-access literature of this disease, by stated mechanism.

| category | deaths |
|---|---:|
| mechanism unstated | 28 |
| progressive disease, mechanism unspecified | 8 |
| respiratory failure | 3 |
| competing non-cancer cause | 3 |
| second malignancy | 3 |
| locoregional complication | 2 |
| visceral metastasis complication | 2 |
| treatment-related | 2 |
| ambiguous | 1 |
| **total** | **52** |

This is the study's first result rather than a limitation of it. A research programme directed at
preventing a specific event cannot, from its own literature, describe that event in most of the
patients it has recorded.

### 3.2 Competing causes and second malignancies

Among the 15 deaths with a stated mechanism, six were from a competing cause or a second malignancy,
exceeding any disease-specific mechanism. These recur across independent reports: two patients died of
concurrent malignancies within months of diagnosis in one series; a patient followed for 126 months
with metastatic disease died of unresectable colon cancer; two of sixteen collected intracranial cases
died of causes the reviewing authors judged unrelated; and one patient died of cerebral haemorrhage at
9.5 years with no tumour recurrence.

Case reports over-select the notable, so this is a description of what was recorded and not an
incidence. Its direction is nevertheless the same as the registry result below, which is not subject
to case-report selection.

### 3.3 Respiratory failure, and the distinction from metastatic site

Three deaths were attributed to respiratory failure or to lung metastases. One followed tumour-embolic
ischaemic stroke treated by thrombectomy, with death 15 days later, rather than progressive pulmonary
tumour burden.

This distinction matters because the pulmonary dominance of this disease's metastatic pattern is well
established and is easily transposed into an assumption about how patients die. The site of metastasis
and the mode of death are different claims, and the present corpus supports the first without
establishing the second.

### 3.4 The antitumour ceiling, and its dependence on stage

One national registry cohort reported both cause counts on identical patients.

**Table 2.** Cause of death and the ceiling on antitumour benefit, by stage at diagnosis.

| stratum | n | disease deaths | other-cause deaths | competing share | ceiling |
|---|---:|---:|---:|---:|---:|
| localised, surgically treated | 134 | 9 | 4 | 30.8 % | **6.7 points** |
| metastatic at diagnosis | 29 | 9 | 1 | 10.0 % | **31.0 points** |
| combined | 163 | 18 | 5 | 21.7 % | 11.0 points |

At a median follow-up of just over three years, preventing every death from the sarcoma in the
localised cohort would have added 6.7 percentage points of survival; in the cohort metastatic at
diagnosis it would have added 31.0. The value available to tumour-directed therapy is concentrated in
the stratum that is the minority of patients.

The same cohort reported that distant metastasis was associated with death from the tumour on
multivariate analysis, with an odds ratio of 26.26 (95 per cent CI 2.99 to 231.04), while local
recurrence was not associated with tumour mortality. The confidence interval is very wide on a small
number of events.

### 3.5 Agreement between two independent estimates

Relative survival gave a median competing share of 23.0 per cent across eight series-horizons (range
12.1 to 45.4), against 21.7 per cent from the registry cause split. The two share no input: one is
published all-cause survival divided by a national life table, the other is counts of patients a
registry assigned a cause to, and neither can be derived from the other.

One series was excluded from the band with relative survival of 0.9925, and one horizon of the same
series produced relative survival above 1, meaning the cohort out-lived the general population. That
is a selection signal in a 42-patient cohort reporting 100 per cent five-year survival, not a property
of the disease.

### 3.6 Non-sarcoma deaths occur at background rate

Observed deaths not attributed to the sarcoma were compared against a life table matched on age and
sex, at each cohort's own follow-up: 3.0 per cent observed against 3.1 per cent expected in the
localised stratum (ratio 0.97, 95 per cent CI 0.38 to 2.41) and 3.4 against 3.3 per cent in the
metastatic stratum (ratio 1.04, 95 per cent CI 0.18 to 5.18).

These rest on four events and one event respectively. What they establish is consistency with
background mortality, not equality to it. The comparison is also one-sided: a general-population life
table overstates background mortality for a cohort fit enough to reach and survive a sarcoma
diagnosis, so it can refute the proposition that the gap is ordinary background mortality and cannot
prove it. It did not refute it.

### 3.7 Absence of a growth-rate measurement for pulmonary metastases

A targeted search for the natural history, growth rate or doubling time of pulmonary metastases in
this disease returned zero records. Whether repeated local treatment of lung metastases can keep pace
with their progression depends on that rate, and it has not been measured.

## 4. Discussion

### 4.1 What this bounds

Preventing every death caused by the sarcoma in the localised cohort would have added 6.7 percentage
points of survival at three years. This is an upper bound on all tumour-directed therapy taken
together, and no agent achieves an upper bound. It does not argue against developing such therapy: in
metastatic disease the same calculation gives 31.0 points, and that is where the value is.

What it does argue against is a portfolio that regards all stages as one target. The stratum with most
patients has least to gain, and the stratum with most to gain is a minority.

### 4.2 What this says about the evidence base

That fewer than a third of recorded deaths carry a stated mechanism is a finding about the literature
rather than the disease. It has a practical consequence: every disease-specific survival figure in
this disease rests on somebody having assigned a cause by an instrument no paper reports. The relative
survival analysis was performed because it does not need that assignment, and its agreement with the
cause split provides evidence that the assignment, where made, is not badly wrong.

For ultra-rare cancers generally, the implication is that cause-of-death recording, which costs
nothing at the point of follow-up, determines whether a disease's evidence base can support the
questions its research programme asks.

### 4.3 The population no tumour-directed approach addresses

Between a fifth and a third of deaths after diagnosis are not caused by the sarcoma, and they occur at
approximately the rate the cohort's age and sex predict. Two consequences follow, and only the first
is established here.

Established: the ceiling on antitumour benefit is correspondingly reduced, most severely in localised
disease.

Not established, and stated as a direction rather than a result: if these deaths occur at
general-population rates, then interventions that reduce general-population mortality would be
expected to apply, with a weaker transportability assumption than any tumour-directed therapy
requires, because the deaths in question are not cancer deaths. Quantifying that requires effect sizes
this study did not retrieve, and this disease itself has no outcome data on supportive or host-directed
care in either direction.

One class of supportive intervention does have direct randomised evidence elsewhere in oncology, and
it is the only non-antitumour intervention class with a reported overall-survival benefit in cancer at
all: early specialist palliative care integrated alongside standard oncologic care. The finding
replicates rather than resting on one trial. In metastatic non-small-cell lung cancer, median overall
survival was longer with early palliative care than with standard care alone in the founding trial
(11.6 vs 8.9 months, p=0.02, PMID 20818875), and in two independent replications conducted in
different health systems: a Mexican trial (18.1 vs 10.5 months, HR 1.5 [95% CI 1.04-2.3], p=.030,
PMID 38558247) and a Chinese trial (HR 0.19 [95% CI 0.04-0.85], p=0.029, PMID 37781179). An earlier
evidence synthesis found the survival claim resting on a thin base -- two studies -- before these two
replications existed (PMID 32953543). Every one of these trials is in non-small-cell lung cancer, a
disease whose median survival is measured in months; EMC's natural history is measured in decades, a
population none of these trials enrolled and a transfer no trial has tested. Whether an effect
measured over months of survival extends over a course of years, through what mechanism, and whether
a sarcoma-specific trial of this intervention exists at all, are left here as open questions rather
than assumed answers: a title-level search of the corpus retrieved for this class of intervention
found no sarcoma-specific palliative-care trial.

### 4.4 Lung-directed treatment

Pulmonary metastasis is the dominant distant pattern in this disease, and both surgical
metastasectomy and ablative local therapies are established options in sarcoma more broadly. The
present corpus does not, however, establish respiratory failure as the dominant mode of death, so this
study cannot support prioritising lung-directed treatment on mortality-mechanism grounds. The absence
of any growth-rate measurement (3.7) is the more immediate obstacle: whether repeated local therapy
can outpace this disease's pulmonary progression is unknown, and it is answerable from serial imaging
already held by treating centres.

## 5. Limitations

Open-access full text is a convenience sample: 328 of 600 enumerated records were retrieved, and
non-open-access series are systematically older and larger. Case reports are written because a case
was notable, over-representing unusual terminal events; this biases against the indolent,
competing-cause picture the data nevertheless show. Counts of described patients have no denominator
and support no rate.

The cause split rests on 13 and 10 deaths in two strata of one registry, at a median follow-up of
just over three years, which is short relative to this disease's natural history. Follow-up censors
the two causes unequally: competing deaths accrue immediately while sarcoma deaths continue to accrue
for decades, so short follow-up flatters the competing share. The ceiling figures are therefore lower
bounds on the eventual disease mortality and the competing share is an upper bound at that horizon.

Relative survival was applied to published summary survival with a cohort median age and sex ratio
rather than patient-level data, so the expected-survival term is that of a synthetic cohort rather
than a true Ederer II match. A single national life table for one country and year was applied to
cohorts from five countries across five decades. Excess mortality attributes to the disease any
elevation in other-cause mortality among its patients, including treatment-caused death, which the
cause split counts separately.

Where a paper judged a death unrelated to the sarcoma, that is the paper's judgement, made by an
instrument it does not report.

## 6. Conclusion

The published record of extraskeletal myxoid chondrosarcoma does not say how most of its patients die.
Where it does, deaths from competing causes and second malignancies are the largest identifiable
category, and respiratory failure, though present, is not dominant. Between a fifth and a third of
deaths after diagnosis are not caused by the sarcoma, a figure two independent methods agree on, and
those deaths occur at approximately background rate. The survival available to antitumour therapy is
6.7 percentage points in localised disease and 31.0 in metastatic disease at three years. Research
prioritisation in this disease should reflect that difference, and cause-of-death recording should be
treated as a measurement that determines what its evidence base can answer.

## Appendix A. Corrections made during this work

Both corrections changed a headline figure and are recorded because the superseded values were
circulated internally before they were withdrawn.

**A.1 Competing share, 39.4 per cent superseded by 21.7 per cent.** The first estimate paired a
survival-curve reading against a crude death proportion from a different cohort. When one registry's
own cause counts on identical patients became available, the direct ratio replaced it. The direct
estimator has none of the weaknesses the first disclosed, and the change is a change of method rather
than a correction of arithmetic.

**A.2 Background mortality, 2.4 per cent superseded by 11.3 per cent at ten years.** The life-table
fetch treated the World Health Organization indicator nMx as a five-year probability. It is an
age-specific death rate, and survival over a band of width *w* is exp(−*mw*). The error understated
background mortality roughly fourfold and would have attributed nearly every death to the sarcoma. It
was caught because the resulting figure was implausibly low for a cohort at this age, and confirmed
from the indicator's published name rather than by inspection of which value looked right.

## Data and code availability

All analysis code, input specifications, retrieval artifacts and outputs are available in the
project repository. The retrieval artifacts record every query verbatim with its hit count, so both
positive findings and absences can be reproduced or refuted.
