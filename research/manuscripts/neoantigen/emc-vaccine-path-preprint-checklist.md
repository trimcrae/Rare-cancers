---
id: DOC-EMC-VACCINE-PATH-PREPRINT-CHECKLIST
title: "bioRxiv preprint checklist — the EMC fusion-junction vaccine paper"
level: L3
kind: memo
status: live
canonical_for:
  - what must be done to post PUB-VACCINE-PATH as a bioRxiv preprint
purpose: >
  The deposit steps for this preprint, split into what is done, what still blocks posting, and what is
  deliberately deferred. It exists so the deposit is a short session at a browser rather than a
  re-derivation of decisions already made.
scope: >
  Preprint mechanics only. It makes no scientific claim and states no result; every figure it refers
  to has its home in the manuscript.
audience: [maintainers, collaborators]
related: [DOC-EMC-VACCINE-DEVELOPMENT-PATH, DOC-EMC-VACCINE-PATH-REDTEAM-ROUND1]
date: 2026-08-22
last_verified: 2026-08-22
---

# bioRxiv preprint checklist — PUB-VACCINE-PATH

**Article type: full research article**, subject area Cancer Biology. The venue reasoning is the same
as the ASO submission's and is not re-derived here: bioRxiv is free, sets no word, abstract or
display-item limit, is indexed by Europe PMC, and posting forecloses no journal
([the ASO checklist](../aso/fusion-junction-aso-preprint-checklist.md) carries the venue evidence).

⛔ **THIS PAPER IS NOT READY TO POST.** Section 2 is not a list of nice-to-haves; each row is a
blocker that a reader could check and find wrong.

## 1 · Done, and needs nothing further

| item | state |
|---|---|
| Manuscript | [`emc-vaccine-development-path.md`](./emc-vaccine-development-path.md), hardened through round 1 of an adversarial cycle. Word counts are measured, not asserted; the round-1 ledger carries them |
| Author block | Real name, unaffiliated statement, correspondence address and ORCID `0000-0002-1823-1451`. Held by `test_vaccine_path_numbers.py`, which fails on any `[Name]`-style placeholder |
| Declarations | AI use, data and code availability, competing interests including the survivorship non-financial interest, funding, ethics, and a not-clinical-guidance statement |
| Numbers | Every headline figure bound to the artifact that produces it by [`test_vaccine_path_numbers.py`](../tests/test_vaccine_path_numbers.py), at every site that states it. Mutation-tested 37/37 |
| Superseded register | Appendix A (the coordinate-system correction) and Appendix B (what round 1 withdrew), both enforced by `lint_consistency.py` through `pinned-figures.json` |
| References | Fourteen entries, every identifier transcribed from a fetch record in this repository, every one cited in text, and ten of them additionally resolved at Crossref by a CI run |
| Build | An entry in `build_submission_pdf.py`, so the PDF guard family can reach it |
| Style | Passes the journal-register gate; it was written to that gate rather than retrofitted |
| Gates | `PREFLIGHT_FULL=1 ./scripts/preflight.sh` returns **PREFLIGHT OK, exit 0** (2026-08-22), which is the tier CLAUDE.md requires before any outward-facing step. The gate is clear; §2 below is what is not |

## 2 · Blocks posting — must be closed first

1. **⛔ Reference 12 has no bibliographic record.** The class II arm of Section B4 was screened with
   MHCnuggets, and no citation for that tool exists anywhere in this repository. A Crossref
   bibliographic query returned a *near-miss* — a pan-specific class I binding paper — which was not
   used, because a wrong citation in quotable form is worse than a missing one. **Resolve it by
   targeted search, or withdraw the class II arm.** Nothing else in Section 2 is cheaper than this.
2. **⛔ The class II artifact records no tool version and no models release**, where the class I
   artifact records both. The paper states this as a reproducibility gap. Re-emitting
   `patient-cd4-demo.json` with a `_predictor` block would close it and costs one CI run.
3. **⛔ Reference 9 is a company announcement with no identifier of any kind** and no record in this
   repository. It is labelled as an announcement and cited only for the fact that the announcement was
   made, which is the most that can honestly be done — but a reader cannot follow it. Either capture a
   URL and access date, or cut the framing sentence in §1 that rests on it.
4. **⛔ A decision only the author can make: the manuscript no longer says specialist review is
   required before circulation.** The version reviewed in round 1 said "Review by a sarcoma medical
   oncologist and a tumour immunologist is recommended before circulation", and posting a preprint is
   circulation. That sentence is now a disclosure — the paper states plainly that no such reader has
   seen it — which is the standard preprint framing and does not block posting. **Whether to seek that
   review anyway, before posting, is the author's call and is not a call this repository can make.**

## 3 · Only the author can do these

1. **Post at `biorxiv.org/submit-a-manuscript`.** Article type New Results, subject area Cancer
   Biology, licence CC-BY, corresponding author ORCID-linked, and the survivorship non-financial
   interest entered verbatim from Declarations.
2. **Decide whether this paper gets its own archival deposit** or is covered by the existing Zenodo
   archive. The ASO deposit's DOI is minted and its manifest hashes the repository's artifacts; this
   manuscript's artifacts are in the same tree.

## 4 · Deliberately not done, and why

- **No figure.** Every quantity is in the prose, and the one display item a reader would want — the
  coverage-versus-threshold curve — would restate Section 2.3's ladder without adding to it. If a
  figure is added later it must be cited in first-citation order and rendered as vector.
- **The abstract has not been cut to a journal's cap.** bioRxiv sets none, and cutting to the wrong
  target means cutting twice.
- **The dated capability bands were removed rather than updated.** See Appendix B of the manuscript
  and §5 of the round-1 ledger.
- **No supplementary information.** Nothing in the paper is a derivation long enough to move out of
  it, now that the forecast table is gone.
