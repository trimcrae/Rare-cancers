---
id: DOC-FUSION-JUNCTION-ASO-REDTEAM-ROUND3
title: "Round-3 pre-deposit review of the fusion-junction ASO submission — a verification pass against the artifacts, and four disclosure findings"
level: L3
kind: manuscript
status: live
canonical_for:
  - the round-3 pre-deposit review of the fusion-junction ASO submission manuscript
purpose: >
  Hold the pre-deposit quality review of fusion-junction-aso-research-article.md, run 2026-08-14
  against the committed tree, with every number re-derived from the artifacts rather than read from
  the prose. Its reason for existing is the same as round 2's: a review whose findings are applied
  but not recorded gets re-run from scratch, and its wrong leads get re-raised. It exists separately
  from round 2 because it was run at a different depth — round 2 asked whether the claims were
  supported, this one asks whether the paper is ready to be posted.
scope: >
  Verification of the manuscript's arithmetic against its artifacts, and disclosure findings on the
  submitted text and its display items. "The wet-lab experiment was not done" is never a finding
  here. No screen was re-run and no artifact was regenerated: every figure below is read from a file
  already committed.
audience: [external reviewers, maintainers, autonomous research agents]
related: [DOC-FUSION-JUNCTION-ASO-SUBMISSION, DOC-FUSION-JUNCTION-ASO-REDTEAM-ROUND2, DOC-FUSION-JUNCTION-ASO-PREPRINT-CHECKLIST]
date: 2026-08-14
last_verified: 2026-08-14
---

# Round-3 pre-deposit review of the fusion-junction ASO submission

> ⚠ **EVERY §-REFERENCE BELOW PREDATES THE ROUND-4 RENUMBER AND POINTS AT THE OLD SECTIONS.**
> [Round 4](./fusion-junction-aso-paper-redteam-round4.md) §3 carries the map — in short, old §3.5
> is now §3.4, old §3.6 is §3.5, old §3.7 and §3.11 are §3.6, old §3.8 split into §3.7 and §3.8,
> and old §4 split into §4, §5 and §6. Nothing in this review's findings changed; only where the
> paper keeps them.
>
> **Rounds 1 and 2** are [`fusion-junction-aso-paper-redteam.md`](./fusion-junction-aso-paper-redteam.md)
> and [`fusion-junction-aso-paper-redteam-round2.md`](./fusion-junction-aso-paper-redteam-round2.md).
> Nothing below re-raises a finding from either, and the four items round 2 left open under "what
> the review did not settle" are graded here rather than restated.
>
> **Method.** Every quantitative claim in the manuscript was re-derived from the committed artifacts
> by direct read, not by re-running any screen. Where the repository already holds a test that
> asserts a number, the test was run rather than the number recomputed by hand. The paper's own
> gates were run in full, including the two that are CI-only and therefore invisible to a routine
> `preflight.sh`.

---

## The verification pass: what was checked and what it found

⭐ **No arithmetic error was found.** Every headline number in the manuscript reproduces from the
artifacts exactly. This is worth stating plainly, because it is the outcome the previous two rounds
did not have, and because the findings below are all disclosure findings rather than corrections —
none of them changes a number the paper reports.

Re-derived directly from the artifacts and matching the manuscript exactly:

| claim | manuscript | re-derived |
|---|---|---|
| junction space | 231 pairs → 38 frame-compatible | 38 junctions × 5 registers = 190 design records ✓ |
| designs screened at default depth | 183 | 190 − 7 remote-service failures ✓ |
| designs screened at both depths | 180 | 190 − 7 default failures − 3 deep failures ✓ |
| deeper ceiling raises the count | 164 of 180 | 164 ✓ |
| …of those, never near the 50-hit cap | 129 | 129 ✓ |
| censoring partition | 35 capped + 101 over retention = 136 | 35 + 101 = 136 ✓ |
| mature-parent duplex ≥10 bp | 87 of 190 | 87 ✓ |
| …against wild-type *NR4A3* | 61 | `which_parent_supplies_it.NR4A3` = 61; the six parents sum to 87 ✓ |
| …by gap-level margin | 50/76, 29/76, 8/38 | 50/76, 29/76, 8/38 ✓ |
| parent pre-mRNA, hybridisable and gap-paired | 19 of 190 | `with_hybridisable_gap_paired` = 19 ✓ |
| genome scan span | 2,948,609,696 windows over 3.10 × 10⁹ nt | `windows_scanned` = 2,948,609,696; 1,594,222,653 / 0.5143 = 3.100 × 10⁹ ✓ |
| exact-match stratum | 1.37 expected, 236 observed over 176 | 1.37305, 236, 176 ✓ |
| observed-over-expected | median 0.98, 14 of 176 above 2× | 0.975, 14 ✓ |
| repeat split | 52.5% of hits masked, genome 51.4% | 0.5247, 0.5143 ✓ |
| named parent/paralogue gap-paired site | 20 of 176 | `n_designs_with_a_named_gap_paired_site` = 20 ✓ |
| the two secure candidates' genome load | 0.33 and 0.24 of expectation; 0.06 and 0.04 gap-paired; ranks 26 and 13 | 0.330, 0.238; 0.0568, 0.0367; ranks 26, 13 of 176 ✓ |
| lead reagent's genome load | 0.69 and 0.62 of expectation | 1062/1550.18 = 0.685; 371/598.651 = 0.620 ✓ |
| junctions with a design clearing the parent screen | 35 of 38, the exceptions *TAF15* e14, *TCF12* e3, *TFG* e2 | 35; exactly those three ✓ |
| the seven default-depth failures all return at depth | six dirty, one clean (`GGGCATATCAAGCGCT`) | all seven screened at depth; six carry hybridisable hits, `GGGCATATCAAGCGCT` returns n=3, hybridisable 0 ✓ |

The chance null was re-derived from first principles rather than read: 16-mers within two
substitutions of a given 16-mer number 1 + 16·3 + C(16,2)·3² = **1,129**, so
1,129 / 4¹⁶ = **2.63 × 10⁻⁷**; against the scan's measured 718,571,139-nucleotide span that predicts
**188.9** near-matches at ≥14/16 and, at ≤1 mismatch (49 / 4¹⁶), **8.20** per design. The manuscript
reports 1,129, 2.6 × 10⁻⁷, 189 and 8.2.

**Gates.** All nine preflight gates and both CI-only gates were run. `lint_consistency` 0 ERROR;
`systems_check --check` 0 ERROR; `emc_systems_map_check` OK; `lint_citations` OK; `lint_style` OK
(the manuscript is in its `TARGETS`); `parser_guard` OK; `validate-registry` OK; **`lint_claims`
0 ERROR with no warning against this manuscript**; `submission_citations.py --check` reports 39
annotated citations over 35 distinct PMIDs with 0 unannotated superscripts; `aso_figure_provenance.py
--check` clean over 2 artifacts and 9 rendered files; `junction_aso_thermo.py --check` reproduces the
committed artifact. The six ASO test modules run **137 passed, 0 failed, 0 skipped**.

⚠ **That figure is a measurement of the environment as much as of the code, and the first reading was
wrong in a way worth recording.** Run in this sandbox as found — no `numpy`, no `biopython`, no
`pytest` — the same six modules reported *89 passed, 1 skipped, 1 failed*. Installing the missing
dependencies took the same six modules to 137 passed: **46 tests had not been failing, they had not
been running**, and the one visible failure was
`test_the_16mer_thermo_artifact_still_reproduces` refusing to grade without the nearest-neighbour
table — the module declining to fabricate, not a defect. A partial suite that reports a pass count is
the failure mode CLAUDE.md §7 already names; it is recorded here because **the count a reviewer would
have quoted from a bare sandbox run understates the coverage by a third.**

References: 35 entries, superscripts run 1–35 with no gaps. Six tables present, three figures each as
SVG, PDF and PNG.

---

## Findings

Ordered by how much they bear on what a reader would take from the paper. **None is an arithmetic
error and none changes a reported number.** Three are disclosure gaps against the paper's own
standard; the fourth is a display-item problem.

### 1 · The lead reagent has a hybridisable site in a wild-type parent gene, and the paper does not say so

⛔ **This is the one finding that touches the paper's headline recommendation.**

`5′-GGGCATATCATCAAAC-3′` at *EWSR1* exon 12 is the design §4 puts forward for synthesis, the design
the multi-partner result of §3.2 rests on, and the subject of Figure 2. Two independent screens
place a near-match for it in wild-type ***TAF15***:

| screen | locus | mismatches | gap mismatches | gap fully paired | orientation | compartment |
|---|---|---|---|---|---|---|
| parent pre-mRNA arm | *TAF15* | 2 | **1** | no | forward — hybridisable | **intron–exon spanning** |
| genome-wide arm | *TAF15*, chr17:35,838,545 | 2 | **1** | no | sense, `required_transcript_strand: +` | **intron–exon spanning**, 0 nt to the nearest splice site |

The two arms found it independently, at the same locus, and the pre-mRNA arm records it at all three
of the seams this molecule spans (*EWSR1* e12, *TAF15* e11, *FUS* e10).

**Why it appears in no count in the paper.** Every parent-liability count the manuscript reports
requires the catalytic gap to be *fully* paired: §3.8's 19 of 190, §3.8's 20 of 176, and the
mature-parent screen's 87 of 190 all filter on `gap_fully_paired == true`. This site is one gap
mismatch short of that condition, so it falls outside all three and is reported nowhere.

⛔ **The problem is that the paper explicitly refuses the rule those counts implement.** The Methods
say, of the binary assumption that any mismatch inside the gap abolishes cleavage, that it "is not
supported by the primary literature and is not used for any claim of cleanliness", and cite ≈5-fold
as the single-mismatch bound — that is, a single gap mismatch leaves roughly a fifth of the
cleavage, not none. §3.7 applies exactly that reasoning on the transcript side, naming *H2AP*
"whose single mismatch falls inside the catalytic gap and which the pessimistic bound therefore
counts in full". So the graded principle is applied in the transcript compartment and a binary rule
is applied in the two parent compartments — which are the compartments the paper argues are
decisive.

**Mechanistically this is the same class as the finding §3.8 calls the paper's central one.** The
nine *NR4A3* intron-2/exon-3 sites are described there as "a route to wild-type engagement that does
not pass through the fusion at all, in the compartment where RNase-H1 is active, and it is the
discrimination question this paper is about". The *TAF15* site is that same route — parent gene,
nuclear compartment, spanning the boundary — differing only by one gap position.

**And it is not incidental. It is the multi-partner result's own cost.** §3.2 explains that one
oligonucleotide spans three seams because *EWSR1*, *TAF15* and *FUS* are identical over the ten
donor bases before the breakpoint. The same ten-base homology is what puts this molecule against
wild-type *TAF15*'s own sequence. **The property that buys three-partner coverage is the property
that creates the parent liability**, which is the paper's own thesis — that the parents are what
consume the designs — arriving one layer deeper than the paper takes it.

⚠ **The sentence a reader will rely on.** §4 reports the reagent's load as "recounting to six gene
loci, all at the screen's loosest admitted identity and **none on a parent transcript** (§3.7)".
That is true of the mature-transcript screen it cites. Read as written, and next to §3.2's "occurs
in none of the six wild-type parent transcripts", it will be taken as *no parent liability* — which
the pre-mRNA arm contradicts.

**Recommended disposition.** Not a withdrawal: the site is 2 mismatches with 1 in the gap, no
measurement here says it is cleaved, and the reagent's other properties are unchanged. Disclose it
where the load is discussed, in one sentence, and let it carry the point it actually makes. Proposed
text for §4, after the existing "none on a parent transcript (§3.7)" clause:

> The parent compartments qualify that. The same design carries a hybridisable, intron–exon-spanning
> near-match in wild-type *TAF15* pre-mRNA at two mismatches, one of them inside the catalytic gap,
> found independently by the pre-mRNA and genome-wide arms; it falls outside every parent count
> reported here because those require the gap to be paired in full, and under the graded bounds this
> paper adopts a single gap mismatch does not abolish cleavage. It is the multi-partner result's own
> cost: the ten donor bases shared across *EWSR1*, *TAF15* and *FUS* that let one oligonucleotide
> span three seams are the bases that place it against wild-type *TAF15*.

### 2 · The intermediate parent class is never given a number

The same gate that hides the site above hides a class. Re-derived from
[`aso-premrna-offtarget.json`](../../modalities/aso-premrna-offtarget.json):

| class | designs | reported in the paper |
|---|---|---|
| any parent pre-mRNA near-match | 53 of 190 | yes, §3.8 |
| hybridisable | **40** | no |
| hybridisable **and** gap fully paired | 19 of 190 | yes, §3.8 |
| **hybridisable but not fully gap-paired** | **21** | **no** |

Of the 28 sites those 21 designs carry, **26 are one gap mismatch short** and 2 are two short — and
**5 are in *NR4A3* itself**, the transcript the modality exists to spare. The paper steps from 53 to
19 with nothing in between, so the reader cannot see that the drop is a threshold choice rather than
a measurement.

The mature-parent screen has the same shape: `aso_parent_gap_pairing.py` only considers windows
pairing the whole gap, so a parent duplex missing one gap position is not counted anywhere either.
The 10-bp threshold in that screen *is* disclosed as "a stated threshold, not a measured one" with
every design's raw longest run released; **the full-gap-pairing condition is not disclosed the same
way**, though it is the stricter of the two.

**Recommended disposition.** One sentence in §3.8 and one clause in the Limitations. The numbers are
already computed and need no new run.

### 3 · Tables 2 and 3 display default-depth zeros that the Results withdraw

The Results are explicit that default-depth counts are lower bounds, and §3.5 names designs that
returned zero at the default ceiling and 27, 29 and 84 at ten times it. **Tables 2 and 3 are still
the default-depth result**, and three Table 2 rows print a clean cell for a design the deeper screen
shows is not:

| Table 2 row | design | default cell | at the deeper ceiling |
|---|---|---|---|
| *TCF12* e17 | `GGGCATATCTCTATAA` | n=8, **0 hybridisable, 0 gap-spanning loci** | n=118, **101 hybridisable, 14 gap-spanning hits at 5 loci** |
| *TFG* e6 | `GGGCATATCTTCAATC` | n=37, ≥2 hybridisable, **≤0 gap-spanning loci** | n=238, **193 hybridisable, 29 gap-spanning at 3 loci** |
| *FUS* e7 | `GGGCATATCACCAAAT` | n=34, ≥8 hybridisable, **≤0 gap-spanning loci** | n=141, **107 hybridisable, 30 gap-spanning at 4 loci** |

Across the corpus **7 designs read clean at default depth and carry hybridisable hits at depth**.
Table 3 has the same problem by construction: nine rows, every one printing `0` hybridisable and `0`
residual cleavage load, six of which the paper's own headline withdraws. Both captions disclose this
in prose — Table 3's says so in its first sentence — but a display item is what a reader scans, and
these two currently read against the text that surrounds them. `GGGCATATCTCTATAA` is the sharpest
case: §4 names it as withdrawn and carrying 14 gap-spanning risks, while Table 2 shows it with none.

⚠ Round 2 recorded this as open — *"Re-baselining Table 2 and the corpus counts against this is the
largest edit still outstanding"* — and it is still outstanding. **The data to close it is committed**:
all 38 junctions and 187 design records at the deeper ceiling, no hit list truncated.

**Recommended disposition.** Either regenerate Tables 2 and 3 at the deeper ceiling, or add a
deep-ceiling column to each so no row can be read against its own caption. The second is cheaper and
keeps the default-depth figures the corpus counts were computed at, which is the reason Table 3 gives
for retaining them.

### 4 · "187 design records" is never reconciled with the 190-design panel

§3.5 and §4 both describe the deeper pass as "38 junctions and 187 design records, none truncated".
The panel is 190. The missing three failed at the deeper ceiling and carry no deep count:

| junction | design | status at depth | at default depth |
|---|---|---|---|
| *FUS* e5 | `CAGGGCATATCTCCAC` | screen failed | 23 near-matches |
| *FUS* e5 | `GCATATCTCCACCTCC` | screen failed | 41 near-matches |
| *TFG* e2 | `AGGGCATATCTTCATC` | screen failed | 31 near-matches |

**Nothing follows from it scientifically** — all three were already far from clean at the default
depth, so no candidate is hidden and no count changes. It is a disclosure gap only, and it is below
the paper's own standard: the seven default-depth failures are disclosed explicitly in §3.5, and the
one undecided re-screen is disclosed in §3.6. A reviewer who subtracts 190 − 187 will ask, and the
answer is better in the text than in a reply.

**Recommended disposition.** Half a sentence at the first use of 187.

---

## Pre-deposit blockers, and one thing to decide at the journal step

**Blocking the deposit, author-only.** Three placeholders are unresolved in the manuscript:
`ORCID: [to be inserted]` (line 32) and `[ARCHIVE DOI]` at lines 271 and 868. The
[checklist](./fusion-junction-aso-preprint-checklist.md) §2 already carries these as author tasks,
and the ordering it specifies matters: **reserve the Zenodo DOI before publishing the deposit**, so
the manuscript cites the DOI it will actually have.

**Not blocking, but decide before the journal step.** Measured by `submission_metrics.py`: main text
**9,754 words**, abstract **459 words**, 9 display items, 35 references. bioRxiv sets no limit on any
of these, so none of it blocks the preprint, and the checklist §3 defers the abstract cut
deliberately and for a good reason. Two notes for whoever picks the venue:

- **459 words is more than double every journal cap in play**, and the checklist's note that "the cut
  got bigger" is now measured — this is the figure to plan against, not the 265 it superseded.
- At 9,754 words the manuscript is long for an Article, not only for the Short Communication label
  round 2 retired. The filename and `running title` still read *short communication* while the cover
  letter asks for the Article type; harmless on bioRxiv, worth reconciling before a portal upload.

---

## Dispositions — all four applied, 2026-08-14

| # | disposition |
|---|---|
| 1 | **Applied.** §4 now discloses the *TAF15* pre-mRNA site where the reagent's load is discussed, states that it falls outside every parent count because those require the gap paired in full, and names it as the multi-partner result's own cost rather than an incidental hit. It also records that the *TAF15* exon-6 reagent carries no hybridisable pre-mRNA site, which separates the two reagents on something other than count for a second time. |
| 2 | **Applied.** §3.8 now reports the 40 / 19 / 21 split, that 26 of the 21's 28 sites are one gap mismatch short and five are in *NR4A3*, and that the step from 53 to 19 is a threshold rather than a measurement. The Limitations name the fully-paired condition as the binary rule the Methods otherwise decline, used as an inclusion criterion because no retrieved measurement grades a partly-paired parent duplex. |
| 3 | **Applied, in the generator.** `submission_tables._deep_lookup()` reads the deep screens through `aso_screen_sets.load_screens(GEOMETRY, BLAST_SCREEN, select=is_deep)` — content, not filename — and both tables gain three deeper-ceiling columns beside the default-depth ones rather than in place of them, because the default depth is where the corpus counts were computed. **Table 3 also gains a derived `survives` verdict**, computed from those columns rather than from a remembered list, so the table cannot come to disagree with §3.5 about which designs survive: it now renders 3 `yes` and 6 `no`. A design the deep pass did not return renders `—`, never `0`. |
| 4 | **Applied.** §3.5 now reconciles 187 against the panel's 190 at first use, naming the three failures and their default-depth counts so the reader can see none was a candidate. |

⛔ **AND THE FIRST ATTEMPT AT FINDING 3 BROKE A GUARD, WHICH IS THE MOST USEFUL THING IN THIS FILE.**
The deep measurement was first written as one cell, `84 / 83 / 1`, and
`test_graded_rescore_depth.py::test_no_residual_load_cell_pools_two_depths` failed the build. That
guard scans **every** cell of Table 3's design rows rather than the residual-load column alone,
because the defect it was written for — `31.4 / 101 / 0 / 0`, a default-depth re-score pooled with a
deep one — hid inside a cell shape that looks legitimate: `a / b` is the model-disagreement form and
is correct, so a reader cannot tell a pooled cell from a real one by looking. **Narrowing the guard
to one column would have made the new cell pass and would have re-opened the hole.** The separator
was the problem, so the three values now go in three columns and the guard is untouched.

⚠ **It was caught by the full suite and not by the targeted run.** A 298-test selection over the ASO
and manuscripts suites passed while this was broken, because `test_graded_rescore_depth.py` is a
modalities test that no selector reached. The preflight that caught it reported **1 failure NOT in
the sandbox baseline**, named in full — which is exactly what that baseline mechanism exists to do,
and the reason it stores a list rather than a count.

⚠ **One correction to this review's own text, recorded because it is the mistake it warns about.**
The finding-3 table first reported the deep figures for *TFG* e6 and *FUS* e7 as "0 hybridisable" at
the default depth and as 29 and 30 "hybridisable" at depth. Both were the wrong column:
`n_true_cleavage_risk` is the hybridisable **and** gap-spanning count, not the hybridisable one, and
those two rows print `≥2` and `≥8` hybridisable at default with `≤0` in the gap-spanning column. The
table above is corrected and uses the manuscript's own vocabulary. The paper had it right
throughout — §4 says `GGGCATATCTCTATAA` carries "101 hybridisable near-matches, 14 of them spanning
the catalytic gap", which is exactly what the artifact holds.

## What this review did not do

- **No screen was re-run and no artifact regenerated.** Every figure above is read from a committed
  file. Where a number depended on a field convention rather than a raw count — the minus-strand
  share of 738 of 1,677, the locus inflation of 2.25 — the repository's own passing test was taken
  as the verification rather than a hand recount, because a hand recount that guesses at a field name
  tests the guess.
- **The literature was not re-verified.** Round 2 recomputed every clinical figure and checked all
  identifiers against committed retrieval records, finding no fabricated PMID; `lint_citations`
  passes here and `submission_citations.py --check` reports every superscript anchored. Neither is a
  truth oracle — an anchored identifier is evidence of a fetch, not of correctness.
- **The two open items round 2 parked stay parked**, and neither blocks a preprint: `MIN_DUPLEX_BP = 10`
  is a stated threshold with every raw run released, and no screen artifact yet records the parameter
  values it ran under. The second is the one worth closing next, because it is the defect that let
  round 2's "tenfold retention depth" error survive.
