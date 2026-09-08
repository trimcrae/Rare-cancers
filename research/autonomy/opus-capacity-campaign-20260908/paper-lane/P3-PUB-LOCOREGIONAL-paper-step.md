<!-- collected 2026-09-08T05:15:26Z by campaign coordinator; agent id af3c82da073f16318; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-af3c82da073f16318.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Scratch deleted, tree clean, nothing written to the repository.

---

## Worker

**P3**, PAPER lane, campaign OPUS-CAPACITY-CAMPAIGN-20260908. Candidate: **PUB-LOCOREGIONAL**.

Model: **SELF-REPORT, NOT INDEPENDENTLY VERIFIED** — Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the runtime model from the transcript.

Start `date -u`: `Tue Sep  8 05:09:15 UTC 2026` · HEAD `0d05cb7b3bf27921cceeb76bd69873ed89eb9fd6` · `git status --porcelain` **empty**.
End `date -u`: `Tue Sep  8 05:11:31 UTC 2026` · HEAD `997bc9e769da6bf606392941d46d20b319beab85` (advanced under me — coordinator commits, campaign directory only) · `git status --porcelain` **empty**.

Literal output of the model-evidence command (secrets redacted):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
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
GLOBAL_AGENT_NO_PROXY=...(same list)
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=...(proxy/truststore only)
NO_PROXY=...(same list)
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=...(same list)
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

W25/GSE243553 was not read, referenced or depended on. No network retrieval, no paid API, no GPU. No content-policy refusal occurred. `emc_locoregional_eligibility.py` was **not executed** — it has no `--check` path at all (`main()` unconditionally writes `OUT`, `:255-257`), so I reimplemented its pooling in scratch instead.

---

## Question

Can PUB-LOCOREGIONAL's Results section be written now — and specifically, is its record's central verdict (*"the paper has its denominator and not its numerator"*) still true at this HEAD?

Open because the record is `outlined`, blocked on `BLK-NO-EMC-DATA`, and no manuscript file exists for it anywhere in the tree.

---

## Prior-work check

Commands run (campaign directory excluded per the brief):

- `rg -l -i "locoregional" --glob '!.git' --glob '!research/autonomy/opus-capacity-campaign-20260908/**'` — 60+ hits; the substantive ones are `research/modalities/emc_locoregional_eligibility.py`, `research/modalities/emc-locoregional-eligibility.json`, `research/modalities/emc-site-curation.json`, `research/manuscripts/care-delivery/emc-care-delivery-endpoint-decision.md`, `research/manuscripts/care-delivery/emc-oligometastatic-rt-concept.md`, and the generated `systems/views/L1-st-locoregional.md` / `L2-rt-*`.
- `git ls-files | rg -i "locoregional|perfusion|oligomet"` — 7 files. **No manuscript `.md` for PUB-LOCOREGIONAL exists.** The nearest tracked prose are two care-delivery memos, both scoped to other routes.
- `rg -n "36\.3%|27\.0%|94/259|88/326" …` — the metastasis headline is quoted in exactly one manuscript, `research/manuscripts/aso/fusion-junction-aso-working-record.md:1318`, as background. The recurrence headline is quoted in no manuscript.
- `rg -n "71\.6|84\.5" …` — **zero hits in any manuscript or JSON**; the extremity fractions exist only inside `emc-site-curation.json`. This paper's strongest number has never been written into prose.

`CLOSED-WORK.md` checked. Closed items I am **not** replaying: the RT/IPD synthesis and clinical conditional-recurrence checkpoints (different endpoints), the rejected ICD-O classification paper, the NR4A Perspective refusal, and the seven unreachable series (meisKindblom1999, ussc2022, japan2003, china2016, uMich2023, seer270_2022, and the remiszewski2025 review-laundering ban). `emc-care-delivery-endpoint-decision.md` already ruled `RT-METASTASECTOMY`'s note **DO NOT WRITE** and `RT-RT-INTENSIFY` **REFUTED**; my draft does not re-open either.

Campaign findings taken as given, not re-derived: `pool()` does not integer-check `events` (W53/W60); W68's finding that `meta-analysis.md` is the only document printing the three DL headline pools and that `emc-locoregional-eligibility.json` correctly names crude+Wilson and the pooler it did not use.

---

## Method and inputs

Read-only. All computation in `/tmp/claude-0/p3/` (now deleted).

| input | role |
|---|---|
| `systems/graph/publications.json` → `PUB-LOCOREGIONAL` | the record, read in full |
| `research/data/emc-clinical-registry.json` → `registry.cohorts` (14), `registry.patients` (4), `registry.fields` | pooling input; schema inspection |
| `research/modalities/emc_locoregional_eligibility.py` (271 lines) | source read for `pool()`, `wilson()`, `QUANTITIES`; **not executed** |
| `research/modalities/emc-locoregional-eligibility.json` | committed artifact, compared against my reimplementation |
| `research/modalities/emc-site-curation.json` (27,388 B) | site/metastatic-site/local-therapy counts |
| `research/modalities/emc-recurrence-timing.json` | timing statistics |
| `systems/POLICY-evidence.md` §2.1–§2.7 | binding pooling contract, §2.5 quoted verbatim below |
| `research/manuscripts/care-delivery/emc-care-delivery-endpoint-decision.md` | prior decisions on adjacent routes |

Tools: `python3` (stdlib `json`, `math`), `rg`, `git` read-only. My Wilson reimplementation is byte-for-byte the same closed form as `emc_locoregional_eligibility.py:141-149` with `z = 1.959963984540054`.

---

## Eligibility verification (claim-by-claim table)

### A. The sized problem — reproduced independently

`who_ever_metastasises`, from `research/data/emc-clinical-registry.json#registry.cohorts[*].metastasis.{events,denom}`:

| cohort label (`.label`) | `sourceId` | `populationKey` | events/denom | % |
|---|---|---|---|---|
| Localised at diagnosis, surgically treated | `masunaga2025` | `masunaga2025-jpreg` | 39/134 | 29.1 |
| Long-term outcome series (Meis-Kindblom) | `meisKindblom1999` | `meisKindblom1999` | 35/76 | 46.1 |
| European two-institution series (Chiusole) | `chiusole2020` | `chiusole2020` | 20/49 | 40.8 |
| **pooled, k = 3** | | | **94/259** | **36.3%** (Wilson 95% CI **30.7–42.3**), range **29.1–46.1** |

`who_recurs_locally`, from `…cohorts[*].recurrence.{events,denom}`:

| cohort label | `sourceId` | `populationKey` | events/denom | % |
|---|---|---|---|---|
| Localised at diagnosis, surgically treated | `masunaga2025` | `masunaga2025-jpreg` | 16/134 | 11.9 |
| Long-term outcome series (Meis-Kindblom) | `meisKindblom1999` | `meisKindblom1999` | 40/83 | 48.2 |
| US Sarcoma Collaborative database | `ussc2022` | `ussc2022` | 18/60 | 30.0 |
| European two-institution series (Chiusole) | `chiusole2020` | `chiusole2020` | 14/49 | 28.6 |
| **pooled, k = 4** | | | **88/326** | **27.0%** (Wilson 95% CI **22.5–32.1**), range **11.9–48.2** |

Every figure matches `research/modalities/emc-locoregional-eligibility.json` exactly — events, denominators, percent, both interval bounds, `cohorts_pooled`, `source_ids`, `per_cohort_percent`, `heterogeneity_range_percent`, and both `cohorts_excluded` maps (11 rows for metastasis, 10 for recurrence). Zero discrepancies.

Two structural checks I ran on the same pass:
- **All eight `{events, denom}` values that enter the two pools are Python `int`.** The `pool()` non-integer-check that W53/W60 identified is **latent, not live**, on today's committed registry. I did not audit the enforcement of it.
- The §2.1(3) exclusion fires as documented: `Metastatic at diagnosis` (`criteria.stage == "distant"`, n=29) is dropped from the metastasis pool by name, not by a missing field. `dataStatus` is `partial-curated`; `SAMPLE_SYNTHETIC` appears nowhere.

Grades:

| claim | grade |
|---|---|
| 36.3% (94/259), CI 30.7–42.3, k=3, range 29.1–46.1 | **PRIMARY** — reproduced from committed integer counts; the counts themselves are RETRIEVED from three published series |
| 27.0% (88/326), CI 22.5–32.1, k=4, range 11.9–48.2 | **PRIMARY** (same basis); the pooled *endpoint* is a mixture — see negative D |
| 71.6% / 84.5% extremity fractions | **RETRIEVED** — transcribed site tables, pooled here; not in the registry |
| any statement that a locoregional or radiation intervention works | **UNSUPPORTED** — asserted nowhere in this report or draft |

### B. The three stated negatives, each checked rather than repeated

I enumerated the full cohort key space by recursive walk. It is exactly: `contextReason, criteria(.stage), diseaseDeath(.denom,.events), dssText, fiveYearDSS, label, medianFollowupMonths, metastasis(.denom,.events), metastasisPct, n, note, otherCauseDeath(.denom,.events), otherCauseDeathNote, pool, populationKey, primaryRef, provenance, recurrence(.denom,.events), recurrencePct, recurrenceText, sourceId, stratum, studyPeriod, studyPeriodUnknown`.

| stated negative | verdict | evidence |
|---|---|---|
| **1. No cohort carries a primary anatomical site field** | **TRUE, but materially narrower than it reads** | No `site` key on any of the 14 cohorts. **However**: (i) `registry.fields.site` = `"Anatomic site"` — the schema *defines* the field, it is the per-patient schema, and **4/4 `registry.patients` carry it** (`abdominal wall`, `thigh`, `intracranial`, `knee`); (ii) `cohorts[13]` (`china2016`, n=40) carries **`"Median age 49; lower limb 60%."` in its free-text `note`** — a primary-site proportion, present as prose, percentage-only, on a `pool: false` cohort. So "no site data anywhere in the registry" would be **false**; "no cohort carries a poolable integer site count" is what is true. |
| **2. Metastatic site appears once in free text rather than as data** | **TRUE, exactly as stated** | Exactly one cohort-level occurrence: `cohorts[1]` (`masunaga2025`, metastatic-at-dx, n=29) `note` = `"27 lung, 2 peritoneal metastases; 16 received systemic therapy…"`. Every other `lung`/`pulmonar` hit in the file is in `overview`, `treatments`, `followUp`, `patients[].note` or citation prose. |
| **3a. No cohort records lesion burden** | **TRUE, and it survives outside the registry too** | No lesion-count key in the cohort key space. The two `burden` string hits are `"tumour mutational burden 0.67 mut/Mb"` — a genomic quantity, not a lesion count. `emc-site-curation.json#⛔_what_is_still_not_computable.lesion_burden`: *"no series prints per-patient lesion counts."* **CONFIRMED unresolved.** |
| **3b. No cohort records time-to-metastasis** | **TRUE of the registry; FALSE as a statement about the corpus** | No timing key on any cohort (`medianFollowupMonths` is follow-up, not interval-to-event). **But** `research/modalities/emc-recurrence-timing.json#cohorts[0].events[1]` carries `masunaga2025`, event `distant_metastasis`, **median 16 months from diagnosis, IQR 10–31, n = 39**, `printed_in` the paper's Results. `emc-site-curation.json` adds a second: chiusole2020 median 5.9 years, bishop2019 median 28 months. **What is missing is per-patient timing, not the quantity.** Printed medians and IQRs exist for three series and are committed. |

**The most valuable finding of this run is a fourth check the record does not ask for.** The record's premise — *"the paper has its denominator and not its numerator"* — is **superseded at this HEAD, and the module that produced it says so in its own source.** `emc_locoregional_eligibility.py:52-56` sets `QUANTITIES["primary_anatomical_site_distribution"]["computable"] = True` with `"⚠ *Superseded, retained: False.*"` and `resolved_by: research/modalities/emc-site-curation.json`. That artifact (generated by `emc_site_curation.py`, committed 2026-09-04) carries `pooled_extremity_fraction`, which I reproduced independently:

| reading | events/denom | % | Wilson 95% CI | per-cohort | range |
|---|---|---|---|---|---|
| **extremity, strict** (limb rows as each series defines them) | **194/271** | **71.6** | **65.9–76.6** | chiusole 78.0, masunaga 67.8, bishop 78.0 | 67.8–78.0 |
| **extremity, inclusive** (+ shoulder 9, groin 8, axilla 3, buttock 15 — the junctional rows masunaga files under trunk) | **229/271** | **84.5** | **79.7–88.3** | chiusole 78.0, masunaga 88.3, bishop 78.0 | 78.0–88.3 |

Arithmetic verified from the printed subcounts: chiusole 40+6 = 46/59; masunaga strict 100+16 = 116/171, inclusive +35 = 151/171; bishop 32/41. Sums 194 and 229 over 271. Both Wilson intervals reproduce to the published decimal. Denominators differ from the registry cohorts (59 vs 49; 171 vs 134+29) for a stated and correct reason recorded in the artifact's own `⚠_these_denominators_DIFFER…` block.

**So RT-LIMB-PERFUSION's eligible fraction exists.** `PUB-LOCOREGIONAL.why_not_written` in `systems/graph/publications.json` is **stale prose relative to the committed artifacts it describes** — it names a curation step that was carried out on 2026-08-25 and extended on 2026-08-27. This is a record-vs-artifact disagreement, not a defect I am proposing to repair; I author no patch.

### C. What genuinely remains missing

RT-LUNG-DIRECTED's numerator. `emc-site-curation.json#lung_confined_readings` is explicit and the finding **cuts against the route**: masunaga 27/29 and bishop 12/13 are **upper bounds**, because "had lung metastases" is an involvement word, not a confinement word; chiusole's rows are non-exclusive (23+4+14 = 41 over 26) and its table and running text disagree by one and two patients; and drilon2008 — the only reachable series that draws the distinction in its own words — prints **63% confined against 80% lung-as-first-site**, percentage-only, so §2.1(2) forbids reconstructing counts from it. No pooled lung-confined fraction is admissible.

### D. One limitation the pooled recurrence figure carries structurally

`ussc2022`'s cohort `note` reads `"Locoregional recurrence 18/60; any relapse 41.6%"` — it contributes a *locoregional* count while `masunaga2025` and `meisKindblom1999` contribute unqualified recurrence. The 27.0% is a **mixture of endpoints**, as the artifact's own `_limits[2]` states. It is the weaker of the two headline figures and the draft below says so.

---

## The single curation step, specified

**NOT PERFORMED. NOT CODE. NO FILE WRITTEN. This is a specification only.**

The step the record names for primary site is **already done**. The one that remains, and that would convert the surviving denominator into RT-LUNG-DIRECTED's eligible fraction, is:

> **Transcribe, per patient, whether metastatic disease was confined to the lung or involved the lung alongside another site — as mutually exclusive categories over one stated stratum — for `drilon2008`.**

| element | specification |
|---|---|
| **Field** | a new `metastatic_pattern` row per series taking exactly one of `lung_confined` / `lung_plus_other` / `non_lung`, with `{events, denom}` integers and a named stratum, added to `emc-site-curation.json#series[]` — **not** to `research/data/emc-clinical-registry.json`, which `emc-site-curation.json` records as being inside the manuscript inventory and therefore not the right home for newly transcribed counts. |
| **Cohort** | `drilon2008` — n=86 or 87 (the paper's abstract and Results disagree; the registry carries 87, and the discrepancy is recorded unresolved). It is the **only** reachable series that separates confined from involved in its own words. |
| **Source** | `PMC2779719` (PMID 18951519, DOI 10.1002/cncr.23978, *Cancer* 2008), already retrieved at $0 through the NCBI PMC full-text API and already cited in `emc-site-curation.json#context_not_pooled[0]`. The counts are **not** in the rendered text layer — the sentence is percentage-only ("approximately 62%… 17%… 13%… 8%"; "63% with metastasis confined to the lungs and 17% with metastasis at other sites concurrent with lung disease") — so the step is specifically **to render the table object that channel does not render**, not to re-read the paragraph. |
| **What must NOT be done** | back-derive 63% × 34% × 87 into a count. `POLICY-evidence` §2.1(2) forbids it, and `emc-site-curation.json` refuses it explicitly. Nor may `remiszewski2025` be used: it is a review, and §1.3 forbids laundering a primary's counts through one. |
| **Resulting quantity** | a single-series lung-confined fraction `x/n` with a Wilson 95% interval, over the stratum "diagnosed with or progressed to metastatic disease". **Not a pool** — k would be 1, and §2.1(3)/§2.4 forbid summing it with masunaga's presenting stratum or bishop's during-follow-up stratum. Expected magnitude ≈ 63% of the metastatic subgroup, materially **below** the 27/29 and 12/13 upper bounds, i.e. the step is expected to *shrink* the route's eligible fraction. |
| **Cost / reachability** | $0 if the table renders. If it does not, the honest outcome is **UNKNOWN**, and the quantity stays percentage-only context. `Paioli 2020` (PMID 32572850) is recorded as a lead with **no PMCID**, hence not reachable at $0, and not assumed non-overlapping with chiusole2020. |

---

## Drafted section

Manuscript register. Every number carries its source path. **No file was written; this draft exists only here.**

---

### Results

**3.1 The population a local-control strategy would exist for**

Across three non-overlapping series with explicit integer event counts, **36.3% of patients (94 of 259; Wilson 95% CI 30.7–42.3%)** developed distant metastatic disease during follow-up. The per-series rates were 29.1% (39/134), 46.1% (35/76) and 40.8% (20/49), a range of **29.1–46.1%** (`research/modalities/emc-locoregional-eligibility.json#who_ever_metastasises`, pooled from `research/data/emc-clinical-registry.json#registry.cohorts[*].metastasis`). A fourth cohort, patients metastatic at diagnosis, is excluded by construction: its metastasis rate is 100% by inclusion criterion, and pooling it would inflate the estimate (`systems/POLICY-evidence.md` §2.1, rule 3).

Local recurrence was recorded in **27.0% of patients (88 of 326; Wilson 95% CI 22.5–32.1%)** across four non-overlapping series, per-series 11.9%, 48.2%, 30.0% and 28.6% — a range of **11.9–48.2%** (`…#who_recurs_locally`). That range is wide, and it is the honest signal rather than the point estimate: the series differ in era, referral pattern and follow-up length, and one is a pathology consultation series selected toward diagnostically difficult tumours. The pooled recurrence figure is additionally a **mixture of endpoints** — one contributing series reports locoregional recurrence specifically and the others report recurrence without qualifying it — and is therefore the weaker of the two figures reported here.

Both are crude during-follow-up proportions with censoring ignored and follow-up lengths that differ between cohorts (`systems/POLICY-evidence.md` §2.2, §2.4). They are not survival estimates and are not prognostic for any individual. Because metastases in this disease appear over many years, crude proportions over mixed follow-up systematically **understate** lifetime event rates; that bias runs against the argument developed here and is stated for that reason.

**3.2 Where the primary tumour sits**

Isolated limb perfusion can be offered only for an extremity primary, so the eligible fraction for that modality is the extremity fraction. Site distributions printed over the whole series were transcribed from the primary reports of three open-access series — an Italian/French two-institution series (n = 59), a Japanese national registry study (n = 171) and a US single-institution series (n = 41), n = 271 in total (`research/modalities/emc-site-curation.json#series`). Under each series' own top-level limb categories, **71.6% of primaries were extremity (194/271; Wilson 95% CI 65.9–76.6%)**, per-series 78.0%, 67.8% and 78.0%.

That figure is bounded below by a definition rather than by sample size. One series files shoulder (9), groin (8), axilla (3) and buttock (15) — 35 of its 171 patients — under *trunk*, and each is a primary for which limb-directed delivery is arguable rather than excluded. Counting them as extremity gives **84.5% (229/271; 95% CI 79.7–88.3%)** (`…#pooled_extremity_fraction`). The gap between the two readings, 12.9 percentage points, is **wider than the sampling interval on either**, so the binding uncertainty in this quantity is a category boundary, not a denominator. Neither reading is called the answer here, and any single extremity fraction quoted for this disease is quoting a boundary its author did not state. The inclusive reading is further asymmetric: only one of the three series contributes junctional patients to it, so it is biased downward by an unknown amount (`…#_method.⛔_the_inclusive_pool_is_NOT_symmetric`).

**3.3 Where the metastases sit — the limit of this analysis**

A lung-directed strategy is offerable only to patients whose metastatic disease is lung-confined. **That fraction is not computable from the reachable literature, and this analysis does not estimate it.**

Four series say something about metastatic site and no two say it in the same form (`research/modalities/emc-site-curation.json#lung_confined_readings`). Two print an exclusive partition that exhausts its cohort — 27 lung and 2 peritoneal on 29 patients metastatic at diagnosis, and 12 lung and 1 bone on 13 patients who metastasised during follow-up — but these describe **different presentation strata over different populations and may not be summed** (§2.1.3, §2.4). Both are also **upper bounds rather than measurements**: the printed verb in the larger of them is that 27 patients *had* lung metastases, which states involvement and not confinement, and a one-category-per-patient table records the site a patient was filed under, not the absence of another. A third series' metastatic-site rows are non-exclusive (23 lung + 4 bone + 14 other = 41 over a denominator of 26), and its table and running text disagree by one and by two patients; no confined fraction can be read from it and none is inferred. The one series that draws the confined/involved distinction in its own words reports **63% confined against 80% with lung as the first site** — so roughly a fifth of lung involvement in that series is lung plus another site — and prints percentages only, which under §2.1(2) may not be converted into counts.

Two further quantities a local-control argument would want are absent from the reachable record at the level required. **Per-patient lesion burden is printed by no series**, so no fraction meeting any conventional oligometastatic threshold can be stated. **Time to metastasis exists only as printed summary statistics** — median 16 months from diagnosis, IQR 10–31, over 39 events in the largest series (`research/modalities/emc-recurrence-timing.json#cohorts[0].events[1]`), with medians of 5.9 years and 28 months in two others — and **never per patient**, so it cannot be crossed with site or with burden.

**3.4 Local therapy of metastases is already being delivered**

All three curated series record it as counts of what was done: metastasectomy in 8 of 29 patients presenting with distant metastases in one; 8 lung metastasectomies and 2 radiofrequency ablations in another; and surgical resection of metastases in 5 of the 13 patients who recurred distantly in the third (`research/modalities/emc-site-curation.json#⭐_local_therapy_of_metastases_is_already_being_given`). **These are counts with no comparator and no outcome attached, and nothing follows from them about whether any of it helped.** One of the three series states in its own words that neither salvage surgery (p = 0.15) nor salvage chemotherapy (p = 0.24) was associated with improved disease-specific survival. The relevance of the counts is descriptive only: a local approach to metastatic disease in this disease is a description of existing practice, so the open question concerns extension of an existing practice rather than its introduction.

**3.5 What these numbers together do and do not establish**

Taken together the figures describe a **match between a reported disease profile and a class of treatment**, and nothing more. A disease in which roughly a third of localised patients develop distant disease, a quarter to a third recur locally, and between 72% and 85% of primaries arise in a limb or at a limb girdle, is a disease whose reported profile overlaps the operating envelope of locoregional and radiation-based modalities as those modalities are described in the general literature. **That overlap is a matching statement about published descriptions. It is not evidence that any locoregional, radiation, perfusion or ablative intervention is effective, safe, selective, or ready for use in this disease, and no such claim is made anywhere in this paper.** An eligibility denominator states how many patients a strategy could be **offered** to if it worked; it is silent on whether it works. No randomised trial of any of these interventions exists in this disease, and in every series read here every treatment was allocated by indication.

---

### Limitations

The pooled estimates in §3.1–3.2 are **crude denominator-weighted proportions with Wilson 95% score intervals**, computed under the binding contract at `systems/POLICY-evidence.md` §2. They are **hypothesis-generating, not prognostic**; there is no survival model and no individual prediction. The random-effects (DerSimonian–Laird) pooler used elsewhere in this repository was deliberately not used here, because these are simple proportions, which §2 governs; quoting one method where the other is meant is a real error, and the estimator is named on every figure above.

The limitations §2.5 attaches to every such figure apply here in full and are reproduced in the contract's own terms: **publication bias (case reports over-represent unusual or severe disease); heterogeneous and often short follow-up; no censoring or Kaplan–Meier estimation; no risk-adjustment or multivariable control; and a small total N for a rare cancer. The figure is a rough signal, never a personal prognosis.**

Beyond §2.5, five limitations are specific to this analysis. **First, one series contributes the largest denominator to both headline pools**, which §2.2 requires be disclosed rather than absorbed into a weighted mean. **Second**, the pooled series differ in era, referral pattern and follow-up, and one is explicitly a consultation series — a selection this pooling cannot correct for. **Third**, distant metastasis and local recurrence are different endpoints with different clinical meaning, and the recurrence pool mixes a locoregional-specific count with unqualified recurrence counts; it is the weaker figure. **Fourth**, crude proportions over mixed follow-up understate lifetime event rates in a disease whose metastases appear over many years, so §3.1 is a floor and not a central estimate. **Fifth and most consequentially, the eligible fraction for a lung-directed strategy is not reported here at all**: it is not a number this analysis declines to emphasise, it is a number the reachable record cannot supply, for the reasons given in §3.3. The single step that would supply it — a per-patient confined-versus-involved transcription from the one series that draws that distinction in its own words — is specified in the Methods and has **not** been performed.

The site fractions in §3.2 rest on three series with **licence-restricted or paywalled siblings**: seven further candidate series return no PMC identifier and their site tables were not reachable, and one review was excluded because deriving a primary's counts through a review is forbidden by contract. Their absence is **unknown, not zero**, and the direction of any resulting selection is unestimated. Finally, no wet-laboratory work underlies any statement in this paper, and no computational or observational result reported here can establish efficacy, safety, selectivity, therapeutic window or clinical readiness for any intervention.

---

## Writability verdict

### **WRITABLE NOW.**

Not merely writable as "the argument plus the sized problem plus a named gap", which is what the record anticipated — writable with **one numerator already in hand**. RT-LIMB-PERFUSION's eligible fraction (71.6% strict / 84.5% inclusive, n = 271, k = 3, both intervals reproduced) exists in `emc-site-curation.json`, has never been written into any prose in this repository, and is the paper's strongest and most novel quantity.

Three qualifications on that verdict, each load-bearing:

1. **The record's own `why_not_written` is stale and should not be quoted as the paper's premise.** It says the site quantity was never curated; `emc_locoregional_eligibility.py:52-56` says `computable: True`, marks the old `False` as *"Superseded, retained"*, and names `emc-site-curation.json` as its home. The paper must be written from the artifacts, not from the graph record.
2. **RT-LUNG-DIRECTED's numerator is genuinely absent** and the draft states it as a limit rather than an implication. It should not be softened later: the one series that separates confined from involved reports a materially lower figure than the two upper bounds, so the missing number is expected to be unflattering to the route.
3. **Lesion burden is not obtainable from any reachable source** and no future curation step is specified for it. If a reviewer asks for an oligometastatic fraction, the answer is that it does not exist in this literature.

Sections not drafted here — Introduction, Methods, Discussion — require no new inputs; all their inputs are committed. Venue remains `preprint`, consistent with the record and with the standing aiXiv grant; **PUB-ASO remains the first manuscript to finish**, and this deliverable does not compete with it.

---

## Validation evidence

**RUN.** Environment: `python3` (stdlib only), Linux container, cwd `/home/user/Rare-cancers`, scratch `/tmp/claude-0/p3/` (deleted at end).

| # | command | exit | key output |
|---|---|---|---|
| 1 | `date -u; git rev-parse HEAD; git status --porcelain` (start) | 0 | `Tue Sep 8 05:09:15 UTC 2026`; `0d05cb7b…`; status **empty** |
| 2 | `python3 /tmp/claude-0/p3/repro.py` (independent reimplementation of `pool()`/`wilson()` over the registry) | 0 | `dataStatus: partial-curated n_cohorts: 14` · `== metastasis k= 3 94 / 259 = 36.3 CI 30.7 42.3` · `range [29.1, 46.1]` · `== recurrence k= 4 88 / 326 = 27.0 CI 22.5 32.1` · `range [11.9, 48.2]` · `int-check:` all eight values `('int','int')` |
| 3 | `python3 /tmp/claude-0/p3/neg.py` (recursive cohort key-space walk + token census) | 0 | key space listed above; `'extremity': 0`, `'oligomet': 0`, `'anatom': 0`, `'timeTo': 0` |
| 4 | `python3 -c "…wilson(194,271); wilson(229,271)…"` | 0 | `strict (71.6, 65.9, 76.6) incl (84.5, 79.7, 88.3)`; addends `194 229 271` |
| 5 | `rg -l -i "locoregional" …`; `git ls-files \| rg -i "locoregional\|perfusion\|oligomet"`; `rg -n "71\.6\|84\.5" …`; `rg -n "36\.3%\|27\.0%\|94/259\|88/326" …` | 0 | no PUB-LOCOREGIONAL manuscript exists; 71.6/84.5 appear in no manuscript; 36.3% appears once, at `research/manuscripts/aso/fusion-junction-aso-working-record.md:1318` |
| 6 | `date -u; git rev-parse HEAD; git status --porcelain; rm -rf /tmp/claude-0/p3` (end) | 0 | `Tue Sep 8 05:11:31 UTC 2026`; `997bc9e7…`; status **empty**; scratch removed |

All figures in the draft trace to row 2, row 4, or a quoted `printed_in` field of a committed artifact.

**PROPOSED (NOT RUN).** The drilon2008 table transcription in "The single curation step"; the Introduction, Methods and Discussion sections; any registry or artifact edit. **`research/modalities/emc_locoregional_eligibility.py` was NOT executed** — I read its source and confirmed it has no `--check` path and that `main()` unconditionally writes `research/modalities/emc-locoregional-eligibility.json` (`:255-257`). `research/modalities/atr_hrd_sarcoma_series.py` was not invoked in any form. `scripts/preflight.sh` was not run. No gate, guard, linter, test or CI job was audited, executed or discussed as a finding.

---

## Limitations

This report's own limits, distinct from the manuscript's:

- I verified the pooling **arithmetic and its inputs**, not the transcription accuracy of the underlying counts. Whether `39/134`, `35/76`, `20/49`, `16/134`, `40/83`, `18/60`, `14/49` and the site subcounts faithfully reflect the printed papers is **UNKNOWN to me**; I opened no source PDF and made no network request. Every count is second-hand at one remove.
- `emc-site-curation.json`'s `verified_against` fields assert PDF and PMC reads performed on 2026-08-25/27. Per the campaign's own W43 finding, an assertion of a reading recorded in a JSON field is **undecidable, not false**. The extremity fractions inherit that status.
- The extremity pool's admissibility under §2.3 rests on `emc-site-curation.json`'s argument that bishop2019's overlap partners (SEER, USSC) contribute no site distribution to *that* pool. I read the argument and find it internally coherent; I did not independently establish that the three site populations are disjoint.
- `pool()`'s missing integer check is latent on today's data (verified) but I did not examine what would happen under a future edit — that is enforcement, outside my lane.
- The 12.9-point strict/inclusive gap means **no single extremity fraction should be extracted from this report** without its definition.
- The `PUB-LOCOREGIONAL.why_not_written` staleness is reported as a factual disagreement between a graph record and the artifacts it describes. I authored no repair, proposed no patch, and edited nothing.

---

## Stop condition

**Set at dispatch:** stop when the two headline pools are independently reproduced with their k, denominators, per-cohort values and heterogeneity ranges; the three negatives are each individually checked against the registry schema; the single curation step is specified against a named reachable source; and a Results + Limitations draft with per-figure provenance exists in this report.

**MET.** All four conditions satisfied. Returned early against the ~40-call / ~40-minute target. One material finding beyond scope: the record's premise is superseded by its own module's `QUANTITIES` table and by `emc-site-curation.json`, and one stated negative (time-to-metastasis) is true only of the registry.

---

## Tool-call and wall-clock count actually used

**19 tool calls** (18 Bash, 1 Bash-persisted-output read). **Wall clock ≈ 2 min 16 s** measured start-to-end (`05:09:15Z` → `05:11:31Z`). Well inside both targets.

---

## Next concrete action

**One successor, in the PAPER lane, sized for one worker:**

> Draft the **Introduction, Methods and Discussion** of PUB-LOCOREGIONAL to accompany the §3 Results and Limitations above, and return them in report text. All inputs are already committed — `research/modalities/emc-locoregional-eligibility.json`, `research/modalities/emc-site-curation.json`, `research/modalities/emc-recurrence-timing.json`, `systems/POLICY-evidence.md` §2, and the two care-delivery memos, whose `RT-METASTASECTOMY` DO-NOT-WRITE and `RT-RT-INTENSIFY` REFUTED rulings the Discussion must honour rather than re-open. The Methods must name crude denominator-weighted proportions with Wilson intervals, state that the DerSimonian–Laird pooler was deliberately not used and why, and carry the drilon2008 curation step as declared future work. **No new retrieval, no wet-lab claim, no efficacy claim, and PUB-ASO stays ahead of it in the queue.**

A second, separable item for the **coordinator, not for a paper worker**: `PUB-LOCOREGIONAL.why_not_written` in `systems/graph/publications.json` states that primary anatomical site was never curated, while `research/modalities/emc_locoregional_eligibility.py:52-56` marks that exact sentence *"Superseded, retained"* and names the artifact that resolved it. That is a graph record disagreeing with the committed artifacts it describes. I author no repair for it and flag it for an owner ruling.
