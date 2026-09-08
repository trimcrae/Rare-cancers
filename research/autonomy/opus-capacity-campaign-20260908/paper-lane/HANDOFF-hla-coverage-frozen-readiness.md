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

## ⭐ UPDATED 2026-09-08 — the register conversion, and what it did and did not touch

This handoff now describes the **converted** manuscript. The conversion was one bounded,
reader-facing pass: house glyphs and administrative narrative removed, emphasis cut to load-bearing
sentences, sentence-form headings recast, and standing author and declaration metadata added.

⛔ **Nothing scientific moved.** No prediction, construct, source, threshold or independence
approximation was changed, and no producer was re-run. Proved rather than asserted: the multiset of
numeric tokens in the file before and after the conversion is **identical except for the draft label
`v0.2`, which was then restored**. Every percentage token survives with the same multiplicity, and
the allele identifiers, peptide sequences and artifact key names are unchanged. The only removals
are the frontmatter's backfill placeholder and the word SEPARATE from a heading.

- **Prior version preserved:** the pre-conversion bytes are
  `5ad6ae1b5da8ddfc16df55ba006d4b5c27d69a45e9f735c6d34bec00e95092a4` (47,005 B) at `49ed058e`, and
  the supersession history stays in `hla-coverage-emc-history.md`, 16,259 B, `17b7b078fdf4ee40…`,
  unmodified.
- **Preserved in the converted text and re-checked here:** the maximum e7::e3 coverage 16.11%
  (13.83–18.71%), the minimum CD4 coverage 2.27%, three incomplete and thirteen complete regions on
  the paper's own three-base-allele criterion, the 1.78% product with its all-junction versus
  e7::e3-only scope mismatch stated in the Abstract, section 2.4 and limitation 12, the one
  qualifying class-II allele from a 23-allele panel on one junction, the approximate independence
  step reported as the implemented approximation rather than an exact IEDB formula, and UNKNOWN kept
  distinct from zero throughout.

**Metadata added, all of it truthful.** Tristan D. McRae, independent researcher, unaffiliated,
trimcrae@gmail.com, ORCID 0000-0002-1823-1451; no funding; no competing interests; AI assistance by
Claude (Anthropic) and OpenAI models under the author's direction, the author responsible, and no
human peer review claimed. The ethics wording states that this is an analysis of public data
involving no new recruitment, sampling or intervention, and that no ethics approval was sought or
obtained for it. ⛔ It invents **no** formal "not required" determination and makes **no** broad
"no patient records" claim.

## ⛔ FROZEN — an independent final review is running

The converted manuscript at **47,368 bytes**, sha256
`768398917208449a088c6d2aa9549d9162b4bbc9aa1c3584d13a55c1ac45af0c`, is **frozen** for one required
independent review, `/root/hla_final_ultra` (`gpt-6-astra`, ultra), dispatched by root. ⛔ **Its
science must not be mutated while that review runs.** The corrections below are to THIS HANDOFF's
stale release-gap entries only; the reviewer holds that correction and does not wait for a new
science sha. The reproducibility limit on the missing raw frequency and region-map inputs and the
absent retrieval date stands, and `BLK-ANTIGEN-COLD` stands.

## Exact frozen revision

- **Manuscript:** `research/manuscripts/neoantigen/hla-coverage-emc.md`, **47,368 bytes**, sha256
  `768398917208449a088c6d2aa9549d9162b4bbc9aa1c3584d13a55c1ac45af0c`.
- **Record:** `systems/graph/publications.json` → `PUB-HLA-COVERAGE`, state **`drafted`**, target
  venue **`preprint`**, `outcome_potential: negative_or_methods`, `patient_path: none`, and
  **`blocked_by: BLK-ANTIGEN-COLD`**.

## Complete dependency list, with digests

"Complete" here means what the code actually imports and the inputs it actually reads, established
by reading each producer's imports and path constants rather than by transcribing the manuscript's
links. ⚠ **That correction matters: it adds a twelfth file the link list missed.**

| role | file | bytes | sha256 |
|---|---|---:|---|
| manuscript | `research/manuscripts/neoantigen/hla-coverage-emc.md` | 47,368 | `768398917208449a…45af0c` |
| superseded-values sibling | `research/manuscripts/neoantigen/hla-coverage-emc-history.md` | 16,259 | `17b7b078fdf4ee40…1b5cd3` |
| producer, sections 3.1–3.2 | `research/modalities/hla_coverage.py` | 28,637 | `8631e3f5d450ad72…600074` |
| its artifact | `research/modalities/hla-coverage.json` | 22,890 | `3b40a86392404800…4acf9f` |
| producer, section 3.3 | `research/modalities/coverage_scan.py` | 10,998 | `711fbdd773522303…0f1619` |
| its artifact | `research/modalities/coverage-curve.json` | 12,725 | `eb04c77ad5945083…545acb` |
| its chart | `research/modalities/coverage-curve.png` | 97,719 | `ff10a8bc438a55a5…473609` |
| producer, section 3.4 | `research/modalities/vaccine_construct.py` | 14,832 | `e698896950957378…d98bc2` |
| its artifact | `research/modalities/vaccine-construct.json` | 8,836 | `c61fd8105be1d827…c05d61c` |
| class-I epitope input | `research/modalities/fusion-breakpoint-neoantigens.json` | 46,191 | `ae1ba4f7216a11a9…3eec0c` |
| class-II epitope input | `research/modalities/patient-cd4-demo.json` | 22,737 | `4c60e479d47995ca…d8506e` |
| ⭐ **scan input the link list missed** | `research/modalities/epitope-allele-matrix.json` | 1,517 | `24da5269b71a2d2b…` |

**Code dependencies, read rather than assumed.** `hla_coverage.py` imports stdlib only (`csv`, `io`,
`json`, `math`, `os`, `re`, `sys`, `time`, `urllib.request`) and reads
`fusion-breakpoint-neoantigens.json` and `patient-cd4-demo.json`. `coverage_scan.py` imports stdlib
plus **`hla_coverage` itself**, reusing its AFND fetch, pooling and region resolver, and reads
`fusion-breakpoint-neoantigens.json` and `epitope-allele-matrix.json`. `vaccine_construct.py`
imports stdlib only and reads `fusion-breakpoint-neoantigens.json` and `patient-cd4-demo.json`.

## ⛔ The exact reproducibility limit on the frequency and reference inputs

**The frequency and region-map inputs are fetched at run time and are NOT retained anywhere in this
repository.** Measured: `hla_coverage.py` pulls them over `urllib.request` from
`_source_urls.allele_frequencies` (the `slowkow/allelefrequencies` AFND mirror) and
`_source_urls.region_mapping` (the ISO 3166 / UN M49 table), and a search of `research/` finds no
cached AFND table, no mirror snapshot and no region-map copy. **No retrieval date or timestamp is
recorded either** — `hla-coverage.json` carries `_source_status` "AFND frequencies retrieved from
MIT-licensed mirror" and no date field of any kind.

Stated exactly, because the two halves differ:

- A reader **can** re-derive every figure the manuscript prints, offline, from the committed JSONs,
  because each printed value names its key path. That claim in section 5 stands.
- A reader **cannot** re-run the producers offline to reproduce those JSONs, and **cannot identify
  which upstream snapshot they came from**, because the input was not retained and its retrieval
  time was not recorded. Re-running today would fetch a later mirror state and produce a different,
  later analysis.

⛔ This is recorded as the limit it is. No fetch was performed, no source hunt was opened, and
nothing is reconstructed. It is **not** claimed that no dependency is missing merely because the
manuscript's links resolve.

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
| `lint_style.py <target>` after conversion | this file only, explicit path | **0 ERROR** (was 159 before the conversion) | 0 |
| `lint_consistency.py` | repo-wide, 29 targets | 0 ERROR | 0 |
| `lint_claims.py <target>` | this manuscript | clean | 0 |
| `lint_citations.py` | repo-wide | exits 1; **zero findings name this file** | 1 |
| `test_hla_coverage_seam_provenance.py` | the class-II seam provenance | 8 passed | 0 |
| `test_coverage_threshold_curve.py`, `test_fusion_neoantigen_invalidation.py`, `test_vaccine_path_numbers.py` | the curve, the epitope set, the downstream vaccine-path numbers | 45 passed | 0 |

⭐ **The register measurement is now clean.** Before the conversion an explicit-path
`lint_style.py <this file>` returned 159 ERROR, dominated by em-dash density (79 over 6,133 words =
12.9/1000 against a limit of 6.0); it now returns **0 ERROR**. ⚠ **That is still an explicit-path
measurement, not gate coverage**: this file remains outside `lint_style.TARGETS`, so the gate would
not enforce the register if it drifted again. Adding it is an owner decision and is not made here.

⛔ **One check is now failing because of this conversion, and it is reported rather than absorbed.**
`test_the_paper_states_what_its_own_claims_depend_on.py::test_claim_coverage_has_not_regressed`
compares the committed `claim-coverage.json` against a live census run, and the census now reads this
file at 222 sentences / 113 with a number against the committed 90 / 56. The documented remedy is
`python3 research/manuscripts/claim_coverage.py --write`. ⚠ **I ran it, inspected the result, and
reverted it.** Regenerating rewrites rows for **22 documents**, not one: it would silently absorb
pre-existing drift in the ATR package, the endpoint, mortality and biomarker papers and fifteen
others, several of them frozen or parked under accepted holds. Rewriting a shared deposit artifact
about frozen papers is not inside a register conversion, so the census is left stale and named here
for the owner. ⚠ **The same test was already failing before this conversion**, on
`care-delivery/emc-trial-reachability.md` (101 → 108 sentences), which this work did not touch.
⛔ No guard was edited, no floor moved, and nothing was skipped.

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

6. ⭐ **CLOSED 2026-09-08 — the register conversion is done.** This gap said the document sat in
   repository register and that converting it was an unmade owner decision. It has since been
   converted: explicit-path `lint_style` went from 159 ERROR to **0**, glyphs and administrative
   narrative are out, and the sentence-form headings are recast. ⚠ What remains true is only gap 7:
   the file is still outside `lint_style.TARGETS`, so the gate would not catch a future drift.
7. ⚠ **Neither gate covers it.** It is in neither `lint_style.TARGETS` nor `lint_consistency`'s 29
   targets, and **no pinned figure binds it**; the clean results above are explicit-path measurements
   for the two that apply.
8. ⛔ **No full `scripts/preflight.sh` and no `PREFLIGHT_FULL` receipt** exists for this revision.
9. ⭐ **CLOSED 2026-09-08 — the declarations are complete.** This gap said section 6 was thin and
   carried no ethics statement. Section 6 is now a full Declarations block: author contributions;
   funding none; competing interests none; ethics stated as an analysis of public data with no new
   recruitment, sampling or intervention and no approval sought or obtained for it; AI assistance by
   Claude (Anthropic) and OpenAI models under the author's direction with the author responsible and
   no human peer review claimed; and the not-a-medical-device statement retained. ⛔ It invents no
   formal "not required" institutional determination and makes no broadened "no patient records"
   claim.

## Prior dispositions, carried unchanged

- **N2** audited roughly 140 superseded coverage numbers in the Abstract, §3.1 and §3.2, and the
  parent recorded a blocker rather than patching them, because a per-value patch reintroduces the
  drift the supersession banner recorded.
- **HW1** then produced a whole-document projection rather than piecemeal substitution (362 → 479
  lines, tables generated from the JSON, a source-key map of **242 LINES / MAP ENTRIES** — ⚠ **not
  242 numeric data rows**; the entries are prose values, retained-unverified values and
  auto-generated cells, each naming its artifact and key path), collected **for owner
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
