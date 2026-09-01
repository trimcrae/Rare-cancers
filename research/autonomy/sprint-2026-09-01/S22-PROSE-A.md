---
id: DOC-SPRINT-S22-PROSE-A
title: "S22-PROSE-A — splitting the over-ceiling prose in the vaccine-path and fusion-output papers"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S22-PROSE-A — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S22-PROSE-A — over-ceiling sentence splitting, PUB-VACCINE-PATH and PUB-FUSION-OUTPUT

**Item(s):** the readability worklist in [`S5-READABILITY.md`](./S5-READABILITY.md) (AUT-PD-142 blast radius)
**Started / Finished (UTC):** 2026-09-01T19:30:35Z / 2026-09-01T19:53:49Z

## Owned paths — named before any edit, per the seat prompt

- `research/manuscripts/neoantigen/` — the vaccine-path document is
  **`research/manuscripts/neoantigen/emc-vaccine-development-path.md`** (PUB-VACCINE-PATH; S5's table
  row: 18 over-ceiling before and after the splitter fix, longest 108 w, all real prose).
  The directory also holds `fusion-junction-neoantigen-paper.md` (PUB-NEOANTIGEN, 4 real) and
  `hla-coverage-emc.md` (PUB-HLA-COVERAGE, 4 real).
- **`research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md`**
  (PUB-FUSION-OUTPUT; S5's table row: 15 real over-ceiling, longest 89 w).
- `research/autonomy/sprint-2026-09-01/S22-PROSE-A.md` (this file).

⛔ **Not touched:** `degrader/nr4a3-degrader-paper.md`, `program/emc-treatment-roadmap.md`, anything
under `care-delivery/`, §B3 of the vaccine paper, and `neoantigen/hla-coverage-emc.md` — the last
because `git status` showed another seat had it open (see "What I could not do").

## Verdict

**FIXED (partial by design).** Over-ceiling sentences: PUB-FUSION-OUTPUT **15 → 0**, PUB-NEOANTIGEN
**4 → 0**, PUB-VACCINE-PATH **19 → 4**, and every one of the remaining four is either §B3 material I
was told to leave alone or a linter extraction artefact — **none is un-split prose I declined to
work on.** 33 sentences were split. **Caution markers are byte-identical before and after in all
three papers** (194 → 194, 171 → 171, 36 → 36), and no number, PMID, accession or citation moved.

---

## What I measured

### 1 · The worklist (the fixed linter, on the live tree)

```
$ python3 research/manuscripts/lint_readability.py --report <the four owned manuscripts>
document                                             sent  mean  p90  max  >60w  FKGL  caution/1kw
emc-vaccine-development-path.md                       695  24.4   45  108    18  13.2         11.5
nr4a3-fusion-transcriptional-output.md                462  25.8   49   89    15  13.2         15.7
fusion-junction-neoantigen-paper.md                   158  23.3   40   80     4  13.6         12.2
hla-coverage-emc.md                                   110  23.4   44   80     4  14.0         11.7
```

Matches S5's table exactly, so the row is **not refuted** — the defect is real prose and still there.
The per-sentence worklist with line numbers came from `lint_readability.body()`/`sentences()` called
directly; that list, not the count, was the work queue.

### 2 · Three of the flags were NOT prose — two distinct extractor defects, both new

⛔ **Neither is the splitter fix from AUT-PD-142. Both live upstream of it and both are still open.**

**(a) `body()` deletes a sentence-terminating numeral that a line wrap put at column 0.**
`lint_readability.py:136` applies `re.sub(r"^\s*\d+\.\s+", "", t)` **per line**, to strip ordered-list
markers. These manuscripts are hard-wrapped, so a sentence ending `… as internal residue 266.` whose
wrap puts `266.` at the start of the next line has that token **deleted**, and the two sentences are
glued and reported at their combined length. The discriminating observation — identical prose, only
the wrap differs:

```
266. at line start -> [32]   "… as internal residue Four of the five in-frame junctions place aspartate …"
266. mid-line      -> [19, 14]  "… as internal residue 266."  /  "Four of the five in-frame junctions …"
```

That is the whole of `emc-vaccine-development-path.md`'s remaining Figure-1-legend flag (64 w
reported; **19 w + 14 w real, both far under the ceiling**). I did not reword it: the prose is
correct and the instrument is not, and reflowing a line to clear a bar would be clearing the bar
without fixing the instrument. Ledger row proposed below.

**(b) The deliberate "no sentence opens with a digit or a lowercase letter" exclusion is false for
this corpus.** S5 pinned that exclusion as a negative test on the argument that a false split
understates a length — sound in direction, and the premise is wrong on three live sentences:

| document | glued at | reported | real parts |
|---|---|---:|---:|
| `nr4a3-fusion-transcriptional-output.md` | `… **NR4A occupancy** (§3.11). 110 published NR4A …` | 63 w | 3 w + 60 w |
| `nr4a3-fusion-transcriptional-output.md` | `… might substitute for one. 110 NR4A peak sets …` | 74 w | 28 w + 46 w |
| `fusion-junction-neoantigen-paper.md` | `… and 4 \`OUT_OF_FRAME\`. **e11** is among the refusals …` | 80 w | 47 w + 27 w |

(The third opens with a lowercase identifier only after `body()` strips the emphasis markers.)
⭐ **These three I DID fix in the prose**, because "don't start a sentence with a bare numeral" is
ordinary scientific-writing advice and the recast is meaning-neutral: `110 published NR4A ChIP-seq
peak sets — … — were intersected with …` became `The scan intersected 110 published … peak sets — …
— with …`; `110 NR4A peak sets — … — were intersected` became `All 110 …`; `**e11** is among the
refusals` became `**And e11 is among the refusals**`. Ledger row proposed below all the same, because
the exclusion will mis-measure the next such sentence.

### 3 · The honesty check — caution counted marker by marker, not per 1000 words

`lint_readability._CAUTION` matches itemised against the pre-edit text (reconstructed by
reverse-applying every edit, so the comparison is against MY baseline and not against another seat's
concurrent work):

| paper | caution markers before | after | markers that changed |
|---|---:|---:|---|
| `emc-vaccine-development-path.md` | 194 | **194** | none |
| `nr4a3-fusion-transcriptional-output.md` | 171 | **171** | none |
| `fusion-junction-neoantigen-paper.md` | 36 | **36** | none |

And a token-level audit over numbers, PMIDs, PMCs, GSE/GPL/PRJNA/SRP accessions, bracketed citation
markers and HLA alleles found **zero value changes** in any of the three papers — every difference
was punctuation attached to a token (`0.5,` → `0.5.`) where a semicolon became a full stop.

### 4 · Gates (scoped to my change, per charter §6)

| gate | result |
|---|---|
| `lint_readability.py --check` on the fusion-output and neoantigen papers | ✅ **OK** — "no sentence over 60 words, no caution lost" |
| `lint_readability.py --check` on the vaccine paper | ⛔ FAIL, 4 sentences — **all four are deferred B3 material or defect (a)**; itemised below |
| `lint_claims.py` on all three | **0 ERROR**, 10 WARN → 11 WARN (the one new WARN analysed below) |
| `lint_style.py` on the vaccine paper (it is a `TARGETS` file) | 1 ERROR, `bold-midsentence` `**less**` — **pre-existing and not mine**; reproduced on the pre-edit text |
| `lint_consistency.py` | ✅ 0 ERROR across 26 target files |
| `lint_citations.py` / `lint_citation_types.py` | ✅ 0 error; the one retraction advisory is in a file I did not touch |

**The new `lint_claims` WARN is a per-sentence-window artefact, not a strengthened claim.** R4
(`confirm/establish/validate`) has `clears_on="disclaimer"` and is evaluated **per sentence**. Before
my split, "The experimentally validated fusion-junction epitopes …" sat in the same 79-word sentence
as its own disclaimer ("a handful of epitopes **is not a set** against which a threshold can be
calibrated"), which cleared it. Splitting moved the disclaimer into the next sentence, so the
regex no longer sees it. The count of the word `validated` in the file is **6 before and 6 after**,
and the disclaimer is still the very next sentence. I left it: rewording to fit a regex's sentence
window is the metric-as-target failure `scientific-writing` §5 exists to stop.

**⚠ `lint_style` on the vaccine paper is red on `**less**` at line 655, and it is not mine.** That
bold sits inside §B3, in the sentence S20-VACCINE-RECONCILE is rewriting tonight
("the **less** adverse of the two configurations"). Reproduced on my pre-edit copy at the equivalent
line, and the string `less` appears **zero times** in my edit set. **It is the current holder's to
clear, and the driver should not attribute it to this seat.**

---

## What I changed

| path | words before | after | Δ | over-ceiling before → after |
|---|---:|---:|---:|---|
| `research/manuscripts/neoantigen/emc-vaccine-development-path.md` | 20,941 | 20,951 | **+10** | 19 → **4** |
| `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md` | 17,340 | 17,351 | **+11** | 15 → **0** |
| `research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md` | 5,068 | 5,067 | **−1** | 4 → **0** |

⛔ **Two of the three papers are longer, by +10 and +11 words (+0.05% and +0.06%), and I am reporting
that rather than buying it back.** Splitting a compound sentence costs a subject and a verb wherever
the second half was an elliptical clause; the only ways to return to zero were to delete a clause or
to strip a qualifier, which is the one failure the seat brief and `scientific-writing` §4 both name.
Fourteen of the 33 splits are exactly neutral (a semicolon became a full stop and a conjunction went
away), and nine are net negative.

⚠ The vaccine paper's "before" is **20,941 words, not the 20,410 at `HEAD`** — S20-VACCINE-RECONCILE
added ~530 words to §B3 and the abstract while I was measuring. My before/after is computed against
the tree as I read it, so the +10 is mine and the ~530 is not.

### The audit table — every sentence changed, original beside replacement

⭐ Generated by re-splitting both versions with `lint_readability.sentences()` and diffing the
sentence lists, so it is the instrument's own reading of what changed, not my recollection of it.
Word counts are post-extraction (inline code and emphasis markers stripped), which is why a
manifest sentence of backticked filenames reads short.

#### PUB-VACCINE-PATH — `research/manuscripts/neoantigen/emc-vaccine-development-path.md`

```text
--- change 1 (before line 56) ---
  BEFORE [61w] Class I binding was predicted with MHCflurry 2.1.4, models release 2.2.0 [2], on a ten-allele panel for the junction screen and a 34-allele panel for the coverage scan, calling a peptide strong at a presentation percentile of 0.5 or below; class II binding with MHCnuggets [12] on 23 class II alleles across DR, DP and DQ at 100 and 1000 nM.
  BEFORE [77w] Coverage is the union carrier frequency of the presenting alleles over Allele Frequency Net Database records [1]; the sampling model a pooled binomial would require does not hold, so no confidence interval is placed on it and three other readings are reported in its place: the exact within-locus form of the coverage expression, distribution-free Fréchet bounds on the between-locus dependence the formula assumes away, and the empirical spread of the same quantity recomputed inside each source population.
  AFTER  [41w] Class I binding was predicted with MHCflurry 2.1.4, models release 2.2.0 [2], on a ten-allele panel for the junction screen and a 34-allele panel for the coverage scan; a peptide is called strong at a presentation percentile of 0.5 or below.
  AFTER  [21w] Class II binding used MHCnuggets [12] on 23 class II alleles across DR, DP and DQ at 100 and 1000 nM.
  AFTER  [17w] Coverage is the union carrier frequency of the presenting alleles over Allele Frequency Net Database records [1].
  AFTER  [19w] The sampling model a pooled binomial would require does not hold, so no confidence interval is placed on it.
  AFTER  [40w] Three other readings are reported in its place: the exact within-locus form of the coverage expression, distribution-free Fréchet bounds on the between-locus dependence the formula assumes away, and the empirical spread of the same quantity recomputed inside each source population.

--- change 2 (before line 70) ---
  BEFORE [76w] In place of the confidence interval withdrawn from earlier versions, the pooled figure is bounded three ways: the exact within-locus form raises it by 0.33 percentage points, so it cannot be too high for that reason; Fréchet bounds place it in [17.5%, 29.9%] under any linkage disequilibrium whatever; and recomputed inside each of the 112 source populations that measured the whole presenting panel it has a median of 24.5% and a range of 0% to 66.0%.
  AFTER  [17w] In place of the confidence interval withdrawn from earlier versions, the pooled figure is bounded three ways.
  AFTER  [19w] The exact within-locus form raises it by 0.33 percentage points, so it cannot be too high for that reason.
  AFTER  [12w] Fréchet bounds place it in [17.5%, 29.9%] under any linkage disequilibrium whatever.
  AFTER  [27w] Recomputed inside each of the 112 source populations that measured the whole presenting panel, it has a median of 24.5% and a range of 0% to 66.0%.

--- change 3 (before line 145) ---
  BEFORE [74w] Peptide-specific cytotoxic T cells were induced in some patients, delayed-type hypersensitivity responses were absent in both trials, half the 12 patients on the arms combining peptide with incomplete Freund's adjuvant and interferon-alpha had stable disease during the vaccination period, and one patient in that series developed an intracerebral haemorrhage after the second vaccination; an accompanying evaluation of the later trial concluded that no robust immune response to the target epitope had been shown [19].
  AFTER  [18w] Peptide-specific cytotoxic T cells were induced in some patients, and delayed-type hypersensitivity responses were absent in both trials.
  AFTER  [36w] Half the 12 patients on the arms combining peptide with incomplete Freund's adjuvant and interferon-alpha had stable disease during the vaccination period, and one patient in that series developed an intracerebral haemorrhage after the second vaccination.
  AFTER  [21w] An accompanying evaluation of the later trial concluded that no robust immune response to the target epitope had been shown [19].

--- change 4 (before line 266) ---
  BEFORE [69w] The four read-through tracts are 9, 9, 31 and 9 residues long before a premature stop, yielding 97 distinct 8- to 11-mers in total; and three of the four — those from EWSR1 exons 6, 8 and 14 — converge on the identical eight-residue core YALRPSPI, differing only in the seam residue, because a frameshift into the same acceptor exon reads the same nucleotides in the same shifted register.
  AFTER  [24w] The four read-through tracts are 9, 9, 31 and 9 residues long before a premature stop, yielding 97 distinct 8- to 11-mers in total.
  AFTER  [44w] Three of the four — those from EWSR1 exons 6, 8 and 14 — converge on the identical eight-residue core YALRPSPI, differing only in the seam residue, because a frameshift into the same acceptor exon reads the same nucleotides in the same shifted register.

--- change 5 (before line 368) ---
  BEFORE [65w] A threshold chosen because it raises coverage would be the same defect this paper exists to name, arriving from the other side; the 28 alleles at a percentile of 5 are not a better answer than the 4 at 0.5, they are a demonstration that the question "what fraction of patients could this reach?" has no answer until somebody defends a cut, and nobody has.
  AFTER  [22w] A threshold chosen because it raises coverage would be the same defect this paper exists to name, arriving from the other side.
  AFTER  [18w] The 28 alleles at a percentile of 5 are not a better answer than the 4 at 0.5.
  AFTER  [25w] They are a demonstration that the question "what fraction of patients could this reach?" has no answer until somebody defends a cut, and nobody has.

--- change 6 (before line 546) ---
  BEFORE [79w] The experimentally validated fusion-junction epitopes in the literature are individual sequences across a few fusions, the HLA-A\24:02-restricted SYT-SSX junction peptide [17,18], the four EWSR1::FLI1 breakpoint peptides of the Ewing sarcoma case report [20] and the fusion neoantigens of a head and neck series [21], and a handful of epitopes is not a set against which a threshold can be calibrated; calibrating on point-mutation neoantigens instead would import an assumption about junction peptides that is the very thing in question.
  AFTER  [44w] The experimentally validated fusion-junction epitopes in the literature are individual sequences across a few fusions: the HLA-A\24:02-restricted SYT-SSX junction peptide [17,18], the four EWSR1::FLI1 breakpoint peptides of the Ewing sarcoma case report [20] and the fusion neoantigens of a head and neck series [21].
  AFTER  [15w] A handful of epitopes is not a set against which a threshold can be calibrated.
  AFTER  [19w] Calibrating on point-mutation neoantigens instead would import an assumption about junction peptides that is the very thing in question.

--- change 7 (before line 598) ---
  BEFORE [108w] The sentence "a negative result would be close to decisive" appeared in an earlier version of this section and was doing no work, because a null eluate bounds nothing until three quantities are fixed in advance: a stated limit of detection in peptide copies per cell, so that "not presented" is separated from "below the instrument"; a stated number of independent specimens and their HLA types, since the lead peptide is presented on one allele and a specimen not carrying it cannot test the claim; and a positive control peptide of known abundance eluted in the same run, without which a null is indistinguishable from a failed elution.
  AFTER  [36w] The sentence "a negative result would be close to decisive" appeared in an earlier version of this section and was doing no work, because a null eluate bounds nothing until three quantities are fixed in advance.
  AFTER  [23w] The first is a stated limit of detection in peptide copies per cell, so that "not presented" is separated from "below the instrument".
  AFTER  [32w] The second is a stated number of independent specimens and their HLA types, since the lead peptide is presented on one allele and a specimen not carrying it cannot test the claim.
  AFTER  [25w] The third is a positive control peptide of known abundance eluted in the same run, without which a null is indistinguishable from a failed elution.

--- change 8 (before line 907) ---
  BEFORE [64w] That pathway has since been read in the same two EMC cohorts and the reading does not carry the analogy across: the linker and core-protein modules are higher in EMC than in the comparator sarcomas on both platforms, the backbone-polymerisation and 4-O-sulfotransferase modules disagree between platforms, the sulfate-donor module is lower on both, and three sulfotransferase modules fall below the read's own readability floor.
  AFTER  [21w] That pathway has since been read in the same two EMC cohorts and the reading does not carry the analogy across.
  AFTER  [43w] The linker and core-protein modules are higher in EMC than in the comparator sarcomas on both platforms, the backbone-polymerisation and 4-O-sulfotransferase modules disagree between platforms, the sulfate-donor module is lower on both, and three sulfotransferase modules fall below the read's own readability floor.

--- change 9 (before line 962) ---
  BEFORE [74w] Twelve archival EMC tumours profiled by whole-transcriptome targeted sequencing carry more B-cell infiltration in the low-risk half of the series than in the high-risk half, and proof-of-concept multiplex immunofluorescence on two of the specimens reports exhausted CD3+CD8+PD1+ T cells and FOXP3+ regulatory T cells in the high-risk one; the authors state that every immunofluorescence comparison is a within-specimen region-of-interest analysis, that their prognostic model overfits, and that the work is exploratory and hypothesis-generating [15].
  AFTER  [25w] Twelve archival EMC tumours profiled by whole-transcriptome targeted sequencing carry more B-cell infiltration in the low-risk half of the series than in the high-risk half.
  AFTER  [22w] Proof-of-concept multiplex immunofluorescence on two of the specimens reports exhausted CD3+CD8+PD1+ T cells and FOXP3+ regulatory T cells in the high-risk one.
  AFTER  [26w] The authors state that every immunofluorescence comparison is a within-specimen region-of-interest analysis, that their prognostic model overfits, and that the work is exploratory and hypothesis-generating [15].

--- change 10 (before line 1000) ---
  BEFORE [64w] A construct of that shape has been made and administered once already: the Ewing sarcoma vaccine was an off-the-shelf multi-peptide product spanning a recurrent breakpoint rather than a per-patient design [20], and routine fusion analysis in a clinical genomics workflow finds EWS breakpoints clustered tightly, with about three quarters of Ewing sarcoma and desmoplastic small round cell tumours sharing one exon 7 motif [22].
  AFTER  [31w] A construct of that shape has been made and administered once already: the Ewing sarcoma vaccine was an off-the-shelf multi-peptide product spanning a recurrent breakpoint rather than a per-patient design [20].
  AFTER  [32w] Routine fusion analysis in a clinical genomics workflow finds EWS breakpoints clustered tightly, with about three quarters of Ewing sarcoma and desmoplastic small round cell tumours sharing one exon 7 motif [22].

--- change 11 (before line 1049) ---
  BEFORE [66w] The antiangiogenic component addresses B7 by a mechanism — vascular normalisation reduces the physical and vascular barriers to lymphocyte entry — and antiangiogenic tyrosine kinase inhibitors carry the most consistent prospective signal in this disease: pazopanib gave an objective response in 4 of 22 evaluable patients with a median progression-free survival of about 19 months [11], and a sunitinib series reported activity in translocated EMC [13].
  AFTER  [19w] The antiangiogenic component addresses B7 by a mechanism: vascular normalisation reduces the physical and vascular barriers to lymphocyte entry.
  AFTER  [45w] Antiangiogenic tyrosine kinase inhibitors carry the most consistent prospective signal in this disease — pazopanib gave an objective response in 4 of 22 evaluable patients with a median progression-free survival of about 19 months [11], and a sunitinib series reported activity in translocated EMC [13].

--- change 12 (before line 1057) ---
  BEFORE [70w] The checkpoint half of that backbone has never been given alone in a reported EMC cohort, and one patient has been reported outside one: a man with EWSR1::NR4A3 EMC, microsatellite stable at a tumour mutational burden of 0.67 mut/Mb and with TSC2 loss, whose microenvironment a commercial assay profiled as immune-enriched and fibrotic with high PD-L1, and who received single-agent pembrolizumab with a near-complete response reported over 15 cycles [16].
  AFTER  [24w] The checkpoint half of that backbone has never been given alone in a reported EMC cohort, and one patient has been reported outside one.
  AFTER  [35w] The patient was a man with EWSR1::NR4A3 EMC, microsatellite stable at a tumour mutational burden of 0.67 mut/Mb and with TSC2 loss, whose microenvironment a commercial assay profiled as immune-enriched and fibrotic with high PD-L1.
  AFTER  [13w] He received single-agent pembrolizumab with a near-complete response reported over 15 cycles [16].

--- change 13 (before line 1191) ---
  BEFORE [67w] The binder counts and every coverage figure derived from them depend on an acceptance threshold this paper does not defend, and no multiplicity correction is applied anywhere: 174 peptides were screened against 10 and then 34 alleles at two thresholds, with no decoy control and no null expectation, so the calls that pass are reported as what the screen returned rather than as an enrichment over chance.
  AFTER  [27w] The binder counts and every coverage figure derived from them depend on an acceptance threshold this paper does not defend, and no multiplicity correction is applied anywhere.
  AFTER  [22w] The screen tested 174 peptides against 10 and then 34 alleles at two thresholds, with no decoy control and no null expectation.
  AFTER  [19w] The calls that pass are therefore reported as what the screen returned rather than as an enrichment over chance.

--- change 14 (before line 1259) ---
  BEFORE [108w] Every figure in Sections 2 and 3 is generated by a script in and is committed as a JSON artifact beside it: for the junction set and predicted binders, for population coverage, for the coverage-versus-allele-count curve, for the coverage-versus-threshold curve of Section 2.3, for the proteome search of Section B5, for the out-of-frame screen of Section 2.2, for the near-self search of Section B3, for the second-predictor check, for the within-locus form, the Fréchet bounds and the between-population spread of Section 2.3, for the one-residue pre-screen of Section B5 and its validation, and for the per-patient shortlisters, and for the candidate construct and its minimal synthetic long peptide.
  AFTER  [22w] Every figure in Sections 2 and 3 is generated by a script in and is committed as a JSON artifact beside it.
  AFTER  [25w] The junction and coverage figures come from (the junction set and predicted binders), (population coverage), (the coverage-versus-allele-count curve) and (the coverage-versus-threshold curve of Section 2.3).
  AFTER  [26w] The screens come from (the proteome search of Section B5), (the out-of-frame screen of Section 2.2), (the near-self search of Section B3) and (the second-predictor check).
  AFTER  [40w] The rest come from (the within-locus form, the Fréchet bounds and the between-population spread of Section 2.3), (the one-residue pre-screen of Section B5 and its validation), and (the per-patient shortlisters) and (the candidate construct and its minimal synthetic long peptide).
```

#### PUB-FUSION-OUTPUT — `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md`

```text
--- change 1 (before line 198) ---
  BEFORE [61w] It is a seven-platform series — seven sibling print runs of one clone library — of which only GPL3290 carries a usable EMC-versus-comparator contrast, so the 10 versus 6 here is not the whole deposit; and the published Subramanian cohort was 10 EMC against 26 other sarcomas, so a reader opening the accession will find comparators this analysis does not use.
  AFTER  [35w] It is a seven-platform series — seven sibling print runs of one clone library — of which only GPL3290 carries a usable EMC-versus-comparator contrast, so the 10 versus 6 here is not the whole deposit.
  AFTER  [25w] The published Subramanian cohort was 10 EMC against 26 other sarcomas, so a reader opening the accession will find comparators this analysis does not use.

--- change 2 (before line 264) ---
  BEFORE [64w] Four known answers were graded before any biological read: ENO3 (UP on both platforms — the positive control), NR4A3 (UP — tumour identity), PLAGL1 (DOWN, PMID 16112421 — the directional falsifier, the only prediction an arm-wide offset cannot manufacture) and SGK1 (flat or down at transcript level despite 10/10 protein positivity, PMID 16756948 — the only row whose published transcript and protein directions oppose).
  AFTER  [9w] Four known answers were graded before any biological read.
  AFTER  [19w] The first two are ENO3 (UP on both platforms — the positive control) and NR4A3 (UP — tumour identity).
  AFTER  [45w] The other two are PLAGL1 (DOWN, PMID 16112421 — the directional falsifier, the only prediction an arm-wide offset cannot manufacture) and SGK1 (flat or down at transcript level despite 10/10 protein positivity, PMID 16756948 — the only row whose published transcript and protein directions oppose).

--- change 3 (before line 305) ---
  BEFORE [63w] NR4A occupancy (§3.11). 110 published NR4A ChIP-seq peak sets — ChIP-Atlas, ReMap2022 and the Haller et al. acinic cell carcinoma deposit — were intersected with the class-A genes' regulatory windows, the same window as the motif scan, so the sequence and occupancy axes ask about one region, and every count placed against a background panel of 198 genes assembled for an unrelated question.
  AFTER  [3w] NR4A occupancy (§3.11).
  AFTER  [45w] The scan intersected 110 published NR4A ChIP-seq peak sets — ChIP-Atlas, ReMap2022 and the Haller et al. acinic cell carcinoma deposit — with the class-A genes' regulatory windows, the same window as the motif scan, so the sequence and occupancy axes ask about one region.
  AFTER  [16w] Every count was placed against a background panel of 198 genes assembled for an unrelated question.

--- change 4 (before line 430) ---
  BEFORE [68w] Stated at the weight it deserves: one of the five, PLAGL1 on GPL6244, is inside its null band and is therefore sign-concordant but not a reading at this power, and the two SGK1 cells agree by way of a prediction ("flat or down") that an inside-the-band reading satisfies — so those cells could not have refused the prediction downward, and their bands are printed above for that reason.
  AFTER  [29w] Stated at the weight it deserves: one of the five, PLAGL1 on GPL6244, is inside its null band and is therefore sign-concordant but not a reading at this power.
  AFTER  [37w] The two SGK1 cells agree by way of a prediction ("flat or down") that an inside-the-band reading satisfies, so those cells could not have refused the prediction downward, and their bands are printed above for that reason.

--- change 5 (before line 490) ---
  BEFORE [63w] First, the control role tested one proposition only — is it up on both platforms — and everything that separates ENO3 from PPARG and SEMA3C here was not part of it: the exact permutation p, invariance across five comparator strata, the reference-pool-matched contrast, the matrix adjustment, the 3SEQ percentile, the muscle control and the NBRE enrichment could each have failed and did not.
  AFTER  [31w] First, the control role tested one proposition only — is it up on both platforms — and everything that separates ENO3 from PPARG and SEMA3C here was not part of it.
  AFTER  [32w] The exact permutation p, invariance across five comparator strata, the reference-pool-matched contrast, the matrix adjustment, the 3SEQ percentile, the muscle control and the NBRE enrichment could each have failed and did not.

--- change 6 (before line 661) ---
  BEFORE [74w] The EWSR1-NR4A3 set is too sparse for its zero to be a reading — it recovers 2 of 203 promoters in a background gene panel assembled for an unrelated question, so a chosen gene could not have been recovered either — and the TAF15-NR4A3 co-location does not clear a null that slides the same four-site configuration, at its true spacing, to a random offset within the same window (p = 0.08, 20,000 seeded draws).
  AFTER  [39w] The EWSR1-NR4A3 set is too sparse for its zero to be a reading: it recovers 2 of 203 promoters in a background gene panel assembled for an unrelated question, so a chosen gene could not have been recovered either.
  AFTER  [32w] The TAF15-NR4A3 co-location does not clear a null that slides the same four-site configuration, at its true spacing, to a random offset within the same window (p = 0.08, 20,000 seeded draws).

--- change 7 (before line 701) ---
  BEFORE [69w] Why a screen of retrieved full text could not reach it is worth recording, because the shape recurs: in a pooled screen the perturbation identity is data rather than metadata, so appears zero times in that paper's abstract and zero times across all 24 of the series' GEO sample records, and this project's prior chromatin census was antigen-centric with a ChIP-seq-only method vocabulary, which no ATAC deposit can satisfy.
  AFTER  [18w] Why a screen of retrieved full text could not reach it is worth recording, because the shape recurs.
  AFTER  [32w] In a pooled screen the perturbation identity is data rather than metadata, so appears zero times in that paper's abstract and zero times across all 24 of the series' GEO sample records.
  AFTER  [19w] This project's prior chromatin census was also antigen-centric with a ChIP-seq-only method vocabulary, which no ATAC deposit can satisfy.

--- change 8 (before line 719) ---
  BEFORE [65w] Across GEO, SRA, BioProject, BioSample, ArrayExpress/BioStudies, ENA and ChIP-Atlas, searched on 2026-08-08, an EMC disease term returns zero deposits carrying any chromatin library strategy; the 46 SRA runs an EMC term does return are every one RNA-Seq, WXS, WGS, Targeted-Capture or CAGE; and ChIP-Atlas's complete antigen index carries NR4A3 in one cell type only (CD1c⁺ dendritic cells) and EWSR1 in seven, none of them EMC.
  AFTER  [24w] Across GEO, SRA, BioProject, BioSample, ArrayExpress/BioStudies, ENA and ChIP-Atlas, searched on 2026-08-08, an EMC disease term returns zero deposits carrying any chromatin library strategy.
  AFTER  [18w] The 46 SRA runs an EMC term does return are every one RNA-Seq, WXS, WGS, Targeted-Capture or CAGE.
  AFTER  [22w] ChIP-Atlas's complete antigen index carries NR4A3 in one cell type only (CD1c⁺ dendritic cells) and EWSR1 in seven, none of them EMC.

--- change 9 (before line 735) ---
  BEFORE [74w] The available surrogates were then measured rather than dismissed, because "no fusion cistrome" invites the reasonable objection that some NR4A chromatin data exists and might substitute for one. 110 NR4A peak sets — from ChIP-Atlas, ReMap2022, and the Haller et al. acinic cell carcinoma deposit described below — were intersected with the class-A genes' regulatory windows, the same −10 kb/+15 kb window as the motif scan, so the two axes ask about one region.
  AFTER  [28w] The available surrogates were then measured rather than dismissed, because "no fusion cistrome" invites the reasonable objection that some NR4A chromatin data exists and might substitute for one.
  AFTER  [47w] All 110 NR4A peak sets — from ChIP-Atlas, ReMap2022, and the Haller et al. acinic cell carcinoma deposit described below — were intersected with the class-A genes' regulatory windows, the same −10 kb/+15 kb window as the motif scan, so the two axes ask about one region.

--- change 10 (before line 800) ---
  BEFORE [89w] ENO3 is supported by every instrument that returned a reading: both array platforms under an exact permutation test and after multiple-testing correction; every comparator stratum separately, including the myxoid-matched and reference-pool-matched arms; 75% of its delta retained under matrix adjustment on the platform where that covariate differs, and 100% on the platform where it does not; the top 2% of 14,120 genes in an independent cohort on an unrelated technology; flat muscle markers that are more muscle-restricted than it is; and more exact NBREs than its own composition-matched null.
  AFTER  [10w] ENO3 is supported by every instrument that returned a reading.
  AFTER  [26w] Both array platforms support it under an exact permutation test and after multiple-testing correction, as does every comparator stratum separately, including the myxoid-matched and reference-pool-matched arms.
  AFTER  [23w] Matrix adjustment retains 75% of its delta on the platform where that covariate differs and 100% on the platform where it does not.
  AFTER  [39w] It is in the top 2% of 14,120 genes in an independent cohort on an unrelated technology, the muscle markers are flat and more muscle-restricted than it is, and it carries more exact NBREs than its own composition-matched null.

--- change 11 (before line 856) ---
  BEFORE [69w] It does not reach a study registered in the Sequence Read Archive that was never given a GEO series, and one such study is public: / , 12 FFPE EMC tumour BioSamples, released 2025-11-11, all 12 runs downloadable, with per-sample break-apart FISH status (8 positive, 4 negative), site, size and morphology — larger than any cohort read here, and carrying the per-sample fusion annotation none of the three has.
  AFTER  [25w] It does not reach a study registered in the Sequence Read Archive that was never given a GEO series, and one such study is public.
  AFTER  [46w] It is / : 12 FFPE EMC tumour BioSamples, released 2025-11-11, all 12 runs downloadable, with per-sample break-apart FISH status (8 positive, 4 negative), site, size and morphology — larger than any cohort read here, and carrying the per-sample fusion annotation none of the three has.

--- change 12 (before line 954) ---
  BEFORE [68w] (b) is now partly measured rather than conceded: the GPL6244 comparator arm is 23/29 myxoid, so it is largely matched to EMC on matrix architecture, and ENO3 is unchanged against the myxoid-only arm (+0.808, p = 8 × 10⁻⁵); adjusting for an 11-gene matrix proxy chosen to contain no EMC-selected gene leaves 75% of its delta where the covariate differs between arms and 100% where it does not.
  AFTER  [8w] (b) is now partly measured rather than conceded.
  AFTER  [31w] The GPL6244 comparator arm is 23/29 myxoid, so it is largely matched to EMC on matrix architecture, and ENO3 is unchanged against the myxoid-only arm (+0.808, p = 8 × 10⁻⁵).
  AFTER  [29w] Adjusting for an 11-gene matrix proxy chosen to contain no EMC-selected gene leaves 75% of its delta where the covariate differs between arms and 100% where it does not.

--- change 13 (before line 969) ---
  BEFORE [83w] Class A is three genes wide; nothing has been deposited on EMC material under any chromatin library strategy, so no experiment has measured where an NR4A3 fusion binds or what chromatin does in EMC chromatin — while the same archives hold chromatin maps for EWSR1::WT1, EWSR1::ATF1, EWSR1::FLI1, FUS::DDIT3 and HEY1::NCOA2, and hold one accessibility screen carrying four NR4A3 fusions in HEK293T (GSE243553); and the 110 NR4A peak sets that do exist are measured — not assumed — to be unable to substitute (§3.11).
  AFTER  [6w] Class A is three genes wide.
  AFTER  [29w] Nothing has been deposited on EMC material under any chromatin library strategy, so no experiment has measured where an NR4A3 fusion binds or what chromatin does in EMC chromatin.
  AFTER  [25w] The same archives, meanwhile, hold chromatin maps for EWSR1::WT1, EWSR1::ATF1, EWSR1::FLI1, FUS::DDIT3 and HEY1::NCOA2, and one accessibility screen carrying four NR4A3 fusions in HEK293T (GSE243553).
  AFTER  [21w] And the 110 NR4A peak sets that do exist are measured — not assumed — to be unable to substitute (§3.11).

--- change 14 (before line 1043) ---
  BEFORE [61w] This is a ceiling on the disease, not on the search: a term search of GEO returned 56 records, of which 22 were series or curated datasets, every one was read at sample level, and none was a fourth EMC expression cohort — the seventeen unrelated sarcoma and chondrosarcoma deposits among them carry no EMC sample between them (§3.13, Table 10).
  AFTER  [11w] This is a ceiling on the disease, not on the search.
  AFTER  [31w] A term search of GEO returned 56 records, of which 22 were series or curated datasets; every one was read at sample level, and none was a fourth EMC expression cohort.
  AFTER  [18w] The seventeen unrelated sarcoma and chondrosarcoma deposits among them carry no EMC sample between them (§3.13, Table 10).

--- change 15 (before line 1131) ---
  BEFORE [68w] The one genome-wide chromatin readout that carries NR4A3 fusions at all reads accessibility in HEK293T (GSE243553), not occupancy in EMC chromatin, and cannot close the gap; nor can the existing NR4A chromatin data stand in for it, since across 110 peak sets — including four deep NR4A3 cistromes in acinic cell carcinoma, a disease driven by wild-type NR4A3 — no class-A gene carries occupancy beyond a background panel.
  AFTER  [26w] The one genome-wide chromatin readout that carries NR4A3 fusions at all reads accessibility in HEK293T (GSE243553), not occupancy in EMC chromatin, and cannot close the gap.
  AFTER  [41w] Nor can the existing NR4A chromatin data stand in for it: across 110 peak sets — including four deep NR4A3 cistromes in acinic cell carcinoma, a disease driven by wild-type NR4A3 — no class-A gene carries occupancy beyond a background panel.
```

#### PUB-NEOANTIGEN — `research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md`

```text
--- change 1 (before line 38) ---
  BEFORE [77w] Breakpoint-resolved prediction (junctions derived at the transcript level from real Ensembl exon structure, MHCflurry-2.0) grades all 27 declared exon pairs and emits 5 in-frame junctions (EWSR1 exons 7/9/10/12/13 → NR4A3 exon 3) yielding 11 distinct predicted binders, 4 of them strong, with no single pan-EMC epitope: the most-shared candidate appears in 4 of 5 junctions and is a weak binder, three of the five junctions return no strong binder at all, and every strong binder is breakpoint-specific.
  AFTER  [46w] Breakpoint-resolved prediction (junctions derived at the transcript level from real Ensembl exon structure, MHCflurry-2.0) grades all 27 declared exon pairs and emits 5 in-frame junctions (EWSR1 exons 7/9/10/12/13 → NR4A3 exon 3) yielding 11 distinct predicted binders, 4 of them strong, with no single pan-EMC epitope.
  AFTER  [31w] The most-shared candidate appears in 4 of 5 junctions and is a weak binder, three of the five junctions return no strong binder at all, and every strong binder is breakpoint-specific.

--- change 2 (before line 86) ---
  BEFORE [75w] If such a peptide is presented on MHC, a T-cell response against it is the cleanest possible selectivity for EMC: it spares wild-type NR4A3 and EWSR1 at the sequence level — ⚠ NOT every normal cell, which no test here has assessed, and — because the fusion is the truncal, clonal driver present in every tumour cell and never subclonally lost — it cannot be escaped by antigen loss the way a passenger-mutation response can.
  AFTER  [42w] If such a peptide is presented on MHC, a T-cell response against it is the cleanest possible selectivity for EMC: it spares wild-type NR4A3 and EWSR1 at the sequence level — ⚠ NOT every normal cell, which no test here has assessed.
  AFTER  [31w] And because the fusion is the truncal, clonal driver present in every tumour cell and never subclonally lost, it cannot be escaped by antigen loss the way a passenger-mutation response can.

--- change 3 (before line 107) ---
  BEFORE [71w] Not because the biology is unknown, but because the steps past "know the variant" are hard, and they are exactly the honest caveats of §6: the breakpoint varies between patients (no single off-the-shelf product), the junction is mostly self-sequence (only the seam is foreign, so central tolerance may have pruned reactive T cells), sarcomas are low-mutational-burden "cold" tumours, and a bespoke per-patient product for an ultra-rare cancer has weak commercial pull.
  AFTER  [25w] Not because the biology is unknown, but because the steps past "know the variant" are hard, and they are exactly the honest caveats of §6.
  AFTER  [46w] The breakpoint varies between patients (no single off-the-shelf product), the junction is mostly self-sequence (only the seam is foreign, so central tolerance may have pruned reactive T cells), sarcomas are low-mutational-burden "cold" tumours, and a bespoke per-patient product for an ultra-rare cancer has weak commercial pull.

--- change 4 (before line 155) ---
  BEFORE [80w] The other 22 are explicit refusals carried in the artifact's , not silent omissions — 9 (NR4A3 exon 2 carries no CDS; a fusion to it retains 176 nt of 5′UTR before NR4A3's ATG), 9 (NR4A3 exon 4 resumes at residue 318, outside the corrected plausible range), and 4 . e11 is among the refusals: it is the only declared donor cut that falls on a codon boundary, so it is precisely the one the two coordinate systems disagree about.
  AFTER  [50w] The other 22 are explicit refusals carried in the artifact's , not silent omissions — 9 (NR4A3 exon 2 carries no CDS; a fusion to it retains 176 nt of 5′UTR before NR4A3's ATG), 9 (NR4A3 exon 4 resumes at residue 318, outside the corrected plausible range), and 4 .
  AFTER  [31w] And e11 is among the refusals: it is the only declared donor cut that falls on a codon boundary, so it is precisely the one the two coordinate systems disagree about.
```

---

## What I deferred, and why — the four sentences still over the ceiling

All four are in `emc-vaccine-development-path.md`. **None of them is prose I judged too hard.**

| line | words | why it stands |
|---:|---:|---|
| 639 | 87 | §B3, the anchor-position sentence ("Position 1 and position 5 face outward …"). S20-VACCINE-RECONCILE is rewriting this material tonight and a third seat found the near-self null turns on whether position 1 counts as an anchor. **Off limits by the seat brief, and it grew from 70 w to 87 w under that seat while I worked** — evidence the material is live. |
| 71 | 85 | The abstract's near-self sentence, which now carries the position-1 qualifier ("… though six of the 11 would if position 1 counted as an anchor, which no allele-specific motif held here can settle"). This *states the B3 result*; off limits for the same reason. It was 51 w at my first reading and is 85 w now — again, not mine. |
| 1204 | 63 | "The near-self search of B3 is the one analysis here that carries a null …" — the B3 null itself, named explicitly in the brief. |
| 1253 | 64 | **Not a sentence.** Extractor defect (a) above: 19 w + 14 w of correct prose, glued because a line wrap put `266.` at column 0. Reporting it is the fix; rewording the prose is not. |

⭐ **So PUB-VACCINE-PATH's clause-7 exposure is now three B3 sentences and one linter bug.** Once
S20 lands and defect (a) is fixed, the split needed to clear the clause is small and well-specified —
and the three B3 sentences must be split by whoever owns that claim, because two of them carry the
qualifier the whole reconciliation is about.

## What I could not do, and what it is actually waiting on

- **`neoantigen/hla-coverage-emc.md` (PUB-HLA-COVERAGE) — deliberately not taken, and it turned out
  not to need me.** The seat brief gives me the `neoantigen/` directory, but `git status` showed the
  file already `M` alongside `shared-vs-individualized-neoantigen-evidence.md` and
  `emc-vaccine-path-aixiv-metadata.json`, i.e. another seat was working across that directory. Two
  seats writing one file in one tree is a lost write, not a merge, so I left it.
  ⭐ **Re-measured at 19:56Z before writing this sentence rather than after: it now reads 0
  over-ceiling (longest 59 w) and `--check` is green** — S5's 4 were cleared by that seat while I
  worked. Nothing is owed here.
- **Nothing else is blocked.** No CI, no fetch, no compute, no decision from trimcrae.

## ⚠ A defect I introduced and repaired, disclosed because the repair is invisible in the final tree

My first pass rewrapped each edited paragraph at 100 columns. The rewrapper treated a **blank line**
as the only block boundary — but list items in these manuscripts are adjacent lines with no blank
between them, so it reflowed whole lists into single paragraphs and buried **24 list markers
mid-line** in `nr4a3-fusion-transcriptional-output.md` (`… PubMed identifier 21536545. - **GSE4303**
— …`, `… not the common one. 5. **The normal arm …`). Caught by grepping for a list marker preceded
by non-whitespace, before any gate ran.

**Repair, and why it is clean:** `git show HEAD:<path>` was byte-identical to my reverse-applied
pre-edit reconstruction modulo whitespace, which proves no other seat had touched that file, so I
restored it from `HEAD`, made the rewrapper treat a list marker as a block boundary, and re-applied
the same 24 edits. The vaccine and neoantigen papers were checked for the same damage and had none
(list-marker line counts 36 → 37 and 28 → 28, the one addition being another seat's). Final state:
**0 mid-line list markers in all three files, and list-marker counts identical to `HEAD`.**

⭐ **The lesson worth keeping: a whitespace-only tool can silently destroy document structure, and
the readability gate cannot see it** — every reflowed list still measured clean, because a buried
`- **GSE4303**` is just more words in a sentence. Same orthogonality as CLAUDE.md §6's inverted
claims: the guard measures one property and the damage is in another.

## Ledger rows the driver should write

Two, neither of which I may write myself. Both are in the same family as S5's rows 1 and 2, and both
are strict-only in direction (they can only make a length longer, never shorter).

1. **`what`:** ⛔ `lint_readability.body()` DELETES A SENTENCE-TERMINATING NUMERAL THAT A LINE WRAP
   PUT AT COLUMN 0, GLUING TWO SENTENCES. `research/manuscripts/lint_readability.py:136` applies
   `re.sub(r"^\s*\d+\.\s+", "", t)` per line to strip ordered-list markers; these manuscripts are
   hard-wrapped, so a sentence ending `… as internal residue 266.` that wraps with `266.` at the
   start of the next line loses that token entirely. Measured 2026-09-01 on identical prose wrapped
   two ways: `266.` at line start → one 32-word "sentence" with the number missing; `266.` mid-line
   → 19 w + 14 w, both correct. This is **the whole of `emc-vaccine-development-path.md`'s Figure 1
   legend flag** and therefore part of PUB-VACCINE-PATH's live clause-7 exposure. The fix is to
   require the marker to be followed by list-like content, or to strip markers before wrapping is
   undone rather than per line. ⚠ **The reading is wrap-dependent, so re-wrapping a paragraph can
   silently clear or create a flag** — which is also why no writer should be asked to fix it in
   prose. **`kind`:** `process_defect` · **`state`:** `queued` · `cost_class`: free.

2. **`what`:** ⚠ `lint_readability`'s "no sentence in these manuscripts opens with a digit or a
   lowercase letter" EXCLUSION IS FALSE, MEASURED ON THREE LIVE SENTENCES. S5 pinned it as a negative
   test on the correct argument that a false split understates a length; the premise is what fails.
   Measured 2026-09-01: `… **NR4A occupancy** (§3.11). 110 published NR4A ChIP-seq peak sets …`
   (reported 63 w, real 3 w + 60 w) and `… might substitute for one. 110 NR4A peak sets …`
   (reported 74 w, real 28 w + 46 w) in `nr4a3-fusion-transcriptional-output.md`, and
   `… and 4 \`OUT_OF_FRAME\`. **e11** is among the refusals …` in
   `fusion-junction-neoantigen-paper.md` (reported 80 w, real 47 w + 27 w), where the lowercase
   opener appears only after `body()` strips emphasis markers. **All three were fixed in the prose by
   this seat**, so the corpus no longer demonstrates it — the row is about the next such sentence.
   ⛔ **Widening the opener class is the unsafe direction** (S5's own note), so the honest fix is
   narrow: a digit or a stripped-emphasis identifier that follows a terminal stop **and** begins a
   token that is not a decimal continuation. **`kind`:** `process_defect` · **`state`:** `queued` ·
   `cost_class`: free.

**No hand-off.** `neoantigen/hla-coverage-emc.md` was the one candidate and another seat cleared it
during this window (verified: 0 over-ceiling, `--check` green), so of the four owned manuscripts,
three now pass clause 7's sentence test outright and the fourth is held only by §B3 and by ledger
row 1 above.
