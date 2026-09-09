---
id: DOC-PORTFOLIO-INVESTIGATION-ANDGATE-3-2026-09-09
title: "ANDGATE-3 — the in-trans term is missing from the fusion's own partition function; the reported selectivity inversion is a modelling artifact"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: ANDGATE-3
continues: ANDGATE-2 (item 2 of its §7), PUB-ANDGATE
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# ANDGATE-3 — auditing the arm-2 multiplicity sensitivity, and what it exposed

## 1. The concrete question

ANDGATE-2 closed with two named follow-ups. Item 1 (measure in-hub `C_E` by FCS on a CRISPR
knock-in tag) is wet-lab and unavailable here. **Item 2 — "settle what arm 2 binds, and how many
sites per chain", which it called the cheaper one and "the sensitivity that could overturn the bulk
verdict" — has a computable half: is the multiplicity sensitivity that produces the fragility set up
correctly?** Concretely: `n`, the number of engageable arm-2 sites, is a property of the EWSR1 LC
domain, and the Erratum establishes that **the fusion carries that same LC domain**. Does the
lane's model apply `n`, and the in-trans competition it drives, to both species?

## 2. Merit rationale

The in-trans cost curve is the only quantitative handle the lane has on the manuscript's §8.7
caveat, and every downstream statement in PUB-ANDGATE and ANDGATE-2 — the half-window point, the
regime placement of the literature anchors, the multiplicity fragility, and the claim that the
design **inverts** above `C_E = EM` — is read off it. If the curve is asymmetric between the two
species it compares, those statements are being read off the wrong function. Auditing a
two-generation-deep derived curve before a third generation builds on it is exactly the load-bearing
step, and it is pure CPU arithmetic on committed inputs: no ligand, no sampling, no data.

## 3. The exact evidence gap

* PUB-ANDGATE's `f_fusion(...)` takes no `C_E` argument. Its committed
  `fusion-andgate-trans-competition.json` reports `fusion_fraction_bound = 0.5261` at **every one of
  the 13 sweep points, from `C_E` = 0 to 10 mM** (`checks/02-…/stdout.txt`). The fusion partition
  function has **no `C_E` dependence at all**.
* ANDGATE-2's `place_literature_bound_on_cost_curve.py` inherits that `f_fusion` unchanged and sweeps
  multiplicity as `C_E = n × C_protein` — i.e. **`n` on the wild-type/trans side only**; the cis term
  stays at one site.
* The manuscript's own Erratum (lines 52–56) and §2/§3 (79–81, 127–128, 153–158) state that the LC
  domain is **not** fusion-restricted and that the fusion is `EWSR1-LC :: NR4A3-LBD`. So a ligand
  anchored by arm 1 on the **fusion's** NR4A3-LBD can bridge in trans to a free LC chain exactly as
  it can on wild-type NR4A3, and the same `n` multiplies the fusion's cis term.
* This is not a re-run of either lane and not a new baseline review: it is the internal-consistency
  check neither lane performed.

## 4. Re-derivation first — the committed numbers DO reproduce

Before touching anything, **16 committed values were re-derived digit for digit** from the same
inputs by an independent re-implementation (`checks/01`, identity checks hard-fail with exit 1):

* PUB-ANDGATE `fusion_fraction_bound` 0.5261, `wildtype_fraction_bound` 0.0909, cis-only window 5.79;
* all four ANDGATE-2 literature placements (E1 5.776/0.9982, E2 5.536/0.9567, E2b 5.684/0.9822,
  E3 3.156/0.5455);
* all ten ANDGATE-2 multiplicity rows (5.776, 5.755, 5.684, 5.489, 5.061 / 5.536, 5.101, 4.033,
  2.630, 1.578).

**There is no arithmetic discrepancy.** The finding is a structural asymmetry in the model those
correct numbers come from.

## 5. The step taken, and the result

**Artifact.** `andgate3_symmetric_trans_model.py` → `andgate3-symmetric-trans-competition.json`
(this directory). Pure stdlib, CPU, no network, no external data, no GPU, no paid compute.

Same convention and same states as the parent lane, with two terms repaired:

```
Z_fus = 1 + L/Kd1 + n·L/Kd2 + (L/Kd1)·( n·EM/Kd2  +  C_E/Kd2 )      <- trans term was absent
Z_wt  = 1 +                   (L/Kd1)·( 1         +  C_E/Kd2 )
```

**Result A — the reported inversion is an artifact, and this is the decisive item.** Because the
trans term is identical in both partition functions, the low-occupancy window is

```
window = [ 1 + n·EM/Kd2 + C_E/Kd2 + n·Kd1/Kd2 ] / [ 1 + C_E/Kd2 ]  >  1  for all C_E,
```

monotonically decaying **to 1 and never below it**. PUB-ANDGATE §4 item 3 states the window is
"**inverted (0.70×, 0.58×) above EM** — where the molecule prefers wild-type NR4A3 to the fusion."
Those exact committed values are reproduced here (0.700 at `C_E` = 3 mM, 0.580 at 10 mM) and become
**1.064 and 1.008** under the symmetric treatment. **A bivalent ligand cannot prefer a chain
carrying one of its two epitopes over a chain carrying both; the inversion was the omitted term.**
The correct statement is that selectivity **asymptotes to unity** — the gate stops working, it does
not run backwards.

**Result B — an honest negative on the multiplicity concern.** Applying `n` symmetrically raises the
absolute window substantially (at the 200 nM anchor, n = 10: **9.84×** symmetric vs 5.68× one-sided),
but when each `n` is compared against its **own n-matched cis-only baseline**, the retained fraction
is essentially unchanged (0.9822 vs 0.9822 at n = 10; 0.6973 vs 0.6970 at the 5 µM ceiling).
**ANDGATE-2's multiplicity fragility conclusion therefore survives the correction in relative terms.**
The one-sidedness misstates the absolute window, not the shape of the fragility. This is recorded as
a negative against my own hypothesis and is not smoothed over.

**Result C — the bulk verdict is unchanged and slightly strengthened.** At the literature anchors
(0.2–5 µM) the correction moves the retained window by <1% (0.9982→0.9983; 0.9567→0.9587).
ANDGATE-2's "negligible in bulk nucleoplasm" stands. The intra-condensate regime moves from retained
0.5455 to 0.5677 — still "materially degraded", still resting on an unmeasured quantity.

**Validation / baseline.** The 16-value digit-for-digit reproduction above *is* the baseline; the
script exits 1 rather than proceeding if any of them drifts. No prior symmetric model exists.

**Provenance.** Kd1 = 10 µM, Kd2 = 100 µM, EM = 1 mM, L = 1 µM — the manuscript's own illustrative
values, unchanged, via `../PUB-ANDGATE/andgate_trans_competition_model.py`. `C_E` and `n` are swept,
never asserted. The two literature anchors are carried over from ANDGATE-2 **with its caveats intact**
(the 200 nM figure is EWS/FLI1, not wild-type EWSR1) and are re-stated as anchors, not as `C_E`.

**Limitations.**
1. **Conditional and bounding only.** No validated, selective, cell-active EWSR1-LC arm-2 ligand
   exists in the public record. Nothing here asserts one exists or reports any molecule's properties.
   Every number is a property of a model and is **not** an EMC efficacy, safety,
   selectivity-as-therapeutic-property, therapeutic-window or clinical-readiness claim.
2. The symmetric trans bridge is still charged **no** steric or configurational penalty on either
   side; a real trans bridge to a disordered LC chain will be worse than modelled for both species.
3. Site multiplicity is treated as `n` independent equivalent sites with no cooperativity or
   excluded volume, and `n_cis = n_trans` — the fusion retains the N-terminal LC, whereas wild-type
   EWSR1 carries additional C-terminal RGG/IDR sequence, so `n_cis ≤ n_trans` is the more likely
   truth and was **not** assumed here.
4. Occupancy, not degradation. The separate degradation model is untouched.
5. **The decisive datum is still missing.** This corrects a model; it measures nothing. In-hub
   engageable wild-type EWSR1-LC site concentration remains UNKNOWN — not zero.

**Boundaries drawn against the two named results.** This step touches **neither**. DEGRADER-2
concerns the *shared-LBD* degrader paper's no-overlap sentence and its `STOP_NO_REFERENCE`
covalent-ligandability dependency — a different manuscript and a different gate; nothing here
re-counts C397 frames or reopens that stop. MONOVALENT-3 concerns corridor-closure clash cutoffs and
residue attribution in a structural model; nothing here is structural, and no clash cutoff, docking,
structure prediction or sampling was run. The no-GPU deferral stands untouched.

**Stop condition — reached.** Complete when the committed numbers were re-derived, the asymmetry was
localised to one named term, the corrected curve was computed, and the inversion claim was resolved.
It stops there: it does not estimate `C_E`, does not adopt any `n`, does not reopen the arm-2 ligand
gate, and does not edit the manuscript.

## 6. Shared-file impact — none required

The **manuscript makes no inversion claim**; §8.7 says only that the mode is unmodelled. The defect
lives entirely in this campaign's own lane artifacts (`PUB-ANDGATE/FINDING.md` §4 item 3 and its
JSON; `ANDGATE-2`'s inherited `f_fusion`). **No shared file needs changing, so no diff is offered
and none was applied.** The correction to record is: **PUB-ANDGATE's "inverted / prefers wild-type"
statement should not be carried forward by any later lane.** ANDGATE-2's §7 recommendation for
manuscript §8.7 remains valid as written, because it cites the bulk-regime bound and the
`C_E* = Kd2` threshold, neither of which this correction moves.

## 7. Next credible independent work

1. **Unchanged and still decisive:** measure free engageable wild-type EWSR1-LC site concentration,
   in-hub and nucleoplasmic, in a fusion-bearing cell (ANDGATE-2 item 1). Nothing computational
   substitutes for it.
2. **Newly available and cheap:** the corrected formalism makes `n` a *design lever* rather than only
   a liability — `n·EM/Kd2` is the cis term. Whether an arm-2 chemotype engaging several LC motifs
   helps or hurts is now a well-posed CPU question, but it is **not** answerable until the
   manuscript resolves which of its two incompatible readings of arm 2 (discrete IDR contact vs
   condensate partitioning) it means. That resolution, flagged by PUB-ANDGATE item 5 and still open,
   is the gating item for any further modelling in this lane.
