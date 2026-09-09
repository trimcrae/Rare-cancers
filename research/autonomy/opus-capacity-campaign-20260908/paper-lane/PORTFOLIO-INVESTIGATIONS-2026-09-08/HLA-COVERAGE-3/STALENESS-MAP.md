---
id: DOC-PORTFOLIO-INVESTIGATION-HLA-COVERAGE-3-STALENESS-MAP
title: "Staleness map — everything downstream of coverage_scan.py, 2026-09-09"
level: L4
kind: staleness-map
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# Staleness map — `research/modalities/coverage_scan.py`

Machine-readable twin: `staleness-map.json` (48 rows). Generator: `staleness_map.py`, which parses
the producer with `ast` and **never imports or executes it**.

⛔ **Route B8 (HLA-C) is CLOSED.** The producer was not run. No HLA-C allele frequency exists in
this checkout, none was fetched or substituted, and every quantity that would need one is reported
**UNKNOWN — never zero**.

## Verdict key

| verdict | meaning |
|---|---|
| **REPRODUCES** | the current producer would write the committed value |
| **CHANGES** | it would write a different value, and that value is determinable offline |
| **CHANGES_DIRECTION** | it would change or stay; the code fixes the **direction**, the magnitude is not determinable offline |
| **UNDETERMINABLE** | cannot be settled offline at all |
| **AFFECTED_CLAIM** | a prose claim whose truth value moves without a number changing |

Totals: **REPRODUCES 4 · CHANGES 20 · CHANGES_DIRECTION 20 · UNDETERMINABLE 3 · AFFECTED_CLAIM 1.**

## 0 · The drift, stated exactly

`coverage_scan.py` (sha256 `711fbdd7…`) · `PANEL = PANEL_AB + PANEL_C` = **34 + 18 = 52**, loci A/B/C.
`epitope-allele-matrix.json` `panel` = **34**, loci A/B. `epitope-allele-loose-matrix.json` `panel`
= **34**. `coverage-curve.json` `panel_size` = **34**.

**New fact this lane adds:** the committed 34-allele panel is **element-for-element identical to the
producer's current `PANEL_AB`** (verified, `checks/01`). The drift is therefore **purely additive** —
the appended `PANEL_C` block and nothing else. No A/B allele was changed, reordered or removed. That
is what makes most of the directions below derivable at all.

## 1 · Tier 1 — written directly by `coverage_scan.py`

| file · key | committed | verdict | under the current producer |
|---|---|---|---|
| `epitope-allele-matrix.json` · `panel` length | 34 | **CHANGES** | **52** |
| `epitope-allele-matrix.json` · `panel` loci | A, B | **CHANGES** | A, B, **C** |
| `epitope-allele-matrix.json` · `panel` first 34 entries | = `PANEL_AB` | **REPRODUCES** | identical |
| `epitope-allele-matrix.json` · `_note` | "…broad **HLA-A/-B** panel (MHCflurry-2.0)." | **CHANGES** | "…broad **HLA-A/-B/-C** panel…" (producer string literal) |
| `epitope-allele-matrix.json` · `alleles_without_a_model` | **key absent** | **CHANGES** | **key present** — `predict_matrix()` writes it unconditionally, together with `⚠_missing_model_is_not_a_negative`. Its **contents are UNDETERMINABLE offline**: they depend on MHCflurry 2.1.4's own `supported_alleles`. |
| `epitope-allele-matrix.json` · `n_peptides` | 174 | **REPRODUCES** | 174 — peptides come from the untouched breakpoint file |
| `epitope-allele-matrix.json` · `rank_column` | `presentation_percentile` | **REPRODUCES** | same |
| `epitope-allele-matrix.json` · `strong_binders` | 5 rows | **CHANGES_DIRECTION** | **≥ 5** |
| `epitope-allele-matrix.json` · `presenting_alleles` | A\*01:01, A\*30:02, B\*07:02, B\*15:01 | **CHANGES_DIRECTION** | a **superset** of those four |
| `coverage-curve.json` · `panel_size` | 34 | **CHANGES** | **52** |
| `coverage-curve.json` · `_note` | "…HLA-A/-B alleles…" | **CHANGES** | "…HLA-A/-B/-C alleles…" |
| `coverage-curve.json` · `n_presenting_alleles` | 4 | **CHANGES_DIRECTION** | **≥ 4** |
| `coverage-curve.json` · `global_max_coverage` | **0.304** | **CHANGES_DIRECTION** | **≥ 0.304**, magnitude **UNKNOWN** |
| `coverage-curve.json` · `global_alleles_to_reach` | all four targets `null` | **CHANGES_DIRECTION** | each target reached at the same n, an earlier n, or still `null` |
| `coverage-curve.json` · `regions` | 15 sub-regions | **UNDETERMINABLE** | rebuilt from a **live** AFND fetch; unevaluable offline, and the HLA-C half is closed |
| `coverage-curve.png` | committed image | **CHANGES_DIRECTION** | redrawn; changes iff the curve changes |

**Why the direction is fixed and not merely hoped for.** `predict_matrix()` calls
`predictor.predict(peptides=peps, alleles={a: [a] for a in usable})` — **one single-allele sample
per allele**. Each output row's `best_allele` is therefore that allele, and its percentile is
calibrated per allele; adding alleles to the panel adds rows and **cannot alter or remove an
existing row**. `greedy_curve` then keeps only alleles with a non-`None` AFND frequency and
accumulates `1 − ∏(1 − af)²`, which is non-decreasing. So every coverage figure can **rise or stay,
and cannot fall**. How far it rises needs HLA-C frequencies: **route B8, closed, UNKNOWN**.

## 2 · Tier 2 — producers that read `epitope-allele-matrix.json`

These are **second-order**: they are correct on today's tree and go stale only *after*
`coverage_scan.py` is re-run. Verified: `epitope-allele-loose-matrix.json`'s panel is byte-equal to
the strict matrix's (`checks/03`).

| file · key | committed | verdict | under the current producer |
|---|---|---|---|
| `epitope-allele-loose-matrix.json` · `panel` | 34 | **CHANGES** | 52 — `coverage_threshold_curve.predict_loose()` reads `json.load(open(STRICT))["panel"]`, **not** `coverage_scan.PANEL` |
| `epitope-allele-loose-matrix.json` · `calls` | 112 | **CHANGES_DIRECTION** | ≥ 112 |
| `coverage-threshold-curve.json` · `at_conventional_threshold.coverage` | **0.304** | **CHANGES_DIRECTION** | ≥ 0.304 — equal to `coverage-curve.json`'s max **by construction** (asserted in `research/modalities/tests/test_coverage_threshold_curve.py`) |
| `coverage-threshold-curve.json` · `at_conventional_threshold.n_presenting_alleles` | 4 | **CHANGES_DIRECTION** | ≥ 4 |
| `coverage-threshold-curve.json` · `allele_frequencies` | 28 alleles, **A/B only** | **UNDETERMINABLE** | ⛔ **the load-bearing B8 wall.** Whether AFND carries the 18 `PANEL_C` alleles, and at what frequency, cannot be established from this checkout and may not be acquired. |
| `coverage-threshold-curve.json` · `steps` | committed step list | **CHANGES_DIRECTION** | ≥ as many steps |
| `predictor-concordance.json` · `n_panel` | 34 | **CHANGES** | **52** — `predictor_concordance.panel()` returns `json.load(open(MATRIX))["panel"]` |
| `epitope-allele-matrix-mhcnuggets.json` · `panel` | 34 | **CHANGES** | **52** |
| `epitope-allele-matrix-mhcnuggets.json` · `alleles_without_a_model` | committed list | **CHANGES_DIRECTION** | ≥ as many; MHCnuggets HLA-C support is **UNKNOWN** here |
| `vaccine-threshold-calibration.json` · `_panel` | 34 | **CHANGES** | **52** — `panel = strict["panel"]` |
| `stage0-vaccine-item-provenance.json` · `n_alleles_in_the_panel` | 34 (`panel_source: epitope-allele-matrix.json → panel`) | **CHANGES** | **52** |
| `stage0-vaccine-item-provenance.json` · `n_panel_alleles_presenting_anything…` | 28 | **CHANGES_DIRECTION** | ≥ 28 |
| `run-manifest.json` · artifact hashes | as committed | **CHANGES** | new hashes for every file above |

## 3 · Tier 3 — the manuscript, `research/manuscripts/neoantigen/emc-vaccine-development-path.md`

| line | sentence | verdict | under the current producer |
|---|---|---|---|
| 59 | "…a **34-allele panel** for the coverage scan" (§Methods) | **CHANGES** | 52 |
| 267 | "a **34-allele screen** of the same peptides at the same threshold returns **five** strong peptide-allele calls rather than four" (§2.2) | **CHANGES_DIRECTION** | "52-allele"; **≥ five** calls. **Enforced**: `test_vaccine_path_numbers.py` binds `r"a (\d+)-allele screen of the same peptides"` to `len(matrix["panel"])`. |
| 284 | "Screened against the same **34-allele** panel…, those 97 peptides return **10** strong peptide-allele calls across **6** alleles" (§2.2) | **CHANGES_DIRECTION** | 52; ≥ 10 across ≥ 6 |
| 327 | "on **34 alleles** the same lead peptide is also strong on **HLA-A\*30:02**" (§2.3) | **CHANGES_DIRECTION** | "52 alleles"; and **the single-added-allele account may break** — `test_the_broad_panel_adds_exactly_the_allele_the_paper_says_it_adds` asserts exactly one added allele. **UNKNOWN** whether an HLA-C allele would join it. |
| 328 | "gives **27.4%** on ten alleles and **30.4%** on 34" (§2.3) | **CHANGES_DIRECTION** | **27.4% is NOT downstream of `coverage_scan.py`** and does not move; the second figure becomes ≥ 30.4% on 52 |
| 539 | "The **34-allele** screen finds **4** presenting alleles and **30.4%**" (§B1) | **CHANGES_DIRECTION** | 52; ≥ 4; ≥ 30.4% |
| 769 | "On the **34-allele** set the same product gives **2.0%**" | **CHANGES_DIRECTION** | ≥ 2.0% |
| 1110 | "The class I panels remain at **10 and 34** alleles" (§B4) | **CHANGES** | 10 and **52** |
| 1231 | "…tested 174 peptides against **10 and then 34** alleles" (§7) | **CHANGES** | 10 and then **52** |
| 1236 | "0.644% of **59,160** peptide-allele tests" (§7 decoy null) | **CHANGES** | **90,480.** 59,160 = 1,740 decoys × 34 exactly; the denominator is arithmetic in the panel size. The **0.644% rate** over a C-inclusive panel is **UNKNOWN**. |
| 1239 | "presents on a median of **23 of the 34** alleles, a mean of 22.6…, closed form **22.95**" (§7) | **CHANGES_DIRECTION** | denominator **52** is determinate; the closed form is `n_panel × (1−(1−p)^174)` and `p` for a C-inclusive panel is **UNKNOWN** |
| 1290 | "The step function over the **34-allele** panel" (Figure 2 caption) | **CHANGES** | 52 |
| 1332 | "**Table 2. The 34-allele class I panel** … it carries **no HLA-C**…" | **CHANGES** | **52 — and this is the one place the drift produces a WRONG page rather than a stale one.** See §5. |
| 1305 | §8: "Every figure … is generated by a script … and is committed as a JSON artifact beside it, **with one exception**" | **AFFECTED_CLAIM** | the claim acquires a **second** exception |

**Not downstream, and confirmed reproducing:** `hla-coverage.json`'s
`coverage_any_strong_binder_allele` = **0.2737** and `coverage_e7e3_public` = **0.0851** are
produced by `hla_coverage.py` from the breakpoint records' own `binders` list. Both were
independently re-derived to four decimal places in `checks/01`. The panel drift does not touch them.

## 4 · Tier 4 — guards and graph

| where | today | verdict | after a re-run |
|---|---|---|---|
| `research/manuscripts/tests/test_vaccine_path_numbers.py::test_the_panel_the_paper_names_is_the_panel_that_ran` | passes | **CHANGES** | **FAILS** unless every "34-allele screen" site in the prose moves with the artifact. This guard is what converts the drift into a build failure instead of a silent error — **it must not be weakened.** |
| …`::test_the_broad_panel_adds_exactly_the_allele_the_paper_says_it_adds` | passes | **UNDETERMINABLE** | passes **iff** no HLA-C allele presents a strong junction binder. Whether MHCflurry 2.1.4 scores HLA-C at all is **UNKNOWN** and closed (B8). |
| `research/modalities/tests/test_coverage_threshold_curve.py` cross-artifact identity | passes | **CHANGES_DIRECTION** | still passes if **both** curves are regenerated; **fails if only one is** |
| `research/manuscripts/vaccine_path_tables.py --check` | passes | **CHANGES** | reports **STALE** for the `class-i-panel` block |
| `systems/graph/artifact-refs.json`, the `coverage-scan.json` disposition entry | already withdraws any byte-for-byte reproduction endorsement for `coverage_scan.py` | **REPRODUCES** | unchanged — and **corroborating**: this lane is the concrete reason that withdrawal was correct |

## 5 · The one latent defect, not merely staleness

`vaccine_path_tables.panel_block()` builds Table 2 from the matrix panel:

* the header is `f"**Table 2. The {len(panel)}-allele class I panel.**"` — it **would read 52**;
* the body emits **only** `a = [p for p in panel if p.startswith("HLA-A")]` and the matching
  `HLA-B` row. **There is no HLA-C branch.** The 18 C alleles would be **silently dropped**, so the
  table would list **34 alleles under a 52-allele heading**;
* the caption's hard-coded clause "**it carries no HLA-C and no class II allele**" would become
  **false**, and it is not derived from the panel, so nothing would catch it.

This is determinable offline by reading the generator, and it is a defect the paper owner should fix
**before** any re-run, not after.

## 6 · Limitations of this map

1. **The producer was not run.** Every verdict is a source reading. A run could differ if MHCflurry's
   behaviour differs from the code's plain meaning.
2. **`alleles_without_a_model` is the hinge.** If MHCflurry 2.1.4 has no HLA-C models, all 18 C
   alleles land in that field, no C row is scored, and every `CHANGES_DIRECTION` row above resolves
   to *unchanged* — with the artifacts still differing by the panel, the `_note`, and the two new
   keys. If it does have them, the direction is up by an unknown amount. **Which of the two is the
   case is UNKNOWN here and is route B8.**
3. **No ordering is asserted.** All six files arrive in the squashed `-s ours` merge `14a3f172d`;
   whether the producer was broadened after the artifacts were written, or the artifacts were
   written from an older producer, **cannot be dated from this history** and is not claimed.
4. ⛔ **Nothing here is a claim about immunogenicity, presentation, efficacy, safety, selectivity,
   therapeutic window or clinical readiness.** "Coverage" is allele carriage under a model the
   manuscript itself records as unjustified.
