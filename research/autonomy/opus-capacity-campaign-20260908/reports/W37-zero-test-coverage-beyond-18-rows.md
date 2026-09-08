<!-- collected 2026-09-08T03:47:01Z by campaign coordinator; agent id a99faa53e188f0fd6; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a99faa53e188f0fd6.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Scratch deleted, live tree untouched (`git status --porcelain` → 0 lines). Report follows.

---

## Worker

**W37** — preflight-gate census lane (extension past the eighteen `--check` rows), OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I am told I am Claude Opus 5 (`claude-opus-5`). Nothing in my environment independently confirms a served model; `env` carries no model variable at all.

`date -u` **end**: `Tue Sep  8 03:43:04 UTC 2026`. (No `date -u` was taken at start; my first tool call, `git rev-parse HEAD`, was at approximately 03:29Z by the session clock — I record this gap honestly rather than back-filling a timestamp I did not take.)

`git rev-parse HEAD` **start**: `1c9d827870599576c0c027a9134363d59456fd04` · **end**: `5ae0fa04ff9516ac8f820381079d644a094f4a77`. HEAD moved under me (coordinator report collection). `git status --porcelain` at end: **empty**. I wrote nothing into `/home/user/Rare-cancers` and ran no git write operation. All execution was under `/tmp/claude-0/w37/`, now **deleted** (`ls` → "No such file or directory"; `/` at 19 GiB free).

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start; the four long proxy-list variables `GLOBAL_AGENT_NO_PROXY`, `NO_PROXY`, `npm_config_noproxy` and `JAVA_TOOL_OPTIONS` are elided only where they repeat the `no_proxy` value verbatim):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
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
GLOBAL_AGENT_NO_PROXY=<same list as no_proxy>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=<proxy/truststore flags; repeats the no_proxy list>
NO_PROXY=<same list as no_proxy>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<same list as no_proxy>
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

For every gate `scripts/preflight.sh` invokes **outside** the eighteen-row loop at `847-864`: does it iterate a committed collection, and if so does it carry a **zero-test** (refuses on empty), a **floor** (refuses below a committed number), or **neither**? Where neither: what is the collection, what is its size at HEAD, and what would have to change for it to reach zero?

Open because W29 and W29b measured the shape exhaustively *inside* the loop and nowhere else. Both reports' denominators are "18", and `scripts/preflight.sh` is a 1,648-line script in which the loop occupies eighteen lines.

## Prior-work check

Read in full as instructed: `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W29-preflight-row-provenance.md` and `reports/W29b-vacuous-path-reachability.md` (the latter from `## Question` to the end of its Validation section).

Commands run for scope, with what they showed:

- `grep -n -v '^\s*#' scripts/preflight.sh | grep -n -E '\.py|\.mjs|\.sh|node |npm |grep -|git ls-files|awk|for f in'` → the invocation inventory below. **Fourteen gates, two report-only steps, and the test tiers sit outside `847-864`.**
- `grep -n -E 'DEFAULT_TARGETS|^TARGETS|glob|rglob|os.walk|os.listdir|json.load|for .* in |if not |return (0|1|2)|len\(' <each module>` → collection roots and guard sites.
- `wc -l` over the fourteen gate sources → 10,795 lines total, of which `systems/systems_check.py` is 4,591.

Non-duplication, checked rather than assumed. W29 classified the eighteen `--check` bodies; W29b measured reachability of five of them and read the floor precedent. **Neither touched any gate in my inventory**, with two partial exceptions I therefore do not re-derive: W29b established `systems/parser_guard.py:189-197` compensates `trigger_scan`'s registry-absence skip, and that `parser_guard.check_scan_triggers` iterates `triggers` with no floor. I re-executed both to confirm rather than restate, and my contribution there is the rest of `parser_guard`. W13f/W13g measured `validate-registry.mjs`'s cross-file `pool`-flag enforcement; **my question about that file is different** (does it refuse a zero denominator), and I make no pooling claim.

W25 was not read, referenced or extended. CLOSED-WORK items confirmed not replayed: no PUB-EMC-CLASSIFICATION, no Brenca/Hofvander/Davis, no `GSE4303`/`GSE28866`, no NR4A Perspective, no source fetch, no clinical claim. **No network was attempted at all.** `scripts/preflight.sh` was not run. `research/modalities/atr_hrd_sarcoma_series.py` was never invoked.

## Method and inputs

| Input | Path | Role |
|---|---|---|
| The script | `/home/user/Rare-cancers/scripts/preflight.sh` (1,648 lines) | invocation inventory outside `847-864` |
| 14 gate sources | the paths in R1 | read for collection root and guard shape |
| Scratch tree | `/tmp/claude-0/w37/tree` | `tar --exclude=./.git` copy of the whole working tree — **the only place any collection was emptied**; deleted at end |
| Live tree | `/home/user/Rare-cancers` | read-only; two measurements taken here (`lint_citations._tracked()` import, `ls receipts/*.json | wc -l`), `git status --porcelain` empty before and after |

System `python3`, `node` (both present). `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/w37/pyc`. No paid API, no GPU, no publication, no network.

**A method note on the clinical registry.** `research/data/emc-clinical-registry.json` was emptied **only inside the scratch copy**, never in the working tree, and no registry content was interpreted, quoted, or reasoned about — only the gate's arithmetic over it. `systems/POLICY-evidence.md` governs *editing* the registry; I edited nothing.

**A correction to my own first measurement, recorded because it is the exact defect `parser_guard` documents.** My first parse of `lint_style.TARGETS` used a loose `"([^"]+)"` regex and reported "23 declared, 10 missing". Ten of those were quoted fragments inside comments, not paths. Re-parsed with the line-shaped form `parser_guard.check_paths` uses (`^\s*"([^"]+)",?\s*$`): **13 targets, 0 missing**. The loose count is retracted.

## Result

### R0 — The inventory: fourteen gates outside the loop (`PRIMARY`)

| # | Line | Gate | rc on failure |
|---|---|---|---|
| 1 | 586 | `research/manuscripts/lint_consistency.py` | rc=1 |
| 2 | 609 | `systems/systems_check.py --check` | rc=1 |
| 3 | 627 | `research/manuscripts/emc_systems_map_check.py --check` | rc=1 |
| 4 | 650 | `research/manuscripts/lint_claims.py` | rc=1 |
| 5 | 684 | `research/manuscripts/lint_citations.py` | rc=1 |
| 6 | 700 | `research/manuscripts/lint_style.py` | rc=1 |
| 7 | 716 | `systems/parser_guard.py` | rc=1 |
| 8 | 723 | `node scripts/validate-registry.mjs` | rc=1 |
| 9 | 929 | `research/autonomy/receipt_schema.py --check` | rc=1 |
| 10 | 1437 | `research/manuscripts/lint_submission_residue.py` | rc=1 |
| 11 | 1484 | `research/autonomy/contract_check.py --check` | rc=1 |
| 12 | 1507 | `scripts/tier_budget.py --check` | rc=1 |
| 13 | 1536 | `research/autonomy/derived_ids.py --check` | rc=1 |
| 14 | 1593 | `scripts/record_selector_validation.py` (PREFLIGHT_FULL branch) | rc=1 |

Not gates: `lint_changed_prose.py` (661) and `lint_readability.py --report` (713) both end `|| true` and cannot redden a run — correctly, since the second is documented repository-wide as a screen, not a measure. The pytest tiers and the `affected_tests.py` / `paper_scoped_tests.py` selectors are a separate lane I did not enter.

### R1 — The census (`PRIMARY`; grade in the last column)

| # | Gate | Committed collection(s) it iterates | Size at HEAD | Zero-test? | Floor? | Verdict | Evidence |
|---|---|---|---|---|---|---|---|
| 1 | `lint_consistency.py` | `research/manuscripts/pinned-figures.json` → `targets`, `derivations`, `artifact_figures`, `table_completeness`, `subset_checks`, `superseded` | **29 targets** | no | no | **NEITHER** | **RUN** — C1 |
| 2 | `systems_check.py --check` | `systems/graph/*.json`, 15 collections | **620 objects** | no | no, but see note | **NEITHER (compensated)** | **RUN** — J1 |
| 3 | `emc_systems_map_check.py --check` | `research/manuscripts/emc-systems-map.json`, 8 sections | **155 items** | no | no | **NEITHER** | **RUN** — I1, I2 |
| 4 | `lint_claims.py` | in-source `DEFAULT_TARGETS` + glob `systems/views/L[012]-*.md` + `publications.json → document.file` | **137 files** | **partly, externally** | no | **MIXED** | source-derived + **RUN** (baseline) |
| 5 | `lint_citations.py` | `git ls-files --cached --others --exclude-standard` | **7,778 files / 743 prose** | no | no | **NEITHER** | **RUN** — E-git |
| 6 | `lint_style.py` | in-source `TARGETS` (13) + `FIGURE_SOURCES` (2) | **13 + 2** | no | no | **NEITHER** | **RUN** — G1 |
| 7 | `parser_guard.py` | 5 in-source check groups; inside them: plan checklist items, `pinned-figures.targets`, `lint_claims.DEFAULT_TARGETS`, `method-watch-triggers.triggers`, 6 fixed registry paths | **38 plan items, 5 groups** | **YES ×2** | no | **MIXED — the strongest gate outside the loop** | **RUN** — B1, C1b, plan-strip |
| 8 | `validate-registry.mjs` | `registry.citations`, `registry.cohorts`, and nested `consensusQuestions` / `systemicEvidence` / `emergingTreatments.items` / `studies.items` | **25 citations, 14 cohorts** | no | **per-item only** | **NEITHER (partially coupled)** | **RUN** — E1, E2 |
| 9 | `receipt_schema.py --check` | `glob.glob(research/autonomy/receipts/*.json)` | **129 files / 107 governed** | no | no | **NEITHER** | **RUN** — D1, D2 |
| 10 | `lint_submission_residue.py` | `build_submission_pdf.PAPERS` (in-source) ∪ `submission-metrics.json → rows[]` | **34 documents; 5 metrics rows** | no | no | **NEITHER (in-source half dominates)** | **RUN** — H1 |
| 11 | `contract_check.py --check` | in-source `required` field paths + `*_KEY` constants + receipt fixtures; and the contract step **text** | **5 paths, 6 constants, 7,743 chars** | no | **YES — `_MIN_STEP_CHARS = 400`** | **FLOOR (on text length, not on a collection)** | source-derived + **RUN** (baseline) |
| 12 | `tier_budget.py --check` | `scripts/tier-budgets.json → tiers` (3), and per tier a directory listing of `test_*.py` | **3 tiers; 1,466 / 7,247 / 966 functions** | no | **inverted — a CEILING** | **NEITHER, and structurally so** | **RUN** — A1, A2 |
| 13 | `derived_ids.py --check` | `derived-ledger-ids.json → bindings`, `systems/graph/routes.json`, `research-ledger.json → entries` | **83 bindings / 83 routes / 415 entries** | no | **relational coverage only** | **NEITHER when all three empty together** | **RUN** — F2, F4 |
| 14 | `record_selector_validation.py` | in-source 2-tuple `FILES` | 2 | n/a | n/a | **not a gate over a collection — it WRITES** `scripts/selector-validation.json` | source-derived, **NOT RUN by design** |

**Net: of the thirteen gates that iterate anything, one carries a floor (on a character count, not a collection), one carries zero-tests (over two of its five groups), and eleven carry neither.**

### R2 — The four cleanest instances, with the real exit codes (`PRIMARY`, executed)

These are the rows where a green run measured literally nothing, quoted verbatim from stdout.

**(a) `tier_budget.py --check` with `tiers: {}` — rc 0 and *no output at all*.**
```
-- A1 tier_budget: tiers={}
   rc=0
   (stdout empty)
-- A2 tier_budget: all tier dirs nonexistent
   rc=0
   ok    modalities                 0/7500  test function(s) in 0 file(s)
   ok    paper-guards               0/1000  test function(s) in 0 file(s)
```
This one is structural, not an oversight: a budget is a **ceiling**, and 0 ≤ 1500 is the direction the tool was built to permit. `count_dir` returns `(0, 0, [])` for a directory that is not there, so **deleting an entire test tier passes this gate green**. The module's own docstring already reasons about the inverse case — it counts an unparseable test file as **1**, "counting it as zero would let a broken file buy headroom under the ceiling, which is the wrong direction for a budget" — and the same argument applied to a vanished directory would give the opposite answer to the one the code gives. I state that as an observation about the code's own stated reasoning; I propose no change.

**(b) `lint_consistency.py` with every `pinned-figures.json` collection emptied — rc 0.**
```
lint_consistency: 0 ERROR across 0 target file(s)
```
This is the campaign's canonical sentence with the denominator visible in it. `parser_guard` run against the *same* emptied file also stayed green (`C1b`, rc 0) — its `check_paths` verifies that each declared target **exists**, which an empty list satisfies trivially. CLAUDE.md §1 makes `pinned-figures.json` the home of "changes to pinned quantities"; the gate that enforces it cannot tell an enforced contract from an emptied one.

**(c) `receipt_schema.py --check` with the receipts directory empty *or absent* — rc 0 both ways.**
```
-- D1 receipt_schema: receipts dir ABSENT   rc=0   0 governed receipt(s), 0 failure(s), 0 unreadable
-- D2 receipt_schema: receipts dir EMPTY    rc=0   0 governed receipt(s), 0 failure(s), 0 unreadable
```
The collection is a **directory listing** (`glob.glob(receipt_dir/*.json)`), 129 files at HEAD. `if (args.check and (r["failures"] or r["unparsed"]))` cannot be true over an empty glob. Note this is the receipt schema *checker* — the artifact class the preflight comment at 1550 treats as the evidence of a governed run.

**(d) `emc_systems_map_check.py --check` with every section emptied — rc 1 at first, then rc 0 after the prescribed remedy.**
```
-- I1 emptied map, committed view unchanged
   rc=1   ERROR [V1] emc-systems-map.md differs from what the registry generates
          emc_systems_map_check: 0 registry items · 1 ERROR · 1 WARN
-- I2a python3 …/emc_systems_map_check.py --write-view          rc=0  wrote emc-systems-map.md
-- I2b emptied map + regenerated view
   rc=0   emc_systems_map_check: 0 registry items · 0 ERROR · 1 WARN
```
**This is the most useful result of the unit, and it generalises W29's finding rather than contradicting it.** W29 established that the thirteen re-derivation rows resist a degenerate input *because* they compare a recomputation against committed bytes. That protection is real, and it is exactly one command deep: it fires on the state where the source shrank and the generated view did not, and the module's own instruction for that ERROR — "Regenerate with `--write-view`" — dissolves it. A commit that empties the map and regenerates its view in the same commit, which is the normal workflow this repository prescribes, passes green over **0 registry items**. `systems_check --check` behaves the same way (`J1`: the emptied graph reddens on `[G2] paper-strength.md differs … Run --write-views`, not on emptiness); I did not run the regenerate-then-check variant for `systems_check` because its baseline in my scratch copy was already rc=1 with 179 pre-existing link errors, so the second step would not have been interpretable. **`systems_check` is therefore graded source-derived for the regenerate case and RUN for the first.**

### R3 — `lint_citations.py`: the collection is not committed data at all (`PRIMARY`, executed)

Its corpus comes from a subprocess, and the failure is unguarded (`lint_citations.py:186-192`):

```python
r = subprocess.run(["git", "-C", ROOT, "ls-files", "--cached", "--others", "--exclude-standard"], …)
if r.returncode != 0:
    return []
```

Run in my scratch copy, which has no `.git`, so `git ls-files` exits non-zero:

```
lint_citations: 0 prose identifier(s), 0 unanchored, 237 in ledger (…), 237 stale ledger row(s)
lint_citation_types: 0 type claim(s) checked against 13 cached record(s), 0 error(s)
lint_citation_types: retraction sweep (2026-09-01) — 0 prose identifier(s): 0 checked against PubMed,
    0 retracted, 0 outside PubMed's reach …, 0 NOT SWEPT.
rc=0
```

**Four denominators collapse to zero simultaneously and the gate exits 0.** At HEAD the same call returns **7,778 tracked files, 743 prose, 4,526 anchor files** (measured in the live tree by importing `_tracked()` — read-only; `git status --porcelain` stayed empty).

The honest weighting: on a normal checkout `git ls-files` succeeds, so this is not a live vacuity the way W29b's `origin/literature-cache` hole is. It is reachable where git is absent, where `ROOT` is not a work tree, or from a source export. What makes it worth recording is the *shape*: this module already carries two long comments about its own readout going vacuous — the ledger anchoring itself in 2026-08-07 ("the guard kept working while its READOUT went vacuous, and a count of 0 is the one number nobody re-examines") and the type-cache exclusion of 2026-08-27 — and the `return []` above is the same failure one layer further out, on the corpus rather than the anchors. Note also that **237 of 237 ledger rows read as stale** in this state, deliberately classed "stale bookkeeping, not a defect".

### R4 — Where the collection *is* protected, and by what (`PRIMARY`)

Three protections exist outside the loop. None is a floor over a committed collection.

**(a) `parser_guard.py` — two genuine zero-tests, both executed.** Its `check_plan_heading` refuses an ORDERED PLAN section that parses to no checklist items:
```
   plan checklist items: 38
   rc=1   ERROR [work_ledger] the ORDERED PLAN section exists but contains no checklist items
          why this is not a warning: … an empty list that is indistinguishable from a finished plan
```
and `check_paths` refuses `lint_claims.DEFAULT_TARGETS` parsing to empty ("an empty target list makes the linter pass over nothing at all"), plus a **required-member** assertion that `systems/views/plan.md` is among those targets, added because moving the plan dropped the linted set silently while the warning count went *down*. **This is the only place outside the loop that names the defect and fails on it.** It is the same shape W29b established for `single_slot_identity.py:412-416`: a zero-test, not a floor — and, like it, both of `parser_guard`'s zero-tests are over things parsed out of **Python source or a Markdown section**, not over a committed JSON array. Its two JSON-array iterations, `pinned-figures.targets` and `method-watch-triggers.triggers`, have neither (B1 and C1b, both rc 0). Its summary line prints a **constant** — `5 dependency groups checked` — regardless of how much data was inside them.

**(b) `contract_check.py` — the only floor outside the loop, and it is over characters.** `_MIN_STEP_CHARS = 400`, against 7,743 chars at HEAD, refusing with "the anchor probably matched a passing mention rather than the step itself". Structurally this is the `lit_consensus_probe.py` pattern W29b identified: a committed number set far below the true value so it tests plumbing rather than content. It guards *one extracted text*, not a collection count.

**(c) `derived_ids.py` — relational coverage, which holds only while one side is populated.** Emptying the bindings table alone reddens, because every route in `systems/graph/routes.json` must be bound:
```
-- F2 bindings={}, ledger entries=[]   rc=1
   83 route(s) in systems/graph/routes.json have no derived ledger id: RT-6MP, RT-AF3-INTERFACE, … — run `derived_ids.py --extend`
```
Empty **all three** together and the coupling has nothing to compare:
```
-- F4 routes=[], bindings={}, ledger entries=[]   rc=0
   0 route→id bindings, frozen and agreeing with the ledger
```
"Frozen and agreeing" over nothing, rc 0.

### R5 — `validate-registry.mjs`: a zero denominator, printed, rc 0 (`PRIMARY`, executed)

```
-- E2:cohorts emptied alone (was n=14)
   rc=0   OK - EMC clinical registry valid: 25 citation(s), 0 cohort(s). 0 warning(s).
```

The success line **prints the denominator it did not check**. The file does carry a per-item floor — `if (!positions.length) errors.push(\`${qw} needs at least one position\`)` — so a *consensus question* may not be empty; the *set of questions*, the *set of cohorts* and the *set of citations* may all be. Emptying every collection at once gave rc 1 with 23 errors, but those come from surviving nested references to `registry.citations`, not from an emptiness refusal, and single-collection emptying is the reachable state anyway. My probes for `consensusQuestions` and `systemicEvidence` did not find those keys at the top level of `registry`, so **those two rows are uninformative and I claim nothing about them**; only the `cohorts` result is measured.

Given CLAUDE.md §7 and `systems/POLICY-evidence.md`, this is the gate over the most sensitive committed collection in the repository, and "0 cohort(s)" is a green result.

### R6 — What would have to change for each collection to reach zero (`PRIMARY` for the mechanism, `PREDICTION` for likelihood)

| Collection | Route to zero | Grade |
|---|---|---|
| `pinned-figures.json` sections | a hand edit or a merge resolving a conflicted registry to "keep theirs"; the file is hand-maintained (CLAUDE.md §1 makes it a human's file) | PREDICTION |
| `tier-budgets.json → tiers`, and each tier's directory | a hand edit, **or a directory rename/move** — `count_dir` treats a missing directory as 0 with no complaint, so a restructure empties this gate without touching it | PRIMARY (mechanism executed, A2) |
| `receipts/*.json` | a cleanup commit, a `.gitignore` change, or a checkout that omits the directory; absence and emptiness are indistinguishable here (D1 == D2) | PRIMARY (both executed) |
| `emc-systems-map.json` sections | any commit that shrinks the map **and** regenerates the view, which is the workflow the module itself prescribes | PRIMARY (I2 executed) |
| `git ls-files` corpus (`lint_citations`) | git absent, a non-work-tree `ROOT`, or a source export | PRIMARY (executed) |
| `lint_style.TARGETS`, `lint_claims.DEFAULT_TARGETS`, `builder.PAPERS` | a Python source edit only — and `DEFAULT_TARGETS` alone is externally zero-tested by `parser_guard` | PRIMARY |
| `registry.cohorts` | a hand edit to the clinical registry | PREDICTION |
| `derived-ledger-ids.bindings` + `routes.json` + `research-ledger.entries` | all three together; any one alone reddens | PRIMARY (F2/F4 executed) |

**I authored no check, no diff, no floor and no repair. No guard was weakened, relaxed or reordered. `scripts/preflight.sh` was not run and `atr_hrd_sarcoma_series.py` was never invoked.**

## Validation evidence

Environment for every run: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, system `python3` and `node`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w37/pyc`, cwd `/tmp/claude-0/w37/tree` unless stated. Each mutation was made to one file, run, then restored from the live tree before the next. **No network of any kind was attempted, so I have no denial to record.**

**RUN — baseline, unmodified scratch copy, all fourteen gates** (verbatim tail of each):

```
rc=0  lint_consistency: 0 ERROR across 29 target file(s)
rc=1  systems_check: 620 objects across 15 collections · 179 ERROR · 209 WARN · 7 INFO
rc=0  emc_systems_map_check: 155 registry items · 0 ERROR · 2 WARN
rc=0  lint_claims: 0 ERROR, 178 WARN across 137 file(s)
rc=0  lint_citations: 0 prose identifier(s), 0 unanchored, 237 in ledger …
rc=0  lint_style: 0 ERROR across 15 file(s)
rc=0  parser_guard: 5 dependency groups checked · every registered parser can still find its input
rc=0  OK - EMC clinical registry valid: 25 citation(s), 14 cohort(s). 0 warning(s).
rc=0  107 governed receipt(s), 0 failure(s), 0 unreadable
rc=0  lint_submission_residue: 34 outgoing document(s), 5 finding(s), 5 baselined, 0 new, 0 stale
rc=0  5 required field path(s), 6 key constant(s), 7743 chars of contract read, 0 disagreement(s)
rc=0  ok commit-loop 1466/1500 · ok modalities 7247/7500 · ok paper-guards 966/1000
rc=0  83 route→id bindings, frozen and agreeing with the ledger
```

Two baseline results need stating plainly rather than glossing:

- **`systems_check --check` is rc=1 on this tree**, with 179 errors, the sampled one being `research/autonomy/opus-capacity-campaign-20260908/inputs/evidence-4878/research/autonomy/OPERATING_PROTOCOL.md links to 'correspondence/README.md', which does not exist` — i.e. the gate is walking the campaign's own copied input material. Whether that also reddens the live tree is **UNKNOWN**: I did not run `systems_check` against `/home/user/Rare-cancers`, and my scratch copy is not a git checkout. I flag it and claim nothing further; it is the coordinator's to check, not mine.
- **`lint_citations` rc=0 with zero denominators is the degenerate case, not a baseline** — my scratch tree has no `.git`, which is precisely what R3 measures.

**RUN — degenerate-input experiments.** Every command's real exit code, in the order executed:

```
A1  tier-budgets.json tiers={}                                      rc=0   (no output)
A2  tier dirs -> 'no/such/dir'                                      rc=0   0/7500, 0/1000, 0/1500 in 0 file(s)
B1  method-watch-triggers.json triggers=[]  -> parser_guard         rc=0   5 dependency groups checked
B1b same file -> trigger_scan.py --check (loop row 16, confirming)  rc=0   0 ERROR across 0 trigger(s)
C1  pinned-figures.json all 6 collections=[] -> lint_consistency    rc=0   0 ERROR across 0 target file(s)
C1b same file -> parser_guard                                       rc=0   5 dependency groups checked
D1  research/autonomy/receipts ABSENT                               rc=0   0 governed receipt(s)
D2  research/autonomy/receipts EMPTY                                rc=0   0 governed receipt(s)
E1  registry: every collection emptied                              rc=1   23 error(s) (nested citation refs)
E2  registry: cohorts=[] alone (was 14)                             rc=0   OK … 25 citation(s), 0 cohort(s)
F2  bindings={} + ledger entries=[] , routes intact                 rc=1   83 route(s) … have no derived ledger id
F4  routes=[] + bindings={} + ledger entries=[]                     rc=0   0 route→id bindings, frozen and agreeing
G1  all 13 lint_style TARGETS files absent                          rc=0   lint_style: 0 ERROR across 2 file(s)
H1  submission-metrics.json rows=[] (was 5)                         rc=0   34 outgoing document(s) — corpus unchanged
I1  emc-systems-map.json every list=[] (195 items removed)          rc=1   [V1] view differs · 0 registry items
I2a --write-view on the emptied map                                 rc=0   wrote emc-systems-map.md
I2b emptied map + regenerated view -> --check                       rc=0   0 registry items · 0 ERROR · 1 WARN
I3  restored                                                        rc=0   155 registry items · 0 ERROR · 2 WARN
J1  systems/graph/*.json every list=[] (753 items removed)          rc=1   [G2] view differs · 0 objects across 15
plan systems/views/plan.md checklist items stripped (38)            rc=1   ERROR [work_ledger] … contains no checklist items
plan restored                                                       rc=0
```

**PROPOSED (NOT RUN):**
- `systems_check --check` after `--write-views` on an emptied graph — the analogue of I2b. Not run because this tree's `systems_check` baseline is already rc=1.
- `lint_claims.py` with `DEFAULT_TARGETS` emptied — requires editing the module's source, which I did not do; graded source-derived.
- `record_selector_validation.py` — never run: it writes `scripts/selector-validation.json`.
- Any behaviour of the pytest tiers or the two test selectors.

## Limitations

- **The scratch tree has no `.git`.** That is what makes R3 measurable, and it is also a confound for every gate that shells out to git: `emc_systems_map_check` printed `WARN [O4] git is unavailable, so the unclassified-use sweep did not run` and `WARN [C1] none of ('origin/main', …) is present`, and `systems_check`'s baseline redness may be partly of the same kind. Exit codes I attribute to *emptiness* are those where the emptied run differs from the same tree's own baseline; I have not separated git-absence effects inside the 179 `systems_check` errors and do not claim to.
- **Emptying a collection is not the same as a collection that got emptied on a real branch.** W29b did the reachability work for five loop rows; I did not do it for these thirteen. Every "route to zero" in R6 is graded, and the PREDICTION rows are reasoning about maintenance, not measurement.
- **`systems_check.py` is 4,591 lines and I read its collection loading and its `main()`, not its body.** Its verdict in R1 rests on one executed run plus its summary arithmetic (`total = sum(len(g[c]) for c in COLLECTIONS)`), and I mark the regenerate-then-check case source-derived.
- **`validate-registry.mjs`'s nested collections are partly unmeasured** — my `consensusQuestions` / `systemicEvidence` probes found no such top-level keys, so only `cohorts` is a measured result and I have made no claim about the others.
- This is a census of a *gate's arithmetic*. It says nothing about whether any registry, ledger, receipt or manuscript is scientifically correct, and nothing about EMC efficacy, safety, selectivity or clinical readiness. There is no wet lab and nothing here touches one.
- A gate reporting OK over an empty collection is a **measurement gap, not evidence that anything is wrong with the repository today**. Every collection I emptied is populated at HEAD, and the sizes in R1 are the measured denominators.

## Stop condition

Set up front: **return as soon as every gate `preflight.sh` invokes outside `847-864` is classified as zero-test / floor / neither, with an executed exit code wherever the gate is read-only and cheap.** **MET.** Fourteen gates enumerated; thirteen classified with a measured HEAD denominator; eleven classified by execution, two source-derived and labelled (`contract_check`'s floor, `record_selector_validation`), plus four sub-cases explicitly labelled NOT RUN. Scratch directory deleted.

## Tool-call and wall-clock count actually used

**30 tool calls** (all `Bash`; no file was written into the repository, no git write operation was run, no subagent was dispatched). Wall clock approximately **14 minutes**, `HEAD 1c9d8278` → `HEAD 5ae0fa04`, ending `2026-09-08T03:43:04Z`. Under both the ~40-call and ~40-minute targets.

## Next concrete action

**One successor, inside this lane:** run the I2b experiment against `systems/systems_check.py` — empty the fifteen `systems/graph/` collections, run `--write-views`, then `--check` — in a scratch copy whose `systems_check` baseline is first established as rc=0 (which requires either a `.git`-bearing copy or an accounting of the 179 pre-existing link errors). That single result decides whether the largest gate in the repository behaves like `emc_systems_map_check` (green over zero objects once the view is regenerated in the same commit) or is genuinely protected, and it is the one row in my census I could not settle by execution.

A second, cheaper item that belongs to whoever owns `systems_check`, not to this lane: **`systems_check --check` returned rc=1 with 179 errors in my scratch copy of the working tree**, sampled as broken relative links inside `research/autonomy/opus-capacity-campaign-20260908/inputs/`. If that reproduces in the live checkout, the campaign's own input material is reddening a preflight gate. I did not run it live and it is UNKNOWN.
