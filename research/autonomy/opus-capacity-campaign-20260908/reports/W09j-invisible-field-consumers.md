<!-- collected 2026-09-08T04:52:29Z by campaign coordinator; agent id a1187a18eb6c7479a; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a1187a18eb6c7479a.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Scratch deleted, live tree clean, HEAD verified stable outside the campaign directory. Report follows.

---

## Worker

- **Worker:** W09j, lane 9, OPUS-CAPACITY-CAMPAIGN-20260908. Successor measurement to W09i; read-only static-consumer census, no repair authored or proposed.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model — `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions. The coordinator must extract the actual runtime model from the transcript.
- `date -u` **start** `Tue Sep  8 04:38:33 UTC 2026` · **end** `Tue Sep  8 04:48:12 UTC 2026`.
- `git rev-parse HEAD` **start** `408b676aec3625a36917755662516232a27a1278` · **end** `8a667406e875ae99c7d50347b2e895a177fcb048`. ⚠ **HEAD moved under me.** Verified rather than assumed: `git diff --stat 408b676a HEAD -- systems/ scripts/ research/ ':!research/autonomy/opus-capacity-campaign-20260908'` produced **empty output** — no file I searched changed between the two commits. Every citation below is valid at both HEADs.
- `git status --porcelain` **start** 0 lines · **end** 0 lines. **Write isolation honoured:** nothing written, moved or deleted under `/home/user/Rare-cancers`; no git write operation; `scripts/preflight.sh` not run; no graph file, view, manuscript or report touched; no patch authored or proposed. All execution under `/tmp/claude-0/w09j/`, **now deleted** (`rm -rf`; `ls` confirms absent; free disk 18 GiB).
- No network, no retrieval, no paid API, no GPU. `research/modalities/atr_hrd_sarcoma_series.py` never invoked, with or without `--check`. W25 not read, audited or referenced. Frozen corpus not read — the line-shift correction in `CORPUS-CONTEXT.md` names `systems/systems_check.py` as one of two files whose corpus line numbers are wrong, and every `:NN` citation below is a `systems_check.py` or sibling line number resolved in the **live checkout**.
- No content-policy refusal occurred.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (exit 0, captured at start; five long proxy lines elided as marked, nothing else removed):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
[no_proxy=… elided]
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
[GLOBAL_AGENT_NO_PROXY=… elided]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
[JAVA_TOOL_OPTIONS=… elided]
[NO_PROXY=… elided]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
[npm_config_noproxy=… elided]
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

---

## Question

W09i measured that **40 of 148** (collection, required-name) pairs are wholly invisible to `systems_check.py --write-views`: delete the field from every record and the mode still exits 0, prints `wrote 111 view(s)`, and regenerates byte-identical views — **1,547 required field instances** in total.

**My bounded question: for each of those 40, does any OTHER executable consumer in the repository read the field?** Not "is it required" (the schema says so, and plain mode enforces it — W09i measured 40/40 raising `ERROR [S…]`), but "does anything else in `systems/`, `scripts/` or `research/` actually name and read this field".

This is open because W09i deliberately stopped at the `--write-views` boundary and named no other reader. A field the view generator ignores may still be load-bearing for a gate, a producer or a test — or it may be a value nothing in the repository ever reads.

**Answer: (a) 10 · (b) 30 · (c) 0.** Ten of the forty are read by an executable consumer outside the `--write-views` path. The other thirty are named only in their JSON Schema `required` declaration (and, for most, in prose); no executable names them. Two of those thirty — `publications/posted_by` and `instruments/module` — have **zero** mentions anywhere in the repository outside `systems/graph/` and their own schema file.

---

## Prior-work check

| command / read | result |
|---|---|
| read in full, as dispatched | `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W09i-write-views-presence-enforcement.md` |
| `ls reports/ \| grep -i W09` | W09, W09b–W09i present. I read only W09i in full (my dispatch's named input). W25 not listed among them and not read. |
| `rg -l -F 'graph/<collection>' -g '*.py' -g '*.sh' systems scripts research` (×9) | the per-collection executable candidate sets — 2 to 24 files each |
| `rg -l -F 'systems/graph' -g '*.py' -g '*.sh' systems scripts research` | **69** executables mention the graph path at all (after excluding the campaign directory) |

**Campaign reports are not repository evidence** (COMMON-BRIEF §3): the only campaign artifact I used is W09i's measured 40-pair list, which my dispatch supplies as the input set, not as a finding I am re-grading. I re-measured nothing of W09i's — no scratch copy, no mutation, no `--write-views` run. **From "Known, measured, and NOT worth rediscovering":** I did not re-measure the 0-of-89 resolution rate, did not touch `origin/literature-cache`, ran no tests (so the `pytest` interpreter trap does not arise), and did not attribute the `systems_check --check` baseline.

---

## Method and inputs

| input | role |
|---|---|
| `/home/user/Rare-cancers` @ `408b676a` → `8a667406` (identical outside the campaign directory) | tree searched, read-only throughout |
| W09i report §R.3 | the 40 (collection, required-name) pairs — the input set, transcribed exactly |
| `systems/schema/*.json` (11 files) | where each required name is declared |
| `systems/`, `scripts/`, `research/` minus `research/autonomy/opus-capacity-campaign-20260908/` | the search space |
| `rg` 14.x, Python 3.11 (`/usr/local/bin/python3`), Linux, no network | tools |

**Procedure.**

1. **Transcribe the 40 pairs** from W09i §R.3 into `pairs.txt` (24 distinct names across 9 collections; count verified = 40).
2. **Scope the candidate consumers per collection.** A file cannot read `collection.field` unless it loads that collection. For each of the 9 collections I built the candidate set from `rg -F "graph/<collection>"` over `*.py`/`*.sh`, plus `systems/systems_check.py` and `systems/tests/test_systems_check.py` in every set, plus four files that address the graph as `REPO / "systems" / "graph" / "<x>.json"` and so miss the literal-path grep (`research/autonomy/venue_fit.py`, `systems/tests/test_autonomy_venue_fit.py`, `systems/tests/test_autonomy_priority.py`, `systems/tests/test_extract_requirement_register.py`, `systems/extract_requirement_register.py`).
3. **Grep each pair's name inside its own collection's candidate set**, with field-access patterns: `["n"]`, `.get("n"`, `"n":`, `"n",` / `"n")` / `"n"]`, `"n" in`.
4. **Disambiguate every hit by reading it.** Names like `file`, `kind`, `level`, `title`, `status`, `owner`, `why` collide across collections and against document frontmatter, so raw hit counts are not evidence. Two devices did the disambiguation: (i) I mapped every `systems_check.py` hit line to its enclosing top-level `def` and then extracted, per function, which `g["<collection>"]` keys that function actually indexes; (ii) I read the ~20 ambiguous call sites directly.
5. **Used W09i's measurement as a decisive filter, not as an assumption.** For an INVISIBLE pair, deletion produced byte-identical views and no `KeyError`. That is empirical proof that **no `render_*` function reads that collection's field** — so any `render_*` hit for such a pair is provably a different collection. This filter is what makes the ambiguous generic names tractable, and it is the one place my result rests on W09i's run rather than on my own reading.
6. **Non-executable search** for class (b): `systems/schema/*.json` line-level, then `.md`/`.json` outside `systems/graph/`, `systems/views/`, `systems/schema/` and the campaign directory.

**Sampling rule: none.** All 40 pairs were searched and every non-trivial hit read.

---

## Result

### R.1 — ⭐ The three counts `PRIMARY`

| class | pairs | % of 40 |
|---|---|---|
| **(a) read by at least one other gate / producer / test** | **10** | 25.0% |
| **(b) named only by non-executable declaration or prose** | **30** | 75.0% |
| **(c) read by nothing at all** | **0** | 0% |

**(c) is 0 by construction, and that needs saying plainly rather than filed as a result.** Every one of the 40 is a `required` member in `systems/schema/*.json` — that is what made it a required field in the first place — and `check_schemas` enforces those declarations generically in plain mode (W09i: 40/40 raise `ERROR [S…]`, 1,547 instances). So no pair is unreferenced in the literal sense. The substantive finding is **(b) = 30**: for thirty pairs the schema declaration is the *only* thing that reads them, and no line of executable code anywhere names the field. Under the stricter criterion "mentioned nowhere outside `systems/graph/` and its own schema file", the count is **2**: `publications/posted_by` and `instruments/module` (§R.4).

### R.2 — ⭐ The 10 class-(a) pairs, with exact file:line `PRIMARY`

| # | pair | consumer | exact site(s) | consumer type |
|---|---|---|---|---|
| 1 | `modalities/revisit_trigger` | modality-census test | `systems/tests/test_modality_census.py:175` (`trg = m.get("revisit_trigger") or []`), used at `:176`, `:178` | **test** — `m` iterates `graph["modalities"]`; asserts every `parked_capability` names a reachable `TECH-*` |
| 2 | `technologies/paper_id` | literature trigger scanner | `scripts/trigger_scan.py:785` (read, dedupe key), `:795` (write) | **producer** — `techs = json.load(TECHNOLOGIES)`; `s` iterates `tech["pending_signals"]` |
| 3 | `publications/kind` | claim-coverage census | `research/manuscripts/claim_coverage.py:141` (`if entry.get("kind") != "publication": continue`) | **producer/gate** — `entry` iterates `systems/graph/publications.json` |
| 3 | `publications/kind` | its test | `research/manuscripts/tests/test_the_census_reads_every_publication_endpoint.py:104` (same predicate) | **test** |
| 4 | `instruments/file` | `check_pointers` `[P1]`/`[P2]` | `systems/systems_check.py:700` (`if isinstance(node.get("file"), str)`) → `:714` (`path = owner["file"]`) | **gate**, plain-mode only |
| 5 | `lanes/file` | same | `systems/systems_check.py:700`, `:714` | **gate**, plain-mode only |
| 6 | `requirements/file` | same | `systems/systems_check.py:700`, `:714` | **gate**, plain-mode only |
| 7 | `strategies/file` | same | `systems/systems_check.py:700`, `:714` | **gate**, plain-mode only |
| 8 | `routes/title` | asymmetry linter | `research/manuscripts/lint_asymmetry.py:507` (`_PROSE_KEYS`), applied at `:557` | **linter** — value-generic, see caveat |
| 9 | `requirements/title` | same | `research/manuscripts/lint_asymmetry.py:507`, `:557` | **linter** — value-generic |
| 10 | `blockers/why` | same | `research/manuscripts/lint_asymmetry.py:507`, `:557` | **linter** — value-generic |

**Rows 4–7 are one mechanism and it is the most interesting result here.** `check_pointers` (`systems_check.py:709`) iterates `for coll in COLLECTIONS: for row in g[coll]:` and hands each row to `_owner_blocks`, which yields **every dict at any depth carrying a string `file`** and then checks that path exists on disk. `COLLECTIONS` (`systems_check.py:38–…`) is the 14-name list `strategies, routes, requirements, blockers, technologies, forecasts, instruments, objects, evidence, artifacts, claims, roadmap, lanes, publications`. So `file` in four of the invisible collections **is** read — by a plain-mode gate that never runs under `--write-views`. Deleting the field does not make that gate fail; it makes it silently check fewer pointers. `_owner_blocks`'s own docstring at `:692` records that this generalisation was written *because* a hand-listed two-place version missed a real bad anchor.

**Rows 8–10 carry a caveat that must not be dropped.** `lint_asymmetry.py` scans every long JSON string value under `systems/graph/` (`SCAN_PREFIXES` at `:96–100`). The literal field name is read at `:557` — `if km.group("key").lower() in _PROSE_KEYS` — but only to *prefix the label* on a finding; the value is scanned whether or not its key is in `_PROSE_KEYS`. So the name is genuinely read, and these three fields are the only ones of the 40 whose names appear in that list, but the linter would still scan their prose under any other key name. **It is also not wired into a gate:** `rg 'lint_asymmetry'` finds no hit in `scripts/preflight.sh`, `scripts/fast_checks.py` or `.github/`; its only executable exercise is `research/manuscripts/tests/test_lint_asymmetry.py`, which runs it against `tmp_path` corpora, never the working tree.

### R.3 — The full per-field table, all 40 `PRIMARY`

`instances` = W09i's measured deletion count. "Nearest collision" names the code that a name-only grep would wrongly credit, and which I read and rejected.

| # | collection | field | inst. | class | consumer (a) / why not (b) |
|---|---|---|---|---|---|
| 1 | modalities | `kind` | 217 | **b** | all `kind` reads are blockers (`systems_check.py:299, 346, 636, 639, 900, 4369`) or document frontmatter (`:1508, 1872, 1879`); `derive()` does not index `g["modalities"]` at all |
| 2 | modalities | `level` | 217 | **b** | every `level` read is frontmatter `fmv.get("level")` (`systems_check.py:601, 603, 623, 1507`) or a schema enum (`:1812`) |
| 3 | modalities | `revisit_trigger` | 9 | **a** | `systems/tests/test_modality_census.py:175`. (`systems_check.py:943, 988` and `priority.py:263` read the **routes** `timing.revisit_trigger`, not the modality one) |
| 4 | technologies | `paper_id` | 302 | **a** | `scripts/trigger_scan.py:785`, `:795` |
| 5 | routes | `kind` | 83 | **b** | as row 1 — no site reads a route's `kind` |
| 6 | routes | `level` | 83 | **b** | as row 2 |
| 7 | routes | `provenance` | 83 | **b** | `systems_check.py:479` reads `objects[].definition.provenance`; `:692` is a docstring; `nr4a3_tcip_reach.py:174` reads its own record's provenance |
| 8 | routes | `title` | 83 | **a** | `lint_asymmetry.py:507`, `:557` (value-generic). `systems_check.py:2155` reads `lane['title']`; `:3163–3164` is `_pub_title` |
| 9 | publications | `kind` | 33 | **a** | `claim_coverage.py:141`; `test_the_census_reads_every_publication_endpoint.py:104` |
| 10 | publications | `level` | 33 | **b** | as row 2. `test_systems_check.py:1930` *constructs* a fixture carrying `level`; it never reads one |
| 11 | publications | `outcome_potential_why` | 33 | **b** | **zero** hits in any `.py`/`.sh` under `systems/`, `scripts/`, `research/`. Named in `publication.schema.json:20, 245`; prose at `research-ledger.json:2222` and `sprint-2026-09-01/S37-BRANCH-DEBT.md:225` |
| 12 | publications | `_evidence` | 1 | **b** | zero literal `_evidence` reads; every grep hit is the substring inside `supporting_evidence` / `check_evidence_base`. Prose at `aso/fusion-junction-aso-cover-letter.md:312` |
| 13 | publications | `doi` | 1 | **b** | `systems_check.py:3686` is inside `render_evidence_base`, whose collections are `artifacts/claims/evidence/objects` — an evidence DOI, not a publication's |
| 14 | publications | `posted` | 1 | **b** | `systems_check.py:3139, 4222` use `"posted"` as a *state-name key* in glyph/weight maps, not as a field read |
| 15 | publications | `posted_by` | 1 | **b (strict)** | **zero** hits anywhere in the repository outside `systems/graph/publications.json` and `publication.schema.json:52, 104` |
| 16 | publications | `published_at_utc` | 1 | **b** | zero executable hits; prose at `aso/fusion-junction-aso-cover-letter.md:111` |
| 17 | publications | `venue` | 1 | **b** | `venue_fit.py` reads only `p.get("target_venue")` and `p["id"]` off the graph (`:610–613`); its `c["venue"]` are its own journal-catalogue rows. `systems_check.py:3524` is `render_technologies` (forecasts/technologies) |
| 18 | instruments | `closure_kind` | 32 | **b** | every read is a **route's** `closure_kind`: `systems_check.py:1056` (`SHARED_ROUTE_FIELDS`), `:4325–4327, 4346–4347, 4372`, `render_l2(r, g)` `:3087–3088`, `render_paper_strength:4456`; `priority.py:343`; `test_nr4a3_tcip_reach.py:227` |
| 19 | instruments | `file` | 32 | **a** | `systems_check.py:700` → `:714` (`check_pointers`, `[P1]`/`[P2]`) |
| 20 | instruments | `module` | 32 | **b (strict)** | **zero** field-name hits; `"module"` does not occur in `systems_check.py` at all. Every `.md` hit is the English word. Named only at `instrument.schema.json:11, 20` |
| 21 | instruments | `owner` | 32 | **b** | `_owner_blocks` keys on `file`, not `owner` — `:692` is its docstring saying so. `check_legacy_agreement:1087` lists `owner` for **blockers** only |
| 22 | lanes | `file` | 18 | **a** | `systems_check.py:700`, `:714` |
| 23 | lanes | `owner` | 18 | **b** | as row 21 |
| 24 | requirements | `confidence` | 16 | **b** | reads are forecast confidence (`:288, 295, 3454`) or route `state.confidence` (`:4348, 4373`) |
| 25 | requirements | `file` | 16 | **a** | `systems_check.py:700`, `:714` |
| 26 | requirements | `last_verified` | 16 | **b** | `systems_check.py:1910` reads document **frontmatter**; `priority.py:430` reads a route's `state.last_verified` |
| 27 | requirements | `owner` | 16 | **b** | as row 21 |
| 28 | requirements | `provenance` | 16 | **b** | as row 7 |
| 29 | requirements | `status` | 16 | **b** | every read is a route's `state.status` (`:419, 613, 4328, 4353, 986`) or frontmatter `status` (`:1840, 1876–1904`) |
| 30 | requirements | `title` | 16 | **a** | `lint_asymmetry.py:507`, `:557` (value-generic) |
| 31 | strategies | `file` | 14 | **a** | `systems_check.py:700`, `:714`. (`parser_guard.py:135–136` reads `pinned-figures.json` rows, not strategies) |
| 32 | strategies | `kind` | 14 | **b** | as row 1. `ledger_schema.py:605, 662` bucket **ledger entries** by `kind` |
| 33 | strategies | `last_verified` | 14 | **b** | as row 26 |
| 34 | strategies | `level` | 14 | **b** | as row 2 |
| 35 | strategies | `owner` | 14 | **b** | as row 21 |
| 36 | strategies | `provenance` | 14 | **b** | as row 7 |
| 37 | strategies | `running_job` | 2 | **b** | zero executable hits. Prose at `systems/AUDIT-2026-08-06-routes.md:185, 201`; `sprint-2026-09-01/S54-ROUTE-CLAIMS-AUDIT.md:99`; `S43-proposed-graph-additions.json:18` |
| 38 | blockers | `changed_on` | 1 | **b** | zero field reads (both `.py` greps are `what_changed_on_<date>` key names). Prose: a quoted JSON block at `degrader/selectivity-requirement-sizing.md:527` |
| 39 | blockers | `was` | 1 | **b** | zero hits of any kind outside the schema (`blocker.schema.json:129, 132`) and prose |
| 40 | blockers | `why` | 1 | **a** | `lint_asymmetry.py:507`, `:557` (value-generic). `systems_check.py:2008, 2014` read an **artifact-refs** entry's `why`; `:3016, 3070` are `render_l2` |

### R.4 — The two pairs with no repository mention at all `PRIMARY`

`publications/posted_by` and `instruments/module` are the strictest cases: outside `systems/graph/` and their own schema file, the field name does not occur anywhere in `systems/`, `scripts/` or `research/` — no code, no test, no document, no ledger entry. `rg 'posted_by' .` excluding graph, views, schema and the campaign directory returned **nothing**. These are the two fields the repository requires, stores (1 and 32 instances), and never mentions again.

### R.5 — What this does and does not say about W09i's blast radius `SECONDARY`

W09i's headline is that 1,547 required field instances can vanish with `--write-views` reporting success. This census refines the consequence, not the number:

- For **30 of 40 pairs**, the *only* thing standing between the field and total absence is `check_schemas` in plain mode. Nothing reads the value. Their content is unverifiable by any executable in the tree.
- For **4 pairs** (`file` in instruments, lanes, requirements, strategies) a real plain-mode gate reads them and would silently check less.
- For **3 pairs** (`routes/title`, `requirements/title`, `blockers/why`) the reader is a linter that is not wired into any gate.
- Only **3 pairs** (`modalities/revisit_trigger`, `technologies/paper_id`, `publications/kind`) are read by a consumer that is both executable and load-bearing outside `systems_check.py`.

---

## Validation evidence

**RUN** — all commands from `/home/user/Rare-cancers` (read-only) or `/tmp/claude-0/w09j/` (now deleted). Environment: Linux, `rg` 14.x, Python 3.11 `/usr/local/bin/python3`, no network.

| # | command | exit | key output |
|---|---|---|---|
| 1 | `date -u; git rev-parse HEAD; git status --porcelain` (start) | 0 | `Tue Sep 8 04:38:33 UTC 2026`; `408b676a…`; 0 lines |
| 2 | `rg -l -F 'systems/graph' -g '*.py' -g '*.sh' systems scripts research` | 0 | 69 files after excluding the campaign directory |
| 3 | `rg -l -F "graph/<coll>" -g '*.py' -g '*.sh' …` ×9 | 0 | per-collection candidate sets (instruments: **0** executables outside `systems_check.py`) |
| 4 | `python3 scan2.py` (40 pairs × their own collection's candidate set) | 0 | per-pair hit counts; 7 names with **0** hits repo-wide |
| 5 | `python3 sc.py` (map every `systems_check.py` hit line → enclosing `def`) | 0 | 40 pair→function tables |
| 6 | `python3 fn.py` (per-function `g["<coll>"]` index extraction) | 0 | e.g. `derive` → `artifacts blockers claims instruments lanes objects routes strategies technologies` (**no `modalities`**); `render_l2(r, g)` → `blockers forecasts publications technologies` |
| 7 | `sed -n` reads of 21 ambiguous line ranges in `systems_check.py` | 0 | quoted in R.2/R.3 |
| 8 | `rg -n '<name>' -g '*.py' -g '*.sh' systems scripts research` for the 9 distinctive names | 0 | `outcome_potential_why`, `posted_by`, `published_at_utc`, `running_job` → **0 lines each** |
| 9 | `sed -n '38,60p' systems/systems_check.py \| grep -o '"[a-z]*"'` | 0 | `COLLECTIONS` = 14 names incl. `instruments`, `lanes`, `requirements`, `strategies` |
| 10 | `rg -n 'lint_asymmetry' scripts/preflight.sh scripts/fast_checks.py .github` | 1 | **no output** — not wired into a gate |
| 11 | `rg -n 'posted_by' .` excl. graph/views/schema/campaign | 1 | **no output** |
| 12 | `git diff --stat 408b676a HEAD -- systems/ scripts/ research/ ':!…campaign…'` | 0 | **empty** — nothing I searched moved while I searched it |
| 13 | `rm -rf /tmp/claude-0/w09j`; `ls -d /tmp/claude-0/w09j` | 0; 2 | `No such file or directory`; free disk 18 GiB |
| 14 | `date -u; git rev-parse HEAD; git status --porcelain \| wc -l` (end) | 0 | `Tue Sep 8 04:48:12 UTC 2026`; `8a667406…`; **0** |

**PROPOSED (NOT RUN):** every executable check in the repository — I ran no test, no linter, no `systems_check.py` invocation in any mode, and no `scripts/preflight.sh`. I ran no mutation and no `--write-views`. I did not verify by execution that deleting a class-(a) field changes a gate's output; that would require the scratch-copy method W09i used and is the obvious successor. No patch, diff, gate or test was authored or proposed.

---

## Limitations

- **This is a static search, not a dynamic trace.** A consumer that reads a field through a variable key (`row[k]` in a loop over a name list), through `**kwargs`, or by serialising the whole record would not appear. I mitigated this for the largest such case — `_owner_blocks`'s any-depth `file` walk, which a naive name grep would have missed — but I cannot bound the class.
- **Collection attribution rests partly on W09i's measurement.** My filter "a `render_*` hit for an INVISIBLE pair is provably a different collection" is sound only if W09i's byte-identical-views result is sound. I did not re-run it. If that run were wrong, several `render_*` hits I rejected would need re-reading; the class-(a) rows drawn from `check_pointers`, the tests and the producers do not depend on it.
- **The candidate set is scoped to files that name the graph path.** A file that reads `systems/graph/*.json` through a helper in a third module, or by a glob assembled at runtime, is outside my set. I checked for a shared loader and found none; the repository addresses the graph by literal path or by `REPO / "systems" / "graph" / …`, and I covered both forms.
- **Class (b) versus (c) is a definitional choice, and it drives the headline.** I counted the JSON Schema `required` declaration as a non-executable mention, which makes (c) = 0. Counting the schema as an executable consumer instead — `check_schemas` does read it, generically — would make all 40 class (a) and the question vacuous. I report both readings and the strict subset (2 pairs) so the coordinator can apply either.
- **`lint_asymmetry`'s reads are value-generic**, and calling rows 8–10 class (a) on that basis is the weakest of the ten. It is stated in R.2 rather than buried.
- **No claim about whether any of these fields *should* exist.** Nothing here says a field is dead weight; `publications/outcome_potential_why` carries a portfolio judgement that a human reads (`research-ledger.json:2222`), and being unread by code is not being useless. **Nothing here bears on EMC efficacy, safety, selectivity, therapeutic window or clinical readiness.** No patient data, no wet lab, no clinical claim, no truth-grading of any repository claim.
- Measured at `408b676a`/`8a667406` only, with the intervening diff verified empty outside the campaign directory.

## Stop condition

**Set up front:** stop when all 40 pairs have been searched across `systems/`, `scripts/` and `research/` (campaign directory excluded), every non-trivial hit has been read and attributed to a collection, and each pair is classified (a)/(b)/(c) with an exact `file:line` for every (a) — or at ~40 tool calls / ~40 minutes, whichever comes first.

**MET.** 40/40 classified, 0 sampled, 0 deferred; 10 class-(a) pairs carry 14 exact citations; scratch deleted; live tree clean. Returned on meeting it, under both budgets.

## Tool-call and wall-clock count actually used

**23 tool calls** (all `Bash`; one was killed by timeout and re-run, counted). **Wall clock 04:38:33Z → 04:48:12Z ≈ 10 minutes.** Budget was ~40 calls / ~40 minutes.

## Next concrete action

**For the graph owner, one measurement and one decision, in that order.**

The measurement, which is a direct extension of this census and W09i's method: **for the four `file` pairs (instruments, lanes, requirements, strategies), delete the field on a scratch copy and count the change in plain-mode `[P1]`/`[P2]` output.** W09i measured that these deletions add only the schema `[S…]` errors — which means `check_pointers` silently verifies fewer pointers rather than complaining. Quantifying "how many pointer checks does deleting `file` from one collection switch off" turns "a gate reads it" into a number, and it is the only one of my ten class-(a) rows where the consumer is a real gate whose coverage can shrink invisibly. That is a ~30-minute scratch-copy run using W09i's exact restore discipline.

The decision, unchanged in substance from W09i and now with the consumer side filled in: for **30 of the 40 invisible pairs the schema `required` declaration is the sole reader**, so wiring `check_schemas` into `--write-views` is not a redundancy — for three quarters of this set it is the only enforcement that exists. The counter-weight W09i measured (plain mode exits 1 at HEAD on 179 committed-tree `[D…]`/`[K1]` errors from the campaign directory) still stands and still makes today the wrong day. **I have written no patch and propose none**; the mode-wiring decision is the graph owner's.

A second, smaller item worth someone's attention and not mine to act on: `research/manuscripts/lint_asymmetry.py` is a working linter with a passing test file and **no gate invocation anywhere** — not in `preflight.sh`, not in `fast_checks.py`, not in `.github/`. Whether that is deliberate is a question for its owner, not a defect I am asserting.
