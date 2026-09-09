---
id: DOC-PORTFOLIO-INVESTIGATION-PUB-FUSION-OUTPUT-20260908
title: "PUB-FUSION-OUTPUT lane — can the only fusion-perturbation chromatin experiment test the class-A catalogue, or only illustrate it?"
level: L4
kind: investigation
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# PUB-FUSION-OUTPUT — portfolio investigation, 2026-09-08

Lane scope: fusion-output **biology** and externally testable interpretation. No figure, render or PDF
work was done; the FO estimand adjudication was not reopened. Writes are confined to this directory.
Nothing here is an efficacy, selectivity, safety, therapeutic-window or clinical-readiness statement.

## 1 · The question

The manuscript's interpretive core is that in EMC, "elevated in the tumour" and "driven by the
fusion" are inseparable, and that the three class-A genes (*SEMA3C*, *PPARG*, *ENO3*) are the only
ones with a fusion DNA-binding assay behind them. **Exactly one genome-wide experiment in which an
NR4A3 fusion is the perturbation exists** (GSE243553 / Frenkel *et al.*, doi:10.1038/s41587-024-02347-4;
scATAC of 116 oncofusions in HEK293T). The manuscript uses it only as a bounded caveat and quotes its
peak counts without re-deriving them.

**Question.** Does that external experiment's *own* EWSR1::NR4A3 program contain the class-A genes,
and is that program specific enough to the EMC fusion for a prospective EMC-expression read of it to
be attributable to this fusion rather than to a generic oncofusion accessibility program?

Both halves can come back negative, which is what makes this a test rather than an illustration.

## 2 · Paper-level merit

Patient relevance is indirect but real: every therapeutic argument in EMC runs through "the fusion's
output is where the disease lives", and the catalogue that names that output is three genes. The
contribution is non-trivial because it inverts the usual direction of use — instead of asking whether
an EMC-derived gene set looks elevated (the read §1.1 of the manuscript exists to refuse), it asks
whether a gene set defined **entirely outside EMC, by the fusion itself**, contains the genes the
literature attributes to that fusion. The evidence is attainable: the 32 program BEDs and their frozen,
outcome-independent promoter memberships are already retrieved and hashed in-repository.

## 3 · The exact evidence gap, and how it differs from completed or held work

* Completed: `gse243553-eno3-overlap-2026-08-08.md` intersected GSE243553 with **four *ENO3* NBRE
  coordinates** — one gene, the manuscript's own designated positive control, targeted at sequence
  sites. It did not ask what the fusion's program contains, and could not.
* Declined: W25 (`reports/W25-gse243553-candidate-merit.md`) refused the **partner-binding / family
  clustering** line as a paper because the primary publication already reports it. That is a claim
  about relations among the 32 programs; **it is not the class-A membership question**, and W25's own
  audit found the statistics sound.
* Held / gated: `nr4a3-program-source-2026-09-07` prepared the memberships for a prospective **EMC
  expression program-specificity** test, and explicitly stopped before any outcome: "No empirical
  outcome process is running at handoff", with the executable outcome protocol left as a
  coordinator-owned gate.
* The gap this lane addresses sits before that gate and needs no outcome data: **membership itself has
  never been read against the class-A catalogue, and the identifiability of the prospective test has
  never been quantified.**

## 4 · The bounded step taken

Two outcome-blind analyses over the frozen membership table, at the packet's primary ±2 kb promoter
rule with ±1 kb / ±5 kb as declared sensitivities. **No expression value of any kind was read.**

### 4.1 · The class-A genes are absent from the EMC fusion's own program

At every window, **none of *SEMA3C*, *PPARG*, *ENO3* is in the EWSR1::NR4A3 program.** Where they do
appear (2 kb):

| gene | in EWSR1-NR4A3 | programs containing it (of 32) |
|---|---|---|
| *SEMA3C* | no | **0** — in no program at any window |
| *ENO3* | no | 3 — TAF15-NR4A3, TCF12-NR4A3, TMPRSS2-ERG |
| *PPARG* | no | 6 — TAF15-NR4A3, TCF12-NR4A3, TFG-NR4A3, **CCDC6-RET, ETV6-NTRK3, FGFR3-TACC3** |

The last row is the substantive reading: *PPARG*'s promoter opens under three fusions containing **no
NR4A3 sequence at all** — three kinase fusions — as well as under three NR4A3 fusions. Whatever opens
that promoter in this biosensor is not specific to the NR4A3 DNA-binding domain. This is independent
of, and concordant in direction with, the manuscript's Table 9 result that *PPARG* carries **zero**
promoter-window peaks in all four deep NR4A3 ChIP-seq experiments.

**The absences are calibrated, and the calibration refuses one reading.** A raw "in *k* of 32
programs" count is confounded by program size (EWSR1-NR4A3 contributes 69 common-platform genes;
TAF15-NR4A3, 637). A size-weighted independence null (Poisson-binomial over the 32 program sizes,
universe 15,930 shared symbols) puts *PPARG* at P(K≥6) = 3e-06 — **and that null is refused by its own
control: it predicts 0.04 genes at k ≥ 6 where 91 are observed.** Programs are strongly correlated, so
the independence model is wrong and its p-value is not reported as evidence. The honest calibration is
the empirical one: *PPARG* at k = 6 sits in the top 2.2% of program-member genes, but 91 genes reach
that level, so *PPARG* is promiscuous rather than exceptional. **Absence from the EWSR1::NR4A3 program
is not evidence of absent regulation** — that program is small and shallow (112 nuclei, promoter-window
mapping captures only ~12–16% of its peaks, distal regulation excluded by construction), so a specific
gene's absence is the expected outcome for almost any gene. Only the *positive* cross-partner pattern
for *PPARG* is read here.

### 4.2 · The prospective specificity test is identifiable against alternatives, marginal within the family

| window | EWSR1-NR4A3 genes | minus all 28 alternative-fusion programs | minus those **and** the other 3 NR4A3 fusions | largest single alternative program's containment |
|---:|---:|---:|---:|---|
| 1 kb | 36 | 23 | **4** | CCDC6-RET, 11.1% |
| **2 kb** | **69** | **40** | **7** | CCDC6-RET, 13.0% |
| 5 kb | 142 | 57 | **6** | CCDC6-RET, 21.1% |

Jaccard of EWSR1-NR4A3 against the other NR4A3 fusions at 2 kb: TCF12 0.281, TFG 0.156, TAF15 0.093.
So a future EMC-expression read of this program can be attributed to *an NR4A3 fusion* rather than to
oncofusion accessibility in general (40 genes clear the manuscript's own ≥4-gene set-score floor by a
wide margin), but a read attributed to the **EWSR1 partner specifically** rests on 4–7 genes — at or
barely above that floor, and below it in no window only by a margin of three genes. That is a
quantitative design constraint the gated protocol did not have.

## 5 · Artifact · validation · provenance · limitations · stop condition

* **Artifacts.** `program-identifiability.json`, `classA-promiscuity.json`, `size-weighted-null.json`;
  code `program_identifiability.py`, `classA_promiscuity.py`, `size_weighted_null.py` (stdlib only,
  deterministic, no network, no GPU, no spend). `checks/01…03/` hold every execution attempt with
  `command.txt`, `stdout.txt`, `stderr.txt`, `exit_code.txt`. All three exited 0 on first run.
* **Validation / baseline.** Two baselines, both reported: the empirical cross-program membership
  distribution (used), and the size-weighted independence null (**computed, then refused** by its own
  91-vs-0.04 control). The 4-gene set-score floor is the manuscript's own, not a new threshold. The
  three windows are the packet's pre-declared primary and sensitivities, not chosen post hoc.
* **Provenance.** Sole input `outputs/common-platform-membership.tsv` plus
  `sources/tpm-symbol-universe.txt` and `sources/GPL6244-gene-to-probes.json` from
  `research/autonomy/nr4a3-program-source-2026-09-07` in the frozen corpus at
  `/tmp/claude-0/frozen-corpus/extracted/corpus/…`, read in place. That packet's memberships were
  frozen **before** any outcome and its mapping specification was hashed before mapping began. No file
  outside this lane directory was written, read-locked or copied; no commit, no preflight.
* **Limitations.** HEK293T, ectopic, **accessibility not occupancy**, not EMC material — this cannot
  make any gene "fusion-driven" and must never be cited as a cistrome. Promoter ±2 kb only; distal
  regulation is out of scope by the packet's rule, so a gene regulated distally is unreadable here, not
  unregulated. The BEDs are positive-only (increased accessibility vs empty vector), so a closing
  program is invisible. Program depth varies ~9-fold across the four NR4A3 fusions, so cross-program
  counts are confounded by depth in a way the empirical calibration bounds but does not remove.
  Absence of a gene from a program is an unread negative, never a measured zero.
* **Stop condition.** Stopped at the outcome boundary, deliberately. The membership half is complete
  and needs no further computation. The expression half is **not runnable in this lane**: no EMC
  expression matrix exists in the checkout or the frozen corpus (only sample metadata for GSE4303 and
  GSE24369), GEO egress is proxy-denied, and the outcome protocol is a coordinator-owned frozen gate
  that a lane worker must not pre-empt. **That is the honest missing dependency, named.**

## 6 · Outcome for the paper

Not a new paper and not an admission request. Two usable results, both testable-not-illustrative:

1. **A finding for §3.11/§4.3 of PUB-FUSION-OUTPUT**, at its own strength: the sole genome-wide
   NR4A3-fusion perturbation experiment places **none** of the three class-A genes in the
   EWSR1::NR4A3 program, and places *PPARG* under three fusions carrying no NR4A3 sequence. This
   sharpens the existing Table 9 negative rather than contradicting it, and it is the first reading of
   that dataset's EMC-fusion program against this catalogue.
2. **A design constraint** on the gated prospective specificity test: 40 genes carry an
   NR4A3-vs-other-fusion contrast; only 4–7 carry an EWSR1-vs-other-NR4A3-partner contrast, so the
   partner-specific version of that test is underpowered by construction and should be pre-declared as
   secondary if it is run at all.

No prose in the manuscript was edited. Any use of point 1 belongs to the paper's owner; if wanted, it
is a §3.11 addition and would need an exact unapplied diff prepared by that owner, not by this lane.
