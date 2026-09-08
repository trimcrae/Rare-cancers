> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sweep complete. Sanity check: the real tree shows only the coordinator's own campaign-directory files as modified — nothing of mine (`git status --porcelain` from `/home/user/Rare-cancers`); all my execution was under `/tmp/claude-0/w12b/`. Both the 35×3 `--check` sweep and the 35×3 write-mode sha256 sweep ran to completion (105 runs each), and I confirmed the patched module set has zero remaining bare text opens.

---

## Worker

**W12b**, Lane 12 (refill) — converting W12's single-artifact encoding demonstration into a per-artifact re-derivation proof across the endpoint analysis.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:06:37 UTC 2026`. `date -u` at end: `Tue Sep  8 02:25:57 UTC 2026`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (identity-bearing lines; proxy/`no_proxy` lines elided for length, they contain no model name):

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

**Write isolation honoured.** `git rev-parse HEAD` → `92abbcb905cacf07f14b238db50d1b98f6590374`. `git status --porcelain` in `/home/user/Rare-cancers`, run at the start and again at the end, showed only the campaign directory and the coordinator's own report files — **no file of mine, tracked or untracked, anywhere in the repository**. No git write operation of any kind. All execution under `/tmp/claude-0/w12b/`.

---

## Question

**Does every committed EMC endpoint artifact re-derive byte-identically under a hostile (non-UTF-8) locale once the text encoding and newline are pinned — and which artifacts do not, even with the fix?**

Open because W12 proved the mechanism on **one** artifact (`endpoint-regime-map.json`, sha `f542b99d…`) with a hand-written call-shape reproduction, not by running the repository's own generators. A single-artifact demonstration cannot tell you whether the patch shape is *sufficient*, and it cannot find artifacts that carry a **second, different** defect underneath the encoding one. That is exactly what this run set out to test.

---

## Prior-work check

I did not re-derive W12's established findings; I took them as given per my dispatch. My own novelty checks:

```
$ rg -n "getpreferredencoding|utf8_mode|PYTHONUTF8|PYTHONIOENCODING" --glob '!.git' .
   (no output, exit 1)
```
Zero hits repository-wide — confirming W12's R5 and, additionally, that **`PYTHONIOENCODING` and `sys.stdout.reconfigure` appear nowhere**, which is the gap my STILL-BROKEN rows land in.

```
$ git ls-files | rg -i "windows|portab|platform"
research/autonomy/throughput-2026-09-04/archive-portability-tests.log
research/autonomy/throughput-2026-09-04/portability-tests.log
```
Same two post-repair PASS logs W12 found; still no retained failure log. I did not attempt to reconstruct it.

`CLOSED-WORK.md` items I confirmed I am **not** replaying: the lane-11 source-index bundle (sole owner lane 11 — I touched none of it, and where `line_citations.py` appears below it is only as a generator exit code, not a source-index change); the retained NR4A Perspective refusal; the closed scientific gates (Davis, Hofvander, Brenca, promoter transfer, ICD-O paper); every unrecovered source (Pazopanib, anthracycline, sunitinib, trabectedin, Wagner, CTARC); and `GSE4303`/`GSE28866`. This finding is a reproducibility defect in generator code and depends on none of them. **No scientific conclusion changes.**

---

## Method / inputs

**Enumeration (step 1) — by reading the code, not guessing.**

```
$ cd /home/user/Rare-cancers/research/manuscripts
$ for f in *.py; do if grep -q '"--check"' $f; then echo $f; fi; done | wc -l
35
```
66 Python modules live in `research/manuscripts`; **35** carry a literal `"--check"` re-derivation entry point. I widened W12's three (`endpoint_regime_map.py`, `placebo_arm_calibration.py`, `submission_tables.py`) to all 35 and cross-checked each against its `OUT`/`OUT_REL` constant (`grep -n '^OUT' *.py`) to learn which committed artifact it owns.

**Scratch copy (step 2).**
```
$ mkdir -p /tmp/claude-0/w12b/repo
$ tar --exclude=./.git -cf - . | (cd /tmp/claude-0/w12b/repo && tar -xf -)   # exit 0
$ cp -a /tmp/claude-0/w12b/repo /tmp/claude-0/w12b/repo_patched              # exit 0
```
`ls -a` confirms no `.git` in either copy. **This is a real limitation and I flag it under Limitations** — generators that shell out to git degrade in the scratch.

**Environment.** `Python 3.11.15` (`/usr/bin/python3`), Linux `6.18.44-fc-v24`, stdlib only (no third-party package is imported by the tested generators' `--check` paths). Baseline container: `LANG`/`LC_ALL` unset, `sys.flags.utf8_mode = 1`, `locale.getpreferredencoding(False) = 'utf-8'`.

**Three configurations, run for every module, twice (once `--check`, once write-mode):**

| id | code | interpreter + environment | cwd |
|---|---|---|---|
| **a** | current | `python3` (utf8_mode=1, LANG/LC_ALL unset) | `/tmp/claude-0/w12b/repo` |
| **b** | current | `LC_ALL=C LANG=C PYTHONUTF8=0 python3 -X utf8=0` | `/tmp/claude-0/w12b/repo` |
| **c** | **patched** | `LC_ALL=C LANG=C PYTHONUTF8=0 python3 -X utf8=0` | `/tmp/claude-0/w12b/repo_patched` |
| **d** | patched | as **c**, plus `PYTHONIOENCODING=utf-8` | `/tmp/claude-0/w12b/repo_patched` |

Config **d** was added *after* the STILL-BROKEN rows appeared, to test a hypothesis about their cause. Under **b** the interpreter reports `locale.getpreferredencoding(False) = 'ANSI_X3.4-1968'`, i.e. ASCII — strictly more hostile than Windows cp1252, which is why it converts W12's *silent* mojibake into a loud `UnicodeDecodeError`.

**The patch (step 3c)** was applied to the scratch copy by an AST-guided rewriter (code inline below), not by hand: `encoding="utf-8"` on every text-mode `open()`/`read_text()`/`write_text()`, and `newline="\n"` on every text-mode write. It modified **94 of 196** `.py` files under `repo_patched/research/manuscripts`, left binary-mode opens untouched, and every patched file still parses (`ast.parse` over the tree: **0 syntax errors**). The diff it produced for `endpoint_regime_map.py` is **character-for-character W12's proposed patch**, which is my check that the rewriter implements the intended shape:

```diff
-    with open(CORPUS) as fh:
+    with open(CORPUS, encoding="utf-8") as fh:
-        with open(OUT) as fh:
+        with open(OUT, encoding="utf-8") as fh:
-    with open(OUT, "w") as fh:
+    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
```

**sha256 evidence.** `--check` yields only an exit code, so I ran each generator a second time in **write mode** and hashed what it actually produced against the committed bytes in the read-only real repository. Changed files were detected by an mtime+size snapshot of `research/manuscripts` before and after each run, then **restored from `/home/user/Rare-cancers` after every run** so the next generator saw committed inputs.

---

## Result

### The headline: STILL BROKEN — the encoding patch is NOT sufficient

Five generators fail under a hostile locale **even with every text open pinned**. The cause is a **second, different defect** that no amount of file-I/O patching can reach: **`print()` of non-ASCII text to a stdout whose encoding is inherited from the process locale.** `sys.stdout` is a `TextIOWrapper` the interpreter builds before any of this code runs; `encoding=` on an `open()` call cannot touch it.

| Module | chk **a** | chk **b** | chk **c** | write **a** | write **b** | write **c** | Verdict | Character that kills it |
|---|---|---|---|---|---|---|---|---|
| `build_submission_parts.py` | 0 | 1 | **1** | 0 | 1 | **1** | **STILL BROKEN** | `U+2014` EM DASH in the per-part progress line, `build_submission_parts.py:395` |
| `emc_systems_map_check.py` | 0 | 1 | **1** | 0 | 1 | **1** | **STILL BROKEN** | `U+00B7` MIDDLE DOT in the summary line, `emc_systems_map_check.py:1364` |
| `submission_metrics.py` | 0 | 0 | 0 | 0 | 1 | **1** | **STILL BROKEN (write path only)** | `U+2014` at `submission_metrics.py:630` |
| `lint_readability.py` | 1 | 1 | 1 | 0 | 1 | **1** | **STILL BROKEN (write path only)** | `U+26A0` WARNING SIGN at `lint_readability.py:359` |
| `line_citations.py` | 2 | 2 | 2 | 1 | 1 | **1** | **STILL BROKEN, and MASKED** | `U+26A0` at `line_citations.py:688` |

Verbatim, config **c** (patched, hostile), `build_submission_parts.py --check`, exit **1**:
```
  File "/tmp/claude-0/w12b/repo_patched/research/manuscripts/build_submission_parts.py", line 395, in build
    print(f"{name} [{part_name}]: {os.path.relpath(out, REPO)} \u2014 {counts['blocks']} block(s), "
UnicodeEncodeError: 'ascii' codec can't encode character '\u2014' in position 111: ordinal not in range(128)
```

Verbatim, config **c**, `emc_systems_map_check.py --check`, exit **1** — note it got all the way to the *last line of output* having done all its work:
```
WARN  [C1] none of ('origin/main', ...) is present in this checkout ...
  File "/tmp/claude-0/w12b/repo_patched/research/manuscripts/emc_systems_map_check.py", line 1364, in main
    print(f"\nemc_systems_map_check: {n_items} registry items \xb7 "
UnicodeEncodeError: 'ascii' codec can't encode character '\xb7' in position 43: ordinal not in range(128)
```

**Two of these five are worse than a crash, and are the reason this row set matters:**

1. **`submission_metrics.py` writes a byte-perfect artifact and then exits 1.** In config **c** the produced `research/manuscripts/submission-metrics.json` has sha256 `a147db965c3ce368df9cdb50629d64d8eab1f37df76bee2ffb5395107dd695ef`, **identical to committed**, 13,057 bytes — and the process still returns exit 1, because it crashes on the summary `print()` *after* the file is closed. Any caller that gates on the exit code (`scripts/preflight.sh` does) declares a successful regeneration a failure. The inverse hazard is the same shape: a generator that crashes after a *partial* write would leave a truncated artifact behind a non-zero exit.

2. **`line_citations.py` returns exit 1 in all three configs — for two entirely different reasons.** At baseline (**a**) exit 1 is its ordinary content report. Under **b**/**c** exit 1 is a `UnicodeEncodeError` crash at line 688, having printed only part of its findings. **The exit code is identical, so no gate anywhere can tell the two apart.** A CI step that accepts "line_citations exits 1, that's its normal state" would be silently accepting a crash. This is the most dangerous single row in the table.

**Cause confirmed, not assumed.** I re-ran all five under config **d** (identical to **c**, plus `PYTHONIOENCODING=utf-8`):

```
$ cd /tmp/claude-0/w12b/repo_patched
$ LC_ALL=C LANG=C PYTHONUTF8=0 PYTHONIOENCODING=utf-8 python3 -X utf8=0 \
      research/manuscripts/build_submission_parts.py --check
exit=0
$ ... emc_systems_map_check.py --check        exit=0
$ ... submission_metrics.py                   exit=0
$ ... lint_readability.py                     exit=0
$ ... line_citations.py                       exit=1   # back to its ORDINARY content report,
                                                       # printing "NO QUOTE"/"QUOTED" findings, no traceback
```
Four of five return to exit 0; the fifth returns to its baseline behaviour. **The diagnosis holds: the residual defect is the stdout encoding, not the file I/O.**

**Windows relevance (PREDICTION, not reproduced — I have no Windows host).** Whether these five fail on Windows depends on the active console code page, which is not a constant:

| character | site | cp1252 | cp437 | cp850 | ascii (`LC_ALL=C`, reproduced) |
|---|---|---|---|---|---|
| `U+2014` EM DASH | `build_submission_parts:395`, `submission_metrics:630` | OK | **FAIL** | **FAIL** | **FAIL** |
| `U+00B7` MIDDLE DOT | `emc_systems_map_check:1364` | OK | OK | OK | **FAIL** |
| `U+26A0` WARNING | `lint_readability:359`, `line_citations:688` | **FAIL** | **FAIL** | **FAIL** | **FAIL** |
| `U+26D4` NO ENTRY | committed artifact keys | **FAIL** | **FAIL** | **FAIL** | **FAIL** |

So on a legacy `cp437`/`cp850` console four of the five fail; on a modern `cp1252` console two still fail (`U+26A0`). The mechanism is reproduced; only the per-codepage outcome is a prediction.

### FIXED — hostile locale, patched, sha256 matches committed

Every row below fails under **b** and passes under **c** with the produced bytes identical to the committed bytes. These are `PRIMARY` measurements: real generator runs, real sha256.

| Module | Committed artifact | chk a/b/c | sha256 produced under **c** | vs committed | Verdict |
|---|---|---|---|---|---|
| `endpoint_regime_map.py` | `endpoint/endpoint-regime-map.json` (54,064 B) | 0/1/0 | `f542b99d1f5984e6b584f6f217d6e4b000d798e84baaa954c3bf498cabe10a55` | **MATCH** | **FIXED** |
| `placebo_arm_calibration.py` | `endpoint/placebo-arm-calibration.json` (53,551 B) | 0/1/0 | `3823ca7874906113748321ce9b8c9330d3301396f7e5be15713a41538f19b2c7` | **MATCH** | **FIXED** |
| `endpoint_corpus.py` | `endpoint/endpoint-corpus.json` (941,272 B) | 0/1/0 | `1675e8d56707d331805b2ad6b8c664dd683fad6d97b5884197ec9ae66e75c634` | **MATCH** | **FIXED** |
| `endpoint_prior_art_audit.py` | `endpoint/endpoint-prior-art-audit.json` (23,214 B) | 0/1/0 | `4bb09c6309cc6470e5c070e4f072e933373a2b0e6114e68a3330a68aef6103e5` | **MATCH** | **FIXED** |
| `endpoint_regime_figure.py` | `endpoint/endpoint-regime-map.svg` (12,323 B) | 0/1/0 | `be3794a4c75beb5119f86c14f477de82747ae992f3f952a7df3a4c9f28d41566` | **MATCH** | **FIXED** |
| `endpoint_result_figures.py` | `endpoint/endpoint-gap-distribution.svg` (15,826 B) | 0/1/0 | `b54d140c717b96683fa363d098ddcea44abd7a56d36e3a8a663345ba0dbb673b` | **MATCH** | **FIXED** |
| `endpoint_result_figures.py` | `endpoint/endpoint-zero-response.svg` (4,078 B) | — | `832067f5dd1a1e638b53e0a978d45d326219d27c934c9daa5f1aa3479ff7d5da` | **MATCH** | **FIXED** |
| `orr_dcr_reread.py` | `endpoint/orr-dcr-reread.json` (428,155 B) | 0/1/0 | `95ac62e88a18288acee3330ac93541c6f458d23831e3a1c2ee1055930345f6d9` | **MATCH** | **FIXED** |
| `submission_tables.py` | `aso/fusion-junction-aso-submission-tables.md` (69,246 B) | 0/1/0 | `cd7f516ca52f99f9b6504e50da3333fa538f18d4c32e4e1636fa98dee7bc941e` | **MATCH** | **FIXED** |
| `vaccine_path_tables.py` | `neoantigen/emc-vaccine-development-path.md` (134,434 B) | 0/1/0 | `59a72c41cd4f5ed1c1657a2208213df6a08d0d9a4e957739020a013f4d0e396e` | **MATCH** | **FIXED** |
| `submission_citations.py` | (check-only path; rewrote no artifact in the write run) | 0/1/0 | — | exit-code only | **FIXED (exit code only)** |

**11 rows fixed, 10 with byte evidence.** `submission_tables.py` is the artifact W12 measured at 479 bytes larger under Win32 text mode; with `newline="\n"` pinned it comes back at exactly `cd7f516c…`, 69,246 bytes. This is the direct confirmation W12's R4 predicted.

### NOT AFFECTED — locale-insensitive (a = b = c = 0)

`aso_coverage_ladder.py`, `aso_journal_tables.py`, `aso_reagent_coverage.py`, `aso_sequence_manifest.py` (CSV + FASTA), `claim_ablation.py`, `claim_coverage.py`, `emc_endpoint_alternatives.py`, `emc_endpoint_discordance.py`, `emc_fusion_partner_pooling.py`, `emc_systemic_therapy_pooling.py`, `submission_packet.py`, `tcf12_breakpoint_assignment.py`, `venue_fee_screen.py` (check path). **13 modules.** Their `--check` succeeds identically in all three configs — their inputs and outputs happen to be ASCII-clean on the paths exercised. This is a genuine negative result and it narrows the blast radius: the defect is not uniform across `research/manuscripts`.

### A third, separate finding: 8 artifacts never re-derive byte-identically, in ANY locale

While tabulating I found artifacts that DIFFER from committed under config **a** — the baseline, normal locale, unpatched code. This has nothing to do with encoding. Same byte size, different sha256:

| Artifact | baseline produced | committed | bytes |
|---|---|---|---|
| `endpoint/emc-endpoint-alternatives.json` | `aee0f09b292abd35…` | `ca586e82bc315282…` | 96,266 = 96,266 |
| `endpoint/emc-endpoint-discordance.json` | `bb392587f7d2c6d1…` | `6538ab267530ce42…` | 18,248 = 18,248 |
| `endpoint/emc-systemic-therapy-pooling.json` | `76c0aea4a8f90f85…` | `5c0d5f65a44ddd28…` | 79,198 = 79,198 |
| `fusion-partner/emc-fusion-partner-pooling.json` | `00b45dd7b84a57e2…` | `ad449441142e4fb3…` | 113,032 = 113,032 |
| `aso/…-journal-article-figure-legends.docx` | `be85ba21b4cfb658…` | `2491aa501271ca87…` | 6,508 = 6,508 |
| `aso/…-journal-article-title-page.docx` | `1729b811f01cd083…` | `b9581ce1c848395b…` | 6,812 = 6,812 |

Cause, measured not guessed — I regenerated one and diffed the parsed JSON:
```
$ diff <(canonical-json produced) <(canonical-json committed)
310c310
<  "_generated_utc": "2026-09-08T02:25:19Z",
---
>  "_generated_utc": "2026-08-09T01:33:55Z",
```
A single embedded wall-clock stamp of fixed width. The `--check` paths strip it (`_strip_volatile`), which is why they pass. **The honest consequence: for these artifacts sha256 is not a reproducibility criterion and must not be used as one** — the `--check` comparison is the criterion. The two `.docx` files are the same story via the zip member timestamps. I am reporting this as an observation about what sha256 can and cannot certify here, **not** as a defect to repair.

### Step 5 — is the fix complete? (AST census, re-run on the patched copy)

| Census scope | text `open()` w/o `encoding=` | `read_text` w/o | `write_text` w/o | text write w/o `newline=` |
|---|---:|---:|---:|---:|
| The 35 `--check` modules, **before** patch | 50 | 0 | 0 | 43 |
| The 35 `--check` modules, **after** patch | **0** | **0** | **0** | **0** |
| Whole `research/manuscripts` tree (196 files), before | 114 | 6 | 2 | 146 |
| Whole `research/manuscripts` tree, **after** | **1** | 0 | 0 | 0 |

**Zero remaining bare text-mode opens in every patched generator.** The single residual in the whole tree is `tests/test_no_test_may_write_to_the_tracked_tree.py:77`:
```python
@pytest.mark.parametrize("mode", ["w", "wb", "a", "r+", "x"])
def test_every_writing_mode_is_refused(pretend_tracked, mode):
    with pytest.raises(RuntimeError, match="opened the git-tracked file"):
        open(pretend_tracked, mode).close()
```
The mode is a parametrized variable that includes `"wb"`, so it is not statically classifiable and **must not be patched** — the test is asserting that the tracked-tree write guard fires, and it never reads or writes content. Correctly excluded.

So the file-I/O fix is **complete for what it covers**, and **incomplete for the defect class**: it is silent about `sys.stdout`, which is where all five STILL-BROKEN rows live.

---

## Validation evidence

All commands **RUN**. Environment for every run: Python 3.11.15, Linux 6.18.44-fc-v24, stdlib only. Real repository read-only at `92abbcb905cacf07f14b238db50d1b98f6590374`; all execution under `/tmp/claude-0/w12b/`.

**V1 — scratch setup, exit 0.** `tar --exclude=./.git` copy + `cp -a` clone; `ls -a` confirms no `.git`; `git status --porcelain` in the real repo unchanged before and after.

**V2 — the patch, exit 0.**
```
$ python3 /tmp/claude-0/w12b/patch_encoding.py /tmp/claude-0/w12b/repo_patched/research/manuscripts
{"files_scanned": 196, "files_modified": 94,
 "unresolved": {"tests/test_no_test_may_write_to_the_tracked_tree.py": [[77, "dynamic-mode"]]}}
$ python3 -c "<ast.parse over the patched tree>"   →  parse failures: 0 []
```

**V3 — the 35 × 3 `--check` sweep, driver exit 0, 105 runs, no timeouts.** Full exit-code matrix printed in Result. Result file `/tmp/claude-0/w12b/check-results.json`.

**V4 — the 35 × 3 write-mode sha256 sweep, driver exit 0, 105 runs.** 104 completed normally; `venue_fee_screen.py` hit the 300 s per-run cap in all three configs (network fetch through the egress proxy) and is recorded `TIMEOUT`. Result file `/tmp/claude-0/w12b/write-results.json`. Every changed file restored from the real repository after each run.

**V5 — config d, the cause test for the STILL-BROKEN rows, exits quoted verbatim in Result.**

**V6 — AST census before/after, exit 0.** Table in Result.

**V7 — `_generated_utc` diff, exit 0.** Quoted verbatim in Result.

**V8 — codepage encodability table, exit 0.** `str.encode()` against `cp1252`/`cp437`/`cp850`/`ascii`.

**V9 — real-tree cleanliness, exit 0.** `git status --porcelain` at start and end shows only the coordinator's campaign directory.

**PROPOSED (NOT RUN):**
- The stdout patch below was **not** applied to any file and was **not** exercised. Only the `PYTHONIOENCODING=utf-8` *environment* form of the fix was executed (config **d**, exits quoted). The source-level `sys.stdout.reconfigure` form is **PROPOSED (NOT RUN)**.
- No `pytest` run, no `scripts/preflight.sh` run — my dispatch did not authorise them and the campaign brief forbids preflight unless dispatched.
- No Windows host. Every Windows codepage outcome is **PREDICTION**; every mechanism is reproduced on Linux.
- I regenerated **no** committed artifact in the real tree.
- `venue_fee_screen.py` write-mode behaviour under all three configs: **not measured** (timeout).

### Code actually run — the AST-guided patcher

```python
"""AST-guided rewriter: pin encoding= on every text-mode open()/read_text()/write_text(),
and newline="\n" on every text-mode write. Byte-preserving elsewhere."""
import ast, os, sys, json

WRITE_MODES = set("wax")

def rewrite(path):
    src = open(path, encoding="utf-8").read()
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return None, [("SYNTAXERROR", str(e))]
    edits, unresolved = [], []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.id if isinstance(fn, ast.Name) else (fn.attr if isinstance(fn, ast.Attribute) else None)
        if name not in ("open", "read_text", "write_text"):
            continue
        kws = {k.arg for k in node.keywords}
        if None in kws:                       # **kwargs -- cannot reason, leave alone
            unresolved.append((node.lineno, "starstar")); continue
        if name == "open":
            mode = None
            if len(node.args) > 1:
                a = node.args[1]
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    mode = a.value
                else:
                    unresolved.append((node.lineno, "dynamic-mode")); continue
            for k in node.keywords:
                if k.arg == "mode":
                    if isinstance(k.value, ast.Constant) and isinstance(k.value.value, str):
                        mode = k.value.value
                    else:
                        unresolved.append((node.lineno, "dynamic-mode")); mode = "?"
            if mode == "?":
                continue
            mode = mode or "r"
            if "b" in mode:                   # binary I/O has no encoding, correctly skipped
                continue
        elif name == "read_text":
            mode = "r"
        else:
            mode = "w"
        ins = ""
        if "encoding" not in kws:
            ins += ', encoding="utf-8"'
        if name != "read_text" and set(mode) & WRITE_MODES and "newline" not in kws:
            ins += ', newline="\\n"'
        if ins:
            if not node.args and not node.keywords:
                ins = ins[2:]                 # no leading ", " when the call is empty
            edits.append((node.end_lineno, node.end_col_offset, ins))
    if not edits:
        return src, unresolved
    lines = src.splitlines(keepends=True)
    for lineno, col, ins in sorted(edits, reverse=True):   # bottom-right upward
        L = lines[lineno - 1]
        assert L[col - 1] == ")", (path, lineno, col)
        lines[lineno - 1] = L[:col - 1] + ins + L[col - 1:]
    return "".join(lines), unresolved

if __name__ == "__main__":
    root = sys.argv[1]
    n_files = n_edit = 0
    unres = {}
    for dp, dn, fnames in os.walk(root):
        dn[:] = [d for d in dn if d not in (".git", "__pycache__")]
        for f in fnames:
            if not f.endswith(".py"):
                continue
            p = os.path.join(dp, f)
            before = open(p, encoding="utf-8").read()
            out, u = rewrite(p)
            n_files += 1
            if u:
                unres[os.path.relpath(p, root)] = u
            if out is not None and out != before:
                open(p, "w", encoding="utf-8", newline="").write(out)
                n_edit += 1
    print(json.dumps({"files_scanned": n_files, "files_modified": n_edit,
                      "unresolved": unres}, indent=1))
```

The three-way driver (`run_checks.py`), the write-mode sha256 driver (`run_writes.py`) and the census (`census.py`) are in `/tmp/claude-0/w12b/`; their logic is described exactly in Method, and their outputs are the tables above.

### The missing half of the repair — PROPOSED (NOT RUN), for the owner

The environment form is **measured** (config **d**, exits quoted above). The source form below was **not executed**:

```python
# At the top of each entry point that prints non-ASCII -- build_submission_parts.py,
# emc_systems_map_check.py, submission_metrics.py, lint_readability.py, line_citations.py.
# open(..., encoding=...) cannot reach sys.stdout: the interpreter built that wrapper from
# the process locale before this module was imported.
def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")   # Python >= 3.7
        except (AttributeError, ValueError):
            pass                                   # already correct, or not a TextIOWrapper
```

And the guard W12 proposed should be widened, because as written it would have passed all five STILL-BROKEN modules. The smallest honest addition — **PROPOSED (NOT RUN)**:

```python
def test_the_generator_survives_a_hostile_locale(module):
    """A patched text-open is not enough: print() of a non-ASCII character still crashes on a
    stdout whose encoding came from the locale. Reproduced on Linux; no Windows host needed."""
    env = dict(os.environ, LC_ALL="C", LANG="C", PYTHONUTF8="0")
    env.pop("PYTHONIOENCODING", None)          # the point is that it must not be required
    p = subprocess.run([sys.executable, "-X", "utf8=0",
                        os.path.join(MANUSCRIPTS, module), "--check"],
                       cwd=REPO, env=env, capture_output=True)
    assert b"UnicodeEncodeError" not in p.stderr and b"UnicodeDecodeError" not in p.stderr, (
        f"{module} crashed on the process encoding, not on its science:\n"
        f"{p.stderr.decode('utf-8', 'replace')[-800:]}")
```
Note the assertion is on the *traceback*, not on the exit code — deliberately, because `line_citations.py` proves an exit code cannot distinguish a crash from a finding.

---

## Limitations

- **No `.git` in the scratch copy.** Generators that shell out to git degrade there. This is why `aso_archive_manifest.py` and `aso_deposit_drift.py` report a baseline exit 1 ("STALE: manifest would change") and produce artifacts smaller than committed (376,767 B vs 382,546 B; 87,436 B vs 89,168 B), and why `line_citations.py` prints `fatal: not a git repository` at baseline, and why `emc_systems_map_check.py` emits its `[C1]` working-tree WARN. **Whether those manifests are genuinely stale in the real repository is UNKNOWN — I did not test it, and this evidence cannot decide it.** Their verdicts are `N/A (baseline blocked)`, not `STILL BROKEN`.
- **Blockers recorded, not stubbed** (per hard limit): `journal_abbreviations.py` and `nat_scope_census.py` fail at write with `<urlopen error Tunnel connection failed: 403 Forbidden>` against `eutils.ncbi.nlm.nih.gov` — an ordinary egress denial, already a known route. `aso_priorart_evidence.py` (exit 2) and `journal_reference_authors.py` need `git fetch origin literature-cache`, absent here. `build_aixiv_metadata.py` (exit 2) requires `--paper {fusion-output,vaccine-path}`, which my uniform `--check` harness does not supply — its verdict is `N/A (harness)`, not a defect. `venue_fee_screen.py` write mode exceeded 300 s in all three configs. **I stubbed nothing and weakened no assertion or `--check` comparison anywhere.**
- **`LC_ALL=C` is stricter than Windows.** ASCII raises where cp1252 silently mojibakes. My config **b** therefore *converts* W12's silent-corruption failure mode into a loud one; it does not reproduce the silent one. W12 already demonstrated the silent path separately. Windows-specific exception strings and per-codepage outcomes remain PREDICTION.
- **`--check` paths, not full pipelines.** I exercised each generator's own re-derivation entry point. Cross-generator ordering (one generator's output feeding another) was neutralised by restoring committed inputs between runs; a real end-to-end regeneration on Windows could surface interactions this design cannot see.
- **The AST census is a lower bound.** It cannot see `open` reached through an alias or `functools.partial`.
- **Scope.** This is a reproducibility and tooling finding. **No EMC scientific value, endpoint, or conclusion is changed, questioned, or supported by any of it.** No computational result here bears on efficacy, safety, selectivity or clinical readiness.

---

## Stop condition

**Set:** a per-artifact three-way re-derivation table with real sha256 evidence and an explicit FIXED / STILL BROKEN / N/A verdict for each.

**MET.** 35 generators enumerated from the code; 210 real runs (105 `--check`, 105 write-mode) across three configurations plus 5 confirmatory config-**d** runs; 22 committed artifacts hashed against their committed bytes; **11 FIXED** (10 with byte-identical sha256 evidence), **5 STILL BROKEN** with the second defect isolated and its cause confirmed by an executed test, **13 NOT AFFECTED**, **7 N/A or blocked** with each blocker named. The completeness check was run rather than assumed: **0** remaining bare text-mode opens in the patched generator set.

One partial: `venue_fee_screen.py` write-mode is `TIMEOUT` in all three configs and is honestly unmeasured. Its `--check` path was measured and is NOT AFFECTED.

---

## Tool-call and wall-clock count actually used

**36 tool calls; ~19 minutes wall clock** (`date -u` 02:06:37 → 02:25:57). Both within the campaign's ~40/~40 target. Process note: I initially spawned several redundant background waiters polling the same result file; the coordinator flagged this mid-run, I stopped them all (`TaskStop` on the monitor plus `pkill`, all exited 144), verified the real sweep (`run_writes.py`, pid 17935) was untouched and its 104 completed runs preserved, and replaced the polling with bounded waits. The first bounded wait timed out at 600 s with 104/105 runs done, which I reported; a second bounded harvest wait (340 s, exit 0) collected the final result file. No output was lost.

---

## Next concrete action

**One successor task for this lane:** *Apply the two-part repair — the mechanical `encoding=`/`newline=` rewrite plus `sys.stdout/stderr.reconfigure(encoding="utf-8")` in the five named entry points — to the real tree in a proper writer worktree, add the widened locale guard, and run `scripts/preflight.sh` (and `PREFLIGHT_FULL=1` if the ASO candidate is touched) to prove the repair does not disturb the 22 artifacts this run hashed.* Every input that task needs now exists: the exact file and line numbers, the verified patch shape, the committed sha256 of each artifact it must not change, and a guard that fails on the traceback rather than the exit code. It requires write authority this lane does not have, so it belongs to a writer with a worktree — not to a read-only campaign worker.

A second, smaller successor if the owner wants it separated: decide explicitly whether `_generated_utc` should stay in the eight timestamped artifacts. It makes sha256 useless as a provenance check on exactly the artifacts the repository elsewhere hashes for provenance. That is a design decision for the owner, not a defect I should pre-empt.

result: Across 35 `research/manuscripts` generators and 215 real runs, W12's encoding patch FIXES 11 (10 proven byte-identical to committed sha256, including `endpoint-regime-map.json` `f542b99d…` and `fusion-junction-aso-submission-tables.md` `cd7f516c…`) but leaves 5 STILL BROKEN under a second, distinct defect — `print()` of non-ASCII to a locale-encoded `sys.stdout`, which no `open(encoding=)` can reach; `submission_metrics.py` writes a byte-perfect artifact and still exits 1, and `line_citations.py` returns the same exit 1 for a crash as for a finding, so no gate can tell them apart.
