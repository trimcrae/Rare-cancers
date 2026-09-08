<!-- collected 2026-09-08T04:32:14Z by campaign coordinator; agent id aed8090adc524c954; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aed8090adc524c954.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Scratch deleted, live tree clean. Report follows.

---

## Worker

- **Worker:** W09i, lane 9 refill, OPUS-CAPACITY-CAMPAIGN-20260908. Successor to W09h, executing its named next action as a *measurement*, not a repair.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions only. The coordinator must extract the actual runtime model from the transcript.
- `date -u` **start** `Tue Sep  8 03:38Z` (first tool call) · **end** `Tue Sep  8 03:52:40 UTC 2026`.
- `git rev-parse HEAD` **start** `1c9d827870599576c0c027a9134363d59456fd04` · **end** `604984d8f6d3623e0c9fc59b52b50181f617b9e7`. ⚠ **HEAD moved under me.** `git diff --stat 1c9d8278 604984d8 -- systems/` is **empty**; `git diff --name-only` between them touches only `research/autonomy/opus-capacity-campaign-20260908/` and its `reports/`. Every measurement below is valid at both HEADs.
- `git status --porcelain` **start** 0 lines · **end** 0 lines. **Write isolation honoured:** nothing written, moved or deleted under `/home/user/Rare-cancers`; no git write operation; `scripts/preflight.sh` not run; `--write-views` never run against the live tree; no graph file and no `systems_check.py` touched in the live tree; no patch authored or proposed. All execution under `/tmp/claude-0/w09i/`, **now deleted** (`rm -rf /tmp/claude-0/w09i`; free disk after: 20 GiB).
- No network, no retrieval, no paid API, no GPU. `research/modalities/atr_hrd_sarcoma_series.py` never invoked. W25 not read or referenced. Frozen corpus not read (not needed — this is a measurement on the live tree).

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (exit 0, captured at start; 51 lines, five long proxy lines elided as marked, nothing else removed):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
[no_proxy=… elided]
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
[GLOBAL_AGENT_NO_PROXY=… elided]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
[JAVA_TOOL_OPTIONS=… elided]
[NO_PROXY=… elided]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
[npm_config_noproxy=… elided]
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

At end, `env | grep -i -E 'claude|anthropic|model' | grep -c .` returned **51** — the same line count. I did not re-paste the block; nothing exported during the run.

---

## Question

W09h measured one instance of a general hole: `systems_check.py --write-views` does not run `check_schemas` before writing, so deleting `outcome_potential_why` from all 33 publication records gives exit 0 and 111 byte-identical views, while the same tree in plain mode gives exit 1 and 33 `[S3]` errors.

**How large is that hole?** For *every* required name `check_schemas` actually enforces, on a scratch copy: delete the field from all records, run `--write-views`, and record the real exit code and whether the regenerated views are byte-identical to the committed baseline. Report the three-way split — invisible to `--write-views`, noticed by it, untested.

Open because W09h explicitly says the 92-name figure was inherited from a name-level census and only one name was demonstrated. A blast radius asserted from a census is not a measured blast radius.

**Answer, exhaustively measured, no sampling:** of the **148** (collection, required-name) pairs that actually exist in `systems/graph/`, **40 are wholly invisible to `--write-views`** (exit 0, `wrote 111 view(s)`, byte-identical views, 1,547 required field instances deleted), **35 change a view** (exit 0, views differ), **73 exit 1 — but every one of them by an uncaught `KeyError`, not a check** (73/73 verified). **0 untested.** So the mode that people run after editing the graph catches nothing by design: where it appears to fail, it is crashing.

---

## Prior-work check

| command / read | what it showed |
|---|---|
| read in full, as dispatched | `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W09h-successor.md` (whole, incl. R.5), `systems/POLICY-evidence.md` |
| `sed -n '470,560p' systems/systems_check.py` | the actual body of `check_schemas` — it validates **exactly 10 collections** against 10 schema entrypoints (`[S1]` strategies/routes/blockers/modalities; `[S3]` lanes/requirements/instruments/publications; `[S2]` technologies; `[S3]` forecasts). This is the enforced surface, and it is the denominator I used — not "names required in any of the 11 schemas". |
| `grep -n "class SchemaSet" -A 80 systems/systems_check.py` | full `Draft202012Validator` with a cross-file `referencing.Registry`; `validate()` evolves the validator onto the `$defs` member so internal `$ref`s resolve. So `required` inside nested/`$ref`'d subschemas **is** live, and my recursive enumeration must follow `$ref`/`allOf`/`anyOf`/`oneOf`/`then`/`else` — it does. |
| `git status --porcelain` | 0 lines — **this materially updates W09h's caveat**, see R.4. |

**Not replayed, not re-litigated.** I graded no claim's truth anywhere. W09g's four defective clauses, W09f's ten, W09h's four-way consumption census and its prose ranking: taken as given, none re-graded, none re-measured. W25 not read. No external route, denied or otherwise, was touched (no network used). I did not verify W09h's "92" as a claim about *its own* denominator — I built my own from source, as dispatched, and the two are not the same quantity (see Limitations).

---

## Method and inputs

| input | role |
|---|---|
| `/home/user/Rare-cancers` @ `1c9d8278` → `604984d8` (`systems/` byte-identical across the move) | tree under test, read-only throughout |
| `systems/schema/` — 11 schema files, of which **10 entrypoints** are reached by `check_schemas` | source of the enforced `required` set |
| `systems/graph/` — the 10 validated collections, each a bare JSON list (14/83/21/217·/18/16/32/33/28/28 records) | the population mutated |
| `systems/views/` — 111 generated files | the diff target; **the committed live copy is the baseline**, never a copy of a copy |
| `systems/systems_check.py` | the program executed |
| `/tmp/claude-0/w09i/copy/` | scratch copy, `tar --exclude=./.git --exclude=./results`; the only place anything was written |

Python 3.11 (`sys.executable`), stdlib + the repo's own `jsonschema`/`referencing`. Procedure:

1. **Enumerate the enforced required set (`reqenum.py`).** For each of the 10 (collection, schema-entrypoint) pairs actually named in `check_schemas`, recursively walk the entry subschema — following `$ref` across files via `$id` and filename, plus `allOf`/`anyOf`/`oneOf`/`then`/`else`, `properties`, `patternProperties`, `items`, object-valued `additionalProperties` — collecting every `required` member with its JSON-pointer path. Cycle-guarded.
2. **Restrict to reality.** For each (collection, name), count actual occurrences at any depth in that collection's graph file. Zero occurrences → `NOT-PRESENT`, not tested (deleting an absent field is a no-op).
3. **Mutate exhaustively (`blast2.py`).** For every remaining pair: recursively delete that key from every record in the collection, write the file, run `python3 systems/systems_check.py --write-views` (real exit code, real stdout), then `diff -rq` the regenerated `systems/views/` against the **committed live** `systems/views/`, then run plain mode and count `ERROR [S…]` lines naming that field.
4. **Restore between every mutation:** the pristine bytes of all 10 graph files are held in memory before the first mutation and rewritten verbatim after each one. A **no-edit control** ran first and a **final restore + regeneration** ran last; both gave `write_exit=0 diff_exit=0 diff_lines=0`, i.e. the copy reproduces the committed views exactly at both ends.
5. **Crash typing (`crashtype.py`).** Every pair with a non-zero `--write-views` exit was re-run and its final output line classified.
6. **Spot re-verification** of four `INVISIBLE` pairs with a full `diff -r` (not `-q`) and captured stdout.

**Sampling rule, stated explicitly: there is none — this is a census.** Every (collection, required-name) pair that occurs at least once in `systems/graph/` was mutated and measured: **148 of 148**. This was affordable because `--write-views` runs in 0.23 s. The only untested pairs are the 21 that do not occur in any record, and I do not count those as tested.

---

## Result

### R.1 — The enforced required set `PRIMARY`

| quantity | n |
|---|---|
| collections `check_schemas` validates | **10** |
| schema entrypoints reached (9 files; `technology.schema.json` supplies two) | 10 |
| (collection, path, required-name) triples reachable | 184 |
| **(collection, required-name) pairs** | **169** |
| **distinct required names across the enforced surface** | **106** |
| pairs present in ≥1 record → **tested** | **148** |
| pairs never instantiated → untested | 21 |
| names never instantiated in any collection | 15 |
| total required field instances actually deleted across the census | **9,005** |

⚠ **This 106 is not W09h's 92 and they are not the same quantity.** W09h counted names required in ≥1 of **all 11** schemas *and* present in the graph — which folds in `document.schema.json` (Markdown frontmatter, not `systems/graph/`) and does not distinguish which collection enforces which name. Mine counts names required anywhere reachable **from the 10 entrypoints `check_schemas` actually validates**, keyed by collection. I verified 106 from source as dispatched and did not inherit 92. Neither figure is wrong for its own denominator; the collection-keyed pair is the unit a blast-radius measurement needs, because 12 names have **different verdicts in different collections** (R.3).

### R.2 — ⭐ The split `PRIMARY`

All 148 tested pairs, exhaustive.

| verdict | pairs | % of 148 | distinct names | required field instances deleted | `--write-views` exit | views vs committed baseline |
|---|---|---|---|---|---|---|
| **INVISIBLE** | **40** | **27.0%** | 24 | **1,547** | **0**, `wrote 111 view(s)` | **byte-identical** |
| VIEW-CHANGED | 35 | 23.6% | 32 | 2,679 | **0** | differ |
| **CRASH (`KeyError`, not a check)** | **73** | **49.3%** | 51 | 4,779 | 1 | n/a — write aborted |
| untested (never instantiated) | 21 | — | 15 | 0 | — | — |

⭐ **`--write-views` contains no check at all.** All 73 non-zero exits are an uncaught `KeyError` raised while the generator subscripts the record (`crashtype.py`: 73/73, e.g. `strategies/confidence: KeyError: 'confidence'`). Not one of the 148 pairs produced a validation message from `--write-views`. Whether a missing required field is caught therefore depends entirely on whether the generator happens to write `row["x"]` rather than `row.get("x")` — an accident of subscript style, exactly as W09h inferred from one case, now measured across all 73.

**The `INVISIBLE` verdict is a measured zero, not a broken harness.** The same harness produced 35 differing-view results and 73 crashes, and the no-edit control and final restore both diffed clean. Four `INVISIBLE` pairs were re-run with a full `diff -r` and captured stdout:

```
technologies/paper_id:                exit=0 stdout='systems_check: wrote 111 view(s) to systems/views/' full_diff_exit=0 difflines=0
publications/outcome_potential_why:   exit=0 stdout='systems_check: wrote 111 view(s) to systems/views/' full_diff_exit=0 difflines=0
modalities/kind:                      exit=0 stdout='systems_check: wrote 111 view(s) to systems/views/' full_diff_exit=0 difflines=0
requirements/title:                   exit=0 stdout='systems_check: wrote 111 view(s) to systems/views/' full_diff_exit=0 difflines=0
```

**And plain mode catches every one of them: 40/40 `INVISIBLE` pairs raised at least one `ERROR [S…]` naming the deleted field, one per affected record.** The two modes are cleanly disjoint on this set: 1,547 required field instances can vanish with `--write-views` reporting success, and plain mode reports all 1,547.

### R.3 — The 40 invisible pairs `PRIMARY`

`plain_S_errors` = `ERROR [S1|S2|S3]` lines naming that field in plain mode; `new_errors` = total errors above the 181-error baseline.

| collection | required name | occurrences deleted | plain_S_errors | new_errors |
|---|---|---|---|---|
| modalities | `kind` | 217 | 217 | 217 |
| modalities | `level` | 217 | 217 | 217 |
| technologies | `paper_id` | 302 | 302 | 302 |
| routes | `kind` / `level` / `provenance` / `title` | 83 each | 83 each | 83 each |
| publications | `kind` / `level` / **`outcome_potential_why`** | 33 each | 33 each | 33 each |
| instruments | `closure_kind` / `file` / `module` / `owner` | 32 each | 32 each | 32 each |
| lanes | `file` / `owner` | 18 each | 18 each | 18 each |
| requirements | `confidence` / `file` / `last_verified` / `owner` / `provenance` / `status` / `title` | 16 each | 16 each | 16 each |
| strategies | `file` / `kind` / `last_verified` / `level` / `owner` / `provenance` | 14 each | 14 each | 14 each |
| modalities | `revisit_trigger` | 9 | 9 | 9 |
| strategies | `running_job` | 2 | 2 | 2 |
| blockers | `changed_on` / `was` / `why` | 1 each | 1 each | 1 each |
| publications | `_evidence` / `doi` / `posted` / `posted_by` / `published_at_utc` / `venue` | 1 each | 1 each | 1 each |

**Fifteen names are invisible in every collection where they occur:** `_evidence`, `changed_on`, `closure_kind`, `doi`, `level`, `module`, `outcome_potential_why`, `paper_id`, `posted`, `posted_by`, `provenance`, `published_at_utc`, `running_job`, `venue`, `was`.

**Twelve names get different verdicts in different collections** — `confidence`, `file`, `kind`, `last_verified`, `owner`, `purpose`, `revisit_trigger`, `state`, `status`, `title`, `why`, `work_state`. `routes/title` is invisible while `lanes/title` crashes; `routes/confidence` changes a view while `requirements/confidence` is invisible. **This is why a name-level census cannot answer this question and a collection-keyed one can.**

### R.4 — Reproduction and extension of W09h's single case `PRIMARY`

W09h's finding reproduces exactly: `publications/outcome_potential_why`, 33 deletions → `--write-views` exit 0, `wrote 111 view(s)`, `diff -r` exit 0, 0 lines; plain mode 33 `[S3]` errors. **It generalises to 23 more names and 39 more pairs**, and the two largest are far bigger than it: `technologies/paper_id` (302 instances) and `modalities/kind` / `modalities/level` (217 each). By instance count `outcome_potential_why` is the **7th** largest hole, not the first. It remains the most *interesting* one because it carries free prose (W09h, R.3) — but on the axis this unit measures, it is a small member of a class that reaches 1,547 instances.

### R.5 — The `[D4]` interaction, measured — and W09h's caveat needs updating `PRIMARY`

W09h reported the plain-mode baseline as exit 1 with **143 `[D4]`** errors from this campaign's **untracked** report files. Measured now on the scratch copy of `1c9d8278`:

| baseline (unmodified scratch copy) | value |
|---|---|
| `--write-views` exit / views diff | **0** / **0** (byte-identical to committed) |
| plain-mode exit | **1** |
| plain-mode total `ERROR` lines | **181** |
| `ERROR [D4]` | **166**, and **166/166 are under `research/autonomy/opus-capacity-campaign-20260908/`** |
| `ERROR [K1]` 8, `[D1]` 3, `[D11]` 3, `[D6]` 1 | `[D1]`/`[D11]`/`[D6]` and 6 `[K1]` are also campaign-directory files; **2 `[K1]` are an artefact of my `--exclude=./results` copy** and are not a property of the tree |

⚠ **The correction that matters: `git status --porcelain` is now 0 lines. The campaign reports are committed.** The 166 `[D4]` errors are therefore **not** an untracked-file artefact any more — they are a *committed-tree* plain-mode failure at HEAD. This strengthens the tradeoff W09h handed to the graph owner rather than softening it: wiring `check_schemas` into `--write-views` today would make regeneration fail on the committed tree, for 179 reasons that have nothing to do with the graph.

**It did not confound my measurement, and here is why.** `--write-views` runs no document checks at all, so its exit code is untouched by `[D4]` — every one of my 148 `--write-views` exits is a clean 0-or-`KeyError` signal. For plain mode I never used the exit code (it is 1 at baseline); I used the **delta above the 181-error baseline** and a **field-name-matched `ERROR [S…]` count**, both of which are `[D4]`-independent. The `[D4]` mass affects only the *readability* of a plain-mode run, not any number in R.2 or R.3.

---

## Validation evidence

**RUN** — all under `/tmp/claude-0/w09i/`, cwd `/tmp/claude-0/w09i/copy`, Python 3.11, Linux, no network, no writes to the repository:

| # | command | exit |
|---|---|---|
| 1 | `tar --exclude=./.git --exclude=./results -cf - . \| tar -xf - -C /tmp/claude-0/w09i/copy` | 0 (428 MB) |
| 2 | `python3 systems/systems_check.py --write-views` (control) | **0**, `wrote 111 view(s)`, 0.228 s |
| 3 | `diff -r /home/user/Rare-cancers/systems/views …/copy/systems/views` (control) | **0** |
| 4 | `python3 systems/systems_check.py` (plain baseline) | **1**, 406 output lines, 181 errors |
| 5 | `python3 /tmp/claude-0/w09i/reqenum.py` (schema enumeration) | 0 |
| 6 | `python3 /tmp/claude-0/w09i/blast2.py` (**148 mutations × 2 runs each + control + final restore**) | 0 |
| 7 | `python3 /tmp/claude-0/w09i/crashtype.py` (73 crash re-runs, typed) | 0 |
| 8 | four-pair full-`diff -r` spot re-verification | 0 |
| 9 | `git diff --stat 1c9d8278 604984d8 -- systems/` | 0, **empty output** |
| 10 | `rm -rf /tmp/claude-0/w09i` | 0 |

Verbatim key output:

```
CONTROL write_exit=0 diff_exit=0 diff_lines=0
CONTROL plain_exit=1 errors=181
publications  outcome_potential_why      occ=  33 rm=  33 w_exit=0 diff=0/   0 plain=1 S_err= 33 newerr=  33 -> INVISIBLE
technologies  paper_id                   occ= 302 rm= 302 w_exit=0 diff=0/   0 plain=1 S_err=302 newerr= 302 -> INVISIBLE
strategies    confidence                 occ=  14 rm=  14 w_exit=1 diff=0/   0 plain=1 S_err=  0 newerr=-181 -> CRASH
routes        state                      occ=  83 rm=  83 w_exit=0 diff=1/  98 plain=1 S_err= 83 newerr=  83 -> VIEW-CHANGED
FINAL-RESTORE write_exit=0 diff_exit=0 diff_lines=0
```

```
  73  KeyError   e.g. strategies/confidence: KeyError: 'confidence'
FINAL restore: write_exit 0 diff_exit 0 difflines 0
```

Restoration is verified twice over: the final restore regenerated the committed views byte-for-byte, and the live tree ended `git status --porcelain` = 0 lines.

**PROPOSED (NOT RUN):** any change to `systems_check.py` or any graph file; any patch, diff or validator (**none authored, none proposed** — the mode-wiring decision is the graph owner's); `scripts/preflight.sh`; any plain-mode or `--write-views` run against the live tree; the 21 never-instantiated required pairs; `research/modalities/atr_hrd_sarcoma_series.py`.

---

## Limitations

- **Deletion is recursive by name within the collection.** Deleting `file` from `routes` removed 211 instances although only 83 are top-level — nested occurrences of the same name go too. This *widens* the mutation, so an `INVISIBLE` verdict is if anything conservative (more was removed and still nothing changed); but for a `VIEW-CHANGED` verdict I cannot attribute the change to the top-level occurrence specifically. Affects 8 pairs where occurrences exceed record count.
- **Whole-field deletion, not sentinel substitution.** W09h's sentinel method answers "does the value render"; mine answers "does absence get noticed". They are different questions and I ran only mine. A field whose *value* is unread but whose *presence* is required would appear here only as `INVISIBLE`.
- **`CRASH` is not "caught".** A `KeyError` traceback does stop a bad write, so in a narrow operational sense 73 pairs are protected — by luck, with no message naming the schema, and with `systems/views/` left in whatever partial state the crash produced. I did not measure partial-write damage.
- **The enforced set is what `check_schemas` reaches.** Names required by `document.schema.json` and any schema not in the 10 entrypoints are outside this census by construction — they govern Markdown frontmatter, not `systems/graph/`.
- **21 pairs / 15 names untested**, because they occur in no record (mostly required inside optional sub-objects — `resolution`, `per_tech`, `expected_value` — plus `strategies/routes`, `strategies/why`, `routes/uncertainty`). Their behaviour under `--write-views` is **UNKNOWN**, not zero.
- `results/` was excluded from the scratch copy. The control proves the 111 views do not depend on it; it accounts for exactly 2 of the 181 baseline `[K1]` errors and nothing else I report.
- Measured at `1c9d8278`/`604984d8` only; `systems/` is identical at both. Nothing here bears on EMC efficacy, safety, selectivity or clinical readiness; no patient data, no wet lab, no clinical claim, no truth-grading of any repository claim. No content-policy refusal occurred.

## Stop condition

**Set up front:** stop when every required name `check_schemas` enforces is enumerated from source with its owning collection, and every such name that occurs in a record has been deleted, regenerated and diffed with real exit codes, the scratch copy verifiably restored — or at ~40 tool calls / ~40 minutes, whichever first.

**MET, and exhaustively rather than by sample.** 106 names / 169 pairs enumerated; 148/148 instantiated pairs mutated and measured; 0 sampled, 0 skipped among instantiated pairs; control and final restore both clean; scratch deleted. Returned on meeting it.

## Tool-call and wall-clock count actually used

**20 tool calls** (19 `Bash`, 1 `ToolSearch`), no repository write, no git write, no network. **Wall clock 03:38Z → 03:52:40Z ≈ 15 minutes.** Budget was ~40 calls / ~40 min.

## Next concrete action

**For the graph owner, unchanged in substance from W09h but now with the real denominator to weigh it against:** decide whether `--write-views` should run `check_schemas` before writing. The number that should drive the decision is no longer "one field": **40 (collection, required-name) pairs covering 24 names and 1,547 required field instances can be deleted outright and `--write-views` still prints `wrote 111 view(s)` and exits 0 with byte-identical output**, while 73 more are caught only by an uncaught `KeyError` whose message never mentions a schema. The counter-weight is now heavier too and should be stated plainly to whoever decides: at HEAD the tree is **clean**, yet plain mode exits 1 with **179 committed-tree errors from the campaign directory itself** (166 `[D4]` + `[D1]`/`[D11]`/`[D6]`/`[K1]`), so wiring the checks in today would break regeneration for reasons unrelated to the graph. **The prerequisite is therefore the campaign directory's frontmatter, not the mode wiring** — and a successor could measure exactly that: how many of the 179 are fixable by adding frontmatter to campaign reports, and whether `check_schemas` alone (rather than all invariants) could be wired into `--write-views` without inheriting the `[D…]` document checks at all. I have written no patch and propose none.
