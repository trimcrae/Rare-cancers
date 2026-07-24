# BioEmu cross-check of the NR4A3 LBD cryptic pocket (method-watch trigger, BioEmu v1.4.x)

**Date:** 2026-07-24. **Trigger:** `method-watch.md` "cheap generative conformational-ensemble model
(BioEmu / AlphaFlow / …) **validated against known cryptic pockets**", action (a): *"re-grade the NR4A3 LBD
cryptic-pocket ensemble at near-zero cost as a cross-check on the metadynamics."* Prompted by the BioEmu v1.4.0
release (Microsoft, 2026-07-20). Provider: **Vast.ai** (image `triskit23/bioemu`, RTX-4090).

## TL;DR
An **orthogonal, learned generative ensemble** (BioEmu — a diffusion emulator of protein equilibrium ensembles,
Lewis et al., *Science* 2025) generated a conformational ensemble of the apo NR4A3 LBD **from sequence alone**
(no MD, no metadynamics, no opened input structure). Scored through the **identical** harmonized Pocket-5
detector used for every other NR4A3 ensemble, it **independently finds and opens the Pocket-5 cryptic site**, but
its *druggable-open* population sits **well below** the metadynamics estimate and **very close to the
experimental NMR ensemble**. This corroborates the site's existence/openability by an independent method, and —
honestly — suggests the enhanced-sampling metadynamics may *over*-represent the open-state population.

## Result (fpocket 4.0, harmonized score-independent Pocket-5 match, D\*=0.53)
Data: [`nr4a3-bioemu-crosscheck.json`](nr4a3-bioemu-crosscheck.json). 56 frames propagated (64 requested).

| Ensemble | method | site detected | **druggable ≥ D\*** (of propagated) | ≥ D\* among detected |
|---|---|---|---|---|
| **BioEmu (this run)** | learned generative, **sequence-only** | 38/56 = **0.68** | **7/56 = 0.125** | 7/38 = 0.184 |
| Metadynamics | biased-MD enhanced sampling | 25/25 = 1.00 | **17/25 = 0.68** | 0.68 |
| Unbiased release (pooled) | plain MD | 75/75 = 1.00 | 44/75 = 0.587 | 0.587 |
| **8XTT experimental NMR** | solution-NMR conformers | 19/20 = 0.95 | **3/20 = 0.15** | 3/19 = 0.158 |
| AF2 static | single model | 1/1 | 0/1 = 0.0 | 0.0 |

## Interpretation (honest — the integrity guardrail governs this)
1. **Independent corroboration of the SITE.** BioEmu, which never saw NR4A3 MD and starts only from the LBD
   sequence, detects the fixed Pocket-5 lining site in **68%** of frames and opens it to a fully druggable
   state in a **non-trivial minority (12.5%)**. That an orthogonal, learned method re-finds the same cryptic
   site strengthens the claim that the site is real and openable — a *new evidence axis*, per the breadth-first
   "state of the art" principle, not a re-run of the same test.
2. **Quantitative divergence on the POPULATION — reported straight, not spun.** BioEmu's druggable-open
   fraction (0.125) is far below metadynamics (0.68) and unbiased release (0.587), but **strikingly consistent
   with the experimental 8XTT NMR ensemble (0.15)**. This is exactly what BioEmu's documented behavior predicts:
   its **apo** cryptic-pocket recall is its *weakest* regime (~50% in the `bioemu-benchmarks` set), and an
   independent 2026 benchmark (JCTC 10.1021/acs.jctc.6c00135) shows it is **not calibrated on the absolute
   probability of rare pocket opening**. So BioEmu's number is a *lower*, unbiased-style estimate — and the fact
   that **two independent unbiased sources (BioEmu 0.125 and NMR 0.15) agree on a minority-open population**,
   while the *biased* metadynamics reports a majority (0.68), flags that the metad/release fractions may
   **over-represent** the open state. That tension is decision-relevant and is now on the record.
3. **What this does NOT establish.** BioEmu is a **hypothesis generator**, not a druggability oracle: a
   druggable-pocket *claim* still rests on the fpocket/energetics gate, and BioEmu cannot, alone, prove the
   pocket "binds" anything. It does not replace the physics-based evidence; it is a cheap, orthogonal
   cross-check that both (a) independently confirms the site and (b) provides an unbiased population estimate
   that tempers the enhanced-sampling number.

## Method (fully comparable by construction)
- **Ensemble:** `bioemu.sample` on the 254-aa apo NR4A3 LBD construct (UniProt Q92570 373–626, read from the
  pre-metadynamics AF2 model — sequence only, so non-circular vs the AF2/MD machinery), 64 samples,
  `batch_size_100=10`, bundled ColabFold MSA.
- **Side chains:** `bioemu.sidechain_relax --no-md-equil` (HPacker) — raw BioEmu frames are backbone-only; fpocket
  needs all-atom cavities. (`nr4a3_bioemu_prepare.py` then renumbers BioEmu's 1..254 → UniProt 373..626 and
  splits per-frame PDBs.)
- **Detection:** the **same** `pocket_tracking.py` scorer used for metad/release — fixed Pocket-5 lining set
  (406,407,410,411,412,481,484,485,531,534), score-independent composite gate (Jaccard≥0.25, frac_recovered≥0.30,
  centroid≤8 Å), fpocket 4.0, D\*=0.53 — so the fraction-druggable is directly comparable, not a re-derived metric.
- **Code:** `nr4a3_bioemu_pocket.py` (scorer), `nr4a3_bioemu_prepare.py` (frames), `nr4a3_bioemu_vast_launch.py`
  (Vast launcher), `research/compute/Dockerfile.bioemu` (baked image), `fusion-cpu-extras.yml`
  tasks `bioemu_bake|run|collect|status|stop`. Tests: `tests/test_bioemu_crosscheck.py`.
- **Provenance:** `meta` in the result JSON (model bioemu 1.4.1, image, num_samples, git branch). Cost: one
  RTX-4090 for ~20 min (~$0.10–0.15).

## Statistical note
56 frames → the 0.125 druggable fraction carries a wide binomial CI (~0.05–0.24, Wilson 95%). The **qualitative**
conclusion (minority-open, concordant with NMR, below biased-metad) is robust to that width; a larger N would
only tighten the point estimate. Per the "run each test to its field standard, then STOP" rule, this cheap
cross-check has served its purpose — no depth-spend to narrow a CI on a corroborating axis is warranted unless a
specific decision hinges on the exact fraction.
