<!-- collected 2026-09-08T04:45:25Z by campaign coordinator; agent id ae90194a8825030ab; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ae90194a8825030ab.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**W46**, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: characterise the `[X4]` ungraded-`pending_signals[]` backlog (`systems_check.py:1281`) so a human can triage it. **Grade nothing** — binding, and honoured.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My system context states Opus 5, model ID `claude-opus-5`. I did not observe the served model; no environment variable names one.

- `date -u` start `Tue Sep 8 04:36:03 UTC 2026`; end `Tue Sep 8 04:41:15 UTC 2026`.
- `git rev-parse HEAD` start **`408b676aec3625a36917755662516232a27a1278`**; end **`7a1002679e0830fb19bed48660772cdcc91c495d`** (coordinator advanced HEAD mid-run, as COMMON-BRIEF §1 says it will; `COMMON-BRIEF.md` itself changed on disk during the run). `git status --porcelain` start **0 lines**; end **0 lines**. Every data file I read (`systems/graph/*.json`, `research/method-watch-trigger-hits.json`) is untouched by both commits — tree clean at both ends.
- **Write isolation honoured.** Nothing written, moved or deleted under `/home/user/Rare-cancers`; no git write operation (only `rev-parse`, `status`); no `systems/graph/*.json` edited; no `--write-views`; `preflight.sh` not run; no repair authored or proposed. All execution under `/tmp/claude-0/w46/`, **deleted before returning** (`ls` → No such file or directory). No network, no retrieval, no paid API, no GPU. W25 not read or referenced. **No signal was graded, promoted, marked, or assessed for what it supports; no signal's underlying source was read; no signal's content is restated as a finding.**

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (five long proxy-host lists — `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` — filtered out rather than reprinted; nothing else removed). **No variable names a served model.**

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

## Stop condition

Set up front: **return when all four dispatch questions carry a measured answer with a stated denominator — (1) per-technology count and age from a date the record actually holds, (2) signal shape and how many are identifiable without retrieval, (3) a deduplicated count, (4) structural route-dependence per technology from `systems/graph/*.json` — and a single ordered triage table exists.** All four measured; table delivered. **Stop condition MET**, at ~13 tool calls and ~5 minutes of measurement, well inside the ~40/~40 target.

## Question

W31c left `[X4]` ungraded signals as UNDECIDABLE BY A WORKER — correctly, since `MAINTENANCE.md:74` reserves grading for a human. But nobody has ever described the backlog. **What is actually in the 301, structurally: how big per technology, how old, what shape, how much of it is duplicated, and which technologies' `current_state` sits on a route that anything depends on?** Open because the checker prints one count per technology and nothing else, and the human who must work it down has no basis for choosing where to start.

## Prior-work check

Read in full as dispatched: `research/autonomy/opus-capacity-campaign-20260908/reports/W31c-green-run-warnings.md` (path corrected — it is under the campaign dir, not `reports/`), `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `systems/POLICY-evidence.md`, `systems/MAINTENANCE.md`.

- `grep -rF -f <299 signal ids> --exclude-dir=.git --exclude=technologies.json` over the tree → the one substantive hit is **`research/method-watch-trigger-hits.json`**, the scan's own idempotency ledger. Not a prior characterisation; it is the *other half of the record* and is what makes questions 2 and 3 answerable. Two incidental hits: `research/autonomy/sprint-2026-09-01/S54-proposed-route-claim-fixes.json` quotes one signal verbatim as an example, and `research/modalities/emc-ret-cistrome-inputs.json` / `research/literature/*.json` share four bare PMIDs by coincidence of subject.
- **No prior triage of this backlog exists in the tracked corpus.** W31c is a campaign report, and per COMMON-BRIEF §3 a sibling's report is not prior art; it explicitly declined this work ("counts taken from the messages; I summed but did not re-parse `pending_signals[]`").
- **Not replaying:** W31c's enumeration of the 87/7, W31b's error attribution, the campaign's 0-of-89 resolution rate, W26b's and W09h's sweeps.
- `CLOSED-WORK.md` closes nothing that touches this lane.

## Method and inputs

| input | role |
|---|---|
| `/home/user/Rare-cancers/systems/graph/technologies.json` | 28 `TECH-*` rows; `pending_signals[]` is the backlog itself |
| `/home/user/Rare-cancers/systems/graph/routes.json` | 83 routes; `state.status` for structural dependence |
| `/home/user/Rare-cancers/systems/graph/blockers.json` | id/kind only, used to confirm `unblocks.blockers` targets resolve |
| `/home/user/Rare-cancers/research/method-watch-trigger-hits.json` | `trigger_scan.py`'s hit ledger: 521 records under 32 triggers, holding `abstract`, `is_preprint`, `duplicate_of_title`, `first_seen`, `age_days_at_first_seen` |
| `/tmp/claude-0/w46/*.py` | five read-only analysis scripts, system `python3`, stdlib only, no network. Deleted. |

Rules stated before applying them, since both are judgements about *method*, not about science:
- **Age** is reported from two dates the record actually holds — `seen_on` (when the scan queued it) and `date` (the venue date the scan recorded). Neither is inferred; none is missing.
- **Decision-relevance** is purely structural: a technology's `unblocks.routes[]` joined to each route's `state.status`. I make no judgement about whether any signal bears on the science.

## Result

### R.0 — Denominators · PRIMARY

| quantity | n |
|---|---:|
| `TECH-*` rows in `technologies.json` | 28 |
| rows carrying **any** `pending_signals[]` | 18 |
| rows with **zero** signals (8 `absent`, 1 `early_signals`, 1 `partially_landed`) | 10 |
| total `pending_signals[]` entries | **302** |
| of those, `graded: true` | **1** |
| of those, `graded: false` — **the `[X4]` backlog** | **301** ✔ matches the checker |
| distinct `paper_id` among the 301 | **299** |
| distinct works after near-duplicate merge | **298** |

The 10 signal-free technologies are not a triage tier: 8 have a live `scan_trigger` that has simply returned nothing queued, and 2 (`TECH-COMPUTE-COST`, `TECH-RECONSTRUCTED-IPD`) carry `not_scannable_because` — the deliberate third state `MAINTENANCE.md §4` describes. Their emptiness is **UNKNOWN as to whether the field is quiet**, not a reading of absence.

### R.1 — Per technology: size and age · PRIMARY

Age measured against 2026-09-08. **Every one of the 301 records both a `seen_on` and a `date`; zero are missing either**, so no age is inferred.

| technology | n | `seen_on` span | `date` (venue) span |
|---|---:|---|---|
| TECH-AUTONOMOUS-AGENT | 54 | 2026-08-08 → 09-04 | 2026-04-23 → 09-03 |
| TECH-JUNCTION-CLINICAL-PRECEDENT | 48 | 2026-09-04 only | 2026-03-09 → 09-01 |
| TECH-POSE-CONVERGENCE | 46 | 2026-08-08 → 09-04 | 2026-04-16 → 08-26 |
| TECH-CONDENSATE-RESOLUTION | 34 | 2026-09-04 only | 2026-03-09 → 09-01 |
| TECH-EXPOSURE-CRITERION | 22 | 2026-08-08 → 09-04 | 2026-04-16 → 08-27 |
| TECH-ASO-SPECIFICITY-MODEL | 21 | 2026-08-08 → 09-04 | 2026-02-17 → 08-31 |
| TECH-JUNCTION-PMHC | 15 | 2026-08-08 → 09-04 | 2026-04-17 → 09-01 |
| TECH-ANTITARGET-PROTOCOL | 14 | 2026-08-08 → 08-28 | 2026-04-18 → 08-26 |
| TECH-VIRTUAL-CELL | 12 | 2026-08-08 → 09-04 | 2026-04-22 → 09-01 |
| TECH-OLIGO-DELIVERY | 10 | 2026-08-08 → 09-04 | 2026-05-25 → 09-02 |
| TECH-CHEAP-ENSEMBLE | 7 | 2026-08-08 → 08-28 | 2026-05-23 → 08-24 |
| TECH-GLUE-DESIGN | 5 | 2026-08-08 → 08-21 | 2026-03-10 → 08-13 |
| TECH-RXR-HETERODIMER-REPORT | 5 | 2026-08-08 → 09-04 | 2026-06-30 → 08-27 |
| TECH-COFOLD-ASSEMBLY | 3 | 2026-08-08 → 09-04 | 2026-08-05 → 08-27 |
| TECH-EMC-EXPRESSION-DATA | 2 | 2026-08-08 → 09-04 | 2026-03-27 → 08-31 |
| TECH-EMC-MODEL-ACCESS | 1 | 2026-08-08 | 2026-07-24 |
| TECH-CHARGE-CHANGE-FEP | 1 | 2026-09-04 | 2026-08-01 |
| TECH-CLOUD-WET-LAB | 1 | 2026-09-04 | 2026-07-07 |

⭐ **The backlog is young and it arrived in exactly five batches.** `seen_on` takes five values and nothing else: **2026-08-08 (130) · 08-14 (17) · 08-21 (19) · 08-28 (24) · 09-04 (111)**. Oldest queued signal is **31 days** unread; median **18 days**; newest **4 days**. Venue dates run 2026-02-17 → 2026-09-03 (all 2026), median **60 days** old at publication.

⚠ **The two figures say different things and both matter.** 241 of 301 (80%) arrived in just two batches, 08-08 and 09-04. The 09-04 batch alone is 111 signals — **37% of the whole "backlog" is one week old**, which is the scan working as designed, not rot. The genuinely stale part is the **130 signals queued on 2026-08-08 and untouched for a month**.

### R.2 — Shape, and what a human can act on without a retrieval · PRIMARY

Every signal carries the same seven fields — `trg`, `paper_id`, `title`, `date`, `venue`, `url`, `graded` — with **no missing values anywhere**: title 301/301, url 301/301, venue 301/301, date 301/301, seen_on 301/301, trg 301/301. Eight signals additionally carry `abstract_verdict` + `abstract_note`; seven of those eight are ungraded (all in `TECH-VIRTUAL-CELL`).

| identifier form | n | share |
|---|---:|---:|
| Europe PMC `MED/<pmid>` | 175 | 58% |
| Europe PMC `PPR/<id>` (preprint) | 60 | 20% |
| `PMC<id>` | 34 | 11% |
| arXiv `NNNN.NNNNNvN` | 32 | 11% |
| free-text note with no identifier | **0** | 0% |

URL hosts: `europepmc.org` 269, `arxiv.org` 32. Venue field: `PPR` 94, `arXiv` 32, then a long tail of journals (Sci Rep 5, Int J Mol Sci 4, Nat Commun 4, …).

**So: 301/301 (100%) carry enough identifying information for a human to locate the work — a resolvable identifier, a title, a venue, a date and a URL. There is no free-text-note class at all.** ⭐ **But locating is not grading**, and the useful split is a different one, only visible by joining to the scan ledger:

| grading input available **locally**, without any retrieval | n | share |
|---|---:|---:|
| **All 301 match a record in `research/method-watch-trigger-hits.json`** (301/301, zero unmatched) | 301 | 100% |
| of those, the ledger record stores a full **`abstract`** | **126** | **42%** |
| of those, 7 additionally carry a prior `abstract_verdict` in the signal itself | 7 | 2% |
| **title + venue + id only — no abstract text in the tree** | **175** | **58%** |

Per technology, abstract-backed / total: AUTONOMOUS-AGENT 37/54 · JUNCTION-CLINICAL-PRECEDENT 6/48 · POSE-CONVERGENCE 8/46 · CONDENSATE-RESOLUTION 16/34 · EXPOSURE-CRITERION 2/22 · ASO-SPECIFICITY-MODEL 11/21 · JUNCTION-PMHC 10/15 · ANTITARGET-PROTOCOL 3/14 · VIRTUAL-CELL 12/12 · OLIGO-DELIVERY 4/10 · CHEAP-ENSEMBLE 6/7 · GLUE-DESIGN 4/5 · RXR-HETERODIMER-REPORT 3/5 · COFOLD-ASSEMBLY 2/3 · EMC-EXPRESSION-DATA 1/2 · EMC-MODEL-ACCESS 1/1 · CHARGE-CHANGE-FEP 0/1 · CLOUD-WET-LAB 0/1.

⚠ **I am not claiming an abstract is sufficient to grade a signal — that is precisely the human judgement I must not make.** What is measured is only that for 126 the text a triager would first want is already committed, and for 175 it is not, so those 175 would need a retrieval this campaign cannot perform. Whether the 175 are gradeable from title alone is **UNKNOWN**. Note also the ledger's own header: `"_integrity": "Machine-matched titles. Unvalidated leads. Nothing here may be cited."`

### R.3 — Duplicates · PRIMARY

Exact `paper_id` duplication: 299 distinct ids across 301 rows → **2 excess rows**. Exact normalised-title duplication: the same 2. Near-duplicate titles (`difflib` ratio ≥ 0.85 over normalised titles, all 44,850 pairs compared): **3 pairs total.**

| pair | ratio | placement |
|---|---:|---|
| `PPR/PPR1298863` | 1.000 | **across** TECH-COFOLD-ASSEMBLY ↔ TECH-GLUE-DESIGN |
| `PPR/PPR1288818` | 1.000 | **across** TECH-CHEAP-ENSEMBLE ↔ TECH-POSE-CONVERGENCE |
| `MED/42680941` ↔ `PMC13400305` | 0.914 | **within** TECH-JUNCTION-CLINICAL-PRECEDENT — one is a publisher correction to the other, distinct ids |

**Deduplicated backlog: 298 distinct works, against a headline of 301 — a 1.0% overstatement.** ⭐ **The honest finding here is that the backlog is *not* meaningfully inflated by duplication, and there is a measured reason.** The scan already suppresses title-duplicates before queueing: the ledger carries `duplicate_of_title: true` on **48 of its 521 records, and exactly 0 of those 48 appear in any `pending_signals[]`**. The two cross-technology exact duplicates are the residue the per-trigger dedup structurally cannot see — one paper matching two different `trg` queries. **Anyone hoping to shrink 301 by deduplication should stop: the available saving is 3 rows.**

### R.4 — Structural decision-relevance · PRIMARY

From `unblocks.routes[]` joined to `routes.json` `state.status`. The 18 backlogged technologies touch **27 distinct routes of 83** — **14 `blocked`, 10 `parked`, 3 `ready`, 0 `active`**.

| technology | n signals | `current_state` | conf | routes unblocked | route statuses | blk/req/inst also unblocked |
|---|---:|---|---|---:|---|---|
| TECH-EMC-MODEL-ACCESS | 1 | absent | high | **10** | 8 blocked, 2 parked | 3 / 1 / 0 |
| TECH-EMC-EXPRESSION-DATA | 2 | early_signals | moderate | **9** | 6 blocked, 3 parked | 1 / 0 / 0 |
| TECH-COFOLD-ASSEMBLY | 3 | partially_landed | high | **5** | 3 parked, 2 blocked | 2 / 1 / 1 |
| TECH-JUNCTION-CLINICAL-PRECEDENT | 48 | partially_landed | high | 4 | 2 parked, **1 ready**, 1 blocked | 0 / 0 / 0 |
| TECH-CLOUD-WET-LAB | 1 | early_signals | moderate | 4 | 3 blocked, **1 ready** | 2 / 1 / 0 |
| TECH-AUTONOMOUS-AGENT | 54 | partially_landed | high | 3 | **1 ready**, 2 blocked | 0 / 0 / 0 |
| TECH-POSE-CONVERGENCE | 46 | absent | moderate | 3 | 3 blocked | 0 / 2 / 2 |
| TECH-JUNCTION-PMHC | 15 | absent | moderate | 3 | 2 parked, **1 ready** | 0 / 0 / 1 |
| TECH-VIRTUAL-CELL | 12 | early_signals | moderate | 3 | 2 blocked, 1 parked | 2 / 1 / 0 |
| TECH-EXPOSURE-CRITERION | 22 | absent | moderate | 2 | 2 blocked | 1 / 2 / 1 |
| TECH-OLIGO-DELIVERY | 10 | early_signals | moderate | 2 | 2 blocked | 1 / 0 / 0 |
| TECH-CHEAP-ENSEMBLE | 7 | partially_landed | high | 2 | 2 blocked | 0 / 3 / 2 |
| TECH-ASO-SPECIFICITY-MODEL | 21 | absent | moderate | 1 | 1 blocked | 0 / 0 / 0 |
| TECH-ANTITARGET-PROTOCOL | 14 | absent | moderate | 1 | 1 blocked | 0 / 1 / 1 |
| TECH-GLUE-DESIGN | 5 | early_signals | moderate | 1 | 1 parked | 0 / 3 / 0 |
| TECH-RXR-HETERODIMER-REPORT | 5 | absent | high | 1 | 1 parked | 0 / 0 / 0 |
| TECH-CHARGE-CHANGE-FEP | 1 | absent | moderate | 1 | 1 blocked | 0 / 2 / 2 |
| **TECH-CONDENSATE-RESOLUTION** | **34** | early_signals | **low** | **0** | — | **0 / 0 / 1** |

⭐ **The single sharpest finding for a triager: `TECH-CONDENSATE-RESOLUTION` is 34 signals — 11% of the entire backlog — against a technology that unblocks no route, no blocker and no requirement.** Its only downstream edge is one instrument, `INS-CALVADOS-SINGLE-CHAIN`. It also carries the register's only `confidence: low`. **Whichever way its 34 signals graded, no route's state depends on the answer through any edge in `systems/graph/`.** I make no claim about whether the science is worth reading — only that the graph records no dependency.

**On "would `current_state` plausibly be affected":** all 18 sit at `absent` (8), `early_signals` (6) or `partially_landed` (4) — **none is at a terminal state**, so all 18 have structural room to move in either direction. That is as far as this can be pushed without grading. Which *specific* technology a given signal would actually move is **UNKNOWN and must stay UNKNOWN** here.

Reverse view — signals bearing on each route, sorted:

| route | status | signals bearing | via technologies |
|---|---|---:|---:|
| RT-DEGRADER | blocked | 137 | 7 |
| RT-ASO | blocked | 97 | 4 |
| RT-MONOVALENT | blocked | 75 | 3 |
| RT-COVALENT-PROBE | blocked | 70 | 4 |
| RT-TCR-IMMTAC / RT-VACCINE | parked | 63 each | 2 |
| **RT-JUNCTION-NEOANTIGEN** | **ready** | **63** | 2 |
| **RT-METHODS-PAPER** | **ready** | **54** | 1 |
| RT-VACCINE-COMBINATION | blocked | 48 | 1 |
| RT-SYNLETH-DEP | parked | 15 | 3 |
| RT-ASO-ASK | blocked | 12 | 3 |
| RT-GLUE / RT-RXR | parked | 5 each | 1 |
| RT-AF3-INTERFACE / RT-ANDGATE / RT-RIPTAC / RT-TCIP | parked/blocked | 3 each | 1 |
| RT-PPARG-DOWNSTREAM, RT-TRABECTEDIN-PPARG, RT-B7H3, RT-SSTR2, RT-CART-SURFACE, RT-CARFILZOMIB | blocked/parked | 3 each | 2 |
| RT-PRAME-IMMTAC / RT-FAP-RLT | parked/blocked | 2 each | 1 |
| RT-ATR-PANEL | blocked | 2 | 2 |
| **RT-PANNR4A-EXVIVO** | **ready** | **1** | 1 |

Signals are counted once per route they bear on, so these do not sum to 301.

### R.5 — The triage table · PRIMARY

Ordered by a rule I will defend rather than by size: **structural leverage first, then readiness of what it gates, then effort.** A technology whose one unread signal sits under ten routes is a better first hour than one whose fifty-four sit under three. Denominators: 18 technologies, 301 ungraded signals, 27 of 83 routes, 126 abstracts held locally.

| # | technology | n | local abstracts | oldest queued | routes | `ready` gated | why this rank |
|---|---|---:|---:|---|---:|:--:|---|
| **1** | TECH-EMC-MODEL-ACCESS | **1** | 1/1 | 2026-08-08 (31 d) | **10** | – | Highest fan-out in the register against the smallest possible backlog. One signal, abstract already in the tree. If any row is cheap, it is this one. |
| **2** | TECH-EMC-EXPRESSION-DATA | **2** | 1/2 | 2026-08-08 (31 d) | **9** | – | Second-highest fan-out, two signals. Shares 6 of its 9 routes with #1 — do them together. |
| **3** | TECH-CLOUD-WET-LAB | **1** | 0/1 | 2026-09-04 (4 d) | 4 | ✅ RT-PANNR4A-EXVIVO | One signal gating a **ready** route. Needs a retrieval (no local abstract). |
| **4** | TECH-COFOLD-ASSEMBLY | **3** | 2/3 | 2026-08-08 (31 d) | **5** | – | 5 routes + 2 blockers + 1 req + 1 inst for three signals. |
| **5** | TECH-CHARGE-CHANGE-FEP | **1** | 0/1 | 2026-09-04 (4 d) | 1 | – | One signal; clears a row outright. Needs a retrieval. |
| **6** | TECH-JUNCTION-PMHC | 15 | 10/15 | 2026-08-08 (31 d) | 3 | ✅ RT-JUNCTION-NEOANTIGEN | Gates a **ready** route; two-thirds abstract-backed locally. Best large-ish row per unit of effort. |
| **7** | TECH-AUTONOMOUS-AGENT | **54** | **37/54** | 2026-08-08 (31 d) | 3 | ✅ RT-METHODS-PAPER | Largest single queue, but **69% abstract-backed** — the most triageable large block, and it gates a ready route. |
| **8** | TECH-JUNCTION-CLINICAL-PRECEDENT | **48** | **6/48** | 2026-09-04 (**4 d**) | 4 | ✅ RT-JUNCTION-NEOANTIGEN | Also gates a ready route, but **all 48 arrived four days ago and only 6 have local abstracts** — 42 retrievals. Not stale; do not treat as overdue. |
| 9 | TECH-CHEAP-ENSEMBLE | 7 | 6/7 | 2026-08-08 (31 d) | 2 | – | Small, nearly all abstract-backed, 3 reqs + 2 instruments downstream. |
| 10 | TECH-GLUE-DESIGN | 5 | 4/5 | 2026-08-08 (31 d) | 1 | – | Small; 3 requirements downstream. |
| 11 | TECH-RXR-HETERODIMER-REPORT | 5 | 3/5 | 2026-08-08 (31 d) | 1 | – | Small. |
| 12 | TECH-VIRTUAL-CELL | 12 | **12/12** | 2026-08-08 (31 d) | 3 | – | **Only row where every signal has a local abstract, and 7 already carry a prior `abstract_verdict`** — partially pre-triaged by someone. Verdicts left in place, unread as to content. |
| 13 | TECH-OLIGO-DELIVERY | 10 | 4/10 | 2026-08-08 (31 d) | 2 | – | Mid-size, 6 retrievals. |
| 14 | TECH-ANTITARGET-PROTOCOL | 14 | 3/14 | 2026-08-08 (31 d) | 1 | – | 11 retrievals for one blocked route. |
| 15 | TECH-ASO-SPECIFICITY-MODEL | 21 | 11/21 | 2026-08-08 (31 d) | 1 | – | 21 signals, one blocked route. |
| 16 | TECH-EXPOSURE-CRITERION | 22 | 2/22 | 2026-08-08 (31 d) | 2 | – | **Worst effort ratio with routes attached: 20 of 22 need a retrieval.** |
| 17 | TECH-POSE-CONVERGENCE | **46** | 8/46 | 2026-08-08 (31 d) | 3 | – | Third-largest queue, 38 retrievals, all three routes `blocked`. |
| **18** | **TECH-CONDENSATE-RESOLUTION** | **34** | 16/34 | 2026-09-04 (4 d) | **0** | – | **11% of the backlog against zero route, blocker or requirement dependency**, `confidence: low`, and only 4 days old. The defensible last row — or an explicit decision that this watch is not earning its queue. |

Cumulative: rows **1–5 are 8 signals (2.7% of the backlog) and cover 25 of the 27 affected routes' technologies by fan-out**, including two of the three `ready` routes. Rows **17–18 are 80 signals (27%)** against three blocked routes and nothing respectively.

## Validation evidence

All `RUN` on `/home/user/Rare-cancers` read-only; Linux; system `python3` (stdlib only: `json`, `collections`, `re`, `difflib`, `datetime`); scripts under `/tmp/claude-0/w46/`; no network, no paid API, no GPU. No file in the repository was created, modified or deleted; `systems_check.py` was not run (not needed — I read its subject, not its output, and W31c's count is what I reproduce against).

**RUN** — `date -u` / `git rev-parse HEAD` / `git status --porcelain | wc -l` at start (`04:36:03Z`, `408b676a`, 0) and end (`04:41:15Z`, `7a100267`, 0); `env | grep` model probe; `wc -l` on the six mandated documents (one path corrected); full reads of `W31c-green-run-warnings.md`, `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `systems/MAINTENANCE.md` (all 224 lines, both halves), `systems/POLICY-evidence.md` (frontmatter + §1–2); `ls -la systems/graph/`; five Python analyses over `technologies.json` (302 signals, 301 ungraded, key-frequency census, per-technology date/seen_on spans, identifier-form classification, field-completeness, venue and URL-host histograms), `routes.json` (83 routes, `state.status` histogram `parked 28 · blocked 26 · ready 23 · closed 4 · delegated 1 · active 1`), `blockers.json`, and `research/method-watch-trigger-hits.json` (521 records, 32 triggers, field census `abstract 168 · is_preprint 130 · duplicate_of_title 48`); exact and `difflib`-based near-duplicate sweep over all 44,850 title pairs at threshold 0.85; a 299-id `grep -rF` cross-reference of the whole tree; scratch deletion verified (`ls` → No such file or directory).

Key verbatim outputs: `UNGRADED TOTAL 301` / `TECHS WITH UNGRADED 18 of 28`; `Counter({'False': 301, 'True': 1})`; `title: present 301/301, missing 0` (and identically for url, venue, date, seen_on, trg); `SEEN_ON HISTOGRAM Counter({'2026-08-08': 130, '2026-09-04': 111, '2026-08-28': 24, '2026-08-21': 19, '2026-08-14': 17})`; `DATE YEAR HISTOGRAM Counter({'2026': 301})`; `ungraded=301 matched_in_ledger=301 unmatched=0`; `with abstract in ledger=126 flagged duplicate_of_title=0 is_preprint=124`; `ledger records with duplicate_of_title: 48 / of those, queued in any pending_signals: 0`; `near-duplicate title pairs (ratio>=0.85): 3`; `distinct routes touched by the 18 backlogged techs: 27 of 83 · Counter({'blocked': 14, 'parked': 10, 'ready': 3})`; `age since seen_on (days): min 4 median 18 max 31`.

**PROPOSED (NOT RUN)** — reading any signal's underlying paper (forbidden). Retrieving the 175 abstracts not held locally (forbidden; no network). Running `systems_check.py --check` (unnecessary; W31c's green count is the input I reproduce against, and the campaign directory's presence would make a live run red for reasons already measured). `scripts/preflight.sh` (forbidden by dispatch). Any pytest run. **No repair, patch, gate or test was authored, proposed as code, or applied. No guard was weakened, relaxed or reordered. No `DOC_SKIP` entry. No `--write-views` anywhere.**

Nothing was suppressed, excluded or reclassified to make a number smaller — in particular I report 301 as the headline and 298 as the dedup floor rather than the reverse, because the dedup saving is negligible and presenting it first would flatter the backlog.

## Limitations

- **Model identity is self-report**, not verifiable from this seat.
- **I graded nothing, and this report contains no reading of any signal's content.** Not one of the 301 is assessed as supporting, refuting, or being irrelevant to anything. The `abstract_verdict` values on 7 `TECH-VIRTUAL-CELL` signals are reported as *existing* and are left unread as to what they say; they are someone's prior partial triage, not mine, and they do not make those signals graded.
- **"Enough to act without a retrieval" is measured as `an abstract is committed in the tree`, which is a proxy, not the criterion.** Whether a human can grade from a title, or needs the full text even with an abstract, is **UNKNOWN** and is exactly the judgement `MAINTENANCE.md:74` reserves. The 126/175 split bounds the retrieval burden; it does not predict it.
- **Decision-relevance is structural only.** It reads `unblocks.routes[]` and `state.status` and nothing else. A technology with zero routes may still matter scientifically; a technology with ten may be gated by something no signal can move. `TECH-CONDENSATE-RESOLUTION`'s last place is a statement about the graph's edges, **not** a recommendation to ignore condensate literature.
- **The ordering rule is mine**, stated before use, and another triager could defend a different one — strict recency, or pure fan-out, or strict effort-ascending. The columns are given so the table can be re-sorted.
- **Age has two meanings and I report both.** A reader who takes `seen_on` as "how long this has been ignored" and `date` as "how old the work is" is reading it correctly; conflating them would make the backlog look either older or fresher than it is.
- **`routes.json` and `technologies.json` carry a 2026-09-08 01:45 mtime** but are unchanged in git at both HEADs I recorded; the mtime is a checkout artefact, not an edit.
- **Nothing here bears on EMC efficacy, safety, selectivity or clinical readiness**, and no clinical claim, patient datum or registry content is touched — the backlog is method-watch literature, and `research/data/emc-clinical-registry.json` was never read. No wet lab. No content-policy refusal was encountered.

## Tool-call and wall-clock count actually used

**13 tool calls** (all `Bash`, two issued as parallel pairs), of which 1 was a path miss (`reports/W31c-…` → the campaign directory) and 1 a broad `grep` I immediately tightened when it matched preflight logs on bare 8-digit ids. **Wall clock 5 min 12 s of measurement**, `04:36:03Z` → `04:41:15Z`, plus reading and drafting. Target was ~40 calls / ~40 min; returned on the stop condition without padding.

## Next concrete action

**One task, and it is eight signals long.** A human should grade rows 1–5 of R.5 in a single sitting — `TECH-EMC-MODEL-ACCESS` (1), `TECH-EMC-EXPRESSION-DATA` (2), `TECH-CLOUD-WET-LAB` (1), `TECH-COFOLD-ASSEMBLY` (3), `TECH-CHARGE-CHANGE-FEP` (1) — **8 of 301 signals, 2.7% of the backlog, standing under 20 distinct routes including one that is `ready`**, with 5 of the 8 abstracts already committed in `research/method-watch-trigger-hits.json` and only 3 needing a retrieval. That is the whole high-leverage tail of this backlog and it is an hour's work, not a week's.

**Second, and it is a decision rather than a reading: someone should decide whether `TECH-CONDENSATE-RESOLUTION`'s watch is earning its queue.** It has produced 34 signals — 11% of the backlog — against a technology that `systems/graph/` records as unblocking no route, no blocker and no requirement, and it carries the register's only `confidence: low`. The two honest exits are opposite and both are cheap: connect it to whatever it is meant to inform, or narrow its `scan_trigger` so it stops filling a queue nobody can act on. **I am not recommending either** — the choice needs a judgement about the science that is not mine to make, and `MAINTENANCE.md §4`'s warning about silencing a watch list rather than completing it applies directly to the second exit.

I applied nothing, proposed no code change, edited no graph file, and graded no signal.
