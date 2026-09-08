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
