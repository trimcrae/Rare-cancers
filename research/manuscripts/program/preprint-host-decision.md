---
id: DOC-PREPRINT-HOST-DECISION
title: Where an unaffiliated author's preprints go, after bioRxiv declined one
level: L3
kind: manuscript
status: live
canonical_for: [preprint_host_choice]
purpose: decision memo, written to one question
scope: >-
  Preprint-host choice for every publication this programme aims at a preprint. It reports no
  scientific result, asserts nothing about any disease or agent, and is not a scientific record.
audience: [maintainers, autonomous research agents]
date: 2026-08-21
last_verified: unverified
---
# Where an unaffiliated author's preprints go, after bioRxiv declined one

> **Role: decision memo, written to one question.** *"Just heard back from bioRxiv with a rejection
> because I'm unaffiliated. We need a preprint host that allows unaffiliated researchers"*
> (trimcrae, 2026-08-21.) It ranks the candidate hosts on what each one **says** about who may post,
> and says what changes in the repository once one is chosen.

## The exposure is not one paper

`systems/graph/publications.json` aims **23 of its 32 publication endpoints at `target_venue:
preprint`** — derived, not typed:

```bash
python3 -c "import json; p=json.load(open('systems/graph/publications.json')); \
print(sum(1 for x in p if x.get('target_venue')=='preprint'), 'of', len(p))"
```

Two of them are immediate rather than eventual:

- **The ASO paper** (`aso/fusion-junction-aso-research-article.md`) is the one that was submitted.
  It is graded against a `bioRxiv-preprint` venue record in
  [`submission_metrics.py`](../submission_metrics.py) and appears in
  [`SUBMISSION-PACKET.md`](../SUBMISSION-PACKET.md) under *"bioRxiv (preprint; journal venue still
  open)"*. Its masthead already reads *"Prepared for deposit; not yet posted"*, so nothing has to be
  retracted — only re-aimed.
- **The degrader paper's plan of record is ChemRxiv**
  ([`nr4a3-degrader-preprint-plan.md`](../degrader/nr4a3-degrader-preprint-plan.md)), and that plan
  confirmed ChemRxiv's **fee** in writing while never reading its **eligibility** rule. A second
  route losing its terminus for the same reason is the failure this memo exists to prevent, which is
  why ChemRxiv is tested here alongside the replacements rather than assumed safe.

## Four tests, and a host has to pass all four

A host that takes the paper and is invisible to the field is not a route to a reader — CLAUDE.md §5
holds that the published record is the only channel by which any of this reaches a patient. So:

| # | Test | Why it is a gate rather than a preference |
|---|---|---|
| 1 | **Eligibility** — an unaffiliated author may post, in the server's own words | The reason this memo exists. |
| 2 | **Cost** — $0 | The programme's standing fee constraint; the precedent is [`venue-fee-routes-2026-08-10.json`](../../literature/venue-fee-routes-2026-08-10.json), where "hybrid" turned out never to mean "free". |
| 3 | **Persistence** — a DOI, and versioning | The plan of record is a *living* preprint bumped v2, v3 as routes change ([`emc-treatment-strategy.md`](./emc-treatment-strategy.md), tier B). A host without versions cannot carry it. |
| 4 | **Discovery** — indexed where a sarcoma researcher looks | Europe PMC, Crossref, Google Scholar. This is the half a host comparison usually skips. |

## The floor, which is already built and needs no one's permission

⭐ **The worst case is not "no DOI". It is "no preprint-server audience".**
[`scripts/zenodo_deposit.py`](../../../scripts/zenodo_deposit.py) and
[`deposit-zenodo.yml`](../../../.github/workflows/deposit-zenodo.yml) already build a **per-paper**
Zenodo deposition from that paper's own archive manifest and **reserve its DOI before the files
freeze**, so the paper and the archive it cites carry the same identifier. Zenodo asks a depositor
for no institution. Every paper in this programme can therefore be given a citable, versioned,
$0 DOI today, whatever any preprint server decides.

That is a floor, not the answer: a Zenodo record is a deposit, not a preprint server, and it does not
put the work in front of the readers a preprint server reaches. The ranking below is about the
audience, with the floor already secured.

## What each host says

⏳ **PENDING — this section is deliberately empty rather than plausibly filled.** The eligibility,
cost, persistence and indexing pages for bioRxiv, ChemRxiv, arXiv, OSF Preprints, Preprints.org,
Research Square, Zenodo, Qeios, SSRN, Authorea and ScienceOpen are being read with a headless
Chromium on a GitHub Actions runner, because this sandbox's egress proxy blocks every one of those
domains and bioRxiv 429s shared runner IPs on plain HTTP
([`preprint_host_policy_fetch.py`](../../../scripts/preprint_host_policy_fetch.py), the
`preprint-host-policy` arm of `fetch-literature.yml`). The verdicts go here, each quoting the
retrieved page.

⛔ **NOTHING GOES IN THIS TABLE FROM RECOLLECTION OR FROM A SEARCH SNIPPET.** That is the whole
reason the fetch exists: the assumption that a preprint server takes anyone is exactly the class of
unread assumption that once sent a venue decision to a publisher which no longer published the
journal ([`venue-fee-routes-2026-08-10.json`](../../literature/venue-fee-routes-2026-08-10.json)).

