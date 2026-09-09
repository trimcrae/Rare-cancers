---
id: DOC-PORTFOLIO-INVESTIGATION-KINASE-2-PREREG-2026-09-09
title: "KINASE-2 — analysis constants declared before any number was computed"
level: L4
kind: preregistration
status: frozen
date: 2026-09-09
lane: KINASE-2
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# Declared before the run (written 2026-09-09T00:11Z, before any permutation was executed)

Input, sole and committed: `research/modalities/emc-expression-panels.json`
(`generated_utc` 2026-08-29T12:51:32+00:00). Byte-identical between lane PUB-KINASE-LEADS's
baseline HEAD `b6baa1b7` and this lane's HEAD `a11a1ea7` (`git diff` over that path is empty),
so both nulls are built on exactly the same numbers.

* **Permutations: `N_PERM = 2000`.**
* **Seed: `SEED = 20260909`** (`numpy.random.default_rng(20260909)`).
* **Permutation scheme:** within each platform independently, the EMC / comparator labels are
  reassigned at random over that platform's labelled samples, holding the arm sizes fixed
  (GPL6244 6 EMC / 29 comparator; GPL3290 10 EMC / 6 comparator). Samples of neither arm stay out.
  Missing values stay attached to their sample, so each gene's missingness pattern is preserved.
* **Primary frame:** the 431 genes drawn into *both* committed random background samples — the same
  frame lane PUB-KINASE-LEADS used, so the two nulls differ only in what is randomised.
* **Secondary frame:** the 414 curated `gene_reads` genes readable on both platforms (per-sample z
  is committed for these), as a sensitivity check.
* **Statistics fixed in advance:** (1) direction-concordance rate of the frame; (2) joint empirical
  p for each lead gene = fraction of null draws that are concordant in direction AND at least as
  strong on the weaker platform; (3) Pearson and Spearman correlation of t across the frame between
  the two platforms.
* **Lead genes placed:** the same fourteen lane PUB-KINASE-LEADS placed — RET, SGK1, NDRG1, ALK,
  ROS1, PRKDC, XRCC5, XRCC6, NR4A3, EGFR, GFRA1, GFRA2, GDNF, HDAC3.
* **No outcome is preferred.** A permutation concordance near 65% and a permutation concordance
  near 50% are both reported as found, and the FINDING states which of lane PUB-KINASE-LEADS's
  conclusions each would strengthen or weaken.
* **Stop condition:** stop once both nulls are computed on the primary frame, the recomputed
  observed statistics reproduce lane PUB-KINASE-LEADS's published values exactly, and the secondary
  frame either reproduces or breaks the primary headline. Stop immediately and report the
  discrepancy instead if the observed statistics fail to reproduce.
