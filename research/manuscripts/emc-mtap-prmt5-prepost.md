---
id: DOC-EMC-MTAP-PRMT5-PREPOST
title: Pre-posting checklist — the EMC PRMT5/MTAP preprint
level: L3
kind: runbook
status: live
canonical_for: ["posting readiness of the EMC PRMT5/MTAP preprint"]
purpose: >
  Hold every item that must be cleared before this specific manuscript is posted, separated into what
  an agent can close and what only trimcrae can supply — so the blocking set is a short explicit list
  rather than a vague "needs review".
scope: >
  Pre-posting steps for one manuscript. It posts nothing and authorises nothing.
audience: [maintainers, external reviewers]
date: 2026-08-09
last_verified: 2026-08-09
related: [DOC-EMC-MTAP-PRMT5, DOC-NR4A3-DEGRADER-PREPRINT-PLAN]
---

# Pre-posting checklist — PRMT5/MTAP

> ⛔ **NOTHING HERE POSTS ANYTHING.** Posting is outward-facing and irreversible, so it is trimcrae's
> call under CLAUDE.md §3, and the standing instruction as of 2026-08-09 is that nothing is posted
> until the papers are developed enough to rank.

## Venue — determined, and it is NOT the degrader paper's venue

⭐ **bioRxiv, not ChemRxiv.** The existing checklist picks ChemRxiv because the degrader paper is a
cryptic-pocket and de-novo-design paper, i.e. med-chem/comp-chem. **This manuscript is biological** —
a target-class hypothesis raised from expression and dependency data, with no chemistry in it. The
same checklist already names the alternative: *"bioRxiv is the alternative if we lean the framing
biological (also free)."* That is this paper.

- **Cost: $0.** bioRxiv posting is free, which satisfies the standing hard constraint (trimcrae,
  2026-07-05: **no pay-to-publish, author pays $0**).
- ⚠ **Journal route is NOT determined and is deliberately left open.** The degrader paper's JCIM plan
  does not transfer — JCIM is a chemical-information journal and this paper has no chemistry. Picking
  a biological journal with a confirmed $0 subscription route is a separate decision and is not made
  here.

## What an agent can close, and its state

| item | state |
|---|---|
| Figures rendered from committed artifacts, provenance-hashed | ✅ four figures, `--check` verifiable |
| SI written — methods, full tables, controls, failure modes | ✅ `emc-mtap-prmt5-hypothesis-SI.md` |
| Abstract structured for a preprint server | ✅ with the qualifier in its own paragraph |
| Every prose identifier anchored to a retrieval | ✅ `mtap-prmt5-emc-citations.json`, 0 new unanchored |
| Language rules (no efficacy/safety/window/readiness) | ✅ `lint_claims` 0 ERROR |
| Falsifiers stated, with the likeliest failure named | ✅ F1–F8, F8 names the pan-essentiality route |
| Data availability — every series and panel identified | ✅ §2 and SI §S1 |

## ⛔ What only trimcrae can supply — the actual blocking set

1. ✅ **RESOLVED 2026-08-09 — the details were already in the repository and I did not look.**
   Author, affiliation and corresponding email are now in the manuscript: Tristan McRae, independent
   researcher, unaffiliated, trimcrae@gmail.com — read from
   `research/compute/access-allocation-request.md`, and the unaffiliated status is what
   `emc-post-degrader-options.md` and `emc-atr-vulnerability-assessment.md` already state in prose.
   ⚠ **ORCID is the one piece genuinely absent from the repository.** It is optional on bioRxiv but
   worth having; only trimcrae can create or supply one.
2. **The decision to post at all**, and whether this paper goes first among the portfolio.
3. **Licence choice** (bioRxiv offers CC-BY among others). The degrader plan chose CC-BY for ChemRxiv;
   it is not automatic here.
4. **Whether to contact the holders of the two published EMC models before or after posting.** §4 of
   the manuscript names an addition to a screen those holders already run — that is an outreach act,
   and outreach is outward-facing.

## ⚠ Honest statements that must survive to the posted version

These are in the manuscript and must not be softened during any formatting pass:

- **No EMC cell line carrying the fusion appears in any public dependency dataset.** Every dependency
  figure is a transfer from other sarcomas.
- **PRMT5 and MAT2A are dependencies in 94.5% and 96.7% of 176 sarcoma lines.** The proliferation half
  of the transferred result is therefore close to expected.
- ⛔ **ROUTE 2 IS CLOSED BY THIS PAPER'S OWN DATA, and the closure must not be softened back into a
  caveat during any formatting pass.** *MTAP* is flat where the read is powered (−0.02 SD); the entire
  locus signal is *CDKN2A* (−0.40 SD), which reverses on the second platform (+0.17). The window
  selects on *MTAP* loss, so the locus reading does not support it.
- ⚠ **The methylosome GROUP does not separate this disease** — pooled, EMC ranks second of four
  comparator classes. *PRMT5* alone does. Route 1's claim is stated on the gene, not the group, and
  must stay that way.
- **16 tumours, two decade-old array platforms, uncorrected for multiple testing.**
- **Route 1's source is a preprint that states it is not certified by peer review.**

## Re-check before any posting pass

```bash
python3 research/modalities/emc_mtap_prmt5_figures.py --check   # figures match the artifacts
python3 research/manuscripts/lint_claims.py                     # language rules (CI-only gate)
python3 research/manuscripts/lint_citations.py                  # every identifier traces to a fetch
./scripts/preflight.sh                                          # all 7 gates
```
