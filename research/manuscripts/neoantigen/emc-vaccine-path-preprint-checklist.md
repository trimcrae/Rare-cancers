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

**v1.1 posted 2026-08-22** (submission_id 1367) carrying the two §2c survivors. ⚠ **A new version
does not withdraw the old one** — aiXiv keeps both rows under the same id — so v1.0 remains readable
and nothing said there is retracted by this.

## 2b-cal · ⭐ WHAT A RATING OF 6 IS WORTH, MEASURED RATHER THAN ASSUMED

`Rating` arrives as a bare integer with **no scale, minimum or maximum** anywhere in the payload or
the OpenAPI schema, and "rating 6" was reported three times in one session as though it carried
meaning. Measured against the public corpus (`aixiv_review.py calibrate`, run 32592101151,
2026-08-22, n=41 reviews over 40 public papers):

| | |
|---|---|
| distribution | min **0**, max **10**, mean **4.32**, median **4** — **n=874 reviews over the whole archive** |
| shape | 0:2 · 1:36 · 2:134 · 3:172 · 4:142 · 5:113 · 6:142 · 7:**100** · 8:27 · 10:4 (plus one 5.5 and one 6.5 — the scale is not integer-only) |
| **ours (v1.0–v1.3, all 6)** | **77th percentile** raw (600 below, 142 equal, 132 above); **68th** once each submitter counts once (n=199) |
| ⛔ **is a 7 rare?** | **No — 100 papers hold one, and 131 hold 7 or better.** The earlier reading that 8 was the ceiling and ≥7 was ~10% came from a 150-paper sample and is superseded |

⚠ *Superseded, retained — the first two calibration runs were measured on ONE PAGE.*
They reported *"min 2, max 8, mean 4.07, median 4 (n=41); ours 84th percentile"* and a de-duplicated
*"68th percentile (n=17)"*. **`/api/submissions/public` paginates and its `limit` defaults to 100**,
so both were computed against ~3% of a 1,327-submission archive, and that page happened to be
dominated by one submitter's serialised resubmissions. Neither figure may be quoted. The corrected
sampler pages to exhaustion and takes every *k*-th paper rather than the first *N*
(run 32594895218).

⛔ **AND THE "THE CORPUS IS SLOP" READING WAS ITSELF AN ARTEFACT OF THAT PAGE.** Across the real
sample the ratings are almost uniform from 2 to 6; the floor is crank physics (two 1s: unification-
of-relativity-and-thermodynamics, modified relativistic dynamics) but it is a **thin** floor, not the
bulk. The 8s are ordinary competent work — a proved identity in modular representation theory, an
empirical study of AI citation behaviour, a cross-architectural LLM introspection study with
multiple independent designs.

⭐ **SO THE STANDING TARGET OF ≥7 IS A TOP-DECILE BAR ON THIS PLATFORM** (trimcrae, 2026-08-22:
*"We should strive to get everything to at least a 7"*), and 8 is the highest anyone in the sample
has reached.

⛔ **SO 6 IS A GOOD RATING HERE, AND THE WORKING ASSUMPTION THAT IT WAS MEDIOCRE WAS WRONG.** It was
never checked against anything; the corpus median is 4.

⚠ **Two things this does NOT establish.** The scale's true maximum is **UNKNOWN** — 8 is the highest
*observed*, and a corpus that never exceeds its own maximum cannot reveal the ceiling. And a
percentile is not acceptance: the aiXiv paper's stated rule is **≥3 of 5 'accept' votes from a
five-member LLM panel**, while both of our reviews came from **one** reviewer ("Official Agent"), so
whatever produced them is not that panel. Neither `status` (100 of 100 read "official review
completed") nor `doi` (4 of 100, each merely echoing the record's own `aixiv_id` with no `10.xxxx/`
registrant prefix) separates accepted from rejected.

## 2b-int · ⛔ THE RATING IS NOT AN AUTHENTICATED SIGNAL, AND FOUR VERSIONS DID NOT MOVE IT

**Four versions, four reviews, every one by `Official Agent`, every one rated 6.**

| version | review | what changed | rating |
|---|---|---|---:|
| v1.0 | 1362 | baseline | 6 |
| v1.1 | 1363 | proteasomal cleavage and TAP named; cross-locus LD stated | 6 |
| v1.2 | 1364 | unreviewed proteome searched, 127,090 entries | 6 |
| v1.3 | 1365 | reframed to lead with the isoform-boundary finding | 6 |

⛔ **`POST /api/submit-review` carries NO security requirement** in `openapi.json` and takes a
free-text `reviewer` field, so any party can post any rating on any paper. The full corpus shows what
that produces: a **rating of 10 whose entire review text is "Nah"**, and another 10 whose review reads
*"0 Axiomas 0 postulados = ABARCA TODO LO FÍSICAMENTE EXISTENTE"*. A reviewer calling itself
`Anonymous Agent` also appears. **So the number is not a quality measurement that can be chased on its
merits, and this repository will not post a review of its own work to move it.**

⚠ **The recurring finding cannot be closed here.** Every round returned "purely computational scope
without experimental validation" — and this programme has no wet lab by design. Meanwhile v1.2's
summary called the paper *"rigorous, transparent, and intellectually honest"* with *"exceptional
clarity"*, and still scored 6. Polish was never the binding constraint, and neither was the finding.

⭐ **The paper improved across those four versions and that is the part worth keeping** — a closed
reference, a searched unreviewed proteome, a named processing limit, and a result promoted out of a
limits ledger into the title. Only the score was unmoved.

## 2c · The external round, verified — 2 of 7 findings survived

Review 1362 (*Official Agent*, rating **6**) verified against the artifacts under `paper-hardening`
§5, **refute by default**. Main text **7,557 → 7,616 words (+59)**.

⚠ *Superseded, retained: "Budget declared before applying: **+60 words** on main text; delivered
**+59**."* The **+60 was a cap this repository invented** — aiXiv imposes no length limit of any kind,
so six words were trimmed to meet a number no venue asked for (trimcrae, 2026-08-22:
*"We don't need a word budget on aiXiv submissions"*; rule now scoped in `paper-hardening` §1). The
**delta is still measured and reported**, because the thirteen-round evidence behind that rule is a
prose failure — closing findings by appending qualifiers — and that gate is replace-not-append, which
this round met: both survivors rewrote the sentences they touched.

| finding | verdict | evidence |
|---|---|---|
| Purely computational; no wet-lab validation | **REFUTED as a defect** | Stated in the frontmatter scope, the abstract's closing sentence and §7. It is the programme's declared condition, not an unreported gap |
| Pooled 30.4% "treats patients as if they could have any of the five junctions" | **REFUTED** | §2.3 already draws exactly this distinction and justifies pooling by it: *"Because an individualised platform selects against the patient's own genotype rather than a public epitope, the relevant figure is the pooled-junction one"* |
| Coverage rests on a single HLA-B\*15:01 call, unacknowledged | **REFUTED** | The abstract and §2.3 both state each presenting allele rests on one peptide-allele call, all five within 0.1264 percentile units of the threshold |
| Regional variance makes one accrual number misleading | **REFUTED** | §2.3 reports the regional spread and says the no-panel-reaches-half claim *"holds for the pooled global frame and not everywhere"* |
| "Does not test or discuss the impact of linkage disequilibrium" | **REFUTED as stated, PARTIALLY VALID underneath** | §7 already disclosed the independence assumption **and quantified** the same-locus correction at ~0.3 pp — further than the review credits. What was genuinely missing is that cross-locus haplotype LD is unmodelled and unestimated. ✅ **Applied** |
| Proteasomal cleavage / TAP transport not modelled | ✅ **VALID — applied** | `grep -i "proteasom\|TAP"` over the manuscript returned **nothing**. The paper bounded its calls generally ("a screen, not evidence of presentation") but never named the unmodelled steps. §7 now does |
| Compare against immunopeptidomics pipelines; cover DNA/RNA vaccine design, bispecifics, CAR-T | **DECLINED, with reason** | A scope expansion, not a defect. §1's length gate governs, and those routes are other papers' endpoints in [L3](../../../systems/views/L3-publications.md) — restating them here duplicates a fact that has a home |

⭐ **The review's care is worth recording, because it bears on how much weight the seat gets.** It
distinguished the lead peptide (`NMPCVQAQY`, HLA-B\*15:01) from the withdrawn one (`DMPCVQAQY`,
HLA-B\*35:01) correctly, and cited section numbers that exist. Its two misses were both **claims that
the paper omits something it in fact states** — the failure mode of a reader working from one pass,
which is exactly what `paper-hardening` §4 predicts an external seat cannot do as well as the
repository-grounded seats.

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
