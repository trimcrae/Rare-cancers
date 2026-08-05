---
id: DOC-EMC-SURFACE-TARGET-LANDSCAPE
title: In-silico surface-antigen prioritisation for extraskeletal myxoid chondrosarcoma: one cell line, a translocation-sarcoma
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `manuscript` from its location under research/manuscripts/.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# In-silico surface-antigen prioritisation for extraskeletal myxoid chondrosarcoma: a translocation-sarcoma surrogate, a hard normal-tissue filter — and a validation request

> **Preprint status (2026-07-03; ⛔ materially amended 2026-08-05 — read
> [Amendment 1](#amendment-1-2026-08-05---the-cell-line-this-manuscript-called-the-one-real-emc-line-is-recorded-as-not-carrying-the-fusion)
> first).** Computational, **hypothesis-generating** manuscript, extensively
> self-red-teamed (see [`emc-surface-target-redteam.md`](./emc-surface-target-redteam.md)). It reports what an
> honest in-silico surface-antigen analysis for EMC can and cannot establish from public data. The central,
> deliberately un-triumphant finding is that **a rigorous selectivity test plus a hard normal-tissue-window
> filter leaves essentially no classic protein surface antigen that is both tumour-selective and
> normal-tissue-restricted** — the analysis mainly *refines priorities and flags liabilities* (notably that
> the field-default B7-H3 is not selective in the data), and
> nominates a neuroendocrine-differentiation hypothesis (SSTR2 / GD2) the field has not pursued for EMC. No
> antigen is asserted as an EMC-validated target. The manuscript's second purpose is a specific, respectful
> request to the groups holding patient-derived EMC models for the data that would actually resolve it (§7).
> ⚠ **Superseded by Amendment 1, retained verbatim because it was a headline of the 2026-07-03 version and
> stays quotable:** this banner also read *"surfaces one real EMC cell line's own profile"*, and the title
> began *"…for extraskeletal myxoid chondrosarcoma: **one cell line**, a translocation-sarcoma surrogate…"*.

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
| §3.4's **SSTR2 / GD2 neuroendocrine hypothesis** | ✅ **SURVIVES.** Its stated basis is EMC's **reported IHC** neuroendocrine differentiation (INSM1, synaptophysin — §1, still `[verify]`-flagged), never this line. It loses the §3.1 corroboration above and nothing else. **It was already labelled a hypothesis requiring direct EMC measurement, and still is** |
| §3.2 **selectivity** (incl. the headline *B7-H3 is not selective, BH q = 1.0*) | ✅ **SURVIVES, RE-LABELLED.** The line is **1 of 45** class members carrying expression data, and the class must now be described as translocation-sarcoma **plus one line of disputed identity**. Quantified rather than asserted: recomputing every actionable antigen's `enrichment_vs_rest` with the line dropped moves it by **≤ 0.13 log2TPM** (largest: GPC3 0.93→0.81; CD276 0.14→0.15; CDH11 3.18→3.29), with **no sign flips**. ⚠ Honest limit: the rank-based Mann–Whitney *p* cannot be recomputed from the committed artifact, which stores summary statistics rather than per-line values, so the *q*-values are **not** re-derived here — the effect-size bound is |
| §3.3 **normal-tissue window** | ✅ **UNAFFECTED.** Built entirely from Human Protein Atlas normal tissue; no cell line enters it |
| §3.5 (the public EMC dataset is unusable) and §7 (the collaboration request) | ✅ **STRENGTHENED, not weakened.** Both argue that patient-derived EMC model data is the essential missing input. Removing the one apparent counter-example makes that argument stronger, and §7's ask is unchanged |

### ⭑ The general lesson, which is worth more than the specific correction

The `[to verify]` flag on this line was written honestly and carried faithfully in four places for a month.
**Carrying a flag is not resolving one.** What resolved it was one free API call that could have been made on
day one. The inventory of every repository file that leaned on this line is in
[`emc-atr-vulnerability-assessment.md` §2.3](./emc-atr-vulnerability-assessment.md); each of those files now
carries its own dated amendment, and the line's status is registered as an object
(`OBJ-LINE-HEMCSS`) in [`emc-systems-map.json`](./emc-systems-map.json) so a future claim that reads EMC
biology off it fails a checker rather than a reader.

---

**Keywords:** extraskeletal myxoid chondrosarcoma; EWSR1::NR4A3; surfaceome; therapeutic window; antibody–drug
conjugate; CAR-T; radioligand therapy; SSTR2; neuroendocrine differentiation.

---

## Abstract

**Background.** Extraskeletal myxoid chondrosarcoma (EMC) is a rare translocation sarcoma driven by the
*EWSR1::NR4A3* fusion, a nuclear transcription factor. Driver-directed routes (an NR4A3 degrader; a
fusion-junction antisense oligonucleotide) confront an intracellular-delivery or druggability gate.
Cell-surface antigens offer an orthogonal axis (ADC, CAR/NK, T-cell engager, radioligand therapy) whose
gating differs — but at the cost of the fusion-level selectivity the oligonucleotide uniquely offers.

**Methods.** We built a public-data pipeline: a largely-unbiased human surfaceome (UniProt plasma-membrane +
transmembrane/GPI, unioned with a small actionable-antigen seed) ranked by expression and by a rank-based
selectivity test
(Mann–Whitney, Benjamini–Hochberg) across a translocation-sarcoma DepMap class (n = 76), which also contains
the single line DepMap annotates *Extraskeletal Myxoid Chondrosarcoma* (H-EMC-SS / ACH-001519) — ⛔ **a line
whose fusion status the curated record contradicts, so it is NOT read here as EMC evidence; see
[Amendment 1](#amendment-1-2026-08-05---the-cell-line-this-manuscript-called-the-one-real-emc-line-is-recorded-as-not-carrying-the-fusion).**
*(Superseded, retained: this sentence read "— contrary to the common assumption — **also contains one genuine
EMC line (H-EMC-SS / ACH-001519)** whose surface transcriptome we report directly (n = 1, descriptive)".)*
We then applied a hard **normal-tissue therapeutic-window filter** (Human Protein Atlas tissue *and* blood-cell specificity, with vital-tissue/immune overrides;
controls validated). Positive/negative/hard controls check each classifier branch.

**Results.** Selectivity (versus other cancer lineages) is significant for CDH11, KIT, FGFR1, NCAM1, GPC2,
PTK7, MCAM and EPHB4, and — importantly — **not** for B7-H3/CD276 (BH q = 1.0), EGFR or FAP. The normal-tissue
filter is decisive and sobering: of the classic candidates, **none is both selective and normal-tissue-
restricted.** They partition into selective-but-broadly-expressed (CDH11, GPC2, FGFR1, MCAM, EPHB4),
selective-but-immune/vital-liability (NCAM1/CD56 — on NK cells; PTK7; KIT), and non-selective (B7-H3, EGFR,
FAP); only GD2 (assayed via its synthase B4GALNT1, an imperfect proxy) shows a restricted *normal-tissue*
window (its EMC expression is unmeasured). EMC's reported neuroendocrine differentiation (IHC: INSM1,
synaptophysin — pending citation) motivates two hypotheses the field has not tested for EMC: **SSTR2** (target
of the approved radioligand ¹⁷⁷Lu-DOTATATE) and **GD2** — both requiring direct EMC measurement.

**Conclusion.** Done rigorously, in-silico surface-target discovery for EMC does not hand over a clean target;
its value is to de-risk over-optimistic assumptions (especially B7-H3), to expose antigen-specific liabilities,
and to nominate the neuroendocrine SSTR2/GD2 route. *(Superseded, retained: this sentence also credited the
work with "to surface the one available EMC line's profile" — withdrawn by Amendment 1.)* The
decisive validation — EMC surface *protein* expression with a normal-tissue window — requires the
patient-derived EMC lines, and we invite their holders to co-resolve it.

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

**The gap.** EMC surface-antigen expression has not been systematically mapped, and EMC has been assumed absent
from public cell-line panels. We provide the first in-silico surface-antigen analysis for EMC, with a
deliberately hard normal-tissue filter and honest statistics, to prioritise scarce validation and to specify
what that validation is.

---

## 2. Methods

All analyses are computational, use public data, run in CI, and commit their outputs (Data & code). No wet-lab
work was done. Provenance and per-stage controls are recorded in each output JSON.

**2.1 Surfaceome.** UniProt-reviewed human proteins with a plasma-membrane location (SL-0039) plus a
transmembrane (KW-0812) or GPI-anchor (KW-0336) topology, unioned with a curated seed of actionable surface
antigens (so established targets are always evaluated). The committed run used **2,820 genes from UniProt ∪ 47
curated seed antigens** (41 of the seed already in the UniProt set) = **2,826 unique**, of which **2,692** are
present in the DepMap expression matrix and were scanned — so the seed is a small, mostly-redundant minority
and the set is largely, though **not strictly, unbiased**; the UniProt fetch status and counts are recorded in
the output. [`emc_surfaceome_scan.py`]

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
descriptor), **not** a tumour-vs-normal window, and that it mechanically favours mesenchymal antigens because
the DepMap panel is epithelial-dominated. Self-check: housekeeping genes are excluded by construction (a
minimal sanity check, not validation); CD276 recovers as broadly expressed. [`emc_surfaceome_scan.py`]

**2.3 Normal-tissue therapeutic-window filter (the primary axis).** For each antigen we queried the Human
Protein Atlas for RNA tissue specificity, tissue distribution, per-tissue nTPM, **blood-cell specificity**, and
subcellular location, and classified a window verdict with correct HPA semantics: only *tissue enriched* /
*group enriched* with a *restricted distribution* and no vital-tissue and no strong immune/circulating signal
is **RESTRICTED**; *tissue enhanced* (detected broadly with a peak) is **ENHANCED_BROAD**, not restricted;
*low tissue specificity* **or a "detected in all" distribution** is **BROAD_LIABILITY** (the distribution
override demotes e.g. MCAM, which is "group enriched" but detected in all tissues); and expression in a vital
tissue, or a *confined* blood signal (*immune-cell enriched* / *group enriched* — not weak *immune-cell
enhanced*), overrides all as **VITAL_OR_IMMUNE_LIABILITY**. Controls: DLL3/GPC3 (tumour-restricted) must be RESTRICTED, B2M BROAD,
and a **hard control CD3E** (an immune antigen) must NOT be RESTRICTED — all satisfied. HPA RNA is bulk normal
tissue and a window *prior*, not a safety guarantee, and mRNA ≠ surface protein. [`emc_surface_normal_window.py`]

**2.4 Real-EMC public data (attempted).** We attempted the only usable dedicated public EMC tumour
transcriptome we could identify (GSE4303) and
report why it is unusable. [`emc_gse4303_crosscheck.py`, `emc_line_data_probe.py`]

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
§3.4's hypothesis rests on EMC's **reported IHC** phenotype and must be read from there alone. **The analysis
is anchored in nothing except a lineage-generic surrogate class**, which is what §7 asks the model-holding
groups to fix.

### 3.2 Selectivity across the translocation-sarcoma class — and B7-H3 is not selective

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
treating B7-H3 as the obvious first choice.

### 3.3 The normal-tissue window is decisive — and leaves no clean classic antigen

Applying the hard window filter (controls validated: DLL3/GPC3 → RESTRICTED, B2M → BROAD, CD3E →
VITAL_OR_IMMUNE_LIABILITY; [`emc-surface-normal-window.json`]):

| Antigen | HPA tissue specificity | Blood-cell signal | Window verdict |
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
(**Figure 1**: antigens plotted by selectivity × window tier; the selective-and-restricted quadrant is
unpopulated — [`emc-surface-prioritization.png`]). The candidates fail the window in specific, nameable ways:
- **NCAM1/CD56** is on NK cells (fratricide risk for CAR/NK; a circulating compartment) and neural tissue; the
  CD56 ADC **lorvotuzumab mertansine (IMGN901)** was clinically developed and discontinued (no efficacy benefit,
  added toxicity) [Socinski/Spira — citations to verify]. It is not a clean target despite its selectivity.
- **CDH11** is broadly expressed in normal fibroblasts, synovium and bone (an established rheumatoid-arthritis/
  fibrosis target); its high cross-cancer enrichment is the mesenchymal-vs-epithelial artifact above. Pairing it
  with binary-kill modalities (CAR/TCE) would attack normal mesenchyme body-wide.
- **B7-H3, EGFR, FAP** are non-selective and/or broad; **FGFR1/MCAM/EPHB4** are window-liabilities.
- **GD2** (via the B4GALNT1 proxy — GD2 is a glycolipid, not a gene product, so this is indirect) has the only
  restricted *normal-tissue* window here, consistent with GD2's known tumour-restricted profile — but **whether
  EMC expresses GD2 is unmeasured**, so this is a favourable window, not evidence of an EMC target.

### 3.4 A neuroendocrine hypothesis the field has not tested for EMC: SSTR2 and GD2

EMC's neuroendocrine differentiation (INSM1+, synaptophysin+; §1 — **reported IHC, still `[verify]`-flagged;
this is the hypothesis's ONLY basis**) motivates two candidate targets absent from prior EMC surface
discussions. ⚠ **Amendment 1 withdraws the §3.1 corroboration this section previously drew from the DepMap
line's neural surface transcripts; the hypothesis itself is unchanged and was always labelled as needing
direct EMC measurement.**
- **SSTR2 (somatostatin receptor 2)** — the target of the *approved* radioligand **¹⁷⁷Lu-DOTATATE**
  (Lutathera; approved for gastroenteropancreatic neuroendocrine tumours on the NETTER-1 trial [Strosberg et
  al., *N Engl J Med* 2017 — verify]) and its ²²⁵Ac α-analogues. If EMC's neuroendocrine phenotype
  extends to SSTR2 surface expression, an off-the-shelf theranostic (SSTR-PET + peptide-receptor radioligand
  therapy) becomes testable without a bespoke agent. The first gate is whether EMC expresses SSTR2 at all
  (unmeasured); *if* it does, then — its window being ENHANCED_BROAD (SSTR2 is expressed in normal
  neuroendocrine/GI tissue) — dosimetry, not novelty, is the remaining gate, as for approved NET-RLT.
- **GD2** — a surface glycolipid with mature CAR/antibody platforms and (via B4GALNT1) the only restricted-window
  signal in §3.3.

These are hypotheses requiring direct EMC measurement (SSTR2 IHC/PET; GD2 immunostaining), not claims.

### 3.5 The public real-EMC tumour dataset is unusable

The only usable, dedicated public EMC tumour transcriptome we could identify, GSE4303, is a seven-platform
two-colour cDNA-clone microarray (three EMC samples per platform; `matrix_files_found` lists seven GPLs) whose
values are reference-pool log-ratios and
whose probes lack gene symbols; zero shortlist genes resolved ([`emc-gse4303-crosscheck.json`]). It cannot rank
surface antigens. **Combined with §3.1 — which after Amendment 1 leaves this analysis with *no* usable real-EMC
observation at all, rather than one line — this is precisely why patient-derived EMC model data is the
essential input (§7).** *(Superseded, retained: this sentence read "Combined with §3.1 (a single EMC line in
DepMap), this is precisely why…".)*

---

## 4. The modality axis — differently gated, not obviously easier

If a validated EMC surface antigen existed, the modalities it enables gate differently from the oligonucleotide:

| Modality | Intracellular delivery? | Replacing gate | Crossfire note |
|---|---|---|---|
| T-cell engager (antigen × CD3) | No | Cold/excluded TME (poor in adult sarcoma) | — |
| CAR-T / CAR-NK | No | Solid-tumour infiltration; cold TME; fratricide (for NK-cell antigens) | — |
| Radioligand therapy | No | Antigen level; dosimetry; **tumour-to-normal uptake ratio** | β (¹⁷⁷Lu) ~2 mm; α (²²⁵Ac) ~50–80 µm |
| ADC | Internalisation (clinically validated) | Internalisation; tumour-vs-normal window | — |

**Correcting a common intuition:** radioligand crossfire mitigates *heterogeneous tumour uptake* (it kills
tumour cells the ligand never bound); it does **not** make a *broadly-expressed normal* antigen safer — for a
normal-tissue antigen, crossfire widens the irradiated field. So B7-H3's breadth is not "rescued" by RLT; the
RLT case rests on tumour-to-normal uptake ratios and dosimetry (the basis of approved SSTR2-RLT).

---

## 5. Discussion

**A differently-gated third axis, honestly weighed.** EMC's driver can be attacked from protein (degrader), RNA
(fusion-exclusive ASO) and surface (this work) compartments. The surface axis trades the ASO's
intracellular-delivery gate for others that, in EMC specifically, may be no easier: the abundant **myxoid/
chondroid extracellular matrix** is a diffusion and binding-site barrier to antibodies, adoptive cells and
radioligands, and adult sarcoma has a poor CAR/TCE record in cold, immune-excluded tumours. The honest framing
is *orthogonal and differently-gated*, not "more tractable".

**No fusion linkage.** Every antigen here is a generic lineage antigen with no mechanistic connection to
EWSR1::NR4A3; success or failure would be independent of the fusion. This is a first-order cost: the surface
axis abandons the program's distinctive fusion-exclusivity. Its justification is pragmatic (delivery), not
mechanistic, and EMC's role is as a clean single-driver *entry* indication for antigens that are pan-sarcoma/
pan-cancer.

**What the analysis is good for.** Negative and prioritising results: B7-H3 is not transcriptionally selective;
CD56/CDH11/PTK7/KIT carry specific window liabilities; the neuroendocrine phenotype points to SSTR2/GD2. These
sharpen where scarce wet-lab effort should and should not go.

---

## 6. Limitations

- **⛔ NO real-EMC observation at all.** *(Superseded, retained: this limitation read "**One EMC line, n = 1**
  (H-EMC-SS); no statistics from it, and its authentication/fusion status is unverified.")* The `[to verify]`
  was answered on 2026-08-05 against the line — Amendment 1 — so the analysis rests entirely on the
  lineage-generic surrogate class plus normal-tissue priors. **This is the single largest limitation and it is
  larger than the 2026-07-03 version stated.**
- **Surrogate is lineage-generic;** surface phenotype tracks lineage, and Ewing/synovial differ from EMC.
- **mRNA ≠ surface protein;** target density, epitope accessibility and internalisation — what modalities need —
  are not measured. Rankings are coarse tiers.
- **Cross-cancer selectivity ≠ tumour-vs-normal;** the normal-tissue window (HPA bulk RNA) is a prior, not a
  safety guarantee, and GD2 is assessed only via a synthase proxy.
- **The public EMC dataset is unusable** (§3.5); the surrogate cannot be corroborated against real EMC tumours.
- **Clinical-agent and EMC-biology citations are flagged** [citation to verify] and must be sourced before use.
- **Delivery is not solved by naming an antigen;** modality-specific gates (myxoid-matrix penetration, cold TME,
  dosimetry) remain.

---

## 7. The validation this needs — a collaboration request

This analysis produces *priors and cautions*, not a validated target, and the single decisive dataset is EMC
surface **protein** expression with a normal-tissue comparison. Two groups hold patient-derived EMC models:
**USZ-EMC** (Bangerter et al., *Human Cell* 2022/2023) and **NCC-EMC1-C1** (Iwata et al., *Human Cell* 2025).
⛔ **Those models are now the ONLY route to real EMC data for this analysis** — *(superseded, retained: this
sentence continued "DepMap additionally holds H-EMC-SS (n = 1)", withdrawn by Amendment 1)*. We propose a
genuine collaboration rather than a data extraction:

- If useful to them, we will **run their existing RNA-seq/expression** through this pipeline and share
  everything; at n ≫ 1 it validates or refutes the selectivity and window priors on real EMC.
- A targeted **surface panel** — prioritising the questions this analysis raises: is **SSTR2** expressed
  (→ off-the-shelf DOTATATE theranostic)? is **GD2** present? and, given the window liabilities, are the
  selective-but-broad antigens (GPC2, CDH11) actually surface-restricted at the protein level in EMC?
- Authorship and study design led by the groups whose models make the work possible.

We approach the model-holders directly and privately; this manuscript states the analysis, not a claim on their
data.

---

## 8. Conclusion

A deliberately hard in-silico analysis does not deliver a clean EMC surface target: rigorous selectivity
testing plus a normal-tissue window shows the field-default B7-H3 is not selective and that the selective
candidates carry specific window liabilities, leaving a favourable-normal-tissue-window GD2 (EMC expression
unknown) and a grounded-but-unmeasured-in-EMC SSTR2/DOTATATE neuroendocrine hypothesis as the questions most
worth testing. We specify the protein-level validation that matters and invite the EMC-model groups to resolve
it. *(Superseded, retained: this sentence began "We report the one available EMC line's profile, specify…" —
withdrawn by Amendment 1.)*

---

## Data & code availability

Code and committed outputs (`research/modalities/`, refreshed to the `modalities-cache` branch):
- Surfaceome scan + selectivity + the disputed line's profile — `emc_surfaceome_scan.py` →
  `emc-surfaceome-scan.json`
- ⛔ Line-identity readout behind Amendment 1 — `emc_atr_vulnerability.py` → `emc-atr-vulnerability.json`
  → `part_a_hemcss_identity`
- Normal-tissue window — `emc_surface_normal_window.py` → `emc-surface-normal-window.json`
- EMC-line data probe — `emc_line_data_probe.py` → `emc-line-data-probe.json`
- GSE4303 cross-check — `emc_gse4303_crosscheck.py` → `emc-gse4303-crosscheck.json`
- Red-team log — `emc-surface-target-redteam.md`

Sources: UniProt; DepMap (incl. ACH-001519, identity disputed — Amendment 1); Cellosaurus (CVCL_1238); Human
Protein Atlas; NCBI GEO (GSE4303).

## References

Verified in the repository pool:
- **Sjögren H, et al.** EWSR1/NR4A3 fusion in EMC.
- **Panagopoulos I, et al.** EMC fusion variants/partners.
- **Bangerter, et al.** USZ-EMC patient-derived models. *Human Cell* 2022/2023.
- **Iwata S, et al.** NCC-EMC1-C1. *Human Cell* 2025.
- **Uhlén M, et al.** Human Protein Atlas. *Science* 2015.
- **Bausch-Fluck D, et al.** The in silico human surfaceome. *PNAS* 2018.

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
- Clinical-stage agents per antigen (GPC2, PTK7, B7-H3 ifinatamab deruxtecan, etc.) — **[verify]** per antigen.
- EMC incidence (<1% of soft-tissue sarcoma) — **[verify]**.

---
*Provenance: consolidates the surfaceome scan (BH-corrected selectivity + the ACH-001519 profile, whose EMC
label is withdrawn by Amendment 1), the normal-tissue window (controls validated), the EMC-line data probe and
the GSE4303 cross-check (committed CPU outputs on `modalities-cache`), two red-team passes
([`emc-surface-target-redteam.md`]) and the 2026-08-05 line-identity readout
([`../modalities/emc-atr-vulnerability.json`](../modalities/emc-atr-vulnerability.json) →
`part_a_hemcss_identity`). No antigen is asserted as an EMC-validated target.*
