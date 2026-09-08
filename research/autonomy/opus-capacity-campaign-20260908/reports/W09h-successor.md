<!-- collected 2026-09-08T03:34:17Z by campaign coordinator; agent id ac8b284de14fe3099; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ac8b284de14fe3099.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

- **Worker:** W09h, lane 9 refill, OPUS-CAPACITY-CAMPAIGN-20260908. Taking the second named action of W09g.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No `env` variable names a served model; `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions. The coordinator must extract the runtime model from the transcript.
- **Write isolation honoured.** Nothing written, moved or deleted under `/home/user/Rare-cancers`; no git write operation of any kind; `scripts/preflight.sh` not run; no generated view hand-edited; no correction applied. All execution under `/tmp/claude-0/w09h/`.
- `date -u` **start** `Tue Sep  8 03:19:20 UTC 2026` · **end** `Tue Sep  8 03:27:34 UTC 2026`.
- `git rev-parse HEAD` **start** `84f02dae1809ae050e40254f06310ed849982527` · **end** `e1728471a97ae71db899190a6310d76fcc5c233d`. ⚠ **HEAD moved under me.** I verified nothing I measured changed: `git diff --name-only 84f02dae e1728471` touches **only** `research/autonomy/opus-capacity-campaign-20260908/reports/` (the coordinator committing sibling reports), and `git diff --stat 84f02dae e1728471 -- systems/` is **empty** — `systems/schema/`, `systems/graph/` and `systems/views/` are byte-identical across the move. All counts below are valid at both HEADs.
- `git status --porcelain` **start**: empty (0 lines). **end**: empty (0 lines). `git status --porcelain systems/`: 0 lines at end.
- **Sources read:** the live checkout only. The frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/` was not needed and not read. **No network, no retrieval, no paid API, no GPU.** One incidental egress attempt (`www.proteinatlas.org:443`) was **rejected by the proxy** and was not initiated by any command of mine — it appeared in a proxy notice attached to a `df`/`du` call; I made no retrieval attempt and did not retry anything.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (exit 0), at start. The five long proxy lines (`no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS`) are elided as marked; nothing else removed:

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

The end-of-run `env` output was not re-captured verbatim; the process environment was not modified during the run and no command exported anything. I state that as an unverified-by-second-capture point rather than pasting a block I did not re-run.

---

## Question

Across **all 11 schemas under `systems/schema/` and all 19 graph files under `systems/graph/`**, for every declared field: is it schema-REQUIRED, does any generator or validator actually READ it (measured in code, not inferred from the name), and does it RENDER into `systems/views/`? Classify every field into required-and-consumed / required-and-unconsumed / optional-and-consumed / optional-and-unconsumed with an honest denominator, demonstrate the unconsumed verdict by sentinel substitution and regeneration, and rank the required-and-unconsumed fields by prose volume.

Open because W09g established this for exactly **one** field (`outcome_potential_why`) and named the generalisation as its second successor action. Nobody has measured whether that field is an isolated accident or the visible member of a class.

**Answer, all measured: it is a small class, and `outcome_potential_why` dominates it. Five field names are required-and-unconsumed (38 instances, 0.2% of all field instances); all five have a sentinel-measured blast radius of exactly zero; `outcome_potential_why` carries 8,017 characters of prose — 96% of all prose in that class and 21× the next-largest member. Separately, and more consequential than the census: `systems_check.py --write-views` does not run the invariant checks at all, so deleting `outcome_potential_why` from all 33 records regenerates all 111 views byte-identically at exit 0.**

---

## Prior-work check

| command | what it showed |
|---|---|
| read in full, as dispatched | `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `systems/POLICY-evidence.md`, `reports/W09g-publications-prose-fields.md` (whole), and W09b / W09d / W09e / W09f (W09b, W09d, W09f skimmed for method and closed findings; W09e read for its sentinel method) |
| `grep -rln "systems/graph\|GRAPH_DIR" --include=*.py --include=*.mjs --include=*.js --include=*.sh .` | **64** graph-consuming code files — the set I use as the consumption denominator, rather than assuming `systems_check.py` is the only consumer. It is not: 19 field names are consumed only by non-generator code. |
| `grep -n "outcome_potential_why" systems/systems_check.py` and repo-wide over four extensions | **zero hits** — W09g's finding **independently reproduced**, by a different regex and a different scan (1,527 code files). |
| `grep -n "validate\|\.schema\.json" systems/systems_check.py` | the schema↔collection binding at `:495-522` — publications **are** validated against `publication.schema.json#/$defs/publication`. This refutes the reading that the schema is decorative, and led to the `--write-views` finding in R.5. |

**Not replayed.** W26 is concurrently auditing absence-claim truth in `routes.json`; **I graded no claim's truth anywhere in this report** — my axis is field consumption. W09g's six non-TRUE clauses, W09f's ten, W09e's C5 correction, W09b's audit: all taken as given, none re-litigated, none re-graded. PUB-EMC-CLASSIFICATION (user-rejected), the NR4A Perspective refusal, lane 11's source-index, every denied external route: untouched. No network was used, so no denied route could have been replayed.

---

## Method and inputs

| input | role |
|---|---|
| `/home/user/Rare-cancers` @ `84f02dae` → `e1728471` (`systems/` identical in both) | tree under test, read-only throughout |
| `systems/schema/` — 11 schemas | source of `properties` and `required`, walked recursively including `$defs` and nested sub-objects |
| `systems/graph/` — 19 files, 16,257 field instances | the population censused |
| `systems/systems_check.py` (4,591 lines) | the generator/validator actually executed |
| `systems/views/` — 111 generated files | the render target diffed |
| 1,527 `.py`/`.mjs`/`.js`/`.sh` files repo-wide; 64 of them graph-consuming | the consumption evidence |
| `/tmp/claude-0/w09h/copy/` | scratch copy via `tar --exclude=./.git --exclude=./results`; the only place anything executed or changed |

Python 3.11.15, stdlib only. Procedure:

1. **Schema axis.** Recursively walk each schema collecting every `properties` key (declared) and every `required` array member (required), at every nesting depth including `$defs`.
2. **Population axis.** Parse all 19 graph files and recursively enumerate every key actually present, with occurrence count and total string length. Names beginning `_` are separated out as **metadata/prose annotations**, not fields.
3. **Consumption axis, measured two ways so a false negative is visible.** (a) strict key-access regex `["'.]name` in all 1,527 code files; (b) plain word-boundary `\bname\b` in the same files. Method (a) produced **false unconsumed verdicts** for `aliases`, `grade_pointers`, `published_to`, `asserts_grade`, `cited_in`, `misattributed_as` — I discarded it and report the **conservative (b) numbers throughout**. Under (b) a field counts as consumed if any of the 64 graph-consuming files names it.
4. **Render axis.** For each field, check whether any of its actual committed string values (first 60 chars) appears verbatim anywhere under `systems/views/`.
5. **Demonstration.** Whole-field sentinel substitution on the scratch copy → `python3 systems/systems_check.py --write-views` → `diff -r` against the **committed** `systems/views/`, with a **no-edit control first**, real exit codes on every run, the pristine file restored after every sentinel, and a **restore-verification regeneration** after each. Two **positive controls** on consumed fields prove the method can detect a change.

Note on the scratch copy: a copy excluding `research/` produced a **454-line view diff**, so `systems_check.py` genuinely reads `research/`. Excluding only `.git` and `results/` reproduced the committed views exactly. The reported copy includes `research/`.

---

## Result

### R.1 — The honest denominator `PRIMARY`

| quantity | n |
|---|---|
| schema files | 11 |
| graph files | 19 |
| distinct property names declared across all schemas | 241 |
| distinct names in a `required` array in ≥1 schema | 111 |
| **distinct non-`_meta` field names actually present in `systems/graph/`** | **245** ← the census denominator |
| `_`-prefixed metadata/prose keys present (excluded) | 20 |
| **field instances** (every occurrence, every record, every nesting level) | **16,257** ← the weighted denominator |
| of the 245: declared in ≥1 schema | 171 |
| of the 245: **present but declared in NO schema** | **74** |
| of the 245: required in ≥1 schema | 92 |
| declared in a schema but present in no graph file | 68 |
| **required** in a schema but present in no graph file | 18 |

⚠ **Two denominator caveats I will not round away.** (i) The 18 "required but never present" names are overwhelmingly required *inside optional sub-objects* (`resolution`, `compute_case`, `pending_version`, `per_tech`) that no record instantiates, plus `document.schema.json`'s `audience`/`scope`/`generator`, which govern Markdown frontmatter and not `systems/graph/` at all — that is normal conditional-requirement behaviour, **not** dead schema. (ii) Field names are shared across schemas: 10 names are `required` in one schema and merely declared in another, so "required" below means *required by at least one schema that governs a collection where the field appears*. A name-level census cannot resolve that finer than this, and I do not claim it does.

### R.2 — ⭐ The four-way classification `PRIMARY`

Counted both by distinct field name and by field instance, because the two tell different stories.

| class | names | % of 245 | instances | % of 16,257 |
|---|---|---|---|---|
| required-and-consumed | 87 | 35.5% | 10,911 | 67.1% |
| **required-and-UNCONSUMED** | **5** | **2.0%** | **38** | **0.2%** |
| optional-and-consumed | 122 | 49.8% | 5,010 | 30.8% |
| optional-and-unconsumed | 31 | 12.7% | 298 | 1.8% |

Supporting splits: 179 of the 245 names are read by `systems_check.py` itself; **19 are read only by non-generator code** (linters, `publish_bar.py`, `priority.py`, the autonomy tests) — which is why "read by the generator" is the wrong consumption test and I did not use it. Of the 74 schema-undeclared names present in the graph, 19 are also unconsumed: **fields that no schema declares and no code reads**.

**The verdict on the generalisation W09g asked for: `outcome_potential_why` is NOT a one-off, but the class it belongs to is small — 5 names, 0.2% of field instances. The repository is, on this axis, in good shape.** That is the honest headline, and it is a largely negative result.

### R.3 — The five required-and-unconsumed fields, ranked by prose carried `PRIMARY`

The ranking the dispatch asked for. "Prose" = total committed string characters in that field across all records; a large unread prose field is where a wrong claim can sit unchecked.

| rank | field | graph file | required by | occurrences | **total chars** | mean chars | measured blast radius |
|---|---|---|---|---|---|---|---|
| **1** | **`outcome_potential_why`** | `publications.json` | `publication.schema.json` | **33** | **8,017** | 243 | **0 lines** (S1) |
| 2 | `posted_by` | `publications.json` | `publication.schema.json` (inside `posted`) | 1 | 150 | 150 | **0 lines** (S5) |
| 3 | `running_job` | `strategies.json` | `research-object.schema.json` | 2 | 134 | 67 | **0 lines** (S6) |
| 4 | `published_at_utc` | `publications.json` | `publication.schema.json` (inside `posted`) | 1 | 20 | 20 | **0 lines** (S7) |
| 5 | `changed_on` | `blockers.json` | `blocker.schema.json` (inside `kind_history`) | 1 | 10 | 10 | **0 lines** (S8) |

⭐ **`outcome_potential_why` carries 8,017 of the class's 8,331 characters — 96.2% — and 21× the next member.** Ranks 2–5 are a timestamp, an actor name, a short job label and a date: **short, structured, factual, and essentially unable to carry a wrong scientific claim.** Rank 1 is 33 free-prose justifications averaging 243 characters each. **On this axis the class has exactly one member that matters, and W09g had already found it.** Ranks 2–5 are a true negative, and I report them as such rather than dressing them up as four more findings.

For completeness, the largest **optional**-and-unconsumed prose fields (same measurement, no requirement backing): `provenance_flag` (`evidence.json`, 12 occ, 4,698 chars), `abstract_note` (`technologies.json`, 8 occ, 2,646), `what_this_registry_adds` (`integrity.json`, 2 occ, 1,002), `cost_realized` (`lanes.json`, 17 occ, 832), `exon_level` (`objects.json`, 19 occ, 630), `misattribution_note` (`evidence.json`, 1 occ, 464), `control_note` (`artifacts.json`, 2 occ, 438), `correction_owed` (`routes.json`, 1 occ, 336). **`provenance_flag` and `abstract_note` together carry 7,344 unread characters — comparable to `outcome_potential_why` — and neither is required, so neither is even guaranteed to exist.** If the concern is "prose nobody checks", the optional class is nearly as large as the required one and is not visible from the schema at all.

Twenty-three names appear in **no** `.py`/`.mjs`/`.js`/`.sh` file anywhere in the repository: `outcome_potential_why`, `abstract_note`, `what_this_registry_adds`, `cost_realized`, `misattribution_note`, `correction_owed`, `abstract_verdict`, `posted_by`, `title_as_posted`, `running_job`, `resolution_home`, `coi`, `read_url`, `published_at_utc`, `resolved_on`, `changed_on`, `qeios_id`, `declarations_as_posted`, `has_control`, `kind_history`, `resolved_conflicts`, `sub_forms`, `version_number`.

### R.4 — The demonstration: nine sentinel runs, two positive controls, all restored `PRIMARY`

Control first, then each sentinel, each followed by a restore-verification regeneration. Every exit code is the real one.

| run | field · graph file | substitutions | `systems_check` exit | `diff -r` exit | changed lines | files touched | sentinel visible in views |
|---|---|---|---|---|---|---|---|
| **CONTROL** (no edit) | — | 0 | **0** | **0** | **0** | 0 | — |
| **S1** | `outcome_potential_why` · publications | 33 | 0 | **0** | **0** | 0 | 0 |
| **S2** | `provenance_flag` · evidence | 12 | 0 | **0** | **0** | 0 | 0 |
| **S3** | `abstract_note` · technologies | 8 | 0 | **0** | **0** | 0 | 0 |
| **S4** | `title_as_posted` · publications | 1 | 0 | **0** | **0** | 0 | 0 |
| **S5** | `posted_by` · publications | 1 | 0 | **0** | **0** | 0 | 0 |
| **S6** | `running_job` · strategies | 2 | 0 | **0** | **0** | 0 | 0 |
| **S7** | `published_at_utc` · publications | 1 | 0 | **0** | **0** | 0 | 0 |
| **S8** | `changed_on` · blockers | 1 | 0 | **0** | **0** | 0 | 0 |
| **P1 positive control** | `rationale` · modalities | 217 | 0 | **1** | **206** | 1 | 103 |
| **P2 positive control** | `what_it_would_claim` · publications | 33 | 0 | **1** | **232** | 84 | 116 |

Every run ended `RESTORE: check_exit=0 diff_exit=0`, i.e. the pristine graph file was put back and regeneration reproduced the committed views exactly. **The positive controls are what make the eight zeros meaningful**: the same harness, on consumed fields, produces 206 and 232 changed lines with the sentinel string plainly visible in the diff. A zero from this harness is a measured zero, not a broken measurement.

**S4 resolves an ambiguity my own census raised.** `title_as_posted` was the single unconsumed field whose committed value *does* appear verbatim under `systems/views/`. The sentinel shows changing it moves **nothing**: the string in the views is a **coincidental collision** with the same title carried by a different, consumed field. Value-appearance is therefore a **proxy that can be wrong in the false-positive direction**, and I flag it as such rather than reporting it as a render.

### R.5 — ⭐ The finding that outranks the census: `--write-views` does not run the checks `PRIMARY`

This was not in my dispatch; it fell out of probing whether `required` is enforced at all, and it changes how every "blast radius" result in this lane should be read.

| probe | `systems_check` args | exit | views diff | what it printed |
|---|---|---|---|---|
| delete `outcome_potential_why` from **all 33** records | `--write-views` | **0** | **0** (byte-identical) | one line: `systems_check: wrote 111 view(s)` |
| the same deletion | *(no args)* | **1** | — | **33** × `ERROR [S3] publications/PUB-… (root): 'outcome_potential_why' is a required property` |
| delete `what_it_would_claim` from all 33 | `--write-views` | **1** | — | `KeyError: 'what_it_would_claim'` — an **uncaught crash**, not a validation message |
| delete `provenance_flag` (optional) from 12 records | `--write-views` | 0 | 0 | nothing |

Three consequences, stated exactly:

1. **The schema's `required` array IS enforced** — `check_schemas` at `systems_check.py:495-522` validates `publications` against `publication.schema.json#/$defs/publication` with the `jsonschema` reference implementation, and it fires cleanly. W09g's field is not unvalidated for *presence*.
2. **But `--write-views` skips the invariants entirely.** The regeneration mode that produces the views — the mode this lane's blast-radius method uses, and the mode a person runs after editing the graph — emits one line and exits 0 with 33 required fields missing. **Presence-enforcement and view-regeneration are two disjoint modes**, and only the first catches anything.
3. **Where "required" appears to bite in the generator, it is a `KeyError`, not a guard.** `what_it_would_claim` "fails" under `--write-views` only because a bare `p["what_it_would_claim"]` raises. That is an accident of subscript style, not a check.

⚠ **Baseline honesty.** The plain-mode run on my scratch copy exits **1** on the *unmodified* tree with 158 errors, of which **143 are `[D4]` "has no frontmatter"** raised against **this campaign's own untracked report files** in `research/autonomy/opus-capacity-campaign-20260908/`. That non-zero baseline is an artefact of the working tree's uncommitted campaign output, not evidence about the committed graph, and I do not claim it is anything more. I did not run plain mode against the real tree.

### R.6 — What this does and does not say about the four defective clauses

W09g graded four clauses in `outcome_potential_why` defective. My measurement confirms, independently and across all 33 records at once, that **correcting or corrupting any of them changes zero generated bytes** — the view-drift check cannot see them. It adds that **a required field can be deleted outright, from every record, and `--write-views` still exits 0**. It says **nothing** about whether those clauses are true; that is W09f/W09g's grading and W26's live audit, and I did not touch it.

**I am not proposing a validator and I have written none.** Whether the repair is correcting the prose, giving the field a checker, running the invariants inside `--write-views`, or deciding an unread justification field is fine as an unread justification field, is the graph owner's decision. The census and the demonstration are the deliverable.

---

## Validation evidence

**RUN** (all in `/tmp/claude-0/w09h/`, Python 3.11.15, Linux, no network):

| # | command | exit |
|---|---|---|
| 1 | `tar --exclude=./.git --exclude=./results -cf - . \| tar -xf - -C /tmp/claude-0/w09h/copy` | 0 |
| 2 | `cd /tmp/claude-0/w09h/copy && python3 systems/systems_check.py --write-views` (control) | **0**, `wrote 111 view(s)` |
| 3 | `diff -r /home/user/Rare-cancers/systems/views /tmp/claude-0/w09h/copy/systems/views` (control) | **0**, 0 lines |
| 4 | `python3 /tmp/claude-0/w09h/census.py` (schema+graph+code+views census) | 0 |
| 5 | `python3 /tmp/claude-0/w09h/recount.py` (word-boundary consumption recount) | 0 |
| 6 | `python3 /tmp/claude-0/w09h/sentinel.py` (control + S1–S4 + P1, each with restore-verify) | 0 |
| 7 | `python3 - <<'…'` re-using `sentinel.run` for S5–S8 + P2 | 0 |
| 8 | `python3 /tmp/claude-0/w09h/probe.py` and `probe2.py` (deletion probes, both modes) | 0 |
| 9 | `git diff --stat 84f02dae e1728471 -- systems/` | 0, **empty output** |

Verbatim key output, S1 and its positive control P2:

```
S1-required   field=outcome_potential_why substitutions=33 check_exit=0 diff_exit=0 changed_lines=0 files=0 sentinel_lines=0
   RESTORE: check_exit=0 diff_exit=0 (0/0 = pristine restored)
P2-POSCONTROL field=what_it_would_claim   substitutions=33 check_exit=0 diff_exit=1 changed_lines=232 files=84 sentinel_lines=116
   RESTORE: check_exit=0 diff_exit=0 (0/0 = pristine restored)
```

```
args=['--write-views'] deleted=33 exit=0  lines_mentioning_field=0   out_lines=1
args=[]                deleted=33 exit=1  lines_mentioning_field=33  out_lines=401
    "ERROR [S3]  publications/PUB-ANDGATE (root): 'outcome_potential_why' is a required property"
```

**PROPOSED (NOT RUN):** any validator, any correction to any graph file, any `scripts/preflight.sh` run, any plain-mode `systems_check.py` run against the real tree, any sentinel of the 39 remaining unconsumed fields.

**Environment incident, recorded not hidden.** Two commands mid-run failed with `ENOSPC` on the harness temp filesystem (0 MB free) after my first 612 MB full-tree copy. I recovered by deleting that copy and rebuilding a 9 MB + `research/` copy, then **re-established the control run from scratch** (row 2/3 above) before any sentinel. No measurement crossed the incident.

---

## Limitations

- **The consumption axis is name-based, not dataflow-based.** A field accessed dynamically — `for k, v in record.items()`, a `getattr`, a key built by string concatenation — would be scored unconsumed. `systems_check.py` contains 22 `.items()` calls, so this is a live risk, not a theoretical one. **The sentinel demonstration is what closes the gap, and it closes it for the 9 fields I substituted, not for the other 39 unconsumed names.** Those 39 carry a name-grep verdict only.
- Consumption is measured **repo-wide over `.py`/`.mjs`/`.js`/`.sh`**. A field read by a GitHub Actions YAML expression, a `jq` filter inside a workflow, or a human reader is scored unconsumed. **"Unconsumed" here means "no code in those four languages reads it", never "nobody uses it" and never "it is worthless".** A justification field a human reads before approving a paper is doing real work that this census cannot see.
- The census is **name-level**, so a name required in one schema and optional in another is scored required (10 such names). It does not resolve per-collection requirement.
- Render is measured by **regeneration diff** (strong, 9 fields) and by **value substring match** (a proxy, all fields) — and S4 proved the proxy yields false positives. Where the two disagree, the sentinel wins.
- **I graded no claim's truth.** Nothing here says any clause in any field is right or wrong. That is W09f/W09g's completed grading and W26's live audit.
- The plain-mode baseline exit 1 is dominated by this campaign's own untracked files; it is **not** evidence about the committed tree, and I did not test the committed tree in plain mode.
- No wet lab, no clinical claim, no patient data, no external retrieval. Nothing here bears on EMC efficacy, safety or readiness.
- `results/` was excluded from the scratch copy. The control run proves the views do not depend on it; it does **not** prove no invariant does.

---

## Stop condition

**Set up front:** stop when (a) every field name in `systems/graph/` is classified on the required × consumed axes with counts and a stated denominator, (b) at least three unconsumed fields have a sentinel-substitution + regeneration demonstration with a no-edit control and real exit codes, and (c) the required-and-unconsumed set is ranked by prose volume — **or** at ~40 tool calls / ~40 minutes, whichever comes first.

**MET, and exceeded on (b).** 245 names and 16,257 instances classified; **nine** sentinel runs (all 5 required-and-unconsumed fields plus 3 optional and 1 ambiguous) against a clean control, with **two positive controls** the census did not require; the ranking delivered. Returned on meeting it, at roughly half the tool budget.

---

## Tool-call and wall-clock count actually used

**25 tool calls** (all `Bash`; no file written inside the repository, no git write, no network). **Wall clock 03:19:20Z → 03:27:34Z = 8 min 14 s** of execution, plus report drafting. Budget was ~40 calls / ~40 min.

---

## Next concrete action

**One task, for the graph owner, not for a worker to execute unasked:** decide whether `systems_check.py --write-views` should run `check_schemas` before it writes. The measurement that motivates it is in R.5 and takes one command to reproduce — delete `outcome_potential_why` from all 33 records, run `--write-views`, observe exit 0 and 111 byte-identical views; run it again with no arguments, observe exit 1 and 33 `[S3]` errors. **This is a one-line-of-judgement decision about mode wiring, and it is worth more than any per-field validator**, because it restores presence-enforcement to the mode people actually run after editing the graph — for all 92 required names at once, not just the one W09g found. I have written no patch and propose none; the tradeoff (regeneration would start failing on a tree whose untracked files trip 143 unrelated `[D4]` errors) is real and is the owner's to weigh.
