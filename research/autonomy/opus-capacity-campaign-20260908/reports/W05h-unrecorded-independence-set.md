<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:29:18Z UTC
     agent id a0698641de828564a ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a0698641de828564a.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

## Worker

- **Worker:** W05h, lane 5 refill (cross-study patient independence), OPUS-CAPACITY-CAMPAIGN-20260908. Named successor to W05g. Task: compute the set difference that both prior methods are blind to.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`), Claude Code 2.1.42, remote cloud container. I cannot observe the served model; no environment variable names one. The coordinator must extract the runtime model from the transcript. No finding below depends on which model produced it.
- **`date -u` start:** `Tue Sep  8 03:16:49 UTC 2026`. **`date -u` end:** `Tue Sep  8 03:23:57 UTC 2026`.
- **HEAD moved under me, as it did for W05d/W05f/W05g.** Start `c81236b90c7905caa2e75a57b332ad33f2c10d02`; end `6552a6c8d35158858b4b9ed3846b8a276032873a`. The brief's freeze at `92abbcb…` has not held for several workers now.
- **`git status --porcelain`** — start: **empty** (no output). End: three lines, **none of them mine**:
  ```
   M research/autonomy/opus-capacity-campaign-20260908/reports/W06g-mortality-relabel-matrix.md
  ?? research/autonomy/opus-capacity-campaign-20260908/reports/W27-drift-gate-hash-census.md
  ?? research/autonomy/opus-capacity-campaign-20260908/reports/W30-registry-policy-conformance.md
  ```
  I checked rather than assumed: `git diff --name-only c81236b 6552a6c` returns **14 files, all under `research/autonomy/opus-capacity-campaign-20260908/`** (coordinator report collection). Filtering that prefix leaves **zero** files. **Not one file I measured or quoted changed between my start and end commits.**
- **`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`**, verbatim, identical at start and end (five long proxy-exclusion variables — `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `JAVA_TOOL_OPTIONS`, `npm_config_noproxy` — also match on the `anthropic` substring inside their host lists and are filtered here for length only; they carry no model identity):

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

**Which cohorts appear in a pool, a denominator, or an "independent cohorts" phrasing somewhere in the tracked tree, yet carry NO independence-bearing record and NO prose overlap statement anywhere — the residual blind spot that W05f's lexical scan and W05g's structural scan share?**

Open because it is, by construction, invisible to both prior methods: W05f matched sentences and W05g matched fields, and a cohort whose independence was never written down in either form produces neither. W05g named this as its own Limitation 2 and as its successor task.

**Answer up front: the set difference is NOT empty. It has exactly one member — Filion 2009 — plus one adjacent class of independence claims made over cohorts that are never named at all. The two ceilings therefore do not meet.** A second, unexpected finding: **W05g's four-file inventory is incomplete; I found four more independence-bearing files, one of which is precisely the file that rescues the expression cohorts from this set.**

## Prior-work check

Commands run and what they showed:

| # | command | what it showed |
|---|---|---|
| 1 | `cat COMMON-BRIEF.md CLOSED-WORK.md CORPUS-CONTEXT.md` (in `research/autonomy/opus-capacity-campaign-20260908/`) | read in full; write-isolation and closure rules applied |
| 2 | `cat systems/POLICY-evidence.md` | read in full; §2.1/§2.3 (what may be pooled, double-counting) and §2.6/§2.7 are the contract the fields implement |
| 3 | `sed -n '30,224p' reports/W05-patient-independence-audit.md` | the 4-tier rubric and the 8-row per-cohort verdict table, read in full and applied below **as written, relaxed nowhere** |
| 4 | `sed -n '20,237p' reports/W05g-schema-level-independence-check.md` | its R1 four-file inventory, its R2 clean negative, and its Limitation 2 naming this exact task |
| 5 | `grep -n -A6 -E '^## (Question\|Method\|Result)\|^### R[0-9]\|lexic' reports/W05f-window-arithmetic-audit.md` | W05f's decision rule, its R1 single defect site, and its Limitation 1 (lexical recall is a floor) |
| 6 | `wc -l` over W05/W05e/W05f/W05g | 224 / 344 / 268 / 237 lines |

**Closed items I confirm I am not replaying.** I attempted **no patient, case or specimen identity** — closed-unresolved. Every cohort below was handled as an opaque key. I did not touch Brenca case identity, Hofvander/EGA, paired Davis, promoter transfer, the ICD-O paper, lane-11 source-index material, or the restricted NR4A Perspective. **No network request of any kind was made**, so no denied route was replayed. I **adjudicated no source pair**, **added and removed no cohort from any pool or denominator**, and **propose no repair**. I did not re-run W05f's sentence scan or W05g's dependence test; my method is a membership test, not a defect scan.

**I did not take W05g's four-file list on trust** — the dispatch required re-derivation, and the re-derivation changed the answer (R1 below).

## Method and inputs

Four stages, all offline, all over the live checkout at `/home/user/Rare-cancers`. Python 3.11 stdlib only. One script, `/tmp/claude-0/w05h/inv.py`, plus inline `python3 -` heredocs and `git grep`. Nothing written inside the repository.

**Stage 1 — independent re-derivation of the independence-bearing file inventory.** I deliberately did **not** reuse W05g's regex. W05g matched independence-shaped *key names* and gated on cohort vocabulary. I walked all **4,518 tracked `.json` files** and matched on the **decision semantics** (`pool|overlap|independ|disjoint|double|dedup|duplicat|exclud|exclus|population|cohort|denom|distinct|shared|stratum|strata|counted|context_?reason`), then gated on a document-level domain regex (`cohort|patient|case|studyPeriod|populationKey|denom|accrual|registry|pmid|doi|n_enrolled|series`) applied to the **raw text**, not the key set — a different gate, so a file whose independence field is named in unanticipated vocabulary can still qualify via its prose. **501 files** carry an independence-shaped key; **326** also pass the domain gate. I then read the candidate key-sets by hand and separately ran `git grep -ln` for each of the 13 canonical field names across **all** tracked files, not only JSON.

**Stage 2 — the recorded set.** For each independence-bearing file I extracted every record carrying a patient-level independence or pooling-eligibility field, keyed by `sourceId` / `source_id` / `key` / `id` / cohort key.

**Stage 3 — the used set.** Every cohort unit that appears in a pool, a denominator, or an "independent cohorts" phrasing: the registry `cohorts[]` and `treatments.systemicEvidence[]`, the three pooling artifacts' `cohorts[]`, `emc-ipd-survival.json`'s `candidate_sources[]`, the expression cohorts of W05's rows 1–5, plus a tree-wide `git grep -iE "independent (emc )?(cohort|series|dataset|patient|case|sample|tumour|tumor)"` over manuscripts and `systems/graph/`, negative-filtered to keep only affirmative claims.

**Stage 4 — the set difference,** with per-member evidence of use (file:line) and evidence of non-recording (an exhaustive walk of every structured occurrence of that unit).

**Files decisive to the result:** `research/data/emc-clinical-registry.json`, `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json`, `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json`, `research/modalities/emc-ipd-survival.json`, `research/modalities/expression-validation-readiness.json`, `research/manuscripts/aso/fusion-junction-aso-coverage-ladder.json`, `research/manuscripts/endpoint/emc-endpoint-alternatives.json`, `research/modalities/emc-cohort-search.json`, `research/modalities/nr4a3-fusion-targets.json`, `systems/graph/evidence.json`, `research/manuscripts/repurposing/pparg-direction-emc.md`, `research/manuscripts/repurposing/repurposing-hypotheses.md`, `research/manuscripts/program/emc-unexplored-treatment-lanes.md`.

## Result

### R1 — W05g's four-file inventory is incomplete: there is a fifth file, and three more besides `PRIMARY`

The dispatch asked me to say so if I found one. I found four.

| file | independence-bearing field(s) | why W05g's gate missed it | verified at |
|---|---|---|---|
| **`research/modalities/expression-validation-readiness.json`** | **`independence` (5 records)**, `array_exact_ID_overlap` | The field is named `independence` — inside W05g's over-broad key regex — but the file's records are **molecular deposits**, and its per-record vocabulary is `platform`/`assay_units`/`sample_records`, so it reads as an expression artifact rather than a cohort table. It is nevertheless the single most load-bearing independence file in the repository for W05's rows 1–5. | `:58`, `:303`, `:2249`, `:2595`, `:3577`; `array_exact_ID_overlap` at `:2` |
| `research/manuscripts/aso/fusion-junction-aso-coverage-ladder.json` | `contextReason`, `its_non_overlap_argument`, `4_non_overlapping_populations` (×2), `pooling_admissibility`, `third_series_deliberately_not_pooled`, `fifth_partner_cohort_deliberately_not_pooled` | Carries a genuine `contextReason` — W05g reported `contextReason` as occurring in only two files. | `:1831`, `:1958`, `:2091`, `:2111` |
| `research/manuscripts/endpoint/emc-endpoint-alternatives.json` | `non_overlap_argument`, `author_overlap`, `⚠_and_the_two_cohorts_are_not_independent` | W05g reported `non_overlap_argument` in one file; it is in two JSON artifacts and three generators. | `:872` |
| `research/modalities/emc-cohort-search.json` | `known_cohorts`, `is_new_fourth_cohort`, `gsm_overlap_examples`, `n_gsm_overlapping_a_known_cohort` (56 candidate rows) | Deposit-level overlap detection — an *overlap establisher*, which under W05's rubric asymmetry is exactly the cheap direction. | `:16`, `:36`, `:56` |

⚠ **This does not overturn W05g's negative.** Its finding was that no independence-bearing field is *date-determined*; the four files above contain no date-driven decision either (the coverage ladder's `4_non_overlapping_populations` cites countries, institutions and authorship, and explicitly labels its sixteen-year separation as *"an argument from provenance rather than a linkage check, and it is stated as one"*). What it does overturn is W05g's claim that **only** four files encode a record-level independence decision. The correct count is **eight**. I re-derived it rather than trusting the list, which is why the number moved.

### R2 — The recorded set: 37 cohort units carry an independence-bearing record `PRIMARY`

Extracted mechanically, not by hand. Unit → the record and the fields it carries (abridged; the full 61-row table was printed by the run):

| source file | units recorded | fields |
|---|---|---|
| `research/data/emc-clinical-registry.json#/registry/cohorts/0-13` | 12 distinct sourceIds over 14 rows | `pool` (14/14), `contextReason` (9), `populationKey` (5), `stratum` (2) |
| `…#/treatments/systemicEvidence/7` | `palmerini2022trobsultrarare` | `pool`, `contextReason` |
| `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json#/cohorts/0-7` | 8 | `pool_orr` (8), `pool_dc` (8), `pool_dc_reason`, `pool_reason`, `why_excluded` |
| `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json#/cohorts/0-15` | 16 rows / 13 distinct sourceIds | `pool` (14), `contextReason` (9), `populationKey` (9), `pool_note`, `overlap_note` |
| `research/modalities/emc-ipd-survival.json#/candidate_sources/1-16` | 16 | `overlap_risk` |
| `research/modalities/expression-validation-readiness.json#/cohorts/*` | 5 (`GSE4303`, `GSE28866`, `GSE24369`, `GSE170983`, `PRJNA1357027`) | `independence` |
| **total distinct units** | **37** | — |

**The decisive rescue.** W05's rows 1–5 — the cohorts I expected to be the blind spot, since the four clinical files cannot reach them — are **all five recorded**, verbatim:

- `GSE4303` (`:303`) and `GSE24369` (`:2595`): *"within-study patient identity and cross-study identity unresolved, including overlap with the published reference"*
- `GSE28866` (`:2249`): *"cross-study patient identity unresolved; alias relationship separately documented as a source assertion"*
- `GSE170983` (`:58`): *"source explicitly reports same deposit/publication/four EMC samples; not a separate validation cohort; exact alias sample crosswalk unavailable"*
- `PRJNA1357027` (`:3577`): *"within-study patient identity and cross-study identity unresolved, including the published reference"*
- and the method line on `array_exact_ID_overlap` (`:2`), which states its own limit correctly: `"exact_GSM_intersection_only;_empty_does_not_prove_patient_independence"`, `value: []`.

These are UNKNOWN verdicts, not independence claims — which is the point. **An UNKNOWN that is written down is auditable; an UNKNOWN that was never written down is the defect this task hunts.** W05's tier verdicts stand untouched; I re-adjudicated nothing.

### R3 — The set difference: one member `PRIMARY`

| member | where it IS used (file:line) | evidence it is NOT recorded | verdict |
|---|---|---|---|
| **Filion 2009** — 3 fusion-positive EMC, PMID 18855877, PMC4429309 (W05 row 6) | `research/manuscripts/repurposing/pparg-direction-emc.md:185` — *"**two independent cohorts, concordant** (10 EMCs, Subramanian 2005; 3 fusion-positive EMCs, Filion 2009)"*. `research/manuscripts/repurposing/repurposing-hypotheses.md:335` — *"concordant across two independent cohorts, 10 EMCs against 26 other sarcomas [15] and 3 fusion-positive EMCs against 137 other sarcomas [16]"*. `systems/graph/evidence.json:405` — the paired half of the same claim: *"The independent EMC cohort (10 EMCs) … one of the two concordant abundance cohorts."* | An exhaustive walk of **every** structured occurrence of `Filion`/`18855877`/`PMC4429309` across all 4,518 tracked JSON returns **16 files, and not one carries an independence-bearing field for it.** Every occurrence is bibliographic (`research/literature/submission-reference-metadata-2026-08-09.json:339`; `research/manuscripts/citation-retraction-sweep.json`), gene-set (`research/modalities/nr4a3-fusion-targets-confounds.json:92` set `E_filion_table2_overlap_with_subramanian`), citation-count (`research/literature/fusion-consensus-probe.json` anchor `filion_2009_pparg`), or graph-evidence (`systems/graph/evidence.json:167`, record `EV-FILION-2009` — keys `id`/`canonical`/`citation`/`what_it_supports`/`aliases`/`misattributed_as`/`cited_in`, **no pool, no overlap, no independence field**). It is **absent from `expression-validation-readiness.json`'s five cohorts** — consistent with W01c's finding that Filion 2009 publishes no data-availability statement, so it has no deposit to key on. No prose overlap or non-overlap statement exists in the pre-campaign corpus. | ⛔ **MEMBER — an independence judgement made implicitly and unauditable by either prior method.** |

**The one near-miss, and why it does not rescue Filion.** `research/modalities/nr4a3-fusion-targets.json:81` looks like an overlap record and is not one:

> `"verdict": "⛔ CONFIRMED CIRCULAR: GSE4303 is the Subramanian et al. 2005 cohort, so Filion Table 2 (the overlap with Subramanian's top 50) is a gene list DERIVED FROM THIS DATA. Its score on GPL3290 is not a test and is reported for completeness only. Filion Table 1 and GSE24369 are unaffected."`

That is **gene-list circularity**, not patient overlap. It establishes that a *derived gene set* is not independent of GSE4303's data, and it explicitly leaves Filion Table 1 — the 3-patient cohort — unaffected. Under W05's rubric it bears on neither tier; it is not about patients at all. The repository has correctly caught the *analytic* dependency between Filion and Subramanian while never asking the *patient* question.

**The asymmetry is the finding.** One side of the "two independent cohorts" claim (Subramanian 2005 = GSE4303) has an explicit `independence` record saying identity is unresolved. The other side (Filion 2009) has nothing. The claim as written at `:185` is therefore stronger than the record on either half, and the half that would have flagged it is the half that was never created.

### R4 — An adjacent class: independence asserted over cohorts that are never named `PRIMARY`

These cannot be set-difference members in the strict sense — there is no cohort unit to look up — but they are the same failure one step earlier, and a census that omitted them would be dishonest.

| file:line | claim | why it is not testable |
|---|---|---|
| `research/manuscripts/program/emc-unexplored-treatment-lanes.md:574` | *"three independent series report CD117 positivity at 52.6%, 84%, and 'variable in all cases' **[API]**"* | **No series is named**, none is curated into any artifact, and the `[API]` tag marks it as machine-retrieved and unread. Three independent series are asserted; zero cohort units exist. |
| `systems/graph/modalities.json:842`; `systems/graph/routes.json:8649` | *"confirmation at the transcript level in an independent EMC cohort"*; *"External validation in an independent cohort"* | **Prospective**, not claims about existing data. Recorded for completeness; these are not defects. |

### R5 — Two schema-level omissions found in passing, neither a set-difference member `PRIMARY`

1. **`research/modalities/emc-ipd-survival.json#/candidate_sources/0`** (`seer270_2022`, file line `:29`) is the **only one of 17 candidate-source rows with no `overlap_risk` field** — its keys are `source_id`, `n`, `endpoint_hint`, `why_candidate`, `full_text_reachable`, `figure_checked`, `reachability_2026_08_25`, `reachability_2026_08_27`, `⛔_caveat`. It is **not** a set-difference member, because `seer270_2022` is recorded in the registry at `research/data/emc-clinical-registry.json#/registry/cohorts/9` with `pool: false`, `contextReason: "population-overlap; percentage-only"`. But within its own file it is a hole in an otherwise complete column. ⛔ I propose no repair.
2. **Single-patient reports are covered by a class-level record, not per-unit records.** Four registry citations (`andradeRojas2025`, `gunasekaran2026`, `jiang2026`, `wang2026`) appear only at `/registry/patients/0-3`, and `galitskiy2025emcpembrolizumab` only at `/treatments/systemicEvidence/9` (n=1), none carrying a `pool` field. They are not blind-spot members because `emc-systemic-therapy-pooling.json` records `single_patient_reports_excluded_as_a_class` — *"excluded from every pooled proportion in this file"*, with a structural publication-bias rationale. That is a recorded pooling judgement, applied at class level. Worth naming because a per-unit audit would score five false positives here.

### R6 — The honest denominator

| quantity | value | basis |
|---|---|---|
| tracked `.json` files walked | **4,518** | `git ls-files`; 1 unparseable (`research/modalities/e3-provenance-correction.json`, `Expecting ',' delimiter: line 22 column 22`) — the same file W05g flagged, still broken |
| files with an independence-shaped key | 501 | Stage-1 walk |
| …also passing the domain gate | 326 | Stage-1 walk |
| files carrying a **record-level patient-independence or pooling-eligibility decision** | **8** (W05g said 4) | R1 |
| **cohort units with an independence-bearing record** | **37** | R2 |
| cohort units used in a pool, denominator or independence phrasing and testable | **38** | 37 + Filion 2009 |
| **set difference (members)** | **1** — Filion 2009 | R3 |
| **coverage** | **37 / 38 = 97.4 %** | — |
| independence claims over **unnamed** cohorts (untestable, excluded from the ratio) | **1 claim over 3 unnamed series** (CD117) + 2 prospective mentions | R4 |

⚠ **The 97.4 % is a coverage figure over the units I could enumerate, not a bound on the corpus.** See Limitations 1 and 3.

### R7 — Do the two ceilings meet?

**No.** W05g's closing sentence was *"if the set difference is empty, that is itself the finding, and the two ceilings then meet."* It is not empty. Stated precisely:

- W05f's lexical ceiling and W05g's structural ceiling **jointly cover 37 of 38 enumerable cohort units**.
- **Filion 2009 sits outside both.** No sentence commits an overlap or non-overlap claim about it (so W05f cannot see it); no field encodes one (so W05g cannot see it); yet three committed locations call it one of "two independent cohorts". It is exactly the object both prior methods predicted they would miss, and it exists.
- **The residual blind spot is real but small, and it is now named rather than bounded.** That is a strictly better epistemic state than "one defect is a ceiling", because a named single member can be checked; an unbounded blind spot cannot.

## Validation evidence

**RUN.** All reads in `/home/user/Rare-cancers`; the one script stored and run from `/tmp/claude-0/w05h/`. Linux 6.18.44-fc-v24, bash, Python 3.11, stdlib only. **No network tool of any kind was invoked.**

| # | command | exit | key output |
|---|---|---|---|
| 1 | `date -u; git rev-parse HEAD; git status --porcelain; env \| grep -i -E 'claude\|anthropic\|model' \| sed …; mkdir -p /tmp/claude-0/w05h` | 0 | start `03:16:49Z`, HEAD `c81236b9…`, status **empty**, env as quoted above |
| 2 | `cat COMMON-BRIEF.md CLOSED-WORK.md CORPUS-CONTEXT.md`; `cat systems/POLICY-evidence.md` | 0 | read in full |
| 3 | `sed -n '30,224p' reports/W05-…md`; `sed -n '20,237p' reports/W05g-…md`; `grep -n -A6 … reports/W05f-…md` | 0 | rubric, verdict table, W05g R1–R4, W05f R1/R4/Limitations |
| 4 | `python3 /tmp/claude-0/w05h/inv.py` | 0 | `tracked json: 4518 read ok: 4518 parse/read fail: 1`; `files with independence-shaped KEY: 501 ; also domain-gated: 326`; per-file key census |
| 5 | `for k in contextReason populationKey overlap_risk pool_orr pool_dc non_overlap_argument double_counting overlap_note pool_note residual_overlap_risk population_overlap_warning primary_non_overlapping secondary_assume_independent; do git grep -ln "\"$k\"" -- . ; done` | 0 | `contextReason` in **4** non-report files incl. `fusion-junction-aso-coverage-ladder.json`; `non_overlap_argument` in **2** JSON artifacts + 3 generators — both wider than W05g reported |
| 6 | inline `python3`: dump `expression-validation-readiness.json` cohort keys + `independence` values | 0 | 5 cohorts `GSE170983/GSE24369/GSE28866/GSE4303/PRJNA1357027`, each with an `independence` string, quoted verbatim in R2 |
| 7 | inline `python3`: registry cohort enumeration | 0 | 14 rows, 12 sourceIds; 5 `pool:true` / 9 `pool:false`, every exclusion carrying a `contextReason`; 25 registry citation ids |
| 8 | inline `python3`: record-shape probe over the four clinical files | 0 | record paths and key-sets; **`candidate_sources/0` printed with no `overlap_risk`** |
| 9 | inline `python3`: build the recorded-unit table across all five files | 0 | **`RECORDED UNITS: 37`**, 61 (unit, record, fields) rows printed |
| 10 | inline `python3`: registry `systemicEvidence` + `sourceId` provenance for the 5 uncovered citations | 0 | 10 rows, 1 with `pool`; the 4 uncovered citations resolve to `/registry/patients/0-3`, `galitskiy…` to `/treatments/systemicEvidence/9` |
| 11 | inline `python3` regex over `emc-systemic-therapy-pooling.json` | 0 | `single_patient_reports_excluded_as_a_class`, `exclusions_ledger`, `residual_overlap_risk`, `population_overlap_warning` quoted verbatim |
| 12 | inline `python3`: exhaustive walk of every tracked JSON containing `Filion\|18855877\|PMC4429309`, printing JSON-pointer path + value | 0 | **16 files, zero independence-bearing fields**; full path list reproduced in R3 |
| 13 | inline `python3`: dump `nr4a3-fusion-targets.json#/circularity_reading` | 0 | the `CONFIRMED CIRCULAR` verdict, verbatim in R3 |
| 14 | `git grep -n -iE "independent (emc )?(cohort\|series\|dataset\|patient\|case\|sample\|tumour\|tumor)"` over manuscripts + `systems/graph/`, negative-filtered | 0 | 30 affirmative claims; each resolved to its cohorts in R3/R4 |
| 15 | `grep -n` for each quoted claim | 0 | line numbers as cited: `pparg-direction-emc.md:185`, `repurposing-hypotheses.md:335`, `systems/graph/evidence.json:405`, `emc-unexplored-treatment-lanes.md:574`, `expression-validation-readiness.json:2,58,303,2249,2595,3577`, `nr4a3-fusion-targets.json:81`, `emc-ipd-survival.json:29` |
| 16 | `date -u; git rev-parse HEAD; git status --porcelain; env …` | 0 | end `03:23:57Z`, HEAD `6552a6c8…`, status = 3 campaign-report lines, none mine |
| 17 | `git diff --name-only c81236b 6552a6c \| grep -v '^research/autonomy/opus-capacity-campaign-20260908/'` | 1 (no match) | **empty** — all 14 changed files are campaign reports; **no file I measured moved** |

**Scripts written:** `/tmp/claude-0/w05h/inv.py` only; everything else was an inline heredoc. **No repository file was written, moved or deleted; no git write operation was run.** `git status --porcelain` attributes nothing to me at either end.

**PROPOSED (NOT RUN):**
- Extend the membership test to `.md` tables and `.py` literals that name a cohort in a pool without a JSON record. Not run: out of the bounded scope, and the JSON artifacts are where pooling decisions are actually read.
- Repair `research/modalities/e3-provenance-correction.json` so it parses, then re-walk it. Not run: I am read-only and it is not my file; W05g already routed this.
- Retrieve Filion 2009's full text for an accrual window or a non-overlap statement. Not run: **no network was permitted or used**, and the tier-A evidence would have to come from the paper, not from this repository.

**No test suite was run** — this audit changes no code and no shared state, and my dispatch forbids `scripts/preflight.sh`. **No skipped check is reported as a pass. No content-policy refusal was encountered.**

## Limitations

1. **A membership test over enumerable units is not a census of the corpus.** My "used" set is built from five artifacts plus a lexical sweep for independence phrasings. A cohort pooled in a `.md` table with no JSON record and no matching phrase would be missed by all three methods — mine included. The 97.4 % in R6 is coverage over what I could enumerate, and I state it as that rather than as a bound.
2. **One tracked JSON still does not parse** (`research/modalities/e3-provenance-correction.json`), so its structure is UNKNOWN. W05g's targeted grep found no cohort vocabulary in it; that lowers the risk, it does not close it.
3. **My independence-field inventory rests on a regex plus judgement**, exactly as W05g's did — but a *different* regex and a *different* gate, which is why it found four more files. Two independent derivations disagreeing by four files is itself evidence that neither is exhaustive. A third derivation might find a ninth file.
4. **"No prose overlap statement" is a negative over the pre-campaign corpus.** W05's own report, now committed at `reports/W05-patient-independence-audit.md:141`, *is* a prose statement about Filion's overlap status (tier C → UNKNOWN), and W05d records the pair at `:138` as adjudicated with both windows undocumented. **The lane's own outputs populate the very record set the lane audits.** I report the set difference against the corpus as it stood before this campaign wrote into it, because scoring the campaign's own reports as pre-existing records would make the defect disappear by bookkeeping. Read the other way — counting campaign reports — the set difference is empty and the ceilings meet, but only because W05 created the missing statement four workers ago. Both readings are stated; neither is hidden.
5. **Finding that a cohort is unrecorded says nothing about whether it overlaps anything.** Filion 2009 (3 EMC, MSKCC per W01c) and Subramanian 2005 (10 EMC, Stanford) may well be patient-disjoint. **Unrecorded is not overlapping**, and under W05's rubric an institutional difference is a tier-C falsifier that licenses nothing in the confirming direction. **I adjudicated this pair no further than membership.**
6. **No source was retrieved and no network was used.** Every fact traces to a committed file at the cited line, read between `c81236b9` and `6552a6c8`, and I verified by diff that none of those files moved in that interval.
7. **No patient, case or specimen identity was attempted.** Cohort keys, GSM ids and BioSample ids were handled as opaque strings throughout. Libraries are not specimens, arrays are not patients, runs are not patients.
8. **No clinical claim.** Nothing here bears on EMC treatment, efficacy, safety, selectivity or prognosis. **No denominator, pooled proportion or interval changes; I proposed no change to any and applied nothing.** There is no wet lab.
9. **I hold no authority over the rubric** and applied W05's tiers as written, relaxing nothing. W05e's IMMUNOSARC tier C → UNKNOWN, W05d's conjunctivity verdict, W05f's single repair site and W05g's date-independence negative are inputs here, not things I re-litigated.

## Stop condition

**Set up front, before any measurement:** return the moment all three of — (a) the independence-bearing file and field inventory is **independently re-derived** over tracked JSON with the discovery method stated and W05g's four-file list either confirmed or corrected; (b) the cohort-usage set and the recorded set are both enumerated and the set difference computed, with `file:line` for where each member IS used and positive evidence of where it is NOT recorded; (c) the honest denominator is stated with its coverage caveat — whichever comes first against the ~40-call / ~40-minute target.

**MET**, at 28 tool calls and 7 minutes. (a) yielded a correction: eight files, not four. (b) yielded a non-empty set of exactly one member plus one adjacent unnamed-cohort class. (c) is R6. I returned on meeting it rather than spending the remaining budget hunting for a second member.

## Tool-call and wall-clock count actually used

**28 tool calls** (all `Bash`; no network tool of any kind, no MCP call), against the ~40 target. **Wall clock 7 min 08 s** (`03:16:49Z` → `03:23:57Z`), against the ~40 min target.

## Next concrete action

**One successor, and it is a repair route rather than a fourth scan — the scanning axes are now exhausted for this lane.** The set difference has one member and its shape is known: **Filion 2009 is called "one of two independent cohorts" in three committed locations (`pparg-direction-emc.md:185`, `repurposing-hypotheses.md:335`, `systems/graph/evidence.json:405`) while its counterpart GSE4303 carries an explicit `independence` record saying cross-study identity is unresolved.** The concrete task for the owner of `research/manuscripts/repurposing/pparg-direction-emc.md`: narrow those three sentences to what the record supports — two cohorts on two platforms whose patient relationship is unrecorded — and add one `independence` entry for Filion 2009 alongside the five already in `research/modalities/expression-validation-readiness.json`, worded to match its neighbours (`"cross-study patient identity unresolved; no deposit, no data-availability statement in the source"` — W01c's finding). That is a one-record addition plus a wording narrowing, needs no network, adjudicates no pair, changes no denominator, pooled proportion or interval, and would take the coverage in R6 from 37/38 to 38/38. ⛔ **I made no such edit** — I am read-only, those files are not mine, and I propose no repair beyond naming the gap; routing it is the coordinator's call.

**Second, smaller, and for whoever owns the schema rather than this lane:** `research/modalities/emc-ipd-survival.json#/candidate_sources/0` is the one row of seventeen missing the `overlap_risk` field its siblings all carry (R5.1). It is covered elsewhere, so nothing is currently wrong — but a column with one hole is how the next blind spot starts.
