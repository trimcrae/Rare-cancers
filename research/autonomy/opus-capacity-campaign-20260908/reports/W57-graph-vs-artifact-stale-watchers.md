<!-- collected 2026-09-08T04:54:43Z by campaign coordinator; agent id acc79230c1d00b89d; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-acc79230c1d00b89d.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

W57, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: successor to W26d — census of the "stale watcher" defect class across `systems/graph/`.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions. The coordinator must extract the runtime model from the transcript.

`date -u` — start `Tue Sep  8 04:45:15 UTC 2026`, end `Tue Sep  8 04:50:58 UTC 2026`.
`git rev-parse HEAD` — start `fb1a3f8040537234010114053b36ec55b729c65e`, end `56f355f65b7b3e47aeb434ac02edf4cf049f40f3` (**HEAD moved under me**; per the brief's 03:36Z correction that is expected — the coordinator was collecting reports. All my measurements were taken between these two commits; I did not re-measure at the end commit).
`git status --porcelain` — **0 lines at start, 0 lines at end.** Nothing written, moved or deleted in the repository; no git write operation; no graph file, view, report or manuscript edited; no repair, patch, gate or test authored; `scripts/preflight.sh` not run; `atr_hrd_sarcoma_series.py` never invoked. All execution under `/tmp/claude-0/w57/`, **deleted before returning** (`ls` → `No such file or directory`).

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (literal; three long proxy lists and `JAVA_TOOL_OPTIONS` elided as `…` and marked as such):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=…  [elided, proxy list]
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
GLOBAL_AGENT_NO_PROXY=…  [elided, proxy list]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=…  [elided, truststore + proxy flags]
NO_PROXY=…  [elided, proxy list]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=…  [elided, proxy list]
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

No network, no retrieval, no paid API, no GPU, no human contact, no publication. No clinical, efficacy, safety, selectivity or readiness claim; there is no wet lab. Nothing in this report restates graph prose as a scientific finding — every number below is a count of characters, keys and list elements in committed JSON.

---

## Question

Across all 19 files in `systems/graph/`, how many prose fields state a **specific quantity or state attributed to a named artifact outside `systems/graph/`**, what is each artifact's live value, and how many of those fields are read by any executable at all?

Open because W26d measured the *reach* of one instance (`TECH-RECONSTRUCTED-IPD`, 2 fields → 4 view lines) and named the structural gap — *"the drift guard's fixed point is 'the view matches the graph', never 'the graph matches the artifact it cites'"* — but measured the class size at exactly one member.

---

## Prior-work check

Read in full first: `COMMON-BRIEF.md` (all of it, including the HEAD correction and the whole "Known, measured, and NOT worth rediscovering" section), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W26d-refuted-clause-blast-radius.md`.

- `rg -n -i "stale watcher" --glob '!.git' --glob '!research/autonomy/opus-capacity-campaign-20260908/**'` → **0 hits**. `git ls-files | rg -i "stale|watcher"` → 9 files, all about *lane* staleness (`lane_staleness_watch.py`, `lane-staleness-watch.yml`, `test_preflight_cannot_read_stale_bytecode.py`), none about graph-vs-artifact drift. The class has no prior tracked census.
- **Taken as given, not re-measured** (per the brief): `modalities.json` prose reaches zero views; `requires` is never read; the campaign resolution rate; the `origin/literature-cache` question; the pytest-interpreter trap; the `systems_check --check` baseline. I ran no `--check`, no `--write-views`, no generator.
- `reports/W25-*` — **not read, not referenced.** Lane-2 statistics — not touched. Sibling reports supplied W26d's single seed case only; every value below comes from a read I performed.

---

## Method and inputs

Read-only, `/home/user/Rare-cancers` working tree, Python 3.11 stdlib, Linux, no network. Four stages, all scripted under `/tmp/claude-0/w57/`:

1. **Leaf extraction.** Walked all 19 `systems/graph/*.json` to every string leaf with its dotted path: **13,506 string leaves**.
2. **Class filter (broad).** Leaf must (a) contain a file token outside `systems/graph/`, (b) be prose (≥60 chars, contains whitespace), (c) carry a quantity/state token (`\d+`, zero, none, not yet, never, currently, today, empty, absent, missing, has not, still, no longer) within 140 chars of the artifact mention → **210 fields**. Tightened to a 60-char adjacency window → **206 fields**.
3. **Gradable subset.** Restricted to fields naming a **machine-readable JSON artifact** outside `systems/graph/` (a `.md`/`.py`/`.yml` artifact has no mechanically comparable live value) → **104 fields / 148 (field, artifact) pairs**. Artifact paths resolved against `git ls-files` by basename.
4. **Grading.** For each field I extracted every snake_case key token co-occurring with the artifact, searched the live artifact JSON for that key at any depth, and printed the prose sentence beside the live value → **55 distinct (field, artifact, key) claim triples**, which I then graded by hand, running targeted arithmetic (list lengths, label counts, distinct-value sets, sums) in Python against the live artifacts.

**Calibration first, and it matters.** I also ran a purely mechanical screen — "is every number adjacent to the artifact mention literally present in that artifact's text?" — over all 148 pairs. It returned 29 non-corroborated pairs and **it graded W26d's known-STALE case as corroborated** (the literal `0` occurs elsewhere in `emc-ipd-survival.json`). ⛔ **A number-presence grep cannot detect this defect class**; only key-resolved comparison can. That negative result is reported as a finding, not discarded.

---

## Result

### R.1 — Class size, by filter stage `PRIMARY`

| stage | fields |
|---|---:|
| string leaves in the 19 graph files | 13,506 |
| prose leaf + artifact outside `systems/graph/` + quantity/state within 140 chars | **210** |
| …within 60 chars | 206 |
| …artifact is a machine-readable JSON (gradable class) | **104** (148 field×artifact pairs) |
| …resolvable to a named key with a live value (graded set) | **31 fields / 55 field×artifact×key triples** |

Per-file distribution of the 104-field gradable class: `routes.json` 44, `plan.json` 18, `blockers.json` 9, `requirements.json` 7, `artifacts.json` 6, `evidence.json` 5, `modalities.json` 3, `objects.json` 3, `publications.json` 3, `instruments.json` 2, `lanes.json` 2, `artifact-refs.json` 1, **`technologies.json` 1** (W26d's case). Seven of the 19 files carry no member of the class.

### R.2 — Grades over the 31 graded fields `PRIMARY`

| grade | fields | 
|---|---:|
| **AGREES** | **24** |
| **STALE** | **3** |
| **UNCHECKABLE** | **4** |

**AGREES (24 fields, verified by reading the live artifact):** `instruments.json` 29 (`patient-cd4-demo.json` `junction_context` = `QYSQQSSSYGQQ|NMPCVQAQYSPS`, byte-identical); `objects.json` 13 ×2 (`nr4a3-exon-audit.json` exons 1–2 `coding_nt_in_exon` 0; exon 3 `first_protein_residue` 1); `blockers.json` 16.evidence.2 (`autonomy-state.json` `gpu_spend_prohibited.verbatim` quoted exactly, `set_by` "trimcrae, 2026-09-02"); `plan.json` blocks.15 ×4 (`cancellation_ratio` 0.0111; 6 of 10 `charge_change ≠ 0`; `heavy_1 = heavy_4 = 59`; `calib_hi` = Wurz_cmpd1 / 8G1Q / CCD YHB); blocks.23 ×5 (`trajectory_objects_found` 0; all **17** legs `frac_frames_in_contact` = 1.0 with one distinct value; 72 objects total across `by_class`; 796 MB `built_cif` = 796,689,589 B; 1.35 GB `built_system` = 1,349,596,712 B; 27 kB `leg_result` = 26,890 B); blocks.24 (`n_complete` 18, `n_units` 19); blocks.27 ×2 (`realised_usd` 73.79, `n_computable` 18); blocks.57 and `requirements.json` 13 ×2 (`antitarget-selfcontrol.json` `panel_readable` false); `publications.json` 1.posted (`PUB-ASO.json` `reviewed_commit` `3d5c709b…`, `last_round` 34, blockers `[]`, `p1s` len 7 — all four sub-claims agree); `requirements.json` 4.claim_ceiling and 4.claim_ceiling_raw (`pose-convergence-401.json` `cross_method_evidence` = "NONE…"; `pose-conditionality-census.json` Part-B `n_gradeable` 0; `apo-pose-site-in-regime.json` `n_gradeable` 14); `requirements.json` 10.claim_ceiling_raw (`min_models_per_arm` 16, `reproducibility_bar` 3); `routes.json` 41 (`per_run.*.ewsr1_break_apart_fish` = 8 EWSR1+ / 4 EWSR1−, n=12); `routes.json` 52 and 54 (`depmap-sarcoma-dependency.json` every per-gene `n_sarcoma` = 91, distinct set `{91}`); `routes.json` 74 (`absolute_risk_computable` false; `cross_cohort_summary.comparisons` 12, `comparisons_where_both_exclude_1` 0); `routes.json` 79 (`emc-terminal-events.json` `deaths_by_label` sums to 52, `treatment_related` = 2).

### R.3 — ⭐ The full STALE list (3 fields) `PRIMARY`

**S1 · `systems/graph/technologies.json` → `TECH-RECONSTRUCTED-IPD.not_scannable_because`** (W26d's seed case, re-confirmed independently at my HEAD)
> quoted: *"`curves_supplied` in research/modalities/emc-ipd-survival.json, **which is 0 today** and is the only number that can change this capability's state"*
> live: `research/modalities/emc-ipd-survival.json` → `/curves_supplied` = **1**
> **STALE — graph says 0, artifact says 1.**

**S2 · `systems/graph/objects.json` → `OBJ-LINE-HEMCSS.notes`** (new, not previously reported anywhere I could find)
> quoted: *"the `identity` verdict, the `may_not_ground` list, **the 30-entry `read_by` sweep** and its `_sweep_limit` stay in research/manuscripts/emc-systems-map.json"*
> live: `research/manuscripts/emc-systems-map.json` → `objects[18]` (id `OBJ-LINE-HEMCSS`, same record) `read_by` has **114** entries
> **STALE — graph says 30, artifact carries 114.** ⚠ Sharper than a plain drift: the sentence's own argument is that the graph must *not* hold a second copy of the fact, and the one number it nonetheless typed is the one that went stale — 3.8× off.

**S3 · `systems/graph/routes.json` → route 81 `.rationale`**
> quoted: *"of **162 death-cue sentences** in research/literature/emc-mortality-probe.json (34 EMC-titled papers), exactly ONE mentions embolism at all"*
> live: `research/literature/emc-mortality-probe.json` → `terminal_events` is a list of **162 papers** (each with `n_sentences`/`sentences`), and `summary.death_sentences_total` = **577**, `summary.papers_with_death_sentences` = **162**
> **STALE — the quantity 162 is attached to the wrong unit: 162 is the paper count, the sentence count is 577.** The failure mode is *unit* misattribution rather than temporal drift, but it is the same class: a number typed into the graph about an artifact, with nothing that can compare them. ⚠ The same field's *other* sub-claim is AGREES (PMID 41799218 does carry `label: respiratory_failure` in `emc-terminal-events.json`), and the parenthetical "34 EMC-titled papers" is UNCHECKABLE — no field of the probe carries it (`oa_corpus_enumerated` 600, `fulltext_retrieved` 328).

### R.4 — UNCHECKABLE (4 fields) `PRIMARY`

| field | why |
|---|---|
| `routes.json` 17 `.grade.value` | cites `coverage-scan.json` — **no such tracked file** |
| `routes.json` 51 `.supporting_evidence[1].what_it_supports` | cites `schema.json` — no unambiguous tracked file of that name |
| `artifact-refs.json` `_why[5]` | *"valb-triangle-chem.json was REMOVED from this file"* — the artifact is untracked, so there is no live value to compare; the claim is about the graph file itself |
| `plan.json` blocks.15 | *"`n_replicates=1`"* attributed to the r0 cycle — `degrader-paper-schedule.json` `milestones[5].result_r0` carries **no `n_replicates` key** (only `result_n3`, = 3), and the record is flagged `_superseded_by`. No comparable live value. |

### R.5 — ⭐ How many graded fields are read by ANY executable `PRIMARY`

Using the brief's key-literal rule (`["']key["']|\.key\b` over `*.py *.mjs *.sh *.yml`), and applying W43's correction — **do the grep per artifact, never per field name** — I restricted it to the **66 executables that reference `systems/graph` at all**:

| graph field key | executables (of the 66 graph consumers) that contain the key literal |
|---|---|
| `not_scannable_because` | `systems/systems_check.py`, `systems/tests/test_systems_check.py` |
| `claim_ceiling` / `claim_ceiling_raw` | `systems_check.py`, `extract_requirement_register.py`, both tests (+ `emc_icdo_contamination.py`, `tcip_citation_gate.py` for `claim_ceiling`) |
| `rationale`, `zero_dollar_next_step` | `systems_check.py`, `systems/tests/test_modality_census.py` |
| `why_not_higher`, `closure_note`, `retired_by_action`, `best_next_action`, `what_it_would_claim`, `text`, `note`/`notes` | `systems_check.py` (+ others) |
| `_what_this_changes` (`publications.json`) | **0 files anywhere in the repository** |
| `cost_realized` (`lanes.json`) | **0 files anywhere in the repository** |

**Result: of the 31 graded fields, 29 sit under a key literal that at least one graph-consuming executable contains; 2 sit under a key literal no executable contains at all** (`publications.json … posted._what_this_changes`, `lanes.json … cost_realized` — the latter is one of my class members, the former is an AGREES field).

⚠ **That 29 is an upper bound and should not be quoted as "29 fields are checked."** Three things degrade it, all measured: (i) generic key names (`note`, `text`, `value`, `what`, `evidence`) hit unrelated code — repository-wide the name `note` appears in 152 files and `value` in 123, almost none of them touching the graph; (ii) containing the literal is not reading *this* record's field; and (iii) **for every one of the 31, what the consumer can do with the field is render or lint the string — no executable anywhere opens the cited artifact and compares.** All three STALE fields are in the "read by something" 29. `not_scannable_because` (S1) is read by `systems_check.py` and asserted on by `test_systems_check.py`, and the defect survived both. **Readership is not checkability**, which is exactly W26d's point, now measured across the class rather than on one field.

---

## Validation evidence

Environment: live checkout `/home/user/Rare-cancers`, HEAD `fb1a3f80` → `56f355f6`, `git status --porcelain` 0 lines throughout. Python 3.11 stdlib, Linux, no network, no paid API, no GPU. Scripts written to and run from `/tmp/claude-0/w57/` only.

### `RUN` — extraction and filtering
```
$ python3 /tmp/claude-0/w57/dump.py
13506
cands 1192
$ python3 /tmp/claude-0/w57/f3.py     # 140-char adjacency
210
Counter({'routes.json': 91, 'plan.json': 26, 'artifacts.json': 20, 'evidence.json': 16, ...})
$ python3 (60-char adjacency, JSON artifacts only)
Counter({'routes.json': 44, 'plan.json': 18, 'blockers.json': 9, 'requirements.json': 7, ...}) total 104
$ python3 /tmp/claude-0/w57/ws.py | tail -1
PAIRS 55
```

### `RUN` — the mechanical screen, and its measured failure on the positive control
```
$ python3 /tmp/claude-0/w57/grade.py
Counter({'OK': 145, 'ARTIFACT_NOT_FOUND': 3})
claims(field,artifact pairs): 148
n with missing numbers: 29
   ARTIFACT_NOT_FOUND artifact-refs.json _why.5 valb-triangle-chem.json
   ARTIFACT_NOT_FOUND routes.json 17.grade.value coverage-scan.json
   ARTIFACT_NOT_FOUND routes.json 51.supporting_evidence.1.what_it_supports schema.json
# technologies.json::26.not_scannable_because is NOT in the 29 — the known-STALE case passes the screen.
```

### `RUN` — the three STALE grades, verbatim
```
### technologies.json :: 26.not_scannable_because | ART research/modalities/emc-ipd-survival.json | KEY curves_supplied
   PROSE: `curves_supplied` in research/modalities/emc-ipd-survival.json, which is 0 today ...
   LIVE : /curves_supplied = 1

$ python3 -c "... emc-systems-map.json objects[18] ..."
map obj18 id/name: {'id': 'OBJ-LINE-HEMCSS', ...}      graph obj18 id: OBJ-LINE-HEMCSS
read_by len 114
PROSE snippet: ['... the 30-entry `read_by` sweep and its `_sweep_limit` stay in research/manuscripts/emc-systems-map.json ...']

$ python3 -c "... emc-mortality-probe.json ..."
summary {"n_queries": 24, ..., "papers_with_death_sentences": 162, "death_sentences_total": 577, ...}
terminal_events type <class 'list'> 162
routes[81].rationale: "... of 162 death-cue sentences in research/literature/emc-mortality-probe.json (34 EMC-titled papers) ..."
```

### `RUN` — representative AGREES arithmetic
```
n_sarcoma distinct: {91}   n_sarcoma_models 176
FISH: Counter({'EWSR1+': 8, 'EWSR1-': 4}) n_runs 12
deaths_by_label sum 52 {... 'treatment_related': 2, 'respiratory_failure': 3 ...}
legs n 17  frac vals {1.0}   trajectory_objects_found 0
by_class n totals = 72 ; built_cif 796689589 B ; built_system 1349596712 B ; leg_result 26890 B
pairs 10  charge_change!=0: 6
step1: {'n_units': 19, 'n_complete': 18, 'n_computable': 18, 'n_blocked': 1, 'realised_usd': 73.79}
PUB-ASO: last_round 34, blockers [], n p1s 7, reviewed_commit 3d5c709b69bc32a00a7776bf47303771d17d87f5
cross_cohort_summary: comparisons 12, comparisons_where_both_exclude_1 0
```

### `RUN` — readership
```
$ grep -rEl "systems/graph" --include=*.py --include=*.mjs --include=*.sh --include=*.yml . | grep -v opus-capacity-campaign | wc -l
66
# per-consumer key-literal grep output quoted in R.5; `_what_this_changes` and `cost_realized`: 0 files repository-wide.
```

### `RUN` — write isolation and cleanup
```
$ date -u; git rev-parse HEAD; git status --porcelain | wc -l
Tue Sep  8 04:50:58 UTC 2026 ; 56f355f65b7b3e47aeb434ac02edf4cf049f40f3 ; 0
$ rm -rf /tmp/claude-0/w57 && ls -d /tmp/claude-0/w57
ls: cannot access '/tmp/claude-0/w57': No such file or directory
```

### `PROPOSED (NOT RUN)`
- Any repair, restatement, gate, test or guard for the three STALE fields. **Not authored, not proposed as code.** Disposition belongs to the graph owner.
- `systems_check.py` in any mode, `--write-views`, `--check`, `scripts/preflight.sh`, `validate-registry.mjs`, `atr_hrd_sarcoma_series.py`. None run.
- Grading the 73 gradable-class fields whose claims resolve to no named key, and the 102 fields in the broad 206 whose artifact is a `.md`/`.py`/`.yml`.

---

## Limitations

- **Denominator honesty.** 31 graded is a *floor*, not the class size. The class as defined has **104** JSON-artifact members and **206** members counting `.md`/`.py`/`.yml` artifacts; I graded only those whose claim resolves to a named key with a comparable live value. The 73 ungraded JSON-artifact fields are **UNKNOWN, not AGREES.** In particular `plan.json`'s 18 members are multi-kilobyte narrative blocks (`blocks[].text`) each carrying many claims; I graded the key-resolvable ones inside them and did not exhaust them. Any headline of the form "3 of 31 are stale" must carry this denominator, and the true stale count over the full class can only be ≥ 3.
- **My filter can miss members.** An artifact referred to by prose name with no file extension, or a quantity more than 60 characters from the mention, is invisible to it. A field it skipped is UNKNOWN.
- **A measured negative on instruments:** literal-number-presence grepping is unfit for this class — it passed the known positive control. Anyone building a screen here must resolve the key, not the number.
- **Grades are valid for the artifact contents between HEAD `fb1a3f80` and `56f355f6` only,** and go stale exactly as the fields they grade do. HEAD moved under me; the graph files and the artifacts I read are outside this campaign's directory and the brief records that no file outside it has changed, but I did not re-read at the end commit.
- **AGREES means the quoted value matches the live value I looked up.** It does not mean the artifact's value is correct, nor that the surrounding scientific reasoning holds. I verified no scientific content and re-opened no grade.
- **R.5's 29 is an upper bound on name-level readership, not a coverage figure**, for the three reasons given; and no executable in the repository compares any graph field to the artifact it cites, which is the class's defining property, not an incidental gap.
- No clinical claim. Nothing here bears on EMC efficacy, safety, selectivity or clinical readiness.

---

## Stop condition

**Set up front:** return the moment (a) the class is enumerated across all 19 files with a stated filter, (b) every gradable member with a resolvable live value is graded AGREES / STALE / UNCHECKABLE with both values quoted for each STALE, (c) the readership question is answered by the brief's key-literal rule applied per-artifact, and (d) scratch is deleted and start/end state recorded — or at ~40 tool calls / ~40 minutes.

**MET on all four legs, inside budget.** 104-field gradable class enumerated; 31 fields graded (24 / 3 / 4); three STALE fields quoted against live values; readership measured over the 66 graph-consuming executables with two fields read by nothing anywhere; scratch deleted; tree clean at start and end.

---

## Tool-call and wall-clock count actually used

**21 tool calls** (target ~40). **Wall clock 5 min 43 s by the UTC clock** — `date -u` start `04:45:15Z`, end `04:50:58Z` (target ~40 min). Real elapsed session time including model latency was longer; I report the clock bracket rather than an estimate. The saving came from scripting the enumeration once and batching the artifact lookups into three Python calls rather than one call per claim.

---

## Next concrete action

**Hand the graph owner the two new STALE fields with their live values and let the owner decide the wording; do not let a lander touch them without a reader.** `objects.json OBJ-LINE-HEMCSS.notes` (30 vs **114**) is the one to take first: it is a single number inside a sentence whose whole argument is *"a second copy here would be a second home for the one fact those guards exist to protect"* — the sentence is right and the number it typed anyway is 3.8× wrong, which is the cleanest available illustration of the class for whoever decides policy. `routes.json` route 81 is second and is a unit fix, not a re-count. **S1 stays with W26d's owner.** ⚠ None of the three is caught by re-rendering: S1 renders on one register line (W26d measured it), and no executable compares any of them to its artifact.

The honest successor for this lane is **finishing the denominator**: grade the 73 gradable-class fields whose claims name no key (they need per-claim reading, not a harness) and then the 102 `.md`/`.py`-artifact members. It is the same method with no new instrument, and until it is done the only defensible statement is "at least 3 stale in a class of at least 104". A cheaper and possibly more valuable variant, if the coordinator wants one unit rather than two: grade `routes.json` alone — 44 of the 104 members live there, it is the largest single reservoir, and it is the file whose prose the route pages reprint most widely.

⛔ What I would *not* dispatch: any worker to build a gate that compares graph prose to artifact values. Three of 31 graded fields are stale; the artifacts are heterogeneous, the claims are natural-language, and the repository's own precedent (`emc_ipd_survival.py:220-228`, cited in the brief) is that the answer to an unfalsifiable field is a named instrument for one measurable thing, not a general checker.
