---
id: DOC-EMC-TRIAL-REACHABILITY
title: Eligible but unfindable — trials that admit an ultra-rare sarcoma while listing conditions that never name it
level: L3
kind: manuscript
status: live
canonical_for: ["the 2026-08-09 EMC trial-reachability finding"]
purpose: >
  Report that patients with an ultra-rare fusion-driven sarcoma are eligible for recruiting trials
  that a condition search on their own diagnosis does not return, because eligibility is written on
  the molecular lesion while the field that search reads is written on the histology — and show that
  the obvious fix, a keyword map, is worse than no map.
scope: >
  L3. Two public trial registries — one US, one UK — read on two dates, with every candidate's
  eligibility text retrieved individually and read. Two further non-US registries refused automated
  access and a third failed at the TLS handshake; all three are reported as unread endpoints rather
  than as absences. It reports no experiment,
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
*NR4A3* fusion, most often to EWSR1, next to TAF15, and rarely to FUS, TCF12 or TFG, as a review
reports (PMID 32967265). Patients and clinicians searching for trials search the way a diagnosis is
written: by histology.

**The problem.** Trial eligibility is increasingly written the other way, on a fusion family, a
molecular class, or a translocation, while the registry's *listed conditions*, the field a
histology search matches against, continue to name the diseases the sponsor had in mind. When those
two disagree, a patient can be eligible for a recruiting trial that a condition search on their own
diagnosis does not return.

**What we did.** We read one public registry twice and a second one once, retrieving the full
eligibility text of every adjudicated candidate individually rather than trusting a fielded screen.
Two further non-US registries refused automated access, a third failed at the TLS handshake, and a
fourth went unread because our own query URL was wrong. A positive control fetched in the same run
returned normally, so the two refusals are statements about those endpoints rather than about our
retrieval; a handshake failure is not separable from a fault of our own.

**What we found.** At least two recruiting interventional trials admit this disease and neither
lists it; the candidate pool was built by keyword screens, one of which came back at its page
limit, so two is a floor. One is eligibility-defined on the FET fusion family (EWSR1, FUS, TAF15),
so on the criterion as posted it admits this disease when the fusion partner is one of those three
and not when it is TCF12 or TFG; its four listed conditions name three other sarcomas and
paediatric cancer. The other has a cohort for *translocation-associated soft tissue sarcoma*, a
class this disease belongs to; that class term is itself among its listed conditions, so the trial
is findable by the class and not by the histology, which its conditions field never names. Nine
further registry records — a molecularly-defined master screening protocol with seven of its arms,
one of those not yet recruiting, and one separate basket trial — do not name it either. One
recruiting trial does list the histology, among 42 conditions, and bounds age at 1 to 30 years at
the diagnostic biopsy, so the gap reported here is not universal. The sharpest result is an
absence, bounded by the search that measured it: a term search for the driver gene returns five
studies, none about this disease or any sarcoma, and the one cancer study among them is a surgical
cholangiocarcinoma series that mentions the gene incidentally. No trial that search returns is
indexed to this disease's driver.

**The finding that matters more than the count.** Both trials we adjudicated as *refusing* this
disease would have passed an automated keyword screen. One is titled for fusion-positive sarcoma and
then restricts to three named histologies; the other contains the exact string *extra-skeletal*
while meaning extraskeletal Ewing sarcoma. A reachability map built by keyword would have carried
both, and a map that sends a patient toward a trial that will refuse them is worse than no map at
all. Eligibility text has to be read one trial at a time.

**Why it matters.** Closing this gap needs no laboratory, no compound and no cell line. The fix is
that trials whose eligibility is molecular should list the histologies that molecular criterion
admits — a transcription where the criterion names a class, and an editorial act where it names a
gene family. Anyone building a matching tool should read criteria rather than match strings.

---

## 1 · The mechanism

A registry record has two fields that do different jobs and are written by different logic.

**Listed conditions** are the field a condition search matches. They are chosen by the sponsor and
describe the diseases the trial was designed around.

**Eligibility criteria** are what actually decides admission. Increasingly they are molecular: a
fusion family, a pathway alteration, a class of rearrangement.

For a common cancer the two coincide, so nobody notices. For an ultra-rare disease that sits inside
a molecular class, they come apart: the class is named in the criteria and the disease is not named
anywhere. The patient is inside the trial's own definition and outside its index.

## 2 · Sources and retrieval

| step | what | when |
|---|---|---|
| Registry-wide screens | fusion (400 studies, its page limit), basket (199) and sarcoma (526) screens, plus a term search on the driver gene; 1,159 unique studies indexed | 2026-08-07 |
| Per-trial eligibility | every unconfirmed candidate re-fetched individually and its criteria read | 2026-08-09 |
| Non-US registries | five endpoints attempted, one answered, with a positive control in the same run | 2026-08-09 |

The fielded screens carry no eligibility text, so they can identify a candidate and can never
confirm one; one sarcoma screen was unfielded and did carry it. Every admission and every refusal
reported below therefore rests on a per-trial retrieval, and the two refusals in §4 were only
detectable that way. The basket records in §3's third row are the exception and are not adjudicated:
eligibility text was retrieved for three of those nine, two of them individually and the third
inside the unfielded screen, so they are reported as molecularly defined and nothing more.

The earlier read carried a transport defect with two modes, and the second one bounds this paper's
coverage. The fetcher passed registry payloads through an HTML stripper, which deletes spans between
angle brackets. The registry writes comparison operators as literal `<` and `>` inside free-text
criteria, so each one opened a span the stripper closed at the next `>`. Eligibility text lost
characters, and where a deleted span crossed the JSON structure a whole record or a whole module
vanished. Twelve records were lost that way, five of them recoverable from another payload in the
same file. Three of the remaining seven came from the two condition searches on the diagnosis
itself; all three are closed studies, one completed and two terminated, so none of them changes a
count of recruiting trials. The search on the full histology name was re-run cleanly after the fix,
the same afternoon. It returned 23 studies against a reported total of 23: those three, and
NCT06239272, the one record that lists the histology, and not one of the trials §3 reports as
admitting. The search on *myxoid chondrosarcoma* was not re-run. The rule
applied at the time barred quoting any sentence that itself carried a removal marker, which left
marker-free criteria quotable. NCT05918640's eligibility text carries one such marker and was not
re-fetched after the fix, so the criterion quoted for it in §3 is the sentence the artifact records
as transport-clean rather than a re-read one. That defect has since been fixed at the fetcher.

## 3 · Records with molecular eligibility and no histology in their conditions

| trial | eligibility basis | listed conditions | EMC listed? |
|---|---|---|---|
| NCT05918640, lurbinectedin, phase 1/2, recruiting | verbatim: *Patients must have a known FET fusion (fusion that contains EWSR1, FUS, or TAF15)*. On the criterion as posted it therefore admits this disease when the partner is one of those three, and not when it is TCF12 or TFG | Ewing sarcoma · desmoplastic small round cell tumour · paediatric cancer · undifferentiated sarcoma | no |
| NCT06571734, zanzalintinib, phase 2, recruiting, target enrolment 73 | a cohort for translocation-associated soft tissue sarcoma, a class this disease belongs to; the record does not enumerate the class | all seven as retrieved 2026-08-09: metastatic leiomyosarcoma · unresectable leiomyosarcoma · bone sarcoma · translocation-associated soft tissue sarcoma · synovial sarcomas · metastatic osteosarcoma · Ewing sarcoma. The fielded screen two days earlier recorded ten; the difference is unexplained | no |
| nine further registry records: a master screening protocol, seven of its arms (one not yet recruiting) and one separate basket trial | defined by molecular alteration rather than histology, and not adjudicated: eligibility text was retrieved for only three of the nine, and whether this disease's fusion matches an open arm is a question for the trial team | various; none names this histology | no |
| NCT04151342, recruiting, target enrolment 5500 | admits by wording, rare molecular alterations | observational: it enrols the patient and does not treat them | no |

The last row is kept separate from the three above it. A reachability claim that quietly counts an
observational cohort alongside interventional trials inflates itself. Two trials admit and offer
treatment; a third admits and offers enrolment in an observational cohort. Those are counts of the
five records whose eligibility text this paper read and judged one at a time — three here and the
two refusals in §4 — not of the registry.

A term search for the driver gene returns five studies (exercise physiology, spinal-cord injury,
neck pain, and a surgical cholangiocarcinoma series) that mention the gene incidentally. Not one is
about this disease, and the one cancer study among them is a hepatic-resection series rather than a
study of the gene. That search returns whole records, so it is capped by response size rather than
page size, and no total was recorded: five is what it returned, not what the registry holds. No
trial that search returns is indexed to this disease's driver.

## 4 · The counter-finding: the cost of a keyword map

Two candidates were adjudicated as not admitting this disease, and both would have survived an
automated screen:

- one is titled for fusion-positive sarcoma and then restricts eligibility to three named
  histologies: fusion-framed and histology-limited, the exact inverse of the mechanism above;
- the other contains the literal adjective *extra-skeletal* while meaning extraskeletal Ewing
  sarcoma, a different disease that shares an adjective.

### 4.1 · Exclusion in the one non-US registry that answered

This section was drafted the other way, and the full text inverted it. The sweep was written up as
*"no non-US trial names this disease"*, which is true of the titles and false of the records. A
phase III first-line soft-tissue-sarcoma trial registered as ISRCTN07742377 names the histology in
its eligibility criteria, spelled *extra-skeletal myxoid chondrosarcoma*, in order to exclude it,
alongside desmoplastic small round cell tumour. A second trial, ISRCTN60791336, names the parent
term in its exclusion list.

This is not a criticism of that trial. Excluding a histology expected to respond poorly to the
agents under test is an ordinary and defensible design. The relevance is entirely about findability:
two queries ran there. The parent term *chondrosarcoma* returns two trials, neither of them about
this histology, and the one that mentions it does so to say no; *sarcoma AND fusion* returns one
study, a diagnostic methylome classifier rather than a treatment trial.

The mechanism therefore runs in both directions, which is the fuller result. In the three records
those two queries returned, the disease appears only as an exclusion; where trials are indexed
molecularly, it is admitted and never named. One recruiting record does both, and it bounds the
claim: NCT06239272 is a recruiting interventional trial that carries the histology among its 42
listed conditions, and its inclusion criterion is age 1 to 30 at the diagnostic biopsy rather than
at enrolment. So nothing
here says that no listing anywhere names this disease and admits it: the diagnosis search returns
this trial whatever the patient's age, and the criterion as posted admits those biopsied at 1 to 30.

A map built by string matching would have carried both. The cost of a false positive here is not a
wasted query; it is a patient or a clinician pursuing a trial that will refuse them, in a disease
where the number of options is small enough that each one carries weight.

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
  time on a second date and one more refused automated access; a third failed at the TLS handshake,
  which the positive control cannot separate from a fault of our own. The WHO portal was not reached
  because this sweep's URL was wrong, a defect here rather than a finding about that registry. A
  refusal says what an endpoint would answer, never what a registry contains, so nothing above may
  be read as those registries having been searched and found empty. The geographic scope of this
  finding is partly measured, and not shown to generalise.
- Every absence reported here is an absence from a condition search. The registry's free-text
  search reads fields beyond the conditions list: the driver-gene term search returned trials whose
  listed conditions are neck pain and spinal-cord injury. No free-text search on the disease name
  was run, so whether one would surface these two trials is untested.
- The counts here are floors. The screens that built the pool match keywords, and they search
  different fields: fusion and basket are free-text term searches, the sarcoma screen that returned
  526 is a condition search, and the unfielded sarcoma screen combines the two. The fusion screen
  came back at its page limit, so the pool is truncated, and that truncation is what makes these
  counts floors. Which fields a free-text term search covers is not established here: it reaches
  past the conditions and interventions lists, since the driver-gene search above returned trials
  that name the gene in neither. So whether a trial carrying its fusion language only in eligibility
  text could enter the pool is untested — §4's warning about instruments, pointed at this paper's
  own numerator. Of the five records adjudicated, four were re-fetched and read on 2026-08-09 —
  two admit, one of them observationally, and two refuse — and NCT05918640 was confirmed
  separately on 2026-08-07.
- Reachability here means registry indexing and nothing else. Site geography, referral route and
  centre type are separate barriers and are not measured here. Three instances are nonetheless
  visible in the records that were read. One of the two admitting trials is run by a paediatric
  centre and enrols from age 10, with no upper age limit posted; the translocation cohort requires
  that
  pathology have been reviewed at an NCCN-designated centre; and the observational cohort in §3
  recruits only at Canadian sites.
- Statuses go stale. Every status here is as posted on the retrieval date, and one of the nine, the
  basket trial NCT03767075, carried a RECRUITING flag last verified in April 2024.
- This is not a matching service and no patient was involved.

## 6 · Remedies

1. Sponsors whose eligibility is molecular should list the histologies that criterion admits in the
   conditions field. Listing the molecular class alone does not close the gap: NCT06571734 already
   lists *translocation-associated soft tissue sarcoma*, and a condition search on the histology
   still does not return it. Where the criterion names a class, a defined histology list may already
   exist in the protocol, simply sitting outside the field that search reads — though whether this
   particular protocol enumerates one, rather than leaving the class term to the investigators' own
   judgment, is not something the registry record settles (§5). Where the criterion instead names a
   gene family, no such list exists to transcribe: enumerating every histology an EWSR1, FUS or TAF15
   criterion admits is an editorial act, not a transcription. NCT07188532 shows the cost, listing
   *round cell sarcoma with EWSR1-non-ETS fusion* while §4 adjudicates it as refusing this disease.
2. Registries could index eligibility text, not only conditions.
3. Anyone building a matching tool should read criteria rather than match strings. Section 4 is the
   demonstration, with two worked examples that a string matcher gets wrong.

## 7 · Data availability

Every trial identifier, every verbatim criterion quoted, and every adjudication is in
`research/literature/fet-fusion-trial-eligibility-2026-08-07.json`,
`research/literature/emc-trial-reachability-adjudication-2026-08-09.json` and, for the non-US sweep
of §4.1 and its endpoint results, `research/literature/non-us-registry-sweep-2026-08-09.json`. All
three record the run that fetched them and the date. Only the first records a retrieval URL per
record. The adjudication file ran from an inline manifest that was never committed and names the API
base only; the non-US sweep records its workflow run, the registry names and the two queries it
sent, but no endpoint URL, so §4.1 cannot be re-fetched from the deposit alone. The URL manifests
behind the 2026-08-07 sweep are `research/literature/emc-clinical-sweep-targets.json`,
`research/literature/emc-clinical-sweep-c3.json`, `research/literature/emc-clinical-sweep-c4.json`
and, for the unfielded sarcoma screen,
`research/manuscripts/modality-census/lit-targets-frontier-capability-2026-08-07.json`;
the statuses of the three records the damaged condition searches dropped are in
`research/modalities/emc-hypoxia-therapeutic-status.json`; the stripper fix is in
`scripts/lit_fetch_urls.py`.

## 8 · Declarations

**Competing interests.** None. **Funding.** None; this work was carried out by one unaffiliated
individual using public registry data. **Ethics.** No human subjects, no patient data; every record
used is a public trial registration. **AI assistance.** The retrieval, adjudication and drafting
were carried out with substantial assistance from an AI coding agent under the author's direction,
which is disclosed rather than omitted.
