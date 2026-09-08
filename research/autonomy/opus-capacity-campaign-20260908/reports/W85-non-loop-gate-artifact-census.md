<!-- collected 2026-09-08T05:10:27Z by campaign coordinator; agent id a036a580e6fb056a2; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a036a580e6fb056a2.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**W85**, gate-artifact-provenance lane (W73's named successor), OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I am told I am Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start of run; no `*MODEL*` variable exists; the five long proxy-list variables `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` are elided at their values only — they carry no model information and appear verbatim in the transcript):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,…,api.anthropic.com,…
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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,…
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 … (proxy config)
NO_PROXY=localhost,127.0.0.1,::1,…
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,…
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**Start:** `Tue Sep 8 05:01:49 UTC 2026`, HEAD `b1f6a6dcc2149b6a8a5ee38ccfc54823c07bb056`, `git status --porcelain` **empty**.
**End:** `Tue Sep 8 05:06:29 UTC 2026`, HEAD `9a936582365c8b46cb69e171d9fcd063c6a6add9`, `git status --porcelain` **empty (0 lines)**. HEAD advanced mid-run (coordinator collection). Verified, not assumed: `git diff --name-only b1f6a6dc 9a936582 | grep -v opus-capacity-campaign-20260908 | wc -l` → **0**, so every module and input I measured is byte-identical across my window. Scratch `/tmp/claude-0/w85/` **deleted** (`ls -d` → `No such file or directory`). I wrote nothing into `/home/user/Rare-cancers` and ran no git write operation (only `rev-parse`, `status`, `diff --name-only`, `ls-files`).

## Question

For the **six `--check` gates outside** the 18-row loop — `systems/systems_check.py` (`preflight.sh:609`), `research/manuscripts/emc_systems_map_check.py` (`:627`), `research/autonomy/receipt_schema.py` (`:929`), `research/autonomy/contract_check.py` (`:1484`), `scripts/tier_budget.py` (`:1507`), `research/autonomy/derived_ids.py` (`:1536`) — enumerate every artifact each reads, classify PRODUCER (`file:line`) or HAND-MAINTAINED with record counts, and determine the decisive property W73 isolated: **does the gate produce an artifact of its own to byte-compare against, or can it only validate shape?** Then: which, if any, share row 17's exposure?

Open because W73 explicitly scoped these six out ("not censused here — out of scope for the bounded question") and named this as its successor task. No worker has covered them.

## Prior-work check

Read **in full** as instructed: `COMMON-BRIEF.md` (746 lines), `CORPUS-CONTEXT.md` (82), `CLOSED-WORK.md` (70), `reports/W73-producerless-gate-artifacts.md` (209), `reports/W44-vacuous-pass-census.md` (249).

Taken **as given, not redone**: W73's 133-artifact / 26-hand-maintained census of the 18-row loop and its row-17 conclusion; W44's 4-of-18 vacuous-pass measurement; W45's regenerate-then-check escape class and its three-valued discriminator; W74's refinement (a cross-source anchor blocks the escape only if the loop is driven from the non-emptied side) and its measured `emc_systems_map_check` escape **with** `.git` present; W72's 5-of-33 unwired-checker census; W37c's finding that `emc-systems-map.json` has no generator; W41 on `inputs/`; W31b on the campaign's own `systems_check` footprint. I did not re-measure any of these.

Commands: `grep -n -i -E "W73|W44|W45|W72|producerless|vacuous" COMMON-BRIEF.md` (locating the sections quoted above); `sed -n` over `scripts/preflight.sh` at each of the six line numbers ±14, which confirms all six invocations verbatim and that none is inside the `:847-864` loop.

W25 was not read, referenced, extended or audited. `scripts/preflight.sh` was **not run and not edited**. `atr_hrd_sarcoma_series.py` was never invoked in any mode. No `--refresh`, no `--write-views`, no `--write-view` anywhere. No CLOSED-WORK item replayed; no network attempted, so I have no denial to record. No content-policy refusal occurred in this run.

## Method and inputs

Read-only against the live checkout at the HEADs above; all execution in a `cp -a` copy at `/tmp/claude-0/w85/tree` (617 MB, `.git` removed after copy), `PYTHONDONTWRITEBYTECODE=1`, `/usr/local/bin/python3` (3.11), now deleted.

1. **Read-set enumeration** by reading each gate's source: module-level path constants, `os.path.join(REPO, …)` sites, `glob`/`os.walk`/`os.listdir` roots, and data-driven dereferences (paths carried *inside* an input record). For `systems_check` I resolved its two f-string path constructions by hand (`f"{name}.json"` over the 15-name `COLLECTIONS` list at `:220`, `f"{key}.schema.json"` at `:510`) — exactly W73's documented f-string false-negative class, which a basename grep would have missed.
2. **Env-knob check**: none of the six constructs a path from an environment variable; `grep` for `environ`/`getenv` in the four small modules returns nothing, and the two large ones parameterise only by CLI flag (`--dir`, `--contract`, `--map`).
3. **Writer detection, W73's three passes** over `*.py *.mjs *.sh *.yml`, campaign directory excluded: pass 1 literal write idioms, pass 2 helper verbs (`write_ledger`, `dump`, `emit`, `save`), pass 3 proximity/variable resolution. Pass 2 recovered one producer pass 1 missed (`research-ledger.json`, named only as `LEDGER_FILE` at `priority.py:54` and written through `ledger_io.write_ledger` at `:1670`). Every remaining candidate was grepped individually; all hits were read-only `open(...)`, `tmp_path` test fixtures, or prose naming the file while writing something else.
4. **Write-freedom read from source BEFORE any execution**: `receipt_schema.py` contains **no write primitive at all**; `contract_check.py` has only read `open(...)`; `tier_budget.py` only reads; `derived_ids.py`'s single write (`:224`) is inside `extend()`, unreachable from `--check`. I did not execute `systems_check.py` or `emc_systems_map_check.py` at all.
5. **Emptying probes** for the four small gates only, in the scratch copy, with true exit codes captured (`out=$(cmd); rc=$?` — an earlier pipe-to-`tail` measurement returned `tail`'s status and was re-run).

## Result

### A. Per-gate read sets, with producer classification

All rows `PRIMARY` (counts and writer-absence are properties of committed bytes measured at the HEADs above).

**Gate `:609` — `systems/systems_check.py --check`**

| Artifact set | n | Producer |
|---|---|---|
| `systems/graph/*.json` — the 15 `COLLECTIONS` (`:38-56`, resolved via `f"{name}.json"` at `:220`) plus `plan.json` (`:226`), `integrity.json` (`:228`), `artifact-refs.json` (`:1991`), `link-baseline.json` (`:2245`), `relations.json` (`:2335`) | **19 files** | **HAND-MAINTAINED** — no writer in the tree; `CLAUDE.md` §7 states it (`systems/graph/*.json` owns model state) |
| `systems/schema/*.schema.json` (`:170`, `:495-522`) | **11 files** | HAND-MAINTAINED |
| `systems/views/**/*.md` (`:4537-4543`) | **111 files** | **PRODUCER — `systems/systems_check.py:4524-4531`** (`write_views`, `open(path,"w")` at `:4529`) |
| `research/method-watch-triggers.json` (`:882`, `:1227`) | 39 triggers | HAND-MAINTAINED (W73, reproduced) |
| `research/manuscripts/emc-systems-map.json` (`LEGACY`, `:1047`) | 22 keys; routes 40, instruments 32, revival_triggers 28 | HAND-MAINTAINED (W37c, reproduced) |
| `research/manuscripts/nr4a3-program-map.md` (`MAP_DOC`, `:1105`) | 4,505 lines | HAND-MAINTAINED (`realised_spend.py:61,427` instructs a human to update it) |
| `research/manuscripts/pinned-figures.json` (`PINNED`, `:1360`) | 183 entries (W47) | HAND-MAINTAINED |
| `CLAUDE.md`, `AGENTS.md` (`:1361`), `README.md`, `CONTRIBUTING.md`, `systems/POLICY-evidence.md` (`:1528`), `systems/CONVENTIONS.md` (`:1795`), `scripts/preflight.sh` (`:1579`), `.claude/skills/*/SKILL.md` (`:1403`,`:1533`) | ~8 + skills | HAND-MAINTAINED |
| **A whole-repository `os.walk(REPO)`** (`:1126-1137`, and sibling walks at `:1326`, `:1857`, `:2292`) over every `.md/.py/.json/.yml` outside transient/`archive/` | ~7,855 tracked files, **820** of them `.md` | mixed; not a fixed path list |

**Gate `:627` — `research/manuscripts/emc_systems_map_check.py --check`**

| Artifact | n | Producer |
|---|---|---|
| `research/manuscripts/emc-systems-map.json` (`MAP_PATH`, `:60`) | as above | HAND-MAINTAINED |
| `research/manuscripts/emc-systems-map.md` (`VIEW_PATH`, `:61`) | 720 lines | **PRODUCER — `emc_systems_map_check.py:1333`** (`open(VIEW_PATH,"w")` under `--write-view`) |
| `research/method-watch.md` (`:807`) | 611 lines | HAND-MAINTAINED |
| `research/method-watch-triggers.json`, reached indirectly as `m["_scan_interop"]["_scan_registry"]` (`:876-879`) | 39 triggers | HAND-MAINTAINED |
| Repo paths carried inside map records — `artifacts[].path` (12, opened `rb` at `:430`, `:667`), `instruments[].module` (32, `:699`), guards (`:261`), homes (`:454`), claim documents | **170 distinct repo paths named in the map, 170/170 present** | mixed (produced artifacts + hand documents) |
| The tracked-file sweep `git ls-files --cached --others --exclude-standard` (`:349-352`) | whole tree | n/a |

**Gate `:929` — `research/autonomy/receipt_schema.py --check`**

| Artifact | n | Producer |
|---|---|---|
| `research/autonomy/receipts/*.json` (`RECEIPT_DIR`, `:79`; `glob` at `:383`) | **129 files** (107 governed, 18 pre-schema, 0 unreadable) | **HAND-MAINTAINED** — no writer anywhere; `preflight.sh:920-921` states it in the gate's own header (*"There is no receipt writer … every cycle hand-authors the JSON"*), and `.claude/skills/research-loop/SKILL.md:51` is the instruction to a human/agent |

**That is the entire read set. One collection, one directory, all hand-authored.**

**Gate `:1484` — `research/autonomy/contract_check.py --check`**

| Artifact | n | Producer |
|---|---|---|
| `.claude/skills/research-loop/SKILL.md` (`CONTRACT`, `:89`) | 126 lines; the extracted step is **7,743 chars** | HAND-MAINTAINED |
| `research/autonomy/receipt_schema.py` — read **as text** and AST-parsed (`:281`, `open(S.__file__)`) | 432 lines; 6 `*_KEY` constants, 5 required field paths | HAND-MAINTAINED (source) |

Its receipt fixtures are **in-source literals** (`_fixtures()`, `:160-180`), not committed artifacts.

**Gate `:1507` — `scripts/tier_budget.py --check`**

| Artifact | n | Producer |
|---|---|---|
| `scripts/tier-budgets.json` (`BUDGETS`, `:46`) | 3 tiers | **HAND-MAINTAINED** — the gate's header calls it *"a number somebody decided"* (`preflight.sh:1495`) |
| Every `test_*.py` under the declared directories (`count_dir`, `:80-97`): `scripts/tests`, `research/autonomy/tests`, `systems/tests` (102 files, 1466 fn), `research/manuscripts/tests` (111 files, 966 fn), `research/modalities/tests` (436 files, 7247 fn) | **649 files, 9,679 test functions** | HAND-MAINTAINED (source) |

**Gate `:1536` — `research/autonomy/derived_ids.py --check`**

| Artifact | n | Producer |
|---|---|---|
| `research/autonomy/derived-ledger-ids.json` (`MAP_PATH`, `:67`) | **83 bindings** | **PRODUCER — `research/autonomy/derived_ids.py:224`** (`path.write_text`, inside `extend()`, `--extend` only; append-only, never renumbers) |
| `research/autonomy/research-ledger.json` (`LEDGER_PATH`, `:68`) | **415 entries** | **PRODUCER — `research/autonomy/priority.py:1670`** via `ledger_io.write_ledger`; the file's own `_generated_by` says `python3 research/autonomy/priority.py --write`. *(Recovered only by pass 2 — the basename is bound to `LEDGER_FILE` at `priority.py:54` and never re-spelled at the write.)* |
| `systems/graph/routes.json` (`ROUTES_PATH`, `:69`) | **83 routes** | HAND-MAINTAINED |

### B. The decisive property — does the gate produce an artifact of its own to byte-compare?

| Gate | Produces its own artifact? | Byte-compare in `--check`? | What `--check` can therefore establish |
|---|---|---|---|
| `:609` `systems_check.py` | **YES — 111 generated views** (`:4524-4531`) | **YES** — `check_views` (`:4535-4545`) re-renders every view in memory and compares text; mismatch → `[G2]` | Recomputation equality **plus** shape/invariants |
| `:627` `emc_systems_map_check.py` | **YES — `emc-systems-map.md`** (`:1333`) | **YES** — `main` re-renders and compares at `:1342-1354`; mismatch → `V1` | Recomputation equality plus shape |
| `:929` `receipt_schema.py` | **NO** — no write primitive in the module | **NO** | Shape only (per-receipt field presence/type) |
| `:1484` `contract_check.py` | **NO** | **NO** | Agreement between two hand-maintained sources (contract text ↔ enforcer's constants) — a **cross-source** check, not a byte-compare |
| `:1507` `tier_budget.py` | **NO** | **NO** | A one-sided **threshold** (`functions > budget`) plus an AST shadowed-name check |
| `:1536` `derived_ids.py` | It **can write one of its own inputs** (`--extend`), but `--check` never regenerates or compares it | **NO** | **Three-way cross-source** agreement (map ↔ routes ↔ ledger) |

**Four of six produce no artifact to compare against.** That is a far higher producerless fraction than the 18-row loop, where W73 found exactly one (row 17) of eighteen.

### C. Which share row 17's exposure — measured, not argued

Row 17's exposure is the **conjunction**: entire input set hand-maintained **AND** no produced artifact of its own **AND** an empty input collection still exits 0.

| Gate | All inputs hand-maintained? | No produced artifact? | Empties to exit 0? | Shares row 17's exposure? |
|---|---|---|---|---|
| `:929` `receipt_schema.py` | **YES** (129/129) | **YES** | **YES — measured, rc=0**: `--check --dir <empty dir>` → `0 governed receipt(s), 0 failure(s), 0 unreadable` | **YES — full structural match to row 17** |
| `:1507` `tier_budget.py` | **YES** (650 files) | **YES** | **YES — measured, rc=0** ×2: every `test_*.py` deleted from the three commit-loop dirs → `ok commit-loop 0/1500 test function(s) in 0 file(s)`; `tiers` → `{}` → no output at all | **YES, and by a second door** — the check is one-sided, so *deletion always looks compliant* |
| `:1536` `derived_ids.py` | 1 of 3 (routes) hand; 2 produced | **YES** | **Only when all three are emptied together — measured, rc=0**: `0 route→id bindings, frozen and agreeing with the ledger`. Emptying *bindings alone* → **rc=1** (2 ledger rows unbound). Emptying *routes alone* → rc=0 with a note, **by documented design** (`preflight.sh:1533`) | **PARTIAL** — protected by a cross-source anchor (W45/W74's discriminator), not by a producer |
| `:1484` `contract_check.py` | **YES** (2/2) | **YES** | **NO — measured, rc=1** on an empty contract (`no numbered step … whose title contains 'Write the receipt' … it refuses rather than passes`) **and** rc=1 on a 30-char near-empty step (`< 400`, `_MIN_STEP_CHARS`) | **NO** — an **in-source constant** blocks it; the module's `ContractUnreadable` docstring names the failure mode explicitly (*"a vacuous pass is exactly how `subagent_width` governed nothing for a fortnight"*) |
| `:609` `systems_check.py` | No (111 views produced) | No | Not tested by me; W37c/W74 measured the emptying and regenerate-then-check behaviour | **NO** (produces 111 artifacts it compares) |
| `:627` `emc_systems_map_check.py` | No (view produced) | No | W74 measured full escape via `--write-view` then `--check` (regenerate-then-check, W45's class) | **NO** on row 17's property; **YES** on W45's separate escape class |

**Answer: two of the six share row 17's exposure outright — `receipt_schema.py` (`:929`) and `tier_budget.py` (`:1507`) — and a third, `derived_ids.py` (`:1536`), shares the producerless half but is protected by a cross-source anchor that only fails when all three inputs empty together.** Counting the loop and the non-loop gates as one surface, the producerless-and-vacuous population is **three of twenty-four gates**, not one of eighteen.

Two refinements W73's frame did not anticipate:

- **`receipt_schema.py` is a stricter match to row 17 than row 17 is.** Row 17 has 4 records; this gate has 129 hand-authored files, so it is not near-empty by record count — but its inputs are **created one at a time by an agent following a prose instruction**, so the failure that matters is not emptying, it is a receipt that is never written. A cycle that writes no receipt is indistinguishable from a clean board here, and the gate's own preflight header already says the prevention half *"has to be here and nowhere else"* because there is no writer. **SOURCE-READ plus the measured empty-dir run; I did not test a partially-populated directory.**
- **`tier_budget.py` is one-sided by construction, which is a distinct shape from row 17's.** `count_dir` (`:82-83`) returns `(0, 0, [])` when a directory is absent, with an explicit comment defending the *opposite* case (an unparseable file counts as 1, so it cannot buy headroom). Deleting tests can only move a tier further under budget. This is not a defect claim — a budget gate is *supposed* to be one-sided — but it means the gate's green is compatible with any amount of test loss, and W41's separate `PREFLIGHT_FULL` pure-logic test, not this gate, is what notices an undeclared directory.

I authored no repair, no patch, no diff, no gate and no test. No guard was weakened, relaxed or reordered. No producer was added.

## Validation evidence

**RUN** — environment: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, `/usr/local/bin/python3` (3.11), `PYTHONDONTWRITEBYTECODE=1`, cwd `/tmp/claude-0/w85/tree` (a `cp -a` copy with `.git` removed). No network attempted. All exit codes captured as `out=$(cmd); rc=$?`.

Baseline, unmutated scratch copy:
```
research/autonomy/receipt_schema.py rc=0 |    107 governed receipt(s), 0 failure(s), 0 unreadable
research/autonomy/contract_check.py rc=0 |    5 required field path(s), 6 key constant(s), 7743 chars of contract read, 0 disagreement(s)
scripts/tier_budget.py              rc=0 |    ok commit-loop 1466/1500 · modalities 7247/7500 · paper-guards 966/1000
research/autonomy/derived_ids.py    rc=0 |    83 route→id bindings, frozen and agreeing with the ledger
```

Emptying probes:
```
A  receipt_schema --check --dir <empty dir>      rc=0   0 governed receipt(s), 0 failure(s), 0 unreadable      [VACUOUS PASS]
B  contract_check --check --contract <0 bytes>   rc=1   FAILED no numbered step … 'Write the receipt' … refuses rather than passes
B2 contract_check --check --contract <30 chars>  rc=1   FAILED … extracted to only 30 characters (< 400) … refusing rather than checking against near-empty text
C  tier_budget --check, all test_*.py deleted from scripts/tests, research/autonomy/tests, systems/tests
                                                 rc=0   ok commit-loop 0/1500 test function(s) in 0 file(s)     [VACUOUS PASS]
C2 tier_budget --check, tiers -> {}              rc=0   (no output)                                             [VACUOUS PASS]
D1 derived_ids --check, routes.json -> []        rc=0   note: 83 binding(s) name a route no longer in the graph … [by documented design, preflight.sh:1533]
D2 derived_ids --check, routes [] + bindings {}  rc=1   ledger row AUT-027 serves RT-FUSION-OUTPUT, which the frozen map does not bind
D3 derived_ids --check, routes restored, bindings {}  rc=1  (same two ledger rows)
D4 derived_ids --check, all three emptied        rc=0   0 route→id bindings, frozen and agreeing with the ledger [VACUOUS PASS]
   restore all                                   rc=0   83 route→id bindings, frozen and agreeing with the ledger
```

Write-freedom, read from source **before** each run: `grep -nE 'open\([^)]*"w|write_text|json\.dump\(|os\.replace|shutil\.|makedirs|\.write\(' research/autonomy/receipt_schema.py` → **no match, exit 1**; `contract_check.py` write-idiom hits: none (only read `open` at `:117`, `:281`); `tier_budget.py`: none (`:90`, `:106` read); `derived_ids.py`: one, `:224`, inside `extend()`.

Writer detection (exit 0 each): pass-1 idiom grep over `*.py *.mjs *.sh *.yml` for `research-ledger.json`, `derived-ledger-ids.json`, `routes.json`, `artifact-refs.json`, `link-baseline.json`, `relations.json`, `plan.json`, `integrity.json`, `tier-budgets.json`, `method-watch.md`, `nr4a3-program-map.md`, `pinned-figures.json` → every hit a `tmp_path` test fixture or an unrelated file; pass-2/3 verb-and-proximity grep → recovered `priority.py:1670`; per-artifact residual grep for `method-watch.md`, `nr4a3-program-map.md`, `pinned-figures.json`, `SKILL.md`, `CONVENTIONS.md`, `emc-systems-map.json`, `tier-budgets.json` → **zero write contexts**, only prose and docstrings. `grep -rn … 'graph/*.json' | grep <write idioms> | grep -v /tests/` → **empty**; same for `receipts/`.

Counts: `ls research/autonomy/receipts/*.json | wc -l` → **129**; `ls systems/graph/*.json` → **19**; `ls systems/schema/*.json` → **11**; `find systems/views -name '*.md' | wc -l` → **111**; `git ls-files '*.md' | wc -l` → **820**; `git ls-files | wc -l` → **7855**; JSON record counts by `json.load` (bindings 83, entries 415, routes 83, tiers 3, map 22 keys); 170 distinct repo paths named inside `emc-systems-map.json`, 170/170 present on disk.

Tree integrity: live `git status --porcelain` **0 lines at start and end**; `git diff --name-only b1f6a6dc 9a936582 | grep -v opus-capacity-campaign-20260908 | wc -l` → **0**; `rm -rf /tmp/claude-0/w85 && ls -d /tmp/claude-0/w85` → `No such file or directory`.

**PROPOSED (NOT RUN):** I did **not** execute `systems/systems_check.py` or `research/manuscripts/emc_systems_map_check.py` in any mode — their emptying and escape behaviour is quoted from W37c/W45/W74 and labelled as theirs. I did not test a *partially* populated receipt directory, a single missing receipt, or a partially deleted tier. I did not test file **removal** (as opposed to emptying) for `tier-budgets.json` or the three `derived_ids` inputs. I ran no gate against the live tree and did not run `scripts/preflight.sh`.

## Limitations

- **Writer-absence is a strong inference from three grep passes plus a per-path manual grep, not proof.** W73's two documented false-negative classes are real: I resolved `systems_check`'s f-string path constructions by hand and checked all six modules for env-knob paths (none), but a producer that constructs one of these paths by a route I did not anticipate would be missed. The HAND-MAINTAINED classifications are therefore an **upper bound**.
- `systems_check`'s read set is **not a fixed artifact list** — several of its checks are whole-repository `os.walk`s. I enumerated its *named* inputs exhaustively and characterised the walk; I did not instrument it at runtime (W44's `sys.addaudithook` method would give the observed set, and I did not run the module).
- `emc_systems_map_check`'s dereferenced set is **data-driven** (170 paths carried inside the map). That count is this tree's value and moves with the map.
- The counts (129 receipts, 9,679 test functions, 83/415/83, 111 views) are values at HEAD `b1f6a6dc`/`9a936582` and move as the repository moves. The **structural** verdicts — produces-an-artifact-or-not, and the exit codes above — are properties of the code and are stable until a module changes.
- My four probes were run **without `.git`** in the scratch copy. None of these four modules calls git (verified: no `subprocess` git invocation in any of them), so W74's git-presence caveat does not apply here — but that caveat is exactly why I did not extend the probes to `emc_systems_map_check`, which does.
- **HAND-MAINTAINED is not wrong.** No artifact's content was graded, no artifact is claimed stale, mislabelled or incorrect, and nothing here bears on EMC efficacy, safety, selectivity, therapeutic window or clinical readiness. There is no wet lab. These are measurements of Python exit codes and committed bytes.
- No content-policy refusal occurred in this run.

## Stop condition

Set up front: *return once each of the six non-loop gates has (a) its read-artifact set enumerated, (b) every artifact classified PRODUCER with a `file:line` or HAND-MAINTAINED with a documented writer-absence, (c) record counts, (d) a determination of whether it produces an artifact of its own to byte-compare, and (e) a stated verdict on whether it shares row 17's exposure.*

**MET on all five**, for all six gates, with (d) and (e) backed by ten executed probes rather than argument for the four gates policy allowed me to run. Returning without padding.

## Tool-call and wall-clock count actually used

**19 tool calls; 4 min 40 s wall clock** (05:01:49Z → 05:06:29Z). Well inside the ~40/~40 target.

## Next concrete action

**For a human owner, not a worker, and it is now a two-gate question rather than one.** W73 ended by asking whether `citation_debt.py` should be a gate at all. The same question now applies with the same evidence to `receipt_schema.py:929` — and the answer there is likely *different*, because the repository has already reasoned about it in the gate's own header: it says a receipt writer cannot exist because the cycle contract asks an agent to author the JSON, and that the commit is therefore the only moment anything can check. If that reasoning holds, the missing guard is not a producer but a **presence** check (did this cycle write a receipt at all?), which no gate currently makes. `tier_budget.py` needs no ruling — one-sidedness is correct for a budget — but its green should not be read as "the tests are still there"; W41's `PREFLIGHT_FULL` pure-logic test is the only thing that notices a directory leaving a tier. **I am not proposing, drafting or applying any of this**; CLAUDE.md §6's rule against changing a guard needs an owner ruling, and the executed exit codes above are the evidence it should rest on.

**The natural read-only successor in this lane**, if one is wanted: instrument `systems_check.py --check` from the outside with `sys.addaudithook` (W44's method, W71's don't-edit-the-module discipline) to convert its walk-driven read set from "characterised" to "observed", which is the one input set in this census that remains an enumeration of names rather than a measurement.
