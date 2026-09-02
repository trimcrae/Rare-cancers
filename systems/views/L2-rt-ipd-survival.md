---
id: DOC-VIEW-RT-IPD-SURVIVAL
title: RT-IPD-SURVIVAL — Patient-level survival reconstructed from published Kaplan-Meier curves
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Can the time-to-event data this disease's clinical questions all require be recovered from the curves already published?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-IPD-SURVIVAL — Patient-level survival reconstructed from published Kaplan-Meier curves

**Family:** [ST-CARE-DELIVERY](L1-st-care-delivery.md) · **state:** ○ ready · computed · confidence low · verified 2026-08-25

**Grade** (owned by [`systems/graph/routes.json`](../graph/routes.json)): ⭐ THE INSTRUMENT IS BUILT AND ITS KNOWN-ANSWER CONTROL PASSES; ONLY THE CURVES ARE MISSING. research/modalities/emc_ipd_survival.py implements Guyot et al. 2012 and recovers a held-out synthetic cohort EXACTLY — 26 patients, 11 events, 15 censored, identical to truth, survival agreeing within 0.004 except at the tail — and the control is shown to be capable of failing (a three-fold-wrong risk table collapses the recovered cohort to 7). ⛔ THE CONTROL BOUNDS ALGORITHMIC ERROR AND CANNOT FAIL ON A MIS-READ PIXEL: it is fed exact coordinates, whereas a real curve is read off a figure by eye. ⚠ *Superseded, retained: "Digitization error is bounded separately, per curve, by max_abs_km_deviation against the quality floor."* MEASURED 2026-08-25 and it is FALSE: that field compares the reconstruction to the DIGITIZED curve, so a reading error moves both sides together. The same rendered figure read with a calibration wrong by one pixel carries more than twice the true error against a known cohort and a LOWER max_abs_km_deviation than the clean read. Digitization error now has its own instrument and its own bound: research/modalities/km_digitize.py and km-digitization-error.json.  ⛔ FEASIBILITY DOWNGRADED THE SAME DAY IT WAS REGISTERED, BY A COUNT THAT SHOULD HAVE BEEN TAKEN FIRST (2026-08-09). Of 340 EMC full texts in the 554-record open-access corpus, only **19 print a Kaplan-Meier curve at all**, and only 2 also mention numbers-at-risk in text — both of those being conference-abstract collections rather than series. The binding constraint is therefore 19, not the size of the literature, and after §2.3 excludes overlapping populations the poolable set is plausibly single digits covering a few hundred patients. ⚠ THE 2 IS A WEAK PROXY AND MUST NOT BE QUOTED AS THE ANSWER: a numbers-at-risk row is usually rendered INSIDE the figure image, which no text search can see, so it undercounts in exactly the direction that matters. The 19 is NOT a proxy — 'Kaplan-Meier' is named in text whenever a curve is shown — which is why the honest constraint is 19 and the true reconstructable count lies somewhere at or below it. Closed-access series are outside the corpus entirely. ⭐ Superseded, retained: this route was registered on the premise that 'dozens of EMC series print a Kaplan-Meier curve'. Dozens do not. The instrument and its control are unaffected — what falls is the size of the dataset it can build, and with it everything downstream.  ⭐ 2026-08-25 — THE FIGURES WERE LOOKED AT, AND THE ROUTE HAS ITS FIRST RECONSTRUCTED COHORT AND ITS BINDING NEGATIVE IN THE SAME PASS. Article PDFs for all seven candidates with a PMC id were retrieved (five reached, via europepmc.org/articles/<PMCID>?pdf=render), rasterised, and READ. Of the five: masunaga2025 prints three Kaplan-Meier figures and NO numbers-at-risk row; chiusole2020 prints four and NO numbers-at-risk row; martinbroto2020 prints NO Kaplan-Meier curve at all (its Figure 3 is a swimmer plot); stacchiotti2013 and morioka2016 each print one curve WITH a risk row. ⛔ THE TWO LARGEST REACHABLE EMC SERIES (n=171 and n=59) ARE UNRECONSTRUCTABLE FOR A REPORTING REASON, NOT A SCIENTIFIC ONE, and the only two figures that carry a risk row are the two smallest cohorts in the set. ⚠ The 2026-08-09 text-search proxy said 2 of 19 mention numbers-at-risk in text and warned it undercounts; looking at the graphics found the same order of magnitude rather than a hidden reservoir. ✅ stacchiotti2013 Figure 2 has been digitized and reconstructed: 11 patients, 9 events, 2 censored, median PFS 7.98 months against the caption's printed 8 — a quantity the reconstruction never saw, and this program's only check of a READING rather than of arithmetic. ⛔ ONE CURVE IS NOT A POOLED DATASET: n=11, PFS not OS, and the registry flags it as overlapping the Milan series.  ⭐ 2026-08-25, SAME PASS — A SWIMMER PLOT TURNED OUT TO CARRY MORE THAN THE CURVES DID. martinbroto2020's Figure 3 draws one bar per patient (n=49) for the 49-patient phase II analysis population of a nivolumab + sunitinib trial, with an arrow marking a patient still progression-free at last assessment. That is patient-level data with NO Kaplan-Meier inversion and NO numbers-at-risk requirement, so a figure this route would otherwise have refused yields more than either curve it accepted. All 49 bars were read; three independent checks the paper itself supplies all pass — 49 bars against the caption's n=49, a reconstructed Kaplan-Meier median of 5.553 months against the caption's 5.6, and 4 extraskeletal myxoid chondrosarcoma bars against Table 1's 4. ⛔ CLAIM CEILING: four patients, identified by BAR COLOUR, in a subgroup the trial neither pre-specified nor analysed. It supports a statement about what those four patients' bars show and nothing about efficacy or about the disease. ⚠ The source figure is CC BY-NC 4.0 against an Apache-2.0 repository, so the image is NOT committed and the reading is not re-runnable from a bare checkout — the recipe names the URL, page and dpi that reproduce it. ⭐ 2026-08-27 — THE REFUSALS ARE NOW A MEASUREMENT RATHER THAN AN EYE READING, AND THEY SURVIVED IT. Every admissibility verdict this route holds was an agent looking at a page raster and writing `numbers_at_risk_row: false` into a field — unre-runnable, and nothing in the repository could disagree with it. research/modalities/km_risk_row_detect.py measures the band structure beneath a figure's axis instead: a numbers-at-risk row is a band of narrow marks, tick-aligned, immediately below the tick labels. It reads a vector figure through the PDF text layer and a raster figure through its pixels, because EIGHT of this corpus's nine Kaplan-Meier figures are raster images with no text layer -- four of them in an encoding a pure-stdlib reader has to decline outright, read instead from the published page rasters -- and one is vector text — a single-arm detector is wrong for this literature whichever arm it picks. ⛔ THE TWO READINGS AGREE ON ALL NINE FIGURES: masunaga2025's three and chiusole2020's four are `absent`, stacchiotti2013 Figure 2 and morioka2016 Fig. 1 are `present`. ⭐ AND THE DETECTOR IS SHOWN CAPABLE OF THE OTHER ANSWER TWICE OVER — it fires on both real positives, and on morioka2016 it RE-READ the risk row itself (5,5,5,3,3,1,1,1), the same eight numbers a human read two days earlier by a different method. ⚠ Its scope is a figure that this program can decode: chiusole2020's JPEG curves were read from the weaker 200-dpi page raster and are labelled as such, and a figure it cannot decode is recorded `undetermined`, never as a negative. Measurement: km-risk-row-detection.json. Admit-or-refuse per series, largest first: research/literature/emc-km-admissibility-2026-08-27.json. ⛔ 2026-08-27, SAME PASS — THE RETRIEVAL CEILING MOVED BY ONE RUNG AND THE HEADLINE DID NOT. Three untried rungs were added (PMC's own article-PDF endpoint, every Unpaywall OA location rather than the best one, and OpenAlex as a second index) and run against all eleven unretrieved candidates. seer270_2022 (n=270), the LARGEST open-access EMC series, is graded gold open access by both indexes and answers 403 to plain HTTP and to a real headless Chromium at its only PDF location; its second location is a DOAJ landing page with no file. A human with a browser can read that paper and this program cannot, so ITS FIGURES REMAIN UNSEEN — the risk-row question there is unasked, not answered. huang2023 and japan2003 sit behind the same kind of wall. ⭐ What did move: PMC answers /articles/<PMCID>/pdf/ for the two NIH author manuscripts (drilon2008 n=87, bishop2019 n=41) with HTTP 200 and a 1,817-byte 'Preparing to download' interstitial — not a refusal and not a PDF, which is how three rounds recorded them as `unresolved`. Following that redirect is the open rung.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_IPD_SURVIVAL["○ RT-IPD-SURVIVAL"]:::fam
  BLK_NO_CURATED_CLINICAL_DATA{{"BLK-NO-CURATED-CLINICAL-DATA — Three of these six clinica…"}}:::blk
  BLK_NO_CURATED_CLINICAL_DATA --> RT_IPD_SURVIVAL
  TECH_RECONSTRUCTED_IPD(["TECH-RECONSTRUCTED-IPD<br/>expected 2026H2"]):::tech
  TECH_RECONSTRUCTED_IPD -.-> BLK_NO_CURATED_CLINICAL_DATA
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

## Scientific rationale

This repository's evidence contract states its own limit in s2.5 — 'no censoring/Kaplan-Meier; no risk-adjustment or multivariable control' — and s2.4 refuses to merge time-anchored survival. That is a correct account of the method s2.2 mandates, not a limit of the published record: dozens of EMC series print a Kaplan-Meier curve, and Guyot's algorithm inverts one back into the data that generated it. ⭐ The consequence is concrete rather than general: RT-SCHEDULING is closed `definitional` precisely because no pooled progression-free-survival figure may be built under the contract, and reconstruction is the mechanism that makes such a pool legal.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-IPD-SURVIVAL` | the reconstruction recovers a held-out cohort exactly, and the control is demonstrably capable of failing | `direct` |

## Remaining unknowns

- How many published EMC series print a numbers-at-risk table at all — ANSWERED for the reachable candidate set, and MEASURED rather than eyeballed on 2026-08-27: of the nine Kaplan-Meier figures in the five reachable papers, two print a risk row and both belong to the smallest cohorts (km-risk-row-detection.json). It is NOT answered for the series this program cannot fetch — seer270_2022 (n=270), meisKindblom1999 (n=117), drilon2008 (n=87), ussc2022, huang2023, uMich2023, japan2003, china2016, bishop2019 and the two closed Stacchiotti series — which is eleven of sixteen candidates and where the remaining count lives.
- How large digitization error is on real figures — now bounded FROM BELOW by km-digitization-error.json against synthetic renders (worst off-step error 0.0035; worst whole-curve error 0.0636, from a one-pixel calibration slip), and checked per figure against a quantity the paper printed. It is not bounded from ABOVE, and a synthetic render is an easier figure than a journal one.
- Which series overlap in population, since POLICY-evidence.md s2.3 excludes the smaller of any overlapping pair and the SEER analyses certainly overlap each other. UNCHANGED, and it now binds: the one reconstructed curve is from the Milan series, which the registry flags as overlapping chiusole2020 and stacchiotti2014sunitinib.
- ⭐ NEW — whether a SWIMMER PLOT can substitute for a Kaplan-Meier curve. martinbroto2020's Figure 3 draws one bar per patient with censoring shown by an arrow, which IS patient-level data and needs no Guyot recursion; the EMC patients are one colour inside a mixed sarcoma cohort, so the question is whether the subgroup can be separated by colour reliably enough to claim it.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Digitize the curves and numbers-at-risk tables of the open-access EMC series and run them through the built instrument — INSTRUMENT BUILT 2026-08-25 (research/modalities/km_digitize.py) and exercised on the one reachable figure that carries a risk row | ⛔ none built | yes | — |
| Validation against a series whose true patient-level data is published, which would bound digitization error rather than algorithmic error — PARTLY MET by a different construction: the reconstruction reproduces a median the paper printed and the reconstruction never saw. That checks the reading on ONE summary statistic, not on the whole cohort, and a series printing full patient-level data is still the stronger test | ⛔ none built | yes | — |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-CURATED-CLINICAL-DATA** | `insufficient_data` | `TECH-RECONSTRUCTED-IPD` |

## Readiness — what this could become today

**`internal_note`**

⛔ THE CEILING IS 19 CURVES, NOT THE INSTRUMENT. The instrument is validated and its known-answer control passes; what is unknown is whether enough reconstructable curves exist to build a dataset worth publishing. After POLICY-evidence.md §2.3 excludes overlapping populations the poolable set is plausibly single digits. ⚠ Confidence was `moderate` until the count was taken and is now `low` — the grade text carried the downgrade while this field did not, which is the defect CLAUDE.md §4 names: a populated field is not a measured one, and the paper-strength score reads THIS field, not the prose.

**Missing:**
- ⛔ THE CEILING IS WHAT THE FIGURES PRINT, NOT THE INSTRUMENT. Both instruments now exist and both have controls; the reachable literature supplies one admissible EMC curve.
- more curves that can actually be reconstructed — of the five reachable candidates, two print a numbers-at-risk row and one of those is not an EMC cohort, so the reconstructable set reached so far is ONE curve of 11 patients. The binding constraint is what journals print, not what this program can read.

## Where this route ends — the paper

**[PUB-IPD-SURVIVAL](L3-publications.md)** — *A reconstructed patient-level survival dataset for extraskeletal myxoid chondrosarcoma* (unwritten)

`contributing` · ○ `unwritten` · aimed at `preprint`

**This route contributes:** The dataset every other clinical route in this portfolio stops at the absence of.

**The paper would claim:** What the published record of an ultra-rare cancer can and cannot yield as patient-level survival data, measured rather than assumed. Of the extraskeletal myxoid chondrosarcoma series reachable at no cost, the two largest print seven Kaplan-Meier curves between them and NO numbers-at-risk row, so neither can be reconstructed at all; one curve carries a risk row and yields 11 patients, reproducing that paper's own printed median; a trial that prints no Kaplan-Meier curve at all yields four more at patient level from its SWIMMER PLOT, which needs no risk table and no inversion; and two further patients are printed outright in a table and need only transcribing. ⛔ THERE IS NO POOLED TIME-TO-EVENT DATASET AT THE END OF THIS, and the reason is what journals print rather than what an instrument can read. ⚠ *Superseded, retained: "Patient-level survival data for extraskeletal myxoid chondrosarcoma, reconstructed from every published Kaplan-Meier curve that prints a numbers-at-risk table — the first pooled time-to-event dataset in this disease, and the input its unanswerable clinical questions were waiting on."* That claim was written before anybody looked at the figures. The figures were looked at on 2026-08-25 and the promised pool is not there to be built.

**It is not written because:** The paper is unwritten; the science for it now exists. ⚠ *Superseded, retained: "no published figure has been digitized into it yet."* One has — stacchiotti2013 Figure 2, 11 patients, 9 events, median 7.98 months against the caption's printed 8, a number the reconstruction never saw. What changed is the paper's FINDING rather than its readiness: it is now largely a negative about the reporting practice of a literature, with a method and a small dataset attached. ⛔ CURVES stays empty and a test still enforces it; coordinates reach the program only through a digitizer artifact naming the committed image it read.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

Every input is either committed or free to curate, and the work is $0.

| horizon | effect |
|---|---|
| Cost trend | flat |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-CARE-DELIVERY](L1-st-care-delivery.md), which is where these are asserted — a family limitation binds every route inside it.*

- Nothing in this family produces a new agent, so its ceiling is bounded by what the existing arsenal can do — and its floor is that the arsenal is already being used, so the gain is variance-reduction rather than a new option.
- Every route here ends in an observational or modelled argument. No randomised trial will ever settle a surgical-margin or surveillance-interval question in a disease this rare, so the limits of the design must travel with every claim.
- Reconstructed and registry data are re-expressions of published records, never new patients — they inherit every selection and publication bias of the series they came from and can correct none of it.
- Treatment associations in observational sarcoma data are dominated by confounding by indication, which runs in the direction that makes therapy look harmful; a route here that reports an unadjusted hazard has produced an artefact, not a result.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness.

## Best next action

Digitize the Kaplan-Meier curve and numbers-at-risk table of the largest open-access EMC series and admit or refuse it against the quality floor.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 artifacts:** [ART-IPD-SURVIVAL](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against)

[← ST-CARE-DELIVERY](L1-st-care-delivery.md) · [← L0](L0-ecosystem.md)
