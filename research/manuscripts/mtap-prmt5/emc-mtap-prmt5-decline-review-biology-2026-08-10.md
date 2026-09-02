---
id: DOC-EMC-MTAP-PRMT5-DECLINE-BIOLOGY
title: "Grounds to decline — domain biology lens (emc-mtap-prmt5-hypothesis.md)"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: An adversarial domain assessment hunting every scientific ground on which the PRMT5 manuscript would be declined.
scope: Review of one manuscript. Reports no new result and asserts nothing about any disease or agent.
audience: [maintainers, external reviewers]
date: 2026-08-10
last_verified: 2026-08-10
---

# Grounds to decline — domain biology lens

> **THIS IS A SIMULATED INTERNAL REVIEW, WRITTEN BY AN AI REVIEWER AT THE AUTHOR'S REQUEST. IT IS
> NOT CORRESPONDENCE FROM *GENES, CHROMOSOMES AND CANCER* OR FROM ANY OTHER JOURNAL, NOT A REAL PEER
> REVIEW, AND NOT A DECISION. No editor, no journal and no external referee has seen this
> manuscript. It exists to find the objections a sarcoma-biology referee would raise, before one
> does.**

Manuscript under review: `research/manuscripts/emc-mtap-prmt5-hypothesis.md`, with
`emc-mtap-prmt5-hypothesis-SI.md`, `emc-mtap-prmt5-hypothesis-cover-letter.md` and the five figures
in `research/manuscripts/figures/`.

Reviewer stance: FET-fusion sarcoma biology; arginine methylation and the PRMT5–MEP50 methylosome;
MTA-cooperative PRMT5 pharmacology; the 9p21 MTAP/CDKN2A locus. Round one of simulated review was
largely statistical and disclosure-focused, and its revision list was worked through carefully. This
review does not repeat it. It reads the biology, and it reads the manuscript's cited sources against
the verbatim full texts committed in this repository — the bioRxiv text behind reference [2]
(`literature/emc-post-degrader-options/prmt5_ccs_biorxiv_pdf.txt`), the Ewing paper [3]
(`literature/fet-arginine-methylation/PMC12354397.txt`), the EMC review [1]
(`literature/ct-reverify-c3b-2026-08-07/PMC12504171.txt`) and the EMC models paper [18]
(`literature/bangerter-2023-emc-exvivo/PMC9813045.txt`), all on the `literature-cache` branch — and
against the per-sample values in `research/modalities/emc-expression-panels.json`,
`emc-prmt5-substrate-motif-map.json`, `emc-prmt5-route-controls.json`, `emc-prmt5-multiplicity.json`
and `emc-cohort-search-inputs.json`.

---

## Verdict

**Decline in present form.** Not on integrity, not on arithmetic, and not on candour: the numbers I
re-derived from the committed artifacts reproduce, the corrections registers are honest, and the
paper's disclosure of its own weaknesses is better than most submissions. It fails on what it claims
to have established. The title, the abstract, section 4.1, the conclusion and the cover letter all
assert that one of the two rationales **survives**, and the evidence offered for that survival does
not survive being read against the two papers it is transferred from.

**The single strongest ground: the only new evidence the manuscript brings to the surviving
rationale — the retained-motif comparison of §3.7 — is arithmetically empty and is aimed at a
mechanism that neither cited source demonstrates.** EWSR1's eleven GRG sites are not spread through
the protein; four of them sit in one twenty-residue cluster (residues 301, 303, 316, 320) and the
next is 143 residues away at 463, so **every breakpoint anywhere in residues 321–462 retains exactly
four sites** — a 142-residue plateau covering 22% of the protein. Both breakpoints the manuscript
calls a match land inside it, 107 residues apart. The "match" is what the arithmetic returns for
almost any mid-protein cut. And the mechanism it is meant to make plausible — the fusion protein as
a PRMT5 substrate — is not what reference [2] reports: [2] describes PRMT5 as "a new EWSR1-ATF1
binding **co-activator**", evidenced by co-immunoprecipitation and promoter occupancy, and nowhere
shows that the fusion is methylated or maps the interaction to the EWSR1 portion. Remove the motif
comparison and the transfer reduces to "two other EWSR1-fusion sarcomas show PRMT5 dependence, EMC
is a third, nobody has looked". That is a legitimate reason to run an experiment. It is not a
rationale that survives testing, because nothing in this manuscript tested it.

**Does the fusion-class transfer survive? No — not in the form argued.** It survives only in the
weak form the manuscript explicitly says it has moved beyond (Appendix A: *"The transfer is argued
rather than assumed"*). Every element added to lift it above an assumption either carries no
information (grounds 1) or points at a mechanism the sources do not support (grounds 2 and 3).

A publishable paper is recoverable from this material, and I would want to see it: a bounded
negative on the MTAP locus, an honest statement of the transcript readings with their effect sizes,
and a hypothesis stated at the strength the evidence actually supports. That is a different paper
from the one submitted, and it needs a different title.

---

## GROUNDS TO DECLINE

### 1. §3.7, §4.1, §5, abstract — the retained-motif "match" is a degenerate statistic, and the paper's own figure shows it

**What is wrong.** §3.7 concludes that "The transfer between the two diseases, previously stated as
an assumption (Appendix A), therefore has quantitative content, and the content is a match at the
commonest junction of each disease". §4.1 and §5 carry it forward as one of the two things that
lifted the transfer above an assumption; the abstract states the counts. There is no quantitative
content. The retained-site count is a step function with one enormous plateau, and both breakpoints
sit on it.

**Evidence.** `emc-prmt5-substrate-motif-map.json` → `wild_type_proteins.EWSR1.positions.GRG` gives
the eleven sites as **301, 303, 316, 320, 463, 489, 564, 574, 591, 602, 635**. Four are one cluster
inside residues 301–320; the fifth is at 463. Therefore:

| retained 5′ residues | GRG sites kept | why |
|---|---:|---|
| ≤ 300 | 0 | before the cluster |
| 321 – 462 | **4** | after the cluster, before site 5 — a 142-residue window, 21.6% of the protein |
| 463 – 488 | 5 | one more |

EWSR1::NR4A3 type 1 cuts at 431. EWSR1::ATF1 exon 8 cuts at 324. Both are in the 321–462 window,
**107 residues apart**, and both therefore return 4. So do EWSR1::ATF1 exon 10 (348) and any other
junction in that third of the protein. Across all eight fusions the manuscript tabulates, the count
takes only three values — 0, 4, 5. Figure 5 draws the point unambiguously: every bar labelled "4
kept" carries the same four red ticks in the same place.

Two further problems in the same sentence. The manuscript attributes the agreement to "coincidence
of where the RGG boxes fall", which reads as though two independent cluster structures happened to
align; there is one EWSR1 and one cluster, and the only coincidence is that two breakpoints fell in
the same 142-residue gap. And the agreement is metric-dependent: on the RG axis the same artifact
gives type 1 **8** retained dipeptides against EWSR1::ATF1 e8's **7**, so on the axis the rest of
this repository counts, the two do not match.

**Classification: STRUCTURAL — survivable.** No revision makes a step function informative. The
paper survives by withdrawing the claim: state the plateau, state that the agreement is what the
cluster structure produces for most breakpoints, and delete "quantitative content" and the sentences
in §4.1, §5 and the abstract that rest on it. What remains of §3.7 — that the segment every EWSR1
fusion retains carries none of the sites — is a real and reportable sequence observation, and should
be the section's only conclusion.

---

### 2. §1.2, §3.7 — reference [2] shows binding and promoter occupancy, not methylation of the fusion, and does not localise the interaction to the EWSR1 portion

**What is wrong.** §1.2 sets up the transfer with: "Both fusions retain the same N-terminal EWSR1
segment, which is the region the sequence analysis of section 3.7 measures." That sentence asks the
reader to believe (a) that the shared EWSR1 segment is where PRMT5 acts, and (b) that §3.7 measures
that segment. Neither holds. §3.7's own finding is that the shared segment — EWSR1 residues 1–300,
the SYGQ-rich region every EWSR1 fusion retains — contains **no** GRG site; §3.7 measures the region
beyond it, which is exactly the region the fusions do *not* share. **The paper's shared part is
motif-free and its motif-bearing part is not shared.** The construction is self-defeating and a
referee will see it in one pass.

**Evidence, from the committed full text of [2].** The preprint's own summary of its finding is
"the identification of protein arginine methyltransferase 5 (PRMT5) as a new EWSR1-ATF1 **binding
co-activator** to stimulate its transcription activity". The supporting experiments are: interactome
proteomics; a Flag co-immunoprecipitation in HEK293T of an artificial EWSR1(2-325)–ATF1(66-271)
construct, in which "strong PRMT5 signal was detected in the M2 immunoprecipitate"; a ChIP in the
clear cell line DTC-1 showing that the c-Fos promoter CRE site "is also occupied by PRMT5"; and
shPRMT5 reducing c-Fos transcript and CRE reporter activity. The strings "methylation of EWSR1" and
"SDMA" do not appear in the document. No truncation or domain-mapping experiment localises the
PRMT5 interaction to any part of the fusion. In the same co-IP, **CREB1 was detected in the M2
complex**, which the authors attribute to heterodimerisation "through its bZIP domain that is
retained in EWSR1-ATF1" — that is, an equally good route into the complex through the *ATF1* half,
which EWSR1::NR4A3 does not have.

So the manuscript's §3.7 computes where a substrate motif falls in a protein that its load-bearing
source never proposed as a substrate, and §1.2 attributes the source's mechanism to a region the
source never implicated. §3.7's closing paragraph ("These counts do not show that any NR4A3 fusion
is methylated, that PRMT5 is the enzyme…") disclaims the substrate hypothesis while the sections
around it continue to argue from it.

**Classification: STRUCTURAL — survivable.** State plainly what [2] showed (binding, promoter
occupancy, transcriptional requirement) and what it did not (methylation of the fusion, any
domain mapping). Then §3.7 cannot be read as evidence for the transfer, and §1.2's sentence must be
rewritten or deleted.

---

### 3. §1.2, §4.1, §4.2 — reference [3]'s own proposed mechanism is Ewing-specific replication stress, and the manuscript never states it

**What is wrong.** [3] is now the paper's strongest support (§4.1: "a result in a second
EWSR1-fusion sarcoma shows a fusion-dependent PRMT5 requirement"). The manuscript describes what [3]
observed and omits what [3] concluded, and what [3] concluded does not transfer through EWSR1.

**Evidence, verbatim from [3].** "ES cells experience a high degree of replication stress and R-loop
formation due to **EWS-FLI1-dependent promotion of CDK9-mediated RNA Polymerase II activation**… Our
findings that PRMT5 is upregulated in ES cells contributing to genome stability and DNA repair after
replication stress is highly suggestive that PRMT5 is an unappreciated component of the ES cell
replication stress buffering system counteracting deleterious EWSR1::FLI1-induced replication
stress." And in the same figure as the fusion-dependence result: "ES cells are genetically BRCA1
wildtype, however the ability of the EWS-FLI1 fusion protein to sequester BRCA1 promotes HR
deficiency leading to olaparib sensitivity", with the measured consequence that "**olaparib was only
effective in reducing the survival of A673 cells when EWS-FLI1 was expressed**".

Both of those are properties of *EWS-FLI1* and of Ewing biology — the ETS half's transcriptional
output, and BRCA1 sequestration — not of the EWSR1 N-terminus the two diseases share. Nothing in
this manuscript, and nothing in the literature it cites, establishes that EWSR1::NR4A3 produces
comparable replication stress or R-loop burden. And because olaparib alone was also fusion-dependent
in the same system, "fusion-dependent" in [3] is a property shared by replication-stress agents
generally rather than a signature of a PRMT5-specific route into the fusion.

The manuscript's own citation record knows this: `research/literature/mtap-prmt5-emc-citations.json`
records for [3] that "the authors attribute PRMT dependence in this disease to replication stress
and R-loop formation driven by EWS-FLI1…". The manuscript mentions R-loops once, in §3.7, attributed
to [9] and in a different argument. A reader of the paper alone would not learn that the source's
mechanism is a disease-specific one.

**Classification: STRUCTURAL — survivable.** Adding the sentence weakens the transfer but does not
kill the paper; suppressing it is what a referee will not forgive, because the omitted sentence is
the one that decides whether the transfer is a fusion-class argument or a disease-specific one.

---

### 4. §3.2, §4.1, title, abstract — the MTAP rationale is not "closed"; it was tested with an instrument that cannot see the event, and the paper's own per-sample data holds the pattern it never reports

**What is wrong.** Two separable errors, and the second is the serious one.

**(a) A mean contrast cannot test a subset event.** Homozygous 9p21 deletion is present in some
tumours and absent in others. The manuscript knows this — §4.2 says "MTAP protein lost **in a
subset** would define a genetically selected group" — and then tests it with a difference in group
means (Welch's *t*) and a family-wise adjusted *p*. Those have almost no power against a minority
event: with reference [11] cited for MTAP loss reaching "up to 20% in various sarcomas", zero
deleted cases among six tumours is consistent with a frequency up to about **39%** at 95%
confidence, and zero among all sixteen with about **17%**. The manuscript nowhere states that its
test is mis-specified for its hypothesis.

**(b) The per-sample data is committed, is not reported, and contains a low tail on the ten-tumour
arm.** `emc-expression-panels.json` → `gene_reads.MTAP`, GPL3290: four of the ten EMC tumours sit at
array percentiles of **1.1%, 4.0%, 4.6% and 5.5%** for MTAP — below every comparator, the lowest of
which is at 11.0% — with log-ratios of −4.83, −4.14, −3.72 and −2.58. Two obvious rebuttals fail on
the same file. It is not the reference-channel confound: **all ten EMC tumours share one reference
label** (`CRH-mRNA`), so a split *inside* the EMC arm cannot come from the denominator. And it is
not array quality: those four samples carry 3.8%, 4.6%, 5.9% and 7.6% of their cached genes below
the 5th array percentile, inside a cohort range of 1.4%–8.9%.

§3.2 reports this platform as "−0.607 SD, opposite sign" and prints no *t* for it, while printing
*t* for the platform that shows nothing. The sign in question is **the sign the hypothesis
predicts**, on the arm with ten EMC tumours rather than six. Describing a hypothesis-consistent
direction as a "reversal" and closing the rationale on the other platform is a presentational choice
that buries the paper's only positive MTAP reading.

**(c) The discriminating check is free, is in the same file, and supports the authors — and they did
not run it.** If those four tumours carried 9p21 homozygous deletion, CDKN2A should fall with MTAP;
[5] is cited for exactly that co-deletion. It does not. In the same four samples CDKN2A sits at the
**73rd, 68th, 87th and 89th** percentiles of their own arrays — anti-correlated with MTAP, and the
opposite of a co-deletion pattern. On the six-tumour platform no EMC sample is a low MTAP outlier at
all (*z* +0.456 to +0.884, all above the array mean). **That** is a strong argument that no
deletion-like state is visible here, and it is a per-sample argument about a per-sample event. The
manuscript instead argues from a group mean and an adjusted *p*, which are the two statistics that
cannot address it.

**Classification: FIXABLE** (no new data, no spend), but the fix changes the title. Report the
per-sample tail, report the CDKN2A cross-check, state the binomial bound, and replace "closed" and
the title's "an MTAP-locus rationale that does not [survive]" with "not supported, and not testable
at transcript level in sixteen tumours".

---

### 5. §3.2 — "the closure of this rationale is exactly what an adjusted *p* of 1.00 states" is an evidence-of-absence error, contradicted by the paper's own SI and by its own controls

**What is wrong.** §3.2 writes that MTAP's adjusted *p* of 1.00 "is the one place in this paper
where correcting for the number of genes examined strengthens the argument rather than weakening it:
the closure of this rationale is exactly what an adjusted *p* of 1.00 states." An adjusted *p* of
1.00 states that a statistic this large arises in essentially every permuted labelling. It is a
failure to reject. It is not a measurement that anything is absent.

**Evidence, from inside the same submission.** SI §S5c says so in terms: "An adjusted *p* is a
statement about how often a labelling of these samples produces a statistic this large somewhere in
the family. **It is not a statement that a reading is absent**, which matters most for the two
controls that read as expected and still do not clear a threshold." And
`emc-prmt5-multiplicity.json` → `max_statistic_permutation.adjusted_p` returns **0.85 for NR4A3 on
GPL6244** — the pathognomonic driver transcript, definitionally over-expressed by the fusion in
every one of these tumours — and **1.00 for ENO3 on GPL6244**, a published direct transactivation
target. A procedure that cannot detect the fusion transcript in the disease the fusion defines
cannot be quoted as stating a negative about anything else.

**Classification: FIXABLE.** Delete the sentence. Keep the adjusted values and describe them as the
SI already does. The closure argument should rest on ground 4(c), which is a real observation.

---

### 6. §1.2, §4.1, §4.3 F2 — the fusion-dependence result the transfer now rests on is one engineered line, one partial knockdown, and a growth readout that cannot exclude a growth-rate confound

**What is wrong.** The manuscript presents [3]'s result as "a fusion-dependent PRMT5 requirement
measured in a disease that is not EMC", and F2 makes the transfer's reasonableness turn on it. The
design is not described anywhere in the manuscript, and the design is the objection.

**Evidence, verbatim from [3].** A single engineered line: "we focused on the engineered A673 cell
line utilised in the ESCLA dataset (A673-tetON-shEWSR1::FLI1) that **enables controllable
suppression of the oncogenic fusion without a major compromise in cell viability**". A partial
depletion: "the effects of single agent GSK591 and MS023 were largely supressed by **partial
depletion** of EWSR1::FLI1". A growth readout: viable cell number by trypan blue exclusion after
four days. A partially fusion-depleted Ewing line proliferates more slowly, and the measurable
effect of any antiproliferative agent shrinks with it.

This is precisely the confound the manuscript itself sets up in §3.3 — PRMT5 loss is
antiproliferative in ~95% of all screened lines, so a growth effect is close to expected — and then
does not apply to the experiment it leans on hardest. §4.1 and F2 should carry the design and the
confound in one sentence each.

**Classification: FIXABLE.**

---

### 7. §4.2, abstract — the principal proposed experiment measures the endpoint the paper itself says is uninformative

**What is wrong.** §3.3 states the criterion: "the part that could be specific to this disease, and
the part any transfer must rest on, is **the effect on fusion-driven transcription rather than on
growth**." §4.2 then proposes "one clinical-stage PRMT5 inhibitor added to a screen already running
on published EMC models", which is a viability screen, and asserts that this "tests the surviving
rationale directly". It does not. A growth effect is the expected result in ~95% of lines of any
lineage (§3.3, SI §S4), so the positive branch of the paper's principal experiment discriminates
nothing — as F8 concedes in a different section. The paper's own precedent for the right readout is
in [2]: a CRE-driven reporter and c-Fos qPCR. Neither that, nor a concurrently run non-EMC
comparator line, is in the proposed design.

A second, smaller inaccuracy in the same sentence: [18] reports a **completed** 40-agent panel on
two established models. Whether that screen "already runs" today is a statement about another
group's current activity, and it is presented as fact in the abstract and in §4.2.

**Classification: FIXABLE.** Specify the readout as fusion-output plus viability, specify a
concurrent non-EMC comparator, and drop the claim that a screen is currently running.

---

### 8. §4.2, §1.2 — the inhibitor class is unspecified, and the paper's own two sources give opposite answers by class

**What is wrong.** "One clinical-stage PRMT5 inhibitor" is not an experiment; it is three or four
different experiments depending on which compound is chosen, and the manuscript's own two sources
already show that the choice decides the outcome.

**Evidence.** [2] tested three PRMT5 inhibitors "representing two different modes of inhibition":
GSK591 and GSK3326595 bind the substrate pocket; JNJ-64619178 binds the SAM and substrate pockets
together. The result, verbatim: "GSK591 and GSK3326595 were **only weakly active** in DTC-1 and
SU-CCS-1 cells with GI50s in the **high µM concentration range**", and "**neither of these two
substrate-competitive inhibitors significantly inhibited EWSR1-ATF1's transcription activity**". Only
JNJ-64619178 was potent, and even it spanned a 100-fold range across the three lines (GI50 41.0,
438.5 and 4.4 nM). [3], meanwhile, obtained its fusion-dependent effect with GSK591 — a
substrate-competitive compound of the class that failed in clear cell sarcoma.

Two consequences. §1.2's description of [2] — "a clinical-stage PRMT5 inhibitor inhibited growth in
vitro and in vivo" — is true of one of the three compounds tested and omits that a second
clinical-stage PRMT5 inhibitor in the same experiment was weakly active in two of three lines. That
is a cited result described more favourably than its source supports. And a negative result in an
EMC model with a substrate-competitive compound would be uninterpretable, because the transfer's own
source disease already produced that negative.

Separately, the manuscript's two rationales require different agent classes and it never says so: an
MTA-cooperative inhibitor of the class [4] is cited for depends on MTA accumulation in MTAP-deleted
cells and is the wrong tool in MTAP-intact models, whereas the fusion rationale calls for a
first-generation compound.

**Classification: FIXABLE.** Name the compound and its class, and state which rationale each class
tests.

---

### 9. §4.2, §4.3 F10 — the two-construct experiment cannot be run on the published models, and could not attribute a difference to motif count if it were

**What is wrong.** §4.2 claims EMC "answers this more cleanly than any other disease in the family,
because its transcript types differ in retained motif count while sharing a driver, with type 1
retaining four GRG sites and type 2 none. Comparing PRMT5 inhibition across the two separates the
mechanisms." Both halves fail.

**Evidence.** The two published models of [18], which §4.2 nominates as the vehicle, are
**USZ20-EMC1, carrying EWSR1-NR4A3, and USZ22-EMC2, carrying TAF15-NR4A3**; no transcript type is
reported for either. There is no published type 2 EWSR1::NR4A3 model to compare against. If the
available pair is used instead, the contrast is EWSR1 against TAF15 — a different 5′ protein — and
the manuscript's own §3.7 table already gives TAF15::NR4A3 zero retained sites, so any difference is
confounded by the entire N-terminal partner.

Even the intended pair is confounded by design. From `emc-prmt5-substrate-motif-map.json`, type 1 is
EWSR1 exon 12 :: NR4A3 exon 3, retaining 431 EWSR1 residues, 1058 aa total; type 2 is EWSR1 exon 7
:: NR4A3 exon 2, retaining 264 residues, 949 aa total. The two differ by **167 residues of the EWSR1
transactivation region and in the NR4A3 moiety itself**. A difference in PRMT5 sensitivity between
them is attributable to fusion potency, protein stability or NR4A3 content at least as readily as to
four glycine-flanked arginines. F10's pre-specified reading — "type 1 responding and type 2 not
would make the fusion protein the substrate and define a transcript-type group" — therefore does not
follow from the experiment described. The only design that isolates the motif is a site-directed
arginine substitution within one construct, which is not proposed (and, correctly, could not be by
this author).

**Classification: STRUCTURAL — survivable by deletion.** As written it is offered as one of two
"decisive experiments"; it is not decisive and is not runnable. Either delete it or restate it as
requiring isogenic engineered constructs and a motif mutant, and say that neither exists.

---

### 10. §3.4, §3.5, §4.1 — the instrument's own positive control under-performs the test gene, and effect size and overlap are never reported

**What is wrong.** The manuscript reports contrasts in *t* and in *z*-units and never in fold-change
or in sample overlap, and on both measures the primary reading is small and the positive control is
weak.

**Evidence,** recomputed from `gene_reads[*].per_sample` on GPL6244:

| gene | Δ (*z*) | raw log2 difference | fold | comparators at or above the lowest EMC sample |
|---|---:|---:|---:|---:|
| *NR4A3* (the disease-defining fusion transcript) | +0.742 | +1.457 | ≈2.7× | 5 of 29 |
| *PRMT5* | +0.263 | +0.544 | ≈1.5× | 7 of 29 |

Two readings follow. First, a series in which the pathognomonic driver separates EMC only ~2.7-fold
with 17% sample overlap has a compressed dynamic range, and a ~1.5-fold PRMT5 difference sits inside
it. Second, PRMT5's larger *t* comes from an unusually tight EMC arm (SD 0.081 *z* against the
comparator arm's 0.115), not from separation: seven of twenty-nine comparator tumours read above the
lowest EMC tumour. "*PRMT5* alone does [separate]" (§3.4), "*PRMT5* alone separates it from the other
tumour classes" (§4.1) and the same phrase in the cover letter are true of class medians and false
of samples. Set beside the manuscript's own creditable observation that the two pooled
skeletal-muscle references read *above* EMC on PRMT5, what the data supports is "a ~1.5-fold higher
median on a within-array rank scale", which is a much smaller statement than the paper makes.

**Classification: FIXABLE.** Report fold-change and overlap beside every *t*; replace "separates"
with a statement about medians.

---

### 11. §2.1, SI §S1 — the 35-tumour series is a study of a different disease in which EMC is a morphological control, and neither series is stated to be fusion-confirmed

**What is wrong.** The manuscript calls GPL6244 "the powered platform" and builds the surviving
rationale on it, describing GSE24369 only as 6 EMC against "17 low-grade fibromyxoid sarcoma, 6
desmoid fibromatosis, 6 myxofibrosarcoma". It does not say what the series is.

**Evidence.** The deposited summary, committed in `research/modalities/emc-cohort-search-inputs.json`
under `GSE24369`, reads: "Analysis of gene expression in **17 low-grade fibromyxoid sarcoma (LGFMS)
samples compared to that of histologically similar tumors**… The results identifies a LGFMS-specific
gene expression profile". The same record carries `"pubmed": null`.

So the six EMC cases were assembled as **morphological mimics of another entity**, not as a
consecutive or representative EMC series; and the seventeen-sample class the manuscript uses as its
FET-fusion control is the original study's index arm. Selection on myxoid morphology is not a
neutral selection for a paper making a transcript claim about EMC. Compounding it, neither §2.1 nor
SI §S1 states whether NR4A3 rearrangement was confirmed in any case in either series — and EMC's
differential diagnosis is precisely the myxoid tumours sitting in the comparator arm. A journal whose
readership is fusion diagnostics will ask.

**Classification: FIXABLE** by disclosure. State the series' design and index disease, state that
the EMC cases are archival diagnoses of unstated molecular confirmation, and treat the NR4A3 control
of §3.5 as the only available evidence bearing on it.

---

### 12. §3.6 — the "chondroid lineage" control is premised on a lineage this tumour does not have, and the manuscript's own reference [1] says so

**What is wrong.** §3.6's third control asks whether PRMT5 moves with COL2A1, COL9A1, COL11A2, SOX5
and SOX6, and its stated residual limitation is that "it cannot exclude that chondroid tumours
generally express *PRMT5*". EMC is not a chondroid tumour.

**Evidence, verbatim from [1]**, which the manuscript cites for the disease: "**Despite its name, EMC
does not exhibit true cartilaginous differentiation and is now classified as a mesenchymal tumour of
uncertain differentiation rather than a conventional chondrosarcoma.**" The same review notes only
that "some tumours show areas of chondroid metaplasia".

As written, the control tests co-expression with markers of a differentiation programme the index
tumour does not have — so a null is uninformative rather than reassuring — and its stated limitation
is about a class EMC is not in. More important for the readership: **the manuscript never tells the
reader that the disease's name is not its lineage**, which is the first thing a sarcoma pathologist
checks and which bears directly on the choice of comparator arms (none of which is cartilaginous
either, as §3.6 correctly notes).

**Classification: FIXABLE.** State the lineage fact with its citation, and reframe the control as
what it is — a check against myxoid/matrix-associated transcription — or drop it.

---

### 13. §3.6 — PRMT1 is flat in EMC on both platforms, which is a disanalogy with the disease the transfer comes from, and it is not reported

**What is wrong.** The PRMT-family control is used only to show that PRMT5's elevation is not
family-wide. The same table carries a reading that cuts against the transfer and is not mentioned.

**Evidence.** `emc-prmt5-route-controls.json` → `prmt_family_specificity`: **PRMT1 *t* = 0.175 on
GPL6244 and 1.358 on GPL3290** — flat on both. [3]'s premise is that "the expression and activity of
the arginine methyltransferases **PRMT1 and PRMT5** are elevated in Ewing sarcoma", and its largest
effect is the *combination* of PRMT1 and PRMT5 inhibition (91% viability reduction in A673 against
modest single-agent effects; single-agent GSK591 induced only "a low level of apoptosis"). So the
co-elevated enzyme that carries half of the source's mechanism is not elevated here, and §4.2's
proposed single-agent experiment omits the arm that produced the source's effect. One of those two
facts belongs in §3.6 and the other in §4.2.

**Classification: FIXABLE.**

---

### 14. §3.7, abstract — the fusion denominators are incomplete on both sides, and one of them is contradicted by the manuscript's own source

**What is wrong.** The abstract and §3.7 state that "two of three reported clear cell fusions retain
four". Round one corrected this analysis from one junction to three; the denominator is still not
the reported set.

**Evidence.** [2], the source of the clear cell rationale, states: "Besides the initial discovery of
type 1 EWSR1-ATF1 fusion in CCSST patients, **6 other types of EWSR1-ATF1 fusion and EWSR1-CREB1**
have also been reported in CCSST patients." EWSR1::CREB1 — a recognised fusion of this tumour family
— appears nowhere in the manuscript. "Three reported clear cell fusions" is a count of the junctions
this repository happens to hold, presented as a count of the reported set.

The EMC side is incomplete in the same way. [1] names "EWSR1::NR4A3, TAF15::NR4A3 and **FUS::NR4A3**"
as common EMC fusions and also lists TCF12::NR4A3; §3.7 tabulates three EWSR1 types and TAF15 only,
and FUS is not among the wild-type proteins in `emc-prmt5-substrate-motif-map.json` at all — although
FUS is a FET protein with its own RGG content and is therefore the most informative missing row in
the table.

**Classification: FIXABLE.** Say "the three junctions recorded in the source artifact" rather than
"the three reported fusions", or compute the missing ones. Given ground 1, neither changes the
conclusion — which is itself the argument for saying so.

---

### 15. Abstract, §1.3, cover letter — the priority claim is categorical where the evidence is conditional, and its most dangerous counterexample sits inside the paper's own strongest citation

**What is wrong.** §1.3 is careful and correct: it narrows to "nothing indexed pairs the PRMT5
methylosome with extraskeletal myxoid chondrosarcoma", states that the screen matched titles and
abstracts, and says an absence in it is not proof that no such work exists. The abstract states
flatly "**No indexed study examines the PRMT5 methylosome in this histology**", and the cover letter
repeats the flat form. A referee reads the abstract.

**What I checked, and it partly supports the authors.** I searched every full text on the
`literature-cache` branch that names this histology for PRMT5, MEP50 or methylosome terms. The only
co-occurrence is a search-result index containing a general epigenetics review; **no cached paper
carries a PRMT5, MEP50 or methylosome result for EMC.** The narrow form of the claim survives this
repository's own corpora.

**The unchecked counterexample.** [3]'s methods describe the expression comparison behind its
pan-sarcoma statement as drawn from a dataset of "**7 different fusion positive sarcoma subtypes**
including n=24 EWSR1-FLI1 and n=4 EWSR1-ERG" — only two of the seven are named. If EMC is among the
other five, then an indexed, peer-reviewed paper has already plotted PRMT5 and MEP50 in this
histology, and the paper's priority sentence is false in the very citation it calls its strongest.
The manuscript does not check, and it is the single check most likely to falsify its own claim.

**And the framing is less novel than presented.** [3] already proposes, for its own disease, *both*
of the rationales this manuscript presents as the two that would put the methylosome in front of a
FET-fusion sarcoma: the fusion as a selection marker for first-generation PRMT5 inhibitors ("the
fusion itself could potentially serve as predictive biomarker for responses to first-generation
PRMT5 inhibitors") and MTAP-deleted selection for second-generation MTA-cooperative inhibitors,
noting that "12% of patients have CDKN2A deletion, an event that often leads to co-deletion of MTAP"
and pointing at a running adult-sarcoma study of that class. The intellectual structure of this
manuscript is a transposition of that discussion to another disease. That is a legitimate thing to
publish; presenting it without saying so is not.

**Classification: FIXABLE.** Bring the abstract and cover letter into line with §1.3's wording,
resolve the seven-subtype panel, and add one sentence crediting [3] with having raised both
rationales for its own disease.

---

### 16. §4.2, §4.3 F6 — MTAP immunohistochemistry is proposed as decisive on a one-directional validity statement

**What is wrong.** §4.2 justifies the stain with [11]: "homozygous deletion was found in 90% to 100%
of cases with complete MTAP expression loss, checked against FISH". That is the predictive value of
**loss → deletion**. F6 then uses the converse as the falsifier — "MTAP immunohistochemistry retained
across an EMC series" is offered as decisive, and as confirmation "that the locus reading was a
*CDKN2A* shadow". The converse requires sensitivity (deletion → loss), which the manuscript does not
give and [11] is not cited for; MTAP protein can also be lost non-deletionally, and staining can be
heterogeneous in an archival series.

The defence available to the authors is a good one and should be made explicitly rather than in
passing: an MTA-cooperative agent depends on the metabolic consequence of MTAP **protein** loss, so
protein is the correct analyte regardless of mechanism — while noting that the class's clinical
selection, per [4], is on *MTAP deletion*, so a stain and a trial's entry criterion are not the same
test.

Related wording: F6 and SI §S7 describe the low locus score as a "*CDKN2A* shadow". No evidence of a
*CDKN2A* genetic event is presented anywhere — the reading is a ~1.9-fold transcript difference with
no sample at floor — and "shadow" implies an event casting it.

**Classification: FIXABLE.**

---

### 17. §1.2, §4.4, §9 — reference [2] is now cited as a peer-reviewed paper whose record could not be retrieved, while its load-bearing statements were read only from the preprint

**What is wrong.** §4.4 discloses this properly. §1.2, where the statements are actually used, does
not, and the reference list presents a full journal record. The committed retrieval record
`research/literature/prmt5-ccs-preprint-publication-status-2026-08-10.json` carries
`⛔_verification_level: "[SE] SEARCH-INDEX ONLY"` and records that the publisher page, the PMC record,
the bioRxiv page and the institutional repository were all unreachable from the working environment.
So the manuscript attributes to a peer-reviewed version statements it read in a 2022 preprint, on a
bibliographic record it could not confirm, and it removed the "not certified by peer review" caveat
on that basis. Given ground 8 — the inhibitor-class result is the most consequential thing in that
source and is read from the preprint alone — this matters more than it looks.

Minor, same class: `mtap-prmt5-emc-citations.json` records reference [10] as "[MD] metadata read from
the retrieved Europe PMC record; full text not retrieved… TITLE-LEVEL ONLY". §2.5 discloses the
metadata-level verification of [8] and says nothing about [10], which §3.7 uses for the premise that
EWSR1 is extensively arginine-methylated.

**Classification: FIXABLE.**

---

### 18. §3.6, SI §S5a — the GPL3290 proliferation confound may sit in the comparator arm, and both readings are available

**What is wrong.** §3.6 narrates the GPL3290 disagreement as EMC being more proliferative. The
per-sample values do not clearly say that.

**Evidence.** `gene_reads.MKI67`, GPL3290: the nine EMC tumours with a value sit at array percentiles
of 6–30%, and the six comparators at 0–18%, with two comparator values at *z* = −3.72 and −3.88. Both arms are
below their arrays' means; the pooled *t* = 2.30 is carried by two extreme comparator values rather
than by high proliferation in EMC. SI §S5a already shows MKI67 falling to *t* = 1.09 against the
label-matched half. The manuscript reports the split and still narrates the confound in the other
direction.

**Classification: FIXABLE.** One sentence in §3.6.

---

## Round-one response claims I checked and found overstated

**(a) The review response declines to cite the EWSR1 activation-domain claim on a false premise, and
the sentence that replaced it is the one at issue in ground 2.** `emc-mtap-prmt5-hypothesis-review-response-2026-08-10.md`,
M8 item 4, declines the citation "[r]ather than cite a source this repository does not hold", and
Appendix A records the removal of "the EWSR1 portion supplies the activation domain" as uncited. The
repository does hold a source, and the manuscript already cites it: reference [1], whose committed
full text states that the fusion "produces a chimeric protein that has the **transactivation domain
of EWSR1** and the DNA binding domain of NR4A3". A correct, citable sentence was deleted and
replaced by "Both fusions retain the same N-terminal EWSR1 segment, which is the region the sequence
analysis of section 3.7 measures" — which is both misleading (§3.7 measures the region beyond the
shared segment) and loose (the retained segments are 431 and 324 residues, not the same segment).

**(b) The same reference also supports the natural-history claim that Appendix A removed as
uncited.** [1] states "Mitotic activity is usually low" and describes the course as "indolent yet
metastasising". §1.1 now carries a hedged expectation and an *MKI67* control instead. That is
defensible, but the register of the change — a claim withdrawn for want of a citation that the
paper's own reference supplies — recurs across items and understates the reference list's reach.

**(c) "Its status since 2022 was not established here" is closed on a search-index record only.** The
response reports the preprint's publication as "Accepted and closed", and "'Not certified by peer
review' is removed from §1.2 and §4.4 because it is no longer true". The supporting artifact records
that nothing at the publisher, PMC, bioRxiv or the institutional repository could be retrieved. The
status is *believed*, not established, and §1.2 no longer carries any caveat. See ground 17.

**(d) M6 is described as "Accepted in full" but the denominator problem is one level up.** The
response reports all three recorded EWSR1::ATF1 junctions, which is what the artifact holds. [2]
itself reports seven types plus EWSR1::CREB1. See ground 14.

**Claims I checked that hold.** The multiplicity values (0.208, 0.238, 0.508, 0.850, 0.0097, 1.00)
reproduce exactly against `emc-prmt5-multiplicity.json`. The per-class medians correcting the
round-one reviewer reproduce (solitary fibrous tumour +1.0525 against desmoid +1.0508 and EMC
+1.3044). The reference-channel composition, the 578/1,662 missingness figures, the exclusion
sensitivity (6.24 → 6.31; 0.69 → 0.70; −5.40 → −5.66), the DepMap selectivity figures and the
retained-residue and site counts in §3.7 all reproduce against the named artifacts. Figure 5 does
plot all three clear cell junctions. The register of both files is clean.

---

## Fix list

Only the FIXABLE items. Each is doable from data already committed, with no new experiment and no
spend.

1. `emc-mtap-prmt5-hypothesis.md` §3.2 — delete "the closure of this rationale is exactly what an
   adjusted *p* of 1.00 states"; replace with SI §S5c's own formulation that an adjusted *p* is not a
   statement that a reading is absent. (Ground 5)
2. `emc-mtap-prmt5-hypothesis.md` §3.2 — print the GPL3290 *MTAP* *t* (−2.27) in the locus table
   beside its Δ, and stop describing the hypothesis-consistent direction on the ten-tumour arm as a
   "reversal" without its statistic. (Ground 4b)
3. `emc-mtap-prmt5-hypothesis.md` §3.2 and SI §S3 — add the per-sample *MTAP* reading on GPL3290:
   four of ten EMC tumours at array percentiles 1.1%, 4.0%, 4.6% and 5.5%, below every comparator
   (lowest 11.0%), all ten sharing one reference label, and those four samples not globally low
   arrays. (Ground 4b)
4. `emc-mtap-prmt5-hypothesis.md` §3.2 and §4.1 — add the *CDKN2A* cross-check in those same four
   samples (73rd, 68th, 87th, 89th array percentiles) and make it the argument for the closure, in
   place of the adjusted-*p* argument. (Ground 4c)
5. `emc-mtap-prmt5-hypothesis.md` §3.2, §4.1, §4.3 F5/F6 and the **title** — replace "closed" with
   "not supported, and not testable at transcript level in sixteen tumours"; add the binomial bound
   (0 of 6 is consistent with a frequency to ~39%, 0 of 16 to ~17%, against [11]'s "up to 20% in
   various sarcomas"). (Ground 4a)
6. `emc-mtap-prmt5-hypothesis.md` §3.7 — add the GRG position list and state the plateau: sites at
   301, 303, 316, 320 then 463, so any breakpoint in residues 321–462 retains exactly four. (Ground 1)
7. `emc-mtap-prmt5-hypothesis.md` §3.7, §4.1, §5 and the abstract — delete "has quantitative
   content" and every sentence that offers the retained-count match as support for the transfer.
   (Ground 1)
8. `emc-mtap-prmt5-hypothesis.md` §3.7 — note that on the RG axis the same two fusions retain 8 and 7
   dipeptides, so the agreement is metric-dependent. (Ground 1)
9. `emc-mtap-prmt5-hypothesis.md` §1.2 — rewrite or delete "Both fusions retain the same N-terminal
   EWSR1 segment, which is the region the sequence analysis of section 3.7 measures"; restore the
   activation-domain statement with its citation to [1]. (Grounds 2 and (a))
10. `emc-mtap-prmt5-hypothesis.md` §1.2 and §3.7 — state what [2] showed (interactome, co-IP,
    promoter occupancy, shRNA effect on fusion-driven transcription) and what it did not (methylation
    of the fusion; any domain mapping), and note that CREB1 enters the same complex through the
    retained ATF1 bZIP. (Ground 2)
11. `emc-mtap-prmt5-hypothesis.md` §1.2 and §4.1 — state [3]'s own proposed mechanism (PRMT5 in the
    replication-stress response buffering EWSR1::FLI1-driven CDK9/RNA Pol II activation and R-loops;
    BRCA1 sequestration) and that olaparib alone was also fusion-dependent in the same system.
    (Ground 3)
12. `emc-mtap-prmt5-hypothesis.md` §1.2, §4.1 and F2 — state [3]'s design: one engineered line, partial
    fusion knockdown, four-day viable-cell readout; and name the growth-rate confound. (Ground 6)
13. `emc-mtap-prmt5-hypothesis.md` §4.2 and abstract — specify the readout as fusion-driven
    transcription plus viability, add a concurrent non-EMC comparator, and delete the claim that a
    screen "already runs". (Ground 7)
14. `emc-mtap-prmt5-hypothesis.md` §4.2 — name the inhibitor and its mechanistic class, and record
    that [2] found both substrate-competitive compounds only weakly active and without effect on
    EWSR1-ATF1 transcription while [3]'s result used one of them. State that the MTAP rationale
    requires an MTA-cooperative agent and the fusion rationale a first-generation one. (Ground 8)
15. `emc-mtap-prmt5-hypothesis.md` §1.2 — correct the description of [2] from "a clinical-stage PRMT5
    inhibitor inhibited growth" to name how many were tested and how the others behaved. (Ground 8)
16. `emc-mtap-prmt5-hypothesis.md` §3.5 table and §3.4 — add fold-change and the count of comparator
    samples at or above the lowest EMC sample for *PRMT5* (≈1.5×, 7 of 29) and *NR4A3* (≈2.7×, 5 of
    29); replace "*PRMT5* alone separates it" with a statement about class medians. (Ground 10)
17. `emc-mtap-prmt5-hypothesis.md` §2.1 and SI §S1 — state that GSE24369 is a low-grade fibromyxoid
    sarcoma study in which EMC is one of the "histologically similar tumors", quoting the deposited
    summary; state that GEO carries no linked publication; state that molecular confirmation of the
    EMC diagnoses is not recorded in either deposit. (Ground 11)
18. `emc-mtap-prmt5-hypothesis.md` §1.1 or §3.6 — state, with [1], that EMC does not exhibit true
    cartilaginous differentiation and is classified as a tumour of uncertain differentiation; reframe
    the chondroid control accordingly and delete the "chondroid tumours generally express *PRMT5*"
    limitation. (Ground 12)
19. `emc-mtap-prmt5-hypothesis.md` §3.6 and §4.2 — report *PRMT1* at *t* = 0.175 and 1.358 as a
    disanalogy with [3], and note that [3]'s largest effect was the PRMT1 + PRMT5 combination.
    (Ground 13)
20. `emc-mtap-prmt5-hypothesis.md` §3.7 and abstract — say "the three junctions recorded in the source
    artifact" rather than "three reported clear cell fusions", note [2]'s statement of seven types
    plus EWSR1::CREB1, and note that FUS::NR4A3 and TCF12::NR4A3 are reported EMC fusions not
    tabulated here. (Ground 14)
21. `emc-mtap-prmt5-hypothesis.md` abstract and `...-cover-letter.md` — bring the priority sentence
    into line with §1.3's conditional wording. (Ground 15)
22. `emc-mtap-prmt5-hypothesis.md` §1.3 or §4.1 — resolve whether EMC is among the seven
    fusion-positive sarcoma subtypes in the expression panel [3] draws on, and record the answer;
    add one sentence crediting [3] with raising both rationales for its own disease. (Ground 15)
23. `emc-mtap-prmt5-hypothesis.md` §4.2 and F6 — state that [11]'s cited validity runs loss →
    deletion, that a retained stain excludes the protein-loss state the window selects on rather than
    excluding 9p21 deletion, and that [4]'s clinical selection is genomic; drop "*CDKN2A* shadow" or
    say it is a transcript reading with no evidence of a *CDKN2A* event. (Ground 16)
24. `emc-mtap-prmt5-hypothesis.md` §1.2 and §9 — carry the reference [2] verification caveat at the
    point of use, not only in §4.4; add reference [10]'s title-level verification to §2.5 or SI §S9.
    (Ground 17)
25. `emc-mtap-prmt5-hypothesis.md` §3.6 — note that the GPL3290 *MKI67* signal is carried by two
    extreme comparator values and that both arms sit below their arrays' means, so the confound may
    be a comparator measurement artefact. (Ground 18)
26. `emc-mtap-prmt5-hypothesis.md` §4.2 and F10 — delete the two-construct experiment, or restate it
    as requiring isogenic engineered constructs plus a motif mutant, recording that the two published
    models are EWSR1::NR4A3 and TAF15::NR4A3 rather than type 1 and type 2. (Ground 9; the design
    itself is structural, only the honest restatement is fixable.)
