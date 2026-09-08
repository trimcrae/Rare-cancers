# NOTES — HW1 lane, hla-coverage-emc.md regeneration

## 0. State, and verification that my inputs did not move under me

| | value |
|---|---|
| start `date -u` | Tue Sep  8 13:15:38 UTC 2026 |
| start `git rev-parse HEAD` | `d775c80f8e64bc64b67e8c2fb46edeaa2cca2911` |
| start `git status --porcelain` | *(empty — clean tree)* |
| end `date -u` | Tue Sep  8 13:22:42 UTC 2026 |
| end `git rev-parse HEAD` | `1bc583b4a2b81d051d19472a21f018051b93174e` |
| end `git status --porcelain` | 4 modified files, all coordinator work on *other* manuscripts (`degrader/nr4a3-degrader-paper.md`, `fusion-partner/emc-fusion-partner-stratification.md`, `neoantigen/fusion-junction-neoantigen-paper.md`, `occupancy/nr4a3-monovalent-pocket-route.md`) |

HEAD advanced while I worked, as the brief warned. **Verified, not assumed:**
`git diff --stat d775c80 1bc583b -- research/modalities/hla-coverage.json
research/modalities/coverage-curve.json research/manuscripts/neoantigen/hla-coverage-emc.md`
returns **empty** — none of my three inputs changed between the HEAD I read and the HEAD at exit,
and none of them is in the dirty set. Everything below was read at a stable state.

I wrote **nothing** under `/home/user/Rare-cancers`; all output is in `/tmp/claude-0/hw1-lane/`.

## 1. Scope actually delivered

The dispatch asked for Abstract + §3.1 + §3.2. The coordinator's in-flight refinement widened this
to a whole-document coherent projection, and that is what `AFTER-block.md` is: a complete
replacement document — frontmatter, PARKED note, new provenance and evidence-class headers,
Abstract, §1, §2.1–§2.5, §3.1–§3.4, §4, §5, §6, new §7 (history pointer), §8 references.

Counts: `BEFORE-block.md` 362 lines (the whole current file, verbatim); `AFTER-block.md` 479 lines;
`block.diff` 642 lines; `HISTORY-superseded.md` 191 lines; `SOURCE-KEY-MAP.md` 242 lines
(52 prose rows + 3 retained-unverified rows + 164 auto-generated table-cell rows).
Tables in the candidate: **3** — §3.1 global per-allele (4 data rows), §3.2 regional
(16 data rows, 10 columns), §3.3 global curve (4 data rows).
`BEFORE-narrow-abstract-3.1-3.2.md` is the original narrow extract (Abstract + §3.1 + §3.2), kept
so the earlier scope is still adjudicable.

## 2. What changed in substance, not merely in value

1. **The supersession banner no longer sits over live numbers.** The 2026-08-07 banner, the
   superseded Abstract, the superseded §3.1/§3.2, the superseded §2.1/§2.4 allele sets, the
   superseded §4 limitation 3 and the superseded §3.3 paragraph are all reproduced **verbatim** in
   `HISTORY-superseded.md` (proposed live path `hla-coverage-emc-history.md`), and the live body
   points to it from a new §7. Nothing was deleted or reworded. This resolves the exact incoherence
   the coordinator flagged: the banner previously said the both-arms figure was *not computed*
   immediately above corrected prose reporting 1.78%.
2. **The class-I allele sets are now the artifact's.** §2.1 previously named A\*11:01 + B\*08:01
   (e7::e3) and a five-allele all-strong set. The artifact says **B\*15:01 alone** and
   **A\*01:01, B\*07:02, B\*15:01**. Both are corrected, and §2.1 now names the third, *different*
   allele population (the 34-allele scan, which adds A\*30:02) explicitly so the three are never
   cross-quoted.
3. **The class-II arm is one allele, not two.** §2.4 and §4 previously named DRB1\*03:01 and
   DRB1\*07:01 as the strong helpers and carried 28.4% / 16.5%. The artifact's
   `class_ii_cd4_helper_alleles` has exactly one entry, **DRB1\*14:01**; CD4 coverage is **6.49%**
   and both-arms **1.78%**. All four figures are corrected everywhere they appear.
4. **The both-arms figure is reported without a fabricated interval.** `hla-coverage.json` has
   `coverage_cd8_and_cd4_combined` but **no `_95ci` counterpart**. The candidate says so in the
   Abstract, in §2.4 and in §3.1 rather than propagating one.
5. **`null` is rendered as UNKNOWN and the reason is given.** Micronesia has no class-I coverage
   (all three allele leaves `null`); Polynesia has no e7::e3 leaf. The old table printed `n/a` and
   `0.0%` in the CD4 column for Micronesia; the new table prints UNKNOWN for the class-I cells and
   the actual leaf (6.86%) for CD4, and §3.2 explains that these rows are absent data, not low
   coverage.
6. **Unequal denominators are now visible in the table.** A new column reproduces
   `coverage_all_alleles_used` per region, so Polynesia's one-allele 1.95% and Melanesia's
   two-allele 1.37% cannot be read as like-for-like against the twelve three-allele rows.
7. **Evidence classes are separated structurally.** A standing header defines the three kinds of
   statement (predicted binding score / modelled carrier coverage / measured presentation or
   immunogenicity — of which there are none), and the words "predicted" and "modelled" are carried
   into every results sentence rather than dropped after the Methods.
8. **The source is labelled SECONDARY.** §2.2 and §4.3 now say the frequencies come from an AFND
   *mirror*, not AFND, and that mirror lag propagates unchecked.
9. **§3.3 regenerated from `coverage-curve.json`.** The old text said the curve ran
   12.4 → 20.6 → 27.4 → 30.4 and that "no other region exceeds 42.3%" — the leaves give
   12.41 → 20.62 → 27.37 → 30.40, Northern Europe `max_coverage` 61.10% reaching 50% at 2 alleles,
   Western Europe 42.28%. The old claim "90% is unreachable in every region" is replaced by the
   stronger and directly-keyed fact that **every** `alleles_to_reach` entry at 80/90/95% is `null`
   in every region, and all four global thresholds are `null`.
10. **§4 Limitations rewritten to 11 items**, adding: coverage is a projection not an observation;
    the secondary-source/staleness limitation; `null` ≠ 0; small regional samples; and the
    three-denominators rule. Every pre-existing limitation is preserved.

## 3. Qualitative claims dropped, and why

- **"CD8-best regions (Melanesia, East Asia, Oceania) are the CD4-worst" / "anti-correlated".**
  Dropped. The current leaves do not show it: Eastern Asia has both the highest e7::e3 coverage
  (15.40%) and the second-highest CD4 coverage (9.84%); Northern Africa has the lowest computed
  e7::e3 (0.76%) *and* the lowest CD4 (2.46%); the highest CD4 region (Australia and New Zealand,
  14.33%) is mid-table on class I. The candidate states the extremes and explicitly declines to
  compute or assert a correlation, since computing one would be a new statistic.
- **"Melanesia is the CD8-best region" (53.3%) and "e7::e3 rides on A\*11:01, common in East Asian
  and Oceanian populations".** Dropped. A\*11:01 is not in any current allele set; the e7::e3 arm
  is B\*15:01 alone, and the regional ordering it produces is led by **Eastern Asia** (B\*15:01
  regional af 0.0802, the highest of any region), with Melanesia at 0.86%.
- **"Northern Europe 78.9% / Sub-Saharan Africa 35.9%" as the any-strong range.** Dropped;
  the range is now 60.43% (Northern Europe) to 1.37% (Melanesia), with Micronesia UNKNOWN.
  Northern Europe remains the maximum; the minimum region changed entirely.
- **"the full multi-allele panel leaves ~40% uncovered" and "misses ~70% of patients".** Dropped
  as free-standing derived percentages. The candidate makes the same point in words
  ("the clear majority", "well below half") so that no number appears without a key path.
- **"~90% of Sub-Saharan African and Latin American patients" missed.** Dropped: it was a
  complement of the superseded e7::e3 regional values and has no leaf.
- **Micronesia CD4 "0.0%".** Dropped as a claim of zero; the leaf is 6.86%.

## 4. Numbers I could not source, and what I did about them

- **No interval exists for `coverage_cd8_and_cd4_combined`.** Missing input: a
  `coverage_cd8_and_cd4_combined_95ci` leaf (or a stated propagation rule for the product of two
  approximate intervals). Condition that would supply it: `hla_coverage.py` emitting that key on a
  regeneration. I did not compute one. Branch stopped.
- **No regional both-arms figure exists.** `regions[*]` has no combined key. Not printed.
- **§3.4's construct numbers (27 aa, 15 aa, 2 CD8, 1 CD4) live in `vaccine-construct.json`**, which
  is outside the two artifacts I was scoped to read. I retained the subsection verbatim and added
  an explicit reviewer flag that it is **not re-verified in this pass**. Condition that would
  resolve it: an owner (or a follow-up lane scoped to that artifact) re-reading
  `vaccine-construct.json`. I did not open it.
- **§1's `0.495` druggability** comes from `novel-modalities.md` §2; retained verbatim, flagged
  RETAINED / NOT RE-VERIFIED in the key map.
- **The retained note's "44 predicted binders … IC50 66.1 nM"** has no leaf in either artifact. It
  is preserved verbatim in `HISTORY-superseded.md` and is **not** restated in the live body.
- **The `⛔` leaf in `hla-coverage.json` is literally `null`** (`⛔_class_ii_provenance.⛔`), and
  `coverage-curve.json` has no `⛔` field at all. So the dispatch's premise that the artifacts
  carry prediction-only text "in their own `⛔` fields" is **not** borne out at this HEAD. The
  prediction-only framing in the candidate is instead sourced to the artifacts' `_note` fields
  ("strong MHCflurry binder", "MHCnuggets") and `_class_ii_note`, which is what they actually say.
  I did not invent a `⛔` string.

## 5. Verification of the readings the dispatch asked me to check myself

All confirmed by direct read of the JSON leaves (not taken on trust):
`global.coverage_e7e3_public` = 0.0851 ✓; `global.e7e3_public_epitope_alleles` = `["HLA-B*15:01"]` ✓;
`global.coverage_any_strong_binder_allele` = 0.2737 ✓; `global.all_strong_binder_alleles` = 3 alleles
(`HLA-A*01:01`, `HLA-B*07:02`, `HLA-B*15:01`) ✓; `global.coverage_cd4_classii` = 0.0649 ✓;
`global.class_ii_cd4_helper_alleles` = `["DRB1*14:01"]` ✓; `global.coverage_cd8_and_cd4_combined`
= 0.0178 ✓; `global.allele_frequencies` has exactly 4 keys ✓; `coverage-curve.json.panel_size` = 34
with `n_presenting_alleles` = 4 and `global_max_coverage` = 0.304 ✓.

## 6. What I did NOT do

No producer, figure generator, gate or preflight run. No code, patch or test authored. No guard
touched. No network, no paid API, no GPU, no publication, no new source, no new prediction, no
peptide or vaccine-design work, no clinical claim, no contact with humans. No `reports/W25-*` or
W25 continuation read or referenced. No content-policy refusal was encountered in this lane.

## 7. Companion edits a scientific owner still has to decide

`AFTER-block.md` is a whole-document replacement, so it is internally consistent on its own. Two
integration decisions remain and are **not** mine to take: (a) whether the history record lands as
a sibling file `research/manuscripts/neoantigen/hla-coverage-emc-history.md` (the path the
candidate links to) or as an appendix inside the manuscript; (b) whether other documents quoting
the superseded 29.7% / 58.0% / 28.4% / 16.5% figures need the same projection — I did not survey
them, since a repository census is out of scope.

## 8. Disclosure: intermediate scratch files removed

Six intermediate build fragments in this lane (`_part_head.md`, `_part_body.md`, `_part_c.md`,
`_t1.md`, `_t2.md`, `_maprows.md`) were removed after assembly. Their content is **fully and
verbatim contained** in the delivered files: `_part_*.md` concatenate to `AFTER-block.md` and
`_t1/_t2/_maprows` are embedded in `AFTER-block.md` and `SOURCE-KEY-MAP.md`. No campaign evidence
directory, no collected set and no file named in any receipt was touched. Recording it here rather
than leaving it silent; if the collector wants the fragments as separate files they are
reconstructible by splitting `AFTER-block.md` at the `## 1. Background` heading.
