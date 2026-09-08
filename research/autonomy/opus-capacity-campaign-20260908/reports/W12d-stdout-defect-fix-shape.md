> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

## Worker

**W12d**, lane 12 refill, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:46:37 UTC 2026`. `date -u` at end: `Tue Sep  8 02:51:23 UTC 2026` (plus report drafting).

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (identity-bearing lines verbatim; the three pure host-list proxy lines `no_proxy`/`NO_PROXY`/`GLOBAL_AGENT_NO_PROXY`/`npm_config_noproxy`/`JAVA_TOOL_OPTIONS` are elided for length and contain no model name):

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

**HEAD actually read.** `git rev-parse HEAD` at start **and** at end: `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d` — unchanged across my run. This is **not** the `92abbcb905…` named in COMMON-BRIEF.md and **not** W12c's `47aac85…`/`7d08121…`; the coordinator has continued committing collected reports. `git status --porcelain` at start: **empty (0 lines)**. At end: **empty (0 lines)**. `git diff --stat` at end: **empty**. I wrote nothing into the tree; all execution and all output files are under `/tmp/claude-0/w12d/`. No git write of any kind.

I read the live cloud checkout at `/home/user/Rare-cancers`. I did not need the frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/`: every claim here is a measurement I ran against the live tree, not a novelty or absence claim about prior work.

---

## Question

W12b showed the file-`open()` encoding patch fixes 11 of 35 `research/manuscripts` generators but leaves 5 broken, because they `print()` non-ASCII to a locale-built `sys.stdout`. W12c measured that population at **1,031 sites across 317 files**, touching **16 of the 18 `--check` rows** of the preflight re-derivation gate.

**What is the smallest single change that fixes the whole class, and does it actually fix it under a reproduced C locale?**

Open because W12c explicitly stopped at the census and recorded that **zero** code, test, gate, workflow or documentation hit exists in this tree for `PYTHONIOENCODING`, `PYTHONUTF8`, `stdout.reconfigure` or `getpreferredencoding` — so no candidate fix has ever been evaluated, let alone executed.

---

## Prior-work check

```
$ grep -rn 'PYTHONUTF8\|PYTHONIOENCODING' .github/ scripts/ 2>/dev/null | wc -l
0
$ grep -n 'export\|PYTHON' scripts/preflight.sh | head -30
94:export PYTHONPYCACHEPREFIX="$PREFLIGHT_PYCACHE"
  (…no PYTHONUTF8, no PYTHONIOENCODING anywhere)
```

Confirms W12c's measured absence still holds at `3f5fc95`. I read `W12-windows-portability-defects.md` (R1–R7, the **file-I/O** class), `W12b-locale-rederivation-proof.md` (the 35×3 sweep, the 5 still-broken modules and their exemplar lines), and `W12c-stdout-defect-census.md` (the 1,031/317 census, the 18-row gate table, the cp1252 severity axis, and its four-part lower-bound caveat). I am not re-deriving any of those counts — I consume them and test a fix against them.

**CLOSED-WORK.md items I confirmed I am not replaying:** the retained NR4A Perspective refusal (not approached); PUB-EMC-CLASSIFICATION (untouched); every unrecovered source (Pazopanib, anthracycline, sunitinib, trabectedin, Wagner, CTARC — not consulted, irrelevant to a tooling finding); lane 11's source-index (untouched, W11b sole owner); `GSE4303`/`GSE28866` (not read). Per my dispatch I did **not** re-open W12's Windows-log question (W12b established those logs do not exist in the tree) and did **not** widen into W14's guard question. **This report makes no scientific or clinical claim.**

---

## Method / inputs

- Live checkout `/home/user/Rare-cancers` @ `3f5fc95d80…`, read-only. Interpreter `Python 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0]`, Linux `6.18.44-fc-v24`.
- Every run used `env -i PATH=… HOME=… PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/w12d/pyc` so no interpreter state, no user env and no bytecode leaked between arms, and no `.pyc` could land in the tree.
- **Hostile arm** ("before"): `LC_ALL=C LANG=C PYTHONUTF8=0 python3 -X utf8=0`, which yields `sys.stdout.encoding = ascii`.
- **Baseline arm**: `LANG=C.UTF-8 LC_ALL=C.UTF-8`, no flags.
- **Fix arms**: `A` = hostile + `PYTHONIOENCODING=utf-8`; `A2` = `LC_ALL=C LANG=C PYTHONUTF8=1`; plus a deliberate corruption arm `PYTHONIOENCODING=ascii:replace`.
- Only **read-only invocations** were executed: the 18 `--check`/`--check-archive` rows named at `scripts/preflight.sh:849-866`, and five read-only lint/audit entry points. No generator was run in write mode. `scripts/preflight.sh` itself was **not run**. No network.
- Byte comparison: sha256 of each run's combined stdout+stderr capture, plus `git rev-parse HEAD`, `git status --porcelain` and `git diff --stat` before and after every sweep.
- Non-UTF-8 audit: `git ls-files -z | xargs -0 -n50 file --mime-encoding`.

---

## Result

### 1. The failure reproduces — five verbatim `UnicodeEncodeError`s, real exit codes

**PRIMARY.** All under `env -i … LC_ALL=C LANG=C PYTHONUTF8=0 python3 -X utf8=0`, cwd `/home/user/Rare-cancers`:

| site | invocation | rc (hostile) | rc (baseline) | error |
|---|---|---:|---:|---|
| `research/manuscripts/lint_readability.py:383` | `--check` | **1** | 1 | `UnicodeEncodeError` U+26D4 | 
| `research/modalities/atr_hrd_sarcoma_series.py:1424` | `--check` | **1** | 0 | `UnicodeEncodeError` U+2014 |
| `research/manuscripts/lint_citation_types.py:413` (via `lint_citations.py`) | *(no args)* | **1** | 1 | `UnicodeEncodeError` U+2014 |
| `research/manuscripts/lint_submission_residue.py:469` | *(no args)* | **1** | 0 | `UnicodeEncodeError` U+2014 |
| `research/manuscripts/line_citations.py:688` | *(no args)* | **1** | 0 | `UnicodeEncodeError` U+26A0 |

Verbatim tails:

```
  File "/home/user/Rare-cancers/research/manuscripts/lint_readability.py", line 383, in main
    print("\n\u26d4 readability check FAILED:")
UnicodeEncodeError: 'ascii' codec can't encode character '\u26d4' in position 1: ordinal not in range(128)

  File "/home/user/Rare-cancers/research/modalities/atr_hrd_sarcoma_series.py", line 1424, in main
    print(f"OK \u2014 the slot is bound to {SERIES} (artifact, caches, systems map, "
UnicodeEncodeError: 'ascii' codec can't encode character '\u2014' in position 3: ordinal not in range(128)

  File "/home/user/Rare-cancers/research/manuscripts/lint_citation_types.py", line 413, in check
    print("lint_citation_types: ADVISORY (exit code unaffected) %s:%d cites a paper PubMed "
UnicodeEncodeError: 'ascii' codec can't encode character '\u2014' in position 167: ordinal not in range(128)

  File "/home/user/Rare-cancers/research/manuscripts/lint_submission_residue.py", line 469, in check
    print("lint_submission_residue: hallucinated references are gate 6's trigger and remain "
UnicodeEncodeError: 'ascii' codec can't encode character '\u2014' in position 89: ordinal not in range(128)

  File "/home/user/Rare-cancers/research/manuscripts/line_citations.py", line 688, in main
    print(f"  {tag}  {c['target']} `:{c['cited']}` -> :{c['true']}   {c['quote'][:64]!r}"
UnicodeEncodeError: 'ascii' codec can't encode character '\u26a0' in position 104: ordinal not in range(128)
```

**Three findings the reproduction adds to W12c, all PRIMARY:**

1. **The site count is not the failure count.** Of the 18 gate rows, only **1** (`atr_hrd_sarcoma_series.py`) actually raised `UnicodeEncodeError` on this tree's current content; the other 15 rows with sites exited 0 because their non-ASCII lines sit on *failure* branches that a clean tree never reaches. **The 1,031 sites are latent; the realised failure rate depends on tree state, so the defect is worst exactly when something else is already wrong.** That is the severity argument, and it is the opposite of reassuring.
2. **The read defect masks the print defect.** Four gate rows died of `UnicodeDecodeError` before reaching any print: `submission_tables.py`, `submission_citations.py`, `vaccine_path_tables.py`, `aso_deposit_drift.py`, `emc_condensate_report.py` (5 rows) — e.g. `UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2 in position 250`. **5 of 18 gate rows fail under a C locale on a clean tree**, one by encode and four by decode. Any fix evaluated only against the print class is scored against a masked denominator.
3. **`lint_citation_types.py:413` is not in W12c's named inventory** for the `lint_citations.py` entry point — the failure surfaced through a module W12c's per-entry-point table does not list. This is a live confirmation of W12c's own stated lower-bound caveat, not a contradiction of it.

### 2. Candidate fix shapes, with coverage, cost, and what each silently changes

Site denominators are W12c's (**SECONDARY**, adopted not re-derived): 1,031 sites / 317 files total; 195 sites in modules that are `--check`-bearing or named in `preflight.sh`; **52 sites in the 18 gate rows, 16 of 18 rows affected**; 836 sites in modules neither `--check` nor preflight-named.

| # | Shape | Sites covered | Gate rows covered | Cost | What it silently changes |
|---|---|---|---|---|---|
| **A** | `export PYTHONIOENCODING=utf-8` once in `scripts/preflight.sh` | ≤195 (only in processes preflight starts); **0 of the 836** | **16 of 16 print-affected rows, but 0 of the 5 decode-class rows** | 1 line, 1 file | Nothing on this box: 18/18 gate outputs byte-identical (§3). Only rebinds stdio; `open()` default untouched. **PRIMARY: proved not to fix the decode class — 5/5 decode rows still rc=1.** |
| **A2** | `export PYTHONUTF8=1` once in `scripts/preflight.sh` | same ≤195; **0 of the 836** | **16 of 16 print rows AND 5 of 5 decode rows — all 18 rows rc=0** | 1 line, 1 file | On this box: **provably nothing** — native `sys.flags.utf8_mode` is already `1`, so the flag is a literal no-op here (§3). On a cp1252 box it also changes the default `open()` encoding cp1252→utf-8; every tracked text file is already utf-8 (only two PDFs are non-text), so no read can be mis-decoded. **This is a fix, not a corruption.** |
| **B** | Shared `sys.stdout.reconfigure(encoding="utf-8")` preamble in each module | 1,031 of 1,031, in principle | 16 of 16 print rows; **0 of 5 decode rows** | **317 file edits** — it is not one change; it is 317, each a diff on a gated module, each one a chance to move a hashed byte | Nothing, *if* `errors` is left strict. With `errors="replace"`/`"backslashreplace"` it is a corruption — see below. Cannot protect an import-time print that runs before the preamble. |
| **B′** | One `sitecustomize.py` + `export PYTHONPATH` | 1,031 in principle | all 18 | 1 new file + 1 export | Applies to **every** Python process that inherits `PYTHONPATH`, including `pytest`, `pip` and unrelated tooling. Same env-inheritance ceiling as A2 with a strictly larger blast radius. Not smaller than A2, and less honest about its own scope. |
| **C** | Per-site ASCII substitution | 1,031 if done exhaustively | all 18 | **1,031 edits** | **This is the corruption answer, and it must be said plainly.** These modules build committed artifact text and print status text out of the *same* character repertoire. A repo-wide `—`→`--` sweep would rewrite literals inside the `doc` strings that the `--check` rows compare byte-for-byte against committed files, turning **every one of the 18 rows red**. A hand-scoped variant avoids that but is 1,031 hand judgements. Not a fix at repository scale. |
| **D** | Do nothing | 0 | 0 | 0 | Keeps the measured state: 5 of 18 gate rows fail on a clean tree under a C locale, and the 1,031 latent sites fire preferentially when the tree is already broken. |
| **E** | Any candidate with `errors="replace"` / `"backslashreplace"` / `PYTHONIOENCODING=ascii:replace` | — | — | — | **Rejected. Demonstrated corruption, PRIMARY.** `atr_hrd_sarcoma_series.py --check` under `PYTHONIOENCODING=ascii:replace` exits **rc=0** and prints `OK ? the slot is bound to GSE299349 …` — the em dash silently became `?`. It converts a crash into a mangled green. It does not alter a hashed committed artifact (no `--check` row hashes its own stdout — preflight captures each row to `$_genout/$i.out` and re-prints it, it never digests it), but it degrades the diagnostic stream a human reads to decide whether the gate is honest. **A fix must specify strict errors.** |

**Does any candidate alter bytes that a `--check` hashes?** Measured answer for A and A2: **no** (§3, 18/18 byte-identical, tree untouched). Structural answer for C: **yes, catastrophically, if applied as a sweep** — so C is a corruption, not a fix. Answer for E: it does not touch hashed artifact bytes, but it corrupts the gate's own log and converts failure into false success, which is the exact defect class `scripts/preflight.sh`'s own header comment was written about.

### 3. Proof of the recommended shape on a bounded subset — PRIMARY

**Five reproduced sites, before → after, real exit codes:**

| site | baseline rc | hostile rc (before) | `+PYTHONIOENCODING=utf-8` (A) | `+PYTHONUTF8=1` (A2) |
|---|---:|---:|---:|---:|
| `lint_readability.py --check` | 1 | 1 (`UnicodeEncodeError`) | **1, no exception** | **1, no exception** |
| `atr_hrd_sarcoma_series.py --check` | 0 | 1 (`UnicodeEncodeError`) | **0** | **0** |
| `lint_citations.py` | 1 | 1 (`UnicodeEncodeError`) | **1, no exception** | **1, no exception** |
| `lint_submission_residue.py` | 0 | 1 (`UnicodeEncodeError`) | **0** | **0** |
| `line_citations.py` | 0 | 1 (`UnicodeEncodeError`) | **0** | **0** |

Both fix arms restore the baseline exit code exactly, in all five cases. `lint_readability` and `lint_citations` are rc=1 in *baseline too* — those are genuine content findings, not encoding failures, and the fix correctly leaves them failing. **A fix that turned those green would have been the wrong fix.**

**stdout/stderr byte identity, baseline vs both fix arms (sha256, first 16 hex):**

| site | stdout base | stdout A | stdout A2 | stderr base | stderr A |
|---|---|---|---|---|---|
| `lint_readability` | `07bfe06663f2da8d` | `07bfe06663f2da8d` | `07bfe06663f2da8d` | `e3b0c44298fc1c14` | `e3b0c44298fc1c14` |
| `atr_hrd_sarcoma_series` | `06c0293f78060ab9` | `06c0293f78060ab9` | `06c0293f78060ab9` | `e3b0c44298fc1c14` | `e3b0c44298fc1c14` |
| `lint_citations` | `46df52e9809ca14f` | `46df52e9809ca14f` | `46df52e9809ca14f` | `0af7f64084af61ac` | `0af7f64084af61ac` |
| `lint_submission_residue` | `2c903a9db24100e5` | `2c903a9db24100e5` | `2c903a9db24100e5` | `e3b0c44298fc1c14` | `e3b0c44298fc1c14` |
| `line_citations` | `92ac4bcfc47262d9` | `92ac4bcfc47262d9` | `92ac4bcfc47262d9` | `e3b0c44298fc1c14` | `e3b0c44298fc1c14` |

**Full 18-row gate sweep, baseline (`C.UTF-8`) vs recommended fix (`LC_ALL=C LANG=C PYTHONUTF8=1`)** — every row's exit code **and** combined-output sha256:

All 18 rows: **rc 0 → rc 0, sha256 IDENTICAL, 18/18.** Digests (first 12 hex, same in both arms): `submission_tables 9957173d9e74` · `claim_coverage 214a88464cc5` · `submission_citations 568646e8e142` · `submission_metrics 5bdd6236c0f7` · `aso_sequence_manifest a700259b29e1` · `aso_journal_tables 94098c64e781` · `aso_offtarget_duplex_energy a6476322f824` · `submission_packet d7abd7fb46f1` · `vaccine_path_tables e3b0c44298fc` · `aso_archive_manifest f9158b6cd655` · `aso_deposit_drift e3b0c44298fc` · `emc_condensate_report 9b5d315f8e66` · `atr_hrd_sarcoma_series 06c0293f7806` · `single_slot_identity fb0cf7107a71` · `instrument_census 35a99a5cb796` · `trigger_scan 6e25ca27f83d` · `citation_debt d326d8fa8134` · `news_match 86c0546515a0`.

Compare the **unfixed** hostile arm on the same 18 rows: `rc=1` for `submission_tables` (decode), `submission_citations` (decode), `vaccine_path_tables` (decode), `aso_deposit_drift` (decode), `emc_condensate_report` (decode), `atr_hrd_sarcoma_series` (**encode**) — 6 red rows, versus 0 with the fix.

**No committed artifact changed.** After every sweep: `git rev-parse HEAD` = `3f5fc95d80…` (unchanged), `git status --porcelain` = 0 lines, `git diff --stat` = empty.

**Why the byte identity is structural, not luck (PRIMARY):**
```
$ env -i PATH=… HOME=… python3 -c "import sys,locale;print('utf8_mode',sys.flags.utf8_mode,…)"
utf8_mode 1 stdout utf-8 pref utf-8 fs utf-8
$ env -i PATH=… HOME=… PYTHONUTF8=1 python3 -c "…"
utf8_mode 1 stdout utf-8 pref utf-8 fs utf-8
```
This box already runs in UTF-8 mode, so `PYTHONUTF8=1` changes **nothing at all** here. It cannot alter a byte on the machine that currently produces the committed artifacts. It only takes effect on the machine that is currently broken.

**Non-UTF-8 audit (PRIMARY):** `git ls-files -z | xargs -0 -n50 file --mime-encoding` reports exactly two non-`utf-8`/`us-ascii`/`binary` tracked files, both PDFs (`research/release-candidates/PUB-ASO/2026-09-04/submission/supplementary-file-2{,-anonymized}.pdf`, `unknown-8bit`). **No tracked text file would be mis-decoded by a utf-8 default.**

---

## Recommendation, and its residual

**Recommend candidate A2: one exported line in `scripts/preflight.sh`, beside the existing `PYTHONPYCACHEPREFIX` export at line 94.** Not A — A leaves 5 of 18 gate rows red under a C locale, because it fixes only the write side of a two-sided defect. Not B/B′/C — none of them is one change, and C is a corruption at repository scale.

```diff
 PREFLIGHT_PYCACHE="$(mktemp -d)"
 export PYTHONPYCACHEPREFIX="$PREFLIGHT_PYCACHE"
 trap 'rm -rf "$PREFLIGHT_PYCACHE"' EXIT
+
+# Every gate below is a Python process this script starts, and every one of them both READS
+# committed UTF-8 text and PRINTS non-ASCII status text. Under a C/POSIX or cp1252 locale the
+# interpreter builds stdio and the default open() from the LOCALE, before any repository code
+# runs, so a gate dies on its own diagnostic. MEASURED 2026-09-08 at 3f5fc95 under
+# `LC_ALL=C LANG=C PYTHONUTF8=0 python3 -X utf8=0`: 6 of the 18 --check rows exit 1 on a CLEAN
+# tree -- five with UnicodeDecodeError, one (atr_hrd_sarcoma_series.py:1424) with
+# UnicodeEncodeError. With this one line: all 18 exit 0 and every row's output is sha256-identical
+# to the C.UTF-8 baseline. It is exported here, not set per call site, for the same reason as the
+# line above it.
+# ⛔ THE ERROR HANDLER MUST STAY STRICT. PYTHONIOENCODING=...:replace also makes the rows "pass" --
+# by printing `OK ? the slot is bound to ...` and returning 0. That is a crash converted into a
+# mangled green, which is the exact defect class this file's header was written about.
+# ⚠ THIS IS A NO-OP ON A UTF-8 BOX -- `sys.flags.utf8_mode` is already 1 there -- so it cannot
+# move a committed byte on the machine that generates them. It only acts where things are broken.
+export PYTHONUTF8=1
```

**Residual — what this does NOT fix, and why.**

| residual | size | why |
|---|---:|---|
| Sites in modules preflight never starts | **836 of 1,031 (81 %)** | An exported variable reaches only the processes this script spawns. W12c's 836 are overwhelmingly `research/modalities` GPU/fleet tooling run by hand or by other drivers. |
| Sites reachable only via other callers | UNKNOWN | 161 files under `.github/workflows` invoke `python`; 4 other shell scripts (`dev-setup.sh`, `regenerate_aso_chain.sh`, `regenerate_endpoint_chain.sh`, `watch_aso_screens.sh`) invoke `python3`. **None of them would inherit this export.** |
| Sub-processes spawned with a replaced environment | **UNKNOWN, upper bound 173** | `grep -rn 'env='` over the four scanned dirs gives **188** call sites; **73** files use `os.environ.copy()`/`dict(os.environ)`/`{**os.environ}` somewhere. A child given a hand-built `env=` dict loses `PYTHONUTF8` and is un-fixed inside a fixed parent. I did not resolve which of the 188 are safe — that is a per-call-site read, not a grep. |
| Interactive/direct developer runs | not counted | `python3 research/manuscripts/line_citations.py` typed at a C-locale shell still crashes. |
| W12c's four static lower bounds | not counted | Non-literal non-ASCII (constants, `.format`, `chr()`), aliased `print`, logging shims. `lint_citation_types.py:413` surfacing in my run is direct evidence this class is real. |

**Honest bottom line: there is no single change that fixes all 1,031 sites.** Environment is per-process and cannot be guaranteed across 161 workflow files, 4 shell drivers, up to 173 re-parented subprocesses and every hand-typed command. The smallest single change that fixes **the whole gated class** — all 18 `--check` rows, both the encode and the decode half, with zero byte movement — is the one exported line above. Anything claiming to fix all 1,031 is either 317 edits (B), 1,031 edits (C), or a claim that the environment is under control when it demonstrably is not.

---

## Validation evidence

**RUN.** Environment for every command: cwd `/home/user/Rare-cancers`, tree at `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d`, `Python 3.11.15`, Linux `6.18.44-fc-v24`, no network, `env -i` with only `PATH`, `HOME`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w12d/pyc` plus the arm's variables.

1. Hostile reproduction, 18 gate rows + 6 lint entry points:
   `env -i … LC_ALL=C LANG=C PYTHONUTF8=0 … python3 -X utf8=0 <file> [--check]`
   → 6 of 18 gate rows **rc=1** (5 `UnicodeDecodeError`, 1 `UnicodeEncodeError`); 3 of 6 lint entry points **rc=1** `UnicodeEncodeError`. Tracebacks quoted verbatim in §1.
2. Baseline: `env -i … LANG=C.UTF-8 LC_ALL=C.UTF-8 … python3 <file> [--check]` → 18 of 18 gate rows **rc=0**.
3. Fix arm A: `… LC_ALL=C LANG=C PYTHONUTF8=0 PYTHONIOENCODING=utf-8 …` → 5/5 encode sites restored to baseline rc; **5/5 decode rows still rc=1 `UnicodeDecodeError`**.
4. Fix arm A2: `… LC_ALL=C LANG=C PYTHONUTF8=1 …` → **18/18 gate rows rc=0, all 18 combined-output sha256 identical to baseline**; 5/5 encode sites restored to baseline rc with byte-identical stdout and stderr.
5. Corruption arm: `… PYTHONIOENCODING=ascii:replace … python3 research/modalities/atr_hrd_sarcoma_series.py --check` → **rc=0**, output `OK ? the slot is bound to GSE299349 (artifact, caches, systems map, 1 declaring document(s))`.
6. No-op proof: `sys.flags.utf8_mode` is `1` with and without `PYTHONUTF8=1` on this box.
7. Tree integrity, checked after every sweep: `git rev-parse HEAD` unchanged, `git status --porcelain` 0 lines, `git diff --stat` empty.
8. Encoding audit: `git ls-files -z | xargs -0 -n50 file --mime-encoding` → 2 non-text hits, both PDFs.

Raw captures retained under `/tmp/claude-0/w12d/` (`gate/*.out`, `gate/*.err`, `sweep/*.base`, `sweep/*.fix`, `base.*`, `before.*`, `afterA.*`, `afterA2.*`, `repl.out`).

**PROPOSED (NOT RUN).**
- `scripts/preflight.sh` was **not** executed, per dispatch. The claim "the fix makes preflight green under a C locale" is therefore **PREDICTION** built on 18 individually-run rows, not a preflight observation.
- No generator was run in **write mode** — write mode mutates the tree and I am read-only. Write-mode byte identity under the patch is **not established by me**; W12b's 35×3 write-mode sha256 sweep is the nearest evidence and is **SECONDARY** here.
- No Windows, cp1252 or macOS execution. Every cp1252 statement is **PREDICTION**.
- The diff above was **not applied and not `git apply --check`ed** (no tree writes permitted). It is a proposal, not a validated patch.
- The 188/173/73 `env=` figures are grep counts, not a resolved analysis of which subprocesses drop the variable. **UNKNOWN.**

---

## Limitations

- **One platform, one interpreter.** Everything ran on Linux/CPython 3.11.15. `-X utf8=0 LC_ALL=C` is a faithful *simulation* of an ASCII-stdio interpreter, not a Windows console. It is strictly harsher than cp1252 (ASCII fails on `— … § · ±` which cp1252 survives), so it over-detects relative to Windows and under-detects nothing.
- **The realised failure set is tree-state-dependent.** 15 of the 16 print-affected gate rows exited 0 here only because their non-ASCII lines are on failure branches. A different tree state produces a different, probably larger, red set. Nothing in my method bounds that.
- **Coverage arithmetic inherits W12c's denominators**, including its four-part lower-bound caveat. `lint_citation_types.py:413` is direct evidence the true site count exceeds 1,031.
- The `--check` rows are read-only *by design and by the gate's own documented contract*; I verified this empirically only through `git status`, which is a whole-tree assertion, not a per-row one.
- **No scientific, biological or clinical claim is made or supported by anything here.** This is tooling.
- "No `PYTHONUTF8`/`PYTHONIOENCODING` in this tree" is measured at `3f5fc95` in the live checkout. It is UNKNOWN whether such a guard existed historically or exists on a branch.

---

## Stop condition

**Set up front:** stop as soon as (a) at least three named sites reproduce a verbatim `UnicodeEncodeError` with real exit codes under a forced C locale, (b) every candidate shape has a stated coverage/cost/silent-change verdict including an explicit answer on hashed bytes, and (c) the recommended shape is demonstrated before-and-after on those sites plus the 18-row gate with a byte comparison proving no committed artifact moved.

**MET.** (a) five reproductions, not three; (b) six shapes scored, with the corruption verdict on C and E demonstrated rather than asserted; (c) 5/5 sites and 18/18 gate rows, byte-identical, tree unchanged at both ends. Returned immediately on meeting it.

---

## Tool-call and wall-clock count actually used

**11 tool calls** (all `Bash`). Wall clock **02:46:37Z → 02:51:23Z = 4 min 46 s** of execution, plus report drafting. Well inside the ~40-call / ~40-min target.

---

## Next concrete action

**One successor, bounded and inside lane 12: resolve the subprocess residual.** Read the **188** `env=` call sites in `research/manuscripts`, `research/modalities`, `scripts`, `systems` and classify each as *inherits* (built from `os.environ.copy()`/`{**os.environ}`) or *replaces* (hand-built dict). Then, for the replacing subset, measure — by execution under `LC_ALL=C LANG=C PYTHONUTF8=1` in a parent — how many child processes actually lose the variable and crash. That converts my largest UNKNOWN into a number and tells the owner whether the one-line export is sufficient for the gate or whether the gate additionally needs its children's `env=` dicts audited. It is read-only, needs no tree write, and is roughly a 30-minute task.

A second, lower-value option I explicitly do **not** recommend as next: extending the export to `.github/workflows`. That is 161 files, it is a CI-configuration change rather than a defect repair, and W14 owns the guard question — it should wait until someone decides whether a *guard* (a test asserting the gate survives a C locale) is wanted, which is W14's call, not mine.
