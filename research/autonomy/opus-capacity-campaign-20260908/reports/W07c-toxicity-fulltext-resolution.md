> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met — both papers resolved to a definite verdict at full-text level. Report follows.

---

# W07c — Full-text resolution of the two abstract-level-provisional MIXED-ARM-ONLY rows (cabozantinib, apatinib)

## Worker

- **Worker ID:** W07c · **Lane 7 refill** — executing W07b's named "Next concrete action."
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I report myself as Claude Opus 5 (`claude-opus-5`) under Claude Code 2.1.42, remote cloud environment. I did not observe the served model and do not assert it as fact; the coordinator extracts the actual per-child runtime model from the transcript.
- **HEAD actually read: `b9a0257e6acff53ad22535cf2adf261313e0b250`.** This is **not** the `92abbcb905cacf07f14b238db50d1b98f6590374` named as frozen in COMMON-BRIEF.md and used by W07 and W07b. The tree has advanced (the coordinator has since collected 17 worker reports, visible as untracked files under `reports/` plus a modified `WAVE-LOG.md`). I record the real HEAD rather than the brief's stated one. **None of the files W07/W07b depended on changed** — my findings are external (PubMed) and my prior-work check ran against this newer HEAD, so the difference does not affect any result below, but it must not be papered over.
- **`date -u` at start:** `Tue Sep  8 02:27:19 UTC 2026` · **at end:** `Tue Sep  8 02:29:10 UTC 2026`

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (46 substantive lines; four proxy/`JAVA_TOOL_OPTIONS`/`no_proxy` lines that match only through embedded `anthropic.com` hostnames are shown in the raw capture but filtered here as noise — identical count, 46, at end):

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

**Write-isolation compliance:** no repository file created, modified or deleted. `git status --porcelain` shows 17 entries at both start and end — the same 17 coordinator-collected reports and `WAVE-LOG.md`, none of them mine. My only writes were to `/tmp/claude-0/w07c/` (one copied tool-result JSON, `ft.json`), outside the tree. No git write operation of any kind. `scripts/preflight.sh` not run — not authorised by this dispatch, no code authored.

---

## Successor selection — which one I took, and what I declined

W07b's "Next concrete action" section names **one** successor and **one** explicit non-successor.

**TAKEN:** *"retrieve the full texts (or supplementary safety tables) of PMID 34716194 (cabozantinib, PMC8776602) and PMID 32547189 (apatinib, PMC7237692) … and check whether either disaggregates adverse events by histology."*

It passes all three admission tests:
- **(a) executable read-only** — pure retrieval plus local parsing under `/tmp/claude-0/w07c/`; nothing in the tree touched.
- **(b) no denied route** — neither PMID appears anywhere in CLOSED-WORK.md. The denied list is Sunitinib 2014 (24703573), Wagner 2020 (32856598), CTARC 2022 (35144048), Trabectedin/RT 2018 (10.4172/clinical-practice.1000433), pazopanib primary (31331701 full text), and anthracycline PMC3879193/24345066. 34716194 and 32547189 are on none of them, and I touched none of them.
- **(c) network scope** — served entirely by the PubMed MCP server (`convert_article_ids`, `get_full_text_article`). No publisher fetch, no proxy egress, no PMC HTTP route. W07b predicted this would need the Actions runner because "this environment's PMC route is recorded in-repo as commonly blocked" — **that prediction was wrong for the MCP path**, which is a distinct route from the recorded HTTP egress block and returned both full texts without error. That is itself a reusable finding for the campaign.

**DECLINED — the one W07b explicitly excluded:** *"further pazopanib retrieval"* (PMID 31331701 full text). Declined on ground (b): CLOSED-WORK records the pazopanib primary full paper as unrecovered, and W07b itself marked this PROPOSED-not-attempted deliberately. I did not test that route and assert nothing about it.

**Also declined, from W07's older next-action list (already executed by W07b):** re-reading the nine Q5 abstracts — DUPLICATE, W07b completed it.

No fallback was needed. The mandated fallback (three-way denominator classification of every W07b figure) is **not** delivered here because the named successor was executable and reached a verdict, exactly as the dispatch ordering requires.

---

## Question

**Do the cabozantinib STS phase 2 trial (PMID 34716194) and the apatinib chondrosarcoma two-centre study (PMID 32547189) disaggregate their adverse-event data by histology — such that an EMC-specific adverse-event denominator exists inside either paper — or is the mixed denominator the only one present at full-text and table level?**

Open because W07b classified both rows `MIXED-ARM-ONLY` **from the abstract only**, and flagged this in its own Limitation 1 as the single soft edge in its replacement claim: a supplementary safety table disaggregated by histology would overturn both rows and would be the only way to discover it. A secondary open item was W07b's Limitation 4 — n(EMC) for the cabozantinib trial was UNKNOWN, the abstract naming EMC among responding histologies without a count.

---

## Prior-work check

Commands run read-only from `/home/user/Rare-cancers` (full output in Validation evidence):

1. `cat …/COMMON-BRIEF.md` and `cat …/CLOSED-WORK.md` — read in full before any other action.
2. `cat …/reports/W07-patient-reported-outcomes-denominators.md` (290 lines) and `…/reports/W07b-toxicity-denominator-enumeration.md` (266 lines) — read in full.
3. `rg -c -- "PMC8776602|PMC7237692" --glob '!.git' .` — both PMCIDs already appear across ~10 tracked files (`emc-systemic-therapy-pooling.json`, `emc-clinical-registry.json`, `rt-lung-mets-probe.json`, `emc-mortality-probe.json`, `citation-retraction-sweep.json`, `candidates.json`, others). **The papers are not new to the corpus.**
4. `rg -n "11\.1%|16\.7%" --glob '!.git' research/ systems/` — the cabozantinib record in `research/literature/rt-lung-mets-probe.json` (lines 202, 1656) holds **the abstract only**, including the sentence `"The most common grade 3/4 adverse events were hypertension (7.4%) and neutropenia (16.7%)."` **No Table 3 counts, no body-text toxicity paragraph, and no apatinib toxicity section exist anywhere in the tree.**
5. `rg -n -i "disaggregat|histology-specific safety|EMC-specific denominator" --glob '!.git' .` — hits only in the W07 and W07b reports' own prose.

**Conclusion of the check:** the *papers* are retained; the *full-text adverse-event structure* — which is the actual object of this question — is not. What is new here is the table-level verification, plus two source-internal numeric discrepancies (§5.4) that are invisible from the abstracts the repository holds.

**CLOSED-WORK compliance, item by item:** Sunitinib 2014 (24703573) — not touched, and I make no claim about it; PMID 23058004 was not re-read and nothing is substituted for the 2014 cohort. Wagner 2020, CTARC 2022, Trabectedin/RT 2018 — not touched. Pazopanib primary (31331701) — **not retrieved**; used below only at W07b's already-retained abstract strength, no exposure window, no erratum, no method-omission claim. Anthracycline PMC3879193/24345066 — not touched, no rate. PUB-EMC-CLASSIFICATION and every Brenca route — not approached. **No case added to any pooled denominator; nothing pooled at all.**

---

## Method / inputs

**Retrieval, all via the PubMed MCP server, 2026-09-08 ~02:27 UTC:**

1. `mcp__PubMed__convert_article_ids(ids=["34716194","32547189"], id_type="pmid")` — **run first, as the dispatch requires**, to confirm the PMCIDs rather than trusting W07b's transcription.
2. `mcp__PubMed__get_full_text_article(pmc_ids=["PMC8776602","PMC7237692"])` — one call, both articles.

**Mismatch guard, executed:** the tool result was parsed locally and every returned `identifiers` block checked against what I requested. Both matched exactly — `PMC7237692 → pmid 32547189 → doi 10.2147/CMAR.S253201` and `PMC8776602 → pmid 34716194 → doi 10.1158/1078-0432.CCR-21-2480`. **Zero mismatches; nothing discarded.** (The tool's documented silent PMID-as-PMCID failure mode did not occur, because I passed verified PMCIDs.)

**Local processing:** the 62.2 KB tool result was copied to `/tmp/claude-0/w07c/ft.json` and read with `python3 -c` JSON/regex scans. No network beyond the two MCP calls. Article metadata, abstracts, body text and table content below are **from PubMed / PubMed Central**; DOI links given for both articles.

**Classification rubric — W07b's, unchanged**, so the rows remain comparable: `EMC-SPECIFIC` / `MIXED-ARM-ONLY` / `NO-AE-DATA` / `UNRECOVERED`, with a sub-flag for graded-and-counted vs narrative.

---

## Result

### 5.1 Headline — both rows CONFIRMED `MIXED-ARM-ONLY` at full-text and table level; W07b's Limitation 1 is CLOSED, its Limitation 4 is RESOLVED

Neither paper disaggregates adverse events by histology. In both, the adverse-event denominator is explicitly and only the whole mixed cohort — 54 for cabozantinib, 33 for apatinib — while **both papers disaggregate efficacy by histology in the same results section.** W07b's replacement claim therefore survives its own stated soft edge and is upgraded from abstract-level-provisional to full-text-established for these two papers.

Additionally: **n(EMC) for the cabozantinib trial is 3 of 54 evaluable** (Table 1, baseline characteristics), recovered here. W07b's Limitation 4 is answered.

### 5.2 Verdict table

Evidence grades: `PRIMARY` = the paper's own reported observation on its own patients. No `PREDICTION` or `EXPERIMENTAL VALIDATION` row arises in this lane.

| Paper | n(EMC) | Efficacy disaggregated by histology? | AE denominator as stated by the source | Any EMC-only AE denominator? | Verdict | Grade |
|---|---|---|---|---|---|---|
| Cabozantinib, Clin Cancer Res 2022;28(2):279–288, PMID 34716194, [DOI](https://doi.org/10.1158/1078-0432.CCR-21-2480) | **3** of 54 evaluable (Table 1) — *was UNKNOWN in W07b* | **Yes** — responders enumerated by histology (2 ASPS, 2 UPS, 1 EMC, 1 uterine LMS) | Table 3 caption, verbatim: *"Grade 2 and higher adverse events occurring in >3% of patients. Worst grade that is at least possibly related to study drugs is shown for each patient (= 54 total patients)."* | **No** | **MIXED-ARM-ONLY — CONFIRMED at table level** | PRIMARY |
| Apatinib, Cancer Manag Res 2020;12:3513–3525, PMID 32547189, [DOI](https://doi.org/10.2147/CMAR.S253201) | **3** of 33 (*"3/33 (9.1%) extraskeletal myxoid CS"*) | **Yes** — ORR, DoR and PFS all given per subtype, incl. EMC ORR *"33.4% for myxoid CS (1/3)"* and *"For extraskeletal myxoid CS, although there were only 3 cases, the median DoR was 21.2 months (range, 10.9, 28.1) with one PR and two SD"* | Toxicity section, verbatim: *"All 33 patients (100%) experienced one or more AEs… Grades 3 or 4 treatment-related AEs were observed including anorexia (12 patients [36.4%]), wound dehiscence and infections (9 [27.3%]), platelet decrease (3 [9.1%]), and hypertension (2 patients [6.1%])."* | **No** | **MIXED-ARM-ONLY — CONFIRMED at full-text level** | PRIMARY |

### 5.3 The asymmetry is now demonstrated, not inferred

W07b called the apatinib paper's behaviour "the sharper and more interesting finding" — denominator discipline applied to efficacy and dropped for safety — but could only infer it from the abstract. The full text **demonstrates** it, and shows the cabozantinib paper does the same thing:

- Apatinib gives EMC its own efficacy denominator **four separate times** (subtype ORR 1/3; median DoR 21.2 mo over the 3 cases; EMC subtype as a univariate PFS covariate; EMC named in the paper's own concluding sentence as a subgroup that *"might benefit from this therapy more"*) — and gives EMC its own safety denominator **zero times**.
- Cabozantinib names the single EMC responder individually in its results text and lists EMC as n=3 in Table 1, yet its Table 3 collapses every patient into one 54-patient safety column with no subtype axis at all.

Both papers therefore single EMC out as a subtype worth reporting separately **when the news is efficacy**, and dissolve it into the pooled arm **when the topic is harm**. Over the three mixed-histology papers in W07b's enumerated set (trabectedin 3/36, apatinib 3/33, cabozantinib 3/54 — the last now quantified), the count is **3 of 3**.

### 5.4 Two source-internal numeric discrepancies, found by checking each paper's stated counts against its own stated percentages

These are reported as **observations about the sources**, not as corrections and not as new rates. I computed no rate of my own; I checked each paper's printed percentage against the numerator and denominator that same paper prints, which is denominator-provenance verification and is this lane's function.

**(i) Cabozantinib — the abstract's two grade-3 percentages do not match the paper's own Table 3 counts, and appear transposed.**

| Source location | Statement, verbatim |
|---|---|
| Abstract | *"The most common grade 3/4 adverse events were hypertension (7.4%) and neutropenia (16.7%)."* |
| Body, Results | *"The most common grade 3 events were hypertension (9 patients, 11.1%) and neutropenia (4 patients, 7.4%)"* |
| Table 3 (count data) | Hypertension: grade 2 = 21, **grade 3 = 9**. Neutrophil count decreased: grade 2 = 7, **grade 3 = 4**. Denominator stated as 54. |

The three do not agree. Against the paper's own denominator of 54, the abstract's *values* 16.7% and 7.4% correspond to counts 9 and 4 respectively, but the abstract attaches 7.4% to hypertension and 16.7% to neutropenia — the reverse of the Table 3 counts; and the body's "9 patients, 11.1%" is inconsistent with its own numerator (11.1% is the paper's ORR figure, 6/54, appearing elsewhere in the same abstract). **The count data in Table 3 (9 and 4 over 54) are the primary record; the two percentage renderings disagree with those counts and with each other.** I state which figure sits where and stop. I do not declare a corrected percentage, and nothing downstream should quote the abstract sentence as a checked value — **`research/literature/rt-lung-mets-probe.json` holds exactly that abstract sentence at lines 202 and 1656**, and W07b's table row 5 quotes it too.

**(ii) Apatinib — the abstract conflates a withdrawal count with a grade-3+ count, and its percentage does not match its own printed fraction.**

| Source location | Statement, verbatim |
|---|---|
| Abstract | *"Grade 3 or higher adverse events were frequent in 11/33 (39.3%) of patients who discontinued apatinib due to deterioration of their general condition."* |
| Body, Toxicity | *"All 33 patients (100%) experienced one or more AEs, and 11 (39.3%) had AEs leading to the withdrawal of apatinib."* |

In the body, **11 is the number of patients who withdrew because of AEs** — not a count of patients with grade ≥3 events. The body's own grade 3/4 counts are separate and larger for the leading term (anorexia 12). The abstract's sentence therefore mislabels a discontinuation numerator as a grade-3+ numerator. Separately, the printed percentage 39.3% does not correspond to the printed fraction 11/33 against the paper's own denominator (the paper's other four AE percentages — 12→36.4%, 9→27.3%, 3→9.1%, 2→6.1% — are each consistent with a denominator of 33; this one is not). **Consequence: W07b's table row 6 quotes the abstract sentence, and it should not be used as a grade-3+ figure.** The defensible retained statement is the body's: 33/33 experienced ≥1 AE, and 11 withdrew for AEs after a median of 4 months (range 1–8), all over a 33-patient mixed-chondrosarcoma denominator, none of it EMC-attributable.

### 5.5 What lane 7's claim set looks like after this run

**Upgraded from provisional to established (these two papers only):**
> *"Neither the cabozantinib STS phase 2 trial nor the apatinib chondrosarcoma two-centre study disaggregates adverse events by histology. Cabozantinib's Table 3 states its denominator as 54 total patients; apatinib's toxicity section reports over all 33. Both papers disaggregate efficacy by histology in the same results section, including for their EMC patients (3 and 3 respectively)."*

**Newly available, with its denominator attached:**
> *"The cabozantinib trial enrolled 3 patients with extraskeletal myxoid chondrosarcoma among 54 evaluable, one of whom had a confirmed partial response."*

**Unchanged and still not supportable:** any EMC toxicity, discontinuation or dose-reduction rate, derived, pooled or transferred; anything read across from the conventional-chondrosarcoma pazopanib trial (PMID 31509242), which excludes EMC by protocol; anything from W07 rows 11/13 beyond retained strength. **Nothing in this report is pooled with anything.**

**No clinical claim whatsoever.** Explicitly: nothing in this lane bears on the safety, tolerability, therapeutic window, efficacy or clinical readiness of cabozantinib, apatinib, pazopanib, trabectedin, sunitinib, any anthracycline, or any other agent, for any patient. This is an evidence-availability and denominator-provenance audit of how two papers report their numbers. It supports no treatment choice.

---

## Validation evidence

### RUN

**V1.** Start clock and HEAD.
```
$ date -u
Tue Sep  8 02:27:19 UTC 2026
$ git rev-parse HEAD
b9a0257e6acff53ad22535cf2adf261313e0b250
```
Exit 0. Divergence from the brief's frozen `92abbcb9…` recorded in §Worker.

**V2.** PMCID confirmation **before** any full-text call — verbatim server response:
```
{"status":"ok","response-date":"2026-09-07 22:27:41",
 "request":{"idtype":"pmid","ids":["34716194","32547189"],"tool":"pubmed-mcp-server"},
 "records":[{"pmcid":"PMC8776602","pmid":"34716194","doi":"10.1158/1078-0432.CCR-21-2480","requested-id":"34716194"},
            {"pmcid":"PMC7237692","pmid":"32547189","doi":"10.2147/CMAR.S253201","requested-id":"32547189"}]}
```
Both PMCIDs match W07b's transcription. (Note the server's own `response-date` is stamped `2026-09-07 22:27:41`, four hours behind the container's `date -u`; a server-side timezone offset, recorded, not reconciled.)

**V3.** Full-text call and **mismatch guard**, verbatim output of the parse:
```
$ python3 -c "import json; d=json.load(open('ft.json')); ..."
IDENT: {'pmcid': 'PMC7237692', 'pmid': '32547189', 'doi': '10.2147/CMAR.S253201'}
TITLE: Apatinib for Treatment of Inoperable Metastatic or Locally Advanced Chondrosarcoma: What We Can Learn About the Biological Behavior of Chondrosarcoma from a Two-Center Study
LEN: 18395
KEYS: ['identifiers', 'title', 'full_text', 'doi', 'abstract']
---
IDENT: {'pmcid': 'PMC8776602', 'pmid': '34716194', 'doi': '10.1158/1078-0432.CCR-21-2480'}
TITLE: Clinical Activity of Single-Agent Cabozantinib (XL184), a Multi-receptor Tyrosine Kinase Inhibitor, in Patients with Refractory Soft-Tissue Sarcomas
LEN: 38339
KEYS: ['identifiers', 'title', 'full_text', 'doi', 'abstract']
---
EXIT=0
```
**Both returned PMIDs equal the PMIDs I requested. Zero mismatches, nothing discarded.** Titles match the expected articles (cabozantinib STS phase 2; apatinib chondrosarcoma two-centre) — an independent check beyond the identifier match.

**V4.** Apatinib toxicity section, retrieved verbatim (exit 0), quoted in full in §5.2/§5.4. Also verified: `re.findall(r'Table\s*\d?', t)` over the apatinib text returned `[]` — **the extraction contains no table blocks for this paper**, which is the basis of Limitation 2 below.

**V5.** Cabozantinib Table 3 retrieved with its caption and all rows (exit 0) — caption and the hypertension/neutrophil rows quoted in §5.2 and §5.4. The table has columns Grade 2 / Grade 3 / Grade 4 and rows by MedDRA system-organ class; **there is no histology axis.** Supplementary material mentions in the text are `Supplementary Fig. S1` (PFS by prior VEGF therapy), `S2` (hypertension incidence vs time on study), `S3` (biomarkers by outcome) — none is an AE-by-histology table.

**V6.** n(EMC)=3 for cabozantinib, from the Table 1 baseline block, verbatim fragment: `…Clear cell sarcoma\n\n3\n\nSpindle cell sarcoma\n\n3\n\nExtraskeletal myxoid chondrosarcoma\n\n3\n\nLiposarcoma, total…`. Exit 0.

**V7.** Prior-work `rg` commands (exit 0) — output in §Prior-work check. Key negative: no tracked file contains the Table 3 counts or the apatinib toxicity paragraph; `rt-lung-mets-probe.json` lines 202/1656 hold the cabozantinib **abstract** only.

**V8.** End clock, HEAD and write-isolation:
```
$ date -u
Tue Sep  8 02:29:10 UTC 2026
$ git rev-parse HEAD
b9a0257e6acff53ad22535cf2adf261313e0b250
$ git status --porcelain | grep -c .
17
```
Exit 0. HEAD unchanged; the 17 dirty entries are the coordinator's collected reports and `WAVE-LOG.md`, identical to the start-of-run listing — **none is mine.** Substantive `env` match count 46 at end, identical set to start.

### PROPOSED (NOT RUN)

- **Retrieval of the cabozantinib Supplementary Data files themselves** (as opposed to the body's references to S1–S3). Not attempted; the body text characterises all three supplementary figures, and none is an AE table. A residual, small possibility that an unlisted supplementary file stratifies AEs by histology is left explicitly open as Limitation 1.
- **A publisher-side or PMC-HTTP fetch of the apatinib tables.** Not attempted — the MCP extraction carried no table blocks for that paper, and I did not open a second route.
- **Full text of PMID 31331701 (pazopanib).** Deliberately not attempted — CLOSED-WORK route, explicitly excluded by W07b.
- **Widening beyond W07's Q5 query set** (e.g. "side effects", "complications", "safety"). Out of this successor's scope; carried forward as the next action.
- `scripts/preflight.sh` — not run; not authorised, no code authored.

### Content-policy refusals

**None encountered.** No branch was refused, no denied route replayed, nothing rephrased or rerouted.

---

## Limitations

1. **"No histology-disaggregated AE data" means: not in the body text, not in the cabozantinib AE table, and not in any supplementary item the body describes.** For cabozantinib I read the actual Table 3; for apatinib I read the actual toxicity section. Neither is a proof that no unlisted supplementary file anywhere stratifies AEs by subtype. This is now a much narrower UNKNOWN than W07b's, but it is still UNKNOWN, **not zero.**
2. **The apatinib extraction contained no table blocks** (`Table` regex → `[]`). Its Table 1 (baseline) and any tabulated AE listing were not inspected. The toxicity *section* is unambiguous — one denominator, 33 — but an unread apatinib table is a real gap and the weaker of the two verdicts.
3. **The n(EMC)=3 figure for cabozantinib is a baseline enrolment count from Table 1**, over the 54 evaluable patients (55 enrolled, 1 never started). It is not a safety-population count, because the paper defines no per-histology safety population.
4. **The set remains exactly W07's Q5**, nine papers. A paper reporting EMC-specific AEs under "side effects", "complications", "safety" or a bare CTCAE term is outside it and would not have been found. Conference abstracts, non-English and unindexed literature are likewise outside.
5. **§5.4 reports discrepancies; it does not adjudicate them.** I did not contact authors, check errata, or declare a corrected percentage. The count data are stated as the primary record because counts are what the tables carry; that is a provenance judgement, not a recomputation.
6. **I did not re-verify W07's other table rows or W07b's other seven rows.** Only its rows 5 and 6 (and its Limitations 1 and 4) are affected. The pazopanib EMC-specific counterexample of §5.1/§5.3 in W07b stands untouched and unre-checked by me.
7. **Nothing here is clinical.** No safety, tolerability, therapeutic-window, efficacy or readiness claim for any agent or any patient is made or implied. Two of these papers report drugs in advanced pretreated cohorts; that this report names their adverse-event structure says nothing about whether any patient should receive them.
8. **HEAD divergence.** I read `b9a0257e…`, not the brief's `92abbcb9…`. External findings are unaffected; a prior-work `rg` run at the older commit could in principle differ, though the only tree changes are added worker reports.

---

## Stop condition

**Set (by the dispatch):** the named successor executed to a definite verdict with a real command and exit code.

**Status: MET.** The successor W07b named — full-text/supplementary check of PMID 34716194 and PMID 32547189 for histology-disaggregated adverse events — was executed via `mcp__PubMed__convert_article_ids` (PMCIDs confirmed first, as required) and `mcp__PubMed__get_full_text_article`, with local parsing at exit 0 (V3–V6).

**Verdict, definite and two-sided:** **both papers CONFIRMED `MIXED-ARM-ONLY`.** Neither disaggregates adverse events by histology; cabozantinib's Table 3 states its denominator as 54 total patients and carries no subtype axis, apatinib reports toxicity over all 33. W07b's Limitation 1 is closed for these two rows; its Limitation 4 is resolved with n(EMC) = 3 of 54. Two source-internal numeric discrepancies were found in passing and are reported without adjudication. No fallback task was needed or performed.

---

## Tool-call and wall-clock count actually used

**Tool calls: 11** — 7 Bash (all read-only or `/tmp` scratch), 1 ToolSearch, 1 PubMed `convert_article_ids`, 1 PubMed `get_full_text_article` (both articles in one call), plus the initial paired setup call. **Wall clock: ~1.9 minutes** (02:27:19 → 02:29:10 UTC). Well inside the ~40-call / ~40-minute self-observed target; returned on stop-condition satisfaction, no padding. Batching both full texts into a single MCP call is again what made this cheap.

---

## Next concrete action

**One specific successor:** re-run W07's Q5 with the vocabulary Q5 missed — `"extraskeletal myxoid chondrosarcoma"[All Fields] AND ("side effect*"[All Fields] OR "complication*"[All Fields] OR "safety"[All Fields] OR "CTCAE"[All Fields] OR "dose reduction"[All Fields] OR "discontinuation"[All Fields])` — and classify only the PMIDs **not already among the nine**, using W07b's unchanged four-way rubric. This directly attacks Limitation 4 above (and W07b's Limitation 2), which is now the largest remaining soft edge in lane 7: every claim in the lane is enumerated over a nine-paper set defined by four search terms, and the completeness of that set has never been tested. It is finite, read-only, needs nothing beyond PubMed MCP metadata, replays no denied route, and is decisive either way — either the set is stable under vocabulary widening, which materially strengthens the enumerated claim, or it is not, which must be known before any of it is written down.

**Explicitly not successors:** (a) further pazopanib retrieval — CLOSED-WORK, and excluded by W07b; (b) chasing the two §5.4 discrepancies to errata or author correspondence — outside read-only scope and outside the campaign's no-external-correspondence rule; (c) any attempt to reconcile or recompute the discrepant percentages, which would manufacture exactly the rate this lane exists to prevent.

---

result: W07b's named successor executed and both target rows resolved — PMCIDs confirmed via `convert_article_ids` before any full-text call, both returned PMIDs matched what was requested (zero mismatches), and both papers are CONFIRMED `MIXED-ARM-ONLY` at full-text/table level: cabozantinib's Table 3 states its denominator verbatim as "= 54 total patients" with no histology axis, apatinib reports toxicity over all 33, while both disaggregate *efficacy* by histology in the same results section — making the asymmetry demonstrated rather than inferred, 3 of 3 mixed-histology papers in the set; n(EMC) for cabozantinib recovered as 3 of 54 evaluable (W07b's Limitation 4 resolved), and two source-internal numeric discrepancies found and reported without adjudication (cabozantinib's abstract grade-3 percentages disagree with its own Table 3 counts and appear transposed; apatinib's abstract mislabels an 11-patient AE-withdrawal count as a grade-3+ count with a percentage that does not match its own fraction) — both of which affect quoted rows in W07b and the abstract stored in `research/literature/rt-lung-mets-probe.json`; no rate computed, nothing pooled, no clinical claim, no repository writes, HEAD read was `b9a0257e6acff53ad22535cf2adf261313e0b250` (not the brief's frozen `92abbcb9…`).
