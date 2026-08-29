---
id: DOC-FAP-RLT-REGRADE
title: RT-FAP-RLT — the 2026 evidence, verified live, and what it does and does not change
level: L3
kind: memo
status: live
canonical_for:
  - "the 2026-08-07 live re-verification of the evidence superseding RT-FAP-RLT's 2022 grade"
  - "the RT-FAP-RLT grade from 2026-08-07"
purpose: >
  Re-verify, through CI rather than from memory, the four 2025–26 items said to supersede
  RT-FAP-RLT's `concept` grade; state what the class-level evidence now actually shows; and say
  honestly what FAP evidence exists in EMC specifically as opposed to in sarcoma generally.
scope: >
  L3. One route. It re-grades RT-FAP-RLT and nothing else. It deliberately does NOT promote the
  route's readiness: the class evidence moved and the EMC evidence did not, and those are different
  axes that a single "grade" has been conflating.
audience: [maintainers, autonomous research agents, external reviewers]
related: [DOC-EMC-UNEXPLORED-LANES, DOC-OFCS-VAR2CSA-LANE]
date: 2026-08-07
last_verified: 2026-08-07
---

# RT-FAP-RLT — the 2026 evidence, verified live

> ⛔ **NOTHING HERE ASSERTS EFFICACY, SAFETY, A THERAPEUTIC WINDOW OR CLINICAL READINESS — FOR EMC OR
> FOR ANY SARCOMA.** The first human FAP-radioligand therapy series in sarcoma produced **no objective
> response** and a median overall survival of 4 months; that is reported below because it is the
> evidence, not despite being unhelpful to the route.

## 0 · Why this exists, and how each fact was checked

[`emc-unexplored-treatment-lanes.md` §3.4](../program/emc-unexplored-treatment-lanes.md#34--fap-radioligand--the-2026-increment)
records that `RT-FAP-RLT` is graded off 2022 ⁹⁰Y-FAPI data and that four 2025–26 items supersede it.
That memo labelled all four **[API]** and its own §7 says verification was uneven. This re-checks
every one against a live source, and **two of the four descriptions were wrong in ways that matter.**

**Channel.** The sandbox egress proxy denies `www.ebi.ac.uk`, `clinicaltrials.gov`,
`eutils.ncbi.nlm.nih.gov` and `api.crossref.org` on CONNECT, so literature retrieval ran on a GitHub
Actions runner via `fetch-literature.yml` (`query` path, Europe PMC), published to the
`literature-cache` branch. **Verification levels: [FT]** open-access full text · **[API]** Europe PMC
structured record + abstract · **[search]** web-search index summary and/or sponsor press release —
**below this repository's bar** · **[unverified]**.

---

## 1 · The four items, re-checked

| # | claim in §3.4 | live result | verdict |
|---|---|---|---|
| 1 | `NCT07156565` — [Ac225]-RTX-2358 in relapsed/refractory sarcoma, phase 1/2, RECRUITING, start 2025-11-12, paired diagnostic [Cu64]LNTH-1363S | ATLAS ("Actinium Therapy for Late-stage Aggressive Sarcomas"), sponsor **Ratio Therapeutics**; open-label seamless phase 1/2 in relapsed/refractory **FAP-positive** soft-tissue sarcoma; start **2025-11-12**, recruiting; modified 3+3 escalation, phase 2 expansion up to 50 patients; primary completion est. **Jan 2028**; first cohort dosed **2025-12-16**; the trial's stated goals include the safety of the diagnostic agent **[Cu64]LNTH-1363S** alongside the therapeutic | ✅ **corroborated**, but only **[search]** — see [§4](#4--limits) |
| 2 | `NCT06298916` (PHANTOM) — ⁶⁴Cu-FAPI PET/CT in sarcoma **against FAP IHC**, recruiting | "**64Cu-LNTH-1363S** in Patients With Sarcoma or Gastrointestinal Tract Cancer", phase 1/2a, sponsor **BAMF Health**, recruiting; part 1 metastatic sarcoma, part 2 non-metastatic sarcoma or GI cancer; stated objectives are **safety/tolerability, dosimetry, and an optimal imaging dose and time window** | ⚠ **partly wrong.** The agent is `64Cu-LNTH-1363S`, not a generic "⁶⁴Cu-FAPI" — which matters, because it is **the same molecule as ATLAS's companion diagnostic**, a stronger fact than the memo states. But **"against FAP IHC" is not in the retrieved objectives** and is `[unverified]` |
| 3 | First human FAP-RLT sarcoma therapy readout — ¹⁷⁷Lu-FAPI-2286, n = 6, PMID 42080808; tolerated, 3 of 6 died of progression before follow-up imaging | **PMID 42080808** **[API]** — Jokar N *et al.*, *"FAP-Targeted Theranostics in Advanced Sarcoma: A Pilot Study of ⁶⁸Ga-FAPI-46 Imaging and ¹⁷⁷Lu-FAPI-2286 Therapy"*, DOI `10.1097/rlu.0000000000006507`. Every element **matches verbatim** — and see [§2](#2--what-the-therapy-readout-actually-says) for what the memo left out | ✅ **matches, and materially incomplete** |
| 4 | FAP IHC ↔ PET SUVmax **r = 0.88 in 22 STS patients**, PMID 42128000 | **PMID 42128000** **[API]** — Liu Y *et al.*, *Br J Radiol*, DOI `10.1093/bjr/tqag106`. Verbatim: *"Survival analyses included **22 patients, of whom 10 underwent FAP IHC staining**. A significant association was observed between FAP levels and SUVmax for these STS patients (**r = 0.88, P < 0.001**)."* Tracer is **[⁶⁸Ga]Ga-FAPI-04** | ⛔ **CORRECTION — the denominator is 10, not 22.** 22 is the survival cohort; the correlation rests on the 10 who had IHC |

⚠ *Superseded, retained (CLAUDE.md rule 1.2): "**FAP IHC ↔ PET SUVmax r = 0.88** in **22** STS
patients"; and "`NCT06298916` (PHANTOM) — ⁶⁴Cu-FAPI PET/CT in sarcoma **against FAP IHC**".*

**What item 4 still supports, correctly stated.** In that same cohort of 22, FAPI-avid tumour volume
and total lesion FAP expression were independent predictors of PFS (HR 4.15, P = 0.01) and OS
(HR 4.12, P = 0.02). So the *prognostic* half is on 22; only the *IHC-to-uptake* half is on 10. The
route's actual dependency is the second one — whether a PET scan can stand in for an expression
measurement — and it is the weaker of the two.

---

## 2 · What the therapy readout actually says

This is the single most decision-relevant item on the list and §3.4 quotes only its tolerability.
Verbatim from the retrieved abstract of **PMID 42080808** **[API]**:

- 6 patients, median age 29, histologically confirmed **treatment-refractory metastatic sarcoma**;
  2–4 cycles of ¹⁷⁷Lu-FAPI-2286 at 3.7–7.4 GBq per cycle.
- **No grade ≥3 treatment-related toxicities.** Adverse events limited to grade 2 leukopenia (n = 1),
  grade 1 anaemia (n = 2), grade 1 thrombocytopenia (n = 1).
- **3 of 6 died of disease progression before follow-up imaging could be completed.**
- Of the 3 evaluable: one mixed response, one stable disease, one progressive disease.
  ⛔ **No objective response.**
- **Median overall survival 4 months (95% CI 0–8.8).**
- ⚠ **⁶⁸Ga-FAPI-46 showed no statistically significant difference from ¹⁸F-FDG** on SUVmean, SUVmax,
  MTV/FTV, TLG/TLF or tumour-to-liver ratio; ¹⁸F-FDG showed slightly higher metabolic tumour volumes.

**Two consequences for this route, and neither is favourable.**

1. **The class-level efficacy premise weakened rather than strengthened.** The current grade owner
   ([`emerging-modalities-scan-emc.md` §2](../modality-census/emerging-modalities-scan-emc.md#2-fap-targeted-radioligand-therapy-fapi-rlt--emerging-plausibly-applies))
   rests on ⁹⁰Y-FAPI-46 *"controlled disease in ~half of advanced-sarcoma patients"* (2022). The 2026
   therapy readout is the first prospective FAP-RLT series in sarcoma and it did not reproduce that.
   ⚠ n = 6, heavily pretreated, half unevaluable — this is not a refutation, it is the first real
   data point and it is discouraging.
2. **The "eligibility is directly measurable" premise is now contradicted in its own literature.**
   That same grade-owner section argues FAP-PET makes eligibility directly measurable. In the only
   sarcoma series that compared them, FAP-PET was **not distinguishable from FDG** on any measured
   parameter. A tracer that does not separate from the standard tracer is a weaker selection
   instrument than the grade assumes.

⭐ **What genuinely did improve** is that the route now has a **named, dated, monitorable external
event**: ATLAS is recruiting with FAP positivity as an entry criterion and a primary completion
estimate of January 2028. That converts `timing.two_year_delta` from a hope into a date.

---

## 3 · FAP in EMC specifically — an unreported measurement, not a missing one

The readiness register records `RT-FAP-RLT.readiness.missing = ["any measurement in EMC"]`.
**It survives — but only just, and for a different reason than before.** A published cohort has
stained EMC tissue for FAP; what is missing is the *reported EMC-specific number*, which is an
extraction request rather than an experiment. This section is the evidence for both halves.

**(a) The literature — and the first answer here was too strong.**
A **642-record** Europe PMC corpus for `(FAPI OR "FAP-2286" OR "FAPI-46" OR "fibroblast activation
protein") AND (sarcoma OR chondrosarcoma OR "soft tissue sarcoma") AND (radioligand OR radionuclide
OR radiopharmaceutical OR theranostic OR "177Lu" OR "225Ac" OR "90Y" OR "68Ga" OR "64Cu" OR PET)`
contains **zero titles or abstracts** mentioning extraskeletal myxoid chondrosarcoma, `NR4A3` or
`EWSR1`.

⛔ **THAT ZERO IS A ZERO OVER METADATA, AND READING THE FULL TEXTS BROKE IT.** A proximity scan of
all **483** retrieved full texts — an EMC term within 1,500 characters of a FAP term — returns
**one** paper, and it is not noise:

> **PMID 38964294** / PMC11797935 **[FT]** — Umakoshi M *et al.*, *"Prognostic Value of
> Cancer-Associated Fibroblast Marker Expression in the Intratumoral and Marginal Areas of Soft
> Tissue Sarcoma"*. **133 soft-tissue sarcomas scored by FAP immunohistochemistry**, intratumoral and
> marginal, and the enrolled histological subtypes are listed verbatim as including
> ***"synovial sarcoma, extraskeletal myxoid chondrosarcoma, Ewings sarcoma…"***

⚠ **So EMC tissue HAS been stained for FAP, in a published cohort.** What does **not** exist is an
EMC-*specific* readout: the paper reports pooled and grade-stratified analyses, and its only
subtype-level analyses are of well-differentiated liposarcoma and undifferentiated pleomorphic
sarcoma (*"for which we collected a relatively large number of cases"*, Table 5).

⛔⛔ **AND HALF THE ASK IS ALREADY ANSWERED IN THE PAPER, WHICH SHRINKS THE OTHER HALF TO n = 1.**
Re-read against the PMC full text on 2026-08-29: **Table 1 (*"Details of all enrolled cases"*)
reports the enrolled histology counts, and `Extraskeletal myxoid chondrosarcoma` is **1**.** Of the
133 cases, one is EMC — alongside Ewing sarcoma at 1, fibrosarcoma at 1 and poorly differentiated
leiomyosarcoma at 1, against well-differentiated liposarcoma at 34 and undifferentiated pleomorphic
sarcoma at 28. The count was never missing; it was in a table the earlier proximity scan did not
reach, because that scan matched an EMC term near a FAP term and Table 1 names the subtype without
naming FAP.

⛔ **THE CONSEQUENCE IS UNFAVOURABLE AND IT IS THE POINT OF THIS RE-READ.** The extraction ask
survives — the EMC case's intratumoral and marginal FAP scores are genuinely not reported, and no
per-case data is deposited — but what it would return is **two ordinal scores (0–6 each) on a single
specimen**. That is a case-level observation, not a measurement of FAP in EMC, and it cannot
establish, refute or grade FAP as a target in this disease. **An answered extraction ask would leave
`missing: ["any measurement in EMC"]` standing.**

⚠ **A second limit, stated by the authors, applies to that single case if the scores ever arrive.**
The paper is explicit that in the intratumoral area *"None of the CAF markers was able to completely
distinguish CAFs from sarcoma cells"*, so *"all cells that were positive for any of the three CAF
markers"* — sarcoma cells included — were scored together. **An intratumoral FAP score in this cohort
is therefore not a measurement of the CAF compartment**, which is the compartment a FAP radioligand
targets. Only the marginal score is scored on spindle-shaped CAF-marker-positive cells alone, and the
authors add that anti-FAP staining *"was somewhat weak, making it difficult to evaluate"*.

⚠ *Superseded, retained (CLAUDE.md rule 1.2): "**the number of EMC cases is not stated in the
retrieved text**"; and the framing that the ask is "**a request for an existing measurement, not a
request for a new experiment — which is a materially better position than the route was recorded as
being in**". The first is wrong — Table 1 states it. The second is true as far as it goes and was
read too favourably: an existing measurement at n = 1 is cheaper to obtain and no more able to
settle the question. Retained before that: this section's own first reading, that FAP had never been
measured in EMC tissue at all.*

The same paper is also the honest statement of where the field is: *"**Few studies have examined FAP
in sarcoma**"*, and *"FAP is not a specific marker of certain types of sarcoma"*.

The nearest **radioligand** datapoint in the corpus remains **PMID 35025783**, *"Increased ⁶⁸Ga-FAPI
Activity in Chondrosarcoma of Nasal Cavity"* — a **single case** of **conventional** chondrosarcoma
**[API]**. ⚠ **Conventional chondrosarcoma is not EMC**, and the lane memo's own *ivosidenib/IDH* row
makes exactly this point about nominal name-matching: EMC has no IDH mutation and no true cartilage
differentiation. One FAPI-avid nasal chondrosarcoma is not evidence about a myxoid soft-tissue
sarcoma driven by a FET fusion.

**(b) The repository's own screen — and it is worse than "does not answer the question".**
`RT-FAP-RLT.remaining_unknowns[0]` currently says the surfaceome screen returns
`FAP selectivity_q = 0.1555 / myxoid 0.0` but cannot see a CAF compartment. Both halves are true and
**a third fact is missing**, now measured in
[`surfaceome-instrument-limits.json`](../../modalities/surfaceome-instrument-limits.json) → `L5`:

> The single DepMap line matching the `myxoid` subtype is **`ACH-001519`**, whose EMC identity **this
> repository retracted on 2026-08-05** — Cellosaurus `CVCL_1238` records no `EWSR1` fusion and
> DepMap's filtered fusion caller names no FET gene. The scan's own artifact carries the note
> *"⛔ NOT AN EMC READING"*.

So `myxoid 0.0` is not a low FAP reading in EMC. It is a reading of **one cell line that is not EMC**,
at n = 1, in a compartment that could not contain the antigen anyway. **The scan holds no EMC
observation of FAP for two independent reasons**, and quoting `myxoid 0.0` as though it bore on EMC
would be the "populated field is not a measured one" failure in CLAUDE.md §4.

**(c) The counterweights, unchanged and still real.** EMC is hypovascular, which limits delivery of
anything systemic. And the boron-neutron-capture negative in
[`emc-unexplored-treatment-lanes.md` §6](../program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected)
generalises to this route by the memo's own reasoning: **a radioligand is dosed per unit volume and
delivered per cell**, and EMC is matrix-dominated. Neither is measured in EMC either — they are
arguments, and they are recorded as arguments.

---

## 4 · Limits

- ⛔ **No trial fact here is `[API]`.** ClinicalTrials.gov is denied at the egress proxy (an
  organisation policy denial, which `/root/.ccr/README.md` says to report rather than route around),
  and this repository has **no CI path that can fetch an arbitrary URL**: `fetch-literature.yml`'s
  `targets_file` input takes a **path in the checked-out ref**, so only URLs already committed to a
  branch the runner checks out can be fetched, and this agent is constrained not to push a branch.
  **Items 1 and 2 are therefore `[search]`** — a web-search index summary plus sponsor press
  releases. ⭐ **This caps the verification level of every trial claim in the portfolio, not just
  these two**, and closing it is small: an inline `targets_json` input on that workflow, or an
  NCT-id input to a registry probe script.
- **Neither PMID 42080808 nor 42128000 is open access**, so both are abstract-level `[API]`. Subtype
  breakdown of the 6 treated patients is **not in the abstract** and is `[unverified]` — median age
  29 is suggestive of bone/round-cell sarcomas but that is an inference, not a reading.
- **The ⁹⁰Y-FAPI-46 2022 figure was not re-verified here.** It is the grade owner's, it is not
  contradicted by anything retrieved, and it stays where it is.

---

## 5 · The proposed re-grade

**It is not a promotion, and the honest reason is that two axes moved in opposite directions.**

| axis | before | after | why |
|---|---|---|---|
| class-level clinical evidence | inferred from one 2022 ⁹⁰Y series | **measured in sarcoma, and weak** — first therapy readout has no objective response, median OS 4 months, and FAP-PET did not separate from FDG | §2 |
| EMC-specific evidence | none | **still none REPORTED, and the extraction that would change that is n = 1** — a published 133-case FAP-IHC sarcoma cohort includes EMC, and its Table 1 reports **exactly one** EMC case (measured 2026-08-29); that case's FAP scores are unreported, so the ask is real and what it would return cannot settle the question. The one figure that looked like an EMC reading is a retracted cell line | §3 |
| external monitorable event | none | **ATLAS recruiting, FAP-positivity-selected, primary completion est. Jan 2028** | §1 |
| instrument coverage | screen "does not answer the question" | screen **cannot** answer it — measured, `L1`/`L5` | [`surfaceome-instrument-limits.json`](../../modalities/surfaceome-instrument-limits.json) |

Proposed `grade.value`, replacing *"Emerging, plausible"*:

> **Emerging; class evidence now MEASURED in sarcoma and weak; EMC still entirely unmeasured
> (2026-08-07).**

`readiness.attainable_today` stays `internal_note` and **`missing: ["any measurement in EMC"]`
survives verbatim** — that was the explicit test this re-grade had to pass, and it passes.
⚠ **It passes on the narrower reading, and the wording is now doing real work:** what is missing is a
*reported* EMC measurement. EMC tissue has been FAP-stained inside a published cohort (§3a), so
`evidence_required` gains a **named extraction ask** rather than an experiment — a materially cheaper
thing to be blocked on, and something a future session should not have to rediscover.
⛔ **AND ON THE 2026-08-29 RE-READ THAT ASK IS n = 1, WHICH IS WHY IT DOES NOT PROMOTE THE ROUTE
EITHER.** Table 1 of PMID 38964294 reports one EMC case in 133. An extraction request that succeeds
returns two ordinal scores on one specimen, and the authors' own method note says the intratumoral
score cannot separate CAFs from sarcoma cells. **`missing: ["any measurement in EMC"]` would still
stand after a fully successful ask** — so the ask is worth making and must not be recorded as a path
to closing the gap. §3.
`state.maturity` stays `concept`: nothing about EMC was computed. What changes is that
`supporting_evidence` stops being empty and starts naming what the rationale actually rests on, at
`strength: class_inherited`, which is the field that exists precisely to keep transferred evidence
visible as transferred.

**Routed, verified and deliberately not applied:**
[`fap-rlt-map-edits.json`](./fap-rlt-map-edits.json). Nothing here hand-edits `systems/graph/**`,
`systems/views/**` or the roadmap.
