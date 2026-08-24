---
id: DOC-PREPRINT-HOST-DECISION-ROUND2
title: Where the extended ASO report goes after Research Square, and the test the first memo did not have
level: L3
kind: manuscript
status: live
canonical_for: [preprint_host_choice_after_research_square]
purpose: >
  Reopen the preprint-host choice for the EXTENDED fusion-junction ASO report, whose destination was
  decided by DOC-PREPRINT-HOST-DECISION on 2026-08-21 and refuted on 2026-08-24 when Research Square
  declined it. It adds the test that memo did not have, re-reads the candidates at primary source,
  and separates what is established from what two rounds of fetching still cannot reach.
scope: >
  Preprint-host choice only. It reports no scientific result and asserts nothing about any disease,
  sequence or agent. It selects no venue: choosing one and submitting to it are the author's, per
  CLAUDE.md §3.
audience: [maintainers, autonomous research agents]
date: 2026-08-24
last_verified: 2026-08-24
---

# Where the extended ASO report goes after Research Square

> **Role: decision memo, second round.** It supersedes the CALL of
> [`preprint-host-decision.md`](./preprint-host-decision.md) and nothing else in it. That memo's
> four tests, its bioRxiv reading, its arXiv measurement and its Zenodo floor all stand.

## 1 · What was refuted, and it was the call rather than the reasoning

The first memo's call was **"Post it to Research Square. It clears all four tests with no
gatekeeper."** Research Square declined the manuscript at screening on 2026-08-24 and its §11
refuses appeals.

⛔ **THE ROOT CAUSE IS A 404 NOBODY READ AS A GAP.** That call rested on this sentence:

> "Screened for complete author information, appropriate declaration statements, and potential risks
> to human health"

which is a **marketing bullet** from `researchsquare.com/preprints`, not the Editorial Policies. The
Editorial Policies fetch is in the same corpus, under `research_square_policies` in
[`preprint-host-eligibility.json`](../../literature/preprint-host-eligibility.json): it was pointed at
`researchsquare.com/publishers/preprint-policies`, returned **404 on all four attempts**, and was
recorded `status: None`. The real path is `/legal/editorial`. So the content-type list and the full
screening list had **never been read in this repository** until trimcrae pasted the page on
2026-08-24 ([capture](../../literature/research-square-editorial-policies-2026-08-24.md)).

★ **AND THE BULLET CONTAINED THE WARNING.** *"Potential risks to human health"* was on it the whole
time. The memo tested that list for whether **affiliation** was on it — it is not — and never asked
whether **this paper** was. ⚠ *That is the generalisable defect, and it is not "we used the wrong
URL": a `status: None` row in a fetch corpus is an **unanswered question wearing the costume of a
reading**, and the prose above it was written as though the row had answered.*

## 2 · The fifth test, which is the one that actually fired

The first memo's four gates were **eligibility, cost, persistence, discovery**. Every one of them
graded a property of the SERVER. None graded whether the server would take **this manuscript**.

| # | Test | Status |
|---|---|---|
| 1 | Eligibility — an unaffiliated author may post | unchanged, and it was **never the binding constraint at Research Square** |
| 2 | Cost — $0 | unchanged |
| 3 | Persistence — DOI and versions | unchanged |
| 4 | Discovery — on Europe PMC's indexed list | unchanged; the list was **re-read 2026-08-24** and is byte-identical to the 2026-08-21 reading, 34 servers, nothing added or removed |
| **5** | **⭐ CONTENT SCREEN — would this server's public-harm screen decline THIS paper** | **NEW. It is what declined it.** |

⛔ **TEST 5 IS NOT A RESEARCH SQUARE QUIRK. IT IS UNIVERSAL AT REPUTABLE LIFE-SCIENCE SERVERS, AND
THAT IS THE FINDING THAT GOVERNS THE WHOLE CHOICE.** Read at primary source, 2026-08-24
([`browser-fetch.json`](../../literature/browser-fetch.json)):

**bioRxiv**, whose second screening stage is volunteer Principal Investigators:

> "Affiliates consider two main questions: Does the manuscript present biological research? And **is
> there potential for public harm from posting it as a preprint?**" … "A submission may also be
> declined as better disseminated after peer review, **most often because of the potential negative
> impact of the findings on the public**." … "Approximately 5% of bioRxiv submissions are found not
> to meet our criteria for posting."

**Research Square** §6:

> "…and **inappropriate, alarming, highly controversial, or pseudoscientific claims**. Articles with
> strong conclusions, especially in the absence of fully accessible data, may also be screened out."

⭐ **AND THIS IS NO LONGER AN INFERENCE FROM TWO SERVERS — A THIRD CARRIES THE SAME TWO CLAUSES,
NEARLY WORD FOR WORD.** Preprints.org, read 2026-08-24 from a 2026-06-13 archive snapshot
([capture](../../literature/preprints-org-screening-2026-06-13-snapshot.md)), screens for content
that does not contain *"harmful, provocative, controversial, or pseudoscientific statements"* and
rejects *"manuscripts drawing strong conclusions without fully accessible supporting data"*. Set
beside Research Square §6 — *"inappropriate, alarming, highly controversial, or pseudoscientific
claims"*, *"articles with strong conclusions, especially in the absence of fully accessible data"* —
these are the same screen. **It is common preprint-server boilerplate, not one venue's house style,
and the first memo's second choice is therefore the same door rather than a way around it.**

**So swapping servers does not, on its own, clear the thing that fired.** A paper that prints
orderable 16-mers against a human oncogene, opens with a box of do-not-administer cautions, and is
authored by a person with the disease will meet this screen at every server that has one. ⚠ **The
cautions are not the defect** — they are correct and they should stay. They are, however,
load-bearing evidence *for* the screener, and pretending otherwise is how this gets refused a third
time.

## 3 · The candidates, re-read 2026-08-24

⛔ **TWO ROUNDS OF FETCHING CANNOT REACH FOUR OF THESE, AND THAT IS RECORDED AS UNKNOWN RATHER THAN
FILLED IN.** Preprints.org and ChemRxiv returned **403 to plain HTTP (2026-08-21) and to a real
headless Chromium (2026-08-24)** — bot protection keyed on TLS fingerprint, which a browser normally
defeats and here did not. A search summary is not a reading; that is the precise substitution that
produced the bioRxiv error.

| Host | 1 eligibility | 2 $0 | 3 DOI+ver | 4 Europe PMC | 5 content screen | overall |
|---|---|---|---|---|---|---|
| **Qeios** | ✅ no affiliation gate — affiliation appears only as "which one is primary"; ORCID recommended | ✅ "no Article Processing Charges (APCs), and no reader fees" | ✅ | ✅ indexed | ⭐ **the thinnest surface found.** Its Publishing Policy has **no screening section and no article-type list**, and says *"Researchers shall be free to pursue their research activity without being censored."* ⚠ See the two cautions below | **best fit on test 5** |
| **Preprints.org** | ✅ **CLOSED 2026-08-24 via web archive** — institutional email "where possible, **or email addresses used in previously published papers**"; ORCID recommended. Both fallbacks are open to this author. Not an affiliation gate | ✅ | ✅ | ✅ indexed | ⛔ **THE SAME SCREEN THAT DECLINED THIS PAPER**, in near-identical words: "harmful, provocative, controversial, or pseudoscientific statements" and "strong conclusions without fully accessible supporting data" | **passes 1–4, fails the same test 5** |
| **SciELO Preprints** | ✅ no affiliation item in the submission checklist | ✅ | ✅ | ✅ indexed | ⚠ not captured | ⛔ **one-shot**: the checklist requires authors to declare the manuscript *"não foi depositado e/ou disponibilizado previamente em outro servidor de preprints"* — posting here forecloses posting anywhere else |
| **ChemRxiv** | ⚠ **STILL UNKNOWN** — 403 live from every route, and the archive has **zero snapshots** of `/policies-and-procedures`, so that path is probably not the real one. Attempts and the real archived paths: [capture §last](../../literature/preprints-org-screening-2026-06-13-snapshot.md) | ✅ | ✅ | ✅ indexed | ⚠ unread. ⛔ The reported exclusion for *"materials that may pose a health or security risk"* is a SEARCH SUMMARY and is not evidence | unread; also the degrader paper's plan of record depends on this row |
| **medRxiv** | ⚠ its submit page carries **no** affiliation sentence, unlike bioRxiv's — but same operator, and registration was not reached | ✅ | ✅ | ✅ indexed | same screening family as bioRxiv | scope is clinical/health research; this is neither |
| **OSF Preprints** | ✅ affiliation is an optional paid institutional feature, not a gate | ✅ | ✅ | ❌ **the generic server is NOT on the list** — the four OSF communities that are (PsyArXiv, MetaArXiv, EcoEvoRxiv, PaleorXiv) are not cancer biology | — | **fails test 4** |
| **Zenodo** | ✅ | ✅ | ✅ | ❌ DataCite DOI, Europe PMC requires Crossref | n/a | the floor, already secured; not the channel |
| **aiXiv** | ✅ | ✅ | ✅ | ❌ not on the list | ✅ no comparable screen | ⚠ see §5 |
| **bioRxiv** | ❌ | — | — | — | — | closed 2026-08-21 |
| **Research Square** | ✅ | ✅ | ✅ | ✅ | ❌ **declined this paper** | closed 2026-08-24, no appeal |

**Named but unexamined**, all on Europe PMC's list: Authorea Preprints, SSRN, ScienceOpen Preprints,
AIJR Preprints, Access Microbiology, VeriXiv, Beilstein Archives. None has been read here. Two are
probably out on scope or eligibility grounds that have **not been checked** — Access Microbiology is
a Microbiology Society venue, VeriXiv is Gates-linked — and saying so is a guess, not a finding.

### ⚠ Two cautions on Qeios, neither of which is a disqualification

1. **"No screening section in the Publishing Policy" is not the same as "no screen."** Europe PMC's
   own indexing criteria require that a server *"have a screening procedure that is described in a
   public statement"*, and Qeios is indexed — so such a statement very likely exists on a page this
   fetch did not target. **The honest entry is that the Publishing Policy contains none, not that
   Qeios does not screen.**
2. ⛔ **ITS GENERATIVE-AI PERMISSION IS NARROWER THAN THIS PAPER'S DISCLOSURE, AND THIS IS THE ONE
   PLACE QEIOS FITS WORSE THAN RESEARCH SQUARE.** Qeios: *"Authors may use such tools **to improve
   the language and readability** of their manuscript, but this use must be disclosed."* This
   manuscript's declaration is far broader — an LLM wrote the analysis code, ran the pipelines,
   drafted and revised the text, and conducted internal review. Qeios does not forbid that; it
   simply does not address it, while granting a narrower permission by name. Research Square's §1.3,
   by contrast, requires only that LLM use be documented. **Do not present Qeios as the AI-safe
   choice — on the stated text it is the opposite.**

## 4 · What is genuinely open, and it is not only "which server"

Because test 5 is what fired and test 5 exists nearly everywhere, the server question is downstream
of a question about the submission itself. Both halves below are **the author's**, and the second is
one this repository's own rules forbid an agent to decide.

- **(a) Change nothing, and pick the server with the thinnest screen.** Fastest. Qeios today, with
  Preprints.org and ChemRxiv behind it once their policies are actually read.
- **(b) Change what a screener sees first, changing no caution and no claim.** A screener reads
  title → abstract → first box, and this paper's are a **52-word, 356-character** declarative
  quantitative conclusion, followed immediately by Box 1's cautions.
  ⛔ **AN AGENT MUST NOT DO THIS ON ITS OWN, AND THE RULE IS EXPLICIT.** CLAUDE.md §3: *"DO NOT
  RESHAPE A NAMED PAPER INTO A DIFFERENT ONE. Retitling or reframing the paper he asked for — to
  chase a score, a venue's taste or a reviewer's rubric — publishes something he did not ask for
  under the identifier he did."* Retitling to suit a screener is that rule's central case. It is
  **raised here as a factor and left with trimcrae**, and it is not done.

## 5 · aiXiv, since it is working and the question was asked

aiXiv has no affiliation gate, no comparable content screen, and this programme already posts there
(`aixiv.260822.000005`, the vaccine-path paper). **Its objection has never been eligibility and is
not weakened by the Research Square refusal:** it is **absent from Europe PMC's indexed-server
list**, re-read 2026-08-24 and unchanged. A sarcoma researcher's literature search does not surface
it. The first memo's second objection also stands — this paper needs a wet-lab group to pick it up,
and a venue defined by AI-generated research invites that audience to weigh provenance rather than
argument.

★ **That is an argument about REACH, not about legitimacy, and it does not make aiXiv wrong to use.**
Posting there is compatible with posting on an indexed server; nothing about it forecloses SciELO's
exclusivity clause except SciELO's own. **If the choice is between aiXiv and nothing, aiXiv wins** —
a paper nobody can find still beats a paper nobody can read.

## 6 · What this memo does not do

It selects no venue and submits nothing. Choosing the paper and the act is trimcrae's, per
CLAUDE.md §3, and the outstanding 403s mean two of the five candidates cannot honestly be ranked yet.
