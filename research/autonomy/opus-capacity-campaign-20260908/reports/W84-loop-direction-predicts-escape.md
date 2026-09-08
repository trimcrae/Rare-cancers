<!-- collected 2026-09-08T05:10:27Z by campaign coordinator; agent id aa2adf7937c1efcc1; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aa2adf7937c1efcc1.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

## Worker

**W84** — loop-direction discriminator lane (W74's named successor), OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My context states I am Claude Opus 5, exact ID `claude-opus-5`. Nothing in my environment confirms a served model — `env` carries no model variable. The coordinator must extract the actual per-child runtime model from the transcript.

- `date -u` start `Tue Sep  8 05:01:02 UTC 2026` · end `Tue Sep  8 05:06:33 UTC 2026`.
- `git rev-parse HEAD` start **`49ed4d4e94df6753a7300b893d718583f87a03e3`** · end **`9a936582365c8b46cb69e171d9fcd063c6a6add9`** (HEAD moved under me — coordinator report collection). My `cp -a` scratch copy captured the tree at **`b1f6a6dcc2149b6a8a5ee38ccfc54823c07bb056`**; all measurements pin to that tree.
- `git status --porcelain` in `/home/user/Rare-cancers`: **0 lines at start, 0 lines at end.** I wrote nothing there and ran no git write operation there (only `rev-parse`, `status`, `grep`, `sed -n`, reads). `--write-views`/`--write-view` was **never** run against the live tree. All git writes (`hash-object`, `commit-tree`, `update-ref`, `checkout --`) were inside the scratch copy only.
- All execution under `/tmp/claude-0/w84/`, **deleted before returning** (`SCRATCH_RM_EXIT=0`; `ls` → "No such file or directory"; `/` 15 G free). No network, no paid API, no GPU, no publication. `scripts/preflight.sh` not run. `atr_hrd_sarcoma_series.py` never invoked in any mode. W25 not read, audited, extended or referenced.

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

W74 refined W45's escape discriminator to a fourth value: *a cross-source anchor blocks the regenerate-then-check escape only if the loop is driven from the non-emptied side.* **Does loop direction predict survival?** For the three surviving cross-source families in `systems_check.py` (`[L2]` 89, `[W1]` 18, `[M2]` 16) and the two vacuous ones in `emc_systems_map_check.py` (`[C1]`, `[O4]`): classify the enclosing loop SOURCE-DRIVEN or OTHER-HOME-DRIVEN by reading, then **test the classification by emptying the OTHER home instead** and measuring which families go vacuous and which fire.

## Prior-work check

Read in full as instructed: `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W74-escape-holds-with-git.md`, `reports/W45-regenerate-then-check-census.md`, `reports/W37c-error-family-anchor-census.md`. I took as given and did **not** re-run: W37c's anchor census (89 pairs; 2 VIEW / 35 GRAPH / 28 CROSS / 24 NON-GRAPH), W61's confirmed 18/`[W1]` measurement, W45's escape census, W74's git-present result, the 0-of-89 resolution rate, the `systems_check` campaign-footprint baseline, and the pytest-interpreter trap. **W25 not read or referenced.**

⚠ **One prior-work correction the coordinator needs.** `reports/W58-escape-test-sixteen-modules.md` landed in the live tree *during* my run (it is one of the four files in my end-of-run `diff -rq`). W58 **already settled W45's 16 source-graded modules by execution** — 15 executed, 1 excluded — so the second half of my dispatch ("what it would take to settle them by reading rather than running") is asking about a set that has since been settled by running. I read its Result section rather than duplicating it, and I fold its R7.1 into my verdict below because it independently supports my refutation. My own measurements are new: nobody has emptied the *other* home for either module.

Source reads locating the loops (live tree, read-only): `systems/systems_check.py:1060-1103` (`check_legacy_agreement`), `:1126-1180` (`check_lanes`), `:1180-1225` (`check_requirement_source_agreement`); `research/manuscripts/emc_systems_map_check.py:321-335` (`_tracked_files`), `:395-535` (`[O4]`), `:640-700` (`[C1]`).

## Method and inputs

| Input | Value |
|---|---|
| Source tree | `/home/user/Rare-cancers`, copied at start with `cp -a` **including `.git`** (W74 measured that removing `.git` hides 5 real `[O4]` errors) |
| Scratch | `/tmp/claude-0/w84/repo`, `CP_EXIT=0`, 985 M, `git rev-parse HEAD` = `b1f6a6dc`, in-scratch `git status --porcelain` = **0 lines**, `origin/main` = `0dcb24c0` |
| Environment | `python3`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w84/pyc`, cwd = scratch root |
| Green baseline | W37b/W61's method: `mv research/autonomy/opus-capacity-campaign-20260908` outside the scan root, moved back at the end |
| "Empty the other home" — `[L2]` | recursively replace **every list** in `research/manuscripts/emc-systems-map.json` with `[]` (**195 rows**), graph left fully populated |
| — `[M2]` | delete every `\| **R<n>** \|` row from `research/manuscripts/nr4a3-program-map.md` (**16 rows**), graph intact |
| — `[W1]` | `sed -E 's/\bLANE[- ]([0-9]+)\b/LNXX\1/g'` over the **57** `.md/.py/.json/.yml` files outside `systems/graph/` and `systems/views/` that carry a `LANE-n` mention; `systems/graph/` deliberately untouched so the lane register (`reg`) stays intact — a **partial** emptying, see Limitations |
| — `[C1]` | in scratch only: `git update-ref refs/remotes/origin/main $(git commit-tree $(git hash-object -w -t tree /dev/null))` — the publish ref now resolves to an **empty tree**, registry intact; restored to `0dcb24c0` afterwards |
| — `[O4]` | move the 7 corpus files whose text triggers `[O4]` out of the scan root, `objects` intact |
| — `[O4]` source-side control | set `emc-systems-map.json["objects"] = []` (**19 rows**), corpus intact |
| Restore | byte backups of every mutated file + `tar` of the 57 sed'd files + `git checkout -- systems/views`; verified by `git status --porcelain` = 0 and empty `git diff` |

## Result

### R1 — The static classification, by reading (`PREDICTION` until R2/R3 measured it)

| Family | Enclosing construct (`file:line`) | Iterated over | Class |
|---|---|---|---|
| `[L2]` | `systems_check.py:1092` `for rid, lrow in lg.items()` where `lg = by_id(legacy.get(coll, []))` | legacy registry | **OTHER-HOME-DRIVEN** |
| `[L4]` (sibling) | `:1099` `for rid in set(gr) - set(lg)` | graph | source-driven |
| `[M2]` | `:1203` `for rid in sorted(missing_in_graph)`, `missing_in_graph = set(rows) - set(gr)`, `rows` parsed from the roadmap | roadmap | **OTHER-HOME-DRIVEN** |
| `[M3]` (sibling) | `:1206` `set(gr) - set(rows)` | graph | source-driven |
| `[W1]` | `:1141` `for lid in sorted(set(seen) - reg)`, `seen` built by `os.walk(REPO)` | filesystem sweep | **OTHER-HOME-DRIVEN** |
| `[W2]` (sibling) | `:1145` `for lid in sorted(reg - set(seen))` | `g["lanes"]` | source-driven |
| `[C1]` | `emc_systems_map_check.py:655` `for c in m.get("claims", [])`, reaching out per row via `git_show(publish_ref, path)` | emptied registry | **SOURCE-DRIVEN** |
| `[O4]` | **nested**: `:513` `for obj in disputed` (registry) → `:517` `for path in tracked` (git corpus), behind the early return `:510 if not disputed: return` | **both** | **SOURCE-GATED, OTHER-HOME-SWEPT** |

`[O4]` is the row the dispatch's binary classification cannot express. Its *loop* is other-home-driven; its *gate* is source-driven.

### R2 — ⭐ The inversion measured in `systems_check.py`: direction predicts, exactly (`PRIMARY`, executed)

Green baseline, campaign directory held out, reproduced a fifth time: `systems_check: 620 objects across 15 collections · 0 ERROR · 87 WARN · 7 INFO`, **exit 0**.

| Family | Direction | Graph emptied (W37b/W61, given) | **Other home emptied (this run)** |
|---|---|---|---|
| `[L2]` | other-home-driven | **89 ERROR (survives)** | **0** — vacuous |
| `[L4]` | source-driven | 0 — vacuous | **136 WARN (fires; baseline 47)** |
| `[M2]` | other-home-driven | **16 ERROR (survives)** | **0** — vacuous |
| `[M3]` | source-driven | 0 — vacuous | **16 ERROR (fires)** — the same 16 requirements, mirrored |
| `[W1]` | other-home-driven | **18 ERROR (survives)** | **0** — vacuous |
| `[W2]` | source-driven | 0 — vacuous | **10 WARN (fires; baseline 0)** |

**Every one of the six rows inverted in the direction the source reading predicted, with no exception.** The `[M2]`→`[M3]` mirror is exact at 16.

The escape does **not** open in the mirrored direction either: `--write-views` (rc 0, `wrote 111 view(s)`) followed by `--check` left the histogram **byte-identical** — `19 ERROR · 186 WARN · 7 INFO`, exit 1, still 16 `[M3]`. `write_views` owns only `systems/views/`, so it can author neither side of a graph↔other-home comparison.

⚠ Collateral I caused and must attribute: 3 of the 19 errors are `[K2]`, not a direction result — my `LANE-n` sed rewrote heading text (`LANE 2`, `LANE 14`) inside `nr4a3-program-map.md` and one degrader memo, breaking two same-file `#…lane-2…` anchor slugs. That is my mutation, not a repository defect.

### R3 — ⭐ `emc_systems_map_check.py`: `[C1]` confirms the rule, `[O4]` REFUTES it (`PRIMARY`, executed)

**`[C1]` — source-driven, and it survives emptying the other home.** Green baseline `155 registry items · 0 ERROR · 0 WARN`, exit 0, with `origin/main` = `0dcb24c0` live. Repointing `origin/main` at an empty-tree commit (`1dd54acc`) while leaving the registry fully populated:

```
emc_systems_map_check: 155 registry items · 17 ERROR · 0 WARN        exit 1
ERROR [C1] CLM-IDR-EMC: research/manuscripts/program/emc-post-degrader-options.md quotes
           research/modalities/emc-fet-idr-census.json, which is ABSENT on `origin/main`
```
17 errors, one per claim — the exact mirror of W74's "empty the registry → `[C1]` vacuous". **Prediction confirmed.**

**`[O4]` — the counter-example. It goes vacuous when EITHER side is emptied.** Baseline with the campaign directory in the scan root: `155 registry items · 7 ERROR · 0 WARN`, exit 1, all 7 `[O4]` (this campaign's own footprint — `COMMON-BRIEF.md` plus six reports, two more than W74 saw because the coordinator has since collected more).

| Arm | What was emptied | `[O4]` count | Exit |
|---|---|---|---|
| A0 baseline | nothing | **7** | 1 |
| A1 | **source only** — `objects: []` (19 rows); git corpus 100% intact | **0** | 1 (`[V1]` view drift only) |
| A2 | **other home only** — the 7 naming files removed; `objects` 100% intact | **0** | **0** (`0 ERROR · 0 WARN`) |

A loop-direction predictor classifies `[O4]` by its `for path in tracked` sweep as other-home-driven and therefore predicts it **survives** emptying the registry. It does not: `:510 if not disputed: return` fires first. **The static one-line test is refuted by a measured counter-example.**

### R4 — ⛔ Plain answer: direction predicts survival in `systems_check.py`, and does NOT generalise to a one-line static test

Six of six `systems_check` rows and `[C1]` obey the rule — **7 of 8 families**. `[O4]` breaks it, and it breaks it in the dangerous direction: the naive reading says "this check survives", the execution says it is silent. The defect a one-line test would miss is a check that *looks* anchored in an unemptied corpus and is switched off by a guard three lines above the loop.

The rule that does hold, stated precisely enough to be usable:

> A check is vacuous under emptying a home iff **every** enclosing iteration *and* **every** enclosing early-return guard on the path to its raise site depends on that home. Vacuity is a property of the whole conjunction of gates, not of the innermost loop.

That is a *reachability* predicate, not a one-line pattern. It is decidable statically — a raise-site-to-function-entry path walk over the AST, collecting each `for`/comprehension iterable and each `if …: return` predicate and attributing each to a home — but it is a small static analysis, not a grep, and W37c's own census unit (the `(code, function)` pair) is too coarse for it: `[O4]` and `[C1]` are both "CROSS" and both "cross-anchored", and they behave oppositely.

W58's R7.1, landed independently while I ran, is the same finding from the other end: blockers are *tried in execution order*, so a per-module census reports the **first** blocker, not the strongest. `[O4]` is that phenomenon inside a single check.

### R5 — What it would now take to settle W45's 16 source-graded modules by reading

Largely moot: **W58 settled 15 of them by execution during this campaign** (1 excluded by dispatch), so the cheap answer is "read W58, do not re-derive". For any *future* module, reading alone would suffice only with all of the following, and R3 is the evidence for each:

1. A **guard-path walk**, not a loop classification — every `return`/`continue`/`raise` between function entry and the raise site, with each predicate attributed to a home (`[O4]`).
2. A **regeneration-mode ownership map** — which path prefixes the write mode authors (`write_views` owns `systems/views/` and nothing else); a check survives only if the regenerator cannot author both sides.
3. An **execution-order model**, because an earlier crash or refusal pre-empts a later anchor (W45's `KeyError` case; W58's `emc_prmt5_effect_sizes` refusal).
4. A **degradation-shape parameter**, since "empty every list" is one shape among many and W45 already measured shape-dependence.

Points 3 and 4 are not obtainable by reading at all in the general case. **A static screen can therefore triage but cannot settle; the honest use of R2/R3 is as a cheap prioritiser that names which checks to execute, with `[O4]`-shaped nested gates as its known false-positive class.**

**I authored no repair, no patch, no gate, no test and no floor. No guard was weakened, relaxed, narrowed or reordered. No `DOC_SKIP` entry was added. `write_views`, `main()`'s flag conditional and `check_links`' view inclusion were not touched. `--write-views`/`--write-view` was never run against the live tree. `scripts/preflight.sh` was not run. `atr_hrd_sarcoma_series.py` was never invoked.**

## Validation evidence

**RUN.** All in `/tmp/claude-0/w84/repo` unless stated; `python3` = `/usr/local/bin/python3`; no network attempted, so I have no denial to record; no content-policy refusal occurred.

Scratch provenance: `cp -a /home/user/Rare-cancers /tmp/claude-0/w84/repo` → `CP_EXIT=0`, 985 M, `.git` present, in-scratch `HEAD=b1f6a6dc`, `origin/main=0dcb24c0`, `git status --porcelain` = 0 lines.

Verbatim, `emc_systems_map_check` arms:
```
A0 (campaign in scan root)   A0_EXIT=1   155 registry items · 7 ERROR · 0 WARN     [O4]×7
A1 objects:=[] (19 removed)  A1_EXIT=1   136 registry items · 1 ERROR · 0 WARN     [V1]×1, [O4]×0
A2 7 naming files removed    A2_EXIT=0   155 registry items · 0 ERROR · 0 WARN     [O4]×0
A0b restore                  A0B_EXIT=1  155 registry items · 7 ERROR · 0 WARN
B0 green (campaign held out) B0_EXIT=0   155 registry items · 0 ERROR · 0 WARN
B1 origin/main:=empty tree   B1_EXIT=1   155 registry items · 17 ERROR · 0 WARN    [C1]×17
B0c ref restored 0dcb24c0    B0C_EXIT=0  155 registry items · 0 ERROR · 0 WARN
```
Verbatim, `systems_check`:
```
B0s green baseline           B0S_EXIT=0  620 objects across 15 collections · 0 ERROR · 87 WARN · 7 INFO
   (baseline histogram: [L4]47 [X4]19 [Q4]8 [B5]6 [L5]3 [Q3]2/1 [D5]1 [B9]1 [B3]1 [K1]1 [K0]1)
C1 other homes emptied       C1_EXIT=1   620 objects … · 19 ERROR · 186 WARN · 7 INFO
   ([L4]136 [X4]19 [M3]16 [W2]10 [Q4]8 [B5]6 [L5]3 [K2]3 … ; [L2]0 [M2]0 [W1]0)
C2 --write-views             WRITE_EXIT=0  wrote 111 view(s) to systems/views/
C2 --check                   C2_EXIT=1   620 objects … · 19 ERROR · 186 WARN · 7 INFO  (identical)
```
Degradation counts printed by the mutators: `ROWS_REMOVED 195` (legacy registry), `OBJECTS_REMOVED 19`, `RROWS_DELETED 16`, 57 files sed'd, 7 corpus files moved.

Restoration: byte backups (`bak-map.json`, `bak-map.md`, `bak-roadmap.md`, `bak-lanefiles.tar`) restored; `git checkout -- systems/views`; campaign directory moved back. ⚠ One restore error I caught and fixed: the `tar` of the 57 LANE files was taken *after* the roadmap R-rows were deleted, so untarring re-broke the roadmap — the re-check showed `16 ERROR [M3]`, I re-copied `bak-roadmap.md`, and the final state verified clean. **Final scratch state: `git status --porcelain` = 0 lines, `git diff --stat` empty**, `emc_systems_map_check --check` back at its A0 baseline (`7 ERROR`, exit 1) and `systems_check --check` at its campaign-present baseline (264 ERROR — W31b's footprint family, which grows by one per collected report).

Live-tree isolation: `git status --porcelain` in `/home/user/Rare-cancers` = **0 lines at start and end**; `diff -rq --exclude=.git /home/user/Rare-cancers /tmp/claude-0/w84/repo` = **5 lines, all inside the campaign directory** (an updated `COMMON-BRIEF.md` plus four reports the coordinator collected after my copy: W58, W76, W78, W80). **No file outside the campaign directory differs.** Scratch deleted: `SCRATCH_RM_EXIT=0`, `ls` → "No such file or directory", `/` 15 G free.

**PROPOSED (NOT RUN):** the AST guard-path walk described in R4 (I authored no such tool); a full `[W1]` other-home emptying that also neutralises `LANE-n` inside `systems/graph/*.json`; any degradation shape other than the ones tabulated; any `--check` against the live working tree; re-execution of W58's 16 modules.

## Limitations

- **`[W1]`'s other home was emptied only partially.** I excluded `systems/graph/` from the sed to keep the lane register intact, so nine lane ids remain mentioned in graph JSON and `[W2]` fired 10 rather than the full register. The direction result (`[W1]` 0, `[W2]` 0→10) is unaffected; the magnitude is a floor.
- **3 of the 19 errors in R2 are my own collateral** (broken same-file anchor slugs from the LANE sed), not a directional finding. I attribute them rather than netting them out.
- **"Emptying the other home" is not one operation.** For `[C1]` it was a synthetic empty-tree ref; for `[O4]` it was removing the seven files that trigger it. Both are the smallest faithful analogue of "the other side carries nothing to compare", but neither is the only such analogue, and W45 already measured that shape can change the answer.
- **`[O4]`'s baseline errors are this campaign's own footprint.** A0's 7 and A2's 0 are statements about a scan root containing (or not) campaign reports, not about the repository's tracked content.
- **7 of 8 families is not a population.** These five families were selected *because* W37c/W74 found them interesting. The rule's error rate over all 89 `(code, function)` pairs is UNKNOWN.
- **This is a census of gate arithmetic, not of science.** A gate exiting 0 over an emptied source is a **measurement gap**, not evidence that anything in the repository is wrong today, and it says nothing about EMC efficacy, safety, selectivity, therapeutic window or clinical readiness. Every source I degraded is populated at HEAD (155 registry items, 620 graph objects, 195 legacy rows, 16 roadmap register rows) and every one was restored and re-verified before the scratch tree was deleted. There is no wet lab.
- HEAD advanced during my run (`49ed4d4e` → `9a936582`); measurements pin to the copied tree at `b1f6a6dc`.

## Stop condition

Set up front: **return the moment all five families are classified by source reading and each classification is tested by emptying the other home, with per-code histograms, the live tree verified untouched and the scratch deleted.** **MET**, and it produced a refutation rather than a confirmation, which the dispatch names as the more valuable result. Returned early.

## Tool-call and wall-clock count actually used

**13 tool calls** (several batching many commands; one background `cp -a`). Wall clock **05:01:02Z → 05:06:33Z ≈ 5.5 minutes** — far inside the ~40-call / ~40-minute target.

## Next concrete action

**One successor, and it is a measurement of the rule's error rate, not a tool.** The rule held 7 of 8 times and failed once, in the unsafe direction. The bounded run that would price it: **for all 28 CROSS `(code, function)` pairs in W37c's census, statically record (a) the iterable of every enclosing loop and (b) the predicate of every enclosing early-return guard, predict vacuity under graph-emptying from the conjunction, then check the predictions against W61's already-measured histogram** (`[L2]`89 `[W1]`18 `[M2]`16 `[G2]`13 → 18 all-`[W1]`). That needs no new execution at all — the ground truth is already measured — and it converts "7 of 8" into a real false-negative rate for the `[O4]` shape. If the conjunction predicate scores 28/28 against W61, the screen is worth having as a triage instrument with its limits stated; if it does not, it should be retired rather than published.

**Explicitly not a successor:** any repair, anchor, floor, zero-test or ownership change for either module; any change to `write_views`, `main()`'s `--write-views`/`--no-view-check` conditional, or `check_links`' view inclusion. W37c's named hazard — giving a generator ownership of `emc-systems-map.json` — runs straight through `[L2]`, which my R2 has now shown is the *only* thing standing between an intact graph and an unpoliced legacy registry in that direction too. Also not a successor: re-running W45's 16 source-graded modules, which W58 has already executed.
