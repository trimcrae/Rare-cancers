<!-- collected 2026-09-08T05:15:26Z by campaign coordinator; agent id a4230d3b4033f449e; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a4230d3b4033f449e.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

All work complete; scratch deleted; tree clean at start and end.

---

## Worker

**P2**, PAPER lane, OPUS-CAPACITY-CAMPAIGN-20260908. Candidate: `PUB-CARE-DELIVERY`.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED** — I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the real per-child runtime model from the transcript.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (run at start; no `*model*` variable exists in this environment, and the grep's `model` term matched nothing):

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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,...
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 ... (proxy config, elided for length only)
NO_PROXY=localhost,127.0.0.1,::1,...
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,...
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**State record.**

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 05:08:50 UTC 2026` | `Tue Sep  8 05:11:30 UTC 2026` |
| `git rev-parse HEAD` | `0d05cb7b3bf27921cceeb76bd69873ed89eb9fd6` | `997bc9e769da6bf606392941d46d20b319beab85` |
| `git status --porcelain` | empty | empty |

HEAD advanced under me (coordinator collection commits, as COMMON-BRIEF §1 warns). **All my reads were at `0d05cb7b`.** I wrote nothing to the repository and ran no git write operation. Scratch was `/tmp/claude-0/p2/`, created empty and deleted (`rm -rf`, then `ls` → `No such file or directory`).

## Question

Is `PUB-CARE-DELIVERY` writable now, and if not, what exactly is missing? Concretely: (1) do the four extraction artifacts its record names exist and say what it says; (2) is the 554-record corpus behind `BLK-NO-FIELD-ATTENTION-MEASUREMENT` reachable from this checkout with no network call; (3) what do the verified inputs actually support in manuscript prose?

## Prior-work check

Commands run and what they showed:

- `rg -c -i "PUB-CARE-DELIVERY" --glob '!.git' --glob '!research/autonomy/opus-capacity-campaign-20260908/**'` — 18 files. The substantive ones outside generated `systems/views/`: `systems/graph/{publications,routes,blockers}.json`, `research/manuscripts/care-delivery/emc-care-delivery-endpoint-decision.md` (4 hits), `research/autonomy/research-ledger.json` (14 hits), `research/autonomy/sprint-2026-09-01/{S15-CAREDELIVERY,S18-FALSE-ABSENCES,S2-ESCALATION}.md`.
- `git ls-files | rg -i "care-delivery"` — 11 tracked paths, including the whole `research/manuscripts/care-delivery/` directory.
- `rg -l -i "term census" …` — 10 files, **all of them the blocker's own text or a view rendering it**. No census artifact, no census script, no census output exists anywhere in the tree.
- `grep -rln "40885991" …` — 10 files; the abstract itself is committed at `research/literature/rt-lung-mets-probe.json:1058` and `:1245`.

**Closed items I confirmed I am not replaying** (`CLOSED-WORK.md`): I did not touch the NR4A Perspective, the ASO/Qeios deliverables, the rejected registry ICD-O classification paper, or any denied retrieval route (Pazopanib, Sunitinib 2014, Wagner 2020, CTARC 2022, Trabectedin/RT 2018). `CLOSED-WORK.md:28-30` explicitly instructs reading the care-delivery records before proposing a new clinical question — I did that, and it is what produced the central finding below. I read no `reports/W25-*` and touched no GSE243553 scope.

**⛔ The decisive prior work, which changes the answer to my own question.** Two committed records that the `publications.json` record does not cite:

1. `research/autonomy/research-ledger.json:1234` — ledger row **AUT-064**, `serves: {route: RT-SURGICAL-QUALITY, publication: PUB-CARE-DELIVERY, strategy: ST-CARE-DELIVERY}`, `state: "done"`: *"⛔ The publish decision is ANSWERED — no. The margin finding restates the printed conclusion of its own largest source's abstract (PMID 40885991 …), so it fails the consequence test trimcrae applied to DOC-EMC-ICDO-9231-CLASSIFICATION on 2026-08-23. **The next action is to fold the denominator sensitivity … into a short internal record, not a paper.**"* The same sentence is mirrored at `systems/graph/routes.json:8289`.
2. `research/manuscripts/care-delivery/emc-care-delivery-endpoint-decision.md` §6 (`:371-470`), dated 2026-09-01/02 — **the Findings prose I was asked to draft has already been written**, as §6.1 (AUT-064, margin denominator sensitivity) and §6.2 (AUT-065, follow-up window), under an explicit header: *"⛔ **NEITHER OF THESE IS A PAPER, AND NEITHER BECOMES ONE HERE.** … Nothing in this section is added to a submission text, to `systems/graph/publications.json`, or to any venue."*
3. The same ledger file records the user's own verbatim answer of 2026-09-01 to a group question that named PUB-CARE-DELIVERY by name: **"ASO only today."** That is consistent with `CLAUDE.md` §0.

I therefore treat the Findings draft below as a **re-derivation from the artifacts for this report's own auditability**, not as new prose, and I say so again in the draft header. Producing it as a *paper* section would replay a closed decision.

## Method and inputs

Read-only inspection of the live working tree at `0d05cb7b`, plus local git plumbing and the frozen corpus. No network call of any kind: no `git fetch`, no `git ls-remote`, no HTTP. `python3` (`/usr/local/bin/python3`) with `json` only, for reading and re-counting.

Exact inputs:

- `systems/graph/publications.json` — record `PUB-CARE-DELIVERY` (`why_not_written` at `:119`).
- `systems/graph/blockers.json` — record `BLK-NO-FIELD-ATTENTION-MEASUREMENT`.
- `research/modalities/emc-surgical-quality.json`, `emc-site-curation.json`, `emc-prognostic-coefficients.json`, `emc-recurrence-timing.json`.
- `research/modalities/emc-care-delivery-evidence.json` (`corpus` block, `:5-17`).
- `research/manuscripts/care-delivery/emc-care-delivery-endpoint-decision.md`.
- `research/autonomy/research-ledger.json` (rows AUT-064, AUT-065, and the 2026-09-01 group-notification record).
- `research/literature/rt-lung-mets-probe.json:1058` — the committed PMID 40885991 abstract.
- `.git/{refs,logs,shallow,config}`; `/tmp/claude-0/frozen-corpus/extracted/corpus/`.

I ran no gate, no linter, no test, and never invoked `research/modalities/atr_hrd_sarcoma_series.py`.

## Eligibility verification (claim-by-claim table)

All four artifacts **exist**, and all four counts **reproduce**. Every value below was read from the file at `0d05cb7b`.

| # | Record's claim | Exact path | Exact key | Exact value | Reproduces? | Grade |
|---|---|---|---|---|---|---|
| 1 | 196 operated patients with a margin | `research/modalities/emc-surgical-quality.json` | `counts.operated_patients_with_a_margin_recorded` (line 195) | `196` | **YES.** Independently recomputed from the same file: `series[masunaga2025].registered` 171 − `margin_all_registered.no_surgery` 15 = **156**, plus `series[chiusole2020].margin_field_available_for` = **40**. 156 + 40 = 196. | **RETRIEVED** — a transcription of two printed tables (Masunaga Table 1; Chiusole Table 2 + Results sentence, both `printed_in` fields quote the source text). Not primary patient data; this repository holds no patients. |
| 2 | 271 patients' primary site | `research/modalities/emc-site-curation.json` | `pooled_extremity_fraction.extremity_strict.denom` (and `.extremity_inclusive.denom`) | `271` | **YES.** Recomputed from `series[*].n_total`: 59 (chiusole2020) + 171 (masunaga2025) + 41 (bishop2019) = **271**; each series' `primary_site_counts_sum` equals its own `n_total`, so no patient lacks a site. | **RETRIEVED**, with a **PREDICTION-adjacent caveat carried by the file itself**: the *pooled fraction over* those 271 is a computed estimate (`estimator: "crude denominator-weighted proportion (POLICY-evidence §2.2)"`, Wilson 95%), and the file records that these denominators deliberately differ from the clinical registry's cohorts and that both are right (`⚠_these_denominators_DIFFER_from_the_registry_cohorts_AND_BOTH_ARE_RIGHT`). |
| 3 | 45 printed Cox coefficients | `research/modalities/emc-prognostic-coefficients.json` | `counts.estimable_coefficients` (line 899) | `45` | **YES, and the arithmetic is now explicit.** `models[*].rows` holds **81** rows total; **48** carry a numeric `hr`; exactly **3** of those 48 carry `non_estimate: "complete_separation"` (`hr: 0.0`, `ci: null` — `previous_surgery=yes` and `site=upper_limb` on disease-specific survival, univariate and multivariate). 48 − 3 = **45**, matching the sibling key `counts.non_estimates_excluded: 3`. Corroborated independently inside the file at `_transcription_verified.hr_ci_p_triples_matched: 45`, `hr_ci_p_triples_not_found: 0`. | **RETRIEVED** (transcribed fitted coefficients from two printed tables). ⚠ The *transcription check itself* is **UNSUPPORTED from this checkout**: `_transcription_verified.⚠_the_source_texts_are_not_repository_content` states the source texts *"live on the literature-cache working branch, so this check is reproducible only where that branch is checked out."* Same unreachable ref as §Blocked route. |
| 4 | Four printed time-to-event statistics | `research/modalities/emc-recurrence-timing.json` | `counts.events_with_a_printed_median` | `4` | **YES.** Enumerated from `cohorts[*].events[*]`: masunaga2025 local recurrence 15 mo, distant metastasis 16 mo, death from tumour 36 mo; chiusole2020 distant metastasis 70.8 mo (`printed_as: "5.9 years"`). Chiusole local recurrence carries `median_months: null` with `⛔_no_timing`, matching `counts.events_with_no_timing_at_all: 1`; `counts.events_with_a_printed_iqr: 3`. | **RETRIEVED**, each with a verbatim `printed_in` quotation of the source sentence. |

**A finding about the record's own prose, not about the artifacts.** `publications.json`'s `why_not_written` opens *"**Six** extraction artifacts exist"* and then names **four**. The other two are identifiable from `emc-care-delivery-endpoint-decision.md`'s "one home for every number" list — `research/modalities/emc-radiotherapy-contradiction.json` and `research/modalities/emc-ipd-survival.json`, both of which exist — so the sentence is internally consistent once the reader has that second file, and is under-specified without it. **No count is wrong; the sentence is incomplete.** I did not adjust any prose (read-only), and I did not verify those two extra artifacts' contents, which are outside my four.

**Verified separately, because the draft turns on it:** the "margin decides local recurrence" headline really is the printed conclusion of its own largest source. `research/literature/rt-lung-mets-probe.json:1058` carries the PMID 40885991 abstract, whose Conclusions read verbatim *"Wide resection is mandatory to reduce the risk of local recurrence of localized EMCs"*, and whose Results already print the multivariate figure *"an R1 or R2 surgical margin was a risk factor for unfavorable local recurrence (hazard ratio [HR] 4.76 [95% CI: 1.72-13.15]; p = 0.003)"* — the identical HR the coefficients artifact transcribes.

## The blocked route: exact failed condition and exact reopening input

**Route: BLOCKED. Not substituted, not proxied, nothing inferred from the absence.**

The named free step is a term census over 554 records at `literature/emc-care-delivery-and-classification/` on branch `literature-cache` (`emc-care-delivery-evidence.json:5-17`: `records: 554`, `branch: "literature-cache"`, `path: "literature/emc-care-delivery-and-classification/"`, produced by `.github/workflows/fetch-literature.yml` run `31341462928`, dispatched 2026-08-09).

**Exact failed condition**, measured with local refs and the local filesystem only:

| Probe | Command | Result |
|---|---|---|
| Any ref named `literature-cache` | `git show-ref`; `git for-each-ref --format='%(refname) %(objectname)'` | **Absent.** Exactly five refs exist: `refs/heads/{claude/confident-bardeen-ji76cd, main}`, `refs/remotes/origin/{claude/confident-bardeen-ji76cd, codex/opus-cloud-inputs-20260908, main}`. |
| Packed refs | `ls -la .git/packed-refs` | `No such file or directory`. |
| Reflog trace | `grep -ril "literature-cache" .git/logs` | Two hits — **both are this campaign's own commit-message text**, `commit: campaign: collect W02j and W40; record the literature-cache ref state`, in `.git/logs/HEAD:39` and the branch log. **No ref ever pointed at it here.** This corroborates W40 rather than contradicting it. |
| Clone completeness | `git rev-parse --is-shallow-repository`; `wc -l .git/shallow` | `true`; **44** grafts. (⚠ My dispatch said 43 and COMMON-BRIEF says 42 — the graft count has grown with the campaign's own commits. Non-substantive, but quote 44 if quoting me.) |
| Fetch refspec | `git config --get-all remote.origin.fetch` | `+refs/heads/*:refs/remotes/origin/*` — the branch would be fetched *if it were fetched*; nothing was. |
| Path in the working tree | `ls -la literature`; `git ls-files \| grep -c '^literature/'` | `No such file or directory`; **0** tracked files. |
| Path in the frozen corpus | `ls /tmp/claude-0/frozen-corpus/extracted/corpus/`; `find … -ipath "*care-delivery-and-classification*"` | Corpus top level is `AGENTS.md CLAUDE.md README.md research scripts systems` — **no `literature/` member at all**; the `find` returns nothing. |

**The failed condition, stated exactly:** *no local ref, no local object, no working-tree path and no frozen-corpus member resolves `literature/emc-care-delivery-and-classification/`; the clone is shallow (44 grafts) and `literature-cache` was never fetched into it.* Per COMMON-BRIEF §2 this is **UNKNOWN, not absent** — whether the branch exists on the remote is not decidable from here, and I did not try to find out. I ran no `git ls-remote`, no fetch, and no HTTP request.

**Exact input required to reopen**, for someone with the remote:

- **Ref:** `refs/heads/literature-cache` on `origin` (the repository this checkout's `origin` points at).
- **Path:** `literature/emc-care-delivery-and-classification/` — 554 records, per `emc-care-delivery-evidence.json`, produced by `.github/workflows/fetch-literature.yml` run id `31341462928` dispatched 2026-08-09, with declared positive control PMID `32856598` passing.
- **Commands they would run** (none of which I may run):
  ```
  git fetch --no-tags origin literature-cache:refs/remotes/origin/literature-cache
  git ls-tree -r --name-only origin/literature-cache -- literature/emc-care-delivery-and-classification/ | wc -l   # expect 554
  ```
  The blocker's own `retired_by_action` names the alternative route it was retired through before: *"through the same GitHub contents API route that produced the 2026-09-01 metastasectomy refutation."* Either route is a **network act and is outside my authority**, and the second is outside this container's egress in any case.
- **What must then be delivered** for the blocker to retire: a term census reporting *"how the corpus divides between systemic-agent, surgical, margin and follow-up subject matter"* (`BLK-NO-FIELD-ATTENTION-MEASUREMENT.retired_by_action`), with a committed receipt — because `research/modalities/emc_care_delivery_evidence.py::absence_result` currently states of this same corpus that the file *"holds no term-census receipt over the named corpus, so the number of matching records is UNKNOWN."*

**Not done, deliberately:** I did not substitute `research/literature/*.json` (which are probe caches over a different, smaller retrieval), did not count terms over the tracked manuscripts as a stand-in, and drew no inference of any kind from the corpus being unreachable. Its absence here says nothing about what it contains.

**Clause 3 taken as given.** I did not re-attempt the "diagnosis known before the operation" clause. For the record only, the artifact independently states the same thing at `emc-surgical-quality.json`: `treatment_setting.recorded_in_any_reachable_series: false`, `unplanned_excision.recorded_in_any_reachable_series: false`, with `⛔_this_is_a_reading_not_a_gap` — Masunaga prints no centre, volume or referral status; Chiusole is entirely referral-centre care with no comparator.

## Drafted section

> **Status of this draft, stated inside it because it must travel with it.** This is a re-derivation *for audit*, not a new paper section. Equivalent prose already exists as an **internal record** at `research/manuscripts/care-delivery/emc-care-delivery-endpoint-decision.md` §6.1–§6.2, written 2026-09-01/02 under an explicit decision **not** to publish it standalone (ledger row AUT-064, `research/autonomy/research-ledger.json:1234`). Nothing below may be moved into a submission text without reopening that decision with its owner.

### Findings

**Two open-access series report a surgical margin for 196 operated patients, and no single positive-margin rate describes them.** Across the Japanese national-registry series, 39 of the 156 patients who were operated carried an R1 or R2 margin — 25.0%, Wilson 95% CI 18.9–32.3% (`research/modalities/emc-surgical-quality.json`, `masunaga2025_rates.positive_margin_among_all_operated`). Restricted to the operated patients who were localized at diagnosis the proportion is 22.4% (30/134, 16.2–30.2%; `…positive_margin_among_operated_localized_at_diagnosis`), and among those already metastatic at diagnosis it is 40.9% (9/22, 23.3–61.3%; `…positive_margin_among_operated_metastatic_at_diagnosis`). In the two-centre Italian/French series the margin field is recorded for 40 patients and 14 of them are R1 or R2 — 35.0%, 22.1–50.5% (`chiusole2020_rates.positive_margin_among_those_with_the_field_recorded`). **The eighteen-point gap between 22.4% and 40.9% sits inside one paper and one table, and separates patients who differ only in whether they had already metastasised when they presented.** A reader given any one of these four figures alone has been misled, and the direction of the error depends on which figure they were given. No pooled rate is computed here or in the artifact: the two series share neither era (1980–2018 against 2002–2022), setting (two referral centres against a national registry) nor denominator convention, and `systems/POLICY-evidence.md` §2.1 and §2.3 refuse the merge (`emc-surgical-quality.json`, `⛔_nothing_is_pooled`).

**The margin is also the one covariate that survives a cross-cohort filter over 45 fitted coefficients, and the finding it supports is not new.** The two series print seven Cox models across four endpoints; 45 coefficients are estimable with 95% intervals, three further rows being non-estimates from complete separation (`research/modalities/emc-prognostic-coefficients.json`, `counts.estimable_coefficients`, `counts.non_estimates_excluded`). Margin lies on the harmful side of 1 in all three endpoints of the registry series and in the institutional series, and it is the only covariate significant in more than one model: local recurrence HR 4.76 (1.72–13.15), distant metastasis 2.37 (1.21–4.64) univariate and 3.40 (1.57–7.38) adjusted (`models[*].rows`, `variable: surgical_margin`, `level: R1_or_R2`). The second cohort is consistent without independently establishing it — its own margin interval, 2.021 (0.540–7.570) for overall survival, includes 1. **This is a restatement of a published conclusion and must be read as one.** The larger source's own abstract prints both the figure and the inference: *"Multivariate analysis showed that an R1 or R2 surgical margin was a risk factor for unfavorable local recurrence (hazard ratio [HR] 4.76 [95% CI: 1.72-13.15]; p = 0.003)"* and *"Wide resection is mandatory to reduce the risk of local recurrence of localized EMCs"* (PMID 40885991, abstract as committed at `research/literature/rt-lung-mets-probe.json:1058`). What is added here is not the direction of the effect but the denominator sensitivity above, which that abstract does not contain. Across the 12 cross-cohort comparisons available, 11 agree in direction, every pair of intervals overlaps, and **in none do both intervals exclude 1** (`cross_cohort_summary`) — the agreement count is close to uninformative and is reported so that it is not mistaken for corroboration.

**Where the disease arises is settled; how long it is watched is not.** Primary site is transcribed for 271 patients across three series (59, 171 and 41; `research/modalities/emc-site-curation.json`, `series[*].n_total`, each series' `primary_site_counts_sum` equal to its own total). Limb primaries account for 71.6% under each series' own top-level category (194/271, 65.9–76.6%) and 84.5% once the junctional girdle sites one series files under trunk are included (229/271, 79.7–88.3%), by crude denominator-weighted proportion with Wilson intervals (`pooled_extremity_fraction`). Against that, the timing record is thin: four printed time-to-event medians exist in total (`research/modalities/emc-recurrence-timing.json`, `counts.events_with_a_printed_median`), and in the 134 localized, operated patients of the registry series the 16 local recurrences occurred at a median of 15 months from surgery with an interquartile range of 4.5 to 63.5 months, while that cohort's median follow-up is 38 months. **The upper quartile of the recurrence times therefore lies 25.5 months beyond the median follow-up** (`events_beyond_the_observation_window`), and death from tumour behaves the same way, upper quartile 69 months against the same 38. Both numbers come from one paper, one cohort and one clock, which holds era, country, setting and imaging generation constant by construction and leaves none of them available as an explanation.

**One clause of the intended claim is not answerable from this record at all.** Whether the diagnosis was known before the operation cannot be studied in this disease from the reachable literature: neither series reports treatment setting, centre, centre volume or referral status, and neither defines an unplanned excision (`emc-surgical-quality.json`, `treatment_setting.recorded_in_any_reachable_series: false`, `unplanned_excision.recorded_in_any_reachable_series: false`). That is a property of what the publications report, not of the curation, and re-curating either paper cannot produce it.

### Limitations

Every figure above is an **observational association or a count of what was done**, transcribed from the printed tables of retrospective series in which every treatment was allocated by indication. **Nothing here asserts efficacy, safety, selectivity, a therapeutic window or clinical readiness, and no computational work in this repository could establish any of them; there is no wet laboratory and no patient was studied here.** No surveillance interval, duration or intensity is derived, and none may be derived from these numbers: a median and an interquartile range establish a long right tail and cannot be differentiated into a hazard. None of the four margin proportions is a measure of surgical performance — a positive margin in a metastatic patient is frequently a deliberate choice, and neither publication prints the intent of any operation (`emc-surgical-quality.json`, `⚠_this_is_not_a_quality_metric`). The metastatic-stratum row rests on 22 operated patients and carries a direction, not a point estimate. No absolute risk follows from the 45 coefficients: neither paper prints a baseline hazard or any quantity one can be recovered from, so the models cannot be applied to a patient (`emc-prognostic-coefficients.json`, `⛔_what_is_structurally_impossible_from_print`). An interquartile range that *fits inside* a follow-up window is what censoring produces and is not evidence against it — the inference runs one way only — and lead-time bias is untouched: moving the date a recurrence is detected need not move the date of death, and no reachable series reports what fraction of late recurrences were resectable. Neither cohort prints a numbers-at-risk row beneath any of its seven stratified Kaplan–Meier curves. The margin-and-recurrence direction is a **restatement of PMID 40885991's own printed conclusion** and is not offered as a new result. The transcription check behind the 45 coefficients was performed against source texts held on a branch not present in this checkout and is **not reproducible here**. And the claim that the literature has attended to systemic agents at the expense of these determinants is, at present, **an argument with no measurement behind it**: the corpus that would measure it is unreachable from this checkout, so the size and direction of any such imbalance are UNKNOWN.

## Writability verdict

**NOT WRITABLE** — as `PUB-CARE-DELIVERY`, in its registered framing, for **two independent reasons**, either of which alone is sufficient.

1. **The second half of the working title has no measurement and cannot acquire one from here.** "What the literature has been looking at instead" is held by `BLK-NO-FIELD-ATTENTION-MEASUREMENT`, whose only named retiring act is a term census over a corpus that does not resolve in this checkout by any local route. That is not a *task*, it is a **missing input requiring a network act I have no authority to take**.
2. **The first half is already decided, and decided against, by a record with more authority than the publication register.** Ledger row AUT-064 (`state: "done"`, serving `PUB-CARE-DELIVERY`) reads *"The publish decision is ANSWERED — no … a short internal record, not a paper"*; the internal record it prescribes was written on 2026-09-02 as `emc-care-delivery-endpoint-decision.md` §6.1–§6.2, whose own header forbids its promotion to a submission text; and the user's verbatim answer of 2026-09-01 to the question that named this paper was **"ASO only today."** `CLAUDE.md` §0 says the same thing.

Stated the other way, so the coordinator can see exactly what would change it: **the census would retire the blocker but would NOT make the paper writable**, because reason 2 is a judgement already taken and only its owner can reopen it. So the honest form of "writable after n named inputs" here is *two* inputs and only one of them is technical:

- **(a)** `refs/heads/literature-cache` → `literature/emc-care-delivery-and-classification/` fetched, and a term census run over its 554 records with a committed receipt.
- **(b)** An owner decision reopening AUT-064's recorded "no" — which no worker may take, and which the consequence test applied on 2026-08-23 currently answers in the negative.

⚠ **The publication register is stale against the ledger on this record.** `publications.json`'s `why_not_written` presents the paper as blocked on one free step; the ledger and the decision memo record the publish question as **answered no** and the resulting internal record as **already written**. A reader of the graph alone cannot see that. This is a real inconsistency between two committed homes, it is exactly the class COMMON-BRIEF's stale-watcher result (W57) describes, and **I did not edit either file** — routing it is the coordinator's call.

## Validation evidence

**RUN** — all in `/home/user/Rare-cancers`, `python3` = `/usr/local/bin/python3`, git 2.x, no network. All exit 0 unless stated.

| Command | Key verbatim output |
|---|---|
| `git rev-parse HEAD` | `0d05cb7b3bf27921cceeb76bd69873ed89eb9fd6` (start) / `997bc9e769da6bf606392941d46d20b319beab85` (end) |
| `git status --porcelain` | empty at start and end |
| `git show-ref` | 5 refs; **no** `literature-cache` |
| `ls -la .git/packed-refs` | `ls: cannot access '.git/packed-refs': No such file or directory` (exit 2) |
| `git rev-parse --is-shallow-repository` | `true` |
| `wc -l .git/shallow` | `44 .git/shallow` |
| `git config --get-all remote.origin.fetch` | `+refs/heads/*:refs/remotes/origin/*` |
| `ls -la literature` | `ls: cannot access 'literature': No such file or directory` (exit 2) |
| `git ls-files \| grep -c '^literature/'` | `0` |
| `ls /tmp/claude-0/frozen-corpus/extracted/corpus/` | `AGENTS.md CLAUDE.md README.md research scripts systems` |
| `find /tmp/claude-0/frozen-corpus/extracted -ipath "*care-delivery-and-classification*"` | (no output) |
| `grep -n "196" research/modalities/emc-surgical-quality.json` | `195:    "operated_patients_with_a_margin_recorded": 196` |
| python3: sum `series[*].n_total` in `emc-site-curation.json` | `chiusole2020 59 / masunaga2025 171 / bishop2019 41` → 271, each `primary_site_counts_sum` equal to its `n_total` |
| python3: row census over `emc-prognostic-coefficients.json` | `rows total 81 numeric hr 48 non-estimates 33`; 3 rows carry `non_estimate: "complete_separation"`; 48−3 = 45 = `counts.estimable_coefficients` |
| python3: enumerate `cohorts[*].events[*]` in `emc-recurrence-timing.json` | 4 events with a numeric median (15, 16, 36, 70.8 mo); 1 with `median_months: null` |
| `rg -l -i "term census" --glob '!.git' --glob '!…campaign…'` | 10 files, all the blocker text or a view of it; **no census artifact** |
| `grep -ril "literature-cache" .git/logs` | 2 files, both matching only this campaign's own commit-message text |
| `rm -rf /tmp/claude-0/p2 && ls -d /tmp/claude-0/p2` | `ls: cannot access '/tmp/claude-0/p2': No such file or directory` |

**PROPOSED (NOT RUN)** — the two reopening commands in §The blocked route. Both are network acts, both are outside my authority and this container's egress, and **neither was attempted**.

**Not run, by instruction:** `scripts/preflight.sh`, `publish_bar.py`, any gate, linter or test, and `research/modalities/atr_hrd_sarcoma_series.py` in any form.

## Limitations

I read four artifacts, not the six the record alludes to; `emc-radiotherapy-contradiction.json` and `emc-ipd-survival.json` were identified by name but **not verified**. Every count I checked is a check on *internal* consistency — that the artifact's declared totals reproduce from its own rows — and **not** a check that any transcription matches its source paper: the source texts live on the same unreachable branch, so no worker in this container can verify a single digit against a publication. The PMID 40885991 abstract I quote is a committed cache entry (`rt-lung-mets-probe.json`), not a retrieval, and I did not open any link. The absence of `literature-cache` here is **UNKNOWN about the remote**, and nothing in my report may be read as evidence that the corpus does not exist or does not contain 554 records. My model identity is self-reported and unverified. HEAD moved under me mid-run; all reads are anchored at `0d05cb7b` and a re-run at a later HEAD could in principle differ, though the campaign's measured invariant is that only the campaign directory has changed. Finally, my writability verdict rests in part on reading a ledger row and a memo as authoritative over the graph record; that reading is an interpretation, and the two homes genuinely disagree.

## Stop condition

Declared up front: **stop as soon as (a) the four named artifacts are graded claim-by-claim, (b) the literature-cache route is settled reachable-or-not with an exact failed condition and exact reopening input, (c) the supported Findings and Limitations are drafted, and (d) a writability verdict is stated** — with no repair, patch, gate or test authored, and no substitute corpus used.

**MET, in full.** No branch was left open. One content-policy refusal would have stopped a branch; **none occurred**. No W25 scope, no GSE243553, no held work was read or referenced.

## Tool-call and wall-clock count actually used

**20 tool calls; 2 minutes 40 seconds wall clock** (`05:08:50Z` → `05:11:30Z`). Well inside the ~40-call, ~40-minute target; returning early.

## Next concrete action

**One action, for a human, not for a worker: put the reopening question to the owner and, if the answer is yes, take input (a) on a networked runner.**

Specifically — and in this order, because the second is wasted if the first is answered no:

1. **Ask the owner whether AUT-064's recorded "no" is being reopened.** The evidence has changed since 2026-09-01 in one respect only — the denominator sensitivity is now written down and the margin restatement is now explicitly labelled as a restatement — and it has not changed in the respect the decision turned on. `CLAUDE.md` §0 and the 2026-09-01 "ASO only today" both point the other way. **No worker may take this decision.**
2. **Only if reopened:** fetch `refs/heads/literature-cache` on a runner that has the remote, run the term census over the 554 records at `literature/emc-care-delivery-and-classification/`, and commit the receipt into `research/modalities/emc-care-delivery-evidence.json` so that `emc_care_delivery_evidence.py::absence_result` stops saying the matching-record count is UNKNOWN. That retires `BLK-NO-FIELD-ATTENTION-MEASUREMENT` by the act it names.

**A separate, smaller action that needs no decision and no network**, routed rather than taken because I am read-only: **reconcile `systems/graph/publications.json`'s `PUB-CARE-DELIVERY.why_not_written` with ledger row AUT-064.** The graph presents an answered publish question as an open one, and names four of six artifacts. Owner of `systems/graph/` should make that edit; I did not.
