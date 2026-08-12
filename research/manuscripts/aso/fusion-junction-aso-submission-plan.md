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

**Plan of record: bioRxiv preprint (free) + Nucleic Acid Therapeutics, subscription route.**
bioRxiv rather than ChemRxiv because the framing is biological rather than chemical — the degrader
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

**Plan of record: bioRxiv preprint (free, immediately) → Cancer Gene Therapy, subscription route.**
The preprint is unaffected by the venue question and should not wait on it.

## 2 · What the venue demands, and where the submission stands

⚠ **This table was written against the WORKING RECORD, before the submission text existed as a
separate file.** Every row below now measures `fusion-junction-aso-short-communication.md`; the
superseded column is kept because the size of the gap is the reason the split happened.

| requirement | state (2026-08-12) | was, before the split |
|---|---|---|
| ~6,000 words main text | ✅ ≈4,200 | ≈21,000 — the dominant restructuring task |
| structured abstract | ✅ present, 274 words, four headed parts | present but long and narrative |
| IMRaD | ✅ Results ordered by finding, §3.1–§3.4 | ordered as a **chronology** (§3a, 3a-bis, … 3a-nonies) |
| numbered figures | ✅ three, generated from committed artifacts, with legends | **none exist** |
| numbered reference list with author/title/journal/year | ✅ 28 entries, `fusion-junction-aso-submission-references.md`, numbering DERIVED from per-citation PMIDs | prose carries bare PMIDs; journal titles were deliberately not stored by the fetch path |
| journal register | ✅ `lint_style.py` clean: 0 glyphs, bold ≈5/1000 against a limit of 12, em-dash ≈5/1000 against 6 | bold 33.2/1000, em-dash 17.5/1000, 286 mid-sentence bolds, 127 glyphs |
| data availability | ⛔ **open** — artifacts are repo JSON on a feature branch; a citable archive is needed | same |
| author block, funding, competing interests | ✅ **written** — author block taken from the form already committed across the other manuscripts; self-funded, no funder role; no financial interests, with survivorship declared as a non-financial one | not yet reached |
| ORCID | ⛔ **open — trimcrae only.** No ORCID iD exists anywhere in the repository; free to register and required by some publishers at submission | not yet reached |
| figures in a submission format | ⛔ **open** — the three figures are dependency-free SVG, which is vector and loses nothing, but NAT will want EPS/TIFF/PDF. No converter exists in the dev sandbox; this is a CI step, not a redraw |
| venue confirmation | ✅ **decided — Cancer Gene Therapy (Springer Nature), $0 subscription route read at primary source.** See §1b; NAT remains preferred if a human can load its page, since the block is bot detection |

## 3 · What must NOT be lost in the rewrite

The compression is where an honest paper turns into an over-claiming one, so these are fixed points:

- **0 of 5 designs are clean at every junction screened.** This is the headline result and it is a
  negative. It must not migrate into the discussion or soften into "promising".
- **The method-level novelty is nil.** Junction-directed oligonucleotides are a 35-year lineage that
  has reached clinical testing. The novelty claim is indication-level only.
- **Delivery is unsolved for a tumour.** The inhaled route has reached patients in *other*
  indications and against airway-accessible targets; that is not a claim about a sarcoma nodule.
- **The multi-partner result is conditional** on patients carrying breakpoints at the homologous
  exons, which nobody here has shown.
- **The retraction record must survive somewhere.** Repository rule 1.2 requires superseded values be
  registered. A journal does not want that in the running text; the SI or a data-repository record is
  the right home, and dropping it entirely is not an option.

## 4 · Sequence

1. Restructure Results by finding; move the chronology and the correction record to SI.
2. Build the figures from committed artifacts.
3. Reconstruct the reference list in journal form.
4. Register rewrite, then add the manuscript to `lint_style.py` `TARGETS` so the gate holds it.
5. Archive the artifacts for a data-availability statement.
6. Post the preprint; submit.
