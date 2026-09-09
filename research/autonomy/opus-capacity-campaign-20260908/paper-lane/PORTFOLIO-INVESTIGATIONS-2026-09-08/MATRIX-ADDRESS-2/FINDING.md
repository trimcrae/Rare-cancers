---
id: DOC-PORTFOLIO-INVESTIGATION-MATRIX-ADDRESS-2
title: "MATRIX-ADDRESS-2 — the fourth EMC cohort's compartment blindness is dominantly a processing choice, not the assay panel"
level: L4
kind: investigation
status: complete
date: 2026-09-09
last_verified: 2026-09-09
---

# MATRIX-ADDRESS-2 — attributing the fourth cohort's 862-gene ceiling

Worker: second-round portfolio investigation lane, campaign `OPUS-CAPACITY-CAMPAIGN-20260908`.
Checkout `/home/user/Rare-cancers`, branch `claude/confident-bardeen-ji76cd`,
HEAD `7b6c2c41dc8b032ebb9aca4238f3c242f704748e` (recorded in `checks/01`).
Read-only outside this directory. No network, no CI, no GPU, no paid API, no `preflight.sh`,
no `git add/commit/push`, no subagents. No shared file is changed and no diff is proposed.

## 0 · Question

Round one (`PUB-MATRIX-ADDRESS`) measured that the EMC-dedicated fourth cohort
(`PRJNA1357027` / `SRP640302`) reads **6 of 53** compartment markers — **0/11 endothelial,
0/5 transport** — and named three candidate causes it declared **"not separable from committed
files"**: the assay panel, the common-probe intersection, or the gene matcher. It routed the
separation to a retrieval task (the deposit's probe manifest) under someone else's authorisation.

**Is that separation really unavailable locally — and if not, which cause dominates?**

## 1 · Merit rationale

The fourth cohort is the deposit whose arrival retired `BLK-NO-EMC-DATA`; it is the only EMC-
dedicated expression instrument this repository holds, and its 862-gene ceiling is the binding
constraint on every question anyone would put to it, not only the compartment one. If that
ceiling is a property of the **assay**, it is permanent and the cohort is simply a small panel.
If it is a property of **our own quantification**, it is repairable at zero cost with no new data,
no fetch and no authorisation — and the ceiling currently recorded in the graph understates what
this cohort can support. Distinguishing those is cheap, decisive, and load-bearing for a
programme that has been reasoning from the 862-gene table as if it were the instrument.

## 2 · Exact evidence gap

Round one read `emc-fourth-cohort-gene-counts.tsv` (862 rows). It did **not** open
`emc-fourth-cohort-probe-counts.tsv` — **213,007 rows, 18.8 MB, committed at HEAD**, holding the
per-run persisted count of every probe sequence, not just the intersected 1,645. The producer's
record states it offered the matcher only `n_probes_in_every_read_run = 1645`. Whether that all-12
rule, rather than the panel, is what caps the table is a **countable property of a committed file**.
That is the gap, and it needs nothing that is closed.

## 3 · Step taken — and first, re-derivation of round one

**Every round-one number I rely on was re-derived from the underlying artifact
(`checks/01-rederive-round1`) and reproduces digit for digit:**

* `emc-fourth-cohort-gene-counts.tsv` sha256 = `8aa3064a97a496a8fa09ef4ae8e472a612318e49ea91d0daac915a3b8fa180cc` — matches the recorded hash.
* `emc-fourth-cohort-probe-counts.tsv` sha256 = `c689e0fd4f5c8cda0f132cd8ce42f039f691bf94cb8d81d3f622886e2bdd26fc` — matches.
* Gene table rows **862**; probe table rows **213,007**; assigned probe rows **906**; distinct assigned genes **862** — all match the record.
* Per-panel marker presence in the gene table: endothelial **0/11**, transport **0/5**, immune **1/10** (`CSF1R`), fibroblast **1/9** (`COL1A1`), mural **2/7** (`NOTCH3`, `CSPG4`), hyaluronan **2/11** (`CD44`, `VCAN`) — **total 6/53**, exactly round one's figure.
* Positive control reproduces: `ACTB` present, `GAPDH` absent.

*`checks/01` exits **1**, honestly: its final command is `grep -cx GAPDH`, which finds zero matches
and returns 1. That is the preserved real exit code, not a failure of the check.*

**New measurement.** `probe_intersection_rarefaction.py` reads the 213,007-row probe table and,
for k = 1…12, counts the probe sequences persisted in **at least k** of the 12 runs and the share
of all 67,890,929 persisted reads they carry. Output: `probe-intersection-rarefaction.json`.

| probe persisted in ≥ k of 12 runs | probes | share of persisted reads |
|---|---|---|
| **12 (the rule actually used)** | **1,645** | **0.3511** |
| 11 | 3,639 | 0.4584 |
| 10 | 5,856 | 0.5252 |
| 8 | 10,910 | 0.6200 |
| **6 (majority)** | **16,222** | **0.6640** |
| 1 | 213,007 | 1.0000 |

k = 12 returns **exactly 1,645**, independently reproducing the producer's recorded
`n_probes_common_to_every_read_run`, and that set contains **all 906** assigned probes.

## 4 · Result

> **The 1,645-probe ceiling is imposed by the all-12-runs intersection, not by the assay panel.**
> Relaxing the rule to a majority (≥6 of 12) admits **16,222** probe sequences — **9.9×** more —
> carrying **66.4%** of persisted reads instead of **35.1%**. Even ≥10 of 12, a strict rule,
> admits **5,856** probes (3.6×) and **52.5%** of reads. The current table is built from
> **just over a third of the cohort's own sequenced signal.**

This **falsifies "the panel is small" as the dominant explanation.** Individual runs persist a
median of **35,134** sequences (range 19,019–39,456), and 16,222 survive a majority rule — the
order of magnitude of a whole-transcriptome templated-ligation panel, consistent with the
depositors' description. The collapse to 1,645 is what happens when a strict intersection meets a
**lossy-counting persistence cap that drops different low-count probes in different runs**: it is
an artifact of our own pipeline's conjunction of two choices, and it is the reason the cohort
looks like a 862-gene panel.

**What this does NOT establish, and the boundary matters.** It does **not** show that `PECAM1` or
any other marker would be recovered by relaxing k. Turning the extra probes into genes requires
matching their sequences to a human transcriptome — the Ensembl cDNA/ncRNA route (**B1/B2**), which
is **closed** and which I did not attempt or work around. All 906 assignments sit at k = 12, so the
committed data carry **no** gene label for a single one of the additional probes. The arithmetic
extrapolation (906/1,645 = 55.1% assignment rate → order 8,900 assigned probes at k ≥ 6) is a
**projection, not a measurement**, and higher-persistence probes are plausibly easier to match, so
it is not even an unbiased one. **The recovered gene count is UNKNOWN, not estimated.**

**Consequence for round one's routing.** Round one sent the separation out as a retrieval task
needing the deposit's manifest. That is now only **half** right: the *panel-versus-intersection*
question is settled locally and negatively for the panel, and the remaining step —
re-running the existing, committed matcher `emc_fourth_cohort_quant.py` at k ≥ 6 or k ≥ 10 — is a
**CPU-only re-quantification against an already-permitted reference route**, not a new acquisition.
Whether that route is currently open is a question for whoever owns it; it is not this lane's to
open, and I did not.

**Round one's paper-level conclusion is unchanged.** The compartment premise remains untestable on
what is held: the two arrays still have the markers without an admissible comparison, and this
cohort still reads 6/53 **today**. This lane changes the *cause*, the *cost*, and the *owner* of
the fix — nothing about EMC.

## 5 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `probe_intersection_rarefaction.py` (deterministic, no network, aborts if the input
hash disagrees with the producer's record); `probe-intersection-rarefaction.json`;
`checks/01-rederive-round1`, `checks/02-rarefaction`, `checks/03-awk-independent-verify`, each with
`command.txt`, `stdout.txt`, `stderr.txt`, `exit_code.txt`. Three attempts, none discarded, none
overwritten; exit codes 1, 0, 0 as actually returned.

**Validation / baseline.** (i) The full rarefaction was re-derived by a single `awk` pass sharing
no code with the Python, agreeing on **all twelve rungs** to six decimal places
(`checks/03`). (ii) The k = 12 rung reproduces the producer's independently recorded 1,645, an
external anchor neither program was fitted to. (iii) The k = 12 set contains exactly the 906
assigned probes, confirming the intersection is the set the matcher was offered. (iv) Both input
hashes recomputed and matched before any counting.

**Provenance.** Two committed paths at HEAD `7b6c2c41`, both hash-verified:
`research/modalities/emc-fourth-cohort-probe-counts.tsv` and
`research/modalities/emc-fourth-cohort-quant.json`. Nothing else was read for the measurement, and
nothing outside this lane directory was written.

**Limitations.** (1) A zero in the probe table means **not persisted**, not observed-zero — the
producer's own caveat — so presence-in-k-runs is a statement about lossy counting, not about
transcript, and the rarefaction is not a detection curve. (2) No gene is assigned, no expression
value read, no arm contrast, score or p-value computed; the withdrawn Lane-2 statistics are not
touched or re-opened. (3) The recovered **gene** yield at relaxed k is UNKNOWN (see §4).
(4) Read-share is over **persisted** reads (67,890,929), not over all reads sequenced.
(5) **Nothing here is a measurement of EMC.** No claim about vasculature, matrix, accessibility,
delivery, efficacy, selectivity, safety, therapeutic window or clinical readiness follows from any
line of it, and none is made.

**Stop condition (pre-set, and met).** Stop when the all-12 intersection's contribution to the
1,645-probe ceiling is quantified from committed files, independently re-derived by a second code
path, and anchored to the producer's own recorded count — reporting either that the panel or the
intersection dominates, or that the two are genuinely inseparable locally. Met. The pre-set branch
"if separating them would require the closed Ensembl route, stop and report the boundary rather
than crossing it" **did fire**, at the gene-recovery step, and was obeyed: the gene yield is left
UNKNOWN.

**Next credible independent work, not attempted here.** Re-run the committed
`emc_fourth_cohort_quant.py` matcher over the k ≥ 6 and k ≥ 10 probe sets to measure — rather than
project — the recovered gene count and whether any compartment marker returns; this needs the
Ensembl transcript route and belongs to whoever holds that authorisation. Until it is done, the
graph's implicit "862 genes" description of this cohort should be read as **a property of one
processing choice, not of the deposit.**
