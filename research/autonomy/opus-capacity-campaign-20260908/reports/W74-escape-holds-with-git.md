<!-- collected 2026-09-08T05:00:19Z by campaign coordinator; agent id a8d208d54235b4409; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a8d208d54235b4409.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**W74** — regenerate-then-check escape lane (git-present confound settlement), OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My context states I am Claude Opus 5, exact ID `claude-opus-5`. Nothing in my environment confirms a served model — `env` carries no model variable. The coordinator must extract the actual per-child runtime model from the transcript.

- `date -u` start `Tue Sep  8 04:54:04 UTC 2026` · end `Tue Sep  8 04:57:08 UTC 2026`.
- `git rev-parse HEAD` start **`fcb36d3c651223d90b98c0cb64169bb106e6e060`** · end **`129a4e2a1c39352a7a697c42445bb27fc50f9b0c`** (HEAD moved under me — coordinator report collection).
- `git status --porcelain` start: **0 lines**. End: **0 lines**. I wrote nothing into `/home/user/Rare-cancers` and ran no git write operation there (only `rev-parse`, `status`, `show-ref`, `grep`, and reads). `--write-view` was **never** run against the live tree.
- All execution under `/tmp/claude-0/w74/`, **deleted before returning** (`SCRATCH_RM_EXIT=0`; `ls` → "No such file or directory"; `/` 18 G free). No network, no paid API, no GPU, no publication. `scripts/preflight.sh` not run. `research/modalities/atr_hrd_sarcoma_series.py` never invoked in any mode. W25 not read or referenced.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start; the four long proxy-list variables `GLOBAL_AGENT_NO_PROXY`, `NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` are elided only where they repeat the `no_proxy` value verbatim):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
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
GLOBAL_AGENT_NO_PROXY=<same list as no_proxy>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=<proxy/truststore flags; repeats the no_proxy list>
NO_PROXY=<same list as no_proxy>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<same list as no_proxy>
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

W45 measured the full regenerate-then-check escape on `research/manuscripts/emc_systems_map_check.py` — empty all 8 registry sections (195 rows), run its own prescribed remedy `--write-view`, `--check` goes to exit 0 over 0 registry items — **but in a scratch tree with no `.git`**, where the module printed `WARN [C1] none of ('origin/main', …) is present` and `WARN [O4] git is unavailable`. Those two checks were **unavailable, not passing**, so whether the escape holds in a git-present checkout was explicitly UNKNOWN (W37 had the same confound).

**Bounded question: reproduce the three-step sequence in a scratch copy that includes `.git`. Do `[C1]` and `[O4]` become live checks that block the escape, or do they pass and the escape hold regardless?**

## Prior-work check

Read in full as instructed: `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W45-regenerate-then-check-census.md`, `reports/W37-zero-test-coverage-beyond-18-rows.md` (its I1/I2a/I2b sequence and R6), and `reports/W37b-systems-check-regenerate-identity.md` R1–R5 (its green-baseline-by-holdout method, which I reused). W37c's anchor census I take from the brief as given and did not re-derive. **W25 not read, audited, extended or referenced.**

I did not re-measure anything the brief records as settled: the 0-of-89 resolution rate, the `origin/literature-cache` question, the pytest-interpreter trap, the `systems_check` baseline attribution, W37b's `systems_check` result, or W45's other 25 modules. The one thing I deliberately re-ran is W45's own git-less sequence, as the **control** my verdict needs — that is the point of the dispatch, not a replay.

Source reads locating the mechanism (live tree, read-only): `emc_systems_map_check.py:76` (`PUBLISH_REF_CANDIDATES`), `:322-360` (`_tracked_files`), `:405`, `:505-535` (the `[O4]` sweep), `:640-700` (`check_claims`, `[C1]/[C2]/[C3]`).

## Method and inputs

| Input | Value |
|---|---|
| Source tree | `/home/user/Rare-cancers` @ `fcb36d3c` (copied at start) |
| Scratch (git-present) | `cp -a /home/user/Rare-cancers /tmp/claude-0/w74/repo-git` — **`.git` included**, `CP_EXIT=0`, 984 M |
| Scratch (git-absent control) | the *same* tree after `rm -rf .git` — one scratch tree at a time, as the dispatch requires on a disk-constrained container (`/` never below 15 G) |
| Degradation | `empty.py`: recursively replace **every list** in `research/manuscripts/emc-systems-map.json` with `[]` — identical shape to W45/W37; **195 rows removed**, reproducing their number exactly |
| Restore | `bak-map.json` / `bak-map.md` taken before any mutation; verified `diff -q` IDENTICAL and re-checked to baseline exit code after every arm |
| Environment | system `python3`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w74/pyc`, cwd = scratch root |
| Green-baseline method (arm B) | `mv research/autonomy/opus-capacity-campaign-20260908` outside the scan root, W37b's method, then moved back |

Three arms were run:
- **A — git present, tree as-is** (campaign directory in place).
- **B — git present, green baseline** (campaign directory held out), the interpretable arm.
- **C — git absent, tree as-is**, the control reproducing W45/W37's configuration.

Confirmed before any write mode: the module resolves `REPO` from `__file__`, so a copy under `/tmp` writes only under `/tmp`.

## Result

### R0 — The refs actually present in this shallow clone (`PRIMARY`)

`git show-ref` in the live tree returns five refs, and the two the module looks for **both exist**:

```
0dcb24c0c2ec99688b4f686c3998c32913ef1b61 refs/remotes/origin/main
9f861f51afdf23f541d80c7ef41fcb2c6953efa6 refs/heads/main
fcb36d3c651223d90b98c0cb64169bb106e6e060 refs/heads/claude/confident-bardeen-ji76cd
```
`.git/shallow` has **43** graft lines. `origin/main` resolves to `0dcb24c0`, a **different commit from HEAD** — so in a git-present tree `[C1]/[C2]/[C3]` are genuinely cross-*ref* checks (`git_show(publish_ref, path)`), not working-tree reads. This is the strongest form the check can take, and it is the form that ran here.

### R1 — ⭐ The three arms, full ERROR/WARN histograms at every step (`PRIMARY`, all executed)

Counts are the module's own summary line (`N registry items · E ERROR · W WARN`), with per-code histograms from the `ERROR [xx]` / `WARN  [xx]` lines.

| Arm | Step | Command | Exit | Summary line | ERROR histogram | WARN histogram |
|---|---|---|---|---|---|---|
| **A** git present, as-is | 0 baseline | `--check` | **1** | `155 registry items · 5 ERROR · 0 WARN` | `[O4]` 5 | — (none) |
| **A** | 1 | empty every list | — | `ROWS_REMOVED 195` | — | — |
| **A** | 2 | `--check` | **1** | `0 registry items · 1 ERROR · 0 WARN` | `[V1]` 1 | — |
| **A** | 3 | `--write-view` | **0** | `wrote research/manuscripts/emc-systems-map.md` | — | — |
| **A** | 4 | `--check` | **0** | `0 registry items · 0 ERROR · 0 WARN` | **none** | **none** |
| **A** | restore | `--check` | **1** | `155 registry items · 5 ERROR · 0 WARN` | `[O4]` 5 | — |
| **B** git present, green baseline | 0 baseline | `--check` | **0** | `155 registry items · 0 ERROR · 0 WARN` | none | **none** |
| **B** | 1 | empty every list | — | `ROWS_REMOVED 195` | — | — |
| **B** | 2 | `--check` | **1** | `0 registry items · 1 ERROR · 0 WARN` | `[V1]` 1 | — |
| **B** | 3 | `--write-view` | **0** | `wrote research/manuscripts/emc-systems-map.md` | — | — |
| **B** | 4 | `--check` | **0** | `0 registry items · 0 ERROR · 0 WARN` | **none** | **none** |
| **B** | restore | `--check` | **0** | `155 registry items · 0 ERROR · 0 WARN` | none | none |
| **C** git ABSENT, as-is (control) | 0 baseline | `--check` | **0** | `155 registry items · 0 ERROR · 2 WARN` | none | `[O4]` 1 (**unavailable**), `[C1]` 1 (**unavailable**) |
| **C** | 1 | empty every list | — | `ROWS_REMOVED 195` | — | — |
| **C** | 2 | `--check` | **1** | `0 registry items · 1 ERROR · 1 WARN` | `[V1]` 1 | `[C1]` 1 (unavailable) |
| **C** | 3 | `--write-view` | **0** | `wrote research/manuscripts/emc-systems-map.md` | — | — |
| **C** | 4 | `--check` | **0** | `0 registry items · 0 ERROR · 1 WARN` | **none** | `[C1]` 1 (unavailable) |
| **C** | restore | `--check` | **0** | `155 registry items · 0 ERROR · 2 WARN` | none | `[O4]` 1, `[C1]` 1 |

Arm C reproduces W45's and W37's numbers exactly (`0 ERROR · 2 WARN` → `1 ERROR · 1 WARN` → `0 ERROR · 1 WARN`, exit 0), so the two configurations are comparable and the control is sound.

### R2 — ⭐ VERDICT: **ESCAPE HOLDS WITH GIT** (`PRIMARY`)

With `.git` present and `origin/main` resolvable, `[C1]` and `[O4]` are **live and passing, not unavailable** — arm B's green baseline prints **0 WARN**, i.e. neither degradation notice fires — and the same three-step sequence still ends at **exit 0 over 0 registry items with 0 ERROR and 0 WARN**. W45's UNKNOWN is settled in the direction of the escape.

Distinguishing *unavailable* from *passed*, per row, at the green baseline:

| Check | git absent (arm C) | git present (arm B) | After empty + `--write-view` (arm B step 4) |
|---|---|---|---|
| `[C1]/[C2]/[C3]` claim resolution | **UNAVAILABLE** — `WARN [C1] none of ('origin/main', …) is present … checked in the WORKING TREE` | **LIVE and PASSED** — 17 claims resolved against `origin/main` `0dcb24c0` via `git_show`, 0 errors, no warning | **VACUOUS** — `m["claims"]` is `[]`, the loop body never executes |
| `[O4]` unclassified-use sweep | **UNAVAILABLE** — `WARN [O4] git is unavailable, so the unclassified-use sweep did not run` | **LIVE and PASSED** — `git ls-files --cached --others --exclude-standard` returned a real corpus, swept, 0 unclassified uses | **VACUOUS** — `disputed` is `[]`, so `:510 if not disputed: return` fires **before** `_tracked_files()` is ever called |

### R3 — The mechanism, located in source (`PRIMARY`)

Both checks are anchored in *another home* (a git ref; the tracked-file corpus), but **both are iterated over collections that live inside the very file being emptied**:

- `emc_systems_map_check.py:655` — `for c in m.get("claims", []):` — the entire `[C1]/[C2]/[C3]` body is inside this loop. Empty `claims` (17 rows) and the cross-ref comparison has nothing to compare.
- `emc_systems_map_check.py:405` — `disputed = [o for o in m.get("objects", []) if o.get("status") == "identity_disputed"]`, and `:510` — `if not disputed: return`, which precedes `tracked = _tracked_files()` at `:512`. Empty `objects` (19 rows) and the sweep returns before it even asks whether git exists.

This refines W37b/W45's discriminator rather than contradicting it. W37b's surviving `systems_check` families (`[L2]` 89, `[W1]` 18, `[M2]` 16) iterate **the other home** and report items present there but missing from the graph — direction "present elsewhere, absent from the emptied source", which survives. `[C1]` and `[O4]` here iterate **the emptied source** and reach out to the other home per row — direction "present in the source, check it elsewhere", which goes vacuous. **A cross-source anchor blocks the escape only if the loop is driven from the non-emptied side.** That is W37c's "direction decides" result, now measured at single-check resolution on the module W45 could not test.

### R4 — ⚠ Incidental and, in one direction, the opposite of what was assumed (`PRIMARY`, executed, no repair authored)

Two measured facts the coordinator should have, neither of which I acted on:

1. **`emc_systems_map_check.py --check` is RED at HEAD in a git-present checkout of this branch — exit 1, 5 `[O4]` errors** — and every one is this campaign's own footprint, five campaign report files naming `H-EMC-SS` / `HEMCSS` / `ACH-001519` without being classified in `OBJ-LINE-HEMCSS.read_by`:
   `reports/W57-graph-vs-artifact-stale-watchers.md`, `W05-patient-independence-audit.md`, `W05c-identifier-namespace-matrix.md`, `W07d-lane7-vocabulary-stability.md`, `W07h-assumed-composition-rows.md`. Removing the campaign directory takes it to `0 ERROR · 0 WARN`, exit 0 — the same shape W31b measured for `systems_check`. This is measured on a scratch copy at `fcb36d3c`; I did not run `--check` in the live tree. **This is a campaign-footprint artefact, not a defect in the registry, and nothing here is a repository fault to repair.**
2. **Removing `.git` HIDES those five real errors.** The git-less scratch tree that W45 and W37 (and I, in arm C) used reports `0 ERROR · 2 WARN`. The `[O4]` warning is honest about it — it says the sweep "did not run" — but the exit code is 0 either way, so a git-less run of this gate is green over a state a git-present run reddens. Anyone reading a git-less `--check` as a baseline is reading a weaker gate than CI runs.

Also worth recording: at arm A step 4, the emptied-and-regenerated registry produced **0 WARN** — emptying `objects` silences even the module's *own* notice that its sweep is degraded. The state that most needs a warning is the state that prints none.

**I authored no repair, no patch, no gate, no test and no floor. No guard was weakened, relaxed, narrowed or reordered. `write_view`'s ownership was not touched. `--write-view` was never run in the live tree. `scripts/preflight.sh` was not run. `atr_hrd_sarcoma_series.py` was never invoked.**

## Validation evidence

**RUN.** All in `/tmp/claude-0/w74/repo-git`, `python3` + `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/w74/pyc`.

Scratch provenance: `cp -a /home/user/Rare-cancers /tmp/claude-0/w74/repo-git` → `CP_EXIT=0`, `du -sh` 984 M, `.git` present; in-scratch `git rev-parse HEAD` = `fcb36d3c…`, `git rev-parse --verify -q origin/main` = `0dcb24c0…`, `git status --porcelain` = 6 lines (all `??` campaign reports written by the coordinator after my start snapshot; none mine).

Verbatim, arm B (the interpretable arm):
```
=== B-STEP0 baseline ===            B_STEP0_EXIT=0
emc_systems_map_check: 155 registry items · 0 ERROR · 0 WARN
=== B-STEP1 empty ===               ROWS_REMOVED 195
=== B-STEP2 --check ===             B_STEP2_EXIT=1
emc_systems_map_check: 0 registry items · 1 ERROR · 0 WARN
ERROR [V1] research/manuscripts/emc-systems-map.md differs from what the registry generates -- it was hand-edited or the registry moved. Regenerate with --write…
=== B-STEP3 --write-view ===        B_STEP3_EXIT=0    wrote research/manuscripts/emc-systems-map.md
=== B-STEP4 --check ===             B_STEP4_EXIT=0
emc_systems_map_check: 0 registry items · 0 ERROR · 0 WARN
=== B-RESTORE ===                   B_RESTORE_EXIT=0
emc_systems_map_check: 155 registry items · 0 ERROR · 0 WARN
```
Verbatim, arm C control (git absent):
```
RM_GIT_EXIT=0                       C_STEP0_EXIT=0
emc_systems_map_check: 155 registry items · 0 ERROR · 2 WARN
WARN  [O4] git is unavailable, so the unclassified-use sweep did not run -- a NEW file reading a disputed-identity model would not be caught in this environment
WARN  [C1] none of ('origin/main', 'refs/remotes/origin/main', 'main') is present in this checkout -- claim artifacts were checked in the WORKING TREE, which is weaker th…
C_STEP2_EXIT=1  0 registry items · 1 ERROR · 1 WARN
C_STEP3_EXIT=0  wrote research/manuscripts/emc-systems-map.md
C_STEP4_EXIT=0  0 registry items · 0 ERROR · 0 WARN → summary line reads `0 ERROR · 1 WARN`; the one WARN is [C1]
C_RESTORE_EXIT=0  155 registry items · 0 ERROR · 2 WARN
```
Arm A verbatim is in R1; arm A restore returned to its own baseline (`exit 1, 5 [O4]`), arms B and C to theirs (`exit 0`).

Restoration and isolation: `diff -q` of the scratch map JSON and MD against the pre-mutation backups → IDENTICAL in every arm; the held-out campaign directory moved back (`CAMPAIGN_RESTORED=0`). Live tree: `diff -q` of `/tmp/claude-0/w74/bak-map.json|.md` (taken from the live tree) against `research/manuscripts/emc-systems-map.json|.md` → **`LIVE_MAP_UNCHANGED`**; `git status --porcelain` in `/home/user/Rare-cancers` → **0 lines at start and 0 lines at end**. Scratch deleted: `SCRATCH_RM_EXIT=0`, `ls /tmp/claude-0/w74` → "No such file or directory", `/` 18 G free.

**No network of any kind was attempted, so I have no denial to record. No `git fetch` was run.** No content-policy refusal occurred.

**PROPOSED (NOT RUN):** the same git-present re-test for W45's other three executed escapes (`emc_fet_idr_census`, `atm_status_atri_stratification`, `emc_atr_vulnerability` — W45 states these do not consult git, so the confound does not apply and I did not spend a run confirming it); any degradation shape other than "empty every list"; a per-section emptying that would isolate which single section (`claims` vs `objects`) each check depends on; any run of `--check` against the live working tree.

## Limitations

- **"Escape" means escape against exactly the degradation I ran** — every list emptied, 195 rows. A different degradation shape (e.g. emptying `artifacts` but keeping `claims`) would leave `[C1]` non-vacuous and is untested; W45's `emc_fet_frame_and_composition` `KeyError` case shows shape can change the answer.
- **`origin/main` at `0dcb24c0` is whatever this shallow clone last fetched.** The `[C1]` pass at arm B's baseline is a pass against *that* ref, not against the true remote head; the clone is shallow (43 grafts) and I did not fetch. Had the ref been absent — a state the module itself warns about — `[C1]` would have degraded to a working-tree read exactly as in arm C.
- **My `[O4]` "LIVE and PASSED" for arm B is a pass over the corpus minus the held-out campaign directory.** With the campaign directory in place (arm A) `[O4]` is live and *failing*, 5 errors. Both are true statements about different scan roots; neither is a statement about the repository's tracked content, which is what arm B isolates.
- **This is a census of gate arithmetic, not of science.** A gate reporting OK over an emptied registry is a **measurement gap**, not evidence that anything in the repository is wrong today, and it says nothing about EMC efficacy, safety, selectivity, therapeutic window or clinical readiness. The registry is fully populated at HEAD (155 items) and was restored and re-verified in every arm before deletion. There is no wet lab.
- HEAD advanced during my run (`fcb36d3c` → `129a4e2a`); every measurement pins to the tree as copied at `fcb36d3c`.
- I ran the `systems_check` comparison not at all — W37b's result is cited as given, not re-measured.

## Stop condition

Set up front: **return the moment the three-step sequence has been executed with full ERROR/WARN histograms in both a git-present and a git-absent scratch copy, `[C1]` and `[O4]` are each classified unavailable / passed / vacuous at each step, and the live tree is verified untouched with scratch deleted.** **MET.** Three arms rather than the two required (the green-baseline arm B was added because arm A's baseline was red for a campaign-footprint reason and would otherwise have been uninterpretable). Returned early.

## Tool-call and wall-clock count actually used

**16 tool calls** (several batching many commands). Wall clock **04:54:04Z → 04:57:08Z ≈ 3 minutes**, far inside the ~40-call / ~40-minute target.

## Next concrete action

**One successor, and it is a measurement, not a repair.** W45's discriminator is now four-valued, and the newly separated value is the useful one: *loop direction*. The bounded run that would convert this into a general instrument is — **for each of the surviving cross-source error families in `systems_check.py` (`[L2]` 89, `[W1]` 18, `[M2]` 16) and each vacuous one here (`[C1]`, `[O4]`), read the enclosing loop and classify it as driven from the regenerable source or from the other home, then confirm the classification predicts survival by emptying the *other* home instead.** If direction predicts survival in both modules, the repository has a one-line static test for whether any given check is escapable, which is cheaper than W45's per-module execution census and would settle her 16 source-graded modules by reading rather than running.

**Explicitly not a successor:** any repair, anchor, floor, zero-test or ownership change for `emc_systems_map_check.py`. Whether `[C1]` should iterate `artifacts` from the git ref rather than `claims` from the registry is a maintainer's decision about what the registry is for, and the brief's named hazard — giving the regenerator ownership of `emc-systems-map.json` — runs directly through this file. The 5 live `[O4]` errors in R4 are the campaign's own footprint and belong to the coordinator's cleanup, not to a code change.
