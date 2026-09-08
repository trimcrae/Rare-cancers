---
id: DOC-OPUS-CAMPAIGN-ESCALATIONS-BIOMORT
title: "Three escalations from the mortality and biomarker promotion lane"
level: L4
kind: memo
status: live
purpose: >
  Record three findings that a promotion lane surfaced, verified enough to be actionable, and
  correctly declined to resolve, so they are not lost between owners.
scope: >
  L4. Findings and evidence only. Nothing here is applied, and none of it is a re-review of settled
  science.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Three escalations, none resolved here

A promotion lane over `emc-mortality-mechanisms-paper.md` and
`dependency/emc-biomarker-selected-classes.md` delivered its reader-facing candidates and stopped at
three things it judged to be owner decisions rather than readability edits. It was right to stop.
All three are recorded with the evidence, and none is acted on.

## 1 · The memo's 388-paper corpus has no artifact basis

`research/manuscripts/emc-mortality-mechanisms.md` §3 twice describes "the same **388**-paper
retrieved corpus". `research/literature/emc-mortality-probe.json` records
`oa_corpus_enumerated 600`, `fulltext_attempted 400`, `fulltext_retrieved 328`,
`papers_with_death_sentences 162`. There is no 388.

⚠ **A correction to how this was first reported.** A grep for `388` in the probe artifact does return
hits, so "388 appears nowhere" is too strong. Every hit is inside an identifier — PMIDs `38388202`,
`38849448`, `38899283`, DOIs `10.4317/jced.53888`, `10.3171/case24388`, `10.21873/cgp.20388`, and an
NCT number inside a title. **None is a corpus count.** The finding stands; the phrasing needed
tightening.

The same discrepancy has a second face: the identical null search is described against two different
denominators. The paper says "a title-level search of **the 25 records retrieved from this class of
intervention**", matching `early_palliative_care_survival.retrieved: 25`. The memo says "a
title-level search of the same **388-paper retrieved corpus**". Those are not reconcilable as
written, and the paper's is the artifact-backed one.

⛔ The memo is a separate document with its own id (`DOC-EMC-MORTALITY-MECHANISMS`) and was outside
the lane's write scope. It is untouched.

## 2 · Whether the mortality paper's 52 is 51 deaths

`emc-terminal-events-classified.json` holds 18 rows summing to **52**, and the paper's §3.1 says
"Fifty-two deaths were described". One row — PMID 23213584, `visceral_metastasis_complication`,
n = 1 — carries its own note: *"⚠ Not a death sentence. … Counted in the mechanism table only as a
complication, never as a death."*

Verified independently: 18 rows, summed n = 52, exactly one row carrying that note.

So on the artifact's own reading the count of **deaths** is 51 and 52 is the **mechanism-table**
total. If that is right, 15/52 = 28.8 % becomes 15/51 = 29.4 %, and several downstream sentences
move with it.

⛔ **Not changed.** 52 is a headline denominator that has already been through a correction pass, and
deciding whether the paper's sentence or the artifact's note is the one to move is a science
decision, not a readability edit. It is recorded here rather than quietly adjusted or quietly
dropped.

## 3 · Whether the biomarker paper is converted to journal register

`dependency/emc-biomarker-selected-classes.md` is `kind: manuscript` with a submission-shaped title,
but it is written in the loud repository register: 27 ⛔/⚠/⭐ markers, bold at 19.2 per 1000 against a
limit of 12.0, em-dashes at 11.5 against 6.0, sentence headings. It has no author or correspondence
block, no venue note and no data-and-code-availability statement.

⛔ **Deliberately not converted.** Nearly every one of those 27 markers sits on a load-bearing hedge,
refusal or closure — the ⛔ "no EMC line in the dependency panel", the ⚠ "the MKI67 control fails on
GPL3290", the ⛔ "the half that selects the class is not present", the ⚠ "an absent reading is not a
reading of absence". Converting the register means rewriting the sentence carrying each one, which is
the class of change a promotion lane must not make unilaterally. Adding an authorship block is an
authorship act and belongs to the owner.

This is a scoped decision with its measurement attached, not a defect found and abandoned.
