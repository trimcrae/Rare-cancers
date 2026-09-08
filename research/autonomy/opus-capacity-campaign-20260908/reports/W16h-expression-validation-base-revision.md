<!-- collected 2026-09-08T03:47:01Z by campaign coordinator; agent id a84ac3e586d683243; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a84ac3e586d683243.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

**W16h**, LANE 16 sixth refill — successor to W16g, dispatched at its named next action: resolve the `expression_validation_readiness` residual.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My system context states I am powered by Opus 5, exact model ID `claude-opus-5`. I did not observe the served model and do not assert it as fact. No environment variable in this container names a served model.

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 03:40:18 UTC 2026` | `Tue Sep  8 03:42:42 UTC 2026` |
| `git rev-parse HEAD` | `5ae0fa04ff9516ac8f820381079d644a094f4a77` | `5ae0fa04ff9516ac8f820381079d644a094f4a77` |
| `git status --porcelain` | **empty** (first observed at 03:41Z, immediately before the only command that executed repository code; see Limitations) | **empty** |

**HEAD did not move under me.** Both inputs I measured re-hashed identically at end (`emc-expression-panels.json` = `123bd05a…`, `primary-marker-evidence.json` = `f79884ce…`). `git rev-list --count HEAD` was **349** at start (W16g saw 346; the coordinator committed three reports in between).

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (piped through `cut -c1-90`; the truncated proxy/truststore lines contain no model identity):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com
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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 -Djavax.net.ss
NO_PROXY=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.ant
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

---

## Stop condition (stated up front)

Return the moment all three hold: (1) the existence status of `8c1f2925…` is settled as one of "never existed here" / "existed and is now unreachable in this checkout" / UNKNOWN, with the shallow-clone caveat honoured; (2) the inertness interval of `--check` is measured or explicitly UNKNOWN; (3) the cluster is stated as exactly 7 or exactly 8, with the conditional made explicit.

**All three hold, and (3) is now unconditional. Stop condition MET.**

---

## Question

**Did `8c1f292536b7d725186491b42c19c87c0b6c855c` ever exist in this repository, how long has `expression_validation_readiness.py --check` been inert, and does that make the `emc-expression-panels.json` drift cluster exactly 7 or exactly 8?**

Open because W16g bounded the cluster at 7-of-at-most-8 with this module as the single named residual, unmeasurable because its hard-pinned `BASE` is absent from the object database.

---

## Prior-work check

Read in full: `COMMON-BRIEF.md` (corrected 03:36Z), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W16g-unmeasured-panel-consumers.md`; head of `reports/W16f-gse24369-drift-diagnosis.md`. **W25 not read, referenced or touched.**

```
rg -n -l "expression_validation_readiness|8c1f292536b7d725" --glob '!.git' \
   --glob '!research/autonomy/opus-capacity-campaign-20260908/**' .
git ls-files | rg -i "local-source-history|expression.validation.readiness"
grep -rl "8c1f292536b7d725186491b42c19c87c0b6c855c" /tmp/claude-0/frozen-corpus/extracted/corpus/
```

17 tracked non-campaign files name the module or the revision. **The decisive one nobody had opened is `research/autonomy/cycle-outcomes/20260905T111908Z-083a73575a/local-source-history.bundle`** — a tracked Git bundle. `CLOSED-WORK.md` closes nothing here. I did not replay W16f's or W16g's measurements; I re-derived only the two input hashes my conclusion rests on.

**Corpus note:** the frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/corpus/` contains the cycle-outcome directory but **not** `local-source-history.bundle` (nor the `*.log`/`round-1.jsonl` binaries). A worker searching only the corpus would conclude the recovery route does not exist. It does; it is in the live checkout.

---

## Method / inputs

Read-only on `/home/user/Rare-cancers`. **No git write operation of any kind was run against the live repository**, and no file under it was created, edited or deleted (`git status --porcelain` empty at end; the live `.git` still returns `could not get object info` for `8c1f2925…` and holds **0** `readiness-source` refs).

The one execution used a **scratch object store**: `cp -a /home/user/Rare-cancers/.git /tmp/claude-0/w16h/gitdir` (367 MB), the bundle fetched into *that* copy, then the module run with `GIT_DIR=/tmp/claude-0/w16h/gitdir` so its `subprocess.check_output(["git","show",f"{BASE}:{path}"], cwd=ROOT)` resolved against scratch objects while reading the live tree's artifacts. Same `GIT_DIR` technique W16g used for `surface_address_sensitivity`.

**Before running it I confirmed from source that `--check` writes nothing** (`expression_validation_readiness.py:335-349`): `path.write_bytes(...)` is reachable only under `if args.write:`; the `--check` branch is `elif path.read_bytes() != content...: raise SystemExit(...)`. `--write` and `--check` are a `required=True` mutually exclusive group, so no mode is the default. `atr_hrd_sarcoma_series.py` was not invoked at all. `scripts/preflight.sh` not run. No network, no paid API, no GPU. `python3` 3.11.15, `PYTHONDONTWRITEBYTECODE=1`.

Scratch deleted before returning: `rm -rf /tmp/claude-0/w16h` → `ls` gives `No such file or directory`; free space unchanged at 18 G available / 20 G used.

---

## Result

### 1 · Did `8c1f2925…` ever exist in this repository? — **IT EXISTS. Answer: "existed, and is present in the tree as a bundled object, but is unreachable from the object database of this checkout."** · PRIMARY

W16g's inference was reasonable and **wrong on the strongest reading**, for a reason W16g's own evidence contained: the clone is shallow.

| Probe | Result | Mark |
|---|---|---|
| `cat .git/shallow` | **42 graft points**, including `14a3f172d6b494d872f6d2678c7d0caa7ef26ccc` at line 4 | PRIMARY |
| Consequence | **`14a3f172` is a shallow graft boundary, not the repository root.** W16g's "root `14a3f172`, 346 commits" is a *truncation floor*, not a full history. `git log` bottoms out at `2026-09-04 00:34:12` — four days of history, for a project whose artifacts date to August. | PRIMARY |
| `git cat-file -t 8c1f2925…` (live) | `fatal: git cat-file: could not get object info` | PRIMARY |
| loose object / all 4 pack `.idx` | absent from all five | PRIMARY |
| reachable from any ref? | 5 refs, none contains it | PRIMARY |
| `git reflog --all` (97 entries, 6 log files) | never mentioned | PRIMARY |
| **`git bundle verify …/local-source-history.bundle`** | **`is okay`** — `contains 8c1f292536b7d725186491b42c19c87c0b6c855c refs/heads/codex/readiness-source-20260905`; `requires 0e5ff28c176b78c6487e1e778483306428229e9b` | **PRIMARY** |
| Is the prerequisite here? | `git cat-file -t 0e5ff28c…` → **`commit`**, and `git merge-base --is-ancestor 0e5ff28c HEAD` → **is an ancestor of HEAD** | PRIMARY |
| bundle sha256 | `1e845ad27a37360d4923acfc115bfb7943af9a317d98e95aea0a807b25b1ab39` — **matches** `source-history.json` exactly | PRIMARY |

**So the commit is not lost. It is committed to this repository as a bundle, its prerequisite is already in this clone, and it restores with one local, offline `git fetch` — the exact `restore_command` recorded in `source-history.json`.** After restoring into scratch: `git cat-file -t` → `commit`; author **Codex**, `2026-09-05 07:19:03 -0400`, subject *"Apply user-authorized immediate research restart"*, on `refs/heads/codex/readiness-source-20260905`, three commits past `0e5ff28c`.

**Why it is absent from the ref graph — and this is the load-bearing structural fact:**

```
git merge-base --is-ancestor 8c1f2925 <ref>
  HEAD                        -> NOT ancestor
  refs/remotes/origin/main    -> NOT ancestor
  refs/heads/main             -> NOT ancestor
  81db6f24 (the commit that added the module) -> NOT ancestor
```

`8c1f2925…` is on a **side branch that was never merged and never pushed**. `source-history.json` says so in its own words: *"Preserves exact local source Git objects for pinned generator after authenticated connector synchronization; normal clone has prerequisite commit."* The runner-receipt confirms it ran on a different machine — `"worktree": "C:\\Projects\\EMC-Research\\..."`, model `gpt-6-astra`. The bundle was the author's deliberate remedy for exactly this: a pin to a commit that would otherwise be unreachable off that Windows clone.

**On the shallow clone specifically:** I did *not* need to resolve whether the shallow graft hides `8c1f2925…`, and I do not claim it does — the bundle settles existence positively and independently. But the shallow finding stands as a correction: **no absence conclusion about any pre-2026-09-04 object may be drawn from this clone's `git log`.** W16g's "346 commits with root `14a3f172`" should not be relied on as a history.

### 2 · How long has `--check` been inert? — **Since the module first landed: `81db6f24`, 2026-09-05 07:50:51 -0400. ~3.0 days as of 2026-09-08T03:42Z.** · PRIMARY

| Evidence | Value |
|---|---|
| Only commit touching `expression_validation_readiness.py` in available history | `81db6f24d2e47bfbc8f9da24e7c8d65780ebf803`, Tristan Drake McRae, `2026-09-05 07:50:51 -0400`, *"Preserve verified EMC CHRNA6 readiness resource and restart research"* |
| Same commit also added | `local-source-history.bundle` — module and its recovery route landed **together** |
| `git cat-file -e 8c1f2925:research/modalities/expression_validation_readiness.py` | **`absent-at-BASE`** — the module does not exist at its own pinned base |
| `BASE` reachable from `81db6f24`? | **NOT ancestor** |

**The interval is not "since the revision went missing" — the revision was never in the mainline to go missing from.** `--check` has been inert in every clone of this repository from the module's first commit onward, because the pin was always to an unmerged local branch. It has never once been runnable in a plain clone; it has always been runnable after the one documented offline restore.

**Was it ever green?** Yes, on the author's machine and once here. Three independent records agree, and my run reproduces all of them:

| Source | `expression-validation-readiness.json` | `.md` |
|---|---|---|
| `metadata-repair-check.log` (mode `check`, 2026-09-05) | `0031e135…` | `bf0626b3…` |
| `coordinator-repair.json` `final_artifact_sha256` | `0031e135…` | `bf0626b3…` |
| **my run, 2026-09-08, exit 0** | **`0031e135…`** | **`bf0626b3…`** |

(`check-2.log` shows `.md` = `38deddd6…`, the pre-frontmatter body; `coordinator-repair.json` records the D4 frontmatter addition, `"memo_body_unchanged": true`. That accounts for the one differing hash.)

### 3 · What `--check` compares, and the cluster · PRIMARY

**What it compares (source, `main()` at line 335 and `Audit.__init__` at line 57):** it rebuilds `expression-validation-readiness.json` and `.md` in memory from **six blobs read via `git show BASE:<path>`**, and compares each **byte-for-byte against the committed artifact on disk**. It is an output-freshness check on its own two artifacts.

**Its inputs never come from the working tree.** `emc-expression-panels.json` reaches it only as `git show 8c1f2925:research/modalities/emc-expression-panels.json`. **Therefore no edit to the working-tree panel can ever change what this module produces, and it can never register panel drift** — precisely the silent-staleness defect `W24b-r07-r08-either-or.md:217` already recorded ("**the staleness is SILENT**… after C3, `--check` **still passes**"). W24b diagnosed the mechanism three days ago; W16g met the same code from the other side, and the two now meet.

**Measured, not inferred — the actual run:**

```
$ GIT_DIR=/tmp/claude-0/w16h/gitdir PYTHONDONTWRITEBYTECODE=1 timeout 600 \
    python3 research/modalities/expression_validation_readiness.py --check
{"base_revision": "8c1f292536b7d725186491b42c19c87c0b6c855c", "cohort_rows_including_alias": 5,
 "decision": "no_go_for_expression_comparison_with_current_allowed_inputs", "input_files": 6,
 "mode": "check", "output_sha256": {
   "research/modalities/expression-validation-readiness.json": "0031e135…9eb12",
   "research/modalities/expression-validation-readiness.md":   "bf0626b3…4aae55"},
 "source_pointers": 1175, "status": "PASS"}
EXIT=0
```

⭐ **The residual is measured, and the cluster is EXACTLY SEVEN — unconditionally, by two independent arguments.**

- **Empirically:** with `BASE` resolved, `--check` **PASSES, exit 0**. It is not a DIFFERS. It is not an 8th member.
- **Structurally, and this is the stronger argument:** it reads the panel only at a frozen revision, so it is *incapable* of membership in a working-tree drift cluster in either direction. Its verdict would be PASS whatever the committed panel said.

W16g's "bounded above by eight" resolves downward. **The `emc-expression-panels.json` drift cluster is 7 committed artifacts: `emc_proteostasis_read`, `emc_prmt5_route_controls`, `emc_mtap_locus_persample`, `emc_hypoxia_confounds`, `emc_prmt5_effect_sizes`, `emc_prmt5_multiplicity`, `emc_mtap_prmt5_figures`.** No unknowns remain in the accounting.

### 4 · A finding for the drift owner that I did not go looking for · PRIMARY

All six pinned inputs at `8c1f2925…` are **byte-identical to the working tree today**:

| Input | sha256 at BASE (from `plan.json`, confirmed by `git show BASE:… \| sha256sum`) | working tree today |
|---|---|---|
| `emc-expression-panels.json` | `123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9` | **identical** |
| `emc-expression-panels-inputs.json` | `6a4f778a…f1f3a8` | **identical** |
| `emc-cohort-search.json` | `f730d8d4…6c8d2` | **identical** |
| `emc-fourth-cohort-quant.json` | `1769b3f0…638f2` (`…4638fcf5165`) | **identical** |
| `emc-fourth-cohort-quant-inputs.json` | `bdb38ded…f24bbf` | **identical** |
| `primary-marker-evidence.json` | `f79884ce…4ec39c` | **identical** |

**The panel frozen at `BASE` is `123bd05a…` — W16g's "now" hash, the *new* side of the drift, the same side `surface-address-sensitivity.json` records as its parent.** So a third committed artifact independently timestamps the panel on the new side, from an authenticated external runner on 2026-09-05, while `mtap-prmt5-figure-provenance.json`'s stamp (`38233b8e…`) sits alone on the old side. That is additional decision evidence pointing the same way W16f's stamp-gap evidence pointed.

**I am not deciding which side is stale.** I did not repoint `BASE`, did not add or propose any guard, did not author a patch, and touched none of the seven drifting artifacts. **No clinical claim of any kind:** everything above is internal file-consistency measurement over committed artifacts. There is no wet lab; nothing here bears on EMC efficacy, safety, selectivity, therapeutic window or clinical readiness. The module's own scientific verdict is unchanged and remains `no_go_for_expression_comparison_with_current_allowed_inputs`.

---

## Validation evidence

**RUN.** All in `/home/user/Rare-cancers` (read-only) or `/tmp/claude-0/w16h/` (deleted). `python3` 3.11.15, `git` on PATH, no network.

| # | Command | Exit | Key output |
|---|---|---|---|
| 1 | `date -u; git rev-parse HEAD; git rev-list --count HEAD` | 0 | `03:40:18Z`; `5ae0fa04…`; **349** |
| 2 | `cat .git/shallow \| grep -c .` ; `grep -n 14a3f172 .git/shallow` | 0 | **42**; hit at **line 4** — the clone IS shallow |
| 3 | `git cat-file -t 8c1f2925…` (live) | **128** | `fatal: git cat-file: could not get object info` |
| 4 | `ls .git/objects/8c/1f2925…` ; `git verify-pack -v` ×4 `\| grep -c ^8c1f2925` | 2 / 0×4 | absent loose and from all four packs |
| 5 | `git for-each-ref` ; `git reflog --all \| wc -l` | 0 | 5 refs, none contains it; 97 reflog entries, no mention |
| 6 | `grep -rn 8c1f2925 --exclude-dir=.git .` | 0 | 17 tracked non-campaign files, incl. `plan.json`, `source-history.json`, `expression_validation_readiness.py:18` |
| 7 | `sha256sum local-source-history.bundle` | 0 | `1e845ad2…1ab39` — **matches** `source-history.json` |
| 8 | **`git bundle verify …/local-source-history.bundle`** | **0** | **`is okay`**; contains `8c1f2925… refs/heads/codex/readiness-source-20260905`; requires `0e5ff28c…` |
| 9 | `git cat-file -t 0e5ff28c…` ; `git merge-base --is-ancestor 0e5ff28c HEAD` | 0 / 0 | **`commit`**; **is an ancestor of HEAD** |
| 10 | `git log … -- expression_validation_readiness.py` and `-- local-source-history.bundle` | 0 | both: **`81db6f24…` `2026-09-05 07:50:51 -0400`**, one commit |
| 11 | `git log --date=iso \| tail -3` | 0 | history bottoms out `2026-09-04 00:34:12` at the graft `14a3f172` |
| 12 | `sha256sum` the six pinned inputs (live tree) | 0 | all six **equal** `plan.json`'s `input_sha256`; panel = `123bd05a…` |
| 13 | `grep -n "write_bytes\|args.write\|add_mutually" …readiness.py` + read `main()` | 0 | `write_bytes` reachable **only** under `if args.write:` — `--check` provably non-writing |
| 14 | `cp -a .git /tmp/claude-0/w16h/gitdir` (scratch) | 0 | 367 MB copied |
| 15 | `git --git-dir=<scratch> fetch <bundle> refs/heads/codex/readiness-source-20260905:…` | **0** | `* [new branch] codex/readiness-source-20260905` |
| 16 | `git --git-dir=<scratch> cat-file -t 8c1f2925…` ; `log -1` | 0 | **`commit`**; `Codex`, `2026-09-05 07:19:03 -0400`, *"Apply user-authorized immediate research restart"* |
| 17 | `git --git-dir=<scratch> merge-base --is-ancestor 8c1f2925 <4 refs>` | — | **NOT ancestor** of HEAD, `origin/main`, `main`, `81db6f24` |
| 18 | `GIT_DIR=<scratch> git show 8c1f2925:…/emc-expression-panels.json \| sha256sum` | 0 | **`123bd05a9f9f5d08…f336bd9`** — the panel at BASE = today's panel |
| 19 | `GIT_DIR=<scratch> git cat-file -e 8c1f2925:…/expression_validation_readiness.py` | 128 | `exists on disk, but not in '8c1f2925'` — **module absent at its own base** |
| 20 | **`GIT_DIR=<scratch> … python3 expression_validation_readiness.py --check`** | **0** | **`"status": "PASS"`**, `source_pointers: 1175`, output hashes `0031e135…` / `bf0626b3…` |
| 21 | `git status --porcelain` immediately before and after #20 | 0 | **empty both times** — the run wrote nothing |
| 22 | live `git cat-file -t 8c1f2925…`; `for-each-ref \| grep -c readiness-source` | 128 / — | still absent; **0** refs — live `.git` unmodified |
| 23 | `date -u; git rev-parse HEAD; git status --porcelain` (end) | 0 | `03:42:42Z`; **`5ae0fa04…` unchanged**; status **empty** |
| 24 | `rm -rf /tmp/claude-0/w16h; ls -d`; `df -h /` | — | `No such file or directory`; 18 G free |

**PROPOSED (NOT RUN):** (a) `emc_surface_normal_window.py` with HPA reachable, then diff — still the only way its identity can be measured (W16g's finding, unchanged); (b) a check of whether `8c1f2925…` exists on the origin remote — not run, no network, and unnecessary since the bundle settles existence locally.

---

## Limitations

- **`git status --porcelain` was first observed at 03:41Z**, one minute into the run and immediately before the only command that executed repository code — not at 03:40:18Z with the first `date -u`. The tree was clean then and clean at end; I state the gap rather than imply a start-of-run observation I did not make.
- **I proved the commit exists in a bundle; I did not prove it exists in the origin remote's ref graph.** Whether `origin` holds `codex/readiness-source-20260905` is **UNKNOWN** (no network was used). The four `merge-base` results show it is not an ancestor of any ref this clone has.
- **I did not resolve whether the shallow graft additionally hides it.** The bundle made that unnecessary. The shallow correction stands on its own: this clone's history is truncated at 2026-09-04, and W16g's "root `14a3f172`" is a graft point.
- **The `--check` PASS was obtained with a restored object store**, not in a default clone. In a default clone the command still exits 1 on `CalledProcessError`. The measurement establishes what `--check` *does when BASE resolves*, which is exactly the conditional W16g named — and it removes the conditional.
- **`--check` is an output-freshness check against frozen inputs, not a drift detector.** Its PASS says its two artifacts still match what those six frozen blobs produce. It says nothing about whether the frozen blobs are current. That silent-staleness property is a real defect, already recorded by W24b; **I did not repair it, propose a repair, or author a patch.**
- **I re-derived only two of W16f/W16g's measurements** (the panel hash and `primary-marker-evidence`). The six drifting modules from W16f and the 7th from W16g are taken as they measured them; I did not re-run them.
- **The frozen corpus omits the bundle**, so corpus-only searches cannot reproduce my central finding. Not an error in the corpus — binaries were excluded by selection — but a real transfer limit.
- **No clinical, efficacy, safety, selectivity, prognosis or readiness claim** is made or implied. Nothing here touches the `bishop2019` per-pool clause. **I did not decide which side of the panel drift is stale**, and added no guard to any of the seven red artifacts.

---

## Stop condition

Stated up front; **MET**, and met more strongly than scoped. (1) Existence settled **positively** — the commit is preserved in a tracked bundle whose prerequisite is already here, and the shallow clone's silence was not promoted to absence. (2) Inertness measured: **since `81db6f24`, 2026-09-05 07:50:51 -0400, ~3.0 days — the module's entire life**, because the pin was always to an unmerged branch. (3) The cluster is **exactly 7**, unconditionally, by both an executed `--check` (exit 0, PASS) and a structural argument that does not depend on the run. Returning now.

---

## Tool-call and wall-clock count actually used

**14 tool calls** (all Bash; several batched two-at-a-time in parallel; none denied). **Wall clock 03:40:18Z → 03:42:42Z = 2 min 24 s** of measurement, plus brief reading and report drafting. Well inside the ~40/~40 target; returning early rather than padding.

---

## Next concrete action

**Report to the owner of `research/modalities/expression_validation_readiness.py`, as a diagnosis for their decision, not as a repair:** the module's `--check` has been inert in every clone since it landed, because `BASE = 8c1f2925…` names an **unmerged, unpushed local branch tip**; it is recoverable offline with the one-line `restore_command` already recorded in `source-history.json`; and once recovered it **PASSES**. Two decisions are theirs, and both are genuinely open: (a) whether the pin should be to a reachable mainline commit, given that all six pinned blobs are currently byte-identical to the working tree — a change that would convert a silent-staleness surface into a live one, and which W24b already identified as the deeper defect; (b) whether `preflight` should restore the bundle so the check is runnable, or whether a check that cannot run is worse than no check. **Explicitly not the next action:** repointing `BASE`, restoring the bundle into the live repository, or adding any identity guard to the seven drifting artifacts — seven are red today and the which-side-is-stale decision is still open, so a guard added now would be a broken gate. **Lane 16's drift-cluster accounting is closed at 7 with no residual; the successor question is the staleness decision itself, which is the data owner's, not a worker's.**
