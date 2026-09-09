---
id: DOC-OPUS-CAMPAIGN-PORTFOLIO-PUB-VACCINE-PATH-FINDING
title: "PUB-VACCINE-PATH portfolio investigation — the threshold benchmark: unmeasured, and undersized as preregistered"
level: L4
kind: investigation-finding
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# PUB-VACCINE-PATH — which bottleneck is rate-limiting, and what benchmark would measure it

## 1. The question

`emc-vaccine-development-path.md` §6.1 orders its remaining questions and puts one first:
**defend the acceptance threshold, or record that it cannot be defended** — calibrate the class I
presentation-percentile cut against experimentally validated *fusion-junction* epitopes. Everything
in B1 is "a point on a curve" until that is done, and it is the only step that needs neither an EMC
specimen nor a proteomics facility.

**Question, concretely:** is that step rate-limiting because the validated fusion-junction epitope
set is *absent*, or because the reading was never *taken* — and how large would such a benchmark
have to be before it could distinguish a cut of 0.5 from 0.2 at all?

## 2. Paper-level merit

The cut is load-bearing for the whole route. The manuscript's own numbers: coverage is 0% at 0.2,
30.4% at 0.5, 72.6% at 2.0, and every one of its four presenting-allele calls sits inside a
0.0844-percentile-unit window. A route graded "low coverage" on an undefended convention is graded
on the instrument. The benchmark is public-data-only, needs nobody's permission, is reusable by any
fusion-junction neoantigen programme, and — unlike B2 — is attainable. Patient relevance is indirect
and honest: it decides whether an antigen-directed route in this disease is dismissed on a
convention. **No efficacy, safety, presentation, immunogenicity or readiness claim is made or
implied anywhere below.** A calibrated threshold calibrates a predictor, nothing more.

## 3. The exact evidence gap, and what distinguishes it from completed or held work

The step **was attempted once** (`research/modalities/vaccine-threshold-calibration.json`, run
2026-09-01T20:31:04Z, GitHub-hosted CPU runner). Its decoy-null arm (arm D) succeeded and is what
§7 of the manuscript reports. Its **calibration arm (arm F) returned n = 0**, and the artifact's own
verdict is `WITHHELD ... the size of the validated fusion-junction set was not measured on this run`.

**What I established (offline, from the artifact's own recorded error strings):** all **90** failures
are one and the same client-side defect — a PostgREST `400`, `offset` sent without `order`, on
**90/90** offset-carrying URLs. The 400 body was returned *by the IEDB API*, so the host was
**reachable** on that run. **Arm F's zero is a collector failure, not evidence of absence**, and the
manuscript's fallback reading ("if no validated set exists, that absence is itself the finding") is
**not** currently available to it.

Distinction from prior work: this is not the §7 decoy null (a different arm, which succeeded and is
untouched here); not B2 immunopeptidomics; not a figure or PDF task; not a re-review of the paper;
no denied source, no cohort, no new data. It concerns the *state of one already-attempted
computational step* and the *size of the benchmark it would need*.

## 4. The bounded step taken

`benchmark_sufficiency.py` → `benchmark-sufficiency.json`. Three offline readings.

**(a) Why arm F is empty.** Above: 90/90 `offset`-without-`order` 400s, server reached.

**(b) Static audit of the committed fix.** The defect is **already fixed in the committed script**
(`ORDER_BY = "linear_sequence"`, both paging sites carry `&order=`, 2/2) but **no successful re-run
exists in the tree**, so the reading is still not taken. The audit found a **residual defect**:
`linear_sequence` is *not row-unique* — one peptide recurs across alleles, assays and references —
and limit/offset paging over a non-unique sort key has no total order, so rows can be **skipped** as
well as repeated. `fetch_table`'s `seen` set hides repeats and cannot recover a skip. Arm F's probes
are declared exhaustive (60 × 1000 rows), so a skip lands directly on the preregistered `min_n`
gate as a silent undercount. Row-unique keys **are** present in the schema the run itself recorded
(`mhc_search` → `elution_id`, `structure_id`; `tcell_search` → `tcell_id`, `structure_id`).
Repair stated as an **unapplied** diff: `UNAPPLIED-PATCH-stable-paging.diff`. No tracked file edited.

**(c) How big the benchmark must be — the new quantitative result.** The run preregistered its own
sufficiency gate: **n ≥ 30 epitopes and a 95% CI width ≤ 0.20** on sensitivity at the cut. Those two
criteria are **jointly satisfiable at n = 30 only at near-degenerate sensitivities** — Wilson:
0, 0.033, 0.067, 0.933, 0.967, 1.0; exact Clopper-Pearson: 0, 0.033, 0.967, 1.0. In the regime where
the cut actually matters — an intermediate sensitivity, which is what separates 0.5 from 0.2 — n = 30
**cannot** meet the declared width. Epitopes required for width ≤ 0.20:

| true sensitivity | Wilson n | Clopper-Pearson n |
|---|---|---|
| 0.5 | 93 | 104 |
| 0.7 | 78 | 88 |
| 0.8 | 60 | 70 |
| 0.9 | 34 | 42 |

So the preregistered floor of 30 is **~3× short** at sensitivity 0.5 and short even at 0.9. It is a
floor, not a sufficient size, and quoting it as *the* gate understates the set a defensible cut
would take. For scale, the experimentally validated fusion-junction epitopes the manuscript itself
names are **single-digit** (one SYT-SSX peptide, four *EWSR1*::*FLI1* peptides, a head-and-neck
series); whether IEDB holds tens more is **unknown and is precisely the measurement**.

**Which bottleneck is rate-limiting, on this evidence:** not B2 first. §6.1's step 1 is *not* the
cheap settled prerequisite the ordering assumes — it is unmeasured, its collector has a residual
paging defect, and its preregistered sufficiency gate is undersized for the informative regime. Two
concrete, cheap things stand between the paper and its own step 1, and neither needs tissue.

## 5. Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `benchmark-sufficiency.json`, `benchmark_sufficiency.py`,
  `UNAPPLIED-PATCH-stable-paging.diff`, `checks/` (2 attempts, both preserved).
* **Validation / baseline.** Error classification is exhaustive over all 90 recorded errors
  (90/90 one class; 90/90 offset URLs carry no `order`). Clopper-Pearson intervals are computed by
  bisection on the exact binomial tails and cross-checked against Wilson, which is uniformly
  narrower, as expected. Paging-site audit is a static count over the committed source, 2/2.
* **Provenance.** `research/modalities/vaccine-threshold-calibration.json` (run
  2026-09-01T20:31:04Z), `research/modalities/vaccine_threshold_calibration.py` @ HEAD,
  `research/manuscripts/neoantigen/emc-vaccine-development-path.md` §§2.3, 6.1, 7, B1.
  No network retrieval succeeded; nothing external was ingested.
* **Limitations.** ⛔ No efficacy, safety, presentation, immunogenicity or clinical-readiness claim;
  a threshold benchmark calibrates an instrument and says nothing about any tumour or patient.
  I did **not** measure how many validated fusion-junction epitopes exist — `query-api.iedb.org` is
  unreachable from this sandbox (`CONNECT 403`, `checks/01-iedb-probe`), so that count stays
  **UNKNOWN**; absence is not claimed. The skip risk in (b) is a property of non-unique-key offset
  paging, argued from the schema and the code, **not** observed in a fetch. The sample-size table
  assumes independent epitopes and a simple binomial sensitivity; a paired comparison of two cuts on
  the same epitopes (McNemar) would need fewer, and the circularity the artifact already flags —
  MHCflurry is trained on IEDB — makes any such sensitivity an **upper bound**.
* **Stop condition.** Stopped at the sandbox egress boundary. This lane does not dispatch CI, does
  not commit, and does not edit the tracked script or the manuscript. It stops here.

## 6. Next credible independent work (not done here, not authorised here)

1. Apply the unapplied diff and re-run `vaccine_threshold_calibration.py` on the CPU runner that
   reached IEDB before; the arm F count is then measured rather than withheld.
2. Whatever that count is, compare it against §4(c) rather than against `min_n = 30`, and if it
   falls short, report the shortfall as the finding — a set that cannot resolve sensitivity to
   ±0.10 cannot defend 0.5 against 0.2, and §2.3's curve remains the only honest report of coverage.
3. Consider replacing the absolute floor in the prereg with the width criterion alone, since the
   width criterion already implies a floor and the floor as written can pass a set that fails it.
