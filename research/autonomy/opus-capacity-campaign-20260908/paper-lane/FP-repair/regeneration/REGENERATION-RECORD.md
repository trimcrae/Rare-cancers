# The one producer/artifact regeneration, recorded in full

## Command, exactly as run

```
cd /home/user/Rare-cancers
python3 research/manuscripts/emc_fusion_partner_pooling.py
```

- **stdout**: `regen-stdout.txt`, 7,380 bytes, first line
  `wrote /home/user/Rare-cancers/research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json`
- **stderr**: `regen-stderr.txt`, **0 bytes** — captured to its own file, not merged into stdout
- **exit code**: `regen-exit.txt` → `EXIT=0` (real `$?`, no pipe in the command)

⭐ **Exactly one regeneration was run.** All producer edits for REG-B-2, REF-B-2 and STAT-B-2 were made
first and the generator was invoked once.

## Bytes and hashes, before and after

`BEFORE-hashes.txt` and `AFTER-hashes.txt` hold `sha256` and byte size for the five load-bearing files.

| file | before (bytes) | after (bytes) |
|---|---:|---:|
| `emc_fusion_partner_pooling.py` | 141,313 | 147,369 |
| `emc-fusion-partner-pooling.json` | 113,953 | 117,419 |
| `emc-fusion-partner-stratification.md` | 88,081 | 90,417 |
| `emc-fusion-partner-correction-register.md` | 61,026 | 67,429 |
| `test_fusion_partner_prose_matches_its_artifact.py` | 151,822 | 155,018 |

⭐ The three "before" hashes for the producer, artifact and manuscript are **identical to those pinned in
`HANDOFF-FP-frozen-current.md` §1.2**, so this repair started from the package that handoff froze.
`BEFORE-emc-fusion-partner-pooling.json` is the pre-regeneration artifact retained verbatim.

## Semantic and numeric delta of the regeneration

`numeric-delta.txt` compares every leaf of the artifact before and after.

- **Numeric values changed at the same key: 0.**
- **Numeric keys removed: 3** — `cohorts[0].strata.EWSR1::NR4A3.{events,denom}` and the heterogeneity key
  `sunitinib-2014 (EWSR1 arm)`.
- **Numeric keys added: 3** — the same three values (`6`, `8`, `75.0`) under `non-TAF15` names.
- **Fields added: 2** — `cohorts[sunitinib-2014].assumptions[0]` and `[1]`.
- **Strings changed: 8** — `_generated_utc` (a timestamp), `A_tki_objective_response.verdict`, the secondary
  contrast `note`, `citations.davis2017.verification_note`, `cohorts[sunitinib-2014].stratum_definition`,
  `cohorts[llombart-bosch-2022-prevalence].context_note` (REG-B-2),
  `cohorts[sunitinib-2012-two-cases].overlap_note`, and `what_could_kill_this[4]` (STAT-B-2).

⭐ **Every one of those eight is a correction named in the register (A38, A41, A42).** No other section of
the artifact moved, and the primary prognostic calculations of analysis B are byte-identical
(`QUANTITY-ACCOUNTING.md`, last two rows).

## Focused FP checks — honest exit capture

⚠ **Two pytest runs, both recorded.** The first ran against the corrected tree before the register rows and
the guard bindings were reconciled, and it **FAILED**:

```
PYTEST_EXIT=1
3 failed, 177 passed
  test_every_artifact_pointer_the_prose_names_resolves
  test_every_fraction_and_percentage_is_bound_or_declared
  test_the_guard_binds_a_material_share_of_the_documents_figures
```

⚠ **The first run's raw stdout was written to `fp-pytest-stdout.txt` and then OVERWRITTEN by the second
run into the same path.** The block quoted above is the failing run's summary as it was emitted to the
terminal, retained here; its full traceback file no longer exists. Named as a gap rather than reconstructed.

All three were caused by the new register prose: a pointer written `what_could_kill_this[4]` that the
pointer resolver reads as a record id, and figures restated in the register that no binding or declaration
covered. ⛔ **The guard was not loosened to make them pass.** The pointer was rewritten in the register's own
words ("the fifth entry of `what_could_kill_this`"), the unbound restatements in A38 and A42 were replaced by
references to this directory, and A41's three prevalence shares — which are the evidence for the retracted
superlative and had to stay printed — were **bound to the artifact** by two new bindings, so the guard now
watches two figures more than before.

Second run, after those repairs, `stdout` in `fp-pytest-stdout.txt`, `stderr` in `fp-pytest-stderr.txt`
(0 bytes), exit in `fp-pytest-exit.txt`:

```
/root/.local/bin/pytest -q -p no:cacheprovider \
  research/manuscripts/tests/test_fusion_partner_prose_matches_its_artifact.py \
  research/manuscripts/tests/test_fusion_partner_prose_asserts_the_relations_its_artifact_computes.py \
  research/manuscripts/tests/test_fusion_partner_author_years_are_bound_to_the_citation_map.py \
  research/manuscripts/tests/test_the_fusion_partner_gene_identifiers_are_ones_an_artifact_names.py \
  research/manuscripts/tests/test_emc_fusion_partner_pooling_check.py

182 passed, 1 warning in 2.84s
PYTEST_EXIT=0
```

⭐ **`PYTEST_EXIT=0` was emitted by the shell, from an unpiped command.** It is a measurement, not an
inference. 182, not 180, because two bindings were added; **no test was skipped, deselected or removed**,
and the count rose only by the two new ones.

Two lint gates, each with its own `$?` (`lint-exits.txt`):

```
python3 research/manuscripts/lint_style.py        → lint_style: 0 ERROR across 15 file(s)        LINT_STYLE_EXIT=0
python3 research/manuscripts/lint_consistency.py  → lint_consistency: 0 ERROR across 29 target file(s)  LINT_CONSISTENCY_EXIT=0
```

⛔ **The old missing pytest exit code from the 2026-09-08T18:19:19Z five-module run stays unmeasured.**
Nothing here was run to manufacture it, and this run does not supply it retrospectively.

⛔ No broad manuscript suite, no preflight, no ablation, no mutation harness and no blind seat was run for
this repair. Their absence is unchanged from `HANDOFF-FP-frozen-current.md` §5 and is not softened here.
