# In-silico surface-antigen prioritisation for extraskeletal myxoid chondrosarcoma: one cell line, a translocation-sarcoma surrogate, a hard normal-tissue filter — and a validation request

> **Preprint status (2026-07-03).** Computational, **hypothesis-generating** manuscript, extensively
> self-red-teamed (see [`emc-surface-target-redteam.md`](./emc-surface-target-redteam.md)). It reports what an
> honest in-silico surface-antigen analysis for EMC can and cannot establish from public data. The central,
> deliberately un-triumphant finding is that **a rigorous selectivity test plus a hard normal-tissue-window
> filter leaves essentially no classic protein surface antigen that is both tumour-selective and
> normal-tissue-restricted** — the analysis mainly *refines priorities and flags liabilities* (notably that
> the field-default B7-H3 is not selective in the data), surfaces one real EMC cell line's own profile, and
> nominates a neuroendocrine-differentiation hypothesis (SSTR2 / GD2) the field has not pursued for EMC. No
> antigen is asserted as an EMC-validated target. The manuscript's second purpose is a specific, respectful
> request to the groups holding patient-derived EMC models for the data that would actually resolve it (§7).

**Keywords:** extraskeletal myxoid chondrosarcoma; EWSR1::NR4A3; surfaceome; therapeutic window; antibody–drug
conjugate; CAR-T; radioligand therapy; SSTR2; neuroendocrine differentiation.

---

## Abstract

**Background.** Extraskeletal myxoid chondrosarcoma (EMC) is a rare translocation sarcoma driven by the
*EWSR1::NR4A3* fusion, a nuclear transcription factor. Driver-directed routes (an NR4A3 degrader; a
fusion-junction antisense oligonucleotide) confront an intracellular-delivery or druggability gate.
Cell-surface antigens offer an orthogonal axis (ADC, CAR/NK, T-cell engager, radioligand therapy) whose
gating differs — but at the cost of the fusion-level selectivity the oligonucleotide uniquely offers.

**Methods.** We built a public-data pipeline: an unbiased human surfaceome (UniProt plasma-membrane +
transmembrane/GPI, seeded with actionable antigens) ranked by expression and by a rank-based selectivity test
(Mann–Whitney, Benjamini–Hochberg) across a translocation-sarcoma DepMap class (n = 76), which — contrary to
the common assumption — **also contains one genuine EMC line (H-EMC-SS / ACH-001519)** whose surface
transcriptome we report directly (n = 1, descriptive). We then applied a hard **normal-tissue therapeutic-window
filter** (Human Protein Atlas tissue *and* blood-cell specificity, with vital-tissue/immune overrides;
controls validated). Positive/negative/hard controls check each classifier branch.

**Results.** Selectivity (versus other cancer lineages) is significant for CDH11, KIT, FGFR1, NCAM1, GPC2,
PTK7, MCAM and EPHB4, and — importantly — **not** for B7-H3/CD276 (p = 0.98), EGFR or FAP. The normal-tissue
filter is decisive and sobering: of the classic candidates, **none is both selective and normal-tissue-
restricted.** They partition into selective-but-broadly-expressed (CDH11, GPC2, FGFR1, MCAM, EPHB4),
selective-but-immune/vital-liability (NCAM1/CD56 — on NK cells; PTK7; KIT), and non-selective (B7-H3, EGFR,
FAP); only GD2 (assayed via its synthase B4GALNT1, an imperfect proxy) shows a restricted window. EMC's
documented neuroendocrine differentiation (INSM1, synaptophysin) motivates two hypotheses the field has not
tested for EMC: **SSTR2** (target of the approved radioligand ¹⁷⁷Lu-DOTATATE) and **GD2**.

**Conclusion.** Done rigorously, in-silico surface-target discovery for EMC does not hand over a clean target;
its value is to de-risk over-optimistic assumptions (especially B7-H3), to expose antigen-specific liabilities,
to surface the one available EMC line's profile, and to nominate the neuroendocrine SSTR2/GD2 route. The
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
antigens (so established targets are always evaluated). The committed run drew **2,820 genes from UniProt**
plus **47 seed** antigens (2,826 total; 2,692 present in the DepMap expression matrix and scanned) — so the
seed is a small minority and the set is largely, though **not strictly, unbiased**; the UniProt fetch status
and counts are recorded in the output. [`emc_surfaceome_scan.py`]

**2.2 Expression, selectivity, and the one EMC line.** DepMap OmicsExpression (log2(TPM+1)). We defined a
translocation-sarcoma class by OncotreeSubtype (Ewing/synovial/alveolar/DSRCT/clear-cell + the EMC line;
n = 76) as a lineage-generic surrogate, and — a correction to the field's assumption — identified a **single
genuine EMC line, ACH-001519 (H-EMC-SS), OncotreeSubtype "Extraskeletal Myxoid Chondrosarcoma"**, whose own
top surface antigens we report (n = 1, descriptive; H-EMC-SS authentication and EWSR1::NR4A3 status flagged
[to verify]). For each surface gene we report expression, an effect size (enrichment versus non-sarcoma
lineages), and a **rank-based one-sided Mann–Whitney p that the class exceeds the rest, Benjamini–Hochberg
corrected**. We are explicit that this is cross-*cancer* selectivity (a distinguishable-from-epithelial-tumours
descriptor), **not** a tumour-vs-normal window, and that it mechanically favours mesenchymal antigens because
the DepMap panel is epithelial-dominated. Self-check: housekeeping genes are excluded by construction (a
minimal sanity check, not validation); CD276 recovers as broadly expressed. [`emc_surfaceome_scan.py`]

**2.3 Normal-tissue therapeutic-window filter (the primary axis).** For each antigen we queried the Human
Protein Atlas for RNA tissue specificity, tissue distribution, per-tissue nTPM, **blood-cell specificity**, and
subcellular location, and classified a window verdict with correct HPA semantics: only *tissue enriched* /
*group enriched* with no vital-tissue and no strong immune/circulating signal is **RESTRICTED**; *tissue
enhanced* (detected broadly with a peak) is **ENHANCED_BROAD**, not restricted; *low tissue specificity* is
**BROAD_LIABILITY**; and expression in a vital tissue or a confined immune/circulating compartment overrides
all as **VITAL_OR_IMMUNE_LIABILITY**. Controls: DLL3/GPC3 (tumour-restricted) must be RESTRICTED, B2M BROAD,
and a **hard control CD3E** (an immune antigen) must NOT be RESTRICTED — all satisfied. HPA RNA is bulk normal
tissue and a window *prior*, not a safety guarantee, and mRNA ≠ surface protein. [`emc_surface_normal_window.py`]

**2.4 Real-EMC public data (attempted).** We attempted the only public EMC tumour transcriptome (GSE4303) and
report why it is unusable. [`emc_gse4303_crosscheck.py`, `emc_line_data_probe.py`]

---

## 3. Results

### 3.1 The one EMC line in public data — H-EMC-SS

Contrary to the assumption that EMC is absent from public cell-line panels, DepMap contains one line annotated
Extraskeletal Myxoid Chondrosarcoma — **ACH-001519 / H-EMC-SS**. Its own top surface-antigen transcripts are
the most EMC-specific in-silico signal available (n = 1, descriptive; no statistics; authentication/fusion
status [to verify]):

**Table 1. H-EMC-SS (ACH-001519) top surface-antigen transcripts** (log2(TPM+1); single sample, descriptive;
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

Two honest readings. First, the list is **dominated by ubiquitous membrane proteins** (APP, the tetraspanins
CD63/CD81, BSG/CD147, ITGB1, CD59, LAMP1) — raw single-line expression surfaces housekeeping surface proteins,
which is precisely why the selectivity and normal-tissue filters below are necessary and why "highly expressed"
is not "targetable". Second, and more interestingly, **FGFR1 ranks third** and several **neural-associated
surface proteins (DNER, RTN4/Nogo, PMP22, APP)** appear — consistent with EMC's neuroendocrine/neural
differentiation (§1) and supportive of the SSTR2/GD2 hypothesis (§3.4). This single line cannot carry
statistical weight, but it anchors the analysis in real EMC and is exactly the data that, at n ≫ 1, would
resolve the questions below.

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
| EPHB4 | +1.0 | 3e-4 | yes |
| MCAM/CD146 | +1.09 | 3e-3 | yes |
| **B7-H3/CD276** | **+0.14** | **1.0** | **NO** |
| FAP | +0.02 | 0.16 | no |
| EGFR | −2.21 | 1.0 | no |

Two cautions, stated up front. First, this is **cross-cancer** selectivity, which the epithelial-dominated
DepMap panel biases toward mesenchymal antigens (CDH11's +3.18 is largely "not expressed by carcinomas", not
"tumour-specific"). Second, mRNA magnitude to two decimals conveys false precision about surface-protein
density; read these as **coarse tiers**. The one decision-grade result here is negative and useful: **B7-H3,
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

The intersection of §3.2 (selective) and §3.3 (restricted) among classic protein antigens is **empty**. The
candidates fail the window in specific, nameable ways:
- **NCAM1/CD56** is on NK cells (fratricide risk for CAR/NK; a circulating compartment) and neural tissue; the
  CD56 ADC **lorvotuzumab mertansine (IMGN901)** was clinically developed and discontinued (no efficacy benefit,
  added toxicity) [Socinski/Spira — citations to verify]. It is not a clean target despite its selectivity.
- **CDH11** is broadly expressed in normal fibroblasts, synovium and bone (an established rheumatoid-arthritis/
  fibrosis target); its high cross-cancer enrichment is the mesenchymal-vs-epithelial artifact above. Pairing it
  with binary-kill modalities (CAR/TCE) would attack normal mesenchyme body-wide.
- **B7-H3, EGFR, FAP** are non-selective and/or broad; **FGFR1/MCAM/EPHB4** are window-liabilities.
- **GD2** (via the B4GALNT1 proxy — GD2 is a glycolipid, not a gene product, so this is indirect) is the only
  restricted-window signal, consistent with GD2's known tumour-restricted profile.

### 3.4 A neuroendocrine hypothesis the field has not tested for EMC: SSTR2 and GD2

EMC's neuroendocrine differentiation (INSM1+, synaptophysin+; §1) motivates two candidate targets absent from
prior EMC surface discussions:
- **SSTR2 (somatostatin receptor 2)** — the target of the *approved* radioligand **¹⁷⁷Lu-DOTATATE** and its
  ²²⁵Ac α-analogues [Strosberg; Frontiers 2022 — citations to verify]. If EMC's neuroendocrine phenotype
  extends to SSTR2 surface expression, an off-the-shelf theranostic (SSTR-PET + peptide-receptor radioligand
  therapy) becomes testable without a bespoke agent. Its window here is ENHANCED_BROAD (SSTR2 is expressed in
  normal neuroendocrine/GI tissue), so dosimetry, not novelty, is the gate — exactly as for approved NET-RLT.
- **GD2** — a surface glycolipid with mature CAR/antibody platforms and (via B4GALNT1) the only restricted-window
  signal in §3.3.

These are hypotheses requiring direct EMC measurement (SSTR2 IHC/PET; GD2 immunostaining), not claims.

### 3.5 The public real-EMC tumour dataset is unusable

The only public EMC tumour transcriptome, GSE4303, is a seven-platform two-colour cDNA-clone microarray (three
EMC samples per platform; `matrix_files_found` lists seven GPLs) whose values are reference-pool log-ratios and
whose probes lack gene symbols; zero shortlist genes resolved ([`emc-gse4303-crosscheck.json`]). It cannot rank
surface antigens. Combined with §3.1 (a single EMC line in DepMap), this is precisely why patient-derived EMC
model data is the essential input (§7).

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

- **One EMC line, n = 1** (H-EMC-SS); no statistics from it, and its authentication/fusion status is unverified.
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
**USZ-EMC** (Bangerter et al., *Human Cell* 2022/2023) and **NCC-EMC1-C1** (Iwata et al., *Human Cell* 2025);
DepMap additionally holds H-EMC-SS (n = 1). We propose a genuine collaboration rather than a data extraction:

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
candidates carry specific window liabilities, leaving GD2 (indirectly) and a grounded SSTR2/DOTATATE
neuroendocrine hypothesis as the forward leads. We report the one available EMC line's profile, specify the
protein-level validation that matters, and invite the EMC-model groups to resolve it.

---

## Data & code availability

Code and committed outputs (`research/modalities/`, refreshed to the `modalities-cache` branch):
- Surfaceome scan + selectivity + EMC-line profile — `emc_surfaceome_scan.py` → `emc-surfaceome-scan.json`
- Normal-tissue window — `emc_surface_normal_window.py` → `emc-surface-normal-window.json`
- EMC-line data probe — `emc_line_data_probe.py` → `emc-line-data-probe.json`
- GSE4303 cross-check — `emc_gse4303_crosscheck.py` → `emc-gse4303-crosscheck.json`
- Red-team log — `emc-surface-target-redteam.md`

Sources: UniProt; DepMap (incl. H-EMC-SS/ACH-001519); Human Protein Atlas; NCBI GEO (GSE4303).

## References

Verified in the repository pool:
- **Sjögren H, et al.** EWSR1/NR4A3 fusion in EMC.
- **Panagopoulos I, et al.** EMC fusion variants/partners.
- **Bangerter, et al.** USZ-EMC patient-derived models. *Human Cell* 2022/2023.
- **Iwata S, et al.** NCC-EMC1-C1. *Human Cell* 2025.
- **Uhlén M, et al.** Human Protein Atlas. *Science* 2015.
- **Bausch-Fluck D, et al.** The in silico human surfaceome. *PNAS* 2018.

To verify (do not treat as established until sourced):
- EMC neuroendocrine differentiation / INSM1, synaptophysin as EMC markers — **[citation to verify]** (Modern
  Pathology 2017; comprehensive EMC review 2025).
- H-EMC-SS (ACH-001519) authentication and EWSR1::NR4A3 status — **[citation to verify]** (Cellosaurus/DepMap).
- CD56 ADC lorvotuzumab mertansine (IMGN901) discontinuation — **[citation to verify]**.
- SSTR2 / ¹⁷⁷Lu-DOTATATE (approved NET radioligand) and ²²⁵Ac analogues — **[citation to verify]**.
- α (²²⁵Ac ~50–80 µm) vs β (¹⁷⁷Lu ~2 mm) tissue ranges — **[citation to verify]**.
- CDH11 normal fibroblast/synovial/bone expression (RA/fibrosis target) — **[citation to verify]**.
- Clinical-stage agents per antigen (GPC2, PTK7, B7-H3, etc.) — **[citation to verify]** per antigen.
- EMC incidence (<1% of soft-tissue sarcoma) — **[citation to verify]**.

---
*Provenance: consolidates the surfaceome scan (incl. H-EMC-SS profile + BH-corrected selectivity), the
normal-tissue window (controls validated), the EMC-line data probe and the GSE4303 cross-check (committed CPU
outputs on `modalities-cache`), and two red-team passes ([`emc-surface-target-redteam.md`]). No antigen is
asserted as an EMC-validated target.*
