<!-- collected 2026-09-08T04:42:31Z by campaign coordinator; agent id ad60410e64224377b; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ad60410e64224377b.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**W41** (re-dispatch), OPUS-CAPACITY-CAMPAIGN-20260908. Lane: precise footprint and consequence of the campaign's nested `inputs/` copies.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My system context states Opus 5, exact id `claude-opus-5`. Nothing in the environment names a served model; the coordinator must extract the real per-child model from the transcript.

- `date -u` start `Tue Sep  8 04:33:38 UTC 2026` · end `Tue Sep  8 04:39:27 UTC 2026`.
- `git rev-parse HEAD` start **`408b676aec3625a36917755662516232a27a1278`** · end **`408b676a`** — unchanged.
- `git status --porcelain` start: **0 lines** · end: **0 lines**.
- **Write isolation honoured.** Nothing written, moved or deleted in `/home/user/Rare-cancers`; no git write operation (only `rev-parse`, `status`, `ls-files`, `log`, `grep`, `check-ignore` — all reads). `scripts/preflight.sh` NOT run. `atr_hrd_sarcoma_series.py` never invoked. No repair, patch, gate, test or `DOC_SKIP` authored or proposed. Nothing deleted from the campaign directory. All execution under `/tmp/claude-0/w41/`, **deleted before returning** (`RM_EXIT=0`, `ls` → No such file or directory). No network, no paid API, no GPU.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — the five long proxy-host lists (`no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS`) are elided as `<proxy host list>`; nothing else removed. **No variable names a served model.**

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=<proxy host list>
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
GLOBAL_AGENT_NO_PROXY=<proxy host list>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=<proxy host list + truststore flags>
NO_PROXY=<proxy host list>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<proxy host list>
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

## Stop condition

Set up front: **return the moment (1) every file under `inputs/` is enumerated and each copy-of-a-tracked-path classified identical/divergent by hash, (2) all 9 `inputs/`-attributable errors are individually classified (a)/(b)/(c) against a measured test of the original's own resolution, and (3) the preflight consequence is settled per gate from source — which gates see `inputs/` at all, and whether any of the 9 survives deleting the campaign directory.** All three measured, plus one gate consequence neither prior report found. **MET.**

## Question

The campaign's `inputs/` subtree produces 9 `systems_check --check` errors including the only `[D6]` id collision. **Is that a damaged repository invariant, or a checker tripping on the campaign's own scratch material — and which preflight gates does it actually redden?**

## Prior-work check

Read in full as dispatched: `research/autonomy/opus-capacity-campaign-20260908/reports/W31b-systems-check-error-attribution.md`, `.../reports/W37-zero-test-coverage-beyond-18-rows.md`, `systems/POLICY-evidence.md` (all 386 lines), `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md` including both "Known, measured, and NOT worth rediscovering" sections.

Not replayed, per those sections: the baseline attribution itself (W31b: 100% campaign-caused, 0 ERROR without the campaign dir), the 0-of-89 backlog verification (W36/W36b), the pytest-interpreter fact (W29f), `origin/literature-cache` (W40). I take W31b's counterfactual as datum and measure the composition of the 9 it identified but did not decompose. **W25 not read, referenced or extended.** No clinical claim anywhere in this report; nothing here bears on EMC efficacy, safety, selectivity or readiness; no wet lab.

Commands used for scope: `git ls-files`, `git check-ignore -v`, `git ls-files --others --exclude-standard`, `git grep -l`, `git status --ignored --porcelain`.

## Method and inputs

| Input | Role |
|---|---|
| `/home/user/Rare-cancers` @ `408b676a` | tree under test, **read-only, live checkout** (not a copy) |
| `research/autonomy/opus-capacity-campaign-20260908/inputs/` | 63 files, the subtree measured |
| `systems/systems_check.py` | checker; `main()` (`:4551-4590`), `write_views` (`:4524-4531`), `DOC_SKIP` (`:1289`), `TRANSIENT_DIRS` + design note (`:1425-1437`) |
| `scripts/preflight.sh` | gate wiring, read at `:1329-1400` and the `PREFLIGHT_FULL`/`PREFLIGHT_TESTS` switches |
| 12 gate sources + 649 tracked test files | grepped for `os.walk` / `rglob` / `glob.glob` / `ls-files` to find who can see `inputs/` |
| `/tmp/claude-0/w41/` | the only place anything was written; deleted at end |

`PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/w41/pyc`, system `python3`. **I ran `systems_check.py --check` against the live tree only after reading `main()` and confirming the sole write site (`write_views`) is reachable only under `--write-views`; `check_views` opens views read-mode.** `git status --porcelain` was 0 lines immediately after.

## Result

### R.1 — `inputs/` IS GITIGNORED. It is not tracked repository content. · PRIMARY — this reframes the question

```
$ git ls-files -- .../inputs | wc -l                      → 0
$ git ls-files --others --exclude-standard -- .../inputs   → 0
$ git check-ignore -v .../inputs/evidence-4878/research/autonomy/OPERATING_PROTOCOL.md
research/autonomy/opus-capacity-campaign-20260908/.gitignore:10:inputs/	<path>
```

The campaign committed a tracked `.gitignore` whose line 10 is `inputs/`, with a documented reason: both capsules already exist as committed blobs on `codex/opus-cloud-inputs-20260908`, and re-committing ~2.9 MiB of identical bytes was refused. `git status --ignored --porcelain` returns six entries repository-wide; five are `__pycache__`/`.pytest_cache`, and **`inputs/` is the only non-cache ignored path in the tree.**

So `inputs/` exists **only in this working tree**. It is in no commit, it is not in the index, and it does not exist in a fresh clone or in CI.

**This corrects a load-bearing sentence in W31b.** W31b wrote that the door it found "is not one `TRANSIENT_DIRS` can close, because the campaign's files are legitimately tracked repository content, not harness state." That is true of `reports/` (197 tracked files at my HEAD) and **false of `inputs/`** — and `inputs/` is where all 9 errors under examination come from, `[D6]` included. Those 9 are the *same class* as the incident `systems_check.py:1427-1437` already records in its own words: *"`os.walk` finds them; git does not (`.gitignore:15`) … 541 ERROR in the main checkout and 0 ERROR on the same commit checked out cleanly elsewhere."* Gitignored nested copies of repository content, found by a walk that never consults git — `grep -n 'subprocess|git ls-files|gitignore' systems/systems_check.py` returns **one hit, and it is that comment.**

### R.2 — The footprint: 63 files, 3 real copies of tracked paths · PRIMARY

63 files, two capsules (`evidence-4878/`, `source-index/`) plus their two source `.zip`s. Mapping each file's path with its first component stripped onto `git ls-files`, then comparing SHA-256 against the live original:

| Copy under `inputs/` | Live tracked original | Bytes | Verdict |
|---|---|---|---|
| `evidence-4878/research/autonomy/OPERATING_PROTOCOL.md` | `research/autonomy/OPERATING_PROTOCOL.md` | 16,732 vs 10,898 | **DIVERGENT** |
| `source-index/scripts/tests/test_a_tier_budget_is_a_decision_somebody_took.py` | same path | 9,481 | **BYTE-IDENTICAL** |
| `source-index/scripts/tier-budgets.json` | same path | 4,759 | **BYTE-IDENTICAL** |

`source-index/README.md` maps onto the root `README.md` by prefix-stripping but is **not a copy** — capsule-specific content, basename coincidence; the mapping is retracted. The other 59 files have no tracked counterpart: capsule evidence (`outcome.json`, `archive-members.json`, preflight logs, nested `.zip`s), and lane-11 proposed code (`source-index/research/tools/source_reuse_index.py` + its test) for which `research/tools/` does not exist in the tree at all.

**The one divergent copy diverges substantially and in a governance-relevant direction.** Both files carry identical frontmatter — same `id: DOC-AUTONOMY-OPERATING-PROTOCOL`, same `date: 2026-09-04`, same `last_verified: 2026-09-04` — while the bodies differ: **74 lines present only in the copy, 1 line present only in the live file.** The copy-only material includes a "Continue beyond a route-specific blocker" section citing a 2026-09-06 user reaffirmation, a 2026-09-05 rule that *"every paper requires one independent ultra-reasoning pass before submission"*, and a paper-priority-rank paragraph. The single live-only line is `Journal submission and outreach follow the user's specific authorization and existing authority.`, which the copy replaces with `Journal submission follows its existing authority. The user's 2026-09-06 standing research_correspondence …`.

`git grep -l` over tracked files finds **zero** hits for `ultra-reasoning`/`reasoning_effort: ultra` and **zero** for `Continue beyond a route-specific blocker`. So an agent that read the copy would be following procedural rules the tracked protocol at this HEAD does not contain, under the same document id and the same `last_verified` date. **Which version is authoritative is UNKNOWN to me** — I did not trace the capsule's provenance beyond its recorded origin ref, and W38/W38b own the corpus-vs-live divergence lane. I report the fact and make no claim about which is correct.

### R.3 — Live-tree baseline, and W37's UNKNOWN answered · PRIMARY

```
$ PYTHONDONTWRITEBYTECODE=1 python3 systems/systems_check.py --check    # LIVE checkout @408b676a
systems_check: 620 objects across 15 collections · 219 ERROR · 239 WARN · 7 INFO
SC_EXIT=1
$ git status --porcelain | wc -l → 0
```

Histogram: **206 D4, 6 K1, 3 D1, 3 D11, 1 D6.** Errors naming a path under `inputs/`: **exactly 9.** Errors naming any path **outside** the campaign directory: **0.**

**W37's flagged UNKNOWN — "whether that also reddens the live tree" — resolves to YES, it reproduces in the live checkout**, with the same 9 errors and the same sampled broken link. W31b's growth model also holds exactly at a third independent point: 197 collected reports + 7 scaffolding + 2 `inputs/` = 206 D4, measured.

### R.4 — Classification of all 9, each against a measured test · PRIMARY

For the six `[K1]`, the decisive test is whether the link target exists **at the original's depth** (`research/autonomy/`), and whether the link exists in the live original at all:

| # | Code | Subject | Link exists in live original? | Target at `research/autonomy/`? | Class |
|---|---|---|---|---|---|
| 1 | K1 | → `RESEARCH_CYCLE.md` | yes | **EXISTS** | **(b)** position artefact |
| 2 | K1 | → `CODEX_RUNNER.md` | yes | **EXISTS** | **(b)** position artefact |
| 3 | K1 | → `portfolio-2026-09-05/recommendation.md` | no (copy-only text) | **EXISTS** | **(b)** position artefact |
| 4 | K1 | → `CLAUDE_DELEGATION.md` | no (copy-only text) | **MISSING** (and untracked anywhere) | **(a′)** genuine broken link — but in the *copy's* text, which is in no tracked file |
| 5 | K1 | → `author-declarations.json` | no (copy-only text) | **MISSING** | **(a′)** same |
| 6 | K1 | → `correspondence/README.md` | no (copy-only text) | **MISSING** | **(a′)** same |
| 7 | D4 | `inputs/source-index/README.md` | — | no tracked counterpart | **(b)** checker walking untracked scratch |
| 8 | D4 | `inputs/source-index/evidence/independent-comparison/report.md` | — | no tracked counterpart | **(b)** same |
| 9 | D6 | id claimed by 2 files | — | see below | **(c)-shaped, but working-tree only** |

**Zero of the 9 are class (a) as the dispatch defined it** — a genuine defect in a tracked original that the copy merely surfaces twice. The live `OPERATING_PROTOCOL.md` produces **no** `[K1]`: both links it actually contains resolve. Three of the six K1 are pure depth artefacts. The other three (`(a′)`) are real dangling links, but they exist only inside the divergent capsule text, so they are a defect **of the capsule**, not of the repository — nothing in any commit points at those three names (`git ls-files | grep -E 'CLAUDE_DELEGATION|author-declarations|autonomy/correspondence'` → empty).

**The `[D6]` specifically:**
```
$ git grep -l -F 'id: DOC-AUTONOMY-OPERATING-PROTOCOL' HEAD --
HEAD:research/autonomy/OPERATING_PROTOCOL.md
```
**Exactly one tracked claimant.** The invariant "an id must resolve to exactly one document" **holds over the repository**. The collision exists only because a gitignored file sits inside the walk root.

### R.5 — Consequence for `scripts/preflight.sh` · PRIMARY (gates read from source; preflight NOT run)

Of the fourteen gates W37 enumerated, only one performs a broad tree walk. `grep -nE 'os\.walk|rglob|glob\.glob|ls-files'` across all twelve Python gates:

- **`systems/systems_check.py`** — five `os.walk(REPO)` sites (`:1126, 1318, 1851, 2280`, plus scoped walks), no git consultation. **Sees `inputs/`.**
- **`lint_citations.py:187` and `emc_systems_map_check.py:351`** — both use `git ls-files --cached --others --exclude-standard`, which **excludes gitignored paths by construction** (measured: that command returns 0 files under `inputs/`). **Blind to `inputs/`, correctly.**
- The other nine gates (`lint_consistency`, `lint_claims`, `lint_style`, `parser_guard`, `receipt_schema`, `lint_submission_residue`, `contract_check`, `tier_budget`, `derived_ids`) plus `validate-registry.mjs` iterate declared JSON collections, in-source target lists or one fixed glob. **None can see `inputs/`.**

**Gate 2 (`preflight.sh:609`, `systems_check --check`) is the only linter gate reddened by `inputs/` — and `inputs/` is not what makes it red.** It is rc=1 at 206 D4 from the tracked `reports/` alone; removing `inputs/` would leave 210 errors and rc=1. The 9 are 4.1% of a gate that fails regardless.

**A second gate, which neither W31b nor W37 covered, IS made to fail by `inputs/` alone — a pytest guard.** Grepping all 649 tracked test files for broad walks found three walking the repo root. Two are harmless (`test_munck_attribution_retired.py` — `grep -rl Munck` over `inputs/` returns **0**; the census-clone test symlink-mirrors the tree but `claim_coverage.py` has no walk at all, so it pays a copy cost and nothing more). The third is not:

`scripts/tests/test_a_tier_budget_is_a_decision_somebody_took.py::test_every_tests_directory_in_the_repository_is_inside_some_budget` walks `ROOT`, skipping only `.git`, `node_modules`, `__pycache__` and dot-directories, and asserts every directory named `tests` containing a `test_*.py` is listed in a tier of `scripts/tier-budgets.json`. `inputs/` is not a dot-directory. Replicating the test body verbatim as a standalone read-only script:

```
$ python3 /tmp/claude-0/w41/replicate.py
found tests dirs: 7
missing from every budget: ['research/autonomy/opus-capacity-campaign-20260908/inputs/source-index/research/tools/tests',
                            'research/autonomy/opus-capacity-campaign-20260908/inputs/source-index/scripts/tests']
REPLICATE_EXIT=1
```

The five budgeted directories are `scripts/tests`, `research/autonomy/tests`, `systems/tests`, `research/manuscripts/tests`, `research/modalities/tests`. The two capsule `tests/` directories are in no tier, so the assertion fails. **This is a faithful replication, not the pytest invocation itself** (I declined to run pytest to avoid any write into the checkout); it is labelled accordingly in Validation.

Reading `preflight.sh:1352-1372`: `scripts/tests` runs only when `PREFLIGHT_TESTS=1` or `PREFLIGHT_FULL=1`, and is suppressed when `PREFLIGHT_PAPER` is set. So:

| Invocation | Effect of `inputs/` |
|---|---|
| bare `./scripts/preflight.sh` (the normal commit gate) | gate 2 red — but red from `reports/` anyway; the tier test **does not run**. **No net change.** |
| **`PREFLIGHT_FULL=1`** (CLAUDE.md §6's publication-candidate gate) | gate 2 red **and** the pure-logic tier fails on two directories that exist only because this campaign extracted a capsule into the checkout. |
| `PREFLIGHT_FULL=1` with `PREFLIGHT_PAPER` named | tier test suppressed; gate 2 red as above. |
| CI `tests.yml` / any fresh clone | **green with respect to `inputs/`** — the files are in no commit. |

**Would any of the 9 survive the campaign directory being deleted? No — none of them.** All nine name paths under `inputs/`. Independently: exactly one tracked file claims the `[D6]` id; the live protocol's own two links resolve; the two D4 subjects have no tracked counterpart; and at my HEAD **0 of 219 errors name any path outside the campaign directory** — the same result W31b got by actually removing the directory.

### R.6 — The plain answer · PRIMARY

**The campaign has NOT damaged a repository invariant. It has tripped two checkers on its own untracked scratch material — and the `[D6]` is the clearest case of that, not the exception to it.**

Stated without softening, because the dispatch was right to demand it be said either way:

- The id-uniqueness invariant **holds** over every tracked file. `DOC-AUTONOMY-OPERATING-PROTOCOL` has exactly one claimant in `HEAD`. Nothing was committed that breaks it, and nothing needs repairing to restore it.
- The collision is produced entirely by a **gitignored** file that the campaign's own `.gitignore` deliberately kept out of the repository, found by a walk that by design never asks git. It disappears the moment the extraction is removed, and it never existed in any commit, clone or CI run.
- **W31b's refusal to propose a `DOC_SKIP` remains right, and my measurement gives it a better reason than the one it had.** W31b declined because the 9 were "real findings"; on measurement, six of the nine are not findings about this repository at all (three depth artefacts, two untracked-scratch D4, one working-tree-only id collision), and the three that are real broken links are broken in a capsule document, not in a tracked file. The correct reason to refuse a `DOC_SKIP` is not that it would hide real defects — it is that **narrowing the checker is the wrong instrument for a problem whose cause is untracked material inside the walk root**, which is precisely what the design note at `systems_check.py:1436` says: *"Do NOT 'fix' this by excluding only `.claude/worktrees`."*

Two things are nevertheless genuinely worth the coordinator's attention, and neither is a checker problem:

1. **A divergent copy of the live operating protocol is sitting in the working tree under the same document id, carrying procedural rules — including an "every paper requires one independent ultra-reasoning pass before submission" requirement — that appear in no tracked file.** That is a documentation-integrity hazard for any agent that reads the wrong one, and it is independent of any gate.
2. **A `PREFLIGHT_FULL=1` run on this branch, in this container, fails a pure-logic test for a reason unconnected to any change** — and `PREFLIGHT_FULL=1` is the publication-candidate gate. That failure is new information; it is not in W31b, W37 or `COMMON-BRIEF.md`.

## Validation evidence

Environment for every run: live checkout `/home/user/Rare-cancers` @ `408b676a`, container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, system `python3`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w41/pyc`. No network attempted, so no denial to record. Every exit code quoted is a real captured `$?`.

**RUN** — `git ls-files`/`--others --exclude-standard`/`check-ignore -v` over `inputs/` (tracked=0, untracked-listed=0, ignored by `.gitignore:10`); `git status --ignored --porcelain` (6 entries, `inputs/` the only non-cache one); 63-file enumeration with sizes; prefix-strip mapping onto 7,808 tracked paths with per-file `sha256sum` comparison (2 IDENTICAL, 1 DIVERGENT, 1 false positive retracted); `diff` of the two `OPERATING_PROTOCOL.md` (74 `>` lines, 1 `<` line, `wc -c` 16,732 vs 10,898, frontmatter compared line by line); `systems/systems_check.py --check` on the **live** tree (`SC_EXIT=1`, 219 ERROR / 239 WARN / 7 INFO; `git status --porcelain` → 0 immediately after); histogram and the 9 `inputs/` lines quoted verbatim; existence test of all six K1 targets at `research/autonomy/`; per-target presence test in live vs copy; `git grep -l -F 'id: DOC-AUTONOMY-OPERATING-PROTOCOL' HEAD --` (one file); `git grep -l` for the copy-only governance phrases (zero tracked hits); write-site read of `systems_check.py:4524-4531` and `main():4551-4590` **before** running it; `DOC_SKIP`/`TRANSIENT_DIRS` read; walk-site grep across 12 gate sources and 649 tracked test files; walk-body reads of the three broad-walk tests; `scripts/tier-budgets.json` directory list; `preflight.sh:1329-1400` read for the tier switch; verbatim replication of `test_every_tests_directory_in_the_repository_is_inside_some_budget` (`REPLICATE_EXIT=1`, two unbudgeted directories named); scratch deleted (`RM_EXIT=0`).

**PROPOSED (NOT RUN)** — `scripts/preflight.sh` end-to-end and `PREFLIGHT_FULL=1` (dispatch forbids; every gate consequence in R.5 is derived from source plus the read-only runs above, so **no preflight exit code is measured here**). The actual `pytest scripts/tests/test_a_tier_budget_is_a_decision_somebody_took.py` invocation — **not run**, to keep write isolation absolute (pytest would create `.pytest_cache`/`__pycache__` inside the checkout); R.5's failure is a verbatim replication of the test body against the same inputs, and is labelled as such rather than as a pytest result. Any repair, `DOC_SKIP`, patch, gate or test — **none authored, none proposed, none applied.** No guard weakened, relaxed or reordered. Nothing deleted from the campaign directory.

## Limitations

- **Model identity is self-report.**
- **The tier-budget failure is a replication, not a pytest run.** It executes the assertion's exact logic against the exact same JSON and walk filter, but a real `pytest` invocation could differ through a fixture I did not reproduce (`doc` is a fixture loading `tier-budgets.json`; I loaded the same file directly). Treat it as a strong prediction of a red test, not as a captured pytest exit code.
- **219 ERROR is already stale.** It was true at `408b676a` / 04:33Z and grows by one per collected report (W31b's model, which held exactly at my point).
- **Provenance of the divergent `OPERATING_PROTOCOL.md` is UNKNOWN.** I established the two files differ and that the copy-only text is absent from every tracked file; I did **not** establish which is newer, which is authoritative, or how the capsule came to hold it. That belongs to whoever owns the capsule and to the W38/W38b divergence lane.
- **My classification of the three `(a′)` K1 rests on absence of the target across `git ls-files` and on disk at `research/autonomy/`.** Absence is UNKNOWN, not proof, if those documents exist on another branch — which is plausible given the same capsule carries protocol text absent here.
- **This is a hygiene and gate-arithmetic result.** It says nothing about whether any graph claim, registry row, ledger entry or manuscript is scientifically correct, and nothing about EMC efficacy, safety, selectivity or clinical readiness. There is no wet lab.
- I did not examine the ~180 WARN or the 7 INFO, nor the `.zip` capsule contents beyond byte sizes.

## Tool-call and wall-clock count actually used

**21 tool calls** (all `Bash`; two issued as a parallel pair). **Wall clock ≈ 6 minutes**, `04:33:38Z` → `04:39:27Z`, plus report drafting. Well inside the ~40-call / ~40-minute target; returned as soon as the stop condition was met.

## Next concrete action

**One item, and it is the coordinator's: decide what happens to `research/autonomy/opus-capacity-campaign-20260908/inputs/` before anyone runs `PREFLIGHT_FULL=1` on this branch, and record the decision where a worker will see it.** The material is gitignored, so removing the extraction from the working tree costs nothing recoverable — both capsules remain as committed blobs on `codex/opus-cloud-inputs-20260908`, and the `.gitignore` header already prints the two `git show` commands that restore them. Removing it deletes all 9 errors, deletes the `[D6]`, and un-fails the tier-budget guard, without narrowing any checker and without touching a tracked file. If it must stay for the campaign's duration, then the honest form is a line in `COMMON-BRIEF.md` saying so — that `inputs/` is untracked scratch, that its 9 `systems_check` errors are working-tree-only, and that `PREFLIGHT_FULL=1` will fail `test_every_tests_directory_in_the_repository_is_inside_some_budget` while it is present. **I applied nothing and propose no code change**; both routes above are removals of the campaign's own untracked material or a note, not a repair to any gate.

A second, smaller item for whoever owns the operating protocol: the divergent copy at `.../inputs/evidence-4878/research/autonomy/OPERATING_PROTOCOL.md` carries 74 lines of procedural rules — including a standing pre-submission ultra-reasoning requirement dated 2026-09-05 — that exist in **no** tracked file at `408b676a`, under the same document id and the same `last_verified: 2026-09-04`. Whether the live protocol is missing them or the capsule is carrying a superseded variant is UNKNOWN and worth one deliberate check by someone with the branch history.
