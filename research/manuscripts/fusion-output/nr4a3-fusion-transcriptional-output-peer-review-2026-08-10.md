---
id: DOC-NR4A3-FUSION-TRANSCRIPTIONAL-OUTPUT-PEER-REVIEW
title: "Simulated peer review — nr4a3-fusion-transcriptional-output.md (Genes, Chromosomes and Cancer)"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: A simulated journal peer review of the transcriptional-output manuscript, and the revision list it generates.
scope: Review of one manuscript. Reports no new result and asserts nothing about any disease or agent.
audience: [maintainers, external reviewers]
date: 2026-08-10
last_verified: 2026-08-10
---

> **THIS IS A SIMULATED INTERNAL REVIEW WRITTEN BY AN AI REVIEWER INSIDE THIS REPOSITORY.**
> It is not correspondence from *Genes, Chromosomes and Cancer*, from Wiley, or from any journal,
> editor or referee. No journal has seen this manuscript. Nothing here is an editorial decision, and
> nothing here may be quoted or forwarded as if it came from a journal. It is a red-team exercise:
> one reviewer's simulated report, produced to find what a real referee would find before a real
> referee does.

# Simulated peer review

**Manuscript:** *Almost every gene set reads higher in the index arm: a size-matched empirical null for small rare-tumour expression series, and what it leaves of the EWSR1::NR4A3 direct-target catalogue*
**Target journal:** *Genes, Chromosomes and Cancer* (Wiley), Original Research Article
**Reviewed material:** main text, Supplementary Information, cover letter, submission checklist, Figures 1–5 and `figure-provenance.json`, plus the committed artifacts that produce the numbers
**Reviewer:** simulated referee with a statistical-genomics remit
**Date:** 2026-08-10

---

## Recommendation

**Major revision** — conditional on a reframing that the author may decide not to accept, in which case
rejection is the correct outcome rather than a further round.

This is a careful, unusually self-critical piece of work whose disease-facing content is real and worth
publishing: an exhaustively evidence-typed catalogue of what any NR4A3 chimera has been shown to bind, a
measurement that the native-to-fusion transfer assumption fails in both directions, a comparator-stratum
dissection that dissolves one of the three published targets, a calibrated occupancy audit of every
available NR4A peak set, and a bounded, honestly qualified map of the chromatin experiment nobody has
done in this disease. Almost all of that is new, and the manuscript's habit of reporting the reading
that damages its own case is a virtue I rarely see. But the paper is submitted with a *methodological*
headline, and that headline does not survive scrutiny. The "size-matched empirical null drawn from the
platform's own genes" is a re-derivation of the competitive gene-set null that has been in the
literature since the mid-2000s, and the manuscript cites none of the prior art — not the
competitive-versus-self-contained framework, not restandardization, not CAMERA, not ROAST, not
single-sample scoring with size-matched or expression-matched control sets. Worse, the null is
demonstrably an *independence* null (I verified this against the artifact: `null_sd × sqrt(n)` is
constant to within 5% across set sizes from 10 to 250 on both platforms), which is precisely the
construction the prior art exists to correct, and the manuscript acknowledges the defect in one sentence
and then reports every downstream verdict as though it did not apply. Alongside that, I found several
numerical claims that disagree with the artifacts and figures behind them, including one — a 17-gene
null band quoted three times as a 19-gene band — that is exactly the error class the paper was written
to abolish, and an arithmetic error in the instrument-control paragraph that a previous correction
introduced. The revision that would make me recommend acceptance is not more analysis: it is to
subordinate the method to the biology, cite and position against the prior art, fix the traceable
numbers, and cut roughly half the text. Every one of those steps is free.

---

## MAJOR POINTS

### 1. The central methodological claim is a re-derivation, and no prior art is cited anywhere in the paper
*Applies to: Title; Abstract; §1.1; §2.3; §4.2 first bullet; §6 first paragraph; cover letter ¶2.*

The paper's stated contribution is that a gene-set read on a small series is uninterpretable until it is
calibrated against random gene sets of the same size drawn from the same platform. That is the
**competitive** gene-set null. It is not new. The distinction between competitive nulls (gene sampling)
and self-contained nulls (subject sampling), and the argument that competitive nulls are invalid under
inter-gene correlation, is the standard reference framework in this area (Goeman and Bühlmann, 2007).
Combining a gene-randomization null with a sample-permutation null — which is exactly the pairing this
manuscript builds in §2.3 and §2.6 — is *restandardization* (Efron and Tibshirani, 2007). A competitive
test that additionally estimates and corrects the inter-gene correlation is CAMERA (Wu and Smyth, 2012);
the rotation-based self-contained counterpart is ROAST (Wu et al., 2010). Single-sample set scoring with
an explicit size-matched null of random gene sets is standard in `singscore` (Foroutan et al., 2018),
and control sets matched on *expression bin* rather than size alone are the default in the most widely
used single-cell module-scoring implementation. GSVA and ssGSEA are the obvious comparators for the
per-sample mean-z score the paper uses.

The manuscript does say, once, in §4.2, "Nothing here is a first-in-field claim." That sentence is
buried under a bullet headed "The calibration, which is the contribution", and it is contradicted by the
title, by the abstract's "We supply the calibration that refuses such a read", by §1.1's "That
calibration is the instrument this paper supplies", and by the cover letter's first substantive
paragraph. A referee with a methods background will read those four and conclude the author does not
know the field. There is not a single statistical reference in the reference list: Welch, Benjamini–
Hochberg, the permutation framework, the binomial tail and the `+1/+1` empirical-p smoothing all appear
without a citation.

**What would resolve it.** (a) Delete every sentence that presents the calibration as supplied, new, or
this paper's contribution, in all four locations. (b) Add a short Methods subsection — 150 words is
enough — that names the competitive/self-contained distinction, names CAMERA and ROAST, names
restandardization, and states plainly what this implementation does *differently*, which as far as I can
tell is only this: it reports the observed effect as a *fraction of the detectability threshold* rather
than as a p-value. That reporting convention is a genuine, modest, citable contribution and it is worth
keeping — but it is a presentational device, not an instrument. (c) Retitle around the biology (see
point 12). (d) If the author wants the methodological point to stand on its own, it belongs in a
separate short methods note, and it will need a simulation study benchmarking it against CAMERA before
any methods venue will take it. That is out of scope for this submission and should not be attempted
inside it.

Zero cost. No new data.

### 2. The null is an independence null; the paper's headline figure of merit is not the quantity it is used as
*Applies to: §2.3 last paragraph; §3.9 and Table 8; §5 Limitation 9; Figure 1 caption.*

I checked this directly against `nr4a3-fusion-targets.json`. For every scored set, `null_sd × sqrt(n)` is
essentially constant:

| platform | set sizes checked | `null_sd × sqrt(n)` |
|---|---|---|
| GPL6244 | 10, 16, 19, 20, 21, 63, 188, 189, 231, 250 | 0.2528 – 0.2683 |
| GPL3290 | 10, 14, 17, 18, 57, 157, 169, 176, 196, 230 | 0.6623 – 0.6969 |

The residual 3–5% decline at large n is exactly the finite-population correction for sampling without
replacement from a 4,000-symbol pool. Two consequences follow, and both matter.

First, the 4,000-draw resampling buys nothing that a closed form does not already give: the band is
`offset ± 1.96 σ_platform / sqrt(n_readable)`, with `σ = 0.266` on GPL6244 and `σ = 0.694` on GPL3290. A
reader can reproduce every band in Table 8 and Table S2 on the back of an envelope. That is worth saying
in the paper — it makes the method easier to adopt, which is what the author wants — and it also makes
the "it costs one seeded resampling" selling point redundant.

Second, and more seriously: because the null carries no correlation structure at all, its anti-conservatism
for a coherent set is not a caveat but a quantifiable bias. Under an average inter-gene correlation
`ρ̄`, the variance inflation is `1 + (n−1)ρ̄`; at n = 17 and a modest `ρ̄` of 0.05–0.10 the threshold
widens by 1.4–1.6×, and the A+B aggregate on GPL3290 reaches roughly 55–63% of it rather than 88%.
**The direction of that bias is not symmetric across the paper's claims.** The headline *negative* is
robust and in fact strengthened: a set that fails an anti-conservative null fails a correct one a
fortiori. But every *positive* in the paper sits on the unprotected side — set D at 11.9× and 4.2×, all
six PPARγ arms in SI §S4, and every single-gene "outside its null band" grade in §3.3 and §3.5.
Limitation 9 states the problem in one sentence and then nothing in the results propagates it.

**What would resolve it.** Compute `ρ̄` for each real gene set from the same z-matrices already in hand
(free, one pass), report the variance-inflated threshold beside the uninflated one in Table 8 and Table
S2, and confine unqualified competitive-null language to the negatives. Where a positive rests on the
competitive null alone — which is the case for three of the six PPARγ arms, as SI §S4 already admits —
say so in the main text, not only in the SI.

### 3. A 17-gene null band is quoted three times as a 19-gene band, and the illustrative t is the paper's own set
*Applies to: Abstract sentence 2; §1.1 paragraph 2; §3.4 paragraph 1.*

All three locations read "an arbitrary 19-gene set on GPL3290" with band `[−0.297, +0.376]`. The
artifact records `set_size: 17`, `null_q025: −0.29715`, `null_q975: 0.37648` — the band is for a
**17-gene** set, because only 17 of the 19 A+B genes are readable on GPL3290 (`ICAM1` and `MYH7` are
not). Supplementary Table S2 records 17 correctly. Figure 1's top-right panel is labelled "A+B
direct-target set (17 readable)" and "95% of random 17-gene sets" — correctly. So the figure and the SI
agree with the artifact and the main text does not, in the one sentence of the paper on which the whole
argument turns. In a manuscript whose thesis is that a band is meaningless unless it is matched to the
set's size, quoting a band at the wrong size is the error the paper exists to abolish, and a referee who
notices it will doubt everything else.

Two further problems in the same sentence. The `t = 3.16` is not "an arbitrary 19-gene set": it is this
paper's own A+B direct-target set (`t = 3.159` in the artifact), presented as if it were a generic
demonstration. And the null is computed over Δ, not over `t` — nothing in the paper establishes what
`t` an arbitrary set of that size prints, because the resampling never recorded one.

**What would resolve it.** (a) Change 19 to 17 in all three places and say the band is for the readable
size. (b) Say whose set the t belongs to: "this paper's own aggregate target set prints t = 3.16 and
still falls inside the band". (c) If a claim on the `t` scale is wanted, recompute `t` for each of the
4,000 draws already generated and report the null distribution of `t` — one extra line in the producer,
no new data.

### 4. Set D is neither fully independent of GPL3290 nor a fair instrument benchmark
*Applies to: §3.9 and Table 8; §3.8; Figure 1 lower row; Abstract sentence 5; §6 paragraph 1.*

Set D — Filion's top-25 EMC-versus-137-sarcomas list — is described as "an INDEPENDENT replication set:
it comes from neither readable series", and its 11.9-fold and 4.2-fold clearance is the paper's proof
that "the instrument reads this disease, not this set". Two objections.

*Partial circularity.* Set D and set E share three genes: `DKK1`, `MAN1A1`, `NMB`. Set E is defined in
the artifact as "the 20 genes Filion's EMC profile shares with the top 50 of Subramanian et al. 2005",
and §3.8 establishes that GSE4303 *is* the Subramanian cohort. Those three genes are therefore
documented members of a top-50 list derived from GPL3290 itself. They are 3 of the 18 set-D genes
readable on GPL3290, and the paper's own circularity discipline — which it applied to set E and then, to
its credit, to a single gene row — requires that this be stated and the contrast re-run without them.

*Selection on the same contrast.* Set D was selected as the 25 probe sets most over-expressed in EMC
versus other sarcomas. Scoring it on another EMC-versus-sarcoma contrast is a winner's-curse
replication. It is a real cross-platform, cross-cohort replication and worth reporting as one, but it
cannot calibrate what effect size a *mechanistically* selected set should reach, and so it cannot
license the inference in §3.9 that the A+B negative is "bounded, not underpowered". A list chosen for
maximal difference on this contrast will clear by an order of magnitude on any platform that works;
that says the platform works, not that the aggregate target set is meaningfully flat.

**What would resolve it.** Re-score set D on GPL3290 with `DKK1`, `MAN1A1` and `NMB` removed and report
both values (free). Relabel set D throughout as "a positive control selected on the same contrast",
delete "the instrument reads this disease, not this set" as a general instrument claim, and replace it
with the narrower and defensible "the contrast detects a list selected for this difference at 11.9× and
4.2× threshold".

### 5. "A bounded negative, not an underpowered one" overreaches the artifact that produces it
*Applies to: §3.9 final sentence of paragraph 2; Abstract sentence 5; §6 paragraph 1; §4.2 first bullet.*

The producing artifact, `nr4a3-fusion-targets-confounds.json` → `minimum_detectable_effect`, carries its
own guard: *"This is a DETECTABILITY threshold on this instrument at these arm sizes, not a statistical
power calculation — no alternative hypothesis is assumed."* The manuscript then makes exactly the power
claim the artifact refuses. "Reached 39% and 88% of threshold" is the ratio of an observed point
estimate to the 97.5th percentile of a null. It is a descriptive quantity. It carries no information
about the probability of detecting a true effect of any given size, and it is not a bound on what effect
sizes have been excluded.

**What would resolve it.** Replace the power language with an interval statement. Two free options,
either sufficient: report the set-level Δ with a confidence interval from the existing exact
label-permutation machinery, and state the smallest true Δ that this design would place outside the
95% band with (say) 80% probability. Both are computable from artifacts already committed. Then the
sentence becomes "effects larger than X SD are excluded; effects smaller than X are not", which is what
a bounded negative actually is.

### 6. The occupancy multiplicity arithmetic assumes uniform, independent p-values and has neither
*Applies to: §2.6 item 5 final sentence; §3.11 paragraph beginning "The first number to read"; Table 9; Figure 4 caption.*

"2 of 36 gene-by-experiment tests reach p < 0.05 against 1.8 expected by chance — a binomial p of 0.54"
requires (i) that each empirical p be uniform on [0,1] under the null and (ii) that the 36 tests be
independent. Neither holds. The p-values are ranks within a 198-gene panel of small integer peak counts;
they are heavily discrete and heavily tied — `PPARG` returns exactly 1.00 in 11 of its 12 experiments,
and `SEMA3C` in 8 of 12. Under that discreteness the probability of the event `p < 0.05` is not 0.05,
so 1.8 is not the expected count. And the 36 tests share the same three genes, the same background
panel, and peak sets that overlap heavily by construction (eight of the twelve informative experiments
are NR4A1 ChIPs, four are the same Haller deposit).

I want to be clear that this cuts *against* the paper's own conclusion being overstated in the direction
of a false negative, not a false positive: with the true null mass below 0.05 smaller than nominal, two
hits could be less ordinary than the binomial suggests. The section's leading argument — that 82.8% of
arbitrary genes carry a peak in the deepest catalogue, so a raw count is worthless — is excellent and
does not depend on the binomial at all.

**What would resolve it.** Either obtain the null by permutation over panel genes, holding each peak
set's depth fixed (free, the peak cache is committed), or drop the binomial entirely and report the raw
counts beside the panel column, which is the honest and sufficient reading the section already leads
with. Do not report a binomial tail on rank statistics.

### 7. §3.12 miscounts the occupancy hits and states a stronger negative than the data support
*Applies to: §3.12 paragraph 1; §6 paragraph 3.*

§3.12 reads: "no class-A gene exceeds a background panel in any NR4A peak set (§3.11), and *ENO3*'s one
nominally significant value falls in a **normal parotid gland** rather than any tumour — 2 hits in 36
tests against 1.8 expected". The artifact's `per_gene_summary` gives `ENO3` two nominally significant
values, `p = 0.0348` (normal parotid, NR4A3) and `p = 0.0498` (`SRX1653204`'s sibling `SRX1653203`,
NR4A1), and gives `PPARG` and `SEMA3C` none. Both of the "2 hits in 36" are therefore ENO3's, which
makes "*ENO3*'s one nominally significant value" contradict the clause it sits in. Separately, "no
class-A gene exceeds a background panel in any NR4A peak set" is false as written; what is true is that
no gene exceeds it after accounting for 36 tests, which is what Figure 4's caption says ("judged at a
Bonferroni threshold for those twelve").

**What would resolve it.** Rewrite as: "*ENO3* is the only class-A gene with any nominal hit and it has
both of the two — one in a normal parotid gland and one in an NR4A1 experiment — and neither survives
correction across the 36 tests." Table 9 already prints the `SRX1653203` value (`2, p 0.050`), so this
is a prose fix only.

### 8. The single-gene null band is computed once per platform and applied to genes measured on fewer samples
*Applies to: §2.3 final sentence; §2.4; §3.3 and Table 4; §2.6 item 1; Table 5; SI Table S3.*

On GPL3290 the design is described everywhere as 10 versus 6. It is not, gene by gene. From
`gene_reads` in the primary artifact: `PLAGL1` is measured on **8** EMC samples against 6 comparators;
`PPARG` on 10 against **5**; `NR4A3` on 9 against 2 (correctly refused). Only 42 of the 78 readable
genes have the full 10 versus 6. Yet the size-1 null band applied to `PLAGL1` is `[−1.31352, +1.40969]`
— the identical band applied to `SGK1` at 10 versus 6, and printed as such in Table 4. A contrast on
fewer samples has a wider sampling distribution, so the band applied to the directional falsifier — the
control §2.4 calls "the only prediction an arm-wide offset cannot manufacture" — is too narrow, and its
"outside null, AGREES" grade is anti-conservative by an unquantified amount. In a paper whose
contribution is size matching, this is a size-matching failure.

The same missingness undercuts a Methods statement. §2.6 item 1 says "Arm sizes give 1,623,160 and 8,008
distinct assignments — few enough to enumerate completely, so every reported p is exact rather than
sampled." C(35,6) = 1,623,160 and C(16,10) = 8,008 are correct for the full design, but `PLAGL1`'s
enumeration is C(14,8) = 3,003 and `PPARG`'s is C(15,10) = 3,003. The p-values are presumably still
exact for their own designs; the sentence as written is not true of every gene.

**What would resolve it.** (a) Add `n_EMC / n_comparator` columns to Tables 4, 5 and S3 — the artifact
already carries them. (b) Draw the size-1 null under each gene's own missingness pattern rather than
once per platform (free; the resampling is already per-platform, so this is a loop change). (c) Correct
the assignment-count sentence to say the enumeration is complete for whatever design each gene has, and
give the range.

### 9. Class B is not one evidence class, and it supplies 16 of the 19 genes in the headline aggregate
*Applies to: §2.1 and Table 1; §3.1 paragraph 3; SI Table S1; §3.9 and Table 8.*

Table 1 defines class B as "a DNA-binding or promoter assay performed with **native NR4A3**", and §2.1
says rows "were read from retrieved full text, not from memory". Supplementary Table S1 does not sustain
that for a substantial minority of class B. `LOXL2` and `MYH7` are supported by "named a direct NOR-1
target gene in the source review". `BIRC3` and `ICAM1` cite only "Reviewed in PMCID …" with "NBRE
binding site" as the assay and no primary source retrieved. `TH`, `CCND1` and `VTN` rest wholly or
partly on review assertion. That is a different evidence type from `SMPX` (promoter deletion, site-
directed mutagenesis, EMSA and ChIP in human cells) or `CDKN2AIP` (ChIP plus mutation-reversed reporter
in human cells).

This is not a bookkeeping quibble, because class B contributes 16 of the 19 genes in the A+B aggregate,
and the A+B aggregate carries the paper's headline negative. The composition of the set on which the
central result rests is partly determined by rows whose evidence is a review's assertion — inside a
paper whose entire method is evidence typing.

**What would resolve it.** Split class B into B1 (primary assay retrieved and read) and B2 (asserted in
a review, primary not retrieved), report the split in Table 1, and score A+B1 as the primary aggregate
with A+B as a sensitivity. Free: it is a relabelling of `LITERATURE_TARGETS` plus a re-run.

### 10. `MYH7` is simultaneously a class-B target and a "skeletal-muscle marker" control, and the muscle control has no calibration
*Applies to: §3.5 final paragraph; Table S6; Figure 5 and its caption.*

The muscle-admixture control uses `ACTA1`, `MYH7`, `PYGM` and `MYL1` as markers whose flatness bounds
admixture. `MYH7` is in the paper's own class-B target list (Table 1, §3.1, Table S1). If the
native-to-fusion transfer assumption held, `MYH7` would be expected to move, so its flatness is being
read as evidence about admixture while the paper's own catalogue makes it evidence about the target set.
The control cannot serve both roles.

Second, and more important for a paper about calibration: Table S6 and Figure 5 report four percentile
differences with no uncertainty and no null, on the same 6-versus-29 design the paper insists is
uninterpretable without one. `PYGM` moves +0.142, about 45% of `ENO3`'s +0.315, and the text calls that
"none of them separates the tumour arms". The paper applies its own instrument to `ENO3` and not to the
markers used to defend `ENO3`. That is the sharpest form of the question a referee will ask: does the
headline result get judged by the rule the paper applies to everyone else? Here it does not.

**What would resolve it.** (a) Remove `MYH7` from the marker panel, or keep it and state the conflict
explicitly. (b) Put all four marker differences through the same size-1 null the class-A genes go
through, and report the bands in Table S6 (free). (c) Weaken the sentence to what four uncalibrated
points can carry: "the three most muscle-restricted markers do not separate the arms and a fourth moves
about half as far as *ENO3*; this is a four-point comparison without an error estimate, not a test."

### 11. §3.3's instrument-control count is arithmetically wrong, and a previous correction introduced the error
*Applies to: §3.3 paragraph 2; Table 4; Appendix A row 5.*

§3.3 states: "Five of the six control × platform cells carried a computable contrast, and all five agree
with the published direction; none disagrees. The sixth (*NR4A3* on GPL3290) is not measurable."

There are four controls and two platforms. Table 4 prints **eight** cells, not six. From the artifact:
seven are computable (only `NR4A3` on GPL3290 is not measurable); six are gradeable and all six agree;
`PLAGL1` on GPL6244 is inside its band and is explicitly not graded. Of the six agreements, two are
`SGK1` cells whose prediction ("flat or down") is satisfied by an inside-band reading, and one is
`PLAGL1` at 8 versus 6 (point 8). So the number of genuinely falsifiable, outside-band agreements is
**four**: `ENO3` on both platforms, `NR4A3` on GPL6244, `PLAGL1` on GPL3290.

Appendix A records that this sentence was already corrected once, from "Four of four graded controls
agree". The correction replaced one wrong count with another, in the paragraph §2.4 identifies as "the
last place that distinction may collapse".

**What would resolve it.** Rewrite as: "Eight control × platform cells; seven carry a computable
contrast and one (*NR4A3* on GPL3290) does not. Six are gradeable against their null and all six agree
with the published direction; none disagrees. `PLAGL1` on GPL6244 falls inside its band and is not a
reading at this power. Of the six agreements, four are outside-band readings that could have refused
their prediction; the two `SGK1` cells could not, because an inside-band reading satisfies 'flat or
down'." Add the per-gene n from point 8.

### 12. The paper does two jobs, and the venue judgement follows from which one it leads with
*Applies to: whole manuscript; title; cover letter; submission checklist §1.*

The checklist already flags this as the main risk and concludes the answer is unchanged. I disagree.

**As submitted, I think a GCC editor desk-rejects this more often than not.** The triage signal is title
plus abstract. The title's first clause is a statistical generality; the second clause promises a
negative about a three-gene catalogue. The abstract opens on a statistical failure mode and reaches the
disease in its second sentence. An editor at a cancer cytogenetics and genomics journal reads that as a
biostatistics methods paper with a sarcoma illustration, sees no new genomic data and three archival
series from 2005, 2011 and 2012, and returns it as out of scope. The cover letter's decision to lead
with "The contribution is a calibration, and I have ordered the paper to say so" makes this more likely,
not less: it tells the editor in the first substantive paragraph that the paper is about statistics.

**The framing that works at GCC** is the inverse of the current one. Lead with the disease question,
which is squarely in scope and genuinely novel:

> *The published direct-target catalogue of the EWSR1::NR4A3 fusion is three genes wide, and none of the
> three is separable from disease association in the available EMC expression record.*

Under that title, the paper's assets line up exactly with GCC's remit: an exhaustively evidence-typed
catalogue with the assay, cell system and species behind every claim; the measurement that the
native-to-fusion transfer fails in both directions, which matters to anyone reasoning from NR4A3
literature to EMC; the demonstration that `SEMA3C`'s elevation is a property of which sarcomas sit in
the comparator arm and reverses sign against desmoid fibromatosis; the circularity finding on `PPARG`
and GSE4303; the calibrated occupancy audit; and the mapped absence of any chromatin experiment on EMC
material against sibling fusions for which the field runs it routinely. The empirical null then becomes
what it is — a Methods subsection, two paragraphs, positioned against CAMERA and ROAST — and the
"reached X% of threshold" convention becomes a reporting choice a reader can adopt, which is a more
persuasive way to propagate a method than claiming to have invented it.

I would not split this into two papers. The methods half will not survive methods review as novel
(point 1), so a split produces one publishable paper and one that is rejected. Subordinate, do not
split.

### 13. Length and display items: the paper is roughly twice the length it needs to be
*Applies to: whole manuscript; §2.5–§2.7; §3.10; §3.11; §3.13; Appendices A and B; Tables 1, 4, 6, 7, 9, 10; Figures 2 and 5.*

The submission packet measures 12,160 words of main text and the paper carries 15 numbered display
items. Both are well beyond what a focused genomic re-analysis needs, and length is itself a
desk-reject risk.

**Move to Supplementary Information, in full:**

- **Appendix A** (superseded values and corrected claims). This is a repository supersession register,
  not journal content. No journal prints twenty rows of the manuscript's own revision history, and its
  presence signals to an editor that the file is a working document. The one item worth keeping in the
  main text is the retracted chromatin-absence inference, as a single sentence in §3.11 where the
  narrower claim now lives.
- **Appendix B** (what would change the conclusions). Compress to three sentences at the end of §4.3.
- **§3.10** (the NBRE motif scan and the GSE243553 intersection) in its entirety, retaining two
  sentences in §4.3 item 5. It is the axis the paper itself concludes is exhausted, and it consumes
  roughly 900 words.
- **§3.13** (the fourth-cohort search) and **Table 10**, retaining three sentences in Limitation 1. The
  SRA deposit paragraph is important and should stay in Limitation 1 in compressed form.
- **§2.7** (cohort search method) and the second half of **§2.6**, both of which already have fuller
  versions in the SI.
- **§3.11**'s search narrative, retaining Table 9 and the three bullet readings.
- **Tables 1, 4, 6, 7 and 9** to the SI. Table 1 is a four-row definition that can be prose; Table 4 is
  an instrument-control table that belongs in Methods-adjacent supplementary material; Tables 6 and 7
  are already duplicated at greater depth as Tables S4 and S7-adjacent material.
- **Figure 2** (a three-category count of the evidence classes) does not need a figure; it is one
  sentence. **Figure 5** to the SI alongside Table S6.

**Keep in the main text:** Tables 2, 3, 5, 8 and Figures 1, 3, 4. That is 4 tables and 3 figures — seven
display items, a normal number — and should land the text between 5,000 and 6,000 words.

### 14. The abstract is 333 words against a believed 250-word limit and contains one factual overstatement
*Applies to: Abstract.*

The packet's counting rule gives 333 words; my own count of the plain prose gives 332. Roughly 83 words
must go. Sentence-by-sentence lengths are 19, 59, 29, 20, 43, 59, 7, 59, 18, 19.

Before cutting, one substantive error must be fixed. Sentence 5 reads "**In three cohorts on three
platforms** that aggregate reaches 39% and 88% of its null threshold". The aggregate was scored on
**two** platforms. The 3SEQ arm carries no set score at all — §2.5 states that no z-score, no test and
no confidence interval is computed there, and Table 8 has only two columns. Change to "On both readable
array platforms".

**Where the 83 words come from, specifically:**

1. **Sentence 2, cut ~31 words.** Delete the three-item list of unrelated sets ("PPARγ targets, hypoxia
   metagenes and adipogenesis all move alike") and the appositive clause. Replace with: *"In a
   10-versus-6 extraskeletal myxoid chondrosarcoma (EMC) series, unrelated gene sets move alike, because
   a set's per-sample score is one draw from a distribution whose width depends on the set's size and on
   the platform: this paper's own 17-gene target set prints t = 3.16 and still falls inside the band of
   a random set of that size."* (Note the 19→17 correction from point 3 lands here.)
2. **Sentence 6, cut ~14 words.** Delete the instrument list at the front ("Exact label permutation,
   every comparator stratum separately, a matrix covariate and a muscle control then separate") and open
   with *"Calibrated and permutation-tested, three genes usually treated alike separate:"*.
3. **Sentence 8, cut ~25 words.** Delete the accession, the peak-set count and the background-panel
   clause; end after "in EMC material". Those belong in the body, and the abstract loses nothing.
4. **Sentences 9 and 10, cut ~13 words** by merging: *"Until a fusion cistrome in EMC chromatin exists,
   'elevated in EMC' and 'driven by the fusion' are inseparable — in this disease and in any series with
   a small index arm and heterogeneous comparators."*

That is roughly 83 words and leaves the abstract at approximately 249. **Confirm the real GCC limit on
the journal's own page before cutting**; the checklist records 250 as search-derived and unverified
because Wiley serves a bot challenge, and the two repository files currently hold two different beliefs
about it.

### 15. Repository register has survived into a submission text
*Applies to: whole manuscript and SI.*

I ran the repository's own manuscript-register gate (`lint_style.py`) against these two files. Neither
is in that gate's `TARGETS`, so it has never been applied to them. Measured:

| file | words | bold runs / 1000 (limit 12) | em-dashes / 1000 (limit 6) | glyphs | mid-sentence bold | sentence-shaped headings | banned phrases |
|---|---:|---:|---:|---:|---:|---:|---:|
| main text | 14,043 | **16.7** | **12.2** | 25 | 54 | 9 | 4 |
| SI | 5,243 | **23.1** | **15.8** | 20 | 16 | 5 | 1 |

140 findings across the two files. Specific tics a copy editor will flag: the warning glyphs `⚠`, `⛔`
and `⭐` appear 27 times across the two files and the arrow `→` a further 32, on 45 flagged lines,
including inside Results (§3.10, §3.11, §3.13), inside Discussion (§4.2), inside the Conclusion (§6)
and inside Table 9's surrounding prose; two sentences are set in full capitals ("AND THE BOUND IS
LOAD-BEARING, BECAUSE A DEPOSIT OUTSIDE IT EXISTS" in §3.13); `→` is used as running punctuation in
Data and code availability and throughout the SI; almost every paragraph opens with a bolded clause;
section headings are sentences separated by a middle dot ("3.4 · The global offset is not the problem —
null-band width is"); and "deliberately" appears four times across the two files defending choices no
reader has questioned. The prose also repeatedly asserts its own honesty ("Stated
at full honesty", "and that has to be said plainly", "the honest summary", "rather than merely
conceded"), which in a journal reads as advocacy rather than as a report and is the single most
recognisable machine-written tic in the file.

**What would resolve it.** Add both files to `lint_style.py`'s `TARGETS` and drive the gate to zero.
Delete every glyph; convert every bolded clause to plain prose or to a subheading; convert headings to
noun phrases ("3.4 · Null-band width, not the global offset"); halve the em-dashes; and delete every
sentence whose content is a claim about the paper's own candour.

---

## MINOR POINTS

1. **§1.3, "42–70% of their citations come from EMC records" — I cannot trace the 70%.** The committed
   probe `fusion-consensus-probe.json` gives Filion 2009 at 22/52 = 42%, Subramanian 2005 at 27/50 =
   54%, and Kim 2016 at 4/12 = 33%. Brenca 2019's total-citation query returned `hit_count: null` — the
   query executed and produced no count — so no committed value supports 70%. Either recover the value
   or restate the range from what is held.
2. **§1.3, "each is cited by four to six EMC reviews", excludes the source of the surviving gene.** The
   counts are Filion 4, Brenca 5, Subramanian 6. Kim 2016 — the `ENO3` source, and therefore the source
   behind the one gene the paper says survives everything — is cited by **0** EMC reviews and by 12
   papers in total. The sentence's purpose is to argue that the near-absence is not an artefact of
   obscure sources; the one source that most needs that defence is silently omitted from it. State the
   Kim figures.
3. **"Top 2% of 14,120 genes" uses the wrong denominator.** In §3.7, §3.12 and §6 the percentile is
   attributed to 14,120 genes; the artifact ranks within the 13,708 genes that have a computable
   EMC/normal ratio (13,247 for the sarcoma axis). Say "of the 13,708 genes with a computable ratio".
4. **198 versus 203 background-panel genes, in adjacent sections, unexplained.** §3.10 reports "2 of 203
   promoters" while §3.11 and Table 9 use "a background panel of 198 genes". The producing artifact
   explains the difference (211 genes resolve on hg38, minus 8 focus genes = 203; the motif scan
   resolves 198) and warns against quoting one for the other; the manuscript carries neither number's
   provenance. Add one clause.
5. **`ENO3`'s GPL6244 delta is printed at two values.** Tables 4 and 5 give +0.8075; Tables S3 and S5
   give +0.8074. §3.3 claims the independent second implementation "matches ... to four decimal places
   on both platforms"; the agreement is to three. Either reconcile the rounding or weaken the claim.
6. **Table 6 presents duplicate strata as distinct.** Its GPL6244 "vs non-myxoid only (6)" column is
   numerically identical to Table S4's `class_desmoid_fibromatosis_only` column, because the six
   non-myxoid comparators *are* the six desmoids; its GPL3290 "pool-matched only (3)" column is
   identical to `class_DFSP_only`. §3.6's "+0.805, +0.808, +0.807 across strata that share almost
   nothing" therefore counts one stratum twice. Label the columns for what they are.
7. **Table 6 omits the stratum whose p §3.6 quotes.** The myxofibrosarcoma-only sub-arm is not a column
   of Table 6, yet §3.6 quotes `SEMA3C` at "p = 0.136 at its worst", which is that stratum's value in
   Table S4. Either show the column or cite Table S4 at that sentence.
8. **"Least favourable stratum" is defined by the largest p, which is not least favourable.** For
   `SEMA3C` the scientifically worst stratum is the *significant reversal* against desmoid fibromatosis
   (−0.645, p = 0.015), not the non-significant −0.523 (p = 0.136). Define the summary rule explicitly,
   and say that for `SEMA3C` the least favourable reading is a significant effect in the opposite
   direction.
9. **SI Table S4 still carries a label Appendix A records as corrected.** The GPL6244 column is headed
   `class_fibrosarcoma_only`; Appendix A row 2 records the correction of "6 fibrosarcoma" to six
   *myxofibrosarcomas*, and the producing artifact's `class_counts` still reads `fibrosarcoma: 6`. The
   correction reached the prose and not the generated table.
10. **Table 8 labels sets by requested size while the null is matched to readable size.** "(19)", "(16)"
    and "(21)" are the requested counts; on GPL3290 the readable counts are 17, 14 and 18. Figure 1 and
    Table S2 do this correctly. Print both, or print the readable size.
11. **§3.9's heading says "12-fold"; the body, the abstract and §6 say 11.9-fold.** Use one value.
12. **Table 2 says "42,000-spot" while §2.3 says 43,008 probes.** Use the measured number in both.
13. **The null pool is a seeded 4,000-symbol subsample with no stated reason and no seed-sensitivity
    check.** §2.3 discloses that it is a subsample (21% of GPL6244's mapped symbols, 27% of GPL3290's),
    that the same pool is reused at every set size, and that the gene under test is not excluded. It
    does not say why a subsample was used at all — sampling from the full universe costs the same — nor
    whether a second seed reproduces the band. I estimate the combined Monte-Carlo and pool-composition
    error on the GPL3290 97.5th percentile at roughly ±2%, which would move "88% of threshold" by about
    ±2 points and does not change any verdict; but that is my estimate and it belongs in the paper.
    Redraw the pool under 20 seeds and report the spread (free, one loop).
14. **The null is matched on size but not on expression level or detection rate.** A real target list is
    biased toward well-expressed, well-annotated genes; a uniform draw from all mapped symbols is not,
    and on a two-colour cDNA array where 27,203 of 43,008 spots resolve through an EST bridge, a large
    part of the pool is low-signal. Expression-binned control sets are standard practice for exactly
    this reason. The direction of the resulting bias is not obvious a priori and should be measured, not
    argued: report an expression-decile-matched null alongside the uniform one for the A+B set and set D
    (free). This is the single most valuable free addition available to the paper, because it addresses
    the "is this just a re-derivation" objection by engaging established practice rather than deflecting
    it.
15. **No statistical method in the paper carries a citation.** Welch's test, Benjamini–Hochberg, the
    exact permutation framework, the binomial tail, and the `+1/+1` empirical-p smoothing all appear
    without a reference. Add them.
16. **Figure 4 has a text collision.** The "NBRE motif / sequence, not occupancy" column header and the
    "NR4A occupancy" column header overlap and are unreadable at submission size. Regenerate with wider
    column spacing or shorter headers.
17. **Figure 4's colour rule for the 3SEQ column is undocumented and contradicts the text.** `PPARG` is
    coloured "supported by this instrument" at percentiles 84.0 and 96.4, while `SEMA3C` is not
    supported at 94.2 and 92.6; the caption says the 3SEQ column "carries no test", which leaves the
    reader with no way to know what "supported" means there. §3.7 separately calls `PPARG`'s 84th
    percentile "the weakest cell in the table". State the threshold in the caption, or grey the whole
    column and let the printed percentiles speak.
18. **Figure 4's stratum column is GPL6244-only but is not labelled as such,** and "across 5 strata"
    counts the duplicate stratum of minor point 6.
19. **A percentile is used as an instrument in §3.12 and §6 after §2.5 refuses to make it one.** §2.5 is
    right that no test is available at n = 4; §3.12 then lists "the top 2% of 14,120 genes in an
    independent cohort" among the instruments that support `ENO3`, and §6 repeats it. Say explicitly
    that this axis contributes a rank and not a test.
20. **Disambiguate "Subramanian et al. 2005."** The manuscript uses it for the EMC expression cohort.
    The most-cited gene-set analysis paper in this area is also Subramanian et al. 2005. If any
    gene-set-methodology citation is added under point 1, the two must be distinguished on first use or
    every reader will misread one of them.
21. **§2.7 does not disclose the query repair that the Results and SI do.** The Methods description of
    the cohort search presents six queries; §3.13's final paragraph and SI §S7 disclose that four
    returned zero, that all four shared a field restriction, and that three returned records when
    re-asked. A reader of Methods alone would not know the reported search is a repaired one. Move one
    sentence into §2.7.
22. **The Zenodo DOI timing is inconsistent between documents.** The manuscript's Data and code
    availability says the repository "will be archived to Zenodo with a citable DOI at submission" in
    one clause and the checklist §7 item 2 notes the section "already states this is planned at
    acceptance". Fix to one.
23. **The ORCID placeholder is still in the title block and the cover letter.** Required before
    submission.
24. **Cover letter, paragraph 2.** It leads with the calibration as the contribution. Under the
    reframing of major point 12, rewrite it to lead with the three-gene catalogue and the mapped absence
    of an EMC chromatin experiment, and mention the null once, in the methods sentence.

---

## Revision list

Work top to bottom. Every item is achievable with no new data, no bench work and no spend.

1. `nr4a3-fusion-transcriptional-output.md`, **title** — retitle around the disease result; the
   calibration leaves the title. Suggested: *"The published direct-target catalogue of the EWSR1::NR4A3
   fusion is three genes wide, and none is separable from disease association in the available EMC
   expression record."*
2. `nr4a3-fusion-transcriptional-output.md`, **§1.1** — delete "That calibration is the instrument this
   paper supplies" and the surrounding novelty framing; keep the failure mode, which is well argued.
3. `nr4a3-fusion-transcriptional-output.md`, **§1.1, §3.4, Abstract** — change "19-gene set on GPL3290"
   to "17-gene set" in all three places, and attribute the `t = 3.16` to this paper's own aggregate
   rather than to "an arbitrary" set.
4. `nr4a3-fusion-transcriptional-output.md`, **§2.3** — add the prior-art paragraph: competitive versus
   self-contained nulls, restandardization, CAMERA, ROAST, size-matched and expression-matched control
   sets in single-sample scoring. State what this implementation does differently (the
   fraction-of-threshold reporting convention) and nothing more.
5. `nr4a3-fusion-transcriptional-output.md`, **§2.3** — state that the band is algebraically
   `offset ± 1.96 σ_platform / sqrt(n_readable)`, give σ per platform (0.266 GPL6244, 0.694 GPL3290),
   and note that the resampling reproduces the closed form.
6. `nr4a3_fusion_targets.py` and **Tables 8, S2** — compute the mean inter-gene correlation for each
   real set and report the variance-inflated threshold beside the uninflated one.
7. `nr4a3-fusion-transcriptional-output.md`, **§3.9, §6, Abstract, §4.2** — delete "a bounded negative,
   not an underpowered one" and every equivalent; replace with the interval statement (set-level Δ with
   a permutation confidence interval, plus the smallest Δ this design would place outside the band with
   80% probability).
8. `nr4a3_fusion_targets.py` and **§3.9, Table 8, Figure 1** — re-score set D on GPL3290 with `DKK1`,
   `MAN1A1` and `NMB` removed; report both values; relabel set D as a positive control selected on the
   same contrast; delete "the instrument reads this disease, not this set" as a general claim.
9. `nr4a3_fusion_targets.py` — draw the size-1 null under each gene's own `n_EMC / n_comparator` rather
   than once per platform; regenerate Tables 4, 5 and S3 with those columns printed.
10. `nr4a3-fusion-transcriptional-output.md`, **§2.6 item 1** — correct the "8,008 distinct assignments
    … every reported p is exact" sentence to reflect that `PLAGL1` (8 versus 6) and `PPARG` (10 versus
    5) enumerate C(14,8) and C(15,10) = 3,003 each.
11. `nr4a3-fusion-transcriptional-output.md`, **§3.3** — rewrite the control-count sentence: eight cells,
    seven computable, six gradeable, six agreeing, four of those six outside-band and therefore
    falsifiable. Add the per-gene n.
12. `nr4a3_fusion_targets.py` → `LITERATURE_TARGETS`, **Table 1, §3.1, SI Table S1** — split class B into
    B1 (primary assay retrieved) and B2 (review assertion); make A+B1 the primary aggregate and A+B the
    sensitivity; re-run and update Table 8 and Table S2.
13. `nr4a3_fusion_targets_confounds.py`, **§3.5, Table S6, Figure 5** — remove `MYH7` from the muscle
    marker panel or flag the conflict with its class-B membership; put all marker differences through
    the size-1 null; weaken the "none of them separates the tumour arms" sentence to acknowledge
    `PYGM` at +0.142.
14. `nr4a3-fusion-transcriptional-output.md`, **§3.5** — "three markers" lists four (`ACTA1`, `MYH7`,
    `PYGM`, `MYL1`) with four values. Change to four, and note that three sit at or below zero and one
    at +0.142, which is what Figure 5's caption already says.
15. `nr4a3_fusion_targets_occupancy.py`, **§2.6 item 5, §3.11** — replace the binomial tail with a
    permutation null over panel genes at fixed peak-set depth, or drop the multiplicity statistic and
    report raw counts against the panel column.
16. `nr4a3-fusion-transcriptional-output.md`, **§3.12 and §6** — rewrite the occupancy sentence: `ENO3`
    holds both of the two nominal hits (p = 0.0348 in normal parotid gland, p = 0.0498 in an NR4A1
    experiment) and neither survives correction; delete "no class-A gene exceeds a background panel in
    any NR4A peak set" as written.
17. `nr4a3_fusion_targets.py` — redraw the null pool under 20 seeds and report the spread of the 97.5th
    percentile per platform; add one sentence to §2.3.
18. `nr4a3_fusion_targets.py`, **§2.3 and Table 8** — add an expression-decile-matched null for the A+B
    set and set D as a sensitivity analysis, and report it beside the uniform-draw null.
19. `nr4a3-fusion-transcriptional-output.md`, **Abstract** — apply the four cuts in major point 14 to
    reach approximately 249 words, and change "In three cohorts on three platforms" to "On both readable
    array platforms". Confirm the real GCC abstract limit on the journal's page first.
20. `nr4a3-fusion-transcriptional-output.md` → `nr4a3-fusion-transcriptional-output-SI.md` — move
    Appendix A, Appendix B, §3.10, §3.13 and Table 10, §2.7, the second half of §2.6, and §3.11's search
    narrative to the SI; keep the compressions named in major point 13.
21. `nr4a3-fusion-transcriptional-output.md` — move Tables 1, 4, 6, 7 and 9 and Figures 2 and 5 to the
    SI, leaving Tables 2, 3, 5, 8 and Figures 1, 3, 4 in the main text (seven display items).
22. `nr4a3-fusion-transcriptional-output.md`, **§1.3** — recover or restate the citation-share range; the
    committed probe supports 42%, 54% and 33%, and Brenca's total-citation query returned no count. Add
    Kim 2016's figures (12 total citations, 0 EMC reviews) to the same sentence.
23. `nr4a3-fusion-transcriptional-output.md`, **§3.7, §3.12, §6** — change the percentile denominator from
    14,120 to 13,708 (and 13,247 for the sarcoma axis).
24. `nr4a3-fusion-transcriptional-output.md`, **§3.10 and §3.11** — add one clause reconciling the 198-
    and 203-gene resolutions of the same background panel.
25. `nr4a3-fusion-transcriptional-output.md`, **Tables 4, 5 versus SI Tables S3, S5** — reconcile
    `ENO3`'s GPL6244 delta (+0.8075 versus +0.8074) and weaken §3.3's "four decimal places" claim to
    three.
26. `nr4a3-fusion-transcriptional-output.md`, **Table 6 and §3.6** — label the duplicate strata (the
    non-myxoid column is the desmoid column; the pool-matched column is the DFSP column); either add the
    myxofibrosarcoma-only column or cite Table S4 where its p is quoted; define "least favourable
    stratum" and state that for `SEMA3C` it is a significant reversal.
27. `nr4a3_fusion_targets_confounds.py` and **SI Table S4** — rename `class_fibrosarcoma_only` to the
    corrected `class_myxofibrosarcoma_only`, and update `class_counts` in the producing artifact.
28. `nr4a3-fusion-transcriptional-output.md`, **Table 8** — label sets by readable size per platform, or
    print both requested and readable.
29. `nr4a3-fusion-transcriptional-output.md`, **§3.9 heading** — "12-fold" to "11.9-fold"; **Table 2** —
    "42,000-spot" to 43,008 probes.
30. `nr4a3_fusion_targets_figures.py`, **Figure 4** — fix the overlapping column headers; state the 3SEQ
    column's colour threshold in the caption or grey the column; label the stratum column as GPL6244 and
    correct "5 strata".
31. `nr4a3-fusion-transcriptional-output.md`, **References** — add citations for Welch, Benjamini–
    Hochberg, the permutation framework and the gene-set methodology named in item 4; disambiguate
    Subramanian et al. 2005 on first use.
32. `nr4a3-fusion-transcriptional-output.md`, **§2.7** — move one sentence about the query repair from
    §3.13 into Methods.
33. `nr4a3-fusion-transcriptional-output.md`, **Data and code availability** — settle the Zenodo DOI
    timing (submission or acceptance, not both).
34. `lint_style.py` → `TARGETS` — add `nr4a3-fusion-transcriptional-output.md` and
    `nr4a3-fusion-transcriptional-output-SI.md`, then drive the gate to zero: delete all 59 decorative
    glyphs on their 45 flagged lines, unbold all 70 mid-sentence runs, convert 14 sentence-shaped
    headings to noun phrases, halve the
    em-dashes, remove the four "deliberately"s and the full-capital sentences, and delete every sentence
    asserting the paper's own candour.
35. `nr4a3-fusion-transcriptional-output-cover-letter.md`, **paragraph 2** — rewrite to lead with the
    three-gene catalogue and the mapped absence of an EMC chromatin experiment; mention the null once, in
    a methods sentence.
36. `nr4a3-fusion-transcriptional-output.md` and the cover letter — fill the ORCID placeholders.
37. `nr4a3-fusion-transcriptional-output-submission-checklist.md`, **§1** — record that the venue
    rationale was re-examined a second time and that the recommendation now depends on the reframing in
    item 1; if the author declines the reframing, move the primary target to a methods or general
    cancer-genomics venue before submitting anywhere.
