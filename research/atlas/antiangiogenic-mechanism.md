# Fusion-subtype antiangiogenic mechanism — kinome comparison + response-linked data model

> Strategy Project 3 (computational portions). Two deliverables: (1) a kinome-level comparison that
> asks *which inhibited-kinase set best matches EMC responders* (not which nominal target is
> over-expressed), and (2) a response-linked common data model / CRF a collaborator can populate.
> The load-bearing clinical fact is now primary-abstract confirmed (atlas claim C019): **sunitinib
> responders expressed EWSR1::NR4A3; refractory cases carried TAF15::NR4A3.**

## 1. Kinome-level TKI comparison

**Principal reported kinase targets** of the relevant multikinase inhibitors. These are
well-established from drug labels and kinome-profiling literature; **exact potencies (Kd/IC50) must be
sourced from a single quantitative kinome-profiling reference (e.g. a Davis/Karaman-class dataset)
before publication** — this table is the qualitative target-set scaffold, not potencies.

| TKI | VEGFR1/2/3 | PDGFRA/B | KIT | RET | FGFR | CSF1R | FLT3 | MET | AXL | ALK | EMC clinical status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Pazopanib** | ✓✓ | ✓ | ✓ | – | ✓(1/3) | ✓ | – | – | – | – | **ORR 18%, responders EWSR1** |
| **Sunitinib** | ✓✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | – | – | – | **6/10 PR; responders EWSR1, refractory TAF15** |
| Cabozantinib | ✓(2) | – | ✓ | ✓ | – | – | ✓ | ✓✓ | ✓ | – | trial cohort (NCT05836571, pooled) |
| Regorafenib | ✓✓ | ✓ | ✓ | ✓ | ✓ | – | – | – | – | – | untested in EMC |
| Lenvatinib | ✓✓ | ✓ | ✓ | ✓ | ✓✓ | – | – | – | – | – | untested in EMC |
| Axitinib | ✓✓ (selective) | ✓ | ✓(weak) | – | – | – | – | – | – | – | untested in EMC |
| Selective RET (selpercatinib/pralsetinib) | – | – | – | ✓✓ | – | – | – | – | – | – | untested — clean RET test |
| **Brigatinib** | – | – | – | – | – | – | ✓ | – | – | ✓✓ | NCC cytotoxic hit (NOT antiangiogenic) |

**The inference the atlas draws (a falsifiable hypothesis, not a conclusion):**
- The two agents with EMC activity (pazopanib, sunitinib) **share VEGFR1–3 + PDGFRA/B + KIT** — a
  vascular/stromal target set. That shared set is the leading candidate for the responder-defining axis.
- **RET** is hit by sunitinib (and cabozantinib/lenvatinib/regorafenib) and is **reproducibly elevated
  in EMC** (Davis 2017; GSE24369 reprocessing AUC 0.86, claim C006/C018) — but elevation is a *marker*,
  not proven dependency. A **selective RET inhibitor** is the clean experiment that separates
  "RET is functional" from "RET is a fusion-state marker."
- **Brigatinib has no VEGFR/PDGFR activity** — so if the antiangiogenic hypothesis is right, brigatinib
  should NOT reproduce the pazopanib/sunitinib clinical pattern; its NCC single-model cytotoxicity is a
  *different* (non-vascular) mechanism requiring deconvolution. This is a built-in negative control.

**Rational next TKIs to test** (by target-set overlap with responders + a distinguishing axis):
cabozantinib (adds MET/AXL/RET — tests whether those broaden response), lenvatinib (adds FGFR),
and a selective RET inhibitor (isolates RET). Rank by which inhibited-kinase set best matches the
EWSR1-responder pattern, **not** by which nominal target reads highest.

**Why this can't be settled in tumor-cell monoculture.** VEGFR/PDGFR/CSF1R act largely on
endothelium, pericytes, fibroblasts and myeloid cells. The validation system must be co-culture
(EMC + endothelial/fibroblast/macrophage), conditioned-medium, or vascularized spheroids, with
phosphoproteomics after short TKI exposure — not a viability plate.

## 2. Response-linked common data model (CRF for a collaborator cohort)

Strategy Projects 3 + 5. An unaffiliated researcher must **not** collect identifiable data; the
clinical institution owns consent/ethics/de-identification. This is the schema to hand them.

**Per treatment-episode record:**

| field | notes |
|---|---|
| `patient_id` (institution-controlled) | de-identified surrogate |
| `fusion_partner` | EWSR1 / TAF15 / TCF12 / FUS / other — **mandatory, never pooled** |
| `five_prime_exon`, `nr4a3_exon`, `breakpoint` | exact junction where sequenced |
| `histologic_variant` | conventional / cellular / rhabdoid / high-grade |
| `baseline_biopsy_site`, `baseline_biopsy_date` | |
| `rna_available`, `archival_tissue_available` | enables correlative science |
| `drug`, `dose`, `line_of_therapy` | |
| `prior_antiangiogenic_exposure` | resistance-state covariate |
| `pretreatment_measurements[]` (lesion, date) | ≥2 needed for pre-treatment growth rate |
| `ontreatment_measurements[]` (lesion, date) | |
| `best_recist_response`, `pfs`, `os`, `time_to_next_treatment` | |
| `reason_for_discontinuation`, `adverse_events` | |
| `posttreatment_sample_available` | resistance analysis |

**Derived endpoints (computed, not stable-disease alone):** pre-treatment growth rate, on-treatment
growth rate, **growth-modulation index (GMI)**, depth + duration of shrinkage, landmark 6-/12-mo PFS,
time-to-next-treatment — all stratified by fusion partner, with leave-one-patient-out sensitivity.

**Go/no-go for any biomarker claim:** predicts *growth-rate-adjusted* benefit; stable under
leave-one-patient-out; not merely a proxy for EWSR1-vs-TAF15 unless that distinction is itself
validated; has a falsifying mechanistic experiment; measurable on archival tissue.

## 3. Honest limitations
- Kinase-target sets here are qualitative; potencies must be sourced from one quantitative kinome
  dataset before any ranking is published.
- The EWSR1-responsive / TAF15-refractory differential rests on small N from a single group
  (Stacchiotti/European network) and is not growth-rate-adjusted in the source reports.
- EMC has no fusion-partner metadata in the public expression sets, so the tumor-cell-intrinsic
  EWSR1-vs-TAF15 vascular/guidance signature cannot be built without collaborator RNA-seq.
