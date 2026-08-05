---
id: DOC-EMC-ATRI-PREREG
title: Pre-registration — ATR-inhibitor sensitivity in extraskeletal myxoid chondrosarcoma
level: L4
kind: prereg
status: immutable
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `prereg` from its location under research/modalities/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# Pre-registration — ATR-inhibitor sensitivity in extraskeletal myxoid chondrosarcoma

> ## ⛔ SCOPE, BEFORE ANYTHING ELSE: THIS IS AN ASK, NOT A PLAN
>
> **This program has no wet lab, no institutional affiliation and no committed collaborator.**
> It is one private individual working in-silico. **Nothing in this document is scheduled, funded,
> resourced or going to happen** on any timeline this program controls.
>
> **What this document IS:** a **publish-to-convince artifact** — a protocol written out in full,
> with its criteria, its controls and its adverse prior all fixed *in advance*, and offered to
> whoever might one day run it. Its value is that **if anyone ever does run it, the result is
> interpretable**, because the bar was set before the numbers existed rather than after. That is a
> real contribution and it is the correct form for it. It is not a claim that we will execute it.
>
> **What this document is NOT:** a next step, a work plan, a commitment, or evidence that anything
> has been or will be tested. **Every readout in §4 and every criterion in §5 requires a bench we
> do not have.** Where the text below says "run", "plate" or "stain", read *"a lab that chose to
> take this up would…"*.
>
> ⚠ **Superseded, retained (2026-08-03):** an earlier framing of this file, and of route 1 in the
> options memo, described the panel as *"the cheapest wet-lab ask"* and read as though the
> experiment were something this program would carry out. It never was. The cost of an experiment
> we cannot run is not "cheap" — it is *unavailable*, and calling it cheap misrepresented the one
> constraint that actually binds. The corrected reading: route 1's ask is **the least demanding of
> the wet-lab-gated routes**, which is a statement about the *other* routes, not about our reach.
>
> **What this program CAN settle by itself** is a different and much narrower question — whether the
> hypothesis is internally consistent in public data and whether it transfers to EMC. That is done,
> it is $0, and it lives in
> [`emc-atr-vulnerability-assessment.md`](../manuscripts/emc-atr-vulnerability-assessment.md) +
> [`emc_atr_vulnerability.py`](./emc_atr_vulnerability.py). **It is not evidence that an ATR
> inhibitor kills EMC cells and cannot become that evidence.**

**Written and committed BEFORE any cell is plated, and before anyone who could plate one has been
approached.** A criterion written after the numbers arrive is not a criterion; that is the whole
reason this document exists and the reason it is dated by its commit rather than by a line of prose.

**Route:** [`emc-post-degrader-options.md`](../manuscripts/emc-post-degrader-options.md) route 1.
That memo is the design rationale and the ranking; it is not re-derived here and nothing here amends
it. **Board row:** [`../IDEAS.md`](../IDEAS.md).

---

## 0 · ⛔ What this is, and what it is not

> **This is a TEST OF A CLASS INHERITANCE. It is not a claim that ATR inhibitors treat EMC.**

No statement about efficacy, safety, a therapeutic window, dosing, or clinical readiness is made or
implied here or anywhere downstream of it. **A PASS licenses exactly one sentence** — *"EMC cells
carrying an NR4A3 fusion were more sensitive to ATR inhibition than a matched non-FET sarcoma
comparator, by a margin that survived a general-chemosensitivity correction and was not matched by
the negative-translation control"* — and **nothing else**. It does not license a dose, a schedule, a
combination, a patient, or a trial.

**This program has no wet lab and no committed collaborator** (scope note above). Everything below is
specified so that a group which *does* could run it without re-deriving anything, and so that
whatever they got back would be interpretable against criteria that were fixed in advance. **Nobody
has agreed to run it and nobody has been asked.**

### 0b · What is executable by whom — so the reader never has to guess

| item | who can do it | status |
|---|---|---|
| The public-data transfer test (is the hypothesis internally consistent; does it transfer to EMC) | **us, in-silico, $0** | ✅ done — [`emc-atr-vulnerability-assessment.md`](../manuscripts/emc-atr-vulnerability-assessment.md) |
| The structural precondition from sequence | **us, in-silico, $0** | ✅ done — [`emc_fet_idr_census.py`](./emc_fet_idr_census.py) |
| The DSB-recruitment arm: exon-verified construct designs, the RGG dose-calibration prediction and the within-EMC TCF12 negative control | **us, in-silico, $0** (the designs; a lab still has to build and image them) | ✅ done — [`emc-atr-collaborator-package.md`](../manuscripts/emc-atr-collaborator-package.md) → [`emc_fet_construct_designs.py`](./emc_fet_construct_designs.py). ⚠ It also **corrects the junction this file's §1 relies on** — the commonest EMC fusion is EWSR1 exon 12, not exon 7; see that file's appendix |
| The GDSC / DepMap re-cuts | **us, in-silico, $0** | ✅ done — [`fet_ddr_axis_scan.py`](./fet_ddr_axis_scan.py) |
| ⛔ Everything in §3–§6 below — cells, dose–response, γH2AX, PARPi arm, proliferation index | **a laboratory. NOT us.** | **HOPE, not plan.** No lab engaged, none approached |
| ⛔ The optional ATM-pS1981 ± IR mechanism readout | **a laboratory. NOT us.** | **HOPE, not plan** |

---

## 1 · The hypothesis, and exactly how much of it is inherited

**Published, in other diseases.** FET fusion oncoproteins are recruited to DNA double-strand breaks
through the retained FET N-terminal intrinsically-disordered region and **suppress ATM activation and
downstream signalling**, leaving the compensatory ATR axis load-bearing; ATR inhibition is therefore
synthetic lethal in FET-rearranged cancers ([PMID 37205599](https://pubmed.ncbi.nlm.nih.gov/37205599/) /
bioRxiv 10.1101/2023.04.30.538578). Reported evidence: elimusertib IC50 **20–60 nM** in FET-driven
lines, and significant anti-tumour responses in **5 of 5** FET-rearranged PDX models spanning an ETS
partner (Ewing), a bZIP partner (clear cell sarcoma, EWSR1::ATF1) and a zinc-finger partner (DSRCT,
EWSR1::WT1), the DSRCT model reaching a partial response by RECIST.

**Inherited by EMC, on two grounds and no more.**

1. **Partner identity.** EMC's 5′ partners are the FET-family genes: **46 (79 %) EWSR1::NR4A3,
   9 (16 %) TAF15::NR4A3, 2 (3 %) TCF12::NR4A3** of 58 EMCs plus 1 (2 %) with no identified partner
   ([PMID 36948401](https://pubmed.ncbi.nlm.nih.gov/36948401/), verbatim), with an independent series
   at 62 % / 27 % / 4 % ([Agaram 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4015728/)) — so
   **≈ 89–95 % of EMC is FET-rearranged**, and ⚠ **the TCF12 minority is predicted NOT to carry the
   lesion**, which is a discriminating prediction rather than a hedge.
2. **Structural precondition, computed by us.** The mechanism needs the fusion to retain the FET
   N-terminus and lose the C-terminal RGG repeats.
   [`emc_fet_idr_census.py`](./emc_fet_idr_census.py) → [`emc-fet-idr-census.json`](./emc-fet-idr-census.json)
   tests exactly that from sequence.

**⛔ What is NOT inherited, stated so nobody has to discover it later.** *No NR4A3 fusion has ever
been tested for DSB recruitment, for ATM suppression, or for ATR-inhibitor sensitivity.* The
mechanism has never been observed in a nuclear-receptor-partnered FET fusion. **That is the gap this
experiment exists to close, and it is the reason a null here is worth as much as a hit.**

---

## 2 · The prior we are arguing against, written down before the result

Two facts already argue for a modest expectation, and both are registered here so a disappointing
result cannot be re-narrated afterwards as unexpected.

- ⚠ **EMC is indolent** — 5-year OS 66–88 %, median time to metastasis ≈ 28 months. ATR-inhibitor
  activity generally tracks proliferation and replication stress. A slowly-cycling tumour offers
  fewer replication forks to catch and a lower baseline γH2AX for the readout to move. **This is why
  a proliferation index is a required readout below, not an optional one** — so a null can be
  attributed rather than merely recorded.
- ⚠ **Our own public-data analysis is equivocal, and it is reported here rather than in a footnote.**
  In GDSC2 8.5, FET-keyed lines are more sensitive to ATR inhibitors after correcting for each line's
  general drug sensitivity (AZD6738 Δ **−0.491**, *t* −5.08; VE-822 Δ **−0.423**, *t* −2.20) — but
  they are more sensitive still to PARP inhibitors (talazoparib Δ **−2.065**; olaparib Δ **−1.016**)
  and about equally to paclitaxel (Δ **−0.525**), while two controls sit at zero as they should
  (adavosertib +0.021, bortezomib +0.087). One home:
  [`fet-ddr-axis-scan.json`](./fet-ddr-axis-scan.json) → `atr_inhibitor_sensitivity_gdsc`.
- ⛔ **And the PARP row has a known clinical answer that goes the wrong way.** *"Both xenograft
  studies and clinical trials in ES patients failed to demonstrate any benefit for PARP inhibitor
  monotherapy"* — from the very paper proposing the ATR route. **A larger in-vitro FET-line DDR
  sensitivity has already failed to translate.** That is the single most important prior here and it
  is what the negative-translation control in §4 exists to detect.

**So the honest expectation registered in advance is: a modest, real, sub-micromolar shift, not a
dramatic one — and a meaningful probability of no shift at all.**

---

## 3 · The panel

| | |
|---|---|
| **EMC arm** | ≥ 2 independent NR4A3-fusion-positive EMC models. Named candidates, all published: **USZ20-EMC1** and **USZ22-EMC2** ([Bangerter et al., *Human Cell* 2023;36:446–455](https://link.springer.com/article/10.1007/s13577-022-00818-x)), **NCC-EMC1-C1** ([Iwata et al., *Human Cell* 2025](https://link.springer.com/article/10.1007/s13577-025-01250-7)), **H-EMC-SS** |
| **Fusion status** | **Required, per model, by RT-PCR or RNA-seq**, and reported. A model whose fusion is not confirmed is not an EMC arm datapoint |
| **Comparator arm** | ≥ 2 **non-FET sarcoma** lines. Non-FET is the load-bearing property — a fusion-driven non-FET line (e.g. synovial, SS18::SSX) is a better comparator than a karyotypically complex one because it controls for "fusion-driven" separately from "FET" |
| **Compound** | any clinical-grade ATR inhibitor available to the lab. ⚠ **They are not interchangeable** — the source reports berzosertib showing no monotherapy activity in Ewing xenografts where elimusertib worked — so **the compound used must be named in any reported result**, and a null with one does not transfer to another |
| **Format** | 7-point dose–response, ≥ 3 biological replicates, 72–96 h |

⚠ **The EMC arm is n ≈ 2–4 models in the world.** This design cannot be well-powered in the usual
sense and does not pretend to be. It is powered to detect a large effect and to *exclude* one; the
criteria in §5 are written accordingly.

---

## 4 · Readouts — three, and each is load-bearing

1. **Viability IC50 / AUC**, ATR inhibitor, EMC arm vs comparator arm. The primary.
2. **γH2AX** by immunofluorescence or western, at a fixed sub-IC50 concentration and time.
   Pre-validated as the informative pharmacodynamic marker in this exact setting: the source found
   p-CHK1 did not discriminate and that *"gH2AX proved to be a reliable biomarker for elimusertib
   activity"*.
3. ⭐ **A PARP-inhibitor arm, as an INTERNAL NEGATIVE-TRANSLATION CONTROL.** This is the design
   contribution of the GDSC analysis in §2 and it costs one extra column on the same plate. **If the
   EMC lines look PARP-inhibitor-sensitive to a similar or greater degree, the assay is reproducing
   the Ewing in-vitro pattern that already failed to translate clinically, and the ATR result must be
   discounted to the same extent.** Reporting an ATR number without this arm is reporting the half of
   the picture that already misled the field once.
4. **A proliferation index** (doubling time or Ki-67) for every line, for the reason in §2.

**Optional, higher-value if the lab can:** ATM autophosphorylation (pS1981) ± ionising radiation, which
would be the first direct test of the *mechanism* — not just its predicted consequence — in any NR4A3
fusion.

---

## 5 · The criteria, fixed now

| tier | condition | what it licenses |
|---|---|---|
| **HIT** | EMC arm IC50 ≥ **3-fold** lower than the comparator arm, in **every** EMC model tested, **and** the PARP-arm differential is smaller than the ATR differential, **and** γH2AX rises in the EMC arm | the one sentence in §0. Next step: an in-vivo model, and the mechanism readout |
| **EQUIVOCAL** | an ATR differential is present but the PARP differential is **equal or larger** | ⛔ **general DDR/chemo-sensitivity, not an ATR result.** Report as such. Does not license the §0 sentence |
| **NULL** | no differential ≥ 3-fold | the class inheritance is not supported in EMC by this readout. **Report it.** Combined with the proliferation index, this is a publishable negative that saves other groups the experiment |
| **UNINTERPRETABLE** | fusion status unconfirmed in an arm, or < 2 EMC models, or γH2AX flat in a comparator known to respond | no reading. Re-run |

**The 3-fold bar is chosen before the data and is deliberately coarse**, because with 2–4 models a
finer threshold would be false precision. **A null is not a failure of this preregistration** — §2
registers a meaningful probability of it, and the route's ranking already accounts for it.

---

## 6 · What would be done with each outcome — also fixed now

⚠ **Read this section as conditional throughout.** Nobody is running the experiment; these are the
interpretations pre-committed to *so that they cannot be chosen after the fact* by whoever does.
The only thing this program itself commits to is writing up whatever comes back honestly.

- **HIT** → write it up with the class argument, the structural census and the GDSC caveat all
  included; propose the in-vivo and mechanism experiments; **do not** propose a trial.
- **EQUIVOCAL** → report as a general-chemosensitivity finding. It would still be the first
  systematic drug-sensitivity characterisation of EMC models against a mechanistic hypothesis.
- **NULL** → publish. A negative that closes a plausible class inheritance for an ultra-rare cancer
  is worth more to the field than the same effort spent on the next hypothesis, and this repo's
  standing rule is that predictable nulls are reported as results, not buried.
- **In every case** → the TCF12::NR4A3 minority prediction (§1) is stated, because it is the part of
  this hypothesis that is falsifiable *within* EMC rather than against another disease.

---

## 7 · Provenance and limits

- Every literature figure above is fetched and quoted from
  [`lit-targets-emc-post-degrader.json`](../manuscripts/lit-targets-emc-post-degrader.json) on the
  `literature-cache` branch. Nothing here is quoted from memory or from a search summary.
- **The structural precondition census is a SEQUENCE argument.** It cannot show that any NR4A3 fusion
  is recruited to double-strand breaks or suppresses ATM. Those are the measurements being asked for.
- **The GDSC comparator is every non-FET line in GDSC2, not other sarcomas**, and its FET group is
  dominated by Ewing. It says nothing about EMC directly — **no EMC line is in GDSC2.** ⭑ The
  matched-comparator version of that contrast is now computed and is in
  [`emc-atr-vulnerability-assessment.md`](../manuscripts/emc-atr-vulnerability-assessment.md).
- **We have not contacted any of the groups named in §3, and there is no plan to.** Doing so is an
  outward-facing act and is gated on trimcrae per CLAUDE.md §3. Until then this file is a document,
  not a project.
- ⚠ **H-EMC-SS is named in §3 as a candidate EMC model and its fusion status is UNVERIFIED.** §3's
  "Fusion status" row already requires per-model confirmation, and that requirement is now doing
  real work rather than being boilerplate — see part A of
  [`emc-atr-vulnerability-assessment.md`](../manuscripts/emc-atr-vulnerability-assessment.md).
