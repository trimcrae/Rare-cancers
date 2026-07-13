# NR4A3-selective degrader — weekly field-scan log

Dated summaries of new/relevant literature + methods for the in-silico NR4A3-degrader program (EMC /
EWSR1::NR4A3). Produced by the weekly field-scan Routine (Mon 8 AM ET), or manually when that run fails.
Sources are real search hits; novelty/dating is flagged where it couldn't be verified. No fabricated papers.

---

## 2026-07-13 (Mon) — MANUAL catch-up

> ⚠ The automated Routine fired at 8:03 AM ET but delivered no email and no commit; a 9:20 AM ET re-fire also
> failed to produce this branch. This entry was produced **by hand** in the working session, so it reflects the
> **current landscape**, not strictly the past 7 days (arXiv IDs date items to 2025–2026). The Routine needs a
> durable fix (its fresh-session env is failing before completion).

**This week's takeaway:** Quiet week for brand-new NR4A/EMC biology, but two things touch the plan: (1) **Boltz
2.1 is now closed-source / API-only** — our co-fold generator stays pinned to open Boltz-1/-2; and (2) a cluster
of **ternary / molecular-glue cooperativity free-energy papers** is exactly the prior art our Track B ΔG_coop
method must cite and benchmark against.

### 1) METHOD-WATCH (plan-relevant — top priority)
- **Boltz 2.1 → closed-source, API-only (reported June 2026).** Our open co-fold path stays on Boltz-1/-2
  (open weights); 2.1's affinity gains are not self-hostable. No change to the "generator never ranks
  selectivity" rule. ⚠ verify current license before relying on it.
  https://rowansci.com/tools/boltz-2 · https://www.biorxiv.org/content/10.1101/2025.06.14.659707v1
- **Independent Boltz-2 reliability evaluation (arXiv 2603.05532, ~Mar 2026).** Boltz-2 is a strong binary
  classifier but weak at *quantitative* affinity ranking — supports our stance that generator scores never
  enter S_d. https://arxiv.org/html/2603.05532v1
- **"Cooperative Free Energy: Induced PPI + Cooperative Solvation in Ternary Complexes" (JCTC 5c00736).**
  Pathway-independent cooperativity FEP decomposition — direct prior art for our ΔG_coop method; cite +
  benchmark against. https://pubs.acs.org/doi/10.1021/acs.jctc.5c00736
- **"Quantifying Cooperativity through Binding Free Energies in Molecular Glue Degraders" (JCTC 5c00064 /
  PMC12159975).** Glue-cooperativity FEP benchmarked to experiment — same relevance.
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12159975/
- **Additional architecture-proposal generators for the breadth-first list:** IntFold (arXiv 2507.02025, a
  controllable co-folding foundation model) and PROflow (arXiv 2405.06654, iterative PROTAC-structure
  refinement) — evaluate alongside Boltz + DeepTernary; never as rankers.
  https://arxiv.org/pdf/2507.02025 · https://arxiv.org/pdf/2405.06654

### 2) NR4A / EMC
- No new NR4A3 / EMC primary papers surfaced this week. **NR-V04** (JEM 2024) remains the central positive
  control (NR4A1-selective; spares NR4A2/3) — https://rupress.org/jem/article/221/3/e20231519/276559/ .
  EMC dual-fusion case (EWSR1::NR4A3 + HAPLN1::EDIL3, 2024) noted —
  https://www.sciencedirect.com/science/article/pii/S2772736X24000306 . Standing structural note unchanged:
  NR4A LBDs show no canonical open pocket (bulky hydrophobic fill), consistent with our cryptic-pocket premise.

### 3) Degrader methodology (context / references)
- **"Targeted Protein Degradation in the Digital Era" review (ScienceDirect, 2026)** — computational TPD
  challenges/opportunities; useful manuscript-intro framing.
  https://www.sciencedirect.com/science/article/pii/S3050787126002015
- Standing ternary references: JCIM end-point cooperativity BFE
  (https://pubs.acs.org/doi/10.1021/acs.jcim.4c01227) and the JCIM PROTAC-ternary-prediction benchmark
  (https://pubs.acs.org/doi/10.1021/acs.jcim.4c00426).

**Action items for the program:** add the two JCTC cooperativity-FEP papers + the TPD review to
`method-watch.md` prior-art; keep Boltz pinned to open weights; queue IntFold as a candidate second/third
co-fold generator to evaluate after DeepTernary Step-3 completes.
