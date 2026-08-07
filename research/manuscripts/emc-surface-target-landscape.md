---
id: DOC-EMC-SURFACE-TARGET-LANDSCAPE
title: "In-silico surface-antigen prioritisation for extraskeletal myxoid chondrosarcoma: a surrogate search checked against the disease's own tissue"
level: L3
kind: manuscript
status: live
canonical_for:
  - the surface-antigen prioritisation for EMC and what EMC tumour tissue says about it
  - the grade of RT-B7H3
purpose: >
  The preprint for PUB-SURFACE-TARGETS. It reports an in-silico surface-antigen search built on a
  translocation-sarcoma surrogate and a normal-tissue prior, and then reports what happened when that
  search was finally checked against three EMC tumour-tissue cohorts: not one of the eleven therapeutic
  addresses its routes name is concordantly elevated in EMC relative to comparator sarcomas, and the one
  antigen that is elevated on both arrays — ALCAM, which no route names — has no normal-organ separation.
scope: >
  Public expression data only. Transcript, never protein; never surface localisation, density,
  selectivity, safety, a therapeutic window, or clinical readiness — none of those quantities is
  computed anywhere in this document or in any artifact it cites.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-07
last_verified: 2026-08-07
---
# In-silico surface-antigen prioritisation for extraskeletal myxoid chondrosarcoma: a surrogate search checked against the disease's own tissue

> **Preprint status (2026-07-03; ⛔ materially amended 2026-08-05, and its central framing REPLACED
> 2026-08-07 — read [Amendment 2](#amendment-2-2026-08-07---the-search-has-been-checked-against-emc-tumour-tissue-and-its-lead-antigen-does-not-survive-the-check)
> first, then [Amendment 1](#amendment-1-2026-08-05---the-cell-line-this-manuscript-called-the-one-real-emc-line-is-recorded-as-not-carrying-the-fusion)).**
> Computational, **hypothesis-generating** manuscript, extensively self-red-teamed (see
> [`emc-surface-target-redteam.md`](./emc-surface-target-redteam.md)). Its subject is now **an
> instrument and its audit**: a surface-antigen search that had to be run without the disease's own
> expression data, and the three EMC tumour cohorts that were subsequently read against it. The
> result is a **demotion**, and the demotion is the finding. No antigen is asserted as an EMC-validated
> target and none is asserted to be safe, selective or effective in EMC.
> ⚠ **Superseded, retained verbatim, because both were headlines of earlier versions and stay quotable:**
> the 2026-07-03 banner read *"surfaces one real EMC cell line's own profile"* and the title began
> *"…for extraskeletal myxoid chondrosarcoma: **one cell line**, a translocation-sarcoma surrogate…"*;
> the 2026-08-05 banner read that the analysis *"reports what an honest in-silico surface-antigen
> analysis for EMC can and cannot establish from public data"* and that its finding was that
> **"a rigorous selectivity test plus a hard normal-tissue-window filter leaves essentially no classic
> protein surface antigen that is both tumour-selective and normal-tissue-restricted."** That sentence
> is not withdrawn — it is now a statement about the **surrogate**, and §3.6–§3.9 report what the
> disease's own tissue says instead.

---

## Amendment 2 (2026-08-07) — ⛔ the search has been checked against EMC tumour tissue, and its lead antigen does not survive the check

**This manuscript's stated limit, in the endpoint register and in its own §6, was that every negative it
reported was "bounded by that surrogate basis rather than by an EMC tissue measurement". That limit no
longer holds, because the measurement now exists.** Three EMC tumour-tissue cohorts are read —
**GSE24369 on GPL6244**, **GSE4303 on GPL3290**, and **GSE28866 on 3SEQ**, the third of which carries
**27 normal-organ libraries** and so supplies the on-target/off-tumour exposure axis this analysis had
never been able to ask for. Every number lives in
[`emc-expression-panels.json`](../modalities/emc-expression-panels.json) →
`reads.read_8_SURFACE_ANTIGEN` / `gene_reads` and
[`gse28866-tumour-vs-normal.json`](../modalities/gse28866-tumour-vs-normal.json) → `per_gene.values`;
the canonical interpretation of the third cohort is
[`gse28866-tumour-vs-normal-reading.md`](./gse28866-tumour-vs-normal-reading.md), which this document
does not contradict.

⛔ **THE CHECK IS UNFAVOURABLE AND THAT IS THE POINT.** The search ran without the disease's own
expression data and named a set of therapeutic addresses. The disease's tissue now says that **not one of
the eleven addresses this manuscript's routes name is concordantly elevated in EMC relative to comparator
sarcomas** — and that the one antigen which *is* elevated on both arrays, **ALCAM, is an antigen no route
names, and it has no separation from normal visceral organ tissue on the only cohort that can measure
that**. A surrogate-bounded search whose leads do not reproduce when the disease is finally measured is a
result about the method, and it is a better paper than the one that was drafted, not a worse one.

### What Amendment 2 changes

| manuscript element | status after this amendment |
|---|---|
| The framing that the analysis's negatives are **bounded by the surrogate rather than by an EMC measurement** (§6, and the endpoint register's `what_it_would_claim`) | ⛔ **SUPERSEDED.** Three EMC tumour cohorts are read. The surrogate is now one instrument among several and its disagreements with the tissue are reported in §3.9 rather than being the paper's boundary |
| §3.4's **SSTR2 / GD2 neuroendocrine hypothesis**, nominated as one of the two questions "most worth testing" | ⚠ **DOWNGRADED, not closed.** SSTR2 has its first EMC-tissue readings (§3.7) and none of them shows elevation; the somatostatin-receptor family panel could not be scored at all on GPL3290. The GD2 proxy B4GALNT1 is flat, and its whole synthase panel is lower in EMC on **both** platforms. ⛔ None of this measures receptor protein density, which is the quantity a radioligand would see, so the hypothesis is weakened and **not** refuted |
| §3.2's headline that **B7-H3/CD276 is not selective** | ✅ **STRENGTHENED and re-based.** It was a surrogate result; CD276 now also reads **lower** in EMC tumour tissue than in comparator sarcomas on the one platform that can read it (§3.6). ⚠ It is **not readable at all** on GPL3290 — an instrument statement, never a low reading |
| §3.2's list of **eight significantly-selective antigens** (CDH11, KIT, FGFR1, NCAM1, GPC2, PTK7, MCAM, EPHB4) | ⚠ **NOT REPRODUCED.** In EMC tumour tissue **zero of the eight** are concordantly higher than comparator sarcomas on both arrays; two (FGFR1, PTK7) are concordantly **lower** (§3.5) |
| §3.3's conclusion that the **selective-and-restricted intersection is empty** | ⚠ **RE-SCOPED, and it was computed over a set that did not contain CSPG4** — a measured coverage gap in that instrument, not a rejection (§3.8). The statement stands for the antigens the filter actually saw |
| §3.5's finding that the **public EMC dataset GSE4303 is unusable** | ⛔ **SUPERSEDED BY AN INSTRUMENT CHANGE, not by new data** (§3.10). One of its seven platforms, GPL3290, is now readable through an accession bridge; the earlier "zero shortlist genes resolved" was a property of the symbol lookup, not of the deposit |
| §3.1 / Table 1 and everything downstream of the disputed cell line | ⛔ **UNCHANGED — still withdrawn** by [Amendment 1](#amendment-1-2026-08-05---the-cell-line-this-manuscript-called-the-one-real-emc-line-is-recorded-as-not-carrying-the-fusion). Amendment 2 does not restore it |
| §7's **collaboration request** | ✅ **SURVIVES, with a changed ask.** The decisive missing datum is no longer "any EMC expression data" — it is **protein and surface localisation**, plus a cohort large enough to carry a distribution (§7) |

### ⭑ The general lesson, which is again worth more than the specific correction

The 2026-08-05 amendment's lesson was *carrying a flag is not resolving one*. This one's is adjacent and
narrower: **a search that cannot see its own subject will still return a ranked list, and the list will
look like a result.** Nothing in the original ranking was miscomputed; every number in §3.2 and §3.3 is
reproducible and unretracted. What was wrong was the implicit inference from *"selective in the
surrogate"* to *"worth measuring in EMC"* — and the four candidate reasons the two instruments disagree
(§3.9) are all live, so this amendment does not replace one instrument's authority with another's.

---

## Amendment 1 (2026-08-05) — ⛔ the cell line this manuscript called "the one real EMC line" is recorded as NOT carrying the fusion

**This is a correction to the manuscript's own framing, published here rather than quietly edited away,
because the honest self-criticism is the point of the document and a correction that hides what it corrects
is not a correction.**

**What the 2026-07-03 version claimed, verbatim and still quotable:** the abstract said the DepMap
translocation-sarcoma class *"— contrary to the common assumption — **also contains one genuine EMC line
(H-EMC-SS / ACH-001519)** whose surface transcriptome we report directly (n = 1, descriptive)"*, §3.1 was
headed *"The one EMC line in public data — H-EMC-SS"* and called its top surface antigens *"the most
EMC-specific in-silico signal available"*, and §2.2 recorded that line's *"authentication and EWSR1::NR4A3
status flagged [to verify]"*.

**That flag now has an answer, and the answer is unfavourable.** Three independent readouts, recorded in
[`../modalities/emc-atr-vulnerability.json`](../modalities/emc-atr-vulnerability.json) →
`part_a_hemcss_identity` (verdict `NOT_FUSION_POSITIVE_PER_CURATED_RECORD`) and narrated in
[`emc-atr-vulnerability-assessment.md` §2](./emc-atr-vulnerability-assessment.md):

1. **Cellosaurus `CVCL_1238` carries an explicit curated caution, verbatim:** *"Caution: Does not harbor a
   gene fusion involving EWSR1 which is a hallmark of extraskeletal myxoid chondrosarcoma
   (PubMed=34413129)."*
2. **DepMap's own filtered fusion caller** (`OmicsFusionFiltered.csv`, 24Q4, 1,670 models) has the model
   **present** with **2** calls — `AL158209.1--NEBL` and `VIM--RPS25` — and **neither names NR4A3, EWSR1,
   TAF15 or FUS**. ⭑ The model being *in* the file is what makes this a reading of absence rather than an
   absent reading.
3. **NR4A3 transcript, independent of the caller:** **0.941 log2(TPM+1)** — 83rd percentile of 1,673 lines,
   but against a panel **median of 0.214**, i.e. most lines do not express NR4A3 at all. A fusion transcript
   carries the NR4A3 body under EWSR1's promoter and would be expected to read far higher. **Weak
   corroboration only.**

### ⚠ What this amendment does NOT claim — the boundary is load-bearing

Cell-line identity is settled by **STR authentication against the donor and RT-PCR for the fusion**. Neither
is in public data at the resolution needed and **neither is something this programme can perform** — it has
no bench. So this amendment establishes that **the public record does not support** the label this manuscript
applied; it does **not** establish what the line is instead, that the original characterisation was wrong, or
that the line is not EMC. A line can be misidentified, can drift in culture, or can be a genuine
fusion-negative tumour of the same histology — a real category, since a minority of EMC carries no identified
FET partner. Cellosaurus also records an 18-locus STR profile cross-referenced to DepMap `ACH-001519`,
COSMIC-CLP `907290` and RIKEN `RCB0508`: **the line is a real, profiled entity; the open question is what it
is, not whether it exists.**

### What is withdrawn, what survives, and what is unchanged

| manuscript element | status after this amendment |
|---|---|
| Title's *"one cell line"*, the abstract's *"one genuine EMC line"*, the banner's *"surfaces one real EMC cell line's own profile"*, §3.1's *"the most EMC-specific in-silico signal available"*, §7's *"DepMap additionally holds H-EMC-SS"* | ⛔ **WITHDRAWN.** These read the line as EMC-and-fusion-positive, which the public record does not support |
| §3.1 **Table 1** (the line's own top surface transcripts) | ⛔ **WITHDRAWN AS AN EMC READING; RETAINED AS DATA** and re-labelled a **single sarcoma line of disputed identity**. The numbers are real DepMap expression; what they are a profile *of* is what changed |
| §3.1's reading that DNER / RTN4 / PMP22 in Table 1 is *"loosely consistent with EMC's neuroendocrine/neural differentiation"* | ⛔ **WITHDRAWN.** It was a corroboration of §3.4 taken from this line. The manuscript already graded it *"a suggestion, not evidence"*; it is now not even that |
| §3.4's **SSTR2 / GD2 neuroendocrine hypothesis** | ✅ **SURVIVED Amendment 1** on the basis of EMC's **reported IHC** neuroendocrine differentiation (INSM1, synaptophysin — §1, still `[verify]`-flagged), never this line. ⚠ **Amendment 2 downgrades it on new evidence** (§3.7) |
| §3.2 **selectivity** (incl. the headline *B7-H3 is not selective, BH q = 1.0*) | ✅ **SURVIVES, RE-LABELLED.** The line is **1 of 45** class members carrying expression data, and the class must now be described as translocation-sarcoma **plus one line of disputed identity**. Quantified rather than asserted: recomputing every actionable antigen's `enrichment_vs_rest` with the line dropped moves it by **≤ 0.13 log2TPM** (largest: GPC3 0.93→0.81; CD276 0.14→0.15; CDH11 3.18→3.29), with **no sign flips**. ⚠ Honest limit: the rank-based Mann–Whitney *p* cannot be recomputed from the committed artifact, which stores summary statistics rather than per-line values, so the *q*-values are **not** re-derived here — the effect-size bound is |
| §3.3 **normal-tissue window** | ✅ **UNAFFECTED by Amendment 1.** Built entirely from Human Protein Atlas normal tissue; no cell line enters it |
| §3.5 (the public EMC dataset is unusable) and §7 (the collaboration request) | ⚠ **Amendment 1 called both "STRENGTHENED". Amendment 2 supersedes the first half** — GSE4303's GPL3290 arm is now readable (§3.10) — and narrows the second (§7) |

### ⭑ The general lesson, which is worth more than the specific correction

The `[to verify]` flag on this line was written honestly and carried faithfully in four places for a month.
**Carrying a flag is not resolving one.** What resolved it was one free API call that could have been made on
day one. The inventory of every repository file that leaned on this line is in
[`emc-atr-vulnerability-assessment.md` §2.3](./emc-atr-vulnerability-assessment.md); each of those files now
carries its own dated amendment, and the line's status is registered as an object
(`OBJ-LINE-HEMCSS`) in [`emc-systems-map.json`](./emc-systems-map.json) so a future claim that reads EMC
biology off it fails a checker rather than a reader.

---

**Keywords:** extraskeletal myxoid chondrosarcoma; EWSR1::NR4A3; surfaceome; normal-tissue exposure; antibody–drug
conjugate; CAR-T; radioligand therapy; ALCAM; CSPG4; SSTR2; surrogate validity.

---

## Abstract

**Background.** Extraskeletal myxoid chondrosarcoma (EMC) is a rare translocation sarcoma driven by the
*EWSR1::NR4A3* fusion, a nuclear transcription factor. Driver-directed routes (an NR4A3 degrader; a
fusion-junction antisense oligonucleotide) confront an intracellular-delivery or druggability gate.
Cell-surface antigens offer an orthogonal axis (ADC, CAR/NK, T-cell engager, radioligand therapy) whose
gating differs — but at the cost of the fusion-level selectivity the oligonucleotide uniquely offers. EMC
has been assumed to be absent from usable public expression data, so surface-antigen prioritisation for it
has had to run on surrogates.

**Methods.** We built a public-data pipeline in two stages. **Stage 1 (surrogate)**: a largely-unbiased human
surfaceome (UniProt plasma-membrane + transmembrane/GPI, unioned with a small actionable-antigen seed)
ranked by expression and by a rank-based selectivity test (Mann–Whitney, Benjamini–Hochberg) across a
translocation-sarcoma DepMap class (n = 76), then filtered by a hard normal-tissue prior (Human Protein
Atlas tissue *and* blood-cell specificity, with vital-tissue/immune overrides). That class also contains
the single line DepMap annotates *Extraskeletal Myxoid Chondrosarcoma* (H-EMC-SS / ACH-001519) — ⛔ **a line
whose fusion status the curated record contradicts, so it is NOT read here as EMC evidence; see
[Amendment 1](#amendment-1-2026-08-05---the-cell-line-this-manuscript-called-the-one-real-emc-line-is-recorded-as-not-carrying-the-fusion).**
*(Superseded, retained: this sentence read "— contrary to the common assumption — **also contains one genuine
EMC line (H-EMC-SS / ACH-001519)** whose surface transcriptome we report directly (n = 1, descriptive)".)*
**Stage 2 (the audit, new in this version)**: we then read three EMC **tumour-tissue** cohorts —
GSE24369/GPL6244 (6 EMC vs 29 comparator sarcomas), GSE4303/GPL3290 (10 vs 6), and GSE28866/3SEQ (4 EMC,
27 normal-organ and 32 non-EMC-sarcoma libraries) — and asked whether stage 1's leads reproduce. Positive,
negative and hard controls check each classifier branch; NR4A3, ENO3 and MKI67 check the tissue instrument.

**Results.** In the surrogate, selectivity is significant for CDH11, KIT, FGFR1, NCAM1, GPC2, PTK7, MCAM and
EPHB4 and — importantly — **not** for B7-H3/CD276 (BH q = 1.0), EGFR or FAP; the normal-tissue prior then
leaves **no** classic candidate both selective and restricted. **In EMC tumour tissue those priorities do not
reproduce.** **Not one of the eleven therapeutic addresses this manuscript's routes name is concordantly
elevated in EMC relative to comparator sarcomas** — CD248 and CD276 read lower on the one platform that can
read them, FAP and PRAME are flat on both, SSTR2 is flat, and the rest are discordant or single-platform —
and **zero of the eight surrogate-selective antigens are concordantly higher on both arrays** either; two,
FGFR1 and PTK7, are concordantly lower. The one antigen elevated on both arrays is **ALCAM** (Δ +1.091 and
+0.753 SD units), **which no route names**, and on the one cohort carrying normal organs its EMC median
(0.578) sits **below** the normal-tissue median (0.631) while remaining above other sarcomas (0.377) — the
lineage axis survives and the exposure axis does not. What is concordantly elevated in EMC tissue is a
**matrix/proteoglycan module**
(VCAN, BGN, CD44, GPC1) plus ALCAM, on a background that is already high everywhere. **CSPG4** is the largest
absolute row in the 3SEQ deposit and was **never evaluated by stage 1 at all** — a measured coverage gap —
but it moves strongly on one array and not the other, so it is held open rather than promoted.

**Conclusion.** Done rigorously, in-silico surface-target discovery for EMC does not hand over a clean target,
and when its output is finally checked against the disease's own tissue the leads largely do not reproduce.
The value of the work is a set of negatives with a named basis, an audited estimate of how far a
lineage-surrogate ranking transfers, and a specification of the measurement that would actually decide the
question. *(Superseded, retained: this sentence previously read that the work's value is "to de-risk
over-optimistic assumptions (especially B7-H3), to expose antigen-specific liabilities, and to nominate the
neuroendocrine SSTR2/GD2 route", and — before Amendment 1 — also credited it with "to surface the one
available EMC line's profile".)* The decisive validation — EMC surface *protein* expression with a
normal-tissue comparison — requires the patient-derived EMC models, and we invite their holders to
co-resolve it.

---

## 1. Introduction

EMC is a rare soft-tissue sarcoma (commonly cited as well under 1% of soft-tissue sarcomas [citation to
verify]) defined by a translocation fusing the 5′ region of *EWSR1* (less often TAF15/others) to the orphan
nuclear receptor *NR4A3*, producing a chimeric transcription factor on a genome with few recurrent secondary
mutations [Sjögren; Panagopoulos; whole-genome characterisation citation to verify]. Its line of differentiation
was long debated; recent immunohistochemistry supports a **neuroendocrine phenotype** — INSM1 is a
sensitive/relatively specific EMC marker and synaptophysin/NSE are frequently expressed, while S100 is only
focally positive [Yoshida/Modern Pathology 2017; comprehensive review 2025 — citations to verify].

**The intracellular-target bottleneck and the surface alternative.** Because the driver is nuclear,
driver-directed therapies act inside the cell and confront a druggability or oligonucleotide-delivery gate.
Cell-surface antigens enable modalities that change the problem: ADC (clinically validated antibody-mediated
delivery), T-cell engagers and CAR-T/NK (act at the surface; no intracellular delivery), and radioligand
therapy (payload is radiation). We stress at the outset that this is a *different* gating, **not** an obviously
easier one in EMC (§5), and that it sacrifices the fusion-exclusivity of the RNA route.

**The gap, and how it changed.** EMC surface-antigen expression has not been systematically mapped, and EMC
was assumed to be absent from usable public expression data. That assumption forced stage 1 of this work onto
a lineage surrogate, and it is the assumption this version tests: three EMC tumour cohorts turn out to be
readable at zero cost, two of them only after a probe-to-symbol accession bridge was built (§2.5, §3.10). So
this manuscript is no longer only a prioritisation. It is a prioritisation **and the audit of that
prioritisation against its own subject**, which is a rarer and more useful object: the field routinely builds
surrogate-based target lists for rare tumours and almost never gets to report what happened when the tumour
itself was measured.

---

## 2. Methods

All analyses are computational, use public data, run in CI at no compute cost, and commit their outputs
(Data & code). No wet-lab work was done. Provenance and per-stage controls are recorded in each output JSON.

### Stage 1 — the surrogate search

**2.1 Surfaceome.** UniProt-reviewed human proteins with a plasma-membrane location (SL-0039) plus a
transmembrane (KW-0812) or GPI-anchor (KW-0336) topology, unioned with a curated seed of actionable surface
antigens (so established targets are always evaluated). The committed run used **2,820 genes from UniProt ∪ 47
curated seed antigens** (41 of the seed already in the UniProt set) = **2,826 unique**, of which **2,692** are
present in the DepMap expression matrix and were scanned — so the seed is a small, mostly-redundant minority
and the set is largely, though **not strictly, unbiased**; the UniProt fetch status and counts are recorded in
the output. ⚠ **The scanned gene list itself was not recorded**, which is why §3.8's CSPG4 coverage gap is
`UNDECIDABLE` rather than resolvable. [`emc_surfaceome_scan.py`]

**2.2 Expression, selectivity, and the disputed line.** DepMap OmicsExpression (log2(TPM+1)). We defined a
translocation-sarcoma class by OncotreeSubtype (Ewing/synovial/alveolar/DSRCT/clear-cell, plus the single line
DepMap annotates *Extraskeletal Myxoid Chondrosarcoma*; n = 76) as a lineage-generic surrogate.
⛔ **That line — ACH-001519 (H-EMC-SS) — is recorded by Cellosaurus as NOT carrying an EWSR1 fusion
([Amendment 1](#amendment-1-2026-08-05---the-cell-line-this-manuscript-called-the-one-real-emc-line-is-recorded-as-not-carrying-the-fusion)),
so it is one of 45 class members with expression data and is NOT treated as EMC evidence.** Dropping it moves
every actionable antigen's `enrichment_vs_rest` by ≤ 0.13 log2TPM with no sign flips (Amendment 1), so the
selectivity result below does not rest on it. *(Superseded, retained: this paragraph read "— a correction to
the field's assumption — identified a **single genuine EMC line, ACH-001519 (H-EMC-SS)**… whose own top
surface antigens we report (n = 1, descriptive; H-EMC-SS authentication and EWSR1::NR4A3 status flagged
[to verify])".)* For each surface gene we report expression, an effect size (enrichment versus non-sarcoma
lineages), and a **rank-based one-sided Mann–Whitney p that the class exceeds the rest, Benjamini–Hochberg
corrected**. We are explicit that this is cross-*cancer* selectivity (a distinguishable-from-epithelial-tumours
descriptor), **not** a tumour-vs-normal contrast, and that it mechanically favours mesenchymal antigens because
the DepMap panel is epithelial-dominated. Self-check: housekeeping genes are excluded by construction (a
minimal sanity check, not validation); CD276 recovers as broadly expressed. [`emc_surfaceome_scan.py`]

**2.2b The measured limits of this instrument.** Four limits are computed rather than asserted, and each bears
on a conclusion below ([`surfaceome-instrument-limits.json`](../modalities/surfaceome-instrument-limits.json)):
**L1** — the scanned population is tumour-cell monoculture, so **no stromal/CAF compartment exists in it at
all**; **L2** — an antigen carried only by stroma reads at the floor, demonstrated with **LRRC15** (an
established sarcoma CAF antigen with a clinical ADC programme behind it) at `frac_expressed` **0.0**; **L3** —
a glycan such as oncofetal chondroitin sulfate has no gene and cannot be ranked at all; **L4** — **CSPG4 has no
per-gene row in any committed artifact of this instrument**, so its absence from §3.3's conclusion is a
coverage gap and not a negative; **L5** — the scan holds no EMC observation of FAP, for two independent
reasons (no CAF compartment, and the one "myxoid" line is the disputed one). ⚠ **L1/L2 mean the stage-1
verdict on FAP and CD248 is partly a statement about what monoculture can contain**, which is exactly why the
bulk-tissue read in §3.6 is not a redundant second opinion.

**2.3 Normal-tissue prior (stage 1's primary filter).** For each antigen we queried the Human Protein Atlas
for RNA tissue specificity, tissue distribution, per-tissue nTPM, **blood-cell specificity**, and
subcellular location, and classified a verdict with correct HPA semantics: only *tissue enriched* /
*group enriched* with a *restricted distribution* and no vital-tissue and no strong immune/circulating signal
is **RESTRICTED**; *tissue enhanced* (detected broadly with a peak) is **ENHANCED_BROAD**, not restricted;
*low tissue specificity* **or a "detected in all" distribution** is **BROAD_LIABILITY** (the distribution
override demotes e.g. MCAM, which is "group enriched" but detected in all tissues); and expression in a vital
tissue, or a *confined* blood signal (*immune-cell enriched* / *group enriched* — not weak *immune-cell
enhanced*), overrides all as **VITAL_OR_IMMUNE_LIABILITY**. Controls: DLL3/GPC3 (tumour-restricted) must be
RESTRICTED, B2M BROAD, and a **hard control CD3E** (an immune antigen) must NOT be RESTRICTED — all behaved as
specified. ⛔ HPA RNA is bulk normal tissue and a **prior**, not a safety statement, and mRNA is not surface
protein. [`emc_surface_normal_window.py`]

### Stage 2 — the EMC tumour-tissue audit (new in this version)

**2.4 Three cohorts, two axes, three platform families.** Every contrast below has its one home in
[`emc-expression-panels.json`](../modalities/emc-expression-panels.json) and
[`gse28866-tumour-vs-normal.json`](../modalities/gse28866-tumour-vs-normal.json).

| cohort | platform | EMC | comparator arm | what it is the axis for |
|---|---|---|---|---|
| **GSE24369** | GPL6244 (Affymetrix Gene ST, single-channel) | 6 | 29 sarcomas: 17 LGFMS, 6 desmoid fibromatosis, 6 fibrosarcoma | **lineage** — EMC vs other soft-tissue tumours |
| **GSE4303** | GPL3290 (two-colour cDNA, log-ratio vs a reference pool) | 10 | 6 sarcomas: 3 DFSP, 3 GIST | **lineage**, second cohort, different comparators |
| **GSE28866** | 3SEQ (3′-end sequencing, read density) | 4 | **27 normal-organ libraries** (bowel, breast, colon, kidney, lung, uterus) **and 32 non-EMC sarcoma libraries** (DDLPS, ESS, EWS, GIST, LMS, MLPS, SS) | **on-target/off-tumour exposure** (the normal arm) **and** lineage (the sarcoma arm) |

⛔ **THE TWO AXES ARE DIFFERENT QUESTIONS AND ARE NEVER COLLAPSED HERE.** The 27 normals are visceral organs
with almost no soft tissue in them, so a gene high in EMC against that panel is **not** thereby shown to be
EMC-specific rather than mesenchymal-lineage-specific; and a gene high against other sarcomas says nothing
about normal-organ exposure. This is stated at length in
[`gse28866-tumour-vs-normal-reading.md` §1](./gse28866-tumour-vs-normal-reading.md), which is canonical for it.

⛔ **3SEQ 3′-END READ DENSITY IS NOT ARRAY INTENSITY AND THE TWO ARE NEVER POOLED.** Array figures below are
**Δ = EMC mean z minus comparator mean z, in SD units of that array's own probe distribution**, with Welch *t*
and df; 3SEQ figures are **ratios of medians of per-peak medians** and carry no test at all. A statement that
mixes them is a category error, and no statement below does.

**2.5 Readability is reported as an instrument state, never as a low reading.** GPL3290's probes carry EST
accessions only, so a gene can be unreadable there purely because its accession did not resolve through the
curated-dictionary + UniGene + live-query bridge. Every gene therefore carries a **cross-platform state** —
`CONCORDANT_UP_ON_BOTH`, `CONCORDANT_DOWN_ON_BOTH`, `DISCORDANT_OPPOSITE_SIGNS`,
`MOVED_ON_ONE_FLAT_ON_THE_OTHER`, `FLAT_ON_BOTH`, `READABLE_ON_ONE_PLATFORM_ONLY`,
`NOT_READABLE_ON_EITHER_PLATFORM` — and the last two are **instrument statements**. ⛔ **An absent reading is
not a reading of absence:** CD248, CD276 and SSTR2 are unreadable on GPL3290, and nothing in this manuscript
treats that as evidence about their expression. A curated panel is scored only above a floor of 3 readable
genes and 0.5 coverage; two panels fall below it and emit **no score**.

**2.6 The tissue instrument's own controls.** Before any antigen is read, three genes with known answers are
read on the same platforms ([`emc-expression-panels.json`](../modalities/emc-expression-panels.json) →
`reads.control`): **NR4A3** must be up (it is the disease-defining over-expression) — Δ **+0.741** (*t* = 4.66)
on GPL6244, EMC at the 76th array percentile, and on 3SEQ its median across the 32 non-EMC sarcomas is
**0.000** against **0.216** in EMC; **ENO3**, a published direct transactivation target of an NR4A3 fusion
(PMID 26310886), must be up — Δ **+0.808** (*t* = 3.61) and **+3.811** (*t* = 13.22), and 2.53×/2.02× on 3SEQ;
**MKI67** must be approximately flat, because EMC is slow-cycling and a large proliferation delta would mean
the contrast is being driven by cellularity — Δ **+0.129** (*t* = 0.53) on GPL6244. ⚠ NR4A3 emits **no
contrast** on GPL3290, where only 2 comparator samples carry a value against a floor of 3. **These are
controls, not results:** they license reading the other rows, and they license nothing else.

**2.7 Uncorrected by design.** No multiple-testing correction is applied anywhere in the tissue read. The
reads were specified before the tables were parsed, and each is reported with its *t* and df so a reader can
apply their own. **A |t| threshold in a verdict is a readability aid and not a test**, and with n = 6 and
n = 10 archival tumours nothing here settles anything at the level of a population.

---

## 3. Results

### 3.1 ⛔ WITHDRAWN AS AN EMC READING — the DepMap line annotated EMC, and why it is not EMC evidence

> ⛔ **This section is retained, not deleted, and its claim is withdrawn.** It read, verbatim: *"### 3.1 The
> one EMC line in public data — H-EMC-SS. Contrary to the assumption that EMC is absent from public cell-line
> panels, DepMap contains one line annotated Extraskeletal Myxoid Chondrosarcoma — **ACH-001519 / H-EMC-SS**.
> Its own top surface-antigen transcripts are the most EMC-specific in-silico signal available (n = 1,
> descriptive; no statistics; authentication/fusion status [to verify])."* The `[to verify]` was answered on
> 2026-08-05 and the answer contradicts the label —
> [Amendment 1](#amendment-1-2026-08-05---the-cell-line-this-manuscript-called-the-one-real-emc-line-is-recorded-as-not-carrying-the-fusion).

DepMap does contain one line whose OncotreeSubtype string is *Extraskeletal Myxoid Chondrosarcoma* —
**ACH-001519 / H-EMC-SS**. **Cellosaurus `CVCL_1238` records, citing a primary source, that it "does not
harbor a gene fusion involving EWSR1 which is a hallmark of extraskeletal myxoid chondrosarcoma"; DepMap's own
filtered fusion caller lists 2 calls for the model and neither names NR4A3 or any FET gene.** Its
transcriptome is therefore reported below as **a single sarcoma line of disputed identity**, not as EMC data,
and nothing downstream is read from it as an EMC property. ⚠ This is a statement about the **public record**,
not an STR-authenticated identity test — see Amendment 1 for what it cannot settle.

**Table 1. ACH-001519 / H-EMC-SS top surface-antigen transcripts — ⛔ a single sarcoma line of DISPUTED
identity, NOT an EMC profile** (log2(TPM+1); single sample, descriptive;
[`emc-surfaceome-scan.json` → `emc_line_top_surface`]).

| Rank | Antigen (log2TPM) | Rank | Antigen (log2TPM) |
|---|---|---|---|
| 1 | APP (9.9) | 9 | CD164 (8.5) |
| 2 | CD63 (9.5) | 10 | DNER (8.5) *neural* |
| 3 | **FGFR1 (9.3)** | 11 | BSG/CD147 (8.2) |
| 4 | SLC38A2 (9.0) | 12 | RTN4/Nogo (8.2) *neural* |
| 5 | GPRC5B (8.9) | 13 | MMP14 (8.1) |
| 6 | PERP (8.8) | 14 | ITGB1 (7.9) |
| 7 | SLC3A2 (8.6) | 15 | PMP22 (7.8) *neural/myelin* |
| 8 | CD81 (8.5) | 16 | ALCAM (7.7) |

One honest reading survives. The list is **dominated by ubiquitous membrane proteins** (APP, the tetraspanins
CD63/CD81, BSG/CD147, ITGB1, ALCAM) — raw single-line expression surfaces housekeeping surface proteins, which
is precisely why the selectivity and normal-tissue filters below are necessary and why "highly expressed" is
not "targetable". **That reading is about single-line expression as an instrument and holds for any line.**

⛔ **The second reading is WITHDRAWN and retained verbatim, because it was a corroboration of §3.4 and must
stay quotable:** *"Second, **FGFR1 ranks third** and several **neural-associated surface proteins (DNER,
RTN4/Nogo, PMP22)** appear — loosely consistent with EMC's neuroendocrine/neural differentiation (§1), though
from a single line this is a suggestion, not evidence, for the SSTR2/GD2 hypothesis (§3.4). This one line
cannot carry statistical weight; it anchors the analysis in an established EMC line (ECACC-catalogued
H-EMC-SS; authentication/fusion status [to verify]) and is exactly the data that, at n ≫ 1, would resolve the
questions below."* ⚠ **A neural-marker pattern in a line the curated record does not accept as EMC is not
evidence about EMC**, and the manuscript's own hedge ("a suggestion, not evidence") does not rescue it —
§3.4's hypothesis rests on EMC's **reported IHC** phenotype and must be read from there alone. ⭑ **And FGFR1's
appearance here is now doubly uninformative**: in EMC tumour tissue FGFR1 is `CONCORDANT_DOWN_ON_BOTH` arrays
(§3.5).

### 3.2 Stage 1 selectivity across the translocation-sarcoma class — and B7-H3 is not selective

With a rank-based, BH-corrected test (surrogate class vs non-sarcoma lineages; [`emc-surfaceome-scan.json`]):

| Antigen | Enrichment (log2TPM, class − rest) | BH q | Significantly selective? |
|---|---|---|---|
| KIT | +2.46 | ~0 | yes |
| CDH11 | +3.18 | ~0 | yes |
| FGFR1 | +1.99 | ~0 | yes |
| NCAM1/CD56 | +1.74 | ~0 | yes |
| GPC2 | +1.49 | ~0 | yes |
| PTK7 | +1.24 | 2e-4 | yes |
| MCAM/CD146 | +1.09 | 3e-3 | yes |
| EPHB4 | +1.0 | 3e-4 | yes |
| **B7-H3/CD276** | **+0.14** | **1.0** | **NO** |
| FAP | +0.02 | 0.16 | no |
| EGFR | −2.21 | 1.0 | no |

Two cautions, stated up front. First, this is **cross-cancer** selectivity, which the epithelial-dominated
DepMap panel biases toward mesenchymal antigens (CDH11's +3.18 is largely "not expressed by carcinomas", not
"tumour-specific"). Second, mRNA magnitude to two decimals conveys false precision about surface-protein
density; read these as **coarse tiers**. (Note also that the single EMC line of §3.1 is one of the 76 class
lines, so its ~1/76 contribution is negligible and FGFR1 appearing in both §3.1 and §3.2 is *not* independent
corroboration.) The one decision-grade result here is negative and useful: **B7-H3,
the field's default EMC surface target, is not significantly selective in the data** (q = 1.0). B7-H3 protein
can be tumour-restricted despite broad mRNA — the basis of its clinical traction — so this is a
selectivity-of-transcript caveat, not a claim about protein; but it removes the transcriptomic rationale for
treating B7-H3 as the obvious first choice. ⭑ **§3.6 now adds the EMC-tissue reading of the same antigen, and
it points the same way.**

⚠ **A third caution, added 2026-08-07 and specific to two rows.** **FAP** and **CD248** are stromal antigens,
and §2.2b's L1/L2 show this instrument has no stromal compartment — LRRC15 reads at `frac_expressed` 0.0 in
it. So "FAP is not selective (q = 0.16)" is a statement about tumour cells in culture and is **not** a
statement about FAP in an EMC tumour. §3.6 is the instrument that can speak to that, and it happens to point
the same way — which is a coincidence of direction, not a corroboration.

### 3.3 Stage 1's normal-tissue prior is decisive — and leaves no clean classic antigen

Applying the hard filter (controls behaved as specified: DLL3/GPC3 → RESTRICTED, B2M → BROAD, CD3E →
VITAL_OR_IMMUNE_LIABILITY; [`emc-surface-normal-window.json`]):

| Antigen | HPA tissue specificity | Blood-cell signal | Verdict |
|---|---|---|---|
| **B4GALNT1 (GD2 synthase)** | Tissue enriched | none | **RESTRICTED** |
| CDH11 | Tissue enhanced | none | ENHANCED_BROAD |
| GPC2 | Tissue enhanced | none | ENHANCED_BROAD |
| FAP | Tissue enhanced | none | ENHANCED_BROAD |
| SSTR2 | Tissue enhanced | none | ENHANCED_BROAD |
| EGFR | Tissue enhanced | none | ENHANCED_BROAD |
| FGFR1 | Low tissue specificity | — | BROAD_LIABILITY |
| MCAM/CD146 | Group enriched | none | BROAD_LIABILITY |
| EPHB4 | Low tissue specificity | immune enhanced | BROAD_LIABILITY |
| CD276/B7-H3 | Low tissue specificity | none | BROAD_LIABILITY |
| ERBB2 | Low tissue specificity | immune enhanced | BROAD_LIABILITY |
| **NCAM1/CD56** | Tissue enhanced | **immune enriched (NK)** | **VITAL_OR_IMMUNE_LIABILITY** |
| **PTK7** | Low tissue specificity | **immune enriched** | **VITAL_OR_IMMUNE_LIABILITY** |
| **KIT** | Tissue enhanced | **group enriched (haematopoietic/mast)** | **VITAL_OR_IMMUNE_LIABILITY** |

The intersection of §3.2 (selective) and §3.3 (restricted) among classic protein antigens is **empty**
(**Figure 1**: antigens plotted by selectivity × normal-tissue tier; the selective-and-restricted quadrant is
unpopulated — [`emc-surface-prioritization.png`]). ⚠ **Figure 1 renders stage 1 only. No figure exists for the
EMC-tissue axis**, and the tables in §3.5–§3.6 are that axis's whole presentation. The candidates fail in
specific, nameable ways:
- **NCAM1/CD56** is on NK cells (fratricide risk for CAR/NK; a circulating compartment) and neural tissue; the
  CD56 ADC **lorvotuzumab mertansine (IMGN901)** was clinically developed and discontinued (no efficacy benefit,
  added toxicity) [Socinski/Spira — citations to verify]. It is not a clean target despite its selectivity.
- **CDH11** is broadly expressed in normal fibroblasts, synovium and bone (an established rheumatoid-arthritis/
  fibrosis target); its high cross-cancer enrichment is the mesenchymal-vs-epithelial artifact above. Pairing it
  with binary-kill modalities (CAR/TCE) would attack normal mesenchyme body-wide.
- **B7-H3, EGFR, FAP** are non-selective and/or broad; **FGFR1/MCAM/EPHB4** are liabilities on this prior.
- **GD2** (via the B4GALNT1 proxy — GD2 is a glycolipid, not a gene product, so this is indirect) has the only
  restricted normal-tissue prior here, consistent with GD2's known tumour-restricted profile — but **whether
  EMC expresses GD2 is not measured by anything in this manuscript**, so this is a favourable prior and not
  evidence of an EMC target.

⚠ **This intersection was computed over the antigens the filter actually saw, and CSPG4 was not among them**
(§2.2b L4, §3.8). "Empty" therefore means *empty of the classic antigens that were evaluated*, which is
weaker than it originally read.

### 3.4 The neuroendocrine hypothesis as it stood before the tissue read — SSTR2 and GD2

EMC's neuroendocrine differentiation (INSM1+, synaptophysin+; §1 — **reported IHC, still `[verify]`-flagged;
this is the hypothesis's ONLY basis**) motivated two candidate targets absent from prior EMC surface
discussions. ⚠ **Amendment 1 withdrew the §3.1 corroboration this section previously drew from the DepMap
line's neural surface transcripts.** ⛔ **Amendment 2 downgrades the hypothesis itself on new evidence — read
§3.7 with this section, which is retained as the statement of what was proposed and why.**
- **SSTR2 (somatostatin receptor 2)** — the target of the *approved* radioligand **¹⁷⁷Lu-DOTATATE**
  (Lutathera; approved for gastroenteropancreatic neuroendocrine tumours on the NETTER-1 trial [Strosberg et
  al., *N Engl J Med* 2017 — verify]) and its ²²⁵Ac α-analogues. If EMC's neuroendocrine phenotype
  extends to SSTR2 surface expression, an off-the-shelf theranostic (SSTR-PET + peptide-receptor radioligand
  therapy) becomes testable without a bespoke agent. The first gate is whether EMC expresses SSTR2 at all;
  *if* it does, then — its normal-tissue verdict being ENHANCED_BROAD (SSTR2 is expressed in normal
  neuroendocrine/GI tissue) — dosimetry, not novelty, is the remaining gate, as for approved NET-RLT.
- **GD2** — a surface glycolipid with mature CAR/antibody platforms and (via B4GALNT1) the only
  restricted-prior signal in §3.3.

These were hypotheses requiring direct EMC measurement (SSTR2 IHC/PET; GD2 immunostaining), not claims.

---

### 3.5 ⛔ THE AUDIT — stage 1's selective antigens do not reproduce in EMC tumour tissue

Every antigen §3.2 called significantly selective now has a reading in EMC tumour tissue. **None of the eight
is concordantly higher in EMC than in comparator sarcomas on both arrays. Two are concordantly lower.**
(Δ = EMC mean z − comparator mean z, SD units of that array's own probe distribution; Welch *t*;
[`emc-expression-panels.json` → `reads.read_8_SURFACE_ANTIGEN.cross_platform_board`].)

| Antigen | stage-1 BH q | GPL6244 Δ (*t*) | GPL3290 Δ (*t*) | cross-platform state |
|---|---|---|---|---|
| **FGFR1** | ~0 | **−0.778** (−4.54) | **−1.940** (−12.19) | ⛔ `CONCORDANT_DOWN_ON_BOTH` |
| **PTK7** | 2e-4 | **−0.524** (−3.87) | **−0.658** (−4.55) | ⛔ `CONCORDANT_DOWN_ON_BOTH` |
| CDH11 | ~0 | +0.318 (+2.65) | −1.181 (−3.78) | ⚠ `DISCORDANT_OPPOSITE_SIGNS` |
| MCAM/CD146 | 3e-3 | −0.288 (−2.65) | +0.279 (+1.18) | `MOVED_ON_ONE_FLAT_ON_THE_OTHER` |
| KIT | ~0 | +1.353 (+3.03) | +0.399 (+0.55) | `MOVED_ON_ONE_FLAT_ON_THE_OTHER` |
| NCAM1/CD56 | ~0 | −0.268 (−1.08) | +1.028 (+1.97) | `FLAT_ON_BOTH` |
| EPHB4 | 3e-4 | +0.050 (+0.56) | +0.614 (+1.72) | `FLAT_ON_BOTH` |
| GPC2 | ~0 | −0.015 (−0.36), EMC at the **31st** array percentile | ⛔ not readable | `READABLE_ON_ONE_PLATFORM_ONLY` |

**And the two antigens stage 1 called *not* selective read the same way in tissue**, which is the part of the
comparison that works: **EGFR** is `CONCORDANT_DOWN_ON_BOTH` (−0.619, *t* = −3.41; −0.670, *t* = −2.02), and
**CD276** is lower in EMC on the one platform that reads it (§3.6). ⭑ **So the surrogate's *negatives*
transferred and its *positives* did not** — which is the asymmetry a reader should take away, and it is the
opposite of the asymmetry an over-optimistic reading would assume.

⚠ **Three things this table is not.** It is **not** a refutation of §3.2, which asked a different question
(sarcoma lines vs other cancer lineages, in monoculture) and answered it correctly. It is **not** corrected
for multiple testing. And a `FLAT_ON_BOTH` or single-platform row is **not** a demonstration that the antigen
is absent — §2.5.

### 3.6 ⛔ THE HEADLINE — no route-named therapeutic address is concordantly elevated in EMC tumour tissue

The read's `route_named_addresses` panel is **eleven** genes, and its membership is not chosen here: it is
assembled from the therapeutic addresses this manuscript's own routes NAME (RT-CART-SURFACE, RT-B7H3,
RT-PRAME-IMMTAC, RT-SSTR2, RT-FAP-RLT, RT-TCRT-CTA), plus the two coverage corrections of §2.2b
([`emc-expression-panels.json`](../modalities/emc-expression-panels.json) →
`reads.read_8_SURFACE_ANTIGEN.provenance`). **Not one of the eleven is `CONCORDANT_UP_ON_BOTH` in EMC
tumour tissue:**

| Route-named address | GPL6244 Δ (*t*), EMC array percentile | GPL3290 Δ (*t*) | 3SEQ vs 27 normal organs | 3SEQ vs 32 other sarcomas | state |
|---|---|---|---|---|---|
| **CD248** (stromal) | **−0.698** (−2.32), 59th | ⛔ not readable | 0.84× | 0.65× | `READABLE_ON_ONE_PLATFORM_ONLY` |
| **CD276/B7-H3** (RT-B7H3) | **−0.249** (−2.55), 79th | ⛔ not readable | 1.30× | 1.42× | `READABLE_ON_ONE_PLATFORM_ONLY` |
| **FAP** (RT-FAP-RLT) | −0.265 (−0.81), 88th | −0.144 (−0.55) | 1.63× | 1.59× | `FLAT_ON_BOTH` |
| **SSTR2** (RT-SSTR2) | −0.042 (−0.40), 60th | ⛔ not readable | 1.54× | 1.37× | `READABLE_ON_ONE_PLATFORM_ONLY` |
| **PRAME** (RT-PRAME-IMMTAC) | −0.004 (−0.05), **30th** | +0.868 (+1.43), **11th** | normal median **0.000** | **0.53×** | `FLAT_ON_BOTH` |
| **CSPG4** (coverage correction, §2.2b L4) | **+0.885** (+7.42), 81st | −0.189 (−0.40) | 3.31× | 2.51× | `MOVED_ON_ONE_FLAT_ON_THE_OTHER` |
| ALPP | −0.021 (−0.34), 32nd | +0.315 (+1.59) | — | — | `FLAT_ON_BOTH` |
| MSLN | −0.086 (−2.53), 42nd | +0.835 (+2.10) | 0.27× | 1.23× | ⚠ `DISCORDANT_OPPOSITE_SIGNS` |
| GPC3 | −0.508 (−3.25), 28th | +0.804 (+2.15) | **0.09×** | 0.48× | ⚠ `DISCORDANT_OPPOSITE_SIGNS` |
| L1CAM | +0.096 (+0.86), 44th | +1.883 (+3.93) | 0.33× | 1.62× | `MOVED_ON_ONE_FLAT_ON_THE_OTHER` |
| CDH17 | −0.135 (−4.67), 14th | +0.515 (+0.92) | 0.91× | 0.50× | `MOVED_ON_ONE_FLAT_ON_THE_OTHER` |

⭑ **And the one antigen that IS `CONCORDANT_UP_ON_BOTH` is one no route names.** ALCAM sits in the read's
`sarcoma_cell_surface_addresses` panel, not in `route_named_addresses`, and appears nowhere in the route
register:

| Not route-named | GPL6244 Δ (*t*), EMC array percentile | GPL3290 Δ (*t*) | 3SEQ vs 27 normal organs | 3SEQ vs 32 other sarcomas | state |
|---|---|---|---|---|---|
| **ALCAM** | **+1.091** (+7.01), 99th | **+0.753** (+2.21) | **0.578 / 0.631 = 0.92×** | 1.53× | ✅ `CONCORDANT_UP_ON_BOTH` |

⚠ **Six of these twelve genes gained their first EMC-tissue array contrast on 2026-08-07** — ALCAM, CD248,
CD276, FAP, PRAME and SSTR2 — when a lost surface-antigen read was restored to the panel module. **Five of
the six are route-named and all five are flat or lower; the sixth is ALCAM.** Before that date the routes
that name these addresses had **no EMC measurement of them at all**, which is what their records still say.

**Read the rows, not just the count.**

- **ALCAM is the only antigen in either table elevated on both arrays, and it is the one the exposure axis
  demotes.** Its EMC 3SEQ median (0.578) sits **below** the normal-organ median (0.631) while staying above
  other sarcomas (0.377). ⇒ **the lineage half survives and the exposure half does not**, and for a
  surface-directed modality the exposure axis is the one that decides whether the address is usable at all.
  **ALCAM as an EMC-vs-sarcoma marker is untouched by this**; what is weakened is ALCAM as a therapeutic
  address. ⚠ This is a single cohort, n = 4, transcript-level, on 2 peaks, and it is **not** a safety
  statement about anything.
- **CD248 (endosialin/TEM1) inverts.** It is the surrogate scan's **only** selectivity-significant antigen
  among this set (`enrichment_vs_rest` 2.29, q = 0.0 —
  [`surfaceome-instrument-limits.json`](../modalities/surfaceome-instrument-limits.json) →
  `limits.L2_stromal_floor_demonstrated`), and in EMC tissue it is **lower** than comparator sarcomas on the
  one platform that reads it, and below normal organs on 3SEQ. §3.9 records the disagreement without
  resolving it.
- **CD276/B7-H3 points the same way in tissue as in the surrogate.** Lower in EMC than comparator sarcomas
  (*t* = −2.55), while sitting at the 79th array percentile — i.e. **expressed and not differential**, which
  is exactly the profile that makes an antigen a poor discriminator rather than an absent one.
- **FAP is flat, and the comparator arm is why that is interesting.** GSE24369's comparators are desmoid
  fibromatosis and fibrosarcoma — fibroblastic lesions in which FAP is expected to be high — so "not higher
  than the comparator" is partly a statement about the comparator. EMC itself sits at the **88th** array
  percentile, so this is **not** a reading that EMC lacks FAP. What it does say is that a FAP-directed route
  cannot claim EMC as a selectively FAP-rich indication among soft-tissue tumours. The whole
  **stromal/matrix panel** (13 genes: FAP, CD248, LRRC15, PDGFRA/B, ANTXR1, TNC, MMP14, POSTN, THY1, FN1,
  COL11A1, ACTA2) is lower in EMC on **both** platforms (−0.328, *t* = −1.89; −0.467, *t* = −1.80) — the one
  panel-level result that is concordant and unfavourable.
- **PRAME reads at the floor of every readable cohort.** 30th array percentile on GPL6244 with Δ ≈ 0; 11th
  percentile of log-ratios on GPL3290, where its nominally positive Δ has |*t*| = 1.43 and is flat; and a
  3SEQ EMC median of 0.102 that is **half** the other-sarcoma median, on a single peak. ⚠ **The 3SEQ normal
  median for PRAME is 0.000, so the "vs normal" ratio is undefined and is not reported** — a cancer-testis
  antigen being absent from normal organs is expected and says nothing about EMC.
- **The precondition for the two HLA-directed routes is down on both platforms.** The antigen-presentation
  panel (B2M, HLA-A/B/C, TAP1/2, TAPBP, NLRC5, PSMB8/9, CIITA, ERAP1) reads lower in EMC than comparator
  sarcomas on GPL6244 (−0.216, *t* = −2.90, 12/12 readable) and GPL3290 (−0.228, *t* = −0.84, 11/12). ⚠ The
  second is not significant on any reading and the panel is a **precondition**, not a target — but a
  TCR-directed or ImmTAC-style route needs class-I presentation, and this is the direction that route does
  not want.

⚠ **The panel-level score for the route-named addresses disagrees between platforms and is reported as such**:
lower in EMC on GPL6244 (−0.0935, *t* = −1.66, 11/11 readable) and higher on GPL3290 (+0.599, *t* = 2.91,
**8/11** readable). ⛔ **The three genes missing from the GPL3290 score are CD248, CD276 and SSTR2 — three of
the four that read down or flat on GPL6244** — so the two panel scores are not computed over the same set and
the disagreement is partly a coverage artifact. **The per-gene table above is the honest presentation; the
panel scores are not.**

### 3.7 SSTR2 and GD2 get their first EMC readings, and neither supports the hypothesis

§3.4 nominated these as the two questions most worth testing. Both now have EMC-tissue readings, and **the
readings are unsupportive without being decisive**:

- **SSTR2.** On GPL6244, EMC sits at the **60th percentile** of the array's own probe distribution with
  Δ = −0.042 (*t* = −0.40) against comparator sarcomas — **present, mid-distribution, and indistinguishable
  from the comparators**. Not readable at all on GPL3290, and the whole **somatostatin-receptor family panel
  (SSTR1–5) could not be scored there**: 1 of 5 genes readable, coverage 0.20 against a floor of 0.50, so the
  artifact **emits no score** and records this as an instrument limit. On GPL6244 the family panel is flat
  (−0.008, *t* = −0.20, 5/5 readable). On 3SEQ, EMC is 1.54× the normal-organ median and 1.37× other sarcomas,
  on 2 peaks and n = 4.
- **GD2, via B4GALNT1.** Flat on GPL6244 (Δ = −0.069, *t* = −1.00, EMC at the **49th** array percentile) and
  not readable on GPL3290. Its whole **glycan-synthase panel** (B4GALNT1, ST8SIA1, ST3GAL5, B3GALT4, FUT4) is
  **lower in EMC on both platforms** (−0.147, *t* = −4.96; −1.050, *t* = −3.44). ⛔ **GD2 is a glycolipid and
  B4GALNT1 is a synthase, so this is a proxy for a proxy** and cannot exclude the antigen.

⇒ **What changes.** The hypothesis was that EMC's reported neuroendocrine phenotype might extend to SSTR2
surface expression at a level worth imaging. Its first EMC transcript readings show no elevation over other
soft-tissue tumours and no striking absolute signal. ⛔ **What does NOT change:** a peptide-receptor
radioligand route depends on **absolute receptor protein density and tumour-to-normal uptake ratio**, and
**no quantity in this manuscript measures either**. A single ⁶⁸Ga-DOTATATE scan or an SSTR2 IHC on archival
EMC remains the cheap decisive measurement, and these readings lower the prior for it rather than removing
the reason to do it.

### 3.8 CSPG4 — the largest row in the new data, and a gene stage 1 never evaluated

**CSPG4 has no per-gene row in any committed artifact of the stage-1 instrument.** Whether it was ever scanned
is recorded as `UNDECIDABLE` — the artifact stores gene counts but not the gene list — so **its absence from
§3.3's empty intersection is a measured coverage gap, not a rejection**
([`surfaceome-instrument-limits.json`](../modalities/surfaceome-instrument-limits.json) →
`limits.L4_cspg4_coverage_gap`). It matters because CSPG4 is one of the two carrier proteoglycans the founding
oncofetal-chondroitin-sulfate work names, and the surfaceome seed held only the other one (CD44).

In EMC tissue it is the **largest absolute row in the 3SEQ deposit** — EMC median **8.730**, an order of
magnitude above every other row in that panel, 3.31× the normal-organ median and 2.51× other sarcomas — and it
moves strongly on GPL6244 (Δ +0.885, *t* = 7.42) and not at all on GPL3290 (Δ −0.189, *t* = −0.40).

⚠ **State the shape precisely, because two shapes license different next steps.** The artifact's classifier
records `MOVED_ON_ONE_FLAT_ON_THE_OTHER`, **not** `DISCORDANT_OPPOSITE_SIGNS`: the GPL3290 value is negative
in sign but flat by magnitude, so this is *"strongly up here, silent there"* rather than *"up here, down
there"*. **The row does not replicate; it is also not contradicted.** Two candidate explanations are live and
neither is settled here — the GPL3290 comparator arm is **n = 6** (3 DFSP, 3 GIST) with an unusually high
CSPG4 mean, and **DFSP is a dermal fibroblastic tumour while CSPG4/MCSP is a well-known melanocytic and
pericytic antigen**, so a high comparator arm would flatten the contrast for reasons that are about the
comparator rather than about EMC. The 3SEQ row rests on **one peak** and n = 4, and HPA already places CSPG4
on the broad-liability list, so its normal-tissue behaviour beyond those six organs is unaddressed by
anything here.

⇒ **CSPG4 is held open: not promoted, not buried.** What it earns is a place in the next pass and an explicit
note that the original "no clean antigen" conclusion was computed without it.

### 3.9 What IS elevated in EMC tissue is a matrix module — and the two instruments invert on the genes that matter

Across the 100 genes on the cross-platform board, exactly **five** are `CONCORDANT_UP_ON_BOTH` arrays:
**VCAN**, **BGN**, **CD44**, **GPC1** and **ALCAM**. Four of the five are matrix or proteoglycan genes; ALCAM
is the only classical single-pass cell-surface adhesion molecule among them.

| Gene | GPL6244 Δ (*t*) | GPL3290 Δ (*t*) | 3SEQ vs normal | 3SEQ vs other sarcomas |
|---|---|---|---|---|
| VCAN | +0.629 (+3.94) | +1.561 (+4.76) | 3.33× | 2.01× |
| BGN | +0.400 (+4.14) | +1.733 (+3.87) | 1.91× | 2.49× |
| CD44 | +0.711 (+7.86) | +0.707 (+3.04) | 1.69× | 1.64× |
| GPC1 | +0.187 (+3.11) | +1.000 (+4.01) | — (not in the 3SEQ panel) | — |
| ALCAM | +1.091 (+7.01) | +0.753 (+2.21) | **0.92×** | 1.53× |

⚠ **Three reasons this is weaker than it looks.** **(a) The background is saturated** — VCAN's EMC samples sit
at the 99.7th and 97.5th array percentiles against comparators at the 97.8th and 91.2nd, so the separation is
small on top of a signal that is high everywhere, and a matrix proteoglycan being abundant in a myxoid tumour
is **expected, which is not the same as discriminating**. **(b) These are largely secreted or matrix-associated
products, not cell-surface addresses** — a versican or biglycan transcript is a statement about what the
tumour deposits, not about what a binder would find on a cell. **(c) Bulk archival tissue cannot deconvolve
compartments**, so a matrix or stromal signal may be reporting the compartment's presence rather than the
tumour cell's, and this analysis has no single-cell or spatial data with which to separate them.

**⭐ The two instruments invert on the three genes where they can be compared**, and that is recorded rather
than resolved ([`emc-expression-panels.json`](../modalities/emc-expression-panels.json) →
`reads.read_8_SURFACE_ANTIGEN.instrument_disagreement_with_the_depmap_surfaceome_scan`): **CD248** is the
surrogate's only selectivity-significant antigen here and is lower in EMC tissue; **ALCAM** was scored and
rejected by the surrogate and is higher in EMC tissue on both arrays; **CD44** is the surrogate's most
strongly negative row here and is higher in EMC tissue on both arrays. **Four explanations are live and
nothing in either artifact discriminates them:** the two ask **different questions** (sarcoma-vs-other-cancer
versus EMC-vs-other-sarcoma — opposite answers are not even inconsistent); they read **different
populations** (the surrogate contains no verified *EWSR1::NR4A3* line, so it holds no EMC observation at all);
they read **different compartments** (monoculture is tumour cells only, bulk tissue adds stroma, vasculature,
immune infiltrate and matrix); and they use **different measurements** (RNA-seq TPM in cultured lines versus
array intensity in archival tissue on two decade-old platforms). ⛔ **This manuscript does not pick a winner.**
What would discriminate them is a single-cell or spatial EMC dataset, which separates the tumour-cell
compartment from the stromal one and so tests the third explanation directly; none is in hand.

### 3.10 GSE4303 is no longer unusable — and the change was to the instrument, not to the data

> ⛔ **Superseded, retained verbatim:** *"### 3.5 The public real-EMC tumour dataset is unusable. The only
> usable, dedicated public EMC tumour transcriptome we could identify, GSE4303, is a seven-platform
> two-colour cDNA-clone microarray (three EMC samples per platform; `matrix_files_found` lists seven GPLs)
> whose values are reference-pool log-ratios and whose probes lack gene symbols; zero shortlist genes
> resolved ([`emc-gse4303-crosscheck.json`]). It cannot rank surface antigens. Combined with §3.1 — which
> after Amendment 1 leaves this analysis with no usable real-EMC observation at all, rather than one line —
> this is precisely why patient-derived EMC model data is the essential input (§7)."*

**One of GSE4303's seven platforms, GPL3290, is now readable**, with 10 EMC and 6 comparator samples. Nothing
about the deposit changed. What changed is the probe-to-symbol bridge: GPL3290's probes carry **EST
accessions only**, and resolving them through a curated dictionary, a UniGene archive and live queries turns
"probes lack gene symbols" into a partial gene index. ⚠ **That bridge is the weak link on this platform** —
a gene can be unreadable there purely because its accession did not resolve, which is exactly why CD248,
CD276, SSTR2, GPC2 and B4GALNT1 carry `READABLE_ON_ONE_PLATFORM_ONLY` and **not** a low reading. The measured
accession-resolution rate is recorded on every run and compared to the previous run's, because a wider bridge
changes **which** genes are readable and a gene readable now and unreadable before is explained by the bridge
rather than by biology.

⭑ **The lesson generalises past this dataset.** "The public data is unusable" was true of the instrument that
existed when it was written and was carried forward as though it were a property of the deposit. It cost this
analysis its entire tumour-tissue axis for a month, and the fix was free.

### 3.11 The negative controls behave, which is what licenses reading any of the above

On the exposure axis, four antigens with no reason to be present in a soft-tissue sarcoma read **lower in EMC
than in normal tissue**: **GPC3** (0.102 vs 1.129 = 0.09×), **MSLN** (0.257 vs 0.941 = 0.27×), **L1CAM**
(0.082 vs 0.245 = 0.33×) and **CDH17** (0.066 vs 0.073 = 0.91×). Together with the NR4A3 / ENO3 / MKI67
controls of §2.6, this is an assay saying the expected thing about antigens whose answer is already known.
⛔ **A working control licenses reading the other rows and nothing more.** It is not evidence for any row.

---

## 4. The modality axis — differently gated, not obviously easier

If a validated EMC surface antigen existed, the modalities it enables gate differently from the oligonucleotide:

| Modality | Intracellular delivery? | Replacing gate | Crossfire note |
|---|---|---|---|
| T-cell engager (antigen × CD3) | No | Cold/excluded TME (poor in adult sarcoma); class-I presentation | — |
| CAR-T / CAR-NK | No | Solid-tumour infiltration; cold TME; fratricide (for NK-cell antigens) | — |
| Radioligand therapy | No | Antigen level; dosimetry; **tumour-to-normal uptake ratio** | β (¹⁷⁷Lu) ~2 mm; α (²²⁵Ac) ~50–80 µm |
| ADC | Internalisation (clinically validated) | Internalisation; tumour-vs-normal contrast | — |

**Correcting a common intuition:** radioligand crossfire mitigates *heterogeneous tumour uptake* (it kills
tumour cells the ligand never bound); it does **not** make a *broadly-expressed normal* antigen safer — for a
normal-tissue antigen, crossfire widens the irradiated field. So B7-H3's breadth is not "rescued" by RLT; the
RLT case rests on tumour-to-normal uptake ratios and dosimetry (the basis of approved SSTR2-RLT).

⭑ **§3.6 adds a modality-specific consequence.** The exposure axis is not equally load-bearing across this
table. An antigen that is elevated versus other sarcomas but **not** versus normal visceral organs — ALCAM's
exact profile — is a usable **diagnostic or lineage marker** and a poor address for any of the four binary-kill
or radiation modalities above, all of which act wherever the antigen is. That distinction is why §3.6 refuses
to give ALCAM a single verdict.

---

## 5. Discussion

**A differently-gated third axis, honestly weighed.** EMC's driver can be attacked from protein (degrader), RNA
(fusion-exclusive ASO) and surface (this work) compartments. The surface axis trades the ASO's
intracellular-delivery gate for others that, in EMC specifically, may be no easier: the abundant **myxoid/
chondroid extracellular matrix** is a diffusion and binding-site barrier to antibodies, adoptive cells and
radioligands, and adult sarcoma has a poor CAR/TCE record in cold, immune-excluded tumours. The honest framing
is *orthogonal and differently-gated*, not "more tractable". ⭑ §3.9 sharpens this: the genes that *are*
concordantly elevated in EMC tissue are largely the matrix itself, so the compartment that most complicates
delivery is also the compartment carrying most of the differential signal.

**No fusion linkage.** Every antigen here is a generic lineage antigen with no mechanistic connection to
EWSR1::NR4A3; success or failure would be independent of the fusion. This is a first-order cost: the surface
axis abandons the program's distinctive fusion-exclusivity. Its justification is pragmatic (delivery), not
mechanistic, and EMC's role is as a clean single-driver *entry* indication for antigens that are pan-sarcoma/
pan-cancer.

**⭐ What this paper is actually for, after the audit.** It is no longer primarily a target list. Its
contribution is **an audited estimate of how far a lineage-surrogate surface ranking transfers to the disease
it was built for**, and in this instance the answer is: **the negatives transferred and the positives did
not.** Stage 1's two headline negatives (B7-H3 not selective; EGFR not selective) both point the same way in
EMC tissue; stage 1's eight positives produce zero concordant confirmations. That asymmetry has a plausible
and testable mechanism — a cross-lineage selectivity test is measuring *"mesenchymal, not epithelial"*, which
is a property EMC shares with every comparator in the tissue cohorts, so it cannot discriminate within them —
and it is a caution that applies to every surrogate-based rare-tumour target list, not only this one.

**What survives as usable output.** Three things. **(a)** A set of **negatives with a named basis**: B7-H3 is
not a differentially-expressed EMC address on either instrument; the stromal panel is lower in EMC than in
comparator sarcomas on both platforms; PRAME reads at the floor of every readable cohort. **(b)** A
**demoted-but-intact marker**: ALCAM separates EMC from other sarcomas on three cohorts and three platform
families, which is a marker-grade result even though the same data removes its case as a therapeutic address.
**(c)** A **held-open lead with a stated defect**: CSPG4, which the original search never evaluated.

**What does not survive.** The implicit promise that a surrogate ranking plus a normal-tissue prior is enough
to prioritise scarce validation effort for a rare tumour. It was not enough here, and the check that showed it
cost nothing and could have been run first.

---

## 6. Limitations

**These are the constraints a reader should apply to every number above. None of them is discharged anywhere in
this manuscript.**

**On the tumour-tissue cohorts (stage 2)**

- **n = 4 EMC in the 3SEQ arm** — the only arm carrying normal tissue. Those are **medians of four libraries**:
  no confidence interval, no test, no distribution. The array arms are n = 6 and n = 10. **Nothing here
  settles anything at the level of a population**, and every "×" in §3.6–§3.9 is a ratio of medians of four
  samples.
- **⛔ 3SEQ 3′-end read density is NOT array intensity and must NEVER be pooled with GPL6244/GPL3290.** The
  arrays' z-scores and percentiles measure a probe's position in that array's own distribution; 3SEQ measures
  reads at a 3′ peak. The two are reported in separate columns throughout for this reason, and a figure that
  combined them would be meaningless.
- **Several genes rest on a single peak** in the 3SEQ deposit — **CSPG4, FAP, GPC3, L1CAM and PRAME** among
  them. One peak has no internal replication; `n_peaks` is carried in the artifact for exactly this reason.
  Several array rows likewise rest on **one probe** (`n_probes_mapping` = 1 for ALCAM, CD248, CD276, SSTR2,
  FAP, PRAME and CSPG4 on GPL6244), and probe-level disagreement is not surfaced where several probes exist —
  they are collapsed by mean.
- **The 27 normals are a tissue panel, not matched adjacent tissue, and six organs are not a body.** Bowel,
  breast, colon, kidney, lung and uterus contain almost no soft tissue, so the normal arm is an
  **on-target/off-tumour exposure** axis and **not** a lineage-specificity axis. A gene high against that
  panel is not thereby EMC-specific rather than mesenchymal.
- **Different comparator arms.** GSE24369's comparators are LGFMS / desmoid fibromatosis / fibrosarcoma;
  GSE4303-GPL3290's are DFSP and GIST (n = 6 total). A gene can move in one cohort and not the other because
  the comparator changed, not because EMC did — §3.8's CSPG4 is the worked example.
- **Two platforms with different physics.** GPL3290 is two-colour log-ratio against a reference pool, so an
  absolute level there means "relative to the pool" and only the between-group contrast is interpretable; an
  `array_percentile` on GPL3290 is a percentile of log-**ratios**, which is not the statement "expressed".
- **⛔ An absent reading is not a reading of absence.** CD248, CD276, SSTR2, GPC2 and B4GALNT1 are unreadable
  on GPL3290; ALPPL2, CTAG1B, MAGEA3, NECTIN4 and SSX2 are unreadable on both. **Nothing in this manuscript
  treats any of those as low, and two curated panels emit no score at all** rather than a score from too few
  genes.
- **No multiple-testing correction, by design** (§2.7). Every *t* and df is reported so a reader can apply
  their own.
- **Bulk archival tissue, not deconvolved.** EMC is matrix-dominated, so tumour-cell content varies and every
  reading is a mixture of tumour cells, CAFs, endothelium, immune infiltrate and matrix. A stromal or
  pericyte antigen can read high because the compartment is present, not because the tumour cell carries it —
  and §3.9's matrix module is precisely where this bites hardest.
- **Sample classification is string matching** on the verbatim GEO annotation. Every annotation is reproduced
  in the artifact so a mis-bucketed sample is auditable without another run.

**On what transcript data cannot say about a surface target**

- **⛔ Transcript, not protein, and nothing about surface localisation.** Every address named here — ALCAM,
  CSPG4, CD248, CD276, SSTR2, FAP, PRAME, GD2 — is a protein or a glycan question. A transcript says nothing
  about whether the protein reaches the plasma membrane, at what **density**, or whether the epitope a binder
  needs is exposed. Transcript-to-protein correlation for membrane proteins is modest and is not measured
  here. **A high transcript reading is a reason to stain. It is not an antigen call.**
- **⛔ No safety statement, no therapeutic window, no efficacy claim, and no statement of clinical readiness
  appears anywhere in this document, because no such quantity is computed anywhere in it or in any artifact
  it cites.** The HPA normal-tissue verdicts of §3.3 are a bulk-RNA **prior**; the 3SEQ normal arm is six
  organs at n = 27 libraries. Neither is a safety assessment, and no agent named here has been given to an
  EMC patient on the basis of anything in this manuscript.
- **Cross-cancer selectivity is not tumour-vs-normal**, and GD2 is assessed only through a synthase proxy
  (§3.7), which is a proxy for a proxy.

**On stage 1, unchanged**

- **⛔ No usable real-EMC observation enters stage 1 at all** — Amendment 1. Stage 1 rests entirely on the
  lineage-generic surrogate class plus normal-tissue priors, and the surrogate contains no verified
  *EWSR1::NR4A3* line.
- **The surrogate is lineage-generic;** surface phenotype tracks lineage, and Ewing/synovial differ from EMC.
- **The scanned gene list was never recorded**, so CSPG4's coverage gap is `UNDECIDABLE` rather than
  resolvable (§2.2b, §3.8), and the same could in principle be true of other genes nobody has thought to
  check.
- **Stage 1 has no stromal compartment**, demonstrated at `frac_expressed` 0.0 for LRRC15, so its verdicts on
  FAP, CD248 and LRRC15 are partly statements about what monoculture can contain.

**On the whole exercise**

- **Two instruments disagree on three of the genes where they can be compared, and this manuscript does not
  resolve the disagreement** (§3.9). Choosing whichever instrument suits a route would not be evidence.
- **Clinical-agent and EMC-biology citations are flagged** [citation to verify] and must be sourced before use.
- **Delivery is not solved by naming an antigen;** modality-specific gates (myxoid-matrix penetration, cold
  TME, dosimetry) remain, and none of them is addressed here.

---

## 7. The validation this needs — a collaboration request

This analysis produces *priors, cautions and negatives*, not a validated target, and after §3.6 the single
decisive dataset is no longer "any EMC expression data". **It is EMC surface *protein* expression with a
normal-tissue comparison, on a cohort large enough to carry a distribution.** Two groups hold patient-derived
EMC models: **USZ-EMC** (Bangerter et al., *Human Cell* 2022/2023) and **NCC-EMC1-C1** (Iwata et al., *Human
Cell* 2025).
⛔ **Those models remain the route to EMC data this analysis cannot obtain from public deposits** —
*(superseded, retained: this sentence read "Those models are now the ONLY route to real EMC data for this
analysis", which was true on 2026-08-05 and is not true after §3.10; and before that it continued "DepMap
additionally holds H-EMC-SS (n = 1)", withdrawn by Amendment 1)*. We propose a genuine collaboration rather
than a data extraction:

- If useful to them, we will **run their existing RNA-seq/expression** through this pipeline and share
  everything; at n ≫ 1 it would test the three cohort readings above on a fourth, independent population.
- A targeted **surface protein panel**, whose questions have changed and are now sharper than the 2026-07-03
  version's: **(1)** is **ALCAM** protein on the EMC cell surface, and at what density relative to normal
  visceral tissue — the axis §3.6 says it fails at transcript level? **(2)** is **CSPG4** protein present, the
  gene the original search never evaluated and the largest absolute row in the 3SEQ deposit? **(3)** is
  **SSTR2** detectable by IHC or ⁶⁸Ga-DOTATATE at all, given §3.7's flat transcript readings — a single scan
  closes or opens the whole radioligand route? **(4)** given §3.6, is there any protein-level reason to keep
  **B7-H3** on the list?
- **A single-cell or spatial EMC dataset would be worth more than any of these individually**, because it is
  the one measurement that discriminates the four explanations in §3.9 by separating the tumour-cell
  compartment from the stromal one.
- Authorship and study design led by the groups whose models make the work possible.

We approach the model-holders directly and privately; this manuscript states the analysis, not a claim on their
data.

---

## 8. Conclusion

A deliberately hard in-silico analysis does not deliver a clean EMC surface target, and when its output is
checked against the disease's own tumour tissue the leads largely do not reproduce: **not one of the eleven
therapeutic addresses this work's routes name is concordantly elevated in EMC relative to comparator
sarcomas, zero of the eight surrogate-selective antigens are concordantly elevated on both arrays, and the
one antigen that is elevated on both — ALCAM, which no route names — shows no separation from normal visceral
organ tissue on the only cohort able to measure that.** What survives is a set of negatives with a named
basis, a demoted-but-intact
lineage marker, one held-open lead (CSPG4) the original search never evaluated, and an audited caution about
surrogate-based target lists for rare tumours. We specify the protein-level measurement that would actually
decide the question and invite the EMC-model groups to resolve it. *(Superseded, retained: this sentence
previously read "rigorous selectivity testing plus a normal-tissue window shows the field-default B7-H3 is not
selective and that the selective candidates carry specific window liabilities, leaving a
favourable-normal-tissue-window GD2 (EMC expression unknown) and a grounded-but-unmeasured-in-EMC
SSTR2/DOTATATE neuroendocrine hypothesis as the questions most worth testing"; and, before Amendment 1, it
began "We report the one available EMC line's profile, specify…".)*

---

## Data & code availability

Code and committed outputs (`research/modalities/`, refreshed to the `modalities-cache` branch):

**Stage 2 — the EMC tumour-tissue audit**
- EMC tumour-tissue panels, all three arrays and every per-gene contrast — `emc_expression_panels.py` →
  [`emc-expression-panels.json`](../modalities/emc-expression-panels.json), specifically
  `reads.read_8_SURFACE_ANTIGEN` (the surface-antigen read, its panel groups, the `cross_platform_board`, the
  CD248 and CSPG4 follow-ups and the recorded instrument disagreement), `reads.control` (NR4A3 / ENO3 /
  MKI67) and `gene_reads` (per-sample values)
- EMC-vs-normal-organ exposure axis — [`gse28866-tumour-vs-normal.json`](../modalities/gse28866-tumour-vs-normal.json)
  → `per_gene.values`; its canonical reading is
  [`gse28866-tumour-vs-normal-reading.md`](./gse28866-tumour-vs-normal-reading.md)
- Measured limits of the stage-1 instrument (L1–L5) — `surfaceome_instrument_limits.py` →
  [`surfaceome-instrument-limits.json`](../modalities/surfaceome-instrument-limits.json)

**Stage 1 — the surrogate search**
- Surfaceome scan + selectivity + the disputed line's profile — `emc_surfaceome_scan.py` →
  `emc-surfaceome-scan.json`
- ⛔ Line-identity readout behind Amendment 1 — `emc_atr_vulnerability.py` → `emc-atr-vulnerability.json`
  → `part_a_hemcss_identity`
- Normal-tissue prior — `emc_surface_normal_window.py` → `emc-surface-normal-window.json`
- EMC-line data probe — `emc_line_data_probe.py` → `emc-line-data-probe.json`
- ⛔ GSE4303 cross-check, superseded by §3.10 — `emc_gse4303_crosscheck.py` → `emc-gse4303-crosscheck.json`
- Red-team log — `emc-surface-target-redteam.md`

Sources: UniProt; DepMap (incl. ACH-001519, identity disputed — Amendment 1); Cellosaurus (CVCL_1238); Human
Protein Atlas; NCBI GEO — **GSE24369** (GPL6244), **GSE4303** (GPL3290), **GSE28866** (3SEQ, supplementary
peak table `GSE28866_36048_normalized_peaks_cancer_and_normal.txt.gz`).

## References

Verified in the repository pool:
- **Sjögren H, et al.** EWSR1/NR4A3 fusion in EMC.
- **Panagopoulos I, et al.** EMC fusion variants/partners.
- **Bangerter, et al.** USZ-EMC patient-derived models. *Human Cell* 2022/2023.
- **Iwata S, et al.** NCC-EMC1-C1. *Human Cell* 2025.
- **Uhlén M, et al.** Human Protein Atlas. *Science* 2015.
- **Bausch-Fluck D, et al.** The in silico human surfaceome. *PNAS* 2018.
- **PMID 26310886** — ENO3 as a direct transactivation target of an NR4A3 fusion through chromatin
  modification of its promoter; the positive control of §2.6.
- **PMID 34413129** — the primary source Cellosaurus cites for the H-EMC-SS fusion caution (Amendment 1).

To verify (candidate anchors identified; confirm before treating as established):
- EMC neuroendocrine differentiation — **INSM1** as a sensitive/relatively specific EMC marker (*Modern
  Pathology* 2017; EMC INSM1 series PMID 36563884) and frequent synaptophysin/NSE positivity; S100 only
  focal — **[verify]**.
- ⛔ **RESOLVED 2026-08-05, unfavourably — H-EMC-SS (ACH-001519):** Cellosaurus `CVCL_1238` records
  *"Caution: Does not harbor a gene fusion involving EWSR1 which is a hallmark of extraskeletal myxoid
  chondrosarcoma (**PubMed=34413129**)"*, and DepMap's filtered fusion caller names no FET gene for the model.
  See Amendment 1. *(Superseded, retained: this entry read "an ECACC-catalogued EMC line; authentication STR /
  EWSR1::NR4A3 status — **[verify via Cellosaurus/DepMap]**." — the verification was done and the label did
  not survive it.)*
- CD56 ADC **lorvotuzumab mertansine (IMGN901)** — SCLC Phase 1/2 (no efficacy benefit, added toxicity;
  PMID 28341109) and CD56⁺ solid-tumour Phase I (PMID 26961907) — **[verify]**.
- SSTR2 / **¹⁷⁷Lu-DOTATATE** (Lutathera; NETTER-1, **Strosberg et al., *NEJM* 2017**) and ²²⁵Ac
  somatostatin-receptor α-analogues — **[verify]**.
- α (²²⁵Ac ~50–80 µm) vs β (¹⁷⁷Lu ~2 mm) tissue ranges — standard radiobiology — **[verify]**.
- CDH11 normal fibroblast/synovial/bone expression (rheumatoid-arthritis/fibrosis target) — **[verify]**.
- CSPG4/MCSP as a melanocytic and pericytic antigen, and its expression in DFSP — the candidate explanation
  of §3.8's platform disagreement — **[verify]**.
- Oncofetal chondroitin sulfate / VAR2CSA carrier proteoglycans (CSPG4, CD44) — **[verify]**; the
  sulfation-machinery panel is sourced (Wu et al., *Front Cell Dev Biol* 2021, PMID 34966741) in
  `surfaceome-instrument-limits.json`.
- Clinical-stage agents per antigen (GPC2, PTK7, B7-H3 ifinatamab deruxtecan, ALCAM, CSPG4) — **[verify]** per
  antigen.
- EMC incidence (<1% of soft-tissue sarcoma) — **[verify]**.
- GEO accessions and sample annotations for **GSE24369**, **GSE4303** and **GSE28866** — reproduced verbatim in
  `emc-expression-panels.json` → `platforms.<file>.sample_annotations_verbatim` and
  `gse28866-tumour-vs-normal.json` → `sources`; the originating publications are **[verify]**.

---
*Provenance: consolidates the stage-1 surfaceome scan (BH-corrected selectivity + the ACH-001519 profile, whose
EMC label is withdrawn by Amendment 1), the normal-tissue prior (controls behaved as specified), the EMC-line
data probe, the GSE4303 cross-check (superseded by §3.10), the stage-2 EMC tumour-tissue read across three
cohorts and three platform families, the measured limits of the stage-1 instrument, two red-team passes
([`emc-surface-target-redteam.md`]) and the 2026-08-05 line-identity readout
([`../modalities/emc-atr-vulnerability.json`](../modalities/emc-atr-vulnerability.json) →
`part_a_hemcss_identity`). All committed CPU/CI outputs; no GPU compute and no wet-lab work. No antigen is
asserted as an EMC-validated target, and no claim of safety, selectivity, efficacy or clinical readiness is
made anywhere.*
