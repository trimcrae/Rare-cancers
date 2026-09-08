# T1 — source-method packet: what does a trial-registry free-text term search cover?

Input revision **67050fcc2a1929669e14a539d11d9060497da416**. `claude-opus-5` **medium**, saved first-party subscription — **no paid
fallback, no overage, no credits, no GPU**. Deadline **2026-09-09T02:37:19Z**.

## Correction that authorises this

I previously wrote that this question was bounded because "no such route is admitted". **That was an
assumption, not a measurement** — the absence of a prior tiny contract is not an unavailable
capability. Ordinary public-source method questions fall under the standing workstream authority.

## The question — a method/capability question, not a census

`research/manuscripts/care-delivery/emc-trial-reachability.md` line ~225 states:

> "**Which fields a free-text term search covers is not established here**: it reaches past the
> conditions and interventions lists, since the driver-gene search above returned trials that name the
> gene in neither. So whether a trial carrying its fusion language only in eligibility text could
> enter the pool is **untested** — §4's warning about instruments, pointed at this paper's own
> numerator."

**Settle what can be settled about the instrument**, and scope precisely what cannot.

## Parent readings already taken — start from these, do not repeat them

| route | result |
|---|---|
| `WebFetch https://clinicaltrials.gov/data-api/about-api/search-areas` | **`EGRESS_BLOCKED`** — "Access to clinicaltrials.gov is blocked by the network egress proxy." **Measured. Do not retry this host.** |
| `WebSearch` for the API's search areas | **returned content**: secondary sources state `query.term` is a free-text search across all study fields — title, conditions, interventions, description **and eligibility criteria** |

## Finite acceptance

1. **Establish the field coverage as well as permitted capabilities allow**, using `WebSearch` and
   `WebFetch` against hosts that are **not** blocked. ⛔ **Do not retry `clinicaltrials.gov`** — that
   block is measured. ⛔ No paid access, no credentials, no scraping workarounds, no alternative
   mirror chosen to evade a block. Any block or refusal is **recorded verbatim** and that branch stops.
2. **Grade the evidence explicitly.** The authoritative page is unreachable, so anything you obtain is
   at best **secondary / search-index level**. Say so in those words. **Repeated agreement between
   secondary sources is not authoritative confirmation.**
3. **Answer the manuscript's actual question, and its limits.** Even if `query.term` covers eligibility
   text, ask and answer: **does that settle what the paper's own screens did?** The paper's searches may
   have used a different interface, endpoint or version. If the instrument the paper used cannot be
   identified from committed inputs, **say that is the residual and leave it unresolved.**
4. **Deliverable:** a memo, and — if and only if the evidence supports it — a **proposed** replacement
   for that caveat sentence, in your lane, carrying its evidence grade in the text. ⛔ **Do not edit
   the manuscript.**
5. ⛔ **This does NOT reopen the four closed care-delivery source gates and does NOT authorise
   replaying the old term census.** One method question about field coverage. **No new census, no
   re-screening, no trial counting, no numerator work.**
6. If nothing can be established beyond the parent's two readings, **record that exact finite result
   and stop** — a supported stop is a successful outcome.

## Bounds

⛔ No write to any shared repository path; everything lives in `/tmp/claude-0/t1-lane/`. **No git
write** — read-only git only. ⛔ No manuscript, registry, gate or artifact edit. ⛔ No
`scripts/preflight.sh`. ⛔ No reopening of a closed contract. There is no wet lab: no EMC efficacy,
safety, selectivity or clinical-readiness claim, and **no claim about any patient's trial
eligibility**. Invent no fact, source or measurement. If a request of yours is refused by content
policy, stop that branch, record the refusal verbatim, never route around it.
⛔ **Retain every source action and its exact result** — the URL or query, and the response as
returned. **DELETE NOTHING**, including your lane. Record `date -u`, `git rev-parse HEAD`,
`git status --porcelain` at start and end.

## Stop conditions

Acceptance 6; any step needing a prohibited action; or **~30 tool calls / ~30 minutes**.
