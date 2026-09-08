> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

## Worker

**W11d**, lane 11 refill (tier-hosting adjudication) — OPUS-CAPACITY-CAMPAIGN-20260908. Adjudicator only: I authored, delivered and proposed **no** version of `scripts/source_reuse_index.py` or its test file. W11b remains sole owner of source-index code changes.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) from my own system context. No environment variable in this container names a served model. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` start: `Tue Sep  8 02:34:37 UTC 2026` · `date -u` end: `Tue Sep  8 02:37:02 UTC 2026`

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — literal output (four long proxy host-list variables marked as elided; they match only on the substring `anthropic` inside a no-proxy list and name no model):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=… (proxy host list, elided)
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
GLOBAL_AGENT_NO_PROXY=… (proxy host list, elided)
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=… (proxy config, elided)
NO_PROXY=… (proxy host list, elided)
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=… (proxy host list, elided)
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**HEAD actually read: `7d081218f107363573573e6d102e4334567adf77`**, identical at start and end of my run. This is neither the brief's frozen `92abbcb905cacf07f14b238db50d1b98f6590374` nor W11c's `b9a0257e6acff53ad22535cf2adf261313e0b250` nor W14b's `92abbcb90`; the checkout keeps advancing as the coordinator lands sibling reports. I record what I read.

**Write isolation honoured.** Zero files created or modified under `/home/user/Rare-cancers`. All execution and all scratch output under `/tmp/claude-0/w11d/`. No git write operation. No network. I did not run `scripts/preflight.sh`. I changed no budget file, raised no ceiling, deleted no test, added nothing to any tier, and do not propose the 30-test gate.

---

## Question

Taken from `scripts/tier-budgets.json`'s own `_how_to_raise_a_ceiling`, which pre-empts a ceiling edit and names the two sanctioned alternatives:

**(a) Is there a cheaper tier that could host the six implementable §2 items, and (b) has anything currently in the commit-loop tier stopped earning its place?**

Open because W11c's adjudication stopped at the arithmetic — ≥21 test functions needed against 16 post-placement headroom — and explicitly deferred the routing question to a successor. Neither half has been measured. The `_how_to_raise_a_ceiling` guidance has been quoted in this lane twice but never executed against.

---

## Prior-work check

```
$ git ls-files | grep -E '(^|/)tests?/' | sed -E 's#/[^/]+$##' | sort -u
research/autonomy/tests
research/manuscripts/tests
research/modalities/tests
scripts/tests
systems/tests
```

Exactly five tracked test directories, and every one is claimed by a tier. There is **no unbudgeted tracked test directory** to route into.

```
$ grep -rn 'tier_budget' .github/workflows/ scripts/ --include='*.yml' --include='*.sh'
scripts/preflight.sh:1507:if python3 scripts/tier_budget.py --check; then
```

The budget gate has exactly one call site and no workflow runs it.

```
$ ls pytest.ini setup.cfg tox.ini pyproject.toml conftest.py
ls: cannot access 'pytest.ini': No such file or directory        (and the other four, likewise)
```

No pytest configuration and no `testpaths` anywhere — confirmed independently, matching what `scripts/preflight.sh` asserts in its own comment. Nothing is collected by accident; every directory that runs is named explicitly by a caller.

Reports read in full: `reports/W11b-source-index-consolidated-repair.md` (1854 lines, skimmed for the delivered pair and the §2 quotation), `reports/W11c-source-index-divergence-adjudication.md` (329 lines, in full), `reports/W14b-guard-coverage-sweep.md` (opening 120 lines, for its method-limits framing on the same class of measurement). `COMMON-BRIEF.md`, `CLOSED-WORK.md` and `CORPUS-CONTEXT.md` read in full.

I confirm I am **not** replaying: the arbitrary ceiling increase, the 30-test gate, PUB-EMC-CLASSIFICATION, or any Brenca route. I did **not** re-adjudicate D7 or D8; I carry W11c's decline-on-merits recommendation forward unchanged. I did not consult the frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/`, and I make **no** novelty or absence claim that would require it — every statement below is a measurement of the live checkout at `7d08121`, which is strictly newer than the corpus's `93b` base, and I did not copy or overlay the corpus.

---

## Method / inputs

Live checkout `/home/user/Rare-cancers` @ `7d081218f107363573573e6d102e4334567adf77`. Files read in full: `scripts/tier_budget.py` (172 lines), `scripts/tier-budgets.json`. Files read in part: `scripts/preflight.sh` (lines 1195–1400, 1500–1515, plus a targeted grep over all 1650+ lines), `.github/workflows/tests.yml` (lines 430–570).

One analysis script, `/tmp/claude-0/w11d/analyze.py`, written and run outside the repository. It re-uses `tier_budget.count_dir` by import so my per-directory numbers are produced by **the repository's own counting code**, not by a re-implementation, then adds: per-file test-function counts by AST; a name-mention scan of each of the 102 commit-loop test files against 6,747 tracked non-tier files (`.py .sh .yml .yaml .json .md .cfg .ini .toml`); and skip/`importorskip` detection.

**Environment limit that shaped the method, stated up front: `pytest` is not installed in this container.** `/usr/local/bin/python3 -m pytest` → `No module named pytest`, exit 1; likewise `/usr/bin/python3` and `/usr/bin/python3.11`. So `--collect-only` was impossible and **the reachability measurement in §3 is static, not dynamic.** This is the same population-difference W14b recorded for the dev sandbox versus CI.

---

## Result

### 1. The full tier table, measured by execution

`python3 scripts/tier_budget.py`, exit 0, at `7d08121`:

| Tier | Directories (membership rule) | Files | Measured | Ceiling | Headroom | Shadowed | Default preflight loop | `PREFLIGHT_TESTS=1` / `FULL=1` | `PREFLIGHT_PAPER` set | `tests.yml` (every push) | Class |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **commit-loop** | `scripts/tests`, `research/autonomy/tests`, `systems/tests` | 102 | **1466** | 1500 | **34** | 0 | **NO** — skipped, prints "SKIPPED -- PREFLIGHT_TESTS=1 runs them" | YES (`systems/tests` only when `RUN_TESTS=1`, which both flags set) | **NO** — `RUN_SELECTOR_TESTS=0` | **YES**, whole directories | PRIMARY |
| **paper-guards** | `research/manuscripts/tests` | 111 | **966** | 1000 | **34** | 0 | **NO** | YES (`RUN_TESTS=1`) | YES — runs in full in every paper gate | **YES**, whole directory | PRIMARY |
| **modalities** | `research/modalities/tests` | 436 | **7247** | 7500 | **253** | 0 | **NO** | YES via `PREFLIGHT_MODALITIES=1` / `FULL=1`; selector-scoped or full | YES — scoped to the named paper's deposit modules | **YES**, whole directory | PRIMARY |

Per-directory decomposition, produced by importing `tier_budget.count_dir` (PRIMARY):

| Directory | Tier | Files | Test functions |
|---|---|---|---|
| `scripts/tests` | commit-loop | 21 | 218 |
| `research/autonomy/tests` | commit-loop | 65 | 880 |
| `systems/tests` | commit-loop | 16 | 368 |
| `research/manuscripts/tests` | paper-guards | 111 | 966 |
| `research/modalities/tests` | modalities | 436 | 7247 |

**Verbatim, exit 0:**
```
   ok    commit-loop             1466/1500  test function(s) in 102 file(s)
   ok    modalities              7247/7500  test function(s) in 436 file(s)
   ok    paper-guards             966/1000  test function(s) in 111 file(s)
```

My `commit-loop 1466/1500` **independently reproduces W11c's figure** at a different HEAD (`7d08121` vs `b9a0257`). Per the dispatch I did not coordinate with any concurrent worker; this is my own measurement and it happens to agree.

**Three properties of the membership rule that matter for hosting, read out of `tier_budget.py` rather than assumed:**

1. **Membership is purely by directory, with no subject test.** `count_dir(rel)` walks `spec["directories"]`; nothing inspects what a test is about. A file's tier is decided by where it sits, full stop.
2. **`count_dir` uses `os.listdir`, not a recursive walk.** A test file placed in a *subdirectory* of a tier directory would be counted by **no tier at all** while still being collected by `tests.yml`'s directory-level pytest invocation. This is a real hole in the ceiling. **I measured it and found it unexploited: all five tier directories have `subdirs=0`, `nested_test_files=0`.** I report it as a latent defect and explicitly do **not** recommend using it — routing tests into a subdirectory to escape a ceiling is exactly the shape `_how_to_raise_a_ceiling` and `amendment_guard` exist to refuse.
3. **An unparseable file counts as 1, deliberately** ("counting it as zero would let a broken file buy headroom"). Zero unparseable files in the commit-loop tier.

**What actually runs each tier, stated plainly:** since 2026-09-02, on trimcrae's decision, **no tier runs in the default commit loop.** The only tier-related thing the default loop executes is `scripts/tier_budget.py --check` itself, at `preflight.sh:1507`, unconditional, ~0.1 s. `tests.yml` is the authority and runs all five directories in one pytest step on every push:

```
python -m pytest research/modalities/tests research/manuscripts/tests systems/tests scripts/tests
  research/autonomy/tests -q --continue-on-collection-errors --durations=25 -n 4 --dist loadfile
```

### 2. Per-item hosting analysis for the six implementable items

Item costs are **W11c's**, carried forward unchanged and re-marked `PREDICTION` — they are estimates of tests that do not exist, and I wrote none. Total for the six: **15**.

Every one of the six is a test of `scripts/source_reuse_index.py`, an offline, dependency-free, corpus-only lookup helper. There are exactly **five** directories it could be placed in, so the hosting question has exactly five candidate answers:

| Candidate directory | Tier it would join | Headroom before | Headroom after +15 | Legitimate by that tier's stated subject? | Runtime consequence of hosting it there |
|---|---|---|---|---|---|
| `scripts/tests` | commit-loop | 34 (16 after W11b's 18-fn pair) | 19 (1 after the pair) | **Yes** — "the pure-logic suites… none of it is about a manuscript". Exact fit. | Runs in `tests.yml` and under `PREFLIGHT_TESTS/FULL`. **Excluded from the paper tier** (`PREFLIGHT_PAPER` sets `RUN_SELECTOR_TESTS=0`), so it costs a publication run **nothing**. |
| `research/autonomy/tests` | commit-loop | same shared pool | same | Subject mismatch (leases, receipts, cadence, ledger) but same tier — **no budget relief whatsoever** | identical to above |
| `systems/tests` | commit-loop | same shared pool | same | Subject mismatch (the systems model) — **no budget relief whatsoever** | identical to above |
| `research/manuscripts/tests` | paper-guards | **34** | **19** | **No.** "The papers' own guards — the only suite whose subject is the thing being published." A lookup helper is not a manuscript claim. | **Strictly more expensive**: this suite runs **in full in every paper gate**, which the commit-loop tier is deliberately excluded from. |
| `research/modalities/tests` | modalities | **253** | **238** | **No.** "The science suites for every route." A lookup helper is not a route or a modality. | **Strictly more expensive**: 72 % of every publication run; and the paper-scoped selector picks modules by a paper's deposit, which will never name this helper — so it would ride the full-tier path. |

Per-item, since the dispatch asks item by item — the hosting answer is **identical for all six**, because tier membership is decided by the file's directory and all six items' tests would live in one test file for one helper:

| # | Item | Min new test fns | Tiers that could host by directory membership | Cost to each tier's headroom | Class |
|---|---|---|---|---|---|
| D1 | `KNOWN_*` rename | 1 | commit-loop (any of 3 dirs) · paper-guards · modalities | −1 to whichever tier receives it | PREDICTION |
| D2 | `admitted_fields` / `FIELD_NOT_ADMITTED` | 4 | same three | −4 | PREDICTION |
| D3 | sha256 / `PROVENANCE_UNVERIFIED` (narrowed offline form only) | 3 | same three | −3 | PREDICTION |
| D4 | `referenced_origin_missing` | 2 | same three | −2 | PREDICTION |
| D5 | Zenodo concept advisory (`conceptdoi`-carrying records only) | 3 | same three | −3 | PREDICTION |
| D6 | `base_revision` surfaced | 2 | same three | −2 | PREDICTION |
| | **Six-item total** | **15** | | commit-loop 34→19 (16→1 post-placement) · paper-guards 34→19 · modalities 253→238 | PREDICTION |
| D7 | current-vs-superseded | — | — | **DECLINED ON MERITS**, W11c, carried forward unchanged | — |
| D8 | advisory title candidates | — | — | **DECLINED ON MERITS**, W11c, carried forward unchanged | — |

**Answer to half (a): there is no cheaper tier. `scripts/tests` is already the cheapest correct home, and the two tiers with more headroom are both more expensive to run and both wrong by subject.**

The word "cheaper" in `_how_to_raise_a_ceiling` cannot mean "has more headroom" — the file's own `_what_this_does_not_measure` says a count is not a cost and "a tier over budget may be entirely sound and simply in the wrong place." Read as runtime cost, the ordering is the reverse of the headroom ordering: modalities has 253 spare functions and is the **most** expensive tier in the repository (72 % of every publication run, 0 failures in eight committed `PREFLIGHT_FULL` logs); paper-guards has the same 34 as commit-loop and runs in the paper gate that commit-loop is exempt from; commit-loop is the only tier that costs a *publication* run nothing. Moving a lookup helper's tests into modalities would buy 253 functions of paper headroom by making every publication gate slower and by filing a lookup helper as a science route. That is accretion with a fig leaf, and it is the precise failure this file was written to stop.

**One honest qualification, and it is the strongest thing I can say for a move:** the numbers do fit in modalities and do not fit in commit-loop. 18 + 15 = 33 against 34 leaves **1** function of commit-loop headroom for the entire rest of the repository, which is not a survivable margin — the tier grew 789 → 1,119 in ten days once. So "place everything in `scripts/tests`" is arithmetically possible and operationally reckless. That is an argument for **landing fewer items**, not for relabelling them as modalities.

### 3. Which commit-loop tests no gate reaches — measured, and the answer is zero

**Measured result: 0 of 102 commit-loop test files, and 0 of 1466 test functions, are unreachable by every gate, workflow and chain.** Every file in all three directories is reached by `tests.yml`'s single pytest step on every push, and by `scripts/preflight.sh:1376` under `PREFLIGHT_TESTS=1` or `PREFLIGHT_FULL=1`. Both invocations name **directories**, not files, with no `--ignore` covering these three paths, and there is no `pytest.ini`/`testpaths` that could redirect collection.

| Reach question | Files | Test functions | Class |
|---|---|---|---|
| Reached by `tests.yml` on every push | **102 / 102** | **1466 / 1466** | PRIMARY |
| Reached by `preflight.sh` under `PREFLIGHT_TESTS=1` / `PREFLIGHT_FULL=1` | 102 / 102 | 1466 / 1466 | PRIMARY |
| Reached by the **default** preflight commit loop | **0 / 102** | **0 / 1466** | PRIMARY |
| Reached under `PREFLIGHT_PAPER=<paper>` | 0 / 102 | 0 / 1466 | PRIMARY |
| Not individually named anywhere outside the three tier directories (**heuristic, not reachability**) | 28 | 322 | SECONDARY |
| Unparseable files silently counted as 1 | 0 | — | PRIMARY |
| Shadowed test names (paid for, never run) | **0** | 0 | PRIMARY |

**Answer to half (b): nothing in the commit-loop tier has stopped earning its place by the measurable criterion — no test in it is dead, shadowed, or unreached.** The two failure modes the repository itself names — a shadowed `def test_` that "does not fail, it ceases to exist" (`tier_budget.py::_shadowed`), and a directory run by nothing (the 2026-08-22 selector suite, the 2026-08-27 autonomy suite, the 2026-09-01 `systems/tests` wiring) — are both **currently at zero**. Those three historical holes were each found and closed, and the closures hold at `7d08121`.

**The one structural oddity worth putting in front of a human, stated as a fact not a recommendation:** the tier named `commit-loop` is **not run by the commit loop**. Since 2026-09-02 all 1466 of its functions are opt-in, and `tier-budgets.json`'s own `why` already concedes this — "THESE ARE NOW OPT-IN (PREFLIGHT_TESTS=1) and out of both the default loop and any paper tier, so the ceiling protects CI's time and the opt-in run's, not the commit loop's." So the ceiling is real (it protects the `tests.yml` push gate and the FULL publication run) but the tier's *name* now misdescribes what it gates. That is a naming observation. It is **not** evidence that anything has stopped earning its place, and I decline to convert it into one.

**Method limits on §3, stated in the same terms W14b stated them for the same class of measurement:**

- **The 28-file "not individually named" list is a name-mention heuristic and is NOT a reachability finding.** It answers "does any file outside these three directories contain this basename?", which is a different question from "does anything run it". Because both callers name directories, a file can be mentioned by nothing and still execute on every push — and all 28 do. Publishing that list as "tests nothing runs" would be exactly the error W11c made on D7 and the review made on F4: reasoning from a string's presence or absence rather than from what the code does. I include the list only as a *documentation-coverage* signal.
- **Static reach is not execution.** `pytest` is absent from this container (verbatim: `No module named pytest`, exit 1, on three interpreters), so I could not run `--collect-only` and cannot report collected-test counts, collection errors, or which tests actually execute. A file can be reached by the invocation and still contribute zero assertions on a given box.
- **I found and corrected a false positive in my own detector, and report it against myself.** My first pass flagged nine files as carrying a module-level skip. Reading the nine showed **all nine are false positives**: my regex `^\s*pytest\.skip\(` matched *indented, in-function, conditional* skips (e.g. `systems/tests/test_modality_census.py:56` `pytest.skip("census not populated yet")` inside a test body). **Zero commit-loop files take an `allow_module_level=True` skip, and zero use `importorskip`.** The corrected count is what appears in the table; the uncorrected nine would have manufactured a spurious "these files don't run" finding.
- **Conditional in-function skips are real but unmeasured here.** Several tests skip when a committed artifact is absent or history is shallow (`test_a_review_names_what_it_read.py:82` "shallow history — nothing to measure over"; `test_a_score_must_derive_from_its_own_inputs.py:78` "no derived row in the committed ledger"). Under `actions/checkout@v4`'s default shallow clone, some of these may skip in CI. **How many, and how often, I did not measure and cannot measure without pytest.** That is the one place where a test could be paying rent and returning less than it appears to, and it is an open question I am handing on rather than answering.
- **Zero-headroom-per-file is not measured.** "Earning its place" in the fullest sense means guarding an incident that can still recur. `tier-budgets.json` says so directly — "a tier under budget can still be full of guards that measure nothing" — and I make **no** claim about the quality or continued relevance of any of the 1466 functions. I measured whether they run, not whether they are worth running. Adjudicating 1466 guards on merit is not a bounded task and I did not attempt it.

---

## Validation evidence

All **RUN** unless marked. Environment: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, `/usr/local/bin/python3`, repo `/home/user/Rare-cancers` @ `7d081218f107363573573e6d102e4334567adf77`. Scratch: `/tmp/claude-0/w11d/`.

**V1 — environment and HEAD, exit 0.** `date -u` → `Tue Sep  8 02:34:37 UTC 2026`; `git rev-parse HEAD` → `7d081218f107363573573e6d102e4334567adf77`. Repeated at end: `Tue Sep  8 02:37:02 UTC 2026`, same HEAD.

**V2 — `python3 scripts/tier_budget.py`, cwd repo root, EXIT=0.** Verbatim:
```
   ok    commit-loop             1466/1500  test function(s) in 102 file(s)
   ok    modalities              7247/7500  test function(s) in 436 file(s)
   ok    paper-guards             966/1000  test function(s) in 111 file(s)
```

**V3 — per-directory decomposition via `import tier_budget; tier_budget.count_dir(rel)`, EXIT=0.** Verbatim:
```
commit-loop    scripts/tests                  exists=True files=21 fns=218 shadowed=0
commit-loop    research/autonomy/tests        exists=True files=65 fns=880 shadowed=0
commit-loop    systems/tests                  exists=True files=16 fns=368 shadowed=0
commit-loop    TOTAL fns=1466 ceiling=1500 headroom=34
modalities     research/modalities/tests      exists=True files=436 fns=7247 shadowed=0
modalities     TOTAL fns=7247 ceiling=7500 headroom=253
paper-guards   research/manuscripts/tests     exists=True files=111 fns=966 shadowed=0
paper-guards   TOTAL fns=966 ceiling=1000 headroom=34
```

**V4 — every tracked test directory is claimed by a tier, EXIT=0.** `git ls-files | grep -E '(^|/)tests?/' | sed -E 's#/[^/]+$##' | sort -u` → exactly the five directories listed in Prior-work check. `ls research/tools` → `No such file or directory` (confirming W11c's finding that the original helper's home is untracked/inputs-only).

**V5 — non-recursive counting hole, measured unexploited, EXIT=0.** Verbatim:
```
scripts/tests subdirs=0 nested_test_files=0
research/autonomy/tests subdirs=0 nested_test_files=0
systems/tests subdirs=0 nested_test_files=0
research/manuscripts/tests subdirs=0 nested_test_files=0
research/modalities/tests subdirs=0 nested_test_files=0
```

**V6 — what runs the tiers, EXIT=0.** `tests.yml:540-543` verbatim:
```
        run: >-
          python -m pytest research/modalities/tests research/manuscripts/tests systems/tests scripts/tests
          research/autonomy/tests
          -q --continue-on-collection-errors --durations=25 -n 4 --dist loadfile
```
`preflight.sh:1330,1353-1355,1364,1371,1376` verbatim (gating chain):
```
[ "${RUN_TESTS:-0}" = "1" ] && SYSTEMS_TESTS="systems/tests"
RUN_SELECTOR_TESTS=0
[ "${PREFLIGHT_TESTS:-0}" = "1" ] && RUN_SELECTOR_TESTS=1
[ "${PREFLIGHT_FULL:-0}" = "1" ] && RUN_SELECTOR_TESTS=1
[ -n "${PREFLIGHT_PAPER:-}" ] && RUN_SELECTOR_TESTS=0
  echo "== pytest (pure-logic suites) == SKIPPED -- PREFLIGHT_TESTS=1 runs them; tests.yml runs all"
$PYTEST $PYTEST_PAR scripts/tests research/autonomy/tests $SYSTEMS_TESTS -q ... 
```

**V7 — budget gate has one call site, EXIT=0.** `grep -rn 'tier_budget' .github/workflows/ scripts/` → single hit `scripts/preflight.sh:1507`. Surrounding block read: unconditional in the default loop, `rc=1` on failure.

**V8 — no pytest config, EXIT=2 (all five absent).** `ls pytest.ini setup.cfg tox.ini pyproject.toml conftest.py` → five "No such file or directory".

**V9 — `python3 /tmp/claude-0/w11d/analyze.py`, EXIT=0.** 102 files, 6,747 corpus files scanned, `total fns: 1466` (reproducing V2 through an independent AST path), `unparseable: (none)`, 28 files / 322 functions individually unmentioned outside the tier directories, full list printed in transcript and summarised above.

**V10 — module-skip false positives run down, EXIT=0.** All nine flagged files inspected with `grep -n -B3 'pytest\.skip'`; all nine skips are indented in-function conditionals. Representative verbatim:
```
### systems/tests/test_modality_census.py
55-    if not graph["modalities"]:
56:        pytest.skip("census not populated yet")
### research/autonomy/tests/test_a_review_names_what_it_read.py
81-    if len(shas) < 20:
82:        pytest.skip("shallow history — nothing to measure over")
```
Corrected finding: **zero** module-level skips, **zero** `importorskip`, in the commit-loop tier.

**V11 — pytest unavailable, EXIT=1.** Verbatim:
```
/usr/local/bin/python3: No module named pytest
```
Reproduced on `/usr/bin/python3` and `/usr/bin/python3.11`. This is the limit that forced §3 to be static.

**PROPOSED (NOT RUN):**
- Every test-function count in the six-item table is W11c's estimate of tests that do not exist. I wrote none and ran none, by design — I am an adjudicator and may not author source-index tests.
- `pytest --collect-only -q scripts/tests research/autonomy/tests systems/tests --continue-on-collection-errors -p no:cacheprovider` — the dynamic reachability measurement that would convert §3's static reach into executed-test counts and expose conditional-skip frequency. **Cannot run here** (V11); it needs a box with pytest, i.e. CI.
- Re-running `scripts/tier_budget.py` **after** any placement rather than projecting the total. Not run because I placed nothing.

---

## Limitations

- **Static reach only.** Without pytest I measured which files an invocation *names*, not which assertions *execute*. Conditional in-function skips (V10) are unquantified, and under a shallow `actions/checkout` clone some may skip in CI. This is the one avenue by which a commit-loop test could be under-earning, and it remains **UNKNOWN**, not zero.
- **The 28-file unmentioned list is a heuristic and proves nothing about reachability.** Stated in §3 and repeated here because it is the finding most likely to be misquoted.
- **Test-cost figures are inherited predictions.** I re-used W11c's 15-function total for the six items rather than re-deriving it. If it is wrong, my headroom arithmetic (34 → 19, or 16 → 1 post-placement) moves with it. The qualitative conclusion — modalities is not cheaper — does not depend on the number.
- **"Cheaper" is my reading of `_how_to_raise_a_ceiling`.** The file does not define the word. I read it as runtime cost, supported by `_what_this_does_not_measure`'s explicit statement that the count is not a cost; a reader who reads it as headroom would reach the opposite routing answer. I flag the ambiguity rather than hiding behind my reading.
- **I did not adjudicate any of the 1466 functions on merit.** "Nothing has stopped earning its place" is a claim about *dead* tests — unreached, shadowed, or unparseable — and about nothing else. A tier can be fully alive and still full of guards for incidents that cannot recur; measuring that is not a bounded task and I did not attempt it.
- **HEAD drift.** All numbers are the tree at `7d08121` at 02:34–02:37 UTC on 2026-09-08 and will move as the campaign lands reports. Concurrent workers have measured tier totals separately; I did not coordinate and report only my own.
- **No scientific claim.** This is the budget of a read-only lookup helper's test suite. It establishes nothing about EMC, NR4A3, any therapeutic, any patient, or any degrader. No efficacy, safety, selectivity, therapeutic-window or clinical-readiness claim is made or implied. There is no wet lab.

---

## Stop condition

**Set:** (1) the full tier table measured by execution; (2) a per-item hosting analysis for the six implementable items; (3) a measured list of commit-loop tests no gate reaches, with the method's limits stated.

**MET, all three.**

1. Three tiers, ceilings, measured totals, membership rules and what runs each — measured by `scripts/tier_budget.py` (exit 0) and decomposed through the repository's own `count_dir`, cross-read against `preflight.sh` and `tests.yml`.
2. Six items costed against all five candidate directories. **Answer: no cheaper tier exists.** `scripts/tests` (commit-loop) is already the cheapest correct home; modalities has 253 spare functions and is the most expensive tier to run and wrong by subject; paper-guards has identical headroom, runs in the paper gate commit-loop is exempt from, and is wrong by subject.
3. **The list is empty: 0 of 102 files, 0 of 1466 functions unreached.** Zero shadowed, zero unparseable, zero module-level skips. **Answer: nothing in the commit-loop tier has stopped earning its place** by any criterion I could measure. Limits stated, and my own nine-file false positive found, overturned and reported against myself.

So the dispatch's own sentence is the finding: **"No cheaper tier exists and nothing has stopped earning its place"** is the complete answer, and it is what the evidence shows. Both sanctioned alternatives in `_how_to_raise_a_ceiling` are therefore **exhausted for this work**, which leaves only its third option — a ceiling raised *with* the measurement that justifies it and declared in `amendments.jsonl` — and that is trimcrae's decision, not a worker's. I did not take it and do not recommend a cycle take it to land its own test, which the same file names as the shape `amendment_guard` exists to refuse. Returning immediately.

---

## Tool-call and wall-clock count actually used

**11 tool calls** (all Bash), **~2.5 minutes wall clock** (02:34:37 → 02:37:02 UTC). Well inside the ~40-call / ~40-minute target.

---

## Next concrete action

**One task, for W11b as sole code owner, unchanged in shape from W11c's recommendation but now with the tier question answered underneath it: place the 18-function pair plus D6 and D4 only, in `scripts/tests`, and stop there.** 1466 → 1488/1500, verified by re-running `scripts/tier_budget.py` after placement rather than projecting it. That is the cheapest correct tier, it costs the publication gate nothing (`PREFLIGHT_PAPER` excludes it), and it leaves 12 functions of shared headroom.

**D1, D2, D3, D5 should now be closed as "no viable home", not carried as pending work.** The routing question they were deferred for has been answered by measurement: there is no cheaper tier, and nothing is available to delete in exchange. Adding all four takes commit-loop to 1499/1500 — one function of headroom for the entire repository — which is not a margin, and buying room by filing a lookup helper's tests as a science modality would make every publication run slower to protect a number. If those four behaviours are genuinely wanted, the honest next step is a **declared ceiling amendment** put to trimcrae with this measurement attached, not a routing manoeuvre by a worker.

**D7 and D8 remain declined on merits** (W11c), carried forward here unchanged and not re-adjudicated, so the next reader of §2 does not re-open them.

**One separable follow-up, outside this lane and small:** `tier_budget.count_dir` counts non-recursively, so a test file in a subdirectory of any tier directory would be budgeted by nothing while still running on every push. Measured unexploited today (all five directories have zero subdirectories), so this is a latent hole, not a live defect — but it is the same "a rule nothing measures" shape the file was written for, and a one-line `os.walk` would close it. Not mine to author.
