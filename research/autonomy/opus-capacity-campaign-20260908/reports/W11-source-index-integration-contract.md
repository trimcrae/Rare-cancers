> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git tree; the coordinator is the sole collector.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).
>
> COLLECTION NOTE: this worker was later resumed with the arrived source-index capsule and then
> STOPPED by the coordinator, because resuming it created a second concurrent source-index worker
> alongside W11b and the campaign permits only one owner of source-index changes. The text below is
> W11's completed pre-capsule report (longest assistant block in the transcript), recovered after an
> earlier collection pass wrote only the resumed agent's opening line. The capsule-consuming work is
> W11b's.

---

Sanity check complete: no `*source*index*` file is tracked at `92abbcb9`, and the bundle commit `4878b9b9` is not an object in this clone — the dependency is genuinely pending, not missing. The discovery contract is fully reproduced. Report follows.

---

## Worker

**W11**, lane 11 — source-index repair integration (sole owner of source-index changes).

**Model evidence — SELF-REPORT, not independently verified.** I report myself as Claude Opus 5 (`claude-opus-5`) per my own system context. I did not observe the served model; the coordinator must extract the actual per-child runtime model from the transcript. `CLAUDE_CODE_VERSION=2.1.42`, `CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default`. No env var in this container names a model at all — the literal output below contains no model field, and I do not infer one.

`date -u` at start: `Tue Sep  8 01:54:34 UTC 2026`
`date -u` at end: `Tue Sep  8 01:56:36 UTC 2026`

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (literal, both runs identical; long proxy vars elided only where marked):

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
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 … (proxy config, elided)
```
(`no_proxy`/`NO_PROXY`/`GLOBAL_AGENT_NO_PROXY`/`npm_config_noproxy` also matched on `anthropic` inside their host lists; elided as pure proxy config.)

Write isolation honoured: **zero** files created or modified under `/home/user/Rare-cancers`. All execution in `/tmp/claude-0/w11-repro`. No git write operation of any kind. `git status --porcelain` at start showed only the pre-existing untracked campaign directory `research/autonomy/opus-capacity-campaign-20260908/`, which I did not touch.

## Question

**What exactly must a new source-index module and its tests satisfy to be discovered, to run, and to land in an existing test tier of this repository — and what mechanism made the original helper's discovery fail?**

It is open because the source-index bundle has not arrived (see Prior-work check), so the only legitimate work available is to fix the *receiving contract* rather than to guess at code I have not seen. It is worth doing now because the failure recorded in `CLOSED-WORK.md` ("discovery failed — the directory was not importable") is a *contract* failure, not a code-quality failure, and it is reproducible without the bundle.

## Prior-work check

Commands run and results:

- `git ls-files | rg -i "source.?index"` → **no output, exit 1.** No source-index file is tracked at the freeze point `92abbcb905cacf07f14b238db50d1b98f6590374` (confirmed as HEAD by `git rev-parse HEAD`).
- `rg -n -i "source.index" --glob '!.git' -l` → 5 files: `research/literature/fusion-breakpoint-sweep-2026-08-24.json`, `research/literature/fusion-junction-vaccine-prior-art-2026-08-24.json`, and the three campaign documents in `research/autonomy/opus-capacity-campaign-20260908/` (`AGENT-ROLES.md`, `MANIFEST.md`, `CLOSED-WORK.md`). The two literature JSONs are incidental regex matches on adjacent "source"/"index" text in fusion sweeps, **not** source-index code. So the only references to this lane's subject are the campaign's own dispatch documents.
- `git cat-file -t 4878b9b9d1c082cea46e636dad47be419f1fe021` → `fatal: git cat-file: could not get object info`. **The bundle commit is not an object in this clone.** This is UNKNOWN/pending input, not proof of absence — exactly as the dispatch states.
- `CLOSED-WORK.md` read in full. Confirmed I am not replaying: the ASO/Qeios deliverables, the retained biology-access refusal, the closed scientific gates, or the unrecovered sources. The "Source-index state (lane 11 only)" block is my direct input and I treat its three constraints as binding: no arbitrary test-ceiling increase, no 30-test gate, prefer complete named final files with legitimate integration into **existing** tiers.

**I did not reinvent, guess at, or repair source code I have not seen.** No source-index implementation appears anywhere in this report.

## Method / inputs

Files read at `92abbcb9` (all read-only): `scripts/tier-budgets.json`, `scripts/tier_budget.py` (172 lines, read in full), `scripts/preflight.sh` (1,648 lines, read by targeted `sed -n` and `grep -n`; the file is 133 KB and was not read in one pass), `scripts/affected_tests.py` (399 lines, structure surveyed), `scripts/fast_checks.py` (185 lines, docstring and defs), `scripts/tests/` (21 files listed), `systems/tests/` (16 files listed), `research/autonomy/tests/conftest.py`, and import preambles of `scripts/tests/test_affected_tests.py` and `systems/tests/test_systems_check.py`.

Execution environment for the reproduction: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, working directory `/tmp/claude-0/w11-repro`.

**Interpreter finding that must be stated up front, because it changes how the evidence reads.** `python3 -c "import pytest"` → `ModuleNotFoundError: No module named 'pytest'`, and `command -v pytest` → `/root/.local/bin/pytest`, whose shebang is `#!/root/.local/share/uv/tools/pytest/bin/python3`, reporting `pytest 9.1.1`. Under `scripts/preflight.sh:419-427` this container therefore takes the **middle branch**:

```
419  if python3 -c "import pytest" >/dev/null 2>&1; then
420    PYTEST="python3 -m pytest"
422  elif command -v pytest >/dev/null 2>&1; then
423    PYTEST="pytest"
424    PYTEST_BRANCH="the bare \`pytest\` console script — ⛔ A UV TOOL IN ITS OWN ISOLATED VENV"
```

which the file itself flags at lines 406 and 412 as the branch that once "made the gate report **36 failures that do not exist**". My reproduction used that uv-tool pytest deliberately, because it is what preflight would use here. It is adequate for discovery/collection semantics (pure stdlib test files, no scientific dependency) but **it is not evidence about this repository's real suites**, and I ran none of them.

## Result

### R1 — How test files are discovered: two independent mechanisms with different rules

| # | Row | Finding | Class |
|---|---|---|---|
| R1a | Runner discovery | `preflight.sh:1376` — `$PYTEST $PYTEST_PAR scripts/tests research/autonomy/tests $SYSTEMS_TESTS -q --durations=25 --continue-on-collection-errors`. Directories are **named explicitly**, not scanned. Manuscripts at `:1221`, modalities at `:1086`/`:1082`. | PRIMARY (code read) |
| R1b | Budget discovery | `tier_budget.py:78-102` `count_dir(rel)` — `os.listdir(path)`, **non-recursive**, filtered by `entry.startswith("test_") and entry.endswith(".py")` (`:86-87`). Directories come from `tier-budgets.json` `tiers[*].directories`. | PRIMARY (code read) |
| R1c | Divergence | These two never agree on a subdirectory: pytest recurses, `count_dir` does not. Measured below. | PRIMARY (executed) |
| R1d | No pytest config | `pytest.ini`, `setup.cfg`, `pyproject.toml`, `tox.ini` all absent from the repository root (`cat` returned nothing for each). There is no `[tool.pytest]` section, no `testpaths`, no `python_files` override, no configured `importmode`. **All pytest defaults apply**, including default import mode `prepend`. | PRIMARY |
| R1e | No `__init__.py` anywhere | `find scripts systems research/autonomy/tests research/manuscripts/tests research/modalities/tests -name '__init__.py'` → **no output**. Not one test directory is a package. | PRIMARY |
| R1f | `conftest.py` | Exactly three: `research/autonomy/tests/`, `research/modalities/tests/`, `research/manuscripts/tests/`. **`scripts/tests/` and `systems/tests/` have none.** | PRIMARY |

### R2 — What makes a directory importable to that mechanism (the root cause)

`scripts/tests/` and `systems/tests/` are not packages and have no `conftest.py`. The repository's actual convention is an explicit `sys.path` insertion inside each test module. `scripts/tests/test_affected_tests.py:19-21`:

```python
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import affected_tests as A  # noqa: E402
```

and `systems/tests/test_systems_check.py:22-25`:

```python
sys.path.insert(0, SYS)

import systems_check as sc  # noqa: E402
import parser_guard as pg  # noqa: E402
```

**So "importable" in this repository does not mean `__init__.py`. It means: the directory holding the subject module is placed on `sys.path` by the test module itself, before the `import`, with `# noqa: E402` on the import line.** A test that omits this preamble fails at *collection*, not at assertion — which is precisely the shape recorded in `CLOSED-WORK.md`. Reproduced (Case F1 vs F2, full commands in Validation evidence):

| Row | Case | Result | Class |
|---|---|---|---|
| R2a | Test does `import source_index` with no `sys.path` preamble | `E ModuleNotFoundError: No module named 'source_index'`; `ERROR scripts/tests/test_source_index_helper.py`; `1 error in 0.01s`; **exit 1** | PRIMARY (executed) |
| R2b | Identical test with the repository's `sys.path.insert(0, os.path.join(ROOT, "scripts"))` preamble | `1 passed in 0.00s`; **exit 0** | PRIMARY (executed) |
| R2c | Duplicate test basename across two tier directories, no `__init__.py` | `import file mismatch … HINT: … use a unique basename`; `Interrupted: 1 error during collection`; **exit 2** | PRIMARY (executed) |
| R2d | `__init__.py` present under a hyphenated parent dir (`source-index/tests/`) | `1 passed`, **exit 0** — pytest 9.1.1 handled it. The hyphen did **not** break collection here. | PRIMARY (executed) |
| R2e | Same tree with `__init__.py` removed | `1 passed`, **exit 0** | PRIMARY (executed) |

R2d/R2e are a **negative result and I preserve it**: my initial hypothesis that a non-identifier directory name breaks pytest collection was **refuted** on pytest 9.1.1. The importability failure is the `sys.path`/`ModuleNotFoundError` mechanism (R2a), and secondarily basename collision (R2c) — not `__init__.py` absence and not the hyphen.

One caveat on hyphens I did verify rather than assume: `importlib.import_module('source-index.core')` **succeeded** (exit 0) via namespace-package resolution, but a bare `import source-index.core` statement is a syntax error. A hyphenated directory is therefore usable only through `importlib`, never through the `import` statement the repository's convention uses.

### R3 — Tiers, budgets, and current standing

From `scripts/tier-budgets.json` (`tiers` object) and measured live with `python3 scripts/tier_budget.py` in the real repository (read-only, exit 0):

| Tier | Directories (`tier-budgets.json`) | Ceiling | **Measured now** | Headroom | Class |
|---|---|---|---|---|---|
| `commit-loop` | `scripts/tests`, `research/autonomy/tests`, `systems/tests` | 1500 | **1466** in 102 files | **34** | PRIMARY |
| `paper-guards` | `research/manuscripts/tests` | 1000 | **966** in 111 files | 34 | PRIMARY |
| `modalities` | `research/modalities/tests` | 7500 | **7247** in 436 files | 253 | PRIMARY |

Units: **test *functions*, counted by AST walk — not collected tests.** `tier_budget.py:26-28` states this explicitly: "IT THEREFORE COUNTS TEST FUNCTIONS, NOT COLLECTED TESTS: a parametrized function is one here and many to pytest." Uncertainty: none in the count itself (deterministic AST walk, `:97-100`); the count is exact for the freeze commit and will move with any other lane's landed tests.

### R4 — What `preflight.sh` actually runs, normal vs `PREFLIGHT_FULL=1`

Gating variables, quoted:

```
551  [ "${PREFLIGHT_TESTS:-0}" = "1" ] && RUN_TESTS=1
552  [ "${PREFLIGHT_FULL:-0}" = "1" ] && RUN_TESTS=1
578  [ "${PREFLIGHT_FULL:-0}" = "1" ] && RUN_MODALITIES=1
1330 SYSTEMS_TESTS=""
1331 [ "${RUN_TESTS:-0}" = "1" ] && SYSTEMS_TESTS="systems/tests"
1355 RUN_SELECTOR_TESTS=0
1356 [ "${PREFLIGHT_TESTS:-0}" = "1" ] && RUN_SELECTOR_TESTS=1
1357 [ "${PREFLIGHT_FULL:-0}" = "1" ] && RUN_SELECTOR_TESTS=1
1364 [ -n "${PREFLIGHT_PAPER:-}" ] && RUN_SELECTOR_TESTS=0
```

| Mode | pytest actually executed | Class |
|---|---|---|
| **Default** (no flags) | **No pytest at all** on `scripts/tests`, `research/autonomy/tests`, `systems/tests` — `RUN_SELECTOR_TESTS=0` prints `== pytest (pure-logic suites) == SKIPPED` (`:1366-1368`). Manuscripts gated behind `RUN_TESTS` (`:1200`), modalities behind `RUN_MODALITIES`. Only the fast doc/artifact linters run, plus the tier-budget gate. | PRIMARY |
| `PREFLIGHT_TESTS=1` | Adds `research/manuscripts/tests` (`:1221`) and `scripts/tests research/autonomy/tests systems/tests` (`:1376`). | PRIMARY |
| `PREFLIGHT_FULL=1` | Sets `RUN_TESTS` **and** `RUN_MODALITIES`: everything above plus `research/modalities/tests/` (`:1086`) unscoped. This is the only tier `publish_bar` clause 2 accepts (`:1307-1313`). | PRIMARY |
| `PREFLIGHT_PAPER` set with FULL | `RUN_SELECTOR_TESTS=0` (`:1364`) — **`scripts/tests` and `systems/tests` are NOT run** in a paper-scoped publication run. | PRIMARY |

The tier-budget gate runs **unconditionally**, in every mode, at `:1507`:

```
1507  if python3 scripts/tier_budget.py --check; then
1508    :
1509  else
1510    echo "   ⛔ a tier is over its budget -- ..."
1512    rc=1
```

**Consequence for this lane:** the budget ceiling is enforced on *every commit*, while the tests that would prove a source-index module works are **not run by default at all**. A source-index test lands its *cost* immediately and its *verification* only behind a flag.

### R5 — Measured divergence between the two discovery mechanisms (a real budget hole)

Synthetic tier tree with 2 test functions in a correctly-named flat file, 4 in `scripts/tests/source_index/test_nested.py`, and 1 in a wrongly-prefixed `scripts/tests/source_index_tests.py`:

| Mechanism | Result | Class |
|---|---|---|
| `python3 scripts/tier_budget.py` | `ok commit-loop 2/3 test function(s) in 1 file(s)` — exit 0 | PRIMARY (executed) |
| `pytest scripts/tests -q --collect-only` | `6 tests collected in 0.00s` | PRIMARY (executed) |

**Four test functions ran and were charged to nobody.** The nested subdirectory is invisible to `count_dir`'s `os.listdir` (`tier_budget.py:85`) but fully visible to pytest's recursive collection. The wrongly-prefixed file (`source_index_tests.py`) was invisible to *both* — it is neither counted nor run, i.e. a silently dead test file.

This is the same defect class the budget file exists to prevent (`tier-budgets.json` `_why_this_file_exists`: "THE BLOAT WAS ACCRETION AND NOBODY EVER DECIDED IT"), and it means **placing source-index tests in a subdirectory would evade the ceiling rather than respect it.** That evasion is available and I am specifying against it.

### R6 — The shadowed-name guard, verified firing

`tier_budget.py:49-75` `_shadowed()` detects two `def test_x` in one namespace. Verified on the synthetic tree with a deliberate duplicate:

```
   SHADOW commit-loop                3/3     test function(s) in 1 file(s)
         scripts/tests/test_source_index.py: test_a defined at lines [1, 3] — only the LAST one runs
::error::scripts/tests/test_source_index.py defines test_a at lines [1, 3]. ...
SHADOW_EXIT=1
```

Exit 1, i.e. it would fail the commit gate at `preflight.sh:1507`. Note the count read `3/3`: the shadowed function is **still charged to the ceiling while measuring nothing** (`tier_budget.py:60-65`).

## Integration requirement specification

Every requirement below is derived from code read at `92abbcb9` with a line reference, or from a command I executed. **No ceiling increase is proposed. No 30-test gate is proposed.** This specification is what the bundle must satisfy; it does not describe or assume the bundle's contents.

**S1 — Implementation module location.** The subject module goes at `scripts/<name>.py` (flat, directly in `scripts/`), matching `affected_tests.py`, `tier_budget.py`, `fast_checks.py`. Rationale: the repository's only working import convention (`scripts/tests/test_affected_tests.py:19-21`) inserts `os.path.join(ROOT, "scripts")` on `sys.path` and imports by bare module name. A nested package under `scripts/` would require a different preamble that has no precedent here.

**S2 — Module name is a Python identifier, underscores only.** No hyphen. A hyphenated name is unreachable by the `import` statement (verified: `import source-index.core` is a syntax error; only `importlib.import_module` reaches it, exit 0 in Case G). Suggested `scripts/source_index.py`; the bundle's own final name governs if it already has one and is a valid identifier.

**S3 — Test file location: flat, directly inside an existing tier directory.** `scripts/tests/` is the correct home (its subject is a `scripts/` module, and `scripts/tests` is a `commit-loop` directory per `tier-budgets.json`). **No subdirectory.** Derived from `tier_budget.py:85` (`os.listdir`, non-recursive) against measured pytest recursion — R5 shows a subdirectory runs 4 uncounted tests. A subdirectory is a budget-evasion, not a layout choice.

**S4 — Test filename: `test_<something>.py`, and the basename must be globally unique across all five test directories.** Prefix and suffix required by `tier_budget.py:86-87` (`startswith("test_") and endswith(".py")`) — R5 measured `source_index_tests.py` as counted by nothing and run by nothing. Uniqueness required because no directory has `__init__.py` (R1e) and pytest's default `prepend` import mode then keys modules by basename: Case B produced `import file mismatch … Interrupted: 1 error during collection`, exit 2. Verify with `git ls-files | rg '/tests/<basename>$'` before naming.

**S5 — No `__init__.py`.** Not one exists in the repository (R1e). Adding one to `scripts/tests/` would change the import identity of all 21 existing modules in that directory for a benefit R2d/R2e measured as zero.

**S6 — The test module MUST carry the `sys.path` preamble.** Exactly the established form, mirroring `scripts/tests/test_affected_tests.py:19-21`:

```python
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import source_index  # noqa: E402
```

**This single requirement is the root cause of the recorded discovery failure.** Omitting it produces `ModuleNotFoundError` at collection with exit 1 (Case F1); including it produces `1 passed`, exit 0 (Case F2). The `# noqa: E402` is not decorative — it is required because the import follows executable statements, and it is present on both existing precedents.

**S7 — No duplicate test function names within a module or class body.** `tier_budget.py:49-75`; verified firing with exit 1 (R6). A shadowed test is charged to the ceiling and measures nothing.

**S8 — Tier assignment rule.** `commit-loop`, because the tier is defined by *directory membership*, not by subject: `tier-budgets.json` `tiers["commit-loop"]["directories"] = ["scripts/tests", "research/autonomy/tests", "systems/tests"]`, consumed at `tier_budget.py:112`. Placing the file in `scripts/tests/` **is** the tier assignment; there is no separate declaration to make.

**S9 — Budget impact: the hard number is 34.** Measured `commit-loop` standing is **1466/1500**. The source-index tests must therefore total **at most 34 test functions**, counted as AST `def test_*` (parametrization is free — `tier_budget.py:26-28`). If the bundle's tests exceed 34, the three permitted answers are those in `tier-budgets.json` `_how_to_raise_a_ceiling`, in its stated order: (1) does it belong in a cheaper tier; (2) has something in the tier stopped earning its place; (3) only then, a governed ceiling change with a measurement and an `amendments.jsonl` declaration. **Editing the number is explicitly the last option and is not authorized by this lane.** The 34 is a *ceiling I measured*, not a target: fewer is better, and the recorded 10 original tests sit comfortably inside it.

⚠ **34 is shared headroom, not reserved.** Any other lane that lands a `commit-loop` test before the bundle reduces it. Re-run `python3 scripts/tier_budget.py` at integration time; do not trust this number at merge.

**S10 — Verification command for integration, and what it does *not* prove.** The tests do not run in the default commit loop (`preflight.sh:1355-1368`, R4). The scoped command is:

```
PREFLIGHT_TESTS=1 ./scripts/preflight.sh
```

which reaches line 1376. `PREFLIGHT_FULL=1` is reserved for a publication candidate per `CLAUDE.md` §6 and is not required to land a `scripts/` module. ⛔ **In this container that run would take the uv-tool pytest branch (`preflight.sh:422-424`), the branch this file itself records as having reported "36 failures that do not exist" (`:406`). An integration verdict from this container is not trustworthy; the authority is `tests.yml`, which `preflight.sh:1289-1290` and `:1349-1352` both name as running all four directories in full on every push.** I did not run preflight — my dispatch does not authorize it, and the brief forbids it absent that.

**S11 — Tracked-tree guard does not bind here, and that is a gap to know about.** `research/autonomy/tests/conftest.py` installs `tracked_tree_guard` ("NO TEST MAY WRITE TO A GIT-TRACKED FILE") for the autonomy suite; `research/modalities/tests/` and `research/manuscripts/tests/` have their own conftest. **`scripts/tests/` has no `conftest.py` at all** (R1f), so a test landing there is *not* protected by that guard. A source-index test must therefore not write to the tracked tree by its own construction — nothing will catch it if it does.

**S12 — The case-sensitive disclaimer assertion is a live open item, unseen.** `CLOSED-WORK.md` records the one failing test of ten as "a case-sensitive disclaimer assertion". I have not seen that assertion or the string it compares against, and I do not propose a fix. It is a real 1/10 failure and must be resolved on the actual code, not on my reading of a summary line.

## Validation evidence

All commands **RUN**, in `/tmp/claude-0/w11-repro`, outside the repository. `pytest` = `/root/.local/bin/pytest`, version **9.1.1**, interpreter `/root/.local/share/uv/tools/pytest/bin/python3`. Repository reads used system `python3` = **3.11.15**.

**Interpreter probe (RUN).**
`python3 -c "import pytest,sys;print(pytest.__version__, sys.version)"` → `ModuleNotFoundError: No module named 'pytest'` (exit 1).
`command -v pytest` → `/root/.local/bin/pytest`; `pytest --version` → `pytest 9.1.1`; `head -1 $(command -v pytest)` → `#!/root/.local/share/uv/tools/pytest/bin/python3`.

**Case A — flat tests dir, no `__init__.py`, unique basename (RUN).**
`cd $W/A && pytest tests -q` → `1 passed in 0.00s`, **A_EXIT=0**.

**Case B — duplicate basename across two tier dirs, no `__init__.py` (RUN).**
`cd $W/B && pytest scripts/tests systems/tests -q`, verbatim:
```
ERROR collecting systems/tests/test_source_index.py
import file mismatch:
imported module 'test_source_index' has this __file__ attribute:
  /tmp/claude-0/w11-repro/B/scripts/tests/test_source_index.py
which is not the same as the test file we want to collect:
  /tmp/claude-0/w11-repro/B/systems/tests/test_source_index.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
ERROR systems/tests/test_source_index.py
!!!!! Interrupted: 1 error during collection !!!!!
1 error in 0.08s
```
**B_EXIT=2.**

**Case C — test file in a subdirectory of the tier dir (RUN).**
`cd $W/C && pytest scripts/tests -q` → `2 passed in 0.01s`, **C_PYTEST_EXIT=0**. pytest recurses.

**Case D — `__init__.py` under a hyphenated parent (RUN).**
`cd $W/D && pytest source-index/tests -q` → `1 passed in 0.00s`, **D_EXIT=0**. Hypothesis refuted.

**Case E — same tree, `__init__.py` removed (RUN).**
→ `1 passed in 0.00s`, **E_EXIT=0**.

**Case F1 — helper import with no `sys.path` preamble (RUN).** THE ROOT-CAUSE REPRODUCTION.
`cd $W/F && pytest scripts/tests -q --continue-on-collection-errors`, verbatim tail:
```
scripts/tests/test_source_index_helper.py:1: in <module>
    import source_index
E   ModuleNotFoundError: No module named 'source_index'
ERROR scripts/tests/test_source_index_helper.py
1 error in 0.01s
```
**F1_EXIT=1.**

**Case F2 — identical test with the repository's preamble (RUN).**
→ `1 passed in 0.00s`, **F2_EXIT=0**.

**Case G — hyphenated dir via importlib (RUN).**
`python3 -c "import importlib; m=importlib.import_module('source-index.core'); print(m)"` → `<module 'source-index.core' from '/tmp/claude-0/w11-repro/G/source-index/core.py'>`, **G_EXIT=0**.

**Case H — budget vs collection divergence (RUN).** `scripts/tier_budget.py` and a trimmed `tier-budgets.json` (single tier, ceiling 3) copied into the synthetic tree; the real repository was not modified.
`python3 scripts/tier_budget.py` → `ok commit-loop 2/3 test function(s) in 1 file(s)`, **H_REPORT_EXIT=0**.
`python3 scripts/tier_budget.py --check` → same, **H_CHECK_EXIT=0**.
`pytest scripts/tests -q --collect-only` → `6 tests collected in 0.00s`.

**Case R6 — shadowed guard (RUN).** Output quoted in full at R6, **SHADOW_EXIT=1**.

**Real repository standing (RUN, read-only).**
`cd /home/user/Rare-cancers && python3 scripts/tier_budget.py`:
```
   ok    commit-loop             1466/1500  test function(s) in 102 file(s)
   ok    modalities              7247/7500  test function(s) in 436 file(s)
   ok    paper-guards             966/1000  test function(s) in 111 file(s)
```
**REAL_EXIT=0.**

**PROPOSED (NOT RUN):** `PREFLIGHT_TESTS=1 ./scripts/preflight.sh` (S10). Not authorized by my dispatch, and its verdict in this container would come from the degraded uv-tool pytest branch.

**PROPOSED (NOT RUN):** any execution of the source-index bundle's helper, its 10 tests, or its 4 CLI examples. **The bundle has not arrived.**

### On the 9 static findings and their two diffs

Stated explicitly, as instructed. **The 9 review findings are not an empirically passed review.** They are a read-only static opinion. Both accompanying literal diffs **failed `git apply --check` with malformed hunks**, so neither was ever applied, and no run exists that demonstrates any of the 9 findings is real or that any proposed change is correct. **I have not seen the code they refer to** — no source-index file is tracked at `92abbcb9` and the bundle commit `4878b9b9d1c082cea46e636dad47be419f1fe021` is not an object in this clone. Nothing in this report validates, ranks, or adopts any of the 9 findings; when the bundle lands, each must be re-established against the actual file, and a finding that cannot be reproduced against real code is not a defect.

The one piece of *empirical* history I do rely on is the recorded execution in `CLOSED-WORK.md`: discovery failed on importability; running the 10 tests directly gave 9 pass / 1 fail (a case-sensitive disclaimer assertion); 4 CLI examples exited 0. I treat that as a prior measurement I did not perform, not as my own evidence.

## Limitations

- **The bundle is absent.** This specification is a receiving contract; it cannot be confirmed to fit code I have not read. Any requirement may need adjustment against the real file layout, and S12's failing assertion is untouched.
- **The pytest here is not the repository's pytest.** All discovery evidence comes from uv-tool pytest 9.1.1 in an isolated venv with no scientific dependencies — the branch `preflight.sh:406` records as having manufactured 36 phantom failures. My cases are pure-stdlib and dependency-free, so I believe the collection semantics transfer, but that belief is **not measured** and the transfer limit is real. The authority on this repository's real behaviour is `tests.yml`.
- **Version-bound.** Case D/E (hyphens and `__init__.py` are harmless) is a pytest-9.1.1 result. It may not hold on the CI pytest version, which I did not determine. The safe requirements S2/S5 do not depend on it.
- **I did not read `preflight.sh` end to end** — 1,648 lines / 133 KB, read by targeted grep and `sed`. A gate outside the lines I quoted could bear on integration. In particular I did not audit gates 1-8 or the `record_bar_evidence` path.
- **1466/1500 is a snapshot at `92abbcb9`**, dated 2026-09-08T01:56Z. It is not reserved headroom (S9).
- I did not assess whether the source-index module is scientifically worth having. Nothing here bears on EMC efficacy, safety, selectivity, or clinical readiness; it is repository tooling.
- **Incidental finding, outside my lane, not acted on:** `scripts/fast_checks.py`'s docstring names `tests/test_fast_checks.py` twice as the guard that keeps its member count honest, but no `test_fast_checks.py` exists in `scripts/tests/` (21 files listed, none matching). This is a dangling reference — UNKNOWN whether the file was renamed, moved, or removed. I did not investigate further and I made no change.

## Stop condition

**Set:** an empirically grounded, line-referenced integration requirement specification plus a reproduced demonstration of the discovery/importability behaviour, ready to consume the bundle on arrival.

**MET.** Twelve requirements S1-S12, each with a line reference or an executed command; the root cause reproduced in both directions (F1 exit 1 / F2 exit 0); two additional real failure modes reproduced (basename collision exit 2; the subdirectory budget hole, 6 run vs 2 counted); one hypothesis honestly refuted (D/E); and the hard budget number measured at 34.

**Partially blocked, and stated as such:** the specification cannot be *validated against the bundle*, because the bundle did not arrive within this run. That is pending input, not a failure of this lane.

## Tool-call and wall-clock count actually used

**16 tool calls** (all Bash; 2 of them parallel pairs). **Wall clock ~2 minutes** of tool time, `01:54:34Z` to `01:56:36Z` — well inside the ~40-minute / ~40-call target. I returned as soon as the stop condition was met rather than padding.

## Next concrete action

**One successor, for this lane, when the bundle lands:** check the delivered files against S1-S9 in order — flat `scripts/<identifier>.py`; flat `test_<unique>.py` in `scripts/tests/`; the `sys.path` preamble of S6 present; no `__init__.py`; no shadowed names — then run `python3 scripts/tier_budget.py` to re-measure live headroom against the bundle's actual test-function count, and only then attempt the 9 static findings **against the real code**, discarding any that cannot be reproduced. Do not port either malformed diff; re-derive each change from the file.

**Blocked until then**, and I decline to invent adjacent work: the honest state of this lane is "contract established, awaiting input", and the useful thing is to stop here rather than to manufacture a second deliverable.

result: Lane 11 receiving contract established empirically — the source-index bundle's discovery failure is reproduced as a missing `sys.path` preamble (ModuleNotFoundError at collection, exit 1) rather than a missing `__init__.py`; specification S1-S12 is line-referenced to `tier_budget.py`/`preflight.sh`, the `commit-loop` tier measures 1466/1500 giving a hard 34-test-function ceiling with no budget change needed, and a previously unrecorded budget hole was measured (tests in a subdirectory of a tier dir run under pytest but are counted by nobody: 6 run vs 2 counted).
