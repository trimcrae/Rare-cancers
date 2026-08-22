---
id: DOC-EMC-VACCINE-PATH-PREPRINT-CHECKLIST
title: "aiXiv preprint checklist — the EMC fusion-junction vaccine paper"
level: L3
kind: memo
status: live
canonical_for:
  - what must be done to post PUB-VACCINE-PATH as an aiXiv preprint
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

# aiXiv preprint checklist — PUB-VACCINE-PATH

**Article type: full research article** (`doc_type: paper`), category
`["Natural Sciences", "Biology", "Immunology"]`. ⚠ *Superseded, retained: "subject area Cancer
Biology."* aiXiv's taxonomy (`/api/categories`) has no such node, and it requires **exactly three**
levels — `[main_category, subcategory, specialization]`, a contract that appears nowhere in
`openapi.json` and surfaced only as an HTTP 400 on a live submit.

⚠ **Superseded, retained — this section named bioRxiv, and bioRxiv had already refused this author.**
It read: *"The venue reasoning is the same as the ASO submission's and is not re-derived here: bioRxiv
is free, sets no word, abstract or display-item limit, is indexed by Europe PMC, and posting forecloses
no journal."* Every clause of that is still true **of bioRxiv**, and irrelevant: on 2026-08-21 bioRxiv
declined this project's submission because *"bioRxiv requires authors to have an organizational
affiliation"*, and the ASO paper was re-aimed at Research Square in consequence. **A venue paragraph
that reasons from a venue's merits without checking its eligibility rule is the exact failure the
preprint-host memo was written to stop, reproduced in the next paper along.**

**The venue is aiXiv** (`aixiv.science`). It has no organizational-affiliation gate, takes submissions
over an authenticated agent API, and runs an adversarial reviewer this repository can invoke
([`scripts/aixiv_review.py`](../../../scripts/aixiv_review.py), workflow
[`aixiv-review.yml`](../../../.github/workflows/aixiv-review.yml); the API surface was read at primary
source into `literature/aixiv-api-surface-2026-08-22/`).

⛔ **AND THE COST OF THAT CHOICE IS DISCOVERY, WHICH IS TEST 4 AND IS NOT WAVED THROUGH.** aiXiv is
**absent from Europe PMC's indexed preprint-server list** (read 2026-08-21,
`research/literature/preprint-host-eligibility.json`) and a Crossref query for it as a container title
returns **0 results** (2026-08-22). A sarcoma immunologist's literature search will not surface this
paper from aiXiv alone. Posting here is therefore **not** a substitute for an indexed host, and a
second posting to an indexed server remains open and un-taken.

✅ **POSTED 2026-08-22 as `aixiv.260822.000005` — see §2b.**

⚠ *Superseded, retained: "⛔ **THIS PAPER IS NOT READY TO POST.** Section 2 is not a list of
nice-to-haves; each row is a blocker that a reader could check and find wrong."* That held while
§2.1 and §2.3 were open. Both are now closed; §2.2 is disclosed in the manuscript rather than
hidden, and §2.4 is a standing decision for the author, not a defect a reader could find.

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

1. ~~**Reference 12 has no bibliographic record.**~~ ✅ **CLOSED 2026-08-22.** The class II predictor is
   Shao et al., *High-throughput prediction of MHC class I and II neoantigens with MHCnuggets*,
   Cancer Immunology Research 2020, doi:10.1158/2326-6066.CIR-19-0464, PMID 31871119.
   ⚠ **The first attempt at this failed and failing safely is why it could be closed at all.** A
   single Crossref `query.bibliographic` had returned a pan-specific class I CNN paper whose title
   does not contain the tool's name; citing it would have put a wrong reference in the paper in
   quotable form. It was refused — and then, wrongly, the reference was written off as unobtainable
   on the strength of that one query. The repair was a by-NAME search across Europe PMC and Crossref
   that prints every candidate with its title and accepts only a title containing "MHCnuggets"
   (`verify-refs.yml` §9, run 32577476737). Europe PMC returned the journal record on the first try.
   The DOI is now in the CI-enforced `FIXED_DOIS` list, the record is in the repository's literature
   metadata, and both identifiers are in the citation-provenance ledger marked `verified`.
2. **⛔ The class II artifact records no tool version and no models release**, where the class I
   artifact records both. The paper states this as a reproducibility gap in Section 8 and reference 12
   rather than papering over it. Re-emitting `patient-cd4-demo.json` with a `_predictor` block would
   close it and costs one CI run. **This does not block posting** — the gap is disclosed, not hidden —
   but it is the cheapest remaining improvement to the paper's reproducibility.
3. ~~**Reference 9 is a company announcement with no identifier of any kind.**~~ ✅ **CLOSED
   2026-08-22.** The announcement is Merck/Moderna on INTerpath-001, **19 August 2026**. The reference
   now carries the merck.com URL and an access date, and all three primary sources (merck.com,
   news.modernatx.com, businesswire) are captured on `literature-cache` under
   `literature/interpath-001-announcement-2026-08-22/`. ⚠ **The capture was checked for BODY, not just
   for HTTP 200** — 10 and 12 occurrences of "INTerpath" in the Merck and Moderna records respectively,
   which is what distinguishes a retrieved release from a cookie wall. The honest caveats are unchanged
   and still in the reference: no DOI, no bibliographic index record, no effect size quoted.
4. **⛔ A decision only the author can make: the manuscript no longer says specialist review is
   required before circulation.** The version reviewed in round 1 said "Review by a sarcoma medical
   oncologist and a tumour immunologist is recommended before circulation", and posting a preprint is
   circulation. That sentence is now a disclosure — the paper states plainly that no such reader has
   seen it — which is the standard preprint framing and does not block posting. **Whether to seek that
   review anyway, before posting, is the author's call and is not a call this repository can make.**

## 2b · ✅ POSTED — `aixiv.260822.000005`, 2026-08-22

**Live at https://aixiv.science/abs/aixiv.260822.000005** (submission_id 1366, version `1.0`, status
`Under Review`). Submitted through [`aixiv-review.yml`](../../../.github/workflows/aixiv-review.yml)
after `PREFLIGHT_FULL=1 ./scripts/preflight.sh` returned **PREFLIGHT OK, exit 0**.

⛔ **IT WAS SUBMITTED WITH `is_public: 0` AND IT IS PUBLIC ANYWAY.** The stored record reads
`is_public: 0`, and an unauthenticated reader still gets **HTTP 200** from both
`/abs/aixiv.260822.000005` — rendering title, author, correspondence e-mail and full abstract — and
`/api/pdf/aixiv.260822.000005`. **The flag is metadata about intent, not access control; there is no
rehearsal mode and every submit is a publication.** Recorded here because the tooling briefly
described `--public 0` as a private-first path, which was an untested assumption and is false.

**The reviewer ran without being asked.** `POST /api/start_attack_review` returned HTTP 500, but the
paper entered at `status: "Under Review"` — what aiXiv's own scheduler polls — and a review by
*Official Agent* (id 1362) appeared about three minutes after submission. It engages the actual
content: the 8.5% vs 12.3% panel dependence, the clustering of every strong call within 0.1264
percentile units of the threshold, and the Q92570-3 isoform match that withdrew `DMPCVQAQY`. Reviews
are committed under `research/literature/aixiv-reviews/`.

⚠ **This is one round from one reviewer, and it is not the convergence test.** `paper-hardening` §8
requires no blockers **and** no P1s across the seat set; this paper stands at round 1 plus one
external seat.

## 3 · Only the author can do these

1. ~~**Post at `biorxiv.org/submit-a-manuscript`.**~~ **Superseded — see the venue note above.** The
   post is now an authenticated API call and is scripted, so it is no longer a browser session: dispatch
   [`aixiv-review.yml`](../../../.github/workflows/aixiv-review.yml) with `mode=dry-run-submit` to read
   the payload, then `mode=submit` with `i_understand_this_is_outward_facing=true`. Licence CC-BY,
   corresponding author ORCID `0000-0002-1823-1451`, and the survivorship non-financial interest
   entered verbatim from Declarations. **The metadata is a committed file**
   ([`emc-vaccine-path-aixiv-metadata.json`](./emc-vaccine-path-aixiv-metadata.json)) rather than a form
   filled twice, so what was submitted is auditable after the fact.
2. **Decide whether this paper gets its own archival deposit** or is covered by the existing Zenodo
   archive. The ASO deposit's DOI is minted and its manifest hashes the repository's artifacts; this
   manuscript's artifacts are in the same tree.

## 4 · Deliberately not done, and why

- **No figure.** Every quantity is in the prose, and the one display item a reader would want — the
  coverage-versus-threshold curve — would restate Section 2.3's ladder without adding to it. If a
  figure is added later it must be cited in first-citation order and rendered as vector.
- **The abstract has not been cut to a journal's cap.** aiXiv's `SubmissionCreate` declares `abstract`
  as a nullable string with no `maxLength`, so it sets none either, and cutting to the wrong
  target means cutting twice.
- **The dated capability bands were removed rather than updated.** See Appendix B of the manuscript
  and §5 of the round-1 ledger.
- **No supplementary information.** Nothing in the paper is a derivation long enough to move out of
  it, now that the forecast table is gone.
