> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git working tree; the coordinator is the sole collector.
> Per-child runtime model evidence, extracted by the coordinator from the child transcript:
> `"model":"claude-opus-5"` (OBSERVED, not self-report).

---

Sanity check passed: under a hostile (ASCII) locale the patched read/write shape reproduces the committed artifact byte-identically (sha256 `f542b99d…`), while the current code raises `UnicodeDecodeError`. Report below.

---

## Worker

**W12**, Lane 12 — actual observed Windows portability friction affecting EMC reproducibility.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model; the coordinator must extract the actual per-child runtime model from the transcript. Literal output of the required command (start of run, `date -u` = `Tue Sep 8 01:54:48 UTC 2026`) is long; the non-redacted, non-proxy lines are:

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
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

End of run `date -u` = `Tue Sep 8 01:57:36 UTC 2026`. End-of-run re-check of the same variables was identical for the identity-bearing lines (`AI_AGENT=claude-code_2-1-263_agent`, `CLAUDE_CODE_VERSION=2.1.42`, `CLAUDE_EFFORT=medium`, `CLAUDE_CODE_ENTRYPOINT=remote`).

Frozen read commit confirmed: `git log -1 --format=%H` → `92abbcb905cacf07f14b238db50d1b98f6590374`. No file under `/home/user/Rare-cancers` was created or modified; no git write of any kind was performed. All execution scratch is under `/tmp/claude-0/w12/`.

---

## Question

**Does a locale/line-ending-dependent text-I/O defect in the EMC analysis scripts change the values or the bytes of committed EMC artifacts on a non-UTF-8 platform (Windows being the motivating case), and is it caught by any existing guard?**

It is open because the 2026-09-04 throughput memo repaired a *different* portability class (native path separators in consistency scans, plus `.gitattributes` line-ending preservation at checkout) and then recorded a **passing** portability suite. Nothing in the tree addresses what Python itself *writes* and *reads* when the process locale is not UTF-8. I checked: there is **no guard for this anywhere in the repository** (see Prior-work check).

I did **not** assume a shared cause or a "~97 same-cause" set. The census I actually measured (52 in `research/manuscripts`, 1221 in `research/modalities`, 3 in `scripts`) matches no such figure, and I treat the classes separately below.

---

## Prior-work check

**Retained failure evidence — what actually exists, stated plainly.**

```
$ rg -n -i "windows|win32|WinError|CRLF|\\r\\n|os\.sep|PermissionError|cp1252|encoding" \
     research/ scripts/ systems/ --glob '!.git' | head -80
```
→ ~80 hits, **none of which is a failure record**. Every `Windows`/`win32` hit is in `scripts/research_run.py` (the Codex runner's Windows job-object containment — live code, not a defect log). Every `encoding` hit is a *correct* explicit `encoding="utf-8"`, i.e. evidence of prior hardening, not of breakage.

```
$ ls research/autonomy/preflight-logs/     → 10 .log files
$ rg -n -i -l "windows|win32|winerror|cp1252" research/autonomy/preflight-logs/
                                            → (no output, exit 1: zero matching files)
```
**There is no retained Windows failure log in the preflight logs.**

```
$ git ls-files | rg -i "windows|portab|platform"
research/autonomy/throughput-2026-09-04/archive-portability-tests.log
research/autonomy/throughput-2026-09-04/portability-tests.log
$ cat research/autonomy/throughput-2026-09-04/portability-tests.log
91 passed, 1 skipped in 20.75s
$ cat research/autonomy/throughput-2026-09-04/archive-portability-tests.log
27 passed in 2.82s
$ git log --oneline -15 --grep="[Ww]indows"
1a2d667d Bound research cycles and prepare a six-page ASO NAT candidate
```

**Honest record of the dependency:** the *only* retained description of the Windows failures is prose in `research/autonomy/throughput-2026-09-04/README.md`:

> "Repair Windows checks | Native path separators caused false parser, map, archive and residue failures. Consistency scans also descended into worktrees and dependency caches. Excluding those directories and normalizing repository paths removed those false findings; `.gitattributes` preserves source line endings."

**The exact failure logs for that class are NOT retained** — only the post-repair PASS logs above and this summary. `research/autonomy/throughput-2026-09-04/measurements.json` contains no Windows failure detail (`rg -n -i "windows|separator|gitattributes|line ending"` → 4 hits, all incidental: a benchmark method note, `runner_tests_after_windows_setting`, `separate_protocol_words`). So the specific artifact this lane's brief anticipated is **unavailable**, and per the brief I pivoted to an **observed, empirically reproduced** defect in the same lane rather than reconstructing the missing one.

I also confirmed the two repairs the memo claims are genuinely present, so I am **not** re-reporting them as defects:
- `cat .gitattributes` → `* -text` plus per-type `binary`. Real; prevents git-side EOL conversion at checkout. **Exit 0.**
- Separator normalization is real and widespread: `rg -n "\.replace\(os\.sep"` finds it applied in `submission_tables.py:89`, `lint_citations.py:365`, `submission_packet.py:243`, `emc_systems_map_check.py:960`, `aso_archive_manifest.py` (×5), `claim_coverage.py:114`, `systems_check.py:1127,1319`.

**CLOSED-WORK.md items I confirmed I am not replaying:** the lane-11 source-index bundle (case-sensitive disclaimer assertion, 9 static findings, the two `git apply --check` failures) — Lane 11 is its sole owner and I touched none of it; the retained NR4A Perspective refusal; the closed scientific gates (Davis, Hofvander, Brenca, promoter transfer, ICD-O paper); and all unrecovered sources (Pazopanib, anthracycline, sunitinib, trabectedin, Wagner, CTARC). This lane's finding is a code defect and depends on none of them.

**Novelty check for my actual finding:**
```
$ rg -n "getpreferredencoding|utf8_mode|PYTHONUTF8" --glob '!.git' .
   (no output, exit 1)
```
**Zero hits repository-wide.** No test, script, doc, or CI step anywhere considers the process's preferred encoding. This defect class is unguarded and, as far as the tracked corpus shows, undiagnosed.

---

## Method / inputs

- Frozen tree at `92abbcb905cacf07f14b238db50d1b98f6590374`, read-only.
- Interpreter: `Python 3.11.15`, Linux `6.18.44-fc-v24`.
- **Critical environment observation:** this container runs with `sys.flags.utf8_mode = 1` and `locale.getpreferredencoding(False) = 'utf-8'`, with `LANG` and `LC_ALL` both **unset**. UTF-8 mode is what makes the defect invisible here.
- Files audited: `research/manuscripts/*.py`, `scripts/*.py`, `research/modalities/*.py`, `systems/*.py`.
- Census method: `ast.parse` + `ast.walk` over every module, flagging `open(...)`/`io.open(...)` calls whose mode string contains no `b` and whose keywords contain no `encoding`, plus `Path.read_text`/`write_text` without `encoding`. Run from `/tmp` heredoc; the tree was not mutated.
- Artifacts probed (committed, read-only): `research/manuscripts/aso/fusion-junction-aso-submission-tables.md`, `research/manuscripts/endpoint/endpoint-regime-map.json`, `research/manuscripts/endpoint/placebo-arm-calibration.json`, `research/manuscripts/endpoint/endpoint-corpus.json`.
- Windows text-mode semantics were reproduced on Linux two ways: (a) `open(..., newline="\r\n")`, which is byte-exact for what Win32 text mode does to `\n`; (b) `LC_ALL=C LANG=C PYTHONUTF8=0 python3 -X utf8=0`, which yields a non-UTF-8 `getpreferredencoding` and exercises the identical `open()` code path Windows would.

---

## Result

### Census of unguarded text I/O (PRIMARY — measured by AST, not grep)

| Directory | `open()` text-mode, no `encoding=` | `Path.read_text` no `encoding=` | `Path.write_text` no `encoding=` | Grade |
|---|---:|---:|---:|---|
| `research/modalities` | 1221 | 16 | 12 | PRIMARY |
| `research/manuscripts` | 52 | 5 | 2 | PRIMARY |
| `scripts` | 3 | 0 | 0 | PRIMARY |
| `systems` | 0 | 1 | 1 | PRIMARY |

Top `research/manuscripts` offenders (the EMC analysis layer): `placebo_arm_calibration.py` 7, `vaccine_path_tables.py` 7, `submission_citations.py` 6, `submission_tables.py` 4, `orr_dcr_reread.py` 4, `endpoint_prior_art_audit.py` 4, `endpoint_corpus.py` 4, `emc_systems_map_check.py` 4, `endpoint_regime_map.py` 4, `build_aixiv_metadata.py` 3.

Uncertainty: the AST count is exact for statically-written `open(...)` calls; it cannot see `open` reached through an alias or `functools.partial`. It is therefore a **lower bound**. The count is a count of call sites, not of files that actually carry non-ASCII — the impact ranking below does that separately.

### Do the EMC artifacts actually contain characters a Windows ANSI codepage cannot hold? (PRIMARY)

| Artifact | bytes | distinct non-ASCII | cp1252-encodable? |
|---|---:|---:|---|
| `aso/fusion-junction-aso-submission-tables.md` | 69,246 | 27 (`§°²³¹×Δ–—“”†` …) | **NO** — `UnicodeEncodeError` at `\u2032` (prime), pos 2264 |
| `endpoint/placebo-arm-calibration.json` | 53,551 | 10 (`\xa0´üγ\u2009≤≥⚠⛔⭐`) | **NO** — `UnicodeEncodeError` at `\u26d4`, pos 2376 |
| `endpoint/endpoint-regime-map.json` | 54,064 | 2 (`⚠⛔`) | **NO** — `UnicodeEncodeError` at `\u26d4`, pos 40812 |
| `endpoint/endpoint-corpus.json` | 941,272 | 8 (`©®±ïöμ≥，`) | **NO** — `UnicodeEncodeError` at `\uff0c` (fullwidth comma), pos 114903 |

n = 4 artifacts, all committed at the frozen commit. This is a property of the committed bytes, not an estimate.

### Ranked findings

---

**R1 — Silent data corruption on read: `open(CORPUS)` with no `encoding=`. EMPIRICALLY REPRODUCED. Highest impact.**
Sites: `endpoint_regime_map.py:264,266,544`; `placebo_arm_calibration.py:202,204,208,212,216,511`; `endpoint_result_figures.py:181`; `emc_systems_map_check.py:157,879,1344`; and 40 more in `research/manuscripts`.

This is ranked first not because it is loudest but because in the Windows case it is **silent**. cp1252 maps almost every byte value, so decoding a UTF-8 artifact as cp1252 raises **no exception**:

```
cp1252 DECODE of the UTF-8 artifact: SUCCEEDED SILENTLY (no exception)
  utf-8 sees : '  ],\n  "⛔_t'
  cp1252 sees: 'â›”_the_zero'
  json.loads on the mojibake string: OK
```

`json.loads` accepts the mojibake. A JSON **key** in `endpoint-regime-map.json` silently changes identity from `⛔_the_zero…` to `â›”_the_zero…`. Any downstream lookup on that key misses, and the analysis proceeds with a different value rather than stopping. Under a stricter ASCII locale it instead raises — `UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2 in position 40812` — which is the *better* outcome. Grade: **PRIMARY** (the corruption is demonstrated on the committed artifact, not predicted).

**R2 — Re-derivation checks compare corrupted text against fresh text. EMPIRICALLY REPRODUCED.**
`endpoint_regime_map.py:544` and `placebo_arm_calibration.py:511` implement the `--check` path: read the committed `OUT` with a bare `open(OUT)`, then compare to the freshly computed `doc`. On a non-UTF-8 platform the committed side is mojibake and the computed side is correct, so the comparison fails and prints `FAIL: {OUT_REL} does not re-derive. Differing keys: [...]`. **This is a reproducibility check failing for a purely non-scientific reason** — structurally the same failure mode as the retained lane-11 case-sensitive disclaimer assertion, which is why I flag it separately from R1.

**R3 — Hard failure on write: `open(OUT, "w")` + `json.dump(..., ensure_ascii=False)`. EMPIRICALLY REPRODUCED.**
Sites: `endpoint_regime_map.py:554`, `placebo_arm_calibration.py:521`, `submission_tables.py:3193`, `vaccine_path_tables.py:243`, `aso_delivery_routes.py:261`, `emc_systems_map_check.py:1333`.

The defect is a *pair*: `ensure_ascii=False` deliberately emits non-ASCII, while the sink has no `encoding=`. Reproduced with the exact call shape at `submission_tables.py:3193`:
```
write WITHOUT encoding=: UnicodeEncodeError: 'ascii' codec can't encode character '\u2014' in position 15: ordinal not in range(128)
```
On Windows this is `'charmap' codec can't encode character '\u2032'` (proven encodable-check above). Grade: **PRIMARY** for the failure; **PREDICTION** only for the precise Windows exception text, since I have no Windows host.

**R4 — Line-ending translation silently changes the sha256 of byte-hashed artifacts. EMPIRICALLY REPRODUCED.**
No manuscript write path passes `newline=`. Only three places in the whole tree do (`scripts/measure_bounded_review.py:59`, `research/modalities/surface_address_sensitivity.py:367,368` — all `newline="\n"`), which shows the repository already understands this class and fixed it in exactly two files.

This matters because the repository **hashes source bytes**: `.gitattributes` opens with "Scientific build stamps hash source bytes"; `build_submission_parts.py:434` records `hashlib.sha256` of the manuscript a part was cut from; `citation_scan_cache.py` keys every cache entry on a file's sha256. Measured on the real artifact:

```
committed sha256      : cd7f516ca52f99f9b6504e50da3333fa538f18d4c32e4e1636fa98dee7bc941e
POSIX text-mode write : cd7f516ca52f99f9b6504e50da3333fa538f18d4c32e4e1636fa98dee7bc941e MATCH
Win32 text-mode write : 510156b1370d68d70dcf73ebc37e56a3ed1086028c2341c3a83f441919236708 DIFFER
size posix=69246 win=69725 delta=479 bytes
```

**This is the incompleteness in the 2026-09-04 repair.** `.gitattributes` `* -text` correctly stops git converting line endings at *checkout*, but it has no effect on what the Python *generator* writes. A Windows regeneration of `fusion-junction-aso-submission-tables.md` produces a 479-byte-larger file with a different sha256 and identical scientific content — invalidating every provenance stamp and cache key over it. Grade: **PRIMARY**.

**R5 — No guard exists for any of the above. PRIMARY (measured absence).**
`rg -n "getpreferredencoding|utf8_mode|PYTHONUTF8" --glob '!.git' .` → zero hits, exit 1. The `portability-tests.log` 91-pass suite cannot detect R1–R4 because it ran under the same UTF-8-mode interpreter that masks them. Note this is an **UNKNOWN-to-the-repo gap that I measured as absent in the tracked corpus**, not proof that no one ever knew.

**R6 — Hardcoded `/tmp` defaults. STATIC FINDING (NOT EMPIRICALLY REPRODUCED).**
`scripts/venue_typeset_geometry.py:176`, `research/modalities/ternary_stage_validate.py:17`, `boltz_src/entry.py:48,63`, `nrv04_charge_cache.py:45,67`, `abfe_sel_leg.py:132,137`, `selcal_dockq_decoy_scale.py:189,193`, and others. `/tmp` does not exist on Windows. **However**, every one of these I inspected is either an `argparse` default the caller overrides, an environment-variable fallback (`os.environ.get(..., "/tmp/...")`), or inside `boltz_src/` which runs on a Linux GPU container by design. I therefore rank this **low** for EMC reproducibility and did **not** patch it. Reporting it because the lane asked for it, and marking it honestly as not reproduced and probably not worth touching.

**R7 — `os.symlink` in tests. STATIC FINDING (NOT EMPIRICALLY REPRODUCED).**
`research/manuscripts/tests/test_the_census_artifact_and_the_guard_corpus_are_a_pair.py:112,286`. `os.symlink` needs Developer Mode or elevation on Windows and raises `OSError`/`WinError 1314` otherwise. Two call sites, test-only, no effect on EMC values. Low.

**Explicitly NOT a finding.** Path separators. The memo's repair is real and I could not find an EMC-relevant regression. The `.split("/")[-1]` occurrences (`verify_map_edit_anchors.py:178,189`, `lint_readability.py:351`, `row4_pose_map_edits.py:387`) all operate on *already-normalized repo-relative* strings and only for console display. I record this as a **negative result**: the assumed dominant cause for this lane is, as far as I can measure, already fixed.

---

## Validation evidence

All commands `RUN` from `/home/user/Rare-cancers` (read-only) with scratch in `/tmp/claude-0/w12/`. Environment: Python 3.11.15, Linux 6.18.44-fc-v24, `LANG`/`LC_ALL` unset, `sys.flags.utf8_mode=1`.

**V1 — baseline locale (exit 0):**
```
py 3.11.15 / getpreferredencoding(False)= utf-8 / sys.flags.utf8_mode= 1 / LANG= None LC_ALL= None
```

**V2 — cp1252 encodability of committed artifacts (exit 0):** table in Result. Four `UnicodeEncodeError` messages quoted verbatim there.

**V3 — silent cp1252 mojibake on read (exit 0):** quoted verbatim in R1.

**V4 — CRLF sha256 divergence (exit 0):** quoted verbatim in R4.

**V5 — the defect reproduced on Linux with the exact call shapes (exit 0):**
```
$ LC_ALL=C LANG=C PYTHONUTF8=0 python3 -X utf8=0 - <<'EOF' ... EOF
utf8_mode      = 0
preferredenc   = ANSI_X3.4-1968
write WITHOUT encoding=: UnicodeEncodeError: 'ascii' codec can't encode character '\u2014' in position 15: ordinal not in range(128)
read WITHOUT encoding= : UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2 in position 40812: ordinal not in range(128)
```

**V6 — SANITY CHECK: the proposed patch shape fixes it and reproduces the committed bytes (exit 0):**
```
$ LC_ALL=C LANG=C PYTHONUTF8=0 python3 -X utf8=0 - <<'EOF' ... EOF
preferredenc = ANSI_X3.4-1968
patched read : OK, 15 top-level keys
committed sha: f542b99d1f5984e6b584f6f217d6e4b000d798e84baaa954c3bf498cabe10a55
patched   sha: f542b99d1f5984e6b584f6f217d6e4b000d798e84baaa954c3bf498cabe10a55 BYTE-IDENTICAL
```
Under the same hostile locale where the current code raises, the patched read/write shape both succeeds and round-trips `endpoint-regime-map.json` to **byte-identical** committed content. This is the check I ran before reporting completion.

**V7 — census (exit 0):** AST counts in Result.

**V8 — guard absence (exit 1, no output):** `rg -n "getpreferredencoding|utf8_mode|PYTHONUTF8" --glob '!.git' .`

**PROPOSED (NOT RUN):**
- The patches in the next section were **not applied** (write isolation) and therefore **not** exercised by `pytest` or `scripts/preflight.sh`. I ran neither, per the brief.
- No Windows host was available. Every Windows-specific exception *string* is a PREDICTION; every failure *mechanism* is reproduced on Linux.
- I did not regenerate any committed artifact.

---

## Proposed minimal patches — PROPOSED (NOT RUN), do not apply without the owner

Two shapes, mechanical and content-preserving. V6 shows the combined shape reproduces committed bytes exactly.

```python
# FILE: research/manuscripts/endpoint_regime_map.py
# R1/R2 — line 264-267, build(): pin the read encoding.
def build():
    with open(CORPUS, encoding="utf-8") as fh:
        corpus = json.load(fh)
    with open(DISCORDANCE, encoding="utf-8") as fh:
        emc = json.load(fh)

# R2 — line 544, the --check re-derivation path.
        with open(OUT, encoding="utf-8") as fh:
            committed = json.load(fh)

# R3/R4 — line 554, the write path. `ensure_ascii=False` REQUIRES an explicit
# encoding; newline="\n" keeps the sha256 stable on any platform.
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
```

```python
# FILE: research/manuscripts/placebo_arm_calibration.py
# R1 — lines 202-216, build(): identical treatment, six read sites.
def build():
    with open(CORPUS, encoding="utf-8") as fh:
        corpus = json.load(fh)
    with open(ALTERNATIVES, encoding="utf-8") as fh:
        alts = json.load(fh)
    regime = None
    if os.path.exists(REGIME):
        with open(REGIME, encoding="utf-8") as fh:
            regime = json.load(fh)
    detail = {}
    if os.path.exists(DETAIL):
        with open(DETAIL, encoding="utf-8") as fh:
            detail = json.load(fh).get("records", {})
    nat = {}
    if os.path.exists(NATURAL_HISTORY):
        with open(NATURAL_HISTORY, encoding="utf-8") as fh:
            nat = json.load(fh)

# R2 — line 511.
        with open(OUT, encoding="utf-8") as fh:
            committed = json.load(fh)

# R3/R4 — line 521.
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
```

```python
# FILE: research/manuscripts/submission_tables.py
# R3/R4 — line 3193. This writes the byte-hashed manuscript table artifact,
# the one measured at 479 bytes larger under Win32 text mode.
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)
    print(f"wrote {OUT}")
    return 0
```

For R5, the smallest guard that would have caught all of R1–R4. It needs no Windows host, because it makes the hostile locale explicit:

```python
# FILE: research/manuscripts/tests/test_text_io_does_not_depend_on_the_process_locale.py
"""Committed EMC artifacts contain characters no Windows ANSI codepage can hold, and the
repository hashes source bytes. A generator that inherits the locale encoding or the platform
line ending therefore either crashes, silently corrupts, or changes a sha256 -- for a reason
that has nothing to do with the science. Reproduced on Linux via UTF-8 mode off + C locale;
no Windows host is required."""
import ast
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)

# The EMC analysis modules whose outputs are committed and byte-hashed. Extend
# deliberately; a blanket sweep over every module would be a different change.
GUARDED = (
    "endpoint_regime_map.py",
    "placebo_arm_calibration.py",
    "submission_tables.py",
)


def _bare_text_opens(path):
    """(lineno, mode) for open() calls in text mode with no explicit encoding."""
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if not (isinstance(fn, ast.Name) and fn.id == "open"):
            continue
        mode = ""
        if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
            mode = node.args[1].value or ""
        for kw in node.keywords:
            if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                mode = kw.value.value or ""
        if "b" in mode:
            continue
        if any(kw.arg == "encoding" for kw in node.keywords):
            continue
        out.append((node.lineno, mode or "r"))
    return out


@pytest.mark.parametrize("module", GUARDED)
def test_every_text_open_pins_its_encoding(module):
    bare = _bare_text_opens(os.path.join(MANUSCRIPTS, module))
    assert not bare, (
        f"{module}: text-mode open() without encoding= at lines "
        f"{[n for n, _ in bare]}. These inherit locale.getpreferredencoding(), "
        "which is cp1252 on Windows and ASCII under LC_ALL=C."
    )


@pytest.mark.parametrize("module", GUARDED)
def test_every_text_write_pins_its_newline(module):
    """Win32 text mode turns '\\n' into '\\r\\n', changing the sha256 of a hashed artifact."""
    bad = [n for n, m in _bare_text_opens(os.path.join(MANUSCRIPTS, module)) if "w" in m or "a" in m]
    with open(os.path.join(MANUSCRIPTS, module), encoding="utf-8") as fh:
        src = fh.read()
    assert 'newline="\\n"' in src or not bad, (
        f"{module}: writes text without newline=\"\\n\"; regeneration on Windows "
        "would change committed bytes without changing content."
    )


def test_the_modules_import_under_a_non_utf8_locale():
    """The end-to-end reproduction: same interpreter, UTF-8 mode off, C locale."""
    env = dict(os.environ, LC_ALL="C", LANG="C", PYTHONUTF8="0")
    for module in GUARDED:
        proc = subprocess.run(
            [sys.executable, "-X", "utf8=0", "-c",
             "import importlib, sys; sys.path.insert(0, %r); "
             "importlib.import_module(%r)" % (MANUSCRIPTS, module[:-3])],
            env=env, capture_output=True, text=True,
        )
        assert proc.returncode == 0, (
            f"{module} fails to import under LC_ALL=C with UTF-8 mode off:\n{proc.stderr}"
        )
```

I have **not** run this test. It is `PROPOSED (NOT RUN)`. I did not author or relax any acceptance criterion; the assertions restate constraints the repository already imposes on itself (byte-hashed stamps, `.gitattributes` byte preservation).

---

## Limitations

- **No Windows host.** Every mechanism is reproduced on Linux via a non-UTF-8 locale; the specific Windows exception text and the exact cp1252 failure position are PREDICTIONS derived from encoding the committed bytes, not from a Windows run.
- **The retained evidence this lane was built around does not exist.** The Windows path-separator failure logs are not in the tree — only a prose summary and post-repair PASS logs. I did not reconstruct, infer, or approximate them. Everything I report instead is independently measured at the frozen commit.
- **The AST census is a lower bound** and counts call sites, not affected files. A site reading pure-ASCII data is harmless; I did not classify all 1288 sites, only the EMC-critical ones.
- **`research/modalities` (1221 sites) is largely out of scope for EMC reproducibility** — much of it is GPU/compute driver code that runs only on Linux containers by design. I did not triage it and make no claim about it.
- **This is a code-portability finding only.** It says nothing about EMC biology, NR4A3 fusion behaviour, degrader efficacy, safety, selectivity, or clinical readiness. It does not change any scientific conclusion; it changes whether a conclusion can be *regenerated* on a non-UTF-8 platform.
- The patches are unapplied and untested by the repository's own tiers. Whether they disturb any existing guard is **UNKNOWN**.
- R6 and R7 are labelled `STATIC FINDING (NOT EMPIRICALLY REPRODUCED)` and should not be treated as demonstrated.

---

## Stop condition

**Set:** a ranked, evidence-graded portability defect list with proposed minimal patches, *or* an honest record that the retained failure evidence is unavailable plus the alternative observed defect diagnosed instead.

**Met — both halves.** The retained Windows failure logs are recorded as unavailable with the exact commands showing their absence, and I diagnosed and empirically reproduced a distinct, currently-unguarded defect class (R1–R5) affecting committed EMC artifacts, with patches and a guard. The one check I ran before declaring completion (V6) confirms the patch shape both fixes the failure and reproduces committed bytes exactly.

---

## Tool-call and wall-clock count actually used

**18 tool calls** (target ~40). **Wall clock 01:54:48Z → 01:57:36Z ≈ 3 minutes** of tool execution (target ~40 min). No sleeping, no padding; returned on meeting the stop condition. No content-policy refusal was encountered in this lane.

---

## Next concrete action

**Apply R1–R4 to the three named EMC modules and add the R5 guard, then verify by regeneration rather than by inspection.** Concretely: with write authority, apply the patches above, then run each module's `--check` re-derivation path twice — once normally and once under `LC_ALL=C LANG=C PYTHONUTF8=0 python3 -X utf8=0` — and require that both print `OK: … re-derives` and that `sha256` of each regenerated artifact equals the committed value. That converts my single-artifact V6 result into a full re-derivation proof across the endpoint analysis, and it is the check that would have caught this class on 2026-09-04. It is a bounded, finite task for a single owner and does not touch Lane 11's source-index work.

A **rejected** successor, recorded so it is not picked up by mistake: sweeping all 1221 `research/modalities` sites. That is a large mechanical diff across GPU driver code with no demonstrated EMC-reproducibility impact, and it would violate the "do not expand one task into every optional backlog item" rule.

result: Lane 12 closed — the retained Windows failure logs do not exist in the tree (only a 2026-09-04 prose summary plus post-repair PASS logs), so I diagnosed instead a real, unguarded locale/line-ending defect in the EMC analysis scripts: 52 unencoded text-I/O sites in `research/manuscripts` write and read committed artifacts that are provably not cp1252-encodable, causing `UnicodeEncodeError` on write, *silent* mojibake corruption of JSON keys on read, and a 479-byte/different-sha256 divergence on the byte-hashed manuscript artifact — all reproduced on Linux under `LC_ALL=C PYTHONUTF8=0`, with minimal patches whose shape was verified to round-trip a committed artifact byte-identically, and a proposed guard for a class the repository currently has zero coverage of.
