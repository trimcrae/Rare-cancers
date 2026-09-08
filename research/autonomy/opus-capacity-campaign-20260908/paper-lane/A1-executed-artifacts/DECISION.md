# A1 DECISION — research/hypotheses/candidates.json supports NO new paper

Worker A1, OPUS-CAPACITY-CAMPAIGN-20260908. Model SELF-REPORT, NOT INDEPENDENTLY VERIFIED: claude-opus-5.

## Verdict

**0 of 14 candidates supports a substantively separate paper-level question that is not already
covered.** The whole file is the data appendix of an already-**drafted** endpoint,
`PUB-REPURPOSING` (`systems/graph/publications.json`, state `drafted`, document
`research/manuscripts/repurposing/repurposing-hypotheses.md`), which cites
`research/hypotheses/candidates.json` at `:545`. Per the campaign rule, a candidate already inside a
drafted endpoint is NOT new — and here the endpoint is not merely adjacent, it is generated from the
same source table.

## Ranking criterion used

Paper merit, in this order, with each gate binding before the next:
1. **Not already covered** by a drafted/posted endpoint or a recorded closure.
2. **Would change a reader's mind** — a result whose direction is not already the field's or this
   repository's stated position.
3. **Decisive input reachable from committed bytes at $0 without a bench.**
Ease of execution is deliberately excluded and was not used to break any tie.

## Ranked residue (all fail gate 1; ranked by how close they come)

1. **carfilzomib-proteasome** — the only row with a named, $0, non-bench, committed-bytes open item
   (ledger `AUT-PD-112`). It fails gate 1: it is a **correction inside a drafted paper**, not a paper.
2. **vegfr-tki-extension** — largest clinical surface, but its decisive sources (pazopanib primary,
   Sunitinib 2014) are on the `CLOSED-WORK.md` denied/unrecovered list, and its own open question is
   `PUB-FUSION-PARTNER`, drafted and in hardening round 11.
3. **imatinib-kit-subset** — the only T3 row; its open question needs patients that do not exist.
4. **zaltoprofen / pioglitazone (PPARγ)** — ledger `AUT-052` records the literature half CLOSED and
   `AUT-072` records the direction ANSWERED-IN-THE-NEGATIVE; the remainder is a cell panel.
5–14. See `candidate-adjudication.json` for the per-row grade, coverage and missing condition.

## Explicit failure on the named non-grounds

The strongest *generalisable* question the file suggests — that `notTriedInEmc: true` is a
disease-level novelty flag that cannot see negative evidence one level up in the parent histology,
so ultra-rare candidate menus systematically over-report novelty — **is already the drafted paper's
own central analysis and has already been peer-reviewed.** `repurposing-hypotheses-peer-review-2026-08-10.md:44`
names the evidence-versus-novelty anti-correlation as the manuscript's central observation; `:314`
already records that for the enumeration arm "untried" means "absent from a ten-entry internal
list", not absent from the literature; `:321` already requires the novelty claim for **each of the
fourteen candidates** to be restated as resting on a search of undemonstrated recall. Re-proposing it
under a new title, a new owner or a new model would be exactly the move the campaign forbids, and it
is refused on that ground.

## Recommended single next executable checkpoint

**Not a new paper.** The one checkpoint with real merit and reachable inputs is `AUT-PD-112`:
add `EV-MAKI-2005` (class-level clinical bound) and `EV-BOKLAN-2025` (existing carfilzomib
combination schedule) into `repurposing-hypotheses.md` §4.1 and Table 3, **replacing** text rather
than appending, with the Appendix A row and the word budget the venue cap requires.

* (a) **Question.** Does an evidence-graded repurposing menu that screens novelty at the *disease*
  level mislead by omission when the drug class already has a closed trial in the parent tumour
  group? For carfilzomib the answer in committed bytes is yes.
* (b) **Inputs, reachable.** `systems/graph/evidence.json` (EV-MAKI-2005, EV-BOKLAN-2025);
  `research/literature/carfilzomib-class-clinical-2026-08-28.json` — abstract-level, PubMed-retrieved
  2026-08-28, **no full text**: PMID 15739208 carries no PMCID and PMC12428389 was not fetched. Access
  limit: the per-histology enrolment denominator of EV-MAKI-2005 is UNKNOWN and stays UNKNOWN here.
* (c) **Contribution and novelty uncertainty.** It repairs an omission, it does not add a finding.
  Novelty as a *paper*: none — the endpoint is drafted. Novelty as a *correction*: recorded and
  unapplied as of this HEAD.
* (d) **Distinction from prior no-gos.** It is not a synthetic sweep or figure-validation successor;
  not P1–P6, S1/S3 or S6; not NR4A-labelled; touches no denied source; adds no cohort.
* (e) **Acceptance.** The two evidence ids appear in §4.1 and Table 3 of the manuscript by
  replacement, with the Appendix A row, and `python3 research/manuscripts/lint_consistency.py` and
  `lint_citations.py` still exit 0.
* (f) **Stop.** Stop if the replacement cannot be made within the venue word cap without deleting a
  hedge, or if `AUT-PD-112`'s premise fails on reading §4.1. **It is an owner/manuscript act — no
  campaign worker may take it, and A1 did not.**

## What this decision does NOT claim

No efficacy, safety, selectivity, therapeutic-window or readiness claim is made for any of the 14
agents. "Approved elsewhere" is a regulatory fact only. No candidate is asserted to work in EMC —
the file's own disclaimer says none is known to. There is no wet lab, and 9 of the 14 candidates'
own open questions are bench experiments.
