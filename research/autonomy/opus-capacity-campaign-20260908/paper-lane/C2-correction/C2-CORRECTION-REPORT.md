# C2 finite correction — delivered evidence

Date 2026-09-08. Owner: the single admitted C2 correction owner. Scope: the five finite C2 items in
`C2-Integration2-and-PAB2-root-adjudication-20260908.md` (root memo, 9,183 B, read in full), applied
as one settled correction BATCH over the same inputs. A batch is not one execution: it took two
actual derivations (RUN-01 and the settled RUN-05) with the delta and test runs separate, and
RUN-02's exit 1 is an original result that the later 21-pass run does not overwrite. No commit and no push were made from this
lane; the parent integrates.

**This is an inference and label correction over existing observations.** No new source
adjudication, no new clinical science, no source acquisition, no row eligibility, no rates, no
patient pooling, no source-join verification, no endpoint-paper reopening, no jobs 2/3 re-run, no
broad suite, no floor change, no publication-gate amnesty, and **no count quota**. The endpoint
paper remains **PARKED** under its existing ten scientific findings.

## What was produced

New, explicitly versioned sibling outputs in this directory. v2, v1, Job 3, the cache and the leaves
are untouched.

| Artifact | Bytes | Role |
|---|---|---|
| `CORRECTED-C-arm-attribution-v3-derive.py` | 63,777 | corrected producer (v2 producer + the five corrections) |
| `CORRECTED-C-arm-attribution-v3-map.tsv` | 872,675 | 552 rows × 53 columns |
| `CORRECTED-C-arm-attribution-v3-checks.json` | 10,763 | 32 checks, 0 failed, plus the corrected counts |
| `CORRECTED-C-arm-attribution-v3-schema.json` | 10,446 | 53 columns documented in emitted order |
| `CORRECTED-C-arm-attribution-v3-tests.py` | 26,310 | 21 focused value/edge-case tests, 21 PASS |
| `C2-v2-to-v3-delta.py` | 6,899 | read-only field/row map producer |
| `FIELD-MAP-v2-to-v3.tsv` | 2,657 | 39 v2 columns → 53 v3 columns |
| `ROW-DELTA-v2-to-v3.tsv` | 286,704 | per-row v2→v3 disposition, all 552 rows |
| `CHECKS-RUNS/RUN-*` | — | every attempt, its exact command, stdout, stderr and real exit code |

Exact hashes: `SHA256-v3-artifacts.txt`.

## Item 1 — count complement

v2 lines 683–696 set `not_source_confirmed_rows` from a hand-listed subset of four states
(`PROPOSED`, `UNRESOLVED`, `CONTESTED`, `UNKNOWN_IN_THIS_CACHE`), silently omitting the 132
`LABEL_MATCH` rows. It reported **362** where the complement of the named state is **494**.
**All 18 of v2's saved checks passed with this error present.**

v3 adds `partition_counts()`, which computes any complement as *total minus the named state* and
returns the partition so a caller can test that it sums. Delivered values (all measured, from
`CORRECTED-C-arm-attribution-v3-checks.json`):

```
total_rows                               552
rows_in_a_source_field_match_state        58
rows_not_in_a_source_field_match_state   494
  by state: LABEL_MATCH 132 | PROPOSED 337 | UNRESOLVED 11 | CONTESTED 1 | UNKNOWN_IN_THIS_CACHE 13
rows_in_PROPOSED_UNRESOLVED_CONTESTED_or_UNKNOWN   362   (the honest name for what v2 measured)
v2_not_source_confirmed_rows_withdrawn: v2_reported 362, actual complement 494,
                                        rows_moved_or_promoted_to_fix_it 0
```

Three checks enforce it: `state_counts_partition_every_row_exactly_once`,
`the_complement_is_total_minus_the_named_state_not_a_hand_listed_subset`, and
`label_only_and_description_supported_matches_stay_separate_strengths`. Test `T6` proves the same
identity on a synthetic partition and on the empty case. **No row was promoted, moved or
re-adjudicated.** The 362 figure is retained under a name that says what it counts.

## Item 2 — contested binding is cleared

v2 lines 343–348 downgraded a bound arm to `CONTESTED` on the arm's own contrary registered
description but left `bound_arm_index` set, contradicting the schema and the check at v2 lines
635–638 (`an_arm_is_bound_only_by_SOURCE_CONFIRMED_or_LABEL_MATCH`).

v3 clears the binding on downgrade and loses nothing:

- `arm_link_relation` → `CONTRARY_DESCRIPTION_BINDING_CLEARED:<original relation>`
- `downgraded_candidate_arm_index` / `_arm_label` / `_registered_type_verbatim` keep the candidate
- `candidate_arm_indices` = that index, `n_candidate_arms` = 1 — the candidate is not discarded
- `contrary_description_locator` = `…armGroups[i].description`, with the text in
  `contrary_description_evidence_excerpt`
- `arm_link_source_locator` still carries the original label locator
- a leaf verdict that stood before the downgrade is preserved in
  `leaf_claim_verification_before_downgrade`, and the live verdict becomes
  `LEAF_CLAIM_NOT_ADJUDICATED_BOUND_ARM_DESCRIPTION_CONTRARY`

Clearing the binding is **not** a claim that the candidate is the wrong arm.

The existing contrary-description fixture `T2a` was extended to assert the cleared binding, the
preserved candidate, both locators, the evidence text, and comparator propagation (role `CONTESTED`,
`bound_arm_registered_type_verbatim` empty because no type is read through a cleared binding, no
identity assumption, and the conditional arm-set statement with its own assumption). `T2e` adds the
leaf-agreement shape. Two checks enforce it in the delivered table. **No delivered row exercises
this branch: 0 of 552 rows carry a cleared binding, and the delivered CONTESTED row (1) is the
`LEAF_CLAIMED_ARM_LABEL_ABSENT_FROM_THIS_RECORD` shape.** The branch is checked by fixture.

## Item 3 — zero-arm contract

v2 evaluated the comparator-text proposal branches (lines 421–429) **before** the zero-arm
`UNKNOWN` branch (430–432), so group text could in principle have produced a comparator role in a
record with no registered arm to attach it to, against the broad saved invariant.

v3 decides zero arms **first**. For zero registered arms: `arm_link_state`,
`registry_type_statement` (now `UNKNOWN_NO_ARMS_REGISTERED_IN_THIS_CACHE`) and `comparator_role` are
all UNKNOWN. Any comparator wording in the results-group text is preserved as unverified evidence in
its own new column `group_text_comparator_wording_unverified`
(`GROUP_TEXT_PLACEBO_OR_SHAM_WORDING`, `GROUP_TEXT_NO_INTERVENTION_WORDING`,
`GROUP_TEXT_CONTROL_OR_COMPARATOR_WORDING`,
`GROUP_TITLE_TREATMENT_SEQUENCE_CONTAINING_A_PLACEBO_TOKEN`), populated on every row, not only
zero-arm rows (20 rows carry wording; distribution in the checks file).

`UNKNOWN` here means **not established in this cache — not that no comparator existed.**
New case `T2f` covers zero arms with explicit placebo wording and with control/sequence wording.
Two checks enforce it. The six delivered zero-arm rows were already UNKNOWN and are unchanged; none
of them carries comparator wording.

## Item 4 — evidence representation

**"Verbatim" was false.** v2 line 455 replaces newlines with spaces and cuts the leaf narrative at
400 characters, and the TSV writer normalises tabs and newlines again on the way out.

- `leaf_narrative_verbatim_not_parsed` → **`leaf_narrative_transformed_excerpt_not_parsed`**, with
  `leaf_excerpt_transform` =
  `NEWLINE_TO_SPACE;CUT_AT_400_CHARS;TSV_WRITE_NORMALISES_TAB_AND_NEWLINE;ORIGINAL_RETRIEVABLE_ONLY_VIA_leaf_claim_locator`,
  `leaf_excerpt_original_chars`, and `leaf_excerpt_at_400_char_cap`.
- The original leaf locator (`leaf_claim_locator`, `LEAF-OUT/<file>:line N`) is retained and is the
  only route to the untransformed text.
- `group_description` → `group_description_transformed_excerpt` with the same provenance pair.
- The narrative check's own description no longer says "carried verbatim only".
- **Observed, not assumed: 0 of 552 rows reach the 400-character cap** (`T7` reads the four
  delivered leaves read-only and asserts the recorded provenance against the values).

**"12 payloads" → the actual ten FILES entries.** The source-module-absence check reads
`FILES` = 5 BOR eras + 5 placebo eras = **10** cached payload files. The observation itself is
unchanged (`participantFlowModule` 0, `armGroupLabels` 0) and is **preserved as a ten-file scoped
observation, not a newly verified twelve-file absence**. A second check asserts the named scope
equals the files actually read. **No additional payload was audited.**

## Item 5 — no promotion of text correspondence to registry identity or independence

Agreeing label and description fields are two **correlated text fields of one record**, not two
independent sources, and their agreement is not a registry assertion that a results group **is** a
registered arm. The live machine vocabulary now says so:

| v2 token | v3 token |
|---|---|
| `SOURCE_CONFIRMED` (58 rows) | `SOURCE_FIELD_MATCH` (58 rows) |
| `TWO_INDEPENDENT_FIELD_IDENTITIES:<a>+<b>` | `TWO_AGREEING_FIELD_MATCHES:<a>+<b>` |
| `DESCRIPTION_FIELD_IDENTITY:<a>` | `DESCRIPTION_FIELD_MATCH_ONLY:<a>` |
| `LABEL_IDENTITY_ONLY:<a>` | `LABEL_FIELD_MATCH_ONLY:<a>` |
| `LABEL_IDENTITY_AND_DESCRIPTION_IDENTITY_DISAGREE` | `LABEL_FIELD_MATCH_AND_DESCRIPTION_FIELD_MATCH_DISAGREE` |
| `LABEL_AND_DESCRIPTION_SOURCE_IDENTITIES_NAME_DIFFERENT_ARMS` | `LABEL_AND_DESCRIPTION_FIELD_MATCHES_NAME_DIFFERENT_ARMS` |
| `COMPARATOR_SUPPORTED_BY_SOURCE_CONFIRMED_ARM_TYPE` (8 rows) | `COMPARATOR_TYPE_INFERRED_VIA_SOURCE_FIELD_MATCH` (8 rows) |
| `COMPARATOR_PROPOSED_BY_LABEL_MATCHED_ARM_TYPE` (13 rows) | `COMPARATOR_PROPOSED_BY_LABEL_FIELD_MATCHED_ARM_TYPE` (13 rows) |
| change-map class `COMPARATOR_SUPPORTED` (both sides) | class `COMPARATOR_TYPE_INFERRED` (both sides; same partition) |
| `not_source_confirmed_rows` = 362 | `rows_not_in_a_source_field_match_state` = 494, plus `rows_in_PROPOSED_UNRESOLVED_CONTESTED_or_UNKNOWN` = 362 |

- Unique exact and case/whitespace match locators, candidate lists and all ambiguities are preserved
  unchanged (`LABEL_BYTE_EXACT` 96, `LABEL_CASE_WS_FOLD` 36, `DESC_BYTE_EXACT`/`DESC_CASE_WS_FOLD`
  combinations 38 + 3 + 16, `UNRESOLVED` 11 with every candidate kept).
- **The 132 label-only rows and the 58 description-supported rows remain different evidence
  strengths** and are never summed into one "confirmed" figure; a check enforces it.
- **Comparator type inferred through a matched group-arm relationship now carries the unproved
  identity assumption** in machine state. New column `comparator_role_identity_assumption`:
  `ASSUMES_TWO_AGREEING_SOURCE_FIELD_MATCHES_ARE_ARM_IDENTITY_UNPROVED` (8 rows),
  `ASSUMES_LABEL_FIELD_CORRESPONDENCE_IS_ARM_IDENTITY_UNPROVED` (13 rows). Every bound row also
  names its assumption in `registry_type_statement_assumption` — in v2 the strongest state left that
  field empty, which read as independent registry confirmation.
  **The eight type-supported rows are not eight independently clinically validated comparators.**
- **Explicit source-join verification has NOT been established here.** Every row carries
  `source_join_verification` = `NOT_ESTABLISHED_REGISTRY_JOIN_FIELDS_ABSENT_FROM_THIS_CACHE`; the
  registry's own join fields (`resultsSection.participantFlowModule`,
  `armsInterventionsModule.interventions[].armGroupLabels`) are absent from this cache.
- A check refuses the tokens `SOURCE_CONFIRMED`, `TWO_INDEPENDENT_FIELD_IDENTITIES`,
  `COMPARATOR_SUPPORTED` and `INDEPENDENTLY_CONFIRMED` anywhere in the delivered state columns.

## Row map — what actually changed in the data

From `ROW-DELTA-v2-to-v3.tsv` (RUN-07, exit 0), over all 552 rows and every CARRIED column except
the two free-prose columns (`comparator_role_basis`, `arm_link_source_locator`, whose text the
corrections deliberately rewrite).

⛔ **Scope of the three counts below, stated precisely.** They classify the **carried** columns only.
**Outside** the classification, and therefore NOT covered by "IDENTICAL": the **two excluded prose
columns** (378 of the changed strings are comparator-basis text) and the **14 columns added in v3**,
which have no v2 counterpart to compare. **These counts are not proof of complete per-row semantic
identity**, and must not be quoted as if they were.

```
IDENTICAL         336
VOCABULARY_ONLY   158     (token renamed, same meaning, same row)
SUBSTANTIVE        58     (all of them: registry_type_statement_assumption, empty -> named)

rows whose arm_link_state changed after renaming    0
rows whose comparator_role changed after renaming   0
rows whose bound_arm_index changed                  0
columns: 39 -> 53   (2 renamed, 14 added, 0 removed)
changed cells: VOCABULARY arm_link_relation 190, arm_link_state 58, comparator_role 21,
               registry_type_statement 6, registry_type_statement_assumption 132,
               disposition_vs_v1 41; SUBSTANTIVE registry_type_statement_assumption 58
```

**The only substantive per-row change is that the 58 source-field-matched rows now name the
identity assumption they always rested on.** No state, role, binding or count of any delivered row
was altered to satisfy any of the five items.

## Commands, streams and real exit codes

Every attempt is preserved in its own directory under `CHECKS-RUNS/` with `cmd.txt` (cwd + the exact
expanded command), `stdout.txt`, `stderr.txt` and `exit.txt`. `run-check.sh` uses no pipes, so `$?`
is the command's own status. Nothing was overwritten or re-run in place.

| Run | Command (cwd = this directory) | Exit | Result |
|---|---|---|---|
| `RUN-01-derive-20260908T220048Z` | `python3 CORRECTED-C-arm-attribution-v3-derive.py CORRECTED-C-arm-attribution-v3-map.tsv CORRECTED-C-arm-attribution-v3-checks.json` | **0** | 552 rows, 32 checks, 0 failed |
| `RUN-02-tests-20260908T220237Z` | `python3 CORRECTED-C-arm-attribution-v3-tests.py` | **1** | **preserved failure**: 21 tests, 20 PASS, 1 FAIL — `T5a` still asserted v2's `assume == ""` for the strongest state, which item 5 withdraws. Stream kept intact. |
| `RUN-03-tests-20260908T220248Z` | `python3 CORRECTED-C-arm-attribution-v3-tests.py` | **0** | 21 tests, 21 PASS, 0 not-PASS after `T5a` was corrected to assert the named assumption |
| `RUN-04-delta-20260908T220413Z` | `python3 C2-v2-to-v3-delta.py` | **0** | field map + row map emitted |
| `RUN-05-settled-derive-20260908T220427Z` | same as RUN-01 | **0** | settled-tree re-derivation |
| `RUN-06-settled-tests-20260908T220430Z` | same as RUN-03 | **0** | 21/21 |
| `RUN-07-settled-delta-20260908T220430Z` | same as RUN-04 | **0** | field/row maps regenerated |

Reproducibility: `sha256sum -c` of the map and checks file taken before RUN-05 against the files
RUN-05 rewrote → both `OK`, exit 0. The settled tree derives byte-identically.

Input identities verified before and after the work:

- root memo `C2-Integration2-and-PAB2-root-adjudication-20260908.md`, 9,183 B, read in full;
  mechanical intake report `INTAKE-REPORT.md`, 12,688 B, sha256 `6905293f…` ✅ (parent-verified).
- v2 artifacts re-verified against `CORRECTED-C-arm-attribution-v2/SHA256-v2-artifacts.txt`:
  all 8 lines `OK` (exit 0) **after** this work — v2 is unmodified.
- `git status --porcelain` over `CORRECTED-C-arm-attribution-v2/`,
  `CORRECTED-C-arm-attribution/` and `LEAF-OUT/`: **empty**. Both original versions, the leaves and
  the cache are byte-preserved; every original attempt directory under
  `CORRECTED-C-arm-attribution-v2/CHECKS-RUNS/` (RUN-01 … RUN-08, including the two exit-1 runs) is
  untouched.
- cache: `/tmp/…/scratchpad/ctg-cache-216bd1b5`, read-only, no network call
  (`producer_makes_no_network_call` PASS).

## Residual limits — carried forward, not repaired

1. **Not repaired here, by instruction**: v2/P-AB2 attempt 04 holds a partial diagnostic stream,
   attempt 09's command is recorded in shorthand, attempt 08 embeds no module hash, and C2 RUN08
   uses command placeholders. These old outputs were **not reconstructed and not re-run**. The new
   `CHECKS-RUNS` runs here record fully expanded commands so the defect does not recur.
2. The contrary-description downgrade branch (item 2) is exercised by **fixture only**; no delivered
   row reaches it. Its behaviour in the delivered table is therefore checked as an invariant
   (0 violations), not observed.
3. The ten-file absence observation is **scoped to those ten payload files**. Nothing here
   establishes absence across any wider payload set.
4. **Explicit source-join verification remains unestablished** for every row: the registry's join
   fields are absent from this cache. Every state in this table is a computed correspondence between
   free-text source fields of one record.
5. The 552-row key set and Job 3's row-selection rule are **inherited unchanged** from the
   unconfirmed job2/job3 chain and are neither re-derived nor endorsed here.
6. Leaf narratives are transformed excerpts; the untransformed originals live only in the leaf files
   named by `leaf_claim_locator`. No narrative was observed at the cap, but that is an observation
   over the four delivered leaves, not a guarantee about any other input.
7. This correction changes vocabulary, one arithmetic complement, one schema violation, one branch
   order and two evidence descriptions. It **does not** make any row's clinical attribution more
   certain than v2 left it.

## Propagation note for the parent

Integration2 must carry forward: the corrected count complement (494, with 362 retained under its
operational name), the corrected field-match terminology and its two distinct strengths (132
label-only vs 58 description-supported), the unproved identity assumption on every inferred
comparator type, the ten-file scoping of the absence observation, and the transformed-excerpt label
on narrative text. Nothing in this component authorises the withdrawal or restatement of any
Integration2 contradiction claim; that is Integration2's own item.
