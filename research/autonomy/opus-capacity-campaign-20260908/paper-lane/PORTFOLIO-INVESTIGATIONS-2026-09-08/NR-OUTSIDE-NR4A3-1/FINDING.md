---
id: DOC-LANE-NR-OUTSIDE-NR4A3-1-FINDING
title: "NR-OUTSIDE-NR4A3-1 — is the surviving evidence for PUB-NR-OUTSIDE-NR4A3 typed and attributed as its own prose says?"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
lane: NR-OUTSIDE-NR4A3-1
endpoint: PUB-NR-OUTSIDE-NR4A3
---

# NR-OUTSIDE-NR4A3-1 — finding

Endpoint `PUB-NR-OUTSIDE-NR4A3` has **no `document.file`**: `state: outlined`, `outcome_potential:
negative_or_methods`, `patient_path: none`. The prior campaign step
(`paper-lane/P6-PUB-NR-OUTSIDE-NR4A3-paper-step.md`) already graded both routes negative and drafted a
Results section. So the open question for this lane is not "is the paper right" and not a re-grading of
those routes. It is whether the **evidence the drafted negative actually leans on is what the prose says
it is** — because on this endpoint the negative *is* the product, and a negative built on a
mis-typed source is not a cheaper failure than a wrong positive.

## Question

**Is PMC9489176 — the record the drafted section leans on for the ~70%-EWSR1 denominator claim *and* for
this route's only positive EMC observation — the review its prose calls it; and does the reach
arithmetic that closes the partner route reproduce from its own underlying artifact?**

Concretely answerable, and answerable today on held data plus the admitted PubMed route.

## Merit

Patient relevance is indirect and honest: this endpoint's whole value is telling a small rare-sarcoma
field that **two nuclear-receptor routes around NR4A3 are closed, and why** — so that the next group does
not spend a cycle re-opening them. That is only worth publishing if the closure is airtight. The
partner route is closed on a **reach bound derived from zero events**, and the evidence that the
dominant partner imports nothing is a **retrieval negative**. Both are weak-form evidence whose whole
credibility rests on the sources being exactly the kind of source claimed. One mis-typed source is
therefore a paper-level defect here, not a copy-editing one. The contribution is non-trivial and the
evidence is attainable — it was attained below at zero marginal cost.

## Evidence gap this lane closed, and what it is distinct from

The prior P6 step verified route gradings against primary records and recomputed the Wilson bounds. It
did **not** check the *publication type* of the record it cites twice, and it emitted the prose that is
now a **live repository defect**: `lint_citation_types` fails at
`P6-PUB-NR-OUTSIDE-NR4A3-paper-step.md:172` with `TYPE CLAIM WITH NO CACHED METADATA — prose calls
PMCID PMC9489176 "a review"`. That defect belongs to this lane's target and to no other. It is distinct
from the twelve other type errors in the same run, which sit in W04b/W06/W09/W09e and are not mine.

## Step taken

1. Ran the live guard and isolated this endpoint's error (check 01).
2. Retrieved the metadata **verbatim** through the admitted route — `mcp__PubMed__convert_article_ids`
   (`id_type='pmcid'`) then `mcp__PubMed__get_article_metadata`. Nothing was typed from memory.
3. Re-derived all three Wilson bounds from scratch (check 02) and re-read the cohort counts from their
   owning artifact (check 03), then ran a denominator sensitivity (check 04).
4. Prepared **two UNAPPLIED diffs**, each proved with `git apply --check` (checks 05–07; the first
   attempt failed on a hunk count and is preserved).

### Result — the type claim is REFUTED

According to PubMed, PMID 36103645 / PMC9489176
([DOI](https://doi.org/10.1200/PO.22.00039)) — Wilbur HC et al., *JCO Precis Oncol* 2022;6:e2200039,
"Identification of Novel PGR-NR4A3 Fusion in Extraskeletal Myxoid Chondrosarcoma and Resultant Patient
Benefit From Tamoxifen Therapy." — carries `article_types`:

```
["Journal Article", "Research Support, N.I.H., Extramural"]
```

**No `Review`.** The prose is wrong, and it is wrong in a way that matters: the ~70%-EWSR1 background
figure and this route's **only** positive EMC observation come from the *same single primary report*.
Calling it a review presents one report's background sentence as synthesised literature — precisely the
misattribution class `research/manuscripts/citation-article-types.json` was created for on 2026-08-26.

⚠ **The ledger row alone does not clear the gate.** From `lint_citation_types.py:88-92` and `:293`,
`TYPE_RULES["review"] = ("Review", "Systematic Review")`, and the record's types intersect that set
emptily — so adding the row converts the error from *no cached metadata* to a *type disagreement* and
the exit code stays `1`. **Both diffs are required.** This is a reading of the guard's code, not an
executed demonstration; no attempt was made to run the guard against a modified tracked tree.

### Result — the reach arithmetic reproduces exactly

Recomputed independently at `z = 1.959963984540054`, `k = 0`:

| n | recomputed Wilson95 upper | committed | reproduces |
|---|---|---|---|
| 58 (Huang, PMID 36948401) | `0.062117855787202914` | `0.062117855787202914` | yes |
| 26 (Agaram, PMC4015728) | `0.1287289218592153` | `0.1287289218592153` | yes |
| 84 (pooled) | `0.04373172841465988` | `0.04373172841465988` | yes |

Digit for digit. The route's travelling number — hormone-responsive-partner fraction of EMC bounded
above at ~4.4% on 0 events in 84 genotyped cases — stands as computed.

### Secondary finding — a denominator that does not add up

`research/manuscripts/degrader/nr4a3-emc-biology-evidence.md` (Hypothesis 2, pillar 1) records Agaram as
**"26 cases: 16/7/1"**. **16 + 7 + 1 = 24, not 26.** Two of 26 are unaccounted for in the stated partner
breakdown. The Huang row is internally consistent (46 + 9 + 2 + 1 = 58). P6 repeated "26: 16 / 7 / 1"
without flagging the sum.

This does not flip the endpoint's negative — `k = 0` for PGR and GREB1 either way — but it moves the
bound. Counting only the 24 with a named partner call widens Agaram from `0.1287289218592153` to
`0.13797620467498017`, and the pooled bound from `0.04373172841465988` (n = 84) to `0.04475062369010032`
(n = 82). **Left OPEN**: whether those two cases carried another partner, were NR4A3-rearranged with no
partner call, or are a transcription slip here cannot be settled from held artifacts — the Agaram
primary table was not retrieved in this lane, and I did not retrieve it. Recorded, not corrected.

## Merit verdict for the endpoint

**GO, narrowly, and only as a negative-results and fusion-architecture note** — consistent with P6's
verdict, but conditioned on three things P6 did not state: the ~70% figure must be attributed to a
single primary report rather than to review literature; the pooled denominator must be reconciled or
carried with its 2-case gap; and the guard must be green on both diffs before anything is written up.
None of that is a new experiment. **No efficacy, safety, selectivity, therapeutic-window or
clinical-readiness claim follows from any of it, and none is made.**

## Artifact · validation · provenance · limitations · stop condition

**Artifact.** `pmc9489176-type-and-reach-rederivation.json` (parses, check 09), plus
`UNAPPLIED-01-citation-article-types-add-36103645.diff` and `UNAPPLIED-02-p6-prose-type-claim.diff`.

**Validation / baseline.** Baseline is the guard's own live output at HEAD (check 01, exit **1**, 13
type errors, 1 of them this endpoint's). Validation is threefold: the PubMed record is verbatim from the
admitted connector and independently re-resolved from PMCID to PMID; all three Wilson bounds reproduce
the committed values to the last printed digit; and both diffs return `git apply --check` exit **0**.

**Provenance.** PubMed (NCBI) via the PubMed MCP connector for the metadata. Everything else is the live
checkout at HEAD `9a0ee12226deef23fabc72011c64bab9fee18763`, with the four load-bearing files
re-hashed at use (check 08) — the shared checkout moved under me from `673d3304` to `9a0ee122` during
the lane, which is expected with concurrent writers and is why the hashes are recorded.

**Limitations.** The type verdict settles *what kind of paper PMC9489176 is*; it does **not** re-check
whether the ~70% figure is numerically right, and I did not retrieve the paper's full text. The
"ledger row alone is insufficient" claim is a code reading, not a demonstration. The 2-case Agaram gap
is reported unresolved — no primary retrieval was attempted, so it remains UNKNOWN, not zero and not
benign. The reach bound still rests on zero events under an **unverified** non-overlap assumption and on
cohorts genotyped by targeted assays the index case's own authors say would have missed their fusion;
none of that was re-litigated here. Nothing in this lane touches the dormancy route, whose `UNREAD`
grading I did not re-examine. `scripts/preflight.sh` was **not** run, per the contract, so the tree-wide
effect of these diffs is unmeasured.

**Stop condition (stated and MET).** Stop when (a) PMC9489176's `article_types` are retrieved verbatim
through the admitted route and the prose claim is graded against them, (b) the reach arithmetic is
independently recomputed against its committed values, and (c) every shared-file change exists as an
unapplied diff proved by `git apply --check`. All three met. No refusal was encountered; no closed route
was entered.

## Next credible independent work (not done here, not authorised here)

1. The parent applies both diffs together and re-runs `lint_citation_types` — the only thing that turns
   the code reading above into a measurement.
2. Retrieve the Agaram *Hum Pathol* 2014 partner table and reconcile 26 against 16/7/1, or restate the
   pooled denominator as 82 with the gap on its face.
3. The three record corrections P6 already named (`why_not_written` over-stating the dormancy limit as
   permanent; `what_it_would_claim`'s "tool compound"; folding in `hspa8-promoter-hormone-grade.json`)
   remain outstanding and are the record owner's, not this lane's.
