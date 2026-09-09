---
id: DOC-EMC-PROGRAM-1-FINDING-20260909
title: "EMC-PROGRAM-1 — PUB-EMC-PROGRAM's roadmap claims audited against this campaign's evidence: three falsified, four narrowed, six unsupported by the artifact they cite"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: EMC-PROGRAM-1
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
target: PUB-EMC-PROGRAM
target_document: research/manuscripts/program/emc-treatment-roadmap.md
siblings_read: [SYNLETH-2, PUB-SYNLETH, PUB-MTAP-PRMT5, DEP-THRESHOLD, SURFACE-2, EPITOPE-BENCHMARK, VACCINE-PATH-2, MATRIX-ADDRESS-3, BIOMARKER-DEP-3, DEGRADER-2]
---

# EMC-PROGRAM-1

⛔ **No treatment recommendation, no patient-specific advice, and no statement that any route is or is
not clinically viable is made or may be read out of this document.** No wet lab, no EMC observation.
Every DepMap `frac_dependent`, `selectivity` and `log2(TPM+1)` figure below is a **screen statistic on
a public cell-line panel**, not an efficacy, safety, selectivity or therapeutic-window property. No
network, no GPU, no paid API, no publication act, no outreach, no `git add/commit/push`, no
`preflight.sh`, no subagent. Every write is inside this directory; the manuscript was **not** edited —
the correction is delivered as an unapplied diff.

## 1 · The question

PUB-EMC-PROGRAM owns **zero routes of its own** (both its routes carry `role: context`), so every
scientific claim in the roadmap is **inherited** from a lane underneath it. This campaign narrowed or
falsified a large part of that inheritance. So: **which sentences in
`emc-treatment-roadmap.md` still have the support they cite, once the citation is followed to the
artifact and the artifact is read against this campaign's results — and which sentences are
therapeutic-readiness claims that computation cannot carry?**

## 2 · Merit rationale

An umbrella paper is the one place in a portfolio where a falsified sub-result silently survives:
it re-states a lane's conclusion in its own prose, so correcting the lane does not correct the
umbrella. PUB-EMC-PROGRAM has never had a lane and is `state: drafted` for
`target_venue: journal_submission`. Its two flagship routes rest on a fusion-addiction premise whose
class-transfer step was tested and **failed** in owned data this week, and its delivery proposal rests
on a surface screen whose vital-tissue half has **never run**. Auditing it is patient-relevant in the
only honest sense available here: it prevents a document that hands experiments to other groups from
handing them a premise the repository's own data no longer supports.

## 3 · Evidence gap this closes

The gap was **not** new computation. It was that no one had walked the roadmap's claims to their
cited artifacts. The inputs are the manuscript's own citations — `nr4a3-structure-assessment.json`,
`nr4a-selectivity.json`, `depmap-sarcoma-dependency.json`, `depmap-target-expression.json`,
`aso-insilico-evaluation.json`, `nr4a3-program-map.md`, `nr4a3-degrader-paper.md` — read alongside the
ten sibling lanes listed in the frontmatter. This differs from those lanes' work: each of them settled
one artifact; none of them opened the roadmap.

## 4 · Step taken, and the result

**Every number in the roadmap was re-derived from the artifact it cites**
(`rederive_roadmap_numbers.py`, `checks/01`, exit 0), then 28 claims were ruled in
`CLAIM-LEDGER.tsv`, each verdict naming the lane or artifact that establishes it.

### 4.1 · Reproduces exactly, digit for digit

fpocket druggability **0.495** (Pocket 5, span 406–534); disordered N-terminus (frac pLDDT < 50 =
**0.965**); FLI1-in-Ewing **−0.934** / **0.741** / **n = 27**; Pocket-5 divergent residues **7**
(L406, T407, T410, R412, I484, I531, L534); CD276 sarcoma mean **5.73**, frac expressed **0.99**;
PRAME **0.53**, CTAG1B **0.05**, MAGEA4 **0.07**; myxoid CD276 **4.44** (n = 1); ASO **0** of **5**
transcriptome-clean over **186,185** transcripts, best design 0 exact / **8** one-mismatch, **2** of 5
seeds straddling the junction. The roadmap's arithmetic is sound.

### 4.2 · Three claims FALSIFIED

1. **The FET-fusion class prior (§4.1, Abstract, §8).** PUB-MTAP-PRMT5 tested the class transfer
   inside the powered series: FET comparator (LGFMS, FUS::CREB3L2) vs non-FET gives *t* = **−0.160**,
   Δ = **−0.008 SD** (CI −0.101 to +0.086), *p* = **0.873**. FET-fusion driver status carries no
   class-level signal on the one axis this program can test.
2. **The WIP status of the de-novo warhead arm (§4.1, §7).** The roadmap lists it as *running,
   pipelines built*. `nr4a3-program-map.md` records Route A as **blocked, nothing running**
   (line 2926), Route B **blocked on R5, nothing running** (3040), Route C **parked, nothing running**
   (3190).
3. **The inherited no-overlap selectivity sentence.** DEGRADER-2 falsified it with an exact count —
   three NR4A3 C397 frames at or below the paralogue reference; the 0.9993 pairwise dominance is a
   geometric ranking statement, not evidence of selective labelling.

### 4.3 · The one number that does not reproduce as described

§4.2 reports the junction sites as *"poorly accessible (best ≈0.35 unpaired probability)"*. The
artifact's five designs carry **0.353, 0.369, 0.417, 0.338, 0.381**. The maximum is **0.417**. The
0.353 is the accessibility of the top-**ranked** design, and the file's own `ranking_key` sorts on
off-target count first — so the sentence reports a rank, not a maximum. The conclusion (poor
accessibility) survives; the stated statistic does not. Related: the two designs whose siRNA seed
straddles the junction — the design goal — are exactly the two at **81.2 % GC** carrying **58** and
**95** one-mismatch off-targets, which the results paragraph's flat "~75 %" does not convey.

### 4.4 · Support that does not exist in the cited artifact

* **B7-H3 "internalises" (§4.2)** — the citation is a DepMap expression read; internalisation is not
  an expression measurement.
* **B7-H3 as a clean delivery handle** — SURFACE-2: the producer's `vital_tissue` is `[]` on **all 45**
  scored rows because it derives from a `null` `rna_tissue_specific_nTPM`. **No candidate in that file
  has ever been screened against a vital tissue.**
* **"4 of the 5 engageable" handles distinguish NR4A2** — re-derivable only to *6 of 7 differ from
  NR4A2* (I531 is Ile in both) from `nr4a-selectivity.json`; the "engageable" subset is defined in
  `nr4a3-program-map.md` §2.4, not in the artifact the sentence cites.
* **Every `frac_dependent` in the panel** — DEP-THRESHOLD: one fraction per arm at one fixed cut
  (−0.5); a sweep is not computable, so 0.741 carries no interval (BIOMARKER-DEP-3: no interval is
  placeable on any `rest_frac_dependent`).
* **The vaccine/HLA retention (§5, §7)** — EPITOPE-BENCHMARK: **n = 15** validated junction epitopes
  across nine fusion oncoproteins against a requirement of **93**; achievable 95 % CI width **0.4515**.

### 4.5 · Therapeutic-readiness language

Three constructions do work that computation cannot support, and are flagged as such in the ledger and
corrected in the diff: the rubric's **"needs exactly one EMC target test … before use"** (a
clinical-readiness ordering), the table's **"fastest such route"** (a speed ordering over untested
routes), and the abstract's **"de-risked hypotheses"** (an assertion of reduced risk, on the two routes
this campaign moved the other way). The roadmap's explicit refusals — no efficacy comparison, the
categorical-gap framing, "a specification for the warhead, not a demonstrated property", the §9
hypotheses-not-computed fence, the per-route kill-criteria — are correctly fenced and are recorded as
STANDS.

## 5 · Artifact · validation · provenance · limitations · stop condition

**Artifacts.** `CLAIM-LEDGER.tsv` (28 rows; claim, section, cited support, re-derived or campaign
evidence, verdict, establishing lane/artifact); `rederive_roadmap_numbers.py`;
`UNAPPLIED-corrections.diff` (7 hunks, 107 lines); `work/emc-treatment-roadmap.md` (the corrected copy
the diff was cut from — a lane-local working file, not a second manuscript).

**Validation.** The re-derivation reproduces every roadmap figure it could reach from the cited
artifact, which is the baseline that makes the one non-reproducing statistic (§4.3) readable. The diff
is proved by `git apply --check --verbose`, **exit 0** (`checks/03`), against the working tree at read
time. **The diff is NOT applied**; `git status --porcelain` on the manuscript is empty.

**Provenance.** All inputs are repository files read read-only at 2026-09-09; the sibling lanes'
`FINDING.md` files supply the campaign verdicts and are cited by lane name in every ledger row.
No network access, no retrieval, no paid resource, no GPU.

**Limitations — load-bearing.**
1. The ledger rules on **support**, not on truth. FALSIFIED means the cited support fails, not that the
   underlying biology is settled — nothing here is an EMC observation.
2. C28 (the categorical-gap claim) was **not** re-derived: `research/data/emc-clinical-registry.json`
   was not opened, and editing the clinical registry is out of lane.
3. C15 (cryptic pocket 0.751) is not re-derivable read-only from any artifact in this repository; it
   is recorded NOT-CHECKABLE-LOCALLY, not disputed.
4. The diff corrects the **worst** offenders only. Ledger rows C05, C06, C10, C11, C13 and C22 are
   recorded but deliberately not patched, to keep one reviewable correction rather than a rewrite.
5. Concurrent writers share this checkout; the diff was cut and checked against one read of the file
   and must be re-checked before any application.

**Stop condition.** Reached. The audit is complete over the manuscript, the diff is proved and
unapplied, and the remaining ledger rows are the owner's decision, not this lane's. The next credible
independent step belongs to PUB-EMC-PROGRAM's owner: decide whether a program paper whose
fusion-addiction class prior has been falsified in owned data can keep that premise in the abstract at
all, or must state it as an open question gated entirely on the dTAG experiment.
