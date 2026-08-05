---
id: DOC-VIEW-ST-IMMUNO
title: ST-IMMUNO — Immunotherapy and antigen-directed approaches
level: L1
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Can the immune system be pointed at EMC — via the junction neoantigen, a surface antigen, a cancer-testis antigen, or checkpoint blockade?
scope: Level 1. 9 routes.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# ST-IMMUNO — Immunotherapy and antigen-directed approaches

**Thesis.** If a tumour-restricted antigen exists, the discrimination problem is solved by the immune system rather than by chemistry, and potency comes free. The bet is that EMC presents something the immune system can see.

**Portfolio role:** `hedge` · **state:** ✓ blocked · computed · confidence low

> The largest family by route count and the one most constrained by a single shared fact: EMC is antigen-cold and the junction is a weak peptide-HLA. Several routes here were downgraded on measurements rather than on reasoning, which is the useful kind of downgrade.

## What this family may NOT be used to claim

- EMC is antigen-cold and the fusion junction is a weak peptide-HLA — a property of this tumour and this junction, not of any modality here.
- Surface-antigen selectivity was measured on cell-line surrogates rather than on EMC tissue, so the negatives are as provisional as the positives would have been.
- One route's predicted binders span junction seams that a corrected exon index says do not exist; that result is void and the question is open.

## Routes

| route | state | maturity | readiness today | next action |
|---|---|---|---|---|
| **[RT-B7H3](L2-rt-b7h3.md)**<br/>B7-H3 (CD276) / CD56 → ADC, bispecific or CAR-T | ✓ parked | computed | `internal_note` | Keep registered with the surrogate caveat attached to the negative. |
| **[RT-CART-SURFACE](L2-rt-cart-surface.md)**<br/>CAR-T for EMC (surface-directed) | ✓ blocked | computed | `internal_note` | Keep registered. The antigen search re-runs automatically when EMC expression data lands. |
| **[RT-ICI-TKI](L2-rt-ici-tki.md)**<br/>Checkpoint inhibitor + anti-angiogenic TKI combination | ○ ready | concept | `internal_note` | Keep as landscape context, cited and never overstated. It is the comparator, not a contribution. |
| **[RT-JUNCTION-NEOANTIGEN](L2-rt-junction-neoantigen.md)**<br/>Fusion-junction neoantigen (the antigen, shared by three delivery routes) | ✓ blocked | computed | `internal_note` | Regenerate the junction-neoantigen predictions against the corrected exon index, then re-grade. Every predicte |
| **[RT-PANNR4A-EXVIVO](L2-rt-pannr4a-exvivo.md)**<br/>Ex-vivo pan-NR4A pole (CAR-T manufacturing additive) | ✓ ready | computed | `preprint` | Use it more prominently as the argument that the family's chemistry has a use that does not depend on solving  |
| **[RT-PRAME-IMMTAC](L2-rt-prame-immtac.md)**<br/>PRAME-directed brenetafusp (ImmTAC) / PRAME CAR-TCR | ○ blocked | computed | `experimental_proposal` | Include in the collaborator ask: an expression confirm on EMC tissue is small, and the therapeutic already exi |
| **[RT-TCR-IMMTAC](L2-rt-tcr-immtac.md)**<br/>Fusion-junction TCR-T / soluble-TCR (ImmTAC) against the junction peptide-HLA | ○ parked | concept | `internal_note` | Keep registered. Re-grade after the neoantigen predictions are regenerated. |
| **[RT-TCRT-CTA](L2-rt-tcrt-cta.md)**<br/>TCR-T / engineered T cells vs a cancer-testis antigen (synovial-sarcoma port) | ✓ parked | computed | `internal_note` | Keep registered for automatic re-grade when EMC expression data lands. |
| **[RT-VACCINE](L2-rt-vaccine.md)**<br/>Fusion-junction vaccine / HLA-coverage paper | ✓ parked | computed | `internal_note` | Keep the HLA-coverage output as a reusable input to eligibility analysis. Do not advance the vaccine while the |
## What this family buys the portfolio — blockers it RETIRES

- **BLK-NOT-FUSION-SELECTIVE** (`fundamental_biological_limit`) — The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half)
- **BLK-PARALOGUE-DDG** (`requires_better_simulation_accuracy`) — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** (`requires_better_structure_prediction`) — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer

## Best next action

Regenerate the junction-neoantigen predictions against the corrected exon index — the current binders span seams no reported junction produces, and the regeneration is free.

*Cost:* $0

[← L0](L0-ecosystem.md)
