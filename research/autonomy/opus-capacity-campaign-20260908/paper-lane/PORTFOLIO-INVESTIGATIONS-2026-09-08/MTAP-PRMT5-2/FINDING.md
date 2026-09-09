---
id: DOC-PORTFOLIO-INVESTIGATION-MTAP-PRMT5-2
title: "MTAP-PRMT5-2 — what PUB-MTAP-PRMT5 still asserts after the FET-class transcript null, claim by claim"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: MTAP-PRMT5-2
repo_commit: e61fed278ff72e04ca8cc75f068a927be050a0ed
---

# MTAP-PRMT5-2 — the paper after the null

## 1. The question

After `PORTFOLIO-INVESTIGATIONS-2026-09-08/PUB-MTAP-PRMT5/` recorded that FET-fusion driver status
carries no *PRMT5* transcript elevation inside the paper's own comparator arm (*t* = −0.16,
*p* = 0.873), **what does `research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis.md` and its SI
still assert, and is any of it still supported?** A falsification recorded in a lane directory does
not rewrite the paper; this lane enumerates the claims and gives each a verdict.

## 2. Merit

PUB-MTAP-PRMT5 is a `drafted` endpoint in `systems/graph/publications.json` for a disease with no
targeted agent. A recorded negative that nobody carries back into the prose is how a paper ends up
asserting something its own repository has already refuted. The bounded, cheap and useful act is to
say precisely which sentences the null reaches and which it does not — and, equally, to refuse the
mirror-image overreach that "MTAP/PRMT5 biology is irrelevant in EMC", which does not follow and is
contradicted by the same run.

## 3. The evidence gap

The prior lane produced the statistic and explicitly made **no manuscript edit**. Nothing in the
repository maps that statistic onto the manuscript's claim set, and no artifact says which claims
survive it. That mapping is what was missing, and it needs no new data.

## 4. The step taken

### 4.1 Re-derivation first (required before building on it)

`rederive_fet_null.py` (this lane, written without reusing the prior lane's script) recomputes Welch
*t* and permutation *p* directly from `research/modalities/emc-expression-panels.json`.

**The falsification reproduces.**

| quantity | prior lane | this lane |
|---|---:|---:|
| *t*, FET comparator vs non-FET comparators | **−0.160** | **−0.1598** |
| Δ mean *z* | −0.0075 | −0.0075 |
| *n* | 17 vs 12 | 17 vs 12 |
| permutation *p* | **0.87255** (MC, 200,000 draws, seed 20260908, SE 0.00075) | **0.87327** (MC, 1,000,000 draws, seed 424245, SE 0.00033) |

The exact comparison is: LGFMS (FUS::CREB3L2, *n* = 17) against pooled desmoid fibromatosis (*n* = 6)
plus fibrosarcoma (*n* = 6), on per-sample `z_vs_array` for *PRMT5* in
`gene_reads.PRMT5["GSE24369_series_matrix.txt.gz"]`, GPL6244. C(29,17) = 51,895,935 labelings, so
neither lane enumerated exactly; both *p* values are independent Monte-Carlo estimates of the same
exact *p*, differing by 0.00072 — about 0.9 combined standard errors. That is sampling noise, not a
discrepancy. Four published baselines re-derive at the same time: *PRMT5* +6.2356 against the printed
+6.24, *MTAP* +0.6853 against +0.69, *CDKN2A* −5.3982 against −5.40, *NR4A3* +4.6625 against +4.66.

Two further reproductions confirm §3.4 is numerically sound as printed: per-class *PRMT5* medians
EMC 1.3045 / desmoid 1.0509 / LGFMS 1.0427 / fibrosarcoma 0.9370 (printed +1.30, +1.05, +1.04, +0.94),
and the pooled four-gene methylosome (PRMT5, WDR77, RIOK1, CLNS1A) putting EMC second below desmoid.

### 4.2 What is and is not falsified — the precision the task demands

**Falsified:** *"FET-fusion driver status predicts elevated PRMT5 transcript"*, within GSE24369.

**Not falsified:** the fusion rationale itself. That premise is functional — PRMT5 is required for
fusion-driven transcription — and its evidence is reference [3] (peer-reviewed, Ewing) and the §3.7
motif match. Transcript abundance was never its observable; **the paper's own reference [3] already
says depleting EWSR1::FLI1 did not change PRMT transcript levels**, so this null independently
corroborates the cited literature in a second FET sarcoma rather than contradicting the transfer.

**Also not falsified, and the mirror-image error to avoid:** EMC separates from the FET class on
*PRMT5* as strongly as from the non-fusion classes (*t* = +5.98, exact *p* = 5.9 × 10⁻⁵ over 100,947
labelings). The MTAP locus question is untouched, and no dependency observation in EMC exists in
either direction. Nothing here licenses "MTAP/PRMT5 biology is irrelevant in EMC".

**Consequence:** the transcript reading is **EMC-associated and class-uninformative**. It bounds the
fusion rationale without supporting it.

### 4.3 The ledger

`claim-ledger.json` — 24 claims, each with site, verdict and the artifact/key that establishes it.
Counts: **STANDS 16 · NARROWED-BY-THE-FALSIFICATION 5 · FALSIFIED 0 · NOT-CHECKABLE-LOCALLY 4**.
That is 25 labels over 24 claims because C13 carries two — NOT-CHECKABLE by this lane's design,
STANDS as recorded.

**FALSIFIED = 0 is the honest count and is itself the finding.** The paper never printed the
sentence the null kills. What it did was place the class transfer and the EMC transcript contrast in
adjacent sentences without stating their independence, and describe the FET comparator as a control
in only one of its two directions. The diff touches six sites — the five NARROWED ones, plus C09,
which stands as written and gains a limitation:

* **C04 · §3.4 / figure 4 caption** — the primary site. "a FET-fusion control on whether the reading
  is simply what a fusion sarcoma looks like" tests one direction. The second direction is now
  measured and is null.
* **C07 · abstract** — sentence order invites reading *t* = 6.24 as class evidence.
* **C08 · §4.1** — "Two limits sit on the surviving rationale"; there are three.
* **C09 · §4.4** — needs the orthogonality stated, and symmetrically that the comparator is
  FUS-driven so an EWSR1-specific premise is untested here rather than refuted.
* **C21 · SI §S5** and **C22 · SI §S7 item 3** — the same framing in the supplement.

### 4.4 Disposition — reframe, do not retire

The endpoint should **not** be retired and the fusion rationale should **not** be withdrawn. One
*reading* of it should be retired: the transcript contrast as class-level evidence. After the
correction the rationale rests explicitly and only on reference [3] and the motif match, both
arguments about plausibility and neither an EMC observation — which is what §4.4 already says. The
paper absorbs this without losing a result.

## 5. Artifact · validation · provenance · limitations · stop condition

**Artifacts.** `claim-ledger.json` (machine-readable, 24 claims + pin exposure + downstream sites);
`proposed-correction.diff` (**UNAPPLIED**, 108 lines, two files); `rederivation-fet-null.json`;
`rederive_fet_null.py`; `checks/01..07`.

**Validation.** `git apply --check -p1 proposed-correction.diff` → **exit 0**
(`checks/05-git-apply-check`). `git status --porcelain research/manuscripts/mtap-prmt5/` → empty
(`checks/06`): the manuscript is untouched on disk. `checks/04` records exit **1**, which is
diff(1)'s "files differ" status, preserved rather than masked. Baseline for the new numbers is the
four published *t* values that re-derive through a separate code path.

**Provenance.** Sole data input `research/modalities/emc-expression-panels.json` at repo commit
e61fed278ff72e04ca8cc75f068a927be050a0ed, per-sample `z_vs_array` and `class` only. Class-to-driver assignments are the
manuscript's own (§2.1, §3.4). No network, no fetch, no paid resource, no GPU.

**Limitations — load-bearing.**
1. The FET comparator is **FUS**-driven. This addresses the FET family; a narrower premise stated on
   EWSR1 fusions specifically is untested, because GSE24369 holds no second EWSR1-fusion class.
2. GPL3290 cannot run this test — its comparators are DFSP and GIST, neither FET. The platform
   disagreement of §3.6 is untouched.
3. Six EMC tumours, one series, a decade-old array. Nothing here makes the transcript contrast
   significant: the family-wise adjusted *p* of 0.21 still governs (§3.5).
4. Transcript is not dependency and not copy number. **No efficacy, safety, selectivity or
   clinical-readiness claim follows from any of it, and none is made.**
5. C12 (DepMap per-line) and C23/C24 (publisher confirmation, prior-art screen) are
   NOT-CHECKABLE-LOCALLY. The per-line `CRISPRGeneEffect` fetch is the parents' open gap and outside
   this lane's authority; **it was not attempted**. Unverified is not wrong.
6. The proposed prose is a correction, not a rewrite. It changes no number, no falsifier row, no
   figure image and no pin.

**Pins — reported, not changed.** `research/manuscripts/pinned-figures.json` lists the manuscript at
`targets[21]` and three pinned values that live in it — `emc_prmt5_mat2a_pct_gpl6244` [24],
`emc_prmt5_mat2a_pct_gpl3290` [25], `emc_prmt5_pct_gpl6244` [26], all owned by
`research/modalities/census-route-expression-grading.json` and all quoted in §3.1. **The diff touches
none of their lines and alters no pinned value.** Downstream, `systems/graph/routes.json:5820` and its
generated view `systems/views/L2-rt-mtap-prmt5.md:23` carry the same route grade; every figure they
quote re-derives unchanged, and the optional one-clause addition there is **for the coordinator
alone** — graph state is out of lane and no diff against it is offered.
`research/manuscripts/nr4a3-program-map.md` contains no PRMT5 or MTAP mention at all.

**No rescue analysis was sought.** One prespecified contrast was re-derived once and reported as it
came out. No subgroup, alternative statistic or reweighting was tried.

**Stop condition — reached.** The claim set is enumerated, the statistic reproduces, and the
correction is prepared and proved appliable. The lane stops here. The next credible work is the
functional one the paper already names (§4.2), which this lane cannot run: there is no wet lab.
