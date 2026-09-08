> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

## Worker

**W15d**, lane 15 refill — data ingestion / normalisation / evidence retention. Successor to W15c, testing W15c's proposed `I6` against W15's own five adapters.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) from my own system context. No environment variable in this container names a served model. The coordinator must extract the actual per-child runtime model from the transcript; I do not assert it as observed fact.

`date -u` at start: `Tue Sep  8 02:25:54 UTC 2026`. At end: `Tue Sep  8 02:28:33 UTC 2026`.

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

**HEAD actually read: `b9a0257e6acff53ad22535cf2adf261313e0b250`** — not the frozen `92abbcb…` named in the brief; the coordinator has committed worker reports since. I verified all five files my run reads are byte-identical between the two commits (evidence below), so W15's baseline is legitimately comparable. Tree at end: `git status --porcelain` non-untracked lines = only ` M research/autonomy/opus-capacity-campaign-20260908/WAVE-LOG.md`, which was already modified at my start and is the coordinator's, not mine. I wrote nothing in the repository; all execution in `/tmp/claude-0/w15d/`. No network, no paid API, no GPU, no git write. No content-policy refusal in this lane.

## Question

**If `I6` is added to `RetainedFact`, how many of W15's own five adapters' currently-STATED denominators survive it — and if the store thereby loses its only computable rates, is that information or a reason the field should stay optional?**

Open because W15c measured `I6`'s effect on the *clinical registry* (17 lossless records → 0) but explicitly did not measure it on the module's own store, and named exactly that as the risk the successor must report honestly.

## Prior-work check

Commands run against the tracked corpus, with what they showed:

```
$ git ls-files | rg -i "retained_fact|retained-fact"
(no output)
```
`RetainedFact` remains uncommitted — it exists only inside W15/W15b/W15c report prose. Nothing I build enters the tree.

```
$ rg -l "I6" research/autonomy/opus-capacity-campaign-20260908/reports/
research/autonomy/opus-capacity-campaign-20260908/reports/W15c-retainedfact-registry-composition.md
```
`I6` is named only by W15c, as a proposal, `PROPOSED (NOT RUN)` against W15's adapters. Not previously executed.

```
$ rg -l -i "denominator_means" --glob '!.git'
systems/tests/test_autonomy_health.py
research/manuscripts/care-delivery/emc-absence-claims-refuted.json
research/autonomy/sprint-2026-09-01/S18-FALSE-ABSENCES.md
research/modalities/emc-care-delivery-evidence.json
research/modalities/emc-site-curation.json
research/modalities/emc-radiotherapy-contradiction.json
research/modalities/emc_care_delivery_evidence.py
research/autonomy/autonomy-state.json
research/autonomy/opus-capacity-campaign-20260908/reports/W15b-…  W15-…  W15c-…
research/modalities/emc_site_curation.py
research/modalities/tests/test_emc_radiotherapy_contradiction.py
research/modalities/emc_radiotherapy_contradiction.py
```

**This contradicts W15c.** W15c's prior-work section states that `denominator_means` "appears **only** in W15's report". It does not: it is a **committed key in four tracked JSON files**, with committed Python that writes it and a committed test that asserts on it. W15c's conclusion (the field is optional and unread *by `RetainedFact`*) is still correct, but its premise that the concept is novel to lane 15 is wrong, and that error is load-bearing for `I6` — see Result §4. This is the discrepancy I was told to treat as a first-class finding.

```
$ rg -c "denominator_means" research/data/emc-clinical-registry.json   # exit 1, no matches
```
The registry has no such key, consistent with W15c.

I read `CLOSED-WORK.md` in full. I am not replaying: PUB-EMC-CLASSIFICATION, the registry ICD-O paper (user-rejected), any Brenca route, any unrecovered-source route (I fetched nothing, changed or unchanged), lane 11's source-index, or the frozen external-validation comment. I checked sibling W15b's headline to avoid duplicating it: it measured *how many* FT_QUOTE-tier facts exist (70, vs W15's baseline 1); I measure what `I6` does to the STATED denominators. Different question, no overlap.

## Method / inputs

Read-only on the tree. Python 3.11.15, Linux 6.18.44-fc-v24, stdlib only, no network, cwd `/tmp/claude-0/w15d/pkg`.

**Reconstruction.** I did not retype W15's module. I extracted the two fenced `python` blocks from `reports/W15-ingestion-normalisation-retention.md` programmatically, so the module and its test suite are byte-for-byte what W15 reported: 397 lines, `md5 a72db49b6f495c22041d726a68ba94fb`, and 142 lines, `md5 94bf84573bd987a89bd46a5d943271d2`. Vocabularies, `RetentionError`, `_norm_id`, `_kind_of`, `__post_init__` and `rate` are unmodified; **no invariant weakened, removed or reordered.**

Inputs the five adapters read (all read-only, all verified unchanged between `92abbcb` and `b9a0257`):

| Adapter | File |
|---|---|
| `from_corpus_quotes` | `research/modalities/emc-care-delivery-evidence.json` |
| `from_care_delivery_findings` | `research/modalities/emc-care-delivery-evidence.json` |
| `from_trabectedin_series` | `research/literature/emc-trabectedin-denominator-2026-09-01.json` |
| `from_ledger` | `research/manuscripts/citation-provenance-ledger.json` |
| `from_fetch_records` | `research/literature/arxiv-aso-route.json`, `research/literature/venue-fee-pages-2026-08-24.json` |

**How `I6` was applied.** In a separate file (`i6.py`) that imports the unmodified module, captures `_ORIGINAL_POST_INIT = rf.RetainedFact.__post_init__`, and installs a wrapper whose **first statement calls the original in full**, then adds the new check. Purely additive; I1–I5 still fire, in their original order.

```python
DENOMINATOR_UNITS = ("patient", "tumour", "specimen", "biosample", "sequencing_run")
_ORIGINAL_POST_INIT = rf.RetainedFact.__post_init__

def _post_init_with_i6(self):
    _ORIGINAL_POST_INIT(self)                      # original invariants first, unchanged
    if self.denominator_status == "STATED" and self.denominator_means not in DENOMINATOR_UNITS:
        raise rf.RetentionError(
            f"I6: STATED denominator requires a declared unit from {DENOMINATOR_UNITS}; "
            f"denominator_means={self.denominator_means!r}")
```

The enum is W15c's, transcribed verbatim. **It is a placeholder for a determination I do not make**: what any `n` counts is W13b's live question.

**Unit of analysis.** Records are fed to each adapter **one at a time** (`fn({key: [item]}, rel)`) so a refusal does not abort the rest of that adapter's input, giving a per-record survivor count rather than a first-failure abort.

Scratch files: `/tmp/claude-0/w15d/pkg/{retained_facts.py, test_retained_facts.py, i6.py, run_i6.py, ingest_i6_cli.py, run_tests_i6.py}`.

## Result

### 1. W15's own tallies reproduced exactly — no discrepancy

`summarise()` over the real committed inputs returned, field for field, W15's reported numbers: `n_records 277`, `n_distinct_sources 274`, tiers `{FT_QUOTE 1, ABSTRACT 6, METADATA 33, UNCORROBORATED 237}`, denominators `{STATED 6, UNKNOWN 1, NOT_APPLICABLE 270}`, access `{FULL_TEXT 18, ABSTRACT_ONLY 6, METADATA_ONLY 237, UNRECOVERED_403 5, UNRECOVERED_OTHER 11}`, `n_with_computable_rate 2`. The trabectedin subject query returned the same two unpooled rows (den 2 and 3, numerator 0). W15's 17 tests still pass at exit 0. **No discrepancy in W15's tallies.** (The discrepancy I did find is in W15c's prior-work check, §4.)

### 2. The six STATED denominators, per adapter and per record — PRIMARY

| # | Adapter | record_id | source | den | `denominator_means` as populated | source key it came from |
|---|---|---|---|---|---|---|
| 1 | `from_corpus_quotes` | `CQ-masunaga2025-0` | PMID 40885991 | 29 | `"the 29 of 171 patients who had distant metastases at diagnosis; 27 had lung metastases and two peritoneal dissemination"` | **committed `denominator_means`** |
| 2 | `from_care_delivery_findings` | `FIND-surgery-is-the-lever` | PMID 32856598 | 439 | `"SEER 1973-2016, n=439 (373 locoregional)"` | `design` |
| 3 | `from_care_delivery_findings` | `FIND-the-disease-outruns-its-follow-up` | PMID 32572850 | 67 | `"Italian Sarcoma Group, 3 referral centres, n=67 localised, NR4A3-rearrangement confirmed, centrally reviewed to WHO 2013, median follow-up 55 months"` | `design` |
| 4 | `from_care_delivery_findings` | `FIND-single-centre-surgical-series` | PMID 36326382 | 13 | `"single reference centre, n=13, 2006-2018"` | `design` |
| 5 | `from_trabectedin_series` | `TRAB-morioka2016` | PMID 27418251 | 2 | `"5 subjects allocated to trabectedin: 2 EMC + 3 mesenchymal chondrosarcoma"` | `arm_composition` |
| 6 | `from_trabectedin_series` | `TRAB-palmerini2022` | PMID 36568164 | 3 | `"36 patients with ultra-rare or other rare translocation-related sarcoma; 35 evaluable for response; EMC n=3"` | `arm_composition` |

`from_ledger` (237 records) and `from_fetch_records` (33 records) hard-code `denominator_status="NOT_APPLICABLE"` and `denominator_means=None`; neither can ever produce a STATED denominator, so neither is touched by `I6`.

**Only record 1 reads a committed `denominator_means` key.** In the other five, W15's adapter code fills the field with a *study-design* string (`design`) or an *arm-composition* string (`arm_composition`). Those files carry no `denominator_means` key at all (verified: `'denominator_means' in f` is `False` for all four `findings` and both `series`). So five of the six values in the field are a category error introduced by the adapter, not data the tree committed.

### 3. Survivors under `I6`: **0 of 6** — PRIMARY

| Adapter | CONSTRUCTED base | CONSTRUCTED with I6 | REFUSED by I6 | STATED denominators surviving |
|---|---|---|---|---|
| `from_corpus_quotes` | 1 | 0 | 1 | **0 of 1** |
| `from_care_delivery_findings` | 4 | 1 | 3 | **0 of 3** |
| `from_trabectedin_series` | 2 | 0 | 2 | **0 of 2** |
| `from_ledger` | 237 | 237 | 0 | 0 of 0 (n/a) |
| `from_fetch_records` | 33 | 33 | 0 | 0 of 0 (n/a) |
| **TOTAL** | **277** | **271** | **6** | **0 of 6** |
| records with a computable `rate` | **2** | **0** | — | — |

Every one of W15's six STATED denominators is refused. The store's only two computable rates — `TRAB-morioka2016` 0/2 and `TRAB-palmerini2022` 0/3, both zero-numerator — are both lost. Under `I6`, `RetainedFact` can compute no rate from anything this repository has retained.

The whole-pipeline CLI no longer completes: it aborts on the first STATED record with `RetentionError` at **exit 1**. W15's own 17 tests, unmodified, drop to **12 run, 3 errors, exit 1** — `test_stated_denominator_does_divide`, `test_zero_denominator_does_not_divide`, and `setUpClass` of `AdaptersReadTheRealCommittedFiles` (which collapses that class's 5 tests). Those are not spurious: they are the suite correctly reporting that the module's ability to divide is gone.

### 4. What the closed enum would have to contain — and why it cannot be a unit enum

I scanned each of the six strings for a unit noun (`patient(s)`, `tumour(s)`, `specimen(s)`, `biosample(s)`, `sequencing run`, `case(s)`, `subject(s)`, `sample(s)`), and printed the ±25/35-character context around the number actually recorded as the denominator:

| record | den | unit noun anywhere in string | context around that number |
|---|---|---|---|
| `CQ-masunaga2025-0` | 29 | `patients` | `the 29 of 171 patients who had distant me` |
| `FIND-surgery-is-the-lever` | 439 | **NONE** | `seer 1973-2016, n=439 (373 locoregional)` |
| `FIND-the-disease-outruns-its-follow-up` | 67 | **NONE** | `3 referral centres, n=67 localised, NR4A3-…` |
| `FIND-single-centre-surgical-series` | 13 | **NONE** | `single reference centre, n=13, 2006-2018` |
| `TRAB-morioka2016` | 2 | `subjects` | `llocated to trabectedin: 2 emc + 3 mesenchymal…` (the noun `subjects` attaches to **5**, not to 2) |
| `TRAB-palmerini2022` | 3 | `patients` | `able for response; emc n=3` (the noun `patients` attaches to **36**; a third number, 35, is "evaluable") |

**Three of six name no counting unit at all** — `n=439`, `n=67`, `n=13` are bare. In all three the correct answer is **UNKNOWN**; I make no guess, and I note that a SEER `n` and a referral-centre `n` need not count the same kind of object. In the other three a unit noun is present but is **attached to a different number than the one recorded as the denominator** (171 not 29; 5 not 2; 36 not 3). So on the committed data the unit of the denominator is undeclared in **6 of 6** cases. What the enum "would have to contain" is not determinable from these strings, and I decline to derive it.

The deeper problem, from the corpus-wide grep: the repository's seven distinct committed `denominator_means` values, across four tracked files, are all of this shape —

```
'patients localized at diagnosis who did not undergo surgery, within a 171-patient series'
'patients who DEVELOPED distant metastases during follow-up in a cohort that was LOCALISED
   at diagnosis — an incidence cohort, not a presenting stratum'
'patients with distant metastases AT DIAGNOSIS — a presenting cohort, not everyone who ever
   metastasised'
'the 8 of 142 patients localized at diagnosis who did not undergo surgery; 104 had an R0
   resection, 22 R1, 8 R2'
```

Every one says `patients`; none of them is *about* the word `patients`. The field as the repository actually uses it is a **population definition**, not a counting unit, and its whole value is the qualifier — "an incidence cohort, not a presenting stratum" is precisely the distinction that stops two rows being compared. Collapsing that field to a five-token enum would satisfy `I6` and **delete the information the field exists to carry**. `I6` as W15c specified it is therefore the wrong shape, not merely expensive: it strengthens the guard by destroying the evidence. The correct shape is two fields — a new required `denominator_unit` from a closed enum when `denominator_status == "STATED"`, and `denominator_means` retained as free text — which is still strictly a strengthening. That is a design correction I hand on; I did not implement it, and it does not change the measured answer, because a `denominator_unit` field does not exist in any committed file either, so its survivor count today is also **0 of 6**.

### 5. The honest answer to W15c's question

Plainly: **the survivors are none.** Zero of six. Adding `I6` takes lane 15's store from two computable rates to zero, breaks its CLI at exit 1, and breaks 3 of its own 17 tests. Combined with W15c's registry result (17 lossless records → 0), a `RetainedFact` that requires a declared denominator unit currently admits **no fully-typed quantitative record anywhere in this repository**.

**Is that information, or a reason the field should stay optional? It is information, and it is not a reason to make the field optional.** The argument, stated so it can be attacked:

- The two "lost" rates are `0/2` and `0/3`. Their scientific content is *no located objective response among a handful of EMC patients in two trial arms*, which is already, and correctly, recorded in the source artifact with `pooled: false`. Losing the division loses nothing a reader had. It is not plausible that this repository's quantitative capability rests on a rate computed over a denominator of 2.
- The reason those two divisions are licensed today is that `denominator_status == "STATED"` and the number is non-zero. But "the source printed a number" and "we know what the number counts" are different facts, and `RetainedFact` currently conflates them. `TRAB-palmerini2022` is the case in point: the string beside `den=3` also contains 36 and 35, and the response denominator in that trial is stated as 35 *evaluable*, not 36 *patients*. A schema that will divide by 3 without asking which of those three numbers is the population is not preserving a rate; it is preserving the appearance of one.
- Making the field optional to keep the two rates would be exactly the move the brief forbids: weakening a guard so a failure disappears. It would also restore a schema that W15c measured as catching **0 of W13's 12 findings** — the one field that could have caught them being the one left unread.
- The cost is real and I will not minimise it: with `I6`, `rate` becomes dead code on every currently committed input, and a lane that wants a rate has to first get someone to declare a unit. **That cost is acceptable.** The blocker it exposes is a genuine evidence blocker, not a tooling one: nobody has recorded what these `n`s count. A store that says "0 computable rates, because no denominator declares its unit" is a true statement about this evidence base. A store that says "2 computable rates" is a false one, and its falseness is precisely of the kind CLAUDE.md §4 and `POLICY-evidence` exist to prevent.
- The honest caveat: this argument is cheap **because n=2 rates**. If the store held hundreds of rates over well-characterised cohorts, "refuse everything until a unit is declared" would be a much harder call and I would not resolve it this confidently from a refusal count. I am not claiming a general principle; I am reporting that in *this* store, at *this* size, the cost of `I6` is two divisions by 2 and 3 that nobody should have been doing.

I make no clinical claim, no rate, no pooled estimate and **no unit determination**. Whether the unit is patients, tumours or something else is W13b's live question and this run does not answer it.

## Validation evidence

Environment for every `RUN` below: Python 3.11.15, Linux 6.18.44-fc-v24 x86_64, stdlib only, **no network**, cwd `/tmp/claude-0/w15d/pkg`, repository read-only at `b9a0257e6acff53ad22535cf2adf261313e0b250`.

### RUN — inputs unchanged since the frozen commit

```
$ git diff --stat 92abbcb905cacf07f14b238db50d1b98f6590374 HEAD -- \
    research/modalities/emc-care-delivery-evidence.json \
    research/literature/emc-trabectedin-denominator-2026-09-01.json \
    research/manuscripts/citation-provenance-ledger.json \
    research/literature/arxiv-aso-route.json \
    research/literature/venue-fee-pages-2026-08-24.json
INPUT_DIFF_EXIT=0        # empty diff — all five inputs identical to the frozen commit
```

### RUN — verbatim reconstruction

```
$ python3 (extract fenced python blocks from W15's report)
n python blocks: 2
0 397 #!/usr/bin/env python3 | """One normalised structure for every literature fact this r
1 142 #!/usr/bin/env python3 | """Behaviour tests for retained_facts.
EXTRACT_EXIT=0
a72db49b6f495c22041d726a68ba94fb  /tmp/claude-0/w15d/pkg/retained_facts.py
94bf84573bd987a89bd46a5d943271d2  /tmp/claude-0/w15d/pkg/test_retained_facts.py
```

### RUN — W15's baseline reproduced

```
$ python3 retained_facts.py --root /home/user/Rare-cancers \
    --fetch-file research/literature/arxiv-aso-route.json \
    --fetch-file research/literature/venue-fee-pages-2026-08-24.json
{
 "n_records": 277,
 "n_distinct_sources": 274,
 "by_provenance_tier": {"FT_QUOTE": 1, "ABSTRACT": 6, "METADATA": 33, "UNCORROBORATED": 237},
 "by_denominator_status": {"STATED": 6, "UNKNOWN": 1, "NOT_APPLICABLE": 270},
 "by_access_status": {"FULL_TEXT": 18, "ABSTRACT_ONLY": 6, "METADATA_ONLY": 237,
                      "UNRECOVERED_403": 5, "UNRECOVERED_OTHER": 11},
 "n_with_computable_rate": 2
}
REAL_EXIT=0

$ python3 retained_facts.py --root /home/user/Rare-cancers --subject trabectedin --json | …
ABSTRACT | 27418251 | num 0.0 | den 2.0 STATED | 0 objective response(s) among 2 located EMC patients…
ABSTRACT | 36568164 | num 0.0 | den 3.0 STATED | 0 objective response(s) among 3 located EMC patients…
REAL_EXIT=0
```

Identical to every figure W15 reported.

### RUN — `I6` applied as a strengthening, all five adapters re-run per record

```
$ python3 run_i6.py
--- BASE (W15's invariants, unmodified)
adapter                         CONSTRUCTED  REFUSED  STATED denom
from_corpus_quotes                        1        0             1
from_care_delivery_findings               4        0             3
from_trabectedin_series                   2        0             2
from_ledger                             237        0             0
from_fetch_records                       33        0             0
TOTAL                                   277        0             6
records with a computable rate: 2

--- WITH I6 (strengthening; original __post_init__ called first)
adapter                         CONSTRUCTED  REFUSED  STATED denom
from_corpus_quotes                        0        1             0
from_care_delivery_findings               1        3             0
from_trabectedin_series                   0        2             0
from_ledger                             237        0             0
from_fetch_records                       33        0             0
TOTAL                                   271        6             0
records with a computable rate: 0

REFUSALS INTRODUCED BY I6 (per record, verbatim message)
  from_corpus_quotes corpus_quotes[0]
      I6: STATED denominator requires a declared unit from ('patient', 'tumour', 'specimen',
      'biosample', 'sequencing_run'); denominator_means='the 29 of 171 patients who had distant
      metastases at diagnosis; 27 had lung metastases and two peritoneal dissemination'
  from_care_delivery_findings findings[0]
      … denominator_means='SEER 1973-2016, n=439 (373 locoregional)'
  from_care_delivery_findings findings[2]
      … denominator_means='Italian Sarcoma Group, 3 referral centres, n=67 localised, …'
  from_care_delivery_findings findings[3]
      … denominator_means='single reference centre, n=13, 2006-2018'
  from_trabectedin_series series[0]
      … denominator_means='5 subjects allocated to trabectedin: 2 EMC + 3 mesenchymal chondrosarcoma'
  from_trabectedin_series series[1]
      … denominator_means='36 patients with ultra-rare or other rare translocation-related sarcoma;
      35 evaluable for response; EMC n=3'

SURVIVORS: STATED denominators that carry a declarable unit
  count = 0

computable rates: base=2  with I6=0
REAL_EXIT=0
```

(Exit 0 by design: `run_i6.py` is an inventory that catches `RetentionError` per record. The survivor count is the product.)

### RUN — the pipeline and W15's own suite under `I6`

```
$ python3 ingest_i6_cli.py --root /home/user/Rare-cancers --fetch-file … --fetch-file …
  File "/tmp/claude-0/w15d/pkg/retained_facts.py", line 180, in from_corpus_quotes
    out.append(RetainedFact(
  File "/tmp/claude-0/w15d/pkg/i6.py", line 21, in _post_init_with_i6
    raise rf.RetentionError(
retained_facts.RetentionError: I6: STATED denominator requires a declared unit from
('patient','tumour','specimen','biosample','sequencing_run'); denominator_means='the 29 of 171 …'
REAL_EXIT=1

$ RARE_CANCERS_ROOT=/home/user/Rare-cancers python3 run_tests_i6.py
ERROR: setUpClass (test_retained_facts.AdaptersReadTheRealCommittedFiles)
ERROR: test_stated_denominator_does_divide (…MissingDenominatorIsNeverZero…)
ERROR: test_zero_denominator_does_not_divide (…MissingDenominatorIsNeverZero…)
Ran 12 tests in 0.002s
FAILED (errors=3)
REAL_EXIT=1

# control, same suite, no I6:
$ RARE_CANCERS_ROOT=/home/user/Rare-cancers python3 -m unittest test_retained_facts
Ran 17 tests in 0.007s
OK
REAL_EXIT=0
```

### RUN — committed-field inspection and unit-noun scan

Outputs are transcribed in Result §2 and §4 (`'denominator_means' in f` → `False` for all four `findings` and both `series`; the ±context strings around each recorded denominator; the seven distinct committed `denominator_means` values across four tracked files). `REAL_EXIT=0` on both.

### PROPOSED (NOT RUN)

- Splitting the guard into a required closed-enum `denominator_unit` plus the retained free-text `denominator_means` (Result §4). Not implemented, not run.
- Committing `RetainedFact` or `I6` anywhere in the tree. Not done — the module is not committed code.
- `scripts/preflight.sh`. The brief forbids running it here.
- Any edit to `research/data/emc-clinical-registry.json`, and any proposal of one. Not done; A1/A2 belong to its owner and to W13b.

## Limitations

- **The enum is not mine and is not validated.** `('patient','tumour','specimen','biosample','sequencing_run')` is W15c's proposal transcribed. A different enum would change nothing here — three of six strings name no unit noun at all, and the other three attach one to a different number — but I have not tested alternatives, and the 0/6 result is conditional on `I6` reading `denominator_means` as a unit field, which §4 argues it should not.
- **I determine no cohort unit.** Where the committed data does not declare what an `n` counts, my answer is UNKNOWN. W13b owns that question.
- **The unit-noun scan is a token search, not comprehension.** It shows which nouns appear and where, not what the authors meant. It cannot license a unit assignment and I draw none from it.
- **`n=6`.** The whole quantitative result rests on six records and two rates. The cost argument in Result §5 is correspondingly narrow and I say so there; it is not a general rule about schema strictness.
- **Read-only and uncommitted.** `RetainedFact` is not in the tree, so none of this is a change to the repository — it is a measurement of a proposal. Nothing here can be relied on as a passing gate on committed code.
- **No clinical content.** This establishes nothing about EMC efficacy, safety, selectivity or readiness. It creates no patient, no cohort and no denominator. A refusal count is bookkeeping, not science.
- I did not read `systems/POLICY-evidence.md` because I neither read nor touched the clinical registry in this run; the requirement attaches to editing it, which I did not do.

## Stop condition

Set: W15's tallies reproduced or a discrepancy diagnosed; `I6` applied as a strengthening and all five adapters re-run with a real command and exit code; a per-adapter survivor count; an explicit argued answer to the cost question.

**MET.** All of W15's reported figures reproduced exactly from a byte-verbatim reconstruction (no discrepancy in W15's tallies; a separate discrepancy diagnosed in W15c's prior-work claim about `denominator_means`). `I6` applied purely additively, original `__post_init__` called first, all five adapters re-run per record at `REAL_EXIT=0` for the inventory and `REAL_EXIT=1` for the pipeline and the suite. Per-adapter survivors: 0/1, 0/3, 0/2, n/a, n/a — **0 of 6 overall**, 2 computable rates → 0. Cost question answered explicitly: the loss is information, the cost is acceptable at this size, and the field must not be made optional again.

## Tool-call and wall-clock count actually used

12 tool calls (target ~40). Wall clock `02:25:54Z → 02:28:33Z` ≈ **3 minutes** (target ~40). Returning on the stop condition; no padding.

## Next concrete action

**Lane 15: re-specify the guard as `denominator_unit` (required closed enum when `denominator_status == "STATED"`) *beside* the retained free-text `denominator_means`, and measure how many of the seven distinct committed `denominator_means` values in the four tracked modality files could be split into (unit, population-definition) without losing a qualifier.** That is the concrete follow-up this run's §4 produced: `I6` as specified would satisfy the invariant by deleting the "incidence cohort, not a presenting stratum" distinction, which is the opposite of retention. The measurement is over four committed files, needs no network, and — critically — it can be done **without assigning any unit**, by asking only whether the string separates cleanly, and routing the units themselves to W13b.

Not mine, and stated so it is not dropped: the committed `denominator_means` key already has writers (`emc_care_delivery_evidence.py`, `emc_site_curation.py`, `emc_radiotherapy_contradiction.py`) and a committed test (`research/modalities/tests/test_emc_radiotherapy_contradiction.py`); any real schema change touches their owners, not lane 15 alone.
