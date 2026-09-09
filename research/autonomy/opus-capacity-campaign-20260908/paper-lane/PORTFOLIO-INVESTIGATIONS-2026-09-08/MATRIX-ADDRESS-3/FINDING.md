---
id: DOC-PORTFOLIO-INVESTIGATION-MATRIX-ADDRESS-3
title: "MATRIX-ADDRESS-3 — the k>=6 / k>=10 re-run would recover no additional gene from held data; the recovery is entirely a reference-route question"
level: L4
kind: investigation
status: complete
date: 2026-09-09
last_verified: 2026-09-09
---

# MATRIX-ADDRESS-3 — pricing the relaxed-intersection re-run without the closed reference route

Worker: third-round portfolio investigation lane, campaign `OPUS-CAPACITY-CAMPAIGN-20260908`.
Checkout `/home/user/Rare-cancers`, branch `claude/confident-bardeen-ji76cd`,
HEAD `90de330ba28dfe098159c4860a00fe03709dc3ea` (recorded in `checks/01`).
Read-only outside this directory. No network of any kind, no CI, no GPU, no paid API, no
`preflight.sh`, no `git add/commit/push`, no subagents. No shared file is changed and no diff is
proposed. **Routes B1/B2 (Ensembl cDNA/ncRNA) were not attempted, retried, proxied around or
substituted**, and no HTTP request was issued from this lane.

## 0 · Question

MATRIX-ADDRESS-2 measured that the fourth EMC cohort's 862-gene ceiling is imposed by our own
all-12-runs strict intersection, and named the next step as a CPU-only re-run of the committed
matcher `research/modalities/emc_fourth_cohort_quant.py` at k >= 6 and k >= 10.

**Exactly what would that re-run recover — and how much of it can be had without the closed
Ensembl route?**

## 1 · Merit rationale

The programme currently reads this cohort's 862-gene table as if it were the instrument. Round two
showed the ceiling is a processing choice and left the recovered gene count explicitly UNKNOWN,
with an arithmetic projection (order 8,900 assigned probes at k >= 6) flagged as a projection. An
UNKNOWN of that size is a standing invitation to plan on the projection. Converting it into an
exact figure — how many extra probes are labellable from what is already committed, and how many
are not — costs seconds of CPU, needs nothing that is closed, and either unlocks the cohort at zero
cost or prices the closed dependency precisely. It bears on patients only indirectly, through
whether this deposit can answer questions at all; it makes no claim about EMC.

## 2 · Exact evidence gap

Round two measured probe **persistence**; it did not open the gene-label side. Two committed
label sources exist and only one of them was used by round two:

* `research/modalities/emc-fourth-cohort-probe-counts.tsv` — `assigned_gene` column, **906** rows.
* `research/modalities/emc-fourth-cohort-quant-inputs.json` — `probe_map.probe_to_gene` (**906**)
  **and `probe_map.probe_to_several_genes` (77)**, the latter absent from the TSV entirely.

And the matcher's assignment rule has a part that needs **no reference at all**: it forms 50/42/34-nt
cores at trims 0/4/8, indexes each core **and its reverse complement**, and reads the gene off the
transcript matching at the best core length (recorded: **34 nt**). Two probes sharing a core match
the same transcript. **Whether any of the k >= 6 / k >= 10 probes share a core with an already-
labelled probe is a countable property of committed files.** That is the gap.

## 3 · Step taken

### 3a · Independent re-derivation of round two's rarefaction — no discrepancy

Round two verified its Python against `awk`. I re-ran **both of those unchanged** and added **two
further routes sharing no code with either**:

* **Route C — set union, no per-row arithmetic** (`cut` + `grep` + `sort` + `uniq` only): for each
  of the 12 run columns, extract the probe ids with a non-zero count in that column; concatenate;
  `sort | uniq -c` gives each probe's run multiplicity directly.
* **Route D — Perl streaming reimplementation** of both the probe counts and the read shares.

**All four routes agree digit for digit on all twelve rungs**, and the re-run of round two's Python
reproduced its committed JSON artifact **byte for byte** (`diff` → IDENTICAL). Route C independently
recovers the exact-k histogram (162,981 probes at k = 1 … **1,645 at k = 12**) and 400,479 persisted
(probe, run) pairs. k = 12 → **1,645**, read share **0.351112**; k >= 10 → **5,856**, **0.525211**;
k >= 6 → **16,222**, **0.663989**; 213,007 rows, 67,890,929 persisted reads. **No rung disagrees.**

### 3b · What the re-run needs, and what part of it ran here

`emc_fourth_cohort_quant.py::map_probes_to_genes` obtains its reference **only** by
`urllib.request.urlopen` against `https://ftp.ensembl.org/pub/current_fasta/homo_sapiens`
(`cdna`, then `ncrna`; the committed record shows 465,769 + 203,778 transcripts and 1.48 Gbp
scanned in 574.6 s). **There is no local cache and no local transcriptome anywhere in the
checkout** — the only FASTA in the tree is `research/manuscripts/aso/fusion-junction-aso-sequences.fasta`,
which is ASO material, not a reference (`checks/03`). So the *reference* half of a k >= 6 re-run is
route B1/B2 and is closed. I did not attempt it.

The *core-identity* half needs no reference, so I ran it:
`relaxed_k_label_recovery.py` → `relaxed-k-label-recovery.json` (`checks/05`).

## 4 · Result — exact, and negative

**Committed label inventory: 983 distinct probes** (906 single-gene + 77 multi-gene), and
**every one of them sits at k = 12** — measured, not assumed (`⛔ every_one_of_them_sits_at_k: [12]`).

| threshold | probes | read share | already labelled | not labelled | labelled by core identity, no reference | still UNKNOWN | best-case gene count from held data |
|---|---|---|---|---|---|---|---|
| k = 12 | 1,645 | 0.351112 | 983 | 662 | **67** | 595 | **862** |
| k >= 10 | 5,856 | 0.525211 | 983 | 4,873 | **172** | 4,701 | **862** |
| k >= 6 | 16,222 | 0.663989 | 983 | 15,239 | **402** | 14,837 | **862** |

> **The k >= 6 / k >= 10 re-run recovers ZERO additional genes from data held in this checkout.**
> Core identity does label **402** of the 15,239 unlabelled k >= 6 probes (**2.64 %**) and **172** of
> 4,873 at k >= 10 (**3.53 %**) — all at the 34-nt core, both strands — but every gene they inherit
> is **already one of the 862**. `distinct_single_genes_added_by_core_identity = 0` at every
> threshold. **14,837 of 16,222 probes at k >= 6 (91.46 %) stay UNKNOWN**, and only the closed
> reference route can decide them.

So the useful figure is not a bigger gene table but a **price**: relaxing the intersection is free
and already done, while **converting it into genes is 100 % a reference-route purchase**. Round
two's projection ("order 8,900 assigned probes at k >= 6") is neither confirmed nor refuted here; it
remains a projection, and this lane shows the held data cannot move it at all.

**Two incidental measurements, both preserved rather than acted on.**

1. **A real artifact of the committed matcher, not a defect I may fix.** `_core_sets` builds its core
   dict with `d.setdefault(core, p)`, so when two probes share a 34-nt core only the first is
   credited. **67 of the 662 probes the matcher called `unassigned` at k = 12 are core-identical
   (or reverse-complement-identical) to a probe it did assign** — their gene is in fact determined
   by evidence already held. This changes no gene count (all 67 inherit existing genes) and I
   changed no matcher, guard or pin; it is reported as an unapplied observation only.
2. **The extra probes are mostly NOT sequencing-error halo.** Against the k = 12 set, only
   **1,720 / 15,239 (11.29 %)** of the extra k >= 6 probes lie within Hamming distance 1 and a
   further **41 (0.27 %)** at distance 2 — **11.56 % within distance 2**; at k >= 10,
   **596 + 14 = 610 / 4,873 (12.52 %)**. So roughly seven in eight of the probes a majority rule
   admits are genuinely distinct sequences rather than one-base variants of the strict set. That is
   **consistent with** round two's conclusion that the panel is not small — it does not prove they
   are panel members, because an unmatched sequence could still be an adapter, a chimera or a
   multi-error read, and nothing here can tell which. **Projection, not measurement.**

**Nothing above says any compartment marker would return.** `PECAM1` and the other 47 unread
markers remain exactly as unread as round one found them, and the 6/53 figure is unchanged.

## 5 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `relaxed_k_label_recovery.py` (deterministic, stdlib only, aborts if the input hash
disagrees with the producer's record, issues no network call) and
`relaxed-k-label-recovery.json`; `checks/01`–`checks/05`, each with `command.txt`, `stdout.txt`,
`stderr.txt`, `exit_code.txt`.

**Validation / baseline.** (i) Four independent routes over the rarefaction agree on all twelve
rungs; the re-run of round two's own program reproduces its committed artifact byte for byte.
(ii) k = 12 → 1,645 reproduces the producer's separately recorded
`n_probes_common_to_every_read_run`, an anchor no program here was fitted to. (iii) The core-identity
step reproduces the matcher's own recorded `best_core_length_nt = 34` as the length that
propagates every label, and the 983-probe inventory reconciles exactly with the recorded
906 + 77 = 983 matched probes at the 34-nt core. (iv) The probe-table sha256 was recomputed and
matched (`c689e0fd…d26fc`) before any counting.

**Provenance.** Committed paths at HEAD `90de330b`: `emc-fourth-cohort-probe-counts.tsv`,
`emc-fourth-cohort-quant.json`, `emc-fourth-cohort-quant-inputs.json`, `emc_fourth_cohort_quant.py`
(read only). Nothing outside this lane directory was written.

**Limitations.** (1) A zero in the probe table means **not persisted**, not observed-zero — the
producer's own caveat — so every threshold statement is about lossy counting, not about transcript.
(2) An unlabelled probe is **UNKNOWN**, not unassigned and not off-panel. (3) The Hamming
diagnostic is a projection about sequence relatedness, not an identification. (4) No gene beyond
the committed 862 is named, no expression value read, no arm contrast, score or p-value computed.
(5) Read share is over persisted reads (67,890,929), not over all reads sequenced.
(6) **Nothing here is a measurement of EMC.** No delivery, accessibility, efficacy, selectivity,
safety, therapeutic-window or clinical-readiness claim follows from any line of it, and none is made.

**Compute and storage actually used.** Whole lane: **CPU only, four cores available, one used**.
`relaxed_k_label_recovery.py`: **1.47 s wall, 1.18 s user + 0.08 s sys, 83,020 KiB peak RSS**
(`checks/05/stderr.txt`). The four rarefaction routes are single passes over the 18.8 MB table
(route C makes 12 column passes plus one 400,479-line sort); all completed in seconds.
**No network bytes, no GPU-seconds, no paid API calls, $0.** Storage written: this lane directory
only, **132 KiB measured by `du -sh`**, no temporary file larger than the 400,479-line id list in `/tmp` (deleted by the
script that made it). No repo copy, no worktree.

**Stop condition (pre-set, and met).** Stop when either (a) a rung of round two's rarefaction fails
to reproduce — report it digit for digit and stop; or (b) the exact number of k >= 6 / k >= 10
probes labellable from committed data alone is measured, with the residue named UNKNOWN rather than
projected. (a) did not fire: all four routes agree. (b) is met: 402 / 172 labellable, 0 new genes,
14,837 / 4,701 UNKNOWN. The pre-set branch "if labelling the residue needs the Ensembl route, stop
at the boundary rather than crossing it" **fired and was obeyed**.

**Next credible independent work, not attempted here.** The only remaining step is the reference
purchase itself: run the committed matcher's `map_probes_to_genes` over the 16,222-probe k >= 6 set
against the human cDNA + ncRNA sets. It is CPU-only and costs no money, but it needs a route this
lane may not open, and it is now priced exactly: **14,837 probes carrying 31.29 percentage points
of persisted reads hang on it, and nothing short of it moves the gene count off 862.** Until it is
done, the graph's implicit "862 genes" remains a property of one processing choice **and** of one
closed reference route — not of the deposit.
