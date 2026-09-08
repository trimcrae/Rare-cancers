---
id: DOC-EMC-TXN-PROTEOSTATIC
title: Transcriptional and proteostatic dependency of a fusion transcription factor — what a no-wet-lab program can and cannot establish
level: L3
kind: manuscript
status: live
canonical_for: ["the 2026-08-09 EMC transcriptional-CDK and chaperone dependency readings"]
purpose: >
  Test two dependencies that the structure of this disease's driver predicts — on the general
  transcriptional machinery, and on the chaperone system — and report that abundance and dependency
  disagree for both, in opposite directions, with the dependency axis deciding each time.
scope: >
  L3. Two public archival expression series, 16 EMC tumours, transcript level only, plus a public
  sarcoma-line CRISPR dependency panel containing no EMC line. Reports no experiment in EMC cells, no
  drug exposure and no patient.
audience: [maintainers, external reviewers, autonomous research agents, collaborators]
date: 2026-08-09
last_verified: 2026-09-08
related: [DOC-MODALITY-CENSUS, DOC-EMC-BIOMARKER-SELECTED]
---

# Transcriptional and proteostatic dependency of a fusion transcription factor

**Tristan D. McRae**

Independent researcher, unaffiliated. Correspondence: trimcrae@gmail.com.
ORCID 0000-0002-1823-1451.

*Study type: a computational study of public archival tumour-expression series and a public
sarcoma-line CRISPR dependency panel. No experiment was performed, no cell was cultured, and no new
recruitment, sampling or clinical intervention was undertaken. The records analysed here were
deposited publicly by others.*

> ⛔ **Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness for any agent
> in any disease.** This paper reads public transcript data from 16 archival tumours and a public
> dependency panel containing no cell line from this disease.

---

## Summary

Extraskeletal myxoid chondrosarcoma (EMC) is driven by an *NR4A3* gene fusion, most often
**EWSR1::NR4A3**. Two dependencies follow from what that driver *is*, and neither had been assessed in
this disease:

**The driver's entire mechanism is transactivation.** A cancer whose driver is a transcription factor
may depend disproportionately on the general transcriptional machinery — the *transcriptional addiction*
argument (PMID 28187285), made druggable by covalent CDK7 inhibitors (PMID 25043025) and demonstrated in
one defined tumour type (PMID 26406377).

**The driver is a chimera of two domains that never evolved together**, which is a folding problem
before it is a signalling one. ⚠ The step from there to *chimeric proteins are disproportionately
chaperone-dependent* is this programme's working hypothesis and is stated as one: no source retrieved
here establishes it as a general property of fusion proteins, and nothing in this paper rests on it
being true.

⭐ **For both, abundance and dependency disagree — and they disagree in opposite directions.** The
transcriptional half reads as the most concordant elevation anywhere in this programme's expression
census and then closes completely on dependency. The chaperone half reads as an internally contradictory
elevation and then survives, weakly, for a reason the abundance data alone could not have shown.

**The methodological claim is that the second axis is the one that decides, and that reading only the
first would have produced a confident and wrong answer in both cases** — in opposite directions.

---

## 1 · What was measured

Two public series (GSE24369 on GPL6244: 6 EMC vs 29 comparator sarcomas; GSE4303 on GPL3290: 10 vs 6),
read as *z*-scores against each array's own probe distribution and scored as group means of the
EMC-minus-comparator difference, Welch *t*, uncorrected for multiple testing. Where a group is called
*significant* below, that means an uncorrected two-sided *p* < 0.05 at the Welch degrees of freedom the
artifact itself prints beside each *t*; the artifact computes no *p* and applies no correction, and
neither does this paper. Figures are owned by
[`emc-expression-panels.json`](../../modalities/emc-expression-panels.json) and the per-route grading by
[`census-route-expression-grading.json`](../../modalities/census-route-expression-grading.json).
⚠ **Both scored groups are repo-curated pathway-membership lists, not published gene sets or
signatures.** Each panel's own `provenance` field says so in terms — "REPO-CURATED pathway-membership
list. This is NOT a published gene set or signature. Any statement resting on it must say so" — so
every group-level *t* below is a statement about a list this programme assembled, and a differently
drawn list could move it.

The dependency axis is the public sarcoma-line CRISPR panel
([`depmap-sarcoma-dependency.json`](../../modalities/depmap-sarcoma-dependency.json)). ⚠ **Two
different numbers describe that panel and this paper needs both**: the release catalogues **176 sarcoma
models**, but every gene read here carries `n_sarcoma = 91`, so **91 lines are actually screened** and
91 is the denominator under every dependency percentage below. The 176 is a catalogue size, not a
sample size.
⛔ **No line in it supplies a CRISPR observation for this disease.** The single line carrying the EMC
label has no CRISPR gene-effect data at all
([`fet-ddr-axis-scan.json`](../../modalities/fet-ddr-axis-scan.json), `emc_line.has_crispr_gene_effect
= false`), which settles the point on its own; the further curated
record that it does not harbour the fusion is *suggestive and consistent, not definitive* in the
repository's own words, and this paper does not rest on it or treat that line's disease identity as
resolved. So every dependency figure is a **transfer from other sarcomas**, and the honest bound is
not a small sample but no observation in this disease. Class definitions are anchored in
[`txn-dependency-class-definitions-2026-08-09.json`](../../literature/txn-dependency-class-definitions-2026-08-09.json).

## 2 · The transcriptional half — supported on abundance, closed on dependency

**Abundance.** The CDK7 initiation module is higher in EMC on **both** platforms (*t* = 3.69 and 4.11),
and so is the transcriptional output context (*t* = 3.78 and 4.81). The elongation module is higher on
both, significant on one (*t* = 1.19 and 2.26; the second clears the criterion narrowly, at an
uncorrected two-sided *p* = 0.04, and would not survive Bonferroni correction across the fourteen
group readings this paper prints); the processivity kinases show **no clear elevation**
(*t* = −0.88 and −0.69, neither significant — negative, but not a decrease this reading can claim). This is the most
concordant elevation in the whole census, and read alone it looks like support.

**Dependency.** Across the **91 screened** sarcoma cell lines (of the 176 sarcoma models the release
catalogues), **CDK7 and CDK9 are dependencies in 100% of them**, with mean
gene effects of −1.85 and −1.46 and **essentially no sarcoma selectivity** (0.085 and 0.017).

⛔ **A gene required in every line of a tissue class offers nothing to select on.** The elevation is
real and buys no separation between this tumour and any other. The route closes here, and it closes on
the axis that decides rather than on the axis that was measured first.

⚠ **This does not say a transcriptional CDK inhibitor would be inactive in EMC.** It says that if such
an agent acts, it will not be acting on something specific to this disease — which matters for an
ultra-rare cancer whose only realistic path is an argument for *why this disease in particular*.

## 3 · The chaperone half — an internally contradictory elevation

**Abundance, and the contradiction.** The HSP90 machine reads higher in EMC on **both** platforms
(*t* = 3.86 and 3.46), and the co-chaperones likewise in direction (*t* = 1.64 and 2.01, neither
significant by the criterion above). ⛔ **The HSP70 arm and the heat-shock response — which the artifact
scores as one group, not two — show no elevation on either platform** (*t* = −1.06 and −0.96; the
direction is negative on both, but neither reading is significant, so what is reported here is an
absence of elevation and not a decrease this reading can claim).

⚠ **Neither arm is read at full gene coverage, and the split is between two incompletely read groups.**
The HSP90 machine is 4 of 4 genes readable on GPL6244 but only **3 of 4** on GPL3290 (coverage 0.75),
the unreadable member being *HSP90AA1* — and GPL3290 is where its effect size is largest (0.61 SD units
against 0.09). The HSP70 and heat-shock group is **4 of 5** on both platforms (coverage 0.8), but not
the same 4: *HSPA8* has no probe on GPL6244 and *HSF1* none on GPL3290, so the two platforms are not
reading the same list, and the heat-shock transcription factor itself is absent from the platform that
carries the larger HSP90 effect. An unreadable gene is a missing probe, not a gene shown to be
unexpressed. A missing member of either list could move either direction.

That split is the finding. The route's premise is a standing proteostatic load created by an unstable
chimera, and a cell under standing proteostatic load would be expected to raise its stress response.
**The prediction expects elevation; the reading shows none.**

⚠ **And the obvious refutation does not hold either**, which is why this is reported as unresolved
rather than closed: the malignancy-supporting HSF1 programme is *distinct from* the classical heat-shock
response (PMID 22863008). A tumour can run one without the other, so a low heat-shock arm is not by
itself evidence against chaperone dependence. Neither reading survives cleanly.

**Dependency, and an asymmetry the abundance data could not show.** The two HSP90 paralogues are
dependencies in only **5.5%** and **18.7%** of sarcoma lines. The kinase-specific co-chaperone CDC37 is a
dependency in **97.8%**. None of the three shows sarcoma selectivity.

⚠ **The paralogue result must not be read as "HSP90 is dispensable."** Two paralogues that back each
other up will *each* score non-essential in a single-gene knockout screen; that is a property of the
instrument, not of the chaperone, and no public panel answers the dual-knockout question. What the
near-essential co-chaperone does establish is that the machine is load-bearing across this tissue class —
so a route hoping to exploit it needs an argument for why the tumour needs it *more* than a normal cell,
and nothing here supplies one.

## 4 · Why this is one paper and not two

Both halves were derived from the same premise — that the driver's structure predicts its dependencies —
and both were tested with the same two instruments. They produced opposite failures:

| | abundance says | dependency says | outcome |
|---|---|---|---|
| transcriptional CDK | strong, concordant support | pan-essential, no selectivity | **closed** |
| chaperone | internally contradictory | machine load-bearing, paralogues untestable | **unresolved** |

⭐ **Reading only abundance would have given a confident answer in both cases, and been wrong in both** —
promoting the class that closes and burying the one that stays open. That is the transferable result, and
it is not specific to this disease.

## 5 · What would settle each

**For the transcriptional half — nothing computational settles it.** The class is closed on
selectivity, and no expression or dependency reading can reopen it. Only a demonstration that the fusion
creates a *specific* transcriptional vulnerability, rather than a general one, would — and that is a
model experiment.

**For the chaperone half — one measurement, and it is not an expression question.** Is the chimera an
HSP90 **client**? That is a co-immunoprecipitation or degradation-on-inhibition readout in an EMC model.
⚠ Its cheaper precursor was a literature question — whether any FET-family fusion protein is a
documented chaperone client — and that question has been answered as far as one search can answer it:
**no published binding assay retrieved by that search shows any FET-family fusion protein to be a
chaperone client.** ⚠ That is a bounded negative, not a proof of absence: it rests on **fifteen PubMed
queries run on 2026-08-27**, each recorded with its string and its hit count in the file cited below.
No co-immunoprecipitation, pull-down or client-screen result for any *FUS*, *EWSR1* or *TAF15* fusion
appears in what those queries returned. What exists is dependence without binding: EWS::FLI1 protein falls when HSP90 is
inhibited pharmacologically (PMID 24388362, PMID 36495678) and when the HSP90 co-chaperone SGT1 is
knocked down (PMID 25985210) — and for *NR4A3* fusions the chaperone literature is empty, its only
record being *HSPA8* appearing as a fusion **partner** in one case (PMID 28383167), which is a
different fact. ⭐ The comparison that sets the bar is AML1-ETO, shown to bind the chaperonin TRiC
directly through its DNA-binding domain (PMID 26706127): the assay exists and has been run on another
fusion family, so this is a gap in the literature rather than a limit of the instrument. Sources, and
the queries that returned nothing, are in
[`fet-fusion-chaperone-clientship-2026-08-27.json`](../../literature/fet-fusion-chaperone-clientship-2026-08-27.json).

## 6 · Falsifiers

| # | claim | the observation that would kill it |
|---|---|---|
| F1 | the CDK7 module is elevated in EMC | a third EMC series in which it is null or lower |
| F2 | transcriptional CDKs offer no selectivity in this tissue class | a sarcoma-selective dependency for CDK7 or CDK9 in a larger or better-powered panel |
| F3 | the HSP90 machine is elevated in EMC | a third series reversing it |
| F4 | the HSP70 and heat-shock group (scored as one) is not elevated | a third series in which it rises with the HSP90 machine — which would restore the standing-load reading |
| F5 | the chimera's clientship is untested | a published co-immunoprecipitation for any FET-family fusion protein — **the cheapest way this paper is superseded** |
| F6 | the HSP90 paralogues' low dependency reflects redundancy | a dual-knockout showing the machine is genuinely dispensable in sarcoma lines |
| F7 | neither reading is a proliferation artefact | a series matched on proliferation in which both contrasts disappear |

## 7 · Limits

- **Sixteen tumours, two decade-old array platforms, uncorrected for multiple testing**, with different
  comparator arms on each.
- **A transcript is not a protein, an activity or a dependency.** Both halves of this paper turn on that
  gap, and it is why the second axis exists.
- **No EMC cell line carrying the fusion appears in any public dependency dataset**, so every dependency
  figure is a transfer from other sarcomas and inherits that limit wherever it appears.
- **The comparator arm is other sarcoma**, so every abundance statement is relative.
- **Nothing here has been tested in an EMC cell**, and no agent in either class has been given to a
  patient with this disease.

## 8 · Data, evidence and declarations

Every value in this paper is read from artifacts committed in this repository. Nothing was retrieved
for it that is not already deposited here, and no producer was run to write it.

| what it supplies | artifact |
|---|---|
| the scored expression panels, per platform, with their group means, *t*, Welch df and per-gene readability | [`emc-expression-panels.json`](../../modalities/emc-expression-panels.json) |
| the per-route grading, including the census verdict quoted for the transcriptional half | [`census-route-expression-grading.json`](../../modalities/census-route-expression-grading.json) |
| the public sarcoma-line CRISPR panel: mean gene effects, dependent fractions, selectivity, `n_sarcoma` and the catalogued model count | [`depmap-sarcoma-dependency.json`](../../modalities/depmap-sarcoma-dependency.json) |
| the record that the one EMC-labelled DepMap model carries no CRISPR gene-effect data | [`fet-ddr-axis-scan.json`](../../modalities/fet-ddr-axis-scan.json) |
| the class definitions, and the background citations in the summary and section 3 (PMIDs 28187285, 25043025, 26406377, 22863008) | [`txn-dependency-class-definitions-2026-08-09.json`](../../literature/txn-dependency-class-definitions-2026-08-09.json) |
| the chaperone-clientship search, its fifteen dated queries and their hit counts, and every PMID in section 5 | [`fet-fusion-chaperone-clientship-2026-08-27.json`](../../literature/fet-fusion-chaperone-clientship-2026-08-27.json) |

The scored gene groups are repo-curated pathway-membership lists, not published gene sets or
signatures; each panel's own `provenance` field says so, and every group-level statistic here is a
statement about a list this programme assembled. No figure has been rendered for this paper; its
display items are the tables in the running text.

**Author contribution.** T.D.M. is the sole author and is responsible for the design, the analysis,
the interpretation and the manuscript.

**AI assistance.** Analysis and drafting were carried out with Claude (Anthropic) and OpenAI models
under the author's direction, and the author is responsible for the content. No AI tool is an author.
This manuscript has not been peer reviewed by a human reviewer.

**Declarations.** Funding: none. Competing interests: none. Ethics: no ethics approval was sought and
none was obtained for this analysis, and no institution or committee has determined whether any is
required. The analysis reads public archival tumour-expression series and a public cell-line
dependency panel deposited by others; it involved no new recruitment, no new sampling, no clinical
intervention and no patient contact.
