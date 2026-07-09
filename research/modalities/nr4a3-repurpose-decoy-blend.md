# Repurposing screen ↔ decoy-null: provenance and seamless blend

**Purpose.** Fold the drug-repurposing selectivity screen into the existing decoy-null narrative
(§2.4/§2.5 of the degrader paper) so it *reinforces the same specificity story at ~6k-compound scale*,
rather than sitting beside it as a separate analysis with its own receptors and its own null.

## 1. The specificity story the repurposing screen extends
The single-snapshot MM-GBSA NR4A3 "selectivity margin" is **non-specific on its own**: a 38-drug non-NR4A
decoy set (`decoy_library.py`) run through the identical dock→MM-GBSA funnel scores `confirmed_selective`
**39 % of the time**, because the NR4A3 receptor frame is systematically scored more favorably than the
paralogue frames. So `margin > 0` is meaningless; the decoy null gives a calibrated bar
(`selectivity_calibration.py`: 95th-pct margin **+13.12 kcal/mol**), and a candidate is only credibly
selective if its margin sits in the extreme right tail of that null. In the de-novo campaign only
`denovo_111` (+15.70) cleared it.

The repurposing screen asks the same question of ~6,000 **marketed** drugs (Broad Drug Repurposing Hub):
docked NR4A3-pocket triage → promote the strong tail (top-250, dG ≤ ≈ −8.4) → 3-receptor dock → single-
snapshot MM-GBSA → **calibrate against the same decoy null**. Because n is ~160× the decoy set, it is a far
more robust demonstration of the non-specificity: it measures what fraction of a large, structurally diverse
marketed-drug set the raw verdict mislabels, and whether *any* existing drug clears the calibrated bar.

## 2. Provenance of the cached opened conformers (why a re-run was needed)
The 3-receptor funnel docks each paralogue's **metad-opened** pocket, extracted deterministically by
`nr4a3_warhead.extract_opened_conformer` (max-fpocket-druggability frame over a fixed
`N_FPOCKET_FRAMES = 25` linspace of each `*-metad` trajectory). Deterministic ⇒ identical metad input ⇒
identical conformer.

A conformer-hash audit (`compare_conformers.py`, workflow `compare-conformers-aws.yml`) found the screen's
first pass had reused a **different** opened-frame extraction than the rest of the paper:

| prefix | NR4A1 opened.pdb | NR4A2 opened.pdb | NR4A3 |
|---|---|---|---|
| `nr4a3-decoy-matrix` (the +13.12 null) | `8bedd…` (frame 524, drug 0.981) | `c8d00…` (frame 125, 0.938) | `fbb87…` release |
| `nr4a3-denovo-matrix` (whole de-novo campaign) | `8bedd…` | `c8d00…` | `fbb87…` |
| `nr4a3-matrix` (first-pass cache) | `f34ea…` | `4c6db…` | — |
| `nr4a3-repurpose-3recept` (first pass) | `f34ea…` | `4c6db…` | `fbb87…` |

NR4A3 matched everywhere (fixed release-druggable structure); the **paralogue** conformers differed. That
mismatch is why the first-pass margins ran off the decoy scale (max repurpose margin +19.8 vs decoy max
+16.46): the drugs were scored against *different* paralogue pockets than the null. The committed +13.12 bar
was therefore **not** applicable to the first-pass numbers.

## 3. The fix — re-run on the canonical frames
Re-docked all 250 promoted drugs on the **canonical `nr4a3-denovo-matrix` conformers** (the exact frames the
decoy null and de-novo campaign use; `cache_prefix=nr4a3-denovo-matrix`, release NR4A3), then single-snapshot
MM-GBSA (`nr4a3-repurpose-3recept-fm` → `nr4a3-repurpose-mmgbsa-fm-s0..s12`). Now the committed +13.12 null is
frame-matched **by construction**, and the screen is a same-receptor, same-null, same-method extension of the
paper — its above-null hits are directly comparable to `denovo_111`.

The report (`report_repurpose_selectivity.py`, calibrated readout, commit history d33b096→) drops the raw
`confirmed_selective` count (uncalibrated) and reports the **ABOVE-NULL** set: drugs whose frame-matched
NR4A3 margin exceeds the +13.12 bar, each with an empirical p-value (fraction of decoys ≥ its margin).

## 4. Result (to fill from the frame-matched REPORT)
- Fraction of the 250 promoted marketed drugs the raw verdict calls `confirmed_selective`: _[TBD]_ (expected
  ≈ the 39 % decoy rate → reinforces non-specificity at scale).
- Drugs clearing the +13.12 decoy-calibrated bar (ABOVE-NULL): _[TBD list, with margins + p_decoy]_.
- Interpretation vs `denovo_111` (+15.70, 1/38 decoys above): _[TBD]_.
- Pan-NR4A (CAR-T angle) engagers: _[TBD]_ — same caveats (docking promiscuity, MM-GBSA magnitude inflation).

**Caveat carried from the null:** single-snapshot MM-GBSA magnitudes are inflated (no entropy/ensemble);
trust the direction and the above-null flag, not kcal/mol. Any above-null hit is a screening-grade prediction
warranting FEP, not a validated selective binder.
