# FP correction — remaining blockers, preserved failures, and what the parent owns

2026-09-08. ⛔ Nothing here clears a publication gate. The frozen `f44b75588` candidate remains PARKED; this
is the narrower descriptive revision, and its release stays subject to its existing separate gates.

## 1 · Does meaningful standalone merit survive the removals? — YES, narrowed

After removing every source-unverified quantity, what remains is a coherent, useful paper:

- **Response** (§3.1): drug-specific recorded response proportions with their differences and real
  imprecision, the 26/23/22 analysis-population flow, the conditional-mixture framing, the restored Davis
  classification at secondary provenance, and the explicit statement that a treated-only comparison cannot
  establish a treatment interaction.
- **Outcome** (§3.3): one source-verified series' recorded per-partner event counts and observation windows,
  the unknown-cause death kept distinct, and four further series reported at their own scope — including
  Sjögren's corrected 0/3 vs 1/5.
- **Prevalence** (§3.5): 28/154 = 18.2 % (12.9–25.0) over four series whose partner counts are now **all**
  source-verified, with the four-denominator ascertainment flow shown per series and no signed missingness.
- **Mechanism and preclinical** (§3.6–3.7): bounded to the designs used, with the GSE28866 ratios stated at
  their actual deposited, square-root-compressed scale.

⚠ **What it no longer claims is the thing it used to lead with**: there is no pooled prognostic magnitude and
no size-confounding story. The paper is now an accounting of a small selected evidence base, which is what the
review said the defensible contribution was.

## 2 · PRESERVED FAILURE — the prose-binding guard suite (NOT repaired, NOT exempted)

```
python3 -m pytest research/manuscripts/tests/test_emc_fusion_partner_pooling_check.py \
  research/manuscripts/tests/test_fusion_partner_prose_matches_its_artifact.py \
  research/manuscripts/tests/test_fusion_partner_prose_asserts_the_relations_its_artifact_computes.py \
  research/manuscripts/tests/test_fusion_partner_author_years_are_bound_to_the_citation_map.py \
  research/manuscripts/tests/test_the_fusion_partner_gene_identifiers_are_ones_an_artifact_names.py -q
→ 107 failed, 75 passed        PYTEST_EXIT=1
```

Full streams: `execution/pytest-fp-checks-stdout.txt`, `execution/pytest-fp-checks-summary.txt`.

⛔ **No guard was edited, floored, exempted, skipped or rerun to green.** The failure is honest and it is
explained, not hidden:

- **`test_fusion_partner_prose_matches_its_artifact.py` and
  `test_fusion_partner_prose_asserts_the_relations_its_artifact_computes.py`** bind *individual sentences of
  the frozen candidate* to *individual artifact fields*. Both the sentences and the fields were deliberately
  removed by this correction, so essentially every assertion addresses text that no longer exists. **These
  guards are instruments calibrated to the parked paper, not detectors reporting a defect in the new one.**
- **`test_emc_fusion_partner_pooling_check.py`** — 5 failed, 4 passed. All five fail in *setup*, with
  `KeyError: 'disease_specific_death'` / `'strata'`, because they perturb the withdrawn Huang nodes. The
  behaviour they exist to guard was therefore left unmeasured by them, so it was demonstrated separately and
  the record preserved at `execution/check-writes-nothing-demonstration.txt`: perturbing a **live** pooled
  count makes `--check` exit **1** and leave the perturbed file untouched, and the unperturbed artifact
  passes `--check` with exit **0**.
- **Passing:** `test_fusion_partner_author_years_are_bound_to_the_citation_map.py` (5 passed) and
  `test_the_fusion_partner_gene_identifiers_are_ones_an_artifact_names.py` (10 passed), both clean.

**This is the one irreducible blocker of this correction, and it is scoped, not open-ended.** Re-binding a
~2,400-line per-sentence guard suite to the corrected prose is a distinct, sizeable job with its own risk
profile — it is exactly the kind of work that must not be done in the same pass as the scientific correction,
because a guard rewritten by the same owner in the same breath as the prose it checks stops being an
independent check. **Recommended:** the parent assigns it as a separate scoped task, with the corrected
manuscript and artifact as fixed inputs.

## 2a · One observation that is NOT this lane's

The tracked-tree guard reported at the end of the pytest run that the run changed
`research/autonomy/opus-capacity-campaign-20260908/paper-lane/FO-pdf-production/evidence/76-FINAL-squashed-content-diff.txt`.
⛔ That file belongs to the concurrently running FO PDF renderer's lane, not to this one, and nothing in this
correction touches it. It is reported rather than acted on: this owner did not modify, revert or delete it.
The FP artifact was verified intact immediately afterwards — `--check` exits **0** and the artifact hash
matches `execution/AFTER-hashes.txt`. The parent may want to check it against the FO owner.

## 3 · The parent owns these

1. **The FP publication-graph entry** (`systems/graph/publications.json`:237). It still carries the novelty
   copy F10 narrows and, if it restates the withdrawn pooled magnitude, the F12 withdrawal. ⛔ Not edited
   here: shared graph state is the parent's, and this owner does not touch it.
2. **Integration** — commit and push. This owner made no commit and no push.
3. **Assigning the guard re-binding** described in §2.
4. Any downstream FP producer or artifact summary outside the four files listed in the manifest.

## 4 · Reopening evidence, recorded so it is not lost

- **Huang 2023 Table 1** reopens the withdrawn outcome analysis if an authentic original is supplied, or an
  authoritative source is obtained through a **separately authorised** ordinary route and verified cell by
  cell. ⛔ A contemporaneous extraction record must **not** be reconstructed from the quarantined values in
  `cohorts[huang-2023-outcome].withdrawn_2026_09_08` and labelled an original. The paper's own §6 lists it
  as the second of six observations that would reduce the uncertainty.
- **Stacchiotti 2019** (pazopanib full text) would supply the partner-by-analysis-population flow §3.1 marks
  as unaccounted.
- **Paioli 2021** full text would supply per-partner event counts and the adjustment structure §3.4 marks as
  unknown.

## 5 · Execution boundary honoured

⛔ No source retrieval. No new biological analysis. No patient-level reconstruction beyond published retained
records. No new model. No random-effects or CMH selection. No source-query expansion. No broad test sweep. No
hypothesis search. No new structural work. No shared-graph edit. No scientific rewrite of any other paper.
One scoped producer update and one regeneration, both recorded with exact commands, streams, exit codes,
before/after hashes and a full numeric-leaf delta.
