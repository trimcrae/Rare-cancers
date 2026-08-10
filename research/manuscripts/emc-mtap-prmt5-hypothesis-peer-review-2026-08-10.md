---
id: DOC-EMC-MTAP-PRMT5-PEER-REVIEW
title: "Simulated peer review — emc-mtap-prmt5-hypothesis.md (Genes, Chromosomes and Cancer)"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: A simulated journal peer review of the PRMT5 manuscript, and the revision list it generates.
scope: Review of one manuscript. Reports no new result and asserts nothing about any disease or agent.
audience: [maintainers, external reviewers]
date: 2026-08-10
last_verified: 2026-08-10
---

# Simulated peer review — "The PRMT5 methylosome in extraskeletal myxoid chondrosarcoma"

> **THIS IS A SIMULATED INTERNAL REVIEW, WRITTEN BY AN AI REVIEWER AT THE AUTHOR'S REQUEST. IT IS
> NOT CORRESPONDENCE FROM *GENES, CHROMOSOMES AND CANCER*, NOT A REAL PEER REVIEW, AND NOT A
> DECISION. No editor, no journal and no external referee has seen this manuscript. It exists only
> to find the objections a real referee would raise, before one does.**

Manuscript: `research/manuscripts/emc-mtap-prmt5-hypothesis.md`
Also read: the SI, the cover letter, the pre-posting checklist, the five figures, and the committed
artifacts each number is said to come from.
Reviewer stance: fusion-driven sarcoma genetics and epigenetics; PRMT5/MEP50 biology; 9p21
MTAP/CDKN2A co-deletion; small archival microarray series.

Because the underlying artifacts were available to me, this review traces the load-bearing numbers
back to the JSON and Python that produced them rather than taking them on trust. Most of them check
out exactly. The ones that do not, and the readings the artifacts contain but the manuscript does
not report, are the substance of what follows.

---

## Recommendation: **major revision**

This is a careful, unusually self-critical paper, and its central editorial decision — separating a
rationale that survives from one that does not, and leading with the closure rather than burying it
— is the right one for this journal. The verification I was able to do is largely reassuring: the
*t* statistics, the exact permutation counts, the proliferation- and chondroid-adjusted values, the
dependency percentages and means, the genome-wide percentiles, the GRG and RG site counts and the
retained-residue counts all reproduce exactly against the committed artifacts, and the five figures
match their sources on a provenance check. That is a better record than most submissions achieve.
But three things stand between this draft and acceptance. First, the multiple-testing limit is
treated as a disclosure problem when it is a result-changing one: the standard correction is
computable from data already in the repository at no cost, and when I computed it the primary
contrast does not clear conventional thresholds on either platform. Second, the 16-tumour platform
carries a batch confound — half its comparator arm was hybridised against a different two-colour
reference pool from every EMC tumour — that the manuscript nowhere mentions, and which offers a
simpler explanation for the platform disagreement than the one the paper gives. Third, several
sample- and gene-level facts that shape the results are undisclosed: seven of forty-two samples
dropped from one series, a comparator arm of two on a control the paper presents as an instrument
check, and one of three reported clear cell breakpoints omitted from the analysis that carries the
surviving rationale. None of these is fatal and none requires a bench experiment to fix. All are
fixable by re-analysis of data already committed, by honest weakening of the claims, and by saying
plainly what was done. I would want to see the revision before recommending acceptance.

---

## Major points

**M1. A Methods number in §2.3 traces to no artifact, and disagrees with the artifact that exists.**

§2.3 states that the genome-wide statistic was computed "for every symbol the platform's probes map
to (18,474 on GPL6244 and 14,402 on GPL3290)". The committed artifacts say otherwise:
`research/modalities/emc-prmt5-route-controls.json` records
`per_platform.*.genome_wide_placement.n_symbols_scored` as 18,688 and 14,404, and
`research/modalities/emc-expression-panels.json` records the same two values under
`platforms.*.genome_wide_null`. The pair 18,474 / 14,402 appears in no committed artifact at any
point in that file's history — the controls artifact has exactly one committed version and it reads
18,688 / 14,404. The same wrong pair also appears in SI §S10 and in the pre-posting checklist.

This is small arithmetically and large in principle, for two reasons. §2.6 states that "The author
verified every reported value against the committed artifact that produced it"; this number fails
that check, so the sentence as written is not true of the manuscript. And it is exactly the failure
mode the paper's own Appendix A already registers for the superseded MTAP value of −0.023, which
"entered the prose from a source the repository cannot show". A referee who found one such number
will assume there are others; the fix should therefore be a systematic re-check, not a single edit.

There is a second, separable inaccuracy in the same sentence. On GPL3290 the artifact records
`n_symbols_with_a_probe` = 14,932 against `n_symbols_scored` = 14,404, so 528 symbols that do have a
probe yielded no statistic. "Every symbol the platform's probes map to" is therefore not what was
computed.

*Resolution.* Replace both numbers in §2.3, SI §S10 and the checklist with 18,688 and 14,404;
register 18,474 / 14,402 in Appendix A as superseded; and rewrite the parenthesis to say how many
symbols were scored out of how many carried a probe, on each platform.

---

**M2. The multiplicity limit is not only undisclosed, it is result-changing, and the correction can
be run on data already committed.**

§2.1, §2.3, §3.5 and §4.4 all state that no multiplicity correction is applied, and §3.5 is careful
that a genome-wide rank "is not a corrected *p*". That honesty is real and I credit it. But the
manuscript then leaves the question there, and the abstract leads with the two exact permutation
*p*-values (0.000142 and 0.000125) with no adjusted counterpart beside them. A reader — and a
referee — will take those as the strength of the transcript evidence. They are not: they are exact
for the labelling of a single gene chosen after a curated panel of several hundred genes and a
genome-wide scan of ~18,700 and ~14,400 symbols had been examined.

The standard remedy is a max-statistic (Westfall–Young style) permutation correction, and every
input for it is already committed. I ran it as a reviewer's check on
`research/modalities/emc-expression-panels-inputs.json`, permuting the arm labels exactly as §2.3's
exact test does, recomputing Welch's *t* for every gene at each permutation, and recording the
maximum |*t*| across genes per permutation (B = 500, seed fixed). Using only the 1,857 (GPL6244) and
1,662 (GPL3290) genes held in that cache:

| gene | platform | reported \|*t*\| | FWER-adjusted *p* (reviewer's computation) |
|---|---|---:|---:|
| *PRMT5* | GPL6244 | 6.24 | 0.13 |
| *PRMT5* | GPL3290 | 6.67 | 0.07 |
| *CDKN2A* | GPL6244 | 5.40 | 0.32 |
| *MAT2A* | GPL6244 | 4.13 | 0.84 |
| *MAT2A* | GPL3290 | 4.10 | 0.76 |
| *NR4A3* (control) | GPL6244 | 4.66 | 0.61 |
| *ENO3* (control) | GPL6244 | 3.61 | 0.97 |
| *ENO3* (control) | GPL3290 | 13.22 | 0.006 |
| *MTAP* | both | 0.69 / 2.27 | 1.00 / 1.00 |

Two caveats, and both push the same way. My null was built on roughly a tenth of the symbols the
manuscript's own scan covers, and adding symbols can only raise the permuted maximum and therefore
raise the adjusted *p*. Correlation among the curated genes reduces the effective number of tests
relative to a random set of the same size, which also depresses my figures. So these are lower
bounds on the adjusted *p*, not estimates of it.

The consequences the manuscript must absorb:

- The primary transcript contrast does not clear 0.05 on either platform once the number of genes
  examined is accounted for. It is close on the 16-tumour platform and not close on the 35-tumour
  one.
- Of every reading in the paper, only *ENO3* on GPL3290 survives correction. Neither instrument
  control survives on GPL6244.
- §3.2's positive claim that "The locus signal on the powered platform is *CDKN2A*" rests on an
  adjusted *p* of about 0.32 and must be weakened accordingly. The *closure* of the MTAP rationale is
  unaffected — *MTAP* is at an adjusted *p* of 1.00 on both platforms, which is exactly the paper's
  point and is the one place where correction helps the argument rather than hurting it.
- §3.5's sentence that the placement supports "only the narrower statement that on these arrays a *t*
  of *PRMT5*'s size is uncommon" stops one clause short of the truth. A |*t*| of 6.24 is uncommon
  among individual genes and is *not* uncommon among the maxima that arise by chance when this many
  genes are scanned at this sample size.

Is the absence of correction fatal? In my judgement, no — for three reasons that the revision should
make explicitly, rather than leaving me to supply them. The paper's claim is a hypothesis and is
framed as one; the two series are independent, so *PRMT5* ranking first of the readable PRMT family
on both platforms is a replication statement that no single-platform correction captures; and the
paper's most useful result is a negative, which correction strengthens. What is not acceptable is
reporting 0.000142 in an abstract without the adjusted figure beside it.

*Resolution.* Run the max-statistic permutation over the full genome-wide *t* matrix — the fetch step
already builds it in memory in `_genome_wide_null` — and report the adjusted *p* in §3.5's table
beside the exact permutation *p*. Rewrite the abstract sentence to carry both. Add one sentence to
§4.4 stating which readings survive correction and which do not. Do not delete the exact permutation
*p*: it answers a different and legitimate question, and the paper should say which.

---

**M3. On GPL3290 the comparator arm is confounded with the two-colour reference channel, and this is
nowhere disclosed.**

The `sample_annotations_verbatim` block of `emc-expression-panels.json`, under the GPL3290
platform record, carries the
verbatim GEO annotations for all sixteen samples. They split as follows: all ten EMC tumours were
hybridised against a reference labelled `CRH-mRNA`; the three DFSP comparators against `CRH`; and
the three GIST comparators against `UHR`, a universal human reference. In a two-colour design every
value is a ratio to the reference channel, so changing the reference changes every ratio
systematically. Half the comparator arm on this platform therefore differs from every EMC tumour in
the denominator of the measurement, not only in the biology.

This matters more than a generic batch caveat because GPL3290 is the platform on which the
proliferation control fails (§3.6, row 2), and a reference-pool difference is a simpler and more
mundane explanation for an apparently elevated proliferation score than a real difference in growth
fraction. The manuscript currently attributes the disagreement to the platforms measuring "different
quantities" in a general way, and does not name the specific difference its own artifact records.

The reassuring half, which I computed and which the manuscript should report: splitting the
comparator arm by reference pool leaves the direction and rough size of the primary contrast intact.
*PRMT5* gives *t* = 5.97 against the three reference-matched DFSP comparators and *t* = 4.32 against
the three UHR-referenced GIST comparators, against 6.67 pooled. *MAT2A* is less stable, falling to
*t* = 2.18 in the reference-matched contrast from 4.10 pooled.

*Resolution.* Add the reference-channel composition to §2.1's table or to SI §S1. Add one sentence to
§3.6 naming the confound as a candidate explanation for the platform disagreement. Report the
reference-matched sensitivity analysis in the SI. All of this is computable from
`emc-expression-panels-inputs.json` with no new data.

---

**M4. The *NR4A3* instrument control on GPL3290 is computed on a comparator arm of two samples, which
the paper's own pipeline refuses to score, and the paper explains the result by the wrong mechanism.**

§3.5's table reports *NR4A3* on GPL3290 as "+1.70, top 38.5%", and §3.5's text builds an
interpretation on it: "*NR4A3* is only mid-table there, consistent with the probe-placement caveat
the source artifact carries, since on a 3′-biased array the probe can sit in the region the fusion
replaces". Checking the artifact:

- In `emc-expression-panels.json`, the `gene_reads.NR4A3` record for GPL3290 has
  `welch_EMC_vs_comparator: null`, and its verdict states that there is no group contrast because
  n_EMC is 9 and n_comparator is 2 against a floor of 3 per group, so no contrast was computed. Only
  two of the six comparator samples carry a value for this gene, and one of the ten EMC samples does
  not.
- The +1.70 comes from the separate genome-wide path, whose Welch helper requires only two per arm
  rather than the panel's floor of three. So the manuscript reports as a control a value its own
  panel declines to emit.
- The self-check that §2.3 invokes ("the two agree for every gene on both platforms") skips any gene
  the panel did not score, so it does not and cannot vouch for this particular value.
- The probe-placement caveat is genuinely in the artifact — it is pre-specified in the control block —
  so the attribution is not invented. But the artifact's *measured* reason for refusing this read is
  the sample count, and the manuscript quotes the pre-specified explanation while omitting the
  measured one. Two comparator samples, one from each reference pool, is a sufficient explanation on
  its own.

*Resolution.* In §3.5, either drop the GPL3290 *NR4A3* row or report it with its arm sizes stated
inline (n = 9 versus 2) and a note that the panel's own floor excludes it. Replace the
probe-placement sentence with one that gives both candidate explanations and says which is measured.
Disclose in §2.1 or §2.3 that per-gene missingness varies on GPL3290: of the 1,662 genes in the
cached input, 578 (34.8%) have at least one missing value and 51 (3.1%) have an arm below three.

---

**M5. Seven of GSE24369's forty-two samples were dropped from the analysis without disclosure, and
five of them are a sarcoma comparator that ranks second on the primary endpoint.**

§2.1's table describes GSE24369 as 6 EMC against "29 comparator sarcomas". The series carries 42
samples. `class_counts` records EMC 6, LGFMS 17, desmoid fibromatosis 6, fibrosarcoma 6, and
`unclassified` 7. The seven unclassified are five solitary fibrous tumours and two pooled
skeletal-muscle RNA samples, and reading the classifier in `emc_atr_vulnerability.py`
(`COMPARATOR_BUCKETS`) shows why: there is no pattern for solitary fibrous tumour, so those five fell
through to `unclassified` and out of the comparator arm. This was not a designed exclusion.

Excluding two pooled normal-tissue samples from an arm of tumours is correct and needs only a
sentence. Excluding five solitary fibrous tumours is a substantive analytic choice that a referee
will notice, and it is the class that matters most: computing per-class medians on GPL6244, the
excluded class sits at a *PRMT5* median of +1.14, second only to EMC's +1.30 and above desmoid
fibromatosis (+1.05), LGFMS (+1.04) and fibrosarcoma (+0.94). On the pooled four-gene methylosome
score it ranks first, above both desmoid fibromatosis and EMC.

So figure 4's two claims are both affected. "EMC ranks second of four comparator classes, below
desmoid fibromatosis" becomes third of five once the excluded class is drawn. "*PRMT5* alone does
[separate], with a median of +1.30 against +1.05, +1.04 and +0.94" omits a fourth comparator class at
+1.14, which narrows the gap the figure exists to display.

The good news, which the manuscript should report: adding the five back to the comparator arm barely
moves the headline statistics. *PRMT5* goes from *t* = 6.24 to 6.31, *MTAP* from 0.69 to 0.70,
*CDKN2A* from −5.40 to −5.66. The primary results are robust to the exclusion; the figure-4 ranking
claim is not.

*Resolution.* State in §2.1 that GSE24369 deposits 42 samples of which 35 were analysed, name what
was excluded and why, and separate the defensible exclusion (pooled normal tissue) from the
accidental one. Redraw figure 4 with the fifth class included, or state its medians in the caption
and say why it is not plotted. Report the sensitivity of the primary contrasts to the inclusion in
the SI.

---

**M6. §3.7 and figure 5 present one of three reported EWSR1::ATF1 breakpoints, and the one omitted
retains zero sites.**

The motif analysis carries the surviving rationale, and its rhetorical peak is that "The commonest
EMC fusion and the commonest clear cell sarcoma fusion retain the same number of sites". The
`measured_comparator_fusions_on_the_same_ruler` block of
`emc-prmt5-substrate-motif-map.json` holds three reported EWSR1::ATF1 junctions, not one:
exon 8 retains 4 GRG sites, exon 10 retains 4, and exon 7 retains none. The §3.7 table and figure 5
show only exon 8. `emc-fet-construct-designs.json` labels all three, so this is presentation, not
absence of data.

Including the other two does not destroy the argument — two of three reported types retain four
sites — but it makes it visibly less clean, and a referee who checks the source will see that the
cleanest of three available comparisons was the one selected. The paper's credibility rests on doing
the opposite. The omission also weakens §4.2's two-construct proposal, which is built on
motif-count contrast within a single disease and would be sharpened by noting that clear cell sarcoma
already offers the same contrast across its own breakpoints.

*Resolution.* Add the two further reported EWSR1::ATF1 junctions to §3.7's table with their site
counts, or plot them in figure 5. Rewrite the concluding sentence of §3.7 to say that two of three
reported clear cell junctions retain the same number of sites as the commonest EMC fusion and one
retains none.

---

**M7. Two readings already in the committed artifacts bear directly on the paper's own stated limits
and are not reported; a third is described in the SI but is not in the artifact.**

*(a) PRMT5 is not sarcoma-selective, and the artifact says so numerically.* §3.3 states that PRMT5
and MAT2A are dependencies in 94.5% and 96.7% of the 91 screened sarcoma lines, and argues correctly
that this makes a growth effect close to expected. `depmap-sarcoma-dependency.json` carries the
sharper number and the manuscript does not use it: for PRMT5, `rest_frac_dependent` is 0.941 and
`selectivity` is 0.013 — that is, PRMT5 is a dependency in 94.1% of non-sarcoma lines too, and there
is essentially no sarcoma preference at all. This is one clause, it comes from the same table the
paper already cites, and it converts §3.3's argument from "close to expected within sarcoma" to "not
distinguishable from pan-essentiality across DepMap". It is a strictly stronger statement of the
paper's own limit and it should be in the text.

*(b) A pre-specified cellularity control was run and is not reported.* The control block in
`emc-expression-panels.json` names MKI67 with the pre-specified expectation "approximately FLAT …
EMC is slow-cycling; a large proliferation delta would say the contrast is being driven by
cellularity". The measured values are *t* = 0.53 on GPL6244 (flat, as expected) and *t* = 2.30,
+1.24 SD on GPL3290. That is a pre-specified control passing on one platform and moving on the other,
in the same direction and on the same platform as the twelve-gene proliferation control of §3.6.
It corroborates the paper's own weakest point and is currently absent from both the manuscript and
the SI. Suppressing a control that fires is the one thing a paper of this kind cannot do, even
inadvertently.

*(c) SI §S5 describes a control block that does not exist.* SI §S5 states that "The
instrument-control read, covering housekeeping recovery and a marker expected high in the comparator
arm rather than in EMC, is carried in the source artifact's control block". The control block
contains NR4A3, ENO3, MKI67, EWSR1, TAF15 and FUS. There is no housekeeping gene in it and no marker
designated as comparator-high. Either the sentence is describing a different analysis or it is
wrong; as written it tells a reader a control was run that was not.

*Resolution.* Add the PRMT5 pan-DepMap selectivity figure to §3.3 and to SI §S4. Add MKI67 to §3.6's
table or to SI §S5 with both platform values and its pre-specified expectation. Rewrite SI §S5's
control sentence to name the six genes actually in the block and their expectations.

---

**M8. Eleven references are not adequate for a Research Article of this scope, and the gaps are
specific.**

Reference practice is otherwise good: all eleven are cited, numbered in order of first appearance,
and the citation-anchoring discipline behind them is better than most submissions. But the following
load-bearing claims currently carry no citation, and several of them a referee will not let pass.

1. **Both primary data sources.** GSE24369 and GSE4303 are cited only as accessions. The
   publications that generated them must be cited; a referee assessing whether the comparator arms
   are appropriate cannot do so from an accession alone.
2. **DepMap and Chronos.** §2.2 names "the DepMap public 24Q4 release (Chronos)" with no citation to
   the release, its DOI, or the Chronos method.
3. **The transcript-type breakpoints of §3.7.** §2.5 says "Breakpoint positions are as reported in the
   sources" and names no source. `emc-fet-construct-designs.json` records them with identifiers and
   verbatim quotations, so the citations exist and only need transcribing. This is the single most
   important gap, because falsifier F9 is explicitly "a corrected breakpoint" — a reader cannot check
   a breakpoint whose source is not given.
4. ***ENO3* as a published direct target.** §3.5 calls *ENO3* "a published direct target of an NR4A3
   fusion" and gives no reference. The whole instrument-control argument rests on this being true; the
   artifact carries the identifier.
5. **"The natural history is indolent and the tumour is slow-cycling"** (§1.1), which is uncited and
   is load-bearing twice over — once for the argument that division-rate-scaling mechanisms are weak
   here, and once for how §3.6's proliferation disagreement should be read.
6. **"The systemic classes with any disease-specific evidence number about eight"** (§1.1).
7. **The EWSR1 activation-domain claim** (§1.2): that the fusion is constitutively active "because
   the EWSR1 portion supplies the activation domain".
8. **"Two such models exist and are published, and their holders have already run a multi-agent
   functional screen on them"** (§4.2). This is a factual claim about specific published models and
   about what a named group has done, and it is the premise of the paper's principal proposed
   experiment. It cannot stand uncited.
9. **The modality census of §1.3** ("enumerated 217 categories of cancer treatment"). This traces to a
   repository document with no external locator. Either give it a citable form in §8 or drop the
   number and keep the qualitative statement.
10. **MEP50/WDR77 in the methylosome.** §1.2 cites [6] for the structural requirement, which is right,
    but the manuscript uses "MEP50 (WDR77)" and "methylosome" as established terms without a review
    citation a non-specialist editor can follow.

Separately: **the preprint that is the original source of the surviving rationale has not been
checked since 2022.** §4.4 says "Its status since 2022 was not established here". A referee will not
accept that. Establishing whether a four-year-old preprint has since been published is a literature
search, requires no data this work does not already have, and is squarely the authors' work. If it has been published, the paper's
strongest citation improves; if it has not, that is itself informative and the caveat should say so
in those terms rather than in terms of not having looked.

---

**M9. The Methods would not let an independent group reproduce this analysis.**

§2.6 says every number "is regenerable from public data by scripts in the accompanying repository".
That is true of the repository and not of the Methods, and a journal reader has only the Methods.
The following are needed and absent.

1. **Sample classification and exclusion.** How each GEO sample was assigned to EMC or to a comparator
   class, and which samples were excluded (M5). Currently a reader cannot get from 42 deposited
   samples to 35 analysed.
2. **The comparator arms' composition.** §2.1 gives "29 comparator sarcomas, including a
   FET-rearranged histology" and "6". The actual composition — 17 LGFMS, 6 desmoid fibromatosis, 6
   fibrosarcoma on one platform; 3 DFSP and 3 GIST on the other — is decision-relevant for every
   contrast in the paper and belongs in the table.
3. **The *z*-score background.** §2.1 says values are converted "against that array's own full probe
   distribution". Whether that distribution is per-sample or per-series, and whether the mean and SD
   are taken over all probes or only mapped ones, changes every number and is not stated.
4. **Multi-probe collapse.** Several genes map to more than one probe (MTAP maps to two on GPL3290,
   MKI67 to two). The rule for combining them is not given.
5. **Probe-to-symbol mapping.** The bridge is built from GEO platform annotation plus a UniGene
   archive plus live NCBI queries, and its resolution rate varied between runs. None of this is in the
   Methods, and the SI's own corrections register shows the bridge is the volatile part of the
   pipeline.
6. **Missing-value handling** in both the panel path and the genome-wide path, including the differing
   minimum-arm-size floors between them (M4).
7. **The two-colour reference channel** (M3).
8. **Software.** No language, version, or statistical library is named anywhere.

*Resolution.* Expand §2 by roughly a page, or move the detail into the SI and point at it. None of it
requires new analysis; it requires writing down what the code does.

---

## Minor points

**m1.** **Appendix A, first row, cites the wrong reference.** It reads "a peer-reviewed
fusion-dependent PRMT5 requirement in a second EWSR1-fusion sarcoma [2]". Reference [2] is the
bioRxiv preprint that the same manuscript repeatedly describes as not certified by peer review; the
peer-reviewed result is [3]. Change [2] to [3].

**m2.** **§3.1 quotes array percentiles on a platform where the artifact says they are not
interpretable.** "*MAT2A* sits at the 99th percentile of its array on GPL6244 and the 84th on
GPL3290; *PRMT5* sits at the 91st and at the 59th." The source artifact labels GPL3290's values
"two-colour log-ratio vs a reference pool (RELATIVE — an absolute level is NOT interpretable; only
the between-group contrast is)". Drop the GPL3290 percentiles or state explicitly that they are
percentiles of a log-ratio distribution and carry no absolute meaning.

**m3.** **The PRMT-family counts read as a contradiction between the two documents.** §3.6 says
"Eight family members are readable on GPL6244 and seven on GPL3290"; SI §S3's PRMT-family row says
"7/8" and "6/8". Both are right — the main text includes PRMT5 itself and the SI's group excludes it
— but nothing says so. Add four words to one of them.

**m4.** **Reference [8], on which all of §3.7 rests, was read at abstract level only.** The citation
artifact records its verification as "[MD] metadata + abstract read from the retrieved Europe PMC
record; full text is not open access and was NOT read". The manuscript quotes it directly and never
says this. Since the GRG motif definition is the foundation of the entire sequence analysis, the
verification level should be stated in §2.5 or in SI §S9.

**m5.** **"largely supressed" (§1.2) reproduces a typographical error from the quoted source.** That
is correct scholarly practice, but add "[sic]" so a copy-editor does not silently "fix" a verbatim
quotation.

**m6.** **The abstract's "for which no targeted agent exists" is stronger than reference [1]
supports**, which is "no clinically validated agent directly targets NR4A3". Align the two; the
weaker form costs three words and is unassailable.

**m7.** **Figure 4's caption calls EMC one of the "four comparator classes".** EMC is the index
class, not a comparator. Rewrite as "second of the four classes plotted" (and see M5, which changes
the count).

**m8.** **Figure 5 omits TAF15::NR4A3**, which appears in §3.7's table, while the caption says "each
fusion's retained 5′ segment" is drawn below EWSR1. The omission is defensible — TAF15 is a different
protein and a different ruler — but the caption should say so rather than implying completeness.

**m9.** **The abstract is 249 words against a 250-word limit.** There is no headroom for the
additions M2 and M6 require. Plan the trade now: the sentence enumerating the four data sources can
be compressed, and the exact permutation *p*-values can move to the Results if the adjusted values
take their place in the abstract.

**m10.** **The title is 22 words and 166 characters, in three clauses.** It is descriptive and I like
what it does, but it is long for the journal and the third clause ("and two inexpensive tests") is
the weakest of the three. Consider dropping it.

**m11.** **§2.4's "at least 60% of its magnitude" survival threshold is author-chosen** and the paper
says so, which is right. Add the two realised fractions so a reader can apply their own threshold:
5.23/6.24 = 0.84 (passes) and 2.71/6.67 = 0.41 (fails). As written a reader cannot tell whether the
GPL3290 failure was marginal.

**m12.** **§4.2's outcome table and §4.3's falsifier table overlap substantially.** F2 and F6 restate
rows 1–2 and 5–6 of the outcome table. Merging them would shorten the Discussion by half a page
without losing content, and would stop a referee reading the repetition as padding.

**m13.** **§8 names the DepMap release with no accession or DOI**, so the data-availability statement
does not in fact let a reader retrieve it. Same for the figshare files the release is distributed as.

**m14.** **The cover letter and the manuscript disagree about ORCID.** The cover letter states "no
ORCID accompanies this submission"; the manuscript title block carries "[ORCID TO BE SUPPLIED BY THE
AUTHOR BEFORE SUBMISSION]". Resolve to one before sending.

**m15.** **The editorial HTML comment block (currently between the abstract's scope statement and the
Abstract heading) must be deleted before submission.** It contains venue reasoning, fee-route notes
and instructions to the author. It is invisible in rendered Markdown and will not be invisible in a
converted submission file.

**m16.** **Register.** The running text of the manuscript and SI is clean — I found no glyph warnings,
no mid-sentence bold and no em-dashes in the body, and the repository's own style gate confirms it.
Three residues of the repository voice remain and are worth a pass: §3.4's "The two figures
illustrate the same methodological point in opposite directions", §4.1's "the gene-level cut makes it
more precise rather than less", and §4.4's "an argument is not a result" are all sentences about the
paper's own epistemic virtue rather than about the biology. One such sentence reads as rigour; three
begin to read as advocacy. The corrections appendices are correctly exempt and should stay as they
are.

**m17.** **§3.3's phrase "which is the expected profile for a biomarker rather than a target and
serves as the panel's internal control"** is doing two jobs in one clause and the second is
overstated. A gene being a non-dependency is consistent with it being a biomarker; it is not a
positive control for the panel in the sense the sentence implies. Split it.

---

## Revision list

Work through these in order. Every item is doable from data already committed; none requires a bench
experiment, a collaborator, or any spend.

1. `emc-mtap-prmt5-hypothesis.md` §2.3: replace "18,474 on GPL6244 and 14,402 on GPL3290" with
   "18,688 on GPL6244 and 14,404 on GPL3290", and add that on GPL3290 those 14,404 are of 14,932
   symbols carrying a probe.
2. `emc-mtap-prmt5-hypothesis-SI.md` §S10: same replacement in the sentence beginning "The same
   statistic is computed for every symbol".
3. `emc-mtap-prmt5-prepost.md`, "Multiple testing" row: same replacement.
4. `emc-mtap-prmt5-hypothesis.md` Appendix A: add a row registering 18,474 / 14,402 as superseded,
   with the artifact fields that own the correct values.
5. `emc-mtap-prmt5-hypothesis.md` §2.6: either re-verify every remaining number against its artifact
   and keep the verification sentence, or weaken it to name which classes of value were checked.
6. Run a max-statistic permutation correction over the full genome-wide *t* matrix on both platforms
   (extend `_genome_wide_null` in `emc_expression_panels.py`, or add a mode to
   `emc_prmt5_route_controls.py`); commit the adjusted *p* values to
   `emc-prmt5-route-controls.json`.
7. `emc-mtap-prmt5-hypothesis.md` §3.5, placement table: add an "adjusted *p*" column carrying the
   result of item 6 beside each gene's rank.
8. `emc-mtap-prmt5-hypothesis.md` §3.5, final paragraph: after "a *t* of *MTAP*'s size is not", add a
   sentence stating that a |*t*| of *PRMT5*'s size is not uncommon among the per-permutation maxima
   that arise when this many genes are scanned at this sample size, and give the adjusted value.
9. `emc-mtap-prmt5-hypothesis.md` Abstract: replace "exact permutation *p* = 0.000142 and 0.000125"
   with the exact *p* plus its multiplicity-adjusted counterpart on each platform; compress elsewhere
   to stay within 250 words (see item 30).
10. `emc-mtap-prmt5-hypothesis.md` §3.2, paragraph 2: weaken "The locus signal on the powered
    platform is *CDKN2A*" to state that *CDKN2A* carries what signal the locus score has, and that
    this reading does not survive multiplicity correction either; keep the *MTAP* closure as it
    stands, and add that *MTAP* is at an adjusted *p* of 1.00 on both platforms.
11. `emc-mtap-prmt5-hypothesis.md` §4.4, paragraph 1: after "with no correction for multiple
    testing", add one sentence naming which readings survive correction and which do not.
12. `emc-mtap-prmt5-hypothesis.md` §2.1, series table: add the reference-channel composition of
    GPL3290 (EMC and DFSP against a common reference, GIST against a universal human reference) and
    the comparator composition of both series (17 LGFMS / 6 desmoid fibromatosis / 6 fibrosarcoma;
    3 DFSP / 3 GIST).
13. `emc-mtap-prmt5-hypothesis.md` §3.6, paragraph after the control table: add a sentence naming the
    reference-channel difference as a candidate explanation for the GPL3290 proliferation result,
    ranked beside the biological one.
14. `emc-mtap-prmt5-hypothesis-SI.md` §S5: add the reference-matched sensitivity analysis: *PRMT5*
    *t* = 5.97 against the three reference-matched comparators and 4.32 against the three
    universal-reference comparators, versus 6.67 pooled; note *MAT2A* falling to 2.18.
15. `emc-mtap-prmt5-hypothesis.md` §3.5, placement table: for the *NR4A3* row on GPL3290, either
    delete it or annotate it "n = 9 versus 2; below the panel's own floor of three per arm".
16. `emc-mtap-prmt5-hypothesis.md` §3.5, paragraph beginning "The two controls do not behave alike" —
    replace the probe-placement sentence with one giving both candidate explanations and identifying
    the sample count as the measured one.
17. `emc-mtap-prmt5-hypothesis.md` §2.3 or §2.1: state the per-gene missingness on GPL3290 (578 of
    1,662 cached genes have a missing value; 51 have an arm below three) and state the differing
    minimum-arm-size floors of the panel path and the genome-wide path.
18. `emc-mtap-prmt5-hypothesis.md` §2.1: state that GSE24369 deposits 42 samples of which 35 were
    analysed, and name the exclusions: two pooled normal-tissue samples excluded by design, five
    solitary fibrous tumours excluded because the classifier carried no pattern for them.
19. `emc-mtap-prmt5-hypothesis.md` figure 4 caption and `emc_mtap_prmt5_figures.py`: redraw with the
    solitary fibrous tumour class included as a fifth class, or state its medians (+1.14 for *PRMT5*;
    highest of all classes on the pooled score) in the caption with the reason it is not plotted.
    Correct "four comparator classes" to "the four classes plotted".
20. `emc-mtap-prmt5-hypothesis-SI.md` §S5: add the exclusion sensitivity: including the five
    solitary fibrous tumours moves *PRMT5* from *t* = 6.24 to 6.31, *MTAP* from 0.69 to 0.70 and
    *CDKN2A* from −5.40 to −5.66.
21. `emc-mtap-prmt5-hypothesis.md` §3.7, fusion table: add the two further reported EWSR1::ATF1
    junctions with their retained-site counts (one retaining 4, one retaining 0), from
    `emc-prmt5-substrate-motif-map.json`.
22. `emc-mtap-prmt5-hypothesis.md` §3.7, paragraph beginning "The commonest EMC fusion and the
    commonest clear cell sarcoma fusion retain the same number of sites" — rewrite to state that two
    of three reported clear cell junctions retain four sites and one retains none.
23. `emc-mtap-prmt5-hypothesis.md` §3.3, paragraph 2: add the pan-DepMap figures for PRMT5 from
    `depmap-sarcoma-dependency.json`: 94.1% of non-sarcoma lines dependent, selectivity 0.013.
    Mirror in `emc-mtap-prmt5-hypothesis-SI.md` §S4's table as two extra columns.
24. `emc-mtap-prmt5-hypothesis.md` §3.6 control table, or `emc-mtap-prmt5-hypothesis-SI.md` §S5: add
    the pre-specified MKI67 cellularity control with both values (*t* = 0.53 on GPL6244; *t* = 2.30,
    +1.24 SD on GPL3290) and its pre-specified expectation of flatness.
25. `emc-mtap-prmt5-hypothesis-SI.md` §S5, paragraph 2: rewrite the control-block sentence to name
    the six genes actually in the block and their expectations; delete the reference to housekeeping
    recovery and to a comparator-high marker.
26. `emc-mtap-prmt5-hypothesis.md` §9: add references for: GSE24369's source publication; GSE4303's
    source publication; the DepMap 24Q4 release and the Chronos method; the transcript-type breakpoint
    sources recorded in `emc-fet-construct-designs.json`; the *ENO3* direct-target result recorded in
    `emc-expression-panels.json`; the indolent/slow-cycling natural history; the eight systemic
    classes; the EWSR1 activation-domain claim; the two published EMC models and the screen run on
    them; and a methylosome review for MEP50/WDR77.
27. `emc-mtap-prmt5-hypothesis.md` §2.5: name the breakpoint sources added in item 26 rather than
    "as reported in the sources".
28. Establish the current publication status of reference [2] by literature search, then rewrite
    §4.4's preprint paragraph to state what was found rather than that the check was not made. Update
    the reference if it has been published.
29. `emc-mtap-prmt5-hypothesis.md` §1.3: either give the modality census a citable form in §8 or
    remove "217 categories" and keep the qualitative claim.
30. `emc-mtap-prmt5-hypothesis.md` §2: expand to cover: sample classification and exclusion; arm
    composition; the *z*-score background definition (per-sample or per-series, all probes or mapped
    only); the multi-probe collapse rule; probe-to-symbol bridge construction and its resolution rate;
    missing-value handling in both paths; the two-colour reference channel; and the software and
    versions used. Move detail to the SI and point at it if §2 becomes unbalanced.
31. `emc-mtap-prmt5-hypothesis.md` Appendix A, row 1: change the citation "[2]" to "[3]".
32. `emc-mtap-prmt5-hypothesis.md` §3.1, sentence 2: delete the two GPL3290 percentiles, or annotate
    them as percentiles of a log-ratio distribution with no absolute interpretation.
33. `emc-mtap-prmt5-hypothesis.md` §3.6, paragraph 2: after "Eight family members are readable on
    GPL6244 and seven on GPL3290", add "counting *PRMT5* itself", so it no longer appears to
    contradict SI §S3.
34. `emc-mtap-prmt5-hypothesis.md` §2.5, or `emc-mtap-prmt5-hypothesis-SI.md` §S9: state that
    reference [8] was verified at abstract level and that its full text was not available
    open-access.
35. `emc-mtap-prmt5-hypothesis.md` §1.2: add "[sic]" inside the quotation "largely supressed by
    partial depletion of EWSR1::FLI1".
36. `emc-mtap-prmt5-hypothesis.md` Abstract, sentence 1: replace "for which no targeted agent exists"
    with the form reference [1] supports, that no clinically validated agent directly targets NR4A3.
37. `emc-mtap-prmt5-hypothesis.md` figure 5 caption: state that TAF15::NR4A3 is tabulated but not
    plotted, because it is a different 5′ protein and therefore a different ruler.
38. `emc-mtap-prmt5-hypothesis.md` §2.4, final sentence: add the two realised magnitude fractions,
    0.84 and 0.41, against the 60% threshold.
39. `emc-mtap-prmt5-hypothesis.md` §4.2 and §4.3: merge the outcome-interpretation table into the
    falsifier table, keeping every distinct row and deleting the duplicated ones.
40. `emc-mtap-prmt5-hypothesis.md` §8: add the DepMap release accession or DOI to the data
    availability table.
41. `emc-mtap-prmt5-hypothesis.md` §3.3, sentence 3: split "which is the expected profile for a
    biomarker rather than a target and serves as the panel's internal control" into two claims and
    weaken the second.
42. `emc-mtap-prmt5-hypothesis.md` §3.4, §4.1 and §4.4: remove two of the three sentences that
    comment on the paper's own epistemic standing, keeping the one in §4.4.
43. `emc-mtap-prmt5-hypothesis.md` title block: resolve the ORCID placeholder against the cover
    letter's statement that no ORCID accompanies the submission.
44. `emc-mtap-prmt5-hypothesis.md`: delete the editorial HTML comment block before any submission or
    conversion pass.
45. `emc-mtap-prmt5-hypothesis.md` title: consider dropping the third clause.
46. After items 6, 19 and 24, re-run `emc_mtap_prmt5_figures.py --check` so the provenance hashes
    match the regenerated artifacts, and re-run the document gates.
