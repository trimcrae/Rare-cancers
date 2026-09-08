---
id: DOC-OPUS-CAMPAIGN-FROZEN-HLA
title: "Frozen final-readiness handoff — modelled HLA coverage of predicted junction binders"
level: L4
kind: memo
status: live
purpose: >
  Hand the corrected HLA coverage manuscript to root's scientific acceptance with its exact frozen
  revision, its complete dependency list with digests, its source provenance, the checks that
  actually ran with their real scope, and every unresolved scientific and release gap.
scope: >
  L4. A readiness handoff. It edits no science, runs no producer for a receipt, authorises no
  publication act, and asserts no green gate.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Frozen handoff — `neoantigen/hla-coverage-emc.md`

## Exact frozen revision, verified rather than assumed

- **Manuscript:** `research/manuscripts/neoantigen/hla-coverage-emc.md`, **47,005 bytes**, sha256
  `5ad6ae1b5da8ddfc16df55ba006d4b5c27d69a45e9f735c6d34bec00e95092a4`, title *Modelled HLA coverage of
  predicted EWSR1::NR4A3 junction binders in extraskeletal myxoid chondrosarcoma*.
- **Last touched at `5f442c85`** ("HLA: integrate the corrected coverage manuscript and its history
  sibling"). ⭐ **Checked, not forced:** the file's current bytes on this branch hash identically to
  the bytes at both `5f442c85` and `0e542b84`, so there is no later integrated correction to prefer
  and the earlier hash is still the live one.
- **Record:** `systems/graph/publications.json` → `PUB-HLA-COVERAGE`, state **`drafted`**, target venue
  **`preprint`**, `outcome_potential: negative_or_methods`, `patient_path: none`, and — see gaps below
  — **`blocked_by: BLK-ANTIGEN-COLD`**.

## Complete dependency list, with digests

Eleven files, **328,829 bytes** total. Small enough to travel whole; no cache, sandbox copy or
regenerated intermediate is included, and nothing was deleted to make room (19 GiB free on this
volume, well above the 10 GiB floor).

| role | file | bytes | sha256 |
|---|---|---:|---|
| manuscript | `research/manuscripts/neoantigen/hla-coverage-emc.md` | 47,005 | `5ad6ae1b5da8ddfc…95092a4` |
| superseded-values sibling | `research/manuscripts/neoantigen/hla-coverage-emc-history.md` | 16,259 | `17b7b078fdf4ee40…1b5cd3` |
| producer (§3.1–§3.2) | `research/modalities/hla_coverage.py` | 28,637 | `8631e3f5d450ad72…600074` |
| its artifact | `research/modalities/hla-coverage.json` | 22,890 | `3b40a86392404800…4acf9f` |
| producer (§3.3 curve) | `research/modalities/coverage_scan.py` | 10,998 | `711fbdd773522303…0f1619` |
| its artifact | `research/modalities/coverage-curve.json` | 12,725 | `eb04c77ad5945083…545acb` |
| its chart | `research/modalities/coverage-curve.png` | 97,719 | `ff10a8bc438a55a5…473609` |
| producer (§3.4 construct) | `research/modalities/vaccine_construct.py` | 14,832 | `e698896950957378…d98bc2` |
| its artifact | `research/modalities/vaccine-construct.json` | 8,836 | `c61fd8105be1d827…c05d61c` |
| class-I epitope input | `research/modalities/fusion-breakpoint-neoantigens.json` | 46,191 | `ae1ba4f7216a11a9…3eec0c` |
| class-II epitope input | `research/modalities/patient-cd4-demo.json` | 22,737 | `4c60e479d47995ca…d8506e` |

⭐ **No essential input is missing.** Every file the manuscript's §5 names resolves on disk at the
digests above, and no dependency had to be reconstructed, searched for or invented.

## Source provenance and reproducibility, with its actual weaknesses

`hla_coverage.py` fetches two public sources — the AFND allele frequencies via the MIT-licensed
`slowkow/allelefrequencies` mirror and an ISO 3166 / UN M49 region map — and reads the committed
class-I and class-II epitope JSONs for presenting alleles. ⚠ The artifact's `_source_status` records
only *"AFND frequencies retrieved from MIT-licensed mirror"*: **it is a secondary source with no
retrieval date recorded here**, so mirror lag, AFND revisions and survey composition propagate
unchecked. The manuscript states this as limitation 3. If a source is unreachable the script records
`source_unavailable` rather than emitting a number.

⛔ **No producer was re-run to prepare this handoff**, and the manuscript's §5 says the same of the
text: every figure is read from the committed artifacts as they stand. A regeneration against a
refreshed upstream mirror would be a **different, later version** of this analysis, and is explicitly
not a precondition for reviewing this frozen one.

## The four corrected quantities, re-derived here from the artifact

Read out of `hla-coverage.json` by the parent, not taken from the lane's report:

- **Maximum e7::e3 coverage: Northern Europe 16.11 % (95 % CI 13.83–18.71 %)** —
  `regions["Northern Europe"].coverage_e7e3_public = 0.1611`, CI `[0.1383, 0.1871]`, and it is the
  maximum across all 16 sub-regions.
- **Minimum CD4 class-II coverage: Sub-Saharan Africa 2.27 %** —
  `coverage_cd4_classii = 0.0227`, CI `[0.0165, 0.0308]`, the minimum of the 16.
- **Three incomplete, thirteen complete.** ⚠ On the manuscript's own criterion — carrying all three
  base class-I alleles in `coverage_all_alleles_used` — Polynesia, Melanesia and Micronesia are
  incomplete and thirteen regions are complete. A looser criterion (any missing coverage value) gives
  2/14 and is **not** the one the paper uses; I checked the paper's definition rather than assuming.
- **1.78 % is a product across mismatched scopes.** `coverage_cd8_and_cd4_combined = 0.0178` =
  0.2737 × 0.0649, where the class-I factor is pooled over binders of **all resolved junctions** and
  the class-II factor screens the **e7::e3 junction only**. ⛔ It is **not** joint eligibility for one
  construct and not a requirement a durable response must meet. The manuscript says exactly this in
  the Abstract and in limitation 12.
- **The independence step is reported as the implemented approximation, not as an exact IEDB
  formula.** §2.3 states that the artifact's `_method` cites IEDB but that the expression multiplies
  terms for B\*07:02 and B\*15:01 — two alleles at the **same locus** — which cross-locus independence
  does not license, and that the direction and size of the bias are **not established**.

## Checks that actually ran, with their real scope

| check | scope | result | exit |
|---|---|---|---|
| `lint_style.py` | the repo gate's own TARGETS | 0 ERROR across 15 files | 0 |
| `lint_consistency.py` | repo-wide, 29 targets | 0 ERROR | 0 |
| `lint_claims.py <target>` | this manuscript | clean | 0 |
| `lint_citations.py` | repo-wide | exits 1; **zero findings name this file** | 1 |
| `test_hla_coverage_seam_provenance.py` | the class-II seam provenance | 8 passed | 0 |
| `test_coverage_threshold_curve.py`, `test_fusion_neoantigen_invalidation.py`, `test_vaccine_path_numbers.py` | the curve, the epitope set, the downstream vaccine-path numbers | 45 passed | 0 |

⚠ **An off-target measurement, reported as such and NOT as debt.** An explicit-path
`lint_style.py <this file>` returns 159 ERROR, dominated by em-dash density (79 over 6,133 words =
12.9/1000 against a limit of 6.0). **This file is not in `lint_style.TARGETS`**, and that gate's own
header says the house style is correct everywhere else in the repository, so this is a measurement of
register, not a failing gate and not a defect. It is a **release** question, listed below.

## Unresolved scientific and release gaps

**Scientific, and owned by root:**

1. ⛔ **`BLK-ANTIGEN-COLD`.** The publication record lists this paper as blocked by it: *EMC is
   antigen-cold, and the fusion junction is a weak peptide-HLA* — a `fundamental_biological_limit`
   owned by `neoantigen/immunotherapy-options-emc.md`. The manuscript's own framing is consistent
   with it (limitation 1, and `outcome_potential_why`: "a population ceiling computed for an epitope
   whose presentation is unestablished"). Whether a paper under that blocker is releasable is root's
   call, not this handoff's.
2. **The independence approximation is unresolved**, by the paper's own statement — not quantified,
   not signed off, and not claimed conservative.
3. **The class-II arm rests on one qualifying allele** (DRB1\*14:01) from a 23-allele panel on one
   junction; the manuscript refuses to read 6.49 % or 1.78 % as clinical "at least" statements.
4. **Predicted, not observed.** Every binder is a prediction; the allele frequencies are observed
   surveys. The paper keeps those two apart and states there is **no wet lab** and therefore no
   measured presentation or immunogenicity anywhere in it. ⛔ **No patient eligibility and no efficacy
   claim is made or implied here.**
5. **Three sub-regions are incomplete and `null` is UNKNOWN, not zero**; four regions have small
   survey bases (Micronesia 129 individuals, Polynesia 450, Australia/NZ 702, Melanesia 1,269).

**Release, and owned by the author:**

6. ⚠ **Register.** The document is in repository register, not journal register (see the off-target
   measurement above). If it goes out as a preprint, a register conversion is the same class of work
   the biomarker paper needed — an owner decision and an authorship act, deliberately not made here.
7. ⚠ **Neither gate covers it.** It is in neither `lint_style.TARGETS` nor `lint_consistency`'s 29
   targets, and **no pinned figure binds it**; the clean results above are explicit-path measurements
   for the two that apply.
8. ⛔ **No full `scripts/preflight.sh` and no `PREFLIGHT_FULL` receipt** exists for this revision.
9. **Declarations exist but are thin** (§6: AI assistance, no funding, no competing interests, not a
   medical device). There is no ethics statement of the form the biomarker and mortality papers now
   carry. Adding one is ordinary metadata, not a scientific change, and is left to the owner with the
   rest of the release decision.

## Prior dispositions, carried unchanged

- **N2** audited roughly 140 superseded coverage numbers in the Abstract, §3.1 and §3.2, and the
  parent recorded a blocker rather than patching them, because a per-value patch reintroduces the
  drift the supersession banner recorded.
- **HW1** then produced a whole-document projection rather than piecemeal substitution (362 → 479
  lines, tables generated from the JSON, a 242-row source-key map), collected **for owner
  adjudication** in [`COLLECTION-HW1-hla-regeneration-candidate.md`](COLLECTION-HW1-hla-regeneration-candidate.md).
  It was integrated at `5f442c85`, which is the revision frozen here.
- **S29-HLA-STALE** (2026-09-01) records the 3-vs-23 class-II panel defect in `hla-coverage.json` and
  the systems graph, and how a fixed generator shipped a stale artifact for four days under green
  gates. The corrected 23-allele panel is what `_class_ii_note` now enumerates.
- ⛔ **HW1's deleted intermediate fragments stay explicit.** §7 records that the build lane deleted
  six intermediate working fragments after assembly, that containing the content is not proof the
  original bytes survive, that they were not recovered, and that they are **deliberately not
  recreated**. That limitation travels with the document and is **not** re-audited here.

## What this handoff is not

⛔ It is not publication permission, not a reviewer record, and not a claim that any gate is green. It
is **not** authority for new peptide or construct design, new source searches, recreation of any HLA
survey, or any held source or figure validation route. Root owns scientific acceptance and the one
required independent review when the package is ready.
