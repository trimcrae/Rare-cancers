<!-- collected 2026-09-08T03:43:42Z by campaign coordinator; agent id a1941ee4c316dc290; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a1941ee4c316dc290.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

**W29d** — subprocess exit-status defect census lane, OPUS-CAPACITY-CAMPAIGN-20260908. Successor to W29b's R3 finding.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). Nothing in this container's environment names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start**: `Tue Sep  8 ~03:26 UTC 2026` (first captured explicit stamp `03:40:17`; start HEAD capture preceded it in the same session) · **end**: `Tue Sep  8 03:40:30 UTC 2026`.

`git rev-parse HEAD` **start**: `1c9d827870599576c0c027a9134363d59456fd04` · **end**: `5ae0fa04ff9516ac8f820381079d644a094f4a77`. HEAD moved under me (the coordinator collecting sibling reports). Every finding is anchored to `file:line` plus quoted source read from the live checkout; the intervening commits are report collection, not source changes to the files I measured. Neither HEAD is `92abbcb9` (the campaign *start* commit, not a pin — per the corrected brief).

`git status --porcelain` at end: **empty**. I wrote nothing into `/home/user/Rare-cancers` and ran no git write operation. All execution under `/tmp/claude-0/w29d/` with `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/w29d/pyc`; **the scratch directory has been deleted** (`ls` → `No such file or directory`, quoted below).

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (end-of-run; the five long proxy-list variables `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` are filtered out of this paste — they appear verbatim in the start capture in the transcript and contain no model information):

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
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

## Question

W29b's R3 established one live silent degrade: `research/manuscripts/submission_citations.py:303-307` shells out to `git ls-tree -r --name-only origin/literature-cache`, never reads `returncode`, and on this checkout the command exits **128** — so the last-resort metadata source contributes zero records and says nothing.

**How widespread is that defect shape?** Concretely: across `scripts/`, `research/` and `systems/` (`.py`, `.sh`, `.mjs`), how many subprocess call sites do not inspect the exit status; which of them are LOAD-BEARING (a silent failure changes a reported result or a gate verdict) versus BENIGN; and — for the top load-bearing cases — what is the *real* exit code of the underlying command in this tree today?

Open because W29b measured exactly one site, in one function, and explicitly framed it as an instance ("This is a silent degrade that is currently active, not a hypothetical"). Nothing had asked how large the population is.

## Prior-work check

Commands run in `/home/user/Rare-cancers`, campaign directory excluded:

```
rg -n -i "returncode|check=False|exit status|\|\| true" --glob '!.git' \
   --glob '!research/autonomy/opus-capacity-campaign-20260908/**' -l   -> 169 files
git ls-files | rg -i "subprocess|exit.?code|returncode|census"
rg -n -i "silent degrade|exit status is not|ignores? (the )?(return|exit)" \
   --glob '!.git' --glob '!research/autonomy/opus-capacity-campaign-20260908/**'
```

The third search returned exactly **two** tracked hits, both self-documentation of this defect shape, not a census:

```
research/manuscripts/emc_systemic_therapy_pooling.py:1465:  # shell's exit status is not wired into anything, however correct its comparison is.
research/manuscripts/emc_fusion_partner_pooling.py:2305:  # shell's exit status is not wired into anything, however correct its comparison is.
```

A third self-documentation sits at `research/compute/publish_artifacts.sh:121` — *"every call site here is `|| true`-shaped, so the snapshot would come up empty"*. **No tracked repository artifact enumerates this defect class.** No `git ls-files` hit is a census of subprocess exit handling.

Campaign siblings checked for overlap (and they are not repository evidence, per the corrected brief): `W12c-stdout-defect-census.md` is about `sys.stdout` encoding under a hostile locale; `W12e-subprocess-env-residual.md` is about `env=` inheritance of `PYTHONUTF8`. Both are subprocess-adjacent and **neither asks about exit status**. `W14b-guard-coverage-sweep.md` / `W14e-fake-guard-triage.md` concern guard coverage, not subprocess status. I am not replaying W29b's single site — I re-verified it and extended it.

W25 was not read, referenced or opened.

## Method and inputs

1. **Enumeration (Python).** An AST scanner (`/tmp/claude-0/w29d/census.py`, now deleted) walked every `.py` under `scripts/`, `research/`, `systems/` — **1,490 files, 1,490 parsed, 0 parse failures** — and collected every `ast.Call` whose qualified callee ends in `run`, `check_output`, `Popen`, `call`, `check_call`, `system`, `popen`, `getoutput`, `getstatusoutput` on a `subprocess.`/`sp.`/`os.` receiver. For each site it recorded kwargs, `check=` value, assignment target, enclosing function, and whether `.returncode`/`.check_returncode` appears on that target anywhere in the enclosing function.
2. **Refinement.** A second pass (`refine.py`) re-parsed each flagged site to separate three cases the first pass conflates: `CHECKED_INLINE` (`subprocess.run(...).returncode` used directly as the expression value), `DEFERRED_TO_CALLER` (a helper wrapper that *returns* the `CompletedProcess`, so the check belongs at its call sites), and genuinely `UNCHECKED`.
3. **Caller audit** of every `DEFERRED_TO_CALLER` wrapper in non-test, non-remote-entrypoint code, by grepping `returncode` in the wrapper's own file.
4. **Shell/JS.** `find` + `rg` over 19 `.sh` and 11 `.mjs` files: `|| true` sites, and whether each script arms `set -e`.
5. **Execution verification** of the top load-bearing cases: the underlying commands run read-only in the live tree with their real rc captured, plus two in-process/CLI runs of the affected modules.

Inputs are the live checkout at the HEADs above. The frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/corpus/` was **not** used — this question is about the live tree's actual refs and exit codes, which a file snapshot cannot answer.

## Result

### R1 — The denominator, stated honestly

| Quantity | n | Evidence class |
|---|---|---|
| `.py` files under `scripts/`,`research/`,`systems/` | 1,490 (all parsed, 0 failures) | `PRIMARY` |
| **Python subprocess call sites enumerated** | **539** | `PRIMARY` |
| Sites where the scanner found an exit-status inspection | 341 | `PRIMARY` |
| Sites flagged for refinement | 198 | `PRIMARY` |
| — of those, `CHECKED_INLINE` (`run(...).returncode` as the value) | 18 | `PRIMARY` |
| — of those, `DEFERRED_TO_CALLER` (wrapper returns `CompletedProcess`) | 41 | `PRIMARY` |
| — of those, **`UNCHECKED` (no exit-status inspection anywhere in the enclosing scope)** | **139** | `PRIMARY` |
| `UNCHECKED` in non-test, non-remote-GPU-entrypoint code | 53 | `PRIMARY` |
| `UNCHECKED` by area | modalities 113, manuscripts 13, scripts 8, autonomy 5 | `PRIMARY` |
| `.sh` files | 19; **84** `\|\| true` sites total | `PRIMARY` |
| `.sh` files that do **not** arm `set -e` | 12 of 19 | `PRIMARY` |
| **`.mjs` subprocess call sites** | **0** (11 `.mjs` files; `rg` for `child_process\|execSync\|spawnSync\|exec(\|spawn(` returned nothing) | `PRIMARY` |
| **Graded from source only** | 130 of 139 `UNCHECKED` Python sites + all 84 shell sites | `PRIMARY` |
| **Verified by executing the underlying command** | **9** (7 git commands + 2 module runs) | `PRIMARY` |

**Scanner limits, measured not assumed.** The 341 "checked" figure includes `check_output`/`check_call` (which raise) and `check=True`. It counts an inspection *anywhere in the enclosing function*, so it can over-credit a site whose `.returncode` is read on a different branch. Conversely the 139 `UNCHECKED` can over-report where the check lives in a caller of a non-returning helper. Both directions were spot-checked by hand for every site graded below; the aggregate figures were not.

### R2 — The four-way contrast on one identical failure mode (`PRIMARY`, executed)

Four modules read the same non-existent ref, `origin/literature-cache`. **The repository does not handle it consistently.** This is the single most informative result of the census.

| Site | Handling | Verdict on a rc=128 |
|---|---|---|
| `research/manuscripts/build_reference_list.py:78` | `if ls.returncode: sys.exit("cannot read origin/literature-cache — run \`git fetch origin literature-cache\` first")` | **Fails loud, with the remedy.** `BENIGN` |
| `research/manuscripts/journal_reference_authors.py:246-254` | `check=True` inside `try`, `except CalledProcessError: raise SystemExit("cannot read … — \`git fetch origin literature-cache\` first")` | **Fails loud, with the remedy.** `BENIGN` |
| `research/manuscripts/aso_delivery_routes.py:100` | `check=True`; `_load()` catches and returns `None`; the caller records *"not present … at read time — an ABSENT READING, never a reading of absence"* | **Degrades, and says so in the artifact.** `BENIGN` |
| **`research/manuscripts/submission_citations.py:304, 307`** | **no `check=`, `returncode` never read** | **Silent. 0 records, 0 bytes of output.** `LOAD-BEARING` |

Three of four consumers of the *same* ref announce the failure and name the fix. The fourth does not. The defect is therefore not an unrecognised hazard in this repository — it is a **single omission inside a pattern the repository otherwise applies correctly**, which is why W29b's finding is a real defect rather than a design preference.

### R3 — LOAD-BEARING sites, graded

| # | `file:line` | Command | What the caller does with empty output | Grade |
|---|---|---|---|---|
| 1 | `research/manuscripts/submission_citations.py:304` | `git ls-tree -r --name-only origin/literature-cache` | `for path in r.stdout…` never iterates; `out` stays `{}` | **LOAD-BEARING** (confirmed rc=128) |
| 2 | `research/manuscripts/submission_citations.py:307` | `git show origin/literature-cache:{path}` | unreachable today because #1 yields no paths; independently rc=128 | **LOAD-BEARING** (confirmed rc=128) |
| 3 | `research/manuscripts/lint_changed_prose.py:114` | `git diff -U2 [rev_range] -- <targets>`; `_git()` returns only `.stdout` | zero hunks → **"0 changed passage(s) … OK", rc 0** | **LOAD-BEARING** (confirmed: underlying rc=128, module rc=0) |
| 4 | `research/manuscripts/journal_reference_authors.py:267` | `git hash-object <file>` | `.stdout.strip()` → `""` recorded as the source **blob hash** in the provenance record | **LOAD-BEARING** (provenance); rc=0 today |
| 5 | `research/autonomy/cadence.py:118` | `git log -1 --format=%cI -- <newest>` | file has **zero** `returncode` references; empty stdout becomes the cycle-start timestamp | **LOAD-BEARING** (reported result); rc UNKNOWN in a degraded tree |
| 6 | `research/modalities/nr4a3_linker_library_canonical.py:524` | `git log -1 --format=%H -- research/modalities/linker_design.py` | empty string recorded as the kernel-provenance SHA | **LOAD-BEARING** (provenance); rc=0 today |
| 7 | `research/modalities/instrument_register_renumber.py:171` | `git ls-files --cached --others --exclude-standard` | empty file list → renumber sees an empty tracked tree | **LOAD-BEARING**; rc=0 today |
| 8 | `research/compute/publish_artifacts.sh:151` | `BASE="$(git rev-parse HEAD 2>/dev/null \|\| true)"` — script arms `set -uo pipefail`, **no `-e`** | empty `BASE`; the file's own comment at :121 says the snapshot "would come up empty" | **LOAD-BEARING** (self-documented) |
| 9 | `research/modalities/throughput_harvest.py:339` / `throughput_decay.py:117` | `_sh(...)` returns `.stdout` only | empty measurement series feeds a reported throughput figure | **LOAD-BEARING** (reported result) |

### R4 — BENIGN sites, graded (representative, not exhaustive)

| `file:line` | Why benign |
|---|---|
| `research/autonomy/publish_bar.py:181, 184` | `git worktree remove --force` / `prune` in a `finally:`; **cleanup after the result is already yielded**. The load-bearing `worktree add` two lines up at :171 **does** check `added.returncode != 0` and yields an explicit failure message. |
| `research/manuscripts/row4_pose_map_edits.py:362, 378` | `git show origin/main:<file>` unchecked, but empty body → `na = 0` → `ok` false → `bad` increments. **Fails closed, louder not quieter.** Verified `git show origin/main:…` rc=0, 27,133 bytes in this tree. |
| `scripts/emc_km_reachability_census.py:41` | explicit `check=False`, `.stdout.strip() or None` — records **`None`**, i.e. "unknown", not a wrong value. |
| `research/modalities/autoteardown.py:80, 91`; `modal_gpu_bench.py:37`; `nr4a3_md_modal.py:41, 59` | remote-host GPU entrypoints; `nvidia-smi` is a diagnostic print, `apt-get install` is best-effort setup, the teardown call is by design last-resort. Not a repository gate verdict. |
| `scripts/preflight.sh` — 34 `\|\| true` sites | Every one I read is followed by an explicit test of the *content* (`failed=$(grep -cE '^FAILED' …)`, `_ocount`, `_mcount`, `_slines`) and each carries a comment explaining that `grep` exits 1 on no match under `set -euo pipefail`. **The status is discarded deliberately and the verdict is rebuilt from output.** |
| `scripts/preflight.sh:661` (`lint_changed_prose.py \|\| true`) and `:713` (`lint_readability.py --report`) | The gate comment at :657-660 states the instrument "reports warnings rather than errors, so it cannot fail the build". The `\|\| true` is correct **at the gate**; the defect is inside the module (row 3 above). |
| `research/manuscripts/claim_ablation.py:124, 242`; `fusion_cofold.py:112`; `nr4a3_ternary.py:136`; `selcal_cofold_run.py:172, 292, 305`; `nrv04_ternary.py:146` | Scanner false positives — `.returncode` is taken directly on the call expression (`CHECKED_INLINE`, n=18). |
| `aso_deposit_drift.py:62`, `build_reference_list.py:50`, `emc_model_junction_evidence.py:59`, `emc_prior_art_fulltext_screen.py:58`, `goal_progress.py:41`, `queue_view.py:86` | `DEFERRED_TO_CALLER` wrappers whose callers **do** check — confirmed by `grep -c returncode`: 1, 2, 2, 1, 1, 2 respectively, each at the decision point. |

### R5 — "No exit-status check" is measured; "will fail in practice" is mostly UNKNOWN

| Claim | Status |
|---|---|
| 139 Python sites have no exit-status inspection | **PRIMARY, measured** |
| 2 of them (`submission_citations.py:304,307`) fail **right now** in this checkout | **PRIMARY, executed — rc=128** |
| 1 of them (`lint_changed_prose.py:114`) produces a false clean verdict on any unresolvable rev-range | **PRIMARY, executed — underlying rc=128, module rc=0** |
| The other 136 will fail in practice | **UNKNOWN.** Six were executed and returned **rc=0** in this tree (`git show origin/main:…`, `git log -1 --format=%H -- linker_design.py`, `git hash-object`, `git diff -U2 -- research/manuscripts`, `git cat-file -e origin/main:…`). rc=0 today is **not** proof they cannot fail; it is one measurement in one tree. |
| The 84 shell `\|\| true` sites are defects | **NO — refuted for `scripts/preflight.sh`.** Its 34 sites are documented and content-tested. Only `publish_artifacts.sh:151` was graded load-bearing, on the strength of its own comment. |

## Validation evidence

Environment: `/home/user/Rare-cancers`, Linux, `python3` (system), `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/w29d/pyc`. All **RUN** unless stated.

**V1 — refs present in this checkout** (`git for-each-ref --format='%(refname)'`, rc=0):
```
refs/heads/claude/confident-bardeen-ji76cd
refs/heads/main
refs/remotes/origin/claude/confident-bardeen-ji76cd
refs/remotes/origin/codex/opus-cloud-inputs-20260908
refs/remotes/origin/main
```
Neither `refs/remotes/origin/literature-cache` **nor** `refs/heads/literature-cache` exists at HEAD `1c9d8278`. (W29b reported `refs/heads/literature-cache` present at `216bd1b5fb25…` at its own HEAD; at mine it is absent. I record the discrepancy and do not resolve it — it does not change the outcome, since `origin/literature-cache` is what all four modules name.)

**V2 — the underlying commands, real exit codes:**
```
--- git ls-tree -r --name-only origin/literature-cache
rc=128   stdout_bytes=0   fatal: Not a valid object name origin/literature-cache
--- git show origin/literature-cache:x.json
rc=128   stdout_bytes=0   fatal: invalid object name 'origin/literature-cache'.
--- git show origin/main:research/manuscripts/row4_pose_map_edits.py
rc=0     stdout_bytes=27133
--- git log -1 --format=%H -- research/modalities/linker_design.py
rc=0     stdout_bytes=41
--- git hash-object research/manuscripts/lint_citations.py
rc=0     stdout_bytes=41
--- git diff -U2 -- research/manuscripts
rc=0     stdout_bytes=0
--- git cat-file -e origin/main:research/manuscripts/lint_citations.py
rc=0     stdout_bytes=0
```

**V3 — the silent degrade, executed in-process** (`_literature_cache()` loaded by `importlib`, stdout and stderr both captured):
```
SITE A submission_citations._literature_cache()
  records returned: 0
  stdout emitted: ''
  stderr emitted: ''
rc=0
```
**Zero records, zero bytes on either stream.** W29b's R3 finding is independently reproduced at a different HEAD.

**V4 — the new load-bearing site, executed via its CLI:**
```
$ python3 research/manuscripts/lint_changed_prose.py no-such-ref-xyz..HEAD
lint_changed_prose: 0 changed passage(s) over no-such-ref-xyz..HEAD
   OK
rc=0

$ git diff -U2 no-such-ref-xyz..HEAD -- research/manuscripts
underlying rc=128
fatal: bad revision 'no-such-ref-xyz..HEAD'
```
The module reports **`OK`, rc 0**, naming the very rev-range git refused to resolve. `_git()` at :114 returns `.stdout` and discards the `CompletedProcess`.

**V5 — caller audit of deferred wrappers** (`grep -c returncode`): `aso_deposit_drift.py` 1 (`:73 if shown.returncode != 0`), `build_reference_list.py` 2 (`:78`, `:83`), `emc_model_junction_evidence.py` 2, `emc_prior_art_fulltext_screen.py` 1, `goal_progress.py` 1, `queue_view.py` 2 — all at decision points. `research/autonomy/cadence.py` **0** — genuinely unchecked.

**V6 — write isolation and scratch deletion:**
```
$ rm -rf /tmp/claude-0/w29d && ls -d /tmp/claude-0/w29d
ls: cannot access '/tmp/claude-0/w29d': No such file or directory
$ git status --porcelain      (in /home/user/Rare-cancers)
   [no output]
```

**PROPOSED (NOT RUN):** hand-verification of the 130 unexecuted Python sites and the 83 unexecuted shell sites; determination of whether `cadence.py:118`'s `git log` can fail in a real tree; execution of `journal_reference_authors.py`, `instrument_register_renumber.py` and `publish_artifacts.sh` under a deliberately broken git. **None of these was run.** No repair, patch or diff was authored, proposed or applied, per my dispatch. `scripts/preflight.sh` was **not** run. `research/modalities/atr_hrd_sarcoma_series.py` was **not** invoked.

## Limitations

- **The 539 / 341 / 139 figures are scanner output, not 539 hand reads.** The AST heuristic credits an inspection anywhere in the enclosing function and cannot follow a `CompletedProcess` through a data structure or across modules. It is a screen that says where to look. Only the ~25 sites in R3/R4 were read by hand.
- **Shell is graded far more coarsely than Python.** I counted `|| true` (84) and `set -e` arming (12 of 19 scripts lack it) — I did **not** enumerate every `$(...)` command substitution in shell, so the shell denominator is a lower bound and the true shell figure is **UNKNOWN**.
- **`.mjs` returned zero call sites.** That is measured absence of `child_process` usage in the 11 files, not proof the files run no external process by another route.
- **rc=0 today is one measurement in one tree.** Six sites returned rc=0 here; that establishes they are not *currently* failing, and nothing more. Their behaviour in CI's default checkout, in a fresh clone, or in a worktree is **UNKNOWN**.
- The LOAD-BEARING / BENIGN grading is my judgement against the dispatch's definition, applied to code I read. It is not a test result. For sites 4-7 and 9 in R3 I graded on *what the value is used for*, having confirmed no exit check exists — I did **not** demonstrate a wrong output for any of them. Only sites 1-3 are demonstrated.
- This census says nothing about EMC efficacy, safety, selectivity or clinical readiness, and touches no patient data. It is a software-defect inventory.
- No repair is offered, by instruction. Nothing here should be read as a recommendation to change any guard.

## Stop condition

**Set up front:** return once (a) every `.py`/`.sh`/`.mjs` subprocess call site under `scripts/`, `research/`, `systems/` is enumerated with a stated denominator, (b) the unchecked set is separated from the checked and the deferred, (c) the load-bearing subset is graded with `file:line` and consequence, and (d) at least the top load-bearing cases are verified by running the underlying command and recording its real exit code.

**MET.** 539 Python sites enumerated (139 unchecked), 84 shell `|| true` sites, 0 `.mjs` sites; 9 verifications executed; 2 sites confirmed failing at rc=128 today and 1 further module demonstrated returning a false `OK`. Returned immediately on meeting it.

## Tool-call and wall-clock count actually used

**27 tool calls** (all `Bash`; no file writes into the repository, no git write operation, no network, no paid API, no GPU). **Wall clock ≈ 15 minutes** (`03:25`–`03:40:30 UTC`), against the ~40-call / ~40-minute target. Returned early.

## Next concrete action

**One successor task for this lane:** decide the disposition of `research/manuscripts/lint_changed_prose.py:114` — the one *newly* demonstrated load-bearing site (R3 row 3, V4). It is a preflight row (`scripts/preflight.sh:661`), it prints `OK` and exits 0 on a rev-range git exited 128 on, and unlike `submission_citations.py` its consequence is not currently zero: it is the repository's only instrument watching for a dropped qualifier, and the corpus records that this defect class produced most of hardening rounds 9-11's findings. The successor should (i) determine whether any tracked workflow or documented invocation actually passes a rev-range to it — I did not check `.github/workflows/`, so that is UNKNOWN — and (ii) route the finding to the module's owner. **I am not the right actor to author the repair**: my dispatch forbids proposing one, and per `CLAUDE.md` §7 a change to a preflight-row module belongs to one coordinator in an isolated worktree, not to a read-only census worker.
