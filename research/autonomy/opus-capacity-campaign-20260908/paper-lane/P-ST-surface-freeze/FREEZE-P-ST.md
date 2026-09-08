# P-ST — surface-target main and SI, frozen for one final scientific review

**Owner:** P-ST paper owner (sole), admitted by root as execution.
**Date:** 2026-09-08. **Baseline:** HEAD `aca13df91`, both manuscripts clean at HEAD before this work.
**Scope edited:** `research/manuscripts/surface-targets/emc-surface-target-landscape.md` and
`emc-surface-target-landscape-si.md`, in place. Nothing else was edited. No commit, no push, no
producer run, no figure rebuild, no source fetch, no new cohort, no prediction, no spawned agent.
`research/manuscripts/submission-metrics.json` was regenerated as a side effect of running
`submission_metrics.py` twice and was restored with `git checkout --` both times; it is unmodified.

## What the reviewer is being asked to review

One reader-facing main text and one SI, corrected against the retained measurement artifacts. The
corrections are listed with their superseded wording in **Appendix A6** of the main text and in the
"Superseded, retained" blocks of SI Notes S1, S3 and S5 and SI Table S7.

## Per-file hashes at freeze

| file | bytes | sha256 |
|---|---:|---|
| `research/manuscripts/surface-targets/emc-surface-target-landscape.md` | 99615 | `8931895d65bf6cc7de0d83b8cbd6c644b3eb664de221b56861a2a0940584df6f` |
| `research/manuscripts/surface-targets/emc-surface-target-landscape-si.md` | 41853 | `92a7c49fc406a391d519912108fe888dc499c635ec29d1c3f834445665cdafd1` |

### Necessary unchanged dependencies (read-only, untouched by this work)

| file | bytes | sha256 |
|---|---:|---|
| `research/modalities/emc-tissue-read-statistics.json` | 90201 | `3213777eefcea5c62f5cda457ca9e391dc63e7740ed58ec2aadf3cf120f12317` |
| `research/modalities/emc-surfaceome-scan.json` | 46945 | `3180c4ba550350967f157fd9a1f15d13bd84e233c7fa16b3d2266842d0cb63c0` |
| `research/modalities/emc-surface-normal-window.json` | 34621 | `0787c7f7279562dcd9eca96a0ae4578a27773477e21f2e8ae940200c25b09aab` |
| `research/modalities/surfaceome-instrument-limits.json` | 15501 | `1db6d18d91f074efddf4d2f2ed6b7d8daecf5d44a9d70801b872296433142e94` |
| `research/modalities/emc-expression-panels.json` | 13253561 | `123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9` |
| `research/modalities/aso-delivery-antigen.json` | 53488 | `eab3a6f5a7d7bcf6271bda3b3f0580b06e0d90bc553d5b75038af43eb4070287` |
| `research/modalities/gse28866-tumour-vs-normal.json` | 27256 | `ac0a17bd81dd8bc2ecc3b5bb380de5ae00921ae2d32b5a9595bd1449720be407` |
| `research/literature/remaining-reference-metadata-2026-08-09.json` | 14227 | `422d30a2ddc853fd55e5eb4bcb5c089194583f8484195a5afbedb969b7083e3f` |
| `research/literature/submission-reference-metadata-2026-08-09.json` | 20018 | `7e313379b8febd2de8b16af17153c0ba381cfbe5bb5169a876b819d0dace0c0e` |
| `research/literature/emc-prior-art-2026-08-09.json` | 6597 | `3c45960a14a99ce739b7643c2f73705e3d0b8900841af1a289f9e534379d4112` |
| `checks/check_bindings.py` (this lane's checker) | 15002 | `8881fcb83fa8a75f6f82a19b997575e2d0591b86a031fda6a8c06b741f87ab65` |

The two statistics artifacts match the byte counts and hashes root read directly. The manuscripts were
built from the artifacts, not from the rejected diff; the preserved `NOT-ACCEPTED-surface-targets/`
directory and its `working-copy.diff` were read for their claim list only and were **not** applied,
restored or modified.

## D2 — nine versus eighteen, resolved by defining the sets

Both numbers are kept, each only where its own denominator applies.

- **Nine** = selectivity-significant antigens **within the classic-antigen subset of Table 1**:
  CDH11, KIT, CD248, FGFR1, NCAM1, GPC2, PTK7, MCAM, EPHB4. (The paper previously said eight; it had
  omitted CD248, which carries `selectivity_significant: true` at q = 0.0.)
- **Eighteen** = selectivity-significant antigens **within the whole retained actionable set of 47**:
  the nine above plus ALK, DLL3, ENPP1, FGFR4, PDGFRA, PDGFRB, ROR1, SLC34A2, STEAP1.

Every overall claim about "the surrogate-selective antigens" now covers all 18 and says so. The two
estimands are stated as nested, not contradictory. The disclosure the full-set claim requires is made
explicitly in the Abstract, Results, Table 3, Limitations and SI Note S5: **five of the 18 — ALK,
ENPP1, FGFR4, SLC34A2, STEAP1 — were never placed on the 100-gene cross-platform board and have no
EMC-tissue reading at all**, and **six of the 18 — those five plus PDGFRA — carry no normal-tissue
prior record** (SI Table S2 footnote). Neither absence is read as a negative.

Consequence for the intersection claim: over the classic subset the selective-and-restricted
intersection is empty, as before. Over the full retained set it is **not** empty — it contains exactly
DLL3 (q = 0.0079, window RESTRICTED). Both statements are printed, each with its denominator, and
Figure 1's caption now records that the figure plots the classic subset and does not plot DLL3.

## D1 — the real statistics integrated, direction kept separate from evidence

Integrated throughout Methods, Results, Limitations, Tables 3–5 and SI Methods S7 / Tables S5, S7 /
Note S3: the correction policy (BH within platform, alpha 0.05, corrected separately per platform),
the exact p, 95 % CIs and q values, the corrected cross-platform states, the resolution figures
(24/95 and 16/78 significant; median CI half-width 0.259 and 0.957 SD), and all three sensitivity
analyses (reference-matched GPL3290 DFSP-only; GPL6244 with solitary fibrous tumour; the normal
skeletal-muscle anchor with its own disqualifying control).

- Concordantly increased set under the stored criterion: **BGN, CD44, VCAN** (was five).
- **ALCAM is reported with its direction intact and its evidence stated:** positive point estimates on
  both arrays, significant on GPL6244 (q = 0.000373), not significant on GPL3290 (q = 0.161652, CI
  −0.024 to 1.531), and positive-but-not-significant again in the reference-matched sensitivity
  analysis (Δ +1.233, q = 0.082). It is stated as a threshold statement about evidence, explicitly
  **not** as biological absence or equivalence, and the positive estimate is not suppressed. GPC1 is
  handled the same way and both are retained in Table 5.
- Stored labels are explained as classifications, not proof of no effect: `FLAT_ON_BOTH` is qualified
  in the main text, Table 3, SI Methods S7 and SI Table S7 by the width of the GPL3290 interval; the
  CD276 sequencing ratio of 1.42 is stated as descriptive with the stored `FLAT` label named as a
  banding rule applied to a ratio, not a test; stromal-panel directions carry their p values (0.095,
  0.097) and are not called findings.

## Specific repairs, each applied

| Root's instruction | Where |
|---|---|
| Remove the false no-correction / no-sensitivity / no-other-array-contrast statements | Methods, Limitations, SI Note S5 (correction); Methods, SI Note S3 (sensitivity); Results (the "carry no EMC-tissue array contrast elsewhere" sentence and its predecessor priority claim both withdrawn without replacement) |
| Remove the unsupported transfer-asymmetry conclusion | Abstract Conclusions, Results, Discussion; withdrawal recorded in Appendix A6 |
| Remove the unsupported ALCAM-marker conclusion | Discussion's "demoted but intact marker … in all three cohorts" replaced by the per-platform evidence |
| Correct the CSPG4 claim | Results: absent from the **selectivity scan**, present in the **normal-window artifact** as ENHANCED_BROAD; also SI Note S1 L4 |
| Qualify the stale L4 instrument-limit field precisely, no rerun, no restamp | Methods, Results and SI Note S1 L4 all state that `in_emc_surface_normal_window: false` was written against an 18-antigen version of the prior, that the current prior classifies 46 and lists CSPG4 among those added, and that the field is left unaltered |
| D3: abstract subset count, Table S2 subset caption, DLL3 Methods/Notes reference | Abstract now nine/18; Table S2 caption says "a subset of the artifact, which classifies 46" and the missing named rows were added from the artifact; the DLL3 cross-reference points at **Supplementary Methods S3** (the classification semantics) and Table 3, not at Note S3 (CSPG4) |
| U1: resolve its actual two reasons | Methods and SI Note S1 L5 now state both reasons in full — no fibroblast compartment, and the contradicted identity of ACH-001519 — instead of a backward reference |
| Remove the B7-H3 protein-restriction claim; scope or withdraw modality suitability | The protein-restriction sentence is removed. The "poor address for any modality that acts wherever the antigen is" verdict is scoped as an inference from transcript data with the deciding measurements named as absent |
| Withdraw the blanket reverification claim; state the actual checks | Methods "Use of large language models" and the Declarations now state manuscript-against-artifact and main-against-SI comparison only, and explicitly disclaim an independent pipeline reproduction |
| Keep the 21 verified improvements where their scopes hold | ORCID `0000-0002-1823-1451` in both author blocks with the editorial note superseded; honest ethics/AI narrowing in the deposit box, Declarations and a new SI declarations block; six-subtype substring class definition incl. alveolar rhabdomyosarcoma and the absent DSRCT term; five instrument limits with the L2 counter-reading; DLL3 uniqueness; LRRC15 → ENHANCED_BROAD in Table 1 and Table S2; CSPG4 4.94× (previous "order of magnitude" corrected) and its ENHANCED_BROAD prior; CSPG4 GPL6244/GPL3290 contrasts; the route-panel and MKI67 readings incl. the GPL3290 MKI67 value the SI had recorded as "not reported"; the four added Table S3 panels gene-for-gene in order and "All nine panels"; Table S6's CD248 row re-sorted to rank 2; the 46-antigen Table S2 preamble; the reference preamble naming `remaining-reference-metadata-2026-08-09.json` for entries 4, 5, 6, 13, 16, 17, 18 and eleven from the submission record, with Appendix A4's stale "still carry their identifier alone" paragraph superseded and retained |

### One correction beyond root's list, flagged for the reviewer

The GSE24369 comparator arm was printed as "6 fibrosarcoma". The deposit's own verbatim sample
annotations read **Myxofibrosarcoma**, and `fibrosarcoma` is an internal class label in
`emc-expression-panels.json` that reached the prose; `emc-tissue-read-statistics.json` records the arm
as `myxofibrosarcoma`. Methods and Table 2 now say myxofibrosarcoma, and Methods additionally records
the five solitary fibrous tumour and two pooled normal skeletal-muscle arrays in the deposit that are
outside the primary contrast. This is recorded in Appendix A6. **A reviewer should confirm this is
wanted**, since it was not among the named repairs.

## Checks actually run

`checks/check_bindings.py` — a read-only checker written for this lane. It recomputes the set
definitions, the intersection, the board coverage, the corrected states, the sensitivity rows, the
resolution figures, the panel memberships, the reference records and the cohort composition from the
artifacts, and asserts the manuscript and SI strings that carry them; it also checks the withdrawn
claims are absent from the live body while remaining quotable in the correction register, and that
main and SI agree where both state the same fact.

| capture | exit code | result |
|---|---|---|
| `checks/run-1.out` | 1 | 85 pass, 5 fail — 3 line-wrap mismatches in the checker's literals, 2 checker bugs (searched the whole file instead of the live body, so the register's verbatim quotations tripped them) |
| `checks/run-2.out` | 1 | crashed: relative paths, run from the wrong working directory |
| `checks/run-3.out` | 1 | 116 pass, 4 fail — all four were checker defects (body-vs-whole-file, a wording mismatch, a regex that caught Supplementary Notes as Methods, and a naive banned-phrase test that matched the paper's own scope disclaimer) |
| `checks/run-4.out` | 1 | 119 pass, 2 fail — the banned-phrase test still matching the scope disclaimer |
| `checks/run-5-PASS.out` | **0** | 122 pass, 0 fail |
| `checks/run-6-PASS.out` | **0** | 122 pass, 0 fail, after two prose-transition fixes |

Every failed capture is preserved unmodified alongside the successful ones; none was overwritten.
No test was skipped, and no guard was weakened — the four fixes after run-3 changed the checker's
addressing and literals, not the strictness of any assertion about the manuscript.

**Not run, deliberately:** `scripts/preflight.sh` and the repository test suite (broad tests are
fenced, and the parent integrates), `submission_metrics.py` beyond the two measurement runs above, and
any producer, figure build or network call.

## Current limitations of this frozen package

1. **⚠ Length. The main body grew from 5,213 to 7,621 words** (measured between the Abstract heading
   and the Display items heading, comments stripped). `submission_metrics.py` reports the manuscript at
   7,202 main words and 347 abstract words against believed BJC limits of 5,000 and 200. **The paper was
   already over both limits at HEAD; this revision made it substantially more so.** This is a format
   problem an editor returns, not a scientific one, and it was not fixed here because compressing 2,400
   words of newly corrected statistical prose is a second editing pass with its own error risk. The
   obvious lever, if the reviewer wants it, is to move the per-platform state narrative in "Surrogate
   priorities in EMC tumour tissue", the ALCAM evidence paragraph and the three sensitivity-analysis
   descriptions wholly into SI Methods S7 and leave one sentence plus a pointer in each place.
2. **Artifact contents were verified; artifact validity was not.** Every number here was read against
   the committed artifact named for it. No step from the public deposits to those artifacts was
   independently reproduced, and both the manuscript and this record say so.
3. **The stale L4 field is qualified in prose, not repaired in the artifact.** A future producer run
   would close it; none was authorised or performed.
4. **Figure 1 is unchanged and was not rebuilt.** Its caption now scopes what it plots, and states that
   DLL3, the one member of the selective-and-restricted intersection over the full set, is not drawn.
5. **Five selective antigens remain unmeasured in tissue** and six carry no normal-tissue record. The
   paper discloses this; closing it would need those genes placed on the board, which is a producer run.
6. **The simulated sibling review-response is not reconciled and was not edited.**
   `emc-surface-target-landscape-review-response-2026-08-10.md` is committed in the same directory,
   describes these corrections as already applied, and reports the selective set as 18 without the
   classic-subset distinction. It is historical commentary on purported changes, not an empirical
   source; Appendix A6 says so and says the artifacts govern. **It is outside this lane's ownership**
   (main and SI only) and remains an inconsistency in the directory for whoever owns it.
7. **Word-level style has not been re-linted.** `lint_readability.py` was not run.

## Reopening condition

None of the corrected central questions turned out to be unsupported: the corrected statistics exist,
are committed, and change the paper's counts without emptying it. The scientific claim that survives is
weaker and better bounded than the one it replaces, which is the correct outcome rather than a blocker.
The one condition that would reopen the science is a producer run that places ALK, ENPP1, FGFR4,
SLC34A2 and STEAP1 on the cross-platform board and queries them against the normal-tissue prior; until
then the full-set claim rests on 13 of 18 measured members and says so.
