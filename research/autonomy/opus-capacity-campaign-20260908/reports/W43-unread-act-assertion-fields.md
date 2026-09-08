<!-- collected 2026-09-08T04:44:01Z by campaign coordinator; agent id ade77cbf763e1e09a; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ade77cbf763e1e09a.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Scratch deleted; report follows.

## Worker

**W43**, OPUS-CAPACITY-CAMPAIGN-20260908 (re-dispatch after a rate-limit kill). Lane: census of act-asserting fields across committed evidence artifacts.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions. The coordinator must extract the served model from the transcript.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (proxy/no_proxy/JAVA_TOOL_OPTIONS lines elided as marked, nothing else removed):

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
no_proxy=… [elided]  NO_PROXY=… [elided]  GLOBAL_AGENT_NO_PROXY=… [elided]
npm_config_noproxy=… [elided]  JAVA_TOOL_OPTIONS=… [elided, proxy/truststore]
```

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 04:35:29 UTC 2026` | `Tue Sep  8 04:40:38 UTC 2026` |
| `git rev-parse HEAD` | `408b676aec3625a36917755662516232a27a1278` | `408b676aec3625a36917755662516232a27a1278` |
| `git status --porcelain` | empty | empty (0 lines) |

HEAD did not move under me. **Write isolation honoured**: zero writes under `/home/user/Rare-cancers`, zero git write operations, no registry edit, no artifact edit, no repair authored, no gate proposed. All execution under `/tmp/claude-0/w43/`, **deleted** (`rm -rf`; `ls` → "No such file or directory"). No network, no retrieval, no MCP call, no paid API, no GPU. `scripts/preflight.sh` not run. `atr_hrd_sarcoma_series.py` never invoked. **No generator or module was executed at all** this run — every finding is from reading committed bytes with `python3` stdlib and `grep`, so no write-free check path had to be established.

## Question

Across the committed artifacts this repository treats as evidence — `research/data/emc-clinical-registry.json`, `research/manuscripts/pinned-figures.json`, `systems/graph/*.json`, and the provenance-carrying JSON under `research/modalities/` and `research/manuscripts/` — **which fields assert a human or external act, how many records carry them, does any code read them, and is the assertion decidable from the repository at all?** And: **how many of those are called load-bearing by a committed prose sentence while nothing reads them?**

Open because W30c established the shape for exactly one field (`verified` in the clinical registry) and W28c established dead-field counting for exactly one artifact (`pinned-figures.json`). Neither asked whether the pattern is a class.

## Prior-work check

Read in full first, in this order: `systems/POLICY-evidence.md` (386 lines), `research/autonomy/opus-capacity-campaign-20260908/reports/W30c-policy-sections-without-gates.md`, the head of `.../W28c-registry-schema-and-pattern-census.md` through R.3, then `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md` — including both "Known, measured, and NOT worth rediscovering" sections. **W25 not read, not referenced.**

Note for the coordinator: the dispatch prompt's paths `reports/W30c-…` and `reports/W28c-…` do not exist; there is no top-level `reports/` directory. The files are at `research/autonomy/opus-capacity-campaign-20260908/reports/`. Located with `find . -path ./.git -prune -o -name '*W30c*' -print -o -name '*W28c*' -print`.

Commands run for prior art:
- `find` as above → the two reports.
- Field-name greps over `*.py *.mjs *.sh *.yml *.yaml` (below) — these ARE the prior-art check for "does anything already consume this".
- `grep -rn -- "<field>" --include='*.md' . | grep -v opus-capacity-campaign` for every unread field, to find the prose sentence that declares its meaning.

`CLOSED-WORK.md` closes nothing in this lane: it covers scientific gates (Davis, Hofvander, Brenca, promoter transfer, pazopanib/sunitinib/CTARC recovery, the user-rejected registry ICD-O paper), the NR4A Perspective refusal, retained-source limits, and lane-11 source-index ownership. Per the brief, sibling campaign reports are premises, not repository evidence: I take W30c's `verified`-is-unread result as a premise and **re-measure its denominator**, which turned out to be wrong.

I did not read the frozen corpus. Every claim below is about committed bytes in the live checkout at HEAD `408b676a`.

## Method and inputs

**Enumeration, not name-guessing.** I walked every JSON object in five groups and counted *every* key, then filtered to act-asserting names by reading the key list — not by grepping a guessed name list. Groups and file counts: the registry (1 file), `pinned-figures.json` (1), `systems/graph/*.json` (19), `research/modalities/**/*.json`, `research/manuscripts/**/*.json` (986 files parsed across the last two).

**Reader determination.** For each candidate field I ran a *key-literal* grep, not a substring grep:

```
grep -rnE "[\"']<field>[\"']|\.<field>\b" --include='*.py' --include='*.mjs' --include='*.sh' \
     --include='*.yml' --include='*.yaml' . | grep -v '/\.git/'
```

then **read every hit** to classify it as a WRITE (a generator emitting the field into its own artifact), a COPY (propagating it), a RENDER (printing it into a view), or a READ (a branch, assertion or refusal that can fail on its value). The substring grep is useless here and I record why: bare `grep -c verified` returns **5,088** hits and `graded` **4,358**, almost all prose; the key-literal grep returns **86** and **69**.

**Schema path.** `systems/systems_check.py:492-522` validates graph collections against `systems/schema/*.json` — `strategies/routes/blockers/modalities` `[S1]`, `lanes/requirements/instruments/publications` `[S3]`, `technologies` `[S2]`, `forecasts` `[S3]`. A field named in a schema `required` array of a validated collection therefore has a **presence** reader even when no Python line names it. I extracted every `required` array from all 11 schemas to catch this.

Sources read directly: `scripts/validate-registry.mjs`, `research/manuscripts/lint_citations.py`, `research/modalities/emc_ipd_survival.py:200-235,770-800`, `systems/systems_check.py:492-522,1175,1979-2008,4104`, `research/manuscripts/emc_systems_map_check.py:197`, `research/modalities/tests/test_lint_citations.py:405-406`, `research/modalities/emc-site-curation.json:27,216`, `research/manuscripts/aso/lit-targets-aso-verify.json:7`.

Tools: system `python3` (stdlib only), `git`, `grep`. Four scratch scripts (`keys.py`, `census.py`, `census2.py`, `final.py`) under `/tmp/claude-0/w43/`, now deleted.

## Result

### R.0 Headline

**The class exists and has 21 members that nothing reads.** Of **34** act-asserting fields I could enumerate across the four artifact groups, **13 are ENFORCED**, **21 are UNREAD**, and of those 21, **20 are UNDECIDABLE FROM THE REPOSITORY** — they record an act (a link opened, a figure looked at, a full text retrieved, a clinician review) that no committed byte can confirm or refute. Total unread act-assertion records: **≈478**.

**Four fields are declared load-bearing by a committed prose sentence and read by nothing.** W30c found one; there are four, and one of them was *recognised as undecidable by this repository and remedied by building an instrument* — which is the precedent, not a defect.

⚠ **Nothing here says any of these values is false.** An unread field is undecidable, not wrong. I opened no link and retrieved nothing.

### R.1 The denominator correction: registry `verified` is 36 records, not 25 `PRIMARY`

W30c reported 25 of 25 citations asserting `verified: true`. Measured at HEAD `408b676a`, the registry carries **36** `verified` keys, all `true`:

| path | n | values |
|---|---|---|
| `/registry/citations/<id>/verified` | 25 | `true` ×25 |
| `/studies/items[]/verified` | **11** | `true` ×11 |

The 11 extra are a `studies.items[]` list (titles: "From pathogenesis to the patient's bedside…", "Pazopanib for treatment of advanced extraskeletal…", nine more). W30c's 25 is the citations subset; the field's real denominator is 36. `scripts/validate-registry.mjs` contains no `verified` literal and no `.verified` access (I extracted every quoted identifier in the file: `SAMPLE_SYNTHETIC against age agent claim contested curated data diseaseDeath distant emerging label localized metastasis mixed n null number otherCauseDeath primaryRef question recurrence regional research secondary sex sourceId stage supports title url vitalStatus year`). **W30c's core result stands and the denominator is 36/36 UNEVAL.**

### R.2 The census — 34 fields, graded `PRIMARY`

Grade key: **ENFORCED** = at least one non-write reader that can branch, assert or refuse on the value (I name the line); **UNREAD-BUT-DECIDABLE** = nothing reads it, but a committed byte could settle it; **UNREAD-AND-UNDECIDABLE** = nothing reads it and no committed byte could settle it.

#### ENFORCED (13)

| field | artifact(s) | n | reader (read) | what is actually enforced |
|---|---|---|---|---|
| `verified_by` | `graph/requirements.json` | 16 | `systems_check.py:374,1006,1220,3939,3954`; schema `required` on `$defs/requirement` | presence + cross-file agreement with the roadmap |
| `verified_against` | 13 modality + 16 manuscript files | 35 | `test_emc_site_curation.py:48`; `test_emc_ipd_survival.py:320` asserts the literal `"text layer"` | presence, and one content assertion |
| `digitized_by` | `emc-ipd-survival.json`, `km-figure-readings.json` | 2 recipes | **`emc_ipd_survival.py:786` refusal** (`no_digitization_provenance`), `test_emc_ipd_survival.py:145,191` | presence — this is POLICY-evidence §2.7(c), and it is the only §2.7 hand-step field with a refusal behind it |
| `last_reviewed` | `graph/forecasts.json` | 28 | `systems_check.py:4104` staleness (`< "2026-02-05"`); `test_systems_check.py:93` | presence + age |
| `checked_on` | `graph/artifact-refs.json` (4), ledger (13) | 17 | `systems_check.py:2008` (`need = ("why","checked_on")`); `test_lint_citations.py:405` (ARXIV rows only) | presence |
| `checked_by` | `citation-provenance-ledger.json` | 14 | `test_lint_citations.py:406` (ARXIV rows only, 13 of 237 entries) | presence, on 13/237 |
| `provenance_flag` | `graph/evidence.json` | 12 | `emc_systems_map_check.py:197` (`if not ev.get("provenance_flag")`) | presence |
| `closed_on` | `graph/lanes.json` | 18 | `systems_check.py:1175`; `test_systems_check.py:1362-3` (date shape) | presence + format |
| `changed_on` | `graph/blockers.json` | 1 | schema `required` on `kind_history/items` | presence |
| `posted_by`, `published_at_utc` | `graph/publications.json` | 1 each | schema `required` inside `posted` (publications validated at `systems_check.py:508-510`) | presence |
| `seen_on` | `graph/technologies.json` | 302 | schema `required` on `pending_signals/items`; `systems_check.py:3524` renders | presence |
| `last_verified` | `graph/routes/requirements/strategies` (113) + doc frontmatter | 113 | schema `required` inside requirement `state`; `systems_check.py:1910` treats the literal `"unverified"` specially | presence, and one sentinel value |
| `read_from` | 6 modality files | 99 | `test_realised_spend.py:93`; `test_emc_radiotherapy_contradiction.py:132,150` asserts `"literature-cache" in e["read_from"]` | presence + substring |

Four more with real readers that are act-*adjacent* rather than act-asserting, recorded for completeness: `needs_human_read` (193, aggregated at `fusion_junction_census.py:617`), `evidence_verified` (7, `test_structural_provenance_census.py:31`), `reviewed_only` (4, `test_junction_proteome_novelty.py:120`), `written_by` (2, `lane_staleness_watch.py:774`). `dataStatus` (registry, 1) is the one registry field in this whole census with a hard validator branch: `validate-registry.mjs:43`.

#### UNREAD-BUT-DECIDABLE (1)

| field | artifact(s) | n | why decidable | caveat |
|---|---|---|---|---|
| `retrieved_file` | 5 endpoint artifacts | **1,157** | the value names a file path; existence is a committed fact | **1,108 of them name `literature-cache:literature/xdisease-ctg-results/…`**, and per the campaign's own settled finding (W40) that branch has never existed in this checkout. So decidable *in principle*, **UNKNOWN in this tree** — and W40 records that whether it exists on the remote is itself unknown. I did not fetch. |

#### UNREAD-AND-UNDECIDABLE-FROM-THE-REPOSITORY (20)

| field | artifact(s) | n | values | act asserted |
|---|---|---|---|---|
| `verified` | **clinical registry** | **36** | `true` ×36 | a link was opened and confirmed to support the exact claim (§1.2/§1.3) |
| `verified_by` | `citation-provenance-ledger.json` | 90 | `fetch-literature.yml … Crossref` ×48, `… EuropePMC` ×26, `PubMed/PMC MCP connector` ×10, `WebSearch (rung 0)` ×2, … | who/what performed the verification |
| `verified_on` | ledger | 90 | `2026-08-08` ×75, `2026-08-27` ×11, `2026-08-24` ×4 | when |
| `verified_source` | ledger | 90 | `Crossref` 48, `EuropePMC` 27, `PubMed` 11, … | against which external service |
| `openAccess` | registry (25) + 4 manuscript files (38) | **63** | `true` 36 / `false` 27 | an external licence/access fact |
| `open_access_full_text_retrieved` | `aso/lit-targets-aso-verify.json` | **58** | `false` 38 / `true` 20 | a full text was actually retrieved |
| `accessed` | registry (25) + 2 manuscript files (26) | **51** | `2026-06-20` ×17, `2026-08-07` ×22, … | a date a source was accessed |
| `figure_checked` | `emc-ipd-survival.json` | 17 | `false` 12 / `true` 5 | **a human looked at the graphic** |
| `read_level` | `emc-icdo-contamination.json` | 16 | `[FT]` 6, `[API]` 5, `[DOC]` 5 (incl. `"[FT] for the body, NOT for Table 1"`) | how deeply the source was read |
| `retrievalNote` | registry (5) + `aso/…-submission-references.json` (2) | 7 | free text (403 outcomes, reference-chasing narratives) | what retrieval was attempted and what happened |
| `verified_utc` | 1 modality + 3 manuscript files | 4 | ISO timestamps | when a verification ran |
| `resolved_on` | `graph/integrity.json` (2), `emc-systems-map.json` (2) | 4 | `2026-08-03`, `2026-08-05` | when a conflict was resolved |
| `date_read` | `emc-test-article-routes.json` | 5 | `2026-08-15` ×5 | when a source was read |
| `fetched_via` | `claim-ceiling-grade-map.json` | 5 | `fetch-literature.yml run 33181002075…` | which external CI run fetched it |
| `read_url` | `graph/publications.json` | 1 | `https://www.qeios.com/read/VL3LJR.2` | an external page exists |
| `lastReviewed` | registry | 1 | `2026-06-20` | when the registry was reviewed |
| `reviewedBy` | registry | 1 | `"Initial automated draft from published literature - NOT yet clinician-reviewed"` | **who reviewed it — here, a disclosure that nobody clinical has** |
| `committed_cache_fetched_utc` | 22 modality + 1 manuscript file | 23 | 2 distinct timestamps | when a cache was fetched (copied from the cache's own `_fetched_utc`, never re-read) |
| `retrieved_via` | 7 files | 56 | `Europe PMC REST search…`, `IDENTIFIED from the reference list of…` | which external route was used |
| `retrieved_utc` | 8 manuscript + 1 modality file | 27 | dates | when. *(Presence — not value — is asserted for the type-cache subset by `test_citation_type_guard.py:50`; I grade the field unread because no consumer branches on it and the 22 in the other artifacts have no reader at all.)* |

**Unread act-assertion records, summed: ≈478** (1,157 more if `retrieved_file` is counted).

`pinned-figures.json` contributes **zero** fields to this class. Its 64 distinct keys contain no `verified`/`checked`/`retrieved`/`read` field. W28c's eleven dead fields are a different class — dead *scoping and documentation* metadata, not act assertions. **The two shapes are adjacent, not the same.**

### R.3 The four fields a committed sentence calls load-bearing that nothing reads `PRIMARY`

This is the finding the unit asked for. W30c found one; there are four. Ordered by how explicitly the sentence makes the field decide what may be claimed.

1. **`verified` — clinical registry, 36 records.** `systems/POLICY-evidence.md` §1.3: *"`verified: true` is set **only** when the link was opened and confirmed to support the exact claim. Auto-fetched but unread → `verified: false`."* §1.2's schema block annotates it *"a human/agent confirmed the link resolves AND supports the specific claim"*. No reader anywhere. **UNDECIDABLE, 36/36 UNEVAL.**

2. **`open_access_full_text_retrieved` — `research/manuscripts/aso/lit-targets-aso-verify.json`, 58 records.** The artifact's own header field states: *"`open_access_full_text_retrieved=false` means only the abstract was retrievable. Where the manuscript needs a claim from the body of such a paper, that claim is UNVERIFIED and is named as such."* The field is written to decide whether a manuscript claim counts as verified, and **38 of 58 rows say `false`**. Key-literal grep across `*.py *.mjs *.sh *.yml`: **zero hits**. The naming-as-unverified it mandates is a human discipline, not a check.

3. **`read_level` — `research/modalities/emc-icdo-contamination.json`, 16 records.** The same field name carries the same contract elsewhere in the tree, stated outright at `research/autonomy/sprint-2026-09-01/S16-NEGATIVES-fetches.json:6`: *"Every record below is an ABSTRACT-level retrieval unless `read_level` says otherwise, and the findings file states its conclusions at that weight."* Values include `"[FT] for the body, NOT for Table 1"` and `"[FT], used as a [2°] source for another paper's numbers"` — precision that exists to bound what may be quoted. Zero readers.

4. **`figure_checked` — `research/modalities/emc-ipd-survival.json`, 17 records (5 true / 12 false).** ⭐ **This one is the interesting case and it cuts the other way.** `emc_ipd_survival.py:209` and `:230` make it load-bearing in prose (*"Rows still reading `figure_checked: False` are the ones whose full text this program cannot reach at $0. That is a REACHABILITY statement, never a statement about the paper."*), and nothing reads the field. But the same comment block, at `:220-228`, states the general problem in the repository's own words and records what was done about it:

   > *"AND ON 2026-08-27 EVERY ONE OF THOSE READINGS WAS RE-TAKEN BY AN INSTRUMENT, because **an eye reading recorded in a JSON field is unfalsifiable: nothing in the repository could disagree with it**. `research/modalities/km_risk_row_detect.py` measures the band structure beneath each figure's axis and answers present / absent / undetermined… THE TWO READINGS AGREE ON ALL NINE KAPLAN-MEIER FIGURES… and the instrument is shown capable of the other answer, because it fires on both figures that DO print a risk row."*

   So this program **independently identified W30c's undecidability class, named it precisely, and replaced the human-act field with a measurement that can disagree** — including a demonstrated positive control. `figure_checked` survives as a reachability label beside `risk_row_measured_2026_08_27`, which is the decidable field. **This is a precedent in the corpus, not a defect, and it is the honest answer to "what would you do about the other twenty" without me proposing anything.**

Two near-misses I record but do not count as instances:
- **`digitized_by`** is mandated by POLICY-evidence §2.7(c) (*"who read the figure and with what tool… an unattributed coordinate is indistinguishable from an invented one"*) and **is** read — `emc_ipd_survival.py:786` refuses admission without it. Presence enforced; the *content* (that a particular person used a particular tool) remains undecidable. §2.7(c) is therefore the **only** act-asserting policy sentence in this census with a refusal behind it.
- **`reviewedBy`** (registry, 1) carries `"Initial automated draft from published literature - NOT yet clinician-reviewed"` — a self-disclosure of an act *not* performed, unread by anything. Its honesty is the reason it is not a defect.

### R.4 Two structural observations the census produced

**F1 — the same field name is ENFORCED in one artifact and UNREAD in another, and a name-level grep hides it.** `verified_by` has 18 key-literal code hits, all in `systems/systems_check.py` and `systems/tests/`, all about `graph/requirements.json`. The **90** `verified_by` values in `citation-provenance-ledger.json` are read by nothing. `lint_citations.py` reads exactly two ledger keys — `key` (line 432, 445) and `status` (line 446, 537) — out of 237 entries; its own docstring at line 409 says *"the ledger records WHO CHECKED an identifier"*, and the who/when/where triple (`verified_by` / `verified_on` / `verified_source`, 90 each) is exactly the part nothing consumes. The machine-readable half (`status`: 143 `unverified_at_baseline`, 93 `verified`, 1 `known_absent_upstream`) is the half that is read. **Any census of this class done by field name alone will overstate coverage; it must be done per artifact.**

**F2 — a field in this class already caused a wrong committed claim, by ambiguity rather than by falsehood.** `research/modalities/emc-site-curation.json:27` records the incident verbatim: nine EMC series were declared unreachable because *"`openAccess` is a LICENCE field and it was read as an ACCESS statement. A restrictive licence and an unreachable full text are different facts."* Two of the nine (`bishop2019`/PMC7771031, `drilon2008`/PMC2779719) were then read at $0. The registry carries `openAccess` on all 25 citations and nothing reads it — so the field's only consumer was a human, and the human misread it. **Recording this as an already-corrected historical incident, not a live defect, and not as any statement about those papers.**

## Validation evidence

**RUN.** Environment: `/home/user/Rare-cancers`, HEAD `408b676aec3625a36917755662516232a27a1278` (unchanged start to end), `git status --porcelain` empty at both ends. System `python3` stdlib only (no third-party imports), `git`, `grep`. Scratch `/tmp/claude-0/w43/` (deleted). **No test suite was run and no pass/fail is asserted anywhere in this report.**

Key-literal reader grep, verbatim shape and decisive results:

```
$ grep -rnE "[\"']verified[\"']|\.verified\b" --include='*.py' --include='*.mjs' --include='*.sh' \
       --include='*.yml' --include='*.yaml' . | grep -v '/\.git/' | wc -l
86        # every hit read; ZERO touch research/data/emc-clinical-registry.json
          # (vast_filter_ablation.py:76 / vast_market_intel.py:161 are Vast.ai GPU offers;
          #  ternary_calib_search.py:82, fusion_frame_trap.py:579,591, test_layer1_curation.py:41
          #  are each about their own artifact)

$ grep -rn -- "verified" --include='*.py' … . | wc -l
5088      # substring grep, for contrast — this is why it was not used
```

Zero key-literal hits (the UNREAD set), each verified individually:

```
verified_on   0      verified_source 0    open_access_full_text_retrieved 0
retrievalNote 0      lastReviewed    0    reviewedBy   0
resolved_on   0      changed_on      0    published_at_utc 0    read_url 0
posted_by     0      date_read       0    fetched_via  0
read_level    0 outside its own generator research/modalities/emc_icdo_contamination.py
figure_checked 0 outside its own generator (all 17 hits are literal writes at
               emc_ipd_survival.py:241,254,272,276,280,284,305,309,313,317,321,327,331,336,361,380,384)
```

Registry `verified` enumeration (heredoc, verbatim):

```
11 /studies/items[]/verified
25 /registry/citations/<id>/verified      (masunaga2025 … galitskiy2025emcpembrolizumab)
{True}                                     # set of all 11 studies.items values
```

Ledger and IPD denominators (heredoc, verbatim):

```
ledger entries 237
kinds Counter({'DOI': 112, 'PMID': 75, 'PMCID': 27, 'ARXIV': 13, 'NCT': 7, 'GEO': 3})
status Counter({'unverified_at_baseline': 143, 'verified': 93, 'known_absent_upstream': 1})
with verified_by 90 with checked_by 14
figure_checked Counter({False: 12, True: 5})
```

Schema-enforcement path (read, not run): `systems/systems_check.py:495-522` validates `strategies/routes/blockers/modalities` `[S1]`, `lanes/requirements/instruments/publications` `[S3]`, `technologies` `[S2]`, `forecasts` `[S3]`. Extracted `required` arrays naming census fields: `blocker…/kind_history/items ['changed_on']`, `publication…/posted ['posted_by','published_at_utc']`, `requirement/$defs/requirement ['verified_by']`, `requirement…/state ['last_verified']`, `technology…/pending_signals/items ['seen_on']`, `technology/$defs/forecast ['last_reviewed']`, `document.schema.json ['last_verified']`.

Scratch removal and end state:

```
$ rm -rf /tmp/claude-0/w43 && ls /tmp/claude-0/w43
ls: cannot access '/tmp/claude-0/w43': No such file or directory
$ date -u ; git rev-parse HEAD ; git status --porcelain | wc -l
Tue Sep  8 04:40:38 UTC 2026
408b676aec3625a36917755662516232a27a1278
0
```

**PROPOSED (NOT RUN).** None. I authored no test, no patch, no gate and no validator, and I propose none. `pytest` is installed in this container per the campaign's settled finding, but no test in this census needed running to establish who reads a field — that is read off the source — and running one would have proved nothing about an act performed outside the repository.

## Limitations

1. **`grep` finds consumption, not intent.** A consumer could read one of these fields through a variable indirection, a `for k in row:` loop, or a dict comprehension my key-literal pattern misses. "UNREAD" means **I found no reader**, which is UNKNOWN rather than proven absence. I mitigated it by reading every hit for the 34 fields and by extracting schema `required` arrays, which caught 6 presence-readers that no Python line names.
2. **Enumeration is bounded by JSON.** I walked JSON only. Act assertions living in Markdown frontmatter, YAML, or prose inside these artifacts are not in the denominator — except `document.schema.json`'s `last_verified`, which I picked up through the schema. `research/autonomy/**` and `research/literature/**` were outside the named scope; `read_level` and `verified_utc` both have carriers there that I counted only where they fall inside the scoped groups.
3. **Field-name identity is not field identity** (F1). Every grade in R.2 is per artifact; a reader of `verified_by` in `graph/requirements.json` says nothing about `verified_by` in the ledger, and I have graded them separately.
4. **Denominators are small in the registry and large only in generated corpora.** 36 registry `verified`, 90 ledger triples, 1,157 `retrieved_file`. A clean census at n=36 is a census at n=36.
5. **I verified nothing by retrieval.** No network, no link opened. Every `verified: true`, `accessed`, `figure_checked: true` and `open_access_full_text_retrieved` value is **UNKNOWN — not confirmed and not refuted**. A field nothing reads is undecidable, never thereby false, and none of this is a defect in the data.
6. **No clinical claim.** This is a census of repository wiring. Nothing here says any treatment works, is safe, selective, or ready for a patient; no count in the registry is restated as a clinical claim; there is no wet lab and no EMC efficacy, safety or clinical-readiness statement anywhere in this report.
7. **Commit ordering is not established.** I measured the tree as it stands at one HEAD; I cannot say when any of these values was written or by which act.

## Stop condition

**Set up front:** enumerate act-asserting fields by *reading* the key space of the four artifact groups rather than guessing names; per field, count records and values, determine by key-literal grep and hit-reading whether any code reads it, and grade ENFORCED / UNREAD-BUT-DECIDABLE / UNREAD-AND-UNDECIDABLE with honest denominators; count the fields a committed prose sentence calls load-bearing that nothing reads; then return without proposing a repair.

**MET.** 34 fields graded — 13 ENFORCED, 1 UNREAD-BUT-DECIDABLE, 20 UNREAD-AND-UNDECIDABLE, ≈478 unread act-assertion records. **Four** load-bearing-by-sentence-but-unread fields, against W30c's one. W30c's registry finding is confirmed with its denominator corrected from 25 to **36/36 UNEVAL**. `pinned-figures.json` contributes zero members, so W28c's dead fields are an adjacent class rather than the same one.

## Tool-call and wall-clock count actually used

**14 tool calls** (all Bash; 2 of them the mandated start/end state records, 1 the scratch deletion). **0** network calls, **0** retrieval calls, **0** MCP calls, **0** generator or module invocations, **0** test runs, **0** repository writes, **0** git write operations. Wall clock **04:35:29Z → 04:40:38Z ≈ 5.2 minutes** of measured tool time plus report drafting. Well inside the ~40 call / ~40 minute target; returning rather than padding.

## Next concrete action

**One artifact, one question, no science and no writes: audit `research/manuscripts/citation-provenance-ledger.json` against `lint_citations.py` and report which of its 237 entries' fields the gate actually consumes.** It is the largest act-assertion store in the repository (237 entries, 90 carrying an unread who/when/where triple), its own docstring says it exists to record *who checked* an identifier, and the gate reads only `key` and `status` — while `checked_on`/`checked_by` are asserted by a test for **13 ARXIV rows out of 237**. The successor question is whether the 143 `unverified_at_baseline` rows and the 93 `verified` rows differ in any field a consumer could ever distinguish, which decides whether the ledger's status vocabulary is decidable or is a second instance of the same shape at 20× the record count.

I propose this and nothing else. **I have written nothing, edited no artifact, touched the clinical registry not at all, authored no repair, gate or test, and weakened no guard.** W30c's and W28c's own proposals stand unaddressed by me; the repository's own answer to this class already exists as a precedent at `research/modalities/km_risk_row_detect.py`, and naming it is not the same as proposing to apply it.
