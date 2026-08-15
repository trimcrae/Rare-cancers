---
id: DOC-FUSION-JUNCTION-ASO-REDTEAM-ROUND2
title: "Round-2 adversarial review of the fusion-junction ASO submission — findings, dispositions, and the claims that were wrong on the data"
level: L3
kind: manuscript
status: live
canonical_for:
  - the round-2 red team of the fusion-junction ASO submission manuscript
purpose: >
  Hold the second adversarial review of fusion-junction-aso-research-article.md, run 2026-08-13 as
  five independent reviewers plus the maintaining agent's own pass, with the disposition of every
  finding and the evidence behind it. Its reason for existing is that a review whose findings are
  applied but not recorded gets re-run from scratch, and its wrong leads get re-raised — which is
  exactly what round 1 avoided by recording two of them.
scope: >
  Critique of the manuscript's claims, framing, internal consistency, arithmetic and methods. "The
  wet-lab experiment was not done" is never a finding here; "the write-up claims more than the
  finished analyses establish" is.
audience: [external reviewers, maintainers, autonomous research agents]
date: 2026-08-13
last_verified: 2026-08-13
---

# Round-2 red team of the fusion-junction ASO submission

> **Round 1** is [`fusion-junction-aso-paper-redteam.md`](./fusion-junction-aso-paper-redteam.md),
> against the 2026-06-26 working record. It is a different document with different section numbering
> and all of its findings were applied there; nothing below re-raises one.
>
> **Method.** Five reviewers ran in parallel against the committed tree, each with one lens —
> nucleic-acid chemistry and RNase-H1 enzymology; computational genomics and statistics; clinical
> sarcoma and the literature record; data integrity against the artifacts; handling editor for
> structure, register and length. Each was required to cite an artifact field, a code line or a
> recomputation for every finding, and forbidden to write "probably". **Every finding below was then
> re-verified independently before it was applied**, which is why three of them are in the wrong-leads
> section instead of in the paper.

---

## The one finding that produced new work rather than a correction

**A mature wild-type parent transcript can pair the whole catalytic gap, and none of the paper's
three screens could see it.** Raised by the chemistry reviewer, confirmed by recomputation, and now
its own screen: [`aso_parent_gap_pairing.py`](../../modalities/aso_parent_gap_pairing.py) →
[`aso-parent-gap-pairing.json`](../../modalities/aso-parent-gap-pairing.json), guarded by
[`test_aso_parent_gap_pairing.py`](../../modalities/tests/test_aso_parent_gap_pairing.py).

Why all three screens missed it, each verifiable in code:
1. the gap-resolved alignment screen drops parent-gene records outright
   (`junction_aso_offtarget.is_parent`, applied at `screen_one`) and filters at ≥14/16 identity —
   these duplexes run 8–13/16;
2. the exhaustive scan admits ≤1 mismatch, far stricter;
3. the pre-mRNA arm searches **unspliced** sequence, in which an exon is followed by an intron, so it
   structurally cannot reach a **mature** exon–exon junction. It found the wild-type *NR4A3*
   intron-2/exon-3 route and could not, by construction, find the mature exon-2/exon-3 one.

Measured over all 190 designs: **87 have a mature-parent duplex of ≥10 contiguous base pairs pairing
the whole six-nucleotide gap, 61 of them against wild-type *NR4A3***. It falls with the gap-level
margin — 50 of 76 at margin 1, 29 of 76 at margin 2, 8 of 38 at margin 3 — which is what the margin's
definition predicts, since at margin 1 a parent needs one lucky base to pair the whole gap and at
margin 3 it needs three.

⛔ **Five of the nine designs the paper called clean carry one, at 11–12 bp**, including
`5′-CAGGGCATATCTTGCA-3′` — the single design that passes all four conventional rules — **against
wild-type *NR4A3* itself**. Four do not, and those four are now the paper's honest candidate set.

**This is the margin's blind spot, not an unrelated risk.** The margin counts bases unique to the
fusion *at the seam*; it never asks whether a parent carries those bases elsewhere in its own
transcript. So the margin is a predictor of parent engagement rather than a guarantee against it, and
the paper now says so.

---

## Findings applied

Ordered by how much they changed what the paper claims.

| # | lens | finding | disposition |
|---|---|---|---|
| 1 | chemistry, maintainer | **The LNA caveat pointed the wrong way**, in the paper (×3), in `junction_aso_thermo.py` and in the artifact. It read "LNA raises affinity on the fusion and parent duplexes alike, compressing their difference, so the discrimination reported here is an upper bound." Two errors: equal *absolute* stabilisation leaves a *difference* unchanged rather than compressed; and it is not equal — because the seam lies strictly inside the gap, `n_donor` and `n_acceptor` are both in {6…10}, so **the fusion duplex pairs all ten LNA residues and each parent duplex exactly five**, for all 190 designs by construction. LNA therefore *widens* ΔΔG. | Corrected everywhere; the value is now stated as a conservative **floor**, and the superseded wording is registered in the module docstring and the artifact field per rule 1.2. Found independently by the chemistry reviewer and by the maintaining agent, from the same architecture argument. |
| 2 | comp-genomics | **The 50-hit BLAST ceiling censors counts far below 50**, so "hit list complete" was never established. The archive's own `-deep500` re-screens prove it: **all 23 re-screened designs grew, and 20 had not approached the cap** — 9→34, 10→110, and one reporting **15**, a count the pipeline treats as complete, returned **204**. | §3.6 now states that every alignment count is a lower bound whether or not it reached the cap, with those measurements; Table 3's caption no longer says "complete"; the Limitations say the 47 assessable designs are themselves bounds. The cleanliness claim was already resting on the exhaustive arm and still does. |
| 3 | clinical | **The one published *TCF12::NR4A3* breakpoint is exon-resolved and is the dirtiest junction in the panel.** PMID 11156374 reports a chimera retaining "the first 108 amino acids" of TCF12; in this transcript model 108 residues is *TCF12* exon 5 and no other exon (e4 = 74, e6 = 130). That junction carries **17 gap-spanning loci**, the highest in Table 2, and none of the four clean *TCF12* designs is at it. The Limitations had claimed *TCF12* fusions are reported "but not at the exon resolution these designs require". | §3.3 now reports it, as the same pattern the paper already handles well for *TAF15*: the seam patients carry is designable and dirty, the clean seams have no reported patient. Stated as an inference from a residue count, not as an exon reported as such. |
| 4 | chemistry, comp-genomics | **The "three independent instruments" are three functions of one variable.** `max(n_donor, n_acceptor) == 11 − gap_specificity_margin` holds for **190 of 190** designs, so ΔΔG is ordering the margin in kilocalories; and eight of the nine *NR4A3* pre-mRNA sites sit in the shortest-donor register. | §3.9 now says the agreement is arithmetic rather than corroboration, and §3.8 that the liability tracks the tiling register. Found independently by two reviewers with the same identity. |
| 5 | clinical | **"The two available bounds" ignored six gapmer-specific studies in the paper's own retrieval corpus**, all tagged `TO-VERIFY (a)` in `lit-targets-aso-verify.json`, while the two cited bounds are for unmodified chemistry. | Methods now cite PMID 28970564 (of 120+ gapmers across five SNPs, only two or three achieved preferential cleavage in cells) and PMID 42327837 (selectivity engineered by modifying a gap position). Both point the same way as the paper's conclusion and are far better architecture-matched than a 1995 unmodified-DNA result. |
| 6 | clinical | **The recommended reagent's stated load dropped its only curated-transcript hit.** §3.7 said "One locus, no curated transcript, from a raw count of nine". The sixth hybridisable hit is `NM_012274` (*H2AP*), plus-strand, with its single mismatch **inside the catalytic gap** — disarmed only by the binary rule the Methods explicitly disown. The graded artifact already counts it: 5.2 under the optimistic bound, 6.0 under the pessimistic. | Named in §3.7 and added to the predicted load that §4 says "should travel with" the reagent. |
| 7 | data integrity | "six of those seven annotated only as predicted gene models" at *TAF15* e6 is **five**. The intersection of `loci_with_a_gap_spanning_hit` (7) and `loci_seen_only_as_predicted_models` (6) is 5 — SIRT7 is predicted-only but not gap-spanning. Table 2 printed `7 | 5` correctly; the prose did not. | Corrected. |
| 8 | data integrity | "39 of the 40 screens released in total, the single exception being one coverage-only control" — the manifest records **45 screens committed, 44 gap-resolved, 39 graded**, so there are six exceptions: the coverage-only control and the five deeper re-screens. | Corrected. |
| 9 | comp-genomics | **The chance null is an expectation compared against a median.** Recomputed over the 176 plotted molecules: median 3, **mean 9.199**, max 100, with 51 above the band's 9.1. "It comes in marginally low … the null is over-predicting" was not supported. | §3.6 and the Figure 3 legend now report the mean at the band's upper end and the median at its lower, i.e. a long right tail rather than a shift below. The section's conclusion — load is at chance, so a low count is not evidence of good design — is unchanged. |
| 10 | comp-genomics | "Three designs return perfect 16/16 BLAST matches while the sense-only scan reports no exact match" is **ten** (19 design records, 10 distinct sequences, every such hit minus-strand). | Corrected — it strengthens the paper's own orientation corroboration threefold. |
| 11 | comp-genomics | "a donor coding phase of 1 … necessary and sufficient across all 231 rows" is false: **114 rows have phase 1 and only 38 are EMITTABLE**. Within the exon-3 column (77 rows) the equivalence does hold. | Corrected to "necessary and sufficient across its 77 rows, and necessary but not sufficient across all 231". |
| 12 | chemistry | **The backbone chemistry was never stated**, though every design rule audited (CpG/TLR9 especially) is a phosphorothioate-gapmer rule. | Methods now state a uniform phosphorothioate backbone; the Limitations add that no screen here addresses the sequence-independent liability class of that chemistry. |
| 13 | chemistry | The six-nucleotide gap was never justified and the single fixed architecture was not stated as a limitation. | Methods now give the rationale and note it admits exactly five registers per seam, "which is the whole design space explored here"; Limitations note nothing here bounds a longer gap. |
| 14 | chemistry, maintainer | **The Discussion applied a single-substitution bound to the parent case**, where the parent leaves half the oligonucleotide unpaired — an a-fortiori that runs backwards, since eight mismatches are easier to discriminate than one. | Rewritten: the bounds bound the near-match case, and no retrieved measurement bounds the parent case. |
| 15 | maintainer | **The physics route to the paper's own central uncertainty was never acknowledged**, though human RNase-H1·heteroduplex structures exist and the working record §8 specifies the calculation. | §4 now names it alongside a measurement, and says neither is attempted here. |
| 16 | clinical | The inhaled ASO phase 1 (PMID 39500647) was **32 healthy volunteers**, not patients. | Corrected. |
| 17 | clinical | "no retrieved record concerns a solid-tumour target" is false — `lit-targets-aso-delivery-routes.json` carries **68**, of which exactly **2** have clinical-stage language and neither is a trial. | Corrected to the true and more useful statement: an active preclinical field, not established in patients for this target. |
| 18 | clinical | Uncited clinical sentence ("Surgery … is the backbone of localised disease, and for advanced disease no agent is approved"); "FET-family partner" applied to *TCF12* and *TFG*, which are not FET proteins; "NR4A3 has tumour-suppressive roles of its own" resting on a *double*-knockout phenotype; "Next-generation sequencing of EMC" was six tumours; "by contrast" setting a response rate against an eligibility fraction. | All corrected; PMID 41055792 and 11156374 now cited where they belong. |
| 19 | clinical | The proposed experiment had lost two controls round 1 had added. | Three controls now named: housekeeping positive control, scrambled gapmer of matched chemistry, and a fusion-negative isogenic comparator, with the reason each is needed. |
| 20 | data integrity | "at a tenfold deeper ceiling **and retention depth**" — the ceiling went 50→500, but retention went 15→**305**, not 150. | Corrected. |
| 21 | data integrity | The archive manifest omitted `fusion-object-inventory.json`, which `junction_aso.plausible_nr4a3_resume_residues()` opens unconditionally — so the archive as manifested **could not regenerate the junction atlas**. Measured: `FileNotFoundError`. | Added to the manifest row for the atlas, with the reason. |
| 22 | editor | The submission was labelled a **Short Communication** at ~6,800 main words, six display items and 30 references — a desk-return on format before an editor reads a word. | Cover letter now asks for the **Article** type; the submission plan's stale "~6,000 words ✅ inside it" row, which graded the paper against a target belonging to a venue §1c had already eliminated, is corrected and registered. |
| 23 | editor | The orientation correction was narrated five times; the Limitations were ~60% restatement of §3.6 and Methods; the Results carried two accounts of superseded internal drafts; Figure 3's legend introduced ten designs reported nowhere else. | Cut. The superseded-draft narratives belong in this file and the working record, not in Results. |
| 24 | data integrity | `submission_citations.py --check` **was a no-op**: the module had only `--write` and a default that printed and returned 0, so an unrecognised flag exited 0 regardless of the numbering. | A real `--check` mode now compares every printed superscript against the number its identifiers imply and exits 1 with the offending superscript named; `test_the_check_flag_actually_checks` exercises both directions. |
| 25 | editor, chemistry | Register and copy: two different titles in one file; sentence-shaped section headings; "artefact"/"Artifacts" mixed; "RNase H1" in the keywords against "RNase-H1" throughout; "the design lane" (repository jargon); "Materials and methods" with no materials; ΔG°37 described as "computed at 250 nM strand concentration", which a standard-state free energy has no dependence on. | All corrected. |

---

## Claims that were WRONG ON THE DATA — recorded so they are not re-raised

⭐ **These are the reason every finding was re-verified rather than applied.** One of them would have
introduced the exact defect it alleged.

### ⛔ "The released thermodynamics code does not reproduce the released numbers, and feeds the RNA strand to a DNA-keyed table" — false, and acting on it would have broken the artifact

The chemistry reviewer rated this HIGH, reported that re-running `junction_aso_thermo.py` reproduces
"1 of 190" ΔΔG values, and proposed switching the computation from `target` to `anti`.

Three independent observations refute it:
1. **`python3 research/modalities/junction_aso_thermo.py --check` exits 0** — the committed code
   reproduces the committed artifact byte-for-byte. It did so before the review and after.
2. The three table entries the finding quoted are **misquoted**. Biopython's `R_DNA_NN1` has
   `TT/AA = (−11.5, −36.4)` and `AA/TT = (−7.8, −21.9)`; the finding attributed the first pair to
   `AA/TT`. Its `CA/GT` and `GT/CA` values were wrong in the same way.
3. Biopython's own `Tm_NN` docstring settles the convention: *"For RNA/DNA hybridizations seq must be
   the RNA sequence."* The code passes `target_mRNA_5to3` — the RNA strand — which is correct.
   Measured directly: the committed `dg37_fusion_duplex` of −21.371 reproduces from the target
   strand; the antisense strand gives −22.975.

**The suspicion did locate a real defect, in the justification rather than the number.** The Methods
had claimed the Tm cross-check "excludes" a reversed strand convention. It cannot: this module and
Biopython build the key the same way, so they agree on whatever strand they are handed. That sentence
is now replaced by the real reason the strand is right — the table's documented convention — with the
Tm check demoted to what it actually verifies, the summation. **A validation that cannot fail in the
direction it claims to test is not a validation.**

### "The `FUS` parent-name substring filter dropped real off-targets"

The code defect is real: `is_parent` matches gene aliases as uppercase substrings of the hit
definition, so "mitofusin 1", "vesicle fusing ATPase" and "BCR-ABL **fus**ion transcript" all return
True when the donor is *FUS*. But **measured exposure is nil** — 0 of 1,928 retained hits across the
non-*FUS* screens carry "FUS" or "TLS" in their definition. It is a code fix, not a correction to any
number, and it is recorded here rather than in the paper.

### "test_submission_citations.py passed while the numbering was broken"

Half right. `submission_citations.py --check` genuinely was a no-op (finding 24, fixed). But
`test_the_printed_numbers_are_the_ones_the_identifiers_imply` **does** compare every printed
superscript against the number its identifiers imply, and would have failed on the broken draft — it
simply was not run inside that window. The gap was in the command a human reaches for, not in the
suite.

### "§3.9's '11 minus the margin' identity fails for 173 of 190 designs"

Raised and self-retracted by the data-integrity reviewer, recorded because it is an easy mistake to
repeat: the identity is about the **thermo model's donor/acceptor split**, where
`max(n_donor_side, n_acceptor_side) == 11 − margin` holds 190 of 190. Testing it against the
mature-parent screen's `longest_parent_duplex_bp_through_gap` is testing a different quantity.

### Round-1 items re-checked and still sound

The `-gapres` provenance strings, the 2.20 locus inflation, the 738-of-1,677 minus-strand share, the
censoring partition (35 capped + 101 over retention = 136), the nine clean designs and their
sequences, and the pre-mRNA class split (9 *NR4A3* boundary + 10 *TCF12* intronic) were all
recomputed and confirmed. So were every clinical figure and all 31 PMIDs, each of which anchors to a
committed retrieval record — **no fabricated identifier was found**.

---

## ⛔ The follow-up measurement, and what it withdrew

Finding 2 said every alignment count is a lower bound. The obvious test was to run the deeper search
at the six junctions holding the nine designs the paper called clean — 30 queries, $0, the lane that
already produced the five `-deep500` files. It was dispatched the same session (run `31712344956`,
10.7 min, `screen_mode=deep_rescreen`, `suffix_tag=-clean9-deep500`) and **it withdrew most of the
paper's headline.**

Every hit list is complete at the deeper retention depth (`saved == n` for all nine), so these are
measurements rather than bounds:

| design | junction | n at ceiling 50 | n at 500 | hybridisable | gap-spanning | verdict |
|---|---|---|---|---|---|---|
| `AGGGCATATCGGAGTC` | *FUS* e8 | 3 | **3** | 0 | 0 | survives |
| `GGGCATATCCGACATG` | *TAF15* e1 | 5 | **5** | 0 | 0 | survives |
| `GGCATATCAAGCGCTG` | *TCF12* e7 | 2 | **2** | 0 | 0 | survives the re-screen, fails the parent screen (11 bp) |
| `GGGCATATCCGTGGAC` | *EWSR1* e1 | **0** | 27 | 18 | 0 | not clean |
| `GGCATATCCGTGGACG` | *EWSR1* e1 | **0** | 29 | 22 | 0 | not clean |
| `GCATATCCGTGGACGC` | *EWSR1* e1 | **0** | 84 | 83 | **64** | not clean |
| `GCATATCAAGCGCTGC` | *TCF12* e7 | 1 | 18 | 2 | 0 | not clean |
| `CAGGGCATATCTTGCA` | *TCF12* e9 | 7 | 67 | 18 | **11** | not clean |
| `GGGCATATCTCTATAA` | *TCF12* e17 | 8 | 118 | 101 | **14** | not clean |

⭐ **Three designs that returned ZERO near-matches at the default ceiling returned 27, 29 and 84.** A
count of zero was not a count of zero — the sharpest available form of finding 2, and not something
the reviewers predicted; they established that counts below the cap grow, and this shows the floor
case does too.

**It cost the paper both of its recommendations.** `GGGCATATCTCTATAA` at *TCF12* exon 17 was §4's
"cleanest available test of the mechanism alone" and carries 14 gap-spanning cleavage risks;
`CAGGGCATATCTTGCA`, the one design passing all four conventional rules, carries 11. Both are now
named in the paper as withdrawn rather than quietly dropped.

**Composed with the mature-parent screen, two designs survive everything**:
`5′-AGGGCATATCGGAGTC-3′` at *FUS* exon 8 and `5′-GGGCATATCCGACATG-3′` at *TAF15* exon 1 — and
neither junction has a published patient breakpoint. That is the paper's candidate set, and it is a
floor rather than a total, because the deeper search has not been run at the other 32 junctions.

⚠ **Note how the two screens interact, since neither alone is sufficient**: `GGCATATCAAGCGCTG` passes
the deeper re-screen and fails the parent screen; `GGGCATATCCGTGGAC` does the reverse. Only the
intersection is a candidate, which is why
`test_the_two_survivors_are_what_both_screens_leave` asserts the intersection rather than a
remembered pair.

---

## What the review did not settle

- ✅ **CLOSED — the other 32 junctions have had the deeper search.** Runs `31725944229` and
  `31725954785` covered them in two batches; with the earlier runs that is **38 of 38 junctions, 187
  design records, and no truncated hit list**. The censoring is corpus-wide rather than a quirk of
  the nine: of 157 comparable designs **141 return a higher count, and 125 of those never reached the
  50-hit cap**, median growth 4.1× and maximum 29×. Re-baselining Table 2 and the corpus counts
  against this is the largest edit still outstanding.
- ⚪ **The genome-wide compartment — instrument built, not yet run.** A scoping pass measured a
  prototype rather than estimating: an exhaustive ≤2-mismatch scan of GRCh38, both orientations,
  costs **17.9 min on one core** via a 2-bit-packed 537 MB membership bitmap, which fits the
  existing workflow's ceiling at $0. `aso_genome_offtarget.py` implements it, wired as
  `screen_mode: genome`.
  ⛔ **The `core_nt` attempt did not merely fail — it could not have succeeded.** That corpus has no
  defined nucleotide span, so no null can be formed against it, and its 50-hit cap sat *below* the
  null's own lower bound. It was not a failed measurement; it was an instrument with no reading to
  give. Both defects are structural, which is why a bigger cap would not have helped.
  ⛔ **And a raw genome-wide count must never be the deliverable.** Under the paper's own null,
  ≥14/16 over both strands predicts of order 10³ near-matches per 16-mer *for any 16-mer whatever*.
  Publishing that would re-commit at genome scale the error `offtarget_chance_baseline.py` already
  killed at transcriptome scale, and a reader would take it for a safety finding. The artifact is
  stratified for that reason: exact 16/16 (of order one expected per design, individually
  checkable), observed-versus-expected per design, the named-target lookup, and the repeat split
  that soft-masking gives free.
- **`MIN_DUPLEX_BP = 10`** in the new screen is a stated threshold, not a measured one. Every
  design's raw longest run is released so another threshold can be applied without re-running it.
- **No screen artifact records the parameter values it ran under** (`BLAST_HITLIST_SIZE`,
  `SAVED_HITS_PER_DESIGN`, `OLIGO_LEN`, `WING` are all env-overridable). That is what let the
  "tenfold retention depth" error survive, and recording them in each screen's `method` block would
  close it.
- **The deep artifacts landed on `modalities-cache`, not the branch that dispatched the run.** They
  were pulled onto this branch and committed in the same change, because an artifact the paper
  depends on that lives only on a cache branch is the CLAUDE.md §7 failure exactly.
