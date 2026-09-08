> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git working tree; the coordinator is the sole collector.
> Per-child runtime model evidence, extracted by the coordinator from the child transcript:
> `"model":"claude-opus-5"` (OBSERVED, not self-report).

---

Repo verified clean of my writes (`git status --porcelain | grep -c W08` → 0); script ran exit 0; question is specified and the description computed. Report below.

**Summary (330 words).** Lane 8 asked for a new, feasible EMC disease-course/surveillance question. The prior-work check confirmed what is closed: the aggregate censoring observation (row AUT-065, `research/manuscripts/care-delivery/emc-care-delivery-endpoint-decision.md`, `research/modalities/emc-recurrence-timing.json`) already compares one cohort's upper quartile (63.5 mo) against its own median follow-up (38 mo) using **printed cohort summary statistics** — 2 cohorts, 4 medians, 3 IQRs — and that artifact states its own blocker: no reachable series prints a time-to-recurrence curve with numbers at risk, so **no hazard and therefore no schedule**. RT/IPD KM reconstruction, trial discoverability and the ICD-O registry paper are separately closed. I did not replay any of them.

The genuinely open, non-duplicative unit is **individual patients rather than cohort summaries**. Question pursued: across the fully enumerable PubMed case-report frame for EMC, what is the distribution of the interval from primary diagnosis/surgery to the *first documented distant or regional metastasis*, and how many source-traceable patients have that event beyond 5 and 10 years?

Data availability was verified, not assumed: the frame has `total_count = 84`, and I retrieved all 84 abstracts through the PubMed MCP server (direct NCBI eutils remains denied — CONNECT 403 — and I did not retry that route). A regex screen over 60 on-disk abstracts flagged 35 with interval-like sentences; hand adjudication over all 84 yielded **10 patient-events with an exact interval**, each carrying its verbatim source sentence.

Computed description (exact set, n=10, months): 2.8, 10, 10, 16, 26, 34, 48, 60, 74, 240. Median 30; Q1 11.5, Q3 57. **2/10 events beyond 60 months, 1/10 beyond 120 months.** Two further imprecise events and two occult-primary patients (metastasis documented *before* the primary) are recorded separately.

This is a description of the published record, not of the disease. Case reports over-select unusual courses, there is no denominator, and competing risks are unobserved — so no rate, no hazard, no risk and no surveillance duration follows.

---

## Worker

- **Worker ID:** W08. **Lane 8** — a new feasible EMC disease-course / surveillance question.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My system prompt states I am powered by "Opus 5", exact model ID `claude-opus-5`. I did not observe the served model and do not assert it as fact; the coordinator should extract the actual per-child runtime model from the transcript.
- **Start-of-run env/date: NOT CAPTURED.** Honest gap — the dispatch as originally issued did not require it and the coordinator's correction arrived mid-run. Only the end-of-run capture exists.
- **End of run, `date -u`:** `Tue Sep  8 01:56:54 UTC 2026`
- **End of run, `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`** (verbatim, long proxy/no_proxy lines elided as noted):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,...            [elided: proxy host list]
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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,...  [elided]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 ...  [elided]
NO_PROXY=localhost,127.0.0.1,::1,...            [elided]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,...  [elided]
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**Write-isolation compliance.** Before the coordinator's correction I had created one file, `research/autonomy/opus-capacity-campaign-20260908/code/W08/frame_pmids.txt`. I deleted it (`rm -f` plus `rmdir` of the now-empty `code/W08/`) and re-read the updated `COMMON-BRIEF.md`. Verified afterwards: `git status --porcelain | grep -c W08` → `0`. All execution moved to `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/W08/`. No git write operation of any kind was performed.

---

## Question

**Pursued:** Across the fully enumerable PubMed case-report literature on extraskeletal myxoid chondrosarcoma, what is the empirical distribution of the interval, in months, from primary diagnosis or primary surgery to the **first documented distant or regional metastasis**, at the level of the individual published patient — and how many source-traceable patients have that first event beyond 60 and beyond 120 months?

Formal specification:

| element | specification |
|---|---|
| **Population** | Patients with EMC histology reported in an article indexed in PubMed as `Case Reports[Publication Type]` and matching `extraskeletal myxoid chondrosarcoma AND (metastasis OR recurrence)`. This is a **literature frame**, not a patient population. |
| **Unit of analysis** | One published patient-event (not one article; two articles here contribute two patients each). |
| **Covariate/exposure** | None. This is descriptive; no exposure is contrasted. |
| **Outcome** | First distant or regional metastasis documented in the abstract, with an explicit numeric elapsed interval. |
| **Estimand** | The empirical distribution, and the count/proportion beyond thresholds T ∈ {24, 60, 120} months, **of documented events among published cases**. Explicitly *not* a cumulative incidence, hazard, or risk in EMC patients. |
| **Exact public data** | PubMed, via the PubMed MCP server, query above, retrieved 2026-09-08; `total_count = 84`. |
| **Sample size actually available** | 84 abstracts retrieved (100% of the frame). 10 patient-events met the exact-interval inclusion rule; 2 more with imprecise intervals; 2 occult-primary patients in a separate category. |
| **Credible validation** | Every included row carries the verbatim abstract sentence and its PMID/DOI, so any reader can re-read the source and re-adjudicate. A machine screen (`screen_intervals.py`) is reported separately from the hand adjudication, so screen recall and adjudication judgement are independently checkable. |
| **Falsification condition** | If an independent adjudicator, applying the stated inclusion rule to the same 84 abstracts, produces an included set differing by more than one patient-event, or if any quoted sentence does not appear verbatim in its cited abstract, the table is wrong. |
| **Stop condition** | One fully specified, non-duplicative question with data availability *verified by retrieval* plus a first computed description — or a precise statement of what blocked it. |

**Why it is open.** The closed AUT-065 observation operates on **cohort summary statistics** (medians, one IQR, follow-up medians) and its own artifact records the barrier: `⛔_no_hazard_and_therefore_no_schedule` — "What is printed is a median and, once, an IQR: three points". Nothing in the repository holds a **patient-level** interval census assembled from the case literature. That is a different data object with a different estimand, and it is reachable.

---

## Prior-work check

Commands actually run (from `/home/user/Rare-cancers`):

```
rg -n -i "conditional recurrence|surveillance|follow.up interval|late recurrence|metastas|disease course|hazard" research/ --glob '!.git' -l | head -60
ls -R research/manuscripts/care-delivery/
sed -n 1,120p research/manuscripts/care-delivery/emc-care-delivery-endpoint-decision.md
grep -n -i -B3 -A45 "RT-SURVEILLANCE" research/manuscripts/care-delivery/emc-care-delivery-endpoint-decision.md
grep -n -i -A40 "AUT-065" research/manuscripts/care-delivery/emc-care-delivery-endpoint-decision.md
ls research/modalities/ | grep -i -E "site-curation|recurrence|ipd-surv|case"
python3 -c "json walk of research/modalities/emc-recurrence-timing.json"
ls research/autonomy/clinical-methods-checkpoints-2026-09-07     # -> does not exist (UNKNOWN, not absence of the checkpoint decision)
git branch -a ; find . -type d -name "literature*"
```

What they showed, and what I am therefore **not** replaying:

1. **AUT-065 / RT-SURVEILLANCE is decided and written** (`research/manuscripts/care-delivery/emc-care-delivery-endpoint-decision.md`, §0 table row): *"WRITE IT, ONE PARAGRAPH. The within-cohort censoring observation is confound-free and needs no model. One cohort, one clock: upper quartile 63.5 months against its own median follow-up of 38."* I am not restating that observation.
2. **`research/modalities/emc-recurrence-timing.json`** holds the aggregate data: 2 cohorts, `events_with_a_printed_median: 4`, `events_with_a_printed_iqr: 3`, `events_with_no_timing_at_all: 1`; Masunaga 2025 n=134, median time to distant metastasis 16 mo, median follow-up 38 mo; Chiusole 2020 n=49, 70.8 mo, median follow-up 72 mo. It explicitly refuses pooling (`⛔_nothing_is_pooled`, citing POLICY-evidence 2.4) and refuses any schedule (`⛔_no_hazard_and_therefore_no_schedule`). **My work uses none of these numbers and pools nothing with them.**
3. The same file names the open gap I am addressing from a different direction: *"RT-SURVEILLANCE stays open against a series printing a time-to-recurrence curve with a numbers-at-risk row … which no reachable series prints."* I did **not** attempt to manufacture such a curve, and I did **not** digitise any KM figure — RT-IPD-SURVIVAL is closed and I did not touch `emc-ipd-survival.json`.
4. **CLOSED-WORK.md confirmed:** conditional-recurrence, RT/IPD synthesis and trial-discoverability checkpoints failed; methylation deprioritised; the ICD-O registry classification paper was user-rejected. None is re-proposed here under any name. I read no registry file and computed nothing from `research/data/emc-clinical-registry.json`.
5. `research/autonomy/clinical-methods-checkpoints-2026-09-07` **does not exist in this checkout** (`ls` exit 2). Per the brief that is **UNKNOWN, not proof of absence** — the checkpoint record may live on another branch or arrive with the pending-input bundle. I substituted the care-delivery records, which CLOSED-WORK.md also names.

---

## Method / inputs

- **Tooling:** PubMed MCP server (`mcp__PubMed__search_articles`, `mcp__PubMed__get_article_metadata`); Python 3.11.15; GNU coreutils; `git status` read-only.
- **According to PubMed**, the frame is the query `extraskeletal myxoid chondrosarcoma AND (metastasis OR recurrence) AND case reports[Publication Type]`, sort=relevance, retrieved 2026-09-08, `total_count = 84`, returned in two pages (`retstart` 0 and 40).
- **Retrieval:** all 84 PMIDs fetched via `get_article_metadata`. Note a real API behaviour: **the tool caps at 20 articles per call regardless of how many PMIDs are passed** — my nominal 21- and 22-PMID batches silently returned 20 each. I detected this by set-differencing the returned PMIDs against the frame (24 missing) and issued top-up calls until coverage was 84/84.
- **Egress:** direct NCBI eutils is **denied** — `curl https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi...` returned `curl: (56) CONNECT tunnel failed, response 403`, agent-proxy `connect_rejected`. This matches the standing record; I recorded it and did not retry or reroute. This is an honest unrecovered route, not an absence of data.
- **Files (all outside the repository), in `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/W08/`:** `b1.json`, `b2.json`, `b3.json` (60 abstracts, copied from the harness tool-result persistence); `screen_intervals.py`; `w08_interval_census.py`.
- **Two-stage extraction, deliberately separated:**
  1. *Machine screen* over the 60 on-disk abstracts — a regex for a number plus year/month/week in a sentence that also contains a temporal or event cue. It is a **screen, not a measurement**; recall is not established.
  2. *Hand adjudication* over all 84 abstracts against the stated inclusion rule, each accepted row carrying its verbatim sentence. The 24 abstracts not on disk were adjudicated from the tool output as returned.
- **Adjudication exclusions actually applied** (each a judgement a reader can overturn): PMIDs 8472444 (parosteal chondrosarcoma), 25671361 (clear cell sarcoma), 11504379 (parachordoma), 12743501 (myoepithelioma), 7606973 (unknown primary) — not EMC patients; 38111543 ("further progression of the pulmonary metastases at 29 months" — mets pre-existing, interval not to a *first* event); 28249774 (interval is time alive, not time to event); 11259746 (anchor ambiguous). PMIDs 12672100, 16337717, 21753718 have **no abstract available** — UNKNOWN, not zero.

Code, for the coordinator to place as it sees fit:

```python
# code/W08/screen_intervals.py
#!/usr/bin/env python3
"""W08 screen: find abstract sentences that state an elapsed interval, in the
PubMed 'EMC AND (metastasis OR recurrence) AND case reports' frame.
Screen only -- every hit is hand-adjudicated afterwards. No inference here."""
import json, glob, re, sys

NUM = r"(?:\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)"
PAT = re.compile(
    rf"[^.]*\b{NUM}[- ](?:year|month|week)s?\b[^.]*\.", re.I)
CUE = re.compile(r"after|later|prior|follow|recurr|metasta|since|interval|free", re.I)

def main(paths):
    rows = []
    for p in sorted(paths):
        for a in json.load(open(p))["articles"]:
            pmid = a["identifiers"]["pmid"]
            ab = a.get("abstract") or ""
            hits = [s.strip() for s in PAT.findall(ab) if CUE.search(s)]
            rows.append((pmid, a["identifiers"].get("doi"), a["title"][:70], hits))
    n_hit = sum(1 for r in rows if r[3])
    for pmid, doi, title, hits in rows:
        if hits:
            print(f"--- PMID {pmid} | doi={doi}\n    {title}")
            for h in hits:
                print(f"    > {h}")
    print(f"\nSCREEN: {len(rows)} abstracts, {n_hit} with >=1 interval-like sentence")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or glob.glob("b*.json")))
```

The census script `code/W08/w08_interval_census.py` is the file whose full output is quoted under Validation evidence; its data block is the ten `INCLUDED` rows, two `IMPRECISE` rows and one `OCCULT_PRIMARY_FIRST` row reproduced in the Result table below, each with the verbatim sentence shown there.

---

## Result

**Table 1 — Included patient-events: interval from primary diagnosis/surgery to first documented distant or regional metastasis.** Unit: months. Every row `PRIMARY` (a value printed in the cited abstract, transcribed, not modelled). "Uncertainty" here is *transcription precision*, not a sampling interval — there is no sampling model.

| # | PMID | DOI | months | precision | verbatim source sentence | grade |
|---|---|---|---|---|---|---|
| 1 | 10469211 | [10.1046/j.1365-2559.1999.00735.x](https://doi.org/10.1046/j.1365-2559.1999.00735.x) | 2.8 (12 weeks) | exact | "Three patients had metastases, one at 12 weeks, one at 10 months, and one at presentation of recurrent tumour." | PRIMARY |
| 2 | 10469211 | [10.1046/j.1365-2559.1999.00735.x](https://doi.org/10.1046/j.1365-2559.1999.00735.x) | 10 | exact | (same sentence) | PRIMARY |
| 3 | 9158707 | [10.1016/s0046-8177(97)90081-2](https://doi.org/10.1016/s0046-8177(97)90081-2) | 10 | exact | "The patient with myxoid chondrosarcoma of the posterior mediastinum developed bilateral pulmonary metastases 10 months after surgery and has been lost to follow-up since." | PRIMARY |
| 4 | 35494187 | [10.5114/jcb.2022.115161](https://doi.org/10.5114/jcb.2022.115161) | 16 | exact | "She presented with a large right inguinal lymph node metastasis of EMC 16 months after surgery." | PRIMARY |
| 5 | 23588370 | [10.1097/PAS.0b013e3182796e46](https://doi.org/10.1097/PAS.0b013e3182796e46) | 26 | exact | "Two patients developed lung metastases at 26 and 74 months and are alive with disease at 44 and 74 months, respectively." | PRIMARY |
| 6 | 10450885 | [10.1007/s002560050531](https://doi.org/10.1007/s002560050531) | 34 | exact | "At 34 months, retroperitoneal metastases were noted on abdominal CT." | PRIMARY |
| 7 | 18308379 | [10.1016/j.urology.2007.11.092](https://doi.org/10.1016/j.urology.2007.11.092) | 48 | exact | "…4 years after surgery, manifested with testicular enlargement, a period punctuated by three local recurrences." | PRIMARY |
| 8 | 9711893 | [10.2169/internalmedicine.37.625](https://doi.org/10.2169/internalmedicine.37.625) | 60 | exact | "…pulmonary metastasis from the extraskeletal myxoid chondrosarcoma (EMC) which had been detected 5 years earlier." | PRIMARY |
| 9 | 23588370 | [10.1097/PAS.0b013e3182796e46](https://doi.org/10.1097/PAS.0b013e3182796e46) | 74 | exact | (same sentence as row 5) | PRIMARY |
| 10 | 15810095 | [10.3748/wjg.v11.i14.2203](https://doi.org/10.3748/wjg.v11.i14.2203) | **240** | exact | "We describe a case of a man suffering from EMC who developed a single pancreatic metastasis 20 years after the initial diagnosis." | PRIMARY |

**Table 2 — Imprecise intervals, excluded from the primary set, used only in sensitivity.**

| PMID | months | precision | verbatim | grade |
|---|---|---|---|---|
| 25619049 | ~12 | approximate ("About a year") | "About a year after the end of the treatment an intracardiac mass was identified during a follow up chest CT-scan." | PRIMARY (imprecise) |
| 273676 | <72 | upper bound | "…our patient had a less than six-year remission from the neoplasm." | PRIMARY (imprecise) |

**Table 3 — Separate category: metastasis documented BEFORE the primary was found.**

| PMID | DOI | n patients | verbatim | grade |
|---|---|---|---|---|
| 3731040 | [10.1002/1097-0142(19860901)58:5<1144::aid-cncr2820580528>3.0.co;2-l](https://doi.org/10.1002/1097-0142(19860901)58:5%3C1144::aid-cncr2820580528%3E3.0.co;2-l) | 2 | "The patients presented with metastasis to the lung, 10 years and 2 years, respectively, prior to discovery of the primary neoplasms in the soft tissues of the lower extremities." | PRIMARY |

**Table 4 — Computed description (`w08_interval_census.py`, exit 0).** All rows are `PRIMARY` arithmetic over Table 1/2 values. Percentages are proportions **of documented published events**; they are not risks and carry no sampling uncertainty because there is no sample.

| statistic | exact set (n=10) | sensitivity, exact+imprecise (n=12) | grade |
|---|---|---|---|
| values (months) | 2.8, 10, 10, 16, 26, 34, 48, 60, 74, 240 | + 12, 72 | PRIMARY |
| min / median / max | 2.8 / 30.0 / 240.0 | 2.8 / 30.0 / 240.0 | PRIMARY |
| Q1 / Q3 (inclusive method) | 11.5 / 57.0 | 11.5 / 63.0 | PRIMARY |
| events > 24 months | 6/10 = 60% | 7/12 = 58% | PRIMARY |
| events > 60 months | **2/10 = 20%** | 3/12 = 25% | PRIMARY |
| events > 120 months | **1/10 = 10%** | 1/12 = 8% | PRIMARY |
| longest source-traceable interval | **240 months (20 years), PMID 15810095** | same | PRIMARY |

**The one defensible finding, stated as narrowly as the data allows.** In the enumerable PubMed EMC case-report literature there exist **at least two source-traceable patients whose first documented metastasis occurred more than five years after primary treatment, and at least one more than ten years after** (240 months). The existence of these patients does not depend on any denominator and is not manufactured by publication bias: selective publication changes which patients are written up, it cannot invent an elapsed interval printed in a peer-reviewed abstract. What publication bias *does* forbid is the next sentence anyone would want to write — the proportion. **20% and 10% are proportions of published events, not of patients, and must never be read as the fraction of EMC patients whose metastasis a five- or ten-year window would miss.**

`UNKNOWN` rows, recorded rather than treated as zero: 3 frame articles have no abstract available (PMIDs 12672100, 16337717, 21753718); the interval to a third metastasis in PMID 10469211 is stated only as "at presentation of recurrent tumour"; and the machine screen's recall against the hand adjudication was not measured.

---

## Validation evidence

**RUN.** Environment: Linux container, Python 3.11.15, working directory `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/W08`.

1. Frame retrieval, PubMed MCP — `search_articles`, two pages: `total_count: 84`, 40 + 44 PMIDs returned.
2. Coverage check (dedup against frame), exit 0:
```
b1.json 20
b2.json 20
b3.json 20
unique retrieved: 60
frame: 84
missing n= 24
```
Top-up calls then brought coverage to 84/84.
3. Egress probe, **denied and not retried**:
```
$ curl -sS -o /tmp/x.xml -w "%{http_code}\n" "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=extraskeletal+myxoid+chondrosarcoma&retmax=2"
curl: (56) CONNECT tunnel failed, response 403
[agent-proxy] eutils.ncbi.nlm.nih.gov:443 — connect_rejected
Exit code 1
```
4. Screen, exit 0:
```
$ python3 screen_intervals.py b1.json b2.json b3.json
...
SCREEN: 60 abstracts, 35 with >=1 interval-like sentence
EXIT=0
```
5. Census, exit 0 — verbatim key output:
```
$ python3 w08_interval_census.py
frame_total_count = 84 ; abstracts_retrieved = 84 ; included_events = 10
imprecise_excluded = 2 ; occult_primary_first = 1

[exact intervals only] n=10 patient-events (months)
  values : [2.8, 10.0, 10.0, 16.0, 26.0, 34.0, 48.0, 60.0, 74.0, 240.0]
  min/median/max : 2.8 / 30.0 / 240.0
  Q1 / Q3        : 11.5 / 57.0
  >  24 months : 6/10 = 60% of DOCUMENTED events
  >  60 months : 2/10 = 20% of DOCUMENTED events
  > 120 months : 1/10 = 10% of DOCUMENTED events

[sensitivity: exact + imprecise] n=12 patient-events (months)
  values : [2.8, 10.0, 10.0, 12.0, 16.0, 26.0, 34.0, 48.0, 60.0, 72.0, 74.0, 240.0]
  Q1 / Q3        : 11.5 / 63.0
  >  60 months : 3/12 = 25% of DOCUMENTED events
  > 120 months : 1/12 = 8% of DOCUMENTED events
EXIT=0
```
6. Write-isolation check, exit 0: `git status --porcelain | grep -c W08` → `0`.

**PROPOSED (NOT RUN).** Independent second adjudication of all 84 abstracts by a different reader/agent, and measurement of the screen's recall against that adjudication. Full-text retrieval for the 3 abstract-less PMIDs. Extension of the same census to the *local recurrence* interval (candidate sources already visible in the screen: PMID 1531226 at 168 months, PMID 22743288 at 84 months, PMID 15810095 at 168 months). Cross-checking each interval against the article full text rather than the abstract.

---

## Limitations

- **This describes the published record, not the disease.** The estimand is a property of a literature frame. It is not incidence, not cumulative risk, not a hazard.
- **Publication bias is severe and one-directional for the proportion.** A 20-year interval to metastasis is precisely the sort of course that gets written up; a metastasis at 8 months in an ordinary patient often does not. The proportions in Table 4 are therefore **not** upper or lower bounds on any population quantity and must not be quoted as one. Only the **existence counts** — at least 2 patients beyond 60 months, at least 1 beyond 120 — survive the bias, and even those are lower bounds on existence, never on frequency.
- **No denominator exists.** The number of EMC patients who *never* metastasised, or who were followed and censored, is unobserved in a case-report frame. Nothing here can be divided by anything.
- **Competing risks are unobserved.** Patients who died of other causes, or of local disease, before a metastasis could be documented never enter this frame. Any reading of these intervals as a time-to-event distribution ignores that censoring entirely.
- **Anchors are heterogeneous.** Some intervals run from primary surgery, some from initial diagnosis; the abstracts do not always say which. The repository's own `emc-recurrence-timing.json` flags this exact hazard (`⚠_the_anchors_differ_by_the_time_to_surgery`). I did not correct for it and the values must not be pooled with the cohort medians in that artifact.
- **Abstract-only ascertainment.** Intervals were read from abstracts, not full texts; an abstract may compress or round a timeline. Three articles have no abstract at all.
- **Diagnostic drift over five decades.** The frame spans 1978–2026; EMC's definition and the availability of `NR4A3` fusion confirmation changed substantially across it. Older cases may not meet current diagnostic criteria.
- **No clinical recommendation is made or implied.** Nothing here says how long anyone should be watched, how often, or with what modality. Detecting a metastasis earlier moves the date of detection and need not move any outcome — lead-time bias applies in full.
- **Not transferable** to other sarcomas, and not a validation of anything in `research/modalities/`.

---

## Stop condition

**Set:** one fully specified, feasible, non-duplicative question with data availability *actually verified*, plus a first computed description if the data was reachable.

**MET.** The question is specified across all ten required elements; the prior-work check confirms it duplicates neither AUT-065's aggregate observation nor any of the four closed gates; availability was verified by retrieving 84/84 abstracts rather than by assuming; and a first honest description was computed by a script that ran to exit 0 with every value traceable to a quoted sentence and a DOI. One route (direct NCBI eutils) was blocked and is recorded as blocked, without reroute.

---

## Tool-call and wall-clock count actually used

Approximately 26 tool calls; wall clock from first repository read to final validation approximately 20 minutes (end-of-run `date -u` = 2026-09-08T01:56:54Z). Both inside the self-observed targets in COMMON-BRIEF.md §1.

---

## Next concrete action

**One successor task, for this lane:** promote the census from abstracts to full texts for the ten included PMIDs plus the three abstract-less ones, and add the local-recurrence interval as a second, separately-anchored column — then have a second independent adjudicator re-derive the included set from the same 84 abstracts and report the disagreement count against the falsification condition stated above. That single step is what would turn a first description into something a reviewer could rely on. It is a literature-retrieval task with a known blocker: several of those journals sit behind routes this repository has already recorded as 403, so the successor must budget for a partially unrecovered set and report it as UNKNOWN rather than dropping it.

I did not attempt any publication, deposit, or external posting, and this lane's output makes no clinical recommendation.

result: Lane 8 delivered a new, non-duplicative EMC surveillance question — a patient-level census of the interval to first documented metastasis across the enumerable 84-article PubMed EMC case-report frame — with availability verified by retrieving all 84 abstracts and a first description computed (n=10 exact events; median 30 months, range 2.8–240; 2/10 beyond 5 years and 1/10 beyond 10 years, stated strictly as counts of published events, not risks).
