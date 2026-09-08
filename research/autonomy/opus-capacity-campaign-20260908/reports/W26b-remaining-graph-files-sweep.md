<!-- collected 2026-09-08T03:38:26Z by campaign coordinator; agent id a5e37f6a619a78056; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a5e37f6a619a78056.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Report follows.

---

## Worker

- **Worker:** W26b, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: graph-file false-absence audit, extending W09b → W09f → W26 onto **every `systems/graph/*.json` except `publications.json` and `routes.json`** (17 files).
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model — `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions. The coordinator must extract the actual runtime model from the transcript.
- **Write isolation honoured on the Git tree.** Nothing written, moved or deleted under `/home/user/Rare-cancers`; `git status --porcelain` empty at start and end; no git write operation of any kind; `scripts/preflight.sh` not run; no view hand-edited; **no correction applied**. All execution under `/tmp/claude-0/w26b/` (scratch copy, `tar --exclude=./.git --exclude=./results`) and `/tmp/claude-0/w26bx/` (scripts).
- ⚠ **One disclosed deviation, outside the repository.** The container's harness temp filesystem hit `ENOSPC` on my second tool call ("*the temp filesystem … is full (0MB free)*"), so I created an empty directory `/home/user/.w26b-tmp` and exported `CLAUDE_CODE_TMPDIR` to it to keep Bash usable. It is outside `/home/user/Rare-cancers`, it never held repository content, and I **removed it at the end** (`rmdir … → REMOVED`, then `git status --porcelain | wc -l` → `0`).
- No network, no retrieval, no paid API, no GPU, no human contact, no publication. No clinical claim; there is no wet lab.

`date -u` — start `Tue Sep  8 03:26:05 UTC 2026`, end `Tue Sep  8 03:33:33 UTC 2026`.

`git rev-parse HEAD` — start `ff6bb018936451d0c2d60fb4a2aa7ae8ba932d7f`, end `215ed8e78f83d1e5acdbb726317dfd0eeed8f6a1`.

`git status --porcelain` — start: **empty**. End: **empty**.

⚠ **HEAD moved under me twice and I report it rather than hide it, and I verified nothing I measured changed.** At end: all seven graph files I sentinelled are byte-identical to the copies I measured (`cmp` → `modalities IDENTICAL`, `strategies IDENTICAL`, `requirements IDENTICAL`, `blockers IDENTICAL`, `artifacts IDENTICAL`, `forecasts IDENTICAL`, `technologies IDENTICAL`), and `diff -rq systems/views /tmp/claude-0/w26b/views-committed` → `VIEWS_UNCHANGED_SINCE_SNAPSHOT`. ⚠ Also note the COMMON-BRIEF names a frozen read commit `92abbcb9…`; this checkout's HEAD was already `ff6bb018` when I started, so the brief's frozen-commit line is stale and I read the live tree instead, as recorded above.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (exit 0), verbatim except five long proxy/JVM lines (`no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS`), which are marked elided and nothing else removed:

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
CLAUDE_CODE_TMPDIR=/home/user/.w26b-tmp        ← set by me mid-run (ENOSPC workaround), absent at start
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

---

## Question

**In the seventeen `systems/graph/*.json` files that are neither `publications.json` nor `routes.json`, how many prose clauses assert a categorical absence about a body of evidence; which of them are refuted by committed evidence; and how many committed view lines does correcting each one actually cost?**

It is open because W09f closed `publications.json` (45% defective on the clauses it examined) and W26 closed `routes.json` (40% of clauses, 0.30% of sentences). Those two files are 676 KB of a 1.57 MB graph. The remaining 890 KB — including the two largest single files, `modalities.json` (187 KB, 217 records) and `plan.json` (182 KB) — had never been swept, and the structural explanation W09f and W26 converged on ("does the field's row supply its scope?") predicts different answers for `modalities.json` (a row per drug class), `strategies.json` (a row per *family*, fanning out to many routes) and `plan.json` (no rows at all — six prose blocks).

---

## Prior-work check

Ran, and read in full: `research/autonomy/opus-capacity-campaign-20260908/COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `systems/POLICY-evidence.md`, and `reports/W09b-absence-claim-audit.md`, `W09f-publications-false-absence-audit.md`, `W09g-publications-prose-fields.md`, `W26-routes-absence-sweep.md`.

- `ls -la /tmp/claude-0/w26x/` → W26's `scan_absence.py`, `sentinel.py`, `sentinel2.py`, `hits.json` still present. **I read W26's scripts and adapted them rather than reinventing the method**, so the term set, the sentence splitter, the sentinel protocol and both controls are the *same instrument* as the routes sweep. That is deliberate: the cross-file comparison this task asks for is only valid if the instrument is identical.
- `python3 -c "…"` over `systems/graph/*.json` → confirmed shapes before walking: 15 files are top-level `list`, four are top-level `dict` (`artifact-refs`, `integrity`, `plan`, `relations`); my walker handles both.
- `grep -n "_clip(" systems/systems_check.py` → seven clip sites; `grep -n "zero_dollar_next_step\|modality-census" systems/systems_check.py` → the census renderer at `:3832`/`:3864`.
- **Not replayed:** `publications.json` and `routes.json` are DONE (W09f/W09g/W26) and I neither re-audited nor sentinelled either. W09h's concurrent question (schema field *consumption*) is different from mine (absence-claim *truth*); where the two touch — my finding that 14 of 45 categorical clauses reach no view — I state it as a measurement of my own clauses, not as a schema census.
- **Closed items confirmed and not touched:** the NR4A Perspective refusal, PUB-ASO ownership, the frozen external-validation comment, the pazopanib/sunitinib/trabectedin/Wagner/CTARC unrecovered sources. No source was fetched; every counter-citation below is a committed file quoted at `file:line`.

---

## Method / inputs

| input | role |
|---|---|
| `/home/user/Rare-cancers` @ `ff6bb018` → `215ed8e7` | tree under test, read-only |
| the **17** graph files (all but `publications.json`, `routes.json`): **526 records, 8,770 string fields, 12,373 sentences** | the sources under test |
| `systems/systems_check.py` | the generator actually run (`--write-views`) |
| `systems/views/` (**111 written files**) | the generated layer, copied to `/tmp/claude-0/w26b/views-committed` before any run |
| `/tmp/claude-0/w26b/repo` | scratch copy, `tar --exclude=./.git --exclude=./results` (`results/` excluded for disk; the no-edit control proves the exclusion does not perturb generation) |
| `/tmp/claude-0/w26bx/scan.py`, `sentinel.py` | the two scripts I wrote (adapted from W26's) and ran |
| counter-evidence corpus | committed files only: `systems/graph/*.json`, `research/modalities/emc-site-curation.json`, `systems/views/**` |

Python 3.11 stdlib only, Linux, no network. Enumeration: walk every string leaf; split on `(?<=[.!?;])\s+|\n+`; match **W26's unchanged 60-term absence regex**; then **hand-classify every hit**.

Target class, W09b's, unchanged: *a clause asserting, about a body of evidence — literature, corpus, archives, registries, cohorts, "anyone", "the field" — that some thing is not recorded, found, reported, built or studied there.* A **disclaimer**, a **self-scoped** statement ("nothing in this repository…"), an **ordinary measurement** ("ZERO EMC lines"), and a **prediction about the future** are **not** this class.

---

## Result

### R.1 — The population, and the fires-versus-survives ratio `PRIMARY`

| file | records | string fields | sentences | regex fires | distinct fields firing |
|---|---:|---:|---:|---:|---:|
| `artifact-refs.json` | 4 | 29 | 53 | 2 | 2 |
| `artifacts.json` | 56 | 326 | 524 | 21 | 21 |
| `blockers.json` | 21 | 162 | 277 | 15 | 11 |
| `claims.json` | 14 | 84 | 106 | 1 | 1 |
| `evidence.json` | 26 | 363 | 538 | 2 | 2 |
| `forecasts.json` | 28 | 432 | 530 | 16 | 16 |
| `instruments.json` | 32 | 310 | 373 | 4 | 4 |
| `integrity.json` | 4 | 55 | 85 | **0** | 0 |
| `lanes.json` | 18 | 153 | 196 | 1 | 1 |
| `modalities.json` | 217 | 2,765 | 3,073 | 34 | 30 |
| `objects.json` | 19 | 237 | 279 | **0** | 0 |
| `plan.json` | 6 | 301 | 2,428 | 39 | 14 |
| `relations.json` | 8 | 210 | 272 | 3 | 3 |
| `requirements.json` | 16 | 332 | 424 | 13 | 13 |
| `roadmap.json` | 15 | 159 | 197 | 5 | 4 |
| `strategies.json` | 14 | 304 | 360 | 25 | 24 |
| `technologies.json` | 28 | 2,548 | 2,658 | 11 | 9 |
| **TOTAL** | **526** | **8,770** | **12,373** | **192** | **155** |

⭐ **My fires-versus-survives ratio: 192 sentences fire, 61 survive the first reading, 45 survive the second. 131 of 192 firings (68%) are not absence-of-evidence claims at all** — a slightly *worse* over-fire rate than W26's 62% on `routes.json` and much worse than W09f's on `publications.json`, and for a locatable reason: **`plan.json` alone contributes 39 firings and exactly one survives.** `plan.json` is a run log written as prose, so its "zero", "never run", "unmeasured" are almost all internal run records and numeric measurements.

The four false-fire shapes, each quoted from my own hit list:

- **ordinary measurements** — `artifacts.json` `ART-DEPMAP-SARCOMA-DEP.note`: *"⚠ 91 sarcoma lines and ZERO EMC lines"*; `plan.json` block 71: *"BRD4 has 24 ternary structures while BRD2 and BRD3 have zero"*;
- **self-scoped statements** — `technologies.json` `TECH-CONDENSATE-RESOLUTION.evidence[3]`: *"No published EMC condensate measurement stratified by 5' fusion partner **is recorded anywhere in this repository**"* — ⭐ **this is the exemplary correct form in my whole population, and I name it so the exclusion is checkable**; also `blockers.json` `BLK-NO-FIELD-ATTENTION-MEASUREMENT.retired_by_action`: *"NO measurement of any kind **anywhere in this repository**"*;
- **disclaimers** — the seven-times-repeated `strategies.json` `*.limitations[n]`: *"Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness"*;
- **predictions about the future** — `forecasts.json` `FC-RECONSTRUCTED-IPD.scenarios.optimistic.rationale`: *"Nothing external accelerates this — no paper, no model and no collaborator"*; `FC-ATOM-MAPPER`: *"…is not anyone's priority."* I exclude these by W26's rule and name them so the exclusion is auditable. They are unhedged forecasts, which is a different defect and not mine to route.

**Survivors: 61.** Of those, **16 are bounded or explicitly self-scoped and stand as written** (e.g. `blockers.json:66` *"printed by **no reachable** series"*; `modalities.json` `MOD-ILP` *"No cohort **in the clinical registry** carries a primary anatomical SITE field"*; `evidence.json` `EV-ZAIENNE-2022` *"measured in CI on 2026-08-03 against Europe PMC and PubMed (0 hits…)"* — dated, named corpus, instrument). **45 are CATEGORICAL.**

### R.2 — The 45 categorical clauses, classified `PRIMARY`

**Tally: 3 FALSE · 13 OVER-SCOPED · 29 UNVERIFIABLE.**
Defective share **16/45 = 36%** of categorical clauses, **16/12,373 = 0.13%** of sentences.

#### ⛔ FALSE — 3 clauses, each refuted by a committed file

| # | record · field · line | clause, quoted | refutation (committed, quoted) |
|---|---|---|---|
| F1 | `modalities.json` `MOD-ISOLATED-LUNG-PERFUSION.zero_dollar_next_step` | *"Metastatic site appears once in one cohort's free-text note and **nowhere as data**; **time-to-metastasis appears nowhere at all**." (dated "measured 2026-08-09")* | R.3 |
| F2 | `modalities.json` `MOD-BRACHYTHERAPY.zero_dollar_next_step` | *"**No cohort carries dose, modality or margin detail**, so there are no inputs for a dose-response fit." (dated "established 2026-08-09")* | R.4 |
| F3 | `strategies.json:21` `ST-PROXIMITY.limitations[0]` | *"No molecule in this family has been shown to bind NR4A3 at all — the pocket every route here depends on **has no known ligand of any kind**."* | R.5 |

#### ⚠ OVER-SCOPED — 13 clauses

| # | record · field | clause, quoted | why, and the smallest fix |
|---|---|---|---|
| 1 | `modalities.json` `MOD-ILP.zero_dollar_next_step` | *"⭐ The real $0 step is re-curating site from the pooled series' open-access primary reports — the single highest-value curation this row depends on."* (with *"THE FIELD … DOES NOT EXIST (measured 2026-08-09)"*) | the registry negative is **true as written**; the row is **stale** — the curation it calls the open next step was committed on **2026-09-04** as `research/modalities/emc-site-curation.json`. Fix: append *"⭐ TAKEN 2026-09-04 — `research/modalities/emc-site-curation.json`."* |
| 2 | `artifacts.json` `ART-HORMONE-PARTNER-LANE.note` | *"…is reported in one EMC patient **in the world literature**…"* | "the world literature" is not a corpus this repository has enumerated. W26 ruled the identical phrasing OVER-SCOPED in `routes.json` `RT-HORMONE-PARTNER.grade.value`. Fix: adopt that record's own exemplary paired half — *"…and in ZERO of the 84 partner-genotyped EMC cases across the two cohorts this repository cites (Wilson 95% upper bound 4.4%)"* — and delete "in the world literature". |
| 3 | `modalities.json` `MOD-SERM-SERD.rationale` | same *"in the world literature"* clause | third copy of the same claim. Same fix. |
| 4 | `artifacts.json:413` `ART-SYSTEMIC-THERAPY-POOLING.note` | *"⛔ **No randomised evidence exists** for any systemic therapy in this disease…"* | the field's own artifact is a *pooling* of a retrieved corpus; no RCT census is committed. Fix: *"⛔ **No randomised evidence for any systemic therapy in this disease has been retrieved into this pool**, and nothing here supports a claim that any agent is better than another, or than none."* — one scope phrase; the ⛔ disclaimer that follows is already correct. |
| 5 | `modalities.json` `MOD-SGK1.rationale` | *"…published two decades ago and **never followed up by anyone**."* | ⚠ **I differ from W26 here and say so.** W26 ruled the near-identical `routes.json` `RT-SGK1.rationale` **FALSE** via its R.3 refutation, but R.3's evidence (PMID 29937513, Urbini 2018) is a follow-up on **RET**, not on SGK1. Applied to an SGK1-specific sentence that refutation does not hold, so I grade this **OVER-SCOPED, not FALSE**. Fix, which the sibling `RT-ALK-HIT.rationale` already prints correctly: *"…and **with no follow-up retrieved in this repository's corpora**."* |
| 6 | `modalities.json` `MOD-TOPO2-NON-ANTHRA.rationale` | *"…and **no EMC observation exists**."* | Fix: *"…and **no EMC observation has been retrieved in the corpora this repository holds, as of 2026-09-08**."* |
| 7 | `modalities.json` `MOD-AR-ANTAGONIST.rationale` | *"**No androgen-receptor dependency is reported in EMC** and none of the known 5′ partners is an androgen-responsive locus"* | the second half is checkable against the committed partner list; the first is a literature negative with no census. Fix: *"No androgen-receptor dependency **has been retrieved for EMC**, and …". |
| 8 | `modalities.json` `MOD-BRACHYTHERAPY` (second clause, same field) | *"What remains is a literature search for brachytherapy arms in this histology."* | ⚠ **stale**: `artifacts.json:534` records *"⭐ PARTICLE/BRACHYTHERAPY CENSUS RUN: brachytherapy and proton beam each reported ONCE in this histology, as case reports rather than registry arms"*. Fix: *"⭐ TAKEN — the census is run (`ART-RT-…`, `artifacts.json:534`): one brachytherapy case report, no registry arm."* |
| 9 | `modalities.json` `MOD-PHOSPHATASE-RECRUIT.rationale` | *"no correctly assembled induced complex on this target **has been produced by anyone**."* | same claim as R9/ST-PROXIMITY; no census. |
| 10 | `requirements.json` `R9.claim_ceiling` + `R9.claim_ceiling_raw` | *"⛔ **no NR4A3 ternary has been correctly assembled by anyone**."* | two fields, one claim. Fix: *"⛔ **no correctly assembled NR4A3 ternary has been retrieved**, and none has been produced here."* |
| 11 | `strategies.json:22` `ST-PROXIMITY.limitations[1]` | *"**No NR4A3 ternary complex has been correctly assembled by anyone**, so every geometry claim in this family is a prediction from an instrument that has never been pointed at this system."* | fourth copy of the same claim; the clause after the comma is exemplary and needs no change. |
| 12 | `strategies.json:60` `ST-OCCUPANCY.limitations[1]` | *"**Nobody has stated** how much paralogue selectivity this family would need, so 'the requirement is smaller here' is not a claim this repository can make."* | ⭐ the *second* half is the correct self-scoped form and the first half contradicts it by reaching to "nobody". Fix: *"**This repository has not stated** how much paralogue selectivity this family would need, and no published statement of it has been retrieved, so …"*. |
| 13 | `technologies.json` `TECH-RECONSTRUCTED-IPD.not_scannable_because` | *"…how many published EMC series print a numbers-at-risk table beside their curve — and **nobody has taken it**."* | Fix: *"…and **it has not been taken here**."* — the honest claim, and the one the same record's `evidence[1]` already makes. |

#### ❓ UNVERIFIABLE — 29 clauses (no committed census either way)

Representative, with file and record: `blockers.json` `BLK-FUNCTIONAL-ACTIONABILITY.statement_about` *"a functional cell assay **nobody has run**"*; `BLK-NO-FIELD-ATTENTION-MEASUREMENT.name` *"a corpus-wide term census **nobody has run**"*; `BLK-UNSIZED-REQUIREMENT` (three clauses) *"three **unmeasured** dose-responses"*; `forecasts.json` `FC-FE-CRYPTIC-POCKET` *"**nobody has assembled** them into a benchmark"*, `FC-EMC-EXPRESSION-DATA` *"neither is on **anyone's** published roadmap"*, `FC-E3-RECRUITER-STRUCTURE` *"Structures of proteins **nobody has solved**"*, `FC-RECONSTRUCTED-IPD` *"**nobody has counted** the tables"*; `modalities.json` `MOD-RET` *"**nobody has measured it**"* and *"a molecular state this disease **is not reported to be in**"*, `MOD-PRMT5-MAT2A` *"it has simply **never been asked**"* and `.requires[0]` *"**unmeasured** in EMC"*, `MOD-ARGININE-DEPRIVATION.requires[0]` *"which is **unmeasured**"*, `MOD-MCL1-BCLXL` *"**Nobody has asked** which one"*, `MOD-WNT-BETA-CATENIN` *"leaves the question **unrun**"*, `MOD-AROMATASE` *"a receptor EMC **has not been shown to depend on**"*, `MOD-TF-LBD-OCCUPANCY` *"a requirement **nobody has sized**"*; `plan.json` block 41 *"That benchmark **does not exist yet**"*; `requirements.json` `R6.claim_ceiling` + `.claim_ceiling_raw` *"a term **nobody has computed**"*; `strategies.json` `ST-OCCUPANCY.limitations[0]` *"**has never been tested by anyone**"*, `ST-REPURPOSING.limitations[1]` (two clauses) *"**has never been read** in EMC tissue"* / *"**does not exist**"*, `ST-RADIOLIGAND.limitations[0]` *"Target expression in EMC is **unmeasured**"*, `ST-MICROENV.limitations[2]` *"**has never been measured** in this disease"*, `ST-LOCOREGIONAL.limitations[0]` *"whose size **has not been established**"*, `ST-CARE-DELIVERY.thesis` *"**no systemic agent has a demonstrated survival benefit**"*; `technologies.json` `TECH-JUNCTION-PMHC` *"the same **unmeasured** premise"*, `TECH-RECONSTRUCTED-IPD.evidence[1]` *"**nobody has counted**"*.

**Smallest correct restatement — one template covers all 29**, and this repository already wrote it: `research/modalities/nr4a3_fusion_targets.py` → `⛔_how_to_state_it`, *"a bounded negative about a SEARCH … **AN ABSENT READING IS NOT A READING OF ABSENCE.**"* Concretely, for `ST-RADIOLIGAND.limitations[0]`: *"Target expression in EMC — **no measurement has been retrieved in the corpora this repository holds, as of 2026-09-08**."* Each substitution is a scope word, not a finding.

### R.3 — `MOD-ISOLATED-LUNG-PERFUSION` says a fact appears "nowhere at all" and a committed file prints it twice `PRIMARY`

The field, in full: *"⛔ THE FIELDS THIS ROW CALLS 'ALREADY CURATED' DO NOT EXIST (measured 2026-08-09). Metastatic site appears once in one cohort's free-text note and nowhere as data; **time-to-metastasis appears nowhere at all**. ⭐ The real $0 step is re-curating metastatic site from the open-access primary reports."*

`research/modalities/emc-site-curation.json` — committed **2026-09-04** (`git log -1` → `Fri Sep 4 00:34:12 2026 +0000 14a3f172`), and cited *by name* from `routes.json` `RT-METASTASECTOMY.grade.value` — states, verbatim, under `⛔_what_is_still_not_computable`:

> `time_to_metastasis`: *"printed as a median in one series (**5.9 years, chiusole2020**) and as a median time to distant metastasis in another (**28 months, bishop2019**), and **nowhere per patient**."*

and it *is* the metastatic-site curation the row calls the open next step: `_what` — *"Anatomical site of the primary tumour and of the metastases … transcribed from the primary reports of the open-access series"* — carrying `pooled_extremity_fraction.extremity_strict` = **194/271, 71.6% (Wilson 95% CI 65.9–76.6)**, per-cohort 78.0 / 67.8 / 78.0, plus a `lung_confined_readings` block for three series.

⭐ **The correct word is "per patient" and the file that supplies it is in the same repository.** Two medians are printed; "nowhere at all" is refuted by a committed file, and site is curated as data with counts, not as one free-text note.

**Smallest correct restatement:** *"⛔ THE FIELDS THIS ROW CALLS 'ALREADY CURATED' DID NOT EXIST WHEN MEASURED 2026-08-09, AND SITE HAS SINCE BEEN CURATED (2026-09-04, `research/modalities/emc-site-curation.json`): extremity-strict 194/271 = 71.6% [65.9–76.6]. **Time-to-metastasis is printed as a median in two series (5.9 y, chiusole2020; 28 mo, bishop2019) and nowhere per patient**, which is what a perfusion-eligibility read would need."*

⛔ No clinical claim: the figures above are counts of what series *reported*, with no outcome, comparator or recommendation attached. Nothing here asserts efficacy, safety or appropriateness of any perfusion, ablation or operation.

### R.4 — `MOD-BRACHYTHERAPY` denies a field that another row of the same graph tabulates four ways `PRIMARY`

The clause: *"**No cohort carries dose, modality or margin detail**, so there are no inputs for a dose-response fit."*

`artifacts.json:510`, `ART-SURGICAL-QUALITY.note`, in the same graph layer:

> *"Surgical **margin** distribution and outcome-by-margin for EMC, transcribed from the two reachable open-access series — **156 operated patients in Masunaga's Table 1 and 40 in Chiusole's Table 2** … ⛔ THERE IS NO SINGLE POSITIVE-MARGIN RATE and the artifact refuses to elect one: **25.0 %** over all operated patients, **22.4 %** among those localized at diagnosis, **40.9 %** among those already metastatic, **35.0 %** in Chiusole where the field was recorded"*

and `artifacts.json:534` supplies the **modality** half per cohort: *"Bishop 2019 reports surgery ALONE as the adverse exposure … Masunaga 2025 reports **(neo)adjuvant radiotherapy** at 0.50 (0.11–2.25)"*, with *"its treated arm carried **R1/R2 margins at 41.7 % against 18.2 %**"* — margin **crossed with** modality, per cohort.

⭐ **Margin is curated and modality receipt is curated; only DOSE is absent — and dose is the one input the sentence's own conclusion actually needs.** The record over-claims two of its three terms and reaches a right conclusion for a wrong reason, which is the failure mode that survives review longest.

**Smallest correct restatement:** *"⛔ THE REGRESSION THIS ROW WAITS ON CANNOT BE BUILT FROM THE REGISTRY. **Margin is curated (ART-SURGICAL-QUALITY: 25.0 % over 196 operated patients across two series) and radiotherapy receipt is curated (ART-RT-…), but no cohort carries a DOSE**, so there are no inputs for a dose-response fit. ⭐ The brachytherapy literature census has been run: one case report, no registry arm (`artifacts.json:534`)."*

### R.5 — `ST-PROXIMITY` drops the scoping its own requirements layer calls load-bearing `PRIMARY`

`strategies.json:21`, `ST-PROXIMITY.limitations[0]`:

> *"No molecule in this family has been shown to bind NR4A3 at all — the pocket every route here depends on **has no known ligand of any kind**."*

`requirements.json:113`, `R4`'s `claim_ceiling`, verbatim:

> *"nothing binds the cryptic pocket, of any molecule. **⚠ Scoping is load-bearing: NR4A3 *is* experimentally ligandable (§5 row R4); the cryptic site is what has no ligand**"*

and `:114` repeats it in `claim_ceiling_raw`.

⭐ **The requirements layer states the distinction and flags it as load-bearing; the strategies layer states the same negative with the distinction removed, and the strategies layer is the one that renders into eight view pages.** The unqualified reading — "NR4A3 has no known ligand of any kind" — is the claim `requirements.json` exists to forbid. `modalities.json:1606` (`MOD-…`, glue chemotype) carries a third variant, *"no ligand of any kind is known for it"*, whose antecedent "it" is the pocket and which is therefore ambiguous rather than wrong.

**Smallest correct restatement**, one clause, one file: *"No molecule in this family has been shown to bind NR4A3's **cryptic pocket** at all — the site every route here depends on has no known ligand of any kind. ⚠ Scoping is load-bearing: NR4A3 itself **is** experimentally ligandable (`R4`)."*

### R.6 — Where these files fall against `publications.json` and `routes.json`, and why `PRIMARY`

| file | categorical clauses examined | FALSE | OVER-SCOPED | defective share of clauses | defective share of sentences |
|---|---:|---:|---:|---:|---:|
| `publications.json` (W09f) | 22, in 41 fields | 4 | 6 | **45%** | — |
| `routes.json` (W26) | 45, in 4,323 fields | 6 | 12 | **40%** | **18 / 6,100 = 0.30%** |
| **these 17 files (this audit)** | **45, in 8,770 fields** | **3** | **13** | **36%** | **16 / 12,373 = 0.13%** |

⭐ **The 36%/40%/45% ordering is real but it is not the finding. The finding is that these seventeen files are not one population and the "does the row supply the scope?" rule predicts each sub-population correctly.**

1. **`strategies.json` behaves like `publications.json`, not like `routes.json`, and it is the worst file in my set.** Its rows are *families*, not routes, so a `limitations[n]` entry is written once about a whole family and inherited by every route in it. 25 firings in 360 sentences — the highest density of any file here — and **10 of its 10 categorical clauses render verbatim into the views**, several into eight pages at once. W09f's diagnosis ("no row to be scoped by") generalises: a `strategies.json` row supplies a *family*, and a family is not a scope for a claim about the literature.
2. **`modalities.json`, the largest file in my set, is the cleanest per sentence and the reason is its row.** 34 firings in 3,073 sentences; a `MOD-*` row names a drug class, a verdict, a band and usually a route, so most of its negatives inherit a real scope for free. Every one of its defects sits where the row's scope stops helping — `zero_dollar_next_step`, a field that describes what *the world* should do next (F1, F2, OS-1, OS-8), and `rationale` on the rows that have **no** route to hand the scope over to.
3. **`plan.json` is a false-positive factory and contributes essentially nothing.** 39 firings, 2,428 sentences, **one** surviving categorical clause. It is a run log, so "zero", "never run" and "unmeasured" are overwhelmingly internal records of this program's own executions — correctly self-scoped by construction, because a run log's subject is the runs.
4. **`integrity.json` and `objects.json` fire zero times.** Two files, 340 string fields, no absence prose at all.

⭐ **And the structural seam, stated as one sentence.** In `routes.json` the defect concentrated in `publication.contribution` — *"the seam where a route-scoped field starts talking about the world"* (W26 R.6). **Here the same seam appears twice under different names: `zero_dollar_next_step` in `modalities.json` and `limitations[n]` in `strategies.json`.** Both are fields whose *job* is to range beyond the row — one says what anyone should do next, the other says what the whole family cannot claim — and 11 of my 16 defective clauses sit in one of those two field names.

### R.7 — Measured blast radius, by whole-field sentinel and regeneration `PRIMARY`

Sixteen sentinels, each: restore all 19 graph files pristine from `/home/user/Rare-cancers`, substitute `ZZSENTINELZZ` for the whole field, re-serialize, regenerate, walk **all 111 written view files including `registers/`**, count sentinel occurrences and unified-diff ±lines against the committed snapshot, restore pristine, regenerate, and **assert the restore is a no-op**. Every `gen_exit=0`, every stdout `systems_check: wrote 111 view(s) to systems/views/`, final `ALL_RESTORED_OK`, `SENTINEL_EXIT=0`.

| record · field | class | files touched | committed lines consumed | sentinel occ. | exit |
|---|---|---:|---:|---:|---|
| `modalities` `MOD-ISOLATED-LUNG-PERFUSION.zero_dollar_next_step` | FALSE | **1** — `modality-census.md:70` | 1 | 1 | 0 |
| `modalities` `MOD-BRACHYTHERAPY.zero_dollar_next_step` | FALSE | **0** | 0 | 0 | 0 |
| `strategies` `ST-PROXIMITY.limitations[0]` | FALSE | **8** — `L1-st-proximity.md:29`, `L2-rt-af3-interface.md:112`, `L2-rt-andgate.md:123`, `L2-rt-degrader.md:161`, `L2-rt-glue.md:131`, `L2-rt-riptac.md:135`, `L2-rt-tcip.md:141`, `L2-rt-ubiq-selective.md:122` | **8** | 8 | 0 |
| `modalities` `MOD-ILP.zero_dollar_next_step` | OVER-SCOPED | **0** | 0 | 0 | 0 |
| `modalities` `MOD-SERM-SERD.rationale` | OVER-SCOPED | **0** | 0 | 0 | 0 |
| `artifacts` `ART-HORMONE-PARTNER-LANE.note` | OVER-SCOPED | **0** | 0 | 0 | 0 |
| `artifacts` `ART-SYSTEMIC-THERAPY-POOLING.note` | OVER-SCOPED | **0** | 0 | 0 | 0 |
| `modalities` `MOD-SGK1.rationale` | OVER-SCOPED | **0** | 0 | 0 | 0 |
| `modalities` `MOD-TOPO2-NON-ANTHRA.rationale` | OVER-SCOPED | **1** — `modality-census.md:98` | 1 | 1 | 0 |
| `strategies` `ST-OCCUPANCY.limitations[1]` | OVER-SCOPED | **5** — `L1-st-occupancy.md:30`, `L2-rt-asymmetric.md:104`, `L2-rt-covalent-probe.md:139`, `L2-rt-monovalent.md:155`, `L2-rt-nr2f1.md:112` | **5** | 5 | 0 |
| `requirements` `R9.claim_ceiling` | OVER-SCOPED | **1** — `registers/requirements.md:189` | 1 | 1 | 0 |
| `requirements` `R9.claim_ceiling_raw` | OVER-SCOPED | **0** | 0 | 0 | 0 |
| `blockers` `BLK-FUNCTIONAL-ACTIONABILITY.statement_about` | OVER-SCOPED | **1** — `registers/blockers.md:372` | 1 | 1 | 0 |
| `technologies` `TECH-RECONSTRUCTED-IPD.not_scannable_because` | OVER-SCOPED | **1** — `registers/technologies.md:188` | **3** | 1 | 0 |
| `forecasts` `FC-E3-RECRUITER-STRUCTURE.scenarios.conservative.rationale` | OVER-SCOPED | **1** — `registers/technologies.md:614` | 1 | 1 | 0 |
| `modalities` `MOD-PRMT5-MAT2A.rationale` | OVER-SCOPED | **0** | 0 | 0 | 0 |

⭐ **Seven of sixteen sentinelled fields have a blast radius of exactly ZERO — the field is not rendered into any committed view at all.** I extended that measurement to the whole categorical population by searching the 111 committed views for each clause verbatim: **31 of the 45 categorical clauses render; 14 do not** — 11 of the 14 in `modalities.json` (5 rendered vs 11 unrendered), against **`strategies.json` at 10 rendered / 0 unrendered**.

⚠ **Consequence, and it cuts both ways.** An unrendered field cannot be caught by the generated layer's own drift guard — `systems_check.py --check` re-renders the views and compares, so prose that reaches no view is prose no re-render can check. Two of my three FALSE clauses (`MOD-BRACHYTHERAPY`, and `MOD-ILP`'s stale sibling) are invisible to the whole view-diff mechanism, which is the plausible reason they have stood since 2026-08-09.

⭐ **And the 150-character clip DOES fire here, unlike in `routes.json` — so sentinel radius ≠ clause-level radius in this file set.** `systems_check.py:3864` renders `esc(_clip(m["rationale"], 150))` into `modality-census.md`. I measured, rather than assumed:

| record · field | field len | offending-clause offset | renders? | line clipped (`…`) | clause survives the clip |
|---|---:|---:|---|---|---|
| `MOD-AR-ANTAGONIST.rationale` | 217 | 0 | ✅ | ✅ | ✅ yes |
| `MOD-ANTIMETABOLITE.rationale` | 357 | 61 | ✅ | ✅ | ✅ yes |
| `MOD-TOPO2-NON-ANTHRA.rationale` | 386 | 95 | ✅ | ✅ | ✅ yes |
| `MOD-SPLICE-SWITCH-ASO.rationale` | 411 | 125 | ✅ | ✅ | ✅ yes |
| `MOD-PHOSPHATASE-RECRUIT.rationale` | 307 | **288** | ✅ | ✅ | ⛔ **no — clipped away** |
| `MOD-ISOLATED-LUNG-PERFUSION.zero_dollar_next_step` | 293 | 190 | ✅ | ❌ | ✅ yes |
| `MOD-RET.rationale` | 693 | 622 | ⛔ no (row has a route) | — | — |
| `MOD-MCL1-BCLXL.rationale` | 286 | 259 | ⛔ no (row has a route) | — | — |
| `MOD-HYPERTHERMIA.zero_dollar_next_step` | 1,001 | 574 | ⛔ no (row not in the live residue) | — | — |

**So for the lander: in `strategies.json` and `requirements.json`, sentinel radius = clause-level radius exactly (each field renders once per page, in full). In `modalities.json` it does not** — `MOD-PHOSPHATASE-RECRUIT.rationale`'s offending clause sits past the clip and a clause-level fix there touches **zero** view lines while the sentinel touches one; and `TECH-RECONSTRUCTED-IPD.not_scannable_because` consumes **3** committed lines for **1** written, because the pristine value wraps across three lines of `registers/technologies.md`.

**Totals for a complete landing of all 16 defective clauses: 15 source fields → 21 committed view lines across 13 view files** — `modality-census.md` (2), `registers/requirements.md` (1), `registers/blockers.md` (1), `registers/technologies.md` (4, of which 3 are one wrapped value), `L1-st-proximity.md` + `L1-st-occupancy.md` (2), and 11 `L2-rt-*.md` lines. ⚠ Every restatement in R.2–R.5 is *longer* than what it replaces, so lines below each edit renumber; the lander must regenerate and re-diff rather than reuse these numbers.

⭐ **Blast radius here is bimodal, where `routes.json` was flat.** `routes.json` gave 1–2 files per field. Here a `modalities.json` or `artifacts.json` field costs **0–1** lines, while a single `strategies.json` `limitations[n]` costs **5–8 files** — the `publications.json` fan-out pattern, arriving through the family layer instead of the publication layer.

---

## Validation evidence

Environment for every run: scratch copy at `/tmp/claude-0/w26b/repo`, produced by `tar --exclude=./.git --exclude=./results -cf - . | tar -xf -` from `/home/user/Rare-cancers` (428 MB; the `results/` exclusion is justified by the no-edit control below, which is byte-clean). Committed views snapshotted to `/tmp/claude-0/w26b/views-committed` (**111 files**) before any generator run. Linux, Python 3.11 stdlib, no network.

### `RUN` — Control 1: regeneration with no edit is a no-op (run FIRST, before any scan or sentinel)

```
$ cd /tmp/claude-0/w26b/repo && python3 systems/systems_check.py --write-views
systems_check: wrote 111 view(s) to systems/views/
CONTROL_GEN_EXIT=0
$ diff -rq /tmp/claude-0/w26b/views-committed /tmp/claude-0/w26b/repo/systems/views
NOEDIT_CONTROL_DIFF_EXIT=0
```

### `RUN` — Control 2: re-serializing the JSON alone changes no view

This is the control that makes every radius below *attributable* to the text and not to the serializer. All seven files I would later sentinel were `json.load`-ed and re-dumped with `indent=2, ensure_ascii=False`, with **no content change**, then regenerated:

```
CONTROL2_RESERIALIZE files=['artifacts.json', 'blockers.json', 'forecasts.json', 'modalities.json',
                            'requirements.json', 'strategies.json', 'technologies.json']
  gen_exit=0 stdout='systems_check: wrote 111 view(s) to systems/views/'
  changed_view_files=0 +0/-0 sentinel_occ=0
CONTROL2_RESTORE gen_exit=0 changed_view_files=0 (expect 0)
```

### `RUN` — Enumeration

```
$ cd /tmp/claude-0/w26bx && python3 scan.py
… (per-file table reproduced in R.1) …
TOTAL                    526    8770  12373    192      155
SCAN_EXIT=0
```

### `RUN` — Sixteen whole-field sentinels

`SENTINEL_EXIT=0`; every case `gen_exit=0` with stdout `systems_check: wrote 111 view(s) to systems/views/`; every case followed by `RESTORE_NOOP=True` (assertion: zero changed view files **and** `gen_exit=0` after restore); terminal line `ALL_RESTORED_OK`. Full per-case output is the R.7 table.

### `RUN` — Clip-offset measurement

Re-implemented `_clip` exactly as `systems/systems_check.py:2036-2042` defines it, and applied the census renderer's own gating conditions (`m.get("route")` / `prior_ref` for `rationale`; `never_searched` + live verdict for `zero_dollar_next_step`). Output is the R.7 clip table.

### `RUN` — Rendering coverage of all 45 categorical clauses

Verbatim search of each clause's first 70 characters across all 111 committed view files: `categorical clauses n=45  rendered_verbatim_in_views=31  NOT_rendered=14`, per-file breakdown and the 14 unrendered clauses listed in R.7.

### `RUN` — Isolation proof

`git status --porcelain` empty at start and end; `cmp` on all seven sentinelled graph files against the scratch copy → `IDENTICAL` ×7; `diff -rq systems/views /tmp/claude-0/w26b/views-committed` → `VIEWS_UNCHANGED_SINCE_SNAPSHOT`; `rmdir /home/user/.w26b-tmp` → `REMOVED`.

### `PROPOSED (NOT RUN)`

- Landing any of the 16 restatements. **Nothing applied**, per my dispatch.
- `PREFLIGHT_FULL=1 scripts/preflight.sh` after a landing. Not run; not authorised here.
- A committed census that would move any of the 29 UNVERIFIABLE clauses to TRUE or FALSE. Requires retrieval; I had none.

---

## Limitations

- **Regex recall is unmeasured.** 192 firings is a *lower* bound on absence prose: a clause phrased outside the 60-term set is invisible to me. I did not sample non-firing sentences to estimate recall, so **"45 categorical clauses" is a floor, not a census** — the exact error this audit exists to name, applied to itself.
- **Classification is mine and hand-made.** The FALSE/OVER-SCOPED/UNVERIFIABLE boundary is a judgement; I published every quoted clause and its reason so each call is checkable and reversible. **I disagree with W26 on one call** (`MOD-SGK1` / `RT-SGK1.rationale`, R.2 row 5) and say so rather than inheriting it.
- **UNVERIFIABLE means unverifiable, not false.** 29 clauses may each be perfectly true. Their defect is that this repository cannot show it, which is a stating defect, not a scientific one.
- **`plan.json` is under-audited relative to its size.** 2,428 sentences reduced to one surviving categorical clause. I read all 39 firings, but a run log written as six prose blocks is the shape my instrument handles worst, and a reader should treat `plan.json` as *screened*, not *cleared*.
- **`results/` was excluded from the scratch copy for disk reasons** (the container was at 97% and the harness temp filesystem had already thrown `ENOSPC`). Both controls came back byte-clean, so nothing under `results/` participates in view generation — but I did not prove that independently of the controls.
- **No clinical claim, no efficacy claim, no wet lab.** Every count quoted from `emc-site-curation.json`, `ART-SURGICAL-QUALITY` and `artifacts.json:534` is a count of what a series *reported*, carried here only to check a sentence in a JSON file. Nothing here bears on whether any treatment works.
- **The blast-radius numbers are valid for HEAD `ff6bb018`/`215ed8e7` only** and go stale the moment any of these fields is edited.

---

## Stop condition

**Set up front:** return the moment (a) all 17 files are enumerated and sentence-split, (b) every regex firing is hand-classified, (c) every surviving categorical clause is graded with a restatement, and (d) both controls plus a sentinel set spanning every file that carries a defect have run with restores asserted — or at ~40 tool calls / ~40 minutes, whichever came first, reporting partials honestly.

**MET, inside budget, on all four legs.** 192/192 firings hand-classified; 45/45 categorical clauses graded with restatements; both controls clean; 16 sentinels across 7 files, all restored to a proven no-op. Nothing was left partial and nothing was applied.

---

## Tool-call and wall-clock count actually used

**34 tool calls** (target ~40). **Wall clock 7 min 28 s** — `date -u` start `03:26:05Z`, end `03:33:33Z` (target ~40 min). The saving is almost entirely W26's: reusing its scanner, term set and sentinel harness removed the instrument-building phase, and I record that so the coordinator does not read the speed as reduced scope.

---

## Next concrete action

**Land the single highest-value, lowest-risk fix first: `strategies.json:21` `ST-PROXIMITY.limitations[0]` (R.5).** It is the only clause in my set that is FALSE, that the repository's *own* `requirements.json:113` explicitly labels a load-bearing scoping error, and that renders into **8 view files** — the widest blast radius I measured, and the only defect here that reaches seven `L2-rt-*` route pages that a reader will treat as independent confirmations. It is a one-field, one-clause edit in one file; regenerate with `systems/systems_check.py --write-views` and re-diff rather than reusing my line numbers.

**One thing the lander must be told, because it is not visible from a diff:** the two `modalities.json` FALSE/stale clauses (R.3, R.4) render into **zero** view lines, so `--check` will stay green whether or not they are fixed. They need a reviewer, not a gate.
