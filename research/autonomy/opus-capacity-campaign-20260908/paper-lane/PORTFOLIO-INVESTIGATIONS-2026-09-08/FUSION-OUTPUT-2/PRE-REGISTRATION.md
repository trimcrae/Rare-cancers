---
id: DOC-PORTFOLIO-INVESTIGATION-FUSION-OUTPUT-2-PREREG-20260909
title: "Pre-registration — NR4A3 accessibility-program specificity test: two contrasts, frozen gene sets, declared detectability"
level: L4
kind: prereg
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# Pre-registration — the two NR4A3-program contrasts

**This is a design document. It is not a result.** No expression value of any kind was read while
writing it, no contrast was computed, no biological conclusion is reached. Its entire worth is that
the gene sets, the decision rules and the detectability arithmetic are fixed **before** anyone looks
at outcome data. If any number below is later found to have been chosen after an expression value
was seen, this document has failed and the analysis is post hoc.

**Authority.** The executable outcome protocol for the prospective EMC expression test is a
**coordinator-owned frozen gate** (`research/autonomy/nr4a3-program-source-2026-09-07`, README §"Next
gate": "No empirical outcome process is running at handoff"). This lane **pre-specifies** a test. It
does **not** authorise the test, does not open the gate, does not pre-empt the coordinator's protocol,
and does not claim priority over it. If the coordinator's frozen protocol differs from anything here,
the coordinator's protocol governs and this document is a rejected proposal.

## 1 · Why a pre-registration is the right artifact

The completed lane `../PUB-FUSION-OUTPUT/` established, from membership alone, a constraint nobody
had before: the EWSR1::NR4A3 accessibility program survives subtraction of all 28 alternative-fusion
programs with 40 genes at the primary window, but survives subtraction of the other three NR4A3
fusions with only **4–7**. An NR4A3-vs-other-fusion contrast is therefore identifiable; an
EWSR1-partner-specific contrast is underpowered **by construction**, before any data exist. A
constraint of that shape is worth nothing if it is discovered after the gated run is spent. Fixing it
in advance is the deliverable.

## 2 · The frozen gene sets

**Source.** `outputs/common-platform-membership.tsv` from the coordinator-frozen source packet
`research/autonomy/nr4a3-program-source-2026-09-07`, read in place from the frozen corpus at
`/tmp/claude-0/frozen-corpus/extracted/corpus/…`. SHA256 of that file, recorded by the generator:
`b54b3eda97c0663e052cfe52ac4b8dbae3914bbffad73a905de98de8873c801b` (recomputed by the generator at run time and stored in `fusion-program-testsets.json#input.sha256`). Those
memberships were frozen before any outcome, and the promoter mapping specification was hashed
(`5bd33609bba76d70c9d17ace17cd45effa2811003cf153458dd33e4bef72f74d`, frozen 2026-09-07T14:11:33Z)
before mapping began.

**Generator.** `build_testsets.py` (stdlib only, deterministic, no network). Artifact:
`fusion-program-testsets.json`, which carries every gene with its Ensembl gene id and the full list of
programs containing it, so each membership is auditable one gene at a time.

**Subtraction that produced each set.**

* **Contrast A set** = EWSR1-NR4A3 program **minus** the union of all **28** non-NR4A3 fusion programs.
* **Contrast B set** = the contrast A set **minus** the union of the other three NR4A3 fusion programs
  (TAF15-NR4A3, TCF12-NR4A3, TFG-NR4A3).

**Primary window is ±2 kb**, pre-declared; ±1 kb and ±5 kb are the source packet's declared
sensitivities and are reported as **different sets**, not as robustness of the same set (§5).

### 2.1 · Contrast A — NR4A3-vs-other-fusion

| window | n | genes |
|---|---:|---|
| 1 kb | 23 | *AAGAB*, *AFP*, *CCL28*, *CENPI*, *EMC10*, *EYA4*, *FAM13C*, *FAXC*, *FOXA1*, *GUCY2C*, *HAP1*, *IQCH*, *KDM4C*, *NELL2*, *OAS1*, *RNF130*, *SEMG2*, *SH3D19*, *SIDT1*, *SLC25A16*, *SLC2A13*, *TBX21*, *TMEM67* |
| **2 kb (primary)** | **40** | *AAGAB*, *AFP*, *AGL*, *AIMP1*, *ARHGAP17*, *BAZ2A*, *CCL28*, *CDC14A*, *CENPI*, *EMC10*, *FAM13C*, *FAM20A*, *FAXC*, *FBXO21*, *FOXA1*, *GALNT3*, *GUCY2C*, *HAP1*, *IQCH*, *ITLN2*, *KDM4C*, *KRCC1*, *LAMA1*, *MFSD2A*, *NELL2*, *OAS1*, *PIKFYVE*, *PLCXD2*, *RFX3*, *RNF130*, *RNF220*, *SDK1*, *SEMG2*, *SGPP2*, *SIDT1*, *SLC25A16*, *SLC2A13*, *ST3GAL6*, *TBX21*, *TMEM67* |
| 5 kb | 57 | *AAGAB*, *AFP*, *AGL*, *AIMP1*, *ANKRA2*, *AXIN1*, *BAZ1B*, *BAZ2A*, *BBS7*, *BPTF*, *C5AR1*, *CCL28*, *CDC14A*, *CENPI*, *CHRNA6*, *COPZ1*, *CPNE3*, *EMC10*, *EVA1A*, *FAM20A*, *FAXC*, *FBXO38*, *FOXA1*, *FREM3*, *GALNT3*, *GUCY2C*, *IDH1*, *IQCH*, *ITLN2*, *KDM4C*, *KLHL31*, *KRCC1*, *LAMA1*, *MAS1*, *MFSD2A*, *NDUFAF4*, *NNT*, *NUP210L*, *OAS1*, *OLAH*, *PIKFYVE*, *PPTC7*, *RARRES1*, *RFX3*, *RNF220*, *RPN2*, *SDK1*, *SEMG2*, *SGPP2*, *SIDT1*, *SLC25A16*, *SLC9B2*, *ST3GAL6*, *TBX21*, *TMEM67*, *WDR11*, *WDR17* |

### 2.2 · Contrast B — EWSR1-partner-specific

| window | n | genes |
|---|---:|---|
| 1 kb | 4 | *FAXC*, *FOXA1*, *HAP1*, *TBX21* |
| **2 kb (primary)** | **7** | *BAZ2A*, *FAXC*, *FBXO21*, *FOXA1*, *HAP1*, *PIKFYVE*, *TBX21* |
| 5 kb | 6 | *BAZ2A*, *FAXC*, *FOXA1*, *IDH1*, *PIKFYVE*, *TBX21* |

None of the three class-A genes (*SEMA3C*, *PPARG*, *ENO3*) is in any of these sets; that is a
membership fact from the completed lane, carried forward, not a new result.

## 3 · The two contrasts, stated separately

Scoring machinery is the manuscript's own (PUB-FUSION-OUTPUT §2.3, unchanged and not renegotiated
here): per-sample within-array z, gene score = mean z over readable probes, set score = mean z over
readable members, contrast = Welch *t* on per-sample set scores EMC versus comparator, calibrated
against the exact global offset and a size-matched empirical null of 4,000 random sets of the same
size (seeded pool). Floors, also the manuscript's own: **three samples per group**, **four readable
genes**, **0.4 coverage**. A set under a floor emits no number and says so.

Cohorts as the manuscript uses them: **GSE24369** (GPL6244; 6 EMC vs 29 comparators) and **GSE4303**
(GPL3290; 10 EMC vs 6 comparators, graded **circular** for EMC-elevation claims at §3.8). Sample
counts here are metadata only; no expression value was read to obtain them.

### 3.1 · Contrast A — NR4A3-vs-other-fusion (identifiable)

**Question.** Do the 40 genes whose promoters open under an NR4A3 fusion **and under no other
fusion in the panel** behave, in EMC tumour expression, unlike a size-matched random set and unlike
the alternative-fusion programs?

* **Positive.** The contrast A set score is elevated in EMC versus comparator on **both** series, in
  the same direction, each exceeding the exact global offset, with the observed statistic beyond the
  size-matched empirical null at the pre-set α, **and** the index program ranked above the 28
  alternative-fusion program scores (rank-based one-sided *p* ≤ 0.05 is attainable — minimum 1/29 =
  0.0345).
* **Negative.** The set score does not exceed the global offset on either series, or sits inside the
  size-matched null, at an effect the design could have seen (§4). A negative is a real result and is
  reported as one.
* **UNINTERPRETABLE.** Any of: the two series disagree in direction; the effect is present but not
  distinguishable from the global offset (a whole-array shift, not a set-specific one); coverage on a
  platform falls below 0.4 or readable members below 4; the result is carried by GSE4303 alone (that
  cohort is the source of the published EMC-elevation claims and is graded circular); or the
  alternative-fusion programs score comparably, which would mean generic oncofusion accessibility,
  not NR4A3 output. An uninterpretable outcome is **not** converted into a weak positive.

### 3.2 · Contrast B — EWSR1-partner-specific (4–7 genes)

**Question.** Do the 7 genes specific to EWSR1::NR4A3 against the other three NR4A3 fusions behave
differently in EMC from the other three partners' programs?

* **Positive.** Would require the 7-gene set to be elevated on both series beyond the global offset
  and beyond a size-matched null, **and** to outrank the TAF15/TCF12/TFG program scores.
* **Negative.** No elevation at a detectable effect — but see §4: the detectable effect is so large
  that a negative here is close to uninformative.
* **UNINTERPRETABLE — and this is the expected outcome.** A pure rank statement of the EWSR1 program
  against the other three NR4A3 programs has a **minimum attainable one-sided *p* of 1/4 = 0.25** and
  therefore **cannot reach α = 0.05 at any effect size whatsoever**. Separately, the window-invariant
  core of contrast B is **3 genes** (*FAXC*, *FOXA1*, *TBX21*), **below the manuscript's own 4-gene
  floor**, so the set is not the same object across the three windows and a window-robust B result
  cannot be formed. At 1 kb the set is exactly 4 genes, so **a single unreadable probe on either
  platform drops it below the floor** and it emits no number at all.

## 4 · What each contrast could detect, with every assumption stated

Artifact `design-power.json`, generator `power_design.py` (scipy 1.17.1, analytic only, no data).

**Model, in full.** Per gene *g* and sample *i* the manuscript's within-array z is *x*<sub>ig</sub>;
**assume** Var(*x*) = 1 across samples for every gene. Set score *S* = mean over *m* readable members;
**assume** a common average across-sample inter-gene correlation ρ, so Var(*S*) = (1+(*m*−1)ρ)/*m* and
the effective independent gene count is *m*<sub>eff</sub> = *m*/(1+(*m*−1)ρ). **Assume** the
alternative is a **common per-gene elevation *d*** in SD units shared by all members (a heterogeneous
effect with the same mean is strictly harder to detect). Test: two-sided Welch *t* at α = 0.05, 80%
power, using this repository's own MDE convention (W17c): critical sum = *t*<sub>.975</sub>(df) +
*t*<sub>.80</sub>(df), **assuming** df = *n*₁+*n*₂−2 (true Welch df is ≤ that, so these MDEs are
optimistic).

> MDE(*d*) = (*t*<sub>.975</sub>+*t*<sub>.80</sub>) · √(1/*n*₁+1/*n*₂) · √((1+(*m*−1)ρ)/*m*)

**Minimum detectable per-gene effect, GSE24369 (6 vs 29), primary 2 kb window:**

| contrast | *m* | ρ=0 | ρ=0.1 | ρ=0.2 | ρ=0.5 | *m*<sub>eff</sub> at ρ=0.2 |
|---|---:|---:|---:|---:|---:|---:|
| A | 40 | 0.205 | 0.453 | 0.607 | 0.927 | 4.55 |
| B | 7 | 0.489 | 0.619 | 0.726 | 0.979 | 3.18 |

GSE4303 (10 vs 6) is uniformly worse: A 0.730 and B 0.872 at ρ=0.2.

**Three things this arithmetic settles, and they are the point of the document.**

1. **Gene count buys far less than the 40-vs-7 headline suggests.** Under independence (ρ=0) the
   B/A MDE ratio at 2 kb is **2.39**; at a realistic ρ=0.2 for co-regulated promoter sets it is
   **1.195**. Both contrasts collapse toward *m*<sub>eff</sub> ≈ 3–5 effective genes. **The binding
   constraint is 6 and 10 EMC tumours, not the gene count.**
2. **Contrast A can detect only a large effect.** At ρ=0.2 it needs ≈ **0.61 per-gene SD units** on
   the better-powered series, and ≈ **0.89** if one adjusts α for the 28 alternative programs. It is
   identifiable — it clears the 4-gene floor by 36 genes and can reach significance — but it is a
   test for a **large, set-wide elevation**, not for a subtle program signature. A null from it
   excludes effects above roughly 0.6 SD and excludes nothing below.
3. **Contrast B cannot detect anything worth naming, and should not be run.** Numerically: minimum
   attainable rank *p* = **0.25** against the other three NR4A3 programs (unreachable α at any effect
   size); MDE ≈ **0.73–0.87 per-gene SD**, an elevation larger than most whole-tissue contrasts
   produce; window-invariant core of **3 genes**, under the manuscript's own 4-gene floor; and zero
   dropout tolerance at 1 kb. **Recommendation: do not run contrast B.** If the coordinator runs it
   anyway, it must be declared **secondary and descriptive**, must never be reported as a *p*-value
   supporting partner specificity, and a negative from it must not be reported as evidence against
   partner specificity.

## 5 · Windows

±2 kb is primary. The three windows do **not** define the same set: Jaccard across windows is
0.25–0.50 for contrast A and 0.43–0.63 for contrast B (`set-stability.json`, generator
`set_stability.py`). Agreement across windows is therefore **not** available as a robustness argument
for either contrast; a sensitivity window that disagrees with 2 kb is a different set giving a
different answer, and must be reported that way. The window-invariant core is 16 genes for A (clears
the floor) and 3 genes for B (does not).

## 6 · Prerequisite checks, to be run before any contrast

1. **Coverage.** The sets are built on the common TPM ∩ GPL6244 universe, so GPL6244 coverage is 1 by
   construction; **GPL3290 coverage is unknown offline** and must be computed through the manuscript's
   EST-accession bridge before GSE4303 is scored. If coverage < 0.4 or readable members < 4, the set
   emits no number on that platform.
2. **Circularity.** GSE4303 is graded circular for EMC-elevation claims (§3.8). Its role is
   pre-declared as **corroborative only**; a positive that exists only on GSE4303 is uninterpretable
   (§3.1).
3. **Comparator composition.** GSE24369's comparator arm is itself FET-rearranged (LGFMS,
   *FUS::CREB3L2*), so its contrast is FET-versus-FET, and 23 of 29 comparators are myxoid.

## 7 · Stop and refutation conditions, declared in advance

**Stop — do not start.**
* S1. The coordinator's frozen outcome protocol is not opened by its owner. This document confers no
  authority to run anything.
* S2. GPL3290 coverage or readable-member count fails a floor: that platform is dropped, and if both
  fail, the test does not run.
* S3. Contrast B is not run at all on the arithmetic of §4.3, unless the coordinator overrides with
  a recorded reason.

**Stop — mid-analysis.**
* S4. Any request to change the gene set, the window, the floors or the α after an expression value
  has been seen. The sets in §2 are frozen; a changed set is a new, post hoc analysis and must be
  labelled one.
* S5. Direction disagreement between the two series: report as uninterpretable and stop, do not pool.

**Refutation — what would refute the design's own premises.**
* R1. If the contrast A set score is indistinguishable from the exact global offset, the premise that
  a promoter-accessibility program carries a readable tumour-expression signature is refuted for this
  set, at this power.
* R2. If size-matched random sets reach the same score as contrast A, the set carries no
  program-specific information and the accessibility-to-expression bridge fails here.
* R3. If alternative-fusion programs score comparably to contrast A in EMC, the signal is generic
  oncofusion accessibility, and the specificity claim is refuted.
* R4. If contrast A's observed effect is below ≈0.6 per-gene SD, this design could not have seen it;
  the correct report is "not powered", not "absent". **A missing measurement is unknown, not zero.**

## 8 · Limitations carried forward verbatim from the completed lane

> HEK293T, ectopic, **accessibility not occupancy**, not EMC material — this cannot make any gene
> "fusion-driven" and must never be cited as a cistrome. Promoter ±2 kb only; distal regulation is out
> of scope by the packet's rule, so a gene regulated distally is unreadable here, not unregulated. The
> BEDs are positive-only (increased accessibility vs empty vector), so a closing program is invisible.
> Program depth varies ~9-fold across the four NR4A3 fusions, so cross-program counts are confounded
> by depth in a way the empirical calibration bounds but does not remove. Absence of a gene from a
> program is an unread negative, never a measured zero.

Additionally: no result from any contrast specified here can establish efficacy, safety, selectivity,
a therapeutic window or clinical readiness, and none is a patient-specific statement.
