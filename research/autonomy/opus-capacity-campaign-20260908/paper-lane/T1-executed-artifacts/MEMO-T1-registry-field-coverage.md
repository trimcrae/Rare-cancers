# T1 memo — what a free-text term search covers, and what the paper's own screens were

Worker T1. 2026-09-08. Repo HEAD at start `b6586bc9aab9d29860ecdc12896fbf1539ba4890`, tree clean.
Contract: `research/autonomy/opus-capacity-campaign-20260908/paper-lane/CONTRACT-T1-registry-field-coverage-method.md`.
Every source action and its verbatim result: `SOURCE-LOG-T1.md` in this lane.
Nothing shared was written. No manuscript edit. No git write.

## 1 · Result in one paragraph

Two different things were entangled in the manuscript's caveat, and they separate cleanly. **The
instrument the paper used IS identifiable from committed inputs** — this is settled, first-party and
measured. **What that instrument searches is NOT settled**, and cannot be settled from here above
**SECONDARY / SEARCH-INDEX level** evidence, because the authoritative page is behind a measured
egress block and the only routes that would beat that grade are mirrors of the blocked page, which
this contract forbids. So the manuscript's conclusion — *untested* — survives, but its premise can
be sharpened, and the reason it is untested can be stated instead of merely asserted.

## 2 · SETTLED: the instrument the paper's screens used

From committed URL manifests (`research/literature/emc-clinical-sweep-targets.json`,
`emc-clinical-sweep-c3.json`, `emc-clinical-sweep-c4.json`), designated by the manuscript's §7 as
"the URL manifests behind the 2026-08-07 sweep". The registry instrument is the **ClinicalTrials.gov
REST API v2, `GET https://clinicaltrials.gov/api/v2/studies`** — not the website UI, not a v1
endpoint, not a third-party interface. Verbatim, the screens named in §2's table:

- **fusion screen** (400 studies, its page limit):
  `.../studies?query.term=%22gene+fusion%22+OR+%22fusion-positive%22+OR+%22FET+fusion%22+OR+%22translocation%22&filter.overallStatus=RECRUITING&pageSize=400&format=json&fields=NCTId%7CBriefTitle%7COverallStatus%7CPhase%7CInterventionName%7CCondition%7CStudyType`
  — `pageSize=400` corroborates the manuscript's "came back at its page limit".
- **basket screen**:
  `.../studies?query.term=%22basket%22+OR+%22tumor+agnostic%22+OR+%22histology+agnostic%22+OR+%22rare+tumors%22&filter.overallStatus=RECRUITING%7CNOT_YET_RECRUITING&pageSize=400&...`
  (a second, earlier basket variant in `-targets.json` pairs `query.cond=soft+tissue+sarcoma` with a
  `query.term`, and a third is a `query.term` on `"rare tumors" OR "rare cancer"`.)
- **driver-gene term search** (5 studies):
  `.../studies?query.term=NR4A3&pageSize=100&format=json` — **no `fields` parameter**, consistent
  with §4's "that search returns whole records, so it is capped by response size".
- **EWSR1 term search**: `.../studies?query.term=EWSR1&pageSize=100&format=json`.
- **sarcoma condition screen** (526) and the diagnosis searches: `query.cond=...`.
- intervention screens: `query.intr=...`.

Two method points that follow directly and are worth keeping straight:

1. `fields=` restricts the fields **returned**, not the fields **searched**. A screen that returned
   only NCTId/Title/Condition still searched whatever `query.term` searches. The manuscript's "the
   fielded screens carry no eligibility text, so they can identify a candidate and can never confirm
   one" is about the response, and stays correct.
2. The three parameters are distinct search entry points (`query.cond`, `query.intr`, `query.term`).
   The paper's own §5 already says its screens "search different fields"; the manifests make that
   concrete rather than inferred.

**Residual on the instrument.** The manifests are *request* lists; the raw *responses* were not
committed (the sweep files hold URLs, not payloads — checked; no retained registry payload in
`research/literature/` or `research/data/` carries eligibility text from a term search). And §7
already records that the 2026-08-09 adjudication run's manifest "was never committed and names the
API base only". So: the **2026-08-07 term screens that built the pool** are identified to the exact
endpoint and parameter; the **2026-08-09 adjudication** run is identified only to the API base.

## 3 · NOT SETTLED: what `query.term` actually searches — and at what grade

**Evidence grade: SECONDARY / SEARCH-INDEX LEVEL. Not authoritative. No primary source was reached.**
I state that in those words deliberately. The authoritative document — the registry's own search-areas
page — returned a measured `EGRESS_BLOCKED` to the parent and was not retried. No reachable host
served primary API documentation; if I had reached one I would name the host here, and I cannot.

What the secondary record says, and where it disagrees with itself:

- Search-engine summaries (S1, S4) report `query.term` as a general full-text search "across all
  fields", and separately list eligibility criteria among the data the API exposes. S4 names the
  actual mechanism — a **search-areas mapping** in which a named area such as **BasicSearch** defines
  which data pieces a parameter searches, with weights — but does **not** state BasicSearch's
  membership. That mapping is the thing that would settle this, and it lives on the blocked host.
- The one third-party API reference I actually fetched and read (S3, on github.com) describes
  `query.term` **only** as "General full-text search" and, asked directly, reports that it "does not
  explicitly state which text fields each parameter searches or whether eligibility criteria text is
  included."

So the secondary record is not even uniform: it is a mix of vague descriptions and a specific claim
made without a citable field list. **Repeated agreement between secondary sources would not have been
authoritative confirmation in any case** — the campaign has made that error before and corrected it —
and here there is not even clean agreement to over-read.

**What the paper's own data does establish, independently and at first-party grade:** coverage
extends past the conditions and interventions lists, because the `query.term=NR4A3` search returned
studies whose listed conditions are neck pain and spinal-cord injury. That is measured. What it does
**not** identify is *which* further field matched — title, brief summary, detailed description,
keywords, or eligibility text are all consistent with that observation. The raw responses were not
retained, so this cannot be resolved from committed data, and resolving it by new retrieval is both
outside this contract and blocked at the network.

## 4 · Does §3 settle what the paper's own screens did?

**No — and the two questions do not even have the same shape.**

- The *interface* question is answered: API v2 `/studies`, `query.term`, quoted above. The paper's
  screens were not run through a different UI or a v1 endpoint, and that is now checkable from
  committed inputs rather than assumed.
- The *coverage* question is not answered, and would not be answered even by an authoritative
  search-areas page read today, for a reason the paper should say out loud: the screens ran on
  **2026-08-07**. A search-areas mapping read in September 2026 describes the index as of the read,
  and a registry may change its indexing without notice. So the strongest obtainable statement about
  this paper's numerator would still be a dated inference about the instrument as documented later,
  not a measurement of the instrument as it behaved on the run date.
- The empirical route that *would* have settled it for the actual run — inspecting the returned
  records for a study whose only occurrence of the search term is in its eligibility text — is closed
  because the sweep's responses were not committed.

That residual is a real result, not a failure: **the paper's screens are identified; their field
coverage is not, and cannot be recovered from the deposit.**

## 5 · Proposed replacement for the caveat sentence — PROPOSAL ONLY, NOT APPLIED

Replaces, in `research/manuscripts/care-delivery/emc-trial-reachability.md` §5 (~line 225), the two
sentences beginning "Which fields a free-text term search covers is not established here" and ending
"...pointed at this paper's own numerator." Carries its evidence grade in the text, as required.

> Which fields a free-text term search covers is not established here, though the instrument is.
> The fusion and basket screens and the driver-gene search were `query.term` requests to the
> ClinicalTrials.gov REST API v2 `/api/v2/studies` endpoint, and §7's committed URL manifests record
> each one verbatim; the `fields` parameter on some of them restricts what a response returns, not
> what the search reads. What that parameter reads is another matter. It reaches past the conditions
> and interventions lists, since the driver-gene search above returned trials that name the gene in
> neither — but which further field matched, title, summary, description, keywords or eligibility
> text, those records cannot say, and the responses themselves were not retained. The registry's own
> documentation of its search areas could not be read: that host was unreachable from this work's
> network when we tried on 2026-09-08. The descriptions we could reach are secondary, at the level of
> third-party documentation and search-engine summaries rather than the registry's own specification,
> and they are not uniform: several call `query.term` a general full-text search over all study
> fields and place eligibility criteria within it, while the one third-party API reference we read in
> full says only "General full-text search" and does not say whether eligibility text is included.
> Agreement among secondary sources is not confirmation, and none of them describes the index as it
> stood on 2026-08-07, when these screens ran. So whether a trial carrying its fusion language only
> in eligibility text could enter the pool is untested — §4's warning about instruments, pointed at
> this paper's own numerator.

Optional companion line for §7 (data availability), if the owner wants the identification made
explicit where the manifests are named — again a proposal only:

> The manifests record requests, not responses: they establish which endpoint and which query
> parameter each screen used, and cannot show which fields the registry matched them against.

**Notes for the paper's owner.** (a) The replacement is longer than what it replaces; if §5's budget
is tight, the first sentence plus the last sentence alone still carry the upgrade. (b) It asserts
nothing about any trial, any patient's eligibility, any count, or any therapy. (c) Everything in it
is checkable: the URLs against the three committed manifests, the block and the secondary readings
against `SOURCE-LOG-T1.md` in this lane.

## 6 · Unresolved after this work

1. Whether `query.term` (the BasicSearch area) includes `EligibilityCriteria` — unresolved at
   authoritative grade. The settling document is on a host under a measured egress block.
2. What the index covered on **2026-08-07**, the run date — unresolvable in principle from any
   documentation read afterwards, and unrecoverable from the deposit because responses were not kept.
3. The 2026-08-09 adjudication run's exact query URLs — already recorded as missing in §7; unchanged.

## 7 · What T1 did NOT do

No retry of clinicaltrials.gov in any path or subdomain. No mirror or cached copy of the blocked page
(route identified and deliberately declined — see SOURCE-LOG R1). No paid access, no credentials, no
scraping workaround. No new census, no re-screening, no trial counting, no numerator work, no
per-trial lookup, no new registry retrieval of any kind. No reopening of the four closed care-delivery
source gates. No manuscript, registry, gate or artifact edit. No git write. No `scripts/preflight.sh`.
No claim about EMC efficacy, safety, selectivity or clinical readiness, and no claim about any
patient's trial eligibility.
