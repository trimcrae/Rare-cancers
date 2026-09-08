<!-- collected 2026-09-08T03:38:26Z by campaign coordinator; agent id ad21852a7c4f3b0ba; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ad21852a7c4f3b0ba.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Scratch deleted, live tree unchanged. Report follows.

---

## Worker

**W24d**, repair-adjudication lane (complete the D1/D2/D3 × baseline/R07/R08 table), OPUS-CAPACITY-CAMPAIGN-20260908. **I ruled on nothing and landed nothing.**

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) from my own system context. No environment variable in this container names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start: `Tue Sep  8 03:30:17 UTC 2026`** · **end: `Tue Sep  8 03:33:41 UTC 2026`**

`git rev-parse HEAD` **start: `215ed8e78f83d1e5acdbb726317dfd0eeed8f6a1`** · **end: `215ed8e78f83d1e5acdbb726317dfd0eeed8f6a1`** — **HEAD did not move under me**, unlike every prior worker in this chain. `git status --porcelain` → **0 lines at start and 0 lines at end**. No git write operation of any kind, no network call, no paid API, no GPU, no subagent, no skill.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (identical at start and end; **no field names a model**; the five long proxy-exclusion variables that match only on the substring `anthropic` — `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `JAVA_TOOL_OPTIONS`, `npm_config_noproxy` — are elided as marked, everything else verbatim):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=…   [proxy exclusion list, matched on "anthropic"]
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
GLOBAL_AGENT_NO_PROXY=…   [proxy exclusion list]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=…   [proxy exclusion list]
NO_PROXY=…            [proxy exclusion list]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=…   [proxy exclusion list]
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

**Do drift classes D1 (gene-integer), D2 (probe-label) and D3 (probe-count) discriminate between R07 (W14c's patch) and R08 (W14d's patch) on `research/modalities/emc_fourth_cohort_quant.py --check`, measured on one table with an unpatched control in every row?**

Open because no worker had run all three classes against both patches. W14c ran D1/D2 against R07 only (D3 did not exist yet). W14d ran D1/D2/D3 against R08 only. W24b flagged R07-against-D3 as `PROPOSED (NOT RUN)`. W24c ran D3 against all three arms but explicitly left **D1 and D2 against R07 unmeasured in its own hands**, and its record is a coordinator transcription (SECONDARY), not a primary transcript. The nine-cell surface therefore did not exist anywhere.

## Prior-work check

Read in full before any execution: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `reports/W14c-fake-guard-repair-proof.md`, `reports/W14d-fourth-cohort-guard-repair.md`, `reports/W24-repair-routing-index.md`, `reports/W24b-r07-r08-either-or.md`, `reports/W24c-d3-control-against-r07.md`.

Targeted searches actually run:

```
grep -n -i -E "R07|R08|discrimin|D1|D2|D3" W24-repair-routing-index.md   -> :137, :138, :139, :170  (the either/or flag + decision row D01)
grep -n -i -E "discrimin|D1|D2|D3|capabilit" W24b-r07-r08-either-or.md   -> :227(f), :239, :260-262, :342, :376
grep -n '^```' W14c-fake-guard-repair-proof.md                            -> the R07 diff fence at 270..377
find . -name 'tracked_tree_guard*' -not -path './.git/*'                  -> ./research/manuscripts/tests/tracked_tree_guard.py
```

What they showed, and what I am therefore **not** replaying: W24 row 139(b) credits R08 with the D3 *capability*; W24b `:239` already corrected that to "capability is in both patches, what is only in R08 is the executed test". I did not re-derive that reading — I executed it. W24b `:376` named exactly this run as the next action and scoped it to D3; my dispatch widened it to D1/D2 as well, which is the part nobody had done. I replayed no closed scientific gate: **no EMC scientific finding, no ICD-O/classification reading, no Brenca/Hofvander/Davis route, no lane-11 source-index file, no network attempt at the Ensembl fetch or the vendor manifest**, no preflight run, nothing applied to the tree.

**Target-file identity verified, not assumed** (HEAD had moved four times across the prior workers): `sha256sum research/modalities/emc_fourth_cohort_quant.py` → `c5180c11a57463337d023fda58fb5516833d1eb4e4787095e15c35af5eb5965f`, **matching the expected value in my dispatch and the sha W14d read at `3f5fc95d…` and W24b read at `98a0833f…`**. Neither repair has landed; the file has not moved since either was cut.

## Method and inputs

- **Live checkout `/home/user/Rare-cancers` at HEAD `215ed8e7…`, READ-ONLY.** The only things read out of it were the seven report/brief files, the six generator inputs, `research/modalities/tests/`, and `research/manuscripts/tests/tracked_tree_guard.py`.
- **Every execution ran in the scratch copy `/tmp/claude-0/w24d/`, which no longer exists** (deleted before returning; `ls` → `No such file or directory`; free space on `/` 18 G at end). The copy was made with
  `tar --exclude=./.git --exclude=./__pycache__ -cf - -C research/modalities <6 files + tests/> | tar -xf - -C /tmp/claude-0/w24d/pristine`.
  `HERE = os.path.dirname(os.path.abspath(__file__))` (line 64) makes every artifact path resolve inside the scratch copy, so **no run could reach the tree**. `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPYCACHEPREFIX=/tmp/claude-0/w24d/pycache` were exported in every execution call; unlike W14c's part 2, I created **no `__pycache__` under `research/modalities`**.
- **`emc_fourth_cohort_quant.py --check` was never run against the live tree.** Every one of the 12 `--check` invocations below used the scratch copy.
- Baseline hashes of the scratch pristine copy, recorded before anything ran, and **all four match the committed values W14c/W14d/W24b report**:
  `emc_fourth_cohort_quant.py c5180c11…`, gene TSV `8aa3064a…`, probe TSV `c689e0fd…`, JSON `1769b3f0…`.
- Interpreter CPython **3.11.15** (`/usr/local/bin/python3`); test runner **pytest** at `/root/.local/bin/pytest`. Linux, no network.
- **Arm construction.** `base` = the pristine file untouched. `r07` = the diff extracted verbatim from `W14c-fake-guard-repair-proof.md` lines 271-376 (the `” ```diff ”` fence body, 106 lines, 6 hunks) and applied with `git apply` — see the rejection below. `r08` = rebuilt from W14d's six documented edits by exact-string substitution, each substitution asserting `count == 1` before replacing, so a silent mismatch would have aborted the build.
- **Cell protocol.** Each cell got a **freshly restored** run directory (`rm -rf` then re-copy of all five pristine artifacts plus that arm's script), so no cell could inherit another's state. Each arm ran its `clean` cell first, so a failure can be told from a degraded environment.

## Result

### 1. Applying R07 verbatim — it does **not** apply, and this contradicts the SECONDARY W24c record

`PRIMARY`. The diff as published in W14c has **no file header** — it opens directly on `@@ -567,7 +567,7 @@`. Verbatim:

```
$ git apply --check -v /tmp/claude-0/w24d/R07.patch
error: patch fragment without header at line 1: @@ -567,7 +567,7 @@
EXIT=128
```

Quoted rather than hand-adapted, as instructed. I then confirmed the **hunk content itself is sound** without touching it — GNU `patch(1)`, which does not require a header when the target is named on the command line, accepts it:

```
$ patch --dry-run -p0 emc_fourth_cohort_quant.py < /tmp/claude-0/w24d/R07.patch
checking file emc_fourth_cohort_quant.py
EXIT=0
```

To get a `git apply` arm at all I prepended **exactly two mechanical lines** — `--- a/emc_fourth_cohort_quant.py` and `+++ b/emc_fourth_cohort_quant.py` — and changed **nothing inside any hunk**:

```
$ git apply --check -p1 -v /tmp/claude-0/w24d/R07-headed.patch
Checking patch emc_fourth_cohort_quant.py...
CHECK_EXIT=0
$ git apply -p1 /tmp/claude-0/w24d/R07-headed.patch
APPLY_EXIT=0
rej_files=0        # no .rej, no fuzz, no hunk offset reported
$ python3 -c "import ast; ast.parse(open('emc_fourth_cohort_quant.py').read())"  -> syntax OK
```

**Disposition:** W24c's transcribed claim that "`git apply --check` and `git apply` both exit 0, no fuzz, no rejection, no hunk offset" is **true of the headed form and false of the verbatim form**. Since W24c's own transcript is lost, I cannot tell whether it added the header silently or extracted a different span. Either way the corrected statement for the owner is: **R07's hunks apply cleanly at this sha with zero fuzz, but the diff as it stands in the report is not machine-applicable without a two-line file header.** That is a packaging defect in the report, not in the repair.

### 2. The completed nine-cell table (plus the three clean controls)

All twelve cells `PRIMARY`. `MODULE_EXIT` is the exit code of `python3 emc_fourth_cohort_quant.py --check` itself, read directly (`echo "MODULE_EXIT=$?"` immediately after the module call, no pipeline in between). "artifact after" is the `sha256sum` of the drifted file taken on disk **after** the check ran.

| Cell | Arm | Drift class | `--check` stdout | **MODULE_EXIT** | drifted artifact on disk after | Verdict |
|---|---|---|---|---|---|---|
| A0 | baseline (unpatched) | clean | `no drift: the derive half reproduces offline` | **0** | all three committed shas | control green |
| A1 | baseline | **D1** gene int `491`→`1000491` | `no drift: the derive half reproduces offline` | **0** | `8aa3064a…` — **silently restored** | defect reproduced |
| A2 | baseline | **D2** probe label →`BOGUS_GENE_XYZ` | `no drift: the derive half reproduces offline` | **0** | `c689e0fd…` — **silently restored** | defect reproduced |
| A3 | baseline | **D3** probe count `0`→`1000000` | `no drift: the derive half reproduces offline` | **0** | `e7b31a6e…` — left corrupt, **undetected** | defect reproduced |
| B0 | **R07** | clean | `no drift: the derive half reproduces offline` | **0** | all three committed shas | control green |
| B1 | **R07** | **D1** | `DRIFT: ['emc-fourth-cohort-gene-counts.tsv']` | **1** | `2168ab58…` — **not restored** | caught |
| B2 | **R07** | **D2** | `DRIFT: ['emc-fourth-cohort-probe-counts.tsv']` | **1** | `f273b0c0…` — **not restored** | caught |
| B3 | **R07** | **D3** | `DRIFT: ['probe_counts_sha256']` | **1** | `e7b31a6e…` — **not restored** | caught |
| C0 | **R08** (rebuild) | clean | `no drift: the derive half reproduces offline` | **0** | all three committed shas | control green |
| C1 | **R08** | **D1** | `DRIFT: ['emc-fourth-cohort-gene-counts.tsv']` | **1** | `2168ab58…` — **not restored** | caught |
| C2 | **R08** | **D2** | `DRIFT: ['emc-fourth-cohort-probe-counts.tsv']` | **1** | `f273b0c0…` — **not restored** | caught |
| C3 | **R08** | **D3** | `DRIFT: ['probe_counts_sha256']` | **1** | `e7b31a6e…` — **not restored** | caught |

**The nine patched/unpatched cells are complete and the two patched arms are indistinguishable in all nine.** Cell for cell, R07 and R08 produce the **same exit code, the same literal drift list string, and the same on-disk artifact hash**. On D1/D2/D3 there is no capability discriminator between them — not only on D3, as W24c settled, but on all three classes.

Two secondary confirmations that fell out of this:
- **Every drift sha reproduces W14d's published intermediates exactly** — `2168ab58…` (D1), `f273b0c0…` (D2), `e7b31a6e…` (D3) — so my drift constructions are the same experiment W14d and W24c ran, independently rebuilt from the report text.
- **R07's D3 cell (B3) is measured for the first time in a primary record.** W24b left it `PROPOSED (NOT RUN)`; W24c reported it only through a transcription. R07 catches D3 via the JSON key path, printing `['probe_counts_sha256']` — the identical mechanism W14d predicted for R08.

### 3. Regression, all three arms

`PRIMARY`. Run per arm on a freshly restored copy.

| Arm | `pytest tests/test_emc_fourth_cohort_quant.py -q` | PYTEST_EXIT | `--selftest` | SELFTEST_EXIT | TSVs after |
|---|---|---|---|---|---|
| baseline | `20 passed in 0.18s` | **0** | `selftest: 0 failure(s)` | **0** | both committed shas |
| **R07** | `20 passed in 0.19s` | **0** | `selftest: 0 failure(s)` | **0** | both committed shas |
| **R08** | `20 passed in 0.20s` | **0** | `selftest: 0 failure(s)` | **0** | both committed shas |

**A degraded-environment episode, recorded rather than smoothed.** My first regression pass returned `PYTEST_EXIT=4` for **all three arms** with `ModuleNotFoundError: No module named 'tracked_tree_guard'`. That is a collection error from the repository's conftest, caused by my scratch copy containing `research/modalities/tests/` but not `research/manuscripts/tests/tracked_tree_guard.py` — an artefact of my isolation, not a property of any patch. I did **not** weaken, skip or deselect anything: I copied the missing module into the scratch tests directory and re-ran, giving 20/20 on every arm. Because the failure hit all three arms identically it never had discriminating power; I report it because a `4` is not a pass and the distinction matters.

### 4. The R08 rebuild caveat — carried forward, and **reproduced**

`PRIMARY` for my own count, `SECONDARY` for W24c's.

W24c flagged an unexplained off-by-one: its R08 rebuild produced **93** diff lines against W14d's stated "**92** diff lines including context". **I reproduce 93 exactly.**

```
$ diff -u pristine/emc_fourth_cohort_quant.py r08/emc_fourth_cohort_quant.py | wc -l     -> 93
$ diff -u … | tail -n +3 | wc -l   (hunk body only, excluding the ---/+++ header)         -> 91
$ diff -u … | grep -c '^@@'                                                               -> 6
```

So the count is 93 with the two-line file header and 91 without; **neither is 92**, and the off-by-one survives in both directions. My rebuild is therefore the same artifact W24c built, and the discrepancy against W14d's stated figure is real and still unexplained. The honest reading: **W14d's R08 is not machine-applicable at all** — its report gives abbreviated hunk headers (`@@ -589,593`, `@@ -830,831`), no file header, and presents the `--check` branch as a code block rather than a hunk, so any R08 arm anywhere is a **REBUILD of R08 as documented, not R08 as W14d executed it**. Both my C-column cells and W24c's carry that caveat. R07 does not: its hunks are complete and apply with zero fuzz once headed.

Possible benign explanations for the 92/93 gap (I did not test any of them, so they are **UNKNOWN**): W14d counted a diff produced by a different tool or context width, counted before adding a docstring line, or counted its hand-written figure rather than a `wc -l`. **What is measurable is that a faithful rebuild from its published text gives 93/91, and that the rebuilt script passes every acceptance row W14d reported.**

### 5. Size, for the owner's already-tabulated axes

`PRIMARY`, offered only because the owner's remaining axes are size and test count (W24b priced both).

| | baseline | R07 applied | R08 rebuilt |
|---|---|---|---|
| file lines | 958 | **995** (+37) | **974** (+16) |
| `diff -u` lines vs baseline | — | **108** (6 hunks) | **93** (6 hunks) |
| resulting sha256 | `c5180c11…` | `af55c4a96713675d32190c6746dbf265651c92ca50036729d58723af6069b4d7` | `3c4bf3d662c37fa545dea80a94822d212096695ab3524c5049434ee8e29fe08f` |

**I rule on nothing.** The two patches are behaviourally identical on every class anyone has defined; the residual differences are size, applicability of the published diff, and executed-test provenance, and the choice is the module owner's.

## Validation evidence

Environment for every run: CPython 3.11.15, pytest at `/root/.local/bin/pytest`, Linux, no network, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w24d/pycache`, working directories under `/tmp/claude-0/w24d/` only.

**RUN — scratch baseline matches the committed artifacts:**
```
c5180c11a57463337d023fda58fb5516833d1eb4e4787095e15c35af5eb5965f  emc_fourth_cohort_quant.py
8aa3064a97a496a8fa09ef4ae8e472a612318e49ea91d0daac915a3b8fa180cc  emc-fourth-cohort-gene-counts.tsv
c689e0fd4f5c8cda0f132cd8ce42f039f691bf94cb8d81d3f622886e2bdd26fc  emc-fourth-cohort-probe-counts.tsv
1769b3f0ee01f1a640dabc6c4f36ce86630ff62f87249400e070a4638fcf5165  emc-fourth-cohort-quant.json
```

**RUN — R07 application** (verbatim rejection and headed success, both quoted in §1 above; `git apply --check` `CHECK_EXIT=0`, `git apply` `APPLY_EXIT=0`, `rej_files=0`).

**RUN — R08 rebuild:** `edits applied: ['E1-sig', 'E2-probe-write', 'E3-derive-sig', 'E4-passthrough', 'E5-gene-write', 'E6-check-branch']`, `BUILD_EXIT=0`, `syntax OK`. Each of the six substitutions asserted a unique match before replacing.

**RUN — the twelve cells**, verbatim excerpts from `matrix.log` (baseline D1/D3 and both patched D3 shown; the full log carried all twelve and is reproduced in the table above):

```
===== ARM=base  CELL=D1 =====
drifted emc-fourth-cohort-gene-counts.tsv row2 ['AARS1', '491', '987'] -> ['AARS1', '1000491', '987']
sha after drift : 2168ab583b9f2a209e7c0cdd674f3595a30651adc8301946fdbfac537cf8eeaa
no drift: the derive half reproduces offline
MODULE_EXIT=0
AFTER  8aa3064a97a496a8fa09ef4ae8e472a612318e49ea91d0daac915a3b8fa180cc  emc-fourth-cohort-gene-counts.tsv   <- SILENTLY RESTORED

===== ARM=base  CELL=D3 =====
sha after drift : e7b31a6ec554fa39db1d6d82643e52c7da9e424431a414fcff02956d7173487b
no drift: the derive half reproduces offline
MODULE_EXIT=0
AFTER  e7b31a6ec554fa39db1d6d82643e52c7da9e424431a414fcff02956d7173487b  emc-fourth-cohort-probe-counts.tsv  <- UNDETECTED

===== ARM=r07  CELL=D3 =====
sha after drift : e7b31a6ec554fa39db1d6d82643e52c7da9e424431a414fcff02956d7173487b
DRIFT: ['probe_counts_sha256']
MODULE_EXIT=1
AFTER  e7b31a6ec554fa39db1d6d82643e52c7da9e424431a414fcff02956d7173487b  emc-fourth-cohort-probe-counts.tsv  <- NOT restored

===== ARM=r08  CELL=D3 =====
DRIFT: ['probe_counts_sha256']
MODULE_EXIT=1
AFTER  e7b31a6ec554fa39db1d6d82643e52c7da9e424431a414fcff02956d7173487b  emc-fourth-cohort-probe-counts.tsv  <- NOT restored
```

**RUN — regression, first attempt (recorded failure):** `PYTEST_EXIT=4` on all three arms, `ModuleNotFoundError: No module named 'tracked_tree_guard'`; `--selftest` exit 0 on all three even then. **Retry after supplying the missing module:** `20 passed` / `PYTEST_EXIT=0` on all three.

**RUN — live-tree state, end:**
```
$ date -u                    -> Tue Sep  8 03:33:41 UTC 2026
$ git rev-parse HEAD         -> 215ed8e78f83d1e5acdbb726317dfd0eeed8f6a1   (unchanged from start)
$ git status --porcelain     -> porcelain_lines=0
$ sha256sum research/modalities/{emc_fourth_cohort_quant.py,emc-fourth-cohort-gene-counts.tsv,emc-fourth-cohort-probe-counts.tsv,emc-fourth-cohort-quant.json}
c5180c11…  8aa3064a…  c689e0fd…  1769b3f0…      all four byte-unchanged
$ rm -rf /tmp/claude-0/w24d && ls -d /tmp/claude-0/w24d
ls: cannot access '/tmp/claude-0/w24d': No such file or directory
$ df -h /tmp | tail -1        -> /dev/vda  252G  20G  18G  53% /
```

**PROPOSED (NOT RUN):**
- `scripts/preflight.sh` — **not run**, per dispatch.
- The network phases (`--phase probe|quant|map`), the Ensembl fetch and the vendor manifest — **not attempted**; they remain honest unrecovered sources.
- A fourth drift class beyond D1/D2/D3, e.g. a consistent edit to both the probe TSV and the JSON (the residual hole neither repair closes). Not designed, not run.
- The pytest acceptance case W14c drafted and W14d asked to extend to four assertions. Still not authored as a module by anyone.

## Limitations

- **Tooling only. No scientific finding, no EMC conclusion, no biological or clinical claim of any kind.** A guard that can fail says nothing about whether the fourth-cohort counts are right or about any patient.
- **I did not rule between R07 and R08 and did not land either.** The nine cells are a decision surface, not a decision.
- **The R08 arm is a REBUILD, not R08 as W14d executed it.** W14d's diff is not machine-applicable (abbreviated hunk headers, no file header, the `--check` branch given as a code block). My rebuild reproduces W24c's 93-line count and every acceptance row W14d reported, but a rebuild can only ever be as faithful as the published text.
- **The R07 arm required two mechanical header lines** to reach `git apply`. Nothing inside a hunk was altered, and `patch(1)` accepted the hunks verbatim, but the arm is not literally "the report's bytes fed to `git apply`" — no such arm exists, and I say so rather than claiming a clean verbatim apply.
- Three drift classes, one file at a time. **Not proven against arbitrary corruption**, not under concurrent writers. The residual hole W14d named — a consistent edit to the probe TSV *and* the JSON, which `derive()` reproduces exactly — is untouched by both repairs and by me.
- Run in a **7-file scratch copy**, so only the code paths those files reach were exercised. The `tracked_tree_guard` collection error is direct evidence that the scratch copy is not a full checkout.
- **`--check` was never run against the live tree**, so nothing here says how either patch behaves in a real checkout; that is deliberate, since `--check` calls `derive()` unconditionally and writes both TSVs.
- Unchanged by this run and worth restating: repairing the guard does not **enforce** it. Its only caller, `.github/workflows/emc-expression-datasets.yml:1065-1066`, still swallows the exit code (`|| echo "…non-blocking…"`), and `grep -n "fourth_cohort" scripts/preflight.sh` returns nothing (W14d's finding; I did not re-run it).
- **W24c's record is SECONDARY throughout.** Where I contradict it (the verbatim `git apply`), my measurement is primary; where I agree with it (D3 outcomes, the 93-line count), I re-established the number myself rather than citing it.
- Model identity is **SELF-REPORT, NOT INDEPENDENTLY VERIFIED.**

## Stop condition

Set up front: *the nine patched/unpatched × D1/D2/D3 cells executed on one restored-between-cells table, each carrying the real module exit code, the literal drift list printed, and the artifact sha on disk afterwards; each arm's clean control run first; R07's application outcome stated as it actually happened; and W24c's R08-rebuild off-by-one either reproduced or refuted.*

**MET, in full.** Twelve cells executed (nine drift + three clean controls), every one restored from pristine, every one carrying `MODULE_EXIT` read from the module itself. All three clean controls exit 0 with all three committed shas intact, so no arm's environment was degraded. R07's verbatim application **failed** (`error: patch fragment without header`, exit 128) and is quoted rather than adapted; the headed form applied with zero fuzz and zero rejects. W24c's 93-line off-by-one is **reproduced**. Nothing was applied to the tree, HEAD and all four artifact hashes are unchanged, and the scratch directory is deleted. Returning immediately.

## Tool-call and wall-clock count actually used

**23 tool calls** (all `Bash`; no network, no subagents, no paid API, no GPU, no skills). **Wall clock 03:30:17Z → 03:33:41Z = 3 minutes 24 seconds** of execution, plus report drafting — well inside the ~40-call / ~40-minute target.

## Next concrete action

**Correct two rows in `W24-repair-routing-index.md` so the owner reads a true decision surface, then hand the owner the table above and stop sending workers at this file.** Specifically: row 139(b) should no longer credit R08 with the D3 *capability* (both patches have it, now executed on both — cells B3 and C3), and row 137's "two drift legs D1/D2" for R07 should become "all three drift classes, executed by W24d". Add one new row the index does not carry at all: **R07's published diff is not machine-applicable without a two-line file header, and R08's is not machine-applicable at all** — whichever the owner picks, the applier must expect to reconstruct the patch from the report rather than pipe it into `git apply`, and R08 additionally needs its rebuild diffed against W14d's intent before it lands. That packaging fact, not capability, is now the sharpest practical difference between them. Everything else on the axis — size (995 vs 974 lines), executed test count, memory cost — W24b already priced, and the owner can rule in one reading. **No further read-only worker should be sent at `emc_fourth_cohort_quant.py`: four have now converged on the same answer, and the only thing left is a writer with authority applying exactly one patch.**
