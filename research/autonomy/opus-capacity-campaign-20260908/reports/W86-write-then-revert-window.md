<!-- collected 2026-09-08T05:11:06Z by campaign coordinator; agent id a0ec65d6c8ce32d83; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a0ec65d6c8ce32d83.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

## Worker

**W86** — lane: record-only observation of writes during execution of the ungoverned test directories (`scripts/tests`, `systems/tests`); W70's named successor. Campaign OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

- `date -u` **start** `Tue Sep  8 05:02:06 UTC 2026` · **end** `Tue Sep  8 05:07:50 UTC 2026`
- `git rev-parse HEAD` (live) **start** `b1f6a6dcc2149b6a8a5ee38ccfc54823c07bb056` · **end** `0d05cb7b3bf27921cceeb76bd69873ed89eb9fd6`. HEAD advanced four times under me (`b1f6a6dc` → `cf0af448` at the moment of `cp -a` → `9a936582` → `0d05cb7b`), all coordinator collection commits inside the campaign directory (direction proved in Validation).
- `git status --porcelain` on `/home/user/Rare-cancers`: **0 lines at start, 0 lines at end.** No repository write, no git write operation (only `rev-parse`, `log`, `status`, `ls-files`, `check-ignore`, `grep`, `sed`, `cat`, `diff`).
- Scratch `/tmp/claude-0/w86/` **deleted before returning** (`ls -d` → `No such file or directory`; 16 G free).

⚠ **One self-caught error, recorded rather than hidden:** my first verification block began with `cd /tmp/claude-0/w86/tree`, so the `git status`/`git rev-parse HEAD` inside it reported the **scratch** tree, not live. I re-ran both against live from the repository root (`LIVE_HEAD_END=0d05cb7b…`, `LIVE_STATUS_LINES=0`). The scratch-side reading was still useful (scratch status clean after the run) but it is not the live check it looked like.

Literal output of the required command (start capture; the five long proxy-list variables `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` matched on "proxy"/"java", carry no model information, and are elided here — they were emitted in full in the transcript):

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

W70 executed `scripts/tests systems/tests -n 3` and measured the tracked tree clean before and after, but named the gap: **two snapshots cannot see a write-then-revert window**, which is the actual shape of the AUT-PD-186 defect (a concurrent-reader interval, not a residue). Open because nobody had ever *observed* the writes as they happened in those two ungoverned directories. Does any test there write to a tracked path and put it back inside the run?

**Answer: yes — one, and it is not a tracked path but a path in the tracked-tree *working directory*: `systems/tests/test_systems_check.py::test_a_document_declaring_an_unknown_level_fails` creates `research/d11-probe-DELETEME.md` in the live repository root and deletes it 1.17 s later.** W70's endpoint snapshots are structurally blind to it, and so is the tracked-tree guard, because the file is not in `git ls-files`.

## Prior-work check

Read in full as instructed: `COMMON-BRIEF.md` (all "Known, measured…" blocks through line 747), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W70-ungoverned-test-directories.md`, `reports/W54-xdist-and-mutating-test-census.md`. **`reports/W25-*` was not read, listed, referenced or audited.**

Commands and what they showed:
- `ls scripts/tests/conftest.py systems/tests/conftest.py` → both "No such file or directory" — independently re-confirms "no guard installed at all".
- `rg -n -l "addaudithook" --glob '!.git' --glob '!research/autonomy/opus-capacity-campaign-20260908/**'` → 3 hits: `research/manuscripts/tests/tracked_tree_guard.py`, `research/autonomy/sprint-2026-09-01/S6-COMMITLOOP.md`, `research/autonomy/research-ledger.json`. No record-only observer exists in the tree; the only audit hook is the *refusing* guard.
- `rg -n -il "record-only|newermt" …` → 1 hit (`sprint-2026-09-01/S37-ERROR-BODIES.md`), unrelated. No prior `find -newermt` sweep.
- `grep -rn "atr_hrd_sarcoma_series" scripts/tests systems/tests` → **no hits**; the forbidden bare invocation could not occur through this run.

Consumed rather than re-measured: the pytest-interpreter trap (W29f — `pytest` on PATH, never `python3 -m pytest`), the 0-of-89 resolution rate, the `systems_check` campaign-footprint baseline, W41's tier-budget prediction, W54's guard census, W70's endpoint result. Read code, never docstrings, throughout. No network attempted, so **there is no denial to record**. `scripts/preflight.sh` was neither run nor edited. No CLOSED-WORK item replayed.

## Method and inputs

`cp -a /home/user/Rare-cancers /tmp/claude-0/w86/tree` (986 MB, **including `.git`**). Scratch HEAD `cf0af448f41bf6142fe0689d68f8da1430ad1b55`, scratch `git status --porcelain` **empty**. `git ls-files` → **7,853** tracked paths, loaded as the membership set.

**Instrument — scratch measurement code, record-only, deleted with the scratch.** A pytest plugin module held **outside** the tree (`/tmp/claude-0/w86/auditrec.py`, loaded with `-p auditrec` and `PYTHONPATH`, so no `conftest.py` was added to either directory and the tree was not modified). It calls `sys.addaudithook` at import and:
- logs `open` when `mode` contains `w`/`a`/`x`/`+`, or when `mode is None` and `flags & (O_WRONLY|O_RDWR|O_CREAT|O_TRUNC|O_APPEND)`;
- logs `os.remove`, `os.rename`, `os.replace`, `os.truncate`, `os.link`, `os.symlink`, `os.mkdir`, `os.rmdir`, `os.chmod`, `shutil.copyfile`, `shutil.copymode`, `shutil.copystat`, `shutil.move`, `shutil.unpack_archive`;
- records `(timestamp, event, argument index, repo-relative path, tracked?, pytest nodeid, pid)`, attributing each event to the running test via `pytest_runtest_logstart`;
- **never raises out of the hook and never refuses anything** — the whole body is wrapped in `try/except: return`, there is no allow/deny decision anywhere in it, and it is not bound into any `conftest.py`. It observes; it is not a gate. **I did not install `tracked_tree_guard` over these directories, not even in scratch.**

Paired sweep: `touch -d @T0` marker, then `find . -newer <marker>` over the **whole scratch tree including `.git/`** after the run.

Environment: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, cwd `/tmp/claude-0/w86/tree`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w86/pyc`, `-p no:cacheprovider` (matching W54/W70). Interpreter `/root/.local/share/uv/tools/pytest/bin/python3`, pytest 9.1.1, xdist 3.8.0, pluggy 1.6.0, Python 3.11.15.

Command: `pytest scripts/tests systems/tests -n 3 -p auditrec -p no:cacheprovider`. No `-k`, no `--deselect`, no marker filter, no reordering, no plugin disabled, nothing repaired or weakened.

## Result

### R1 — The run: exit 1, **12 failed / 672 passed / 1 skipped**, one more failure than W70 (`PRIMARY`, RUN)

```
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/claude-0/w86/tree
plugins: xdist-3.8.0
created: 3/3 workers
3 workers [685 items]
============ 12 failed, 672 passed, 1 skipped, 4 warnings in 39.48s ============
PYTEST_EXIT=1
```

**685 collected · 672 passed · 12 failed · 1 skipped · 0 deselected · 0 errors · exit 1 · 39.48 s.**

W70 measured 11 failed / 673 passed at HEAD `56f355f6`. At my HEAD `cf0af448` the count is **12**, and the delta is one named test: `systems/tests/test_systems_check.py::test_a_withdrawal_notice_is_not_a_citation`, which was passing for W70. The other 11 are W70's exact set. This is consistent with the campaign footprint growing by report between the two HEADs (the coordinator collected ~20 more reports in the interval) — **the baseline red in these directories is not a fixed number; it moves with the campaign directory's contents**, which is the same property W31b recorded for `systems_check --check`. I did not counterfactually re-run at a pre-campaign commit, so the attribution of that twelfth failure rests on its family (`[D1]`/`[D4]`/`[K1]`/`[K2]` over collected reports) and on it being absent from W70's list three minutes of campaign-time earlier.

The failed set, verbatim from `grep -E "^FAILED"`:

| Failed test | Attribution |
|---|---|
| `scripts/tests/test_a_tier_budget_is_a_decision_somebody_took.py::test_every_tests_directory_in_the_repository_is_inside_some_budget` | exactly W41's predicted failure (the two capsule `tests/` dirs under `…/inputs/source-index/` in no tier) |
| `systems/tests/test_a_claude_hook_is_not_a_dead_pointer.py::test_no_committed_document_names_a_dead_hook` | campaign-directory prose |
| 10 × `systems/tests/test_systems_check.py::…` — `test_every_hand_written_document_has_frontmatter`, `test_every_document_id_resolves_to_exactly_one_file`, `test_no_new_broken_links`, `test_repo_state_is_clean`, `test_cli_check_exits_zero`, `test_every_cited_and_absent_artifact_is_classified`, **`test_a_withdrawal_notice_is_not_a_citation`**, `test_a_dead_code_pointer_still_fires_after_the_external_allowance`, `test_the_document_schema_is_actually_applied`, `test_a_link_checker_that_strips_the_fragment_proves_the_cheaper_half` | `[D1]`/`[D4]`/`[D6]`/`[K1]`/`[K2]` over collected campaign reports |

**No failure is attributable to my instrument** (the plugin makes no assertions and cannot fail a test), and **none is repaired here.** 1 skipped, in-suite conditional, not induced by me.

### R2 — Record-only observation: **0 writes to any tracked path** (`PRIMARY`, RUN)

**2,139 write-shaped events** were logged inside the scratch tree root across 4 processes (controller + 3 xdist workers): `os.remove` 1168, `os.rmdir` 768, `shutil.copyfile` 84, `shutil.copystat` 61, `shutil.copymode` 25, `open` 18, `os.mkdir` 15.

Two filters, both necessary, and the second is a finding in its own right (R5):

1. **Argument position.** 196 events named a tracked path — **every one of them at `argidx 0` of `shutil.copyfile`/`copymode`/`copystat`, i.e. the copy *source*, a read.** These are exactly W54's hand-audit finding (`shutil.copy(HOOK, tmp_path/…)` copies *out of* the tree) now measured rather than read: `.claude/hooks/*.sh`, `research/autonomy/{autonomy-state,priority-weights,research-ledger,derived-ledger-ids}.json`, `research/autonomy/{learning_rate,out_of_ideas,stuck_clock}.py`, and 19 of the 20 `systems/graph/*.json` files. **Zero tracked paths appear in a destination position.**
2. **Path shape.** 1,934 of 2,139 records carry a single-segment basename with no `/` — the fd-relative artefact described in R5.

After both filters: **205 records with a real multi-segment path, 35 of them in a destination position, and `TRACKED-PATH WRITE DESTINATIONS = 0`.**

**W70's endpoint result is upgraded from "no residue" to "no tracked-path write occurred at all, observed at the syscall boundary."** The remaining 35 destinations are 32 under `.git/` and 3 under `research/` (R3, R4).

### R3 — ⭐ The write-then-revert window exists, and here it is (`PRIMARY`, RUN)

The three non-`.git` destination events, all from one test and one path:

| t (epoch) | event | path | tracked | nodeid |
|---|---|---|---|---|
| 1788843881.4549 | `open` (write) | `research/d11-probe-DELETEME.md` | **False** | `systems/tests/test_systems_check.py::test_a_document_declaring_an_unknown_level_fails` |
| 1788843882.0227 | `open` (write) | `research/d11-probe-DELETEME.md` | **False** | same |
| 1788843882.6285 | `os.remove` | `research/d11-probe-DELETEME.md` | **False** | same |

**Window: 1.1736 s**, single worker pid 27899.

Source, `systems/tests/test_systems_check.py:1645-1670`:
```python
def test_a_document_declaring_an_unknown_level_fails(tmp_path, graph):
    probe = os.path.join(REPO, "research", "d11-probe-DELETEME.md")
    ...
    try:
        with open(probe, "w", encoding="utf-8") as fh:      # :1656
            fh.write(f"---\n{head}level: L9\n---\n\nbody\n")
        ...
        with open(probe, "w", encoding="utf-8") as fh:      # :1663
            fh.write(f"---\n{head}level: L4\n---\n\nbody\n")
        ...
    finally:
        if os.path.exists(probe):
            os.remove(probe)                                # :1669
```
Note the signature takes `tmp_path` **and does not use it for the probe** — the file goes to `REPO`.

**Why every existing instrument is blind to it, and none of this is a repair recommendation:**
- `git status --porcelain` before/after (W70's method, and `assert_tree_unchanged()`'s method) sees nothing: the file exists only inside the window, and the `finally` at `:1668-1669` removes it.
- `research/manuscripts/tests/tracked_tree_guard.py` would **not refuse it even if installed here**: the guard's remit is `git ls-files`, and `research/d11-probe-DELETEME.md` is a **new, untracked** path. This is a genuine coverage statement about the guard's design, not about this test.
- During the 1.17 s window a concurrent reader sees `?? research/d11-probe-DELETEME.md` in `git status`, and any concurrent `systems_check` scan of the document tree sees a live document declaring `level: L9` (then `L4`) with `id: DOC-D11-PROBE`. **That is the concurrent-reader interval shape of AUT-PD-186** — a `git add -A` or a whole-tree scan landing inside the window would pick it up. I make no claim that this has ever happened.

**A second, identical probe exists and did not fire in this run** (`source-derived, NOT OBSERVED`): `systems/tests/test_systems_check.py:1580-1581` builds `REPO/research/modalities/k3-probe-DELETEME.md` under the same `try/finally` shape, inside `test_a_dead_code_pointer_still_fires_after_the_external_allowance`. That test **failed at `:1577`** (`assert [w for w in f.warns if "[K3]" in w] == []`, campaign footprint) — an assertion that precedes the probe block — so the write never executed. ⚠ **The campaign's own red baseline is currently masking one of the two in-repo probe windows from observation.** `grep -rn "DELETEME" scripts/tests systems/tests` returns exactly these two sites and no others.

### R4 — The `.git/` destinations, and the subprocess route (`PRIMARY` for the observed half, `SOURCE-DERIVED` for the rest)

32 in-process destination events under `.git/`, all from `scripts/tests/test_a_promise_with_no_commit_stops_the_turn.py` (W54's single IN-PLACE case): 14 × `os.mkdir .git/emc-hooks`, 16 × `open` (write) `.git/emc-hooks/promised-work-last-head`, 1 × `os.remove` of that file (in `test_a_first_run_with_no_baseline_says_nothing`), plus 1 `os.mkdir` + 1 `open` on `.git/worktrees/wt/emc-hooks/…`. Write sites `:65`, `:84`, `:185`, removal `:201`, rewrite `:210`, as W54/W70 recorded.

**`find -newer` over the whole scratch tree including `.git/` — total drift after the run: 1 file, 3 directories.**
```
d 1788843894.05  ./.git
d 1788843860.54  ./.git/emc-hooks
f 1788843860.55  ./.git/emc-hooks/promised-work-last-head
d 1788843882.62  ./research
```
- The file: `.git/emc-hooks/promised-work-last-head`. I had reset it to the live value `063f00fa086253fb520c60a11fcf62882b3a4647` before the run; after the run it holds `cf0af448f41bf6142fe0689d68f8da1430ad1b55` = the scratch HEAD. **W70's R3 residue reproduces exactly**, at a different HEAD, in an independent copy. (It also reproduced in my earlier single-file smoke run.)
- `./research`'s mtime `1788843882.62` is the `os.remove` of the d11 probe — **the `find` sweep independently corroborates R3's window** even though the file itself is gone. This is the sweep earning its place: a directory mtime is the only filesystem trace a completed write-then-revert leaves.
- `./.git`'s mtime `1788843894.05` (the run's last second) is **not** explained by any in-process event. It is explained by the subprocess route below.

**Subprocess invocations in these two suites, and what each could write — enumerated from source, `SOURCE-DERIVED, NOT OBSERVED` (the in-process hook is structurally blind to all of them):** 56 call sites across 14 files. All but five run with `cwd` inside `tmp_path` or a throwaway `git init` repo. The five that touch the live checkout:

| Site | Command | What it could write, from source |
|---|---|---|
| `test_a_promise_with_no_commit_stops_the_turn.py:232` | `git -C REPO worktree add --detach <tmp>/wt HEAD` | **Writes `<REPO>/.git/worktrees/wt/` (gitdir, commondir, HEAD, index, logs).** Removed at `:288` in a `finally` (`git -C REPO worktree remove --force`). Measured: `.git/worktrees` **does not exist** after the run, while `.git`'s mtime moved to the run's last second — **a second write-then-revert window, this one entirely out-of-process and inside `.git/`.** Invisible to the audit hook (subprocess), to `git status` (git-internal), and to `assert_tree_unchanged()`. |
| `test_a_promise_with_no_commit_stops_the_turn.py:73, 92, 192, 207, 278` | `bash .claude/hooks/promised-work-at-turn-end.sh` | `mkdir -p "$STATE_DIR"` (`:101`) and `printf '%s' "$HEAD_NOW" > "$LAST_HEAD_FILE"` (`:107`) → `.git/emc-hooks/promised-work-last-head`. The **doubly-written path**: same target as the in-process writes above. W70 measured this; I reproduce it. |
| `test_no_hand_authored_json_has_a_duplicate_key.py:65` | `git ls-files --cached --others --exclude-standard -- …` `cwd=REPO` | Read-only enumeration; `ls-files` writes no object and does not rewrite the index. No write idiom in the call. |
| `test_a_tier_budget_is_a_decision_somebody_took.py:44` | `python3 scripts/tier_budget.py <args>` `cwd=ROOT` | `grep` for write idioms (`open(...,'w'/'a'/'x')`, `write_text`, `json.dump(`, `os.remove`, `shutil.`) over `scripts/tier_budget.py` returns **zero hits** — it has no writer. |
| `systems/tests/test_systems_check.py:200` | `python3 systems/systems_check.py --check` `cwd=REPO` | `--check` is the read side; the writer is `write_views(g)` at `:4524`, reached only via `--write-views` (`:4553,4560`). No view regeneration on this path. |
| `test_autonomy_publish_bar.py:360, 364` | `python3 research/autonomy/amendment_guard.py --check-log`; `python3 research/autonomy/publish_bar.py --paper PUB-ASO --sha 000…0` `cwd=str(REPO)` | `amendment_guard.py`'s only `json.dump` calls are to stdout (`:263,274`). ⚠ **`publish_bar.py:170-183` runs `git worktree add --detach <mkdtemp>/tree <sha>` with `cwd=REPO`** — the same `.git/worktrees/` write as row 1 — with `worktree remove --force` **and** `git worktree prune` in its `finally` (`:181-184`). With `--sha 000…0` the `add` fails and the early-return `rmtree` path is taken, so on this invocation the write does not land; **on a resolvable sha it would.** |
| `test_no_detached_background.py:101,110,118` | `python3 .claude/hooks/no-detached-background.py` (no `cwd`, so cwd = rootdir = REPO) | Zero write idioms in the hook. |

**Two of the three writes this run made to the repository directory therefore came through routes an in-process audit hook cannot see**, which is the limit W54 named and W70 measured; the `find` sweep is what recovers them, and it recovers them only as directory mtimes.

### R5 — ⚠ The record-only hook has a false-positive mode, and it is the *same* blind spot as the guard, pointing the other way (`PRIMARY`, RUN — methodological)

**1,934 of 2,139 records (90.4%) carry a bare basename with no path separator** — `.gitignore`, `HEAD`, `config`, `description`, `index`, `codex-handover.json`, `pre-push.sample`, 187 distinct names, most of them loose-object directories (`00`, `05`, `0c07f8…`). These come from `shutil.rmtree` of the tests' temporary git repositories, which unlinks **fd-relative** (`os.unlink(name, dir_fd=…)`). CPython's audit event carries the name but **never the `dir_fd`** — the limitation `tracked_tree_guard.py:246` documents. My hook resolved them with `os.path.abspath`, i.e. against the process cwd, which is the repository rootdir.

Consequence, and it would have been a fabricated finding had I stopped one step earlier: **29 records read as `os.remove` of the tracked file `.gitignore` at the repository root, attributed to 24 named tests in `test_research_ownership.py` and `test_research_run.py`.** They are phantoms — those tests write `(self.repo / ".gitignore")` into `tmp_path` (`test_research_ownership.py:33`, `test_research_run.py:37`), there is **no `chdir` anywhere in either file**, and both the live and scratch `.gitignore` are intact (3810 bytes, mtime `2026-09-08 01:45`, unchanged).

⭐ **The finding for anyone who builds on this:** the relative-path hole is not only a way for a write to *escape* a refusing guard — in a *recording* instrument the identical hole **manufactures tracked-path hits that never happened**, and it does so at 90% of event volume. Any future record-only observer must discard single-segment paths or reconstruct the `dir_fd`, and must separate source from destination argument positions. Both filters were load-bearing here: without them this report would have claimed 196 tracked-path events including 29 deletions of `.gitignore`.

### R6 — What this does not say

Nothing here bears on scientific correctness. No computational result establishes EMC efficacy, safety, selectivity, therapeutic window or clinical readiness. There is no wet lab. No claim here is clinical.

## Validation evidence

**RUN.** Environment as in Method. Exit code captured with `echo "PYTEST_EXIT=$?"` immediately after the command, not through a pipe.
```
$ cd /tmp/claude-0/w86/tree && git rev-parse HEAD
cf0af448f41bf6142fe0689d68f8da1430ad1b55
$ git status --porcelain > status-before.txt   # 0 lines
$ AUDIT_ROOT=… AUDIT_OUT=… AUDIT_TRACKED=… PYTHONPATH=/tmp/claude-0/w86 \
  PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=… \
  pytest scripts/tests systems/tests -n 3 -p auditrec -p no:cacheprovider
3 workers [685 items]
12 failed, 672 passed, 1 skipped, 4 warnings in 39.48s
PYTEST_EXIT=1
$ git status --porcelain > status-after.txt    # 0 lines
$ diff status-before.txt status-after.txt      # STATUS_IDENTICAL
```
Run window `T0=1788843853` → `T1=1788843894` (41 s wall). Audit logs: 4 JSON files (2 B, 9.6 KB, 427 KB, 92 KB).

**RUN — the sweep.** `find . -newer /tmp/claude-0/w86/T0MARK` over the whole scratch tree **including `.git/`** → `COUNT=1 files, 3 dirs`, listed verbatim in R4.

**RUN — instrument smoke test, and it is also evidence.** Before the main run I exercised the plugin on `scripts/tests/test_a_promise_with_no_commit_stops_the_turn.py -n 3` alone: `2 failed, 13 passed in 5.33s`, exit 1, 33 records captured. ⚠ Those two failures (`test_work_that_landed_exempts_a_present_tense_announcement`, `test_the_prose_form_of_a_plan_is_caught_without_a_heading`) **do not occur when the file runs inside the full suite** — the file is sensitive to the pre-existing value of `.git/emc-hooks/promised-work-last-head`, which the suite itself sets. Recorded as an observation about that file's order/state dependence; **no repair authored or proposed.** I then restored the file to the live value `063f00fa…` before the main run so the main measurement started from the live state.

**RUN — live untouched.** Live `git status --porcelain` → **0 lines** at `05:02:06Z` and **0 lines** at `05:07:50Z` (the second reading taken from the repository root after correcting the `cd` error noted in Worker). `diff -rq --exclude=.git /home/user/Rare-cancers /tmp/claude-0/w86/tree` → `DIFF_RC=1`, **9 rows, every one inside `research/autonomy/opus-capacity-campaign-20260908/`**: 7 × `Only in <live>/reports:` (`W76`, `W77`, `W79`, `W80`, `W81`, `W82`, `W83`) and 2 × `differ` (`COMMON-BRIEF.md`, `reports/W14e-fake-guard-triage.md`). Direction proved, not assumed: `diff scratch live` on `COMMON-BRIEF.md` is `783a784,815` — a **pure append of 32 lines on the live side**, zero scratch-side hunks; on `W14e` the only differing line is its collection header timestamp (`03:34:17Z` → `05:06:36Z`, live side). `git log --oneline -3` names the two coordinator commits that produced them (`9a936582` 05:03:52Z, `0d05cb7b` 05:06:50Z). **No file outside the campaign directory differs at all.**

**RUN — live git-internal and probe paths.** Live `.git/emc-hooks/promised-work-last-head` after scratch deletion: 40 bytes, mtime `2026-09-08 03:49:56.559428952 +0000`, content `063f00fa086253fb520c60a11fcf62882b3a4647` — **byte-identical to W70's reading, untouched by me.** `ls` on live `research/d11-probe-DELETEME.md` and `research/modalities/k3-probe-DELETEME.md` → both "No such file or directory".

**PROPOSED (NOT RUN):**
- I did not run at `-n 1` or other worker counts; the observation is at `-n 3` only, and the d11 window is one observation of one duration, not a distribution.
- I did not re-run at a pre-campaign commit, so the twelfth failure's attribution is by family and by absence from W70's list, not counterfactually proved.
- I did not observe any subprocess's writes. Every row of R4's subprocess table except the two `.git/` mtime effects is **source-derived, not observed**.
- I did not install `tracked_tree_guard` over these directories, in scratch or anywhere.
- I did not run `scripts/preflight.sh`, `atr_hrd_sarcoma_series.py`, or any producer directly. No network was attempted.

## Limitations

- **The hook is in-process only.** Every `subprocess.run` in these suites is invisible to it — 56 call sites, five of them against the live checkout. Two of the three writes into the repository directory during this run came through that route, and I recovered them only as directory mtimes.
- **The hook's own false-positive mode is large (R5).** 90.4% of records are fd-relative basenames misresolved against cwd; 29 of them named a tracked file. Both correction filters are mine, applied after the fact, and a different rmtree implementation would produce a different phantom set.
- **`find -newer` sees mtimes, not intervals.** It proved the d11 window happened; it cannot say how long or what the content was. Only the audit log gives 1.17 s, and only the source gives the `level: L9` content.
- **One observation of one run.** A test that writes in place only on a code path this run did not reach is unmeasured — and R3 contains a live example: the `k3-probe` write did not execute because its test failed earlier on campaign footprint.
- **Bytecode and pytest cache suppressed** (`PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX`, `-p no:cacheprovider`), matching W54/W70. A default-configured run would additionally create `__pycache__` and `.pytest_cache`.
- Result is for tracked test files at scratch HEAD `cf0af448`. Tests under `…/inputs/source-index/` are lane-11-owned and were not collected or audited.
- **I authored no patch, diff, gate or test.** The audit plugin was scratch measurement code held outside the tree, never bound into a `conftest.py`, never refusing anything, and deleted with the scratch. I weakened, relaxed and reordered nothing; skipped, deselected and disabled nothing; repaired nothing.
- Nothing here bears on scientific correctness or on any clinical property.

## Stop condition

**Set up front:** return as soon as (a) `pytest scripts/tests systems/tests -n 3` has run to completion in a `cp -a` scratch copy under a record-only `sys.addaudithook`, with the real exit code and counts recorded; (b) every tracked path touched during the run is reported with the test that touched it, restored or not; (c) a `find -newer` sweep over the whole scratch tree including `.git/` is paired with it; (d) the subprocess invocations in those suites are enumerated with what each could write, from source; and (e) live is confirmed untouched and the scratch deleted.

**MET on all five.** (a) exit 1, 12 failed / 672 passed / 1 skipped / 685 collected, 2,139 write-shaped events logged. (b) **0 tracked-path write destinations**; the 196 tracked-path events are all copy *sources*; one write-then-revert window found on an untracked path inside the tracked working tree (`research/d11-probe-DELETEME.md`, 1.17 s, `test_systems_check.py:1645-1669`), plus the known `.git/emc-hooks` residue. (c) sweep run, 1 file + 3 dirs, and it independently corroborated the window via `./research`'s mtime. (d) 56 sites enumerated, 5 against the live checkout, tabulated with their source-derived write surface; a second, out-of-process `.git/worktrees/` window identified. (e) live status empty at start and end, all 9 diff rows live-side campaign gains with direction proved, live git-internal file byte-identical, scratch deleted (16 G free). Returning immediately.

## Tool-call and wall-clock count actually used

**26 tool calls**, **~6 minutes wall clock** (`date -u` 05:02:06Z → 05:07:50Z). Well inside the ~40/~40 target; returning early rather than padding.

## Next concrete action

**One successor, and it is a measurement: close the subprocess half, which is now the only unobserved route left in these two directories.** Re-run `scripts/tests systems/tests -n 3` in a `cp -a` copy with the same record-only plugin, plus an **out-of-process** observer for the same events — a `strace -f -e trace=openat,unlink,unlinkat,rename,renameat2,mkdir,mkdirat -y` around the whole pytest process tree, writing to a log outside the tree, filtered to paths under the scratch root. That is still pure observation, refuses nothing, and would attribute the two `.git/worktrees/` and `.git/emc-hooks/` windows to their exact `git`/`bash` invocations rather than inferring them from a parent-directory mtime, and would catch any subprocess write this run's source reading missed. Roughly 8 tool calls. ⚠ It must carry R5's correction forward: `strace -y` reports the resolved path and so avoids the fd-relative phantom entirely, which makes it the *better* instrument for the tracked-path question as well.

**For the owner of `systems/tests/` (findings only, no repair authored or proposed):**
1. `test_systems_check.py:1647` and `:1581` write probe files into the **live repository working tree** (`research/d11-probe-DELETEME.md`, `research/modalities/k3-probe-DELETEME.md`) rather than into the `tmp_path` that `:1645` already takes as a fixture argument. Both are `try/finally`-restored and leave no residue; both open a concurrent-reader window (measured: 1.17 s for the d11 probe) in which the tree contains an extra untracked document. Neither would be refused by `tracked_tree_guard` if it were installed here, because the paths are untracked.
2. `test_a_dead_code_pointer_still_fires_after_the_external_allowance` asserts on the campaign-footprint-sensitive `[K3]` warn set at `:1577`, *before* its own probe block, so while the campaign directory is present that test's actual subject is never exercised.
