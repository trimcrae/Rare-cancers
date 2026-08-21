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

⭐ **The decision letter, supplied by trimcrae 2026-08-21, and it is the authoritative record:**

> "We regret to inform you that your manuscript cannot be considered for bioRxiv because bioRxiv
> requires authors to have an organizational affiliation. It is necessary for submissions to be
> associated with an organization that provides oversight of research activities so that it can
> adjudicate any ethical issues/disputes that arise."
> — the bioRxiv team, to Tristan D. McRae, 2026-08-21

It matches the standing requirement on bioRxiv's own submission page, retrieved at HTTP 200 the same
day ([`preprint-host-eligibility.json`](../../literature/preprint-host-eligibility.json),
target `biorxiv_submission_guide`):

> "Authors wishing to deposit manuscripts must first register on the site and supply an affiliation
> so there is an entity providing oversight we can contact in the event concerns are raised about
> research misconduct."
> — [bioRxiv, *Submit a manuscript*](https://www.biorxiv.org/submit-a-manuscript)

⭐ **Three things follow, and they matter more than the refusal itself.**

1. **The requirement is not "a university".** It is *an organization that provides oversight of
   research activities* and can adjudicate a dispute. That is a wider set than an academic post, and
   it is the only thing bioRxiv says the affiliation is for.
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

*trimcrae, 2026-08-21: "I'd like you to revisit arXiv again since it seems dedicated to exactly the
research I'm doing here." Taken as arXiv's **q-bio** (Quantitative Biology) archive, and it holds on
the merits rather than only on eligibility — this is a computed, no-wet-lab result, which is q-bio's
remit and is exactly what bioRxiv's experimental-biology readership is not selected for. A dedicated
probe writes to `research/literature/arxiv-aso-route.json`.*

arXiv's gate is **endorsement**, and its help page is explicit about what an author without an
institutional address must do:

> "If you are the submitting author or have claimed papers but do not have an institutional email:
> you will need to update your email address to an institutional email. Alternatively you can seek
> personal endorsement from an established arXiv author."
> — [arXiv, *Endorsement*](https://info.arxiv.org/help/endorsement.html)

⭐ **Three properties make this a different kind of obstacle from bioRxiv's, and a better one.**

- **It is one person, once, for the whole archive.** *"most high-level subject areas (e.g., hep-th,
  cond-mat, q-bio) are currently endorsement domains"* and *"at least one positive endorsement is
  required per endorsement category"* — so a single q-bio endorsement covers q-bio.GN, q-bio.BM and
  q-bio.QM together, and every later paper in the same domain.
- **arXiv publishes who can give it.** Its instructions are to open the abstract page of a related
  arXiv paper and follow *"Which authors of this paper are endorsers?"* — a named, public list, not
  a search for goodwill. The endorser must have papers in the domain submitted between three months
  and five years ago.
- **It is not peer review.** *"We do not expect you to read the paper in detail, or verify that the
  work is correct, but you should check that the paper is appropriate for the subject area."*

### What arXiv would want changed, and what it would not

Read from [arXiv's moderation policy](https://info.arxiv.org/help/moderation/index.html) and
[submission guidelines](https://info.arxiv.org/help/submit/index.html):

| Requirement | Where this paper stands |
|---|---|
| Accepted formats are *"(La)TeX … PDF, HTML"*, and arXiv refuses *"PDF created from TeX/LaTeX source"* | ✅ **submittable as built.** `build_submission_pdf.py` prints from HTML with Chromium's `Page.printToPDF`; there is no TeX source to withhold, so the prohibition does not reach it. |
| *"we now include in particular text-to-text generative AI among those that should be reported"*, and such tools *"should not be listed as an author"* | ✅ **already complied with.** The paper's *Use of AI tools* section names the models and the periods they covered, and lists no AI author. |
| Ancillary files (data, programs) may travel with the submission | ✅ fits the SI and the machine-readable tables the availability statement already names. |
| *"serious misrepresentations of … affiliation"* is a decline reason | ✅ the author block states *"Independent researcher, unaffiliated"*, which is the accurate statement, not a workaround. |

⚠ **And three risks that are real, stated rather than smoothed over.**

1. **arXiv describes itself as *"a forum for professional members of the scientific community"***, and
   its moderation policy says *"In some cases, authors may be required to establish a conventional
   publication record and limit their submissions to works that are published in conventional
   journals."* A first submission from an author with no publication record can meet exactly that
   response. Endorsement makes it much less likely; it does not remove it.
2. **Posting is close to irreversible.** *"Once a paper is announced it becomes part of the permanent
   scholarly record. arXiv will only consider requests for removal if the submitter did not have the
   legal right to agree to the license."* Versions are fine — removal is not. A living preprint is
   compatible with that; a paper posted before it was ready is not.
3. ⛔ **The submission-rate rule bites a 23-endpoint programme.** *"There is a practical limit to the
   rate at which appropriate, independent submissions can be produced by any one person. We may
   request that a particular author limit their submission rate"*, with a stated ceiling of *"no more
   than three papers per day"* for a back catalogue. This portfolio plans many preprints from a
   single author, and a burst would attract precisely the scrutiny in risk 1. **Post them spaced, and
   post the strongest first.**

⚠ There is one open item on this route: arXiv's endorsement help page links a blog post about
**changes** to the endorsement process, and a December 2025 change removed institutional e-mail as a
sole qualifier for Mathematics with a January 2026 post extending it. If institutional e-mail no
longer qualifies anyone automatically, an unaffiliated author is in the *same* position as every
other new author — which would be a materially different finding from being locked out. Both posts
are being read at primary source rather than trusted from a search summary.

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


### ⛔ MEASURED, AND IT REVERSES THE arXiv READING FOR *THIS* PAPER

arXiv instructs an author to find an endorser among the authors of related arXiv papers. So "who
could endorse this paper" is answerable by counting, and
[`arxiv-aso-route.json`](../../literature/arxiv-aso-route.json) counts it against arXiv's own API:

| Query over `cat:q-bio*` | Total results in all of arXiv |
|---|---|
| `"antisense oligonucleotide"` OR `gapmer` | **1** |
| `"off-target"` AND (`oligonucleotide` OR `siRNA` OR `ASO`) | **1** |
| `"fusion oncogene"` OR `"fusion transcript"` OR `"gene fusion"` | 7 |
| `sarcoma` OR `"rare cancer"` | 16 |

The single antisense hit is a machine-learning retention-time paper in `q-bio.OT` (2025-11); the
single off-target hit models siRNA endosomal escape (`q-bio.QM`, 2024-12). The gene-fusion hits are
bioinformatics-method papers, several of them a decade old.

**Two conclusions, pointing the same way.** There is no in-domain endorser pool — arXiv's own
recommended route to endorsement has essentially one paper to start from. And the readership is not
there either: the nucleic-acid-therapeutics community does not read q-bio. ⚠ **The intuition that
q-bio is "dedicated to exactly this research" is true of the METHOD — computed, no wet lab — and
false of the SUBJECT.** For a methods paper about doing rigorous no-wet-lab oncology, q-bio would be
a good home. For a fusion-junction ASO design paper whose intended readers run oligonucleotide
experiments, it is a quiet room.

### aiXiv — the right idea about this programme, the wrong room for this paper

[aiXiv](https://arxiv.org/abs/2508.15126) is a real and recent platform (Guowei Huang, University of
Manchester) that accepts AI- and human-authored work and runs AI reviewers for baseline quality
control, on the stated principle that *"we should only care about quality - not who produced it"*
([Science, 2025](https://www.science.org/content/article/new-preprint-server-welcomes-papers-written-and-reviewed-ai)).
It has no organizational-affiliation gate, and it is the one venue whose framing matches how this
programme actually works.

⛔ **And it fails the discovery test harder than any other candidate.** As of a mid-November 2025
update it hosted *"just a few dozen papers"*, submissions are being posted while its AI reviewers are
still being refined, and it is **absent from Europe PMC's indexed-server list** - the same list that
decides whether a sarcoma researcher's literature search can ever surface the work. A bioethicist
quoted in the same Science piece warns the operators must *"be vigilant to ensure aiXiv does not
become a dumping ground"*.

⚠ **There is also a framing cost, and it is not snobbery.** This paper needs a wet-lab sarcoma group
to pick it up and test it. Posting it in a venue defined by AI-generated research invites that
audience to weigh the provenance rather than the argument. The paper's own *Use of AI tools* section
already discloses the tooling honestly, in the place a reader expects it; the venue does not need to
make the same statement a second time and louder.

**Where aiXiv does earn a place:** as the home for a paper *about* the programme - the modality
census, or a methods paper on running a rigorous computation-only oncology programme with AI
scientists. That is a paper whose subject IS what aiXiv exists for. Keep it on the list for that.

## The call, for the EMC ASO paper

**Post it to Research Square.** It clears all four tests with no gatekeeper: free, Crossref DOI,
versioned, on Europe PMC's indexed list, and its screening is for *"complete author information,
appropriate declaration statements, and potential risks to human health"* - none of which is an
organizational-affiliation requirement. Preprints.org is the equivalent second choice; it asks for an
institutional e-mail *"where possible"* and accepts an ORCID instead, which this author has.

Neither arXiv nor aiXiv is the right room for this particular paper, for the measured reasons above,
and neither failure is about eligibility.
