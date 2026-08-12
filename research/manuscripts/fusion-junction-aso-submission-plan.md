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
| **Nucleic Acid Therapeutics** (Mary Ann Liebert) | the field's dedicated oligonucleotide-therapeutics journal; publishes design, mechanism and computational work | **hybrid — subscription route free**, OA optional | ✅ **TARGET** |
| Molecular Therapy — Nucleic Acids | excellent fit, higher profile | fully gold OA, APC mandatory | ❌ out on fee |
| Cancers / IJMS (MDPI) | would accept a computation-only paper | APC mandatory | ❌ out on fee |
| PLOS ONE · Scientific Reports · Frontiers | would accept | APC mandatory | ❌ out on fee |
| JCIM (ACS) | the degrader paper's venue; $0 subscription route confirmed | free route | ❌ out on **scope** — a small-molecule/computational-chemistry journal; this is an RNA paper |
| Briefings in Bioinformatics | methods-general | hybrid | ⚠ fallback, but the emphasis is wrong: this is a therapeutic-design paper, not a method paper |

**Plan of record: bioRxiv preprint (free) + Nucleic Acid Therapeutics, subscription route.**
bioRxiv rather than ChemRxiv because the framing is biological rather than chemical — the degrader
paper's ChemRxiv choice does not transfer.

⚠ **Two things to verify live at submission rather than trust from here:** that NAT's author
instructions still describe a free subscription route, and its preprint policy. Both are stated in
this repository as a plan, not as a retrieved fact — no fee page has been fetched for NAT, and the
degrader plan's discipline (*"FEE/POLICY CONFIRMED IN WRITING"*) has **not** been met for this venue.
Treat the row above as a decision to be confirmed, not a confirmation.

## 2 · What the venue demands that the current draft does not meet

| requirement | current state |
|---|---|
| ~6,000 words main text | **≈21,000** — the dominant restructuring task |
| structured abstract | present but long and narrative |
| IMRaD | Results are ordered as a **chronology** (§3a, 3a-bis, … 3a-nonies), not by finding |
| numbered figures | **none exist** |
| numbered reference list with author/title/journal/year | prose carries bare PMIDs; journal titles were deliberately not stored by the fetch path |
| journal register | measured against `lint_style.py`: bold 33.2/1000 against a limit of 12, em-dash 17.5/1000 against 6, 286 mid-sentence bolds, 127 glyphs |
| data availability | artifacts are repo JSON on a feature branch; a citable archive is needed |

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
