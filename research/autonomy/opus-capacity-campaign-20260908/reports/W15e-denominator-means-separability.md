> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

## Worker

**W15e**, lane 15 refill — data ingestion / normalisation / evidence retention. Successor to W15d.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) from my own system context. No environment variable in this container names a served model. The coordinator must extract the actual per-child runtime model from the transcript; I do not assert it as observed fact.

`date -u` at start: `Tue Sep  8 02:35:17 UTC 2026`. At end: `Tue Sep  8 02:37:51 UTC 2026`.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (verbatim; I dropped only the five long proxy/host-list lines `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS`, which name no model — nothing else altered):

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

**HEAD actually read: `7d081218f107363573573e6d102e4334567adf77`** (`git rev-parse HEAD`, working tree clean, `git status --porcelain` → 0 lines at start and at end). This is **not** the `92abbcb905cacf07f14b238db50d1b98f6590374` named as the frozen read commit in `COMMON-BRIEF.md`; the checkout has moved since the brief was written. I read the tree as it actually stands and record the real commit. I also read the frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/` (base `93b75888e31976195145e2404373b2d7a512f6d1`). I wrote nothing into the repository; my only writes were `/tmp/claude-0/w15e/enumerate.py` and `/tmp/claude-0/w15e/classify.py`.

## Question

**Can each of the seven distinct committed `denominator_means` values be separated into (a counting unit, a population definition) without losing a qualifier?** And, as the design question W15d routed: would a required closed-enum `denominator_unit` **beside** a retained free-text `denominator_means` be a strictly-stronger guard than `I6`, and what would it cost?

Open because W15d measured that `I6` refuses **0 of 6** of lane 15's STATED denominators and destroys both computable rates, then found the field as committed is a **population definition, not a counting unit** — so `I6` satisfies the invariant by deleting the evidence. W15d explicitly did not test whether the two-field repair is even possible on the committed strings, and named exactly that as the successor's task. **I assign no unit to anything**; what any `n` counts is W13b/W13c's question and I do not touch it.

## Prior-work check

```
$ grep -rln "denominator_means" --include=*.json --include=*.py --include=*.md . | grep -v '^./.git'
```
16 files: the four tracked JSON files, three committed writers, two committed tests, `research/autonomy/autonomy-state.json`, `research/autonomy/sprint-2026-09-01/S18-FALSE-ABSENCES.md`, and the five lane-15 campaign reports. This **reproduces W15d's correction of W15c** exactly: the key is committed, not novel to lane 15.

```
$ grep -rn "denominator_unit" . | grep -v '^./.git'
```
Three hits, **all inside `W15d-i6-invariant-consequences.md`** (lines 214, 366, 393) — i.e. only as W15d's proposal. No committed file, no writer, no test uses it.

```
$ grep -rl "denominator_unit" /tmp/claude-0/frozen-corpus/extracted/corpus/ | wc -l   → 0
$ grep -rl "denominator_means" /tmp/claude-0/frozen-corpus/extracted/corpus/ | wc -l  → 11
```
The frozen corpus (base `93b`) contains `denominator_means` in 11 files and `denominator_unit` in **none**. Per `CORPUS-CONTEXT.md` this snapshot is selected, not complete, so this is evidence the two-field split has not been done here, **not** proof of repository-wide absence.

```
$ git ls-files | grep -i -E "denominator|retained"
research/autonomy/opus-capacity-campaign-20260908/reports/W07-patient-reported-outcomes-denominators.md
research/autonomy/opus-capacity-campaign-20260908/reports/W07b-toxicity-denominator-enumeration.md
research/autonomy/opus-capacity-campaign-20260908/reports/W15c-retainedfact-registry-composition.md
research/literature/emc-trabectedin-denominator-2026-09-01.json
research/modalities/tests/test_step1_blocked_denominator.py
```
W07/W07b are separate lanes enumerating *clinical* denominators in sources; I am classifying *strings in committed JSON*. No overlap.

I read `CLOSED-WORK.md` in full. I am not replaying: PUB-EMC-CLASSIFICATION, the registry ICD-O paper (user-rejected), any Brenca route, any unrecovered-source route (I fetched nothing — **no network was used at all**), lane 11's source-index, or the frozen external-validation comment. I read `systems/POLICY-evidence.md` in full before drawing any conclusion touching the clinical registry; see Result §4. I did **not** derive any denominator from a percentage — W15c's flagged hazard — and I derived no denominator at all.

## Method / inputs

- Live checkout `/home/user/Rare-cancers` @ `7d08121`, read-only. Frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/` (read, not copied, not overlaid).
- Four tracked JSON files, read via `json.load`, walked recursively to find every `denominator_means` key with its full JSON path and its sibling keys.
- `systems/POLICY-evidence.md` (DOC-POLICY-EVIDENCE, `last_verified: 2026-08-05`), §2.1 and §2.3 in particular.
- `research/autonomy/opus-capacity-campaign-20260908/reports/W15-*.md`, `W15b-*`, `W15c-*`, `W15d-i6-invariant-consequences.md`.
- Scripts I authored and ran outside the tree: `/tmp/claude-0/w15e/enumerate.py`, `/tmp/claude-0/w15e/classify.py`. `python3` as installed in the container. No third-party packages.

**The classification rule, stated before it was applied, so the result is mechanical rather than an opinion.** For each string I locate every token that could serve as a countable head for the recorded `denominator` integer, using a fixed candidate lexicon `patients?|cases?|tumou?rs?|specimens?|samples?|lesions?|subjects?`, distinguishing *free* occurrences from occurrences *bound inside a numeric compound* (regex `[0-9]+-<lemma>`). Then:

- **NO UNIT PRESENT** — no candidate head occurs anywhere in the string.
- **SEPARABLE** — exactly one free candidate head occurs and no bound occurrence exists; deleting that single token leaves a residue that is still a well-formed population definition retaining every qualifier verbatim.
- **ENTANGLED** — otherwise: the candidate head also occurs *inside* qualifier text, or occurs at two different scopes, so no single deletion is determinate and lifting a unit out cannot be done without touching the qualifier.

**What this rule does and does not decide.** It measures whether a string *separates*. It does **not** decide what the unit is. The candidate lexicon is a search list, not a unit enum, and the fact that one lemma happens to match in all seven strings is a lexical observation I report as such — I explicitly decline to declare it the counting unit for any record. That determination belongs to W13b/W13c and is untouched here.

## Result

### 1. Enumeration — 8 occurrences, 7 distinct values, 4 files — PRIMARY

| # | File | JSON path | sibling `denominator` |
|---|---|---|---|
| V1 | `research/modalities/emc-care-delivery-evidence.json` | `$.absences[0].quotes[0].denominator_means` | 29 |
| V1 (dup) | `research/modalities/emc-care-delivery-evidence.json` | `$.corpus_quotes[0].denominator_means` | 29 |
| V2 | `research/modalities/emc-site-curation.json` | `$.series[0].metastatic.denominator_means` | 26 |
| V3 | `research/modalities/emc-site-curation.json` | `$.series[1].metastatic.denominator_means` | 29 |
| V4 | `research/modalities/emc-site-curation.json` | `$.series[2].metastatic.denominator_means` | 13 |
| V5 | `research/modalities/emc-radiotherapy-contradiction.json` | `$.carbon_ion.patients_reported.denominator_means` | 8 |
| V6 | `research/modalities/emc-radiotherapy-contradiction.json` | `$.carbon_ion.quotes[0].denominator_means` | 8 |
| V7 | `research/manuscripts/care-delivery/emc-absence-claims-refuted.json` | `$.refutations[1].counts_now_readable_and_previously_absent.denominator_means` | 8 |

V1 is byte-identical in two places in one file (sha1 prefix `7129f2a9ea` both times). This confirms W15d's count of **seven distinct** values and adds that it is eight occurrences.

### 2. Classification — **5 SEPARABLE, 2 ENTANGLED, 0 NO UNIT PRESENT** — PRIMARY

Every classification below is the output of the rule stated in Method, run as a script.

**V1 — SEPARABLE** (free candidate heads: 1; bound-in-compound: 0)
Qualifier that must survive verbatim:
> `the 29 of 171 who had distant metastases at diagnosis; 27 had lung metastases and two peritoneal dissemination`

*Note, not part of the classification:* the residue contains two content classes, a denominator relation (`29 of 171`) and a **numerator-level site breakdown** (`27 … two …`). A two-field split preserves both only because the free text is retained; a three-way split into (unit, population, breakdown) is not what is on the table and I did not test it.

**V2 — SEPARABLE** (1 free; 0 bound)
> `with metastatic disease in this series`

*Note:* this qualifier is deictic — `in this series` is meaningless outside its containing record. It survives the split verbatim, but it is the weakest of the seven and it carries no distinguishing qualifier of the kind V3/V4 carry.

**V3 — SEPARABLE** (1 free; 0 bound)
> `with distant metastases AT DIAGNOSIS — a presenting cohort, not everyone who ever metastasised`

**V4 — SEPARABLE** (1 free; 0 bound)
> `who DEVELOPED distant metastases during follow-up in a cohort that was LOCALISED at diagnosis — an incidence cohort, not a presenting stratum`

**V5 — ENTANGLED** (1 free; **1 bound**: `171-patient`)
The candidate head occurs twice at two different scopes: once as the head of the counted population, and once bound inside the qualifier phrase `within a 171-patient national-registry series`, where it names a **different and larger** counting than the one the sibling `denominator: 8` records. Deleting a single token is not determinate, and the bound occurrence cannot be lifted without breaking `171-patient national-registry series`. A scalar `denominator_unit` field cannot say which of the two scopes it records.

**V6 — SEPARABLE** (1 free; 0 bound)
> `the 8 of 142 localized at diagnosis who did not undergo surgery; 104 had an R0 resection, 22 R1, 8 R2`

*Note:* like V1, the residue mixes the denominator relation with a breakdown (`104 / 22 / 8`) that belongs to the 142, not to the 8. It separates by the rule; the residue is nonetheless not a single population definition.

**V7 — ENTANGLED** (1 free; **1 bound**: `171-patient`)
Same structure as V5, with `within a 171-patient series`.

**Tally: SEPARABLE 5, ENTANGLED 2, NO UNIT PRESENT 0.**

**An observation for the owners, flagged and not resolved here — UNKNOWN.** V5, V6 and V7 all sit beside `denominator: 8` and all describe patients localized at diagnosis who did not undergo surgery, but V5 and V7 embed a **171**-total series while V6 embeds **8 of 142**. V5 and V6 are in the *same file*. Whether that is two legitimately different framings of one cohort or a discrepancy is a question for the file's owner; I did not resolve it, I make no clinical claim about it, and I computed nothing from it.

### 3. The design question — measured answer

**Fraction of the seven that could carry a `denominator_unit` field today: NONE. 0 of 7.**

Measured, not asserted: scanning all four files for any key matching `/unit/i` at any depth returns **NONE**. The field does not exist in any committed file, no committed writer emits it, and no committed test asserts on it. So the honest answer to "how many could carry a unit field today" is zero — not because the strings resist it, but because the field does not exist. Separately, and this is the useful number: **5 of 7 are structurally ready** to have a unit lifted out without editing the qualifier, and **2 of 7 (V5, V7) would first require their owner to disambiguate which of two nested scopes the unit names.**

**Is a required closed-enum `denominator_unit` beside a retained free-text `denominator_means` "strictly stronger" than `I6`? Not on one axis — the claim needs the axis named, and W15d's phrasing conflates two.**

- **As a refusal filter it is strictly *weaker*.** `I6` refuses any record whose `denominator_means` is not literally an enum token; that is all seven of these, and W15d measured 0 of 6 survivors on lane 15's own store. The two-field guard admits any record that declares a unit while keeping its free text — a strict **superset** of what `I6` admits. So it refuses less.
- **As a retention guarantee it is strictly *stronger*.** It preserves every qualifier `I6` deletes, including the two that `POLICY-evidence` §2.1 depends on (see §4), while still making a declared unit mandatory whenever `denominator_status == "STATED"`.
- **Neither guard verifies that a declared unit is *correct*.** `I6` checks only that a slot holds a token. The two-field version checks only that a second slot holds a token. Both are type checks, not evidence checks. Calling either "stronger" without saying "stronger at what" overstates them, and I will not do that.

The defensible statement is: **the two-field design dominates `I6` on information retention at the cost of admitting more records, and it is the correct shape precisely because `I6`'s extra refusals are achieved by destroying evidence rather than by detecting a defect.**

**Cost, stated concretely.**

1. **It is not lane 15's to make.** The committed key has three committed writers — `research/modalities/emc_care_delivery_evidence.py:246`, `research/modalities/emc_site_curation.py:86,135,230`, `research/modalities/emc_radiotherapy_contradiction.py:234,273` — and a committed test, `research/modalities/tests/test_emc_radiotherapy_contradiction.py:318` (`assert p["denominator"] == 8 and p["denominator_means"]`). Any real schema change touches **their owners, not lane 15 alone.** I did not edit any of the four JSON files, the three writers, or the test.
2. **Populating the new field is blocked on an open question, not on effort.** Filling `denominator_unit` for even one record requires deciding what that record's `n` counts. That is W13b/W13c's question and it is open. So the field would ship required-and-unfillable, or ship with a migration that guesses — and guessing a unit is exactly the fabrication CLAUDE.md §4 forbids.
3. **Two records need upstream work first.** V5 and V7 cannot receive a scalar unit until their owner says which scope it refers to.
4. **`RetainedFact` is not committed code.** Nothing I built enters the tree. I do not propose committing it, and this report proposes no commit.

### 4. Why the qualifiers are load-bearing — the policy tie — SECONDARY (reading of committed policy)

`systems/POLICY-evidence.md` §2.1 condition 3 states, verbatim, that a cohort may be pooled only if *"The outcome is a **true outcome, not the inclusion criterion** — e.g. a 'metastatic at diagnosis' cohort does **not** contribute to the *metastasis* rate (its metastasis count is structurally 100%)."* §2.3 separately forbids pooling a whole-cohort row together with its sub-strata.

V3's surviving qualifier (`a presenting cohort, not everyone who ever metastasised`) and V4's (`an incidence cohort, not a presenting stratum`) are the **only place in these files** where that distinction is written down. They are not commentary; they are the field-level record of the §2.1(3) test result. `I6` as specified overwrites both with an enum token and thereby erases the evidence that the repository's own pooling contract requires before either row may be used. That is the strongest argument for the two-field shape, and it is an argument from committed policy rather than from my preference. It supports **no clinical claim**: I pooled nothing, computed no rate, and produced no estimate.

## Validation evidence

Environment: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux, `python3` as installed, no network used, no third-party packages. Working directory for the scripts `/tmp/claude-0/w15e/`, reading `/home/user/Rare-cancers` @ `7d08121` read-only.

### RUN — read-only confirmation, start and end

```
$ git rev-parse HEAD
7d081218f107363573573e6d102e4334567adf77
$ git status --porcelain | wc -l
0
```
`0` at start and at end. No git write operation of any kind was performed.

### RUN — enumeration (`/tmp/claude-0/w15e/enumerate.py`), `REAL_EXIT=0`

```
TOTAL OCCURRENCES: 8
DISTINCT VALUES: 7

--- V1 (occurrences: 2) len=119 sha1=7129f2a9ea
VALUE: 'the 29 of 171 patients who had distant metastases at diagnosis; 27 had lung metastases and two peritoneal dissemination'
   AT: research/modalities/emc-care-delivery-evidence.json $.absences[0].quotes[0].denominator_means
   SIBLINGS: {"denominator": 29}
   AT: research/modalities/emc-care-delivery-evidence.json $.corpus_quotes[0].denominator_means
   SIBLINGS: {"denominator": 29}

--- V2 (occurrences: 1) len=47 sha1=1d5476e70a
VALUE: 'patients with metastatic disease in this series'
   AT: research/modalities/emc-site-curation.json $.series[0].metastatic.denominator_means
   SIBLINGS: {"denominator": 26}

--- V3 (occurrences: 1) len=103 sha1=c4e1a52cd1
VALUE: 'patients with distant metastases AT DIAGNOSIS — a presenting cohort, not everyone who ever metastasised'
   AT: research/modalities/emc-site-curation.json $.series[1].metastatic.denominator_means
   SIBLINGS: {"denominator": 29}

--- V4 (occurrences: 1) len=150 sha1=036cbabfde
VALUE: 'patients who DEVELOPED distant metastases during follow-up in a cohort that was LOCALISED at diagnosis — an incidence cohort, not a presenting stratum'
   AT: research/modalities/emc-site-curation.json $.series[2].metastatic.denominator_means
   SIBLINGS: {"denominator": 13}

--- V5 (occurrences: 1) len=106 sha1=b027a75f22
VALUE: 'patients localized at diagnosis who did not undergo surgery, within a 171-patient national-registry series'
   AT: research/modalities/emc-radiotherapy-contradiction.json $.carbon_ion.patients_reported.denominator_means
   SIBLINGS: {"denominator": 8}

--- V6 (occurrences: 1) len=110 sha1=8f51924f9d
VALUE: 'the 8 of 142 patients localized at diagnosis who did not undergo surgery; 104 had an R0 resection, 22 R1, 8 R2'
   AT: research/modalities/emc-radiotherapy-contradiction.json $.carbon_ion.quotes[0].denominator_means
   SIBLINGS: {"denominator": 8}

--- V7 (occurrences: 1) len=88 sha1=589ed16f1b
VALUE: 'patients localized at diagnosis who did not undergo surgery, within a 171-patient series'
   AT: research/manuscripts/care-delivery/emc-absence-claims-refuted.json $.refutations[1].counts_now_readable_and_previously_absent.denominator_means
   SIBLINGS: {"denominator": 8}
REAL_EXIT=0
```

### RUN — classification (`/tmp/claude-0/w15e/classify.py`), `REAL_EXIT=0`

```
M1 keys matching /unit/i anywhere in the four files: NONE
M2 distinct values: 7 of 8 occurrences

V1: SEPARABLE
  candidate-head occurrences: free=1 ['patients']  bound-in-compound=0 []
  QUALIFIER THAT MUST SURVIVE VERBATIM: 'the 29 of 171 who had distant metastases at diagnosis; 27 had lung metastases and two peritoneal dissemination'
  denominator siblings: [29, 29]   at: ['$.absences[0].quotes[0].denominator_means', '$.corpus_quotes[0].denominator_means']

V2: SEPARABLE
  candidate-head occurrences: free=1 ['patients']  bound-in-compound=0 []
  QUALIFIER THAT MUST SURVIVE VERBATIM: 'with metastatic disease in this series'
  denominator siblings: [26]   at: ['$.series[0].metastatic.denominator_means']

V3: SEPARABLE
  candidate-head occurrences: free=1 ['patients']  bound-in-compound=0 []
  QUALIFIER THAT MUST SURVIVE VERBATIM: 'with distant metastases AT DIAGNOSIS — a presenting cohort, not everyone who ever metastasised'
  denominator siblings: [29]   at: ['$.series[1].metastatic.denominator_means']

V4: SEPARABLE
  candidate-head occurrences: free=1 ['patients']  bound-in-compound=0 []
  QUALIFIER THAT MUST SURVIVE VERBATIM: 'who DEVELOPED distant metastases during follow-up in a cohort that was LOCALISED at diagnosis — an incidence cohort, not a presenting stratum'
  denominator siblings: [13]   at: ['$.series[2].metastatic.denominator_means']

V5: ENTANGLED
  candidate-head occurrences: free=1 ['patients']  bound-in-compound=1 ['171-patient']
  denominator siblings: [8]   at: ['$.carbon_ion.patients_reported.denominator_means']

V6: SEPARABLE
  candidate-head occurrences: free=1 ['patients']  bound-in-compound=0 []
  QUALIFIER THAT MUST SURVIVE VERBATIM: 'the 8 of 142 localized at diagnosis who did not undergo surgery; 104 had an R0 resection, 22 R1, 8 R2'
  denominator siblings: [8]   at: ['$.carbon_ion.quotes[0].denominator_means']

V7: ENTANGLED
  candidate-head occurrences: free=1 ['patients']  bound-in-compound=1 ['171-patient']
  denominator siblings: [8]   at: ['$.refutations[1].counts_now_readable_and_previously_absent.denominator_means']

M2 TALLY: {'SEPARABLE': 5, 'ENTANGLED': 2}
M3 fraction of the 7 that could carry a denominator_unit field TODAY (key exists in a committed file): 0/7
REAL_EXIT=0
```

### RUN — prior-work and corpus greps

```
$ grep -rn "denominator_unit" . | grep -v '^./.git'
→ 3 hits, all in reports/W15d-i6-invariant-consequences.md (lines 214, 366, 393)
$ grep -rl "denominator_unit" /tmp/claude-0/frozen-corpus/extracted/corpus/ | wc -l
0
$ grep -rl "denominator_means" /tmp/claude-0/frozen-corpus/extracted/corpus/ | wc -l
11
$ grep -n "denominator_means" research/modalities/emc_care_delivery_evidence.py research/modalities/emc_site_curation.py research/modalities/emc_radiotherapy_contradiction.py research/modalities/tests/test_emc_radiotherapy_contradiction.py
research/modalities/emc_care_delivery_evidence.py:246
research/modalities/emc_site_curation.py:86, 135, 230
research/modalities/emc_radiotherapy_contradiction.py:234, 273
research/modalities/tests/test_emc_radiotherapy_contradiction.py:318:    assert p["denominator"] == 8 and p["denominator_means"]
```

### PROPOSED (NOT RUN)

- Adding a `denominator_unit` key to any committed file, writer, or test. **Not done, not proposed for commit.**
- Implementing the two-field guard in `RetainedFact`. Not implemented and not run. `RetainedFact` is not committed code and nothing from this run enters the tree.
- Running `scripts/preflight.sh` or the committed test suites. My dispatch did not authorise it and I changed nothing that would need gating.
- Resolving the 171-vs-142 observation in `emc-radiotherapy-contradiction.json`. Flagged only.

## Limitations

- **The classification is structural, not semantic.** It measures whether a string separates. It does not establish that any extracted token *is* the counting unit, and I have not decided that for a single record. If W13b/W13c conclude that some `n` counts something other than the head noun each string happens to use, a SEPARABLE verdict here does **not** transfer — the string would still separate, but into a different pair.
- **The candidate lexicon is mine and is unvalidated.** A different lexicon would change nothing for V5/V7 (their entanglement is a repeated-token-at-two-scopes property, independent of which lemma) but could in principle move a SEPARABLE verdict if a string names a second countable head my list omits. I did not test alternative lexicons.
- **n = 7.** Five-of-seven is a count over seven strings in four files, all written by the same small group of committed writers. It is not evidence about how a `denominator_means`-style field behaves in general, and I make no such general claim.
- **This is bookkeeping, not science.** No clinical claim, no rate, no pooled estimate, no denominator derived from a percentage, no unit determination. Nothing here bears on EMC efficacy, safety, selectivity or clinical readiness, and no computational result could.
- **HEAD drift.** I read `7d08121`, not the `92abbcb` the brief names. If the coordinator needs the classification pinned to `92abbcb`, it must be re-run there; I did not check out any other commit (no git writes permitted).
- **Corpus absence is UNKNOWN, not proof.** `denominator_unit` is absent from the selected frozen corpus, which `snapshot-provenance.json` states is not a complete repository and whose `absent_files` are explicitly unknown.
- **Two records are blocked upstream.** V5 and V7 cannot be assigned a scalar unit until their file's owner disambiguates the nested scope; that is not lane 15's call.
- No network was used. No refusal was encountered.

## Stop condition

Set: all seven values enumerated with file and JSON path; each classified SEPARABLE / ENTANGLED / NO UNIT PRESENT with the surviving qualifier quoted where a split is possible; the two-field design costed with a measured count.

**MET.** Seven distinct values across four tracked files enumerated with exact JSON paths and sibling denominators (8 occurrences, V1 duplicated byte-identically). Classification run mechanically from a rule stated in advance: **5 SEPARABLE, 2 ENTANGLED, 0 NO UNIT PRESENT**, at `REAL_EXIT=0`, with the surviving qualifier quoted verbatim for all five separable values. The design question is answered with the axis named — the two-field guard is strictly stronger on retention and strictly weaker as a refusal filter, and neither guard verifies a unit is correct — and the measured count of the seven that could carry a unit field today is **NONE, 0 of 7**, because the key exists in no committed file, writer or test. Ownership stated: any real schema change touches the three committed writers and the committed test, not lane 15 alone. Working tree unmodified throughout.

## Tool-call and wall-clock count actually used

**7 tool calls** (all `Bash`; several batched two independent commands per call). **Wall clock 02:35:17Z → 02:37:51Z = 2 min 34 s.** Well inside the ~40-call / ~40-minute self-observed target. Returned as soon as the stop condition was met; no padding.

## Next concrete action

**Route the two ENTANGLED records to the owner of `research/modalities/emc-radiotherapy-contradiction.json` and `research/manuscripts/care-delivery/emc-absence-claims-refuted.json` as a single scope question — not as a schema proposal.** V5 and V7 each name two nested countings in one string (the recorded `denominator: 8`, and a `171-patient` series inside the qualifier), and V6 in the same file as V5 embeds `8 of 142` instead of 171. Before any `denominator_unit` field could be specified, that owner must state which scope the record's `n` belongs to and whether 171-vs-142 is two framings or a discrepancy. This is a question about committed evidence, it needs no network, and it is answerable without assigning any unit.

**Explicitly not mine and stated so it is not dropped:** the schema change itself is blocked on W13b/W13c's open question of what these `n`s count — a required `denominator_unit` cannot be populated for any of the seven today without guessing a unit, which CLAUDE.md §4 forbids. Lane 15 should not specify that field further until W13b/W13c report. There is a viable successor above; there is no viable successor *inside lane 15* for the schema work itself, because lane 15 owns neither the writers, the test, nor the unit determination.
