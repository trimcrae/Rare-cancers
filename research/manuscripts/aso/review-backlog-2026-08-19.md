# ASO deposit — open findings backlog (round: 2026-08-19)

Nine independent reviewers have reported. This file is the authoritative list of what is NOT yet
applied. Items already applied are listed at the bottom so nobody redoes them.

Paper: `research/manuscripts/aso/fusion-junction-aso-research-article.md`
SI: `.../fusion-junction-aso-supplementary-information.md`
Generators: `research/manuscripts/submission_tables.py`, `build_submission_pdf.py`,
`aso_sequence_manifest.py`, `aso_archive_manifest.py`
Instruments: `research/modalities/aso_parent_null.py`, `aso_parent_gap_pairing.py`
Guards: `research/manuscripts/tests/`, `research/modalities/tests/`

## RULES THAT OVERRIDE EVERYTHING
- NEVER fabricate a PMID, accession, RRID, DOI or sequence. Never write an identifier from
  recollection. If a claim needs a citation nobody retrieved, restate it as an assumption this work
  adopts, or delete it — do not invent a source.
- Generated files change AT THE GENERATOR, never by hand. `systems/views/` is generated.
- Every number written into prose must be recomputed from a committed artifact in the same session.
  If a number has no artifact home, put it in one first.
- Do not run `git checkout/restore/stash/clean`. Do not revert other agents' work.
- Do not commit or push. Leave the tree dirty; the coordinating session commits.

---

# LANE A — manuscript and SI prose (`*.md` only)

## A1. Statistics (from independent re-derivation; every number below was verified)

- **§2.3 composition correction, means vs medians.** Paper says matching removes "about a fifth" of
  the TFG excess. That is true on means (0.3044 of 1.4920 = 20.4%) but the same paragraph has just
  declared the means unusable for these distributions and moved to medians. On medians matching
  removes 33% and the matched non-TFG figure is 1.00 — exactly chance. Print the median-scale
  figures (1.53-fold vs 1.00) beside the mean-scale ones, or scope "a fifth" to means explicitly.
- **§2.3 SD 3.36 → 3.41.** TFG sample SD (ddof=1) is 3.4120; population SD is 3.3547. The companion
  figure 0.44 for the other 146 is the *sample* SD. Use ddof=1 for both: 3.41 and 0.44.
- **§2.3 mean 1.29 → 1.30.** The five scored TFG junctions mean to 1.2977. Round, don't truncate.
- **§2.3 one-sided matching.** The ≤7 G/C restriction is applied to the comparison group only; TFG's
  mean stays over all 30 including its one design at 8 G/C. Matching both sides gives 2.2786 vs
  1.0439 = 17.2% removed. Either restrict both sides or say the restriction is one-sided.
- **§2.5 sub-binomial design effect.** deff 0.8168 reproduces, but a 20,000-draw permutation null
  over the 38 junctions gives mean 1.001, SD 0.206, 95% range 0.62–1.41, p(deff ≤ 0.817) = 0.17. It
  is not distinguishable from 1. Drop the causal sentence ("the five registers disagree with one
  another about NR4A3 more than two designs drawn at random would") and say the sub-analysis's
  design effect is not distinguishable from no clustering, keeping the decision to report the
  nominal interval. For contrast the aggregate deff 1.4225 sits at the 96.6th percentile (p=0.034).
- **§2.5 clustering absorbs only one of the two non-independences named.** Junction clustering places
  a multi-partner molecule's identical records in DIFFERENT clusters, so it does not correct for the
  190-records-are-176-molecules point the same paragraph raises. Molecule-level rate is 82/176 =
  46.6%, Wilson 39.4–54.0%. Say the correction is for register clustering only. Also name the
  interval's construction: Wilson evaluated at n_eff = 133.57.
- **§2.5 the 3.6 pp spread is itself nominal.** √(0.40568×0.59432/190) = 3.56 pp assumes independent
  draws; at the paper's own deff 1.42 the comparable spread is 4.3 pp. Use 4.3, or say 3.6 is nominal.
- **§2.10 seam-hybrid identity has an exception.** max(donor, acceptor) = 11 − margin for all 190,
  but ΔΔG is computed against the MORE STABLE run, and for 6 of 190 that is the shorter side. Add
  "except where the shorter run is the more stable, which is 6 of the 190".
- **§4.3 corpus median.** "against a corpus median of 0.97" is attached to both the ≤2-mismatch ratio
  (0.69) and the gap-paired ratio (0.62). The gap-paired corpus median is 0.8152. Quote 0.82 for the
  gap-paired axis or attach 0.97 to the ≤2-mismatch figure alone.
- **§2.7 the 58% needs its stratum.** 58% is the non-hybridisable share of GAP-PAIRED ≤2-mismatch
  sites (1 − 156/371 = 57.95%); over all ≤2-mismatch sites it is 58.85% → 59%. Name the stratum.

## A2. Negative-result calibration (the cut is used in one direction in places)

- **§2.9 credit side at the loose cut.** "parent-clean designs available at each junction rise from
  2.7 to 4.7 to 6.7" is a reading at ten only. At seven the series is 0.4, 3.6, 6.7 — the two longer
  geometries are unaffected because their gaps already exceed seven, so the loose reading damages
  only the geometry the paper panels. Verify by re-running `aso_parent_gap_pairing` per geometry at
  a cut of 7 before writing it. State it.
- **§4.4 scramble rejection rule.** "redraw the scramble where a wild-type parent pairs its whole
  catalytic gap over ten base pairs or more" — at seven the scramble null is 74.3% and the NR4A3 arm
  23.9% (now in `aso-parent-null.json` → `null_ensembles.*.at_7bp`). Say plainly that a passed
  scramble is clean at ten and not below it.
- **§2.3 topic sentence.** "Specificity does not sort by partner." is contradicted eight sentences
  later in its own paragraph ("one axis printed here does sort by partner"). The Discussion states it
  correctly ("On the one existence statistic tested"). Qualify the Results topic sentence the same way.
- **Box 1 and §6 corpus counts.** Box 1 says "250 of the 780 records the canonical file holds" and §6
  says "every one of the 250 records in the file for which a wild-type parent pairs the whole gap at
  the criterion applied throughout". The file holds 780 rows; 249 carry a mature-parent duplex ≥10 bp;
  252 carry a non-empty `do_not_order` (249 at the ten-base-pair reason + 3 at the separate
  un-rearranged-allele reason); 250 is the count of `pairs_a_wild_type_parent_through_the_gap == True`,
  which folds in one cryptic-exon record with a BLANK duplex field that appears in neither Table 3
  nor Table 4 and so cannot be "marked ⚑ there". Report 249 at the stated criterion, name the column
  the number is reproducible from, and keep the un-rearranged-allele class separate.
- **§6 "Over the 40 junctions the file keys a row to".** The file keys 43 distinct junction values (42
  with a 5-6-5 row). Recompute; do not type it.

## A3. Safety — condemned sequences printed without their verdict

- **§2.6 vs Table 5 look-alikes.** §2.6 names the two kept reagents as `AGTGGGCTCTCCACGG` and
  `ATGAGGGCCTTGTGTG`; Table 5's "beside the panel" rows carry `AGTGGGCTCTCCACGG` and
  `AGTGGGCTCTTGTGTG` — a different molecule. Name the seam beside every sequence in §2.6's closing
  sentences.
- **An aligned do-not-order block.** Four near-identical 16-mers exist across §2.6 and §4.1, two
  orderable and two forbidden, differing by a single-base slide (`CAGTGGGCTCTCCACG`,
  `GCAGTGGGCTCTCCAC`, `AGTGGGCTCTCCACGG`, and §4.1's `GGGCATATCTCCACGG`). Prose is not the right
  carrier for this. Add ONE monospaced aligned block, all four one above the other, each row labelled
  ORDER / DO NOT ORDER, differing bases marked. This is the highest-value single addition available.

## A4. Chemistry (from the ASO chemist)

- **§2.10 free energies.** "every one of the 190 designs favours the fusion duplex … by 4.8 to 13.1
  kcal/mol with a median of 9.6" — these are unmodified DNA:RNA nearest-neighbour values, which §6
  says but §2.10 does not. Add "as an unmodified DNA:RNA hybrid" to the sentence that first reports
  the range.
- **§2.10 / §4.1 the 5′ G-tract.** Both named leads begin 5′-GGG, and at 5-6-5 those three guanines
  are the first three positions of the LOCKED wing. Contiguous locked G-runs are the specific
  synthesis, aggregation and Tm liability of LNA gapmers. The paper currently treats the G-tract only
  as a question of which conventional rule catches it, and says the leads "fail no rule" — which
  reads as a chemistry clearance. State beside the leads that their 5′-GGG lies wholly inside the
  locked wing and name the consequence. (The rule set applied is the DNA/MOE rule set; the
  LNA-specific constraint is the one both leads sit outside.)
- **§2.10 homopolymer count.** "13 carrying a homopolymer run of four" is base-blind. A run of four A
  or T is close to inert; a run of four G is the liability, and its position (locked wing vs DNA gap)
  changes what it costs. Report the 13 split by base and by wing/gap position — recompute, do not type.
- **§2.9 / §4.2 the missing gap-length axis.** Lengthening the DNA gap widens the RNase-H1-competent
  window, which is a recognised driver of RNase-H1-dependent off-target cleavage in gapmer series —
  the direction associated with hepatotoxicity. §6 and §5 raise gapmer hepatotoxicity but tie it only
  to affinity and wing content; §2.9 and §4.2 do not carry it, and §4.2 recommends synthesising the
  5-8-5 arm. Also: locked fraction falls 62.5% → 55.6% → 50% across the three geometries, so the
  affinity-linked liability is itself geometry-dependent and Table 7 has no row for it. Scope
  §2.9's "the trade is exact" to the base-count identity rather than to the whole chemistry account.
- **§2.8 / §4.1 "the organs a systemically dosed phosphorothioate gapmer distributes to".** Liver and
  kidney cortex dominate, but spleen, lymph node, bone marrow and adipose accumulate substantially.
  Write "the organs of highest accumulation" and note that distribution extends beyond them.

## A5. Citation vs source (do NOT invent citations — restate or delete)

- **Intro refs 6+7 distribute two propositions over two sources; each carries only one.** Ref 6
  (PMID 41055792) carries the anthracycline objective-response-rate statement; ref 7 (PMID 31331701)
  carries low sensitivity to cytotoxic chemotherapy generally. Split the attribution.
- **§3 essentiality claim, uncited.** "whose partner genes are essential RNA-binding proteins —
  *TCF12* and *TFG* … are not". No retrieved essentiality artifact exists anywhere under `research/`.
  This sentence relocates the whole case for junction selectivity onto the donor side. Either cite a
  retrieved source or restate it as an assumption. Do not invent one.
- **§6 three uncited literature claims in a row.** "conventional locked-nucleic-acid gapmers carry two
  to four per wing"; "the 5-6-5, 5-8-5 and 5-10-5 geometries tiled here are the convention of the
  2′-O-methoxyethyl gapmers rather than of locked ones"; "high-affinity gapmers are associated in the
  literature with sequence-dependent hepatotoxicity". No retrieved record supports any of the three.
  Restate as adopted premises with that stated, or delete. The third is offered as bearing "on any
  decision to synthesise", so if it stays it must say it is uncited.
- **§6 ref 51 over-generalised.** "where allele selectivity is achieved it is engineered by modifying a
  gap position" is drawn from ONE single-nucleotide-variant study in one gene and one chemistry.
  Narrow to "in one reported gapmer campaign against a single-base substitution, …".
- **§6 ref 33 restatement.** The ~five-fold single-nucleotide discrimination figure is explicitly
  restated from prior work in its source ("have been previously shown"), and is about ASOs generally
  rather than gapmers. Add the restatement qualifier the SI already uses for the gap-length figures.
- **§6 ref 50 count.** The source gives two gapmers for APP 692 G plus one for SNCA 53 A, both in
  vitro and in cells — exactly three. Write "three of more than 120 gapmers", not "two or three".
- **§2.6 ref 24.** The *EWSR1* type-2 exon assignment comes from a narrative review restating primary
  work; the repo's own census artifact records that ("cited for the exon assignment and never for a
  count"). Name it as a review, as the paper does for refs 20/21, 31 and 39.
- **Intro refs 20+21 are not interchangeable.** The repo's pooling artifact records ref 20 as written
  by the senior authors of BOTH primary reports — "not an independent reading of them" — and ref 21
  as the independent corroborating read. Say so, in a paragraph whose point is cohort non-independence.
- **Intro refs 7+19 vs the numeric arm.** The three-to-five arm size comes from refs 20/21, not from
  refs 7/19 whose retrieved records carry no fusion-partner breakdown. Attach the numbers to 20/21.
- **§3 fusion-negative EMC, uncited.** Attach one of the already-retrieved sources that reports
  fusion-negative or rearrangement-negative EMC (ref 39's two cases; ref 36's ">90%").
- **§6 FET low-complexity amino-termini, uncited.** Ref 23 supports the paralogy statement only.
  Reduce the clause to what it supports, or cite a retrieved FET source.
- **§2.10 / §6 the four conventional design rules, uncited.** GC 40–60%, no G-quadruplex motif, no
  homopolymer run of four, no CpG — asserted as field convention with no source, and a whole Results
  paragraph is scored against them. State that the rule set is adopted here and name its basis.
- **§5 ref 39 provenance disagreement.** Two retrieval artifacts disagree about whether the
  citation-marker fact was ever read (`lit-targets-aso-breakpoint-census.json` says yes via OCR;
  `lit-targets-aso-round7-precedents.json` marks it ⛔ UNVERIFIED). Reconcile, and record which
  artifact the sentence stands on.

## A6. First-time-reader defects (vocabulary is the paper's biggest remaining cost)

Highest-yield first. The reader's summary: *"the vocabulary is overloaded — record, screen, clean,
parent, margin, arm, panel, gap, route each carry three to seven senses."*

- **"record" carries seven senses** (bibliographic record, retrieved record, CSV row, design record,
  RefSeq accession, hit record, the public record). Reserve "record" for the CSV row; use "citation",
  "accession", "hit" and "the published literature" for the others. Single highest-yield edit.
- **"clean" carries four senses.** Box 1 defines it strictly (no sense-strand near-match anywhere);
  §2.3 uses it for gap-only cleanliness; §2.9 adds "parent-clean"; §3 adds "identity-clean" for STR
  authentication. Use three named predicates — near-match-clean, gap-clean, parent-clean — mechanically,
  and "STR-concordant" for the cell lines.
- **"screen" carries three senses**: a named instrument, a released per-junction run ("93 screens"),
  and the generic act. Call the second "screen runs" or "screen outputs" so "93" is placeable against "five".
- **"margin" carries five senses**, surgical margin first. Never write bare "margin" for the gap-level
  quantity; §2.5, §2.9 and §2.10 currently do.
- **"arm" carries four senses** (trial arm, null ensemble, experimental arm, coverage component). §6
  already calls the nulls ensembles; use that, and "partner terms" for the coverage components.
- **"gap" collides with itself in §6 screen 1.** "110 retained alignments carry a gap" reads as
  pairing the catalytic gap. Write "carry an indel".
- **"route" carries three senses** in §3 (delivery route, test-article acquisition route, citation
  route). Rename the second "the two sources of a test article".
- **"design" vs "design record" vs "molecule".** The §2 preamble says they are not interchangeable and
  the rest of the paper uses them interchangeably. Pick one word for each and use it mechanically.
- **"liable" / "liability" / "condemn" are load-bearing and never defined.** Add to Box 1: "A design is
  **liable** where a wild-type parent pairs its whole catalytic gap over ten base pairs or more."
- **Abstract terms used before definition**: gap-level margin, clean, load, screen, register. One
  parenthetical clause for gap-level margin buys the paper's second headline result.
- **Abstract "clears the screen" → "clears the mature-parent screen"** (five screens are named later).
- **Abstract "61 against wild-type NR4A3" → "61 of those 87"** (currently ambiguous between /87 and /190).
- **Abstract: 181 of 190 at ANY length is missing.** The abstract gives 87 (at 10) and 175 (at 7); the
  threshold-free rate is 95%. Adding it costs ~8 words and it is the honest anchor. NOTE: the abstract
  is at 399 words against a hard bound of 400 (`test_aso_abstract_is_bounded.py`). Anything added must
  be paid for by cutting, and the cut must be recorded. Judge whether this displaces something weaker.
- **§2.4 "do not order this list" arrives AFTER the nine sequences.** Move it before the list. Table
  4's caption already does this correctly.
- **§2.4 / §2.7 the clean-design count goes 9 → 3 → 4 → 3 and the TCF12 e7 member changes molecule.**
  The reader lost the paper's central quantitative thread here. Add a small table or figure:
  9 default-clean → 3 surviving depth → +1 late-screened → 4 → −1 parent screen → 3 candidates, with
  the member sequences at each step. The paper has seven tables and none is this one.
- **§2.6's section-defining bolded sentence is unparseable on first read.** Lead with the mechanism:
  where a design's acceptor half is *NR4A3* sequence that is not exonic in the mature transcript, the
  un-rearranged allele carries that same sequence behind an intron.
- **§2.9 states its result in the order that builds the wrong belief.** The "guaranteed by the
  instrument" caveat and the one-for-one parent-run rise are a page after the 54-of-54. §3 gets the
  order right; §2.9 does not. Move the nesting-bound caveat into the same paragraph.
- **§2.9 "the count of liable designs does not fall" reads as a null result.** Three positions in one
  paragraph. Lead with "Neither framing is the whole reading" (currently the fourth sentence).
- **§3 antigen paragraph reads as self-contradictory.** "none cleared … together" then "three cleared
  both". Rewrite: "Of twelve, three cleared both measured axes; two of those three were refused by the
  prior and one (RET) is ungraded. No antigen cleared all three."
- **§3 "this work has no laboratory" is the paper's most consequential practical statement and is a
  subordinate clause on p20.** Move it to §4's opening — a reader entering "Reagents, controls and the
  falsification experiment" should already know the experiment has no host.
- **§4.1 two impossibility numbers in one sentence** (114.7% and 101.4%) read as two attempts at one
  calculation. Keep 101.4% in the sentence; move 114.7% to a note.
- **§5 chance expectation has no denominator in the main text.** "189 near-matches for any 16-mer
  whatever over the exhaustive scan's measured span" — the span (718,571,139 nt) appears only in the
  Supplementary Figure S1 legend, and §5 elsewhere gives the genome span as 3.10 × 10⁹, so the reader
  cannot reconcile 189 with 2.6e-7. Give the transcript-scan span where 189 first appears.
- **§4.4 show the arithmetic**: "1/(1 − 0.58) ≈ 2.4".
- **§2.10 the 11 in "11 minus the gap-level margin"** is unexplained. "…is exactly 11 (five wing bases
  plus the six-nucleotide gap) minus the margin".
- **§2.5 19,921 vs 20,011** read as a correction of each other. "19,921 windows over 20,011 nucleotides
  of parent sequence (six transcripts, so 6 × 15 fewer windows than bases)".
- **§2.7 the two secure candidates' loads read as the leads' loads.** "0.33 and 0.24 … 0.06 and 0.04 …
  26th and 13th of 176 and 5th and 1st" — name the designs and state the pairing order.
- **§1 the TAF15 arm's "three to five" denominator range is explained on the next page.** Move the
  explanation into the same sentence.
- **§1 "four records → three papers".** State three papers as the finding and four records as the
  parenthetical.
- **§2.1 three different 77s** on facing concepts. Write "across the 77 rows of the exon-3 column".
- **§2.3 "means of 0.51 to 0.71" — of what?** Name the four partner means. And 30 + 146 = 176, so the
  denominator silently switches from 190 to 176 mid-paragraph: say "of the 176 distinct molecules".
- **§2.4 the 27/29/84 vs 64 confusion.** Either-strand totals and a sense-strand gap-paired subset sit
  four sentences apart with no shared qualifier. This paragraph is carrying a small table in prose.
- **§6 −8.66 denotes three different quantities** (5-8-5 lead's parent ΔG, 5-6-5 panel median, and the
  §6 median). Flag the coincidence where it would otherwise read as an error.
- **§2.1 / §2.6 / §5 type numbers** are declared not to need resolving, then used as objects. Either
  add a two-row type↔exon-pair table or write "EWSR1 e7::NR4A3 e2 (the transcript ref. 24 calls type 2)".
- **Results subsection standfirsts.** Thirteen pages in which the qualification is frequently more
  important than the claim. Give §2.3 and §2.9 a one-line standfirst carrying the NET position.
- **Page footer repetition.** The 66-page repeated order-safety footer has become furniture. Consider a
  short rule on body pages and the full sentence on tables pages and page 1. (Builder change — coordinate
  with Lane B; do not edit the builder from Lane A.)

## A7. SI

- SI preamble says Supplementary Figure S1 "travels with the archive" — it is printed on the main
  PDF's figure-legend pages. Fix the pointer.
- SI cites refs 22, 25, 28, 38, 41, 42, 52 by number and carries no reference list. Add a short
  "References cited in this Supplement" block repeating those seven entries.
- SI title block carries running title, author, affiliation and correspondence but not the article's
  full title and no preprint / not-peer-reviewed statement. Add both.
- SI/main cross-references name the `.md` source filenames; the deposited files are the two PDFs.
  (Coordinate: the fix may belong in the builder — Lane B.)

---

# LANE B — generators, tables, builder, canonical sequence files (NO `.md` prose)

## B1. Figure and table integrity (all verified against the artifacts by the reviewer)

- **Table 4 caption is wrong about Table 3.** It says five of its rows "carry the ⚑ … and Table 3 marks
  them do-not-order for it". Only ONE of the five (`GGCATATCAAGCGCTG`) appears in Table 3 at all —
  Table 3 prints one row per junction, that junction's highest-margin design. At two of those junctions
  Table 3 prints a DIFFERENT, UNMARKED design (EWSR1 e1 → `GGGCATATCCGTGGAC` at 0 bp; TCF12 e9 →
  `GGGCATATCTTGCATA` at 8 bp), so a reader following the pointer lands on a clean row. Drop the
  cross-reference or state what Table 3 selects. The same wrong belief is repeated in
  `submission_tables.py`'s `table4` docstring and at its ⛔ comment near line 1490 — fix both.
- **Table 2 caption.** Table 2 is the table a reagent is chosen from; it carries a "longest parent
  duplex through the gap (bp)" column and its caption never states the ten-base-pair criterion, never
  says clearing is a reading at one cut, and never carries the ⚑ vocabulary. 31 of its 35 rows sit at
  6–9 bp, just under the cut, and the reader cannot see that. Give it the one-sentence gloss Table 4's
  note ⁷ carries, plus the cut caveat Table 3's ⚑ note carries, including that 175 of 190 pair a parent
  at seven and 9 of 38 junctions clear there.
- **Table 5 caption.** "the parent duplex is … at the ten-base-pair criterion applied throughout" reads
  as though the column were filtered at ten. Every value is 0, 7, 8 or 9. Write "…; the criterion
  applied throughout is ten base pairs, which no row here reaches."
- **Table 3 and Table 4 continuation-page running headers** drop both halves of the criterion the
  first-page caption carries — "at the ten-base-pair criterion applied throughout" and "An unmarked row
  is not a clearance, only a reading at that one cut". On one continuation page alone, 14 unmarked
  sequences print beside parent-duplex readings of 7–9 bp under a legend that never states the cut.
  Extend the generated continuation label in `build_submission_pdf.py` (`_label_for_spliced_table`).
- **Table 6 continuation pages lose the ◆ gloss.** `_label_for_spliced_table` glosses ¹–⁹, † and ⚑ but
  has no ◆ branch, and pages 51–52 carry ◆-marked rows whose only definition is on page 50. Add it.
- **Figure 3 title and caption name the wrong quantity.** Title says a longer gap "concedes wild-type
  parent duplex, one for one"; the drawn quantity is the own-seam arithmetic run (3 → 4 → 5), while the
  measured mature-parent duplex through the whole gap for those same three molecules runs 8 → 0 → 0,
  and corpus-wide the ten-base-pair count is flat at 87/88/87. "Parent duplex" is this paper's own name
  for the condemned quantity. Name the drawn axis as the parent-paired gap DNA AT THE DESIGN'S OWN
  SEAM, in both the in-panel title and the caption, and add the 8 → 0 → 0 clause.
- **Figure 3B "a line of slope −1".** The axes are scaled independently (112.7 px/unit vs 19 px/unit),
  so the drawn slope is −0.169. Write "slope −1 in the plotted units (the axes are scaled
  independently)", or square the panel.
- **Figure 1 caption** never says the grid is drawn as two side-by-side continuations with the three
  acceptor columns repeated (the in-figure subtitle does). Add it. And the caption lists the partners
  in a different order from the panels (panels draw EWSR1, FUS | TAF15, TCF12, TFG). List them in
  drawing order.
- **Figure 2 caption** does not say the drawn letters are the TARGET mRNA and that the named reagent is
  its reverse complement — in a paper whose banners say a transcribed sequence is a different molecule.
  Add it. Also: the figure's title asserts "One 16-mer spans three partners' breakpoints" and its own
  caption withdraws two of the three (TAF15 e11 and FUS e10 are carried by no reported patient).
  Retitle to say so, and mark the two unobserved rows in the panel.
- **Supplementary Figure S1's own caveat block** does not say that 40 of the 176 bars are zero and draw
  nothing, so a figure lifted from the paper reads as a 136-bar series starting a quarter of the way in.
  The manuscript caption says it; the figure's self-contained block does not. Add it, plus the 1.12×
  mean ratio.
- **Table 4's title is withdrawn by its own caption** ("The 9 designs with no sense-strand near-match at
  the default search depth. Six of these lose the property when…"). Retitle: "Default-depth near-match
  screen: the 9 shortest hit lists, six of which are not clean at depth".
- **Table 5 is not readable from its caption alone** (~900 words, three row classes sharing a
  "cumulative coverage" column that means something different in each). Split into two tables — the
  ladder (rungs + bounds) and the seams-beside-the-panel — and let the contrast arms live in §4.
- **Table 1**: "in-frame" and "with ≥1 fusion-specific design" are identical in every row and the
  caption never says why both columns exist.
- **Table 2's caption never defines "parent liability", its primary sort key.**

## B2. Canonical sequence files

- **Move `do_not_order` to column 2**, immediately after `sequence`. It is currently the 14th of 14
  columns — off-screen in a default spreadsheet view of the file the paper directs every order to,
  while the comment block above says "READ `do_not_order` FIRST". The FASTA already puts the verdict
  inline on the defline.
- **The full linkage specification must live in the CSV and FASTA chemistry headers**, not only in the
  PDF the reader is told not to order from. "On a phosphorothioate backbone" alone is compatible with
  PS wings and a phosphodiester gap, which is a real gapmer variant. Put verbatim into both headers:
  every one of the 15 internucleoside linkages is a phosphorothioate, stereorandom; the bicycle is
  β-D-oxy-LNA; locked cytosines are 5-methylcytosine and gap cytosines are unmethylated
  2′-deoxycytidine; termini are free 5′-OH and 3′-OH; sodium salt. (§6 now specifies all of these —
  copy from there, do not re-derive.)
- **Add title, author and the archive DOI line to both headers.** These two carriers are the most
  likely to be forwarded on their own and neither can currently be traced back to the deposit.
- **The nine third-state rows.** `EWSR1_e10__NR4A3_intron2crypticExon` and
  `TAF15_e6__NR4A3_intron2crypticExon` designs carry `pairs_a_wild_type_parent_through_the_gap = ""`
  (not measured), an empty duplex cell and an empty `do_not_order`. For those nine the header's
  sentence "an EMPTY value is a reading at that one cut and NOT a clearance" is FALSE — it is no
  reading at all. Give the third state a visible sentinel and say so in the header.

## B3. Deposit mechanics (bioRxiv screener)

- **The archive manifest lists neither deposited PDF, nor itself**, while the Declarations promise "a
  manifest listing every archived file with its SHA-256". It is built by glob from availability
  promises and no promise names the PDFs. Add both PDFs (and either a self-entry or an explicit note).
- **The manifest is already stale**: `git_tree_is_clean_apart_from_this_manifest: false` and 5 of 384
  recorded hashes no longer match disk. Regenerate against a clean tree in the same commit as the
  rebuilt PDFs. (Coordinating session will sequence this — do not commit.)
- **Two near-identical full manuscripts sit in the deposit directory** —
  `fusion-junction-aso-research-article.pdf` (46 pp) and `…-manuscript.pdf` (66 pp) — with the SAME
  `/Title` metadata, 99.8% identical text, and nothing saying which is the deposit artefact. Name the
  deposit artefact explicitly in the availability statement and move or delete the twin. **Check with
  the coordinating session before deleting a tracked file.**
- **`fusion-junction-aso-submission-tables.md` is an orphan** — named nowhere in either PDF, in the
  abstract, or in any availability statement, and carrying no author, no article title and no preprint
  statement. Name it in the availability statement as the machine-readable copy of the same seven
  tables, and add title and author to its header.
- **The main PDF points at `…-supplementary-information.md` and the SI points at
  `…-research-article.md`; neither file is in the deposit.** Have the builder emit the deposited PDF
  filenames in both cross-reference statements.
- **The repository URL breaks across a line at a non-hyphen point** in two places, and it is the
  deposit's only working pointer to the code while the DOI is a placeholder. Mark it non-breaking in
  the builder CSS.
- **Zero link annotations and zero outline/bookmark entries across 69 pages**, including seven
  multi-page landscape tables and 52 references with DOIs. Enable the builder's PDF outline and
  auto-link DOIs and URLs.
- **No preparation date or version on the title page.** Print the build commit's short SHA and date.
- **A Type 3 font appears on the five pages carrying the ⚑ markers in Tables 3 and 4** and nowhere else;
  every other face is an embedded TrueType subset. Force the glyph to the embedded DejaVuSans subset.
- **The "Figure legends" page carries only a heading and a four-sentence note**; the legends themselves
  are printed under each figure on the following pages. Fold the note into the first legend and drop
  the page.
- **The tables file is Markdown**, which is not among the supplementary file types bioRxiv lists.
  Render it to PDF or CSV alongside.
- The two remaining deposit BLOCKERS — the ORCID placeholder and the archive DOI placeholder — are
  trimcrae's to supply and are NOT to be filled by any agent. Leave them; they are working as designed.

---

# LANE C — the guard suite (`research/manuscripts/tests/`, `research/modalities/tests/`)

An audit of 827 guards found 24 defects. Several guards assert something weaker than their docstring
claims, and two certify a false value. Fix the guard, and where the guard was hiding a real defect,
report it to the coordinating session rather than editing the manuscript yourself.

## C1. BLOCKERS

- **`test_pdf_text_layer_is_orderable.py::test_no_page_of_either_pdf_is_left_stranded`** — the "followed
  by a display item" conjunct is implemented as "the next page holds more than 1,500 characters", which
  is true of 47/47 journal pages and 63/66 manuscript pages. A completely blank page in the
  journal-format deposit is guarded by nothing (`test_no_page_is_nearly_empty.py` covers the manuscript
  PDF only, at a 300-char floor). Make the exemption test for an actual `LTFigure`/table grid or a
  `**Table n.` opener.
- **`test_aso_submission_numbers.py` `screens_complete` block (~line 786) + `test_aso_coverage_ladder.py`**
  — `assert len(screened) == 4` pins `screens_complete: true` on all four non-canonical-acceptor seams
  INCLUDING `PGR_e2__NR4A3_e2`, whose record reads `n_screens_that_ran: 5`. The manuscript's §4.1 and
  §2.6 both say the PGR seam is graded on FOUR of five, because the pre-mRNA screen's parent set does
  not carry that donor's unspliced sequence. That flag is what admits PGR to `n_junctions_qualifying =
  9`, which prices SI §S6's 82.9% figure. The companion guard was re-anchored on 2026-08-19 to remove
  the clause that would have exposed this. Give the artifact a per-screen record (PGR pre-mRNA = not
  run), assert `n_screens_that_ran` per junction against the paper's "eight of those nine", and
  re-derive the ladder's membership rule from it. **Report the resulting figure change upward.**

## C2. MAJOR

- **`test_exon_numbering_convention_is_computed.py::test_the_printed_exon_counts_are_the_models`** never
  opens the manuscript. Its `words` parametrize argument is unreferenced and contains a literal `\n`
  that could never match. Changing §6 to "TCF12 carries 20 transcript exons and 18 coding" passes.
  This is the file that exists because that axis is what an earlier version was withdrawn on.
- **`…::test_the_genes_whose_conventions_coincide_really_do`** asserts three genes; the manuscript
  sentence names four, and PGR — the fourth — is absent from both artifacts, so the test certifies an
  unverified claim about the one seam an outside laboratory would reconcile. Add PGR's exon spans and
  UTR lengths to the model, or split the sentence.
- **`…::test_the_index_shift_is_not_assumed_to_equal_the_count_difference`** ends in a tautology no
  input can violate. Drop it and assert the per-gene shifts for TFG and NR4A3 instead.
- **`test_every_ordering_route_carries_the_same_verdict.py`** compares one generated column against
  another generated column that the same generator sets from the same expression, so no input can make
  it fail. Recompute a sample of `mature_parent_duplex_through_gap_bp` from the design sequence against
  the six parent transcripts and assert the flag against THAT.
- **…and the manuscript prose is not one of the routes it checks.** The article body prints 26 distinct
  sequences in 5′-…-3′ form and six of them carry `do_not_order`. Extend the parametrised carrier check
  to the article body: every `5′-…-3′` whose CSV row is condemned must sit within N characters of its
  verdict. (Several of these were fixed in prose this session; the guard must exist so a seventh cannot
  be added silently.)
- **`test_table_captions_state_the_right_geometry.py::test_the_controls_that_have_no_row_really_have_none`**
  skips itself when the caption is reworded. Run the row check unconditionally; assert the caption separately.
- **`…::test_a_caption_claiming_one_architecture_is_true_of_every_sequence_it_prints`** matches one
  literal regex and returns silently on no match. Parse "N-mer" and "a-b-c" tokens out of the caption
  instead of matching the sentence.
- **`test_condemned_designs_are_absent_from_the_tables.py::test_the_research_use_header_describes_the_absence…`**
  is a three-string blacklist whose docstring claims it asserts on the property. Assert on structure.
- **`test_universal_claims_are_scoped_to_what_was_measured.py`** — 5 of its 6 sections are exact-string
  blacklists whose preamble says they pin the scope and not the wording. Each of the five recorded
  contradictions can be reinstated in synonyms. Express each as a quantifier-plus-noun regex, the way
  `test_no_sentence_quantifies_universally_over_the_parent_counts` already does.
- **Nothing guards the manuscript title.** No test reads the front-matter `title`. Nothing derives
  "nearly half" from 87/190, and nothing checks the trade clause against §2.9. The title was rewritten
  one commit ago because the previous one was contradicted by §2.9 — found by a human, not the suite.
  Pin the rate word against the clustered `p`, and the trade clause against §2.9.
- **Nothing guards Box 1's size-of-the-class figures** (the 250/780/"five of the nine"). Derive all
  three from the CSV and Table 4 and assert them against Box 1. **See A2 — the 250 is wrong; the guard
  and the corrected number should land together.**
- **The CSV's documented third state is unreachable by the guard written for it.** Nine rows carry the
  empty "not measured" flag and the header's sentence about empty values is false for them. Assert that
  such rows are distinguishable in the file and that the header says so.
- **`test_aso_abstract_is_bounded.py`** — the bound was raised 380 → 400 to buy four named
  qualifications and pins NONE of them; its four needles are older strings, two of them weak. Add the
  four clauses the raise bought to the needle list. **The abstract has been rewritten this session and
  now sits at 399 words; re-anchor the needles against the current text, including the seven-base-pair
  dual reading and the parent-clean-per-junction clause.**

## C3. MINOR

- `test_justification_does_not_degrade.py` — the ceiling was raised to 17.5 for "half a point of
  headroom on 16.9" and the build now measures 15.93, so the actual headroom is 1.57 and the ceiling
  permits a 33% degradation from the recorded baseline. Re-set to the current build plus the declared
  budget, and add an absolute companion (gap > 9 pt) so the rate cannot be met by a rising median.
- `test_aso_figures_are_vector_not_raster.py::test_the_deposited_figure_carries_live_text…` — `assert
  show` passes on one accidental two-byte `TJ` match in raw compressed bytes, and one figure already
  has two. Scope to inflated content streams and require a count commensurate with the label set.
- `test_aso_sequence_manifest_joins.py::test_the_tables_print_duplex_figures…` — floor of 8 against a
  current yield of 36. Raise it or express it as a fraction of sequence-bearing rows.
- `test_every_ordering_route_carries_the_same_verdict.py` FASTA/table tests silently `continue` when the
  CSV join fails and never assert the join succeeded. Assert joined-record count equals defline count.
- `test_no_page_is_nearly_empty.py::test_the_caption_footnotes_are_classed…` asserts one occurrence
  where the documented fix classed nine. Assert the count against the `**Table n.` openers.
- `test_build_submission_pdf.py::test_front_matter_captures_whole_paragraphs_not_first_lines` pins an
  exact tail string that has been re-typed five times in three days. Assert the abstract crosses its
  source wrap (word count, or a span straddling a known line break) instead. **The abstract changed
  again this session.**
- `test_paired_numeric_lists_are_bound_in_the_right_order.py` matches exactly one sentence in the whole
  manuscript. Widen the verb set; drop `, so the` from the blacklist needle.
- `test_aso_submission_numbers.py` inline `if os.path.exists(...)` blocks at lines 730, 784, 1355, 1659
  report PASS on a checkout missing the artifact, not even a skip. `pytest.fail` on absence.
- `test_aso_coverage_ladder.py` `pytest.skip(fifth["_unavailable"])` lets the guarded data switch off
  its own guard. Fail instead.
- `test_aso_coverage_ladder.py::test_the_manuscripts_best_supported_figure…` never asserts the
  complement its docstring promises ("and no other"), which is how the C1 BLOCKER survived.
- `test_aso_independent_verification.py` asserts typed constants against the committed artifact and
  never compares a live run to it. Assert `good["checks"] == _art()["checks"]`.
- `test_aso_figure_text_fits.py` measures only childless, unanchored, untransformed `<text>` nodes and
  never asserts anything was measured. Assert a minimum measured-element count per figure.
- `test_aso_archive_manifest_vocabulary.py::test_the_committed_manifest_agrees_with_what_is_on_disk`
  compares `[] == []` three times. Hash-compare the generated `screen_coverage` block.
- `test_display_items_are_cited_in_order.py::_body` strips from the FIRST "## Figure legends" heading to
  end of file, guarded by a 20,000-char floor against a 189 KB article. Express the floor as a fraction.
- `test_clustered_intervals_are_computed_not_typed.py` is the strongest file in the set; its only
  weakness is a dangling needle that leaves the contrast value unpinned.

---

# ALREADY APPLIED THIS SESSION — DO NOT REDO

- `aso_parent_null.py` gained `SECONDARY_CUT_BP = 7`: every ensemble now carries an `at_7bp` block and
  the artifact carries a `cut_sensitivity` block with observed counts and junction-level clearance at
  both cuts. Regenerated. Key measured values: at 7, observed 175/190 (92.1%), 9 of 38 junctions clear,
  exon-terminus null 91.4%, scramble null 74.3%, uniform 75.1%, NR4A3 arm observed 38.4% against a
  46.6% null (it reverses).
- Abstract rewritten (399 words against the 400 bound): carries both cut readings with the null moving
  too, the §2.9 credit side, "clearing the screen" at 35 of 38, and the leads' parent runs no longer
  described as "their own".
- §2.5: the seven-base-pair reading now carries the junction-level collapse and the measured nulls at
  seven; `CAGGGCATATCTTGCA` carries its ⚑ verdict; a new paragraph gives the own-parent decomposition
  (85 of the 87 pair one of the design's own two parent genes; two do not, both inside the FET
  paralogue family; the leads' sub-threshold 8 and 9 bp runs are against *TFG*).
- §2.7: the five published-breakpoint junctions now carry "at seven, none clears; at eight, two do";
  the *TCF12* e7 candidate names seven rather than "a stricter cut".
- §3: the designability sentence carries three-at-ten / 29-at-seven / 32-at-any-length.
- §2.4: five of the nine near-match-clean designs carry ⚑ inline with the class statement; the
  depth-surviving `GGCATATCAAGCGCTG` carries its verdict inline.
- §2.10: the CpG paragraph now states the phosphorothioate gap runs against the wing modification;
  the sole rule-passing design carries its ⚑ verdict; 5-methyl-dC is named as the zero-cost removal.
- §6 Design: full chemistry specification — β-D-oxy-LNA named, all 15 linkages PS and stereorandom,
  locked C as 5-methylcytosine, gap C as unmethylated dC, free 5′-OH/3′-OH, sodium salt.
- §2.7: the repeat-mask baseline corrected (54.1% N-free per base; the units mismatch stated; the
  one-sided conclusion stated).
- §6: the −7.77 parent seam restated as a structural floor of the top-margin class (all 38 divide 8/8
  and share the *NR4A3* exon-3 octamer; it is the more stable seam for 25 of 38; class range −7.77 to
  −12.60 against the 190-design panel's −17.51 / −8.66 median).
- §2.9: two "falls from" sign-convention inversions fixed.
- §4.4: the per-window scramble range restated as Monte-Carlo noise with the measured dispersion; the
  scramble control now requires matched geometry and dinucleotide-preserving composition and is scoped
  to the backbone-class component of toxicity; the positive control now requires matched 5-6-5
  β-D-oxy-LNA phosphorothioate geometry.
