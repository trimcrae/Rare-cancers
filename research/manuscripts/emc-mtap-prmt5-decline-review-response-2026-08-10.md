---
id: DOC-EMC-MTAP-PRMT5-DECLINE-RESPONSE
title: "Response to four grounds-to-decline reviews (emc-mtap-prmt5-hypothesis.md)"
level: L3
kind: manuscript
status: live
canonical_for: ["the author's response to the 2026-08-10 round-two adversarial reviews of the EMC PRMT5/MTAP manuscript"]
purpose: Answer every ground raised by the four round-two adversarial reviews, stating what changed and where, or why the ground is declined.
scope: Response to reviews of one manuscript. Reports one new analysis, computed from data already committed. Asserts nothing about efficacy, safety or clinical readiness for any agent.
audience: [maintainers, external reviewers]
date: 2026-08-10
last_verified: 2026-08-10
---

# Response to four grounds-to-decline reviews

> **THESE ARE SIMULATED INTERNAL REVIEWS, WRITTEN BY AI REVIEWERS AT THE AUTHOR'S REQUEST. THEY ARE
> NOT CORRESPONDENCE FROM *GENES, CHROMOSOMES AND CANCER* OR FROM ANY OTHER JOURNAL, NOT REAL PEER
> REVIEW, AND NOT A DECISION. No editor, no journal and no external referee has seen this
> manuscript. This document is the author's response to them, and it is an internal record.**

The four reviews are
[editorial](./emc-mtap-prmt5-decline-review-editor-2026-08-10.md) (desk reject; 10 fixable, 3
structural), [statistical](./emc-mtap-prmt5-decline-review-statistics-2026-08-10.md) (decline; 12
fixable, 3 structural), [biological](./emc-mtap-prmt5-decline-review-biology-2026-08-10.md)
(decline; 14 fixable, 4 structural) and
[integrity](./emc-mtap-prmt5-decline-review-integrity-2026-08-10.md) (minor revision; 147 numbers
traced, 139 exact). Round one is
[`emc-mtap-prmt5-hypothesis-peer-review-2026-08-10.md`](./emc-mtap-prmt5-hypothesis-peer-review-2026-08-10.md)
and its response is
[`emc-mtap-prmt5-hypothesis-review-response-2026-08-10.md`](./emc-mtap-prmt5-hypothesis-review-response-2026-08-10.md).

**Files changed:** `emc-mtap-prmt5-hypothesis.md`, `emc-mtap-prmt5-hypothesis-SI.md`,
`emc-mtap-prmt5-hypothesis-cover-letter.md`, `emc-mtap-prmt5-prepost.md`, all five figures and their
provenance stamp, `emc_mtap_prmt5_figures.py`, `pinned-figures.json`, `systems/graph/publications.json`,
`systems/graph/routes.json` and their generated views. **New:**
`emc_mtap_locus_persample.py` → `emc-mtap-locus-persample.json`, `emc_prmt5_effect_sizes.py` →
`emc-prmt5-effect-sizes.json`, `prmt5-ewing-expression-panel-composition-2026-08-10.json`,
`mtap-prmt5-discovery-and-chronos-2026-08-10.json`.

**Counts. 69 grounds worked through: 67 produced a change, 2 are pure pointers to the structural
list, and 6 further items are declined in whole or in part with the reason given (§4). Eight grounds
are structural and are recorded as unfixable rather than argued away (§11).** All six declines are
partial: each refuses one specific remedy inside a ground that is otherwise applied, and every
parent ground appears among the 67. Where two reviewers conflict, the decision and its reasoning are
stated at the item and in §8.

---

## 1 · The central judgement, accepted in full

Three reviewers independently concluded that the paper claimed a survival its evidence does not
support, and they are right. After the correction the paper itself elected to apply, nothing bearing
on the fusion rationale clears 0.05; the only reading that does is an instrument control. The
manuscript nonetheless carried "a fusion-class rationale that survives" in its title, "survives as a
hypothesis" in its Discussion and Conclusion, and the elevated reading in its abstract.

The title, the abstract, sections 1, 3, 4.1 and 5, the cover letter and the pre-posting checklist
have all been rewritten, and the claim structure has changed rather than the adjectives. The new
title is **"PRMT5 and the MTAP locus in extraskeletal myxoid chondrosarcoma: two rationales tested
against the available public data, neither supported"**. The old title is registered in Appendix A
and in `pinned-figures.json`.

What the paper now reports is what it establishes: a bounded negative on the *MTAP* locus argued
tumour by tumour, a fusion-class rationale this data cannot test, one durable sequence observation,
one sequence claim withdrawn against itself, and two named inexpensive experiments.

---

## 2 · The free analysis that was run before the closure was rewritten

The biology review's ground 4 is the most consequential item in the four reviews and it is accepted
in full. The *MTAP* closure rested on a difference of group means and a family-wise adjusted *p*,
and both are mis-specified for a subset event: homozygous 9p21 deletion is present in some tumours
and absent in others. The review further observed that the committed per-sample data holds a
candidate subset which the manuscript never reported, and that the check which would discriminate a
deletion from a low transcript had never been run.

It has now been run, from the committed per-sample data, with an artifact and a `--check`:
`research/modalities/emc_mtap_locus_persample.py` → `emc-mtap-locus-persample.json`. What it returns:

- **The candidate subset is real and is larger than the review reported.** On GPL3290, **five** of
  ten EMC tumours read below every comparator for *MTAP* on both the within-array *z* and the array
  percentile, at percentiles 1.1, 4.0, 4.6, 5.5 and 10.4 against a lowest comparator of 11.0. The
  review named four; the fifth sits at 10.4 against 11.0 and qualifies on both criteria.
- **The discriminating check comes back for the authors.** *MTAP* loss implies *CDKN2A* loss, so a
  9p21-deleted tumour must read low for both. Not one of the five does. All five carry *CDKN2A*
  between the 50th and 89th percentiles of their own arrays, at or above the array median in every
  case, and the tumour with the lowest *MTAP* reading in the series carries the highest *CDKN2A* in
  the arm. **Zero tumours are deletion-consistent** at a *CDKN2A* cut of the 5th, 10th, 25th or 50th
  percentile.
- **Two further 9p21 genes agree.** *MIR31HG* reads between the 29th and 56th percentiles in those
  five samples and *MLLT3* between the 63rd and 91st, neither at floor.
- **Both alternative explanations for the tail fail.** The five are not globally dim arrays (3.8% to
  7.6% of their cached genes below the 5th percentile, inside a cohort range of 1.4% to 8.9%), and
  all ten EMC tumours share one reference label, so a split within the EMC arm cannot come from the
  two-colour denominator.
- **The within-arm rank association runs the wrong way for co-deletion**, at Spearman *rho* = −0.31
  with an exact two-sided *p* of 0.39 over all 3,628,800 rank permutations. It is reported with its
  *p* and is not over-read.
- **On GPL6244 no EMC tumour is an *MTAP* low outlier at all**, every one lying between the 67th and
  82nd percentiles of its own array.

**What this did to the closure.** It strengthened it and moved it onto the right instrument, and it
also stopped the paper claiming more than a bound. Zero deletion-consistent tumours in sixteen gives
a one-sided 95% binomial upper bound of **17%** on the frequency of such a tumour, against a class
prior in which sarcoma MTAP protein loss reaches 20%. So "closed at transcript level" is withdrawn
and replaced by "not supported, and bounded at 17%", with the question left where it belongs, to a
stain. The argument now rests on the failure of the pre-specified conjunction and on a per-sample
cross-check, rather than on an adjusted *p* of 1.00 that could never have carried it (§5 below).

The result is reported in §3.2 of the manuscript, in SI §S3a, and in the rebuilt Figure 2, whose
right panel is the only place a reader can see it.

---

## 3 · Grounds applied, one entry each

Numbered by review. E = editorial, S = statistical, B = biological, G = integrity.

### E · Editorial and fit

1. **E1, insufficient advance — STRUCTURAL, recorded.** See §11.
2. **E2, article type chosen to fit the figure count.** Applied in part. The recorded reason is
   corrected in the checklist: content selects the type, and the display-item count the old reason
   rested on was wrong in the permissive direction (five figures and eight tables, thirteen items,
   not five). The choice itself is left to the author, because article type travels with venue and
   the brief reserves venue to the author. **Declined in part:** see §10 for why Figure 2 was
   rebuilt rather than deleted and Figure 3 improved rather than demoted.
3. **E3, concurrent overlapping submissions — STRUCTURAL, and the disclosure is made.** See §11 and
   E15 below.
4. **E4, the title names a unit the Results disqualify and the paper leads with the wrong clause.**
   Applied. The title now names *PRMT5* and the *MTAP* locus rather than the methylosome, and the
   negative leads in the title, the abstract, §4.1, §5 and the cover letter.
5. **E5, §4.4 contradicts §4.1 about the replication.** Applied. "What survives correction is the
   replication" is deleted and registered. §4.1 now claims only directional concordance between two
   deposits, states that independence is not established, that GSE24369 carries no linked
   publication and is a study of a different disease, and that patient overlap could not be checked.
6. **E6, unresolvable data availability and an originality claim resting on internal documents.**
   Applied as far as an author can without an outward-facing act. §2.7 and §8 now name the public
   repository, `github.com/trimcrae/Rare-cancers`, and state that an archived release of the state
   the manuscript is built on will be deposited at submission. The census, the 591-text corpus and
   the 322-record screen are relabelled as the author's own unpublished supporting analyses,
   deposited with the manuscript rather than cited as literature. §1.3 now says that neither screen
   is a full-text disease-to-target search.
7. **E7, repository apparatus inside the submission text.** Applied. Both `CLAUDE.md` citations are
   deleted, Appendix A no longer names the pre-posting checklist as a place a claim lives, and both
   the frontmatter and the appendices are marked in the frontmatter and in the appendix preambles as
   repository record removed at submission.
8. **E8, figures.** Applied. See §10.
9. **E9, the abstract asserts flatly what the body qualifies.** Applied. The novelty claim is
   narrowed in §1.3 and the abstract no longer carries the flat form. Length: 249 words.
10. **E10, §4.2 promises two experiments and describes three.** Applied, by deleting the
    two-construct experiment on the biology review's ground 9 rather than by renaming the heading.
    The count is now honestly two.
11. **E11, reference gaps and malformed entries.** Applied in full, and the three gaps the review
    named are closed with real retrievals rather than declined. A Europe PMC search was dispatched
    to a runner on 2026-08-10 and returned the primary discovery literature for the
    *MTAP*/PRMT5 lethality (Kryukov 2016; Marjon 2016) and the method paper for the gene-effect
    scale (Dempster 2021, Chronos), all three now cited with full metadata from the retrieval record
    `mtap-prmt5-discovery-and-chronos-2026-08-10.json`. Reference [7] now carries volume, issue and
    pages. The authorless "Biology" entry is **removed**: the source artifact shows it was never a
    sole source for any junction, so the type 5 and TAF15 junctions lose nothing. The editorial
    annotations are moved out of the reference entries into §1.2, §2.6 and §4.4. The reference list
    is 21 entries and is in strict citation order.
12. **E12, the AI declaration does not answer the publisher's third element.** Applied. §2.7 states
    in the first person what the author personally re-derived and re-read, and §6 carries the
    declaration itself rather than a cross-reference.
13. **E13, author-side risk factors — STRUCTURAL, recorded.** See §11. Nothing is softened.
14. **E15, disclose the related manuscripts.** Applied. The cover letter now names
    `nr4a3-fusion-transcriptional-output` and `emc-atr-collaborator-package`, states that all three
    read GSE24369 or GSE4303 through the same artifact and code base, states what distinguishes
    this one, and offers consolidation if the editors prefer it. The venue is unchanged, as the
    brief requires.
15. **E16, verify the journal's limits.** Not closed and recorded as open, in the checklist, where
    it already was. The per-journal guideline pages return HTTP 403 from CI as well as from the
    sandbox, so the limits remain search-derived. `submission_metrics.py` now counts tables as
    display items, which is the half of the item an author can fix.
16. **E-R1, R2, R3, the three round-one claims found overstated.** All applied. The SI ranking is
    corrected (see G1), the checklist's four superseded values are corrected (see §6), and the
    "full bibliographic metadata" overstatement is resolved by removing the entry it was false of.

### S · Statistical

17. **S1, the framing asserts survival for a null.** Applied. See §1.
18. **S2, the correction's family is undeclared and determines the result.** Applied, and this is
    the item the brief made load-bearing. §2.4 now states that an adjusted *p* is a property of a
    family and that the family is a choice; Table 6 and SI §S5c report all four families
    (0.00015/0.000125 over the reported genes, 0.097/0.064 over the panel cache, 0.208/0.238 over
    the merged array-wide family, 0.208/0.031 over the same family restricted to complete cases);
    and §3.5 names the array-wide family as the one the inference is over and gives the reason. The
    values were recomputed independently rather than quoted from the review, by a module that
    imports `emc_prmt5_multiplicity` and varies only the family, so the two cannot drift apart
    (`emc_prmt5_effect_sizes.py`). All four reproduce the review's figures.
19. **S3, GPL3290 is structurally confounded — STRUCTURAL, and every claim resting on it is
    withdrawn.** See §11.
20. **S4, the adjusted *p* moves to 0.031 on complete cases, and the arm-floor convention is
    undisclosed.** Applied. The complete-case family is the fourth row of Table 6 and §3.5 states
    that on GPL3290 the value turns on a convention as much as on the data. §2.4 states the
    arm-floor zeroing convention and that it biases the adjusted *p* downward.
21. **S5, an adjusted *p* of 1.00 read as evidence of absence.** Applied. See §5.
22. **S6, the *MTAP* negative is unpowered, has no effect size, and is mis-specified.** Applied on
    all three. Table 2 carries log2 differences with 95% Welch intervals; §3.2 gives the minimum
    detectable effect (1.48-fold on GPL6244, 2.59 on GPL3290); and the mis-specification is answered
    by the per-sample analysis of §2 above rather than by a caveat.
23. **S7, the *MTAP* reading on GPL3290 is reported below its own strength.** Applied on all four
    instances. §3.1 and Table 2 carry *MTAP*'s array percentiles (72nd and 13th), Table 2 is
    symmetric across platforms and prints the GPL3290 *t* of −2.27 beside its difference, the
    direction is no longer called a reversal without its statistic, and Figure 2's caption describes
    both genes in both panels.
24. **S8, the reported hypothesis is post hoc with respect to the pre-specification invoked.**
    Applied. §2.7 states what was pre-specified (*MTAP* loss with a recorded direction), that no
    direction was recorded for *PRMT5*, that the statistic moved from the group to the gene after
    the figures were seen, and that this read is one of eighteen on the same tumours. §3.5 uses that
    record to justify the array-wide family. The reviewer is right that stating this costs the paper
    nothing it has not already lost.
25. **S9, every effect reported as a *t* on an unnamed scale.** Applied. Every reported contrast now
    carries a log2 difference with a 95% interval, in §3.2, §3.5 and SI §S3; the fold column is
    given for GPL6244 only, because on GPL3290 the arms do not share a reference pool. §2.1 states
    that no variance moderation was applied, and Table 5 carries each gene's standard-error
    percentile, which makes the reviewer's point directly: *PRMT5*'s standard error sits in the
    bottom tenth on GPL6244 and the bottom twentieth on GPL3290, while *ENO3*, whose difference is
    three times larger, has a smaller *t*. **Declined in part:** the SE-floor sensitivity table is
    not reproduced, for the reason in §4.
26. **S10, 15 of about 113 reported quantities are corrected.** Applied. §2.7 and §4.4 state the
    count, label the rest as uncorrected, and name the panel behind them. The manuscript says "about
    110" from its own count rather than adopting the reviewer's 113.
27. **S11, "exact" overstates what the permutation delivers.** Applied. §2.4, §3.5 and SI §S5c and
    §S10 qualify exactness as with respect to the labellings and under the null of exchangeability,
    and report the between-arm variance-ratio distribution, recomputed here: outside 0.5 to 2 for
    49.5% of genes on GPL6244 and 59.1% on GPL3290. §3.6 and SI §S5 note that *MKI67*'s GPL3290
    reading is carried by two extreme comparator arrays.
28. **S12, the reference-channel split is called discriminating and is not.** Applied. "Discriminating"
    is deleted, §3.6 states that no reference-matched contrast exists on that platform, SI §S5a
    presents the split as a description with that statement attached, and the one
    reference-informative contrast the platform admits is added: DFSP against GIST gives *PRMT5*
    *t* = +0.24.
29. **S13, the class-separation claim is asserted from medians with no test.** Applied. The four
    per-class exact tests are computed and reported in SI §S5b and summarised in §3.4, with a
    within-figure Bonferroni: three of the four comparator classes clear it and myxofibrosarcoma
    does not. "Separates" is replaced by the class-median statement plus the overlap counts, 9 of 34
    comparator tumours at or above the lowest EMC tumour and one of two normal-muscle arrays above
    the EMC median.
30. **S14, one probe per gene — STRUCTURAL, disclosed.** See §11.
31. **S15, five figure, caption and text discrepancies.** All applied. Figure 2's caption rewritten;
    Figure 3 now draws the non-sarcoma fractions with Wilson intervals and its axis is capped at
    100; SI §S5c's family sizes corrected to 250/1,000/3,640 on GPL3290; §2.4's family description
    corrected to "the caches hold 5,449 and 5,216; on GPL3290 368 fail the arm floor" and registered;
    and §2.1 states what can and cannot be resolved about the unexplained sample title and the
    deposit's other platform.
32. **S16, GSE24369's deposited identity.** Applied. See B11.
33. **S17, the family description in §2.4.** Applied and registered, as in S15.

### B · Biological

34. **B1, the retained-motif match is a degenerate statistic — the disclosure is made at full
    strength.** Applied. §3.7 gives the eleven GRG positions, states the plateau (four sites within
    twenty residues, the next 143 later, so any breakpoint across residues 321 to 462 retains
    exactly four: 142 residues, 21.6% of the protein), states that both matched breakpoints fall
    inside it 107 residues apart, states that the count takes only three values across all eight
    fusions, and states that the agreement is metric-dependent (8 against 7 retained RG dipeptides).
    Figure 5 shades and labels the plateau band. Every sentence offering the match as support is
    deleted from §3.7, §4.1, §5 and the abstract, and F9 is marked fired. What §3.7 concludes is the
    observation that survives: the segment every EWSR1 fusion retains carries no site.
35. **B2, reference [2] shows binding, not methylation, and localises nothing.** Applied, and
    verified against the committed preprint full text before rewriting. §1.2 now states the
    interactome proteomics, the Flag co-immunoprecipitation of an EWSR1(2-325)-ATF1(66-271)
    construct, the c-Fos promoter ChIP and the shPRMT5 effect, and states that the report shows
    neither methylation of the fusion nor any domain mapping, and that CREB1 enters the same complex
    through the retained ATF1 bZIP. The self-defeating sentence about the shared N-terminal segment
    is deleted and registered.
36. **B3, reference [3]'s own mechanism is Ewing-specific and was never stated.** Applied, and
    verified verbatim. §1.2 and §4.1 now state the CDK9-mediated Pol II activation and
    replication-stress buffering, the BRCA1 sequestration, and that olaparib alone was
    fusion-dependent in the same figure, with the consequence that fusion dependence there is shared
    by replication-stress agents generally.
37. **B4, the *MTAP* rationale is not closed and the per-sample data was never reported.** Applied
    in full. See §2.
38. **B5, the evidence-of-absence error.** Applied. See §5.
39. **B6, [3]'s design is one line, a partial knockdown and a growth readout.** Applied. §1.2 states
    the design and names the growth-rate confound; F2 carries it.
40. **B7, the principal proposed experiment measures the uninformative endpoint.** Applied. §4.2
    now specifies the readout as fusion-driven transcription plus viability, names reference [2]'s
    CRE reporter and target-gene qPCR as the precedent, and adds a concurrent non-EMC comparator
    line. The claim that a screen "already runs" is deleted from §4.2 and the abstract and
    registered (see G4).
41. **B8, the inhibitor class is unspecified and the sources disagree by class.** Applied. §1.2 and
    §4.2 state that the two rationales need different agent classes, and §4.2 gives [2]'s result by
    class from the committed text: both substrate-competitive compounds weakly active in two of
    three lines and inhibiting fusion-driven transcription in neither, the dual-site compound potent;
    and that [3] obtained its fusion-dependent effect with one of the two that failed. §1.2's
    over-favourable description of [2] is corrected and registered.
42. **B9, the two-construct experiment is not runnable and could not attribute a difference.**
    Applied by deletion. §4.4 now states why the fork cannot be settled by any experiment available
    to this work, and F10 is restated as the fork rather than as a settled test. Recorded as
    structural in §11.
43. **B10, effect size and overlap never reported.** Applied. See S9 and S13.
44. **B11, GSE24369 is a study of a different disease and neither series is fusion-confirmed.**
    Applied. §2.1 quotes the deposited title and summary, states that the six EMC cases were
    assembled as morphological mimics of the depositors' index entity, that the 17-sample FET-fusion
    control is that study's index arm, that GEO carries no linked publication, and that neither
    deposit records molecular confirmation of the EMC diagnoses, leaving the *NR4A3* instrument
    control as the only available evidence bearing on them. SI §S1 carries the same.
45. **B12, the chondroid-lineage control is premised on a lineage this tumour does not have.**
    Applied. §1.1 states with [1] that EMC does not show true cartilaginous differentiation and is
    classified as a tumour of uncertain differentiation; §3.6 reframes the control as a check
    against myxoid and matrix-associated transcription and states that a null in it is
    uninformative; the "chondroid tumours generally express *PRMT5*" limitation is deleted.
46. **B13, *PRMT1* is flat in EMC, a disanalogy with the source disease.** Applied. §3.6 reports
    *t* = 0.18 and 1.36 and the disanalogy; §4.2 notes that [3]'s largest single effect was the
    PRMT1 plus PRMT5 combination.
47. **B14, the fusion denominators are incomplete on both sides.** Applied. §3.7 now says the
    junctions are those recorded in the source artifact, notes [2]'s statement of six further
    EWSR1-ATF1 types plus EWSR1-CREB1, and notes that FUS::NR4A3 and TCF12::NR4A3 are reported EMC
    fusions not tabulated, with FUS named as the most informative missing row.
48. **B15, the priority claim is categorical where the evidence is conditional; and the
    seven-subtype panel.** Applied, and the panel question is resolved as far as public description
    allows — see §7, where it comes out in the authors' favour. §1.3 also credits [3] with raising
    both rationales for its own disease, and §1.2 states that this manuscript's structure is a
    transposition of that discussion.
49. **B16, MTAP IHC is proposed as decisive on a one-directional validity statement.** Applied. §4.2
    states that [11]'s validity runs from loss to deletion, that a retained stain excludes the
    protein-loss state rather than excluding 9p21 deletion, and that the clinical selection reported
    for the MTA-cooperative class is genomic, so a stain and a trial's entry criterion are not the
    same test. F6 carries the same. "*CDKN2A* shadow" is deleted from F6 and SI §S7 and registered.
50. **B17, reference [2]'s verification caveat is not carried at the point of use.** Applied. §1.2
    now carries it, and §4.4 states that it attaches to the inhibitor-class result specifically.
    Reference [20]'s title-level verification is stated in SI §S9.
51. **B18, the GPL3290 proliferation confound may sit in the comparator arm.** Applied. §3.6 and SI
    §S5 report that both arms sit below their arrays' means, give the comparator *z* values, and
    state that two extreme comparator arrays produce the contrast.
52. **B-(a), the activation-domain statement was declined on a false premise.** Applied. Reference
    [1]'s committed full text does state that the fusion "has the transactivation domain of EWSR1
    and the DNA binding domain of NR4A3", and §1.2's replacement sentence, which was the subject of
    B2, is gone.

### G · Integrity

53. **G1, a superseded value live in the SI.** Applied. SI §S4 now reads "third of the five tumour
    classes"; the row is added to SI Appendix S1; and the structural cause is fixed rather than the
    line alone — see §6.
54. **G2, §2.6's universal verification claim, and the register's false account of it.** Applied.
    §2.7 replaces the universal claim with what was actually done, states that a per-value check
    cannot detect a quantity reported at two values in two places, and points at the appendix for
    what it missed. Appendix A's row is rewritten to describe the sentence that now exists rather
    than the one that was intended.
55. **G3, 18,688 against 18,724 — STRUCTURAL for reconciliation, disclosed.** See §11. §2.4 and SI
    §S10 now name both resolutions, their dates, the accompanying probe-count disagreement, and that
    the 0.2% difference moves no adjusted *p*.
56. **G4, reference [18] described as supporting more than it does, in three ways.** Applied, and
    verified against the committed full text. §4.2 now states carfilzomib high and doxorubicin
    good-to-moderate in both models, no venetoclax monotherapy response in the validation, and
    synergy in one model with an additive effect in the other; "a screen that already runs" and "a
    screen already running" are deleted from §4.2 and the abstract and registered.
57. **G5, "the other three members are flat or lower".** Applied. §4.1 states that *WDR77* and
    *CLNS1A* are higher but much smaller and *RIOK1* lower, which dilutes the mean; registered.
58. **G6, Figure 1's caption and suptitle claim "every tumour".** Applied in both the caption and
    the rendered figure, with a pointer to §2.1 and Figure 4; registered.
59. **G7, §3.1 names the coverage floor where the gene-count floor failed.** Applied and registered.
60. **G8, "eight systemic classes" misdescribes a census whose eight include surgery and
    radiotherapy.** Applied and registered; Appendix A's "same number, re-attributed" row is
    corrected too.
61. **G9, F3 and F4 stated on a demoted unit.** Applied. F3 is restated on *PRMT5*; F4 is marked
    fired and merged into F5 and F6.
62. **G10, [3] cited for a proposition its own ledger does not record.** Applied and registered.
63. **G11, no gate reads a number out of prose — STRUCTURAL, partially addressed.** See §11.
64. **G12, the provenance stamp fingerprints artifacts and never images.** Applied. The generator
    now hashes every rendered PNG into the stamp and `check()` compares both sides; the success line
    reports what was actually compared. PDFs are listed and not hashed, because Matplotlib writes a
    creation timestamp into each and two runs of identical code produce different bytes. SI §S6's
    sentence is now true.
65. **G13, declarations incomplete against Wiley's standard set.** Applied. §6 adds patient consent,
    permission to reproduce, clinical-trial registration, a pointer to §8, CRediT roles and the
    preprint intent, and carries the generative-AI statement itself. ORCID remains absent and is
    recorded as the one item only the author can supply.
66. **G14, an SI claim about DepMap traceable to no artifact.** Applied by deletion, which is what
    the review recommended: the paragraph's conclusion rests on the fusion caution alone.
67. **G15, two small SI defects.** Both applied: §S5c's family sizes and Appendix S1's dangling
    §S11 cross-reference.
68. **G16, five presentation defects.** Applied: Figure 2 now carries a legend and states that bars
    are medians while the table reports differences of means; Figure 4 gives pooled normal muscle a
    distinct marker shape rather than a distinct hue and its in-figure caption names solitary
    fibrous tumour; every table in both files is now numbered and called out by number.
69. **G17, "at least 0.21", and two meanings of sixteen.** Both applied: "at least" is dropped, and
    the platforms are named by accession and sample count once in §2.1 and by accession thereafter.

---

## 4 · Grounds declined, with the reason

1. **E2 in part — delete Figure 2.** Declined. The editorial review is right that the old Figure 2
   was Figure 1's right column with a different caption, and it is right in the evidence it gives.
   But the remedy is wrong now, because the biology review turned that figure's subject into the
   paper's central negative: the *MTAP*/*CDKN2A* conjunction is a per-sample argument that no group
   statistic and no per-gene summary can display. Figure 2 has been **rebuilt** so that its right
   panel plots *MTAP* against *CDKN2A* per tumour, which resolves the duplication objection and
   makes the paper's main result visible. Deleting it would have removed the only display of the
   result the paper now leads with.
2. **E2 in part — demote Figure 3 to a table.** Declined, in favour of the statistical review's
   remedy for the same figure. The editorial review is right that three bars is a table; the
   statistical review asked instead for the non-sarcoma fractions to be drawn, for Wilson intervals
   and for the axis to be capped. Doing that makes it a real comparison figure carrying the point
   §3.3 actually makes — that the dependency is as high outside sarcoma as inside it — which a
   three-number table did not. Both reviewers' factual complaints are addressed; only the deletion
   is declined.
3. **S9 in part — the SE-floor sensitivity table.** Declined. Flooring a standard error at a family
   quantile is a stand-in for empirical-Bayes moderation and not a method the manuscript could cite
   or a reader could reproduce from a published procedure; reporting adjusted *p* values computed
   that way would put four numbers in the paper that no named method produces. The underlying point
   is accepted and is reported in the form that is checkable: the difference, the interval, the
   within-arm standard deviations and each gene's standard-error percentile, from which a reader can
   see directly that *PRMT5*'s *t* is large because its standard error is small. §2.1 states that no
   moderation was applied.
4. **S10 in part — the count of 113 reported quantities.** Declined as a number to adopt. The
   enumeration is a reasonable count and it is the reviewer's, not a value this repository owns; the
   manuscript states "about 110" from its own count and names the panel behind it. The substance,
   that the great majority of reported quantities are uncorrected and are labelled so, is applied.
5. **B15 in part — "an indexed paper has already plotted PRMT5 and MEP50 in this histology".**
   Declined on the evidence, which is set out in §7. The check was run and it points the other way.
6. **G17.2 in part — rename the platforms throughout.** Applied in the form the review suggested
   (name them by sample count once, by accession thereafter) rather than by removing "sixteen
   tumours" as the evidence base, which is the correct and conventional description of the study
   and appears in the abstract and §4.4 for that reason.

---

## 5 · One ground where two reviewers agree against round one, and round one was wrong

The statistical review (ground 5), the biology review (ground 5) and the integrity review all
converge on a sentence that round one of simulated review introduced and the previous revision
adopted verbatim into §3.2:

> "It is also at a multiplicity-adjusted *p* of 1.00 on both platforms, which is the one place in
> this paper where correcting for the number of genes examined strengthens the argument rather than
> weakening it: the closure of this rationale is exactly what an adjusted *p* of 1.00 states."

That is wrong and the manuscript's own SI said so. An adjusted *p* of 1.00 states that in every
labelling some gene in a family of about five thousand produced a larger |*t*|; it carries no
information about whether *MTAP*'s difference is zero. The asymmetry was the decisive problem: the
same non-significance was being read as absence of evidence for *PRMT5* and as evidence of absence
for *MTAP*, in one paper. The reviewers' strongest single piece of evidence for this is internal —
the same procedure assigns 0.85 to *NR4A3* on GPL6244, the transcript the fusion defining this
disease places under a new promoter, and 1.00 to *ENO3*, a published direct target.

The sentence is deleted from §3.2 and its echoes from §4.1, §5, the abstract and F5. The closure
argument now rests on the failure of the pre-specified conjunction and on the per-sample cross-check
of §2 above. The old sentence is registered in Appendix A and in `pinned-figures.json`, with the
note that it entered from a reviewer's statistical error.

---

## 6 · Why the SI's superseded value survived, and what now stops the next one

The integrity review's G1 is the item worth reporting for its cause rather than its content. The
previous revision corrected "second of four comparator classes" in the main text, in Figure 4's
caption and in SI §S6, and left it live in SI §S4 and in the pre-posting checklist, so the two
submitted files contradicted each other and one contradicted itself two sections apart.

The reason is mechanical and the review found it: CLAUDE.md rule 1.3 requires a corrected value's
old form to be registered in `pinned-figures.json` in the same commit, because that registry is how
CI finds the copies a fix missed. **No entry in that registry related to this manuscript**, and the
SI was not a target of `lint_consistency.py` at all. The gate built for exactly this failure had
been given nothing to catch it with, and it was right to return 0 ERROR.

Fixed in this revision: the SI and the pre-posting checklist are added to `targets`, and **sixteen
superseded values from this revision are registered** — the old title, the ranking, the symbol
counts, the 176-line denominator, the drifted SD values, the −0.023 locus value, the adjusted-*p*
closure sentence, the systemic-class count, the coverage-floor misattribution, "a screen already
running", "the other three members are flat or lower", Figure 1's "every tumour", the "many
malignancies" attribution, "what survives correction is the replication", "quantitative content",
and the universal verification claim. The linter now finds each of them wherever they appear and
requires a supersession marker, which is what turned up the remaining copies in the checklist.

---

## 7 · The counterexample the biology review said was most likely to falsify the paper

Biology ground 15 identified one unchecked counterexample and called it "the single check most
likely to falsify its own claim": reference [3]'s pan-sarcoma comparison uses an expression panel it
describes only as "Filion (n=137; 7 different fusion positive sarcoma subtypes including n=24
EWSR1-FLI1 and n=4 EWSR1-ERG)", and if EMC is among the unnamed five, then an indexed peer-reviewed
paper has already plotted PRMT5 and MEP50 in this histology.

It was checked, from two committed full texts, and it points the other way. The study of that name
[10] profiled **three** EWSR1::NR4A3-positive EMC tumours on Affymetrix U133A against **137** samples
of five other sarcoma types: 28 Ewing sarcomas, 23 alveolar rhabdomyosarcomas, 28 desmoplastic small
round cell tumours, 12 alveolar soft part sarcomas and 46 synovial sarcomas. Those five sum to
exactly 137, and including the EMC cases would give 140. Reference [3]'s Ewing split of 24 plus 4
reconciles exactly with the 28. So the *n* reference [3] quotes is the comparison set that
**excludes** the EMC tumours, and EMC is very probably not in the panel.

This is a reconciliation of two published descriptions and not an inspection of the deposited
dataset, which was not reachable from this environment, and it is recorded on that footing in
`prmt5-ewing-expression-panel-composition-2026-08-10.json` together with what would overturn it.
§1.3 of the manuscript states it the same way.

The same check produced a correction that runs against the paper, and it is made in §2.1: reference
[10] is a third EMC expression dataset in the published record, so "the only readable EMC expression
data" overstated what a GEO search can support. The claim is now about publicly deposited data, and
the reason that study could not be re-analysed here — no deposit returned by six committed queries,
and its own comparison set recorded as unpublished data — is stated.

---

## 8 · Where the reviewers disagree with each other, and how it was decided

1. **Verdict.** Three reviewers say decline and the integrity reviewer says minor revision. Both are
   right about different things and the disagreement is not really about the same object: the
   integrity review asks whether the document says the same thing twice and means what its artifacts
   say, and on that question the paper was close to sound (139 of 147 numbers exact, no Results
   statistic wrong, all five figures regenerating byte-identically). The other three ask what the
   paper claims, and on that question it was wrong. The revision follows the three: the claim
   structure changed. The integrity review's fix list is applied in full because none of it is in
   tension with that.
2. **Figure 2 and Figure 3.** The editorial review would delete both; the statistical and biology
   reviews want both fixed and one of them made central. Decided for fixing, with reasons at §4
   items 1 and 2. The editorial review's evidence stands and its remedy does not survive the biology
   review's ground 4.
3. **How strong the *MTAP* negative is.** The statistical review holds that the negative is
   unpowered and cannot close the rationale (ground 6); the biology review holds that the right test
   was never run and that running it would strengthen the closure (ground 4c). Both are right and
   they are compatible: the per-sample test is the correct instrument and it comes back clean, and
   sixteen tumours still only bound the frequency at 17%. The manuscript now says both, and says
   them in that order.
4. **Whether the *MTAP* rationale should be described as closed.** The biology review asks for "not
   supported, and not testable at transcript level in sixteen tumours"; the statistical review asks
   for a statement of what the data can and cannot exclude. The manuscript adopts a combination: not
   supported, with the bound stated, and the question left to a stain because protein loss is what
   the agent class turns on and a transcript could not have seen it in any case.

---

## 9 · What the four reviews got wrong, or overstated

Recorded because a response that concedes everything is not a response.

1. **The biology review reports four *MTAP*-low candidates on GPL3290; there are five.** GSM98499
   sits at the 10.4th percentile against a lowest comparator of 11.0 and qualifies on both criteria.
   The correction runs against the paper, which is why it is made: the candidate subset is half the
   arm, not four tenths of it.
2. **The biology review's inhibitor GI50 figures for reference [2] (41.0, 438.5 and 4.4 nM) do not
   appear in the committed full text**, which gives 377 and 347 nM in DTC-1 and SU-CCS-1 at three
   days and an IC50 of 422 nM in the reporter. The manuscript quotes what the committed text says.
   The reviewer's substantive point, that the class decides the outcome, is unaffected and is
   applied.
3. **The statistical review's confidence intervals and minimum detectable effects differ slightly
   from the ones now in the manuscript**, because the manuscript computes them on the array's own
   log2 scale with a Welch critical value rather than on the *z* scale. The manuscript reports its
   own, from a committed artifact with a `--check`. The direction and the conclusion are identical.
4. **The integrity review's "reference [16] is one of four sources for the fusion breakpoints"
   overstates its role.** The source artifact shows it was a corroborating record for the type 5 and
   TAF15 junctions and never a sole source, both of which are independently sourced by [14] and
   [15]. That is why the entry could simply be removed.
5. **The editorial review's "the paper has no positive finding" was true when written and is
   narrower now.** The paper carries one durable positive observation, that the segment every EWSR1
   fusion retains carries none of PRMT5's motif sites in EWSR1, and one bounded negative argued per
   tumour. Neither makes it a large paper, and ground 1 still stands as written.

---

## 10 · Figures, itemised

| figure | what changed |
|---|---|
| 1 | caption and rendered suptitle corrected to "Every tumour in the analysed arms"; footer points at §2.1 and Figure 4 for the five deposited tumours not drawn |
| 2 | **rebuilt.** Was Figure 1's right column with a different caption. Left panel now labelled per platform; right panel plots *MTAP* against *CDKN2A* per tumour on GPL3290 with the co-deletion quadrant marked. Legend added; caption states the mark convention and the median-against-mean distinction |
| 3 | non-sarcoma fractions now drawn beside the sarcoma fractions, with Wilson 95% intervals; x-axis capped at 100; title changed from "PRMT5 and MAT2A are pan-essential across sarcoma lines", which over-stated against §3.3's own argument, to "Dependency inside and outside sarcoma" |
| 4 | pooled normal muscle now a filled triangle rather than an open square in a different hue, so the class survives greyscale; axis labels give tumour counts and the gene multiplier separately instead of reporting gene-by-sample counts as *n*; legend added; in-figure caption names solitary fibrous tumour and the overlap count |
| 5 | EMC fusions solid and comparator fusions hatched rather than distinguished by fill hue; GRG ticks drawn in ink so they survive on both; the 142-residue plateau shaded and labelled with its width and its fraction of the protein; table in §3.7 reordered to the plotting order |
| provenance | every rendered PNG is hashed into the stamp and compared by `--check`, alongside the six source artifacts |

---

## 11 · Structural grounds that revision cannot fix

Stated plainly. Each of these is a property of the data, the record or the author, and no rewriting
of this manuscript removes any of them.

1. **The 16-tumour platform is confounded by construction.** On GPL3290 disease class is perfectly
   collinear with GEO submission block (three disjoint accession ranges), with the two-colour
   reference pool (three references, one per class), and with within-study platform assignment (all
   10 EMC and only 6 of that deposit's 26 comparator sarcomas were put on this array, by a selection
   nobody recorded). A permutation that relabels those sixteen samples is not exchangeable under any
   null the paper tests. The confounding is in the deposit. Every claim that the two series
   constitute a replication is withdrawn, and the platform is reported as a consistency check.
   *(Statistical ground 3.)*
2. **Every primary reading rests on a single probe.** *PRMT5* maps to one probe on each platform,
   *CDKN2A* to one on each, *MTAP* to one and two. On GPL3290 the gene assignment runs through a
   bridge resolving 58.2% of accessions on an array of expressed-sequence tags. No cross-probe
   agreement check exists and none can be constructed; a mis-annotated or cross-hybridising spot is
   excluded by nothing in this work. No decade-old array can be given more probes.
   *(Statistical ground 14.)*
3. **No EMC cell line carrying the fusion exists in any public dependency dataset**, so no
   dependency evidence for this axis in this disease exists or can be generated computationally, and
   the whole dependency section is a transfer.
4. **The mechanistic fork behind the fusion rationale cannot be settled by any experiment available
   to this work.** Separating "the fusion protein is the PRMT5 substrate" from "PRMT5 acts on
   something the fusion depends on" needs isogenic constructs and an arginine-substitution mutant
   within one construct. The two published EMC models are EWSR1-NR4A3 and TAF15-NR4A3 rather than
   transcript type 1 and type 2, so they cannot stand in for that comparison, and type 1 and type 2
   differ by 167 residues of EWSR1 and in the NR4A3 moiety, so a difference between them could not
   be attributed to four glycine-flanked arginines in any case. *(Biology ground 9.)*
5. **The retained-motif count cannot be made informative.** It is a step function with a plateau
   spanning 21.6% of the protein. No revision makes a step function carry information about which
   two breakpoints happen to sit on it. The claim is withdrawn rather than softened.
   *(Biology ground 1.)*
6. **Two symbol universes for GPL6244 cannot be reconciled offline.** 18,688 and 18,724 are two
   resolutions of the same platform table, taken two days apart, and the same caches disagree on the
   probe count mapping to a symbol. Reconciling them needs the platform table re-fetched, and the
   record shows that endpoint is unreliable. What is available is disclosure, and it is made; the
   0.2% difference moves no adjusted *p*. *(Integrity ground 3.)*
7. **No executable gate in this repository reads a number out of this manuscript's prose and
   compares it to an artifact.** `lint_citations` checks identifier provenance, `lint_style` checks
   register, `lint_consistency` checks a registry of pinned and superseded values, and none of them
   reads a statistic. The registry is now populated for this manuscript, which closes the specific
   hole that let a retracted ranking survive, and it does not make the general assurance
   machine-checked. §2.7 of the manuscript states the limit rather than claiming the assurance.
   *(Integrity ground 11.)*
8. **Insufficient advance, and the author profile.** The paper generates no new data. After this
   revision it reports a bounded negative, one sequence observation, one withdrawn sequence claim,
   and two named experiments, from sixteen archival tumours in a disease with no cell line. No
   revision produces a positive result from this data. Separately, the combination of a sole
   unaffiliated author, no ORCID, no funding, declared substantial AI assistance and two further
   manuscripts drawing on the same deposits is a profile an editorial office screens for. None of
   those disclosures may be softened and none is. The overlap is now disclosed in the cover letter,
   with an offer to consolidate; the underlying question of whether one re-analysis of two archival
   series should yield three Research Articles is the editors' to answer, and the cover letter says
   so. *(Editorial grounds 1, 3 and 13.)*
---

## Where this response's section pointers now resolve (relocation pass, 2026-08-10)

The manuscript was cut from 11,537 to about 6,500 words of main text by **relocating** material into
the supplementary file, not by deleting it. Nothing this response records as applied has been
withdrawn, and no disclosure, caveat, confound statement, sensitivity analysis or limitation was
dropped; each either stayed in the main text or moved to a numbered supplementary section that the
main text points at by name. Where a pointer in this document names a main-text section, the finding
is still stated there and the working is now in the supplement:

| what moved | from | to, in full |
|---|---|---|
| the two source reports' designs, mechanisms and inhibitor results by class | §1.2, §4.2 | S11 |
| the corpus and screen composition, and the pan-sarcoma panel arithmetic | §1.3 | S12 |
| the *z*-score background, multi-probe collapse, the probe-to-symbol bridge and its measured rates, the coverage floors, both minimum arm sizes and the realised missingness | §2.1 | S2 |
| the deposit summaries, accession blocks, reference-label caveat and per-array covariates | §2.1 | S1 |
| the family construction, the arm-floor convention and the variance-ratio distribution | §2.4 | S5c, S10 |
| the software stack and what the value-by-value checking does and does not establish | §2.7 | S13 |
| the per-sample controls, the neighbouring 9p21 genes and the ladder of *CDKN2A* cuts | §3.2 | S3a |
| the reference-channel split, including the DFSP-against-GIST contrast | §3.6 | S5a |
| the exclusion sensitivity (*PRMT5* 6.24 to 6.31, *MTAP* 0.69 to 0.70, *CDKN2A* −5.40 to −5.66), the three qualifications on the corrected figures, the count of comparisons and the transfer argument | §4.4, §4.1 | S14 |

Figure and table legends moved to a display-item legends section after the references, which is the
journal's submission format and is why the counted main text falls without any legend being changed.
