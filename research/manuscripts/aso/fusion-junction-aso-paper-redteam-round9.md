---
id: DOC-FUSION-JUNCTION-ASO-PAPER-REDTEAM-ROUND9
title: "Round-9 blind review of the fusion-junction ASO journal article — three real defects, four holes in the gates, and the severity mis-grade that turned five suggestions into blockers"
level: L3
kind: manuscript
status: live
canonical_for:
  - round 9 blind adversarial review of the ASO journal article, and the severity grading over it
purpose: >
  Round 9 hardening of PUB-ASO, run against the PUBLIC v1 rather than against a draft. Five blind
  seats reviewed the pinned commit. This document records what they returned, which findings are
  real defects, and — the part worth reading — why the first pass over them was wrong about severity
  and what that cost.
scope: >
  Computational design and specificity screening only. No wet-lab experiment was performed, and
  nothing here asserts efficacy, potency, safety, a therapeutic window, delivery to a tumour, or
  clinical readiness for any sequence. Every sequence named is a research reagent for laboratory
  investigation only and must not be administered to any person or animal.
audience: [external reviewers, collaborators, maintainers]
date: 2026-08-27
last_verified: 2026-08-27
---

# Round 9 — blind adversarial review of the ASO journal article

**Subject.** `research/manuscripts/aso/fusion-junction-aso-journal-article.md` at pin
`29f4e5e2db381f09c72c934e1f1072976e9d4d24`, blob sha256 `d88abe84f7ed9419…`, 4,614 words. All five
seats verified the digest independently.

**⛔ WHAT MAKES THIS ROUND DIFFERENT.** Rounds 2–8 hardened a draft. This one reviews a manuscript
that is already public: Qeios `VL3LJR`, DOI `10.32388/VL3LJR`, posted 2026-08-27 by trimcrae on his
own ORCID. A confirmed defect here is a defect in a public record, and the only channel that repairs
it is a new version — **which is his act.** PUB-ASO is named in `publication-authority.json` as
excluded from the aiXiv grant for `submit` and `new_version` alike. The loop prepares; it posts
nothing.

**Seats.** Five blind lenses, dispatched as parallel subagents at `subagent_width` 5: regression
against the readability revision; arithmetic re-derived from the committed artifacts; statistics,
inference and experimental design; citations at primary source and instrument coverage; hostile
referee. No seat saw another's output.

---

## ⛔⛔ THE PROCESS FINDING, WHICH MATTERS MORE THAN THE PAPER FINDINGS

**The first pass over these seats graded EIGHT findings as blockers. Three are.**

trimcrae, 2026-08-27, on being shown the count: *"If it's coming back as having 10 blockers, I think
that's a good sign that we have to reevaluate what we're calling a blocker. Not that it's impossible
to actually have 10 but that strikes me as agents making things up to fill a quota more than real
issues if there's that many at this point."*

★ **THE MECHANISM, NAMED PRECISELY, BECAUSE "BE MORE SCEPTICAL" IS NOT A FIX.** `paper-hardening` §5
says REFUTE BY DEFAULT and requires every finding to name the artifact path and field that confirms
it. That was done — and it verified the **wrong proposition**. For each finding the check performed
was *does the text actually say this?* Every one passed, because the seats were quoting accurately.
The question never asked was *is this a reason to stop the paper?* **Existence was verified;
severity was inherited from the seat's own label.**

⚠ **A seat is instructed to grade its own findings, so its labels are not evidence — they are the
thing under review.** Five seats each returning "BLOCKERS:" as a section heading will produce
blockers, and a synthesis that treats those headings as data has outsourced the judgment that is
the synthesis's entire job.

⛔ **AND THE COST WAS MEASURED, NOT HYPOTHETICAL.** Applying all eight took the paper from 4,614 to
5,563 words and from six typeset pages to eight, against a **hard 6-page budget that exists because
*Nucleic Acid Therapeutics* levies a per-page charge**. Roughly an hour then went into cutting real
content to make room — cited case reports on the exon-2 acceptor, the coverage arithmetic and its
non-interval range, a paragraph of the Introduction — all of it to fit additions that mostly should
not have been made. ★ **The over-grade did not merely waste effort: it was actively deleting good
content to fund bad content, and every individual cut looked defensible in isolation.**

★★ **THE TEST TO APPLY AT THE NEXT ROUND'S SYNTHESIS, BEFORE ANY PROSE IS TOUCHED:** for each
finding, *would a reviewer stop this paper for it, or would they suggest it?* A wrong fact, a claim
the paper's own text contradicts, and an internal contradiction stop a paper. A completeness wish, a
"you should also measure X", and a caveat the body already carries elsewhere are suggestions. **Grade
severity from the paper's own standard, not from the seat's heading.**

---

## The three real defects, applied

**D1 · A universal claim that is false on its own artifact.**
Found by the arithmetic seat alone, and only because that seat re-derived a count instead of reading
a sentence.

> "On all four annotated *NR4A3* transcripts, the three with a RefSeq accession included, exon 3 is
> the first coding exon and exon 2 is non-coding…"

`nr4a3-acceptor-exon-numbering.json` records `n_transcripts` = 4 and
`first_coding_exon_ranks_observed` = `[1, 3]`. Three transcripts have their first coding exon at rank
3 — exactly the three carrying a RefSeq accession. The fourth, `ENST00000330847`, has
`n_noncoding_5prime_exons` = 0 and `first_coding_transcript_exon_rank` = 1, so on that transcript
exon 2 **is** coding. ★ The conclusion survives on a different field
(`a_transcript_numbering_exists_where_exon_2_is_the_first_coding_exon` = `false`), so the premise was
wrong and the inference was not. **Replaced with the property the artifact actually states**, which
is both true and shorter. Nothing in the suite matched this sentence and no `pinned-figures.json`
entry covered it.

**D2 · The one place the paper claims activity.**
Found independently by three seats.

> "An unscreened scramble therefore carries a one-in-ten chance of being a second **active molecule**
> offered as a negative control."

The 10.0% is `aso-parent-null.json` → `null_ensembles.scrambled_dinucleotide.rate_liable` = 0.09987:
a rate of *predicted pairing*. "Active molecule" is a cellular property, and the manuscript denies
twice that it measures one — "Both loads are predictions from sequence search rather than measured
activity" and "All five screens address hybridisation rather than cleavage, and none establishes that
a predicted duplex forms or is cut." **In a paper whose whole credibility rests on never claiming
activity, this was the single sentence that did.** Replaced with the predicted-liability statement,
at the same length.

**D3 · Three controls promised, two named.**
The Discussion said "three controls a knockdown assay alone cannot distinguish, two of them the
screened scrambles above"; § Controls says "Two controls are named as sequences (Table 2)"; no third
appears anywhere. An internal contradiction any reviewer catches. **Corrected to two**, at the same
length.

### Also applied, because each is cheap and unambiguous

- **The abstract's unqualified negative-literature claim.** "none is reported for any *NR4A3* fusion"
  — the Introduction says "in the literature retrieved here" and the Discussion disclaims
  exhaustiveness outright. Five words restore the scope the body insists on.
- **A rate with no denominator.** The null ensembles are 38,000 draws each with Wilson intervals, in
  `aso-parent-null.json`; the paper quoted 40.6% with neither. One sentence.
- **An uncited quantitative literature claim.** The six-nucleotide gap requirement had no superscript
  though the Methods attribute it and the source is held (PMID 24981949). Marker added, no words.
- **Reference numbering.** First-citation order ran `1–11, 22, 19, 20, 21, 12, 13, 23, 16, 14, 15,
  17, 18` against a banner in the reference file reading "⛔ NUMBERED BY ORDER OF FIRST CITATION,
  CONTIGUOUSLY". Renumbered to 1–23 in order, with a PMID-preserving post-condition checked in both
  directions. Costs no words.

## Recorded, not applied

Five findings the first pass called blockers and this one calls suggestions. They are kept because a
later round will find them again and should not re-litigate them from scratch.

| Finding | Why it is not a defect |
|---|---|
| The experiment names no readout, delivery route, dose or timepoint | This is a design paper. It supplies reagents and a decision rule; the assay is the laboratory's. |
| Only a falsification criterion is pre-stated, no success criterion | It is a falsification test by construction, and says so. |
| The isogenic arm has no test article at an endogenous locus | The paper already states plainly that neither cell model matches the panel's acceptor. |
| The selectivity ratio is on *NR4A3* while both reagents' largest predicted liability is *TFG* | Both facts are already in the text, two sentences apart. "Also measure *TFG*" is a good suggestion for a reviewer to make. |
| The abstract does not repeat that neither reagent clears every screen | The body says it. An abstract is not obliged to carry every caveat. |

⚠ **The hostile referee's SI blocker is REFUTED outright.** It reported that the supplied
Supplementary Information belongs to a different manuscript with colliding reference numbers. **No SI
is supplied with this paper**: `grep -i supplementary` over the journal article returns zero hits,
and `publications.json` → `PUB-ASO.posted` records the journal article alone going to Qeios. The SI
in that directory belongs to `fusion-junction-aso-research-article.md` and says so in its own line
46. The seat found a real file in a shared directory and inferred a bundle that does not exist.

---

## Guard defects — the round's most valuable output

⛔ **These are holes in this repository's own gates, not in the paper.** They came from the citations
seat, which asked a question no other lens asks: *what reads this sentence?* All four are fixed and
mutation-tested.

**G1 · The paper's central negative was guarded in one document of two.**
`test_the_printed_cut_ladder_is_the_measured_one.py` derives `flips == 4` from the artifact — that
half always bound — then asserts the prose against `PAPER`, which is the **extended report**. The
journal article carries the same sentence and nothing read it. Verified by mutation: the sentence was
inverted in the journal article, every gate in the repository stayed green. Both documents are now
asserted by iterating a tuple, because a copied second assertion is how the pair separates again.

**G2 · The delivery limitation was read by nothing.**
`grep -rn "remains unsolved\|delivery to a solid" --include=*.py` returned zero hits.
`test_the_paper_states_what_its_own_claims_depend_on.py` exists precisely because "absence fires no
other guard", and its `REQUIRED` list had ten rows and no delivery row — while its own margin note
already named delivery among the denials `lint_claims` does not cover. ★ **The worst class of
absence: every number in the paper stays correct without it.**

**G3 · The research-use denial was satisfied by a different sentence.**
The row for "nothing was synthesised or tested" alternated on `…|not for administration`, and the
Abstract already carries that phrase — so deleting the Declarations sentence outright left the guard
green. Verified by mutation on the delivered PDF's text layer: the old alternation missed the
deletion, the tightened one catches it.

**G4 · The reference-ordering invariant was asserted in a banner and checked by nothing**, and the
guard's own docstring still described the retired regime it contradicted. Now checked, and
mutation-verified by transposing two citation labels.

---

## Convergence

⛔ **Not converged, and honestly so.** Three real defects were found in a public paper, which is not
a converged state. But the round did not find eight blockers, and a round-10 synthesis that produces
eight again should be read as evidence about the synthesis before it is read as evidence about the
paper.

**Round 10 should re-seat on the corrected text** and apply the severity test above at synthesis,
before any prose is touched.
