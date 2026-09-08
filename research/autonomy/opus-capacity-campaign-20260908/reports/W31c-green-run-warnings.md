<!-- collected 2026-09-08T03:47:01Z by campaign coordinator; agent id acc3b114e8fcbf673; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-acc3b114e8fcbf673.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**W31c**, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: the content of the *green* `systems_check` run — the 87 WARN and 7 INFO W31b measured but explicitly did not examine.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My system context states Opus 5, model ID `claude-opus-5`. I did not observe the served model; no environment variable names one. Coordinator must extract the real per-child runtime model from the transcript.

- `date -u` start `Tue Sep 8 03:40:45 UTC 2026`; end `Tue Sep 8 03:43:41 UTC 2026`.
- `git rev-parse HEAD` start **`5ae0fa04ff9516ac8f820381079d644a094f4a77`**; end **`5ae0fa04…`** — unchanged. `git status --porcelain` start **0 lines**; end **0 lines**.
- **Write isolation honoured.** Nothing written, moved or deleted under `/home/user/Rare-cancers`; no git write operation (only `rev-parse`, `status`, `ls-files`); `preflight.sh` not run; no `systems/graph/*.json` edited; no `DOC_SKIP` added; no `--write-views` anywhere; no repair authored or proposed. All execution under `/tmp/claude-0/w31c*` on a `tar --exclude=./.git` copy, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w31c-pycache`. **Scratch deleted before returning** (`RM_EXIT=0`; `ls` → no such file; `/` 49% used, 20G free). No network, no paid API, no GPU. W25 not read or referenced.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`. Five long proxy-host lists (`no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS`) filtered out rather than reprinted; nothing else removed. **No variable names a served model.**

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

Set up front: **return when (1) every WARN/INFO code in the green run is defined from its raise site with `file:line` and a verbatim message, (2) all 87 WARN and 7 INFO are classified hygiene vs substantive with an honest denominator, and (3) each substantive warning carries a stated decision procedure and an explicit yes/no on whether it touches the clinical registry or a pinned quantity.** All three measured. **Stop condition MET.**

## Question

W31b's green counterfactual still carried 87 WARN and 7 INFO and left them unexamined. **What are they, and which of them are claims about the graph's scientific content rather than documentation hygiene?**

## Prior-work check

Read in full as dispatched: `COMMON-BRIEF.md` (corrected 03:36Z version, including the "Known, measured, and NOT worth rediscovering" section), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W31b-systems-check-error-attribution.md`, `systems/POLICY-evidence.md`.

- `rg -n -i 'systems_check.*WARN|87 WARN|\[X4\]|\[L4\]|\[Q4\]' --glob '!.git' --glob '!research/autonomy/opus-capacity-campaign-20260908/**' --glob '!systems/systems_check.py' -l` → 17 tracked files. `git ls-files | rg -i 'warn|triage|systems.check'` → `systems/systems_check.py`, `systems/tests/test_systems_check.py`, `scripts/triage-literature.mjs`, plus two campaign reports.
- ⭐ **The one real prior-art hit, and it is partly wrong.** `research/autonomy/sprint-2026-09-01/S52-BLOCKER-PRECISION.md:349` records the verbatim verdict line `systems_check: 604 objects across 15 collections · 0 ERROR · 87 WARN · 7 INFO` and dismisses them as *"pre-existing and unrelated (X4 ungraded scan signals, D5 unverified documents, K3 dead pointers in S43's memo, B9 over-claiming triggers)."* That four-code list is **not** the population: **`[K3]` does not appear in my run at all**, and the list omits `[L4]` (47 of 87, the single largest code), `[Q4]` (8), `[B5]` (6), `[L5]` (3) and `[B3]`. So the 87 has been seen before and characterised loosely; it has not been enumerated. I am not replaying S52's blocker edit.
- **Not re-derived, per dispatch:** `reports/W26b-remaining-graph-files-sweep.md` (17 graph files, absence-claim truth) and `reports/W09h-successor.md` (schema-field enforcement / consumption census). Where my findings touch files those workers swept, I say so below and take their results as given.
- **Not replayed:** W31b's error attribution. I reproduced only the counterfactual run itself, from scratch, as instructed — I did not inherit the number.

## Method and inputs

| input | role |
|---|---|
| `/home/user/Rare-cancers` @ `5ae0fa04` | tree under test, read-only |
| `/tmp/claude-0/w31c/` | `tar --exclude=./.git` copy (613M) — the only place anything executed |
| `/tmp/claude-0/w31c-campaign-backup/` | campaign dir moved **outside the scan root** (W31b's recorded trap) |
| `systems/systems_check.py` | the checker; raise sites read at the lines tabulated in R.2 |
| `systems/graph/*.json`, `research/manuscripts/emc-systems-map.json`, `research/manuscripts/pinned-figures.json` | read-only, to decide individual warnings |

Classification rule, stated before I applied it: a finding is **hygiene** if closing it changes only how a document or registry is *annotated*; it is **substantive** if it asserts something about the model's content — a stale cross-reference, an unresolved pointer, or a claim about what the program can currently show.

## Result

### R.1 — Counterfactual reproduced independently · PRIMARY

```
$ cd /tmp/claude-0/w31c && python3 systems/systems_check.py --check
systems_check: 620 objects across 15 collections · 189 ERROR · 220 WARN · 7 INFO      FULL_EXIT=1

$ mv research/autonomy/opus-capacity-campaign-20260908 /tmp/claude-0/w31c-campaign-backup
$ python3 systems/systems_check.py --check
systems_check: 620 objects across 15 collections · 0 ERROR · 87 WARN · 7 INFO         GREEN_EXIT=0
```

Line counts on the green output: `grep -c '^ERROR'` → **0**, `'^WARN'` → **87**, `'^INFO'` → **7**. W31b's green figure reproduces exactly at a later HEAD. (The red figure has moved on as predicted: 172 → **189** in nine minutes.)

⭐ **And the WARN count is stable in a way the ERROR count is not.** S52 measured `0 ERROR · 87 WARN · 7 INFO` at **604** objects on a 2026-09-01 sprint HEAD; I measure `0 ERROR · 87 WARN · 7 INFO` at **620** objects a week later. The error baseline grows ~1.9/min with campaign progress; the warning population has held at 87 across 16 added graph objects.

### R.2 — Every code the green run emits, from its raise site · PRIMARY

| sev | code | raise site | what raises it | representative message (verbatim from my green run) | n |
|---|---|---|---|---|---:|
| WARN | **L4** | `systems_check.py:1100` | An id present in `systems/graph/{routes,blockers,instruments}.json` and absent from the legacy registry `research/manuscripts/emc-systems-map.json` | `routes/RT-POLQ is new in the graph and absent from the legacy registry (expected while the legacy file is still hand-maintained)` | 47 |
| WARN | **X4** | `:1281` | A `TECH-*` row carrying `pending_signals[]` entries with `graded` falsy | `TECH-AUTONOMOUS-AGENT has 54 UNGRADED scan signal(s) — a human must read them and either promote to \`evidence\` or mark graded; the scan deliberately cannot change \`current_state\` itself` | 18 |
| WARN | **X4** | `:2425` | `relations.json` declares an edge `asserted: true` and no row in the owning collection carries that key | `relations.json declares \`modalities.parent\` as an asserted edge and no row in modalities.json carries it — either the edge was removed and this entry is stale, or it is derived and mis-declared` | 1 |
| WARN | **Q4** | `:1036` | A requirement whose `verified_by[]` instruments are **all** non-usable, where `usable` is *derived* at `:398-410` through `inherits_limits_from` against `NON_SUPPORTING_CONTROL = {"fails","none","inconclusive","mixed"}` | `R1 has instruments but NONE has returned a usable answer -- V13 (its control FAILED), V14 (it has NO control), V15 (its control was MIXED -- partly, which is not a pass). That is a different and more actionable failure than having none` | 8 |
| WARN | **B5** | `:614` | A route with `state.status == ready` whose publication endpoint is `unwritten` or `outlined` | `RT-IPD-SURVIVAL is ready and its endpoint PUB-IPD-SURVIVAL is unwritten — nothing blocks this paper except writing it` | 6 |
| WARN | **L5** | `:1781` | An `objects`/`evidence`/`artifacts` row with empty `cited_by` (claims deliberately excluded — see the `⛔` note at `:1758`) | `4 artifacts at L5 are cited by no route, instrument, lane or claim … ART-ATM-STATUS-ATRI, ART-GSE28866-TUMOUR-VS-NORMAL, ART-PUBLISHED-WARHEAD-REGISTRY, ART-WETLAB-CONTRACTING-COSTS` | 3 |
| WARN | **Q3** | `:1024` | A requirement with no instrument whose `coverage_gap` maps to severity `WARN` in `COVERAGE_GAPS` | `R6 has NO instrument at all -- nothing built yet, and it could be built in this program. ΔG_open is computable … \`authorization: needs_decision\` because it is a GPU spend, not because the method is missing.` | 1 |
| WARN | **D5** | `:1922` | Count of documents with `last_verified: unverified`, bucketed by the `depends_on` map built at `:1845-1849` from `pinned-figures.json` `targets` and the project instructions | `164 document(s) carry \`last_verified: unverified\` … ⭐ **1 of them are LOAD-BEARING** … research/manuscripts/dependency/emc-atr-vulnerability-assessment.md` | 1 |
| WARN | **B9** | `:916` | Trigger/technology blocker disagreements **exactly equal** to `TRIGGER_BLOCKER_BASELINE = 12` (`:859`); above → ERROR at `:908`, below → INFO at `:913` | `12 trigger(s) claim a blocker their technology does not unblock. Each is either a missing technology edge or an over-claiming trigger; the count is the finding and is meant to fall` | 1 |
| WARN | **B3** | `:642` | A blocker that is not `permanent` and whose `inherited_by` is empty | `BLK-NO-FIELD-ATTENTION-MEASUREMENT holds down no route -- it may be retired or mis-scoped` | 1 |
| INFO | **B6** | `:618` | Unconditional publication-endpoint census | `33 publication endpoint(s) for 83 routes: 30 with a document, 3 unwritten` | 1 |
| INFO | **B7** | `:626` | Documents declaring `level: L3` that no publication points at | `231 document(s) declare level L3 and are the endpoint of no route — expected, most are memos, plans and red-teams rather than deliverables: …` | 1 |
| INFO | **Q3** | `:1029` | Same as WARN-Q3 but the `coverage_gap` maps to severity INFO — a stated scope boundary, *"a FINDING, not a defect"* | `R4 has no instrument -- no instrument can be built here -- CLAUDE.md §5, no wet lab` | 2 |
| INFO | **D11** | `:1513` | Unconditional hierarchy census, deliberately never pinned to a file | `hierarchy census (documents, by declared \`level\`): L0 8 · L1 4 · L3 257 · L4 97 · L5 3 · cross-cutting 1 · «absent» 16 · — 40 …` | 1 |
| INFO | **K0** | `:2331` | Unconditional link-checker run count — INFO by an explicit 2026-08-05 decision at `:2325`, *"a link checker silently checking ZERO links is the fail-open shape this repository keeps paying for"* | `relative links checked: 5552 (+1010 anchors), broken: 0 — no grandfather list exists; a broken link is an error` | 1 |
| INFO | **K1** | `:2147` | A cited-but-absent artifact whose owning lane derives `withdrawn` **and** every citing document is in the lane's `withdrawn_in[]` | `\`valb-triangle-chem.json\` is absent and LANE-9 derives \`withdrawn\`; all 2 document(s) naming it record the withdrawal (…). Closed, not pending` | 1 |

87 WARN + 7 INFO, fully accounted.

### R.3 — Hygiene vs substantive · PRIMARY

| class | n WARN | n INFO | codes |
|---|---:|---:|---|
| **Hygiene** — migration lag, a census that always prints, an annotation queue | **47** | **5** | L4 47; B6, B7, D11, K0, K1 |
| **Substantive** — a claim about the graph's content, a stale cross-reference, an unresolved pointer | **40** | **2** | X4 19, Q4 8, B5 6, L5 3, Q3 1, D5 1, B9 1, B3 1; Q3-INFO 2 |

**Hygiene, and why.**
- **L4 × 47** is pure one-directional migration lag, and I decided it rather than assuming it: `routes` legacy 40 / graph 83 / **graph-only 43 / legacy-only 0**; `blockers` 17 / 21 / **4 / 0**; `instruments` 32 / 32 / **0 / 0**. 43 + 4 = **exactly 47**. The graph is a strict superset of the hand-maintained legacy file in every compared collection, so no L4 row can be a disagreement — the disagreement direction is `[L2]`/`[L3]` and both are zero. Closing L4 is a reprojection of a file the checker's own docstring (`:1085`) says nothing compares.
- **B6, D11, K0** print unconditionally and are censuses by design; `K0` reports `broken: 0` over 5,552 links + 1,010 anchors. **B7** is self-labelled *"expected"*. **K1-INFO** is a closed finding reported as closed.

**Substantive, one line each on what it asserts.**
- **X4 `modalities.parent`** — the register of edges claims an edge the model does not have.
- **X4 × 18 ungraded signals — 301 signals total** across 18 technologies (largest: `TECH-AUTONOMOUS-AGENT` 54, `TECH-JUNCTION-CLINICAL-PRECEDENT` 48, `TECH-POSE-CONVERGENCE` 46). This is a real unread-evidence backlog, deliberately un-actionable by machine (`MAINTENANCE.md:74`: *"Nothing may change a status by itself"*).
- **Q4 × 8 + Q3 × 3** — the requirement register's coverage state. Recomputed with the checker's own derivation: **11 of 32 instruments are `usable`; of 16 requirements, 4 have ≥1 usable instrument, 8 have instruments but none usable, 4 have no instrument.** ⚠ **A raw read of `instruments.json` gives 0 usable and 12 Q4 — wrong, because `usable` is *derived* at `:398-410` and is not a stored field.** I made that error first and am recording it, since anyone auditing this register from the JSON alone will make it too.
- **B5 × 6** — 6 ready routes against **3 distinct** endpoints (`PUB-CARE-DELIVERY` accounts for 4). All six carry `why_not_written: None`.
- **L5 × 3** — 6 orphan rows (1 object `OBJ-RES-C166`, 1 evidence `EV-LI-GONG-2026`, 4 artifacts), each confirmed present in its register.
- **D5** — 164 unverified documents, 1 load-bearing.
- **B9 × 12, B3 × 1** — trigger/blocker structure.

### R.4 — What it would take to decide each substantive warning · PRIMARY

| warning | decision procedure | verdict I could reach here |
|---|---|---|
| X4 `modalities.parent` | one command | **DECIDED — the warning is REAL.** `grep -c '"parent"' systems/graph/modalities.json` → **0**, while `relations.json:404-411` declares `parent` `"on": ["modalities"], "asserted": true`. A register of edges names an edge zero rows carry. Its `why` text is a live design rule ("A sub-form refining a broader class… used only where the sub-form's EMC verdict DIFFERS"), so the honest reading is a rule declared and never instantiated, not a deletion the register missed. ⚠ **`modalities.json` and `relations.json` are both in W26b's 17-file sweep and `relations.json` is in W09h's field census — neither found this, because their axes were clause truth and field consumption, not register-vs-model agreement. I do not re-derive their findings.** |
| X4 ungraded × 18 | human reading of 301 `pending_signals[]` entries, one at a time; the checker *cannot* close it (`:1281`) | **UNDECIDABLE BY ME, and correctly so.** Grading a literature signal is exactly the judgement `MAINTENANCE.md:74` reserves for a human. This is 18 of the 40 substantive warnings — nearly half — and it is a work backlog, not a defect. |
| Q4 × 8 / Q3 × 3 | read each named instrument's `known_answer_control.state` and its `inherits_limits_from` chain | **DECIDED AS ARITHMETIC, NOT AS SCIENCE.** The counts reproduce exactly from the graph. Whether a given control *should* read `fails`/`mixed`/`none` is a scientific judgement about the instrument, outside `--check` and outside my lane. |
| B5 × 6 | compare each route's `ready` status against the recorded checkpoint decisions | ⚠ **PARTLY UNDECIDABLE, and this is the one place the green run may be asserting something stale.** `CLOSED-WORK.md` records that *"Clinical conditional-recurrence, RT/IPD synthesis, and trial-discoverability/response checkpoints did not admit their proposed papers"* — which is in direct tension with `[B5]`'s *"nothing blocks this paper except writing it"* for `RT-IPD-SURVIVAL`→`PUB-IPD-SURVIVAL` (and plausibly the four `PUB-CARE-DELIVERY` rows). **I could not decide it: the record `CLOSED-WORK.md` points at, `research/autonomy/clinical-methods-checkpoints-2026-09-07`, does not exist in the tree at `5ae0fa04`** (`ls` → No such file or directory; the brief marks it "pending input"). Per §4 that is **UNKNOWN, not absence.** Deciding it needs that input. |
| L5 × 3 | for each of 6 ids, search for a citing route/instrument/lane/claim | **DECIDABLE, NOT DECIDED** — 6 targeted searches I did not spend. The checker's own docstring (`:1751`) states an orphan *"is not automatically a defect"*; note two of the four orphan artifacts (`ART-ATM-STATUS-ATRI`, `ART-GSE28866-TUMOUR-VS-NORMAL`) name evidence `CLOSED-WORK.md` calls heavily retained, so "registered ahead of citation" is the plausible reading. |
| D5 | check whether the named document is a `pinned-figures.json` target | **DECIDED — and this is the only warning in the green run that touches a pinned quantity.** `research/manuscripts/dependency/emc-atr-vulnerability-assessment.md` is line 44 of `pinned-figures.json`'s `targets` list, which `:1846` reads to build `depends_on`. So a document the numeric-consistency contract points at carries `last_verified: unverified` — nobody has confirmed its content is still true. Closing it requires a human to read that document; **mass-stamping is forbidden by the checker's own note at `:1915`.** |
| B9 × 12 | enumerate 12 `trigger→blocker` pairs and decide each: missing technology edge, or over-claiming trigger | **DECIDABLE, NOT DECIDED.** ⚠ Worth flagging structurally: 12 is *exactly* `TRIGGER_BLOCKER_BASELINE`, so this warning is a **pinned-baseline holder** — a 13th disagreement becomes an ERROR (`:908`), an 11th becomes an INFO telling you to lower the constant (`:913`). It is doing its job. |
| B3 | check `blockers.json` for the row's `inherited_by` | **DECIDED — the warning is REAL as stated.** `BLK-NO-FIELD-ATTENTION-MEASUREMENT` carries `kind: insufficient_data` and **no `inherited_by`, no `permanent`, no `retired_by_technology` keys at all** in the committed row. ⚠ **W26b already read this row's `retired_by_action` and named it an exemplary self-scoped clause** (*"NO measurement of any kind anywhere in this repository"*); I take that as given and add only the structural fact that the blocker holds down no route. Also relevant: `S52-BLOCKER-PRECISION.md:327` records that `[B3]` fires in the *opposite direction* from the failure mode that nearly caused a 38-route mass retirement. |

**Clinical registry and pinned quantities — the direct answer.** **Zero** of the 87 WARN and 7 INFO name `research/data/emc-clinical-registry.json` or any path under `research/data/` (`grep -c 'research/data\|emc-clinical-registry'` on the green output → **0**). The registry's contract is enforced by `scripts/validate-registry.mjs` (gate 10 per `POLICY-evidence.md`), a different checker that `systems_check --check` does not run — so a green `systems_check` says **nothing** about registry integrity. **Exactly one warning touches a pinned quantity: the `[D5]` load-bearing document above.** The `[B5]` care-delivery and IPD-survival routes consume registry-derived work indirectly, but no warning asserts anything about registry content.

### R.5 — Honest denominator · PRIMARY

| how classified | WARN | INFO | total | share of 94 |
|---|---:|---:|---:|---:|
| **From the raise site in source** (`file:line` read, semantics taken from the code and its comments) | 87 | 7 | **94** | **100%** |
| …of which **additionally decided against the data** (I re-ran the raise site's own logic over the graph and reproduced the count, or resolved the named subject) | 61 | 0 | 61 | 65% |
| From the message text alone | 0 | 0 | **0** | 0% |
| **Could not classify** | 0 | 0 | **0** | 0% |

The 61 independently reproduced: L4 47 (superset arithmetic 43+4), Q4 8 + Q3-WARN 1 (usability derivation re-implemented), B5 6 (route status × publication state re-read), X4-relations 1 (`parent` occurrence count). **Not** independently reproduced, though classified from source: the 18 ungraded-signal X4s (counts taken from the messages; I summed but did not re-parse `pending_signals[]`), L5 3, D5 1, B9 1, B3 1 — and all 7 INFO.

**Substantive warnings I actually decided: 3 of 40** (X4-`parent` real; B3 real; D5 real and pinned-touching). **1 of 40 blocked on a file that does not exist** (B5/IPD). **36 of 40 decidable but not decided within this unit's scope** — 18 of those 36 are the ungraded-signal backlog, which no automated procedure can close by design.

## Validation evidence

All `RUN` under `/tmp/claude-0/w31c*` on a `tar --exclude=./.git` copy of `5ae0fa04`; Linux, system `python3` (stdlib only); `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w31c-pycache`; no network. Every exit code quoted is the real captured `$?` or `${PIPESTATUS[0]}`. The checker was never modified; no flag, exclusion or `DOC_SKIP` entry was added; `--write-views` was never invoked anywhere.

**RUN** — `date -u` / `rev-parse` / `status --porcelain` at start and end (HEAD `5ae0fa04`, tree clean, unchanged); scratch tar copy (`TAR_PIPE_EXIT=0`, 613M); full-tree `--check` (`FULL_EXIT=1`, 189 ERROR / 220 WARN / 7 INFO); campaign directory moved **outside** the scan root; green `--check` (`GREEN_EXIT=0`, **0 ERROR / 87 WARN / 7 INFO**); severity-line counts (0 / 87 / 7); per-code histograms for WARN and INFO; full green WARN+INFO output read line by line; raise-site source reads at `:614 :618 :626 :642 :859 :908-916 :1024-1036 :1100 :1281 :1425-1440 :1502-1513 :1781 :1845-1852 :1913-1922 :2147-2166 :2317-2331 :2425` plus the `usable` derivation at `:394-410`; legacy-vs-graph superset arithmetic over `emc-systems-map.json`; `usable` re-derivation with `NON_SUPPORTING_CONTROL` extracted from source; `grep -c '"parent"' systems/graph/modalities.json` → **0** and `relations.json:396-412` read; `BLK-NO-FIELD-ATTENTION-MEASUREMENT` row read; `pinned-figures.json` `targets` grep → line 44; route/publication state read for all six B5 subjects; `ls research/autonomy/clinical-methods-checkpoints-2026-09-07*` → **No such file or directory**; prior-work `rg` and `git ls-files`; `S52-BLOCKER-PRECISION.md:320-360` and `MAINTENANCE.md` read; W26b/W09h read for overlap only. Scratch deletion verified (`RM_EXIT=0`; `ls` → no such file; `/` 49% used).

**PROPOSED (NOT RUN)** — `scripts/preflight.sh` (forbidden by dispatch). `systems/tests/` pytest suite (not my subject). Per-signal reading of the 301 ungraded `pending_signals[]`. Citation searches for the 6 L5 orphans. Enumeration of the 12 B9 pairs. **Any repair: none authored, none proposed as code, none applied.** `research/modalities/atr_hrd_sarcoma_series.py` was never invoked, with or without `--check`.

**Nothing was suppressed, excluded, reclassified or deleted to make a number smaller.** The single subtree move exists only in a throwaway scratch copy that has been deleted, and is reported as a counterfactual measurement, not as a recommended change.

## Limitations

- **Model identity is self-report**, not verifiable from this seat.
- **The green figure is stable but not permanent.** 87/7 held between S52 (2026-09-01, 604 objects) and me (2026-09-08, 620 objects). The *red* figure moved 172 → 189 in nine minutes and must be re-measured by anyone who quotes it.
- **"Substantive" is my stated rule applied by me**, not a property the checker exposes. Another classifier could reasonably move `[B9]` into hygiene (it is a pinned baseline holder) or `[L4]` into substantive (it is a real divergence between two files eleven consumers read).
- **I decided 3 of 40 substantive warnings.** The other 37 are classified and given a decision procedure; that is not the same as decided, and I do not claim any of them is real or spurious.
- **The B5/IPD tension is UNRESOLVED, not resolved in either direction.** The record needed to settle it is absent from the tree.
- **A green `systems_check` still says nothing about the clinical registry** — that is gate 10's job, run by `validate-registry.mjs`, which I did not run.
- **I graded no scientific claim's truth anywhere**, and nothing here bears on EMC efficacy, safety, selectivity or clinical readiness. No wet lab, no network, no paid API, no GPU. No content-policy refusal was encountered.

## Tool-call and wall-clock count actually used

**19 tool calls** (all `Bash`; seven issued as parallel pairs), of which 1 was a wrong-method run I discarded and corrected in place (raw-JSON `usable` read → re-derived through `inherits_limits_from`) and 1 was a path miss (`reports/` → the campaign directory). **Wall clock ≈ 3 minutes** of measurement, `03:40:45Z` to `03:43:41Z`, plus reading and drafting. Well inside the ~40-call / ~40-minute target; returned on the stop condition, no padding.

## Next concrete action

**One task, and it is a decision, not a repair: the maintainer of `systems/graph/relations.json` should decide whether `modalities.parent` is a rule to instantiate or an entry to retire.** It is the only substantive warning in the green run that is (a) fully decided by measurement, (b) a genuine internal inconsistency — a register of edges naming an edge zero of 217 `modalities.json` rows carry — and (c) closable by one person in one edit either way, with the two exits carrying different meanings: instantiate it on the sub-form rows whose EMC verdict differs from their parent's, or delete the declaration and record that the sub-form/parent distinction is not modelled. **Second, and larger but not mine to schedule: the `[D5]` load-bearing document** (`research/manuscripts/dependency/emc-atr-vulnerability-assessment.md`, a `pinned-figures.json` target carrying `last_verified: unverified`) **needs a human to read it and stamp it honestly** — that is the only warning in the whole green run touching a pinned quantity, and the checker's own note forbids clearing it by bulk date.

**I applied nothing and propose no code change.** I did not add a `DOC_SKIP` entry, did not narrow any check, and did not touch `systems/graph/`.
