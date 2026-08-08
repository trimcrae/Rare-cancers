---
id: DOC-PARTNER-EVENT-COUNTS-2026-08-08
title: "Retrieval attempt: per-partner event counts for PUB-FUSION-PARTNER — what landed, what did not, and why"
level: L3
kind: register
status: live
canonical_for: [retrieval status of the three paywalled tables named in emc-fusion-partner-stratification.md §6]
purpose: >
  Record, per source, whether the per-partner event counts that PUB-FUSION-PARTNER needs in order to state a
  MAGNITUDE were retrieved on 2026-08-08, quoting verbatim whatever did land, and naming by name whatever did
  not together with the specific reason it is unreachable.
scope: >
  Retrieval only. This document computes nothing, pools nothing and changes no number in
  emc-fusion-partner-pooling.json. It states what a fetch returned.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-08
last_verified: 2026-08-08
related: [DOC-EMC-FUSION-PARTNER-STRATIFICATION, DOC-POLICY-EVIDENCE]
---
# Retrieval attempt: per-partner event counts for PUB-FUSION-PARTNER

**$0 · no GPU · no rental.** Four GitHub Actions runs of
[`fetch-literature.yml`](../../.github/workflows/fetch-literature.yml), 2026-08-08, 1:40–1:52 PM ET.
Corpus on the `literature-cache` branch under `literature/emc-partner-events{,-r2,-r3,-r4}`; the corpus each
round asked for is [`lit-targets-partner-events.json`](./lit-targets-partner-events.json), and the HTTP status
of every individual fetch is in that round's `_manifest.json`, which is the authority — **not this document
and not the targets file.**

> ⚠ **Nothing here is a treatment recommendation**, and no efficacy, safety, therapeutic window or clinical
> readiness is asserted or implied for any agent. This is a record of which documents a fetch could and could
> not reach.

---

## 1 · The question this was sent to answer

[`systems/views/readiness.md`](../../systems/views/readiness.md) records that
[PUB-FUSION-PARTNER](./emc-fusion-partner-stratification.md) is short of exactly three things: per-partner
**event counts** from Huang 2023 (n = 58) and Paioli 2021 (n = 67), and the pazopanib trial's full **partner
distribution and prior-therapy table** (Stacchiotti 2019). The paper itself says the same in §6 and files all
three under `retrieval_provenance.not_retrievable` in
[`emc-fusion-partner-pooling.json`](./emc-fusion-partner-pooling.json). Retrieving them would convert a stated
direction into a bounded magnitude.

**Method.** Rather than one guess at a URL per paper, each source ran a four-step ladder: OA-location discovery
against four independent indexes (Unpaywall, OpenAlex, Semantic Scholar, OpenAIRE) plus the Europe PMC core
record; then a direct attempt at whatever location step 1 named; then the trial registries, which hold facts a
journal paywall does not cover; then the citation graph, for a later series reporting the same stratification
with counts. **"Paywalled in Europe PMC" and "no legal free copy exists" are different claims, and only the
second closes a route** — that distinction is what produced the one real result below.

---

## 2 · Result, per source

| source | per-partner event counts? | status after this attempt |
|---|---|---|
| **Huang 2023**, Mod Pathol, PMID 36948401 | ❌ **not retrieved** | **Not a paywall — a bot block.** Two independent indexes say a free publisher PDF exists; it returns 403 to CI. |
| **Paioli 2021**, Ann Surg Oncol, PMID 32572850 | ❌ **not retrieved** | **Genuinely closed.** No OA copy anywhere; both institutional-repository records are metadata-only. |
| **Stacchiotti 2019** pazopanib trial, PMID 31331701 | ❌ **not retrieved** | Closed everywhere. **But its prior-therapy question was answered from the registries — §3.** |
| **Stacchiotti 2014** sunitinib series, PMID 24703573 | ❌ **not retrieved** | Closed; no OA location in any index. |

**No per-partner event count was retrieved from any source.** What did land is one qualitative trial fact
(§3) and one previously-unregistered series (§5).

### 2.1 · Huang 2023 — the copy is open access and still unreachable

This is the one status change among the three, and it is not the change that was wanted.

- **Unpaywall** (`huang2023_unpaywall`, HTTP 200) returns `"is_oa": true`, `"oa_status": "bronze"`,
  `"journal_is_oa": false`, with a single OA location of `host_type: "publisher"`, `version:
  "publishedVersion"`, `"oa_date": "2023-03-21"`, and `url_for_pdf`
  `http://www.modernpathology.org/article/S0893395223000662/pdf`.
- **OpenAlex** (`huang2023_openalex`, HTTP 200) independently reports `"oa_status": "bronze"` and the identical
  `oa_url`, with `"any_repository_has_fulltext": false`.
- Both direct attempts failed. `huang2023_modpath_pdf` → **HTTP 403**, body `Just a moment...` (a Cloudflare
  interstitial). `huang2023_sciencedirect_pii` → **HTTP 403**, an Elsevier block page carrying
  `Reference number: a2805bb25ee93105`. Europe PMC has no full text to offer either: its core record gives
  `isOpenAccess: N`, `inEPMC: N`, `hasPDF: N`, `pmcid: None`, and both
  `/MED/36948401/fullTextUrlList` and `/supplementaryFiles` returned **404**.

⭐ **So the entry in `retrieval_provenance.not_retrievable` reading "paywalled" is, for this paper, wrong on
the mechanism.** A free published-version PDF is designated to exist by two independent indexes; what blocks it
is an anti-bot challenge on the publisher's edge, not a subscription. That matters because the two have
different remedies: a paywall needs an institutional subscription or an author, whereas a bot block is defeated
by any human with a browser. **A person can open that URL and read the survival table today.**

The abstract was retrieved in full (Europe PMC core record, HTTP 200) and is concordant with — rather than an
extension of — what the paper already carries. Verbatim:

> "Except for 1 (2%) NR4A3-rearranged EMC without identifiable partners, 46 (79%), 9 (16%), and 2 (3%) cases
> harbored EWSR1::NR4A3, TAF15::NR4A3, and TCF12::NR4A3 fusions, respectively."

> "TAF15::NR4A3 was significantly associated with size >10 cm (78%, P = .025)."

> "Size >10 cm, moderate-to-severe nuclear pleomorphism, metastasis at presentation, TAF15::NR4A3 fusion, and
> the administration of chemotherapy portended shorter univariate disease-specific survival, whereas only size
> >10 cm (P = .004) and metastasis at presentation (P = .032) remained prognostically independent."

Those are the numbers §3.4 and §3.5 already use. **The per-partner survival event counts are in the paper's
tables, which are behind the 403.**

### 2.2 · Paioli 2021 — closed, and the repositories hold nothing

- **Unpaywall**: `"is_oa": false`, `"oa_status": "closed"`, `best_oa_location: null`, **zero** OA locations.
- **OpenAlex**: `"oa_status": "closed"`, `"any_repository_has_fulltext": false`. It lists two repository
  records — IRIS Bologna (`hdl.handle.net/11585/778841`) and Florence Research
  (`hdl.handle.net/2158/1215233`) — both `is_oa: false`, `version: submittedVersion`.
- Both handles were fetched anyway (HTTP 200) and both are **metadata-only**. Florence states verbatim
  *"Non ci sono file associati a questo prodotto"* (there are no files associated with this product); Bologna
  states *"Eventuali allegati, non sono esposti"* (any attachments are not exposed).
- The Springer landing page (HTTP 200) carries the abstract and reference list only.

Retrieved verbatim from the abstract — **aggregate counts, not partner-stratified**:

> "Sixty-seven patients were identified: 13 (20%) female, 54 (80%) male. … Numbers and type of translocation
> were: 50 (80%) NR4A3-EWS, 10 (16%) NR4A3-TAF15, 1 (2%) NR4A3-TCF12, and 1 (2%) NR4A3-TFG."

> "Thirty-five (52%) patients relapsed: 9 had local recurrence (LR) and 26 had distant metastasis (5 with
> concomitant LR)."

> "Patients carrying the NR4A3-EWS translocation had a trend in favor of better DFS (p = 0.08) and DMFS
> (p = 0.09) compared with the patients with NR4A3-TAF15."

⚠ **The 35/67 relapse split is a real retrieved number and it is still not poolable**, because §2.1 of
[`POLICY-evidence.md`](../../systems/POLICY-evidence.md) requires counts on **both sides of the
stratification** and this total is partner-blind. Splitting 35 relapses across a 50/10 partner ratio would be
a back-derived count, which §2.1(2) forbids. It is recorded here so that a future session does not re-fetch it
believing it might be the missing table.

### 2.3 · Stacchiotti 2019 and 2014 — closed everywhere

Both are `"oa_status": "closed"` with zero OA locations in Unpaywall and
`"any_repository_has_fulltext": false` in OpenAlex. `stacchiotti2019_lancet_fulltext` → **HTTP 403**. The
repository handles OpenAIRE and OpenAlex list were all fetched: IRIS Bologna (`11585/779084`, `11585/393895`),
Ferrara (`11392/2495557`), Padova (`11577/3243739`) are metadata-only; **DIGITAL.CSIC** (`10261/214284`)
returns an *Anubis* proof-of-work anti-scraper challenge — verbatim, *"Making sure you're not a bot!"* — which
no stdlib fetcher can clear.

---

## 3 · What DID land: the trial's prior-therapy rule, from two independent registries

The one item in `not_retrievable` that this attempt actually closed is this one, quoted from the artifact:

> "NCT02066285 eligibility text": "not present in the cached ClinicalTrials.gov v2 records (the cached field
> set omits eligibilityModule); would answer whether prior antiangiogenic therapy was permitted."

**It is present, and it answers the question.** From the ClinicalTrials.gov v2 record for NCT02066285
(`nct02066285_ctgov_v2_full`, HTTP 200), under Exclusion Criteria, verbatim:

> **"Patients who have received previous antiangiogenic agents."**

Independently corroborated on a second registry. The same record supplied EudraCT number **2013-005456-15**
and sponsor protocol code **GEIS-32**, and the EU Clinical Trials Register protocol page for that number
(`euctr_geis32_es`, HTTP 200) lists under **E.4 Principal exclusion criteria**, as item **3**, verbatim:

> **"Patients who have received previous antiangiogenic agents."**

Two further retrieved facts bound how this may be read:

- The EU CTR page records *"Date on which this record was first entered in the EudraCT database:
  2014-02-27"*, and the ClinicalTrials.gov record gives an **actual start date of 2014-06** with
  `primaryCompletionDate 2019-12`. So the criterion was on a public protocol record **before accrual opened**;
  it is not a retrospective description.
- A second prior-therapy constraint was retrieved, under Inclusion Criteria, verbatim: *"Patients could have
  received a maximum of 4 lines of chemotherapy for metastatic disease prior to trial enrollment."*

### 3.1 · What this bears on

§3.1, §4.5 and falsifier 3 of §6 all turn on one unresolved question: whether the sunitinib series' patients
re-enrolled on the pazopanib trial. The paper holds the smaller cohort out of the headline for exactly this
reason, which is why its TAF15 denominator is a **range (3 to 5)** rather than a number, and it states plainly
that *"neither report states whether prior antiangiogenic therapy was permitted."*

**One of the two now does.** Sunitinib is an antiangiogenic agent; the trial excluded patients who had received
previous antiangiogenic agents; therefore a patient in the sunitinib series was **ineligible** for the
pazopanib trial, and the two cohorts cannot overlap.

⚠ **Three limits on that, all of which must travel with it, and the first is not a formality:**

1. **This is the protocol's rule, not a patient-level audit.** Registries publish eligibility criteria, not
   enrolment decisions; protocol deviations and waivers occur and are recorded in neither registry. This is
   strong evidence of non-overlap. It is **not proof**, and it must not be written as though a subject list had
   been inspected. The honest form is *"the trial's own eligibility criterion excludes it"*, never *"no patient
   appeared in both"*.
2. **It does not produce a magnitude — see §4.** It changes which denominator is primary, not whether the
   TAF15 arm has any events.
3. **It is a change to a pooling decision, so it belongs in the generator, not in prose.** Acting on it means
   editing `COHORTS` in [`emc_fusion_partner_pooling.py`](./emc_fusion_partner_pooling.py) and regenerating
   the artifact, per the rule that a number typed into the manuscript that disagrees with the artifact is the
   defect. **This document does not make that edit — §6.**

**Also retrieved, and it closes a different open item negatively:** there are **no posted trial results** to
mine. The EU CTR results endpoint returns verbatim *"There are no public results for the specified EudraCT
number"*, and the ClinicalTrials.gov record carries `"hasResults": false` with no `resultsSection`. The trial's
partner distribution is therefore in the Lancet Oncology paper and **nowhere else that is public**.

---

## 4 · Can PUB-FUSION-PARTNER state a MAGNITUDE now?

**No. It still states a direction.** Plainly, because this is the question the task was sent to answer:

- **The blocker was never the overlap.** It is that **the TAF15 arm has zero events**, and a zero-event arm
  cannot yield a magnitude at any denominator. The paper already computes both ends: at 0/5 vs 10/27 the
  Wilson 95 % upper bound on the TAF15 response rate is **43.4 %**, which still sits **above** the comparator
  arm's own point estimate of 37.0 %. Resolving the overlap moves the analysis from one end of a stated range
  to the other; it does not narrow the interval enough to exclude a TAF15 response rate equal to the EWSR1
  one, and the paper's §3.1 conclusion is unchanged word for word.
- **The three tables that would have produced a magnitude were not retrieved.** Huang's per-partner survival
  events, Paioli's per-partner relapse and metastasis events, and the trial's partner distribution all remain
  behind their respective barriers.

**What did improve is the paper's honesty about its own denominator**, and that is worth having: the headline
denominator can become a single number (5) rather than a range (3–5), the analysis currently labelled
*secondary — assumes independence* becomes the POLICY-conformant primary, and §4.5's *"only a paywalled table
can close it"* is now false — a public registry closed it. That is a real tightening of a stated uncertainty.
It is not a magnitude, and it must not be reported as one.

---

## 5 · One previously-unregistered series, found in the citation graph

Searching what cites Huang 2023 and Paioli 2021 surfaced a cohort the paper does not carry, retrieved
(abstract, Europe PMC core record, HTTP 200) rather than recalled:

**Suemitsu Y, Chang HY, Saoud C, Dermawan JK, Hameed M, Singer S, Tap WD, Antonescu CR. "Secondary Genetic
Alterations in Extraskeletal Myxoid Chondrosarcoma." *Genes, chromosomes & cancer* 2025;64. PMID 40828003 ·
doi:10.1002/gcc.70076.** Eighteen patients, MSK-IMPACT. Verbatim:

> "the most common NR4A3 fusion subtype involved EWSR1 (14/18, 78%), while two cases involved TAF15 gene
> partner, and one each TCF12 and FUS genes, respectively."

> "Patients with ≥ 1 SGA showed lower disease-free survival (DFS) (p = 0.022) and poor overall survival (OS)
> (p = 0.014), while **no statistically significant correlation was detected between OS and fusion subtypes**."

⭐ **This is a third independent series failing to establish the partner as a prognostic factor**, joining
Huang 2023 (loses significance on multivariable analysis) and Paioli 2021 (does not reach significance at all)
in §3.4 — and it is the first to say so about **overall survival** directly rather than as a casualty of
adjustment. It strengthens a claim the paper already makes and weakens none.

⚠ **Two reasons it cannot simply be added, both of which a future session must check before using it:**
its senior author and institution are the **same MSKCC group and database** as Agaram 2014, the one cohort
whose event counts §3.3 pools, so §2.3's `population-overlap` rule is squarely in play; and its abstract gives
a partner distribution but **no per-partner event counts**, so it would enter as context, not as a poolable
stratum. It is paywalled (`isOpenAccess: N`, no PMCID).

Three other citation-graph candidates were retrieved and carry nothing usable: PMID 37057757 (2 TAF15 cases,
morphology, no outcomes), PMID 41755350 (5 cases, novel *FUS::NR4A2* and *ACTB::NR4A3* fusions, no
EWSR1-vs-TAF15 contrast), and PMID 40885991 (Japanese national registry, n = 171, open access — but **not
stratified by fusion partner at all**).

---

## 6 · What this document deliberately does NOT do

**No number in [`emc-fusion-partner-pooling.json`](./emc-fusion-partner-pooling.json) was changed, and
[`emc-fusion-partner-stratification.md`](./emc-fusion-partner-stratification.md) was not edited.** No
per-partner event count landed, so there is no new count to fold in, and the one qualitative finding in §3
changes a **pooling decision** — which lives in the generator's `COHORTS` table and must be regenerated, never
hand-typed into prose. Making that edit mid-flight, on a shared branch, would put the paper and its artifact
into exactly the disagreement the paper calls "the defect".

The follow-up edits this attempt has earned, for whoever picks them up:

1. **`retrieval_provenance.not_retrievable` is now wrong in two places** and both are corrections, not
   additions. The `NCT02066285 eligibility text` entry should be **removed** — the text was retrieved (§3).
   The Huang 2023 entry says "paywalled"; the mechanism is a **bot block on a designated-OA PDF** (§2.1), which
   is a different remedy.
2. **§3.1 / §4.5 / §6-falsifier-3**: the overlap is resolved by the trial's own exclusion criterion, subject to
   the three limits in §3.1. This is a change to `COHORTS[stacchiotti-2014-sunitinib].contextReason`, and the
   superseded "3 to 5" range belongs in Appendix A and in
   [`pinned-figures.json`](./pinned-figures.json) in the same commit.
3. **§3.4 / §5** may gain PMID 40828003 as context once the MSKCC overlap with Agaram 2014 is checked (§5).
4. **§6's ask should be re-aimed.** Huang 2023 does not need to be "published in partner-stratified form" — a
   free published-version PDF already exists at a URL a human can open. The ask for that paper is narrower and
   easier: *read the table*.

⚠ **One observation offered as a hypothesis, not a finding.** Appendix A of the paper records a registry
defect in which Huang 2023 is filed under citation id `warmke2023` / label *"Warmke 2023"*, which does not
match its author list. PMID **37057757** is a genuinely distinct 2023 EMC/TAF15 paper whose first author **is**
Warmke LM (retrieved above), which would explain how that label arose. **This is inference from a coincidence
of names and is not evidence about the registry entry**; whoever applies edit `F3` should verify it rather than
quote this line. No registry file was touched by this work.

---

## 7 · Provenance

Every quotation above was read from a file on the `literature-cache` branch, each of which records its source
URL, final URL, HTTP status and content type in its own header. Rounds, run IDs and the exact URL each round
requested: [`lit-targets-partner-events.json`](./lit-targets-partner-events.json).

⚠ **One retrieval defect in this work, recorded rather than quietly fixed.** Round 4's `unpaywall_37057757`
target was built from a **guessed** DOI (`10.1016/j.humpath.2023.04.002`, assuming Human Pathology). PMID
37057757 is in *Genes, chromosomes & cancer*, `10.1002/gcc.23144`. The guessed DOI **resolved to a real but
entirely unrelated paper** about colonic sessile serrated lesions, and Unpaywall returned a confident
`is_oa: true` about that paper. Nothing errored. It was caught only by comparing the returned title against the
expected one. **An invented identifier that resolves is more dangerous than one that 404s**, because every
automated check downstream of it succeeds; the corrected identifiers are recorded under
`_identifiers_returned_by_these_fetches` in the targets file, all read out of fetched records.

⚠ **Two of the four runs lost their retrieval to a push race and had to be re-dispatched.** Runs 31270125124
and 31270225623 both fetched every target successfully and then failed on
`! [rejected] literature-cache -> literature-cache (fetch first)` / `cannot lock ref`. The publish step of
`fetch-literature.yml` pushes once with no retry loop, unlike the lane-probe step in the same file, which
retries three times — so four parallel dispatches of the same workflow serialise fine on their per-corpus
concurrency group but still collide on the single shared `literature-cache` ref. The fix used here was to
re-dispatch serially. **The runs reported `failure` with the data already fetched**, so a session reading only
the conclusion would conclude the sources were unreachable when they were not.
