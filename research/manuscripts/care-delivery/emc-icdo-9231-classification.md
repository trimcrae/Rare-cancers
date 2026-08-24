---
id: DOC-EMC-ICDO-9231-CLASSIFICATION
title: "One code, three diseases: what a registry cohort selected on ICD-O-3 morphology 9231/3 actually contains"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: >-
  Show that ICD-O-3 morphology code 9231/3 is used in the published literature for three mutually
  incompatible populations, that cancer registry practice and registry edit rules disagree about
  which one it denotes, and that the resulting contamination of registry-based extraskeletal
  myxoid chondrosarcoma statistics has never been measured.
scope: >-
  Classification and registry epidemiology. It reports what registry cohorts contain and what the
  coding system can and cannot distinguish. It contains no new patient data, involved no
  wet-laboratory work, and makes no statement about treatment, efficacy, safety or what any
  patient should receive.
audience: [external reviewers, collaborators, maintainers, autonomous research agents]
date: 2026-08-23
last_verified: 2026-08-23
related: [DOC-VIEW-RT-DIAGNOSTIC-PATHWAY]
---

# One code, three diseases: what a registry cohort selected on ICD-O-3 morphology 9231/3 actually contains

**Tristan D. McRae**

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com
ORCID: [ORCID TO BE SUPPLIED BY THE AUTHOR BEFORE SUBMISSION]

Running title: What a 9231/3 registry cohort contains

<!-- EDITORIAL, NOT FOR SUBMISSION.
SCOPE DECISION, trimcrae, 2026-08-23: publish the CODING half without waiting for the magnitude,
and demote the naming argument to a cited paragraph. The size is stated as an open, fully
specified query rather than answered. See systems/graph/publications.json ->
PUB-EMC-CLASSIFICATION.scope_decision. That decision fixed the SCOPE and the TITLE. It is not
authorisation to post, submit or deposit; CLAUDE.md s3 requires the paper to be named for the act.
TITLE HISTORY: this was "One code, two diseases" until the CBTRUS grouping document supplied a
third published reading. Renamed on explicit instruction, never posted under the old title.
EVERY NUMBER AND QUOTE HERE has a row in research/modalities/emc-icdo-contamination.json, which
records how each was obtained and at what provenance level: [FT] full text read, [DOC] a primary
document from the body that owns the thing described, [2o] a figure quoted from a review rather
than from its source, [API] an abstract only.
UNREAD AND SAID SO: PMID 32856598 is a subscription article; not in PMC, not open access, its
publisher PDF URL serves a JavaScript shim, its DOI and article pages return HTTP 403. Its Table 1
is the single highest-value unread object for this work and is named as such in section 6.
STILL OPEN: Table 1 of PMID 31283732, which would give the skeletal 9231/3 count directly. The
PMC article page does not inline its table cells.
NO FIGURE IS DRAWN. If a reviewer asks for one, the natural display item is a two-by-three grid of
morphology against topography with the published counts placed in the cells that have them, which
would make the empty cells the point. -->

> *Declarations for preprint deposit.* Ethics approval and consent were not required and were not
> sought: this work analyses only published literature and public registry documentation, and
> involves no human participants, no identifiable data and no patient-level records. Funding:
> none. Competing interests: none. Data and code: section 7.

> *Scope of the claims.* This is a classification and registry-epidemiology report. It asserts
> nothing about treatment, efficacy, safety, therapeutic window or clinical readiness, and makes
> no treatment recommendation, including a negative one. No count below is a patient count and
> nothing below is a diagnosis.

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare *NR4A3*-rearranged soft-tissue sarcoma.
Population-level statements about it rest almost entirely on cancer registry cohorts selected on
International Classification of Diseases for Oncology, third edition (ICD-O-3) morphology code
9231/3, "myxoid chondrosarcoma". We show that this code is used in the published literature for
three mutually incompatible populations: EMC of soft tissue, a histological subtype of
chondrosarcoma of bone, and an intracranial mesenchymal tumour of the meninges. None of the three
uses is an error. A morphology code carries no information about whether a tumour arose in bone or
in soft tissue, because ICD-O keeps that on a separate topography axis, so the ambiguity is a
property of the coding system and cannot be resolved from the morphology field. We further show
that the Surveillance, Epidemiology and End Results (SEER) programme's own site and histology
validation list takes the skeletal reading, listing 9231/3 under three bone site groups and not
under connective and soft tissue; that a published bone-tumour cohort states in its Methods that
its myxoid bucket includes EMC and then analyses it under a location variable with no soft-tissue
category; and that morphology-selected SEER sarcoma cohorts demonstrably contain bone primaries,
one study having excluded 1,668 of 115,800 retrieved records on topography. The contamination
therefore runs in both directions and is acknowledged in print by authors who tried to remove it.
Its magnitude has never been published. We show that it is reducible to a single registry query,
one half of which is already in the literature, and we state that query rather than answer it.

**Keywords:** extraskeletal myxoid chondrosarcoma; ICD-O-3; cancer registry; SEER; morphology
coding; misclassification.

## 1. Introduction

Almost everything said at population scale about extraskeletal myxoid chondrosarcoma comes from
cancer registries. The disease is too rare for prospective study of any size, so incidence,
survival, treatment patterns and prognostic factors are read from cohorts assembled by querying a
registry for an ICD-O-3 morphology code. In practice that code is 9231/3, whose ICD-O-3 rubric is
"myxoid chondrosarcoma".

The rubric does not say "extraskeletal". That single omission is the subject of this report.

ICD-O is a two-axis system. Morphology says what the tumour looks like; topography says where it
arose. Nothing in a morphology code carries site information, by design. A query on morphology
alone therefore returns every tumour assigned that morphology at any site, and a cohort so
assembled is defined by the coder's histological impression rather than by a disease entity. For
most morphology codes this is harmless, because the rubric names an entity that occurs in one
compartment. For 9231/3 it is not, because the entity it is used for in the soft-tissue literature
is defined by its extraskeletal location, and the rubric drops that word.

We report three consequences. First, three published bodies of work use 9231/3 for three
incompatible populations, and none of them misuses it. Second, registry infrastructure itself does
not agree with the soft-tissue reading. Third, the contamination this produces is bidirectional,
is already acknowledged in print, and has never been quantified.

## 2. Three readings of one code

### 2.1 Extraskeletal myxoid chondrosarcoma of soft tissue

The largest published registry series of EMC states its selection in one sentence: "We queried the
SEER 1973-2016 database for patients with myxoid chondrosarcoma (ICD-O-3: 9231/3)" [1]. No
topography restriction is stated. This is the standard construction in the EMC registry
literature, and every population-level EMC figure in common circulation descends from a query of
this shape.

### 2.2 A histological subtype of chondrosarcoma of bone

A SEER analysis of high-grade chondrosarcoma enumerates its included morphologies as "code 9220
(chondrosarcoma not otherwise specified), code 9221 (juxtacortical chondrosarcoma), code 9231
(myxoid chondrosarcoma), code 9240 (mesenchymal chondrosarcoma), code 9242 (clear cell
chondrosarcoma) and code 9243 (dedifferentiated chondrosarcoma)" [2]. Here 9231 is a subtype of a
bone tumour, sitting beside conventional and juxtacortical chondrosarcoma.

The merge is not accidental, and the paper says so. Defining its histological groups, it writes
that "myxoid chondrosarcoma: it is characterized by the formation of myxoid stroma, and includes
extraskeletal myxoid chondrosarcoma and the myxoid tumor of skull base" [2]. Eighty-seven of its
743 high-grade cases, 11.7%, carry this morphology. Its four exclusion criteria contain no
topography restriction.

The variable that could have separated the two populations reproduces the merge instead. Tumour
location is "classified as axial (including pelvic bones, sacrum, coccyx, ribs, sternum, and
vertebral columns), extremities (including bones of the upper and lower extremities) and other
group (including bones of skull, mandible, and other atypical locations)" [2]. All three
categories are defined in terms of bones. A soft-tissue EMC of the thigh, the commonest
presentation of the disease, is absorbed into a bone category or into "other atypical locations",
and cannot be recovered from the published table.

### 2.3 An intracranial tumour of the meninges

The Central Brain Tumor Registry of the United States, aligning its histology groupings with
current definitions, places 9231 twice: under "Tumors of Meninges, Mesenchymal tumors", in a list
running "8710, 8711, 8810, 8821, 8825, 8840, 9120, 9125, 9130, 9131, 9133, 9161, 9220, 9231, 9240,
9243, 9370-9372", and again under "Other neoplasms related to the meninges" [3].

This third reading is not a study's idiosyncrasy but a national registry's own grouping document.
Paired with a central nervous system topography code, 9231/3 is a CNS tumour; paired with C40 or
C41 it is a bone tumour; paired with C49 it is soft tissue. All three are correct, and the
morphology field cannot distinguish them.

## 3. Registry infrastructure takes the skeletal reading

The SEER programme publishes an ICD-O-3 site and histology validation list, whose purpose it
states plainly: "The ICD-O-3 site/type validation program was modified to allow only for the
site/histology/behavior combinations listed in this publication. All other cases must be
reviewed" [4].

In the April 2022 edition, 9231/3 appears in exactly three site sections, and all three are bone:
bones and joints excluding skull, face and mandible (C400-C403, C408-C409, C412-C414, C418-C419);
bones of skull and face (C410); and mandible (C411). It does not appear in the connective and soft
tissue section (C490-C496, C498-C499), whose osseous and chondromatous entries are 9240/3, 9242/3
and 9243/3 only [4].

We verified this absence by reading the soft-tissue section as a contiguous ordered listing rather
than by counting matches, because a line dropped in text extraction would look identical to a line
that is not there. The section runs from 9170/3 under lymphangiosarcoma directly to 9240/3 under
osseous and chondromatous neoplasms, with every group heading intact and no 918x, 919x, 922x or
923x group between them. The pattern is not specific to 9231/3: 9220/3 behaves the same way,
appearing in the three bone sections plus nasal cavity, larynx and trachea, and likewise absent
from connective and soft tissue.

Two limits belong with this observation. "Must be reviewed" is an override flag rather than a
rejection, so the list does not show that no soft-tissue 9231/3 record exists; and the edition read
is dated 2022, while the cohorts at issue accrued from 1988 and 1973 onward under earlier editions.
What the list does establish is that the skeletal reading of 9231/3 is not one author's
idiosyncrasy. It is the reading built into the registry's own validation program, and it is used
operationally by other registries: the CBTRUS alignment document above prunes its data against that
list by name, instructing that code 8771 be removed as "not in SEER site/type validation list" [3].

## 4. Bidirectional contamination, already acknowledged in print

### 4.1 Bone primaries inside morphology-selected soft-tissue cohorts

A pan-soft-tissue-sarcoma SEER analysis covering 18 registries and diagnosis years 2000 to 2018
retrieved its cohort on ICD-O-3 morphology codes and then removed bone primaries by topography:
"Exclusion criteria included STS confirmed only by autopsy or death certificate and patients with
site codes C40.0 to C42.1 (primary in bone). ... A total of 115,800 patients were retrieved, and a
total of 113,715 patients were included in the final analysis after excluding 417 patients with
only autopsy or death certificates and 1668 patients with primary bone origin" [5].

Selecting a sarcoma cohort on morphology alone therefore does pull bone-primary records. Across
all soft-tissue sarcoma morphologies the rate is 1,668 of 115,800, or 1.44%, computed here from
the study's own two printed counts. That figure is a base rate for morphology-selected sarcoma
cohorts generally, not an estimate for 9231/3, and 9231/3 is precisely the morphology where a
higher rate would be expected, since it is a chondrosarcoma code whose rubric carries no
extraskeletal qualifier.

The same study's supplementary table supplies one half of the quantity this report is about. Its
morphology list contains 9231 and no other code in the 9220 to 9243 range, and it records
"Extraskeletal myxoid chondrosarcoma, 9231, 459" [5]. Those 459 are records with morphology 9231
and a non-bone primary site, in SEER 18, 2000 to 2018.

### 4.2 Extraskeletal myxoid chondrosarcoma inside a bone cohort

The traffic also runs the other way, and one study measured part of it while trying to prevent it.
A SEER analysis of regional lymph node involvement in chondrosarcoma classified "skeletal (axial
bone, extremity bone, and bone [not other specified]) and extraskeletal (arising in site other
than bone) chondrosarcoma ... based on the International Classification of Diseases for Oncology
topography codes in the SEER database", and then reports: "We excluded 404 patients with
extraskeletal myxoid chondrosarcoma because it is a misnomer to call it a real chondrosarcoma" [6].

Its Discussion states the residual problem exactly: "We could not guarantee patients diagnosed
with extraskeletal 'Chondrosarcoma, not other specified' did not have extraskeletal myxoid
chondrosarcoma, which is not considered a chondrosarcoma, but we have tried to diminish the
potential inaccuracies by only including patients with histological confirmation and excluding
those patients with extraskeletal myxoid chondrosarcoma" [6]. Of its 3,374 included patients, 426
had an extraskeletal primary site.

This is the strongest form of the present argument, and it is not ours. A peer-reviewed registry
study removed 404 EMC cases from a chondrosarcoma cohort on topography, and then said in print
that it could not rule out more of them hiding in the cases it kept.

## 5. Constraints on the reading of a measured fraction

Two constraints belong with any future number, and we state them before one exists.

A bone primary carrying morphology 9231/3 is not automatically not EMC. Primary extraskeletal
myxoid chondrosarcoma arising in bone is a documented entity: a recent review states that EMC "may
also occur in less common sites such as the trunk, head and neck, paraspinal soft tissue, abdomen,
retroperitoneal space, and bone", citing among others a five-case study of EMC of the bone [7]. Any
measured bone-primary fraction of a 9231/3 cohort is therefore an upper bound on non-EMC
contamination, not the contamination itself.

The soft-tissue side is not pure either. A soft-tissue 9231/3 record is a registrar's morphology
assignment made from a pathology report, not an *NR4A3*-confirmed diagnosis, and registry studies
lack central pathology review [6]. The one EMC cohort we are aware of that carries no coding
ambiguity at all is a molecularly confirmed, centrally reviewed multicentre series of 67
patients [8], and it is not a registry cohort.

## 6. The closing query

The quantity that is missing is the topography split of a cohort selected on 9231/3 alone. Two
published routes would supply it, and neither requires a new study.

The first is one registry query, and one half of it is already published. A SEER query over the 18
registries, diagnosis years 2000 to 2018, on ICD-O-3 morphology 9231 with no site restriction,
divided by the 459 non-bone records reported for exactly that registry set and window [5], gives
the bone-primary fraction with matched registries, years and code. That is a single frequency
session, not a research programme. The access it requires is SEER Research data, which is granted
on an institutional email address, an application form and a data use agreement, without
institutional review board approval; the analysis client, SEER*Stat, requires Microsoft Windows.

The second is one table. The largest EMC registry series analysed primary tumour site, reporting
that there was no overall survival difference by primary site [1], so its baseline table very
probably prints the site distribution of a 439-case 9231/3 cohort. That paper is a subscription
article and we have not read it; its abstract is the only part of it cited here.

We report the two numbers now in hand side by side and decline to divide them. The 459 non-bone
records above cover SEER 18 for 2000 to 2018; the 791 records reported elsewhere as the raw 9231/3
pull cover 1973 to 2016 over an unstated registry set, and that second figure reaches us through a
review rather than from its source [7]. A ratio built from two different year windows and two
different registry coverages would look like a measurement and would not be one.

## 7. Limitations

This report reads published cohorts and registry documentation. It does not re-analyse any
registry, and every count in it is quoted as its source printed it, with two exceptions that are
computed here from printed counts and labelled at the point of use: the 1.44% bone-primary rate in
section 4.1 and the 11.7% myxoid share in section 2.2.

The validation list read in section 3 is the April 2022 edition. Earlier editions contemporaneous
with the accrual windows of the cohorts discussed have not been read.

The 791-record figure in section 6 reaches us at second hand. We use it only to explain why a
ratio is not computed.

We have not read the full text of the largest EMC registry series, for the reason given in
section 6, and we have not read the baseline table of the chondrosarcoma lymph node analysis,
whose article page does not inline its table cells.

Nothing here establishes that any patient was misdiagnosed, mistreated or miscounted in their own
care. The unit of this report is a registry record.

## 8. A note on the name

The disease's name places it inside a tumour class it does not belong to. EMC shows no cartilage
differentiation and is classified as a mesenchymal tumour of uncertain differentiation, the name
having been retained for historical reasons [9]. The suggestion that this misleads clinical
management is not new and is not ours: a combined-modality series argues that "this tumor name has
likely influenced local management patterns", that "the bone sarcoma treatment pathways do not
apply for soft tissue origins", and that radiotherapy "should not be omitted due to misconceptions
of tumor grade or extrapolations related to primary bone tumor paradigms" [10]. That claim is
asserted rather than measured, and we do not extend it.

We looked for the corresponding effect in guidance and did not find it. The National Comprehensive
Cancer Network publishes, for each of its guidelines, the list of histologies that guideline
covers. Its Soft Tissue Sarcoma guideline lists extraskeletal myxoid chondrosarcoma among its
histologies; its Bone Cancer guideline covers bone cancer, chondrosarcoma, chordoma, Ewing sarcoma,
giant cell tumour of bone and osteosarcoma, and lists extraskeletal myxoid chondrosarcoma
nowhere [11]. Two independent reviews likewise place EMC under soft-tissue sarcoma guidance
[7,9]. This is a reading of where the disease is placed, not of what the guidelines recommend for
it, and the corresponding European guideline texts are not open access and were not read.

The problem this report documents is therefore located in the research record rather than in
guidance. Registry-based statements about EMC rest on a code that three literatures read three
ways, and no published cohort has separated the populations.

## 9. Data and code

Every quotation, count and identifier in this report has a row in
`research/modalities/emc-icdo-contamination.json`, which records for each one how it was obtained
and at what level it was read, distinguishing full text from a primary registry document, from an
abstract, and from a figure quoted through a review. That artifact also records what could not be
read and why, and it carries the definition of a negative result fixed before any fraction was
sought.

## References

[1] Wagner MJ, Chau B, Loggers ET, et al. Long-term outcomes for extraskeletal myxoid
chondrosarcoma: a SEER database analysis. *Cancer Epidemiol Biomarkers Prev.* 2020;29:2351-2357.
doi:10.1158/1055-9965.EPI-20-0447

[2] Prognostic factors and treatment options for patients with high-grade chondrosarcoma.
*Med Sci Monit.* 2019;25. doi:10.12659/MSM.917959. PMID 31765367; PMC6894367.

[3] Aligning the Central Brain Tumor Registry of the United States (CBTRUS) histology groupings
with current definitions. PMID 35859542; PMC9290890.

[4] National Cancer Institute, Surveillance, Epidemiology and End Results Program. ICD-O-3 SEER
site/histology validation list, 29 April 2022.
https://seer.cancer.gov/icd-o-3/sitetype.icdo3.20220429.pdf

[5] Pan-soft tissue sarcoma analysis of the incidence, survival, and metastasis: a population-based
study focusing on distant metastasis and lymph node metastasis. *Front Oncol.* 2022.
PMID 35875111; PMC9303001.

[6] Wan L, Tu C, Li S, Li Z. Regional lymph node involvement is associated with poorer
survivorship in patients with chondrosarcoma: a SEER analysis. *Clin Orthop Relat Res.*
2019;477:2508-2518. doi:10.1097/CORR.0000000000000846

[7] From pathogenesis to the patient's bedside: a comprehensive review of extraskeletal myxoid
chondrosarcoma. 2025. PMID 41055792; PMC12504171.

[8] Chiusole B, et al. Italian Sarcoma Group series of localised, *NR4A3*-rearrangement-confirmed
extraskeletal myxoid chondrosarcoma. PMID 32572850.

[9] Extraskeletal myxoid chondrosarcoma: state of the art and current research on biology and
clinical management. 2020. PMID 32967265; PMC7563993.

[10] Extraskeletal myxoid chondrosarcomas: combined modality therapy with both radiation and
surgery improves local control. 2019. PMID 31436747; PMC7771031.

[11] National Comprehensive Cancer Network. NCCN Clinical Practice Guidelines in Oncology: Soft
Tissue Sarcoma, version 5.2026, and Bone Cancer, version 1.2027. Guideline topic listings,
https://www.nccn.org/guidelines/category_1
