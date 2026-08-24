---
id: DOC-PREPRINTS-ORG-SCREENING-SNAPSHOT
title: Preprints.org author instructions, from a 2026-06-13 web archive snapshot
level: L1
kind: register
status: live
canonical_for: ["every Preprints.org eligibility and screening statement this repository makes"]
purpose: >
  Hold, verbatim, the Screening and author-identification sections of Preprints.org's Instructions
  for Authors, so the candidate row for that server rests on the venue's own words rather than on a
  search summary. It closes a row that two rounds of live fetching could not reach.
scope: >
  L1. One publisher page, as archived 2026-06-13, unedited within the quoted blocks. It makes no
  scientific claim. It is a snapshot of a snapshot and decays twice over; both dates are stated.
audience: [maintainers, autonomous research agents]
date: 2026-08-24
last_verified: 2026-08-24
---

# Preprints.org — Instructions for Authors, as archived 2026-06-13

## ⛔ HOW THIS WAS OBTAINED, AND THE TWO DATES THAT BOUND IT

**This is an ARCHIVE READ, not a live one, and the distinction is the whole warranty.**
`www.preprints.org` returned HTTP 403 to plain urllib from the dev sandbox (2026-08-21), to a real
headless Chromium on a GitHub runner (2026-08-24), and to a local Chromium in this container, which
could not reach it at all — the sandbox egress proxy refuses the domain, and a control fetch of
`example.com` failed identically, so that leg proves nothing about the site.

What worked was the Internet Archive, which is not behind the same bot protection. Route, recorded so
it can be repeated: the CDX API (`web.archive.org/cdx/search/cdx?url=…&output=json&limit=-6`) lists
the newest snapshots, and `web.archive.org/web/<timestamp>id_/<url>` serves the archived bytes raw.
⚠ **The plain `web/2026/<url>` form does NOT work and looks like a site refusal**: it returned 403
with a body the same size as the live site's, i.e. it redirected to the origin. Only the timestamped
`id_` form stays inside the archive.

**Snapshot taken 2026-06-13. Read here 2026-08-24.** The same paragraphs were checked against a
2024-11-28 snapshot and the eligibility sentence is unchanged across the twenty months between them;
the Screening list has been expanded. Nothing here is evidence about the page as it stands today.

## ⭐ THE FINDING, AND IT IS THE REASON THIS CAPTURE MATTERS

**Preprints.org's screening list is near-identical to the one that declined this paper at Research
Square four days ago** — two of its clauses map almost word for word:

| Research Square §6 | Preprints.org, Screening |
|---|---|
| "inappropriate, **alarming**, highly **controversial**, or **pseudoscientific** claims" | "harmful, provocative, **controversial**, or **pseudoscientific** statements" |
| "Articles with **strong conclusions**, especially in the absence of **fully accessible data**, may also be screened out" | "Manuscripts drawing **strong conclusions without fully accessible supporting data** may also be rejected" |

⛔ **So Preprints.org is not a way around what happened. It is the same door.** This is the
strongest evidence yet for test 5 in
[`preprint-host-decision-round2.md`](../manuscripts/program/preprint-host-decision-round2.md): the
public-harm screen is not a Research Square quirk but common preprint-server boilerplate, and a
server swap alone does not clear it.

## The capture

### Author identification — the eligibility question, and it is NOT an affiliation gate

> In order to facilitate author identification, authors should use institutional email addresses
> (e.g., those provided by a university) **where possible, or email addresses used in previously
> published papers**. We recommend the use of ORCID identifiers.

★ **"Where possible" is a preference and the fallback is explicit.** This author holds an ORCID
(`0000-0002-1823-1451`) and has a previously published paper, so both named routes are open to him.
⚠ Read alongside the Screening clause *"All authors are genuine scholars; submissions with fake
names or email addresses may be rejected"* — aimed at fabricated identities, not at unaffiliated
ones, but it is the closest thing on this page to an eligibility judgement and it is a judgement
rather than a rule.

### Screening, verbatim

> **Screening**
>
> Preprints.org does not conduct peer review for submitted manuscripts. Upon submission, each
> manuscript undergoes a screening process to ensure the following: The content is written in
> English. The content has not been previously published. The content adheres to basic publishing
> ethics, and the authors comply with international research ethics regulations. The number of
> independent manuscripts an author can write is limited. Therefore, excessive submissions within a
> short period may require justification and could be rejected. All authors are genuine scholars;
> submissions with fake names or email addresses may be rejected. Authors disclose any potential
> conflicts of interest. The submission includes all necessary figures, references, and other
> critical components. The content does not contain harmful, provocative, controversial, or
> pseudoscientific statements. Manuscripts drawing strong conclusions without fully accessible
> supporting data may also be rejected. Any use of AI is clearly disclosed and conforms to our
> policy.
>
> Additionally, if an author submits multiple similar manuscripts or a new submission appears to be
> a revision of a recent one, we may request that the submissions be treated as new versions of the
> same work or reject them.
>
> **Preprints.org reserves the right to decline posting a preprint for reasons not explicitly stated
> above.** The screening process typically takes 24 hours by our trained editors during the working
> day.

### Two clauses that bear on this programme specifically

> The number of independent manuscripts an author can write is limited. Therefore, excessive
> submissions within a short period may require justification and could be rejected.

⚠ **This programme aims 23 publication endpoints at a preprint.** The same constraint arXiv states
as a submission-rate rule appears here as a screening criterion. It does not bite one submission; it
bites a burst, and the response is the same one the arXiv reading already reached — post them
spaced, strongest first.

> Any use of AI is clearly disclosed and conforms to our policy.

⚠ **UNREAD.** "Our policy" is a separate page this capture does not contain, and the extended
report's AI declaration is unusually broad. Do not record Preprints.org as AI-clear on the strength
of this sentence — it names a policy rather than stating one.

## ⚠ WHAT THIS CAPTURE DOES NOT CLOSE: ChemRxiv

ChemRxiv remains **UNKNOWN**, and the attempts are recorded so nobody repeats them:

- `chemrxiv.org/policies-and-procedures`, `/submission-guide`, `/faqs` — 403 live, from every route.
- The CDX API returns **zero snapshots** for `chemrxiv.org/policies-and-procedures`, so that path is
  probably not the real one. The archived policy paths are
  `chemrxiv.org/engage/chemrxiv/submission-information?show=submission-guide` and
  `?show=author-faq`.
- Raw `id_` fetches of those two returned nothing, most likely because the `?show=` query string
  does not survive the archive URL form.

Only `chemrxiv.org/terms` came back, from a **2020-10-02** snapshot — six years old, and terms of
use rather than a screening statement. ⛔ **It is not quoted here and must not be used to grade the
ChemRxiv row.** A search summary reporting that ChemRxiv excludes "materials that may pose a health
or security risk" is also not evidence; it is the substitution that produced the bioRxiv error.
