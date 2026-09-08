<!-- collected 2026-09-08T03:43:42Z by campaign coordinator; agent id a152db636356cd601; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a152db636356cd601.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

**W29c** — preflight-row execution lane, OPUS-CAPACITY-CAMPAIGN-20260908. Second successor to W29, sibling of W29b.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). Nothing in the container environment names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start** `Tue Sep  8 03:36:30 UTC 2026` · **end** `Tue Sep  8 03:40:25 UTC 2026`.
`git rev-parse HEAD` **start** `1c9d827870599576c0c027a9134363d59456fd04` · **end** `5ae0fa04ff9516ac8f820381079d644a094f4a77`. HEAD advanced under me (coordinator collecting sibling reports). Every input I measured was read at the live checkout and is anchored to `file:line`; a report-only commit between the two HEADs does not touch `scripts/preflight.sh`, the four modules, or the six data files.
`git status --porcelain` **start** empty, **end** empty. I wrote nothing into `/home/user/Rare-cancers` and issued no git write operation. All execution under `/tmp/claude-0/w29c/`, **which I deleted before returning** (`ls -d /tmp/claude-0/w29c` → `No such file or directory`; free space 19 G).

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (end-of-run capture; identical in content to the start capture, from which the five long proxy-list variables `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` are filtered here — they appear verbatim in the start capture in the transcript and carry no model information):

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

## Question

W29 claimed five of the eighteen `--check` rows at `scripts/preflight.sh:847-864` can pass vacuously; W29b **refuted one of the five by execution** (row 3, `submission_citations.py`, rc=2 not rc=0). One in five claimed-vacuous rows was wrong when actually run, and three of the remaining four rest on a single worker's demonstration that nobody re-ran.

**My question, exactly:** for rows **11** (`aso_deposit_drift.py`), **16** (`trigger_scan.py`), **17** (`citation_debt.py`) and **18** (`news_match.py`) — construct the degenerate input independently, record the *real* exit code, and state CONFIRMED or REFUTED per row. Then, for each degenerate state, does a guard elsewhere in preflight compensate? W29b asserted `systems/parser_guard.py` compensates for one absence case but not the empty-list case, and explicitly labelled that claim **PROPOSED (NOT RUN)**. I ran it.

Open because (a) re-derivation of a claim that already failed once for a sibling is the point of the unit, and (b) the compensation claim was never executed by anyone.

## Prior-work check

Read in full as instructed: `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W29b-vacuous-path-reachability.md`. `reports/W29-preflight-row-provenance.md` read via targeted extraction (`grep -n -E "vacuous|row 1[1678]|aso_deposit_drift|trigger_scan|citation_debt|news_match|D2|D5|rc="` then the matched passages in context) — its full text is 30 KB and its rows 1-10, 12-15 are outside my unit.

W25 was not read, referenced, extended or audited (HELD and EXCLUDED). `scripts/preflight.sh` was **not run as a whole**. Row 13 (`atr_hrd_sarcoma_series.py`) was **never invoked** in any tree.

Commands run for prior-work and coverage, with what they showed:

- `grep -rn -E "news-match-queue\.json|citation-debt\.json" --include=*.py --include=*.sh --include=*.mjs --include=*.yml .` (campaign reports excluded) → 7 hits, all inside `citation_debt.py`, `news_match.py`, `trigger_scan.py`, `vaccine_construct.py`. **No existence guard, no writer for the ledger.**
- `grep -rn -E "deposit-drift|deposit_drift" …` → the module, `scripts/preflight.sh:857`, and **one test**, `research/manuscripts/tests/test_the_deposit_the_papers_cite_is_current.py`.
- `grep -rln -E "method-watch-triggers|news-match-queue|citation-debt" scripts/tests research/autonomy/tests systems/tests research/manuscripts/tests research/modalities/tests` → 5 files, all under `systems/tests` or `research/modalities/tests`.
- `grep -rn -E "len\((triggers|items|rows)\)|assert .*(triggers|items|rows).*[0-9]" scripts/tests systems/tests` → **no assertion on any of the three collections** (hits are `autonomy-health`, `systems_check` plan items, `modality_census` rulings). Independently reproduces W29b's negative.

Non-duplication: W29 classified all 18 bodies; W29b measured provenance/reachability and executed row 3. I re-derive **exit codes** for the four rows W29b explicitly did *not* re-run (its own PROPOSED list), and I **execute** the compensation claim W29b could only read. CLOSED-WORK items not replayed: no PUB-ASO edit, no Brenca/Hofvander/Davis, no `GSE4303`/`GSE28866`, no NR4A Perspective, no source fetch, no clinical claim. **No network was attempted at all**, so I have no denial to record. No paid API, no GPU, no publication.

## Method and inputs

Row indices confirmed independently by `sed -n '840,870p' scripts/preflight.sh`: the `for g in` loop opens at **847** with `submission_tables.py` and closes at **864** with `news_match.py`; counting 1-based gives 11 = `aso_deposit_drift.py`, 16 = `trigger_scan.py`, 17 = `citation_debt.py`, 18 = `news_match.py`. W29's line citation stands.

| Input | Path | Role |
|---|---|---|
| Gate | `scripts/preflight.sh:847-864` (rows), `:866-900` (reporting loop), `:716` (parser_guard), `:1080-1088` (modalities pytest) | what the gate runs and what it prints |
| Row 11 | `research/manuscripts/aso_deposit_drift.py`; `aso/deposit-state.json`, `aso/fusion-junction-aso-archive-manifest.json`, `aso/fusion-junction-aso-preprint-checklist.md` | |
| Row 16 | `scripts/trigger_scan.py`; `research/method-watch-triggers.json`, `research/manuscripts/emc-systems-map.json` | |
| Row 17 | `scripts/citation_debt.py`; `research/literature/citation-debt.json` | |
| Row 18 | `scripts/news_match.py`; `research/literature/news-match-queue.json` | |
| Compensation | `systems/parser_guard.py`; `research/manuscripts/tests/test_the_deposit_the_papers_cite_is_current.py`; `research/modalities/tests/test_glue_watch_row.py`; `research/modalities/tests/test_trigger_board_filter.py` | |
| Scratch | `/tmp/claude-0/w29c/tree` — `tar --exclude=./.git` of `scripts systems research .github .claude/skills CLAUDE.md CLAUDE-history.md STRATEGY.md AGENTS.md README.md`, ~640 MB, **deleted at end** | the only place any degenerate input existed |

System `python3` (`/usr/local/bin/python3`), `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w29c/pyc`. Every original file was backed up before mutation and byte-restored after (`diff -q` → `ALL_IDENTICAL`).

**One method note that matters for row 11:** the scratch tree deliberately carries no `.git`, so `_git(["show", rev + ":" + manifest])` fails and `_digests_at` returns `None` — i.e. the scratch *is* the "published revision unresolvable" environment (equivalently: the shallow CI checkout the module's own comment at `:89-91` names). No network was reachable or attempted: `git -C <non-repo> fetch` errors before any transport.

## Result

### R1 — Real exit codes for the four rows (`PRIMARY`, all executed)

| Row | Module | Degenerate input I built | Real exit code | Vacuous-pass claim |
|---|---|---|---|---|
| **11** | `aso_deposit_drift.py` | Ran the module **without** `--check` in a rev-unresolvable tree, so the checklist's generated block became the "⚠ The drift cannot be measured here … UNKNOWN" block; then `--check` | **rc = 0**, and **zero bytes of output** | **CONFIRMED** |
| **16a** | `trigger_scan.py` | `research/manuscripts/emc-systems-map.json` moved away | **rc = 0** | **CONFIRMED** |
| **16b** | `trigger_scan.py` | registry restored; `research/method-watch-triggers.json` `"triggers"` set to `[]` (39 → 0) | **rc = 0** | **CONFIRMED** |
| **17** | `citation_debt.py` | `research/literature/citation-debt.json` `"rows"` set to `[]` (4 → 0) | **rc = 0** | **CONFIRMED** |
| **17b** | `citation_debt.py` | ledger file moved away (variant W29 did not test) | **rc = 1**, uncaught `FileNotFoundError` traceback | not vacuous — **row goes red** |
| **18a** | `news_match.py` | `research/literature/news-match-queue.json` `"items"` set to `[]` (47 → 0) | **rc = 0** | **CONFIRMED** |
| **18b** | `news_match.py` | queue file moved away | **rc = 0** | **CONFIRMED** |

**All four remaining claimed-vacuous rows are CONFIRMED by execution.** The vacuous-pass count is **4 of 18**, exactly as W29b's refutation of row 3 leaves it; nothing here moves it further. Baselines were green first in the same tree (`39 trigger(s)`, `4 record(s), 12 destination(s)`, `47 queued item(s)`), so each rc=0 is a *change of input with no change of verdict*, not a tree that was already broken.

### R2 — Three findings the two prior reports do not contain (`PRIMARY`)

**(a) Row 11 passes in complete silence, and preflight discards every row's success text anyway.** On `--check` success `aso_deposit_drift.main` returns 0 having printed nothing at all. And the reporting loop at `scripts/preflight.sh:881-893` captures each row's output to `$_genout/$i.out` and, when `gen_rc = 0`, prints only `   OK   $label` — the captured text is used **only on failure**. So the denominators rows 16/17/18 do print (`0 ERROR across 0 trigger(s)`, `0 record(s), 0 destination(s)`, `0 ERROR across 0 queued item(s)`) **never reach a reader through the gate**. A human watching preflight cannot distinguish 39 triggers from 0, or 47 queued items from 0, because the gate shows neither number in either case.

**(b) Row 18's printed census is a committed field, not a recomputation — so the degenerate line is self-contradictory and nothing notices.** With `items: []` the check printed, verbatim:

```
news_match --check: 0 ERROR across 0 queued item(s); 0 verdict(s) were rejected at write time; census {'prior_art': 0, 'supports': 7, 'complicates': 1, 'supersedes': 0, 'unclear': 8}
```

Sixteen bearings censused over zero items. `scripts/news_match.py:316` prints `q.get("_bearing_census")` — a value read straight out of the JSON, written at `--ingest` time (`:261`) and never re-derived at `--check` time. The check has, in hand, a committed number that contradicts its own count, and compares them not at all.

**(c) Row 17's *absence* case is not vacuous — it is an uncaught traceback.** `citation_debt.py:56` opens `LEDGER` with no existence guard, so a deleted ledger raises `FileNotFoundError` out of `main`, rc = 1. The gate goes red for the right outcome by the wrong mechanism, and prints the generic `STALE literature citation debt -- rerun 'python3 scripts/citation_debt.py' and commit the result` remedy, which is wrong advice for a missing file. This is the one case among the seven where the row is *not* blind, and it is worth recording as a negative.

### R3 — Compensation elsewhere in preflight, **executed** (`PRIMARY`)

`systems/parser_guard.py` runs at `scripts/preflight.sh:716`. I baselined it green in the scratch tree (`parser_guard: 5 dependency groups checked · every registered parser can still find its input`, rc=0) and then re-ran it under each degenerate state:

| Degenerate state | Row's own rc | `parser_guard` rc | Net: does the tree notice? |
|---|---|---|---|
| A. `emc-systems-map.json` absent (16a) | 0 | **1** — `ERROR [emc_systems_map_check] … is missing`, plus 3 `ERROR [trigger_scan] … evidence_home does not exist` | **COMPENSATED** |
| B. `method-watch-triggers.json` `triggers: []` (16b) | 0 | **0** | **NOT compensated by parser_guard** — see the test caveat below |
| B2. `method-watch-triggers.json` absent | — | **1** — `ERROR [trigger_scan] method-watch-triggers.json is missing` | **COMPENSATED** |
| C. `citation-debt.json` `rows: []` (17) | 0 | **0** | **UNCOMPENSATED** |
| D. `citation-debt.json` absent (17b) | **1** | 0 | covered, by the row itself (traceback) |
| E. `news-match-queue.json` `items: []` (18a) | 0 | **0** | **UNCOMPENSATED** |
| F. `news-match-queue.json` absent (18b) | 0 | **0** | **UNCOMPENSATED** |
| G. deposit-drift UNKNOWN block committed (11) | 0 | **0** | **UNCOMPENSATED by parser_guard** — see below |

**W29b's compensation claim is CONFIRMED by execution**, and sharpened: the map-absence case is caught by *two* independent parser_guard checks (`emc_systems_map_check` and the `trigger_scan` `evidence_home` join), and the triggers-file-absence case is caught too. Its "empty list is not compensated" is also confirmed — `parser_guard` checks that a parser can *find* its input, never how much input there is, which is precisely the shape that lets `triggers: []`, `rows: []` and `items: []` through both guards.

**Row 11, source-level only (`PROPOSED (NOT RUN)` — pytest is absent from this container and installing it is outside my scope).** The one other guard that touches the block is `research/manuscripts/tests/test_the_deposit_the_papers_cite_is_current.py`. Its `§3` predicate is `"PUBLISHED DEPOSIT IS BEHIND" in _open_blocking_section(text).upper()`. Measured by line number in the live checklist: `## 3 · Open …` is at **310**, `⛔ **THE PUBLISHED DEPOSIT IS BEHIND THE PAPER.**` at **471**, and the generated block spans **486-523**. The trigger string is inside §3 and **outside** the generated block, so replacing the block's contents with the UNKNOWN text leaves that predicate satisfied. The test's own docstring says so in advance: *"The generator's own `--check` is the stronger binding (it compares the block byte for byte) and runs in the commit loop. This stays because it fails with the reader's question."* The stronger binding is the row I just showed exits 0 on the UNKNOWN block. This is a code reading plus a line-offset measurement, not a run.

**Row 16b, a genuine refinement of W29b, also source-level (`PROPOSED (NOT RUN)`).** Two modality tests pin *named* triggers out of `method-watch-triggers.json` and would not survive an emptied array:
- `research/modalities/tests/test_glue_watch_row.py:37,42` — `next((t for t in d["triggers"] if t["id"] == TRIGGER_ID), None)` then `assert t is not None, "%s was removed from method-watch-triggers.json"`.
- `research/modalities/tests/test_trigger_board_filter.py:136` — `next(t for t in cfg["triggers"] if t["id"] == "TRG-E3-RECRUITER-STRUCTURE")`, a bare `next` that raises `StopIteration` on an empty list.

So W29b's "row 16b is uncovered by either guard" is right about the two *guards* and incomplete about the *tree*: the modalities pytest tier would catch it — **conditionally**. `scripts/preflight.sh:1080-1088` runs `research/modalities/tests/` in full only when `SEL_STATUS` is neither `scoped` nor `none`; a commit whose change-selector scopes away those two files leaves row 16b uncovered end to end. I could not execute this branch (no pytest), so the coverage is **UNKNOWN-in-execution**, argued from source and from the selector's own branching.

**Nothing anywhere pins a citation-debt row id or a queue item.** `grep -rn -E "CD-000|news-match-queue|_bearing_census"` over all five test directories returns **zero hits**. Rows 17 (`rows: []`) and 18 (`items: []`, and queue absent) have no compensator anywhere in the tree that I could find.

**I authored no repair, no patch, no diff and no new gate. No guard was weakened, relaxed or reordered. `scripts/preflight.sh` was not run. Row 13 was never invoked.**

## Validation evidence

Environment for every run: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, `/usr/local/bin/python3`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w29c/pyc`, cwd `/tmp/claude-0/w29c/tree`. No network attempted.

**RUN — baselines, before any mutation:**
```
$ python3 scripts/trigger_scan.py --check
trigger_scan --check: 0 ERROR across 39 trigger(s); 27 registry revival_trigger field(s) seen
rc=0
$ python3 scripts/citation_debt.py --check
citation debt: 4 record(s), 12 destination(s)
   every declared destination is decided and every discharge verified
rc=0
$ python3 scripts/news_match.py --check
news_match --check: 0 ERROR across 47 queued item(s); 0 verdict(s) were rejected at write time; census {'prior_art': 0, 'supports': 7, 'complicates': 1, 'supersedes': 0, 'unclear': 8}
rc=0
$ python3 research/manuscripts/aso_deposit_drift.py --check       # scratch has no .git → rev unresolvable
the declared deposit drift is not the measured one. This module owns that block; rerun it without --check and commit the result.
⚠ REGENERATE THE ARCHIVE MANIFEST FIRST — this reads the manifest's digests, so a stale manifest makes this print a confident wrong number rather than a stale one.
rc=1
```

**RUN — row 11.** Committed block at HEAD begins `⛔ **28 deposited paths differ** from the published record: **27 changed, 1 added, 0 removed** against its own manifest at 4fd4698daec0.` Step 1, the write in a rev-unresolvable tree:
```
$ python3 research/manuscripts/aso_deposit_drift.py
wrote the deposit-drift block: UNKNOWN changed, UNKNOWN added, UNKNOWN removed against 4fd4698daec0
rc=0
```
The block is now, verbatim:
```
<!-- BEGIN GENERATED deposit-drift · aso_deposit_drift.py · DO NOT EDIT BY HAND -->

⚠ **The drift cannot be measured here**: git cannot produce the published record's revision `4fd4698daec0`, so the size of the gap is UNKNOWN — which is not the same as zero. Run `git fetch origin 4fd4698daec0c39ac77544083dc35d053a4e1e7e` and regenerate.

<!-- END GENERATED deposit-drift -->
```
Step 2:
```
$ python3 research/manuscripts/aso_deposit_drift.py --check
rc=0
--- stdout+stderr (verbatim, empty means no output) ---
--- end ---
```

**RUN — rows 16, 17, 18:**
```
$ mv research/manuscripts/emc-systems-map.json …            # 16a
$ python3 scripts/trigger_scan.py --check
trigger_scan --check: registry not found at /tmp/claude-0/w29c/tree/research/manuscripts/emc-systems-map.json — skipping cross-check
rc=0

$ # registry restored; triggers: 39 -> []                    # 16b
$ python3 scripts/trigger_scan.py --check
trigger_scan --check: 0 ERROR across 0 trigger(s); 27 registry revival_trigger field(s) seen
rc=0

$ # citation-debt.json rows: 4 -> []                         # 17
$ python3 scripts/citation_debt.py --check
citation debt: 0 record(s), 0 destination(s)
   every declared destination is decided and every discharge verified
rc=0

$ mv research/literature/citation-debt.json …                # 17b
$ python3 scripts/citation_debt.py --check
Traceback (most recent call last):
  File "/tmp/claude-0/w29c/tree/scripts/citation_debt.py", line 142, in <module>
    sys.exit(main())
  File "/tmp/claude-0/w29c/tree/scripts/citation_debt.py", line 132, in main
    errors = check(verbose=True)
  File "/tmp/claude-0/w29c/tree/scripts/citation_debt.py", line 56, in check
    with open(LEDGER, encoding="utf-8") as fh:
FileNotFoundError: [Errno 2] No such file or directory: '/tmp/claude-0/w29c/tree/research/literature/citation-debt.json'
rc=1

$ # news-match-queue.json items: 47 -> []                    # 18a
$ python3 scripts/news_match.py --check
news_match --check: 0 ERROR across 0 queued item(s); 0 verdict(s) were rejected at write time; census {'prior_art': 0, 'supports': 7, 'complicates': 1, 'supersedes': 0, 'unclear': 8}
rc=0

$ mv research/literature/news-match-queue.json …             # 18b
$ python3 scripts/news_match.py --check
news_match --check: no queue committed yet — nothing to validate
rc=0
```

**RUN — `parser_guard` compensation sweep**, baseline then all eight states; results tabled in R3. Baseline and post-restore both:
```
$ python3 systems/parser_guard.py
parser_guard: 5 dependency groups checked · every registered parser can still find its input
rc=0
```
State A verbatim head: `ERROR [emc_systems_map_check] research/manuscripts/emc-systems-map.json is missing`. State B2 verbatim: `ERROR [trigger_scan] method-watch-triggers.json is missing` / `parser_guard: 1 parser(s) have lost their input.`

**Restoration:** `diff -q` on all three mutated JSON files against their pre-mutation copies → `ALL_IDENTICAL`; checklist byte-restored from backup; `parser_guard` green again after restore. Live tree `git status --porcelain` empty at start and end.

**PROPOSED (NOT RUN):**
- Every pytest-based compensation claim (`test_the_deposit_the_papers_cite_is_current.py`, `test_glue_watch_row.py`, `test_trigger_board_filter.py`). `python3 -m pytest` reports `No module named pytest` in this container; I did not install it. These are source readings with line numbers, labelled as such.
- I did not build a shallow git clone; the rev-unresolvable condition was produced by a `.git`-free scratch copy, which reaches `_digests_at → None` by the same branch but is not the same provenance.
- I did not run `--ingest` on row 18 to reach `items: []` through the production path; I set the array directly.

## Limitations

- **Four rows measured, of eighteen.** This says nothing about the gate as a whole; `scripts/preflight.sh` was not run and row 13 was never invoked.
- **The degenerate inputs are constructed, not observed.** No repository record shows any of these states occurring on a real branch, and I did not look for one. Reachability-in-practice for rows 11/16/17/18 remains W29b's provenance argument, which I did not re-derive; my unit was exit codes, not reachability.
- **Row 11's environment is a `.git`-free scratch tree, not a shallow clone.** Both reach `_digests_at → None`, but I measured the branch, not the CI provenance.
- **All pytest-tier compensation is unexecuted.** Whether the modalities tests actually redden on `triggers: []` is UNKNOWN-in-execution, and additionally gated by the change-selector at `preflight.sh:1080`.
- **A missing compensator is a search result, not a proof.** I grepped five test directories and the `.py/.sh/.mjs/.yml` surface; a guard expressed some other way would not have been found. Absence here is UNKNOWN, not zero.
- No repair, patch, gate or diff was authored, proposed as code, or applied; no guard weakened or reordered; no clinical, EMC-efficacy, safety, selectivity or readiness claim is made or implied — there is no wet lab and none of this touches biology.

## Stop condition

**Set at the outset:** return as soon as (a) each of rows 11, 16, 17, 18 has a degenerate input I built myself and a real exit code recorded from a run I performed, with a CONFIRMED/REFUTED verdict per row, and (b) the compensation question has been answered per row by **executing** `systems/parser_guard.py`, not by reading it.

**MET on both.** (a) Seven degenerate states across the four rows, all executed, all exit codes recorded verbatim — four rows CONFIRMED vacuous, plus one variant (ledger absent) found *not* vacuous. (b) `parser_guard` baselined green and re-run under all eight states, confirming W29b's compensation claim by execution and confirming its empty-list negative. The one branch I could not execute (pytest) is labelled NOT RUN with its source evidence.

## Tool-call and wall-clock count actually used

**22 tool calls**, **~4 minutes wall clock** (`date -u` 03:36:30Z → 03:40:25Z). Well inside the ~40/~40 target. Scratch directory deleted; 19 G free at exit.

## Next concrete action

**Two candidates, both outside this read-only lane because each ends in a change; hand them to whoever owns the gate.**

1. **The highest-value unexecuted item is the pytest tier.** The single largest gap in W29/W29b/W29c together is that no worker has been able to run `pytest`, so every "a test compensates" claim in all three reports is a source reading. A successor with pytest available should run exactly three tests against exactly three degenerate states — `test_glue_watch_row.py` and `test_trigger_board_filter.py` against `triggers: []`, and `test_the_deposit_the_papers_cite_is_current.py` against the UNKNOWN deposit-drift block — and record the exit codes. That resolves the last conditional in R3 and is ~6 tool calls.
2. **Report (a) is the cheapest real defect found here and needs no floor policy:** `scripts/preflight.sh:881-893` captures each row's stdout and then discards it on success, so the denominators rows 16/17/18 already compute never reach a reader. Surfacing the captured line on `OK` is a smaller change than any floor or zero-test, is independent of the vacuous-pass debate, and would have made `0 ERROR across 0 trigger(s)` visible to a human the first time it happened. I am not proposing the edit, only naming where it belongs.
