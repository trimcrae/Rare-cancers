> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

# W08d — Recovery pass on the 8 unadjudicated EMC interval records

## Worker

- Worker ID: **W08d**, lane 8 refill (successor named by W08c), campaign OPUS-CAPACITY-CAMPAIGN-20260908.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). I did not and cannot observe the served model. No environment variable in this container names a model at all (see dump: there is no `*MODEL*` variable). The coordinator must extract the actual per-child runtime model from the transcript.
- **HEAD actually read: `b9a0257e6acff53ad22535cf2adf261313e0b250`.** Note this is **not** the frozen read commit named in `COMMON-BRIEF.md` (`92abbcb905cacf07f14b238db50d1b98f6590374`); the checkout has moved on since the brief was written, and `git status --porcelain` showed one modified tracked file (`WAVE-LOG.md`) and 17 untracked worker reports. I made no writes to the tree.

`date -u` at start: `Tue Sep  8 02:23:57 UTC 2026`
`date -u` at end: `Tue Sep  8 02:25:21 UTC 2026`

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (run at start; re-run at end, 51 lines, md5 `d34e5ad074f671b813c93e14de5df58c`, byte-identical):

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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 -Djavax.net.ssl.trustStorePassword=changeit -Djavax.net.ssl.trustStoreType=PKCS12 -Dhttps.proxyHost=127.0.0.1 -Dhttps.proxyPort=37223 -Dhttp.nonProxyHosts=localhost|127.0.0.1|::1|127.*|0.*|::|169.254.*|api.anthropic.com|api-staging.anthropic.com|api-pr-preview.anthropic.com|mcp-proxy.anthropic.com|mcp-proxy-staging.anthropic.com|registry.npmjs.org|jsr.io|npm.jsr.io|pypi.org|files.pythonhosted.org|index.crates.io|proxy.golang.org|host.docker.internal|10.*|172.16.*|...|192.168.*|100.64.0.0/10|*.svc.cluster.local -Djdk.http.auth.tunneling.disabledSchemes= -Djdk.http.auth.proxying.disabledSchemes=
NO_PROXY=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,...,*.svc.cluster.local
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,...,*.svc.cluster.local
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

(Three long proxy/no-proxy lines are elided mid-value with `...` for readability only; the full 51-line dump was printed in-session and hashes as above.)

## Question

Can any of the 8 records W08c could not adjudicate — the 5 with `[Abstract not available]` (PMIDs 28467750, 36097623, 21753718, 12672100, 16337717) and the 3 with imprecise/bounded intervals (273676, 25619049, 28249774) — be converted from UNKNOWN into either a documented interval event or a documented non-recoverable, using only routes **not** recorded as denied in `CLOSED-WORK.md`?

It is open because W08c adjudicated from abstracts only and explicitly named this residual as the sole remaining systematic undercount reachable without replaying a denied publisher route.

**Answer: partially yes — exactly one of the eight converts.** PMID 36097623 has an open-access PMC record; its full text yields one admissible Rule A event at 108 months. The other seven are now **documented non-recoverable by every permitted route**, and one of them (28467750) is additionally a categorical exclusion on grounds independent of retrievability.

## Prior-work check

```
$ for p in 28467750 36097623 21753718 12672100 16337717 273676 25619049 28249774; do
    echo "== $p"; rg -l "$p" --glob '!.git' | head -5; done
```
All eight appear only in W08/W08b/W08c campaign reports and in a few unrelated artefacts. Two hits worth naming: `36097623` appears in `research/manuscripts/emc-terminal-events.json`, `research/manuscripts/emc-terminal-events-classified.json`, `research/literature/rt-lung-mets-probe.json` and `research/literature/emc-mortality-probe.json`; `28249774` appears in `research/literature/rt-lung-mets-probe.json` and `research/modalities/nr4a3-nuccore-sweep-inputs.json`. I grepped both files for surrounding context and **found no retained interval sentence for either PMID** — the identifiers occur in probe/ingestion inventories, not as adjudicated interval evidence. Two hits (`16337717`, `273676` in `results/nr4a3-metad-r3/ckpt/HILLS`) are coincidental numeric matches inside a metadynamics checkpoint, not citations.

```
$ git ls-files | grep -i -E "W08|interval-census"
research/autonomy/opus-capacity-campaign-20260908/reports/W08-disease-course-surveillance-question.md
research/autonomy/opus-capacity-campaign-20260908/reports/W08b-interval-census-adjudication.md
```

Closed items confirmed **not** replayed, per `CLOSED-WORK.md`: no Sunitinib 2014, no Wagner 2020, no CTARC 2022, no Trabectedin/RT 2018, no pazopanib, no anthracycline route of any kind; **no publisher route at all**; no institutional or proxy route; no rephrasing or relabelling of any denied route. I did not recreate the restricted NR4A Perspective review. I did **not** open `emc-km-reachability-census-2026-08-25.json` or any cohort-level median, and nothing below is pooled with one.

## Method / inputs

- Transferred prior work read in full: `reports/W08c-blinded-third-adjudication.md` (complete). `reports/W08b-interval-census-adjudication.md` was read targetedly (grep on the eight PMIDs plus the `[Abstract not available]` screen), which confirmed W08b independently found the same five unavailable abstracts and the same three imprecise strings.
- Tools: PubMed MCP server only — `convert_article_ids`, `find_related_articles` (`link_type='pubmed_pmc'`), `get_article_metadata`, `get_full_text_article`. **According to PubMed**; DOI links are given per record below. No `search_articles` call was needed: the frame is fixed by W08c at 84 and I am not rebuilding it.
- Rules applied **exactly as W08c wrote them, unrelaxed**. Rule A = interval from primary diagnosis / primary surgery to FIRST distant or regional metastasis. Rule B = same anchor to FIRST local recurrence. Bounded ("less than"), approximate ("about"), or unanchored values stay in the imprecise bucket. Unretrievable stays UNKNOWN — never a negative, never imputed.
- **Tool-defect guard (W10c's finding) actively applied.** The single `get_full_text_article` call passed a PMCID confirmed by `convert_article_ids` (`PMC9463557`), never a PMID. The returned record's identifiers were checked before any content was used: returned `pmid` = `36097623`, matching the record requested. **No mismatch occurred; had one occurred I would have discarded it loudly and recorded the record as unrecovered.**
- Execution directory `/tmp/claude-0/w08d/`, outside the Git tree. **No write to `/home/user/Rare-cancers` of any kind.**

### Route exhaustion, actually run

`convert_article_ids` on all eight PMIDs returned a PMCID for **exactly one**:

```
{"pmcid":"PMC9463557","pmid":"36097623","doi":"10.1016/j.jdcr.2022.08.012","requested-id":"36097623"}
```

All seven other records returned a bare `{"pmid": "...", "requested-id": "..."}` with **no `pmcid` and no `doi` field beyond what PubMed already held** — i.e. no PMC full text exists for them. `find_related_articles` with `link_type='pubmed_pmc'` over those same seven returned a linkset with **no `linksetdbs` at all** (`{"dbfrom":"pubmed","ids":[...]}` and nothing else), independently confirming zero PMC full-text links. `lookup_article_by_citation` was **not** used to chase these records: it maps a citation to a PMID and cannot return article content, so it has no capacity to convert an UNKNOWN — using it would have manufactured activity without evidence. `find_related_articles` with `pubmed_pubmed` was deliberately **not** used as a conversion route: a computationally similar article is a *different paper about different patients*, and importing an interval from it would be fabricating patient linkage.

## Result

Every count below is a **count of published case-report events**, never a rate, risk, or incidence. **The frame has no denominator.**

### Per-record outcome for all 8 records

| # | PMID | DOI | Outcome | Basis |
|---|---|---|---|---|
| 1 | 36097623 | [10.1016/j.jdcr.2022.08.012](https://doi.org/10.1016/j.jdcr.2022.08.012) | **CONVERTED → Column A event, 108 months** `PRIMARY` | PMC9463557 full text retrieved; PMID verified as matching |
| 2 | 28467750 | [10.2460/javma.250.10.1113](https://doi.org/10.2460/javma.250.10.1113) | **Documented non-recoverable** *and* categorically excluded `UNKNOWN` | No PMCID, no PMC link; abstract still `[Abstract not available]`. Additionally MeSH `Animals`, `Dogs`, `Dog Diseases` — **a canine case**, excluded by W08c's non-human rule regardless of retrievability |
| 3 | 21753718 | [10.1097/PAT.0b013e3283488fec](https://doi.org/10.1097/PAT.0b013e3283488fec) | **Documented non-recoverable** `UNKNOWN` | No PMCID, no PMC link; `[Abstract not available]` re-confirmed. Publication type "Letter"; MeSH includes `Neoplasm Recurrence, Local` and `Fatal Outcome` — so the paper plausibly contains a Rule B interval that is simply not reachable |
| 4 | 12672100 | [10.1002/dc.10271](https://doi.org/10.1002/dc.10271) | **Documented non-recoverable** `UNKNOWN` | No PMCID, no PMC link; `[Abstract not available]` re-confirmed. "Letter"/"Comment", 2 pages. MeSH `Pleural Effusion, Malignant`, `Neoplasm Metastasis` — a plausible Rule A record, unreachable |
| 5 | 16337717 | [10.1016/j.revmed.2005.09.024](https://doi.org/10.1016/j.revmed.2005.09.024) | **Documented non-recoverable** `UNKNOWN` | No PMCID, no PMC link; `[Abstract not available]` re-confirmed. French-language "Letter", 3 pages. MeSH `Lymphatic Metastasis` — a plausible Rule A (regional/nodal) record, unreachable |
| 6 | 273676 | none (no DOI in PubMed) | **Still imprecise** — remains outside both columns | Verbatim: *"our patient had a less than six-year remission from the neoplasm."* Bounded value; no PMCID; no new route. Stays imprecise **by rule**, not by failure to look |
| 7 | 25619049 | none (no DOI in PubMed) | **Still imprecise** — remains outside both columns | Verbatim: *"About a year after the end of the treatment an intracardiac mass was identified during a follow up chest CT-scan."* Approximate **and** anchored to end of treatment, not to primary diagnosis or primary surgery. Two independent reasons; no PMCID |
| 8 | 28249774 | [10.1016/j.prp.2017.02.008](https://doi.org/10.1016/j.prp.2017.02.008) | **Still excluded** — durations of follow-up, not intervals to event | Verbatim: *"Two patients are alive with disease (local recurrence and lung metastasis) after five years and five years and six months, respectively and one patient died of disease two years after the diagnosis."* No PMCID. The full abstract is available (it was never an unavailable-abstract record); the "two years after the diagnosis" value is an interval to **death**, not to a metastasis or recurrence, so Rule A and Rule B both exclude it |

### The one admitted event

**Column A addition — W08d-A9.** `PRIMARY`.

| Field | Value |
|---|---|
| PMID | 36097623 |
| PMCID | PMC9463557 (confirmed by `convert_article_ids`; returned record's PMID verified) |
| DOI | [10.1016/j.jdcr.2022.08.012](https://doi.org/10.1016/j.jdcr.2022.08.012) |
| Months | **108** |
| Anchor | initial diagnosis / primary surgery (left below-knee amputation) |
| Event | first documented distant metastasis — frontal-bone/scalp mass, histologically confirmed metastatic EMC |

Verbatim sentence admitting the event (anchor and event tied in one sentence):

> "Our patient underwent surveillance with yearly chest computed tomography and nuclear bone scans after the initial diagnosis of EMC of the foot and was considered disease-free for 9 years before presenting to the dermatology clinic for a forehead mass presumed to be a lipoma."

Corroborating verbatim sentence for the surgical anchor:

> "His past medical history was pertinent to EMC on the left foot, for which he underwent a left below-the-knee amputation 9 years before his presentation to the clinic, followed by 4 cycles of adjuvant chemotherapy with ifosfamide and doxorubicin."

Confirming the lesion is metastatic EMC rather than a second primary:

> "A review of the primary tumor on the left foot showed identical morphology, consistent with metastatic EMC."

**Admissibility reasoning, including the argument against.** Year-granular values are already admitted in W08c's Column A (A3 "after 2 years", A7 "5 years earlier"), so 9 years = 108 months is consistent, not a relaxation. The event is the *first* distant metastasis: yearly chest CT and bone-scan surveillance is stated, and the patient is described as disease-free across the interval, so no earlier distant event is documented. **The one genuine ambiguity, flagged rather than resolved silently:** the abstract-level narrative also states *"The mass was noted 1 year before presentation after a minor forehead trauma"* — if the metastasis is dated to when the mass was first noticed rather than when it was diagnosed, the interval is 96 months, not 108. I admit 108 because that is the value the source itself states with an explicit anchor ("disease-free for 9 years"), and because the mass noted a year earlier was clinically taken for a lipoma and was not a documented metastasis. An adjudicator preferring the earlier date would enter 96; **either value leaves the union's shape unchanged (both fall between 74 and the Column B maximum) and both exceed every existing Column A value.**

Two things in this full text that I deliberately did **not** use: the article's own statement of *"a median interval of 20 months for distant recurrence"* is a cohort-level median from other literature and is **not pooled** with anything here; and the article's "estimated 10-year survival rate of 60.7%" is a survival statistic from a different population entirely and plays no part in this census.

### W08c's columns, unrevised, and the union

W08c's Column A (n=8) and Column B (n=5) are **reported unchanged**; I did not revise them.

| Set | n (events) | values (months) | min | Q1 | median | Q3 | max | >24 mo | >60 mo | >120 mo |
|---|---|---|---|---|---|---|---|---|---|---|
| W08c Column A (unrevised) | 8 | 10,16,24,26,34,48,60,74 | 10 | 22.00 | 30.0 | 51.00 | 74 | 5 of 8 | 1 of 8 | 0 of 8 |
| **Union A = W08c A + W08d-A9** | **9** | 10,16,24,26,34,48,60,74,**108** | 10 | 24.00 | **34** | 60.00 | **108** | 6 of 9 | 2 of 9 | 0 of 9 |
| W08c Column B (unrevised) | 5 | 16,29,36,42,168 | 16 | 29.00 | 36 | 42.00 | 168 | 4 of 5 | 1 of 5 | 1 of 5 |
| **Union B = W08c B + ∅** | **5** | 16,29,36,42,168 | 16 | 29.00 | 36 | 42.00 | 168 | 4 of 5 | 1 of 5 | 1 of 5 |

Units months. Quartiles by linear interpolation on order statistics, same estimator as W08c. No confidence interval is quoted: this is not a sample from a defined population, so an interval would be uninterpretable. The single addition moves the union Column A median from 30 to 34 months and the maximum from 74 to 108 months — a direct illustration that the unavailable-abstract bucket was biasing the census **downward**, exactly as W08c warned.

**Residual UNKNOWN count after this pass: 4 of 84** (28467750, 21753718, 12672100, 16337717), of which 28467750 would be excluded anyway as canine — so **3 of 84 records remain both unretrievable and potentially eligible**. These are undercounts of unquantified size, not zeros.

## Validation evidence

**RUN.** Environment: `Linux 6.18.44-fc-v24 x86_64`, `Python 3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0]`, cwd `/tmp/claude-0/w08d` (outside the Git tree).

Script `/tmp/claude-0/w08d/stats_union.py`, reproduced in full:

```python
import statistics as st
A_w08c=[10,16,24,26,34,48,60,74]      # W08c Column A, unrevised
B_w08c=[16,29,36,42,168]              # W08c Column B, unrevised
A_add=[108]                           # W08d addition: PMID 36097623 (PMC9463557)
B_add=[]
A=sorted(A_w08c+A_add); B=sorted(B_w08c+B_add)
def q(x,p):
    x=sorted(x); n=len(x); h=(n-1)*p; lo=int(h); hi=min(lo+1,n-1)
    return x[lo]+(h-lo)*(x[hi]-x[lo])
for name,v,base in (("A: first distant/regional metastasis",A,A_w08c),
                    ("B: first local recurrence",B,B_w08c)):
    print(f"--- UNION Column {name}")
    print(f"  W08c set (unrevised): {sorted(base)}  n={len(base)}")
    print(f"  union values (months): {v}")
    print(f"  n = {len(v)}  (documented published case-report events, NOT a rate, risk or incidence)")
    print(f"  min = {min(v)}  Q1 = {q(v,.25):.2f}  median = {st.median(v)}  Q3 = {q(v,.75):.2f}  max = {max(v)}")
    for t in (24,60,120):
        print(f"  events strictly beyond {t} months: {sum(1 for x in v if x>t)} of {len(v)} documented events")
    print()
print("Frame has NO denominator. UNKNOWN records are not zeros and are excluded, not imputed.")
```

Command and verbatim output:

```
$ cd /tmp/claude-0/w08d && python3 stats_union.py; echo "EXIT=$?"
--- UNION Column A: first distant/regional metastasis
  W08c set (unrevised): [10, 16, 24, 26, 34, 48, 60, 74]  n=8
  union values (months): [10, 16, 24, 26, 34, 48, 60, 74, 108]
  n = 9  (documented published case-report events, NOT a rate, risk or incidence)
  min = 10  Q1 = 24.00  median = 34  Q3 = 60.00  max = 108
  events strictly beyond 24 months: 6 of 9 documented events
  events strictly beyond 60 months: 2 of 9 documented events
  events strictly beyond 120 months: 0 of 9 documented events

--- UNION Column B: first local recurrence
  W08c set (unrevised): [16, 29, 36, 42, 168]  n=5
  union values (months): [16, 29, 36, 42, 168]
  n = 5  (documented published case-report events, NOT a rate, risk or incidence)
  min = 16  Q1 = 29.00  median = 36  Q3 = 42.00  max = 168
  events strictly beyond 24 months: 4 of 5 documented events
  events strictly beyond 60 months: 1 of 5 documented events
  events strictly beyond 120 months: 1 of 5 documented events

Frame has NO denominator. UNKNOWN records are not zeros and are excluded, not imputed.
EXIT=0
```

Route-exhaustion evidence, verbatim from `convert_article_ids` (`"response-date":"2026-09-07 22:24:25"` — the tool server's own clock, which lags this container's UTC clock by ~4 h; I report both rather than reconciling them):

```
"records":[{"pmid":"28467750","requested-id":"28467750"},
{"pmcid":"PMC9463557","pmid":"36097623","doi":"10.1016/j.jdcr.2022.08.012","requested-id":"36097623"},
{"pmid":"21753718","requested-id":"21753718"},{"pmid":"12672100","requested-id":"12672100"},
{"pmid":"16337717","requested-id":"16337717"},{"pmid":"273676","requested-id":"273676"},
{"pmid":"25619049","requested-id":"25619049"},{"pmid":"28249774","requested-id":"28249774"}]
```

`find_related_articles(link_type='pubmed_pmc')` over the seven, verbatim and complete:

```
{"linksets":[{"dbfrom":"pubmed","ids":["28467750","21753718","12672100","16337717","273676","25619049","28249774"]}]}
```

No `linksetdbs` key — zero PMC links for all seven.

Tool-defect guard, verbatim identifier block from the single `get_full_text_article` call:

```
"identifiers":{"pmcid":"PMC9463557","pmid":"36097623","doi":"10.1016/j.jdcr.2022.08.012","pii":"S2352-5126(22)00366-6"}
```

Requested `PMC9463557`; returned PMID `36097623` = the record intended. **Match verified. No W10c-class mismatch in this pass.**

Git-tree read state:

```
$ git -C /home/user/Rare-cancers rev-parse HEAD
b9a0257e6acff53ad22535cf2adf261313e0b250
```

**PROPOSED (NOT RUN):** none. No repository test suite, `scripts/preflight.sh`, or lint was invoked — this worker is read-only on the tree and its dispatch did not call for it. No content-policy refusal was encountered anywhere in this pass.

## Limitations

- **Every number here is a count of published case-report events. None is a rate, risk, incidence, hazard, or probability. The frame has no denominator.** Publication bias in a case-report frame is severe and one-directional, and this pass makes that visible: the single record recovered was an *unusually long* 108-month interval, which is precisely the kind of case that gets written up.
- **3 of 84 records remain unretrievable and potentially eligible** (21753718 nasopharynx with `Neoplasm Recurrence, Local`; 12672100 malignant effusion with `Neoplasm Metastasis`; 16337717 neck with `Lymphatic Metastasis`). All three are short Letters in subscription journals with no PMC deposit. **These are honest unrecovered sources.** Both columns remain undercounts by an unquantified amount. MeSH terms tell us these papers are *likely* to contain eligible intervals; they do not tell us the values, and nothing is imputed from them.
- **The MeSH-based plausibility notes above are not evidence of an interval.** They justify calling these records a probable undercount; they license no value.
- **Route exhaustion is scoped to the permitted set.** I tested PMC availability only. `CLOSED-WORK.md` records publisher routes as denied and I did not attempt any; the correct statement is "not reachable by any permitted route", not "does not exist".
- **Anchors remain heterogeneous and unharmonised.** The new event is anchored to initial diagnosis / amputation; union Column A now mixes primary surgery, initial diagnosis, primary detection, and "definitive therapy". Do not average across anchors as if they were one clock.
- **The 108-vs-96-month ambiguity is real and is not resolved by the source.** I chose the value the source states with an explicit anchor and flagged the alternative rather than picking silently.
- **Nothing here is pooled with any cohort-level median in this repository**, and the "median interval of 20 months" quoted inside PMC9463557 is another paper's literature summary and was not used.
- **Competing risks are unobserved**; Columns A and B are not complementary and must not be combined.
- **No surveillance interval, imaging schedule, follow-up duration, or clinical recommendation is stated or implied by anything in this report, and none may be derived from it.**
- **Model identity is self-reported and unverified.** The read HEAD differs from the brief's frozen commit, as recorded above.

## Stop condition

**MET.** All 8 records have a per-record outcome: 1 converted to a documented Rule A event with a verbatim quote (36097623, 108 months); 4 documented non-recoverable with the reason (28467750 — no PMC route *and* canine; 21753718, 12672100, 16337717 — no PMC route, abstract unavailable, subscription Letters); 2 remaining imprecise by rule (273676 bounded, 25619049 approximate and wrongly anchored); 1 remaining excluded as follow-up duration rather than interval-to-event (28249774). Descriptive statistics were recomputed on the explicit union with a real command, environment, and exit code 0. W08c's Column A (n=8) and Column B (n=5) were reported unrevised. The remaining 3 eligible records are hereby fixed as **permanently UNKNOWN under the permitted routes** — not negative, not zero, not imputed.

## Tool-call and wall-clock count actually used

**14 tool calls** (8 Bash, 1 ToolSearch, 5 PubMed MCP: 1 `convert_article_ids`, 1 `find_related_articles`, 1 `get_article_metadata`, 1 `get_full_text_article` — plus the ToolSearch load). Wall clock `02:23:57` → `02:25:21` UTC, approximately **1.5 minutes**, well inside the ~40 minute / ~40 call target. I returned as soon as the stop condition was met.

## Next concrete action

**No viable successor in this lane on the retrieval axis.** The four PMC-absent records are exhausted for every permitted route, and the two imprecise records are imprecise in their source text — no route can make "less than six years" or "about a year" precise, so re-attacking them would be replaying a rule, not finding evidence.

The one genuinely open successor is **adjudication-rule sensitivity, not retrieval**: W08c flagged three borderline calls that each move the union materially — PMID 10469211's two unanchored metastasis values ("one at 12 weeks, one at 10 months", which would add 2.8 and 10 months and pull the median down), the inclusion of osseous EMC (23588370, 28249774, 9149016 — excluding it drops union Column A from n=9 to n=7), and PMID 22743288's combined synovial-sarcoma/EMC histology. A successor should compute the union's descriptive statistics under each of those three rule variants as an explicit **sensitivity table**, with no new retrieval and no new sources, so that the census's dependence on adjudication judgement is quantified rather than argued. That is a finite, fully-local task requiring no external route at all.
