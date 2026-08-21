---
id: DOC-ASO-SUBMISSION-PLAN
title: "Venue and submission plan for the fusion-junction ASO paper"
level: L3
kind: memo
status: live
canonical_for:
  - the target venue for PUB-ASO and why
  - the submission checklist for the fusion-junction ASO manuscript
purpose: >
  The degrader paper's venue decision lives in nr4a3-degrader-preprint-plan.md and is
  chemistry-shaped (ChemRxiv + JCIM). This paper is an RNA-therapeutics paper and needs its own
  decision against the same binding constraint. This file is that decision and the checklist it
  implies. It does not restate the manuscript's science.
scope: >
  Venue, fee model, format requirements and submission mechanics only. No scientific claim is made
  here, and nothing here asserts efficacy, safety, a therapeutic window or clinical readiness.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-12
last_verified: 2026-08-12
---

# Venue and submission plan — the fusion-junction ASO paper

## 1 · The binding constraint comes first, because it eliminates most of the field

**NO PAY-TO-PUBLISH. AUTHOR PAYS $0** (trimcrae, 2026-07-05, stated for the degrader paper and not
specific to it). The journal must have a free **subscription or hybrid** route; the open copy is the
free preprint. This is not a preference to be traded against fit — it removes journals from
consideration outright, and it removes most of the obvious ones here.

| candidate | topical fit | fee model | verdict |
|---|---|---|---|
| **Nucleic Acid Therapeutics** (~~Mary Ann Liebert~~ → **SAGE**, see below) | the field's dedicated oligonucleotide-therapeutics journal; publishes design, mechanism and computational work | ⛔ **UNKNOWN — the Liebert-era assumption is void** | ◐ **TARGET, fee model unconfirmed** |
| Molecular Therapy — Nucleic Acids | excellent fit, higher profile | fully gold OA, APC mandatory | ❌ out on fee |
| Cancers / IJMS (MDPI) | would accept a computation-only paper | APC mandatory | ❌ out on fee |
| PLOS ONE · Scientific Reports · Frontiers | would accept | APC mandatory | ❌ out on fee |
| JCIM (ACS) | the degrader paper's venue; $0 subscription route confirmed | free route | ❌ out on **scope** — a small-molecule/computational-chemistry journal; this is an RNA paper |
| Briefings in Bioinformatics | methods-general | hybrid | ⚠ fallback, but the emphasis is wrong: this is a therapeutic-design paper, not a method paper |

**Plan of record: Research Square preprint (free) + Nucleic Acid Therapeutics, subscription route.**
⚠ *Superseded, retained: "bioRxiv preprint (free)". bioRxiv DECLINED this submission on 2026-08-21 —*
*"bioRxiv requires authors to have an organizational affiliation" — which is a registration gate and*
*not a verdict on the science, so nothing measured here is withdrawn. Ranked alternatives and the*
*reasoning: [preprint-host-decision.md](../program/preprint-host-decision.md).*
A general biology preprint server rather than ChemRxiv because the framing is biological rather than chemical — the degrader
paper's ChemRxiv choice does not transfer.

⛔ **THE PUBLISHER CHANGED, AND THE FETCH IS WHY WE KNOW (measured 2026-08-12).** The venue row
above was written from a Liebert-era assumption about the fee model, flagged in this file as a plan
rather than a retrieved fact. `venue_policy_browser_fetch.py` then read the three Liebert pages:
`home.liebertpub.com` returned **403** on both author-facing URLs, and the open-access URL
**resolved to `sagepub.com/journals/mary-ann-liebert-journals-transition-information`** — *"Mary Ann
Liebert journals transition information"*. **Nucleic Acid Therapeutics is now published by SAGE.**

Consequences, stated plainly:

- **The hybrid/free-subscription claim for this venue is withdrawn.** It rested on Liebert's model
  and Liebert no longer publishes the journal. It is not replaced by a claim that SAGE charges —
  that would be the same error in the other direction. It is **unknown**, and the $0 constraint is
  binding, so the venue cannot be committed to until it is read.
- **The fetcher now targets SAGE**: the transition page, the SAGE journal home for NAT, and SAGE's
  open-access and APC pages. The legacy Liebert URL is retained as a target so the 403 stays on the
  record rather than being quietly dropped.
- ⚠ **A 403 is not a policy reading.** Two of the three original targets refused a browser; that is
  a statement about anti-bot filtering, not about fees. Nothing may be inferred from it.

**This is what the "FEE/POLICY CONFIRMED IN WRITING" discipline is for.** Had the venue been chosen
and the fee model taken on trust, the paper would have been aimed at a publisher that no longer
publishes the journal.

### 1a · What the SAGE read returned, and exactly how far it goes

✅ **The $0 route exists at SAGE, and this is a reading rather than an assumption.** `sagepub.com`'s
open-access page (HTTP 200, resolved to `sagepub.com/journals/open-access`) states, verbatim:

> **"Hybrid Open Access (Sage Choice) Publish Open Access in hybrid subscription journals for an
> article processing charge"** … **"Green Open Access In our Green Open Access option you may share
> the Original Submission or Accepted Manuscript at any time after your paper is accepted and in any
> format"**

Both halves matter for the constraint. Hybrid means OA is an **optional** upgrade behind an APC, so
the subscription side is the free route; and Green OA means the accepted manuscript may be shared
*"at any time … in any format"*, which is the open copy without a fee — on top of the bioRxiv
preprint.

⚠ **AND HERE IS WHAT WAS NOT READ, WHICH MATTERS AS MUCH.** That page is SAGE's **portfolio-wide**
policy, not a statement about this journal. `journals.sagepub.com/home/nat` returned **403**, and the
APC-information URL did not resolve at all. So the chain is: *SAGE operates hybrid subscription
journals with a free route* → *NAT is now a SAGE journal* → **therefore NAT is probably hybrid**. The
last step is an inference, not a reading. A gold-OA journal inside a mostly-hybrid portfolio is an
ordinary thing to exist.

**Status: the venue is viable and not yet confirmed.** What would confirm it is one NAT-specific
page — author guidelines or the journal's own OA statement — read successfully. Until then the plan
of record stands with the inference named as an inference, and **no submission should be made on the
strength of this row alone.**

### 1b · THE DECISION (2026-08-12, trimcrae: *"Pick a venue"*)

⛔ **NAT COULD NOT BE CONFIRMED, AND THE RULE ABOVE SAYS THAT SETTLES IT.** Seven `journals.sagepub.com`
paths were put to a real headless browser across two runs — the journal home, author instructions,
aims and scope, and the description page — and **all seven returned 403**, exactly as Wiley and
Elsevier do. That is bot detection rather than a paywall, so it is not a statement about fees; but
the $0 constraint is binding and this repository's own discipline is FEE CONFIRMED IN WRITING before
committing. A venue whose fee model cannot be read cannot be the venue.

✅ **THE PICK IS *CANCER GENE THERAPY* (Springer Nature), because its fee model WAS read.**
`nature.com/cgt/open-access` returned HTTP 200 and states verbatim that **"Authors who publish open
access in Cancer Gene Therapy are required to pay an article processing charge (APC)"**, refers to
**"our subscription licensing terms"**, and frames the journal among **"hybrid journals"**. Open
access is therefore the optional paid upgrade and **the subscription route is the free one** — the
$0 route, confirmed at primary source rather than inferred from a portfolio page. Scope: the journal
describes itself as *"the essential gene and cellular therapy resource for cancer researchers and
clinicians"*, and a junction-directed nucleic-acid therapeutic for a fusion-driven sarcoma sits
inside that.

⚠ **THIS IS A DECISION UNDER THE CONSTRAINT, NOT A JUDGEMENT THAT CGT IS THE BETTER JOURNAL.** NAT
is the better scientific fit — it is the field's dedicated oligonucleotide-therapeutics journal —
and it remains the preferred venue **the moment its fee model can be read**. The block is
bot detection, so **a human loading `journals.sagepub.com/home/nat` in an ordinary browser settles
it in seconds**, which is the one step this repository cannot take for itself. If that read shows a
subscription route, switch back to NAT before submitting; nothing in the manuscript is venue-specific.

⚠ **THIS WHOLE SUBSECTION IS SUPERSEDED BY §1c, WHICH FOLLOWS IT AND DISQUALIFIES CGT.** It is kept
because the reasoning is the reason the rule in §1c exists, and because the NAT paragraph above is
still live. ⚠ *Superseded, retained: "**Plan of record: bioRxiv preprint (free, immediately) →
Cancer Gene Therapy, subscription route.**"* The surviving half is unchanged: the preprint is
unaffected by the venue question and should not wait on it.

### 1c · ⛔ CGT IS DISQUALIFIED. ITS GUIDE WAS READ, AND IT CHARGES BY THE PAGE (2026-08-12)

**The guide was never missing; the URLs being guessed for it were.** `/cgt/for-authors` and
`/cgt/submission-guidelines` return 404 and do not exist. `nature.com/cgt/authors-and-referees/gta`
returns **HTTP 200** — the same URL shape already known to work for the British Journal of Cancer,
and the one the journal's own home page links as "Guide For Authors". Three rounds of path-guessing
were spent on a page that a link harvest found immediately.

⛔ **AND IT FAILS THE $0 CONSTRAINT, VERBATIM:**

> "After final layout for publication, each page of an article will incur a fixed charge of
> **£145 / $238 per page**. This charge is fully inclusive of colour reproduction … **Page charges
> will NOT apply to authors who choose to pay an article processing charge to make their paper open
> access.**"

So the subscription route carries a **mandatory** per-page charge, and the only way out is the APC.
For a manuscript of this size that is roughly **$1,900–2,400**. This is the Nucleic Acid Therapeutics
trap a second time at **2.6× the price** — NAT was rejected at $90/page — and it is the reason
"hybrid, therefore no APC on the subscription route" was never a sufficient test. §1b's reasoning was
sound and its conclusion is withdrawn: what was read there was the *open-access* page, which settles
the APC question and is silent on page charges.

⚠ **Two format facts, recorded now so the next venue is chosen with them in hand.** There is **no
Short Communication type at CGT** — the types are Article, Review, Brief Communication (2 pages, one
display item, 10 references), Perspective and Correspondence. ⛔ **AND THE MANUSCRIPT NO LONGER FITS
THE ARTICLE TYPE EITHER: it is OVER the main-text cap and OVER the display-item cap, and inside only
the reference cap.** That type also requires an **unstructured abstract of at most 200 words** — the
format the abstract now has, at a length this section deliberately leaves uncut (see the two
paragraphs below).
⚠ *Superseded, retained: "The manuscript's shape fits **Article** comfortably on words, display items
and references." Retired 2026-08-15 by the regenerated measurement. The sentence was written when the
paper was a quarter of its present length; the pre-mRNA compartment, the censoring re-screen, the
added tables and Figure 2 landed after it, and it crossed two of the three caps while a sentence
saying otherwise sat here — a fit verdict typed once and never re-derived, which is the failure rule 1
exists to stop.*

**Neither side of that comparison is typed here, and neither should be.** The measured values have one
home, [`submission-metrics.json`](../submission-metrics.json), regenerated by
`python3 research/manuscripts/submission_metrics.py`; the CGT Article caps have one home,
`VENUES["CGT-Article"]["limits"]` in [`submission_metrics.py`](../submission_metrics.py), read at
primary source from the journal's own guide to authors at HTTP 200. ⛔ **The comparison itself is NOT
regenerated** — that artifact grades this manuscript against bioRxiv, which sets no limits, so
`over_limit` is empty by construction and says nothing about CGT. Read the two files side by side
rather than trusting the verdict above; it is a dated reading, not a measurement. ⚠ *Superseded,
retained: "4,244 words against 12,000; five display items against seven; 29 references against 60" —
every one of those three drifted, which is why no count is written into this file.*

⚠ **FORMAT AND LENGTH WERE HELD UNDER ONE RULE, AND THEY DO NOT DESERVE THE SAME RULE (trimcrae,
2026-08-14: *"This is an abstract. Not a mini paper."*).** *Superseded, retained: "Neither the
abstract format nor its length should be changed until a venue is settled, because both are
venue-specific and the current form is right for a journal that wants a structured abstract."*
That reasoning holds for **length** — cutting to a 200-word cap and re-expanding for a venue that
allows 250 is real work, which is the "cutting twice" this section exists to avoid. It does not
hold for **format**: restoring four bold headings for a venue that mandates them is a two-minute
edit in either direction, so holding the format buys nothing and costs every preprint reader in the
meantime. The abstract is now **unstructured**, which is the norm for a computational
sequence-design paper and what bioRxiv, the imminent destination, receives. The headings were also
load-bearing in the wrong way: a `Results.` label supplies context for free and so licenses a bare
run of numbers beneath it, which is how the abstract came to be unreadable at 199 words. Length
remains uncut and venue-specific, exactly as this section says.

✅ **What this cost and what it bought.** Nothing was submitted, so the cost is zero. What it bought
is the rule generalised: **ask every venue for its FULL fee schedule, not its APC policy** — page,
colour, submission and over-length charges included — and read it from the journal's own guide to
authors rather than from a publisher-wide policy page. Two venues have now been eliminated by
exactly this question, and both looked free until the guide was read.

**Plan of record is therefore: bioRxiv preprint (free, immediately); journal venue REOPENED.**
See §1c above, which is where the disqualification is recorded. ⚠ *Superseded, retained: "See §1d" —
there is no §1d in this file, and a dangling pointer in the sentence carrying the plan of record is
the one place it is least affordable.*

## 2 · What the venue demands, and where the submission stands

⚠ **This table was written against the WORKING RECORD, before the submission text existed as a
separate file.** Every row below now measures `fusion-junction-aso-research-article.md`; the
superseded column is kept because the size of the gap is the reason the split happened.

| requirement | state (2026-08-20) | was, before the split |
|---|---|---|
| main-text length | ⚪ **ungraded — bioRxiv sets no limit**, and no journal is chosen, so there is nothing to be inside of. The measured length is in [`submission-metrics.json`](../submission-metrics.json) and is not stated here. It is an **Article** length, not a Short Communication one, which is why the cover letter asks for the Article type; the filename is historical (⚠ *superseded, retained: "~6,000 words main text · ✅ inside it", which graded the paper against a target belonging to a venue §1c had already eliminated, and "≈4,200"*) | ≈21,000 — the dominant restructuring task |
| abstract | ✅ present, **unstructured**, one paragraph — the form bioRxiv receives and the norm for a computational design paper; four bold headings restore in minutes for a venue that mandates them (BJC does; §1c). Length measured in the same artifact and deliberately uncut (⚠ *superseded, retained: "structured abstract … ✅ present, four headed parts" and "274 words", the latter also contradicting "265" two rows up in this same file*) | present but long and narrative |
| IMRaD | ✅ Results ordered by finding, §3.1–§3.9 (⚠ *superseded, retained: "§3.1–§3.4"*) | ordered as a **chronology** (§3a, 3a-bis, … 3a-nonies) |
| numbered figures | ✅ generated from committed artifacts, with legends, and pinned to their source revisions by `aso_figure_provenance.py --check`. The count is measured in [`submission-metrics.json`](../submission-metrics.json) and is not stated here | **none exist** |
| numbered tables | ✅ generated; the count is measured in the same artifact and is not stated here. Table 4 lists the designs the cleanliness claim is about — added 2026-08-13, because that claim had no table and only four of its nine molecules appeared anywhere in the per-junction specificity table, now Table 3 (⚠ *superseded, retained: "Table 3 lists the designs" and "anywhere in Table 2" — the deposit was renumbered to first-citation order on 2026-08-17 and both tables moved; neither table's contents changed*) (⚠ *superseded, retained: "✅ three, generated" — tables were added after it and the row went on reading as a current count*) | **none exist** |
| numbered reference list with author/title/journal/year | ✅ `fusion-junction-aso-submission-references.md`, numbering DERIVED from per-citation PMIDs; every entry now carries author, title, journal and year, the last two gaps closed by harvesting retrieved records rather than typing them. The count is measured in the same artifact and is not stated here (⚠ *superseded, retained: "✅ 30 entries"; the count grew with the manuscript and this row did not*) | prose carries bare PMIDs; journal titles were deliberately not stored by the fetch path |
| journal register | ✅ `lint_style.py` clean | bold 33.2/1000, em-dash 17.5/1000, 286 mid-sentence bolds, 127 glyphs |
| data availability | ✅ **closed** — the archive is published on Zenodo under [doi:10.5281/zenodo.22028916](https://doi.org/10.5281/zenodo.22028916), open access, CC-BY-4.0: 473 files taken from this repository by `fusion-junction-aso-archive-manifest.json`, every one hash-verified against that manifest before upload. Both of the article's availability statements cite it. ⚠ *Superseded, retained: "⛔ open — artifacts are repo JSON on a feature branch; a citable archive is needed".* | same |
| author block, funding, competing interests | ✅ **written** — author block taken from the form already committed across the other manuscripts; self-funded, no funder role; no financial interests, with survivorship declared as a non-financial one | not yet reached |
| ORCID | ✅ **closed** — `0000-0002-1823-1451`, supplied by trimcrae 2026-08-20 and carried in the author block. ⚠ *Superseded, retained: "⛔ open — trimcrae only. No ORCID iD exists anywhere in the repository".* The iD is registered but the record does not yet list this author's 2019 PLOS ONE paper — Crossref shows no ORCID against that byline — which affects that record, not this deposit | not yet reached |
| figures in a submission format | ✅ **closed** — `figures/svg_to_submission_formats.py` renders vector PDF and 300 dpi PNG for all three, verified no image XObjects and live text. ⚠ *Superseded, retained: "⛔ open … No converter exists in the dev sandbox"* | — |
| venue confirmation | ⛔ **open.** ⚠ *Superseded, retained: "✅ decided — Cancer Gene Therapy (Springer Nature), $0 subscription route read at primary source" — §1c of this same file disqualifies CGT on its own read fee schedule, so this row contradicted the section above it.* NAT remains preferred if a human can load its page, since the block is bot detection |

## 3 · What must NOT be lost in the rewrite

The compression is where an honest paper turns into an over-claiming one, so these are fixed points:

- **The cleanliness claim is a floor over a subset, not a total, and the censoring guard that makes it
  one must survive.** Nine designs at six junctions carry no hybridisable near-match, over the 47 of
  183 designs whose hit lists are complete enough to assess. Drop the guard — count a design clean
  because its *retained* hits are all minus-strand — and the number becomes 24 at 18 junctions. That
  is the single most inviting overstatement available in this paper, and it must not be taken.
  ⚠ *Superseded, retained: "**0 of 5 designs are clean at every junction screened.** This is the
  headline result and it is a negative. It must not migrate into the discussion or soften into
  'promising'." That was true of a five-design screen at one modelled seam. Left standing here it did
  the opposite of its job: a fixed point instructing a future session to reinstate a negative the
  evidence had already overturned.*
- **The method-level novelty is nil.** Junction-directed oligonucleotides are a 35-year lineage that
  has reached clinical testing. The novelty claim is indication-level only.
- **Delivery is unsolved for a tumour.** The inhaled route has reached patients in *other*
  indications and against airway-accessible targets; that is not a claim about a sarcoma nodule.
- **The multi-partner result is conditional** on patients carrying breakpoints at the homologous
  exons, which nobody here has shown.
- **The retraction record must survive somewhere.** Repository rule 1.2 requires superseded values be
  registered. A journal does not want that in the running text; the SI or a data-repository record is
  the right home, and dropping it entirely is not an option.

### 1d · External review, 2026-08-15: the venue shortlist, and a parallel move worth more than the venue

An external reviewer of the submission draft named the realistic targets independently of the fee
question: ***Nucleic Acid Therapeutics*, *Molecular Therapy — Nucleic Acids*, or *PLOS ONE***, with
the judgement that **a sequence-only paper with no wet-lab arm will struggle above that**. Two of
the three are already on this page — NAT as the preferred fit whose fee model could not be read
(§1b), MTNA priced at $116 per page for a non-society member on the checklist. The reading that is
new is the ceiling: this page had been treating venue as a fee-constrained optimisation, and the
constraint that actually binds is the absence of an experiment.

⭐ **AND THE HIGHER-VALUE MOVE IS PARALLEL RATHER THAN SEQUENTIAL.** Post to bioRxiv now — that was
already the plan of record and it is unaffected by the journal question — and separately approach a
group holding molecularly confirmed EMC material with breakpoint sequencing. **Two oligonucleotides
and three controls is a small ask for a laboratory that already has the cells**, and §5 of the
manuscript is written as exactly that request: named sequences, named controls, and a
pre-registered decision threshold.

The obvious group is the **Milan sarcoma group at Istituto Nazionale Tumori**, and this repository
already holds the evidence for why: they are the source of the sunitinib series in
[`emc-fusion-partner-pooling.json`](../fusion-partner/emc-fusion-partner-pooling.json), which is
partner-stratified, so they have both the cohort and the molecular annotation §5.4 requires before
any oligonucleotide is ordered.

⚠ **TWO THINGS THIS SUBSECTION DOES NOT DO.** It does not settle the venue, because the fee reads
in §1b and §1c stand and NAT still needs a human with an ordinary browser. And it does not send
anything: outreach is outward-facing and irreversible, so it goes to trimcrae as a review block
when the preprint is actually ready to post, per CLAUDE.md §3, not before.

⭐ **One further reviewer judgement, recorded because it cuts against this repository's instinct:**
the author's declared connection to the disease is **an asset in that conversation, not something
to keep out of it**. The competing-interests declaration already states it. The outreach draft
should lead with it rather than bury it.

## 4 · Sequence

1. Restructure Results by finding; move the chronology and the correction record to SI.
2. Build the figures from committed artifacts.
3. Reconstruct the reference list in journal form.
4. Register rewrite, then add the manuscript to `lint_style.py` `TARGETS` so the gate holds it.
5. Archive the artifacts for a data-availability statement.
6. Post the preprint; submit.
