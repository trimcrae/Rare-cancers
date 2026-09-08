<!-- collected 2026-09-08T04:49:12Z by campaign coordinator; agent id a2cff550e4a9c9813; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a2cff550e4a9c9813.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

**W44** — preflight-row execution lane, OPUS-CAPACITY-CAMPAIGN-20260908. Successor to W29/W29b/W29c/W29e/W29g.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). Nothing in the container names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start** `Tue Sep  8 04:39:29 UTC 2026` · **end** `Tue Sep  8 04:44:38 UTC 2026`.
`git rev-parse HEAD` **start** `408b676aec3625a36917755662516232a27a1278` · **end** `fb1a3f8040537234010114053b36ec55b729c65e`. HEAD advanced under me while the coordinator collected sibling reports. **Verified, not assumed:** `git diff --name-only 408b676a fb1a3f80 | grep -v 'opus-capacity-campaign-20260908' | wc -l` → **0** — nothing outside the campaign directory changed, so every module, every input file and `scripts/preflight.sh` are byte-identical to what I measured. `git status --porcelain` on the live tree: empty at start (3 untracked campaign reports appeared mid-run, coordinator-written) and **0 lines** at end.

I wrote nothing into `/home/user/Rare-cancers` and issued no git write operation (only `rev-parse`, `status`, `diff --name-only`). All execution under `/tmp/claude-0/w44/`, **deleted before returning** (`ls -d` → `No such file or directory`; 19 G free).

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start capture; the five long proxy-list variables `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` carry no model information and are filtered here — they appear verbatim in the transcript):

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

For each of the eighteen `--check` rows at `scripts/preflight.sh:847-864`: **what is the minimum input set the row actually examines, measured rather than inferred — and can that set be EMPTY while the row still exits 0?**

Open because the existing census answered this for **five rows only**. W29 classified all eighteen bodies from source and asserted that *"the remaining 13 rows cannot pass on a degenerate input, and the reason is structural"* — an argument, never an execution. W29b executed row 3 and refuted W29's claim about it; W29c executed rows 11/16/17/18. Rows 1, 2, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15 have **never been run against an emptied input by anyone**, and one of the two claims that was tested by execution turned out to be wrong. That is exactly the situation where an argument should be replaced by a measurement.

## Prior-work check

Read in full as instructed: `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W29e-discarded-gate-output.md`. `reports/W29g-preflight-row13-and-producers-test.md` was **not present at dispatch and appeared mid-run** — I found it in my own scratch `git status` and read it by targeted extraction (`grep -n -iE "row 13|rc=|vacuous|written|artifact"` then the matched passages); it closes row 13's *output* census (rc=0, 175 bytes, artifact 165,740 B pre-existing so the `:1452` write branch is not taken) and does **not** touch zero-input behaviour. `W29-preflight-row-provenance.md`, `W29b-vacuous-path-reachability.md` and `W29c-degenerate-rows-re-execution.md` were read by targeted extraction (`grep -n -iE "vacuo|refut|row [0-9]+"` and the row tables in context).

Commands run and what they showed:
- `grep -n -iE "vacuo|^\| *[0-9]+ *\|" W29-preflight-row-provenance.md` → the 18-row source classification and the claim **5 of 18 vacuous** (rows 3, 11, 16, 17, 18), with the 13-row "structural" assertion at its line 146 carrying **no execution**.
- `grep -n -iE "vacuo|refut|row [0-9]+" W29b-vacuous-path-reachability.md` → row 3 **REFUTED by execution** (rc=2), count corrected to 4 of 18; and its own limitation line 276 recording that it did not re-run 16/17.
- `sed -n '830,880p' scripts/preflight.sh` → the row list at `:847-864` verbatim, independently confirming the 1-based row indices.

W25 was not read, referenced, extended or audited (HELD and EXCLUDED). `scripts/preflight.sh` was **not run and not edited**. `atr_hrd_sarcoma_series.py` was **never invoked without `--check`**.

Non-duplication: W29 read all 18 from source; W29b executed row 3; W29c executed 11/16/17/18; W29e ran all 17 runnable rows at the **unmutated** tree; W29g ran row 13 unmutated. **Nobody executed any row against an emptied input except for rows 3, 11, 16, 17, 18.** I execute the zero-input case for **all eighteen**, and I derive each row's input set by runtime audit rather than by reading constants.

No CLOSED-WORK item replayed: no PUB-ASO edit, no Brenca/Hofvander/Davis, no `GSE4303`/`GSE28866`, no NR4A Perspective, no source fetch, no clinical claim. **No network was attempted at all**, so I have no denial to record. No paid API, no GPU, no publication, no human contacted. No content-policy refusal occurred.

## Method and inputs

**Write isolation.** `cp -a /home/user/Rare-cancers /tmp/claude-0/w44/tree` including `.git` (981 MB total), so modules resolve revisions as they do live. Scratch `git rev-parse HEAD` = `408b676a`; scratch `git status --porcelain` (tracked) = **0** at start and **0** after every experiment. Every mutation was byte-backed-up and byte-restored.

**Write-freedom confirmed from source BEFORE running**, per dispatch. For each of the twelve modules I had not already seen audited, `grep -nE '"--check|open\([^)]*"w|\.write_text|os\.replace|shutil\.(copy|move)|makedirs'` shows the `--check` dispatch strictly preceding every write site: `submission_tables.py` 3172 vs 3193; `claim_coverage.py` 806 vs 861; `submission_metrics.py` 605 vs 628; `aso_sequence_manifest.py` 1164 vs 1194; `aso_journal_tables.py` 343 vs 353; `aso_offtarget_duplex_energy.py` 345 vs 372; `submission_packet.py` 553 vs 563; `vaccine_path_tables.py` 237 vs 243; `aso_archive_manifest.py` 1932/1957 vs 1974; `emc_condensate_report.py` 333 vs 343; `instrument_census.py` 314 vs 331; `single_slot_identity.py` has **no write primitive at all**. For **row 13** I read `atr_hrd_sarcoma_series.py:1452-1455` first and confirmed the one conditional write is `if not os.path.exists(art_path)`; I verified the artifact present (165,740 B) before and after (unchanged), so that branch was not taken, and I never ran it without `--check`.

**How the minimum input set was measured (this is the methodological addition).** Instead of reading path constants, I installed a `sys.addaudithook` `sitecustomize.py` on `PYTHONPATH` that logs every `open` event resolving inside the scratch tree, and ran all seventeen policy-runnable rows once, unmutated, at `408b676a`. Every row exited **0** (green baseline). The per-row file lists are the **observed** minimum input set. Row 13's set was taken from its source constants (`ART, INPUTS, QUANT_INPUTS = paths_for(SERIES)`, `:105`) rather than the audit run.

**Zero-input construction.** For each row: take its audited file set, subtract the module `.py`/`.pyc` files and the artifact the row compares against (its `OUT`), then reduce every remaining file to a **well-formed empty collection** — a JSON file becomes `{}` or `[]` matching its own top-level type, a `.md`/`.csv`/`.fasta` becomes zero bytes. This tests *zero records*, not *corrupt file*. Four rows got a purpose-shaped variant instead: row 2 (its census population is a directory — `os.listdir(TESTS)` at `claim_coverage.py:537` — so I deleted the 115 files under `research/manuscripts/tests/`), row 14 (its registry is an in-source literal, so `SLOTS = []`), rows 16/17/18 (their collections are named JSON arrays, so `triggers`/`rows`/`items` → `[]`, plus a file-**removed** variant). Row 11's vacuous path requires a git-unresolvable published revision and a committed UNKNOWN block; I did **not** reconstruct it and report W29c's execution as the evidence, adding only the emptied-inputs variant.

Environment for every run: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, `/usr/local/bin/python3` (3.11), `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w44/pyc`, cwd `/tmp/claude-0/w44/tree`. No network attempted.

## Result

### R1 — The eighteen rows at zero inputs (`PRIMARY`; every verdict below except rows 11-vacuous is a run I performed)

Baseline first: all seventeen policy-runnable rows exit **0** at `408b676a` unmutated, so every non-zero below is a *change of input producing a change of verdict*, not a pre-broken tree.

| # | Module (`--check` unless noted) | Minimum input set examined (audited at runtime) | Zero-input behaviour | Evidence |
|---|---|---|---|---|
| 1 | `submission_tables.py` | 160 files: ~144 `research/modalities/*.json` + `aso/` artifacts (compares `…-submission-tables.md`) | **REFUSES** rc=**2** | 144 inputs emptied → `a required artifact is missing` |
| 2 | `claim_coverage.py` | 145 files: 115 guard tests under `research/manuscripts/tests/` + the censused papers (compares `claim-coverage.json`) | **REFUSES** rc=**1** | tests dir emptied → `claim-coverage.json is stale …  covered: committed 106, the census now reports 9` |
| 3 | `submission_citations.py` | 12 files: the research article + SI + 8 reference/target JSONs | **REFUSES** rc=**2** | 11 inputs emptied → `no annotated citations found — nothing to resolve`. Independently reproduces W29b's refutation of W29 |
| 4 | `submission_metrics.py` | 11 files: 7 manuscript `.md` (compares `submission-metrics.json`) | **REFUSES** rc=**1** | manuscripts emptied → per-doc lines read `main= 0w … within believed limits`, byte compare still fails |
| 5 | `aso_sequence_manifest.py` | 23 files: 16 `research/modalities/aso-*.json` + 4 deposit docs (compares CSV+FASTA) | **CRASHES** rc=**1** | `KeyError: 'junctions'` |
| 6 | `aso_journal_tables.py` | 4 files: `…-sequences.csv`, `aso-control-oligos.json` (compares `…-journal-tables.md`) | **REFUSES** rc=**1** | `EWSR1_e12__NR4A3_e3: expected one lead at 5-6-5, found 0` |
| 7 | `aso_offtarget_duplex_energy.py` | 99 files: ~93 `junction-aso-offtarget-*.json` (compares `aso-offtarget-duplex-energy.json`) | **CRASHES** rc=**1**, loudly and on-topic | `aso_screen_sets.GeometryError: no blast_screen artifact in modalities was produced at Geometry(16-mer 5-6-5) (present: none). Loading nothing and repo…` |
| 8 | `submission_packet.py` | 18 files: globbed `aso/…*article*.md`, venue JSONs, figure manifest (compares `SUBMISSION-PACKET.md`) | **REFUSES** rc=**1** | `STALE research/manuscripts/SUBMISSION-PACKET.md — rerun without --check and commit the result` |
| 9 | `vaccine_path_tables.py` | 6 files: `hla-coverage.json`, `epitope-allele-matrix.json`, `coverage-threshold-curve.json`, `fusion-breakpoint-neoantigens.json` (splices into the manuscript) | **CRASHES** rc=**1** | `KeyError: 'regions'` |
| 10 | `aso_archive_manifest.py --check-archive` | **520 files** — every file the `PROMISES` globs resolve to (compares the manifest) | **REFUSES** rc=**1** | 439 emptied → `STALE: the archive inventory would change — re-run without --check` |
| 11 | `aso_deposit_drift.py` | 4 files: `deposit-state.json`, archive manifest, preprint checklist + `git show <rev>:<manifest>` | **VACUOUS PASS** rc=**0** *in its announced-UNKNOWN state* (W29c, not re-derived by me). With its two JSON inputs emptied: **CRASHES** rc=1 | W29c D6/R1: `--check` rc=0, zero bytes of output, when the committed block is the "drift cannot be measured here … UNKNOWN" block. My variant: traceback, rc=1 |
| 12 | `emc_condensate_report.py` | 7 files: 5 `emc-condensate-*.json` (compares the findings note) | **CRASHES** rc=**1** | `KeyError: 'constructs'` |
| 13 | `atr_hrd_sarcoma_series.py` | 3 files: artifact + `atr-hrd-sarcoma-series-inputs.json` + quant-inputs cache | **REFUSES** rc=**1** — *first zero-input measurement of this row* | cache → `{}`, artifact left in place: `IDENTITY UNBOUND — ART-ATR-HRD-SERIES does not hold GSE299349 / C/cache: … has no 'series' field` then `DRIFT — the derive half no longer reproduces the committed artifact`. Artifact byte size unchanged (165,740) — the `:1452` write branch not taken |
| 14 | `single_slot_identity.py` | 750 files, driven by an **in-source** `SLOTS` registry | **REFUSES** rc=**1**, by design and by name | `SLOTS = []` → `REGISTRY EMPTY — this guard measured nothing`. The only row that states the failure mode in its own words (`:411-414`) |
| 15 | `instrument_census.py` | 4 files: `nr4a3-program-map.md` is the sole input (compares census `.json`+`.md`) | **REFUSES** rc=**1** | `instrument_census: the roadmap table starting '\| id \| instrument \| known-answer test \| result \|' is gone. Relocate this parser rather than letting the census silently empty.` |
| 16 | `trigger_scan.py` | 5 files: `method-watch-triggers.json`, `emc-systems-map.json`, `systems/graph/{routes,blockers}.json` | **VACUOUS PASS** rc=**0** ×2 | `triggers: []` (39→0) → rc=0, `0 ERROR across 0 trigger(s)`. Registry **removed** → rc=0, `registry not found … — skipping cross-check`. (Triggers file **removed** → rc=1 `FileNotFoundError`.) |
| 17 | `citation_debt.py` | 6 files: `citation-debt.json` + the destinations it names | **VACUOUS PASS** rc=**0** | `rows: []` (4→0) → rc=0, `citation debt: 0 record(s), 0 destination(s)` + `every declared destination is decided and every discharge verified`. (Ledger **removed** → rc=1 `FileNotFoundError`.) |
| 18 | `news_match.py` | 3 files: `news-match-queue.json`, `systems/graph/publications.json` | **VACUOUS PASS** rc=**0** ×2 | `items: []` (47→0) → rc=0, `0 ERROR across 0 queued item(s)`. Queue **removed** → rc=0, `no queue committed yet — nothing to validate` |

### R2 — The count, and the correction it makes to the campaign's own figure (`PRIMARY`)

**Four of eighteen rows can pass over an empty input collection: rows 11, 16, 17, 18.** That number is unchanged from W29b/W29c — but it was previously **4 measured out of 5 examined**, resting for the other thirteen on W29's structural argument. It is now **4 out of 18 examined, seventeen of them by execution**. Rows 1-10, 12-15 are refuted as vacuous *by measurement*, including the three (13, 14, 15) no prior worker mutated at all.

**W29's structural explanation survives its own test, with one correction.** Its claim was that the vacuous surface tracks a row's *kind*: rows that re-derive an artifact and byte-compare go red when the input empties, rows that merely validate hand-written data do not. Every one of the fourteen re-derivation rows did go non-zero. But the mechanism splits into three, and only the first is the one W29 described:

- **7 rows REFUSE with a purpose-built message** (1, 2, 6, 8, 10, 15, plus 3 at rc=2 and 14 at rc=1 — 9 counting those). Rows 15 and 14 are the strongest: each names the emptiness in the sentence it prints (`rather than letting the census silently empty`; `REGISTRY EMPTY — this guard measured nothing`).
- **4 rows CRASH with an uncaught exception** (5, 9, 12 → `KeyError`; 7 → a domain-specific `GeometryError` whose text does name the empty screen set). The gate goes red, which is the right verdict, but by the wrong mechanism — and the operator gets `STALE <label> -- rerun 'python3 <gen>' and commit the result`, which is wrong advice for an empty input. This is the same defect shape W29c recorded for row 17's *removed* ledger, and I now find it in **four** more rows.
- **1 row (13) refuses through a different guard than its own comparison** — the `single_slot_identity` binding fires on the cache's missing `series` field before the derive-diff reports DRIFT.

**Is any vacuous row's collection near-empty in the committed tree?** Measured at live HEAD: `method-watch-triggers.json` → **39** triggers; `news-match-queue.json` → **47** items; `citation-debt.json` → **4** rows. **Row 17 is the near-empty one**: four records is the smallest live collection behind any vacuous row, and it is the one collection W29b found has **no writer anywhere in the tree** — it is hand-maintained, so it reaches zero by ordinary editing, not by a build failure. Row 11's committed block is currently the *measured* one (`⛔ **28 deposited paths differ** … against its own manifest at 4fd4698daec0`), **not** the UNKNOWN block, so row 11's vacuous path is not live at this HEAD. Rows 16 and 18 are far from empty. No vacuous row is currently passing vacuously; the exposure is proximity, and only row 17 is close.

**What this does not say.** Nothing here is a claim that any of the four rows is currently wrong, that any artifact is empty, or that the gate is failing today — all eighteen rows are green at `408b676a` with real data behind them. It is a claim about what the gate would **not notice**, now measured for every row rather than argued for thirteen. And per W29e/W29c, the gate's success branch (`preflight.sh:890-891`) prints only `   OK   <label>`, so a reader could not tell `0 ERROR across 0 trigger(s)` from `39` even when the row prints it.

**I authored no repair, no patch, no diff, no gate and no test. No guard was weakened, relaxed or reordered. `scripts/preflight.sh` was not run and not edited. Row 13 was never invoked without `--check`, and its write branch was never taken.**

## Validation evidence

**RUN.** Environment as in Method. Baseline, all seventeen policy-runnable rows in the untouched scratch copy:

```
row1 rc=0 … row12 rc=0
ROW 13 SKIPPED BY POLICY   (baseline audit run only; row 13 was run separately, --check, artifact present)
row14 rc=0 row15 rc=0 row16 rc=0 row17 rc=0 row18 rc=0
```

**RUN — zero-input sweep** (each row's audited inputs emptied, its compared artifact left committed, all files byte-restored after):

```
ROW 1  n_inputs_emptied=144 rc=2 | a required artifact is missing
ROW 3  n_inputs_emptied=11  rc=2 | no annotated citations found — nothing to resolve
ROW 4  n_inputs_emptied=7   rc=1 | … main= 0w abs=Nonew items= 0 refs= 0 within believed limits
ROW 5  n_inputs_emptied=20  rc=1 | KeyError: 'junctions'
ROW 6  n_inputs_emptied=2   rc=1 | EWSR1_e12__NR4A3_e3: expected one lead at 5-6-5, found 0
ROW 7  n_inputs_emptied=93  rc=1 | aso_screen_sets.GeometryError: no blast_screen artifact in modalities was produced at Geometry(16-mer 5-6-5) (present: none). Loading nothing and repo…
ROW 8  n_inputs_emptied=10  rc=1 | STALE research/manuscripts/SUBMISSION-PACKET.md — rerun without --check and commit the result
ROW 9  n_inputs_emptied=4   rc=1 | KeyError: 'regions'
ROW 10 n_inputs_emptied=439 rc=1 | STALE: the archive inventory would change — re-run without --check
ROW 12 n_inputs_emptied=5   rc=1 | KeyError: 'constructs'
ROW 15 n_inputs_emptied=1   rc=1 | instrument_census: the roadmap table starting '| id | instrument | known-answer test | result |' is gone. Relocate this parser rather than letting the census silently empty.
```

**RUN — the four special-shaped rows:**
```
$ find research/manuscripts/tests -type f -delete; python3 research/manuscripts/claim_coverage.py --check
claim-coverage.json is stale — it is not what the live census computes:
  papers.…fusion-junction-aso-journal-article.md.covered: committed 106, the census now reports 9
ROW2 rc=1                                  # 115 test files restored, verified
$ # SLOTS = []  in a scratch copy of the module
$ python3 research/modalities/single_slot_identity.py --check
REGISTRY EMPTY — this guard measured nothing
rc=1
$ # atr-hrd-sarcoma-series-inputs.json -> {} ; artifact present, size 165740
$ python3 research/modalities/atr_hrd_sarcoma_series.py --check
IDENTITY UNBOUND — ART-ATR-HRD-SERIES does not hold GSE299349
    C/cache: research/modalities/atr-hrd-sarcoma-series-inputs.json has no `series` field
DRIFT — the derive half no longer reproduces the committed artifact
  differs: assay_types
ROW13 rc=1 ; artifact size after: 165740
```

**RUN — rows 16/17/18, emptied array and removed file:**
```
ROW 16: research/method-watch-triggers.json triggers 39 -> 0 | rc=0 | trigger_scan --check: 0 ERROR across 0 trigger(s); 27 registry revival_trigger field(s) seen
ROW 17: research/literature/citation-debt.json rows 4 -> 0   | rc=0 | citation debt: 0 record(s), 0 destination(s)
ROW 18: research/literature/news-match-queue.json items 47->0 | rc=0 | news_match --check: 0 ERROR across 0 queued item(s); …
16-REMOVED triggers file: rc=1 | FileNotFoundError: … research/method-watch-triggers.json
16-REMOVED registry:      rc=0 | trigger_scan --check: registry not found at … — skipping cross-check
17-REMOVED ledger:        rc=1 | FileNotFoundError: … research/literature/citation-debt.json
18-REMOVED queue:         rc=0 | news_match --check: no queue committed yet — nothing to validate
ROW 11 (inputs emptied to {}): rc=1 | Traceback (most recent call last):
```

**RUN — write-freedom and live-tree integrity, after every experiment:**
```
$ cd /tmp/claude-0/w44/tree && git status --porcelain | grep -v '^??' | wc -l
0
$ diff -rq --exclude=.git /home/user/Rare-cancers /tmp/claude-0/w44/tree | grep -v '^Only in /home/user'
Files …/.pytest_cache/v/cache/nodeids and …/tree/.pytest_cache/v/cache/nodeids differ
Files …/COMMON-BRIEF.md and …/tree/…/COMMON-BRIEF.md differ
$ git diff --name-only 408b676a fb1a3f80 | grep -v 'opus-capacity-campaign-20260908' | wc -l
0
$ git status --porcelain | wc -l          # live tree, at end
0
$ rm -rf /tmp/claude-0/w44 && ls -d /tmp/claude-0/w44
ls: cannot access '/tmp/claude-0/w44': No such file or directory
```
Both `differ` lines are **live-side** changes made after my copy: `COMMON-BRIEF.md` gained 149 appended lines (a coordinator addition about W30d's registry audit — diffed and read; it changes nothing I measured), and `.pytest_cache/v/cache/nodeids` is a sibling's untracked pytest artifact. I never ran pytest. Fifteen `Only in /home/user` entries are new campaign reports. **No file I mutated differs**, and the live tree's tracked state is clean at both ends.

**PROPOSED (NOT RUN):**
- Row 11's vacuous state was **not re-derived by me** — it needs a git-unresolvable published revision plus the UNKNOWN block committed. I report W29c's rc=0 as its evidence and label it accordingly.
- I ran the rows **serially**, not concurrently as `preflight.sh:880` does, and I did not run `scripts/preflight.sh`. Concurrency changes timing, not exit codes.
- Row 13's `--fetch`/non-default-`--series` paths and its artifact-absent write branch are unexercised, by policy.
- I did not test every *partial* denominator (e.g. one record instead of zero). W29b's "floor-of-one" finding for row 3 remains the only measurement of that kind.

## Limitations

- **"Empty" means a well-formed zero-record collection**, not a corrupt or absent file; where the two diverge I ran both (rows 16/17/18) and the divergence is real — row 17 is vacuous on `rows: []` but crashes on a removed ledger, row 16 is vacuous on a removed registry but crashes on a removed trigger file. A single verdict per row would have been wrong.
- **REFUSES vs CRASHES is my classification**, applied by reading the output: a message the module wrote for this case versus an uncaught exception. Both go red, so the *gate's* verdict is identical; the distinction matters only for the operator's remedy text, which is `STALE … rerun and commit` in both cases and is wrong advice in the crash cases.
- **The counts (39, 47, 4, 520, 144) are this tree's values at `408b676a`** and move as the repository moves. The count of vacuous rows (4/18) is a property of the code and is stable until a module changes.
- **Row 1's rc=2 is at 144 files emptied simultaneously**; I did not isolate which single input triggers `a required artifact is missing`, so the *minimum* emptying that reddens row 1 is UNKNOWN — I measured that the full collection cannot be empty, not the smallest sufficient subset. The same applies to rows 2, 5, 7, 8, 10.
- The audited input sets are what each row opened **on this green tree**; a row could open more files on a different branch of its own logic. A file absent from a set is UNKNOWN-for-other-inputs, not proven unread.
- **No scientific claim of any kind is made here.** This is a measurement of shell and Python exit codes. It says nothing about EMC biology, efficacy, safety, selectivity or clinical readiness; there is no wet lab. A row exiting 0 or 1 is a statement about file staleness, never about whether any number in an artifact is scientifically correct.

## Stop condition

**Set at the outset:** return as soon as (a) every one of the eighteen rows has a minimum input set measured rather than inferred, (b) each row has a zero-input verdict of VACUOUS PASS / REFUSES / CRASHES backed by an exit code from a run I performed in an isolated copy — with write-freedom read from source *before* each run and confirmed by diff after — or, where policy forbids the run, by a named prior execution, and (c) the vacuous count is stated together with whether any vacuous row's collection is near-empty in the committed tree.

**MET on all three.** (a) seventeen sets audited at runtime by `sys.addaudithook`, row 13's from source. (b) seventeen rows executed at zero inputs with real exit codes; row 11's vacuous case attributed to W29c and its emptied-input variant run by me. (c) **4 of 18** — rows 11, 16, 17, 18 — with row 17 near-empty at 4 records and writer-less, and row 11's vacuous state not live at this HEAD.

## Tool-call and wall-clock count actually used

**16 tool calls**, **~5 minutes wall clock** (`date -u` 04:39:29Z → 04:44:38Z). Well inside the ~40/~40 target. Scratch deleted; 19 G free at exit.

## Next concrete action

**For whoever owns the gate — not this read-only lane, because it ends in a change:** the eighteen-row zero-input census is now closed, and it isolates the fix to **one row**. Rows 1-10 and 12-15 are structurally protected: emptying their input changes the recomputation, so the byte compare fails. Rows 16 and 18 are vacuous but their live collections are 39 and 47 and both have generators. **Row 17 is the single row where a vacuous pass is reachable by ordinary editing**: 4 records, no writer anywhere in the tree (W29b), no test pinning any row id (W29c's grep, which I did not re-run), and `rows: []` prints `every declared destination is decided and every discharge verified` — a sentence that is true and empty at the same time. The transferable precedent already exists in the eighteen: `single_slot_identity.py:411-414` refuses an empty registry by name, and I executed that refusal (rc=1). I am not proposing the edit, have written none, and have added no guard.

**The one measurement a successor should make and I did not:** for rows 1, 2, 5, 7, 8 and 10, the *minimum* subset whose emptying reddens the row. I proved the full collection cannot be empty; whether a single missing modality artifact out of 144 is caught, or only noticed because 143 others went with it, is unmeasured — and that, not the all-empty case, is the state a real branch produces. Roughly one scratch copy and a bisection per row.
