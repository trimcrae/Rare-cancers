---
id: DOC-FUSION-JUNCTION-ASO-PAPER-REDTEAM-ROUND10
title: "Round-10 blind review of the fusion-junction ASO journal article — one real defect, in a sibling document nobody read"
level: L3
kind: manuscript
status: live
canonical_for:
  - round 10 blind adversarial review of the ASO journal article
purpose: >
  Round 10 hardening of PUB-ASO, re-seating on the text round 9 corrected. Five blind seats reviewed
  the pinned commit. Zero blockers, zero P1s in the article's own prose; one real P1 in the
  GENERATED table captions (a cross-reference leaked from the sibling extended report), fixed this
  round at its generator. Two P2 notes recorded, not applied.
scope: >
  Computational design and specificity screening only. No wet-lab experiment was performed, and
  nothing here asserts efficacy, potency, safety, a therapeutic window, delivery to a tumour, or
  clinical readiness for any sequence. Every sequence named is a research reagent for laboratory
  investigation only and must not be administered to any person or animal.
audience: [external reviewers, collaborators, maintainers]
date: 2026-08-27
last_verified: 2026-08-27
---

# Round 10 — blind adversarial review of the ASO journal article

**Subject.** `research/manuscripts/aso/fusion-junction-aso-journal-article.md` at pin
`8ce32163948a84cb33ff3ef8e0841acde1775744`, blob sha256
`40ace959a67c4ffdb5cb660d7541ae19d548444c97efdaf45ba27d7874b25319`, 4,613 words. This is round 9's
corrected text, unchanged since `f8cba4b` — confirmed by diff against that commit before seating.

**Seats.** Five blind lenses, dispatched as parallel subagents (research-loop's session shape, since
this cycle had no `create_session` mechanism available for a spawned successor): regression against
round 9's repairs; arithmetic re-derived from the committed artifacts; statistics and experimental
design; citations, build and gate coverage; hostile referee. No seat saw another's output or this
document while working.

---

## Result: the article's own prose is clean

**Zero blockers, zero P1s in `fusion-junction-aso-journal-article.md` itself**, across all five
lenses. In detail:

- **Seat 1 (regression on round 9's repairs).** Every one of D1, D2, D3 and the four "also applied"
  fixes verified holding at this pin, quote-checked against the artifacts each depends on. All four
  guard fixes (G1–G4) verified still firing correctly. No new contradiction or backslid claim found
  in a full read.
- **Seat 2 (arithmetic).** Every printed count, percentage, denominator and CI re-derived from the
  producing artifact (`aso-parent-null.json`, `aso-parent-gap-pairing.json`,
  `aso-premrna-offtarget.json`, `aso-offtarget-duplex-energy.json`, `fusion-junction-aso-reagent-
  coverage.json`, `fusion-junction-aso-sequences.csv`) and matched exactly, including non-trivial
  recomputations (the union of mature+precursor liability = 93, the sign-change count = 4, the
  own-parent/cross-parent split = 85/2). Two P2 notes, below.
- **Seat 3 (statistics and design).** Wilson intervals correctly reserved for the Monte Carlo null
  ensembles; the falsification criterion is explicit, matched to named test articles and controls,
  and carries a genuine power/voidness analysis. One P1 candidate, downgraded on review — below.
- **Seat 4 (citations, build, gates).** All 23 in-text citations resolve correctly, in contiguous
  first-citation order, in the file that actually governs this document
  (`fusion-junction-aso-journal-references.md` — seat 4 independently rediscovered that
  `fusion-junction-aso-references.md/.json` are generated from a *different* source document and
  is a naming trap for the next editor, not a defect in the paper; recorded below). Build-stamp
  provenance recomputes exactly. The scope/safety guards (`nothing synthesised or tested`,
  financial-only COI, no efficacy/therapeutic-window/clinical-readiness language) all target the
  journal article specifically, not only its siblings. One real P1, in a sibling artifact — below.
- **Seat 5 (hostile referee).** Verdict: minor revision. Central claim restated accurately; no
  internal contradiction found; the oversell test (proteome-wide selectivity, efficacy, safety,
  therapeutic window, clinical readiness) passed on every axis, explicitly checked. All three
  objections raised are clarity requests, not correctness failures — recorded, not applied, below.

## The one real defect — and it was in a sibling document nobody read

**P1 · Table 2's caption pointed at a section that does not exist in this document.**

`fusion-junction-aso-journal-tables.md` (GENERATED from `research/manuscripts/aso_journal_tables.py`,
never hand-edited) read: *"Section 5 gives why that screening step is what makes a scramble a
control."* The journal article has no numbered sections at all — its headings are Abstract,
Introduction, Materials and Methods, Results, Discussion, with unnumbered subheads. "Section 5" is a
leak from the sibling **extended report** (`fusion-junction-aso-research-article.md`), which has a
numbered `## 5 · Bounds on every claim, and the conditions for falsification` — the section that
does discuss scramble screening in that document. It would have rendered exactly as written in the
submitted PDF (build-stamp hash for `journal-tables.md` matched this exact text before the fix), and
a reviewer or editor encountering "Section 5" in a document with no numbered sections would have had
no idea what it meant.

This is precisely the one-of-a-pair / one-instrument-bound-to-one-sibling defect class
`paper-hardening` §6 warns about, found by the lens that asks "what reads this sentence?" —
`test_the_journal_display_items_say_what_their_rows_say.py`'s 14 tests validate table content
against the sequence CSV but none of them cross-check a caption's prose references against the
article's own heading structure.

**Fix, applied at the generator** (`research/manuscripts/aso_journal_tables.py`), replacing rather
than appending, and **word-neutral** (14 words → 14 words, matching Table 1's own style of naming a
section by its heading rather than a number):

> — Section 5 gives why that screening step is what makes a scramble a control.
> + The Controls section above explains why that screening step makes a scramble a control.

`fusion-junction-aso-journal-tables.md` regenerated from the fixed generator (`python3
research/manuscripts/aso_journal_tables.py`); no other document in the repository carried the stale
string (`grep -rl` swept clean after the fix). All four dependent PDFs rebuilt
(`build_submission_pdf.py --paper aso-journal` in every style: journal, manuscript, preprint, plus
`--anonymized`) — the journal-style PDF held at **6 pages**, the budget this submission has zero
slack against.

⚠ **The three `.docx` submission parts (title page, figure legends, manuscript) could not be
rebuilt in this sandbox** — `soffice`/LibreOffice is installed but fails to load any source file here
(the documented, pre-existing sandbox defect; see `.github/workflows/aso-submission-parts.yml`'s own
header). Routed to that workflow rather than faked locally, per the established pattern
(AUT-PROP-021). Dispatched this cycle; see the receipt for the run id.

## Recorded, not applied

**P1-candidate, downgraded to a suggestion · the panel's "own 95% interval" is a heuristic overlap
check, not a formal sampling CI.** Seat 3: *"the strongest null's 40.6% falls inside the panel's own
95% interval on 45.8%"* computes a Wilson interval on the 190-design panel's point estimate, and the
panel is an exhaustive census of tiled registers, not an i.i.d. sample — the paper itself documents
strong correlation between adjacent registers two paragraphs earlier ("Consecutive registers of one
seam differ by a single-base slide and can carry opposite verdicts"). Re-graded against §8.0's test
before any prose was touched: **not a blocker** (no reader is misled about the finding — the error, if
any, is in the interval's formal justification, not its direction, and it is conservative: a
correctly-widened interval would only make the null-overlap finding *more* likely to hold, never
less) and **not a P1 by the strict definition** (there is no future edit this would silently break;
it is a present question about statistical framing, not a guard gap). Recorded as a suggestion for a
future round with room in the word budget, not applied here — the article is at zero page slack and
this would only add words to remove a nicety, not a defect.

**P2 · reference-file naming trap (seat 4).** `fusion-junction-aso-references.md/.json` are
generated from `fusion-junction-aso-working-record.md`, a *different* source document than the one
that actually feeds this paper (`fusion-junction-aso-journal-references.md`, per its own banner and
`test_journal_references_match_the_prose.py`). Not a defect in the paper — every citation in the file
that governs it resolves correctly — but a real trap for the next editor who greps for "references"
and finds the wrong file first. Filed as a process note; no ledger item opened, since fixing a
filename collision that has never actually misled an edit is not warranted work over the several
higher-priority ready items ahead of it.

**P2 · Declarations wording vs. the posted Qeios v1 record (seat 4).** `publications.json`'s
`PUB-ASO.posted.declarations_as_posted.coi` (v1, posted 2026-08-27) reads the unqualified "No
potential competing interests to declare"; the current manuscript reads the financial-scoped "No
competing financial interests exist" — the deliberate round-8 correction that moved the broader
non-financial disclosure to the cover letter instead. This is not a live inconsistency: v1's posted
record is a frozen historical stamp of what actually went out before round 8's fix, and the current
manuscript carries the corrected wording going into v2. No action needed; the field should stay
frozen as the v1 record and not be retroactively edited to match text that postdates it.

## Convergence

**Not fully converged, and honestly so, by this series' own standard** (round 9: *"the round did not
find eight blockers, and a round-10 synthesis that produces eight again should be read as evidence
about the synthesis before it is read as evidence about the paper"* — round 10 found one, in a
sibling document, which is the trend this standard predicts). The article's own prose passed five
independent lenses clean. `publish_bar` clause 1 (`hardening_converged`) does not close on this
round's own record, per its own rule: a round that found and fixed a real defect is not the round
that gets to certify nothing was found. **Round 11 should re-seat on the corrected tables file**
(and confirm the rebuilt `.docx` parts once the CI rebuild lands) — if it returns clean, that is the
round that closes clause 1.
