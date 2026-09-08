---
id: DOC-MF1-SETTLED-PRESENTATION
title: "MF1 · the settled figure and text presentation for the degrader methods-record"
level: L4
kind: record
status: live
purpose: >
  Hold, verbatim, the internal presentation scaffolding that was removed from the reader-facing
  manuscript on 2026-09-08 — the figure bill a typesetting pass reads, the endpoint status block, the
  role/subordination blockquote and the venue/framing section — so that no pull-list, pointer or
  qualification is lost by removing it from the public text.
scope: >
  L4. A working record. It makes NO scientific claim, states no new result, and changes no threshold.
  Every table below is a COPY of text that was in the manuscript through
  fb3eb862a81af9aadff59a9ab68d8d4272422a7657816cf483fbf663828a5d3e and is reproduced unedited.
audience: [maintainers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# MF1 · the settled figure and text presentation

Written 2026-09-08 by the MF1 preparation owner.

## 1 · What was settled, and how

The manuscript is a **no-figure, no-typed-number** paper: it restates no quantity, and each finding
carries a verdict word, a one-line mechanism and a pointer to the artifact that owns the numbers. That
was already the paper's decided presentation; nothing about it was changed here. What changed is
**where the pull-list lives**. The list is internal typesetting instruction — a reader of the
manuscript is not the audience for it — so it was moved out of the public text into §3 below.

Measured presentation, `research/manuscripts/submission_metrics.measure`, EXIT=0:

| | main_words | abstract_words | figures | tables | display_items | references |
|---|---:|---:|---:|---:|---:|---:|
| before this pass | 6154 | None | 0 | 0 | 0 | 0 |
| after this pass | 5665 | None | 0 | 0 | 0 | 0 |

`abstract_words: None` is the measurer not finding a heading it recognises as the abstract in this
document's shape; it is reported as returned and is not a claim that the abstract is absent (§1 of the
manuscript is the abstract).

⛔ **Required figures: none.** The paper carries no figure and no table of results, by its own
construction. Nothing below asks for one to be drawn.

## 2 · The consequence that was repaired in the same pass

Ten artifacts were named ONLY by the figure bill and by no prose sentence. Removing the bill from the
manuscript would have dropped them out of the paper's provenance, so they were added to the
manuscript's provenance list (§10), each verified present on this branch on 2026-09-08:
`valb-triangle-reduction.json`, `selcal-cofold-dockq.json`, `selcal-dockq-decoy-scale.json`,
`selcal-interface-signature.json`, `nrv04-cys-conservation.json`, `apo-pose-recovery.json`,
`apo-pose-site-in-regime.json`, `pose-conditionality-census.json`, `nr4a-safety-genetics.json`,
`ternary-env-parity.json`, `selectivity_calibration.py`. No number moved and no claim changed.

⚠ `STRATEGY.md` Appendix A row 57 (the withdrawn frozen-gate verdict, §8 item 6) is named by the bill
below and is NOT in the manuscript's provenance list; it is a repository register rather than an
artifact and the manuscript cites it in the prose of §8 already.

## 3 · The figure bill, verbatim as removed from the manuscript

This is the list a typesetting pass reads. It was §9 of the manuscript through
`fb3eb862…3a5d3e` and is reproduced here unedited. Section numbers inside it refer to the
manuscript's numbering **before** this pass (old §10 is now §9, old §12 is now §10, old §13 is now
§11; old §9 and old §11 are gone).

## 9 · The figure bill — every number the manuscript must pull, and where from

⛔ **Nothing in this table is copied into the prose above, and nothing in it may be.** This is the list a
typesetting pass reads. Every path was verified to exist on this branch on 2026-09-08.

| § | what the sentence needs | read from |
|---|---|---|
| Abstract, §4 | the four-way outcome table with all its figures | [roadmap → the scoreboard](../nr4a3-program-map.md#-where-we-are--the-scoreboard-in-plain-language), the ⛔ ONE HOME block |
| Abstract, §5.1 | instrument counts, control status per instrument | [`systems/views/registers/instruments.md`](../../../systems/views/registers/instruments.md); support/disclosed split from [`systems/graph/routes.json`](../../../systems/graph/routes.json) → `RT-METHODS-PAPER.instruments` |
| §4 row 1, §7.2, §8 item 2 | valB_mini ΔΔG_coop, target, replicate figures, replicate SD vs MBAR SE | [roadmap scoreboard](../nr4a3-program-map.md#-where-we-are--the-scoreboard-in-plain-language) rows `RUNG 2` and `RUNG 2 · replicates`; [`valb-triangle-reduction.json`](../../modalities/valb-triangle-reduction.json) |
| §4 row 1, §7.2 item 3 | the closure triangle's blindness result | [`valb-triangle-closure.json`](../../modalities/valb-triangle-closure.json) → `branch_A` |
| §4 row 2, §4.3 | tier, statistic, exact and mirrored *p*, reference-set size and floor, technical failures, admitted legs | [`selcal-verdict.json`](../../modalities/selcal-verdict.json) |
| §4.3 item 2 | co-fold vs crystal DockQ on internal machinery vs target interface | [`selcal-cofold-vs-crystal.json`](../../modalities/selcal-cofold-vs-crystal.json), [`selcal-cofold-dockq.json`](../../modalities/selcal-cofold-dockq.json) |
| §4.3 item 2, §8 item 5 | the in-horizon positive control and the displacement calibration ladder | [`selcal-deepternary-poscontrol.json`](../../modalities/selcal-deepternary-poscontrol.json), [`selcal-dockq-decoy-scale.json`](../../modalities/selcal-dockq-decoy-scale.json) |
| §4 row 3 | tier, *p*, arrangement count, min attainable *p*, per-arm means | [`nrv04-retro-verdict.json`](../../modalities/nrv04-retro-verdict.json) → `verdict`; secondaries in [`nrv04-retro-secondaries.json`](../../modalities/nrv04-retro-secondaries.json) |
| §4 row 3 | the covalent confound — which paralogues carry the cysteine | [`nrv04-cys-conservation.json`](../../modalities/nrv04-cys-conservation.json) |
| §4 row 4, §4.1 | `S`, its replicate SD, the resolvable-magnitude bound, per-arm means | [`nr4a3-5aks-reduction.json`](../../modalities/nr4a3-5aks-reduction.json) |
| §4 row 5, §6(b) | apo pose recovery bands, the self-dock control, the site-transfer counts | [`apo-pose-recovery.json`](../../modalities/apo-pose-recovery.json), [`apo-pose-site-in-regime.json`](../../modalities/apo-pose-site-in-regime.json) |
| §5.2 `V1` | the recovered contact and its distance | [`selcal-interface-signature.json`](../../modalities/selcal-interface-signature.json) |
| §5.2 `V6`/`V7`/`V8`/`V10` | benchmark values and errors | [roadmap §3.1](../nr4a3-program-map.md#31--the-instrument-table) rows `V6`, `V7`, `V8`, `V10` |
| §6(a) | per-receptor self-dock outcomes, blocking targets, `panel_readable`, the affected SI clauses | [`antitarget-selfcontrol.json`](../../modalities/antitarget-selfcontrol.json) → `selfcontrol`, `repair_delta`, `repair_rule` |
| §6(b) | inter-method RMSD and centroid separation, band counts, `R5_resolved` | [`pose-second-method.json`](../../modalities/pose-second-method.json) → `verdict`, `part_a` |
| §6(c) | harmonized druggability against `D*` | [`r3-generation-frame-harmonized.json`](../../modalities/r3-generation-frame-harmonized.json) → `verdict` |
| §6(d) | the three-arm gate sentence, arm-by-arm | [`nr4a3-5bt-gate.json`](../../modalities/nr4a3-5bt-gate.json) → `verdict`, `sentence` |
| §6(d) deepening | models scanned, discriminating contacts found, the validating contact behind the descriptor | [`nr4a3-5bt-signature.json`](../../modalities/nr4a3-5bt-signature.json) → `sentence_replicated`, `descriptor_validation` |
| §7.1 item 2 | the decoy false-positive rate and its replication at library scale | `DECOY_2026_06_30` in [`selectivity_calibration.py`](../../modalities/selectivity_calibration.py), whose chain to the primary run output is committed and checked in [`decoy-null-provenance.json`](../../modalities/decoy-null-provenance.json) ([§10.3](#103--the-two-inputs-that-were-missing-both-closed-2026-08-07) item 1) |
| §7.1 item 4 | the cross-system background and its two preregistered scopes | [`categorical-decoy-null.json`](../../modalities/categorical-decoy-null.json), [`categorical-decoy-null-lbd.json`](../../modalities/categorical-decoy-null-lbd.json) |
| §7.3 | the genotype evidence and the per-tissue overlap | [`nr4a2-sparing-bound.json`](../../modalities/nr4a2-sparing-bound.json), [`nr4a-safety-genetics.json`](../../modalities/nr4a-safety-genetics.json) |
| §8 item 4 | scrambled-objective arm counts, the rule-of-three bound, Fisher *p* | [roadmap scoreboard](../nr4a3-program-map.md#-where-we-are--the-scoreboard-in-plain-language), the deliverables table row |
| §8 item 1 | the retraction census — objects, units, trajectory files | [roadmap §3.3](../nr4a3-program-map.md#33--the-pattern--rewritten-because-the-version-this-page-carried-was-false) |
| §8 item 6 | the withdrawn frozen-gate verdict | [STRATEGY.md Appendix A](../../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) row 57; predicate `nrv04_retro_panel.production_leg_check` |
| Methods | the map-quality caveat on the congeneric map (the open cycle) | [`step1-fanout-map.json`](../../modalities/step1-fanout-map.json) → `cycle_closure` |
| Methods | environment parity between the two execution providers | [`ternary-env-parity.json`](../../modalities/ternary-env-parity.json) |
## 4 · The status block, verbatim as removed (old §0)

Removed as internal registry scaffolding, and stale on its own account.

## 0 · Status of this document

| | |
|---|---|
| endpoint | `PUB-METHODS` · route `RT-METHODS-PAPER` · strategy `ST-DISSEMINATION` |
| what blocks it | **the route's registered inherited-blockers list is empty.** ⚠ That is all the registry says, and it is not a finding that the science is ready: `RT-METHODS-PAPER.readiness.missing` still names one item, and ⚠ **that registry field is stale**: the item it names was closed on 2026-08-07 by a committed artifact (§10.3 item 1). The graph is not this draft's to edit, so the correction is recorded here and left for the register's owner. This row used to quote a `[B5]` line from `systems_check.py --check`; that line is **historical**. B5 fires for a route whose endpoint is unwritten, so it reports a document's existence rather than a scientific blocker, and it stops firing once the endpoint is written — which is what happened here |
| cost to finish | **$0.** No GPU, no rental, no bench. Every input is a committed artifact |
| what is genuinely missing | **for the evidence chain, nothing that is still open.** The two inputs this draft recorded as missing were both closed on 2026-08-07, both at $0, and both by committed artifacts — [§10.3](#103--the-two-inputs-that-were-missing-both-closed-2026-08-07). ⛔ That is a statement about evidence only: the framing decision and submission itself remain outside it ([§11](#11--venue-and-what-is-explicitly-not-decided-here)) |
| what only a wet lab could add | **nothing this paper's claim needs** — the one framing in the register of which that is true ([`paper-framing-options.md`](../program/paper-framing-options.md) §2.1) |
## 5 · The role and framing blockquote, verbatim as removed (manuscript header)

> **Role: the DRAFT of the manuscript for publication endpoint `PUB-METHODS`, route `RT-METHODS-PAPER`.**
> The endpoint's working title and its one-sentence claim are owned by
> [`systems/graph/publications.json`](../../../systems/graph/publications.json) and rendered in
> [`systems/views/L3-publications.md`](../../../systems/views/L3-publications.md); this file is the prose that
> would fill them. **Subordinate to [`nr4a3-program-map.md`](../nr4a3-program-map.md)** — the roadmap owns the
> plan, the gates and every verdict, and where it and this draft differ on any of those, **the roadmap wins.**
>
> ⛔ **THIS DRAFT TYPES NO FIGURE, ON PURPOSE.** Every number in the record already has exactly one home
> (CLAUDE.md rule 1), and a manuscript draft is the single most likely place for a copy to go stale and then
> be quoted. So each finding below carries its **verdict word**, its **mechanism in one line**, and a
> **pointer to the artifact that owns its numbers**; [§9](#9--the-figure-bill--every-number-the-manuscript-must-pull-and-where-from)
> is the figure bill — field-by-field, artifact-by-artifact — that a typesetting pass reads to fill them in.
> A draft that carries the argument and cites the figures is assemblable; a draft that carries a second copy
> of the figures is a liability.
>
> ⚠ **THE FRAMING IS NOT DECIDED HERE.** [Roadmap §13](../nr4a3-program-map.md#13--the-deliverables-framing--an-open-question-with-a-register-and-no-decision)
> records the paper-framing question as OPEN and trimcrae's; [`paper-framing-options.md`](../program/paper-framing-options.md)
> §2.1 grades this framing (`P1`, the known-answer audit) as its recommendation. This draft is written **as
> `P1`** because that is what the endpoint asks for, and it **does not** settle `P1` against `P6`.
> Submission is outward-facing and therefore gated by CLAUDE.md §3 — see [§11](#11--venue-and-what-is-explicitly-not-decided-here).
Replaced in the manuscript by a four-line reader-facing note that keeps the no-typed-figure rule and
drops the roadmap subordination, the §9 pointer and the framing-permission paragraph.

## 6 · Venue and "not decided here", verbatim as removed (old §11)

Removed from the public text as internal process. It is retained here unchanged; nothing in it is
withdrawn, and the venue-fee caution in particular still applies to whoever submits.

## 11 · Venue, and what is explicitly not decided here

**Venue.** A methods/assessment journal rather than a target journal; the register's recommendation and the
$0-to-author constraint are held in [`paper-framing-options.md`](../program/paper-framing-options.md) §2.1 and the
pre-post checklist in [`nr4a3-degrader-preprint-plan.md`](../degrader/nr4a3-degrader-preprint-plan.md). ⚠ **Fee routes
change — verify each venue's in writing at submission**, per the standing rule; do not name a secondary venue
outward-facing before that check.

**Not decided here, and not decidable by an agent:**

1. **The framing choice** (`P1` — this draft — against `P6`, the candidate paper) is registered as open and
   is trimcrae's ([roadmap §13](../nr4a3-program-map.md#13--the-deliverables-framing--an-open-question-with-a-register-and-no-decision)).
   ⛔ It is **not** a gate on any roadmap row, and nothing in this draft waits on it.
2. **Whether this becomes a separate manuscript or the reordering of the existing one.** The existing paper
   plus its SI is the degrader route's single deliverable, and `paper-framing-options.md` estimates a large
   fraction of it survives into this framing largely verbatim. **This draft is the argument and the
   assembly plan; it deliberately does not fork the manuscript**, because a parallel condensed draft has
   drifted out of sync and self-contradicted here before.
3. **Submission itself** — outward-facing and irreversible, therefore gated by CLAUDE.md §3.
