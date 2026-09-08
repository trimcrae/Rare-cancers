<!-- collected 2026-09-08T03:51:46Z by campaign coordinator; agent id af5c308c199af877e; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-af5c308c199af877e.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

**W29e** — preflight-row execution lane, OPUS-CAPACITY-CAMPAIGN-20260908. Successor to W29c.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). Nothing in the container names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start** `Tue Sep  8 03:45:55 UTC 2026` · **end** `Tue Sep  8 03:48:36 UTC 2026`.
`git rev-parse HEAD` **start** `606d79f96526b651f3b825190d721f6b302c032e` · **end** `e5d60db79f9dcbe7a4b2e6b0db1de6e32ccf69e7`. HEAD advanced under me (coordinator collecting sibling reports); the three files that appeared are new campaign reports only (`W16h-…`, `W31c-…`, `W37-…`), and nothing outside `research/autonomy/opus-capacity-campaign-20260908/` changed — observed directly in my live-vs-scratch diff below.
`git status --porcelain` **start** empty, **end** empty. I wrote nothing into `/home/user/Rare-cancers` and issued no git operation other than `rev-parse`/`status`. All execution under `/tmp/claude-0/w29e/`, **deleted before returning** (`ls -d` → `No such file or directory`; 20 G free).

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start capture; the five long proxy-list variables `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` are filtered out here — they appear verbatim in the transcript and carry no model information):

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

W29c's second named next action, independent of the vacuous-pass debate: **how much of what `scripts/preflight.sh` actually measures never reaches the operator?** Concretely — for all eighteen `--check` rows and for the five other named gates, what does each print on success, does that text carry a denominator (a count of what was examined), and does the gate show it or throw it away? W29c measured the discard mechanism for three rows; nobody has measured the size of the loss across the whole gate.

Open because W29c named it and explicitly did not do it, and because the answer is a number the gate's owner can act on without settling any policy question about floors or zero-tests.

## Prior-work check

Read in full as instructed: `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W29c-degenerate-rows-re-execution.md`. `reports/W29b-vacuous-path-reachability.md` read by targeted extraction (`grep -n -E "row 3|refut|submission_citations|vacuous"` then the matched passages) — its row-3 refutation is confirmed here by independent execution (my row 3 runs green at the committed denominator of 74 citations, consistent with W29b's finding that row 3 is not vacuous on an emptied input; I did not re-derive the degenerate case).

W25 was not read, referenced, extended or audited (HELD and EXCLUDED). `scripts/preflight.sh` was **not run as a whole** and was **not edited**. Row 13 (`atr_hrd_sarcoma_series.py`) was **never invoked** in any tree.

Prior-work commands and what they showed:

- `grep -n -E "parser_guard\.py|validate-registry\.mjs|systems_check\.py|tier_budget\.py|lint_consistency\.py" scripts/preflight.sh` → the five decision sites at `:586`, `:609`, `:716`, `:723`, `:1507` (plus a docstring mention at `:7`). These are the file:line answers to part 3.
- `grep -n "" scripts/preflight.sh | sed -n '866,905p'` → the reporting loop verbatim, independently reproducing W29c's `:881-893` claim with corrected boundaries (the capture happens at `:880`, the report loop runs `:884-910`).
- `grep -n -E '"--check(-archive)?"' <each of the 17 modules>` → each module's `--check` dispatch line, all of which precede that module's write site.

I noticed a sibling report `W37-zero-test-coverage-beyond-18-rows.md` appear in the tree during my run and deliberately did **not** read it — per the brief, a sibling's report is not repository evidence, and reading it would compromise the independence of this measurement. My unit (information discarded) is a different question from zero-test coverage.

Non-duplication: W29 classified row bodies; W29b measured reachability and executed row 3; W29c executed four rows under *degenerate* inputs. I execute **all seventeen runnable rows at the committed tree, unmutated**, which no prior worker did, and extend the census to the five non-loop gates, which no prior worker touched.

No CLOSED-WORK item was replayed: no PUB-ASO edit, no Brenca/Hofvander/Davis, no `GSE4303`/`GSE28866`, no NR4A Perspective, no source fetch, no clinical claim. **No network was attempted**, so there is no denial to record. No paid API, no GPU, no publication.

## Method and inputs

**Write isolation.** Everything ran in `/tmp/claude-0/w29e/tree`, a `cp -a` copy of `/home/user/Rare-cancers` **including `.git`** (613 M tree + 367 M `.git`), so the modules could resolve revisions exactly as they do live — this is a fidelity improvement over W29c, whose `.git`-free scratch forced row 11 onto its rev-unresolvable branch. `git rev-parse HEAD` in the scratch = `606d79f9`, `git status --porcelain` empty: a faithful clean checkout.

**Write-freedom verification, both directions.**
1. *Source, before running:* for each of the 17 modules, the `--check` dispatch line precedes every write call site in that file — e.g. `submission_tables.py` dispatch `:3172` vs write `:3193`; `aso_deposit_drift.py` `--check` flag `:133` vs `open(CHECKLIST,"w")` `:155`; `instrument_census.py` `:314` vs `:331`; `news_match.py` `:372` vs the `--ingest` write at `:416`. `single_slot_identity.py` and `citation_debt.py` contain no write primitive at all.
2. *Empirical, after running:* `diff -rq --exclude=.git` live-vs-scratch reported **zero modified files** (only the three new campaign reports present live and absent from my copy), and `git status --porcelain` in the scratch stayed empty. All 17 rows plus all five other gates are byte-confirmed write-free on their check path.

**Row 13 excluded, with the source reason.** `research/modalities/atr_hrd_sarcoma_series.py:1452-1455` sits *inside* the `--check` path: after re-deriving from the cache, `if not os.path.exists(art_path): with open(art_path,"w") ... print("artifact written from the cache")`. Its `--check` therefore writes its artifact under that condition. Never invoked, in any tree.

Environment for every run: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, `/usr/local/bin/python3`, `node` for the registry validator, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w29e/pyc`, cwd `/tmp/claude-0/w29e/tree`.

## Result

### R0 — What the reporting loop does, exactly (`PRIMARY`, read at live HEAD)

| Step | Line | Behaviour |
|---|---|---|
| Scratch dir created | `:846` | `_genout="$(mktemp -d)"` — a private temp dir, deliberately outside the tree |
| Rows fan out concurrently | `:880` | `{ python3 "$gen" "$mode" >"$_genout/$_geni.out" 2>&1; echo $? > "$_genout/$_geni.rc"; } &` — **stdout and stderr are captured to a per-row file, not shown** |
| Report loop reads back | `:884-889` | `label`, `gen`, `gen_rc`, and `gen_out="$(cat "$_genout/$_geni.out" …)"` |
| **Success branch** | **`:890-891`** | `if [ "$gen_rc" = "0" ]; then echo "   OK   $label"` — **`gen_out` is read into a variable and then never referenced.** The label is a hard-coded string from the row list at `:847-864`; not one byte the module produced is printed |
| Failure branch | `:900-907` | `echo "   STALE $label -- rerun 'python3 $gen' and commit the result"`, then `if [ -n "$gen_out" ]; then echo "$gen_out" \| sed 's/^/          /'`, then `rc=1` |
| Capture destroyed | `:911` | `rm -rf "$_genout"` |

So: **captured always, printed only on failure, deleted unconditionally.** The success path emits exactly `   OK   <label>` — 18 fixed strings, identical whether the tree is fully populated or empty.

### R1 — All eighteen rows, run at the committed tree (`PRIMARY`; every row rc=0)

Row order and labels are as listed at `scripts/preflight.sh:847-864`. "Denominator" = a count of what the row actually examined.

| # | Module | Success text emitted (verbatim) | Denominator | Class |
|---|---|---|---|---|
| 1 | `submission_tables.py` | `OK fusion-junction-aso-submission-tables.md reproduces byte-for-byte` | — | EMITS-NO-DENOMINATOR |
| 2 | `claim_coverage.py` | `claim-coverage.json reproduces from the live census (28 documents)` | **28 documents** | **DISCARDED** |
| 3 | `submission_citations.py` | `74 annotated citation(s), 53 distinct PMID(s), 0 UNANNOTATED superscript(s), 0 without fetched metadata` / `  citation numbering is current` | **74 citations, 53 PMIDs** | **DISCARDED** |
| 4 | `submission_metrics.py` | 5 per-manuscript lines (`main= 5276w abs=249w items= 5 refs=11 within believed limits`, …) + `OK research/manuscripts/submission-metrics.json reproduces byte-for-byte` | **5 manuscripts, per-doc word/item/ref counts** | **DISCARDED** (763 bytes, the largest single loss) |
| 5 | `aso_sequence_manifest.py` | `sequence manifest is current (782 sequences, 72 named in the documents and all present)` | **782 sequences, 72 named** | **DISCARDED** |
| 6 | `aso_journal_tables.py` | `journal tables reproduce from the canonical sequence file` | — | EMITS-NO-DENOMINATOR |
| 7 | `aso_offtarget_duplex_energy.py` | `aso-offtarget-duplex-energy.json: current` | — | EMITS-NO-DENOMINATOR |
| 8 | `submission_packet.py` | `submission packet reproduces from submission-metrics.json and the filesystem` | — | EMITS-NO-DENOMINATOR |
| 9 | `vaccine_path_tables.py` | *(zero bytes)* | — | EMITS-NO-DENOMINATOR (silent) |
| 10 | `aso_archive_manifest.py` (`--check-archive`) | `manifest inventory is current (repository-state fields not compared)` | — | EMITS-NO-DENOMINATOR (but carries a **scope caveat** that is also discarded) |
| 11 | `aso_deposit_drift.py` | *(zero bytes)* | — | EMITS-NO-DENOMINATOR (silent) |
| 12 | `emc_condensate_report.py` | `findings note is current` | — | EMITS-NO-DENOMINATOR |
| 13 | `atr_hrd_sarcoma_series.py` | — | — | **NOT-RUN-WITH-REASON**: its `--check` path writes its artifact at `:1452-1455` |
| 14 | `single_slot_identity.py` | `OK   ART-ATR-HRD-SERIES bound to GSE299349 (artifact, 2 caches, systems map, 1 declaring document(s))` | **2 caches, 1 declaring document** | **DISCARDED** |
| 15 | `instrument_census.py` | `instrument_census --check: OK (22 instruments, 16 requirements)` | **22 instruments, 16 requirements** | **DISCARDED** |
| 16 | `trigger_scan.py` | `trigger_scan --check: 0 ERROR across 39 trigger(s); 27 registry revival_trigger field(s) seen` | **39 triggers, 27 fields** | **DISCARDED** |
| 17 | `citation_debt.py` | `citation debt: 4 record(s), 12 destination(s)` / `   every declared destination is decided and every discharge verified` | **4 records, 12 destinations** | **DISCARDED** |
| 18 | `news_match.py` | `news_match --check: 0 ERROR across 47 queued item(s); 0 verdict(s) were rejected at write time; census {'prior_art': 0, 'supports': 7, 'complicates': 1, 'supersedes': 0, 'unclear': 8}` | **47 queued items** (+ the committed census) | **DISCARDED** |

**The number the owner can act on: 9 of the 18 rows compute a denominator that the gate then throws away.** Nine denominators (28 documents, 74 citations, 5 manuscripts, 782 sequences, 2 caches, 22 instruments, 39 triggers, 4 records, 47 queued items) exist inside the gate and reach no operator. Six more rows emit non-empty prose that is also discarded but carries no count; two rows (9 and 11) produce nothing to discard; one row is unmeasured by policy.

**Total discarded on a fully green run: 1,954 bytes across 17 rows** (`wc -c` on the 17 capture files), replaced by 18 copies of `   OK   <label>` totalling roughly 470 bytes of information that does not depend on the tree's contents at all.

W29c's claim reproduces exactly and is confirmed: rows 16/17/18's degenerate texts (`0 ERROR across 0 trigger(s)`, `0 record(s), 0 destination(s)`, `0 ERROR across 0 queued item(s)`) differ from these green texts only in the numbers, and the numbers are precisely the part `:890-891` does not print. **39 and 0 are indistinguishable to a reader of the gate; so are 47 and 0, 4 and 0, 74 and 0, 782 and 0, 22 and 0, 28 and 0.**

### R2 — The five other gates: three discard, two do not (`PRIMARY`, all run)

| Gate | Decision `file:line` | How it is invoked | Success text it actually produced (run in scratch) | Reaches operator? |
|---|---|---|---|---|
| `lint_consistency.py` | `scripts/preflight.sh:586` | `if python3 research/manuscripts/lint_consistency.py; then` — **no redirection** | `lint_consistency: 0 ERROR across 29 target file(s)` | **YES — denominator (29 files) is visible** |
| `systems_check.py` | `scripts/preflight.sh:609` (capture), `:610` (success), `:613` (failure grep), `:615` (`rm -f "$_sc"`) | `>"$_sc" 2>&1`; success prints `   OK` | `systems_check: 620 objects across 15 collections · 197 ERROR · 224 WARN · 7 INFO` (red here for the known campaign-footprint reason) | **NO — and uniquely, discarded on failure too**: `:612` prints only `FAILED -- rerun … to see why`, and `:613` greps the capture solely for a missing-module hint. 224 WARN and 7 INFO are invisible in **both** branches |
| `parser_guard.py` | `scripts/preflight.sh:716` | `>/dev/null 2>&1` — **not even captured** | `parser_guard: 5 dependency groups checked · every registered parser can still find its input` | **NO — denominator (5 groups) discarded at the redirect, unrecoverable** |
| `validate-registry.mjs` | `scripts/preflight.sh:723` | `>/dev/null 2>&1` | `OK - EMC clinical registry valid: 25 citation(s), 14 cohort(s). 0 warning(s).` | **NO — denominator (25 citations, 14 cohorts) and the warning count discarded at the redirect** |
| `tier_budget.py` | `scripts/preflight.sh:1507` | `if python3 scripts/tier_budget.py --check; then :` — **no redirection** | `   ok    commit-loop 1466/1500 test function(s) in 102 file(s)` / `   ok    modalities 7247/7500 … 436 file(s)` / `   ok    paper-guards 966/1000 … 111 file(s)` | **YES — the richest visible output in the gate: three utilisations against their ceilings** |

**Extended total: 12 of 23 measured gate steps compute a denominator that is discarded** — the 9 rows plus `systems_check`, `parser_guard` and `validate-registry`. Two gates (`lint_consistency`, `tier_budget`) already do the thing R1's rows do not: they print their denominator on success, in the same script, and they are the proof that the operator-visible form costs nothing. The inconsistency is not architectural; it is three redirects and one unused shell variable.

One asymmetry worth naming precisely: `parser_guard` and `validate-registry` discard at the **redirect** (`>/dev/null`), so their text is destroyed before any branch could use it; the 18 rows and `systems_check` discard at the **branch**, having already paid to capture it. `gen_out` at `:889` is assigned and, in the success branch, never read.

### R3 — What this does *not* say

Nothing here bears on whether any row's assertion is strong enough, on floors, on zero-tests, or on the vacuous-pass count. A visible denominator would not have made row 16 fail on `triggers: []`; it would have made a human able to *see* the 0. That is the whole claim.

**I authored no repair, no patch, no diff and no new gate. No guard was weakened, relaxed or reordered. `scripts/preflight.sh` was not run and not edited. Row 13 was never invoked.**

## Validation evidence

**RUN.** Environment as in Method. All 17 rows executed serially in `/tmp/claude-0/w29e/tree` by a script mirroring the row list at `:847-864` verbatim, with index 13 replaced by a `NOT RUN BY POLICY` sentinel. Every row `rc=0`; verbatim outputs are quoted in the R1 table. Selected literal transcript:

```
### ROW 5 | research/manuscripts/aso_sequence_manifest.py | --check | canonical sequence file
rc=0
--- output ---
sequence manifest is current (782 sequences, 72 named in the documents and all present)
--- end ---
### ROW 13 | ATR HRD sarcoma series | NOT RUN BY POLICY
### ROW 16 | scripts/trigger_scan.py | --check | reopening-trigger registry join
rc=0
--- output ---
trigger_scan --check: 0 ERROR across 39 trigger(s); 27 registry revival_trigger field(s) seen
--- end ---
```

**RUN — the five other gates**, same tree:
```
$ python3 systems/parser_guard.py
parser_guard: 5 dependency groups checked · every registered parser can still find its input
rc=0
$ node scripts/validate-registry.mjs
OK - EMC clinical registry valid: 25 citation(s), 14 cohort(s). 0 warning(s).
rc=0
$ python3 scripts/tier_budget.py --check
   ok    commit-loop             1466/1500  test function(s) in 102 file(s)
   ok    modalities              7247/7500  test function(s) in 436 file(s)
   ok    paper-guards             966/1000  test function(s) in 111 file(s)
rc=0
$ python3 research/manuscripts/lint_consistency.py
lint_consistency: 0 ERROR across 29 target file(s)
rc=0
$ python3 systems/systems_check.py --check | tail
systems_check: 620 objects across 15 collections · 197 ERROR · 224 WARN · 7 INFO
rc=1
```
The `systems_check` red is the known campaign-footprint baseline the COMMON-BRIEF tells workers not to attribute; I did not attribute it and used only its summary-line *shape*, which is what the gate discards.

**RUN — write-freedom, after everything above:**
```
$ diff -rq --exclude=.git /home/user/Rare-cancers /tmp/claude-0/w29e/tree
Only in /home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/reports: W16h-expression-validation-base-revision.md
Only in /home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/reports: W31c-green-run-warnings.md
Only in /home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/reports: W37-zero-test-coverage-beyond-18-rows.md
$ cd /tmp/claude-0/w29e/tree && git status --porcelain      # empty
$ wc -c /tmp/claude-0/w29e/r*.out | tail -1
1954 total
```
No `Files … differ` line: nothing any module ran modified any file. Live tree `git status --porcelain` empty at start and end.

**PROPOSED (NOT RUN):**
- Row 13. Not invoked in any tree; its behaviour and output are UNKNOWN to this report, and its contribution to the 1,954-byte figure is unmeasured.
- I did not run the rows *concurrently* as `:880` does. Concurrency changes timing, not captured text; but I measured the serial case.
- I did not run `scripts/preflight.sh` itself, so I did not observe the `   OK   <label>` lines being emitted — that half is a source reading of `:890-891`, not a run.

## Limitations

- **Seventeen rows of eighteen, one tree, one commit.** The denominators (39, 47, 782 …) are this tree's values at `606d79f9`; they change as the repository changes. The *count of rows that discard a denominator* (9/18) is a property of the code and is stable until a module's print statement changes.
- **"Denominator" is my classification, applied by reading each success string.** Row 10's "inventory is current" may well be backed by a count internally; what I measured is what it *prints*. A row classified EMITS-NO-DENOMINATOR is a statement about its output, not about its rigour.
- **The 1,954-byte figure excludes row 13** and is a green-tree measurement; a tree with more manuscripts would discard more.
- The failure-branch behaviour of the 18 rows (`:900-907` does print `gen_out`) means this loss is **success-only**. A red run is already informative; the invisible case is exactly the one an operator reads as reassurance.
- `systems_check`'s both-branch discard is read from `:609-615`; I ran the module but not the surrounding shell, so the branch behaviour is a source reading.
- No repair, patch, gate or diff was authored, proposed as code, or applied; no guard weakened or reordered. No clinical, EMC-efficacy, safety, selectivity or readiness claim is made or implied — there is no wet lab and none of this touches biology.

## Stop condition

**Set at the outset:** return as soon as (a) the reporting loop's capture/print/discard behaviour is stated with exact line numbers for the success and failure branches, (b) all eighteen rows are classified with their verbatim success text, each runnable row's text obtained from a run I performed in an isolated copy with write-freedom verified from source beforehand and by diff afterwards, and row 13 excluded with its source reason, and (c) each of the five other gates has a `file:line` decision site and a verbatim success text saying whether its denominator survives.

**MET on all three.** (a) `:880` capture, `:889` read, `:890-891` success discards, `:900-907` failure prints, `:911` deletes. (b) 17 rows run, all rc=0, all texts verbatim; row 13 excluded with `:1452-1455`; write-freedom confirmed twice. (c) Five gates run; three discard (`:609`/`:615`, `:716`, `:723`), two print through (`:586`, `:1507`).

## Tool-call and wall-clock count actually used

**14 tool calls**, **~3 minutes wall clock** (`date -u` 03:45:55Z → 03:48:36Z). Well inside the ~40/~40 target. Scratch deleted; 20 G free at exit.

## Next concrete action

**For whoever owns the gate (not this read-only lane, because it ends in a change): the loss is nine denominators in the row loop plus three in the other gates, and the repository already contains the pattern that fixes it.** `lint_consistency.py` at `:586` and `tier_budget.py` at `:1507` print their counts on success today, in the same script, at no cost — they are the existence proof that the operator-visible form is acceptable here. The three sites that discard are one unused shell variable (`gen_out`, assigned `:889`, unread in the `:890-891` success branch) and two `>/dev/null 2>&1` redirects (`:716`, `:723`), plus `systems_check`'s `:610`. I am not proposing the edit and have written none; I am handing over the measured size of what it would recover.

**The one measurement I could not make and a successor should:** row 13's success text and denominator. It is the only row whose output is unknown to any of W29/W29b/W29c/W29e, and it cannot be run in place because its `--check` writes at `:1452-1455`. A successor should copy the tree, **delete nothing**, confirm `art_path` already exists so the write branch is not taken, run it once, and record the text — roughly 4 tool calls, and it closes the 18-row census.
