# Emerging / other-modality scan for EMC (Phase 2)

> **SOURCE MEMO (internal) — feeds the active manuscript** [`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md)
> via the strategy capstone [`emc-treatment-strategy.md`](./emc-treatment-strategy.md). Not separately submitted.
> Folder map: [`README.md`](./README.md).

**Scope.** Autonomous Phase-2 sweep (2026-06-22) for treatment modalities *beyond* the routes
already on the board (degrader, synth-lethal, vaccine, TCR-T, ImmTAC, TKI+ICI), checking which
plausibly **apply to EWSR1::NR4A3 EMC**. Literature-grounded; tags **[EMC-specific]/[pan-sarcoma]/
[hypothesis]**. Feeds `research/IDEAS.md`.

Result: three genuinely applicable leads (trabectedin, FAP-RLT, B7-H3) plus one novel
downstream-effector hypothesis (PPARG). Ranked by near-term credibility.

---

## 1. Trabectedin — approved, mechanism-fit, has an EMC responder. **NEAR-TERM LEAD.**

- **Mechanism fits a fusion-driven sarcoma exactly.** Trabectedin binds the DNA minor groove and
  **displaces fusion oncoprotein transcription factors from their target promoters** — its
  validated mode of action in myxoid liposarcoma (FUS::DDIT3). EMC is the same *class* of disease:
  EWSR1::NR4A3 is an aberrant transcription factor (it transactivates targets incl. **PPARG**,
  see §4). So trabectedin's mechanism is on-target for EMC's biology. **[hypothesis, strong
  class rationale]**
- **EMC clinical signal.** A metastatic EMC patient had an *impressive response and long-term
  survival* on trabectedin (+ radiotherapy); EMC appears in the trabectedin-treated sarcoma series.
  **[EMC-specific, anecdotal]**
- **Why it's attractive:** approved for soft-tissue sarcoma, already used in this population — a
  *repurposing with mechanistic fit*, not a new molecule. Sits alongside the TKI+ICI combination as
  the most actionable near-term option.
- **Next:** ★ compile the EMC trabectedin response evidence into the graded table with the
  TKI/IO data; consider the rational **trabectedin + (TKI or IO)** combination given non-overlapping
  mechanisms.

## 2. FAP-targeted radioligand therapy (FAPI-RLT) — emerging, plausibly applies. 

- **Pan-sarcoma efficacy signal.** Fibroblast activation protein (FAP) is expressed by
  cancer-associated fibroblasts in >90% of solid tumours; **⁹⁰Y-FAPI-46 RLT controlled disease in
  ~half of advanced-sarcoma patients** (and ²²⁵Ac/¹⁷⁷Lu-FAPI in trials). **[pan-sarcoma]**
- **Why EMC is a good candidate:** EMC is a **myxoid, stroma-rich** tumour — exactly the
  CAF/stroma-heavy context where FAP is abundant. The same FAPI tracer is *diagnostic* (FAP-PET),
  so eligibility is directly measurable. **[hypothesis]**
- **Next:** ★ confirm FAP expression / FAP-PET avidity in EMC from the literature; if avid, FAPI-RLT
  is an off-the-shelf, tumour-agnostic theranostic an EMC patient could access via RLT programs.

## 3. B7-H3 (CD276) surface antigen → ADC / bispecific / CAR-T — broad but needs EMC confirmation.

- **Near-ubiquitous in soft-tissue sarcoma:** B7-H3 expressed in **97% of STS (69% high)**;
  restricted in normal tissue → attractive surface target. **[pan-sarcoma]**
- **Multiple ready modalities:** the ADC **ifinatamab deruxtecan** (B7-H3, clinical), the
  **B7H3×CD3 bispecific CC-3** (active across sarcoma subtypes preclinically), and **B7-H3 CAR-T**
  (see the CAR-T memo). A surface target unlocks the antibody/cell modalities that the
  intracellular fusion/CTAs cannot.
- **Gap:** **EMC-specific B7-H3 IHC** is the missing datum (the 97% is across STS subtypes). This is
  the single cheapest confirm/kill that would open three modalities at once.
- **Next:** ★ search/curate EMC-specific B7-H3 IHC; if EMC is B7-H3⁺, ADC (ifinatamab deruxtecan)
  is the fastest near-term route and B7-H3 CAR-T the cell-therapy route.

## 4. Downstream effector: the fusion activates **PPARG** — novel, druggable, speculative.

- EWSR1::NR4A3 **transactivates the PPARG nuclear-receptor gene** through a PPARG-promoter response
  element [Filion 2009-type work; PMC4429309]. PPARG is a *bona fide druggable* nuclear receptor
  with **approved agonists** (thiazolidinediones: pioglitazone) and antagonists. **[EMC-specific
  mechanism]**
- **The hypothesis:** if the fusion's oncogenic program runs partly *through* PPARG, then PPARG
  modulation is a downstream, already-drugged node — attacking the pathway where it becomes
  pharmacologically tractable, instead of the undruggable TF itself.
- **Caveats / next:** direction matters (is PPARG pro- or anti-tumour here? TZDs are
  pro-differentiation/anti-proliferative in some sarcomas — could be *agonism*, not antagonism, that
  helps). ★ Pull the EMC PPARG-axis literature and any TZD-in-sarcoma data before weighting. Cheap,
  uses approved drugs, mechanistically anchored — a good speculative-but-grounded thread.

## 5. Briefly considered, lower priority
- **XPO1 inhibitor (selinexor):** approved (dedifferentiated liposarcoma context); generic
  anti-proliferative, no EMC-specific rationale. Park.
- **Oncolytic virus / TIL:** generic; no EMC-specific hook. Park.

---

## Bottom line
Phase-2 adds **trabectedin** (approved, mechanism-fit, EMC responder) to the near-term lead tier
alongside TKI+ICI; **FAP-RLT** and **B7-H3 (ADC/bispecific/CAR-T)** as emerging routes gated by a
cheap EMC-expression confirm; and **PPARG** as a novel downstream-effector hypothesis. None of these
needs a molecule that doesn't exist — they need EMC-specific expression/response confirmation.

## References (verified this session)
- EMC two-institution clinical/molecular outcomes (trabectedin-treated series).
  https://pmc.ncbi.nlm.nih.gov/articles/PMC7308468/
- EWSR1/NR4A3 activates the PPARG nuclear-receptor gene. https://pmc.ncbi.nlm.nih.gov/articles/PMC4429309/
- B7-H3 widely expressed in soft-tissue sarcomas (97%/69% high). https://pmc.ncbi.nlm.nih.gov/articles/PMC11523878/
- ⁹⁰Y-FAPI-46 radioligand therapy in advanced sarcoma (Clin Cancer Res 2022).
  https://aacrjournals.org/clincancerres/article/28/19/4346/709301/
- FAP expression in sarcomas. https://pmc.ncbi.nlm.nih.gov/articles/PMC10275689/
