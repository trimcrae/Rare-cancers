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
| **Nucleic Acid Therapeutics** (~~Mary Ann Liebert~~ → **SAGE**, see below) | the field's dedicated oligonucleotide-therapeutics journal; publishes design, mechanism and computational work | ✅ **READ 2026-08-23** — mandatory Publishing Services Fee per typeset page, assessed on acceptance; colour charged separately in print. Rates: [`nat-submission-guidelines-2026-08-23.md`](../../literature/nat-submission-guidelines-2026-08-23.md) | ⭐ **TARGET, Original Paper. Not $0 — see §1a′** |
| Molecular Therapy — Nucleic Acids | excellent fit, higher profile | fully gold OA, APC mandatory | ❌ out on fee |
| Cancers / IJMS (MDPI) | would accept a computation-only paper | APC mandatory | ❌ out on fee |
| PLOS ONE · Scientific Reports · Frontiers | would accept | APC mandatory | ❌ out on fee |
| JCIM (ACS) | the degrader paper's venue; $0 subscription route confirmed | free route | ❌ out on **scope** — a small-molecule/computational-chemistry journal; this is an RNA paper |
| Briefings in Bioinformatics | methods-general | hybrid | ⚠ fallback, but the emphasis is wrong: this is a therapeutic-design paper, not a method paper |

**Plan of record: a preprint of the CONDENSED article (server open) + Nucleic Acid Therapeutics,
Original Paper.**

⚠ *Superseded, retained: "**Plan of record: bioRxiv preprint (free) + Nucleic Acid Therapeutics,
subscription route.** bioRxiv rather than ChemRxiv because the framing is biological rather than
chemical — the degrader paper's ChemRxiv choice does not transfer."* The reasoning about framing
still holds and is not what changed. **bioRxiv DECLINED the submission on 2026-08-23 because the
author is unaffiliated** — the extended report went there on 2026-08-20 and was refused on that
ground alone. The server question is reopened for the condensed article and the shortlist, with what
is and is not established about each, is in the preprint checklist §2b. The ORDER is no longer a
question: NAT's own guidelines say "Accepts preprints? Yes", so posting first cannot disqualify the
submission.

## 1a‴ · THE AUTHOR'S CAP IS $600 TOTAL, AND ONLY TWO VENUES CLEAR IT (trimcrae, 2026-08-24)

⛔ **THIS IS A HARD CEILING ON WHAT PUBLISHING THIS PAPER MAY COST, AND IT RE-PRICES EVERY ROW
ABOVE.** Against it:

| venue | what it would cost | clears $600? |
|---|---|---|
| **Nucleic Acid Therapeutics** | page charges at the read rate, for a manuscript held to the six-page budget, with **no colour requested in print** | ✅ **yes, with one page of headroom and no more** |
| British Journal of Cancer | nothing | ✅ yes — but a desk-rejection risk this paper has already reasoned about |
| Cancer Gene Therapy | page charges at its read rate, which is the higher one | ❌ no |
| NAR Cancer · Molecular Therapy — Nucleic Acids | a mandatory APC in either case | ❌ no, by a wide margin |

★★ **TWO THINGS NOW COST REAL MONEY THAT DID NOT BEFORE, AND BOTH ARE SILENT UNTIL ACCEPTANCE.**

1. **A SEVENTH TYPESET PAGE BREAKS THE CAP.** The six-page budget was a fee-minimisation
   preference; it is now the difference between clearing $600 and not.
   [`test_the_journal_pdf_fits_its_page_budget.py`](../tests/test_the_journal_pdf_fits_its_page_budget.py)
   is what enforces it, and its instruction — pay for an overflow by cutting elsewhere, never by
   raising the budget — is now backed by the author's ceiling rather than by taste alone.
   ⚠ **AND THE PAGE COUNT IS A MODEL, NOT THE JOURNAL'S TYPESETTER.** Our count is taken at NAT's
   own measured geometry ([`venue-typeset-geometry.json`](../../literature/venue-typeset-geometry.json),
   read off its published PDFs), which is the best instrument available here and is still not their
   compositor. **One page of disagreement is the whole headroom**, so the honest statement is that
   this clears the cap on our measurement, not that it is guaranteed to.
2. **⛔ DO NOT REQUEST COLOUR REPRODUCTION IN PRINT.** The guidelines capture is explicit that
   figures supplied in colour appear in colour **online regardless**, and that a print colour
   charge applies only where the author **requests** print colour — at a first-image rate that
   alone would exceed this cap several times over. The election is stated in the cover letter so
   it is not left to a proof-stage default.
   ⭐ **AND THE FIGURE WAS MADE TO SURVIVE THAT, 2026-08-24.** Its panel already did: the breakpoint
   is a rule, donor and acceptor sit either side of it, the divergent base is boxed, and each row's
   reporting status is spelled out in words. **Its own caption did not** — it read "Blue, donor
   exon; green, NR4A3 acceptor exon", naming two channels a greyscale print reader cannot see, and
   measured in greyscale those two fills separate at about 1.1:1. The caption now leads with the
   channel that survives print and names colour as the online cue.

⛔ **Do not multiply any rate by any page count in this repository.** The rates have one home
(the guidelines capture), the page count has another (the budget test), and this section states the
verdict rather than the product.

## 1a⁗ · GENES, CHROMOSOMES AND CANCER WAS PUT TO THE JOURNALS' OWN RECORDS, AND THE TWO AXES DISAGREE (2026-08-25)

trimcrae asked whether GCC fits this paper better than NAT, and whether it is free. **Cost and fit
point at different venues, and that is the finding rather than a failure to decide.**

**Fee: GCC is the $0 route, and this is now read twice at primary source.** Wiley's author pages
were retrieved from CI on 2026-08-10 — hybrid, the charge attaching only to an open-access option the
corresponding author selects AFTER acceptance, a subscription article needing only a copyright or
licence agreement ([`venue-fee-routes-2026-08-10.json`](../../literature/venue-fee-routes-2026-08-10.json),
verdict `GCC.zero_dollar_route: VERIFIED`). On 2026-08-25 trimcrae read the journal's own Article
Publication Charges section in a browser and it says the same thing: an APC applies *"if the Open
Access option is selected"*, and it names no other author charge. **Rates have one home and are not
restated here.**

⚠ **ONE THING IS STILL OPEN AND IT IS THE ONLY THING THAT COULD MOVE THIS ROW.** Wiley states that
page and colour charges are administered by individual journals and are NOT covered by open-access
agreements. The capture above is GCC's fee section and contains no page or colour charge, but that
is absence in an excerpt rather than a search of the page. **Closing it is a human browser read — the
per-journal author-guideline pages 403 to the egress proxy AND to an Actions runner alike**
(recorded 2026-08-10), so no session can take this observation. Until it is taken, GCC is $0 on a
fee section that named nothing else, not $0 on a page searched for the words.

**Fit: both journals were censused with the same instrument**, `nat_scope_census.py`, generalised to
any journal on 2026-08-25 rather than duplicated. Artifacts:
[`nat-scope-census.json`](nat-scope-census.json) and [`gcc-scope-census.json`](gcc-scope-census.json).
⛔ **Both are keyword SCREENS over titles and abstracts, wrong in both directions on individual
records, which is why every count ships with its candidates listed.**

| what the record says | NAT | GCC |
|---|---|---|
| articles PubMed indexes | 614 | 4,060 |
| computation-only candidates, of screened abstracts | 31 of 574 | 218 of 3,915 |
| EMC papers | — | **12**, 1997–2025, including the TAF15::NR4A3 and novel-partner reports this manuscript cites |
| therapeutic-oligonucleotide design papers | the industry off-target framework this paper executes, and a molecular-modelling paper on ASO analogs | **0 — see below** |

★★ **THE DECIDING OBSERVATION IS NOT THE DRY/WET AXIS, WHICH IS A TIE.** Both journals publish
computation-only work at a comparable rate — the two fractions above sit within a few tenths of a
percentage point of each other, and the product is deliberately not typed here — so the objection this paper was braced for at NAT — *an
oligonucleotide journal will want a knockdown* — is not answered by moving to GCC, and GCC does not
gain the paper anything on that axis. What separates them is the MODALITY: GCC's 107 abstracts
matching an oligonucleotide pattern are siRNA-as-a-laboratory-tool and microRNA biology, and the one
title carrying the word "antisense" uses it for a DNA strand, not a drug. **In 4,060 articles the
screen finds no therapeutic-oligonucleotide design paper.** Its therapeutically-flavoured
computational work is prognostic and predictive genomics — a biomarker, not a reagent to synthesise.

**So the trade is stated, and it is a decision rather than a calculation.** GCC has the disease, the
fusion, the readers who hold EMC material, no fee and no page budget — and no precedent for a paper
whose product is two sequences. NAT has the modality, the framework and one page of headroom under
the author's cap on OUR page model rather than their compositor's §1a‴. **A GCC submission would
require the junction census to LEAD and the gapmers to become its application, which changes what
the paper is** — CLAUDE.md §3: reshaping a named paper is not a formatting choice and is not a
session's call.

★★ **AND THE OBJECTION AT GCC IS NOT "NOT NOVEL ENOUGH" — SAYING IT THAT WAY MAKES IT SOUND LIKE
TWO CONTRADICTORY COMPLAINTS** (trimcrae, 2026-08-25: *"It seems like you're saying GCC is a bad fit
because it's not novel enough and too novel"*). It is one complaint about OVERLAP, and it needs
stating in the form a future session can act on.

- **The paper carries no new observation of a tumour.** No new fusion partner, no new breakpoint, no
  new sequencing, no patient. Every disease fact in it is compiled from published reports — which is
  the half a cancer-genetics readership evaluates, and in that half this is a compilation.
- **The paper's new results are real and are not that.** §3 is new: of 190 junction-spanning designs
  87 let a mature wild-type parent pair the entire catalytic gap and 61 do so against wild-type
  *NR4A3*; lengthening the gap cannot buy margin, for an arithmetic reason; and chimeras built at
  real exon termini meet the same screen at 40.6% against the panel's 45.8%, so most of the liability
  is not a property of real fusion junctions. Those are findings about the sequence architecture of
  these transcripts — but their payload is legible only to somebody designing an oligonucleotide,
  and that is the reader the census finds no precedent for.

**So the novelty and the scope do not overlap: the new part is not the part GCC reads, and the part
GCC reads is not new.** ⚠ At NAT the same paper has the mirror shape — the new part IS what that
readership reads, and what is missing is the wet-lab margin measurement §5 specifies. Neither is a
verdict; the two are different bets, and which one is worth taking is a decision, not a count.

⛔ **AND ONE HALF OF THIS IS MEASURED WHILE THE OTHER IS NOT.** The censuses measured 12 EMC papers,
218 computation-only candidates and no therapeutic-oligonucleotide design paper. *How a reviewer
would phrase an objection* is inference from that record, not a reading of it, and must not be quoted
back as though the census said it.

⚠ **PLAN OF RECORD IS UNCHANGED BY THIS SECTION.** It records what the two records say. The venue
is trimcrae's to set.

## 1a⁵ · THE SHAPE PUBLISHES. IT IS THE FUSION HALF THAT HAS NO PRECEDENT (2026-08-25)

trimcrae, 2026-08-25: *"Is there any journal anywhere in the world that has published a design only
ASO paper?"* That is not a venue question — it asks whether this manuscript's SHAPE exists in the
literature at all, and a null answer would have outranked every venue comparison above, because no
choice between NAT and GCC would address it. **The answer is not null.** Artifact:
[`aso-design-only-census.json`](aso-design-only-census.json), the same wet/dry screen as the two
venue censuses with the journal scoping removed.

**⛔ THE "NO WET LAB" OBJECTION IS WEAKER THAN THIS FILE HAS BEEN TREATING IT.** Of 15,916 indexed
antisense papers, 539 report no wet-lab experiment, across 328 journals; excluding reviews, **323
original papers across 183 journals**. A computation-only oligonucleotide paper is ordinary. The
closest single analogue found is a 2024 *Virus Genes* paper designing an antisense oligonucleotide
against hepatitis C entirely in silico — this paper's shape, published, with no experiment.

**★★ AND THE FUSION COLUMN IS THE FINDING.** In the same 15,916 papers, **20** abstracts mention a
fusion transcript, junction, oncogene, chimeric transcript or breakpoint AT ALL. Read: almost
entirely BCR-ABL and BCL-2 work from 1991–2001 performed in cells and mice, plus three modern
entries (a DNAJB1-PRKACA siRNA, and NAB2-STAT6). **None is a design-only fusion-junction paper.**
The manuscript's prior-art claim therefore survives an instrument built to refute it, and the rare
thing about this work is the COMBINATION — design-only *and* junction-directed — not either half.

**Where this shape lands, which is largely not where this file has been looking:**

| journal | computation-only papers (reviews excluded) |
|---|---|
| Nucleic Acids Research | 22 |
| Molecular Therapy — Nucleic Acids | 16 |
| bioRxiv | 10 |
| **Nucleic Acid Therapeutics** | 7 (11 counting reviews) |
| Int J Mol Sci · Mol Ther · RNA · Sci Rep | 6 each |
| **Genes, Chromosomes and Cancer** | **0 — absent from the tally entirely** |

⭐ **GCC's absence is now measured from two independent directions** and they agree: §1a⁗ found no
therapeutic-oligonucleotide design paper in GCC's own 4,060 articles, and this census finds no GCC
row among 328 journals that have published computation-only antisense work.

⛔ **THIS DOES NOT SELECT A VENUE, AND TWO OF THE TOP ROWS ARE ALREADY REFUSED ON FEE.** NAR is
fully open access and Molecular Therapy — Nucleic Acids was priced out at §1a″; bioRxiv declined
this author as unaffiliated (§1). **A fee screen of the journals that actually publish this shape
has NOT been run** and is the obvious next observation, but it is a new venue search rather than a
correction to this one, and the venue is trimcrae's to set.

⚠ **SCREEN LIMITS, UNCHANGED FROM THE OTHER TWO CENSUSES.** A keyword classifier cannot read a
paper; none of the records above has been read beyond title and abstract, and the counts are wrong
in both directions on individual records. Separately, **30 of the 15,916 records (0.2%) were not
retrieved**, because the corpus exceeds PubMed's 9,999-record retrieval ceiling and must be
bisected on publication date, which drops a record carrying no usable date. The artifact reports
`n_retrieved` beside `n_indexed` so that gap is visible rather than smoothed over.

## 1a″ · The reviewer's two alternatives were priced, and both are worse (2026-08-24)

External review proposed *Molecular Therapy — Nucleic Acids* or *NAR Cancer* as better first targets
given the absence of wet-lab data. Both were priced. **Neither is cheaper than the current venue,
and both break the $0 constraint harder than it is already broken.**

⚠ **THE PROVENANCE COLUMN IS THE POINT — two of these rows are READ and two are not.** Elsevier and
Oxford University Press both returned **403 to the runner**, which is the same datacenter-IP refusal
this repository has recorded before, so their figures remain search-derived and must not be cited as
retrieved facts.

| venue | author-facing cost | route | provenance |
|---|---|---|---|
| **Nucleic Acid Therapeutics** (SAGE) | **$90 per typeset page** | subscription; APC-free | ✅ **READ** at primary source 2026-08-23 by trimcrae in a browser → [`nat-submission-guidelines-2026-08-23.md`](../../literature/nat-submission-guidelines-2026-08-23.md) |
| **Cancer Gene Therapy** (Springer Nature) | **$238 per page** (£145), colour inclusive; or APC £3490 | subscription charges per page, OA waives it | ✅ **READ** 2026-08-24, HTTP 200, headless browser → [`venue-fee-pages-2026-08-24.json`](../../literature/venue-fee-pages-2026-08-24.json) |
| Molecular Therapy — Nucleic Acids (Elsevier) | ~$3,900 APC | gold OA, mandatory | ⚠ **SEARCH-DERIVED** — the guide-for-authors page returned **403** to the runner |
| NAR Cancer (OUP) | ~$2,391 APC | gold OA, mandatory | ⚠ **SEARCH-DERIVED** — both author-guideline and charges pages returned **403** |
| British Journal of Cancer | $0 | subscription | ✅ READ previously; desk-rejection risk for a wet-lab-free ultra-rare sarcoma design study |

⭐ **THIS ALSO CLOSES A RISK THIS REPOSITORY HAD FLAGGED AND LEFT OPEN.**
[`submission-metrics.json`](../submission-metrics.json) carried
`⛔_the_CGT_fee_schedule_is_unread_and_that_is_a_live_submission_risk`, because the $0 reading of
Cancer Gene Therapy rested on its open-access page alone and every author-guideline path tried had
returned 404. The Guide to Authors has now been read, and the answer is that **CGT is not a $0 route
either** — it charges per page on the subscription option, at a higher rate than the current venue.
That note is corrected in place rather than deleted.

⚠ **THE CAPTURE HAS ITS OWN FILENAME BECAUSE A SHARED ONE WAS OVERWRITTEN WITHIN HOURS.** These
readings first landed in `research/literature/browser-fetch.json`, which is the generic output of
the browser-fetch workflow mode — so the next dispatch of that mode, fetching something unrelated,
replaced them with its own results and left this table citing a file that no longer contained what
the citation said. A dated, purpose-named capture cannot be clobbered by the next caller.

⛔ **Do not multiply any rate above by a page count anywhere in this repository.** The rate has one
home and the page count has another
([`test_the_journal_pdf_fits_its_page_budget.py`](../tests/test_the_journal_pdf_fits_its_page_budget.py)),
and a product typed into prose drifts against both.

**What this does not settle.** Cost is not the only axis, and the reviewer's underlying point — that
an oligonucleotide-therapeutics journal is a hard room for a paper with no wet-lab data — is not
answered by pricing.

⛔ **AND IT IS NOT TO BE PUT TO THE EDITOR (trimcrae, 2026-08-24: "Don't ask the editor anything").**
⚠ *Superseded, retained: "It is answered, if at all, by the article type: whether NAT's **Methods**
type fits … That question is for the editor and is trimcrae's to ask."* A pre-submission enquiry is
an outward-facing act, it is not authorised, and no session should open one. The submission stands
or falls on the manuscript as built; the article type stays **Original Paper**, which is what the
builder declares and what the page budget is graded against.

## 1a′ · The $0 rule does not survive this venue, and that is a decision already taken

⛔ **NAT'S FEE IS REAL, MANDATORY AND NOW READ.** The Publishing Services Fee is charged per typeset
page and assessed on acceptance; the rate is in the guidelines capture and is not restated here. It
is not avoidable by choosing the subscription route — it IS the subscription route. So the standing
"AUTHOR PAYS $0" constraint at the head of §1 is not satisfied by this venue and cannot be made to
be.

★ **THAT IS WHY THE PAPER WAS CONDENSED, AND THE PAGE COUNT IS THEREFORE A BUDGET RATHER THAN AN
AESTHETIC.** trimcrae reopened NAT on 2026-08-20 on exactly this basis: a full-length manuscript
priced the venue out, and a short article does not. The page budget is measured by
`tests/test_the_journal_pdf_fits_its_page_budget.py`, which owns both the budget and the built
count; a change that adds a page adds a page's fee, which is why that gate is a hard one and not
advice. ⛔ **Do not multiply the rate by the page count anywhere in this repository** — the rate has
one home and the count has another, and a product typed into prose drifts against both.

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

⭐ **AND THE HIGHER-VALUE MOVE IS PARALLEL RATHER THAN SEQUENTIAL.** Post the preprint now — the
posting was already the plan of record and is unaffected by the journal question — and separately
approach a group holding molecularly confirmed EMC material with breakpoint sequencing.
⚠ *Superseded, retained: "Post to bioRxiv now".* The server, not the sequencing, is what changed:
bioRxiv declined this author on 2026-08-23. **Two oligonucleotides
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
