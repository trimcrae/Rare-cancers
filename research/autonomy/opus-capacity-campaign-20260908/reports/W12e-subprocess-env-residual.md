<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:10:00Z UTC
     agent id a500b68b802b546ae ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a500b68b802b546ae.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

## Worker

**W12e**, lane 12 refill, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:57:37 UTC 2026`. `date -u` at end: `Tue Sep  8 03:03:19 UTC 2026` (plus report drafting).

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (verbatim; the five pure host-list lines `no_proxy`/`NO_PROXY`/`GLOBAL_AGENT_NO_PROXY`/`npm_config_noproxy`/`JAVA_TOOL_OPTIONS` are elided for length and carry no model name):

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

End-of-run re-read of the identity-bearing subset was **identical**: `AI_AGENT=claude-code_2-1-263_agent`, `CLAUDE_CODE_VERSION=2.1.42`, `CLAUDE_EFFORT=medium`, `CLAUDE_CODE_ENTRYPOINT=remote`, `ANTHROPIC_BASE_URL=https://api.anthropic.com`, `CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71`, `CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext`.

**HEAD actually read — and it moved during my run, which I record rather than paper over.**
- Start: `git rev-parse HEAD` → `ce743d6ac63c6645ea65121c7a2157b54b0a2ad8`. This is **not** the `92abbcb905…` named in COMMON-BRIEF.md, **not** W12c's `47aac85…`/`7d08121…`, and **not** W12d's `3f5fc95…` — the coordinator has continued committing collected reports.
- End: `a87275c14897230041fde97c9965c9646474df7a`.
- `git diff --name-only ce743d6..a87275c` → **8 files, every one `research/autonomy/opus-capacity-campaign-20260908/reports/W*.md`** (`W01f`, `W04d`, `W05f`, `W07e`, `W08h`, `W10f`, `W13f`, `W17h`). Filtered to `\.py$|^scripts/|^systems/|^research/manuscripts/|^research/modalities/` → **0 files**. **No file I scanned or executed changed between the two commits**, so every count below is valid at both.
- `git status --porcelain` at start: **empty (0 lines)**. At end: **0 lines**, and `git status --porcelain --untracked-files=all` also **0 lines**. `git diff --stat` at start and end: **empty**.
- I wrote **nothing** into `/home/user/Rare-cancers`. All execution, all scratch and all captures are under `/tmp/claude-0/w12e/`. No git write of any kind. `scripts/preflight.sh` was **not** run.

I read the live cloud checkout at `/home/user/Rare-cancers`. I did **not** need the frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/`: every claim here is a measurement I ran against the live tree, not a novelty or absence claim about prior work.

---

## Question

W12d recommended a single exported `PYTHONUTF8=1` in `scripts/preflight.sh` and proved it: under a forced C locale, 6 of the 18 `--check` rows fail on a clean tree, and with the one line all 18 exit 0 with byte-identical output. But an exported variable reaches only processes that inherit it, and W12d left an explicit UNKNOWN with an upper bound of 173: **188 `env=` subprocess call sites** across `research/manuscripts`, `research/modalities`, `scripts` and `systems`, **73 files** using `os.environ.copy()`-style construction somewhere.

**How many subprocesses actually lose the exported variable, and does that break the one-line fix for the 18-row gate?**

Open because W12d closed on a grep count and said so plainly: *"The 188/173/73 `env=` figures are grep counts, not a resolved analysis of which subprocesses drop the variable. UNKNOWN."* This is W12d's own named successor.

---

## Prior-work check

```
$ rg -n -i 'env=.*subprocess|subprocess.*inherit|environment inheritance|os\.environ\.copy.*audit' --glob '!.git' --glob '*.md'
research/autonomy/opus-capacity-campaign-20260908/reports/W12d-stdout-defect-fix-shape.md:279
research/autonomy/opus-capacity-campaign-20260908/reports/W12d-stdout-defect-fix-shape.md:310
```
Only W12d's own UNKNOWN and its successor paragraph. No prior audit exists.

```
$ git ls-files | rg -i 'subprocess.env|env-inherit|environment-audit|utf8'
   (no output)
$ grep -rn 'PYTHONUTF8\|PYTHONIOENCODING\|PYTHONCOERCECLOCALE' --include='*.py' --include='*.sh' --include='*.yml' . | grep -v opus-capacity-campaign
   (no output)
```
Confirms W12c's and W12d's measured absence still holds at `ce743d6`/`a87275c`: **zero** code, script or workflow hit for any of the three interpreter-encoding variables anywhere in the tree outside this campaign's own report text.

I read `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `W12b-locale-rederivation-proof.md`, `W12c-stdout-defect-census.md` and `W12d-stdout-defect-fix-shape.md` in this directory. I am not re-deriving W12b's 35×3 sweep, W12c's 1,031/317 census, or W12d's 18-row sweep — I consume all three and ran only **one** gate row as a control, as my dispatch permits.

**CLOSED-WORK.md items I confirmed I am not replaying:** the retained NR4A Perspective refusal (not approached, not relabelled); PUB-ASO / the ASO-NAT submission and Qeios history (untouched); the frozen external-validation comment (untouched); every unrecovered source (Pazopanib, anthracycline, sunitinib, trabectedin, Wagner, CTARC — not consulted; irrelevant to a tooling finding); `GSE4303`/`GSE28866` (not read); lane 11's source-index (untouched, W11b sole owner). Per dispatch I did **not** extend anything to `.github/workflows`, did **not** author a test, and did **not** re-run the 18-row sweep. **This report makes no scientific, biological or clinical claim. It is tooling.**

---

## Method / inputs

- Live checkout `/home/user/Rare-cancers`, read at `ce743d6ac63c…` and `a87275c14897…` (no scanned file differs between them). `Python 3.11.15`, Linux `6.18.44-fc-v24`, no network reachable (see Limitations).
- **Every** command ran as `env -i PATH=/usr/local/bin:/usr/bin:/bin HOME=/tmp/claude-0/w12e PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/w12e/pycache <arm vars> python3 …` so no interpreter state or user environment leaked between arms and no `.pyc` could land in the tree.
- **Classification is AST-based, not grep-based.** `/tmp/claude-0/w12e/classify.py` walks every `.py` under the four dispatch directories, finds every `ast.Call` carrying an `env=` keyword, unparses the value expression, and — when the value is a bare `Name` — resolves that name's assignments in the enclosing function and module scopes. Output: `/tmp/claude-0/w12e/env_sites.json`, one record per call site with file, line, callee, verdict, expression and resolution trace.
- Every site the AST could not settle was then **read individually in source**, together with the definition of the helper or the origin of the variable it referenced. That per-call-site read is what closed the residual.
- Measurement harnesses: `/tmp/claude-0/w12e/parent.py` (probe + real gate row, 9 child-env shapes), `arm3.py`, `why.py`, `pair.py`.
- Real child used for the consequence measurement: `research/modalities/atr_hrd_sarcoma_series.py --check` — row 13 of the preflight gate block at `scripts/preflight.sh:849-866`, and the **one** row W12d measured as the encode-class failure (`UnicodeEncodeError` on U+2014 at line 1424).

---

## Result

### 1. Reconciling W12d's 188 — what those grep lines actually are

**PRIMARY.** `grep -rn --include='*.py' 'env=' research/manuscripts research/modalities scripts systems | wc -l` → **188**, reproducing W12d's figure exactly (all 188 are in `.py` files; none is in a shell script or YAML).

| category | n | evidence |
|---|---:|---|
| `env=` keyword arguments on a real call expression (AST) | **147** | `ast.Call` with `keyword.arg == 'env'` |
| function-**definition** parameters — `def prune_enabled(env=None)`, `def converge_mode_for_task(task, env=None)`, … | 21 | not calls at all |
| a **different** keyword whose name ends in `env` — `extra_env=`, `source_env=`, `warmup_env=`, `prod_env=`, `commit_s3_env=`, `commit_gcs_env=`, `proc_env=` | 13 | substring match only |
| string literals, comments, and shell text inside heredocs (`echo "… env=$PROTFEP_ENVIRONMENT"`, `print("[tfep] LEG=%s env=%s …")`) | 5 | not code |
| **grep lines with no `env=` kwarg** | **39** | |

`188 − 39 = 149` matched grep lines against **147** distinct kwargs (two lines matched through a one-line span tolerance). **The operative denominator is 147, not 188.** W12d's 188 is a correct grep count and an over-count of the thing that matters, exactly as W12d flagged.

I also reproduced the other two grep figures. `grep -rl -E 'os\.environ\.copy\(\)|dict\(os\.environ\)|\{\*\*os\.environ'` over the same four directories gives **59 files**, not W12d's 73; W12d's regex was evidently wider. I do not use either number below — the per-site classification supersedes both.

### 2. Classification of all 147 `env=` call sites — the requested three-way split

**PRIMARY.** First split by *what the callee is*, because "a subprocess loses the variable" is only meaningful for a callee that starts an OS process:

| callee | n | starts a local OS process? |
|---|---:|---|
| `subprocess.run` | 86 | yes |
| `subprocess.Popen` | 3 | yes |
| local wrappers `_run`, `_publish`, `_sh`, `sh` | 17 | yes (all resolve into `subprocess.run`) |
| `JobSpec(...)` / `gb.JobSpec(...)` | 21 | **no** — a GPU job description; `env` becomes shell exports in an `onstart` script on a **rented remote host** |
| `tv.converge_mode_for_task`, `cf.plan`, `csa.audit`, `rsc.fingerprint_mismatch_reason`, `commit_store_audit.audit`, `_fmr` | 14 | **no** — `env` is a dict the function *reads* |
| `_agg(mean, sd, n, env, hyst)` in `tests/test_ternary_coop_sign.py` | 6 | **no** — `env` here is the string `'ternary'`/`'binary'`, an FEP **thermodynamic** environment, not a process environment at all |

**106 of the 147 sites launch a local child process. 41 do not.**

Now the three-way verdict, on the 106 that do:

| verdict | n | share |
|---|---:|---:|
| **INHERITS** | **106** | **100 %** |
| **REPLACES** | **0** | 0 % |
| **UNDETERMINED** | **0** | 0 % |

The AST alone settled 74 of the 106. The other 32 required the per-call-site read my dispatch demanded, and **every one of them resolved to INHERITS**. The resolutions, each traced to the line that builds the dict:

| sites | file:line of the `env=` use | construction actually found | verdict |
|---:|---|---|---|
| 6 | `tests/test_publish_does_not_revert_another_jobs_artifact.py` :168,191,200,286,297,302 — literally `_publish(..., env={'PUBLISH_IF_CHANGED':'1'})` | `_run` at **:37-43**: `e = dict(os.environ); e.update(env or {}); e.setdefault(...)` | INHERITS (overlay) |
| 5 | `tests/test_publish_regen_failure_fails_the_step.py` :81,89,102,113 + `_run` :74 | `_run` at **:30-36**: identical `dict(os.environ)` + `update` overlay | INHERITS (overlay) |
| 6 | `scripts/tests/test_the_ledger_clock_can_see_past_its_own_threshold.py` :104,106,112,129,141,284 | `_git_env` at **:98-100**: `dict(os.environ, GIT_AUTHOR_NAME=…, **extra)` | INHERITS |
| 2 | `scripts/tests/test_preflight_cannot_read_stale_bytecode.py` :140,154 | `_env` at **:128-132**: `env = dict(os.environ); env.pop("PYTHONPYCACHEPREFIX"); env.pop("PYTHONDONTWRITEBYTECODE"); env.update(extra)` | INHERITS (and it pops **only** the two cache variables) |
| 2 | `research/modalities/step1_liveness_smoke.py` :109,133 | `_env` at **:101**: `{**os.environ, "RESULT_S3": …}` | INHERITS |
| 2 | `research/modalities/nr4a_paralogue_md_job.py` :219,237 | `env0` at **:202**: `dict(os.environ)`, then `env = dict(env0)` | INHERITS (pops `PYTHONPATH` only) |
| 3 | `research/modalities/pose_second_method.py` :335,378,476 (`env=tools["env"]`) | `tools["env"]` set at **:328** from `env` built at **:290**: `env = dict(os.environ)` | INHERITS |
| 1 | `research/modalities/sagemaker_src/entry_fep.py` :108 | `fep_env = dict(env)` at :105, `env = os.environ.copy()` at **:45** (clears `PYTHONPATH` only) | INHERITS |
| 1 | `sagemaker_src/entry_metad_replica_pocket.py` :37 | caller at :75 passes `e` derived from `base = os.environ.copy()` at **:61** | INHERITS |
| 1 | `sagemaker_src/entry_pocket_reharmonize.py` :38 | caller at :76 ff. passes `e` derived from `base = os.environ.copy()` at **:65** | INHERITS |
| 2 | `scripts/research_run.py` :103, :173 | `env` parameter; callers at :530 pass `os.environ` and at :551 pass `dict(os.environ)` | INHERITS |

**There is not one hand-built environment dict on a local-subprocess call site anywhere in `research/manuscripts`, `research/modalities`, `scripts` or `systems`.** The repository's idiom is uniform: copy `os.environ`, then overlay.

The 41 non-spawning sites do contain hand-built dicts — 22 of them, by AST — but they are two categories that a `PYTHONUTF8` export could not reach and does not need to:
- **21 `JobSpec(env={...})`** (e.g. `selcal_vast_launch.py:403`, `step1_liveness_smoke.py:178`, `congeneric_fanout_vast.py:355`, `nrv04_vast_launch.py:1537`, `protfep_vast_launch.py:298`, `vast_bench_sweep.py:550`, plus test fixtures). These become exports in an `onstart` script executed on a **rented Vast/GCP host**. No variable exported by `scripts/preflight.sh` on the developer's box could ever reach them, with or without this fix, and none of them is a gate row.
- **20 pure-function `env=` data dicts** — `tv.converge_mode_for_task(env={})`, `csa.audit(env={'SEED':'7'})`, `rsc.fingerprint_mismatch_reason(env=env_r2)`, `_agg(env='ternary')`. Nothing is spawned; `env` is parsed.

**Other spawn APIs that can replace an environment — checked and empty.** `grep -rn --include='*.py' -E 'os\.execve|os\.execvpe|os\.spawnve|os\.spawnvpe|posix_spawn|multiprocessing.*env'` over the four directories → **no matches**. So `subprocess` is the only environment-replacing spawn surface, and the 147/106 split covers it.

**Denominator context.** The four directories contain **475** `subprocess.{run,Popen,check_output,check_call,call}(` call sites in total. **89** pass `env=` directly (86 + 3); the remaining ~386 omit it entirely, i.e. `env=None`, i.e. full inheritance by definition. Adding the 17 wrapper sites, **106 of 475 spawn sites name an environment and all 106 inherit; the other ~369 inherit trivially.**

### 3. Step 2 of the dispatch — which REPLACES children print or read non-ASCII

**The local-spawn REPLACES subset is empty (n = 0), so this question has no members and cannot inflate the finding.** Stated for the record so the zero is not mistaken for an unexamined gap: had the subset been non-empty, the filter would have been "is the child a Python process that touches non-ASCII". The nearest non-empty analogue — the 21 `JobSpec` dicts — are consumed by a **remote** host, so the filter is moot there for a different and stronger reason.

### 4. The measurement — real children, real exit codes

**PRIMARY. ARM 1.** Parent under `env -i … LC_ALL=C LANG=C PYTHONUTF8=1 …`, itself confirming `utf8_mode=1 stdout=utf-8 PYTHONUTF8='1' LC_ALL='C'`, launching nine children. Six child-env shapes are the repository's own constructions (line-referenced above); three are **SYNTHETIC** hand-built dicts, marked as such, because the tree contains none to run.

| child env shape | class | rc | child `utf8_mode` | child `stdout.encoding` | `PYTHONUTF8` seen by child |
|---|---|---:|---:|---|---|
| `env=` omitted | INHERITS | 0 | 1 | utf-8 | `'1'` |
| `os.environ.copy()` | INHERITS | 0 | 1 | utf-8 | `'1'` |
| `dict(os.environ)` + pop | INHERITS | 0 | 1 | utf-8 | `'1'` |
| `dict(os.environ, K=V)` | INHERITS | 0 | 1 | utf-8 | `'1'` |
| `{**os.environ, …}` | INHERITS | 0 | 1 | utf-8 | `'1'` |
| `dict(os.environ)` + `.update({…})` | INHERITS | 0 | 1 | utf-8 | `'1'` |
| hand-built `{PATH,HOME}` **[SYNTHETIC]** | REPLACES | 0 | 1 | utf-8 | **`None`** |
| hand-built JobSpec-shaped **[SYNTHETIC]** | REPLACES | 0 | 1 | utf-8 | **`None`** |
| hand-built `{PATH}` **[SYNTHETIC]** | REPLACES | 0 | 1 | utf-8 | **`None`** |

**The transport result is unambiguous: all six real repository shapes carry the fix; all three hand-built shapes lose it.** The REPLACES rows nonetheless show `utf8_mode=1` because — as W12d measured — this container's interpreter is **already** in UTF-8 mode by default, so a child that receives nothing lands in the fixed state by accident. On this box the loss is real but invisible.

**PRIMARY. ARM 2, same nine shapes, real gate row `atr_hrd_sarcoma_series.py --check`:** all nine **rc=0**, all nine printing `OK — the slot is bound to GSE299349 …` with a live U+2014. Consistent with ARM 1 and with W12d's no-op finding; not discriminating.

**PRIMARY. ARM 3 — making the loss observable, with the mechanism isolated.** To observe a consequence I model the broken box (`utf8_mode` off by default, as under C/cp1252) by launching every child as `python3 -X utf8=0`, and carry the fix in the **env-only** variable `PYTHONIOENCODING=utf-8`, which has no `-X` escape hatch that would invert the test. The transport question — does the child's `env` dict carry the parent's fix — is identical for `PYTHONUTF8`; only the `-X` override differs, and that override is an artifact of this container, not of the defect.

First, why a naive REPLACES child survives even then:

| child env (all `-X utf8=0`) | rc | `stdout.encoding` | `utf8_mode` |
|---|---:|---|---:|
| `{PATH,HOME}` | 0 | **utf-8** | 0 |
| `{PATH,HOME}` + `LC_ALL=C` | 0 | **ascii** | 0 |
| `{PATH,HOME}` + `PYTHONCOERCECLOCALE=0` | 0 | **ascii** | 0 |
| `{PATH,HOME}` + `LC_ALL=C` + `PYTHONCOERCECLOCALE=0` | 0 | **ascii** | 0 |

**A hand-built env drops `LC_ALL=C` along with the fix, and PEP 538 C-locale coercion then promotes the bare `C` locale to `C.UTF-8` — so on a Linux C-locale box the REPLACES child is accidentally rescued by losing the hostility at the same time it loses the cure.** That is a genuine and non-obvious mitigation, and it is a Linux/glibc one: on a cp1252 Windows console the hostility is the ambient code page, which no `env` dict can strip, so the rescue does not transfer.

With coercion disabled — i.e. modelling a box where dropping the environment does **not** drop the hostility — the paired contrast on the real gate row:

| # | child env shape | fix present in child | rc | outcome |
|---|---|---|---:|---|
| A | **REPLACES**, hostile locale kept | `None` | **1** | `UnicodeEncodeError: 'ascii' codec can't encode character '\u2014' in position 3` |
| B | **REPLACES**, hostile locale dropped too | `None` | **1** | `UnicodeEncodeError: 'ascii' codec can't encode character '\u2014' in position 3` |
| C | **INHERITS** `{**os.environ}` | `'utf-8'` | **0** | `OK — the slot is bound to GSE299349 …` |
| D | **INHERITS** `os.environ.copy()` | `'utf-8'` | **0** | `OK — the slot is bound to GSE299349 …` |
| E | **INHERITS** `dict(os.environ)`+`update` | `'utf-8'` | **0** | `OK — the slot is bound to GSE299349 …` |

**The mechanism is proved with real exit codes: a child given a hand-built `env` dict loses the fix and the gate row dies on its own diagnostic; a child given any of the repository's three real constructions keeps it and exits 0.** The repository has zero instances of the first shape on a local spawn.

### 5. The gate specifically — the question W12d actually needed answered

**PRIMARY, and this is the headline.** Of the 18 `--check` rows at `scripts/preflight.sh:849-866`:

- **`env=` kwarg sites inside the 18 gate-row modules: 0. Every one of the eighteen, measured individually.** (`submission_tables` 0, `claim_coverage` 0, `submission_citations` 0, `submission_metrics` 0, `aso_sequence_manifest` 0, `aso_journal_tables` 0, `aso_offtarget_duplex_energy` 0, `submission_packet` 0, `vaccine_path_tables` 0, `aso_archive_manifest` 0, `aso_deposit_drift` 0, `emc_condensate_report` 0, `atr_hrd_sarcoma_series` 0, `single_slot_identity` 0, `instrument_census` 0, `trigger_scan` 0, `citation_debt` 0, `news_match` 0.)
- The 18 rows contain **4** subprocess call sites in total, in 3 modules, and every one is a **`git`** invocation with `env=` absent: `submission_citations.py:304` (`git ls-tree`), `:307` (`git show`), `aso_archive_manifest.py:955` (`git *args`), `aso_deposit_drift.py:62` (`git -C ROOT`). `git` is not a Python process; it is also given a fully inherited environment.
- `preflight.sh` starts each row as bare `python3 "$gen" "$mode"` with no `env -i`, no `env -u` and no environment scrubbing anywhere in the file (`grep -n 'env -i\|/usr/bin/env -' scripts/preflight.sh` → no matches).

**No gate row spawns a REPLACES child. No gate row spawns a Python child at all.**

---

## Consequence for W12d's recommendation

**The one-line `export PYTHONUTF8=1` is sufficient for the 18-row gate. No `env=` dict audit is additionally required for the gate, because no gate row constructs one.** This is the clean result my dispatch anticipated, and I am saying it plainly rather than manufacturing a residual.

Stated as numbers, replacing W12d's UNKNOWN:

| W12d's residual row | W12d | W12e (measured) |
|---|---|---|
| "Sub-processes spawned with a replaced environment" | **UNKNOWN, upper bound 173** | **0 of 106 local-spawn `env=` sites. 0 of 18 gate rows. Upper bound 173 → actual 0.** |

Three qualifications that belong with that zero, none of which changes it:

1. **The zero is about local subprocesses.** 21 `JobSpec(env={...})` sites *are* hand-built environments, and they *do* lose the variable — but they are consumed on rented remote hosts that a developer-box export was never going to reach, and none is a gate row. If someone later wants UTF-8 on a rented host, that is an `onstart`-script change in `gpu_backend.py`, a different repair with a different owner, and it is **not** a defect in W12d's fix.
2. **The zero is a property of the current tree, not a guarantee.** It holds because the repository's idiom is uniformly copy-then-overlay. Nothing enforces that; the first hand-built `env=` dict added to a gate-row module would silently reintroduce the defect, and no check would notice. Whether that deserves a guard is W14's question, not mine, and I did not author one.
3. **The Linux C-locale rescue is real but does not transfer.** ARM 3 shows a hand-built env on Linux drops `LC_ALL=C` too and PEP 538 coercion saves the child. On Windows/cp1252 the hostility is not an environment variable and the rescue is absent. Any future REPLACES site would therefore be a **Windows-only** failure — the hardest kind to catch on this box, and the exact platform W12's original defect class came from.

---

## Validation evidence

**RUN.** Common environment for every command: cwd `/home/user/Rare-cancers` (or `/tmp/claude-0/w12e/`), tree at `ce743d6ac63c…`→`a87275c14897…` (no scanned file differs), `Python 3.11.15`, Linux `6.18.44-fc-v24`, `env -i PATH=/usr/local/bin:/usr/bin:/bin HOME=/tmp/claude-0/w12e PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/w12e/pycache` plus each arm's variables.

1. `grep -rn --include='*.py' 'env=' research/manuscripts research/modalities scripts systems | wc -l` → **188**, rc 0. W12d reproduced exactly.
2. `python3 /tmp/claude-0/w12e/classify.py` → rc 0, `AST env= kwarg call sites: 147`, `Counter({'INHERITS': 82, 'UNDETERMINED': 33, 'REPLACES': 32})` (pre-read verdicts, over all 147 including non-spawning callees). Records at `/tmp/claude-0/w12e/env_sites.json`.
3. `python3 /tmp/claude-0/w12e/recon2.py` → rc 0, `grep 188 unmatched 39`, categorised `def-param 21 / other-kwarg 13 / string-comment 5`.
4. Per-call-site source reads of all 32 non-INHERITS spawn sites and every helper/origin they reference (`_run` :37-43 and :30-36, `_git_env` :98-100, `_env` :128-132 and :101, `env0` :202, `env` :290, `os.environ.copy()` :45/:61/:65, `research_run.py` :530/:551). All INHERITS.
5. `python3 /tmp/claude-0/w12e/parent.py` under `LC_ALL=C LANG=C PYTHONUTF8=1` → **rc 0**. ARM 1 nine-row table and ARM 2 nine-row gate-row table quoted verbatim above.
6. `python3 /tmp/claude-0/w12e/arm3.py` under `LC_ALL=C LANG=C PYTHONIOENCODING=utf-8` → **rc 0**, six rows, all rc 0 with `fix seen` `'utf-8'` vs `None`.
7. `python3 /tmp/claude-0/w12e/why.py` → coercion mechanism isolated; `REPLACES + LC_ALL=C + PYTHONCOERCECLOCALE=0` on the real gate row → **rc 1**, `UnicodeEncodeError: 'ascii' codec can't encode character '\u2014' in position 3: ordinal not in range(128)`. (This script raised a trailing-whitespace `KeyError` on its own final control loop **after** the decisive row had run; the control was rerun cleanly in step 8.)
8. `python3 /tmp/claude-0/w12e/pair.py` → **rc 0**, the five-row A–E paired table quoted above: REPLACES rc 1 ×2, INHERITS rc 0 ×3.
9. Gate-row `env=`/subprocess census: per-file `grep -c` over all 18 rows → `env=:0` for all eighteen; `subprocess-calls` 2/1/1 in three modules, read in source, all `git`, all `env=` absent.
10. `grep -rn --include='*.py' -E 'os\.execve|os\.execvpe|os\.spawnve|os\.spawnvpe|posix_spawn|multiprocessing.*env'` over the four directories → **no matches**.
11. `sed -n '840,880p' scripts/preflight.sh` → rows launched as bare `python3 "$gen" "$mode"`; `grep -n 'env -i\|/usr/bin/env -' scripts/preflight.sh` → no matches.
12. Tree integrity after every arm: `git rev-parse HEAD`, `git status --porcelain` (0 lines, also with `--untracked-files=all`), `git diff --stat` (empty).

Raw captures and harnesses retained under `/tmp/claude-0/w12e/` (`classify.py`, `recon.py`, `recon2.py`, `dump.py`, `summ.py`, `parent.py`, `arm3.py`, `why.py`, `pair.py`, `env_sites.json`).

**PROPOSED (NOT RUN).**
- `scripts/preflight.sh` was **not** executed, per dispatch. "The fix is sufficient for the gate" rests on the 18 rows' measured `env=` content plus W12d's individually-run 18-row sweep — it is **not** a preflight observation.
- No Windows, cp1252 or macOS execution. Every cp1252 statement, including the "the Linux rescue does not transfer" claim, is **PREDICTION** from the documented locale mechanism, not a measurement.
- W12d's proposed diff remains unapplied and un-`git apply --check`ed. I wrote no patch and authored no test.
- The three REPLACES child shapes in ARM 1/ARM 3 are **SYNTHETIC**, constructed by me, because the tree contains no local-spawn REPLACES site to run. They demonstrate the mechanism, not repository behaviour.

---

## Limitations

- **Static classification of dynamic dicts.** I read each construction site and each helper definition, but I did not trace every mutation between a dict's construction and its use. A `del env["PYTHONUTF8"]` executed somewhere between the two would be invisible to this method. I searched for no such thing and found none; that is a **negative search result, not a proof**.
- **Scope is W12d's four directories.** `research/autonomy` holds a further **10** `env=` grep lines that I did not classify (out of W12d's scope and out of mine), and `.github/workflows` is excluded by dispatch. Both are **UNKNOWN**.
- **Wrapper resolution is one hop deep by inspection.** I resolved `_run`/`_publish`/`_sh`/`sh`/`_env`/`_git_env` to their definitions by hand. A longer chain in a file I classified as INHERITS at the first hop would not have been caught by the AST pass alone; I did not find one.
- **One platform, one interpreter, one locale family.** `-X utf8=0` plus `PYTHONCOERCECLOCALE=0` is a faithful model of an ASCII-stdio interpreter and strictly harsher than cp1252, but it is not a Windows console.
- **This box masks the defect** — `sys.flags.utf8_mode` is already 1 — which is precisely why ARM 1's `rc=0` rows are not evidence that REPLACES is safe, and why ARM 3 was needed. I report the transport fact (`PYTHONUTF8` seen: `'1'` vs `None`) as the primary measurement and the exit codes as its consequence under a modelled interpreter.
- **The `atr_hrd_sarcoma_series.py --check` control attempted outbound HTTPS during my run** — the agent proxy denied 5 CONNECTs (`rest.ensembl.org` ×3, `rest.uniprot.org`, `www.ebi.ac.uk`, all `connect_rejected` by organization policy). The row still exited 0 in every INHERITS arm, so it degrades gracefully; but its `--check` is **not** fully offline, and its exit code under this container's egress policy may not equal its exit code on a networked box. I did not retry, reroute or rephrase any denied route.
- **No scientific, biological or clinical claim is made or supported by anything here.** This is tooling.

---

## Stop condition

**Set up front:** stop as soon as (a) every one of the 188 grep lines is accounted for and every real `env=` call site carries a per-site verdict of INHERITS / REPLACES / UNDETERMINED with the construction that justifies it, (b) at least three representative children have been launched from a parent under `LC_ALL=C LANG=C PYTHONUTF8=1` with their retained-or-lost fix state and real exit codes recorded, and (c) the sufficiency of W12d's one-line export for the 18-row gate is answered yes-or-no from measured evidence rather than inference.

**MET.** (a) 188 fully reconciled — 147 real kwargs, 39 non-kwarg lines categorised; 106 local-spawn sites classified, 32 of them by individual source read, residual UNDETERMINED = 0. (b) nine children in ARM 1, nine in ARM 2, six in ARM 3 and five in the paired control — well past three, with real exit codes including two `rc=1 UnicodeEncodeError`s and three `rc=0`s on a genuine gate row. (c) answered **yes, sufficient**, from a per-row measurement of all 18 gate modules. Returned immediately on meeting it.

---

## Tool-call and wall-clock count actually used

**17 tool calls** (16 `Bash`, 1 `Bash` heredoc-edit; no `Read`, `Write` or `Edit` against the repository). Wall clock **02:57:37Z → 03:03:19Z = 5 min 42 s** of execution, plus report drafting. Well inside the ~40-call / ~40-min target.

---

## Next concrete action

**One successor, bounded and inside lane 12, and it is a decision the owner should make before any more measurement: close lane 12's defect thread by handing W12b→W12e to the `scripts/preflight.sh` owner as a single one-line change with its evidence chain attached.** The chain is now complete and internally consistent — W12b isolated the class, W12c sized it (1,031 sites / 317 files / 16 of 18 gate rows), W12d found the smallest correct repair and proved it byte-identical on all 18 rows, and W12e has closed its only quantitative residual at **0 of 106**. There is no further measurement that changes the recommendation; additional lane-12 census work would be padding.

Two things I explicitly do **not** recommend as next, with reasons:
- **Extending the export to `.github/workflows`** — 161 files, a CI-configuration change rather than a defect repair, and W12d already declined it for the same reason.
- **Authoring a guard test** ("the 18 rows survive a C locale") — it is the obvious follow-on, it would catch the one way the zero above could silently become non-zero, and it is **W14's** question, not lane 12's. Flagged for W14; not started, not scoped, not written.
