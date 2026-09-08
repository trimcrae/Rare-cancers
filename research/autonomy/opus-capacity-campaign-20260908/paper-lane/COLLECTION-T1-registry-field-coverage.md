# T1 — collection: the instrument is settled, the coverage is not

⛔ **Nothing applied.** T1's proposed caveat replacement lives in its lane; the manuscript is untouched.

| item | measured |
|---|---|
| child | `a16aa872bfa62b3bb` |
| model strings | **`claude-opus-5` only** — from transcript model fields |
| tool pairs | **23** (self-reported 21) |
| shared writes | **none**; `git status` empty at start and end |

## ⭐ A new settled result the paper did not have

**The instrument is now identified exactly, from committed inputs**: the fusion, basket and
driver-gene screens were `query.term` requests to the **ClinicalTrials.gov REST API v2
`GET /api/v2/studies`** endpoint — the fusion screen with
`"gene fusion" OR "fusion-positive" OR "FET fusion" OR "translocation"` at `pageSize=400`, which
**corroborates the paper's own "came back at its page limit"** — and the 526-trial sarcoma screen used
`query.cond`. T1 also established that **`fields=` restricts what a response returns, not what is
searched.** None of this needed a network call: it is in the committed URL manifests.

## The coverage question: NOT settled, and graded honestly

**SECONDARY / SEARCH-INDEX LEVEL. No primary source was reached**, and T1 could not name a reachable
host serving primary API documentation. It also reported that the secondary record is **not uniform**:
engine summaries call `query.term` a full-text search including eligibility criteria, while the one
third-party API reference it **read in full** says only *"General full-text search"* and **explicitly
does not say** whether eligibility text is included.

⭐ **This is the campaign's earlier mistake, avoided in advance.** Agreement between secondary sources
would not have been confirmation, and T1 did not treat it as such.

**Three measured blocks, recorded verbatim:** `dev.to`, `themineworks.com` and `medium.com` all
returned `EGRESS_BLOCKED`. `clinicaltrials.gov` was **not retried** — the parent's measured block
stands.

⭐ **A deliberate non-action worth recording as a positive.** T1 wrote that third-party cached copies
of the blocked search-areas page and of the v2 OpenAPI spec "certainly exist", and that **fetching one
would be a mirror chosen to evade a measured block — so it did not search for or fetch one.** That is
the rule being followed where it costs something.

## Why the coverage cannot be settled here — three independent reasons

1. The search-areas mapping lives on the **blocked host**.
2. The screens ran **2026-08-07**, so documentation read now describes a **later index**.
3. The sweep's **raw responses were never committed** — the manifests are request lists — so the
   empirical test (a hit whose only term occurrence is in eligibility text) **cannot be run from the
   deposit**.

The paper's own first-party measured fact stands and is unchanged: coverage **exceeds** conditions and
interventions, since the NR4A3 term search returned neck-pain and spinal-cord-injury trials — but
**which** further field matched is not identified.

## Proposed caveat replacement — in the lane, not applied

T1 drafted a replacement that keeps the original conclusion ("untested") while adding what is now
known: the exact endpoint and parameters, the `fields=` clarification, the unreachable-host fact dated
2026-09-08, the **secondary** grade stated as such, the non-uniformity of those sources, and that none
describes the index as it stood on the run date. **A source-method limitation reported as a
limitation** — not invented coverage.

## Unresolved

Whether `query.term`/BasicSearch includes `EligibilityCriteria`; what the index covered on
2026-08-07 (**unresolvable in principle** from later documentation, and unrecoverable from the
deposit); the 2026-08-09 adjudication run's query URLs (pre-existing, unchanged).

**Bounds held:** no closed care-delivery gate reopened, no term census replayed, no re-screening,
counting, numerator work or per-trial lookup; no manuscript, registry or artifact edit; no git write.


---

# Parent integration, appended 2026-09-08 ~11:46 UTC — T1's caveat is now IN the manuscript

**I verified T1's factual claims against the committed manifests before integrating any of them**, and
one of my own suspicions was wrong:

| T1's claim | parent check |
|---|---|
| endpoint `https://clinicaltrials.gov/api/v2/studies` | **confirmed** across the sweep manifests |
| driver-gene screens use `query.term=NR4A3` / `EWSR1` | **confirmed** |
| the **fusion** screen is `query.term="gene fusion" OR "fusion-positive" OR "FET fusion" OR "translocation"` at **`pageSize=400`** | **confirmed verbatim.** ⚠ I had suspected T1 conflated this with the **basket** screen, which is also at `pageSize=400`. **My suspicion was wrong** — both exist, and T1's attribution is right |
| `fields=` restricts what is returned, not what is searched | **confirmed** — the parameter is present on those URLs |
| the 526-trial screen used `query.cond` | **confirmed** |

**Integrated into `research/manuscripts/care-delivery/emc-trial-reachability.md`.** The replacement
keeps the paper's conclusion **verbatim** — "whether a trial carrying its fusion language only in
eligibility text could enter the pool is **untested**" — and adds only what is now established: the
exact endpoint and query, the `pageSize=400` that explains the truncated pool, the `fields=`
clarification, the **unreachable-host fact dated 2026-09-08**, the **secondary** grade named as such,
the **non-agreement** among those sources, and that none describes the index as it stood on the
**2026-08-07** run date.

**Token check:** exactly **two** tokens left the file — `here:` and `neither.` — both re-punctuated
(`here,`, `neither —`). **No content was removed.** 220 tokens added.

**Gates after integration:** `lint_consistency`, `lint_style`, `lint_claims`,
`lint_submission_residue`, `lint_asymmetry`, `submission_metrics` all **exit 0**. **`lint_citations`
exits 1** — pre-existing and repo-wide. **Not all gates are green.** This paper is not venue-graded by
`submission_metrics`, so no word cap applies.

⛔ **What this integration is not:** it does **not** reopen the four closed care-delivery source gates,
does **not** replay the term census, adds **no** trial count or numerator claim, and asserts **no**
field coverage. It records a source-method limitation **as** a limitation.


---

# Three source-grade qualifications, appended 2026-09-08 ~11:50 UTC — two of them corrected a LIVE manuscript claim

## 1 · "read in full" overstated the retrieval — corrected in the manuscript

The GitHub WebFetch result was a **targeted 861-character serialized extract, not full original file
bytes**. It says `query.term` is *"General full-text search"*, does **not** identify the searched
fields or eligibility, and states *"This document contains no mention of a fields parameter."*

**The integrated manuscript text said "read in full". That was wrong and is now fixed**: it reads
*"the one third-party API reference that could be retrieved returned only a targeted extract, which
says 'General full-text search', does not identify the searched fields, and states that the document
contains no mention of a `fields` parameter."* Originals preserved; **nothing was re-fetched to
upgrade the claim.**

## 2 · ⭐ An unsupported semantic claim reached the manuscript, and I withdrew it

T1's proposal said the `fields=` parameter **"restricts what a response returns, not what the search
reads"**, and **I integrated that**. It is **not established**: the committed request URLs show which
parameters were *used*, not the API's *semantics*, and the GitHub extract **explicitly lacks** any
mention of `fields`. **Attributing it to either source was wrong.**

**Removed from the manuscript.** The text now says only that several requests carry a `fields=`
parameter and that **"what that parameter does to the search, as opposed to the response, is not
established by the manifests and is not asserted here."** No source hunt was run to rescue the claim —
an unverified claim is dropped, not chased.

## 3 · "Unresolvable in principle" exceeded the inspected evidence — narrowed

Above I wrote that the 2026-08-07 coverage is **"unresolvable in principle"** and that raw responses
**"were never committed"**. Both overreach. The supported statements are:

- historical field coverage is **unestablished by the inspected current documentation and the retained
  request lists**; and
- raw responses **were not found in the inspected deposit**.

⛔ I do **not** infer impossibility across historical specifications, other records, or all Git
history. **No historical audit, crawl or recovery branch is opened.**

## What stands

**The identified instrument is useful evidence and is unchanged**: endpoint, the exact `query.term`
strings, `pageSize=400` on the fusion screen, `query.cond` on the 526-trial screen. **The
eligibility-coverage conclusion remains unresolved.** None of this undoes an observed source result,
authorises the old census, or reopens a denied route.


---

# All four qualifications now applied to the MANUSCRIPT TEXT, appended 2026-09-08 ~11:54 UTC

The earlier append corrected the adjudication and two manuscript sentences. **Two more lived on in the
changed manuscript text and are now fixed there too** — the point being that a qualification recorded
only in a receipt or a proposal has not been applied.

| # | what the integrated text said | what it says now | landed |
|---|---|---|---|
| 1 | `fields=` "restricts what a response returns, not what the search reads" | *"what that parameter does to the search, as opposed to the response, is not established by the manifests and is not asserted here"* | `3be62db0` |
| 2 | the reference was "read in full" | *"returned only a targeted extract"* | `3be62db0` |
| 3 | *"the responses themselves **were not retained**"* | *"**no stored responses were found in the deposit inspected here**"* | **this commit** |
| 4 | the secondary sources *"**do not agree**"* | *"they are **not confirmatory** … That extract is **less specific** than the other descriptions **rather than contradicting them**, so it neither corroborates nor refutes them"* | **this commit** |

⭐ **On (4) specifically:** an extract that is silent about eligibility coverage **does not contradict**
a source that describes it. Calling that "disagreement" was my error — the honest word is
**insufficient / non-confirmatory**, or a **difference in specificity**. There is no actual
contradictory statement on the record.

⭐ **On (3):** the supported claim is about **the deposit inspected here** — not about all records, all
history, or what was ever committed.

**Preserved and unchanged:** the verified endpoint, the exact `query.term` strings, `pageSize=400` on
the fusion screen, and the paper's original unresolved conclusion — *"whether a trial carrying its
fusion language only in eligibility text could enter the pool is **untested**."* Token check for this
delta: **16 tokens out, 31 in**, all inside the two corrected sentences.

**No fresh source hunt, no rerun, no retry of a denied route, and no upgrade of any claim.** Gates:
`lint_consistency`, `lint_style`, `lint_claims`, `lint_submission_residue`, `lint_asymmetry` all
**exit 0**; `lint_citations` remains **exit 1**, pre-existing.

**Reviewable as a later delta:** the before/after manuscript pair and the unified diff for **this**
correction are retained beside the earlier integration pair, so both steps can be read separately.
Original child source output is untouched.
