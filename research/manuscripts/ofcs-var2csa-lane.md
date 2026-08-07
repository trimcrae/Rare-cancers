---
id: DOC-OFCS-VAR2CSA-LANE
title: Oncofetal chondroitin sulfate (VAR2CSA / Vartumab) — live verification, and the instrument that could not have found it
level: L3
kind: memo
status: live
canonical_for:
  - "the 2026-08-07 live verification of the ofCS/VAR2CSA platform and its chondrosarcoma-enrolling trial"
  - "the measured blind spots of emc_surfaceome_scan (ART-SURFACE-EXPRESSION)"
purpose: >
  Verify, through CI rather than from memory, what the oncofetal-chondroitin-sulfate platform
  actually is and how far it has got clinically; and convert the instrument limit that hid this
  antigen class from a prose footnote into a measured, CI-enforced artifact.
scope: >
  L3. Two things, deliberately separate. (1) The platform and its trial — verified. (2) The limits
  of this repository's surfaceome instrument — measured. It does NOT grade the ofCS route, because
  the expression read that would inform a grade is dispatched by another agent and is not in hand;
  the slot for it is left open and named.
audience: [maintainers, autonomous research agents, external reviewers]
related: [DOC-EMC-UNEXPLORED-LANES, DOC-FAP-RLT-REGRADE]
date: 2026-08-07
last_verified: 2026-08-07
---

# Oncofetal chondroitin sulfate (VAR2CSA / Vartumab) — live verification, and the instrument that could not have found it

> ⛔ **NOTHING HERE ASSERTS EFFICACY, SAFETY, A THERAPEUTIC WINDOW OR CLINICAL READINESS FOR EMC.**
> A peer-reviewed review reports **~85% of soft-tissue sarcomas positive for ofCS**, but it is
> written by the platform's own co-founders, its primary citation could not be resolved, and the
> figure is **not manuscript-ready**; and **no ofCS reading exists in any chondrosarcoma, any myxoid
> tumour, or EMC** — checked in full text, not assumed
> ([§2](#2--what-ofcs-evidence-in-mesenchymal-tumours-actually-exists)). Every clinical
> statement carries a PMID, PMCID, DOI or NCT and a verification level.

## 0 · What was done, and the verification ladder

Two questions, answered by two different instruments on 2026-08-07:

| question | how it was answered | channel |
|---|---|---|
| What is the ofCS platform, and how far has it got? | Europe PMC structured search + open-access full text | GitHub Actions (`fetch-literature.yml`, `query` path) — the sandbox egress proxy 403s `www.ebi.ac.uk`, `clinicaltrials.gov`, `eutils` and `api.crossref.org` on CONNECT |
| What can this repository's surfaceome instrument not see? | a new `$0` checker over the committed script and its artifacts | [`surfaceome_instrument_limits.py`](../modalities/surfaceome_instrument_limits.py) → [`surfaceome-instrument-limits.json`](../modalities/surfaceome-instrument-limits.json) |

**Verification levels**, used throughout and meaning exactly what they say:
**[FT]** open-access full text retrieved and read · **[API]** structured record + abstract read from
Europe PMC · **[search]** a web-search index summary and/or a sponsor press release, **not** a
registry or publisher record · **[unverified]** could not confirm.
⛔ **A `[search]` fact is below this repository's `[API]` bar and must be upgraded before it enters a
manuscript.** Why any fact here is only `[search]` is stated in [§5](#5--limits-and-what-is-still-unverified).

⭐ **AND `[FT]` DOES NOT SIT ON TOP OF THAT LADDER BY ITSELF.** Two things this memo found are `[FT]`
and still not usable: the `~85%` sarcoma-positivity figure is a **secondary citation from the
platform's own co-founders**, and the trial's enrolment number **disagrees between an `[FT]` source
and `[search]` sources**. **Retrieval level and evidential weight are different axes**, and this
memo's biggest errors came from reading one as the other — first by trusting metadata over full
text, then twice more. Every claim below carries both.

---

## 1 · The platform, verified

**The founding result.** Salanti A, Clausen TM, Agerbæk MØ, *et al.* **"Targeting Human Cancer by a
Glycosaminoglycan Binding Malaria Protein."** *Cancer Cell* 2015. **PMID 26461094**, DOI
`10.1016/j.ccell.2015.09.003` **[API]**. Verbatim from the retrieved abstract:

> *"Plasmodium falciparum engineer infected erythrocytes to present the malarial protein, VAR2CSA,
> which binds a distinct type chondroitin sulfate (CS) exclusively expressed in the placenta. Here,
> we show that the same CS modification is present on a high proportion of malignant cells and that
> it can be specifically targeted by recombinant VAR2CSA (rVAR2). **In tumors, placental-like CS
> chains are linked to a limited repertoire of cancer-associated proteoglycans including CD44 and
> CSPG4.**"*

⚠ **A MISATTRIBUTED QUOTE, AND A CORRECTION THAT WAS ITSELF WRONG FIRST TIME.**
[`emc-unexplored-treatment-lanes.md` §3.6](./emc-unexplored-treatment-lanes.md#36--oncofetal-chondroitin-sulfate)
quotes PMID 26461094 as reporting tissue *"of both epithelial and mesenchymal origin"*. That phrase
is **not** in the paper's Europe PMC record, and is in **no title or abstract** in the 1,304-record
ofCS corpus retrieved today.

⛔ **An earlier draft of this section stopped there and labelled the claim `[unverified]`. That was
an over-correction, and the thing that caught it was reading full text rather than metadata.** The
sentence is verbatim, twice, in this platform's own open-access literature:

> *"…oncofetal chondroitin sulfate (ofCS), which is expressed by placental cells and cancer cells of
> **both epithelial and mesenchymal origin**"* — Agerbæk MØ *et al.*, *Nat Commun* 2018, **PMID
> 30115931** / PMC6095877 **[FT]**, citing the 2015 paper.

So the **claim** is well supported at `[FT]`; only its **attribution** to PMID 26461094's own text is
unverified (that paper is not open access). The fix is a citation swap, not a retraction.
*Superseded, retained: this section's own first reading, that the claim was `[unverified]`.*

**Where the platform is now.**

| item | status | verification |
|---|---|---|
| `NCT06645808` — VARTUTRACE, "PET-imaging of Two Vartumabs in Patients With Solid Tumors" | ⭐ **[FT]** for its existence, phase and population: *"Vartumab is currently being tested in a PET/CT phase 0 imaging trial in 16 patients to determine biodistribution in cancers of both epithelial and mesenchymal origin (ClinicalTrials.gov ID: NCT06645808)"* — Skafte A *et al.*, *Cell Death Dis* 2026, PMC12877138. **[search]** for the rest: two ⁸⁹Zr-labelled Vartumab scFv fragments (F8scFv / C9scFv = VTP-01, VTP-02); **started 2024-12-10**; registered conditions **include chondrosarcoma**; sponsor VAR2 Pharmaceuticals with TRACER. ⚠ **The enrolment figure disagrees across sources**: the `[FT]` sentence says **16 patients**; `[search]` sources say **16 per antibody / 32 total**. Unresolved — do not quote either without a registry read | **[FT]** + **[search]** |
| Vartumab ADC (VTP-03) | ⭐ **[FT]** for the chemistry and its preclinical state: two linker-payloads were assessed on the anti-ofCS antibody fragment — **vc-MMAE** and **ggfg-DXd** — with *in vitro* binding, anti-tumour effect and animal biodistribution, and a repeat-dose rat tolerability study for the vc-MMAE ADC; the paper's own conclusion is that a **bystander effect is required** for complete anti-tumour efficacy in those models — **no** claim about EMC and **no** human data (PMC12877138). **[search]** for the programme timing: GMP production from July 2025, sponsor expects a phase 1/2a **in 2027** | **[FT]** + **[search]** |
| rVAR2 as the clinical vehicle | ⚠ the clinical programme is the **Vartumab antibodies**, not rVAR2. rVAR2 remains the reagent in the CTC/EV-capture literature retrieved today (PMID 30115931, 39337304) | **[search]** for the "discontinued" framing; **[API]** for rVAR2's continuing reagent use |
| Preclinical ADC profiling | Skafte A *et al.*, "Preclinical profiling of antibody drug conjugates targeting oncofetal chondroitin sulfate", *Cell Death Dis* 2026, **PMID 41580438** / PMC12877138 | **[FT]** retrieved |
| ofCS bispecific T-cell engager | Skeltved N *et al.*, *J Exp Clin Cancer Res* 2023, **PMID 37118819** / PMC10142489 | **[FT]** retrieved |
| ofCS CAR-T | Khazamipour N *et al.*, *EMBO Mol Med* 2024, **PMID 39406935** / PMC11554890 | **[FT]** retrieved |
| ofCS ADC in AML | Mujollari J *et al.*, *Blood* 2026, **PMID 41405498** | **[API]** |

⚠ **The memo's characterisation of the trial as "chondrosarcoma and osteosarcoma" is only half
corroborated.** The retrieved description names chondrosarcoma among the active indications;
**osteosarcoma was not corroborated** and is left `[unverified]` here.

---

## 2 · What ofCS evidence in mesenchymal tumours actually exists

⛔ **THIS SECTION REPLACES A WRONG ONE OF MY OWN — TWICE OVER — AND THE WAY IT WAS WRONG IS THE
POINT.** An earlier draft ran a title-and-abstract scan over the 1,304-record ofCS corpus, found
three records pairing the platform with "sarcoma / mesenchymal", observed that all three used
"mesenchymal" in the **EMT-phenotype** sense, and concluded: *"the ofCS platform has never been
tested in a sarcoma of any kind."* **That was false, and it was not marginally false.** A proximity
scan of the **880 retrieved full texts** — a platform term within 1,200 characters of a sarcoma
histology — found the platform paired with **osteosarcoma in 8 papers**, `U2OS` in 5, `MG-63` in 3,
and quantitative ofCS-positivity rates across sarcoma as a class.
⚠ **A zero counted over titles and abstracts is not a zero in the literature** — CLAUDE.md §4's
"an absent reading is not a reading of absence", in a new costume. *Superseded, retained: "the ofCS
platform has never been tested in a sarcoma of any kind."*

**What actually exists, and it is more than the lane memo claimed:**

- ⭐ **Sarcoma tissue positivity rates.** Khazamipour N *et al.*, *"Oncofetal Chondroitin Sulfate: A
  Putative Therapeutic Target in Adult and Pediatric Solid Tumors"*, *Cells* 2020;9(4):818,
  **PMC7226838**, DOI `10.3390/cells9040818` **[FT]**, verbatim:
  > *"Sarcomas commonly express ofCS chains in **50%–100% of cases, depending on subtypes**. Overall,
  > **∼80% of bone sarcomas, and ∼85% of soft-tissue sarcomas are positive for ofCS**. Pediatric
  > sarcoma cell lines generally express high levels of ofCS, and ofCS is **required for migration
  > and invasion capacity** of osteosarcoma and rhabdomyosarcoma cells."*

  ⚠ **Two provenance caveats, and the second is the one that matters.**
  **(1)** This is a **review sentence whose primary citation could not be resolved**: Europe PMC's
  full-text-to-plain-text conversion strips reference cross-links and drops the reference list
  entirely (the retrieved file ends at a bare `## References`), so the source appears as `[ ]`. The
  underlying cohort, assay and subtype breakdown are **[unverified]**.
  **(2)** ⛔ **The review is written by the platform's own commercial principals.** Its declared
  interests, verbatim from the retrieved text: *"M.D. and P.H.S. are co-founders of, and shareholders
  in, VAR2 Pharmaceuticals. N.A.N. and M.Ø.M. are consultants for VAR2 Pharmaceuticals."* That does
  not make the figure wrong; it makes an **unresolvable secondary citation from an interested party**
  the weakest possible basis for the lane's strongest number.
  ⛔ **Do not put "~85% of soft-tissue sarcomas" into a manuscript until the primary source is
  retrieved and read.** That is one targeted fetch away and is the single highest-value follow-up in
  this memo.
- **PMID 39406935** / PMC11554890, *EMBO Mol Med* 2024 **[FT]** — **MG-63 osteosarcoma** was one of
  the two primary target lines for ofCS-targeted CAR T cells: *"We used UM-UC-3 muscle-invasive
  bladder cancer and **MG-63 osteosarcoma** cells, respectively, as target cell lines for most of the
  experiments."* Armed VAR2-CAR T cells upregulated CD25/CD69 on contact, expanded clonally and
  killed MG-63 dose-dependently; *"Similar results were obtained with LNCaP (prostate cancer) and
  **U2OS** (osteosarcoma)."*
- **PMID 30115931** / PMC6095877, *Nat Commun* 2018 **[FT]** — rVAR2 bound *"cancer cells of
  epithelial and mesenchymal origin"* across a panel including **U2OS osteosarcoma** and C32
  melanoma.

**What still does not exist, and this is what disciplines the lane:**

A full-text proximity scan of all **880** retrieved full texts, pairing a platform term with each
histology, returns for the following: **nothing at all.**

| histology | papers pairing it with the ofCS platform |
|---|---|
| **chondrosarcoma** (of any kind) | **0** |
| **myxoid** anything | **0** |
| **extraskeletal** anything | **0** |
| **EMC**, `NR4A3` or `EWSR1::NR4A3` | **0** |
| liposarcoma · leiomyosarcoma · synovial sarcoma | **0** each |

*(For contrast, in the same scan: osteosarcoma 8, `U2OS` 5, `MG-63` 3, rhabdomyosarcoma 1.)*

**So the lane's premise remains an inference — a better-supported one than the memo claimed, and
still an inference.** The class-level figure is about *sarcoma*; EMC's own matrix biology is what
makes it interesting, and that is exactly the axis on which nothing has been measured. ofCS is a
**specific sulfation pattern** — *"unusually long and highly 6-O and 4-O sulfated CS chains"*
(PMC12877138 **[FT]**) — and abundant chondroitin sulfate is not the same thing as chondroitin
sulfate carrying that pattern. ⚠ **EMC is a myxoid tumour whose defining feature is its CS-rich
matrix, and it sits in the one histology bucket the ofCS literature has never looked at.** That is
the whole opportunity and the whole risk in one sentence.

⚠ **AND ONE RETRIEVED DETAIL IS A COUNTERWEIGHT SPECIFIC TO EMC.** In cell lines and mouse models —
**not** in EMC and **not** in any patient — the ADC paper concludes that a **bystander effect is
required to drive complete anti-tumour efficacy** (PMC12877138 **[FT]**);
**nothing here claims efficacy of any kind in EMC.** Bystander killing depends on a released payload reaching neighbouring
cells — so it is a **cells-per-unit-volume** argument, and EMC is the tumour in this portfolio with
the least cellularity per volume. That is the **same mechanism** that closed the BNCT row in
[`emc-unexplored-treatment-lanes.md` §6](./emc-unexplored-treatment-lanes.md#6--considered-and-rejected)
and that discounts the FAP radioligand route
([`fap-rlt-2026-regrade.md` §3c](./fap-rlt-2026-regrade.md#3--fap-in-emc-specifically--an-unreported-measurement-not-a-missing-one)).
⛔ **It is unmeasured in EMC and it is not a refutation. It is the thing this lane would have to
survive**, and it should be written into any grade rather than discovered later.

⭐ **A second retrieved detail cuts directly across [§3](#3--the-instrument-that-could-not-have-found-it--now-measured):**
*"ofCS appears both on the malignant cells, in the ECM and on the **cancer associated fibroblasts**,
while being absent on non-tumor associated fibroblasts and healthy adjacent tissue"* (PMC12877138
**[FT]**). The antigen is therefore partly a **stromal and matrix** antigen — precisely the two
compartments the repository's surfaceome instrument does not contain.

⭐ The one thing that would move this without a wet lab is named in [§4](#4--the-open-slot).

---

## 3 · The instrument that could not have found it — now measured

[`emc-unexplored-treatment-lanes.md` §0](./emc-unexplored-treatment-lanes.md#0--what-this-is-and-what-new-was-screened-against)
asserts in prose that `emc_surfaceome_scan.py` cannot see a glycan or a stromal antigen, and that
`CSPG4` is absent from its seed. **Both are correct in direction and both were unfalsifiable.** They
are now a checker with a committed artifact and six tests
([`test_surfaceome_instrument_limits.py`](../modalities/tests/test_surfaceome_instrument_limits.py)),
so the day the gap is closed the build says so instead of every document quietly going stale.

One home for every number: [`surfaceome-instrument-limits.json`](../modalities/surfaceome-instrument-limits.json).

| id | limit | measured verdict |
|---|---|---|
| **L1** | No stromal / CAF compartment exists in the scanned population — the unit of observation is an immortalised tumour cell line in monoculture | CONFIRMED |
| **L2** | An antigen carried **only** by the stroma reads at the floor: `LRRC15`, a sarcoma stromal ADC target, is at `class_frac_expressed 0.00` | CONFIRMED |
| **L3** | Every gene of the CS/GAG **sulfation machinery** is excluded by the instrument's own UniProt filter, so no sulfation-code argument can come from it | CONFIRMED |
| **L4** | `CSPG4` is in neither the seed nor any output — a coverage gap, not a negative | CONFIRMED |
| **L5** | The scan holds **no EMC observation** of `FAP`, for two independent reasons | CONFIRMED |

### 3a · ⚠ The limit is NARROWER than "the scan cannot see stroma", and the narrow version is the true one

Writing the wide version would have been easy and would have been wrong. `CD248` (endosialin) and
`PDGFRB` are routinely called stromal/pericyte antigens and **both come back
`selectivity_significant: true`** in this very artifact. That is not the instrument malfunctioning:
mesenchymal tumour cells genuinely transcribe them, so there is something in the culture to measure.
The limit that survives measurement is therefore:

> **The scan cannot see a gene that ONLY the stroma expresses.** `LRRC15` and `FAP` are that case.
> `CD248` and `PDGFRB` are not.

### 3b · ⭐ The CSPG4 gap is worse than one missing gene

The 2015 founding paper **names two** carrier proteoglycans for the ofCS epitope — **CD44 and
CSPG4** — as the exemplars of *"a limited repertoire of cancer-associated proteoglycans"*. The scan's
curated `SEED_SURFACE` contains **one** of them.

So this is not a scan that happened to miss a gene. Of the two named carriers of the antigen class
the ofCS lane is built on, it scanned one, and the repository then **rejected** the one it scanned —
`CD44` at `enrichment_vs_rest −3.89`, `selectivity_q 1.0` — while the other was never seen.

⚠ **"Names two" is not "there are two", and an earlier draft of this line said the wrong one.**
Agerbæk *et al.* put the repertoire at *"more than 30 different proteoglycans"* (PMC6095877 **[FT]**),
which if anything **weakens** any single-carrier argument in both directions: a proteoglycan's
transcript abundance is a poor proxy for the epitope whether it is high or low. What is measured here
is only the coverage arithmetic — of the two the founding paper names, this seed holds one.
*Superseded, retained: "names **exactly two** carrier proteoglycans".*

⛔ **What this does NOT say.** It does not say CSPG4 is an EMC target, and it does not say a CSPG4
reading would have changed the scan's conclusion. A carrier's transcript abundance does not establish
that its chains carry the 4-O-sulfation. The claim is only that the instrument's coverage of this
antigen class was **half**, and nothing in the record said so.

### 3c · What CSPG4 evidence actually exists, and where it stops

Both figures the lane memo carries at `[snippet]` are **upgraded to `[API]` here**, and one carries a
tension worth recording:

- **PMID 36110930** / PMC9468862 (Nota SPFT *et al.*, *Front Oncol* 2022) — CSPG4 IHC on a
  76-patient tissue microarray: **medium-to-high in 29 of 41 (71%) conventional chondrosarcoma** and
  **3 of 20 (15%) dedifferentiated chondrosarcoma**; CSPG4-CAR T lysed two chondrosarcoma lines at
  >80% and 70% *in vitro*. ⚠ *"CSPG4 expression showed a **positive** association with time to
  metastasis and survival"* — i.e. **higher CSPG4, better outcome** in chondrosarcoma.
- **PMID 36221119** / PMC9552405 (Boudin L *et al.*, *J Transl Med* 2022) — CSPG4 **gene expression**
  in 1,378 localised STS: high vs low 5-year DFS **49% (95% CI 42–57) vs 61% (56–68)**, HR 1.49
  (1.14–1.94), independent in multivariate. High expression associated with undifferentiated
  pleomorphic sarcoma and **myxofibrosarcoma** subtypes, and with an **immune-excluded**
  microenvironment.

⚠ **The two point in opposite prognostic directions** (chondrosarcoma: higher is better; STS: higher
is worse). They are different assays on different diseases — protein IHC on bone chondrosarcoma
versus mRNA on soft-tissue sarcoma — so this is a discrepancy to state, not to resolve here.

⛔ **And neither reaches EMC — checked in full text, after the same check failed elsewhere in this
memo.** A **2,009-record** Europe PMC corpus for `(CSPG4 OR "chondroitin sulfate proteoglycan 4" OR
"melanoma-associated chondroitin sulfate proteoglycan" OR HMW-MAA OR NG2) AND (sarcoma OR
chondrosarcoma OR osteosarcoma OR "soft tissue")` contains zero titles or abstracts naming EMC,
`NR4A3` or `EWSR1` — **and a proximity scan of its 1,383 retrieved full texts returns exactly one
hit, which is a false positive**: PMC13292224 mentions `NR4A3` as a **T-cell exhaustion marker** in
CAR-T transcriptomics, not as a fusion partner. So the zero is a full-text zero.
⚠ **Conventional chondrosarcoma is not EMC** — the lane memo's own *ivosidenib/IDH* row makes exactly
this point about nominal name-matching, and it applies here with equal force.

---

## 4 · The open slot

**This memo does not grade the ofCS route, and the reason is a missing measurement, not caution.**
The lane depends on a **CS/GAG biosynthesis + PAPS module expression read** against the two readable
EMC series (`GSE24369`, `GSE4303`). **That read is being dispatched by another agent
(`emc-expression-datasets.yml`) and is NOT in hand. Nothing here anticipates its result.**

⚠ **What §2 changed, and what it did not.** The class-level finding — sarcomas broadly ofCS-positive
— raises the **prior** that EMC carries the epitope. It does not change what the module read settles,
because the read is about EMC's own sulfation machinery and the class figure is about other
histologies. ⛔ **And it makes the read's downside sharper rather than softer:** if EMC's
sulfotransferase profile is flat while ~85% of soft-tissue sarcomas are ofCS-positive, that is a
specific and interesting negative about EMC rather than a null result. ⚠ *That comparison inherits
the `~85%` figure's provenance problem in §2 and cannot be made in a manuscript until the primary
source is retrieved.*

⚠ **A second bound, from the same full-text pass.** ofCS *"appears both on the malignant cells, in
the ECM and on the cancer associated fibroblasts"* (PMC12877138 **[FT]**). The two readable EMC
series are **bulk tumour-tissue expression arrays** — neither is sorted or single-cell
([`emc-atr-vulnerability.json`](../modalities/emc-atr-vulnerability.json)) — so unlike the DepMap
monoculture behind [§3](#3--the-instrument-that-could-not-have-found-it--now-measured) they do
contain stroma and matrix. That is a point in the module read's favour and the exact inverse of the
surfaceome instrument's `L1`. ⚠ It is also a limitation of the same fact: a positive module read
**cannot say which compartment the signal came from**, and whatever reports it must say so.

**What it would settle, stated before the answer exists** (so it cannot be reshaped afterwards):

⚠ **AND THE DIRECTIONS BELOW WERE WRONG IN AN EARLIER DRAFT, IN THE WORST POSSIBLE WAY.** That draft
treated ofCS as a **4-O** signature and scored the **6-O** transferases (`CHST3`, `CHST7`) as the
*contrary* reading — so a real 6-O signal would have been recorded as evidence **against** the lane.
Full text: ofCS is *"unusually long and highly **6-O and 4-O** sulfated CS chains"* (PMC12877138
**[FT]**). Both arms belong to the pattern. *Superseded, retained: the 4-O-only framing.* ⛔ **This is
why the directions are written down before the data arrives** — had they been written afterwards,
nothing would have caught it.

| reading | what it would mean |
|---|---|
| The **4-O and 6-O sulfotransferase** arms (`CHST11/12/13/14` and `CHST3/CHST7`) are elevated relative to comparators | EMC carries the enzymatic signature ofCS requires. **Still not a measurement of the epitope** — a sulfation-CODE argument, and the honest in-silico proxy for a stain nobody will run. |
| Chain **polymerases and linker** (`CSGALNACT1/2`, `CHSY1/3`, `XYLT1/2`) are high while the sulfotransferases are flat | EMC makes abundant CS and does not modify it into the ofCS pattern — the histology-to-antigen inference in §2 fails on its own terms. A genuine, publishable negative. |
| `PAPSS1/2` or `SLC35B2/B3` low | the sulfate **donor supply** is limiting, which would undercut any sulfotransferase signal read from the transferases alone |
| The whole module flat | the lane reduces to the abundance argument alone, which §2 shows is not the same claim |

⚠ **Several directions are informative, and one of them closes the lane.** The gene panel to read is
cited, not invented: Wu Z-Y *et al.*, *Front Cell Dev Biol* 2021, **PMID 34966741** / PMC8710744
**[FT]** — linker (`XYLT1/2`, `B4GALT7`, `B3GALT6`, `B3GAT3`), polymerases (`CSGALNACT1/2`,
`CHSY1/3`), sulfotransferases and epimerase (`CHST3/7/11/12/13/14/15`, `UST`, `DSE`); the PAPS supply
genes are this repository's addition and are marked as such in the artifact.

⛔ **Even a perfect module read does not measure ofCS.** It measures the machinery, in bulk mRNA, on
n = 6 and n = 10 cohorts. Anyone quoting it must quote that too.

---

## 5 · Limits, and what is still unverified

- ⛔ **ClinicalTrials.gov could not be read live from here, and nothing in this repository can read
  it.** The sandbox egress proxy denies `clinicaltrials.gov` on CONNECT (an organisation policy
  denial, which per `/root/.ccr/README.md` must be reported rather than routed around), and the one
  CI escape hatch that fetches arbitrary URLs — `fetch-literature.yml`'s `targets_file` path — takes
  a **path in the checked-out ref**, so it can only fetch URLs that are already committed on a branch
  the runner can check out. This agent is constrained not to push a branch, so no new URL could be
  added. **No trial fact here rests on a registry read.** ⭐ NCT06645808 partly escapes that ceiling
  by an accident worth generalising: a **peer-reviewed open-access paper describes its own trial**
  (PMC12877138), so its existence, phase and population are `[FT]`. Closing the ceiling properly is
  one small change: a `targets_json` inline input on that workflow, or an NCT-id input to a registry
  probe script — either would make the registry a first-class `[API]` channel for every future sweep.
  It is recorded here because it silently caps the verification level of *every* trial claim in the
  portfolio, not just these.
- **No full text for PMID 26461094.** Not open access. Its *content* is not in doubt — the
  "mesenchymal origin" claim is `[FT]` from PMC6095877 — but the **quotation's attribution to that
  paper's own text** is not confirmable from here (§1).
- **`osteosarcoma` among NCT06645808's registered conditions**, and **chondrosarcoma specifically**,
  are `[search]` only. The `[FT]` source says "cancers of both epithelial and mesenchymal origin"
  without enumerating histologies (§1).
- ⭐ **THE HIGHEST-VALUE UNFINISHED ITEM IN THIS MEMO IS ONE FETCH.** *"~80% of bone sarcomas and
  ~85% of soft-tissue sarcomas are positive for ofCS"* is the strongest class-level statement the
  lane has, and its **primary citation is unresolvable** from the retrieved text because Europe PMC's
  full-text conversion strips reference cross-links. Retrieving PMC7226838's reference list and then
  that primary source would establish the cohort, the assay and — decisively for this lane — whether
  any **subtype breakdown** exists. Until then the figure must not enter a manuscript.
- ⚠ **The §2 corrections are a warning about this memo's own method, and there were two of them.**
  Its first version drew a "measured absence" from a title-and-abstract scan; the second still
  understated what exists. Both fixes came from reading full text. **Every counted zero in this
  document is now a zero over FULL TEXTS** and says so — but every counted zero in
  [`fap-rlt-2026-regrade.md`](./fap-rlt-2026-regrade.md) should be read the same way: as a lower
  bound on what exists, never an upper one.
- **The instrument limits are limits, not a re-scan.** L1, L2 and L5 cannot be closed by re-running
  anything here; they need data with a stromal compartment. L4 can be closed in one line, and §3b
  says so.
- **This memo grades no route.** The ofCS lane has no entry in `systems/graph/routes.json` and this
  memo does not propose one, because §2 and §4 together say the evidence that would justify a grade
  does not exist yet.

---

## 6 · What is proposed, and where

Routed as machine-readable edits, **verified against the live documents and deliberately not
applied** — [`ofcs-cspg4-map-edits.json`](./ofcs-cspg4-map-edits.json). Nothing in this memo
hand-edits `systems/graph/**`, `systems/views/**` or the roadmap.
