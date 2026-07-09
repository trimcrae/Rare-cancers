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

## 4. Result (frame-matched REPORT, all 250; report-fm-push run 29013995524)
Pooled 250/250 MM-GBSA-scored drugs (13 shards; s5's per-ligand checkpoint uploaded despite GH-run spot
failures, so no data lost). Calibrated against the committed +13.12 null (n=38, on the hash-identical
`nr4a3-denovo-matrix` conformers → effectively frame-matched; a fresh decoy pass through
`nr4a3-repurpose-3recept-fm` would make it airtight).

- **Raw `confirmed_selective`: 97/250 (39 %)** — matches the decoy false-positive rate almost exactly →
  reinforces, at 250-drug scale, that the raw margin is non-specific. This is the headline blend value.
- **ABOVE-NULL (margin > +13.12): 14/250 = 5.6 %** ≈ the ~5 % that clear a 95th-pct bar by construction →
  the promoted set is **not enriched at the bar** (same conclusion as the de-novo campaign, now at scale).
- **Reference = the carried lead `denovo_401`** (single-snapshot margin **+13.92**; also survives
  multi-snapshot de-noising +12.83 ± 2.98, stereo-robust, FEP/ternary subject). (NOT `denovo_111`, the earlier
  single-snapshot foothold, which was **withdrawn** — its physiological cation reverses selectivity.)
- **10 hits exceed denovo_401's single-snapshot +13.92:** flupentixol (+20.54), AGI-5198 (+17.59),
  DDR1-IN-1 (+17.26), ML786 (+17.11), SNX-5422 (+16.27), 20-hydroxyecdysone (+15.43), pizotifen (+14.93),
  pyrantel (+14.86), BMS-309403 (+14.64), CP-640186 (+14.59). **4 of them beat the whole 38-decoy null**
  (p_decoy = 0.000: flupentixol, AGI-5198, DDR1-IN-1, ML786). The remaining 4 above-null (oleandrin +13.73,
  SNX-2112 +13.63, reynoutrin +13.37, BMS-986142 +13.15) clear the bar but sit below 401.
- **⚠ Single-snapshot is the TRIAGE tier only.** denovo_401 earned "lead" by surviving **multi-snapshot
  de-noising**, where `denovo_393` (single-snapshot +18.34) **collapsed to −2.95 ± 3.65**. So these
  high-margin repurposing hits are NOT yet peers of 401 — several will likely collapse the same way. The
  discriminating non-FEP step is multi-snapshot de-noising (`mmgbsa-aws.yml multisnapshot=1`) of the top hits;
  only survivors of that are true 401-tier candidates worth FEP.
- **Chemotype caveat:** the tail is dominated by promiscuity-prone classes (kinase/HSP90 inhibitors, a cardiac
  glycoside, a flavonoid, a lipophilic-amine antipsychotic) — exactly the docking artifacts the caveats flag.
- Pan-NR4A (CAR-T angle): 66 engage all three LBDs at |margin| ≤ 3; same magnitude-inflation/promiscuity caveats.

**Interpretation.** The 6k→250 repurposing screen, run through the *same funnel, receptors, and decoy null* as
the de-novo work, (i) confirms the specificity caveat far more robustly (39 % raw FP at n=250; not enriched at
the bar) and (ii) yields ~10 marketed drugs whose *single-snapshot* margin exceeds the carried lead
denovo_401's, 4 of them beyond the entire decoy null. These are triage-grade only until multi-snapshot
de-noising (non-FEP) tests whether they survive as 401 did or collapse as 393 did; **FEP is gated and NOT run
here.**

**Caveat carried from the null:** single-snapshot MM-GBSA magnitudes are inflated (no entropy/ensemble);
trust the direction and the above-null flag, not kcal/mol. Any above-null hit is a screening-grade prediction
warranting FEP, not a validated selective binder.

## 5. Multi-snapshot de-noising (10-frame MD ensemble; survivor = mean−SD > 0)
De-noised the 10 single-snapshot hits that beat denovo_401. 6/10 survive; the single-snapshot ranking did
NOT hold (flupentixol +20.54 → mean 6.80, mean−SD +2.11). Ranked by mean−SD:

| drug | MoA | mean ± SD | mean−SD | outcome |
|---|---|---|---|---|
| **AGI-5198** | IDH1 inhibitor | 16.36 ± 4.32 | **+12.04** | SURVIVES — exceeds denovo_401 (+9.85) |
| ML786 | RAF inhibitor | 16.75 ± 8.16 | +8.59 | survives (large SD; kinase-promiscuity) |
| CP-640186 | ACC inhibitor | 8.05 ± 4.32 | +3.73 | survives |
| DDR1-IN-1 | DDR1 kinase inh | 8.52 ± 5.24 | +3.28 | survives |
| flupentixol | antipsychotic | 6.80 ± 4.69 | +2.11 | survives (weak; was +20.54 single-snap) |
| BMS-309403 | FABP inhibitor | 5.69 ± 5.19 | +0.50 | survives (marginal) |
| pizotifen | serotonin antag | 3.94 ± 4.41 | −0.47 | collapsed |
| 20-hydroxyecdysone | ecdysone mod | 4.49 ± 6.24 | −1.75 | collapsed |
| SNX-5422 | HSP90 inhibitor | 6.39 ± 9.46 | −3.07 | collapsed |
| pyrantel | nicotinic agonist | 0.47 ± 7.21 | −6.74 | collapsed |

**Standout (single-pass): AGI-5198** appeared to *strengthen* under de-noising to mean−SD +12.04. **⚠ But a
single 10-frame de-noising pass is NOT reproducible run-to-run** (see §5b) — that +12.04 did not replicate — so
this table is a *within-run* snapshot, not the honest readout.

## 5b. The single-pass de-noising is not reproducible — pivot to between-run replicates (2026-07-09)
Re-running the identical 10-frame de-noising on the same drugs swung margins several kcal/mol in both
directions (**AGI-5198 +16.36 in the §5 pass vs +6.37 in a second pass**; others similar). The cause is
structural: the 10 frames come from **one continuous, autocorrelated GB-MD trajectory**, so the *within-run*
SD (the ±SD in §5) reflects only intra-trajectory jitter and **understates the true run-to-run uncertainty**.
A "mean−SD > 0" survivor call from one trajectory is therefore a lucky-draw risk, not a robust result.

**Fix (the standard denovo_401 was already held to).** denovo_401 earned "lead" precisely by surviving
**independent** replication — multi-snapshot **+12.83 ± 2.98**, reproduced in an independent-seed pass at
**+14.75 ± 4.82** (recorded in `nr4a3-degrader-preprint.md` §2.6), "so not a single-draw artifact." We now
hold the repurposing hits to that same bar: run **3 independent de-noising replicates** (independent MD
velocity draws → separate output prefixes `nr4a3-repurpose-mmgbsa-rep1/2/3`) and report the **between-run
mean ± SD**; survivor = between-run mean − SD > 0. Shortlist = the 6 single-pass survivors
(AGI-5198, ML786, CP-640186, DDR1-IN-1, flupentixol, BMS-309403) **plus 4 collapse-controls**
(pizotifen, SNX-5422, 20-hydroxyecdysone, pyrantel) — so the replicate test is shown to *discriminate*
(controls should stay collapsed), not merely destroy. Report tier: `report_repurpose_selectivity.py`
`MODE=REPLICATE`. **Status: 3 replicate jobs dispatched 2026-07-09 (in flight).** The 7 IDH-class inhibitors
get the same 3-replicate treatment once their first-pass dock/MM-GBSA lands. FEP remains gated (not run).
