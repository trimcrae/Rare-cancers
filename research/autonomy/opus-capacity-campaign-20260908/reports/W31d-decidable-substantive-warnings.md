<!-- collected 2026-09-08T04:32:14Z by campaign coordinator; agent id a95a89c7e98d56c02; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a95a89c7e98d56c02.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**W31d**, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: deciding the three decidable-but-undecided substantive-warning groups W31c left open (`[L5]`, `[B9]`, `[B5]`).

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My system context states Opus 5, model ID `claude-opus-5`. I did not observe the served model; no environment variable names one. The coordinator must extract the actual per-child runtime model from the transcript.

- `date -u` start `Tue Sep 8 03:49:00 UTC 2026`; end `Tue Sep 8 03:52:45 UTC 2026`.
- `git rev-parse HEAD` start **`e5d60db79f9dcbe7a4b2e6b0db1de6e32ccf69e7`**; end **`1b372b30c2b05a042b8c44f8090efb4b3a8e5386`** — **HEAD ADVANCED during my run** (the coordinator collected reports mid-run, exactly as `COMMON-BRIEF.md` warns). `git status --porcelain` start **0 lines**; end **0 lines**.
- **Write isolation honoured.** Nothing written, moved or deleted under `/home/user/Rare-cancers` or under `/tmp/claude-0/frozen-corpus/`. No git write operation (only `rev-parse`, `status`, `ls-files`). `preflight.sh` not run. No `systems/graph/*.json` edited, no `--write-views`, no `DOC_SKIP`, no repair authored or proposed. All execution under `/tmp/claude-0/w31d/` with `PYTHONDONTWRITEBYTECODE=1`; **scratch deleted before returning** (`RM_EXIT=0`; `ls` → No such file; `/` 48% used, 20G free). No network, no paid API, no GPU. W25 not read or referenced. No `[X4]` grading, no `[D5]` stamping.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (five long proxy-host lists — `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` — filtered out rather than reprinted; nothing else removed; **no variable names a served model**):

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

Set up front: **return when (1) each of the six `[L5]` orphan ids is graded with the search evidence behind the grade, (2) all twelve `[B9]` trigger→blocker pairs are enumerated with trigger, blocker, technology and which of the two readings the graph supports, and (3) the presence or absence of the clinical-methods checkpoint record in the frozen corpus is determined and its bearing on `[B5]` stated.** All three met. **Stop condition MET**, returned immediately.

## Question

W31c classified 40 substantive warnings and decided 3. **Three of the remaining groups are decidable by bounded read-only work: are the six `[L5]` orphans real orphans, are the twelve `[B9]` pairs missing edges or over-claims, and does the checkpoint record — absent from this checkout — exist in the frozen corpus and resolve the `[B5]` tension?**

## Prior-work check

Read in full as dispatched: `COMMON-BRIEF.md` (corrected 03:36Z/03:44Z version including "Known, measured, and NOT worth rediscovering"), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `research/autonomy/opus-capacity-campaign-20260908/reports/W31c-green-run-warnings.md` (in full — note the dispatch's path `reports/W31c-…` does not exist at repository root; the file lives under the campaign directory), and `systems/POLICY-evidence.md` (all 386 lines, before reading anything under `systems/`).

- `grep -rn "<id>" --include='*.json' --include='*.md' --include='*.py' --include='*.mjs' --include='*.js' .` for each of the six orphan ids, excluding `.git` and the campaign directory — this is the citation search itself, reported in R.1.
- `git ls-files | grep -c 'clinical-methods-checkpoints-2026-09-07'` → **0**.
- **Not replayed:** W31c's own decided three (`[X4]`-`modalities.parent`, `[B3]`, `[D5]`) — I take them as given and do not re-derive them. W26b's 17-file sweep and W09h's field census — taken as given, not re-derived.
- **Not touched, per dispatch and per `MAINTENANCE.md:74` / `systems_check.py:1915`:** the `[X4]` 301-signal grading backlog and the `[D5]` load-bearing document stamp.
- **Closed items I am not re-opening:** the three checkpoints that did not admit their papers stay not-admitted; I read the checkpoint record only to *decide a checker warning*, and I propose no paper.

## Method and inputs

| input | role |
|---|---|
| `/home/user/Rare-cancers` @ `e5d60db7` → `1b372b30` | read-only; the graph under decision |
| `systems/graph/{routes,publications,blockers,technologies,artifacts,objects,evidence,instruments,lanes}.json` | read via `json.load` only |
| `research/method-watch-triggers.json` | the trigger registry `[B9]` compares against |
| `systems/systems_check.py` `:451-490`, `:605-616`, `:850-916`, `:1751-1783` | raise sites and the `cited_by` derivation, read from source |
| `/tmp/claude-0/frozen-corpus/extracted/corpus/research/autonomy/clinical-methods-checkpoints-2026-09-07/` | the checkpoint record — **present**, 32 files + `validation/` |
| `/tmp/claude-0/w31d/{b9.py,b9b.py,b9c.py}` | scratch re-implementations of the checker's own `[B9]` loop; deleted |

`[B9]` was decided by **re-implementing the checker's loop verbatim** (`check_trigger_blocker_agreement`, `:860-905`) in scratch, not by parsing its message text — the WARN message deliberately prints no pair list.

## Result

### R.1 — The six `[L5]` orphans, graded · PRIMARY

Grading rule stated before applying it, taken from the `cited_by` derivation at `:451-486`: a row is cited only if a **route** lists it in `objects`/`evidence`/`artifacts`/`supporting_evidence[].ref`, an **instrument** in `characterises`, a **lane** in `produces` (joined on `path` basename), a **claim** in `artifact`, or an **object** in `definition.provenance`/`length_field.artifact`. Prose mentions in `research-ledger.json`, receipts, memos and generated views are **not** citations by this derivation.

| id | coll | every non-register hit found | grade |
|---|---|---|---|
| `OBJ-RES-C166` | objects | legacy `emc-systems-map.json:1045` + `emc-systems-map.md:270` (the legacy registry's own table), `systems/views/L5-evidence-base.md:52` (generated). No route, instrument, lane or claim. `characterises` scan → `[]`. | **REAL-ORPHAN.** Its own register text is the reason: *"present in the fusion under every plausible breakpoint, absent from every structure in this program."* It is registered to record a **negative structural fact**, which by construction no structural route can cite. Honest, not defective — but genuinely uncited. |
| `EV-LI-GONG-2026` | evidence | `research-ledger.json:5498` (names it as a deliverable of the `RT-ALK-HIT` negative re-grade), `receipts/CYC-0087-1c9f0963.json:30`, generated view `:72`. | **REAL-ORPHAN WITH A BENIGN, IDENTIFIED CAUSE.** ⭐ `RT-ALK-HIT.supporting_evidence` = `['ART-CENSUS-ROUTE-GRADING','ART-DEPMAP-SARCOMA-DEP','ART-ALK-IHC-FET-2026']` — the route cites the **artifact** produced from this paper, not the **evidence row** for the paper. The ledger names both as deliverables of the same cycle; only one got the edge. This is the exact "recorded because it needed a home" case the docstring at `:1765` describes, plus one missing route→evidence edge. |
| `ART-ATM-STATUS-ATRI` | artifacts | `research-ledger.json:1679` (full result, and names *"lane `.github/workflows/atm-status-stratification.yml`"*), generated view `:95`. | **REGISTERED-AHEAD-OF-CITATION → in practice REAL-ORPHAN.** The ledger asserts a producing lane, but `systems/graph/lanes.json` has **18 lanes carrying 8 `produces` entries in total** and none matches `atm-status-atri-stratification.json`. Its own verdict is `INSTRUMENT_CANNOT_DETECT` / *"UNINFORMATIVE RATHER THAN NEGATIVE"*, so no route rests on it — correctly. |
| `ART-GSE28866-TUMOUR-VS-NORMAL` | artifacts | `research/manuscripts/surface-targets/surface-targets-graph-records.json:74` (the **append record that created it**), generated view `:117`. | **REGISTERED-AHEAD-OF-CITATION.** Strongest case of the four: the ingest record appends the artifact and patches `publications.json` in the same file, and its `what_it_is` names a canonical reading memo (`gse28866-tumour-vs-normal-reading.md`) that `CLOSED-WORK.md` lists as required reading. The evidence is in active use; the route→artifact edge was never written. |
| `ART-PUBLISHED-WARHEAD-REGISTRY` | artifacts | legacy `emc-systems-map.json:2628` + `emc-systems-map.md:456`, generated view `:132`. | **REGISTERED-AHEAD-OF-CITATION.** The legacy map states its purpose verbatim: it is *"the record the files carrying the ⛔ superseded, retained 'Munck 2022' attribution should have been pointing at"* — a correction target, registered so a misattribution has somewhere to resolve to. Uncited **by design**, exactly the docstring's second exemption. |
| `ART-WETLAB-CONTRACTING-COSTS` | artifacts | `research-ledger.json:13480`, **`systems/graph/blockers.json:130`** (`BLK-NO-WET-LAB.retired_by_action`: *"ART-WETLAB-CONTRACTING-COSTS owns the numbers"*), `views/registers/blockers.md:135`. | **CITED-AFTER-ALL — by a blocker, which the derivation does not read.** ⭐ This is the one genuine checker gap in the group: a live `blockers.json` row names the artifact as the owner of a figure, and `cited_by` is derived from routes/instruments/lanes/claims/objects **only**. The artifact is load-bearing for `BLK-NO-WET-LAB`'s cost statement and reads as orphaned. |

**Group verdict.** 2 REAL-ORPHAN, 3 REGISTERED-AHEAD-OF-CITATION, 1 CITED-AFTER-ALL. **Zero are defects in the graph's science.** The single actionable finding is `ART-WETLAB-CONTRACTING-COSTS`: a blocker citation that the derivation cannot see. I authored no repair.

### R.2 — All twelve `[B9]` pairs, enumerated and decided · PRIMARY

Reproduced exactly: **12**, equal to `TRIGGER_BLOCKER_BASELINE`. Zero `[B8]` permanent-blocker escalations.

Decision rule, stated before applying it and taken from the checker's own docstring: a blocker of kind `requires_wet_lab` / `requires_external_collaboration` **cannot** be retired by a computational technology (CLAUDE.md §5, and `:867-869` uses precisely this argument for `TECH-VIRTUAL-CELL` × `BLK-FUNCTIONAL-ACTIONABILITY`) → **over-claiming trigger**. A blocker whose `kind` lies inside the technology's own domain → **missing technology edge**.

| # | trigger | blocker (kind) | technology (its `unblocks.blockers`) | reading the graph supports |
|---|---|---|---|---|
| 1 | `TRG-CRYPTIC-POCKET-PREDICTION` | `BLK-R4-BINDS` (`requires_wet_lab`) | `TECH-CHEAP-ENSEMBLE` (`[]`) | **OVER-CLAIMING — self-contradicted.** The trigger's own `note`: *"R4 … is a binding fact, not a prediction fact. A predictor sharpens the prior; **it cannot discharge R4**."* It then lists `BLK-R4-BINDS` in `reopens`. Strongest case in the set. |
| 2 | `TRG-GENERATIVE-ENSEMBLE` | `BLK-R4-BINDS` (`requires_wet_lab`) | `TECH-CHEAP-ENSEMBLE` (`[]`) | **OVER-CLAIMING.** A cheaper/better ensemble generator is computational; a wet-lab binding fact is not retirable by it. |
| 3 | `TRG-NR4A3-DIRECT-MATTER` | `BLK-R4-BINDS` (`requires_wet_lab`) | `TECH-RXR-HETERODIMER-REPORT` (`[]`) | **OVER-CLAIMING *relative to this technology*.** The trigger's claim is legitimate in itself (*"the one blocker that a single published binder would discharge outright"*) — but the discharging event is an **external published binder**, not an RXR-heterodimer report. The trigger is attached to a technology that does not deliver what discharges the blocker. ⚠ The honest repair is arguably neither of the checker's two options; between the two it offers, the graph supports over-claiming. |
| 4 | `TRG-VIRTUAL-CELL-NO-LINE` | `BLK-FUNCTIONAL-ACTIONABILITY` (`requires_wet_lab`) | `TECH-VIRTUAL-CELL` (`['BLK-NO-EMC-DATA','BLK-CLASS-INHERITANCE']`) | **OVER-CLAIMING — named in the checker's own docstring** at `:867-869` as the case that surfaced `[B9]`. The trigger's own `note` even concedes it: *"the one blocker no in-silico structural work can touch."* |
| 5 | `TRG-PARALOGUE-POSITIVE-CONTROL` | `BLK-ENDPOINT-MD` (`no_known_assay`) | `TECH-NONCOVALENT-PARALOGUE-CONTROL` (`['BLK-PARALOGUE-CONTROL']`) | **OVER-CLAIMING — self-flagged.** The trigger's `note` separates the two: *"Distinct from `TRG-ENDPOINT-SELECTIVITY-READOUT` — **that one asks for a better INSTRUMENT**, this one asks for a scoreable SYSTEM."* `BLK-ENDPOINT-MD` is the instrument half, which the note assigns elsewhere. Its other blocker (`BLK-PARALOGUE-CONTROL`) **is** owned and does not appear here — the check is discriminating correctly. |
| 6 | `TRG-EMC-FUNCTIONAL-MODEL` | `BLK-NO-EMC-DATA` (`insufficient_data`) | `TECH-EMC-MODEL-ACCESS` (`['BLK-NO-WET-LAB','BLK-R4-BINDS','BLK-FUNCTIONAL-ACTIONABILITY']`) | **MISSING TECHNOLOGY EDGE — clear.** An EMC functional model is EMC material; the technology already owns three *harder* blockers including two wet-lab ones, so omitting the data blocker is an omission, not a scope statement. |
| 7 | `TRG-EMC-EXPRESSION-DATASET` | `BLK-CLASS-INHERITANCE` (`insufficient_data`) | `TECH-EMC-EXPRESSION-DATA` (`['BLK-NO-EMC-DATA']`) | **MISSING TECHNOLOGY EDGE — clear.** Trigger `note`: *"Six routes are currently graded on class inheritance rather than on an EMC measurement. A dataset that contains EMC is what converts an inherited grade into a measured one."* That is a verbatim description of retiring `BLK-CLASS-INHERITANCE`. Corroborated: `TECH-VIRTUAL-CELL` **already** owns this blocker, so it is technology-retirable in principle. |
| 8 | `TRG-SARCOMA-ATRI-RESPONSE-PANEL` | `BLK-CLASS-INHERITANCE` (`insufficient_data`) | `TECH-EMC-EXPRESSION-DATA` (`['BLK-NO-EMC-DATA']`) | **MISSING TECHNOLOGY EDGE — same edge as #7.** ⭐ One edge (`TECH-EMC-EXPRESSION-DATA → BLK-CLASS-INHERITANCE`) accounts for **2 of the 12**, so the baseline would fall to 10 on a single addition. |
| 9 | `TRG-CHARGE-CHANGE-FEP` | `BLK-PARALOGUE-DDG` (`requires_better_simulation_accuracy`) | `TECH-CHARGE-CHANGE-FEP` (`[]`) | **MISSING TECHNOLOGY EDGE.** A charge-change FEP correction is exactly simulation accuracy on ΔΔG; blocker kind and technology domain coincide. |
| 10 | `TRG-TERNARY-ALCHEMICAL-VALIDATED` | `BLK-PARALOGUE-DDG` (`requires_better_simulation_accuracy`) | `TECH-TERNARY-ALCHEMY` (`[]`) | **MISSING TECHNOLOGY EDGE.** Same argument; validated ternary alchemy is the accuracy this blocker names. |
| 11 | `TRG-GLUE-PROSPECTIVE-DESIGN` | `BLK-INDUCED-COMPLEX` (`requires_better_structure_prediction`) | `TECH-GLUE-DESIGN` (`[]`) | **MISSING TECHNOLOGY EDGE — clear.** Glue design *is* induced-complex prediction; the kinds match exactly. |
| 12 | `TRG-GLUE-PROSPECTIVE-DESIGN` | `BLK-PARALOGUE-DDG` (`requires_better_simulation_accuracy`) | `TECH-GLUE-DESIGN` (`[]`) | **AMBIGUOUS, leaning over-claiming — recorded as undecided rather than forced.** Glue design is a structure/design capability, not a ΔΔG-accuracy one, so it is not obviously the technology that retires a simulation-accuracy blocker; but the trigger reopens `R7`/`R9`/`R10` and `RT-GLUE` legitimately. This is the pair the docstring's own warning is about (*"`TRG-GLUE-PROSPECTIVE-DESIGN` over-claims TWO blockers, so a per-trigger tally reads 11 and hides one"*). |

**Group verdict: 5 over-claiming triggers, 6 missing technology edges, 1 ambiguous.** Note `TRG-GLUE-PROSPECTIVE-DESIGN` contributes 2 of the 12, which is exactly why the baseline is 12 and not 11 — the constant is holding the shape the docstring says it should. **⚠ The baseline is a ledger, not a wall: nothing here authorizes lowering `TRIGGER_BLOCKER_BASELINE`, and I changed nothing.**

### R.3 — `[B5]`: the checkpoint record IS in the corpus, and the tension resolves — but not the way W31c expected · PRIMARY

**Presence.** `research/autonomy/clinical-methods-checkpoints-2026-09-07/` is **absent from this checkout** (`ls` → No such file or directory; `git ls-files | grep -c` → **0**) and **PRESENT in the frozen corpus** at `/tmp/claude-0/frozen-corpus/extracted/corpus/research/autonomy/clinical-methods-checkpoints-2026-09-07/` — **32 files plus a `validation/` subdirectory**, mode `-r--r--r--`, mtime `Sep 8 02:29`, and listed in `metadata/tracked-file-map.txt` with blob hashes. W33's measurement transfers. **This is not UNKNOWN: it is found.**

**What it says.** Two of the three checkpoints `CLOSED-WORK.md` names give an explicit, quotable coordinator decision:

- `conditional-recurrence-gate.json` — `"outcome": "fixed_four_source_gate_not_met"`, `"outcome_computation_performed": false`, `"digitization_performed": false`, and verbatim: **`"coordinator_decision": "Do not launch this manuscript from current inputs."`** All four sources (Drilon `PMC2779719`, Bishop `PMC7771031`, Ogura `PMID 22678528`, Fice `PMC8891938`) carry an explicit `missing` field — no risk tables, no censor marks, no aligned time origins.
- `rt-synthesis-source-decision.md` — recovers Novak 2026 (`PMID 42588730`, `DOI 10.3390/cancers18152515`), finds it does **not** cross-tabulate treatment and recurrence within EMC, and concludes: **"The proposed synthesis remains unallocated for a manuscript or numerical pooling"** and **"No preprint-ready package resulted from this checkpoint."**
- `ranked-checkpoints.md` ranks five questions, each with a stop condition; rank 3 (KM constraints / methods solver) and `methods-paper-next-evidence.txt` record that a pass **"would not justify … an EMC manuscript."**

**Does it resolve the `[B5]` tension? Partly — and the graph resolves the rest by itself.** ⭐ **The decisive finding is not in the corpus at all: every one of the six `[B5]` publication endpoints carries a non-empty `blocked_by` in `systems/graph/publications.json`.**

| route | endpoint | `state` | endpoint's own `blocked_by` |
|---|---|---|---|
| `RT-MDT-LUNG` | `PUB-LOCOREGIONAL` | `outlined` | `['BLK-NO-EMC-DATA']` |
| `RT-IPD-SURVIVAL` | `PUB-IPD-SURVIVAL` | `unwritten` | `['BLK-NO-CURATED-CLINICAL-DATA']` |
| `RT-SURGICAL-QUALITY` | `PUB-CARE-DELIVERY` | `unwritten` | `['BLK-NO-FIELD-ATTENTION-MEASUREMENT']` |
| `RT-SURVEILLANCE` | `PUB-CARE-DELIVERY` | `unwritten` | `['BLK-NO-FIELD-ATTENTION-MEASUREMENT']` |
| `RT-METASTASECTOMY` | `PUB-CARE-DELIVERY` | `unwritten` | `['BLK-NO-FIELD-ATTENTION-MEASUREMENT']` |
| `RT-RISK-MODEL` | `PUB-CARE-DELIVERY` | `unwritten` | `['BLK-NO-FIELD-ATTENTION-MEASUREMENT']` |

The `[B5]` check at `:609-616` reads only `p["state"]` and `r["state"]["status"]`. **It never reads `p["blocked_by"]`.** So its message — *"nothing blocks this paper except writing it"* — is **contradicted by the very row it is reporting on**, 6 times out of 6. The tension W31c could not resolve is therefore **a defect in the warning's wording/predicate, not a stale route status**: the graph already records what blocks each of these papers, and the checkpoint record independently confirms, in prose and with named sources, that these questions did not clear their gates.

⭐ **Cross-finding with W31c's decided `[B3]`.** `BLK-NO-FIELD-ATTENTION-MEASUREMENT` is the blocker W31c graded *"holds down no route"* under `[B3]` (empty `inherited_by`). It is not idle — it blocks a **publication**, and `[B3]` only inspects route inheritance. `[B3]` and `[B5]` are two views of the same unmodelled edge: publication-level blocking is recorded in `publications.json` and read by neither check.

⚠ **Mapping caveat, stated because it bounds the claim.** `grep -rl` for `PUB-IPD-SURVIVAL|PUB-CARE-DELIVERY|RT-IPD-SURVIVAL|RT-SURGICAL-QUALITY` across the corpus checkpoint directory returned **zero files** (`IDGREP_EXIT=1`). The checkpoint record never names a graph id. The correspondence between its three not-admitted checkpoints and these six `[B5]` rows is **by topic, asserted by `CLOSED-WORK.md`, not by identifier** — I did not verify it at the row level and do not claim to have.

## Validation evidence

All **RUN** at `/home/user/Rare-cancers` (read-only, HEAD `e5d60db7` → `1b372b30`) and `/tmp/claude-0/w31d/`; Linux, system `python3` (stdlib only); `PYTHONDONTWRITEBYTECODE=1`; no network, no paid API, no GPU. Exit codes are real captured `$?`.

**RUN** — `date -u` / `git rev-parse HEAD` / `git status --porcelain` at start and end (start `e5d60db7`, end `1b372b30`, tree clean 0 lines both times). Six `grep -rn` citation searches over `*.json|*.md|*.py|*.mjs|*.js` excluding `.git` and the campaign directory. `systems_check.py` source reads at `:440-495` (the `cited_by` derivation), `:605-620` (`[B5]`), `:850-925` (`[B9]` + `TRIGGER_BLOCKER_BASELINE`), `:1735-1800` (`[L5]`). `b9.py` re-implementation of `check_trigger_blocker_agreement` → **`count 12`**, `EXIT=0`, 12 pairs listed, 0 `[B8]`. `b9b.py` (blocker kinds/permanence + technology `unblocks`) `EXIT=0`. `b9c.py` (11 trigger `reopens` blocks) `EXIT=0`. Route/publication join over `routes.json` × `publications.json` reproducing all six `[B5]` pairs with `blocked_by`, `EXIT=0` (two earlier attempts raised `TypeError: unhashable type: 'dict'` because I guessed `r["publication"]` was a string; corrected against the raise site, which reads `(r.get("publication") or {}).get("endpoint")` — recorded because it is the same class of error W31c recorded for `usable`). Graph census: 18 lanes / 8 `produces` entries, 56 artifacts, 32 instruments / 8 `characterises` entries, 19 objects, 83 routes. `ls -la` of the corpus checkpoint directory (32 files + `validation/`). `grep` of `metadata/tracked-file-map.txt` → 20+ blob rows. Full reads of `conditional-recurrence-gate.json`, `rt-synthesis-source-decision.md`, `ranked-checkpoints.md`, head of `methods-paper-next-evidence.txt`. `ls` + `git ls-files` confirming checkpoint absence from the checkout. Scratch deletion verified (`RM_EXIT=0`).

**PROPOSED (NOT RUN)** — `systems/systems_check.py --check` (not needed; I decided warnings W31c had already enumerated, and did not re-derive the counts). `scripts/preflight.sh` (forbidden by dispatch). `systems/tests/` pytest. `scripts/validate-registry.mjs`. **Any repair, patch, gate or test: none authored, none proposed as code, none applied.**

**Nothing was suppressed, excluded, reclassified or deleted.** No guard weakened, relaxed or reordered. No constant changed. No graph file edited.

## Limitations

- **Model identity is self-report**, not verifiable from this seat.
- **HEAD advanced mid-run** (`e5d60db7` → `1b372b30`). Per `COMMON-BRIEF.md` §1 the coordinator's commits touch only the campaign directory, so my graph reads are unaffected — but I read the graph at `e5d60db7` and did not re-read it at `1b372b30`.
- **The `[B9]` decisions are my stated rule applied by me.** The blocker-kind → technology-domain rule is a defensible reading grounded in the checker's own docstring and CLAUDE.md §5; it is not a property the graph exposes. Pair #12 I left ambiguous rather than force. Another reader could move #3 to "missing edge".
- **`[L5]` "REGISTERED-AHEAD-OF-CITATION" vs "REAL-ORPHAN" is a judgement about intent**, read from each row's own register text. Only `ART-WETLAB-CONTRACTING-COSTS` is a measurable checker gap.
- **The `[B5]`↔checkpoint mapping is topical, not by identifier** — the corpus record names no graph id (measured, `IDGREP_EXIT=1`).
- **The corpus is a selected snapshot**, `is_complete_repository: false`. Its `absent_files` are UNKNOWN. Finding the checkpoint record there proves it exists in that snapshot; it does not tell me why it is untracked in this checkout.
- **I graded no scientific claim's truth.** Nothing here bears on EMC efficacy, safety, selectivity, therapeutic window or clinical readiness; there is no wet lab. I re-opened no paper — the three checkpoints stay not-admitted, and I read their records only to decide a checker warning. No content-policy refusal was encountered.
- **A green `systems_check` still says nothing about the clinical registry** (gate 10 / `validate-registry.mjs`, which I did not run).

## Tool-call and wall-clock count actually used

**21 tool calls** (all `Bash`; six issued as parallel pairs), of which 2 were corrections in place (a wrong report path `reports/` → the campaign directory; two `TypeError`s from guessing the `publication` field shape before reading the raise site). **Wall clock 3 min 45 s**, `03:49:00Z` → `03:52:45Z`. Well inside the ~40-call / ~40-minute target; returned on the stop condition, no padding.

## Next concrete action

**One task, and it is a checker-predicate decision the maintainer should make, not a repair I may write: `[B5]` should read the endpoint's own `blocked_by` before asserting "nothing blocks this paper except writing it."** It is the only finding here that is (a) decided by measurement — 6 of 6 endpoints carry a non-empty `blocked_by` the check never reads, (b) independently corroborated outside the graph by the corpus checkpoint record's explicit *"Do not launch this manuscript from current inputs"* and *"remains unallocated for a manuscript or numerical pooling"*, and (c) currently telling a reader the opposite of what the graph records — the most expensive kind of wrong, because it invites someone to start a paper three recorded checkpoints declined. **The same edit closes the `[B3]` half:** `BLK-NO-FIELD-ATTENTION-MEASUREMENT` looks idle only because publication-level blocking is modelled in `publications.json` and read by neither `[B3]` nor `[B5]`. Second, smaller and independent: `ART-WETLAB-CONTRACTING-COSTS` is cited by `BLK-NO-WET-LAB.retired_by_action` and reads as orphaned because `cited_by` never derives from `blockers.json`. **I applied nothing, proposed no code, and touched no graph file, checker or constant.**
