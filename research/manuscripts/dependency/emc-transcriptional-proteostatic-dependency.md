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
last_verified: 2026-08-27
related: [DOC-MODALITY-CENSUS, DOC-EMC-BIOMARKER-SELECTED]
---

# Transcriptional and proteostatic dependency of a fusion transcription factor

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
defined tumour types (PMID 26406377).

**The driver is a chimera of two domains that never evolved together**, which is a folding problem
before it is a signalling one, and chimeric proteins are disproportionately chaperone-dependent.

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
EMC-minus-comparator difference, Welch *t*, uncorrected for multiple testing. Figures are owned by
[`emc-expression-panels.json`](../../modalities/emc-expression-panels.json) and the per-route grading by
[`census-route-expression-grading.json`](../../modalities/census-route-expression-grading.json).

The dependency axis is the public sarcoma-line CRISPR panel
([`depmap-sarcoma-dependency.json`](../../modalities/depmap-sarcoma-dependency.json)), 176 lines.
⛔ **It contains no EMC line** — the one line carrying this disease's label is recorded as not harbouring
the fusion — so every dependency figure is a **transfer from other sarcomas**, and the honest bound is
not a small sample but no observation in this disease. Class definitions are anchored in
[`txn-dependency-class-definitions-2026-08-09.json`](../../literature/txn-dependency-class-definitions-2026-08-09.json).

## 2 · The transcriptional half — supported on abundance, closed on dependency

**Abundance.** The CDK7 initiation module is higher in EMC on **both** platforms (*t* = 3.69 and 4.11),
and so is the transcriptional output context (*t* = 3.78 and 4.81). The elongation module is higher on
both, significant on one (*t* = 1.19 and 2.26); the processivity kinases are flat. This is the most
concordant elevation in the whole census, and read alone it looks like support.

**Dependency.** Across the 91 screened sarcoma cell lines (of 176 sarcoma models in the release), **CDK7 and CDK9 are dependencies in 100% of them**, with mean
gene effects of −1.85 and −1.46 and **essentially no sarcoma selectivity** (0.085 and 0.017).

⛔ **A gene required in every line of a tissue class offers nothing to select on.** The elevation is
real and buys no separation between this tumour and any other. The route closes here, and it closes on
the axis that decides rather than on the axis that was measured first.

⚠ **This does not say a transcriptional CDK inhibitor would be inactive in EMC.** It says that if such
an agent acts, it will not be acting on something specific to this disease — which matters for an
ultra-rare cancer whose only realistic path is an argument for *why this disease in particular*.

## 3 · The chaperone half — an internally contradictory elevation

**Abundance, and the contradiction.** The HSP90 machine reads higher in EMC on **both** platforms
(*t* = 3.86 and 3.46), and the co-chaperones likewise (*t* = 1.64 and 2.01). ⛔ **But the HSP70 arm and
the heat-shock response go the other way on both** (*t* = −1.06 and −0.96).

That split is the finding. The route's premise is a standing proteostatic load created by an unstable
chimera — and a cell under standing proteostatic load should raise its stress response, not lower it.
**The prediction and the reading disagree.**

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

**For the transcriptional half — nothing computational, and that is the point.** The class is closed on
selectivity, and no expression or dependency reading can reopen it. Only a demonstration that the fusion
creates a *specific* transcriptional vulnerability, rather than a general one, would — and that is a
model experiment.

**For the chaperone half — one measurement, and it is not an expression question.** Is the chimera an
HSP90 **client**? That is a co-immunoprecipitation or degradation-on-inhibition readout in an EMC model.
⚠ Its cheaper precursor was a literature question — whether any FET-family fusion protein is a
documented chaperone client — and that question has now been answered: **no FET-family fusion protein
is one.** No co-immunoprecipitation, pull-down or client-screen result exists for any *FUS*, *EWSR1* or
*TAF15* fusion. What exists is dependence without binding: EWS::FLI1 protein falls when HSP90 is
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
| F4 | the HSP70 and heat-shock arms are not elevated | a third series in which they rise with the HSP90 machine — which would restore the standing-load reading |
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
