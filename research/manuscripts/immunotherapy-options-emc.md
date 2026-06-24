# Immunotherapy options for EMC beyond the parked vaccine

> **SOURCE MEMO (internal) — feeds the active manuscript** [`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md)
> via the strategy capstone [`emc-treatment-strategy.md`](./emc-treatment-strategy.md). Not separately submitted.
> Folder map: [`README.md`](./README.md).

**Scope.** Autonomous Phase-1 assessment (2026-06-22): does the synovial-sarcoma TCR-T success
port to EWSR1::NR4A3 EMC, and what other immunotherapy actually has EMC evidence? Decision memo,
literature-grounded; claims tagged **[established]/[EMC-specific]/[hypothesis]**. Companion to
`degrader-vs-synthetic-lethal.md`; feeds the route board in `research/IDEAS.md`.

---

## 1. TCR-T / cancer-testis-antigen port (afami-cel, letetresgene) — **WEAK for EMC**

**The idea.** afamitresgene autoleucel (afami-cel/Tecelra; MAGE-A4, HLA-A\*02-restricted) is
FDA-approved (2024) for synovial sarcoma — the first engineered TCR-T for a solid tumour; and
letetresgene (NY-ESO-1) is in trials for synovial / myxoid-round-cell liposarcoma. If EMC
expressed the antigen, the *cell product already exists* and the weak fusion-junction
immunogenicity problem is sidestepped.

**The gating fact, resolved — and it's mostly negative.** TCR-T against a CTA needs the tumour to
*express* that CTA. The literature says EMC largely does not:
- **NY-ESO-1** is "highly expressed in the majority of synovial sarcomas and myxoid/round-cell
  liposarcomas … but only **rarely in other mesenchymal tumors**" [Endo 2015; Pollack]. NY-ESO-1
  is in fact used to *distinguish myxoid liposarcoma from EMC* — i.e. EMC is NY-ESO-1-low.
  **letetresgene does not port.** [established]
- **PRAME** is low in the chondrosarcoma bucket (~7.7%) [single-centre CTA series, China 2024];
  **MAGE-A1** undetectable in chondrosarcoma. [established, though "chondrosarcoma" ≠ EMC exactly]
- **MAGE-A4** (the afami-cel target) is elevated in osteosarcoma / UPS (~33–40%) but **not
  reported high in EMC**; EMC-specific MAGE-A4 IHC is essentially uncharacterised. [gap]

**Verdict.** The direct port is **weak**. The only door not fully closed: a dedicated **MAGE-A4 /
PRAME IHC series on EMC** — if a meaningful EMC subset is MAGE-A4⁺ *and* HLA-A\*02:01⁺, afami-cel
could apply to that small subset. Prior is low, so this is a *cheap confirm/kill*, not a lead.
**Eligibility funnel** if pursued: `P(MAGE-A4⁺) × P(HLA-A\*02:01 carrier ≈ 0.40 in Europeans, less
elsewhere) × P(accessible trial)` — even optimistically a single-digit-% addressable slice.
(HLA-A\*02:01 carrier frequency is computable exactly from our AFND pipeline, `hla_coverage.py`.)

---

## 2. Checkpoint inhibitor + anti-angiogenic TKI **combination** — **REAL EMC SIGNAL (new lead)**

This surfaced while killing the TCR-T idea and is better-evidenced for EMC than anything else here.

- **Direct EMC clinical evidence.** The phase-II **ImmunoSarc** trial (sunitinib + nivolumab in
  advanced sarcoma) reported ORR 22% and an 18-month OS of 100% among partial responders —
  **explicitly including a patient with extraskeletal myxoid chondrosarcoma** [Martin-Broto et al.;
  ASCO EDBK 2024 review]. An actual EMC responder is rare gold for an ultra-rare tumour.
  **[EMC-specific]**
- **Mechanistic rationale that fits EMC.** EMC's problem for immunotherapy is that it's a
  low-mutational-burden "cold" tumour. Anti-angiogenic TKIs (which EMC is already
  unusually *sensitive* to — its one real clinical signal) **remodel the tumour immune
  microenvironment** (reduce VEGF-driven immunosuppression, normalise vasculature, increase T-cell
  infiltration), i.e. they can convert cold→hot and license a checkpoint response. The TKI
  sensitivity and the IO combination are therefore *synergistic*, not independent. **[hypothesis,
  strong rationale + the ImmunoSarc datapoint]**
- **Why it beats the other routes on *near-term* odds:** every drug already exists and is approved
  (multiple TKIs; nivolumab/pembrolizumab); there is already an EMC responder; and basket/sarcoma
  trials are the natural vehicle. No new target discovery, no bespoke manufacturing.

**Caveats.** n=1 PR is anecdotal; "cold tumour" means single-agent checkpoint inhibition alone is
unlikely to work (consistent with sarcoma IO data broadly). The combination — TKI + ICI — is the
unit of activity, and EMC-specific prospective data beyond ImmunoSarc is thin.

**Next steps (★ computational).** ★ Compile the EMC-specific IO/TKI response evidence (ImmunoSarc +
any case reports/series) into a graded table; ★ compute HLA-A\*02:01 carrier frequency (for any
parallel TCR-T subset) from AFND; identify which approved TKI has the best EMC + IO-combination
rationale (pazopanib, sunitinib, anlotinib, regorafenib).

---

## 2b. ImmTAC / soluble-TCR bispecific (tebentafusp platform) — **weak, same gate as TCR-T**

ImmTACs are soluble affinity-enhanced TCRs fused to anti-CD3 that redirect T cells against an
**intracellular antigen presented as peptide-HLA** (tebentafusp = gp100/HLA-A\*02, approved in
uveal melanoma). Off-the-shelf, no cell manufacturing — attractive. **But it targets a
peptide-HLA, so it inherits the *same* antigen gate as TCR-T:** the relevant ImmTACs are
**brenetafusp** (IMC-F106C; PRAME peptide SLLQHLIGL / HLA-A\*02:01) and MAGE-A4 constructs — and
EMC is PRAME-/MAGE-A4-low (§1). So the generic port is weak.

**The one concrete thread:** brenetafusp runs a **tumour-agnostic Phase-1/2 basket** across many
solid tumours, so a **PRAME⁺ / HLA-A\*02:01⁺ EMC patient** could be eligible *without a bespoke
product*. Prior is small (PRAME ~8% × A\*02:01 carrier × …), but basket access is more realistic
than building anything EMC-specific. The only *EMC-specific* ImmTAC would target the
fusion-junction peptide-HLA — same weak self-adjacent-junction immunogenicity as the vaccine, plus
a bespoke TCR-mimic discovery program. Not a near-term lead.

## 3. Bottom line for the board

- **TCR-T/CTA:** downgrade to *weak* — EMC is CTA-low; only an EMC MAGE-A4/PRAME IHC series could
  reopen a small subset (cheap confirm/kill, low prior).
- **TKI + checkpoint-inhibitor combination:** **elevate** — the best-evidenced near-term
  immunotherapy for EMC (real responder, existing drugs, mechanistic synergy with EMC's TKI
  sensitivity). This is the immunotherapy lead worth carrying forward.

## References (verified this session)
- afami-cel (Tecelra) FDA approval 2024, synovial sarcoma; MAGE-A4 / HLA-A\*02. (Adaptimmune.)
- Endo M, et al. *NY-ESO-1 expression in sarcomas: a diagnostic marker and immunotherapy target.*
  (NY-ESO-1 rare outside synovial / myxoid-RC liposarcoma.) https://pmc.ncbi.nlm.nih.gov/articles/PMC3518519/
- Cancer-testis antigens (MAGE-A1/A4, NY-ESO-1, PRAME) in bone & soft-tissue sarcoma, single
  centre. https://pmc.ncbi.nlm.nih.gov/articles/PMC11951172/
- *Immunotherapy in Sarcoma: Current Data and Promising Strategies.* ASCO Educational Book 2024
  (ImmunoSarc sunitinib+nivolumab; EMC partial responder). https://ascopubs.org/doi/10.1200/EDBK_432234
