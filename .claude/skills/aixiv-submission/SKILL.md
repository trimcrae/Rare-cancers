---
name: aixiv-submission
description: Post a paper from this repository to aiXiv and read its automated review. Load before submitting or revising anything on aixiv.science, before quoting an aiXiv Rating to anyone, and before setting a target rating as a goal. Covers the working mechanics (agent token, the exactly-three category contract, metadata generated from the manuscript, PREFLIGHT_FULL before any post) and the three traps that cost a day: is_public=0 does NOT make a submission private, the Rating is written by an UNAUTHENTICATED endpoint so it is not a quality measurement, and four substantive revisions of one paper moved it not at all while a DIFFERENT paper of the right shape scored 7 on its first version. Also the one thing that does move a rating (pick the paper, do not iterate the prose), and what this repository will not do to raise a number.
---

# Submitting to aiXiv, and what its Rating is worth

Measured 2026-08-22 → 2026-08-23 on `aixiv.260822.000005` (the EMC fusion-junction vaccine paper),
four versions and four reviews, plus a full-corpus pull of **874 reviews**. Client:
[`scripts/aixiv_review.py`](./scripts/aixiv_review.py). Workflow:
[`aixiv-review.yml`](./.github/workflows/aixiv-review.yml). API surface read at primary source into
`literature/aixiv-api-surface-2026-08-22/` on `literature-cache`.

⚠ **Commit gates live in `repo-gates`; the hardening loop lives in `paper-hardening`. Neither is
restated here.**

---

## 0 · ⛔⛔ THE RATING IS NOT AN AUTHENTICATED SIGNAL. DO NOT MAKE IT A TARGET

`POST /api/submit-review` carries **no security requirement** in `openapi.json` and takes a
free-text `reviewer` field. **Any party can post any rating on any paper.** The corpus shows exactly
what that produces:

| rating | the entire review text |
|---:|---|
| **10** | `Nah` |
| **10** | `0 Axiomas 0 postulados = ABARCA TODO LO FÍSICAMENTE EXISTENTE` |

A reviewer calling itself `Anonymous Agent` also appears in the corpus alongside `Official Agent`.

⛔ **SO A TARGET RATING IS TRIVIALLY REACHABLE BY POSTING YOUR OWN REVIEW, AND THIS REPOSITORY DOES
NOT DO THAT.** It would place a fabricated review under trimcrae's name on a paper carrying his
ORCID. If asked to "get a paper to N", the honest answer is this section plus §3 — not a number.
⚠ **And never quote an aiXiv Rating to anyone without saying who wrote it.** Read `reviewer` on the
review record; `calibrate` splits the distribution by reviewer identity for exactly this reason.

## 1 · What the Rating actually is, measured over the whole archive

`calibrate --limit 2000` (run 32607567522), **n=874 reviews**, paged through
`/api/submissions/public` and sampled every *k*-th rather than head-of-list:

```
min 0   max 10   mean 4.32   median 4
 0:2   1:36   2:134   3:172   4:142   5:113   6:142   7:100   8:27   10:4
 (plus one 5.5 and one 6.5 — the scale is NOT integer-only)
```

- **A 7 is not rare: 100 papers hold one, 131 hold 7 or better.**
- ⚠ *Superseded, retained — two earlier readings, both from a 150-paper sample: that the scale topped
  out at **8**, and that ≥7 was "roughly the top decile". `/api/submissions/public` paginates with
  `limit` defaulting to **100**, and the first page was dominated by one submitter's serialised
  resubmissions. Neither figure may be quoted.*
- ⛔ **Percentiles over this corpus mean little on their own.** One submitter held 16 of 78 papers on
  the first page; de-duplicating to one paper per submitter moves the whole picture. `calibrate`
  reports both, and the de-duplicated number is the honest one.

⛔ **NO ACCEPT/REJECT VERDICT EXISTS.** Across the corpus the union of `review_results` fields
contains no decision-like key, and no API response type carries one. The platform paper describes
acceptance by "at least three out of five accept votes"; what is deployed returns **one** reviewer
and no vote. Do not tell anyone a paper was "accepted" on aiXiv.

## 2 · ⛔ THE THREE TRAPS, EACH MEASURED

- **`is_public: 0` DOES NOT MAKE A SUBMISSION PRIVATE.** `aixiv.260822.000005` was submitted with
  `--public 0`; the record reads `is_public: 0` and **the paper is world-readable anyway** —
  `/abs/<id>` returns 200 with title, author, correspondence e-mail and abstract, and
  `/api/pdf/<id>` serves the file, verified from a runner with no credentials. **There is no
  rehearsal mode: every `submit` is a publication.** Treat the flag as metadata about intent, never
  as access control.
- **`category` must be EXACTLY THREE strings** — `[main_category, subcategory, specialization]`,
  drawn from `/api/categories`. This contract appears **nowhere** in `openapi.json`, which types the
  field as a bare array; it surfaced only as an HTTP 400 on a live submit. There is no "Cancer
  Biology" node.
- **THE PLATFORM'S VERSION LABEL IS NOT THE API'S VERSION FORMAT.** aiXiv shows and names versions
  as `v1.4`; `/api/get-review` and the review endpoints reject that with **HTTP 422** — *"version
  must be in the format 'X.Y' or 'X.Y.Z', e.g. 1.0, 2.1, 1.9.3"*. So the form a caller reads off the
  page, and the form this skill's own examples used to print, is the one form that fails. The client
  now strips a leading `v` at the request boundary (only when a digit follows, so `velocity-2`
  survives) and keeps the labelled form in filenames and logs, which is what a human matching an
  artifact against the aiXiv page is looking at.
- **`GET /api/get_pending-review-submissions` TAKES ITS TOKEN AS A QUERY PARAMETER, AND REJECTS THE
  AGENT TOKEN ANYWAY.** A bearer header gets HTTP 422 (`{"loc":["query","token"]}`); the agent
  token in the query string gets HTTP 401 `"Invalid token"`. So the queue aiXiv's own scheduler
  polls is **not readable with the credential this client holds**, and "is my version queued?" has
  no answer available to us. ⛔ **And the query-parameter form is a credential-in-a-URL**: it reached
  an exception string and printed into a world-readable Actions log, where only GitHub's secret
  masking hid it. `_redact` now strips it at the request layer. **Masking is a backstop, not a
  control.**
- **Cloudflare answers urllib's default User-Agent with HTTP 403 "error code: 1010".** That is an
  EDGE verdict on the client's browser signature, not an API verdict on your token — and it reads
  exactly like a bad credential. The client sends a browser UA for this reason; do not remove it.

## 3 · ★★ WHAT MOVES A RATING, AND WHAT DOES NOT

**Four versions of one paper, four `Official Agent` reviews, every one rated 6:**

| version | what changed | rating |
|---|---|---:|
| v1.0 | baseline | 6 |
| v1.1 | named proteasomal cleavage and TAP; stated cross-locus LD | 6 |
| v1.2 | searched 127,090 unreviewed proteome entries — a new measurement | 6 |
| v1.3 | reframed to lead with the paper's own finding | 6 |

⛔ **POLISH IS NOT THE BINDING CONSTRAINT.** v1.2's review called the paper *"rigorous, transparent,
and intellectually honest"* with *"exceptional clarity"* — and scored it 6. Closing findings did not
move it either.

⚠ **AND ONE WEAKNESS RECURRED IN EVERY ROUND: "purely computational scope without experimental
validation."** No revision this programme can make will close that, because there is no wet lab. A
paper whose shape invites that finding is capped, and iterating on it is spend without a return.

★ **BUT "NO EXPERIMENTS" IS NOT ITSELF THE CEILING.** The corpus's top-rated work includes pure
mathematics with no experiment at all — a 10 for solving an open problem from 1967, an 8 for a
proved identity in modular representation theory. What the high scorers share is that each
**delivers a finding**: a theorem, a measured effect, a constructed benchmark. What sits at 4–6 is
the *assessment* — a careful survey of a state of play.

**So the lever is the paper's shape, decided before it is written:** a paper that establishes
something others can be wrong about scores; a paper that reports how things stand does not, however
well it is done. Reframing an existing assessment to lead with its finding was tried (v1.3) and was
not enough on its own.

### ⭐ THE PREDICTION WAS TESTED, AND IT HELD

`nr4a3-fusion-transcriptional-output` — a paper that SUPPLIES AN INSTRUMENT (a size-matched
empirical null for gene-set reads on small series) and says outright that its application is a worked
example rather than the contribution — was posted as `aixiv.260823.000001` and rated **7 on its first
version**, by the same `Official Agent` that rated the assessment paper 6 four times running.

Its review names exactly the properties this section predicted: *"the careful construction of an
empirical null, the transparent reporting of negative and ungradeable results, and the exhaustive
literature curation."*

⚠ **And it names the remaining ceiling honestly**: *"the manuscript's primary contribution is a
cautionary null, not a new biological discovery."* So a delivered instrument reaches 7; a positive
finding is what the 8s and 10s carry. **Pick the paper, do not iterate the prose** — one submission of
the right shape beat four revisions of the wrong one.

## 4 · The runbook

1. **Mint an agent token once.** `POST /api/agents` with `review` in `scopes`, then
   `POST /api/agents/{id}/tokens` — shown once. Store as the `AIXIV_TOKEN` Actions secret; the dev
   sandbox cannot hold it, so every authenticated call originates in CI.
2. **`mode=verify`** — read-only. Confirms the token works **and that an agent carries the `review`
   scope**, which a plain 200 does not tell you. Prints an allowlist of fields, never the response
   body: this repository's Actions logs are world-readable and `/api/profile/me` returns the
   account's e-mail. A 401 from `/api/profile/me/status` is EXPECTED — an agent token is not a Clerk
   user JWT.
3. **Generate the metadata, never hand-write it.**
   [`build_aixiv_metadata.py`](./research/manuscripts/build_aixiv_metadata.py) reads title and
   abstract from the manuscript so the version of record cannot drift from what a reader is told.
   ⚠ Its markdown-to-plain transform is the part that breaks: it once left `"melanoma , which"` and
   turned `HLA-B\*15:01` into `HLA-B\15:01`. Tests assert output **properties**, not agreement with
   a second copy of the same regex.
4. **`mode=dry-run-submit`** — prints the exact payload and needs **no token**, so checking metadata
   never requires holding the credential.
5. **`PREFLIGHT_FULL=1`** before any post. Outward-facing (`repo-gates`).
6. **`mode=submit`** (or `new-version`) — double-gated: the workflow input *and* the script's
   `--i-understand-this-is-outward-facing`. A new version does **not** withdraw the old one; aiXiv
   keeps both rows under the same id.
7. **Wait — and the wait is LONG and IRREGULAR.** ⛔ **THE REVIEWER IS VERY LOW VOLUME, AND THE
   REVIEW IDs PROVE IT.** Our four versions carry review ids **1362, 1363, 1364, 1365 — consecutive
   in aiXiv's global sequence.** Ids are assigned platform-wide, so consecutive ids across four of
   our reviews means **no other paper anywhere on aiXiv was reviewed in between**. The gaps between
   those runs, on our own record: **1.2 h, 5.5 h, 1.0 h**.
   ⚠ **So an empty `fetch` at two hours is not evidence of anything.** `v1.4` was still unreviewed at
   2 h, which sits comfortably inside an observed gap of 5.5 h. Budget **hours, not minutes**, space
   the re-dispatches accordingly, and do not build a theory on an early empty result — I built two
   (a three-minute cadence, then an hourly one) and both were wrong.
   ⚠ **Still unmeasured:** a post time and its own review's `create_time` on one clock. The gaps
   above are between REVIEWS, not from post to review, and they bound the latency from below only. `fetch` commits the review to the branch via
   `publish_artifacts.sh` so a hardening round can cite it by path.
   ⚠ **An empty `review_list` is an absent reading, not a pass** — and polling the *committed file*
   is not polling aiXiv: that file only changes when a `fetch` run commits it, so a loop watching
   the branch after a single dispatch watches a static file forever. Re-dispatch each check.
   ⚠ **aixiv.science is not reachable from the dev sandbox** (403 at the egress proxy), so every
   check costs a CI dispatch. Space them to the cadence above rather than polling per minute.
8. **`mode=calibrate`** before quoting any rating.

⛔ **`start_attack_review` RETURNS HTTP 500** (measured twice, 2026-08-22 and 2026-08-23). The manual
re-review path is broken server-side, so a review cannot be re-run on a fixed version and the
**variance of the score is unmeasurable**. Reviews arrive automatically, one per new submission.
`fetch` is the normal path; `review` is a broken override.

## 4b · ⛔⛔ READ THE BUILT PDF BEFORE YOU POST IT. THE REVIEWER READS THAT, NOT THE MARKDOWN

Every gate in this repository reads the **manuscript source**. `lint_consistency`, `lint_claims`,
`lint_style`, the one-of-a-pair number guards — all of them open the `.md`. **Nothing was reading the
PDF**, which is the only artifact a reviewer ever sees. Two defects rode four published versions of
one paper because of that, and both were found in about a minute by extracting the PDF's text:

- **Markdown backslash escapes were never unescaped.** `build_submission_pdf.py` had no rule for
  `\*`, so `HLA-B\*15:01` reached the emphasis pass with its backslash intact and its asterisk live.
  One escaped allele on a line printed `HLA-B\15:01`. **Two on a line was worse**: the span between
  their live asterisks parsed as emphasis, so `HLA-A\*01:01, HLA-B\*07:02` came out as `HLA-A\` +
  *italic* `01:01, HLA-B\` + `07:02` — both allele names destroyed and unrelated text italicised.
  The paper carries 35 escaped alleles and its entire subject is which HLA alleles present a peptide.
  ⚠ **The one-allele case passes a naive test.** A guard that checks a single escaped allele is green
  throughout the incident, because one asterisk never triggers the emphasis rule. **Test two.**
- **The venue banner on page 1 was false.** It read *"prepared for deposit as a bioRxiv preprint and
  is not yet posted"* while the paper was posted on aiXiv and being read there. A venue banner is a
  claim like any other and goes stale the moment the deposit happens.

**So the step, before every post:**

```python
import pypdf
t = "\n".join(p.extract_text() for p in pypdf.PdfReader(PDF).pages)
assert t.count("\\") == 0                 # no markdown escape survived
for probe in (lead_peptide, lead_allele, "Table 1"):
    assert probe in t                     # note: the builder emits `Table\xa01`
```

⚠ Extraction quirks are not defects: a non-breaking space between "Table" and its number, and
hyphenless line joins, are how the typesetter works. **A backslash is a defect.** Check the count,
not the appearance.

## 5 · Where aiXiv sits in the portfolio

⛔ **It is a preprint server, not a publication venue**, whatever its paper says. No registered DOI
(the `doi` field merely echoes the record's own `aixiv_id`, no `10.xxxx/` registrant; Crossref
returns 0 results), **absent from Europe PMC's indexed list**, and `venue` is null on 99 of 100
public submissions. It cannot discharge a route's endpoint in
[L3](./systems/views/L3-publications.md), and it is **not** a substitute for an indexed host.

★ **What it is genuinely good for:** a fast, free external adversarial read with no
organizational-affiliation gate — which matters here, because bioRxiv declined this author for being
unaffiliated. The review **text** has earned its place: it produced the unreviewed-proteome search,
a real measurement now in the paper. **Use the text; do not chase the number.**
