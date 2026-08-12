---
id: DOC-EMC-SGK1-LANE
title: SGK1 in EMC — verifying the 2006 source, its internal control, and the twenty-year silence
level: L3
kind: memo
status: live
canonical_for: ["the SGK1/EMC lane's primary evidence, its internal control, and its 2026-08-07 grade"]
purpose: >
  Retrieve and verify the 2006 primary source for SGK1 overexpression in EMC, establish what the
  "internal negative control" actually was rather than repeating the claim, check SGK1 against every
  expression and dependency artifact this repository already holds, and measure whether any
  follow-up exists since 2006.
scope: >
  L3. Covers lane 3.10 of emc-unexplored-treatment-lanes.md only. Asserts nothing about efficacy,
  safety or a therapeutic window. It does NOT dispatch an expression read — the exact request it
  would make is stated in section 4 and left for the agent already holding that slot. Graph changes
  are proposed in a routed map-edits JSON, not applied here.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-08-07
last_verified: 2026-08-07
---

# SGK1 in EMC — verifying the 2006 source, its internal control, and the twenty-year silence

> ⛔ **NOTHING HERE ASSERTS EFFICACY, SAFETY, A THERAPEUTIC WINDOW OR CLINICAL READINESS FOR EMC.**
> The human evidence below is ten tumours stained by immunohistochemistry in 2006. The causal
> evidence is a rat cell line. No SGK1 inhibitor has been reported in any clinical trial.

**One-line result.** The memo's headline claim survives verification **including the detail it
rested on** — the internal negative control is real and is stated by the primary source itself. The
silence is real and now measured: **10 forward citations in twenty years, not one of them an SGK1
follow-up in EMC.** Two things the memo did not have: no SGK1 inhibitor has reached the clinic, and
the same group's 2012 human-model repeat of the target-gene screen is an unresolved, retrievable
question that could quietly close the lane.

---

## 1 · The primary source

**Poulin H, Filion C, Ladanyi M, Labelle Y. "Serum- and glucocorticoid-regulated kinase 1 (SGK1)
induction by the EWS/NOR1(NR4A3) fusion protein." 2006. PMID 16756948,
DOI 10.1016/j.bbrc.2006.05.134 — cited by 10.**

⚠ **Verification level: [API] — Europe PMC structured record + abstract, retrieved 2026-08-07.**
`isOpenAccess: false`, **no PMCID**. Europe PMC serves no full-text XML, so the Methods section is
not reachable at $0.

The abstract, on the two arms that matter, verbatim:

> *"To identify genes regulated by the fusion protein in this model, we have generated a **CFK2 cell
> line in which the expression of EWS/NOR1 is controlled by tetracycline**. Using the differential
> display technique, we have identified the serum- and glucocorticoid-regulated kinase 1 (SGK1)
> mRNA as being up-regulated in the presence of EWS/NOR1. Co-immunocytochemistry confirmed
> over-expression of the SGK1 protein in cells expressing EWS/NOR1. Significantly,
> **immunohistochemistry of 10 EMC tumors positive for EWS/NOR1 showed that all of them over-express
> the SGK1 protein in contrast to non-neoplastic cells in the same biopsies and various other
> sarcoma types.** These results strongly suggest that SGK1 may be a genuine in vivo target of
> EWS/NOR1 in EMC."*

And, from the same abstract, what CFK2 is: *"constitutive expression of EWS/NOR1 in **CFK2 fetal rat
chondrogenic cells** induces their transformation as measured by growth beyond confluency and growth
in soft agar."*

---

## 2 · What the internal negative control actually is

**This is the detail the memo's whole case rests on, so it is stated here from the source rather
than repeated.**

✅ **The internal control is REAL and it is what the memo said it was:** *"non-neoplastic cells **in
the same biopsies**"*. That is a within-section comparison, so it is not vulnerable to the failure
mode that sinks most small IHC series — batch effects, fixation differences, antibody lot, or a
comparator cohort processed elsewhere. There is additionally an **external** comparator: *"and
various other sarcoma types"*.

⛔ **And here is exactly how far that gets us, because "internal control" is doing a lot of work.**
The abstract states that the comparison was made. It says **nothing** about the things an IHC result
is normally graded on, and none of them is retrievable at $0 because the paper is paywalled and has
no PMC record:

| what a reader needs to grade this IHC | retrievable? |
|---|---|
| antibody clone, vendor, dilution | ❌ Methods paywalled |
| scoring system and positivity threshold | ❌ Methods paywalled |
| whether scoring was blinded, and by how many readers | ❌ Methods paywalled |
| which non-neoplastic cells (stroma? endothelium? entrapped normal tissue?) and how abundant | ❌ Methods paywalled |
| how many "other sarcoma types", and n per type | ❌ Methods paywalled |
| whether the 10 tumours were consecutive or selected | ❌ Methods paywalled |

⭐ **The honest statement is therefore narrower than "10/10 with an internal negative control" and
still favourable:** *the primary source reports SGK1 protein overexpression in 10 of 10 fusion-positive
EMC tumours by IHC, scored against non-neoplastic cells within the same biopsy sections and against
other sarcoma types; the staining protocol, scoring criteria and reader blinding are not
establishable from the open record.* That sentence is quotable in a manuscript. The shorter one is
not, and the difference is exactly the difference the task asked to check.

⚠ **A second limit, structural rather than methodological.** The human arm is **correlative**. The
only causal link from the fusion to SGK1 is the tet-regulated **rat** CFK2 line, by differential
display. Nothing in the paper shows that SGK1 is *required* by an EMC cell — no knockdown, no
inhibitor, no rescue. The memo says this and it is correct.

---

## 3 · The twenty-year silence, measured

Europe PMC forward-citation retrieval, `CITES:16756948_MED OR (SRC:MED AND EXT_ID:16756948)`,
2026-08-07. **10 citing records in twenty years.** All ten, in full — the list *is* the finding:

| year | PMID | what it is | does it follow up SGK1 in EMC? |
|---|---|---|---|
| 2007 | 17569022 | *"SGK1 survival through various lives may save us all"* — SGK1 review | no |
| 2008 | 18461179 | atrazine / NR5A nuclear receptors | no |
| 2008 | 18951519 | EMC retrospective clinical review, 2 referral centres | no — clinical outcomes |
| 2009 | 18855877 | **Filion C, … Ladanyi M, Labelle Y** — *"The EWSR1/NR4A3 fusion protein … activates the PPARG nuclear receptor gene"*, DOI 10.1002/path.2445 | ⚠ **same group, different gene.** They moved to PPARG |
| 2009 | 19584721 | SGK1 physiology review | no |
| 2009 | 19682370 | NR4A3 locus polymorphisms / beta-cell | no |
| 2009 | 19764891 | *"Targeting SGK1 in diabetes"* | no |
| 2012 | 22592656 | **Filion C, Labelle Y** — *"Identification of genes regulated by the EWS/NR4A3 fusion protein in extraskeletal myxoid chondrosarcoma"*, DOI 10.1007/s13277-012-0415-2 | ⚠ **the one that matters — see below** |
| 2018 | 29327709 | INSM1 IHC in 31 NR4A3-rearranged EMC | no |
| 2020 | 32967265 | Stacchiotti S, … Maestro R, EMC state of the art, PMC7563993 | no — one sentence, quoted below |

### 3a · The lane was not closed by later work. It was never picked up.

The most recent comprehensive EMC review — Stacchiotti *et al.* 2020, **PMID 32967265, PMC7563993**,
DOI 10.3390/cancers12092703 — cites the 2006 paper exactly once, in its list of candidate targets.
Verbatim from the open-access full text:

> *"Wingless-related integration site (WNT) and MYC pathways may represent additional therapeutic
> targets, as key molecules of these signaling pathways have been described to be over-expressed in
> EMC compared to other sarcomas. **The same holds true for peroxisome proliferator-activated
> receptor gamma (PPARG) and Serum/Glucocorticoid Regulated Kinase 1 (SGK1), which have been
> demonstrated to be transcriptional targets of the oncogenic fusion protein.**"*

⭐ **That is the cleanest possible answer to the question the task asked.** The field's own state-of-the-art
review, fourteen years later, still lists SGK1 as an established fusion target and still has nothing
to add. **No paper refutes it. No paper advances it.** This is unworked ground, not abandoned
ground — which is a materially different and better state than the memo could establish.

### 3b · ⚠ The one open thread, and it is retrievable

**PMID 22592656 — Filion C & Labelle Y, 2012, DOI 10.1007/s13277-012-0415-2** — is the *same group*
repeating the target-gene identification after replacing the rat CFK2 system with a human one:

> *"We have generated an **in vitro human cellular model** in which the fusion protein is expressed in
> mesenchymal bone marrow stem cells. We have performed microarray analyses of these cells and
> identified several genes overexpressed in the presence of EWS/NR4A3 which are also overexpressed in
> EMC tumors."*

**The abstract names no gene.** So the single most informative fact about this lane — *did SGK1
reappear when the same group moved from a rat line to a human line?* — sits in a paywalled gene list.

- If SGK1 is in it: the 2006 result is independently reproduced in a human system, and the lane's
  grade rises sharply.
- If SGK1 is absent from it: the group's own follow-up did not recover its own earlier hit, and the
  lane is much weaker than the memo's ranking assumes.

⛔ **Neither outcome is knowable at $0.** `isOpenAccess: false`, no PMCID. This is the lane's
sharpest blocker and it is a **paywall**, not a capability and not a compute cost. It is the kind of
thing a single institutional library login settles in five minutes, which is why it is recorded here
as an ask rather than buried.

---

## 4 · SGK1 against everything this repository already holds

### 4a · Expression artifacts — a measured absence of *reading*, not of expression

`SGK1` was searched for in every expression-bearing artifact the repository holds. **Zero occurrences
in all six:**

| artifact | `"SGK1"` occurrences |
|---|---|
| [`emc-atr-vulnerability.json`](../../modalities/emc-atr-vulnerability.json) — the characterisation of `GSE24369` and `GSE4303` | 0 |
| [`atr-hrd-sarcoma-series.json`](../../modalities/atr-hrd-sarcoma-series.json) | 0 |
| [`atr-hrd-sarcoma-series-quant-inputs.json`](../../modalities/atr-hrd-sarcoma-series-quant-inputs.json) | 0 |
| [`emc-gse4303-crosscheck.json`](../../modalities/emc-gse4303-crosscheck.json) | 0 |
| [`depmap-sarcoma-dependency.json`](../../modalities/depmap-sarcoma-dependency.json) | 0 |
| [`depmap-target-expression.json`](../../modalities/depmap-target-expression.json) | 0 |

⚠ **AN ABSENT READING IS NOT A READING OF ABSENCE.** Every one of those artifacts scores a **curated
gene panel**, and SGK1 has never been in one. The DepMap files score ncBAF/BET/surface/CTA panels;
`fet-ddr-axis-scan` scores a DDR panel; `emc-gse4303-crosscheck` scores a ten-gene surfaceome
shortlist and reports `n_probes_mapped: 0` on the platform it read. **None of these is evidence that
SGK1 is not expressed in EMC.** They are evidence that nobody has asked.

⭐ **Widened to the whole corpus, and the negative holds — with one instructive near-miss.** All
**340** JSON artifacts under `research/modalities/` were scanned for `SGK1`, `SGK2`, `SGK3` and
`PRKDC`. `SGK1` appears in **exactly one family of files** — the drug-repurposing candidate set and
its shards — and there only as an annotated **drug-target string**, never as an expression or
dependency measurement.
⭐ **And the check was extended off this branch, because CLAUDE.md §7 says an artifact's real home
may not be here.** `origin/modalities-cache` — where `depmap-dependency.yml` publishes — carries the
same two DepMap files and **neither contains `SGK1`** (`git show origin/modalities-cache:…` returns
0 occurrences in both). So this is not a branch-drift artefact: **the repository holds no SGK1
reading of any kind, on any branch.**

⛔ **But the same scan found that the sibling lane's gene WAS readable and nobody had read it.**
[`emc-atr-vulnerability-inputs.json`](../../modalities/emc-atr-vulnerability-inputs.json) →
`/part_b/platforms/<platform>/geneset_gene_values` holds **per-sample values for a 1,299-gene panel**
across every EMC-bearing GEO series this repository has characterised, sample titles included. That
panel contains `PRKDC` and it does **not** contain `SGK1`. So on 2026-08-07 one of these two lanes
could be answered from disk and the other could not — and until the scan was run, both were about to
be recorded identically as "needs a GEO dispatch". The reading that came out of it lives in
[`emc-kinase-lane-panel-read.json`](../../modalities/emc-kinase-lane-panel-read.json) and is discussed
in [the DNA-PK assessment](emc-dnapk-nr4a3-lane-assessment.md).
⚠ **`SGK1: measured: false` in that artifact is a fact about a DDR panel's gene list, not about
SGK1.** It is printed with that warning attached for exactly this reason.

✅ **And the scan verified one thing §4c depends on:** on `GSE4303`, the EMC samples live on
**`GPL3290` (10 EMC vs 6 comparators)**, while `GPL2937` — the platform
[`emc-gse4303-crosscheck.json`](../../modalities/emc-gse4303-crosscheck.json) actually read — carries
**zero** EMC samples. The platform warning below is therefore measured, not cautionary.

### 4b · DepMap cannot settle this lane even if asked

The only DepMap model labelled EMC is `ACH-001519` / **H-EMC-SS**, and
[`emc-atr-vulnerability.json`](../../modalities/emc-atr-vulnerability.json) records its identity verdict as
`NOT_FUSION_POSITIVE_PER_CURATED_RECORD`, quoting Cellosaurus verbatim: *"Caution: Does not harbor a
gene fusion involving EWSR1 which is a hallmark of extraskeletal myxoid chondrosarcoma
(PubMed=34413129)."* The same artifact records that DepMap's own filtered fusion caller has the model
in the file with two calls, **neither naming NR4A3 or any FET gene**, and that the line has no CRISPR
data. So a DepMap `SGK1` dependency read would be a read on 91 sarcoma lines, **none of them EMC** —
the same bound already recorded for `RT-SYNLETH-DEP` in [`routes.json`](../../../systems/graph/routes.json).

### 4c · The expression read this lane needs — stated, not dispatched

⚠ **Deliberately not dispatched.** Another agent holds the `emc-expression-datasets.yml` slot for a
different gene panel on 2026-08-07 and a competing run would collide. The exact request, so whoever
runs next can add it in one line:

> **Gene: `SGK1`** (aliases `SGK`, `SGK-1`).
> **Series 1: `GSE24369` / `GPL6244`** — **42 samples: 6 EMC vs 36 comparators** (17 low-grade
> fibromyxoid sarcoma, 6 desmoid fibromatosis, 6 myxofibrosarcoma, 5 solitary fibrous tumour, 2
> pooled skeletal-muscle RNA), single-channel intensity. Gene 1.0 ST gene-level, so the request is
> the `SGK1` gene-level summary and its rank among the comparator sarcomas. This is the series that
> can answer *"high in EMC relative to other sarcomas"*, which is the 2006 IHC claim's external arm.
> **Series 2: `GSE4303` / `GPL3290`** — **16 samples: 10 EMC vs 6 comparators**, two-colour
> log-ratio, so any percentile is **relative to the array's reference pool**, not absolute
> expression, exactly as [`emc-gse4303-crosscheck.json`](../../modalities/emc-gse4303-crosscheck.json)
> records for its own read. ⚠ **The platform must be named or the read lands on a matrix with no EMC
> in it**: that crosscheck used `GPL2937`, which carries **zero** EMC samples.
> ⛔ **Two figures in the source memo's §4 do not survive checking and are corrected here rather than
> carried forward** — its "6 EMC vs **29** comparators" belongs to a different series (`GSE80126`,
> 29 samples), and its "93.2 % / 58.2 % **probe mapping**" are `accession_resolution_rate`, not probe
> mapping: on `GSE24369` only **20,324 of 28,459 probes (71.4 %)** carry a symbol. Both read from
> [`emc-atr-vulnerability-inputs.json`](../../modalities/emc-atr-vulnerability-inputs.json) →
> `/part_b/platforms/`; routed as edit `K5` in
> [`kinase-lanes-map-edits.json`](kinase-lanes-map-edits.json).
> **Comparator gene to request in the same call: `PPARG`** — the *other* gene the 2020 review lists
> from the same group's work, so a positive `SGK1` reading can be graded against a claim of the same
> provenance rather than against nothing.
> **What it settles:** whether the correlative human arm of the 2006 paper reproduces in an
> independent, orthogonal-platform EMC cohort. It cannot settle dependency.

---

## 5 · Druggability, graded honestly

✅ **SGK1 is structurally druggable, and the repository owns a stack that could act on it.**
Zhao B *et al.*, 2007, **PMID 17965184**, DOI 10.1110/ps.073161707 — a **1.9 Å crystal structure of
the human SGK1 catalytic domain in complex with AMP-PNP**. Verbatim from its abstract:

> *"Although most of the SGK1 structure closely resembles the common protein kinase fold, **the
> structure around the active site is unique when compared to most protein kinases**. The alphaC
> helix is not present in this inactive form of SGK1 crystal structure … Since the differences from
> other kinases occur around the ATP binding site, this structure can provide valuable insight into
> the design of selective and highly potent ATP-competitive inhibitors of SGK1 kinase."*

⚠ Two cautions that belong beside that, not after it: the deposited structure is of the **inactive**
form, and SGK1's nearest neighbours are SGK2/SGK3 and the AKT family — so an AGC-kinase selectivity
problem is imported, which is the same *class* of problem the degrader program hit in the NR4A
family. It is not the same problem, and it is far better precedented, but it is not free.

⛔ **NO SGK1 INHIBITOR HAS BEEN REPORTED IN A CLINICAL TRIAL — measured, not assumed.** Across a
**1,248-record** Europe PMC corpus retrieved 2026-08-07 for
`SGK1 AND (GSK650394 OR "EMD638683" OR "SI113" OR "SGK1 inhibitor" OR "crystal structure" OR "kinase
domain")`, **zero records** pair SGK1 with a phase-1/2/3 designation, "first-in-human", or an
`NCT` identifier in title or abstract. The chemical matter is entirely preclinical: `GSK650394`,
`EMD638683` (PMID 21865856), the `SI113` series (PMID 25871776 and a decade of follow-ups), and
ongoing optimisation through 2026. The repository's own Broad Drug Repurposing Hub extract
[`nr4a3-repurpose-candidates.json`](../../modalities/nr4a3-repurpose-candidates.json) agrees: `GSK650394`
carries `phase: "Preclinical"`, `target: "SGK1|SGK2"`.

⚠ **So the memo's phrase "druggable AGC kinase" is accurate and must not be read as "clinical-stage".**
The distinction matters for route grading: a route that would need a first-in-human programme is a
different proposition from one that can be tested with an approved agent.

**One transfer datum, and it is transferred, not EMC.** SGK1 has been functionally tested in exactly
one other sarcoma: **PMID 28992614**, DOI 10.1159/000481842 — *"Administration of EMD638683 — an
inhibitor specific for SGK1 — decreased viability of RD and RH30 [rhabdomyosarcoma] cells, enhanced
the effects of the cytotoxic drug doxorubicin leading to reduced migration and decreased cell
proliferation."* Different sarcoma, different driver, no fusion relationship to NR4A3. It shows the
target class is tractable in a sarcoma cell; it says nothing about EMC.

---

## 6 · Verdict

**SURVIVES, AND ITS CENTRAL CLAIM VERIFIES — INCLUDING THE DETAIL THE CASE RESTED ON.**

| the memo's claim | verified? |
|---|---|
| 10/10 EMC tumours positive by IHC | ✅ stated verbatim by the primary source |
| with an internal negative control | ✅ *"non-neoplastic cells in the same biopsies"* — real, and additionally an external sarcoma comparator. ⚠ the staining protocol, scoring criteria and blinding are **not** establishable from the open record |
| a druggable AGC kinase | ✅ 1.9 Å catalytic-domain structure, multiple tool compounds. ⛔ **but entirely preclinical — no clinical trial of any SGK1 inhibitor exists in the retrieved record** |
| published 2006 and never followed up | ✅ **measured: 10 citations in 20 years, none an SGK1 follow-up in EMC**; the 2020 field review still lists it as a fusion target with nothing added |
| the fusion→SGK1 link is from a rat line | ✅ CFK2 fetal rat chondrogenic cells, tet-regulated, differential display |

**What the memo did not have, and what changes:**

1. ⭐ **The silence has a shape.** The original group did not abandon EMC — they published on **PPARG**
   in 2009 and repeated the whole screen in a **human** model in 2012. They walked past SGK1 twice.
   Whether that is because SGK1 did not reproduce, or because PPARG was simply more interesting, is
   the single highest-information question about this lane and it is **one paywalled gene list away**.
2. ⛔ **No clinical-stage inhibitor.** This does not close the lane, but it moves it out of the
   "existing drug, new indication" class the memo's framing implies and into "target validation for a
   preclinical chemical series".
3. ✅ **The generalised principle in the memo holds and is worth keeping** — a druggable enzyme the
   fusion installs, absent from the normal counterpart tissue, is the right shape of target for an
   undruggable-TF disease, and 10/10 with a within-section control is unusually clean for EMC. That
   argument is unaffected by everything above.

**Grade: keep the lane, and rank it on what it can actually reach.** Its next two steps are both
literature/data, both cheap, and neither is compute:

1. the 2012 gene list (**paywalled — an ask, not a run**);
2. the `SGK1` expression read in `GSE24369`/`GSE4303`, specified in §4c and **left for the agent
   holding that slot**.

Only after those does any structure-based work on **PDB 2R5T** become a sensible use of the
repository's docking and free-energy stack — and even then it would be building chemistry against a
target whose EMC dependency has never been tested in a single cell.

**Proposed registration** (routed, not applied):
[`kinase-lanes-map-edits.json`](kinase-lanes-map-edits.json) → `RT-SGK1`.

---

## 7 · Limits of this memo

- **The two decisive papers were read at abstract level only** (PMID 16756948, PMID 22592656). Both
  are outside Europe PMC's open-access full-text set and neither has a PMC record. Every quotation is
  from the Europe PMC structured record and is marked as such at the point of use.
- **The citation screen is a Europe PMC `CITES:` retrieval**, which indexes reference lists Europe PMC
  has parsed. A citing paper Europe PMC has not indexed would not appear. Ten is therefore a floor on
  the citation count, and the "no follow-up exists" claim is a claim about those ten.
- **The "no clinical trial" statement is a statement about titles and abstracts** in a 1,248-record
  corpus, not a trial-registry query. A registered-but-unpublished trial would not appear.
  ⛔ **A registry query WAS attempted and its result must not be read as a finding.** A Europe PMC
  `SRC:CTX` dispatch on 2026-08-07 —
  `(SGK1 AND SRC:CTX) OR ("DNA-PK" AND SRC:CTX) OR (peposertib AND SRC:CTX) OR (AZD7648 AND SRC:CTX)`
  — returned **0 records**, and it returned 0 for **peposertib and AZD7648 as well**. Those two
  demonstrably have registry entries: `NCT03907969` is named in the abstract of PMID 40382524, quoted
  in §5's sibling memo. **So the zero is a property of this retrieval path, not of the registry.**
  The `sync` command in `scripts/fetch-paper.mjs` does not surface `SRC:CTX` records, and the
  known-positive terms are what shows it. ⚠ **An absent reading is not a reading of absence** — this
  one is recorded because a future session finding "0 SGK1 trials" in a log would otherwise read as
  evidence. A real registry read needs a `targets_file` corpus committed to `main` carrying a
  ClinicalTrials.gov API URL, which this agent could not add; it remains a genuine open $0 step.
- **No expression read was performed.** §4c states the request precisely so the finding, when it
  lands, attaches to a stated prediction rather than to a search.
