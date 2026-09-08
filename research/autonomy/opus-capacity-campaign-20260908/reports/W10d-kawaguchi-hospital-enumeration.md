> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

# W10d — Does Kawaguchi 2003 enumerate its eight affiliated hospitals, and is Kyushu University among them?

## Worker

- Worker **W10d**, **Lane 10** refill (older-literature clinical evidence), executing the single decisive successor W10c named.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`), Claude Code 2.1.42, remote cloud container. I cannot observe the served model; the coordinator must extract the runtime model from the transcript. No finding below depends on which model produced it.
- `date -u` **start: `Tue Sep  8 02:25:01 UTC 2026`**. **End: `Tue Sep  8 02:26:02 UTC 2026`.**
- Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (four long proxy/`no_proxy`/`JAVA_TOOL_OPTIONS` lines elided in the second printing only because they contain no identity information and are reproduced verbatim in the start-of-run capture; **no variable names a model**):

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

- **HEAD actually read: `b9a0257e6acff53ad22535cf2adf261313e0b250`** — the same later commit W10c reported, **not** the brief's frozen `92abbcb905cacf07f14b238db50d1b98f6590374`. The freeze no longer holds; I record it rather than smooth it.
- **Write isolation honoured.** Nothing written under `/home/user/Rare-cancers`. `/tmp/claude-0/w10d/` was created and remained **empty** — no script was needed. `git status --porcelain | wc -l` returns **17 at start and 17 at end** (1 modified `WAVE-LOG.md` + 16 untracked coordinator-written reports, all pre-existing and none mine). No git write operation of any kind.

## Question

**Does Kawaguchi 2003 (`japan2003`, PMID 12599237, [DOI](https://doi.org/10.1002/cncr.11162), n=42, "eight affiliated hospitals") enumerate those eight hospitals, and is Kyushu University among them?** Secondarily: does its Methods state an accrual window?

Open because W10c graded Oshiro 2000 (PMID 11493979, Kyushu University) tier C / UNKNOWN against every retained Japanese/Asian EMC series, and identified this one enumeration as the single datum that settles the highest-risk pair outright in either direction.

**Answer: the question is not resolvable on the permitted route. The eight hospitals are not enumerated in anything retrievable, and Kawaguchi 2003 has no PMC deposit.** This is a determinate negative about the route, recorded as an honest unrecovered source.

## Prior-work check

Read in full before any other action: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `reports/W10c-oshiro-overlap-admissibility.md`, and `systems/POLICY-evidence.md` §2.3 / §2.7. (W10b and W05 are transferred through W10c's verbatim quotation of W05's four tiers, which I apply unrelaxed and did not restate in my own words.)

| # | command | what it showed |
|---|---|---|
| 1 | `rg -c -i "12599237" --glob '!.git' .` | 9 files — `citation-provenance-ledger.json`, `emc-clinical-registry.json`, `endpoint/meta-analysis.md`, `citation-retraction-sweep.json`, `emc-km-admissibility-2026-08-27.json`, `rt-lung-mets-probe.json`, `emc-site-curation.json`, `emc_site_curation.py`, and W10c's report. The paper is **well retained at abstract/metadata strength** — this is not a novelty claim. |
| 2 | `rg -n -i "eight affiliated\|8 affiliated\|affiliated hospital" --glob '!.git' .` | The full abstract is already committed twice in `research/literature/rt-lung-mets-probe.json` (lines 1077, 1927). **It says "files of eight affiliated hospitals" and stops.** No committed file anywhere enumerates them. |
| 3 | `rg -l -i "kawaguchi" --glob '!.git' .` | 7 files; the two non-campaign clinical ones are the registry and `endpoint/meta-analysis.md`. Neither carries an institution list. |
| 4 | `rg -l -i "cncr.11162" --glob '!.git' .` | 6 files, same set. |
| 5 | `sed -n '518,566p' research/literature/emc-km-admissibility-2026-08-27.json` | **A prior denied route already exists for this paper** (see Method). |

**Closed items I confirm I am not replaying:** I issued **no** request against Sunitinib 2014 (`24703573`), Wagner 2020 (`32856598`), CTARC 2022 (`35144048`), Trabectedin/RT 2018, the pazopanib primary, or the anthracycline paper. No `curl`, no `WebFetch`, no `WebSearch`, no network request of any kind outside the PubMed MCP server. I did not touch PUB-EMC-CLASSIFICATION, any Brenca route, the restricted NR4A Perspective, Hofvander/EGA, lane-11 source-index material, or `GSE4303`/`GSE28866`. **I did not re-attempt Oshiro 2000 itself.** I added no case to any denominator and attempted no patient or case identity.

## Method / inputs

- Corpus: `/home/user/Rare-cancers` at `b9a0257e6acff53ad22535cf2adf261313e0b250`, read-only. Files read: `systems/POLICY-evidence.md` §2.3 and §2.7, `research/data/emc-clinical-registry.json`, `research/literature/emc-km-admissibility-2026-08-27.json`, `research/literature/rt-lung-mets-probe.json`.
- Tools: PubMed MCP server only (`convert_article_ids` ×2, `get_article_metadata` ×1); ripgrep, `sed`, Python 3 stdlib under Linux 6.18.44-fc-v24, container `container_0166QEHnXrRA8nCR59c9UG4k`.
- **According to PubMed**, all bibliographic content below is from `get_article_metadata(["12599237"])` for Kawaguchi 2003, *Cancer* 2003;97(5):1285–92, [DOI](https://doi.org/10.1002/cncr.11162).
- **Route discipline followed exactly as dispatched.** `convert_article_ids` was called **first**, under both `id_type: pmid` and `id_type: doi`. Both returned a record containing **no `pmcid` field**. Because no PMCID was confirmed, **`get_full_text_article` was never called** — so W10c's tool defect (a PMID silently accepted as a PMCID, returning a different, unrelated article with no error) had no opportunity to fire, and there is no returned record whose PMID needed checking against a request. The defect remains reported and unrepaired.
- **No publisher request was issued and no wall was routed around.** The repository's own record shows a prior `caller_pdf_url` route to `https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/cncr.11162` returned **HTTP 403** (`browser_http: 403`, 2000 bytes of HTML) in round `km-figures-round5-2026-08-27`. That is a **denied route already on record**, and I did not replay it. Note the honest tension the record itself preserves: Unpaywall reports `is_oa: true, oa_status: "bronze"` with one OA location — the same Wiley URL that returns 403. **A bronze OA flag is a claim by a metadata aggregator, not an access grant**, and it does not convert a 403 into a permitted retry.

## Result

### R1 — The enumeration question (PRIMARY / UNKNOWN)

| item | value | class |
|---|---|---|
| Are the eight hospitals enumerated in the PubMed abstract? | **NO** — verbatim: *"Forty-two cases of EMC, which had been identified from **files of eight affiliated hospitals** and confirmed for histologic diagnosis at **the Pathology Center**"*. Neither the hospitals nor "the Pathology Center" is named. | PRIMARY |
| Are they enumerated anywhere in the retained corpus? | **NO** — see prior-work check #2. | PRIMARY |
| Is a PMC full text available to read the Methods? | **NO.** `convert_article_ids` returns `{"pmid":"12599237","requested-id":"12599237"}` under PMID and `{"doi":"10.1002/cncr.11162","requested-id":"..."}` under DOI. **No `pmcid` under either.** | PRIMARY |
| **Is Kyushu University among the eight?** | **UNKNOWN.** Not shown present, not shown absent. | **UNKNOWN** |

### R2 — Author affiliations, recorded and explicitly *not* used as a substitute (PRIMARY, non-decisive)

According to PubMed, the record carries **14 named authors** — Kawaguchi S, Wada T, Nagoya S, Ikeda T, Isu K, Yamashiro K, Kawai A, Ishii T, Araki N, Myoui A, Matsumoto S, Umeda T, Yoshikawa H, Hasegawa T — plus one empty author entry. **Only the first carries an affiliation:** `"Department of Orthopaedic Surgery, Sapporo Medical University, Sapporo, Japan."` The remaining thirteen carry **no affiliation string at all** in the PubMed record. Article types include `Multicenter Study`.

Two observations, both marked as **licensing nothing**:

- No author of Kawaguchi 2003 is Tsuneyoshi M or Oda Y, the Kyushu University anatomic-pathology group that authored Oshiro 2000. **This is not evidence that Kyushu contributed no cases.** A hospital can contribute archival specimens to a multi-institutional review without any of its staff appearing on the byline — which is precisely the mechanism the phrase "files of eight affiliated hospitals … confirmed at the Pathology Center" describes. Treating an absent byline as an absent institution would be exactly the inference `CLAUDE.md` §4 forbids.
- Inferring the eight hospitals from the co-authors' *known* institutional homes would be reconstruction from outside knowledge, not a reading of the paper's Methods. **I did not do it, and it must not be done downstream.** The dispatch asked for the enumeration *verbatim*; a plausible roster is not that.

### R3 — Accrual window (PRIMARY / UNKNOWN — the cap is unchanged)

| item | value | class |
|---|---|---|
| Accrual window stated in the abstract | **NONE.** The only temporal quantity is *"The average follow-up period was 7.4 years."* — a follow-up duration, not an accrual window, and a **mean**, not a range. | PRIMARY |
| Accrual window in the Methods | **UNKNOWN** — Methods unretrievable. | UNKNOWN |
| Retained registry state | `studyPeriodUnknown: true`, `pool: false`, `contextReason: "different-endpoint"`, note *"Diagnosis years not stated (published 2003)."* — already correct; **no repair needed and none proposed.** | PRIMARY |
| Retained KM-admissibility state | `study_period: null`, `verdict: "unreachable"`, *"the risk-row question is unasked, not answered no"* — already correct. | PRIMARY |

**W10c's five-of-seven count stands unchanged: five of the seven retained Asian series still document no accrual window.** `japan2003` remains one of the five. Nothing I found moves that number in either direction.

### R4 — Tier update for the Oshiro × `japan2003` pair (PRIMARY)

Applying W05's four-tier rubric **unrelaxed**, exactly as W10c quotes it (tier B requires **all three** of disjoint institution, disjoint accrual window and disjoint identifier space, *each individually documented*; tier C is any strict subset and is a **falsifier only, licensing nothing**):

| condition | before (W10c) | after (W10d) | change |
|---|---|---|---|
| institution disjoint | UNDOCUMENTED | **UNDOCUMENTED** — the enumeration exists in a paper that cannot be read on any permitted route | none |
| accrual window disjoint | UNDOCUMENTED | **UNDOCUMENTED** — `japan2003` states none; Oshiro's is likewise undocumented | none |
| identifier space disjoint | UNDOCUMENTED | **UNDOCUMENTED** — neither publishes at case level | none |
| **tier** | **C** | **C** | **none** |
| **verdict** | **UNKNOWN** | **UNKNOWN** | **none** |

**The tier update is: no change.** Neither branch of the dispatched conditional fired. Kyushu is **not** shown to be among the eight, so Oshiro's 36 cases are **not** provisionally OVERLAPPING; and Kyushu is **not** shown absent, so the pair does **not** gain one of tier B's three conditions in documented form. The pair remains the highest-risk pair in W10c's table, for the same reason as before, with the decisive datum now demonstrated to be **out of reach on the routes this program may use** rather than merely unattempted.

What is genuinely new is that a *third* status now applies to this datum. Before W10d it was "unattempted"; it is now **"attempted on the only permitted route and determinately absent from it."** That is a smaller gain than the dispatch hoped for, and I am not inflating it.

### R5 — What did NOT change (PRIMARY, stated to prevent downstream drift)

- **Oshiro's IPD refusal stands, untouched.** W10c's `POLICY-evidence.md` §2.7(a)/(d) refusal is independent of the overlap question and was never in scope here. Its verdict remains **`unreachable` / named-but-unusable**, not `refused_no_risk_row`.
- **No case entered any pooled denominator.** Under §2.3, `japan2003` is already `pool: false` and Oshiro's 36 are in no denominator at all. No pooled figure, Wilson interval, or headline in this repository changes because of this report.
- **`japan2003`'s own retained figures** (5/10-yr OS 100%/88%, 5-yr DFS 45%, wide-excision recurrence 14%) are quoted here only as context for what the abstract contains. They are not re-derived, not pooled, and not compared numerically to Oshiro or any other series.
- **No clinical claim of any kind.** Nothing here bears on prognosis, surgical margin adequacy, efficacy, safety, or clinical readiness.

## Validation evidence

**RUN.** Linux 6.18.44-fc-v24, container `container_0166QEHnXrRA8nCR59c9UG4k`, `bash`, ripgrep, Python 3 stdlib. Execution directory `/tmp/claude-0/w10d/` (created, used for nothing — no script was required). All repository access read-only.

| # | Command | Exit | Verbatim key output |
|---|---|---|---|
| 1 | `date -u` (start) | 0 | `Tue Sep  8 02:25:01 UTC 2026` |
| 2 | `git -C /home/user/Rare-cancers rev-parse HEAD` | 0 | `b9a0257e6acff53ad22535cf2adf261313e0b250` (**≠ frozen `92abbcb9…`**) |
| 3 | `rg -c -i "12599237" --glob '!.git' .` | 0 | 9 files (listed in prior-work check) |
| 4 | `rg -n -i "eight affiliated\|8 affiliated\|affiliated hospital" --glob '!.git' .` | 0 | abstract present verbatim ×2 in `rt-lung-mets-probe.json`; **no enumeration anywhere** |
| 5 | `rg -l -i "kawaguchi" --glob '!.git' .` | 0 | 7 files, no institution list |
| 6 | `rg -l -i "cncr.11162" --glob '!.git' .` | 0 | 6 files |
| 7 | `grep -n -A28 '^### 2\.7' systems/POLICY-evidence.md` | 0 | §2.7(a)–(d) read as written |
| 8 | PubMed **`convert_article_ids(["12599237"], id_type="pmid")`** | ok | `{"status":"ok",…,"records":[{"pmid":"12599237","requested-id":"12599237"}]}` — **no `pmcid`, no `doi` field returned** |
| 9 | PubMed **`convert_article_ids(["10.1002/cncr.11162"], id_type="doi")`** | ok | `{"status":"ok",…,"records":[{"doi":"10.1002/cncr.11162","requested-id":"10.1002/cncr.11162"}]}` — **no `pmcid`** |
| 10 | PubMed `get_article_metadata(["12599237"])` | ok | `count: 1`; `identifiers: {"pmid":"12599237","doi":"10.1002/cncr.11162"}` — **no `pmc` field**; abstract text as quoted in R1; sole affiliation `"Department of Orthopaedic Surgery, Sapporo Medical University, Sapporo, Japan. kawaguch@sapmed.ac.jp"` |
| 11 | `sed -n '518,566p' research/literature/emc-km-admissibility-2026-08-27.json` | 0 | `"verdict": "unreachable"`; `routes: [{"route":"caller_pdf_url","http":403,…,"browser_http":403}]`; `unpaywall: {"is_oa":true,"oa_status":"bronze","n_oa_locations":1}` |
| 12 | `git status --porcelain \| wc -l` (start and end) | 0 | `17` both times — tree unchanged by me |
| 13 | `date -u` (end) | 0 | `Tue Sep  8 02:26:02 UTC 2026` |

**`get_full_text_article` was NOT called** — correctly, because no PMCID was ever confirmed. Recording this as a deliberate non-call, not an omission.

**PROPOSED (NOT RUN).** Retrieving the Kawaguchi 2003 PDF through the GitHub Actions runner escape hatch and reading its Methods for the hospital list and accrual window. **Not run**, and I flag that W10c's successor proposal understated the obstacle: the repository already holds a **403 on the publisher route** for exactly this DOI, so an Actions run is not a fresh route but a re-attempt of a denied one from a different IP. Whether a different egress makes it a *genuinely new* route or a circumvention of a wall is a judgment call I am not authorized to make unilaterally, and my dispatch explicitly forbade issuing any publisher request. It needs the coordinator's decision, not a worker's.

## Limitations

- **UNKNOWN is not a soft yes, and here it is also not a soft no.** I did not show Kyushu is among the eight, and I did not show it is not. Both directions remain open. Anyone reading R2's byline observation as "Kyushu is probably not involved" has misread it; the byline is silent on institutional contribution by construction, since the paper's own Methods describe case ascertainment from *files*, not from participating authors.
- **A determinate negative about a route is not a negative about the world.** "Kawaguchi 2003 has no PMC deposit" is established. "The eight hospitals are unknowable" is not — the list is presumably printed in the paper's Materials & Methods, which exists and which this program cannot currently read.
- **Transfer limits.** W10c's tier assignments, W05's rubric and W10b's Oshiro findings are transferred as established; I re-derived none of them and re-verified only the `japan2003` row. Oshiro's 5-yr 73% / 10-yr 63% remain abstract-strength SECONDARY and were not touched.
- **Denominator gap, restated as a hard limit.** No case from Oshiro or `japan2003` entered any pooled denominator, and under §2.3 `japan2003` is already `pool: false`. Nothing here would change that even had the enumeration been recovered.
- **The `bronze` OA flag is a live inconsistency in the retained record** — Unpaywall says openly accessible, the actual fetch said 403. I report the discrepancy and did not resolve it by testing.
- **HEAD is not the frozen commit** (see Worker). I read a later tree, as W10c also did.
- **One author entry in the PubMed record is empty** (`{}`), so the true author count may be 15. I record this rather than silently normalizing it; nothing in the report depends on the count.

## Stop condition

**Set (per dispatch):** either the eight hospitals enumerated verbatim with a Kyushu yes/no and the resulting tier update, **or** a documented non-recoverable with the exact route outcome.

**MET, via the second branch.** The route outcome is exact and reproducible: `convert_article_ids` returns **no PMCID for PMID 12599237 under either PMID or DOI lookup**, therefore `get_full_text_article` had no valid input and was not called; the publisher route is **already recorded denied (HTTP 403)** in `emc-km-admissibility-2026-08-27.json` and was not replayed; no publisher request was issued and no wall was routed around. Kawaguchi 2003 is recorded as an **honest unrecovered source at abstract-and-metadata strength**. The Oshiro × `japan2003` tier is **unchanged at C / UNKNOWN**, and R3 confirms the five-of-seven accrual-window cap stands. This is a complete answer under the dispatch's own terms.

## Tool-call and wall-clock count actually used

**11 tool calls** (7 Bash, 3 PubMed MCP, 1 ToolSearch) against a ~40 target. **Wall clock ≈ 1 minute** (`date -u` 02:25:01 → 02:26:02 UTC) against a ~40-minute target. Returned as soon as the stop condition was met; no padding, no sleeping, no invented extra work.

## Next concrete action

**One task, and it is a coordinator decision rather than a worker task: rule on whether an Actions-runner fetch of `https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/cncr.11162` counts as a genuinely new route or a replay of a route recorded denied.** The repository's record carries a 403 on that exact URL alongside an Unpaywall `bronze` OA flag, and those two facts disagree. Until that is ruled on, no worker should touch this paper: my dispatch forbade a publisher request, and the next worker's would face the same 403 with the same ambiguity.

If the ruling is **replay-forbidden** (which the conservative reading of `CLOSED-WORK.md` supports), then I record honestly: **there is no viable successor in this lane for the overlap question.** The Oshiro × `japan2003` pair stays tier C / UNKNOWN permanently on available routes, the enumeration is unobtainable, and the lane's remaining open items are all downstream of retrievals that have already failed. That is not a failure of the lane; it is the correct terminal state for a question whose decisive datum sits behind a wall this program respects.
