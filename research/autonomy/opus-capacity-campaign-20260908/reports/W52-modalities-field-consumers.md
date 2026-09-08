<!-- collected 2026-09-08T04:49:12Z by campaign coordinator; agent id af975a1ff28cc7210; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-af975a1ff28cc7210.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Done. Scratch deleted, nothing written to the repo.

## Worker

W52, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: successor to W26d — does anything executable read the six unrendered `modalities.json` fields.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions. The coordinator must extract the runtime model from the transcript.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (long proxy/truststore lists marked `[elided]`):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=…  [elided, proxy list]
AI_AGENT=claude-code_2-1-263_agent
CLAUDE_CODE_USER_EMAIL=trimcrae@gmail.com
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_DEBUG=true
CLAUDE_PID=522
CLAUDE_AUTO_BACKGROUND_TASKS=true
CLAUDE_AFTER_LAST_COMPACT=true
CLAUDE_EFFORT=medium
CLAUDE_CODE_GZIP_REQUEST_BODIES=1
CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST=1
CLAUDE_CODE_MESSAGING_SOCKET=/tmp/cc-socks/522.sock
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80
CLAUDECODE=1
SESSION_INGRESS_URL=https://api.anthropic.com
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_WORKER_EPOCH=1
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_PROXY_RESOLVES_HOSTS=true
CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1
GLOBAL_AGENT_NO_PROXY=…  [elided, proxy list]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=…  [elided, truststore + proxy flags]
NO_PROXY=…  [elided, proxy list]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=…  [elided, proxy list]
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**State, start and end.**

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 04:41:40 UTC 2026` | `Tue Sep  8 04:45:21 UTC 2026` |
| `git rev-parse HEAD` | `7a1002679e0830fb19bed48660772cdcc91c495d` | `fb1a3f8040537234010114053b36ec55b729c65e` |
| `git status --porcelain` | 0 lines | 0 lines |

**HEAD moved under me, and I verified it did not disturb anything I measured**, rather than assuming: `git diff --name-only 7a100267 fb1a3f80 | grep -v opus-capacity-campaign-20260908` returns **0 files**, and `git diff --stat 7a100267 fb1a3f80 -- systems/graph/modalities.json systems/schema/modality.schema.json systems/systems_check.py systems/tests/test_modality_census.py research/modalities/census_novelty_audit.py` returns **0 lines**. Every file in this report is byte-identical at both commits.

Write isolation honoured: nothing written, moved or deleted under `/home/user/Rare-cancers`; no git write operation; `scripts/preflight.sh` not run; `systems_check.py --write-views` not run; `atr_hrd_sarcoma_series.py` not invoked at all; no repair, patch, gate or test authored or proposed as code. All execution under `/tmp/claude-0/w52/`, **deleted before returning** (`ls` → `No such file or directory`). No network, paid API, GPU, human contact or publication. No clinical, efficacy, safety, selectivity or readiness claim; there is no wet lab. No content-policy refusal occurred.

---

## Question

For the six `modalities.json` fields W26d measured as reaching zero generated views, and for **every** field name in `modalities.json`: which are read by an executable anywhere in the tree, and which are read by nothing?

Open because W26d filed it explicitly as a limitation it did not answer: *"'Invisible to the view-drift guard' is … not a claim that no check anywhere covers these fields. I did not audit `systems/tests/` for an independent assertion over `modalities.json`. Whether some other check reads these fields is UNKNOWN, not zero."*

---

## Prior-work check

Read in full first: `COMMON-BRIEF.md` (including the HEAD correction, the pytest-interpreter trap, and the "Known, measured, and NOT worth rediscovering" section), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W26d-refuted-clause-blast-radius.md`. `reports/W25-*` not read, not referenced.

- **Taken as given, not re-derived:** W26d's zero-view blast radius for the six fields; the census renderer's route gating; the fan-out range correction; the campaign resolution rate; the `origin/literature-cache` question; the `systems_check --check` campaign-footprint baseline. **No sentinel was run and no view was regenerated.**
- **The pytest trap from the brief cost me one tool call and I record it as a confirmation, not a discovery:** my first probe run under `/usr/local/bin/python3` died with `ModuleNotFoundError: No module named 'pytest'` at `test_modality_census.py:21`; rerunning under `/root/.local/share/uv/tools/pytest/bin/python3` (pytest 9.1.1) worked. Exactly as documented.
- Commands run for prior-work and consumer discovery (campaign directory excluded from every one):
  - `rg -ln --glob '!research/autonomy/opus-capacity-campaign-20260908/**' -g '*.py' -g '*.mjs' -g '*.sh' 'modalities' systems/ scripts/ research/` → 400+ files, but almost all are the **directory** `research/modalities/`, not the graph file.
  - `rg -ln 'modalities\.json' -g '*.py' -g '*.mjs' -g '*.sh' .` → exactly **two** files: `systems/tests/test_modality_census.py`, `research/modalities/census_novelty_audit.py`.
  - `rg -n 'graph/modalities|"modalities"|load_graph|GRAPH_FILES' systems/ scripts/ research/` → adds `systems/systems_check.py` (the generic `load_graph`/`COLLECTIONS` path) and `systems/tests/test_systems_check.py`.
  - `rg -n "[\"']<field>[\"']" systems/ scripts/ research/` for each of the 20 distinct names, then every hit's use site read in source.
- **No sibling campaign report is used as evidence.** W26d supplied the six field names only.

---

## Method / inputs

| input | role |
|---|---|
| `/home/user/Rare-cancers` @ `7a100267` → `fb1a3f80` (identical on every file cited) | tree under test, read-only |
| `systems/graph/modalities.json` (187,400 bytes, 217 records, 20 distinct key names) | the file whose fields are enumerated |
| `systems/schema/modality.schema.json` | read in full — `additionalProperties: false`, 9 required, per-field `type`/`enum`/`const`/`pattern`/`minLength` |
| `systems/systems_check.py` | `load_graph` (217), `check_schemas` [S1] (498), `check_pointers` [P1]/[P2] (709), `check_ids_unique` [I1], relation guard [X1]/[X2] (2384–2400), `render_modalities` (3766–3878) |
| `systems/tests/test_modality_census.py` | 18 assertions; every `m[...]`/`m.get(...)` site read |
| `research/modalities/census_novelty_audit.py` | the only non-`systems/` executable that opens the file (line 33, 96) |
| `scripts/tests/test_no_hand_authored_json_has_a_duplicate_key.py` | globs `systems/graph/*.json` — reads key **names**, never values |
| `/tmp/claude-0/w52/graph/` | scratch **copy** of `systems/graph/*.json`; every mutation happened here, `sc.GRAPH` repointed at it |

Field enumeration was by `json.load` + recursive key walk, not by grep. Python 3.11 stdlib; assertion probe under the uv-tool interpreter (pytest 9.1.1). No network.

**Distinguishing a real dereference from an incidental string** was done by reading each hit: e.g. `"band"`, `"group"`, `"kind"` have dozens of hits under `research/modalities/*.py` and in `systems_check.py`, but every one is on a *different* object (blockers `b`, YAML frontmatter `fmv`, plan blocks, docking score rows), not a modality row. Those are excluded.

---

## Result

### R.1 — Every field name in `modalities.json`, and what reads it `PRIMARY`

"Read by" = a use site where the value of that field on a **modality row** is dereferenced. Schema constraint is listed separately because the schema is a data document applied generically by `check_schemas`, not code that names the field.

| field | occurrences in `modalities.json` | read by (file:line) | schema constraint applied by `systems_check.check_schemas` [S1] | grade |
|---|---:|---|---|---|
| `id` | 217 | `systems_check.py:230` (`by_id`), `:2384`, `:3830`, `:3866`; `test_modality_census.py:42,116,162,184,189,289,311`; `census_novelty_audit.py:122` | `pattern ^MOD-[A-Z0-9-]+$` | READ |
| `name` | 217 | `systems_check.py:3830,3866`; `test_modality_census.py:308` (claim-language regex); `census_novelty_audit.py:83,123` | `minLength 4` | READ |
| `level` | 217 | **nothing** | `const "cross-cutting"` | **UNREAD by code** |
| `kind` | 217 | **nothing** | `const "modality_class"` | **UNREAD by code** |
| `band` | 217 | `systems_check.py:3813,3820` | 4-value `enum` | READ |
| `group` | 217 | `systems_check.py:3830,3837` | 19-value `enum` | READ |
| `verdict` | 217 | `systems_check.py:3778,3809,3846,3853,3866`; `test_modality_census.py:43,59,112,150,163,173,343`; `census_novelty_audit.py:124` | 7-value `enum` + 4 `allOf` implications | READ |
| `prior_coverage` | 217 | `systems_check.py:3778,3809,3820,3865`; `test_modality_census.py:163`; `census_novelty_audit.py:108,144` | 2-value `enum` + `allOf` implication | READ |
| `rationale` | 217 | `systems_check.py:3864` (**route-gated — never reached for the 5 records at issue**); `test_modality_census.py:149-150` (`already_rejected` rows only), **`:308` (ALL rows, claim-language regex)** | `minLength 40` | READ |
| `exemplar` | 217 | `systems_check.py:3866`; `census_novelty_audit.py:83` | `type string` | READ |
| `prior_ref.file` | 106 | `systems_check.py:3858-3861`; `check_pointers:713-716` [P1]; `test_modality_census.py:132,289` | `required` inside object | READ |
| `prior_ref.anchor` | 83 | `systems_check.py:3862`; `check_pointers:719-721` [P2] | `type string` | READ |
| `route` | 75 | `systems_check.py:3846-3850`, relation guard `:2390-2400` [X1]/[X2]; `test_modality_census.py:42-43,58-59,114,230,345` | `pattern ^RT-…` + `allOf` `on_board ⇒ route` | READ |
| **`requires`** | **27** | **nothing — zero quoted hits in any `.py`/`.mjs`/`.sh` under `systems/`, `scripts/`, `research/`** | `type array`, `items.minLength 8` | **UNREAD by code** |
| `blockers` | 37 | `test_modality_census.py:184`; relation guard `:2390-2400` | `items.pattern ^BLK-…` | READ |
| `revisit_trigger` | 9 | `test_modality_census.py:175`; relation guard | `items.pattern ^TECH-…` + `allOf` | READ |
| `zero_dollar_next_step` | 33 | `systems_check.py:3832`; `test_modality_census.py:308,352` | `minLength 20` + `allOf` `candidate ⇒ zdns` | READ |
| `provenance` (`.owner.file`) | 217 (323 `file` nodes total incl. `prior_ref`) | `check_pointers` via `_owner_blocks:713-716` [P1] | `type object`, `additionalProperties: true` | READ |
| `parent` | **0 instances** | `test_modality_census.py:190-195` (cycle/resolution check) | `pattern ^MOD-…` | READ (but no data to read) |

Two whole-file guards read key **names** only, never values, and so cannot distinguish any of the above: `scripts/tests/test_no_hand_authored_json_has_a_duplicate_key.py:45` (glob `systems/graph/*.json`) and `systems_check.check_ids_unique`. `systems/parser_guard.py:191-195` lists five graph files for parser checking — **`modalities.json` is not among them.**

### R.2 — ⭐ Direct answer to W26d's open question, for the six named fields `PRIMARY`

| W26d field | view reach (W26d, given) | any executable assertion? | which |
|---|---:|---|---|
| `MOD-ARGININE-DEPRIVATION.requires[0]` | 0 views | **schema only** | `items.minLength 8`, [S1] |
| `MOD-PRMT5-MAT2A.requires[0]` | 0 views | **schema only** | `items.minLength 8`, [S1] |
| `MOD-PRMT5-MAT2A.rationale` | 0 views | **YES — one** | `test_modality_census.py:308` claim-language regex; plus `minLength 40` |
| `MOD-MCL1-BCLXL.rationale` | 0 views | **YES — one** | same |
| `MOD-RET.rationale` | 0 views | **YES — one** | same |
| `MOD-TF-LBD-OCCUPANCY.rationale` | 0 views | **YES — one** | same |

So W26d's UNKNOWN resolves **two ways in the same set**. The four `.rationale` fields are *not* uncovered: `test_no_row_asserts_efficacy_safety_or_readiness` iterates **every** modality row with no route gating and no verdict gating, so it reaches prose the renderer never prints. The two `requires[0]` fields are covered by **nothing but a length floor** — no code anywhere reads the field, and the one content-level assertion that exists checks `("rationale", "zero_dollar_next_step", "name")` and omits `requires`.

⚠ The rationale coverage is **narrow, not general**. The regex is `\b(?:cures?|will treat|efficacious|is safe|therapeutic window|clinically ready)\b`. It catches one class of overclaim. It cannot see a false absence, a wrong direction of effect, or a stale citation — which is what W26c graded those clauses FALSE for. **A named human reviewer is still required for all six; one of the two reasons W26d gave for that is now removed and the other stands.**

The second gating clause in `test_modality_census.py:149-150` (rationale length cap, "a pointing verdict points rather than argues") applies only to `verdict == "already_rejected"`. Measured verdicts of the five records: `MOD-RET` `excluded`, `MOD-ARGININE-DEPRIVATION` `excluded`, `MOD-PRMT5-MAT2A` `candidate`, `MOD-MCL1-BCLXL` `candidate`, `MOD-TF-LBD-OCCUPANCY` `on_board`. **None is `already_rejected`, so that cap fires on none of them.**

### R.3 — Mutation probe: what each guard actually catches `PRIMARY`

Run on a scratch copy of `systems/graph/` with `sc.GRAPH` repointed; the live tree was never mutated. Baseline on the unmutated copy: 16/17 graph-fixture tests pass, 1 uses a different fixture and was not exercised; 0 schema errors on `modalities`.

| case | mutation | caught by | schema [S1] |
|---|---|---|---|
| A | `MOD-RET.rationale` → *"This route is safe and cures the disease in EMC patients."* | ✅ `test_no_row_asserts_efficacy_safety_or_readiness` → `[('MOD-RET','rationale','is safe')]` | clean |
| B | `MOD-ARGININE-DEPRIVATION.requires[0]` → *"the tumour is safe and this cures it"* | ⛔ **nothing — 16/16 still pass** | clean |
| C | `MOD-PRMT5-MAT2A.requires[0]` → `"XX"` | nothing | ✅ `requires/0: 'XX' is too short` |
| D | `MOD-MCL1-BCLXL.rationale` → 49 chars of `Z` filler | ⛔ **nothing — 16/16 still pass** | clean |
| E | `MOD-TF-LBD-OCCUPANCY.rationale` → `"ZZZZZZZZZZ"` | nothing | ✅ `rationale: 'ZZZZZZZZZZ' is too short` |

⭐ **Case B is the finding.** The exact overclaim language the census's own guard exists to forbid passes silently when written into `requires` instead of `rationale`. **I am reporting this reach measurement; I propose no gate, test or repair, and none should be invented to make the field look covered.**

Case D shows the ceiling on the rationale coverage: replacing a 286-character scientific rationale with filler of legal length trips nothing.

### R.4 — How much of `modalities.json` no executable reads `PRIMARY`

Denominators measured, not estimated. Bytes are the UTF-8 footprint of each `"key": value` pair as serialized at `indent=2`; 172,331 of 187,400 bytes (92.0%) are attributable this way, the remaining 8% being structural punctuation and indentation.

| measure | unread by any executable | total | share |
|---|---:|---:|---|
| **distinct field names** | **3** (`level`, `kind`, `requires`) | 17 present (18 incl. schema-declared `parent`, 0 instances) | **17.6%** |
| **field instances** | **461** (217 `level` + 217 `kind` + 27 `requires`) | 2,674 | **17.2%** |
| **bytes** | **14,167** | 187,400 | **7.56%** |

Two qualifications that matter more than the headline:

- **`level` and `kind` are constants, not content.** Every record carries `"level": "cross-cutting"` and `"kind": "modality_class"`; the schema pins both with `const`. They are unread by code and that is harmless — there is nothing in them to be wrong about. Excluding them, the **substantive** unread surface is `requires` alone: **1 of 15 content-bearing field names, 27 of 2,240 instances, 2,883 bytes = 1.54% of the file.**
- **Free-text prose in this file totals 90,653 bytes (48.4%)** — `rationale` 59,130 + `zero_dollar_next_step` 11,686 + `name` 9,888 + `exemplar` 7,066 + `requires` 2,883. Of that prose, **3.2% (`requires`) is read by nothing**, and **7.8% (`exemplar`, 7,066 bytes) is read by code but by no content assertion at all** — `census_novelty_audit.py:83` and the renderer print it; nothing checks what it says. The claim-language guard covers `rationale` + `zero_dollar_next_step` + `name` = **80,704 bytes, 89.0% of the file's prose.**

⚠ `rationale` is 31.6% of the whole file by bytes, and by W26d's measurement much of it never renders. It is nonetheless the best-covered prose field here: schema floor plus a live all-rows content assertion.

---

## Validation evidence

Environment for every run: `/home/user/Rare-cancers` read-only; scratch at `/tmp/claude-0/w52/` (deleted); Linux; `/usr/local/bin/python3` = 3.11 stdlib; assertion probe under `/root/.local/share/uv/tools/pytest/bin/python3`, pytest 9.1.1. No network.

### `RUN` — the modality census suite at HEAD, unmutated
```
$ pytest -q -p no:cacheprovider systems/tests/test_modality_census.py
..................                                                       [100%]
18 passed in 0.20s
EXIT=0
$ git status --porcelain | head        # (empty)
```
`-p no:cacheprovider` was used specifically so pytest wrote no `.pytest_cache` into the tracked tree; `git status --porcelain` was 0 lines immediately after.

### `RUN` — the pytest-interpreter trap, confirming the brief
```
$ python3 /tmp/claude-0/w52/probe.py
  File "/home/user/Rare-cancers/systems/tests/test_modality_census.py", line 21, in <module>
    import pytest
ModuleNotFoundError: No module named 'pytest'
$ head -1 /root/.local/bin/pytest
#!/root/.local/share/uv/tools/pytest/bin/python3
$ /root/.local/share/uv/tools/pytest/bin/python3 -c "import pytest,sys;print(pytest.__version__,sys.executable)"
9.1.1 /root/.local/share/uv/tools/pytest/bin/python3
```

### `RUN` — mutation probe, verbatim (scratch graph copy only)
```
--- BASELINE (unmutated copy)
   test_a_prior_rejection_table_has_not_grown_past_the_census -> SKIPPED(other fixture)
   n_pass= 16 n_nonpass= 1
SCHEMA baseline modality errors: 0
--- A rationale claimy (MOD-RET)
   test_no_row_asserts_efficacy_safety_or_readiness -> FAIL: modality rows asserting efficacy,
       safety or readiness: [('MOD-RET', 'rationale', 'is safe')]
   n_pass= 15 n_nonpass= 2
   schema modality errors: []
--- B requires[0] claimy (MOD-ARGININE-DEPRIVATION)
   n_pass= 16 n_nonpass= 1
   schema modality errors: []
--- C requires[0] emptied to garbage (MOD-PRMT5-MAT2A)
   n_pass= 16 n_nonpass= 1
   schema modality errors: ["modalities/MOD-PRMT5-MAT2A requires/0: 'XX' is too short"]
--- D rationale replaced by 45-char filler (MOD-MCL1-BCLXL)
   n_pass= 16 n_nonpass= 1
   schema modality errors: []
--- E rationale truncated to 10 chars (MOD-TF-LBD-OCCUPANCY)
   n_pass= 16 n_nonpass= 1
   schema modality errors: ["modalities/MOD-TF-LBD-OCCUPANCY rationale: 'ZZZZZZZZZZ' is too short"]
RESTORED True
```
`RESTORED True` is a byte comparison of the scratch copy against the live file after the last case.

### `RUN` — `requires` has zero code hits
```
$ rg -c --glob '!research/autonomy/opus-capacity-campaign-20260908/**' -g '*.py' -g '*.mjs' -g '*.sh' \
     "[\"']requires[\"']" systems/ scripts/ research/     # total hits: 0
```
Compare `blockers` 115, `revisit_trigger` 7, `zero_dollar_next_step` 3, `exemplar` 2, `prior_coverage` 7 hits — each of which I then resolved to a real modality-row use site by reading it.

### `RUN` — the only two executables that open the file
```
$ rg -ln 'modalities\.json' -g '*.py' -g '*.mjs' -g '*.sh' .
./systems/tests/test_modality_census.py
./research/modalities/census_novelty_audit.py
```
plus `systems/systems_check.py`, which reaches it generically via `COLLECTIONS` (`:64`) and `load_graph` (`:217-227`), never by that filename.

### `RUN` — HEAD moved, nothing measured changed
```
$ git diff --name-only 7a1002679e0830fb19bed48660772cdcc91c495d fb1a3f8040537234010114053b36ec55b729c65e \
    | grep -v opus-capacity-campaign-20260908 | wc -l
0
$ git diff --stat 7a100267 fb1a3f80 -- systems/graph/modalities.json systems/schema/modality.schema.json \
    systems/systems_check.py systems/tests/test_modality_census.py research/modalities/census_novelty_audit.py | wc -l
0
$ rm -rf /tmp/claude-0/w52 && ls -d /tmp/claude-0/w52
ls: cannot access '/tmp/claude-0/w52': No such file or directory
```

### `PROPOSED (NOT RUN)`
- Any test, gate, guard, schema change or repair for `requires`, `exemplar`, or the six fields. **Not authored, not proposed as code, not sketched.** The disposition is not mine.
- `systems/systems_check.py --check` and `--write-views` in any form; `scripts/preflight.sh`. Not run.
- Any re-sentinel or re-render of W26d's measurement. Not run; taken as given.
- Coverage audits of the other 18 `systems/graph/*.json` collections. Out of scope for this unit.

---

## Limitations

- **Valid for the state of these five files at `7a100267`/`fb1a3f80` only**, verified identical at both.
- **"Read by" means a static use site I read, plus — for the six named fields — an executed mutation probe.** For fields outside those six I did not mutation-probe every one, so a use site could in principle be unreachable at runtime (dead branch, gated fixture). Static presence of a dereference is weaker evidence than a fired assertion.
- **Absence of a grep hit is not proof of absence of a read.** A consumer that reads modality rows through a fully dynamic key (`row[k]` inside a loop over `row.items()`) would not appear in a quoted-name search. I found one such generic path and report it — the `[X1]`/`[X2]` relation guard at `systems_check.py:2390-2400` iterates `row.items()` and inspects every value for modelled ids. It *touches* `requires` values but its test (`_id_refs`) never matches prose, so it constrains nothing there. I cannot rule out another such path I did not read.
- **`.github/workflows/` and non-`systems`/`scripts`/`research` locations were excluded by the dispatch's scope.** Whether CI wires an additional check over this file is UNKNOWN, not zero.
- **`test_a_prior_rejection_table_has_not_grown_past_the_census` was not exercised** in the mutation probe (it takes a different fixture). Its source reads a prior-search table, not modality prose fields, so I do not expect it to change the table — but that is a source reading, not a run.
- **A guard's existence is not a guard's adequacy.** The four rationale fields are covered by one six-alternative regex and a 40-character floor. Case D shows that clears with filler. Nothing here says the six fields are adequately checked; it says exactly which mechanisms touch them.
- **Byte shares depend on the serialization convention** (`indent=2`); 8% of the file is structural characters attributable to no single field.
- **No clinical claim.** Every number is a count of bytes, keys or assertions in tracked files. I did not verify any scientific content of any field, and W26c's FALSE grades are carried forward unexamined.

---

## Stop condition

**Set up front:** return the moment (a) the union of field names in `modalities.json` is enumerated from the parsed file, (b) every name is resolved to a read site or to UNREAD by reading each hit's use site, (c) the six named fields have a yes/no answer backed by an executed probe rather than a source reading, and (d) the unread fraction is stated in both bytes and field count — or at ~40 tool calls / ~40 minutes.

**MET on all four legs, well inside budget.** 20 names enumerated by `json.load`; all resolved; the six answered by a five-case mutation probe with exit evidence; unread fraction reported three ways (names, instances, bytes) with the constants-vs-content split made explicit.

---

## Tool-call and wall-clock count actually used

**17 tool calls** (target ~40). **Wall clock 3 min 41 s by the UTC clock** — `date -u` start `04:41:40Z`, end `04:45:21Z` (target ~40 min); real elapsed session time including model latency was longer, and I report the clock bracket rather than an estimate. One call was spent rediscovering the documented pytest-interpreter trap. The saving comes from W26d having already established the zero-view reach, so no sentinel or regeneration phase was needed — I record that so the speed is not read as reduced scope.

---

## Next concrete action

**Route to whoever owns `systems/tests/`: `test_no_row_asserts_efficacy_safety_or_readiness` (`systems/tests/test_modality_census.py:308`) checks `("rationale", "zero_dollar_next_step", "name")` and omits `requires` and `exemplar`, and the measured consequence is that the string *"the tumour is safe and this cures it"* placed in `MOD-ARGININE-DEPRIVATION.requires[0]` passes the entire suite and the schema (probe case B).** That is a field-list asymmetry in an existing guard whose own docstring explains it exists because the census view is linted by nothing else. **I propose no change and have authored none** — the owner decides whether the omission is deliberate (the schema's `_role` note does say the target axis is *allowed* to touch the modality axis only in `requires`, which may be why the prose there is treated differently) or an oversight. The decision needs the person who wrote the field list, not a worker who measured it.

Two smaller items, both measured here and both for the same owner:
1. **`exemplar` (7,066 bytes, 217 instances) is printed by two executables and asserted by none** — and its schema description already carries the warning `⚠ NAMING ONE IS NOT A CLINICAL CLAIM about it, and must never be written as one`. That warning is enforced nowhere.
2. **`modalities.json` is absent from `systems/parser_guard.py:191-195`**, which lists `routes`, `strategies`, `blockers`, `technologies` and `forecasts`. Whether that omission is deliberate is UNKNOWN; I did not read the guard's purpose closely enough to say.

For W26d's lane specifically there is **no further reach work**: the question it left open is now answered, and the honest successor — an adequacy audit of the claim-language regex against the kinds of error W26c actually graded — is a scientific review task, not a reach measurement, and belongs with a named human reviewer rather than another blast-radius run.
