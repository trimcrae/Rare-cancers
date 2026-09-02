---
id: DOC-EMC-TRIAL-REACHABILITY
title: Eligible but unfindable — trials that admit an ultra-rare sarcoma while listing conditions that never name it
level: L3
kind: manuscript
status: live
canonical_for: ["the 2026-08-09 EMC trial-reachability finding"]
purpose: >
  Report that patients with an ultra-rare fusion-driven sarcoma are eligible for recruiting trials
  that no search of their own diagnosis will ever return, because eligibility is written on the
  molecular lesion while search is written on the histology — and show that the obvious fix, a
  keyword map, is worse than no map.
scope: >
  L3. Two public trial registries — one US, one UK — read across three dates, with every candidate's
  eligibility text retrieved individually and read. Three further non-US registries refused
  automated access and are reported as refusals rather than as absences. It reports no experiment,
  no patient and no treatment outcome, and it is not clinical advice.
audience: [maintainers, external reviewers, autonomous research agents, collaborators]
date: 2026-08-09
last_verified: 2026-08-09
related: [DOC-MODALITY-CENSUS]
---

# Eligible but unfindable

> This is not medical advice and not a trial-matching service. Nothing here says any trial
> would accept any particular patient: eligibility is each trial team's decision after their own
> review, and a registry record is a summary of a protocol rather than the protocol. Nothing here
> asserts that any intervention works in this disease.

**Tristan McRae**
Independent researcher, unaffiliated.
Correspondence: trimcrae@gmail.com

---

## Abstract

**Background.** Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare sarcoma defined by an
*NR4A3* fusion, most often EWSR1::NR4A3. Patients and clinicians searching for trials search the way
a diagnosis is written: by histology.

**The problem.** Trial eligibility is increasingly written the other way, on a fusion family, a
molecular class, or a translocation, while the registry's *listed conditions*, the field a
histology search matches against, continue to name the diseases the sponsor had in mind. When those
two disagree, a patient can be eligible for a recruiting trial that no search of their own diagnosis
will ever return.

**What we did.** We read one public registry twice and a second one once, retrieving the full
eligibility text of every adjudicated candidate individually rather than trusting a fielded screen.
Three further non-US registries refused automated access and a fourth went unread because our own
query URL was wrong; a positive control fetched in the same run
returned normally, so those refusals are statements about those endpoints and not about our
retrieval.

**What we found.** Two recruiting interventional trials admit this disease and neither lists it. One
is eligibility-defined on the FET fusion family (EWSR1, FUS, TAF15), the family this disease's usual
5' fusion partner belongs to; its listed conditions are Ewing sarcoma, desmoplastic small round cell
tumour, paediatric cancer and undifferentiated sarcoma. The other has a cohort for
*translocation-associated soft tissue sarcoma*, which EMC is; that class term is itself among its
listed conditions, so the trial is findable by the class and not by the histology, which its
conditions field never names. Nine further registry records — a molecularly-defined master
screening protocol with seven of its arms, one of those not yet recruiting, and one separate basket
trial — name no histology either. The sharpest result is an
absence: a term search for the driver gene returns five studies, none about this disease or any
sarcoma, and the one cancer study among them is a surgical cholangiocarcinoma series that mentions
the gene incidentally. No trial that search returns is indexed to this disease's driver.

**The finding that matters more than the count.** Both trials we adjudicated as *refusing* this
disease would have passed an automated keyword screen. One is titled for fusion-positive sarcoma and
then restricts to three named histologies; the other contains the exact string *extra-skeletal*
while meaning extraskeletal Ewing sarcoma. A reachability map built by keyword would have carried
both, and a map that sends a patient toward a trial that will refuse them is worse than no map at
all. Eligibility text has to be read one trial at a time.

**Why it matters.** This is a gap that a paper can close, which is unusual. It needs no laboratory,
no compound and no cell line; the fix is that trials whose eligibility is molecular should list the
histologies that molecular criterion admits, and that anyone building a matching tool should read
criteria rather than match strings.

---

## 1 · The mechanism

A registry record has two fields that do different jobs and are written by different logic.

**Listed conditions** are what a search matches. They are chosen by the sponsor and describe the
diseases the trial was designed around.

**Eligibility criteria** are what actually decides admission. Increasingly they are molecular: a
fusion family, a pathway alteration, a class of rearrangement.

For a common cancer the two coincide, so nobody notices. For an ultra-rare disease that sits inside
a molecular class, they come apart: the class is named in the criteria and the disease is not named
anywhere. The patient is inside the trial's own definition and outside its index.

## 2 · Sources and retrieval

| step | what | when |
|---|---|---|
| Registry-wide screens | fusion, basket and sarcoma screens, plus a term search on the driver gene | 2026-08-07 |
| Per-trial eligibility | every unconfirmed candidate re-fetched individually and its criteria read | 2026-08-09 |
| Non-US registries | five endpoints attempted, one answered, with a positive control in the same run | 2026-08-09 |

The large screens are fields-limited and carry no eligibility text, so they can identify a candidate
and can never confirm one. Every admission and every refusal reported below therefore rests on a
per-trial retrieval, and the two refusals in §4 were only detectable that way. The basket records in
§3's third row are the exception and are not adjudicated: eligibility text was retrieved individually
for three of those nine, so they are reported as molecularly defined and nothing more.

The earlier read carried a transport defect. The fetcher passed registry payloads through an HTML
stripper, which deletes spans between angle brackets; the registry escapes comparison operators the
same way, so eligibility text containing them lost characters. The rule applied at the time was that
no sentence carrying a removal marker may be quoted, and it is why no criterion is quoted verbatim
from NCT05918640, whose retrieved eligibility text carries one such marker and was not re-fetched
after the fix. That defect has since been fixed at the fetcher.

## 3 · Trials admitting this disease without naming it

| trial | why it admits | listed conditions | EMC listed? |
|---|---|---|---|
| NCT05918640, lurbinectedin, phase 1/2, recruiting | eligibility written on the FET fusion family (EWSR1 / FUS / TAF15); EMC's usual 5′ partner is a FET protein | Ewing sarcoma · desmoplastic small round cell tumour · paediatric cancer · undifferentiated sarcoma | no |
| NCT06571734, zanzalintinib, phase 2, recruiting, n = 73 | a cohort for translocation-associated soft tissue sarcoma, which this disease is | metastatic and unresectable leiomyosarcoma · bone sarcoma · translocation-associated soft tissue sarcoma · synovial sarcoma · osteosarcoma | no |
| nine further registry records: a master screening protocol, seven of its arms (one not yet recruiting) and one separate basket trial | defined by molecular alteration rather than histology; not adjudicated, because eligibility text was retrieved individually for only three of the nine | various; none names this histology | no |
| NCT04151342, recruiting, n = 5500 | admits by wording, rare molecular alterations | observational: it enrols the patient and does not treat them | no |

The last row is kept separate from the three above it. A reachability claim that quietly counts an
observational cohort alongside interventional trials inflates itself. Two trials admit and offer
treatment; a third admits and offers enrolment in a registry.

The driver gene is absent from the index entirely. A term search for it returns five studies
(exercise physiology, spinal-cord injury, neck pain, and a surgical cholangiocarcinoma series) that
mention the gene incidentally. Not one is about this disease, and the one cancer study among them is
a hepatic-resection series rather than a study of the gene. No trial that search returns is indexed
to this disease's driver.

## 4 · The counter-finding: the cost of a keyword map

Two candidates were adjudicated as not admitting this disease, and both would have survived an
automated screen:

- one is titled for fusion-positive sarcoma and then restricts eligibility to three named
  histologies: fusion-framed and histology-limited, the exact inverse of the mechanism above;
- the other contains the literal adjective *extra-skeletal* while meaning extraskeletal Ewing
  sarcoma, a different disease that shares an adjective.

### 4.1 · Exclusion in the one non-US registry that answered

This section was drafted the other way, and the full text inverted it. The sweep was written up as
*"no non-US trial names this disease"*, which is true of the titles and false of the records. A UK
phase III first-line soft-tissue-sarcoma trial names it by its exact full name in its eligibility
criteria, in order to exclude it, alongside desmoplastic small round cell tumour. A second trial's
exclusion list names the parent term.

This is not a criticism of that trial. Excluding a histology expected to respond poorly to the
agents under test is an ordinary and defensible design. The relevance is entirely about findability:
searching that registry for this histology returns two trials, neither of them about it, and the one
that mentions it does so to say no.

The mechanism therefore runs in both directions, which is the fuller result. In the non-US registry
read here the disease appears only as an exclusion; where trials are indexed molecularly, it is
admitted and never named. One record does both, and it bounds the claim: NCT06239272 is a
recruiting interventional trial that carries the histology among its 42 listed conditions, and its
inclusion criterion is age 1 to 30 at the diagnostic biopsy rather than at enrolment. So nothing
here says that no listing anywhere names this disease and admits it: for a patient inside that age
bound the diagnosis search does return this trial, and for a patient biopsied after 30 it does not.

A map built by string matching would have carried both. The cost of a false positive here is not a
wasted query; it is a patient or a clinician pursuing a trial that will refuse them, in a disease
where the number of options is small enough that each one carries weight. Reading eligibility text
one trial at a time is the methodological content of this paper.

## 5 · Limitations

- A registry record is not a protocol. Criteria as posted are a summary, are updated at the
  sponsor's discretion, and a class term may be enumerated in the protocol in a way the registry
  never shows.
- Whether a trial team would accept this histology is their decision, not a registry fact, and
  not something this work can determine. Whether the investigators of the translocation cohort read
  their own term as a general class or as the histologies they listed is precisely the question only
  they can answer.
- Two registries, of five or more. A non-US sweep ran on the date of this draft and only one of
  five non-US endpoints answered. The EU endpoint returned an authentication error for the second
  time on a second date, and two more refused automated access. The WHO portal was not reached
  because this sweep's URL was wrong, a defect here rather than a finding about that registry. A
  refusal says what an endpoint would answer, never what a registry contains, so nothing above may
  be read as those registries having been searched and found empty. The geographic scope of this
  finding is partly measured, and not shown to generalise.
- Statuses go stale. Every status here is as posted on the retrieval date.
- This is not a matching service and no patient was involved.

## 6 · Remedies

1. Sponsors whose eligibility is molecular should list the histologies that criterion admits in the
   conditions field. Listing the molecular class alone does not close the gap: NCT06571734 already
   lists *translocation-associated soft tissue sarcoma*, and a search on the histology still does not
   return it. The information already exists in the protocol; it is simply not in the field that
   search reads.
2. Registries could index eligibility text, not only conditions.
3. Anyone building a matching tool should read criteria rather than match strings. Section 4 is the
   demonstration of why, with two worked examples that a string matcher gets wrong.

## 7 · Data availability

Every trial identifier, every verbatim criterion quoted, and every adjudication is in
`research/literature/fet-fusion-trial-eligibility-2026-08-07.json`,
`research/literature/emc-trial-reachability-adjudication-2026-08-09.json` and, for the non-US sweep
of §4.1 and its endpoint results, `research/literature/non-us-registry-sweep-2026-08-09.json`. Each
records the retrieval URL, the run that fetched it and the date.

## 8 · Declarations

**Competing interests.** None. **Funding.** None; this work was carried out by one unaffiliated
individual using public registry data. **Ethics.** No human subjects, no patient data; every record
used is a public trial registration. **AI assistance.** The retrieval, adjudication and drafting
were carried out with substantial assistance from an AI coding agent under the author's direction,
which is disclosed rather than omitted.
