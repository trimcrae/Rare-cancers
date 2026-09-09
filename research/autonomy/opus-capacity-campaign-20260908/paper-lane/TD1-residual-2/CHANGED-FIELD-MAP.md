---
id: DOC-TD1-RESIDUAL-2-CHANGED-FIELD-MAP
title: "TD1 residual batch 2 — exact changed-field map, R1–R4"
level: L4
kind: repair-record
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# TD1 residual batch 2 — exact changed-field map

**One coherent R1–R4 correction batch**, authored against the accepted focused verification
(`FOCUSED-SCIENTIFIC-VERIFICATION-TD1.md`, 36,301 B, SHA256
`3ba9f1a6f19c6ac1e8637650e5e4d44241c761e07ea3349c3c455b7038bb53bf`) and the root adjudication memo
(8,487 B, SHA256 `abc02ace458e48b99611f2fc613e96d5bbfad77801927f93118bff21f358635f`), both read in full
together with the execution-scope record, the reviewed-input manifest, the retained inputs and the
retained original execution receipts.

⛔ **Nothing here is a new scientific result.** No classifier was run, no producer, no statistic, no
figure, no baseline, no source acquisition and no second review. Every change is interpretation text
or a matching source-code literal. The disposition is unchanged: seven findings closed at
retained-summary scope, F8–F11 partial and now addressed; the narrow descriptive synthesis is viable;
⛔ **the stronger opposite-disagreement / EMC-selectivity claim stays PARKED.**

## Ownership split

| | files | state |
|---|---|---|
| **owner-owned, EDITED IN PLACE** | `research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md` | **14 edits applied** |
| **PARENT-OWNED, UNAPPLIED** | C, G, GP, MC, PUB (5 files) | 28 edits, supplied as unified diffs in `patches/`; **not applied**, no shared file modified |

⛔ No `git add`, no commit, no push, no preflight, no subagent. The only tracked file this lane
modified is the manuscript above.

## Final identities

| object | bytes | SHA256 | Git blob |
|---|---|---|---|
| main **before** (= reviewed pin, unchanged since f610) | 41,911 | `12c082b3d4dc8dabedb4e7f7716435f175da88ea6e684c66f7d40de29942e8aa` | `60fa27c312faefb106f627aaa085c86b8d37b645` |
| main **after** (live) | 48,268 | `9523555483f00cfee00b6cd4cf64f5615f57c011f1640297bf952399e742b3ba` | `0c6c57f63b89f41e8ef7722d87035fbfa440cb50` |

Unapplied parent-owned results (patched pristine copies, produced outside the repository):

| file | before bytes / SHA256 | after bytes / SHA256 | edits |
|---|---|---|---|
| `research/literature/fet-fusion-chaperone-clientship-2026-08-27.json` | 32,858 / `7ba3ed7a…` | 39,198 / `ae44e6e0…` | 19 |
| `research/modalities/census-route-expression-grading.json` | 94,931 / `2dbd21cc…` | 95,906 / `cbb9c9ac…` | 3 |
| `research/modalities/census_route_expression_grading.py` | 54,778 / `42ffb5a9…` | 56,050 / `43447cd4…` | 3 |
| `research/manuscripts/modality-census/cancer-modality-census.md` | 41,391 / `ea130364…` | 42,114 / `d8fd8587…` | 2 |
| `systems/graph/publications.json` | 70,224 / `800e844f…` | 71,000 / `7f923cc0…` | 1 |

Full-length hashes: `checks/BEFORE-HASHES.sha256`, `checks/PATCHED-COPY-HASHES.sha256`,
`checks/PATCH-HASHES.sha256`, and per-edit old/new byte lengths and SHA256 in
`patches/EDIT-LEDGER.json` and `checks/01-apply-main-edits.stdout.json`.

## A · Main manuscript — 14 applied edits

| id | group | field / location | what changed |
|---|---|---|---|
| M1 | R4 | front-matter `scope:` | “release containing no EMC line” → “release **in which no EMC-labelled model contributes CRISPR gene-effect data**” |
| M2 | R4 | top disclaimer block | same substitution in the disclaimer |
| M3 | R4 | §7 Limits bullet | rewritten: no EMC-labelled model contributes gene-effect data; **one EMC-labelled model (ACH-001519) IS in the release's model metadata** with no values; stated as a data-availability fact, explicitly **not** a determination of that line's disease or fusion identity |
| M4 | R1 | §4 search-limits bullet, Q13 | the PMID 25036637 “full text names no FET protein” clause is **withdrawn as a current assertion**; the 2026-08-27 reading is preserved as dated provenance; supplement membership remains **unknown**, and the available material establishes FET membership in **neither** direction |
| M5 | R1 | §4 retained-extract paragraph | heading and framing changed to “**what the retained curated extracts report**”; only PMID 25985210's PMC full text was read on the retrieval date; the full-article negative — “none of those reports includes a cycloheximide chase, a proteasome-block rescue or a parallel mRNA measurement” — is **withdrawn** and replaced by “the retained extracts **do not establish whether** those studies included them, and this paper does not assert that they did not”; the mechanism of depletion is stated as unresolved here |
| M6 | R1 | §5 outcome table, chaperone row | “clientship is untested” → “clientship is **not established by this evidence**” |
| M7 | R3 | §6 U4 | “would revise this exploratory estimate” → “would update confidence in **generalization** and could reveal **between-series heterogeneity**”; adds that it would **not** revise the fixed estimates for the two historical cohorts and that a pooled/population estimate would be a separately defined analysis, none reported here. The existing proteostatic-load warning is kept verbatim |
| M8 | R3 | §6 U5 | the two temporal cases are now separated: a binding assay **published after 2026-08-27** updates the **present evidence inventory** and does not change the historical fact; an **earlier** qualifying item shown to be inside the searched set instead **exposes an extraction or classification error**. The warning that any-FET evidence does not establish EWSR1/TAF15::NR4A3 clientship in EMC is kept verbatim |
| M9 | R4 | §1.1 Scoring (new paragraph) | states **multiple-probe averaging per gene before within-array standardization**, and the implementation's **four-decimal rounding boundary** on background mean/SD, gene averages and stored z-scores; states that every exact-reproduction claim in §8 is bounded by it |
| M10 | R4 | §8 Methods (new paragraph) | **fixed identities**: a table of Git blob SHA-1s for the ten named artifacts/producers, verifiable with `git cat-file -p`; distinguishes numerical inputs from **annotation-only** corrections (which change a blob id and no number); ⛔ no hash claimed for the raw GEO matrices or DepMap CSVs; ⛔ no accessible public archive asserted; ⛔ no producer re-run |
| M11 | R4 | §8 reproduction claim | one sentence replaced by **three explicit levels**: (1) readable back exactly; (2) **classifier REPLAY** is possible against the retained annotations (`sample_annotations_verbatim[].annotation`, `emc_atr_vulnerability._classify_sample`) and conditional *p*/intervals recomputable **from rounded inputs**; (3) **not reproducible** — replay does **not** verify the strings against the deposit, which needs the absent original matrix; all-probe reference distributions, probe mapping and per-line Chronos cannot be reconstructed |
| M12 | R4 | §8 fixed-identity caveat | names the two artifacts (G, C) carrying a **prepared but unintegrated** annotation-only correction, so their blob ids will change while no number does |
| M13 | R4 | §1.1 Scoring | grammar repair inside the M9 sentence; no claim changed |
| M14 | R1 | §4 | line reflow after the M5 correction; no claim changed |

Preserved verbatim and re-checked: the fourteen Δ/*t*/df/coverage rows and their nominal
*p*-values/intervals; the five dependency rows; the SMARCB1 and BRD9 control rows; the MYC and
context deltas; the seven memberships; the cohort counts; the 24Q4 release, threshold and lineage
rule; the fifteen dated query strings and hit counts; the honest no-new-patient-study and
non-exhaustive-treatment-exposure qualifications. See check D/E below.

## B · Parent-owned, UNAPPLIED — `research/literature/fet-fusion-chaperone-clientship-2026-08-27.json` (19 edits, R1)

Every change is an **interpretation string**. ⛔ No query string, hit count, PMID, PMCID, DOI, title,
`assay`, `verbatim` quotation or retrieval date is altered — 110 such literals were checked and all
110 survive byte-identically, and the fifteen hit counts are identical leaf-for-leaf.

| id | exact locator | correction |
|---|---|---|
| C1 | `…queries[Q1].outcome` | “no binding assay in any of them” → not identified **among the items inspected from this query**, with the standing bound |
| C2 | `…queries[Q2].outcome` | “**NO FUS-DDIT3 clientship record exists**” → none identified among the items inspected from this query |
| C3 | `…queries[Q9].outcome` | “**the whole HSP90-inhibitor literature in Ewing sarcoma is four papers**” **withdrawn** → “this query returned four hits”; the string and the count 4 unchanged |
| C4 | `what_this_changes.the_grade_should_not_move` | “**nothing exists for NR4A3 fusions at all**” and the positive/negative **cancellation** rationale **withdrawn**: a non-retrieval is not a measured biological negative and cannot cancel a positive. ◐ PARTLY SUPPORTED retained, resting on its own stated evidence and uncertainty |
| C5 | `what_this_changes.falsifier_F5_of_the_dependency_manuscript` | **RETIRED**. “F5 SURVIVES: no such co-immunoprecipitation exists” carries **no current authority**; the authoritative replacement is named — U5 of the manuscript |
| C6 | `evidence[PMID=28383167].what_it_establishes` | “**the only** chaperone-family record that exists in the EMC literature at all” → “the one chaperone-family record **retrieved for EMC by this dated search**” |
| C7 | `evidence[PMID=31171724].what_it_establishes` | “**the closest thing in the literature**” → “a relevant example **found by this search**”; no comprehensive ranking was performed |
| C8 | `what_this_changes.the_rationale_needs_one_correction` | “**the only** fusion oncoprotein whose chaperone clientship HAS been solved structurally” → the **non-FET comparator identified by this search** (AML1-ETO); no exhaustive uniqueness. The hypothesis-not-finding label is retained |
| C9 | `evidence[PMID=25036637].category` | “read in full” recast as the **dated 2026-08-27 declaration**, retained as provenance, explicitly **not** used as verified full-text content |
| C10 | `evidence[PMID=25036637].what_it_does_NOT_establish` | “the paper's body names no FET protein” retained **only** as the dated declaration, **not asserted** as verified full-text absence |
| C11 | `open_questions_stated_as_unknown[0]` | same treatment; **supplement membership remains UNKNOWN**; the IM-22301 pointer kept |
| C12 | `open_questions_stated_as_unknown[3]` | the assay-absence claim about all three papers **withdrawn**; whether those assays were performed is **UNVERIFIED from the originals available here**; the retained evidence still does not establish a post-translational mechanism |
| C13–C17 | `…queries[Q1, Q4, Q5, Q12, Q14].outcome` | inherit the same bounded inspected-record scope; Q14 additionally states its 43 hits were not all individually screened |
| C18 | `retrieval.full_text_read[0]` | marked **HISTORICAL PROVENANCE, not current authority**; does not by itself verify content and does not reinstate any withdrawn interpretation |
| C19 | `_supersedes.what_changed` | marked **HISTORICAL PROVENANCE, not current authority**; where it and the dated corrections disagree, the dated corrections govern; the authoritative bounded statement is named |

⚠ Q15's existing correction (25 unscreened hits, earlier claim withdrawn), Q3's existing correction
and the corrected `verdict` block were already applied and are **not** touched.

## C · Parent-owned, UNAPPLIED — G / GP / MC / PUB (9 edits, R2)

| id | file | exact field | correction |
|---|---|---|---|
| G1 / GP1 | `census-route-expression-grading.json` / `.py` | `routes.RT-TXN-CDK.route_action` | “broad **non-selective** dependency in non-EMC cancer lines” → “broad **binary** dependency in the screened non-EMC cancer lines, with **selectivity UNRESOLVED**”; “non-selective” explicitly withdrawn because a cancer-versus-cancer screen measured no normal-tissue comparison and no graded response |
| G2 / GP2 | same | `routes.RT-CHAPERONE.observed` | the **GPL3290 biological-corroboration hold PROPAGATES here**: GPL3290 withheld under the reference-design hold (10 EMC `CRH-mRNA`, 3 DFSP `CRH`, 3 GIST `UHR`); biological expression support rests on **GPL6244 alone**; all displayed numbers, requested/readable gene counts and cohort memberships retained unchanged |
| G3 / GP3 | same | `routes.RT-CHAPERONE.verdict` | verdict stated as resting on GPL6244 alone, GPL3290 retained and displayed but withheld from corroboration |
| MC1 | `cancer-modality-census.md` | §3.1 | “which is the definition of pan-essential” → “broad **binary** dependency across the **screened non-EMC** cancer lines” |
| MC2 | `cancer-modality-census.md` | §3.1 | **two readings withdrawn**: (a) that the elevation “buys no window against normal tissue, because every sarcoma line needs these genes regardless of fusion status” — the 91-line binary cancer-versus-cancer summary supplies no normal-tissue observation, no graded drug-response analysis and no fusion-status-stratified result, so it shows **neither** absence of a therapeutic window **nor** fusion independence; (b) that the cytotoxicity concern “turned out to be exactly the mechanism that closed it” — **no mechanism was measured**; class toxicity remains a prior concern, not a finding of this screen. The **de-prioritisation with a stated basis** is retained, with the EMC dependency stated as **unmeasured and therefore unknown, not absent** |
| PUB1 | `systems/graph/publications.json` | `PUB-TXN-DEPENDENCY.outcome_potential_why` | “**resolvable only by a perturbation observation in a fusion-positive EMC model**” **withdrawn**; replaced by the narrower missing-evidence statement — EMC-specific perturbation evidence is **absent** — with five **separate** questions such an observation alone would not settle: chaperone **clientship** (binding), **mechanism** of depletion, tumour-versus-**normal-tissue selectivity**, **reference comparability** of GPL3290, and the **scope** of the dated search |

⛔ `PUB-TXN-DEPENDENCY.what_it_would_claim` is already corrected and is **not** touched. ⛔ The six
earlier applied patches are **not** repeated. ⛔ No census-wide or graph-wide sweep was made; only
the named paragraph and the named route fields.
⚠ `systems/views/L3-publications.md` and `L2-rt-chaperone.md` are **generated** from the graph and
will need the parent's normal regeneration after PUB1 and G1–G3 are integrated. This lane did not
touch generated views.

## D · Checks actually run — commands, streams and measured exits

All streams are retained in `checks/` as `*.stdout.*`, `*.stderr.txt`, `*.exit.txt`.

| # | command | exit | result |
|---|---|---|---|
| 01 | `python3 …/checks/apply_main_edits.py <BEFORE> <live main>` | **0** | 14 edits, each anchor matched **exactly once**; 41,911 → 48,268 B |
| 02 | `python3 …/checks/apply_main_edits.py <BEFORE> <scratch>` then `cmp` | **0** | replay from the frozen `12c082b3…` input reproduces the live file **byte-identically** |
| 03 | `python3 …/checks/build_shared_patches.py <scratch> patches/` | **0** | 28 edits across 5 files, every anchor unique; **no repository file modified** |
| 04 | `python3 …/checks/verify_static.py before/ <scratch>` | **0** | **PASSED**, five checks (below) |
| 05 | `git apply --check -p1 patches/*.patch` ×5 | **0** ×5 | all five patches apply cleanly to the current tree |
| 06 | `python3 -m py_compile <patched GP>` | **0** | patched generator parses |
| 07 | `json.load` on the three patched JSON files | **0** | all valid JSON |
| 08 | `lint_claims` / `lint_changed_prose` / `lint_readability` on the edited main | **0 / 0 / 0** | clean |
| 08 | `lint_asymmetry` / `lint_submission_residue` on the edited main | **2 / 2** | ⛔ **actual command failures, not passes** — neither tool accepts a file argument (`unrecognized arguments`). The same wrong-CLI failure class the previous lane recorded. Not re-run under another invocation, not relabelled |
| 08 / 09 | `lint_style` on the edited main / on the frozen BEFORE | **1 / 1** | ⛔ **failing before and after.** BEFORE: 99 errors, bold 20.6/1000. AFTER: 121 errors, bold 20.7/1000. The increase is entirely in the two pre-existing categories — `bold-midsentence` 53→63 and `glyph` 43→55 — because the corrections use the same ⚠/⛔ convention as the surrounding text. ⛔ **No guard, threshold or matcher was changed**, and this is not claimed as a pass |

### What check 04 actually establishes

- **A · JSON leaf structure.** C **230→230** leaves, G **1181→1181**, PUB **416→416**; **0 leaves
  added, 0 removed, 0 NON-STRING leaves changed**; changed **string** leaves are exactly the declared
  set — C 19, G 3, PUB 1. PUB is keyed by entry `id`, not position.
- **B · Literal preservation in C.** 110 literals checked — every query string, every hit count,
  every PMID/PMCID/DOI/`pubmed_url`, every `title`, `assay` and `verbatim` source quotation, the
  retrieval date and the `full_text_refused` records — **0 missing**. The fifteen hit counts are
  identical leaf-for-leaf.
- **C · G ↔ GP generator agreement.** The patched generator is parsed with `ast` (**never executed**);
  each of the three changed G strings occurs **exactly once** as a string constant in it.
- **D · Main-manuscript quantities.** Every numeric token in the frozen BEFORE main is still present
  in the edited main with **at least** the same multiplicity — **0 lost or reduced** (201→208 distinct,
  432→460 total; the additions are the ten blob SHA-1s, `ACH-001519`, the four-decimal rounding
  statement and the three level numbers).
- **E · Main literal preservation.** 24Q4, Chronos, 91, 176, 97.8, GPL6244, GPL3290, the MYC/context
  deltas, Bonferroni, SMARCB1, BRD9 and the seven cited PMIDs all survive. ⚠ **Honest limit:** five
  probe strings (`1.8630`, `0.077`, `0.839`, `−0.130`, `0.200`) are reported as **not present in the
  BEFORE file either**, so check E says nothing about them; they were not treated as passes.

⛔ **This is annotation integrity, not biological validation.** Nothing above re-establishes any
scientific quantity; it establishes only that the quantities, cohorts, quotations and matching
generated-annotation literals did not change.

## E · What was deliberately NOT done

⛔ No classifier run, no scientific producer, no statistic, no source hunt or retry, no held-source
acquisition, no figure, no baseline, no second focused review, no whole-census or whole-graph sweep.
⛔ No repetition of the six already-applied patches. ⛔ No git add/commit/push, no preflight, no
subagent. ⛔ No original failed or limited attempt was deleted, rewritten or relabelled — the earlier
lane's source-binding, patch-builder, invariance, CLI and lint failures stand as recorded.
⚠ The fifteen reference identifiers remain **NOT SWEPT** against the retraction sweep: that is
**UNKNOWN, not clean**, and unchanged by this batch.
