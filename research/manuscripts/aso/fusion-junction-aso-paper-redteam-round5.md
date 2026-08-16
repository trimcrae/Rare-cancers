---
id: DOC-FUSION-JUNCTION-ASO-REDTEAM-ROUND5
title: "Round-5 pre-deposit swarm review of the fusion-junction ASO submission — findings, adversarial verifications, and the two blockers that did not survive them"
level: L3
kind: manuscript
status: live
canonical_for:
  - the round-5 swarm review of the fusion-junction ASO submission manuscript
  - the round-5 wrong-leads record
purpose: >
  Hold the fifth adversarial review of fusion-junction-aso-research-article.md, run 2026-08-16 as
  nine independent reviewers with no sight of each other, followed by adversarial verification of
  the two findings that carried a reject recommendation. Its reason for existing is the same as
  rounds 2 and 3: a review whose findings are applied but not recorded gets re-run from scratch,
  and its wrong leads get re-raised. It exists separately from round 4 because round 4 was an
  editorial pass that explicitly re-derived nothing, and because the manuscript has since gained
  twenty-eight commits that no round has read.
scope: >
  Claims, arithmetic, citation support, deliverable executability and register consistency, against
  the committed tree at a4031c37905755f7618a5c04fc988278e5632520. No screen was re-run for the
  purpose of changing an artifact; where a reviewer recomputed, it was to test a claim, and the
  recomputation is reported rather than committed. "The wet-lab experiment was not done" is never a
  finding here, and neither is "delivery is unsolved".
audience: [external reviewers, maintainers, autonomous research agents]
related:
  - DOC-FUSION-JUNCTION-ASO-SUBMISSION
  - DOC-FUSION-JUNCTION-ASO-REDTEAM-ROUND4
  - DOC-FUSION-JUNCTION-ASO-PREPRINT-CHECKLIST
date: 2026-08-16
last_verified: 2026-08-16
---

# Round-5 pre-deposit swarm review of the fusion-junction ASO submission

> **Rounds 1–4** are [round 1](./fusion-junction-aso-paper-redteam.md),
> [round 2](./fusion-junction-aso-paper-redteam-round2.md),
> [round 3](./fusion-junction-aso-paper-redteam-round3.md) and
> [round 4](./fusion-junction-aso-paper-redteam-round4.md). Nothing here re-raises a finding from any
> of them. ⚠ **Every §-reference in rounds 1–3 predates the round-4 renumber, and the numbering has
> moved again since.** Findings below are anchored on verbatim quotes and line numbers at the pinned
> commit, never on section numbers.
>
> **Method.** Nine reviewers ran independently with no sight of one another — three journal-referee
> lenses, four wet-lab lenses on the premise that the paper's stated audience is a laboratory that
> would make these molecules, and two integrity lenses. Each was given a digest of what rounds 1–4
> closed, an evidence mandate (an artifact field, a code line, or a verbatim quote for every
> finding), and a ban on the word "probably". **The two findings that carried a reject
> recommendation were then sent to adversarial verifiers instructed to default to refuted.** Both
> failed to survive intact, which is why they are in the wrong-leads section rather than in the
> ledger.

---

## 1 · What this round found that four prior rounds could not

The prior rounds checked the claims against the artifacts, and the artifacts held up again here. **The
defects this round found are overwhelmingly registers disagreeing with each other** — a table built from
a field the repository documents as broken, a superlative the paper falsifies in its own text, a coverage
sentence describing denominators it does not use, and a prior round's ledger recording a fix that never
landed. The underlying screens keep coming out sound.

⚠ **One methodological consequence, and it binds the next round.** Round 4 records adding a nine-term
glossary to the Introduction. It is not in the manuscript — the commit never reached mainline. So
**"closed in a prior round" is not evidence the fix exists**, and any future round that relies on these
digests must spot-check the disposition against the tree.

---

## 2 · P0 — blocks the bioRxiv deposit

Each becomes permanent and citable the moment the deposit lands.

| # | finding | evidence |
|---|---|---|
| **P0.1** | **A named, orderable oligonucleotide for a partner gene the paper does not model.** Line 1130 hands a laboratory `5′-AGTGGGCTCTTCCATT-3′` at *PGR* exon 2. *PGR* occurs three times in 1,442 lines, zero times in the tables or references, and is absent from the Methods accession list — while the paper says "the five known partners" throughout (lines 52, 379, 438, 491). Line 1106's claim that the junction qualifies under a published-breakpoint rule carries no superscript. | `grep -n 'PGR'`; Methods lines 150–151 |
| **P0.2** | **A laundered citation.** Lines 128–130 attribute a partner-stratified denominator ("a *TAF15* arm of three to five patients") to two primary trial reports. Neither carries a fusion-partner breakdown; `emc-fusion-partner-pooling.json` records the cohort as `provenance: "secondary"` with a `primaryRef`. The two reviews the denominators come from — PMID 33799327 and 32967265 — are cited **zero** times. | pooling artifact; grep of the manuscript |
| **P0.3** | **The submission tables print locus counts from a parser the repository documents as broken.** `submission_tables.py` reads `n_loci_with_a_gap_spanning_hit` at lines 143, 336, 361 and 488. `aso_gap_length_tradeoff.py:270` declares that field wrong and asserts "nothing downstream reads it". Recounted with the fixed parser, 31 of 303 deep records differ, all inflated — *TCF12* e5 prints 17 against a corrected 1. **Table 2 therefore contradicts Table 4 and the prose on the same molecule.** | both source files; recount |
| **P0.4** | **A superlative the paper falsifies 58 lines later.** Lines 72 and 1168 call the lead reagent's 123 gap-paired near-matches "the heaviest disclosed transcriptome load of any design considered here". Line 1130 names a reagent at **128**; a panel design carries **240**; **14 deep records exceed 123**. | scan of all deep screens |
| **P0.5** | **"Every one of the five partners" is four at the depth the paper itself ran.** Line 841's conclusion holds only at default search depth. At the deeper ceiling *TFG* has **no** junction whose best design carries no sense-strand near-match — its one clean junction goes from 0 to 29. Table 2 already prints the contradiction. | recompute over the 38 `is_deep` screens |
| **P0.6** | **The abstract states no limitation of scope.** Lines 48–81 contain zero occurrences of computational, in silico, predicted, synthesised, tested, efficacy or safety, and close on reagents "named for synthesis". The sentence that would fix it exists only in YAML frontmatter, which `build_submission_pdf.py:104-107` strips from both PDFs. The body's guard is 940 lines below the abstract. For an ultra-rare cancer whose patients read preprints, the abstract is the artifact that travels alone. | grep; the builder |
| **P0.7** | **An argument with an absent editor, on page 1.** Lines 29–32 carry an article-type justification directly under the title. `build_submission_pdf.py:248` strips frontmatter only, so it reaches both rendered PDFs. The cover letter already makes the request. | the builder; cover letter line 54 |
| **P0.8** | **The abstract reports a load for a molecule it never names** ("the *EWSR1* exon-12 reagent named below"), 962 lines above the sequence — in the one artifact that always travels detached. | line 71 vs line 1033 |

**Already known, still author-only, correctly not re-raised:** `ORCID: [to be inserted]` and the two
`[ARCHIVE DOI]` placeholders (round 3). **And the deposit manifest is stale** —
`fusion-junction-aso-archive-manifest.json` records `git_revision 267f580`, **186 commits behind HEAD, 17
of them touching this directory**, with `git_tree_is_clean_apart_from_this_manifest: false`, and still
calls the paper a short communication. It is what the archive DOI would be minted against.

---

## 3 · P1 — wrong or unsupported, but not deposit-blocking

**Arithmetic and description**

- **A sign error in a load-bearing sentence.** Line 701: *"No design can therefore gain a nucleotide of
  gap-level margin without handing RNase-H1 one more nucleotide of contiguous wild-type-parent duplex."*
  Verified from the artifacts: parent-paired gap DNA distributes `{3nt:38, 4nt:76, 5nt:76}` against
  margins `{3:38, 2:76, 1:76}`, so margin + parent DNA = 6 = the gap, and
  `aso_gap_length_tradeoff.py:373` comments `parent_dna = gap - margin`. **Within a geometry the two move
  inversely** — gaining margin concedes *less*. True only across geometries. The Figure 2 legend repeats
  it and adds "no choice of register avoids it", when register choice is precisely what does.
- **"The same two denominators" is false.** Line 1099's 82.9% rests on a pooled 20-tumour *EWSR1* arm
  (`basis: pooled_two_series`, 17/20) where 68.4% uses 10/15, and the required §2.2 disclosure — 15 of
  20 from one series, with the two series disagreeing 0/15 against 1/5 at one junction — is absent.
  ⚠ **The numbers are right**: both figures re-derive exactly. The defect is the description.
- **The manuscript names the wrong parent at line 635.** An eleven-base-pair duplex is attributed to
  *NR4A3*; the artifact records it against **TCF12** (exhaustive recompute: TCF12 11, NR4A3 8, no tie).
- **59 of the 61 *NR4A3* liabilities are the same site** — the mature exon-2/exon-3 seam. The paper makes
  exactly this disclosure for the analogous pre-mRNA class and withholds it here.
- **Two defects in §3.8 that overstate the favourable side**, surfaced by a verifier rather than a
  reviewer: line 727–728 compares 181/190 against 87/342 across a silent criterion change the artifact's
  own `_threshold_note` warns about, and line 729's pre-mRNA arm is a search inheriting the instrument
  bound, presented immediately after the text says parent-side quantities carry no such qualification.

**The deliverable**

- **The decisive readout has no assay.** Zero occurrences of primer, amplicon, qPCR, RT-PCR, TaqMan,
  normaliser, reference gene, transfect, gymnotic or replicate in 1,442 lines. Because the fusion carries
  *NR4A3* exons 3–8, an assay not deliberately placed relative to the acceptor measures numerator and
  denominator together. ⚠ **Three reviewers reached this independently.** They **disagree on the fix** —
  5′ of the acceptor (avoids the fusion) versus exon2–exon3-spanning (avoids reading the 5′ cleavage
  fragment, which under-reads knockdown and *inflates* selectivity). Both are defensible and they bias in
  opposite directions; the paper specifies neither. **This is an author decision, not a reviewer one.**
- **The threshold cannot be pre-registered.** "Replicate", "sample size", "effect size" and
  "pre-registration" appear nowhere; "power" once, unrelated. An "approximately five-fold" cut with no n
  and no rule for what is compared to it cannot fail honestly. Near the quantification floor a
  denominator of "no detectable change" returns infinite selectivity, which **passes** the test.
- **The threshold has no literature warrant for the case it is applied to.** Line 137 calls it *"the
  measured threshold"*; line 856 says *"no retrieved measurement bounds the parent case"*. Round 2 fixed
  this in the Discussion and round 4 then created §5 by splitting §4 **without carrying the fix into it**.
  ⚠ This is an R5 violation surviving in the submission text — see §5.
- **No control isolates RNase-H1-dependent cleavage**, though the ranking statistic is entirely a model of
  cleavage and line 953 names steric block as unevaluated.
- **The named reagents carry no contrast in the variable being falsified** — all four hold margin 3, and
  the only other margin in the set is confounded with geometry.
- **§5.2 is contradicted by its own artifact.** It says the 5-8-5 "does not buy parental sparing"; the
  artifact records `mature_parent_duplex_through_whole_gap_bp` 8 → 0 at that seam. ⚠ **But see §5** — a
  verifier established that 8 is below the paper's own threshold, so this needs re-reading before it is
  applied.
- **Routine EMC diagnosis cannot supply what §5.4 requires.** *NR4A3* break-apart FISH resolves neither
  partner nor exon; the paper's own 58-case denominator had RNA exome sequencing on **three** cases.
- **The paper describes that assay backwards** at lines 462 and 1257 — a break-apart probe reports that
  one gene is split, not which genes are joined. The error runs *against* the paper's own argument.

**Citation support** — audited across all 49 references, 59 citation points, 65 pairs

- The gap-length figures are cited to a 2005 review that credits them to named primaries; the 7-to-10
  hybrid-length figure is a conjectural explanation (*"This could be because"*) rendered as *"reported as
  the minimum"* — and **that threshold sets the abstract's headline 87-of-190**.
- The Methods drop **"RNA:DNA"** from that quote, which is the qualifier deciding whether LNA wing pairs
  may be counted. At a 5-6-5 every counted run has exactly 6 RNA:DNA nucleotides, so the threshold tests
  hybrid-binding-domain engagement, not the catalytic DNA minimum.
- *"No agent is approved specifically for EMC"* cites a review containing **one** occurrence of "approv",
  inside "Ethical approval", which instead recommends pazopanib.
- *"is required"* where the source shows sufficiency; *"demonstrated in at least four fusions"* where two
  report a parental readout; *"First-line"* unsupported by its source's own stratification.
- **The chimera share is threshold-fragile.** "About half generic, about half specific" is true at
  **exactly one** threshold; across the paper's own cited [7,10] window the split runs 52/48 → **94/6**.

**Language discipline**

- **Three uncited claims about what other groups routinely do**, and `lint_claims` R6 catches none of
  them: *"normally confirmed in cells after synthesis"* (line 54), its Discussion twin (line 864), and
  the 5-methylcytosine practice claim (line 758). ⚠ The safeguard added by the retraction commit
  `267f58098` was **deleted ten minutes later** by `6d43d7aa5`, leaving the positive-direction half of
  the claim with no scope-out anywhere.
- Line 986 makes an unbounded universal negative where the source artifact declares itself INCOMPLETE and
  forbids that use. (A reviewer then read the deferred corpus and found it **supports** the claim — so the
  defect is the missing bound, not the substance.)
- The reproducibility declaration says every quantitative statement is code-produced; the clinical
  statistics are transcribed from publications.

---

## 4 · P2 — wording, framing and register

Primary results reported outside Results (the un-rearranged-allele analysis and its three condemned
sequences appear only in the Discussion; the exon-2 acceptor panel and coverage ladder only in §5, which
at 2,653 words is larger than the Discussion) · the cover letter names a different title from the
manuscript · the submission plan's "fits Article comfortably" is false against the only caps read at
primary source, and the checklist is typed against superseded counts · the title is 190 characters and
contains neither "antisense" nor "oligonucleotide" · the abstract's deliverable sentence is three passives
with no count or sequence, landing after 121 consecutive words of liability · round 4's nine-term glossary
is absent · "the upper cut" is used seven times and defined nowhere in the manuscript · "second most
frequent transcript" should be "second most frequent *EWSR1* transcript" · a Table 6 count pooled over two
registers quoted for a reagent carrying fewer · `chimera` split at the complementary offset in code
(measurably harmless — the pooled ensemble is the exact mirror — but the prose describes what did not run).

---

## 5 · ⛔ WRONG LEADS — recorded so round 6 does not re-raise them

**Both findings that carried a reject recommendation failed adversarial verification.** They were
confident, quantitatively precise, and wrong — which is the third such instance in this paper's review
history and the reason refute-by-default is in the method.

### 5.1 · "A longer catalytic gap does separate them, so the title is false" — **REFUTED**

- **The comparison was not like-for-like.** The reviewer took `n_with_any_gap_pairing_window` at 5-6-5
  and `n_at_or_above_min_duplex_bp` at 5-10-5. The first requires pairing the *whole gap* — 6 bp at
  5-6-5, 10 bp at 5-10-5 — while the second is an absolute 10. `aso-gap-length-tradeoff.json` carries a
  `_threshold_note` warning of exactly this convergence, in every geometry block.
- **At the paper's own criterion the absolute liability is flat: 87 → 88 → 87.** Liable against wild-type
  *NR4A3*: **61 → 61 → 61**. Junctions carrying a liable design: **36 → 36 → 36, 100% set overlap.**
- **The median parent duplex grows 11 → 13 → 15 bp** — a *more* competent RNase-H1 substrate.
- **The lead junction's 8 → 0 crosses no threshold**: 8 is below `MIN_DUPLEX_BP = 10`, so that design was
  never counted as a mature-parent liability. Meanwhile its own-seam hybrid rises *through* 10 bp and its
  parent-paired gap DNA reaches 5 nt — the reported RNase-H1 minimum. **That is what the title asserts.**
- "The measurements appear once in §3.8" is false — they appear five times across four sections,
  including the Discussion and the Figure 2 caption, and the paper acts on them by naming a 5-8-5 reagent.

### 5.2 · "The null's excess collapses across the threshold, so 10 was chosen to maximise it" — **PARTIALLY SURVIVES, blocker withdrawn**

- **The numbers reproduce exactly** — all four rows to four decimals, two independent ways.
- **But 10 does not maximise the effect, and the reviewer's table stopped at the value it accused the
  authors of picking.** Over the artifact's declared 6–12 range the ratio is **24.35 at threshold 11 and
  45.45 at 12**, against 7.41 at 10. Choosing 10 forgoes a factor of 3.3 and 6.1. It is maximal only
  inside [7,10], a window bounded above by the *citation*.
- **The charge is a theorem, not a tell.** Observed count falls monotonically with threshold while
  obs/null rises, for all seven arms at all seven thresholds — so "minimises the count" and "maximises the
  ratio" are necessarily the same threshold whenever the screen works at all. **No dataset with a real
  effect could fail this charge.**
- **Direction is robust across the whole cited range** under junction-clustered CIs (38 clusters).
- **What survives is disclosure only**, and it is filed in §3: no null exists at threshold 7, the
  artifact carries no threshold-sensitivity field, and the chimera-share claim is fragile.

### 5.3 · Attacks tried and abandoned by the hostile reviewer, recorded with its reasons

The central negative is not an unlabelled identity — the paper labels every identity as one, unprompted,
including in the Figure 2 legend. 45.8% is not inflated by the shared acceptor — the chimera arm was built
to kill exactly that hypothesis and randomises the *NR4A3* window too. §3.8 does not hide the improving
ΔΔG. Novelty is conceded verbatim at line 122. The cell-line objection is the brief's excluded class and
is stated fully at lines 972–987.

---

## 6 · What this review did not do

- **No screen was re-run to change an artifact.** Where a reviewer recomputed — the null across
  thresholds, the locus recount, the per-parent duplex scan — it was to test a claim, and the result is
  reported here rather than committed.
- **No number in the manuscript was edited.** This file is the ledger; application is a separate pass
  behind the human decision gate, because the deposit is outward-facing.
- **The literature was audited for support, not re-fetched wholesale.** 31 references lacking a committed
  abstract were retrieved from Europe PMC in one CI dispatch at $0; 14 carry full text. Three of 65
  citation pairs could not be assessed and are named as such.
- **Round 4's editorial axis was not re-run**, except where the 08-15/08-16 commits introduced new prose.
