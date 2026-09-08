> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check complete: mirror output byte-identical to the real repo before measuring, incumbent `validate-registry.mjs` exit 0 on the patched mirror, structural diff 45 keys added / 0 changed / 0 removed, and `git status --porcelain` shows no tracked modification under `/home/user/Rare-cancers`.

---

## Worker

**W13c** — refill for lane 13, W13b's named finite successor: resolve the unit of `n` for `registry.cohorts[5..13]`.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model; the coordinator must extract the runtime model from the transcript. I do not assert it as observed fact.

`date -u` at start: `Tue Sep  8 02:17:35 UTC 2026`. `date -u` at end: `Tue Sep  8 02:22:31 UTC 2026`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (I filtered out the five long proxy-host-list lines — `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` — which match only on the `anthropic` substring inside a host list and carry no model identity; nothing else changed):

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

⚠ **I dumped `env` once, at start, and did not re-dump at end.** I am reporting that rather than pasting a second block I did not capture. `date -u` at end is above.

⚠ **Frozen-commit correction, reported not concealed.** `git rev-parse HEAD` returned **`b9a0257e6acff53ad22535cf2adf261313e0b250`** — not the brief's frozen `92abbcb9`, and not W13b's mid-run `103ff76f` either. The coordinator has committed twice more (`103ff76f "Add OPUS-CAPACITY-CAMPAIGN-20260908 manifest and worker reports"`, then `b9a0257e "Campaign wave log and second batch of worker reports"`). **My input file is unaffected:** `git diff --stat 92abbcb HEAD -- research/data/emc-clinical-registry.json research/modalities/emc-fourth-cohort-quant.json` is **empty** — byte-identical to the frozen commit. Nothing in this report is invalidated. That commit chain does have a live consequence for W13's validator, quantified in §6 of Result below.

**Write isolation honoured.** `git status --porcelain` filtered to exclude other workers' untracked files is **empty**. I wrote nothing under `/home/user/Rare-cancers` and ran no git write operation against it. All execution was in `/tmp/claude-0/w13c/`.

## Question

**For each of `registry.cohorts[5..13]` — the nine cohorts W13b left untouched — what does its source's own sentence say its headline count counts: patients, tumours, or specimens?**

It is open because W13 proved by machine check (C1, 14/14) that no committed file states the unit of any cohort `n`, and W13b resolved only the five pooled rows, leaving nine C1 violations live and explicitly recording that "absence of a verdict there is UNKNOWN, not clean."

**And I say plainly what W13b said honestly of this successor: it is lower-value than W13b's own run.** All nine of these rows are `pool: false`. None enters `POLICY-evidence.md` §2.2's pooled arithmetic. No verdict I return here can move, corrupt, or correct any published headline number. What it can do is end the C1 finding class rather than leave it half-done: a labelling defect that cannot corrupt a number is still a labelling defect, and nine rows is a bounded job. That is the whole case for this run, and I am not going to dress it up as more.

## Prior-work check

Commands actually run against the tracked corpus:

- `git diff --stat 92abbcb HEAD -- research/data/emc-clinical-registry.json research/modalities/emc-fourth-cohort-quant.json` → **empty**; my inputs are byte-identical to the frozen commit.
- `git -C /home/user/Rare-cancers ls-files | wc -l` → 7638 tracked files; `comm -3` against my scratch mirror's `git ls-files` → **zero** files in either direction.
- Read in full: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `reports/W13-provenance-identity-contract.md` (538 lines), `reports/W13b-pooled-cohort-unit-resolution.md` (428 lines).
- Both prior artifacts extracted **verbatim by regex** from the committed reports rather than retyped: W13's `validate_identity_contract.py` (196 lines — matches W13's stated 196) and W13b's `apply_patch.py` (130 lines, 15 `put()` calls + 3 `denomNote` = W13b's stated 18 keys).

**Closed items I confirmed I am not replaying:**

- **CTARC 2022 (`PMID 35144048`, `DOI 10.1016/j.ctarc.2022.100530`)** — this **is** `cohorts[9]`'s source (`seer270_2022`). CLOSED-WORK records "abstract retained; latest publisher 403, methods unrecovered." I used **only the retained abstract**, via PubMed metadata. I attempted **no** publisher route and replayed **no** denied route. The verdict below is UNKNOWN, which is what the retained strength supports.
- **W13b's `ussc2022` identity precedent, checked rather than assumed.** `cohorts[3]`'s `ussc2022` is `PMID 35962783` (Gusho, *J Surg Oncol*) — a **different paper** from CTARC 2022 (`PMID 35144048`, Brown, *Cancer Treat Res Commun*). I verified this directly in the registry's own citation entries before treating `cohorts[9]` as blocked. `cohorts[9]` genuinely **is** the blocked paper; `cohorts[3]` was not, and W13b retrieved it.
- **Pazopanib primary (Stacchiotti 2019)** — named in `cohorts[8].primaryRef`. CLOSED-WORK: "primary full paper and observed exposure window unrecovered; abstract only." **I did not attempt it.** `cohorts[8]`'s declared `sourceId` is `remiszewski2025` (open access), so I read the row's actual declared source and recorded explicitly that the primary was not read.
- **Sunitinib 2014, Wagner 2020, Trabectedin/RT 2018** — none of the nine cohorts cites any of these. Verified against every `sourceId` and `primaryRef` in the nine rows.
- No content-policy refusal was encountered in this lane. No 403 was encountered, because I attempted no publisher route.

## Method / inputs

Read-only inspection of `/home/user/Rare-cancers` at `b9a0257e` (registry content identical to frozen `92abbcb9`). All execution in `/tmp/claude-0/w13c/`. Nothing written under the repository; no git write of any kind against it. Python 3.11.15, Node (for the incumbent `validate-registry.mjs`), Linux 6.18.44-fc-v24. No network beyond the PubMed MCP tools, no paid API, no GPU.

Retrievals, all via the PubMed MCP tools on 2026-09-08. According to PubMed:

- `get_article_metadata(["31436747","35144048","18951519","36825763","12599237","27402218"])` → Bishop 2019 [DOI](https://doi.org/10.1097/COC.0000000000000590); Brown 2022 [DOI](https://doi.org/10.1016/j.ctarc.2022.100530); Drilon 2008 [DOI](https://doi.org/10.1002/cncr.23978); Brodsky 2023 [DOI](https://doi.org/10.1097/COC.0000000000000988); Kawaguchi 2003 [DOI](https://doi.org/10.1002/cncr.11162); Shao 2016 [DOI](https://doi.org/10.1016/j.anndiagpath.2016.04.004).
- `get_full_text_article(["PMC12504171"])` → Remiszewski 2025 [DOI](https://doi.org/10.1007/s00432-025-06316-5) (CC-BY-NC-ND, open access; 55,085 characters).
- `search_articles("Giner extraskeletal myxoid chondrosarcoma margins recurrence")` → 1 hit; `get_article_metadata(["36376703"])` → Giner 2022 [DOI](https://doi.org/10.1007/s00428-022-03453-x).

## Result

### 1 · Inventory of `cohorts[5..13]` — the first deliverable, and it tells you which rows are retrievable

| # | `label` | `n` | `sourceId` | `pool` | `provenance` | `contextReason` | citation `openAccess` | PMID / PMCID | retrievable? |
|---|---|---|---|---|---|---|---|---|---|
| `[5]` | Localised, single-institution series | 41 | `bishop2019` | false | primary | population-overlap (US single institution; likely within SEER / US Sarcoma Collaborative) | **false** | 31436747 / PMC7771031 | **yes** — abstract states the unit |
| `[6]` | Localised, US SEER population | 156 | `remiszewski2025` | false | **secondary** (`primaryRef`: "Kemmerer et al. (SEER 2004-2012, n=156)") | population-overlap; percentage-only | **true** | 41055792 / PMC12504171 | **yes** — declared source is OA |
| `[7]` | Local recurrence by surgical margin | 31 | `remiszewski2025` | false | **secondary** (`primaryRef`: "Giner et al. (n=31)") | percentage-only | true | 41055792 / PMC12504171 | declared source yes; **primary paywalled** |
| `[8]` | Advanced disease on pazopanib | 26 | `remiszewski2025` | false | **secondary** (`primaryRef`: "Stacchiotti et al., Lancet Oncol 2019 phase 2 (n=26)") | different-endpoint | true | 41055792 / PMC12504171 | declared source yes; **primary in CLOSED-WORK, not attempted** |
| `[9]` | SEER overall-survival series | 270 | `seer270_2022` | false | primary | population-overlap; percentage-only | **false** | 35144048 / — | **abstract only — this IS CTARC 2022, full text blocked** |
| `[10]` | Two-referral-center long-term series (Drilon) | 87 | `drilon2008` | false | primary | percentage-only | **false** | 18951519 / PMC2779719 | **yes** — abstract states the unit |
| `[11]` | Single-institution series (U Michigan) | 44 | `uMich2023` | false | primary | population-overlap | **false** | 36825763 / — | **yes** — abstract states the unit |
| `[12]` | Japanese multi-institutional series | 42 | `japan2003` | false | primary | different-endpoint | **false** | 12599237 / — | **yes** — abstract states the unit |
| `[13]` | Chinese series | 40 | `china2016` | false | primary | percentage-only | **false** | 27402218 / — | **yes** — abstract states the unit |

Two observations from the inventory itself, before any retrieval:

- **`openAccess: false` was a poor predictor of retrievability here.** Six of the nine rows sit on citations flagged `openAccess: false`, and **five of those six** turned out to state their unit in the freely indexed PubMed abstract, so no full text was needed. Only `cohorts[9]` was genuinely blocked. The flag describes the full text's licence, not whether the question can be answered — a distinction worth recording because a future worker reading the flag alone would have written off five resolvable rows.
- **Three of the nine rows (`[6]`, `[7]`, `[8]`) share one `sourceId`.** Their declared source is a narrative review, and each names a different primary in free text. One retrieval covers all three.

### 2 · Per-row unit verdict, from the source's own sentence

According to PubMed:

| row | verdict | class | the source's own sentence |
|---|---|---|---|
| `[5]` n=41 | **patient** | **PRIMARY (stated)** | Bishop 2019, [DOI](https://doi.org/10.1097/COC.0000000000000590), abstract Methods: *"We reviewed the records of **41 consecutive patients** with localized EMC treated at our institution from 1990 to 2016."* Both committed percentages are stated in the same unit: *"There were **5 patients (12%)** with local relapse"*; *"In total, **13 patients (32%)** developed distant metastatic."* |
| `[6]` n=156 | **patient** | **SECONDARY (stated by the declared source)** | Remiszewski 2025, [DOI](https://doi.org/10.1007/s00432-025-06316-5), Radiotherapy section: *"A total of **172 patients** diagnosed between 2004 and 2012 were included in the analysis. Of the **156 evaluable patients**, 94% underwent surgery and 32% received EBRT."* Same sentence supplies the row's note and its dssText (*"94% versus 85% at 5 years"*). |
| `[7]` n=31 | ⛔ **UNKNOWN** | **UNKNOWN** | The declared source's word is **"cases"**: Remiszewski 2025, Surgery section: *"In a series of **31 cases**, the rate of local recurrence was significantly higher with involved margins than with free margins (58% versus 7%) (Giner et al.)."* The primary, **identified here for the first time** as Giner 2022, [DOI](https://doi.org/10.1007/s00428-022-03453-x), uses the same word: *"We studied **31 cases** confirmed as EMC."* Neither says patients. |
| `[8]` n=26 | **patient** | **SECONDARY (stated by the declared source)** | Remiszewski 2025, Targeted therapy section: *"the multicentre phase 2 study (Stacchiotti et al.) that evaluated pazopanib (800 mg daily) in advanced EMC in **26 patients**, **23 of whom met modified intention-to-treat criteria**."* Same passage gives the row's dssText (*"12-month and 24-month overall survival rates were 96% and 90%"*) and note (*"**Four patients** (18% [95% CI 1–36]) achieved an objective response"*). |
| `[9]` n=270 | ⛔ **UNKNOWN** | **UNKNOWN** | The source's own word is **"cases"**: Brown 2022, [DOI](https://doi.org/10.1016/j.ctarc.2022.100530), abstract Results: *"There were **270 cases** of extraskeletal myxoid chondrosarcoma reviewed in this study."* Methods repeat it: the database *"was searched for **cases** of extraskeletal myxoid chondrosarcoma diagnosed between years 2004 and 2015"*; *"**Cases** were stratified according to the anatomic site of the primary tumor."* |
| `[10]` n=87 | **patient** | **PRIMARY (stated)** | Drilon 2008, [DOI](https://doi.org/10.1002/cncr.23978), abstract Methods: *"The clinical behavior and treatment responses of **87 patients** with EMC who were seen at 2 institutions between 1975 and 2008 were examined."* |
| `[11]` n=44 | **patient** | **PRIMARY (stated)** | Brodsky 2023, [DOI](https://doi.org/10.1097/COC.0000000000000988), abstract Results: *"**Forty-four patients** with EMC were identified."* Committed metastasisPct 59 is verbatim and same-unit: *"**26 patients (59%)** ultimately developed metastatic disease"* (26/44 = 59.1%). |
| `[12]` n=42 | **patient** | **PRIMARY (stated)** | Kawaguchi 2003, [DOI](https://doi.org/10.1002/cncr.11162). Title and Methods say "cases", but the Results sentence makes the equation: *"Inadequate initial surgery was defined as a significant risk factor for local recurrence by univariate analysis of **all 42 patients** but not by the analysis of those 30 patients who had undergone wide tumor excision or amputation."* Corroborated by an exhaustive person-level partition: *"Included in the study were **20 men and 22 women**"* (20 + 22 = 42). |
| `[13]` n=40 | **tumour** | **PRIMARY (stated)** — and *not* patient | Shao 2016, [DOI](https://doi.org/10.1016/j.anndiagpath.2016.04.004), abstract: *"Of the **40 tumors**, 30 belonged to the classic subtype, whereas 9 cases were cellular, and 1 case had a rhabdoid phenotype"* (30 + 9 + 1 = 40). Repeated: *"**Twenty-four tumors (60%)** occurred in the lower limb and limb girdles"*; *"**Tumors** ranged in size from 1.5 to 19cm."* **No sentence states a patient count.** |

### 3 · The three judgement calls, shown rather than asserted

**`[12]` resolves to patient despite a "cases" title — and that is the point.** Meis-Kindblom (`cohorts[2]`, W13b's UNKNOWN) and Kawaguchi both put "cases" in the title. W13b was right to stop at Meis-Kindblom and I am right to go past Kawaguchi, because **the test is whether the source's own text equates its cases to patients, and Kawaguchi's does**: *"univariate analysis of all 42 patients"*, plus a sex partition summing to exactly 42. Meis-Kindblom's abstract never does. The title is not the test; the sentence is.

**`[13]` resolves to tumour, not patient, and I did not round it up.** The abstract's person-level facts are tempting and insufficient. *"There were 25 males and 15 females"* sums to 40, but it partitions **the 40 elements** by sex — two tumours from one patient would carry the same sex and still sum to 40, so it does **not** establish 40 distinct people. *"Apart from an adolescent, all patients were adults with a median age of 49years"* gives no count at all. What the abstract **does** state, three times, is that the 40 are tumours. So the unit is `tumour`, stated, and **the patient count for this row is UNKNOWN**. The only thing arithmetic gives — and I label it as arithmetic, not as a source statement — is that the patient count cannot exceed 40.

**`[7]` and `[9]` stop at UNKNOWN, following W13b's Meis-Kindblom precedent exactly.** Both sources' own word is "cases"; neither equates cases to patients; both full texts are on routes I did not and will not take (`[7]` Springer paywall, no PMCID; `[9]` recorded in CLOSED-WORK as publisher-403, abstract retained). For `[9]` the abstract does attach patient-level attributes to the same set (*"worse … for patients with age > 60"*) — **consistent with** one case = one patient, and precisely the reading W13 forbade. For `[7]` the pattern is the sharper one: it is an immunohistochemical/molecular pathology series, the same accessioning shape that made Meis-Kindblom UNKNOWN, and Giner's abstract interchanges the words freely (*"The EWSR1::NR4A3 rearrangement was found in **19 cases** and **7 tumors** presented the TAF15::NR4A3 fusion"*). Two UNKNOWNs is the honest answer, not a failure to try.

### 4 · Four incidental findings, recorded because they are real and not acted on because they are not mine

None of these changes a number; each is a denominator or identity fact the registry does not currently record.

| where | finding | class |
|---|---|---|
| `cohorts[6].n` | **156 is the *evaluable* subset of 172.** The declared source states both; the registry records only 156, with nothing saying it is a subset or what the other 16 were excluded for. | PRIMARY (unrecorded denominator definition) |
| `cohorts[8]` | **`n` and the row's own percentages do not share a denominator.** n=26 is enrolled; the committed ORR 18% is stated by the review on the **23-patient modified intention-to-treat set**. | PRIMARY (unrecorded denominator definition) |
| `cohorts[10]` | **`recurrencePct` 37 and `metastasisPct` 26 are not proportions of 87.** The source restricts them: *"**For patients presenting without metastases**, 37% developed local recurrence … and 26% developed distal recurrence"*, while *"Approximately 13% of patients presented with metastases."* The denominator is the metastasis-free subset. | PRIMARY (unrecorded denominator definition) |
| `cohorts[7].primaryRef` | **The Giner primary is resolvable and the registry holds it only as free text** `"Giner et al. (n=31)"`. It is PMID 36376703, [DOI](https://doi.org/10.1007/s00428-022-03453-x). This is W13's A3-class defect (one study, two identities) in a row W13's C3 check did **not** flag, because C3 only fires when a matching `registry.citations` entry already exists — and for Giner none does. | PRIMARY (identifier unresolved) |

That last one is worth a sentence on its own: **W13's C3 has a blind spot that this run found by hand.** C3 catches a prose `primaryRef` whose study *already* has a citation entry. It cannot catch a prose `primaryRef` whose study has *no* entry, which is the more common case and arguably the worse one. Three of the nine rows (`[6]`, `[7]`, `[8]`) name a primary in free text; only `[8]`'s has a citation entry, so only `[8]` fires C3. I am reporting the gap; I am not widening the check, because authoring my own acceptance criterion mid-measurement is not permitted.

### 5 · The cleared count, split honestly

W13b named the weakness in the check its own patch cleared: **W13's C1 fires on the *absence* of the `nUnit` key**, so a row clears it by writing `nUnit: "UNKNOWN"` — by declaring ignorance rather than resolving it. Acting on that, here is my patch's effect **split, never summed**:

| bucket | rows | count |
|---|---|---|
| **RESOLVED — unit stated by the row's own primary source** | `[5]` patient, `[10]` patient, `[11]` patient, `[12]` patient, `[13]` **tumour** | **5** |
| **RESOLVED — unit stated only by the row's declared *secondary* source; the primary was not read** | `[6]` patient (Kemmerer not retrieved), `[8]` patient (Stacchiotti unrecovered per CLOSED-WORK, not attempted) | **2** |
| **DOCUMENTED AS UNRESOLVABLE — `nUnit: "UNKNOWN"`** | `[7]` (Giner, "cases", Springer paywall), `[9]` (CTARC 2022, "cases", publisher 403 per CLOSED-WORK) | **2** |
| **C1 findings cleared by the patch** | | **9 of 9** |

**Nine cleared is not nine resolved.** It is 5 resolved against a primary, 2 resolved against a secondary attestation only, and 2 documented as unresolvable. I am giving the three-way split rather than W13b's two-way one because the secondary-attested rows genuinely are a distinct epistemic state: their declared source states the unit, but a review demonstrably can misdescribe a primary — W13b caught Chiusole doing exactly that to Meis-Kindblom's denominators. `nUnitObserved: true` on `[6]` and `[8]` means *this row's declared source states it*, and each `nUnitEvidence` says in plain words that the primary was not read.

Across both patches the registry-wide position is: **11 rows resolved (10 patient, 1 tumour), 3 documented-unresolvable (`[2]`, `[7]`, `[9]`), 0 rows left with no verdict.**

### 6 · W13b's live regression — **confirmed, still happening, and worse**

W13b reported that after `103ff76f` made the campaign reports tracked, W13's C12 check began firing on the reports' own prose. **I confirm it is still happening at `b9a0257e`, and the count has grown.**

| commit | total findings | violations | annotated guards | files |
|---|---|---|---|---|
| `92abbcb` (W13's run) | 42 | 41 | 1 | 3 |
| `103ff76f` (W13b's run) | 50 | 45 | 5 | 6 |
| **`b9a0257e` (this run)** | **50** | **45** | **5** | **6** |

The four C12 violations at `b9a0257e`, verbatim from the run:

```
research/autonomy/opus-capacity-campaign-20260908/reports/W13-provenance-identity-contract.md :: line 131
research/autonomy/opus-capacity-campaign-20260908/reports/W13-provenance-identity-contract.md :: line 212
research/autonomy/opus-capacity-campaign-20260908/reports/W01b-brenca-accession-recovery.md :: line 133
research/autonomy/opus-capacity-campaign-20260908/reports/W05-patient-independence-audit.md :: line 140
```

**This is a scope bug, not a finding.** Every one of these lines is a campaign report *quoting or describing* a unit-word defect — W13's own report being flagged for the sentences in which it documents the defect is the clearest possible demonstration. A validator that flags a report for describing a defect is measuring the wrong corpus. **If this validator is ever adopted as a gate it needs a scope exclusion for `research/autonomy/opus-capacity-campaign-20260908/`** (or, more generally, for `research/autonomy/*/reports/`). **PROPOSED (NOT RUN)** — I did not modify the checker, and doing so would have been changing a check mid-measurement.

Note that the eight campaign-report false positives are also why my patch's *totals* look different from W13b's: W13b measured 42 → 34 at `92abbcb`; I measure 50 → 33 at `b9a0257e`. The eight-finding difference is entirely this regression, not my patch. The **class** figures are unaffected and are the ones to read: **C1 goes 14 → 9 → 0.**

## Validation evidence

Environment for every run: Linux 6.18.44-fc-v24, Python 3.11.15, Node (repo-provided), cwd `/tmp/claude-0/w13c`, exit codes as returned by the shell.

### RUN 1 — W13's validator against the real repository at current HEAD

Validator extracted verbatim by regex from W13's committed report (196 lines, matching W13's stated 196) — no retyping, no modification.

```
$ python3 validate_identity_contract.py /home/user/Rare-cancers
TOTAL FINDINGS: 50 across 6 files (45 violations, 5 annotated guards)
REAL_EXIT=1
```

### RUN 2 — scratch mirror, calibrated to byte-identity BEFORE any patch was measured

W13b built its mirror with `git add -A`, which made untracked worker reports tracked and manufactured 8 phantom findings it had to diagnose. I avoided that failure mode by construction: I built the mirror from **`git archive HEAD`**, which emits exactly the tracked tree, then initialised a fresh repo inside it so `git ls-files` matches.

```
$ git -C /home/user/Rare-cancers archive HEAD | tar -x -C mirror
$ cd mirror && git init -q . && git add -A && git commit -qm mirror
mirror files: 7638   real tracked: 7638
$ comm -3 <(git ls-files|sort) <(git -C /home/user/Rare-cancers ls-files|sort)
                                        # (no output — zero files either direction)
$ python3 validate_identity_contract.py /tmp/claude-0/w13c/mirror
TOTAL FINDINGS: 50 across 6 files (45 violations, 5 annotated guards)
MIRROR_EXIT=1
$ diff <(sed 's#/tmp/claude-0/w13c/mirror##' runB.txt) runA.txt && echo IDENTICAL
CALIBRATION: IDENTICAL
```

**The mirror's output is byte-identical to the real repository's.** Only then did I measure any delta.

### RUN 3 — the patches, measured in three states

```
state 1  baseline                        ### C1-COUNT-UNIT-UNDECLARED  (14)
         TOTAL FINDINGS: 50 across 6 files (45 violations, 5 annotated guards)   EXIT=1

state 2  + W13b patch (cohorts[0..4])    ### C1-COUNT-UNIT-UNDECLARED  (9)
         TOTAL FINDINGS: 42 across 6 files (37 violations, 5 annotated guards)   EXIT=1

state 3  + W13c patch (cohorts[5..13])   (C1 absent = all 14 cleared)
         TOTAL FINDINGS: 33 across 6 files (28 violations, 5 annotated guards)   EXIT=1
```

Header diff, baseline → state 3, verbatim:

```
$ diff <(grep '^### ' runB.txt) <(grep '^### ' runD.txt)
1d0
< ### C1-COUNT-UNIT-UNDECLARED  (14)
6d4
< ### C2-DENOM-UNEXPLAINED  (3)
```

**My patch clears 9 of the 9 remaining C1 findings — the entire C1 class is eliminated, and no other check changed in either direction.** The validator still exits 1 on 28 surviving violations. **I did not weaken any check to produce this number**: the validator ran unmodified, extracted verbatim from W13's report, and its output on the unpatched mirror was proven identical to the real repository first.

### RUN 4 — the patch damages nothing

```
$ node scripts/validate-registry.mjs        # real repo, unpatched
OK - EMC clinical registry valid: 25 citation(s), 14 cohort(s). 0 warning(s).
EXIT=0
$ node scripts/validate-registry.mjs        # mirror, PATCHED (W13b + W13c)
OK - EMC clinical registry valid: 25 citation(s), 14 cohort(s). 0 warning(s).
EXIT=0
```

Structural diff of unpatched vs fully patched registry:

```
ADDED 45   CHANGED 0   REMOVED 0
```

45 = W13b's 18 + my 27 (9 rows × 3 keys). **Purely additive: no committed value, key order, or count is altered.**

### RUN 5 — the strict-C1 split, measured not asserted

A **separate, additional** script that reads the patched registry and reports the split. It does not touch and was not used to score the validator above.

```
$ python3 c1_strict.py mirror/research/data/emc-clinical-registry.json
RESOLVED (unit stated by the row's declared source): 11
   cohorts[0 ] Localised at diagnosis, surgically treated    -> patient
   cohorts[1 ] Metastatic at diagnosis                       -> patient
   cohorts[3 ] US Sarcoma Collaborative database             -> patient
   cohorts[4 ] European two-institution series (Chiusole)    -> patient
   cohorts[5 ] Localised, single-institution series          -> patient
   cohorts[6 ] Localised, US SEER population                 -> patient
   cohorts[8 ] Advanced disease on pazopanib                 -> patient
   cohorts[10] Two-referral-center long-term series (Drilon) -> patient
   cohorts[11] Single-institution series (U Michigan)        -> patient
   cohorts[12] Japanese multi-institutional series           -> patient
   cohorts[13] Chinese series                                -> tumour
DOCUMENTED AS UNRESOLVABLE (nUnit=UNKNOWN): 3
   cohorts[2 ] Long-term outcome series (Meis-Kindblom)
   cohorts[7 ] Local recurrence by surgical margin
   cohorts[9 ] SEER overall-survival series
STILL FAILING STRICT C1: 0 []
STRICT_EXIT=1
```

Note that **strict C1 exits 1 even with all 14 rows keyed** — which is the whole point of the strengthening: three rows are documented, not resolved, and a gate that returns 0 there would be lying.

### PROPOSED (NOT RUN)

- **Applying the patch to `research/data/emc-clinical-registry.json`.** Not run, and not mine to run: the clinical registry is protected state under `systems/POLICY-evidence.md` and this worker is read-only. Routed below.
- **Adopting the strengthened C1** (`c1_strict.py`, RUN 5) into the validator. A **strengthening**, offered as a proposal. I did not alter the checker I measured against.
- **Scope exclusion for `research/autonomy/opus-capacity-campaign-20260908/` in C12.** Required before this validator can be a gate. Not run — not my lane, and modifying the checker mid-measurement is not permitted.
- **Retrieving the Kemmerer primary behind `cohorts[6]`** to upgrade it from secondary-attested to primary-stated. Not run — outside this task's nine-row scope, and the row is `pool: false`.
- `scripts/preflight.sh`. Not run — the brief forbids it.
- `scripts/tests/test_no_hand_authored_json_has_a_duplicate_key.py` — W13b reported this exits 1 for `ModuleNotFoundError: No module named 'pytest'` on the **unpatched** repo. I did not re-run it. **Unrun, not passed.**

## The routed patch

**ROUTED, NOT APPLIED.** Owner: whoever owns `research/data/emc-clinical-registry.json` under `systems/POLICY-evidence.md`. It **extends** W13b's patch and does not modify or replace it — apply W13b's first, then this. Purely additive: `nUnit` / `nUnitObserved` / `nUnitEvidence` on `cohorts[5..13]`, in W13b's exact key shape, inserted immediately after `n` so committed key order is preserved. Every row asserts the `n` and `sourceId` it keys off, so it fails loudly rather than silently patching the wrong row if the registry has moved.

```python
#!/usr/bin/env python3
"""W13c proposed patch: nUnit / nUnitObserved / nUnitEvidence on registry.cohorts[5..13].
Extends W13b's patch (cohorts[0..4]) in the same purely additive form. ROUTED, NOT APPLIED —
the clinical registry is protected state under systems/POLICY-evidence.md and this worker is
read-only. This script exists so the registry owner can reproduce the exact edit and so W13's
validator can be measured against it in a byte-calibrated scratch mirror.

Every quoted sentence is the SOURCE'S OWN, retrieved 2026-09-08 via the PubMed MCP tools.
No unit is inferred: where the source's own word is "cases" and no sentence equates cases to
patients, the value written is the string "UNKNOWN".
"""
import json, sys, collections
p = sys.argv[1]
d = json.load(open(p), object_pairs_hook=collections.OrderedDict)
C = d["registry"]["cohorts"]

def put(obj, key, val, after):
    """Insert key immediately after `after`, preserving committed key order."""
    items = list(obj.items()); obj.clear()
    for k, v in items:
        obj[k] = v
        if k == after:
            obj[key] = val

def unit(i, n, sourceId, u, observed, evidence):
    assert C[i]["n"] == n and C[i]["sourceId"] == sourceId, f"cohorts[{i}] has moved"
    put(C[i], "nUnit", u, "n")
    put(C[i], "nUnitObserved", observed, "nUnit")
    put(C[i], "nUnitEvidence", evidence, "nUnitObserved")

# --- cohorts[5] --------------------------------------------- PRIMARY SOURCE, STATED: patient
unit(5, 41, "bishop2019", "patient", True,
     "STATED by the row's own primary source. Bishop et al. 2019, Am J Clin Oncol 42(10):744-8, "
     "PMID 31436747, doi 10.1097/COC.0000000000000590, abstract Methods: \"We reviewed the records "
     "of 41 consecutive patients with localized EMC treated at our institution from 1990 to 2016.\" "
     "The same abstract states this row's two committed percentages in the same unit: \"There were "
     "5 patients (12%) with local relapse\" (= recurrencePct 12) and \"In total, 13 patients (32%) "
     "developed distant metastatic\" (= metastasisPct 32), and medianFollowupMonths 94 is verbatim "
     "(\"Median follow-up time was 94 months\"). Unit is stated in the abstract, so no full text "
     "was needed. Retrieved 2026-09-08 via PubMed MCP get_article_metadata.")

# --- cohorts[6] ------------------------------ DECLARED (SECONDARY) SOURCE, STATED: patient
unit(6, 156, "remiszewski2025", "patient", True,
     "STATED by this row's DECLARED source, which is the secondary one. Remiszewski et al. 2025, "
     "J Cancer Res Clin Oncol, PMC12504171, PMID 41055792, doi 10.1007/s00432-025-06316-5, "
     "Radiotherapy section: \"A total of 172 patients diagnosed between 2004 and 2012 were "
     "included in the analysis. Of the 156 evaluable patients, 94% underwent surgery and 32% "
     "received EBRT.\" That sentence also supplies this row's committed note (94% surgery, 32% "
     "radiotherapy) and its dssText (\"94% versus 85% at 5 years\"). CAVEAT, recorded not hidden: "
     "provenance is \"secondary\" and the primary (Kemmerer et al.) has NOT been retrieved or read "
     "by this repository, so this is a review's word for the primary's unit, not the primary's own "
     "sentence. DENOMINATOR DEFINITION, previously unrecorded: 156 is the EVALUABLE subset of the "
     "172 patients included; the registry records only 156. Retrieved 2026-09-08 via PubMed MCP "
     "get_full_text_article.")

# --- cohorts[7] ------------------------------------------------------------------- UNKNOWN
unit(7, 31, "remiszewski2025", "UNKNOWN", False,
     "UNKNOWN. Neither the declared source nor the primary says \"31 patients\". Declared source "
     "Remiszewski et al. 2025 (PMC12504171, doi 10.1007/s00432-025-06316-5), Surgery section: "
     "\"In a series of 31 cases, the rate of local recurrence was significantly higher with "
     "involved margins than with free margins (58% versus 7%) (Giner et al.)\" — the word is "
     "\"cases\". The primary, which this registry names only as the free text \"Giner et al. "
     "(n=31)\", is IDENTIFIED HERE for the first time: Giner et al. 2022, Virchows Arch "
     "482(2):407-417, PMID 36376703, doi 10.1007/s00428-022-03453-x, titled \"...an "
     "immunohistochemical and molecular analysis of 31 cases\"; its abstract's own sentence is "
     "\"We studied 31 cases confirmed as EMC\" and it likewise never equates cases to patients "
     "(it interchanges the words freely: \"The EWSR1::NR4A3 rearrangement was found in 19 cases "
     "and 7 tumors presented the TAF15::NR4A3 fusion\"). This is an immunohistochemical/molecular "
     "pathology series, the same accessioning pattern for which W13b recorded cohorts[2] "
     "(Meis-Kindblom) as UNKNOWN: one patient's primary and a later recurrence can arrive as two "
     "cases. The primary's full text is behind a Springer paywall (no PMCID; the publisher route "
     "is recorded blocked in this repository's egress inventory) and was not attempted. "
     "Retrieved 2026-09-08 via PubMed MCP get_full_text_article and get_article_metadata.")

# --- cohorts[8] ------------------------------ DECLARED (SECONDARY) SOURCE, STATED: patient
unit(8, 26, "remiszewski2025", "patient", True,
     "STATED by this row's DECLARED source, which is the secondary one. Remiszewski et al. 2025 "
     "(PMC12504171, doi 10.1007/s00432-025-06316-5), Targeted therapy section: \"The notable "
     "exception is the multicentre phase 2 study (Stacchiotti et al.) that evaluated pazopanib "
     "(800 mg daily) in advanced EMC in 26 patients, 23 of whom met modified intention-to-treat "
     "criteria.\" The same passage states this row's dssText in the same unit (\"The 12-month and "
     "24-month overall survival rates were 96% and 90%\") and its note (\"Four patients (18% "
     "[95% CI 1-36]) achieved an objective response\", \"Median PFS was 19 months\"). CAVEAT, "
     "recorded not hidden: the Stacchiotti 2019 primary full paper is recorded UNRECOVERED in the "
     "campaign CLOSED-WORK inventory (abstract only); no route to it was attempted or replayed, "
     "so this is the review's word, not the primary's own sentence. DENOMINATOR DEFINITION, "
     "previously unrecorded: n=26 is the ENROLLED count, while the committed response figures "
     "(ORR 18%) are stated by the review on the 23-patient modified intention-to-treat set, so "
     "n and the percentages in this row's note do not share a denominator. Retrieved 2026-09-08 "
     "via PubMed MCP get_full_text_article.")

# --- cohorts[9] ------------------------------------------------------------------- UNKNOWN
unit(9, 270, "seer270_2022", "UNKNOWN", False,
     "UNKNOWN — the source's own word for the 270 is \"cases\", not \"patients\". Brown, Rakoczy "
     "& Pretell-Mazzini 2022, Cancer Treat Res Commun 31:100530, PMID 35144048, doi "
     "10.1016/j.ctarc.2022.100530, abstract Results: \"There were 270 cases of extraskeletal "
     "myxoid chondrosarcoma reviewed in this study, which were diagnosed most frequently in the "
     "lower limb or hip of older adult males.\" Its Methods use the same word: the SEER database "
     "\"was searched for cases of extraskeletal myxoid chondrosarcoma diagnosed between years 2004 "
     "and 2015\" and \"Cases were stratified according to the anatomic site of the primary "
     "tumor.\" The abstract does attach patient-level attributes to the same set (\"worse ... for "
     "patients with age > 60\"), which is CONSISTENT WITH but does not state one case = one "
     "patient. NOT RESOLVABLE ON A PERMITTED ROUTE: this is the paper recorded in the campaign "
     "CLOSED-WORK inventory as \"CTARC 2022 ... abstract retained; latest publisher 403, methods "
     "unrecovered\". Only the retained abstract was used; no denied route was replayed. NOTE ON "
     "IDENTITY: this is a DIFFERENT paper from cohorts[3]'s ussc2022 (Gusho et al., PMID "
     "35962783), which W13b retrieved successfully. Abstract retrieved 2026-09-08 via PubMed MCP "
     "get_article_metadata.")

# --- cohorts[10] -------------------------------------------- PRIMARY SOURCE, STATED: patient
unit(10, 87, "drilon2008", "patient", True,
     "STATED by the row's own primary source. Drilon et al. 2008, Cancer 113(12):3364-71, PMID "
     "18951519, PMC2779719, doi 10.1002/cncr.23978, abstract Methods: \"The clinical behavior and "
     "treatment responses of 87 patients with EMC who were seen at 2 institutions between 1975 "
     "and 2008 were examined.\" Unit is stated in the abstract, so no full text was needed. "
     "DENOMINATOR DEFINITION, previously unrecorded: this row's recurrencePct 37 and "
     "metastasisPct 26 are NOT proportions of the 87. The source's sentence restricts them: \"For "
     "patients presenting without metastases, 37% developed local recurrence (median time of 3.3 "
     "years) and 26% developed distal recurrence\", while \"Approximately 13% of patients "
     "presented with metastases\" — so the percentage denominator is the metastasis-free subset, "
     "not n. Retrieved 2026-09-08 via PubMed MCP get_article_metadata.")

# --- cohorts[11] -------------------------------------------- PRIMARY SOURCE, STATED: patient
unit(11, 44, "uMich2023", "patient", True,
     "STATED by the row's own primary source. Brodsky et al. 2023, Am J Clin Oncol 46(4):172-177, "
     "PMID 36825763, doi 10.1097/COC.0000000000000988, abstract Results: \"Forty-four patients "
     "with EMC were identified.\" This row's committed metastasisPct 59 is stated in the same "
     "unit and is verbatim: \"26 patients (59%) ultimately developed metastatic disease\" "
     "(26/44 = 59.1%). Unit is stated in the abstract, so no full text was needed. "
     "Retrieved 2026-09-08 via PubMed MCP get_article_metadata.")

# --- cohorts[12] -------------------------------------------- PRIMARY SOURCE, STATED: patient
unit(12, 42, "japan2003", "patient", True,
     "STATED by the row's own primary source, which explicitly equates its cases to patients. "
     "Kawaguchi et al. 2003, Cancer 97(5):1285-92, PMID 12599237, doi 10.1002/cncr.11162. The "
     "TITLE and the Methods use \"cases\" (\"Forty-two cases of EMC, which had been identified "
     "from files of eight affiliated hospitals...\"), but the abstract's own Results sentence "
     "makes the equation the Meis-Kindblom abstract never makes: \"Inadequate initial surgery was "
     "defined as a significant risk factor for local recurrence by univariate analysis of all 42 "
     "PATIENTS but not by the analysis of those 30 patients who had undergone wide tumor excision "
     "or amputation.\" It is corroborated by an exhaustive person-level partition of the same set: "
     "\"Included in the study were 20 men and 22 women\" (20 + 22 = 42). This row is therefore "
     "resolved to patient DESPITE a \"cases\" title — the title alone is not the test. Retrieved "
     "2026-09-08 via PubMed MCP get_article_metadata.")

# --- cohorts[13] --------------------------------------------- PRIMARY SOURCE, STATED: tumour
unit(13, 40, "china2016", "tumour", True,
     "STATED by the row's own primary source, and the stated unit is TUMOUR, not patient. Shao et "
     "al. 2016, Ann Diagn Pathol 23:14-20, PMID 27402218, doi 10.1016/j.anndiagpath.2016.04.004. "
     "The abstract partitions exactly this set as tumours: \"Of the 40 tumors, 30 belonged to the "
     "classic subtype, whereas 9 cases were cellular, and 1 case had a rhabdoid phenotype\" "
     "(30 + 9 + 1 = 40), and repeats the unit: \"Twenty-four tumors (60%) occurred in the lower "
     "limb and limb girdles\", \"Tumors ranged in size from 1.5 to 19cm (mean, 7cm)\". The same "
     "sentence interchanges \"tumors\" and \"cases\". THE PATIENT COUNT IS NOT STATED. The "
     "abstract's person-level facts do not supply one: \"There were 25 males and 15 females\" "
     "partitions the 40 elements by sex but does not establish 40 distinct people (two tumours "
     "from one patient would carry the same sex and still sum to 40), and \"Apart from an "
     "adolescent, all patients were adults with a median age of 49years\" gives no count. "
     "Arithmetic bound only, not a source statement: the patient count cannot exceed 40. This "
     "row's committed dssText (5-/7-year survival 71%/60%) is therefore a survival proportion "
     "whose denominator unit is tumours as stated. Retrieved 2026-09-08 via PubMed MCP "
     "get_article_metadata.")

json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
open(p, "a").write("\n")
print("W13c patch applied to", p)
```

### The strict-C1 measurement script (proposed strengthening, used only for the split above)

```python
#!/usr/bin/env python3
"""PROPOSED STRENGTHENING of W13's C1 (measurement only; the validator measured against was
NOT modified). W13's C1 fires on the ABSENCE of the `nUnit` key, so a row clears it by writing
nUnit:"UNKNOWN" — declaring ignorance rather than resolving it. This reports the honest split."""
import json, sys
C = json.load(open(sys.argv[1]))["registry"]["cohorts"]
res, unk, bad = [], [], []
for i, c in enumerate(C):
    u, o, e = c.get("nUnit"), c.get("nUnitObserved"), (c.get("nUnitEvidence") or "")
    if u is None: bad.append((i, "no nUnit key"))
    elif u == "UNKNOWN": unk.append((i, c["label"]))
    elif o is True and len(e) > 40: res.append((i, c["label"], u))
    else: bad.append((i, "nUnit=%r but observed=%r / evidence %dc" % (u, o, len(e))))
print("RESOLVED (unit stated by the row's declared source):", len(res))
for i, l, u in res: print("   cohorts[%-2d] %-45s -> %s" % (i, l[:45], u))
print("DOCUMENTED AS UNRESOLVABLE (nUnit=UNKNOWN):", len(unk))
for i, l in unk: print("   cohorts[%-2d] %s" % (i, l))
print("STILL FAILING STRICT C1:", len(bad), bad)
sys.exit(1 if (unk or bad) else 0)
```

## Limitations

- **This run cannot move any headline number, and I said so before I started.** All nine rows are `pool: false`. W13b's judgement that this is the lower-value successor was correct and the measurement confirms it: `n` enters no §2.2 arithmetic for any of these rows.
- ⚠ **`cohorts[13]` is `tumour`, and the registry's `n` for that row therefore does not mean what the other twelve rows' `n` means.** Ten rows are patients, one is tumours, three are UNKNOWN. Nothing downstream currently distinguishes them, and this patch only records the distinction — it does not make any consumer honour it.
- **`cohorts[6]` and `cohorts[8]` rest on a *review's* word for a primary this repository has not read.** W13b demonstrated that a review can misdescribe a primary's design and denominators. I have marked both `nUnitObserved: true` because their **declared** source states the unit, and put the caveat in plain words inside each `nUnitEvidence`. A reader who wants primary-stated units for those two rows must retrieve Kemmerer (open) and Stacchiotti 2019 (recorded unrecovered).
- **`cohorts[7]` and `cohorts[9]` are UNKNOWN and no further work in this sandbox resolves them.** Giner's full text is a Springer paywall; CTARC 2022's is a recorded publisher 403. I attempted neither.
- **Seven of nine rows rest on a single abstract each.** For those seven the unit is stated *in* the abstract, so no full text was needed — but an abstract is a smaller evidence surface than a full text, and a full text could in principle qualify a unit an abstract states plainly. I did not check that, because the brief's standard is the source's own sentence and I have it.
- **The four incidental denominator findings (§4) are recorded, not repaired.** They are the registry owner's to act on, and two of them (`[8]`, `[10]`) mean a committed percentage in a row's `note`/`dssText` has a denominator different from that row's `n` — which is a W13 C2-class defect that C2 does not currently detect, because C2 only inspects structured `denom` fields, not prose percentages.
- **W13's C12 scope bug is confirmed but unfixed**, and it inflates every total in this report by 8 findings relative to W13's original measurement. The class figures (C1 14 → 0) are unaffected.
- ⛔ **No clinical, efficacy, safety, prognostic or selectivity claim is made or implied.** Every finding concerns how a count is *recorded*, never whether it is *right*. Adopting this patch changes no scientific conclusion.
- I did not run `scripts/preflight.sh` (forbidden by the brief) and did not re-run the pytest-dependent duplicate-key test W13b found unrunnable. **Unrun, not passed.**

## Stop condition

**Set:** a per-row unit verdict with quoted evidence or an honest UNKNOWN for all nine cohorts; a routed additive patch measured against a byte-calibrated mirror; a cleared count split into resolved versus documented-unresolvable. **Met.**

Nine of nine rows carry a verdict: **seven resolved** (six to `patient`, one to `tumour`), of which five are stated by the row's own primary source and two only by its declared secondary source; **two documented as unresolvable** (`[7]` Giner, `[9]` CTARC 2022), each with the source's own contradicting word "cases" quoted and the unrecoverable route named. Patch routed and not applied, purely additive (27 keys added, 0 changed, 0 removed), verified in a mirror proven byte-identical to the real repository to clear **9 of the 9 remaining C1 findings** — **the C1 class is now empty** — with the validator still exiting 1 on 28 surviving violations and the incumbent `validate-registry.mjs` still exiting 0.

## Tool-call and wall-clock count actually used

**20 tool calls; 4 minutes 56 seconds wall clock** (02:17:35Z → 02:22:31Z). Well inside the ~40/~40 target.

## Next concrete action

**No high-value successor remains in this lane on the unit question — C1 is finished, and I would rather say that than manufacture a tenth row.**

The genuinely open items this run surfaced belong elsewhere, and I name them so they are not lost:

1. **For the registry owner (highest value, unchanged from W13b):** decide and record whether §2.2's pool may mix whole-stratum denominators with assessability-restricted ones, given W13b's measured −2.55 pp / −4.96 pp effect. Still a methods decision, not a worker's fix.
2. **For the campaign coordinator (small, mechanical, blocking):** add the scope exclusion for `research/autonomy/opus-capacity-campaign-20260908/` to C12 before this validator is considered as a gate. Right now it fails on the reports that describe the defect it checks for.
3. **For a lane-13 successor, if one is wanted and the bar is lower:** the four §4 incidental findings are a coherent finite job — three unrecorded denominator definitions (`[6]` 156-of-172, `[8]` 26-vs-23-mITT, `[10]` metastasis-free subset) and one resolvable primary the registry holds only as free text (Giner 2022, PMID 36376703). It is bookkeeping of the same kind as this run and I would rate it below both items above.

---

result: W13c resolved the unit of `n` for all nine remaining EMC cohorts (`cohorts[5..13]`) from the sources' own sentences via PubMed — seven resolved (`[5]` 41, `[6]` 156, `[8]` 26, `[10]` 87, `[11]` 44, `[12]` 42 = patients; `[13]` 40 = **tumours**, patient count not stated) and two documented as unresolvable (`[7]` Giner "31 cases", Springer paywall; `[9]` CTARC 2022 "270 cases", publisher 403 per CLOSED-WORK, abstract-only) — delivering a purely additive routed patch (27 keys, 0 values changed) that in a byte-calibrated scratch mirror clears **9 of 9 remaining C1 findings, emptying the C1 class (14 → 0 across W13b+W13c)** while the validator still exits 1 on 28 violations and the incumbent `validate-registry.mjs` stays exit 0; it also identified the previously free-text Giner primary (PMID 36376703), found three unrecorded denominator definitions (`[6]` 156-of-172 evaluable, `[8]` ORR on 23-patient mITT not 26, `[10]` percentages on the metastasis-free subset not 87), and confirmed W13's C12 scope bug is still live at HEAD `b9a0257e` (4 false positives on the campaign's own reports, including W13's); nothing was written to the repository.
