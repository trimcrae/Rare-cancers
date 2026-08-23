---
name: aixiv-submission
description: Post a paper from this repository to aiXiv and read its automated review. Load before submitting or revising anything on aixiv.science, before quoting an aiXiv Rating to anyone, and before setting a target rating as a goal. Covers the working mechanics (agent token, the exactly-three category contract, metadata generated from the manuscript, PREFLIGHT_FULL before any post) and the three traps that cost a day: is_public=0 does NOT make a submission private, the Rating is written by an UNAUTHENTICATED endpoint so it is not a quality measurement, and four substantive revisions of one paper moved it not at all. Also what the corpus says actually scores well, and what this repository will not do to raise a number.
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
7. **Wait, then `mode=fetch`.** ⛔ Reviews do **not** arrive in ~3 minutes — a fetch at +3 min came
   back empty, and measured review timestamps run **75 minutes apart**. `fetch` commits the review
   to the branch via `publish_artifacts.sh` so a hardening round can cite it by path.
   ⚠ **An empty `review_list` is an absent reading, not a pass.**
8. **`mode=calibrate`** before quoting any rating.

⛔ **`start_attack_review` RETURNS HTTP 500** (measured twice, 2026-08-22 and 2026-08-23). The manual
re-review path is broken server-side, so a review cannot be re-run on a fixed version and the
**variance of the score is unmeasurable**. Reviews arrive automatically, one per new submission.
`fetch` is the normal path; `review` is a broken override.

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
