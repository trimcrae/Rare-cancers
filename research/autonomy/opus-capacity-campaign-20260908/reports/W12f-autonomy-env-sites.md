<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:18:29Z UTC
     agent id a49f2d00da7ab12a6 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a49f2d00da7ab12a6.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

## Worker

**W12f**, lane 12 refill, OPUS-CAPACITY-CAMPAIGN-20260908. Succeeding W12e; closing the two UNKNOWNs it named, not reopening its settled result.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at **start**: `Tue Sep  8 03:10:50 UTC 2026`. `date -u` at **end**: `Tue Sep  8 03:13:21 UTC 2026` (plus report drafting; final wall-clock in the count section).

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (verbatim, except that the five pure host-list lines `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` are elided for length — they carry no model name):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
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
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**HEAD and tree state — HEAD did not move during my run.**
- `git rev-parse HEAD` at start: `98a0833f1ede2cf9cef13790388260567a32e868`. At end: **identical**. `git diff --name-only 98a0833..HEAD` → empty. This is **not** the `92abbcb905…` frozen commit named in COMMON-BRIEF.md, and **not** W12e's `ce743d6…`/`a87275c…`; the coordinator has continued committing collected reports. No file I read changed under me.
- `git status --porcelain` at start: **8 lines**, all `?? research/autonomy/opus-capacity-campaign-20260908/reports/W*.md` (`W01g`, `W02f`, `W04e`, `W06f`, `W07f`, `W09f`, `W12e`, `W20g`) — the coordinator's uncommitted collected reports, none mine. At end: **byte-identical, same 8 lines**.
- I wrote **nothing** into `/home/user/Rare-cancers`. All execution and scratch is under `/tmp/claude-0/w12f/`. Verified: `find research/{modalities,manuscripts} scripts -path '*__pycache__*' -newermt '2026-09-08 03:10:50'` → **empty**; the three `__pycache__` directories present have mtimes `02:27:15`, `03:01:31`, `02:34:58`, all **before** my start (the `03:01:31` one is W12e's). No git write of any kind. `scripts/preflight.sh` was **not** run. No module `--check` was run.

---

## Question

Two questions, both named as UNKNOWN by W12e and neither reopening its settled `0 of 106`:

1. **What are the `env=` sites under `research/autonomy`?** W12e's dispatch scope was `research/manuscripts`, `research/modalities`, `scripts`, `systems`; it recorded *"`research/autonomy` holds a further 10 `env=` grep lines that I did not classify … UNKNOWN"* (W12e Limitations, line 300). `research/autonomy` is the loop's own machinery — `claim.py` and the ledger tests — and part of it runs inside `scripts/preflight.sh`, so an unclassified REPLACES site there would matter more than one in a launcher.
2. **What exactly are the 21 `JobSpec(env={...})` sites affected by, and not affected by?** W12e's one-sentence carve-out (*"they do lose the variable — but they are consumed on rented remote hosts"*) is correct in outcome but loose in mechanism, and it is exactly the sentence a later reader could misread as "there are 21 broken env dicts W12d's fix does not cover."

---

## Prior-work check

Commands run, verbatim, in `/home/user/Rare-cancers`:

```
grep -rn "env=" research/autonomy --include=*.py | wc -l           -> 10
grep -rn "env=" research/autonomy --binary-files=without-match | wc -l -> 45
git ls-files | grep -i full_preflight_runtime                       -> (no output, rc 1)
grep -rn "verify_and_integrate" --exclude-dir=.git .                -> 2 hits, both JSON replay records
grep -rn --include=*.py "env=spec\.env|env=self\.spec\.env|env=job\.env" research scripts systems -> rc 1, no hits
```

Read in full: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, and W12e (`W12e-subprocess-env-residual.md`, 32.5 KB, read via the campaign reports directory), plus the referenced sections of W12/W12b/W12c/W12d through the `env=`-bearing lines in their report files.

**Nothing in `CLOSED-WORK.md` covers this.** The 45-line all-file-types grep reconciles as: **35 lines inside the campaign's own `reports/*.md`** (prose in W12, W12b, W12d, W12e discussing `env=`) and **10 lines in `.py` files**. So the only prior work on `research/autonomy` `env=` sites is W12e's explicit refusal to classify them. I am not replaying W12d's 18-row sweep, not authoring a patch or test, and not touching `.github/workflows` — all three excluded by dispatch and all three declined.

---

## Method / inputs

- Live checkout `/home/user/Rare-cancers` at `98a0833f1ede2cf9cef13790388260567a32e868` (unmoved). `Python 3.11.15`, Linux `6.18.44-fc-v24`. The frozen corpus at `/tmp/claude-0/frozen-corpus/` was **not** needed and **not** read: every file in question is present in the live checkout and no novelty or absence claim here depends on prior work.
- **Independent re-implementation of W12e's method**, not a reuse of its script. `/tmp/claude-0/w12f/classify.py` (authored fresh, 60 lines) walks every `.py` under a given subtree, finds every `ast.Call` carrying a `keyword.arg == 'env'`, `ast.unparse`s the value, and — when the value is a bare `ast.Name` — resolves that name in the enclosing function and module scopes, collecting `Assign`, `AugAssign`, function **parameters**, `.update()`/`.setdefault()`/`.pop()` **mutations**, and `env[k] = …` / `del env[k]` **item-sets**, each with its line number. Mutation and item-set tracking is an addition beyond W12e's described resolver, aimed precisely at the "a `del env['PYTHONUTF8']` between construction and use would be invisible" limitation W12e recorded.
- Every command ran as `env -i PATH=/usr/local/bin:/usr/bin:/bin HOME=/tmp/claude-0/w12f PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/w12f/pycache python3 …`, so no `.pyc` could land in the tree and no interpreter state leaked.
- Every site the AST could not settle was then read individually in source, together with the helper definition or the origin module it references.
- Files read in source: `research/autonomy/claim.py` (lines 225-272), `research/autonomy/cycle-outcomes/20260905T032612Z-df96afc413/verify_and_integrate.py` (1-30), the six `research/autonomy/tests/test_*.py` sites, `research/modalities/gpu_backend.py` (`JobSpec` at :277-286, `_vast_onstart` at :1239-1284, all eight `Backend.submit` bodies), the four `research/modalities/tests/` JobSpec contexts, and `scripts/preflight.sh` (gate block :847-864, autonomy invocations :929/:1376/:1484/:1536, modalities tier :1078-1090, tier guard :1325-1335 and :1360-1376).
- **Cross-check on the shared method.** Running my classifier over W12e's four directories reproduced its headline numbers exactly and independently: **147** `env=` kwarg call sites, callee histogram `subprocess.run 86`, `subprocess.Popen 3`, wrappers `_publish 10 / _sh 3 / sh 2 / _run 2 = 17`, `JobSpec 19 + gb.JobSpec 2 = 21`, data-dict callees `14`, `_agg 6`. This is a genuine reproduction from a separately written script, not a restatement.

---

## Result

### Part 1 — the `research/autonomy` population, classified

**Reconciling the grep count first.** `grep -rn "env=" research/autonomy --include=*.py` → **10 lines**. The AST finds **9** `env=` keyword arguments on real call expressions. The tenth line is `verify_and_integrate.py:10`, `_,env=environment()` — a **tuple-unpacking assignment**, not a keyword argument. 10 = 9 + 1, fully reconciled, no residual.

**Per-site verdicts. All rows PRIMARY (read from committed source at `98a0833`).**

| # | `env=` site (file:line) | callee | starts a local OS process? | what the child is | construction line that justifies the verdict | verdict |
|---|---|---|---|---|---|---|
| 1 | `research/autonomy/claim.py:231` | `subprocess.run` | **yes** | `git` | in-line at `:232`: `env={**os.environ, **self.C_LOCALE}`; `C_LOCALE = {"LC_ALL":"C","LANG":"C","LANGUAGE":""}` at `:228` | **INHERITS** (overlay; overrides 3 named keys only) |
| 2 | `research/autonomy/claim.py:267` | `subprocess.run` | **yes** | `git hash-object -w --path … --stdin` | in-line at `:269`: `env={**os.environ, **self.C_LOCALE}` | **INHERITS** (same overlay) |
| 3 | `research/autonomy/cycle-outcomes/20260905T032612Z-df96afc413/verify_and_integrate.py:23` | `subprocess.run` | **yes** (if it could run) | `sys.executable -X utf8 …` | `env` comes from `:10` `_,env = environment()`, imported at `:8` from `full_preflight_runtime`, **which does not exist in this repository** | **UNDETERMINED** — see the note below |
| 4 | `tests/test_amendment_guard_sees_untracked_governed_files.py:36` | `subprocess.run` | **yes** | `git` (helper `_run(cmd, cwd)`) | `:31` `e = dict(os.environ)` then `:32-35` four `e.setdefault("GIT_*", …)` | **INHERITS** |
| 5 | `tests/test_ids_cannot_collide.py:435` | `subprocess.Popen` | **yes** | **`sys.executable -c src`** — a real Python child | `:434` `env = dict(os.environ, CLAUDE_CODE_SESSION_ID=SESSION_A, CLAUDE_CODE_CHILD_SESSION="1")` | **INHERITS** |
| 6 | `tests/test_out_of_ideas_a_replan_is_not_an_improvement.py:52` | `subprocess.run` | **yes** | `["git","-C",repo,…]` | `:44` `env = dict(os.environ)`; `:47` `env['GIT_AUTHOR_DATE']=env['GIT_COMMITTER_DATE']=stamp`; `:48-51` four `setdefault` | **INHERITS** |
| 7 | `tests/test_stalls_are_named_reaches_the_board.py:184` | `subprocess.run` | **yes** | `["git","-C",repo,…]` | `:176` `env = dict(os.environ)`; `:179` item-set; `:180-183` four `setdefault` | **INHERITS** |
| 8 | `tests/test_stuck_clock_a_retry_is_not_an_advance.py:75` | `subprocess.run` | **yes** | `["git","-C",repo,…]` | `:67` `env = dict(os.environ)`; `:70` item-set; `:71-74` four `setdefault` | **INHERITS** |
| 9 | `tests/test_the_ledger_history_is_read_in_one_git_process.py:51` | `subprocess.run` | **yes** | `["git","-C",repo,…]` | `:43` `env = dict(os.environ)`; `:46` item-set; `:47-50` four `setdefault` | **INHERITS** |

**Totals for `research/autonomy`: 9 call sites, 9 of them local-OS-process spawns, 0 data dicts, 0 remote JobSpecs. INHERITS 8. REPLACES 0. UNDETERMINED 1.**

Not one mutation in the whole population removes a key. Across all 9 sites the mutation set is: four `setdefault("GIT_*")` per git-fixture helper, one `env['GIT_AUTHOR_DATE']=env['GIT_COMMITTER_DATE']=stamp` item-set per ledger fixture, and the two literal `C_LOCALE` overlays. **There is no `pop`, no `del`, and no re-binding anywhere between construction and use** — the exact hole W12e flagged as a limitation, checked mechanically here and found empty in this subtree.

**The one UNDETERMINED, stated honestly rather than rounded to INHERITS.** `verify_and_integrate.py:23` takes its environment from `environment()` in a module `full_preflight_runtime` that is **not in the tree** (`git ls-files | grep full_preflight_runtime` → nothing; the only two textual references are `research/autonomy/codex-handover.json` and the file itself). Its construction is therefore unreadable and I will not guess it. Three facts bound the risk to zero in practice: the file hard-codes `root = Path('C:/Projects/EMC-Research')` — a Windows path that does not exist in this container; it is an archived `cycle-outcomes/` replay artifact, referenced only as a hashed record in `follow-through-2026-09-05/preservation-replay.json` and `coordinator-replay.json`; and it is neither named in `scripts/preflight.sh` nor collectible by pytest (the pure-logic tier runs `research/autonomy/tests`, not `cycle-outcomes/`, and the file is not `test_*.py`). It is **dead archived code that cannot execute here**, but its verdict is UNDETERMINED, not INHERITS.

### The loud-or-plain finding, stated plainly

**No REPLACES site was found under `research/autonomy`, so no REPLACES site reaches a preflight gate row. The count is zero. This is a negative result and I am reporting it as one — there is nothing to say loudly.**

For completeness on reachability, since the zero would only be interesting if these sites were reachable at all: they **are**. `scripts/preflight.sh:1376` runs `$PYTEST $PYTEST_PAR scripts/tests research/autonomy/tests $SYSTEMS_TESTS -q …`, so sites 4-9 execute inside preflight's pure-logic tier — a conditional tier (skipped when `PREFLIGHT_PAPER` is set, per `:1369-1372`), not one of the 18 `--check` rows at `:847-864`. Preflight also invokes three other `research/autonomy` modules directly — `receipt_schema.py --check` (`:929`), `contract_check.py --check` (`:1484`), `derived_ids.py --check` (`:1536`) — and **none of those three contains an `env=` site at all**. So the sites are genuinely inside the gate's blast radius and they still classify 8/8 INHERITS. The zero is a measured zero over a reachable population, not a zero obtained by the population being out of reach.

One site is worth naming because it is the only one of its kind: **`test_ids_cannot_collide.py:435` is the single `env=` call site under `research/autonomy` whose child is a Python interpreter** (`subprocess.Popen([sys.executable, "-c", src], env=env, …)`, two concurrent seats). It is precisely the shape that would break under a replaced environment — and it is built `dict(os.environ, …)`, so it inherits `PYTHONUTF8` from a fixed parent. The other eight children are `git`, which is not a Python process and is unaffected by `PYTHONUTF8` in either direction.

**Consequence for W12e's headline: none.** W12e's `0 of 106` covered its four directories. Adding `research/autonomy` extends the local-spawn census to **115 sites, 114 INHERITS, 0 REPLACES, 1 UNDETERMINED (dead, unreachable, Windows-pathed archive)**. W12d's one-line `export PYTHONUTF8=1` remains sufficient, and this adds no new requirement to it.

### Part 2 — the 21 `JobSpec(env={...})` sites, precisely

**PRIMARY.** 21 sites in **14 files**: 15 sites in 10 launcher modules, 6 sites in 4 test modules.

| group | n sites | n files | files:lines |
|---|---|---|---|
| Vast launchers | **15** | 10 | `abfe_sel_vast_launch.py:285`; `congeneric_fanout_vast.py:355`; `nr4a3_bioemu_vast_launch.py:143`; `nr4a_paralogue_md_vast_launch.py:107`; `nrv04_vast_launch.py:800,1095,1332,1537,1652`; `protfep_vast_launch.py:298`; `selcal_vast_launch.py:371,403`; `step1_liveness_smoke.py:178`; `ternary_vast_launch.py:1312`; `vast_bench_sweep.py:550` |
| tests | **6** | 4 | `tests/test_gpu_backend.py:275,301,313`; `tests/test_s3_scoped_policy.py:98`; `tests/test_vast_account_rental_hold.py:73`; `tests/test_vast_start_refusal.py:59` |

All 21 are in `research/modalities`. All 15 launcher `env` values resolve to hand-built dict literals of lane configuration — `{'GIT_BRANCH':…, 'RESULT_S3':…, 'UNIT_ID':…, 'SEED':…}` and similar — with no `os.environ` spread anywhere in the chain. Four are the direct-literal form (`selcal:403`, `step1_liveness_smoke:178`, plus the test dicts); eleven are a bare `Name` resolving to such a literal, sometimes via a `leg_env(...)` helper plus `.update({...})`.

**What they are affected by, and what they are not. The mechanism, from source.**

`JobSpec.env` is a **dataclass field** (`gpu_backend.py:286`, `env: dict = field(default_factory=dict)`). It is **never passed to a local subprocess anywhere in the repository** — `grep -rn --include=*.py "env=spec\.env|env=self\.spec\.env|env=job\.env" research scripts systems` returns **rc 1, no hits**. Its only consumers in `gpu_backend.py` are two:

- `_vast_onstart()` at `:1279-1284`:
  ```
  env = {**(extra_env or {}), **spec.env}
  ...
  lines += [f"export {k}={shlex.quote(str(v))}" for k, v in env.items()]
  ```
- `:1381`, a read of `(spec.env or {}).get("RESULT_S3")` for checkpoint-target bookkeeping.

**This is the precision that matters, and it is a stronger statement than "they lose the variable": `spec.env` is never an environment at all — it is an ADDITIVE list of `export` lines appended to a shell script that runs on a rented host.** It replaces nothing. The job command on that host inherits the container image's own environment and receives these exports on top. `PYTHONUTF8` is absent in that shell not because a dict displaced it, but because nothing on the remote host ever set it. Calling these sites "environment-replacing" would be a category error; W12e's `REPLACES` classification is about `env=` on `subprocess.run`/`Popen`, and none of these 21 is that.

Counts, so nobody later mistakes a remote-host export gap for a defect in W12d's fix:

| statement | count |
|---|---|
| JobSpec `env=` sites total | **21** |
| …that pass a dict to a local `subprocess.run`/`Popen`/`exec*` | **0** |
| …that are among `scripts/preflight.sh`'s 18 `--check` rows at `:847-864` | **0** |
| …in files reachable by any preflight tier | **6** (the 4 test files, via the modalities pytest tier at `:1086`) |
| …of those 6 that spawn any OS process | **0** — three feed the pure string builder `_vast_onstart` and assert on its text (`test_gpu_backend.py:277`, `test_s3_scoped_policy.py:97`); three feed a `submit()` whose Vast API client is monkeypatched to raise or scripted (`test_vast_account_rental_hold.py:68-73`, `test_vast_start_refusal.py:54-59`) |
| …that could be reached by an exported variable in `scripts/preflight.sh` on a developer box | **0** — the export sets the *parent's* environment; these dicts are literals that were never going to read it, and their destination is another machine |
| non-Vast backends that consume `spec.env` at all | **0 of 7** — `SageMaker`, `Slurm`, `RunPod`, `Salad`, `GCP`, `Modal` all `raise NotImplementedError` in `submit()`; `MockBackend.submit` (`:1723`) ignores `spec.env` entirely and returns a `Handle` |

**Therefore:** the 21 JobSpec sites are affected by **nothing W12d proposed and nothing W12d omitted**. They would be affected only by a change to the `export` block in `_vast_onstart` at `gpu_backend.py:1279-1284`, or by the remote container image. That is a different file, a different machine, and — under CLAUDE.md §3 and the `gpu-compute` posture — a change with GPU-spend implications that lane 12 has neither the authority nor the reason to make. It is **not a residual of W12d's one-line fix**.

A confirming detail from the tree's own idiom, since it makes the boundary concrete: `ternary_vast_launch.py:1218` already ships `'PYTHONUNBUFFERED': '1'` inside its JobSpec `env` literal. The repository already knows how to hand a Python knob to a remote job — through the JobSpec dict, deliberately, per lane. If anyone ever wants UTF-8 mode on a rented host, that is the existing mechanism, one key per launcher or one line in `_vast_onstart`; it has nothing to do with `scripts/preflight.sh`.

---

## Validation evidence

**RUN** — all in `/tmp/claude-0/w12f/`, all with `env -i PATH=/usr/local/bin:/usr/bin:/bin HOME=/tmp/claude-0/w12f PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/w12f/pycache`, Python 3.11.15, Linux 6.18.44-fc-v24, repo at `98a0833`:

1. `grep -rn "env=" research/autonomy --include=*.py | wc -l` → **10**, rc 0.
2. `grep -rn "env=" research/autonomy --binary-files=without-match | wc -l` → **45**, rc 0; the 35 non-`.py` lines are all in `opus-capacity-campaign-20260908/reports/*.md`, listed and inspected.
3. `python3 /tmp/claude-0/w12f/classify.py /home/user/Rare-cancers research/autonomy` → **rc 0**, 9 records, written to `/tmp/claude-0/w12f/autonomy_sites.json`. Verbatim first record: `research/autonomy/claim.py 231 subprocess.run | {**os.environ, **self.C_LOCALE} | Dict | []`.
4. Same classifier over W12e's four directories → **rc 0**, `total env= kwarg call sites in four dirs: 147`; callee `Counter` verbatim: `[('subprocess.run', 86), ('JobSpec', 19), ('_publish', 10), ('tv.converge_mode_for_task', 7), ('_agg', 6), ('subprocess.Popen', 3), ('_sh', 3), ('sh', 2), ('_run', 2), ('gb.JobSpec', 2), ('cf.plan', 2), ('plan', 1), ('audit', 1), ('_fmr', 1), ('rsc.fingerprint_mismatch_reason', 1), ('csa.audit', 1)]`; `JobSpec sites: 21`. **Independently reproduces W12e's 147 and 21.**
5. `grep -rn --include=*.py "env=spec\.env\|env=self\.spec\.env\|env=job\.env" research scripts systems` → **rc 1, no output**.
6. `git ls-files | grep -i full_preflight_runtime` → **no output** (module absent from the tree).
7. Source reads (`sed -n`) of every site and helper cited in the two tables above, plus `gpu_backend.py:277-286`, `:1239-1284`, all eight `submit()` bodies, and `scripts/preflight.sh:847-864`, `:929`, `:1078-1090`, `:1325-1335`, `:1360-1376`, `:1484`, `:1536` — rc 0 throughout.
8. Tree-cleanliness: `find research/modalities/__pycache__ research/manuscripts/__pycache__ scripts/__pycache__ -newermt '2026-09-08 03:10:50'` → **empty**; `git status --porcelain` byte-identical at start and end; `git rev-parse HEAD` identical at start and end.

**PROPOSED (NOT RUN)** — deliberately not done, per dispatch: W12d's 18-row `--check` sweep (not re-run); `scripts/preflight.sh` (not run); any patch, guard test, or `.github/workflows` extension (not authored); any execution of a `research/autonomy` test or `--check` (not run — the pure-logic tier writes and I am read-only). **No child process was launched to measure environment transport in this run at all**; W12e already did that with real exit codes, and repeating it would have been padding. Every classification above is a static source reading, and I label it as such.

---

## Limitations

- **This is a static classification, not a runtime measurement.** I launched no child and produced no exit code of my own. The verdicts rest on reading construction sites, helper definitions and mutation sets in committed source. My classifier now tracks `.update`/`.setdefault`/`.pop` and item-set/`del` mutations by name in the enclosing scopes, which closes W12e's "invisible `del`" hole for this subtree — but only for mutations that name the variable directly. A dict passed to a helper that mutates it under a different parameter name would still be invisible. I searched for none and found none: **a negative search result, not a proof**.
- **The one UNDETERMINED is genuinely undetermined.** `verify_and_integrate.py:23` cannot be classified because its origin module is absent from the repository. I record it as UNDETERMINED rather than inferring a verdict from the archive's dead status.
- **"Reachable by preflight" is read from `scripts/preflight.sh`, not observed.** I did not run preflight, so the tier structure (which rows run under which guard) is a source reading. `research/autonomy/tests` runs in a conditional tier that `PREFLIGHT_PAPER` skips.
- **`spec.env` behaviour on a rented host is inferred from `_vast_onstart`'s source, not observed on a host.** No GPU was rented, no Vast API was contacted, no spend occurred. What happens to encoding inside a remote container image is **UNKNOWN** and outside anything I can measure here.
- **HEAD is `98a0833`, not the `92abbcb905…` frozen in COMMON-BRIEF.md.** My counts are valid at `98a0833`; the coordinator's collected-report commits do not touch any `.py` file I read, but I did not diff against `92abbcb`.
- **No scientific, biological or clinical claim is made or supported by anything in this report.** This is tooling. Nothing here bears on EMC efficacy, safety, selectivity or clinical readiness, and there is no wet lab.

---

## Stop condition

**Set up front, before the first classification call:** return the moment (a) every `env=` call site under `research/autonomy` carries a per-site INHERITS / REPLACES / UNDETERMINED verdict with the construction line that justifies it, separated by whether the callee starts a local OS process, and every grep line is reconciled to the AST count; and (b) the 21 JobSpec sites are enumerated with counts and a precise statement of what they would and would not be affected by, traced to the code that consumes `JobSpec.env`.

**MET, both halves.** (a) 10 grep lines → 9 AST kwargs + 1 tuple-unpack, fully reconciled; 9 verdicts, 8 INHERITS / 0 REPLACES / 1 UNDETERMINED, each with its construction line; all 9 callees are local-process spawns, 8 spawning `git` and 1 spawning a Python interpreter. (b) 21 sites enumerated in 14 files with the consumption mechanism read from `gpu_backend.py:1279-1284` and the local-subprocess grep returning zero hits. Returned immediately on meeting it; no additional work started.

---

## Tool-call and wall-clock count actually used

**16 tool calls**, all `Bash` (12 shell reads/greps/`sed`, 3 classifier runs including its heredoc authoring, 1 evidence capture). No `Read`, `Write`, `Edit`, `Artifact` or MCP call. Zero writes to `/home/user/Rare-cancers`; zero git write operations.

**Wall clock: 03:10:50Z → 03:13:21Z = 2 min 31 s** of execution, plus report drafting — well inside the ~40-call / ~40-minute target.

---

## Next concrete action

**One successor, and it is not more measurement: hand lane 12's thread to the `scripts/preflight.sh` owner exactly as W12e recommended, with this report appended as the closure of its two named UNKNOWNs, and close the lane.** The census is now complete over five directories — **115 local-spawn `env=` sites, 114 INHERITS, 0 REPLACES, 1 UNDETERMINED that is dead Windows-pathed archive code** — and the JobSpec carve-out is now stated as a mechanism (`spec.env` is an additive `export` block in a remote `onstart` script, consumed at `gpu_backend.py:1279-1284`, never a local process environment) rather than as an unexplained exception. **There is no measurement left in this lane that could change W12d's recommendation.**

Two things I explicitly do **not** recommend as next, with reasons:

- **Classifying `.github/workflows`** — excluded by my dispatch, declined by W12d and W12e for the same reason: 161 files of CI configuration, not a defect repair.
- **Resolving `verify_and_integrate.py`'s UNDETERMINED** — it would require reconstructing `full_preflight_runtime`, a module that is not in the repository, to classify a `C:/Projects/EMC-Research`-rooted archive that nothing runs. The correct disposition of that file is an archive question for its owner, not a portability finding. **Not started, not scoped.**
