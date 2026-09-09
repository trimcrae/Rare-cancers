---
id: DOC-MODALITY-CENSUS-2-DEFECT-CONFIRMATION
title: "MODALITY-CENSUS-2 — independent confirmation of the two MODALITY-CENSUS-1 defects, their full blast radius, and what regenerating the novelty audit actually changes"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: MODALITY-CENSUS-2
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
endpoint: PUB-MODALITY-CENSUS
---

# MODALITY-CENSUS-2 — confirmation, blast radius, regeneration

## Question

MODALITY-CENSUS-1 reported two defects it deliberately did not repair. **Do both re-derive
independently, digit for digit; how far has the false quantifier actually spread; and what would
regenerating `census-novelty-audit.json` today really produce?**

## Merit rationale

A ledger row that says a paper is wrong is only worth acting on if a second reader, working from the
primary artifacts rather than the first reader's ledger, gets the same numbers. Both defects concern
the instrument that the census's own §7 promises is checkable, and one of them — a per-gene universal
quantifier over an anti-apoptotic guardian panel — is exactly the kind of sentence a clinician-facing
reader would take as a per-target statement about which BCL-2-family agent to try. Patient relevance
is indirect and stays indirect: this is a transcript-abundance reading in 16 archival EMC tumours, and
nothing here says anything about efficacy, safety, selectivity, a therapeutic window or clinical
readiness for any agent.

## Evidence gap addressed

MODALITY-CENSUS-1 named both defects and stopped, correctly, at its lane boundary. Three things were
left open and are the gap this lane closes:

1. **No second derivation.** The per-gene deltas, the module mean and its *t*, and the 127-vs-111
   arithmetic existed only in one lane's harness, which had itself been wrong three times.
2. **No blast radius.** Nobody had asked whether the same quantifier appears outside §3.2a.
3. **No idea what regeneration costs.** MODALITY-CENSUS-1 declined to regenerate the audit and did
   not state what regeneration would move — so "just re-run it" was an unpriced instruction.

## Step taken

Three bounded actions, all read-only against shared state, all writes confined to this lane.

### 1 · Both defects re-derived from the primary artifacts — BOTH REPRODUCE EXACTLY

Written from `emc-expression-panels.json`, `systems/graph/modalities.json` and
`census-novelty-audit.json` directly; MODALITY-CENSUS-1's ledger was not read by the harness.

**Per-gene EMC-minus-comparator `mean_z` delta, stored panel group
`panels.apoptotic_dependency.groups.anti_apoptotic_the_druggable_ones` → `gene_reads`:**

| gene | GPL6244 | GPL3290 | lower on both? | GPL6244 Welch *t* (from the artifact's own verdict string) |
|---|---:|---:|---|---:|
| BCL2 | −0.8084 | −0.2349 | yes | −3.703 (|t| ≥ 3) |
| MCL1 | −0.2664 | −0.5563 | yes | −1.930 (**|t| < 2 — the artifact calls it *flat*)** |
| BCL2L1 | −0.3801 | −0.4755 | yes | −2.809 (|t| 2–3) |
| **BCL2L2** | **+0.1231** | −0.0457 | **NO** | **+2.908 (|t| 2–3)** |
| **BCL2A1** | **+0.0371** | −0.5299 | **NO** | +0.506 (flat) |

**3 of 5, not 5 of 5** — identical to MODALITY-CENSUS-1, to the fourth decimal. The producing
artifact's own `gene_reads` verdict strings for BCL2L2 and BCL2A1 on GPL6244 begin **"HIGHER in
EMC"**, in words, so the manuscript sentence contradicts the file it cites.

**Module mean, both platforms** — GPL6244 Δ −0.259, *t* = −4.568, df 14.0, 5/5 readable; GPL3290
Δ −0.4097, *t* = −2.538, df 9.8, 5/5 readable. Both reproduce, and both deltas are internally
consistent with the stored group means (recomputed −0.2589 / −0.4096, rounding only). **The module is
lower in EMC on both platforms. That statement is true; the per-gene universal is not.**

**The denominator:** registry holds **217** class rows, **111** with `prior_coverage ==
never_searched`; `census-novelty-audit.json` still carries `n_never_searched_rows: 127`.
Discrepancy **127 − 111 = 16**, reproducing exactly. **New:** 14 of the audit's 73 finding ids are
rows that are now `searched_before` — the audit is not merely carrying a stale total, it is carrying
14 stale *rows*.

### 2 · Blast radius — the quantifier has SIX live sites, not one

Full list with file and line, plus the near-misses that are correct as written and the frozen
before/after copies that must not be touched: **`QUANTIFIER-SITE-LIST.md`**. In summary the same
false universal is live in the census manuscript (§3.2a), **in a second manuscript**
(`research/manuscripts/dependency/emc-biomarker-selected-classes.md:218`, PUB-BIOMARKER-DEP §2.5),
in the grading **generator** `census_route_expression_grading.py:490` and its generated
`census-route-expression-grading.json:1512`, in **`systems/graph/routes.json:6101`**, and in the
generated view `systems/views/L2-rt-apoptosis-dep.md:23`.

**And it was already caught once.** `research/autonomy/review-seats/PUB-BIOMARKER-DEP-20d33f34…-seat-citations-and-instruments.json`
records this exact defect against PUB-BIOMARKER-DEP §2.5, with the same BCL2L2 *t* = +2.91 this lane
re-derived independently; a second seat adds that the artifact's banding rule calls the GPL6244 MCL1
read *flat*. Neither finding was carried across to the census, the generator or the graph. **The
durable finding is the cross-paper propagation gap, not the arithmetic.**

### 3 · The audit regenerated — into this lane only — and it moves far more than one row

Wrapper `regen_novelty_audit_into_lane.py` imports the tracked generator **unmodified** and redirects
its hard-coded `OUT`; the run asserts the tracked file's bytes and hash are unchanged afterwards
(they are). The generated file was never hand-edited.

| | tracked `research/modalities/census-novelty-audit.json` | regenerated (this lane) |
|---|---|---|
| bytes | **72 747** | **92 678** |
| sha256 | `7ebf72497ff5012375f00e43c8c3fcd8663f36f498aadf87c6022b6102bae78e` | `48779947760a9b655f50da8282a1b4bc3eb9a17f7c707b8a625627ff55415eb0` |

**Every changed line, by kind (`checks/07-audit-regen-delta/stdout.txt`):**

* `n_never_searched_rows: 127 → 111` — the row the task named.
* `n_rows_with_a_candidate_collision: 73 → 72`.
* The four `_what` / `_why` / `_this_decides_nothing` / `_bar` prose keys: **unchanged**.
* **14 finding ids dropped** — all 14 because their registry row is now `searched_before`
  (MOD-ARGININE-DEPRIVATION, MOD-BRACHYTHERAPY, MOD-CS-BIOSYNTHESIS, MOD-DNMT, MOD-EZH2, MOD-HSP90,
  MOD-HYPOXIA-PRODRUG, MOD-ILP, MOD-METRONOMIC, MOD-N-OF-1, MOD-RADIOSENSITIZER, MOD-SEQUENCING,
  MOD-THERMAL-ABLATION, MOD-TRANSCRIPTIONAL-CDK).
* **13 finding ids ADDED** — MOD-ANTICOAGULANT, MOD-BONE-TARGETED, MOD-COSTIM-AGONIST,
  MOD-DIETARY-RESTRICTION, MOD-GLUCOCORTICOID, MOD-HIPEC, MOD-IAP-SMAC, MOD-INTRATUMOURAL-DEPOT,
  MOD-NEXTGEN-CHECKPOINT, MOD-RADIOIMMUNOCONJUGATE, MOD-REPURPOSED-NONONC, MOD-USP1-KAT6, MOD-VDR.
  These are rows still filed `never_searched` that **now collide with repository prose that did not
  exist when the audit was last generated**. Each is an unadjudicated candidate false-negative — the
  exact failure mode the instrument exists to surface.
* **Of the 59 ids present in both, 52 changed** (only 7 are byte-identical), every one of them
  upward: MOD-TF-PROTAC 141 → 414 files, MOD-MRNA-THERAPEUTIC 75 → 282, MOD-SPLICE-SWITCH-ASO
  16 → 157, and so on down to MOD-EGFR 1 → 2.

**⚠ So regeneration is not a one-row cosmetic fix, and this is the part that matters.** The corpus
the generator scans grew by roughly five thousand tracked `.md`/`.json` files (the campaign lanes are
now committed), so nearly every count inflates. Two consequences the paper owner must decide on
before any regeneration is committed:

* **The instrument's circularity guard is now leaky.** `SELF` excludes the census by its canonical
  path only. `MOD-RADIOIMMUNOCONJUGATE`'s only two matching files are **copies of the census
  manuscript itself** under `PARENT-TD1-PATCHES-2026-09-08/BEFORE/` and `TD1-residual-2/before/`.
  The census is now colliding with itself through its own archived before-copies. Regenerating
  without extending `SELF` (and probably excluding `research/autonomy/**` process files) commits a
  self-match as a novelty signal.
* **Regenerating changes an *adjudication surface*, not just a number.** 73 → 72 findings with a
  27-row turnover means the "UNREVIEWED" backlog a reader is asked to work through is a different
  backlog. That is a decision for the census owner, not a lane action.

## Artifacts

* `rederivation-2026-09-09.json` — the independent re-derivation, with re-derived sha256/bytes for all
  four inputs.
* `UNAPPLIED-32a-guardian-quantifier.diff` — **unapplied**; corrects §3.2a to the module statement plus
  the explicit three-of-five split, preserving the superseded wording in a dated
  *Superseded, retained (2026-09-09)* note in the section's own existing style. Verdict text
  ("against at the abundance level") and the candidate status are carried through **unchanged**.
* `census-novelty-audit.REGENERATED.json` — regenerated **into this lane**; the tracked file was not
  written and is byte-identical afterwards.
* `QUANTIFIER-SITE-LIST.md` — six live sites, the correct near-misses, the frozen copies.
* Producers: `rederive_two_defects.py`, `regen_novelty_audit_into_lane.py`, `audit_delta.py`,
  `added_attr.py`, `pergene_t.py` — all in this directory, all reading only committed files.

## Validation

* **`git apply --check --verbose` on the diff → real exit code `0`** (`checks/05-git-apply-check/`).
  **Nothing was applied.** No `git add`, `commit`, `push`, no `preflight.sh`.
* **Regeneration asserts the tracked artifact is untouched** — bytes and sha256 re-hashed after the
  run, `tracked file unchanged: CONFIRMED`, exit `0` (`checks/06-…`).
* **Input hashes match MODALITY-CENSUS-1's recorded ones exactly** across two commits of drift:
  panels `59bccb55…`, modalities `5694cdf7…`, audit `7ebf7249…`, manuscript `d8fd8587…`. Same bytes,
  independently derived numbers.
* **A preserved failed attempt.** `checks/04-regenerate-novelty-audit-into-lane/` is the first
  regeneration run, **killed mid-write by ENOSPC on the harness temp filesystem**
  (`/tmp/claude-0/…/tasks`, 0 MB free); the process emitted no exit code and left a zero-byte output,
  and the Bash tool was unusable for several minutes. It is retained as-is, with the cause recorded in
  its `stderr.txt`. **Nothing was deleted to free space** — per the campaign's evidence-retention rule
  the resource problem is reported, not resolved by cleanup. The retry is check 06.

## Provenance

Repo HEAD `65328136ec847a2ae4192cc8274cb6d5a12a6de2`, `git status --porcelain` showing only untracked
campaign lane directories. Sources: `research/modalities/emc-expression-panels.json` (13 254 759 B),
`systems/graph/modalities.json` (187 400 B), `research/modalities/census-novelty-audit.json`
(72 747 B), `research/manuscripts/modality-census/cancer-modality-census.md` (42 114 B), all re-hashed
at use time by the producer. Local CPU, stdlib only. No GPU, no paid API, no network egress, no
download, no publication or outreach act.

## Limitations

* **This checks re-derivability and internal consistency, not biology.** That the module mean is lower
  in EMC on both platforms is a statement about two archival microarray series (16 EMC tumours across
  GPL6244 and GPL3290), uncorrected for multiple testing, at transcript level. **Apoptotic dependency
  is not an abundance** — the panel file says so itself — and nothing here supports or refutes any
  claim about efficacy, safety, selectivity, therapeutic window or clinical readiness for any
  BCL-2-family agent.
* The per-gene Welch *t* values are **read back from the artifact's own verdict strings**, not
  recomputed from per-sample values; the deltas *are* recomputed from stored `mean_z`.
* The regenerated audit is the tracked generator's output **at today's corpus**. It is not a clean
  re-run of the August instrument, because the corpus changed underneath it, and the self-match leak
  above means at least one of its 13 new signals is spurious. It is evidence about what regeneration
  would do — **not a proposal to commit it**.
* Site search covered `.md`/`.json`/`.py`; raw `.jsonl` transcripts were excluded as capture rather
  than claim surface, so a quantifier occurring only inside a transcript would not appear.
* One reader, one pass, no second grader on the site list.

## Stop condition

**Reached.** Both defects reproduce digit for digit; the quantifier's six live sites are enumerated
with file and line; the diff exists, is unapplied, and passes `git apply --check` at exit 0; the audit
is regenerated into this lane with every changed line accounted for and the two decisions regeneration
forces stated. **This lane applies nothing and commits nothing.** The next steps belong to the paper
owner and the graph coordinator: repair sites 2–6 in generation order, decide whether to extend the
audit generator's `SELF` exclusion before regenerating, and adjudicate the 13 new collisions.

⛔ **Explicitly unchanged, and this is a finding, not an omission:** the `RT-APOPTOSIS-DEP` route
verdict and the `MOD-MCL1-BCLXL` candidate status. The quantifier defect is a prose-precision defect
over a result whose module-level form is true on both platforms; it reverses neither.
