# P-ST correction batch — record, changed files, checks and limitations

**Lane:** sole P-ST correction owner, disjoint from the live FP correction owner.
**Date:** 2026-09-08. **No commit, no push, no subagents.** The parent integrates.
**Repository HEAD read at start:** `c6d97dcc2043bd2a21c749339637286915a29a82`.
**Repository HEAD at the final check:** `a6a21fc591d2451038cdf53449b91e3990d59cfb` (HEAD advances during
this campaign; both were recorded, and the packet hashes were re-verified at the second one).

## 1. Inputs actually read

The verified capsule was read read-only at
`/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/pst-capsule/extracted/`.

- `FINAL-SCIENTIFIC-REVIEW-P-ST.md` — read in full, all 258 lines / 53,772 bytes, including every one of
  the 13 findings, Section 4's minimum coherent repair, Section 5's reopening conditions and Section 7's
  verification accounting.
- `P-ST-final-review-root-adjudication-20260908.md` — read in full, 10,718 bytes.
- `reviewer-calculations.json`, `reviewer-calculations-stdout.txt`, `reviewer-calculations-exit.txt`
  (exit 0), `reviewer_calculations.py`, `reviewed-input-manifest.json/.md`, `collection-log.jsonl`,
  `retained-esummary-excerpts.json`, `inspect_retained_esummary.py`, `TRANSFER-MANIFEST.json` and the
  collection scripts — read for the exact quantities relied on below.
- The frozen manuscripts, at the exact reviewed bytes: main 99,615 B sha256
  `8931895d65bf6cc7de0d83b8cbd6c644b3eb664de221b56861a2a0940584df6f`; SI 41,853 B sha256
  `92a7c49fc406a391d519912108fe888dc499c635ec29d1c3f834445665cdafd1`. Both read in full.
- The artifacts the corrections bind to: `emc-tissue-read-statistics.json`,
  `gse28866-tumour-vs-normal.json`, `geo-gse28866-brunner-series.json` (`series_record.overall_design`,
  read verbatim), `emc-surface-normal-window.json`, `emc-surfaceome-scan.json`, and
  `gse28866_tumour_vs_normal.py` (`_extract` and `_calibrate`, read to establish the aggregation order).

⚠ These artifacts were read selectively and through deterministic parsers at the material records. That
is **not** full source validation, and no reading here reproduces any producer from its public source.

## 2. Deliverables in this directory

| Path | What it is |
|---|---|
| `frozen/` | The exact reviewed input bytes, unaltered, for diffing |
| `revised/emc-surface-target-landscape.md` | Corrected main, 132,856 B, sha256 `ebce0a9db28d3c5a7187a10005fc73b5666232a20a1cd110fa74c59d58bee6e3` |
| `revised/emc-surface-target-landscape-si.md` | Corrected SI, 54,084 B, sha256 `105fc8732dfdb367b6793932b663815f74ae76ea483c1c1daf5a40991794a368` |
| `F01-F13-RESPONSE-MAP.md` | Finding-by-finding response, with what was applied, specified and not done |
| `annotation-correction/ANNOTATION-CORRECTION-gse28866-aggregation-order.md` | The separately identified F03 annotation repair: byte-exact, **specified, not applied** |
| `packet/PACKET-MANIFEST.json` | Versioned, hash-manifested local reproducibility packet, 25 entries, 24,362,783 bytes |
| `execution/apply_pst_correction.py` | Part 1 of the correction: 66 exact-match edits, fails on any non-unique match |
| `execution/apply_pst_correction_part2.py` | Part 2: 5 edits, including the Appendix A7 register |
| `execution/apply-stdout.txt`, `apply-part2-stdout.txt` | Full edit logs with before/after hashes |
| `execution/check_pst_correction.py` | The focused post-correction checks |
| `execution/checks-stdout.txt`, `checks-exit.txt` | The check run: **54 passed, 0 failed, exit 0** |
| `execution/head-at-final-check.txt` | The HEAD the final check ran against |

## 3. Files the parent must change to integrate

Only two tracked files change, and both are this lane's owned paths:

1. `research/manuscripts/surface-targets/emc-surface-target-landscape.md` ← `revised/…landscape.md`
2. `research/manuscripts/surface-targets/emc-surface-target-landscape-si.md` ← `revised/…landscape-si.md`

Two further changes are **specified and deliberately not applied**, because they touch shared artifact
paths this lane does not own:

3. `research/modalities/gse28866_tumour_vs_normal.py` — the `_contrast` string literal (Edit 1)
4. `research/modalities/gse28866-tumour-vs-normal.json` — `per_gene._contrast`, additively (Edit 2)

Nothing else in the tree was touched. In particular `research/modalities/emc-surface-prioritization.png`
and `emc_surface_figure.py` are **unaltered**, as F08 requires; the PNG's sha256 is still
`130042b6afab8aea28874d37dd684cde96886ab25b488ab65b83dac391c439bd` and the check verifies it.

Dependencies the revised text now names, and which the packet manifest carries:
`emc_tissue_read_statistics.py` (the actual statistics generator), its inputs
`emc-expression-panels.json` and `emc-expression-panels-inputs.json`, and its helper dependency
`accession-symbol-cache.json`; plus `emc_expression_panels.py`, `gse28866_tumour_vs_normal.py`,
`emc_surfaceome_scan.py`, `emc_surface_normal_window.py`, `surfaceome_instrument_limits.py`,
`emc_line_data_probe.py`, `emc_gse4303_crosscheck.py`, and `emc_surface_figure.py` for provenance only.

## 4. The checks actually run

Command, from the repository root:

```
python3 research/autonomy/opus-capacity-campaign-20260908/paper-lane/P-ST-correction/execution/check_pst_correction.py \
        . research/autonomy/.../P-ST-correction/revised \
        research/autonomy/.../P-ST-correction/packet/PACKET-MANIFEST.json
```

Result: **54 checks, 54 passed, 0 failed, exit 0**, at HEAD `a6a21fc5`. Full output in
`execution/checks-stdout.txt`. What they cover:

- **Text-to-artifact bindings.** 17 printed *q* values across Tables 3 to 5 match
  `emc-tissue-read-statistics.json`; all 173 significance flags equal `q < 0.05`; six Table S6 rows
  (peaks and all three medians) match `gse28866-tumour-vs-normal.json`.
- **F05 arithmetic recomputed from the artifact**, not copied from the review: 14 GPL6244 and 8 GPL3290
  non-significant rows have ordinary intervals excluding zero; median half-widths 0.25865 and 0.952475.
- **F01 measured in the artifact**: 45 classified records, 45 with both quantitative fields null, 9
  liability labels, and exactly {ALCAM, B4GALNT1, GPC3} RESTRICTED-with-"Detected in many".
- **F02/F07 recomputed**: 47 actionable, 18 flagged, split 10 / 3 / 5, zero up on both, FGFR1 and PTK7
  down on both.
- **F08 omission**: original PNG hash unchanged; no Figure 1 display item; no in-text call; the three
  assertions the image printed appear in live prose only inside the paragraph recording the omission.
- **Withdrawn wording gone from live prose** (18 exact phrases) and **corrected wording present** (16
  exact phrases). "Live prose" excludes the Appendix A register, where superseded wording is retained on
  purpose and must stay quotable.
- **Packet integrity**: all 25 manifest entries exist with matching bytes and sha256.

The two correction scripts are themselves a check: each of the 71 edits must match its anchor **exactly
once** or the script exits non-zero without writing. Two anchors initially failed on whitespace and one
on a Unicode character; those failures are visible in the run history and were fixed by correcting the
anchor, never by loosening the match.

⚠ **What these checks are not.** They are not scientific verification of the paper, not a reproduction of
any producer, not a repository preflight, and not a publication gate. `scripts/preflight.sh` was **not
run** by this lane — no commit is being made from here, and running the commit gate was not in scope.

## 5. Limitations of this batch, stated plainly

1. **The revised paper still needs focused scientific verification and its publication gates.** There is
   no automatic unpark, no approval of a preprint, no release gate cleared, and no claim of current CI
   success. The frozen `9f571e81` candidate's HOLD is not lifted by this batch; what this batch produces
   is the narrower archival comparison the adjudication admitted.
2. **The annotation correction is specified, not applied.** Until the integrating owner applies it,
   `gse28866-tumour-vs-normal.json` still carries the reversed aggregation-order annotation, even though
   the manuscript prose is now correct about the order.
3. **The reproducibility packet is local only.** It is a manifest over in-repository bytes. No public
   immutable locator exists, and none was created or claimed.
4. **Selective reading is not full validation.** The artifacts behind these corrections were read at the
   material records and through parsers. No original public source was re-fetched, so nothing here
   validates that any artifact is a correct derivation from its deposit.
5. **The stronger claims stay parked.** Normal-window validation, a quantified transfer estimate, an
   original-scale sequencing analysis, original-source reproduction, prespecification, joint replicability
   FDR, and any mechanism, protein or compartment assignment all remain unavailable on the evidence in
   hand. None was attempted here.
6. **Two structural risks the revision cannot remove.** The paper still rests on small archival cohorts
   (n = 6, n = 10, 4 libraries) on decade-old platforms with different comparator arms and a disclosed
   GPL3290 reference/RNA-input mismatch; and its central instrument comparison remains a comparison of
   two designs that were never built to be compared. The revision makes both visible; it does not fix
   them.
7. **Word count.** The main text grew from 99,615 to 132,856 bytes, largely in Methods, Limitations,
   Data availability and the new Appendix A7 register. The submission venue's body-length limit was
   search-derived rather than publisher-verified (see the retained editorial note in the manuscript), so
   whether the corrected text needs trimming for format — never for scope — is an open question for the
   integrating owner, and the appendices are already declared as supplementary material.

## 6. Scope discipline observed

No source acquisition, no biological or statistical producer, no raw reanalysis, no geometry, no model
work, no broad corpus preflight, no new review baseline, no closed-route retry, no B4 retry, no
publication, no figure rendering, no HPA query, no artifact regeneration, no subagents, no commit, no
push. Real exit codes were preserved throughout; no check was skipped or weakened.


---

## ⚠ Addendum, 2026-09-08 — focused-verification residual batch R1 to R8

Everything above records the F01–F13 batch as delivered and is retained unaltered. A single focused
verification then held that candidate and set eight residuals. They were applied on 2026-09-08 as one
coherent batch; the residual author's artifacts are in `../PST-residual/`.

**Three statements above are now superseded and are corrected here rather than overwritten.**

1. **Section 3, item 2 — "The annotation correction is specified, not applied."** It is **applied**, once,
   by the sole integrating parent on 2026-09-08. `research/modalities/gse28866-tumour-vs-normal.json` is
   now 28,606 B sha256 `386a035175d94ef8eccd3719d74ef39cff5e93461ed2470983777333a1962cee` and
   `gse28866_tumour_vs_normal.py` is 31,856 B sha256
   `404fe28582d9891a498b5407dc980e5ce7a16ac94a11eee267f7f6b7d8d4b46a`. Receipt and leaf-by-leaf
   invariance record: `annotation-correction/APPLIED-2026-09-08/APPLIED-RECORD.md`.
2. **Section 3 — "Files the parent must change to integrate."** Both manuscript paths have now been
   written with the residual-corrected pair:
   `research/manuscripts/surface-targets/emc-surface-target-landscape.md` (146,042 B, sha256
   `371ec8d92c3238b09f2117e14613184c422db1f094e83f431bad07d46e93179e`) and
   `emc-surface-target-landscape-si.md` (56,124 B, sha256
   `290212776b2f103d64a270f12936245be00bfc6c97f5678b492589bc3680ad16`). No commit or push was made from
   this lane; the parent still integrates. The baseline bytes remain in `frozen/` and in Git history.
3. **Section 4 — the 54/0 check result.** That run is a **historical record of 2026-09-08 at HEAD
   `a6a21fc5`** and is preserved verbatim. Re-running the same checker after the residual batch gives
   **52 passed, 2 failed, exit 1** (`../PST-residual/checks/RUN-08-pst-checker/`). Both failures are
   expected and are being left in place; neither check was weakened. See
   `../PST-residual/CHECK-RUN-RECORD.txt` and `RESIDUAL-LIMITATIONS.md`.

The word-count observation in Section 5 item 7 still applies and the main text has grown further, to
146,042 B, largely in Methods, Data availability and the two dated appendix registers.
