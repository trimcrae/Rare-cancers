<!-- collected 2026-09-08T03:34:17Z by campaign coordinator; agent id a2a55b3b49d810ea4; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a2a55b3b49d810ea4.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

**W29b** — preflight-row reachability lane, OPUS-CAPACITY-CAMPAIGN-20260908. Named successor to W29.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). Nothing in this container's environment names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start**: `Tue Sep  8 03:25:49 UTC 2026` · **end**: `Tue Sep  8 03:29:40 UTC 2026`

`git rev-parse HEAD` **start**: `ff6bb018936451d0c2d60fb4a2aa7ae8ba932d7f` · **end**: `215ed8e78f83d1e5acdbb726317dfd0eeed8f6a1`. HEAD moved under me (the coordinator collecting sibling reports). Every file I measured — `scripts/preflight.sh`, the five modules, `single_slot_identity.py`, `systems/parser_guard.py`, the eight dependency data files — was read at the live checkout and every finding is anchored to `file:line` plus quoted content, so a report-only commit between the two HEADs does not touch my inputs. Neither HEAD is the brief's frozen `92abbcb9`.

`git status --porcelain` **start**: empty. **end**: empty. I wrote nothing into `/home/user/Rare-cancers` and ran no git write operation. All execution under `/tmp/claude-0/w29b/` with `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/w29b/pyc`.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (end-of-run; identical in content to the start capture. The five long proxy-list variables `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy` and `JAVA_TOOL_OPTIONS` are filtered out of the paste below and appear verbatim in the start capture in the transcript; they contain no model information):

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

W29 left **REACHABILITY-IN-PRACTICE as UNKNOWN, not zero** for the five vacuous-pass rows of the re-derivation gate (`scripts/preflight.sh:847-864`, rows 3, 11, 16, 17, 18). Three questions, all open:

1. For each of the five, **how could the degenerate state actually arise on a real branch?** Is the file the row depends on generated or hand-written; committed or gitignored; produced by a workflow or optional by design; what writes it; and could a plausible commit, merge, partial checkout or failed generator leave it empty or absent while everything else stays green?
2. **Row 3's vacuous path was never executed** — W29 derived it from source only. Construct the degenerate input and record the real exit code.
3. For the three rows that already print a denominator (`0 ERROR across N trigger(s)`; `N record(s), M destination(s)`; `N queued item(s)`), **could that denominator be compared against a committed floor** the way `single_slot_identity.py` is said to do for its registry — and **precisely what shape does that precedent's refusal actually take?**

Open because W29's own Limitations section names (1) and (2) explicitly, and because its Next-action framing of (3) asserts a precedent whose shape nobody has read.

## Prior-work check

Read in full as instructed: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `reports/W29-preflight-row-provenance.md`. `reports/W13g-cross-file-gate-hole.md` and `reports/W27-drift-gate-hash-census.md` were read at their heads (worker/model/HEAD sections) to establish adjacency and non-overlap, not end to end.

Non-duplication, checked rather than assumed:

- **W29** classified what each of the 18 `--check` bodies asserts. It did **not** measure how any degenerate state arises, did **not** run row 3, and did **not** read `single_slot_identity.py`'s refusal shape. My unit is exactly those three gaps and touches no new row.
- **W27** (concurrent) is the drift-gate hash census; **W27b** (concurrent sibling, named in my dispatch) is resolving module `--check` classes. I read no drift-gate key list and classified no additional module. My three questions are all *downstream* of the classification W27b is redoing.
- **W13g** measures cross-file `pool`-flag enforcement over registry consumers (`scripts/validate-registry.mjs`, preflight gate 10). I touch no registry pooling and no clinical artifact.

Commands run for provenance, with what they showed:

- `git ls-files --error-unmatch <path>` / `git check-ignore -q <path>` over the eight dependency files → all **tracked**, **none ignored** (table in R1).
- `grep -rn -E "news-match-queue|citation-debt\.json|method-watch-triggers|emc-systems-map\.json" --include=*.py --include=*.sh --include=*.mjs --include=*.yml .` → the writer inventory in R1.
- `grep -rn -E "trigger_scan|citation_debt|news_match|submission_citations|aso_deposit_drift" .github/workflows/` → only three workflow references (R1).
- `grep -rn -E "measured nothing|EMPTY —|at least [0-9]+ |MIN_COUNT|floor" --include=*.py scripts/ research/modalities/ research/manuscripts/ systems/` → the floor-precedent inventory in R4.

CLOSED-WORK items confirmed not replayed: no PUB-EMC-CLASSIFICATION, no Brenca/Hofvander/Davis, no `GSE4303`/`GSE28866`, no NR4A Perspective, no source fetch, no clinical claim. **No network was attempted at all** — W29 established that zero of the 18 `--check` paths issue HTTP, so I issued none and have no denial to record.

## Method and inputs

| Input | Path | Role |
|---|---|---|
| The gate | `/home/user/Rare-cancers/scripts/preflight.sh:847-864` | the 18 row literals — **confirmed independently**, see R0 |
| Five modules | `submission_citations.py`, `aso_deposit_drift.py`, `trigger_scan.py`, `citation_debt.py`, `news_match.py` | rows 3, 11, 16, 17, 18 |
| Precedent | `research/modalities/single_slot_identity.py:405-423` | the refusal shape (row 14) |
| Compensating guard | `systems/parser_guard.py:172-200` | existence coverage for two of the dependency files |
| Workflows | `.github/workflows/tests.yml`, `method-watch.yml`, `method-watch-triggers.yml` | which rows run in CI and under what checkout |
| Incident record | `research/modalities/tests/test_publish_regen_failure_fails_the_step.py:1-14` | a **documented, real** failed-generator-with-green-job event |
| Scratch tree | `/tmp/claude-0/w29b/tree` (399 MB) | `tar --exclude=./.git` of `research/{manuscripts,literature,data,modalities}`, `scripts`, `systems` — the only place any degenerate input was created |

System `python3`. `scripts/preflight.sh` was **not run**. Row 13 (`atr_hrd_sarcoma_series.py`) was **never invoked**, in the live tree or on scratch, because W29 established it writes its artifact during `--check` when absent. No paid API, no GPU, no publication, no network.

**A disk-capacity note, because it changed my method.** My first attempt to `tar` the whole tree failed with `No space left on device` (`/dev/vda` at 99%, 606 MB free) — nine sibling workers' scratch trees were resident. I removed my partial copy, waited for siblings to release (22 GB free at second attempt) and copied only the six subtrees I needed. This is why my scratch tree is 399 MB rather than W29's 611 MB.

## Result

### R0 — The line citation, independently confirmed (`PRIMARY`)

`sed -n '847,864p' scripts/preflight.sh` returns exactly the 18 `"<module>|<label>|--check"` literals, opening with `for g in "research/manuscripts/submission_tables.py|submission tables|--check" \` at 847 and closing with `"scripts/news_match.py|news-match queue|--check"; do` at 864. **W29's correction stands.** `845-866` and `849-866` are both wrong.

### R1 — Provenance of every dependency file behind the five rows (`PRIMARY`)

All eight are **tracked and none is gitignored** — measured, not assumed:

| Dependency file | Row | Tracked | Ignored | Bytes | Kind | What writes it |
|---|---|---|---|---|---|---|
| `research/manuscripts/aso/fusion-junction-aso-research-article.md` | 3 | YES | no | 245,142 | **hand-written manuscript** | humans; PUB-ASO is under active revision |
| `research/manuscripts/aso/deposit-state.json` | 11 | YES | no | 28,059 | hand/tool-maintained | `aso_deposit_drift.py --write` |
| `research/manuscripts/aso/fusion-junction-aso-archive-manifest.json` | 11 | YES | no | 382,546 | **generated** | `aso_archive_manifest.py` |
| `research/manuscripts/aso/fusion-junction-aso-preprint-checklist.md` | 11 | YES | no | 89,168 | **hand-written with a generated block** (`BEGIN/END GENERATED deposit-drift`) | `aso_deposit_drift.py --write` splices the block |
| `research/method-watch-triggers.json` | 16, 17 | YES | no | 126,228 | **hand-written** — the module says so: *"Nothing here is a generated artifact — each ERROR above is a hand-written field"* (`trigger_scan.py:916`) | humans only |
| `research/manuscripts/emc-systems-map.json` | 16 | YES | no | 332,797 | **hand-written**; only its `.md` **view** is generated (`emc_systems_map_check.py --write-view` writes `VIEW_PATH`, never `MAP_PATH`) | humans only |
| `research/literature/citation-debt.json` | 17 | YES | no | 11,205 | **hand-written** — `grep` for any write/dump/`git add` against this path across `*.py *.sh *.yml *.mjs` returns **zero hits**; `citation_debt.py` opens it read-only at line 56 and has no `--write` | humans only |
| `research/literature/news-match-queue.json` | 18 | YES | no | 34,650 | **machine-written, wholesale-overwritten** | `news_match.py --ingest` (`scripts/news_match.py:416-418`) |

Denominators at HEAD, measured: `triggers = 39`, `rows = 4`, `items = 47` — matching the three success messages W29 recorded.

### R2 — Reachability-in-practice, settled per row (`PRIMARY` unless marked)

W29's "UNKNOWN, not zero" resolves to **three different answers**, not one. The five rows are not a uniform population.

| Row | Degenerate state | Reachable how, on a real branch | Verdict |
|---|---|---|---|
| **18** `news_match.py` | `items: []` | **REACHABLE BY DESIGN, no bad commit required.** The queue is not hand-maintained — the module's own failure text calls it *"a committed product of a model run"*. `--ingest` rebuilds it wholesale from `load_items()`, which reuses `email_digest.treatment_headlines` to parse the weekly digest. A week with no parsed headlines (feed outage, digest-format change, a parser edit) yields `rows = []`, writes `items: []`, and `check()` prints `0 ERROR across 0 queued item(s)` → **rc 0**. Nothing in the pipeline distinguishes "a quiet week" from "the parser stopped seeing items". | **REACHABLE — routine operation** |
| **18** (variant) | file absent | `if not os.path.exists(QUEUE): … return 0` is **optional-by-design at bootstrap** — its message is *"no queue committed yet"*. On a real branch, absence needs a deletion commit. **No other guard covers it**: `parser_guard.check_registry`'s list does not include this path, and `grep` finds no existence check anywhere. | reachable only by deletion; **uncovered elsewhere** |
| **17** `citation_debt.py` | `rows: []` | **REACHABLE ONLY BY HAND.** The ledger has no writer anywhere in the repository. Emptying it is a human edit, in a 4-row file, and 4 is small enough that a merge resolving to "keep theirs" on a conflicted ledger is credible. Separately and more cheaply: `if trg and trigger_ids and trg not in trigger_ids` silently disables the trigger-pointer join whenever `method-watch-triggers.json` is unreadable — that is a **partial** vacuity needing no ledger change at all. | **REACHABLE — hand edit or merge**; partial vacuity cheaper |
| **16** `trigger_scan.py` — registry absent | `return 0` skip | Registry absence **is caught elsewhere**: `systems/parser_guard.py:189-197` fails on a missing `research/manuscripts/emc-systems-map.json`, and preflight runs `parser_guard` at `scripts/preflight.sh:716`. Same for `method-watch-triggers.json` (`check_scan_triggers`, line 172-179). So the skip is real in the row but **the tree as a whole is not blind to it**. | **COMPENSATED** — a genuine correction to W29 |
| **16** `trigger_scan.py` — `triggers: []` | `0 ERROR across 0 trigger(s)` | **NOT compensated.** `parser_guard.check_scan_triggers` iterates `d.get("triggers", [])` with no floor — an empty list passes it too. Both guards go green on an emptied-but-present config. Reachable by hand edit or a merge that drops the array. | **REACHABLE — uncovered by either guard** |
| **11** `aso_deposit_drift.py` | committed block is the UNKNOWN block | Requires someone to run `--write` where the published rev is unresolvable, then commit. That is exactly what a **shallow checkout** produces, and `actions/checkout@v4`'s default is depth-1 — 18 workflow steps in this repo set `fetch-depth: 0` explicitly *because* they need history, which is direct evidence the shallow default is the norm elsewhere. The repository already suffered the general form of this: `test_publish_regen_failure_fails_the_step.py` records `method-watch-triggers.yml` running `PUBLISH_REGEN` without `pyyaml`, soft-failing, reporting **SUCCESS**, and leaving drift that a human hand-repaired **three times**. | **REACHABLE — and the failure mode has a documented precedent in this repo** |
| **3** `submission_citations.py` | `cites` empty | **NOT REACHABLE — refuted by execution.** See R3. | **REFUTED** |
| **3** (the real one) | fetched-metadata half | **ALREADY PRESENT AT LIVE HEAD.** See R3. | **REACHABLE — currently active** |

### R3 — Row 3: W29's claim is wrong, and the real defect is a different one (`PRIMARY`, executed)

W29 stated row 3's vacuous path as *"`--check` only iterates `cites` and `bare`; both empty → 'citation numbering is current', rc 0"*. **This is not what the code does.** `main()` guards *before* the `--check` dispatch (`submission_citations.py:377-379`):

```python
if not cites:
    print("no annotated citations found — nothing to resolve", file=sys.stderr)
    return 2
```

The `--check` branch is at line 460, thirty lines downstream. An emptied manuscript never reaches it.

**Executed on `/tmp/claude-0/w29b/tree`.** Baseline first, then every annotated superscript and every bare superscript stripped from the manuscript:

```
BASELINE: 74 annotated citation(s), 53 distinct PMID(s), 0 UNANNOTATED superscript(s), 0 without fetched metadata
          citation numbering is current                                    rc=0
D-A:      annotated remaining: 0   bare remaining: 0
          no annotated citations found — nothing to resolve                rc=2
```

**rc = 2. The gate goes red.** Row 3 is *not* vacuous on an emptied input, and the vacuous-pass count is **4 of 18 (22 %), not 5 of 18 (28 %)**.

**What row 3 actually has is a floor-of-one, not a floor-of-zero.** Reduced to exactly one annotated citation:

```
D-B:      1 annotated citation(s), 1 distinct PMID(s), 0 UNANNOTATED superscript(s), 0 without fetched metadata
            ⛔ cited only in the SI, so absent from the numbered list: ['12378528', '24981949', '29937513',
               '36103645', '39126066', '41614678', '7545436']
            citation numbering is current                                  rc=0
```

**rc = 0 on a single comparison, with seven SI-only PMIDs printed and not gated.** The gate cannot tell 74 comparisons from 1.

**And one degenerate state is live right now, at HEAD.** `_literature_cache()` (line 303-306) shells out and never inspects the return code:

```
$ git ls-tree -r --name-only origin/literature-cache
fatal: Not a valid object name origin/literature-cache
rc=128
```

`refs/heads/literature-cache` exists locally (`216bd1b5fb25…`); the **remote-tracking** ref `origin/literature-cache` does not. `r.stdout` is empty, the `for path in …` loop body never executes, `out` is `{}`. The last-resort metadata source contributes **zero records on this checkout** and says nothing. The module's own comment at line 167 already names this — *"that branch is not present in a CI checkout"* — and `tests.yml:222` runs this row in CI under the default checkout. **This is a silent degrade that is currently active, not a hypothetical.** In fairness it currently costs nothing: baseline reports `0 without fetched metadata`, because the 2026-08-17 commit moved those records into `lit-targets-aso-bibliography-completion.json` precisely so they would travel with the repository. The hole is real; its consequence today is zero.

### R4 — The floor precedent: `single_slot_identity.py` is not the precedent it was taken to be (`PRIMARY`)

Its refusal, read at `research/modalities/single_slot_identity.py:412-416`:

```python
if not slots:
    # ⛔ AN EMPTY REGISTRY IS NOT A PASS. A gate that reports OK while measuring nothing is the
    # defect this repository keeps paying for; say it, and fail.
    print("REGISTRY EMPTY — this guard measured nothing", file=sys.stderr)
    return 1
```

**Its precise shape, stated exactly:**

1. **A zero-test, not a floor comparison.** The predicate is `not slots` — emptiness. There is no committed number, no expected count, nothing to drift against. It catches 0 and passes 1.
2. **Over an in-source Python literal, not committed data.** `SLOTS` is a module-level list literal at line 92. Measured: `len(SLOTS) == 1`, ids `['ART-ATR-HRD-SERIES']`. It is a **one-entry** registry that can only empty if someone edits the module — which is why a zero-test suffices there.
3. **Positioned before the loop, after filtering** (`slots = [s for s in SLOTS if args.slot in (None, s["id"])]`), with a separate `return 2` for an unknown `--slot`.
4. **rc 1, to stderr, naming the guard's own failure** rather than the data's.

**Therefore the answer to the dispatch's third question is a qualified no.** Rows 16, 17 and 18 read their collections from **committed JSON data files** that a commit, merge or generator can shrink without touching any source. A transplant of this precedent gives them a zero-test only: it would catch `triggers: []`, `rows: []`, `items: []` — the exact states R2 finds reachable — and would **not** catch 47 → 3, which is the decay a *floor* is for. Calling it "the pattern for comparing a denominator against a committed floor" overstates it in both directions.

**The genuine committed-floor precedents are elsewhere in the repository**, and the gate's owner should be pointed at them instead:

| Precedent | Shape | Fit for rows 16/17/18 |
|---|---|---|
| `scripts/lit_consensus_probe.py:172-173` — `CONTROL_PMID = "1902986"`, `CONTROL_FLOOR = 50` | A **control probe with a hard-coded floor**, deliberately set *"far below its true count; this tests plumbing, not popularity"*, failing `return 2` with `::error::` when the control returns at or below it. Its comment names the exact failure class: *"0 reads as 'nobody cites this paper' … CLAUDE.md §4's absent-reading-as-absence failure with the sign flipped, so it gets a control rather than a comment."* | **Best fit.** Same failure class, and the "far below true" calibration is what keeps a floor from becoming a maintenance tax. |
| `scripts/lit_query_assert.py:54` — `min_records = int(os.environ.get("LIT_MIN_RECORDS", "1") or 1)`, then `if n < min_records` | An **env-overridable minimum with a default of 1**. | Partial fit; an env-overridable floor is weaker than a committed one, since the override travels with the caller. |

**No test asserts any of the three counts.** `grep` over `research/modalities/tests`, `systems/tests` and `scripts/tests` for `len(triggers|rows|items)` and the three message fragments returns no assertion against these collections. So there is currently **no** committed record anywhere of how many triggers, ledger rows or queued items *should* exist. A floor would be the first.

**I authored no check, no diff and no repair.** No guard was weakened, relaxed or reordered.

## Validation evidence

Environment for every run: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, system `python3`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w29b/pyc`. No network of any kind was attempted. `scripts/preflight.sh` not run. Row 13 never invoked.

**RUN — row 3, cwd `/tmp/claude-0/w29b/tree`**, verbatim:

```
$ python3 research/manuscripts/submission_citations.py --check          # baseline
74 annotated citation(s), 53 distinct PMID(s), 0 UNANNOTATED superscript(s), 0 without fetched metadata
  citation numbering is current
rc=0

$ # all <sup>N</sup><!-- PMID: … --> and all bare <sup> removed from the manuscript
$ python3 research/manuscripts/submission_citations.py --check
no annotated citations found — nothing to resolve
rc=2

$ # manuscript reduced to exactly ONE annotated citation, renumbered to 1
$ python3 research/manuscripts/submission_citations.py --check
1 annotated citation(s), 1 distinct PMID(s), 0 UNANNOTATED superscript(s), 0 without fetched metadata
  ⛔ cited only in the SI, so absent from the numbered list: ['12378528', '24981949', '29937513', '36103645', '39126066', '41614678', '7545436']
  citation numbering is current
rc=0
```

The scratch manuscript was restored from `/tmp/claude-0/w29b/paper.orig.md` after each mutation. The live manuscript was never modified.

**RUN — live tree, read-only git query** (`cd /home/user/Rare-cancers`):

```
$ git ls-tree -r --name-only origin/literature-cache
fatal: Not a valid object name origin/literature-cache
rc=128
$ git rev-parse --verify origin/literature-cache
fatal: Needed a single revision
$ git branch -a --list '*literature-cache*'
216bd1b5fb25a56b90ef3cc2373e1fe68322708f	refs/heads/literature-cache
```

**RUN — provenance, live tree, read-only:** the tracked/ignored/bytes table in R1 from `git ls-files --error-unmatch` + `git check-ignore -q` + `stat -c%s` over the eight paths; the denominators from `python3 -c` loading the three JSON files (`39`, `4`, `47`); `len(SLOTS) == 1` from importing `single_slot_identity` and printing `len(s.SLOTS)` and the id list.

**Tree integrity:** `git status --porcelain` empty at start and end; no git write operation issued.

**PROPOSED (NOT RUN):**
- Row 11's shallow-clone reachability argument is **source- and configuration-derived**. I did not create a shallow clone and run `--write` in it, because that would require the `.git` store my scratch copy deliberately excludes.
- Row 16's `triggers: []` and row 17's `rows: []` reachability is **provenance-derived**; W29 already demonstrated both exit codes (D5b, D2), so I did not re-run them.
- Row 18's empty-digest path is derived from `load_items`/`build_queue`/`check` source. I did not run `--ingest` with an empty answer.
- I did not run `parser_guard.py` to confirm it reddens on a removed registry; the coverage claim is read from `systems/parser_guard.py:189-197` plus `scripts/preflight.sh:716`.

## Limitations

- **The vacuous-pass count changes from 5/18 to 4/18 on the strength of one executed refutation.** That is a correction to a sibling report, and it rests on D-A's `rc=2` plus the source guard at line 377-379. The other four remain as W29 demonstrated them.
- **Reachability is an argument from provenance, not an observed incident** for rows 11, 16, 17 and 18. I found one *documented* incident of the general class (`test_publish_regen_failure_fails_the_step.py`) but no recorded instance of any of these five specific rows passing vacuously on a real branch. Absence of such a record is UNKNOWN, not zero — the repository does not keep a log that would show it.
- **`parser_guard` compensation is a code reading, not a run.** I did not execute it against a removed registry.
- **My scratch tree omits `.git` and four subtrees** (`results/`, `.github/`, `research/autonomy/`, `research/compute/`), so any row whose behaviour depends on those was reasoned about in source only.
- **Row 3's live `origin/literature-cache` degrade currently costs nothing** — baseline reports `0 without fetched metadata`. I am claiming a silent-degrade mechanism, not present harm.
- **This says nothing about the gate as a whole.** I did not run `scripts/preflight.sh`, and I measured five of eighteen rows.
- No repair, diff or check was authored, proposed as code, or applied. No guard weakened or reordered. No clinical claim; there is no wet lab, and none of this bears on EMC efficacy, safety or readiness.

## Stop condition

**Set at the outset:** return as soon as (a) every one of the five rows has a provenance answer grounded in `git ls-files`/`check-ignore` plus an identified writer, (b) row 3's degenerate input has been constructed and its **real** exit code recorded, and (c) `single_slot_identity.py`'s refusal has been read and its shape stated precisely enough to say whether it transfers to rows 16/17/18.

**MET on all three.** (a) eight dependency files classified, all tracked, none ignored, writers identified — including the finding that `citation-debt.json` has *no* writer and that `emc-systems-map.json`'s generator writes only its view; (b) `rc=2`, refuting the claimed vacuous path, plus `rc=0` at a denominator of 1, which is the real surface; (c) read at `single_slot_identity.py:412-416` — a zero-test over a **one-entry in-source literal**, not a committed floor, so it does **not** transfer; the transferable precedents are `lit_consensus_probe.py`'s `CONTROL_FLOOR` and `lit_query_assert.py`'s `LIT_MIN_RECORDS`.

## Tool-call and wall-clock count actually used

**19 tool calls**, **~4 minutes wall clock** (`date -u` 03:25:49Z → 03:29:40Z). Well inside the ~40/~40 target. One call was lost to a disk-full `tar` failure and one to cleaning it up.

## Next concrete action

**Hand the gate's owner a two-part change, scoped by what this measurement actually supports — and correct W29's Next-action line before it is acted on.**

1. **Rows 16, 17, 18 get a zero-test, not a floor.** The reachable states measured here are `triggers: []`, `rows: []`, `items: []` and a missing queue. A zero-test in the shape of `single_slot_identity.py:412-416` closes exactly those and is the honest scope. A *committed floor* (47 → 3) is a separate, larger change and should be argued separately, on `lit_consensus_probe.py`'s calibration principle — *"far below its true count; this tests plumbing, not popularity"* — not on `single_slot_identity.py`, which is a one-entry in-source registry and carries no floor at all.
2. **Row 3 gets its return code checked.** `_literature_cache()` at `submission_citations.py:303-306` ignores `rc=128` today, at live HEAD. The smallest correct repair is to inspect `r.returncode` and announce the degrade — the pattern `tests.yml:174-177` already uses and describes in its own words: *"a guard that announces its own weakening is the only kind worth having."* This needs no floor and no new policy.

Both belong to whoever owns the gate; neither is a read-only lane's work, because each ends in a change. **What should not go forward is row 3 on the vacuous-pass list** — it is refuted by execution, and the 5-of-18 figure should be restated as 4 of 18 wherever the campaign has propagated it.
