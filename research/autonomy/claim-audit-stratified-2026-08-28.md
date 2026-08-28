---
id: DOC-CLAIM-AUDIT-STRATIFIED-2026-08
title: Stratified claim audit of the ASO journal article — the interpretation stratum measured, not assumed
level: L3
kind: memo
status: live
canonical_for:
  - this repository's measured Supported/Refuted/Unverifiable rate by claim type
  - the answer to whether our interpretation-claim rate sits near Kosmos's 57.9%
purpose: >
  AUT-PROP-033 asked whether this repository's own interpretation-claim support rate sits near the
  57.9% Kosmos measured, which would mean lint_citations and lint_claims are silent on exactly the
  claim type most likely to be wrong. This is the measurement, on a real sample of a real
  manuscript, with the evidence for every verdict.
scope: >
  One manuscript, thirty sentences, ten per stratum, one verifier. It owns the measured rates and
  the gate-coverage conclusion. It does NOT own the sampling method (claim_audit.py's docstring
  does), the Kosmos figures (method-watch-autonomy-prior-art-2.md §4.1 does), or any change to the
  manuscript — every finding below is reported, none is applied.
audience: [maintainers, autonomous research agents]
date: 2026-08-28
last_verified: 2026-08-28
related: [DOC-METHOD-WATCH, DOC-EMC-AUTONOMY-ARCHITECTURE, DOC-FUSION-JUNCTION-ASO-JOURNAL]
---

# Stratified claim audit — ASO journal article, 2026-08-28

**The question, from AUT-PROP-033.** Kosmos had 102 statements from three reports independently
classified Supported/Refuted by expert scientists who had to reproduce the analysis or find the
literature support, and the rate split hard by statement type: data-analysis claims 85.5%,
literature claims 82.1%, **interpretation claims 57.9%**
([method-watch-autonomy-prior-art-2.md §4.1](../method-watch-autonomy-prior-art-2.md)). Against our
own gates that is uncomfortable in a specific way: `lint_citations` instruments the 82.1% axis and
`lint_claims` R1–R5 instruments claim strength, and neither instruments the 57.9% axis, because an
interpretive sentence carries no citation to resolve and no number to pin. The proposal asked
whether our own interpretation rate sits near 57.9%. This is the measurement.

## What was done

`research/manuscripts/claim_audit.py` enumerates a manuscript's claim sentences, assigns each the
type that decides **what a verifier would have to do** — re-find a source, reproduce a number, or
judge an inference — and draws a seeded stratified sample with the evidence handle for each row. It
emits `verdict: null` and never fills one in; the reason is in its docstring and is the point of the
whole exercise.

On `research/manuscripts/aso/fusion-junction-aso-journal-article.md` at sha256 `40ace959a67c4ffd…`,
seed `20260828`, ten per stratum:

| stratum | population | sampled |
|---|---|---|
| DATA-ANALYSIS | 74 | 10 |
| LITERATURE | 24 | 10 |
| INTERPRETATION | 62 | 10 |
| excluded as non-claim | 27 | — |

Manifest: [`fusion-junction-aso-claim-audit-manifest.json`](../manuscripts/aso/fusion-junction-aso-claim-audit-manifest.json).
Verdicts and their evidence: [`fusion-junction-aso-claim-audit-verdicts.json`](../manuscripts/aso/fusion-junction-aso-claim-audit-verdicts.json).
Regenerate the sample with the `reproduce` command the manifest carries.

Every verdict was reached by **reproducing the number from the artifact that owns it, or re-finding
the source**, never by re-reading the manuscript. Literature re-finds went to PubMed, including PMC
full text for two articles.

## The stratified rates

| stratum | supported | refuted | unverifiable | rate | Wilson 95% | Kosmos |
|---|---|---|---|---|---|---|
| DATA-ANALYSIS | 9 | 0 | 1 | **90.0%** | 59.6–98.2% | 85.5% |
| LITERATURE | 10 | 0 | 0 | **100.0%** | 72.2–100% | 82.1% |
| INTERPRETATION | 7 | **3** | 0 | **70.0%** | 39.7–89.2% | 57.9% |

**Does our interpretation rate sit near Kosmos's 57.9%?** The honest answer is that at n = 10 per
stratum it cannot be distinguished from it. 57.9% lies inside the Wilson interval on 70.0%
(39.7–89.2%), and so does 90.0%. What the sample *does* establish is the **shape**, and the shape is
Kosmos's: interpretation is the worst-performing stratum, it is the only stratum with any refutation
in it, and the gap between it and the other two — 70.0% against 19 of 20 pooled, 95.0% — is where
every failure in this sample lives. **Three refutations in ten interpretation claims, zero in twenty
data and literature claims.** That is the finding; the point estimate is not.

## What the three refutations are

Each is refuted by an artifact this repository already holds, and in two of the three the refuting
evidence is elsewhere in the same manuscript.

1. **`:194` — "The parent liability … is invisible to the instrument a designer would ordinarily
   use, at any threshold that instrument is normally run at."** Recomputing identity at the parent
   liability site each row of `aso-parent-gap-pairing.json` names, the 87 liable designs sit at
   10–14/16 identity, median 12/16, and **seven are at 14/16 — inside the manuscript's own ≥14/16
   near-match threshold**. A three-mismatch budget returns 37 of 87 (42.5%). And the same blastn
   ≥14/16 screen at the deeper result ceiling returns `n_parent_or_intended_hits` of 3, 1, 3, 3, 2
   and 3 for six of those designs, where the default ceiling returned 0 for five of the six and 1
   for the sixth — the threshold is identical in both files, and what removes parents from the off-target list is
   `method.parent_set.names_excluded`, an explicit exclusion. **What survives:** the mechanism holds
   for the large majority at a one- or two-mismatch budget. The universal quantifier does not.
2. **`:295` — "…every design here being specific to the exon pair it was tiled at."** The panel's
   190 design rows carry 176 distinct sequences, of which **nine occur at more than one exon pair,
   covering 23 rows (12.1%)** — including the lead reagent `GGGCATATCATCAAAC`, which appears at
   *EWSR1* e12, *FUS* e10 and *TAF15* e11. **The manuscript says so itself in the Figure 1 legend.**
   Two sentences of one paper contradict each other. **What survives:** the requirement the clause
   supports — sequence the breakpoint before ordering — is unaffected and, given a sequence spanning
   three junctions, strengthened.
3. **`:348` — "A junction design's most plausible wild-type liability is its own parent…"** On
   `aso-offtarget-duplex-energy.json`, 175 of 190 designs carry a gap-paired non-parent near-match,
   45 within 2 kcal/mol of their intended duplex, and 8 a fully paired 16/16 off-target duplex at
   ΔΔG 0.000 — **six of those eight against curated RefSeq records** (LYPD6B `NM_001317003`, ZNF215
   `NM_001354853`), not predicted models, so the paper's own "mostly predicted transcript models"
   caveat does not dispose of them. The parent screen never produces a run longer than 13 bp
   anywhere in the panel. **What survives, stated because it bounds the refutation:** the alignment
   screen excludes parent records by name and accession, so the energy artifact contains no parent
   record and the two arms are not on a common scale — which the manuscript's own next sentence
   concedes. This refutes the comparative as written, not the a-priori argument, for which no
   committed evidence exists either way.

⭐ **All three are the same defect, and it is Kosmos's named one: an excessively strong claim.** Not
a wrong number, not a bad citation — a universal quantifier ("any threshold", "every design",
"most plausible") asserted over evidence that supports the majority case. Each would survive if the
quantifier were dropped.

## What this says about `lint_claims` and `lint_citations`

⛔ **Neither gate could have caught any of the three, and this is a structural statement, not a
tuning complaint.**

- `lint_citations` reads whether a cited record exists and carries the fields we attribute to it.
  **All three refuted sentences carry no citation at all** — that is what put them in the
  interpretation stratum. There is nothing for the gate to resolve. Consistent with its own
  performance in this sample: the literature stratum scored 10 of 10, and every PMID re-found on
  PubMed matched its committed record field for field.
- `lint_claims` R1–R5 reads claim STRENGTH — verb discipline and the never-imply bans. All three
  sentences are already appropriately hedged in form ("most plausible", "would ordinarily"); one is
  a bare structural assertion. **Strength is orthogonal to whether the quantifier is true.** This
  repository has now recorded that orthogonality three times from three directions: a hedged
  sentence on a fabricated PMID passes `lint_claims` (CLAUDE.md §7); claim strength is orthogonal to
  claim DIRECTION (CLAUDE.md §6, the thirteen inverted claims); and now claim strength is orthogonal
  to **claim SCOPE**.
- `claim_coverage.py` enumerates which sentences any instrument watches. It answers "would anything
  notice if this changed", not "is this true", and says so. A sentence can be fully covered and
  false.

★ **The honest conclusion.** The gap AUT-PROP-033 predicted is real and this sample found it on the
first manuscript tried. What it is NOT is an argument for a new linter: a regex cannot decide
whether "any threshold that instrument is normally run at" is true, and a tool that tried would be
the self-scoring failure `claim_audit.py` refuses to become. **The instrument for this axis is a
human or a blind seat reproducing the artifact, and the cheapest form of it is the stratified sample
this tool now makes reproducible.**

## What bounds this result

⛔ **This is not an independent audit in Kosmos's sense, and the difference matters more than the
numbers.** Kosmos's 57.9% came from expert scientists outside the system. This was done by an agent
seat inside the repository that wrote the paper. It can catch a claim the committed artifacts
contradict; **it cannot catch a claim the artifacts and the prose are wrong about together**, and it
shares a model family with the author, which
[`method-watch-autonomy-prior-art-2.md` §5](../method-watch-autonomy-prior-art-2.md) already records
as a measured ceiling on blind seats (BadScientist). Read every rate above with that attached.

Further bounds, stated rather than buried:

- **n = 10 per stratum.** Every interval above is wide enough to contain both Kosmos's figure and
  ours.
- **One manuscript, one verifier, one seed.** A second seed draws a different ten; nothing here says
  the unsampled 60 interpretation sentences are fine.
- **The type assignment is a heuristic**, documented with its precedence and its two crude rules
  (a section-based rule for Methods, and an adoption-marker list drawn from this repository's house
  style). Every row carries its `signals`, so a reader can dispute a type per sentence.
- **One row is UNVERIFIABLE and stays that way**: `:104`, "no laboratory work was performed", is a
  claim about the absence of an event outside the repository. No committed record can settle it, and
  an absent reading is not a reading of absence.

## Findings that fall outside the three verdicts

Recorded here because they were found while verifying, and none is fixed by this seat.

- **`aso-control-oligos.json` contradicts itself in one field.** Its `⛔_not_a_claim_of_inertness`
  says a control "FAILS the specificity screen the reagent passes", while its `_what` says controls
  are "emitted only if it clears the ten-base-pair criterion" and the data show 6 bp and 7 bp
  against a cut of 10 — i.e. clearing. The manuscript sentence that rests on it (`:307`) is correct;
  the artifact's wording is not.
- **Two different sources for one range.** `aso-parent-gap-pairing.json` attributes the seven-to-ten
  hybridised-nucleotide range to PMID 35664704; the manuscript attributes "seven to ten the working
  range" to PMID 24981949. Neither is refuted here; they disagree about provenance.
- **The journal article has no PMID→title artifact of its own.** Its reference list renders straight
  to `fusion-junction-aso-journal-references.md`, and the only committed JSON keyed by its PMIDs,
  `journal-reference-authors.json`, holds authors and no title. PMID 39912803 — reference 13,
  the industry off-target recommendations — resolved to an **empty record** on the sampler's first
  run. `claim_audit.py` now names the record's source per row so the gap is visible instead of
  blank.
- **Two sampled sentences make quantitative claims about a source while carrying no citation
  marker**: `:269` (doubling times, the PMID sits on the previous sentence) and `:362` (paralogue
  redundancy, whose evidence is committed in `lit-targets-nr4a-redundancy.json` but uncited at the
  point of claim). Both verified SUPPORTED; both are invisible to `lint_citations` for the same
  reason.
- **`:217`'s "the liable count does not fall" is true as a count and false as a fraction** — 87 of
  190, 88 of 266, 87 of 342 is 45.8% → 33.1% → 25.4%. The sentence says count. Recorded because a
  reader may take the sentence for the stronger claim.
