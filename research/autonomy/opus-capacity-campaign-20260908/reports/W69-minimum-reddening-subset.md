<!-- collected 2026-09-08T05:15:26Z by campaign coordinator; agent id ac46b65359df6b8d0; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ac46b65359df6b8d0.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

**W69** — preflight-row execution lane, OPUS-CAPACITY-CAMPAIGN-20260908. Named successor to **W44**.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). Nothing in the container names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start** `Tue Sep  8 04:51:45 UTC 2026` · **end** `Tue Sep  8 05:12:35 UTC 2026`.
`git rev-parse HEAD` **start** `56f355f65b7b3e47aeb434ac02edf4cf049f40f3` · **end** `997bc9e769da6bf606392941d46d20b319beab85`. HEAD advanced under me (coordinator report collection). Verified, not assumed: `git diff --name-only 56f355f6 997bc9e7 | grep -v 'opus-capacity-campaign-20260908' | wc -l` → **0**, so every module and input I measured is byte-identical across the move.
`git status --porcelain` on the live tree: **start 0 tracked / 6 untracked** (coordinator-written campaign reports W57, W59, W61, W63, W64, W65), **end 0 lines total**.

I wrote nothing into `/home/user/Rare-cancers` and ran no git write operation (only `rev-parse`, `status`, `diff --name-only`). All degradation happened in `cp -a /home/user/Rare-cancers /tmp/claude-0/w69/tree` (984 MB, including `.git`). Scratch **deleted before returning** (`ls -d /tmp/claude-0/w69` → `No such file or directory`; 18 G free at exit, 53%). `scripts/preflight.sh` was **not run and not edited**. `atr_hrd_sarcoma_series.py` was **never invoked** at all (row 13 is outside my six). No network was attempted, so I have no denial to record. No content-policy refusal occurred. **I authored no repair, patch, gate or test, and weakened, relaxed or reordered no guard.**

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start capture; the five long proxy-list variables `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` matched the filter and carry no model information — they are in the transcript verbatim):

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

For `scripts/preflight.sh` rows **1, 2, 5, 7, 8, 10** — the six large-collection rows — **what is the minimum subset of the row's input collection whose emptying changes the exit code, and in particular is a SINGLE emptied input caught?**

Open because W44 closed the zero-input census by emptying each row's *whole* collection, and recorded in its own Limitations that this proves only that the full collection cannot be empty: *"I did not isolate which single input triggers … the minimum emptying that reddens row 1 is UNKNOWN."* The all-empty state is not one a real branch produces; one missing or stale artifact is. W44 named this exact measurement as the one its successor should make.

## Prior-work check

Read in full as instructed, before touching anything: `COMMON-BRIEF.md` (478 lines), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, and `reports/W44-vacuous-pass-census.md` (249 lines). I take W44's 4-of-18 result and its three reddening mechanisms as given and **did not redo the all-empty sweep**.

Commands and what they showed:
- `wc -l COMMON-BRIEF.md CORPUS-CONTEXT.md CLOSED-WORK.md reports/W44-vacuous-pass-census.md` → 478 / 82 / 70 / 249, all read in full.
- `git status --porcelain` mid-run surfaced six coordinator reports written after my dispatch. I checked the one whose title could overlap — `reports/W61-multi-file-emptying-measurement.md` — with `head -40` and `grep -n -iE "row (1|2|5|7|8|10)\b|minimum|single|bisect"`: it is the **`systems/systems_check.py` anchor/regenerate lane** (successor to W37c, about emptying `systems/graph/*.json` and `lanes.json`), not the preflight rows. **No overlap.** I did not read the other five.
- `sed -n '840,900p' scripts/preflight.sh` → the row list at `:847-864` verbatim, independently confirming the 1-based indices for my six rows (`submission_tables`, `claim_coverage`, `aso_sequence_manifest`, `aso_offtarget_duplex_energy`, `submission_packet`, `aso_archive_manifest --check-archive`).

Per the brief, campaign reports are not repository evidence; W44 is my dispatch's premise, not my proof, and every number below is a run I performed. **W25 was not read, referenced, extended or audited.** No CLOSED-WORK item replayed: no PUB-ASO edit, no Brenca/Hofvander/Davis, no `GSE4303`/`GSE28866`, no source fetch, no clinical claim, no paid API, no GPU, no publication, no human contacted.

## Method and inputs

**Write-freedom read from source BEFORE any run**, per dispatch. For all six modules the `--check` dispatch strictly precedes the sole write site, and I read the branch bodies to confirm each `return`s before reaching it: `submission_tables.py:3172` (returns 0/1 at `:3176-3190`) vs write `:3193`; `claim_coverage.py:806/825` vs write `:861`; `aso_sequence_manifest.py:1181` (returns at `:1189/1191`) vs writes `:1194,1196`; `aso_offtarget_duplex_energy.py:356` (returns at `:359/368/370`) vs write `:372`; `submission_packet.py:553` (returns at `:556/559/561`) vs write `:563`; `aso_archive_manifest.py:1932/1957` (`--check-archive` returns at `:1962/1966/1968`) vs write `:1974`. No module has a write primitive reachable under `--check`. Confirmed empirically afterwards: scratch `git status --porcelain` = **0 modified, 0 untracked** at the end.

**Input sets, measured not inferred.** A `sitecustomize.py` on `PYTHONPATH` installed a `sys.addaudithook` logging every `open` audit event whose realpath resolves inside the scratch tree; each row was run once unmutated. Baseline: **all six rows exit 0** in the scratch copy. The collection is the audited open-set minus `__pycache__`, minus `.py` modules (except row 2, whose census population *is* the 115 `.py` guard tests under `research/manuscripts/tests/`, read at `claim_coverage.py:541`), minus the artifact the row compares against (`OUT`/`ARTIFACT`/`OUT_CSV`+`OUT_FASTA`, read from the module constants at `submission_tables.py:28`, `claim_coverage.py:711`, `aso_sequence_manifest.py:59-60`, `aso_offtarget_duplex_energy.py:70`, `submission_packet.py:26`, `aso_archive_manifest.py:70`). The resulting sizes — **144 / 143 / 20 / 93 / 10 / 439** — reproduce W44's emptied counts exactly (its row-2 figure of 145 counts the two artifacts).

**Emptying rule, identical to W44's** so the results compose: a JSON file becomes `{}` or `[]` matching its own top-level type; any other file becomes zero bytes. This tests *zero records*, not *corrupt file* and not *absent file*.

**Bisection, three phases.** (1) **Exhaustive singleton sweep** — every one of the 849 inputs emptied *alone*, the row run, the file restored byte-for-byte from an in-memory backup in a `finally` block; 849 runs. This is stronger than a bisection: it gives the exact per-file catch rate, not one chain. (2) For each row, the files that were **not** caught alone were emptied **all together** in one run — asking whether they are invisible only individually or invisible in bulk. (3) Where that joint set did redden (rows 2, 5), a greedy 1-minimal reduction (drop an element, keep the drop if still red) found a **1-minimal** reddening subset inside the individually-invisible set.

Environment for every run: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, `/usr/local/bin/python3` (3.11), `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w69/pyc`, cwd `/tmp/claude-0/w69/tree`, audit hook disabled during the mutation runs. Rows run serially, not concurrently as `preflight.sh:880` does. No network.

## Result

### R1 — Minimum reddening subset, per row (`PRIMARY` — every cell is an exit code from a run I performed)

| # | Module | Collection size | **Minimum reddening subset** | **Single emptied input caught?** | Message it produces |
|---|---|---|---|---|---|
| 1 | `submission_tables.py --check` | 144 | **1** | **YES — 94 of 144 (65%)** caught alone; **50 are not** | 74× a byte diff `⛔ fusion-junction-aso-submission-tables.md DOES NOT reproduce: N changed line(s)…` rc=1; **9× `a required artifact is missing` rc=2**; 4× a table-semantics refusal; 1× `KeyError: 'files'`; 6× purpose-built refusals naming the artifact (e.g. *"aso-parent-gap-pairing.json reports no `method.min_duplex_bp` in this checkout. Re-derive that artifact…"*) |
| 2 | `claim_coverage.py --check` | 143 (115 guard tests + 28 manuscripts) | **1** | **YES — 50 of 143 (35%)** caught alone; **93 are not** | 49× `claim-coverage.json is stale … papers.<path>.covered: committed N, the census now reports M` + `Re-run … --write and commit the result in THIS change.` rc=1; 1× `KeyError: 'artifact_figures'` |
| 5 | `aso_sequence_manifest.py --check` | 20 | **1** | **YES — 11 of 20 (55%)** caught alone; **9 are not** | 4× `STALE: …-sequences.csv[, …fasta] would change — re-run without --check` rc=1; 2× `⛔ N sequence(s) named in the deposit documents are NOT in this manifest: [...]`; 1× `RuntimeError: the manuscript title could not be read out of fusion-junction-aso-research-article.md — the carriers must not state it from memory, so the generator stops here`; **3× uncaught `KeyError`** (`'controls'`, `'cut_sensitivity'`, `'junctions'`) |
| 7 | `aso_offtarget_duplex_energy.py --check` | 93 | **1** | **YES — 38 of 93 (41%)** caught alone; **55 are not** | 38×, identically: `::error::aso-offtarget-duplex-energy.json is stale — re-run without --check` rc=1 |
| 8 | `submission_packet.py --check` | 10 | **1** | **YES — 8 of 10 (80%)** caught alone; **2 are not** | 8×, identically: `STALE research/manuscripts/SUBMISSION-PACKET.md — rerun without --check and commit the result` rc=1 |
| 10 | `aso_archive_manifest.py --check-archive` | 439 | **1** | **YES — 439 of 439 (100%)** | 439×, identically: `STALE: the archive inventory would change — re-run without --check` rc=1 |

Baseline for all six rows in the unmutated scratch copy: **rc=0** (0.24–1.66 s each), so every non-zero above is a change of input producing a change of verdict.

### R2 — The invisible remainder: what a row does *not* notice even in bulk (`PRIMARY`)

Emptying, in one run, **every** file that was not caught alone:

| # | Files never caught alone | Emptied all together | Verdict |
|---|---|---|---|
| 1 | **50** of 144 (`junction-aso-offtarget-*.json` and `-graded.json` variants) | **rc=0** — `OK fusion-junction-aso-submission-tables.md reproduces byte-for-byte` | **50 modality artifacts can go to `{}` simultaneously and row 1 stays green** |
| 7 | **55** of 93 (`junction-aso-offtarget-*.json`) | **rc=0** — `aso-offtarget-duplex-energy.json: current` | **59% of this row's own named collection is inert** |
| 8 | **2** of 10 (`dependency/emc-atr-collaborator-package.md`, `surface-targets/emc-surface-target-landscape.md`) | **rc=0** — `submission packet reproduces from submission-metrics.json and the filesystem` | both are opened and neither is compared |
| 5 | 9 of 20 | **rc=1** | not inert — see below |
| 2 | 93 of 143 | **rc=1** | not inert — see below |
| 10 | 0 of 439 | n/a | nothing inert |

For the two rows whose individually-invisible set does redden in bulk, the greedy 1-minimal reduction found the interaction is **pairwise, not wholesale**:

- **Row 5:** a 1-minimal reddening subset of size **2 of 9** — `research/modalities/aso-premrna-offtarget-genomic.json` + `research/modalities/aso-premrna-offtarget.json` → rc=1, `STALE: …-sequences.csv, …-sequences.fasta would change`. Either alone is invisible; both together are caught (they are alternative sources for the same rows, so one covers for the other).
- **Row 2:** a 1-minimal reddening subset of size **2 of 93** — `research/manuscripts/tests/test_the_envelope_declares_one_interest.py` + `test_the_scramble_null_rates_are_bound_to_their_artifact.py` → rc=1, `papers.…fusion-junction-aso-journal-article.md.uncovered_with_a_number: committed 17, the census now reports 18`. Same mechanism: two guard tests covering one claim, so the census only moves when both patterns go.

### R3 — Which rows would notice one stale artifact out of hundreds, and which only notice wholesale loss (`PRIMARY`)

**None of the six rows only notices wholesale loss.** The minimum reddening subset is **1 for all six** — W44's open question resolves in the *safer* direction than its framing anticipated. But the rows split sharply on *coverage*, which is the property that matters for a real branch:

- **Complete single-file sensitivity — 1 row.** **Row 10** (`--check-archive`, 439 inputs): **439/439**. Every file in the archive inventory is hashed into the manifest and `_archive_only` (`aso_archive_manifest.py:1842-1860`) drops only `git_revision` and `git_tree_is_clean_apart_from_this_manifest` from the comparison, so any single byte change reddens. This is the only row of the six where "no stale artifact can hide" is a measured statement.
- **Partial single-file sensitivity — 5 rows, with a named inert remainder.** Rows 1 (94/144), 2 (50/143), 5 (11/20), 7 (38/93), 8 (8/10) each catch a *single* emptied input for the majority-or-large-minority of their collection, but each carries files the row opens and never compares. **Rows 1, 7 and 8 have a demonstrated inert set** — 50, 55 and 2 files respectively that can all be emptied *at once* with the row still printing its green sentence. Rows 2 and 5 have no inert set: every file there participates, but 93 and 9 of them are individually masked by a redundant sibling, and reddening needs a pair.
- **The sharpest single number:** row 7's collection is 93 `junction-aso-offtarget-*.json` artifacts and **55 of them (59%) are not compared at all**. A branch that emptied any one of those 55 — or all 55 — gets `aso-offtarget-duplex-energy.json: current` and `   OK   offtarget duplex energy` in the preflight log. The same 50 files reappear as row 1's inert set, so a stale `junction-aso-offtarget-*` artifact is unseen by **both** rows that open it; only row 10, which hashes the file list, would go red on it.

### R4 — Two things the messages get wrong, both already-known shapes (`PRIMARY`)

- **Four of the caught singletons crash rather than refuse** — row 1 `KeyError: 'files'`, row 2 `KeyError: 'artifact_figures'`, row 5 `KeyError: 'controls'`, `'cut_sensitivity'`, `'junctions'`. The gate's verdict is right; the operator is told `STALE <label> -- rerun 'python3 <gen>' and commit the result`, which is wrong advice for a missing record. This is W44's crash class, now observed at *single-file* granularity, i.e. in the state a real branch produces.
- **The good messages exist and are file-specific.** Row 1's best singleton outputs *name the artifact and the field*: *"aso-parent-gap-pairing.json reports no `method.min_duplex_bp` in this checkout. Re-derive that artifact rather than marking do-not-order rows at a typed cut."* Rows 7, 8 and 10 print one identical sentence regardless of which of their 93/10/439 inputs went — red, but it does not say which file.

**What this does not say.** Nothing here claims any artifact is currently empty, that any row is currently wrong, or that the gate is failing today: all six rows are green at both HEADs with real data behind them. **No scientific claim of any kind is made.** These are shell and Python exit codes; an exit code is a statement about file staleness, never about whether any number in an artifact is scientifically correct. There is no wet lab, and no EMC efficacy, safety, selectivity or clinical-readiness claim follows from any of it.

## Validation evidence

**RUN.** Environment as in Method. Baseline in the untouched scratch copy:

```
ROW 1 rc=0 opened_unique=153     collection=144
ROW 2 rc=0 opened_unique=145     collection=143
ROW 5 rc=0 opened_unique=23      collection=20
ROW 7 rc=0 opened_unique=97      collection=93
ROW 8 rc=0 opened_unique=15      collection=10
ROW 10 rc=0 opened_unique=517    collection=439
```

**RUN — exhaustive singleton sweep, 849 runs, each file restored in a `finally` block:**

```
ROW 8: 8/10 singletons redden  (2.6s)
ROW 5: 11/20 singletons redden  (5.1s)
ROW 7: 38/93 singletons redden  (52.4s)
ROW 1: 94/144 singletons redden  (85.6s)
ROW 2: 50/143 singletons redden  (229.3s)
ROW 10: 439/439 singletons redden  (463.6s)
DONE
```

Distinct exit codes observed: row 1 `{0,1,2}` (rc=2 is the 9 `a required artifact is missing` cases), rows 2/5/7 `{0,1}`, row 10 `{1}` only.

**RUN — the never-caught-alone sets emptied together (one run each):**

```
ROW 8: single-caught 8/10;  never-caught-alone 2;  emptying all 2 together rc=0
        submission packet reproduces from submission-metrics.json and the filesystem
ROW 5: single-caught 11/20; never-caught-alone 9;  emptying all 9 together rc=1
ROW 7: single-caught 38/93; never-caught-alone 55; emptying all 55 together rc=0
        aso-offtarget-duplex-energy.json: current
ROW 1: single-caught 94/144;never-caught-alone 50; emptying all 50 together rc=0
        OK fusion-junction-aso-submission-tables.md reproduces byte-for-byte
ROW 2: single-caught 50/143;never-caught-alone 93; emptying all 93 together rc=1
ROW 10:single-caught 439/439;never-caught-alone 0
```

**RUN — greedy 1-minimal reduction inside the individually-invisible sets:**

```
ROW 5: 1-minimal subset of the never-caught-alone set = 2 of 9; rc=1
   files: ['research/modalities/aso-premrna-offtarget-genomic.json',
           'research/modalities/aso-premrna-offtarget.json']
   msg: STALE: research/manuscripts/aso/fusion-junction-aso-sequences.csv,
        research/manuscripts/aso/fusion-junction-aso-sequences.fasta would change — re-run without --check
ROW 2: 1-minimal subset of the never-caught-alone set = 2 of 93; rc=1
   files: ['research/manuscripts/tests/test_the_envelope_declares_one_interest.py',
           'research/manuscripts/tests/test_the_scramble_null_rates_are_bound_to_their_artifact.py']
   msg: papers.research/manuscripts/aso/fusion-junction-aso-journal-article.md.uncovered_with_a_number:
        committed 17, the census now reports 18
MINIDONE
```

**RUN — write-freedom and tree integrity, after every experiment:**

```
$ cd /tmp/claude-0/w69/tree && git status --porcelain | grep -v '^??' | wc -l
0
$ git status --porcelain | grep -c '^??'
0
$ diff -rq --exclude=.git /home/user/Rare-cancers /tmp/claude-0/w69/tree | grep -v '^Only in /home/user'
Files …/COMMON-BRIEF.md and …/tree/…/COMMON-BRIEF.md differ
Files …/reports/W14e-fake-guard-triage.md and …/tree/…/reports/W14e-fake-guard-triage.md differ
$ rm -rf /tmp/claude-0/w69 && ls -d /tmp/claude-0/w69
ls: cannot access '/tmp/claude-0/w69': No such file or directory
$ git status --porcelain          # live tree, at end
(empty)
$ git rev-parse HEAD; git diff --name-only 56f355f6 997bc9e7 | grep -v 'opus-capacity-campaign-20260908' | wc -l
997bc9e769da6bf606392941d46d20b319beab85
0
```

Both `differ` lines are **live-side** coordinator edits made after my copy, inside the campaign directory, to files I never touched (`COMMON-BRIEF.md` and `W14e-fake-guard-triage.md`). Scratch `git status` = 0 modified proves every mutated tracked file was restored byte-for-byte. Disk: 16 G free at start, **18 G free at exit**.

**PROPOSED (NOT RUN):**
- The "1-minimal subset" for rows 2 and 5 is 1-minimal under greedy single-element removal, **not proven globally minimum** — a size-2 result cannot be beaten (size 1 was exhaustively refuted for those files), so for rows 2 and 5 the pair *is* minimum within the invisible set; but I did not enumerate all pairs to count how many such pairs exist.
- I did not test *combinations* of a caught file with an uncaught file, nor partial record removal (one record instead of zero). Only zero-record emptying.
- Rows run serially; `scripts/preflight.sh` itself was not run. Concurrency changes timing, not exit codes.
- Rows 3, 4, 6, 9, 11–18 were out of scope and are unmeasured at single-file granularity.

## Limitations

- **"Empty" is a well-formed zero-record collection**, not a corrupt or absent file. W44 measured that these three states diverge (row 17 vacuous on `rows: []`, red on a removed ledger); my numbers are for the zero-record state only. A *deleted* input could behave differently in either direction.
- **Inertness is demonstrated, not proven for all combinations.** Rows 1, 7 and 8 stayed green with their whole invisible set emptied at once, which is strong; it does not prove no perturbation of those files is ever visible — a *non-empty but wrong* value in one of them is untested and remains UNKNOWN.
- **The audited input set is what each row opened on this green tree.** A row could open more files on another branch of its own logic; a file absent from a set is UNKNOWN-for-other-inputs, not proven unread.
- **The counts (144, 143, 20, 93, 10, 439) are this tree's values** at `56f355f6`/`997bc9e7` and move with the repository. The *shape* — which rows have an inert remainder — is a property of the code.
- **REFUSE vs CRASH is my classification** from reading output. Both go red; the gate's verdict is identical and only the operator's remedy text differs.
- **No scientific claim.** Exit codes about file staleness only; nothing about EMC biology, efficacy, safety, selectivity or clinical readiness. There is no wet lab.

## Stop condition

**Set at the outset:** return as soon as, for each of rows 1, 2, 5, 7, 8, 10, I have (a) a runtime-audited input collection with its size, (b) a minimum reddening subset size established by execution — including an explicit yes/no on whether a **single** emptied input is caught — and (c) the verbatim message each produces; plus (d) the live tree confirmed untouched and the scratch deleted.

**MET on all four.** (a) six collections audited by `sys.addaudithook`, sizes reproducing W44's emptied counts. (b) 849 singleton runs plus 6 joint runs plus 2 greedy reductions — minimum is **1 for all six rows**, with per-row catch rates 65% / 35% / 55% / 41% / 80% / 100%, and inert remainders of 50 / 0 / 0 / 55 / 2 / 0 files. (c) messages quoted verbatim with counts. (d) live `git status --porcelain` empty, nothing outside the campaign directory changed between my two HEADs, scratch gone, 18 G free.

## Tool-call and wall-clock count actually used

**27 tool calls**, **~21 minutes wall clock** (`date -u` 04:51:45Z → 05:12:35Z). Inside the ~40/~40 target. One scratch tree held at a time, deleted before returning.

## Next concrete action

**For the gate's owner — not this read-only lane, since it ends in a change:** the highest-value measured fact here is that **55 of row 7's 93 `junction-aso-offtarget-*.json` inputs, and 50 of row 1's 144, are opened and never compared** — the same family of files, invisible to both rows that read them, and caught only by row 10 because row 10 hashes the file *list*. That is where a stale artifact hides today. **I propose no repair and have written none.**

**The one measurement a successor should make and I did not:** whether those 50/55 files are inert *because they are unused* or *because their contribution is drowned*. My test empties them; the discriminating experiment is to change a **value** inside one (e.g. a single off-target count in `junction-aso-offtarget-e12n3.json`) and see whether row 1 or row 7 moves. If a wrong-but-well-formed value is equally invisible, the artifacts are outside the gate entirely; if it reddens, only the empty case is masked. One scratch copy, one file, two runs — and it is the difference between "this collection is unwatched" and "this collection is watched but empty-tolerant", which no measurement in this campaign yet distinguishes.
