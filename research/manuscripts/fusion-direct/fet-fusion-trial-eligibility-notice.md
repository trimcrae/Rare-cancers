---
id: DOC-FET-FUSION-TRIAL-ELIGIBILITY-NOTICE
title: FET-fusion trial eligibility — live re-verification and a draft patient/clinician notice
level: L3
kind: memo
status: live
canonical_for: ["the 2026-08-07 live re-verification of the section 3.3 trial set", "the draft FET-fusion eligibility notice awaiting review"]
purpose: >
  Section 3.3 of emc-unexplored-treatment-lanes.md found an open trial whose eligibility is
  fusion-defined rather than histology-defined, and whose listed conditions therefore hide it from
  every EMC patient searching by diagnosis. It called the fix "a paragraph, not a grant." This
  document (a) re-verifies every NCT number in that section against a live registry read performed
  today, (b) widens the search for other trials with the same shape, and (c) carries the draft
  paragraph and the reviewer block it must pass through before it goes anywhere.
scope: >
  L3. `status: live` describes THIS DOCUMENT, which is a finished record of a completed
  verification; the notice it carries in section 4 is an UNPUBLISHED DRAFT awaiting the review in
  section 5, and the two must not be confused. NOTHING HERE HAS BEEN SENT, PUBLISHED OR SHOWN TO
  ANYONE. This document grades no route and re-derives no result; it records registry reads and
  drafts prose from them.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-08-07
last_verified: 2026-08-07
related: [DOC-EMC-UNEXPLORED-LANES]
---

# FET-fusion trial eligibility — live re-verification and a draft notice

> ⛔ **NOT MEDICAL ADVICE, AND NO EFFICACY CLAIM IS MADE ANYWHERE IN THIS DOCUMENT.** Nothing here
> asserts that any listed treatment works in EMC, is safe in EMC, or has a therapeutic window in
> EMC. What is recorded is what a public trial registry said about who each trial will consider,
> at a stated moment. **Eligibility for any trial is determined by that trial's own team, never by
> this document.**

> ⛔ **NOTHING IN THIS FILE HAS BEEN SENT OR PUBLISHED.** Section 4 is a draft; section 5 is the
> review block that must clear before it is shown to anyone outside this repository.

**All registry data:**
[`fet-fusion-trial-eligibility-2026-08-07.json`](../../literature/fet-fusion-trial-eligibility-2026-08-07.json)
— the single home for every status, date, age bound, condition list and verbatim criterion below.
Figures are not re-typed here beyond what the prose needs; the artifact is authoritative.

---

## 1 · How these readings were taken, and why that matters

The dev sandbox egress proxy returns **403 on CONNECT for `clinicaltrials.gov`**, so no registry
read is possible here. Every reading below was taken on a GitHub-hosted runner
(CLAUDE.md §6) by dispatching the on-`main` `fetch-literature.yml` workflow with `ref=main` and a
`targets_file` naming an on-`main` URL manifest. Four runs, all on **2026-08-07**:

| slug | manifest | Actions run | URL-fetch window (ET) |
|---|---|---|---|
| `ct-reverify-sweeptargets-2026-08-07` | `emc-clinical-sweep-targets.json` | `31175763521` | 7:55:13–7:55:43 AM |
| `ct-reverify-frontier-2026-08-07` | `lit-targets-frontier-capability-2026-08-07.json` | `31176517524` | 8:07:15–8:08:29 AM |
| `ct-reverify-c3b-2026-08-07` | `emc-clinical-sweep-c3.json` | `31176811772` | 8:11:48–8:12:18 AM |
| `ct-reverify-c4b-2026-08-07` | `emc-clinical-sweep-c4.json` | `31179088283` | 8:44:00–8:44:25 AM |

### 1b · ⚠ The transport corrupts free text, and one of its two failure modes is silent

This is the most important methodological finding of the exercise, and it applies to **every**
registry read this repository has taken through this path.

`scripts/lit_fetch_urls.py` puts every payload through `strip_html()`, whose
`re.sub(r"(?s)<[^>]+>", " ", raw)` **deletes the span from a `<` to the next `>`**.
ClinicalTrials.gov writes comparison operators as **literal** `<` and `>` inside free-text criteria,
so any criterion containing one loses everything up to the next `>`. Measured in the
LIFFT record itself: `"(age \>16 years) or Lansky of at least 70 (age \ one week since last
dose…"` — a whole clause gone, in a record that parsed perfectly.

Two failure modes, and they are not equally dangerous:

- **LOUD** — the deleted span crosses JSON structure and the record stops parsing. Easy to see.
  **Ten distinct trial records** across five payloads (13 payload instances); the NCT ids are
  listed per payload in the artifact under `unparseable_records`.
- **SILENT** — the record still parses **while whole modules have vanished**. `NCT05836571`'s
  per-study fetch parsed cleanly and carried **no `conditionsModule`, no `designModule` and no
  `eligibilityModule` at all**. A reader trusting "it parsed" would have recorded an EMC-listing
  trial as having no listed conditions.

⛔ **So "the payload parsed" is not evidence that the payload is complete** — the same shape as
CLAUDE.md §4's rule that a populated field is not a measured one. Three rules were applied and are
enforced in the artifact rather than described:

1. Every unfielded record is asserted to carry `identificationModule`, `statusModule`,
   `conditionsModule`, `designModule` and `eligibilityModule`; absences are recorded as
   `silently_damaged_records`, not silently accepted.
2. **No eligibility sentence is quoted anywhere unless that sentence itself carries no removal
   marker.** Every quote in section 4 passed that check.
3. Structured fields are backfilled from a second payload when the first is damaged, with the
   donor named in `fields_backfilled_from_another_payload`.

---

## 2 · Task 1 — re-verification of every NCT number in §3.3

**Result: all nine re-read live; no status differs from what §3.3 records.** Three things are worth
recording anyway, because each would have been invisible in a bare "no change".

| NCT | status read 2026-08-07 | sponsor last verified | note |
|---|---|---|---|
| `NCT05918640` (LIFFT) | RECRUITING | 2026-03 | FET-fusion criterion re-read verbatim and transport-clean |
| `NCT06239272` (NRSTS2021) | RECRUITING | 2026-07 | EMC an explicitly listed condition |
| `NCT05722886` (DETERMINE) | RECRUITING | 2026-06 | |
| `NCT03767075` (Basket of Baskets) | RECRUITING | 2024-04 | ⚠ **stale record** — see below |
| `NCT04040205` (abemaciclib) | RECRUITING | 2026-07 | |
| `NCT01659203` (proton/photon RT) | RECRUITING | 2026-07 | |
| `NCT05836571` (ipi/nivo ± cabo) | ACTIVE_NOT_RECRUITING | 2026-04 | as §3.3 states |
| `NCT03600649` (seclidemstat) | UNKNOWN | 2023-11 | as §3.3 states; EMC explicitly listed |
| `NCT04305548` (trabectedin) | RECRUITING | — | condition list is Mesenchymal Chondrosarcoma only, as §3.3 states |

- ⚠ **`NCT03767075`'s RECRUITING flag is over two years stale.** The sponsor last verified the
  record in **April 2024**. A registry status is a sponsor's assertion with a date attached, and
  "RECRUITING as of 2024-04" is a materially weaker statement than "RECRUITING as of 2026-07".
  The draft notice says so explicitly rather than listing it flatly beside the others.
- ✅ **`NCT06239272`'s "ages 1–30" is right, but not where you would look for it.** The structured
  `minimumAge` field is **absent**; only `maximumAge: 30 Years` is populated. The lower bound comes
  from the criterion text — *"Patients must be 1-30 years at the time of the biopsy that
  established the diagnosis of NRSTS."* — which was retrieved transport-clean. Anyone re-deriving
  the age range from structured fields alone would get "up to 30" and no floor.
- ⚠ **"EMC-eligible" is doing different work in different rows of §3.3, and reading the list flatly
  would mislead a patient.** Of the five §3.3 calls "also verified open and EMC-eligible", only
  **`NCT06239272`** names EMC in its own condition list. **`NCT01659203`** is listed for
  *retroperitoneal sarcoma* — it turns on tumour **location**, not on which sarcoma it is.
  **`NCT04040205`** requires a **CDK-pathway alteration** in addition to its histology list.
  **`NCT05722886`** and **`NCT03767075`** are molecular/arm-matched and name no sarcoma at all.
  This is not an error in §3.3, which was recording routes rather than writing to patients — but
  the draft in §4 separates the three reasons explicitly, because collapsing them is how a patient
  ends up asking about the wrong trial.

---

## 3 · Task 2 — widening the search for the same mechanism

The mechanism generalises as: **eligibility decided by a molecular finding, behind a listed-condition
set that a histology search for EMC will never match.** Screened across 1,159 unique studies drawn
from a recruiting-fusion search (400), a basket/tumour-agnostic search (199), a recruiting-sarcoma
search (526), an unfielded sarcoma+fusion search, registry-wide `EWSR1` and `NR4A3` term searches,
and every study whose condition list names EMC.

**Fusion-family-defined, on eligibility text that was actually read — one** (artifact key
`confirmed_fusion_family_defined`). `NCT05918640` is the only **open** trial in this sweep whose
retrieved eligibility text admits a fusion family broad enough to contain `EWSR1::NR4A3`. Every
other open EWSR1-indexed trial whose eligibility text was readable names its partners individually
— `EWSR1-FLI1`, `EWSR1-ERG`, `EWSR1-WT1` — and so does not reach it. **One trial did state it the
broad way and is closed:** `NCT05275426`, below.

**Molecularly defined rather than histology-defined — nine.** `NCT05722886` (DETERMINE) and its
seven registered treatment arms, plus `NCT03767075`. Admission turns on a genomic alteration and an
open matched arm, not on the tumour's name; the listed conditions are generic ("Solid Tumour",
"Advanced Solid Tumor"), so no EMC histology search returns them.

**Candidates that could not be confirmed — four**, and they are recorded as candidates, not as
findings: `NCT06571734` (listed condition *"Translocation-associated Soft Tissue Sarcoma"*),
`NCT07188532` (listed condition *"Round Cell Sarcoma With EWSR1-non-ETS Fusion"*), `NCT06094101`
(PerVision, *"Fusion+ Sarcoma"*), `NCT04151342` (CARMA, observational). For two the eligibility text
was corrupted in transport; for two the payload was fields-limited and carried none. **None of them
appears in the draft notice**, because a trial named to a patient must rest on eligibility text that
was actually read.

**Screened and excluded — three**, on the retrieved eligibility text: `NCT07695311` and `NCT07328425`
require named partner fusions EMC does not carry. `NCT05275426` is the clearest *second* instance of
the mechanism — its criteria explicitly admitted *"sarcomas with a rearrangement between EWSR1 and a
non-ETS family gene"*, behind a condition list reading only "Ewing Sarcoma; Ewing-Like Sarcoma" — but
its status is **COMPLETED**, so it is a closed illustration, not a route.

### ⭐ 3b · The registry has no index entry for EMC's driver gene

A registry-wide term search for **`NR4A3` returns five studies and not one is an oncology study** —
they are exercise-physiology, spinal-cord-injury, neck-pain and biliary-surgery trials that mention
the gene incidentally. The gene that defines EMC is, as a search key, empty. This is the §3.3
thesis stated at its strongest: the indexing that would connect an EMC patient to a fusion-defined
trial does not exist in either direction.

### 3c · What this screen cannot claim

- The registry-wide `EWSR1` search returns **full** records, so the API caps it by response size
  rather than by `pageSize`: seven studies came back for `pageSize=100`. It is a sample, not an
  enumeration.
- The large screens are fields-limited and carry no eligibility text, so they can raise a candidate
  and never settle one.
- Non-US registries are not covered: the EU CTIS endpoint in the manifest returns
  `403 {"message":"Missing Authentication Token"}`.
- Closing the four open candidates needs one more per-NCT registry read, which needs a new URL
  manifest on a ref CI can check out. This session was instructed not to push, so that read has not
  been taken — it is the one item here blocked on something outside the session.

---

## 4 · DRAFT — the notice §3.3 asks for

> ⛔ **DRAFT. NOT SENT, NOT PUBLISHED, NOT SHOWN TO ANY PATIENT OR CLINICIAN.** Requires the
> review in section 5 first.

---

**If you have extraskeletal myxoid chondrosarcoma (EMC), at least one open clinical trial will not
appear in a search by your diagnosis.**

Most trial searches match on the tumour's name. Some trials decide who can take part by the
tumour's **fusion gene** instead. In EMC the fusion always involves the NR4A3 gene, and its partner
is **EWSR1 in more than 70% of cases and TAF15 in about 20%**, with FUS among the rarer partners
(Stacchiotti *et al.*, *Cancers* 2020;12(9):2703; PMID 32967265). EWSR1, TAF15 and FUS are the three
**FET-family** genes, so the large majority of EMC tumours carry a FET-family partner. A trial that
admits patients on that basis can accept someone with EMC even though EMC appears nowhere in the
trial's listed conditions, and that is exactly why a search by diagnosis never returns it.

The clearest current example is **NCT05918640 (LIFFT)**, a phase 1/2 study of lurbinectedin run by
the Children's Hospital of Philadelphia. It was listed as **recruiting** when the registry was read
on **7 August 2026**. Its phase 1 inclusion criterion reads, word for word: *"Patients must have a
known FET fusion (fusion that contains EWSR1, FUS, or TAF15) as documented by next generation
sequencing, polymerase chain reaction (PCR) or Fluorescence in situ hybridization (FISH)."* The
minimum age is 10, and it is for a solid tumour that has come back or not responded after first
treatment. Its listed conditions are Ewing sarcoma, desmoplastic small round cell tumour,
paediatric cancer and undifferentiated sarcoma — EMC is not one of them. **One detail matters and is
easy to miss: it is the trial's *phase 1* part that is defined this way. Its phase 2 part requires a
diagnosis of Ewing sarcoma with a confirmed EWS-FLI1 fusion**, so it is the phase 1 part that is
worth asking about.

Two more trials choose patients by molecular test result rather than by tumour name, so they are
also invisible to a diagnosis-based search. **NCT05722886** (DETERMINE, Cancer Research UK,
recruiting on 7 August 2026) asks for *"a rare cancer harbouring an actionable genomic alteration …
for which there is a relevant open treatment arm"*. **NCT03767075** (Basket of Baskets, Vall
d'Hebron) matches treatment to the tumour's molecular profile — but its registry record was last
updated by the sponsor in April 2024, so its recruiting status is old and should be checked with
the site before relying on it.

Three other trials were recruiting on 7 August 2026 and could be relevant, for three different
reasons — the difference matters, so it is spelled out rather than run together:

- **NCT06239272** (NRSTS2021, St. Jude Children's Research Hospital) is the only one of the three
  that names extraskeletal myxoid chondrosarcoma in its own list of conditions. Its criteria state
  that patients must be 1–30 years old at the biopsy that established the diagnosis.
- **NCT01659203** (proton or photon radiotherapy, Massachusetts General Hospital; 18 and over) is
  listed for *retroperitoneal sarcoma*. It turns on **where** the tumour is, not on which sarcoma
  it is, so it is relevant only to a tumour in that location.
- **NCT04040205** (abemaciclib, Medical College of Wisconsin) is listed for chondrosarcoma,
  osteosarcoma and soft-tissue sarcoma, and it additionally requires a **CDK-pathway alteration**
  in the tumour, which is a separate test result from the fusion.

Three corrections, because out-of-date lists circulate. **NCT05836571** is active but **not
recruiting**. **NCT03600649** (seclidemstat), which does list EMC, has a registry status of
**unknown** — its record has not been updated since November 2023. And **NCT04305548**, which turns
up next to EMC in search results, lists one condition only: **mesenchymal** chondrosarcoma, which is
a different tumour type from extraskeletal **myxoid** chondrosarcoma despite the similar name.

**What to do with this.** Take these NCT numbers to your treating team. Ask whether your tumour's
fusion has been documented by sequencing, PCR or FISH and which partner gene it involves, because
the fusion-based trials require that documentation in writing. **Nothing here says that any of
these treatments works in EMC — no such evidence is offered and none should be read into this.**
**Whether you are eligible for any trial is decided by that trial's own team after they review your
records; this note cannot decide it.** Trial statuses change, sometimes within weeks, so check each
NCT number on ClinicalTrials.gov yourself, or ask your team to, before acting on anything here.

*Registry readings taken 7 August 2026 from the ClinicalTrials.gov public API.*

---

## 5 · Reviewer block — required before this leaves the repository

CLAUDE.md §3 requires a reviewer-AI block for an outward-facing act. Section 4 is one: a notice
written for patients and clinicians, naming real open trials. It has **not** been sent, published or
shown to anyone. The copyable block:

```
ROLE: You are a reviewer for a computation-only rare-cancer research program. Review the draft
patient/clinician notice below and either APPROVE it, or return a specific list of fixes. Please
weight medical integrity and honest scope above style.

PROJECT AND GOAL. Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare sarcoma driven by an
EWSR1::NR4A3 fusion. This is a one-researcher, computation-only program with no wet lab and no
clinic, so the published record is the only channel by which anything it finds reaches a patient. A
ten-sweep literature search on 2026-08-07 found something that needs no experiment at all: an open
trial whose eligibility is defined by the tumour's FUSION rather than its HISTOLOGY, and whose
listed conditions therefore hide it from every EMC patient searching by diagnosis. The memo called
the fix "a paragraph, not a grant." The draft below is that paragraph.

WHAT WAS DONE.
- Every NCT number asserted in research/manuscripts/program/emc-unexplored-treatment-lanes.md section 3.3
  was re-read LIVE from the ClinicalTrials.gov v2 API on 2026-08-07, through a GitHub Actions
  runner (the dev sandbox proxy 403s clinicaltrials.gov). Four runs: 31175763521, 31176517524,
  31176811772, 31179088283, fetch windows 7:55 AM - 8:44 AM ET.
- All nine statuses re-verified. None had changed. Three qualifications were added: NCT03767075's
  RECRUITING flag was last verified by its sponsor in April 2024 (over two years stale);
  NCT06239272's lower age bound exists only in the criterion text, not in the structured field;
  and of the trials the source memo groups as "EMC-eligible", only NCT06239272 actually names EMC
  in its condition list - NCT01659203 is defined by tumour LOCATION (retroperitoneal) and
  NCT04040205 additionally requires a CDK-pathway alteration. The draft separates those three
  reasons rather than listing them together.
- A widened screen over 1,159 unique studies looked for other trials with the same shape. One
  confirmed (NCT05918640), nine molecularly-defined (DETERMINE + 7 arms, and NCT03767075), four
  candidates that could NOT be confirmed and are excluded from the notice, three screened out.
- A transport defect was found and is documented: the repository's CI fetcher runs strip_html()
  over JSON, which deletes text between angle brackets. One failure mode is silent - a record can
  parse cleanly with whole modules missing (measured on NCT05836571). No eligibility sentence is
  quoted in the notice unless that sentence itself is provably undamaged.

FILES (branch worktree-agent-a28217642f9c44d67, committed, NOT pushed, no PR opened):
  research/literature/fet-fusion-trial-eligibility-2026-08-07.json   (all registry readings)
  research/manuscripts/fusion-direct/fet-fusion-trial-eligibility-notice.md        (this file; draft in section 4)
  research/manuscripts/fet_notice_sync_check.py                      (fails if the draft in
                                                                      section 4 and the copy in
                                                                      this block ever diverge)
  research/manuscripts/program/emc-unexplored-treatment-lanes.md             (section 3.3 now points here
                                                                      and carries the three
                                                                      qualifications; edited, not
                                                                      rewritten)

PROPOSED NEXT ACTION NEEDING SIGN-OFF, VERBATIM:
  "Publish the section 4 notice - unchanged except for fixes returned by this review - to the
  places an EMC patient or their oncologist would actually look. No specific destination has been
  chosen and nothing has been contacted: candidate destinations are a plain page in this
  repository's published record, and/or sending it to EMC and sarcoma patient-advocacy
  organisations and sarcoma centres to host or circulate. Before any of that: re-read every NCT
  number on the day of publication, because a stale 'recruiting' is the one error in this document
  that could actually harm someone."

KNOWN RISKS, UNCERTAINTIES AND JUDGMENT CALLS, STATED HONESTLY.
1. STALENESS IS THE REAL HAZARD. Trial statuses change. A notice naming NCT05918640 as recruiting
   is correct on 2026-08-07 and may be wrong later. The draft carries its retrieval date four times
   and tells the reader to re-check. Judgment call: is a dated snapshot responsible at all, or does
   this need a re-verification commitment (or a machine-regenerated page) before it is published?
2. RAISING HOPE. The notice names a trial an EMC patient may be able to enter. It makes no efficacy
   claim and says so explicitly, but naming a trial is itself a hopeful act. I judged the harm of
   silence larger than the harm of an honest, non-promotional pointer. Please challenge that.
3. I AM NOT A CLINICIAN AND THIS IS NOT A REFERRAL. The notice says eligibility is decided by the
   trial team, twice. Is that sufficient, and is the "what to do with this" paragraph the right
   level of instruction, or should it stop at "ask your team"?
4. THE FUSION-PREVALENCE FIGURE IS FROM A REVIEW, NOT A PRIMARY SERIES. The draft originally
   carried "around nine in ten", unsourced, from the memo. It was replaced with the figures
   actually read from the full text of Stacchiotti et al., Cancers 2020;12(9):2703 (PMID 32967265,
   PMC7563993), retrieved in the same CI run: EWSR1 in more than 70% of cases, TAF15 in about 20%,
   FUS among rarer partners. That is a REVIEW - a secondary source - and this repository's evidence
   policy says a review figure must not be presented as a primary study's. Should the draft cite
   the primary series behind those percentages instead, or is attributing the review by name
   sufficient for a patient-facing document?
5. FOUR UNCONFIRMED CANDIDATES ARE EXCLUDED. NCT06571734, NCT07188532, NCT06094101 and NCT04151342
   all have fusion-defined or molecularly-defined condition entries but their eligibility text
   could not be read. They are recorded in the artifact and deliberately kept OUT of the notice.
   Confirming them needs one further registry read that this session was not permitted to run.
6. SCOPE OF THE SCREEN. Non-US registries are not covered (the EU CTIS endpoint returns 403), and
   the registry-wide EWSR1 search is a size-capped sample rather than an enumeration. The notice
   does not claim completeness, but a reader may infer it.
7. NCT03600649 lists EMC and has a registry status of UNKNOWN. Calling that "not currently
   enrollable" is my reading of an unmaintained record, not a statement from the sponsor. A patient
   could reasonably still ask the site. Is the current wording fair to that?

SPECIFIC QUESTIONS.
  Q1. Is the draft's language acceptable for a patient-facing document - accurate, plain, and free
      of anything that reads as a recommendation or an efficacy claim?
  Q2. Should it be published at all as a dated snapshot, or only with a mechanism that keeps the
      statuses current?
  Q3. Is naming NCT05918640 to patients appropriate, given that EMC is not in its listed conditions
      and the site has not been contacted about EMC referrals? Should the trial team be told first?
  Q4. The fusion-partner percentages are attributed to a named 2020 review. Is that adequate for a
      patient-facing document, or must the primary series behind them be cited instead?
  Q5. Anything that must be REMOVED because it could be acted on incorrectly?

=========================== THE DRAFT NOTICE TO REVIEW, VERBATIM ===========================

If you have extraskeletal myxoid chondrosarcoma (EMC), at least one open clinical trial will not
appear in a search by your diagnosis.

Most trial searches match on the tumour's name. Some trials decide who can take part by the
tumour's FUSION GENE instead. In EMC the fusion always involves the NR4A3 gene, and its partner is
EWSR1 in more than 70% of cases and TAF15 in about 20%, with FUS among the rarer partners
(Stacchiotti et al., Cancers 2020;12(9):2703; PMID 32967265). EWSR1, TAF15 and FUS are the three
FET-family genes, so the large majority of EMC tumours carry a FET-family partner. A trial that
admits patients on that basis can accept someone with EMC even though EMC appears nowhere in the
trial's listed conditions, and that is exactly why a search by diagnosis never returns it.

The clearest current example is NCT05918640 (LIFFT), a phase 1/2 study of lurbinectedin run by the
Children's Hospital of Philadelphia. It was listed as RECRUITING when the registry was read on
7 August 2026. Its phase 1 inclusion criterion reads, word for word: "Patients must have a known
FET fusion (fusion that contains EWSR1, FUS, or TAF15) as documented by next generation sequencing,
polymerase chain reaction (PCR) or Fluorescence in situ hybridization (FISH)." The minimum age is
10, and it is for a solid tumour that has come back or not responded after first treatment. Its
listed conditions are Ewing sarcoma, desmoplastic small round cell tumour, paediatric cancer and
undifferentiated sarcoma - EMC is not one of them. One detail matters and is easy to miss: it is
the trial's PHASE 1 part that is defined this way. Its phase 2 part requires a diagnosis of Ewing
sarcoma with a confirmed EWS-FLI1 fusion, so it is the phase 1 part that is worth asking about.

Two more trials choose patients by molecular test result rather than by tumour name, so they are
also invisible to a diagnosis-based search. NCT05722886 (DETERMINE, Cancer Research UK, recruiting
on 7 August 2026) asks for "a rare cancer harbouring an actionable genomic alteration ... for which
there is a relevant open treatment arm". NCT03767075 (Basket of Baskets, Vall d'Hebron) matches
treatment to the tumour's molecular profile - but its registry record was last updated by the
sponsor in April 2024, so its recruiting status is old and should be checked with the site before
relying on it.

Three other trials were recruiting on 7 August 2026 and could be relevant, for three different
reasons - the difference matters, so it is spelled out rather than run together:
  * NCT06239272 (NRSTS2021, St. Jude Children's Research Hospital) is the only one of the three
    that names extraskeletal myxoid chondrosarcoma in its own list of conditions. Its criteria
    state that patients must be 1-30 years old at the biopsy that established the diagnosis.
  * NCT01659203 (proton or photon radiotherapy, Massachusetts General Hospital; 18 and over) is
    listed for retroperitoneal sarcoma. It turns on WHERE the tumour is, not on which sarcoma it
    is, so it is relevant only to a tumour in that location.
  * NCT04040205 (abemaciclib, Medical College of Wisconsin) is listed for chondrosarcoma,
    osteosarcoma and soft-tissue sarcoma, and it additionally requires a CDK-pathway alteration in
    the tumour, which is a separate test result from the fusion.

Three corrections, because out-of-date lists circulate. NCT05836571 is active but NOT recruiting.
NCT03600649 (seclidemstat), which does list EMC, has a registry status of UNKNOWN - its record has
not been updated since November 2023. And NCT04305548, which turns up next to EMC in search
results, lists one condition only: MESENCHYMAL chondrosarcoma, which is a different tumour type
from extraskeletal MYXOID chondrosarcoma despite the similar name.

What to do with this. Take these NCT numbers to your treating team. Ask whether your tumour's
fusion has been documented by sequencing, PCR or FISH and which partner gene it involves, because
the fusion-based trials require that documentation in writing. NOTHING HERE SAYS THAT ANY OF THESE
TREATMENTS WORKS IN EMC - no such evidence is offered and none should be read into this. WHETHER
YOU ARE ELIGIBLE FOR ANY TRIAL IS DECIDED BY THAT TRIAL'S OWN TEAM AFTER THEY REVIEW YOUR RECORDS;
THIS NOTE CANNOT DECIDE IT. Trial statuses change, sometimes within weeks, so check each NCT number
on ClinicalTrials.gov yourself, or ask your team to, before acting on anything here.

Registry readings taken 7 August 2026 from the ClinicalTrials.gov public API.

================================= END OF DRAFT NOTICE ======================================
```

⚠ **The copy inside the block is the one the reviewer sees, and §4 is the one a future session will
edit.** They must not drift apart: if §4 changes, the block's copy changes in the same commit, or
the review comes back against text that is no longer the draft — and an approval would then attach
to a version nobody read.

✅ **That is asserted, not just stated.**
[`fet_notice_sync_check.py`](../fet_notice_sync_check.py) compares the two copies word-for-word with
markup and punctuation style normalised away, and fails on any difference. Run it after touching
either copy: `python3 research/manuscripts/fet_notice_sync_check.py`. *(This repository's own
lesson, twice over: a property asserted in prose about something a human has to remember is a hope,
not a property.)*

---

## 6 · What is NOT done

- **The notice has not been sent, published, or shown to anyone**, and no destination has been
  chosen. It waits on §5.
- **Four candidate trials remain unconfirmed** (§3, "candidates"), because confirming them needs a
  per-NCT registry read from a URL manifest that would have to reach a ref CI can check out.
- **The fusion-prevalence figure now has a source, but it is a REVIEW.** §3.3's "≈89–95%" was
  unsourced in the draft, so the full text of Stacchiotti *et al.*, *Cancers* 2020;12(9):2703
  (PMID 32967265, PMC7563993) was retrieved in the same CI run (`ct-reverify-c3b-2026-08-07`,
  Europe PMC `fullTextXML`) and the draft now carries what that text actually says — **EWSR1 in
  more than 70% of cases, TAF15 in about 20%**, FUS among rarer partners. Per
  [POLICY-evidence.md](../../../systems/POLICY-evidence.md) that is a **secondary** provenance and the
  primary series behind those percentages has **not** been traced. The reviewer block asks whether
  attributing the review by name is sufficient here.
