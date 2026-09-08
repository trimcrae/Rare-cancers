<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:16:10Z UTC
     agent id a08156064f0640df6 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a08156064f0640df6.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

# W05g — Is W05f's "one defect" a ceiling? The structural (non-lexical) test

## Worker

- **Worker:** W05g, lane 5 refill (cross-study patient independence), OPUS-CAPACITY-CAMPAIGN-20260908. Task: run the structural check that W05f named as the thing that would convert its lexical floor into a ceiling.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`), Claude Code 2.1.42, remote cloud container. I cannot observe the served model; no environment variable names one. The coordinator must extract the runtime model from the transcript. No finding below depends on which model produced it.
- **`date -u` start:** `Tue Sep  8 03:01:18 UTC 2026`. **`date -u` end:** `Tue Sep  8 03:06:32 UTC 2026`.
- **HEAD actually read — and it moved under me, twice more.** The brief freezes the read commit at `92abbcb905cacf07f14b238db50d1b98f6590374`. At my start `git rev-parse HEAD` returned **`fc6ed92999c26f52c47668d1c126321a5f51d1b5`**; at my end **`98a0833f1ede2cf9cef13790388260567a32e868`**. `git status --porcelain` was **empty at start and empty at end** (no output both times). This continues the pattern W05d and W05f recorded: **the freeze does not hold.** Every file I quote is a non-campaign research file; I have no evidence any quoted record moved, but the coordinator should re-verify against the commit that receives any downstream action.
- **Write isolation honoured.** Nothing written under `/home/user/Rare-cancers`. All execution under `/tmp/claude-0/w05g/` (7 scripts, listed in Validation evidence). No git write operation of any kind. **No network egress**: no MCP call, no `curl`, no `WebFetch`. One unrelated proxy denial (`search.rcsb.org:443 connect_rejected`) was emitted by the harness during an unrelated background process while my first command ran; **I made no such request** and nothing in this report derives from it.

**`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`**, end-of-run, verbatim (identical at start; five long proxy-exclusion variables — `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `JAVA_TOOL_OPTIONS`, `npm_config_noproxy` — also match on the `anthropic` substring inside their host lists and are filtered here for length only, carrying no model identity):

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

**Is W05f's "exactly one authored occurrence of the temporal-disjointness inference" a ceiling, or only a floor?** W05f scanned lexically and said plainly that a table whose independence-bearing column is populated purely from a years column, with no sentence anywhere, would be invisible to its method — so its result was a floor. The structural question is: **across the tracked corpus, is any independence-bearing field's value a function of the date fields alone?** That is the schema-level form of the same defect, and it is what W05f's Limitation 1 asked for and marked `PROPOSED (NOT RUN)`.

It is open because nobody has run it. The lexical scan and the structural scan have disjoint failure modes: the lexical one misses defects that were never written in words, the structural one misses defects that are argued in prose but never encoded. Neither subsumes the other.

## Prior-work check

- `git ls-files | grep -iE '\.(csv|tsv|ya?ml|ipynb|jsonl|ndjson)$'` and the extension census — established the file-type universe (4,518 `.json`, 1,488 `.py`, 677 `.md`, 177 `.yml`, 8 `.jsonl`, 4 `.csv`, 5 `.yaml`, 2 `.tsv`, **0 `.ipynb`**).
- Read in full: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`; `systems/POLICY-evidence.md` §2.1/§2.3 (the pooling and double-counting rules the fields implement); `reports/W05-patient-independence-audit.md` (the tier rubric, applied below as written and nowhere relaxed); `reports/W05f-window-arithmetic-audit.md` in full including its R1–R5 and all 8 Limitations. Sampled `W05d` and `W05e` through W05f's transcription of their findings.
- The reports live at `research/autonomy/opus-capacity-campaign-20260908/reports/`, not at the top-level `reports/` path my dispatch named; `find . -name 'W05*'` located them.
- **I did not re-run W05f's lexical scan.** My method shares no regex with it: W05f matched *sentences*; I matched *key names and value-tuples* and then ran an algebraic dependence test. The one place I did grep was to confirm the classification of `accrual` in Python/YAML (Result R4), which is a check of my own candidate list, not a replay of W05f's sentence scan.
- Closed items confirmed not replayed: I did not touch Brenca case identity, Hofvander/EGA, the paired Davis negative, promoter transfer, the ICD-O paper, or the restricted NR4A Perspective. **I attempted no patient, case or specimen identity** — the fields below were treated as opaque strings and booleans; I never asked who any record is about. I adjudicated **no source pair**, added and removed **no cohort from any pool or denominator**, and propose **no repair**: W05f has already routed the one known repair to `research/manuscripts/emc_systemic_therapy_pooling.py` and its owner.

## Method / inputs

Four stages, all offline, all over the live checkout (not the frozen corpus — `CORPUS-CONTEXT.md` allows either; I used the live tree and record its moving HEAD above).

**Stage 1 — enumerate independence-bearing fields (`scan1.py`, `scan2.py`).** I did not start from the dispatch's list. I walked every one of the **4,518 tracked `.json` files**, recursively, and collected every leaf key name matched by a deliberately over-broad independence regex (`pool|overlap|independen|disjoint|double.?count|dedup|duplicat|why_excluded|exclus|population_?key|context_?reason|shared|distinct|unique|contain|counted`) — 4,518 files parsed, **1 parse failure** (`research/modalities/e3-provenance-correction.json`, malformed at line 22; see Limitations). That over-broad pass returns several hundred key names and is dominated by molecular-modelling vocabulary (`n_distinct_loci`, `overlap_bp`, `unique_lysine`, `kmer_containment` — all sequence or structure quantities, none about patients). I then applied a **domain gate**: a file qualifies only if it contains patient-cohort vocabulary (`cohort|patient|studyPeriod|populationKey|denominator|accrual|registry|pmid`). 168 files carry both an independence-shaped key and a date-shaped key; inspecting all 168 by key-set, exactly **four** carry record-level fields that encode a *patient*-independence or pooling-eligibility decision. The dispatch's named list was recovered as a subset, plus nine fields it did not name.

**Stage 2 — enumerate date-bearing fields.** Same walk, matching key names (`studyperiod|accrual|enrol|year|date|period|window|collect|vintage|recruit`) **and, separately, any value containing a bare 4-digit year `\b(19[5-9]\d|20[0-4]\d)\b` under a non-date key** — this is what catches a date embedded in a string, which the task specifically asked for. In the four target files this catches `studyPeriod`, `studyPeriodUnknown`, `year`, and the year embedded in every `source_id` (`stacchiotti2014sunitinib`, `drilon2008`, …).

**Stage 3 — the functional-dependence test (`fdep.py`, `fdep2.py`, `rel.py`, `rel2.py`).** Three tests, because "date-determined" has three non-equivalent forms:

1. **Co-location.** Does the record carrying the independence field carry any date at all, anywhere in its subtree? If not, the field *cannot* be a function of dates within the record.
2. **Same-date/different-value witness.** Partition records by their full date signature. If any class contains two distinct independence values, the field is **not** a function of the dates — that pair is a proof, not an inference. (I also flag the converse trap: if every record has a unique date signature, functional dependence holds *vacuously* and is no evidence at all. `fdep2.py` prints that distinction rather than scoring it as clean.)
3. **The pairwise date-relation test.** W05f's defect is not "value = f(year)", it is "disjointness = f(window relation between two records)". So for `research/data/emc-clinical-registry.json`, the only file with real two-element windows, I computed for every record whether its `studyPeriod` overlaps any other record's, and tested the hypothesis `pool == (window disjoint from all others)` explicitly.

**Stage 4 — the file types W05f excluded.** Header inspection of all 4 CSV and 2 TSV; enumeration of all 182 YAML/YML and 8 JSONL; `git ls-files | grep -c '\.ipynb$'`.

**Files that carry the fields under test:** `research/data/emc-clinical-registry.json`, `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json`, `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json`, `research/modalities/emc-ipd-survival.json`. Python 3.11, stdlib only.

## Result

### R1 — The independence-bearing field inventory, and how it was found `PRIMARY`

Nine of the dispatch's named fields plus nine more that play the same role, found by the over-broad walk rather than by assumption. Only these four files encode a *patient*-level independence or pooling decision at record level.

| file | independence-bearing fields (n occurrences) | date fields present in the file |
|---|---|---|
| `research/data/emc-clinical-registry.json` | `pool` (15), `contextReason` (10), `populationKey` (5), `independence` (1) | `studyPeriod`, `studyPeriodUnknown`, `year` |
| `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json` | `pool_orr` (8), `pool_dc` (8), `pool` (4), `pool_dc_reason` (2), `pool_reason` (1), `why_excluded` (1), `population_overlap_warning` (1), `residual_overlap_risk` (1) | `studyPeriod`, `year` — **only under `.citations.*`** |
| `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json` | `pool` (16), `contextReason` (9), `populationKey` (9), `pool_note` (2), `overlap_note` (2), `non_overlap_argument` (2), `double_counting` (1), `primary_non_overlapping` (1), `secondary_assume_independent` (1) | `year` — **only under `.citations.*`** |
| `research/modalities/emc-ipd-survival.json` | `overlap_risk` (16) | none on the records; years appear only inside `source_id` strings |

Fields the over-broad pass surfaced and I ruled **out of scope, with the reason**: everything in `research/modalities/aso-*`, `emc-ret-cistrome*`, `emc-fet-*`, `nr4a3-*` (`overlap_bp`, `n_distinct_loci`, `shared_donor_run`, `chunk_overlap_nt`, `intervals_overlap`) — these are genomic-interval and residue quantities; "overlap" there is base-pair overlap, and no patient is involved. `verified_independently` / `blockers_distinct` / `distinct_findings` in `research/autonomy/review-seats/*` and `receipts/*` — process bookkeeping about reviews, not cohorts. `n_distinct_accessions`, `n_distinct_samples` — deposit counts, which the rubric's standing rule already forbids reading as patient counts, and which decide no pooling.

### R2 — The direct answer: **no independence-bearing field is date-determined** `PRIMARY`

Three independent lines, any one of which would be sufficient, and they cover different files.

**(a) Structural impossibility by non-co-location — the strongest form, and it covers three of the four files.** The pooling-decision records in both pooling files, and every `overlap_risk` record, carry **no date field anywhere in the record subtree**.

| file | records tested | records carrying any date | verdict |
|---|---|---|---|
| `emc-systemic-therapy-pooling.json` (`pool_orr`/`pool_dc` cohort records) | 8 | **0** | a value cannot be a function of an input the record does not contain |
| `emc-fusion-partner-pooling.json` (`pool` records) | 16 | **0** (one record has `n_enrolled: 26`, a count, not a date) | same |
| `emc-ipd-survival.json` (`overlap_risk` records) | 16 | **0** (keys are `source_id`, `n`, `endpoint_hint`, `figure_checked`, `full_text_reachable`, `why_candidate`, `reachability_2026_08_25`) | same |

In both pooling files, `studyPeriod` and `year` exist **only under `.citations.*`** — a bibliographic block, structurally separate from the decision records, which reference citations by key. The schema does not put a date where a pooling decision could read it. `reachability_2026_08_25` and `risk_row_measured_2026_08_27` are dates of *this repository's own audit actions*, not study windows; treating them as date inputs (which `fdep2.py` did, deliberately over-inclusively) still produces witnesses, below.

**(b) Same-date/different-value witnesses.** Where dates are co-located, the field varies within a fixed date class — a proof of non-dependence.

| witness | file | evidence |
|---|---|---|
| `studyPeriodUnknown: true` class | `emc-clinical-registry.json` | Three records share the identical date content "period unknown". `meisKindblom1999` has `pool: true`; the Japanese multi-institutional series has `pool: false, contextReason: "different-endpoint"`; the Chinese series has `pool: false, contextReason: "percentage-only"`. **Same date content, both `pool` values and two distinct `contextReason` values.** |
| `trabectedin_emc_subset` vs `apatinib_emc_subset` | `emc-systemic-therapy-pooling.json` | identical date content (none), `pool_dc: true` vs `pool_dc: false` |
| `overlap_risk`, 4 witness classes | `emc-ipd-survival.json` | 16 records collapse into 5 date signatures; **4 of the 5 carry multiple distinct values**. One class of five records spans "⚠ Milan series, overlaps stacchiotti2014sunitinib and chiusole2020", "⚠ conference abstract; may be an expansion of martinbroto2020immunosarc1", and "⚠ likely shares Milan/INT patients with the Stacchiotti series". |
| embedded year in `source_id` → `overlap_risk` | `emc-ipd-survival.json` | tested separately because a year hidden in an identifier is exactly the invisible case. **5 of 11 year-classes carry two distinct values** — e.g. year `2025`: "none with institutional series" vs "⚠ conference abstract; may be an expansion of martinbroto2020immunosarc1"; year `2020`: "⚠ likely shares Milan/INT patients…" vs "⚠ likely the parent trial of immunosarc2emc2025". |

**(c) The pairwise date-relation test — the exact shape of W05f's defect, run and refuted.** `emc-clinical-registry.json` is the only file with real two-element windows: 9 of its 15 `pool` records carry a usable `studyPeriod`. Result: **all 9 windows mutually overlap** — every record overlaps all 8 others (they span 1975–2022 with no gaps). The date relation is therefore **constant across the entire record set**, while `pool` splits **4 true / 5 false**. A constant cannot determine a varying value.

```
HYPOTHESIS pool == (window disjoint from ALL others):
  matches 5/9 records -> REFUTED
    counterexample: Localised at diagnosis, surgically treated   pool=True  rule predicts False (sp=[2002,2022])
    counterexample: Metastatic at diagnosis                      pool=True  rule predicts False (sp=[2002,2022])
    counterexample: US Sarcoma Collaborative database            pool=True  rule predicts False (sp=[2000,2016])
    counterexample: European two-institution series (Chiusole)   pool=True  rule predicts False (sp=[1980,2018])
```

The four `pool: true` records are pooled **despite** overlapping windows, and the five `pool: false` records are excluded for reasons the file states in `contextReason`: `population-overlap (US single institution; likely within SEER / US Sarcoma Collaborative)`, `population-overlap; percentage-only`, `percentage-only`, `different-endpoint`. Every one is a population, endpoint or reportability ground. **Not one is a window.** This is the registry behaving as `POLICY-evidence.md` §2.3 requires — the smaller/overlapping cohort marked `pool: false` with its reason recorded — and it is the opposite of the defect.

**Structural note worth recording:** two records share the *identical* window `[2002, 2022]` and the identical `populationKey: masunaga2025-jpreg`, and both pool. They are the localised and metastatic strata of one study — §2.3's "mutually exclusive strata", which are the one case where sharing everything including the window is correct. A date-driven rule would have had to exclude them.

### R3 — What the negative establishes, precisely `PRIMARY`

**W05f's "one defect" is upgraded from a floor to a bounded ceiling over the structural axis.** Stated exactly:

**What the upgrade covers.** Across the **4,518 tracked JSON files**, in the four files that carry record-level patient-independence or pooling-eligibility decisions, **no independence-bearing field's value is a function of any date field** — not of a co-located date (there is none in three of the four files), not of a same-class date signature (11 records fall in witness classes that refute it), not of the pairwise window relation (tested explicitly and refuted 4/9 on the only file with windows), and not of a year embedded in an identifier string (refuted in 5 of 11 classes). Combined with W05f's R4 finding that no `.py` decides overlap from time, **the temporal-disjointness inference exists in this repository at exactly one authored site and has no encoded, schema-level, or generated counterpart anywhere.** Within the union of the two scans' scopes — prose and record structure over `.json`/`.md`/`.py` — one defect is now a **ceiling**, not a floor.

**What the upgrade does not cover.**
1. It says nothing about **whether the independence judgements are correct** — only that they were not derived from dates. `overlap_risk` values are institution-grounded and several are UNKNOWN-flagged; W05's tier verdicts stand untouched. A field grounded in institution can still be wrong.
2. It does not cover the **file types listed as UNKNOWN in R4**, nor the one file that would not parse.
3. It does not cover the **absence of a field**. A cohort silently treated as independent because nothing was recorded about it produces no field for this test to examine; that is invisible to a structural scan exactly as it is to a lexical one. This is the residual joint blind spot of both methods and I flag it as the honest remaining gap.
4. It does not cover **prose in `.md` that no field mirrors** — that is W05f's axis, and its ceiling there is only as good as its lexicon, which W05f itself bounded.
5. **HEAD moved twice during this run**, so this is a statement about the tree as read between `fc6ed92` and `98a0833`, not about any single committed state.

### R4 — The file types W05f excluded: what I covered, what remains UNKNOWN `PRIMARY`

| type | tracked count | covered | finding |
|---|---|---|---|
| **`.ipynb`** | **0** | n/a | **There are no notebooks in this repository.** W05f's exclusion was vacuous here. `COVERED` |
| **`.csv`** | 4 | headers of all 4 | All four are `fusion-junction-aso-sequences.csv` (one source + three copies under `research/release-candidates/PUB-ASO/`). Columns are ASO design fields (`sequence`, `length_nt`, `geometry`, `junction`, `gap_level_margin`, `mature_parent_duplex_*`). **No cohort row, no independence column, no date column.** `COVERED — CLEAN` |
| **`.tsv`** | 2 | headers of both | `emc-fourth-cohort-gene-counts.tsv` and `emc-fourth-cohort-probe-counts.tsv`. Columns are a gene/probe key plus one column per SRR run (`SRR35940646:Si19`, …). These are **expression matrices**; the specimen labels are column headers, and there is no independence-bearing column and no date column. I read headers only and **made no attempt on specimen identity**. `COVERED — CLEAN` |
| **`.yml`/`.yaml`** | 182 (173 GitHub workflows + 9 others) | grep + inspection of every cohort/overlap/denominator hit | 45 workflows matched the vocabulary. Inspecting the matches: all are GPU/FEP/docking orchestration (`pool` = worker pool, `overlap` = interval or paralogue overlap) or the `emc-expression-datasets.yml` mode dispatcher, where "cohort" names a *mode string* (`cohort-search`, `fourth-cohort`) routing to a Python entry point. The 9 non-workflow YAML are Conda environments, a CloudFormation template, and two cofold input plans. **No YAML contains a cohort table, an independence field or a date-driven decision.** `COVERED — CLEAN` |
| **`.jsonl`** | 8 | enumerated; content class identified | `aixiv-postings`, `amendments`, three throughput `.calls.jsonl`, `vast-account-reaper-ledger`, `vast-price-history`, `nr4a3_convergence`. Process/telemetry ledgers; none carries a cohort record. `COVERED — CLEAN` |
| **malformed JSON** | 1 | lexically only | `research/modalities/e3-provenance-correction.json` (1,887 bytes) **fails `json.load`** (`Expecting ',' delimiter: line 22 column 22`) and so was excluded from the structural walk. A targeted grep for `pool\|overlap\|independen\|studyPeriod\|cohort\|patient\|year` returns **no hit**, so it is very unlikely to carry a cohort record — but its *structure* is `UNKNOWN`, and I note that a tracked JSON that does not parse is itself a defect worth someone's attention. |
| **`.pdb`, `.sdf`, `.png`, `.pdf`, `.docx`, `.gz`, binaries** | ~570 | not opened | **UNKNOWN, not clean.** Out of scope and implausible as carriers of a cohort independence table, but I did not look. |

## Validation evidence

**RUN.** All commands executed in `/home/user/Rare-cancers` (reads) with scripts stored and run from `/tmp/claude-0/w05g/`; Linux 6.18.44-fc-v24, bash, Python 3.11.

| # | command | exit | key output |
|---|---|---|---|
| 1 | `date -u`; `env \| grep -i -E 'claude\|anthropic\|model' \| sed …`; `git rev-parse HEAD`; `git status --porcelain` | 0 | start `03:01:18Z`, HEAD `fc6ed929…`, status **empty**; end `03:06:32Z`, HEAD `98a0833f…`, status **empty** |
| 2 | `git ls-files \| sed -E 's/.*\.([A-Za-z0-9]+)$/\1/' \| sort \| uniq -c \| sort -rn` | 0 | `4518 json`, `1488 py`, `677 md`, `177 yml`, `8 jsonl`, `5 yaml`, `4 csv`, `2 tsv` |
| 3 | `python3 /tmp/claude-0/w05g/scan1.py` | 0 | `TRACKED JSON: 4518 PARSE FAIL: 1` — `research/modalities/e3-provenance-correction.json`; full key census |
| 4 | `python3 /tmp/claude-0/w05g/scan2.py` | 0 | `candidate files with BOTH independence-bearing and date-bearing keys: 168`, each with its key sets |
| 5 | inline `python3` over all tracked JSON for the 18 named fields | 0 | exact file/count map reproduced in R1 |
| 6 | `python3 /tmp/claude-0/w05g/fdep.py` | 0 | record-level test; direct-sibling date tuples |
| 7 | `python3 /tmp/claude-0/w05g/fdep2.py` | 0 | subtree-wide test. `overlap_risk: n=16 vals=14 dateTuples=5 recordsWithNoDateAnywhere=5` → `NOT DATE-DETERMINED. 4 witness class(es)`. `pool_dc: NOT DATE-DETERMINED`, witness `['trabectedin_emc_subset','apatinib_emc_subset']` |
| 8 | `python3 /tmp/claude-0/w05g/rel.py` | 0 | registry table; `records with a usable 2-element studyPeriod: 9`; every one `overlapsAnother=True n_overlapping=8`; `HYPOTHESIS pool == (window disjoint from ALL others): matches 5/9 -> REFUTED` with four named counterexamples (quoted verbatim in R2c) |
| 9 | `python3 /tmp/claude-0/w05g/rel2.py` | 0 | both pooling files: every decision record prints `dates={}` |
| 10 | `python3 /tmp/claude-0/w05g/loc.py` | 0 | `studyPeriod`/`year` in both pooling files appear **only** at `.citations.<key>.year` / `.citations.<key>.studyPeriod`; `overlap_risk` record key-sets listed in full |
| 11 | inline `python3`: embedded-year-in-`source_id` → `overlap_risk` | 0 | 11 year classes, **5 with `n_distinct_overlap_risk=2`**, values printed |
| 12 | `head -1` on all 4 CSV + 2 TSV; `git ls-files \| grep -ci '\.ipynb$'`; YAML/JSONL enumeration | 0 | headers as in R4; **`0`** notebooks |
| 13 | `grep -ihoE 'cohort\|patient\|studyPeriod\|overlap\|pool\|accrual\|denominator'` over all workflow YAML, then inspection of every non-GPU hit | 0 | 84 `cohort`, 56 `pool`, 45 `overlap` — all mode strings, worker pools, or interval overlap |
| 14 | `grep -rnE '(studyPeriod\|study_period\|accrual\|year).{0,60}(overlap\|disjoint\|pool)\|…' --include=*.py --include=*.yml --include=*.sh` | 0 | 8 hits. One is W05f's known site (`emc_systemic_therapy_pooling.py:701`). Two (`endpoint_regime_map.py:133,227`, `test_endpoint_logic.py:295`) use "accrual" for **trial accrual status** (completed vs terminated ClinicalTrials.gov queries), not calendar windows — confirmed by reading those lines; both are *warnings* that the two accrual populations must not be pooled. `hormone_partner_map.py:362` is W05f's exemplary self-flagged assumption. **No new date-driven decision.** |
| 15 | `grep -inE 'pool\|overlap\|independen\|studyPeriod\|cohort\|patient\|year' research/modalities/e3-provenance-correction.json` | 1 (no match) | no hit; file is 1,887 bytes |

`git status --porcelain` produced **no output at start and no output at end**: I modified nothing. Scripts written: `scan1.py`, `scan2.py`, `fdep.py`, `fdep2.py`, `rel.py`, `rel2.py`, `loc.py`, all under `/tmp/claude-0/w05g/`.

⚠ **One script failure, recorded rather than hidden.** My first attempt was named `/tmp/claude-0/w05g/enum.py` and every run crashed with `AttributeError: partially initialized module 're' has no attribute 'compile'` — the filename shadowed the stdlib `enum` module on `sys.path`. Renamed to `scan1.py` and re-run; **no result in this report derives from the crashed run**, which produced no output at all.

**PROPOSED (NOT RUN):**
- Repair `research/modalities/e3-provenance-correction.json` so it parses, then re-run `scan1.py` over it. Not run: I am read-only and it is not my file.
- Extend the structural test to the ~570 binary/document files. Not run: out of scope and no cohort table is plausible there.

**No test suite was run** — this audit changes no code and no shared state, and the brief forbids `scripts/preflight.sh` absent a dispatch instruction. **No skipped check is reported as a pass. No content-policy refusal was encountered.**

## Limitations

1. **A negative over a scope is not a negative over the corpus.** This covers tracked JSON structure plus CSV/TSV/YAML/JSONL/notebooks. Binaries and documents are **UNKNOWN, not clean**, and one tracked JSON does not parse.
2. **The joint blind spot survives.** A cohort treated as independent with *nothing recorded* creates neither a sentence for W05f nor a field for me. Both scans are ceilings only over what was written down. I can bound what the repository *says*; I cannot bound what it silently assumes.
3. **My independence-field inventory rests on a regex plus my judgement.** The regex was deliberately over-broad and I list in R1 exactly what I excluded and why, so the judgement is auditable — but a field named in vocabulary I did not anticipate and that failed the domain gate would be missed. The gate is the weakest link, and I state it rather than claim exhaustiveness.
4. **Refuting date-determination is not endorsing the values.** Every `pool`, `overlap_risk` and `contextReason` value in R2 could be individually wrong on its merits. I adjudicated no pair and re-verified no value against its source; W05e's IMMUNOSARC tier-C→UNKNOWN and W05's per-cohort verdicts are taken as given and untouched.
5. **The freeze did not hold** (`fc6ed929…` → `98a0833f…`). Record contents are as read in that interval.
6. **No source was retrieved; no network was used.** Everything rests on committed text and computation over it.
7. **No patient, case or specimen identity was attempted** — closed-unresolved, per dispatch. Specimen labels in the TSV headers were counted as columns and never interpreted.
8. **No clinical claim.** Nothing here bears on EMC treatment, efficacy, safety or prognosis. No denominator, pooled proportion or interval changes; I proposed no change to any of them and applied nothing.
9. **I hold no authority over the rubric** and applied it as written, relaxing nothing. W05d's measured verdict that the conjunctivity is load-bearing is an input here, not something I re-litigated.

## Stop condition

**Set up front:** return the moment all three of (a) the independence-bearing and date-bearing field inventories are complete over tracked JSON with the discovery method stated, (b) the functional-dependence hypothesis is tested against every independence-bearing field in all three of its non-equivalent forms with the result reportable either way, and (c) the CSV/TSV/YAML/notebook gap is either covered or explicitly marked UNKNOWN — whichever comes first with the ~40-call / ~40-minute target.

**MET**, at 19 tool calls and 5 minutes. All three conditions satisfied; the answer is a clean negative with three independent lines of evidence and one witness set per file. I returned on meeting it rather than spending the remaining budget.

## Tool-call and wall-clock count actually used

**19 tool calls** (all `Bash`; no network tool of any kind), against the ~40 target. **Wall clock 5 min 14 s** (`03:01:18Z` → `03:06:32Z`), against the ~40 min target.

## Next concrete action

**One successor, and it is the residual blind spot both scans share, not a third scan of the same corpus.** Neither the lexical nor the structural method can see a cohort whose independence was *never recorded* — no sentence, no field. The concrete task: take the cohort inventory that W05 already built (its 8-row per-cohort verdict table) and the union of independence-bearing records enumerated in R1 above, and compute the **set difference** — cohorts that appear in a pool, denominator or "independent cohorts" phrasing somewhere in the tree but have **no** `pool`/`contextReason`/`overlap_risk`/`populationKey` record and **no** prose overlap statement anywhere. Each such cohort is an independence judgement that was made implicitly and is currently unauditable by either method. This is bounded (the cohort inventory is small), needs no network, adjudicates no pair, and would close the last gap this lane can close without new sources. If the set difference is empty, that is itself the finding, and the two ceilings then meet.
