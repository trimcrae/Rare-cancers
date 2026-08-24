---
id: DOC-EMC-ICDO-9231-CLASSIFICATION
title: "One code, three diseases: what a registry cohort selected on ICD-O-3 morphology 9231/3 actually contains"
level: L3
kind: memo
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
audience: [maintainers, autonomous research agents]
date: 2026-08-23
last_verified: 2026-08-23
related: [DOC-VIEW-RT-DIAGNOSTIC-PATHWAY]
---

# One code, three diseases: what a registry cohort selected on ICD-O-3 morphology 9231/3 actually contains

> ⛔ **THIS IS A RECORD, NOT A PAPER. Closed by trimcrae, 2026-08-23: "this is not a paper.
> Document what we have, merge to main, and drop it."** It keeps its report shape because the
> findings are easier to check that way, not because it is going anywhere. It has no author block,
> no deposit declarations and no venue, and it is not in the prose-style gate's submission-text
> list.
>
> **WHY IT IS NOT A PAPER, so nobody reopens this on the strength of the number alone.** The
> measurement in section 6 is real and, as far as a bounded search could tell, unpublished. What it
> lacks is a consequence. The paper would have had to say that querying this code without a
> topography restriction is common practice — and this report's own corpus contradicts that. Of the
> registry cohorts examined here, the radiotherapy series restricted to soft connective tissue, the
> pan-sarcoma series excluded bone site codes explicitly, and the lymph node series classified by
> topography and removed 404 cases by name. Three of the four checkable cohorts restrict. The one
> that might not is a subscription article nobody here has read. So the honest reading is that the
> field already does the thing this report would have told it to do, and 32.1% prices that practice
> rather than correcting an error.
>
> **What would have to change for this to become a paper again:** evidence that the largest and
> most-cited EMC registry series did NOT restrict on topography, which needs its Methods section
> and therefore a library subscription. Absent that, the number belongs here, as a thing the next
> person designing a registry study of this disease should know.

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
Its magnitude has never been reported. We recover it from a single published cohort that supplies
both halves: of 595 records carrying morphology 9231/3 in SEER 18 for 1988 to 2015, 404 had a
soft-tissue primary and 191 a bone primary, so at least 32% of a morphology-only 9231/3 pull is
bone. Both identified biases push that figure down, and an adjustment for the one whose direction
is known gives about 38%. We do not claim that querying without a topography restriction is common
practice: of the registry cohorts examined here, most restrict explicitly, and the value of the
figure is that it prices what that restriction is worth rather than that it corrects widespread
error.

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

We report four consequences. First, three published bodies of work use 9231/3 for three
incompatible populations, and none of them misuses it. Second, registry infrastructure itself does
not agree with the soft-tissue reading. Third, the contamination this produces is bidirectional and
is already acknowledged in print. Fourth, it is large: at least a third of a morphology-only
9231/3 pull has a bone primary, a figure recoverable from a cohort already published.

## 2. Three readings of one code

### 2.1 Extraskeletal myxoid chondrosarcoma of soft tissue

The largest published registry series of EMC states its selection in one sentence: "We queried the
SEER 1973-2016 database for patients with myxoid chondrosarcoma (ICD-O-3: 9231/3)" [1]. No
topography restriction is stated in the abstract, and we have not read the Methods, so whether one
was applied is unknown to us. We flag this rather than assert it: most of the registry cohorts
examined in this report do restrict on topography explicitly, and this study is the one whose
selection we cannot check.

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

The placement is not a recent revision. SEER publishes errata documenting every update to this
list since February 2001, and we read all sixteen sheets: the two ICD-O-3 errata sets and the
fourteen site and type validation errata issued between June 2001 and July 2019 [12]. None of them
touches 9231/3. Across eighteen years of published changes the code is never added to a site
section, removed from one, or moved between them. Since the current list places it under bone, and
since a move would have had to be recorded to put it there, the skeletal placement holds across the
accrual window of every cohort discussed here. That inference rests on the errata being complete,
which the record cannot attest to about itself, and we did not read the pre-2001 base list.

One erratum is worth reporting for a separate reason. The sheet of 16 September 2002 adds, in full,
"C700-C709 ! OTHER CHONDROSARCOMA 924  9240/3 Mesenchymal chondrosarcoma" [12], extending a
chondrosarcoma morphology to meningeal topography. That is the same pairing the CBTRUS grouping
document makes in section 2.3, arriving independently from the registry that maintains the list.

One limit belongs with all of this. "Must be reviewed" is an override flag rather than a rejection,
so the list does not show that no soft-tissue 9231/3 record exists, and section 4.1 reports 459
that do. What the list establishes is that the skeletal reading of 9231/3 is not one author's
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

## 6. The magnitude

One published cohort supplies both halves of the fraction, so nothing has to be combined across
papers. The lymph node analysis of section 4.2 covers SEER 18 registries and diagnosis years 1988
to 2015, and it reports each half separately. Its Methods give the soft-tissue half: 404 patients
excluded as extraskeletal myxoid chondrosarcoma [6]. Its Table 1 gives the bone half: under
"Histologic type", "Myxoid chondrosarcoma 187 (6%) 4 (9%)", the two columns being patients without
and with regional node involvement, so 191 in total [6].

Those 191 are the myxoid cases that survived an exclusion which removed every extraskeletal one.
The study classifies site from ICD-O topography codes and retains 9231/3 on its included-morphology
list, so the cases remaining under that code are the skeletal ones. We note this step because it is
a deduction from two Methods statements rather than a printed cross-tabulation of site against
histology, which the paper does not provide.

Taking the two together, the cohort's morphology 9231/3 content is 404 soft-tissue and 191 bone
primaries, 595 in all, and the bone-primary fraction is 32.1%.

Table 1 reconciles with every total the paper prints, which is the check that this reading is
correct. Its site rows sum to 3,374 and so do its histology rows; the site totals reproduce the
2,948 skeletal and 426 extraskeletal quoted in the Results; and 4,273 minus 899 recovers the same
3,374.

We report 32.1% as a floor rather than an estimate, because both biases we can identify push it
downward. The 191 is counted after the lymph-node-status requirement, which removed 899 of 4,273
patients, while the 404 was excluded at an earlier stage; if skeletal myxoid cases lost node status
at the cohort-average rate, the pre-filter count is about 242 and the fraction about 37.5%. That
adjustment assumes equal attrition and is offered as an adjustment, not a measurement. Separately,
the order in which the remaining inclusion criteria were applied relative to the 404 exclusion is
not stated; if the 404 is the rawer of the two counts, the bone share is higher still. We have
found no bias acting in the other direction.

Two further readings would sharpen this and neither is a new study. A cross-tabulation of site
against histology for this cohort would remove the one inferred step. The baseline table of the
largest EMC registry series would give an independent replication over a different window; that
paper is a subscription article and we have not read it, and its abstract is the only part of it
cited here.

We decline to compute a second, cross-paper version of this fraction from the other counts in hand.
The 459 non-bone records of section 4.1 cover SEER 18 for 2000 to 2018, and the 791-record raw
9231/3 pull attributed elsewhere to the largest series covers 1973 to 2016 over an unstated
registry set, reaching us through a review rather than from its source [7]. A ratio spanning two
year windows and two registry coverages would look like a measurement and would not be one. It is
also unnecessary, since one study supplies both halves on matched terms.

## 7. Limitations

This report reads published cohorts and registry documentation. It does not re-analyse any
registry, and every count in it is quoted as its source printed it, with two exceptions that are
computed here from printed counts and labelled at the point of use: the 1.44% bone-primary rate in
section 4.1 and the 11.7% myxoid share in section 2.2.

The validation list read in section 3 is the April 2022 edition. We did not read earlier full
editions; the argument that its placement of 9231/3 is stable rests on the errata record, whose
completeness we cannot verify from the record itself.

The 791-record figure in section 6 reaches us at second hand. We use it only to explain why a
cross-paper ratio is not computed.

The central fraction rests on one cohort, one registry programme and one diagnosis window, and on
one step that the source does not print. It is a floor for that cohort. Whether it generalises to
other windows, other registries, or the cohorts assembled by the EMC literature specifically is not
established here, and section 6 names the reading that would test it.

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

[12] National Cancer Institute, Surveillance, Epidemiology and End Results Program. ICD-O-3 coding
materials archive: errata to the ICD-O-3 SEER site/histology validation list, sixteen sheets dated
22 May 2001 to 11 July 2019. https://seer.cancer.gov/archive/icd-o-3/
