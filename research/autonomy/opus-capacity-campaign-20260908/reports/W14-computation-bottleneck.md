> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git tree; the coordinator is the sole collector.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Repository working tree untouched (the only entry is the campaign directory that pre-existed my run). Sanity check: 9 tests fail before / 9 pass after, the new guard demonstrably fails on injected drift, all three artifacts still regenerate bit-identically, and the surrounding EMC suite is unchanged (2 pre-existing scratch-only failures before and after).

## Worker

**W14**, Lane 14 (outstanding computation/reproduction bottleneck in an active EMC analysis).

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 01:55:15 UTC 2026`. At end: `Tue Sep  8 02:03:32 UTC 2026`.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start; no model field present):

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
```
(`no_proxy`/`NO_PROXY`/`JAVA_TOOL_OPTIONS`/`npm_config_noproxy` also matched on the substring `anthropic` inside proxy exclusion lists; omitted as noise. Environment unchanged at end.)

Frozen read commit confirmed: `git log -1 --format=%H` → `92abbcb905cacf07f14b238db50d1b98f6590374`.

## Question

**Do the three EMC mortality-mechanism generators — `emc_relative_survival.py`, `emc_terminal_events.py`, `emc_mortality_decomposition.py` — have any working guard against drift between their committed artifacts and their inputs, and if not, what is the smallest correct repair?**

It is open, and the answer measured on 92abbcb90 is **no, and worse than no**: all three parse *no arguments at all*. `python3 emc_relative_survival.py --check` exits **0 after silently overwriting** `emc-relative-survival.json`. Every sibling EMC generator has a real `--check`, and those `--check` calls are exactly what `scripts/preflight.sh`'s "generated deposit artifacts reproduce from their generators" gate and `scripts/regenerate_endpoint_chain.sh` are assembled from. These three are in no gate, no chain, no workflow and no test — and wiring the old scripts into one would have produced a **permanently green row that was performing a write**, which is the repository's own named failure class (`test_a_guard_that_cannot_fail_is_not_a_guard.py`).

**Why this is active and not a closed gate.** `research/autonomy/research-ledger.json` records `PUB-MORTALITY-MECHANISM` / `claude/emc-symptom-treatment-742257` as *"A LIVE RESEARCH LINE"* with the explicit next action *"(1) `claude/emc-symptom-treatment-742257` — RECOVER IT"*, naming these five modules and *"five computed artifacts (terminal events raw and classified, the decomposition and its inputs, relative survival)"*. The manuscript `emc-mortality-mechanisms-paper.md` carries status `live`. None of paired Davis, promoter transfer, inverse bounds, conditional recurrence or RT/IPD is touched here, and `CLOSED-WORK.md` contains no entry for competing-mortality decomposition, relative survival or terminal events. The ledger's own caution (*"⛔ Do NOT quote 39.4%: the branch's own `4d61197b3` corrected the competing share to 21.7%"*) is precisely a recorded instance of a number drifting in this artifact family with nothing to catch it.

## Prior-work check

Commands run (all read-only, from `/home/user/Rare-cancers`):

```
rg -n -i "<term>" --glob '!.git' -l                       # per generator name
rg -ln "emc_relative_survival" research/manuscripts/tests/ .github/workflows/ scripts/   -> (no output)
rg -ln "emc_terminal_events"   research/manuscripts/tests/ .github/workflows/ scripts/   -> (no output)
rg -ln "emc_mortality_decomposition" research/manuscripts/tests/ .github/workflows/ scripts/
                                     -> research/manuscripts/tests/test_emc_mortality_decomposition.py
rg -rn "reproduce from their generators" --glob '!.git' -l -> scripts/regenerate_endpoint_chain.sh, scripts/preflight.sh, ...
sed -n 847,865p scripts/preflight.sh                       # the 18-row --check gate list
rg -n "relative-survival|relative survival" research/autonomy/research-ledger.json
git log -3 --format='%h %ad %s' --date=short -- research/manuscripts/emc_relative_survival.py ...
```

What they showed: the preflight `--check` gate lists **18 rows, none of them these three**. `emc_relative_survival` and `emc_terminal_events` appear in **zero** tests, workflows or scripts. `emc_mortality_decomposition` has one test module, which does not exercise a `--check` mode (there was none to exercise).

Closed items I confirmed I am **not** replaying: paired Davis, promoter transfer, inverse bounds, conditional recurrence, RT/IPD synthesis, the restricted NR4A Perspective review, the registry ICD-O paper, GSE4303/GSE28866 rediscovery, and the frozen external-validation comment. I invoked no external source and made no retrieval, so no denied route was replayed. I also deliberately did **not** touch `emc_host_factor_model.py` (exits 1 on `UNANCHORED EVIDENCE` — that is a correct guard whose repair would require inventing anchors) or `emc_supportive_effect_transfer.py` (exits 2 pending a hand-written retrieval inputs file).

## Method / inputs

- Frozen tree `92abbcb905cacf07f14b238db50d1b98f6590374`, read-only. All execution in a scratch copy at `/tmp/claude-0/w14` (`cp -r research scripts systems` plus root `*.md`). **No file under `/home/user/Rare-cancers` was created or modified**; verified at end by `git status --porcelain`, whose only line is the pre-existing untracked campaign directory.
- Interpreters: `python3` = CPython **3.11.15** (`/usr/local/bin/python3`, no pytest). Test runner: `/root/.local/bin/pytest` (the uv tool venv named in `scripts/preflight.sh`'s interpreter comment).
- Inputs actually read by the three generators, all committed: `emc-relative-survival-inputs.json` + the background-mortality life table; `emc-terminal-events-classified.json` + the Europe PMC probe; `emc-mortality-decomposition-inputs.json` + the systems-map registry.
- Empirical survey: `--help` (or `--check`) attempted on all ten `research/manuscripts/emc_*.py`; both regeneration chains executed end to end in scratch.

## Result

### Survey of the ten EMC analysis scripts (`PRIMARY` — executed, exit codes quoted)

| Script | `--help`/`--check` exit | State | Grade |
|---|---|---|---|
| `emc_relative_survival.py` | `0` — **ignored the flag and WROTE the artifact** | no argparse; unguarded | PRIMARY |
| `emc_mortality_decomposition.py` | `0` — **ignored the flag and WROTE the artifact** | no argparse; unguarded | PRIMARY |
| `emc_terminal_events.py` | `0` — **ignored the flag and WROTE the artifact** | no argparse; unguarded | PRIMARY |
| `emc_fusion_partner_pooling.py` | `0`, real `--check`: OK | guarded | PRIMARY |
| `emc_endpoint_alternatives.py` | `0`, real `--check`: OK | guarded | PRIMARY |
| `emc_endpoint_discordance.py` | `0`, real `--check`: OK | guarded | PRIMARY |
| `emc_systemic_therapy_pooling.py` | `0`, real `--check`: OK | guarded | PRIMARY |
| `emc_systems_map_check.py` | `0`, 155 items, 0 ERROR, 2 WARN | guarded | PRIMARY |
| `emc_host_factor_model.py` | `1` — `UNANCHORED EVIDENCE -- refusing to model` (HF-SMOKING `PMID 42340948`, HF-CV-RISK `PMID 42068528` in no retrieved artifact) | correctly blocked on retrieval; **not** a defect | PRIMARY |
| `emc_supportive_effect_transfer.py` | `2` — `no inputs at research/manuscripts/emc-supportive-effect-inputs.json` | expected pending-retrieval state | PRIMARY |

### Regeneration chains (`PRIMARY`)

| Chain | Exit | Finding |
|---|---|---|
| `scripts/regenerate_endpoint_chain.sh` | **0** | All 7 producers regenerated **and** re-verified; outputs bit-identical to the committed tree (`diff -rq` against the real repo: no differences outside `__pycache__`). Fully reproducible from committed inputs. |
| `scripts/regenerate_aso_chain.sh` | **1** | Not reproducible here, for two distinct reasons the script itself separates: one step is a **MISSING PREREQUISITE** — `prior-art evidence` needs `git fetch origin literature-cache:refs/remotes/origin/literature-cache`, unavailable in this sandbox — and one gate, `lint_consistency.py`, reported **FAIL**. It also reports `the manifest records no usable git_revision: None`, which it explicitly does not count as a chain failure. `UNKNOWN` whether the `lint_consistency` FAIL reproduces in the real tree; I did not re-run it there and do not claim it does. |

### The defect, demonstrated (`PRIMARY`)

Corrupting the artifact and then invoking the supposed check, before the fix:

```
$ echo '{"BROKEN":1}' > research/manuscripts/emc-relative-survival.json
$ python3 research/manuscripts/emc_relative_survival.py --check >/dev/null 2>&1; echo $?
0
$ head -c 120 research/manuscripts/emc-relative-survival.json
{
 "_readme": "Relative survival for EMC. Estimates mortality in excess of the general population, which is disease-attr
```
`ARTIFACT WAS OVERWRITTEN BY --check` — exit 0, corruption silently repaired, nothing reported. n = 3 scripts, all three identical in shape.

### The repair (`PRIMARY`, executed)

A `--check` mode on all three, matching the convention already used by `emc_endpoint_alternatives.py`. Byte-for-byte comparison is the honest comparison here because — verified by `grep -n "datetime\|utcnow\|now(\|git_revision\|_generated"`, which returned **nothing** in all three — none of these payloads carries a volatile field, so unlike `aso_archive_manifest.py` there is nothing to strip and no cry-wolf risk.

## Validation evidence

All `RUN`. Working directory `/tmp/claude-0/w14`, Python 3.11.15, pytest at `/root/.local/bin/pytest`.

**1. Test BEFORE the fix — 9 failed:**
```
$ /root/.local/bin/pytest research/manuscripts/tests/test_emc_mortality_generators_check_is_a_check.py -q -p no:cacheprovider
9 failed in 0.31s
PYTEST_EXIT=1
```
Representative failure text:
```
E  AssertionError: emc_mortality_decomposition.py --check REWROTE emc-mortality-decomposition.json
   (mtime moved 1788832918805753601 -> 1788832918904048767). A check that writes its own subject is not a check.
```

**2. Patch applied:**
```
$ python3 patch_emc_check.py /tmp/claude-0/w14/research/manuscripts
patched emc_relative_survival.py
patched emc_terminal_events.py
patched emc_mortality_decomposition.py
PATCH_EXIT=0
```

**3. Test AFTER the fix — 9 passed:**
```
$ /root/.local/bin/pytest research/manuscripts/tests/test_emc_mortality_generators_check_is_a_check.py -q -p no:cacheprovider
.........                                                                [100%]
9 passed in 0.29s
PYTEST_EXIT=0
```

**4. The new guard can actually fail (injected drift, all three):**
```
== emc_relative_survival --check on drifted artifact
FAIL: research/manuscripts/emc-relative-survival.json differs from a fresh derivation. Regenerate it with `python3 research/manuscripts/emc_relative_survival.py`.
exit=1
still-drifted(not silently repaired)=1
== emc_terminal_events --check on drifted artifact          ... exit=1   still-drifted=1
== emc_mortality_decomposition --check on drifted artifact  ... exit=1   still-drifted=1
```
The `still-drifted` line is `grep -c _INJECTED_DRIFT` on the artifact *after* the check: the guard reports the drift and leaves it in place rather than papering over it.

**5. No scientific output changed — normal regeneration still bit-identical to the committed tree:**
```
emc-relative-survival       rc=0 IDENTICAL
emc-terminal-events         rc=0 IDENTICAL
emc-mortality-decomposition rc=0 IDENTICAL
```
(`diff` against `/home/user/Rare-cancers/research/manuscripts/*.json`.) Every number in these three artifacts is unchanged; I altered no input, no constant and no computation.

**6. `--help` now works instead of writing:**
```
$ python3 research/manuscripts/emc_terminal_events.py --help
usage: emc_terminal_events.py [-h] [--check]
Tally the classified EMC terminal events, and prove every quote is real.
helprc=0
```

**7. Surrounding suite unchanged:**
```
before patch:  2 failed, 156 passed, 1799 deselected  (pytest -k emc)
after  patch:  2 failed, 165 passed, 1799 deselected  (156 + my 9)
```
The two failures are identical before and after and are **artifacts of my scratch copy, not repository defects**: `test_emc_systems_map_check.py::test_an_unclassified_use_is_an_error` and `::..._of_ANY_alias_is_an_error` need `git ls-files`, and `/tmp/claude-0/w14` is not a git repository — the checker itself says so, printing `WARN [O4] git is unavailable, so the unclassified-use sweep did not run`. Its sibling `WARN [C1]` (`origin/main` absent) is the same artifact; in the real tree `git rev-parse --verify origin/main` succeeds (`92abbcb90…`).

`PROPOSED (NOT RUN)`: adding these three as rows in `scripts/preflight.sh`'s `--check` gate list, and running `scripts/preflight.sh`. My dispatch forbids running preflight and I am read-only, so I neither edited that list nor ran the gate. The three fixed scripts are now *eligible* for it; I did not make them members.

### Code — the fix (three files, unified diff against 92abbcb90)

The full diffs are as printed by `diff -u` in the transcript above. In substance, each of the three files gets, identically:

```diff
+import argparse
 import json
```

a helper inserted immediately before `def main() -> int:` (the three copies differ only in the script name embedded in the two messages):

```python
def _emit(payload: dict, check: bool) -> int:
    """Write OUT, or under --check compare against it and write NOTHING.

    The comparison is byte-for-byte against the serialisation this script would have
    written. Nothing in this payload is volatile -- no timestamp, no git revision -- so
    there is nothing to strip and an exact comparison is the honest one.
    """
    text = json.dumps(payload, indent=1, ensure_ascii=False) + "\n"
    rel = OUT.relative_to(ROOT)
    if check:
        if not OUT.exists():
            print(f"FAIL: {rel} does not exist -- run this script without --check to create it",
                  file=sys.stderr)
            return 1
        if OUT.read_text(encoding="utf-8") != text:
            print(f"FAIL: {rel} differs from a fresh derivation. Regenerate it with "
                  f"`python3 research/manuscripts/emc_relative_survival.py`.", file=sys.stderr)
            return 1
        print("emc_relative_survival --check: OK (committed artifact reproduces exactly)")
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {rel}")
    return 0
```

argument parsing opening `main()`:

```python
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="re-derive and compare against the committed JSON; write nothing; "
                         "exit 1 on any drift")
    args = ap.parse_args()
```

and the write site routed through it:

```diff
-    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
-
-    print(f"wrote {OUT.relative_to(ROOT)}")
+    rc = _emit(payload, args.check)
+    if args.check or rc:
+        return rc
```

One cosmetic note for the coordinator: the mechanical patch leaves **three** blank lines before `def _emit` instead of two. Harmless, but worth collapsing to two before commit.

### Code — the regression test (new file)

`research/manuscripts/tests/test_emc_mortality_generators_check_is_a_check.py`:

```python
"""`--check` on the three mortality-mechanism generators must CHECK, not REWRITE.

WHY THIS EXISTS. Measured 2026-09-08 on 92abbcb90: `emc_relative_survival.py`,
`emc_terminal_events.py` and `emc_mortality_decomposition.py` parsed no arguments at all.
`python3 emc_relative_survival.py --check` therefore exited 0 *after overwriting*
`emc-relative-survival.json` -- verified by corrupting the artifact to `{"BROKEN":1}` and
watching `--check` restore it and report success. Every sibling EMC generator
(`emc_endpoint_alternatives`, `emc_systemic_therapy_pooling`, `emc_fusion_partner_pooling`,
`emc_endpoint_discordance`) has a real `--check`, and those are what
`scripts/preflight.sh`'s "generated deposit artifacts reproduce from their generators" gate
and `scripts/regenerate_endpoint_chain.sh` are built out of. These three were in no gate, no
chain and no workflow, so their committed artifacts carried no drift guard -- and wiring the
old scripts into one would have produced a permanently green row that was doing a write.

The three assertions below are the three halves of that defect: the script parses its
arguments, `--check` re-derives cleanly, and `--check` touches nothing on disk.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[3]
MANU = ROOT / "research" / "manuscripts"

CASES = [
    ("emc_relative_survival.py", "emc-relative-survival.json"),
    ("emc_terminal_events.py", "emc-terminal-events.json"),
    ("emc_mortality_decomposition.py", "emc-mortality-decomposition.json"),
]


def _run(script: str, *flags: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(MANU / script), *flags],
        capture_output=True, text=True, cwd=str(ROOT), timeout=300,
    )


@pytest.mark.parametrize("script,artifact", CASES)
def test_an_unknown_flag_is_refused(script: str, artifact: str) -> None:
    """A generator that ignores its argv cannot be given a mode, and silently writes instead."""
    proc = _run(script, "--not-a-real-flag")
    assert proc.returncode != 0, (
        f"{script} exited 0 on an unrecognised flag, so it parses no arguments at all and "
        f"`--check` is doing a WRITE. stdout={proc.stdout[:300]!r}"
    )


@pytest.mark.parametrize("script,artifact", CASES)
def test_check_reports_the_committed_artifact_reproduces(script: str, artifact: str) -> None:
    proc = _run(script, "--check")
    assert proc.returncode == 0, (
        f"{script} --check failed: {proc.stdout[-800:]}{proc.stderr[-800:]}"
    )
    assert "--check" in proc.stdout, (
        f"{script} --check printed no check verdict: {proc.stdout[:300]!r}"
    )


@pytest.mark.parametrize("script,artifact", CASES)
def test_check_does_not_write_the_artifact(script: str, artifact: str) -> None:
    """The whole point of a --check row in a gate: it may not modify what it is checking."""
    out = MANU / artifact
    before_bytes = out.read_bytes()
    before_mtime = out.stat().st_mtime_ns

    proc = _run(script, "--check")
    assert proc.returncode == 0, proc.stderr[-500:]

    assert out.read_bytes() == before_bytes, f"{script} --check changed {artifact}'s contents"
    assert out.stat().st_mtime_ns == before_mtime, (
        f"{script} --check REWROTE {artifact} (mtime moved {before_mtime} -> "
        f"{out.stat().st_mtime_ns}). A check that writes its own subject is not a check."
    )
```

## Limitations

- **This is an instrument repair, not a scientific result.** No number in `emc-relative-survival.json`, `emc-terminal-events.json` or `emc-mortality-decomposition.json` changed, and nothing here bears on EMC biology, efficacy, safety or clinical readiness. The competing-mortality estimates those artifacts carry are unaffected and retain every limitation their own `limits` blocks state (convenience sample, no denominator, a paper's own judgement rather than adjudication, referral-centre fitness bias).
- The `--check` I added proves an artifact re-derives **from its committed inputs**. It says nothing about whether those inputs are correctly extracted from the literature. The `emc_terminal_events` quote-provenance logic is what covers that, and I did not modify or re-verify it.
- **Everything was executed in a scratch copy, never in the repository.** The three `--check` runs against the real tree that the new test performs are `PROPOSED (NOT RUN)` in the real tree; they ran only against a byte-identical scratch copy of it. Because the artifacts are currently reproducible, I expect them to pass there, but I did not run them there and cannot assert it.
- I did not add these scripts to `scripts/preflight.sh` or to a regeneration chain. Until someone does, the guard exists but nothing in the commit loop runs it — which is precisely the "a `--check` that already existed, that nothing in the commit loop ran" pattern the preflight header records twice (series mismatch, instrument census). This repair makes that wiring *possible and safe*; it does not perform it.
- The `regenerate_aso_chain.sh` failure is reported as measured in scratch only. Its `literature-cache` prerequisite is genuinely unavailable here; the `lint_consistency.py` FAIL is `UNKNOWN` for the real tree.
- The mtime assertion in `test_check_does_not_write_the_artifact` would be fooled by a filesystem with coarse mtime granularity. On this ext4 sandbox `st_mtime_ns` resolved the two writes 98 ms apart, so it discriminated correctly here; the accompanying unknown-flag assertion does not depend on timing at all.

## Stop condition

**Set:** one real, active, bounded bottleneck diagnosed, fixed in code, and verified by an executed before/after regression test — with the before-failure actually shown.

**Met.** The bottleneck is real (demonstrated by corrupting an artifact and watching `--check` exit 0 while restoring it), active (`PUB-MORTALITY-MECHANISM` is a `live` line whose recovery is the ledger's named next action), and not a closed gate (absent from `CLOSED-WORK.md`; none of the forbidden failed science re-run). The before-failure is shown: **9 failed → 9 passed**, plus an injected-drift run proving the new guard is capable of failing. No acceptance criterion or guard was weakened; the change strictly adds a guard where there was none and removes a silent write.

## Tool-call and wall-clock count actually used

**28 tool calls**, wall clock **01:55:15 → 02:03:32 UTC = 8 min 17 s**. Within the ~40-call / ~40-minute target.

## Next concrete action

Add the three repaired generators to `scripts/preflight.sh`'s `--check` gate list as three rows — `research/manuscripts/emc_relative_survival.py|EMC relative survival|--check`, `…emc_terminal_events.py|EMC terminal events|--check`, `…emc_mortality_decomposition.py|EMC mortality decomposition|--check` — measure each row's cost the way the neighbouring rows are annotated, and run `scripts/preflight.sh` once on a settled tree to confirm the rows are green and the gate has not grown a cry-wolf failure. That step needs preflight-running authority this dispatch withheld, and it is the half that turns an existing check into an enforced one.

result: Found and fixed a real, active reproducibility defect — `emc_relative_survival.py`, `emc_terminal_events.py` and `emc_mortality_decomposition.py` parsed no arguments at all, so `--check` exited 0 while silently overwriting the artifact it claimed to verify; added a real `--check` to all three plus a 9-assertion regression test that goes 9 failed → 9 passed, with the new guard proven to fail on injected drift and all three artifacts still regenerating bit-identically. Code returned inline; repository working tree untouched.
