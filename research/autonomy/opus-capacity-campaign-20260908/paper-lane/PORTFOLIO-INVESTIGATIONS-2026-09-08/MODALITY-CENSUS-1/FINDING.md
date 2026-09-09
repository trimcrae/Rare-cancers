---
id: DOC-MODALITY-CENSUS-1-CLAIM-REDERIVATION
title: "MODALITY-CENSUS-1 — which printed quantities of PUB-MODALITY-CENSUS re-derive from the four artifacts it names, and what does not"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: MODALITY-CENSUS-1
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
endpoint: PUB-MODALITY-CENSUS
---

# MODALITY-CENSUS-1 — first-pass claim re-derivation ledger

## Question

PUB-MODALITY-CENSUS ends with an explicit promise: *"Every count and verdict printed above is
derived from four committed artifacts, and each is re-derivable from them without re-running any
producer."* **Is that promise true, claim by claim — and where it is not, what exactly is missing?**

## Merit rationale

The paper's entire methodological contribution is that a census produces a *checkable denominator*
rather than a recollection. That contribution stands or falls on one property — a reader can
re-derive the numbers. The endpoint has **never had a lane** in either campaign round, and its own
`outcome_potential_why` calls it "the weakest `live_positive` here". If its counts do not re-derive,
the paper has no contribution left; if they do, its weakest-link objection is answered with evidence
rather than argument. Patient relevance is indirect but real: the census is the instrument that
surfaced the PRMT5 route, and a reader deciding whether to act on a "never searched" row needs the
row to be checkable.

## Evidence gap addressed

Not "is the census biology right" — most census verdicts are explicitly judgements, and §6 says so.
The unaddressed gap is narrower: **no lane, review or gate had ever checked, claim by claim, that
the manuscript's printed quantities are recoverable from the artifacts it names.** The §5
reconciliation test is deliberately weak (it asserts each prior sweep is *reached*, not that rows
map), and §2.1 records that `prior_coverage` is checked **in one direction only** — nothing catches a
false negative. So the printed tables were, before this pass, unverified in both directions.

The distinguishing inputs are the four artifacts §7 names — `systems/graph/modalities.json`,
`research/modalities/census-novelty-audit.json`,
`research/modalities/census-route-expression-grading.json`,
`research/modalities/emc-expression-panels.json` — plus
`research/modalities/depmap-sarcoma-dependency.json`, which §3.1/§3.2a's dependency fractions
originate in and which the grading file only restates in prose.

**TD1 reconciliation.** The manuscript was edited hours ago by the TD1 R1–R4 integration
(`6466168d7`), and `.../TD1-residual-2/CHANGED-FIELD-MAP.md` rows MC1 and MC2 record §3.1
annotation-only corrections (the withdrawal of "pan-essential", of the no-therapeutic-window reading,
and of the closed-by-cytotoxic-mechanism reading). **Those are already corrected and are not
re-reported here.** The manuscript hash re-derived at use time,
`d8fd8587bd3306e04ad41309c84efe5f32540f6242397b7c9f1d30a5f4039389`, matches the CHANGED-FIELD-MAP's
recorded AFTER hash `d8fd8587…`, so this pass read the post-TD1 text.

## Step taken

One pass over every quantitative claim printed in the manuscript, re-derived from the committed
artifact it names, at two derivation levels — **READ-BACK** (the value is stored) and **RECOMPUTED**
(the value is a grouped count, a sign test, or the manuscript's own stated rounding rule applied to
stored values) — plus explicit **NOT-RE-DERIVABLE-LOCALLY** rows that name the exact missing input.
The harness is bracketed by a **known-answer control pair** (`CTRL-POS` must REPRODUCE, `CTRL-NEG` —
a deliberately wrong quoted value against the same re-derivation — must MISMATCH); if either comes
out the other way the script exits 3 regardless of the real rows.

### Result

| verdict | rows (controls excluded) |
|---|---:|
| REPRODUCES | 33 |
| MISMATCH | **1** |
| NOT-RE-DERIVABLE-LOCALLY | 2 |

Controls: `CTRL-POS` = REPRODUCES, `CTRL-NEG` = MISMATCH, harness trustworthy.

**Everything structural reproduces exactly.** 217 classes, 19 groups, 4 bands; all seven verdict-table
rows with both their columns (42/1, 8/0, 33/0, 95/86, 20/6, 9/8, 10/10); the 111-of-217 headline and
its 14 live rows; all four band rows including the three shares that required the manuscript's stated
rounding rule (53 %, 69 %, 20 %, 29 % — the 20 % and 29 % that are the paper's own most damaging
self-correction); the 73 audit flags and their all-`UNREVIEWED` status; the 8-class incumbent arsenal;
the 20 surviving candidates, all 20 route-registered; the 95 closures; the 33 `already_rejected`
pointers, every one resolving to a file that exists on disk; the three prior sweeps each reached;
16 graded routes; 479 panel genes on 2 platforms; NDRG1 at the 98th percentile and higher on both;
and the DepMap fractions (CDK7/CDK9 100 % of 91 lines; MCL1 83.5 %, BCL2L1 75.8 %, BCL2 2.2 %) read
back digit-for-digit from `depmap-sarcoma-dependency.json`.

### The one MISMATCH — reported, not repaired

**§3.2a, MCL-1 / BCL-xL row: "all five druggable guardians are lower on both platforms."**
The five are the stored panel group `anti_apoptotic_the_druggable_ones` = BCL2, MCL1, BCL2L1,
BCL2L2, BCL2A1. Per-gene EMC-minus-comparator `mean_z` deltas from `emc-expression-panels.json`
→ `gene_reads`:

| gene | GPL6244 | GPL3290 | lower on both? |
|---|---:|---:|---|
| BCL2 | −0.8084 | −0.2349 | yes |
| MCL1 | −0.2664 | −0.5563 | yes |
| BCL2L1 | −0.3801 | −0.4755 | yes |
| **BCL2L2** | **+0.1231** | −0.0457 | **no — higher in EMC on GPL6244** |
| **BCL2A1** | **+0.0371** | −0.5299 | **no — higher in EMC on GPL6244** |

**Three of five, not five of five.** What *is* lower on both is the **group mean**: the stored module
score is lower in EMC on GPL6244 (Δ −0.259, t −4.568, df 14.0, 5/5 readable) and on GPL3290
(Δ −0.4097, t −2.538, df 9.8, 5/5 readable), and that statement reproduces exactly (row
`S32A-GUARDIAN-MODULE-LOWER-BOTH`). The defect is a **module-level result stated with a per-gene
universal quantifier**. It does not reverse the route verdict — "against at the abundance level" is
what the module result says — and it does not touch the §3.2a table's classification of the class as
*not excluded, still a candidate*. It is a prose-precision defect in a paper whose §7 promises
re-derivability, so it is exactly the kind of claim this ledger exists to catch.

⛔ **Not fixed here.** Any repair is an edit to `research/manuscripts/modality-census/`, outside this
lane, and belongs to the paper owner.

### The two NOT-RE-DERIVABLE-LOCALLY rows

* **§2.1 "the first version said 127, and 15 of those rows were wrong."** The registry holds only the
  post-correction state. 127 − 111 = **16**, not 15, and the manuscript separately records a change
  in total class count (215 → 217) over the same correction, so the arithmetic does not close from
  present artifacts. **Missing input:** the pre-2026-08-09 revision of `systems/graph/modalities.json`,
  or a committed per-row before/after list of the 15 `prior_coverage` flips.
  `census-novelty-audit.json` cannot supply it — it adjudicates nothing, and it still carries
  `n_never_searched_rows: 127`.
* **§1 "four whole categories had been invisible to every previous search."** Restated from the
  2026-08-07 sweep, which is a prose manuscript. **Missing input:** a machine-readable category list
  in that sweep; no census artifact stores one.

### One context finding, not a manuscript defect

`census-novelty-audit.json` still records `n_never_searched_rows: 127` while the registry holds 111
— the audit was not regenerated after the 2026-08-09 novelty correction. The manuscript quotes only
the 73 flag count from that file, and 73 reproduces, so no printed number is wrong. But a reader who
opens the audit to check the 111 headline finds 127 there. Recorded as row `S21-AUDIT-DENOM`; **no
regeneration was run and none is proposed by this lane** (regenerating a shared artifact is outside
the lane, and the file's own noisiness is by design).

## Artifact

`claim-rederivation-ledger.json` — 36 rows (34 claims + 2 controls), each carrying the quoted value,
the source artifact and key, the re-derived value, a verdict, the derivation level, and for the
NOT-RE-DERIVABLE rows the exact missing input. Producer: `rederive_census_claims.py`, in this
directory, reading only committed files and writing only into this directory.

## Validation / baseline

* **Known-answer control pair inside the harness** (`CTRL-POS` / `CTRL-NEG`), both behaving as
  required; a comparator failure forces exit 3.
* **Independent environment baseline:** `python3 research/modalities/instrument_census.py --check`
  → exit 0, "OK (22 instruments, 16 requirements)" (check 05). ⚠ This validates that committed
  JSON artifacts load and check correctly in this environment; it reads
  `instrument-census.json`, **not** the census artifacts, so it is an environment baseline and
  **not** an independent check of any claim in this ledger.
* **Four preserved harness-defect runs.** Runs 01–03 each reported MISMATCHes that were **the
  harness's fault, not the paper's**: `findings[*]` carries `adjudication`, not `status`; the
  three-sweep row compared a 1-key dict against a 2-key dict; and run 03 tested "five druggable
  guardians" against the *route*'s gene list (MCL1/BCL2L1/BCL2/BAX/PMAIP1) rather than the panel
  group the manuscript means. All four runs are preserved in `checks/` with their exit codes. The
  surviving MISMATCH is the one that survived being attacked three times.

## Provenance

Repo HEAD at the start of the pass `673d330446ee07a8db3e83b817d9e619834d4d1f`, at the end
`9a0ee12226deef23fabc72011c64bab9fee18763` — other lanes committed concurrently. **All six source
files were re-hashed at use time and are byte-identical across that move, with an empty
`git status --porcelain`:** manuscript `d8fd8587…`, `modalities.json` `5694cdf7…`,
`census-novelty-audit.json` `7ebf7249…`, `census-route-expression-grading.json` `cbb9c9ac…`
(the post-TD1 hash recorded in CHANGED-FIELD-MAP), `emc-expression-panels.json` `59bccb55…`,
`depmap-sarcoma-dependency.json` `d88bed62…`. The hashes are re-derived by the producer on every run
and stored in the ledger.

## Limitations

* **This checks re-derivability, not truth.** A number that reproduces from an artifact is faithful
  to that artifact; whether the artifact is right about biology is a different question this pass
  does not touch.
* **It says nothing about efficacy, safety, selectivity, a therapeutic window or clinical
  readiness**, for any modality class, and no such claim appears here or in the artifact.
* **Non-quantitative claims are out of scope** — the census's mechanism-versus-biology `excluded`
  arguments are judgements and are not gradeable this way.
* Two rows required a reading the artifacts do not store: "live" is not a field (re-derived as
  candidate + parked_capability, the only reading that reproduces and the one the verdict table's own
  6+8 split implies), and the three prior sweeps are named in prose, not by path (identified from §1
  plus the `prior_ref` distribution). Both readings are recorded in the ledger notes.
* `S21-20-CANDIDATES-ADJUDICATED` checks only that there are 20 candidate rows; whether each carries
  an adjudication of its audit flag is a prose property with no schema field.
* One pass, one reader, no second grader.

## Stop condition

**Reached.** The question is answered: 33 of 36 gradeable quantities reproduce digit-for-digit, one
mismatches, two are not locally re-derivable with their missing inputs named. The lane stops here.
The next credible independent step belongs to the paper owner, and it is **not** more re-derivation:
it is (a) deciding the §3.2a quantifier — the honest form is "the druggable-guardian module is lower
in EMC on both platforms", with the per-gene split stated — and (b) deciding whether §2.1's "15" is
recoverable from Git history or should be restated as a range. Neither is this lane's to make.

## Compute and storage

Local CPU only: five Python runs, each under two seconds, plus JSON reads of at most ~9 MB
(`emc-expression-panels.json`). No GPU, no network egress, no paid API, no download, no publication
act. Storage written: **156 KiB**, entirely inside this lane directory. No file outside the lane was
created, edited or deleted; no shared file needed changing, so no unapplied diff is attached.
