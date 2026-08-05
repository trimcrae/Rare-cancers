---
id: DOC-DEPMAP-INSILICO-FINDINGS
title: DepMap in-silico findings for EMC candidates (no-wet-lab evidence)
level: L4
kind: memo
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `memo` from its location under research/modalities/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# DepMap in-silico findings for EMC candidates (no-wet-lab evidence)

> ## ⛔ AMENDMENT (2026-08-05) — every `myxoid` number below is **one cell line, and that line's identity is disputed**
>
> **This file's `myxoid` column is `n = 1`, and the line is `ACH-001519` / H-EMC-SS** — established
> here by exact value match, since neither this file nor
> [`depmap-target-expression.json`](./depmap-target-expression.json) names a model ID: **CD276 4.44,
> NCAM1 0.03, FAP 0.0, ERBB2 5.29, L1CAM 3.18, MCAM 0.12, EGFR 0.19** are byte-identical to that
> line's `myxoid_mean_log2tpm` in [`emc-surfaceome-scan.json`](./emc-surfaceome-scan.json), across
> seven genes. ⭑ **This use was invisible to a name-based search** — the file predates the line's
> discovery and calls the group "myxoid *liposarcoma*" — so it was found by matching the data, not
> the string.
>
> **And that line is not usable as EMC evidence.** Cellosaurus `CVCL_1238` records, citing a primary
> source: *"Caution: Does not harbor a gene fusion involving EWSR1 which is a hallmark of
> extraskeletal myxoid chondrosarcoma (PubMed=34413129)."* DepMap's own filtered fusion caller
> returns 2 calls for the model and neither names NR4A3 or any FET gene
> ([`emc-atr-vulnerability.json`](./emc-atr-vulnerability.json) → `part_a_hemcss_identity`; full
> correction: [`emc-surface-target-landscape.md` → Amendment 1](../manuscripts/emc-surface-target-landscape.md)).
> ⚠ It does **not** establish what the line is instead — that needs STR authentication + RT-PCR,
> which this programme cannot perform.
>
> **So the `myxoid` label in this file is wrong twice over** — it is not myxoid liposarcoma (that
> was the belief when this was written), and it is not usable EMC either. Read it as **one sarcoma
> line of disputed identity**.
>
> | claim in this file | status |
> |---|---|
> | Finding 3: *"PRAME … HIGH in myxoid (7.6) … **EMC is a myxoid-class tumour, so this is the most promising antigen-directed signal**"* and the tracker update *"best antigen-directed option **for a myxoid-class tumour**"* | ⛔ **INVALIDATED as an EMC-proximal read.** The 7.6 is one line of disputed identity. ⭑ Note [`../manuscripts/emc-treatment-roadmap.md`](../manuscripts/emc-treatment-roadmap.md) already **refused** to treat the 7.6 as EMC-proximal — right conclusion, wrong reason (it thought the line was liposarcoma) |
> | Finding 3: **PRAME ≫ MAGE-A4 / NY-ESO-1** (53 % vs 7 % / 5 %) | ✅ **SURVIVES.** A *relative* claim across all sarcoma lines; the disputed line is one of them and cannot move it. This is the defensible form of the PRAME lead |
> | Finding 2: **B7-H3 near-universal (99 %, mean 5.73)** | ✅ **SURVIVES.** Rests on the whole panel; `myxoid 4.4` is one of six subtype numbers and is the *lowest* of them |
> | Finding 2: *"NCAM1/CD56 … **myxoid-subtype ≈ 0** (myxoid *liposarcoma* is not NE)"* → CD56 stays plausible-but-unconfirmed | ⚠ **CONCLUSION SURVIVES, REASONING RE-LABELLED.** The parenthetical is wrong; the 0.03 is one line of disputed identity, so it was never evidence about EMC either way. "Unconfirmed" was and remains right |
> | Finding 1 (fusion addiction by FLI1-in-Ewing analogy) and the CTA-silencing / stromal-FAP caveats | ✅ **UNAFFECTED.** No `myxoid` value enters them |
> | The banner *"EMC has no DepMap line"* and *"no EMC line exists in DepMap"* | ✅ **CORRECT AGAIN**, by accident. It was believed false between 2026-07-03 and 2026-08-05 |
>
> ⚠ **Nothing below is rewritten** — the original text stays quotable, per CLAUDE.md §1.2.
> **A route's grade input moved and is NOT re-graded here:** `RT-PRAME-IMMTAC` is graded *"NEW
> antigen-directed lead — best of the CTAs"* in [`../IDEAS.md`](../IDEAS.md), and Finding 3 is its
> in-silico support. The *relative* half of that support survives; the myxoid-proximity half does
> not. Re-grading is a separate call.

**What.** Results of the in-silico work program's first executable arm — mining public DepMap 24Q4
across **sarcoma lines as an EMC surrogate** (EMC has no DepMap line). Two analyses:
`depmap_target_expression.py` (expression of candidate targets) and the `fusion_addiction_proxy`
added to `depmap_sarcoma_dependency.py`. Data: `depmap-target-expression.json` /
`depmap-sarcoma-dependency.json` (+ charts). **Surrogate evidence, not EMC data.**

**Pipeline validated:** housekeeping ACTB/GAPDH read ~11–12 log2(TPM+1), 100% of lines — the
expression read is trustworthy.

## Finding 1 — the degrader's make-or-break premise is supported (by analogy). **Encouraging.**
The degrader route assumes EMC is *addicted to its fusion* (degrading EWSR1::NR4A3 kills the cell).
We can't test EMC directly, so we used the canonical analogue: **FLI1 dependency in Ewing sarcoma**,
where EWS-FLI1 is the driver.
- **FLI1 in Ewing: gene effect −0.93, 74% of lines dependent (n=27).** A strong, selective
  dependency — FET-fusion sarcomas *are* addicted to their fusion **as a class**.
- This **raises the prior** (a bet-justifying analogy, **not** EMC evidence) that EMC depends on
  EWSR1::NR4A3, i.e. that a degrader *could* be lethal — enough to justify *testing* the driver, not to
  conclude it. Bounded by what actually transfers: the shared **EWS low-complexity transactivation domain**
  drives much of Ewing's addiction, so the analogy supports "EMC is probably fusion-addicted," **not** "the
  NR4A3 effector specifically is essential" (the fusion partners differ). The dTAG test is the make-or-break.
- *Caveat:* NR4A3 itself reads non-essential here (0.02) only because **no line in DepMap is EMC**
  (the few NR4A3⁺ lines aren't EMC); EWSR1's essentiality (−1.2) is its housekeeping RNA-binding
  role, not fusion-specific. FLI1-in-Ewing is an analogy, not EMC proof — but it's a strong one.

## Finding 2 — surface targets: B7-H3 is the standout. **Encouraging for ADC/CAR-T.**
Expression in sarcoma lines, log2(TPM+1); "expressed" = ≥3:
- **CD276 / B7-H3: mean 5.73, 99% of lines expressed**, and **high across every subtype** (Ewing
  4.8, synovial 5.7, myxoid 4.4, ARMS 5.2, rhabdoid 5.4, liposarcoma 6.6). Near-universal →
  strong surrogate support for the **B7-H3 ADC (ifinatamab deruxtecan) / CAR-T / bispecific** route.
  This partly closes the gate that was "no EMC B7-H3 IHC published" — the surrogate says sarcoma
  near-uniformly expresses it.
- **MCAM/CD146: 73%, mean 4.33** (higher than non-sarcoma) — a bonus mesenchymal surface candidate.
- **NCAM1/CD56: 59%, mean 3.23** overall, but **myxoid-subtype ≈ 0** (myxoid *liposarcoma* is not
  NE). EMC's neuroendocrine phenotype (synaptophysin/INSM1⁺) means EMC could differ from that
  surrogate — so CD56 stays *plausible-for-EMC but unconfirmed*, not supported by this surrogate.
- ERBB2/HER2 86% but not sarcoma-selective; EGFR/L1CAM modest. Lower priority.

## Finding 3 — antigen-directed: PRAME is the best bet, MAGE-A4/NY-ESO-1 are out. **Re-ranks TCR-T.**
- **PRAME: 53% of sarcoma lines expressed (mean 3.47), and HIGH in myxoid (7.6) and synovial
  (7.2)** — EMC is a myxoid-class tumour, so this is the most promising antigen-directed signal.
  → **brenetafusp (PRAME ImmTAC, tumour-agnostic basket) and PRAME-directed CAR/TCR become the best
  antigen-directed option**, above MAGE-A4.
- **MAGE-A4 7%, NY-ESO-1/CTAG1B 5%** expressed → confirms the afami-cel/letetresgene port is weak
  for EMC.
- *Major caveat:* **cell lines epigenetically silence cancer-testis antigens** relative to primary
  tumour, so these CTA numbers are **lower bounds** — primary EMC could express more. The relative
  ordering (PRAME ≫ MAGE-A4/NY-ESO-1) is the trustworthy part.

## Caveats that bound all of this
- **Surrogate, not EMC:** no EMC line exists in DepMap; sarcoma lines (incl. myxoid liposarcoma,
  which is *not* EMC) stand in. Reads are priors, not EMC facts.
- **Cell-line artefacts:** CTAs are silenced in culture (CTA reads = lower bounds); **stromal FAP is
  under-represented** in lines (no CAF stroma), so FAP's 44% understates likely tumour FAP — the
  FAPI-RLT case is not weakened by the modest cell-line FAP.

## Net updates to the tracker
- **Degrader:** central premise (fusion addiction) *supported by analogy* → keep as the top
  high-ceiling, driver-directed bet; pair this datapoint with the warhead-design spec in the paper.
- **B7-H3 ADC/CAR-T:** *surrogate-supported* → promote from "gated by unrun IHC" to "expression
  prior favourable; confirm in EMC tissue/public proteomics."
- **PRAME-directed (brenetafusp / PRAME CAR-TCR):** *new mid-tier lead*, best antigen-directed
  option for a myxoid-class tumour — above MAGE-A4/NY-ESO-1.
