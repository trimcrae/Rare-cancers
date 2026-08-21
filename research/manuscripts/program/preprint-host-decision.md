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

## Why bioRxiv said no, in bioRxiv's own words

The refusal is not a screening judgement. It is an **account-level requirement**, stated on the
submission page itself and retrieved at HTTP 200 on 2026-08-21
([`preprint-host-eligibility.json`](../../literature/preprint-host-eligibility.json),
target `biorxiv_submission_guide`):

> "Authors wishing to deposit manuscripts must first register on the site and supply an affiliation
> so there is an entity providing oversight we can contact in the event concerns are raised about
> research misconduct."
> — [bioRxiv, *Submit a manuscript*](https://www.biorxiv.org/submit-a-manuscript)

⭐ **Three things follow, and they matter more than the refusal itself.**

1. **The requirement is not "a university".** It is *an entity that can be contacted about
   misconduct*. That is a wider set than an academic post, and it is the only thing bioRxiv says the
   affiliation is for.
2. **Affiliation appears nowhere in bioRxiv's screening criteria**, which its published screening
   procedure gives as plagiarism, non-scientific content, inappropriate article types, and material
   that could endanger patients or the public — *"Approximately 5% of bioRxiv submissions are found
   not to meet our criteria for posting"*
   ([screening procedures](https://connect.biorxiv.org/news/2022/06/13/screening_procedures)). So
   this was a registration gate, not a verdict on the science, and it says nothing about the
   manuscript.
3. **There is therefore nothing here to appeal.** An appeal argues that a judgement was wrong; a
   registration requirement is satisfied or it is not. The routes that would satisfy it are an
   affiliated co-author, or a named organisation willing to stand as the contactable entity — both
   of which cost a person, and neither of which is a reason to delay posting elsewhere.

## What each host says

Retrieved 2026-08-21 into
[`preprint-host-eligibility.json`](../../literature/preprint-host-eligibility.json). Every cell below
is a reading of the stored page, and the quotations are checkable against it.

| Host | Unaffiliated author may post | $0 | DOI + versions | In Europe PMC's indexed list |
|---|---|---|---|---|
| **bioRxiv** | ❌ **no** — an affiliation naming a contactable entity is required at registration | yes | yes | yes |
| **arXiv** (q-bio) | ⚠ **conditional** — needs endorsement | yes | yes | yes |
| **Zenodo** | ✅ **yes** — *"Eligible depositors: Anyone may register as user of Zenodo"* | yes | yes (DataCite) | ❌ **no** |
| **Research Square** | ⏳ pending | yes | yes | yes |
| **Qeios** | ⏳ pending | ⏳ pending | yes | yes |
| **OSF Preprints** | ⏳ pending | yes | yes | ⚠ **disputed — see below** |
| **ChemRxiv** | ⏳ pending | yes | yes | yes |
| **Preprints.org** | ⏳ pending | ⏳ pending | yes | yes |
| **SciELO Preprints** | ⏳ pending | ⏳ pending | yes | yes |

### arXiv — the obstacle is a person, not an institution

arXiv's gate is **endorsement**, and its help page is explicit about what an author without an
institutional address must do:

> "If you are the submitting author or have claimed papers but do not have an institutional email:
> you will need to update your email address to an institutional email. Alternatively you can seek
> personal endorsement from an established arXiv author."
> — [arXiv, *Endorsement*](https://info.arxiv.org/help/endorsement.html)

That is a solvable obstacle of a different kind: it costs one willing established author in q-bio,
which the outreach list this programme already maintains could plausibly supply. It is not a
same-day route, so it does not compete for the immediate posting.

### Zenodo — the floor, and why it cannot be the audience

Zenodo's policy answers the eligibility question outright, and it is the only host in the table that
does so in a single sentence:

> "Eligible depositors: Anyone may register as user of Zenodo. All users are allowed to deposit
> content for which they possess the appropriate rights."
> — [Zenodo, *Policies*](https://about.zenodo.org/policies/)

⛔ **And it is absent from Europe PMC's indexed-server list**, which is not an oversight: Europe PMC
requires that a preprint carry **a Crossref DOI**, and Zenodo issues **DataCite** DOIs
([Europe PMC, *Preprints*](https://europepmc.org/Preprints); [Zenodo,
*Principles*](https://about.zenodo.org/principles/)). A Zenodo record is a citable, versioned,
permanent deposit — it is not a preprint a sarcoma researcher's literature search will surface.
**Use it as the floor it already is, and do not mistake it for the channel.**

### ⚠ OSF Preprints — two sources disagree, and this memo does not resolve it silently

The Center for Open Science's own product page says preprints on its platform *"are indexed in Web
of Science, Google Scholar, OpenAlex, Europe PMC, and others"*
([COS, *OSF Preprints*](https://www.cos.io/products/osf-preprints)). **Europe PMC's own list does not
name OSF Preprints.** It names four OSF-hosted community servers — PsyArXiv, MetaArXiv, EcoEvoRxiv
and PaleorXiv — and none of them is a cancer-biology venue. The likeliest reconciliation is that
indexing is per-community rather than platform-wide, which would mean the generic OSF Preprints
server is **not** a route into Europe PMC for this work. That is a reading, not a finding, and it is
the one open question in the table that a fetch has not closed.

### Discovery is a named list, and that is what makes it checkable

Europe PMC publishes the servers it indexes and the criteria a server must meet — public content,
API-readable metadata, a public screening statement, a public ethics statement, at least 30
preprints, and a **Crossref DOI** as the identifier ([Europe PMC,
*Preprints*](https://europepmc.org/Preprints)). ⚠ **PubMed is a separate and much narrower
question**: preprints reach PubMed only through the NIH Preprint Pilot, which covers *"preprints
resulting from research funded by the National Institutes of Health"*
([NLM, *NIH Preprint Pilot*](https://www.ncbi.nlm.nih.gov/pmc/about/nihpreprints/)). This programme
has no NIH funding, so **no preprint host reaches PubMed for this work**, and any plan that assumed
otherwise was wrong about a channel rather than about a server.

