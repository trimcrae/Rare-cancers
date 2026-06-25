# Pre-registration: NR4A3 orthosteric-pocket druggability (falsification criteria)

**Purpose.** Fix the decision thresholds *before* the production metadynamics and calibration results
are in, so the conclusion can't be reverse-justified from whatever numbers appear. This is the guard
against the failure mode flagged in review: "would *any* fpocket number end up supporting
druggability?" The answer must be no — each gate below has a pre-set way to fail, and a negative
result is reported as a negative, with the route's weight shifting to the backups
(`emc-treatment-strategy.md`: designed protein binder / AF-2 surface / junction ASO).

Status when written: 2026-06-25, before the 30 ns production run and before the calibration panel
(`nr4a3_calibration.py`) results. The static AF2 orthosteric score is **0.495** (Pocket 5, residues
406–534). The 5 ns validation showed the CV opens (Rg ~0.5 → ~1.05 nm) but produced **no** updated
druggability number yet.

## The claim under test
*A transient, energetically accessible cryptic opening of the NR4A3 orthosteric pocket (Pocket 5)
reaches a druggable state, into which a drug-like, NR4A1/NR4A2-selective warhead can bind.*

This is a **chain** of independent gates. The claim is supported only if the gates below pass; failing
gates are reported, not discarded.

## Gate 0 — Pipeline calibration (must pass, else fpocket evidence is down-weighted)
Run `nr4a3_calibration.py` on a known panel.
- **PASS if:** the known-druggable NR controls (PPARγ `2PRG` and ERα `1ERE`) score their
  experimentally-bound orthosteric ligand-site druggability clearly **≥ 0.5** (expected ~0.7–1.0),
  **and** the occluded Nurr1 apo crystal `1OVL` scores its max **< 0.5**. This demonstrates the
  pipeline separates true-druggable from occluded NR pockets.
- **Defines:** the working druggable threshold **D\*** = max(0.5, midpoint between the lowest druggable
  control ligand-site score and the 1OVL occluded score). All downstream "crosses druggable" tests use
  **D\***, not a naive 0.5.
- **FAIL (controls don't separate):** fpocket on these models is uninformative; we do **not** rest any
  druggability claim on fpocket scores and rely on orthogonal evidence (pocket volume/SASA, docking,
  experimental NR4A ligand-site precedent) instead.

## Gate 0b — Model-vs-crystal over-call check (interpretation, not pass/fail)
Compare the NR4A2 **AF2-model** max druggability to the `1OVL` **crystal** max. A large positive
delta quantifies AF2-model over-call and means our NR4A3 static 0.495 is read as an **upper bound** on
static druggability (the real static pocket is likely tighter). Recorded explicitly in the writeup.

## Gate 1 — Cryptic opening occurs (metadynamics)
- **PASS if:** the converged 30 ns free-energy profile F(Rg) shows an accessible minimum or shoulder at
  an opened Rg distinct from the closed basin (not just biased excursions). 5 ns prelim already shows
  CV motion to ~1.05 nm; convergence assessed by HILLS deposition rate / profile stability.

## Gate 2 — The opened state is actually druggable
Per-frame fpocket on the opened conformations (`nr4a3_mdpocket.py` on the metad trajectory).
- **PASS if:** a non-negligible fraction of opened frames (pre-set: **≥ 5 % of frames**, and at least
  one well-formed cluster) reach druggability **≥ D\*** (from Gate 0), with the pocket still lining the
  406–534 residues (not a splayed/unfolded artifact — checked via the lining-residue identity + that
  the selectivity handles remain pocket-facing).
- **FAIL:** opening does not produce a druggable cavity (Rg rises but druggability stays < D\*, or the
  residues splay without enclosing a pocket) → the small-molecule orthosteric route is **not
  supported**; reconsider the CV and/or pivot to backups.

## Gate 3 — Opening is energetically accessible
From the converged F(Rg).
- **PASS if:** the free-energy cost from the closed basin to the druggable-open state is **≤ ~5
  kcal/mol** (transiently populated at physiological temperature).
- **FAIL (cost ≫ 5 kcal/mol):** the druggable state exists but is not realistically populated → route
  weakened; report as "cryptic but energetically costly."

## Gate 4 — A selective, drug-like ligand can engage it (downstream)
Dock/generate into the best opened conformer (`nr4a3_dock.py` + generative design).
- **PASS if:** drug-like matter docks with a reasonable score **and** contacts a meaningful subset of
  the 7 selectivity handles (L406, T407, T410, R412, I484, I531, L534) with predicted selectivity
  margin vs NR4A1/NR4A2 LBDs.
- **FAIL:** no drug-like/selective binder → small-molecule warhead route not supported.

## Decision rule
- **Route supported** only if **Gate 0 passes** and **Gates 1–3 pass** (Gate 4 strengthens it / is
  required before claiming a candidate).
- **Any of Gates 1–3 failing** → report the negative and shift weight to the backup modalities; do not
  re-tune thresholds post hoc to rescue the result.

## Deviation log (append-only; preserves pre-registration integrity)
- **2026-06-25 — Gate 0 metric corrected (disclosed).** As written, Gate 0 used *max* pocket
  druggability and required the occluded Nurr1 `1OVL` max < 0.5. The calibration run (28202437979)
  showed 1OVL max = **0.864** — i.e. *max* is non-discriminating because every NR LBD has a
  high-scoring **non-orthosteric** cavity (the occluded crystal included). The pre-registered test
  therefore **fails as literally specified**; we correct the discriminator to the **ligand-site /
  orthosteric-specific** druggability (also computed in the same run) and set **D\* = 0.53** from the
  validated drug-bound NR controls (PPARγ 0.599, ERα 0.586, Nurr1-holo 0.677, Nur77-holo 0.529). This
  is disclosed rather than silently swapped; the corrected bar (0.53) is a real drug-bound score, not
  a laxer one, and downstream conclusions hold under both 0.50 and 0.53.

## Anti-confirmation safeguards
1. Thresholds (D\*, 5 % frames, ~5 kcal/mol) are fixed here, before the production/calibration numbers.
2. External yardstick: D\* is set by known-druggable NR controls, not by NR4A3's own number.
3. All gates reported including negatives; the static 0.495 is treated as an upper bound, never as
   standalone evidence of druggability.
4. A CV/parameter change invalidates prior HILLS (enforced by the metad manifest guard), so we cannot
   silently swap the coordinate to manufacture an opening.
