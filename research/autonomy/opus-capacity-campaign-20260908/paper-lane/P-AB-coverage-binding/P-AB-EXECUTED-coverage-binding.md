---
id: DOC-OPUS-CAMPAIGN-P-AB-COVERAGE-BINDING
title: "P-AB executed — the endpoint ghost witness closed, and the three quantities bound"
level: L4
kind: record
status: live
purpose: >
  Record the executed P-AB batch: the endpoint 282 / 100 / three-study binding, the removal of
  comments and docstrings as a source of census document applicability and of harvested coverage,
  the measured before/after for the affected scope, and the other-scope deltas including two
  measured losses that are reported rather than engineered away.
scope: >
  L4. Two files changed (`claim_coverage.py`, `tests/test_endpoint_manuscript_figures.py`) and one
  added (`tests/test_the_census_credits_only_executable_references.py`). No manuscript edited, no
  floor moved, no census regenerated, nothing committed.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# P-AB — executed

Base commit `aca13df91c0f33343460fb53a365b47caf2d035a`. Every capture named below is retained under
`evidence/` in this directory, one file per attempt, failed attempts included and not overwritten.

## 1 · What was wrong, reproduced

`claim_coverage._test_patterns` decided which document a guard reads by searching that guard's
**whole source** — comments and docstrings included — for the document's basename, then harvested
its regex candidates from **every** string constant, docstrings included. Both halves infer
executable behaviour from text Python never evaluates.

`tests/test_aso_abstract_is_bounded.py` names `endpoint/response-endpoint-indolent-tumours.md`
exactly once, at **line 6, inside its module docstring**, narrating the historical mistake of having
borrowed that paper's abstract limit. It opens the two ASO manuscripts and nothing else.

Measured before the change (`evidence/BEFORE-endpoint-census.json`,
`evidence/BEFORE-ghost-witness-patterns.json`, `evidence/BEFORE-sole-witness-breakdown.json`):
that one docstring line was the **sole** census witness for **three** endpoint sentences, through
two ASO-domain patterns —

* `by construction|by necessity of the (?:design|budget)|guaranteed by[^.]{0,60}budget`
* `(?:no|none|not)\b[^.;]{0,90}(?:patient|breakpoint)[^.;]{0,90}(?:report|carr|observ)`

— neither of which asserts anything about this manuscript, and both of which are wildcard exactly
where the identified sentence's quantities are.

**The false witness, run rather than argued.** At `aca13df9`, all five test modules whose source
names this manuscript were run against six perturbations of the identified sentence's quantities.
`evidence/PERT-HEAD-00-baseline.txt` is the clean baseline (131 passed, exit 0);
`evidence/PERT-HEAD-01..06.txt` are the six perturbations — **every one exit 0, 131 passed**:

| # | perturbation | HEAD exit |
|---|---|---|
| 1 | `whether its 282 patients overlap` → 287 | 0 |
| 2 | `France followed 282 patients` → 287 | 0 |
| 3 | `overlap the 100 below` → 107 | 0 |
| 4 | `placed 100 patients on active surveillance` → 107 | 0 |
| 5 | `pooled analysis draws on three prospective` → four | 0 |
| 6 | `A pooled analysis of three prospective observational` → four | 0 |

A sentence the census called covered, whose every stated quantity could move with nothing going red.

**The committed harness agrees, at the base commit** (`evidence/BEFORE-ablation-identified-sentences-AT-HEAD.json`).
`claim_ablation.ablate` on the identified sentence returns `status: applied`, **`red: []`**, baseline
clean (`already_red: 0`), reason:

> `no guard reading this file noticed any of: 282->287, 100->107, Two->Six, three->seven, one->two`

⭐ That is the CI blind row reproduced end to end, on the sentence the census credited to a
docstring.

⚠ **AND A DISTINCTION THAT MUST NOT BE BLURRED.** The other two §6.1 sentences — the ones stating
the 100-patient trial and the 282-patient pooled analysis in the body — were **already red at the
base commit** under the same harness. They carry many other digits (53.4, 43.5, 63.1, 58, 26, 67,
66, 33, 34) and `ablate` stops at the first perturbation that trips a guard, so their redness says
nothing about whether 282, 100 or "three" was bound. The six targeted runs in the table above are
the sharper instrument, and they show those specific quantities unbound at **every** site: perturb
only them and all five guards stay green. The census, separately, credited neither sentence at all
(`read_by: []`).

## 2 · What was implemented

**(a) The binding.** `tests/test_endpoint_manuscript_figures.py` — which does open this manuscript —
gains `test_the_outside_corpus_desmoid_counts_are_the_fetched_abstracts_own`, three
parametrisations. Each quantity is **read back out of the retained fetch record**
`research/manuscripts/endpoint/natural-history-inputs.json` rather than retyped as a constant:
Colombo 2025 (**PMID 39620931**) `Patients (n = 282)` and `Three prospective observational studies`,
Bonvalot 2023 (**PMID 37777684**) `100 patients were enrolled`. Every site in §6.1 that states each
value is listed, so a binding cannot hold at one of two mentions.

⛔ It asserts nothing about disjointness. The manuscript's position — the overlap "is stated in
neither report and is unknown here" — is unchanged and is restated in the guard's docstring as a
limit on what the guard may be read to claim. **No manuscript was edited.**

**(b) The scope and harvest fix.** `claim_coverage._executable_source` blanks comment and docstring
characters (blanks, not deletes: same length, same line structure, so no filename is spliced out of
existence), and `_test_patterns` now applies the substring scope test to that executable text and
skips docstring constants when harvesting.

**(c) A regression test for the mechanism**, `tests/test_the_census_credits_only_executable_references.py`.
Its fixtures are **synthetic**: a document name that exists nowhere in the repository, in a throwaway
`tests/` directory. ⛔ No censused manuscript's basename appears in executable code in it — a test
that pinned this behaviour by naming a real manuscript would become a witness for that manuscript in
the census it checks. Verified: adding the module moves no document's coverage
(`evidence/AFTER4-...json` vs `evidence/AFTER3-...json`).

## 3 · Before / after — the affected scope

Live census, no `--write`. `evidence/BEFORE-all-documents-census.json` →
`evidence/AFTER3-all-documents-census.json`.

`endpoint/response-endpoint-indolent-tumours.md` — **covered 9 → 10, with a number 5 → 8**
(280 sentences, 110 numbered).

* **−3** the ghost rows sole-witnessed by `test_aso_abstract_is_bounded.py`, now uncredited;
* **+4** genuine rows credited to `test_endpoint_manuscript_figures.py`.

Six perturbation runs against the changed tree, clone-only, manuscript never touched in place
(`evidence/PERT00-baseline-clone-green.txt`, exit 0; `evidence/PERT-01-1..06-6.txt`, **all exit 1**),
each failing the correct parametrisation:

| # | perturbation | after exit | failing case |
|---|---|---|---|
| 1 | 282 → 287 (`whether its …`) | 1 | `[39620931-patients]` |
| 2 | 282 → 287 (`… France followed …`) | 1 | `[39620931-patients]` |
| 3 | 100 → 107 (`overlap the … below`) | 1 | `[37777684-patients]` |
| 4 | 100 → 107 (`placed … patients`) | 1 | `[37777684-patients]` |
| 5 | three → four (`draws on …`) | 1 | `[39620931-studies]` |
| 6 | three → four (`A pooled analysis of …`) | 1 | `[39620931-studies]` |

The committed harness agrees: `claim_ablation.ablate` on all three sentences returns
`status: applied`, red, with a clean baseline (`already_red: 0`) —
`evidence/AFTER-ablation-identified-sentences.json`. ⚠ For the identified sentence that is a
**change of verdict**, blind → red; for the other two it is a verdict that was already red for other
digits, and the targeted table above is what shows 282, 100 and "three" newly bound at each site.

⚠ `RUN01-new-guard-first-run.txt` is retained: the first version of the locators failed on the
manuscript's hard line wrapping. The locators are now whitespace-tolerant; `\s+` sits between words,
never over a quantity.

## 4 · Other-scope delta, including two losses reported rather than repaired

Three other documents moved, all through the same channel and none through a floor:

| document | covered | numbered | witness lost | verdict |
|---|---|---|---|---|
| `dependency/emc-atr-vulnerability-assessment.md` | 2 → 0 | 2 → 0 | `test_the_readability_splitter_breaks_where_a_sentence_does.py` | ⭐ **true removal** — that module tests the splitter on synthetic strings and opens no manuscript; the name is at line 21, in a docstring |
| `fusion-output/nr4a3-fusion-transcriptional-output.md` | 7 → 0 | 7 → 0 | `test_build_submission_pdf.py` | ⚠ **false negative** — it names the file only in a comment (line 430) but genuinely opens it through `build_submission_pdf.PAPERS`. ⭐ Note the committed `claim-coverage.json` records this document at **0 covered**, so the new reading agrees with the committed deposit and the live 7 did not |
| `fusion-partner/emc-fusion-partner-stratification.md` | 95 → 87 | 92 → 85 | splitter (1 sentence, true removal) + `test_fusion_partner_prose_asserts_the_relations_its_artifact_computes.py` (7 sentences) | ⚠ **7 are a false negative** — that module resolves the document at runtime through `PROSE_DOCUMENTS`, and its own docstring says naming it in prose was the only way this census could see it |

⛔ **The obvious widening was tried and rejected on measurement, not on taste.** Following each
module's imports and applying the same prose rule to them recovers both false negatives exactly —
and, on the same run (`evidence/AFTER2-all-documents-census.json`), credits
`test_the_paper_states_what_its_own_claims_depend_on.py` to the endpoint and fusion-partner
manuscripts (it imports `claim_coverage`, whose `COVERAGE_FLOOR` names them in code) and
`test_no_page_is_nearly_empty.py` to `emc-atr-collaborator-package.md` (it imports the PDF registry
and opens no manuscript), moving four documents +3 each. That trades a ghost through a docstring for
a ghost through a shared registry, and `COVERAGE_FLOOR`'s own note depends on `claim_coverage` NOT
being scanned. It was reverted.

⭐ **The honest repair for the two losses is in those guards, not here**: each names its document in
executable code, beside the lookup it already performs, and the credit becomes visible for the reason
it is true. Both files belong to other owners and **neither was touched**. ⛔ Planting a filename in
a guard that does not open the document would restore the count and re-create the defect.

⚠ `surface-targets/emc-surface-target-landscape.md` moved 310 → 375 → 399 sentences across this
session's runs. That is a **concurrent writer**, not this change; its covered count is 0 throughout.

## 5 · The floor, and the gate's colour

⛔ **No floor was moved.** All four hold, before and after
(`evidence/AFTER3-all-documents-census.json`):

| document | floor | before | after |
|---|---|---|---|
| `aso/fusion-junction-aso-journal-article.md` | 66 / 44 | 106 / 67 | 106 / 67 |
| `aso/fusion-junction-aso-journal-tables.md` | 4 / 1 | 4 / 2 | 4 / 2 |
| `endpoint/response-endpoint-indolent-tumours.md` | 7 / 4 | 9 / 5 | **10 / 8** |
| `fusion-partner/emc-fusion-partner-stratification.md` | 1 / 1 | 95 / 92 | 87 / 85 |

⚠ **THE GATE IS RED, AND IT WAS ALREADY RED AT THE BASE COMMIT.**
`test_the_paper_states_what_its_own_claims_depend_on.py::test_claim_coverage_has_not_regressed`
fails on its **staleness** half, not its floor half, in both trees:

* at `aca13df9`, unmodified — `evidence/RUN03-BEFORE-gate-at-HEAD.txt`, **exit 1**, 1 failed /
  28 passed, the committed `claim-coverage.json` disagreeing with the live census across many
  documents that have simply been edited since it was written;
* on this tree — `evidence/RUN04-AFTER-gate-worktree.txt`, **exit 1**, 1 failed / 28 passed.

No `… is below its floor` line appears in either. ⛔ The census was **not** regenerated: the
generated shared publication waits for the parent. Whoever regenerates it takes on both the
pre-existing staleness and this change's deltas in one artifact.

### 5.1 The sentences that lost a witness — the honest uncovered report

⚠ **The decline is the finding, not a problem to be papered over.** Every sentence that lost its
census credit is listed by name in `evidence/AFTER-sentences-that-lost-their-witness.json`, against
the HEAD reading in `evidence/BEFORE-covered-sentences-AT-HEAD.json`. Nineteen in total, none of
them below a floor:

| document | now uncovered | which |
|---|---|---|
| `endpoint/response-endpoint-indolent-tumours.md` | **2** | "The narrower claim stands: at these arm sizes a zero is frequently uninterpretable…" and "The missing classification is not imputed here, not identified with any patient…" — both were sole-witnessed by the docstring. The third ghost row is the identified sentence, now genuinely covered. |
| `dependency/emc-atr-vulnerability-assessment.md` | **2** | both sole-witnessed by the splitter test; the document returns to 0 covered, which is its true reading |
| `fusion-output/nr4a3-fusion-transcriptional-output.md` | **7** | the false negative above; ⭐ the committed census already records this document at 0 |
| `fusion-partner/emc-fusion-partner-stratification.md` | **8** | 1 splitter (true), 7 runtime-resolved (false negative) |

⛔ Not one of these was recovered by adding a literal. The endpoint gain is four sentences credited
to a guard that opens the file and reddens on their numbers; everything else is a subtraction.

## 6 · Focused checks and their real exit codes

| capture | what | exit |
|---|---|---|
| `RUN01-new-guard-first-run.txt` | first locator draft, wrapped-line failure, retained | 1 |
| `RUN02-new-guard-green.txt` | endpoint guard module after the locator fix | 0 |
| `RUN03-BEFORE-gate-at-HEAD.txt` | ratchet + census reader at `aca13df9` | 1 |
| `RUN04-AFTER-gate-worktree.txt` | ratchet + census reader on this tree | 1 |
| `RUN05..RUN08` | census-mechanism test, v1 and v2, this tree and HEAD, retained | 0 / 1 / 1 / 1 |
| `RUN09-census-mechanism-tests-v3.txt` | final census-mechanism test, this tree | 0 |
| `RUN10-census-mechanism-tests-v3-AT-HEAD.txt` | same test at `aca13df9`: 5 of 6 fail | 1 |
| `PERT-HEAD-00..06` | the false witness, six perturbations, HEAD | 0 (all) |
| `PERT00`, `PERT-01-1..06-6` | the same six against this tree | 0, then 1 (all) |

| `RUN13-focused-affected-modules.txt` | ten affected modules; aborted in `pytest_sessionfinish` by `tracked_tree_guard` because **another live owner (TD1) wrote the dependency manuscript mid-run**. Its one `F` is the same pre-existing staleness failure. ⛔ No summary line was printed, so **no exit code is claimed** | none |
| `RUN14-census-locator-and-endpoint-guard.txt` | census-mechanism test + the censused-sentence locator + the endpoint guard | **0** (67 passed) |

`RUN10` is the discrimination check: five of the six new cases fail at the base commit and pass
here; the sixth (`code_reference`) passes in both, which is correct — an executable reference must
keep its credit. `RUN14` is the one that matters after the coverage change: the locator gate
(`test_every_censused_sentence_can_be_found_in_its_own_file.py`) still finds every censused sentence
in its own file.

⛔ **RUN11 AND RUN12 ARE NOT CHECKS AND ARE NOT CITED AS ANY.** They were a broad manuscript suite
this lane's contract forbids, launched by this owner and stopped. Both partial captures are
retained; both are **INTERRUPTED — NOT PASSED, with no exit code**. See the parent's
`evidence/RUN11-RUN12-TERMINATION-RECORD.md` and this owner's
`evidence/RUN11-RUN12-OWNER-CORRECTION.md`, which records that the two exit codes I first appended
to those files were my own inference, not the runs', and that the annotations have been removed and
the original names restored.

## 7 · Limits of the static method, retained

The census remains a **static screen over harvested string literals**, and this change does not make
it a measurement:

* a guard that **computes** exposes no literal and stays invisible to it;
* a credited pattern may bind a sentence's **words** while asserting nothing about its digits — the
  exact defect repaired here, still reachable elsewhere;
* `covered` is an **upper bound**, and `uncovered` is the finding;
* applicability is still decided by a **filename appearing in source**. It is now source the
  interpreter evaluates, which is strictly better and still not proof that the guard opens the file.
  ⛔ A filename in an arbitrary executable string is not evidence that a test reads a document.
* **A sibling channel is left open and is named rather than fixed.** `claim_ablation.guards_reading`
  selects the guards to **run** by the same raw-source substring, so a docstring mention still puts
  an unrelated module into an ablation. For a BLIND verdict that direction is conservative; a
  coincidental redness there would report a sentence bound that is not. It changes ablation verdicts
  corpus-wide and belongs to that harness's owner.

## 8 · Scope held

⚠ **One in-scope failure of my own, corrected and recorded**: I launched a broad manuscript suite
twice, which this lane's contract forbids. It produced nothing that is used here. See §6.

⛔ No manuscript edited — the endpoint paper, the ASO papers and the FP paper are untouched;
perturbations ran only in throwaway clones. No floor moved. No exemption added or removed. No census
regenerated or committed. No 95-case sweep, no ablation rerun beyond the three identified sentences,
no source fetch. No commit, no push. Nothing spawned. No other owner's file written — P-ST's surface main/SI, TD1's dependency manuscript, TCIP's interface preprint, and the frozen FP (`f44b75588`) and MF1 (`0b965a127`) packages are all untouched.

⚠ **The two missing ASO case identities remain a documented diagnosis gap**
(`../PROPOSAL-ablation-unwitnessed-cases.md`). Nothing here identifies them, and the eight retained
ASO rows remain a partial, not an all-clear. No original record was recreated.
