# CHECKS — CORRECTED-C arm attribution (original check records, real exit codes)

Date 2026-09-08. Every exit code below is the actual exit status of the command shown; no pipe
masks a status (`${PIPESTATUS[0]}` is used where a pipe appears), and no check was declared
`EXIT=0` without being emitted.

⛔ **No network request of any kind was made.** ⛔ Nothing was committed or pushed.
⛔ Job 3 was **not** re-run; §5 below is the proof its artifacts are byte-unchanged.

## Scope of what was checked, and what was NOT

Focused checks of the **new mapping logic** and of the **specific prior counterexamples** only:
the zero-registered-arm rows, the substring-containment rows, the punctuation/dose-string
normalisation cases, the contradictory-placebo rows, and key/schema/row-coverage compatibility.
**No unchanged full source re-audit was run.** The disease and phase attributions are Job 3's and
were not re-derived or re-checked. `scripts/preflight.sh` was **not** run: it is the commit gate and
nothing is being committed here.

## Command log

```
### 1. cache integrity, run once
$ cd <cache> && sha256sum -c SHA256-MANIFEST.txt
ctg_results_bor_2022_2026.txt: OK
EXIT=0   [all 13 entries OK]

### 2. producer compiles
$ python3 -m py_compile CORRECTED-C-arm-attribution-derive.py
EXIT=0

### 3. producer + 13 deterministic checks
$ python3 CORRECTED-C-arm-attribution-derive.py CORRECTED-C-arm-attribution-map.tsv CORRECTED-C-arm-attribution-checks.json
EXIT=0   [checks_failed=0; the producer exits 1 if any check fails]

### 4. schema JSON well-formed
EXIT=0

### 5. Job 3 artifacts byte-unchanged after all of the above
1d7e8e18b7ad4c437b5a9776b76cfa8e7dd83ca1897f954dfada9c040497bbec  ../CURATION-endpoint-arm-attribution-map.tsv
b99d2af392ec70704cbc61adc41c6aa43ed209b7c940c8e5c4af487afa29e4b4  ../CURATION-endpoint-arm-attribution-derive.py
9b526b9bbf09f636b3fa67a4ad6855983122be75b5bc219bc379c0bff44e6416  ../CURATION-endpoint-arm-attribution.md
4f47d08cb110ab3e7653441cf2fcac1415e67d2d191a542f53379270d1fd1d07  ../PARENT-NOTE-zero-arm-not-control.md
EXIT=0

### 6. new outputs
08b6f8a8a359e9789801f6a11db054a6f5531d7c58048a6047f011af707cb5f2  CORRECTED-C-arm-attribution-map.tsv
047cc3f1b96bedc97f212aba8a288c40369f8ca18e28e129274d20e7659310e2  CORRECTED-C-arm-attribution-checks.json
73d9f7a7756580c70515b3ce4c37cd99ff32158993d79d3307d64c0b055f087c  CORRECTED-C-arm-attribution-schema.json
2d66e15b17a26adb40afbe73c6dd9ff9bbbdda8b875ed9b3cc1526b08068b299  CORRECTED-C-arm-attribution-derive.py
EXIT=0
   553 440262 CORRECTED-C-arm-attribution-map.tsv
```

## The 13 deterministic checks inside the producer

Machine record: `CORRECTED-C-arm-attribution-checks.json` (`checks_failed: 0`). The producer
**exits 1 if any check fails**, so the `EXIT=0` in §3 above is the checks passing, not a claim.

| check | what a failure would have caught | result |
|---|---|---|
| `row_count_equals_552` | a row silently dropped or invented | PASS (`rows=552`) |
| `key_set_identical_to_job3` | a key that does not join to Job 3 / `C2_arms` | PASS (`only_new=0 only_job3=0`) |
| `no_row_missing_a_prior_row` | a corrected row with no prior state to compare | PASS (`missing=0`) |
| `confirmed_fields_only_when_CONFIRMED` | a confirmed field populated from a weaker state | PASS (0 violations) |
| `substring_containment_never_confirmed` | label-only containment promoted to a confirmed link | PASS (0 violations) |
| `zero_arms_never_not_control` | zero registered arms read as `NOT_CONTROL` | PASS (0 violations) |
| `contested_never_resolved_to_a_side` | a contradictory placebo row decided for one field | PASS (0 violations) |
| `candidate_control_carries_no_confirmed_type` | a proposed control carrying a confirmed type | PASS (0 violations) |
| `CONFIRMED_always_binds_one_registered_arm` | a leaf recovery confirmed without binding one arm | PASS (0 violations) |
| `unknown_to_not_control_only_on_record_evidence` | an UNKNOWN flipped to NOT_CONTROL without a registry type | PASS (0 violations) |
| `all_five_machine_states_distinct` | two machine states collapsed into one value | PASS |
| `absent_modules_stay_absent_in_this_cache` | a re-fetch, or use of a module the cache never held | PASS — `participantFlowModule` 0 and `armGroupLabels` 0 occurrences across all 12 payloads |
| `producer_makes_no_network_call` | a network import | PASS — imports are `collections, csv, json, os, re, sys` |

## What these checks do NOT establish

- They do **not** confirm job2 or job3. Those were **never independently confirmed**, and the
  552-key set, the four-cell category rules, the disease attribution and the phase attribution are
  inherited from that unconfirmed chain.
- They do not establish that any individual row's registry link is *true*; they establish that no row
  claims more than its stated evidence supports.
- A `PASS` here is a property of this mapping, not of the endpoint corpus, and not of any manuscript.
